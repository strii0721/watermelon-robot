#
# Author:       strii0721
# Email:        strii0721@outlook.com
# Created on:   Sat May 09 2026
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


from fairino import Robot
import numpy as np
from watermelon_robot.src.mapper.robotic_arm_mapper import RoboticArmMapper

class RoboticArmService:

    def __init__(self, 
                 ip: str = "192.168.58.2", 
                 tool_numero: int = 0,
                 user_numero: int = 0, 
                 speed_rate: int = 30, 
                 tool_stand_by_position: tuple = (-300, -102, 450), 
                 tool_working_orientation: tuple = (90, 0, -90), 
                 camera_pose_matix: np.ndarray = np.array([[-1, 0, 0, 25], 
                                                           [0, -1, 0, 60], 
                                                           [0, 0, 1, 10], 
                                                           [0, 0, 0, 1]])):
        
        self._robotic_arm_mapper = RoboticArmMapper(ip = ip, 
                                                    tool_numero = tool_numero, 
                                                    user_numero = user_numero, 
                                                    speed_rate = speed_rate, 
                                                    tool_stand_by_position = tool_stand_by_position, 
                                                    tool_working_orientation = tool_working_orientation, 
                                                    camera_pose_matix = camera_pose_matix)
    
    def _calculate_safe_pose(self, 
                             pose: tuple) -> tuple:
        
        zero = 0.02

        return tuple(0.02 if abs(x) < zero else x for x in pose)
    
    def _calculate_pose(self, 
                        position: tuple) -> tuple: 
        
        pose = position + self._robotic_arm_mapper.get_tool_working_orientation()

        return pose
    
    def _calculate_world_position(self, 
                                  camera_position: tuple) -> tuple:
        
        w_T_tcp = self._robotic_arm_mapper.get_wTtcp_matrix()
        tcp_T_c = self._robotic_arm_mapper.get_tcpTc_matrix() 
        target_c = np.append(camera_position, 1.0).reshape(4, 1)
        target_w = (w_T_tcp @ tcp_T_c) @ target_c
        world_coordinate = tuple(target_w[0:3, 0].tolist())

        return world_coordinate
    
    def _calculate_midway_pose(self, 
                               pose: tuple) -> tuple: 
        
        midway_pose = list(pose)
        stand_by_position = self._robotic_arm_mapper.get_tool_stand_by_position()
        midway_pose[0] = stand_by_position[0]
        midway_pose[1] = stand_by_position[1]
        midway_pose = tuple(midway_pose)

        return midway_pose

    
    def move_to_position(self, 
                         position: tuple, 
                         is_world_position: bool = False) -> int:
        
        if not is_world_position: 
            position = self._calculate_world_position(camera_position = position)

        pose = self._calculate_pose(position = position)
        midway_pose = self._calculate_midway_pose(pose = pose)

        safe_pose = self._calculate_safe_pose(pose = pose)
        safe_midway_pose = self._calculate_safe_pose(pose = midway_pose)

        state_code = self._robotic_arm_mapper.move_to_pose(pose = safe_midway_pose)
        state_code = self._robotic_arm_mapper.move_to_pose(pose = safe_pose)
        
        return state_code
    
    def stand_by(self) -> int: 
        
        stand_by_position = self._robotic_arm_mapper.get_tool_stand_by_position()
        pose = self._calculate_pose(position = stand_by_position)
        current_pose = self._robotic_arm_mapper.get_tcp_pose()
        midway_pose = self._calculate_midway_pose(pose = current_pose)

        safe_pose = self._calculate_safe_pose(pose = pose)
        safe_midway_pose = self._calculate_safe_pose(pose = midway_pose)

        state_code = self._robotic_arm_mapper.move_to_pose(pose = safe_midway_pose)
        state_code = self._robotic_arm_mapper.move_to_pose(pose = safe_pose)
        
        return state_code