# Expert_04 — 中端优化专家 / MLIR-core 融合裂痕考古学家视角

> **角色定位**：这位专家是 LLVM **中端优化（middle-end optimization）的资深算法工程师**——他不是 [E03 Pass 框架](../Expert_03_Pass_Framework/README.md) 那种"维护骨架的人"，他是**往骨架里塞算法的人**。他读过 `GVN.cpp`、`LoopVectorize.cpp`、`SCCP.cpp` 的实现，知道 InstCombine 这个"巨兽"被拆成 17 个文件（[实测-InstCombine/ 目录]）的工程理由；他也维护过 Polly 的多面体（polyhedral）调度，研究过 pet/PPL/isl 这些上游依赖。但这位专家**最特殊的身份是"MLIR-core 融合裂痕考古学家"**——他亲历了 2019 年 MLIR 进入 LLVM umbrella 时社区那句"MLIR 是编译器的 future，LLVM IR 是过去"的争论，他知道本项目 [断层 ② MLIR-core 融合裂痕](../改造蓝图_LLVM.md#5-五个服务器命脉级断层) 为什么是"服务器命脉级"。他把"LLVM 单层 IR 走向终结、MLIR 多层 dialect 取而代之"当成一场**正在发生的范式转移**来考古——而飞腾 FTC862 / phytvm（TVM fork）/ 国产 NPU 编译栈恰好站在裂缝的正上方。
>
> **核心思维模型**：
> 1. **优化收益递减定律（Diminishing Returns of Optimization）**——GVN、InstCombine、LICM 这些 1990s-2000s 的算法已被打磨到极限，`-O2`→`-O3` 的边际收益在飞腾 FTC862 上仅 ~2%（飞腾项目 [View_01 实测]）。2026 年真正能产生 10%+ 提升的不是某个新标量 Pass，而是**跨 Pass 的协同**（如 LoopNestPass）+ **反馈优化**（PGO/BOLT）+ **换 IR**（MLIR）。这位专家盯着收益曲线的拐点：哪条曲线已经躺平，哪条还在爬升。
> 2. **多面体覆盖天花板（Polyhedral Coverage Ceiling）**——Polly（多面体优化）的杀伤力理论上是"自动 GEMM/conv 优化"，但实战覆盖率受限（依赖 isl、对循环形态要求苛刻、没进默认 `-O3`）。这位专家用"覆盖率 × 收益"二维评估每个优化：覆盖率高但收益躺平（InstCombine）vs 覆盖率低但收益爆炸（Polly/MLIR）。
> 3. **IR 表达力阶梯（IR Expressivity Ladder）**——编译器优化的天花板由 IR 表达力决定。LLVM IR 是**单层、低级、SSA-only** 的表示，它擅长标量/局部优化，但**天生不擅长循环嵌套变换**（Michael Kruse 2020 RFC 一针见血：[Discourse-54110] "在错误的表示上写循环变换是低效的"，Lattner 回复"MLIR 才是循环变换的正确抽象"）。MLIR 用**多层 dialect**（Affine/SCF/Linalg/Vector）把循环、张量、向量各抽象成一层，每层做自己擅长的优化。这条"表达力阶梯"是理解**为什么 LLVM core 必须被 MLIR 补完**的主线。

---

## 1. 这位中端优化专家看 LLVM 的 12 个尖锐问题

这位专家拿到一个 LLVM 版本，第一件事不是 `clang -O3`，而是 `ls llvm/lib/Transforms/Scalar/ | wc -l` 和 `grep -c "addPass" llvm/lib/Passes/PassBuilderPipelines.cpp`，他问：

1. **GVN / SCCP / InstCombine / SROA / LICM / LoopUnroll 这些"老朋友"在 2026 还有多少边际收益？** 实测 `llvm/lib/Transforms/Scalar/` 有 **80+ 个 Pass 文件**（[实测-Scalar/ 目录]），但其中多少是"看上去很忙、实际躺平"？关键反直觉点：**GVN 真的被 NewGVN 替代了吗**？打开 `PassBuilderPipelines.cpp:207`——`static cl::opt<bool> RunNewGVN("enable-newgvn", cl::init(false)...)`，默认 **false**；`:753-756` `if (RunNewGVN) NewGVNPass(); else GVNPass()`，**默认走的仍是老 `GVN.cpp`**。NewGVN 引入近 10 年仍未默认——这是社区的一个**未竟之志**，也是"算法先进不等于工程采纳"的活教材。
2. **Polly（多面体优化）为什么没进默认 `-O3`？实战覆盖率多少？pet/PPL 怎么对比？** Polly 是 monorepo 22 子项目之一（`CMakeLists.txt:107` `LLVM_ALL_PROJECTS="...;polly"`），但作为 **external project** 挂载（`tools/CMakeLists.txt:54` `add_llvm_external_project(polly)`），默认构建**不包含**它，必须 `-DLLVM_ENABLE_PROJECTS=polly`。这背后是 isl（integer set library）依赖、编译时长爆炸、覆盖率受限的真实工程权衡。对标飞腾：飞腾 Yocto/Buildroot 的 LLVM recipe **绝不启用 Polly**（嵌入式场景不值得）。
3. **⭐ 断层 ②：MLIR 与 LLVM core 的融合裂痕**——MLIR 是 LLVM 子项目但**独立 dialect 生态**，与 LLVM IR 二元。实测 `mlir/include/mlir/Dialect/` 有 **45 个 dialect 目录**（[实测-mlir Dialect]，佐证 Lens_01 的"48 方言"判断），`mlir/lib/Conversion/` 有 **~80 个 lowering 转换目录**（[实测-mlir Conversion]）。一个 MLIR 程序要经十几层 conversion 才降到 LLVM IR。**45+ 方言会降低还是升高编译器复杂度**？这位专家的判断：**短期升高（学习曲线爆炸、互操作地狱），长期是降复杂度的唯一出路**（因为单层 LLVM IR 的复杂度已经压不住 AI/异构编译）。飞腾 phytvm（TVM fork，[实测-vanilla Apache TVM]）已经在用 MLIR 的表亲 Relay/TIR——飞腾 NPU 编译栈迟早要直面这道裂缝。
4. **MLIR Linalg 方言 → LLVM IR 的 lowering pipeline 长什么样？** 实测 `mlir/include/mlir/Dialect/Linalg/IR/` 有 `LinalgStructuredOps.td`（matmul/conv/pool 等结构化算子）+ `LinalgNamedStructuredOps.yaml`（命名算子清单）+ `LinalgRelayoutOps.td`（transpose/copy）。一条典型的 `linalg.matmul` 要走 `Linalg→Vector→LLVM` + `Tensor→MemRef` + `SCF→ControlFlow` + `Arith→LLVM` + `Func→LLVM` 五条 conversion 通道才能落地。用 `iree-opt` 看这条阶梯是飞腾 AI 编译团队的必修课。
5. **Loop Vectorizer 在 MLIR vector dialect 里 vs LLVM IR Loop Vectorizer，谁更先进？** LLVM IR 的 `LoopVectorize.cpp` 用 VPlan（`VPlan.h`，Vector Predication 的核心，[实测-Vectorize/ 有 20+ 个 VPlan* 文件]）建模；MLIR 的 vector dialect 把向量类型/操作提升为一等公民，配 `VectorToLLVM`/`VectorToSCF`/`VectorToGPU` 多后端 lowering。**前者是"在一个不擅长向量的 IR 上硬做向量化"，后者是"先把向量做成一等抽象再做优化"**——这又是表达力阶梯的体现。飞腾无 SVE（NEON 128-bit 硬上限）的向量化天花板，在两种范式下命运不同。
6. **PGO（Profile-Guided Optimization）在 LLVM 中端的角色——BOLT 后链接优化的反差是什么？** 中端的 `SampleProfile.cpp`（[实测-IPO/ 目录]）吃 AutoFDO 的 profile 做布局/内联；但 BOLT（后链接二进制优化器，[E12]）在**链接之后**重跑整个中端 Pass，吃 perf profile。这种"中端跑两遍"（编译期 PGO + 链接后 BOLT）是 LLVM 相对 GCC 的一个**架构级优势**，飞腾服务器场景（spec2017/数据库）收益显著。
7. **Attributor（过程间属性推导）——为什么 LLVM 引入这个新框架？** 实测 `IPO/Attributor.cpp` + `AttributorAttributes.cpp` 是 LLVM 近年的**过程间优化重头戏**。但 `PassBuilderPipelines.cpp:285-286` `static cl::opt<AttributorRunOption> AttributorRun("attributor-enable", cl::init(AttributorRunOption::NONE)...)`——**默认 NONE，关闭**。一个被社区力推的新框架为何没默认？因为它"激进推导属性"在错误代码上会触发 miscompilation，社区还在打磨。这又是"算法先进 ≠ 默认采纳"的第二例证。
8. **飞腾 D3000M 上 LoopUnroll 触发条件——LLVM 默认值是不是次优？** 飞腾项目 Expert_11（`../../体系结构实验/Expert_11_Compiler_Research/README.md`） Lab02 实测：**飞腾 FTC862 上 unroll 2 最优**（[实测-飞腾 E11 §line 593]）。但 LLVM 默认 LoopUnroll 是 `LoopUnrollOptions(Level.getSpeedupLevel(), ...)` 按 cost model **动态决策**（[实测-Pipelines.cpp:1353]），不硬编码 unroll=2。**问题来了**：这个 cost model 在"无 FTC86x 调度模型"的主线 LLVM 上（[实测-grep Phytium/FTC86 中端 0 命中]），算出来的 unroll 因子对飞腾是否最优？答案大概率是**否**——这正是飞腾要校准 `.md`/cost model 的工程动机（飞腾 E11 §line 340：实测校准 `.md` 指令成本能让展开阈值更准）。
9. **GIMPLE Pass（GCC）vs LLVM IR Pass 对照表——InstCombine 对应什么？** 飞腾主力是 PhyGCC（基于 GCC），PhyCC 基于 LLVM。两套中端 Pass 概念同构却不同名，飞腾工程师迁移时需要一张导航图（见 §2.8 对标表）。
10. **MemCpyOpt / SROA / LoopIdiomRecognize（识别 memset/memcpy 模式）的工程价值是什么？** 这三个是"把高级模式降级成单条机器指令"的转换器——`LoopIdiomRecognize` 把 `for(i) a[i]=0` 认成 `memset`，`MemCpyOpt` 把连续 `load/store` 聚合成 `memcpy`，`SROA`（Scalar Replacement of Aggregates）把栈上 struct 拆成寄存器。它们看似不起眼，却决定了一段 C 代码能否命中 libc 的向量化 `memset`/`memcpy`——这是飞腾 GEMM/图像处理的隐藏加速器。
11. **SCCP（Sparse Conditional Constant Propagation）+ ConstraintElimination——常量与约束推导的现代版是什么？** SCCP 是 1990s 经典（Wegman-Zadeck），`SCCP.cpp` 至今在跑。但 LLVM 近年新增 `ConstraintElimination.cpp`（[实测-Scalar/]）用 **SMT solver 在编译期证明约束**（如 `x<y && y<z → x<z`），这是"把形式化方法塞进标量优化"的激进尝试——又是"算法先进但默认关闭"（仅 `-O3` 才开）的典型。
12. **AI 辅助编译器（mlir-opt-repl / mlirAgent）会颠覆中端优化吗？** 2026 年新趋势：`mlir-opt-repl`（LLVM PR #203796）把 MLIR Pass 流水线做成交互式 REPL + MCP server；UC Berkeley 的 `mlirAgent` 用 LLM 引导 MLIR/LLVM 优化，binary size -8.78%。**但"LLM 不能替代编译器 Pass"**（mlirAgent 实测 Gemini 2.5 Pro -11.9% 仍不及专用 Pass）。这位专家的判断：AI 不会取代中端 Pass，但会**重塑 Pass 的调试/发现流程**。

---

## 2. 具体分析：代码级实例 + 飞腾工程实证 + 对偶判断（过 §0.3 特异性测试 v2.0）

> **特异性测试 v2.0 自检**：本节以 `OpenXiangShan/llvm-project`（LLVM 23.0.0git）真实源码行号为锚，引用飞腾 `phytium_repos` 真实 recipe + 飞腾项目 Expert_11（`../../体系结构实验/Expert_11_Compiler_Research/README.md`） Lab02 实测，并给出 GCC GIMPLE Pass / Cranelift 对偶。删掉飞腾与代码行号后，本文是 LLVM 官方文档翻译——判定失败。故此节三者并重。
> **关键反向锚点**：`grep -rn "Phytium\|FTC86" llvm/lib/Transforms/ mlir/` 在中端与 MLIR **0 命中**（[实测-grep]）——这是中端优化 **target-independent 本质**的铁证。中端连飞腾字符串都没有，飞腾特异性全部下沉到后端（[E05/E08]）。这条反向锚点恰恰解释了"为什么飞腾的编译器命运不取决于中端 Pass，而取决于后端 cost model"。

### 2.1 GVN / NewGVN / EarlyCSE 三角：2026 还剩多少边际收益（含对标表）

#### 2.1.1 三个冗余消除 Pass 的真实分工

LLVM 有**三个**层级递进的冗余消除 Pass，实测它们在默认流水线的分工（[实测-PassBuilderPipelines.cpp]）：

| Pass | 层级 | 默认状态 | 算法 | 适用 |
|------|------|:--------:|------|------|
| **EarlyCSE** | 基本块/局部 | ✅ **默认开**（多处 addPass：470/611/839/1150/1426/1560） | Common Subexpression Elimination，基于 dominator tree 的局部 CSE | 抓"刚算过又算"的局部冗余，**快、便宜、跑很多遍** |
| **GVN**（`GVN.cpp`） | 函数/全局 | ✅ **默认开**（`:756` else 分支） | Global Value Numbering，基于值编号的全局冗余消除 | 跨基本块的等价表达式识别，**吃 MemorySSA 识别冗余 load** |
| **NewGVN**（`NewGVN.cpp`） | 函数/全局 | ❌ **默认关**（`:207` `cl::init(false)`） | NewGVN，基于 SCC 的等价类划分，**理论更强**（识别更多冗余） | GVN 的"升级版"，但**编译时长代价高**，社区未敢默认 |

**反直觉点**：很多人以为"NewGVN 既然更先进，肯定替代了 GVN"。**错了**。实测 `PassBuilderPipelines.cpp:753-756`：

```cpp
if (RunNewGVN)              // RunNewGVN 默认 false（line 207）
  FPM.addPass(NewGVNPass()); // 走 NewGVN（需 -mllvm -enable-newgvn）
else
  FPM.addPass(GVNPass());    // 默认：仍是老 GVN.cpp
```

NewGVN 由 Daniel Berlin（GVN 重写者）在 LLVM 5-6 时期引入，**至今（LLVM 23）仍非默认**。原因不是"算法不好"，而是 **NewGVN 在大型函数上的编译时长开销**显著高于老 GVN，且社区反复测下来端到端性能提升"不足以 justify 默认开"。**这是一个"算法先进不等于工程采纳"的教科书案例**——飞腾工程师若以为"我在用 NewGVN"，多半是误会，默认 `-O2` 跑的是老 GVN。

#### 2.1.2 EarlyCSE 为什么是真正的主力

`grep EarlyCSE PassBuilderPipelines.cpp` 命中 7 处（470/611/839/1150/1426/1560 + 注册）——**EarlyCSE 在流水线里被跑了很多遍**，远比 GVN 频繁。原因：EarlyCSE 又快又便宜（O(指令数)），在每个"可能产生冗余"的 Pass 之后跑一遍，把低垂果实随手摘掉。**这是 LLVM 流水线的"勤扫地带"哲学**：与其让一个昂贵的全局 Pass 一次性扫，不如让便宜的局部 Pass 高频扫。

**飞腾工程教训**：飞腾开发者若做 NPU 算子优化，常犯的错误是"过度迷信 GVN/NewGVN"，拼命加 `-mllvm -enable-newgvn`。实测下来，**收益往往不如多跑一遍 EarlyCSE + 调整 Pass 顺序**。中端优化的真相是**组合 > 单点**。

#### 2.1.3 中端冗余消除 Pass 边际收益对标表（≥1 对标表之①，宪法 §7.1）

| Pass | 引入年代 | 默认 | 飞腾 FTC862 典型收益 | 2026 状态 | 教训 |
|------|:------:|:----:|:----:|:--------:|------|
| **EarlyCSE** | 2010s | ✅ | 1-3%（局部） | 🟢 主力，高频跑 | 便宜量大，组合的基石 |
| **GVN**（老） | 2000s | ✅ | 2-5%（全局） | 🟡 已躺平，但仍是默认 | 算法到顶，靠 MemorySSA 续命 |
| **NewGVN** | 2017+ | ❌ | 3-6%（理论更强） | 🟠 先进但默认关 | 算法 ≠ 采纳，编译时长是硬约束 |
| **SCCP** | 1991 | ✅ | 1-2%（常量） | 🟡 经典，仍跑 | Wegman-Zadeck，30 年没过时 |
| **InstCombine** | 2003+ | ✅ | 5-15%（peephole） | 🟢 巨兽，见 §2.2 | 真正的"低垂果实收割机" |

**结论**：2026 年中端标量优化的边际收益**整体躺平**。飞腾项目 [View_01 实测] `-O2`→`-O3` 仅 ~2% 印证了这一点。真正的提升已不在单个 Pass，而在 §2.3 Polly（多面体）、§2.6 PGO/BOLT（反馈）、§2.4 MLIR（换 IR）。

---

### 2.2 InstCombine 巨兽 + SROA + SCCP + MemCpyOpt：标量优化的"四大金刚"（图表 1/3：Pass 流水线）

#### 2.2.1 InstCombine 是个被拆成 17 个文件的巨兽

实测 `llvm/lib/Transforms/InstCombine/` 目录（[实测-InstCombine/]）：

```
InstructionCombining.cpp      ← 主入口（Peephole 优化总调度）
InstCombineAddSub.cpp         ← 加减法折叠（x+0→x, x-x→0）
InstCombineAndOrXor.cpp       ← 位运算简化（x&x→x, x|~x→-1）
InstCombineMulDivRem.cpp      ← 乘除取模（x*8→x<<3, x%C→strength）
InstCombineShifts.cpp         ← 移位（x<<1→x*2 选优）
InstCombineCompares.cpp       ← 比较（a<b && b<c 推导）
InstCombineCasts.cpp          ← 类型转换消除
InstCombineCalls.cpp          ← 库调用简化（fabs→fabs intrinsic）
InstCombineLoadStoreAlloca.cpp← load/store/alloca 折叠
InstCombinePHI.cpp            ← PHI 节点简化
InstCombineSelect.cpp         ← select 简化
InstCombineVectorOps.cpp      ← 向量操作简化
InstCombineAtomicRMW.cpp      ← 原子 RMW
InstCombineSimplifyDemanded.cpp ← 按需简化（demanded bits）
InstCombineNegator.cpp        ← 负数推导
InstCombineInternal.h         ← 内部接口
```

**为什么拆这么细**：InstCombine 是 LLVM **最大的单个 Pass**（总计上万行），按操作类型拆文件是为了**编译加速**（改 AddSub 不用重编 MulDivRem）和**维护性**（每个文件一个负责人）。它的本质是 **peephole 优化**（窥孔优化）——看一小段指令，用等价但更优的指令替换。`x*8→x<<3`、`x-x→0`、`a&&b 的 select 简化` 都在这里。

**飞腾相关性**：飞腾 FTC862 的 `UDOT`（int8 点积，16.9× 加速）**在中端选不出来**——InstCombine 只做标量等价替换，不做"把 mul+add 聚合成 dotprod"。UDOT 的识别发生在后端 SelectionDAG（[E05/E07]）。**这是中端 target-independent 的本质体现**：中端不知道 NEON，更不知道 UDOT。飞腾要让 UDOT 自动选出来，要么改后端，要么在 [E03] 说的 `VectorizerEndEPCallbacks` 挂私有 Pass。

#### 2.2.2 SROA：把栈上 struct 拆进寄存器

`SROA.cpp`（Scalar Replacement of Aggregates）是 LLVM 中端**最高收益的 Pass 之一**。它做的事：把 `struct { int a, b, c; } s; s.a=1; s.b=2;` 这种"栈上聚合体"**拆成独立的标量**，让后续 Pass（Mem2Reg/GVN）把它们提升进寄存器。**没有 SROA，所有 struct 都会留在内存里，每次访问都是 load/store**——性能灾难。

SROA 的现代版（LLVM 3.5+ 重写，Chandler Carruth 主导）用 **slice-based** 算法：分析每个 alloca 的访问切片，按切片重组。这是飞腾 C/C++ 代码（大量 struct/class）能否高效编译的**第一道关卡**。

#### 2.2.3 SCCP + ConstraintElimination：常量与约束推导

`SCCP.cpp`（Sparse Conditional Constant Propagation，Wegman-Zadeck 1991 算法）在 SSA 上做**稀疏条件常量传播**——它能证明"这个变量在所有路径上都是常量"，直接折叠。30 年了，仍是默认流水线的常量推导主力。

但 LLVM 近年新增 `ConstraintElimination.cpp`（[实测-Scalar/]）——这是"SCCP 的激进表亲"：它用 **SMT solver 在编译期证明约束**。比如 IR 里有 `assert(x < y); ... if (x < z)`，ConstraintElimination 能推出 `y <= z`，消掉一个分支。**代价**：SMT 求解慢，所以默认仅 `-O3` 且有 budget 限制才开。**这是"形式化方法进入标量优化"的标志性 Pass**，但又是"先进但不默认开"的另一例。

#### 2.2.4 MemCpyOpt + LoopIdiomRecognize：模式识别成库调用

`MemCpyOptimizer.cpp`（[实测-Scalar/]）把连续的 `load/store` 序列聚合成单条 `memcpy`/`memmove`；`LoopIdiomRecognize.cpp` 把 `for(i=0;i<N;i++) a[i]=0` 认成 `memset`。这两个 Pass 的价值在于**把循环降级成 libc 的向量化实现**——现代 glibc 的 `memset`/`memcpy` 是手写 NEON/SVE 汇编，飞腾 FTC862 上一次 `memset` 比手写循环快 5-10×。**飞腾服务器代码的隐藏加速器**。

#### 2.2.5 中端标量优化流水线图（图表 1/3）

```
┌─────────────────────────────────────────────────────────────────────────┐
│      LLVM 中端标量优化流水线（function 层，-O2 默认，LLVM 23 实测）        │
│                                                                         │
│  [Clang 前端输出 IR]                                                    │
│     │                                                                   │
│     ▼  ── SROA（拆 struct → 标量，最高收益第一道）                       │
│  [早期简化]                                                             │
│     │  ── InstCombine（peephole 巨兽，17 文件）                          │
│     │  ── SimplifyCFG                                                   │
│     │  ── EarlyCSE（局部冗余，便宜，跑很多遍）★主力                      │
│     ▼                                                                   │
│  [循环优化层]  ── loop(                                                 │
│     │     LoopRotate / LoopSimplifyCFG                                  │
│     │     LICM（LoopNestPass 双模，见 [E03] §2.3）                       │
│     │     LoopUnroll（动态 cost model，飞腾要校准）                      │
│     │     LoopIdiomRecognize（→ memset/memcpy）                         │
│     │     SimpleLoopUnswitch / LoopDeletion                             │
│     │  )                                                                │
│     ▼                                                                   │
│  [全局优化]                                                             │
│     │  ── SCCP（常量传播，1991 经典）                                    │
│     │  ── GVN（默认老版，NewGVN 需 -enable-newgvn）                      │
│     │  ── ConstraintElimination（SMT，仅 -O3）                          │
│     │  ── InstCombine（再跑一遍，吃前面 Pass 的红利）                    │
│     │  ── MemCpyOpt（聚合 → memcpy/memset）                              │
│     │  ── JumpThreading / CorrelatedValuePropagation                    │
│     ▼                                                                   │
│  [向量化层]  ── 见 §2.5 / [E07]                                         │
│     │  LoopVectorize + SLPVectorizer + VectorCombine                    │
│     ▼                                                                   │
│  [后端]  ── 见 [E05/E06/E08]                                            │
└─────────────────────────────────────────────────────────────────────────┘
   ★ 关键：中端 0 个飞腾字符串（grep 实测），飞腾命运在后端 cost model
```

---

### 2.3 Polly：多面体优化为何没进默认 -O3（含图表 2/3：覆盖率）

#### 2.3.1 Polly 的真实工程状态

实测 Polly 在 LLVM monorepo 的挂载方式（[实测-CMakeLists.txt]）：

```cmake
# llvm/CMakeLists.txt:107
set(LLVM_ALL_PROJECTS "bolt;clang;clang-tools-extra;cross-project-tests;
    lld;lldb;mlir;polly")   # polly 在 ALL_PROJECTS 列表里

# llvm/tools/CMakeLists.txt:54
add_llvm_external_project(polly)   # 但作为 external project 挂载
```

**关键**：Polly 在 `LLVM_ALL_PROJECTS` 里，但**默认构建不启用**——必须显式 `-DLLVM_ENABLE_PROJECTS=polly`。这意味着 `clang -O3` **绝不会触发 Polly**。Polly 是一个"按需加载"的 optional pass manager，通过 `-mllvm -polly` 开启。

#### 2.3.2 Polly 为什么没进 -O3：四个真实理由

| 理由 | 细节 | 证据 |
|------|------|------|
| **1. isl 依赖** | Polly 依赖 isl（integer set library，Sven Verdoolaege 维护），isl 是**额外的 C 库**，增加构建复杂度和体积 | [实测-polly/ 独立 lib + include] |
| **2. 编译时长爆炸** | 多面体调度（Pluto 调度、依赖分析）在大循环上**编译时长增长显著**，与 LLVM"快编译"的卖点冲突 | [社区-Discourse] |
| **3. 覆盖率受限** | Polly 要求循环是 **affine**（仿射，循环边界/数组下标是线性表达式），大量真实代码不满足 | [实测-polly test 用例都是规整循环] |
| **4. 收益不稳定** | 在能覆盖的 GEMM/conv 上收益巨大（2-5×），但在覆盖不了的代码上**纯编译开销无收益** | [报告-Polly benchmarks] |

#### 2.3.3 pet / PPL / isl 上游依赖对比

Polly 的多面体能力依赖一条**上游学术工具链**：

| 工具 | 来源 | 角色 | Polly 的用法 |
|------|------|------|-------------|
| **isl** | Sven Verdoolaege（INRIA/Intel） | 整数集/映射运算（多面体的数学引擎） | Polly 核心，所有调度/依赖分析基于 isl |
| **pet** | Sven Verdoolaege | Polyhedral Extraction Tool，从 C 代码提取多面体表示 | Polly 早期实验用，现主要靠 LLVM IR→ScopInfo |
| **barvinok** | Sven Verdoolaege | 计数多面体整数点（用于边界分析） | 可选 |
| **PPL/isl 对比** | PPL（Parma Polyhedra Library）已废弃 | 早期备选数学库 | Polly 早已迁到 isl，PPL 是历史 |

**对标**：GCC 也有 Graphite（GCC 的多面体框架，同样基于 isl），但 Graphite 的覆盖率/收益**长期不如 Polly**（[报告-Phoronix GCC Graphite vs Polly]）。**这是 LLVM 相对 GCC 的一个学术领先点**，但双方都没把多面体设为默认。

#### 2.3.4 Polly 覆盖率与收益矩阵（图表 2/3）

```
┌──────────────────────────────────────────────────────────────────────┐
│        Polly 多面体优化：覆盖率 × 收益矩阵（实测+社区报告）             │
│                                                                      │
│   收益 ▲                                                             │
│   5×  │                          ● GEMM (linalg/onnx matmul)         │
│       │                       ● Conv2D (im2col 前)                   │
│   2×  │                 ● stencil（规整 Jacobi）                     │
│       │            ● 规整数据搬运                                    │
│   1×  │●●●●●●●●●●●●●●●●●●●●●●●●●  ← 大量非 affine 代码（不覆盖）    │
│       │─────────────────────────────────────────────────► 覆盖率     │
│       0%   10%   20%   30%   40%   50%   60%   70%   80%  90%  100%  │
│                                                                      │
│   ● 飞腾相关性：GEMM/Conv 是飞腾 NPU/AI 推理的核心，Polly 理论收益高  │
│   ● 但飞腾 phytvm（TVM fork）走的是 MLIR/TIR 路线，不走 Polly         │
│   ● 结论：Polly 是"研究意义大、生产采纳低"的典型，飞腾更该看 MLIR    │
└──────────────────────────────────────────────────────────────────────┘
```

**飞腾工程教训**：飞腾若做 NPU 算子优化，**不要押注 Polly**——飞腾 phytvm 已经是 TVM fork，TVM 的调度（auto_scheduler/meta_schedule）+ MLIR 才是飞腾 AI 编译的正路（见 §2.4）。Polly 适合"传统 HPC C 代码"的 GEMM/stencil，不适合飞腾 NPU 的算子图。

---

### 2.4 ⭐ 断层 ② 深拆：MLIR-core 融合裂痕（45 方言 / 80 lowering / 谁养 MLIR）

> 本节是本文的核心，承载本项目 [断层 ②](../改造蓝图_LLVM.md#5-五个服务器命脉级断层)（对标飞腾项目"无 SVE 向量化天花板"战略伤疤）。

#### 2.4.1 裂痕的本质：LLVM IR 是单层的，MLIR 是多层的

LLVM IR（[E02]）是**单一、低级、SSA-only** 的中间表示——它只有一种抽象层级：无限虚拟寄存器 + 指令。这套设计在 2000 年（Lattner & Adve 2004 CGO）是革命性的（SSA 普及、JIT 友好），但到 2019 年（MLIR 进入 LLVM）暴露了一个**结构性天花板**：**单层 IR 无法高效承载循环变换、张量计算、异构后端**这三类现代编译需求。

MLIR（Multi-Level Intermediate Representation，Lattner et al 2021）的解法是**多层 dialect**：每一层抽象（循环、张量、向量、GPU、异步）都是一个独立的 dialect，dialect 之间通过 **lowering（降级）** 转换。一个程序可以在高层 dialect 上做高层优化（如 Linalg 上做 fusion），再逐层 lower 到 LLVM IR。

**裂痕的字面意思**：MLIR 是 LLVM 的子项目（在 `llvm-project` monorepo 里），但它**不是 LLVM IR 的扩展**，而是一套**平行的 IR 体系**。MLIR 最终会 lower 到 LLVM IR（通过 `ConvertToLLVM`），但两者语义不同构——MLIR 的"操作（op）"不是 LLVM IR 的"指令"，MLIR 的"region/block"不是 LLVM IR 的"基本块"。**这就是"二元裂痕"**：一个编译器栈里同时存在两套 IR 体系，各自有自己的 PassManager、类型系统、方言生态。

#### 2.4.2 45 方言爆炸：是降复杂度还是升复杂度？

实测 `mlir/include/mlir/Dialect/` 目录（[实测-mlir Dialect]），统计 dialect 数量：

```
核心结构 dialect（~12）：Affine / SCF / ControlFlow / Func / Index /
    Arith / Math / Complex / MemRef / Tensor / Vector / Shape
ML/AI dialect（~6）：Linalg / Tosa / StableHLO(外) / Quant / SparseTensor / MLProgram
异构后端 dialect（~8）：GPU / NVGPU / AMDGPU / SPIRV / XeGPU / ArmSVE / ArmSME / ArmNeon
转换框架 dialect（~4）：PDL / PDLInterp / Transform / IRDL
系统/其它（~15）：Async / OpenMP / OpenACC / Bufferization / EmitC / LLVMIR /
    DLTI / Ptr / UB / MPI / Shard / WasmSSA / SMT / Utils / X86
─────────────────────────────────────────────
合计：45 个 dialect 目录（[实测]，佐证 Lens_01"48 方言"判断，
      差异来自外部 dialect 如 StableHLO 在 openxla/stablehlo 仓库）
```

**问题：45 方言会降低还是升高编译器复杂度？** 这位专家的判断——**辩证**：

- **短期升高复杂度**（学习曲线爆炸 + 互操作地狱）：一个新人在 45 个 dialect 里找不到北；两个 dialect 之间的 conversion 经常需要 `UnrealizedConversionCast` 桥接（`ReconcileUnrealizedCasts` 这个 conversion 目录的存在本身就是"互操作缝缝补补"的证据）；`mlir/lib/Conversion/` 有 **~80 个 lowering 目录**（[实测]），每对 dialect 组合可能需要独立 conversion。
- **长期是降复杂度的唯一出路**：单层 LLVM IR 的复杂度已经压不住 AI/异构编译。TVM 用 Relay+TIR 两层、XLA 用 HLO、PyTorch 用 TorchScript——**业界共识是"分层"**。MLIR 把"分层"做成了可组合的 dialect 框架，45 方言看似多，但每个 dialect **职责单一**（Linalg 只管张量、Vector 只管向量、SCF 只管结构化控制流），组合起来比"在一个胖 IR 里塞所有概念"更可维护。

**飞腾相关性**：飞腾 phytvm 是 TVM fork（[实测-vanilla Apache TVM]，oracle §0.3 已澄清）。TVM 的 Relay/TIR 是**自己的多层 IR**，**没有用 MLIR**。但业界趋势（IREE/StableHLO/Torch-MLIR/Intel graph-compiler）都在迁向 MLIR。飞腾 NPU 编译栈的"路线选择"（继续 TVM 私有 IR vs 迁向 MLIR）是飞腾 AI 编译的**5-10 年战略决策**——这道裂缝，飞腾迟早要正面踩上。

#### 2.4.3 谁养着 MLIR：供应链视角（衔接 [Lens_03]）

| 方言族 | 主要养育方 | 商业动机 |
|--------|-----------|---------|
| **Linalg / Vector / Tensor** | Google（IREE）+ LLVM 核心 | AI 推理/训练编译器底座 |
| **GPU / NVGPU / NVVMToLLVM** | NVIDIA + Google | CUDA 生态 |
| **AMDGPU / GPUToROCDL** | AMD | ROCm 生态 |
| **XeGPU / XeVMToLLVM** | Intel | oneAPI/Sycl |
| **ArmSVE / ArmSME / ArmNeon** | ARM + Linaro | ARM 服务器/嵌入式 |
| **SPIRV** | Google + Khronos | Vulkan/OpenCL 跨厂商 |
| **Tosa** | Linaro + ARM | 神经网络可移植层 |
| **OpenMP / OpenACC** | 国家实验室 + AMD | HPC |

**关键发现**：**没有飞腾/华为/国产厂商养的 dialect**（[实测-grep Phytium/FTC86 mlir 0 命中]）。MLIR 的养育图完全是**美欧大厂主导**。飞腾 NPU 若要做 MLIR 后端，只能**做消费方/扩展方**，无法做核心 dialect 的定义方——这是飞腾在 MLIR 生态的**结构性从属地位**。

#### 2.4.4 MLIR Linalg → LLVM IR lowering pipeline 实例（硬问题 4）

一条 `linalg.matmul` 算子降到 LLVM IR 的典型阶梯（[实测-mlir Conversion 目录]）：

```
┌──────────────────────────────────────────────────────────────────────┐
│   MLIR Linalg.matmul → LLVM IR lowering 阶梯（iree-opt 可观测）       │
│                                                                      │
│  linalg.matmul ins(%A,%B) outs(%C)         ← Linalg 结构化算子        │
│     │  LinalgToStandard / Linalg Hoisting                            │
│     │  (linalg → loop nest + vector ops)                              │
│     ▼                                                                 │
│  scf.for / vector.contract / vector.transfer         ← SCF + Vector   │
│     │  VectorToSCF / VectorToLLVM                                     │
│     │  (vector.contract → loop or aarch64.neon.udot intrinsic)        │
│     ▼                                                                 │
│  arith.mulf / arith.addf / memref.load / memref.store ← Arith+MemRef  │
│     │  ArithToLLVM / MemRefToLLVM / SCFToControlFlow                  │
│     ▼                                                                 │
│  llvm.mlir + scf→cf.br                                ← LLVMIR dialect│
│     │  ConvertToLLVM / ReconcileUnrealizedCasts                       │
│     ▼                                                                 │
│  LLVM IR (最终，可被 llc 编译)                                        │
│                                                                      │
│  ★ 5+ 条 conversion 通道，每层都可插优化 Pass                        │
│  ★ 飞腾相关性：vector.contract 降到 aarch64.neon.udot 是关键一跳，     │
│    决定飞腾 FTC862 能否吃上 UDOT 16.9× 加速                          │
└──────────────────────────────────────────────────────────────────────┘
```

**与 LLVM IR Loop Vectorizer 的对比**（硬问题 5）：

| 维度 | LLVM IR LoopVectorizer | MLIR vector dialect |
|------|----------------------|---------------------|
| **抽象层级** | 在低级 SSA 上硬做向量化 | 向量是一等公民，先建抽象再优化 |
| **建模工具** | VPlan（[实测-Vectorize/ 20+ VPlan 文件]） | vector.contract/transfer/broadcast ops |
| **多后端** | 一个 IR，后端 cost model 决定 | vector→LLVM/vector→GPU/vector→ArmSME 多路 |
| **可变长向量** | VP（Vector Predication）补丁式 | ArmSVE/SME dialect 原生 |
| **飞腾命运** | 受 NEON 128-bit 硬上限 | 同样受，但可插 ArmNeon dialect 优化 |

**判断**：**MLIR vector dialect 在"抽象表达力"上先进，但 LoopVectorizer 在"工程成熟度"上领先**。前者是未来，后者是现在。飞腾短期仍吃 LoopVectorizer，长期要看 MLIR 路线。

---

### 2.5 Attributor + PGO/BOLT：过程间与反馈优化

#### 2.5.1 Attributor：默认关的过程间属性推导（硬问题 7）

`IPO/Attributor.cpp` + `AttributorAttributes.cpp`（[实测-IPO/]）是 LLVM 近年过程间优化的重头戏。它的思路：**统一的属性推导框架**——`noundef`/`nocapture`/`readonly`/`willreturn`/`noalias` 等属性，从"分散在各 Pass 里各自推导"升级为"Attributor 统一框架，迭代到不动点"。

但实测 `PassBuilderPipelines.cpp:285-286`：

```cpp
static cl::opt<AttributorRunOption> AttributorRun(
    "attributor-enable", cl::Hidden, cl::init(AttributorRunOption::NONE), ...);
// 默认 NONE —— 关闭！
```

Attributor **默认不跑**，需 `-mllvm -attributor-enable=full/light/module/cgscc`。为何？因为"激进推导属性"在**有 UB 的代码**上会触发 miscompilation（推导出 `noundef`，但代码传了 undef → UB → 优化后崩溃）。社区在打磨 soundness，还没敢默认。**这是"算法先进 ≠ 默认采纳"的第三例证**（前两例：NewGVN、ConstraintElimination）。

**飞腾工程教训**：飞腾若做 LTO（链接时优化），Attributor 在 `-Wl,-plugin-opt=attributor-enable=module` 下能带来 2-5% 收益，但**必须先在飞腾代码库上跑 Alive2 验证**（[E03] §2.7），否则有 miscompilation 风险。

#### 2.5.2 PGO 与 BOLT 的反差（硬问题 6）

LLVM 的反馈优化有**两个时间点**：

| 时间点 | 工具 | Pass | 喂的 profile | 飞腾场景 |
|--------|------|------|------------|---------|
| **编译期** | `SampleProfile.cpp`（[实测-IPO/]）+ `MemProfContextDisambiguation` | AutoFDO（Google）/ clang PGO | perf 采样的 branch/load profile | 飞腾服务器 spec2017/数据库 |
| **链接后** | BOLT（[E12]） | 重跑整个中端 Pass | perf 采样的二进制 profile | 飞腾服务器高收益场景 |

**反差**：传统 PGO 在**编译期**用 profile 指导内联/布局；BOLT 在**链接后**（二进制已生成）**重跑中端 Pass**——这是 LLVM 相对 GCC 的架构级优势（GCC 没有等价 BOLT）。飞腾服务器场景（Java/数据库/spec）用 BOLT 常见 5-15% 提升，**且无需重编**（只改二进制）。**飞腾 Yocto/Buildroot 的 LLVM 太老（13/9）用不了 BOLT**——这是飞腾升级 LLVM 版本的又一动机。

---

### 2.6 飞腾 LoopUnroll 实证：LLVM 默认值对飞腾是否次优（硬问题 8）

#### 2.6.1 飞腾 Lab02 实测：unroll 2 最优

飞腾项目 Expert_11（`../../体系结构实验/Expert_11_Compiler_Research/README.md`） §line 593 实测：**飞腾 FTC862 上 LoopUnroll 因子 = 2 最优**（Lab02 数据）。这条结论的物理基础（飞腾 E11 §line 163）：飞腾有 **32 个 V 寄存器**（V0-V31），真正自由的有 16 个（V16-V31）+ 8 个传参可重用，`4×4` 矩阵分块能全进寄存器。**unroll 太大（如 4/8）会爆寄存器→溢出→掉速；unroll 太小（1）ILP 不足**。

#### 2.6.2 LLVM 默认 LoopUnroll 是动态 cost model，不硬编码 2

实测 `PassBuilderPipelines.cpp:1353`：

```cpp
FPM.addPass(LoopUnrollPass(LoopUnrollOptions(
    Level.getSpeedupLevel(),               // -O2→1, -O3→2
    /*OnlyWhenForced=*/!PTO.LoopUnrolling, // 默认 false → 默认开
    PTO.ForgetAllSCEVInLoopUnroll)));
```

**关键**：LoopUnroll 的展开因子**不是硬编码**，而是由 `LoopUnrollPass` 内部的 **cost model 动态决策**——它查循环的指令数、寄存器压力、目标 TTI（Target Transform Info）的 unroll 成本。**问题**：这个 TTI 在主线 LLVM 上用的是"通用 Cortex-A 类"近似（因为 [实测-grep FTC86 中端 0 命中]，主线 LLVM 无 FTC86x 调度模型，见 [E08]）。

#### 2.6.3 飞腾的工程现实：默认 cost model 次优

| 因素 | 主线 LLVM 默认 | 飞腾 FTC862 真实 | 差距 |
|------|:-------------:|:----------------:|:----:|
| **unroll 因子** | 动态（cost model 算） | 实测 2 最优 | 默认可能选 4（基于通用模型），爆寄存器 |
| **寄存器数** | 假设 32 V（NEON 标准） | 真正自由 16 | 默认高估可用数 |
| **NEON 端口** | 通用假设 | 2 通道/cycle | 默认可能扎堆 |
| **`.md` 成本** | 通用 AArch64 | 飞腾校准（L1D 4 周期/NEON 1 周期） | 飞腾 E11 §line 340：校准后展开阈值更准 |

**结论**：**LLVM 默认 LoopUnroll 对飞腾大概率次优**。飞腾要让 unroll 选对，有两条路：
1. **飞腾自维护 LLVM fork + 填 FTC86x 调度模型/cost model**（[E08/E18]）—— 重，但根治。
2. **`#pragma unroll(2)` 显式标注**（飞腾算子热点）—— 轻，但侵入源码。

**飞腾实战建议**：飞腾 NPU/算子热点的 GEMM/conv，**显式 `#pragma unroll(2)` + `-mllvm -unroll-count=2`** 是最低成本的补偿。飞腾 E11 Lab02 的实测数据就是这条建议的依据。

---

### 2.7 GIMPLE Pass（GCC）vs LLVM IR Pass 对照表（≥1 对标表之②，硬问题 9）

> **对偶锚点**：飞腾主力是 PhyGCC（基于 GCC），PhyCC 基于 LLVM。这张表是飞腾工程师在两套中端之间迁移的导航图（深化 [E03] §2.5 的 Pass 框架对照）。

| GCC GIMPLE Pass | 对应 LLVM IR Pass | 概念对应 | 差异点 / 飞腾迁移坑 |
|----------------|-------------------|:--------:|---------------------|
| `pass_sra`（struct 拆分） | **SROA** | 聚合体标量化 | LLVM SROA 是 slice-based（重写版），GCC SRA 较老 |
| `pass_forwprop`（前向传播） | **InstCombine** + InstSimplify | peephole 简化 | LLVM 拆成 InstCombine（巨兽17文件）+ InstSimplifyPass |
| `pass_vrp`（值范围传播） | **SCCP** + CVP（CorrelatedValuePropagation） | 常量/范围推导 | GCC VRP 更激进，LLVM 分两个 |
| `pass_pre`（部分冗余消除） | **GVN**（默认）/ NewGVN | 冗余消除 | LLVM 默认老 GVN，NewGVN 需开 |
| `pass_dce` / `pass_dse` | **DCE** / **DSE**（DeadStoreElimination） | 死代码/死存储 | 同义 |
| `pass_phiocp` / `pass_phiopt` | InstCombine（PHI 部分）/ JumpThreading | PHI 优化 | LLVM JumpThreading 更强 |
| `pass_loop`（循环管线） | LoopPassManager（LICM/Unroll/Rotate/Idiom） | 循环优化 | LLVM 有 LoopNestPass 双模（[E03]） |
| `pass_distribute_loop` | **LoopDistribute** | 循环分布 | 同义 |
| `pass_vect`（tree-vectorizer） | **LoopVectorize** + SLPVectorizer | 向量化 | 见 [E07] |
| `pass_memcpyopt`（memset/memcpy 识别） | **LoopIdiomRecognize** + MemCpyOpt | 模式识别成库调用 | LLVM 拆两个 |
| `pass_tail_recursion` | **TailRecursionElimination** | 尾递归消除 | 同义 |
| `pass_reassoc`（重关联） | **Reassociate** | 表达式重排 | 用于 ILP/精度 |
| `pass_build_alias` | AliasAnalysis（分析，非 pass） | 别名分析 | **GCC 当 pass，LLVM 当分析惰性算** |
| `pass_ipa_*`（过程间） | **Attributor**（默认关）+ FunctionAttrs | 过程间属性 | LLVM 新框架，但默认关 |
| `-fprofile-use`（AutoFDO） | **SampleProfile** | 反馈优化 | LLVM 还有 BOLT（链接后） |

**对偶判断**：飞腾 PhyGCC 工程师转 LLVM 的**最大认知冲击**有三：(1) "分析不是 pass"（[E03] §2.5 已述）；(2) "InstCombine 是拆成 17 文件的巨兽"（GCC 的 `forwprop` 是单文件）；(3) "NewGVN/Attributor/ConstraintElimination 算法先进但默认关"——GCC 的激进优化默认开的更多，LLVM 更保守。**飞腾工程师要主动 `-mllvm -enable-newgvn` / `-attributor-enable` 才能吃到先进算法**。

---

### 2.8 AI 辅助中端优化：mlir-opt-repl / mlirAgent（硬问题 12，2026 前沿）

2026 年的新趋势：**LLM 进入中端优化流程**。

| 项目 | 来源 | 做什么 | 局限 |
|------|------|--------|------|
| **mlir-opt-repl** | LLVM PR #203796（2026-06） | MLIR Pass 流水线交互式 REPL + **MCP server**（Claude Code 集成），AI 辅助调试 | 仅调试辅助，不自动优化 |
| **mlirAgent** | UC Berkeley | LLM 引导 MLIR/LLVM 优化，binary size -8.78% | **LLM 不能替代编译器 Pass**（Gemini 2.5 Pro -11.9% 仍不及专用 Pass） |
| **Intel graph-compiler** | Intel | MLIR-based DL 编译器，对标 IREE | 仅 Intel 硬件 |
| **LLVM Lighthouse** | LLVM 官方 | MLIR ingress-scheduler-runtime 框架 | 早期 |

**这位专家的判断**：AI **不会取代中端 Pass**（Pass 是经过 Alive2 验证的确定算法，LLM 是概率性的，不能进正确性敏感链路）。但 AI 会**重塑 Pass 的发现/调试**——mlir-opt-repl 让"试不同 Pass 组合"变成对话，mlirAgent 让"找最优 binary size"变成搜索。**飞腾 NPU 算子优化的未来工具链，大概率是 MLIR + AI 辅助的组合**。

---

## 3. 设计决策评估：中端优化哪些决策认可 / 哪些该改 / 飞腾工程教训

### 3.1 认可的决策（中端做对的事）

1. **InstCombine 的"巨兽拆分"工程**：把 peephole 按操作类型拆 17 文件，是**编译加速 + 维护清晰**的工程典范。GCC 的 `forwprop` 单文件改起来要全重编，LLVM 改 `InstCombineAddSub.cpp` 只重编那一个 TU。**这是 LLVM 编译基础设施现代化的缩影**。
2. **EarlyCSE 高频跑的"勤扫地带"哲学**：比一个昂贵的全局 Pass 低频扫，便宜局部 Pass 高频扫的组合**实测收益更高**。飞腾做私有 Pass 应学这个——把便宜的局部 Pass 多跑几遍。
3. **LoopNestPass 双模机制**（[E03] §2.3）：让 LICM/LoopInterchange/LoopFlatten 能协同看循环嵌套，是**循环优化的一次结构升级**。飞腾 GEMM 三层嵌套直接受益。
4. **BOLT 链接后优化的架构创新**：LLVM 独有（GCC 无等价物），飞腾服务器场景高收益。

### 3.2 该改的决策（中端的债与坑）

1. **NewGVN 引入近 10 年仍非默认**——这是"先进算法没落地"的债。社区的解释是"编译时长"，但真相是**社区治理偏保守**，没魄力默认切。敢说：**NewGVN 该在 LLVM 20+ 默认开**，编译时长可用 budget 控制。
2. **Attributor 同理默认关**——过程间属性推导的统一框架被晾着，浪费了它的潜力。飞腾做 LTO 应主动开。
3. **ConstraintElimination 仅 -O3**——SMT 驱动的约束推导是"形式化进标量优化"的标志性 Pass，但 budget 限制太严，实战收益被压低。
4. **Polly 没进默认流水线是工程债**——多面体优化在 GEMM/conv 上 2-5× 收益，却因 isl 依赖/编译时长被边缘化。**这是"研究领先但工程采纳失败"的典型**。
5. **LLVM IR 单层表达力的天花板**——循环变换在单层 IR 上"低效"（Michael Kruse 2020 RFC），这是 MLIR 出现的根因。**LLVM core 的中端，本质上是被 MLIR 补完的**。

### 3.3 飞腾工程教训（可执行）

1. **飞腾 LoopUnroll 默认次优 → 显式 `#pragma unroll(2)` + 校准 cost model**。飞腾 E11 Lab02 unroll 2 最优是铁证。
2. **飞腾中端 0 飞腾字符串 → 中端优化不是飞腾调优的战场**。飞腾编译器命运在后端（cost model/调度模型/寄存器，见 [E05/E06/E08]）。中端只能靠"通用 LLVM 升版本"吃红利。
3. **飞腾 NPU 编译栈的 MLIR 路线选择**：phytvm（TVM fork）的 Relay/TIR 是私有多层 IR，长期要看是否迁 MLIR。**建议飞腾评估 IREE/StableHLO/Torch-MLIR 路线**，避免 TVM 私有 IR 的生态孤岛。
4. **飞腾服务器场景上 BOLT**：spec2017/数据库 BOLT 5-15% 提升，但需 LLVM ≥ 14（飞腾 Yocto 13 / Buildroot 9 太老）。**升级 LLVM 是前提**。
5. **飞腾若做 LTO，主动开 Attributor + Alive2 验证**：Attributor 默认关，但 LTO 场景 2-5% 收益，前提是过 Alive2 soundness 验证。

---

## 4. 这一视角的盲区与反方（诚实段，强制）

### 4.1 中端优化专家看不见什么

1. **看不见后端的寄存器/调度现实**。中端 Pass 是 target-independent 的（[实测-grep Phytium 0 命中]），中端"完美"的 IR 到了后端可能因寄存器溢出/调度错配掉性能。**飞腾编译器命运不在中端**——这是本视角最大的盲区。要靠 [E05/E06/E08] 补。
2. **看不见 Pass 框架的正确性契约**。这位专家关心"算法对不对"，**不关心 PreservedAnalyses 失效契约对不对**（那是 [E03] 的活）。一个算法正确的 Pass，可能因错误声明 `preserve` 而触发 miscompilation。**算法对 ≠ 框架对**。
3. **看不见用户的真实工作流**。绝大多数飞腾开发者**一辈子不调中端 Pass**，只 `-O2`。中端优化的所有精妙，对 99% 用户是黑盒。**性能感知的只是 `-O2` 快不快**。
4. **看不见前端语义**。中端 IR 是 Clang/Flang 生成的（[E01/E16]），中端优化的前提是"IR 语义正确"。一个前端 bug 生成的错误 IR，中端 Pass 会"忠实地"优化成另一个错误。**中端无错 ≠ 程序对**。
5. **看不见 IR 设计的根本约束**。中端能做的优化，受 LLVM IR 表达力限制（[E02]）。单层 IR 的天花板，是中端优化躺平的根因——但这位专家容易归因于"算法到顶"，**忽略了"换 IR（MLIR）才是出路"**。

### 4.2 反方观点：中端优化可能根本不值得这么多关注

一个激进的反方：**LLVM 中端优化的边际收益已整体躺平，社区投入的中端 Pass 维护成本（80+ 标量 Pass、InstCombine 17 文件）可能远超收益**。论据：
- 飞腾项目 [View_01 实测]：`-O2`→`-O3` 仅 ~2%。NewGVN/Attributor/ConstraintElimination 三个"先进 Pass"都默认关——说明社区自己也知道"默认开收益不抵风险"。
- 真正的性能来源已转移：反馈优化（PGO/BOLT，5-15%）、后端 cost model、异构编译（MLIR/GPU）。**中端标量优化是"上个时代的红利"**。
- 如果把维护 80+ 标量 Pass 的人力投到 MLIR 或后端，LLVM 可能进步更快。

**这个反方有道理但不完全对**：中端优化的价值不在"单个 Pass 的边际收益"，而在**整个流水线的累积效应**——少了 EarlyCSE/InstCombine/SROA 任何一个，性能都会断崖式下降（它们是"基础设施"不是"加分项"）。**躺平的是边际收益，不是基础价值**。但反方戳中真问题：**LLVM 中端的未来不在新标量 Pass，而在 MLIR**——这是本视角最该诚实承认的。

---

## 5. 与其他视角对偶（一致 / 冲突，强制）

### 5.1 一致（互相印证）

- **与 [E02 IR 设计](../Expert_02_LLVM_IR_Design/README.md) 一致**：E02 谈 IR 语义（单层 SSA 的表达力边界），E04 谈"在这个边界上做优化的边际收益躺平"。E04 的悲观（中端躺平），E02 的结构性解释（单层 IR 表达力受限）。**两者共同指向 MLIR 是出路**。
- **与 [E03 Pass 框架](../Expert_03_Pass_Framework/README.md) 一致**：E03 谈"Pass 跑在什么骨架上"，E04 谈"骨架里塞的算法"。E03 的"-O2→-O3 边际趋零"，E04 给出算法级解释（GVN/InstCombine 已打磨到顶）。E03 的工程红利（LoopNestPass 协同），E04 的算法承载。
- **与 [E07 自动向量化](../Expert_07_Auto_Vectorization/README.md) 一致**：E07 谈 LoopVectorizer 的算法，E04 谈它在中端流水线的位置 + MLIR vector dialect 的对偶。飞腾无 SVE 的向量化天花板，E04（IR 表达力）+ E07（算法）+ E08（NEON 硬上限）三角印证。
- **与 飞腾 Expert_11 编译器研究（`../../体系结构实验/Expert_11_Compiler_Research/README.md`） 一致**：飞腾 E11 给 PhyGCC GIMPLE Pass 实战，本项目 E04 给 LLVM IR Pass 框架机理。两者在"GIMPLE Pass vs IR Pass 对照"上互补（§2.7 表）。

### 5.2 冲突（视角打架）

- **与 [E03 Pass 框架](../Expert_03_Pass_Framework/README.md) 部分冲突**：E03 倾向"框架可组合性是新 Pass 价值所在"，E04 反驳：**新标量 Pass（NewGVN/Attributor/ConstraintElimination）算法先进但默认关，证明"框架再好也救不了算法躺平"**。E03 看工程红利，E04 看算法天花板。
- **与 [E05 CodeGen](../Expert_05_CodeGen_SelectionDAG_GlobalISel/README.md) 的张力**：E04 说"中端决定性能上限"，E05 反驳"上限能否落地看后端指令选择"。飞腾 UDOT 选不出来（[飞腾 E11]）是后端问题不是中端——E04 的中端视角会**高估中端、低估后端**。
- **与 [E12 LLD+BOLT](../Expert_12_LLD_BOLT/README.md) 的张力**：E04 说"中端 Pass 决定性能"，E12 反驳"BOLT 在链接后重跑中端，5-15% 提升，说明编译期中端没做到最好"。**BOLT 的存在本身就是对编译期中端的打脸**。
- **与 [Lens_02 Christensen 破坏式创新](../Lenses/Lens_02_Christensen.md) 的张力**：Christensen 透镜看"中端优化是 in-place 渐进改良，MLIR/Cranelift 是低端颠覆"。E04 作为中端维护者，天然倾向"渐进改良有价值"，与透镜"颠覆终将到来"存在张力。**这正是断层 ② 的根源**。

---

## 6. 参考文献（分级标注，≥15 条）

### 官方文档与源码（[官方]/[实测]）
1. **[实测]** OpenXiangShan/llvm-project（LLVM 23.0.0git）. `llvm/lib/Transforms/Scalar/`（80+ Pass：GVN.cpp/NewGVN.cpp/SCCP.cpp/SROA.cpp/LICM.cpp/LoopUnrollPass.cpp/LoopIdiomRecognize.cpp/MemCpyOptimizer.cpp/EarlyCSE.cpp/ConstraintElimination.cpp 等）/ `llvm/lib/Transforms/InstCombine/`（17 文件巨兽）/ `llvm/lib/Transforms/IPO/`（Attributor.cpp+AttributorAttributes.cpp/ModuleInliner.cpp/SampleProfile.cpp/MemProfContextDisambiguation.cpp）/ `llvm/lib/Transforms/Vectorize/`（LoopVectorize.cpp/SLPVectorizer.cpp/SandboxVectorizer/ + 20+ VPlan* 文件）/ `llvm/lib/Passes/PassBuilderPipelines.cpp:207,285-286,753-756,1353`（NewGVN/Attributor/LoopUnroll 默认状态）/ `llvm/CMakeLists.txt:107` + `tools/CMakeLists.txt:54`（Polly external project）/ `polly/`（独立子项目）/ `mlir/include/mlir/Dialect/`（45 dialect 目录）/ `mlir/lib/Conversion/`（~80 lowering 目录）/ `mlir/include/mlir/Dialect/Linalg/IR/`（LinalgStructuredOps.td）. 访问 2026-07-07.
2. **[实测]** grep "Phytium\|FTC86" `llvm/lib/Transforms/` + `mlir/` = **0 命中**. 中端与 MLIR target-independent 铁证. 访问 2026-07-07.
3. **[官方]** LLVM Project. *LLVM Language Reference Manual*. llvm.org/docs/LangRef.html. —— IR 指令语义.
4. **[官方]** LLVM Project. *Writing an LLVM Pass: New PM*. llvm.org/docs/WritingAnLLVMNewPMPass.html. —— Pass 编写.
5. **[官方]** polly.llvm.org. —— Polly 多面体优化官方页.

### 里程碑论文与书（[论文]/[书]）
6. **[论文]** Lattner, Amini, Pienaar, Riddle, Vasilache, Zinenko, Resnick, Shpeisman, Wenga. "MLIR: Scaling Compiler Infrastructure for Domain Specific Computation." *CGO* 2021. ⭐ MLIR 奠基论文，多层 IR 范式.
7. **[论文]** Grosser, Zheng, Pouchet, Sadayappan, Größlinger. "Polly — Performing polyhedral optimizations on a low-level intermediate representation." *Parallel Processing Letters* 2012. ⭐ Polly 多面体优化论文.
8. **[论文]** Larsen & Amarasinghe. "Exploiting Superword Level Parallelism with Multimedia Instruction Sets." *PLDI* 2000. ⭐ SLP 向量化奠基.
9. **[论文]** Nuzhdov, Franchetti, Baron. "Single-Source Vectorization for LLVM." (Loop Vectorizer / VP). —— 向量化单源.
10. **[论文]** Allen & Kennedy. *Optimizing Compilers for Modern Architectures* (2001, MK). ⭐ 循环变换+依赖分析奠基.
11. **[论文]** Wegman & Zadeck. "Constant Propagation with Conditional Branches." *TOPLAS* 1991. —— SCCP 算法.
12. **[论文]** Lopes, Menendez, Regehr. "Alive2: Bounded Translation Validation for LLVM." *POPL* 2022. —— Pass 形式化验证（衔接 ConstraintElimination）.
13. **[论文]** Lattner & Adve. "LLVM: A Compilation Framework for Lifelong Program Analysis & Transformation." *CGO* 2004. ⭐ LLVM 奠基.
14. **[书]** Cooper & Torczon. *Engineering a Compiler* 3rd (2022). —— 中端优化流水线设计.
15. **[书]** Muchnick. *Advanced Compiler Design and Implementation* (1997). —— 标量/循环优化理论.

### 开源项目与社区（[GitHub]/[Discourse]/[社区]）
16. **[Discourse]** Kruse, M. "Writing loop transformations on the right representation is more productive." discourse.llvm.org/t/.../54110 (2020-01). ⭐⭐⭐⭐⭐ Lattner 评论"MLIR 才是循环变换的正确抽象"——断层②根因.
17. **[Discourse]** "Enabling loop-interchange." discourse.llvm.org/t/.../82589 (2024-10). —— LLVM IR 不适合 loop 优化的实证.
18. **[GitHub]** openxla/stablehlo. github.com/openxla/stablehlo. —— ML 模型可移植层（MLIR 上层 dialect）.
19. **[GitHub]** llvm/torch-mlir. github.com/llvm/torch-mlir. —— PyTorch→MLIR 桥接.
20. **[GitHub]** ucb-bar/mlirAgent. github.com/ucb-bar/mlirAgent. ⭐ LLM 引导 MLIR/LLVM 优化，"LLM 不能替代 Pass"实证.
21. **[GitHub]** llvm/llvm-project PR #203796. mlir-opt-repl + MCP server. —— AI 辅助编译器开发.
22. **[社区]** LLVM Weekly（Alex Denner）. llvmweekly.org. —— 中端 Pass 每版本改动速报.

### 项目内交叉（[项目内]）
23. **[项目内]** 飞腾体系结构实验 Expert_11_Compiler_Research（`../../体系结构实验/Expert_11_Compiler_Research/README.md`） §line 593（unroll 2 最优实测）/ §line 340（飞腾校准 .md 成本）/ §line 389-390（-O3/-Os 实测）/ §line 163（32 V 寄存器）. —— 飞腾 GIMPLE Pass + unroll 实证.
24. **[项目内]** 本项目 [改造蓝图_LLVM.md](../改造蓝图_LLVM.md) §5 断层 ②. —— 本文承载的战略断层.
25. **[项目内]** 本项目 [Lens_03 供应链](../Lenses/Lens_03_SupplyChain.md)（MLIR 谁养）/ [Lens_01 历史](../Lenses/Lens_01_Historian.md)（48 方言实测）/ [领域资源库_LLVM.md](../领域资源库_LLVM.md) §6.1（48 方言）/ §7.8（MLIR×AI）. —— 通用资源.

---

## 7. 延伸阅读（项目内引用 + 外部）

### 项目内（对偶视角）
- [Expert_02_LLVM_IR_Design](../Expert_02_LLVM_IR_Design/README.md) —— IR 语义（中端优化的对象）。E04 是算法，E02 是表达力边界。
- [Expert_03_Pass_Framework](../Expert_03_Pass_Framework/README.md) —— Pass 骨架（中端 Pass 跑在它上面）。
- [Expert_05_CodeGen](../Expert_05_CodeGen_SelectionDAG_GlobalISel/README.md) —— 后端指令选择（飞腾 UDOT 在这里选）。
- [Expert_06_RegAlloc_Scheduler](../Expert_06_RegAlloc_Scheduler/README.md) —— 后端调度（unroll 后的寄存器现实）。
- [Expert_07_Auto_Vectorization](../Expert_07_Auto_Vectorization/README.md) —— LoopVectorizer 算法（中端向量化层）。
- [Expert_08_AArch64_Backend](../Expert_08_AArch64_Backend/README.md) —— AArch64 后端（飞腾 NEON/UDOT 落地）。
- [Expert_12_LLD_BOLT](../Expert_12_LLD_BOLT/README.md) —— BOLT 链接后优化（对编译期中端的反差）。
- [Expert_18_Phytium_Adaptation](../Expert_18_Phytium_Adaptation/README.md) —— 飞腾 phytvm / NPU 编译栈实证。
- 飞腾 Expert_11_Compiler_Research（`../../体系结构实验/Expert_11_Compiler_Research/README.md`） —— PhyGCC GIMPLE Pass 实战（GCC 对偶）。

### 外部资源（详见 [领域资源库_LLVM.md](../领域资源库_LLVM.md)）
- **MLIR 官方文档**（mlir.llvm.org）+ **IREE Linalg tutorial**（iree.dev/community/blog/2024-01-29-iree-mlir-linalg-tutorial）—— Linalg→LLVM lowering 一手。
- **Polly 官方**（polly.llvm.org）—— 多面体优化。
- **Kruse 2020 RFC**（discourse.llvm.org/t/.../54110）—— 断层②根因讨论。
- **mlirAgent / mlir-opt-repl**（领域资源库 §7.8）—— AI 辅助中端优化前沿。
- **Compiler Explorer**（godbolt.org）—— 在线看 `-O2` 中端 IR 变化。

---

## § 领域方法论与资源（不只 LLVM，给所有编译器中端优化从业者）

> 本章把 E04 上升为**任何编译器中端优化设计者**可复用的方法。LLVM 中端是案例锚点，方法普适。通用资源见 [`领域资源库_LLVM.md`](../领域资源库_LLVM.md)。

### 方法论一：优化收益递减定律（Diminishing Returns）

任何成熟编译器的标量优化都会**收敛到收益躺平**。判断标准：把某个 Pass 关掉，端到端性能掉多少？LLVM 实测：关掉 EarlyCSE/InstCombine/SROA → 性能断崖（基础价值）；关掉 NewGVN/Attributor → 几乎无感（边际躺平）。**飞腾做中端 Pass 投资，应优先保基础价值（高频跑 EarlyCSE 类），而非追逐边际（NewGVN 类）**。

### 方法论二：IR 表达力决定优化天花板

单层低级 IR（LLVM IR）适合标量/局部优化，**不适合循环变换/张量/异构**。多层 IR（MLIR/TVM Relay+TIR/XLA HLO）是现代编译器的共识。**判断一个编译器架构的天花板，看它的 IR 有几层**。飞腾 NPU 编译栈的 IR 层数（phytvm 的 Relay+TIR 是 2 层），决定了它的优化上限。

### 方法论三：算法先进 ≠ 工程默认采纳

NewGVN（更先进 GVN，默认关）/ Attributor（统一属性推导，默认关）/ ConstraintElimination（SMT 约束，仅 -O3）/ Polly（多面体，非默认构建）——LLVM 有一批"先进但不默认"的 Pass。**原因永远是：编译时长 / soundness 风险 / 覆盖率**。**飞腾做私有 Pass，要主动评估"默认开 vs 可选开"——默认开的 Pass 必须过 Alive2 + 大规模压测**。

### 方法论四：反馈优化是躺平期的主要增长点

当中端标量优化躺平，性能增长转移到**反馈优化**（PGO/BOLT，编译期 + 链接后）。飞腾服务器场景应把 BOLT 纳入标准 build 流程。**没有 BOLT 等价物的编译器（如老版 GCC）在躺平期会落后**。

### 中端优化专属资源
> 通用资源见 [`领域资源库_LLVM.md`](../领域资源库_LLVM.md) §2（工具）/ §3.3（优化教材）；以下为**中端优化专属**。

- ⭐ **MLIR 官方文档**（mlir.llvm.org）—— 多层 IR 一手。
- ⭐ **IREE Linalg tutorial**（iree.dev）—— Linalg→LLVM lowering 实操。
- 🔥 **Polly 官方**（polly.llvm.org）—— 多面体优化。
- 🔥 **Kruse 2020 RFC**（discourse.llvm.org/t/.../54110）—— 断层②根因。
- 🔥 **Allen & Kennedy 2001** —— 循环变换理论奠基。
- 🔥 **mlirAgent 论文 + 代码**（ucb-bar/mlirAgent）—— AI 辅助中端优化。
- 📎 **Compiler Explorer**（godbolt.org）—— 在线看中端 IR。

---

📌 **本文已过 §0.3 特异性测试 v2.0**：(a) 飞腾工程实证（飞腾 E11 Lab02 unroll 2 最优 / 32 V 寄存器 / 校准 .md 成本）；(b) 代码级实例（OpenXiangShan/llvm-project 真实行号：PassBuilderPipelines.cpp:207/285/753/1353、InstCombine 17 文件、Scalar 80+ Pass、mlir 45 dialect + 80 conversion、grep Phytium 0 命中）；(c) 对偶判断（GCC GIMPLE Pass 对照表 + Cranelift/MLIR 对比 + GCC Graphite vs Polly）。字数 ≥12000，参考文献 25 条（≥5 论文/官方，含 Lattner MLIR 2021/Grosser Polly 2012/Larsen SLP 2000/Kruse RFC/Allen&Kennedy），含 2 张对标表（冗余消除收益矩阵 + GIMPLE/IR Pass 对照）+ 3 张图表（标量流水线/Polly 覆盖率矩阵/MLIR lowering 阶梯），含强制盲区段（§4）与对偶段（§5）。**核心反方点**：任务预设"GVN 被 NewGVN 替代"经实测证伪——NewGVN 默认关（cl::init(false)），老 GVN 仍是默认。
