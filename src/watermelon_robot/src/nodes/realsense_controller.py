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
from utils import CommonUtils
from cv_bridge import CvBridge
from watermelon_robot_interface.msg import RealSenseFrame
from utils import CommUtils


class RealsenseController(Node):

    def __init__(self):

        super().__init__("realsense_controller")
        CommonUtils.node_initializer(self)

        self.realsense_service = RealsenseService()
        self.cv_bridge = CvBridge()

        self.realsense_frame_publisher = self.create_publisher(msg_type = RealSenseFrame,
                                                               topic = self.output_0, 
                                                               qos_profile = qos_profile_sensor_data)
        
        self.read_frame_timer = self.create_timer(timer_period_sec = 1/self.fps, 
                                                  callback = self.read_frame)
        
        CommonUtils.node_initialized(self)

    def read_frame(self):
        """读取 RealSense 深度相机的一帧，并发布至话题。
        """        
        
        frames = self.realsense_service.read_frames()

        if frames:       
            [color_frame, depth_frame, intrinsics] = frames
            color_frame = self.cv_bridge.cv2_to_imgmsg(cvim = color_frame, 
                                                       encoding = "bgr8")
            depth_frame = self.cv_bridge.cv2_to_imgmsg(cvim = depth_frame, 
                                                       encoding = "16UC1")
            timestamp = self.get_clock().now().to_msg()
            header = CommUtils.create_header(stamp = timestamp)
            realsense_frame = CommUtils.create_realsense_frame(header = header,
                                                               color_frame = color_frame, 
                                                               depth_frame = depth_frame, 
                                                               intrinsics = intrinsics)
            
            self.realsense_frame_publisher.publish(msg = realsense_frame)
        
        
def main():

    rclpy.init()
    camera_controller = RealsenseController()
    rclpy.spin(camera_controller)
    camera_controller.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()