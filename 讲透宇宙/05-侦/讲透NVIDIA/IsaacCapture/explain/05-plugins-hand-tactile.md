# 05 插件群 I——手部与触觉：契约、四手套与合成手

## 一、角色定位

IsaacCapture 设备接入是**进程级插件**架构：每硬件一条 plugin.yaml 清单 + 独立可执行文件，宿主 `PluginManager` 以子进程拉起，数据经 OpenXR（CloudXR）回流。`src/plugins/` 手部与触觉群：`manus/`（16 文件：注入+flex 外推+触觉回环）；`wuji_glove/`（21→26 关节重排）；`oglo_tactile/`（BLE 直连 80 taxel，纯录制）；`haptikos/`（外骨骼直读指关节）；`controller_synthetic_hands/`（**无硬件源**——扳机合成"握拳程度"受控的手）；`plugin_utils/` 公共件；`sensing/` 见勘误——不是插件。

共性使命：把"手上硬件"翻译成**注入的 hand tracking 关节流**或 **SchemaPusher collection**，外加触觉通道。

## 二、内部结构

### 2.1 契约：plugin.hpp 是进程包装器非接口类

`core::Plugin`（`plugin.hpp:86`）**没有任何虚函数**——宿主侧子进程 RAII 包装器：构造即 fork/exec，`stop()` 发 SIGINT 等待（`plugin.hpp:23` 超时 2.0s 升级 SIGKILL）、`check_health()` 探活、崩溃抛 `PluginCrashException`。真正的"生命周期契约"是三件套：**plugin.yaml（声明）+ main.cpp 信号循环（存活）+ OpenXR session（数据）**。`PluginManager`（`plugin_manager.hpp:43`）扫清单发现插件，`devices` 条目仅 UI 路由元数据。插件骨架一律：main.cpp 注册 SIGINT/SIGTERM（manus `app/main.cpp:21` `static_assert(ATOMIC_BOOL_LOCK_FREE == 2)` 保信号安全）→ 循环到 stop。

### 2.2 manus：三数据集开关 + 单例 Tracker

`--datasets=human,sensors,haptic`（`manus_hand_tracking_plugin.hpp:47`）切三路：human 注入 26 关节 / sensors 推 flex 到 `manus_sensors_*`（`manus_glove_collection.hpp:40`）/ haptic 收反向命令。`ManusTracker` 显式单例（`manus_hand_tracking_plugin.hpp:63`；C 静态回调需全局锚点）。每帧 `update()`（`manus_hand_tracking_plugin.cpp:137`）：状态发布 → 触觉命令消费（**按 left/right 端点分别读**——两手指令在同一 collection，单样本读取后到者覆盖前一只）→ 传感器外推 → 手部注入。触觉五电机（`manus_hand_tracking_plugin.hpp:44`：SDK API 就是 powers[5]）。腕位姿优先 xdev 原生手追（`manus_hand_tracking_plugin.cpp:432`），退回控制器 aim pose。

### 2.3 wuji_glove：坐标系考古学

SDK 给 21 关节（MediaPipe 序），OpenXR 要 26 槽——`kMpToXr[21]`（`wuji_glove_plugin.cpp:35`）映射，5 个独有槽留空清 VALID 位。表上方注释是全插件最有份量的一句：**"KEEP IN SYNC with the Python table OPENXR_TO_MEDIAPIPE_INDICES in wuji_hand_retargeter.py — a silent divergence is a joint-permutation bug nothing catches at runtime"**——两表互为镜像，无编译期约束，只能靠纪律。

基变换 `remap_to_openxr_basis`：URDF FK 基与 OpenXR 基差绕 Z 180°，共轭即位置与四元数 x、y 同取反（四行），constexpr 自测 + `static_assert` 编译期验证。

### 2.4 oglo_tactile：BLE 流水线与时间学

不注入手部姿态，只录制触觉：`OgloBleClient`（抽象传输，`ble/oglo_ble_client.hpp:35`；bluez 唯一后端，换 BLE 库是 licensing decision）→ 解析 → 队列 → `IGloveSink`（`oglo_glove_sink.hpp:22`）。**必须先读 config 再订阅**：每手几何（5 指×16=`kNumTaxels=80`，`oglo_packet_parser.hpp:21`）与采样率、封包格式都来自设备 JSON manifest。32 位微秒计数器约 71.6 分钟回绕——`extend_device_ns`（`oglo_tactile_plugin.cpp:35`）提升为单调 64 位纳秒。两板斧：**停滞看门狗**（超时重连，sink 不重建——"Recording continues into the same sink"）；**停机排水**。

### 2.5 haptikos、synthetic_hands 与 plugin_utils

