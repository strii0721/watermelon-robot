import cv2
from utils import ImageUtils
import os


if __name__ == "__main__":
    
    fps = 60
    video_name = "video-2.mp4"
    video_path = os.path.join("resource", "lane_detection", video_name)
    video_capture = cv2.VideoCapture(video_path)
    
    rtn, frame = video_capture.read()
    while rtn: 
        hsv, blurred, binary, binary_morphology = ImageUtils.preprocess_frame(frame)
        cv2.imshow(f"{video_name}", frame)
        cv2.imshow(f"{video_name}-hsv", hsv)
        cv2.imshow(f"{video_name}-blurred", blurred)
        cv2.imshow(f"{video_name}-binary", binary)
        cv2.imshow(f"{video_name}-binary_morphology", binary_morphology)
        cv2.waitKey(int(1/fps*1000))
        rtn, frame = video_capture.read()