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


from utils.thread_tuils import ThreadUtils
from nodes.impl.robotic_arm import RoboticArm
from nodes.impl.logger import Logger
from nodes.impl.simulation_targets import SimulationTargets
import time
from utils.topic_utils import TopicUtils
from nodes.impl.camera import Camera

if __name__ == "__main__":

    robotic_arm_0 = RoboticArm()
    logger_0 = Logger()
    simulation_targets_0 = SimulationTargets()
    camera_0 = Camera()
    
    handler_robotic_arm_0 = ThreadUtils.register(entity = robotic_arm_0)
    handler_logger_0 = ThreadUtils.register(entity = logger_0)
    # handler_simulation_targets_0 = ThreadUtils.register(entity = simulation_targets_0)
    handler_camera_0 = ThreadUtils.register(entity = camera_0)

    # handler_robotic_arm_0.start()
    # handler_logger_0.start()
    # handler_simulation_targets_0.start()
    handler_camera_0.start()

    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("主程序结束。")