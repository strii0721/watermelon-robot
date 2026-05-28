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
                     roi_y_min_portion: float, 
                     roi_y_max_portion: float, 
                     detect_step: int) -> list:
        """使用 YOLO 检测道路。

        Args:
            model (YOLO): 应该传入一个模型对象而非模型路径或者名字。
            source_image (np.ndarray): 相机获得的原始图像。
            roi_y_min_portion (float): 兴趣区域的顶部 y 坐标。
            roi_y_max_portion (float): 兴趣区域的底部 y 坐标。
            detect_step (int): 中心点绘制步长。

        Returns:
            list: 关键数据列表 [当前偏移角度, 最远点像素坐标]。
        """        
        
        height, width = source_image.shape[:2]
        roi_y_min = int(height * roi_y_min_portion)
        roi_y_max = int(height * roi_y_max_portion)
        results = model.predict(source = source_image, 
                                verbose = False)
        
        # 绘制当前航向参考点和参考航向线
        ego_point = (int(width/2), roi_y_max)
        cv2.circle(source_image, ego_point, 5, (255, 0, 0), -1)
        ego_direction = (ego_point, (ego_point[0], int((roi_y_min + roi_y_max)/2)))
        cv2.line(source_image, ego_direction[0], ego_direction[1], (255, 0, 0), 2)
        
        # 分析当前偏离角度
        reach_terminal = True
        angle = 0.0
        if results[0].masks is not None:
            mask_xy = results[0].masks.xy[0]
            lane_polygon = np.array(mask_xy, dtype=np.int32)
            mask_lane = np.zeros((height, width), dtype=np.uint8)
            cv2.fillPoly(mask_lane, [lane_polygon], 255)
            kernel_square = np.ones((2, 2), np.uint8)
            mask_lane = cv2.erode(mask_lane, kernel_square, iterations = 4)
            mask_lane = CVUtils.not_maximum_connected_area_suppresion(binary_image = mask_lane)
            mask_lane = cv2.dilate(mask_lane, kernel_square, iterations = 4)
            mask_lane_roi = mask_lane.copy()
            CVUtils.cut_roi(binary_image = mask_lane_roi, 
                            roi_y_min = roi_y_min, 
                            roi_y_max = roi_y_max)
            center_points = []
            for y in range(0, height, detect_step):
                row = mask_lane_roi[y, :]
                lane_pixels = np.where(row == 255)[0]
                if len(lane_pixels) > 0:
                    x_left = lane_pixels[0]
                    x_right = lane_pixels[-1]
                    x_center = int((x_left + x_right) / 2)
                    center_points.append((x_center, y))
                    if y < (roi_y_min + roi_y_max) / 2: 
                        reach_terminal = False
                        
            overlay_lane = np.zeros((height, width, 3), dtype = mask_lane.dtype)
            overlay_lane_roi = np.zeros((height, width, 3), dtype = mask_lane_roi.dtype)
            overlay_lane[:, :, 0] = mask_lane
            overlay_lane_roi[:, :, 1] = mask_lane_roi

            cv2.addWeighted(overlay_lane, 0.5, source_image, 1.0, 0, dst = source_image)
            cv2.addWeighted(overlay_lane_roi, 0.3, source_image, 1.0, 0, dst = source_image)
            
            for i in range(len(center_points) - 1):
                pt1 = center_points[i]
                pt2 = center_points[i+1]
                cv2.line(source_image, pt1, pt2, (0, 0, 255), 3)
                cv2.circle(source_image, pt1, 2, (0, 255, 255), -1)
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
                reference_point = (int((x1 + x2)/2), int((y1 + y2)/2))
                reference_direction = (ego_point, reference_point)
                angle = CVUtils.claculate_direction_error(ego_direction = ego_direction, 
                                                          reference_direction = reference_direction)

                # 绘制航向点十字准星
                mark_size = 5
                cv2.line(source_image, (reference_point[0] - mark_size, reference_point[1]), (reference_point[0] + mark_size, reference_point[1]), (0, 0, 255), 2)
                cv2.line(source_image, (reference_point[0], reference_point[1] - mark_size), (reference_point[0], reference_point[1] + mark_size), (0, 0, 255), 2)
                if angle >= 0:
                    arow_color = (39, 127, 255)
                else: 
                    arow_color = (0, 0, 255)
                thickness = 2
                cv2.arrowedLine(source_image, ego_point, reference_point, arow_color, thickness, tipLength = 0.05)
        
        return [reach_terminal, angle]

    @classmethod
    def check_target_validation(cls, 
                                target_coordinate: tuple) -> bool:
        """判断检测到的目标坐标是否合法。

        Args:
            target_coordinate (tuple): 目标坐标（相机参考系下）。

        Returns:
            bool: 目标合法性.
        """        
        
        if not ((-200 < target_coordinate[0] and target_coordinate[0] < 200) and (-200 < target_coordinate[1] and target_coordinate[1] < 200) and (0 < target_coordinate[2] and target_coordinate[2] < 500)):
            return False
        
        if not(target_coordinate[0] > -50):
            return False
        
        return True
    
