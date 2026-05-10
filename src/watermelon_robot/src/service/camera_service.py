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

class CameraService: 

    def __init__(self) -> None:
        
        self._camera_mapper = CameraMapper()
        self._target_lock = False

    def get_target_lock(self) -> bool:

        return self._target_lock
    
    def set_target_lock(self, 
                        status: bool) -> None:
        
        self._target_lock = status

    def get_raw_frame(self) -> None | tuple: 

        image_color, image_depth, aligned_depth_frame, aligned_color_frame, camera_intrinsics = self._camera_mapper.get_frames()

        if not aligned_color_frame or not aligned_depth_frame:

            return None
        
        return (image_color, image_depth, aligned_depth_frame, aligned_color_frame, camera_intrinsics)
    
    def calculate_median_depth(self, 
                               depth_frame, 
                               center_x: int, 
                               center_y: int, 
                               window_size: int = 5):

        rad = max(0, window_size // 2)
        w = depth_frame.get_width()
        h = depth_frame.get_height()

        xs = np.clip(np.arange(center_x - rad, center_x + rad + 1), 0, w - 1)
        ys = np.clip(np.arange(center_y - rad, center_y + rad + 1), 0, h - 1)

        vals = []
        for y in ys:
            for x in xs:
                d = depth_frame.get_distance(int(x), int(y))
                if d > 0:
                    vals.append(d)
        if len(vals) == 0:
            return 0.0
        
        return float(np.median(vals))

    # def deproject_pixel_to_point(self, 
    #                              intrinsics, 
    #                              px, 
    #                              py, 
    #                              depth):

    #     pt = rs.rs2_deproject_pixel_to_point(
    #         intrinsics, [float(px), float(py)], float(depth)
    #     )

    #     return float(pt[0]), float(pt[1]), float(pt[2])
    
    def calculate_3d_camera_coordinate(self, 
                                       depth_frame, 
                                       center_x, 
                                       center_y,
                                       depth_intrin) -> tuple:

        # x = center_x
        # y = center_y
        # dis = depth_frame.get_distance(x, y)  # 获取该像素点对应的深度
        # print ('depth: ',dis)       # 深度单位是m

        # 前有中值滤波
        depth = self.calculate_median_depth(depth_frame = depth_frame, 
                                  center_x = center_x, 
                                  center_y = center_y)
        camera_coordinate = rs.rs2_deproject_pixel_to_point(depth_intrin, [float(center_x), float(center_y)], depth) # type: ignore
        camera_coordinate = tuple(camera_coordinate)

        return camera_coordinate