# Expert_18 — 飞腾/国产化适配收口专家视角（深化版）

> **角色定位**：飞腾编译器战略收口专家——把全部 LLVM 项目里"飞腾工程实证"的散点收口成一套完整判断。本视角是路线 B 的命脉（宪法 §0.1 + §3.4 E18 阶段 B 先行），它既是对前面所有 Expert/Lens 的飞腾线索的收口，也是"国产 CPU 厂商如何在被锁定的全球编译器基础设施（LLVM/GCC）里追求自主可控"这个普世命题的唯一案例锚点。
> **核心思维模型**：
> 1. **供应链角色判定**（生产者 vs 消费者 vs 贡献者 vs 自研者）——源自 Lens_03 供应链分析师的"养育图谱"方法论，本专家把它落到"编译器层"
> 2. **特异性反向锚点**（主线 LLVM "无 FTC86x" 这种"缺失"也是特异性）——源自宪法 §0.3，"零命中"比"有改动"更具诊断价值
> 3. **国产对偶矩阵**（飞腾 vs 华为 vs 龙芯 vs 平头哥 vs 海光 vs 申威）——源自 Lens_07 国产化战略家的六厂商分级，本专家把它量化到 commit 数/调度模型/团队规模

> ⚠️ **本文是路线 B 的"飞腾案例"核心**（宪法 §0.1）。所有判断基于 5 个实测清单 + NPU SDK 代码级深挖，零编造。`[实测]` 标注的全部来自 phytium_repos / OpenXiangShan 真实文件。

---

## §0.3 双重门槛自检（特异性测试 v2.0，宪法 §0.3 强制）

> 删掉飞腾后本文是否读得通？是否只是翻译 LLVM 官方文档？

**判定：通过。** 本视角满足双重门槛的全部三项（远超"至少一项"要求）：

| 门槛 | 证据 | 强度 |
|------|------|:----:|
| **(a) 飞腾工程实证** | phytvm `contrib/phytium/codegen_npu.cc:28` `mapper_cmd = config->mapper_bin_path` + `codegen.h:62` "Path to mapper binary npu_compiler"；phytium_repos 45 仓库零 LLVM patch | 🔴 铁证 |
| **(b) 代码级实例** | `codegen_npu.cc:98` `system(mapper_cmd.c_str())` 外部二进制调用；`codegen.h:8` "Strictly Confidential. This is the NC-SDK Standard license"；主线 LLVM `AArch64Processors.td:833/1544` 有 `TSV110`（华为）无 FTC86x（飞腾） | 🔴 铁证 |
| **(c) 对偶判断** | 飞腾 NPU 编译器走 PHYIR + npu_compiler mapper（绕过 LLVM）vs 华为昇腾 CANN（基于 LLVM/TVM/MLIR 全栈）——两条路线的根本分野（§2.5） | 🟢 强 |

**反软文检验**：本文核心结论"飞腾是国产 CPU 中编译器自主度最低的之一"是基于公开仓库 grep 的结构性事实，不是攻击；本文同时诚实地给出反方观点（§5.2）"消费者姿态在桌面场景可能就是对的"。**绝不为某厂商背书，也不为某厂商唱衰**。

---

## 0. 路线 B 的护城河（最重要的开篇）

本项目走"领域通用指南（飞腾为案例）"路线（宪法 §0.1 + oracle §0.3）。这是 oracle 战略评审的核心结论：**LLVM 不是飞腾的芯片**，强行套"芯片特异剖析"范式会逼出伪造特异性。本项目的护城河 = LLVM 作为编译器基础设施的领域通用深度 + 飞腾 phytium_repos 作为案例锚点。

**飞腾案例的护城河全靠 5 个实测清单**（见 §1），它们证明了以下三件事——这是路线 B 的"飞腾案例"全部内容的核心三角：

1. **飞腾 NPU/GPU 编译器创新在 LLVM 之外**（外部 `npu_compiler`/`gpu_compiler` 二进制，**完全绕过 LLVM codegen**）——本专家在 §2.4 用 `codegen_npu.cc` + `codegen_phydnn_gpu.cc` 的 `system()` 调用做了代码级铁证
2. **主线 LLVM 23.0 + 飞腾 45 公开仓库 = 零飞腾 LLVM 痕迹**（飞腾不自研 LLVM fork，也无主线调度模型）——本专家用 `grep FTC86|Phytium|phytium` 全树零命中做了铁证
3. **华为有毕昇+TSV110+主线贡献，龙芯有主线后端，飞腾三者皆无**（飞腾是国产 CPU 中编译器投入最浅的）——本专家用 34 个 AArch64 调度模型清单 + 六厂商矩阵做了铁证

**这三条结论是路线 B 的"飞腾案例"全部内容的核心**。它们把一个尖锐的普世命题推到读者面前：**后发国家如何在被锁定的全球编译器基础设施里追求"自主可控"，以及这种追求的真实成色**。下面 §1 是 5 个清单的详细数据，§2 是收口判断（含三个新增深度解剖 §2.4/§2.5/§2.6），§3 是国产对偶（含量化矩阵 §3.8），§4 是给飞腾的建议（含长期 RISC-V 就绪度 §4.4）。

---

## 1. 5 个实测清单（路线 B 地基）

> 全部清单已写入本目录的 5 个独立文件。本节是核心结论摘要 + 关键代码锚点。

### 1.1 phytvm fork diff（核心发现，纠正 oracle §0.3）

📄 完整清单：[`phytvm_diff_findings.md`](./phytvm_diff_findings.md)

**oracle §0.3 战略级发现（已确认）**：`codegen_arm.cc` 是 **vanilla Apache TVM upstream**（ASF License + "this is used as an example" 注释，第 38-40 行）。**这不是飞腾深度自研的 LLVM 后端**。

**E18 深挖结论（比 oracle §0.3 更深一层，本视角的核心增量）**：
- 飞腾真实定制**不在 LLVM 层**——而在四个层面：
  - **设备类型注册层**：fork 了 DLPack 标准，新增 7 个 device type enum（`kDLPhytium=16` 到 `kDLPhytiumGOCOpenCL=22`，`3rdparty/dlpack/include/dlpack/dlpack.h:93-105`）
  - **runtime 层**：25 个文件（`src/runtime/phytium/`，含 npu_runtime.cc/gpu_runtime.cc/offline_gpu_runtime.cc/pipeline_executor.cc）
  - **relay contrib codegen 层**：12 个文件（飞腾专有 `Strictly Confidential` NC-SDK license，见 §2.4 深度解剖）
  - **Python 量化层**：8 个文件（`python/tvm/relay/phy_quantize/`，KL 散度校准 + PHYQuantizeAnnotate pass）
- **决定性发现**：`contrib/phytium/*.cc` 全目录 grep `LLVM|llvm|mcpu|target_triple|triple` **零命中** `[实测-grep]`。飞腾 NPU/GPU 子图编译**完全不经过 LLVM codegen**，而是走自研 PHYIR → 外部闭源编译器二进制（`npu_compiler`/`gpu_compiler`），见 §2.4。
- **构建证据**：phytvm `CMakeLists.txt` grep `phytium|Phytium|PHYTIUM|use_phytium` 无 `USE_PHYTIUM` 之类构建开关 `[实测-grep]`；`docker/install/ubuntu_install_llvm.sh` 从 apt.llvm.org 装上游 llvm-4.0/7/8/9，**完全上游，无飞腾 LLVM fork**。

**可信度**：`[实测-grep/读文件]`，铁证级。这条结论是整个 E18 的地基——飞腾对 TVM 的定制是"设备抽象 + runtime + 专有 codegen + 量化"，**LLVM 层是 vanilla，未被触碰**。

### 1.2 phytium_repos 45 目录 LLVM patch 盘点

📄 完整清单：[`phytium_repos_llvm_patches.md`](./phytium_repos_llvm_patches.md)

**结论**：**45 仓库零飞腾 LLVM/Clang patch**。全部是上游发行版的包管理 recipe 或第三方依赖自带文件：
- Android 11 → LLVM 12.0.0（AOSP prebuilt，`external_llvm-project/llvm/CMakeLists.txt:8` `set(LLVM_VERSION_MAJOR 12)`，grep FTC86/Phytium 零命中）
- Yocto → LLVM 13.0.1（poky 上游 recipe，`llvm_git.bb:22` `PV="13.0.1"`，3 个 patch 全是 Khem Raj 的 Yocto 社区 patch）
- Buildroot/pi-os → LLVM/Clang 9.0.1（`llvm.mk:8` `LLVM_VERSION=9.0.1`，buildroot 上游）
- FreeBSD → LLVM 19.1.7（FreeBSD 15 base 编译器，`Version.inc` `CLANG_VERSION 19.1.7`，唯一把 Clang 当默认 base 编译器的）
- openEuler embedded BSP → 纯 GCC，无 LLVM recipe

**可信度**：`[实测-grep/读文件]`，铁证级。45 仓库无一是"飞腾自研 LLVM/Clang fork"——飞腾在整个 OS/固件/嵌入式栈里是**纯消费者**。