haptikos 最薄：外骨骼直读指关节，腕用控制器 aim pose 硬编码偏移 `wrist_offest=Vector3(0,-0.05f,-0.06f)`（`haptikos_hands_plugin.cpp:167`）；`static_assert(XR_HAND_JOINT_COUNT_EXT == HAPTIKOS_NUM_OF_JOINTS)` 编译期对齐关节数——无重排表。synthetic_hands 的 worker（`synthetic_hands_plugin.cpp:58`）是"无硬件手部数据源"标准答案：读手柄 `trigger_value()` 当握拳目标平滑趋近（`CURL_SPEED = 5.0`），`HandGenerator::generate`（`hand_generator.hpp:21`）按 curl 生成 26 关节；注释明言在位是注入前提，"a different plugin could choose a different policy"——同一套 HandInjector，两种存在性语义。`HandInjector`（`hand_injector.hpp:24`）封装 NVIDIA 私有扩展 `XR_NVX1_device_interface`：一实例一手，**析构即置 isActive=false**——各插件"丢控制器就 reset 注入器"的原因。`PluginDeviceStatusPublisher`（`plugin_device_status_publisher.hpp:32-34`）定义心跳：1s 心跳、3s 陈旧超时、变化即推。

## 三、外部连接

上游：各自 SDK（ManusSDK；wuji_sdk；OGLO 无 SDK——协议裸实现；Haptikos）。下游汇入 OpenXR/CloudXR：HandInjector（XR_NVX1）→ 宿主 HandTracker → Python HandsSource；SchemaPusher → 对应 tracker；触觉命令反向。

## 四、数据流

manus 单帧：

```
SDK 回调 → 缓存 → update(): 心跳 → 读 left/right 触觉命令 → VibrateFingers
  → flex → SchemaPusher → manus_sensors_{l,r} → HandInjector.push
宿主: HandTracker → TeleopSession → HandsSource
```

## 五、设计决策

1. **进程隔离换故障域隔离**：SDK 崩溃只死插件进程，宿主可重启；代价是每插件重复"信号+OpenXR+日志"骨架、不共享代码——接受重复换自包含。
2. **注入 vs 推流二分**：retargeting 主链路走 HandInjector（"runtime 眼里的手追"），旁路走 SchemaPusher collection。manus 两路都走；oglo 只走后者；wuji/haptikos 只走前者。合成手是 CI 资产——与 leader 臂 synthetic 后端构成"无硬件路径"。
3. **时间戳分层**：注入用 OpenXR 时钟、collection 双时钟（local common + raw device）、OGLO 加回绕——三插件三种时间学。

## 六、新人提示

- 读序：synthetic_hands → haptikos → wuji → manus → oglo，复杂度递增；先读 `plugin.hpp`/`plugin_manager.hpp` 建宿主视角。
- plugin.yaml 的 `command` 是相对 working_dir 的路径（`"./manus_hand_plugin"`，`plugin.yaml:6`）——布局错了报的是进程启动失败而非清单错误。
- 调手套先看状态心跳（3 秒陈旧阈值）：在线但没数据，问题在数据链路不在连接；wuji 改关节表**必须**同步动 Python 侧，否则是无感知的关节置换 bug。
- oglo config 未读即订阅症状是 taxel 全错而非报错；manus `--datasets` 传空串可纯监视。

## 源码实证勘误

1. **`sensing/` 不是插件**：任务书列入插件群（11 文件），实测全是 scripts/docker/configs/README——`sensing/README.md:6` 自定位 "SENSING GMSL cameras...uses NVIDIA SIPL"，无 plugin.yaml/可执行插件/C++ 源码。
2. **plugin.hpp 无"生命周期契约接口"**：任务书预期该契约，实际 `core::Plugin` 是子进程 RAII 包装器（无虚函数/on_start/on_stop 钩子）；契约由 plugin.yaml+信号循环+OpenXR session 事实构成。
3. **manus 文件数 16 对但含非源码**（.gitignore/CMakePresets 等）；核心是 core/ 3 个 C++ 文件（hpp 204 + cpp 1416 行 + collection hpp），tools/ 是调试器。
4. **wuji_glove 文件数**：任务书称 7，实测 8（含 .gitignore；主体 wuji_glove_plugin.{hpp,cpp} 635 行 + wuji_glove.cpp 75 行）。
5. **oglo "BLE 客户端在 ble/ 子目录"属实**，但 `oglo_ble_client.cpp`（28 行）只是工厂桩，真实现是 `oglo_ble_client_bluez.cpp`（611 行，libdbus）——按文件名找主实现会找错。

---
`路径约定`：锚相对仓库根（如 `manus_hand_tracking_plugin.hpp:44` 即 `src/plugins/manus/core/inc/manus/` 下同名文件）；`plugin.hpp*` 在 `src/core/plugin_manager/` 下。
`元数据`：chars=4749（不计空格）；anchors=21（file:line，唯一）；勘误=5。
