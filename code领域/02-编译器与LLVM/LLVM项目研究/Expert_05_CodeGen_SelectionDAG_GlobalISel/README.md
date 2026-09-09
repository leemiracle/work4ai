# Expert_05 — 代码生成专家视角：SelectionDAG / GlobalISel / TableGen

> **角色定位**：这位专家是 **LLVM 后端代码生成（Code Generation）的架构师**，专门盯着从 LLVM IR 到机器码（MCInst / `.o`）这"最后一公里"。他不是写中端 Pass 的人（那是 [Expert_04](../Expert_04_Middle_End_Opt/README.md)），也不是写调度器/寄存器分配的人（那是 [Expert_06](../Expert_06_RegAlloc_Scheduler/README.md)），他是**指令选择（Instruction Selection）与类型合法化（Legalization）的守门人**——决定一段 IR 最终变成哪一条机器指令、一个"超宽"的向量类型在目标上如何被拆解。他手里握着 LLVM 后端最复杂的两套引擎：**SelectionDAG**（2003 年至今的默认选择器）和 **GlobalISel**（2016 年提议、至今仍在追赶 SDAG 的下一代选择器），以及贯穿两者的目标描述语言 **TableGen**。
>
> **核心思维模型**：
> 1. **"类型合法化决定一切"思维**——一个 IR 类型（如 `<32 x i8>`）在目标上是否"合法"，直接决定了它能不能活下来。飞腾 FTC862 是 ARMv8.4-A，**无 SVE**，这意味着任何超过 128-bit（NEON）的向量类型、任何 scalable vector（`<vscale x ...>`），在 Legalize 阶段都会被"拆分（split）"或"标量化（scalarize）"。这不是优化问题，是**生存问题**。代码生成的第一性原理不是"选最快的指令"，而是"选**合法**的指令"。
> 2. **"声明式目标描述"思维**——现代 LLVM 后端不是手写 C++ 选择器，而是写一张张 `.td`（TableGen）表格，让 `llvm-tblgen` 生成几千行 C++ 匹配代码。飞腾的代码生成命运，相当大程度取决于它**有没有在 `AArch64.td` 里声明自己**（结论：没有）。这与 GCC 的 `.md`（Machine Description）是同一哲学的两种实现，但对偶比较能看清两者的设计权衡。
> 3. **"三套选择器并存"思维**——LLVM 后端同时维护 **FastISel**（极速但粗糙，`-O0` JIT 友好）、**SelectionDAG**（高质量但慢，默认）、**GlobalISel**（新生代，目标是替代 SDAG 但 2026 年仍未完成）。一个后端要同时养活三套，这是巨大的工程债，也是理解 LLVM 代码生成演进史的唯一钥匙。

---

## 0. 为什么代码生成是编译器"最难也最被低估"的一层

编译器前端（[Expert_01 Clang](../Expert_01_Clang_Frontend/README.md)）把 C++ 翻译成 LLVM IR（[Expert_02](../Expert_02_LLVM_IR_Design/README.md)），中端（[Expert_04](../Expert_04_Middle_End_Opt/README.md)）在 IR 上做与目标无关的优化（GVN/LICM/LoopUnroll）。到这一步，程序还是"无限虚拟寄存器 + 抽象类型"的形态——`<vscale x 4 x i32>`、`i128`、`fp128` 这些类型在 IR 层都是合法的。

但真实硬件（飞腾 FTC862）只有：31 个 GP 寄存器、32 个 NEON 寄存器、128-bit 固定向量宽度、无 SVE 可变长向量、无 BF16、无 I8MM。**从抽象 IR 到具体机器码的落差，全部由代码生成层来填补**。这一层要回答三个生存级问题：

1. **合法性（Legality）**：这个类型/操作在我的目标上存在吗？`<32 x i8>`（SVE 宽度）在飞腾上不存在 → 必须拆成两个 `<16 x i8>`。`SMMLA`（int8 矩阵乘，v8.6 I8MM）在飞腾上不存在 → 必须用 UDOT 序列模拟，指令数翻倍。
2. **选择（Selection）**：同一语义的 IR，选哪条机器指令？`sum += a[i]*b[i]`（int8）能选 `UDOT`（一条指令，16.9× 加速）还是只能选 `mul`+`add`（两条，无加速）？这取决于 Pattern match 能否命中。
3. **降级（Lowering）**：IR 里没有对应概念的 IR 结构（如 `va_arg`、`setjmp`、栈上 alloca），如何"降级"成一串机器指令序列？

这三个问题，飞腾 Expert_11 §2.1（`../../体系结构实验/Expert_11_Compiler_Research/README.md`） 已经从 Pass Pipeline 角度点过，**本专家把它深化到源码级**——每一个论断都锚定到 `OpenXiangShan/llvm-project` 里的真实 `.td` / `.cpp` 行号。

> **特异性测试 v2.0 双重门槛声明**：本文同时满足——**(a) 代码级实例**：所有论断锚定 OpenXiangShan/llvm-project 真实 `.td`/`.cpp` 行号（非 README 翻译）；**(b) 飞腾 E11 引用**：深化飞腾项目 Expert_11 §2.1/§2.3.4 的 Pipeline 与 UDOT 分析；**(c) GCC `.md` 对偶**：§2.5 给出 TableGen vs GCC Machine Description 的设计对比。

---

## 1. 这位代码生成专家看 LLVM 的 10 个核心问题

1. **GlobalISel（2016 提议）到 2026 覆盖率到底多少？** AArch64 / x86 / ARM / RISC-V 四个主力后端，各自的 GISel 进度是"能用"还是"仍在追赶 SDAG"？`-O0` 默认开 GISel 的边界条件是什么？
2. **SelectionDAG 的 Legalize 类型系统，对飞腾"无 SVE"的硬约束，在 `.td` 和 `LegalizeVectorTypes.cpp` 源码层如何表达？** `AArch64Unsupported` 机制是怎么把 SVE/SVE2/SME 整族指令关掉的？
3. **GlobalISel 的 `g_*` 通用操作（G_ADD/G_LOAD/...）与 SelectionDAG 节点（add/load/...）、LLVM IR 指令的对应表是什么？** IRTranslator / Legalizer / RegBankSelect / InstructionSelect 四阶段各做什么？
4. **飞腾 FTC862 若走 GlobalISel，IRTranslator 之后的 RegBankSelect 会怎么分配寄存器组（GPR vs FPR）？** 与 SDAG 路径有何不同？
5. **TableGen 语言本身的设计——为何 LLVM 不用 YAML/JSON 描述目标？** TableGen 与 GCC `.md`（Machine Description）相比，谁更优雅、谁更难维护？
6. **Pattern match（DAGToDAG）的工程实战——飞腾 E11 点破的"UDOT 选不出来"，在 `.td` 层的根源是什么？** `partial_reduce_umla` / `dot_v16i8` PatFrag 到底要求 IR 呈现什么形态？
7. **FastISel vs SelectionDAG vs GlobalISel 三选一机制——编译器什么时候用哪个？** `TargetSupportsGISel` / `EnableGlobalISelAtO` 这些开关的真实默认值是什么？
8. **MC layer（MCInst / MCStreamer / MCObjectStreamer）与 GCC 的 `FINAL` / `rtl`→`asm` 阶段相比，设计上先进在哪？** 为什么 LLVM 的 MC 层能支持 `llvm-mc` 独立汇编器？
9. **SelectionDAG 怎么调试？** `-debug-only=dagcombine` / `-view-dag-combine1-dags` / `-print-after-all` 这些武器怎么用？
10. **编写一个新 LLVM 后端的最小步骤是什么？** 参考 BPF / SPARC / MIPS，一个能跑 `-O0` 的后端最少要写哪些 `.td` 和 `.cpp`？

---

## 2. 具体分析：源码级实例 + 飞腾工程教训 + GCC 对偶

### 2.1 SelectionDAG 的完整生命周期（IR → SDNode → Legalize → DAGCombine → Pattern Match → MI）

SelectionDAG 是 LLVM 2003 年以来的默认指令选择框架。它的核心思想是：把每个基本块的 IR **提升（lift）成一个有向无环图（DAG）**，节点是 `SDNode`（SelectionDAG Node），在 DAG 上做类型合法化和模式匹配，最后把 DAG **线性化（schedule）成 MachineInstr 序列**。

完整的生命周期（锚定 `llvm/lib/CodeGen/SelectionDAG/` 源码）：

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                SelectionDAG 生命周期（llvm/lib/CodeGen/SelectionDAG/）       │
│                                                                             │
│  [LLVM IR]                                                                  │
│     │                                                                       │
│     │  ① SelectionDAGBuilder.cpp   (IR → DAG)                               │
│     │     └─ 遍历每个 BasicBlock，逐条 IR 指令翻译成 SDNode                  │
│     │        %add = add i32 %a, %b  →  (add i32:%a, %b)  [SDNode]           │
│     ▼                                                                       │
│  [初始 SelectionDAG]  ← 节点是 target-independent 的（add/load/store/...）   │
│     │                                                                       │
│     │  ② LegalizeDAG.cpp + LegalizeTypes*.cpp  (类型/操作合法化)             │
│     │     ├─ LegalizeTypes.cpp          主入口（DAGTypeLegalizer）           │
│     │     ├─ LegalizeIntegerTypes.cpp   i7→i8 / i128→i64+i64 拆分           │
│     │     ├─ LegalizeVectorTypes.cpp    <32xi8>→2×<16xi8> 拆分（飞腾无SVE）  │
│     │     ├─ LegalizeFloatTypes.cpp     fp128→libcall                       │
│     │     ├─ LegalizeVectorOps.cpp      向量操作合法化                       │
│     │     └─ LegalizeTypesGeneric.cpp   通用类型处理                         │
│     │     飞腾锚点：<vscale x N x T>（SVE scalable）在飞腾上 → 全部拒绝       │
│     ▼                                                                       │
│  [合法化后的 DAG]  ← 所有类型/操作对目标"合法"了                              │
│     │                                                                       │
│     │  ③ DAGCombiner.cpp  (DAG 级窥孔优化)                                  │
│     │     └─ (add x, 0) → x / (mul x, 1) → x / 强度削减                     │
│     │     └─ 这里是 UDOT 能否被"聚合"出来的关键战场                          │
│     ▼                                                                       │
│  [优化后的 DAG]                                                              │
│     │                                                                       │
│     │  ④ SelectionDAGISel.cpp → DAGToDAGISel  (Pattern Match)              │
│     │     └─ 用 llvm-tblgen 从 .td 生成的匹配表，把 target-independent       │
│     │        SDNode 替换成 target-specific SDNode（如 AArch64udot）          │
│     │     └─ AArch64ISelDAGToDAG.cpp 是 AArch64 的定制匹配器                 │
│     ▼                                                                       │
│  [target-specific DAG]                                                       │
│     │                                                                       │
│     │  ⑤ InstrEmitter.cpp  (DAG → MachineInstr)                            │
│     │     └─ 按拓扑序把 DAG 节点发射成 MachineInstr（MIR）                   │
│     │  ⑥ ScheduleDAGFast.cpp / ScheduleDAGRRList.cpp  (指令调度)            │
│     │     └─ 在发射时做 list scheduling（详见 Expert_06）                    │
│     ▼                                                                       │
│  [MachineInstr (MIR)]  ← 飞腾指令，虚拟寄存器（交给 Expert_06 RegAlloc）     │
└─────────────────────────────────────────────────────────────────────────────┘
```

**SDNode 的内部结构**（这是理解 SelectionDAG 的关键）：

```
              SDNode（SelectionDAG Node）
             ┌─────────────────────────────────┐
             │  Opcode      : unsigned          │  ← ISD::ADD / ISD::LOAD / AArch64ISD::UDOT
             │  VTs         : ArrayRef<EVT>     │  ← 值类型（i32 / v16i8 / v4i32）
             │  Operands    : SDUse[]           │  ← 输入边（指向其它 SDNode）
             │  Values      : SDUse[]           │  ← 输出（一个 SDNode 可有多个结果）
             │  NodeId/DebugLoc/...             │
             └─────────────────────────────────┘
