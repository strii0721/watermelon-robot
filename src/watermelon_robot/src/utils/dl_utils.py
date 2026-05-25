#
# Author:       strii0721
# Email:        strii0721@outlook.com
# Created on:   Mon May 25 2026
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
from utils import CVUtils
from ultralytics import YOLO
import numpy as np


class DLUtils: 
    
    @classmethod
    def predict_targets(cls, 
                        model: YOLO, 
                        color_image, 
                        depth_image, 
                        camera_intrinsics) -> list:

        rtn = model.predict(source = color_image, 
                            verbose = False)
        results = rtn[0]
        boxes = results.boxes
        target_list = []

        if boxes is not None:
            for box in boxes:
                cls_id = int(box.cls[0].item())
                name = results.names.get(cls_id, str(cls_id))

                if name == "watermelon":
                    box_pixel_x1, box_pixel_y1, box_pixel_x2, box_pixel_y2 = box.xyxy[0].tolist()
                    confidence = float(box.conf[0].item())
                    center_pixel_x = int((box_pixel_x1 + box_pixel_x2) / 2)
                    center_pixel_y = int((box_pixel_y1 + box_pixel_y2) / 2)
                    crosshair_pixel_x = center_pixel_x
                    crosshair_pixel_y = int(box_pixel_y1) - int((box_pixel_y1 - box_pixel_y2) / 8)
                    
                    target = CVUtils.calculate_camera_coordinate(center_pixel = (crosshair_pixel_x, crosshair_pixel_y), 
                                                                 depth_image = depth_image, 
                                                                 camera_intrinsics = camera_intrinsics)
                    label = f'{name} {confidence:.2f}'
                    mark_size = 5
                    cv2.rectangle(color_image, (int(box_pixel_x1), int(box_pixel_y1)), (int(box_pixel_x2), int(box_pixel_y2)), (0, 255, 0), 2)
                    cv2.circle(color_image, (center_pixel_x, center_pixel_y), mark_size, (0, 0, 255), -1)
                    cv2.line(color_image, (crosshair_pixel_x - mark_size, crosshair_pixel_y), (crosshair_pixel_x + mark_size, crosshair_pixel_y), (0, 0,255), 2)
                    cv2.line(color_image, (crosshair_pixel_x, crosshair_pixel_y - mark_size), (crosshair_pixel_x, crosshair_pixel_y + mark_size), (0, 0,255), 2)
                    cv2.putText(color_image, label, (int(box_pixel_x1), int(box_pixel_y1)-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                    cv2.putText(color_image, f'Xc:{target[0]:.2f} Yc:{target[1]:.2f} Zc:{target[2]:.2f}', (int(box_pixel_x1), int(box_pixel_y1) + 20),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

                    if DLUtils.check_target_validation(target_coordinate = target): 
                        target_list.append(target)

        return target_list

    @classmethod
    def predict_lane(cls,
                     model: YOLO, 
                     source_image: np.ndarray, 
                     canvas: np.ndarray,
                     roi_y_min_portion: float, 
                     roi_y_max_portion: float, 
                     detect_step: int) -> float:
        
        height, width = source_image.shape[:2]
        roi_y_min = int(height * roi_y_min_portion)
        roi_y_max = int(height * roi_y_max_portion)
        step = detect_step
        
        # 绘制当前航向参考点和参考航向线
        results = model.predict(source = source_image, 
                                verbose = False)
        reference_point = (int(width/2), roi_y_max)
        cv2.circle(canvas, reference_point, 5, (255, 0, 0), -1)
        reference_line = (reference_point, (reference_point[0], int((roi_y_min + roi_y_max)/2)))
        cv2.line(canvas, reference_line[0], reference_line[1], (255, 0, 0), 2)
        
        
        if results[0].masks is not None:
            mask_xy = results[0].masks.xy[0]
            polygon = np.array(mask_xy, dtype=np.int32)
            binary_mask = np.zeros((height, width), dtype=np.uint8)
            cv2.fillPoly(binary_mask, [polygon], 255)
            center_points = []
            for y in range(0, height, step):
                row = binary_mask[y, :]
                white_pixels = np.where(row == 255)[0]
                if len(white_pixels) > 0:
                    x_left = white_pixels[0]
                    x_right = white_pixels[-1]
                    x_center = int((x_left + x_right) / 2)
                    center_points.append((x_center, y))
            overlay = canvas.copy()
            cv2.fillPoly(overlay, [polygon], (0, 255, 0))
            cv2.addWeighted(overlay, 0.3, canvas, 0.7, 0, dst = canvas)
            # for i in range(len(center_points) - 1):
            #     pt1 = center_points[i]
            #     pt2 = center_points[i+1]
            #     cv2.line(source_image, pt1, pt2, (0, 0, 255), 3)
            #     cv2.circle(source_image, pt1, 2, (0, 255, 255), -1)
            if len(center_points) >= 2:
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
                                                navigation_line = navigate_line)

                # 绘制航向点十字准星
                mark_size = 5
                cv2.line(canvas, (navigate_point[0] - mark_size, navigate_point[1]), (navigate_point[0] + mark_size, navigate_point[1]), (0, 0, 255), 2)
                cv2.line(canvas, (navigate_point[0], navigate_point[1] - mark_size), (navigate_point[0], navigate_point[1] + mark_size), (0, 0, 255), 2)
            
            if angle >= 0:
                arow_color = (39, 127, 255)
            else: 
                arow_color = (0, 0, 255)
            thickness = 2
            cv2.arrowedLine(canvas, reference_point, navigate_point, arow_color, thickness, tipLength = 0.05)
        
        else:
            angle = 0.0
        
        return angle

    @classmethod
    def check_target_validation(cls, 
                                target_coordinate: tuple): 
        
        if not ((-200 < target_coordinate[0] and target_coordinate[0] < 200) and (-200 < target_coordinate[1] and target_coordinate[1] < 200) and (0 < target_coordinate[2] and target_coordinate[2] < 500)):
            return False
        
        if not(target_coordinate[0] > -50):
            return False
        
        return True
    
