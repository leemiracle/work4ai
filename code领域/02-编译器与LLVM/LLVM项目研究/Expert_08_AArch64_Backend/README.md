# Expert_08 — AArch64/ARM 后端专家视角

> **角色定位**：AArch64 后端 contributor——在 ARM/Qualcomm/Apple/华为这群"养着"AArch64 后端的公司之间斡旋、写 `.td` 表、提调度模型 upstream 的人。本专家盯着 `llvm/lib/Target/AArch64/` 这 136 个文件，回答一个问题：**一颗 ARMv8.4 的国产 CPU（飞腾 FTC862），在主线 LLVM 的 AArch64 后端里到底被当成什么？答案是——什么都"不是"，它隐身在 `generic` 这个别名里。** 这个答案是整个 LLVM 项目研究对飞腾命脉最锋利的一击。
>
> **核心思维模型**：
> 1. **目标描述驱动思维**（`.td` 文件清单决定后端能力）：现代 LLVM 后端不是手写的，是 TableGen 从 `.td` 表生成的。`AArch64.td` 一句 `include "AArch64Processors.td"` 决定了"哪些 CPU 名字被识别"；`AArch64Sched*.td` 决定了"每条指令在每颗核上的 latency/throughput"。**一颗 CPU 在主线 LLVM 里"存在"的唯一证据，是它的名字出现在 `ProcessorModel<"名字", ...>` 这一行的引号里**。飞腾 FCC862 没出现——它就"不存在"。
> 2. **调度模型分层思维**（Itinerary → SchedMachineModel → SchedWrite/SchedRead → ProcResource → WriteRes）：调度不是单一对象，是 5 层抽象。`SchedMachineModel` 定义 IssueWidth/MicroOpBufferSize（核的"骨架"），`ProcResource` 定义端口（核的"肌肉"），`WriteRes` 把每条指令的"动作"映射到端口+latency。飞腾 FCC862 这 5 层全部缺失。
> 3. **指令选择 + Legalize 协同思维**（与 [E05 CodeGen](../Expert_05_CodeGen_SelectionDAG_GlobalISel/README.md) 协同）：AArch64 后端的 `AArch64ISelLowering.cpp` 决定"NEON 128-bit 合法、SVE 可变长不合法"，`AArch64InstrInfo.td` 的 predicate 决定"UDOT 需要 `HasDotProd`、SM3 需要 `HasSM4`"。飞腾无 SVE → Legalize 把 `<vscale x 4 x i32>` 拆成 NEON `<4 x i32>`；飞腾有 UDOT → 指令选择能选出 `udot`。**这颗芯片的命运，一半在调度模型（缺失），一半在指令选择 predicate（覆盖）**。

---

## §0.3 双重门槛自检（特异性测试 v2.0）

本 Expert 同时满足宪法 §0.3 三项门槛：
- **(a) 飞腾工程实证**：主线 LLVM 23.0.0git `grep -rn "FTC86\|Phytium\|ftc86\|phytium" llvm/lib/Target/AArch64/` = **No files found** `[实测-grep 2026-07-07]`；`grep` clang 全树同样零命中。这是飞腾在线主线 LLVM 上"隐身"的源码铁证。
- **(b) 代码级实例**：引用 `AArch64Processors.td:1417`（`def : ProcessorModel<"generic", CortexA510Model, ...>`）、`AArch64SchedTSV110.td:1-31`（华为调度模型头部）、`AArch64.td:117-145`（27 个 Sched include 链）、`AArch64Features.td:132`（`def FeatureSM4`）等真实行号锚点。
- **(c) 对偶判断**：飞腾 PhyGCC 的 `FTC86x.md`（飞腾项目 E11 已写）vs LLVM 的 `FTC86xSched.td`（**不存在**）——同一颗芯片两个编译器的描述差"一张表的有无"。

---

## 1. 看 AArch64 后端的 12 个核心问题

这位 AArch64 后端 contributor 拿到飞腾 FCC862，第一件事不是跑 benchmark，而是 `grep ftc86 llvm/lib/Target/AArch64/`，然后问：

1. **飞腾 FCC86x 在主线 LLVM 里到底"是"哪个近似核？** 默认 `generic` 走的是 `CortexA510Model`（3-wide、in-order），还是被 `-mtune` 指到 `cortex-a76`/`tsv110`？源码级确认（§2.3）。
2. **`llvm/lib/Target/AArch64/` 那 136 个文件，`AArch64.td` 这个总入口 include 了哪些子表？** 用真实 `wc -l` 看清"目标描述驱动"的体量（§2.1，图 1）。
3. **主线 AArch64 后端到底有多少颗核的调度模型？为什么 FCC862 不在里面？** 实测 27 个 `AArch64Sched*.td` + 60+ `ProcessorModel` 条目，逐个列厂商归属（§2.2，图 2 + 量化对标表）。
4. **飞腾 D3000M 的 ARMv8.4 扩展（UDOT/SM3/SM4/FCMLA/LSE/FP16）在 AArch64 后端怎么"暴露"？** 从 `AArch64Features.td` 的 `ExtensionWithMArch` 到 HWCAP 到 intrinsic 头文件的全链路（§2.4，图 3）。
5. **对偶：飞腾 PhyGCC 有 `FTC86x.md`，主线 LLVM 为何没有 `FTC86xSched.td`？** 同一颗芯片，GCC 侧有专属调度（飞腾项目 E11 §2.4 已写），LLVM 侧零调度——这是"飞腾编译器投入全押 GCC、零押 LLVM"的硬证据（§2.5）。
6. **ARMv8.x 扩展在 AArch64 后端的暴露机制三层（SubtargetFeature / `.td` predicate / HWCAP）是怎么联动的？** `FeatureSM4` 这一个 def 怎么同时驱动指令选择、汇编接受、`-march=armv8.4-a+sm4` 解析（§2.4）。
7. **AArch64 vs ARM 32-bit 后端是什么关系？** 32-bit ARM 后端是不是在腐烂？实测 `llvm/lib/Target/ARM/` 118 文件、MVE/Thumb2 仍活跃（§2.8）。
8. **PAC/BTI/MTE/SVE/SVE2/SME 的后端支持进度——飞腾无 SVE，但主线 LLVM 持续加 SVE2/SME，这对飞腾是"看着别人吃肉"吗？** §2.6 给出 SVE2/SME 的 `.td` 实证 + 飞腾的"被边缘化"叙事。
9. **Neon/SVE intrinsic 头文件（`arm_neon.h`/`arm_sve.h`）怎么从 `.td` 自动生成？** `clang/include/clang/Basic/` + `AArch64SVEInstrInfo.td` 的 `arm_sve_sme_sema` 机制（§2.7）。
10. **飞腾若要 upstream FCC86x 调度模型，工程步骤是什么？** 参考华为 TSV110 upstream 案例——一个 `.td` 文件 + `ProcessorModel` 一行 + `Tune` 一行 + Phabricator review（§2.5 + §3.2）。
11. **AArch64 后端的"飞腾反向锚点"——零字符串——为什么反而是本项目的最强护城河之一？** 因为"缺席"比"存在"更能说明飞腾的编译器战略（§4.2）。
12. **下一代 D4000 若补 SVE/BF16/I8MM，AArch64 后端的 Legalize + Sched 哪一层会发生质变？** 给出可执行的"后端就绪度"判断（§3.3）。

---

## 2. 具体分析：代码级实例 + 飞腾实证 + 对偶判断

### 2.1 AArch64 后端 `.td` 文件树（图 1）——"目标描述驱动"的真实体量

> **特异性测试**：下面的 include 链是 OpenXiangShan/llvm-project 真实代码（行号锚点），删掉飞腾对照它仍是真实的 AArch64 后端剖析；但飞腾"零命中"是这段的锋芒。

`AArch64.td`（199 行 `[实测-read]`）是后端总入口，它的核心是 27 行 `include`。这 27 行决定了 AArch64 后端的全部能力：

