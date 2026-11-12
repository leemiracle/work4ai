# DLSS SDK 分发仓 Onboarding（NVIDIA/DLSS，310.9.1）

## 1. 仓库定位：SDK 分发仓，不是算法源码仓

NVIDIA/DLSS 是 RTX DLSS SDK 的官方公开分发仓，git log 单提交即 `DLSS 310.9.1 SDK`。它不含任何 DLSS 神经网络的实现代码：`README.md:2` 自述"Public repo for NVIDIA RTX DLSS SDK"，`README.md:3` 明言 DLSS Sample App 只随 GitHub release 发布（不在仓内）。仓内只有三类资产：`include/` 23 个 C/C++ 头文件（全部 API 契约）、`lib/` 68 个预编译二进制（约 1.31GB）、`utils/` 8 个排障工具。理解这一点后阅读预期就对了——本仓读的是"接口设计与分发工程"，而非模型。

`NVIDIAImageScaling/` 目录本地为空：`.gitmodules:2-3` 声明它是指向 NVIDIAGameWorks/NVIDIAImageScaling 的子模块，`README.md:10`/`README.md:14` 给出两种拉取命令。NIS（空间放大+锐化）与 DLSS（时序超分）互补：前者跨平台无 RTX 依赖、后者要 RTX 硬件。许可上 `LICENSE.txt:1` 是 RTX SDKs 统一专有许可（覆盖 DLSS/NGX/RTXGI 等），头文件 SPDX 均标 `LicenseRef-NvidiaProprietary`（如 `include/nvsdk_ngx_defs.h:3`），与 NIS 的宽松许可不同源，混用须分清。

## 2. 目录地图与文件计数

- `include/`（23 头）：按后缀分五族——`nvsdk_ngx.h`/`nvsdk_ngx_vk.h` 门面（D3D11/12/CUDA 与 Vulkan）、`*_defs*` 4 件类型契约、`*_params*` 3 件参数结构、loader+standalone 3 件动态加载、`*_helpers*` 10 件参数打包器（含两个 deprecated 转发桩）。
- `lib/`（68 件）：Linux 两架构各 7、`Windows_x86_64` 34、`Windows_aarch64`/`Windows_arm64ec` 各 10。
- `doc/`（6 PDF+1 zip，被 .understandignore 的 `*.pdf` 裁掉不入图谱）：DLSS/FG/RR 三本编程指南+RTX UI 指南——深度集成第一手资料。
- `utils/`（8 件）：7 个成对 .reg 注册表开关 + 1 个 jitter 调试说明。

## 3. 核心架构：五层头文件契约栈

全仓 import 图（44 条边）呈清晰分层，自底向上：

1. **defs 层（契约根）**：`include/nvsdk_ngx_defs.h`（859 行）被其余 22 个头中的大半依赖。API 版本 `NVSDK_NGX_VERSION_API_MACRO=0x0000015`（`include/nvsdk_ngx_defs.h:56`，1.5.0）；结果码族 `NVSDK_NGX_Result`（`:96-178`，Success=0x1、Fail=0xBAD00000 起 18 个失败码）；成败判定用 `0xFFF00000` 掩码宏（`:183-184`）；特性枚举 `NVSDK_NGX_Feature`（`:186-237`）里 SuperSampling=1（`:190`）、DeepResolve=10、FrameGeneration=11、DeepDVC=12、RayReconstruction=13（`:208-214`）。近 200 个参数键字符串宏在 `:647-853`，其中只读 EParameter 用 `"#\xNN"` 魔法串（`:572-645`）。Vulkan 补充契约在 `include/nvsdk_ngx_defs_vk.h:93-100`（`NVSDK_NGX_Resource_VK`：VkImageView/VkBuffer 二态 union+ReadWrite）。
2. **params 层**：`include/nvsdk_ngx_params.h:52-74` 定义 C++ 纯虚 `NVSDK_NGX_Parameter` 键值总线（Set/Get 各 8 类型重载+Reset），`:79-110` 给 C 侧 `NVSDK_NGX_Parameter_SetULL` 等自由函数——同一对象两种语言面。
3. **门面层**：`include/nvsdk_ngx.h` 头部 `:13-67` 的 HOW TO USE 注释就是七步集成手册（Init→GetCapabilityParameters→Set→GetScratchBufferSize→CreateFeature→EvaluateFeature→Release/Shutdown）；`include/nvsdk_ngx_vk.h:114` 的 `NVSDK_NGX_VULKAN_RequiredExtensions` 做 Vulkan 扩展预检，`:172-174` Init 家族（Ext2 显式 GIPA/GDPA）。
4. **loader/standalone 层**：`include/nvsdk_ngx_loader.h:69` 起的 `NVSDK_NGX_HEADER_ONLY` 实现块负责找 NGX Core；`include/nvsdk_ngx_standalone_common.h:107-123` 的 `NVSDK_NGX_DEFINE_API` 宏生成函数指针表结构体。
5. **helpers 层**：static inline 参数打包器，把结构体逐键 Set 成键值对，见第 5 节。

