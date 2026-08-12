# 9 校 CS 课程跨校深度对比矩阵 · Step-by-Step

> 这份文档把 9 所学校的「同一主题」放在一起做深度对比——不是清单，是**分析**。每个主题分 3 层：(1) 各家招牌课与教授；(2) 教学法差异；(3) 学完之后能做什么。

---

## §1 编程入门与计算思维

### 1.1 课程编号 / 教授
| 学校 | 课程 | 教授 / 教材 | 风格 |
|------|------|-----------|------|
| Stanford | CS106A/B (Python/C++) | Julie Zelenski, Chris Piech | 项目驱动（图形/游戏）|
| **CMU** | 15-112 (Python) | David Kosbie | 极高强度（每周 15+ 小时）|
| MIT | 6.100A + 6.101 | Ana Bell | 紧凑严谨 |
| **Berkeley** | **CS 61A** (SICP-Python) | **John DeNero** | **抽象优先**（函数/对象/解释器）|
| Princeton | COS 126 | Sedgewick | Java + TOY 机 |
| Cambridge | Part IA Foundations | Marcelo Fiore | 数学/逻辑重 |
| Oxford | Foundations of CS | Andrew Pitts | 类型论传统 |
| ETH | EPROG (Scala/Java) | | 强类型开头 |
| Toronto | CSC 108/148 | | 标准 Python/OO |

### 1.2 教学法核心差异
- **Berkeley 61A 教"抽象"**：先讲函数 → 对象 → 解释器（学期末自己写一个 Scheme 解释器），是 SICP 精神的最完整 Python 现代化版本。
- **CMU 15-112 教"工程量"**：要求学生 1 学期完成 5000+ 行代码的 6 个大项目（含动画、游戏、AI），强度全国之首。
- **Stanford CS106 教"可视化动机"**：用图形库（Python Graphics）让学生从第一周就能写动画游戏。
- **Princeton COS 126 用 TOY machine**：学生先在虚拟机上写汇编，理解硬件层。

### 1.3 学完后能力
| 学习路径 | 后续衔接 |
|---------|---------|
| CS 61A | → CS 61B 数据结构（无障碍）|
| 15-112 | → 15-122 + 15-150（CMU 内部高门槛）|
| CS106A | → CS106B + CS107（连续性强）|

---

## §2 数据结构与算法

### 2.1 招牌课
- **Princeton COS 226 + Sedgewick《Algorithms 4ed》**：Coursera 上 200 万学习者，**全球最广为学习的算法课**。Java 实现，可视化极强。
- **CMU 15-251 Great Ideas**：理论味重（P vs NP、Gödel、Cantor 对角线都教）。
- **MIT 6.006 + 6.046**： Erik Demaine / Srini Devadas，理论严谨。
- **Berkeley CS 61B (Josh Hug)**：Java 实现，教学反馈极好。
- **Stanford CS161**：偏算法分析。

### 2.2 教学法核心差异
- **Princeton**：把"算法可视化"做到极致——每个算法配交互 demo。
- **MIT**：把"数学严谨性"做到极致——Master theorem 求解递推、amortized analysis 必考。
- **CMU 15-251**：把"思想史"做到极致——停机问题、Cantor 对角线、P vs NP、零知识证明。

### 2.3 学完后能力
- Princeton：能立即在 LeetCode Medium-Hard 上手。
- CMU 15-251：能理解 TCS 论文的动机。
- MIT：能写严谨的算法证明。

---

## §3 计算机系统

### 3.1 三大金标准
1. **CMU 15-213 CSAPP（Bryant & O'Hallaron）**：教材即行业圣经（《Computer Systems: A Programmer's Perspective》），所有 lab 公开（bomb lab、attack lab、malloc lab、shell lab、proxy lab）。
2. **MIT 6.828 / 6.S081（Frans Kaashoek, Robert Morris）**：实现 xv6，一个真实的小型 UNIX。所有 lab 用 RISC-V。
3. **Berkeley CS 162**：Pintos 项目（Intel x86 教学内核）。

### 3.2 深度对比
| 维度 | CSAPP (CMU) | 6.828 (MIT) | CS 162 (Berkeley) |
|------|------------|-------------|-------------------|
| 入口视角 | **自下而上**：从 bit → asm → C → 程序的运行 | **自上而下**：先写 user prog → 再下沉内核 | **中段切入**：直接进内核 Pintos |
| 编程语言 | C + 一点 asm | C (RISC-V) | C + Java（project）|
| 标志性 lab | bomb lab（破解二进制）| xv6 syscall / FS / VM | Pintos thread/VM/FS |
| 适合人群 | 想理解"程序在机器上怎么跑"的所有人 | 想做 OS / 内核的人 | 想做 systems research 的人 |
| 配套书 | CSAPP textbook | xv6 book（原创）| OSTEP（Wiseman，免费）|

