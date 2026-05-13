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


import pyrealsense2 as rs
import numpy as np

class RealsenseMapper: 

    def __init__(self):

        self.pipeline = rs.pipeline()  # type: ignore
        self.pipeline_config = rs.config() # type: ignore
        self.pipeline_config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30) # type: ignore
        self.pipeline_config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30) # type: ignore
        self.pipeline.start(self.pipeline_config)
        self.align_method = rs.align(rs.stream.color) # type: ignore

    def retrieve_frames(self) -> list:

        frames = self.pipeline.wait_for_frames()
        aligned_frames = self.align_method.process(frames)
        aligned_color_frame = aligned_frames.get_color_frame()
        aligned_depth_frame = aligned_frames.get_depth_frame()
        intrinsics = aligned_depth_frame.profile.as_video_stream_profile().intrinsics

        return [aligned_color_frame, aligned_depth_frame, intrinsics]
    
    def stop(self):

        self.pipeline.stop() # type: ignore
