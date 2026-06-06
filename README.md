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
    现在同步脚本只会同步项目根目录下的 [weights-best](resource/weights-best) 目录了，需要在 Jetson上做量化，然后做一个软连接到功能包路径下的 resource 对应文件夹中。

#### 1.2 部署脚本

1. [launch](scripts/launch) 统一的启动配置入口，后面可跟多个启动项。例如
   ```
   scripts launch web sub
   ```
   就会启动 web.launch.py 和 sub.launch.py 两个启动项
2. [sync](scripts/sync)
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

之前分别尝试了 yolov8-seg 和 yolo26-seg 128轮（batch = 8）和 512轮（batch = 64），报告放在 runs 文件夹中，也能在 [Google Drive](https://drive.google.com/drive/folders/1sn2bvBRu4CmVb2lKj7wDZh9eaKqxcOvn?usp=sharing) 找到。

#### 3.2 项目配置

去看一下 [config_utils](src/watermelon_robot/src/watermelon_robot/utils/config_utils.py) 和 [node_utils.py](src/watermelon_robot/src/watermelon_robot/utils/node_utils.py) 这两个文件。这里实现了配置项与源码的解耦以及给每一个节点初始化时绑定配置项。默认配置文件在 [default.yaml](src/watermelon_robot/config/default.yaml)。

#### 3.3 节点结构

**初号机**的上下两块板各有一个 *logic_controller*，用来控制总体的逻辑。每一个 *logic_controller* 控制若干硬件控制器，例如 *super_logic_controller* 控制了一个 *robotic_arm_controller* 和 *robotic_arm_controller*。节点复用需要在[配置文件](src/watermelon_robot/config/default.yaml)中的 **_node_initializer** 一节中添加配置以及在 launch 文件中增加节点实例（参考 **3.2**）。

#### 3.4 有关二号机

代码是通用的，现在开启 [example.py](src/watermelon_robot/launch/example.py) 中所有的节点就行，不过后续肯定要优化逻辑和增加节点。

#### 3.5 有关节点自动装配机制

细节参考 [NodeUtils](src/watermelon_robot/src/watermelon_robot/utils/node_utils.py) 中的 *assemble_nodes()*， 简单来说就是在 ROS2 功能包的 [setup.py](src/watermelon_robot/setup.py) 中注册 *executable*，在[配置文件](src/watermelon_robot/config/default.yaml)中绑定这个节点名称和 *executable* （节点名称和  *executable* 是多对一的，也就是说一个 *executable* 可复用），最后在 [launch](src/watermelon_robot/launch) 中参照[示例](src/watermelon_robot/launch/example.py)写启动项配置就行。