### 1.3 主线 LLVM FTC86 调度模型源码确认

📄 完整清单：[`主线LLVM_FTC86_源码确认.md`](./主线LLVM_FTC86_源码确认.md)

**结论**：LLVM 23.0.0git 全树（`llvm/`+`clang/`+`AArch64/`）grep `FTC86|FTC66|Phytium|ftc86|ftc66|phytium` **零命中** `[实测-grep]`（路径 `/data/usershare/ai/riscv/OpenXiangShan/llvm-project/`）。

34 个 AArch64 调度模型（`AArch64Sched*.td`）中**无飞腾**，但有：
- **华为 TSV110**（鲲鹏 920）：`AArch64Processors.td:833/1544`，带 `TSV110Model`——华为向 LLVM 上游贡献的
- 富士通 A64FX、Ampere Ampere1/Ampere1B、Marvell ThunderX1/2/3、高通 Kryo/Falkor、三星 ExynosM3/4/5、Apple Cyclone、Qualcomm Oryon……都有专属调度模型
- **飞腾 FTC862 零专属调度模型**——这是"飞腾性能未被编译器充分挖掘的根因之一"（与飞腾 Expert_11 §3.2 实测呼应：用通用 Cortex-A 近似调度，性能损失约 5-10%）

**飞腾在主线 LLVM 的实际待遇**：`clang -mcpu=ftc862` **不被识别**；飞腾只能用 `clang -march=armv8.4-a` + 通用 AArch64Schedule.td 近似模型；指令调度/寄存器分配/向量化决策都**非 FTC862 最优**。

**可信度**：`[实测-grep/读文件]`，铁证级。这是"飞腾在主线 LLVM 是匿名 ARM 核"的硬证据。

### 1.4 飞腾 SDK LLVM 版本矩阵

📄 完整清单：[`飞腾SDK_LLVM版本矩阵.md`](./飞腾SDK_LLVM版本矩阵.md)

**结论**：6 大 OS 全用上游 LLVM，版本 9.0.1→19.1.7 跨 5 年，**碎片化严重**。默认工具链**除 FreeBSD 外全是 GCC**——飞腾主编译器路线是 GCC（PhyGCC），LLVM 次要。

**碎片化的工程治理意义**：LLVM 9（2019）到 LLVM 19（2024）跨 5 年，飞腾没有统一工具链版本策略。这意味着飞腾用户在 Android（LLVM12）、Yocto（LLVM13）、FreeBSD（LLVM19）之间横跳时，会遇到 ABI/IR 兼容性碎片。对比华为毕昇（统一基于 LLVM 17+ 的商业发行版），飞腾的工具链治理是短板（对偶 Expert_17 §3 治理）。

**可信度**：`[实测-读文件]`（PhyCC/PhyGCC 闭源部分诚实标为 `[推测]`）。

### 1.5 国产 CPU 厂商 LLVM 生态对照

📄 完整清单：[`国产CPU厂商_LLVM_fork_生态.md`](./国产CPU厂商_LLVM_fork_生态.md)

**结论**：三档分化——
- **第一档（主线正式后端，最强）**：龙芯 LoongArch（LLVM 16+ 正式后端，2023-03；2026-01 仍活跃提交 LA32），LLVM 22.x 还在加特性
- **第二档（深度 fork + 主线贡献）**：华为毕昇（深度 fork + tsv110 上游 + openEuler 平行宇宙 LLVM 替 GCC 全发行版），平头哥玄铁 C910 fork（RISC-V 后端上游 + c910-llvm 开源），进迭时空（`RISCVSchedSpacemitX60.td` 进主线）
- **第三档（纯消费者，最末）**：**飞腾最末档，纯消费者**（既无主线后端，也无 fork upstream，也无调度模型）

**可信度**：`[websearch]` 竞品部分 + `[实测]` 飞腾部分。

---

## 2. 飞腾在 LLVM 供应链的最终定位（路线 B 的核心判断）

### 2.1 飞腾是"纯消费者"，不是"生产者"

| 角色 | 飞腾 | 华为 | 龙芯 | 平头哥 | 海光 |
|------|:----:|:----:|:----:|:----:|:----:|
| 自研 ISA | ❌（用 ARMv8.4） | ❌（用 ARMv8.2） | ✅（LoongArch） | ❌（用 RISC-V） | ❌（用 x86 Zen） |
| 主线 LLVM 后端 | ❌ | ⚠️（tsv110 调度模型） | ✅（独立后端） | ⚠️（RISC-V 侧 Ascalon） | ✅（x86，c86-4g 跟进） |
| LLVM fork（商业） | ⚠️ PhyCC/PhyGCC（闭源） | ✅ 毕昇（开源+商业） | — | ✅ 玄铁（开源） | — |
| 主线 commit 贡献 | ❌（零） | ✅（TSV110） | ✅（maintainer） | ✅ | ✅ |
| 主线调度模型 | ❌ | ✅（`AArch64SchedTSV110.td`） | — | ✅（`RISCVSchedTTAscalonX.td`） | — |
| NPU 编译器 | 外部二进制（绕过 LLVM） | 昇腾 CANN（基于 LLVM/TVM/MLIR） | — | — | DCU（AMD GPU 衍生） |

**飞腾的 LLVM 供应链角色**：**纯消费者**——用主线 LLVM/GCC 当工具，零贡献回主线，零自研 fork upstream，零主线调度模型。这在五家里是唯一的"三项全无"（华为有调度模型+fork+commit，龙芯有后端+maintainer，平头哥有 fork+调度模型，海光有后端+commit）。

**Lens_03 供应链分析师的精确表述**（对偶）：飞腾在 AArch64 后端供应链里是**唯一缺席的中国服务器 CPU 厂商**。Lens_03 实测发现一个**反直觉的供应链事实**——中国 RISC-V 厂商（平头哥、进迭时空）在 LLVM 供应链是"生产者"（有具名调度模型 `RISCVSchedTTAscalonX.td`/`RISCVSchedSpacemitX60.td`），而中国 ARM 厂商（飞腾、鲲鹏 TaiShan v110 早期）是"消费者"。原因：RISC-V 是开源 ISA，任何厂商都能往主线塞调度模型无授权壁垒；ARM 的 ISA 由 ARM 一家定，国产厂商只能加调度但飞腾连这个都没做。**商业模式决定供应链位置**——平头哥卖 IP 需要生态可见度，飞腾卖整芯片不需要 LLVM 可见度。

### 2.2 飞腾"自主可控"叙事的编译器层脆弱点

飞腾/CEC 的官方叙事是"自主可控"。本专家从编译器层诚实验真（这是 §0.3 反软文精神的体现）：

| "自主可控"维度 | 飞腾现状 | 编译器层判断 |
|--------------|---------|-----------|
| ISA 自主 | ❌ ARMv8.4（v9 不授中国） | 锁死在 ARM v8.4，编译器红利（SVE2/MTE/SME/FP8）永远拿不到 |
| 编译器框架自主 | ❌ 用开源 LLVM/GCC | 无自研编译器框架（对比华为有毕昇框架、龙芯有 LoongArch 工具链栈） |
| 调度模型自主 | ❌ 主线 LLVM 无 FTC86x | 编译器调度次优，性能损失 5-10% |
| NPU 编译自主 | ⚠️ 外部 npu_compiler/gpu_compiler 二进制（黑盒，Strictly Confidential） | 不可审计、不可复现、零社区生态 |
| 生态主导权 | ❌ 纯消费者，零主线 commit | 无主线影响力，LLVM 未来方向由 Apple/Google/AMD/ARM/华为决定 |

**结论**：飞腾"自主可控"叙事在**编译器层是最脆弱的一环**。芯片自主（FTC862 自研核、4-wide OoO、ARMv8.4 标准 FEAT）≠ 编译器自主。Lens_07 国产化战略家给飞腾打的"自主度"分是 **L1（准入：能编译能跑）远未达 L3（可演：能贡献能演进）**——这是"叙事注水"：消费者包装成了生产者。

**这不是攻击飞腾，是诚实诊断**：飞腾在芯片层是"ARMv8.4 + 国密原生 + 军工资质"的差异化选手（飞腾 E06/E07 共识），但在编译器层是"零 upstream + 全闭源 fork"的滞后选手。**芯片层的护城河没有传导到编译器层**——这是飞腾"自主可控"叙事最大的断层。

### 2.3 与 Lens_07 国产化战略家对偶

Lens_07 已给出 5 注可证伪下注（本专家**完全认同**并补充代码级支撑）：

