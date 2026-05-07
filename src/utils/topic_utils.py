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