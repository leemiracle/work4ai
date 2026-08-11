# CS221: Artificial Intelligence: Principles and Techniques

> **课程官网**: https://stanford-cs221.github.io/
> **当前学期**: Autumn 2025-2026
> **讲师**: **Percy Liang**（Stanford AI Lab, HELM/CRFM 创始人）
> **Head CA**: Ken Liu
> **上课时间**: 周一/周三 13:30-14:50，NVIDIA Auditorium
> **前置课程**: CS106A/B（编程）、CS103（离散数学）、CS109（概率论）、Math 51（线性代数）
> **评分构成**: 8 次每周作业（40%）+ 期末考试（60%）+ 项目（最多 +1.5% 额外分）
> **GitHub**: https://github.com/stanford-cs221/autumn2025-lectures
> **关联项目代码**: `topic2-agent-v2/dspy_framework.py`（LLM 框架，CS221 思想的延伸）

---

## 📚 课程定位

CS221 是斯坦福大学 **AI 入门的旗舰课程**，由 **Percy Liang** 教授主讲（Autumn 2025）。人工智能的目标是用**严谨的数学工具**解决复杂的现实问题。CS221 不是一门"深度学习课"——它是一门系统性地教授 AI 四大支柱（**学习、搜索、不确定性推理、决策**）的基础课，为所有后续 AI/ML 课程打下统一的理论框架。

### 核心设计哲学

CS221 围绕一个统一框架组织所有 AI 技术：

```
                        ┌─────────────────┐
   现实世界问题 ───────> │  Model (模型)    │
                        │  + Loss (损失)   │ ───> AI 系统
                        │  + Optimize (优化)│
                        └─────────────────┘
```

**每一个 AI 问题都可以分解为三个组件**：
1. **Model（模型）**：描述世界的数学结构（线性模型、决策树、贝叶斯网络、MDP...）
2. **Loss（损失函数）**：定义"好坏"的标准（均方误差、交叉熵、负对数似然...）
3. **Optimize（优化算法）**：找到最优参数（梯度下降、回溯搜索、值迭代...）

这个 **Model + Loss + Optimize** 框架贯穿课程始终——从线性回归到贝叶斯网络到强化学习，所有算法都被统一在这同一套语言下。

### 2025 年新增内容

Autumn 2025 版本新增了两个重要讲次：
- **Lecture 17: Language Models**（大语言模型）——反映 LLM 时代的 AI 格局变化
- **Lecture 18: AI & Society**（AI 与社会）——嵌入式伦理教育（Embedded Ethics）
- **Lecture 19: AI Supply Chains**（AI 供应链）——LLM 训练的数据/算力/人力链条

---

## 🎯 学习目标

完成本课程后，你将能够：

1. **掌握 AI 的统一框架**——用 Model + Loss + Optimize 分析任何 AI 问题
2. **实现机器学习算法**——线性回归、逻辑回归、梯度下降、特征工程
3. **解决搜索与规划问题**——BFS/DFS/A*、一致性搜索、对抗搜索（Minimax/Alpha-Beta）
4. **建模序贯决策**——马尔可夫决策过程（MDP）、值迭代、策略迭代、Q-Learning
5. **推理不确定性**——贝叶斯网络、精确推理、近似推理（MCMC）
6. **理解逻辑推理**——一阶逻辑、SAT 求解、知识表示
7. **批判性思考 AI 的社会影响**——公平性、可解释性、AI 供应链中的权力关系

---

## 📅 完整模块（按周/讲）

> 以下基于 Autumn 2025 官方日历（共 20 讲，10 周）

### Week 1: 概述与机器学习 I

| 讲次 | 主题 | 关键概念 |
|------|------|----------|
| **L1** | Overview | AI 全景、Model+Loss+Optimize 框架、课程导览 |
| **L2** | Learning I | 线性回归、损失函数（MSE）、梯度下降 |

**HW1 [Foundations]**: 基础复习——线性代数、概率、Python（due Week 2 Tue）

### Week 2: 机器学习 II-III

| 讲次 | 主题 | 关键概念 |
|------|------|----------|
| **L3** | Learning II | 逻辑回归、交叉熵损失、分类 |
| **L4** | Learning III | 特征工程、正则化、模型选择、泛化 |

**HW2 [Sentiment]**: 情感分类——用逻辑回归 + 特征工程实现文本分类（due Week 3 Tue）

