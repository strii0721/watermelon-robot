from utils.thread_tuils import ThreadUtils
from nodes.impl.robotic_arm import RoboticArm
from nodes.impl.logger import Logger
from nodes.impl.simulation_targets import SimulationTargets
import time
from utils.topic_utils import TopicUtils

if __name__ == "__main__":

    LOGGER_TOPIC = "LOGGER_MAIN_PROCESS"
    TopicUtils.create_topic(topic_name = LOGGER_TOPIC)

    robotic_arm_0 = RoboticArm()
    logger_0 = Logger()
    simulation_targets_0 = SimulationTargets()
    
    handler_robotic_arm_0 = ThreadUtils.register(entity = robotic_arm_0)
    handler_logger_0 = ThreadUtils.register(entity = logger_0)
    handler_simulation_targets_0 = ThreadUtils.register(entity = simulation_targets_0)

    handler_robotic_arm_0.start()
    handler_logger_0.start()
    handler_simulation_targets_0.start()

    try:
        while True:
            message = f"主程序持续运行..."
            TopicUtils.publish(topic_name = LOGGER_TOPIC, 
                               message = message)
            time.sleep(3)
    except KeyboardInterrupt:
        print("主程序结束。")