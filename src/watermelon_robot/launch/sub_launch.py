#
# Author:       strii0721
# Email:        strii0721@outlook.com
# Created on:   Wed May 20 2026
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
from launch_ros.actions import Node

def generate_launch_description():

    LYNCHPIN = Node(
        package = "watermelon_robot", 
        executable = "sub_logic_controller", 
        name = "LYNCHPIN", 
        output = "screen"
    )

    DWDB_221E = Node(
        package="watermelon_robot",
        executable="chassis_controller",
        name = "DWDB_221E",
        output="screen"
    )

    AMA_10 = Node(
        package="watermelon_robot",
        executable="realsense_controller",
        name = "AMA_10",
        output="screen"
    )

    ZERO_ORDER_OIL_TANK_0 = Node(
        package="watermelon_robot",
        executable="monitor",
        name = "ZERO_ORDER_OIL_TANK_0",
        output="screen"
    )

    ZERO_ORDER_OIL_TANK_1 = Node(
        package="watermelon_robot",
        executable="monitor",
        name = "ZERO_ORDER_OIL_TANK_1",
        output="screen"
    )
    
    return LaunchDescription([
        LYNCHPIN,
        DWDB_221E,
        AMA_10,
        ZERO_ORDER_OIL_TANK_0, 
        ZERO_ORDER_OIL_TANK_1
    ])