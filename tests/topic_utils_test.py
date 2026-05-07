from utils.topic_utils import TopicUtils as TopicUtils

if __name__ == "__main__": 
    TopicUtils.create_topic(topic_name = "LOGGER_ROBOTIC_ARM")

    print(TopicUtils.is_empty(topic_name = "LOGGER_ROBOTIC_ARM"))

    TopicUtils.publish(topic_name = "LOGGER_ROBOTIC_ARM", 
                  message = [1,2,3])
    
    print(TopicUtils.is_empty(topic_name = "LOGGER_ROBOTIC_ARM"))

    TopicUtils.publish(topic_name = "LOGGER_ROBOTIC_ARM", 
                  message = [4,5,6])
    TopicUtils.publish(topic_name = "LOGGER_ROBOTIC_ARM", 
                  message = [7,8,9])
    print(f'{TopicUtils.listen(topic_name = "LOGGER_ROBOTIC_ARM")}')
    print(f'{TopicUtils.listen(topic_name = "LOGGER_ROBOTIC_ARM")}')
    print(f'{TopicUtils.listen(topic_name = "LOGGER_ROBOTIC_ARM")}')
    print(TopicUtils.is_empty(topic_name = "LOGGER_ROBOTIC_ARM"))