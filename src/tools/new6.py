import cv2
import numpy as np
import cv2
import numpy as np

def _YCrCgCb(bgr_image):

    b, g ,r = cv2.split(bgr_image)

    Y  = 0.299 * r + 0.587 * g + 0.114 * b
    Cr = (r - Y) / 1.402 + 128
    Cb = (b - Y) / 1.772 + 128
    Cg = (g - Y) / 0.825 + 128

    return (Y, Cr, Cg, Cb)

def BGR2DCgCrCb(bgr_image):

    Y, Cr, Cg, Cb = _YCrCgCb(bgr_image = bgr_image)
    dCgCrCb = 2 * Cg - Cr - Cb
    # Cg = np.clip(Cr , 0, 255).astype(np.uint8)
    # Cr = np.clip(Cb , 0, 255).astype(np.uint8)
    # Cb = np.clip(Cg * 2 , 0, 255).astype(np.uint8)

    # dCgCrCb = cv2.merge([Cg, Cr, Cb])

    dCgCrCb = np.clip(dCgCrCb , 0, 255).astype(np.uint8)
    
    return dCgCrCb


bgr = cv2.imread(filename = "resource/1778569756162-color.png")

dCgCrCb = BGR2DCgCrCb(bgr)

h, w = bgr.shape[:2]

gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)

blurred = cv2.GaussianBlur(dCgCrCb, (5, 5), 0)

# _, binary = cv2.threshold(gray, 80, 255, cv2.THRESH_BINARY)
_, binary = cv2.threshold(dCgCrCb, 80, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

def nothing(x):
    pass

# 1. 读取你的二值化图像 (这里假设你已经有一张黑白图了)
img = cv2.imread('your_binary_image.png', 0)
# 为了演示，我们生成一张带噪点和断裂的模拟图
# img = np.zeros((400, 400), dtype=np.uint8)


cv2.namedWindow('Morphology Debugger')

# 创建滑动条：核的宽度、高度，以及操作类型
cv2.createTrackbar('Kernel Width', 'Morphology Debugger', 1, 30, nothing)
cv2.createTrackbar('Kernel Height', 'Morphology Debugger', 1, 30, nothing)
# 0: 腐蚀(Erode), 1: 膨胀(Dilate), 2: 开运算(Open-去噪), 3: 闭运算(Close-连断裂)
cv2.createTrackbar('Operation', 'Morphology Debugger', 0, 3, nothing)

while True:
    # 获取滑动条当前值 (确保核的尺寸至少为1)
    w = max(1, cv2.getTrackbarPos('Kernel Width', 'Morphology Debugger'))
    h = max(1, cv2.getTrackbarPos('Kernel Height', 'Morphology Debugger'))
    op_idx = cv2.getTrackbarPos('Operation', 'Morphology Debugger')
    
    # 生成自定义矩形核
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (w, h))
    
    # 根据选择执行形态学操作
    if op_idx == 0:
        result = cv2.erode(binary, kernel, iterations=1)
    elif op_idx == 1:
        result = cv2.dilate(binary, kernel, iterations=1)
    elif op_idx == 2:
        result = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
    else:
        result = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        
    # 将原图和结果拼接在一起对比显示
    combined = np.hstack((binary, result))
    cv2.imshow('Morphology Debugger', combined)
    
    # 按 'q' 键退出
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()