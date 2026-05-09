from controller.robotic_arm_controller import RoboticArmController
from fairino import Robot
INITIAL_POSITION = [-820,-202,50]
IDEAL_POSITION = [-495,-102,475]
STANDBY_POSITION = [-300, -102, 450]

# robot = Robot.RPC()

# _, version = robot.GetSDKVersion()

# print(version)

controller = RoboticArmController()

state_code = controller.stand_by()
print(state_code)

controller.close()