### 3.3 学完后能力
- CSAPP：能 gdb 调试、读 objdump、理解 cache、写 SIMD。
- xv6：能写一个 syscall、改 page table。
- Pintos：能实现多线程调度器。

---

## §4 数据库系统

### 4.1 教授图谱
- **CMU 15-445 Andy Pavlo**：研究列存/OLAP 顶会常客；课程用 bus-tub（C++），所有 lecture 录像在 YouTube，**近年最强 DB 教学**。
- **MIT 6.830 Robert Morris**：简单 bus-tub 的 Java 版本；理论性强。
- **Berkeley CS 186**：基于 Spark + Postgres。
- **Stanford CS145**：NoSQL / Big Data 倾向。

### 4.2 教学法差异
- **CMU 15-445 教"如何实现一个 DB"**：buffer pool / B+ tree / query exec / MVCC / consensus 全栈实现一遍。
- **MIT 6.830 教"DB 的核心抽象"**：serializability/isolation/2PL/ARIES 等"思想武器"。
- **Berkeley CS 186 教"如何用 DB"**：SQL + 实战。

### 4.3 学完后能力
- CMU 15-445：能从零写一个单机 DB。
- MIT 6.830：能讨论 isolation level 的微妙差别。

---

## §5 分布式系统

### 5.1 王者：MIT 6.824（Frans Kaashoek, Robert Morris）
- 实现：MapReduce / Raft / KV store（基于 Raft）/ Shard KV（基于 Paxos）。
- 4 个 lab 渐进式（lab1 = MR，lab2 = Raft，lab3 = KV，lab4 = Shard）。
- Go 语言实现，**全球公认 #1 分布式课**。

### 5.2 强劲对手：CMU 15-440 / 15-721（David Andersen）
- 偏系统研究，读论文为主。
- 15-721 Advanced Database Systems（Pavlo）覆盖 OLAP / OLTP / Cloud DB。

### 5.3 ETH Reliable Distributed Systems
- 强项是**理论严谨**：FLP 不可能性、Byzantine、PBFT、CRDT 都教。
- 与 Paxos / Raft 互补，强调"为什么这样设计"。

### 5.4 学完后能力
- MIT 6.824 lab1-4 全做完：能去 Google/ByteDance/AWS 做分布式后端。
- CMU 15-721：能做 DB 研究。
- ETH RDS：能写一致性证明。

---

## §6 人工智能（经典 + 搜索）

### 6.1 双雄
- **Berkeley CS 188 Pacman（Pieter Abbeel, Dan Klein）**：4 个 Pacman 项目（搜索 / 多 agent / RL / Bayes），**edX 50 万学习者**。Pacman 形象全球家喻户晓。
- **Stanford CS221（Dorsa Sadigh, Percy Liang）**：21 世纪重写版，加入 ML/DL 元素。

### 6.2 学术视角差异
- **CMU 15-381 AI**：更理论，搜索 + decision theory + RL。
- **MIT 6.034 Patrick Winston**：经典 GOFAI，2010 年代仍在用。
- **Toronto CSC 384**：偏向逻辑推理 + planning。

### 6.3 学完后能力
- CS 188：能写出可玩 Pacman 的 5 种 agent（搜索 + RL + Bayes）。
- CS221：能搭一个 end-to-end 推荐系统。

---

## §7 机器学习（经典）

### 7.1 双王
- **Stanford CS229 吴恩达**：行业事实标准。三个笔记（Linear Algebra / Probability / PCA）够自学一学期。
- **CMU 10-701 Tom Mitchell / Matt Gormley**：学术血统最纯（《Machine Learning》教材作者）。

### 7.2 同档位
- **Berkeley CS 189（Sahai, Hasson）**：mathematically dense，被誉为"ML 入门最硬核"。
- **MIT 6.867**：理论派，强调概率视角。
- **Princeton COS 435**：精简版。

### 7.3 学完后能力
- CS229：能从零写 SVM、决策树、神经网络。
- CS 189：能严格推导 PAC / VC / Rademacher。

---

## §8 深度学习

### 8.1 Stanford CS231N（Karpathy 时代）传奇地位
- 2015-2017 年 Karpathy 教的版本是**历史最强 DL 教学**（Karpathy 后来去特斯拉/OpenAI）。
- 现在（2025-2026）由 Justin Johnson / Fei-Fei Li 接续，PyTorch 化。

### 8.2 MIT 6.S191（Alexander Amini）—— 现代最强
- 每年 1 月 IAP 短学期，密集 4 周。
- 主讲深度生成模型 / RL / Computer Vision / Efficient ML。

