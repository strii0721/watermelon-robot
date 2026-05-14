from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():

    DWDB_221E = Node(
        package="watermelon_robot",
        executable="chassis_controller",
        name = "DWDB_221E",
        output="screen"
    )

    TEST = Node(
        package="watermelon_robot",
        executable="test_chassis",
        name = "TEST",
        output="screen"
    )

    return LaunchDescription([
        DWDB_221E,
        TEST
    ])