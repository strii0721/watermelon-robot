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
from watermelon_robot_interface.msg import IChassisDirectionControl
from watermelon_robot_interface.srv import IChassisStartStopControl
from protocol import QOSFile
from utils import config
from service import ChassisService
import time


class ChassisController(Node):

    def __init__(self):

        super().__init__("chassis_controller")
        CommonUtils.node_initializer(self)

        self.chassis_service = ChassisService()
        self.forward_speed = config.chassis.forward_speed
        self.last_control_time = 0
        self.controller = PIDController(pid_triple = config.chassis.pid_controller.pid_triple, 
                                        integral_limit = 50,
                                        output_limit = config.chassis.pid_controller.maximum_output_abs)


        self.sub_chassis_direction = self.create_subscription(msg_type = IChassisDirectionControl, 
                                                              topic = self.input_0,
                                                              qos_profile = QOSFile.reliable_qos, 
                                                              callback = self.correct_error)

        self.pub_cmd_vel = self.create_publisher(msg_type = Twist, 
                                                 topic = self.output_0,
                                                 qos_profile = QOSFile.reliable_qos, )
        
        self.srv_chassis_start_stop = self.create_service(srv_type = IChassisStartStopControl, 
                                                          srv_name = self.duplex_0, 
                                                          callback = self.chassis_start_stop)

        CommonUtils.node_initialized(self)
        
    def enable_chassis(self):
        """向底盘 SDK 订阅的话题直接发布线速度为初始速度并且无角速度的消息。
        """        

        twist_msg = self.chassis_service.start(forward_speed = self.forward_speed)
        self.pub_cmd_vel.publish(msg = twist_msg)
        self.last_control_time = time.time()

    def disable_chassis(self): 
        """向底盘 SDK 订阅的话题直接发布速度为0的消息。
        """        
        
        twist_msg = self.chassis_service.stop()
        self.pub_cmd_vel.publish(msg = twist_msg)
        self.last_control_time = 0

    def chassis_start_stop(self,
                           request: IChassisStartStopControl.Request, 
                           response: IChassisStartStopControl.Response) -> IChassisStartStopControl.Response:
        """控制底盘的启停

        Args:
            request (IChassisStartStopControl.Request): 请求对象。
            response (IChassisStartStopControl.Response): 响应对象。

        Returns:
            IChassisStartStopControl.Response: 响应对象。
        """        
        
        status = request.status
        if status: 
            self.enable_chassis()
        else: 
            self.disable_chassis()

        response.is_success = True

        return response

    def correct_error(self, 
                      control_variable_msg: IChassisDirectionControl):
        """接收底盘航向角度误差数据，调用 PID 控制器输出控制量，调用函数生成底盘 SDK 兼容的控制消息后发布。

        Args:
            control_variable_msg (IChassisDirectionControl): 包装角度误差数据的消息对象。
        """        
        
        now = time.time()
        if self.last_control_time:
            contro_interval = now - self.last_control_time
            angular_error = control_variable_msg.angular_error
            control_variable = self.controller.update_control_variable(error = angular_error, 
                                                                       control_interval = contro_interval)
            self.get_logger().info(f"当前角度误差：{angular_error} | 产生控制变量：{control_variable}")
            twist_msg = self.chassis_service.apply_control_variable(control_variable = control_variable,
                                                                    forward_speed = self.forward_speed, 
                                                                    yaw_angle = angular_error)
            self.pub_cmd_vel.publish(msg = twist_msg)
        self.last_control_time = now


def main():

    rclpy.init()
    chassis_controller = ChassisController()
    rclpy.spin(chassis_controller)
    chassis_controller.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
