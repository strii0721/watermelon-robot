import cv2
import numpy as np
import matplotlib.pyplot as plt

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

def BGR2YCrCb(bgr_image):

    Y, Cr, Cb, Cg = _YCrCgCb(bgr_image = bgr_image)
    YCrCb = cv2.merge([Y, Cr, Cb])

    return YCrCb

if __name__ == "__main__": 

    bgr = cv2.imread(filename = "resource/field.jpg")
    # bgr = cv2.imread(filename = "resource/image.png")
    bgr_copy = bgr.copy()
    
    bgr_gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    ycrcb = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)

    dCgCrCb = BGR2DCgCrCb(bgr_image = bgr)

    b, g, r = cv2.split(bgr)

    ret, bgr_gray_bin = cv2.threshold(bgr_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    bgr_gray_otsu_gaussian_bulured = cv2.GaussianBlur(bgr_gray_bin, (21, 21), 0)

    edges = cv2.Canny(bgr_gray_otsu_gaussian_bulured, 50, 100)

    lines = cv2.HoughLines(edges, 1, np.pi/180, 500)

    if lines is not None:
        for line in lines:
            rho, theta = line[0]
            a = np.cos(theta)
            b = np.sin(theta)
            x0 = a * rho
            y0 = b * rho
            # 延长线段使其贯穿屏幕
            x1 = int(x0 + 1000 * (-b))
            y1 = int(y0 + 1000 * (a))
            x2 = int(x0 - 1000 * (-b))
            y2 = int(y0 - 1000 * (a))
            cv2.line(bgr_copy, (x1, y1), (x2, y2), (0, 0, 255), 2)

    cv2.imshow('Standard Hough', bgr_copy)
    cv2.imshow("edges", edges)
    cv2.imshow("dCgCrCb", g)
    cv2.waitKey(5000)
    cv2.destroyAllWindows()