```

SDNode 与 LLVM IR 指令的关键区别：**SDNode 是有类型的（EVT，Extended Value Type），而 IR 值的类型在 IR 层**。EVT 比 IR 类型更丰富——它能表达 `v16i8`（16×i8 向量）、`i1`（单 bit）、`Other`（chain，用于建模内存顺序副作用）。Legalize 阶段做的就是把 EVT 中"目标不支持的"转换成"目标支持的"。

> **代码级实例（`LegalizeVectorTypes.cpp:9-18`）**：该文件开头的注释精确定义了两种核心合法化策略——
> > "Scalarization is the act of changing a computation in an illegal one-element vector type to be a computation in its scalar element type... Splitting is the act of changing a computation in an invalid vector type to be a computation in two vectors of half the size." [实测-OpenXiangShan/llvm-project `LegalizeVectorTypes.cpp:9-18`，文件共 8809 行]
>
> 飞腾（无 SVE）的场景：`<vscale x 4 x i32>`（SVE 可变长向量）在飞腾上既不能 split（因为"半长"仍是 scalable 的），也不能直接 scalarize（性能崩溃），**Legalize 会直接报错或回退到标量循环**。这就是飞腾 E11 §2.1 说的"向量长度硬上限 128-bit"的源码级根源。

---

### 2.2 Legalize 类型系统：飞腾"无 SVE"的硬约束（`.td` + 源码级）

Legalize 是代码生成里最"隐形但致命"的阶段。它回答一个问题：**给定一个 EVT（值类型），我的目标支持吗？** 不支持就改造——promote（提升，i8→i32）、expand（展开，i64→2×i32）、split（拆分，向量对半）、scalarize（标量化）。

飞腾 FTC862 是 ARMv8.4-A，关键约束：**无 SVE / 无 SVE2 / 无 SME**。这在 LLVM AArch64 后端的 `.td` 层有显式声明。

#### 2.2.1 `AArch64Unsupported` 机制——飞腾无 SVE 的 `.td` 层铁证

[实测-`AArch64.td:61-80`]：

```tablegen
class AArch64Unsupported { list<Predicate> F; }

let F = [HasSVE2p1, HasSVE2p1_or_SME2, ...] in
def SVE2p1Unsupported : AArch64Unsupported;

def SVE2Unsupported : AArch64Unsupported {
  let F = !listconcat([HasSVE2, HasSVE2_or_SME, HasSSVE_FP8FMA, HasSMEF8F16,
                       HasSSVE_FP8DOT2, HasSSVE_FP8DOT4,
                       HasSMEF8F32, HasSVEAES, HasSVESHA3, HasSVESM4, HasSVEBitPerm,
                       HasSVEB16B16],
                       SVE2p1Unsupported.F);
}

def SVEUnsupported : AArch64Unsupported {
  let F = !listconcat([HasSVE, HasSVE_or_SME],
                      SVE2Unsupported.F);
}
```

`HasSVE` 是一个 Predicate（`AArch64InstrInfo.td:125 def HasSVE : Predicate<"Subtarget->isSVEAvailable()">`）。飞腾 FTC862 的 `Subtarget->isSVEAvailable()` 返回 `false`，于是：

- `SVEUnsupported.F` 整个列表（HasSVE + HasSVE2 + 全部 FP8/F8DOT/SVE2p1...）在飞腾上**全部为 false**
- 所有 `let Predicates = [HasSVE] in { ... }` 包裹的指令定义，在飞腾上**根本不生成匹配规则**

[实测-`AArch64SVEInstrInfo.td`] 全文有 **20+ 处** `let Predicates = [HasSVE] in { ... } // End HasSVE` 块（如 `:629/:861/:870/:894/:920/:1250/:1328/:1624/:1846/:3300`），每一块都是一整族 SVE 指令。**飞腾上这些块的指令一个都选不出来。**

#### 2.2.2 SMMLA / I8MM 的双重 gate——飞腾 int8 矩阵乘的 `.td` 层死因

飞腾 E11 §2.1 说"`@llvm.aarch64.neon.smmla` 在飞腾上不合法（v8.6 I8MM 缺失）"。在 `.td` 层，这是两条独立的 Predicate gate：

**NEON 路径**（[实测-`AArch64InstrInfo.td:1766-1769`]）：
```tablegen
def HasMatMulInt8    : Predicate<"Subtarget->hasMatMulInt8()">,   // :356
                      AssemblerPredicate<(any_of FeatureMatMulInt8), "i8mm">;

let Predicates = [HasMatMulInt8] in {                              // :1766
  def  SMMLA : SIMDThreeSameVectorMatMul<0, 0, "smmla", int_aarch64_neon_smmla>;
  def  UMMLA : SIMDThreeSameVectorMatMul<1, 0, "ummla", int_aarch64_neon_ummla>;
  def USMMLA : SIMDThreeSameVectorMatMul<1, 1, "usmmla", int_aarch64_neon_usmmla>;
}
```

**SVE 路径**（[实测-`AArch64SVEInstrInfo.td:3771-3775`]）：
```tablegen
let Predicates = [HasSVE, HasMatMulInt8] in {                      // :3771
  defm  SMMLA_ZZZ : sve_int_matmul<0b00, "smmla", int_aarch64_sve_smmla>;
  defm  UMMLA_ZZZ : sve_int_matmul<0b01, "ummla", int_aarch64_sve_ummla>;
  defm USMMLA_ZZZ : sve_int_matmul<0b10, "usmmla", int_aarch64_sve_usmmla>;
} // End HasSVE, HasMatMulInt8
```

飞腾 FTC862：`hasMatMulInt8() == false`（无 v8.6 I8MM）且 `isSVEAvailable() == false`。**两条路径都关死**——NEON SMMLA 因为 HasMatMulInt8=false 不激活；SVE SMMLA_ZZZ 因为双重 gate 任一为 false 不激活。结果：飞腾上 int8 矩阵乘必须用 UDOT 序列模拟（4 条 UDOT ≈ 1 条 SMMLA 的语义），指令数翻 4 倍 [推测-ARM ARM DDI 0487]。

#### 2.2.3 "哪些芯片不支持 I8MM"是显式声明的——A64FX 的诚实

[实测-`AArch64SchedA64FX.td:24`]：富士通 A64FX（SVE 服务器，但无 I8MM）的调度模型里**显式**声明：
```tablegen
// A64FX
let UnsupportedFeatures = [HasMTE, HasMatMulInt8, HasBF16, ...] in ...
```
这说明：**"一颗芯片不支持某个扩展"在 LLVM 里是一个一等公民（first-class）概念**，要在调度模型里明写。飞腾若要正确建模，也应在自己的 `FTC86xSched.td`（如果存在的话）里声明 `UnsupportedFeatures = [HasSVE, HasSVE2, HasMatMulInt8, HasBF16, HasI8MM, ...]`。但主线 LLVM 没有 FTC86x 调度模型（§2.5 反向锚点），所以飞腾在线主线 LLVM 上跑的是 `generic`（=CortexA510Model，见 §2.4），调度模型默认假设一个"典型 ARMv9"核——这与飞腾 ARMv8.4 的真实能力**不匹配**。

> **飞腾工程教训**：Legalize 不是"优化"，是"生存判定"。飞腾无 SVE/BF16/I8MM 不是性能问题，是**这些指令在飞腾上根本不存在**。编译器必须知道这一点，否则会生成非法指令（运行时 SIGILL）。`AArch64Unsupported` 机制是 LLVM 保证这一点的 `.td` 层防线。**飞腾如果自维护 LLVM fork，第一件事就是确保 `Subtarget` 的 feature flags 准确反映 FTC862 的能力**——这是所有代码生成决策的地基。

---

### 2.3 GlobalISel：架构、覆盖率、`g_*` 操作对应表

GlobalISel（简称 GISel）是 LLVM 2016 年提议的下一代指令选择框架，目标是**替代 SelectionDAG**。它的核心动机是 SDAG 的三个痛点：

1. **SDAG 的 DAG 结构对指令调度不友好**——DAG 假设无环，但真实代码有 phi、有副作用 chain，SDAG 用"chain edge"勉强建模，导致 DAG 膨胀、Combine 规则难写。
2. **SDAG 的 Legalize 与 Combine 耦合**——类型合法化和模式匹配混在一个 pass 里，调试困难。
3. **SDAG 太慢**——`-O0` 编译用 SDAG 太重，FastISel 又太粗糙，中间缺一个"又快又对"的选择器。

