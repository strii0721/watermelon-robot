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


from watermelon_robot.controller import PIDController
import rclpy
from watermelon_robot.protocol.state_machine import NodeWithStateMachine as Node
from watermelon_robot.utils import NodeUtils
from geometry_msgs.msg import Twist
from watermelon_robot_interface.msg import ChassisControlSequence
from watermelon_robot.protocol import QoSFiles
from watermelon_robot.utils import config
from watermelon_robot.service import ChassisService
from rclpy.qos import qos_profile_sensor_data
from enum import IntEnum


class ChassisController(Node):
    
    class STATES(IntEnum):
        
        DISABLED = 0
        START = 101
        STOP = 102

    def __init__(self):

        super().__init__("chassis_controller")

        self.chassis_service = ChassisService()
        
        pid_triple = config.chassis.pid_controller.pid_triple
        integral_limit = config.chassis.pid_controller.integral_limit
        output_limit = config.chassis.pid_controller.output_limit
        self.controller = PIDController(pid_triple = pid_triple, 
                                        integral_limit = integral_limit,
                                        output_limit = output_limit)

        self.chassis_control_sequence_subscriber = self.create_subscription(msg_type = ChassisControlSequence, 
                                                                            topic = self.channels.input_0,
                                                                            qos_profile = qos_profile_sensor_data, 
                                                                            callback = self.cache_chassis_control_sequence)

        self.cmd_vel_publisher = self.create_publisher(msg_type = Twist, 
                                                       topic = self.channels.output_0,
                                                       qos_profile = QoSFiles.chassis_control)

        NodeUtils.node_initialized(self)
        
    def cache_chassis_control_sequence(self, 
                                       chassis_control_sequence: ChassisControlSequence) -> None:
        
        self.last_chassis_control_sequence = chassis_control_sequence
        
    def forward(self) -> None:   
          

        forward_speed = self.last_chassis_control_sequence.forward_speed
        error_rads = self.last_chassis_control_sequence.error_rads
        
        control_variable = self.controller.update_control_variable(error = error_rads, 
                                                                   control_interval = self.get_real_heartbeat_period_sec())
        twist_msg = self.chassis_service.apply_control_variable(control_variable = control_variable,
                                                                forward_speed = forward_speed)
        self.cmd_vel_publisher.publish(msg = twist_msg)
        
        # error_degrees = math.degrees(error_rads)
        # self.get_logger().info(f"当前弧度误差：{error_rads} | 角度误差：{error_degrees} | 产生控制变量：{control_variable}")
        
    def hold(self) -> None:
        
        twist_msg = self.chassis_service.apply_control_variable(control_variable = 0.0,
                                                                forward_speed = 0.0)
        self.cmd_vel_publisher.publish(msg = twist_msg)
        
        
    def heartbeat(self) -> None:
        
        super().heartbeat()
        
        match self.retrieve_node_state():
            
            case self.STATES.DISABLED:
                pass
            
            case self.STATES.START:
                self.forward()
            
            case self.STATES.STOP:
                self.hold()
            

def main():

    rclpy.init()
    chassis_controller = ChassisController()
    rclpy.spin(chassis_controller)
    chassis_controller.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
