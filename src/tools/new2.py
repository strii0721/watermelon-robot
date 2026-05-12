import cv2
import numpy as np
import math

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

    return dCgCrCb

# bgr = cv2.imread(filename = "resource/field.jpg")
bgr = cv2.imread(filename = "resource/image.png")
blurred = cv2.GaussianBlur(bgr, (5, 5), 0)

zeros = np.zeros(bgr.shape[:2], dtype=np.uint8)
b, g, r = cv2.split(bgr)
green = cv2.merge([zeros, g, zeros])

dCgCrCb = BGR2DCgCrCb(bgr)


gray = cv2.cvtColor(dCgCrCb, cv2.COLOR_BGR2GRAY)

_, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

# hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
# lower_blue = np.array([100, 50, 50])
# upper_blue = np.array([130, 255, 255])

kernel = np.ones((3, 3), np.uint8)
# binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
# binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
binary = cv2.dilate(binary, kernel, iterations=1)
binary = cv2.erode(binary, kernel, iterations=1)

edges = cv2.Canny(binary, 100, 150)


lines = cv2.HoughLines(edges, 1, np.pi/180, 100)

angles = []
# if lines is not None:
#     for line in lines:
#         rho, theta = line[0]
#         a = np.cos(theta)
#         b = np.sin(theta)
#         x0 = a * rho
#         y0 = b * rho
#         # 延长线段使其贯穿屏幕
#         x1 = int(x0 + 1000 * (-b))
#         y1 = int(y0 + 1000 * (a))
#         x2 = int(x0 - 1000 * (-b))
#         y2 = int(y0 - 1000 * (a))
#         cv2.line(bgr, (x1, y1), (x2, y2), (0, 0, 255), 2)

cv2.imshow("green", green)
cv2.imshow("binary2", binary)
cv2.imshow("edges", edges)
cv2.imshow("bgr", bgr)
cv2.waitKey(0)
cv2.destroyAllWindows()