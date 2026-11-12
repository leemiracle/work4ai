# 01 gst-nvinfer：推理主插件（TensorRT 原生路径）

## 一、角色定位

`gst-nvinfer` 是 DeepStream 的"主推理引擎"插件——直接内嵌 TensorRT runtime、在进程内 GPU 上执行推理的那一个。整个 DeepStream 管线的"智能"源头就在这里：上游 `nvstreammux` 把多路视频聚成批，批流到 nvinfer，它负责缩放/色彩转换（预处理）、调用 TensorRT 引擎执行前向、把原始输出张量解析成结构化检测/分类元数据（后处理），再把结果以 `NvDsObjectMeta`/`NvDsClassifierMeta` 形式挂回 buffer 往下游送。

它和兄弟插件 `nvinferserver` 的分工是明确的：nvinfer 走**进程内 TensorRT C++ API**（模型以 Caffe/UFF/ONNX 或预生成 engine 文件形式加载），nvinferserver 走 **Triton 推理服务器**（进程外 gRPC 或进程内 C API）。前者延迟最低、路径最短，是检测器（Primary GIE）和二级分类器（Secondary GIE）的默认选择。

这个目录分两层，理解这一点是读代码的钥匙：

- **插件层** `src/gst-plugins/gst-nvinfer/`：GStreamer 元素壳，管 pad 协商、GObject 属性、配置文件解析、批组装线程。
- **引擎层** `src/utils/nvdsinfer/`（编译成 `libnvds_infer.so`）：真正的推理上下文 `NvDsInferContext`，管 TensorRT 引擎构建、CUDA 缓冲区池、预处理/后处理。

两层之间的契约是公共头 `includes/nvdsinfer_context.h`（1017 行）——它定义了 DeepStream 推理接口 API（`@ingroup NvDsInferApi`），也是一个可独立使用的库：应用程序可以完全绕过 GStreamer，直接 `createNvDsInferContext()` 拿句柄做推理。

## 二、内部结构

**引擎层根接口**（`includes/nvdsinfer_context.h`）：

- `NvDsInferContext` 抽象类（L798-820）：三个纯虚方法构成完整的推理生命周期——`queueInputBatch()` 提交一批帧（阻塞）、`dequeueOutputBatch()` 按提交顺序取回输出、`releaseBatchOutput()` 归还缓冲。注释明确说明"输出的出队顺序对应入队顺序；失败则该批输出丢失"。
- 工厂函数 `createNvDsInferContext()`（L881，C++）/ `NvDsInferContext_Create()`（L914，C 包装）。
- 关键常量与枚举：`NVDSINFER_MAX_BATCH_SIZE 1024`（L112）；`NvDsInferNetworkMode` 四档 FP32/INT8/FP16/BEST（L127-133，注释指明对齐 trtexec 的 `--fp16/--int8/--noTF32/--best` 旗标，`useStronglyTyped` 对应 `--stronglyTyped`）；网络类型五种（L138-158）——Detector/Classifier/Segmentation/InstanceSegmentation，以及 `NvDsInferNetworkType_Other = 100`（输出层不解析、张量直接随元数据流动，是自定义后处理的逃生门）。
- 检测聚类四模式（L236-240）：`GROUP_RECTANGLES`（OpenCV）、`DBSCAN`、`NMS`、`DBSCAN_NMS_HYBRID`，参数结构 `NvDsInferDetectionParams`（L199-230）里 preClusterThreshold/postClusterThreshold/eps/minBoxes/topK 一应俱全。

**引擎层实现**（`src/utils/nvdsinfer/`，13 文件）：

