# 06 插件群 II+III——动捕、SE3 追踪器、领队臂与通用输入

## 一、角色定位

覆盖 `src/plugins/` 剩余 12 插件，三群：**全身动捕**（xsens/noitom/sharpa_avatar）把动捕骨架变 `FullBodyPose`——xsens 收 MVN UDP、noitom 读 SDK 回调、sharpa 是"化身手套"；**SE3 追踪器双件**是 6-DoF 位姿复播器非动捕（见勘误）；**领队臂与通用输入**——rebot/so101_leader 是主从遥操作领队端（直读电机流 `JointStateOutput`），spacemouse/gamepad/方向盘/踏板桌面输入，oak 是 H.264 录制插件。共性：全遵循第 05 篇插件骨架，数据源换成动捕服/总线/HID/相机。

## 二、内部结构

### 2.1 xsens_full_body：UDP 协议 + 帧判决器

**teleop_wire.hpp**：MVN "Isaac Teleop" 预设的 XTLP 线协议（`teleop_wire.hpp:6-24` 即协议表）——每报文一帧，小端头+裸 FlatBuffer。逐字段手解不用 packed struct：**线序固定小端，大端主机上 struct 静默错位**。

**frame_decision.hpp/.cpp**：把"数据报该怎么办"抽成纯函数 `FrameDecider::classify`——判决枚举（`frame_decision.hpp:28`）Deliver/Malformed/Oversize/Unverified/Stale，事件标志与判决**正交**。拆分动机在头注释：插件持有 socket/session，无运行时无法单测。细节：`SESSION_RESYNC_AFTER=30`（60Hz 半秒）；`last_seq_` 存"最后通过的 seq"而非"期望的下一个"（duplicate-seq-0 根源）。判决顺序承重：校验器先于状态变更——恶意 payload 推不动流。

**xsens_full_body_plugin.cpp**：构造"先 session 后 socket"；恢复双梯子——socket 重绑 ~2.3s、session 重建 ~23.5s；退避 50ms 片睡（`main.cpp:20`：atomic 而非 `volatile sig_atomic_t`）。测试后门 `XSENS_TELEOP_INJECT_RECV_ERRORS` 注错。

### 2.2 noitom 与 sharpa

noitom：SDK 回调 → `FullBodyPose`。**单位纪律**：显式把 SDK 配置成厘米再乘 `SDK_CENTIMETERS_TO_METERS = 0.01f`（`noitom_mocap_plugin.cpp:31`），日志直打 "sdk_units=centimeters, output_units=meters"。

sharpa_avatar：manus 同构三件套+`DeviceDataCategory` 双类别（`avatar_hand_tracking_plugin.hpp:36-40`）。README 警告：**别同时跑 avatar-backend 或 Avatar Desktop**（USB 争用）。清单是 `plugin.yaml.in` 模板，五者唯一。

### 2.3 SE3 追踪器

controller_se3_tracker（110 行）：XR 手柄 grip pose 重发为通用 SE3 collection。wire 汇合参数**从 `core::Se3Tracker` 门面取**（`controller_se3_tracker_plugin.cpp:40-46`：唯一真相源，错配静默无数据）；无效帧也推——单位位姿+`is_valid=false`（显式无效优于沉默）。

vive_se3_tracker：每个 Ultimate Tracker 一条 `vive_tracker_<serial>` collection。**collection 名第一帧定格不可改名**（数据线只在姿态包带序列号）；广告文件（每用户目录而非 /tmp）供 `record_se3_vive.py` 用。README：姿态按 VIVEHub 原点**原样转发**非 OpenXR base space——跨设备对齐下游做。

### 2.4 领队臂

**so101_leader**：6 个 FEETECH STS3215。`FeetechBus` 裸实现 SMS/STS 协议（无 SDK），子集：失力矩（可 back-drive）+ **单条 SYNC READ 读全部六舵机**（`so101_leader_plugin.cpp:271-274`：一次往返而非六次）+ LeRobot 同形校准。

**rebot_devarm_leader**：`/dev/ttyACM*` 走 Damiao（USB-CDC 转 CAN）、`can0` 走 RobStride，零 SDK 裸实现。Damiao 反馈是定点数（16 位位置/12 位速度，按 `kModelLimits` 解码）。**多圈编码器回绕防御**：多圈计数器掉电即失，行程超一圈的夹爪醒来读到"物理位置+2πk"（B601-DM 实测：物理闭合夹爪读 +6.227rad = -0.056 + 2π）；窗外读数判回绕，`valid=false` 流出——否则从动机器人 t=0 就撞软限位。

### 2.5 通用输入与 oak

