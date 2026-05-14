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


import cv2
import numpy as np
from sensor_msgs.msg import CameraInfo
import math


class CVUtils:

    @classmethod
    def calculate_median_depth(cls, 
                               depth_image, 
                               center_pixel: tuple,
                               window_size: int = 5):

        center_y, center_x = center_pixel
        radius = max(0, window_size // 2)
        height, width = depth_image.shape
        xs = np.clip(np.arange(center_x - radius, center_x + radius + 1), 0, width - 1)
        ys = np.clip(np.arange(center_y - radius, center_y + radius + 1), 0, height - 1)
        vals = []

        for y in ys:
            for x in xs:
                d = depth_image[int(x), int(y)]
                if d > 0:
                    vals.append(d)

        if len(vals) == 0:
            return 0.0
        
        return float(np.median(vals))

    @classmethod
    def calculate_camera_coordinate(cls,
                                    center_pixel: tuple,
                                    depth_image: np.ndarray,
                                    camera_intrinsics: CameraInfo) -> tuple:
        
        x_pixel, y_pixel = center_pixel
        Z = CVUtils.calculate_median_depth(depth_image = depth_image, 
                                              center_pixel = center_pixel)
        
        fx = camera_intrinsics.k[0]
        cx = camera_intrinsics.k[2]
        fy = camera_intrinsics.k[4]
        cy = camera_intrinsics.k[5]

        X = (x_pixel - cx) * Z / fx
        Y = (y_pixel - cy) * Z / fy

        return (X, Y, Z)

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

        Y, Cr, Cg, Cb = CVUtils.calculate_YCrCgCb(bgr_image = bgr_image)


        Cg = np.clip(Cr , 0, 255).astype(np.uint8)
        Cr = np.clip(Cb , 0, 255).astype(np.uint8)
        Cb = np.clip(Cg * 2 , 0, 255).astype(np.uint8)
        dCgCrCb = cv2.merge([Cg, Cr, Cb])

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
    def lane_detection_preprocess(cls, 
                                  source_image: np.ndarray, 
                                  roi_y_min_portion: float, 
                                  roi_y_max_portion: float) -> list:
        
        height, width = source_image.shape[:2]

        roi_y_min = int(height * roi_y_min_portion)
        roi_y_max = int(height * roi_y_max_portion)

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
        binary_morphology = CVUtils.not_maximum_connected_area_suppresion(binary_morphology)
        binary_morphology = cv2.morphologyEx(binary_morphology, cv2.MORPH_OPEN, kernel_square, iterations= 20)
        binary_morphology = cv2.dilate(binary_morphology, kernel_rectangle, iterations = 3)

        return [hsv, blurred, binary, binary_morphology]
  
    
    @classmethod
    def predict_lane(cls, 
                     canvas: np.ndarray, 
                     binary: np.ndarray, 
                     roi_y_min_portion: float, 
                     roi_y_max_portion: float, 
                     detect_step: int):
        
        height, width = binary.shape
        roi_y_min = int(height * roi_y_min_portion)
        roi_y_max = int(height * roi_y_max_portion)
        step = detect_step

        # 绘制当前航向参考点和参考航向线
        reference_point = (int(width/2), roi_y_max)
        cv2.circle(canvas, reference_point, 5, (255, 0, 0), -1)
        reference_line = (reference_point, (reference_point[0], int((roi_y_min + roi_y_max)/2)))
        cv2.line(canvas, reference_line[0], reference_line[1], (255, 0, 0), 2)

        center_points = []

        for y in range(roi_y_max, roi_y_min, -step):

            row = binary[y, :]

            reference_pixels = np.where(row == 255)[0]

            if len(reference_pixels) > 0:
                center_x = int(np.mean(reference_pixels))
                center_points.append((center_x, y))

        if len(center_points) > 2:

            # 绘制预测航向点
            points_arr = np.array(center_points)
            x = points_arr[:, 0]
            y = points_arr[:, 1]
            z = np.polyfit(y, x, 1)
            line_function = np.poly1d(z)
            y1 = roi_y_max
            x1 = int(line_function(y1))
            y2 = roi_y_min
            x2 = int(line_function(y2))
            navigate_point = (int((x1 + x2)/2), int((y1 + y2)/2))
            navigate_line = (reference_point, navigate_point)

            angle = CVUtils.claculate_angle(reference_line = reference_line, 
                                            navigate_line = navigate_line)

            mark_size = 5
            cv2.line(canvas, (navigate_point[0] - mark_size, navigate_point[1]), (navigate_point[0] + mark_size, navigate_point[1]), (0, 0, 255), 2)
            cv2.line(canvas, (navigate_point[0], navigate_point[1] - mark_size), (navigate_point[0], navigate_point[1] + mark_size), (0, 0, 255), 2)

            if angle >= 0:
                arow_color = (39, 127, 255)
            else: 
                arow_color = (0, 0, 255)
            thickness = 2
            cv2.arrowedLine(canvas, reference_point, navigate_point, arow_color, thickness, tipLength = 0.05)

            return angle
    
    @classmethod
    def claculate_angle(cls, 
                        reference_line, 
                        navigate_line):
        
        reference_start, reference_end = reference_line
        navigate_start, navigate_end = navigate_line
        vector_feference = (reference_end[0] - reference_start[0], -(reference_end[1] - reference_start[1]))
        vector_navigate = (navigate_end[0] - navigate_start[0], -(navigate_end[1] - navigate_start[1]))

        angle_reference = math.degrees(math.atan2(vector_feference[1], vector_feference[0]))
        angle_navigate = math.degrees(math.atan2(vector_navigate[1], vector_navigate[0]))

        angle_diff = angle_navigate - angle_reference
        angle_diff = (angle_diff + 90) % 180 - 90

        return angle_diff
