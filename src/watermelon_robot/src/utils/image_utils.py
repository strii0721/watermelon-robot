#
# Author:       strii0721
# Email:        strii0721@outlook.com
# Created on:   Wed May 13 2026
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
import cv2
import time
from utils import config

class ImageUtils: 

    @classmethod
    def calculate_YCrCgCb(cls, 
                          bgr_image):

        b, g ,r = cv2.split(bgr_image)

        Y  = 0.299 * r + 0.587 * g + 0.114 * b
        Cr = (r - Y) / 1.402 + 128
        Cb = (b - Y) / 1.772 + 128
        Cg = (g - Y) / 0.825 + 128

        return (Y, Cr, Cg, Cb)


    @classmethod
    def BGR2DCgCrCb(cls, 
                    bgr_image):

        Y, Cr, Cg, Cb = ImageUtils.calculate_YCrCgCb(bgr_image = bgr_image)


        Cg = np.clip(Cr , 0, 255).astype(np.uint8)
        Cr = np.clip(Cb , 0, 255).astype(np.uint8)
        Cb = np.clip(Cg * 2 , 0, 255).astype(np.uint8)
        dCgCrCb = cv2.merge([Cg, Cr, Cb])

        # dCgCrCb = 2 * Cg - Cr - Cb
        # dCgCrCb = np.clip(dCgCrCb , 0, 255).astype(np.uint8)

        return dCgCrCb
    
    @classmethod
    def not_maximum_connected_area_suppresion(cls, 
                                              binary_image):

        contours, hierarchy = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if not contours:
            return binary_image

        largest_contour = max(contours, key=cv2.contourArea)

        supressed = np.zeros_like(binary_image)

        cv2.drawContours(supressed, [largest_contour], -1, 255, thickness=cv2.FILLED)

        return supressed
    
    
    @classmethod
    def preprocess_frame(cls, 
                         source_image: np.ndarray) -> list:
        
        height = source_image.shape[0]
        width = source_image.shape[1]

        roi_y_min = int(height * config.lane_detection.roi.y_min)
        roi_y_max = int(height * config.lane_detection.roi.y_max)

        hsv = cv2.cvtColor(source_image, cv2.COLOR_BGR2HSV)

        # 是时候使用 HSV 了，效果要比 RGB 好
        h, s, v = cv2.split(hsv)

        # dCgCrCb = CommonUtils.BGR2DCgCrCb(source_image)

        # gray = cv2.cvtColor(dCgCrCb, cv2.COLOR_BGR2GRAY)

        blurred = cv2.GaussianBlur(s, (3, 3), 0)

        _, binary = cv2.threshold(blurred, 40, 255, cv2.THRESH_OTSU)

        # 赞美形态学
        kernel_rectangle = np.ones((2, 1), np.uint8)
        kernel_square = np.ones((2, 2), np.uint8)
        binary_morphology = binary.copy()
        binary_morphology = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel_rectangle, iterations= 30)
        binary_morphology = cv2.erode(binary_morphology, kernel_rectangle, iterations = 3)
        binary_morphology[0:roi_y_min, :] = 0
        binary_morphology[roi_y_max:height, :] = 0
        binary_morphology = ImageUtils.not_maximum_connected_area_suppresion(binary_morphology)
        binary_morphology = cv2.morphologyEx(binary_morphology, cv2.MORPH_OPEN, kernel_square, iterations= 20)
        binary_morphology = cv2.dilate(binary_morphology, kernel_rectangle, iterations = 3)

        return [hsv, blurred, binary, binary_morphology]