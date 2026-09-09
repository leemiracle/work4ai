# Lens_06 — 用教育学家的眼睛看 LLVM

> **范式**：Anderson & Krathwohl (2001) 修订版 Bloom 认知分类法 + Shulman (1986) 学科教学知识（PCK）+ Sweller (1988) 认知负荷理论（CLT）+ Bjork & Bjork (2011) "合意困难"（desirable difficulties）
> **为什么从业者看不见**：编译器工程师从 LLVM **内部**看它，天然认为这个"伟大工程"理所当然该教。他们看不见的是**教学翻译损耗**——一个生产级的、6 个月 release 一次的、API 漂移、抽象泄漏的工业代码库，作为**教学对象**有结构性缺陷：它让学生在 Bloom 的"应用"层极度高效（调 API 写 Pass），却绕过了"分析/评价/创造"层（从零设计一个 IR 的不变量）。从业者看不见"会写 Pass ≠ 理解编译器"，正如物理学家看不见"会用示波器 ≠ 理解麦克斯韦方程"。本透镜破解的同质化是：**所有专家都默认"LLVM 值得学 = LLVM 值得教"，而教育学家要问的是"值得学的东西怎么教才不害人"。**

---

## 1. 这个范式的核心逻辑（四个教育学镜头叠加）

教育学家不是"教 LLVM 的人"，而是"研究**学习如何发生**的人"。我用四个互补框架叠加，避免单一理论的盲区。

### 1.1 修订版 Bloom 分类法（Anderson & Krathwohl 2001）——认知金字塔

Anderson 对 Bloom 原版（1956）的关键修订：把"知识"维度独立成四类（事实/概念/程序/元认知），把"认知过程"维度重排为六层。这是评估"LLVM 教到哪一层"的尺子：

```
            ┌──────────┐
            │ 6 创造   │ ← 从零设计一个 IR / 写一个新后端 / 提出新优化
            ├──────────┤
            │ 5 评价   │ ← 判断 undef vs poison 谁对 / 评 New PM vs Legacy PM
            ├──────────┤
            │ 4 分析   │ ← 拆解 SelectionDAG 合法化流程 / 读 LangRef 推语义
            ├──────────┤
            │ 3 应用   │ ← 调 IRBuilder 写一个 Pass（Kaleidoscope 主战场）
            ├──────────┤
            │ 2 理解   │ ← 解释 SSA 是什么 / 解释 -O2 做了什么
            ├──────────┤
            │ 1 记忆   │ ← 背 IR 指令清单 / 背 Pass 名字
            └──────────┘
```

**核心命题**：好的编译教育应把学生推向第 4-6 层（分析/评价/创造）。LLVM 的官方资源（Kaleidoscope）主要服务第 3 层（应用），**这是它的成功，也是它的天花板**。

### 1.2 Shulman 的 PCK（Pedagogical Content Knowledge，1986）

Shulman 在《Those Who Understand》里提出：教师光有**学科知识（CK, Content Knowledge）**不够，还得有**把学科知识翻译成学生能学的东西的能力（PCK）**——即"知道学生会在哪里卡住、用什么类比、先教什么后教什么"。LLVM 的尴尬在于：**它的 CK 是世界顶级的（IR 设计、SSA、Pass 框架都是工程典范），但它的 PCK 是薄弱的**——Kaleidoscope 是工程师顺手写的"我怎么实现的"，不是教育学家设计的"学生该怎么学"。

### 1.3 Sweller 认知负荷理论（CLT, 1988）

Sweller 区分三种认知负荷：**内在负荷**（任务本身难，如 SSA 构造）、**外在负荷**（呈现方式带来的额外负担，如 CMake 工具链、版本不匹配）、**相关负荷**（促进图式建构的有益负荷）。Kaleidoscope 的最大教学问题是**外在负荷失控**：学生花在"装对 LLVM 版本、配 CMake、修 Chapter 4 编不过"的时间，远超花在"理解 SSA"上的时间（见 §2.1 实证）。

### 1.4 Bjork 的"合意困难"（desirable difficulties, 2011）

Bjork 父子的反直觉发现：**让学习"太顺"反而损害长期保持**。穿插测试、间隔练习、变换情境能提升长期记忆（"desirable difficulties"）。推论到编译教育：如果 LLVM 让学生"调个 API 就能生成代码"，这种**过度顺滑**可能让学生误以为"我懂了编译器"，实则只在第 3 层。真正深入的理解需要**合意困难**——比如从零实现一个寄存器分配器，被图着色算法的边界条件反复折磨。

**四框架叠加后的总命题**：LLVM 是编译教育的**双刃剑**——它在 Bloom 第 3 层（应用）和 PCK 的"降低入门门槛"上极其成功，但它的版本漂移制造外在认知负荷，它的"开箱即用"消解了合意困难，而它的官方教程 Kaleidoscope 因为"只有 double"无法触及第 4-6 层。它**帮了**编译教育的普及，却可能在**深度**上**害了**编译教育。

