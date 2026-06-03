#
# Author:       strii0721
# Email:        strii0721@outlook.com
# Created on:   Wed Jun 03 2026
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


from rclpy.node import Node
from utils import NodeUtils
import rclpy
from cv_bridge import CvBridge
from rclpy.qos import qos_profile_sensor_data
from watermelon_robot_interface.msg import RealSenseFrame
from utils import CommUtils
import cv2

class SubTest(Node):
    
    def __init__(self):

        super().__init__("sub_test")
        NodeUtils.node_initializer(self)
        
        self.cv_bridge = CvBridge()
        self.realsense_frame_publisher = self.create_publisher(msg_type = RealSenseFrame,
                                                               topic = self.output_0, 
                                                               qos_profile = qos_profile_sensor_data)
        self.read_frame_timer = self.create_timer(timer_period_sec = 1/self.fps, 
                                                  callback = self.read_frame)
        self.video_capture = cv2.VideoCapture(self.video_path)
        NodeUtils.node_initialized(self)

    def read_frame(self):
        """读取 RealSense 深度相机的一帧，并发布至话题。
        """        
        
        rtn, frame = self.video_capture.read()

        if rtn:       
            timestamp = self.get_clock().now().to_msg()
            header = CommUtils.create_header(stamp = timestamp)
            color_frame = self.cv_bridge.cv2_to_imgmsg(cvim = frame, 
                                                       encoding = "bgr8")
            realsense_frame = CommUtils.create_realsense_frame(header = header,
                                                               color_frame = color_frame)
            
            self.realsense_frame_publisher.publish(msg = realsense_frame)
        
        
def main():

    rclpy.init()
    sub_test = SubTest()
    rclpy.spin(sub_test)
    sub_test.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()