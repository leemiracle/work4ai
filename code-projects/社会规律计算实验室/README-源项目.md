# Social Laws · 社会规律研究实验室

> **沿着社会科学的子领域，用图论、博弈论、动力系统、复杂系统、ABM、因果推断、LLM-Agent 仿真多种工具，把"社会规律"从格言变成可推导、可仿真、可证伪的对象。**

---

## 这是什么

这是一个**长期研究项目**，不是教程，也不是科普。它的核心命题是：

> **社会规律是长在子领域里的——合作、不平等、革命、极化、隔离、扩散——每个子领域都有反复出现的数学骨架。把它们抽出来，用 Python 跑一遍，你就能看见"看不见的手"在动。**

每个章节都遵循同一个结构：

1. **历史与故事**——这个规律最早是谁、在什么场景下发现的。
2. **直觉**——一句话比喻，以及"为什么必须发生"。
3. **数学**——关键方程、推导主线、假设与边界。
4. **代码**——从零用 NumPy/NetworkX 实现一遍，并跑出可视化。
5. **批判**——这个模型的局限、失败模式、误用风险。

---

## 为什么按子领域而非方法组织

社会规律的研究有两个轴线：

- **方法轴**：网络、博弈、复杂系统、ABM、因果推断、LLM-Agent
- **子领域轴**：社会关系、合作、不平等、权力政治、文化传播、市场城市

传统教科书按方法分（"博弈论教材"、"网络科学教材"）——这样学完你会**拥有一堆工具，但不知道要修什么**。

本项目反过来：**以子领域为主轴**，方法是工具箱。每个子领域里会自然调用多种方法：

> 研究革命既要博弈论（理性选择参与与否）、又要复杂系统（相变与临界）、又要网络（信息级联）。研究不平等既要 ABM（财富分布涌现）、又要统计（帕累托分布）、又要经济学（Piketty 的 r > g）。

更进一步，**第七个模块专门做交叉研究**——"并结合子领域"——比如：
- 犯罪 × 网络（黑帮网络结构如何影响打击效果）
- 算法 × 政治 × 传播（推荐系统如何放大极化）
- LLM × 社会（用 AI agent 仿真整个小型社会）

| 维度 | 传统按方法分 | **本项目按子领域分** |
|---|---|---|
| 主线 | 工具的内逻辑 | **研究对象的内规律** |
| 工具 | 每模块单一 | **每模块多工具并用** |
| 跨模块 | 弱（各工具独立） | **强（同一现象多种视角）** |
| 故事感 | 工具发展史 | **真实社会议题** |
| 终点 | 掌握工具 | **能解释/预测社会现象** |

---

## 项目结构

```
social-laws/
├── README.md                   ← 你在这里
├── docs/                       ← 方法论与路线图
│   ├── roadmap.md              ← 8-10 周可执行路线
│   ├── math-primer.md          ← 数学自检清单
│   ├── methodology.md          ← ⭐数学如何介入社会科学
│   ├── reading-list.md         ← 经典+前沿文献（西方）
│   ├── cssci-frontiers.md      ← ⭐⭐中国顶刊配套研究（CSSCI 学者方向）
│   └── cssci-real-papers.md    ← ⭐⭐⭐NCPSSD 抓取的真实论文（含作者/期号/页码）
│
├── 00-foundations/             ← 模块0: 方法论 primer
│
├── 01-relations/               ← ⭐子领域1: 社会关系与网络
│   (关系结构如何决定机会 — Granovetter, 小世界, 无标度)
│
├── 02-cooperation/             ← ⭐子领域2: 合作与集体行动
│   (自私个体为何能合作 — 囚徒困境, 演化博弈, Nowak 五规则)
│
├── 03-inequality/              ← 子领域3: 不平等与社会分层
│   (财富差异如何涌现固化 — 帕累托, Sugarscape, Piketty)
│
├── 04-power-politics/          ← 子领域4: 权力、政治与冲突
│   (革命/投票/极化 — 阿罗不可能, Kuran 相变, 极化涌现)
│
├── 05-culture-cognition/       ← 子领域5: 文化、传播、认知
│   (文化演化、信息扩散 — Boyd-Richerson, SIR, 观点动力学)
│
├── 06-markets-cities/          ← 子领域6: 市场、组织、城市
│   (经济网络、隔离、规模法则 — Schelling, West 幂律)
│
├── 07-crosscuts/               ← ⭐⭐子领域7: 交叉专题（"并结合"）
│   (跨子领域综合研究 — 犯罪×网络, 算法×极化, LLM×社会)
│
├── projects/                   ← 可演示作品集
└── notes/                      ← 论文精读 + 读书笔记
```

