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



class ControlUtils:

    @classmethod
    def update_pid_control_variable(self, 
                                    pid_triple: tuple, 
                                    error: float, 
                                    dt: float): 

        kp, ki, kd = pid_triple

        p_term = kp * error
        
        self.integral += error * dt
        # 积分限幅 (Anti-windup)
        if self.integral_min is not None:
            self.integral = max(self.integral_min, self.integral)
        if self.integral_max is not None:
            self.integral = min(self.integral_max, self.integral)
            
        i_term = self.ki * self.integral
        
        derivative = (error - self.previous_error) / dt
        d_term = self.kd * derivative
        
        # 5. 计算总控制量
        output = p_term + i_term + d_term
        
        # 6. 输出限幅
        if self.output_min is not None:
            output = max(self.output_min, output)
        if self.output_max is not None:
            output = min(self.output_max, output)
            
        # 记录本次误差供下次微分使用
        self.previous_error = error
        
        return output