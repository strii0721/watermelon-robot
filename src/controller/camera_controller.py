import pyrealsense2 as rs
import numpy as np
import time


class CameraController:

    def __init__(self):
        self.pipeline = rs.pipeline()
        self.config = rs.config()

        self.config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
        self.config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
        self.pipeline.start(self.config)
        self.align = rs.align(rs.stream.color)
        print("Camera initialized and streaming started.")

    def get_frames(self):
        """Capture a pair of aligned color and depth frames."""
        frames = self.pipeline.wait_for_frames()
        aligned_frames = self.align.process(frames)
        aligned_depth_frame = aligned_frames.get_depth_frame()
        aligned_color_frame = aligned_frames.get_color_frame()
        img_color = np.asanyarray(aligned_color_frame.get_data())
        img_depth = np.asanyarray(aligned_depth_frame.get_data())
        matrix = aligned_depth_frame.profile.as_video_stream_profile().intrinsics
        return img_color, img_depth, aligned_depth_frame, aligned_color_frame, matrix

    def median_depth(self, depth_frame, cx, cy, window_size=5):
        """Calculate the median depth in a square window around the pixel (cx, cy)."""
        rad = max(0, window_size // 2)
        w = depth_frame.get_width()
        h = depth_frame.get_height()

        xs = np.clip(np.arange(cx - rad, cx + rad + 1), 0, w - 1)
        ys = np.clip(np.arange(cy - rad, cy + rad + 1), 0, h - 1)

        vals = []
        for y in ys:
            for x in xs:
                d = depth_frame.get_distance(int(x), int(y))
                if d > 0:
                    vals.append(d)
        if len(vals) == 0:
            return 0.0
        return float(np.median(vals))

    def deproject_pixel_to_point(self, intrinsics, px, py, depth):
        """Convert pixel coordinates to 3D point in camera space."""
        pt = rs.rs2_deproject_pixel_to_point(
            intrinsics, [float(px), float(py)], float(depth)
        )
        return float(pt[0]), float(pt[1]), float(pt[2])

    def stop(self):
        """Stop the camera streaming."""
        self.pipeline.stop()
        print("Camera streaming stopped.")

    def get_3d_camera_coordinate(depth_pixel, aligned_depth_frame, depth_intrin):
        x = depth_pixel[0]
        y = depth_pixel[1]
        dis = aligned_depth_frame.get_distance(x, y)  # 获取该像素点对应的深度
        # print ('depth: ',dis)       # 深度单位是m
        camera_coordinate = rs.rs2_deproject_pixel_to_point(depth_intrin, depth_pixel, dis)
        print("camera_coordinate: ", camera_coordinate)

        return dis, camera_coordinate
