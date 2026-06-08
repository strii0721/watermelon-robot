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


from rclpy.node import Node
import rclpy
from watermelon_robot.utils import config
from launch_ros.actions import Node as Node2
from rclpy.client import Client
from enum import IntEnum
from utils import CommUtils


class NodeUtils: 

    @classmethod
    def node_initializer(cls, 
                         node_entity: Node) -> None:
        """初始化节点对象，为其绑定属性，同时向终端打印初始化信息。也会为其创建状态机。

        Args:
            node_entity (Node): 初始化节点对象。
        """        
        
        node_name = node_entity.get_name()
        node_entity.get_logger().info(f"{node_name} 已上线，正在初始化...")
        
        node_config = getattr(config._node_initializer, node_name)
        attribute_dictionary = vars(node_config)
        for attribute_name in attribute_dictionary.keys():
            setattr(node_entity, attribute_name, getattr(node_config, attribute_name))

    @classmethod
    def node_initialized(cls, 
                         node_entity: Node) -> None:
        """节点对象初始化结束后行为。

        Args:
            node_entity (Node): 初始化节点对象。
        """        
        
        node_name = node_entity.get_name()
        node_entity.get_logger().info(f"{node_name} 初始化完成...")
        
    @classmethod
    def assemble_nodes(cls, 
                       node_name_list: list) -> list:
        """按名称自动根据名称装配节点。用于 ROS2 的 launch 机制。

        Args:
            node_name_list (list): 需要装配的节点名称。

        Returns:
            list: 节点对象列表。
        """        
        
        node_list = []
        
        for name in node_name_list:
            node_config = getattr(config._node_initializer, name)
            executable = node_config.executable
            node = Node2(
                package = "watermelon_robot",
                executable = executable, 
                name = name, 
                output = "screen"
            )
            node_list.append(node)
            
        return node_list
    
    @classmethod
    def comm_node_state(cls, 
                        caller: Node, 
                        handler: Client, 
                        state: IntEnum) -> rclpy.Future:
        
        timestamp = caller.get_clock().now().to_msg()
        header = CommUtils.create_header(stamp = timestamp)
        request = CommUtils.create_node_state_comm_request(header = header, 
                                                           state = state)
        future = handler.call_async(request = request)
        
        return future