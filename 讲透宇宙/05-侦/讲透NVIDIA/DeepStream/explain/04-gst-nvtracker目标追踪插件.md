# 04 gst-nvtracker：目标追踪插件（NvMOT 框架与调度层）

## 一、角色定位

`gst-nvtracker` 给检测框赋"时间身份"。上游 nvinfer 每帧独立吐出一堆框，框与框之间没有关联；nvtracker 接手后为每个目标维护跨帧的唯一 `trackingId`，把"第 37 帧的行人"和"第 38 帧的行人"接成一条轨迹。下游一切时序智能——越线计数、方向判断、徘徊检测、轨迹回溯——全部建立在 trackingId 的连续性上。检测器可以 `interval` 跳帧（第 1 篇），跳帧期间的框也由 tracker 补齐，这是省算力不丢功能的支柱。

这个插件最重要的架构事实：**它自己不做跟踪算法**。真正的跟踪器（NvDCF、IOU、NvSORT、DeepSORT 等）是独立的"低层库"（low-level library），以 `ll-lib-file` 属性 dlopen 进来；本目录代码是**调度与编排层**——负责帧格式转换、线程模型、批/源生命周期管理、元数据双向翻译。C ABI 契约在 `includes/nvdstracker.h`：六个 `NvMOT_*` 函数族 + 一组纯 C 结构体。低层库多为 NVIDIA 二进制发布（源码仓里只有 `src/utils/nvmultiobjecttracker/model/tracker_ReID` 的 ReID 模型资产），但契约是开放的——任何人可以写自己的跟踪库插进来。

目录 10 个文件三层：GStreamer 壳（`gstnvtracker.cpp` 1040 行）、编排核心（`nvtracker_proc.cpp` 3205 行 + `nvtracker_proc.h` 387 行）、两个缓冲管理器（`convbufmanager.cpp` 290 行、`miscdatabufmanager.cpp` 411 行）。

## 二、内部结构

**GStreamer 壳**（gstnvtracker.cpp）：

- 关键属性：`ll-lib-file`（L446，低层库路径）、`display-tracking-id`（L462）、`input-tensor-meta`（L474）+ `tensor-meta-gie-id`（L479，直接吃上游 nvdspreprocess 的张量做 ReID 特征，跳过图像转换）、`sub-batches`（L493-497，两种写法：源 id 列表分号分隔，或子批尺寸冒号分隔）、`sub-batch-err-recovery-trial-cnt`（L502-504，低层库失败重试次数，-1 无限）。
- 主数据路径在 L888/L905：`trackerIface->submitInput(input)` 提交后 `waitForCompletion(inputParams)` 等待——插件在 transform 里同步等待批处理完成。

**编排核心 `NvTrackerProc`**（nvtracker_proc.h L35- / nvtracker_proc.cpp）：

- 对上接口（nvtracker_proc.h L42-66）：`init/addSource/removeSource/resetSource/submitInput/waitForCompletion/flushReqs/updateDynamicConfig`——GStreamer 侧只见这八个动词。
- **低层库装载** `initTrackerLib`（nvtracker_proc.cpp L986-1049）：`dlopen(RTLD_NOW | RTLD_NODELETE)`（L992），随后 dlsym 一组符号。**必需**三个：`NvMOT_Init`/`NvMOT_DeInit`/`NvMOT_Process`（L1002-1021，缺一即失败）；**可选**四个：`NvMOT_RetrieveMiscData`（L1023，历史帧数据回溯）、`NvMOT_RemoveStreams`（L1029，源删除）、`NvMOT_UpdateParams`（L1035，运行时改配置）、`NvMOT_Query`（L1042，能力协商，缺省"Using default parameters"）——可选符号缺失只 LOG_INFO，功能降级不致命，这是 C ABI 演进留的余地。
- **线程模型**：`init` 起主处理线程 `m_ProcessBatchThread`（L359）；若配置了 `sub-batches`，每个子批再起独立线程 `processSubBatch`（L411/L438）并持有**独立 `NvMOTContextHandle`**——不同组源可并行跑不同的跟踪上下文（甚至不同的库配置）。
- **id 体系**（nvtracker_proc.h L68-83）：`SurfaceStreamId`（uint64，由 `StreamId`+`SurfaceId` 合成）区分"每源每 surface"——360 度 dewarp 这类一源多 surface 的场景有一等支持；`SubBatchId`/`SeqIndex` 把批内帧精确定位。

**C ABI 数据结构**（includes/nvdstracker.h）：

