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


from std_msgs.msg import Header
from sensor_msgs.msg import Image, CameraInfo
from watermelon_robot_interface.msg import RealSenseFrame, LaneError
from rclpy.time import Time
from watermelon_robot_interface.srv import ChassisStartStop

class CommUtils:
    
    @classmethod
    def create_header(cls, 
                      stamp: Time, 
                      frame_id: str = "") -> Header:
        
        header = Header()
        header.stamp = stamp
        header.frame_id = frame_id
        
        return header
    
    @classmethod
    def create_realsense_frame(cls, 
                               header: Header, 
                               color_frame: Image,
                               depth_frame: Image, 
                               intrinsics: CameraInfo) -> RealSenseFrame:
        
        realsense_frame = RealSenseFrame()
        realsense_frame.header = header
        realsense_frame.color_frame = color_frame
        realsense_frame.depth_frame = depth_frame
        realsense_frame.intrinsics = intrinsics
        
        return realsense_frame
    
    @classmethod
    def create_lane_error(cls, 
                          header: Header, 
                          error_degrees: float, 
                          error_rads: float, 
                          reach_terminal: bool) -> LaneError:
        
        lane_error = LaneError()
        lane_error.header = header
        lane_error.error_degrees = error_degrees
        lane_error.error_rads = error_rads
        lane_error.reach_terminal = reach_terminal
        
        return lane_error
    
    @classmethod
    def create_request_chassis_start_stop(cls, 
                                          header: Header, 
                                          target_state: bool) -> ChassisStartStop.Request:
        
        request = ChassisStartStop.Request()
        request.header = header
        request.target_state = target_state
        
        return request
    
    @classmethod
    def create_response_chassis_start_stop(cls, 
                                           header: Header, 
                                           is_success: bool, 
                                           message: str = "") -> ChassisStartStop.Response:
        
        response = ChassisStartStop.Response()
        response.header = header
        response.is_success = is_success
        response.message = message
        
        return response