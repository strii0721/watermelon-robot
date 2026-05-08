import argparse
from contextlib import suppress
import numpy as np
import torch
import sys

# sys.path.append("/home/wheeltec/fr_ws/fr_python/yolov13")
from ultralytics import YOLO


def parse_args():
    p = argparse.ArgumentParser(
        description="YOLOv13 model with optional FlashAttention setup."
    )
    p.add_argument(
        "--model",
        type=str,
        default="n",
        choices=["n", "s", "l", "x"],
        help="yolov13 model scale: n/s/l/x",
    )
    p.add_argument("--conf", type=float, default=0.80, help="confidence threshold")
    p.add_argument("--iou", type=float, default=0.45, help="NMS IoU threshold")
    p.add_argument(
        "--device",
        type=str,
        default=None,
        help='device to run the model on (e.g., "cpu", "0", "auto")',
    )
    p.add_argument(
        "--half", action="store_true", help="use half precision if CUDA is available"
    )
    p.add_argument(
        "--show_3d", action="store_true", help="show XYZ (camera frame) for bbox center"
    )
    return p.parse_args()


def setup_device(opt):
    if opt.device is not None:
        device = torch.device(
            f"cuda:{opt.device}" if str(opt.device).isdigit() else opt.device
        )
    else:
        device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    use_half = bool(opt.half and device.type == "cuda")
    return device, use_half


def check_flash_attention():
    with suppress(Exception):
        import flash_attn

        return True
    return False


def load_model(scale: str, device, use_half: bool, conf: float, iou: float):
    # weights = f'resource/model_weights/yolov13{scale}.pt'
    weights = f"resource/model_weights/yolo26/best.pt"
    # weights = f"resource/model_weights/best.pt"
    model = YOLO(weights)
    model.overrides["imgsz"] = 640
    model.overrides["conf"] = conf
    model.overrides["iou"] = iou
    model.to(device)
    if use_half:
        model.model.half()
    return model
