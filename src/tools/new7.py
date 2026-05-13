import cv2
import os
import numpy as np
import time
import glob

fps = 60
video_name = "video-2.mp4"

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

def get_file_names(directory):

    file_names = os.listdir(directory)
    return file_names

def keep_largest_connected_component(binary_img):
    """
    保留二值图像中面积最大的白色连通区域，舍弃其他区域。
    :param binary_img: 输入的二值化图像 (单通道，像素值为 0 或 255)
    :return: 仅包含最大连通区域的二值图像
    """
    # 1. 寻找图像中的所有轮廓
    # cv2.RETR_EXTERNAL: 只提取最外层轮廓
    # cv2.CHAIN_APPROX_SIMPLE: 压缩水平、垂直和对角线段，只保留端点，节省内存
    contours, hierarchy = cv2.findContours(binary_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # 如果没有找到任何轮廓（全黑图像），直接返回原图
    if not contours:
        return binary_img

    # 2. 找到面积最大的轮廓
    # 使用 max 函数，以 cv2.contourArea (轮廓面积) 作为比较标准
    largest_contour = max(contours, key=cv2.contourArea)

    # 3. 创建一个与原图大小相同的全黑背景 (Mask)
    result_mask = np.zeros_like(binary_img)

    # 4. 在全黑背景上，将最大的轮廓用纯白色 (255) 填充画出来
    # 参数 -1 表示绘制列表中的所有轮廓（这里列表里只有最大轮廓）
    # thickness=cv2.FILLED (或 -1) 表示实心填充
    cv2.drawContours(result_mask, [largest_contour], -1, 255, thickness=cv2.FILLED)

    return result_mask

def main():

    video_capture = cv2.VideoCapture(video_path)

    # directory = os.path.join("resource/realsense_capture/color")
    # search_pattern = os.path.join(directory, '*.png') 
    # file_paths = glob.glob(search_pattern)
    # if not file_paths:
    #     print("未找到任何图片，请检查路径和图片格式！")
    #     return
    # file_paths.sort() 
    
    roi_portion = 0.40
    trunck_number = 1
    time_prev = time.time()
    frame_no = 0
    rtn, frame = video_capture.read()
    # frame = cv2.imread(file_paths[0])
    height = frame.shape[0]
    width = frame.shape[1]

    while rtn: 
    # for file_path in file_paths:
        
        frame_copy = frame

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        h, s, v = cv2.split(hsv)

        dCgCrCb = BGR2DCgCrCb(frame)

        gray = cv2.cvtColor(dCgCrCb, cv2.COLOR_BGR2GRAY)

        blurred = cv2.GaussianBlur(s, (5, 5), 0)

        _, binary = cv2.threshold(blurred, 40, 255, cv2.THRESH_OTSU)

        kernel = np.ones((2, 1), np.uint8)
        binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations= 30)
        binary[0:int(height - height * roi_portion), :] = 0
        binary = keep_largest_connected_component(binary)
        kernel = np.ones((2, 2), np.uint8)
        binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations= 20)



        center_points = []
        start_y = int(height - height * roi_portion * 1/2)
        end_y = int(height - height * roi_portion)
        step = 5

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






        pt1 = (int(width * 1/2), height)
        pt2 = (int(width * 1/2), height - int(height * roi_portion * 1/2))
        arow_color = (0,0,255)
        thickness = 1
        cv2.arrowedLine(frame_copy, pt1, pt2, arow_color, thickness, tipLength = 0.05)
        time_now = time.time()
        fps_real = int(1 / (time_now - time_prev))
        time_prev = time_now
        cv2.putText(img = frame_copy, 
                    text = f"FPS {fps_real} | Frame No. {frame_no} | Frame Size {width}x{height}", 
                    org = (5, 20), 
                    fontFace = cv2.FONT_HERSHEY_SIMPLEX, 
                    fontScale = 0.5, 
                    color = (0, 0, 255), 
                    thickness = 2)
        cv2.imshow(f"{video_name}", frame_copy)
        cv2.imshow(f"{video_name}-binary", binary)
        cv2.imshow(f"{video_name}-blurred", blurred)
        cv2.waitKey(int(1/fps*1000))
        frame_no += 1
        rtn, frame = video_capture.read()
        # frame = cv2.imread(file_path)
        # print(file_path)

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
