from controller.robotic_arm_controller import RoboticArmController
from fairino import Robot
import time

class DefaultRoboticArmController(RoboticArmController):

    def __init__(self, 
                 ip: str = "192.168.52.2", 
                 tool_numero: int = 0,
                 user_numero: int = 0, 
                 ideal_working_orientation: list = [90, 0, -90]):
        
        # self._robotic_arm = Robot.RPC(ip)
        self._tool_numero = tool_numero
        self._user_numero = user_numero
        self._ideal_working_orientation = ideal_working_orientation


    def close(self) -> None:

        self._robotic_arm.CloseRPC()

    def _be_safe(self, 
                 target: list) -> list:
        
        safe_target = []
        zero = 0.02

        for i in target:
            if(i == 0):
                safe_target.append(i + zero)
            else: 
                safe_target.append(i)

        return safe_target


    def move_to_pose(self, 
                     target_pose: list) -> int:
        
        safe_target_pose = self._be_safe(target = target_pose)
        # state_code = self._robotic_arm.MoveCart(desc_pos = safe_target_pose, 
        #                                         tool = self._tool_numero, 
        #                                         user = self._user_numero)
        time.sleep(2)
        state_code = 0
        return state_code
    
    def move_to_position(self, 
                         target_position: list) -> int:
        
        target_pose = target_position + self._ideal_working_orientation
        state_code = self.move_to_pose(target_pose = target_pose)
        
        return state_code