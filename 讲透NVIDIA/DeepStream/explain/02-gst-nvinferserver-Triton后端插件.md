# 02 gst-nvinferserver：Triton 后端插件（gRPC/CAPI 双模式）

## 一、角色定位

`gst-nvinferserver` 是 DeepStream 面向 **Triton Inference Server** 的推理插件。它把 `nvinfer` 的"进程内 TensorRT"换成 Triton 生态：模型仓（model repository）、ensemble、多框架 backend（TensorRT/ONNX/PyTorch/TF）、显式版本管理、A/B 流量分配。当你的管线需要 Triton 的模型治理能力，或者模型根本不是 TRT engine 时，就用它替换 nvinfer——两者产出的 NvDsMeta 语义一致，下游 tracker/OSD/消息链完全无感。

它最有意思的工程特性是**双模式后端**：同一份配置文件、同一个 `IInferContext` 接口，底下可以是
1. **CAPI 模式**（进程内）：把 Triton 的 `tritonserver` C 库直接链进来，在自己进程里拉起一个 Triton 实例（`model-repo` 指向本地目录）；
2. **gRPC 模式**（进程外）：作为纯客户端连远端（或本机独立进程的）Triton server（`url: ip:port`），还支持 CUDA 共享内存传输入张量。

和第 1 篇一样分两层：插件层 `src/gst-plugins/gst-nvinferserver/`（4 对文件）+ 引擎层 `src/utils/nvdsinferserver/`（60 文件，编译成 `libnvds_infer_server.so`），公共接口在 `includes/nvdsinferserver/`。引擎层的配置格式是 **protobuf 文本**（prototxt），这是它与 nvinfer（key=value/YAML）最直观的差异。

## 二、内部结构

**公共接口层**（`includes/nvdsinferserver/infer_icontext.h`）：

- `IInferContext`（L59-98）只有四个方法：`initialize(prototxt, logFunc)`、`run(input, outputCb)`（注释明言 "expect the call is async_mode"，全异步回调制）、`deinit()`、`getNetworkInputInfo()`。比 nvdsinfer 的 queue/dequeue 双向接口更瘦。
- 三个 C 导出工厂（L108-138）：`createInferTrtISContext()`（CAPI）、`createInferTritonGrpcContext()`（gRPC）、`createInferTritonSimpleContext()`（轻量）。另有 `NvDsTritonServerInit/Deinit`（L149/L160）管理**进程级 Triton 单例**——注释写明"所有模型在任何 InferContext 之前预加载"，这是多插件共享一个 server 实例的机制。

**引擎层抽象**（`src/utils/nvdsinferserver/`）：

- 三接口鼎立：`IPreprocessor`/`IPostprocessor`（infer_iprocess.h L46/L64）、`IBackend`（infer_ibackend.h L65）。`IBackend::enqueue()`（L170-172）签名是全回调式的——`InputsConsumed` 与 `InferenceDone` 两个 `std::function`，天然适配 Triton 异步执行。
- 继承骨架（infer_common.h L63-68 前向声明可见）：`InferCudaContext`（infer_cuda_context.cpp L73 起，负责 CUDA 资源/预处理器/后处理器装配，`createPreprocessor` L209/`createPostprocessor` L264）是公共基座；`InferTrtISContext`（infer_trtis_context.cpp L50，CAPI 模式）与 `InferGrpcContext`（infer_grpc_context.cpp L37）都从它派生——`InferGrpcContext::allocateResource` 干完自己的事后直接 `return InferCudaContext::allocateResource(config)`（L282），gRPC 模式复用 CAPI 模式的全部前后处理逻辑，只换"执行后端"。
- **CAPI 后端**：`TrtISServer`（infer_trtis_server.h L538）包装 `TRITONSERVER_ServerOptionsNew` → `ServerOptionsSetModelRepositoryPath` → `ServerNew` 全流程（infer_trtis_server.cpp L903-982），日志/strict-readiness/backend 目录/pinned+CUDA 内存池都在 options 阶段配好。请求侧（infer_trtis_server.cpp L44-200）直接用 Triton C API：`TRITONSERVER_InferenceRequestNew` → `SetCorrelationId`（L122，序列模型）→ `SetFlags`（SEQUENCE_START/END，L132-140）→ `AddInput`/`AppendInputData`（L193-200）→ `SetResponseCallback`（L248）。
- **gRPC 后端**：`InferGrpcClient`（infer_grpc_client.cpp L57 起）包装 Triton client SDK 的 `tc::InferenceServerGrpcClient::Create`（L67）、`ModelMetadata`/`ModelConfig`（L92/L104，启动时拉模型元数据反推层信息）、健康三连 `isServerLive/isServerReady/isModelReady`（L123/L136/L149）、`LoadModel/UnloadModel`（L164/L178，热加载）。`TritonGrpcBackend::ensureServerReady/ensureModelReady`（infer_grpc_backend.cpp L116/L32）在初始化时轮询等待。
- **配置协议**：`nvdsinferserver_config.pb.{h,cc}`（4964/4574 行）定义 `infer_config`/`triton`/`server` 等消息；**关键 oneof**（`nvdsinferserver_config.pb.h` L1276-1277、L3710-3790）：`server` 要么 `kModelRepo` 要么 `kGrpc`——这正是插件层二选一的分派依据。`model_config.pb.{h,cc}`（17780/15879 行生成对）是 Triton 官方 `model_config.proto` 的完整生成物，让 DeepStream 能直接读懂模型仓里的 `config.pbtxt`（后处理 `output_parser`、`preprocess` 的 tensor_order/scale 等配置都靠它对齐 Triton 语义）。
- 流管理：`StreamManager`（infer_stream_manager.cpp L25-116：`waitStream/startStream/stopStream/popDeprecatedStream/streamInferDone`）给每路请求分配 Triton 流槽、回收过期流——序列模型（LSTM 等）状态跟踪靠 `InferLstmController`（infer_lstm.cpp）。