---

## 2. 用教育学看 LLVM：五个尖锐判断

### 2.1 判断一：Kaleidoscope 是入门金标准，也是入门陷阱

**结论：它是 LLVM 唯一的端到端官方教程，因此是事实上的"金标准"；但它的三个教学取舍让它同时是陷阱。**

**实证 1（双重门槛 a）**：本地 `OpenXiangShan/llvm-project/llvm/examples/` 共 13 个教学示例：

```
examples/
├── BrainF/          Brainfuck 解释器（展示 IR 构造）
├── Bye/             最小 plugin Pass
├── ExceptionDemo/
├── Fibonacci/       递归 Fibonacci（JIT）
├── HowToUseJIT/     老 JIT 入门
├── HowToUseLLJIT/   ORC LLJIT 入门
├── IRTransforms/    IR 变换示例
├── Kaleidoscope/    ⭐ 唯一端到端教程（Chapter2-9）
├── ModuleMaker/     最小 Module 构造
├── OptSubcommand/   opt 子命令
├── OrcV2Examples/   ORC JIT v2 系列
├── ParallelJIT/
└── SpeculativeJIT/
```
`[实测]` 只有 Kaleidoscope 是"从 lexer 到 JIT 的完整语言"，其余 12 个都是**片段**（一个 API 的最小用法）。所以 Kaleidoscope 承载了它不该独自承载的全部"端到端教学"压力——它一坏，LLVM 的官方教学入口就断了。

**陷阱 1：只有 double 一种类型。** 读本地 `examples/Kaleidoscope/Chapter2/toy.cpp`，lexer 里全局变量是 `static double NumVal;`，AST 节点是 `NumberExprAST(double Val)`。Kaleidoscope 官方文档直言（连城中译本与 Haskell 版 sdiehl 均保留此句）：

> "为了保持简单，Kaleidoscope 中唯一的数据类型是 64 位浮点类型（C 语言里的 `double`）。因此所有值隐式为双精度，语言不需要类型声明。"[官网教程]

**教育后果**：学生学完 Kaleidoscope 形成的心智模型是"编译器 = 词法 + 语法 + 生成 IR + 几个优化"，**完全绕开了类型系统、类型检查、指针、内存管理、调用约定**——而这恰恰是真实编译器 70% 的工程量。这是 Bloom 第 3 层（应用 IRBuilder）对第 4 层（分析类型系统设计）的**结构性回避**。学生带着这个模型去读 Clang 源码会直接崩溃。

**陷阱 2：版本漂移制造外在认知负荷。** Kaleidoscope 是"版本敏感"教程的活化石：
- LLVM 3.3：`llvm/DerivedTypes.h` → `llvm/IR/DerivedTypes.h` 路径迁移，教程网页与源码不一致 `[Discourse 2013]`
- LLVM 3.7：legacy JIT 移除后 Chapter 4+ **长期 broken**，直到 2015 年 Lang Hames 大修改用 ORC JIT `[llvm-commits 2015]`
- LLVM 3.9：`createBasicAliasAnalysisPass` 已不存在，教程未更新 `[Discourse 2017]`
- **LLVM 18（2024-10）**：还在修 Chapter 3 代码片段与完整代码不一致（PR #111289，`IRBuilder<>` 构造与 `getDoubleTy(TheContext)` vs `*TheContext`）`[GitHub PR]`

LLVM 是 6 个月 release 节奏（每年 3/9 月 `[官方]`）。一个中文社区作者 2024 年基于 LLVM 18 写的 Kaleidoscope 笔记，到 2026 年（LLVM 20）可能已经 API 不匹配。**领域资源库 §6.3-6.5 列举的数十篇中文 Kaleidoscope 笔记，绝大多数绑定了特定 LLVM 版本**——这正是 Sweller 说的"外在认知负荷"：学生还没理解 SSA，先被"为什么我的 Chapter 4 编不过"耗尽精力。

**陷阱 3：手写递归下降，掩盖了形式语言理论。** Chapter 2 的 parser 是纯手写 `ParseBinOpRHS`（运算符优先级递归下降），不碰 LR(1)/LL(1)/LALR，不碰 yacc/bison/antlr。**教学后果**：学生学完 Kaleidoscope 不知道"为什么要学龙书第 4 章的自动机理论"，因为 Kaleidoscope 让他们以为"手写 if-else 就能解析一切"。这是对 Bloom 第 2 层（理解形式语言本质）的绕过。

