from fairino import Robot

robot = Robot.RPC('192.168.58.2')
joint_pos = [0, -90, 90, 0, 90, 0]
tool = 0
user = 0
# vel = 100.0
# acc = 100.0
# ovl = 100.0
# epos = [0.0] * 4
# blendT = 0.0
# flag = 0
# offset_pos = [0.0] * 6
code = robot.MoveCart(desc_pos=[-820, -202, 50, 90, 0, 0], 
                   tool=tool, 
                   user=user, 
                #    vel=vel, 
                #    acc=acc, 
                #    ovl=ovl, 
                #    exaxis_pos=epos, 
                #    blendT=blendT, 
                #    offset_flag=flag, 
                #    offset_pos=offset_pos
                   )
print(code)
robot.CloseRPC()