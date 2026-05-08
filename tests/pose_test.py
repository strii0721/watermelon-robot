from controller.robotic_arm_controller import RoboticArmController
from fairino import Robot
INITIAL_POSITION = [-820,-202,50]
IDEAL_POSITION = [-495,-102,475]
STANDBY_POSITION = [-300, -102, 450]

# robot = Robot.RPC()

# _, version = robot.GetSDKVersion()

# print(version)

controller = RoboticArmController()

controller.move_to_position(IDEAL_POSITION)

controller.close()