- `NvMOTFrame`（L280-317）：一帧输入——`streamID/seq_index/frameNum/timeMeta`（PTS/NTP/接收时间三元组）、`doTracking/reset` 旗标、`bufferList`（多个转换后的 buffer）、`objectsIn`（检测框列表 `NvMOTObjToTrackList`）。
- `NvMOTTrackedObj`（L324-359）：输出——`trackingId`/`bbox`/`confidence`/`age`（轨迹帧龄）/`associatedObjectIn`（回指输入框）之外，还有一大截**增值字段**：`reid`（ReID 特征向量）、`visibility`、`ptImgFeet/ptWorldFeet`（图像/世界坐标脚点）、`convexHull`、`mask`（实例分割掩码）、`bbox3DWorld/bbox3DImg[8][2]`（3D 框八角点）以及 128 字节 `reserved`——结构本身就是低层库能力的"最大公约数合同"。
- `NvMOTTrackedObjBatch`（L380-388）带 `pReidTensorBatch`（整批 ReID 张量输出）；`NvMOTTrackerMiscData`（L393-404）三路历史数据：`pPastFrameObjBatch`（过去帧轨迹，供滞后取用）、`pTerminatedTrackBatch`（已终止轨迹）、`pShadowTrackBatch`（影子轨迹）。

**两个缓冲管理器**：`ConvBufManager`（convbufmanager.h L32-）管图像转换池——`MAX_BUFFER_POOL_SIZE = 2`（L30，注释明言 fixed），`convertBatchAsync`/`syncBuffer` 异步转换+同步等待；IOU 这类不用图像的跟踪器时池"intentionally empty"（L68-70）。`TrackerMiscDataManager`（miscdatabufmanager.cpp）管 misc 数据缓冲池，池耗尽时告警"Try increasing user-meta-pool-size"（nvtracker_proc.cpp L2553-2557）。

## 三、外部连接

- **上游**：nvinfer/nvinferserver（检测框在 `NvDsObjectMeta`）。`input-tensor-meta=1` 时改吃 `nvdspreprocess` 挂的 `NVDS_PREPROCESS_BATCH_META` 用户元数据——submitInput 里按 `tensor-meta-gie-id` 过滤（L772-778）、校验张量 gpu-id 与 tracker 一致（L784）、验证 `GST_NVDSPREPROCESS_MEMORY_TYPE` 内存类型（L792），然后把预处理 surface 直接拼成追踪输入（L805-811）。
- **下游**：nvdsanalytics（第 5 篇的越线/方向全靠 trackingId）、OSD（`display-tracking-id` 画 ID）、msgconv（事件消息携带轨迹）。`NvDsTargetMiscDataBatch`（past-frame 数据）经 user meta 流动，是"先出结果后补轨迹"类应用（消息回调里取历史）的通道。
- **低层库生态**：NVIDIA 发布的 NvDCF/IOU/NvSORT/DeepSORT 库 + 社区自研库，同一 ABI；`nvdstracker.h` 是唯一契约文件。
- **系统依赖**：NvBufSurface 变换（VIC/GPU 硬件缩放）、CUDA（ReID 推理）、NVTX（性能打点）。

## 四、数据流

1. **提交** `submitInput`（L701-856）：先查 `m_TrackerLibError`（L704，低层库已挂就拒绝新批）。图像路径：`numTransforms > 0` 时等转换池空闲（L717-731），`convertBatchAsync` 把批缩放到低层库要的分辨率/格式（L737 注释强调**异步**，真正访问前必须 sync）。张量路径如上。然后 `m_PendingBatch[batchId]` 登记（L835-846，防重复提交）并入队 `m_ProcQueue` 或走 `dispatchSubBatches`。
2. **处理线程** `processBatch`（L2436-2600）主循环：
   - 先处理两类**控制请求**：源删除（`m_TrackerLibRemoveStreams`，L2468-2491）与动态配置更新（`m_TrackerLibUpdateParams`，L2493-2502）——控制流与数据流同队列，天然串行化。
   - **帧重排** `queueFrames`（L2510-2514）：同一 `ssId` 出现多帧时按 `frameNum` 升序拆成多次调用——注释给了具体例子 `{(ssId1,frameNum1); (ssId2,frameNum1); (ssId1,frameNum2)}`，保证跟踪器看到的帧序单调。
   - **misc 数据领取**（L2516-2558）：从池里 pop 一个 `NvTrackerMiscDataBuffer`，按配置挂 pastFrame/terminated/shadow/reid 四路输出指针；池空则告警降级。
   - **填帧与执行**：`fillMOTFrame` 把 NvDs 检测框翻译成 `NvMOTFrame.objectsIn`（L2575-2578），`syncBuffer` 等图像转换完成（L2569-2572），然后在 NVTX 段里调 **`m_TrackerLibProcess(contextHandle, &procInput, &procResult)`**（L2573-2585）——插件层唯一一次真正"跟踪"。
   - **回写**：可选 `NvMOT_RetrieveMiscData` 取历史帧数据（L2588-2596），`updateBatchMeta` 把 `NvMOTTrackedObj` 写回 `NvDsObjectMeta`（trackingId、confidence 等，L2597）。
   - **完成信号**：批从 `m_PendingBatch` 移除、`m_CompletionQueue` 推入并 notify（L2600-2615）——`waitForCompletion`（L858）由此解除阻塞，GStreamer transform 返回，buffer 下行。
3. **子批模式** `processSubBatch`（L2804 起）：与主循环同构，但每线程独立 `contextHandle`、独立 misc 池（L2812-2824），并有 `errRecoveryTrials` 重试计数（L2810）——低层库崩了按配置次数重初始化，`-1` 无限拉起。
4. **源生命周期**：`removeSource` 走请求队列串行化删除（避免与数据竞争），`resetSource`（L692-699）把下一帧标记 `reset=true`（`NvMOTFrame.reset` 字段）让低层库自行清轨迹。

