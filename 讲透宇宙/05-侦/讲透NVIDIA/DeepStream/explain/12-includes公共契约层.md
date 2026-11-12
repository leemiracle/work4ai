# 12 includes/：公共契约与 vendored 依赖层

## 一、角色定位

`includes/` 是整个 DeepStream 生态的**宪法层**：74 个顶层头文件 + 四个子目录（opentelemetry 592 个、prometheus 21 个、ds3d、nvdsinferserver），全部以 `include <xxx.h>` 的系统级路径被 src/ 各组件与下游 ISV 代码引用。它承担两种截然不同的角色：**自研公共契约**——nvdsmeta.h（1130 行，元数据根契约）、nvbufsurface.h（1148 行，缓冲抽象）、nvdsinfer_context.h（1017 行，推理 API）、nvmsgbroker/nvds_msgapi（消息层）等，这些头定义的结构体跨插件、跨应用、跨语言边界流动，改一个字段就是全生态 ABI 事件；**vendored 三方依赖**——opentelemetry v1.23.0（version.h:13 实证）、prometheus-cpp、half.hpp 4618 行（第 34 行标注 Version 2.2.0，Christian Rau 2012-2021 的 IEEE 754 半精度库），把可观测性与 FP16 转换的依赖钉死在仓内，用户装一个 deb 就齐活。理解这一层的分层，就理解了 DeepStream "插件如何解耦"的物理基础。

## 二、内部结构

**nvdsmeta.h 根契约**：核心是池化元数据对象模型——`NvDsMetaPool`（第 221 行）挂五种池：frame/obj/classifier/display/user/label_info（NvDsBatchMeta 结构体内第 270-285 行逐字段声明）；`NvDsBatchMeta`（第 262 行）→`NvDsFrameMeta`（第 306 行，含 `bInferDone` 第 341 行推理完成标志）→`NvDsObjectMeta`（第 365 行）三级嵌套；每级都留 `misc_*_info[MAX_USER_FIELDS]` 扩展槽（第 50 行定义 MAX_USER_FIELDS=4，batch/frame/obj 各 4 个 gint64）；API 族 `nvds_add_user_meta_to_{batch,frame,roi,obj}`（第 755-788 行）+ `nvds_get_user_meta_type` 字符串注册式类型分配（第 1123 行）+ `nvds_batch_meta_copy_func` 拷贝协议（第 868 行）。**NvDsMetaType**（第 197 行）是开放枚举：NVIDIA 段保留、用户段从 NVDS_START_USER_META 起自增。**配套专用头**：nvdsmeta_schema.h（503 行）定义云上报 payload——`NVDS_PAYLOAD_DEEPSTREAM/MINIMAL/PROTOBUF` 三态+CUSTOM 段（第 96-105 行）、NvDsEventMsgMeta（第 394 行）与 NvDsVehicleObject/NvDsPersonObject(Ext) 领域对象（第 171-224 行）；gstnvdsmeta.h 是 GstMeta 桥（`gst_buffer_get_nvds_batch_meta`，第 187 行），NVDS_BATCH_GST_META 枚举锚点在第 76 行；nvds_latency_meta.h 定义 NvDsFrameLatencyInfo 逐源延迟探针。**nvbufsurface.h**：NVBUF_MEM_CUDA_{DEVICE,PINNED,UNIFIED,ARRAY} 内存类型枚举（第 353-374 行）、NVBUF_MAP_READ/WRITE 映射模式（第 76-79 行）、色彩格式与平面布局类型，allocate/map/transform 三族函数——**"帧"在这层被抽象为跨设备表面而非裸指针**。**推理契约双子**：nvdsinfer.h（319 行，张量侧——NvDsInferLayerInfo/NetworkInfo/解析回调 NvDsInferParseObjectInfo）与 nvdsinfer_context.h（1017 行，引擎侧——NvDsInferContextInitParams 第 246-491 行近 250 行初始化参数结构）。**消息层**：nvds_msgapi.h 定义连接/发送/订阅回调与 `nvds_msgapi_connect/send/send_async`（第 117/132/150 行），nvmsgbroker.h 是适配器加载契约。

## 三、外部连接

