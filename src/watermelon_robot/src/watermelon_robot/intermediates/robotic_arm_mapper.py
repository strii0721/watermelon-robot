#
# Author:       strii0721
# Email:        strii0721@outlook.com
# Created on:   Sun May 10 2026
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
from watermelon_robot.utils.kinematics_utils import KinematicsUtils
import numpy as np
from typing import cast


class RoboticArmMapper:

    def __init__(self, 
                 ip: str, 
                 tool_numero: int,
                 user_numero: int, 
                 speed_rate: int, 
                 standby_status: tuple, 
                 calibration_marix: np.ndarray, 
                 eye_in_hand: bool):
        
        self.robotic_arm = Robot.RPC(ip)
        self.tool_numero = tool_numero
        self.user_numero = user_numero
        self.robotic_arm.SetSpeed(speed_rate)
        use_cartesian = standby_status[0]
        if not use_cartesian:
            _, standby_sextuplet = self.calculate_forward_kinematic(joint_position = standby_status[1])
            self.standby_sextuplet = tuple(standby_sextuplet)
        else:
            self.standby_sextuplet = tuple(standby_status[1])
        self.w_T_tcp = KinematicsUtils.calculate_pose_matrix(cartesian_sextuplet = self.standby_sextuplet)
        self.calibration_marix = calibration_marix
        self.eye_in_hand = eye_in_hand
    
    def get_standby_sextuplet(self) -> tuple:
        
        return self.standby_sextuplet
    
    def get_wTtcp_matrix(self) -> np.ndarray: 

        return self.w_T_tcp
    
    def get_calibration_matrix(self) -> np.ndarray:
        
        return self.calibration_marix
    
    def get_eye_in_hand_setting(self) -> bool:
        
        return self.eye_in_hand
    
    def get_tcp_pose(self, 
                     block: bool = False) -> tuple:
        """获取当前机械臂末端位姿六元组

        Args:
            block (bool, optional): 调用 SDK 函数的方式是否为阻塞. Defaults to False.

        Returns:
            tuple: 机械臂末端位姿六元组
        """        
        
        block_flag = 0 if block else 1
        rtn = self.robotic_arm.GetActualTCPPose(flag = block_flag)
        state_code, tcp_pose_list = rtn
        state_code = cast(int, state_code)
        tcp_pose = tuple(tcp_pose_list)
        
        return (state_code, tcp_pose)
    
    def move_to_joint_space(self, 
                            joint_position: list) -> int:
        """关节空间运动。

        Args:
            joint_space (tuple): 关节空间六元组，度为单位。

        Returns:
            int: 机械臂响应状态码。
        """        
        
        state_code = self.robotic_arm.MoveJ(joint_pos = joint_position, 
                                            tool = self.tool_numero, 
                                            user = self.user_numero)
        
        return state_code
    
    def move_to_pose(self, 
                     pose: tuple) -> int:
        """移动至给定位姿六元组。

        Args:
            pose (tuple): 位姿六元组（世界坐标系）。

        Returns:
            int: 机械臂响应状态码。
        """        
        
        pose_list = list(pose)
        state_code = self.robotic_arm.MoveCart(desc_pos = pose_list, 
                                               tool = self.tool_numero, 
                                               user = self.user_numero)
        state_code = cast(int, state_code)

        return state_code
    
    def operate_tool(self, 
                     tool_id: int, 
                     command_code: int) -> int:
        """向末端工具输出一个命令码。

        Args:
            tool_id (int): 工具编号。
            command_code (int): 命令码。

        Returns:
            int: 工具响应状态码。
        """        
        
        state_code = self.robotic_arm.SetDO(id = tool_id, 
                                             status = command_code, 
                                             smooth = 0, 
                                             block = 1)
        
        return state_code
    
    def calculate_forward_kinematic(self, 
                                    joint_position: list) -> tuple:
        """根据关节空间进行正运动学结算。

        Args:
            joint_position (list): 关节空间位置。

        Returns:
            tuple: (状态码, 末端工具笛卡尔位姿六元组)。
        """        
        
        rtn = self.robotic_arm.GetForwardKin(joint_pos = joint_position)
        
        
        state_code, sextuplet = rtn
        
        
        
        return state_code, tuple(sextuplet)