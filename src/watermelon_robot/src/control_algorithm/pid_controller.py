#
# Author:       strii0721
# Email:        strii0721@outlook.com
# Created on:   Fri May 22 2026
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
import time


class PIDController:

    def __init__(self,
                 pid_triple: tuple,
                 integral_limit: float,
                 output_limit: float):
        """构造函数。

        Args:
            pid_triple (tuple): PID 参数。
            integral_limit (float): 积分项绝对值上限。
            output_limit (float): 输出绝对值上限。
        """        

        self.kp, self.ki, self.kd = pid_triple
        self.maximum_output_abs = output_limit
        self.integral_limit = integral_limit
        self.integral = 0
        self.previous_error = 0

    def update_control_variable(self,
                                error: float, 
                                control_interval: float) -> float:        
        """根据误差应用 PID 控制器输出控制量。

        Args:
            error (float): 角度误差（角度）。

        Returns:
            float: 控制量。
        """
        
        dt = control_interval
        p_term = self.kp * error
        integral = self.integral + error * dt
        self.integral = max(-self.integral_limit, min(self.integral_limit, integral))
        i_term = self.ki * self.integral
        derivative = (error - self.previous_error) / dt
        d_term = self.kd * derivative
        
        output = p_term + i_term + d_term
        output = max(-self.maximum_output_abs, min(self.maximum_output_abs, output))
        self.previous_error = error

        return output