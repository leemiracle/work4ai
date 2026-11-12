# 03 nvstreammux：流聚合器（batch 组装引擎与新一代 streammux2）

## 一、角色定位

`nvstreammux` 是每条 DeepStream 管线的第一个"汇合点"：N 路解码后的视频流各自进入 N 个 request sink pad，它把同一时间窗内的帧**组装成一个大 batch**（单个 `NvBufSurface`，`surfaceList[]` 按源排布 + `NvDsBatchMeta`），从唯一 src pad 推出。下游所有批处理元素（nvinfer/nvtracker/nvdsanalytics）都假设输入是这个格式——没有 muxer 就没有 DeepStream 的"多路单批"执行模型，GPU 一次前向吃 N 帧正是高吞吐的根基。

这个角色在 9.1 代码库里是**新旧两代并存**的格局，读代码前必须分清：

- **旧版（legacy）**：编译期链接 `libnvdsgst_multistream_legacy` 预编译库（gst-nvmultistream2/Makefile L50），源码不在仓库里。
- **新版（streammux2）**：核心逻辑全开源在 `src/utils/nvstreammux/`（4 个 .cpp，构建 `libnvds_streammux.so`），插件壳在 `src/gst-plugins/gst-nvmultistream2/`（同目录共存）。切换由**环境变量**控制——`gstnvmultistream.cpp` L38-39：`USE_NEW_NVSTREAMMUX=yes` 才注册新版 `nvstreammux`/`nvstreamdemux`；L58-66 的 `#if 0` 注释直说了演进方向："Disabling all static Gst APIs for loading streammux2 based on ENV var … TODO: Revert … when we are ready to drop legacy muxer"——legacy 正在退场，本篇以开源的新版为主线。

新版核心类 `NvStreamMux`（`src/utils/nvstreammux/include/nvstreammux.h` L39）的自我定位写在注释里（L34-37）："low level helper for core logic, this is **agnostic of gstreamer** or any other wrapper on higher level"——刻意不依赖 GStreamer，方便单测与复用；GStreamer 语义（pad、caps、event）在插件层的 `gstnvstreammux.cpp`（1878 行）与 `gstnvstreampad.cpp` 里翻译。

## 二、内部结构

**`src/utils/nvstreammux/` 四文件分工**：

- `nvstreammux.cpp`（915 行）：`NvStreamMux` 状态机。持有 pad 表 `inputs`（id → `SinkPad*`）、条件变量 `cv`、输出批 `batch`；`set_policy()`（L67-72）注入批策略。事件处理族 `handle_eos`/`handle_eos_cascaded`（L160/L171，级联 muxer 专用）/`handle_segment`/`handle_stream_reset`/`handle_flush_stop`（L180-203）覆盖源生命周期。`remove_pad`（L432 起）拆除源时先把队列排空再删——L438 的 `max_drain_wait_ms = 5000` 上限防卡死，注释明言"Mirror the legacy mux teardown order"。
- `nvstreammux_batch.cpp`（606 行）：`BatchPolicy` 批组装策略（下节数据流详述）。
- `nvstreammux_pads.cpp`（143 行）：`SinkPad`/`SourcePad` 封装（队列、EOS 状态、mimetype）。
- `MuxConfigParser.cpp`（421 行）：YAML 配置两组结构——`[property]` 组键名（L31-43）：`algorithm-type`（批方法）、`batch-size`、`adaptive-batching`、`enable-source-rate-control`、`max-fps-control`、`overall-max(min)-fps-n/-d`、`max-same-source-frames`；`[source-group-*]` 组（L25-31）：per-source 的 `max/min-fps-n/-d`、`priority`、`max-num-frames-per-batch`。`CHECK_ERROR` 宏（L46-56）在 DEBUG 版打印解析错误、静默回退默认值——配置写错不炸管线但行为可能悄悄变。

**批策略数据结构**（`include/nvstreammux_batch.h`）：

- `NvStreammuxBatchMethod` 三值（L45-49）：`NONE`/`ROUND_ROBIN`/`PRIORITY`。
- `BatchPolicyConfig`（L51-71）：批方法、adaptive_batching、批大小、总 fps 上下限、`max_same_source_frames`（单源在批内最大占比）、per-source 属性表。
- `BatchBufferWrapper`/`NvDsBatchBufferWrapper`（L92-135）：输出批抽象，`copy_buf()` 把输入帧写入 `NvBufSurface->surfaceList[]` 的指定槽位，`copy_meta()` 把每源 frame meta 挂进 `NvDsBatchMeta`——**帧数据的物理拼装点**。
- `LastBatchState`（L73-77）：记录上一批轮转到的优先级/源位置，round-robin 连续性的锚点。

**插件层**（`src/gst-plugins/gst-nvmultistream2/`）：

