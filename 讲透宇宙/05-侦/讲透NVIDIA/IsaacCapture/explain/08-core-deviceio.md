# 08 · 设备 IO 基座与运行时粘合：tracker 家族、会话生命周期与插件生态

## 一、角色定位

`src/core` 是 IsaacCapture 的 C++ 基座：遥操作的一切输入（头/手/手柄/全身动捕/键盘/插件）从这层汇入，记录/回放在这层成形，日志经这层汇流。它也是运行时粘合——把 OpenXR、MCAP、spdlog、CloudXR、插件进程黏成可从 Python 驱动的整体。覆盖 deviceio_base(13)/deviceio_session(12)/pusherio(4)/python(16)/log_bridge(9)/plugin_manager(8)/oxr(6)/oxr_utils(8)/mcap(6)/cloudxr(2) 加 src/compat(4)；设备本体实现分家在 deviceio_trackers/live/replay_trackers 与 src/plugins。

## 二、内部结构

**tracker 家族——marker 与 impl 两分。** 根接口三层：`ITrackerImpl`（`tracker.hpp:16`）是每帧被更新的工人，唯一方法 `update(monotonic_time_ns)`（`tracker.hpp:31`），抛异常即致命；`ITrackerSession`（`tracker.hpp:50`）是查询接口；`ITracker`（`tracker.hpp:60`）是公共 API。关键契约是**按对象地址解析**：impl 表以 `const ITracker*` 为键，逻辑等价新实例不命中（`tracker.hpp:39`）。每类设备一个 impl 基类：`IHandTrackerImpl::get_left/right_hand()` 返回 `Serialized<HandPose>`（`hand_tracker_base.hpp:19`）；`IFullBodyTrackerImpl` vendor-agnostic，所有后端产出同一 `Serialized<FullBodyPose>`（`full_body_tracker_base.hpp:19`）。vendor 由 `TrackerVendor`（string id+参数 map）构造时选。typed 壳在 deviceio_trackers：`HandTracker`（`hand_tracker.hpp:13`）是轻 marker，`get_left_hand(session)` 查 impl。

**会话——live/replay 对偶。** `DeviceIOSession`（`deviceio_session.hpp:63`）静态工厂 `run(trackers, OpenXRSessionHandles, McapRecordingConfig, VendorConfig)`（`deviceio_session.hpp:74`）；`update()` 一把 tick 全部 impl，记录激活时 impl 直接写 MCAP。`McapRecordingConfig`（`deviceio_session.hpp:38`）用 (ITracker*, 通道名) 映射决定谁被录；`VendorConfig`（`deviceio_session.hpp:54`）按 tracker 选 vendor。mcap::McapWriter 前向声明避免消费者链接 mcap 库（`deviceio_session.hpp:22`）。`ReplaySession`（`replay_session.hpp:39`）是镜像，filename 可空=全 push 喂、不读录制（`replay_session.hpp:32`）。

**pusherio——FlatBuffer 走 NVIDIA 私有 XR 扩展。** `SchemaPusher`（`schema_pusher.hpp:88`）经 `XR_NVX1_push_tensor`+`XR_NVX1_tensor_data`（`:98`）把序列化数据推进 tensor collection；`push_buffer` 收双时间戳（系统单调钟+设备原始钟，`:131`），内部转 XrTime、读侧转回，两端 `DeviceDataTimestamp` 语义一致。

**python/py_utils——析构时序显式化。** `_deviceio_session` 模块（`deviceio_session/python/session_bindings.cpp:21`）先 import `_deviceio_trackers`；`PyDeviceIOSession`（`session.hpp:26`，deviceio_py_utils）存在的原因：直接绑定会把析构留给 pybind holder、落在 OpenXR 拆除之后产生 invalid-handle（`session.hpp:21`）——`close()` 在 `__exit__` 显式 reset。src/core/python 的 16 文件是打包基建。

**log_bridge——跨进程一根日志管道。** `isaaccapture::Logger`（`logger.hpp:18`）刻意不用 core:: 命名空间，logger 名镜像 Python 点分约定（`logger.hpp:15`）。插件进程用 `SocketForwardSink`（`socket_sink.hpp:29`）经 Unix domain socket 把记录送回 leader 的 logging_config，best-effort 丢行不阻塞（`socket_sink.hpp:24`）。