### 8.3 Toronto CSC 413/2547H —— 学术血统纯正
- Hinton 在 Toronto 工作近 40 年，DBN / RBM / 反向传播 / Capsule 都诞生于此。
- CSC 2547H 是 Hinton 退休前最后几年的研究生课。

### 8.4 Berkeley CS 182 / 285（Sergey Levine）
- CS 182 = Deep Neural Nets；CS 285 = Deep RL。

### 8.5 学完后能力
- CS231N：能从零写 CNN、ResNet、attention。
- 6.S191：能从零写 VAE/GAN/Diffusion。
- CSC 413：能从零写 Transformer + RLHF。

---

## §9 自然语言处理

### 9.1 Stanford CS224N（Chris Manning）—— 行业 #1
- 配套教材 Jurafsky & Martin SLP3（《Speech and Language Processing》3rd）。
- 历史覆盖 HMM / PCFG / Word2Vec / Transformer / BERT / GPT。

### 9.2 CMU 11-411/611/711 NLP —— 学术最久
- 11-411：Lori Levin（1980s 一直在教）。
- 11-711 Advanced NLP：覆盖语法理论 / KBP / MT。
- 11-737 Multilingual NLP：Graham Neubig 招牌课之一。

### 9.3 ETH NLP（Ryan Cotterell）—— 形式语言传统
- 强调 FST / WFST / 形态学 / weighted grammar。
- 与统计/神经 NLP 形成对比。

### 9.4 Oxford Deep NLP（Youn Kim, Phil Blunsom）—— 欧洲招牌
- 偏生成/符号神经混合。

### 9.5 学完后能力
- CS224N：能从零写 BERT + fine-tune。
- 11-711：能从零写 LALR parser + CKY。
- ETH NLP：能用 OpenFST 实现形态学引擎。

---

## §10 计算机视觉

### 10.1 Oxford VGG（Andrew Zisserman）—— 历史最强
- VGG 实验室是 VGGNet / Double Caption / FlowNet 的发源地。
- 课程覆盖从 SIFT 到 Transformer。

### 10.2 Berkeley CV（Jitendra Malik）—— 经典学派源头
- 1999 年做了 normalized cuts / shape context 等开创工作。
- 现在（2025）和 Pieter Abbeel 合作做机器人视觉。

### 10.3 CMU 16-385 / 16-720 —— 工程派
- Takeo Kanade 在 CMU 几十年，CV 实验室规模全球最大。
- 16-720 (grad) 覆盖 bundle adjustment / 多视几何。

### 10.4 ETH 3D Vision（Marc Pollefeys）—— 几何派
- 多视几何圣经《Multiple View Geometry》(Hartley & Zisserman) 中的 Zisserman 后来到 Oxford，Pollefeys 继承 ETH 几何传统。
- 强项是 SLAM / 3D 重建。

### 10.5 学完后能力
- Oxford VGG：能从零写 SIFT + ResNet + DETR。
- Berkeley：能从零写 segmentation + metric learning。
- ETH：能从零写 SLAM。

---

## §11 强化学习

### 11.1 Berkeley CS 285（Sergey Levine）—— 全球 #1
- Levine 是 TRPO / SAC / world model 的核心作者。
- YouTube 全套公开，**全球 RL 学习者的事实入口**。

### 11.2 Stanford CS234（Emma Brunskill）
- 偏理论 / online learning / safe RL。

### 11.3 MIT 6.S193（Alexander Amini）
- 1 月 IAP 短期版，与 6.S191 配套。

### 11.4 学完后能力
- CS 285：能从零写 SAC + model-based + world model。
- CS234：能严格推导 Bellman / TD / Q-Learning 收敛性。

---

## §12 理论 CS / ML 理论

### 12.1 Princeton COS 511/512 —— 理论 ML 圣地
- Elad Hazan《Introduction to Online Convex Optimization》作者。
- 覆盖 PAC / VC / Rademacher / online learning / bandits。

### 12.2 CMU 15-251 + 15-351 —— 经典 TCS
- 15-251 Great Ideas 是 CMU 本科 TCS 王牌，覆盖 Cantor / Gödel / Turing / Cook-Levin / Karp。
- 15-351 Algorithms（Guy Blelloch）。

### 12.3 Cambridge Part IB Complexity + Part II Information Theory
- 复杂度类 + 信息论双线并行。

### 12.4 学完后能力
- COS 511：能读 COLT/NeurIPS 理论 track 论文。
- 15-251：能理解 Gödel / Church-Turing / Cook-Levin。

---

## §13 形式化方法 / PL 理论

### 13.1 Oxford Categories, Proofs & Processes（Samson Abramsky 学生群体）
- 范畴论 + 进程演算 + Curry-Howard 三位一体。
- 全球唯一**正式教 category theory 的本科 CS 课程**。

