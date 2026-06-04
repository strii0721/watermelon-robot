#
# Author:       strii0721
# Email:        strii0721@outlook.com
# Created on:   Thu Jun 04 2026
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


from flask import Flask, Response, render_template_string, request, jsonify
from rclpy.node import Node
from utils import NodeUtils
from sensor_msgs.msg import Image
from rclpy.qos import qos_profile_sensor_data
from cv_bridge import CvBridge
import cv2
from functools import partial
from types import SimpleNamespace
import rclpy
from rclpy.subscription import Subscription
from ament_index_python.packages import get_package_share_directory
package_share_dir = get_package_share_directory('watermelon_robot')
import os
import threading
import time

class VideoSlot:

    def __init__(self):
        self.subscriber_callback: callable = None
        self.channel_name: str = None
        self.subscriber: Subscription = None
        self.data: bytes = None
        self.url: str = None


class VideoSlotList:
    
    def __init__(self, 
                 url: str, 
                 slot_number: int):
        """管理某个页面的视频坑位。

        Args:
            url (str): 页面的 url 。
            slot_number (int): 页面视频坑位的总数。
        """        
        
        self.url:str = url
        self.video_slot_list:list[VideoSlot] = [VideoSlot() for _ in range(slot_number)]
        
    def register_video_slot(self,
                            caller: Node,
                            video_slot_nomeric: int,
                            channel_name: str, 
                            subscriber_callback: callable, 
                            flask_app: Flask, 
                            url: str, 
                            endpoint_name: str,
                            response_function: callable) -> bool:
        """注册一个坑位。一个页面上的视频坑位总数在一开始的时候就是固定的，如果注册的视频坑位编号不存在则会注册失败。

        Args:
            caller (Node): 函数调用对象，应当是一个 ROS2 的 Node，主要为了创建 subscriber。
            slot_nomeric (int): 视频坑位编号。
            channel_name (str): 频道编号，就是 ROS2 的 topic 名称。
            subscriber_callback (callable): 用于接收视频流的处理函数。由于是从 ROS2 中接收的视频流，然后通过 Flask发布，所以采用了 Cache 机制。
            flask_app (Flask): 注册路由用的 Flask App 对象。
            url (str): Flask 路由。
            endpoint_name (str): Flask endpoint 名称。
            response_function (callable): 处理 Flask 路由用的函数。

        Returns:
            bool: 是否创建成功。True 则创建成功。
        """        
        
        is_success = False
        
        if video_slot_nomeric in range(len(self.video_slot_list)):
            
            video_slot = self.video_slot_list[video_slot_nomeric]
            video_slot.subscriber_callback = subscriber_callback
            self.set_video_slot_channel_name(caller = caller, 
                                             video_slot_nomeric = video_slot_nomeric, 
                                             channel_name = channel_name)
            video_slot.data = None
        
            video_slot.url = url
            flask_app.add_url_rule(rule = url, 
                                   endpoint = endpoint_name,
                                   view_func = partial(response_function, 
                                                       video_slot_list = self,
                                                       video_slot_nomeric = video_slot_nomeric))
            self.video_slot_list[video_slot_nomeric] = video_slot
            is_success = True
            
        return is_success
        
    def get_video_slot(self, 
                       slot_nomeric: int) -> VideoSlot | None:
        """获取坑位列表中的 slot 对象。

        Args:
            slot_nomeric (int): slot 编号。

        Returns:
            VideoSlot | None: 获得的 slot 对象。
        """        
        
        if slot_nomeric in range(len(self.video_slot_list)):
            return self.video_slot_list[slot_nomeric]
        else:
            return None
        
    def set_video_slot_channel_name(self, 
                                    caller: Node,
                                    video_slot_nomeric: int, 
                                    channel_name: str) -> None:
        
        video_slot = self.video_slot_list[video_slot_nomeric]
        video_slot.channel_name = channel_name
        if video_slot.subscriber is not None:
            caller.destroy_subscription(video_slot.subscriber)
        video_slot.subscriber = caller.create_subscription(msg_type = Image, 
                                                           topic = channel_name, 
                                                           callback = partial(video_slot.subscriber_callback, 
                                                                              video_slot_list = self,
                                                                              video_slot_nomeric = video_slot_nomeric) ,
                                                           qos_profile = qos_profile_sensor_data)
    
    
