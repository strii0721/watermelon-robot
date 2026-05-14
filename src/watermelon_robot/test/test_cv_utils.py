import cv2
from utils import CVUtils
import os
from utils import config


if __name__ == "__main__":
    
    fps = 60
    video_name = "video-2.mp4"
    video_path = os.path.join("resource", "lane_detection", video_name)
    video_capture = cv2.VideoCapture(video_path)
    
    rtn, frame = video_capture.read()
    while rtn: 
        hsv, blurred, binary, binary_morphology = CVUtils.lane_detection_preprocess(source_image = frame, 
                                                                                       roi_y_min_portion = config.lane_detection.roi.y_min_portion, 
                                                                                       roi_y_max_portion = config.lane_detection.roi.y_max_portion, )
        cv2.imshow(f"{video_name}", frame)
        cv2.imshow(f"{video_name}-hsv", hsv)
        cv2.imshow(f"{video_name}-blurred", blurred)
        cv2.imshow(f"{video_name}-binary", binary)
        cv2.imshow(f"{video_name}-binary_morphology", binary_morphology)
        cv2.waitKey(int(1/fps*1000))
        rtn, frame = video_capture.read()