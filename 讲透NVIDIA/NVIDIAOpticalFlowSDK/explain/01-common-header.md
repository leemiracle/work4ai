# 01 · nvOpticalFlowCommon.h — NVOFA 跨设备公共契约

> 本文行号锚均指 nvOpticalFlowCommon.h；涉其他文件处用全名标注。

## 1. 角色定位

NVOFA 是 Turing 及以后 GPU 内置的硬件光流/立体视差引擎，独立于图形与 CUDA 核工作（README）。本文件是它的 C API"宪法"层：CUDA/Vulkan/DirectX 全部后端共享的枚举、参数结构体与函数指针原型都在这 552 行里定义。本仓库仅有的两个头中，它承载全部数据模型，nvOpticalFlowCuda.h 只是把契约绑定到 CUDA 上下文。对上它定义客户端可见的会话/缓冲/执行参数，对下规定驱动必须实现的五类函数指针形状。API 版本宏固定 2.0（L62-64）。

## 2. 内部结构

四段式布局：平台适配、11 个枚举、8 个结构体、5 个函数指针原型加 1 个真函数。

- 平台适配：L42-55 MSVC 的 stdint 兜底分支（实为死代码，见勘误 2）；L57-61 定义 NVOFAPI，Windows 上展开为 __stdcall；L62-64 版本宏 NV_OF_API_VERSION=(2<<4)|0=0x20；L65 MIN_ERROR_STRING_SIZE=80。
- 不透明句柄：L72-74 前向声明 NvOFHandle/NvOFGPUBufferHandle/NvOFPrivDataHandle，实现细节全部藏在驱动侧。
- 枚举群：NV_OF_STATUS 共 12 个错误码（L79-145）；NV_OF_CAPS 10 项能力查询（L159-180）；NV_OF_PERF_LEVEL 性能档位 SLOW=5/MEDIUM=10/FAST=20（L185-192）；输出网格 1/2/4（L198-205）与提示网格 1/2/4/8（L211-219）；NV_OF_MODE 光流/立体视差二选一（L229-235）；缓冲用途四种（L241-250）；缓冲格式八种（L255-269，其中 32 位 UINT 代价格式被官方自述低效且计划弃用，L263-266）；视差范围 128/256（L274-280，仅 Turing 之后 GPU）。
- 结构体：NV_OF_FLOW_VECTOR 的 flowx/flowy 各 int16_t S10.5 定点（L289-293）；NV_OF_STEREO_DISPARITY 为 uint16_t 的 11.5 定点（L302-305）；NV_OF_INIT_PARAMS 会话参数（L311-327）；NV_OF_BUFFER_DESCRIPTOR（L333-344）；NV_OF_ROI_RECT 是无 typedef 的裸 struct（L358-364）；NV_OF_EXECUTE_INPUT_PARAMS（L370-391）；NV_OF_EXECUTE_OUTPUT_PARAMS（L397-406）。
- 函数指针原型：PFNNVOFINIT（L432）、PFNNVOFEXECUTE（L462，异步语义见其注释 L437-439）、PFNNVOFDESTROY（L479）、PFNNVOFGETLASTERROR（L501）、PFNNVOFGETCAPS（L528）；以及全文件唯一不经函数指针表、可直接链接的真函数 NvOFGetMaxSupportedApiVersion（L545）。

## 3. 外部连接

被 nvOpticalFlowCuda.h:41 include——本仓库唯一消费者；Vulkan/DirectX 后端头在完整 SDK 下载包中扮演相同角色。自身仅依赖 <stdint.h>（L54），纯契约零实现。绝大多数调用不走符号链接：客户端持有函数指针表（装配点在 nvOpticalFlowCuda.h:212-226），本头只定义指针形状；唯一直连导出符号是 L545 的版本查询。C++ 客户端由 extern "C" 包裹（L67-70），保证名字不被改编。

## 4. 数据流

一次会话的数据流全部由本头结构体承载：建实例（CUDA 侧入口）→ nvOFGetCaps 两段式查能力（L528：capsVal 先传 NULL 探数量、再传数组取值）→ NV_OF_INIT_PARAMS 定型会话（L311-327，width/height 以像素计）→ 按 NV_OF_BUFFER_DESCRIPTOR 建 GPU 缓冲（L333-344；输出/提示缓冲宽高以网格数计）→ 每帧填 NV_OF_EXECUTE_INPUT_PARAMS（inputFrame/referenceFrame/可选 externalHints/disableTemporalHints，L370-391）调 nvOFExecute → 硬件按 outGridSize 网格逐格写出 S10.5 光流（1 符号位+10 整数位+5 小数位，格式说明 L286-288）或 11.5 视差到 NV_OF_EXECUTE_OUTPUT_PARAMS::outputBuffer（L397-406）→ nvOFDestroy 释放。错误路径：NV_OF_STATUS 返回码加 nvOFGetLastError 取至少 80 字符描述串（L501/L65）。

## 5. 设计决策（含勘误）

- 【勘误 1】L35 头注释声称 "uses #pragma directives to pack structure members with one byte alignment"，但 grep 实证全文件零 #pragma 指令——"pragma" 一词只在注释本身出现。结构体实际按编译器默认对齐布局；若信注释、按单字节对齐假设做二进制读写或跨编译器传结构体会踩坑，疑为历史版本残留。
- 【勘误 2】L42 写 `#if defined(_MSC_VER_) && (_MSC_VER_ < 1600)`，宏名多打尾部下划线（MSVC 定义的是 _MSC_VER），因此 L44-51 的整数类型兜底 typedef 永不激活，任何编译器都走 L54 的 #include <stdint.h>。
- S10.5/11.5 定点是 NVOFA ASIC 原生输出格式：下游把 int16 除以 32 得像素位移；定点直通硬件、零转换开销，这是选定点而非浮点的原因。
- perfLevel 枚举值 5/10/20 刻意不连续（L188-190），给驱动分级调度留插值空间，客户端勿对其做算术假设。
- 输出/提示缓冲宽高以网格为单位、输入以像素为单位（L338-341）：同名字段两种量纲，免客户端除法，但也是最容易传错的地方。
- padding/padding2 显式占位（L386/388）加 hPrivData 保留字段（L323/387/405）保 ABI 布局稳定；NV_OF_BOOL 用 enum 模拟（L150-154，NV_OF_TRUE = !NV_OF_FALSE）求 C89 兼容。

## 6. 新人提示

- 改此头等于改 ABI：新字段只能追加在结构体尾部并同步升版本宏（L62-63）；它是 NVIDIA 官方 SDK 头，应当只读对待。集成时 include nvOpticalFlowCuda.h 即自动拉入，勿重复定义其中的类型。
- 调用顺序是硬约束：Execute 前必须 Init 成功，否则 NV_OF_ERR_NOT_INITIALIZED（L134）；对互相独立的图像对务必 disableTemporalHints=1（L382-385）——默认 0 时前帧光流自动当作当前帧提示，对无时域关联的输入反而劣化质量。
- 代价缓冲优先 8 位 NV_OF_BUFFER_FORMAT_UINT8，32 位 UINT 官方自述低效且计划弃用（L263-267）。
- 解码量纲：flowx/flowy 除以 32.0 才是像素位移；视差为无符号 11.5（无负值）。Turing 上 disparityRange 必须置 UNDEFINED（L324-325）；hintGridSize 须大于等于 outGridSize（L316-318）。