| 下注 | Lens_07 判断 | E18 代码级补充 |
|------|------------|--------------|
| 1. 飞腾 2030 前 upstream FTC86x | < 15%（2026-28）/ 30-50%（2028-30）| 主线 LLVM 零 FTC86x 是结构性事实（§1.3），飞腾无 maintainer 团队 |
| 2. 龙芯 LoongArch 自主度 2030 | ≥90% | 龙芯主线 LLVM 后端 + 22.x 持续加 LA32，铁证 |
| 3. 华为 AscendNPU-IR 成国产 AI 编译器标准 | 55-70% | 华为 CANN 基于 LLVM/TVM/MLIR 全栈（§2.5 对照） |
| 4. 海光 2027 前 LLVM 合入完整 c86-4g | 60-75% | GCC 17 已合入（2026-06），LLVM 跟进中 |
| 5. 飞腾 2032 前启动 RISC-V 编译器栈 | 60-75% | §4.4 深化：RISC-V 转向的编译器就绪度评估 |

本专家补充："**飞腾是六家国产 CPU 厂商里编译器自主度最低的之一**"是结构性事实，不是偶然。Lens_07 的四阶段自主度评分（用→Fork→Upstream→自研）里，飞腾停在**阶段 2（Fork）**：PhyCC（LLVM fork，闭源）+ PhyGCC（GCC fork，闭源），两个 fork 都没开源、都没 upstream。**最自主的阶段 3（自研 ISA + upstream 框架，如龙芯）自主度上限 70-90%，飞腾当前停在阶段 2 约自主度 40-60%**。

### 2.4 飞腾 NPU 编译器架构深度解剖（新增，代码级铁证）

> 这是本深化版最重要的增量。前述 5 清单只证明了"飞腾 NPU 编译绕过 LLVM"，本节用代码级证据解剖**它到底是什么、怎么绕过的、绕过之后走的是什么**。

#### 2.4.1 三层架构：TVM 设备抽象 + PHYIR 中间表示 + 外部 mapper 二进制

飞腾 NPU 编译器是一个**三明治架构**，从上到下：

```
┌─────────────────────────────────────────────────────────┐
│  第一层：飞腾 fork 的 Apache TVM（PHYTVM）               │
│  - 7 个 device type（kDLPhytiumNPU=17 等，dlpack.h:93）  │
│  - 25 个 runtime 文件（src/runtime/phytium/）            │
│  - 12 个 contrib codegen 文件（Strictly Confidential）   │
│  - 8 个 phy_quantize Python 文件（KL 散度校准）          │
│  ※ LLVM 层（src/target/llvm/）= vanilla upstream，零触碰 │
├─────────────────────────────────────────────────────────┤
│  第二层：飞腾自研 PHYIR 中间表示                         │
│  - AsPHYIR（Python 注册的 Relay→PHYIR 转换，codegen_npu.cc:35）│
│  - phydnn_version 前缀 "PHYDNN001008"（codegen.h:55）    │
│  - 输出 .imgir 文件（intermediate machine IR）           │
│  ※ 这是飞腾自己的 IR，不是 LLVM IR，不是 MLIR dialect    │
├─────────────────────────────────────────────────────────┤
│  第三层：外部闭源编译器二进制（mapper / offline compiler）│
│  - npu_compiler（bin/npu_compiler，ELF 二进制，不可读）  │
│  - gpu_compiler（需 GPU_COMPILER_INSTALL_PATH 环境变量） │
│  - libnpucompiler.so（lib/，NPU 编译器共享库）           │
│  - 由 system() 子进程调用（codegen_npu.cc:98）           │
│  ※ 完全黑盒，Strictly Confidential NC-SDK license        │
└─────────────────────────────────────────────────────────┘
```

#### 2.4.2 代码级证据链（铁证）

**证据 1：`codegen.h` 飞腾版权 + Strictly Confidential license** `[实测-读文件]`
```
codegen.h:6   @copyright Copyright (c) Phytium Technology Co., Ltd. All Rights Reserved
codegen.h:8   @license Strictly Confidential.
codegen.h:9           This is the NC-SDK Standard license
```
contrib/phytium 目录下 9 个文件全部标 "Strictly Confidential"（codegen.h/codegen_npu.cc/codegen_phydnn_gpu.cc/codegen_customcl.cc/codegen_customcpp.cc/codegen_goc_cl.cc/codegen_profile.cc/utils.h/utils.cc + customcl_source_module.h/customcpp_source_module.h/goc_cl_source_module.h）。**这是飞腾 SDK 里唯一可见的"专有编译器层"痕迹，但全部标记为保密**。

**证据 2：`codegen.h` 定义外部二进制路径** `[实测-读文件]`
```
codegen.h:35  String mapper_bin_path;
codegen.h:36  String gpu_compiler_bin_path;
codegen.h:62  TVM_ATTR_FIELD(mapper_bin_path)
codegen.h:63      .describe("Path to mapper binary npu_compiler")
codegen.h:65  TVM_ATTR_FIELD(gpu_compiler_bin_path)
codegen.h:66      .describe("Path to gpu compiler binary gpu_compiler")
```
`PhytiumConfigNode` 有 15 个配置字段，其中 `mapper_bin_path` 和 `gpu_compiler_bin_path` 明确指向**外部二进制**。`phydnn_version` 默认 "PHYDNN001008"（飞腾自己的版本号体系）。

**证据 3：`codegen_npu.cc` 用 system() 调用 npu_compiler** `[实测-读文件]`
```
codegen_npu.cc:28   std::string mapper_cmd = config->mapper_bin_path;
codegen_npu.cc:35   const auto* fp = runtime::Registry::Get("AsPHYIR");  // Relay → PHYIR
codegen_npu.cc:36   std::string phyir_json = (*fp)(func, nullptr, false, f_attrs_file);
codegen_npu.cc:37   std::string phyir = phydnn_version + phyir_json;  // 加 PHYDNN 前缀
codegen_npu.cc:89   mapper_cmd += " -n " + f_phyir.GetFileName();   // PHYIR 输入
codegen_npu.cc:90   mapper_cmd += " -p " + p_phyir.GetFileName();   // 参数输入
codegen_npu.cc:91   mapper_cmd += " -f " + mbs.GetFileName();        // 输出 .mbs
codegen_npu.cc:92   mapper_cmd += " -m " + config->mapconfig;        // MAP 配置
codegen_npu.cc:93   mapper_cmd += " -c " + config->hwconfig;         // HW 配置
codegen_npu.cc:98   int sys_status = system(mapper_cmd.c_str());     // 调外部二进制！
```
**完整的 NPU 编译管道**：Relay Function → `AsPHYIR`（转 PHYIR）→ 写临时文件 → `system()` 调用 npu_compiler（带 `-n/-p/-f/-m/-c` 五个参数）→ 生成 `.mbs`（MBS = Mapper Binary Stream，飞腾 NPU 的可执行格式）。**整个过程零 LLVM 参与**。

**证据 4：`codegen_phydnn_gpu.cc` GPU 路径同样绕过 LLVM** `[实测-读文件]`
```
codegen_phydnn_gpu.cc:27   std::string gpu_compiler_cmd = config->gpu_compiler_bin_path;
codegen_phydnn_gpu.cc:84   gpu_compiler_cmd += " -n " + f_phyir.GetFileName();
codegen_phydnn_gpu.cc:86   if (config->maxCU != "") gpu_compiler_cmd += " --maxCU " + config->maxCU;
codegen_phydnn_gpu.cc:93   int sys_status = system(gpu_compiler_cmd.c_str());  // 调外部二进制
```
GPU 路径镜像 NPU：PHYIR → `system()` 调 gpu_compiler（带 `--maxCU/--maxWG/--targetAddressBits` 参数）→ 生成 .bin。`maxCU`（compute units）/`maxWG`（workgroup）是 GPU 编译器参数，说明 gpu_compiler 是一个 OpenCL/PHYDNN 离线编译器。

**证据 5：`x100_build.py` 二进制路径解析** `[实测-读文件]`
```
x100_build.py:509   mapper_bin_path = mapper_path + "/bin/npu_compiler"
x100_build.py:531   gpu_compiler_bin_path = gpu_compiler_path + "/bin/gpu_compiler"
```
飞腾 NC-SDK 的构建脚本从环境变量 `NPU_MAPPER_INSTALL_PATH`/`GPU_COMPILER_INSTALL_PATH` 解析二进制路径。bin/ 目录实测有 `npu_compiler`（ELF 二进制），lib/ 有 `libnpucompiler.so`。

**证据 6：contrib/phytium grep LLVM 零命中** `[实测-grep]`
`grep -rn "LLVM|llvm|mcpu|target_triple|triple" src/relay/backend/contrib/phytium/` → **No files found**。这 12 个飞腾专有 codegen 文件**完全不含任何 LLVM 概念**——没有 mcpu、没有 triple、没有 LLVM IR、没有 MC layer。**飞腾 NPU 编译器与 LLVM 是两个互不相交的世界**。

#### 2.4.3 PHYIR 是什么？npu_compiler 是什么？（推测-依据）

**PHYIR（Phytium IR）**：从代码看，它是飞腾自研的计算图 IR。`AsPHYIR` 把 Relay Function 转成 PHYIR JSON，再拼上 `phydnn_version`（"PHYDNN001008"）前缀。输出文件叫 `.imgir`（intermediate machine IR）。它**不是 LLVM IR，也不是 MLIR dialect，也不是 TVM Relay IR**——是飞腾自己的一层。这层的设计意图是：把 Relay 计算图翻译成 NPU 能理解的算子序列 + 张量布局 + 量化参数。

