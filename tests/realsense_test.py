import pyrealsense2 as rs
import numpy as np
import cv2

def test_realsense():
    # 1. 创建一个管道 (Pipeline)
    pipeline = rs.pipeline()

    # 2. 创建配置对象
    config = rs.config()

    # 告诉管道我们要获取哪些流。这里配置获取 640x480 分辨率，30帧/秒的深度流和彩色流
    config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
    config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

    print("正在启动 RealSense 相机...")
    try:
        # 3. 启动相机流
        pipeline.start(config)
        print("相机启动成功！按 'q' 键退出窗口。")

        while True:
            # 4. 等待获取新的一组数据帧 (包含深度和彩色)
            frames = pipeline.wait_for_frames()
            
            # 提取深度帧和彩色帧
            depth_frame = frames.get_depth_frame()
            color_frame = frames.get_color_frame()

            # 如果有任何一个帧没获取到，就跳过这次循环
            if not depth_frame or not color_frame:
                continue

            # 5. 将获取到的帧数据转换为 Numpy 数组，方便 OpenCV 处理
            depth_image = np.asanyarray(depth_frame.get_data())
            color_image = np.asanyarray(color_frame.get_data())

            # 6. 处理深度图：将单通道的深度数据映射为伪彩色图，方便人眼观察
            # 这里的 alpha=0.03 是一个缩放因子，你可以根据实际距离调整它让颜色对比更明显
            depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)

            # 7. 将彩色图和深度伪彩色图水平拼接在一起
            images = np.hstack((color_image, depth_colormap))

            # 8. 使用 OpenCV 显示画面
            cv2.namedWindow('RealSense Test', cv2.WINDOW_AUTOSIZE)
            cv2.imshow('RealSense Test', images)

            # 检测键盘输入，如果按下 'q' 键则退出循环
            key = cv2.waitKey(1)
            if key & 0xFF == ord('q'): # 27 是 ESC 键
                break

    except Exception as e:
        print(f"发生错误: {e}")
        print("请检查相机是否已正确连接，或者是否有其他程序正在占用相机。")

    finally:
        # 9. 释放资源，停止管道
        print("正在关闭相机...")
        pipeline.stop()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    test_realsense()