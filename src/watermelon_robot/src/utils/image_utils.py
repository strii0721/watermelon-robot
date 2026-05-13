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
from sensor_msgs.msg import CameraInfo

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
    def lane_detection_preprocess(cls, 
                                  source_image: np.ndarray, 
                                  roi_y_min_portion: float, 
                                  roi_y_max_portion: float) -> list:
        
        height = source_image.shape[0]
        width = source_image.shape[1]

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
        binary_morphology = ImageUtils.not_maximum_connected_area_suppresion(binary_morphology)
        binary_morphology = cv2.morphologyEx(binary_morphology, cv2.MORPH_OPEN, kernel_square, iterations= 20)
        binary_morphology = cv2.dilate(binary_morphology, kernel_rectangle, iterations = 3)

        return [hsv, blurred, binary, binary_morphology]
    
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
        # camera_coordinate = rs.rs2_deproject_pixel_to_point(camera_intrinsics, [float(center_x), float(center_y)], center_depth) # type: ignore
        # camera_coordinate = tuple(camera_coordinate)
        # camera_coordinate_mm = tuple(x * 1000 for x in camera_coordinate)
        Z = ImageUtils.calculate_median_depth(depth_image = depth_image, 
                                              center_pixel = center_pixel)
        
        fx = camera_intrinsics.k[0]
        cx = camera_intrinsics.k[2]
        fy = camera_intrinsics.k[4]
        cy = camera_intrinsics.k[5]

        X = (x_pixel - cx) * Z / fx
        Y = (y_pixel - cy) * Z / fy

        return (X, Y, Z)
    
    @classmethod
    def predict_targets(cls, 
                        model, 
                        device,
                        color_image, 
                        depth_image, 
                        confidence,
                        iou,
                        camera_intrinsics) -> list:

        rtn = model.predict(source = color_image, 
                            verbose = False, 
                            device = device, 
                            conf = confidence, 
                            iou = model.iou)
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
                    
                    target = ImageUtils.calculate_camera_coordinate(center_pixel = (crosshair_pixel_x, crosshair_pixel_y), 
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

                    if ImageUtils.check_target_validation(target_coordinate = target): 
                        target_list.append(target)

        return target_list
    
    
    @classmethod
    def check_target_validation(cls, 
                                target_coordinate: tuple): 
        
        if not ((-100 < target_coordinate[0] and target_coordinate[0] < 100) and (-50 < target_coordinate[1] and target_coordinate[1] < 50) and (0 < target_coordinate[2] and target_coordinate[2] < 1000)):
            return False
        
        if target_coordinate[0] < 0:
            return False
        
        return True
    
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

        # 绘制当前航向参考点
        reference_point = (int(width/2), roi_y_max)
        cv2.circle(canvas, reference_point, 5, (255, 0, 0), -1)

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
            mark_size = 5
            cv2.line(canvas, (navigate_point[0] - mark_size, navigate_point[1]), (navigate_point[0] + mark_size, navigate_point[1]), (0, 0, 255), 2)
            cv2.line(canvas, (navigate_point[0], navigate_point[1] - mark_size), (navigate_point[0], navigate_point[1] + mark_size), (0, 0, 255), 2)

            # 绘制偏航参考线
            arow_color = (0,0,255)
            thickness = 1
            cv2.arrowedLine(canvas, reference_point, navigate_point, arow_color, thickness, tipLength = 0.05)
