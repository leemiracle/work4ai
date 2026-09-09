# AI for Compilers：从 MLIR / TVM 到 LLM 代码生成

> 卷：`08-ai4x-applications` · 第 3 章
> 主题：编译器基础设施的演进，以及机器学习如何渗透到编译优化的每一个层级——从 IR 设计、自动调度，到 LLM 直接生成代码与 Agent 自主修复工程问题。
> 状态：✅ 2026-07-20 完成。**所有 arXiv ID 一手核实**（共 14 个），并纠正任务大纲中 **4 处错误 ID**（详见文末勘误表）。

---

## 0. 为什么「AI4Compiler」是工程价值最高的方向之一

如果说 AI4Science 是「用 AI 找新材料、找新药」，那么 AI4Compiler 就是「用 AI 让 AI 自己跑得更快、让所有软件跑得更快」。这是一个**正反馈飞轮**：

```
更强的模型 → 更好的代码生成与编译优化 → 更快的训练/推理 → 更强的模型
```

它的工程价值体现在三个层面：

1. **杠杆极大**：编译器优化一个百分点，所有上层软件免费受益。Google 的 MLGO 把 LLVM 的二进制体积再压 7%，对部署在数十亿设备的 Chrome / Android 是天文级的收益。
2. **AI 自己受益**：PyTorch 2 的 `torch.compile`、TVM、Triton 这些工具，本质上都是「用程序去生成更快的程序」，而它们现在又被 LLM 加速。自举（bootstrapping）正在发生。
3. **离钱最近**：Codex / Copilot / Cursor / Devin 这一整条线，已经是一个数百亿美元的市场。它不是「未来可能有用」，而是「现在就在赚钱」。

本章按**时间线**和**抽象层级**两条线索展开：先讲清楚编译器本身的结构（这是理解一切优化的前提），再讲 ML 如何进入编译器的每一层，最后落到 LLM 时代最热的代码生成与软件工程 Agent。

---

## 1. 历史：从 GCC（1987）到 LLVM（2002）到 MLIR（2020）到 AI 时代

### 1.1 编译器的史前史与 GCC（1987）

编译器的历史几乎和计算机一样长。1957 年 IBM 的 John Backus 领导开发了 **FORTRAN 编译器**——这是第一个「把数学公式翻译成机器码」的实用编译器，Backus 因此获得 1977 年图灵奖。但真正把「编译器」变成一门可复用的**工程学科**的，是几个关键抽象的诞生。

1987 年，Richard Stallman 启动 **GNU Compiler Collection（GCC）**。GCC 的历史贡献不在于它支持了多少语言，而在于它**确立了「三段式编译器」的事实标准**：前端（Frontend）→ 中间表示（IR）→ 后端（Backend）。任何新语言只要写一个前端，就能复用 GCC 的优化器和所有后端；任何新硬件只要写一个后端，就能支持所有 GCC 前端语言。这种**关注点分离**让编译器的开发成本从「N×M」（N 种语言 × M 种硬件）降到了「N+M」。

### 1.2 LLVM（2002，Chris Lattner）——现代编译器的基石

GCC 虽然伟大，但它有一个致命的工程问题：它的 IR 和优化 pass 紧密耦合，且**整个编译器是一个不可拆分的庞然大物**——你很难把 GCC 的某个优化 pass 单独拿出来用在别处。2000 年，**Chris Lattner** 在伊利诺伊大学香槟分校（UIUC）读博，在导师 Vikram Adve 指导下设计了一个全新的编译基础设施 **LLVM**（Low Level Virtual Machine）。LLVM 的核心理念有三条：

1. **一切皆库**：优化 pass、IR、代码生成器都是独立的、可组合的、可重用的库（library），而不是一个 monolithic 的程序。你可以只链接你需要的 pass。
2. **SSA（静态单赋值）形式作为一等公民**：LLVM IR 从一开始就是 SSA 形式，每个变量只被赋值一次，这让数据流分析极其规整。
3. **IR 是一等可序列化对象**：LLVM IR 可以被写进文件（`.ll` 文本格式或 `.bc` 二进制格式），被读出来再优化。这意味着你可以「先编译到 IR，存盘，明天再优化」。

2005 年 Lattner 加入 Apple，LLVM 成为 Apple 工具链的根基（Clang、Swift 编译器都建立在 LLVM 之上）。今天，LLVM 是地球上**最重要的编译器基础设施**：Clang（C/C++）、Rust（rustc 后端）、Swift、Julia、Kotlin/Native、MLIR、PyTorch 的 GPU 后端……全都站在 LLVM 的肩膀上。2020 年图灵奖颁给 Lattner 与 Adve，表彰 LLVM。

### 1.3 MLIR（2020）——多层级 IR

LLVM 解决了「后端复用」问题，但它只有一个 IR 层级（接近机器的 LLVM IR）。到了 2010 年代，两个新趋势让单一 IR 不够用了：
- **深度学习编译**：从 TensorFlow 计算图到 LLVM IR 之间，差着好几个抽象层级（图级算子融合、循环级 tiling、向量级 SIMD），每一层都需要自己的优化，硬塞进一个 IR 会非常别扭。
- **异构硬件爆发**：CPU、GPU、TPU、FPGA、各种 AI 加速器，每种的内存模型和并行模型都不同。

2019 年，Lattner（此时在 Google）和 Mehdi Amini 等人发起了 **MLIR（Multi-Level Intermediate Representation）**。MLIR 的革命性在于：它不是一个具体的 IR，而是一个**制造 IR 的框架**——你可以用它的「Dialect」机制定义任意多层 IR，让它们在同一套基础设施里互相「lowering」（下降）。

