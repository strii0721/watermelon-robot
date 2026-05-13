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
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Image, CameraInfo
from std_msgs.msg import Float64
import message_filters
from utils import ImageUtils
from watermelon_robot_interface.srv import ILogicControllerAction
from utils import config
import cv2
import time
from cv_bridge import CvBridge
import os


class SubLogicController(Node):

    def __init__(self):

        super().__init__("sub_logic_controller")
        CommonUtils.node_initializer(self)

        self.cv_bridge = CvBridge()
        self.gpr_0 = time.time()   # 用于用于 self.detect_lane() 的帧率统计
        self.sub_eye_on_chassis_color_raw = message_filters.Subscriber(node = self, 
                                                                       msg_type = Image, 
                                                                       topic = self.input_0,
                                                                       qos_profile = qos_profile_sensor_data)
        
        self.sub_eye_on_chassis_depth_raw = message_filters.Subscriber(node = self, 
                                                                       msg_type = Image, 
                                                                       topic = self.input_1,
                                                                       qos_profile = qos_profile_sensor_data)
        
        self.sub_eye_on_chassis_camera_intrinsics = message_filters.Subscriber(node = self, 
                                                                               msg_type = CameraInfo, 
                                                                               topic = self.input_2,
                                                                               qos_profile = qos_profile_sensor_data)
        
        self.pub_chassis_direction = self.create_publisher(msg_type = Float64, 
                                                           topic = self.output_0, 
                                                           qos_profile = qos_profile_sensor_data)
        
        self.pub_eye_on_hand_boxed = self.create_publisher(msg_type = Image, 
                                                           topic = self.output_1, 
                                                           qos_profile = qos_profile_sensor_data)
        
        self.srv_logic_controller_action = self.create_service(srv_type = ILogicControllerAction, 
                                                               srv_name = self.duplex_0, 
                                                               callback = self.logic_controller_action)
        
        self.approximate_time_synchronizer = message_filters.ApproximateTimeSynchronizer(
            fs = [self.sub_eye_on_chassis_color_raw, 
                  self.sub_eye_on_chassis_depth_raw, 
                  self.sub_eye_on_chassis_camera_intrinsics],
            queue_size = self.ats.queue_size,
            slop = self.ats.slop
        )
        self.approximate_time_synchronizer.registerCallback(self.detect_lane)

        CommonUtils.node_initialized(self)

        # video_name = "video-2.mp4"
        # video_path = os.path.join("resource", "lane_detection", video_name)
        # self.video_capture = cv2.VideoCapture(video_path)
        # self.tmr_camera_frame = self.create_timer(timer_period_sec = 1/30, 
        #                                           callback = self.detect_lane)

    def logic_controller_action(self, 
                                request: ILogicControllerAction.Request, 
                                response: ILogicControllerAction.Response) -> ILogicControllerAction.Response:
        
        
        desired_status = request.enable

        # TODO 控制底盘启停的代码

        response.success = True

        return response


    def detect_lane(self, 
                    color_image_msg, 
                    depth_image_msg, 
                    camera_info_msg):
    # ):
        
        color_image = self.cv_bridge.imgmsg_to_cv2(color_image_msg, desired_encoding = "bgr8")
        # depth_image = self.cv_bridge.imgmsg_to_cv2(depth_image_msg, desired_encoding = "16UC1")
        # camera_intrinsics = camera_info_msg

        rtn, color_image = self.video_capture.read()

        hsv, blurred, binary, binary_morphology = ImageUtils.lane_detection_preprocess(source_image = color_image, 
                                                                                       roi_y_min_portion = config.lane_detection.roi.y_min_portion, 
                                                                                       roi_y_max_portion = config.lane_detection.roi.y_max_portion, )
        ImageUtils.predict_lane(canvas = color_image, 
                                binary = binary_morphology, 
                                roi_y_min_portion = config.lane_detection.roi.y_min_portion, 
                                roi_y_max_portion = config.lane_detection.roi.y_max_portion, 
                                detect_step = config.lane_detection.detect_step)

        height, width = binary.shape
        now = time.time()
        real_fps = int(1/(now - self.gpr_0))
        self.gpr_0 = now
        cv2.putText(img = color_image, 
                    text = f"FPS {real_fps} | Frame Size {width}x{height}", 
                    org = (5, 20), 
                    fontFace = cv2.FONT_HERSHEY_SIMPLEX, 
                    fontScale = 0.5, 
                    color = (0, 0, 255), 
                    thickness = 2)
        
        image_message = self.cv_bridge.cv2_to_imgmsg(color_image, encoding="bgr8")
        self.pub_eye_on_hand_boxed.publish(msg = image_message)


def main():

    rclpy.init()
    sub_logic_controller = SubLogicController()
    rclpy.spin(sub_logic_controller)
    sub_logic_controller.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()