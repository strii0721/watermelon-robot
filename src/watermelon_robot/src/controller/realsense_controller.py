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
from sensor_msgs.msg import Image, CameraInfo
from rclpy.qos import qos_profile_sensor_data
from service import RealsenseService
from utils import CommonUtils
from cv_bridge import CvBridge


class RealsenseController(Node):

    def __init__(self):

        super().__init__("RealsenseController")
        CommonUtils.node_initializer(self)

        self.realsense_service = RealsenseService()
        self.cv_bridge = CvBridge()

        self.eye_on_hand_color_raw = self.create_publisher(msg_type = Image, 
                                                           topic = self.output_0, 
                                                           qos_profile = qos_profile_sensor_data)
        
        self.eye_on_hand_depth_raw = self.create_publisher(msg_type = Image, 
                                                           topic = self.output_1, 
                                                           qos_profile = qos_profile_sensor_data)
        
        self.eye_on_hand_camera_intrinsics = self.create_publisher(msg_type = CameraInfo, 
                                                                   topic = self.output_2, 
                                                                   qos_profile = qos_profile_sensor_data)
        
        self.tmr_camera_frame = self.create_timer(timer_period_sec = 1/self.fps, 
                                                  callback = self.camera_frame_capture)
        
        CommonUtils.node_initialized(self)

    
    def camera_frame_capture(self):
        
        rtn = self.realsense_service.read_current_frame()

        if not rtn: 
            return None
        
        [color_frame, depth_frame, camera_intrinsics] = rtn

        color_msg = self.cv_bridge.cv2_to_imgmsg(color_frame, encoding = "bgr8")
        depth_msg = self.cv_bridge.cv2_to_imgmsg(depth_frame, encoding = "16UC1")
        # intrinsics_msg = self.realsense_service.convert_intrinsics2camera_info(rs_intrinsics = camera_intrinsics)
        intrinsics_msg = camera_intrinsics

        timestamp = self.get_clock().now().to_msg()
        color_msg.header.stamp = timestamp
        depth_msg.header.stamp = timestamp
        intrinsics_msg.header.stamp = timestamp

        self.eye_on_hand_color_raw.publish(msg = color_msg)
        self.eye_on_hand_depth_raw.publish(msg = depth_msg)
        self.eye_on_hand_camera_intrinsics.publish(msg = intrinsics_msg)
        

def main():

    rclpy.init()
    camera_controller = RealsenseController()
    rclpy.spin(camera_controller)
    camera_controller.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()