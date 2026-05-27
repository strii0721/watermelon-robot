#
# Author:       strii0721
# Email:        strii0721@outlook.com
# Created on:   Mon May 11 2026
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
from service import RealsenseService
import time
import os

def main():

    INTERVAL = 1/5
    SAVE_FOLDER = "realsense_capture"

    camera_service = RealsenseService()
    image_folder = os.path.join("resource", SAVE_FOLDER)
    os.makedirs(image_folder, exist_ok = True)
    os.makedirs(os.path.join(image_folder, "color"), exist_ok = True)
    os.makedirs(os.path.join(image_folder, "depth"), exist_ok = True)
    os.makedirs(os.path.join(image_folder, "depth-map"), exist_ok = True)

    while True:

        color_frame, depth_frame, intrinsics = camera_service.read_frames()
        timestamp = int(time.time() * 1000)
        depth_map_image_array = cv2.applyColorMap(cv2.convertScaleAbs(depth_frame, alpha=0.03), cv2.COLORMAP_JET)
        color_image_path = os.path.join(image_folder, f"color", f"{timestamp}-color.png")
        depth_image_path = os.path.join(image_folder, f"depth", f"{timestamp}-depth.png")
        depth_map_image_path = os.path.join(image_folder, f"depth-map", f"{timestamp}-depth-map.png")
        cv2.imwrite(color_image_path, color_frame)
        cv2.imwrite(depth_image_path, depth_frame)
        cv2.imwrite(depth_map_image_path, depth_map_image_array)
        print(f"[{time.time():.4f}][INFO] 彩色图像保存至：{color_image_path}")
        print(f"[{time.time():.4f}][INFO] 深度图像保存至：{depth_image_path}")
        print(f"[{time.time():.4f}][INFO] 深度映射图像保存至：{depth_map_image_path}")
        time.sleep(INTERVAL)

if __name__ == "__main__":
    main()