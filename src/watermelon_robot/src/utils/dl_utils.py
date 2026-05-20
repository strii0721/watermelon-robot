import cv2
from utils import CVUtils
from ultralytics import YOLO


class DLUtils: 
    
    @classmethod
    def predict_targets(cls, 
                        model: YOLO, 
                        device,
                        color_image, 
                        depth_image, 
                        camera_intrinsics) -> list:

        rtn = model.predict(source = color_image, 
                            verbose = False, 
                            device = device)
        results = rtn[0]
        boxes = results.boxes
        target_list = []

        if boxes is not None:
            for box in boxes:
                cls_id = int(box.cls[0].item())
                name = results.names.get(cls_id, str(cls_id))

                if name == 'watermelon':
                    box_pixel_x1, box_pixel_y1, box_pixel_x2, box_pixel_y2 = box.xyxy[0].tolist()
                    confidence = float(box.conf[0].item())
                    center_pixel_x = int((box_pixel_x1 + box_pixel_x2) / 2)
                    center_pixel_y = int((box_pixel_y1 + box_pixel_y2) / 2)
                    crosshair_pixel_x = center_pixel_x
                    crosshair_pixel_y = int(box_pixel_y1) - int((box_pixel_y1 - box_pixel_y2) / 8)
                    
                    target = CVUtils.calculate_camera_coordinate(center_pixel = (crosshair_pixel_x, crosshair_pixel_y), 
                                                                 depth_image = depth_image, 
                                                                 camera_intrinsics = camera_intrinsics)
                    label = f'{name} {confidence:.2f}'
                    mark_size = 5
                    cv2.rectangle(color_image, (int(box_pixel_x1), int(box_pixel_y1)), (int(box_pixel_x2), int(box_pixel_y2)), (0, 255, 0), 2)
                    cv2.circle(color_image, (center_pixel_x, center_pixel_y), mark_size, (0, 0, 255), -1)
                    cv2.line(color_image, (crosshair_pixel_x - mark_size, crosshair_pixel_y), (crosshair_pixel_x + mark_size, crosshair_pixel_y), (0, 0,255), 2)
                    cv2.line(color_image, (crosshair_pixel_x, crosshair_pixel_y - mark_size), (crosshair_pixel_x, crosshair_pixel_y + mark_size), (0, 0,255), 2)
                    cv2.putText(color_image, label, (int(box_pixel_x1), int(box_pixel_y1)-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                    cv2.putText(color_image, f'Xc:{target[0]:.2f} Yc:{target[1]:.2f} Zc:{target[2]:.2f}', (int(box_pixel_x1), int(box_pixel_y1) + 20),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

                    if DLUtils.check_target_validation(target_coordinate = target): 
                        target_list.append(target)

        return target_list

    @classmethod
    def check_target_validation(cls, 
                                target_coordinate: tuple): 
        
        if not ((-200 < target_coordinate[0] and target_coordinate[0] < 200) and (-200 < target_coordinate[1] and target_coordinate[1] < 200) and (0 < target_coordinate[2] and target_coordinate[2] < 500)):
            return False
        
        if not(target_coordinate[0] > -50):
            return False
        
        return True
    
