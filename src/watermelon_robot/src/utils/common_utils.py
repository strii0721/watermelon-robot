#
# Author:       strii0721
# Email:        strii0721@outlook.com
# Created on:   Mon May 11 2026
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


import yaml
from ament_index_python.packages import get_package_share_directory
import os
import json
from types import SimpleNamespace
import sys
from rclpy.utilities import remove_ros_args
from rclpy.node import Node


class CommonUtils: 

    @classmethod
    def get_config(cls, 
                   config_profile: str = "default"): 
        
        package_share_dir = get_package_share_directory('watermelon_robot')
        config_dir = os.path.join(package_share_dir, "config", f"{config_profile}.yaml")
        with open(config_dir, 'r', encoding='utf-8') as f:
            config_dictionary = yaml.safe_load(f)
        config = json.loads(json.dumps(config_dictionary), object_hook=lambda d: SimpleNamespace(**d))
        config._config_dictionary = config_dictionary

        return config


    @classmethod
    def node_initializer(cls, 
                         node_entity: Node) -> None:
        node_name = node_entity.get_name()
        node_entity.get_logger().info(f"{node_name} 已上线，正在初始化...")
        from utils import config
        node_config = getattr(config._node_initializer, node_name)
        attribute_dictionary = vars(node_config)
        for attribute_name in attribute_dictionary.keys():
            setattr(node_entity, attribute_name, getattr(node_config, attribute_name))