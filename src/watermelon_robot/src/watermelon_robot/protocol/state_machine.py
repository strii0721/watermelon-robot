#
# Author:       strii0721
# Email:        strii0721@outlook.com
# Created on:   Sun Jun 07 2026
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


from enum import IntEnum
from rclpy.node import Node
from watermelon_robot_interface.srv import StateComm
from typing import cast
from watermelon_robot.utils import NodeUtils


class BaseStates(IntEnum):
    
    DISABLED = 0
    
class NodeWithStateMachine(Node):
    
    def __init__(self, 
                 node_name: str, 
                 state_comm_channel: str):
        """意味着这是一个带状态机机制的 ROS2 节点。构造函数会为这个节点创建状态机，之后将状态机初始化为 DISABLED。

        Args:
            node_name (str): 节点默认名称。
        """        
        
        super().__init__(node_name = node_name)
        NodeUtils.node_initializer(node_entity = self)
        self.create_state_machine()
        self._state_comm_service = self.create_service(srv_type = StateComm, 
                                                       srv_name = state_comm_channel, 
                                                       callback = self._update_node_state)
        
    class STATES(BaseStates):
        DISABLED = 0
    
    def create_state_machine(self) -> None:

        self._state = BaseStates.DISABLED
        
    def _update_node_state(self, 
                           request: StateComm.Request, 
                           response: StateComm.Response) -> StateComm.Response:
        
        state = self.STATES(request.state)
        self.update_node_state(state = state)
        response.is_success = True
        
        return response

    def update_node_state(self, 
                          state: STATES) -> None:
        """转移节点状态机状态。若状态转移则会在终端打印相关信息。

        Args:
            state (ST_BASE): 目标状态。
        """        

        if not hasattr(self, "_state"):
            self.get_logger().warn(f"节点 {self.get_name()} 未创建状态机！")

        else:
            if self.retrieve_node_state() != state:
                self._state = state 
                self.get_logger().info(f"状态切换，当前状态：{self._state}")

    def retrieve_node_state(node_entity: Node) -> STATES | None:

        if not hasattr(node_entity, "_state"):
            node_entity.get_logger().warn(f"节点 {node_entity.get_name()} 未创建状态机！")
            return None
        else:
            return node_entity._state