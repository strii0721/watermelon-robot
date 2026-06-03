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
from utils import NodeUtils
from geometry_msgs.msg import Twist
from watermelon_robot_interface.msg import ChassisControlSequence
from protocol import QoSFiles
from utils import config
from service import ChassisService
import time
from types import SimpleNamespace
import math
from rclpy.qos import qos_profile_sensor_data


class ChassisController(Node):

    def __init__(self):

        super().__init__("chassis_controller")
        NodeUtils.node_initializer(self)

        self.chassis_service = ChassisService()
        self.history = SimpleNamespace()
        self.history.last_control_time = time.time()
        
        pid_triple = config.chassis.pid_controller.pid_triple
        integral_limit = config.chassis.pid_controller.integral_limit
        output_limit = config.chassis.pid_controller.output_limit
        self.controller = PIDController(pid_triple = pid_triple, 
                                        integral_limit = integral_limit,
                                        output_limit = output_limit)

        self.chassis_control_sequence_subscriber = self.create_subscription(msg_type = ChassisControlSequence, 
                                                                            topic = self.input_0,
                                                                            qos_profile = qos_profile_sensor_data, 
                                                                            callback = self.correct_error)

        self.cmd_vel_publisher = self.create_publisher(msg_type = Twist, 
                                                       topic = self.output_0,
                                                       qos_profile = QoSFiles.chassis_control)

        NodeUtils.node_initialized(self)
        
    def correct_error(self, 
                      chassis_control_sequence: ChassisControlSequence):   
          
        now_time = time.time()
        if chassis_control_sequence.is_enabled:
            error_rads = chassis_control_sequence.error_rads
            forward_speed = chassis_control_sequence.forward_speed
            
            control_interval = now_time - self.history.last_control_time
            control_variable = self.controller.update_control_variable(error = error_rads, 
                                                                       control_interval = control_interval)
            error_degrees = math.degrees(error_rads)
            self.get_logger().info(f"当前弧度误差：{error_rads} | 角度误差：{error_degrees} | 产生控制变量：{control_variable}")
            
        else:
            control_variable = 0
            forward_speed = 0
            
        twist_msg = self.chassis_service.apply_control_variable(control_variable = control_variable,
                                                                forward_speed = forward_speed)
        self.cmd_vel_publisher.publish(msg = twist_msg)
        self.history.last_control_time = now_time
            

def main():

    rclpy.init()
    chassis_controller = ChassisController()
    rclpy.spin(chassis_controller)
    chassis_controller.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
