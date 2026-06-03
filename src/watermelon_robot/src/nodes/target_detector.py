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
from utils import config, NodeUtils, ModelUtils, DLUtils, CommUtils
from watermelon_robot_interface.msg import RealSenseFrame
from rclpy.qos import qos_profile_sensor_data
from cv_bridge import CvBridge
import time
import cv2
from sensor_msgs.msg import Image
import json
import rclpy


class TargetDetector(Node):
    
    def __init__(self):
        
        super().__init__("target_detector")
        NodeUtils.node_initializer(self)
        
        self.model = ModelUtils.load_model(model_name = config.target_detection.model.name, 
                                           task = config.target_detection.model.task,
                                           use_engine = config.target_detection.model.use_engine,
                                           use_half = config.target_detection.model.use_half, 
                                           device_no = config.target_detection.model.device_no, 
                                           image_size = config.target_detection.model.image_size, 
                                           confidence = config.target_detection.model.confidence, 
                                           iou = config.target_detection.model.iou)
        self.cv_bridge = CvBridge()
        
        self.in_hand_realsense_subsciber = self.create_subscription(msg_type = RealSenseFrame, 
                                                                    topic = self.input_0, 
                                                                    callback = self.detect_targets, 
                                                                    qos_profile = qos_profile_sensor_data)
        
        self.target_list_publisher = self.create_publisher(msg_type = Image, 
                                                       topic = self.output_0, 
                                                       qos_profile = qos_profile_sensor_data)
        
        self.overlay_publisher = self.create_publisher(msg_type = Image, 
                                                       topic = self.output_1, 
                                                       qos_profile = qos_profile_sensor_data)
        
        NodeUtils.node_initialized()
        
    def detect_targets(self, 
                       realsense_frame: RealSenseFrame) -> None:
            
            timestamp = time.time()
            header = CommUtils.create_header(stamp = timestamp)
            
            color_frame = self.cv_bridge.imgmsg_to_cv2(img_msg = realsense_frame.color_frame, 
                                                       desired_encoding = "passthrough")
            depth_frame = self.cv_bridge.imgmsg_to_cv2(img_msg = realsense_frame.depth_frame, 
                                                       desired_encoding = "passthrough")
            intrinsics = realsense_frame.intrinsics
        
            targets = DLUtils.predict_targets(model = self.model, 
                                              color_image = color_frame, 
                                              depth_image = depth_frame, 
                                              intrinsics = intrinsics)
            target_list_json = json.dumps(targets)
            target_list = CommUtils.create_target_list(header = header, 
                                                       target_list_json = target_list_json)
            
            now_time = time.time()
            fps = 1.0 / (now_time - self.last_frame_time)
            self.last_frame_time = now_time
            cv2.putText(self.latest_frame.color_image, f'FPS: {fps:.2f}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
            image_message = self.cv_bridge.cv2_to_imgmsg(cvim = color_frame, 
                                                         encoding="bgr8", 
                                                         header = header)
            
            self.target_list_publisher.publish(msg = target_list)
            self.overlay_publisher.publish(msg = image_message)


def main():

    rclpy.init()
    target_detector = TargetDetector()
    rclpy.spin(target_detector)
    target_detector.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()    