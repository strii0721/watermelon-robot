import cv2
import os
import numpy as np
import time

fps = 60
video_name = "video-0.mp4"

video_path = os.path.join("resource", "lane_detection", video_name)

def _YCrCgCb(bgr_image):

    b, g ,r = cv2.split(bgr_image)

    Y  = 0.299 * r + 0.587 * g + 0.114 * b
    Cr = (r - Y) / 1.402 + 128
    Cb = (b - Y) / 1.772 + 128
    Cg = (g - Y) / 0.825 + 128

    return (Y, Cr, Cg, Cb)

def BGR2DCgCrCb(bgr_image):

    Y, Cr, Cg, Cb = _YCrCgCb(bgr_image = bgr_image)
    

    Cg = np.clip(Cr , 0, 255).astype(np.uint8)
    Cr = np.clip(Cb , 0, 255).astype(np.uint8)
    Cb = np.clip(Cg * 2 , 0, 255).astype(np.uint8)
    dCgCrCb = cv2.merge([Cg, Cr, Cb])

    # dCgCrCb = 2 * Cg - Cr - Cb
    # dCgCrCb = np.clip(dCgCrCb , 0, 255).astype(np.uint8)
    
    return dCgCrCb


def main():

    video_capture = cv2.VideoCapture(video_path)
    frame_no = 0
    rtn, frame = video_capture.read()
    h = frame.shape[0]
    w = frame.shape[1]
    roi_portion = 0.5
    trunck_number = 1
    time_prev = time.time()

    while rtn: 

        frame_copy = frame

        dCgCrCb = BGR2DCgCrCb(frame)

        gray = cv2.cvtColor(dCgCrCb, cv2.COLOR_BGR2GRAY)

        blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        _, binary = cv2.threshold(blurred, 50, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        kernel = np.ones((5, 1), np.uint8)
        binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
        # binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        # binary = cv2.erode(binary, kernel)

        center_points = []
        start_y = h - 20
        end_y = h // 2
        step = 10

        for y in range(start_y, end_y, -step):
            row = binary[y, :]
            white_pixels = np.where(row == 255)[0]

            if len(white_pixels) > 0:
                center_x = int(np.mean(white_pixels))
                center_points.append((center_x, y))
                cv2.circle(frame_copy, (center_x, y), 5, (255, 0, 0), -1)

        if len(center_points) > 2:
                points_arr = np.array(center_points)
                x = points_arr[:, 0]
                y = points_arr[:, 1]

                z = np.polyfit(y, x, 1)
                p = np.poly1d(z)

                y1 = start_y
                x1 = int(p(y1))
                y2 = end_y
                x2 = int(p(y2))

                cv2.line(frame_copy, (x1, y1), (x2, y2), (255, 0, 255), 2) 






        pt1 = (int(w * 1/2), h)
        pt2 = (int(w * 1/2), h - int(h * roi_portion * 1/2))
        arow_color = (0,0,255)
        thickness = 1
        cv2.arrowedLine(frame_copy, pt1, pt2, arow_color, thickness, tipLength = 0.05)
        time_now = time.time()
        fps_real = int(1 / (time_now - time_prev))
        time_prev = time_now
        cv2.putText(img = frame_copy, 
                    text = f"FPS {fps_real} | Frame No. {frame_no} | Frame Size {w}x{h}", 
                    org = (5, 20), 
                    fontFace = cv2.FONT_HERSHEY_SIMPLEX, 
                    fontScale = 0.5, 
                    color = (0, 0, 255), 
                    thickness = 2)
        cv2.imshow(f"{video_name}", frame_copy)
        cv2.imshow(f"{video_name}-binary", binary)
        cv2.waitKey(int(1/fps*1000))
        frame_no += 1
        rtn, frame = video_capture.read()

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
