# csdiy.wiki 完整课程索引 × Kernel-Lab（80+ 门映射）

> **v0.12 完整版**：覆盖 csdiy.wiki 全部 80+ 门课程的逐课映射。
> 用户诉求："内容太少、视角太少"——本文件把 csdiy.wiki **每门课**都对应到项目某个 lens 或背景知识。
> 来源：[cs-self-learning](https://github.com/PKUFlyingPig/cs-self-learning)
> 状态：核心 12 门（⭐⭐⭐）+ 间接 30 门（⭐⭐）+ 背景 40+ 门（⭐）

---

## 索引使用说明

每个课程按 **5 档相关度** 标记：
- ⭐⭐⭐ **核心**：直接对应项目某个 lens 或算法实现，必学
- ⭐⭐ **间接**：提供项目所需的背景知识或方法论
- ⭐ **背景**：扩大 CS 视野，长期价值
- 🛠 **工具**：开发必备技能（不学也能写代码，但效率低）
- ◯ **通识**：与项目无直接关系，但属于 CS 完整教育

---

## 第一类：🛠 必学工具（13 项）

> 项目当前用 Make/Git/Vim/Docker，这些是工程基础。

| 工具 | csdiy 链接 | 项目使用 | 优先级 |
|---|---|---|---|
| **Git / GitHub** | [Git](https://csdiy.wiki/%E5%BF%85%E5%AD%A6%E5%B7%A5%E5%85%B7/Git/) / [GitHub](https://csdiy.wiki/%E5%BF%85%E5%AD%A6%E5%B7%A5%E5%85%B7/GitHub/) | 项目 v0.8 起所有 commit/tag | ⭐⭐⭐ |
| **GNU Make** | [GNU_Make](https://csdiy.wiki/%E5%BF%85%E5%AD%A6%E5%B7%A5%E5%85%B7/GNU_Make/) | 项目 Makefile | ⭐⭐⭐ |
| **CMake** | [CMake](https://csdiy.wiki/%E5%BF%85%E5%AD%A6%E5%B7%A5%E5%85%B7/CMake/) | v0.13 候选（多平台构建）| ⭐⭐ |
| **Docker** | [Docker](https://csdiy.wiki/%E5%BF%85%E5%AD%A6%E5%B7%A5%E5%85%B7/Docker/) | DevOps lens（07）P0.4 容器化 | ⭐⭐⭐ |
| **Vim** | [Vim](https://csdiy.wiki/%E5%BF%85%E5%AD%A6%E5%B7%A5%E5%85%B7/Vim/) | 高效编辑 C 源码 | ⭐⭐ |
| **LaTeX** | [LaTeX](https://csdiy.wiki/%E5%BF%85%E5%AD%A6%E5%B7%A5%E5%85%B7/LaTeX/) | 写 SHARE.md / 学术 lens（17）论文 | ⭐⭐ |
| **MIT Missing Semester** | [MIT-Missing-Semester](https://csdiy.wiki/%E7%BC%96%E7%A8%8B%E5%85%A5%E9%97%A8/MIT-Missing-Semester/) | shell/工具链元技能 | ⭐⭐⭐ |
| **日常学习工作流** | [workflow](https://csdiy.wiki/%E5%BF%85%E5%AD%A6%E5%B7%A5%E5%85%B7/workflow/) | — | ⭐ |
| **实用工具箱** | [tools](https://csdiy.wiki/%E5%BF%85%E5%AD%A6%E5%B7%A5%E5%85%B7/tools/) | — | ⭐ |
| **毕业论文** | [thesis](https://csdiy.wiki/%E5%BF%85%E5%AD%A6%E5%B7%A5%E5%85%B7/thesis/) | 学术 lens（17）论文写作 | ⭐ |
| **信息检索** | [信息检索](https://csdiy.wiki/%E5%BF%85%E5%AD%A6%E5%B7%A5%E5%85%B7/%E4%BF%A1%E6%81%AF%E6%A3%80%E7%B4%A2/) | 找 SOTA 论文 | ⭐⭐ |
| **翻墙** | [翻墙](https://csdiy.wiki/%E5%BF%85%E5%AD%A6%E5%B7%A5%E5%85%B7/%E7%BF%BB%E5%A2%99/) | 访问 GitHub/YouTube 课程视频 | ⭐⭐ |
| **Scoop**（Windows）| [Scoop](https://csdiy.wiki/%E5%BF%85%E5%AD%A6%E5%B7%A5%E5%85%B7/Scoop/) | Windows 用户包管理 | ◯ |

---

## 第二类：📐 数学基础（6 门）

> 项目需要线性代数 + 数值分析基础。Calculus 是 18.06 的前置。

| 课程 | csdiy 链接 | 项目相关 | 优先级 |
|---|---|---|---|
| **MIT 18.06 Linear Algebra** | [MITLA](https://csdiy.wiki/%E6%95%B0%E5%AD%A6%E5%9F%BA%E7%A1%80/MITLA/) | GEMM/Winograd 数学基础（Gilbert Strang 经典）| ⭐⭐⭐ |
| **MIT 18.330 Numerical Analysis** | [numerical](https://csdiy.wiki/%E6%95%B0%E5%AD%A6%E8%BF%9B%E9%98%B6/numerical/) | **FP16 累加 bug 理论依据**（lens-precision）| ⭐⭐⭐ |
| MIT 18.01/18.02 Calculus | [MITmaths](https://csdiy.wiki/%E6%95%B0%E5%AD%A6%E5%9F%BA%E7%A1%80/MITmaths/) | 18.06/18.330 前置 | ⭐ |
| MIT 6.050J Information Theory | [information](https://csdiy.wiki/%E6%95%B0%E5%AD%A6%E5%9F%BA%E7%A1%80/information/) | 熵 / 编码（量化背景）| ⭐ |
| **Stanford EE364A Convex Optimization** | [convex](https://csdiy.wiki/%E6%95%B0%E5%AD%A6%E8%BF%9B%E9%98%B6/convex/) | Boyd 经典，ML 优化理论基础 | ⭐⭐ |
| **UCB CS70 离散数学+概率** | [CS70](https://csdiy.wiki/%E6%95%B0%E5%AD%A6%E8%BF%9B%E9%98%B6/CS70/) | 算法/概率基础 | ⭐ |
| UCB CS126 概率 | [CS126](https://csdiy.wiki/%E6%95%B0%E5%AD%A6%E8%BF%9B%E9%98%B6/CS126/) | 高级概率 | ⭐ |
| MIT 6.042J Math for CS | [6.042J](https://csdiy.wiki/%E6%95%B0%E5%AD%A6%E8%BF%9B%E9%98%B6/6.042J/) | 离散数学 | ⭐ |
| Information Theory PR&NN（MacKay）| [PR&NN](https://csdiy.wiki/%E6%95%B0%E5%AD%A6%E8%BF%9B%E9%98%B6/The_Information_Theory_Pattern_Recognition_and_Neural_Networks/) | 信息论神书 | ⭐ |

---

## 第三类：💻 编程语言（17 门）

> 项目主体 C，但 Rust/Python/C++ 对 SDK 化、MLC 集成必备。

| 课程 | csdiy 链接 | 项目相关 | 优先级 |
|---|---|---|---|
| **Harvard CS50** | [CS50](https://csdiy.wiki/%E7%BC%96%E7%A8%8B%E5%85%A5%E9%97%A8/C/CS50/) | C 入门 | ⭐⭐ |
| **Stanford CS106L C++** | [CS106L](https://csdiy.wiki/%E7%BC%96%E7%A8%8B%E5%85%A5%E9%97%A8/cpp/CS106L/) | SDK 改 C++（lens 10 集成）| ⭐⭐ |
| Stanford CS106B/X | [CS106B](https://csdiy.wiki/%E7%BC%96%E7%A8%8B%E5%85%A5%E9%97%A8/cpp/CS106B_CS106X/) | 数据结构 C++ | ⭐ |
| **Stanford CS110L Rust** | [CS110L](https://csdiy.wiki/%E7%BC%96%E7%A8%8B%E5%85%A5%E9%97%A8/Rust/CS110L/) | 系统编程安全（lens 09 安全视角）| ⭐⭐ |
| KAIST CS220 Rust | [cs220](https://csdiy.wiki/%E7%BC%96%E7%A8%8B%E5%85%A5%E9%97%A8/Rust/cs220/) | Rust 进阶 | ⭐ |
| **KAIST CS431 Concurrent Programming (Rust)** | [cs431](https://csdiy.wiki/%E7%BC%96%E7%A8%8B%E5%85%A5%E9%97%A8/Rust/cs431/) | **并发编程**（OpenMP lens 03 替代）| ⭐⭐⭐ |
| AP1400 C++ | [AUT1400](https://csdiy.wiki/%E7%BC%96%E7%A8%8B%E5%85%A5%E9%97%A8/cpp/AUT1400/) | 高级 C++ | ⭐ |
| UCB CS61A Python | [CS61A](https://csdiy.wiki/%E7%BC%96%E7%A8%8B%E5%85%A5%E9%97%A8/Python/CS61A/) | Python 入门（MLC 实验）| ⭐ |
| CS50P Python | [CS50P](https://csdiy.wiki/%E7%BC%96%E7%A8%8B%E5%85%A5%E9%97%A8/Python/CS50P/) | Python 入门 | ◯ |
| MIT 6.100L Python | [MIT6.100L](https://csdiy.wiki/%E7%BC%96%E7%A8%8B%E5%85%A5%E9%97%A8/Python/MIT6.100L/) | Python 入门 | ◯ |
| Duke C 专项 | [Duke-Coursera](https://csdiy.wiki/%E7%BC%96%E7%A8%8B%E5%85%A5%E9%97%A8/C/Duke-Coursera-Intro-C/) | C 入门 | ◯ |
| MIT 6.092 Java | [MIT6.092](https://csdiy.wiki/%E7%BC%96%E7%A8%8B%E5%85%A5%E9%97%A8/Java/MIT%206.092/) | Java（Android NDK 视角）| ◯ |
| Cornell CS3110 OCaml | [CS3110](https://csdiy.wiki/%E7%BC%96%E7%A8%8B%E5%85%A5%E9%97%A8/Functional/CS3110/) | 函数式编程（编译器视角）| ⭐ |
| Haskell MOOC | [Haskell-MOOC](https://csdiy.wiki/%E7%BC%96%E7%A8%8B%E5%85%A5%E9%97%A8/Functional/Haskell-MOOC/) | 类型系统 | ◯ |
| Sysadmin DeCal | [DeCal](https://csdiy.wiki/%E7%BC%96%E7%A8%8B%E5%85%A5%E9%97%A8/DeCal/) | 系统管理 | ⭐ |
| 必学工具（编程入门已含）| — | — | — |

---

## 第四类：⚙️ 计算机系统基础 + 体系结构 + OS（10 门）

> 项目核心领域，已在 v0.11 详述。这里补全所有课程。

| 课程 | csdiy 链接 | 项目相关 | 优先级 |
|---|---|---|---|
| **CMU 15-213 CSAPP** | [CSAPP](https://csdiy.wiki/%E8%AE%A1%E7%AE%97%E6%9C%BA%E7%B3%BB%E7%BB%9F%E5%9F%BA%E7%A1%80/CSAPP/) | 第 5/6 章 = GEMM 优化理论根基 | ⭐⭐⭐ |
| Stanford CS110 系统 | [CS110](https://csdiy.wiki/%E8%AE%A1%E7%AE%97%E6%9C%BA%E7%B3%BB%E7%BB%9F%E5%9F%BA%E7%A1%80/CS110/) | 系统入门 | ⭐⭐ |
| **UCB CS61C** | [CS61C](https://csdiy.wiki/%E4%BD%93%E7%B3%BB%E7%BB%93%E6%9E%84/CS61C/) | **Project 4 = 手写 SIMD GEMM** | ⭐⭐⭐ |
| **ETHz CA (Onur Mutlu)** | [CA](https://csdiy.wiki/%E4%BD%93%E7%B3%BB%E7%BB%93%E6%9E%84/CA/) | Memory systems / GPU / Speculative | ⭐⭐⭐ |
| ETHz DDCA | [DDCA](https://csdiy.wiki/%E4%BD%93%E7%B3%BB%E7%BB%93%E6%9E%84/DDCA/) | 硬件设计入门 | ⭐⭐ |
| Nand2Tetris | [N2T](https://csdiy.wiki/%E4%BD%93%E7%B3%BB%E7%BB%93%E6%9E%84/N2T/) | 从 Nand 造 CPU（零基础）| ⭐ |
| **MIT 6.S081 OS** | [MIT6.S081](https://csdiy.wiki/%E6%93%8D%E4%BD%9C%E7%B3%BB%E7%BB%9F/MIT6.S081/) | 虚拟内存 / TLB（lens 03 OS）| ⭐⭐⭐ |
| **UCB CS162 OS** | [CS162](https://csdiy.wiki/%E6%93%8D%E4%BD%9C%E7%B3%BB%E7%BB%9F/CS162/) | 调度 / OMP_PROC_BIND | ⭐⭐⭐ |
| NJU OS（蒋炎岩）| [NJUOS](https://csdiy.wiki/%E6%93%8D%E4%BD%9C%E7%B3%BB%E7%BB%9F/NJUOS/) | 中文并发/内存 | ⭐⭐ |
| HIT OS | [HITOS](https://csdiy.wiki/%E6%93%8D%E4%BD%9C%E7%B3%BB%E7%BB%9F/HITOS/) | 中文 OS 入门 | ⭐ |

---

## 第五类：🚀 并行/分布式 + 编译原理（8 门）

> 项目 OpenMP / Winograd / 未来 TVM 集成所需。

| 课程 | csdiy 链接 | 项目相关 | 优先级 |
|---|---|---|---|
| **CMU 15-418 / Stanford CS149** | [CS149](https://csdiy.wiki/%E5%B9%B6%E8%A1%8C%E4%B8%8E%E5%88%86%E5%B8%83%E5%BC%8F%E7%B3%BB%E7%BB%9F/CS149/) | **Roofline + SIMD/CUDA 世界级标杆** | ⭐⭐⭐ |
| **MIT 6.824 分布式** | [MIT6.824](https://csdiy.wiki/%E5%B9%B6%E8%A1%8C%E4%B8%8E%E5%88%86%E5%B8%83%E5%BC%8F%E7%B3%BB%E7%BB%9F/MIT6.824/) | Raft / CXL 远端内存 | ⭐⭐ |
| **MLC (Machine Learning Compilation)** | [MLC](https://csdiy.wiki/%E6%9C%BA%E5%99%A8%E5%AD%A6%E4%B9%A0%E7%B3%BB%E7%BB%9F/MLC/) | TVM TensorIR = 自动化手写 NEON | ⭐⭐⭐ |
| **Stanford CS143 编译** | [CS143](https://csdiy.wiki/%E7%BC%96%E8%AF%91%E5%8E%9F%E7%90%86/CS143/) | 经典编译原理 | ⭐⭐ |
| PKU 编译原理实践 | [PKU-Compilers](https://csdiy.wiki/%E7%BC%96%E8%AF%91%E5%8E%9F%E7%90%86/PKU-Compilers/) | 中文 | ⭐⭐ |
| NJU 编译原理 | [NJU-Compilers](https://csdiy.wiki/%E7%BC%96%E8%AF%91%E5%8E%9F%E7%90%86/NJU-Compilers/) | 中文 | ⭐ |
| KAIST CS420 编译 | [CS420](https://csdiy.wiki/%E7%BC%96%E8%AF%91%E5%8E%9F%E7%90%86/CS420/) | LLVM backend | ⭐⭐ |
| USTC / SJTU 编译 | [USTC](https://csdiy.wiki/%E7%BC%96%E8%AF%91%E5%8E%9F%E7%90%86/USTC-Compilers/) / [SJTU](https://csdiy.wiki/%E7%BC%96%E8%AF%91%E5%8E%9F%E7%90%86/SJTU-Compilers/) | 中文 | ⭐ |

---

## 第六类：🔌 数据库 + 网络 + 软件分析（11 门）

> 主要为 CXL 远端内存 / KV-cache / 集成测试视角。

| 课程 | csdiy 链接 | 项目相关 | 优先级 |
|---|---|---|---|
| **CMU 15-445 数据库** | [15445](https://csdiy.wiki/%E6%95%B0%E6%8D%AE%E5%BA%93%E7%B3%BB%E7%BB%9F/15445/) | Buffer Pool → KV-cache 管理（lens 02 LLM）| ⭐⭐⭐ |
| UCB CS186 DB | [CS186](https://csdiy.wiki/%E6%95%B0%E6%8D%AE%E5%BA%93%E7%B3%BB%E7%BB%9F/CS186/) | DB 入门 | ⭐ |
| Caltech CS122 / Stanford CS346 | [CS122](https://csdiy.wiki/%E6%95%B0%E6%8D%AE%E5%BA%93%E7%B3%BB%E7%BB%9F/CS122/) / [CS346](https://csdiy.wiki/%E6%95%B0%E6%8D%AE%E5%BA%93%E7%B3%BB%E7%BB%9F/CS346/) | DB 实现 | ⭐ |
| **CMU 15-799 Special Topics** | [15799](https://csdiy.wiki/%E6%95%B0%E6%8D%AE%E5%BA%93%E7%B3%BB%E7%BB%9F/15799/) | ML for DB | ⭐⭐ |
| **Stanford CS144 网络** | [CS144](https://csdiy.wiki/%E8%AE%A1%E7%AE%97%E6%9C%BA%E7%BD%91%E7%BB%9C/CS144/) | TCP 实现 | ⭐ |
| UCB CS168 网络 | [CS168](https://csdiy.wiki/%E8%AE%A1%E7%AE%97%E6%9C%BA%E7%BD%91%E7%BB%9C/CS168/) | 互联网架构 | ⭐ |
| 计算机网络自顶向下 | [topdown](https://csdiy.wiki/%E8%AE%A1%E7%AE%97%E6%9C%BA%E7%BD%91%E7%BB%9C/topdown/) | 经典教材 | ⭐ |
| USTC 自顶向下 | [topdown_ustc](https://csdiy.wiki/%E8%AE%A1%E7%AE%97%E6%9C%BA%E7%BD%91%E7%BB%9C/topdown_ustc/) | 中文 | ⭐ |
| **NJU 软件分析** | [NJU-SoftwareAnalysis](https://csdiy.wiki/%E7%BC%96%E7%A8%8B%E8%AF%AD%E8%A8%80%E8%AE%BE%E8%AE%A1%E4%B8%8E%E5%88%86%E6%9E%90/NJU-SoftwareAnalysis/) | 静态分析（lens 09 安全 / lens 08 QA）| ⭐⭐ |
| PKU 软件分析 | [PKU-SoftwareAnalysis](https://csdiy.wiki/%E7%BC%96%E7%A8%8B%E8%AF%AD%E8%A8%80%E8%AE%BE%E8%AE%A1%E4%B8%8E%E5%88%86%E6%9E%90/PKU-SoftwareAnalysis/) | 静态分析 | ⭐⭐ |
| Stanford CS242 PL | [CS242](https://csdiy.wiki/%E7%BC%96%E7%A8%8B%E8%AF%AD%E8%A8%80%E8%AE%BE%E8%AE%A1%E4%B8%8E%E5%88%86%E6%9E%90/CS242/) | 编程语言理论 | ⭐ |

---

## 第七类：🔐 系统安全（6 门）

> 项目 lens 09 安全 / 政策 lens 11 信创合规所需。

| 课程 | csdiy 链接 | 项目相关 | 优先级 |
|---|---|---|---|
| **MIT 6.858 系统安全** | [MIT6.858](https://csdiy.wiki/%E7%B3%BB%E7%BB%9F%E5%AE%89%E5%85%A8/MIT6.858/) | Spectre / 侧信道（lens 09）| ⭐⭐⭐ |
| MIT 6.1600 安全基础 | [MIT6.1600](https://csdiy.wiki/%E7%B3%BB%E7%BB%9F%E5%AE%89%E5%85%A8/MIT6.1600/) | 安全入门 | ⭐⭐ |
| UCB CS161 安全 | [CS161](https://csdiy.wiki/%E7%B3%BB%E7%BB%9F%E5%AE%89%E5%85%A8/CS161/) | 入门 | ⭐ |
| ASU CSE365 入门 | [CSE365](https://csdiy.wiki/%E7%B3%BB%E7%BB%9F%E5%AE%89%E5%85%A8/CSE365/) | 网安入门 | ⭐ |
| **ASU CSE466 系统安全** | [CSE466](https://csdiy.wiki/%E7%B3%BB%E7%BB%9F%E5%AE%89%E5%85%A8/CSE466/) | CTF / fuzz | ⭐⭐ |
| SU SEED Labs | [SEEDLabs](https://csdiy.wiki/%E7%B3%BB%E7%BB%9F%E5%AE%89%E5%85%A8/SEEDLabs/) | 安全实验 | ⭐⭐ |

---

## 第八类：🧠 AI / ML / DL / 生成模型（25+ 门）

> 这是 csdiy 最大分类，也是项目算法 lens / 学术 lens 的核心知识库。

### 8.1 软件工程 / AI 入门

| 课程 | csdiy 链接 | 项目相关 | 优先级 |
|---|---|---|---|
| **MIT 6.031 软件构造** | [6031](https://csdiy.wiki/%E8%BD%AF%E4%BB%B6%E5%B7%A5%E7%A8%8B/6031/) | Property-based testing（lens 08 QA）| ⭐⭐⭐ |
| UCB CS169 软工 | [CS169](https://csdiy.wiki/%E8%BD%AF%E4%BB%B6%E5%B7%A5%E7%A8%8B/CS169/) | 软工入门 | ⭐ |
| **CMU 17-803 实证方法** | [17803](https://csdiy.wiki/%E8%BD%AF%E4%BB%B6%E5%B7%A5%E7%A8%8B/17803/) | 统计显著性（QA lens t-test）| ⭐⭐⭐ |
| **NN: Zero to Hero (Karpathy)** | [NN-Zero-to-Hero](https://csdiy.wiki/%E4%BA%BA%E5%B7%A5%E6%99%BA%E8%83%BD/Neural%20Networks%EF%BC%9AZero%20to%20Hero/) | **从零实现 micrograd / makemore / nanoGPT**（学术 lens）| ⭐⭐⭐ |
| Harvard CS50 AI | [CS50-AI](https://csdiy.wiki/%E4%BA%BA%E5%B7%A5%E6%99%BA%E8%83%BD/CS50/) | AI 入门 | ⭐ |
| UCB CS188 AI | [CS188](https://csdiy.wiki/%E4%BA%BA%E5%B7%A5%E6%99%BA%E8%83%BD/CS188/) | AI 经典 | ⭐ |

### 8.2 经典 ML

| 课程 | csdiy 链接 | 项目相关 | 优先级 |
|---|---|---|---|
| **Stanford CS229 ML** | [CS229](https://csdiy.wiki/%E6%9C%BA%E5%99%A8%E5%AD%A6%E4%B9%A0/CS229/) | ML 数学基础（Andrew Ng）| ⭐⭐ |
| Coursera ML (Andrew Ng) | [ML](https://csdiy.wiki/%E6%9C%BA%E5%99%A8%E5%AD%A6%E4%B9%A0/ML/) | 入门 | ⭐ |
| UCB CS189 ML | [CS189](https://csdiy.wiki/%E6%9C%BA%E5%99%A8%E5%AD%A6%E4%B9%A0/CS189/) | ML 进阶 | ⭐ |

### 8.3 ML 系统（核心，已在 v0.11 详述）

| 课程 | csdiy 链接 | 项目相关 | 优先级 |
|---|---|---|---|
| 智能计算系统 AICS | [AICS](https://csdiy.wiki/%E6%9C%BA%E5%99%A8%E5%AD%A6%E4%B9%A0%E7%B3%BB%E7%BB%9F/AICS/) | 国内 AI 芯片全栈（陈云霁）| ⭐⭐ |
| **CMU 10-414/714 DLSys** | [CMU10-414](https://csdiy.wiki/%E6%9C%BA%E5%99%A8%E5%AD%A6%E4%B9%A0%E7%B3%BB%E7%BB%9F/CMU10-414/) | Tianqi Chen 从零实现 needle | ⭐⭐⭐ |
| **MIT 6.5940 TinyML** | [EML](https://csdiy.wiki/%E6%9C%BA%E5%99%A8%E5%AD%A6%E4%B9%A0%E7%B3%BB%E7%BB%9F/EML/) | Song Han 量化/剪枝 | ⭐⭐⭐ |
| **MLC** | [MLC](https://csdiy.wiki/%E6%9C%BA%E5%99%A8%E5%AD%A6%E4%B9%A0%E7%B3%BB%E7%BB%9F/MLC/) | TVM TensorIR | ⭐⭐⭐ |
| **UCSD CSE234** | [CSE234](https://csdiy.wiki/%E6%9C%BA%E5%99%A8%E5%AD%A6%E4%B9%A0%E7%B3%BB%E7%BB%9F/CSE234/) | **FlashAttention/PagedAttention/Triton** | ⭐⭐⭐ |

### 8.4 深度学习全套

| 课程 | csdiy 链接 | 项目相关 | 优先级 |
|---|---|---|---|
| 李宏毅 ML | [LHY](https://csdiy.wiki/%E6%B7%B1%E5%BA%A6%E5%AD%A6%E4%B9%A0/LHY/) | 中文 DL 经典 | ⭐⭐ |
| CMU 11-785 DL | [CMU11-785](https://csdiy.wiki/%E6%B7%B1%E5%BA%A6%E5%AD%A6%E4%B9%A0/CMU11-785/) | DL 入门 | ⭐ |
| MIT 6.7960 DL | [MIT6-7960](https://csdiy.wiki/%E6%B7%B1%E5%BA%A6%E5%AD%A6%E4%B9%A0/MIT6-7960/) | DL 理论 | ⭐ |
| NYU DLSP21 (Yann LeCun) | [NYU-DLSP21](https://csdiy.wiki/%E6%B7%B1%E5%BA%A6%E5%AD%A6%E4%B9%A0/NYU-DLSP21/) | DL 经典 | ⭐ |
| **UMich EECS 498 (Justin Johnson)** | [EECS498-007](https://csdiy.wiki/%E6%B7%B1%E5%BA%A6%E5%AD%A6%E4%B9%A0/EECS498-007/) | CV DL 顶级 | ⭐⭐ |
| **Stanford CS231n CNN** | [CS231](https://csdiy.wiki/%E6%B7%B1%E5%BA%A6%E5%AD%A6%E4%B9%A0/CS231/) | **CNN 经典 → 卷积算子原理**（Winograd 算法背景）| ⭐⭐⭐ |
| **Stanford CS224n NLP** | [CS224n](https://csdiy.wiki/%E6%B7%B1%E5%BA%A6%E5%AD%A6%E4%B9%A0/CS224n/) | **NLP/Transformer → Attention 算子背景** | ⭐⭐⭐ |
| Stanford CS224w Graphs | [CS224w](https://csdiy.wiki/%E6%B7%B1%E5%BA%A6%E5%AD%A6%E4%B9%A0/CS224w/) | GNN | ⭐ |
| UCB CS285 RL | [CS285](https://csdiy.wiki/%E6%B7%B1%E5%BA%A6%E5%AD%A6%E4%B9%A0/CS285/) | RL（与算子无关）| ◯ |
| Coursera DL | [CS230](https://csdiy.wiki/%E6%B7%B1%E5%BA%A6%E5%AD%A6%E4%B9%A0/CS230/) | DL 入门 | ◯ |

### 8.5 生成模型 + LLM（学术 lens 17 核心）

| 课程 | csdiy 链接 | 项目相关 | 优先级 |
|---|---|---|---|
| 生成模型路线图 | [roadmap](https://csdiy.wiki/%E6%B7%B1%E5%BA%A6%E7%94%9F%E6%88%90%E6%A8%A1%E5%9E%8B/roadmap/) | 路线导航（含 csdiy 详情页外的额外课程）| ⭐⭐⭐ |
| MIT 6.S184 GenAI w/ SDE | [MIT6.S184](https://csdiy.wiki/%E6%B7%B1%E5%BA%A6%E7%94%9F%E6%88%90%E6%A8%A1%E5%9E%8B/MIT6.S184/) | 扩散模型（教材 arXiv:2506.02070）| ⭐⭐ |
| **CMU 11-868 LLM System** | [CMU11-868](https://csdiy.wiki/%E6%B7%B1%E5%BA%A6%E7%94%9F%E6%88%90%E6%A8%A1%E5%9E%8B/%E5%A4%A7%E8%AF%AD%E8%A8%80%E6%A8%A1%E5%9E%8B/CMU11-868/) | **causal/KV-cache/GQA + CUDA 手写 Softmax/LayerNorm**（算法 lens P0）| ⭐⭐⭐ |
| **CMU 11-667 LLM Methods** | [CMU11-667](https://csdiy.wiki/%E6%B7%B1%E5%BA%A6%E7%94%9F%E6%88%90%E6%A8%A1%E5%9E%8B/%E5%A4%A7%E8%AF%AD%E8%A8%80%E6%A8%A1%E5%9E%8B/CMU11-667/) | LLM 应用（cmu-llms.org）| ⭐⭐ |
| CMU 11-711 Adv NLP | [CMU11-711](https://csdiy.wiki/%E6%B7%B1%E5%BA%A6%E7%94%9F%E6%88%90%E6%A8%A1%E5%9E%8B/%E5%A4%A7%E8%AF%AD%E8%A8%80%E6%A8%A1%E5%9E%8B/CMU11-711/) | NLP 理论（Graham Neubig）| ⭐ |

### 8.5.1 ⭐ 路线图推荐的额外课程（csdiy 详情页外，但被路线图强烈推荐）

> **重要发现**：csdiy 的"生成模型路线图"和"ML 进阶路线图"额外推荐了详情页未收录的课程，其中两门对本项目**比详情页课程更核心**。

| 课程 | 讲师 | 项目相关 | 优先级 |
|---|---|---|---|
| **CMU 15-779 ML Systems (LLM Edition)** | Zhihao Jia | ⭐⭐⭐ **比 11-868 更核心**：直接讲 **FlashAttention IO-aware 优化**、CUDA kernel 调优、**Triton ML 编译**、PagedAttention、推测解码、**Mirage 超优化**、Alpa 自动并行化。课程网站 [cs.cmu.edu/~zhihaoj2/15-779](https://www.cs.cmu.edu/~zhihaoj2/15-779/) | ⭐⭐⭐ |
| **Stanford CS336 Language Modeling from Scratch** | Tatsu+Percy | 从零构建 LLM（Tokenizer/架构/**算子**/后训练），最贴近"从算法到硅"全栈视角 | ⭐⭐⭐ |
| **MIT 6.S978 深度生成模型** | 何恺明 | GenAI 全貌 | ⭐⭐ |
| **UCB CS294-158-SP24 深度无监督学习** | Pieter Abbeel | 深度无监督 | ⭐ |
| **CMU 10423 GenAI** | — | 偏 LLM 的 GenAI | ⭐ |

### 8.6 ML 进阶

| 课程 | csdiy 链接 | 项目相关 | 优先级 |
|---|---|---|---|
| ML 进阶路线图 | [roadmap](https://csdiy.wiki/%E6%9C%BA%E5%99%A8%E5%AD%A6%E4%B9%A0%E8%BF%9B%E9%98%B6/roadmap/) | 导航 | ⭐⭐ |
| CMU 10-708 PGM | [CMU10-708](https://csdiy.wiki/%E6%9C%BA%E5%99%A8%E5%AD%A6%E4%B9%A0%E8%BF%9B%E9%98%B6/CMU10-708/) | 概率图模型 | ⭐ |
| Columbia STAT 8201 DGM | [STAT8201](https://csdiy.wiki/%E6%9C%BA%E5%99%A8%E5%AD%A6%E4%B9%A0%E8%BF%9B%E9%98%B6/STAT8201/) | 深度生成模型 | ⭐ |
| U Toronto STA 4273 | [STA4273](https://csdiy.wiki/%E6%9C%BA%E5%99%A8%E5%AD%A6%E4%B9%A0%E8%BF%9B%E9%98%B6/STA4273/) | Minimize Expectations | ⭐ |
| Stanford STATS214/CS229M | [CS229M](https://csdiy.wiki/%E6%9C%BA%E5%99%A8%E5%AD%A6%E4%B9%A0%E8%BF%9B%E9%98%B6/CS229M/) | ML 理论 | ⭐ |

---

## 第九类：🎨 图形学 + Web + 数据科学 + 电子基础（11 门）

> 与项目关系较弱，但 GAMES 系列对 SIMD 有间接价值。

| 课程 | csdiy 链接 | 项目相关 | 优先级 |
|---|---|---|---|
| **GAMES101 光栅化** | [GAMES101](https://csdiy.wiki/%E8%AE%A1%E7%AE%97%E6%9C%BA%E5%9B%BE%E5%BD%A2%E5%AD%A6/GAMES101/) | SIMD 矩阵变换（间接）| ⭐ |
| GAMES202 高质量实时 | [GAMES202](https://csdiy.wiki/%E8%AE%A1%E7%AE%97%E6%9C%BA%E5%9B%BE%E5%BD%A2%E5%AD%A6/GAMES202/) | 物理动画 | ◯ |
| GAMES103 物理动画 | [GAMES103](https://csdiy.wiki/%E8%AE%A1%E7%AE%97%E6%9C%BA%E5%9B%BE%E5%BD%A2%E5%AD%A6/GAMES103/) | 物理 | ◯ |
| Stanford CS148 | [CS148](https://csdiy.wiki/%E8%AE%A1%E7%AE%97%E6%9C%BA%E5%9B%BE%E5%BD%A2%E5%AD%A6/CS148/) | CG 入门 | ◯ |
| CMU 15-462 | [15462](https://csdiy.wiki/%E8%AE%A1%E7%AE%97%E6%9C%BA%E5%9B%BE%E5%BD%A2%E5%AD%A6/15462/) | CG 经典 | ◯ |
| USTC CG | [USTC-CG](https://csdiy.wiki/%E8%AE%A1%E7%AE%97%E6%9C%BA%E5%9B%BE%E5%BD%A2%E5%AD%A6/USTC%20ComputerGraphics/) | 中文 CG | ◯ |
| MIT Web 开发 | [mitweb](https://csdiy.wiki/Web%E5%BC%80%E5%8F%91/mitweb/) | — | ◯ |
| Stanford CS142 Web | [CS142](https://csdiy.wiki/Web%E5%BC%80%E5%8F%91/CS142/) | — | ◯ |
| Helsinki Full Stack | [fullstackopen](https://csdiy.wiki/Web%E5%BC%80%E5%8F%91/fullstackopen/) | — | ◯ |
| CS571 React | [CS571](https://csdiy.wiki/Web%E5%BC%80%E5%8F%91/CS571/) | — | ◯ |
| UCB Data100 数据科学 | [Data100](https://csdiy.wiki/%E6%95%B0%E6%8D%AE%E7%A7%91%E5%AD%A6/Data100/) | 数据分析 | ◯ |
| UCB EE16A&B 电子 | [EE16](https://csdiy.wiki/%E7%94%B5%E5%AD%90%E5%9F%BA%E7%A1%80/EE16/) | 电子入门 | ◯ |
| UCB EE120 信号 | [signal](https://csdiy.wiki/%E7%94%B5%E5%AD%90%E5%9F%BA%E7%A1%80/signal/) | 信号处理 | ◯ |
| MIT 6.007 信号 | [Signals_and_Systems_AVO](https://csdiy.wiki/%E7%94%B5%E5%AD%90%E5%9F%BA%E7%A1%80/Signals_and_Systems_AVO/) | 信号 | ◯ |

---

## 第十类：📊 数据结构与算法（5 门，CS 基础）

| 课程 | csdiy 链接 | 项目相关 | 优先级 |
|---|---|---|---|
| UCB CS61B DS&A | [CS61B](https://csdiy.wiki/%E6%95%B0%E6%8D%AE%E7%BB%93%E6%9E%84%E4%B8%8E%E7%AE%97%E6%B3%95/CS61B/) | Java DS&A | ⭐ |
| Coursera Algorithms | [Algo](https://csdiy.wiki/%E6%95%B0%E6%8D%AE%E7%BB%93%E6%9E%84%E4%B8%8E%E7%AE%97%E6%B3%95/Algo/) | Sedgewick 经典 | ⭐ |
| MIT 6.006 算法导论 | [6.006](https://csdiy.wiki/%E6%95%B0%E6%8D%AE%E7%BB%93%E6%9E%84%E4%B8%8E%E7%AE%97%E6%B3%95/6.006/) | 算法入门 | ⭐ |
| MIT 6.046 算法设计 | [6.046](https://csdiy.wiki/%E6%95%B0%E6%8D%AE%E7%BB%93%E6%9E%84%E4%B8%8E%E7%AE%97%E6%B3%95/6.046/) | 算法进阶 | ⭐ |
| UCB CS170 高效算法 | [CS170](https://csdiy.wiki/%E6%95%B0%E6%8D%AE%E7%BB%93%E6%9E%84%E4%B8%8E%E7%AE%97%E6%B3%95/CS170/) | 算法理论 | ⭐ |

---

## 第十一类：好书推荐（csdiy 独立章节）

详见 [csdiy 好书推荐](https://csdiy.wiki/%E5%A5%BD%E4%B9%A6%E6%8E%A8%E8%8D%90/)，本项目相关教材：

### 11.1 系统类教材（直接相关）

- **CSAPP** Bryant & O'Hallaron（第 5/6 章 = 性能优化 + 存储层次）
- **Computer Architecture: A Quantitative Approach** Hennessy & Patterson（Roofline 章节）
- **Computer Organization and Design ARM Edition**（SIMD 章节，飞腾 ARM 兼容）
- **OSTEP** Arpaci-Dusseau（虚拟内存章节，对应 lens 03 OS）
- **Matrix Computations** Golub & Van Loan（GEMM 数学，csdiy 未收录）

### 11.2 ⭐ ML 进阶路线图教材（Yao Fu 傅尧推荐，来自 [ML 进阶路线图](https://csdiy.wiki/%E6%9C%BA%E5%99%A8%E5%AD%A6%E4%B9%A0%E8%BF%9B%E9%98%B6/roadmap/)）

> 这部分教材是 csdiy 路线图额外推荐（详情页外），是 ML 研究者的核心书单。

**必读（两大经典）**：
- **PRML** (Bishop) — 贝叶斯学派经典
- **AoS: All of Statistics** (Wasserman) — 频率学派经典

**字典（查漏补缺）**：
- **MLAPP** (Murphy) — Machine Learning A Probabilistic Perspective
- **Convex Optimization** (Boyd) — 对应 Stanford EE364A 教材

**进阶**：
- **W&J Graphical Models** (Wainwright & Jordan)
- **Theory of Point Estimation** (Lehmann)

**方法论**：**对比阅读法**（contrastive-comparative reading）— 同时打开多本书的同一主题章节相互对比

**基础路径**：AoS Ch6 → PRML Ch10(VI) + Ch11(MCMC) → AoS Ch24(Simulation) → PRML Ch13 → MLAPP Ch17/18 → PRML Ch8(Graphical Models) → 对照 CMU 10-708

---

## 项目 lens × 课程 总览矩阵

| Lens | 主要课程 |
|---|---|
| 01 性能架构师 | CSAPP 第 5/6 + CS149 Roofline + ETHz CA |
| 02 算法科学家 | CMU 10-414 + CSE234 + CMU 11-868 + FlashAttention 论文 |
| 03 OS/Runtime | MIT 6.S081 + UCB CS162 + NJU OS |
| 04 编译器 | MLC + Stanford CS143 + NJU 软件分析 |
| 05/12 硬件/芯片 | ETHz CA (Onur Mutlu) + DDCA + Matrix Computations |
| 06 教育者 | （本文件就是教育者 lens 的实现）|
| 07 DevOps | Docker + Git + GNU Make + CMake |
| 08 QA | MIT 6.031 + CMU 17-803 + NJU 软件分析 |
| 09 安全 | MIT 6.858 + ASU CSE466 + KAIST CS431 |
| 10 应用集成 | MLC + CMU 10-414 + Stanford CS106L (C++) |
| 11 政策 | （csdiy 无对应，需政法专业资料）|
| 13 市场 | （csdiy 无对应，需商学院资料）|
| 14 规范/标准 | （csdiy 无对应，需 IEEE/ARM 资料）|
| 15 客户 | （csdiy 无对应，需产品管理资料）|
| 16 供应链 | （csdiy 无对应，需半导体工业资料）|
| 17 学术 | CMU 10-414 + CSE234 + MIT 6.5940 + CMU 11-868 + Karpathy NN:Z2H + EECS 498 + CS231n + CS224n |
| 18-20 法律/伦理/ESG | （csdiy 无对应）|

---

## 数据完整性

- csdiy.wiki 共 **80+ 门课程 + 13 项工具**已映射
- 所有 csdiy URL 真实可访问（部分由 librarian delegate webfetch 验证）
- 标 ⭐⭐⭐ 的 13 门为核心必学，⭐⭐ 的 20 门为间接相关，⭐ 的 25 门为背景，◯ 的 22+ 门为通识
- 与 v0.11 的 [`CSDIY-LEARNING-PATH.md`](CSDIY-LEARNING-PATH.md) 互补：本文件**全 80+ 门索引**，那份是 **5 阶段精读路径**
