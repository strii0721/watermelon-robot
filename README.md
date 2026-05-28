## 1.部署

#### 1.1 部署资源

所有资源文件均上传至 [Google Drive](https://drive.google.com/drive/folders/1sn2bvBRu4CmVb2lKj7wDZh9eaKqxcOvn?usp=sharing)，需要下载解压放置于项目根目录下的 [resource](resource) 文件夹中。

1. 数据集
   之后有新增的数据集转换为 YOLO 格式放到 [dataset](resource/datasets)下对应子任务目录即可。数据集在训练和量化（INT8）的时候有用到。

2. 第三方库
   除了在 environment.yml 中提到的，还有些库放在 [3rd-party](resource/3rd-party) 需要手动安装。其中必须要安装的是 fairino, onnxruntime_gpu。安装 fairino 的时候注意架构，安装 onnxruntime_gpu 的时候注意版本。NYJSSYS 的同事们，**初号机**上下两块 Jetson 的环境我已经配好了，通过以下命令启动：
   ```
   conda activate fairino
   ```
3. ROS2 功能包的 resource 文件 
    将 resource.tar.gz 解压后放在 [resource](resource) 目录下即可，同步脚本会自动同步到 Jetson 上的目标文件夹中（参考1.2 部署脚本）

#### 1.2 部署脚本

1. [distclean](scripts/distclean) 
   清理 colcon 构建产物。
2. [sub_launch](scripts/sub_launch)
   底盘 Jetson 上节点一键启动。
3. [super_launch](scripts/super_launch)
   机械臂 Jetson 上节点一键启动
4. [sync](scripts/sync)
   将项目同步到指定 Jetson。例如：
   ```
   scripts/sync 192.168.0.100
   ```

## 2. 工具

都放在 [tools](src/tools) 目录中，用法参考源码。

1. [yolo_commander.py](src/tools/yolo_commander.py) 
   用于训练、量化、验证模型。
2. [record_camera_frame.py](src/tools/record_camera_frame.py)
   用于录制数据集。
> 其他的没什么用

## 3. 其他

#### 3.1 底盘导航的模型

之前分别尝试了 yolov8-seg 和 yolo26-seg 128轮（batch = 8）和 512轮（batch = 64），报告打包成了 runs.tar.gz，也能在[Google Drive](https://drive.google.com/drive/folders/1sn2bvBRu4CmVb2lKj7wDZh9eaKqxcOvn?usp=sharing)找到。

#### 3.2 项目配置

去看一下 [common_utils.py](src/watermelon_robot/src/utils/common_utils.py) 这个文件。这里实现了从文件中给每一个节点初始化时绑定配置项。默认配置文件在 [default.yaml](src/watermelon_robot/config/default.yaml)。

#### 3.3 节点结构

**初号机**的上下两块板各有一个 *logic_controller*，用来控制总体的逻辑。每一个 *logic_controller* 控制若干硬件控制器，例如 *super_logic_controller* 控制了一个 *robotic_arm_controller* 和 *robotic_arm_controller*。节点复用需要在[配置文件](src/watermelon_robot/config/default.yaml)中的 **_node_initializer** 一节中添加配置以及在 launch 文件中增加节点实例。

#### 3.4 有关二号机

代码应该是通用的，但是听说二号机只有一块板子了，所以 launch 文件需要重写，上下两个逻辑控制器也可以合并为一个。