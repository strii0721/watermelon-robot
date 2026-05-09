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

class RoboticArmController:

    def __init__(self, 
                 ip: str = "192.168.58.2", 
                 tool_numero: int = 0,
                 user_numero: int = 0, 
                 speed_rate: int = 30, 
                 stand_by_position: list = [-300, -102, 450], 
                 ideal_working_orientation: list = [90, 0, -90]):
        
        self._robotic_arm = Robot.RPC(ip)
        self._tool_numero = tool_numero
        self._user_numero = user_numero
        self._robotic_arm.SetSpeed(speed_rate)
        self._stand_by_position = stand_by_position
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


    def _move_to_pose(self, 
                     target_pose: list) -> int:
        
    
        
        safe_target_pose = self._be_safe(target = target_pose)
        state_code = self._robotic_arm.MoveCart(desc_pos = safe_target_pose, 
                                                tool = self._tool_numero, 
                                                user = self._user_numero)
        
        return state_code
    
    def calculate_real_position(self, 
                                target_position: list) -> list: 
        
        real_position = target_position
        real_position[0] += 50
        real_position[0] += 30

        return real_position
    
    def calculate_pose(self, 
                       target_position: list) -> list:
        
        return target_position + self.get_ideal_working_orientation()
    
    def calculate_midway_position(self, 
                                  target_position: list) -> list: 
        
        midway_position = self.get_stand_by_position()
        midway_position[2] = target_position[2]
        return midway_position
    
    def move_to_position(self, 
                         target_position: list, 
                         safe: bool = True) -> int:

        # self._robotic_arm.NewSplineStart(type = 1)
        target_pose = self.calculate_pose(target_position = self.calculate_real_position(target_position = target_position))

        if safe: 
            midway_pose = self.calculate_pose(target_position = self.calculate_midway_position(target_position = self.calculate_real_position(target_position = target_position)))
            print(f"中间安全位姿 {midway_pose}")
            self._move_to_pose(target_pose = midway_pose)
            # self._robotic_arm.NewSplinePoint(desc_pos = midway_pose, 
            #                                  tool = self._tool_numero, 
            #                                  user = self._user_numero, 
            #                                  lastFlag = 0)


        print(f"真实目标位姿 {target_pose}")
        self._move_to_pose(target_pose = target_pose)
        # self._robotic_arm.NewSplinePoint(desc_pos = target_pose, 
        #                                      tool = self._tool_numero, 
        #                                      user = self._user_numero, 
        #                                      lastFlag = 1)
        self._robotic_arm.NewSplineEnd()
        
        return 0
    
    def stand_by(self, 
                 safe: bool = True) -> list:

        _, current_position = self.get_tcp_pose()[:3]

        midway_position = self.calculate_midway_position(target_position = current_position)

        if safe: 
            midway_pose = self.calculate_pose(target_position = midway_position)
            print(f"中间安全位姿 {midway_pose}")
            self._move_to_pose(target_pose = midway_pose)

        target_pose = self.get_stand_by_pose()
        print(f"就位位姿 {target_pose}")
        self._move_to_pose(target_pose = target_pose)

        return 0
    
    def get_stand_by_position(self) -> list:

        return self._stand_by_position.copy()
    
    def get_ideal_working_orientation(self) -> list:

        return self._ideal_working_orientation.copy()
    
    def get_stand_by_pose(self) -> list:

        return self.calculate_pose(target_position = self.get_stand_by_position())
    
    def get_tcp_pose(self, 
                     block = False) -> list:
        
        flag = 0 if block else 1
        tcp_pose = self._robotic_arm.GetActualTCPPose(flag = flag)

        return tcp_pose
    
    def valid_position(self, 
                       target_position: list) -> bool:
        

        target_pose = target_position + self.get_ideal_working_orientation()
        print(f"desc_pos{target_pose}")
        print(f"joint_pos_ref{self.get_stand_by_pose()}")
        _, is_valid = self._robotic_arm.GetInverseKinHasSolution(type = 2, 
                                                                 desc_pos = target_pose, 
                                                                 joint_pos_ref = self.get_stand_by_pose())
        
        return is_valid