# 02 · nvOpticalFlowCuda.h — CUDA 后端唯一入口与 12 项函数表

> 本文行号锚均指 nvOpticalFlowCuda.h；涉 nvOpticalFlowCommon.h 处用全名标注。

## 1. 角色定位

本文件是 NVOFA（Turing+ GPU 硬件光流/立体视差引擎）C API 的 CUDA 后端绑定层：把 nvOpticalFlowCommon.h 定义的跨设备契约落到具体 CUDA 上下文。全文件只做三件事——定义 CUDA 侧扩展类型（缓冲类型/stride 结构）、给出 7 个 CUDA 专属函数指针的签名、声明唯一入口 NvOFAPICreateInstanceCuda（L239）。设计哲学是"构造即绑定"：客户端调用一次入口函数，驱动把 12 个实现指针填进 NV_OF_CUDA_API_FUNCTION_LIST（L212-226），此后一切调用都走这张函数表，驱动与客户端二进制完全解耦。本仓库不含实现（实现在 NVIDIA 驱动里），这个头就是客户端与驱动之间的全部接口边界。

## 2. 内部结构

- 依赖：L41 include nvOpticalFlowCommon.h（拉入全部公共契约）；L42 include <cuda.h>（引 CUcontext/CUstream/CUarray/CUdeviceptr 四个 driver-API 类型）；L43 定义 MAX_NUM_PLANES=3（NV12 最多三平面）。
- CUDA 扩展类型：NV_OF_CUDA_BUFFER_TYPE 的 CUARRAY/CUDEVICEPTR 二选一（L54-60）；NV_OF_BUFFER_STRIDE 逐平面横竖 stride 字节数（L66-70）；NV_OF_CUDA_BUFFER_STRIDE_INFO 为 stride 数组加平面数（L76-80）。
- 7 个函数指针 typedef：PFNNVCREATEOPTICALFLOWCUDA（L99，签名 `(CUcontext device, NvOFHandle *hOf)`）；PFNNVOFSETIOCUDASTREAMS（L131）；PFNNVOFCREATEGPUBUFFERCUDA（L153-154，bufferDesc+bufferType+hOfGpuBuffer 三参）；PFNNVOFGPUBUFFERGETCUARRAY 返回 CUarray（L167）；PFNNVOFGPUBUFFERGETCUDEVICEPTR 返回 CUdeviceptr（L180）；PFNVOFGPUBUFFERGETSTRIDEINFO 单 N 前缀孤例（L195，见勘误 2）；PFNNVOFDESTROYGPUBUFFERCUDA（L205）。
- 函数表本体：NV_OF_CUDA_API_FUNCTION_LIST（L212-226）恰好 12 个成员（L214-225）——会话四件套 nvCreateOpticalFlowCuda/nvOFInit/nvOFExecute/nvOFDestroy，缓冲五件套 nvOFCreateGPUBufferCuda/nvOFGPUBufferGetCUarray/nvOFGPUBufferGetCUdeviceptr/nvOFGPUBufferGetStrideInfo/nvOFDestroyGPUBufferCuda，流同步 nvOFSetIOCudaStreams，查询两件套 nvOFGetLastError/nvOFGetCaps。
- 入口声明：NvOFAPICreateInstanceCuda(uint32_t apiVer, NV_OF_CUDA_API_FUNCTION_LIST *functionList)（L239）。

## 3. 外部连接

上游：L41 对公共头的 include 是本仓库唯一 imports 边；<cuda.h> 要求客户端处在可链接 CUDA driver API 的环境。下游：链接期只需两个导出符号——本头的 NvOFAPICreateInstanceCuda（L239）与公共头的 NvOFGetMaxSupportedApiVersion（nvOpticalFlowCommon.h:545），实现在完整 SDK 的库/驱动组件中，本仓库不含。Vulkan/DirectX 后端（完整 SDK 包内）与本文件平行同构：各有自己的 CreateInstance 入口与缓冲类型扩展，公共契约零重复——这正是"公共头+后端头"两层分层的收益。

## 4. 数据流

