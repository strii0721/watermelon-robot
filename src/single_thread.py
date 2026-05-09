#
# Author:       strii0721
# Email:        strii0721@outlook.com
# Created on:   Thu May 07 2026
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


from controller.camera_controller import CameraController
from utils import yolo_utils
import time
import cv2
from controller.robotic_arm_controller import RoboticArmController
from utils.camera_utils import CameraUtils


class Main:

    _target_lock = False

    def daemon():

        opt = yolo_utils.parse_args()
        device, use_half = yolo_utils.setup_device(opt)
        fa_on = yolo_utils.check_flash_attention()
        model = yolo_utils.load_model(opt.model, device, use_half, opt.conf, opt.iou)
        camera = CameraController()
        robotic_arm = RoboticArmController(speed_rate = 100)
        robotic_arm.stand_by()
        print(f"机械臂就位...")
        prev_t = time.time()
        while True:
            img_color, img_depth, aligned_depth_frame, aligned_color_frame, matrix = camera.get_frames()
            if not aligned_color_frame or not aligned_depth_frame:
                continue

            pred = model.predict(
                source=img_color,
                verbose=False,
                device=device,
                conf=opt.conf,
                iou=opt.iou,
            )

            res = pred[0]
            boxes = res.boxes
            targets = []

            for b in boxes:
                cls_id = int(b.cls[0].item())
                name = res.names.get(cls_id, str(cls_id))
                if name == 'watermelon':
                    x1, y1, x2, y2 = b.xyxy[0].tolist()
                    conf = float(b.conf[0].item())

                    cx = int((x1 + x2) / 2)
                    cy = int((y1 + y2) / 2)
                    depth = camera.median_depth(aligned_depth_frame, cx, cy, window_size=5)
                    depth_top = camera.median_depth(aligned_depth_frame, cx, int(y1), window_size=5)
                    label = f'{name} {conf:.2f}'
                    cv2.rectangle(img_color, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                    # 瓜中心
                    cv2.circle(img_color, (cx, cy), 5, (0, 0, 255), -1)
                    # 藤蔓
                    cv2.circle(img_color, (cx, int(y1)), 5, (0, 0, 255), -1)
                    cv2.putText(img_color, label, (int(x1), int(y1)-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                    if depth > 0:
                        X, Y, Z = camera.deproject_pixel_to_point(matrix, cx, cy, depth)
                        
                        # if X != 0 and Y != 0 and Z != 0:
                        if True:
                            Xt, Yt, Zt = camera.deproject_pixel_to_point(matrix, cx, int(y1), depth_top)

                            Xt *= 1000
                            Yt *= 1000
                            Zt *= 1000
                            target_position = CameraUtils.get_world_coordinate(camera_coordinate = [Xt, Yt, Zt])


                            # x = robotic_arm.get_stand_by_position()[0] - (Zt + 10) + 100
                            # y = robotic_arm.get_stand_by_position()[1] + (Xt - 25) - 10
                            # z = robotic_arm.get_stand_by_position()[2] - (Yt - 60) + 20
                            # target_position = [x, y, z]

                            cv2.putText(img_color, f'Xt:{Xt:.2f} Yt:{Yt:.2f} Zt:{Zt:.2f}', (int(x1), int(y1) + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
                            targets.append(target_position)

            # 锁定目标
            if targets and not Main.get_target_lock():
                targets.sort(key=lambda item: item[1])
                if targets[-1][1] > -102 : 
                    Main.set_target_lock(True)
                    # for target in targets:
                    # target_position = targets[-1]
                    # midway_position = [
                    #     RoboticArmController.get_stand_by_position()[0], 
                    #     RoboticArmController.get_stand_by_position()[1],
                    #     target_position[2] 
                    # ]
            
            now = time.time()
            fps = 1.0 / (now - prev_t) if now > prev_t else 0.0
            prev_t = now
            cv2.putText(img_color, f'FPS: {fps:.2f}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
            cv2.imshow('Cut Watermelon Task - Camera View', img_color)
            cv2.waitKey(1)



            if Main.get_target_lock():

                target_position = targets[-1]
                print(f"当前目标位置：{target_position}")

                valid = robotic_arm.valid_position(target_position = target_position)

                # if valid:
                if True:
                    robotic_arm.move_to_position(target_position = target_position)

                    # TODO
                    # 执行器业务代码
                    time.sleep(2)

                    robotic_arm.stand_by()
                    
                else: 
                    print(f"位置不合理")

                Main.set_target_lock(False)

    @classmethod
    def set_target_lock(cls, 
                        flag: bool) -> None:
        
        Main._target_lock = flag
    
    @classmethod
    def get_target_lock(cls) -> bool:

        return Main._target_lock
    

if __name__ == "__main__":
    Main.daemon()