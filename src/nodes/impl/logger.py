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

class Logger(Node):

    


    def __init__(self):

        self.DAEMON_INTERVAL = 0.001
        
        self.LISTEN_LIST = [
            "LOGGER_ROBOTIC_ARM", 
            "LOGGER_MAIN_PROCESS"
        ]

        for topic_name in self.LISTEN_LIST:
            TopicUtils.create_topic(topic_name = topic_name)
        

    def daemon(self) -> None:
        
        while True:
            for topic_name in TopicUtils._topic_dictionary.keys():
                if (topic_name in self.LISTEN_LIST and not TopicUtils.is_empty(topic_name = topic_name)): 
                    message = TopicUtils.listen(topic_name = topic_name)
                    self._log(source = topic_name, 
                              message = message)
                    time.sleep(self.DAEMON_INTERVAL)


    def _log(self, 
             source: str,
             message: str) -> None:
        timestamp = int(time.time())
        print(f"[{timestamp}][INFO][{source}] {message}")