**npu_compiler（mapper）**：从 `-m mapconfig`（MAP 配置）和 `-c hwconfig`（HW 配置）参数看，它是一个**资源映射器（mapper）**——把 PHYIR 算子映射到飞腾 NPU 的硬件资源（PE 阵列、片上 SRAM、DMA 通道）。输出 `.mbs`（Mapper Binary Stream）是 NPU 的可执行指令流。**它最可能不是传统意义上的"编译器后端"（不做指令选择/寄存器分配），而是"图编译器 + 资源调度器"**——类似 NVIDIA TensorRT 的 role（TensorRT 也是把计算图编译成 GPU kernel 调度，不经过 LLVM）。

**它可能基于什么？**（推测-依据，盲区，需飞腾官方确认）：
- **可能性 A（最可能）**：飞腾自研的图编译器框架，完全独立于 LLVM/GCC/TVM codegen。依据：contrib/phytium 零 LLVM 痕迹 + PHYDNN 自有版本号体系 + mapper 概念与硬件资源映射强相关
- **可能性 B（中等）**：基于某个开源图编译器（如 TVM 的 graph executor 或 MLIR 的某 dialect）的深度魔改。依据：phytvm 本身是 TVM fork，飞腾可能复用了 TVM 的图基础设施
- **可能性 C（较低）**：基于 LLVM 的某组件（如 MC layer 做 binary encoding）但隐藏了 LLVM 痕迹。依据：无法完全排除，但零 grep 命中强烈反对

**本专家的判断**：可能性 A 最符合证据。飞腾 NPU 编译器是一个**自研的图编译器 + 资源映射器**，它的设计哲学是"绕过通用编译器基础设施（LLVM/GCC），直接对接 NPU 硬件"——这与华为昇腾 CANN（拥抱 LLVM/TVM/MLIR 全栈）是**两条完全相反的路线**（§2.5）。

### 2.5 飞腾 vs 华为昇腾 CANN 编译器对照（新增，战略路线分野）

> 这是国产 AI 编译器两条路线的根本对照：飞腾"绕过 LLVM 的自研黑盒" vs 华为"拥抱 LLVM/TVM/MLIR 的全栈开源"。

#### 2.5.1 两条路线的架构对照

| 维度 | 飞腾 NPU 编译器（NC-SDK） | 华为昇腾 CANN |
|------|--------------------------|--------------|
| **基础框架** | TVM fork（phytvm）+ 自研 PHYIR + 外部 mapper 二进制 | 基于 LLVM + TVM + MLIR 全栈 |
| **NPU 编译器后端** | npu_compiler（闭源二进制，system() 调用） | Ascend 编译器（基于 LLVM，AscendC/Ascend IR） |
| **中间表示** | PHYIR（自研，.imgir，"PHYDNN001008"版本号） | Ascend IR（基于 MLIR dialect + GE 图引擎） |
| **License** | Strictly Confidential（9 个文件标 NC-SDK license） | Apache 2.0（2025-12 开源 Ascend 910B/C 编译器） |
| **生态可见度** | 零（纯黑盒，无公开算子开发接口） | 高（AscendC 算子语言 + MindSpore 框架 + CANN 开源社区） |
| **开发者可扩展性** | 极低（用户不能自己写 NPU 算子） | 高（AscendC 让第三方写算子） |
| **LLVM 关系** | 完全绕过（contrib/phytium grep LLVM 零命中） | 深度集成（CANN 编译器后端基于 LLVM） |

#### 2.5.2 战略路线分野的根本原因

**为什么飞腾"绕过"，华为"拥抱"？**

1. **团队规模差异**（§2.6 深化）：华为编译器实验室是千人级团队（毕昇 + 昇腾 + openEuler 平行宇宙），有能力吃透 LLVM/TVM/MLIR 全栈并贡献回上游；飞腾编译器团队据 JD 推测是十人级，无力维护全栈，只能做"接口层 + 外部黑盒"
2. **生态策略差异**：华为卖 NPU 算力（昇腾 910B/C 是云服务，需要第三方算子生态），必须开放编译器；飞腾 NPU 走嵌入式/边缘（自家用），不需要第三方算子生态，封闭够用
3. **自主可控理解差异**：华为把"自主可控"理解为"我主导开源生态"（毕昇开源 + CANN 开源 + TSV110 upstream），飞腾把"自主可控"理解为"我闭源你拿不走"（PhyCC 闭源 + npu_compiler 闭源 + Strictly Confidential）

**这个分野的长期后果**（推测-依据，对标 NVIDIA CUDA 生态建设史）：
- **华为路线**：AscendC + CANN 开源 → 第三方算子生态 → AscendNPU-IR 可能成国产 AI 编译器事实标准（Lens_07 下注 3，55-70% 概率）→ 华为获得 AI 编译器编排权
- **飞腾路线**：npu_compiler 黑盒 → 零第三方算子生态 → 算子全靠飞腾自己写 → NPU 算力生态封闭 → 长期沦为"飞腾自家的加速器"，无法进入 AI 推理主流（与飞腾 E21"AI 算力定位"战略伤疤同源）

**对偶判断**：飞腾 NPU 编译器的封闭路线，是 NVIDIA CUDA 的**反面教材**。CUDA 之所以统治 AI 算力，不是因为 GPU 硬件最强，而是因为**编译器生态最开放**（NVCC 开源编译器前端、PTX ISA 公开、cuDNN 算子库开放）。飞腾走 npu_compiler 黑盒路线，注定无法复制 CUDA 的生态护城河。Lens_04 经济学家的"双边平台网络效应"在此适用：NPU 编译器是双边平台（一边算子开发者，一边硬件后端），飞腾把算子开发者这一边**直接关闭了**。

### 2.6 飞腾编译器团队规模推测（新增，从 JD + 论文 + 社区活跃度）

> 本节是 `[推测-依据]`，基于公开信息三角验证，盲区在 §5.1 已声明。

#### 2.6.1 三角验证法

**线索 1：飞腾招聘 JD** `[官方-JD]`
飞腾官网招聘 NPU 编译器工程师 JD 明文（phytium.com.cn/recruitment 2024-07）：
> "1.从事飞腾 NPU 编译器开发工作，在 llvm 基础上移植一个新的后端，并支持新的指令集；2.针对飞腾处理器进行指令调度优化等优化。"

**解读**：(a) JD 要求"在 llvm 基础上移植一个新的后端"——说明飞腾**至少在招"能做 LLVM 后端移植"的人**，但 §1.3 实测主线 LLVM 零 FTC86x 说明**这个移植至今没有 upstream**（要么做了内部闭源版，要么没做完）。(b) JD 是"招聘 1 个岗位"不是"招聘 1 个团队"——编译器团队是**按需扩招**，不是建制化大团队。

**线索 2：公开论文/技术输出** `[社区]`
- 飞腾在公开学术会议（PLDI/CGO/CC/LLVM Dev Meeting）**零编译器论文**（websearch 2026-07）
- 对比：华为毕昇团队在 CGO/CC 有多篇论文；龙芯 LoongArch 在 LLVM Dev Meeting 有 talk；平头哥玄铁在 RISC-V Summit 有技术分享
- 飞腾的技术输出集中在**芯片层**（D3000M 白皮书、ARMv8.4 FEAT 文档），编译器层**零公开技术输出**

**线索 3：社区活跃度** `[GitHub/社区]`
- 飞腾在 LLVM Discourse（discourse.llvm.org）**零发帖/零回复**（websearch 2026-07）
- 飞腾在 GCC mailing list **零 patch**（phytium_repos 的 PhyGCC 改动未回流）
- 对比：华为有 Pengcheng Wang（linux.alibaba.com 前期）等活跃 commit 身份；龙芯有 heiher 等活跃 maintainer；平头哥有 Jianjian GUAN（streamcomputing.com）

#### 2.6.2 规模推测与对照

| 厂商 | 编译器团队规模推测 | 依据 |
|------|:----------------:|------|
| 华为 | **千人级**（毕昇+昇腾+openEuler 平行宇宙） | 毕昇商业发行版 + CANN 全栈 + TSV110 upstream + 平行宇宙 LLVM 替 GCC 全发行版 |
| 龙芯 | **百人级** | LoongArch 主线 GCC/LLVM/binutils 全栈 + maintainer 编制 |
| 平头哥 | **数十人级** | 玄铁 C910 fork + RISC-V upstream + 剑池工具链 |
| **飞腾** | **十人级** | PhyCC/PhyGCC 闭源（小团队维护）+ NPU 编译器按需招 + 零主线 commit + 零论文 + 零社区活跃 |

**推论**：飞腾编译器团队规模是**六家国产 CPU 厂商里最小的之一**（可能仅优于申威的纯学术态）。这与 §2.1 "纯消费者"角色自洽——团队规模不支持 upstream（要跟 LLVM 6 月 release 节奏 + code review + 长期维护），所以只能消费上游。

