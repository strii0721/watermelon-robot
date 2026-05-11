#type: ignore
import argparse
from contextlib import suppress
import torch
from ament_index_python.packages import get_package_share_directory
# import sys
# sys.path.append("/home/wheeltec/fr_ws/fr_python/yolov13")
from ultralytics import YOLO
import os
import config.default as config
import yaml

package_share_dir = get_package_share_directory('watermelon_robot')

class ModelUtils:

    @classmethod
    def parse_args(cls):

        argument_parser = argparse.ArgumentParser(
            description="YOLOv13 model with optional FlashAttention setup."
        )
        argument_parser.add_argument(
            "--model",
            type=str,
            default="n",
            choices=["n", "s", "l", "x"],
            help="yolov13 model scale: n/s/l/x",
        )
        argument_parser.add_argument("--conf", type=float, default=0.25, help="confidence threshold")
        argument_parser.add_argument("--iou", type=float, default=0.45, help="NMS IoU threshold")
        argument_parser.add_argument(
            "--device",
            type=str,
            default=None,
            help='device to run the model on (e.g., "cpu", "0", "auto")',
        )
        argument_parser.add_argument(
            "--half", action="store_true", help="use half precision if CUDA is available"
        )
        argument_parser.add_argument(
            "--show_3d", action="store_true", help="show XYZ (camera frame) for bbox center"
        )

        known_args, _ = argument_parser.parse_known_args()

        return known_args

    @classmethod
    def setup_device(cls, 
                     config):
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
                   name: str, 
                   device: torch.device, 
                   use_half: bool, 
                   conf: float, 
                   iou: float):
        # weights = f'resource/model_weights/yolov13{scale}.pt'
        # weights = f"resource/model_weights/best.pt"
        weights = os.path.join(package_share_dir, "model_weights", name)
        model = YOLO(weights)
        model.overrides["imgsz"] = 640
        model.overrides["conf"] = conf
        model.overrides["iou"] = iou
        model.to(device)
        if use_half:
            model = model.half()
        return model
