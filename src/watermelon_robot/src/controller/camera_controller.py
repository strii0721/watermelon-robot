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

class CameraController(Node):

    def __init__(self, 
                 camera_fps: int = 30):

        super().__init__('camera_controller')

        self._camera_service = CameraService()
        self.cv_bridge = CvBridge()

        self.cli_robotic_arm_action_once = self.create_client(srv_type = IRoboticArmAction, 
                                                              srv_name = "s/robotic_arm/action_once")
        
        self.pub_camera_current_frame = self.create_publisher(msg_type = Image, 
                                                              topic = "t/camera/current_frame", 
                                                              qos_profile = qos_profile_sensor_data)
        
        self.tmr_camera_frame = self.create_timer(timer_period_sec = 1/camera_fps, 
                                                    callback = self.camera_frame_capture)

    def robotic_arm_action_once(self, 
                                camera_coordinate: tuple):
        
        request = IRoboticArmAction.Request()
        request.camera_position = camera_coordinate

        return self.cli_robotic_arm_action_once.call_async(request)
    
    
    def robotic_arm_action_once_done_callback(self, 
                                              future):
        
        response = cast(IRoboticArmAction.Response, future.result())
        
        if response.state_code == 0: 
            self._camera_service.set_target_lock(status = False)
    
    def camera_frame_capture(self):
        
        prev = time.time()
        rtn = self._camera_service.get_raw_frame()

        if not rtn: 
            return
        
        image_color, image_depth, aligned_depth_frame, aligned_color_frame, camera_intrinsics = rtn

        if not aligned_color_frame or not aligned_depth_frame: 
            return
        
        # 有获取目标列表并且原地修改彩色摄像头图像的预感
        target_list = self.analysis_frame(source_image = image_color, 
                                          aligned_depth_frame = aligned_depth_frame, 
                                          camera_intrinsics = camera_intrinsics)
        
        # 以移窗锁定目标
        if not self._camera_service.get_target_lock() and target_list: 
            target_list.sort(key=lambda target: target[0])
            if target_list[-1][0] > 0 : 
                self._camera_service.set_target_lock(status = True)
                future = self.robotic_arm_action_once(camera_coordinate = target_list[-1])
                future.add_done_callback(callback = self.robotic_arm_action_once_done_callback)
        
        # 正因如此，以计算帧率并发布当前帧为目标吧
        now = time.time()
        fps = 1.0 / (now - prev) if now > prev else 0.0
        cv2.putText(image_color, f'FPS: {fps:.2f}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        image_message = self.cv_bridge.cv2_to_imgmsg(image_color, encoding="bgr8")
        self.pub_camera_current_frame.publish(msg = image_message)


    def analysis_frame(self, 
                       source_image, 
                       aligned_depth_frame, 
                       camera_intrinsics):
        
        configure = ModelUtils.parse_args()
        device, use_half = ModelUtils.setup_device(configure)
        fa_on = ModelUtils.check_flash_attention()
        model = ModelUtils.load_model(configure.model, device, use_half, configure.conf, configure.iou)
        rtn = model.predict(source = source_image, 
                            verbose = False, 
                            device=device, 
                            conf=configure.conf, 
                            iou=configure.iou)
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
                    center_z = self._camera_service.calculate_median_depth(depth_frame = aligned_depth_frame, 
                                                                 center_x = center_x, 
                                                                 center_y = center_y, 
                                                                 window_size = 5)
                    crosshair_x = center_x
                    crosshair_y = int(y1)
                    crosshair_z = self._camera_service.calculate_median_depth(depth_frame = aligned_depth_frame, 
                                                                    center_x = center_x, 
                                                                    center_y = int(y1), 
                                                                    window_size = 5)
                    label = f'{name} {conf:.2f}'
                    size = 5
                    thickness = 2
                    cv2.rectangle(source_image, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                    cv2.circle(source_image, (center_x, center_y), size, (0, 0, 255), -1)
                    # cv2.circle(source_image, (crosshair_x, crosshair_y), size, (0, 0, 255), -1)
                    cv2.line(source_image, (crosshair_x - size, crosshair_y), (crosshair_x + size, crosshair_y), (0, 0, 255), thickness)
                    cv2.line(source_image, (crosshair_x, crosshair_y - size), (crosshair_x, crosshair_y + size), (0, 0, 255), thickness)
                    cv2.putText(source_image, label, (int(x1), int(y1)-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                    if crosshair_z > 0:
                        target = self._camera_service.calculate_3d_camera_coordinate(depth_frame = aligned_depth_frame, 
                                                                               center_x = crosshair_x, 
                                                                               center_y = crosshair_y, 
                                                                               depth_intrin = camera_intrinsics)


                    cv2.putText(source_image, f'Xc:{target[0]:.2f} Yc:{target[1]:.2f} Zc:{target[2]:.2f}', (int(x1), int(y1) + 20), cv2.FONT_HERSHEY_SIMPLEX, 5, (255, 0, 0), 2)
                    target_list.append(target)

        return target_list


def main():

    rclpy.init()
    camera_controller = CameraController()
    rclpy.spin(camera_controller)
    camera_controller.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()