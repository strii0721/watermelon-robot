from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    
    monitor = Node(
        package='watermelon_robot',
        executable='monitor',
        output='screen'
    )

    camera_controller = Node(
        package='watermelon_robot',
        executable='camera_controller',
        output='screen'
    )

    robotic_arm_controller = Node(
        package='watermelon_robot',
        executable='robotic_arm_controller',
        output='screen'
    )

    web_monitor = Node(
        package='watermelon_robot',
        executable='web_monitor',
        output='screen'
    )
    
    return LaunchDescription([
        # monitor,
        camera_controller,
        robotic_arm_controller,
        web_monitor
    ])