import cv2
import numpy as np

def draw_navigation_line(image_path):
    # 1. 读取图像
    img = cv2.imread(image_path)
    if img is None:
        print("无法读取图像，请检查路径")
        return
    
    # 调整图像大小以便于处理和显示 (可选)
    h, w = img.shape[:2]
    scale = 800 / h
    img = cv2.resize(img, (int(w * scale), 800))
    h, w = img.shape[:2]

    # 2. 转换为灰度图并进行高斯模糊去噪
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (9, 9), 0)

    # 3. 阈值分割：黑色地膜很暗，泥土较亮
    # 设定一个阈值 (例如 80)，高于80的认为是路径(白)，低于80的认为是地膜(黑)
    _, thresh = cv2.threshold(blurred, 80, 255, cv2.THRESH_BINARY)

    # 4. 形态学操作：去除噪点，填补空洞
    kernel = np.ones((15, 15), np.uint8)
    morph = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
    morph = cv2.morphologyEx(morph, cv2.MORPH_CLOSE, kernel)

    # 5. 逐行扫描寻找路径中点
    center_points = []
    # 从图像底部开始，向上扫描到图像高度的 1/3 处 (避开顶部复杂的背景)
    start_y = h - 20
    end_y = h // 3
    step = 30 # 每隔 30 像素扫描一行

    for y in range(start_y, end_y, -step):
        row = morph[y, :]
        # 找到该行中所有白色像素的索引
        white_pixels = np.where(row == 255)[0]
        
        if len(white_pixels) > 0:
            # 简单粗暴的方法：取该行所有白色像素的平均位置作为中点
            # 在实际复杂场景中，可以寻找最长连续白色线段的中点
            center_x = int(np.mean(white_pixels))
            center_points.append((center_x, y))
            # 在原图上画出采样点 (蓝色小圆圈)
            cv2.circle(img, (center_x, y), 5, (255, 0, 0), -1)

    # 6. 拟合导航线
    if len(center_points) > 2:
        # 将点集转换为 numpy 数组
        points_arr = np.array(center_points)
        x = points_arr[:, 0]
        y = points_arr[:, 1]

        # 使用一次多项式 (直线) 拟合: x = ay + b
        # 注意：这里用 y 来预测 x，因为导航线接近垂直
        z = np.polyfit(y, x, 1)
        p = np.poly1d(z)

        # 计算拟合直线的起点和终点
        y1 = start_y
        x1 = int(p(y1))
        y2 = end_y
        x2 = int(p(y2))

        # 在原图上画出拟合的导航线 (红色粗线)
        cv2.line(img, (x1, y1), (x2, y2), (0, 0, 255), 4)

    # 7. 显示结果
    cv2.imshow("Threshold Mask", morph)
    cv2.imshow("Navigation Line", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# 运行函数，请将 "your_image.jpg" 替换为你的图片文件名
draw_navigation_line("resource/image.png")