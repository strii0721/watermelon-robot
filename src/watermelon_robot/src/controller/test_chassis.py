import rclpy
from rclpy.node import Node
from watermelon_robot_interface.msg import IChassisDirectionControl
from rclpy.qos import qos_profile_sensor_data
import math

class TestChassis(Node):

    def __init__(self): 

        super().__init__("test_chassis")
        self.tmr0 = self.create_timer(timer_period_sec = 0.05, 
                                      callback=self.call_chassis)
        self.pub = self.create_publisher(msg_type = IChassisDirectionControl, 
                                         topic = "t/signal/chassis/direction", 
                                         qos_profile = qos_profile_sensor_data)
        self.x = 0

    def call_chassis(self):
        
        angle = math.sin(self.x)
        self.x += 1
        msg = IChassisDirectionControl()
        msg.angular_error = 0.0
        self.pub.publish(msg = msg)

def main():

    rclpy.init()
    test_chassis = TestChassis()
    rclpy.spin(test_chassis)
    test_chassis.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__": 
    main()