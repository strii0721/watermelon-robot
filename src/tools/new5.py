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


bgr = cv2.imread(filename = "resource/image.png")

dCgCrCb = BGR2DCgCrCb(bgr)

h, w = bgr.shape[:2]

gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)

blurred = cv2.GaussianBlur(dCgCrCb, (5, 5), 0)

# _, binary = cv2.threshold(gray, 80, 255, cv2.THRESH_BINARY)
_, binary = cv2.threshold(dCgCrCb, 80, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

# kernel = np.ones((5, 5), np.uint8)
# binary = cv2.erode(binary, kernel)
kernel = np.ones((5, 1), np.uint8)
binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
# binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
# binary = cv2.erode(binary, kernel)

center_points = []
start_y = h - 20
end_y = h // 2
step = 10

for y in range(start_y, end_y, -step):
    row = binary[y, :]
    white_pixels = np.where(row == 255)[0]
    
    if len(white_pixels) > 0:
        center_x = int(np.mean(white_pixels))
        center_points.append((center_x, y))
        cv2.circle(bgr, (center_x, y), 5, (255, 0, 0), -1)

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

        cv2.line(bgr, (x1, y1), (x2, y2), (0, 0, 255), 4)

cv2.imshow("blurred", binary)
cv2.imshow("dCgCrCb", dCgCrCb)
cv2.imshow("bgr", bgr)
cv2.waitKey(0)
cv2.destroyAllWindows()