### 13.2 Cambridge Hoare Logic & Model Checking
- C.A.R. Hoare 在剑桥工作时发明了 CSP / Hoare Logic。
- 课程内容直接是 Hoare 的学术遗产。

### 13.3 ETH Formal Methods（David Basin）
- Basin 的 specification language / Alloy / TLA+ 传统。
- 强调"自动验证"。

### 13.4 CMU 15-414（André Platzer）
- Platzer 是 differential dynamic logic 作者，强在 cyber-physical verification。

### 13.5 学完后能力
- Oxford CPP：能理解 intuitionistic type theory / topos。
- Cambridge Hoare Logic：能写 Floyd-Hoare 三元组并证明。
- ETH FM：能用 TLA+ / Alloy 写 spec。

---

## §14 安全 / 密码学

### 14.1 MIT 6.858（Kohno, Roesner）—— 系统 + 安全
- lab：用 ROP/JOP 攻破真实二进制。
- 同时教 sandbox / capability / sandboxing。

### 14.2 Berkeley CS 161（Dawn Song, Raluca Ada Popa）
- Dawn Song 是符号执行 / 模糊测试顶会常客。
- Popa 是 encrypted DB / TEE 专家。

### 14.3 CMU 15-511/15-740
- Nicolas Christin 安全策略 / 网络安全。

### 14.4 ETH Information Security
- David Basin，含 TLS protocol 形式化验证。

### 14.5 学完后能力
- 6.858：能写 ROP exploit + sandbox。
- CS 161：能用 symbolic execution 找 bug。

---

## §15 公平性 / 可信 AI / 因果

### 15.1 ETH Causality（Jonas Peters）—— 全球唯一招牌
- Peters《Elements of Causal Inference》作者。
- 覆盖 PC / FCI / do-calculus / IV / LiNGAM。

### 15.2 Princeton COS 595/597
- Solon Barocas, Moritz Hardt 等的 fairness 经典课。
- Hardt《Fairness and Machine Learning》合著者。

### 15.3 Stanford CS329T / CS324 (Percy Liang)
- 覆盖 RLHF / RLAIF / fairness benchmarks。

### 15.4 学完后能力
- ETH Causality：能从观测数据做因果发现。
- COS 595：能算 demographic parity / equalized odds 并 tradeoff。
- CS329T：能搭 alignment benchmark。

---

## 🎯 一图总结（9 校 × 15 主题）

| 主题 | 头部招牌 | 学术血统 | 工程实战 | 学生最爱 |
|------|---------|---------|---------|---------|
| Intro 编程 | Berkeley 61A | Oxford/Cambridge | CMU 15-112 | Stanford CS106A |
| DSA | Princeton COS 226 | CMU 15-251 | Berkeley CS 61B | MIT 6.006 |
| OS | CMU 15-213 + MIT 6.828 (并列) | Cambridge | MIT xv6 | CMU CSAPP |
| 数据库 | CMU 15-445 Pavlo | MIT 6.830 Morris | Berkeley CS 186 | Stanford CS145 |
| 分布式 | **MIT 6.824 Kaashoek (#1)** | ETH RDS | CMU 15-721 | Berkeley CS162 |
| 经典 AI | Berkeley CS 188 Pacman | CMU 15-381 | Stanford CS221 | MIT 6.034 |
| ML 经典 | **Stanford CS229 Ng (#1)** | CMU 10-701 | Berkeley CS 189 | MIT 6.867 |
| 深度学习 | Stanford CS231N (历史) | Toronto CSC 413 | MIT 6.S191 (现代) | Berkeley CS 182 |
| NLP | **Stanford CS224N Manning (#1)** | CMU 11-411/711 | ETH Cotterell | Oxford Deep NLP |
| CV | Oxford VGG Zisserman | Berkeley Malik | CMU 16-385 | ETH Pollefeys 3D |
| RL | **Berkeley CS 285 Levine (#1)** | Stanford CS234 | MIT 6.S193 | CMU 16-824 |
| 理论 ML | Princeton COS 511 Hazan | Cambridge Part II | CMU 15-251 | MIT 6.046 |
| 形式化 | Oxford CPP | Cambridge Hoare | ETH FM | CMU 15-414 |
| 安全 | MIT 6.858 | Berkeley CS 161 | ETH InfoSec | Princeton COS 432 |
| 因果/公平 | ETH Causality Peters | Princeton COS 595 | Stanford CS329T | CMU 17-800 |

**结论**：每所学校都有它"独占鳌头"的主题。没有任何一所学校在所有主题都是第一——这就是为什么 9 校联合学习是最优策略。

---

**完成日期**：2026-08-12 · 作者：AI Mentor (ai-mentor) + 学生
