#
# Author:       strii0721
# Email:        strii0721@outlook.com
# Created on:   Tue May 26 2026
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


from service import RoboticArmService
import time

def main():
    
    robotic_arm_service = RoboticArmService(ip = "192.168.58.2", 
                                            tool_standby_sextuplet = [102, -282.5, 418, 180, -90, -90], 
                                            camera_pose_matix = [[0, -1, 0, 25],
                                                                 [1, 0, 0, 60],
                                                                 [0, 0, 1, 10],
                                                                 [0, 0, 0, 1]], 
                                            speed_rate = 20)
    scissors_id = 8
    close_flag = 1
    open_delay_sec = 2
    state_code = robotic_arm_service.scissors_close(tool_id = scissors_id, 
                                                    close_flag = close_flag)
    if state_code != 0:
        print(f"剪刀闭合失败！状态码：{state_code}")
        
    time.sleep(open_delay_sec)
    state_code = robotic_arm_service.scissors_open(tool_id = scissors_id, 
                                                   close_flag = close_flag)
        
    if state_code != 0:
        print(f"剪刀张开失败！状态码：{state_code}")    

if __name__ == "__main__":
    main()