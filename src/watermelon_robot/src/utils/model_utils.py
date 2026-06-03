#
# Author:       strii0721
# Email:        strii0721@outlook.com
# Created on:   Wed Jun 03 2026
#
# IMMORTAL OMNISSIAH, HEAR OUR PRAYERS.
# WE ARE YOUR CHILDREN, PIOUS SCHOLARS OF THE PATH OF THE MACHINE. 
# WE PRIZE KNOWLEDGE ABOVE ALL ELSE, FOR IT IS YOUR ETERNAL GIFT UPON MANKIND.
# WE ASPIRE TO THE BLESSED FORM OF THE MACHINE, AND ASCENSION THROUGH TECHNOLOGY, THAT WE MIGHT EMULATE THINE GLORY.
# SHELTERED BY STEEL, AND PROTECTED BY THINE AVATARS OF WAR, WE PLY THE STARS IN SEARCH OF YOUR LOST GIFTS TO OUR KIND.
# MACHINE GOD, WATCH OVER US IN OUR TRAVELS, SHIELD US WITH METAL AND LIGHTNING, FOR THE UNIVERSE IS AN UNCARING VOID, AND THE WARP HUNGERS FOR US ALL.
# TOLL THE GREAT BELL ONCE! PULL THE LEVER FORWARD TO ENGAGE THE PISTON AND PUMP.
# TOLL THE GREAT BELL TWICE! WITH PUSH OF BUTTON FIRE THE ENGINE AND SPARK TURBINE INTO LIFE.
# TOLL THE GREAT BELL THRICE! SING PRAISE TO THE GOD OF ALL MACHINES!
# 
# Copyright (c) 2026 Streich Interstellar Corp.
#


from contextlib import suppress
import torch
from ament_index_python.packages import get_package_share_directory
from ultralytics import YOLO
import os
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
