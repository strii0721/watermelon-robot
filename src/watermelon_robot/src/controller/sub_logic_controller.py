#
# Author:       strii0721
# Email:        strii0721@outlook.com
# Created on:   Wed May 13 2026
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


import rclpy
from rclpy.node import Node
from utils import CommonUtils
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Image, CameraInfo
import message_filters
from utils import CVUtils
from watermelon_robot_interface.srv import ILogicControllerComm, IChassisStartStopControl
from watermelon_robot_interface.msg import IChassisDirectionControl
from utils import config
import cv2
import time
from cv_bridge import CvBridge
from protocol import LogicControllerCommCode, QOSFile
from protocol import ST_SUB_LOGIC_CONTROLLER as ST
from typing import cast
from types import SimpleNamespace
from utils import ModelUtils
from utils import DLUtils


class SubLogicController(Node):

    def __init__(self):

        super().__init__("sub_logic_controller")
        CommonUtils.node_initializer(self)

        self.latest_frame = SimpleNamespace()
        self.angular_error = 0.0
        self.last_frame_time = time.time()
        self.use_yolo = config.lane_detection.use_yolo
        self.publish_direction_error_last_triggered = time.time()
        self.stop_timer = None
        if self.use_yolo:
            self.model = ModelUtils.load_model(model_name = config.lane_detection.model.name, 
                                               task = config.lane_detection.model.task, 
                                               use_engine = config.lane_detection.model.use_engine,
                                               confidence = config.lane_detection.model.confidence)
        else:
            self.reference_frames = []

        self.heartbeat_timer = self.create_timer(timer_period_sec = self.heartbeat_interval, 
                                                 callback = self.heartbeat)
        
        self.sub_eye_on_chassis_color_raw = message_filters.Subscriber(self, 
                                                                       Image, 
                                                                       self.input_0,
                                                                       qos_profile = qos_profile_sensor_data)
        
        self.sub_eye_on_chassis_depth_raw = message_filters.Subscriber(self, 
                                                                       Image, 
                                                                       self.input_1,
                                                                       qos_profile = qos_profile_sensor_data)
        
        self.sub_eye_on_chassis_camera_intrinsics = message_filters.Subscriber(self, 
                                                                               CameraInfo, 
                                                                               self.input_2,
                                                                               qos_profile = qos_profile_sensor_data)
        
        self.pub_chassis_direction = self.create_publisher(IChassisDirectionControl, 
                                                           self.output_0, 
                                                           qos_profile = QOSFile.reliable_qos)
        
        self.pub_eye_on_chassis_direction = self.create_publisher(Image, 
                                                                  self.output_1, 
                                                                  qos_profile = qos_profile_sensor_data)
        
        self.pub_eye_on_chassis_binary_morphology = self.create_publisher(Image, 
                                                                          self.output_2, 
                                                                          qos_profile = qos_profile_sensor_data)
        
        self.srv_logic_controller_comm = self.create_service(srv_type = ILogicControllerComm, 
                                                             srv_name = self.duplex_0, 
                                                             callback = self.answer_super_logic_controller)
        
        self.cli_chassis_start_stop = self.create_client(srv_type = IChassisStartStopControl, 
                                                         srv_name = self.duplex_1)
        
        self.approximate_time_synchronizer = message_filters.ApproximateTimeSynchronizer(
            fs = [self.sub_eye_on_chassis_color_raw, 
                  self.sub_eye_on_chassis_depth_raw, 
                  self.sub_eye_on_chassis_camera_intrinsics],
            queue_size = self.ats.queue_size,
            slop = self.ats.slop
        )
        self.approximate_time_synchronizer.registerCallback(self.recieve_latest_frame)

        CommonUtils.node_initialized(self)
        CommonUtils.transfer_node_state(self, ST.ENABLED)
        
        # TODO 测试用，之后记得删
        if self.is_test:
            self.test_timer = self.create_timer(timer_period_sec = 0.01, 
                                                callback = self.test_send)
            video_path = "/home/lynchpin/repository/watermelon-robot/resource/datasets/lane-detection/legacy/video-5.mp4"
            self.video_capture = cv2.VideoCapture(video_path)
        
    def test_send(self):
        
        rtn, frame = self.video_capture.read()
        if rtn: self.latest_frame.color_image = frame
        
    def chassis_start_done(self, 
                           future: rclpy.Future):
        """启动底盘响应的回调函数。

        Args:
            future (rclpy.Future): 底盘响应的 Future 对象。
        """        
        
        response = cast(IChassisStartStopControl.Response, future.result())
        if response.is_success:
            self.get_logger().info(f"底盘启动成功！")
            CommonUtils.transfer_node_state(self, ST.ENABLED)
            
        else:
            self.get_logger().warn(f"底盘启动失败！")
            CommonUtils.transfer_node_state(self, ST.QUIT)

    def enable_chassis(self) -> rclpy.Future:
        """启动底盘。
        """        
        
        request = IChassisStartStopControl.Request()
        request.timestamp = time.time()
        request.status = True
        future = self.cli_chassis_start_stop.call_async(request = request)
        future.add_done_callback(callback = self.x)
        CommonUtils.transfer_node_state(self, ST.PENDING)
        
    def chassis_stop_done(self, 
                          future: rclpy.Future):
        """关闭底盘响应的回调函数。

        Args:
            future (rclpy.Future): 底盘响应的 Future 对象。
        """        
        
        response = cast(IChassisStartStopControl.Response, future.result())
        if response.is_success:
            self.get_logger().info(f"底盘已停止！")
            CommonUtils.transfer_node_state(self, ST.DISABLED)
            
        else:
            self.get_logger().warn(f"底盘停止失败！")
            CommonUtils.transfer_node_state(self, ST.QUIT)
        
    def disable_chassis(self):
        """关闭底盘。
        """        
        
        request = IChassisStartStopControl.Request()
        request.timestamp = time.time()
        request.status = False
        future = self.cli_chassis_start_stop.call_async(request = request)
        future.add_done_callback(callback = self.chassis_stop_done)
        CommonUtils.transfer_node_state(self, ST.PENDING)

    def answer_super_logic_controller(self, 
                                      request: ILogicControllerComm.Request, 
                                      response: ILogicControllerComm.Response) -> ILogicControllerComm.Response:
        """响应上逻辑控制器发来的逻辑控制器命令。此处应用重传机制，至少一次重传才会请求成功。

        Args:
            request (ILogicControllerComm.Request): 逻辑控制器命令请求。
            response (ILogicControllerComm.Response): 逻辑控制器命令响应。

        Returns:
            ILogicControllerComm.Response: 逻辑控制器命令响应。
        """        
        
        comm_code = request.comm_code
        retransmission = request.retransmission
        self.get_logger().info(f"收到上逻辑控制器通信，通信码 {comm_code}")
        response.is_success = False
        response.retransmission = retransmission
        
        match comm_code:
            case LogicControllerCommCode.DISABLE_CHASSIS:
                if self.state == ST.DISABLED:
                    response.is_success = True
                else:
                    self.disable_chassis()

            case LogicControllerCommCode.ENABLE_CHASSIS: 
                if self.state == ST.ENABLED:
                    response.is_success = True
                else:
                    self.enable_chassis()
                    
        return response
    
    def publish_direction_error(self) -> None:
        """发布角度误差（角度）。
        """        
        
        now = time.time()
        if now - self.publish_direction_error_last_triggered > config.chassis.pid_controller.control_interval:
            control_msg = IChassisDirectionControl()
            control_msg.timestamp = time.time()
            control_msg.angular_error = self.angular_error
            self.pub_chassis_direction.publish(msg = control_msg)
            self.publish_direction_error_last_triggered = now
    
    def check_terminal(self, 
                       reach_terminal: bool) -> None:
        """检查是否抵达终点，若是则停止底盘。当且仅当连续时长的帧检测到抵达道路边缘或检测不到道路，判断为抵达终点。

        Args:
            reach_terminal (bool): 当前帧是否符合到达终点的条件。
        """        
        
        if reach_terminal:
            if self.stop_timer:
                    if time.time() - self.stop_timer > config.chassis.stop_delay:
                            self.disable_chassis()
            else: 
                self.stop_timer = time.time()
    
    def analysis_latest_frame(self):
        """分析最新帧获取并保存角度误差，并发布附加导航线叠加层的彩色图片消息。
        """      

        if vars(self.latest_frame): 
            color_image = self.latest_frame.color_image.copy()
            cv_bridge = CvBridge()
            
            if self.use_yolo:
                reach_terminal, self.angular_error = DLUtils.predict_lane(model = self.model, 
                                                                          source_image = color_image, 
                                                                          roi_y_min_portion = config.lane_detection.roi.y_min_portion, 
                                                                          roi_y_max_portion = config.lane_detection.roi.y_max_portion, 
                                                                          detect_step = config.lane_detection.detect_step)
            else:
                [binary, 
                 binary_suppressed, 
                 binary_mask] = CVUtils.lane_detection_preprocess(source_image = color_image, 
                                                                  roi_y_min_portion = config.lane_detection.roi.y_min_portion, 
                                                                  roi_y_max_portion = config.lane_detection.roi.y_max_portion, 
                                                                  maximum_window_size = config.lane_detection.cv.maximum_window_size,
                                                                  reference_frames = self.reference_frames)
                self.reference_frames.append(binary_suppressed)
                canvas = color_image.copy()
                self.reference_frames = self.reference_frames[-config.lane_detection.cv.reference_depth:]
                reach_terminal, self.angular_error= CVUtils.predict_lane(source_image = binary_mask, 
                                                                         canvas = canvas, 
                                                                         roi_y_min_portion = config.lane_detection.roi.y_min_portion, 
                                                                         roi_y_max_portion = config.lane_detection.roi.y_max_portion, 
                                                                         detect_step = config.lane_detection.detect_step)
            self.check_terminal(reach_terminal)
                
            height, width = color_image.shape[:2]
            now_time = time.time()
            real_fps = int(1/(now_time - self.last_frame_time))
            self.last_frame_time = now_time
            cv2.putText(img = color_image, 
                        text = f"FPS {real_fps} | Frame Size {width}x{height}", 
                        org = (5, 20), 
                        fontFace = cv2.FONT_HERSHEY_SIMPLEX, 
                        fontScale = 0.5, 
                        color = (0, 0, 255), 
                        thickness = 2)
            image_message = cv_bridge.cv2_to_imgmsg(color_image, encoding="bgr8")
            self.pub_eye_on_chassis_direction.publish(msg = image_message)
            if not self.use_yolo:
                additional = cv_bridge.cv2_to_imgmsg(binary_mask, encoding = "mono8")
                self.pub_eye_on_chassis_binary_morphology.publish(msg = additional)            

    def recieve_latest_frame(self, 
                             color_image_msg: Image, 
                             depth_image_msg: Image, 
                             camera_info_msg: CameraInfo) -> None:
        """接收摄像头回传的最新帧图片消息并保存。

        Args:
            color_image_msg (Image): 彩色图片消息。
            depth_image_msg (Image): 深度图片消息。
            camera_info_msg (CameraInfo): 相机内参。
        """  
        
        cv_bridge = CvBridge()
        self.latest_frame.color_image = cv_bridge.imgmsg_to_cv2(color_image_msg, desired_encoding = "passthrough")
        self.latest_frame.depth_image = cv_bridge.imgmsg_to_cv2(depth_image_msg, desired_encoding = "passthrough")
        self.latest_frame.camera_intrinsics = camera_info_msg
        
    def wait_quit(self) -> None:
        """等待退出。
        """        
        
        self.get_logger().warn(f"节点已进入退出状态，若未退出请手动退出...")
            
    def heartbeat(self) -> None:
        """节点的核心业务循环，加入了状态机机制。
        """        
        
        match self.state:
            case ST.QUIT:
                self.wait_quit()
                
            case ST.ENABLED:
                self.analysis_latest_frame()
                self.publish_direction_error()
                
            case ST.DISABLED:
                pass
            
            case ST.PENDING:
                pass


def main():

    rclpy.init()
    sub_logic_controller = SubLogicController()
    rclpy.spin(sub_logic_controller)
    sub_logic_controller.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()