## 4. 关键机制一：NGX Core 发现链（loader.h）

链接期只链接薄壳，真身在驱动里。`include/nvsdk_ngx_loader.h:307-417` 的 `NGXLoadCoreLibrary` 按 Windows 五级降级找 `_nvngx.dll`：①应用目录（`:315-321`，注释记 471.11 驱动起改名 `_nvngx.dll`，ARM64 用 `_arm64_nvngx.dll`）②QueryAdapterInfo 查 D3DKMT 注册表（`:120-266`；`:192-194` 注释 OS 会少估缓冲区必须 malloc 超配）③`nvlddmkm\Parameters\NGXCore` ④`nvlddmkm\NGXCore`（`:357-361`）⑤legacy 全局键 `SOFTWARE\NVIDIA Corporation\Global\NGXCore`（`:363-368`，注释点名 Proton/Wine 依赖此键"不要删"，附 Valve wine commit 链接）。Linux 侧极简：`:65` 定义 `NGX_CORE_LIBRARY_NAME "libnvidia-ngx.so.1"`，`:405-416` 直接 dlopen 全局搜索路径。这套降级链是 Linux Steam Proton 跑 DLSS 游戏能工作的契约基础。

## 5. 关键机制二：helpers 参数打包与 deprecated 桩甄别

helpers 家族把"填近 60 个键"压缩成一个结构体调用：`include/nvsdk_ngx_helpers_d3d.h:103-167` 的 `NGX_D3D11_EVALUATE_DLSS_EXT` 单次展开 58 个 Set；D3D12 版在 `:297-361`。两个细节：`:117-118`/`:161-162` 的 `x==0.0f?1.0f:x` 三目给 MV scale/曝光参数静默兜底；`include/nvsdk_ngx_helpers.h:65-114` 的 `NGX_DLSS_GET_OPTIMAL_SETTINGS` 经 `DLSSOptimalSettingsCallback` 回调问驱动最优渲染分辨率，`:104-107` 老驱动无动态 min/max 键时回退最优值。

两个 17 行文件是陷阱指示牌：`include/nvsdk_ngx_helpers_dlssd.h:15` 与 `include/nvsdk_ngx_helpers_dlssg.h:15` 均 `#pragma message` 声明 deprecated（改 include `_d3d` 版），`:17` 转发。这是 2026 年从单头拆成 per-API 子族留下的兼容壳——见到告警直接换 include 即可。版权年佐证代际：主族头多为 2019-2023，dlssd/dlssg 子族与 standalone/loader 为 2026。

## 6. 三大特性族的后端矩阵

DLSS-SR（超分）、DLSS-RR（光线重建，dlssd）、DLSS-FG（帧生成，dlssg）三族的输入面各不相同，但 API 骨架一致（Create→Evaluate）：