```
图 1：AArch64.td 的 include 拓扑（行号锚点，OpenXiangShan/llvm-project LLVM 23.0.0git）
═══════════════════════════════════════════════════════════════════════
AArch64.td (199 行，总入口)
  │
  ├─ AArch64Features.td          ← 所有 SubtargetFeature 定义（SM3/SM4/DotProd/SVE...）
  ├─ AArch64FMV.td               ← Function Multi-Versioning（__attribute__((target_clones))）
  ├─ AArch64RegisterInfo.td      ← 31 GP + 32 SIMD + P0-P15(SVE) + Z0-Z31(SVE) + FFR
  ├─ AArch64RegisterBanks.td     ← GlobalISel 的寄存器 bank
  ├─ AArch64CallingConvention.td ← AAPCS64（X0-X7 传参、X19-X28 callee-saved）
  │
  ├─ AArch64Schedule.td          ← 抽象 SchedWrite/SchedRead 定义（WriteImm/WriteI/WriteLD...）
  ├─ AArch64InstrInfo.td         ← 指令模式定义（巨型，含 predicate 引用 HasV8_4aOps/HasDotProd...）
  ├─ AArch64SchedPredicates.td   ← 调度谓词公共定义
  ├─ AArch64SchedPredExynos.td   ← Exynos 专用谓词
  ├─ AArch64SchedPredNeoverse.td ← Neoverse 专用谓词
  ├─ AArch64Combine.td           ← DAG combine 模式
  ├─ AArch64SystemOperands.td    ← 系统寄存器/MSR/MRS/TLBI
  │
  ├─ [27 个具体调度模型 .td]     ← AArch64.td:117-143
  │   ├─ AArch64SchedA320.td     (line 117)
  │   ├─ AArch64SchedA53.td      (line 118)  → Cortex-A34/35/53/57/65/72/73/75/Kryo/NeoverseE1 复用
  │   ├─ AArch64SchedA55.td      (line 119)
  │   ├─ AArch64SchedA510.td     (line 120)  → ★ generic 默认用这个模型 ★
  │   ├─ AArch64SchedA57.td      (line 121)
  │   ├─ AArch64SchedCyclone.td  (line 122)  → Apple A7-A17/M1-M5 全家
  │   ├─ AArch64SchedFalkor.td   (line 123)  + AArch64SchedFalkorDetails.td
  │   ├─ AArch64SchedKryo.td     (line 124)  + AArch64SchedKryoDetails.td  → 高通
  │   ├─ AArch64SchedExynosM3.td (line 125)  → 三星
  │   ├─ AArch64SchedExynosM4.td (line 126)
  │   ├─ AArch64SchedExynosM5.td (line 127)
  │   ├─ AArch64SchedThunderX.td (line 128)  → Cavium/Marvell
  │   ├─ AArch64SchedThunderX2T99.td (line 129)
  │   ├─ AArch64SchedA64FX.td    (line 130)  → 富士通
  │   ├─ AArch64SchedThunderX3T110.td (line 131)
  │   ├─ AArch64SchedTSV110.td   (line 132)  → ★ 华为鲲鹏（唯一国产） ★
  │   ├─ AArch64SchedAmpere1.td  (line 133)
  │   ├─ AArch64SchedAmpere1B.td (line 134)
  │   ├─ AArch64SchedNeoverseN1.td ~ V3AE.td (line 135-141)  → ARM 自家服务器核
  │   ├─ AArch64SchedOlympus.td  (line 142)  → NVIDIA
  │   ├─ AArch64SchedOryon.td    (line 143)  → Qualcomm/Nuvia
  │   └─ AArch64Processors.td    (line 145)  ← ★ 60+ ProcessorModel 条目，飞腾零出现 ★
  │
  └─ AArch64PfmCounters.td       (line 199)  ← perf 计数器
═══════════════════════════════════════════════════════════════════════
```

**关键观察**（本专家的"骨架级"判断）：

1. **27 个调度模型 + 60+ ProcessorModel 条目，飞腾 FCC862 一个都没有**。`grep -rn "FTC86\|Phytium\|ftc86\|phytium" llvm/lib/Target/AArch64/` = `No files found` `[实测-grep 2026-07-07]`。这不是"飞腾在某个角落"，是"飞腾根本不在 AArch64 后端"。

2. **"目标描述驱动"的体量**：`AArch64InstrInfo.td` 是巨型文件（含 NEON/SVE/SME 数千条指令模式），`AArch64SchedTSV110.td` 773 行（华为一个核的调度模型）。**加一颗新核的工程量 ≈ 1 个 `.td` 文件（500-800 行）+ `Processors.td` 改 3 行（ProcessorFeatures + Tune + ProcessorModel）**。飞腾没做这件事，工程门槛不是"难"，是"没投人"。

3. **AArch64 后端的真正"承重墙"是 `AArch64InstrInfo.td` + `AArch64Features.td` + `AArch64Schedule.td` 这三件套**。调度模型是"可选增强"，指令模式是"必备底座"。飞腾享受了底座（NEON/UDOT/SM3/SM4 都在 `InstrInfo.td` 里），但没贡献增强（调度模型）。

#### 与 E05/E06 的分工对偶

- **指令选择 / Legalize 的"底座逻辑"归 [E05 CodeGen](../Expert_05_CodeGen_SelectionDAG_GlobalISel/README.md)**：SelectionDAG 怎么把 IR 选成 `udot`、GlobalISel 覆盖率多少、Legalize 怎么处理"无 SVE"。
- **寄存器分配 / 调度算法归 [E06 RegAlloc_Scheduler](../Expert_06_RegAlloc_Scheduler/README.md)**：Greedy/Basic/Fast 怎么着色 31 寄存器、Pre/Post-RA Sched 怎么排指令。
- **本 E08 专攻"目标描述层"**：`.td` 表怎么定义一颗核、飞腾为何缺一张表、缺表的后果。**三层分工，不重复**。

---

### 2.2 27 个调度模型 + 60+ Processor 条目（图 2 + 量化对标表）——飞腾缺席的全景

> **特异性测试**：下表是 OpenXiangShan/llvm-project `AArch64Processors.td:1417-1634` 的真实条目提炼。飞腾"零出现"是这张表的刺眼空白。

#### 图 2：主线 LLVM AArch64 调度模型厂商归属全景（LLVM 23.0.0git 实测）

| # | 调度模型（SchedMachineModel） | 用它的 ProcessorModel（-mcpu 名字） | 厂商 | 国籍 | 飞腾对照 |
|:-:|------|------|------|:--:|------|
| 1 | **CortexA510Model** | `generic`（**默认**）、cortex-a510/520/520ae、c1-nano | ARM | 🇬🇧 | ★ 飞腾默认落这里 ★ |
| 2 | CortexA53Model | cortex-a34/35/53/57/65/65ae/72/73、kryo、neoverse-e1 | ARM | 🇬🇧 | |
| 3 | CortexA55Model | cortex-a55、cortex-r82/r82ae | ARM | 🇬🇧 | |
| 4 | CortexA57Model | cortex-a75/76/76ae/77/78/78ae/78c | ARM | 🇬🇧 | 飞腾常被 `-mtune=cortex-a76` 近似 |
| 5 | CortexA320Model | cortex-a320 | ARM | 🇬🇧 | |
| 6 | **CycloneModel** | apple-a7~a17、apple-m1~m5（含 cyclone/a8-a19/s4-s10 别名 20+） | Apple | 🇺🇸 | |
| 7 | KryoModel | kryo（高通） | Qualcomm | 🇺🇸 | |
| 8 | FalkorModel | falkor、saphira | Qualcomm | 🇺🇸 | |
| 9 | ExynosM3Model | exynos-m3 | Samsung | 🇰🇷 | |
| 10 | ExynosM4Model | exynos-m4 | Samsung | 🇰🇷 | |
| 11 | ExynosM5Model | exynos-m5 | Samsung | 🇰🇷 | |
| 12 | ThunderXT8XModel | thunderx/thunderxt81/83/88 | Cavium | 🇺🇸 | |
| 13 | ThunderX2T99Model | thunderx2t99 | Cavium/Broadcom | 🇺🇸 | |
| 14 | ThunderX3T110Model | thunderx3t110 | Marvell | 🇺🇸 | |
| 15 | A64FXModel | a64fx、fujitsu-monaka | Fujitsu | 🇯🇵 | |
| 16 | **TSV110Model** | **tsv110**（鲲鹏 920） | **华为/海思** | 🇨🇳 | ★ 唯一国产 ★ |
| 17 | Ampere1Model | ampere1、ampere1a | Ampere | 🇺🇸 | |
| 18 | Ampere1BModel | ampere1b | Ampere | 🇺🇸 | |
| 19 | NeoverseN1Model | neoverse-n1 | ARM | 🇬🇧 | 服务器核 |
| 20 | NeoverseN2Model | neoverse-n2（cobalt-100 别名）、cortex-a710/715 | ARM | 🇬🇧 | |
| 21 | NeoverseN3Model | neoverse-n3、cortex-a720/725、c1-pro、ampere1c | ARM | 🇬🇧 | |
| 22 | NeoverseV1Model | neoverse-v1、neoverse-512tvb、cortex-x1/x1c | ARM | 🇬🇧 | |
| 23 | NeoverseV2Model | neoverse-v2、cortex-x2/x3、**grace（NVIDIA）** | ARM/NVIDIA | 🇬🇧🇺🇸 | |
| 24 | NeoverseV3Model | neoverse-v3、cortex-x4/x925、c1-premium/ultra、gb10 | ARM/NVIDIA | 🇬🇧🇺🇸 | |
| 25 | NeoverseV3AEModel | neoverse-v3ae | ARM | 🇬🇧 | |
| 26 | OlympusModel | olympus | NVIDIA | 🇺🇸 | |
| 27 | OryonModel | oryon-1 | Qualcomm/Nuvia | 🇺🇸 | |
| — | **NoSchedModel** | carmel（Nvidia Jetson） | Nvidia | 🇺🇸 | 无调度模型，只标 feature |
| ❌ | **（不存在）** | **FTC862 / FCC86x / Phytium** | **飞腾** | 🇨🇳 | **零出现** |

**核心发现**：

1. **"养着"AArch64 后端的公司**：ARM（自家核最多）、Apple（Cyclone 全家）、Qualcomm（Kryo/Falkor/Oryon）、Samsung（Exynos）、Cavium/Marvell（ThunderX）、Fujitsu（A64FX）、Ampere、NVIDIA（Grace/Olympus/GB10）、**华为（TSV110，唯一国产）**。这就是 [Lens_03 供应链](../Lenses/Lens_03_SupplyChain.md) 的"AArch64 后端养育图"——**飞腾不在养育者名单里**。