## 五、设计决策

- **算法与调度彻底分离**：跟踪算法迭代快、形态多（光流/相关滤波/ReID 深度特征/3D 卡尔曼），而调度层问题（批管理、转换池、线程、元数据翻译）稳定。用 C ABI + dlopen 让两者独立演进，同一调度层可以挂从纯 CPU IOU（零图像需求）到重型 NvDCF+ReID（要 GPU 张量）的任意实现——`numTransforms` 为 0 时的空池路径（convbufmanager.h L68-70）就是为最轻实现留的门。
- **必需/可选符号分级**：三个核心函数必需、四个增强可选。库作者可以从最小实现起步（IOU 跟踪器几十行就能接上），新能力（shadow tracks、ReID 张量输出）作为可选符号逐步加——ABI 版本地狱的务实解法。
- **控制流搭数据流便车**：源删除/配置更新不另设同步机制，而是作为特殊"请求"排进处理队列（L2468-2502）——与数据处理天然互斥，免锁设计。
- **`reserved[128]` 与超集结构**：`NvMOTTrackedObj` 把 ReID/3D 框/掩码/世界坐标全塞进一个结构（L324-359）而不是分层可选结构——牺牲一点 ABI 敏感度换取"一个结构走天下"，配合 `NvMOT_Query` 能力协商。
- **转换池固定为 2**：`MAX_BUFFER_POOL_SIZE=2`（convbufmanager.h L30）是吞吐与显存的折中——双缓冲足够让"当前批在跟踪"与"下一批在转换"重叠；池小了流水断，池大了显存浪费且帧龄变大。
- **`waitForCompletion` 同步语义**：与 nvinfer 的多线程推批不同，tracker 在 transform 里同步等结果。跟踪本质上是序贯的（下一帧依赖上一帧状态），批间并行收益有限，同步换来了下游时间序的强保证。
- **张量直通省一遍图像管线**：`input-tensor-meta` 让 tracker 与推理共享同一个预处理输出（nvdspreprocess 已缩放好的张量），省一次 NvBufSurface 变换和一次 GPU 拷贝——多路高分辨率场景的实打实优化。

## 六、新人提示

1. **选低层库先看 IOU 基线**：`ll-lib-file` 指向 `libnvds_nvmultiobjecttracker.so` 时配置文件里 `trackerWidth/trackerHeight/useBatchedBuffer` 决定图像路径；IOU 只用框不用图（转换池空转），CPU 路数堆到几十路时先把 NvDCF 换 IOU 对比，很多场景精度损失远小于预期。
2. **ID 跳变先查三处**：①检测 interval 太大（跟踪器空窗太长丢关联）；②tracker 的 `maxShadowTrackingAge`/ termination 门槛（目标短暂遮挡被判终止）；③分辨率转换过狠（`trackerWidth` 太小，ReID 特征失真）。日志 `gstnvtracker:` 前缀全开（`GST_DEBUG=nvtracker:6`）能看到 low-level lib 的 init/query 输出。
3. **自己的跟踪库从最小 ABI 起步**：实现 `NvMOT_Init/Process/DeInit` 三函数 + 一个 `NvMOT_Query`（哪怕全默认）即可跑通；对照 `nvdstracker.h` L280-410 的结构注释写填充逻辑，别实现可选符号直到需要。
4. **pastFrame 是深度功能**：消息回调常发生在批已下行之后（第 6 篇 msgconv），此时要"过去几帧的轨迹"就得靠 `NvMOT_RetrieveMiscData` 填的 `pPastFrameObjBatch`——配置 `past-frame=1` 且注意 `user-meta-pool-size`（告警见 L2553）。
5. **sub-batches 是按 GPU/组并行**：源数巨大时把批拆多个子批各配独立上下文（L411）；但子批间**无 ID 语义隔离之外的独立性**——同一目标跨子批不会关联，切分要按物理相机边界切。
6. **360/多 surface 源认准 SurfaceStreamId**：普通应用 pad_index 即 streamId；dewarp 源一帧多 surface，必须理解 `StreamId+SurfaceId` 合成的 64 位 id（nvtracker_proc.h L73-77），下游 analytics 按 ssId 对账。
7. **低层库崩溃恢复有限**：`m_TrackerLibError` 置位后主路径直接放行未处理帧（L2456 注释"send unprocessed as output"），管线不断但轨迹全断——监控里要有对 trackingId 突然清零的告警；子批模式才配 `err-recovery-trial-cnt` 自动拉起。

> 注：本篇行号基于 DeepStream 9.1 源码（`src/gst-plugins/gst-nvtracker/`、`includes/nvdstracker.h`）核实。NvDCF/NvSORT 等低层跟踪库本仓库不含源码（仅 `src/utils/nvmultiobjecttracker/model/tracker_ReID` 资产），其内部行为以二进制发布文档为准。
