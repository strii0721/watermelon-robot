from enum import Enum

class ST_SUPER_LOGIC_CONTROLLER(Enum):
    
    QUIT = 0
    
    DETECTING = 101
    
    TARGET_LOCKED = 201
    READY_TO_OPERATE = 202
    
    PENDING = 1024
    
    
class ST_SUB_LOGIC_CONTROLLER(Enum):
    
    QUIT = 0
    ENABLED = 101
    DISABLED = 201
    
    PENDING = 1024