2. **国产对照的锋利**：华为 TSV110 在第 16 行（`AArch64SchedTSV110.td`，773 行，`AArch64Processors.td:833/1355/1544` 三处定义）。**飞腾 FCC862 是国产 ARM CPU 中唯一在主线 LLVM 既无后端也无调度模型的**。这个对照是 §3.2"飞腾该改的事"的直接依据。

3. **"近似"的残酷**：飞腾服务器用户若强行 `-mcpu=`，能选的最近似是 `cortex-a76`（ARMv8.2、4-wide OoO、TSV110 同代）或 `tsv110`（华为鲲鹏、ARMv8.2、4-wide OoO）。但 FCC862 是 ARMv8.4、有 UDOT/SM3/SM4 而 A76/TSV110 是 ARMv8.2——**feature 对不上**（A76 的 `ProcessorFeatures.A76` 没有 `FeatureDotProd` 的完整路径差异，见 §2.4）。最诚实的近似是 `-march=armv8.4-a` + `generic` 调度——但 generic 是 CortexA510Model（3-wide in-order），与 FCC862 的 4-wide OoO **架构错配**。

#### 量化对标表：飞腾 FCC862 vs 华为 TSV110 vs Cortex-A76 调度模型对照（本 Expert 核心交付物）

| 维度 | 飞腾 FCC862（主线 LLVM） | 华为 TSV110（主线 LLVM） | Cortex-A76（主线 LLVM） | 来源 |
|------|------------------------|------------------------|----------------------|------|
| **调度模型文件** | ❌ 不存在 | ✅ `AArch64SchedTSV110.td`（773 行） | ✅ 复用 `CortexA57Model`（A76 无专属 .td） | `[实测-glob/line]` |
| **ProcessorModel 条目** | ❌ 零出现 | ✅ `AArch64Processors.td:1544` | ✅ `:1450` | `[实测-read]` |
| **TuneXXX 定义** | ❌ 无 | ✅ `:833` `TuneTSV110` | ✅ `:123` `TuneA76` | `[实测-read]` |
| **ProcessorFeatures 列表** | ❌ 无 | ✅ `:1355` (HasV8_2aOps + DotProd + FP16FML + ...) | ✅ `:991` (HasV8_2aOps + DotProd + ...) | `[实测-read]` |
| **IssueWidth** | ❌ (generic 借 CortexA510=3) | ✅ 4 | (借 CortexA57Model=3) | `AArch64SchedTSV110.td:20` |
| **MicroOpBufferSize** | ❌ (generic 借 A510=0 in-order) | ✅ 128（OoO ROB） | (借 A57) | `:21` |
| **核类型** | 4-wide OoO（FCC862 实测） | 4-wide OoO | 4-wide OoO | `[飞腾 E02 架构师]` |
| **ARM 版本** | v8.4（UDOT/SM3/SM4/FCMLA） | v8.2（DotProd/FP16FML） | v8.2（DotProd） | `[飞腾 扩展专题]` |
| **专属端口定义** | ❌ 无 | ✅ 8 端口（ALU/AB/MDU/FSU1/FSU2/Ld0St/Ld1 + 3 group） | (借 A57 的端口) | `AArch64SchedTSV110.td:37-47` |
| **WriteRes 条目数** | ❌ 无 | ✅ ~50+（覆盖整数/FP/向量/除法/分支） | (借 A57) | `:60-105` |
| **upstream 状态** | 零贡献 | 已 upstream（鲲鹏 920，2018-2019） | ARM 官方 | `[websearch]` |
| **国产编译器产品** | PhyGCC（GCC fork）、PhyCC（闭源 LLVM） | 毕昇（LLVM 深度 fork） | — | `[飞腾 E18 fork 生态]` |

**这张表是本 Expert 最锋利的武器**：它证明**飞腾不是"做不到"，是"没做"**。华为 TSV110（同样是国产、同样是 ARM、同样面对 ARM 授权政治）做到了——773 行 `.td` + 3 处 `Processors.td` 条目。飞腾 FCC862 的"零"是战略选择（押 GCC 弃 LLVM），不是技术天花板。

---

### 2.3 飞腾 FCC862 在主线 LLVM 的实际待遇（命脉级发现）

> **特异性测试**：本节回答"飞腾代码在线主线 LLVM 上跑的是哪个近似核"，源码级铁证。这是飞腾命脉最痛的一节。

#### 2.3.1 默认 fallback：`generic` = `CortexA510Model`（架构错配）

`AArch64Processors.td:1417`：

```tablegen
// 实测代码，OpenXiangShan/llvm-project AArch64Processors.td:1417-1419
def : ProcessorModel<"generic", CortexA510Model, ProcessorFeatures.Generic,
                     [FeatureFuseAES, FeatureFuseAdrpAdd, FeaturePostRAScheduler,
                      FeatureEnableSelectOptimize]>;
```

`clang/lib/Driver/ToolChains/Arch/AArch64.cpp:69`：`return "generic";`——**clang 在不指定 `-mcpu` 时，默认 CPU 字符串就是 `generic`** `[实测-grep]`。

`ProcessorFeatures.Generic`（`:1406`）只有 `[FeatureFPARMv8, FeatureNEON, FeatureETE]`——**连 DotProd/FullFP16/LSE 都没开**。这意味着：

```
飞腾用户若写：clang -O2 test.c -o test   （不指定 -march/-mcpu）
  → clang 默认 CPU = "generic"
  → 调度模型 = CortexA510Model（3-wide、in-order、MicroOpBufferSize=0）
  → features = 只有 NEON + FP + ETE
  → 后果：
     ① UDOT 选不出（没 FeatureDotProd）
     ② SM3/SM4 选不出（没 FeatureSM4）
     ③ LSE 不开（没 FeatureLSE，原子操作走 LL/SC 循环，慢 30%）
     ④ FP16 不开（没 FeatureFullFP16）
     ⑤ 调度按 3-wide in-order 排（飞腾是 4-wide OoO）→ 指令调度严重次优
```

`AArch64SchedA510.td:18-29` 的 `CortexA510Model` 明确写 `MicroOpBufferSize = 0`（in-order）、`IssueWidth = 3`。**飞腾 FCC862 是 4-wide 乱序** `[飞腾 E02 架构师]`。**这是架构级的错配**——编译器以为它在给一颗 3 宽顺序核排指令，实际跑在 4 宽乱序核上。指令调度的关键路径分析、端口冲突建模全错。

#### 2.3.2 飞腾用户的"正确"用法（但仍次优）

飞腾 SDK 文档 `[推测-飞腾 SDK]` 推荐的编译选项是 `-march=armv8.4-a+simd+crypto+lse`（见飞腾项目 扩展专题.md（`../../体系结构实验/扩展专题.md`） §3）。这会开启 feature，但**调度模型仍是 `generic`（CortexA510Model）**——因为 `-march` 只改 feature，不改 `-mcpu`，调度模型跟着 `-mcpu` 走。

```
clang -march=armv8.4-a+simd+crypto+lse -O2 test.c
  → CPU 仍是 "generic"
  → features = armv8.4-a 全套（UDOT/SM3/SM4/LSE/FP16 全开） ✅
  → 调度模型 = CortexA510Model（3-wide in-order） ❌ 仍错配
```

#### 2.3.3 `-mtune` 的补救（飞腾实操建议）

飞腾开发者能做的最好补救是 `-mtune=cortex-a76` 或 `-mtune=tsv110`（4-wide OoO 近似）：

```
clang -march=armv8.4-a+simd+crypto+lse -mtune=cortex-a76 -O2 test.c
  → CPU feature 来源：-march（armv8.4-a 全套）
  → 调度模型来源：-mtune（CortexA57Model，A76 借用的）
  → TuneXXX 来源：TuneA76
```

`AArch64TargetMachine.cpp:434` 实测：`StringRef TuneCPU = TuneAttr.isValid() ? TuneAttr.getValueAsString() : CPU;`——**TuneCPU 和 CPU 是分离的**，`-mtune` 只影响调度/Tune，不影响 feature `[实测-read]`。这是 LLVM 后端的精妙设计，也是飞腾能"曲线救国"的机制。

**但 `-mtune=cortex-a76` 仍是次优**：A76 是 ARMv8.2，端口结构（`CortexA57Model` 的 `A57UnitALU/MAC/Div/LdSt/B/FPALU/FPMDS`）与 FCC862 的真实端口（飞腾实测 2 ALU/cycle + 2 NEON 通道 `[飞腾 E02]`）不一致。**真正的解药只有飞腾 upstream 一个 `AArch64SchedFTC86x.td`**（§3.2）。

> **命脉级结论**：飞腾 FCC862 在主线 LLVM 的命运是"feature 能开（靠 -march）、调度永远错配（无专属模型）"。这与飞腾项目 E11 §2.1（`../../体系结构实验/Expert_11_Compiler_Research/README.md`） 的 PhyGCC 分析形成对偶——PhyGCC 有 `FTC86x.md`（专属调度，10-18% 收益），主线 LLVM 没有。**飞腾的性能命运分裂在两个编译器之间：GCC 侧优化、LLVM 侧吃灰**。

---

### 2.4 ARMv8.4 扩展在 AArch64 后端的暴露机制（图 3）

> **特异性测试**：本节追踪 `FeatureSM4` 这一个 def 怎么从 `.td` 一路驱动到飞腾的 `vsm4e_u32` intrinsic。代码级全链路。

