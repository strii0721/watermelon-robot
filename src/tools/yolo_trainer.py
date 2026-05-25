from ultralytics import YOLO
import cv2
import numpy as np
import os
import time

class YOLOTrainer:
    
    def __init__(self, 
                 project_name: str, 
                 dataset_yaml_path: str,
                 image_size: list = [480, 640],
                 device: str = "0"):
        
        self.project_name = project_name
        self.image_size = image_size
        self.dataset_yaml_path = dataset_yaml_path
        self.device = device

    def train(self, 
              model_path: str,
              run_name: str,
              epoch_number: int = 200, 
              batch_size: int = 64, 
              patience: int = 0):

        model = YOLO(model = model_path)
        results = model.train(
            data = self.dataset_yaml_path,
            imgsz = self.image_size,
            epochs = epoch_number,
            batch = batch_size,
            device = self.device,
            project = self.project_name,
            name = run_name, 
            patience = patience
        )
        
        if results: 
            result_folder = os.path.join(f"{self.project_name}", f"{run_name}")
            print(f"训练成功！训练结果保存于 {result_folder}")
        else: 
            print(f"训练失败！")
    
    def quantization(self, 
                     model_path: str, 
                     format: str = "engine", 
                     int8: bool = False):
        
        model = YOLO(model = model_path)
        if format == "onnx":
            quantized_model_path = model.export(
                format = format,  
                half = True,
                int8 = int8,
                imgsz = self.image_size,
                device = self.device
            )
        else: 
            quantized_model_path = model.export(
                format = format,  
                half = True,
                int8 = int8,
                data = self.dataset_yaml_path,
                imgsz = self.image_size,
                device = self.device
            )
        print(f"量化后权重文件保存于：{quantized_model_path}")
    
    def simulate(self, 
                 model_path: str, 
                 video_path: str, 
                 confidence: float = 0.8):

        model = YOLO(model = model_path)
        video_path = video_path
        video_capture = cv2.VideoCapture(video_path)
        rtn, frame = video_capture.read()
        
        while rtn:
            results = model.predict(source = frame, 
                                    conf = confidence)
            if results[0].masks is not None:
                height, width = frame.shape[:2]
                mask_xy = results[0].masks.xy[0]
                polygon = np.array(mask_xy, dtype=np.int32)
                binary_mask = np.zeros((height, width), dtype=np.uint8)
                cv2.fillPoly(binary_mask, [polygon], 255)
                center_points = []
                step = 10 
                for y in range(0, height, step):
                    row = binary_mask[y, :]
                    white_pixels = np.where(row == 255)[0]
                    if len(white_pixels) > 0:
                        x_left = white_pixels[0]
                        x_right = white_pixels[-1]
                        x_center = int((x_left + x_right) / 2)
                        center_points.append((x_center, y))
                overlay = frame.copy()
                cv2.fillPoly(overlay, [polygon], (0, 255, 0))
                frame = cv2.addWeighted(overlay, 0.3, frame, 0.7, 0)
                for i in range(len(center_points) - 1):
                    pt1 = center_points[i]
                    pt2 = center_points[i+1]
                    cv2.line(frame, pt1, pt2, (0, 0, 255), 3)
                    cv2.circle(frame, pt1, 2, (0, 255, 255), -1)
            cv2.imshow("Predicted Lane", frame)
            cv2.waitKey(1)
            rtn, frame = video_capture.read()
    
if __name__ == "__main__":
    
    PROJECT_NAME = "lane-detection"
    DATASET_VERSION = "v20260524"
    IMAGE_SIZE = [480, 640]
    DEVICE = "0"
    PATIENCE = 64
    
    dataset_yaml_path = os.path.join("resource", "datasets", f"{PROJECT_NAME}", f"{DATASET_VERSION}", "yolo-segment", f"dataset.yaml")
    trainer = YOLOTrainer(project_name = PROJECT_NAME, 
                          dataset_yaml_path = dataset_yaml_path, 
                          image_size = IMAGE_SIZE, 
                          device = DEVICE)
    
    # 训练
    # PRETRAINED_MODEL_NAME = "yolov8n-seg"
    # EOOCH_NUMBER = 512
    # BATCH_SIZE = 64
    # timestamp = int(time.time())
    # model_path = f"resource/weights_raw/{PRETRAINED_MODEL_NAME}.pt"
    # run_name = f"{PRETRAINED_MODEL_NAME}-b{BATCH_SIZE}-{timestamp}"
    
    # trainer.train(model_path = model_path,
    #               run_name = run_name, 
    #               epoch_number = EOOCH_NUMBER, 
    #               batch_size = BATCH_SIZE,
    #               patience = PATIENCE)
    
    # 量化
    # model_path = "resource/weights_best/yolo26n-seg-b8-1779665610.pt"
    # trainer.quantization(model_path = model_path, 
    #                      format = "engine", 
    #                      int8 = False)
    
    
    # 模拟验证
    trainer.simulate(model_path = "resource/weights_quantized/yolo26n-seg-b8-1779665610-fp16.engine", 
                     video_path = "resource/datasets/lane-detection/v20260524/video/video-5.mp4", 
                     confidence = 0.5)