**对偶（门槛 c）**：GCC 没有 Kaleidoscope 等价物。GCC 的教学价值在于"读一个真实工业编译器源码"，但门槛极高（GENERIC/GIMPLE/RTL 三层 IR + C 宏地狱）。Rice 大学 Keith Cooper 的 COMP 412（*Engineering a Compiler* 教材的母课）用的是**自研的"Triples"教学编译器**，故意不碰 GCC/LLVM `[教材]`。所以 Kaleidoscope 的"唯一性"是 LLVM 相对 GCC 的**教学优势**，但也是它的**单点故障**。

### 2.2 判断二：龙书 vs LLVM——是互补，不是替代；但本科课都选"龙书精神 + 从零实现"

**结论：龙书在 Bloom 第 2/4 层（理解/分析理论），LLVM 在第 3/5 层（应用/评价工程）。Top 本科编译课**没有一所**用 LLVM 当主框架，因为"从零实现"才是第 6 层（创造）。**

**课程实证（门槛：联网核实课程主页，2025-2026 学年）**：

| 课程 | 学校/讲师 | 教材 | 学生实现的目标 | LLVM 角色 | Bloom 主战场 |
|------|----------|------|--------------|----------|:----------:|
| **15-411** Compiler Design | CMU / Seth Copen Goldstein（2026 Spring） | **虎书 ML 版**（Appel *Modern Compiler Implementation in ML*）`[官方slides]` | C0 子集 → x86-64（自选语言，OCaml 为主） | **可选 Lab 3.5**（把 L3 编译到 `.ll`，60 分） | 6 创造 |
| **6.110**（原 6.035）Computer Language Eng. | MIT（2025 Spring） | 自编讲义 | **Decaf**（类 Java）从零 → MIPS/x86 | **仅参考资源**（"gold mine of SSA optimizations"） | 6 创造 |
| **CS 164** Programming Languages & Compilers | UC Berkeley / Schasins（2025 Fall） | 自编讲义 | OCaml 手写 → **x86 汇编** | **完全不用** `[课程FAQ]` | 6 创造 |
| **CS143** Compilers | Stanford / Aiken 体系 | **龙书**（紫龙书 2nd，2006）"非必需，仅参考" `[lecture01]` | **Cool**（Classroom OO Lang）→ MIPS（SPIM 模拟器），C++ | **完全不用**（目标 MIPS） | 6 创造 |
| **CS 6120** Advanced Compilers | Cornell / Adrian Sampson（2025fa） | 无固定教材（论文驱动） | LLVM + **自研教育 IR "Bril"** | **核心**（Lesson 7 专讲，用"LLVM for Grad Students"教程）`[课程]` | 5 评价 + 研究 |

**这张表推翻了一个流行误判**：很多人以为"LLVM 已经成为编译教学事实标准"。**事实是——只有研究生课（Cornell CS 6120）深度用 LLVM**；四所顶尖本科课（CMU/MIT/Berkeley/Stanford）**全部坚持"从零实现"**，LLVM 最多是可选后端或参考资源。原因正是 §1 的教育学逻辑：

- **从零实现 = Bloom 第 6 层（创造）**，强制学生面对类型系统、寄存器分配、调用约定的**完整决策空间**；
- **用 LLVM = 停在第 3 层（应用 API）**，把最难的部分（后端、优化、代码生成）外包给 LLVM，学生学不到"为什么这样设计 IR"。

CMU 15-411 的设计最具教育学自觉：6 个 Lab 让学生从 L1（直线代码）逐步到 L4（内存），**每个 Lab 都要自己实现**，LLVM 只是一个"附加 Lab 3.5"——让学生**额外**体验"如果用工业 IR 会怎样"。这是**合意困难（从零）+ 工业对照（LLVM）**的教科书式平衡 `[CMU lab6llvm.pdf]`。

**龙书 vs LLVM 的真正分工**：龙书教**为什么**（自动机为何能解析、SSA 为何加速数据流、图着色为何是 NP-hard 但可启发式），LLVM 教**怎么做**（IRBuilder 怎么调、Pass 怎么注册、TableGen 怎么写）。**缺了龙书的"为什么"，学生只会调 API 不懂原理；缺了 LLVM 的"怎么做"，学生懂原理但不会落地。** 真正完整的编译教育是两者**强制互补**——这正是 CMU/Stanford 的做法（龙书/虎书 + 从零实现，LLVM 作对照）。

### 2.3 判断三：LLVM 是"研究生课事实标准"，不是"本科课事实标准"

接 §2.2 的证据。我把判断精确化，回应硬问题 3：

