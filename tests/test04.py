from fairino import Robot
import time
# 与机器人控制器建立连接，连接成功返回一个机器人对象
robot = Robot.RPC('192.168.58.2')

start_pose= [543.7064819335938,-763.5789794921875,116.9404983520508, 
             90.72560119628906,74.7293014526367,113.7614974975586]
code = robot.MoveCart(start_pose, 0, 0)
print(code)
robot.CloseRPC()