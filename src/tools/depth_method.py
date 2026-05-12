import pyrealsense2 as rs
import numpy as np

# 1. 初始化并启动 Pipeline
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
profile = pipeline.start(config)

# 2. 获取相机的 Depth Scale (非常重要！)
depth_sensor = profile.get_device().first_depth_sensor()
depth_scale = depth_sensor.get_depth_scale()
print(f"当前相机的 Depth Scale 为: {depth_scale} 米/单位") # 通常输出 0.001

try:
    while True:
        # 3. 等待一帧数据
        frames = pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()
        if not depth_frame:
            continue

        # 4. 将深度帧转换为 numpy 数组 (类型为 uint16, shape 为 480x640)
        depth_image = np.asanyarray(depth_frame.get_data())
        
        # 打印中心点像素的原始值和真实距离
        center_y, center_x = 240, 320
        raw_value = depth_image[center_y, center_x]
        real_distance = raw_value * depth_scale
        
        print(f"中心点原始数值: {raw_value}, 真实距离: {real_distance:.3f} 米")

        # --- 补充：如果你想用 OpenCV 显示深度图 ---
        # 因为 OpenCV 无法直接显示 uint16 的图像，你需要把它映射到 0-255 的 8位彩色图 (伪彩色)
        # 这里的 cv2.convertScaleAbs 只是为了可视化，不要用它来做距离计算！
        import cv2
        depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)
        cv2.imshow('Depth Image', depth_colormap)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
finally:
    pipeline.stop()
    cv2.destroyAllWindows()