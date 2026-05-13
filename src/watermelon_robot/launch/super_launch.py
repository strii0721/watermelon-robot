from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():

    CELESTIAL_FULCRUM = Node(
        package = "watermelon_robot", 
        executable = "super_logic_controller", 
        name = "CELESTIAL_FULCRUM", 
        output = "screen"
    )

    CAERULA_ARBOR = Node(
        package="watermelon_robot",
        executable="robotic_arm_controller",
        name = "CAERULA_ARBOR",
        output="screen"
    )

    PRESERVATOR = Node(
        package="watermelon_robot",
        executable="realsense_controller",
        name = "PRESERVATOR",
        output="screen"
    )

    PRIESTESS_EYES_0 = Node(
        package="watermelon_robot",
        executable="monitor",
        name = "CAERULA_ARBOR",
        output="screen"
    )
    
    return LaunchDescription([
        CELESTIAL_FULCRUM,
        CAERULA_ARBOR,
        PRESERVATOR,
        PRIESTESS_EYES_0
    ])