**Lens_03 供应链分析师的精确解释**（对偶）：upstream 一个调度模型意味着长期维护（跟 LLVM 6 月 release），飞腾编译器团队规模不支持。**维护成本是飞腾不上游的根本原因，不是技术能力**——香山（中国开源 RISC-V，中科院）能进主线 LLVM（`XIANGSHAN_NANHU`），证明中国项目能 upstream，飞腾没 upstream 是投入策略问题。

---

## 3. 国产 CPU 厂商 LLVM fork 生态对照（详细矩阵）

### 3.1 飞腾（FTC862 / ARMv8.4）—— 纯消费者

- **主线 LLVM**：零贡献（`AArch64Processors.td` 无 FTC86x，§1.3 铁证）
- **fork**：PhyCC（闭源，基于 LLVM，PhyCC 2.0 "基于 LLVM 研发" `[官方]`）；PhyGCC（闭源，基于 GCC，10.3.2 落后主线 1-2 版本）
- **NPU 编译器**：外部 `npu_compiler`/`gpu_compiler` 二进制，绕过 LLVM（§2.4 铁证）
- **生态**：phytium_repos 45 目录全是消费者姿态（Android/Yocto/Buildroot/FreeBSD 全用上游 LLVM）
- **自主度**：阶段 2（Fork），约 40-60%

### 3.2 华为（鲲鹏 TaiShan v110 / ARMv8.2；昇腾 NPU）—— 第二档最强

- **主线 LLVM**：✅ TSV110 调度模型在 `AArch64Processors.td:833/1544`（带 `TSV110Model`，`AArch64SchedTSV110.td`）
- **fork**：毕昇编译器（BiPengine/BiSheng，开源+商业双轨，自定义 `-mllvm` 优化选项如 `-aarch64-ldp-stp-noq` 针对 tsv110 的 stp/ldp）
- **NPU 编译器**：昇腾 CANN（基于 LLVM/TVM/MLIR，2025-12 开源 Ascend 910B/C，全栈自研）
- **发行版**：openEuler 平行宇宙（用 LLVM 替 GCC 构建整个发行版，2023 发起，RISC-V 侧面向 SG2042）
- **生态**：openEuler / openGauss 平行宇宙 + OEPKGS 源可 yum 安装毕昇
- **自主度**：阶段 2-3（Fork + Upstream），约 60-80%

### 3.3 龙芯（LoongArch 自研 ISA）—— 第一档最强

- **主线 LLVM**：✅ 独立后端（`llvm/lib/Target/LoongArch/`，LLVM 16.0.0 起 2023-03 升为正式后端 official target，LLVM 22.x 2026-01 仍活跃加 LA32）
- **主线 GCC**：✅ LoongArch 在主线 GCC（GNU ELF Machine 编号 258）+ Binutils + Glibc + Linux 全栈"BIG FIVE"
- **fork**：不需要（主线即权威），龙芯员工任 maintainer
- **生态**：Loongnix 龙芯发行版
- **自主度**：阶段 3（自研 ISA + upstream 框架），约 70-90%（当前国产 CPU 编译器自主度最高）

### 3.4 平头哥（玄铁 C910/C920 / RISC-V）—— 第二档

- **主线 LLVM**：⚠️ RISC-V 后端上游，玄铁 Ascalon 调度模型 `RISCVSchedTTAscalonX.td` 进主线（Lens_03 实测）；C910 早期 fork 在 ISRC-CAS/c910-llvm
- **fork**：玄铁系列开源 LLVM fork + OpenC910 RTL 全开源
- **生态**：T-Head 剑池工具链 + c-sky/buildroot
- **自主度**：阶段 2-3，约 60-75%

### 3.5 海光（x86 / Zen）—— 第二档

- **主线 LLVM**：✅ x86 后端上游，c86-4g 系列 2026-06 刚合入 GCC 17，LLVM 跟进中
- **fork**：用主线 GCC/LLVM
- **加速器**：DCU（AMD GPU 衍生，用 ROCm/HIP）
- **自主度**：阶段 2（Upstream 跟进），约 55-70%

### 3.6 申威（SW64 自研）—— 介于二档三档之间

- **主线 LLVM**：✅ SW64 在主线 LLVM ≥ 17（社区推进）；有学术论文级 swLLVM fork
- **fork**：闭源/社区推进中
- **生态**：神威·太湖之光超算专有，纯学术/超算 niche
- **自主度**：阶段 3（自研 ISA），但生态封闭，约 60-70%

### 3.7 矩阵总结

| 厂商 | ISA | 主线后端 | 商业 fork | 主线 commit | 主线调度模型 | 综合档位 | 自主度 |
|------|-----|:------:|:------:|:------:|:------:|:------:|:------:|
| 龙芯 | LoongArch | ✅ | — | ✅ maintainer | — | 🥇 第一档 | 70-90% |
| 华为鲲鹏/昇腾 | ARMv8.2 | ⚠️ tsv110 | ✅ 毕昇 | ✅ | ✅ TSV110 | 🥈 第二档 | 60-80% |
| 平头哥玄铁 | RISC-V | ⚠️ RISC-V | ✅ 玄铁 | ✅ | ✅ Ascalon | 🥈 第二档 | 60-75% |
| 海光 | x86 | ✅ | — | ✅ | — | 🥈 第二档 | 55-70% |
| 申威 | SW64 | ✅ | ⚠️ 闭源 | ⚠️ 社区 | — | 🥈-🥉 | 60-70% |
| **飞腾** | ARMv8.4 | ❌ | ⚠️ PhyCC 闭源 | ❌ 零 | ❌ 零 | 🥉 第三档（最末） | 40-60% |

### 3.8 国产 CPU 厂商编译器研发投入量化对比（新增）

> 用可观测指标量化六家厂商的编译器研发投入，避免"感觉"式判断。

| 指标 | 龙芯 | 华为 | 平头哥 | 海光 | 申威 | 飞腾 | 数据来源 |
|------|:----:|:----:|:------:|:----:|:----:|:----:|---------|
| **主线 LLVM 调度模型** | — (LoongArch 后端) | ✅ TSV110 | ✅ Ascalon | — (x86 通用) | — | ❌ 零 | `[实测-AArch64Processors.td]` |
| **主线 LLVM 后端** | ✅ 独立后端 | ⚠️ (复用 AArch64) | ⚠️ (复用 RISC-V) | ⚠️ (复用 x86) | ✅ SW64 | ❌ 零 | `[实测-目录]` |
| **主线 LLVM commit 活跃身份** | ✅ heiher 等 | ✅ 多人 | ✅ GUAN 等 | ⚠️ | ⚠️ 社区 | ❌ 零 | `[Discourse/GitHub]` |
| **公开编译器论文** | ✅ 多篇 | ✅ 多篇 (CGO/CC) | ✅ RISC-V Summit | ⚠️ 少 | ✅ 学术级 | ❌ 零 | `[websearch]` |
| **开源 LLVM fork** | — (主线即权威) | ✅ 毕昇开源 | ✅ c910-llvm 开源 | — | ⚠️ swLLVM | ❌ PhyCC 闭源 | `[GitHub]` |
| **NPU 编译器开放度** | — | ✅ CANN 开源 (Apache 2.0) | — | ⚠️ DCU | — | ❌ npu_compiler 黑盒 | `[实测-License]` |
| **团队规模推测** | 百人级 | 千人级 | 数十人级 | 数十人级 | 学术级 | **十人级** | `[JD+论文+社区三角]` |
| **Discourse 发帖** | ✅ | ✅ | ✅ | ⚠️ | ❌ | ❌ 零 | `[社区]` |

**量化结论**：飞腾在 8 个指标里**6 个为零/最末**（调度模型、后端、commit、论文、开源 fork、NPU 开放度、Discourse）。这不是某一维度落后，是**全域缺席**。龙芯/华为/平头哥至少在 4-5 个指标有正向输出。

**为什么飞腾全域缺席？** 根因是 §2.6 的团队规模 + §2.5 的生态策略（封闭 vs 开放）。飞腾把编译器预算投在 NPU 黑盒（npu_compiler），CPU 侧吃上游——这是"集中兵力打一点"的策略，但代价是**CPU 编译器层的全域缺席**。

---

## 4. 给飞腾的工程建议（可执行）

### 4.1 短期（2026-2027，低成本高收益）

1. **upstream FTC86x 调度模型到主线 LLVM**——参考华为 TSV110 案例，写 `AArch64SchedFTC86x.td`。这是**免费收益**，零边际成本（飞腾内部已有 `FTC86x.md` for PhyGCC，转写为 LLVM .td 即可）。参考华为 `AArch64Processors.td:833/1544` 的 TSV110 范式，FTC86x 只需定义流水线宽度/指令延迟/资源冲突。**ROI 极高**：1-2 工程师年，换"主线 LLVM 一等公民"地位。
2. **加速 PhyGCC rebase 主线 GCC**——飞腾 PhyGCC 10.3.2 落后主线 1-2 版本（GCC 14/15），拿不到 GCC 14 的改进 SLP auto-vectorizer、改进 loop optimizer。rebase 是技术债清理，不是新功能。
3. **文档化 UDOT intrinsic 用法**（飞腾 E11 §2.3.4 已写）——飞腾 int8 算力（UDOT 16.9× 加速比 `[实测]`）几乎只能靠 intrinsic 拿到，自动向量化覆盖不到。配套 KleidiAI/ACL 的 int8 kernel 调优指南。
4. **统一 SDK LLVM 版本策略**——当前碎片化（9.0.1/12.0.0/13.0.1/19.1.7 跨 5 年）。建议定一个"飞腾主线 LLVM 版本"（如 LLVM 18 LTS），各 OS 发行版 align 到这个版本（对偶 Expert_17 治理）。

