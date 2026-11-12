# NVIDIAOpticalFlowSDK 新人入门（ONBOARDING）

- 基线：edb50da3（"nvof 2.0 headers for opencv"），图谱 10 节点 / 19 边 / 3 层 / 10 步导览
- 规模：3 文件 813 行（Common 551 + Cuda 244 + README 18）

## 1. 项目定位

**纯头文件契约仓**：全仓只有 2 个 C API 头 + 1 个 README，无实现、无示例、无构建系统。它发布 NVOFA——Turing 及之后 GPU 内置的硬件光流/立体视差引擎——的客户端 API 契约。引擎独立于图形/CUDA 核工作，端到端光流卸载后 CPU/GPU 核被解放（README.md:L2-4）。应用：目标检测跟踪、帧率上变换、深度估计、拼接。门槛：Turing+ GPU，Windows 驱动 445.87+ / Linux 450.51+（README.md:L14-15）。

两个认知：①**本仓不是完整 SDK**——文档/示例/库需另行下载（README.md:L17-18），commit 主题点明其意义：把 NV-OF 2.0 头独立发布给 OpenCV 等下游；②**头即 ABI**——布局与签名是驱动↔客户端二进制契约，动字段顺序即破坏性变更。技术栈：纯 C 头（extern "C" 兼容 C++），依赖 <cuda.h>，Windows 下 __stdcall（nvOpticalFlowCommon.h:L57-61）。

## 2. 架构总览

图谱三层，对应"文档 → 契约 → 后端"：

- **L01 文档总览**（README.md）：硬件定位、场景、驱动门槛、完整 SDK 下载入口。
- **L02 跨设备公共契约**（nvOpticalFlowCommon.h，枢纽 fanOut=10）：11 个枚举（错误码、能力、档位、网格、模式、缓冲用途/格式、视差范围）+ 8 个参数结构体 + 5 个函数指针原型。版本宏固定 2.0，主版本左移 4 位拼进 uint16_t（nvOpticalFlowCommon.h:L62-64）。
- **L03 CUDA 后端入口**（nvOpticalFlowCuda.h）：唯一入口 NvOFAPICreateInstanceCuda + 12 项函数指针表，把契约落到 CUDA 上下文，用 CUarray/CUdeviceptr/CUstream 扩展缓冲与流。

分层动机：同一契约供 CUDA/Vulkan/DirectX 多后端头平级复用，各后端只做"入口+后端类型+函数表"。

## 3. 核心链路

按 tour 十步串成主数据流：

1. **版本协商**：NvOFGetMaxSupportedApiVersion（nvOpticalFlowCommon.h:L545）——公共头唯一可直接链接的函数，返回值低 4 位次版本、其余主版本。
2. **拿函数表**：以 NV_OF_API_VERSION 为参调 NvOFAPICreateInstanceCuda（nvOpticalFlowCuda.h:L239）填充 12 项函数指针——全库只导出 2 个符号。
3. **建会话/定型**：nvCreateOpticalFlowCuda（vtable 第一项，nvOpticalFlowCuda.h:L214）后 nvOFInit（nvOpticalFlowCommon.h:L432）——NV_OF_INIT_PARAMS 一次定死宽高/网格/模式/档位。
4. **建缓冲**：按 NV_OF_BUFFER_DESCRIPTOR 分配输入/输出/提示/代价四类缓冲（nvOpticalFlowCuda.h:L153-154）。
5. **逐帧执行**：nvOFExecute（nvOpticalFlowCommon.h:L462）异步提交，输出按 outGridSize 网格填充；最后逐层 Destroy。

数据流本质：灰度 8bit/NV12/ABGR8 像素进 → 硬件引擎 → 每格一个 NV_OF_FLOW_VECTOR（int16 flowx/flowy，S10.5 定点，nvOpticalFlowCommon.h:L289-293）或 11.5 定点视差出。

## 4. 关键文件深读

### 4.1 nvOpticalFlowCommon.h（551 行，公共契约）

- **NV_OF_STATUS**（L79-145）：12 个错误码，排错第一手语义表。
- **NV_OF_CAPS**（L159-180）：10 项能力查询；GetCaps 两段式——先 NULL 拿个数再拿值（nvOpticalFlowCommon.h:L504-528）。
- **NV_OF_PERF_LEVEL**（L185-192）：SLOW=5/MEDIUM=10/FAST=20，慢档=最佳质量——名字是性能档、语义是质量档，最易记反。
- **NV_OF_INIT_PARAMS**（L311-327）：硬约束在字段注释：hintGridSize ≥ outGridSize（L318）、hPrivData 保留须置 NULL（L323）、Turing 上 disparityRange 必须 UNDEFINED（L324-325）。
- **NV_OF_EXECUTE_INPUT_PARAMS**（L370-391）：立体视差模式下两帧句柄变为校正后左/右视图（L372-375）；disableTemporalHints=1 供独立图像对——默认 0 时上帧结果自动作提示，连续视频提准、独立对反而劣化（L382-385）。
- **NV_OF_ROI_RECT**（L358-364）：对齐极苛——start_x/width 对齐 32*outGridSize、start_y 对齐 8*max(outGridSize,2)、最小 32x16（L350-356），ROI 外矢量无效。

### 4.2 nvOpticalFlowCuda.h（244 行，CUDA 后端）

