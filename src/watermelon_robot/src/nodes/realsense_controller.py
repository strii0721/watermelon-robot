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
from rclpy.qos import qos_profile_sensor_data
from service import RealsenseService
from utils import NodeUtils
from cv_bridge import CvBridge
from utils import CommUtils
from sensor_msgs.msg import Image, CameraInfo
from typing import cast


class RealsenseController(Node):

    def __init__(self):

        super().__init__("realsense_controller")
        NodeUtils.node_initializer(self)

        self.realsense_service = RealsenseService()
        self.cv_bridge = CvBridge()

        self.realsense_frame_color_publisher = self.create_publisher(msg_type = Image,
                                                                     topic = self.output_0, 
                                                                     qos_profile = qos_profile_sensor_data)
        
        self.realsense_frame_depth_publisher = self.create_publisher(msg_type = Image,
                                                                     topic = self.output_1, 
                                                                     qos_profile = qos_profile_sensor_data)
        
        self.realsense_frame_intrinsics_publisher = self.create_publisher(msg_type = CameraInfo,
                                                                          topic = self.output_2, 
                                                                          qos_profile = qos_profile_sensor_data)
        
        self.read_frame_timer = self.create_timer(timer_period_sec = 1/self.fps, 
                                                  callback = self.read_frame)
        
        NodeUtils.node_initialized(self)

    def read_frame(self):
        """读取 RealSense 深度相机的一帧，并发布至话题。
        """        
        
        frames = self.realsense_service.read_frames()

        if frames:
            timestamp = self.get_clock().now().to_msg()
            header = CommUtils.create_header(stamp = timestamp)   
            [color_frame, depth_frame, intrinsics] = frames
            
            color_frame = self.cv_bridge.cv2_to_imgmsg(cvim = color_frame, 
                                                       encoding = "bgr8", 
                                                       header = header)
            depth_frame = self.cv_bridge.cv2_to_imgmsg(cvim = depth_frame, 
                                                       encoding = "16UC1", 
                                                       header = header)
            intrinsics = cast(CameraInfo, intrinsics)
            intrinsics.header = header
            
            self.realsense_frame_color_publisher.publish(msg = color_frame)
            self.realsense_frame_depth_publisher.publish(msg = depth_frame)
            self.realsense_frame_intrinsics_publisher.publish(msg = intrinsics)
        
        
def main():

    rclpy.init()
    camera_controller = RealsenseController()
    rclpy.spin(camera_controller)
    camera_controller.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()