- `nvdsinfer_context_impl.cpp`（2448 行）：`NvDsInferContextImpl` 是唯一实现。`allocateBuffers()`（L1552）建两条 CUDA stream——`m_InferStream` 跑推理、`m_PostprocessStream` 跑后处理拷贝，并用 NVTX 命名便于 nsight 追踪（L1561-1562）。输出缓冲池 `resizeOutputBufferpool()`（L1445）有显存护栏：`cudaMemGetInfo` 检查剩余显存低于 `(1 - m_MaxGPUMem/100) * total` 就拒绝扩池（L1459-1462），自动扩池时一次只加 6 个（`queueInputBatch` L1916 附近的 `resizeOutputBufferpool(6)`）。
- `nvdsinfer_model_builder.cpp`（1375 行）：`TrtModelBuilder` 负责从 Caffe/UFF/ONNX 构建 engine。`buildEngine()`（L886/L896）调 `buildSerializedNetwork()`，有一个贴心的 FP16 回退：TRT10+ 下若 FP16 失败会清掉 `g_fp16FlagWasSet` 重试（L931-940），成功后 `deserializeCudaEngine`（L949）。INT8 路径挂校准器 `setInt8Calibrator`（L433/L1045）。engine 可 `serializeEngine`（L1289）落盘缓存、`deserializeEngine`（L1318）直接复用。构建期 workspace 上限 `WORKSPACE_SIZE = 450MB`（L47）。
- `nvdsinfer_backend.cpp`：`createBackendContext()`（L176）按是否用 DLA 分成 `FullDimTrtBackendContext`（L294）与 `DlaFullDimTrtBackendContext`（L365），两者 `enqueueBuffer` 最终都是 `m_Context->enqueueV3(stream)`（L348/L413）——TRT 10 的 enqueue 三代接口。
- `nvdsinfer_context_impl_output_parsing.cpp`（993 行）：输出解析，按网络类型分派到 `NvDsInferContextImpl::parseBoundingBox`/`parseAttributes` 等路径，并对接 `NvDsInferParseCustomAvg`/`NvDsInferParseCustomBoundingBox` 等自定义解析函数（model config 里的 `parse-bbox-func-name` 回调）。
- `nvdsinfer_conversion.cu`（554 行）：片上归一化/色彩空间转换 kernel。

**插件层**（`src/gst-plugins/gst-nvinfer/`，6 对文件）：

- `gstnvinfer.cpp`（2848 行）是主体：`GstNvInfer` 继承 `GstBaseTransform`，属性枚举（gstnvinfer.h L66-90）包括 `OPERATE_ON_GIE_ID`（只对上游某个 GIE 的检测框做二级推理）、`OPERATE_ON_CLASS_IDS`/`FILTER_OUT_CLASS_IDS`、`INPUT_TENSOR_META`/`OUTPUT_TENSOR_META`、`DYNAMIC_PROPERTIES` 等；还有一个 GObject 信号 `SIGNAL_MODEL_UPDATED`（L93-98），模型热更新完成时通知应用。
- `gstnvinfer_impl.cpp`（489 行）：`DsNvInferImpl`（gstnvinfer_impl.h L219）持有 `m_InferCtx`（L242），实现模型后台加载与 `ensureReplaceNextContext()`（L238/gstnvinfer_impl.cpp L448）——运行中换模型的机制。
- `gstnvinfer_property_parser.cpp`（1492 行）+ `gstnvinfer_yaml_parser.cpp`（1091 行）：新旧两代配置文件（key=value 与 YAML）解析。
- `gstnvinfer_allocator.cpp`（267 行）：自定义 GstAllocator，从内部缓冲池给色彩转换后的帧分配内存。
- `gstnvinfer_meta_utils.cpp`（813 行）：把推理输出翻译成 NvDsMeta（检测框、分类属性、分割掩码）。

## 三、外部连接

- **上游**：几乎总是 `nvstreammux`（批流）。也接受任何带 `NvBufSurface` + `NvDsBatchMeta` 的上游元素。输入兼容性检查在 `gst_nvinfer_process_full_frame`（gstnvinfer.cpp L1721-1731）：device 内存要求 `surface->gpuId == 元素 gpu-id`，否则报"Memory Compatibility Error"。
- **下游**：tracker、nvinferserver、nvdsanalytics、OSD、msgconv——下游靠批元数据里每个检测框的 `unique_component_id`（即 nvinfer 的 `unique-id` 属性）识别框出自哪个 GIE，二级推理正是用 `operate-on-gie-id` 反向引用它。
- **横向**：与 `nvinferserver` 共享元数据格式与"process-mode 全帧/对象"概念但互不依赖；`gst-nvdspreprocess` 产出的预处理张量可经 `INPUT_TENSOR_META` 直接喂进来，跳过内部缩放。
- **系统依赖**：TensorRT（nvinfer1/nvonnxparser）、CUDA runtime、NvBufSurface 变换库（NVIDIA 多媒体栈）、NVTX、GStreamer base。
- **应用侧**：`deepstream-app` 及全部 sample app 用它组 GIE 链；`service-maker`、Python 绑定也是这颗插件的壳。