### Week 3: 搜索 I-II

| 讲次 | 主题 | 关键概念 |
|------|------|----------|
| **L5** | Search I | 搜索问题形式化、BFS、DFS、UCS、A* |
| **L6** | Search II | 一致性（Consistency）、启发式设计、约束满足问题（CSP）|

**HW3 [Route]**: 路线规划——用 A* 实现城市导航（due Week 4 Tue）

### Week 4: 马尔可夫决策过程 I-II

| 讲次 | 主题 | 关键概念 |
|------|------|----------|
| **L7** | MDPs I | MDP 定义、策略、值函数 V(s)/Q(s,a)、贝尔曼方程 |
| **L8** | MDPs II | 值迭代（Value Iteration）、策略迭代（Policy Iteration）|

**HW4 [Mountaincar]**: 控制 MountainCar——用 MDP 求解器控制小车爬坡（due Week 5 Tue）

### Week 5: MDPs III 与博弈 I

| 讲次 | 主题 | 关键概念 |
|------|------|----------|
| **L9** | MDPs III | 强化学习入门、Q-Learning、探索 vs 利用 |
| **L10** | Games I | 博弈论、Minimax、期望最大化（Expectimax）|

**HW5 [Pacman]**: Pac-Man——用搜索 + MDP 实现 Pac-Man 智能体（due Week 6 Tue）

### Week 6: 博弈 II 与贝叶斯网络 I

| 讲次 | 主题 | 关键概念 |
|------|------|----------|
| **L11** | Games II | Alpha-Beta 剪枝、蒙特卡洛树搜索（MCTS）|
| **L12** | Bayesian Networks I | 贝叶斯网络定义、条件独立性、D-分离 |

**HW6 [Bayesian]**: 贝叶斯网络——构建概率图模型进行推理（due Week 7 Fri）

### Week 7: 贝叶斯网络 II-III

| 讲次 | 主题 | 关键概念 |
|------|------|----------|
| **L13** | Bayesian Networks II | 精确推理（变量消元）、信念传播 |
| **L14** | Bayesian Networks III | 近似推理、马尔可夫链蒙特卡洛（MCMC）、采样 |

**HW7 [Logic]**: 从语言到逻辑——自然语言→逻辑表达式（due Week 8 Fri）

### Week 8: 逻辑 I-II

| 讲次 | 主题 | 关键概念 |
|------|------|----------|
| **L15** | Logic I | 一阶逻辑（FOL）、知识表示、逻辑推理 |
| **L16** | Logic II | SAT 求解、归结（Resolution）、DPLL 算法 |

### Week 9: 现代主题（🆕 2025 新增）

| 讲次 | 主题 | 关键概念 |
|------|------|----------|
| **L17** 🆕 | Language Models | LLM 架构、训练范式、RLHF、prompting |
| **L18** 🆕 | AI & Society | AI 公平性、可解释性、嵌入式伦理 |

> ⚠️ **11/19 (Wed): 期末考试 6-9pm（占 60%）**

### Week 10: AI 供应链与总结（🆕 2025 新增）

| 讲次 | 主题 | 关键概念 |
|------|------|----------|
| **L19** 🆕 | AI Supply Chains | LLM 训练的数据采集、标注劳工、算力垄断 |
| **L20** | Fireside Chat, Conclusion | 课程总结、AI 的未来方向 |

**HW8 [Society]**: AI 与社会——伦理分析论文（due Week 10 Fri）

---

## 🧮 核心算法/数学

### 1. 统一框架：Model + Loss + Optimize

```python
# CS221 的核心范式——每个算法都是这个模板的实例
model = SomeModel()           # 1. Model: 定义假设空间
loss = compute_loss(model, data)  # 2. Loss: 定义目标
model = optimize(loss)         # 3. Optimize: 求解最优参数
```

| 问题 | Model | Loss | Optimize |
|------|-------|------|----------|
| 线性回归 | $f(x) = w^Tx + b$ | MSE: $\sum(y_i - f(x_i))^2$ | 梯度下降 |
| 逻辑回归 | $p(y=1|x) = \sigma(w^Tx)$ | 交叉熵 | 梯度下降 |
| 搜索 | 状态空间图 | 路径代价 | A* / BFS / DFS |
| MDP | $(S, A, T, R, \gamma)$ | 累计折扣奖励 | 值迭代 |
| 贝叶斯网络 | DAG + 条件概率表 | 负对数似然 | EM / 最大似然 |

