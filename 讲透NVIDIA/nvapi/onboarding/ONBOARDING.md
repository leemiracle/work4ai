# 讲透 nvapi：NVAPI SDK 开源发行面 Onboarding

> 仓库：`NVIDIA/nvapi` @ commit `70d337db`（2026-09 版头文件族）｜图谱 97 节点/172 边/4 层/5 步导览，fingerprints 35 文件
> 本文所有 `file:line` 锚均为主会话对源码逐一核实的结果（2026-11-09）。

## 一、这个仓库是什么：头文件即 SDK

NVAPI 是 NVIDIA 在 Windows 平台访问 GPU/驱动专有能力的 C 接口层——显示拓扑、G-SYNC、SLI、3D Stereo、驱动 profile、D3D 扩展设备创建等，这些超出 DirectX/OpenGL 标准面的能力全部从这里出去。本仓库**不是 NVAPI 的实现**，而是它的公开开源发行面：README.md 第一段说得直白——仓库含 headers、interface definitions 与四个架构的 import library，而 "The actual NVAPI implementation is provided by the NVIDIA GPU driver installed on the system"。换言之：**头文件 + .lib 存根在这里，实体在显卡驱动里**。

这个形态决定了仓库的一切特点：

- 全仓 35 个被图谱收录的文件里，唯一超过 2.5k 行的文本是 `nvapi.h`（26124 行）——它是纯声明头，没有任何函数体；
- 四个目录 `x86/ amd64/ aarch64/ arm64ec/` 各放一个 `.lib`（439838 / 999686 / 840896 / 1102180 字节），链接器拿它们解析符号，运行时再绑到驱动提供的 nvapi.dll；
- `docs/` 放 R615 驱动代的官方参考手册 `R615-NVAP-Reference-OpenSource.chm`（6.37MB）与 `R615-NVAPI-OpenSource-Release-Notes.pdf`（170KB）——CHM 与头文件同代发布，是接口语义的权威补充；
- 许可是 MIT（License.txt 带 SPDX 标注），但 README 结尾明言 "This project is currently not accepting contributions"——不开贡献是政策而非疏漏。

一句话定位：**读这个仓库 = 读 NVAPI 的 ABI 契约**。理解了"声明在此、实体在驱动"这一点，后面所有设计都顺理成章。

## 二、分层全景：四层地图

图谱把 35 个文件划成 4 层：

| 层 | 内容 | 代表文件（锚） |
|---|---|---|
| L01 核心 API 头（11 文件） | nvapi.h 全量声明、接口 ID 总表、lite 子族、驱动设置 ID | `nvapi.h`、`nvapi_interface.h:30`、`nvapi_lite_common.h`、`NvApiDriverSettings.h:158` |
| L02 HLSL 扩展（3 文件） | 着色器侧 intrinsic 三件套 | `nvHLSLExtns.h`、`nvHLSLExtnsInternal.h:32`、`nvShaderExtnEnums.h:40` |
| L03 示例代码（14 文件） | 七组可编译 Windows 样例 | `Sample_Code/i2c/i2c.cpp:301`、`Sample_Code/Sync_Configuration/Sync_Configuration.cpp:301` |
| L04 平台库与文档（7 文件） | 四架构 .lib + CHM + 许可 | `amd64/nvapi64.lib`、`docs/R615-NVAP-Reference-OpenSource.chm` |

依赖关系极简单：nvapi.h 处于扇入中心（fanIn 9），所有示例与 HLSL 头都汇聚到它；L04 的二进制是叶子。整个仓库没有构建系统——示例是 Visual Studio 工程形态（stdafx.h/targetver.h 预编译头套装，见 `Sample_Code/DisplayColorControl/targetver.h`），SDK 本身"拷头文件+链 .lib"即用。

## 三、接口发现机制：QueryInterface 魔数总表

NVAPI 不走 Windows 传统 dll 导出表，而是**单入口 + 按 ID 取函数指针**：先拿 `NvAPI_QueryInterface`，再用 32 位魔数 ID 换取每个真实函数的地址。魔数总表就在 `nvapi_interface.h`：

