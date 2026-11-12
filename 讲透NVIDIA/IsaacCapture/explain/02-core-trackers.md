# 02 追踪三轨（live / deviceio / replay）——同一抽象的三种数据来源

## 一、角色定位

四个 C++ 库分工（均在 `src/core/`）：`deviceio_base/`（11 头文件）纯接口层；`deviceio_trackers/`（22 文件）**公共 API 层**——tracker 标记类（8 手写 + 清单生成 16 个）与 pybind 绑定；`live_trackers/`（29 文件）**实况轨**（OpenXR 拉、可选写 MCAP）；`replay_trackers/`（21 文件）**回放轨**（MCAP 读）。核心设计：应用只持有公共层 tracker 对象（无状态标记），数据来源由会话层注入——同一个 `HeadTracker`，配 `DeviceIOSession` 是真头显，配 `ReplaySession` 是昨天的录制。**采集与回放是同一抽象的两种 impl**，"录制、回放调参、再上真机"零代码切换。

## 二、内部结构

### 2.1 抽象基座：三个接口

`ITrackerImpl`（`tracker.hpp:16`）只有 `update(int64_t monotonic_time_ns)`（L31）——每帧由会话线程驱动，抛异常即致命（L27-29）。`ITrackerSession`（L50）是解析入口，**身份契约**（L38-45）：按 tracker **对象地址**解析而非值相等——必须传注册进会话的同一实例，新建等价实例只会得到 "Tracker implementation not found"。`ITracker`（L60）只有 `get_name()`，纯标记接口，类型化访问器经 session 查 impl 转发；每类在 deviceio_base 有 `I*TrackerImpl` 抽象（如 `IHeadTrackerImpl`，`head_tracker_base.hpp:16`），live 与 replay 各实现一份。

### 2.2 公共 API 层：8 个手写类 + 16 个清单类

轮询位姿四类：`HeadTracker`（`head_tracker.hpp:13`，XR_VIEW 空间，`get_head(session)` 返回 `Serialized<HeadPose>`）、`HandTracker`（`hand_tracker.hpp:13`，左右手各一查询 L24-25）、`ControllerTracker`（`controller_tracker.hpp:15`，`apply_left/right_haptic_feedback` L52-58——**左右由调哪个方法表达，不是参数**）、`FullBodyTracker`（`full_body_tracker.hpp:23`，vendor 无关标记，24 关节 L27）。

事件流一类：`KeyboardTracker`（`keyboard_tracker.hpp:175`）是唯一"进程内设备"（不需 OpenXR 扩展）。心脏 `KeyboardInputState`（L54）：多 provider 各自上报、按 provider 隔离持有键，事件按"合并键盘"语义记录；每帧 drain，未排水上限 4096（L74），超限改发最小变更并 resync；键码以 evdev 为底座（L31）。

通道与推流配对三类：`MessageChannelTracker`（`message_channel_tracker.hpp:19`，UUID 通道、双向收发 L40-42、单消息 64KB L22）；`TensorPushTracker`（`tensor_push_tracker.hpp:16`）是通用**生产者**——不透明 payload 经 `XR_NVX1_push_tensor` 推成 tensor 样本，schema 归调用方；`HapticCommandReaderTracker`（`haptic_command_reader_tracker.hpp:23`）是配对**消费者**——按 `collection_id`/`endpoint` 分桶（L20-22、L43）。

清单生成 16 类：`trackers.toml` 16 条目注册 spacemouse/gamepad/pedal/tactile/soma 系列等；`defaults.toml` 占位模板（L7），pull/push 默认相反（L21-28）：pull 录制 MCAP 有通道列表，push（`trackers.toml:79-80`）默认不录制、类名后缀 PushTracker。**加简单拉取型设备只需一个 .fbs 加一行 TOML**。

### 2.3 Live 轨

`LiveDeviceIOFactory`（`live_deviceio_factory.hpp:55`）静态聚合所需 OpenXR 扩展（L68）并构造 impl（L73）。分发靠编译期表 `k_tracker_dispatch`（`live_deviceio_factory.cpp:154`）：每行一个 (类型, vendor) 对，`FullBodyTracker` 独占三行——`body.pico-xr`（L161）、Noitom、Xsens；清单生成行垫表尾（L172）。运行期 `create_tracker_impl`（L378-392）按 vendor 过滤、首个类型命中即建。vendor 是字符串 id 而非枚举（`tracker_vendor.hpp:25-30`）。

`LiveHeadTrackerImpl`（`live_head_tracker_impl.hpp:24`）的 `update()`（live_head_tracker_impl.cpp:44-91）：**先失效后发布**（L47-48）；VALID/TRACKED 两个 bit 分开存（L62-72：CloudXR 断连后可能仍留 VALID 位，分开才能区分占位姿态与活跃追踪）；发布走 `publish_and_record`（tracker_channels.hpp:183）——**编码恰好一次**，录制时 payload 嵌在 Record 字节里。拉取 tensor 的 impl 复用两层基座：`SchemaTrackerBase`（`schema_tracker_base.hpp:63`）封装 `XR_NVX1_tensor_data`（三时钟域时间戳 L75-84）；`SchemaTracker`（`schema_tracker.hpp:29`）加类型知识与落盘——**只有录制才解包 native**（L57-64，线上已是目标类型 adopt 零拷贝 L117-119）；积压样本逐个写 channel 0，最终样本再写 tracked 子通道（L107-113）。

