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
            


            