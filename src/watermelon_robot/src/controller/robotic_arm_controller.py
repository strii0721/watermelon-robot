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
from service import RoboticArmService
from watermelon_robot_interface.srv import IRoboticArmAction
import time
from utils import config
from utils import CommonUtils
import numpy as np


class RoboticArmController(Node):

    def __init__(self):
        
        super().__init__('robotic_arm_controller')
        CommonUtils.node_initializer(self)

        # 此处可快速更换机械臂构型（当然是在配置文件里）
        robotic_arm = config.robotic_arm

        self.robotic_arm_service = RoboticArmService(ip = robotic_arm.ip, 
                                                     tool_standby_sextuplet = tuple(robotic_arm.tool_standby_sextuple), 
                                                     camera_pose_matix = np.array(robotic_arm.camera_pose_matix),
                                                     speed_rate = robotic_arm.speed_rate)
        
        state_code = self.robotic_arm_service.stand_by()
        if state_code == 0 :
            self.get_logger().info("机械臂已复位...")
        else:
            self.get_logger().warn(f"机械臂复位失败，状态码{state_code}")

        self.srv_robotic_arm_action_once = self.create_service(srv_type = IRoboticArmAction, 
                                                               srv_name = self.duplex_0, 
                                                               callback = self.robotic_arm_action_once)
        CommonUtils.node_initialized(self)
        
        
    def robotic_arm_action_once(self, 
                                request: IRoboticArmAction.Request, 
                                response: IRoboticArmAction.Response) -> IRoboticArmAction.Response:
        
        position = tuple(request.camera_position)
        state_code = self.robotic_arm_service.move_to_position(position = position, 
                                                                is_world_position = False)
        
        if state_code != 0 : 
            response.state_code = state_code
            self.robotic_arm_service.stand_by()
            return response
        
        # 剩余机械臂业务代码
        # TODO
        time.sleep(2)

        
        self.robotic_arm_service.stand_by()
        response.state_code = state_code

        return response
    
        
def main():

    rclpy.init()
    robotic_arm_controller = RoboticArmController()
    rclpy.spin(robotic_arm_controller)
    robotic_arm_controller.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()        