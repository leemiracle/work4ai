# 讲透 nvidia-ipmi-oem（NVIDIA/nvidia-ipmi-oem）

> NVIDIA IPMI OEM support library——OpenBMC ipmid 插件（C++23），一个代码库服务 DGX/BlueField/Grace 三平台带外管理。
> 本地仓：`/usr-data/data2/repos/agent-repos/NVIDIA/nvidia-ipmi-oem`（commit dba74af0，2026-11 同步）。

## 流水线状态

| 步骤 | 状态 | 产物 |
| --- | --- | --- |
| DeepWiki 全量抓取 | ✅ 既有 | `deepwiki/`（25 页结构化内容，wiki_full.md 242KB） |
| understand 图谱 | ✅ 2026-11-09 | 仓内 `.understand-anything/knowledge-graph.json`：**357 节点/605 边/8 层/10 步 tour**，fingerprints 43 文件基线@dba74af0 |
| onboarding | ✅ 2026-11-09 | `onboarding/ONBOARDING.md`（6240 非空白字符 8 节 43 唯一行号锚，全锚界内终验） |
| explain | ✅ 2026-11-09 | `explain/` 2 篇：01 DGX OEM 命令面（2959 字/28 锚）、02 安全与敏感命令线（3674 字/26 锚） |

## 口径说明

字数=不计空格总字符；行号锚写入前经 `sed -n`/`grep -n` 对源码逐条核实（本轮批量校验 90 项、修 29 处漂移后全绿）。

## 源码级实证勘误（vs DeepWiki 快照/图谱论断/直觉认知）

1. **DeepWiki 核心命令函数名系捏造**：`ipmiOemSetNvBootstrapAccount`/`ipmiOemGpuSmbpbiPassThru`/`ipmiOemSetNvLivefish`/`ipmiOemNvPowerCapCmd`/`ipmiOemSetNvDhcp`/`ipmiOemNvSetFanPwm`/`ipmiOemGetPsuPresent` 全仓 grep **零命中**（论断出处 deepwiki/wiki_full.md:99,105,140-146）；真实名为 `ipmiGetBootStrapAccount`（`Grace/src/ghoemcommands.cpp:1751`）、`ipmiSMBPBIPassthroughCmd`（:186）、`ipmicmdEnterLiveFish`（`src/BF/oemcommands.cpp:573`）、`ipmiOemPsuPower`（`src/oemcommands.cpp:2872`）、`ipmiSetFanZonePWMDuty`（:1436）。
2. **SMBPBI "直通 I2C" 论断双重错误**：DeepWiki 表格"GPU Management | Grace | Direct I2C passthrough"（deepwiki/wiki_full.md:146）——真实现走 D-Bus `xyz.openbmc_project.GpuMgr` 的 `Passthrough` 方法（`Grace/src/ghoemcommands.cpp:234-236` 方法调用+`Passthrough`）非直连 I2C；且 BF 共用核心里的 `ipmiSMBPBIPassthroughCmdBF`（`src/BF/oemcommands.cpp:703-713`）是拒绝桩（"unsupported in Spectre / Bluefield 2/3"），Grace 注册还要 `ENABLE_SMBPBI_PASSTHRU==1`（`Grace/src/ghoemcommands.cpp:2957-2976`）。
3. **commandutils.hpp "统一注册模式"不成立**（图谱 L03/T03 论断）：`ipmiPrintAndRegister`（`include/commandutils.hpp:57`）在全仓 src/Grace **零引用**；实际注册全走 `ipmi::registerHandler`/`registerGroupHandler`（DGX 50 处/BF 59 处/GH 37 处 grep 实证）。
4. **白名单"安全第一道闸"名不符实**（图谱 T02 论断）：`ipmi-whitelist.conf` 仅一行注释零条目（`ipmi-whitelist.conf:1`），`generate-whitelist.py` 生成的头**无任何仓内源文件 include**（grep 零命中）——该机制属上游 phosphor-host-ipmid，本仓只带生成器与空模板。
5. **SBMR 错误日志名不符实**：`"supported only in SSIF interface"`（`src/sbmr-bootprogress.cpp:57`）实际判定接受 smbusV20+systemInterface+oem 三种 medium（:51-56）——日志口径窄于代码；DeepWiki "SSIF/System Interface Only"（deepwiki/wiki_full.md:4871）也漏了 oem。
6. **BF "共用核心 40+ 命令"口径需打折**（图谱 L06）：`src/BF/oemcommands.cpp` 有 30 处 "unsupported in" 拒绝桩（:694-759 连片），风扇/BIOS POST/SMBPBI 在 BF2/BF3/Spectre 上全部 ccResponseError——文件大半是占位桩而非实现。
7. **"BF 是 DGX 裁剪"直觉反了**（CMake 实证）：BF2/BF3/Spectre 构建的 `znvipmioemcmds` **不含** `common_library_sources`（storage/sensor，`CMakeLists.txt:208-213`），却**全量编入 DGX 核心** `src/oemcommands.cpp`（:137-152 各组合均含）——BF 构建=DGX 全量+BF 附加−传感器/存储。
8. **README 单行**（`README.md:1`）：仓内知识载体实为 commit message（如 1266083 对 BIOS 密码通道修复的完整根因分析）与 CMake 注释，DeepWiki 若引申 README 之外的"文档"需警惕。

## 附：与 KCCL/NCCL 轮的可比锚经验

本仓两篇 explain 的"上下文短锚"（`:N` 指代本节主文件）占锚总量 2/3，抽验时须按篇主题归位（zoo 轮钉版口径）；README 勘误第 1/2 条为 DeepWiki 捏造级错误，引用该 wiki 的函数名前务必回源码 grep。
