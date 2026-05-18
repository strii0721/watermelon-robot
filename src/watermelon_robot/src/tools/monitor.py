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
from utils import CommonUtils

class Monitor(Node):

    def __init__(self): 

        super().__init__("monitor")
        CommonUtils.node_initializer(self)

        self.render_interval = int((1/self.fps) * 1000)
        self.cv_bridge = CvBridge()
        self.latest_frame = None
        
        self.sub_camera_current_frame = self.create_subscription(msg_type = Image, 
                                                                 topic = self.input_0,
                                                                 qos_profile = qos_profile_sensor_data, 
                                                                 callback = self.render)
        flag = False
        if hasattr(self, "is_livestream"):
            if self.is_livestream:
                flag = True
        if flag:
            self.app = Flask(__name__)
            self.lastest_frame = None
            self.app.add_url_rule('/', 'index', self.index)
            self.app.add_url_rule('/video_feed', 'video_feed', self.video_feed)
            self.flask_thread = threading.Thread(target=self.flask_server_start, daemon=True)
            self.flask_thread.start()
            CommonUtils.node_initialized(self)
            self.get_logger().info(f"{self.get_name()} 运行模式：网络推流 | 访问端口：{self.livestream_port}")
        else: 
            CommonUtils.node_initialized(self)
            self.get_logger().info(f"{self.get_name()} 运行模式：终端")


    def render(self, message): 
        
        self.latest_frame = self.cv_bridge.imgmsg_to_cv2(message, desired_encoding="passthrough")
        flag = False
        if hasattr(self, "is_livestream"):
            if self.is_livestream:
                flag = True
        if flag:
            cv2.waitKey(self.render_interval)
        else:
            cv2.imshow(f"{self.get_name()}", self.latest_frame)
            cv2.waitKey(self.render_interval)


    def flask_server_start(self):

        self.app.run(host="0.0.0.0", port=self.livestream_port, threaded=True, use_reloader=False)


    def generate_frames(self):

        while True:

            if self.latest_frame is not None:
    
                rtn, buffer = cv2.imencode('.jpg', self.latest_frame)
                if rtn:
                    frame_bytes = buffer.tobytes()
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                    
            time.sleep(1/self.fps)


    def video_feed(self):

        return Response(self.generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


    def index(self):
        html = f"""
        <html>
            <body style="text-align: center;">
                <h2>监视器 {self.get_name()} 实时画面</h2>
                <img src="/video_feed" style="border: 2px solid black; max-width: 100%;">
            </body>
        </html>
        """
        return render_template_string(html)


def main():

    rclpy.init()
    monitor = Monitor()
    rclpy.spin(monitor)
    monitor.destroy_node()
    rclpy.shutdown()
    

if __name__ == '__main__':

    main()