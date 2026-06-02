#
# Author:       strii0721
# Email:        strii0721@outlook.com
# Created on:   Thu May 14 2026
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


from control_algorithm import PIDController
import rclpy
from rclpy.node import Node
from utils import CommonUtils
from geometry_msgs.msg import Twist
from watermelon_robot_interface.srv import ChassisStartStop
from watermelon_robot_interface.msg import LaneError
from protocol import QOSFile
from utils import config, StateUtils
from service import ChassisService
import time
from enum import Enum

class STATE(Enum):
    
    ENABLED = 101
    DISABLED = 201


class ChassisController(Node):

    def __init__(self):

        super().__init__("chassis_controller")
        CommonUtils.node_initializer(self)

        self.chassis_service = ChassisService()
        self.forward_speed = config.chassis.forward_speed
        self.last_control_time = time.time()
        
        pid_triple = config.chassis.pid_controller.pid_triple
        integral_limit = config.chassis.pid_controller.integral_limit
        output_limit = config.chassis.pid_controller.output_limit
        self.controller = PIDController(pid_triple = pid_triple, 
                                        integral_limit = integral_limit,
                                        output_limit = output_limit)


        self.lane_error_subscription = self.create_subscription(msg_type = LaneError, 
                                                                topic = self.input_0,
                                                                qos_profile = QOSFile.reliable_qos, 
                                                                callback = self.cache_error)

        self.pub_cmd_vel = self.create_publisher(msg_type = Twist, 
                                                 topic = self.output_0,
                                                 qos_profile = QOSFile.reliable_qos)
        
        self.srv_chassis_start_stop = self.create_service(srv_type = ChassisStartStop, 
                                                          srv_name = self.duplex_0, 
                                                          callback = self.chassis_start_stop)
        
        self.heartbeat_timer = self.create_timer(timer_period_sec = self.heartbeat_period_sec, 
                                                 callback = self.heartbeat)

        CommonUtils.node_initialized(self)
        StateUtils.transfer_node_state(self, STATE.ENABLED)
        
    def cache_error(self, 
                    lane_error: LaneError) -> None:
        
        self.cached_lane_error = lane_error
        
    def enable_chassis(self):
        """向底盘 SDK 订阅的话题直接发布线速度为初始速度并且无角速度的消息。
        """        

        twist_msg = self.chassis_service.start(forward_speed = self.forward_speed)
        self.pub_cmd_vel.publish(msg = twist_msg)
        self.last_control_time = time.time()
        StateUtils.transfer_node_state(self, STATE.ENABLED)

    def disable_chassis(self): 
        """向底盘 SDK 订阅的话题直接发布速度为0的消息。
        """        
        
        twist_msg = self.chassis_service.stop()
        self.pub_cmd_vel.publish(msg = twist_msg)
        StateUtils.transfer_node_state(self, STATE.DISABLED)

    def chassis_start_stop(self,
                           request: ChassisStartStop.Request, 
                           response: ChassisStartStop.Response) -> ChassisStartStop.Response:
        """控制底盘的启停

        Args:
            request (ChassisStartStop.Request): 请求对象。
            response (ChassisStartStop.Response): 响应对象。

        Returns:
            ChassisStartStop.Response: 响应对象。
        """        
        
        target_state = request.target_state
        if target_state: 
            self.enable_chassis()
        else: 
            self.disable_chassis()

        response.is_success = True

        return response

    def correct_error(self):
        """接收底盘航向角度误差数据，调用 PID 控制器输出控制量，调用函数生成底盘 SDK 兼容的控制消息后发布。
        """        
        
        error_degrees = self.cached_lane_error.error_degrees
        now = time.time()
        contro_interval = now - self.last_control_time
        control_variable = self.controller.update_control_variable(error_degrees = error_degrees, 
                                                                   control_interval = contro_interval)
        self.get_logger().info(f"当前角度误差：{error_degrees} | 产生控制变量：{control_variable}")
        twist_msg = self.chassis_service.apply_control_variable(control_variable = control_variable,
                                                                forward_speed = self.forward_speed)
        self.pub_cmd_vel.publish(msg = twist_msg)
        self.last_control_time = now
            
    def heartbeat(self) -> None:
        
        match self.state:
            case STATE.ENABLED:
                self.correct_error()
            
            case STATE.DISABLED:
                pass


def main():

    rclpy.init()
    chassis_controller = ChassisController()
    rclpy.spin(chassis_controller)
    chassis_controller.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
