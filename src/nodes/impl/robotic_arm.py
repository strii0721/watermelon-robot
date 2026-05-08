#
# Author:       strii0721
# Email:        strii0721@outlook.com
# Created on:   Thu May 07 2026
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


from nodes.node import Node
from controller.impl.default_robotic_arm_controller import DefaultRoboticArmController
from utils.topic_utils import TopicUtils
import time
from nodes.impl.camera import Camera

class RoboticArm(Node):

    DAEMON_INTERVAL = 0.1
    OPERATION_INTERVAL = 2

    TOPIC_LOGGER = "LOGGER_ROBOTIC_ARM"
    TOPIC_TARGET_QUEUE = "TARGET_QUEUE"

    STANDBY_POSITION = [0, 0, 0]

    def __init__(self):

        self.robotic_arm = DefaultRoboticArmController()
        TopicUtils.create_topic(self.TOPIC_LOGGER)
        TopicUtils.create_topic(self.TOPIC_TARGET_QUEUE)

    def daemon(self) -> None:

        while True:
            if (not TopicUtils.is_empty(topic_name = self.TOPIC_TARGET_QUEUE)): 
                target_position = TopicUtils.listen(topic_name = self.TOPIC_TARGET_QUEUE)
                log_message = f"目标位置：{target_position}"
                TopicUtils.publish(topic_name = self.TOPIC_LOGGER, 
                              message = log_message)
                state_code = self.robotic_arm.move_to_position(target_position = target_position)
                log_message = f"移动结束状态码：{state_code}"
                TopicUtils.publish(topic_name = self.TOPIC_LOGGER, 
                              message = log_message)
                
                # 切割的业务代码待补充
                if state_code == 0:
                    # TODO
                    pass
                
            else:
                if Camera.target_lock:
                    log_message = f"目标列表空，继续前进"
                    TopicUtils.publish(topic_name = self.TOPIC_LOGGER, 
                                  message = log_message)
                    Camera.target_lock = False

            time.sleep(self.DAEMON_INTERVAL)