### 2. 梯度下降（Gradient Descent）

$$w_{t+1} = w_t - \eta \nabla_w \mathcal{L}(w_t)$$

**线性回归的梯度**（MSE 损失）：
$$\nabla_w \mathcal{L} = \frac{2}{n} X^T(Xw - y)$$

### 3. A* 搜索算法

$$f(n) = g(n) + h(n)$$

- $g(n)$：从起点到 $n$ 的实际代价
- $h(n)$：从 $n$ 到目标的**启发式估计**（必须 admissible——不高估）

**一致性条件**：$h(n) \leq c(n, n') + h(n')$ → A* 保证最优且不重复展开节点

### 4. 马尔可夫决策过程（MDP）

**定义**: 元组 $(S, A, T(s'|s,a), R(s,a,s'), \gamma)$

**贝尔曼方程**（值函数）：
$$V^*(s) = \max_{a \in A} \sum_{s'} T(s'|s,a) \left[ R(s,a,s') + \gamma V^*(s') \right]$$

**最优 Q 函数**：
$$Q^*(s,a) = \sum_{s'} T(s'|s,a) \left[ R(s,a,s') + \gamma \max_{a'} Q^*(s',a') \right]$$

**值迭代算法**:
```
重复直到收敛:
    对每个状态 s:
        V(s) = max_a Σ T(s'|s,a)[R + γ V(s')]
```

### 5. Q-Learning（无模型 RL）

