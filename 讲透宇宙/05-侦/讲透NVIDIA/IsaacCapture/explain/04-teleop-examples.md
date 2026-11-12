# 04 teleop 双示例——零 ROS 脚本集与完整 ROS2 参考应用

## 一、角色定位

`examples/teleop/` 与 `examples/teleop_ros2/` 是同一 teleop 栈的两种交付姿势："把 IsaacCapture 接到机器人上，第一步怎么写？"

- **`teleop/python/`（零 ROS）**：14 个独立脚本 + 共享循环模块，各演示一种"源节点 → retargeter → 会话"组合，进程内直调 `isaaccapture` API，也是活文档（`joint_space_device_example.py:6` 自称 API reference + end-to-end test）。
- **`teleop_ros2/`**：可部署 ROS2 节点（rclpy）+ 接口包 + C++ 集成测试 + Dockerfile，把 TeleopSession 输出翻译成 ROS2 话题（`xr_teleop/*`）与 TF。

分工：teleop 教**组成流水线**，teleop_ros2 教**产品化**（参数化/话题化/容器化/重连）。

## 二、内部结构

### 2.1 示例集：14 脚本能力矩阵

按"源 → 重定向目标"六类：

| 类别 | 代表 | 内容 |
|---|---|---|
| SE3 末端 | se3_retargeting | Hands/Controllers→Se3Abs/Rel |
| 灵巧手 | dex_bimanual | 双手→DexBiManual+Reorderer |
| 夹爪 | gripper_retargeting | 捏合→GripperRetargeter |
| 通用输入 | spacemouse_printer | HID/SDL/键盘→printer+retargeter |
| 底盘运动 | locomotion_retargeting | VR 手柄/脚踏→Locomotion/FootPedal |
| 关节空间 | joint_space_device | SO-101 领队臂→JointStateRetargeter |

精讲样本：

**se3_retargeting_example.py**——最小闭环三行：构造源、`Se3RetargeterConfig(...)`（`se3_retargeting_example.py:50`）、`retargeter.connect({...})`（`se3_retargeting_example.py:58`）。connect 入参是"输入名→OutputSelector"字典，返回可交 TeleopSessionConfig 的子图；绝对（捏合中心）/相对（增量）两口径。

**spacemouse_printer_example.py**——插件系统最短演示：TeleopSessionConfig 内联 `PluginConfig(...)`（`spacemouse_printer_example.py:58`），`BUNDLED_PLUGINS_DIR` 自 teleop_session_manager 导入（`spacemouse_printer_example.py:24`），会话启动自动拉起插件子进程；按钮按下/抬起沿单独打行（`spacemouse_printer_example.py:95-98`）。

**joint_space_device_example.py**——最复杂，docstring 画出通路（`joint_space_device_example.py:9`）：JointStateOutput→Source→Retargeter→TensorReorderer→OutputCombiner("action")。硬编码 SO-101 关节名（`joint_space_device_example.py:51`）；`--mode ee` 走 URDF 前向运动学；`--launch-plugin` 以 `subprocess.Popen` 拉起插件（`joint_space_device_example.py:224`）；结尾"流活性"断言——多帧 `np.allclose` 全等判陈旧保持流并 FAILED。

### 2.2 `_example_loop.py`：共享循环

`run_example_loop`（`_example_loop.py:29`）：单调钟 deadline 循环、60 FPS 节流（`_example_loop.py:44`）、KeyboardInterrupt 在会话上下文内捕获让 with 块清理。

### 2.3 teleop_ros2：参考应用分层

11 模块：`teleop_ros2_node.py`（唯一 ROS 节点，8 publisher+TF（`teleop_ros2_node.py:104`））；`node_parameters.py`（683 行最大，`NodeParameters`（`node_parameters.py:64`））；`teleop_profiles.py`（**模式→发布行为静态编译层**：`PublishType` 8 能力（`teleop_profiles.py:21`）、`TeleopProfile` 7 档（`teleop_profiles.py:32`）→运行期按 spec 校验每帧）；`session_config.py`（参数→SessionConfig，按 mode 组装链，`OutputCombiner`（`session_config.py:162`）合并输出）；`messages.py`（高维数据 msgpack 进 ByteMultiArray（`messages.py:165`））；`teleop_ros2_retargeters/`（应用层小件：关节名重排/追踪丢失置 none）+geometry 等辅助件。

