import cv2
from utils import CVUtils
import time

def main():
    video_path = "resource/lane_detection/video-5.mp4"
    video = cv2.VideoCapture(video_path)

    rtn, frame = video.read()
    reference_frames = []
    while rtn:
        binary, binary_supressed, binary_morphology = CVUtils.lane_detection_preprocess(source_image = frame, 
                                                                                        roi_y_min_portion = 0.7, 
                                                                                        roi_y_max_portion = 0.9,
                                                                                        maximum_window_size = 5,
                                                                                        reference_frames = reference_frames)
        angular_error = CVUtils.predict_lane(canvas = frame, 
                                             source_image = binary_morphology, 
                                             roi_y_min_portion = 0.7, 
                                             roi_y_max_portion = 0.9,  
                                             detect_step = 5)
        cv2.imshow("frame", frame)       
        cv2.imshow("binary_morphology", binary_morphology)
        cv2.waitKey(1)
        reference_frames.append(binary_supressed)
        reference_frames = reference_frames[-5:]
        rtn, frame = video.read()
        
if __name__ == "__main__":
    main()