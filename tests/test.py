from fairino import Robot
import time
# 与机器人控制器建立连接，连接成功返回一个机器人对象
robot = Robot.RPC('192.168.58.2')
# for i in range(2000):
#     robot.StartJOG(ref = 0, 
#                    nb = 1, 
#                    dir = 1, 
#                    max_dis = 1.0)
#     time.sleep(0.1)
#     robot.ImmStopJOG()
#     time.sleep(0.1)
tool = 0
user = 0
# vel = 100.0
# acc = 100.0
# ovl = 100.0
oacc = 100.0
blendT = 0.0
blendR = 0.0
epos = [0.0] * 4
# flag = 0
# offset_pos = [0.0] * 6

j0 = [0] * 6
j1 = [-11.904, -99.669, 117.473, -108.616, -91.726, 74.256]
j2 = [-45.615, -106.172, 124.296, -107.151, -91.282, 74.255]
j3 = [-29.777, -84.536, 109.275, -114.075, -86.655, 74.257]
j4 = [-31.154, -95.317, 94.276, -88.079, -89.740, 74.256]
rtn = robot.MoveJ(joint_pos=j0, 
                  tool=tool, 
                  user=user, 
                #   vel=vel, 
                #   acc=acc, 
                #   ovl=ovl, 
                  exaxis_pos=epos, 
                  blendT=blendT, 
                #   offset_flag=flag, 
                #   offset_pos=offset_pos
                )
print(f"movej errcode:{rtn}")