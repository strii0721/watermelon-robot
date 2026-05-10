#
# Author:       strii0721
# Email:        strii0721@outlook.com
# Created on:   Sun May 10 2026
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
from service.robotic_arm_service import RoboticArmService
from watermelon_robot_interface.srv import IRoboticArmAction
import numpy as np
from std_srvs.srv import Empty

class RoboticArmController(Node):

    def __init__(self, 
                 speed_rate: int = 30):
        
        super().__init__('robotic_arm_controller')

        self._robotic_arm_service = RoboticArmService(speed_rate = speed_rate)

        self.srv_robotic_arm_action_once = self.create_service(srv_type = IRoboticArmAction, 
                                                          srv_name = "s/robotic_arm/action_once", 
                                                          callback = self.robotic_arm_action_once)
        
        
    def robotic_arm_action_once(self, 
                                request: IRoboticArmAction.Request, 
                                response: IRoboticArmAction.Response) -> IRoboticArmAction.Response:
        
        position = tuple(request.camera_position)
        state_code = self._robotic_arm_service.move_to_position(position = position, 
                                                                is_world_position = False)
        
        # 剩余机械臂业务代码
        # TODO
        
        # 暂时都返回 0状态码，异常处理之后再说
        response.state_code = 0

        return response
    
    
        
def main():

    rclpy.init()
    robotic_arm_controller = RoboticArmController()
    rclpy.spin(robotic_arm_controller)
    robotic_arm_controller.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()        