#
# Author:       strii0721
# Email:        strii0721@outlook.com
# Created on:   Sat May 09 2026
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
from scipy.spatial.transform import Rotation as R

class KinematicsUtils:

    @classmethod
    def calculate_pose_matrix_from_tuple(cls, 
                                         pose_tuple: tuple, 
                                         seq = "xyz") -> np.ndarray:

        x, y, z = pose_tuple[0], pose_tuple[1], pose_tuple[2]
        rx, ry, rz = pose_tuple[3], pose_tuple[4], pose_tuple[5]

        rotation = R.from_euler(seq = seq, 
                                angles = [rx, ry, rz], 
                                degrees = True)
        
        rotation_matrix = rotation.as_matrix()
        transform_matrix = np.eye(4)
        transform_matrix[0:3, 0:3] = rotation_matrix
        transform_matrix[0:3, 3] = [x, y, z]

        return transform_matrix