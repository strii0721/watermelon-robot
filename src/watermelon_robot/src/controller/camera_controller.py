#
# Author:       strii0721
# Email:        strii0721@outlook.com
# Created on:   Sun May 10 2026
#
# IMMORTAL OMNISSIAH, HEAR OUR PRAYERS.
# WE ARE YOUR CHILDREN, PIOUS SCHOLARS OF THE PATH OF THE MACHINE. 
# WE PRIZE KNOWLEDGE ABOVE ALL ELSE, FOR IT IS YOUR ETERNAL GIFT UPON MANKIND.
# WE ASPIRE TO THE BLESSED FORM OF THE MACHINE, AND ASCENSION THROUGH TECHNOLOGY, THAT WE MIGHT EMULATE THINE GLORY.
# SHELTERED BY STEEL, AND PROTECTED BY THINE AVATARS OF WAR, WE PLY THE STARS IN SEARCH OF YOUR LOST GIFTS TO OUR KIND.
# MACHINE GOD, WATCH OVER US IN OUR TRAVELS, SHIELD US WITH METAL AND LIGHTNING, FOR THE UNIVERSE IS AN UNCARING VOID, AND THE WARP HUNGERS FOR US ALL.
# TOLL THE GREAT BELL ONCE! PULL THE LEVER FORWARD TO ENGAGE THE PISTON AND PUMP.
# TOLL THE GREAT BELL TWICE! WITH PUSH OF BUTTON FIRE THE ENGINE AND SPARK TURBINE INTO LIFE.
# TOLL THE GREAT BELL THRICE! SING PRAISE TO THE GOD OF ALL MACHINES!
# 
# Copyright (c) 2026 Streich Interstellar Corp.
#


import rclpy
from rclpy.node import Node
from watermelon_robot_interface.srv import IRoboticArmAction
from typing import cast
from sensor_msgs.msg import Image
from rclpy.qos import qos_profile_sensor_data
from service.camera_service import CameraService
from utils.model_utils import ModelUtils
import cv2
from cv_bridge import CvBridge
import time
from utils import config