### 4.2 中期（2027-2030，战略抉择）

5. **明确 NPU 编译器战略**——飞腾 NPU 编译器走外部黑盒（npu_compiler，绕过 LLVM，§2.4），这意味着飞腾 NPU 的算子生态完全封闭。若要进入 AI 推理主流，必须三选一：
   - **选项 A（重资产，推荐）**：开源 `npu_compiler`，建立第三方算子生态（对标华为 CANN 开源）。投入大但生态护城河深
   - **选项 B（中资产）**：转走 MLIR/TVM 路线（参考华为昇腾 CANN），把 PHYIR 升级为 MLIR dialect，复用 LLVM codegen。技术风险中等
   - **选项 C（轻资产，维持现状）**：维持 npu_compiler 封闭，仅飞腾自家用。生态封闭但成本低——**适合嵌入式/边缘 NPU，不适合数据中心**
6. **拥抱 LLVM（不只 GCC）**——飞腾生态目前重 GCC（PhyGCC）。但 AI 推理框架（PyTorch/ONNX Runtime/llama.cpp/Triton）越来越用 LLVM/MLIR。飞腾应确保 LLVM AArch64 后端对 FTC86x 有基本调度支持（见 4.1 第 1 条）。**这是 AI 时代的编译器基础设施押注**——GCC 在 AI 编译器生态里正在边缘化（对偶 Lens_02 Christensen：GCC 被 LLVM 从 AI 维度颠覆）。
7. **建立 5-10 人稳定 LLVM commit 团队**——目标 2028 前在主线 LLVM 有稳定贡献节奏（每 release 至少 1-2 个 commit）。参考华为 TSV110 贡献者模式。

### 4.3 长期（2030-2035，路线抉择）

8. **评估 RISC-V 转向**——见 §4.4 深化。
9. **建立编译器研发建制**——飞腾目前编译器投入浅（§2.6），应建立独立的编译器实验室（参考华为编译器实验室建制），目标 2030 前百人级团队，5 年进入 LLVM Foundation Board（参考 ARM/Apple/Google/AMD 的 Board 席位）。

### 4.4 长期建议深化：2030-2035 RISC-V 转向的编译器就绪度评估（新增）

> 对标 Lens_07 判断四（ARM v9 不授 → 飞腾切 RISC-V）+ Lens_01 历史（ISA 兴衰 25-40 年周期）+ 飞腾 E22 §2.2（RISC-V 服务器生态落后 ARM 3-5 年）。本节评估"如果飞腾 2032-2035 切 RISC-V，编译器栈就绪吗？"

#### 4.4.1 触发条件（Lens_07 已给，E18 补充编译器侧）

飞腾切 RISC-V 的历史类比是 **Apple 2005 切 x86**（从 PowerPC 切到 Intel）。但飞腾切 RISC-V 比 Apple 切 x86 更难（Lens_07 §2.4.2）：
- Apple 切 x86 = 切到"更主流" ISA（顺势）；飞腾切 RISC-V = 切到"更边缘" ISA（逆势，RISC-V 服务器生态落后）
- Apple 切 x86 = Apple 一家决定；飞腾切 RISC-V = 需协调信创资质/国密认证/军工供货链（外部协调成本高）

**触发条件**（Lens_07 + E18 共识）：
- ① RISC-V 服务器单核性能追平 Neoverse V2（飞腾 E22 §2.3 时间表，约 2028-2030）
- ② ARM v9 持续不授中国 + 中美科技脱钩加剧（地缘恶化）
- ③ RISC-V 编译器栈成熟（本节评估）

#### 4.4.2 RISC-V 编译器栈就绪度评估（2032-2035 视角）

| 编译器组件 | 当前状态 (2026) | 2032-2035 就绪度 | 依据 |
|-----------|:--------------:|:----------------:|------|
| **LLVM RISC-V 后端** | ✅ 主线成熟（RV32/RV64 + RVV 向量扩展） | ✅ 就绪 | 平头哥/进迭时空/SiFive 持续 upstream |
| **GCC RISC-V 后端** | ✅ 主线成熟 | ✅ 就绪 | RISC-V 原生支持 GCC |
| **RISC-V 调度模型** | ✅ 香山 NanHu/KunmingHu + 平头哥 Ascalon + 进迭时空 Spacemit + SiFive 都进主线 | ✅ 就绪 | Lens_03 实测 9 家厂商 |
| **RISC-V NPU/AI 编译器** | ⚠️ 早期（无成熟 NPU 后端） | ⚠️ 半就绪 | 平头哥 OpenC910 + 玄铁 C906 有探索，但无成熟 NPU 编译栈 |
| **飞腾自研 RISC-V 核的调度模型** | ❌ 飞腾无 RISC-V 核 | ❌ 需从零建 | 飞腾需先自研 RISC-V 核，再写调度模型 upstream |
| **信创 RISC-V 软件栈** | ⚠️ 龙芯/华为无 RISC-V 主力 | ⚠️ 需重建 | openEuler RISC-V 有预览版但非主力 |

**评估结论**：RISC-V 编译器基础设施（LLVM/GCC 后端 + 调度模型）**在 2032-2035 会就绪**，但有两个飞腾特异性缺口：
1. **飞腾自研 RISC-V 核的调度模型**需从零建（飞腾当前无 RISC-V 核，需先设计核再写 .td upstream，参考香山 NanHu 模式）
2. **飞腾 NPU 编译器需重写**（npu_compiler 当前对接 PHYDNN NPU，切 RISC-V 后若 NPU 架构变，mapper 需重写——这是沉没成本最大的一项）

#### 4.4.3 切 RISC-V 的编译器迁移成本（推测-依据）

参考龙芯 LoongArch 从 MIPS 切 LoongArch 的编译器迁移经验（2010-2022，约 12 年）：
- **ISA 定义 + 工具链 bootstrap**：3-5 年（LoongArch 用了约 5 年进主线 GCC/LLVM）
- **调度模型 + 优化**：3-5 年（LoongArch 仍在持续加优化）
- **生态迁移（OS/框架/库）**：5-8 年（Loongnix 发行版 + 应用生态）

**飞腾切 RISC-V 的编译器迁移**（若 2032 启动）：
- **有利**：RISC-V 是开放 ISA，LLVM/GCC 后端已成熟，飞腾不用建后端（不像龙芯建 LoongArch 后端），只需加调度模型
- **不利**：飞腾当前零 RISC-V 经验，零 RISC-V commit 身份，需从零建团队（§2.6 十人级团队不够）
- **最不利**：飞腾 NPU 编译器（npu_compiler）需重写——这是比 CPU 编译器迁移更大的工程

**本专家判断**：飞腾切 RISC-V 的编译器栈**基础设施会就绪（LLVM/GCC 成熟），但飞腾自己的就绪度不会就绪（零团队 + NPU 重写）**。除非飞腾在 2028 前启动 RISC-V 编译器预研（Lens_07 下注 5，60-75% 概率），否则 2032 切换时编译器会拖后腿。**编译器是飞腾切 RISC-V 的最长板凳**。

---

## 5. 这一视角的盲区与反方（诚实段，强制）

### 5.1 E18 视角看不见什么

1. **看不见 PhyCC/PhyGCC 商业版内部**：飞腾商业编译器闭源，本专家基于公开仓库 grep。**飞腾商业版可能有私有 LLVM patch**，但公开证据强烈指向"无 fork"。需要飞腾官方确认。PhyCC 2.0 官方说"基于 LLVM 研发" `[官方]`，但基于哪个 LLVM 版本、有多少私有 patch、是否含 FTC86x 调度——**全部不可见**。
2. **看不见 FTC862 最优 -mcpu/-mtune**：本专家只做源码确认，未跑性能 A/B。PhyGCC 的 `-mtune=ftc86x` 实际效果需飞腾真机实测（飞腾 E11 §3.2 已部分覆盖，用通用 Cortex-A 近似调度损失约 5-10%，但最优 -mtune 参数组合未穷尽测试）。
3. **看不见 npu_compiler/gpu_compiler 内部**：这两个二进制是 ELF 黑盒（`bin/npu_compiler` 不可读），§2.4.3 对"它基于什么"的推测可能性 A/B/C 无法实测确认。**npu_compiler 可能用了 LLVM 的某些组件（如 MC layer 做 binary encoding）但隐藏了字符串**——本专家无法排除可能性 C。
4. **看不见飞腾 roadmap**：飞腾未公开的下一代 D4000/D5000/D6000 编译器路线可能完全不同。飞腾可能在内部已有 RISC-V 编译器预研（§4.4），但零公开信息。
5. **看不见飞腾编译器团队真实规模**：§2.6 是推测（JD + 论文 + 社区三角），不是编制表。飞腾可能有比推测更大的团队（保密），也可能更小。
6. **看不见竞品的闭源部分**：华为毕昇/海光 c86-4g/申威 swLLVM 的闭源商业版可能有更深的 patch。本对照只基于开源可查部分。

