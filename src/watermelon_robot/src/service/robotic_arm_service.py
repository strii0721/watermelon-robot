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


import numpy as np
from mapper import RoboticArmMapper

class RoboticArmService:

    def __init__(self, 
                 ip: str,
                 tool_standby_sextuplet: tuple,
                 camera_pose_matix: np.ndarray, 
                 speed_rate):
        
        tool_stand_by_position = tool_standby_sextuplet[:3]
        tool_working_orientation = tool_standby_sextuplet[3:]
        self._robotic_arm_mapper = RoboticArmMapper(ip = ip, 
                                                    tool_numero = 0, 
                                                    user_numero = 0, 
                                                    speed_rate = speed_rate, 
                                                    tool_stand_by_position = tool_stand_by_position, 
                                                    tool_working_orientation = tool_working_orientation, 
                                                    camera_pose_matix = camera_pose_matix)
    
    def calculate_safe_pose(self, 
                            pose: tuple) -> tuple:
        """由于 Fairino 机械臂 SDK 限制，特殊位姿参数会导致逆运动学解算失败，故需要在特殊位姿参数加上极小的修正量。

        Args:
            pose (tuple): 原始位姿六元组。

        Returns:
            tuple: 安全位姿六元组。
        """        
        
        zero = 0.02

        return tuple(0.02 if abs(x) < zero else x for x in pose)
    
    def calculate_pose(self, 
                       position: tuple) -> tuple: 
        """根据目标位置坐标计算目标位姿。

        Args:
            position (tuple): 目标位置坐标。

        Returns:
            tuple: 目标位姿六元组。
        """        
        
        pose = position + self._robotic_arm_mapper.get_tool_working_orientation()

        return pose
    
    def calculate_world_position(self, 
                                 camera_position: tuple) -> tuple:
        """根据相机坐标计算世界参考系坐标。

        Args:
            camera_position (tuple): 相机参考系位置坐标。

        Returns:
            tuple: 世界参考系坐标六元组。
        """        
        
        w_T_tcp = self._robotic_arm_mapper.get_wTtcp_matrix()
        tcp_T_c = self._robotic_arm_mapper.get_tcpTc_matrix() 
        target_c = np.append(camera_position, 1.0).reshape(4, 1)
        target_w = (w_T_tcp @ tcp_T_c) @ target_c

        world_coordinate = tuple(target_w[0:3, 0].tolist())

        return world_coordinate
    
    def calculate_midway_pose(self, 
                              pose: tuple) -> tuple: 
        """计算中间位置的位姿。机械臂会先移动到与目标位置世界参考系 z 轴等高的位置。

        Args:
            pose (tuple): 目标位姿六元组。

        Returns:
            tuple: 中间位置位姿。
        """        
        
        midway_pose = list(pose)
        stand_by_position = self._robotic_arm_mapper.get_tool_stand_by_position()
        midway_pose[0] = stand_by_position[0]
        midway_pose[1] = stand_by_position[1]
        midway_pose[2] = pose[2]
        midway_pose = tuple(midway_pose)

        return midway_pose
    
    def move_to_position(self, 
                         position: tuple, 
                         is_world_position: bool = False) -> int:
        """移动机械臂至指定位姿。

        Args:
            position (tuple): 目标位置坐标。
            is_world_position (bool, optional): 该坐标是否为世界参考系（机械臂底座参考系）. Defaults to False.

        Returns:
            int: 机械臂状态码
        """        
        
        if not is_world_position: 
            position = self.calculate_world_position(camera_position = position)

        pose = self.calculate_pose(position = position)
        midway_pose = self.calculate_midway_pose(pose = pose)
        safe_pose = self.calculate_safe_pose(pose = pose)
        safe_midway_pose = self.calculate_safe_pose(pose = midway_pose)
        
        state_code = self._robotic_arm_mapper.move_to_pose(pose = safe_midway_pose)
        if state_code != 0:
            return state_code
        state_code = self._robotic_arm_mapper.move_to_pose(pose = safe_pose)
        
        return state_code
    
    def stand_by(self) -> int: 
        """恢复机械臂为初始位姿

        Returns:
            int: 机械臂状态码
        """        
        
        stand_by_position = self._robotic_arm_mapper.get_tool_stand_by_position()
        pose = self.calculate_pose(position = stand_by_position)
        _, current_pose = self._robotic_arm_mapper.get_tcp_pose()
        midway_pose = self.calculate_midway_pose(pose = current_pose)
        
        state_code = self._robotic_arm_mapper.move_to_pose(pose = midway_pose)
        if state_code != 0:
            return state_code
        state_code = self._robotic_arm_mapper.move_to_pose(pose = pose)
        
        return state_code