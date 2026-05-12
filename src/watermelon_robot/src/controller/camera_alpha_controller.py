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
from service import RealsenseService
from utils.model_utils import ModelUtils
import cv2
from cv_bridge import CvBridge
import time
from utils import config


class CameraAlphaController(Node):

    def __init__(self):

        super().__init__("camera_alpha_controller")
        self.get_logger().info(f"目标检测摄像机已上线，正在初始化...")

        self._camera_service = RealsenseService()
        self.cv_bridge = CvBridge()
        self._last_frame_time = time.time()
        self._target_lock = False

        self.cli_robotic_arm_action_once = self.create_client(srv_type = IRoboticArmAction, 
                                                              srv_name = "s/robotic_arm/action_once")
        
        
        self.pub_camera_current_frame = self.create_publisher(msg_type = Image, 
                                                              topic = "t/camera/current_frame", 
                                                              qos_profile = qos_profile_sensor_data)
        
        self.tmr_camera_frame = self.create_timer(timer_period_sec = 1/config.video.capture_fps, 
                                                  callback = self.camera_frame_capture)
        
        self._device, self._use_half = ModelUtils.setup_device()
        self._fa_on = ModelUtils.check_flash_attention()
        self._model = ModelUtils.load_model(device = self._device, 
                                            use_half = self._use_half)
        
        self.get_logger().info(f"目标检测摄像机初始化完成...")
    

    def robotic_arm_action_once(self, 
                                camera_coordinate: tuple):
        
        request = IRoboticArmAction.Request()
        request.camera_position = camera_coordinate

        return self.cli_robotic_arm_action_once.call_async(request)
    
    
    def robotic_arm_action_once_done(self, 
                                     future):
        
        response = cast(IRoboticArmAction.Response, future.result())
        self._target_lock = False
        
        state_code = response.state_code
        if state_code == 0: 
            self.get_logger().info(f"机械臂执行完成")
        
        else:
            self.get_logger().warn(f"机械臂执行异常，异常状态码{state_code}")

    
    def camera_frame_capture(self):
        
        
        rtn = self._camera_service.read_current_frame()

        if not rtn: 
            return
        
        color_frame_array, depth_frame_array,color_frame, depth_frame, camera_intrinsics = rtn

        if not (color_frame and depth_frame): 
            return
        
        target_list = self._camera_service.analysis_frame(model = self._model, 
                                                          device = self._device, 
                                                          color_frame_array = color_frame_array, 
                                                          depth_frame = depth_frame, 
                                                          camera_intrinsics = camera_intrinsics)
        

        if not self._target_lock and target_list: 
            self._target_lock = True
            target_list.sort(key=lambda target: target[0])
            target = target_list[-1]
            self.get_logger().info(f"目标相机参考系坐标：{target}")
            future = self.robotic_arm_action_once(camera_coordinate = target)
            future.add_done_callback(callback = self.robotic_arm_action_once_done)
        

        now = time.time()
        fps = 1.0 / (now - self.refresh_last_frame_time(now_time = now))
        cv2.putText(color_frame_array, f'FPS: {fps:.2f}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        image_message = self.cv_bridge.cv2_to_imgmsg(color_frame_array, encoding="bgr8")

        self.pub_camera_current_frame.publish(msg = image_message)

    def refresh_last_frame_time(self, 
                                now_time: float) -> float:
        
        tmp = self._last_frame_time
        self._last_frame_time = now_time

        return tmp


def main():

    rclpy.init()
    camera_controller = CameraAlphaController()
    rclpy.spin(camera_controller)
    camera_controller.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()