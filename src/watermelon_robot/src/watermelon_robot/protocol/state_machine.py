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
from watermelon_robot_interface.srv import NodeStateComm
from typing import cast
from watermelon_robot.utils import NodeUtils
import time

    
class NodeWithStateMachine(Node):
    
    class STATES(IntEnum):
        
        DISABLED = 0
    
    def __init__(self, 
                 node_name: str):
        """意味着这是一个带状态机机制的 ROS2 节点。构造函数会为这个节点创建状态机，之后将状态机初始化为 DISABLED。

        Args:
            node_name (str): 节点默认名称。
        """        
        
        super().__init__(node_name = node_name)
        NodeUtils.node_initializer(node_entity = self)
        self.create_state_machine()
        service_channel = f"node_state/{self.node_type}/{self.get_name()}"
        self._state_comm_service = self.create_service(srv_type = NodeStateComm, 
                                                       srv_name = service_channel, 
                                                       callback = self._update_node_state)
        
        self._heartbeat_timer = self.create_timer(timer_period_sec = self.heartbeat_period_sec, 
                                                  callback = self.heartbeat)
        self._last_heartbeat = time.time()
        self._real_heartbeat_period_sec = 0
        
    def heartbeat(self) -> None:
        """这是状态机的主循环函数，在这里使用 match-case 处理状态。
        """        
        
        now = time.time()
        self._real_heartbeat_period_sec = now - self._last_heartbeat
        self._last_heartbeat = now
        
    def get_real_heartbeat_period_sec(self) -> float:
        
        return self._real_heartbeat_period_sec
    
    def create_state_machine(self) -> None:

        self._state = self.STATES.DISABLED
        
    def _update_node_state(self, 
                           request: NodeStateComm.Request, 
                           response: NodeStateComm.Response) -> NodeStateComm.Response:
        """供节点间通信 service 回调的形式函数，自动监听频道并且修改节点状态。会自动调用真正的 update_node_state()。

        Args:
            request (StateComm.Request): 节点间状态更改请求。
            response (StateComm.Response): 节点间状态更改响应。

        Returns:
            StateComm.Response: 节点间状态更改响应。
        """        
        
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
                self.get_logger().info(f"状态切换，当前状态：{self.retrieve_node_state()}")

    def retrieve_node_state(node_entity: Node) -> STATES | None:
        """拉取当前节点状态机状态。

        Args:
            node_entity (Node): 节点实例对象。

        Returns:
            STATES | None: 节点状态机状态。若节点未创建状态机则输出警告到终端。
        """        

        if not hasattr(node_entity, "_state"):
            node_entity.get_logger().warn(f"节点 {node_entity.get_name()} 未创建状态机！")
            return None
        else:
            return node_entity._state