- `gstnvmultistream.cpp`（85 行）：plugin_init，新旧版注册开关。
- `gstnvstreammux.cpp`（1878 行）：新版 `nvstreammux` 元素本体——动态 request pad、caps 协商（NVMM/系统内存）、`config-file-path` 属性对接 MuxConfigParser。
- `gstnvstreammux_ntp.cpp`（383 行）：NTP 时间戳计算器（下详）。
- `gstnvstreamdemux.cpp`（1023 行）：镜像拆批，把 batch 还原成 N 路单流。
- `GstNvStreamMuxCtx`、`gstnvtimesynch.cpp`（190 行）：音频参数缓存（`SaveAudioParams` L26）与时间同步小件。

## 三、外部连接

- **上游**：任意视频解码器/源（`nvv4l2decoder`、`uridecodebin`、`nvarguscamerasrc`…），要求 caps 与 muxer 协商出的统一分辨率/格式一致（新版支持 per-pad 分辨率不同，转换在插件层做）。RTSP 源的 **RTCP SR 时间戳**通过 pad probe 传给 NTP 计算器对齐绝对时间。
- **下游**：`nvinfer`/`nvinferserver`/`nvtracker`/`nvdsanalytics`/`nvstreamdemux`。下游对 batch 的第一个动作几乎都是 `gst_buffer_get_nvds_batch_meta`——muxer 是 `NvDsBatchMeta` 的诞生地。
- **批元数据语义**：`frame_meta.pad_index` = 源 id（nvinferserver 的 `OPTION_NVDS_SREAM_IDS` 直接消费它）；`frame_num` per-source 递增，EOS 后可按 `frame_num_reset_on_eos`（nvstreammux.h L73-76）重置。
- **级联**：`handle_eos_cascaded` 证明 muxer 可以串 muxer（多级聚合，例如先按机器分组再全局聚合），事件语义专门为此处理。

## 四、数据流

核心是 `NvStreamMux::push_loop`（nvstreammux.cpp L304-416）——一个**批生命周期循环**：

1. **入队**：各 sink pad 收到 buffer，进 `SinkPad` 队列并 `notify_all()` 唤醒循环（`add_buffer()` 注释 L384-386 提到"could block on the downstream plugin's sink chain function"——所以推批前先解锁，否则下游背压会饿死输入）。
2. **组装**：`batch_policy.form_batch(batch, get_batch_size())`（L338）。`get_batch_size()`（nvstreammux_batch.cpp L318-328）在 adaptive_batching 下=**活跃源数×每帧 surface 数**（EOS 源剔除），否则=配置值——`adaptive-batching` 让批大小随源数伸缩。`form_batch`（L433 起）按 `BATCH_METHOD` 遍历优先级 multimap：PRIORITY 从高到低逐源取帧；ROUND_ROBIN 用 `last_batch_state`（L487-496）从上批断点继续转。每源取帧上限受 `update_with_source` 的 `max_same_source_frames`（`allowed_repeats`，L420 附近）钳制，防快源灌满整批。
3. **等待窗口**：`calculate_wait()`（nvstreammux_batch.cpp L158-187）由 overall-min-fps 反推批的最早推出时间（min_fps=5/1 → 本批最晚等 200ms，自 `last_batch_time` 起算）；`cv.wait_for(lck, wait_time)`（L347）睡眠等新帧。
4. **出批判定**：`is_ready()`（L212-217）= `acc_batch == batch_size`（凑满）；`is_ready_or_due()`（L219-234）= 凑满 **或** `calculate_delay()==0`（已过 min-fps 窗口）且 `acc_batch>0` 就强制推出——**凑不满也走**，这是慢源不拖垮快源的关键。
5. **拷贝与推出**：`copy_batch(out_buf, dest_batch_meta)`（L370，内部走 wrapper 的 `copy_buf/copy_meta` 拼帧与元数据）→ 若开 max-fps 控制且未到 min 时间窗则 `apply_throttle()`（L371-379，注意先解锁再节流）→ `update_last_batch_time()` → `push_batch()`（L389，此时锁已释放）。
6. **NTP 时间戳**（插件层，`gstnvstreammux_ntp.cpp`）：`gst_nvds_ntp_calculator_new`（L38 起）建每源计算器，两种模式 `SYSTEM_TIME`（挂系统钟）与 `RTCP`（用 RTSP 的 RTCP Sender Report 把 PTS 映射到绝对 NTP）。修正模式由 frame_duration 决定（L68-79）：`GST_CLOCK_TIME_NONE`→DISABLED、`0`→AUTOMATIC、给定值→USER_FRAME_RATE。**单调性修正**在 L186-192：新算出的 NTP 与上帧差 < 0.9×平均帧时长时，改用 `prev_ntp_ts + avg_frame_time` 外推——RTCP 包抖动不会产生时间倒流；L298-299 对超前 2 帧时长的异常打 WARNING。
7. **EOS/重置**：全 pad EOS → `all_pads_eos`（L300）→ 冲最后一批；单源 EOS 只把它从 adaptive 批大小分母里减掉（`num_sources_eos`，L324）。