**插件层**（`src/gst-plugins/gst-nvinferserver/`）：

- `gstnvinferserver.cpp`（706 行）：GStreamer 壳，pad 协商与 GObject 属性（`config-file-path` 等，比 nvinfer 精简很多——大部分复杂度挪进了 prototxt）。
- `gstnvinferserver_impl.cpp`（1552 行）：核心 `GstNvInferServerImpl`。`start()`（L520 起）读配置→`google::protobuf::TextFormat::ParseFromString`（L532）→`validatePluginConfig`→**模式分派**（L564-588）：`tritonParams.has_grpc() && has_model_repo()` 同时配置直接报错"either native or grpc should be provided"；有 `grpc` 走 `createInferTritonGrpcContext`（L574），否则 `createInferTrtISContext`（L577）。
- `gstnvinferserver_meta_utils.cpp`（592 行）：与 nvinfer 同构的元数据挂载。

## 三、外部连接

- **上游**：与 nvinfer 完全相同——nvstreammux 批流 + NvDsBatchMeta；`processBatchMeta`（gstnvinferserver_impl.cpp L656-665）同样三分派：`inputTensorFromMeta` → `processInputTensor`、`isFullFrame` → `processFullFrame`、否则 `processObjects`。
- **下游**：tracker、nvdsanalytics、OSD、msgconv——消费的元数据与 nvinfer 同格式，`unique-id` 语义一致。
- **Triton 侧**：CAPI 模式 dlopen `libtritonserver.so`（仓库留了 `tritonserver_include/tritonserver.h` 与 `tritonserver_stub/libtritonserver_dummy.export` 两个桩，构建期无真库也能链）；gRPC 模式链 Triton client SDK。
- **模型仓**：`model_repo` 目录内每个模型一个 `config.pbtxt` + 版本子目录；DeepStream 的自定义解析库（`custom_lib`/`parse-bbox-func-name`）与 Triton 的 ensemble 可以在同一管线里共存。
- **跨插件**：进程内多个 nvinferserver 元素可共享 `ITritonServerInstance` 单例（L100-104 注释），模型只加载一份。

## 四、数据流

以 `processFullFrame`（gstnvinferserver_impl.cpp L966 起）为例：

1. **跳批**：`m_IntervalCounter++ % (inferInterval()+1)`（L968），语义与 nvinfer 的 interval 相同。
2. **批组装与预处理**：帧缩放进 `BatchSurfaceBuffer`（`ReturnScaleParams` L667 回填 scale/offset 供后处理还原坐标），与 nvinfer 一致走 CUDA 预处理；`infer_preprocess.cpp`（648 行）+ `infer_preprocess_kernel.cu`（382 行）执行片上 scale/normalize/ROI 裁剪，`tensor_pool` 尺寸受 `kNetworkPoolSize=3/kNonPreprocessNetworkPoolSize=5`（infer_trtis_context.cpp L38-39）约束。
3. **请求打包**：`batchInference`（L731-773）把批缓冲装进 `BaseBatchArray`，`addBatchOptions`（L680-727）往里塞 NvDs 上下文——`OPTION_NVDS_BATCH_META`、`OPTION_NVDS_GST_BUFFER`、frame/obj meta 列表、stream id 列表（L685-724）。**这些指针是回程机票**：输出回来时后处理靠它们找到该把检测框写到哪个 `NvDsFrameMeta`。
4. **异步提交**：`m_InferCtx->run(batchArray, cb)`（L751-757），cb 里 `reqBuf->promise.set_value()`；同时 `queueOperation` 把"等 future + `InferenceDone`"排进 **`m_OutputThread`**（L615-618 创建的专用输出线程，L763-766）。与 nvinfer 的双 GQueue 队列方案不同，这里是 promise/future + 单输出线程的事件队列。
5. **后端执行**（二选一）：CAPI 模式 `IBackend::enqueue` → Triton 响应回调 → 输出张量 D2H（若配置）；gRPC 模式 `TritonGrpcBackend::Run`（infer_grpc_backend.cpp L130）→ 若 `enable_cuda_buffer_sharing` 走共享内存，否则序列化发送。
6. **输出与元数据**：输出线程醒来 → `InferenceDone` → `infer_postprocess.cpp`（1232 行）解析检测/分类/分割 → 经 `gstnvinferserver_meta_utils.cpp` 写 NvDsMeta → 原 GstBuffer 下推。二级推理的对象缓存（`secondary_reinfer_interval`，L1226-1263）与 nvinfer 的 history map 机制同源。

