# 国产 CPU 厂商 LLVM/GCC fork 生态对照（开源可查部分）

> 实测日期：2026-07-07
> 数据源：websearch（2026 年公开信息）+ phytium_repos 实测

---

## 0. 一句话结论

国产 CPU 厂商在 LLVM 编译器层的投入呈**三档分化**：龙芯（LoongArch 主线正式后端，最强）、华为（毕昇深度 fork + tsv110 调优，次强）、平头哥（玄铁 C910 fork）构成第一/二梯队；**飞腾处于最末档——零 LLVM fork，纯上游消费者**。

---

## 1. 各厂商 LLVM 生态对照表

| 厂商 | 架构 | LLVM fork | 主线状态 | 编译器产品 | 飞腾对比 |
|------|------|-----------|---------|-----------|---------|
| **龙芯** | LoongArch | 上游主线 | **正式后端（LLVM 16.0.0 起，2023-03）** `[websearch]` | 龙架构工具链 | 飞腾无后端 |
| **华为** | ARM（鲲鹏）/ 昇腾 | **毕昇（BiSheng）深度 fork** `[websearch]` | TSV110 调度模型在主线 | 毕昇编译器、LLVM for openEuler | 飞腾无 fork |
| **平头哥** | RISC-V（玄铁） | ISRC-CAS/c910-llvm `[websearch]` | RISC-V 主线（标准部分） | 剑池工具链 | 飞腾无 fork |
| **海光** | x86 (Zen) | 无（用 AMD 上游） | x86 主线 | GCC | 与飞腾同档（消费者） |
| **申威** | SW-64 | 闭源/社区推进中 | 未入主线（SW_64 在 openEuler 支持列表） | 自研 | 闭源不可查 |
| **飞腾** | ARM (FTC862) | **无** | **零飞腾字符串（实测）** | PhyGCC(GCC)、PhyCC(闭源) | **基准（最浅）** |

---

## 2. 重点厂商详述

### 2.1 龙芯 LoongArch —— 最强 `[websearch]`
- **LLVM 16.0.0（2023-03-18）** 将 LoongArch 从实验性后端提升为**正式后端（official target）**，任何平台默认编译。
- 2026-01 仍有活跃提交（如 pcadd 指令的 PC 相对寻址，commit 6df63dc，作者 heiher）`[websearch]`。
- 龙芯官方：LoongArch 已获 GNU ELF Machine 编号(258)、Linux/GCC/LLVM/Glibc/Binutils 等"BIG FIVE"全面支持。
- **飞腾反差**：飞腾 ARM 架构不需要自己的后端（复用 AArch64），但也因此失去主线话语权和特异性优化。

### 2.2 华为 —— 深度 fork + 上游贡献 `[websearch]`
- **毕昇编译器（BiSheng）**：华为编译器实验室基于 LLVM 的 C/C++/Fortran 工具链，鲲鹏深度调优。
  - 自定义 `-mllvm` 优化选项（如 `-aarch64-ldp-stp-noq` 针对 tsv110 的 stp/ldp 指令优化）
  - 需 `-mcpu=tsv110` 使能
  - OEPKGS 源可 yum 安装
- **LLVM for openEuler**：openEuler 社区发行，含自定义优化选项列表。
- **openEuler 平行宇宙计划**：用 LLVM 替换 GCC 构建整个发行版（2023 发起），RISC-V 侧已面向 SG2042 推出 UEFI 预览版，系统 LLVM 15.0.7 `[websearch]`。
- **主线贡献**：AArch64SchedTSV110.td（鲲鹏 920 调度模型）已在主线（实测确认，见主线确认报告第2节）。
- **昇腾**：CANN 编译器（2025-12 前开源 Ascend 910B/C），NPU 编译器路线。
- **飞腾反差**：华为有完整的"商业 fork（毕昇）+ 上游贡献（TSV110）+ 发行版计划（平行宇宙）"三位一体，飞腾三者皆无。

### 2.3 平头哥玄铁 —— RISC-V fork `[websearch]`
- **ISRC-CAS/c910-llvm**：中科院软件所开源，基于 LLVM 实现玄铁 C910 指令集（RISC-V + 自定义 Cache/同步/算术指令子集）。
- 玄铁标准 RISC-V 部分已随主线 RISC-V 后端。
- 工具链产品：剑池系列。
- **飞腾反差**：平头哥虽小但有针对性 fork，飞腾无。

### 2.4 飞腾 —— 纯消费者（本任务实测基准）`[实测]`
- 公开 45 仓库零 LLVM fork（见 phytium_repos_llvm_patches.md）。
- 主线 LLVM 零飞腾字符串（见主线确认报告）。
- 编译器路线以 GCC 为主（PhyGCC 10.3.2），PhyCC（基于 LLVM）闭源未开源。

---

## 3. 战略解读

### 3.1 为什么飞腾"不需要" LLVM fork？`[推测-依据]`
- 飞腾是 **ARM 架构**（FTC862 = ARMv8.4），可直接复用上游 AArch64 后端。
- 龙芯/平头哥"必须"自研是因为 LoongArch/玄铁自定义指令**上游不认**，被迫 fork。
- 飞腾的"省事"是双刃剑：合规无负担，但放弃了编译器层差异化（无 FTC862 调度模型 → 调度次优）。

### 3.2 飞腾的编译器层差异化去了哪里？`[推测-依据]`
- 从 phytvm 实测看：飞腾的编译器创新在 **NPU/GPU 外部编译器（npu_compiler/gpu_compiler，闭源）**，不在 CPU 编译器（LLVM/GCC）。
- 即飞腾把编译器研发预算投在 AI 加速器侧，CPU 侧吃上游。

---

## 4. 对 Expert_18 写作的输入建议

1. **核心对照表**：第1节表格直接进 E18，作为"飞腾在国产 CPU 编译器生态中的定位"可视化锚点。
2. **战略叙事**：E18 的核心论点之一应是"飞腾是国产 CPU 中编译器投入最浅的"——龙芯/华为/平头哥都有 fork 或主线后端，飞腾纯消费。
3. **三方对照**：详细写华为毕昇（最强对照）、龙芯 LoongArch（自主 ISA 典范）、平头哥玄铁（RISC-V fork）三个 case，衬托飞腾的"缺席"。
4. **盲区诚实段**：申威/海光闭源不可查；飞腾 PhyCC 闭源，本结论基于开源证据，商业版可能另有 fork（需飞腾官方确认）。
5. **对偶链接**：与 Expert_10（RISC-V 后端，讲平头哥/玄铁）、Expert_17（治理，讲开源话语权）联动。
