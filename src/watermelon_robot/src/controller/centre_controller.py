#
# Author:       strii0721
# Email:        strii0721@outlook.com
# Created on:   Wed May 13 2026
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
from utils import CommonUtils
from watermelon_robot_interface.srv import IRoboticArmAction
from typing import cast
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Image, CameraInfo
from utils import ImageUtils
from utils import ModelUtils
import time
import cv2
from cv_bridge import CvBridge
import message_filters


class CentreController(Node):

    def __init__(self):

        super().__init__("CenterController")
        CommonUtils.node_initializer(self)

        self.target_lock = False
        self._device, self._use_half = ModelUtils.setup_device()
        self._fa_on = ModelUtils.check_flash_attention()
        self.cv_bridge = CvBridge()
        self.last_frame_time = time.time()

        self._model = ModelUtils.load_model(device = self._device, 
                                            use_half = self._use_half)
        
        self.eye_on_hand_color_raw = message_filters.Subscriber(node = self, 
                                                                msg_type = Image, 
                                                                topic = self.input_0,
                                                                qos_profile = qos_profile_sensor_data)
        self.eye_on_hand_depth_raw = message_filters.Subscriber(node = self, 
                                                                msg_type = Image, 
                                                                topic = self.input_1,
                                                                qos_profile = qos_profile_sensor_data)
        
        self.eye_on_hand_camera_intrinsics = message_filters.Subscriber(node = self, 
                                                                        msg_type = CameraInfo, 
                                                                        topic = self.input_2,
                                                                        qos_profile = qos_profile_sensor_data)
        
        self.eye_on_hand_boxed = self.create_publisher(msg_type = Image, 
                                                       topic = self.output_0, 
                                                       qos_profile = qos_profile_sensor_data)
        
        self.cli_robotic_arm_action_once = self.create_client(srv_type = IRoboticArmAction, 
                                                              srv_name = self.duplex_0)
        
        
        
        self.approximate_time_synchronizer = message_filters.ApproximateTimeSynchronizer(
            fs = [self.eye_on_hand_color_raw, 
                  self.eye_on_hand_depth_raw, 
                  self.eye_on_hand_camera_intrinsics],
            queue_size = self.ats.queue_size,
            slop = self.ats.slop
        )
        print(f"=========================={self.ats.slop}")
        self.approximate_time_synchronizer.registerCallback(self.detect_target)
        
        CommonUtils.node_initialized(self)

    
    def detect_target(self, 
                      color_image_msg, 
                      depth_image_msg, 
                      camera_info_msg):

        color_image = self.cv_bridge.imgmsg_to_cv2(color_image_msg, desired_encoding = "bgr8")
        depth_image = self.cv_bridge.imgmsg_to_cv2(depth_image_msg, desired_encoding = "16UC1")
        camera_intrinsics = camera_info_msg
        target_list = ImageUtils.predict_targets(model = self._model, 
                                                             device = self._device, 
                                                             canvas = color_image, 
                                                             depth_image = depth_image, 
                                                             camera_intrinsics = camera_intrinsics)

        if not self.target_lock and target_list: 
            self.target_lock = True
            target_list.sort(key=lambda target: target[0])
            target = target_list[-1]
            self.get_logger().info(f"当前目标（手眼相机参考系）：{target}")
            future = self.robotic_arm_action_once(camera_coordinate = target)
            future.add_done_callback(callback = self.robotic_arm_action_once_done)
        

        now = time.time()
        fps = 1.0 / (now - self.refresh_last_frame_time(now_time = now))
        cv2.putText(color_image, f'FPS: {fps:.2f}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

        image_message = self.cv_bridge.cv2_to_imgmsg(color_image, encoding="bgr8")
        self.eye_on_hand_boxed.publish(msg = image_message)

    def refresh_last_frame_time(self, 
                                now_time: float) -> float:
        
        tmp = self.last_frame_time
        self.last_frame_time = now_time

        return tmp
    
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

def main():

    rclpy.init()
    centre_controller = CentreController()
    rclpy.spin(centre_controller)
    centre_controller.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()