> 论文：**MLIR: A Compiler Infrastructure for the End of Moore's Law**，Lattner, Amini, Bondhugula, Cohen, Davis, Pienaar, Riddle, Shpeisman, Vasilache, Zinenko（2020）
> [arXiv:2002.11054](https://arxiv.org/abs/2002.11054)

### 1.4 AI 增强时代（2018—）

当编译器基础设施（LLVM / MLIR）成熟之后，下一个问题是：**那些靠人写启发式（heuristic）的优化决策，能不能交给机器学习？** 编译器里到处都是这样的决策：

- 循环要不要展开？展开几层？
- 两个函数要不要 inline？
- 寄存器怎么分配？
- 算子 fusion 后的循环怎么 tile？

这些决策传统上是编译器专家**手写一堆 `if-else` 规则**来定的。它们是 NP-hard 的，启发式只在「常见情况」下好用。2018 年起，TVM 的 AutoTVM 开了先河：用机器学习学一个**代价模型（cost model）**来预测某个 schedule 的执行时间，从而在巨大的搜索空间里找到更优解。从此，「learned cost model + search」成了深度学习编译器的标配。再后来，LLM 直接登场，把「生成代码」这件事从「调启发式」变成了「让模型写」。

下面我们先把编译器的基本结构讲透——这是一切后续讨论的地基。

---

## 2. 编译器的基本结构：Frontend · IR · Optimizer · Backend

一个经典编译器可以抽象为四段流水线：

```
源代码 ──[Frontend]──► IR ──[Optimizer]──► 优化后的 IR ──[Backend]──► 机器码
       (parser/AST)        (一系列 pass)               (codegen)
```

### 2.1 Frontend（前端）

前端负责把人类可读的源代码变成机器可处理的中间表示。它通常分三步：

1. **词法分析（Lexing）**：把字符流切成 token。比如 `a = b + 1` 被切成 `[ID("a"), EQ, ID("b"), PLUS, INT(1)]`。工具：`flex`、手写 DFA。
2. **语法分析（Parsing）**：根据文法（grammar）把 token 序列组织成**抽象语法树（AST）**。这步要处理运算符优先级、结合性、递归下降。工具：`bison`（LALR）、ANTLR、现代编译器多用手写递归下降解析器（因为错误恢复更好）。
3. **语义分析**：类型检查、作用域解析、变量是否声明、函数签名是否匹配。这一步产出一个**带类型注解的 AST**，然后 lowering 到 IR。

GCC 前端是「一个语言一个」，Clang 是 C/C++/ObjC 的前端，Swiftc 是 Swift 前端——但它们都吐到同一个 LLVM IR。

### 2.2 IR（中间表示）

IR 是编译器的**心脏**。好的 IR 设计直接决定优化能做得多好。一个工业级 IR 通常具备：

- **SSA（Static Single Assignment）形式**：每个变量只被赋值一次。这听起来限制很大，但它让数据流分析（「这个值是从哪来的？」「它被谁用了？」）变得极其规整——因为定义-使用链（def-use chain）是显式的。LLVM IR、MLIR、Sea of Nodes（Graal）都是 SSA。**SSA 的核心数学结构是「支配树（dominator tree）」**：它刻画了「从入口到某点的所有路径都必经哪些节点」，是寄存器分配、循环分析的基础。
- **类型系统**：IR 也有类型（`i32`、`float`、指针、张量……），让优化能在类型层面做不变量推导。
- **可序列化**：能写进文件、能 round-trip（读出来和原来一样），方便调试和增量编译。

### 2.3 Optimizer（优化器 = 一堆 Pass）

优化器不是一个大函数，而是**一串 pass（遍）**，每个 pass 读进 IR、做一个变换、吐出新的 IR。pass 分两类：

- **分析 pass（Analysis Pass）**：不修改 IR，只计算并缓存一些信息（别名分析、支配关系、循环信息、活跃变量分析）。
- **转换 pass（Transformation Pass）**：真正改 IR。经典优化：

| 优化 | 作用 | 典型条件 |
|---|---|---|
| 常量折叠 | `1+2` → `3` | 编译期可算 |
| 死代码消除（DCE） | 删掉结果没被用的指令 | SSA 让这步极容易 |
| 公共子表达式消除（CSE） | `a=x+y; b=x+y` → `a=x+y; b=a` | 需要别名分析保证 `x,y` 不变 |
| 循环展开（Unroll） | 把循环体复制几遍 | 消除分支开销、增加 ILP |
| inline | 把函数调用替换为函数体 | 基于启发式决策 |
| 向量化（Vectorization） | 把标量运算改成 SIMD | 依赖数据依赖分析 |
| 循环不变量外提 | `for i: a = b*c; use(a)` → 外面算 | 需证明 `b*c` 循环不变 |

pass 之间有依赖：你得先跑「活跃变量分析」才能做「死代码消除」。编译器用一个 **pass manager** 来调度这些依赖。**「pass 顺序」本身就是一门艺术**——同样一批 pass，先跑谁后跑谁，结果性能可能差 10%。这正是机器学习想介入的地方（见 §5）。

### 2.4 Backend（后端 = Codegen）

后端把优化后的 IR 翻译成具体机器的汇编/机器码。它的核心步骤：

1. **指令选择（Instruction Selection）**：IR 操作映射到目标 ISA 指令（用 tree pattern matching 或 DAG 覆盖，如 LLVM 的 `SelectionDAG` / `GlobalISel`）。
2. **指令调度（Instruction Scheduling）**：安排指令顺序，利用流水线、避免数据 hazard。这是 NP-hard，传统用列表调度启发式。
3. **寄存器分配（Register Allocation）**：把虚拟寄存器映射到有限的物理寄存器，放不下的 spill 到内存。经典算法是**图着色（graph coloring）**——把「同时活跃的变量」连成边，给图着色，颜色数 ≤ 寄存器数。这同样是 NP-hard。

寄存器分配和指令调度**互相耦合**：调度影响活跃区间，活跃区间影响着色难度，着色结果又影响可用的调度自由度。这是后端优化最难的地方，也是 RL 想啃的硬骨头。

理解了这四段，下面所有「AI for X」的故事，本质都是「把 X 里的某个启发式，换成学习到的模型」。

---

## 3. MLIR：制造 IR 的框架

### 3.1 为什么需要多层级 IR

传统编译器是「单 IR」的：GCC 有 GIMPLE 和 RTL 两层，LLVM 主要用一层 LLVM IR。但深度学习场景里有**巨大的抽象跨度**：

- **最高层**：用户写的 PyTorch / TensorFlow / JAX 代码，是 Python 里的算子图。
- **图级**：`matmul → relu → matmul` 这种融合，发生在「图」抽象层。
- **循环级**：单个算子内部的多层 for 循环，要做 tiling、unroll、向量化。
- **向量级**：SIMD / 张量核指令。
- **最底层**：LLVM IR → 机器码。

如果只用一层 IR，要么高层抽象（算子）丢失（没法做图融合），要么低层细节（循环）和高层逻辑混在一起，优化 pass 写起来极痛苦。MLIR 的答案是：**让每层都有自己的 IR，让它们在同一套基础设施里互相 lowering**。

### 3.2 Dialect 系统

MLIR 的核心抽象是 **Dialect（方言）**。一个 dialect 定义一组操作（op）、类型、属性，相当于一个「命名空间」。例如：

- `linalg` dialect：结构化的线性代数算子（matmul、conv），描述「计算什么」。
- `affine` dialect：多面体循环结构，描述「循环怎么嵌套」。
- `vector` dialect：SIMD 向量操作。
- `gpu` / `nvvm` / `llvm` dialect：往硬件下降。

编译流程就是一连串 lowering：

```
用户模型 ──► linalg dialect ──► affine dialect ──► vector dialect ──► llvm dialect ──► 机器码
        (图级融合)        (循环 tiling)      (向量化)          (后端)
```

MLIR 的精妙之处在于：**每一层 lowering 都可以挂自己的优化 pass**，而且所有 pass 共用同一套基础设施（IR 文本格式、验证器、pattern rewriter、FileCheck 测试）。这把「构建一个领域专用编译器」的成本，从「从零造轮子」降到「定义一个 dialect + 复用基础设施」。

### 3.3 MLIR 在主流框架中的角色

- **TensorFlow / JAX**：XLA（Accelerated Linear Algebra）编译器内部大量使用 MLIR。JAX 的 `jit` 把 Python trace 成 HLO，再经 MLIR lowering 到硬件。
- **PyTorch（Torch-MLIR）**：社区项目，把 PyTorch 图翻译成 MLIR，再 lowering 到各种后端。
- **Flang（Fortran 编译器）**：LLVM 的 Fortran 前端，正逐步用标准 MLIR 重写其后端以获得性能。
- **硬件厂商**：NVIDIA、AMD、Intel、各种 TPU/NPU 厂商都把 MLIR 作为对接自家加速器的桥梁——定义一个「我的硬件 dialect」，从 `linalg`/`vector` lowering 下来。

MLIR 让「为一块新 AI 芯片写编译器」这件事，从「五年」缩短到「一两年」。这是它最大的工业价值。

---

## 4. TVM：深度学习编译器的开山之作

### 4.1 TVM 的核心思想：计算与调度分离

MLIR 是「通用编译基础设施」，而 **TVM**（Tensor Virtual Machine）是**专为深度学习设计的端到端编译器**。TVM 由陈天奇（Tianqi Chen）等人在 2018 年提出，核心理念来自 Halide：

> 论文：**TVM: An Automated End-to-End Optimizing Compiler for Deep Learning**，Chen, Moreau, Jiang, Zheng, Yan 等（2018）
> [arXiv:1802.04799](https://arxiv.org/abs/1802.04799)

TVM 把一个算子的实现拆成两部分：

- **Compute（计算）**：描述「算什么」——比如矩阵乘法 `C[i,j] = sum(A[i,k]*B[k,j])`。这是纯数学定义，不含任何循环结构。
- **Schedule（调度）**：描述「怎么算」——循环怎么分块（tile）、怎么并行、怎么向量化、数据怎么放进共享内存。这是性能优化的全部空间。

同一个 compute，配不同的 schedule，性能可以差 10-100 倍。TVM 用一种叫 **Tensor Expression（TE）** 的 DSL 让你写 compute，然后通过调度原语（`split`、`fuse`、`bind`、`cache_read`……）生成各种 schedule，再编译成 CUDA / LLVM IR。这种**计算与调度解耦**的思想，是整个深度学习编译领域的奠基性抽象。

### 4.2 AutoTVM：第一次把 ML 塞进编译器

但问题来了：schedule 的搜索空间是天文数字的。一个算子怎么 tile，有多少种组合？百万、千万级。靠人调不现实。TVM 的回答是 **AutoTVM**：

1. **定义模板**：人类专家给出一个 schedule 模板，里面留若干「可调旋钮」（tile size、unroll factor）。
2. **采样 + 实测**：在目标硬件上实际跑一批采样到的配置，记录真实执行时间。
3. **训练 cost model**：用这些实测数据训练一个**学习型代价模型（learned cost model）**，通常是 XGBoost 或一个小神经网络，输入 schedule 特征，预测执行时间。
4. **用 cost model 搜索**：cost model 推理比实测快几千倍，用它在大空间里快速筛选，再用实测验证 top-k。

这是「learned cost model + search」范式的**第一次大规模工业落地**。它的本质洞察是：**编译器优化里很多决策不是「对错」问题，而是「哪个更快」的预测问题——而预测正是 ML 最擅长的事。**

### 4.3 Ansor（AutoScheduler）：摆脱人工模板

AutoTVM 的局限在于：它依赖人类专家写 schedule **模板**。模板写得好不好，决定了搜索空间的质量。如果模板漏掉了某个高效 schedule 形态，AutoTVM 永远找不到它。2020 年 OSDI 上的 **Ansor**（后来集成进 TVM 成为 `AutoScheduler`）解决了这个问题：

> 论文：**Ansor: Generating High-Performance Tensor Programs for Deep Learning**，Zheng, Jia, Sun, Wu, Yu, Haj-Ali, Wang, Yang, Zhuo, Sen, Gonzalez, Stoica（OSDI 2020）
> [arXiv:2006.06762](https://arxiv.org/abs/2006.06762)

Ansor 不再依赖人工模板，而是用一个**分层的搜索空间表示**自动生成 schedule：它把算子的计算结构展开成一棵「调度树」，每层对应一类调度决策（要不要 tile、怎么并行），然后用**进化搜索 + 学习型 cost model** 在这棵树上探索。Ansor 能找到 AutoTVM 模板空间之外的更优解，在 Intel CPU / ARM CPU / NVIDIA GPU 上分别带来最高 3.8×、2.6×、1.7× 的加速。

Ansor 之后，社区又发展出 **MetaSchedule**（用 MLIR 的 TensorIR，更现代化）、以及 NVIDIA 的 **CUTLASS**、OpenAI 的 **Triton** 等竞争方案。但「learned cost model + search」这个核心范式，是它们共同的祖宗。

---

## 5. AI for Compiler Optimization：把启发式换成模型

TVM 的 AutoTVM 是「用 ML 学 cost model」。但编译器里还有大量**其他**决策也可以交给 ML。这一节按「优化对象」分类梳理。

### 5.1 学习循环变换（Learned Loop Transformation）

循环优化（tiling、unroll、interchange、fusion）是性能优化的重头戏。除了 TVM 这类「学 cost model」方案，学术界还探索了直接**用图神经网络（GNN）对程序做表征**的方法：把程序的控制流图 / 数据流图喂给 GNN，输出「该做哪些变换」的策略。难点在于：循环变换的效果高度依赖上下文（同一个 tile size 在不同代码里效果相反），模型必须理解程序的全局结构。

### 5.2 指令调度（Instruction Scheduling，RL）

后端的指令调度是经典 NP-hard 问题，传统用列表调度启发式。**强化学习（RL）** 在这里有天然优势：把「调度顺序」当作动作序列，把「执行时间 / 能耗」当作奖励，用策略梯度训练一个调度器。Meta（Facebook）开源的 **CompilerGym**（Hegedűs 等，ICLR 2022）把 LLVM 和 GCC 的多个优化决策包装成 RL 环境，让研究者可以像玩游戏一样训练编译优化策略。它提供了标准化的 observation（程序图）、action（选优化 pass）、reward（代码体积 / 运行时间下降），是这个方向最重要的基础设施。（注：CompilerGym 论文经检索未在 arXiv 以稳定 ID 命中，请按会议版本 ICLR 2022 检索。）

### 5.3 寄存器分配（Register Allocation，GNN）

寄存器分配的图着色本质是图问题，而**图神经网络天生适合处理图结构**。有研究把「干涉图」（interference graph，两个同时活跃的变量连边）喂给 GNN，输出每个变量该分到哪个寄存器或该 spill 到内存。相比启发式的线性扫描或图着色，GNN 能学到更细腻的权衡（比如「牺牲这个变量 spill，能换来后面三个变量都不用 spill」）。

### 5.4 Inlining / 向量化：MLGO——第一个进 LLVM 主线的 ML

**函数内联（inlining）** 决定要不要把函数调用展开成函数体——展开能消除调用开销、暴露更多优化机会，但会让代码体积膨胀。传统 LLVM 用一堆手写启发式（函数大小、调用深度、热点）。2021 年 Google 的 **MLGO** 把这个决策换成了机器学习模型：

> 论文：**MLGO: a Machine Learning Guided Compiler Optimizations Framework**，Trofin, Qian, Brevdo, Lin, Choromanski, Li（Google，2021）
> [arXiv:2101.04808](https://arxiv.org/abs/2101.04808)

MLGO 用两种算法（Policy Gradient 强化学习 + Evolution Strategies 进化策略）训练 inlining-for-size 模型，相比 LLVM 的 `-Oz`（最小体积）再压 **7%** 二进制体积。更重要的是，**这是第一个完整集成进工业级编译器（LLVM 主线）复杂 pass 的 ML 工作流**——意味着它不是论文 demo，而是真的在 Chrome、Android 里跑。它的关键工程经验：模型必须在一个语料上训练后，能泛化到「几个月后代码变了、目标也变了」的真实场景，否则没法落地。

下表对比这几条路线：

| 方向 | 传统方法 | ML 方法 | 代表 | 状态 |
|---|---|---|---|---|
| 张量调度 | 人工模板 / 库 | learned cost model + 搜索 | AutoTVM / Ansor | 工业级落地 |
| 指令调度 | 列表调度 | 强化学习 | CompilerGym | 研究为主 |
| 寄存器分配 | 图着色 / 线性扫描 | GNN | 学术原型 | 研究探索 |
| Inlining | 手写启发式 | RL / ES | MLGO | **LLVM 主线** |
| Pass 顺序 | 固定 pipeline | RL 排序 | CompilerGym | 研究探索 |

---

## 6. LLM for Code 详讲：从 Codex 到开源 SOTA

前面五节讲的是「ML 优化编译器内部决策」。这一节开始，我们进入**完全不同的范式**：用大语言模型（LLM）**直接生成代码**。这两件事经常被混为一谈，但它们的本质区别在于——前者是「替换编译器里的一个组件」，后者是「让模型当程序员」。

### 6.1 Codex（2021）：代码 LLM 的开端

> 论文：**Evaluating Large Language Models Trained on Code**，Mark Chen, Tworek, Jun 等（OpenAI，2021）
> [arXiv:2107.03374](https://arxiv.org/abs/2107.03374)

Codex 是 GPT-3 在 GitHub 公开代码上微调（fine-tune）的产物。它的历史地位在于：**它是第一个证明「LLM 能写出可运行代码」的工作**。论文同时发布了 **HumanEval** 基准——164 道 Python 编程题，每题给一个 docstring，让模型补全函数，然后跑单元测试判对错。这是代码生成领域最重要的 benchmark，至今仍是标配。

Codex 的几个关键发现：
- 在 HumanEval 上单次采样（pass@1）解决 **28.8%**，而 GPT-3 是 0%。
- **重复采样（repeated sampling）极其有效**：每题采样 100 次，能解决 **70.2%**。这意味着「模型不是不会，而是需要多试几次 + 一个筛选器」——这个洞察后来被 AlphaCode 发挥到极致。
- Codex 的生产版本驱动了 **GitHub Copilot**，开启了 AI 编程助手时代。

### 6.2 AlphaCode（2022）：竞赛级代码生成

> 论文：**Competition-Level Code Generation with AlphaCode**，Yujia Li, Choi, Chung, Kushman, Schrittwieser 等（DeepMind，2022，Science）
> [arXiv:2203.07814](https://arxiv.org/abs/2203.07814)

Codex 能做简单题，但**竞赛编程题**（需要算法推理、理解复杂题意）远超它的能力。AlphaCode 攻克了这个难度。它在 Codeforces 平台上达到 **top 54.3%** 的排名——这是首次 AI 在真实编程竞赛中达到人类中位水平。AlphaCode 的三个关键组件：

1. **大规模干净数据集**：从代码竞赛平台爬取并清洗训练数据。
2. **大规模采样**：对每道题生成**百万级**候选解。
3. **行为过滤（execution-based filtering）**：把候选解在样例上跑，只保留行为正确的，再去重。这一步是灵魂——它把「生成」和「验证」分离，用执行结果当过滤器。

AlphaCode 证明了：**代码生成的瓶颈不在模型多聪明，而在「怎么从海量候选里筛出对的」**。这个「generate-then-filter」范式成了后续所有竞技代码系统的模板。

### 6.3 开源浪潮：Code Llama、DeepSeek-Coder、StarCoder2

闭源模型（Codex、AlphaCode、GPT-4）很强，但不可复现、不可商用。2023-2024 年，开源社区掀起了一波**代码专用基础模型**浪潮。

**Code Llama（Meta，2023）** 基于 Llama 2，在代码上继续训练，提供 7B/13B/34B/70B 多个尺寸，支持 infilling（中间填空）和 16K-100K 长上下文。HumanEval 达到 67%。

> 论文：**Code Llama: Open Foundation Models for Code**，Rozière, Gehring, Gloeckle 等（Meta，2023）
> [arXiv:2308.12950](https://arxiv.org/abs/2308.12950)

**DeepSeek-Coder（DeepSeek，2024）** 是这一波的国产代表。1.3B-33B 多尺寸，在 2 万亿 token 的高质量**项目级**代码语料上从头训练，16K 窗口 + fill-in-the-blank。它在多项基准上不仅超越所有开源代码模型，还**超过 Codex 和 GPT-3.5**，并且许可证允许商用。

> 论文：**DeepSeek-Coder: When the Large Language Model Meets Programming -- The Rise of Code Intelligence**，Guo, Zhu, Yang 等（DeepSeek，2024）
> [arXiv:2401.14196](https://arxiv.org/abs/2401.14196)

**StarCoder 2（BigCode，2024）** 是 HuggingFace + ServiceNow + NVIDIA 合作的 BigCode 项目产物。它的最大贡献在**数据透明度**：训练数据 The Stack v2 建立在 Software Heritage 的数字公地之上，发布每一条源代码的持久标识符（SWHID），让数据可审计、可追溯——这是对「代码 LLM 训练数据是否合法」这个争议的技术回应。

> 论文：**StarCoder 2 and The Stack v2: The Next Generation**，Lozhkov, Li, Ben Allal 等（BigCode，2024）
> [arXiv:2402.19173](https://arxiv.org/abs/2402.19173)

| 模型 | 机构 | 年份 | 尺寸 | 关键特性 | arXiv |
|---|---|---|---|---|---|
| Codex | OpenAI | 2021 | ~12B | 代码 LLM 开端 + HumanEval | 2107.03374 |
| AlphaCode | DeepMind | 2022 | 41B | 竞赛级 + 行为过滤 | 2203.07814 |
| Code Llama | Meta | 2023 | 7-70B | infilling + 长上下文 | 2308.12950 |
| DeepSeek-Coder | DeepSeek | 2024 | 1.3-33B | 项目级语料 + 商用 | 2401.14196 |
| StarCoder 2 | BigCode | 2024 | 3-15B | 数据透明 + SWHID | 2402.19173 |

国产的 **Qwen-Coder / Qwen2.5-Coder**（阿里）也是开源代码模型的第一梯队，在 HumanEval / MBPP 等基准上屡刷 SOTA，许可证开放，是国内开发者最易获取的强代码模型。

---

## 7. LLM 用于反编译（Decompilation）

### 7.1 反编译是什么，为什么难

**反编译**是编译的逆过程：把机器码 / 二进制还原成可读的高层源代码。它在安全分析（逆向恶意软件、漏洞挖掘）、遗留系统维护、跨平台移植里极其重要。传统工具（**Ghidra** / IDA Pro / Hex-Rays）能做，但产出质量很差——主要因为这些**信息在编译时已经丢失**：

1. **变量名**：源码里的 `user_count` 编译后变成寄存器 `r5` 或内存 `[rbp-8]`，名字信息全没了。
2. **类型信息**：`int`、`struct`、`enum` 在机器码里都是位模式，得反推。
3. **控制流结构**：源码的 `if/else/for/while` 被编译成跳转指令（`jmp`、`je`），要从跳转图恢复出高级结构。
4. **可执行性**：反编译出来的代码常常不能直接重新编译运行（变量类型对不上、指针语义丢失）。

传统反编译的核心是**图论算法**：从指令流构建控制流图（CFG），做支配关系分析识别循环，用结构化算法恢复 if/while。但「猜变量名、猜类型」基本靠启发式，产出像天书。

### 7.2 LLM4Decompile：用 LLM 翻译二进制

LLM 的出现给了反编译一条新路径：把它当成**机器码到源码的翻译任务**（就像英译中）。**LLM4Decompile** 是第一个大规模开源的反编译专用 LLM 系列（1.3B-33B）：

> 论文：**LLM4Decompile: Decompiling Binary Code with Large Language Models**，Tan, Luo, Li, Zhang（EMNLP 2024）
> [arXiv:2403.05286](https://arxiv.org/abs/2403.05286)

LLM4Decompile 有两种用法：
- **End 模式**：直接吃二进制（汇编文本），吐源码。
- **Ref 模式**：先用 Ghidra 反编译，得到一个粗糙版本，再让 LLM **refine**（精修）。

在 HumanEval-decompile 和 ExeBench 上，LLM4Decompile 的**可重新执行率（re-executability）**比 GPT-4o 和 Ghidra 高出 100% 以上；Ref 模式比 End 模式再提升 16.2%。这说明：**反编译的最佳路径不是「扔掉传统工具全靠 LLM」，而是「传统工具 + LLM 精修」的混合管线**——这正是 §15 用户建议里强调的「AI 不是替代工程，而是增强工程」。

---

## 8. AI for Program Synthesis（程序合成）

在 LLM 之前，程序合成（program synthesis）是一个有几十年历史的领域。它的目标比「代码生成」更严格：**给定一个规约（specification），自动合成满足它的程序**。规约有三种形态：

- **输入-输出示例（examples）**：「给你 `([1,2,3], 6)` 和 `([4,5], 9)`，猜一个返回列表求和的函数」。这叫 **programming by example (PBE)**。
- **形式逻辑规约**：用一阶逻辑 / 时序逻辑描述程序应满足的性质。
- **自然语言描述**：「写一个判断回文的函数」——这才是 LLM 时代的主战场。

### 8.1 FlashFill（2011）：程序合成的工程巅峰

> 论文：**FlashFill（Excel 中的智能填充）**，Sumit Gulwani（Microsoft Research，2011，POPL；后续 CACM 2012）
> 注：FlashFill 无 arXiv 版本，按 POPL 2011 / CACM 2012 引用。Sumit Gulwani 因此获 2019 年 ACL 受邀演讲等多项荣誉。

FlashFill 是程序合成最成功的**工业落地**——它就是 Excel 里那个「你拖一下填充柄，它猜出你想做的变换」的功能。用户给几个示例（比如 `"(123) 456-7890"` → `"1234567890"`），FlashFill 秒级合成一个字符串处理程序。它支撑了 Excel 数十亿用户每天的使用，是程序合成领域「真的赚到钱、真的有人用」的标杆。

FlashFill 的技术核心是**基于演绎的枚举搜索 + 领域专用 DSL**：在一个精心设计的字符串变换 DSL 上，用类型引导的搜索快速枚举候选程序，用示例过滤。它的成功靠的不是「模型多强」，而是「**问题定义得多窄**」——把范围限制在字符串变换 DSL 上，搜索空间可控，工程上才可行。

### 8.2 DeepCoder（2016）：神经网络增强搜索

DeepCoder 把神经网络的预测能力注入传统的枚举搜索：

> 论文：**DeepCoder: Learning to Write Programs**，Balog, Gaunt, Brockschmidt, Nowozin, Tarlow（Microsoft Research Cambridge，ICLR 2017）
> [arXiv:1611.01989](https://arxiv.org/abs/1611.01989)

DeepCoder 的洞察：给定输入-输出示例，训练一个神经网络**预测「目标程序可能用到哪些 DSL 操作符」**（比如「这道题大概要用 `sort` + `map` + `sum`」）。用这个预测去**裁剪搜索空间**——只在预测出来的操作符子集里搜索。这把传统枚举搜索加速了一个数量级。DeepCoder 确立了「**神经网络做引导 + 经典搜索做骨架**」的范式，和 AlphaCode 的「generate-then-filter」异曲同工：都是把 ML 用在搜索的某一段，而不是替换整个搜索。

### 8.3 跨域合成

程序合成的现代方向包括：用 LLM 直接从自然语言生成程序（这就是 §6 的代码生成）、用 LLM 辅助形式化方法的合成（如 sketch-based synthesis）、以及用执行反馈迭代修正（self-repair，见 §9）。趋势很清晰：**纯粹的符号搜索太慢，纯粹的 LLM 太不可靠，混合管线是未来**。

---

## 9. AI for Program Repair（自动程序修复）

**自动程序修复（Automated Program Repair, APR）** 的目标：给定一段有 bug 的代码（+ 可能的测试用例 / 错误信息），自动生成修复版本。它分几代：

1. **基于搜索**：从「正确代码库」里找相似的，移植过来（代表：GenProg）。
2. **基于约束**：把 bug 局部化，用形式约束求解「该改成什么」（代表：SemFix、Angelix）。
3. **基于学习**：用神经网络学「buggy → fixed」的映射。

### 9.1 AlphaRepair：transformer 当修理工

> 论文：**A Transformer-Based Approach for Source Code Repair**（系统名 **AlphaRepair**），Michael Fu, Chakkrit Tantithamthavorn（Monash University，ASE 2022）
> 引用：DOI [10.1145/3551349.3556960](https://doi.org/10.1145/3551349.3556960)
> ⚠️ 注：AlphaRepair **无 arXiv 版本**（任务大纲给的 `2110.10885` 实为一篇代数拓扑的同调论文，已弃用，详见文末勘误）。

AlphaRepair 把程序修复建模成**掩码语言模型填空**：把 buggy 行 mask 掉，让 transformer 预测正确内容。它属于「learning-based」第三代，特点是**不需要测试用例驱动搜索**，直接靠模型从大量代码里学到的「正确模式」补全。局限是：当 bug 涉及多行、跨文件的逻辑改动时，单行 mask 不够用——这推动了后续的 **multi-line repair** 和基于 Agent 的修复（见 §11）。

### 9.2 LLM 时代的修复：从单行到仓库级

GPT-4 / Claude 出现后，APR 进入了「**让模型直接改，再用测试验证**」的阶段。一个关键发现（Olausson 等，ICLR 2024）是：**LLM 的自我修复（self-repair）效果，被「模型能不能准确评估自己的代码」这个瓶颈卡住**——如果用更强的模型提供反馈，self-repair 收益大增；让模型自己评估自己，收益常常有限甚至为负。这解释了为什么 Devin / Cursor 这类 Agent 必须接真实的执行环境（编译器、测试）当裁判，而不是相信模型的自我判断。

---

## 10. AI for Formal Verification（形式化验证）

形式化验证用数学方法证明程序 / 协议满足某性质，是软件可靠性的终极武器。它与编译器有两个交集：

### 10.1 编译器自身的正确性

编译器是「所有软件都依赖的底层」，所以**编译器本身的 bug 危害极大**——它会把你正确的源代码编成错误的机器码。证明编译器正确（**verified compiler**）是形式化方法的高地，代表是 **CompCert**（用 Coq 证明的 C 编译器，Xavier Leroy，2016 POPL 奠基性工作）。CompCert 证明了「源程序语义 ⟹ 编译后机器码语义」的保持，是程序语言理论（PLT）与形式化方法结合的丰碑。但 CompCert 的性能和功能都不如 GCC/LLVM，工业采用有限——**正确性和实用性之间的张力，是这个领域永恒的主题**。

### 10.2 SMT solver + ML：编译优化的形式后盾

编译器优化要保证「优化前后语义等价」，这需要**等价性检查（equivalence checking）**，背后是 **SMT solver**（Satisfiability Modulo Theories，如 Z3、CVC5）。SMT solver 解决「这个逻辑公式可不可满足」的问题，是连接「程序」和「数学」的桥梁。

ML 正在加速 SMT 求解：用 GNN / transformer 预测「哪个启发式、哪个分支、哪个公理优先」，能在难题上把求解时间砍几个数量级。这与本卷 `03-ai4math/01-formal-proof` 章节强相关——**AlphaProof（DeepMind，IMO 2024 银牌）用 Lean + RL 证明数学定理，其底层就是「ML 引导的形式化搜索」，和 ML 引导的编译器优化共享同一套思想**。

> 一句话总结这个共性：无论是「证明定理」「调度指令」还是「着色寄存器」，本质都是在巨大的搜索空间里找解——而 ML 的价值就是**用学到的先验，把搜索引导到正确的子空间**。

---

## 11. IDE 集成与 Agent：从补全到自主工程师

### 11.1 第一代：行内补全（Copilot, 2021—）

GitHub Copilot（Codex 驱动）开启了 IDE 内嵌 AI 的时代。它的形态是**幽灵代码（ghost text）**：你写到一半，它灰色提示补全，按 Tab 接受。这一代的价值是「减少打字量」，本质是**单点预测**。Continue、Tabnine、Codeium 等同类产品都属此列。

### 11.2 第二代：对话式编辑（Cursor, Continue, Aider）

第二代把 LLM 从「补全工具」升级成「**可对话的编辑伙伴**」。代表是 **Cursor**（Anysphere）和开源的 **Continue** / **Aider**。它们的核心能力：

- **Chat about code**：选中一段代码问「这段为什么慢？」
- **多文件编辑**：描述「把这个 API 从 REST 改成 GraphQL」，它跨多个文件改。
- **Cursor Composer / Aider**：进入「**agent 模式**」——给一个任务，它自己规划、改代码、跑测试、根据错误反馈迭代。

Aider 的设计尤其值得学：它把每次修改做成 **git commit**，让 AI 的改动可审计、可回滚——这是「让 AI 写代码」能工程化的关键纪律（参见你的 `agent-guide` 项目里关于 Agent 可控性的反复强调）。

### 11.3 第三代：自主软件工程 Agent（Devin, Cognition）

第三代是 2024 年爆发的「**AI 软件工程师**」：**Devin**（Cognition）、**SWE-agent** 等。它们的目标不是「帮你写一段代码」，而是「**自主解决一个完整的工程 issue**」——读 issue、浏览代码库、定位 bug、写补丁、跑测试、提交 PR。

SWE-bench 是衡量这一代能力的标尺：

> 论文：**SWE-bench: Can Language Models Resolve Real-World GitHub Issues?**，Jimenez, Yang, Wettig, Yao, Pei, Press, Narasimhan（Princeton，ICLR 2024）
> [arXiv:2310.06770](https://arxiv.org/abs/2310.06770)

SWE-bench 从 12 个流行 Python 仓库的真实 GitHub issue + 对应 PR 构造了 2294 道题：给模型一个代码库 + issue 描述，让它改代码并通过测试。论文发布时（2023-10），最强的 Claude 2 只解出 **1.96%**——真实工程问题对 LLM 是降维打击式的难。

SWE-agent 的贡献是提出了 **Agent-Computer Interface（ACI）**：

> 论文：**SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering**，Yang, Jimenez, Wettig, Lieret, Yao, Narasimhan, Press（2024）
> [arXiv:2405.15793](https://arxiv.org/abs/2405.15793)

它的洞察是：**Agent 用什么接口去操作电脑，极大影响性能**。SWE-agent 设计了专门的 ACI（文件编辑、仓库导航、命令执行的定制接口），用 GPT-4 把 SWE-bench 解题率提到 **12.5%**。论文的核心教训是——**「界面设计」是 Agent 时代的「API 设计」**，给 AI 用的工具，要在「信息密度」和「可操作性」上专门优化，而不是直接复用人类用的 IDE。

| 代际 | 形态 | 代表 | 自主度 | 时间 |
|---|---|---|---|---|
| 1 | 行内补全 | Copilot, Codeium | 极低（预测） | 2021 |
| 2 | 对话编辑 | Cursor, Continue, Aider | 中（可多文件） | 2023 |
| 3 | 自主 Agent | Devin, SWE-agent | 高（自主解决 issue） | 2024 |

---

## 12. AI for Compiler 测试与验证

编译器这么复杂，**怎么测它没 bug**？这是编译器工程的核心难题。AI 在这里有两条进路。

### 12.1 Fuzzing：随机生成测试程序

**Csmith**（Yang 等，PLDI 2011）是这个方向的里程碑。它是一个**能随机生成「合法且对编译器有挑战」的 C 程序**的工具——生成的程序要语法合法、定义良好（无 UB），且故意包含能触发各种优化路径的结构（深度嵌套循环、复杂表达式、位运算）。然后用「**差分测试（differential testing）**」：同一个程序用 GCC、Clang、不同优化级别编译，跑出来结果应该一样；不一样就说明某个编译器有 bug。Csmith 在 2000 年代帮 GCC 和 LLVM 找到了**几千个**优化器 bug。

**Yarpgen** 是另一个类似的随机程序生成器，专门针对中端优化。LLM 现在也被用来做 fuzzing：2024 年的「Finding Missed Code Size Optimizations in Compilers using LLMs」（Italiano & Cummins，CC 2025，arXiv:2501.00655）用现成的 LLM 生成随机代码，再用差分测试找「编译器没做好的优化」——仅 150 行代码，就在 C/C++/Rust/Swift 编译器里找到 24 个确认 bug。LLM 当 fuzzer 的优势是：它能生成「更像真实代码」的样本，覆盖人类写的规则生成器想不到的角落。

### 12.2 Equivalence Checking

更严格的方法是**形式化地证明「优化前后语义等价」**。对每个优化 pass，把变换前的 IR 和变换后的 IR 喂给 SMT solver，问「是否存在一个输入让两者行为不同」。这在工业编译器里用于关键优化 pass 的验证。ML 在这里加速 SMT 求解（§10.2）。

---

## 13. JIT 编译与 AI：torch.compile / JAX / Triton

前面讲的都是「**提前编译（AOT）**」——`gcc a.c` 一次性编译完。但 Python 生态主导的深度学习，大量使用**即时编译（JIT）**：运行时才把 Python / 计算图编译成优化后的机器码。这一节讲三大 JIT 生态。

### 13.1 PyTorch 2.x：`torch.compile`

PyTorch 历史上是「动态图 + eager 执行」——每行算子在 GPU 上立刻跑，没有全局优化。这在易用性上无敌，但性能被 TensorFlow 的静态图（XLA）甩开。PyTorch 2.0 的 `torch.compile`（由 TorchDynamo + TorchInductor 组成）解决了这个矛盾：

```python
import torch
model = MyModel()
model = torch.compile(model, mode="max-autotune")  # 一行，性能起飞
```

它的工作流：
1. **TorchDynamo**：在运行时 hook Python 字节码，把 Python 计算图 trace 出来（用 frame guard 保证安全）。
2. **TorchInductor**：把图 lowering 成 Triton（GPU）或 C++（CPU）代码，再做融合、调度优化。
3. `mode="max-autotune"` 还会触发 AutoTVM 风格的 kernel 搜索。

`torch.compile` 的意义：它把「用编译器优化 AI 模型」这件事，从「专家手写 CUDA kernel」变成了「一行 Python 调用」。它是 MLIR/Triton/AutoTVM 这些技术对普通用户的最终封装。（torch.compile 的系统论文经检索未在 arXiv 以稳定 ID 命中，主要文档见 PyTorch 官方 blog 与 TorchInductor 设计文档。）

### 13.2 JAX：`jit` + `vmap` + `pmap`

JAX（Google）从一开始就是「**函数式 + 可微 + 可编译**」的设计。它的核心是三个变换高阶函数：

- `jit(f)`：把函数 `f` JIT 编译（trace 成 HLO → XLA → MLIR → 硬件）。
- `vmap(f)`：自动向量化（把「处理一个样本」的函数变成「处理一个 batch」，无需手写 batch 维度）。
- `pmap(f)`：跨设备并行（把函数分布到多 GPU/TPU）。

JAX 的设计哲学是「**把硬件细节藏在纯函数变换后面**」——你写的代码是数学，编译器负责把它映射到任何硬件。这和 TVM 的「compute/schedule 分离」、MLIR 的「多层级 lowering」是同一种思想的不同表达。

### 13.3 Triton（OpenAI）：GPU kernel 的 Python DSL

写高性能 CUDA kernel 是个苦活——要手动管线程块、共享内存、bank conflict。**Triton**（Philippe Tillet 等，OpenAI）的定位是「**用 Python 写 GPU kernel，编译器帮你并行化**」：

```python
import triton
import triton.language as tl

@triton.jit
def add_kernel(x_ptr, y_ptr, out_ptr, N, BLOCK: tl.constexpr):
    pid = tl.program_id(0)
    offs = pid * BLOCK + tl.arange(0, BLOCK)
    mask = offs < N
    x = tl.load(x_ptr + offs, mask=mask)
    y = tl.load(y_ptr + offs, mask=mask)
    tl.store(out_ptr + offs, x + y, mask=mask)
```

你写的是「**块级（block-level）**」逻辑——每个 program 处理一个 BLOCK，Triton 编译器负责把这个块级逻辑映射到 GPU 的线程层级（自动处理线程分块、共享内存、向量化）。这让写 GPU kernel 的门槛从「CUDA 专家」降到「会写 Python for 循环」。

Triton 是当今最重要的 GPU 编程抽象之一：**FlashAttention、vLLM 的 PagedAttention、PyTorch Inductor 的 GPU 后端，全都建立在 Triton 之上**。它和 TVM/MLIR 的关系是互补的——Triton 给「人」用（写 kernel），TVM/Ansor 给「搜索器」用（找 schedule）。（Triton 无正式 arXiv 论文，按 OpenAI blog 与 GitHub `openai/triton` 引用。）

---

## 14. 2025-2026 关键论文与前沿

代码 Agent 这条线在 2025-2026 进展极快。SWE-bench 从 2023 年的 1.96%（Claude 2），到 2024 年的 12.5%（SWE-agent），到 2025 年的**数倍提升**——闭源强模型（Claude 3.5/4、GPT-4.x 系列）配合更好的 Agent 框架，在 SWE-bench Verified 上已达到人类工程师可观的通过率（具体数字请以 swebench.com 官方 leaderboard 实时为准，本卷不臆造具体百分比）。

一个值得关注的 2025 年末方向是**论文到代码库的自主复现（paper-to-codebase synthesis）**：

> 论文：**DeepCode: Open Agentic Coding**，Li, Li, Guo, Ren, Huang（HKUDS，2025-12）
> [arXiv:2512.07921](https://arxiv.org/abs/2512.07921)

DeepCode 把「论文复现」建模成一个**信息流管理问题**：在有限的上下文预算下，最大化任务相关信号。它用四类信息操作——源压缩（蓝图蒸馏）、结构化索引（有状态代码记忆）、条件知识注入（RAG）、闭环纠错——在 **PaperBench** 基准上达到 SOTA，超过了 Cursor、Claude Code 等商业 Agent，并在关键复现指标上**超过顶尖机构的博士级人类专家**。这预示着 2026 年的一个趋势：**Agent 不再只是「写代码」，而是「做科研复现」甚至「做科研」**——这正好呼应本卷 `02-ai4science` 的主题。

其他 2025-2026 热点（描述为主，未逐条核实 arXiv ID，按会议/blog 检索）：多模态代码 Agent（看截图改前端）、长上下文仓库级理解（100万+ token 处理整个 monorepo）、Agentic 调试（Agent 主动跑、主动读 trace）、以及「**模型自己训模型**」的自举实验（用代码 Agent 改训练脚本再训练下一代）。

---

## 15. 代码示例：用 LLM 思维生成一个 CUDA kernel

让我们用一个具体例子，把本章的几个概念串起来。任务是**实现一个「softmax」GPU kernel**——这是 LLM 训练里最基础的算子之一。

**第一步：理解算子（compute）**
```
softmax(x_i) = exp(x_i) / sum_j exp(x_j)
```
为了数值稳定，先减去最大值：`softmax(x_i) = exp(x_i - max) / sum_j exp(x_j - max)`。

**第二步：用 Triton 写 block-level kernel（schedule 由编译器补）**

```python
import triton, triton.language as tl

@triton.jit
def softmax_kernel(x_ptr, out_ptr, n_cols, BLOCK: tl.constexpr):
    # 每个程序处理一行的 BLOCK 个元素
    row = tl.program_id(0)
    offs = tl.arange(0, BLOCK)
    mask = offs < n_cols
    x = tl.load(x_ptr + row * n_cols + offs, mask=mask, other=-float('inf'))

    # 数值稳定：减最大值
    x = x - tl.max(x, axis=0)
    num = tl.exp(x)
    den = tl.sum(num, axis=0)
    out = num / den

    tl.store(out_ptr + row * n_cols + offs, out, mask=mask)
```

**第三步：理解它背后的编译流水线**
1. `@triton.jit` 把这个 Python 函数 trace 成一个 IR。
2. Triton 编译器把「BLOCK 级逻辑」lowering 到「线程级 CUDA」（自动分配 warp、处理共享内存、向量化 `exp`）。
3. 最终生成 PTX / SASS 机器码跑在 GPU 上。

**第四步：用 LLM 加速这个过程**
在现代工作流里，你不会从零写这个 kernel——你会：
1. 让 Cursor / Copilot 根据注释「`# 写一个 fused softmax kernel`」生成初版。
2. 让 Agent 跑 benchmark，对比 PyTorch 的 `torch.softmax`，发现慢在哪。
3. 让 Agent 根据性能 profile 迭代（加 `num_warps` 调参、改 memory access pattern）。

这正是本章的主线：**编译器（Triton）负责把抽象映射到硬件，LLM 负责（部分地）替代「人写 + 人调」**。两者结合，让一个不会写 CUDA 的工程师，也能产出接近专家的 kernel。

---

## 16. 给用户的建议：为什么 AI4Compiler 是工程价值最高的方向之一

结合你的背景（工程级 Python、PyTorch 教程级、想做「应用数学研究型工程师」）和本章内容，我给你三条具体建议：

**1. 从「会用」到「会改」：先吃透 `torch.compile` 和 Triton。**
这两个工具是 AI4Compiler 对普通用户最高频的接口。你不需要会写编译器，但你要理解：`torch.compile` 背后是 TorchDynamo + Inductor + Triton + MLIR 这一长串管线；Triton 背后是「block-level → thread-level」的 lowering。理解这些，你就能在模型训练慢的时候，知道瓶颈在编译器哪一段，而不是瞎调 batch size。推荐路径：写一个 Triton kernel（用 §15 的 softmax）→ 跑 benchmark → 用 `torch.compile(mode="max-autotune")` 对比 → 读 Triton 生成的 PTX。这是把「编译器理论」变成「工程肌肉记忆」最快的路。

**2. 把 AI4Compiler 当作「应用数学 + 工程」的最佳结合点。**
你说过你的研究方向候选包括「数值分析 / 优化理论」。编译器优化本质就是**离散优化 + 图论 + 概率推理**的组合：寄存器分配是图着色（图论）、指令调度是 NP-hard 排序（组合优化）、learned cost model 是回归（概率）、MLGO 的 inline 是 RL（决策过程）。这是一个「数学深度足够、工程落地明确、且和 AI 强绑定」的领域——比纯做「另一个 LLM 微调」有更高的护城河。如果你想读研 / 转研究，**「ML for Compilation」是一个窗口期还没关的方向**（不像 NLP 已经卷成红海）。

**3. 警惕「全靠 LLM」的幻觉，拥抱「混合管线」。**
本章反复出现一个模式：AlphaCode（generate-then-filter）、LLM4Decompile（Ghidra + LLM refine）、MLGO（模型决策 + 编译器执行）、self-repair（LLM 改 + 测试验）。**没有一个成功系统是「纯 LLM 端到端」的**——全部都是「LLM 负责生成 / 预测，经典工具负责验证 / 执行」。这对你做 Agent 项目（你的 `agent-guide`）是核心教训：**永远给 LLM 接一个真实的执行环境当裁判**（编译器、测试、形式验证器），而不是相信它的自我评估。这也是为什么 §11 强调 ACI（Agent-Computer Interface）设计——给 AI 用的工具，要在「可验证性」上专门设计。

> 一句话总结全章：**编译器是把「人类意图」翻译成「机器动作」的机器；AI for Compiler 是让这台翻译机自己学会翻译得更快、更准、甚至自己写下一台翻译机。这是计算机科学里少数几个「数学够深、工程够实、AI 够热」的三栖方向。**

---

## 📌 进一步阅读

**编译器基础（书籍）**
- 《Compilers: Principles, Techniques, and Tools》（龙书，Aho 等）—— 编译原理圣经。
- 《Engineering a Compiler》（Cooper & Torczon）—— 工程视角，比龙书更现代。
- 《Advanced Compiler Design and Implementation》（鲸书，Muchnick）—— 优化深度。
- LLVM 教程（llvm.org/docs/tutorial）—— 手把手写一门 Kaleidoscope 语言。

**关键论文（已核实 arXiv ID）**
- MLIR：[arXiv:2002.11054](https://arxiv.org/abs/2002.11054) — 编译基础设施的范式转移。
- TVM：[arXiv:1802.04799](https://arxiv.org/abs/1802.04799) — 深度学习编译开山之作。
- Ansor：[arXiv:2006.06762](https://arxiv.org/abs/2006.06762) — 无模板自动调度。
- MLGO：[arXiv:2101.04808](https://arxiv.org/abs/2101.04808) — 第一个进 LLVM 主线的 ML。
- Codex：[arXiv:2107.03374](https://arxiv.org/abs/2107.03374) — 代码 LLM + HumanEval。
- AlphaCode：[arXiv:2203.07814](https://arxiv.org/abs/2203.07814) — 竞赛级生成 + 行为过滤。
- DeepCoder：[arXiv:1611.01989](https://arxiv.org/abs/1611.01989) — 神经网络引导搜索。
- Code Llama：[arXiv:2308.12950](https://arxiv.org/abs/2308.12950) — 开源代码基础模型。
- DeepSeek-Coder：[arXiv:2401.14196](https://arxiv.org/abs/2401.14196) — 国产开源 SOTA。
- StarCoder 2：[arXiv:2402.19173](https://arxiv.org/abs/2402.19173) — 数据透明。
- LLM4Decompile：[arXiv:2403.05286](https://arxiv.org/abs/2403.05286) — LLM 反编译。
- SWE-bench：[arXiv:2310.06770](https://arxiv.org/abs/2310.06770) — 真实工程问题基准。
- SWE-agent：[arXiv:2405.15793](https://arxiv.org/abs/2405.15793) — Agent-Computer Interface。
- DeepCode：[arXiv:2512.07921](https://arxiv.org/abs/2512.07921) — 论文复现 Agent，2025 末 SOTA。

**无 arXiv 版本，按 venue 检索**
- FlashFill：Gulwani, POPL 2011 / CACM 2012。
- AlphaRepair：Fu & Tantithamthavorn, ASE 2022（DOI 10.1145/3551349.3556960）。
- CompilerGym：Hegedűs 等，ICLR 2022。
- Triton：OpenAI blog / GitHub `openai/triton`。
- Csmith：Yang 等，PLDI 2011。
- CompCert：Leroy，JFP / POPL 系列。

**动手资源**
- TVM 教程：tvm.apache.org/docs/tutorials
- Triton 教程：`openai/triton` 的 python/tutorials
- MLIR Toy Tutorial：mlir.llvm.org/docs/Tutorials/Toy
- CompilerGym：github.com/facebookresearch/CompilerGym

---

## ✍️ 思考题（5 道）

1. **【compute vs schedule】** TVM 把算子实现拆成「计算」和「调度」。请用这个框架分析：为什么同一个矩阵乘法，在 V100 和 A100 上最优的 tile size 完全不同？如果让你设计一个「跨硬件自动调度」系统，你会让 cost model 学「硬件特征」还是「直接学 schedule」？两者的泛化性差异是什么？

2. **【generate-then-filter】** AlphaCode 对每道题采样百万候选再用执行过滤。Codex 的论文也说「采样 100 次比采样 1 次好得多」。请思考：这个范式在什么情况下会失效？（提示：如果搜索空间里正确解的密度极低，或者验证器本身不可靠。）这与传统编译器里「learned cost model + 搜索」的根本区别是什么？

3. **【LLM 能不能取代编译器？】** 有人畅想「未来 LLM 直接从自然语言生成机器码，不再需要编译器」。请用本章的知识论证：这为什么不可行？至少从「正确性验证」「优化空间规模」「可复现性」三个角度分析。再反过来想：编译器的哪些部分**最可能**被 LLM 取代，哪些部分几乎不可能？

4. **【Agent-Computer Interface】** SWE-agent 论文的核心结论是「给 AI 用的界面，要专门设计」。请对比「人类用的 IDE」和「AI 用的 ACI」在设计目标上的冲突——人类需要什么（可视化、鼠标、渐进式）？AI 需要什么（高信息密度、可程序化、可回溯）？这个洞察对你设计自己的 Agent（参考你的 `agent-guide` 项目）有什么启发？

5. **【数学与工程的交叉】** 寄存器分配是图着色问题（NP-hard），指令调度是 NP-hard 排序，inline 决策是马尔可夫决策过程。请选其中一个，写出它的**形式化定义**（状态 / 动作 / 目标函数），并讨论：为什么传统启发式在某些情况下会失败，而 RL / GNN 能做得更好？再思考：这些 ML 方法的「可解释性」和「可证明正确性」问题，在工业部署里有多致命？

---

## 附：arXiv ID 核实勘误表（任务大纲错误纠正）

本次调研遵循「所有 arXiv ID 一手核实」铁律。任务大纲给出的 14 个候选 ID 中，**有 4 个错误**（错误率 29%），全部已在 arXiv API 一手核实后纠正。这是本卷「任务提示也会给错 arXiv ID」（lesson #5）的又一次实证。

| 系统 | 大纲给的（错误）ID | 实际验证内容 | 正确 ID / 引用方式 |
|---|---|---|---|
| **MLIR** | 2202.01195 | ❌ 药物-靶点亲和力预测论文（q-bio.BM） | ✅ **arXiv:2002.11054** |
| **AlphaCode** | 2203.07880 | ❌ CuO 四方相凝聚态物理论文（cond-mat） | ✅ **arXiv:2203.07814** |
| **DeepCoder** | 1611.01789 | ❌ Brink-Axel 假设核物理论文（nucl-ex） | ✅ **arXiv:1611.01989**（差一个数字） |
| **AlphaRepair** | 2110.10885 | ❌ 任意域上调和代表元代数拓扑论文（math.AT） | ✅ **ASE 2022（无 arXiv 版本）**，DOI 10.1145/3551349.3556960 |

**核对无误的 ID（10 个）**：TVM 1802.04799、Ansor 2006.06762、Codex 2107.03374、Code Llama 2308.12950、DeepSeek-Coder 2401.14196、StarCoder2 2402.19173、LLM4Decompile 2403.05286、MLGO 2101.04808、SWE-bench 2310.06770、SWE-agent 2405.15793。

**额外验证并引用的 2025 论文**：DeepCode 2512.07921（PaperBench SOTA，论文复现 Agent）。

**注**：CompilerGym（ICLR 2022）、torch.compile、Triton 等系统，经检索未在 arXiv 以可稳定命中的 ID 出现（猜测的 2109.08268 实为 CMS 粒子物理论文、2307.05672 实为 HUBS X 射线望远镜论文，均已弃用），故按「会议 / blog / GitHub」引用，**不臆造 arXiv ID**。

<!-- delegate 直接写入，2026-07-20 -->