- 表本体 `nvapi_interface_table[]` 从 `nvapi_interface.h:30` 开始，实测 **522 个条目**，每行形如 `{ "NvAPI_Initialize", 0x0150e828 }`（`nvapi_interface.h:32`）；
- 表尾是最新代际的接口：NGX（`NvAPI_NGX_GetDriverFeatureSupport`）、利用率采样注册（`NvAPI_GPU_ClientRegisterForUtilizationSampleUpdates`）与 RISE 三件套 `NvAPI_RegisterRiseCallback / NvAPI_RequestRise / NvAPI_UninstallRise`（`nvapi_interface.h:551-553`）——RISE/NGX 出现在表尾，说明这张表与新驱动特性同步生长；
- 该文件仅 556 行、纯数据表初始化，无任何函数——第三方语言绑定（Python/Rust 的 nvapi 封装）普遍直接消费这张表。

与它配套的是"先初始化"约定：`nvapi.h:73` 的注释写明 "It is now mandatory to call NvAPI_Initialize before calling any other NvAPI"（声明在 `nvapi.h:87`），`NvAPI_Unload`（`nvapi.h:117`）须成对调用——但下文会看到，示例代码几乎都只初始化不卸载，唯一例外连初始化都不做。

四架构 .lib 的意义在此机制下特别清楚：存根库只为链接期提供 `NvAPI_QueryInterface` 等入口符号；ARM64EC 版（`arm64ec/nvapia64ec.lib`，1102180 字节，四架构中最大）服务 Windows on ARM 的 x64 兼容进程——NVAPI 对 WoW/EC 场景是一等公民。

## 四、nvapi.h 26k 行的拼接术：lite 子族与 SAL 卫生对

`nvapi.h`（26124 行）不是一口气写完的：头部 `nvapi.h:38-43` 依次 include 六个 `nvapi_lite_*` 头（salstart→common→sli→surround→stereo→d3dext），文件尾部再 include `nvapi_lite_salend.h` 收尾。lite 子族是按专题拆出的轻量头，可单独包含：

- `nvapi_lite_common.h`（674 行）是类型基座：`NvU32` 的 typedef 按 GCC/Clang/MSVC 多分支展开（`nvapi_lite_common.h:71` 与 `nvapi_lite_common.h:86-97`），`NvAPI_Status` 枚举在 `nvapi_lite_common.h:264`；最常用接口也在这里——`NvAPI_GPU_GetMemoryInfo`（`nvapi_lite_common.h:538`，**R520 起废弃**，`nvapi_lite_common.h:519` 注释与 `nvapi_lite_common.h:537` 编译器废弃标注直指继任者 `NvAPI_GPU_GetMemoryInfoEx` 在 `nvapi_lite_common.h:600`）、`NvAPI_EnumPhysicalGPUs`（`nvapi_lite_common.h:633`）；
- `nvapi_lite_d3dext.h` 提供 `NvAPI_D3D11_CreateDevice`（`:84`）等 D3D11 扩展入口——feature level 协商式设备创建是它的招牌能力；
- `nvapi_lite_sli.h` 的 `NvAPI_D3D_GetCurrentSLIState`（`:92`）与 `nvapi_lite_stereo.h`（21 个 Stereo 接口，`grep NVAPI_INTERFACE NvAPI_Stereo` 实测 21 条）、`nvapi_lite_surround.h`（Surround 视口布局）各自成专题。

**SAL 卫生对**是这个头文件族最精巧的工程细节：`nvapi_lite_salstart.h`（813 行）为各家编译器把 `__in/__out/__ecount` 等 SAL 标注定义为空宏（`nvapi_lite_salstart.h:41` 起），`nvapi_lite_salend.h`（809 行）在翻译单元末尾把这些宏逐个 `#undef`（`nvapi_lite_salend.h:29-37` 起）——保证包含 nvapi 头之后用户的宏命名空间不被污染。结构对齐则由 `nvapi.h:47` 的 `#pragma pack(push,8)` 统一（尾部 pop 配对），D3D 接口段另有两处 `pack(push,4)` 特例（`nvapi.h:14629,15242`）。注意：**pragma pack 在 nvapi.h 里而不在 salstart**——图谱摘要把这条记到了 salstart 头上，README 勘误第 6 条有记。

