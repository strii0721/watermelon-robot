import cv2
import os

def main():
    
    input_folder = os.path.join("resource", "lane_detection")
    video_names = [
        "video-0.mp4", 
        "video-1.mp4", 
        "video-2.mp4", 
        "video-5.mp4", 
    ]
    
    for video_name in video_names:
        
        input_path = os.path.join(input_folder, video_name)
        video = cv2.VideoCapture(input_path)
        frame_nomeric = 0
        rtn, frame = video.read()
        output_folder = os.path.join("resource", "lane_detection", "video_frames", f"{video_name[:-4]}")
        os.makedirs(output_folder, exist_ok=True)
        while rtn:
            frame_nomeric += 1
            cv2.imshow("monitor", frame)
            cv2.waitKey(1)
            output_path = os.path.join(output_folder, f"{video_name[:-4]}-frame-{frame_nomeric}.png")
            print(f"{output_path}")
            cv2.imwrite(filename = output_path, 
                        img = frame)
            rtn, frame = video.read()
            
if __name__ == "__main__":
    main()