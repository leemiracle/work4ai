# Expert_11 — GPU/异构后端专家 / 服务器命脉级断层①承载者视角

> **角色定位**：这位专家是 LLVM 的 **GPU/异构后端战略师**——他在 AI 基础设施公司（或 GPU 厂商）的编译器部门干过，亲手往 `llvm/lib/Target/AMDGPU/` 或 `NVPTX/` 提过 patch，评估过"上 ROCm 还是上 CUDA"，纠结过"OpenMP target offload 还是 SYCL 还是 CUDA"。他不关心某一棵 IR 的 SSA 形态（那是 [E02 IR](../Expert_02_LLVM_IR_Design/README.md) 的活），不关心某个通用 Pass（那是 [E03 Pass](../Expert_03_Pass_Framework/README.md) / [E04 中端](../Expert_04_Middle_End_Opt/README.md) 的活），他关心的是**承载今天全球 AI 算力的那几条异构编译通路**：AMDGPU、NVPTX、BPF、SPIR-V，以及它们上面的 OpenMP target offload / SYCL / CUDA / OpenCL。他是本项目 [服务器命脉级断层①"GPU/异构后端对齐债"](../改造蓝图_LLVM.md#5-五个服务器命脉级断层) 的**唯一核心承载者**——因为这个断层的本质，是"AMDGPU/NVPTX/BPF 每个由不同公司单点养着，质量参差，且谁撤退都震荡全球 AI 编译"。这位专家同时回答"飞腾 NPU 的算力路线该怎么走"——他与 [E18 飞腾适配](../Expert_18_Phytium_Adaptation/README.md) 强对偶，因为 [E18 实测结论](../Expert_18_Phytium_Adaptation/phytvm_diff_findings.md) 是"飞腾 NPU/GPU 走外部闭源编译器，**完全绕过 LLVM codegen**"。
>
> **核心思维模型**：
> 1. **公司化单点养育（Corporate Single-Point Foster）**——继承 [Lens_03 供应链](../Lenses/Lens_03_SupplyChain.md) 的核心范式。AMDGPU、NVPTX、Hexagon、SystemZ 是 LLVM 里最硬的四个单点后端：目录里全是同一家的微架构代号、`.mailmap` 里全是同一家的邮箱。一个 GPU 后端再漂亮，sponsor 公司战略一收缩，18 个月内就功能性腐烂。AI 时代的全球算力命脉，吊在 AMD 和 NVIDIA 两家公司的编译器投入上——这是本专家看一切 GPU 后端问题的第一滤镜。
> 2. **"对齐债"思维（Alignment Debt）**——为什么叫"对齐债"？因为 LLVM 的 25 个 Target 后端**没有统一的上游抽象**：AMDGPU 走 SelectionDAG+GlobalISel 混合、NVPTX 几乎纯 SelectionDAG、BPF 用 GlobalISel、SPIR-V 是纯 GlobalISel。每个后端各搞一套合法化、各搞一套调度、各搞一套 intrinsic。新加一个 GPU 指令特性（如 MFMA/warp shuffle/cooperative matrix），要在四个后端里各对齐一遍——这就是"债"，每代硬件累积一次。对齐债不是"今天跑不了"，而是"每代 GPU 升级都要还一遍利息"。
> 3. **"绕过 vs 进入 LLVM"二分**——这是飞腾 NPU 最关键的判断。GPU/NPU 编译有两条路：(a) **进入 LLVM**——把设备做成 LLVM Target 后端（AMDGPU/NVPTX 路线，走 LLVM codegen）；(b) **绕过 LLVM**——把设备做成独立编译器二进制，靠前端 IR（TVM Relay/MLIR）生成设备指令（飞腾 `npu_compiler`/`gpu_compiler`、华为昇腾 CANN 路线）。本专家的飞腾实证锚点是 [E18 实测](../Expert_18_Phytium_Adaptation/phytvm_diff_findings.md)：`codegen.h` 的 `PhytiumConfig` 配置的是**外部编译器二进制路径**（`mapper_bin_path`="npu_compiler"、`gpu_compiler_bin_path`="gpu_compiler"），飞腾 NPU/GPU **根本不进 LLVM**。

---

## 1. 这位 GPU/异构后端专家看 LLVM 的 10 个尖锐问题

这位专家拿到一个 LLVM 版本，第一件事不是 `clang -O3`，而是 `ls llvm/lib/Target/`、`ls llvm/lib/Target/SPIRV/` 和 `ls offload/`，他问：

1. **服务器命脉级断层① GPU 后端对齐债**：AMDGPU / NVPTX / BPF 三个后端每个由谁养着（AMD/NVIDIA/Meta/Google）？哪个在腐烂？为什么 `ls llvm/lib/Target/AMDGPU/` 一眼能看到 250+ 文件（含完整 R600 遗产 + GCN 14 代 gfx600→gfx1310），而 `ls llvm/lib/Target/NVPTX/` 只有 ~75 文件，`ls llvm/lib/Target/SPIRV/` 已悄悄进主线（~90 文件，纯 GlobalISel）？这三个后端成熟度的悬殊，是公司养育强度的直接投影。

2. **SPIR-V 后端的崛起——它会不会统一 AMDGPU/NVPTX？** SPIR-V 已经是 OpenCL/Vulkan/Mesa 的目标 IR。本地实测 `SPIRVSubtarget.h:42` 明确写 `enum SPIRVEnvType { Kernel, Shader, Unknown }`——一个后端**同时瞄准 Kernel（OpenCL/Compute）和 Shader（Vulkan/Graphics）两个世界**。SPIR-V 进主线（2022 LLVM 15 起正式 `llvm/lib/Target/SPIRV/`）是不是"GPU 后端的 SQL"——一个统一中间层吃掉 AMDGPU/NVPTX 的分裂？

3. **OpenMP target offload / SYCL / OpenCL / CUDA 在 LLVM 里的四条路线谁赢？** 本地 `offload/` 目录（含 `libomptarget/` + `plugins-nextgen/amdgpu/` + `plugins-nextgen/cuda/`）证明 OpenMP target offload 已是 LLVM monorepo 一等公民，而 SYCL 的 `libsycl/` 也在 monorepo 里。CUDA 永远是 NVIDIA 闭源 nvcc（基于 EDG 前端，不是 Clang）的主场。这四条路线在 LLVM 里的政治/技术博弈，决定了"未来 AI 训练代码用 `#pragma omp target` 还是 `__global__` 还是 SYCL"。

4. **飞腾 NPU（phytvm）的 target 走 LLVM 直接后端，还是走 MLIR→LLVM？** [E18 实测结论](../Expert_18_Phytium_Adaptation/phytvm_diff_findings.md)：飞腾 NPU/GPU 走**外部二进制编译器**（`npu_compiler`/`gpu_compiler`），**完全绕过 LLVM codegen**。这跟 AMDGPU/NVPTX"进 LLVM"的路线**根本不同**。这对飞腾 AI 算力意味着什么？飞腾的 AI 编译器是"黑箱图编译器"，不享受 LLVM 生态的自动优化、Pass 复用、调试器——但也避开了对齐债。这是一笔什么交易？

5. **AMDGPU 后端：AMD 100% 养着？commit 数据。AMDGPU 与 ROCm/ROCm-Device-Libs 的关系。** 实测 `GCNProcessors.td` 从 gfx600（Southern Islands 2012）一路到 gfx1310（2025+），14 代硬件全覆盖，外加完整 R600 遗产（`R600*.cpp/.td` 一整套）。AMDGPU 是不是 LLVM 里**单一公司投入最大的后端**？AMD 的 ROCm 战略与 AMDGPU 后端的共生关系是什么？

6. **NVPTX 后端：NVIDIA 养着？为什么 NVIDIA 主推 nvcc（基于 EDG）而不是 Clang/LLVM？** 实测 `NVPTX/cl_common_defines.h` 用 `__NV_CL_C_VERSION`（NVIDIA 的 NVVM 版本号），`NVVMReflect.cpp`/`NVVMIntrRange.cpp` 是 NVIDIA NVVM 编译器专用。NVIDIA 为什么一边往 LLVM 贡献 NVPTX，一边自己用 EDG 做 nvcc？这是"养着备胎"还是"防御性开源"？

7. **BPF 后端：eBPF 在 Linux 内核用 LLVM 编译，Meta/Google/Isovalent 谁主导？** 实测 `BPF/BTFDebug.cpp`（BPF Type Format）、`BPFAbstractMemberAccess.cpp`（CO-RE = Compile Once Run Everywhere）、`BPF/AsmParser/`（BPF 现在有汇编器了）。BPF 不是 GPU，但它是"异构"的另一种范式——内核态虚拟机。BPF 在 `.mailmap` 里是 Meta（`fb.com`）+ Google（`google.com`），但 Isovalent（后被思科收购）和 eBPF 基金会才是今天的政治中心。BPF 是 LLVM 里**唯一真正"三家共养 + 基金会托管"的异构后端**。

8. **Hexagon 后端：Qualcomm 单点，撤退风险？** 实测 `Hexagon/HexagonScheduleV5.td ... V81.td`（16 代调度全 Qualcomm），HVX 向量扩展（`HexagonISelLoweringHVX.cpp`）。Qualcomm 的 Hexagon DSP 是手机 modem/AI 加速的命脉，但 DSP 市场在收缩。如果 Qualcomm 像 Imagination 卖掉 MIPS 那样收缩 Hexagon，这个 ~150 文件的后端谁接？

9. **CPU/GPU 统一 IR 的探索：MLIR/StableHLO/IREE/Intel graph-compiler 谁赢？** 本地 `mlir/include/mlir/Dialect/GPU/` 有 IR/Pipelines/TransformOps/Transforms/Utils 完整一套，`mlir/include/mlir/Dialect/SPIRV/` 有 IR/Interfaces/Linking/Transforms。MLIR 的 GPU dialect + SPIRV dialect 是"GPU 之上的统一抽象层"。Google 的 StableHLO/IREE、Intel 的 graph-compiler、PyTorch 2.0 的 PT2/TorchInductor——谁会统一"CPU/GPU/NPU 统一 IR"？这是断层①的终极解药还是另一个对齐债源头？

10. **未来 GPU 后端架构：MLIR GPU dialect + SPIR-V vs 直接 NVPTX/AMDGPU？** 如果 MLIR GPU dialect + SPIRV 成熟，未来的 AI 编译是不是"前端 → MLIR GPU/SPIRV → 后端"？还是说 NVIDIA 永远会让直接 NVPTX + CUDA 保持性能优势，把统一抽象打回"理论上统一、实际上分裂"？这是本专家 2030 年的押注点。

---

## 2. 具体分析：代码级实例 + 飞腾工程实证 + 对偶判断（过 §0.3 特异性测试 v2.0）

> **特异性测试 v2.0 自检**：本节以 `OpenXiangShan/llvm-project`（LLVM 23.0.0git）真实目录列举 + 真实 `.td`/`.cpp` 文件名 + `.mailmap` 为锚，引用 [E18 phytvm diff 实测](../Expert_18_Phytium_Adaptation/phytvm_diff_findings.md) 的飞腾 `codegen.h`/`target_kind.cc`，并给出"如果换 nvcc/MLIR/TVM 会怎样"的对偶判断。删掉飞腾与代码实证后，本文是 LLVM 官方文档翻译——判定失败。故此节三者并重。

### 2.1 GPU/异构后端公司化养育地图（核心交付物 + 对标表）

#### 2.1.1 25 个 Target 后端，谁是异构、谁是 CPU（[实测-目录]）

本地 `OpenXiangShan/llvm-project/llvm/lib/Target/` 实测有 **25 个 Target 后端子目录** `[实测-目录]`：AArch64、AMDGPU、ARC、ARM（32位）、AVR、BPF、CSKY、DirectX、Hexagon、Lanai、LoongArch、M68k、Mips、MSP430、NVPTX、PowerPC、RISCV、Sparc、SPIRV、SystemZ、VE、WebAssembly、X86、XCore、Xtensa。

本专家关心的"异构"后端（非 CPU）只有**6 个**：

| 异构后端 | 设备类型 | 目录文件数级别 | 主 sponsor |
|---------|---------|:---:|---------|
| **AMDGPU** | GPU（AMD） | 超大（250+ 文件，GCN+R600） | AMD 单一 |
| **NVPTX** | GPU（NVIDIA） | 中（~75 文件，NVVM） | NVIDIA 单一 |
| **SPIRV** | 跨厂商虚拟 ISA | 中大（~90 文件，GlobalISel） | Khronos+Google+Intel |
| **BPF** | 内核态虚拟机 | 中（~62 文件，BTF/CO-RE） | Meta+Google+Isovalent/eBPF基金会 |
| **Hexagon** | DSP（Qualcomm） | 超大（~150 文件，HVX） | Qualcomm 单一 |
| **DirectX** | 图形（Microsoft） | 小中 | Microsoft 单一 |

其余 19 个（AArch64/ARM/X86/RISCV/PowerPC/SystemZ/Mips/LoongArch/VE/Sparc/M68k/AVR/MSP430/ARC/CSKY/Lanai/XCore/Xtensa/WebAssembly）都是 CPU 或 CPU-like 后端，由 [E08 AArch64](../Expert_08_AArch64_Backend/README.md)/[E09 x86](../Expert_09_x86_Backend/README.md)/[E10 RISC-V](../Expert_10_RISCV_Backend/README.md) 负责。WebAssembly 介于 CPU 与异构之间（虚拟 ISA），由 [E04 中端](../Expert_04_Middle_End_Opt/README.md) 的 MLIR 章节顺带覆盖。

#### 2.1.2 异构后端养育地图速读（图表①）

```
              LLVM 异构后端公司化养育地图（断层①核心）
   ┌────────────────────────────────────────────────────────────────┐
   │ 🟢 多家共养 + 基金会托管（抗撤退）                                │
   │   BPF    = Meta + Google + Isovalent（思科收购）+ eBPF 基金会     │
   │   SPIRV  = Khronos（规范）+ Google + Intel（主线实现）             │
   ├────────────────────────────────────────────────────────────────┤
   │ 🔴 单公司单点（撤退即震荡全球 AI 编译器供应链）                     │
   │   AMDGPU = AMD 单一（ROCm 战略捆绑，gfx600→gfx1310 全包）          │
   │   NVPTX  = NVIDIA 单一（但 NVIDIA 主推闭源 nvcc，NVPTX 是备胎）     │
   │   Hexagon= Qualcomm 单一（DSP modem 命脉，HVX 向量）               │
   │   DirectX= Microsoft 单一（图形，DXIL/SM6.x）                      │
   ├────────────────────────────────────────────────────────────────┤
   │ ⚠️ 飞腾/国产异构后端：主线零存在                                  │
   │   飞腾 NPU/GPU = 外部 npu_compiler/gpu_compiler（绕过 LLVM）       │
   │   华为昇腾 NPU = CANN 编译器（自建，不入主线）                       │
   │   → 国产 AI 算力在 LLVM 异构后端供应链里彻底缺席（反向锚点）        │
   └────────────────────────────────────────────────────────────────┘
```

#### 2.1.3 异构后端成熟度 + 公司养育对标表（≥1 对标表，宪法 §7.1）

这是本专家的核心交付物——**四维评估**：成熟度（文件规模+代际覆盖）、公司养育、单点风险、对飞腾的可借鉴度。

| 异构后端 | 文件规模 | 硬件代际覆盖 | 主 sponsor | 单点风险 | GlobalISel | 典型用例 | 对飞腾的可借鉴度 |
|---------|:---:|------|---------|:---:|:---:|------|:---:|
| **AMDGPU** | 250+ 文件 | gfx600→gfx1310（14 代）+ R600 遗产 | **AMD 单一** | 🔴🔴🔴 极高 | 部分（混合 SDAG） | ROCm/HIP AI 训练、OpenCL | 🟢 高（GPU 后端范本） |
| **NVPTX** | ~75 文件 | sm_20→sm_100+（但模型稀疏） | **NVIDIA 单一** | 🔴🔴 高（但 NVIDIA 自己用 nvcc） | 否（纯 SelectionDAG） | CUDA（开源路径）、OpenMP target | 🟢 高（GPU 后端范本） |
| **SPIRV** | ~90 文件 | SPIR-V 1.0→1.6 + Kernel/Shader 双环境 | **Khronos+Google+Intel** | 🟡 低（多家） | **是（纯 GlobalISel）** | OpenCL/Vulkan/SYCL/WebGPU | 🟢 极高（统一抽象） |
| **BPF** | ~62 文件 | BPF 指令集（v1→v5，稳定） | **Meta+Google+Isovalent+eBPF 基金会** | 🟢 最低（基金会托管） | 部分（GISel dir） | Linux eBPF、XDP、可观测性 | 🟡 中（异构范式参考） |
| **Hexagon** | ~150 文件 | V5→V81（16 代 DSP）+ HVX | **Qualcomm 单一** | 🔴🔴 高 | 否（VLIW packetizer） | 手机 modem/AI DSP | 🟠 低（VLIW 太特殊） |
| **DirectX** | 小中 | SM6.0→SM6.x（DXIL） | **Microsoft 单一** | 🔴 高 | 否 | DirectX 12 图形/计算 | 🟠 低（图形向） |

**读表结论**：
- **AMDGPU 是 LLVM 异构后端的绝对王者**——250+ 文件、14 代硬件、完整 GlobalISel+SelectionDAG 混合、自带机器调度器（`SIMachineScheduler`）、自带寄存器压力（`GCNRegPressure`）。它是飞腾若做 GPU 后端的**唯一范本**。
- **SPIRV 是唯一"纯 GlobalISel"的异构后端**——这意味着 SPIR-V 从第一天起就跳过了 [E05 CodeGen](../Expert_05_CodeGen_SelectionDAG_GlobalISel/README.md) 的 Legacy SelectionDAG 路径，是 LLVM 后端现代化的样板。
- **BPF 是养育最健康的**——4 个 sponsor + 基金会托管，是 LLVM 里**唯一不怕任何一家撤退**的异构后端。
- **飞腾在异构后端供应链里是"零存在"**——既不像 AMD/NVIDIA 那样养后端，也不像 SPIR-V 那样进 Khronos 规范。E18 实测的 `npu_compiler`/`gpu_compiler` 是飞腾在异构编译里唯一的自研痕迹，但它在 LLVM 之外。

#### 2.1.4 `.mailmap` 反向印证（硬证据，[实测-.mailmap]）

`.mailmap` 67 行 `[实测-.mailmap]` 提取的异构后端养育证据：

| 公司 | `.mailmap` 邮箱 | 对应异构后端 | 印证 |
|------|----------------|------------|------|
| **Qualcomm** | `qti.qualcomm.com`/`quicinc.com`（**12+ 人**：Brian Cain、Eli Friedman、Adarsha Regmi…）| Hexagon（DSP）+ AArch64（Oryon）| Hexagon 单点铁证 |
| **Meta** | `fb.com`（Saleem Abdulrasool 前期 `abdulras@fb.com`）| BPF + llvm core | Meta 养 BPF |
| **Google** | `google.com`（maskray `maskray@google.com`）+ `chromium.org`（hans/thakis）| llvm core + clang + BPF + SPIRV | Google 跨多个异构后端 |
| **NVIDIA** | `nvidia.com`（rnk/Reid Kleckner `rnk@nvidia.com`→`rnk@llvm.org`）| NVPTX + clang | NVIDIA 养 NVPTX（但 rnk 现主要做 clang） |
| **ARM/Apple/SiFive/平头哥/龙芯/IBM/Imagination/NEC** | 各家域名 | CPU 后端（AArch64/RISCV/LoongArch/PowerPC/Mips/VE）| 与异构后端无关 |

**`.mailmap` 的供应链读法**：AMD 和 Khronos 不在 `.mailmap` 里直接出现大量邮箱——AMD 是因为 AMDGPU 的工作主要由 AMD 员工用 `amd.com` 域名提交（结构印证：GCNProcessors.td 全是 AMD gfx 代号），Khronos 是规范组织（SPIR-V 规范在 Khronos，实现在主线靠 Google/Intel/Codeplay 员工）。`.mailmap` 不是养育全集，但 Qualcomm 的 12+ 人 Hexagon 阵营是**单点最硬的铁证**。

### 2.2 AMDGPU 深度解剖：AMD 单点养育的"AI 编译器命脉"

#### 2.2.1 250+ 文件的规模意味着什么（[实测-目录]）

`ls llvm/lib/Target/AMDGPU/` 实测**250+ 源文件** `[实测-目录]`，是 LLVM 25 个后端里**文件数最多**的（超过 X86 和 AArch64）。拆解它的内部结构，能看出 AMDGPU 后端的三个世界：

**世界一：R600 遗产（~30 文件）**。`R600*.cpp/.td/.h` 一整套——`R600AsmPrinter`、`R600ClauseMergePass`、`R600ControlFlowFinalizer`、`R600ExpandSpecialInstrs`、`R600FrameLowering`、`R600ISelLowering`、`R600InstrInfo`、`R600MachineCFGStructurizer`、`R600MachineScheduler`、`R600OptimizeVectorRegisters`、`R600Packetizer`、`R600Processors.td`、`R600Schedule.td`。R600 是 AMD 2010-2013 的 TeraScale 架构（HD 5000/6000 系列），**早已停产**，但代码还在主线。这是 LLVM 后端"删不掉遗产"的活教材——只要还有人用老卡跑 OpenCL，R600 就不能删。

**世界二：GCN/SI 现代后端（~150 文件）**。`SI*.cpp/.h` 一整套——`SIAnnotateControlFlow`、`SIFixSGPRCopies`、`SIFoldOperands`、`SIFormMemoryClauses`、`SIInsertWaitcnts`、`SIInstrInfo`、`SILoadStoreOptimizer`、`SILowerControlFlow`、`SILowerSGPRSpills`、`SIMachineScheduler`、`SIMemoryLegalizer`、`SIOptimizeExecMasking`、`SIPreAllocateWWMRegs`、`SIWholeQuadMode`。GCN（Graphics Core Next）是 AMD 2012 至今的统一 GPU 架构，SI（Southern Islands）是第一代。这套代码是 ROCm/HIP 的编译后端。

**世界三：GlobalISel 现代化（~30 文件）**。`AMDGPUGlobalISel*`、`AMDGPULegalizerInfo`、`AMDGPUInstructionSelector`、`AMDGPURegBank*`、`AMDGPUCombinerHelper`、`AMDGPUCombine.td`。AMDGPU 是 LLVM 里少数**同时维护 SelectionDAG 和 GlobalISel 两条 codegen 路径**的后端——这是 AMDGPU 工程债最重的一块（详见 §2.2.4）。

#### 2.2.2 GCNProcessors.td：14 代 GPU 的调度模型（[实测-读文件]）

`GCNProcessors.td`（352 行 `[实测-读文件]`）是 AMDGPU 的微架构清单。按代际枚举：

```
GFX6  (Southern Islands, 2012): gfx600/601/602, tahiti/pitcairn/verde/hainan/oland
GFX7  (Sea Islands, 2013):       gfx700/701/702/703, kaveri/hawaii/kabini/mullins
GFX8  (Volcanic Islands):        gfx800/801/802/803/810/811/812/813, tonga/fiji/polaris
GFX9  (Vega, 2017):              gfx900/902/904/906/908/909/90c/940/941/942 ← MI300!
GFX10 (RDNA/CDNA, 2019):         gfx1010/1011/1012/1013/1030.../1100.../1150...
GFX11 (RDNA3, 2022):             gfx1100/1101/1102/1103/1150/1151/1152/1153/1170
GFX12 (RDNA4/CDNA, 2024+):       gfx1200/1201/1250/1251
GFX13 (下一代, 2025+):            gfx1310  ← [实测-GCNProcessors.td:350] 已有占位
```

**关键观察**：gfx942 是 AMD MI300X（Instinct MI300X，2023 末发布的 AI 训练旗舰，HBM3 + CXL）`[官方-AMD]`。gfx1310 是 2025+ 的下一代占位。**这意味着 LLVM AMDGPU 后端与 AMD 硬件路线图同步——AMD 每发一代 GPU，先在 GCNProcessors.td 加一行**。这是 AMD 单点养育的最直接证据：除 AMD 自己，没人知道 gfx13 的指令延迟/资源占用。

#### 2.2.3 AMDGPU 与 ROCm 的共生关系

AMDGPU 后端不是孤立存在——它是 **ROCm（Radeon Open Compute）软件栈**的编译后端。完整依赖链：

```
用户代码 (HIP/C++/OpenMP)
  ↓ Clang/LLVM 前端（HIP 是 C++ 扩展）
LLVM IR
  ↓ AMDGPU 后端（llvm/lib/Target/AMDGPU/）
GCN ISA（汇编 .s）
  ↓ lld 链接 + ROCm-Device-Libs（数学库/bitcode）
HSACO（HSA Code Object，可执行）
  ↓ ROCr 运行时（用户态驱动）
MI300X/MI250/MI210 GPU 硬件
```

**ROCm-Device-Libs**（`ROCm-Device-Libs` 仓库）是一组预编译的 LLVM bitcode 设备库（OpenCL C 内建、HIP 数学、OCML/ockl），在链接时与用户 bitcode 合并。这意味着 **AMDGPU 后端 + ROCm-Device-Libs 是一对**——AMD 同时养着这两个仓库。`[社区-AMD ROCm]`

**对偶判断（如果换 nvcc/CUDA 会怎样）**：AMD 的 ROCm/HIP 路线对标 NVIDIA 的 CUDA。区别：CUDA 的 `nvcc` 用 **EDG（Edison Design Group）前端**（不是 Clang），`nvcc` 是闭源；而 ROCm 的 `clang` 用 **Clang/LLVM 前端**，AMDGPU 后端开源。这是 AMD 的开源策略——用 LLVM 开源生态对抗 NVIDIA 闭源 CUDA。**代价**：AMD 把整个 AI 编译命脉的"后端养育"单点扛在自己肩上（详见 §4 盲区）。

#### 2.2.4 AMDGPU 的对齐债：双 codegen 路径（SelectionDAG + GlobalISel）

AMDGPU 同时维护 `AMDGPUISelDAGToDAG`（SelectionDAG 路径）和 `AMDGPUInstructionSelector`（GlobalISel 路径）。看真实文件名 `[实测-目录]`：
- `AMDGPUISelDAGToDAG.cpp/.h` + `AMDGPUISelLowering.cpp/.h`（SelectionDAG）
- `AMDGPUInstructionSelector.cpp/.h` + `AMDGPULegalizerInfo.cpp/.h` + `AMDGPURegBankSelect.cpp`（GlobalISel）
- `AMDGPUPreLegalizerCombiner.cpp` + `AMDGPURegBankCombiner.cpp` + `AMDGPURegBankLegalize*.cpp`（GlobalISel combiner/合法化）

**为什么双轨**：因为 AMDGPU 太大（250+ 文件、14 代硬件），GlobalISel 还没完全覆盖所有指令选择场景，只能"新指令走 GlobalISel、老指令还在 SelectionDAG"。这是 [E05 CodeGen](../Expert_05_CodeGen_SelectionDAG_GlobalISel/README.md) 的 SelectionDAG→GlobalISel 迁移在 AMDGPU 上的具体投影。**债的代价**：每加一个 GCN 指令特性，要在两套 codegen 里各合法化一遍——这就是"对齐债"的微观表现。

### 2.3 NVPTX 深度解剖：NVIDIA 的"开源备胎"

#### 2.3.1 ~75 文件的精简后端（[实测-目录]）

`ls llvm/lib/Target/NVPTX/` 实测 **~75 文件** `[实测-目录]`，比 AMDGPU 小一个量级。原因：NVIDIA PTX（Parallel Thread Execution）是一个**虚拟 ISA**，不像 AMD 的 GCN 是真实硬件 ISA。PTX 的指令集稳定、抽象，NVPTX 后端只需把 LLVM IR 降到 PTX 汇编，**实际的 PTX→SASS（流多处理器原生码）翻译由 NVIDIA 闭源驱动完成**。所以 NVPTX 后端比 AMDGPU 简单——它只管"生成 PTX"，不管"PTX 怎么跑在硬件上"。

关键文件 `[实测-目录]`：
- `NVPTXAsmPrinter.cpp/.h`——直接打印 PTX 文本（不是二进制！PTX 是文本汇编）。
- `NVPTXISelLowering.cpp/.h`——SelectionDAG 指令选择（NVPTX 几乎纯 SelectionDAG，**没有 GlobalISel**，这是它和 AMDGPU/SPIRV 的代差）。
- `NVPTXLowerAlloca.cpp`、`NVPTXLowerArgs.cpp`、`NVPTXLowerUnreachable.cpp`——CUDA 特有的 IR lowering（alloca→shared memory、参数布局）。
- `cl_common_defines.h`——`__NV_CL_C_VERSION`（NVIDIA NVVM 的 OpenCL C 版本号）`[实测-cl_common_defines.h]`。
- `NVVMReflect.cpp`、`NVVMIntrRange.cpp`、`NVVMProperties.cpp/.h`——NVIDIA NVVM 编译器专用 Pass（NVVM = NVIDIA 虚拟机，Clang CUDA 的内部表示）。

#### 2.3.2 为什么 NVIDIA 主推 nvcc（EDG）而不是 Clang

这是 GPU 后端最反直觉的供应链事实：**NVIDIA 一边往 LLVM 贡献 NVPTX 后端，一边自己用 EDG 做 nvcc**。`[官方-NVIDIA nvcc]`

**EDG（Edison Design Group）** 是一家专门做 C++ 前端的公司，NVIDIA 买 EDG 的前端做 `nvcc`。`nvcc` 的工作流：`CUDA C++ → EDG 前端 → NVVM IR（LLVM IR 子集）→ LLVM NVPTX 后端 → PTX`。**注意：nvcc 内部也用 LLVM NVPTX 后端！** 只是前端用 EDG 而不是 Clang。

**为什么不用 Clang**：
1. **历史**：CUDA 2007 诞生时，Clang 还远不成熟（Clang 2007 才起步）。NVIDIA 用 EDG 是当时唯一选择。
2. **稳定性**：EDG 是商业前端，NVIDIA 付费锁定，不受 LLVM 6 月 release 节奏影响。CUDA 编译器需要**极端稳定**——AI 训练代码跑一次几百万美元，编译器 bug 是灾难。
3. **C++ 标准跟随速度**：EDG 总是第一个支持最新 C++ 标准（它本身就是卖标准符合性的）。

**那 NVIDIA 为什么还养 NVPTX 后端**：因为 `nvcc` 内部用 LLVM NVPTX 后端生成 PTX。**NVIDIA 养 NVPTX 不是为了开源社区，是为了自己的 nvcc**——把后端开源 = 免费获得社区的 bug 报告和 patch。这是"防御性开源"：核心前端（EDG）闭源，后端（NVPTX）开源，但整体编译器（nvcc）闭源。`.mailmap` 里 `rnk@nvidia.com`→`rnk@llvm.org`（Reid Kleckner）是 NVIDIA 派驻 LLVM 的人，但他现在主要做 **clang**（C++），不是 NVPTX——这印证了 NVIDIA 对 NVPTX 的投入是"够用就行"，不追求像 AMDGPU 那样的极致。

#### 2.3.3 NVPTX 的对齐债：纯 SelectionDAG 的滞后

NVPTX **没有 GlobalISel** `[实测-目录]`（目录里没有 `NVPTXInstructionSelector`/`NVPTXLegalizerInfo`）。这是 LLVM 异构后端里最滞后的——当 AMDGPU/SPIRV 都已部分或全面上 GlobalISel，NVPTX 还停在 SelectionDAG。原因：NVIDIA 不需要 NVPTX 后端"领先"，只要它"稳定"——CUDA 性能靠 NVIDIA 闭源的 PTX→SASS 驱动优化，不靠 LLVM 后端。**NVPTX 的对齐债是"主动选择的债"**，不是养不起。

### 2.4 BPF 深度解剖：唯一健康的异构后端（基金会托管）

#### 2.4.1 BPF 不是 GPU，但它是异构编译的另一种范式

BPF（Berkeley Packet Filter）→ eBPF（extended BPF）是 Linux 内核里的**虚拟机**。它不是 GPU，但它是"异构"的核心范式——用户态写 C 代码，编译成 BPF 字节码，加载到内核态执行（网络过滤 XDP、可观测性、安全、追踪）。**BPF 字节码由 LLVM BPF 后端生成**（内核态的 JIT 把 BPF 字节码翻译成本地 CPU 指令）。

#### 2.4.2 BPF 后端的三个杀手特性（[实测-目录]）

`ls llvm/lib/Target/BPF/` 实测 **~62 文件** `[实测-目录]`，规模介于 NVPTX 和 SPIRV 之间。三个杀手文件：

**① BTFDebug.cpp/.h（BPF Type Format）**。BTF 是 BPF 的调试信息格式（类似 DWARF，但为内核优化）。内核需要 BTF 来做 CO-RE（见下）。BTF 是 BPF 后端独有的——其他后端用 DWARF，BPF 必须同时生成 BTF。

**② BPFAbstractMemberAccess.cpp（CO-RE = Compile Once - Run Everywhere）**。这是 BPF 最革命性的特性。传统 BPF 程序为特定内核版本编译（因为内核结构体布局每版变）。CO-RE 让 BPF 程序**编译一次，在不同内核版本上重定位**——靠 BTF 记录的字段偏移信息，运行时调整。`BPFAbstractMemberAccess` 就是实现 CO-RE 重写的 Pass。

**③ BPF/AsmParser/（BPF 汇编器）+ GISel/（BPF GlobalISel）**。BPF 现在有完整的汇编器和 GlobalISel 支持——这说明 BPF 是被认真当"一等后端"养的，不是玩具。

#### 2.4.3 BPF 的养育结构：基金会托管（[社区-eBPF 基金会]）

BPF 的养育是 LLVM 异构后端里**最健康**的：
- **Meta（Facebook）**：早期养（`.mailmap` `fb.com` Saleem Abdulrasool）。Meta 用 BPF 做网络/可观测性（Katran 负载均衡器）。
- **Google**：用 BPF 做内核可观测性、安全。`.mailmap` `google.com`/`chromium.org`。
- **Isovalent**（2023 被思科收购）：Cilium/eBPF 商业化公司，养 BPF 工具链。
- **eBPF 基金会**（Linux Foundation 下）：托管 BPF 规范、BTF 规范、libbpf。

**为什么 BPF 健康而 AMDGPU/NVPTX 单点**：BPF 是**开放规范 + 多家利益 + 基金会托管**——任何一家撤退，基金会和另外几家能接。AMDGPU 是**封闭硬件 + 单家公司**——AMD 一撤，没人能写下一代 gfx 调度模型。**这是异构后端养育健康的根本条件：规范开放 + 利益多元 + 基金会兜底**。SPIR-V 正在走这条路（见 §2.5）。

#### 2.4.4 BPF 的对齐债：内核 ABI 锁定

BPF 后端的债不是 codegen 债，而是 **内核 ABI 锁定**——BPF 指令集由 Linux 内核定义，内核只在特定版本加新指令（BPF v1→v5）。LLVM BPF 后端必须**精确匹配内核的 BPF 指令集版本**，否则生成的字节码内核不认。这是"上游规范（内核）+ 下游实现（LLVM）"的同步债。

### 2.5 SPIR-V 后端的崛起：断层①的"统一解药"还是"第三个分裂"？

#### 2.5.1 SPIR-V 进主线的事实（[实测-目录]）

**这是 GPU 后端 2022-2026 最重要的变化**。本地 `ls llvm/lib/Target/SPIRV/` 实测 **~90 文件** `[实测-目录]`，SPIR-V 已经是 LLVM 主线一等 Target 后端（2022 LLVM 15 起正式进 `llvm/lib/Target/SPIRV/`）。这意味着 LLVM 现在**原生能把 IR 编译成 SPIR-V**（以前要靠 Khronos 的 SPIRV-LLVM-Translator 外挂工具做 IR→SPIR-V 翻译）。

关键文件 `[实测-目录]`：
- `SPIRVSubtarget.h:42`——`enum SPIRVEnvType { Kernel, Shader, Unknown }` `[实测-SPIRVSubtarget.h]`。**一个后端同时瞄准 Kernel（OpenCL/Compute）和 Shader（Vulkan/WebGPU/Graphics）两个环境**。这是 SPIR-V 的本质：跨厂商、跨用途的虚拟 ISA。
- `SPIRVInstructionSelector.cpp` + `SPIRVLegalizerInfo.cpp` + `SPIRVRegisterBankInfo.cpp`——**纯 GlobalISel**（没有 `SPIRVISelDAGToDAG`）。SPIR-V 从第一天就是 GlobalISel，是 LLVM 后端现代化样板。
- `SPIRVStructurizer.cpp` + `SPIRVMergeRegionExitTargets.cpp`——结构化控制流（SPIR-V 要求结构化 CFG，不能用任意跳转）。这是 SPIR-V 比 LLVM IR 严格的地方。
- `SPIRVBuiltins.td`——SPIR-V 内建函数表（Khronos 规范定义）。
- `SPIRVSymbolicOperands.td`——SPIR-V 操作码的符号化定义。

#### 2.5.2 SPIR-V 会统一 AMDGPU/NVPTX 吗？四象限判断

**这是断层①的核心战略问题。** 本专家的判断：**短期不会，长期会部分统一，但不会完全取代**。

**支持统一的证据**：
1. **SPIR-V 已是 OpenCL/Vulkan/Mesa/WebGPU 的目标**——Khronos 推 SPIR-V 做"GPU 的 SQL"。`[官方-Khronos SPIR-V]`
2. **AMDGPU 和 NVPTX 都接受 SPIR-V 输入**——AMD 的 ROCm 有 SPIR-V 二进制支持，NVIDIA 的 Vulkan/Compute 也吃 SPIR-V。
3. **MLIR 的 SPIRV dialect + GPU dialect** 默认目标是 SPIR-V（见 §2.8）——MLIR 生态已选边站。
4. **SYCL（Intel oneAPI）默认走 SPIR-V**——Intel 的 SYCL 编译器（`libsycl/` 在 monorepo）生成 SPIR-V，再由 Intel GPU 驱动执行。

**反对统一的证据**：
1. **NVIDIA 永远会让直接 NVPTX + CUDA 保持性能优势**——SPIR-V 是抽象层，多一层就丢一点性能。NVIDIA 的 CUDA 生态靠"直接 PTX"的性能优势粘住用户。
2. **AMD 的 ROCm 性能靠直接 GCN ISA**——SPIR-V → GCN 的翻译会丢优化机会。
3. **"统一抽象"在 GPU 史上从未成功**——OpenCL 想统一，被 CUDA 打败；Vulkan 想统一图形，但 DirectX/Metal 各占一方。GPU 厂商永远有"绕过统一层"的商业动机。

**本专家的判断（可证伪）**：到 2030 年，SPIR-V 会统一**"跨厂商的图形 + 通用计算"层**（OpenCL/Vulkan/WebGPU/SYCL），但**不会统一"极致性能的 AI 训练"层**（CUDA/HIP 仍走直接 NVPTX/AMDGPU）。飞腾若做 AI 算力，**SPIR-V 是"够用但非最优"的统一层，直接后端是"最优但单点"的赌注**。

#### 2.5.3 SPIR-V 的养育：Khronos+Google+Intel（最接近 BPF 的健康度）

SPIR-V 后端的养育结构：
- **Khronos**（规范层）：SPIR-V 规范、SPIRV-Tools、SPIRV-Cross。Khronos 是 GPU 厂商联盟（AMD/NVIDIA/Intel/ARM/Qualcomm/Apple 都是成员），规范中立。
- **Google**：主线 SPIR-V 后端实现（`.mailmap` `google.com`）。Google 用 SPIR-V 做 WebGPU/Chrome。
- **Intel**：SPIR-V + SYCL + oneAPI。Intel GPU 走 SPIR-V。
- **Codeplay**（被 Intel 收购）：SYCL/SPIR-V 商业化。

SPIR-V 的养育是"规范开放（Khronos）+ 多家实现"，接近 BPF 的健康度。**这是断层①最有希望的解药方向**。

### 2.6 OpenMP target offload / SYCL / CUDA / OpenCL 四条路线（图表②）

#### 2.6.1 四条路线在 LLVM 里的实现（[实测-offload/目录]）

本地 `ls offload/` 实测 `[实测-目录]`：`libomptarget/`（OpenMP target 运行时）、`liboffload/`（新一代 offload 库）、`plugins-nextgen/amdgpu/`（AMDGPU 插件）、`plugins-nextgen/cuda/`（CUDA 插件）。**OpenMP target offload 已是 LLVM monorepo 一等公民**。

四条路线的政治/技术博弈：

```
                LLVM 里的四条异构编程路线（图表②）
   ┌──────────────────────────────────────────────────────────────┐
   │ CUDA（NVIDIA 闭源主场）                                        │
   │   源 → EDG 前端(nvcc) → NVVM IR → NVPTX 后端 → PTX → NVIDIA GPU│
   │   主场；LLVM 只能"开源跟跑"（clang --cuda 走 NVPTX）            │
   ├──────────────────────────────────────────────────────────────┤
   │ HIP（AMD 开源对标 CUDA）                                       │
   │   源 → Clang 前端 → LLVM IR → AMDGPU 后端 → GCN ISA → AMD GPU  │
   │   AMD 主推；HIP 语法几乎等同 CUDA（hipify 一键转换）            │
   ├──────────────────────────────────────────────────────────────┤
   │ OpenMP target offload（标准委员会，LLVM 一等公民）              │
   │   #pragma omp target → Clang → offload/runtime → 各设备插件     │
   │   plugins-nextgen/amdgpu + cuda → AMDGPU/NVPTX 后端            │
   │   跨厂商；但"通用但非最优"（CUDA/HIP 更贴近硬件）               │
   ├──────────────────────────────────────────────────────────────┤
   │ SYCL / OpenCL（Intel 主推）                                    │
   │   SYCL C++ → Clang → SPIR-V → 各 GPU 驱动                      │
   │   Intel oneAPI；libsycl 在 monorepo；默认走 SPIR-V              │
   │   跨厂商 + C++ 风格；但生态弱于 CUDA/HIP                        │
   └──────────────────────────────────────────────────────────────┘
```

#### 2.6.2 四条路线谁赢？分场景判断

| 场景 | 赢家 | 理由 |
|------|------|------|
| **NVIDIA AI 训练** | CUDA | 生态垄断（PyTorch/tensorRT 全围绕 CUDA）；NVIDIA 硬件占 80%+ `[第三方报告-Jon Peddie 2024]` |
| **AMD AI 训练** | HIP | ROCm 全栈；HIP≈CUDA 语法降低迁移成本 |
| **跨厂商 HPC（超算）** | OpenMP target | 标准委员会背书；超算（Frontier/Aurora/Lumi）多厂商混合 |
| **Intel GPU / oneAPI** | SYCL | Intel 主推；Aurora 超算用 oneAPI |
| **移动/嵌入式 GPU** | OpenCL/Vulkan | 跨厂商；SPIR-V 目标 |
| **AI 推理（通用）** | 各家私有（TensorRT/CANN/phytvm）| 见 §2.7 飞腾路线 |

**对偶判断**：LLVM monorepo 同时养着 OpenMP target（`offload/`）+ SYCL（`libsycl/`）+ AMDGPU + NVPTX + SPIRV，**没有下注单一路线**。这是 LLVM 作为基础设施的"中立性"——它给所有路线提供后端，让市场决定。但这也意味着 LLVM 的异构投入分散，每条路线都不如厂商私有方案极致（CUDA 比 clang --cuda 强，ROCm 比 OpenMP target 强）。**LLVM 是异构编译的"公共地"，不是"冠军"**。

### 2.7 飞腾 NPU 绕过 LLVM：E18 实测的工程判断（§0.3 飞腾工程实证锚点）

#### 2.7.1 E18 实测结论复述（强对偶锚点）

[E18 phytvm_diff_findings.md](../Expert_18_Phytium_Adaptation/phytvm_diff_findings.md) 的核心实测结论（本专家必须引用，因为这是飞腾 AI 算力路线的工程锚点）：

1. **`phytvm/src/target/llvm/codegen_amdgpu.cc` 是 vanilla Apache TVM**（`[实测-读文件]` 头部 ASF License + `#if TVM_LLVM_VERSION` 守卫）`[实测-E18]`。飞腾的 phytvm 是 Apache TVM v0.11.dev0 的完整 fork，LLVM target 部分**未触碰**。
2. **`phytvm/src/relay/backend/contrib/phytium/codegen.h` 的 `PhytiumConfig` 配置外部编译器** `[实测-E18/codegen.h]`：
   ```cpp
   TVM_ATTR_FIELD(mapper_bin_path)
       .describe("Path to mapper binary npu_compiler");   // NPU 外部编译器
   TVM_ATTR_FIELD(gpu_compiler_bin_path)
       .describe("Path to gpu compiler binary gpu_compiler");  // GPU 外部编译器
   TVM_ATTR_FIELD(phydnn_version).set_default("PHYDNN001008");
   ```
3. **`phytvm/src/target/target_kind.cc:439-458` 注册 7 个 target kind** `[实测-target_kind.cc]`：
   ```cpp
   TVM_REGISTER_TARGET_KIND("phytium", kDLPhytium)
       .set_default_keys({"phytium", "npu", "phydnn_gpu"});
   TVM_REGISTER_TARGET_KIND("npu", kDLPhytiumNPU)
       .set_default_keys({"npu"});              // NPU：默认 key 只有 npu
   TVM_REGISTER_TARGET_KIND("phydnn_gpu", kDLPhytiumGPU)
       .set_default_keys({"phydnn_gpu", "opencl"});  // GPU：走 OpenCL，不走 LLVM GPU 后端
   ```
4. **grep `LLVM|llvm|mcpu|target_triple` 在 `contrib/phytium/*.cc` 零命中** `[实测-E18-grep]`——飞腾 NPU/GPU 的 Relay 子图编译**根本不碰 LLVM**。

#### 2.7.2 飞腾 AI 算力路线的本质判断

把这些证据串起来，飞腾的 AI 算力编译路线是：

```
飞腾 NPU/GPU 编译路线（E18 实测）
   ┌───────────────────────────────────────────────────────┐
   │ 用户模型（ONNX/Relay）                                   │
   │   ↓ TVM Relay（phytvm fork）                             │
   │ Relay 子图划分（飞腾定制：PHYQuantizeAnnotate pass）       │
   │   ↓ 按设备类型分发                                       │
   │ ┌─────────────┬───────────────┬─────────────────────┐ │
   │ │ NPU 子图    │ phydnn_gpu 子图│ host CPU 子图        │ │
   │ │ ↓ npu_compiler│ ↓ gpu_compiler│ ↓ LLVM codegen_arm │ │
   │ │ （闭源二进制）│ （闭源二进制） │ （vanilla TVM）     │ │
   │ │ ↓ NPU 指令   │ ↓ OpenCL/GPU  │ ↓ FTC862 ARM 机器码 │ │
   │ └─────────────┴───────────────┴─────────────────────┘ │
   └───────────────────────────────────────────────────────┘
```

**核心判断**：飞腾 NPU/GPU 走**外部闭源编译器**（`npu_compiler`/`gpu_compiler`），**完全绕过 LLVM codegen**。LLVM 在飞腾 phytvm 里只服务 **host CPU target**（FTC862 上跑 host 代码），用的是 vanilla upstream LLVM（对应 [E08 AArch64](../Expert_08_AArch64_Backend/README.md) 的内容）。

#### 2.7.3 这是笔什么交易？——绕过 LLVM 的代价与收益

| 维度 | 绕过 LLVM（飞腾路线）| 进入 LLVM（AMDGPU/NVPTX 路线）|
|------|-------------------|---------------------------|
| **开发成本** | 高（自建图编译器，从零写指令选择）| 中（复用 LLVM codegen 框架，写 TableGen）|
| **优化上限** | 取决于 npu_compiler 内部能力（黑箱）| 受限于 LLVM 后端框架 |
| **生态复用** | ❌ 不享受 LLVM Pass/调试器/分析工具 | ✅ 复用 LLVM 全套基础设施 |
| **对齐债** | ✅ 无（自管，无上游同步压力）| ❌ 重（每代硬件跟 LLVM 6 月 release）|
| **机密保护** | ✅ 强（npu_compiler 闭源，微架构不外泄）| ❌ 弱（upstream 调度模型=公开微架构情报）|
| **可维护性** | 取决于飞腾团队规模 | 强（社区维护主线）|
| **被制裁韧性** | ✅ 强（不依赖上游 LLVM 决策）| ❌ 弱（被列实体清单可能影响 upstream）|

**飞腾的工程理性**：飞腾 2021-12 被列入美国实体清单 `[报道]`，AI 算力是战略命脉（飞腾 S5000C-E 80 核服务器定位 `[官方-飞腾]`）。在这种地缘约束下，**绕过 LLVM 是工程理性**：
1. **机密**：NPU/GPU 微架构情报（指令延迟/资源占用/调度）是飞腾的核心机密，upstream LLVM 调度模型=公开机密。
2. **制裁韧性**：不依赖上游 LLVM 决策，即使被进一步限制也不影响自研编译器。
3. **对齐债免疫**：飞腾 NPU 架构与 AMD/NVIDIA GPU 不同（NPU 是张量阵列，不是 SIMT），强行套 AMDGPU 后端反而是削足适履。

**代价**：飞腾放弃了 LLVM 生态的红利——没有 LLVM 调试器（lldb 无法调 NPU kernel）、没有 LLVM Pass 复用、没有社区 bug 报告。飞腾 AI 编译器的 bug 只能飞腾自己查。这是"用自给自足换自主可控"的经典国产化权衡，与 [Lens_07 国产化战略家](../Lenses/Lens_07_China_Localization.md) 的判断一致。

#### 2.7.4 对偶：华为昇腾、寒武纪的同类路线

飞腾不是唯一绕过 LLVM 的国产 AI 厂商：

| 厂商 | AI 芯片 | 编译器 | 是否进 LLVM |
|------|--------|-------|:---:|
| **飞腾** | D3000/S5000 NPU + PHYDNN GPU | phytvm（TVM fork）+ npu_compiler/gpu_compiler | ❌ 绕过 |
| **华为昇腾** | Ascend 910/310 NPU | CANN（CANN 编译器，基于 LLVM/TVM/MLIR 私有 fork）| ❌ 自建不入主线 |
| **寒武纪** | MLU（MLU270/290） | NeuWare（Cambricon Compiler）| ❌ 自建 |
| **燧原** | 邃思 GPU | Enflame 工具链 | ❌ 自建 |
| **天数智芯** | 天垓 GPU | Iluvatar 工具链 | ❌ 自建 |
| **摩尔线程** | MTT S 系列 GPU | MUSA 工具链（CUDA 兼容）| ❌ 自建 |
| **百度昆仑** | 昆仑芯 XPU | XTCL | ❌ 自建 |

**结论**：**所有中国 AI 芯片厂商都绕过 LLVM 上游**。这不是巧合，是地缘 + 机密 + 对齐债的综合结果。这与 [Lens_03 供应链](../Lenses/Lens_03_SupplyChain.md) §2.5 的判断（飞腾在 LLVM 供应链是"纯消费者"）完全一致——飞腾在 CPU 后端（AArch64）是消费者，在异构后端是**零存在**。

### 2.8 MLIR GPU dialect + SPIRV：断层①的"架构层解药"（图表③）

#### 2.8.1 MLIR 在 monorepo 里的 GPU/SPIRV 抽象（[实测-目录]）

本地 `ls mlir/include/mlir/Dialect/GPU/` 实测 `[实测-目录]`：`IR/`、`Pipelines/`、`TransformOps/`、`Transforms/`、`Utils/`。`ls mlir/include/mlir/Dialect/SPIRV/` 实测：`IR/`、`Interfaces/`、`Linking/`、`Transforms/`、`Utils/`。

**MLIR 的异构编译架构**：

```
         MLIR GPU/SPIRV 统一抽象层（图表③）
   ┌────────────────────────────────────────────────┐
   │ 前端（Torch-MLIR / TensorFlow / StableHLO）       │
   │   ↓ MLIR 高层 dialect（linalg/tensor/math）       │
   │ GPU dialect（launch/grid/block/thread 抽象）       │
   │   ↓ mlir-translate                               │
   │ ┌──────────┬───────────┬──────────────────────┐ │
   │ │ SPIRV    │ NVVM      │ ROCM (ROCDL)          │ │
   │ │ dialect  │ dialect   │ dialect               │ │
   │ │ ↓ SPIR-V │ ↓ LLVM IR │ ↓ LLVM IR             │ │
   │ │ 二进制    │ → NVPTX   │ → AMDGPU              │ │
   │ │          │   后端     │   后端                 │ │
   │ └──────────┴───────────┴──────────────────────┘ │
   │ 目标：Vulkan/WebGPU/OpenCL │ CUDA │ ROCm/HIP      │
   └────────────────────────────────────────────────┘
```

**关键**：MLIR 的 GPU dialect 是"硬件无关的 GPU 启动抽象"（grid/block/thread/warp），SPIRV dialect 是"SPIR-V 的 MLIR 表示"。MLIR 给出**三条降级路径**：
1. **GPU → SPIRV → SPIR-V 二进制**（跨厂商，Vulkan/WebGPU/OpenCL）
2. **GPU → NVVM → LLVM IR → NVPTX 后端**（NVIDIA）
3. **GPU → ROCDL → LLVM IR → AMDGPU 后端**（AMD）

#### 2.8.2 MLIR 统一抽象 vs 直接后端：2030 押注

**这是断层①的架构层博弈**。本专家的押注（可证伪，2028 回看）：

**押注 A（MLIR 统一占主导）**：到 2028 年，**跨厂商 AI 推理**（Vulkan Compute/WebGPU/OpenCL）会主要走 MLIR GPU→SPIRV 路径，SPIR-V 成为"够用层"。理由：Google IREE、Intel graph-compiler、StableHLO 都押注 MLIR+SPIRV。

**押注 B（直接后端守住极致性能）**：到 2030 年，**极致性能的 AI 训练**仍走直接 NVPTX/AMDGPU（CUDA/HIP），NVIDIA 永远会让直接路径比抽象层快。理由：NVIDIA 的商业利益 + CUDA 生态粘性。

**押注 C（飞腾/国产走 MLIR 私有方言）**：飞腾的 `npu_compiler` 未来可能**内部基于 MLIR**（MLIR 适合做 NPU 编译器，比 LLVM IR 更高层），但不会 upstream。这与华为昇腾（CANN 内部据说用 MLIR）一致。**MLIR 会成为国产 AI 编译器的"私有地基"，但不是主线贡献**。

#### 2.8.3 MLIR GPU/SPIRV 的养育：Google 主导（断层②的投影）

MLIR 的 GPU/SPIRV dialect 主要由 **Google**（IREE、StableHLO）和 **Intel**（graph-compiler、SYCL）养。这与 [断层② MLIR-core 融合裂痕](../改造蓝图_LLVM.md#5-五个服务器命脉级断层) 直接相关——MLIR 是 Google 主导的 AI 编译未来，但它在 LLVM monorepo 里与 LLVM core 是"二元"关系（MLIR 依赖 LLVM，但有自己的 dialect 生态）。**MLIR GPU/SPIRV 的命运，取决于 MLIR 与 LLVM core 的融合进度**——这是 E04 中端 + MLIR 章节的核心议题。

### 2.9 Hexagon/VE/单点后端的撤退风险（断层①的边缘投影）

#### 2.9.1 Hexagon：Qualcomm 单点的 ~150 文件重资产（[实测-目录]）

`ls llvm/lib/Target/Hexagon/` 实测 **~150 文件** `[实测-目录]`，是 LLVM CPU/GPU 后端里文件数第三大（仅次于 AMDGPU 和 X86）。结构：
- `HexagonScheduleV5.td ... V81.td`（**16 代调度全 Qualcomm**，从 V5 到 V81）`[实测-目录]`——与 AMDGPU 的 gfx 代际清单同构，都是单公司硬件路线图的投影。
- `HexagonISelLoweringHVX.cpp` + `HexagonPatternsHVX.td`（HVX = Hexagon Vector eXtensions）——Hexagon 的向量扩展。
- `HexagonVLIWPacketizer.cpp`（VLIW 打包）——Hexagon 是 VLIW 架构，指令调度=打包多条指令到一个 packet，这是 Hexagon 最特殊的 codegen 挑战。

**撤退风险分析**：Qualcomm 的 Hexagon DSP 主要用于手机 modem（5G 基带）和边缘 AI（Hexagon NPU/HTP）。如果 Qualcomm 像 NVIDIA 退出手机 modem 芯片业务（2016 把 Icera 关了）那样收缩 Hexagon DSP，这 150 文件的后端谁接？**几乎无人**——VLIW packetizer 极其特殊，只有 Qualcomm 内部工程师懂。这是 [Lens_03 供应链](../Lenses/Lens_03_SupplyChain.md) §2.2 的"硬单点"判断：Hexagon 撤退腐烂周期 18-24 个月。

#### 2.9.2 VE：NEC 单点的向量机后端

`ls llvm/lib/Target/VE/` 实测 ~58 文件 `[实测-目录]`。VE 是 NEC SX-Aurora TSUBASA（向量超算）的后端。NEC 单点。VE 市场极小（日本超算富岳的辅助系统），但 NEC 长期养着。撤退风险高（NEC 超算业务规模小），但影响面窄（只有日本 HPC 用）。

#### 2.9.3 单点后端的共性教训（对飞腾的警示）

Hexagon/VE/SystemZ/AMDGPU/NVPTX/LoongArch 都是单点后端。**单点后端的共性教训**：
1. **目录规模 = sponsor 投入**——AMDGPU 250 文件 = AMD 重投，VE 58 文件 = NEC 轻投。文件数是养育强度的代理。
2. **代际覆盖 = 活跃度**——Hexagon V5→V81（活跃）vs Mips P5600 一代（冻结）。`*Schedule*.td` 的代数 = 后端是否还活着。
3. **撤退信号 = 长时间无新代 + 无新 sponsor**——参考 MIPS（Imagination 撤退后冻结）。

**对飞腾的警示**：飞腾若某天为 FTC86x 或下一代 NPU upstream 一个调度模型，必须承诺**长期维护**（跟 LLVM 6 月 release），否则就是制造下一个"孤儿后端"。飞腾目前的工程理性是**不 upstream**（保护机密 + 避免维护负担），这与 [Lens_03](../Lenses/Lens_03_SupplyChain.md) §2.5.4 的预测（飞腾 2028 前不上游，概率 80%）一致。

---

## 3. 设计决策评估：LLVM 哪些决策认可 / 哪些该改 / 飞腾工程教训

### 3.1 认可的决策

**① SPIR-V 进主线是 2022-2026 最正确的决策。** 把 SPIR-V 做成 LLVM 一等 Target 后端（而不是外挂 SPIRV-LLVM-Translator），让 LLVM 原生支持跨厂商 GPU 编译。这是断层①唯一的"架构层解药"。SPIRV 用纯 GlobalISel 也树立了后端现代化样板。

**② OpenMP target offload 进 monorepo 是中立性的体现。** LLVM 同时养 OpenMP target + SYCL + AMDGPU + NVPTX + SPIRV，不下注单一路线，让市场决定。这是基础设施的正确姿态。

**③ BPF 的 CO-RE（BPFAbstractMemberAccess）是工程杰作。** "编译一次，跨内核版本运行"是异构编译里最优雅的设计之一。飞腾若做跨 NPU 版本兼容，CO-RE 的思路（运行时重定位）值得借鉴。

### 3.2 该改的决策

**① AMDGPU 双 codegen 路径（SelectionDAG + GlobalISel）该收口。** 250 文件里同时维护两套指令选择是巨大工程债。AMD 应明确 timeline，把 SelectionDAG 路径废弃。但这受制于 [E05 CodeGen](../Expert_05_CodeGen_SelectionDAG_GlobalISel/README.md) 的 GlobalISel 覆盖率，短期内难实现。

**② NVPTX 没上 GlobalISel 是滞后。** NVPTX 是唯一没有 GlobalISel 的异构后端。虽然 NVIDIA 不需要 NVPTX"领先"，但长期看 SelectionDAG 是技术债。

**③ 异构后端之间没有统一的上游抽象。** AMDGPU/NVPTX/SPIRV/BPF 各搞一套合法化、各搞一套 intrinsic、各搞一套调度。MLIR GPU/SPIRV dialect 是尝试统一，但还在 LLVM core 之外。**断层①的"对齐债"本质就是缺乏统一抽象**。

### 3.3 飞腾工程教训

**教训一：飞腾的"绕过 LLVM"是正确的工程理性，但不是技术最优。** 在地缘 + 机密 + 对齐债的三重约束下，绕过 LLVM 是飞腾的唯一选择。但代价是放弃 LLVM 生态红利（调试器、Pass、社区）。飞腾 AI 编译器团队必须自给自足。

**教训二：飞腾若未来 upstream NPU 后端，必须走"MLIR 私有 dialect"而非"LLVM 直接后端"。** NPU 架构（张量阵列）与 GPU（SIMT）不同，强行套 AMDGPU 后端是削足适履。MLIR 的 dialect 机制（linalg/tensor + 自定义 NPU dialect）更适合 NPU 编译。但飞腾不会 upstream（机密 + 制裁）。

**教训三：飞腾 NPU 的"图编译器"路线与 AMDGPU 的"LLVM 后端"路线是两种范式。** 飞腾 `npu_compiler` 是图编译器（mapper），不是传统 LLVM 后端。这决定了飞腾 AI 编译器的优化空间在"图级"（算子融合、内存规划），不在"指令级"（LLVM 后端强项）。这是飞腾与 AMD/NVIDIA GPU 编译的根本差异。

---

## 4. 这一视角的盲区与反方（诚实段，强制）

> **敢说看不见什么，才不是软文。**

1. **commit 数据本地跑不出，用"结构印证"代理。** 本地是 OpenXiangShan 的 squashed mirror（单 commit `[实测-reflog]`），`git log --pretty=format:"%an" llvm/lib/Target/AMDGPU/` 跑不出按公司 commit 历史。本专家用"目录规模 + `.td` 代际命名 + `.mailmap` 邮箱 + 社区共识"三方交叉代理 commit 份额。这有偏差——一个高质量 maintainer 抵十个外围贡献者，commit 数 ≠ 养育质量。

2. **闭源编译器（npu_compiler/gpu_compiler/nvcc）内部无法实测。** 本专家判断飞腾 NPU"绕过 LLVM"基于 `codegen.h` 的外部二进制路径配置 + `contrib/phytium/*.cc` 零 LLVM 命中。但 `npu_compiler`/`gpu_compiler` 二进制是闭源的，**其内部是否基于 LLVM fork 未知**。推测：npu_compiler 可能是图编译器（mapper），非传统 LLVM 后端；但也可能内部链了 LLVM。无法实测确认——这是诚实承认的盲区。

3. **GPU 后端性能数据无法本地实测。** 本专家判断"直接后端比 SPIR-V 抽象层快"是社区共识 + 商业逻辑推断，不是本地 benchmark 实测。真实性能差距可能因场景而异（计算密集 vs 内存密集）。

4. **MLIR 统一抽象的进度判断基于目录结构，非功能完整度。** 本专家判断"MLIR GPU/SPIRV 是断层①解药"基于 `mlir/include/mlir/Dialect/GPU/` 和 `SPIRV/` 的目录存在。但目录存在 ≠ 功能成熟。MLIR GPU dialect 的实际覆盖率、与直接后端的性能差距，需要实测，本专家未做。

5. **政治/制裁变量外生化。** 本专家假设 AMD/NVIDIA/Qualcomm 基于"商业理性"养后端。但美国制裁可能强制切断中国厂商（如华为）的 LLVM 贡献，或限制 AMD/NVIDIA 对中国的 GPU 出口（已发生：2022-2023 美国限制 A100/H100/AI 芯片出口中国 `[报道]`）。把地缘当外生常数是分析便利，不是事实——这与 [Lens_03](../Lenses/Lens_03_SupplyChain.md) §4 盲区段完全同构。

6. **"对齐债"的量化缺失。** 本专家提出"对齐债"概念，但没有量化"每代 GPU 升级要还多少债"（具体人月）。这是定性判断，量化需要 GPU 厂商内部数据。

**反方一句话**：GPU 后端的命运，可能不是由 codegen 质量决定，而是由**硬件出货量 + 生态粘性**决定。CUDA 不是因为 NVPTX 后端好而赢，是因为 NVIDIA GPU 卖得多 + PyTorch/tensorRT 生态锁死。本专家看 codegen 对齐债，但市场看的是"这块卡能不能跑我的模型"——两者经常错位。

---

## 5. 与其他视角对偶（一致 / 冲突，强制）

| 对偶视角 | 一致点 | 冲突点 / 互补 |
|---------|------|-------------|
| **[Lens_03 供应链](../Lenses/Lens_03_SupplyChain.md)** | 都识别"公司化单点养育" | **Lens_03 是底图（谁养谁），E11 是 zoom-in（GPU 后端技术细节）**。Lens_03 §2.1 给出全 25 后端养育地图，E11 §2.1 深挖 6 个异构后端。E11 的"AMDGPU=AMD 单点"是 Lens_03 判断的具体展开。**E11 是 Lens_03 异构后端章节的技术补充**。 |
| **[E18 飞腾适配](../Expert_18_Phytium_Adaptation/README.md)** | 都讲飞腾绕过 LLVM | **强对偶**：E18 §0.2 是战略级发现（codegen_arm.cc 是 vanilla TVM），E11 §2.7 是异构编译视角的复述 + 深化。E11 给出"绕过 vs 进入 LLVM"的交易矩阵（§2.7.3），E18 给出 phytvm 完整 diff。**两者互为表里**。 |
| **[E05 CodeGen SelectionDAG/GlobalISel](../Expert_05_CodeGen_SelectionDAG_GlobalISel/README.md)** | 都讲 SelectionDAG→GlobalISel 迁移 | **分工**：E05 讲通用迁移机制，E11 讲各异构后端的具体投影（AMDGPU 双轨、NVPTX 纯 SDAG、SPIRV 纯 GISel）。**E11 §2.2.4/§2.3.3 是 E05 在 GPU 后端的案例**。 |
| **[E04 中端 + MLIR 章节](../Expert_04_Middle_End_Opt/README.md)** | 都讲 MLIR 是异构编译未来 | **断层①+断层②交叉**：E11 §2.8 讲 MLIR GPU/SPIRV dialect（断层①解药），E04 MLIR 章节讲 MLIR-core 融合裂痕（断层②）。**E11 的 MLIR 是"异构出口"，E04 的 MLIR 是"与 core 的关系"**。两者共同回答"MLIR 是否会颠覆 LLVM core"。 |
| **[Lens_01 历史学家](../Lenses/Lens_01_Historian.md)** | 都看技术兴衰周期 | **时间维度 vs 空间维度**：Lens_01 预测"MLIR 是否颠覆 LLVM core"，E11 提供"MLIR GPU/SPIRV 是否颠覆直接 NVPTX/AMDGPU"的 GPU 后端视角。**E11 是 Lens_01 在异构领域的 zoom-in**。 |
| **[Lens_07 国产化战略家](../Lenses/Lens_07_China_Localization.md)** | 都讲国产 AI 芯片绕过 LLVM | **对策 vs 现状**：Lens_07 讲"飞腾/华为怎么摆脱依赖"（对策），E11 §2.7.4 讲"所有中国 AI 厂商都绕过 LLVM"（现状底图）。**E11 是 Lens_07 的异构后端证据源**。 |
| **[断层② MLIR-core 融合裂痕](../改造蓝图_LLVM.md#5-五个服务器命脉级断层)** | 都讲 MLIR 与 LLVM 的二元关系 | **交叉**：断层①（GPU 对齐债）的解药是 MLIR GPU/SPIRV，但 MLIR 本身有断层②（与 core 融合裂痕）。**两个断层互为前提**——断层②不解决，断层①的 MLIR 解药也不稳。 |
| **飞腾项目 E21 AI 算力定位](../../体系结构实验/Expert_21_AI_Compute_Positioning/README.md)** | 都讲飞腾 AI 算力伤疤 | **芯片层 vs 编译器层**：飞腾 E21 讲"D3000M 无 BF16/I8MM/SVE 是芯片层伤疤"，LLVM E11 讲"飞腾 NPU 绕过 LLVM 是编译器层选择"。**两者叠加 = 飞腾 AI 算力的"双重脆弱"**：芯片没原生 AI 指令 + 编译器不入主流生态。 |

---

## 6. 参考文献（≥15，分级标注）

1. **[实测-目录]** 本项目实测 `OpenXiangShan/llvm-project/llvm/lib/Target/` 25 个后端子目录及各异构后端文件清单（AMDGPU 250+、NVPTX ~75、SPIRV ~90、BPF ~62、Hexagon ~150）。访问 2026-07-07。
2. **[实测-读文件]** 本项目实测 `llvm/lib/Target/AMDGPU/GCNProcessors.td`（352 行，gfx600→gfx1310 14 代 + R600 遗产）。访问 2026-07-07。
3. **[实测-读文件]** 本项目实测 `llvm/lib/Target/SPIRV/SPIRVSubtarget.h:42`（`enum SPIRVEnvType { Kernel, Shader, Unknown }`）。访问 2026-07-07。
4. **[实测-读文件]** 本项目实测 `llvm/lib/Target/NVPTX/cl_common_defines.h`（`__NV_CL_C_VERSION` NVIDIA NVVM 版本号）。访问 2026-07-07。
5. **[实测-.mailmap]** 本项目实测 `OpenXiangShan/llvm-project/.mailmap`（67 行，Qualcomm 12+ 人、Meta fb.com、Google google.com、NVIDIA nvidia.com→llvm.org）。访问 2026-07-07。
6. **[实测-E18]** [E18 phytvm_diff_findings.md](../Expert_18_Phytium_Adaptation/phytvm_diff_findings.md) ——飞腾 phytvm vs upstream Apache TVM 完整 diff，确认 NPU/GPU 走 npu_compiler/gpu_compiler 外部二进制，绕过 LLVM。访问 2026-07-07。
7. **[实测-E18/codegen.h]** 本项目实测 `phytvm/src/relay/backend/contrib/phytium/codegen.h`（`PhytiumConfig`：`mapper_bin_path`="npu_compiler"、`gpu_compiler_bin_path`="gpu_compiler"）。访问 2026-07-07。
8. **[实测-target_kind.cc]** 本项目实测 `phytvm/src/target/target_kind.cc:439-458`（7 个 phytium target kind 注册）。访问 2026-07-07。
9. **[实测-offload]** 本项目实测 `offload/` 目录（libomptarget/ + liboffload/ + plugins-nextgen/amdgpu/ + plugins-nextgen/cuda/）+ `PluginManager.cpp:243`（sm_80/sm_89 CUDA 兼容）+ `plugins-nextgen/amdgpu/rtl.cpp:3241`（gfx942 MI300）。访问 2026-07-07。
10. **[官方-Khronos]** Khronos Group, *SPIR-V Specification*（[khronos.org/registry/spir-v](https://www.khronos.org/registry/spir-v/)）——SPIR-V 规范，Kernel + Shader 双环境，本专家 §2.5 依据。
11. **[官方-AMD ROCm]** AMD, *ROCm Documentation*（[rocmdocs.amd.com](https://rocdocs.amd.com/)）——AMDGPU 后端 + ROCm-Device-Libs 共生关系，§2.2.3 依据。
12. **[官方-NVIDIA nvcc]** NVIDIA, *CUDA Compiler Driver NVCC*（[docs.nvidia.com/cuda](https://docs.nvidia.com/cuda/cuda-compiler-driver-nvcc/)）——nvcc 基于 EDG 前端，§2.3.2 依据。
13. **[社区-eBPF 基金会]** eBPF Foundation（Linux Foundation）（[ebpf.foundation](https://ebpf.foundation/)）——BPF 规范 + BTF + libbpf 基金会托管，§2.4.3 依据。
14. **[论文-CO-RE]** Andrii Nakryiko, *BPF CO-RE (Compile Once – Run Everywhere)*, LWN.net 2020 —— BPF CO-RE 设计，§2.4.2 `BPFAbstractMemberAccess` 依据。
15. **[论文-AMDGPU]** Stanislav M. Ivanov 等, *AMD GPU Code Generation in LLVM* 相关讨论，LLVM Dev Meeting 2017-2023 —— AMDGPU 后端演进，§2.2 依据。
16. **[论文-OpenMP target]** Alexey Bataev 等（IBM/LLVM），*OpenMP Target Offloading in Clang and LLVM*，OpenMP Architecture Review Board —— OpenMP target offload 实现，§2.6 依据。
17. **[Discourse-LLVM]** LLVM Discourse（[discourse.llvm.org](https://discourse.llvm.org/)）——SPIR-V 进主线讨论、AMDGPU GlobalISel 迁移、OpenMP target 治理，各 § 印证。
18. **[GitHub]** SPIRV-LLVM-Translator（[github.com/KhronosGroup/SPIRV-LLVM-Translator](https://github.com/KhronosGroup/SPIRV-LLVM-Translator)）——SPIR-V 进主线前的外挂翻译工具，§2.5.1 历史依据。
19. **[GitHub]** MLIR GPU/SPIRV dialect（`mlir/include/mlir/Dialect/GPU/` + `SPIRV/`）——MLIR 异构抽象层，§2.8 依据。
20. **[第三方报告]** Jon Peddie Research, *GPU Market Share Report 2024* —— NVIDIA GPU 市占 80%+，§2.6.2 判断依据。
21. **[报道]** 美国对华 AI 芯片出口管制（A100/H100/H800/A800 限制），2022-2023 Reuters/路透社报道 —— §4 盲区 + §2.7.3 制裁韧性依据。
22. **[社区-LLVM 资源库]** 本项目 [`领域资源库_LLVM.md`](../领域资源库_LLVM.md) §7.8（AI-LLM 前沿）+ §11（飞腾 PhyCC/PhyGCC 实证）——本专家飞腾判断的交叉印证源。

---

## 7. 延伸阅读（项目内引用 + 外部）

### 项目内
- [Lens_03 供应链](../Lenses/Lens_03_SupplyChain.md) §2.1（25 后端公司化养育地图全图）、§2.2（单点失败排序）、§2.5（飞腾在 LLVM 供应链的位置）
- [E18 飞腾适配](../Expert_18_Phytium_Adaptation/README.md)（phytvm diff 完整证据，本专家 §2.7 的源）
- [E05 CodeGen](../Expert_05_CodeGen_SelectionDAG_GlobalISel/README.md)（SelectionDAG→GlobalISel 迁移机制，本专家 §2.2.4/§2.3.3 的通用层）
- [E04 中端 + MLIR 章节](../Expert_04_Middle_End_Opt/README.md)（MLIR 与 LLVM core 融合，断层②，本专家 §2.8 的背景）
- [E08 AArch64](../Expert_08_AArch64_Backend/README.md)（飞腾 host CPU 后端，phytvm LLVM codegen 服务对象）
- [改造蓝图_LLVM.md](../改造蓝图_LLVM.md) §5（断层①定义）、§3.2（E11 定位）
- 飞腾项目 E21 AI 算力定位（`../../体系结构实验/Expert_21_AI_Compute_Positioning/README.md`）（飞腾芯片层 AI 算力伤疤，与编译器层叠加）

### 外部
- Khronos SPIR-V Registry（规范）
- AMD ROCm Documentation（AMDGPU 后端 + ROCm-Device-Libs）
- NVIDIA CUDA Compiler Driver NVCC（EDG 前端）
- eBPF Foundation（BPF/BTF/CO-RE）
- LLVM GPU/SPIR-V Dev Meeting talks（2022-2025）
- Google IREE、Intel graph-compiler、StableHLO（MLIR 异构编译前沿）

---

## § 领域方法论与资源（异构/GPU 编译器通用，不只 LLVM）

> 本章把 E11 的 GPU/异构后端分析上升为**任何异构编译器（GPU/NPU/DSP/FPGA）都适用的方法论**。LLVM 是案例锚点，方法普适。通用资源见 [`领域资源库_LLVM.md`](../领域资源库_LLVM.md) §7.8。

### 方法论一：异构后端"进入 vs 绕过 LLVM"决策矩阵

任何做 AI 芯片/NPU/GPU 的厂商，都要回答"编译器进 LLVM 还是绕过"。决策矩阵：

| 因素 | 进 LLVM（AMDGPU/NVPTX 路线） | 绕过 LLVM（飞腾/昇腾路线） |
|------|--------------------------|-------------------------|
| 芯片架构 | 标准 GPU（SIMT/向量） | 特殊架构（张量阵列/数据流） |
| 地缘约束 | 无（非制裁实体） | 有（被制裁/机密敏感） |
| 团队规模 | 大（能跟 LLVM 6 月 release） | 小（自管节奏） |
| 生态需求 | 高（需社区 Pass/调试器） | 低（自给自足） |
| 商业模式 | 卖 IP/生态（需可见度） | 卖整芯片（不需可见度） |

**结论**：标准 GPU + 非制裁 + 大团队 → 进 LLVM（AMD/NVIDIA）。特殊架构 + 制裁 + 机密 → 绕过（飞腾/昇腾）。**没有绝对优劣，只有匹配**。

### 方法论二：GPU 后端成熟度评估五维

评估任何 GPU 后端（AMDGPU/NVPTX/SPIRV/私有）的成熟度：
1. **代际覆盖**：`*Schedule*.td` 或 processor list 覆盖几代硬件？活的后端每代都有。
2. **codegen 路径**：SelectionDAG（老）/ GlobalISel（新）/ 混合（债重）？
3. **文件规模**：>100 文件=重投，<60 文件=轻投/玩具。
4. **sponsor 数**：单点 vs 多家共养 vs 基金会托管。
5. **生态绑定**：是否与运行时（ROCm/CUDA/CANN）紧耦合。

### 方法论三：异构编译"统一抽象"的可行性判断

判断任何"统一 GPU IR"（SPIR-V/MLIR GPU/StableHLO）能否成功：
1. **规范是否开放**（Khronos/基金会 vs 单公司）——开放=可能统一，封闭=不可能。
2. **性能损耗是否可接受**——抽象层多一层丢性能，极致性能场景会绕过。
3. **厂商商业动机**——GPU 厂商永远有"绕过统一层"的动机（粘性），统一层只能赢"够用层"。
4. **历史先例**——GPU 史上"统一抽象"（OpenCL）从未完全成功，CUDA 始终占主导。

**通用判断**：跨厂商"够用层"（图形/通用计算）会被统一（SPIR-V）；极致性能"训练层"（CUDA/HIP）不会被统一。

### 方法论四：国产 AI 芯片编译器的"绕过 LLVM"共性

所有中国 AI 芯片厂商（飞腾/华为/寒武纪/燧原/天数/摩尔线程/百度昆仑）都绕过 LLVM 上游。共性原因：
1. **地缘**：被制裁实体清单，不依赖上游决策。
2. **机密**：微架构情报不外泄。
3. **对齐债**：不跟 LLVM 6 月 release。
4. **架构特殊**：NPU/DSA 非标准 GPU，套 LLVM 后端是削足适履。

**代价**：放弃 LLVM 生态红利（调试器/Pass/社区 bug 报告），自给自足。这是"自主可控"的工程成本。

### 异构/GPU 编译器资源（通用）

- **规范**：Khronos SPIR-V/OpenCL/Vulkan、eBPF/BTF、PTX ISA（NVIDIA）、GCN ISA（AMD）
- **后端**：llvm/lib/Target/AMDGPU/NVPTX/SPIRV/BPF/Hexagon（代码级范本）
- **运行时**：ROCm/ROCm-Device-Libs、CUDA、libomptarget、libsycl、libbpf
- **MLIR 异构**：MLIR GPU/SPIRV dialect、Google IREE、Intel graph-compiler、StableHLO
- **国产案例**：飞腾 phytvm（TVM fork）、华为昇腾 CANN、寒武纪 NeuWare
- **社区**：LLVM GPU/SPIR-V Dev Meeting、Khronos DevU、eBPF Summit

### 给异构编译器工程师的通用建议

1. **先选路线（进 LLVM vs 绕过）**：这是最高层决策，决定后续所有工程。参考方法论一。
2. **若进 LLVM，学 AMDGPU 范本**：AMDGPU 是 GPU 后端最完整的实现，从 GCNProcessors.td 到 SIMachineScheduler 到 GlobalISel，全套都有。
3. **若绕过 LLVM，学飞腾/昇腾**：TVM fork + 外部编译器二进制 + 自定义 device type，是绕过 LLVM 的工程范本。
4. **NPU 用 MLIR，不用 LLVM IR**：NPU 架构（张量阵列）比 GPU（SIMT）更高层，MLIR 的 linalg/tensor dialect 比 LLVM IR 更适合。
5. **关注 SPIR-V**：即使绕过 LLVM，SPIR-V 是跨厂商"够用层"，未来通用计算/AI 推理可能必须支持。

---

> **本专家一句话**：**LLVM 的异构后端是 AI 算力的命脉，但这命脉吊在三家公司肩上——AMD 养 AMDGPU（250 文件、14 代硬件，AI 训练开源唯一完整后端）、NVIDIA 养 NVPTX（备胎，真正赢的是闭源 nvcc+EDG）、Qualcomm 养 Hexagon（单点 DSP）。SPIR-V 进主线是断层①唯一的"统一解药"，但永远赢不了 CUDA/HIP 的极致性能层。飞腾的 AI 算力选择绕过 LLVM（npu_compiler/gpu_compiler 闭源二进制），这是地缘+机密+对齐债下的工程理性，代价是放弃 LLVM 生态红利。所有中国 AI 芯片厂商都绕过 LLVM——这不是巧合，是国产化的工程共识。本专家盯着 GPU 后端的对齐债，市场盯着"这块卡能不能跑我的模型"——两者经常错位，但命脉只认后者。**
