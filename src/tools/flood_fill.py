import cv2
import numpy as np

def create_bottom_center_mask(image_path):
    # 1. 读取图像 (OpenCV 默认读取为 BGR 格式，与 RGB 逻辑一致)
    img = cv2.imread(image_path)
    if img is None:
        print("无法读取图像，请检查路径")
        return
    
    h, w = img.shape[:2]

    # 2. 选取底边中心点作为种子点
    # OpenCV 的坐标系是 (x, y)，即 (列, 行)
    seed_point = (w // 2, h - 1)

    # 3. 创建供 floodFill 使用的 mask
    # 注意：OpenCV 规定 floodFill 的 mask 尺寸必须比原图宽和高各多 2 个像素
    mask = np.zeros((h + 2, w + 2), dtype=np.uint8)

    # 4. 定义颜色容差 (可以根据实际图像的复杂程度进行微调)
    # 这里的 (20, 20, 20) 表示 B, G, R 三个通道向下和向上允许的最大颜色差值
    lo_diff = (20, 25, 20)  # 负向色差阈值
    up_diff = (20, 25, 20)  # 正向色差阈值

    # 5. 设置填充标志位 (flags)
    # 4: 表示只考虑上下左右 4 个方向的连通性 (也可以设为 8)
    # (255 << 8): 表示在 mask 中将找到的连通区域填充为 255 (白色)
    # cv2.FLOODFILL_MASK_ONLY: 告诉函数不要改变原图 img，只把结果画在 mask 上
    flags = 4 | (255 << 8) | cv2.FLOODFILL_MASK_ONLY

    # 6. 执行漫水填充
    cv2.floodFill(img, 
                  mask, 
                  seed_point, 
                  newVal=(0, 0, 0), # 因为用了 FLOODFILL_MASK_ONLY，这个值其实不会作用于原图
                  loDiff=lo_diff, 
                  upDiff=up_diff, 
                  flags=flags)

    # 7. 裁剪 mask，恢复到原图大小
    # 此时 mask 中：选中的连通区域是 255(白)，未选中的背景是 0(黑)
    extracted_mask = mask[1:-1, 1:-1]

    # 8. 按照需求反转颜色：制作“白色背景，黑色为选取”的蒙版
    # 将 255 变 0，0 变 255
    final_mask = cv2.bitwise_not(extracted_mask)

    # --- 以下为显示和保存结果的代码 ---
    cv2.imshow("Original Image", img)
    cv2.imshow("Final Mask", final_mask)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
    # cv2.imwrite("output_mask.png", final_mask)
    return final_mask

# 调用示例
create_bottom_center_mask("resource/image.png")