$$Q(s,a) \leftarrow Q(s,a) + \alpha \left[ r + \gamma \max_{a'} Q(s',a') - Q(s,a) \right]$$

关键特性：**off-policy**——可以用任何行为策略（如 ε-greedy）收集数据来学习最优策略。

### 6. 博弈搜索（Minimax + Alpha-Beta）

**Minimax**（零和博弈）：
$$V(s) = \begin{cases} \max_{a} V(s') & \text{如果 } s \text{ 是 MAX 节点} \\ \min_{a} V(s') & \text{如果 } s \text{ 是 MIN 节点} \end{cases}$$

**Alpha-Beta 剪枝**：维护 $\alpha$（MAX 的当前最优值）和 $\beta$（MIN 的当前最优值），当 $\alpha \geq \beta$ 时剪枝。

### 7. 贝叶斯网络推理

**联合分布分解**:
$$P(X_1, ..., X_n) = \prod_{i=1}^{n} P(X_i | \text{Parents}(X_i))$$

**变量消元**（精确推理）：利用条件独立性，通过消除非查询变量来高效计算边缘概率。

---

## 💻 项目代码

### `topic2-agent-v2/dspy_framework.py`

**实现内容**：DSPy 风格的声明式 LLM 框架，体现 CS221 的 Model+Loss+Optimize 思想在 LLM 时代的延伸。

| 模块 | 类/函数 | 功能 |
|------|---------|------|
| 输入输出契约 | `Signature` | 声明式定义 LLM 调用的输入/输出字段 |
| 可组合模块 | `Module` | 类似 PyTorch 的模块化设计 |
| 优化器 | `BootstrapFewShot` | 自动选择最优 few-shot 示例 |
| GEPA 模拟 | `GEPAOptimizer` | 进化式 prompt 优化 |
| LLM 客户端 | `LLMClient`（来自 `core/llm.py`）| 统一的 LLM 调用接口 |

**CS221 框架映射**:
```
CS221: Model + Loss + Optimize
  ↕ 映射到 LLM 时代
DSPy:  Signature (Model) + Metric (Loss) + Optimizer (Optimize)
```

**运行命令**:
```bash
cd topic2-agent-v2
python3 dspy_framework.py
# 演示: Signature 定义 → Module 组合 → Bootstrap FewShot 优化
```

### CS221 原版作业（8 次）

| HW | 代号 | 应用场景 | AI 技术 | 难度 |
|----|------|----------|---------|------|
| 1 | Foundations | 基础复习 | 线性代数+概率+Python | ⭐ |
| 2 | Sentiment | 情感分类 | 逻辑回归+特征工程 | ⭐⭐ |
| 3 | Route | 路线规划 | A*搜索+启发式 | ⭐⭐ |
| 4 | Mountaincar | 控制小车 | MDP+值迭代 | ⭐⭐⭐ |
| 5 | Pacman | Pac-Man 智能体 | 搜索+RL+博弈 | ⭐⭐⭐⭐ |
| 6 | Bayesian | 概率推理 | 贝叶斯网络+变量消元 | ⭐⭐⭐⭐ |
| 7 | Logic | 自然语言→逻辑 | 一阶逻辑+知识表示 | ⭐⭐⭐ |
| 8 | Society | AI 伦理 | 批判性分析 | ⭐⭐ |

---

## 📊 关键论文/教材

### 核心教材（全部免费在线）

- **Russell & Norvig**. [*Artificial Intelligence: A Modern Approach*](http://aima.cs.berkeley.edu/) (AIMA). — **AI 圣经**，CS221 的非官方参考书，覆盖所有主题
- **Sutton & Barto**. [*Reinforcement Learning: An Introduction*](http://incompleteideas.net/book/the-book-2nd.html). — RL 领域的奠基教材（免费）
- **Koller & Friedman**. [*Probabilistic Graphical Models*](http://mitpress.mit.edu/books/probabilistic-graphical-models). — 贝叶斯网络权威（CS228 教材）
- **Hastie, Tibshirani & Friedman**. [*The Elements of Statistical Learning*](https://web.stanford.edu/~hastie/ElemStatLearn/). — 机器学习的统计视角（免费）

### 关键论文

- **Tesauro (1995)**. *Temporal Difference Learning and TD-Gammon*. *CACM*. — RL 的经典成功案例
- **Kocsis & Szepesvári (2006)**. *Bandit based Monte-Carlo Planning*. — MCTS/UCT 算法
- **Mnih et al. (2015)**. [Human-level control through deep reinforcement learning](https://www.nature.com/articles/nature14236). *Nature*. — DQN
- **Silver et al. (2016)**. *Mastering the game of Go with deep neural networks and tree search*. *Nature*. — AlphaGo
- **Pearl (1988)**. *Probabilistic Reasoning in Intelligent Systems*. — 贝叶斯网络奠基
- **Brown et al. (2020)**. [Language Models are Few-Shot Learners](https://arxiv.org/abs/2005.14165). — GPT-3（Lecture 17 参考）

### LLM 时代相关（2025 新增讲次）

- **Khattab et al. (2024)**. [DSPy: Compiling Declarative LLM Calls into Pipelines](https://arxiv.org/abs/2310.03714). *ICLR*. — 本项目 `dspy_framework.py` 的理论基础
- **Ouyang et al. (2022)**. *Training language models to follow instructions with human feedback*. — RLHF
- **Bender et al. (2021)**. [*On the Dangers of Stochastic Parrots*](https://dl.acm.org/doi/10.1145/3442188.3445922). — AI 伦理（Lecture 18 参考）

---

## 🎯 学习路径

```
Week 1-2  ┌─ 机器学习（Model+Loss+Optimize 的首次实践）
          │   └─ HW2 Sentiment: 从零实现逻辑回归
          │   ⚠️ 这是整个课程的思维范式基石
          │
Week 3    ├─ 搜索（从"学习"切换到"规划"）
          │   └─ HW3 Route: A* 算法 + 启发式设计
          │
Week 4-5  ├─ MDP + 强化学习（不确定性下的决策）
          │   └─ HW4 Mountaincar + HW5 Pacman
          │   ⚠️ 贝尔曼方程是本模块的数学核心
          │
Week 5    ├─ 博弈论（多智能体决策）
          │   └─ Minimax + Alpha-Beta + MCTS
          │
Week 6-7  ├─ 贝叶斯网络（不确定性推理）
          │   └─ HW6 Bayesian: 变量消元 + 采样
          │   ⚠️ 概率推理是 AI 最优雅的部分之一
          │
Week 8    ├─ 逻辑推理（符号 AI）
          │   └─ HW7 Logic: 从自然语言到一阶逻辑
          │
Week 9-10 ├─ 🆕 现代主题: LLM + AI 伦理 + AI 供应链
          │   └─ 理解 AI 从"经典算法"到"LLM 时代"的转变
          │
Exam      └─ 11/19 期末考试（60%）——覆盖全部模块
```

### 给自学者的建议

1. **先吃透 Model+Loss+Optimize 框架**——这是 CS221 的"武功心法"，掌握后所有算法都变得清晰
2. **认真做 HW2 (Sentiment)**——从零实现逻辑回归，理解梯度下降的每一步
3. **手推贝尔曼方程**——MDP/RL 的所有推导都基于它
4. **Pacman 作业是最有趣的**——把搜索、MDP、博弈融为一体的综合实战
5. **对比经典 AI vs LLM**——2025 版本的 L17-L19 帮你理解 AI 范式转变

---

## 💡 反思

### 为什么 CS221 是 AI 教育的黄金标准

1. **统一框架的优雅**：Percy Liang 的天才之处在于用 Model+Loss+Optimize 这一个框架统一了从线性回归到 MCTS 到贝叶斯网络的所有 AI 技术。学完后你获得的不只是几个算法，而是一种**分析任何 AI 问题的方法论**。
2. **广度与深度的平衡**：CS221 覆盖了 AI 的全部经典支柱（ML/搜索/MDP/博弈/贝叶斯/逻辑），每个主题都有动手编程作业，深度足以建立真正的理解。
3. **与时俱进的更新**：2025 年新增的 LLM、AI 社会和 AI 供应链讲次，反映了 Percy Liang 对 AI 领域格局变化的敏锐判断（他本人是 HELM/CRFM 的创始人，LLM 评估的领军人物）。
4. **嵌入式伦理教育**：CS221 专门配有 Ethics CA 团队，将伦理讨论嵌入技术课程本身——这在 AI 时代尤为重要。

### 常见学习陷阱

- **知识点太多，容易迷失**：8 周覆盖 6 大 AI 主题，节奏极快。必须抓住 Model+Loss+Optimize 这根主线。
- **概率论是硬门槛**：贝叶斯网络模块重度依赖 CS109 的概率基础。如果不熟条件概率，先复习。
- **编程作业的 autograder 很严格**：CS221 的自动评分以严格著称——检查输出格式！
- **Honor Code 极其严格**：不能看同学的代码/答案，不能上传到公开 GitHub，甚至不能用 AI "检查"你的答案。

---

## 🚀 扩展

### 深入方向

CS221 是斯坦福 AI 课程体系的"入口"，几乎每个主题都对应一门深入课程：

| CS221 主题 | 深入课程 | 焦点 |
|-----------|----------|------|
| 机器学习 | **CS229** (Machine Learning) | ML 数学严谨化 |
| 深度学习 | **CS231N** (CV) / **CS224N** (NLP) | 神经网络专项 |
| 强化学习 | **CS234** (RL) | MDP/RL 深入 |
| 博弈论 | **CS269I** (Incentives) | 算法博弈论 |
| 概率图模型 | **CS228** (PGM) | 贝叶斯网络/马尔可夫随机场 |
| LLM | **CS324** (LLM) / **CS25** (Transformers) | 大模型前沿 |
| AI 安全 | **CS329I** | AI 对齐与安全 |
| 多智能体 | **CS238** (Decision Making) | 决策理论 |

### 实战项目建议

1. **用 Model+Loss+Optimize 框架重新分析你做过的每个 AI 项目**——加深理解
2. **实现一个完整的 Pac-Man 智能体**——结合搜索 + RL + 博弈（CS221 HW5 的扩展）
3. **构建一个贝叶斯网络医疗诊断系统**——实践概率推理
4. **用 DSPy 框架优化 LLM pipeline**——本项目 `dspy_framework.py` 的延伸
5. **复现经典 RL 论文**——如 DQN 或 AlphaGo 的简化版

### 与其他课程的关系

```
CS106B (编程) + CS103 (离散数学) + CS109 (概率) + Math51 (线代)
                          │
                          ▼
                   CS221 (AI 入门)  ◄── 你在这里
                          │
          ┌───────────────┼───────────────┐
          ▼               ▼               ▼
     CS229 (ML)      CS224N (NLP)    CS234 (RL)
          │               │               │
          ▼               ▼               ▼
     CS324 (LLM)    CS25 (TF)       CS329I (Safety)
```

CS221 是整个斯坦福 AI 课程树的**根节点**——无论你想深入机器学习、自然语言处理、计算机视觉、强化学习还是 AI 安全，CS221 都提供了必要的统一理论框架和基础工具箱。它是"AI 从业者的通识教育"。

---

> *"The goal of AI is to tackle complex real-world problems with rigorous mathematical tools."* — Percy Liang, CS221