---

## 七子领域路线（速览）

| 阶段 | 子领域 | 时长 | 核心命题 | 主要工具 |
|---|---|---|---|---|
| **0** | foundations | 1 周 | 数学如何介入社会 | 全部 |
| **1** | relations | 2 周 | 关系结构决定机会 | 网络、图论 |
| **2** | cooperation | 2 周 | 合作如何可能 | 博弈、演化 |
| **3** | inequality | 1 周 | 不平等如何涌现 | ABM、统计 |
| **4** | power-politics | 1 周 | 革命相变与极化 | 阿罗、相变 |
| **5** | culture-cognition | 1 周 | 文化演化与传播 | SIR、双传承 |
| **6** | markets-cities | 2 周 | 隔离与规模法则 | Schelling、West |
| **7** | crosscuts | 持续 | 跨子领域综合 | 多工具组合 |

详见 [`docs/roadmap.md`](docs/roadmap.md)。

---

## 核心方法论（一段话版）

社会研究有两条长期对立又互补的路径：**还原论**（把社会还原到个体决策——博弈论、理性选择）与**涌现论**（个体规则简单，群体产生不可预测的总体模式——复杂系统、ABM）。本项目的态度是**两条腿走路**，再加第三条腿：**网络化**（个体嵌入关系结构），第四条腿：**数据驱动**（现实校准）。

警惕 **"物理学妒忌"**——不是所有社会现象都有漂亮的解析解，有时候仿真就是答案，有时候连仿真也答不了。详见 [`docs/methodology.md`](docs/methodology.md)。

---

## 如何使用这个仓库

### 1. 先做数学自检
打开 [`docs/math-primer.md`](docs/math-primer.md)。每项 3 道题，做不出就跳到 `math-learning` skill 补课。

### 2. 按路线图推进
跟着 [`docs/roadmap.md`](docs/roadmap.md) 一周一周走。**每周必须有可运行的代码产出**，否则不算完成。

### 3. 跑代码
```bash
cd /data/usershare/ai/social-laws/01-relations/
python3 01-graph-basics.py
```
所有代码设计为：纯 NumPy/SciPy/NetworkX/Matplotlib，**不依赖外部 API**（07-crosscuts 的 LLM 实验除外）。

### 4. 做笔记
读完每节，在 `notes/` 下写一份 300-800 字复盘：**这个模型让我惊讶的是什么？它的局限是什么？**

---

## 与其他项目 / Skill 的关系

| 资源 | 在本项目中的角色 |
|---|---|
| `math-learning` skill | 数学补课主入口 |
| `agent-guide` 项目 | 07-crosscuts 的 LLM-Agent 工程基础 |
| `ml-theory` skill | 因果推断、统计学习支撑 |
| `concept-3layer` skill | 每节内容生成器 |
| `paper-mastery` skill | `notes/` 论文精读工作流 |
| `progress-tracker` skill | 每周末回顾进度 |

---

## 学习哲学（写给未来的自己）

1. **研究对象 > 工具**：方法是刀，社会现象是肉。不要恋刀忘肉。
2. **动手 > 输入**：1 个能讲清楚的仿真 > 10 本读过的书。
3. **可视化优先**：每个模型都要画出来，看不见的不算理解。
4. **从零实现**：先纯 NumPy 写一遍，再用库。
5. **拥抱反直觉**：Schelling 隔离、Granovetter 弱连带、Nowak 合作——这些反直觉正是数学化最有价值之处。
6. **跨子领域结合**：最有趣的洞见往往在子领域边界（犯罪 × 网络、算法 × 政治、文化 × 演化）。
7. **批判永不停歇**：每个模型都有局限性，警惕"模型崇拜"。

---

## 灵感来源

- **Schelling, Thomas** — *Micromotives and Macrobehavior* (1978)
- **Epstein, Joshua** — *Generative Social Science* (2007)
- **Granovetter, Mark** — *The Strength of Weak Ties* (1973)
- **Nowak, Martin** — *Evolution of Cooperation* (2006)
- **Watts, Duncan** — *Everything Is Obvious* (2011)
- **Salganik, Matthew** — *Bit by Bit* (2017)
- **Park, Joon Sung 等** — *Generative Agents* (2023)
- **Piketty, Thomas** — *Capital in the 21st Century* (2014)

---

## 开始

打开 [`docs/roadmap.md`](docs/roadmap.md)，从模块 0 开始。

> **"如果你没能生长出它，你就没理解它。" —— Joshua Epstein**

---

*项目状态：v0.3 · 加入 CSSCI 中国顶刊配套研究 · 2026-07*
