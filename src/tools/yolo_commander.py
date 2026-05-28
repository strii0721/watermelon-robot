from ultralytics import YOLO
import cv2
import numpy as np
import os
import time
import argparse
from types import SimpleNamespace

def parse_args():
    
    parser = argparse.ArgumentParser()
    
    parser.add_argument("project_name" ,
                        type = str, 
                        help = "子项目名称")
    
    parser_group_command = parser.add_subparsers(dest = "command", 
                                                 required = True)
    
    parser_train = parser_group_command.add_parser("train", 
                                                   help = "训练")
    parser_train.add_argument("--base-model", 
                              type = str, 
                              default = "yolo26n-seg",
                              help = "预训练模型名称")
    parser_train.add_argument("--dataset", 
                              type = str, 
                              default = "yolo-segment",
                              help = "训练集名称") 
    parser_train.add_argument("--batch-size", 
                              type = int, 
                              default = 64, 
                              help = "训练用批次大小")
    parser_train.add_argument("--epoch-number",
                              type = int,
                              default = 512, 
                              help = "训练迭代次数")
    parser_train.add_argument("--patience",
                              type = int, 
                              default = 64, 
                              help = "早停轮次")
    
    parser_quantize = parser_group_command.add_parser("quantize", 
                                                      help = "量化(TensorRT)")
    parser_quantize.add_argument("--model", 
                                 type = str, 
                                 required = True, 
                                 help = "原始模型名称")
    parser_quantize.add_argument("--accuracy", 
                                 type = str, 
                                 default = "fp16", 
                                 help = "量化精度")
    
    parser_simulate = parser_group_command.add_parser("simulate", 
                                                      help = "模拟测试")
    parser_simulate.add_argument("--model-path", 
                                 type = str, 
                                 required = True, 
                                 help = "模型路径")
    parser_simulate.add_argument("--video-path", 
                                 type = str, 
                                 required = True, 
                                 help = "视频路径")
    parser_simulate.add_argument("--confidence", 
                                 type = float, 
                                 default = 0.8, 
                                 help = "检测置信度")
    
    parser.add_argument("--image-size", 
                        type = list, 
                        default = [480, 640], 
                        help = "图片输入尺寸")
    parser.add_argument("--device", 
                        type = str, 
                        choices = ["cuda", "cpu"], 
                        default = "cuda", 
                        help = "训练用设备")
    
    
    arguments = parser.parse_args()
    
    return arguments

class YOLOCommander:
    
    def train(self, 
              arguments: SimpleNamespace):

        model_path = os.path.join("resource", "weights-base", f"{arguments.base_model}.pt")
        dataset_path = os.path.join("resource", "datasets", f"{arguments.project_name}", f"{arguments.dataset}", f"dataset.yaml")
        timestamp = int(time.time())
        run_name = f"{arguments.base_model}-{arguments.batch_size}-{timestamp}"
        model = YOLO(model = model_path)
        results = model.train(
            project = arguments.project_name,
            name = run_name, 
            data = dataset_path,
            device = arguments.device,
            batch = arguments.batch_size,
            epochs = arguments.epoch_number,
            imgsz = arguments.image_size,
            patience = arguments.patience
        )
        
        if results: 
            result_folder = os.path.join(f"{arguments.project_name}", f"{run_name}")
            print(f"训练成功！训练结果保存于 {result_folder}")
        else: 
            print(f"训练失败！")
    
    def quantize(self, 
                     arguments: SimpleNamespace):
        
        model_path = os.path.join("resource", "weights-best", f"{arguments.project_name}", f"{arguments.model}.pt")
        format = "engine"
        model = YOLO(model = model_path)
        match arguments.accuracy:
            case "fp16":
                quantized_model_path = model.export(
                    format = format, 
                    device = arguments.device,
                    half = True,
                    imgsz = arguments.image_size,
                )
            case "int8":
                quantized_model_path = model.export(
                    format = format,
                    device = arguments.device,
                    int8 = True,
                    data = self.dataset_yaml_path,
                    imgsz = arguments.image_size,
                )
            case _:
                quantized_model_path = None
                print(f"不支持此格式")
                
        if quantized_model_path:
            print(f"量化后权重文件保存于：{quantized_model_path}")
    
    def simulate(self, 
                 arguments):

        model = YOLO(model = arguments.model_path)
        video_path = arguments.video_path
        video_capture = cv2.VideoCapture(video_path)
        rtn, frame = video_capture.read()
        
        while rtn:
            results = model.predict(source = frame, 
                                    conf = arguments.confidence, 
                                    verbose = False)
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
    
    arguments = parse_args()
    commander = YOLOCommander()
    
    match arguments.command:
        case "train": 
            commander.train(arguments = arguments)
        case "quantize": 
            commander.quantize(arguments = arguments)
        case "simulate": 
            commander.simulate(arguments = arguments)