## 五、GPU 侧两套扩展：HLSL 三件套与驱动设置 ID

### HLSL Shader Extensions（L02 三件套）

DirectCompute/HLSL 侧的扩展是"假 UAV 通信槽"协议：

1. `nvHLSLExtnsInternal.h:32` 定义 256 字节通信槽结构 `NvShaderExtnStruct`（`nvHLSLExtnsInternal.h:50` 注释明示 struct size: 256 bytes），`nvHLSLExtnsInternal.h:68` 声明假 UAV `RWStructuredBuffer<NvShaderExtnStruct> g_NvidiaExt`——应用须先 `#define NV_SHADER_EXTN_SLOT u7` 选一个空闲槽位（`nvHLSLExtnsInternal.h:55-58` 的示例注释）；
2. 应用侧只该用 `nvHLSLExtns.h`（2578 行，按返回类型扫描实测 **175 个顶层导出**）：warp shuffle、FP16/FP32/UINT64 原子、VPRS 着色率属性求值、纹理 footprint、wave multi-prefix 扫描、光线追踪 micro-triangle 求交等。导出按**重载簇**组织——`NvEvaluateAttributeAtSampleForVPRS` 一名 12 个重载、`NvInterlocked*Fp16x2` 一簇 8 个；
3. 内部封包层 `nvHLSLExtnsInternal.h`（955 行，29 个 `__Nv*` 内部函数）里，`__NvReferenceUAVForOp` 有 **28 个重载**——每种 UAV 类型一版，是扩展调用协议的统一报文组装入口；
4. opcode 编号全部在 `nvShaderExtnEnums.h`（179 行，74 个 `#define NV_EXTN_OP_*`），`NV_SHADER_EXTN_VERSION`=1（`:40`）、`NV_WARP_SIZE`=32（`:45`）。该头 HLSL 与 C++ 双端共享；调用前应经 `NvAPI_D3D1x_IsNvShaderExtnOpCodeSupported` 逐 opcode 探测支持性。

### 驱动设置 ID（profile 体系）

`NvApiDriverSettings.h`（1459 行）+ `NvApiDriverSettings.c`（1209 行）定义 NVIDIA profile 的可编程面。注意结构：**设置 ID 主体不是宏**——`#define` 仅 139 个（几乎全是 `*_STRING` 宽字符串名，如 `OGL_AA_LINE_GAMMA_STRING` 在 `:29`），真正的 ID 在 `enum ESetting`（`:158` 起，129 个 `*_ID` 条目，首个 `OGL_AA_LINE_GAMMA_ID = 0x2089BF6C` 在 `:159`），合法取值在 117 个 `enum EValues_*`（首例 `:293`）。配套 `.c` 文件是 234 个 `g_values*` 数组，供 profile 编辑工具枚举每个设置的合法值域与 min/max。

## 六、示例代码走读：七个样例的调用面

`Sample_Code/` 七组样例由浅入深覆盖典型用法：

