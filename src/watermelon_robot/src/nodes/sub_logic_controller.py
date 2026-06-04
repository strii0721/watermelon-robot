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
from utils import NodeUtils
from rclpy.qos import qos_profile_sensor_data
from watermelon_robot_interface.srv import LogicControllerComm
from watermelon_robot_interface.msg import LaneError, ChassisControlSequence
from utils import config
from protocol import LogicControllerCommCode
from types import SimpleNamespace
from utils import StateUtils, CommUtils
from enum import Enum


class STATE(Enum):
    
    QUIT = 0
    START = 101
    STOP = 201

class SubLogicController(Node):

    def __init__(self):

        super().__init__("sub_logic_controller")
        NodeUtils.node_initializer(self)

        self.history = SimpleNamespace()
        self.history.lane_error_rads = 0.0

        self.heartbeat_timer = self.create_timer(timer_period_sec = self.heartbeat_period_sec, 
                                                 callback = self.heartbeat)
        
        self.lane_error_subscriber = self.create_subscription(msg_type = LaneError, 
                                                              topic = self.input_0, 
                                                              qos_profile = qos_profile_sensor_data, 
                                                              callback = self.cache_lane_error)
        
        self.chassis_control_sequence_publisher = self.create_publisher(msg_type = ChassisControlSequence, 
                                                                        topic = self.output_0, 
                                                                        qos_profile = qos_profile_sensor_data)
        
        self.srv_logic_controller_comm = self.create_service(srv_type = LogicControllerComm, 
                                                             srv_name = self.duplex_0, 
                                                             callback = self.answer_super_logic_controller)

        NodeUtils.node_initialized(self)
        StateUtils.transfer_node_state(self, STATE.STOP)
        
    def cache_lane_error(self, 
                         lane_error: LaneError) -> None:
        """缓存航线误差。

        Args:
            lane_error (LaneError): 频道接收到的航线误差。
        """        
        
        reach_terminal = lane_error.reach_terminal
        if reach_terminal: 
            self.stop_chassis()   
        else:
            self.history.lane_error_rads = lane_error.error_rads 
            
    def forward_lane_error(self) -> None:
        """发布缓存的航线误差。（这个函数是被 heartbeat() 调用的，调用频率可能与误差接收频率不一致，后者是航线预测话题的回调函数，故接收频率与前视相机的帧率一致。）
        """          
        
        timestamp = self.get_clock().now().to_msg()
        header = CommUtils.create_header(stamp = timestamp)
        forward_speed = config.chassis.forward_speed
        chassis_control_sequence = CommUtils.create_chassis_control_sequence(header = header, 
                                                                             error_rads = self.history.lane_error_rads, 
                                                                             forward_speed = forward_speed)
        
        self.chassis_control_sequence_publisher.publish(msg = chassis_control_sequence)

    def start_chassis(self) -> None:
        """启动底盘。
        """        

        timestamp = self.get_clock().now().to_msg()
        header = CommUtils.create_header(stamp = timestamp)
        forward_speed = config.chassis.forward_speed
        chassis_control_sequence = CommUtils.create_chassis_control_sequence(header = header, 
                                                                             error_rads = 0, 
                                                                             forward_speed = forward_speed)
        self.chassis_control_sequence_publisher.publish(msg = chassis_control_sequence)
        
        StateUtils.transfer_node_state(self, STATE.START)
        
    def stop_chassis(self) -> None:
        """关闭底盘。
        """        
        
        timestamp = self.get_clock().now().to_msg()
        header = CommUtils.create_header(stamp = timestamp)
        chassis_control_sequence = CommUtils.create_chassis_control_sequence(header = header, 
                                                                             error_rads = 0, 
                                                                             forward_speed = 0,
                                                                             is_enabled = False)
        self.chassis_control_sequence_publisher.publish(msg = chassis_control_sequence)
        
        StateUtils.transfer_node_state(self, STATE.STOP)

    def answer_super_logic_controller(self, 
                                      request: LogicControllerComm.Request, 
                                      response: LogicControllerComm.Response) -> LogicControllerComm.Response:
        """响应上逻辑控制器发来的逻辑控制器命令。此处应用重传机制，至少一次重传才会请求成功。

        Args:
            request (ILogicControllerComm.Request): 逻辑控制器命令请求。
            response (ILogicControllerComm.Response): 逻辑控制器命令响应。

        Returns:
            ILogicControllerComm.Response: 逻辑控制器命令响应。
        """        
        
        comm_code = request.comm_code
        self.get_logger().info(f"收到上逻辑控制器通信，通信码 {comm_code}")
        timestamp = self.get_clock().now().to_msg()
        header = CommUtils.create_header(stamp = timestamp)
        match comm_code:
            case LogicControllerCommCode.STOP_CHASSIS.value:
                self.stop_chassis()
                response.header = header
                response.is_success = True

            case LogicControllerCommCode.START_CHASSIS.value: 
                self.start_chassis()
                response.header = header
                response.is_success = True
                    
        return response
        
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
                
            case STATE.START:
                self.forward_lane_error()
                
            case STATE.STOP:
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