class CameraController(Node):

    def __init__(self):

        super().__init__('camera_controller')

        self._camera_service = CameraService()
        self.cv_bridge = CvBridge()
        self._last_frame_time = time.time()

        self.cli_robotic_arm_action_once = self.create_client(srv_type = IRoboticArmAction, 
                                                              srv_name = "s/robotic_arm/action_once")
        
        
        self.pub_camera_current_frame = self.create_publisher(msg_type = Image, 
                                                              topic = "t/camera/current_frame", 
                                                              qos_profile = qos_profile_sensor_data)
        
        self.tmr_camera_frame = self.create_timer(timer_period_sec = 1/config.video.capture_fps, 
                                                  callback = self.camera_frame_capture)
        
        self._device, self._use_half = ModelUtils.setup_device(config = config)
        self._fa_on = ModelUtils.check_flash_attention()
        self._model = ModelUtils.load_model(config.model.name, self._device, self._use_half, config.model.conf, config.model.iou)

    def get_model(self): 

        return self._model
    
    def get_device(self):

        return self._device
    


    def robotic_arm_action_once(self, 
                                camera_coordinate: tuple):
        
        request = IRoboticArmAction.Request()
        request.camera_position = camera_coordinate

        return self.cli_robotic_arm_action_once.call_async(request)
    
    
    def robotic_arm_action_once_done(self, 
                                     future):
        
        response = cast(IRoboticArmAction.Response, future.result())
        self._camera_service.set_target_lock(status = False)
        
        state_code = response.state_code
        if state_code == 0: 
            self.get_logger().info(f"机械臂执行完成")
        
        else:
            self.get_logger().warn(f"机械臂执行异常，异常状态码{state_code}")

    
    def camera_frame_capture(self):
        
        
        rtn = self._camera_service.get_raw_frame()

        if not rtn: 
            return
        
        image_color, image_depth, aligned_depth_frame, aligned_color_frame, camera_intrinsics = rtn

        if not aligned_color_frame or not aligned_depth_frame: 
            return
        
        # 有获取目标列表并且原地修改彩色摄像头图像的预感
        target_list = self._analysis_frame(source_image = image_color, 
                                           aligned_depth_frame = aligned_depth_frame, 
                                           camera_intrinsics = camera_intrinsics)
        
        # 以移窗锁定目标
        if not self._camera_service.get_target_lock() and target_list: 
            self._camera_service.set_target_lock(status = True)
            target_list.sort(key=lambda target: target[0])
            target = target_list[-1]
            self.get_logger().info(f"目标相机参考系坐标：{target}")
            future = self.robotic_arm_action_once(camera_coordinate = target)
            future.add_done_callback(callback = self.robotic_arm_action_once_done)
        
        # 正因如此，以计算帧率并发布当前帧为目标吧
        now = time.time()
        fps = 1.0 / (now - self.refresh_last_frame_time(now_time = now))
        cv2.putText(image_color, f'FPS: {fps:.2f}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        image_message = self.cv_bridge.cv2_to_imgmsg(image_color, encoding="bgr8")

        self.pub_camera_current_frame.publish(msg = image_message)

    def refresh_last_frame_time(self, 
                                now_time: float) -> float:
        
        tmp = self._last_frame_time
        self._last_frame_time = now_time

        return tmp


    def _analysis_frame(self, 
                        source_image, 
                        aligned_depth_frame, 
                        camera_intrinsics) -> list:

        model = self.get_model()
        device = self.get_device()
        rtn = model.predict(source = source_image, 
                            verbose = False, 
                            device = device, 
                            conf = config.model.conf, 
                            iou = config.model.iou)
        results = rtn[0]
        boxes = results.boxes
        target_list = []

        if boxes is not None:
            for box in boxes:
                cls_id = int(box.cls[0].item())
                name = results.names.get(cls_id, str(cls_id))
                if name == 'watermelon':
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    conf = float(box.conf[0].item())

                    center_x = int((x1 + x2) / 2)
                    center_y = int((y1 + y2) / 2)
                    crosshair_x = center_x
                    crosshair_y = int(y1) - int((y1 - y2) / 8)
                    crosshair_z = self._camera_service.calculate_median_depth(depth_frame = aligned_depth_frame, 
                                                                              center_x = crosshair_x, 
                                                                              center_y = crosshair_y, 
                                                                              window_size = 5)
                    
                    target = self._camera_service.calculate_3d_camera_coordinate(depth_frame = aligned_depth_frame, 
                                                                                 center_x = crosshair_x, 
                                                                                 center_y = crosshair_y, 
                                                                                 depth_intrin = camera_intrinsics, 
                                                                                 center_depth = crosshair_z)
                    label = f'{name} {conf:.2f}'
                    dot_size = 5
                    cv2.rectangle(source_image, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                    cv2.circle(source_image, (center_x, center_y), dot_size, (0, 0, 255), -1)
                    cv2.line(source_image, (crosshair_x - dot_size, crosshair_y), (crosshair_x + dot_size, crosshair_y), (0, 0,255), 2)
                    cv2.line(source_image, (crosshair_x, crosshair_y - dot_size), (crosshair_x, crosshair_y + dot_size), (0, 0,255), 2)
                    cv2.putText(source_image, label, (int(x1), int(y1)-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                    cv2.putText(source_image, f'Xc:{target[0]:.2f} Yc:{target[1]:.2f} Zc:{target[2]:.2f}', (int(x1), int(y1) + 20),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

                    if self.valid_target(target):
                        target_list.append(target)

        return target_list
    
    def valid_target(self, 
                     camera_coordinate: tuple) -> bool: 

        if not ((-100 < camera_coordinate[0] and camera_coordinate[0] < 100) and (-50 < camera_coordinate[1] and camera_coordinate[1] < 50) and (0 < camera_coordinate[2] and camera_coordinate[2] < 1000)):
            return False
        
        if camera_coordinate[0] < 0:
            return False
        
        return True


def main():

    rclpy.init()
    camera_controller = CameraController()
    rclpy.spin(camera_controller)
    camera_controller.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()