| 样例 | 规模 | 主线 API（锚） |
|---|---|---|
| GPUHandleEnumeration | 101 行 C | `main` 在 `gpuHandleEnumeration.c:45`；`NvAPI_SYS_GetLogicalGPUs` 在 `gpuHandleEnumeration.c:65`、`GetPhysicalGPUs` 在 `gpuHandleEnumeration.c:86` |
| DisplayColorControl | 41+217 行 | `NVHelper.cpp:40` Initialize_NVAPI、`NVHelper.cpp:57` GetGPUs、`NVHelper.cpp:72` GetConnectedDisplays、`NVHelper.cpp:192` NvAPI_Disp_ColorControl |
| i2c | 448 行 | DDC/CI 校验 `i2c.cpp:227`、VCP 亮度码 `0x10` 报文 `{0x82,0x01,0x10,0xAC}` 在 `i2c.cpp:255`、读改亮度流程 `i2c.cpp:301`、校验和 `i2c.cpp:177` |
| CustomTiming | 267 行 | `_tmain` 在 `CustomTiming.cpp:57`，Try→Save→Revert 三段式在 `CustomTiming.cpp:168`（ApplyCustomDisplay） |
| DisplayConfiguration | 446 行 | 路径枚举与 SetDisplayConfig 全流程（`DisplayConfiguration.cpp` 446 行） |
| QSYNC_Event_Registration | 139 行 | `_tmain` 在 `QSYNC_Event_Registration.cpp:48`、回调注册 `QSYNC_Event_Registration.cpp:75`、事件处理 `HandleQSYNCEvent` 在 `QSYNC_Event_Registration.cpp:114`（Win10+/R460+） |
| Sync_Configuration | 434 行 | 参数查询 `Sync_Configuration.cpp:67`、同步状态 `Sync_Configuration.cpp:113`、三层拓扑 `Sync_Configuration.cpp:166`、CLI 分派 `main` 在 `Sync_Configuration.cpp:301` |

两个值得记住的甄别结论（图谱批阶段笔记 + 主会话复核）：其一，`Sync_Configuration.cpp` **全文 0 次调用 NvAPI_Initialize**（grep 实证），是七样例中唯一假定调用方已完成初始化的——照抄它做模板会踩坑；其二，`QSYNC_Event_Registration.cpp:1` 的 `stdafx.h` 引用指向仓外文件（悬空 include），编译该样例需自备预编译头。另外示例普遍"只初始化不 Unload"，与头文件"成对调用"的教导不一致——示例代码的工程卫生不代表最佳实践。

## 七、使用方式、设计决策与新人路线

**怎么用**：把仓库根的头文件加进 include path、按目标架构链对应 .lib（x86→`x86/nvapi.lib`，x64→`amd64/nvapi64.lib`，ARM64→`aarch64/nvapia64.lib`，ARM64EC→`arm64ec/nvapia64ec.lib`）。运行时要求装了 NVIDIA 驱动；接口可用性用 `NvAPI_Initialize` 后各查询接口的返回码判断，HLSL 扩展用 opcode 探测接口逐个确认（见第五节）。

**三个关键设计决策**：

1. **单入口 + 魔数 ID 取指针**（第三节）换来的是：驱动可以按版本裁剪实体、ABI 完全由 ID 表稳定、四架构只是链接存根差异——代价是调试器里看不到常规导出表；
2. **声明头拼接 + SAL 卫生对**（第四节）让 26k 行巨头的可维护性靠 lite 子族分解，同时把"包含 nvapi 头"对用户编译环境的侵入压到零；
3. **开源发行面 vs 闭源实体**的边界划在头文件：所有"能做什么"在此可见，所有"怎么做"在驱动里。CHM 手册承担语义细节，R615 版与当前头同代。

**新人上手路线**（对应图谱 5 步导览）：README→`nvapi.h` 头部 100 行（初始化约定 + lite 拼接）→`nvapi_interface.h` 通读魔数表（556 行，半小时能翻完）→跑 GPUHandleEnumeration 样例建立手感→按需深入：显示栈读 i2c/CustomTiming，G-SYNC 读 Sync 系列，计算方向读 HLSL 三件套（从 `nvShaderExtnEnums.h` 的 opcode 清单入手最顺）。做 profile 工具则直接进 `NvApiDriverSettings.h` 的 ESetting/EValues 双层枚举。

**三个必踩的坑**：忘记 Initialize（或照抄 Sync_Configuration 模板）；用了 `NvAPI_GPU_GetMemoryInfo`（R520 已废弃，换 `GetMemoryInfoEx`）；HLSL 扩展没做 opcode 支持性探测就直接发指令。
