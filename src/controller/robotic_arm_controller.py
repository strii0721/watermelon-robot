#
# Author:       strii0721
# Email:        strii0721@outlook.com
# Created on:   Thu May 07 2026
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
import time

class RoboticArmController:

    _STANDBY_POSITION = [-300, -102, 450]

    def __init__(self, 
                 ip: str = "192.168.58.2", 
                 tool_numero: int = 0,
                 user_numero: int = 0, 
                 ideal_working_orientation: list = [90, 0, -90]):
        
        # self._robotic_arm = Robot.RPC(ip)
        self._tool_numero = tool_numero
        self._user_numero = user_numero
        self._ideal_working_orientation = ideal_working_orientation


    def close(self) -> None:

        self._robotic_arm.CloseRPC()

    def _be_safe(self, 
                 target: list) -> list:
        
        safe_target = []
        zero = 0.02

        for i in target:
            if(i == 0):
                safe_target.append(i + zero)
            else: 
                safe_target.append(i)

        return safe_target


    def move_to_pose(self, 
                     target_pose: list) -> int:
        
        safe_target_pose = self._be_safe(target = target_pose)
        # state_code = self._robotic_arm.MoveCart(desc_pos = safe_target_pose, 
        #                                         tool = self._tool_numero, 
        #                                         user = self._user_numero)

        state_code = 0
        time.sleep(2)
        
        return state_code
    
    def move_to_position(self, 
                         target_position: list) -> int:
        
        target_pose = target_position + self._ideal_working_orientation
        state_code = self.move_to_pose(target_pose = target_pose)
        
        return state_code
    
    def stand_by(self) -> int:

        state_code = self.move_to_position(target_position = self._STANDBY_POSITION)

        return state_code
    
    @classmethod
    def get_stand_by_position(cls) -> list:

        return RoboticArmController._STANDBY_POSITION