## 四、数据流

以一帧批 buffer 到达为线，串起插件层三线程设计：

1. **入队** `gst_nvinfer_submit_input_buffer`（gstnvinfer.cpp L2371）：先查模型热替换（L2383 `ensureReplaceNextContext`），`current_batch_num <= stabilize_buffer_count` 的启动期帧直接丢弃不推理（L2394，让管线先稳定）。map 出 `NvBufSurface` 后三路分派（L2428-2434）：`input_tensor_from_meta`（吃上游张量元数据）→ `gst_nvinfer_process_tensor_input`；`process_full_frame`（主检测器）→ `gst_nvinfer_process_full_frame`；否则（二级）→ `gst_nvinfer_process_objects`。
2. **批组装与片上转换** `gst_nvinfer_process_full_frame`（L1700）：`interval_counter++ % (interval+1)` 实现 `interval` 跳批省算力（L1715）。每帧经 `get_converted_buffer()`（NvBufSurfTransform 批量缩放+色彩转换，写入内部池 `conv_buf`），帧参数（scale_ratio、offset、frame_meta 指针）压进 `GstNvInferBatch.frames`；攒满 `max_batch_size` 或到达输入批尾即 `convert_batch_and_push_to_input_thread` 提交（L1802-1811）。
3. **双线程流水**：启动时起两条线程（L1277-1289）——`nvinfer-input-queue-thread`（因为 `queueInputBatch` 是阻塞函数，转换与提交并行）与 `nvinfer-output-thread`（L2565 `gst_nvinfer_output_loop`）。原 GstBuffer 本身包成 `push_buffer=TRUE` 的标记批也进同一队列（L2476-2485），保证输出顺序与提交顺序对齐。
4. **引擎层执行** `NvDsInferContextImpl::queueInputBatch`（nvdsinfer_context_impl.cpp L1826）：批次超 `m_MaxBatchSize` 拒收（L1832）；`m_Preprocessor->transform()` 把转换后的帧打包进绑定缓冲；从 `m_FreeBatchQueue` 弹一套输出缓冲（空了且开 autoIncMem 就扩 6 套，L1916-1923）；构 `BackendBatchBuffer` 后 `m_BackendContext->enqueueBuffer()` 上 TRT（L1935）；`cudaEventRecord(m_InferCompleteEvent)`，再让 postprocess stream `cudaStreamWaitEvent` 等 inference 完成（L1940-1949）后异步拷 D2H，最后把批次推进 `m_ProcessBatchQueue`。
5. **出队与元数据挂载**：插件 output_loop 弹批 → `dequeueOutputBatch`（L2033）`cudaEventSynchronize(m_OutputCopyDoneEvent)` 等 D2H 完成 → `postProcessHost()` 解析 → output_loop 把检测框/分类属性经 `gstnvinfer_meta_utils.cpp` 写入 NvDsMeta，遇到 `push_buffer` 标记批才把原 GstBuffer 推给下游（L2627-2630）。
6. **异步分类捷径**：`classifier_async_mode` 下（L2443-2470）二级分类器不等结果，buffer 立即下推；结果回来后写进 per-source 的 `GstNvInferObjectHistoryMap`（gstnvinfer.h L165），下次对象再现时补挂最新属性。历史图定期清理（`cleanup_history_map` L1819，按 `MAP_CLEANUP_INTERVAL`/`CLEANUP_ACCESS_CRITERIA` 淘汰陈旧对象）。

## 五、设计决策