- **本科层（undergrad）**：LLVM **不是**事实标准。CMU/MIT/Berkeley/Stanford 四校 2025-2026 本科编译课，无一以 LLVM 为主框架。它们共享的设计哲学是"**学生自己造轮子**"——因为教育学的共识是：**没有比"亲手实现一遍"更强的合意困难**。
- **研究生层（grad/research）**：LLVM **是**事实标准。Cornell CS 6120 用 LLVM + Bril，UC Berkeley 的 PL 研究大量基于 LLVM/MLIR（如 §7.8 的 mlirAgent 出自 ucb-bar），博士生的"实现任务"普遍落在 LLVM 上。因为研究生已经过了"从零实现"的阶段，需要的是**可扩展的工业平台**做研究载体。

**这个分层的意义**：LLVM 的教学胜利是**选择性**的——它征服了研究生课和工业入门培训，却**没能**征服本科核心课。这恰恰说明教育学界对 LLVM 有清醒的警惕：**它太"好用"了，好用到会偷走学生从零实现的机会。**（Bjork 的"过度顺滑"警告）

### 2.4 判断四：工业工程债 vs 学术理论正确的撕裂——真实存在，且是 LLVM 教学的隐性毒药

**结论：LLVM 的几大工程债（undef/poison 演进、New PM 10 年迁移）在从业者看是"工程现实"，在教育学家看是"教学毒药"——因为学生学的"理论正确"和 LLVM 的"实际语义"对不上。**

**实证 1：undef → poison 的语义漂移。** 龙书/虎书教给学生的是**干净的未定义行为模型**：除以零 = UB，编译器可任意假设它不发生。但 LLVM IR 的现实是**两套并存的 UB 机制**：
- `undef`（早期）：一个"可以取任意值"的占位符，**非确定性**——同一个 undef 在不同使用点可取不同值，导致优化器可能推出矛盾。
- `poison`（2017- 推动迁移）：一个"一旦被使用就触发 UB"的传播性值，**确定性更强**，但 LangRef 长期两者并存 `[LangRef]`。

学生从龙书学到"UB 是一个清晰概念"，到 LLVM 发现有的优化在 undef 下正确、在 poison 下错误（或反之），需要读 Alive2（Lopes et al. POPL 2022 `[论文]`）这种形式化工具才能确证 Pass 正确性。**这就是 Bloom 第 5 层（评价）的撕裂**：学术教的"对错"是二值的，工业的"对错"取决于 undef 还是 poison 语义。学生从课堂到工业的落差，本质是**理论抽象 vs 工程债未清**的落差。

**实证 2：New PM 迁移债（本项目 Expert_03 已详述）。** Legacy PassManager → New PassManager 迁移**拖了 10 年**（约 2014-2024），中间 LLVM 13/14/15/16 的 Pass 写法 API 反复变。一个中文学生 2022 年学的 Legacy PM FunctionPass 教程（资源库 §6.3 Yuuoniy、§6.7 史宁宁），到 2026 年（LLVM 20，New PM 已是默认）**部分作废**。教育后果：**学生投资在一个会过期的 API 上**，这是 PCK 的灾难——教师不知道该教 Legacy 还是 New PM，学生不知道该学哪个。

**对偶（门槛 c）**：GCC 的 GIMPLE Pass 也演进，但 GCC 是**年度 release**（远慢于 LLVM 6 个月），API 相对稳定。所以"工程债作为教学毒药"这个问题，**LLVM 比 GCC 严重**——LLVM 的快节奏是工程优势（快速迭代），却是教学劣势（教程保鲜期短）。这是 Lens_02 Christensen 透镜看不见的：低端颠覆（模块化/快迭代）赢了市场，却把"教学稳定性"当代价付了。

### 2.5 判断五：AI 时代编译教育——LLM 能写 Pass，但不能让"学编译器"过时

**结论：LLM 已经能写简单的 Pass、能审 PR 找 bug，但**不能**替代编译教育的核心（不变量推理、抽象设计、正确性论证）。AI 时代编译教育不是"教得更少"，而是"教得更深"——把机械的 API 调用交给 AI，把"为什么"还给人类。**

**实证 1：LLM 写优化 Pass——有效但有天花板。** UC Berkeley 的 mlirAgent `[GitHub]`：LLM 引导 MLIR/LLVM 优化，binary size -8.78%（匹敌 Magellan/ICML 2025，且用 10× 更少迭代）。但论文实证："**LLM 不能替代编译器 Pass**"——Gemini 2.5 Pro 单独跑 -11.9%，**不如**专门的 Pass 流水线。结论是 LLM 是**辅助**而非**替代**。

**实证 2：LLM 审 PR 找 bug——已经进 LLVM 流程。** LLVM Discourse 2026-03 的"Automated review with agents" `[Discourse]`：AI 代理审查 207 个 PR，**每 PR 成本约 $2，发现 30+ 个真 bug**。这意味着：**LLM 已经能承担编译器代码审查的"机械部分"**（找内存泄漏、未初始化、API 误用）。

**教育推论（教育学家的关键判断）**：如果 LLM 能写 Pass、能审 PR，那编译教育该教什么？我的判断是——**回归 Bloom 第 4-6 层**：

