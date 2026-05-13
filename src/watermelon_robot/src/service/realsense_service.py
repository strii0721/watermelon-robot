#
# Author:       strii0721
# Email:        strii0721@outlook.com
# Created on:   Sun May 10 2026
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


from mapper import RealsenseMapper
from utils import ImageUtils

class RealsenseService: 

    def __init__(self) -> None:
        
        self.camera_mapper = RealsenseMapper()


    def read_current_frame(self) -> list | None: 

        [color_frame, 
         depth_frame, 
         intrinsics] = self.camera_mapper.retrieve_frames()

        if color_frame is None or depth_frame is None:
            return None
        
        color_cv2array = ImageUtils.convert_pyrealsense2cv2array(source_image = color_frame)
        depth_cv2array = ImageUtils.convert_pyrealsense2cv2array(source_image = depth_frame)
        intrinsics_camera_info = ImageUtils.convert_intrinsics2camera_info(rs_intrinsics = intrinsics)
        
        return [color_cv2array, depth_cv2array, intrinsics_camera_info]