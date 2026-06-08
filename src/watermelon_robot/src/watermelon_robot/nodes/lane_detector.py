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


from watermelon_robot.protocol.node_with_state_machine import NodeWithStateMachine as Node
from watermelon_robot.utils import config
from watermelon_robot.utils.dl_utils import DLUtils
from watermelon_robot.utils.model_utils import ModelUtils
from watermelon_robot.utils.comm_utils import CommUtils
from watermelon_robot.utils.node_utils import NodeUtils
from watermelon_robot_interface.msg import LaneError
from rclpy.qos import qos_profile_sensor_data
from cv_bridge import CvBridge
import cv2
import time
from sensor_msgs.msg import Image
import rclpy
from enum import IntEnum


class LaneDetector(Node):
    
    class STATES(IntEnum):
        
        DISABLED = 0
        ENABLED = 100
    
    def __init__(self):
        
        super().__init__("lane_detector")
        
        self.cv_bridge = CvBridge()
        self.model = ModelUtils.load_model(model_name = config.lane_detection.model.name, 
                                           task = config.lane_detection.model.task, 
                                           use_engine = config.lane_detection.model.use_engine,
                                           confidence = config.lane_detection.model.confidence)

        self.last_frame_time = time.time()
        self.last_frame = None
        
        self.realsense_frame_color_subscriber = self.create_subscription(msg_type = Image, 
                                                                         topic = self.channels.input_0, 
                                                                         callback = self.cache_realsense_frame_color, 
                                                                         qos_profile = qos_profile_sensor_data)
        
        self.lane_error_publisher = self.create_publisher(msg_type = LaneError, 
                                                          topic = self.channels.output_0, 
                                                          qos_profile = qos_profile_sensor_data)
        
        self.navigation_color_monitor_publisher = self.create_publisher(msg_type = Image, 
                                                                        topic = self.channels.output_1, 
                                                                        qos_profile = qos_profile_sensor_data)
        
        
        
        NodeUtils.node_initialized(self)
        
    def cache_realsense_frame_color(self, 
                                    color_frame: Image) -> None:
        
        self.last_color_frame = color_frame
    
    def detect_lane(self) -> None:
        
        if self.last_color_frame:
        
            color_frame = self.cv_bridge.imgmsg_to_cv2(img_msg = self.last_color_frame, 
                                                       desired_encoding = "passthrough")
            
            reach_terminal, lane_error_rads = DLUtils.predict_lane(model = self.model, 
                                                                   source_image = color_frame, 
                                                                   roi_y_min_portion = config.lane_detection.roi.y_min_portion, 
                                                                   roi_y_max_portion = config.lane_detection.roi.y_max_portion, 
                                                                   detect_step = config.lane_detection.detect_step, 
                                                                   lane_offset = config.lane_detection.lane_offset)
            timestamp = self.get_clock().now().to_msg()
            header = CommUtils.create_header(stamp = timestamp)
            lane_error = CommUtils.create_lane_error(header = header, 
                                                     error_rads = lane_error_rads, 
                                                     reach_terminal = reach_terminal)
            height, width = color_frame.shape[:2]
            fps = int(1 / self.get_real_heartbeat_period_sec())
            cv2.putText(img = color_frame, 
                        text = f"FPS {fps} | Frame Size {width}x{height}", 
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
        
    def heartbeat(self):
        
        super().heartbeat()
        
        match self.retrieve_node_state():
            
            case self.STATES.DISABLED:
                pass
            
            case self.STATES.ENABLED:
                self.detect_lane()
        
        
def main():

    rclpy.init()
    lane_detector = LaneDetector()
    rclpy.spin(lane_detector)
    lane_detector.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()        