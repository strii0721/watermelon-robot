from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    
    priestess_eys_0 = Node(
        package='watermelon_robot',
        name = "PRIESTESS_EYES_0",
        executable='monitor',
        output='screen',
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
    
    return LaunchDescription([
        # monitor_alpha,
        camera_alpha_controller,
        # robotic_arm_controller,
        priestess_eys_0
    ])