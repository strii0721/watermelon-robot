from nodes.node import Node
from utils.camera_control import CameraControl
from utils import yolo_model
import time
import cv2
from utils.topic_utils import TopicUtils
from controller.impl.default_robotic_arm_controller import DefaultRoboticArmController


class Main:

    
    

    def daemon():

        DAEMON_INTERVAL = 0.1
        RIGHT_EDGE = 265

        TOPIC_TARGET_QUEUE = "TARGET_QUEUE"
        
        TOPIC_LOGGER = "LOGGER_CAMERA"

        target_queue = []
        target_lock = False

        opt = yolo_model.parse_args()
        device, use_half = yolo_model.setup_device(opt)
        fa_on = yolo_model.check_flash_attention()
        model = yolo_model.load_model(opt.model, device, use_half, opt.conf, opt.iou)
        camera = CameraControl()
        robotic_arm = DefaultRoboticArmController()
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
                    cv2.circle(img_color, (cx, cy), 5, (0, 0, 255), -1)
                    cv2.circle(img_color, (cx, int(y1)), 5, (0, 0, 255), -1)
                    cv2.putText(img_color, label, (int(x1), int(y1)-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                    if depth > 0:
                        X, Y, Z = camera.deproject_pixel_to_point(matrix, cx, cy, depth)
                        
                        if X != 0 and Y != 0 and Z != 0:
                            Xt, Yt, Zt = camera.deproject_pixel_to_point(matrix, cx, int(y1), depth_top)
                            dist = abs(Y - Yt)*1000
                            x = -Z * 1000 + robotic_arm.get_stand_by_position()[0]
                            y = X * 1000
                            z = -Y * 1000 + robotic_arm.get_stand_by_position()[2]
                            cv2.putText(img_color, f'X:{x:.2f} Y:{y:.2f} Z:{z:.2f}', (int(x1), int(y1) + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
                            targets.append(([x, y, z], dist))
            
            
            now = time.time()
            fps = 1.0 / (now - prev_t) if now > prev_t else 0.0
            prev_t = now
            cv2.putText(img_color, f'FPS: {fps:.2f}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
            cv2.imshow('Cut Watermelon Task - Camera View', img_color)
            cv2.waitKey(1)

            # 锁定目标
            if targets and not target_lock:
                targets.sort(key=lambda item: item[0][1])
                if targets[-1][0][1] > 100 : 
                    target_lock = True

                    for target in targets:
                        target_queue.append(target[0])

            if target_lock:
                for target in target_queue:
                    print(f"当前目标：{target}")
                    robotic_arm.move_to_position(target_position = target)
                    time.sleep(2)
                    robotic_arm.stand_by()
                target_queue = []
                target_lock = False

    

if __name__ == "__main__":
    Main.daemon()