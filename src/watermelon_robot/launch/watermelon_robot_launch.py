from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    
    MONITOR_0 = Node(
        package='watermelon_robot',
        executable='monitor',
        name = "MONITOR_0",
        output='screen',
    )

    PRIESTESS_EYES_0 = Node(
        package='watermelon_robot',
        executable='realsense_controller',
        name = "PRIESTESS_EYES_0",
        output='screen'
    )

    robotic_arm_controller = Node(
        package='watermelon_robot',
        executable='robotic_arm_controller',
        name = "watermelon_robot",
        output='screen'
    )

    PRTS = Node(
        package = "watermelon_robot", 
        executable = "centre_controller", 
        name = "PRTS", 
        output = "screen"
    )
    
    return LaunchDescription([
        PRIESTESS_EYES_0,
        MONITOR_0, 
        PRTS
    ])