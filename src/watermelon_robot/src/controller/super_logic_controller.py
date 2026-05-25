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
from watermelon_robot_interface.srv import IRoboticArmAction, ILogicControllerComm
from typing import cast
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Image, CameraInfo
from utils import config
from utils import DLUtils
from utils import ModelUtils
import time
import cv2
from cv_bridge import CvBridge
import message_filters
from protocol import LogicControllerCommCode
from protocol import ST_SUPER_LOGIC_CONTROLLER as ST
from types import SimpleNamespace


class SuperLogicController(Node):

    def __init__(self):

        super().__init__("super_logic_controller")
        CommonUtils.node_initializer(self)
        
        self.latest_frame = SimpleNamespace()
        self.target_list = []
        self.current_target = None
        self.fa_on = ModelUtils.check_flash_attention()
        self.last_frame_time = time.time()
        self.model = ModelUtils.load_model(model_name = config.model.name, 
                                           use_half = config.model.use_half, 
                                           device_no = config.model.device_no, 
                                           image_size = config.model.image_size, 
                                           confidence = config.model.confidence, 
                                           iou = config.model.iou)
        
        self.heartbeat_timer = self.create_timer(timer_period_sec = self.heartbeat_interval, 
                                                 callback = self.heartbeat)
        
        self.sub_eye_on_hand_color_raw = message_filters.Subscriber(node = self, 
                                                                    msg_type = Image, 
                                                                    topic = self.input_0,
                                                                    qos_profile = qos_profile_sensor_data)
        
        self.sub_eye_on_hand_depth_raw = message_filters.Subscriber(node = self, 
                                                                    msg_type = Image, 
                                                                    topic = self.input_1,
                                                                    qos_profile = qos_profile_sensor_data)
        
        self.sub_eye_on_hand_camera_intrinsics = message_filters.Subscriber(node = self, 
                                                                            msg_type = CameraInfo, 
                                                                            topic = self.input_2,
                                                                            qos_profile = qos_profile_sensor_data)
        self.pub_eye_on_hand_boxed = self.create_publisher(msg_type = Image, 
                                                           topic = self.output_0, 
                                                           qos_profile = qos_profile_sensor_data)
        
        self.cli_robotic_arm_action_once = self.create_client(srv_type = IRoboticArmAction, 
                                                              srv_name = self.duplex_0)
        
        self.cli_logic_controller_comm = self.create_client(srv_type = ILogicControllerComm, 
                                                            srv_name = self.duplex_1)
        
        self.approximate_time_synchronizer = message_filters.ApproximateTimeSynchronizer(
            fs = [self.sub_eye_on_hand_color_raw, 
                  self.sub_eye_on_hand_depth_raw, 
                  self.sub_eye_on_hand_camera_intrinsics],
            queue_size = self.ats.queue_size,
            slop = self.ats.slop
        )
        self.approximate_time_synchronizer.registerCallback(self.recieve_latest_frame)
        
        CommonUtils.node_initialized(self)
        CommonUtils.transfer_node_state(self, ST.DETECTING)
        
    def command_sub_logic_controller(self, 
                                     comm_code: LogicControllerCommCode, 
                                     retransmission:int = 0) -> rclpy.Future:  
        """向下逻辑控制器发送命令。

        Args:
            comm_code (LogicControllerCommCode): 命令码。
            retransmission (int, optional): 请求重传次数. Defaults to 0.

        Returns:
            rclpy.Future: 下逻辑控制器响应的 Futrue 对象。
        """        
        
        request = ILogicControllerComm.Request()
        request.comm_code = comm_code
        request.retransmission = retransmission
        future = self.cli_logic_controller_comm.call_async(request)
        return future
        
    def enable_chassis_done(self, 
                            future: rclpy.Future):
        """启动底盘请求的回调函数。此处应用重传机制，若一次请求失败则会在回调中重传请求，直到成功或超过重传次数限制。

        Args:
            future (rclpy.Future): 底盘响应的 Future 对象。
        """        
        
        response = cast(ILogicControllerComm.Response, future.result())
        retransmission = response.retransmission + 1
        
        if response.is_success:
            self.get_logger().info(f"底盘启动成功！")
            CommonUtils.transfer_node_state(self, ST.DETECTING)
        else:
            if retransmission <= self.request_retransmission_limit:
                future = self.command_sub_logic_controller(comm_code = LogicControllerCommCode. ENABLE_CHASSIS, 
                                                           retransmission = retransmission)
                future.add_done_callback(callback = self.enable_chassis_done)
            else:
                self.get_logger().info(f"底盘启动失败！")
                CommonUtils.transfer_node_state(self, ST.QUIT)
            
    def enable_chassis(self) -> None:
        """发布启动底盘的请求。
        """        
        
        future = self.command_sub_logic_controller(comm_code = LogicControllerCommCode.ENABLE_CHASSIS)
        future.add_done_callback(callback = self.enable_chassis_done)
        CommonUtils.transfer_node_state(self, ST.PENDING)
    
    def operate_robotic_arm_done(self, 
                                 future: rclpy.Future) -> None:
        """机械臂动作的回调函数

        Args:
            future (rclpy.Future): 动作响应的 Future 对象。
        """        
        
        response = cast(IRoboticArmAction.Response, future.result())
        
        if response.is_success: 
            self.get_logger().info(f"机械臂执行完成")
            self.enable_chassis()
        else:
            self.get_logger().warn(f"机械臂执行异常，异常信息：{response.message}")
            CommonUtils.transfer_node_state(self, ST.QUIT)
        
    def operate_robotic_arm(self) -> None:
        """获取当前目标坐标（手眼相机坐标系）并尝试进行一次机械臂动作。
        """        
        
        if not self.current_target:
            return
        
        request = IRoboticArmAction.Request()
        request.timestamp = time.time()
        request.position_on_camera = self.current_target
        future = self.cli_robotic_arm_action_once.call_async(request)
        future.add_done_callback(callback = self.operate_robotic_arm_done)
        CommonUtils.transfer_node_state(self, ST.PENDING)
        
    def disable_chassis_done(self, 
                             future: rclpy.Future):
        """停止底盘请求的回调函数。此处应用重传机制，若一次请求失败则会在回调中重传请求，直到成功或超过重传次数限制。

        Args:
            future (rclpy.Future): 底盘响应的 Future 对象。
        """        
        
        response = cast(ILogicControllerComm.Response, future.result())
        retransmission = response.retransmission + 1
        
        if response.is_success:
            self.get_logger().info(f"底盘停止成功！")
            CommonUtils.transfer_node_state(self, ST.READY_TO_OPERATE)
        else: 
            if retransmission <= self.request_retransmission_limit:
                future = self.command_sub_logic_controller(comm_code = LogicControllerCommCode. DISABLE_CHASSIS, 
                                                           retransmission = retransmission)
                future.add_done_callback(callback = self.disable_chassis_done)
            else:
                self.get_logger().info(f"底盘停止失败！")
                CommonUtils.transfer_node_state(self, ST.QUIT)
            
    def diable_chassis(self) -> None:
        """发布停止底盘的请求。
        """        
        
        future = self.command_sub_logic_controller(comm_code = LogicControllerCommCode.DISABLE_CHASSIS)
        future.add_done_callback(callback = self.disable_chassis_done)
        CommonUtils.transfer_node_state(self, ST.PENDING)
            
    def lock_target(self) -> None: 
        """锁定视野中最靠近前进方向反方向的目标。
        """        
        
        if not self.target_list:
            return
        
        target_list = self.target_list
        target_list.sort(key=lambda target: target[0])
        self.current_target = target_list[-1]
        self.get_logger().info(f"目标已锁定！当前目标（手眼相机参考系）：{self.current_target}")
        CommonUtils.transfer_node_state(self, ST.TARGET_LOCKED)
        
    def analysis_latest_frame(self) -> None:
        """分析最新帧获取并保存目标列表，并发布附加目标框叠加层的彩色图片消息。
        """        
        
        if vars(self.latest_frame): 
            cv_bridge = CvBridge()
            self.target_list = DLUtils.predict_targets(model = self.model, 
                                                       color_image = self.latest_frame.color_image, 
                                                       depth_image = self.latest_frame.depth_image, 
                                                       camera_intrinsics = self.latest_frame.camera_intrinsics)
            
            now_time = time.time()
            fps = 1.0 / (now_time - self.last_frame_time)
            self.last_frame_time = now_time
            cv2.putText(self.latest_frame.color_image, f'FPS: {fps:.2f}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
            image_message = cv_bridge.cv2_to_imgmsg(self.latest_frame.color_image, encoding="bgr8")
            self.pub_eye_on_hand_boxed.publish(msg = image_message)
        
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
        
        self.analysis_latest_frame()
        
        match self.state:
            case ST.QUIT:
                self.wait_quit()

            case ST.DETECTING:
                self.lock_target()
                    
            case ST.TARGET_LOCKED:
                self.diable_chassis()
            
            case ST.READY_TO_OPERATE:
                self.operate_robotic_arm()
            
            case ST.PENDING:
                pass
                

def main():

    rclpy.init()
    super_logic_controller = SuperLogicController()
    rclpy.spin(super_logic_controller)
    super_logic_controller.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()