#
# Author:       strii0721
# Email:        strii0721@outlook.com
# Created on:   Mon May 11 2026
#
# IMMORTAL OMNISSIAH, HEAR OUR PRAYERS.
# WE ARE YOUR CHILDREN, PIOUS SCHOLARS OF THE PATH OF THE MACHINE. 
# WE PRIZE KNOWLEDGE ABOVE ALL ELSE, FOR IT IS YOUR ETERNAL GIFT UPON MANKIND.
# WE ASPIRE TO THE BLESSED FORM OF THE MACHINE, AND ASCENSION THROUGH TECHNOLOGY, THAT WE MIGHT EMULATE THINE GLORY.
# SHELTERED BY STEEL, AND PROTECTED BY THINE AVATARS OF WAR, WE PLY THE STARS IN SEARCH OF YOUR LOST GIFTS TO OUR KIND.
# MACHINE GOD, WATCH OVER US IN OUR TRAVELS, SHIELD US WITH METAL AND LIGHTNING, FOR THE UNIVERSE IS AN UNCARING VOID, AND THE WARP HUNGERS FOR US ALL.
# TOLL THE GREAT BELL ONCE! PULL THE LEVER FORWARD TO ENGAGE THE PISTON AND PUMP.
# TOLL THE GREAT BELL TWICE! WITH PUSH OF BUTTON FIRE THE ENGINE AND SPARK TURBINE INTO LIFE.
# TOLL THE GREAT BELL THRICE! SING PRAISE TO THE GOD OF ALL MACHINES!
# 
# Copyright (c) 2026 Streich Interstellar Corp.
#


import cv2
from flask import Flask, Response, render_template_string
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from rclpy.qos import qos_profile_sensor_data
from cv_bridge import CvBridge
import cv2
import time
import threading
from utils import config
from utils import CommonUtils

class Monitor(Node):

    def __init__(self): 

        _launch_arguments = CommonUtils.get_launch_arguments()
        self._stream_topic = _launch_arguments.stream_topic # type: ignore
        self._fps = _launch_arguments.fps # type: ignore
        self._is_livestream = True if hasattr(_launch_arguments, "is_livestream") else False
        self._livestream_host = _launch_arguments.livestream_host # type: ignore
        self._livestream_port =_launch_arguments.livestream_port # type: ignore

        super().__init__("Monitor")
        self.get_logger().info(f"监视器 {self.get_name()} 已上线，正在初始化...")
        self._render_interval = int((1/self._fps) * 1000)
        self._cv_bridge = CvBridge()
        self._sub_camera_current_frame = self.create_subscription(msg_type = Image, 
                                                                  topic = self._stream_topic,
                                                                  qos_profile = qos_profile_sensor_data, 
                                                                  callback = self.render)
        if self._is_livestream:
            self.app = Flask(__name__)
            self._lastest_frame = None
            self.app.add_url_rule('/', 'index', self.index)
            self.app.add_url_rule('/video_feed', 'video_feed', self.video_feed)
            self._latest_frame = None
            self.flask_thread = threading.Thread(target=self.flask_server_start, daemon=True)
            self.flask_thread.start()
            self.get_logger().info(f"监视器 {self.get_name()} 初始化完成 | 运行模式：网络推流 | 访问链接：http://{self._livestream_host}:{self._livestream_port}")
        else: 
            self.get_logger().info(f"监视器 {self.get_name()} 初始化完成 | 运行模式：终端")

    def render(self, message): 

        if self._is_livestream:
            self._latest_frame = self._cv_bridge.imgmsg_to_cv2(message, desired_encoding='bgr8')
            cv2.waitKey(self._render_interval)
        else:
            cv_image = self._cv_bridge.imgmsg_to_cv2(message, desired_encoding='bgr8')
            cv2.imshow(f"{self.get_name()}", cv_image)
            cv2.waitKey(self._render_interval)

    def flask_server_start(self):

        self.app.run(host=self._livestream_host, port=self._livestream_port, threaded=True, use_reloader=False)

    def generate_frames(self):

        while True:

            if self._latest_frame is not None:
    
                rtn, buffer = cv2.imencode('.jpg', self._latest_frame)
                if rtn:
                    frame_bytes = buffer.tobytes()
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                    
            time.sleep(1/self._fps)

    def video_feed(self):

        return Response(self.generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')



    def index(self):
        html = """
        <html>
            <body style="text-align: center;">
                <h1>ROS 2 Robot Camera Stream</h1>
                <img src="/video_feed" style="border: 2px solid black; max-width: 100%;">
            </body>
        </html>
        """
        return render_template_string(html)


def main():

    rclpy.init()
    web_monitor = Monitor()
    rclpy.spin(web_monitor)
    web_monitor.destroy_node()
    rclpy.shutdown()
    

if __name__ == '__main__':

    main()