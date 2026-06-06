#
# Author:       strii0721
# Email:        strii0721@outlook.com
# Created on:   Tue Jun 02 2026
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
from watermelon_robot.utils import NodeUtils
from watermelon_robot_interface.msg import LaneError
from rclpy.qos import qos_profile_sensor_data
from cv_bridge import CvBridge
from watermelon_robot.utils import config, DLUtils, ModelUtils, CommUtils
import cv2
import time
from sensor_msgs.msg import Image
import math
import rclpy
from types import SimpleNamespace

class LaneDetector(Node):
    
    def __init__(self):
        
        super().__init__("lane_detector")
        NodeUtils.node_initializer(self)
        
        self.cv_bridge = CvBridge()
        self.model = ModelUtils.load_model(model_name = config.lane_detection.model.name, 
                                           task = config.lane_detection.model.task, 
                                           use_engine = config.lane_detection.model.use_engine,
                                           confidence = config.lane_detection.model.confidence)

        self.history = SimpleNamespace()
        self.history.reach_terminal_timer = None
        self.history.last_frame_time = time.time()
        
        self.realsense_frame_color_subscriber = self.create_subscription(msg_type = Image, 
                                                                         topic = self.input_0, 
                                                                         callback = self.detect_lane, 
                                                                         qos_profile = qos_profile_sensor_data)
        
        self.lane_error_publisher = self.create_publisher(msg_type = LaneError, 
                                                          topic = self.output_0, 
                                                          qos_profile = qos_profile_sensor_data)
        
        self.navigation_color_monitor_publisher = self.create_publisher(msg_type = Image, 
                                                                        topic = self.output_1, 
                                                                        qos_profile = qos_profile_sensor_data)
        
        
        
        NodeUtils.node_initialized(self)
        
    def check_terminal(self, 
                       reach_terminal: bool) -> None:
        """检查是否抵达终点，若是则停止底盘。当且仅当连续时长的帧检测到抵达道路边缘或检测不到道路，判断为抵达终点。

        Args:
            reach_terminal (bool): 当前帧是否符合到达终点的条件。
        """        
        
        if reach_terminal:
            if self.history.reach_terminal_timer:
                    if time.time() - self.history.reach_terminal_timer > config.chassis.stop_delay_sec:
                            return True
            else: 
                self.history.reach_terminal_timer = time.time()
        else: 
            self.history.reach_terminal_timer = None
        
        return False
    
    def detect_lane(self, 
                    color_frame_message: Image) -> None:
        
        color_frame = self.cv_bridge.imgmsg_to_cv2(img_msg = color_frame_message, 
                                                   desired_encoding = "passthrough")
        timestamp = self.get_clock().now().to_msg()
        header = CommUtils.create_header(stamp = timestamp)
        
        reach_terminal, lane_error_rads = DLUtils.predict_lane(model = self.model, 
                                                               source_image = color_frame, 
                                                               roi_y_min_portion = config.lane_detection.roi.y_min_portion, 
                                                               roi_y_max_portion = config.lane_detection.roi.y_max_portion, 
                                                               detect_step = config.lane_detection.detect_step, 
                                                               lane_offset = config.lane_detection.lane_offset)
        reach_terminal = self.check_terminal(reach_terminal)
        lane_error_degrees = math.degrees(lane_error_rads)
        lane_error = CommUtils.create_lane_error(header = header, 
                                                 error_degrees = lane_error_degrees, 
                                                 error_rads = lane_error_rads, 
                                                 reach_terminal = reach_terminal)
        height, width = color_frame.shape[:2]
        now_time = time.time()
        real_fps = int(1/(now_time - self.history.last_frame_time))
        self.history.last_frame_time = now_time
        cv2.putText(img = color_frame, 
                    text = f"FPS {real_fps} | Frame Size {width}x{height}", 
                    org = (5, 20), 
                    fontFace = cv2.FONT_HERSHEY_SIMPLEX, 
                    fontScale = 0.5, 
                    color = (0, 0, 255), 
                    thickness = 2)
        color_frame_message = self.cv_bridge.cv2_to_imgmsg(cvim = color_frame, 
                                                           encoding="bgr8", 
                                                           header = header)
        
        self.lane_error_publisher.publish(msg = lane_error)
        self.navigation_color_monitor_publisher.publish(msg = color_frame_message)
        
        
def main():

    rclpy.init()
    lane_detector = LaneDetector()
    rclpy.spin(lane_detector)
    lane_detector.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()        