向上：src/gst-plugins 全部插件与 src/apps 全部应用都直接消费这些头；下游用户的 custom probe/parser 代码同样 include——头文件即 SDK 面向 ISV 的实际边界（安装后被拷到 /opt/nvidia/deepstream/deepstream-9.1/include/ 或 dev 包）。向下：vendored opentelemetry/prometheus 的消费者是 src/utils/nvds_rest_server/（opentelemetry_client.cpp 与 prometheus_client.cpp，REST 服务器把管线指标以 OTel trace 与 Prometheus 指标两种格式导出）；half.hpp 的消费者是 src/utils/nvdsinferserver/infer_trtis_server.cpp（Triton 张量 FP16 转换）；ds3d/ 服务 3D 感知插件族，nvdsinferserver/ 六头文件（infer_icontext/infer_ioptions 等）是 nvinferserver 的 C++ 接口层。横向：nvdsmeta_schema.h 的 payload 结构与 msgconv 插件、Kafka 生态（schema 由 proto 定义）；nvdsinfer_tlt.h 定义 TAO etlt 模型解密接口连 TAO 工具链；civetweb.h/CivetServer.h vendored 的 HTTP 服务端连 REST server。nvds_yml_parser.h 把 YAML→GObject 的解析 API 暴露给 tao_apps 系应用（09 篇的 nvds_parse_* 家族即此）。

## 四、数据流

以一帧的生命周期串起契约链：解码插件产出 NvBufSurface（nvbufsurface.h 的内存类型决定它在 GPU/主机哪里）→nvstreammux 聚批并经 `gst_buffer_add_nvds_meta`（gstnvdsmeta.h:165）挂上 NvDsBatchMeta 桥接进 GStreamer 元数据系统→nvinfer 从池里 acquire obj_meta（nvdsmeta.h 池 API），把 NvDsInferLayerInfo 张量结果（nvdsinfer.h）解析成 bbox/classifier 挂进去→tracker/nvdsanalytics 沿同一条元数据链追加→probe/OSD 消费（07 篇的池级遍历正是遍历这些池）→msgconv 按 nvdsmeta_schema.h 的领域结构组装 NvDsEventMsgMeta→nvds_msgapi_send 走适配器出仓。**misc 槽与 user_meta 是用户的逃生通道**：不改 SDK 结构体就能挂自定义数据（copy/func 协议保证跨线程安全）。可观测性旁路：REST server 在上述任何环节后可被查询，指标经 vendored OTel/Prometheus 客户端导出到运维栈；延迟数据由 nvds_latency_meta.h 的结构承载。

## 五、设计决策

①**池化而非 malloc**：每帧每对象高频诞生/销毁的元数据走预分配池（五种池各司其职），零分配器抖动、天然聚合遍历（OSD 直接吃 full_list 的前提）；代价是池大小管理成了新的调参项。②**misc 槽 + 开放枚举双保险扩展**：4×gint64 留给标量、NvDsUserMeta+字符串注册类型留给结构体——契约二十年不破的关键是"永不删字段，只加槽位"。③**payload schema 独立成头**：云上报结构（person/vehicle 扩展版）与运行时元数据分离，演化节奏解耦——运行时结构追求稳定，schema 追求表达力。④**内存类型枚举而非多套 API**：CUDA device/pinned/unified/array 四种内存一套 NvBufSurface 抽象，transform API 统一转换——Jetson 与 dGPU 的差异被压缩进枚举值选择。⑤**vendored 而非包依赖**：OTel 592 头/prometheus/half 直接进仓，构建不依赖系统版本——对交付 deb 的 SDK 是唯一稳妥解；但版本钉死 v1.23.0 意味着升级要 NVIDIA 自己动手，用户报告的 OTel 上游修复不会自动到达。⑥**根契约 1130 行刻意克制**：nvdsmeta.h 只放"人人都要"的结构，专用元数据（analytics/opticalflow/dewarper/tracker）全部拆独立头——单头万能会变成编译依赖放大器。

## 六、新人提示

写第一个 probe 时把 nvdsmeta.h 当字典查：遍历顺序 batch→frame→obj 三层 for、acquire/release 配对（只 acquire 不 release 会耗尽池，症状是几分钟后元数据"消失"）、自定义数据用 user_meta 而非改结构体。三个高频误读：(1) NvDsObjectMeta 的 rect_params 坐标是 streammux 输出分辨率坐标系，换分辨率不改检测框计算会错位；(2) NVDS_PAYLOAD_DEEPSTREAM 与 MINIMAL 的区别是对象字段裁剪，Kafka 带宽敏感时先试 MINIMAL；(3) nvbufsurface 的 surface 指针跨线程传递前必须确认 mem type——CUDA_DEVICE 指针在主机线程解引用就是段错误，先 NvBufSurfaceMap 做 map。想给自研插件加头文件：放进 includes/ 意味着承诺 ABI 稳定，内部实现头放 src/ 各组件目录更合适。vendored 升级：OTel 想换新版本只能等 NVIDIA 更新仓（version.h:13 锁 1.23.0），自己改 vendored 树会在下次 deb 升级时被覆盖。甄别说明：本篇行数/版本号全部实测——nvdsmeta.h 1130 行、nvbufsurface.h 1148 行、half.hpp 4618 行（v2.2.0）、OTel v1.23.0（version.h:13）、prometheus 21 头；任务书"nvbufsurface"与"vendored OTel v1.23+prometheus+half.hpp 4618 行"四项主张全部核实成立。
