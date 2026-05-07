from fairino import Robot
import time
# 与机器人控制器建立连接，连接成功返回一个机器人对象
robot = Robot.RPC('192.168.58.2')
type = 1
name = "tpd2026"
period_ms = 1000

robot.SetTPDParam(name, period_ms)
robot.Mode(1)
time.sleep(1)
robot.DragTeachSwitch(1)
_, state = robot.IsInDragTeach()
print(state)
robot.SetTPDStart(name, period_ms)
print("SetTPDStart")
time.sleep(5)
robot.SetWebTPDStop()
robot.DragTeachSwitch(0)

time.sleep(1)
print(f"开始复现")

ovl = 20
blend = 1

error,start_pose = robot.GetTPDStartPose(name)
print(f"start pose, xyz is: {start_pose[0]},{start_pose[1]},{start_pose[2]}. \n"
      f"rpy is: {start_pose[3]},{start_pose[4]},{start_pose[5]}")
robot.MoveCart(start_pose, 0, 0)

time.sleep(1)
rtn = robot.MoveTPD(name, blend, ovl)
print(f"MoveTPD rtn is: {rtn}")
time.sleep(1)
robot.SetTPDDelete(name)

robot.CloseRPC()