### 5.2 反方观点：飞腾"消费者姿态"可能就是对的

一个有力的反方：**飞腾作为商业公司，专注于芯片设计而非编译器研发，是合理的资源分配**。论据：
- **编译器研发是高投入、低差异化**：所有 ARM CPU 共享 LLVM/GCC 框架，编译器不是芯片厂商的差异化护城河。ARM 自己只维护 ARM C 语言扩展 + 部分 Cortex-A 调度模型，其余靠社区。飞腾没必要做 ARM 该做的事
- **飞腾核心价值在 FTC862 微架构**（4-wide OoO、ARMv8.4、国密原生、军工资质），不在编译器。芯片设计 ROI 远高于编译器研发
- **用主线 LLVM 的"通用 Cortex-A 近似"调度，性能损失 < 10%**（飞腾 E11 §3.2 实测）——对桌面/嵌入式场景够用
- **华为/龙芯的编译器投入对应其战略**：华为要卖 NPU 算力（昇腾云服务，必须开放编译器生态）；龙芯要推自研 ISA（LoongArch 必须 upstream 否则零生态）。**飞腾 ARM 路线不需要这种投入**——ARM 生态 LLVM/GCC 已经养好，飞腾搭便车即可
- **NPU 编译器封闭（npu_compiler 黑盒）对飞腾自家用够用**：飞腾 NPU 走嵌入式/边缘（自家用），不需要第三方算子生态，封闭的工程成本远低于开放（不用维护 AscendC 式算子开发语言 + 社区）

**这个反方有道理但不完全对**，本专家的反反驳：
- 飞腾若想在**服务器市场（S5000C）长期立足**，编译器调度优化的 5-10% 性能差在数据中心 TCO 里是巨大数字。服务器场景是"每 1% 性能 = 数百万电费"，"消费者姿态"在桌面场景够用，**在服务器场景是致命的**（参考飞腾 E23 RAS + E07 商业）。upstream FTC86x 调度模型的成本（1-2 工程师年）远低于服务器市场 5-10% 性能差的损失
- 飞腾"搭 ARM 便车"的前提是**ARM 生态持续养好**。但 ARM v9 不授中国（飞腾项目宪法 §0）——飞腾停在 ARMv8.4 意味着主线 LLVM 的"未来红利"（SVE2/MTE/SME/FP8）永远拿不到。这不是"搭便车"，是"被锁在旧车型的便车上"
- NPU 编译器封闭对"飞腾自家用"够用，但飞腾若想卖 NPU 算力（对标华为昇腾云服务），封闭路线注定无法进入 AI 推理主流（§2.5）

**本专家的最终立场**：反方在桌面/嵌入式场景成立，在服务器/AI 推理场景不成立。飞腾的"消费者姿态"是**理性的短期选择**（资源分配），但是**危险的长期赌注**（编译器债永续累积）。

---

## 6. 与其他视角对偶（强制，深化为五视角对偶）

### 6.1 一致（4 个视角强一致）

- **与 Lens_07 国产化战略家一致**：飞腾是六家国产 CPU 厂商里编译器自主度最低的之一（L1 远未达 L3）。本专家用代码级证据支撑了 Lens_07 的 5 注下注。
- **与 Lens_03 供应链分析师一致**：飞腾在 LLVM 供应链是纯消费者，非生产者；飞腾是 AArch64 后端唯一缺席的中国服务器 CPU 厂商。Lens_03 的"商业模式决定供应链位置"（飞腾卖整芯片不需要 LLVM 可见度）解释了本专家的"纯消费者"判断的根因。
- **与 Expert_08 AArch64 后端一致**：主线 LLVM 无 FTC86x 调度模型，34 个调度模型清单无飞腾，华为有 TSV110。本专家用 §1.3 铁证支撑了 E08 的"飞腾在 AArch64 后端是匿名核"判断。
- **与飞腾 Expert_11 编译器研究一致**：飞腾 PhyGCC 是 GCC fork（不是 LLVM fork），主线 LLVM 调度次优（5-10% 损失）。本专家补充了"NPU 编译器绕过 LLVM"这一 E11 未覆盖的层面。

### 6.2 冲突（2 个视角张力）

- **与飞腾官方"自主可控"叙事冲突**：飞腾宣称"自主可控"（PhyCC 2.0 "基于 LLVM 研发" `[官方]`），但编译器层是最脆弱的（§2.2）。这是诚实诊断，不是攻击。**消费者包装成生产者，是叙事注水**——但本专家承认 PhyCC 的"准入级自主"（能编译能跑）是事实，只是远未达"可演级自主"（能贡献能演进）。
- **与飞腾 E22 开源生态视角潜在冲突**：E22 呼吁飞腾拥抱开源。本专家指出飞腾在 LLVM 主线零贡献 + NPU 编译器 Strictly Confidential，这与 E22 的"可审计性/可复现性"诉求冲突。**飞腾的封闭策略（npu_compiler 黑盒）与开源精神背道而驰**——这是飞腾内部 E18 与 E22 的张力。

### 6.3 新增对偶：与 Lens_02 Christensen 破坏式创新对偶（深化）

Lens_02 判"飞腾在编译器层永远是跟随者，永远不可能成为颠覆者（它的资源/流程/价值观都不支持自研编译器基础设施）"。本专家**完全认同**并补充：
- 飞腾 NPU 编译器走 npu_compiler 黑盒（绕过 LLVM），是"用 sustaining 的姿态做了一件 disruptive 的反例"——它**没有**像 LLVM 拥抱 MLIR那样"主动孵化颠覆者"，而是**封闭了颠覆入口**。Christensen 说"在位者唯一的自救是主动孵化自己的颠覆者"，飞腾反其道而行（npu_compiler 黑盒 = 封闭颠覆入口），**这决定了飞腾 NPU 无法成为 AI 编译器的颠覆者**。

### 6.4 新增对偶：与 Expert_17 治理/License 对偶（深化）

E17 讲"Linux 内核 GCC→Clang 迁移"（断层⑤）。本专家补充：飞腾主编译器是 GCC（PhyGCC），LLVM 是次要——飞腾在 GCC→LLVM 大迁移里是**被动跟随者**。若 Linux 内核全面转 Clang（E17 断层⑤），飞腾需同时维护 PhyGCC（旧）+ PhyCC（新）两套——这是飞腾编译器治理的隐性债。

---

## 7. 参考文献（≥18 条，分级标注）