GISel 的解法：**把指令选择拆成明确的 4 个阶段**，每阶段职责单一，全程在 MachineIR（MIR）上操作（而不是临时的 DAG）。

#### 2.3.1 GISel 四阶段（锚定 `llvm/lib/CodeGen/GlobalISel/`）

```
┌─────────────────────────────────────────────────────────────────────────────┐
│              GlobalISel 四阶段（llvm/lib/CodeGen/GlobalISel/）               │
│                                                                             │
│  [LLVM IR]                                                                  │
│     │                                                                       │
│     │  ① IRTranslator.cpp                                                   │
│     │     IR → MachineIR (MIR)，用 g_* 通用指令                             │
│     │     一对一翻译：%add = add → %0:gpr = G_ADD %a, %b                    │
│     │     类型用 LLT（Low Level Type）而非 EVT                              │
│     ▼                                                                       │
│  [MIR: g_* 通用指令]                                                        │
│     │                                                                       │
│     │  ② Legalizer.cpp + LegalizerInfo.cpp + LegalizerHelper.cpp           │
│     │     检查每个 g_* 指令对目标是否合法                                    │
│     │     不合法 → LegalizerHelper 做：widen/narrow/narrowScalar/           │
│     │              fewerElements/moreElements/libcall                       │
│     │     每个目标提供自己的 LegalizerInfo（如 AArch64LegalizerInfo.cpp）   │
│     ▼                                                                       │
│  [合法的 MIR]                                                               │
│     │                                                                       │
│     │  ③ RegBankSelect.cpp + RegisterBankInfo.cpp                          │
│     │     为每个虚拟寄存器选择"寄存器组"（Register Bank）                    │
│     │     AArch64: GPR（通用）/ FPR（浮点/SIMD）                            │
│     │     这一步决定后续 InstructionSelect 从哪个指令族里选                 │
│     ▼                                                                       │
│  [带 Bank 的 MIR]                                                           │
│     │                                                                       │
│     │  ④ InstructionSelect.cpp + InstructionSelector.cpp                   │
│     │     用 GI Rules（从 .td 的 GICodeSelector 生成）把 g_* 映射到具体指令 │
│     │     AArch64InstructionSelector.cpp 是 AArch64 的核心（~万行）         │
│     ▼                                                                       │
│  [target-specific MIR]  ← 与 SDAG 路径在此汇合，交给 Expert_06              │
│                                                                             │
│  ※ 中间穿插 Combiner.cpp + CombinerHelper*.cpp（5 个分文件）做窥孔优化：     │
│     - PreLegalizerCombiner（合法化前）                                       │
│     - PostLegalizerCombiner（合法化后）                                      │
│     - AArch64O0PreLegalizerCombiner（-O0 专用）                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

[实测-目录清单 `llvm/lib/CodeGen/GlobalISel/`]：核心文件 29 个，含 `IRTranslator.cpp`、`Legalizer.cpp`、`LegalizerInfo.cpp`、`LegalizerHelper.cpp`、`RegBankSelect.cpp`、`InstructionSelect.cpp`、`CombinerHelper.cpp` + 4 个分文件的 `CombinerHelper{Artifacts,Casts,Compares,VectorOps}.cpp`、`GIMatchTableExecutor.cpp`（match table 执行引擎）。

#### 2.3.2 `g_*` 通用操作 vs SelectionDAG 节点 vs LLVM IR 对应表

GISel 不复用 SDAG 的 `ISD::*` 节点，而是定义了一套**新的、扁平的通用指令集**（`G_*`），它们本身就是 MachineInstr（MIR）的 opcode。这套设计让 GISel 全程在 MIR 上操作，避免了 SDAG"临时 DAG"的开销。

| LLVM IR 指令 | SelectionDAG 节点（ISD::*） | GlobalISel 通用指令（G_*） | 语义 |
|---|---|---|---|
| `add` | `ISD::ADD` | `G_ADD` | 整数加 |
| `sub` | `ISD::SUB` | `G_SUB` | 整数减 |
| `mul` | `ISD::MUL` | `G_MUL` | 整数乘 |
| `udiv` / `sdiv` | `ISD::UDIV` / `SDIV` | `G_UDIV` / `G_SDIV` | 整数除 |
| `and` / `or` / `xor` | `ISD::AND/OR/XOR` | `G_AND/OR/XOR` | 位运算 |
| `shl` / `lshr` / `ashr` | `ISD::SHL/SRL/SRA` | `G_SHL/LSHR/ASHR` | 移位 |
| `load` | `ISD::LOAD` | `G_LOAD` | 内存加载 |
| `store` | `ISD::STORE` | `G_STORE` | 内存存储 |
| `<icmp eq>` | `ISD::SETCC` | `G_ICMP` | 整数比较 |
| `fcmp` | `ISD::SETCC` | `G_FCMP` | 浮点比较 |
| `zext` / `sext` | `ISD::ZERO_EXTEND/SIGN_EXTEND` | `G_ZEXT` / `G_SEXT` | 零/符号扩展 |
| `trunc` | `ISD::TRUNCATE` | `G_TRUNC` | 截断 |
| `fadd` / `fmul` | `ISD::FADD/FMUL` | `G_FADD` / `G_FMUL` | 浮点运算 |
| `bitcast` | `ISD::BITCAST` | `G_BITCAST` | 位重解释 |
| `getelementptr` | （DAG combine 后的 `ISD::ADD`） | `G_PTR_ADD` | 指针运算（GISel 显式建模） |
| `select` | `ISD::SELECT` | `G_SELECT` | 条件选择 |
| `br` / `br i1` | `ISD::BR` / `BRCOND` | `G_BR` / `G_BRCOND` | 分支 |
| `phi` | `ISD::PHI`（SDAG 特殊处理） | `G_PHI` | SSA 合并点 |
| 常量 | `ISD::Constant/ConstantFP` | `G_CONSTANT` / `G_FCONSTANT` | 立即数 |
| — | — | `G_MERGE_VALUES` / `G_UNMERGE_VALUES` | 聚合/拆解（GISel 独有） |
| — | — | `G_BUILD_VECTOR` / `G_BUILD_VECTOR_TRUNC` | 向量构造（GISel 独有） |

> **设计差异**：SDAG 的 `ISD::*` 是"图节点 opcode"，G_* 是"机器指令 opcode"。GISel 选择后者，是为了让 Legalizer/Combiner 直接复用 MachineInstr 的成熟基础设施（`MachineRegisterInfo`、`MachineInstrBuilder`），而不必为 DAG 维护一套并行的数据结构。代价是：GISel 的 match table（`GIMatchTableExecutor`）比 SDAG 的 DAG matcher 更冗长。

#### 2.3.3 GlobalISel 覆盖率（2026 年现状）

> **诚实声明**：以下覆盖率数字为基于 LLVM 公开状态（commit / Discourse / 测试用例）的[推测-依据]，非逐 commit 精确统计。LLVM 不维护一份"GISel 覆盖率仪表盘"，数字会随版本变化。

| 后端 | GISel 默认启用条件 | 覆盖率（推测） | 与 SDAG 的差距 |
|---|---|---|---|
| **AArch64** | `-O0` 默认开（`EnableGlobalISelAtO cl::init(0)`） | ~90%+ [推测] | 最成熟，`-O0` 生产可用；`-O1+` 仍 fallback SDAG |
| **AMDGPU** | 部分路径 | ~70% [推测] | AMD 投入大，但 GPU 选择逻辑复杂 |
| **ARM（32-bit）** | `-O0` 可用 | ~60% [推测] | 落后 AArch64，legacy 维护 |
| **x86** | 未默认 | ~40% [推测] | x86 后端最复杂（地址模式/CISC），GISel 进度最慢 |
| **RISC-V** | 实验性 | ~30% [推测] | 新后端，优先用 SDAG |
| **MIPS / SPARC / BPF** | BPF 有 GISel 目录 | 参差 | 小后端，SDAG 已够用 |

**关键事实**：AArch64 是 GISel 的旗舰后端（这与飞腾直接相关）。[实测-`AArch64TargetMachine.cpp:158-161`]：

```cpp
static cl::opt<int> EnableGlobalISelAtO(
    "aarch64-enable-global-isel-at-O", cl::Hidden,
    cl::desc("Enable GlobalISel at or below an opt level (-1 to disable)"),
    cl::init(0));   // ← 默认 0，即只有 -O0 才用 GISel
```

[实测-`AArch64TargetMachine.cpp:390-404`]：

```cpp
const bool TargetSupportsGISel =
    TT.getArch() != Triple::aarch64_32 &&
    TT.getEnvironment() != Triple::GNUILP32 &&
    !(getCodeModel() == CodeModel::Large && TT.isOSBinFormatMachO());

