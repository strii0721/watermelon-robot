from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    
    monitor_alpha = Node(
        package='watermelon_robot',
        executable='monitor_alpha',
        output='screen'
    )

    camera_alpha_controller = Node(
        package='watermelon_robot',
        executable='camera_alpha_controller',
        output='screen'
    )

    robotic_arm_controller = Node(
        package='watermelon_robot',
        executable='robotic_arm_controller',
        output='screen'
    )

    web_monitor_alpha = Node(
        package='watermelon_robot',
        executable='web_monitor_alpha',
        output='screen'
    )
    
    return LaunchDescription([
        # monitor_alpha,
        camera_alpha_controller,
        robotic_arm_controller,
        web_monitor_alpha
    ])