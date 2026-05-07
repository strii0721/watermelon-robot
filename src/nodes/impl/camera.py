from nodes.node import Node
from utils.camera_control import CameraControl
from utils import yolo_model
import time
import cv2

class Camera(Node):

    DAEMON_INTERVAL = 0.

    def __init__(self):
        opt = yolo_model.parse_args()
        device, use_half = yolo_model.setup_device(opt)
        fa_on = yolo_model.check_flash_attention()
        self.model = yolo_model.load_model(opt.model, device, use_half, opt.conf, opt.iou)
        self.camera = CameraControl()

    def daemon(self):
        prev_t = time.time()
        while True:
            img_color, img_depth, aligned_depth_frame, aligned_color_frame, matrix = self.camera.get_frames()
            if not aligned_color_frame or not aligned_depth_frame:
                continue

            pred = self.model.predict(
                source=img_color,
                verbose=False,
                device=self.device,
                conf=self.opt.conf,
                iou=self.opt.iou,
            )

            res = pred[0]
            boxes = res.boxes

            detected = False
            watermelon_target = []
            for b in boxes:
                cls_id = int(b.cls[0].item())
                name = res.names.get(cls_id, str(cls_id))
                if name == 'watermelon':
                    detected = True
                    x1, y1, x2, y2 = b.xyxy[0].tolist()
                    conf = float(b.conf[0].item())

                    cx = int((x1 + x2) / 2)
                    cy = int((y1 + y2) / 2)
                    depth = self.camera.median_depth(aligned_depth_frame, cx, cy, window_size=5)
                    depth_top = self.camera.median_depth(aligned_depth_frame, cx, int(y1), window_size=5)
                    label = f'{name} {conf:.2f}'
                    cv2.rectangle(img_color, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                    cv2.circle(img_color, (cx, cy), 5, (0, 0, 255), -1)
                    cv2.circle(img_color, (cx, int(y1)), 5, (0, 0, 255), -1)
                    cv2.putText(img_color, label, (int(x1), int(y1)-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                    if depth > 0:
                        X, Y, Z = self.camera.deproject_pixel_to_point(matrix, cx, cy, depth)
                        cv2.putText(img_color, f'X:{X:.2f} Y:{Y:.2f} Z:{Z:.2f}', (int(x1), int(y1) + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
                        if X != 0 and Y != 0 and Z != 0:
                            with self.target_lock:
                                Xt, Yt, Zt = self.camera.deproject_pixel_to_point(matrix, cx, int(y1), depth_top)
                                dist = abs(Y - Yt)*1000
                                watermelon_target.append(((-X*1000, -Z*1000, -Y*1000), dist))
            
            watermelon_target.sort(key=lambda item: item[0][0], reverse=True)
            if watermelon_target:
                self.current_target, self.current_target_dist = watermelon_target[-1]
            else:
                self.current_target = None
                self.current_target_dist = None
            print(self.current_target, self.current_target_dist)

            now = time.time()
            fps = 1.0 / (now - prev_t) if now > prev_t else 0.0
            prev_t = now
            cv2.putText(img_color, f'FPS: {fps:.2f}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
            cv2.imshow('Cut Watermelon Task - Camera View', img_color)

            if not detected:
                with self.target_lock:
                    self.current_target = None
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.stop_threads = True
                break