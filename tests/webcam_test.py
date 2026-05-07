import cv2

def test_webcam():
    print("正在尝试连接摄像头...")
    
    # 0 代表系统中的第一个摄像头（通常对应 /dev/video0）
    # 如果你有多个摄像头，可以尝试改成 1, 2 等
    cap = cv2.VideoCapture(0)

    # 检查摄像头是否成功打开
    if not cap.isOpened():
        print("❌ 错误：无法打开摄像头！")
        print("请检查：")
        print("1. usbipd 是否仍在正常映射状态。")
        print("2. WSL2 中是否有权限访问 /dev/video0（可以尝试在终端运行 sudo chmod 777 /dev/video0 后再试）。")
        return

    # cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    # cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    # 尝试强制使用 MJPG 格式（四字符代码）压缩传输，减少带宽占用
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))

    print("✅ 摄像头连接成功！按 'q' 键退出窗口。")

    try:
        while True:
            # 读取一帧画面
            # ret 是一个布尔值，表示是否成功读取
            # frame 是读取到的图像数据（Numpy 数组）
            ret, frame = cap.read()

            if not ret:
                print("❌ 无法获取画面帧，摄像头可能被断开或被其他程序占用。")
                break

            # 显示画面
            cv2.imshow('Webcam Test (WSL2)', frame)

            # 等待 1 毫秒，并检测键盘输入
            # 如果按下 'q' 键，则退出循环
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            # cv2.imwrite('resource/test_capture.jpg', frame)
            # print("已抓拍一张照片并保存为 test_capture.jpg，请在文件夹中查看！")
            # break # 拍完一张就退出

    except Exception as e:
        print(f"发生异常: {e}")

    finally:
        # 释放摄像头资源并关闭所有窗口
        print("正在关闭摄像头...")
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    test_webcam()