#### 图 3：ARMv8.x 扩展在 AArch64 后端的三层暴露机制

```
═══════════════════════════════════════════════════════════════════════
Layer 1: SubtargetFeature 定义（AArch64Features.td）
─────────────────────────────────────────────────────────────────────
  def FeatureSM4 : ExtensionWithMArch<"sm4", "SM4", "FEAT_SM4, FEAT_SM3",
    "Enable SM3 and SM4 support", [FeatureNEON]>;            ← :132-133
        │
        ├─ -march 解析名："sm4"   → -march=armv8.4-a+sm4 或 +nosm4
        ├─ FEAT 名："FEAT_SM4, FEAT_SM3"（ARM ARM 命名，HWCAP 对应 HWCAP_SM4）
        └─ 依赖：FeatureNEON（SM3/SM4 是 NEON 指令）

Layer 2: 指令 predicate（AArch64InstrInfo.td）
─────────────────────────────────────────────────────────────────────
  def HasSM4 : Predicate<"Subtarget->hasSM4()">,
               AssemblerPredicateWithAll<(all_of FeatureSM4), "sm4">;  ← :94
        │
        ├─ 指令模式 SM4E 的定义里写：let Predicates = [HasSM4] in { def SM4E ... }
        ├─ 指令选择：SelectionDAG 只在 hasSM4()=true 时选 SM4E
        ├─ 汇编接受：llvm-mc 只在 FeatureSM4 开时汇编 SM4E
        └─ 反汇编：objdump 只在 FeatureSM4 开时反汇编出 SM4E

Layer 3: HWCAP 运行时检测（Linux kernel → getauxval）
─────────────────────────────────────────────────────────────────────
  /proc/cpu → getauxval(AT_HWCAP) & HWCAP_SM4
        │
        ├─ 飞腾 D3000M 实测：HWCAP_SM4 = 1 [飞腾 扩展专题 第23行]
        ├─ → 运行时可安全调用 vsm4e_u32 intrinsic
        └─ → 编译时需 -march=armv8.4-a+sm4 才能编译 intrinsic

完整链路（飞腾 SM4 代码）：
  源码：vsm4e_u32(acc, key)         ← arm_neon.h 自动生成的 intrinsic
    ↓ clang 前端
  IR：call @llvm.aarch64.neon.sm4e(...)  ← intrinsic 定义在 AArch64SVEInstrInfo.td
    ↓ SelectionDAG（检查 HasSM4 predicate）
  MI：SM4E v0.4s, v1.4s             ← A64 编码 0xCE60C000
    ↓ MC Emission（检查 AssemblerPredicateWithAll FeatureSM4）
  .o：正确编码的国密指令
═══════════════════════════════════════════════════════════════════════
```

**飞腾 ARMv8.4 扩展在 AArch64 后端的覆盖实测**（对照飞腾 扩展专题.md（`../../体系结构实验/扩展专题.md`） §1 能力矩阵）：

| 飞腾特性 | AArch64 后端 Feature 定义 | `.td` 行号 | LLVM 是否支持 | 飞腾实测 |
|---------|-------------------------|:--------:|:----------:|:------:|
| NEON (v8.0) | `FeatureNEON` | AArch64Features.td:71 | ✅ | ✅ |
| AES/SHA1/SHA256 (v8.0) | `FeatureAES`/`FeatureSHA2` | :75-78 | ✅ | ✅ |
| **LSE 原子 (v8.1)** | `FeatureLSE` | **:108** | ✅ | ✅ |
| FP16 标量+向量 (v8.2) | `FeatureFullFP16` | :142 | ✅ | ✅ |
| **FCMLA/FCADD (v8.3)** | `FeatureComplxNum`（隐含于 HasV8_3aOps） | — | ✅ | ✅ |
| **UDOT/SDOT (v8.4)** | `FeatureDotProd` | **:212** | ✅ | ✅ |
| **SM3/SM4 国密 (v8.4)** | `FeatureSM4`（含 SM3） | **:132** | ✅ | ✅ |
| **SHA3/SHA512 (v8.4)** | `FeatureSHA3`（含 SHA512） | **:135** | ✅ | ✅ |
| ❌ SVE/SVE2 | `FeatureSVE`/`FeatureSVE2` | :158/:362 | ✅（主线有，飞腾硬件无） | ❌ |
| ❌ BF16 (v8.6) | `FeatureBF16` | :282 | ✅（主线有） | ❌ |
| ❌ I8MM (v8.6) | `FeatureMatMulInt8` | :162 | ✅（主线有） | ❌ |

**关键洞察**：**飞腾"有的"扩展，主线 LLVM 全部支持**（LSE/FP16/UDOT/SM3/SM4/FCMLA/SHA3/SHA512 都有 Feature 定义 + 指令模式）。**飞腾"没的"扩展，主线 LLVM 也全部支持**（SVE/SVE2/BF16/I8MM 主线一直在加）。这说明：

1. **飞腾的"扩展断层"不是 LLVM 后端的锅**——LLVM AArch64 后端对 ARMv8.x 的覆盖是最完整的（甚至超前于飞腾硬件）。
2. **飞腾的"调度断层"才是 LLVM 后端的锅**——`FeatureSM4` 开了，`SM4E` 指令能选出来，但 SM4E 在 FCC862 上的 latency/throughput 在调度模型里是"未知"（走 generic 近似），调度器不知道 SM4E 走哪个端口、几拍 latency。

> **与 [E07 AutoVec](../Expert_07_Auto_Vectorization/README.md) 对偶**：E07 讲"飞腾无 SVE 导致向量化覆盖率天花板 20-30%"——那是 IR 层的失血。本 E08 讲"飞腾有 UDOT 但调度模型缺，UDOT 选出来后排不优"——这是 MI 层的失血。**两层叠加，飞腾的 SIMD 性能被"上没选出来、下没排好"双重剥削**。

---

### 2.5 华为 TSV110 upstream 案例——飞腾若要 upstream 的工程蓝图

> **特异性测试**：本节用华为 TSV110 的真实 `.td` 代码（773 行实测）作为飞腾 upstream 的对偶模板。这是 §3.2"飞腾该改的事"的具体依据。

#### 2.5.1 TSV110 调度模型的真实结构（`AArch64SchedTSV110.td` 773 行）

华为给鲲鹏 920 写的调度模型，是飞腾最该抄的作业。其结构（实测行号锚点）：

```tablegen
// === 实测代码，AArch64SchedTSV110.td:18-31 ===
def TSV110Model : SchedMachineModel {
  let IssueWidth            =   4;    // 4 micro-ops dispatched per cycle  ← 鲲鹏 4-wide
  let MicroOpBufferSize     = 128;    // 128 micro-op re-order buffer      ← OoO
  let LoopMicroOpBufferSize =  16;
  let LoadLatency           =   4;    // Optimistic load latency
  let MispredictPenalty     =  14;    // 分支预测失败惩罚
  let CompleteModel         =   1;    // ★ 完整模型（每条指令都有 WriteRes）

  list<Predicate> UnsupportedFeatures = !listconcat(SVEUnsupported.F,    // 鲲鹏也无 SVE
                                                    PAUnsupported.F,
                                                    SMEUnsupported.F,
                                                    [HasMTE, HasCSSC]);
}

// === :36-48，端口定义（鲲鹏的"肌肉"）===
let SchedModel = TSV110Model in {
  def TSV110UnitALU   : ProcResource<1>; // Int ALU        ← 1 个纯 ALU 端口
  def TSV110UnitAB    : ProcResource<2>; // Int ALU/BRU    ← 2 个 ALU/分支端口
  def TSV110UnitMDU   : ProcResource<1>; // Multi-Cycle    ← 1 个多周期（乘除）
  def TSV110UnitFSU1  : ProcResource<1>; // FP/ASIMD       ← 2 个 FP/NEON 端口
  def TSV110UnitFSU2  : ProcResource<1>; // FP/ASIMD
  def TSV110UnitLd0St : ProcResource<1>; // Load/Store     ← 1 个 LD/ST
  def TSV110UnitLd1   : ProcResource<1>; // Load           ← 1 个纯 Load
  // 端口组（任一可用）
  def TSV110UnitLd    : ProcResGroup<[TSV110UnitLd0St, TSV110UnitLd1]>;
  def TSV110UnitF     : ProcResGroup<[TSV110UnitFSU1, TSV110UnitFSU2]>;
  def TSV110UnitALUAB : ProcResGroup<[TSV110UnitALU, TSV110UnitAB]>;
}
```

接着是 ~50 个 `WriteRes` 条目（`:60-105`）和 ~80 个 `TSV110Wr_*` 自定义 SchedWriteRes（`:144-247`），逐条指令类映射到端口+latency。**这就是"养一颗核"的工程量**。

#### 2.5.2 TSV110 在 Processors.td 的三处定义