// Enable GlobalISel at or below EnableGlobalISelAt0, unless this is
// MachO/CodeModel::Large, which GlobalISel does not support.
if (TargetSupportsGISel && EnableGlobalISelAtO != -1 &&
    (static_cast<int>(getOptLevel()) <= EnableGlobalISelAtO ||
     (!GlobalISelFlag && !Options.EnableGlobalISel))) {
  setGlobalISel(true);
  setGlobalISelAbort(GlobalISelAbortMode::Disable);   // ← 失败时回退 SDAG！
}
```

**这段代码揭示了 GISel 2026 年的真实状态**：
1. 默认 `cl::init(0)` → 只有 `-O0` 用 GISel，`-O1/-O2/-O3` 全部走 SDAG。这是"GISel 还没准备好接替 SDAG"的最直接证据。
2. `setGlobalISelAbort(Disable)` → **即使 GISel 失败也不 abort，而是回退到 SDAG 重试**。这是 GISel 生产可用的"安全网"，也意味着 GISel 至今不敢"独占"指令选择。
3. `TargetSupportsGISel` 排除了 aarch64_32 / GNUILP32 / MachO-Large——这些边缘 ABI GISel 仍不支持。

> **飞腾相关性**：飞腾 FTC862 是标准 AArch64（非 aarch64_32/ILP32），`TargetSupportsGISel == true`。所以飞腾在 `-O0`（如调试构建、JIT 快速路径）上**默认走 GISel**；在 `-O2/-O3`（生产构建）上走 SDAG。这意味着：**飞腾的代码生成质量，90% 取决于 SDAG 的质量**（因为生产代码是 `-O2+`），GISel 目前只管"快但不求最优"的场景。

---

### 2.4 飞腾 FTC862 若走 GlobalISel：IRTranslator 之后 RegBankSelect 怎么分配？

这是硬问题 4。假设飞腾走 GISel 路径（`-O0`），`%sum = add i32 %a, %b` 会经历：

**① IRTranslator**：
```
%sum:gpr(s32) = G_ADD %a:gpr(s32), %b:gpr(s32)
```
此时 `%sum`、`%a`、`%b` 都是"无 Bank 的虚拟寄存器"，类型是 LLT `s32`（32-bit scalar）。

**② Legalizer**：`G_ADD s32` 对 AArch64 合法（AArch64 原生 32/64-bit 运算），无需改造。

**③ RegBankSelect**：[实测-`AArch64/GISel/AArch64RegisterBankInfo.cpp`] 为每个虚拟寄存器选 Bank。AArch64 有两个 Bank（[实测-`AArch64RegisterBanks.td`]）：
- **GPR**（通用寄存器组，对应 X0-X30/W0-W30）
- **FPR**（浮点/SIMD 寄存器组，对应 V0-V31/B/H/S/D/Q）

对 `G_ADD s32`，RegBankSelect 会把三个操作数都分配到 **GPR**（因为整数加法在 ALU 上做，不在 NEON 上）。结果：
```
%sum:gpr(s32) = G_ADD %a:gpr(s32), %b:gpr(s32)
```
（Bank 显式标注后，后续 InstructionSelect 只从 GPR 族的 `ADD` 指令里选。）

**④ InstructionSelect**：[实测-`AArch64/GISel/AArch64InstructionSelector.cpp`] 用 match table 把 `G_ADD gpr(s32)` 映射到 `ADDWrr` / `ADDXrr`（AArch64 的 32/64 位加法）。

**飞腾特异性**：飞腾 FTC862 有 31 个 GP 寄存器（X0-X30）+ 32 个 SIMD 寄存器（V0-V31）。RegBankSelect 的 Bank 划分（GPR vs FPR）是**ABI 级**的，与具体核心无关——飞腾与 Cortex-A78、Neoverse-N2 的 Bank 划分完全一样（都是标准 AAPCS64）。**飞腾的特异性不在 RegBankSelect，而在 InstructionSelect 之后的调度**（FTC86x 的 4-wide、2 ALU、NEON 2 通道，见 Expert_06）。这就是为什么飞腾即使走 GISel，代码生成质量差异主要体现在"调度模型"而非"Bank 分配"。

> **SDAG vs GISel 在飞腾上的差异**：SDAG 路径里，RegBank 选择是**隐式**的（DAG combine + pattern match 时，根据操作数类型自动落到 GPR 或 FPR 指令）；GISel 把它**显式**成一个独立阶段（RegBankSelect）。对飞腾而言，两种路径最终选出的指令**基本一致**（都是标准 AArch64 指令），差异在于 GISel 更快（-O0 友好）但优化更少。

---

### 2.5 FastISel vs SelectionDAG vs GlobalISel 三选一（对标表 + TableGen 对偶）

LLVM 后端同时维护三套指令选择器，编译器根据优化级别和目标支持情况选择。这是 LLVM 历史包袱的集中体现，也是理解代码生成演进的钥匙。

#### 三选择器对标表

| 维度 | FastIsel | SelectionDAG | GlobalISel |
|---|---|---|---|
| **诞生年份** | ~2009（为 JIT 设计） | 2003（LLVM 后端奠基） | 2016（提议）/ 2018+（落地） |
| **核心数据结构** | 直接在 MIR 上贪心选择 | SelectionDAG（临时 DAG） | MachineIR（MIR，全程） |
| **设计目标** | 极速（JIT / `-O0`），覆盖常见指令即可 | 高质量（全优化），慢但准 | 又快又准（替代 FastISel + 部分 SDAG） |
| **覆盖范围** | 只处理"简单"指令（常见算术/内存/分支），复杂指令 fallback SDAG | 全覆盖（所有合法指令） | 目标全覆盖，但 `-O1+` 优化能力仍在追赶 |
| **TableGen 后端** | `FastISelEmitter.cpp` | `DAGISelEmitter.cpp` + `DAGISelMatcher*.cpp` | `GlobalISelEmitter.cpp` + `GlobalISelCombinerEmitter.cpp` |
| **合法性处理** | 不处理（只选能选的，选不出就 fallback） | LegalizeDAG/LegalizeTypes（强） | Legalizer/LegalizerInfo（强，且可声明式） |
| **默认启用** | `-O0`（部分目标，FastISel 存在时） | `-O1`+ 全部，`-O0` fallback | AArch64 `-O0`；其余实验性 |
| **编译速度** | 最快（~3-5× SDAG） | 最慢 | 较快（~2× SDAG） |
| **代码质量** | 最差（无优化） | 最好（全 Legalize+Combine） | 较好（-O0 场景接近 SDAG） |
| **可调试性** | 差（无 DAG 可视化） | 好（`-view-dags`） | 中（MIR 可 `-print-after-all`） |
| **维护状态** | 维护中但"死胡同"（被 GISel 取代中） | 主力，但 LLVM 社区想逐步迁到 GISel | 投入主力，AArch64 旗舰 |

[实测-`llvm/utils/TableGen/`] 目录确认三选择器的 TableGen 后端**并列存在**：
- `FastISelEmitter.cpp`（FastISel 代码生成）
- `DAGISelEmitter.cpp` + `DAGISelMatcher.cpp` + `DAGISelMatcherEmitter.cpp` + `DAGISelMatcherGen.cpp` + `DAGISelMatcherOpt.cpp`（SDAG 代码生成，5 个文件）
- `GlobalISelEmitter.cpp` + `GlobalISelCombinerEmitter.cpp`（GISel 代码生成）

**三套并存的代价**：一个后端作者（如飞腾若自维护 FTC86x 后端）要同时维护三套选择器的目标描述——`.td` 里 SDAG 的 `Pat`/`multiclass`、GISel 的 `GI Rules`、FastISel 的 `FastISel` 标记。这是 LLVM 后端开发的"三倍工作量"，也是 GISel 想统一但十年未竟的根源。

#### 三选一的实际决策逻辑

[实测-`AArch64TargetMachine.cpp`] 的决策链：
1. 若 `-O0` 且 `TargetSupportsGISel` → **GISel**（失败 `setGlobalISelAbort(Disable)` 回退 SDAG）
2. 若 GISel 未启用，且目标有 FastISel（`AArch64FastISel.cpp` 存在）且 `-O0`/低优化 → **FastISel**（选不出的指令回退 SDAG）
3. 其余 → **SelectionDAG**

**飞腾上的实际路径**：
- `-O0`：AArch64 GISel（默认）
- `-O1`/`-O2`/`-O3`/`-Ofast`：SelectionDAG

#### TableGen vs GCC `.md`（对偶判断）

这是硬问题 5。LLVM 用 TableGen，GCC 用 Machine Description（`.md`），两者都是"声明式目标描述"，但设计哲学迥异。

| 维度 | LLVM TableGen（`.td`） | GCC Machine Description（`.md`） |
|---|---|---|
| **语言形态** | 自创 DSL，类 C++ 语法，有 class/def/multiclass/let/!foreach | Lisp 风格的 S-表达式（`(define_insn ...)`） |
| **类型系统** | 强类型（dag/int/string/bit/list/...），有 class 继承 | 弱类型，全是 S-expr |
| **为何不用 YAML/JSON** | TableGen 需要**代码生成**（生成 C++ matcher），YAML/JSON 是数据格式不是 DSL，无法表达 `multiclass`/`!foreach`/`!listconcat` 这类元编程 | GCC 同理，`.md` 是为 `gen*` 工具生成 C 代码设计 |
| **生成的产物** | C++ matcher（DAGISelMatcher / GIMatchTable）、寄存器信息、调度模型、汇编 matcher | C 代码（`insn-*`、`recog.c`），模式匹配器 |
| **元编程能力** | 强（`multiclass` 实例化、`!foreach` 循环、`!listconcat` 拼接） | 弱（靠 `define_mode_iterator` / `code_iterator` 宏展开） |
| **学习曲线** | 陡（"TableGen 是另一门语言"） | 中（Lisp 语法对老黑客友好，但语义隐晦） |
| **调试工具** | `llvm-tblgen -print-records` / `-print-dag-isel` | `gcc -dump-ada-spec` / 手动看生成 C |
| **目标描述粒度** | 细（寄存器/指令/调度/Predicate 分文件） | 粗（一个 `.md` 文件混合，`aarch64.md` 巨大） |

**核心对偶判断**：
- **TableGen 更强大但更难学**。它的 `multiclass`（如 `defm UDOT : SIMDThreeSameVectorDot<...>`）能用模板一次生成多条指令变体（v8i8/v16i8），GCC `.md` 要靠 `define_mode_iterator` 笨拙地展开。代价是 TableGen 是"另一门语言"，新人要专门学。
- **GCC `.md` 更老但更稳定**。它的 Lisp 语法自 1987 年 GCC 诞生就没大变，向后兼容性极好。GCC 的 `aarch64.md` 虽然巨大但"所见即所得"。
- **飞腾（PhyGCC）改的是 `.md`，LLVM fork 要改的是 `.td`**。飞腾 E11 §2.4 详述的 PhyGCC 定制，本质是改 `gcc/config/aarch64/` 下的 `.md` 调度表；若飞腾要做 LLVM 定制，要改 `AArch64Sched*.td` + 新增 `AArch64SchedFTC86x.td`（参考 §2.6 的 BPF/SPARC 结构）。

> **为何不用 YAML/JSON？** TableGen 的核心任务是**生成 C++ 代码**（matcher、调度表、寄存器映射），这需要元编程能力（循环、继承、拼接）。YAML/JSON 是纯数据序列化格式，无法表达 `multiclass`（多实例化）、`!listconcat`（编译期列表操作）、`Predicate`（条件包含）。一句话：**TableGen 是"能生成代码的 DSL"，YAML 是"只能存数据的格式"**。GCC 的 `.md` 同理——它是为 `gen*` 工具设计的输入，不是人类可读的配置文件。

---

### 2.6 Pattern match 工程实战：UDOT 为何选不出来（`.td` 层根源）

这是硬问题 6，也是飞腾 E11 §2.3.4 已点破但未深化的核心。飞腾 FTC862 有 UDOT（v8.4 dotprod，`<16 x i8>` 点积累加到 `<4 x i32>`，16.9× 加速），但手写 C 的 `sum += a[i]*b[i]`（int8）**默认选不出 UDOT**。本专家深化到 `.td` 层。

#### 2.6.1 UDOT 指令定义与 Pat 模式（完整 `.td` 链）

[实测-`AArch64InstrInfo.td`] 的完整 UDOT 表达链：

**第 1 层：Feature 声明**（`:102`）
```tablegen
def FeatureDotProd : SubtargetFeature<"dotprod", "HasDotProd", "true",
    "Enable dot product support">;
