# 06 loader.h + standalone 双头：NGX Core 发现链与 CUDA 函数指针引导

## 角色定位

三个 2026 版权的头（图谱 L05 层）构成 header-only 集成模式的运行时引擎：`include/nvsdk_ngx_loader.h` 负责"找到并加载 NGX Core 库"（Windows 五级降级 + Linux dlopen）；`include/nvsdk_ngx_standalone_common.h` 是宏工厂，批量生成任意后端的函数指针表、引导函数、转发桩；`include/nvsdk_ngx_standalone_cuda.h` 用这套宏落地 CUDA 后端。三者全包在 `#if defined(NVSDK_NGX_HEADER_ONLY)` 里（loader.h:69、standalone_common.h:16、standalone_cuda.h:16），由 nvsdk_ngx.h:705-710 自动串联。

## 内部结构

**平台抽象**（`include/nvsdk_ngx_loader.h:49-67`）：Windows 用 HMODULE/FARPROC，POSIX 用 void*/dlsym；`:65` 定义 `NGX_CORE_LIBRARY_NAME "libnvidia-ngx.so.1"`。`:269-305` 的 GetSymbol/LoadLibrary 双平台各一对（Linux 走 `dlopen(RTLD_NOW)`，`:298`）。

**五级发现链 `NGXLoadCoreLibrary`**（`include/nvsdk_ngx_loader.h:307-417`）：①exe 同目录试 `_arm64_nvngx.dll`（ARM64）或 `_nvngx.dll`→`nvngx.dll`（`:315-321`，注释记 471.11 驱动起改名史）；②`NGXGetPathUsingQAI`（`:120-266`）动态 LoadLibrary gdi32.dll 取 D3DKMTEnumAdapters2/QueryAdapterInfo（`:127-139`），按 LUID 匹配适配器（`:180-187`）后查 `Parameters\NGXCore\NGXPath` 与 `NGXCore\NGXPath` 两键（`:198-201`）——`:192-194` 注释揭示 OS 会少估所需空间，必须 malloc 超配缓冲；③④nvlddmkm 服务两级注册表（`:357-361`）；⑤legacy `SOFTWARE\NVIDIA Corporation\Global\NGXCore` 的 FullPath（`:363-368`）——注释郑重声明"Do not remove! Proton/Wine 依赖此键"并附 ValveSoftware wine commit 链接：Linux 玩 Windows 游戏的 DLSS 就靠这条兜底。Linux 分支极简：`:405-416` 直接 dlopen 全局搜索。

**宏工厂**（`include/nvsdk_ngx_standalone_common.h`）：`NGX_FOREACH` 成对迭代宏链（`:41-84`，FE_2..FE_40+NARGS 计数，最多 20 对）实现"宏版 for-each"；`NVSDK_NGX_DEFINE_API`（`:107-123`）生成 API 结构体（每函数一个成员）+ Context 全局态 + 递归互斥锁；`NVSDK_NGX_DEFINE_INIT_COMMON`（`:140-168`）生成 Init_Common：判已初始化→`NGXLoadCoreLibrary`→`NGX_FOREACH(NGX_PFNS_GETSYMBOL)` 批量 dlsym 绑指针→失败返回 FAIL_FeatureNotSupported；`NVSDK_NGX_DEFINE_WRAPPER`（`:174-182`）生成判空转发桩（未初始化→NotInitialized、指针空→OutOfDate）。`:198-234` 的 `NGXProgressCallbackHelper` 用线程局部存储把 C 风格回调（bool*）桥接成内部 bool& 签名。

**CUDA 落地**（`include/nvsdk_ngx_standalone_cuda.h:26-41` 十六个 PFN 类型）：`:43-49` `CUDA_IS_INITED` 判活宏（六组函数按"或"容错）；`:51-67` CUDA_FNS 清单（Init 族用 CORE_CUDA 命名空间对齐 Core 导出名，其余 CUDA）；`:71-72` 两行宏展开全部骨架。手写部分处理精细降级：Init 无 Init_Ext 时若应用传了非空 PathListInfo 则 FAIL_OutOfDate（`:89-94`，老驱动不认搜索路径列表）；Init1 不降级（`:116-117` 注释：多线程支持就是它的存在意义）；Shutdown1 用 outNDevicesLeft 计数归零才重置 Context（`:140-164`）；GetFeatureRequirements 惰性加载（`:183-197`，零 LUID+按需 dlsym，注释对齐官方 nvsdk_ngx_cuda_lib.cpp:420-441 实现）。

## 外部连接

上游仅依赖 defs.h；被 nvsdk_ngx.h 的 HEADER_ONLY 尾部拉起，与 lib/ 薄壳静态库互为替代（同一引导逻辑的 inline 版）。loader 的注册表键与 utils/ 七个 .reg 写的 `HKLM\SOFTWARE\NVIDIA Corporation\Global\NGXCore` 同源——那组开关就是第五级发现键所在 hive 的调试配置。

## 数据流（header-only 首次调用）

`NVSDK_NGX_CUDA_EvaluateFeature` → WRAPPER 判 Context 活 → 首次经 Init_Common：LoadCoreLibrary（五级链）→ 16 个 dlsym → 之后调用直飞函数指针。每 API 入口 `NGXLock lock(g_sdkLibMutexCUDA)`（如 `:76`/`:101`）串行化引导期，但 nvsdk_ngx.h:18 的"非线程安全"声明仍生效。

## 设计决策

1. **宏生成而非手写 16 遍**：三件套宏把后端差异压进一份 CUDA_FNS 清单，加新后端只换清单——代码生成器思路在头文件里的极致运用。
2. **降级矩阵精细区分**：能降则降（Init→老签名）、不能降则 OutOfDate 明示（Init1/PathListInfo 场景）——把驱动能力探测编码进每个分支。
3. **递归互斥锁**（standalone_common.h:19）：允许同线程重入，避免自锁。

## 新人提示

排障：加载失败先开 `utils/ngx_log_verbose.reg` 的 LogLevel 看 loader 日志（发现链每步有 NGX_LOADER_LOG 埋点，宏在 loader.h:36-42）；Linux 查 `ldconfig -p | grep ngx`；Proton/Wine 盯第五级注册表键。读宏代码从 CUDA_FNS 清单入手逆推展开结果，别硬读 NGX_FOREACH 链。
