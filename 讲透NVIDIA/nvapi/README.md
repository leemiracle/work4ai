# 讲透 NVIDIA/nvapi（NVAPI SDK 开源发行面）

| 产物 | 状态 | 位置 |
|---|---|---|
| DeepWiki | ✅ 12/12 页 TRUE_100（2026-10-26 抓取） | [deepwiki/](deepwiki/) |
| understand 图谱 | ✅ 97 节点 / 172 边 / 4 层 / 5 步导览，0 issues，fingerprints 35 文件 @ `70d337db` | 仓内 `.understand-anything/knowledge-graph.json` |
| ONBOARDING | ✅ 7 节 | [onboarding/ONBOARDING.md](onboarding/ONBOARDING.md) |
| explain | ✅ 2 篇 | [explain/01-nvapi-h与接口发现机制.md](explain/01-nvapi-h与接口发现机制.md) ｜ [explain/02-HLSL扩展三件套.md](explain/02-HLSL扩展三件套.md) |

仓库一句话：**NVAPI 的"头文件即 SDK"开源发行面**——nvapi.h（26124 行纯声明）+ QueryInterface 魔数总表（522 条）+ 四架构 .lib 存根 + R615 CHM 手册；实体由 GPU 驱动提供。Windows 显示栈（G-SYNC/Stereo/Surround）、D3D 扩展、HLSL 扩展 intrinsic、驱动 profile ID 体系的 ABI 契约全部在此。

## 勘误清单（源码实证，2026-11-09 核实）

1. **驱动设置 ID 不是"上千个宏"**：图谱 L01 摘要称 NvApiDriverSettings.h "定义 OGL_AA_LINE_GAMMA 等上千个设置 ID 宏、宏密度极高"。实测 `#define` 仅 **139 个**且几乎全是 `*_STRING` 宽字符串名（`NvApiDriverSettings.h:29`）；设置 ID 主体在 `enum ESetting`（`:158` 起，**129 个 `*_ID`**，首例 `:159` `OGL_AA_LINE_GAMMA_ID = 0x2089BF6C`），合法值在 **117 个 `enum EValues_*`**（首例 `:293`）。"宏"口径完全失真，正确叙事是"枚举双层 + 字符串名宏"。
2. **Sync_Configuration 示例不调用 NvAPI_Initialize**：`Sample_Code/Sync_Configuration/Sync_Configuration.cpp`（434 行）grep `NvAPI_Initialize` **0 命中**——七样例中唯一假定调用方已初始化者。把它当模板抄会踩"未初始化"坑；其余样例的标准范式见 `NVHelper.cpp:40`。
3. **HLSL 扩展导出数 173 ≠ 实测 175，且"个数"本身不是稳定口径**：按返回类型扫描 `nvHLSLExtns.h` 顶层定义为 175 个；更本质的是导出按重载簇组织（`NvEvaluateAttributeAtSampleForVPRS` ×12、`__NvReferenceUAVForOp` 28 个 UAV 重载），图谱按簇建代表节点才是正确建模。引用数字时须注明口径。
4. **nvapi_lite_salstart.h 不打 pragma pack**：图谱摘要称 salstart "打开始终配对的 `#pragma pack(push,8)`"。实测 salstart（813 行）内零 pragma pack；`pack(push,8)` 在 **nvapi.h:47**（尾部 pop 配对），另有 D3D 段 `pack(push,4)` 特例两处（`nvapi.h:14629,15242`）。salstart/salend 对只负责 SAL 宏的 define/undef 卫生。
5. **docs/ 不止 CHM**：图谱 L04 描述只列 `R615-NVAP-Reference-OpenSource.chm`（6.37MB），实际还有 `R615-NVAPI-OpenSource-Release-Notes.pdf`（170412 字节）——同代发行说明，是接口变更的一手材料。
6. **GetMemoryInfo 已废弃（R520 起）**：`nvapi_lite_common.h:519` 注释与 `:537` 编译器废弃标注明示改用 `GetMemoryInfoEx`（`:600`）。旧教程/旧代码大量仍引 `GetMemoryInfo`（`:538`），迁移时注意 Ex 版结构 `NV_GPU_MEMORY_INFO_EX` 按内存段细分。
7. **QSYNC 回调函数行号越界（图谱数据错误）**：图谱节点 `HandleQSYNCEvent` lineRange 记 [114,140]，但该文件仅 **139 行**（实测定义在 `QSYNC_Event_Registration.cpp:114` 起）。同文件 `stdafx.h` 为悬空引用（指向仓外文件），样例编译需自备预编译头。
8. **"接口数"两种口径不可混用**：`nvapi.h` 内 `NVAPI_INTERFACE NvAPI` 声明实测 **488 条**，`nvapi_interface.h` 魔数表实测 **522 条**（含 lite 头声明接口与条件编译差异）。引用"数百个接口"时应说明取自哪张口径。

## 本目录导航

- 想懂 ABI 与魔数机制 → onboarding 第三、七节 + explain 01；
- 想懂 GPU intrinsic 通道 → explain 02（256B 通信槽协议）；
- 想跑样例 → onboarding 第六节表格（七个样例的主线 API 锚）；
- 图谱方法注记：本仓为纯声明头重灾区——tree-sitter 对 nvapi.h/nvapi_interface.h/NvApiDriverSettings.c 零提取，函数/类型节点大量来自批阶段手扫（NOTES-DIGEST 22 条有全记录），引用图谱行号前建议按本文锚复核。