九步标准调用序：①客户端自理 cuCtxCreate 建上下文 → ②NvOFAPICreateInstanceCuda(NV_OF_API_VERSION, &ofAPI)（L239）换得函数表 → ③nvCreateOpticalFlowCuda(cuCtx, &hOf) 建会话（L99）→ ④nvOFGetCaps 查支持的网格与宽高 → ⑤nvOFInit 定型会话 → ⑥nvOFCreateGPUBufferCuda 按 NV_OF_BUFFER_DESCRIPTOR+NV_OF_CUDA_BUFFER_TYPE 建 GPU 缓冲（L153-154），再用 GetCUarray/GetCUdeviceptr（L167/180）取原生句柄给自己的 CUDA kernel 读写 → ⑦可选 nvOFSetIOCudaStreams 把前/后处理 kernel 与 OF 引擎流水线化（L131，须在 Execute 前设，否则用默认流，L107-108）→ ⑧循环 nvOFExecute（契约见 nvOpticalFlowCommon.h:462）→ ⑨nvOFDestroyGPUBufferCuda（L205）加 nvOFDestroy 收尾。CPU 侧只提交参数，计算在 NVOFA ASIC 上异步执行（nvOpticalFlowCommon.h:437-439），与 CUDA 核完全并行。

## 5. 设计决策（含勘误）

- 【勘误 1】L88-89 文档注释写 `\param [in] cuContext — Should be set to cuda context created by Client`，但 L99 实际签名的参数名是 device（类型 CUcontext）。按文档找名为 cuContext 的形参会扑空；传参认类型不认名——第一参就是客户端创建好的 CUDA 上下文。
- 【勘误 2】L195 与函数表成员 L219 的 stride 查询指针前缀是 PFNVOF...（单 N），其余 11 个 typedef 全是 PFNNVOF...（双 N）：纯命名不一致，语义无碍，但用 PFNNVOF 通配 grep 函数指针会恰好漏掉它。
- 只导出一个 CreateInstance 符号而非 12 个 API 符号：驱动演进时可按 apiVer 填不同实现集，客户端二进制免重编；apiVer 传公共头的 NV_OF_API_VERSION 宏（nvOpticalFlowCommon.h:64），不匹配返回 NV_OF_ERR_INVALID_VERSION（L236）——与 NVENC/NVDEC SDK 同款手法。
- GetCUarray/GetCUdeviceptr 用返回值报告类型错误（错型返回 NULL/0，L165/178）而非走错误码：轻量查询不动状态机。
- 缓冲双形态覆盖两类下游：CUarray 服务纹理语义与多平面格式，CUdeviceptr 服务线性内存与 kernel 直写；stride 查询独立成 API（L195）而非建缓冲时一并返回，避免契约绑死驱动分配细节。

## 6. 新人提示

- 调用顺序是硬约束：CreateInstance → nvCreateOpticalFlowCuda → nvOFInit → 建缓冲 → Execute；漏 Init 吃 NV_OF_ERR_NOT_INITIALIZED（nvOpticalFlowCommon.h:134）。
- nvOFSetIOCudaStreams 必须在第一次 Execute 前调（L107-108）；不调也能跑，但 CUDA 前后处理与硬件引擎不流水线，吞吐打折。
- 用 GetCUarray 的前提是创建时 bufferType 选了 CUARRAY，否则返回 NULL（L165）；CUdeviceptr 同理返回 0（L178）。自写 kernel 访问输出缓冲必须按 GetStrideInfo 的 strideInfo 走（L195），勿假设紧密排列；光流分量还要除以 32 才是像素位移（S10.5，nvOpticalFlowCommon.h:286-288）。
- 函数表实例放栈或堆皆可，但生命周期须覆盖全部调用；表内指针是驱动填的，不可手动改写。版本协商两步走：先 NvOFGetMaxSupportedApiVersion（nvOpticalFlowCommon.h:545）比对编译头与驱动，再把 NV_OF_API_VERSION 传给 L239 入口，两关都过才继续。
- 本仓库只有头没有库：编译通过不等于能跑——链接与运行需完整 SDK、Turing+ GPU 与 Windows 445.87/Linux 450.51 以上驱动（README 门槛）。所有 \param 注释以实际签名为准（勘误 1 的 cuContext/device 只是最典型一处）。
