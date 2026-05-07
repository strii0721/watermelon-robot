from time import sleep
import time
from fairino import Robot

# 与机器人控制器建立连接
robot = Robot.RPC('192.168.58.2')

def TestServoJUDP(self):
    # 设置回调
    def callback(src_type, count, cmd_id, data_len, content):
        print("回调函数: cmd_id={} count={} data_len={} content={}".format(cmd_id, count, data_len, content))
        return 0

    robot.SetUDPCmdRpyCallback(callback)
    # # 初始化关节位置和外部轴位置
    j= [105, -108, 74, -66, -88.893, -1.621]
    offset_pos = [0, 0, 0, 0, 0, 0]
    epos = [0, 0, 0, 0]
    # # 移动到初始位置
    result=robot.MoveJ(joint_pos=j, tool=0, user=0, vel=100, acc=100, ovl=100,exaxis_pos=epos, blendT=-1, offset_flag=0, offset_pos=offset_pos)
    print("MoveJ返回结果: {}".format(result))
    vel = 0.0
    acc = 0.0
    cmdT = 0.016
    filterT = 0.0
    gain = 0.0
    flag = 0
    dt = 0.1
    cmdID = 0

    # 获取当前关节位置
    ret, j = robot.GetActualJointPosDegree(flag)
    if ret != 0:
        print(f"GetActualJointPosDegree errcode:{ret}")
    while 1:
        count = 300
        result = robot.ServoMoveStart(cmdType=1)
        print("ServoMoveStart返回结果: {}".format(result))
        while count > 0:
            result = robot.ServoJ(joint_pos=j, axisPos=epos, acc=acc, vel=vel, cmdT=cmdT,filterT=filterT, gain=gain, id=cmdID, cmdType=1)
            j[0] += dt
            j[1] += dt
            j[2] += dt
            j[3] += dt
            j[4] += dt
            j[5] += dt
            count -= 1
            time.sleep(0.01)
        result = robot.ServoMoveEnd(cmdType=1)
        print("ServoMoveEnd返回结果: {}".format(result))

        count = 300
        result = robot.ServoMoveStart(cmdType=1)
        print("ServoMoveStart返回结果: {}".format(result))
        while count > 0:
            result = robot.ServoJ(joint_pos=j, axisPos=epos, acc=acc, vel=vel, cmdT=cmdT,filterT=filterT, gain=gain, id=cmdID, cmdType=1)
            j[0] -= dt
            j[1] -= dt
            j[2] -= dt
            j[3] -= dt
            j[4] -= dt
            j[5] -= dt
            count -= 1
            time.sleep(0.01)
        result = robot.ServoMoveEnd(cmdType=1)
        print("ServoMoveEnd返回结果: {}".format(result))
    robot.CloseRPC()
    return 0
TestServoJUDP(robot)