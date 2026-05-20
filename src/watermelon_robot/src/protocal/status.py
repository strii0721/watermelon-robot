from enum import Enum

class ST_SUPER_LOGIC_CONTROLLER(Enum):
    
    QUIT = 0
    STANDBY = 101
    TARGET_DETECTED = 201
    READY_TO_OPERATE = 202
    OPERATING = 203
    
    
class ST_SUB_LOGIC_CONTROLLER(Enum):
    
    QUIT = 0
    STOPPED = 101
    MOVING_FORWATD = 201