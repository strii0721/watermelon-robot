from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    
    monitor_node = Node(
        package='watermelon_robot',
        executable='monitor',
        # name='monitor_node',
        output='screen'
    )

    camera_node = Node(
        package='watermelon_robot',
        executable='camera_controller',
        # name='camera_controller',
        output='screen'
    )

    arm_node = Node(
        package='watermelon_robot',
        executable='robotic_arm_controller',
        # name='robotic_arm_controller_node',
        output='screen'
    )
    
    return LaunchDescription([
        monitor_node,
        camera_node,
        arm_node
    ])