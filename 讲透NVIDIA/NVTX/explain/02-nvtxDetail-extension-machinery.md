# 02 · nvtxDetail：五态扩展槽位与宏生成的实现机制

## 角色定位
`c/include/nvtx3/nvtxDetail/` 是 NVTX"声明在前、注入在后"架构的实现层：主头声明 API，这里决定每次调用到底发生什么——工具已注入则转发工具实现，未注入则降级为空操作。磁盘上 21 个头文件（图谱仅收录 4 个，见仓库 README 勘误），承担扩展协议、加载协议、类型桥三层职责。

## 内部结构
骨架头 `nvtxExtImpl.h`（123 行）定义扩展机制的核心常量：**五态槽位状态机** `NVTX_EXTENSION_FRESH:94`（未初始化）→ `NVTX_EXTENSION_STARTING:96`（初始化中，防重入）→ `NVTX_EXTENSION_LOADED:97`（成功）/`NVTX_EXTENSION_INIT_FN_FAILED:98`（工具初始化函数失败）→ `NVTX_EXTENSION_DISABLED:95`（禁用）；全局结构 `nvtxExtGlobals1_t:101-104` 经 `NVTX_LINKONCE_DEFINE_GLOBAL:106` 保证每个扩展槽跨翻译单元唯一（配套平台头按 Windows/POSIX/Android 分支选 linkonce 实现）。

三个领域实现头与骨架同构：`nvtxExtImplCounters_v1.h`（166 行）、`nvtxExtImplMem_v1.h`（168 行）、`nvtxExtImplPayload_v1.h`（265 行，额外引入 `nvtxExtPayloadTypeInfo.h` 处理类型信息）。它们用 `NVTX_EXT_IMPL` 宏族以函数名为参数展开生成实现体：每个 API 函数三段式——init 桩（首次调用触发加载探测）→ 已加载则跳转工具函数表 → 未加载则空操作返回。

真正的加载协议在图谱未收录的头部：`nvtxInit.h`（499 行）/`nvtxInitDefs.h`（595 行）定义注入库探测与函数表提取；`nvtxImplCore.h`（432 行）+`nvtxImpl.h`（464 行）实现核心 API 的跳转；`nvtxTypes.h`（318 行）做类型桥；`nvtxLinkOnce.h`（88 行）是跨平台唯一性保证。

## 外部连接
上游：`nvToolsExt.h` 末尾（约 `nvToolsExt.h:1681-1686`）在 `NVTX_IMPL_GUARD` 保护下引入 `nvtxDetail/nvtxTypes.h` 与 `nvtxDetail/nvtxImpl.h`——这保证用户不能绕过主头直接 include 实现头。下游：Payload 语义槽被 `nvToolsExtCounters.h`（311 行）的计数器 API 复用（`nvtxCounterRegister/Sample*/BatchSubmit` 依托语义槽传递计数元数据）；Mem 扩展同样经 `nvtxExtImplMem_v1.h` 接入。测试侧 `tests/src/PrintInjection.h:33/44/60` 按 `SUPPORT_DYNAMIC_INJECTION`/`SUPPORT_PREINJECTION`/`SUPPORT_STATIC_INJECTION` 三宏分模式导出注入函数，验证的就是这套加载协议；导出面由 `tests/src/UseExportedApi.cpp:50` 的 X-macro 守护（`nm -D` 自动生成配方注释在 `UseExportedApi.cpp:55`），宏展开正确性由 `tests/src/PayloadEntriesHelper.h:31-32` 的 `NVTX_DEFINE_STRUCT_WITH_SCHEMA`+`NVTX_PAYLOAD_ENTRIES` 变体族逐字段核对。

## 数据流
以 `nvtxCounterSampleInt64` 为例：首次调用 → 宏展开的 init 桩置槽位 STARTING → 尝试发现注入工具（环境变量/已加载模块的导出表）→ 找到则调工具的模块初始化函数（成功置 LOADED，失败置 INIT_FN_FAILED）→ LOADED 后该槽位所有后续调用直接跳转工具函数指针；任何失败态都收敛为空操作，对宿主程序零影响。

## 设计决策
- **宏生成而非手写实现体**：三个 _v1 头的函数体全部由宏族展开，换来协议一致性——代价是静态分析工具提取出 0 个函数实体（本仓图谱实测，属预期而非缺陷）。
- **槽位状态机而非布尔标志**：STARTING 态防多线程重入，INIT_FN_FAILED 与 DISABLED 区分"工具拒绝"与"环境不可用"，避免每次调用重复探测。
- **版本化目录隔离**（_v1 后缀）：扩展协议升级时新增 _v2 头并行存在，老工具按版本号自选。

## 新人提示
读这套机制的顺序：先 `nvtxExtImpl.h:94-106`（状态机+全局结构）再挑 `nvtxExtImplCounters_v1.h` 通读宏展开（166 行最短）。调试"标注没出现在 Nsight 里"的问题时，记住降级路径有三种收敛（无工具/DISABLED/INIT_FN_FAILED），注入库初始化函数返回非零就是第三种。改宏族时必须跑 `tests/src/PayloadEntriesHelperC.c`/`PayloadEntriesHelperCpp.cpp` 双翻译单元验证（C/C++ 展开一致性是硬约束）。