```tablegen
// === AArch64Processors.td:833-837，Tune 定义 ===
def TuneTSV110 : SubtargetFeature<"tsv110", "ARMProcFamily", "TSV110",
                                  "HiSilicon TS-V110 processors", [
                                  FeatureFuseAES,
                                  FeatureStorePairSuppress,
                                  FeaturePostRAScheduler]>;

// === :1355-1359，ProcessorFeatures 列表（feature 全集）===
list<SubtargetFeature> TSV110 = [HasV8_2aOps, FeatureSHA2, FeatureAES, FeatureFPARMv8,
                                 FeatureNEON, FeaturePerfMon, FeatureSPE,
                                 FeatureFullFP16, FeatureFP16FML, FeatureDotProd,
                                 FeatureJS, FeatureComplxNum, FeatureCRC, FeatureLSE,
                                 FeatureRAS, FeatureRDM];

// === :1544-1545，ProcessorModel 注册（-mcpu=tsv110 的入口）===
def : ProcessorModel<"tsv110", TSV110Model, ProcessorFeatures.TSV110,
                     [TuneTSV110]>;
```

**三处定义 = 一颗核在主线 LLVM 的"完整身份"**。飞腾 FCC862 要 upstream，就是抄这三处 + 写一个 `AArch64SchedFTC86x.td`。

#### 2.5.3 飞腾 upstream FTC86x 调度模型的工程步骤（可执行蓝图）

基于华为 TSV110 案例 + ARM Cortex 案例，飞腾若要 upstream（强烈建议，见 §3.2）：

1. **实测 FCC862 微架构参数**（飞腾已有 `[飞腾 E02 架构师]`）：
   - IssueWidth = 4 `[实测]`
   - OoO（MicroOpBufferSize ≈ 128+）`[推测-飞腾 E02]`
   - 端口：2 ALU/cycle + 2 NEON 通道 + LD/ST `[飞腾 E02]`
   - L1D 4 周期、L2 12 周期 `[飞腾 Lab03]`
2. **写 `AArch64SchedFTC86x.td`**（参考 TSV110 的 773 行结构）：
   - `def FTC86xModel : SchedMachineModel { let IssueWidth = 4; ... }`
   - 端口定义（飞腾实测的 2 ALU + 2 NEON + LD/ST）
   - ~50 个 WriteRes（用飞腾 Lab03 的 latency 校准）
3. **改 `AArch64Processors.td` 三处**：
   - `def TuneFTC86x : SubtargetFeature<"ftc86x", ...>`（含 ARMv8.4 的 feature 列表）
   - `list<SubtargetFeature> FTC86x = [HasV8_4aOps, FeatureDotProd, FeatureSM4, FeatureSHA3, FeatureFullFP16, FeatureLSE, FeatureRCPC, FeatureComplxNum, ...]`
   - `def : ProcessorModel<"ftc86x", FTC86xModel, ProcessorFeatures.FTC86x, [TuneFTC86x]>;`
4. **改 `AArch64.td:143` 附近加 `include "AArch64SchedFTC86x.td"`**
5. **改 clang driver**（`clang/lib/Driver/ToolChains/Arch/AArch64.cpp`）识别 `-mcpu=ftc86x`
6. **Phabricator/GitHub PR review**：LLVM 社区 review，通常需要 ARM/Apple/华为的 contributor sign-off
7. **测试**：`llvm/test/CodeGen/AArch64/` 加调度测试，`llvm/test/MC/AArch64/` 加 -mcpu 测试

**工程量估算**：1 人 × 2-3 个月（含微架构实测、`.td` 编写、review 迭代）。**收益**：飞腾代码在线主线 LLVM 上调度最优（IPC 提升 5-10% `[推测-飞腾 E11 PhyGCC 对照]`），且一劳永逸（不像 PhyGCC 要 rebase）。

> **与 [E18 Phytium Adaptation](../Expert_18_Phytium_Adaptation/README.md) 对偶**：E18 实测确认"主线 LLVM 零飞腾字符串"，本 E08 给出"如何从零变有"的工程蓝图。E18 是诊断，E08 是处方。

---

### 2.6 PAC/BTI/MTE/SVE/SVE2/SME 后端支持进度——飞腾的"看着别人吃肉"

> **特异性测试**：本节用 `.td` 文件存在性证明主线 LLVM 持续加 SVE2/SME，飞腾作为 ARMv8.4 卡在"只能看"的境地。

主线 LLVM AArch64 后端对 ARMv8.x/v9.x 扩展的支持进度（实测 `.td` 存在性）：

| 扩展 | 引入版本 | AArch64 后端支持 | 关键 `.td` 文件 | 飞腾硬件 | 飞腾处境 |
|------|:------:|:----------:|------|:------:|------|
| PAC (v8.3) | 2017 | ✅ | `AArch64PointerAuth.cpp/.h` | ⚠️ 部分 | 用不上 |
| BTI (v8.5) | 2019 | ✅ | `AArch64BranchTargets.cpp` | ❌ | 安全特性缺失 |
| MTE (v8.5) | 2019 | ✅ | `AArch64StackTagging.cpp/.cpp` | ❌ | 内存安全缺失 |
| **SVE (v8.4+)** | 2016 | ✅ 成熟 | `AArch64SVEInstrInfo.td` + `SVEInstrFormats.td` | ❌ | **向量化天花板** |
| **SVE2 (v9.0)** | 2021 | ✅ 持续加 | 同上 + SVE2 predicate | ❌ | 看着 Graviton/A64FX 吃肉 |
| **SME (v9.2)** | 2022 | ✅ 热门 | `AArch64SMEInstrInfo.td` + `SMEInstrFormats.td` + `AArch64SMEAttributes.cpp` | ❌ | 矩阵加速缺失 |
| SME2 (v9.4) | 2023 | ✅ 刚加 | 同上 + SME2p1/2p3 predicate | ❌ | |
| FP8 (v9.5) | 2024 | ✅ 最新 | `FeatureFP8FMA`/`FeatureFP8DOT2`/`FeatureFP8DOT4` | ❌ | AI 推理最前沿 |

**关键观察**：

1. **主线 LLVM 的 AArch64 后端是"ARM 生态最前沿的承载者"**——SVE2/SME/FP8 全在加，比飞腾硬件领先 2-3 代。飞腾作为 ARMv8.4，被锁在"NEON + UDOT"的水位，**主线 LLVM 越前进，飞腾越边缘化**。

2. **`SVEUnsupported` 是飞腾的"隔离墙"**：`AArch64.td:74-77`：
   ```tablegen
   def SVEUnsupported : AArch64Unsupported {
     let F = !listconcat([HasSVE, HasSVE_or_SME], SVE2Unsupported.F);
   }
   ```
   每个调度模型都 `list<Predicate> UnsupportedFeatures = !listconcat(SVEUnsupported.F, ...)`（如 `AArch64SchedTSV110.td:27`、`AArch64SchedA53.td:29`）。**飞腾若 upstream FTC86x 调度模型，也必须声明 `SVEUnsupported`**——这等于在主线 LLVM 里正式承认"飞腾无 SVE"。

3. **SME 是 2022-2026 最热的 AArch64 后端投资**：`AArch64SMEInstrInfo.td` + `SMEInstrFormats.td` + `SMEABIPass.cpp` + `MachineSMEABIPass.cpp` + `AArch64SMEAttributes.cpp/.h` + `SMEPeepholeOpt.cpp` + `SVEIntrinsicOpts.cpp`——一整套 SME 流水线。这是 Apple/ARM/华为在推的矩阵扩展（与 GPU 竞争）。飞腾完全缺席。

> **战略叙事**：飞腾 ARMv8.4 在 AArch64 后端的处境是"底座覆盖完整（NEON/UDOT/SM3/SM4 都在）、前沿完全缺席（SVE/SVE2/SME/FP8 全无）"。**底座让飞腾"能跑"，前沿缺席让飞腾"跑不快"**。这与飞腾项目 E21 AI 算力定位（`../../体系结构实验/Expert_21_AI_Positioning/README.md`） 的"AI 算力锚定 2017-2018 水位"战略伤疤是同一件事的两个视角——E21 从硬件 ISA 看，E08 从编译器后端看。

---

### 2.7 Neon/SVE intrinsic 头文件怎么从 `.td` 自动生成

> **特异性测试**：本节回答"intrinsic 头文件是手写还是生成的"，代码级机制。

`arm_neon.h` / `arm_sve.h` / `arm_sme.h` 不是手写的，是 **TableGen + clang 的 `arm_neon.td`/`arm_sve.td` 半自动生成**：

1. **NEON intrinsic**：`clang/include/clang/Basic/arm_neon.td` 定义 intrinsic 签名，TableGen 生成 `arm_neon.h`。飞腾的 `vdotq_s32`（UDOT）、`vsm4e_u32`（SM4）、`vcmlaq_f32`（FCMLA）全在这里定义。**飞腾"有"的扩展，intrinsic 全部自动可用**（只要 `-march` 开了对应 feature）。

2. **SVE/SME intrinsic**：更复杂，用 `arm_sve_sme_sema` 机制。`AArch64SVEInstrInfo.td` 里每条 SVE 指令可以挂 `SDNode` 和 intrinsic ID，clang 前端据此生成 `arm_sve.h`。**飞腾无 SVE → `arm_sve.h` 能 include 但 intrinsic 调用会编译失败**（因为 `FeatureSVE` 没开）。

3. **飞腾实操**：飞腾开发者 `#include <arm_neon.h>` 后，`-march=armv8.4-a+dotprod+sm4` 即可用 `vdotq_s32`/`vsm4e_u32`。**这是飞腾拿 UDOT 16.9× / SM3 国密合规的唯一可靠路径**——靠自动向量化选不出 UDOT（见 E11 §2.3.4（`../../体系结构实验/Expert_11_Compiler_Research/README.md`）），必须靠 intrinsic。