| AI 能做的（第 1-3 层） | AI 暂时不能做的（第 4-6 层） |
|----------------------|---------------------------|
| 背 LangRef 指令清单 | 分析一个优化的**不变量**是否成立 |
| 写一个 boilerplate Pass | 评价 undef vs poison 哪个语义**更正确** |
| 调 IRBuilder 生成代码 | 从零**设计**一个 IR 的类型系统 |
| 找内存泄漏/未初始化 | 论证一个 Pass 在所有输入下**安全** |

**编译教育的核心从来不是"会用 IRBuilder"，而是"能判断一个变换是否保语义、能设计一个抽象是否完备"**——这正是 Alive2（形式化）、龙书（抽象解释/数据流理论）、虎书（类型系统）教的。AI 时代反而让这些**理论**价值回归：当 AI 包办了机械活，人类编译器工程师的不可替代性在于"**告诉 AI 什么是对的**"——而这需要深度理论训练。

**所以**：AI 时代编译教育**不是**要砍掉龙书改教 LLM 提示词，而是要**加强**龙书/虎书/形式化方法，同时**削减** Kaleidoscope 式的 API 跟读（因为那部分 AI 已能做）。这是一个反直觉但教育学上自洽的结论。

---

## 3. 对 LLVM 命运的具体预测/下注（强制可证伪）

> 教育学家透镜的预测聚焦"LLVM 作为教学对象的演化"，不是市场份额（那是 Lens_02/Lens_04 的事）。

**预测 1（Kaleidoscope 单点故障持续）**：到 **2028 年**，Kaleidoscope **仍是** LLVM 唯一的端到端官方教程，且**仍只有 double 一种类型**。理由：LLVM 社区是工程驱动非教育驱动，重写一个"多类型 + 稳定 API + 覆盖 SSA/类型检查/内存"的替代教程需要持续教学投入，而 LLVM Foundation 的资源优先投向工具链而非教学法。
- **可证伪**：若 2028 年前出现官方认可的 Kaleidoscope 替代品（如社区维护的"Kaleidoscope v2 with int/ptr"），本预测错。

**预测 2（本科课不投靠 LLVM）**：到 **2028 年**，美国 Top-5 本科编译课（CMU 15-411 / MIT 6.110 / Berkeley CS164 / Stanford CS143 / 任意 Cornell 本科编译课）**仍坚持"从零实现"为主框架**，LLVM 最多保持"可选后端/参考资源"地位。理由：教育学界的共识（§1.4 合意困难）不会因为 LLVM 更成熟而逆转——"从零实现"是 Bloom 第 6 层的唯一通道。
- **可证伪**：若上述任一课程在 2028 年前把主项目改成"在 LLVM 上加 Pass"，本预测错。

**预测 3（研究生课全面 LLVM/MLIR 化）**：到 **2027 年**，美国 Top-20 CS 院校的**研究生**编译/PL 课**超过 80%** 以 LLVM 或 MLIR 为实验平台（Cornell CS 6120 已是，UW/UCLA/CMU PhD 课跟进）。理由：研究生需要可扩展的工业平台做研究载体，AI 编译（MLIR/StableHLO）进一步强化这个趋势（§7.8）。
- **可证伪**：若研究生课出现"去 LLVM 化"（如改用 Cranelift/Rust 编译器教学），本预测错。

**预测 4（AI 审 PR 进核心流程，但不替代人类审查者）**：到 **2027 年**，LLVM **官方**采纳 AI 辅助 PR 审查作为标准流程（Discourse 90093 已验证可行性 `[Discourse]`），但**强制要求**至少一名人类 reviewer 懂所改模块的语义——因为 AI 找不到 undef/poison 这类语义级 bug。这反而**强化**了对"懂理论的审查者"的需求。
- **可证伪**：若 LLVM 出现"AI 全自动 merge"通道（无人类审查），本预测错。

---

## 4. 这个透镜与从业者视角的冲突（对偶，强制）

### 4.1 冲突点 1："LLVM 伟大" ≠ "LLVM 该这样教"

| 从业者（编译器工程师）视角 | 教育学家视角 |
|--------------------------|------------|
| LLVM 是工程奇迹，应该让更多人会用 | 工程奇迹作为**教学对象**有结构性缺陷，"会用"≠"理解" |
| Kaleidoscope 让无数人入门，功德无量 | 入门门槛低带来**虚假胜任感**（Dunning-Kruger），学生以为懂了实则停在 Bloom 第 3 层 |
| undef/poison 是工程演进的必经之路 | 工程演进对**学习者**是认知陷阱，学生不知道该学哪版语义 |

