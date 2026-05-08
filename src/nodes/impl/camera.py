from nodes.node import Node
from controller.camera_controller import CameraController
from controller.robotic_arm_controller import RoboticArmController
from utils import yolo_utils
import time
import cv2
from utils.topic_utils import TopicUtils
import threading

class Camera(Node):

    _target_lock = False

    def __init__(self):

        self.DAEMON_INTERVAL = 0.001
        self.RIGHT_EDGE = 265

        self.TOPIC_TARGET_QUEUE = "TARGET_QUEUE"
        self.TOPIC_LOGGER = "LOGGER_CAMERA"

        self.opt = yolo_utils.parse_args()
        self.device, use_half = yolo_utils.setup_device(self.opt)
        fa_on = yolo_utils.check_flash_attention()
        self.model = yolo_utils.load_model(self.opt.model, self.device, use_half, self.opt.conf, self.opt.iou)
        self.camera = CameraController()
        self.thread_lock = threading.Lock()
        TopicUtils.create_topic(topic_name = self.TOPIC_TARGET_QUEUE)
        TopicUtils.create_topic(topic_name = self.TOPIC_LOGGER)

    def daemon(self):
        while True:
            with self.thread_lock:
                prev_t = time.time()
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

                targets = []
                for b in boxes:
                    cls_id = int(b.cls[0].item())
                    name = res.names.get(cls_id, str(cls_id))
                    if name == 'watermelon':

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

                            if X != 0 and Y != 0 and Z != 0:
                                Xt, Yt, Zt = self.camera.deproject_pixel_to_point(matrix, cx, int(y1), depth_top)
                                dist = abs(Y - Yt)*1000
                                x = -Z * 1000 + RoboticArmController.get_stand_by_position()[0]
                                y = X * 1000
                                z = -Y * 1000 + RoboticArmController.get_stand_by_position()[2]
                                cv2.putText(img_color, f'X:{x:.2f} Y:{y:.2f} Z:{z:.2f}', (int(x1), int(y1) + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5,    (255, 0, 0), 2)
                                targets.append(([x, y, z], dist))

                curr_t = time.time()
                fps = 1.0 / (curr_t - prev_t) if curr_t > prev_t else 0.0
                cv2.putText(img_color, f'FPS: {fps:.2f}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                cv2.imshow('Cut Watermelon Task - Camera View', img_color)
                cv2.waitKey(1)

            # 锁定目标
            if targets and not Camera.get_target_lock():
                targets.sort(key=lambda item: item[0][1])
                if targets[-1][0][1] > 100: 
                    Camera.set_target_lock(True)

                    for target in targets:
                        TopicUtils.publish(topic_name = self.TOPIC_TARGET_QUEUE, 
                                           message = target)
            time.sleep(self.DAEMON_INTERVAL)
        
    @classmethod
    def get_target_lock(cls) -> bool:

        return Camera._target_lock
    
    @classmethod
    def set_target_lock(cls, 
                        flag: bool) -> None:
        
        Camera._target_lock = flag