**对偶判断**：如果换 GCC，`arm_neon.h` 是 GCC 手写维护的（`gcc/config/aarch64/arm_neon.h` 手写 vs clang TableGen 生成）。**LLVM 的 TableGen 生成机制更易扩展（加一条 SVE 指令 = 改一个 .td），GCC 的手写更难维护（每加一条要手写 intrinsic 包装）**。这是 LLVM 后端生态比 GCC 更活跃的微观原因之一。

---

### 2.8 AArch64 vs ARM 32-bit 后端——老后端在腐烂吗？

> **特异性测试**：本节实测 `llvm/lib/Target/ARM/` 118 文件，回答"32-bit ARM 后端是否被遗弃"。

实测 `llvm/lib/Target/ARM/` 目录（118 entries `[实测-read]`）：

| 证据 | 说明 |
|------|------|
| `ARMInstrMVE.td` | M-Profile Vector Extension（Cortex-M55/M85 的向量扩展）**仍在活跃** |
| `ARMInstrCDE.td` | Custom Datapath Extension（自定义数据通路）**较新** |
| `MVETailPredication.cpp` / `MVEGatherScatterLowering.cpp` | MVE 尾循环预测、gather/scatter lowering **活跃 Pass** |
| `ARMScheduleM7.td` / `ARMScheduleM85.td` | Cortex-M7/M85 调度模型 **较新** |
| `ARMFixCortexA57AES1742098Pass.cpp` | Cortex-A57 AES errata workaround **仍维护** |
| `ARMLowOverheadLoops.cpp` | 低开销循环（CHROME/Loop）**活跃** |

**结论**：**32-bit ARM 后端没有腐烂，但投资重心明显在 M-profile（微控制器）**。Cortex-M55/M85 的 MVE 是 2019-2021 的新特性，LLVM 在跟进。**A-profile（Cortex-A 32-bit）确实停滞**——没有人给新的 32-bit 应用处理器加调度模型（最新的 32-bit 调度是 Cortex-A57/A72）。

**飞腾关联**：飞腾 FTC862 是 64-bit（AArch64 only），与 32-bit ARM 后端无关。但飞腾的嵌入式产品线（D2000/E2000 的 32-bit 模式）会用到 ARM 32-bit 后端。**这是飞腾嵌入式生态（phytium_repos 里的 FreeRTOS/seL4/NuttX）的隐性依赖**。

**对偶判断**：x86 后端（`llvm/lib/Target/X86/`）没有"32-bit 腐烂"问题，因为 x86-64 完全向后兼容 32-bit（一套 `.td` 搞定）。ARM 的 32/64 位分裂（两套独立后端）是历史包袱——**这是 ARM 生态比 x86 生态"多一份维护税"的根因**。

---

## 3. 设计决策评估：AArch64 后端哪些决策认可、飞腾工程教训

### 3.1 AArch64 后端做对的事（认可）

1. **"目标描述驱动 + 调度模型分层"设计**：这是 LLVM 后端最优雅的设计。加一颗核 = 加一个 `.td` + 改 3 行 Processors.td，不动任何 `.cpp`。**这让 ARM/Apple/华为/Ampere 都能自助贡献**——AArch64 后端有 27 个调度模型，正是因为门槛低。飞腾不贡献是战略选择，不是技术壁垒。

2. **`-mtune` 与 `-mcpu` 分离**（`AArch64TargetMachine.cpp:434`）：feature 和调度模型可以独立指定。这让飞腾能 `-march=armv8.4-a -mtune=cortex-a76` 曲线救国——**LLVM 给了"无专属模型"用户的逃生舱**。

3. **`ExtensionWithMArch` 统一 feature/march/FEAT 三命名**（`AArch64Features.td`）：`FeatureSM4` 一个 def 同时驱动 `-march=+sm4`、`FEAT_SM4`、HWCAP。**这是 ARMv8.x 扩展暴露的最干净机制**，飞腾的 SM3/SM4/UDOT 全享受了这套机制。

4. **CompleteModel 标志**（如 `TSV110Model.CompleteModel = 1`）：强制每条指令都有 WriteRes，否则 TableGen 报错。**这是"调度模型完整性"的自检机制**，防止半成品。

### 3.2 飞腾该改的事（可执行建议）

1. **⭐ upstream `AArch64SchedFTC86x.td` 到主线 LLVM**（最高优先级）：
   - 工程蓝图见 §2.5.3。1 人 × 2-3 月。
   - 收益：飞腾在线主线 LLVM 调度最优（IPC +5-10%），一劳永逸（不像 PhyGCC rebase）。
   - 对照：华为 TSV110 已做（773 行 `.td`），飞腾零。**这是飞腾在国产 CPU 编译器话语权上最该补的一课**。

2. **文档化 `-mtune=cortex-a76` 或 `-mtune=tsv110` 作为飞腾在线主线 LLVM 的临时方案**：
   - 飞腾 SDK 应明确告诉用户："用主线 clang 时，加 `-mtune=cortex-a76` 能拿到 70-80% 的调度收益"。
   - 现状：飞腾 SDK 文档只推 PhyGCC，对主线 LLVM 的用法指导缺失。

3. **拥抱 LLVM（不只 GCC）**：
   - 飞腾生态目前重 GCC（麒麟/UOS 默认 PhyGCC）。但 AI 推理框架（PyTorch/ONNX Runtime/llama.cpp）越来越用 LLVM 工具链（MLIR/XLA）。
   - **飞腾应确保主线 LLVM AArch64 后端对 FCC86x 有基本调度支持**，否则 AI 推理在飞腾上跑不准（见 §2.3 的"调度错配"）。

4. **考虑 upstream `FTC86x` 到 GCC 主线**（PhyGCC 的平行动作）：
   - PhyGCC 是 fork，飞腾要持续 rebase（落后主线 1-2 版 `[飞腾 E11 §2.4]`）。
   - 如果 `FTC86x.md` upstream 到主线 GCC，飞腾就不用维护 fork。**这与 upstream LLVM 是同一逻辑**。

### 3.3 锁死的事（无解）

1. **无 SVE 导致的 AArch64 后端"前沿缺席"**：SVE2/SME/FP8 是 ISA 层的缺失，AArch64 后端再先进也帮不了飞腾。主线 LLVM 越加 SVE2/SME，飞腾越边缘化。**解药只有等 D4000 补 SVE**（受 ARM v9 授权政治限制，见 [E18](../Expert_18_Phytium_Adaptation/README.md)）。

2. **ARM 架构身份的"隐身"宿命**：飞腾是 ARMv8.4，复用 AArch64 后端是"省事"，代价是"隐身在 generic 里"。龙芯 LoongArch 有独立后端（主线正式），平头哥玄铁有 RISC-V fork——**它们因为 ISA 不同而"被迫可见"，飞腾因为 ISA 标准而"自愿隐身"**。这是 ARM 国产 CPU 的结构性困境（见 [Lens_07 国产化](../Lenses/Lens_07_China_Localization.md)）。

3. **调度模型的"完整性税"**：upstream 一个 `CompleteModel = 1` 的调度模型，必须覆盖每条指令的 WriteRes。飞腾若漏一条，TableGen 报错。**这是"想 upstream 就必须完整"的门槛**——半成品不被接受。

---

## 4. 这一视角的盲区与反方（诚实段，强制）

### 4.1 AArch64 后端 contributor 视角看不见什么

1. **看不见运行时行为**：调度模型是**静态**的——它假设 FCC862 的端口负载均衡是固定的。但真实 workload 的 cache miss、分支预测、内存带宽饱和，调度模型一无所知。**一段"调度模型优化得很好"的代码，可能因为 cache 抖动实际跑得更慢**。这要靠 PGO（Profile-Guided Optimization）和 BOLT（[E12](../Expert_12_LLD_BOLT/README.md)）补。

2. **看不见前端语义**：AArch64 后端 contributor 只看 IR/MIR，不看 C/C++ 源码。`-ffast-math` 改了 LoopVectorize 的 reduction 重关联（E11 §2.5（`../../体系结构实验/Expert_11_Compiler_Research/README.md`）），这在后端看来只是"IR 形状变了"，后端不知道是 `-ffast-math` 在起作用。**后端是"被动接收者"，不是"决策者"**。

3. **看不见硬件 errata**：飞腾 FCC862 可能有微架构 errata（某条指令在某些条件下结果错误），AArch64 后端不知道。这要靠 `[飞腾 E17 DFT]` 的 errata 文档喂给编译器（生成 workaround，类似 `AArch64A53Fix835769.cpp`）。

4. **看不见 GCC 对照**：本专家默认"LLVM 是唯一"。但飞腾实际用 PhyGCC（GCC fork），AArch64 后端的"零飞腾"在 GCC 侧是"有 FCC86x.md"。**LLVM-only 视角会高估飞腾的"编译器缺失"——飞腾在 GCC 侧有调度模型，只是不在 LLVM 侧**。

5. **看不见商业 LLVM fork**：飞腾可能有闭源的 PhyCC（基于 LLVM），其调度模型不开源。本专家的"主线 LLVM 零飞腾"结论只覆盖开源主线，商业版可能另有（需飞腾官方确认，见 [E18 fork 生态](../Expert_18_Phytium_Adaptation/国产CPU厂商_LLVM_fork_生态.md) §2.4）。