**这是本透镜最锋利的对偶**：从业者从"LLVM 的成功"推导"LLVM 教学的成功"，教育学家从"学习如何发生"发现"成功的工具≠好的教学素材"。两者都**对**，但在不同时间尺度上——短期看 LLVM 降低了入门门槛（从业者对），长期看它可能稀释了深度理解（教育学家对）。

### 4.2 冲突点 2：与 Lens_01 历史学家的对偶

- **Lens_01（历史学家）**：LLVM 颠覆 GCC 是"模块化 + 快迭代"的胜利，是编译器工业史的正剧。
- **Lens_06（教育学家）**：同一份"快迭代"恰恰是教学毒药——6 个月 release 让教程保鲜期短，Kaleidoscope 反复 broken。**颠覆者的工程优势，是教学者的工程劣势。** 这是同一现象的**两面**，没有谁对谁错，只有**利益相关方不同**（工业用户 vs 学生）。

### 4.3 冲突点 3：与 Expert_03 Pass Framework 的对偶

- **Expert_03（Pass 框架从业者）**：New PM 迁移拖 10 年是"工程现实"，LegacyPassManager.cpp 在 LLVM 23 仍 1734 行 `[本项目实测]`。
- **Lens_06（教育学家）**：同一个 10 年迁移，对学生是**API 不断过期的认知地狱**。资源库 §6.3-6.7 的中文 Pass 教程，从 Legacy FunctionPass 到 New PM `opt -passes=`，**至少经历 3 代写法**，每代绑死一个 LLVM 版本区间。从业者接受"债"，教育学家看到"债被转嫁给了学习者"。

### 4.4 一致点（非全是冲突）

教育学家与从业者**一致**认为：(1) LLVM IR 的 SSA 设计是世界级工程典范，值得学；(2) Kaleidoscope 作为入门**总比没有好**（GCC 连这个都没有）；(3) AI 辅助是好东西但需人类把关。分歧只在**深度与节奏**：从业者乐观（LLVM 越好教越好），教育学家审慎（要警惕"好用"偷走深度）。

---

## 5. 这个透镜的盲区与反方（诚实段，强制）

**盲区 1：教育学框架是西方理论，可能不适配中国教学情境。** Bloom/PCK/CLT/desirable difficulties 都源自北美教育心理学。中国编译教学的现实是"**做题导向 + 考研驱动 + 课时压缩**"——很多高校编译课被压缩到 32-48 学时，根本没空间"从零实现"，只能讲龙书理论 + 做几个 LLVM 小实验。在这种情境下，**LLVM 可能反而是"唯一可行"的教学路径**（因为它把工程量降下来了）。我用北美 Top-5 课的标准评判"从零实现更好"，可能**高估了**中国课堂的可行性。**反方**：一生一芯（§双重门槛 b）证明中国学生**能**做全栈从零实现，所以"课时不够"可能是个借口。

**盲区 2："从零实现更好"可能是个浪漫主义判断。** 反方论点：现代软件工程教育趋势是"**复用成熟组件**"而非"造轮子"。让学生在 LLVM 上加 Pass，可能比让他们写一个玩具编译器更贴近工业现实（工业里没人从零写编译器，都在 LLVM/GCC 上改）。我倾向于"从零实现"是基于 Bloom 第 6 层的考虑，但**如果**培养目标是"能用 LLVM 干活的应用工程师"而非"理解原理的研究者"，那 LLVM 式教学**更对**。本透镜隐含了"理解原理 > 会用工具"的价值排序，这是**可争议的**。

**盲区 3：我把 Kaleidoscope 的"只有 double"说成陷阱，但这是**教学取舍的合理结果**。** 一个端到端教程如果要覆盖 int/ptr/struct/类型检查/内存管理，篇幅会膨胀 5-10 倍，反而**更难**作为入门。反方：Kaleidoscope 的极简正是它传播广的原因——"只有 double"让它能在 9 章讲完。我的批评可能**忽视了教学经济学**（篇幅 vs 完整性的权衡）。

**盲区 4：我对 AI 时代编译教育的判断（"回归理论"）可能错。** 反方：也许未来编译教育会**完全重写**——不再教 SSA/LR(1)/图着色，而是教"如何用 LLM agent 编排编译器优化"（如 mlirAgent + mlir-opt-repl MCP server `[PR #203796]`）。如果"让 AI 写 Pass"成为主流技能，那龙书的理论可能像"手写汇编"一样变成少数专家的领域。我对"理论价值回归"的乐观，可能低估了 AI 对编译教育的颠覆速度。

---

## 6. 与其他视角对偶（一致 / 冲突，强制）

