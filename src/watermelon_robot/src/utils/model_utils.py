#type: ignore
from contextlib import suppress
import torch
from ament_index_python.packages import get_package_share_directory
# import sys
# sys.path.append("/home/wheeltec/fr_ws/fr_python/yolov13")
from ultralytics import YOLO
import os
from utils import config

package_share_dir = get_package_share_directory('watermelon_robot')

class ModelUtils:

    @classmethod
    def setup_device(cls):

        if config.model.device is not None:
            device = torch.device(
                f"cuda:{config.model.device}" if str(config.model.device).isdigit() else config.model.device
            )
        else:
            device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        use_half = bool(config.model.use_half and device.type == "cuda")

        return device, use_half

    @classmethod
    def check_flash_attention(cls):
        with suppress(Exception):
            import flash_attn

            return True
        return False

    @classmethod
    def load_model(cls,
                   device: torch.device, 
                   use_half: bool):
        
        weights = os.path.join(package_share_dir, "model_weights", config.model.name)
        model = YOLO(weights)
        model.overrides["imgsz"] = 640
        model.overrides["conf"] = config.model.confidence
        model.overrides["iou"] = config.model.intersection_over_unio
        model.to(device)

        if use_half:
            model = model.half()
            
        return model