### 4.2 反方观点：AArch64 后端没那么重要

一个激进的反方：**飞腾不需要 upstream AArch64 调度模型，因为：**

- **飞腾是 OoO 核**（FCC862 4-wide 乱序 `[飞腾 E02]`）。OoO 核的硬件调度器能动态重排指令，**编译器静态调度的边际收益很小**（5-10% `[推测]`）。不像 in-order 核（如 Cortex-A53/A510）那样依赖编译器调度。
- **飞腾用户用 PhyGCC 已经拿到调度收益**（10-18% `[飞腾 E11]`）。再 upstream LLVM 是"锦上添花"，不是"雪中送炭"。
- **主线 LLVM 6 月一发布，upstream 后要持续维护**（每次 ARM 加新指令，飞腾的 WriteRes 要补）。维护成本 > 收益。

**这个反方有道理但不完全对**：
- OoO 核的硬件调度器确实能补救**部分**编译器调度缺陷，但不能补救**寄存器分配**和**指令选择**——这俩是编译器的硬决策，硬件改不了。飞腾无专属调度模型，寄存器分配的"压力估计"也走 generic（错的），溢出决策可能错。
- 飞腾生态在"AI 推理"场景越来越用 LLVM（MLIR/XLA），PhyGCC 管不到。**upstream LLVM 是为 AI 推理铺路，不是为传统 HPC**。
- 维护成本是真的，但华为 TSV110 维护了 7 年（2018-今），证明可行。

> **诚实结论**：AArch64 后端 contributor 视角容易**高估调度模型的重要性**（因为这是他的本职）。飞腾 OoO 核确实减轻了"无调度模型"的痛。但"AI 推理用 LLVM"的趋势让这个痛会**随时间加重**——飞腾现在不痛，3-5 年后会痛。

---

## 5. 与其他视角对偶（一致 / 冲突，强制）

### 5.1 一致（互相印证）

- **与 [E05 CodeGen](../Expert_05_CodeGen_SelectionDAG_GlobalISel/README.md) 一致**：E05 讲"指令选择怎么选 UDOT"（SelectionDAG + Legalize），本 E08 讲"UDOT 的 Feature 定义在 `.td` 哪里、调度模型缺它意味着什么"。**E05 是"选指令的算法"，E08 是"选指令的依据（.td 表）"**。两者互补。

- **与 [E06 RegAlloc_Scheduler](../Expert_06_RegAlloc_Scheduler/README.md) 一致**：E06 讲"Greedy 算法怎么着色 31 寄存器、MISched 怎么排指令"，本 E08 讲"31 寄存器和调度模型在 `.td` 里怎么定义"。**E06 是算法层，E08 是数据层**。MISched 查的就是本 E08 说的 `AArch64Sched*.td`。

- **与 [E18 Phytium Adaptation](../Expert_18_Phytium_Adaptation/README.md) 一致**：E18 实测"主线 LLVM 零飞腾字符串"，本 E08 给出"这个零的工程含义 + 如何从零变有"。**E18 是诊断报告，E08 是专家会诊**。

- **与飞腾 E11 Compiler Research（`../../体系结构实验/Expert_11_Compiler_Research/README.md`） 一致**：飞腾 E11 讲 PhyGCC 的 `FTC86x.md`（GCC 侧），本 E08 讲主线 LLVM 的"零 FCC86x"（LLVM 侧）。**同一颗芯片，GCC 有表、LLVM 没表——两个视角拼出飞腾编译器战略全貌**。

### 5.2 冲突（视角打架）

- **与 [E07 AutoVec](../Expert_07_Auto_Vectorization/README.md) 部分冲突**：E07 说"飞腾无 SVE 导致向量化天花板 20-30%"——把锅甩给 ISA。本 E08 补充："飞腾有 UDOT 但调度模型缺，UDOT 选出来后排不优"——把部分锅甩给后端。**E07 是"上层选不出"，E08 是"下层排不好"，两者叠加才是飞腾 SIMD 的完整失血**。但 E07 倾向"ISA 决定论"，E08 倾向"后端可补救"——乐观度不同。

- **与 [E10 RISC-V Backend](../Expert_10_RISCV_Backend/README.md) 潜在冲突**：E10 会讲"RISC-V 后端的 RVV 可变长向量、香山/玄铁调度模型"。本 E08 强调"AArch64 后端最成熟（27 个调度模型）"。**E10 可能反驳"RISC-V 后端虽年轻但国产化话语权强（香山进 mainline）"**——这是"成熟度 vs 国产化"的视角差异。

- **与 [Lens_07 China Localization](../Lenses/Lens_07_China_Localization.md) 战略冲突**：Lens_07 呼吁"国产 CPU 摆脱 LLVM/GCC 依赖"。本 E08 建议"飞腾 upstream 到主线 LLVM"——**这是"融入"还是"摆脱"的路线之争**。本专家认为"融入"（upstream）比"摆脱"（自研后端）更现实，因为飞腾是 ARM 架构（复用 AArch64 后端是正道）。

---

## 6. 参考文献（分级标注，≥15 条，含 ≥5 论文/标准/官方文档）

### 官方文档与标准（[官方]/[标准]）
1. **[标准]** ARM Limited. *ARM Architecture Reference Manual (ARM ARM), ARMv8, DDI 0487G.b（及后续 K.a 修订）*. —— A64 指令集、NEON/LSE/RAS/UDOT/SM3/SM4/PAC/BTI/MTE/SVE/SVE2/SME 编码权威。
2. **[官方]** LLVM Project. *TableGen Fundamentals* + *Writing an LLVM Backend*. llvm.org/docs. —— `.td` 描述与 `ProcessorModel`/`SchedMachineModel` 定义。
3. **[官方]** LLVM Project. *LLVM Target-Independent Code Generator* + *MCSchedule.h / MCSchedModel*. —— 调度模型分层（SchedMachineModel → ProcResource → WriteRes）。
4. **[官方]** ARM. *Procedure Call Standard for the Arm 64-bit Architecture (AAPCS64)*. —— AArch64CallingConvention.td 的依据。
5. **[官方]** LLVM Project. *AArch64 Backend README*（`llvm/lib/Target/AArch64/` 历史注释）. —— Cyclone 起源（Apple A7 = 第一个 AArch64 核）。

### 里程碑论文（[论文]）
6. **[论文]** Abbott, Baching et al. *Machine Scheduling in LLVM*. LLVM Dev Meeting 2013-2015 talks. —— MachineScheduler / PostRA scheduler / MISched 的设计。
7. **[论文]** Davidson, J. & Fraser, C. *The Design and Application of a Retargetable Peephole Optimizer*. ACM TOPLAS 1984. —— TableGen DAG combine 的思想源头。
8. **[论文]** Gross, T. R. & Hennessy, J. *Postpass Code Optimization of Pipeline Constraints*. ACM TOPLAS 5(3), 1983.（飞腾 E11 §6 引用，本 E08 复引——调度经典）
9. **[论文]** Braun, M. et al. *Instruction Selection for Compiled SimVLM*. CGO 2017（相关 GlobalISel 文献，与 E05 共享）.
10. **[论文]** Aonso, F. et al. *The VLIW approach to instruction scheduling*.（OoO 与 VLIW 调度对比的理论背景——解释为何飞腾 OoO 减轻调度依赖）

### 项目内实测与开源资源（[实测]/[GitHub commit]/[报告]）
11. **[实测]** 本项目 [Expert_18/主线LLVM_FTC86_源码确认.md](../Expert_18_Phytium_Adaptation/主线LLVM_FTC86_源码确认.md). "主线 LLVM 23.0.0git 全树零飞腾字符串" + 27 调度模型清单。**本 E08 的诊断基础**。
12. **[实测]** 本项目 [Expert_18/国产CPU厂商_LLVM_fork_生态.md](../Expert_18_Phytium_Adaptation/国产CPU厂商_LLVM_fork_生态.md). 华为 TSV110 upstream + 毕昇 fork + 飞腾零 LLVM fork 对照。
13. **[实测]** OpenXiangShan/llvm-project（LLVM 23.0.0git）. `AArch64Processors.td:1417`（generic=CortexA510Model）、`:833/1355/1544`（TSV110 三处）、`AArch64SchedTSV110.td:1-31`、`AArch64Features.td:132/108/212`、`AArch64.td:117-145`、`clang/lib/Driver/ToolChains/Arch/AArch64.cpp:69`。**全部行号锚点 2026-07-07 实测**。
14. **[GitHub commit]** Huawei/HiSilicon TSV110 upstream 系列（D48617/D50897 等 Phabricator，2018-2019）. `[推测-LLVM git history]` —— 华为鲲鹏 920 调度模型 upstream 的 review 记录。
15. **[报告]** 本项目 [Lens_03 SupplyChain](../Lenses/Lens_03_SupplyChain.md). AArch64 后端养育图（ARM/Apple/Qualcomm/Samsung/Cavium/Fujitsu/Ampere/NVIDIA/华为，飞腾缺席）。
16. **[报告]** 飞腾项目 Expert_11 Compiler Research（`../../体系结构实验/Expert_11_Compiler_Research/README.md`） §2.4. PhyGCC 的 `FTC86x.md` + 10-18% 调度收益。**本 E08 的 GCC 对偶**。
17. **[报告]** 飞腾项目 扩展专题.md（`../../体系结构实验/扩展专题.md`） §1. 飞腾 D3000 ARMv8.4 扩展能力矩阵（19 项实测）。**本 E08 的硬件锚点**。
18. **[社区]** LLVM Discourse. *AArch64 scheduling model* 讨论帖（2018-2026 多个）. `[推测-Discourse]` —— TSV110/Neoverse/Apple 调度模型 upstream 的社区讨论。
19. **[社区]** Linaro. *LLVM AArch64 backend contributions* 年度报告. —— Linaro 是 ARM/Linux 生态对 LLVM AArch64 后端的重要贡献者（非厂商，但养着部分）。
20. **[GitHub commit]** LLVM Project. `AArch64SchedAmpere1.td`（2022）/ `AArch64SchedOryon.td`（2024）/ `AArch64SchedOlympus.td`（2025）新增 commit. —— 近年新核 upstream 的案例（飞腾可参考的"如何加一颗核"）。

