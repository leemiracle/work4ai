# CS 学习规划 · 课程地图（csdiy 对照落仓版）

> 本文档把 [CS自学指南 · 一个仅供参考的 CS 学习规划](https://csdiy.wiki/CS%E5%AD%A6%E4%B9%A0%E8%A7%84%E5%88%92/)（页面版本 2026-02-21，检索校准 2026-09-09）的规划结构**在本仓库落地**：csdiy 的每个学习阶段与推荐课程，逐项对照本仓库已有的**理论侧**（讲透系列宇宙）与**实战侧**（九校库 / 单课库 / 整合库）资源；仓库暂缺的领域如实标注 ⚠️ 并给外部正典链接，**不虚构仓库资源**。
>
> **用法**：先工具后课程；除「基础/入门」字眼外无严格先后，满足先修即可自选。想看本仓库自产的 30 课最优路径（与 csdiy 互补：它按「领域」组织，本仓库按「代码实战」组织）→ [UNIFIED_ROADMAP.md](UNIFIED_ROADMAP.md)。
>
> **本仓库与 csdiy 的分工**：csdiy 是「选课指南」（哪门课好、去哪上），本仓库是「知识底座+代码还原」（讲透宇宙管理论穿透，九校库管 200-400 行最小实现）。两边对着用：csdiy 选课 → 本仓库找同主题的讲透家族与可跑脚本。

## 〇、总览：csdiy 规划 × 仓库覆盖判定

| csdiy 领域 | 理论侧（讲透） | 实战侧（脚本/课程库） | 判定 |
|---|---|---|---|
| 必学工具 | — | [CS必学工具箱.md](CS必学工具箱.md) | ✅ 本仓自产 |
| 环境配置 | — | 同上 | ✅ 本仓自产 |
| 数学基础/进阶/高阶 | [讲透数学](../讲透数学/) 38 家族 | [top-math-courses/](../top-math-courses/)（9 校 75 门课） | ✅ 重覆盖 |
| 编程入门 | [讲透程序设计语言](../讲透计算机科学技术/讲透计算机软件/讲透程序设计语言/) | [cs61a-learning/](cs61a-learning/) 等 | ✅ |
| 电子基础（电路/信号与系统） | 数学侧有（调和分析/复分析） | — | ⚠️ 工程侧缺口 |
| 数据结构与算法 | 讲透算法理论/数据结构/图 | [algorithms/](../algorithms/) + 九校库 | ✅✅ 最厚 |
| 软件工程 | 讲透软件工程/软件开发环境 | 九校库 | ✅ |
| 体系结构 | 讲透计算机系统结构/工程 | [CSAPP_HARDWARE_TRUTHS.md](CSAPP_HARDWARE_TRUTHS.md) 三部曲 | ✅✅ |
| 系统入门 | 讲透计算机系统设计 | CSAPP 深读 | ✅ |
| 操作系统 | 讲透操作系统 | mit-cs-projects topic7-os | ✅ |
| 并行与分布式 | 讲透并行处理/分布式处理系统 | mit topic5-dist + 优化三部曲 | ✅✅ |
| 系统安全 | 讲透数据安全与计算机安全 | berkeley topic13-sec | ✅ 理论；⚠️ CTF 实践缺 |
| 计算机网络 | 讲透计算机网络 | [network-systems/](../network-systems/)（mini-TCP） | ✅ |
| 数据库系统 | 讲透数据库 | [database-systems/](../database-systems/) | ✅ |
| 编译原理 | 讲透编译系统 | cambridge 编译主题 | ✅ |
| Web 开发 | — | — | ⚠️ 缺口 |
| 计算机图形学 | 讲透计算机图形学 | stanford topic11-graphics | ✅ |
| 数据科学 | [讲透统计学](../讲透统计学/) 宇宙 | berkeley topic11-data | ✅ |
| 人工智能 | 讲透人工智能理论 | berkeley topic5-ai | ✅ |
| 机器学习 | 讲透统计学习理论 | 九校 ML 主题群 | ✅ |
| 深度学习（含 CV/NLP/GNN/RL） | [讲透模型](../讲透模型/) 宇宙 | [cs224n/](cs224n/) + 九校 | ✅✅ |
| 深度学习系统 | 讲透GPU与系统级/vLLM/高性能计算 | stanford topic4-mlsys | ✅✅ 本仓王牌 |
| 深度生成模型 | 讲透世界模型 | [Karpathy经典代码精读](../Karpathy经典代码精读/) | ✅ |

> 判定结论：csdiy 课程地图的 23 个领域中，本仓库**重覆盖 8 个、覆盖 12 个、真缺口 3 个半**（电子基础工程侧、Web 开发、CTF 实践，加信号与系统工程视角半个）。缺口处置见 [§四](#四缺口总表与补足建议)。

## 一、必学工具与环境配置

**全部收入 [CS必学工具箱.md](CS必学工具箱.md)**：学会提问（提问的智慧）、MIT-Missing-Semester、命令行的艺术、Vim、Git/GitHub、GNU Make/CMake、LaTeX、Docker，加上环境配置（Windows Scoop / 服务器 Linux）与好书推荐、定制课程地图的外部入口。

## 二、数学路线（csdiy 数学基础→进阶→高阶 × 本仓库数学宇宙）

csdiy 给 CS 学生的三层数学路线，本仓库 [讲透数学](../讲透数学/) 38 家族几乎逐条有对应——**这是本仓库对 csdiy 规划覆盖最厚的区域**：

| csdiy 层 | csdiy 推荐 | 本仓库理论侧 | 实战/课程侧 |
|---|---|---|---|
| 基础·微积分线代 | MIT 18.01/18.06, 3B1B | [讲透数学分析](../讲透数学/讲透分析/讲透数学分析/) · [讲透代数学](../讲透数学/讲透代数学/) · [讲透数值线代](../讲透数学/讲透数值线代/) | [top-math-courses/POPULAR_MATH.md](../top-math-courses/POPULAR_MATH.md)（科普线含 3B1B 类） |
| 基础·信息论入门 | MIT 6.050J | [讲透信息论](../讲透数学/讲透信息论/) | 同上 |
| 进阶·离散与概率 | UCB CS70/CS126 | [讲透离散数学](../讲透数学/讲透离散数学/) · [讲透概率论](../讲透数学/讲透概率论/) · [讲透高维概率](../讲透数学/讲透高维概率/) | berkeley topic4-discrete |
| 进阶·数值分析 | MIT ComputationalThinking/18.330/18.335 | [讲透计算数学](../讲透数学/讲透计算数学/) · [讲透数值分析](../讲透数学/讲透分析/讲透数值分析/) · [讲透数学建模](../讲透数学/讲透数学建模/) | 讲透数学各家族 experiments/ |
| 进阶·微分方程 | MIT 18.03/18.152/18.04 | [讲透偏微分方程](../讲透数学/讲透分析/讲透偏微分方程/) · [讲透动力系统](../讲透数学/讲透分析/讲透动力系统/) · [讲透复分析](../讲透数学/讲透分析/讲透复分析/) | — |
| 高阶·凸优化 | Stanford EE364A | [讲透优化](../讲透数学/讲透优化/) | berkeley topic12-opt |
| 高阶·信息论 | MIT 6.441 | 讲透信息论（同上，研究生层看其 01 章） | — |
| 高阶·应用统计 | MIT 18.650 | [讲透数理统计](../讲透数学/讲透数理统计/) · [讲透应用统计数学](../讲透数学/讲透应用统计数学/) · [讲透统计学宇宙](../讲透统计学/) | — |
| 高阶·初等数论 | MIT 18.781 | [讲透数论](../讲透数学/讲透数论/) | — |
| 高阶·密码学 | Stanford CS255 | [讲透数论](../讲透数学/讲透数论/)（数学侧）+ [讲透数据安全与计算机安全](../讲透计算机科学技术/讲透计算机基础/讲透数据安全与计算机安全/) | ⚠️ 密码学专门家族暂缺 |
| 数学科普入口 | Crash Course 类 | — | [top-math-courses/](../top-math-courses/)（9 校 75 门课+书单+故事线） |

## 三、课程地图（专业领域逐条对照）

### 3.1 编程入门

| csdiy 推荐 | 本仓库落点 |
|---|---|
| UCB CS61A（SICP-Python）⭐ | [cs61a-learning/](cs61a-learning/)（逐周学习笔记+代码）· [berkeley topic1-sicp](berkeley-cs-projects/topic1-sicp/) |
| Harvard CS50 / CS50P | [cmu topic1-intro](cmu-cs-projects/topic1-intro/) · [mit topic1-intro](mit-cs-projects/topic1-intro/)（同层入门课的另两家实现） |
| MIT 6.100L（Python） | [Karpathy经典代码精读](../Karpathy经典代码精读/)（micrograd 起步=最好的 Python+自动微分双入门） |
| Stanford CS106B/X（C++） | [princeton topic1-intro](princeton-cs-projects/topic1-intro/)；C++ 深水区见 [AGNER_FOG_OPTIMIZATION.md](AGNER_FOG_OPTIMIZATION.md) |
| Stanford CS110L（Rust）/ Cornell CS3110（OCaml） | ⚠️ 仓库暂缺；语言理论侧看 [讲透程序设计语言](../讲透计算机科学技术/讲透计算机软件/讲透程序设计语言/) |

### 3.2 数据结构与算法

csdiy：CS61B / Coursera Algorithms I&II / 6.006 / CS170 / 6.046——**本仓库覆盖最厚的领域之一**：

- 实战主线：[algorithms/](../algorithms/)（Princeton COS226 × MIT 6.006 × CMU 15-251 三极整合，`algo_integration.py`+`algo_weekly.py`）
- 九校：[berkeley topic2-dsa](berkeley-cs-projects/topic2-dsa/) · [mit topic3-algo](mit-cs-projects/topic3-algo/) + [topic4-algo2](mit-cs-projects/topic4-algo2/) · [princeton topic2-dsa](princeton-cs-projects/topic2-dsa/) + [topic3-graphs](princeton-cs-projects/topic3-graphs/)
- 理论：[讲透算法理论](../讲透计算机科学技术/讲透计算机基础/讲透算法理论/) · [讲透数据结构](../讲透计算机科学技术/讲透计算机基础/讲透数据结构/) · [讲透图](../讲透数学/讲透图/) · [讲透计算复杂度](../讲透数学/讲透计算复杂度/)（NP 问题的复杂度动物园）

### 3.3 软件工程

csdiy：MIT 6.031 / UCB CS169 → [讲透软件工程](../讲透计算机科学技术/讲透计算机软件/讲透软件工程/) · [讲透软件开发环境](../讲透计算机科学技术/讲透计算机软件/讲透软件开发环境/)（含构建工具链，与工具箱的 Make/CMake 互链）；工程规范实战散见九校库各 README。

### 3.4 体系结构

csdiy：Nand2Tetris（入门）→ CS61C（专业）：

- 入门鸟瞰：cmu/mit/princeton 各 topic1；从 01 造计算机的完整阶梯在 [讲透计算机系统设计](../讲透计算机科学技术/讲透计算机系统结构/讲透计算机系统设计/) + [讲透处理器技术](../讲透计算机科学技术/讲透计算机工程/讲透处理器技术/)
- 专业深水区（本仓王牌之一）：[CSAPP_HARDWARE_TRUTHS.md](CSAPP_HARDWARE_TRUTHS.md)（CSAPP/15-213 的 8 个硬件真相）→ [AGNER_FOG_OPTIMIZATION.md](AGNER_FOG_OPTIMIZATION.md) → [ARM_AND_RISCV_OPTIMIZATION.md](ARM_AND_RISCV_OPTIMIZATION.md) → [HIGHWAY_SIMD_LIBRARY.md](HIGHWAY_SIMD_LIBRARY.md)（四部曲，配可运行 demo）
- [berkeley topic3-arch](berkeley-cs-projects/topic3-arch/)（RISC-V 母校版）

### 3.5 系统入门

csdiy：MIT 6.033 / CMU 15-213（CSAPP）→ 15-213 对应 [CSAPP_HARDWARE_TRUTHS.md](CSAPP_HARDWARE_TRUTHS.md)（L03 完全体+demo）；系统通用设计原则在 [讲透计算机系统设计](../讲透计算机科学技术/讲透计算机系统结构/讲透计算机系统设计/)；[mit topic2-fund](mit-cs-projects/topic2-fund/)。

### 3.6 操作系统

csdiy：6.S081（xv6）/ CS162（Pintos）/ NJU 蒋炎岩 / HIT 李治军 → [讲透操作系统](../讲透计算机科学技术/讲透计算机软件/讲透操作系统/)（理论侧）· [mit topic7-os](mit-cs-projects/topic7-os/)（实战侧）。中文课（NJU/HIT）仓库暂无实现，外部正典见 csdiy 原页。

### 3.7 并行与分布式系统

csdiy：CMU 15-418/CS149（并行）+ MIT 6.824（分布式）：

- 并行：[讲透并行处理](../讲透计算机科学技术/讲透计算机系统结构/讲透并行处理/) · [讲透高性能计算](../讲透高性能计算/) · 优化三部曲（见 3.4）；CUDA/编译侧另有 [讲透GPU与系统级](../讲透GPU与系统级/)
- 分布式：[讲透分布式处理系统](../讲透计算机科学技术/讲透计算机系统结构/讲透分布式处理系统/) · [mit topic5-dist](mit-cs-projects/topic5-dist/)（6.824 Raft 实战）· [cmu topic4-distributed](cmu-cs-projects/topic4-distributed/)

### 3.8 系统安全

csdiy：CS161 / SEED Labs / CTF → 理论侧 [讲透数据安全与计算机安全](../讲透计算机科学技术/讲透计算机基础/讲透数据安全与计算机安全/) · 实战侧 [berkeley topic13-sec](berkeley-cs-projects/topic13-sec/) + [mit topic12-sec](mit-cs-projects/topic12-sec/)；⚠️ CTF 夺旗实践（CTF-wiki/CTF-101/Hacker-101）仓库暂缺，见 §四。

### 3.9 计算机网络

csdiy：CS144（写 TCP/IP 栈）/ CS168（理论）→ [network-systems/](../network-systems/)（`mini_tcp.py`=CS144 迷你栈 + `routing.py`=OSPF/BGP 路由）· [讲透计算机网络](../讲透计算机科学技术/讲透计算机系统结构/讲透计算机网络/) · [princeton topic11-networks-sec](princeton-cs-projects/topic11-networks-sec/)。

### 3.10 数据库系统

csdiy：CMU 15-445（bustub）/ UCB CS186 → [database-systems/](../database-systems/)（15-445 × 6.830 × CS186 × CS145 四视角，`db_integration.py`+`db_weekly.py`）· [讲透数据库](../讲透计算机科学技术/讲透计算机软件/讲透数据库/) · [cmu topic3-database](cmu-cs-projects/topic3-database/) · [mit topic6-db](mit-cs-projects/topic6-db/)。

### 3.11 编译原理

csdiy：龙书 + 北大编译实践 → [讲透编译系统](../讲透计算机科学技术/讲透计算机软件/讲透编译系统/) · [讲透自动机理论](../讲透计算机科学技术/讲透计算机基础/讲透自动机理论/)（词法/文法的数学底座）· Cambridge Tripos 编译主题（[cambridge-cs-projects/](cambridge-cs-projects/)）；自己写解释器的最短路径是 [cs61a-learning/](cs61a-learning/) 的 Scheme 解释器周。

### 3.12 Web 开发 ⚠️

csdiy：MIT web dev course（速成）/ Stanford CS142（系统）。**仓库暂缺**（九校库无 Web 主题、讲透宇宙无 Web 家族）；处置见 §四。

### 3.13 计算机图形学

csdiy：CS148 / Games101/103/202 → [讲透计算机图形学](../讲透计算机科学技术/讲透计算机应用/讲透计算机图形学/) · [stanford topic11-graphics](stanford-cs-projects/topic11-graphics/)；Games 系列仓库暂缺，外部正典见 csdiy 原页。

### 3.14 数据科学

csdiy：UCB Data100 / Stanford CS246 → [berkeley topic11-data](berkeley-cs-projects/topic11-data/)（Data100 主题实现）· [讲透统计学](../讲透统计学/) 宇宙（统计理论侧 7 家族）· [讲透应用统计数学](../讲透数学/讲透应用统计数学/)；⚠️ CS246 级海量数据挖掘暂缺。

### 3.15 人工智能

csdiy：CS50 AI（轻量）→ CS188（本科正课）→ [berkeley topic5-ai](berkeley-cs-projects/topic5-ai/)（CS188 主题）· [toronto topic6-ai](toronto-cs-projects/topic6-ai/) · [讲透人工智能理论](../讲透计算机科学技术/讲透人工智能/讲透人工智能理论/) + [讲透人工智能](../讲透计算机科学技术/讲透人工智能/) 家族群（NLP/模式识别/知识工程等 7 支）。

### 3.16 机器学习

csdiy：Coursera ML（入门）→ CS229/CS189（数学）→ [princeton topic9-ml-theory](princeton-cs-projects/topic9-ml-theory/)（ML 理论）· [mit topic10-ml](mit-cs-projects/topic10-ml/) · [cmu topic5-ml](cmu-cs-projects/topic5-ml/) · [berkeley topic6-ml](berkeley-cs-projects/topic6-ml/) · 理论正主 [讲透统计学习理论](../讲透数学/讲透统计学习理论/)；Yao Fu 进阶路线（csdiy 提及）超出本仓库范围。

### 3.17 深度学习

csdiy：Coursera DL / 李宏毅（入门）→ CMU 11-785 / MIT 6.7960 / NYU DLSP21（正课）→ 本仓库映射：

| csdiy 分支 | 推荐 | 本仓库落点 |
|---|---|---|
| 综合与基础 | CMU 11-785 / MIT 6.7960 / NYU DLSP21 | [cmu topic8-deep](cmu-cs-projects/topic8-deep/) · [toronto topic9-deep](toronto-cs-projects/topic9-deep/)（CSC413）· [讲透模型](../讲透模型/) 宇宙 01-07 章 + [讲透PyTorch](../讲透模型/讲透PyTorch/) |
| 计机视觉 | UMich EECS 498 / CS231n | [berkeley topic9-vision](berkeley-cs-projects/topic9-vision/) · [toronto topic11-vision](toronto-cs-projects/topic11-vision/) · [讲透CV](../讲透模型/讲透CV/) |
| 自然语言处理 | CS224n | **[cs224n/](cs224n/)**（Winter 2026 教学简化版：A1-A4+GPT-2 前向）· [berkeley topic8-nlp](berkeley-cs-projects/topic8-nlp/) · [讲透NLP](../讲透模型/讲透NLP/) |
| 图神经网络 | CS224w | [讲透图/22-图神经网络.md](../讲透数学/讲透图/22-图神经网络.md) + [23-WL表达力.md](../讲透数学/讲透图/23-WL表达力.md)（理论穿透版）· [stanford topic6-graph](stanford-cs-projects/topic6-graph/) |
| 强化学习 | CS285 | [berkeley topic7-rl](berkeley-cs-projects/topic7-rl/) · [讲透RL](../讲透模型/讲透RL/) |

### 3.18 深度学习系统

csdiy：CMU 10-414/714（needle）→ MIT 6.5940（TinyML）。**本仓库王牌领域**（作者主场）：[stanford topic4-mlsys](stanford-cs-projects/topic4-mlsys/) · [讲透GPU与系统级](../讲透GPU与系统级/) · [讲透vLLM](../讲透vLLM/) · [讲透高性能计算](../讲透高性能计算/) · [讲透分布式AI系统](../讲透分布式AI系统/)；10-414 的「自己写 autodiff」最短实现 = [Karpathy经典代码精读/01-micrograd-自动微分引擎.md](../Karpathy经典代码精读/01-micrograd-自动微分引擎.md)。

### 3.19 深度生成模型

csdiy：笔者学习路线 → [Karpathy经典代码精读](../Karpathy经典代码精读/)（VQVAE/normalizing flows/makemore/nanoGPT 十篇精读=生成模型最短代码阶梯）· [toronto topic12-generative](toronto-cs-projects/topic12-generative/)（CSC 2547H，Hinton 母校生成模型课）· [讲透世界模型](../讲透模型/讲透世界模型/) · [讲透LLM](../讲透模型/讲透LLM/)。

## 四、缺口总表与补足建议

| # | 缺口 | csdiy 对应推荐 | 处置建议 |
|---|---|---|---|
| 1 | 电子基础·电路 | UCB EE16A&B | 暂不建仓；外部正典 [EE16A](https://inst.eecs.berkeley.edu/~ee16a/sp24/)。理论兴趣可走 [讲透数学/讲透数学建模](../讲透数学/讲透数学建模/) 的电路建模案例 |
| 2 | 电子基础·信号与系统（工程版） | MIT 6.003 / UCB EE120 | 数学侧已有：[讲透调和分析](../讲透数学/讲透分析/讲透调和分析/)（Fourier 与分解）；工程系统版暂缺，外部正典 [MIT 6.003 OCW](https://ocw.mit.edu/courses/6-003-sign-and-systems-fall-2011/) |
| 3 | Web 开发 | MIT web dev / Stanford CS142 | 暂不建仓（与本仓库「重系统/理论/还原」定位弱相关）；外部 [CS142](https://web.stanford.edu/class/cs142/) |
| 4 | CTF 夺旗实践 | CTF-wiki / CTF-101 / Hacker-101 | 理论已有（见 3.8）；实践暂缺，外部 [CTF Wiki](https://ctf-wiki.org/) |
| 5 | 密码学专门课 | Stanford CS255 | 数学底座已有（[讲透数论](../讲透数学/讲透数论/)），专门家族待立项 |
| 6 | 海量数据挖掘 | Stanford CS246 | Data100 层已有（见 3.14），CS246 层暂缺 |

> 补足纪律：与 csdiy 原页一致——「仅供参考」。本表缺口是否建仓，按仓库既有治理（内容够厚再立族）决定，不为了对齐而注水。

## 五、定制属于你的课程地图

csdiy 尾节的「授人以渔」资源，本仓库内外各取一半：

**仓库内（本仓库自产的定制层）**：

- [UNIFIED_ROADMAP.md](UNIFIED_ROADMAP.md)——30 课最优路径（依赖排序+每课最佳学校版本+时间估计）
- [UNIFIED_PLAN_4_TRACKS.md](UNIFIED_PLAN_4_TRACKS.md)——4 路并修计划（E 工程师/R 研究员/M 算法/P 创业者）
- [FAST_TRACK_30.md](FAST_TRACK_30.md)——周历速查版
- [DEEP_ANALYSIS.md](DEEP_ANALYSIS.md)——15 主题跨校对比矩阵（选课前的「同主题哪家强」）
- [CROSS_SCHOOL_INSIGHTS.md](CROSS_SCHOOL_INSIGHTS.md)——跨校元洞察

**外部（csdiy 推荐的原始入口）**：[MIT OpenCourseWare](https://ocw.mit.edu/) · [UCB EECS Course Map](https://hkn.eecs.berkeley.edu/coursesurvey) · [Stanford CS Course List](https://cs.stanford.edu/courses/schedules/) · [csdiy 全站](https://csdiy.wiki/)

## 治理

- 本文档=对照层导航（不生产新知识，只做 csdiy 规划 × 仓库资源的映射与缺口声明）；理论内容归各讲透家族，代码实战归九校库与整合库
- 检索校准 2026-09-09：csdiy 页面版本 2026-02-21（页面尾注）；推荐课程与先修关系按 csdiy 原文转述，未做二次评判
- 仓库链接全部实测（linkcheck）；外部链接为 csdiy 原页推荐的正典入口
- 建档 2026-09-09；缺口建仓决策归仓库治理（见 §四）
