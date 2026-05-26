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
    def check_flash_attention(cls):
        with suppress(Exception):
            import flash_attn

            return True
        return False

    @classmethod
    def load_model(cls,
                   model_name: str,
                   task: str,
                   use_engine: bool = False,
                   use_half: bool | None = None, 
                   device_no: str | int | None = None, 
                   image_size: list | None = None, 
                   confidence: float | None = None, 
                   iou: float | None = None):
        
        weights = os.path.join(package_share_dir, "model-weights", task, model_name)
        model = YOLO(weights)
        if image_size is not None: model.overrides["imgsz"] = image_size
        if confidence is not None: model.overrides["conf"] = confidence
        if iou is not None: model.overrides["iou"] = iou
        if not use_engine:
            if device_no is not None:
                device = torch.device(
                    f"cuda:{device_no}" if str(device_no).isdigit() else device_no
                )
            else:
                device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
            model.to(device)
            if use_half:
                model = model.half()
            
        return model
