#
# Author:       strii0721
# Email:        strii0721@outlook.com
# Created on:   Thu May 21 2026
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
from matplotlib import pyplot as plt

class PIDController: 

    def __init__(self, 
                 pid_triple: tuple, 
                 maximum_output_abs: float):
        
        self.kp, self.ki, self.kd = pid_triple
        self.maximum_output_abs = maximum_output_abs
        self.integral = 0
        self.previous_error = 0
        self.previous_time = time.time()

    def update_control_variable(self, 
                                error: float) -> float:
        """根据误差应用 PID 控制器输出控制量。

        Args:
            error (float): 角度误差（角度）。

        Returns:
            float: 控制量。
        """        

        now = time.time()
        # dt = now - self.previous_time
        dt = 0.01
        print(f"实际控制间隔 {dt}")
        self.previous_time = now

        p_term = self.kp * error
        
        self.integral += error * dt
            
        i_term = self.ki * self.integral
        
        derivative = (error - self.previous_error) / dt
        d_term = self.kd * derivative
        
        # output = p_term + i_term + d_term
        output = p_term + d_term
        
        sign = 1 if output >= 0 else -1

        if abs(output) > self.maximum_output_abs:
            output = sign * self.maximum_output_abs
            
        self.previous_error = error
        
        return output
    
def main():
    
    
    iter = 0
    error = -5.0
    interval = 0.01
    pid_triple = (1.2, 0.1, 0.05)
    maximum_output_abs = 100
    
    plt.ion()

    fig, ax = plt.subplots(figsize=(10, 6))
    iter_data = []
    error_data = []
    line, = ax.plot(iter_data, error_data, 'b-', linewidth=2, label='Error')

    ax.set_title("Real-time Error Oscillation", fontsize=14)
    ax.set_xlabel("Iterations", fontsize=12)
    ax.set_ylabel("Error Value", fontsize=12)
    ax.axhline(0, color='red', linestyle='--', label='Target (Error=0)')
    ax.legend(loc='upper right')
    ax.grid(True, linestyle=':', alpha=0.7)
    
    controller = PIDController(pid_triple = pid_triple, 
                               maximum_output_abs = maximum_output_abs)
    while True:
        iter += 1
        print(f"=================================================")
        print(f"第 {iter} 迭代")
        control_variable = controller.update_control_variable(error = error)
        print(f"误差角度 {error}")
        print(f"控制量 {control_variable}")
        print(f"积分项 {controller.integral}")
        print(f"=================================================")
        error -= control_variable
        
        iter_data.append(iter)
        error_data.append(error)
        if len(iter_data) > 200:
            iter_data = iter_data[-200:]
            error_data = error_data[-200:]
        ax.relim()
        ax.autoscale_view()
        fig.canvas.draw()
        fig.canvas.flush_events()
        
        time.sleep(interval)
        
if __name__ == "__main__":
    
    main()