接口包仅一条自定义消息（`msg/NamedPoseArray.msg:5-8`）：Header+name[]+Pose[]+is_valid[]，is_valid 对应引擎 Optional 语义。

## 三、外部连接

共享内核：teleop_session_manager、retargeters（30+）、deviceio_source_nodes、cloudxr（CloudXRLauncher）。边界不同：teleop 示例是**进程与插件**——spacemouse 拉内置插件、joint_space 拉起 so101_leader 进程靠 collection_id 会合，不 import ROS；teleop_ros2 是**ROS 图**——上游同一 TeleopSession+CloudXR，下游 rclpy/tf2_ros，`TELEOP_CLIENT_ROUTE_ENV` 透传客户端路由（`teleop_ros2_node.py:312`）。

## 四、数据流

每帧主循环（`teleop_ros2_node.py:235-287`）：

```
CloudXR/OpenXR runtime（插件注入 tensor collection）
  → TeleopSession.step() → validate_session_result
    → PublishType 分流：EE→NamedPoseArray+TF；ROOT→Twist/PoseStamped；
      FINGER_JOINTS→JointState；PAYLOAD→msgpack ByteMultiArray
  → rclpy.spin_once(0.0) → sleep(sleep_period_s)
```

三细节：**手动 spin**——逐帧 `spin_once(0.0)`（`teleop_ros2_node.py:251`），时间戳跟 /clock 且单线程无竞争；**无客户端重试**——"no HMD" 特判可重试、sleep 2s 重开会话（`teleop_ros2_node.py:289-297`）；**健康巡检**——外层每会话前、内层每帧前 `health_check()` 双检。

## 五、设计决策

1. **两种集成姿势并存是本目录存在的理由**：进程内 API 零序列化开销适合研究仿真；ROS2 话题牺牲一跳延迟换生态互操作。
2. **能力矩阵而非场景矩阵**：按"输入设备 × 重定向算子"正交组织——`gamepad_printer_example.py:9-10` 点破：同一 gamepad 源同时喂 Se3Rel/Se2/Gripper 三个 retargeter。
3. **Profile 是编译期决策**：构造时解析成不可变 spec，运行期零分支——切模式即重启节点；三变体只差一标志（`teleop_profiles.py:119` 用 `dataclasses.replace` 派生）。
4. **msgpack 而非 ROS 数组**：高维数据保结构、省带宽，代价是消费端也要 msgpack。
5. **示例失败也要可观测**：joint_space 验"收到活的数据"，spacemouse 记按钮沿——断言习惯与 CI 同构。

## 六、新人提示

- 入门顺序：`gripper_retargeting_example_simple.py`（119 行）→ se3 → gamepad_printer → joint_space。
- **每个 TeleopSession 都开 OpenXR 会话**（`spacemouse_printer_example.py:13-14`）——CloudXR runtime 是 tensor transport 载体，不需头显但要活着。
- 键盘两路径：printer 开 GLFW 窗口（焦点才计键）；terminal 零窗口可 SSH（`keyboard_terminal_example.py:11`：须 kitty keyboard protocol 才上报 release）。
- 先装 udev 规则（spacemouse 插件的 install_udev_rules.sh）；`hand_retargeter:=dexpilot` 需 Sharpa Wave URDF 构建期备好。
- 复用：大概率只改 node_parameters.py 关节名默认 + session_config.py 的 retargeter 选择。

## 源码实证勘误

1. **teleop_ros2 文件数**：任务书称 37，实测 32（含 .gitignore 等非代码）；代码主体 = 11 模块 + retargeters 子包 3 文件。
2. **"14 个独立脚本"成立但需口径**：不含 `_example_loop.py` 与 config/；CMakeLists 只做 `install_python_example`，无编译目标。
3. **"零插件依赖"不准确**：spacemouse/joint_space 隐式依赖插件子进程，"零"的是 ROS 依赖；无硬件靠插件 synthetic 后端兜底，仍需插件二进制先构建。
4. **gamepad 三 retargeter 并非对等**：EE 增量（GamepadToSe3Rel）需 `retargeters-lite` 的 scipy，Se2 与夹爪无——缺一不整体失败但对应输出键缺席。

---
`路径约定`：teleop 锚相对 `examples/teleop/python/`；teleop_ros2 锚相对 `examples/teleop_ros2/`（模块在该目录 `python/isaaccapture_examples/teleop_ros2/` 下）。
`元数据`：chars=4714（不计空格）；anchors=26（file:line 26）；勘误=4。
