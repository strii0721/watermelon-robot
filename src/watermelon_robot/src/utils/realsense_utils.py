#
# Author:       strii0721
# Email:        strii0721@outlook.com
# Created on:   Thu May 14 2026
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


import numpy as np
from sensor_msgs.msg import CameraInfo


class RealsenseUtils:

    @classmethod
    def convert_pyrealsense2cv2array(cls, 
                                     source_image):
        
        cv2_array = np.asanyarray(source_image.get_data())

        return cv2_array
    
    @classmethod
    def convert_intrinsics2camera_info(cls, rs_intrinsics):

        camera_info = CameraInfo()
        camera_info.width = rs_intrinsics.width
        camera_info.height = rs_intrinsics.height
        
        camera_info.distortion_model = "plumb_bob"
        camera_info.d = rs_intrinsics.coeffs

        camera_info.k = [rs_intrinsics.fx, 0.0, rs_intrinsics.ppx,
                         0.0, rs_intrinsics.fy, rs_intrinsics.ppy,
                         0.0, 0.0, 1.0]

        camera_info.r = [1.0, 0.0, 0.0,
                         0.0, 1.0, 0.0,
                         0.0, 0.0, 1.0]

        camera_info.p = [rs_intrinsics.fx, 0.0, rs_intrinsics.ppx, 0.0,
                         0.0, rs_intrinsics.fy, rs_intrinsics.ppy, 0.0,
                         0.0, 0.0, 1.0, 0.0]
                  
        return camera_info
