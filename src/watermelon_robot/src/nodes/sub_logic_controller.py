#
# Author:       strii0721
# Email:        strii0721@outlook.com
# Created on:   Wed May 13 2026
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


import rclpy
from rclpy.node import Node
from utils import CommonUtils
from rclpy.qos import qos_profile_sensor_data
import message_filters
from watermelon_robot_interface.srv import ILogicControllerComm, ChassisStartStop
from watermelon_robot_interface.msg import LaneError, ChassisControlSequence
from utils import config
import time
from protocol import LogicControllerCommCode
from typing import cast
from types import SimpleNamespace
from utils import StateUtils, CommUtils
from enum import Enum


class STATE(Enum):
    
    QUIT = 0
    ENABLED = 101
    DISABLED = 201
    
    PENDING = 1024

class SubLogicController(Node):

    def __init__(self):

        super().__init__("sub_logic_controller")
        CommonUtils.node_initializer(self)

        self.history = SimpleNamespace()
        self.history.lane_error_rads = 0.0

        self.heartbeat_timer = self.create_timer(timer_period_sec = self.heartbeat_interval, 
                                                 callback = self.heartbeat)
        
        self.lane_error_subscriber = self.create_subscription(msg_type = LaneError, 
                                                              topic = self.input_0, 
                                                              qos_profile = qos_profile_sensor_data, 
                                                              callback = self.analysis_lane_error)
        
        self.chassis_control_sequence_publisher = self.create_publisher(msg_type = ChassisControlSequence, 
                                                                        topic = self.output_0, 
                                                                        qos_profile = qos_profile_sensor_data)
        
        self.srv_logic_controller_comm = self.create_service(srv_type = ILogicControllerComm, 
                                                             srv_name = self.duplex_0, 
                                                             callback = self.answer_super_logic_controller)
        
        self.cli_chassis_start_stop = self.create_client(srv_type = ChassisStartStop, 
                                                         srv_name = self.duplex_1)


        CommonUtils.node_initialized(self)
        StateUtils.transfer_node_state(self, STATE.ENABLED)

    def enable_chassis(self) -> rclpy.Future:
        """启动底盘。
        """        

        timestamp = time.time()
        header = CommUtils.create_header(stamp = timestamp)
        forward_speed = config.chassis.forward_speed
        chassis_control_sequence = CommUtils.create_chassis_control_sequence(header = header, 
                                                                             error_rads = 0, 
                                                                             forward_speed = forward_speed)
        self.chassis_control_sequence_publisher.publish(msg = chassis_control_sequence)
        
        StateUtils.transfer_node_state(self, STATE.ENABLED)
        
    def disable_chassis(self):
        """关闭底盘。
        """        
        
        timestamp = time.time()
        header = CommUtils.create_header(stamp = timestamp)
        chassis_control_sequence = CommUtils.create_chassis_control_sequence(header = header, 
                                                                             error_rads = 0, 
                                                                             forward_speed = 0,
                                                                             is_enabled = False)
        self.chassis_control_sequence_publisher.publish(msg = chassis_control_sequence)
        
        StateUtils.transfer_node_state(self, STATE.DISABLED)

    def answer_super_logic_controller(self, 
                                      request: ILogicControllerComm.Request, 
                                      response: ILogicControllerComm.Response) -> ILogicControllerComm.Response:
        """响应上逻辑控制器发来的逻辑控制器命令。此处应用重传机制，至少一次重传才会请求成功。

        Args:
            request (ILogicControllerComm.Request): 逻辑控制器命令请求。
            response (ILogicControllerComm.Response): 逻辑控制器命令响应。

        Returns:
            ILogicControllerComm.Response: 逻辑控制器命令响应。
        """        
        
        comm_code = request.comm_code
        retransmission = request.retransmission
        self.get_logger().info(f"收到上逻辑控制器通信，通信码 {comm_code}")
        response.is_success = False
        response.retransmission = retransmission
        
        match comm_code:
            case LogicControllerCommCode.DISABLE_CHASSIS:
                if self.state == STATE.DISABLED:
                    response.is_success = True
                else:
                    self.disable_chassis()

            case LogicControllerCommCode.ENABLE_CHASSIS: 
                if self.state == STATE.ENABLED:
                    response.is_success = True
                else:
                    self.enable_chassis()
                    
        return response
    
    def analysis_lane_error(self, 
                            lane_error: LaneError) -> None:     
        
        reach_terminal = lane_error.reach_terminal
        if reach_terminal: 
            self.disable_chassis()   
        else:
            self.history.lane_error_rads = lane_error.error_rads       
        
    def wait_quit(self) -> None:
        """等待退出。
        """        
        
        self.get_logger().warn(f"节点已进入退出状态，若未退出请手动退出...")
            
    def heartbeat(self) -> None:
        """节点的核心业务循环，加入了状态机机制。
        """        
        
        match self.state:
            case STATE.QUIT:
                self.wait_quit()
                
            case STATE.ENABLED:
                pass
                
            case STATE.DISABLED:
                pass
            
            case STATE.PENDING:
                pass


def main():

    rclpy.init()
    sub_logic_controller = SubLogicController()
    rclpy.spin(sub_logic_controller)
    sub_logic_controller.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()