## 五、设计决策

- **上下文继承树把"前后处理"与"执行后端"正交分解**：`InferCudaContext` 拥有全部 CUDA 资源与前后处理器，`InferTrtISContext`/`InferGrpcContext` 只注入不同的 `IBackend`。新接一种服务后端（比如 vLLM 式 HTTP）只需再派生一个 context + backend，预处理器/后处理器/流管理全部复用——这是 60 文件大目录仍然可控的原因。
- **配置选 protobuf 文本而非 YAML**：`infer_config` 消息树与 Triton 的 `model_config.proto` 打通（model_config.pb 生成对直接编进库），插件读 `config.pbtxt` 语义零转换；代价是配置可读性略差、字段名全 snake_case。插件层用 `DebugString()` 传递配置（L549 `contextStr = m_PluginConfig.infer_config().DebugString()`），两层之间传的是**同构文本**而非结构体——松耦合但多一次序列化。
- **互斥校验前置**：`has_grpc() && has_model_repo()` 在启动即报错（L568-571），不给"默认走某个"的模糊空间——配置歧义宁可早死。
- **指针随行（options 机制）**：NvDs 指针全部塞进 `BufOptions` 跟着张量走全程，而不是全局表查找。这让 `run()` 是纯函数式的（输入数组进、输出回调出），线程安全免费获得，也方便 `NvDsInferServerWrapBuf`（infer_icontext.h L173）这类 C 封装给外部应用用。
- **进程级 Triton 单例**：多模型管线（primary + 多个 secondary 都走 Triton）只起一个 server 实例、一次加载全部模型，`NvDsTritonServerInit` 的注释点明"all models would be loaded prior to all InferContext"——把 Triton 的启动开销摊到整条管线。
- **Other 网络的防呆告警**：`isOtherNetowrk() && !needOutputTensorMeta() && !hasCustomProcess()` 时启动警告（L552-561）——配了"不解析输出"却又没开张量回传，输出等于全丢，提前喊话而非静默。
- **留桩编译**：`libtritonserver_dummy.export` 允许无 Triton 环境编译插件（运行时再加载真库），CI 与交叉编译友好。

## 六、新人提示

1. **读配置先认消息结构**：入口在 `src/utils/nvdsinferserver/nvdsinferserver_config.proto`（includes 下同名 .proto 是权威），`.pb.h` 是生成物不要手改；对照 sample 配置（`src/samples/configs/deepstream-app-triton/`）看 `infer_config.preprocess/postprocess/backend.triton.server` 的层级最直观。
2. **gRPC vs CAPI 的选择标准**：跨机部署/多客户端共享 GPU → gRPC（注意 `enable_cuda_buffer_sharing` 只在同机或 GPUDirect 环境有意义）；单机单进程追求低延迟 → CAPI 省掉网络栈与序列化。两者切换只改 `server:` 一节，其余配置不动。
3. **排错三板斧**：①`GST_DEBUG=nvinferserver:6` 看配置解析与后端初始化；②gRPC 模式先在 shell 里 `curl` server 的 `/v2/health/ready`，客户端侧 `ensureServerReady`（infer_grpc_backend.cpp L116）只轮询不诊断；③CAPI 模式模型加载失败先看模型仓 `config.pbtxt` 的 `platform`/`max_batch_size` 是否与插件配置一致。
4. **自定义解析的落点**：`custom_lib` 指向的 .so 由 `DlLibHandle`（infer_common.h L115）加载，函数签名要同时匹配 DeepStream 侧声明与 Triton 输出布局；写之前先读 `infer_postprocess.cpp` 里现有 parser 的调用方式，别按 nvinfer 的旧签名写。
5. **吞吐调优优先看两处**：`preprocess.tensor_pool.size`（缓冲池深度，默认受 `kNetworkPoolSize=3` 框）与 Triton 侧 `instance_group`（CAPI 模式下模型实例数直接吃同一块 GPU）；输出慢会导致输入池耗尽，现象是日志里 acquire 阻塞而非显式报错。
6. **别混用两代推理插件的配置**：nvinfer 的 `model-file`/`labelfile-path` 键在 nvinferserver 里不存在，反之 `infer_config` 块 nvinfer 也不认。迁移时文档要重写，没有自动转换器。
7. **序列模型（LSTM 状态机）**：`SetCorrelationId` + SEQUENCE_START/END 旗标（infer_trtis_server.cpp L122/L132）已封装好，配置 `sequence_id_prefix` 后每路流自动拿到稳定 correlation id，不需要自己在 pad probe 里造。

> 注：本篇行号基于 DeepStream 9.1 源码（`src/gst-plugins/gst-nvinferserver/`、`src/utils/nvdsinferserver/`、`includes/nvdsinferserver/`）核实；`.pb.h/.pb.cc` 为 protoc 生成物，行号随 protobuf 版本漂移，引用时以字段名定位为准。