- **GStreamer 壳与推理引擎解耦**：1017 行的 `nvdsinfer_context.h` 是稳定公共 API，插件只是它的一种消费者。这让同一推理库能被 service-maker、Python、裸 C 应用复用，也让 `nvinferserver` 插件能以**相同的元数据产出**替换 TensorRT 后端——上层管线无感。
- **三线程流水线**（提交线程/输入队列线程/输出线程 + 引擎层双 CUDA stream）：帧转换、TRT 前向、D2H 拷贝、CPU 解析四段重叠执行。输出缓冲池多套轮换的注释（L1548-1549）写明动机："while the output of one batch is being parsed on the CPU, we can queue pre-processing and inference of another on the GPU"。
- **顺序保持靠标记批而非锁序**：nvinfer 不在原 buffer 上等推理，而是插入 `push_buffer` 标记批维持输出顺序——这让它可以同时积压多个输入 GstBuffer（`input_queue`/`process_queue` 两条 GQueue），吞吐不被单 buffer 生命周期卡死。
- **二级推理的"面积重推"启发式**（`should_infer_object` L1850-1909）：二级分类器只对 `operate_on_gie_id` 匹配、尺寸在 min/max 之间、class_id 命中的对象做；且对象面积增长超过 `REINFER_AREA_THRESHOLD` 或超过 `secondary_reinfer_interval` 帧才重推——用陈旧结果的缓存（`GstNvInferObjectHistory.cached_info`）换取大量算力，这是多级 GIE 级联能跑满路数的关键。
- **显存护栏**：扩池前查 `cudaMemGetInfo`，`m_MaxGPUMem` 百分比封顶（L1459），宁可丢批也不 OOM 整条管线。
- **模型热更新**：`SIGNAL_MODEL_UPDATED` 信号 + `ensureReplaceNextContext()`（每个 buffer 到达时检查）+ 后台加载线程，支持不重启管线换模型。
- **escape hatch 设计**：`network-type=100`（Other）不解析输出张量，配合 `output-tensor-meta=TRUE` 让自定义后处理（如 DLA 网络的奇怪输出、LLM 式嵌入）可以完整流动——这是 DeepStream 保持"通用视频 AI 框架"定位的阀门口。

## 六、新人提示

1. **先读两个文件就够入门**：`includes/nvdsinfer_context.h` 的 doxygen 头注释（L18-83）+ `gstnvinfer.cpp` 的 `submit_input_buffer`→`process_full_frame`→`output_loop` 三函数，比读任何文档都准。
2. **排错先开 GST_DEBUG=nvinfer:5**。常见三坑：gpu-id 与上游 surface 不匹配（L1721 报 Memory Compatibility Error）；batch-size 与 engine 的 max batch 不符（启动时直接失败）；engine 文件与当前 GPU/TRT 版本不符（`deserializeEngine` L1318 的报错会给出路径与版本提示）——重新生成 engine 或删掉缓存让它重建。
3. **看性能用 Nsight Systems**：插件已埋好 NVTX 域与 range（L2399-2407 的 `buffer_process batch_num=`），两条 CUDA stream 也被命名（`nvdsinfer_infer_uid=N`/`nvdsinfer_postproc_uid=N`），时间线上一眼能看出推理与后处理是否重叠。
4. **interval 不是节流器是省算力开关**：`interval=N` 意味着每 N+1 批只推 1 批推理（L1715），中间帧完全没检测元数据——下游 tracker 会靠跟踪填补，但别指望检测框在跳过的帧里存在。
5. **改配置先认准格式**：老 config 是 `key=value`（`gstnvinfer_property_parser.cpp`），新 YAML（`gstnvinfer_yaml_parser.cpp`）字段名不完全对称；两代解析器并存，搜属性名时两个文件都要查。
6. **engine 文件路径坑**：`model-engine-file` 指向的 engine 若比模型文件旧，插件可能直接用旧 engine（不一定报错），调试精度问题时先删 engine 强制重建。
7. 与 `nvinferserver` 二选一时：单机 TensorRT 原生模型 → nvinfer；Triton 生态（ ensemble、非 TRT backend、多进程隔离）→ nvinferserver。两者元数据语义一致，切换时 `config-file` 格式不同（后者的 `infer_config` 是 protobuf 风格 YAML）。

> 注：本篇所有行号基于当前仓库 DeepStream 9.1 源码（`src/gst-plugins/gst-nvinfer/`、`src/utils/nvdsinfer/`、`includes/nvdsinfer_context.h`）核实；若与官方文档冲突，以本文源码行号为准。
