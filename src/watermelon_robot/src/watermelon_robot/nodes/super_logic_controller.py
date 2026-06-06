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
from watermelon_robot.utils import NodeUtils
from watermelon_robot_interface.srv import RoboticArmAction, LogicControllerComm
from typing import cast
from rclpy.qos import qos_profile_sensor_data
from watermelon_robot.utils import CommUtils
import time
from watermelon_robot.protocol import LogicControllerCommCode
from types import SimpleNamespace
from watermelon_robot_interface.msg import TargetList
import json
from enum import Enum

class STATE(Enum):
    
    QUIT = 0
    
    DETECTING = 101
    
    TARGET_LOCKED = 201
    READY_TO_OPERATE = 202
    
    PENDING = 1024


class SuperLogicController(Node):

    def __init__(self):

        super().__init__("super_logic_controller")
        NodeUtils.node_initializer(self)
        
        self.latest_frame = SimpleNamespace()
        self.current_target = None
        self.history = SimpleNamespace()
        self.history.target_list = []
        
        self.heartbeat_timer = self.create_timer(timer_period_sec = self.heartbeat_period_sec, 
                                                 callback = self.heartbeat)
        
        self.target_list_subscriber = self.create_subscription(msg_type = TargetList, 
                                                               topic = self.input_0, 
                                                               qos_profile = qos_profile_sensor_data, 
                                                               callback = self.cache_target_list)
        
        self.command_robotic_arm_client = self.create_client(srv_type = RoboticArmAction, 
                                                             srv_name = self.duplex_0)
        
        self.command_sub_logic_controller_client = self.create_client(srv_type = LogicControllerComm, 
                                                                      srv_name = self.duplex_1)
        
        NodeUtils.node_initialized(self)
        NodeUtils.transfer_node_state(self, STATE.DETECTING)
        
    def cache_target_list(self, 
                          target_list: TargetList) -> None:
        """缓存目标列表。

        Args:
            target_list (TargetList): 目标检测器回传的目标列表。
        """        
        
        target_list_json = target_list.target_list_json
        targets = json.loads(target_list_json)
        self.history.target_list = [tuple(target) for target in targets]
        
    def command_sub_logic_controller(self, 
                                     comm_code: LogicControllerCommCode) -> rclpy.Future:  
        """向下逻辑控制器发送命令。

        Args:
            comm_code (LogicControllerCommCode): 命令码。

        Returns:
            rclpy.Future: 下逻辑控制器响应的 Futrue 对象。
        """        
        
        timestamp = self.get_clock().now().to_msg()
        header = CommUtils.create_header(stamp = timestamp)
        request = CommUtils.create_logic_controller_comm_request(header = header, 
                                                                 comm_code = comm_code)
        future = self.command_sub_logic_controller_client.call_async(request)
        return future
        
    def start_chassis_done(self, 
                            future: rclpy.Future) -> None:
        """启动底盘请求的回调函数。此处应用重传机制，若一次请求失败则会在回调中重传请求，直到成功或超过重传次数限制。

        Args:
            future (rclpy.Future): 底盘响应的 Future 对象。
        """        
        
        response = cast(LogicControllerComm.Response, future.result())
        
        if response.is_success:
            self.get_logger().info(f"底盘启动成功！")
            NodeUtils.transfer_node_state(self, STATE.DETECTING)
        else:
            self.get_logger().info(f"底盘启动失败！")
            NodeUtils.transfer_node_state(self, STATE.QUIT)
            
    def start_chassis(self) -> None:
        """发布启动底盘的请求。
        """        

        future = self.command_sub_logic_controller(comm_code = LogicControllerCommCode.START_CHASSIS)
        future.add_done_callback(callback = self.start_chassis_done)
        NodeUtils.transfer_node_state(self, STATE.PENDING)
    
    def command_robotic_arm_done(self, 
                                 future: rclpy.Future) -> None:
        """机械臂动作的回调函数。

        Args:
            future (rclpy.Future): 动作响应的 Future 对象。
        """        
        
        response = cast(RoboticArmAction.Response, future.result())
        
        if response.is_success: 
            self.get_logger().info(f"机械臂执行完成")
            self.start_chassis()
        else:
            self.get_logger().warn(f"机械臂执行异常，异常信息：{response.message}")
            NodeUtils.transfer_node_state(self, STATE.QUIT)
        
    def command_robotic_arm(self) -> None:
        """获取当前目标坐标（手眼相机坐标系）并尝试进行一次机械臂动作。
        """        
        
        if not self.current_target:
            return
        
        request = RoboticArmAction.Request()
        request.timestamp = time.time()
        request.position_on_camera = self.current_target
        future = self.command_robotic_arm_client.call_async(request)
        future.add_done_callback(callback = self.command_robotic_arm_done)
        NodeUtils.transfer_node_state(self, STATE.PENDING)
        
    def stop_chassis_done(self, 
                             future: rclpy.Future) -> None:
        """停止底盘请求的回调函数。此处应用重传机制，若一次请求失败则会在回调中重传请求，直到成功或超过重传次数限制。

        Args:
            future (rclpy.Future): 底盘响应的 Future 对象。
        """        
        
        response = cast(LogicControllerComm.Response, future.result())
        
        if response.is_success:
            self.get_logger().info(f"底盘停止成功！")
            NodeUtils.transfer_node_state(self, STATE.READY_TO_OPERATE)
        else: 
            self.get_logger().info(f"底盘停止失败！")
            NodeUtils.transfer_node_state(self, STATE.QUIT)
            
    def stop_chassis(self) -> None:
        """发布停止底盘的请求。
        """        
        
        future = self.command_sub_logic_controller(comm_code = LogicControllerCommCode.STOP_CHASSIS)
        future.add_done_callback(callback = self.stop_chassis_done)
        NodeUtils.transfer_node_state(self, STATE.PENDING)
            
    def lock_target(self) -> None: 
        """锁定视野中最靠近前进方向反方向的目标。
        """        
        
        if not self.history.target_list:
            return
        
        target_list = self.history.target_list
        target_list.sort(key=lambda target: target[0])
        self.history.current_target = target_list[-1]
        self.get_logger().info(f"目标已锁定！当前目标（手眼相机参考系）：{self.history.current_target}")
        NodeUtils.transfer_node_state(self, STATE.TARGET_LOCKED)
        
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

            case STATE.DETECTING:
                self.lock_target()
                    
            case STATE.TARGET_LOCKED:
                self.stop_chassis()
            
            case STATE.READY_TO_OPERATE:
                self.command_robotic_arm()
            
            case STATE.PENDING:
                pass
                

def main():

    rclpy.init()
    super_logic_controller = SuperLogicController()
    rclpy.spin(super_logic_controller)
    super_logic_controller.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()