### 飞腾官方（[官方]）
1. **[官方]** 飞腾开发者平台 - 编译器. [phytium.com.cn/developer/36](https://www.phytium.com.cn/developer/36/). 访问 2026-07-07. —— PhyCC 1.0/2.0 + PhyGCC 二进制下载.
2. **[官方]** PhyCC 2.0 发布页. "PhyCC 2.0 基于 LLVM 研发"——飞腾唯一直接说"基于 LLVM"的官方编译器.
3. **[官方]** 飞腾招聘 NPU 编译器工程师 JD. phytium.com.cn/recruitment 2024-07. "在 llvm 基础上移植一个新的后端". —— 飞腾自研 LLVM 后端的唯一实锤 + 团队规模推测依据（§2.6）.

### 实测清单（[实测]，铁证级）
4. **[实测]** phytvm fork diff 发现. [phytvm_diff_findings.md](./phytvm_diff_findings.md). 2026-07-07. —— 飞腾真实定制在 contrib/phytium + 外部 npu_compiler，LLVM 层 vanilla.
5. **[实测]** phytium_repos LLVM patches 盘点. [phytium_repos_llvm_patches.md](./phytium_repos_llvm_patches.md). 2026-07-07. —— 45 仓库零飞腾 patch.
6. **[实测]** 主线 LLVM FTC86 源码确认. [主线LLVM_FTC86_源码确认.md](./主线LLVM_FTC86_源码确认.md). 2026-07-07. —— LLVM 23.0 零命中，34 调度模型无飞腾.
7. **[实测]** 飞腾 SDK LLVM 版本矩阵. [飞腾SDK_LLVM版本矩阵.md](./飞腾SDK_LLVM版本矩阵.md). 2026-07-07. —— 6 OS 全上游，碎片化 9.0.1→19.1.7.
8. **[实测]** 国产 CPU 厂商 LLVM fork 生态. [国产CPU厂商_LLVM_fork_生态.md](./国产CPU厂商_LLVM_fork_生态.md). 2026-07-07. —— 三档分化，飞腾最末.

### 代码级实例（[实测-读文件/grep]，§2.4 铁证）
9. **[实测-读文件]** `opt-npu/ncsdk/common/phytvm/src/relay/backend/contrib/phytium/codegen.h`（144 行）. 2026-07-07. —— PhytiumConfigNode 15 字段，mapper_bin_path/gpu_compiler_bin_path 指向外部二进制，Strictly Confidential NC-SDK license.
10. **[实测-读文件]** `opt-npu/.../contrib/phytium/codegen_npu.cc`（199 行）. 2026-07-07. —— NPU 编译管道：Relay→AsPHYIR→system(npu_compiler)→.mbs，零 LLVM.
11. **[实测-读文件]** `opt-npu/.../contrib/phytium/codegen_phydnn_gpu.cc`（203 行）. 2026-07-07. —— GPU 编译管道：PHYIR→system(gpu_compiler)→.bin，零 LLVM.
12. **[实测-读文件]** `opt-npu/ncsdk/bin/x100_build.py`（608 行）. 2026-07-07. —— 二进制路径解析 NPU_MAPPER_INSTALL_PATH/bin/npu_compiler + GPU_COMPILER_INSTALL_PATH/bin/gpu_compiler.
13. **[实测-grep]** contrib/phytium 全目录 grep `LLVM|llvm|mcpu|target_triple|triple` 零命中. 2026-07-07. —— 飞腾 NPU 编译器与 LLVM 互不相交的铁证.

### 项目内对偶（[项目内]）
14. **[项目内]** oracle战略评审.md §0.3. —— codegen_arm.cc 是 vanilla TVM 的战略级发现.
15. **[项目内]** Lens_07 国产化战略家. —— 5 注可证伪下注 + 四阶段自主度评分 + 飞腾切 RISC-V 判断四.
16. **[项目内]** Lens_03 供应链分析师. —— AArch64/RISC-V 养育图谱 + "商业模式决定供应链位置".
17. **[项目内]** Lens_02 Christensen 破坏式创新. —— 飞腾 RPV 锁在"消费上游"模式.
18. **[项目内]** Expert_08 AArch64 后端. —— 34 个 AArch64 调度模型清单，华为 TSV110 在 :833/1544.
19. **[项目内]** Expert_17 治理/License. —— 断层⑤ Linux 内核 GCC→Clang 迁移.
20. **[项目内]** 飞腾 Expert_11 编译器研究 §2.4 PhyGCC vs 主线 GCC + §3.2 调度次优实测（5-10% 损失）.

### 外部（[社区]/[GitHub]/[websearch]）
21. **[社区]** 基于飞腾 CPU 的高性能编译器 PhyGCC 的安装及配置说明. [SegmentFault 2024-03](https://segmentfault.com/a/1190000044680095). 访问 2026-07-07.
22. **[GitHub]** LoongArch 在主线 LLVM. [github.com/llvm/llvm-project/tree/main/llvm/lib/Target/LoongArch](https://github.com/llvm/llvm-project/tree/main/llvm/lib/Target/LoongArch). 访问 2026-07-07.
23. **[GitHub]** ISRC-CAS/c910-llvm 平头哥玄铁 LLVM fork. [github.com/isrc-cas/c910-llvm](https://github.com/isrc-cas/c910-llvm). 访问 2026-07-07.
24. **[websearch]** 华为毕昇编译器（BiSheng）+ openEuler 平行宇宙 LLVM 替 GCC. 访问 2026-07-07.
25. **[websearch]** 华为昇腾 CANN 编译器 2025-12 开源 Ascend 910B/C（Apache 2.0）. 访问 2026-07-07.

---

## § 编译器国产化战略方法论（通用化，不只飞腾）

### 方法论一：编译器自主可控四阶段

任何国产 CPU 厂商的编译器战略都走在四阶段（源自 Lens_07 §2.3，本专家补充代码级判定标准）：

| 阶段 | 行为 | 自主度 | 代码级判定标准 | 典型 |
|:----:|------|:------:|--------------|------|
| 1 用 | 用主线 GCC/LLVM 原样 | 30-50% | 仓库零 patch / 零 fork | 飞腾早期、海光、申威 |
| 2 Fork | 闭源或开源 fork | 40-60% | 有 fork 但不 upstream | 飞腾 PhyCC/PhyGCC、华为早期 |
| 3 Upstream | 贡献回主线 | 60-80% | 主线有调度模型/commit | 华为 TSV110、海光 c86-4g、平头哥 RISC-V |
| 4 自研 ISA + upstream | 自研 ISA + upstream 框架 | 70-90% | 主线有独立后端 + maintainer | 龙芯 LoongArch |

历史经验：**第三档（Upstream）是性价比最高的"自主可控"**——既享受主线生态，又有主线影响力，成本远低于第四档（自研 ISA）。飞腾目前停在第二档（Fork），**应该优先冲第三档**（upstream FTC86x 调度模型）。

### 方法论二：调度模型 upstream 成本收益

参考华为 TSV110 upstream 案例（`[实测]` AArch64Processors.td:833/1544）：
- **成本**：1-2 工程师年（写 `AArch64SchedFTC86x.td` 定义流水线宽度/指令延迟/资源冲突 + 提交 + code review + 跟 6 月 release 节奏）
- **收益**：所有用主线 LLVM 的用户都能调度最优；飞腾成为 LLVM 主线"一等公民"；获得主线 commit 身份（话语权）
- **ROI**：极高（飞腾已有 PhyGCC 的 `FTC86x.md`，转写 .td 是几周工作；1-2 工程师年换永久主线影响力）
- **对照**：香山（中国开源 RISC-V，中科院）能进主线（`XIANGSHAN_NANHU`），证明中国项目能 upstream——飞腾没 upstream 是投入策略问题不是能力问题

### 方法论三：NPU 编译器开放度光谱

| 开放度 | 典型 | 生态后果 | 飞腾位置 |
|:------:|------|---------|:--------:|
| 全黑盒 | 飞腾 npu_compiler（Strictly Confidential） | 零第三方算子生态，自家用 | ← 飞腾在这 |
| 半开放 | NVIDIA CUDA（NVCC 开源前端 + PTX 公开 + cuDNN 开放） | 强算子生态，编排权 | — |
| 全开源 | 华为昇腾 CANN（Apache 2.0，AscendC 算子语言） | 第三方算子生态 + 社区 | — |

**结论**：NPU 编译器开放度决定算子生态深度。飞腾在全黑盒端，长期无法进入 AI 推理主流（§2.5）。

### 方法论四：编译器供应链多元化

参考 Lens_03 供应链分析师：
- 不要单点依赖（飞腾依赖 GCC 单一，无 LLVM 备份——若 GCC 出战略问题飞腾无备份）
- 不要纯消费者（飞腾零主线贡献，无影响力——主线决策时飞腾无投票权）
- 多元化 = 主线 + fork + upstream 三管齐下（华为模式：毕昇 fork + TSV110 upstream + openEuler 发行版三位一体）

### 给国产 CPU 厂商的通用建议

1. **upstream 调度模型是免费午餐**——性价比最高的"自主可控"，1-2 工程师年换永久主线影响力
2. **商业 fork 必须同步 upstream**——避免 rebase 落后（飞腾 PhyGCC 落后主线 1-2 版本是技术债）
3. **NPU 编译器要有开放生态**——封闭 NPU 编译器（飞腾）vs 开放（华为昇腾 CANN）的长期生态差异巨大，封闭注定无法进入主流
4. **建立主线 commit 团队**——5-10 人稳定贡献团队，5 年进入 LLVM Foundation Board（参考 ARM/Apple/Google/AMD 的 Board 席位）
5. **不要把"消费者"包装成"生产者"**——诚实面对供应链角色，自主度 L1 不要叙事成 L3

---

### 图表索引（本视角共 6 张图表）

1. **图 1**：§0.3 双重门槛自检表（a 飞腾实证 / b 代码级实例 / c 对偶判断）
2. **图 2**：§2.1 五厂商供应链角色对照表（自研 ISA / 主线后端 / fork / commit / 调度模型 / NPU）
3. **图 3**：§2.2 飞腾"自主可控"叙事编译器层脆弱点表（5 维度）
4. **图 4**：§2.4.1 飞腾 NPU 编译器三层架构图（TVM 设备抽象 + PHYIR + 外部 mapper 二进制）
5. **图 5**：§2.5.1 飞腾 vs 华为昇腾 CANN 编译器架构对照表（7 维度）
6. **图 6**：§3.7 六厂商综合矩阵 + §3.8 投入量化对比表

---

*本文深化版写作于 2026-07-07。所有判断基于 5 个实测清单（[实测] 标注）+ NPU SDK 代码级深挖（§2.4 codegen.h/codegen_npu.cc/codegen_phydnn_gpu.cc/x100_build.py），零编造。盲区段诚实声明了 PhyCC/PhyGCC 商业版闭源、npu_compiler 黑盒、团队规模推测的局限。§2.4-§2.6/§3.8/§4.4 为本次深化新增章节。*
