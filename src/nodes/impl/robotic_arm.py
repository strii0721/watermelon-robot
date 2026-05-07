from nodes.node import Node
from controller.impl.default_robotic_arm_controller import DefaultRoboticArmController
from utils.topic_utils import TopicUtils
import time

class RoboticArm(Node):

    DAEMON_INTERVAL = 0.1
    OPERATION_INTERVAL = 2

    TOPIC_NAME_LOGGER = "LOGGER_ROBOTIC_ARM"
    TOPIC_NAME_TARGET_QUEUE = "TARGET_QUEUE"

    def __init__(self):

        self.robotic_arm = DefaultRoboticArmController()
        TopicUtils.create_topic(self.TOPIC_NAME_LOGGER)
        TopicUtils.create_topic(self.TOPIC_NAME_TARGET_QUEUE)

    def daemon(self) -> None:

        while True:
            if (not TopicUtils.is_empty(topic_name = self.TOPIC_NAME_TARGET_QUEUE)): 
                target_position = TopicUtils.listen(topic_name = self.TOPIC_NAME_TARGET_QUEUE)
                log_message = f"目标位置：{target_position}\n"
                TopicUtils.publish(topic_name = self.TOPIC_NAME_LOGGER, 
                              message = log_message)
                state_code = self.robotic_arm.move_to_position(target_position = target_position)
                log_message = f"移动结束状态码：{state_code}\n"
                TopicUtils.publish(topic_name = self.TOPIC_NAME_LOGGER, 
                              message = log_message)
                time.sleep(2)
            else:
                log_message = f"目标列表空\n"
                TopicUtils.publish(topic_name = self.TOPIC_NAME_LOGGER, 
                              message = log_message)

            time.sleep(self.DAEMON_INTERVAL)