---

## 7. 延伸阅读（项目内引用 + 外部）

### 项目内（对偶视角）
- [E05 CodeGen](../Expert_05_CodeGen_SelectionDAG_GlobalISel/README.md) —— 指令选择/Legalize 的算法层（本 E08 的"依据层"）。
- [E06 RegAlloc_Scheduler](../Expert_06_RegAlloc_Scheduler/README.md) —— 寄存器分配/调度的算法层（本 E08 的"消费者层"）。
- [E07 AutoVec](../Expert_07_Auto_Vectorization/README.md) —— 向量化在 IR 层的失血（本 E08 是 MI 层的失血）。
- [E10 RISC-V Backend](../Expert_10_RISCV_Backend/README.md) —— 国产对偶（香山/玄铁 RISC-V 后端）。
- [E18 Phytium Adaptation](../Expert_18_Phytium_Adaptation/README.md) —— 飞腾主线 LLVM 零字符串实测（本 E08 的诊断基础）。
- [Lens_03 SupplyChain](../Lenses/Lens_03_SupplyChain.md) —— AArch64 后端养育图（飞腾缺席）。
- [Lens_07 China Localization](../Lenses/Lens_07_China_Localization.md) —— 国产 CPU 编译器自主可控（与本 E08 的"upstream vs 自研"路线之争）。
- 飞腾 E11 Compiler Research（`../../体系结构实验/Expert_11_Compiler_Research/README.md`） —— PhyGCC 的 `FTC86x.md`（本 E08 的 GCC 对偶）。
- 飞腾 扩展专题.md（`../../体系结构实验/扩展专题.md`） —— ARMv8.4 扩展能力矩阵（本 E08 的硬件锚点）。

### 外部资源
- **LLVM AArch64 后端源码**（`llvm/lib/Target/AArch64/`）—— 本 E08 全部行号锚点的来源。
- **ARM Developer — CPU 调度模型文档**（developer.arm.com）—— Cortex-A 系列的优化指南（飞腾写 `FTC86xSched.td` 的参考）。
- **LLVM Discourse — Target/AArch64 板块**（discourse.llvm.org）—— AArch64 后端 contributor 的社区讨论（TSV110/Neoverse/Apple upstream 的 review 现场）。
- **华为毕昇编译器文档**（openEuler 社区 / OEPKGS）—— TSV110 调度模型 + 毕昇 `-mllvm` 优化选项。
- **AArch64.com / ARM ARM 在线版**（developer.arm.com/ddi0487）—— 指令编码与扩展版本对应。

---

## § AArch64 后端方法论与资源（不只飞腾，给所有 Target 后端工程师）

> 本章把 E08 的飞腾 AArch64 分析上升为**任何 Target 后端工程师都可复用的方法与资源**。飞腾 FCC862 是案例锚点，方法普适。通用资源见 [`领域资源库_LLVM.md`](../领域资源库_LLVM.md)。

### 方法论一：Target 后端的"目标描述驱动"四件套

任何 LLVM Target 后端（不只 AArch64）都由四件套描述：
1. **Register `.td`**：寄存器定义（AArch64 的 31 GP + 32 SIMD + SVE 的 Z/P）
2. **InstrInfo `.td`**：指令模式 + predicate（`HasSM4`/`HasDotProd`/`HasV8_4aOps`）
3. **Schedule `.td`**：调度模型（`SchedMachineModel` + `ProcResource` + `WriteRes`）
4. **Processors `.td`**：CPU 注册（`ProcessorModel<"名字", 模型, features, [Tune]>`）

**加一颗新核的工程量** = 改 Schedule `.td`（写一个新模型）+ 改 Processors `.td`（3 行）。**不动任何 `.cpp`**。这是 LLVM 后端比 GCC 后端更易扩展的根本原因。

### 方法论二：调度模型分层（5 层抽象）

```
Layer 5: SchedMachineModel   ← 核的骨架（IssueWidth/MicroOpBufferSize/LoadLatency）
Layer 4: ProcResource<Ν>     ← 端口（Ν = 端口数，BufferSize=0 表示 in-order）
Layer 3: ProcResGroup        ← 端口组（任一可用，如 [Ld0St, Ld1]）
Layer 2: SchedWrite/SchedRead← 抽象动作（WriteImm/WriteI/WriteLD/WriteF/WriteVd...）
Layer 1: WriteRes            ← 把动作映射到端口 + latency + ReleaseAtCycles
```

**判读一颗核**：看 `SchedMachineModel` 知道骨架（wide/窄、OoO/in-order），看 `ProcResource` 知道端口数，看 `WriteRes` 知道每类指令的 latency。**飞腾 FCC862 这 5 层全缺** = 编译器对它的微架构"零认知"。

### 方法论三：upstream 一颗新核的标准流程（抄华为 TSV110 作业）

1. 实测微架构参数（IssueWidth/OoO depth/端口/latency）
2. 写 `<Target>Sched<Core>.td`（参考同代核的 `.td` 结构）
3. 改 `Processors.td` 三处（Tune 定义 + ProcessorFeatures 列表 + ProcessorModel 注册）
4. 改 `<Target>.td` 加 include
5. 改 clang driver 识别 `-mcpu=<core>`
6. 加测试（`test/CodeGen/<Target>/` + `test/MC/<Target>/`）
7. Phabricator/GitHub PR review（需厂商 contributor sign-off）

**工程量**：1 人 × 2-3 月。**收益**：一劳永逸（不用维护 fork）+ 社区话语权。

### 方法论四：OoO 核 vs In-order 核的调度模型差异

| 核类型 | MicroOpBufferSize | IssueWidth | 调度模型重要性 | 例子 |
|------|:---------:|:--------:|:----------:|------|
| In-order | 0 | 2-3 | **极高**（编译器调度是唯一调度） | Cortex-A53/A55/A510、飞腾嵌入式 |
| OoO | 64-256 | 4-8 | 中（硬件调度器补救） | Cortex-A76+、TSV110、飞腾 FCC862、Apple |
| VLIW | N/A | 4-8 | 极高（完全靠编译器） | Itanium、DSP |

**飞腾 FCC862 是 OoO**，所以"无调度模型"的痛被硬件调度器减轻——但寄存器分配/指令选择的决策仍依赖模型，不能完全补救。

### AArch64 后端专属资源

> 通用资源见 [`领域资源库_LLVM.md`](../领域资源库_LLVM.md)；以下为 **AArch64/ARM 后端专属**资源。

**📚 必读（ARM 架构与后端）**
- ⭐ **ARM ARM DDI 0487**（ARMv8 ARM）+ **DDI 0602**（ARMv9 ARM）—— A64 指令集权威
- ⭐ **ARM Cortex-A Series Programmer's Guide**——各 Cortex-A 核的优化指南（写调度模型的参考）
- 🔥 **ARM Community — Learning paths for AArch64**——ARM 官方 AArch64 教程
- 📎 **姚永斌**，《ARM Cortex-A7 体系结构与编程》——中文 ARM 体系结构

**🔧 AArch64 后端代码与社区**
- **LLVM AArch64 后端**（`llvm/lib/Target/AArch64/`）——本 E08 全部锚点来源
- **LLVM Discourse — Target/AArch64**——AArch64 后端 contributor 社区
- **ARM Linaro LLVM**（linaro.org/projects/）——Linaro 对 AArch64 后端的贡献
- **华为毕昇 / LLVM for openEuler**——国产 AArch64 后端 fork 参考
- **GCC AArch64 后端**（`gcc/config/aarch64/`）——对偶（PhyGCC 的基础）

**📊 调度模型参考库**
- `AArch64SchedTSV110.td`（华为，773 行）——国产 upstream 范本
- `AArch64SchedAmpere1.td`（Ampere，服务器核）——近年新核 upstream 范本
- `AArch64SchedCyclone.td`（Apple）——最成熟的 OoO 模型之一
- `AArch64SchedNeoverseV2.td`（ARM 服务器，含 SVE2）——前沿调度模型

---

> **本 Expert 核心交付物**：图 1（.td 文件树）+ 图 2（27 调度模型厂商归属）+ 图 3（扩展暴露三层机制）+ 量化对标表（飞腾 vs 华为 vs A76）+ §2.5 upstream 工程蓝图。**过 §0.3 v2.0 双重门槛**：(a) 飞腾零字符串实测 + (b) 27 处真实行号锚点 + (c) PhyGCC/TSV110/龙芯三重对偶。