class WebApp(Node):
    
    def __init__(self):
        
        super().__init__("web_app")
        NodeUtils.node_initializer(self)
        
        self.API_VERSION = 1
        
        self.video_slot_list: VideoSlotList = VideoSlotList(url = "index", 
                                                            slot_number = 2)
        
        self.cv_bridge:CvBridge = CvBridge()
        static_dir = os.path.join(package_share_dir, 'static')
        self.app:Flask = Flask(__name__, 
                               static_folder = static_dir,  )
        
        self.video_slot_list.register_video_slot(caller = self, 
                                           video_slot_nomeric = 0,
                                           channel_name = self.input_0, 
                                           subscriber_callback = self.cache_frame_data, 
                                           flask_app = self.app, 
                                           url = self.generate_url(type = "api", url = "/streaming/0"), 
                                           endpoint_name = "video_slot_0",
                                           response_function = self.response_video)
        
        self.video_slot_list.register_video_slot(caller = self, 
                                           video_slot_nomeric = 1,
                                           channel_name = self.input_1, 
                                           subscriber_callback = self.cache_frame_data, 
                                           flask_app = self.app, 
                                           url = self.generate_url(type = "api", url = "/streaming/1"), 
                                           endpoint_name = "video_slot_1",
                                           response_function = self.response_video)
        
        self.app.add_url_rule(rule = "/", 
                              endpoint = "index", 
                              view_func = self.to_index)
        
        self.app.add_url_rule(rule = self.generate_url(type = "api", url = "/chassis"), 
                              endpoint = "chassis", 
                              view_func = self.toggle_chassis, 
                              methods = ["POST"])
        
        self.app.add_url_rule(rule = self.generate_url(type = "api", url = "/channel-name"), 
                              endpoint = "channel_name", 
                              view_func = self.change_channel_name, 
                              methods = ["POST"])
        
        flask_thread = threading.Thread(
            target=self.app.run, 
            kwargs={"host": "0.0.0.0", "port": self.port, "threaded": True, "use_reloader": False},
            daemon=True)
        flask_thread.start()
        NodeUtils.node_initialized(self)
        
    
    def generate_url(self, 
                     type: str, 
                     url: str) -> str:
        
        match type:
            case "api":
                fined_url = f"/api/v{self.API_VERSION}{url}"
            case "static":
                fined_url = f"/static{url}"
            case _:
                fined_url = url
        
        return fined_url
        
        
    def cache_frame_data(self, 
                         frame: Image, 
                         video_slot_list: VideoSlotList,
                         video_slot_nomeric: int) -> None:
        
        frame = self.cv_bridge.imgmsg_to_cv2(img_msg = frame, 
                                             desired_encoding = "passthrough")
        rtn, buffer = cv2.imencode('.jpg', frame)
        if rtn:
            video_slot_list.get_video_slot(slot_nomeric = video_slot_nomeric).data = buffer.tobytes()
    
    def response_video(self, 
                       video_slot_list: VideoSlotList,
                       video_slot_nomeric: int):
        
        def generate_data():
            while True:
                if video_slot_list.get_video_slot(slot_nomeric = video_slot_nomeric).data is not None:
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + video_slot_list.get_video_slot(slot_nomeric = video_slot_nomeric).data +   b'\r\n')
                time.sleep(1 / self.fps)
        
        return Response(generate_data(), 
                        mimetype='multipart/x-mixed-replace; boundary=frame')
        
    def to_index(self):
        
        template_path = os.path.join(package_share_dir, "templates", "index.html")
        with open(template_path, 'r', encoding='utf-8') as f:
            html_string = f.read()
            
        context = {
            "title": f"{self.get_name()} 监控面板",
            "default_channel_0": f"{self.input_0}",
            "default_channel_1": f"{self.input_1}",
            "subtitle": "SURVEILLANCE SYSTEM v1.0"
            }
        return render_template_string(source = html_string, 
                                      **context)
        
    def toggle_chassis(self):
        
        data = request.get_json()
        action = data.get("action")
        
        match action:
            
            case "start":
                self.get_logger().info(f"start chassis...")
            case "stop":
                self.get_logger().info(f"stop chassis...")
                
        return jsonify({
            "status": "success", 
            "message": ""
        })
        
    def change_channel_name(self):
        
        data = request.get_json()
        channel_name = data.get("channel_name")
        video_slot_nomeric = data.get("video_slot_nomeric")
        
        self.video_slot_list.set_video_slot_channel_name(caller = self, 
                                                         video_slot_nomeric = video_slot_nomeric,
                                                         channel_name = channel_name)
        
        return jsonify({
            "status": "success", 
            "message": ""
        })
        
def main():

    rclpy.init()
    web_app = WebApp()
    rclpy.spin(web_app)
    web_app.destroy_node()
    rclpy.shutdown()
    

if __name__ == '__main__':

    main()