| 对偶视角 | 一致点 | 冲突点 |
|---------|-------|-------|
| **Lens_01 历史学家** | 都认为 LLVM 是里程碑 | 历史学家赞"快迭代赢市场"，教育学家批"快迭代害教学" |
| **Lens_02 Christensen** | 都承认 LLVM 模块化降低了门槛 | Christensen 看颠覆是纯收益，教育学家看到"门槛低"的认知代价 |
| **Expert_03 Pass 框架** | 都承认 New PM 迁移是真实工程现实 | 从业者接受"债"，教育学家看到"债转嫁给学习者" |
| **Expert_08 AArch64 后端** | 都承认"主线无 FTC86x 调度模型"是国产化痛点 | 教育学家补充：这也是**国产编译教学的反向锚点**——中国学生学 LLVM 后端找不到本国芯片案例 |
| **Lens_07 国产化** | 都关注中国编译人才缺口 | 国产化视角要"快速培养能用 LLVM 的人"，教育学家要"先打理论基础再上手"——节奏冲突 |

---

## 7. 参考文献（分级标注）

1. Anderson, L. W., & Krathwohl, D. R. (Eds.). (2001). *A Taxonomy for Learning, Teaching, and Assessing: A Revision of Bloom's Taxonomy*. Longman. —— 修订版 Bloom 分类法 `[教材]`
2. Shulman, L. S. (1986). "Those who understand: Knowledge growth in teaching." *Educational Researcher*, 15(2), 4-14. —— PCK 理论奠基 `[论文]`
3. Sweller, J. (1988). "Cognitive load during problem solving: Effects on learning." *Cognitive Science*, 12(2), 257-285. —— 认知负荷理论 `[论文]`
4. Bjork, R. A., & Bjork, E. L. (2011). "Making things hard on yourself, but in a good way: Creating desirable difficulties to enhance learning." *Psychology and the Real World*. —— 合意困难 `[教材]`
5. CMU 15-411/611 Compiler Design（2026 Spring, Seth Copen Goldstein）. [cs.cmu.edu/~411](https://www.cs.cmu.edu/~411/) ; Lab 6 LLVM handout [lab6llvm.pdf](http://www.cs.cmu.edu/~janh/courses/411/23/labs/lab6llvm.pdf). 教材 Appel *Modern Compiler Implementation in ML*. 访问 2026-07-07. `[课程]`
6. Cornell CS 6120: Advanced Compilers（Adrian Sampson, 2025fa）. [cs.cornell.edu/courses/cs6120](https://www.cs.cornell.edu/courses/cs6120/2025fa/) ; Lesson 7: LLVM. 访问 2026-07-07. `[课程]`
7. MIT 6.110 Computer Language Engineering（原 6.035, 2025 Spring）. [6110-sp25.github.io](https://6110-sp25.github.io/) ; Decaf 项目. 访问 2026-07-07. `[课程]`
8. Stanford CS143: Compilers. [web.stanford.edu/class/cs143](https://web.stanford.edu/class/cs143/) ; 龙书（紫龙书 2nd, 2006）[suif.stanford.edu/dragonbook](https://suif.stanford.edu/dragonbook/) ; Cool 语言 manual. 访问 2026-07-07. `[课程/教材]`
9. UC Berkeley CS164: Programming Languages and Compilers（Schasins, 2025 Fall）. [schasins.com/berkeley-cs164-fall-2025](https://schasins.com/berkeley-cs164-fall-2025/) ; FAQ 明确"OCaml → x86，不用 LLVM". 访问 2026-07-07. `[课程]`
10. LLVM Kaleidoscope Tutorial（官方）. [llvm.org/docs/tutorial/MyFirstLanguageFrontend](https://llvm.org/docs/tutorial/MyFirstLanguageFrontend/index.html). 连城中译 [llvm-tutorial-cn.readthedocs.io](https://llvm-tutorial-cn.readthedocs.io/). 访问 2026-07-07. `[官网]`
11. LLVM Discourse. "Kaleidoscope tutorial is out of date"（2013）[discourse.llvm.org/t/28226](https://discourse.llvm.org/t/kaleidoscope-tutorial-is-out-of-date/28226) ; "comments, corrections and Windows support"（2017）[discourse.llvm.org/t/43890](https://discourse.llvm.org/t/kaleidoscope-tutorial-comments-corrections-and-windows-support/43890). 访问 2026-07-07. `[Discourse]`
12. LLVM PR #111289. "[doc] Fix Kaleidoscope tutorial chapter 3 code snippet discrepancies"（2024-10）. [lists.llvm.org/.../1471491](https://lists.llvm.org/pipermail/llvm-commits/Week-of-Mon-20241007/1471491.html). 访问 2026-07-07. `[GitHub PR]`
13. llvm-commits. "Big update to Kaleidoscope tutorials"（Lang Hames, 2015-08）. [lists.llvm.org/.../295958](https://lists.llvm.org/pipermail/llvm-commits/Week-of-Mon-20150824/295958.html). 访问 2026-07-07. `[邮件列表]`
14. Lopes, N. P., et al. (2022). "Alive2: Bounded Translation Validation for LLVM." *POPL 2022*. —— undef/poison 形式化验证 `[论文]`
15. Cooper, K., & Torczon, L. (2022). *Engineering a Compiler* (3rd ed.). Morgan Kaufmann. Rice COMP 412 母教材. `[教材]`
16. 一生一芯（"YSYX"，包云岗团队，2019-）. [ysyx.oscc.cc](https://ysyx.oscc.cc/) ; CCD2025 导教班 [ccf.org.cn/.../845752](https://www.ccf.org.cn/Focus/2025-06-19/845752.shtml). 访问 2026-07-07. `[官方]`
17. 香山编译器 XSCC（基于 LLVM 的 RISC-V 编译器，2025-09）. [IT之家报道](https://www.ithome.com/0/883/720.htm). 访问 2026-07-07. `[报道]`
18. mlirAgent（UC Berkeley）. [github.com/ucb-bar/mlirAgent](https://github.com/ucb-bar/mlirAgent). 访问 2026-07-07. `[GitHub]`
19. LLVM Discourse. "Automated review with agents: ~30 bugs on 207 PRs"（2026-03）[discourse.llvm.org/t/90093](https://discourse.llvm.org/t/automated-review-with-agents-30-bugs-on-207-prs/90093). 访问 2026-07-07. `[Discourse]`
20. 本项目实测. `OpenXiangShan/llvm-project/llvm/examples/`（13 个教学示例 + Kaleidoscope Chapter2-9）`[实测]`

---

## § 范式方法论与资源（教育学透镜通用化）

> 本透镜不只用于 LLVM。任何"**工业级复杂系统作为教学对象**"的评估都可套用这套四框架。通用编译器教育资源见 [`../领域资源库_LLVM.md`](../领域资源库_LLVM.md) §3（教材）/§3.4（免费讲义）/§6（中文教程）/§8（视频课程），本节只补教育学方法论。

### §.1 四框架速查（教育学家工具箱）

| 框架 | 一句话 | 用来评估什么 | 经典出处 |
|------|-------|------------|---------|
| **修订版 Bloom** | 认知六层：记忆→理解→应用→分析→评价→创造 | 这个教学资源把学生推到第几层？ | Anderson & Krathwohl 2001 |
| **PCK** | 会 ≠ 会教 | 这个资源的"学科知识"强还是"教学知识"强？ | Shulman 1986 |
| **认知负荷 CLT** | 内在/外在/相关负荷 | 学生精力花在"学懂"还是"配环境"上？ | Sweller 1988 |
| **合意困难** | 太顺反而忘得快 | 这个资源是不是"过度顺滑"偷走了深度？ | Bjork & Bjork 2011 |

### §.2 评估任何"系统作为教学素材"的检查清单

1. **Bloom 定位**：它主要服务第几层？有没有通往第 6 层（创造）的通道？
2. **PCK 健康度**：它是"工程师顺手写的"还是"教育学家设计的"？学生卡点有没有被预见？
3. **外在负荷审计**：学生花多少时间在"装环境/配版本/修编译错误"而非"理解概念"？
4. **合意困难保护**：它是不是把最难的部分（后端/优化/类型）外包了，让学生失去"被折磨"的机会？
5. **版本稳定性**：它的 API 多久变一次？教程保鲜期多长？学生投资会不会过期？
6. **对偶存在性**：有没有"从零实现"的替代路径作为对照（如 Rice COMP 412 之于 GCC）？

### §.3 教育学透镜的局限（自反）

教育学透镜**默认**了"理解原理 > 会用工具"的价值排序，这在**应用型培养**（如飞腾招 NPU 编译器工程师要的是"能立刻上手 LLVM 后端移植" `[飞腾招聘]`）下可能**不成立**。用本透镜评估飞腾的 PhyCC/PhyGCC 教学价值时，要清醒：飞腾要的是"会用 LLVM 的工程师"而非"懂编译理论的研究者"，两者的教学法**本就该不同**。本透镜的"从零实现更好"判断，**在工业培训场景里应被悬置**。

---

> **一句话总结**：LLVM 帮了编译教育的**普及**（Kaleidoscope 让入门门槛史无前例地低），却可能在**深度**上害了编译教育（它的版本漂移制造外在负荷，它的开箱即用消解合意困难，它的"只有 double"绕开了类型系统这个核心）。教育学家对 LLVM 的判决不是"别教"，而是"**别只教 LLVM**"——本科课坚持从零实现（Bloom 第 6 层），研究生课放手用 LLVM/MLIR（第 5 层），AI 时代反而要**加强**龙书理论（因为机械活 AI 包办了，人类要负责"什么是对的"）。LLVM 是编译教育最锋利的**副武器**，但永远不该是**主武器**。
