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


from mapper.camera_mapper import CameraMapper
import numpy as np
import pyrealsense2 as rs
import cv2
from utils import config

class CameraService: 

    def __init__(self) -> None:
        
        self._camera_mapper = CameraMapper()


    def read_current_frame(self) -> tuple | None: 

        (color_frame_array, 
         depth_frame_array, 
         depth_frame, 
         color_frame, 
         camera_intrinsics) = self._camera_mapper.retrieve_frames()

        if not color_frame or not depth_frame:
            return None
        
        return (color_frame_array, depth_frame_array, color_frame, depth_frame, camera_intrinsics)
    
    
    def calculate_median_depth(self, 
                               depth_frame, 
                               center_pixel: tuple,
                               window_size: int = 5):

        center_x, center_y = center_pixel
        radius = max(0, window_size // 2)
        width = depth_frame.get_width()
        height = depth_frame.get_height()
        xs = np.clip(np.arange(center_x - radius, center_x + radius + 1), 0, width - 1)
        ys = np.clip(np.arange(center_y - radius, center_y + radius + 1), 0, height - 1)
        vals = []

        for y in ys:
            for x in xs:
                d = depth_frame.get_distance(int(x), int(y))
                if d > 0:
                    vals.append(d)

        if len(vals) == 0:
            return 0.0
        
        return float(np.median(vals))

    
    def calculate_camera_coordinate(self,
                                    center_pixel: tuple,
                                    center_depth: float,
                                    camera_intrinsics) -> tuple:
        
        center_x, center_y = center_pixel
        camera_coordinate = rs.rs2_deproject_pixel_to_point(camera_intrinsics, [float(center_x), float(center_y)], center_depth) # type: ignore
        camera_coordinate = tuple(camera_coordinate)
        camera_coordinate_mm = tuple(x * 1000 for x in camera_coordinate)

        return camera_coordinate_mm
    
    def analysis_frame(self, 
                       model, 
                       device,
                       color_frame_array, 
                       depth_frame, 
                       camera_intrinsics) -> list:

        model = model
        device = device
        rtn = model.predict(source = color_frame_array, 
                            verbose = False, 
                            device = device, 
                            conf = config.model.confidence, 
                            iou = config.model.intersection_over_unio)
        results = rtn[0]
        boxes = results.boxes
        target_list = []

        if boxes is not None:
            for box in boxes:
                cls_id = int(box.cls[0].item())
                name = results.names.get(cls_id, str(cls_id))

                if name == 'watermelon':
                    box_pixel_x1, box_pixel_y1, box_pixel_x2, box_pixel_y2 = box.xyxy[0].tolist()
                    confidence = float(box.conf[0].item())
                    center_pixel_x = int((box_pixel_x1 + box_pixel_x2) / 2)
                    center_pixel_y = int((box_pixel_y1 + box_pixel_y2) / 2)
                    crosshair_pixel_x = center_pixel_x
                    crosshair_pixel_y = int(box_pixel_y1) - int((box_pixel_y1 - box_pixel_y2) / 8)
                    crosshair_coordinate_z = self.calculate_median_depth(depth_frame = depth_frame, 
                                                                                         center_pixel = (crosshair_pixel_x, crosshair_pixel_y),
                                                                                         window_size = 5)
                    
                    target = self.calculate_camera_coordinate(center_pixel = (crosshair_pixel_x, crosshair_pixel_y), 
                                                                                 center_depth = crosshair_coordinate_z,
                                                                                 camera_intrinsics = camera_intrinsics)
                    label = f'{name} {confidence:.2f}'
                    mark_size = 5
                    cv2.rectangle(color_frame_array, (int(box_pixel_x1), int(box_pixel_y1)), (int(box_pixel_x2), int(box_pixel_y2)), (0, 255, 0), 2)
                    cv2.circle(color_frame_array, (center_pixel_x, center_pixel_y), mark_size, (0, 0, 255), -1)
                    cv2.line(color_frame_array, (crosshair_pixel_x - mark_size, crosshair_pixel_y), (crosshair_pixel_x + mark_size, crosshair_pixel_y), (0, 0,255), 2)
                    cv2.line(color_frame_array, (crosshair_pixel_x, crosshair_pixel_y - mark_size), (crosshair_pixel_x, crosshair_pixel_y + mark_size), (0, 0,255), 2)
                    cv2.putText(color_frame_array, label, (int(box_pixel_x1), int(box_pixel_y1)-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                    cv2.putText(color_frame_array, f'Xc:{target[0]:.2f} Yc:{target[1]:.2f} Zc:{target[2]:.2f}', (int(box_pixel_x1), int(box_pixel_y1) + 20),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

                    if self.check_target_validation(target_coordinate = target): 
                        target_list.append(target)

        return target_list
    
    
    def check_target_validation(self, 
                                target_coordinate: tuple): 
        
        if not ((-100 < target_coordinate[0] and target_coordinate[0] < 100) and (-50 < target_coordinate[1] and target_coordinate[1] < 50) and (0 < target_coordinate[2] and target_coordinate[2] < 1000)):
            return False
        
        if target_coordinate[0] < 0:
            return False
        
        return True