- **RR**：`include/nvsdk_ngx_defs_dlssd.h:17-33` 三模式枚举（Denoise/Roughness/Depth，区分 hardware depth）；创建参数 `include/nvsdk_ngx_params_dlssd.h:19-33`；helpers 四件（d3d 主实现 `include/nvsdk_ngx_helpers_dlssd_d3d.h:117`/`:418` 双 API 结构、cuda `:130`/`:150`、vk `:131`）。
- **FG**：`include/nvsdk_ngx_defs_dlssg.h:32-46` ResourceFlags（输入位 1<<0..7、输出位 1<<24..26 分开编址）；`include/nvsdk_ngx_params_dlssg.h:41-136` 的 Opt_Eval_Params 含五个 4×4 相机矩阵（`:52-60`）与 11 组 subrect；D3D12 独占主实现 `include/nvsdk_ngx_helpers_dlssg_d3d.h:46-63`，显存预估 `:197`。**FG 无 CUDA 后端**（helpers_dlssg 无 _cuda 文件）——帧生成必须活在呈现队列上，子族文件布局即后端支持矩阵。
- CUDA 路径专用通道：`include/nvsdk_ngx.h:171` 的 `NVSDK_NGX_CUDA_Init1` 收 `NVSDK_NGX_CUDADevice`（`include/nvsdk_ngx_defs.h:272-276`，CUcontext+CUstream，多线程多实例必需）。

## 7. 二进制矩阵与集成模式

68 个库的命名律（任务清单若写"74"系笔误，盘上实证 68）：

- **动态库（特性三胞胎）**：`nvngx_dlss.dll`/`nvngx_dlssd.dll`/`nvngx_dlssg.dll`（Windows）与 `libnvidia-ngx-{dlss,dlssd,dlssg}.so.310.9.1`（Linux），各分 `dev/`（带调试信息，Linux dev 版单文件可达 60MB）与 `rel/`——可选的"随应用分发"特性库，运行时仍经 loader.h 发现链加载。
- **静态库（薄壳）**：Windows `nvsdk_ngx_{d,s}{,_dbg,_iterator0,_iterator1}.lib`（d/s=动态/静态 CRT，dbg/iterator 为调试迭代器级别变体；`lib/Windows_x86_64/x64/` 十件全），另有 vs2010/2012/2013 老工具集、khr、uwp 变体目录；Linux `libnvsdk_ngx.a` 同为薄壳。
- **header-only 模式**：定义 `NVSDK_NGX_HEADER_ONLY` 后 `include/nvsdk_ngx.h:705-710` 自动拉入 loader+standalone_cuda，实现 inline 编进应用免链接 .lib。standalone CUDA 头降级逻辑见 `include/nvsdk_ngx_standalone_cuda.h:74-97`（Init_Ext 缺失但应用传了 PathListInfo 则 FAIL_OutOfDate，`:89-94`）与 `:116-117`（Init1 不降级）。

## 8. 上手路径与常见坑

**建议阅读序**：`README.md` → `include/nvsdk_ngx.h:13-67`（HOW TO USE）→ `include/nvsdk_ngx_defs.h`（类型宇宙）→ `include/nvsdk_ngx_helpers_d3d.h`（参数打包实例）→ doc/ 三本 PDF（SR/FG/RR 编程指南）。图谱 tour 14 步即按此线设计。

**常见坑**：
1. 非线程安全——`include/nvsdk_ngx.h:18-19` 明言，多线程须客户端自锁或走 CUDA_Init1 多实例。
2. D3D11 传 deferred context 会报错（`include/nvsdk_ngx.h:515-518` 要求 immediate context）；D3D12 command list 须 open/recording 且非 copy 队列（`:508-513`）。
3. `NVSDK_NGX_GetParameters` 已废弃（`include/nvsdk_ngx.h:286`），但驱动 ≤445 时它又是唯一回退（`:318-322`）。
4. 老驱动探路：`NVSDK_NGX_GetFeatureRequirements` 可在 Init 前调用（`:598`），standalone 版还会零 LUID 惰性加载库（`include/nvsdk_ngx_standalone_cuda.h:183-197`）。
5. 日志双层：`utils/ngx_log_on.reg:4` 的 LogLevel 是驱动级全局开关，`include/nvsdk_ngx_defs.h:818-823` 的 Overlay/Indicator 参数族是逐次 Evaluate 级。
6. jitter 接错是 SR 画质问题头号来源：`utils/DLSS_Debug_Jitter_Configs.txt:5` 的 CTRL+ALT+F9 热键可运行时循环变换 jitter，F10 交换 XY（`:7`）。
7. clone 后 NIS 目录为空不是 bug；doc/ 的 PDF 才是 SR/FG/RR 参数表的权威出处，头文件注释只是摘要。

（图谱：102 节点/44 边，10 层/14 步 tour；本文行号锚均经源码核实 @310.9.1。）
