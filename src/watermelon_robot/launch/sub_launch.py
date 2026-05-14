from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():

    LYNCHPIN = Node(
        package = "watermelon_robot", 
        executable = "sub_logic_controller", 
        name = "LYNCHPIN", 
        output = "screen"
    )

    DWDB_221E = Node(
        package="watermelon_robot",
        executable="chassis_controller",
        name = "DWDB_221E",
        output="screen"
    )

    AMA_10 = Node(
        package="watermelon_robot",
        executable="realsense_controller",
        name = "AMA_10",
        output="screen"
    )

    ZERO_ORDER_OIL_TANK_0 = Node(
        package="watermelon_robot",
        executable="monitor",
        name = "ZERO_ORDER_OIL_TANK_0",
        output="screen"
    )
    
    return LaunchDescription([
        LYNCHPIN,
        DWDB_221E,
        AMA_10,
        ZERO_ORDER_OIL_TANK_0
    ])