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
from utils.topic_utils import TopicUtils
import time

class SimulationTargets(Node):

    DAEMON_INTERVAL = 0.5
    TOPIC_NAME_TARGET_QUEUE = "TARGET_QUEUE"

    def __init__(self):
        TopicUtils.create_topic(topic_name = self.TOPIC_NAME_TARGET_QUEUE)

    def daemon(self):
        
        for i in range(100):
            fake_target = [i, 0, 0]
            TopicUtils.publish(topic_name=  self.TOPIC_NAME_TARGET_QUEUE, 
                               message = fake_target)
            if i % 10 == 0:
                time.sleep(10)
        
        time.sleep(self.DAEMON_INTERVAL)
            


            