### 2.4 Replay 轨与会话层

`ReplayDeviceIOFactory`（`replay_deviceio_factory.hpp:56`）构造注释是付过学费的：**每 tracker impl 开独立 `McapReader`**（L43-45）——FileReader 预取缓冲跨 chunk 失效，共享 reader 互相踩掉未消费指针；录制 schema 一次性校验（L47-52）；空文件名合法=纯 push-fed 会话（L53-54）。回放通道由 RecordingTraits 决定（`mcap/recording_traits.hpp`）：手写类同名单通道（L20）；清单类只回放 `%channel%_tracked` 最终样本（`defaults.toml:21-23`）。`ReplayHeadTrackerImpl` 的 `update()` 就是 `mcap_viewers_->read(0)`（replay_head_tracker_impl.cpp:41）；回放无视 vendor。会话层 `DeviceIOSession` 构造顺序即防御（deviceio_session.cpp:60-105）：**先 validate vendor 再开 MCAP writer**（L70-71）再建 live 工厂（L99）；`ReplaySession` 同构（replay_session.cpp:18）。

## 三、外部连接

上游：live 轨依赖 `oxr/`+`oxr_utils/`、`XR_NVX1_*` 头、`mcap/`、`schema/`；replay 轨只依赖 mcap 与 schema。下游：两会话类消费两工厂；`tracker_bindings.cpp`（L63 起 pybind11 块，清单类绑定也是生成的 L262-266）把全部 tracker 暴露给 Python——第 1 篇 `deviceio.HandTracker()` 即经此。横切：`codegen/` 读两个 TOML 生成五类 `.inc`（`live_deviceio_factory.hpp:44-46` 钉死清单 tracker 不得手加分发表行）。

## 四、数据流

**实况帧**：会话线程逐 impl 调 `update(monotonic_ns)`——轮询型查 OpenXR、tensor 型排干 collection、keyboard 型 drain 事件；样本编码一次，录制时落 MCAP（清单类双通道）。**查询相位**：`tracker.get_head(session)` 按地址查 impl 返回本帧快照（空句柄=设备不活跃）。**回放帧**：同节拍驱动 replay impl，数据源 `McapTrackerViewers::read`——每条消息先校验再**拷进自有缓冲**（tracker_channels.hpp:211-214：FileReader 缓冲只在下一次 read 前有效）。

## 五、设计决策

- **标记对象 + 注入 impl**：tracker 无状态无后端依赖——"同一 pipeline 录制/回放/实况三用"的根基，mock 一个 impl 即可测上层。
- **地址身份而非名字注册**：省掉注册表与名字冲突；代价是"必须传同一实例"成为文档化契约。
- **vendor 表驱动 + 字符串 id**：加后端=分发表加一行，tracker 类型不动。
- **双通道录制/单通道回放**：tensor 推流生产率可高于会话帧率，录制留全量子通道供离线分析，回放只消费 tracked 子通道——节奏与帧对齐不快进。
- **编码恰好一次 + 事件降级**：`publish_and_record` 录制与发布共享同一份字节；keyboard 4096 上限 + resync，实时性优先于完整性。

## 六、新人提示

1. **加设备先查清单**：flatbuffer 可表达、tensor 可拉取就走 trackers.toml+codegen 路线；只有需直接 OpenXR 调用或进程内状态才手写 impl。
2. **永远传注册过的 tracker 实例**给 session 方法；重建同配置对象查不到 impl。
3. **排查回放空白**先看录制通道名——手写类按 `recording_traits.hpp` 字面通道，清单类带 `_tracked` 后缀。
4. replay 工具保持"每 tracker 一个 reader"纪律——chunk 踩缓冲的坑工厂注释已付过学费。

## 源码实证勘误

1. **tracker 家族分类（任务书口径不完整）**：任务书列五类；源码实有 8 手写类（加 head/keyboard/tensor_push）+ 16 个 `trackers.toml` 清单类。
2. **文件数实测**：live 29 / deviceio_trackers 22 / replay 21（任务书 30/23/21 基本吻合）。
3. **手写与清单类通道策略不同**：双通道只作用于清单 tracker；手写类同名单通道、只写 channel 0（live_head_tracker_impl.cpp:89）。
4. **`schema_tracker.hpp` 属于 live_trackers**，归属目录易误记。
5. **回放无 vendor 维度**：live 的 FullBodyTracker 三个 vendor impl，replay 只有一个（`replay_deviceio_factory.hpp:68`）。

---
`路径约定`：`tracker.hpp` 在 deviceio_base/；`*_tracker.hpp` 在 deviceio_trackers/；live/replay impl 在 `src/core/{live,replay}_trackers/cpp/`；`tracker_channels.hpp`/`recording_traits.hpp` 在 mcap/。
`元数据`：chars=5207（不计空格）；anchors=31（file:line）；勘误=5。