**spacemouse**：`hid_report.cpp` HID 范本：report ID 1/2/3 分发，除 `kFullDeflectionCounts=350` 归一。**gamepad**：SDL3，`SDL_HINT_NO_SIGNAL_HANDLERS`（禁截胡）与 `SDL_HINT_JOYSTICK_ALLOW_BACKGROUND_EVENTS`（后台读垫，`gamepad_connection.cpp:39-41`）定生死。**steering_wheel/pedal**：孪生，都读 joystick 除 32767 归一；差异只在 schema（`generic_3axis_pedal_plugin.cpp:140-142`）。**oak**：DepthAI 管线（`oak_camera.cpp:91`）每路流 H.264 硬编码；`FrameSink` 永远写裸 H.264（`rawdata_writer.hpp:19` "without container"），元数据互斥双通道 OpenXR/MCAP。

## 三、外部连接

上游：MVN Studio、Noitom/Sharpa SDK、VIVEHub（`/tmp/vut.sock`）、Damiao/RobStride/FEETECH、SDL3、OAK。下游统一 `SchemaPusher` collection：动捕→`FullBodyTracker`；SE3→`Se3Tracker(collection_id)`；leader→`JointStateTracker`。

## 四、数据流

```
MVN Studio --UDP/XTLP--> FrameDecider::classify → SchemaPusher::push_buffer
宿主: FullBodyTracker → FullBodySource → FullBodyRetargeter
丢帧: Dropped 计数每 250 帧一行(main.cpp:108)；断链: socket 梯子(2.3s)→session 梯子(23.5s)
```

leader 对照：90Hz → `read_hardware`（Damiao 轮询 5ms 窗；FEETECH 单条 SYNC READ）→ 校准归一 → `JointStateOutputT`（device_id=collection_id，`so101_leader_plugin.cpp:291-292`）→ pusher；宿主 `JointStateSource` 自动发现。

## 五、设计决策

1. **判决与 I/O 分离是 xsens 的可测性引擎**：FrameDecider 存在理由在头注释——分支错误 "look entirely plausible"，不拆就没有测试；对照 noitom（单文件直推）是刻意投入。
2. **身份与汇合约定的两种解法**：vive 用"第一帧定格+广告文件"、controller 用"门面取 wire 参数"——都把"约定漂移"从运行期静默失败挪进结构。
3. **leader 只读不写 + 前端归一化**：电机只收失力矩帧可 back-drive、之后纯读（安全、控制权留给从端）；轴值在插件内归一到 [-1,1]；oak 视频落裸 H.264、元数据互斥双通道——避免双写漂移。

## 六、新人提示

- 读序：controller_se3_tracker → so101_leader → spacemouse → xsens → vive → rebot_devarm → oak。
- 调 xsens 先跑 `tests/test_frame_decision.cpp`（无运行时毫秒级）；MVN 选 "Isaac Teleop"（9764 对齐 plugin.yaml）。
- vive collection 名=序列号，先 `ls` 广告文件。
- leader 带电机先空载：rebot 夹爪 out_of_travel 先归零再上电（回绕掉电必然）；改型号须同步改 `kModelLimits`——表错则解码错位且无异常。
- oak 首次构建 `rm -rf build`（TOOLCHAIN 只首次 configure 生效）；.h264 无容器。

## 源码实证勘误

1. **SE3 追踪器归入"动捕全身"群不准确**：controller/vive_se3_tracker 不产出 FullBodyPose，是单 6-DoF 复播器（`se3_tracker.fbs` schema）；全身动捕只有 xsens/noitom（sharpa 是手部+化身）。
2. **oak 的 plugin.yaml 描述失实**：写 "OAK camera plugin with CloudXR streaming and MP4 recording"，源码实为裸 H.264 录制（`rawdata_writer.hpp:19` "without container"）+ 元数据二选一——无 MP4 容器、无视频 CloudXR 流（仅元数据进 OpenXR）。
3. **sharpa_avatar 文件数**：任务书称 14，实测 15（含 .gitignore；清单是 `plugin.yaml.in` 模板）。
4. **"rebot_devarm_leader(10)/so101_leader(8)" 数对但注意**：两者都含双后端（硬件+synthetic），"主从臂领队端模式"实为"失力矩+只读反馈"被动件——不做运动控制。
5. **noitom 单位换算方向**：README 只说 "Positions are read from the SDK in centimeters and published in meters"，源码是**主动把 SDK 配置成厘米输出**（`noitom_mocap_plugin.cpp:263` "failed to configure SDK position units to centimeters"）再乘 0.01——非被动适配，失败即抛错。

---
`路径约定`：锚相对 `src/plugins/<插件名>/`（如 `frame_decision.hpp:28` 即 `xsens_full_body/` 下）。
`元数据`：chars=4750（不计空格，重校含本行）；anchors=14（file:line）；勘误=5。
