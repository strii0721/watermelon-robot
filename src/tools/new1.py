import cv2
import numpy as np
import math

def detect_crop_rows(image_path):
    # 1. 读取图像
    img = cv2.imread(image_path)
    if img is None:
        print("无法读取图像，请检查路径")
        return
    
    # 调整图像大小以便于处理和显示（可选）
    height, width = img.shape[:2]
    img = cv2.resize(img, (width // 2, height // 2))
    result_img = img.copy()

    # 2. 灰度化
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 3. 高斯模糊（非常重要，用于去除杂草和泥土纹理的干扰）
    # 核大小 (15, 15) 可以根据实际图片分辨率调整
    blurred = cv2.GaussianBlur(gray, (15, 15), 0)

    # 4. Canny 边缘检测
    # 调整阈值以尽量只保留地膜的边缘
    edges = cv2.Canny(blurred, 30, 100)

    # 5. 概率霍夫变换检测直线
    # 参数：边缘图, 距离精度(像素), 角度精度(弧度), 阈值, 最小线长, 最大线段间隙
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=100, minLineLength=150, maxLineGap=50)

    angles = []

    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            
            # 计算直线的角度 (弧度转角度)
            angle = math.degrees(math.atan2(y2 - y1, x2 - x1))
            
            # 过滤掉趋于水平的线 (比如远处的横梁)，只保留纵向的田垄线
            # 假设田垄走向在垂直方向 ±45 度以内 (即角度在 45~135 或 -45~-135 之间)
            if (45 < abs(angle) < 135):
                angles.append(angle)
                # 在结果图上画出检测到的绿色直线
                cv2.line(result_img, (x1, y1), (x2, y2), (0, 255, 0), 3)

    # 6. 计算平均走向角度
    if angles:
        # 简单取平均值作为整体走向参考
        avg_angle = np.mean(angles)
        print(f"检测到 {len(angles)} 条有效田垄线。")
        print(f"田垄平均走向角度: {avg_angle:.2f} 度 (0度为水平向右)")
    else:
        print("未检测到明显的田垄线条。")

    # 显示结果
    cv2.imshow("Original", img)
    cv2.imshow("Edges", edges)
    cv2.imshow("Detected Rows", result_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# 替换为你保存的图片路径
detect_crop_rows('resource/field.jpg')