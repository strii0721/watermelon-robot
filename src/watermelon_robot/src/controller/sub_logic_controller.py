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
from utils import CVUtils
from watermelon_robot_interface.srv import ILogicControllerComm, IChassisStartStopControl
from watermelon_robot_interface.msg import IChassisDirectionControl
from utils import config
import cv2
import time
from cv_bridge import CvBridge
import os
from protocal import LogicControllerCommCode
from typing import cast


class SubLogicController(Node):

    def __init__(self):

        super().__init__("sub_logic_controller")
        CommonUtils.node_initializer(self)

        self.cv_bridge = CvBridge()
        self.gpr_0 = time.time()   # 用于用于 self.detect_lane() 的帧率统计
        
        self.sub_eye_on_chassis_color_raw = message_filters.Subscriber(self, 
                                                                       Image, 
                                                                       self.input_0,
                                                                       qos_profile = qos_profile_sensor_data)
        
        self.sub_eye_on_chassis_depth_raw = message_filters.Subscriber(self, 
                                                                       Image, 
                                                                       self.input_1,
                                                                       qos_profile = qos_profile_sensor_data)
        
        self.sub_eye_on_chassis_camera_intrinsics = message_filters.Subscriber(self, 
                                                                               CameraInfo, 
                                                                               self.input_2,
                                                                               qos_profile = qos_profile_sensor_data)
        
        self.pub_chassis_direction = self.create_publisher(IChassisDirectionControl, 
                                                           self.output_0, 
                                                           qos_profile = qos_profile_sensor_data)
        
        self.pub_eye_on_chassis_direction = self.create_publisher(Image, 
                                                                  self.output_1, 
                                                                  qos_profile = qos_profile_sensor_data)
        
        self.pub_eye_on_chassis_binary_morphology = self.create_publisher(Image, 
                                                                          self.output_2, 
                                                                          qos_profile = qos_profile_sensor_data)
        
        self.srv_logic_controller_comm = self.create_service(srv_type = ILogicControllerComm, 
                                                             srv_name = self.duplex_0, 
                                                             callback = self.logic_controller_comm)
        
        self.cli_chassis_start_stop = self.create_client(srv_type = IChassisStartStopControl, 
                                                         srv_name = self.duplex_1)
        
        self.approximate_time_synchronizer = message_filters.ApproximateTimeSynchronizer(
            fs = [self.sub_eye_on_chassis_color_raw, 
                  self.sub_eye_on_chassis_depth_raw, 
                  self.sub_eye_on_chassis_camera_intrinsics],
            queue_size = self.ats.queue_size,
            slop = self.ats.slop
        )
        self.approximate_time_synchronizer.registerCallback(self.detect_lane)

        CommonUtils.node_initialized(self)


    def logic_controller_comm(self, 
                              request: ILogicControllerComm.Request, 
                              response: ILogicControllerComm.Response) -> ILogicControllerComm.Response:
        
        request = IChassisStartStopControl.Request()
        comm_code = request.comm_code

        match comm_code:
            case LogicControllerCommCode.CHASSIS_ENABLE: 
                response_from_chassis = self.chassis_start_stop(status = True)

            case LogicControllerCommCode.CHASSIS_DISABLE:
                response_from_chassis = self.chassis_start_stop(status = False)

        response.is_success = self.chassis_start_stop_done(response = response_from_chassis)

        return response
    
    def chassis_start_stop(self, 
                           status: bool) -> IChassisStartStopControl.Response:
        
        request = IChassisStartStopControl.Request()
        request.timestamp = time.time()
        request.status = status
        return self.cli_chassis_start_stop.call(request = request)
    
    def chassis_start_stop_done(self, 
                                response: IChassisStartStopControl.Response):
        
        # TODO 需要细化异常处理
        if response.is_success:
            return True
        else:
            self.get_logger().warn(f"下逻辑控制器 - 底盘通信异常，异常信息：{response.message}")
            return False
        

    def detect_lane(self, 
                    color_image_msg, 
                    depth_image_msg, 
                    camera_info_msg):

        color_image = self.cv_bridge.imgmsg_to_cv2(color_image_msg, desired_encoding = "bgr8")
        depth_image = self.cv_bridge.imgmsg_to_cv2(depth_image_msg, desired_encoding = "16UC1")
        camera_intrinsics = camera_info_msg

        hsv, blurred, binary, binary_morphology = CVUtils.lane_detection_preprocess(source_image = color_image, 
                                                                                    roi_y_min_portion = config.lane_detection.roi.y_min_portion, 
                                                                                    roi_y_max_portion = config.lane_detection.roi.y_max_portion, )

        angular_error = CVUtils.predict_lane(canvas = color_image, 
                                             binary = binary_morphology, 
                                             roi_y_min_portion = config.lane_detection.roi.y_min_portion, 
                                             roi_y_max_portion = config.lane_detection.roi.y_max_portion, 
                                             detect_step = config.lane_detection.detect_step)

        # 这一行仅作测试用，实际环境记得注释掉
        angular_error = 0.01

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
        self.pub_eye_on_chassis_direction.publish(msg = image_message)
        image_message = self.cv_bridge.cv2_to_imgmsg(binary_morphology, encoding = "mono8")
        self.pub_eye_on_chassis_binary_morphology.publish(msg = image_message)

        control_msg = IChassisDirectionControl()
        control_msg.timestamp = time.time()
        control_msg.angular_error = angular_error
        self.pub_chassis_direction.publish(msg = control_msg)


def main():

    rclpy.init()
    sub_logic_controller = SubLogicController()
    rclpy.spin(sub_logic_controller)
    sub_logic_controller.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()