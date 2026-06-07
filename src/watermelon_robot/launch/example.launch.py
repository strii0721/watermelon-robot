#
# Author:       strii0721
# Email:        strii0721@outlook.com
# Created on:   Sat Jun 06 2026
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


from launch import LaunchDescription
from watermelon_robot.utils import NodeUtils


def generate_launch_description():
    
    node_list = [
        "PRIESTESS_EYES",       # Web UI
        
        "CELESTIAL_FULCRUM",    # 上逻辑控制器
        "PRESERVATOR",          # 手眼相机
        "LYNCHPIN",             # 目标检测器
        # "CAERULA_ARBOR",        # 机械臂
        
        "ORACLE",               # 下逻辑控制器
        "AMA_10",               # 巡线相机
        # "DWDB_221E",            # 底盘控制器
        "LONETRAIL",            # 航线检测器
        # "YAN"                   # 测试辅助节点
    ]
        
    
    return LaunchDescription(NodeUtils.assemble_nodes(node_list))