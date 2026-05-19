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


import rclpy
from rclpy.node import Node
from utils import CommonUtils
from geometry_msgs.msg import Twist
from watermelon_robot_interface.msg import IChassisDirectionControl
from watermelon_robot_interface.srv import IChassisStartStopControl
from protocal import QOSFile
from utils import config
from service import ChassisService
import time


class ChassisController(Node):

    def __init__(self):

        super().__init__("chassis_controller")
        CommonUtils.node_initializer(self)

        self.chassis_service = ChassisService()
        self.enable = True
        self.forward_speed = config.chassis.forward_speed
        self.pid_controller = PIDController(pid_triple = config.chassis.pid_controller.pid_triple, 
                                            maximum_output_abs = config.chassis.pid_controller.maximum_output_abs)


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

        twist_msg = self.chassis_service.start(forward_speed = self.forward_speed)
        self.pub_cmd_vel.publish(msg = twist_msg)
        self.enable = True


    def disable_chassis(self): 
        
        self.enable = False
        twist_msg = self.chassis_service.stop()
        self.pub_cmd_vel.publish(msg = twist_msg)
        

    def chassis_start_stop(self,
                           request: IChassisStartStopControl.Request, 
                           response: IChassisStartStopControl.Response) -> IChassisStartStopControl.Response:
        
        status = request.status
        if status: 
            self.enable_chassis()
        else: 
            self.disable_chassis()

        response.is_success = True

        return response


    def correct_error(self, 
                      control_variable_msg: IChassisDirectionControl):
        
        if self.enable:
            angular_error = control_variable_msg.angular_error
            angular_speed = self.pid_controller.update_control_variable(error = angular_error)
            self.get_logger().info(f"当前角度误差：{angular_error} | 产生控制变量（角速度）{angular_speed}")
            twist_msg = self.chassis_service.apply_control_variable(control_variable = angular_speed,
                                                                    forward_speed = self.forward_speed, 
                                                                    yaw_angle = angular_error)
            self.pub_cmd_vel.publish(msg = twist_msg)


class PIDController: 

    def __init__(self, 
                 pid_triple: tuple, 
                 maximum_output_abs):
        
        self.kp, self.ki, self.kd = pid_triple
        self.maximum_output_abs = maximum_output_abs
        self.integral = 0
        self.previous_error = 0
        self.previous_time = time.time()


    def update_control_variable(self, 
                                error):

        now = time.time()
        dt = now - self.previous_time
        self.previous_time = now

        p_term = self.kp * error
        
        self.integral += error * dt
            
        i_term = self.ki * self.integral
        
        derivative = (error - self.previous_error) / dt
        d_term = self.kd * derivative
        
        output = p_term + i_term + d_term
        
        sign = 1 if output >= 0 else -1

        if abs(output) > self.maximum_output_abs:
            output = sign * self.maximum_output_abs
            
        self.previous_error = error
        
        return output


def main():

    rclpy.init()
    chassis_controller = ChassisController()
    rclpy.spin(chassis_controller)
    chassis_controller.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
