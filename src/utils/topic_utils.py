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


from typing import Any

class TopicUtils:

    _topic_dictionary = {}

    @classmethod
    def create_topic(cls, topic_name: str) -> None:

        if(topic_name not in TopicUtils._topic_dictionary): 
            TopicUtils._topic_dictionary[topic_name] = []
        
    @classmethod
    def remove_topic(cls, topic_name: str) -> None:
        if (topic_name in TopicUtils._topic_dictionary): 
            del TopicUtils._topic_dictionary[topic_name]
        else: 
            raise Exception(f"话题不存在")
        
        
    @classmethod
    def publish(cls, topic_name: str, 
                message: Any) -> None:
        
        if (topic_name in TopicUtils._topic_dictionary): 
            TopicUtils._topic_dictionary[topic_name].append(message)
        else: 
            raise Exception(f"话题不存在")


    @classmethod
    def listen(cls, topic_name: str) -> Any:
        
        if (topic_name in TopicUtils._topic_dictionary):
            message = TopicUtils._topic_dictionary[topic_name].pop(0)
        else: 
            raise Exception(f"话题不存在")
        return message
    
    @classmethod
    def is_empty(cls, topic_name: str) -> bool:
        
        if(topic_name in TopicUtils._topic_dictionary and TopicUtils._topic_dictionary[topic_name] == []): 
            return True
        else: 
            return False