## 五、设计决策

- **"凑满或超时"双条件出批**（`is_ready_or_due`）：纯粹凑满会因最慢源卡住（head-of-line blocking），纯粹超时浪费批容量。min-fps 窗口本质是给"批完整性 vs 延迟"之间画了一条由配置控制的线，且 `calculate_wait` 的 `running tight` 分支（L181）明示了负载过重时的降级行为。
- **GStreamer 无关核心 + 薄插件壳**：`NvStreamMux` 不 include 任何 gst 头（抽象注释 L34-37），事件用自定义 `EventWrapper`/`SINK_EVENT` 传递。代价是插件层要写一层翻译，收益是批策略可以脱离 GStreamer 单测（Makefile 里 `ENABLE_GST_NVSTREAMMUX_UNIT_TESTS` 条目佐证，gstnvmultistream.cpp L71-79）。
- **adaptive-batching 的语义选择**：批大小=当前活跃源数而非固定值。这与推理侧 `max_batch_size` 的耦合值得注意——源数波动时下游 nvinfer 的 engine batch 必须按最大源数建，否则 L1832 那种超限拒收会发生。
- **双 fps 控制（overall + per-source）分工**：overall-min/max-fps 定义**批节奏**（何时出批、何时节流），per-source `enable_source_rate_control` 的 `get_allowed()`（nvstreammux_batch.cpp L288-305）按 `经过时间×fps` 给每源发帧配额——前者管批、后者管源，快源想灌满 `max_same_source_frames` 也被配额挡住。
- **NTP 修正宁可外推不回退**：L186-192 的单调性钳制说明设计者把"时间戳不倒流"看得比"绝对精确"重——下游 tracker 的时间关联（消息里的 NTP 字段）对倒流零容忍。
- **新旧共存的发布策略**：环境变量开关 + 预编译 legacy 库，让 9.1 的用户一条 `export USE_NEW_NVSTREAMMUX=yes` 就能灰度切换，同时新版完全开源接受社区检视——典型的"替换型重构"的软着陆轨道。
- **`#if 0` 注释钉住的历史**：gstnvmultistream.cpp L58-66 那段被注释的 `GST_PLUGIN_DEFINE` 是迁移期标记——读懂它就明白为什么同目录有两套 pad 事件代码。

## 六、新人提示

1. **先确认你在看哪一代**：文档/博客大多还在讲旧版属性（`width/height/batched-push-timeout/live-source`）；新版配置走 YAML `config-file-path`（MuxConfigParser.cpp 的键名表），两者不通用。开 `USE_NEW_NVSTREAMMUX=yes` 前，先把配置迁到 `[property]`/`[source-group-*]` 结构。
2. **调试批行为开 debug**：`nvstreammux_batch.cpp` 全是 `debug_print`（受 `nvstreammux_debug.h` 控制），`form_batch`/`update_with_source` 的打印能直接看到每批每源取了几帧；比猜 `GST_DEBUG=nvstreammux:6` 更有针对性。
3. **源数 ≠ batch-size 时逐帧看 `get_batch_size`**：adaptive 模式下源掉线（EOS）批会缩，日志 `get_batch_size` 行（L325）打全参（inputs.size/num_sources_eos/adaptive_batching），排查"批怎么变小了"先看这里。
4. **延迟问题先量三个时间**：`calculate_wait` 的等待、`apply_throttle` 的节流、`push_batch` 的下游背压。慢的环节不同，调法完全不同：等待长→提 min-fps；节流多→提 max-fps；背压→查下游（多数是 nvinfer 的输出缓冲池不够）。
5. **NTP 对不上先查修正模式**：`frame-duration` 属性决定 DISABLED/AUTOMATIC/USER 三档（gstnvstreammux_ntp.cpp L68-79），配错档 RTCP 修正直接失效；`sync-inputs` 类时间同步问题也在这条线上排查，时间倒流已被钳制不会出现，出现的是外推漂移。
6. **删源用 request pad 释放而非只发 EOS**：`remove_pad` 有 5 秒 drain 窗（L438），源恢复时 pad id 语义要跟应用层 source id 对齐，否则 frame_meta.pad_index 错位、检测框串流。
7. **级联 muxer 是正路不是 hack**：`handle_eos_cascaded` 说明多级聚合是被一等地位支持的；跨机器聚合（`nvmultiurisrcbin`、分布式场景）下级联比单层巨 mux 更稳。

> 注：本篇行号基于 DeepStream 9.1 开源代码（`src/utils/nvstreammux/`、`src/gst-plugins/gst-nvmultistream2/`）核实。旧版（legacy）muxer 在本仓库无源码（预编译库），涉及其行为的描述均以新版源码与 Makefile 链接关系为据。