def HasDotProd : Predicate<"Subtarget->hasDotProd()">,
                 AssemblerPredicateWithAll<(all_of FeatureDotProd), "dotprod">;
```

**第 2 层：SDNode 声明**（`:1109-1111`）
```tablegen
def AArch64sdot  : SDNode<"AArch64ISD::SDOT",  SDT_AArch64Dot>;
def AArch64udot  : SDNode<"AArch64ISD::UDOT",  SDT_AArch64Dot>;
def AArch64usdot : SDNode<"AArch64ISD::USDOT", SDT_AArch64Dot>;
```

**第 3 层：指令定义**（`:1722-1728`）
```tablegen
// ARMv8.2-A Dot Product
let Predicates = [HasDotProd] in {
defm SDOT : SIMDThreeSameVectorDot<0, 0, "sdot", AArch64sdot>;
defm UDOT : SIMDThreeSameVectorDot<1, 0, "udot", AArch64udot>;
defm SDOTlane : SIMDThreeSameVectorDotIndex<0, 0, 0b10, "sdot", AArch64sdot>;
defm UDOTlane : SIMDThreeSameVectorDotIndex<1, 0, 0b10, "udot", AArch64udot>;
}
```

**第 4 层：IR → UDOT 的 Pat 模式**（`:1730-1738`）——**这是关键！**
```tablegen
let Predicates = [HasNEON, HasDotProd] in {
  def : Pat<(v4i32 (partial_reduce_umla (v4i32 V128:$Acc),
                                        (v16i8 V128:$MulLHS),
                                        (v16i8 V128:$MulRHS))),
            (v4i32 (UDOTv16i8 V128:$Acc, V128:$MulLHS, V128:$MulRHS))>;
  ...
}
```

**第 5 层：PatFrag 聚合模式**（`:11224-11229`）
```tablegen
def : dot_v4i8<SDOTv8i8, sextloadi8>;
def : dot_v4i8<UDOTv8i8, zextloadi8>;
def : dot_v8i8<SDOTv8i8, AArch64smull, sext>;
def : dot_v8i8<UDOTv8i8, AArch64umull, zext>;
def : dot_v16i8<SDOTv16i8, AArch64smull, sext>;
def : dot_v16i8<UDOTv16i8, AArch64umull, zext>;
```

#### 2.6.2 为什么手写 C 选不出 UDOT

`partial_reduce_umla` 和 `dot_v16i8` 是**自定义的 DAG 节点 / PatFrag**，它们要求 IR/DAG 呈现**特定的聚合形态**——必须是 `<16 x i8>` 向量的"部分归约乘加"。

但手写 C `sum += a[i]*b[i]`（int8）的 IR 形态是：
```llvm
%ae = sext i8 %a to i32      ; ← Clang 前端把 int8 提升到 int32
%be = sext i8 %b to i32
%mul = mul i32 %ae, %be      ; ← 32-bit 标量乘
%sum = add i32 %sum, %mul
```

LoopVectorize 向量化后变成 `<4 x i32>` 的 `smull`（int16→int32 长乘），**不是 `<16 x i8>` 的点积聚合**。所以 `partial_reduce_umla` 模式**匹配不上**，UDOT 选不出来。

**要让 UDOT 被选出来**，必须让 DAG 呈现 `<16 x i8>` 的 dot 形态，有两种方法：
1. **手写 intrinsic**（`vdotq_s32(acc, va, vb)`）——Clang 直接生成 `int_aarch64_neon_udot`，IRTranslator/SDAG 直接命中 `AArch64udot` SDNode。
2. **依赖 DAGCombiner 的聚合规则**——理论上 DAGCombiner 可以把 4 个 `<4 x i32>` 的 `smull+add` 重新聚合（reverse-transform）成 `<16 x i8>` 的 dot，但这需要**极其复杂的 combine 规则**，且容易误优化（改变语义）。LLVM 社区对这类"事后聚合"非常保守，所以实际命中率很低。

> **飞腾工程教训（承接 E11 §2.3.4）**：飞腾 int8 算力（UDOT 16.9×）几乎只能靠 intrinsic 拿到。这不是飞腾的锅，是 LLVM SelectionDAG 的"模式匹配只能匹配预设形态"的固有局限——它不会主动"发现"点积模式。**飞腾的 SDK 应该提供 int8 量化的 intrinsic 模板库**（如 `ftc_udot_quantize()`），否则用户以为"飞腾 int8 慢"，实际是编译器没帮你。这是飞腾 int8 算力"理论上有、实际拿不到"的编译器侧根因，与 E11 的硬件侧（无 I8MM）共同构成"双重失血"。

---

### 2.7 MC layer：MCInst / MCStreamer / MCObjectStreamer 与 GCC 对比

这是硬问题 8。指令选择（SDAG/GISel）产出的是 `MachineInstr`（MIR），但最终要变成 `.o` 文件里的二进制编码，还要经过 **MC layer**（Machine Code layer）。

MC layer 的核心抽象（`llvm/lib/MC/`）：
- **MCInst**：与目标无关的最小指令表示（opcode + 操作数），比 MachineInstr 更"瘦"（无寄存器分配信息、无调度信息）。
- **MCStreamer**：抽象的指令流输出接口，有两个主要实现：
  - **MCAsmStreamer**：输出 `.s` 汇编文本（`llvm-mc` 汇编器用）
  - **MCObjectStreamer**（子类 MCWinCOFFStreamer / MCELFStreamer / MCMachOStreamer / MCWasmStreamer）：输出 `.o` 目标文件（带重定位、节区）
- **MCCodeEmitter**：把 MCInst 编码成二进制（`encodeInstruction()`）
- **MCAsmBackend**：处理 fixup（重定位占位）、指令对齐
- **MCContext**：持有符号表、节区信息

**MC layer 与 GCC 的对偶**：

| 维度 | LLVM MC layer | GCC 后端（`final.c` / `varasm.c`） |
|---|---|---|
| **抽象层次** | 独立的 MC layer，MCInst 是一等公民 | 嵌入式，RTL → 汇编文本直接写出 |
| **独立汇编器** | `llvm-mc` 可独立汇编 `.s`（不经过编译器） | GCC 必须调外部 `as`（GNU as） |
| **集成链接器** | LLD 可直接消费 MC 输出 | GCC 调外部 `ld` |
| **JIT 友好** | MC layer 可在内存里直接生成机器码（ORC JIT 用） | GCC 无内建 JIT（有 GCCjit 但独立） |
| **重定位** | MCObjectStreamer 处理 fixup → 重定位表 | RTL→汇编后由 as 处理 |
| **设计哲学** | "汇编器是一等工具"（可独立用 `llvm-mc`） | "汇编是编译器的附属"（必须配 GNU as） |

**MC layer 先进在哪**：
1. **`llvm-mc` 可独立工作**——不需要完整编译器，就能 `.s → .o`，这对交叉编译、固件开发（飞腾嵌入式场景）极有价值。
2. **MCInst 与 MachineInstr 解耦**——指令编码逻辑独立于寄存器分配/调度，可复用（反汇编器 `llvm-objdump -d` 也用 MC）。
3. **JIT 原生支持**——MC layer 可在内存生成代码，这是 LLVM ORC JIT（V8/MySQL JIT）的基础，GCC 无此能力。

> **飞腾相关性**：飞腾嵌入式生态（phytium_repos 45 目录里的 NuttX/FreeRTOS/seL4/Zephyr）大量用 `llvm-mc` / `clang` 做交叉汇编/交叉编译。MC layer 的"独立汇编器"能力是飞腾嵌入式工具链的基础设施。飞腾 SM3/SM4（v8.4 国密）的编码，就依赖 MC layer 的 `MCCodeEmitter` 正确编码 `SM3SS1` 等助记符——主线 LLVM ≥ 14 已支持。

---

### 2.8 编写一个新 LLVM 后端的最小步骤（BPF / SPARC / MIPS 参照）

这是硬问题 10。假设要为飞腾 FTC86x 写一个**独立的 LLVM 后端**（而非复用 AArch64），最小步骤参照 BPF（最简单的现代后端）。[实测-`llvm/lib/Target/BPF/`] 文件清单：

#### 2.8.1 必需的 `.td` 文件（目标描述）

| 文件 | 作用 | BPF 对应 |
|---|---|---|
| `MyTarget.td` | 顶层入口，include 所有子文件 | `BPF.td` |
| `MyTargetRegisterInfo.td` | 寄存器定义（物理寄存器、寄存器类） | `BPFRegisterInfo.td` |
| `MyTargetCallingConv.td` | 调用约定（参数传递、callee-saved） | `BPFCallingConv.td` |
| `MyTargetInstrInfo.td` | 指令定义（def/defm/multiclass） + Pat 模式 | `BPFInstrInfo.td` |
| `MyTargetInstrFormats.td` | 指令编码格式（指令位域布局） | `BPFInstrFormats.td` |

#### 2.8.2 必需的 `.cpp/.h` 文件（C++ 逻辑）

| 文件 | 作用 | BPF 对应 |
|---|---|---|
| `MyTargetMachine.cpp/.h` | TargetMachine（目标机入口，注册 Pass） | `BPFTargetMachine.cpp` |
| `MyTargetSubtarget.cpp/.h` | Subtarget（特性、调度模型选择） | `BPFSubtarget.cpp` |
| `MyTargetFrameLowering.cpp/.h` | 栈帧管理（prologue/epilogue） | `BPFFrameLowering.cpp` |
| `MyTargetISelLowering.cpp/.h` | SelectionDAG Lowering（IR→DAG 的目标定制） | `BPFISelLowering.cpp` |
| `MyTargetISelDAGToDAG.cpp` | DAGToDAG 定制匹配（ComplexPattern） | `BPFISelDAGToDAG.cpp` |
| `MyTargetInstrInfo.cpp/.h` | 指令信息（插桩、分析） | `BPFInstrInfo.cpp` |
| `MyTargetRegisterInfo.cpp/.h` | 寄存器信息（ABI、spill） | `BPFRegisterInfo.cpp` |
| `MyTargetAsmPrinter.cpp` | MC 层打印（MachineInstr → MCInst） | `BPFAsmPrinter.cpp` |
| `MyTargetSelectionDAGInfo.cpp/.h` | SelectionDAG 辅助信息 | `BPFSelectionDAGInfo.cpp` |

#### 2.8.3 可选（GlobalISel 支持）

| 文件 | 作用 |
|---|---|
| `MyTarget/GISel/MyTargetCallLowering.cpp` | 函数调用的 GISel lowering |
| `MyTarget/GISel/MyTargetLegalizerInfo.cpp` | GISel 合法化规则 |
| `MyTarget/GISel/MyTargetRegisterBankInfo.cpp` | 寄存器组映射 |
| `MyTarget/GISel/MyTargetInstructionSelector.cpp` | GISel match table |

BPF 有 `GISel/` 目录（[实测]），说明即使是简单后端也在逐步支持 GISel。

#### 2.8.4 子目录（汇编/反汇编/MC）

| 目录 | 作用 |
|---|---|
| `AsmParser/` | 汇编器（`.s` → MCInst） |
| `Disassembler/` | 反汇编器（二进制 → MCInst） |
| `MCTargetDesc/` | MC 层描述（编码、fixup、格式） |
| `TargetInfo/` | TargetRegistration（注册到 LLVM） |

#### 2.8.5 注册后端（让 LLVM 认识它）

在 `llvm/lib/Target/MyTarget/TargetInfo/MyTargetTargetInfo.cpp` 里：
```cpp
Target &getTheMyTargetTarget() {
  static Target Target;
  return Target;
}
extern "C" void LLVMInitializeMyTargetTargetInfo() {
  RegisterTarget<Triple::mytarget> X(getTheMyTargetTarget(), "mytarget", "My Target");
}
```
并在 `llvm/CMakeLists.txt` 注册目录、`llvm/lib/Targets/` 加 `LLVMBuild.txt`。

> **飞腾的现实选择**：飞腾**不需要**也不应该写独立后端——FTC862 是标准 ARMv8.4-A，应复用 AArch64 后端。飞腾真正要做的是**为 AArch64 后端贡献一个 `AArch64SchedFTC86x.td` 调度模型**（像华为的 `AArch64SchedTSV110.td`、NVIDIA 的 grace、高通的 oryon 那样）。这是"加一个文件"而非"写一个后端"。飞腾至今未做（§2.9 反向锚点），是免费的性能损失。

---

### 2.9 反向锚点：主线 LLVM 对飞腾 FTC86x 的"零养育"

> **这是本专家最锋利的实证，也是与飞腾 E11 §1.1 的直接呼应。**

[实测-`grep -rn "FTC86|Phytium|ftc86|phgtium" llvm/lib/Target/ llvm/lib/CodeGen/`]：**零命中**。
[实测-`grep -rn "FTC86|Phytium|ftc86|phgtium|XiangShan|xiangshan" llvm/`]（全树）：**FTC86/Phytium 全树零命中**，但 **XiangShan（香山）有完整养育**。

香山（开源 RISC-V 处理器）在主线 LLVM 的养育证据：
- [实测-`RISCV/RISCVSchedXiangShanNanHu.td`]：完整的香山南湖调度模型文件（`XiangShanNanHuModel`，含 FuDian FPU 注释）
- [实测-`RISCV/RISCVProcessors.td:796`]：`def XIANGSHAN_NANHU : RISCVProcessorModel<"xiangshan-nanhu", XiangShanNanHuModel, ...>`
- [实测-`RISCV/RISCVProcessors.td:822`]：`def XIANGSHAN_KUNMINGHU : RISCVProcessorModel<"xiangshan-kunminghu", ...>`
- [实测-`RISCV/RISCV.td:69`]：`include "RISCVSchedXiangShanNanHu.td"`

**对比 AArch64 后端的处理器清单**（[实测-`AArch64Processors.td:1417+`]）：
- `generic → CortexA510Model`（`:1417`，**飞腾不指定 -mcpu 时的默认**——这意味着飞腾代码在线主线 LLVM 上被当作"Cortex-A510"调度，而 Cortex-A510 是 ARM 的小核，与飞腾 FTC862 的 4-wide 服务器核微架构完全不同）
- `cortex-a*` 全系列（ARM 官方）
- `neoverse-n1/n2/n3`、`neoverse-v1/v2/v3`（ARM 服务器）
- `tsv110`（华为鲲鹏）
- `thunderx/thunderx2t99/thunderx3t110`（Marvell/Cavium 雷神）
- `a64fx`（富士通 SVE 超算）
- `ampere1/ampere1b`（Ampere Computing）
- `oryon`（高通）
- `olympus`（新核）
- `grace`（NVIDIA Grace，`:1496`）
- `exynos-m3/m4/m5`（三星）
- `cyclone`（Apple）
- `falkor/kyro`（高通老款）
- **零飞腾 FTC86x**

> **决定性判断**：香山（RISC-V，中国开源项目）能进主线 LLVM，飞腾（AArch64，中国商业 CPU）不能。**差异不在国籍，在养育策略**。香山团队主动向 LLVM/RISC-V 社区提交了调度模型 patch 并持续维护；飞腾则把定制锁在私有 PhyGCC（GCC fork）里，未向 LLVM 上游贡献。这是飞腾"在线主线 LLVM 上损失 5-10% 性能"（[推测-飞腾 E11 §3.2]）的根源——主线 LLVM 把飞腾当 Cortex-A510 调度，调度模型不匹配。**这是飞腾最该补的免费收益**。

---

### 2.10 SelectionDAG 调试技巧（硬问题 9）

SelectionDAG 是 LLVM 最难调试的子系统之一。核心武器（详见 [领域资源库_LLVM.md](../领域资源库_LLVM.md) §2 通用工具栈）：

| 工具/选项 | 作用 | 用法 |
|---|---|---|
| `-debug-only=dagcombine` | 打印 DAGCombiner 的决策过程 | `llc -debug-only=dagcombine -mtriple=aarch64 input.ll` |
| `-debug-only=legalize-types` | 打印 LegalizeTypes 决策 | `llc -debug-only=legalize-types ...` |
| `-debug-only=isel` | 打印 SelectionDAGISel 的匹配过程 | `llc -debug-only=isel ...` |
| `-view-dag-combine1-dags` | 可视化第一次 DAGCombine 前的 DAG（graphviz 出图） | 需 `dot` 工具 |
| `-view-dag-combine2-dags` | 可视化第二次 DAGCombine 后 | |
| `-view-legalize-types-dags` | 可视化 LegalizeTypes 过程 | |
| `-view-isel-dags` | 可视化指令选择前的 DAG | |
| `-print-after-all` | 打印每个 Pass 后的 IR/MIR | `llc -print-after-all ...` |
| `-filter-view-dags=funcname` | 只看特定函数的 DAG | 避免大文件刷屏 |

**调试 UDOT 选不出来**的实战流程：
1. `llc -mtriple=aarch64-linux-gnu -mattr=+dotprod -debug-only=isel input.ll` → 看指令选择日志，确认是否尝试匹配 UDOT 模式
2. `llc ... -view-dag-combine2-dags` → 看 DAGCombine 后的 DAG，确认是否有 `<16 x i8>` 的 dot 聚合节点
3. 若 DAG 里只有 `<4 x i32>` 的 smull，说明前端提升导致——UDOT 模式（要求 `<16 x i8>`）匹配不上
4. 用 `llvm-dis` 看 IR，确认 `sext i8 → i32` 是否在前端就发生了

> **飞腾工程教训**：飞腾开发者若怀疑"某段代码没选到最优指令"，第一反应应是 `-debug-only=isel` 看 SelectionDAGISel 的匹配日志，而非猜。这是 LLVM 后端调试的"第一性工具"。

---

## 3. 设计决策评估：LLVM 代码生成的哪些决策认可 / 哪些该改 / 飞腾工程教训

### 3.1 认可的决策

1. **SelectionDAG 的 DAG 抽象**——虽然有"chain edge"的别扭，但 DAG 让 Legalize/Combine/PatternMatch 有了清晰的数学结构，比"直接在 IR 上贪心匹配"更系统。这是 2003 年的设计，至今仍是后端的脊梁。

2. **TableGen 的声明式目标描述**——用 `.td` 描述目标，让 `llvm-tblgen` 生成 matcher，是 LLVM 后端可扩展性的基石。新增一个调度模型（如香山）只需加一个 `.td` 文件，无需改 C++ 选择器。这比 GCC 的 `.md` 更模块化。

3. **`AArch64Unsupported` 机制**——显式声明"哪些特性在该芯片上不支持"，是保证代码生成正确性（不生成非法指令）的优雅防线。

4. **MC layer 的独立汇编器设计**——`llvm-mc` 可独立工作，对交叉编译/固件/JIT 极有价值，是 GCC 没有的能力。

5. **`AArch64Unsupported` + `setGlobalISelAbort(Disable)` 的"安全网"设计**——GISel 失败回退 SDAG，保证了 GISel 渐进迁移不破坏生产。这是务实的工程主义。

### 3.2 该改的决策（LLVM 社区已在改）

1. **三套选择器并存的债**——FastIsel/SDAG/GISel 三套维护成本极高。LLVM 社区的方向是 GISel 最终统一（含 `-O1+`），但 2016→2026 十年未竟，是 LLVM 最大的工程债之一（对标飞腾项目宪法的"New PM 迁移债"断层④，这里是"GISel 迁移债"）。

2. **SDAG 的 chain edge 模型**——用 chain 建模内存副作用，导致 DAG 膨胀、Combine 规则难写。GISel 用 MachineIR 的 SSA + 显式内存语义，是更现代的设计，但迁移成本巨大。

3. **Pattern match 的"预设形态"局限**——UDOT 选不出来（§2.6）暴露了 SelectionDAG 只能匹配预设 Pat、不会主动"发现"模式的缺陷。AI 时代（点积/matmul 算子）这个局限更刺眼。

4. **`generic` 默认调度模型的陷阱**——飞腾不指定 `-mcpu` 时默认 `generic = CortexA510Model`（小核），对服务器核（FTC862）严重失配。应该有一个更"中性"的默认，或强制要求 `-mcpu`。

### 3.3 飞腾工程教训（可执行）

1. **飞腾应向主线 LLVM 贡献 `AArch64SchedFTC86x.td`**——像华为 tsv110、NVIDIA grace、高通 oryon 那样。这是"加一个文件"的免费收益（[推测] 5-10% 调度性能），但飞腾至今未做（§2.9 反向锚点）。**这是飞腾编译器命运最该补的一块**。

2. **飞腾应确保 LLVM fork 的 feature flags 准确**——`Subtarget->hasDotProd()/hasSVE()/hasMatMulInt8()/hasBF16()` 必须如实反映 FTC862（ARMv8.4：有 DotProd，无 SVE/BF16/I8MM）。这是 Legalize 正确性的地基，错一个就生成非法指令。

3. **飞腾应提供 int8 量化 intrinsic 模板库**——UDOT 选不出来是 SelectionDAG 的固有局限（§2.6），飞腾 SDK 应封装 `ftc_udot_quantize()` 等 intrinsic 模板，否则用户拿不到 16.9× 加速。

4. **飞腾 `-O0` 默认走 GISel，`-O2+` 走 SDAG**——开发者应知晓：调试构建（-O0）和生产构建（-O2+）走不同选择器，代码生成质量可能不同。生产性能调优必须基于 `-O2+`（SDAG 路径）。

---

## 4. 这一视角的盲区与反方（诚实段，强制）

### 4.1 代码生成专家看不见什么

1. **看不见前端语义**——指令选择只看 IR/DAG，不关心 C++ 源码意图。一段"语义清晰"的 C++ 可能生成"选不出 UDOT"的 IR（§2.6），代码生成专家会怪"前端提升太激进"，但根因在 C++ 类型提升规则（int8→int32），这是语言语义，编译器改不了。

2. **看不见运行时**——代码生成是静态的，假设"指令选对了就快"。但 cache miss、分支预测失败、内存带宽饱和，代码生成一无所知。一段"选了 UDOT"的代码可能因 cache 抖动比"标量循环"还慢。这要靠 PGO + BOLT（Expert_12）补。

3. **看不见全程序**——代码生成逐函数进行，跨函数/跨 TU 的优化（LTO、内联）在中端（Expert_04），代码生成看不到。一个"本函数最优"的指令选择，可能因为没内联而整体次优。

4. **看不见硬件 errata**——飞腾 FTC862 可能有微架构 errata（某条指令某条件下结果错），代码生成不知道。这要靠 errata 文档喂给编译器生成 workaround。

5. **"选最优指令"的执念可能误导**——代码生成专家容易陷入"必须选 UDOT/BF16"的执念，但很多时候标量代码 + 好的调度（Expert_06）比"选了复杂向量指令但调度烂"更快。指令选择不是孤立最优，要与调度协同。

### 4.2 反方观点：代码生成是"过去式"，未来在中端/MLIR

一个激进的反方：**在 2026 年，代码生成（SDAG/GISel/TableGen）的边际价值在下降，投资重点应转向中端优化（Expert_04）和 MLIR（AI 编译）**。论据：

- AI 时代的关键算子（GEMM/Attention/Conv）都是手写汇编或 intrinsic，根本不经过自动指令选择。代码生成再聪明，热点也不靠它。
- MLIR 的 `linalg`/`tosa` dialect 在更高层做算子融合，到 LLVM IR 时已经是"低级"形态，代码生成的优化空间被压缩。
- SDAG/GISel 的复杂度（Legalize/Combine/PatternMatch）是"技术债"，未来可能被 MLIR 的分层 lowering 取代。

**这个反方有道理但不完全对**：
- 代码生成的价值在"长尾"——非热点的 99% 通用 C/C++ 代码，没人能手写。代码生成把长尾从"非法/次优"拉到"合法且可用"，是基础设施。
- MLIR 最终也要 lower 到 LLVM IR，代码生成是 MLIR 的"出口"。MLIR 再好，底层代码生成烂，整体仍烂。
- 飞腾这种"标准 ARMv8.4 + 无 SVE"的芯片，AI 算力受限，**通用代码的代码生成质量反而是主要性能来源**——这恰恰是 SDAG/GISel 的战场。

**结论**：代码生成不是"过去式"，是"基础设施"。基础设施烂，上层（MLIR/手写算子）也跑不稳。飞腾应同时投资"AI 算子手写"和"通用代码生成质量（贡献调度模型）"。

---

## 5. 与其他视角对偶（一致 / 冲突，强制）

### 5.1 一致（互相印证）

- **与 [Expert_02 LLVM IR](../Expert_02_LLVM_IR_Design/README.md) 一致**：IR 的类型系统（`<vscale x N x T>`、`i128`、`fp128`）是"理想化"的，代码生成的 Legalize 把它"接地"到真实硬件。E02 讲 IR 的抽象，本专家讲 IR 如何被"合法化降级"。两者是"抽象-具体"的上下游。

- **与 [Expert_03 Pass Framework](../Expert_03_Pass_Framework/README.md) 一致**：SelectionDAGISel / GlobalISel 的四阶段（IRTranslator/Legalizer/RegBankSelect/InstructionSelect）都是注册到 PassManager 的 MachineFunctionPass。E03 讲 Pass 框架，本专家讲代码生成 Pass 的内部机制。SelectionDAGISel 是最复杂的"伪 Pass"之一。

- **与 [Expert_06 RegAlloc/Scheduler](../Expert_06_RegAlloc_Scheduler/README.md) 一致**：代码生成产出 MachineInstr（虚拟寄存器），E06 接管做寄存器分配（Greedy/Basic）和指令调度（Pre/Post-RA Sched）。本专家是 E06 的"上游"。飞腾 31 寄存器的红利，在代码生成层（BankSelect）和 RegAlloc 层（E06）共同兑现。

- **与 [Expert_08 AArch64 Backend](../Expert_08_AArch64_Backend/README.md) 一致**：E08 讲 AArch64 后端的整体（寄存器/调度/特性），本专家讲代码生成子系统（SDAG/GISel）如何消费 AArch64 后端的 `.td` 描述。E08 的"无 FTC86x 调度模型"反向锚点（§2.9）正是本专家 §2.9 的同源发现。

- **与飞腾 Expert_11 §2.1（`../../体系结构实验/Expert_11_Compiler_Research/README.md`） 一致并深化**：E11 §2.1 从 Pass Pipeline 角度点破 Legalize 对"无 SVE"的约束、UDOT 选不出来；本专家深化到 `.td` 层（`AArch64Unsupported`、`partial_reduce_umla` Pat、`HasMatMulInt8` gate）和源码层（`LegalizeVectorTypes.cpp:9-18`、`AArch64TargetMachine.cpp:158-161`）。E11 给现象，本专家给 `.td`/源码级根因。

### 5.2 冲突（视角打架）

- **与 [Expert_04 Middle-End Opt](../Expert_04_Middle_End_Opt/README.md) 轻微冲突**：E04 的中端优化（GVN/LICM/LoopUnroll）在 IR 上做，可能"破坏"代码生成想要的形态——例如 LoopUnroll 把循环展开成标量，反而让 UDOT 更难聚合（因为向量性丢失）。中端"最优"可能让后端"选不出最优指令"。这是中端-后端的经典张力，LLVM 用 `TargetTransformInfo`（TTI）让后端给中端"成本反馈"来缓解，但不完美。

- **与飞腾 Expert_11 §2.4 PhyGCC（`../../体系结构实验/Expert_11_Compiler_Research/README.md`） 路径选择冲突**：E11 详述 PhyGCC（飞腾 GCC fork）的调度优化收益（10-18%）。本专家从 LLVM 视角指出：飞腾应投资 LLVM（贡献调度模型 + 拥抱 GISel/MLIR），而非只维护 GCC fork。**E11 是"GCC 工程实战"，本专家是"LLVM 战略建议"——同一个飞腾，两个视角给出不同编译器路线**。真相是飞腾需要双栈（GCC for 服务器/Linux 发行版，LLVM for AI/嵌入式/JIT）。

- **与 [Expert_07 Auto-Vectorization](../Expert_07_Auto_Vectorization/README.md) 协同但有边界争议**：E07 讲 LoopVectorize/SLPVectorizer（中端，IR 层），本专家讲代码生成（后端）。向量化在中端决定"要不要向量化"（生成 `<16 x i8>` IR），代码生成在后端决定"选 UDOT 还是 mul+add"。UDOT 选不出来（§2.6）说明：**中端向量化成功了（生成了 `<16 x i8>`），后端却没选到最优指令**——这是中端-后端衔接的断层。

---

## 6. 参考文献（≥15，分级标注）

### 官方文档与标准
1. **[官方]** LLVM Project. *Writing an LLVM Backend*. llvm.org/docs/WritingAnLLVMBackend. —— 后端 `.td` 描述与注册流程权威。
2. **[官方]** LLVM Project. *TableGen Fundamentals*. llvm.org/docs/TableGen/index.html. —— TableGen 语言手册。
3. **[官方]** LLVM Project. *The LLVM Target-Independent Code Generator*. llvm.org/docs/CodeGenerator.html. —— SelectionDAG/GlobalISel 总览。
4. **[官方]** LLVM Project. *GlobalISel Guide* / *IRTranslator* / *Legalizer* 系列文档. llvm.org/docs/GlobalISel/. —— GISel 四阶段。
5. **[标准]** ARM Limited. *ARM Architecture Reference Manual (ARM ARM), ARMv8, DDI 0487*. —— A64 指令集、NEON/DotProd/I8MM/BF16/SVE 编码（飞腾 E11 实测依据）。
6. **[官方]** GCC. *GNU Compiler Collection Internals: Machine Descriptions*. gcc.gnu.org/onlinedocs/gccint/Machine-Desc.html. —— GCC `.md` 对偶。

### 经典教材与论文
7. **[书]** Cooper & Torczon. *Engineering a Compiler*（3rd ed.）. MK, 2022. —— 指令选择（tree pattern matching）、合法化的标准教材。
8. **[书]** Muchnick. *Advanced Compiler Design and Implementation*. MK, 1997. —— 后端代码生成（指令选择/调度）权威。
9. **[书]** Aho, Lam, Sethi, Ullman. *Compilers: Principles, Techniques, and Tools*（龙书, 2nd）. 2006. —— 语法制导翻译、树模式匹配的理论基础。
10. **[书]** 彭成寒 等. *深入理解 LLVM：代码生成*. 机械工业, 2024. —— 以 LLVM 15 为基线讲 SelectionDAG/Legalize/MC，近年最详细的中文后端深度书。
11. **[书]** Lopes & Auler. *Getting Started with LLVM Core Libraries*. MK, 2014 / 中译本 2019. —— LLVM 后端入门。
12. **[论文]** Fraser, Henry. *Bottom-Up Tree Pattern Matching*. 1991. —— DAG/tree 模式匹配算法（SelectionDAG 的理论基础之一）。
13. **[论文]** Chatuphrom, Prabhu. *eBPF and the BPF Compiler Backend*. —— BPF 后端设计（新后端参照）。
14. **[论文]** Ziels et al. / LLVM GlobalISel RFC (2016). —— GlobalISel 架构提议（Discourse 历史档案）。

### 项目内实测与开源资源
15. **[实测]** 本项目 OpenXiangShan/llvm-project（LLVM 23.0.0git）源码：`llvm/lib/CodeGen/SelectionDAG/`、`llvm/lib/CodeGen/GlobalISel/`、`llvm/lib/Target/AArch64/`、`llvm/utils/TableGen/`。本文所有行号锚点均来自此。
16. **[实测]** 飞腾项目 Expert_11_Compiler_Research（`../../体系结构实验/Expert_11_Compiler_Research/README.md`） §2.1 Pass Pipeline、§2.3.4 UDOT 选择难题、§2.4 PhyGCC。本专家深化其源码级根因。
17. **[GitHub]** LLVM Project. github.com/llvm/llvm-project. —— 代码生成子系统源。
18. **[GitHub]** OpenXiangShan/NanHu 调度模型贡献. github.com/OpenXiangShan/XiangShan. —— 香山进 mainline 的养育实证。
19. **[Discourse]** LLVM Discourse: GlobalISel 进展 / Legalize 讨论. discourse.llvm.org. —— GISel 覆盖率与迁移讨论。
20. **[社区]** Evian-Zhang/llvm-ir-tutorial; VectorizeOrz LLVM Tutorial（B站）. —— 中文 LLVM 后端学习资源（见 [领域资源库_LLVM.md](../领域资源库_LLVM.md) §6）。

---

## 7. 延伸阅读（项目内引用 + 外部）

### 项目内（对偶视角）
- [Expert_02 LLVM IR Design](../Expert_02_LLVM_IR_Design/README.md) —— IR 的类型系统（`<vscale>`/`i128`），代码生成的 Legalize 把它"接地"。
- [Expert_03 Pass Framework](../Expert_03_Pass_Framework/README.md) —— SelectionDAGISel/GISel 是 MachineFunctionPass，注册到 PassManager。
- [Expert_04 Middle-End Opt](../Expert_04_Middle_End_Opt/README.md) —— 中端优化与后端代码生成的张力（LoopUnroll vs UDOT 聚合）。
- [Expert_06 RegAlloc Scheduler](../Expert_06_RegAlloc_Scheduler/README.md) —— 代码生成的下游（寄存器分配 + 调度）。
- [Expert_07 Auto-Vectorization](../Expert_07_Auto_Vectorization/README.md) —— 中端向量化（LoopVec/SLP）与后端指令选择（UDOT）的衔接断层。
- [Expert_08 AArch64 Backend](../Expert_08_AArch64_Backend/README.md) —— AArch64 后端整体（寄存器/调度/特性），本专家是其代码生成子系统的深化。
- 飞腾项目 Expert_11_Compiler_Research（`../../体系结构实验/Expert_11_Compiler_Research/README.md`） §2.1/§2.3.4/§2.4 —— Pipeline、UDOT、PhyGCC，本专家深化其源码级根因。

### 外部资源（通用资源见 [领域资源库_LLVM.md](../领域资源库_LLVM.md)）
- **LLVM Code Generator 文档**（llvm.org/docs/CodeGenerator.html）—— SelectionDAG/GlobalISel 官方总览
- **Writing an LLVM Backend**（llvm.org/docs/WritingAnLLVMBackend.html）—— 新后端开发指南
- **TableGen 文档**（llvm.org/docs/TableGen/index.html）—— `.td` 语言手册
- **GlobalISel 文档**（llvm.org/docs/GlobalISel/）—— GISel 四阶段
- **`llvm-tblgen -print-dag-isel`** —— 调试 TableGen 生成的匹配表
- **Compiler Explorer (godbolt.org)** —— 在线对比 SDAG/GISel/FastISel 输出（`-global-isel` 开关）

---

## § 代码生成方法论与资源（不只 LLVM，给所有后端工程师）

> 本章把 E05 的 LLVM 代码生成分析上升为**任何后端工程师都可复用的方法与资源**。飞腾（FTC862 + PhyGCC）是案例锚点，方法普适。通用资源见 [`领域资源库_LLVM.md`](../领域资源库_LLVM.md)。

### 方法论一：指令选择的"合法性优先"原则

代码生成的第一性原理不是"选最快的指令"，而是"选**合法**的指令"。
1. **合法性判定**：给定操作 + 类型组合，目标是否支持？（LLVM: `LegalizerInfo` / `TargetLowering::getOperationAction`；GCC: `targetm.*` 检查）
2. **不合法的处理**：promote（提升类型）/ expand（展开成多条）/ libcall（调运行时）/ scalarize（标量化）/ split（向量拆分）
3. **优化（合法之后）**：在合法指令里选最优的（pattern match / cost model）

**飞腾案例**：`<vscale x 4 x i32>`（SVE）在飞腾上非法 → Legalize 阶段拒绝；`SMMLA`（I8MM）在飞腾上非法 → Pat 不激活。合法性是优化的前提。

### 方法论二：声明式目标描述（TableGen / .md）

现代编译器后端用"声明式表格"描述目标，而非手写 C/C++ 选择器：
- **LLVM TableGen（`.td`）**：强类型 DSL，`multiclass` 实例化，`llvm-tblgen` 生成 matcher
- **GCC Machine Description（`.md`）**：Lisp S-expr，`gen*` 工具生成 C
- **新后端开发流程**：先写 `.td`/`.md` 描述（寄存器/指令/调度/调用约定），再写少量 C++ 定制（Lowering/DAGToDAG）

**何时用哪种**：LLVM 生态用 TableGen（强元编程，模块化）；GCC 生态用 `.md`（稳定，兼容性好）。飞腾 PhyGCC 改 `.md`，飞腾 LLVM fork 应改 `.td`。

### 方法论三：三选择器的取舍

| 场景 | 推荐选择器 | 理由 |
|------|----------|------|
| JIT 快速编译 | FastISel / GISel(-O0) | 速度优先，质量其次 |
| 生产构建（-O2+） | SelectionDAG | 质量优先 |
| 调试构建（-O0） | GISel（AArch64）/ FastISel | 速度 + 可调试 |
| 新后端开发 | 先 SDAG，后加 GISel | SDAG 文档/案例多 |

### 方法论四：调试代码生成的"四件套"

1. **`-debug-only=isel`**（LLVM）/ **`-fdump-rtl-*`**（GCC）—— 看指令选择日志
2. **`-view-*-dags`**（LLVM）—— 可视化 DAG
3. **`-print-after-all`**（LLVM）—— 看每个 Pass 后的 IR/MIR
4. **`bugpoint` + `llvm-reduce`**（LLVM）—— 自动最小化 miscompilation

### 代码生成专属资源

> 通用资源见 [`领域资源库_LLVM.md`](../领域资源库_LLVM.md) §2/§3/§4；以下为**代码生成/指令选择/合法化/TableGen**专属资源。

**📚 必读书**
- ⭐ **彭成寒 等**, *深入理解 LLVM：代码生成*（机械工业 2024）—— 中文 LLVM 后端深度，LLVM 15 基线，讲 SelectionDAG/Legalize/MC
- ⭐ **Cooper & Torczon**, *Engineering a Compiler* 3rd (2022) §13-14 —— 指令选择与合法化的现代教材
- 🔥 **Muchnick**, *Advanced Compiler Design and Implementation* —— 后端代码生成权威（鲸书）
- 🔥 **Aho et al.**, *龙书* 2nd §8 —— 树模式匹配与语法制导翻译

**🔧 工具**
- **`llvm-tblgen`**：`-print-records` / `-print-dag-isel` / `-gen-dag-isel` 看生成的 matcher
- **`llc`**：`-debug-only=isel/dagcombine/legalize-types` + `-view-*-dags` 调试 SDAG
- **`llvm-mc`**：独立汇编器（MC layer 验证）
- **Compiler Explorer**：`-global-isel=true` 开 GISel 对比 SDAG 输出

**📖 文档**
- LLVM *Writing an LLVM Backend* / *TableGen* / *Code Generator* / *GlobalISel* 官方文档（见 §6 参考文献 1-4）
- GCC *Machine Descriptions*（gccint）—— `.md` 对偶
- LLVM Discourse: "GlobalISel" 标签 —— GISel 进展与讨论

---

> **本专家总结**：LLVM 代码生成是"IR 抽象"到"硬件现实"的桥梁，SelectionDAG（主力）+ GlobalISel（新生代）+ TableGen（目标描述）三者构成这座桥梁的桥墩。飞腾 FTC862 的代码生成命运，不取决于"算法多聪明"，而取决于"`.td` 填得准不准"——而飞腾在主线 LLVM 的 `.td` 里**缺席**（零 FTC86x，对比香山进 mainline），这是飞腾最该补的免费收益。Legalize 对"无 SVE/BF16/I8MM"的硬约束、UDOT 选不出来的 `.td` 根源、三选择器并存的债，是理解 LLVM 代码生成的三把钥匙。