**plugin_manager——子进程监督器（非 dlopen）。** `PluginManager`（`plugin_manager.hpp:36`）在搜索路径发现带 plugin.yaml 的插件（manus 清单声明 name/command/devices，`src/plugins/manus/plugin.yaml:3` 起）；`Plugin`（`plugin.hpp:74`）= fork（`plugin.cpp:319`）+ execvp（`plugin.cpp:396`），stop 先 SIGINT 等默认 2 秒（`plugin.hpp:23`）再 SIGKILL；fork 与 exec 间只做 async-signal-safe 操作（`plugin.cpp:332`）。

**oxr/oxr_utils/mcap/compat。** `OpenXRSession`（`oxr_session.hpp:54`）是 headless 会话管理器；`OpenXRSessionHandles`（`oxr_session_handles.hpp:14`）只装 instance/session/space+`xrGetInstanceProcAddr`——消费模块不链接 OpenXR loader（`:13`）。mcap：`McapTrackerChannels`（`tracker_channels.hpp:49`）写通道时嵌入 .fbs 二进制 schema（`:60`）；读侧 `McapTrackerViewers`（`:225`）构造期做 schema_compat 校验；`publish_and_record`（`:183`）一次编码、记录+发布共用字节；通道名集中 `recording_traits.hpp:26`。cloudxr 两文件全是 CMakeLists——读版本、打包 CloudXR Runtime SDK，零源码。`isaacteleop.py` 是改名兼容层：MetaPathFinder 绑旧包名到同一模块对象（`isaacteleop.py:6`）。

## 三、外部连接

上游：OpenXR runtime（含 XR_NVX1 张量推送）、mcap/spdlog/CloudXR SDK、deps 的 FlatBuffers schema。下游：teleop_session_manager 直接实例化 PluginManager（`teleop_session.py:18`/`:1341`）；src/plugins 约 20 个插件以 plugin.yaml+可执行文件形态被监督；viz 经 `OpenXRSessionHandles` 共享同一 OpenXR 会话。

## 四、数据流

live 帧：OpenXRSession 建 headless 会话 → DeviceIOSession::run 造 impl → 每帧 update：native impl 读 XR 空间、tensor-push impl 从 tensor collection 收 FlatBuffer → `publish_and_record` 打成 Record、写 MCAP、把 payload 视图交还发布 → typed 查询按地址查 impl 返回 `Serialized<HandPose>`。replay 帧：ReplaySession 打开同一 MCAP，update 把下一样本喂给 impl——上层查询接口不变。插件路径：manus_hand_plugin 子进程用自己的 SchemaPusher 推数据入共享 OpenXR 会话，host 侧 live_tensor_push_tracker_impl 读出——进程隔离、数据面走 XR 扩展而非 IPC socket。

## 五、设计决策

- **marker/impl 两分+地址身份**：同一 tracker 类型可被 XR 硬件、插件张量、MCAP 回放三后端实现，上层 API 零改动；代价是必须持注册时的同一实例。
- **MCAP 自描述**：binary schema 随文件走+读端构造期强校验，不匹配的录制被拒绝而非静默误读。
- **进程隔离而非动态库**：插件独立进程崩溃不伤主进程，SIGINT→SIGKILL 有界停机；日志 socket 汇流保单一视角。
- **pybind 析构时序显式化**：C++ 对象与 OpenXR 会话的拆除顺序在 Python GC 下不可依赖，必须 context manager 显式 close。

## 六、新人提示

读码顺序：`tracker.hpp`（68 行讲完身份模型）→ `deviceio_session.hpp`（119 行）→ `tracker_channels.hpp` 的 publish_and_record 注释。排查"Tracker implementation not found"先查是否传了同一对象。写新设备：deviceio_base 加 impl 基类（新 schema 先在 src/core/schema/fbs 加 .fbs 并配 RecordingTraits）→ live/replay_trackers 各加实现 → deviceio_trackers 加 typed 壳。写插件：抄 manus 骨架，数据面用 SchemaPusher，日志别自己开文件。时间戳永远用单调钟域。新代码一律 `isaaccapture`。

## 源码实证勘误

①任务书"插件装载器 dlopen 机制"**有误**：grep 全 src/core 无任何 dlopen/dlsym；PluginManager 是 plugin.yaml 清单发现+fork/execvp 子进程监督器（`plugin.cpp:319/396` 实证），隔离靠进程边界。②"cloudxr(2)"属实但两文件均 CMakeLists.txt、零源码，职责仅打包 CloudXR Runtime SDK。③oxr_session_handles.hpp 实际属于 oxr_utils(8) 而非 oxr(6)（oxr 仅 oxr_session.hpp 一个头）。

---
chars(不含空格)=4782 anchors=36 勘误=3
