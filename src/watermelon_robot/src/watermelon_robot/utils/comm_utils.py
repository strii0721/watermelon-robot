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
from watermelon_robot_interface.msg import LaneError, TargetList, ChassisControlSequence
from watermelon_robot_interface.srv import LogicControllerComm, RoboticArmAction, StateComm
from rclpy.time import Time
from watermelon_robot.protocol import LogicControllerCommCode
from watermelon_robot.protocol.state_machine import BaseStates

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
    def create_target_list(cls, 
                           header: Header, 
                           target_list_json: str) -> TargetList:
        
        target_list = TargetList()
        target_list.header = header
        target_list.target_list_json = target_list_json
        
        return target_list
    
    @classmethod
    def create_chassis_control_sequence(cls, 
                                        header: Header,
                                        forward_speed: float,
                                        error_rads: float, 
                                        is_enabled: bool = True) -> ChassisControlSequence:
        
        chassis_control_sequence = ChassisControlSequence()
        chassis_control_sequence.header = header
        chassis_control_sequence.forward_speed = float(forward_speed)
        chassis_control_sequence.error_rads = float(error_rads)
        chassis_control_sequence.is_enabled = is_enabled
        
        return chassis_control_sequence
    
    @classmethod
    def create_logic_controller_comm_request(cls, 
                                             header: Header, 
                                             comm_code: LogicControllerCommCode) -> LogicControllerComm.Request:
        
        request = LogicControllerComm.Request()
        request.header = header
        request.comm_code = comm_code.value
        
        return request
    
    @classmethod
    def create_robotic_arm_action_request(cls, 
                                          header: Header, 
                                          position_on_camera: tuple) -> RoboticArmAction.Request:
        
        request = RoboticArmAction.Request()
        request.header = header
        request.position_on_camera = position_on_camera
        
        return request
    
    @classmethod
    def create_state_comm_request(cls, 
                                  header: Header, 
                                  state: BaseStates) -> StateComm.Request:
        
        request = StateComm.Request()
        request.header = header
        request.state = state
        
        return request