- **NV_OF_CUDA_API_FUNCTION_LIST**（L212-226）：12 项 vtable——会话创建/Init/Execute/Destroy、缓冲全生命周期、SetIOCudaStreams、GetLastError/GetCaps；驱动与客户端二进制解耦的核心。
- **PFNNVOFSETIOCUDASTREAMS**（nvOpticalFlowCuda.h:L131）：输入/输出流让 CUDA 前后处理与 OF 引擎流水化；须在 Execute 前设置（L102-108）。
- **缓冲双形态**（L54-60）：同一句柄可取 CUARRAY 或 CUDEVICEPTR（L167/L180），取错返回 NULL/0。

### 4.3 README.md（18 行）

门槛、场景、完整 SDK 下载指引——"本仓不是完整 SDK"的唯一官方提示。

## 5. 模块间关系

最关键的 imports 边：nvOpticalFlowCuda.h:L41-42 依次 include nvOpticalFlowCommon.h 与 <cuda.h>——**集成方只包含 nvOpticalFlowCuda.h 即拉入全部契约**。README 以 documents 边覆盖两头。Common 头 fanIn=3/fanOut=10 是枢纽：结构体、枚举与 5 个函数指针类型（PFNNVOFINIT L432、PFNNVOFEXECUTE L462）全在此。

契约分层：公共头用中性类型（NvOFHandle、NV_OF_BUFFER_DESCRIPTOR），CUDA 头用 CUcontext/CUstream/CUarray/CUdeviceptr 具体化；函数表 12 项中 5 项指针类型直接复用公共头——Vulkan/DX 后端头可平级扩展的基础。依赖单向无环：Cuda 头 → Common 头 → <stdint.h>。

## 6. 构建与运行

**本仓没有可构建物**（无 CMakeLists/Makefile/源文件），集成姿势：
1. 两头拷入工程 include 路径并保证能找到 <cuda.h>（OpenCV 即这样消费）；
2. 链接完整 SDK 的 Optical Flow 库——只导出 2 个符号：NvOFGetMaxSupportedApiVersion（nvOpticalFlowCommon.h:L545）与 NvOFAPICreateInstanceCuda（nvOpticalFlowCuda.h:L239），其余 12 API 全走函数表；
3. 运行门槛同上（README.md:L14-15），无硬件时首调即 NV_OF_ERR_OF_NOT_AVAILABLE。

**测试**：零测试零示例；验证用法需下载完整 SDK（README.md:L17-18）。

## 7. 设计决策与取舍（含勘误）

**决策**：①**vtable+工厂**——只导出 2 符号，12 API 经函数表分发，驱动与客户端二进制解耦，版本协商前置；②**输出按网格不按像素**——输出/提示缓冲宽高以网格为单位（nvOpticalFlowCommon.h:L337-341），省显存但单位易踩坑。

**勘误**（文档 vs 源码，均逐行核实）：
1. 【勘误】nvOpticalFlowCommon.h:L35 声称用 #pragma 单字节打包结构体，grep 核实**全仓 #pragma 指令 0 条**（唯一命中即此注释）——承诺不存在。
2. 【勘误】nvOpticalFlowCuda.h:L88-89 文档参数名 cuContext，签名实为 CUcontext device（nvOpticalFlowCuda.h:L99）。
3. 【勘误】nvOpticalFlowCuda.h:L141 引用类型 ::NV_OF_CREATE_BUFFER 全仓不存在，实际是 NV_OF_BUFFER_DESCRIPTOR（nvOpticalFlowCuda.h:L153-154）。
4. 【勘误】nvOpticalFlowCuda.h:L63 注释写 \struct NV_BUFFER_STRIDE，实际名 NV_OF_BUFFER_STRIDE（nvOpticalFlowCuda.h:L66）。
5. 【勘误】NV_OF_ROI_RECT 是全文件唯一不走 typedef struct _X {...} X 范式的结构体（nvOpticalFlowCommon.h:L358 直接 struct 声明无 typedef），而 L390 却以 NV_OF_ROI_RECT* 使用——纯 C 下缺 typedef 支撑会编译失败（C++ 合法；静读结论，未编译验证）。
6. 【勘误】PFN 命名不一致：nvOpticalFlowCuda.h:L195 PFNVOFGPUBUFFERGETSTRIDEINFO（单 N），同表其余均 PFNNVOF*（双 N）。
7. 【勘误·小】README.md:L18 "illustarting" 拼写错；两头 \date 标 2018 而版权行 2020。

## 8. 新人上路

**先看**（按序）：①README 全文；②Common 头枚举区（nvOpticalFlowCommon.h:L79-280）——错误码→能力→档位→网格→模式→缓冲；③NV_OF_INIT_PARAMS 与两组 EXECUTE_PARAMS（nvOpticalFlowCommon.h:L311-406）；④CUDA 头函数表（nvOpticalFlowCuda.h:L212-226）与第 3 节链路对号入座。

**再改**：本仓的"改"只有两种——跟随上游同步版本宏与结构体，或修注释。字段顺序即二进制布局，按旧头编译的消费方不会重编译。

**常见坑**：hintGridSize 忘了 ≥ outGridSize（nvOpticalFlowCommon.h:L318）；hPrivData/padding 没置零（nvOpticalFlowCommon.h:L386-388）；输出缓冲宽高按像素填（应为网格单位，nvOpticalFlowCommon.h:L337-341）；独立图像对忘 disableTemporalHints=1（nvOpticalFlowCommon.h:L382-385）；用 Legacy 32-bit UINT cost 格式（计划弃用应改 UINT8，nvOpticalFlowCommon.h:L263-267）；Turing 卡给 disparityRange 设非 UNDEFINED（nvOpticalFlowCommon.h:L324-325）；ROI 不对齐硬规则（nvOpticalFlowCommon.h:L350-356）。

**心法**：把两个头当"驱动 ABI 的纸面快照"读——注释里每处 Must/should 都是运行期断言的预告。
