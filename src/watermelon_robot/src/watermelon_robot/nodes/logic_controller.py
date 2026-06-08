#
# Author:       strii0721
# Email:        strii0721@outlook.com
# Created on:   Mon Jun 08 2026
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


from watermelon_robot.protocol.node_with_state_machine import NodeWithStateMachine as Node
from watermelon_robot_interface.srv import NodeStateComm, RoboticArmAction
from watermelon_robot_interface.msg import TargetList, LaneError, ChassisControlSequence
from rclpy.qos import qos_profile_sensor_data
from watermelon_robot.utils.node_utils import NodeUtils
from watermelon_robot.utils.comm_utils import CommUtils
import rclpy
from watermelon_robot.nodes.realsense_controller import RealsenseController
from watermelon_robot.nodes.target_detector import TargetDetector
from watermelon_robot.nodes.lane_detector import LaneDetector
from watermelon_robot.nodes.robotic_arm_controller import RoboticArmController
from watermelon_robot.nodes.chassis_controller import ChassisController
from watermelon_robot.utils import config
from enum import IntEnum
import json
from typing import cast
import time


class LogicController(Node):
    
    class STATES(IntEnum):
        
        DISABLED = 0
        
        PENDING = 100
        DETECTING = 101
        
        TARGET_LOCKED = 201
        READY_TO_OPERATE = 202
        
        FINISH = 300
        
        ERROR = 400

    def __init__(self):

        super().__init__("sub_logic_controller")
        
        self.last_target_list = None
        self.last_lane_error = None
        self.reach_terminal_timer = None
        
        self.node_handler_DWDB_221E = self.create_client(srv_type = NodeStateComm, 
                                                         srv_name = self.channels.DWDB_221E)
        self.node_handler_AMA_10 = self.create_client(srv_type = NodeStateComm, 
                                                      srv_name = self.channels.AMA_10)
        self.node_handler_LYNCHPIN = self.create_client(srv_type = NodeStateComm, 
                                                        srv_name = self.channels.LYNCHPIN)
        self.node_handler_ORACLE = self.create_client(srv_type = NodeStateComm, 
                                                      srv_name = self.channels.ORACLE)
        self.node_handler_CAERULA_ARBOR = self.create_client(srv_type = NodeStateComm, 
                                                             srv_name = self.channels.CAERULA_ARBOR)
        self.node_handler_PRESERVATOR = self.create_client(srv_type = NodeStateComm, 
                                                           srv_name = self.channels.PRESERVATOR)
        
        self.target_list_subscriber = self.create_subscription(msg_type = TargetList, 
                                                               topic = self.channels.input_0, 
                                                               qos_profile = qos_profile_sensor_data, 
                                                               callback = self.cache_target_list)
        
        self.lane_error_subscriber = self.create_subscription(msg_type = LaneError, 
                                                              topic = self.channels.input_1, 
                                                              qos_profile = qos_profile_sensor_data, 
                                                              callback = self.cache_lane_error)
        
        self.chassis_control_sequence_publisher = self.create_publisher(msg_type = ChassisControlSequence, 
                                                                        topic = self.channels.output_0, 
                                                                        qos_profile = qos_profile_sensor_data)
        
        self.command_robotic_arm_client = self.create_client(srv_type = RoboticArmAction, 
                                                             srv_name = self.channels.duplex_0)
        
        NodeUtils.comm_node_state(caller = self, 
                                  handler = self.node_handler_CAERULA_ARBOR, 
                                  state = RealsenseController.STATES.ENABLED)
        NodeUtils.comm_node_state(caller = self,
                                  handler = self.node_handler_AMA_10, 
                                  state = RealsenseController.STATES.ENABLED)
        NodeUtils.comm_node_state(caller = self,
                                  handler = self.node_handler_LYNCHPIN, 
                                  state = TargetDetector.STATES.ENABLED)
        NodeUtils.comm_node_state(caller = self,
                                  handler = self.node_handler_ORACLE, 
                                  state = LaneDetector.STATES.ENABLED)
        NodeUtils.comm_node_state(caller = self,
                                  handler = self.node_handler_CAERULA_ARBOR, 
                                  state = RoboticArmController.STATES.MODE_SIMPLE)
        NodeUtils.comm_node_state(caller = self,
                                  handler = self.node_handler_PRESERVATOR, 
                                  state = ChassisController.STATES.STOP)
        
        NodeUtils.node_initialized(self)
        
    def forward_lane_error(self) -> None:
        """发布缓存的航线误差。（这个函数是被 heartbeat() 调用的，调用频率可能与误差接收频率不一致，后者是航线预测话题的回调函数，故接收频率与前视相机的帧率一致。）
        """          
        
        timestamp = self.get_clock().now().to_msg()
        header = CommUtils.create_header(stamp = timestamp)
        forward_speed = config.chassis.forward_speed
        error_rads = self.last_lane_error.error_rads
        chassis_control_sequence = CommUtils.create_chassis_control_sequence(header = header, 
                                                                             forward_speed = forward_speed,
                                                                             error_rads = self.error_rads)
        
        self.chassis_control_sequence_publisher.publish(msg = chassis_control_sequence)
        
    def check_terminal(self, 
                       reach_terminal: bool) -> None:
        """检查是否抵达终点，若是则停止底盘。当且仅当连续时长的帧检测到抵达道路边缘或检测不到道路，判断为抵达终点。

        Args:
            reach_terminal (bool): 当前帧是否符合到达终点的条件。
        """        
        
        if reach_terminal:
            if self.reach_terminal_timer:
                    if time.time() - self.reach_terminal_timer > config.chassis.stop_delay_sec:
                            return True
            else: 
                self.reach_terminal_timer = time.time()
        else: 
            self.reach_terminal_timer = None
        
        return False
        
    def cache_lane_error(self, 
                         lane_error: LaneError) -> None:
        
        
        reach_terminal = self.check_terminal(reach_terminal = lane_error.reach_terminal)
        
        if reach_terminal:
            self.update_node_state(self.STATES.FINISH)
        else:
            self.last_lane_error = lane_error
        
    def cache_target_list(self, 
                          target_list: TargetList) -> None:
        """缓存目标列表。

        Args:
            target_list (TargetList): 目标检测器回传的目标列表。
        """        
        
        self.last_target_list = target_list
        
    def detect_target(self) -> None: 
        """锁定视野中最靠近前进方向反方向的目标。
        """        
        
        if not self.last_target_list:
            return
        
        target_list_json = self.last_target_list.target_list_json
        targets = json.loads(target_list_json)
        target_list =  [tuple(target) for target in targets]
        target_list.sort(key=lambda target: target[0])
        self.current_target = target_list[-1]
        self.get_logger().info(f"目标已锁定！当前目标（手眼相机参考系）：{self.current_target}")
        self.update_node_state(state = self.STATES.TARGET_LOCKED)
        
    def start_chassis_done(self, 
                            future: rclpy.Future) -> None:
        """启动底盘请求的回调函数。此处应用重传机制，若一次请求失败则会在回调中重传请求，直到成功或超过重传次数限制。

        Args:
            future (rclpy.Future): 底盘响应的 Future 对象。
        """        
        
        response = cast(NodeStateComm.Response, future.result())
        
        if response.is_success:
            self.get_logger().info(f"底盘启动成功！")
            self.update_node_state(self.STATES.DETECTING)
        else:
            self.get_logger().info(f"底盘启动失败！")
            self.update_node_state(self.STATES.ERROR)
        
    def start_chassis(self):
        
        future = NodeUtils.comm_node_state(caller = self,
                                           handler = self.node_handler_PRESERVATOR, 
                                           state = ChassisController.STATES.START)
        future.add_done_callback(callback = self.start_chassis_done)
    
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
            self.update_node_state(self.STATES.ERROR)
        
    def command_robotic_arm(self) -> None:
        """获取当前目标坐标（手眼相机坐标系）并尝试进行一次机械臂动作。
        """        
        
        if not self.current_target:
            return
        
        timestamp = self.get_clock().now().to_msg()
        header = CommUtils.create_header(stamp = timestamp)
        request = CommUtils.create_robotic_arm_action_request(header = header, 
                                                              position_on_camera = self.current_target)
        future = self.command_robotic_arm_client.call_async(request)
        future.add_done_callback(callback = self.command_robotic_arm_done)
        self.update_node_state(state = self.STATES.PENDING)
        
    def stop_chassis_done(self, 
                          future: rclpy.Future) -> None:
        """停止底盘请求的回调函数。

        Args:
            future (rclpy.Future): 底盘响应的 Future 对象。
        """   
        
        response = cast(NodeStateComm.Response, future.result())
        
        if response.is_success:
            self.get_logger().info(f"底盘停止成功！")
            self.update_node_state(self.STATES.READY_TO_OPERATE)
        else: 
            self.get_logger().info(f"底盘停止失败！")
            self.update_node_state(self.STATES.ERROR)
            
        
    def stop_chassis(self):
        
        future = NodeUtils.comm_node_state(caller = self,
                                           handler = self.node_handler_PRESERVATOR, 
                                           state = ChassisController.STATES.STOP)
        future.add_done_callback(callback = self.stop_chassis_done)
        
    def error_quit(self) -> None:
        """等待退出。
        """        
        
        self.get_logger().warn(f"系统出现不可恢复故障，请手动退出...")
        
    def finish_quit(self) -> None:
        
        self.get_logger().warn(f"系统已完成当前任务，请手动退出...")
        
    def heartbeat(self):
        
        super().heartbeat()
        
        match self.retrieve_node_state():
            
            case self.STATES.DISABLED:
                pass
            
            case self.STATES.PENDING:
                pass
            
            case self.STATES.DETECTING:
                self.detect_target()
                self.forward_lane_error()
            
            case self.STATES.TARGET_LOCKED:
                self.stop_chassis()
            
            case self.STATES.READY_TO_OPERATE:
                self.command_robotic_arm()
                
            case self.STATES.FINISH:
                self.finish_quit()
            
            case self.STATES.ERROR:
                self.error_quit()
        
def main():

    rclpy.init()
    logic_controller = LogicController()
    rclpy.spin(logic_controller)
    logic_controller.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()