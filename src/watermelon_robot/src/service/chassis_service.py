#
# Author:       strii0721
# Email:        strii0721@outlook.com
# Created on:   Thu May 14 2026
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


from geometry_msgs.msg import Twist
import math

class ChassisService:

    def __init__(self):
        pass


    def stop(self) -> Twist:
        """生成停止的控制消息。

        Returns:
            Twist: Ros2 的速度控制消息。
        """        

        sextuple = [0] * 6
        twist_msg = self.generate_twist_msg(sextuple = sextuple)
        
        return twist_msg
        
    def start(self,
              forward_speed: float) -> Twist:
        """生成启动时仅具有前进线速度的控制消息。

        Args:
            forward_speed (float): 目标前进线速度。

        Returns:
            Twist: Ros2 的速度控制消息。
        """        
        
        sextuple = [forward_speed] + [0] * 5
        twist_msg = self.generate_twist_msg(sextuple = sextuple)
        
        return twist_msg
    
    def apply_control_variable(self, 
                               control_variable: float, 
                               forward_speed: float,
                               yaw_angle: float) -> Twist:
        """根据控制量生成 Ros2 的控制消息。

        Args:
            control_variable (float): 控制量（PID 控制器输出）。
            forward_speed (float): 目标前进线速度。
            yaw_angle (float): 当前偏航角度。

        Returns:
            Twist: Ros2 的速度控制消息。
        """        
        
        linear_x = forward_speed * math.cos(math.radians(yaw_angle))
        angular_z = control_variable
        twist_msg = self.generate_twist_msg(sextuple = [linear_x, 0, 0, 0, 0, angular_z])
        
        return twist_msg

    def generate_twist_msg(self, 
                           sextuple: list) -> Twist:
        """根据 [线速度，角速度] 六元组生成 Ros2 的控制消息。

        Args:
            sextuple (list): 目标速度六元组

        Returns:
            Twist: Ros2 的速度控制消息。
        """        
        
        twist_msg = Twist()
        twist_msg.linear.x = float(sextuple[0])
        twist_msg.linear.y = float(sextuple[1])
        twist_msg.linear.z = float(sextuple[2])
        twist_msg.angular.x = float(sextuple[3])
        twist_msg.angular.y = float(sextuple[4])
        twist_msg.angular.z = float(sextuple[5])

        return twist_msg