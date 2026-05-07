from nodes.node import Node
from utils.topic_utils import TopicUtils
import time

class Logger(Node):

    DAEMON_INTERVAL = 0.1
    LISTEN_LIST = [
        "LOGGER_ROBOTIC_ARM", 
        "LOGGER_MAIN_PROCESS"
    ]


    def __init__(self):

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