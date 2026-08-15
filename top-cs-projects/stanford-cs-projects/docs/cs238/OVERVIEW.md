# CS238 / AA228: Decision Making under Uncertainty

> Stanford University, Autumn 2025（与 AA228 联合开设，同名同内容）
> Instructors: **Mykel J. Kochenderfer**（航空工程 + AI，FAA/NTSB 航空安全顾问）
> Time: Tue/Thu 9:00–10:20 AM, NVIDIA Auditorium
> Prerequisites: **CS109**（概率）+ **CS106A**（编程，课程用 Julia）
> Textbook: Kochenderfer, *Algorithms for Decision Making*, MIT Press 2022（[免费 PDF](https://algorithmsbook.com/)）
> Difficulty: ⭐⭐⭐⭐⭐
> 官网：http://cs238.stanford.edu/ ｜ 镜像：https://aa228.stanford.edu/

---

## 📚 课程定位（独特价值）

Stanford **不确定决策的数学旗舰课**。作者 Kochenderfer 就是教材作者，课程把整本书当官方讲义。它的独特价值在于：

- **一条主线**：用**统一的概率图模型 + 贝叶斯决策框架**，把贝叶斯网络 → 影响图 → MDP → POMDP → RL 串成一个递进的体系，而不是把 RL 孤立讲。
- **应用偏航空/自主系统**：空中交通管制（TCAS 的下一代）、无人机探测、自动驾驶、火星探测车——全部是 Kochenderfer 在 MIT Lincoln Lab / Stanford 做过的真实系统。
- **Julia 原生**：教材所有算法用 Julia 实现（`POMDPs.jl` 生态），不是 Python 的 OpenAI Gym 那一套，更贴近科学计算与离散状态空间。
- **与 CS221 的区别**：CS221 是「机器学习的菜单」，CS238 是「决策的公理化体系」——从理性公理出发，推导出期望效用最大化，再到算法实现。

> 四大主题（官网原文）：
> 1. 存在定义理性行为的**原则性数学框架**。
> 2. 这些计算方法有时能得出**反直觉但更优**的决策。
> 3. 成功应用取决于**表示与近似**的选择。
> 4. 同一套方法可应用于**完全不同的领域**。

---

## 🎯 学习目标

1. 掌握决策的**数学模型与求解方法**（贝叶斯网络、MDP、POMDP、RL）。
2. 能**实现并扩展**关键决策算法（两个编程项目，用 Julia）。
3. 能把真实应用**形式化为数学问题**（proposal 阶段）。
4. 对自己感兴趣的方向做**深度 final project**（35% 权重，可投会议）。
5. 能**批判性地评价**不同决策方法（peer review 环节）。
6. 理解**部分可观测**（POMDP）为什么是真实世界的常态，而非特例。

---

## 📅 完整模块（基于教材 *Algorithms for Decision Making* 四大部分）

### Part I: Probabilistic Reasoning（概率推理）
- 概率论回顾：联合分布、条件、贝叶斯法则
- **贝叶斯网络**（Bayesian Networks）：D-separation、参数学习、结构学习
- 精确推断：变量消元、信念传播
- 近似推断：**采样**（直接采样、拒绝采样、似然加权、Gibbs）、**变分推断**

### Part II: Sequential Problems（序贯决策，完全可观测）
- 理性决策公理 → 期望效用
- **Markov Decision Process (MDP)**
- **动态规划**：价值迭代、策略迭代
- 带约束的 MDP、离散 vs 连续
- 轨迹规划、线性规划求解

### Part III: Model Uncertainty（模型未知 → RL）
- **强化学习**设定：model-based vs model-free
- **模型预测**（最大似然模型）
- **Exploration**：探索-利用困境、UCB、Thompson 采样
- **值函数方法**：Q-learning、SARSA
- **策略搜索**：策略梯度、REINFORCE
- 模仿学习（Behavior Cloning）

### Part IV: State Uncertainty（部分可观测 → POMDP）
- **信念状态**（belief state）= 对真实状态的概率分布
- **贝叶斯滤波**（Bayes filter）、Kalman Filter、Particle Filter
- **POMDP**：定义、信念 MDP 转化
- 离线求解：SARSOP、点集方法
- 在线求解：**POMCP**（Monte Carlo Tree Search for POMDP）
- **Influence Diagram** + 监控与诊断

---

## 🧮 核心算法 / 数学

### 贝叶斯滤波（信念更新，本项目核心）
$$b'(s') = \eta \, O(o \mid s', a) \sum_s T(s' \mid s,a)\, b(s)$$
- $b(s)$：当前对状态 $s$ 的信念
- $T$：转移模型，$O$：观测模型，$\eta$：归一化常数

### Bellman 方程（完全可观测 MDP）
$$U(s) = \max_a \left[ R(s,a) + \gamma \sum_{s'} T(s' \mid s,a)\, U(s') \right]$$

### POMDP 价值函数（分段线性凸，PWLC）
$$V(b) = \max_{\alpha \in \Gamma} \sum_s \alpha(s)\, b(s)$$
- $\alpha$ 向量是价值函数的「片」， belief 空间上是凸的分片线性

### Q-learning（无模型 RL）
$$Q(s,a) \leftarrow Q(s,a) + \alpha\,[r + \gamma \max_{a'} Q(s',a') - Q(s,a)]$$

### 策略梯度（REINFORCE）
$$\nabla_\theta J = \mathbb{E}\left[ \nabla_\theta \log \pi_\theta(a\mid s)\, G_t \right]$$

### Thompson 采样（探索）
$$\pi(a) = \int \theta\, p(\theta \mid \text{history})\, d\theta \quad \text{(对每个 arm 采样后选 argmax)}$$

---

## 💻 项目代码

📁 `supplementary/grad_projects.py::cs238_demo`

**实现**（纯 Python，无外部依赖）：
1. ✅ **POMDP 数据结构**：状态/动作/观测/转移/观测模型/奖励
2. ✅ **信念状态（BeliefState）+ 贝叶斯滤波**：`update(action, observation, pomdp)`
3. ✅ 离散 3 房间「找宝藏」仿真：转移概率 + 观测模型 + 奖励
4. ✅ 简单信念策略：`belief.most_likely() == 'right' → search`

### 运行
```bash
cd stanford-cs-projects
python3 supplementary/grad_projects.py     # 跑全部 5 个 demo
python3 -c "from supplementary.grad_projects import cs238_demo; cs238_demo()"
```

**输出示例**（信念随观测收敛）：
```
📋 CS238: POMDP - 模糊世界中的决策
   初始 belief: {'left': 0.333, 'center': 0.333, 'right': 0.333}
   Step 0: action=move_right, obs=see_empty, reward=0,  belief={'left':..., 'right':0.43}
   Step 1: action=move_right, obs=see_treasure, reward=10, belief={'right':0.88}
```

### 代码与课程的对应关系

| 课程概念 | 代码位置 |
|----------|----------|
| POMDP 六元组 $(S,A,O,T,O,R)$ | `POMDP` dataclass |
| Bayes filter 预测步 $\sum T\, b$ | `BeliefState.update` 内 `pred` |
| Bayes filter 观测更新 $O \cdot pred$ | `BeliefState.update` 内 `obs_prob` |
| 信念策略（myopic） | `cs238_demo` 中 `if belief.most_likely()=='right'` |
| 仿真采样（transition + observation） | `cs238_demo` 的 episode 循环 |

> 注：本项目用 Python 演示核心思想；课程正式作业用 **Julia + POMDPs.jl**，并要求实现完整 SARSOP/POMCP。要冲击 leaderboard 需自己把策略改成 PBVI 或 POMCP。

---

## 📊 关键论文（按 P0/P1/P2 分级）

### 🔴 P0（必读，奠基）
1. **Bellman 1957** *Dynamic Programming* — DP 与最优性原理的开山之作
2. **Sutton & Barto** *Reinforcement Learning: An Introduction*（[在线版](http://incompleteideas.net/book/RLbook2020.pdf)）— RL 圣经
3. **Kochenderfer et al. 2022** *Algorithms for Decision Making*, MIT Press — 本课教材（[免费 PDF](https://algorithmsbook.com/)）
4. **Kaelbling, Littman & Cassandra 1998** "Planning and acting in partially observable stochastic domains" *AIJ* — POMDP 经典综述

### 🟡 P1（重要方法）
5. **Kurniawati, Hsu & Lee 2008** "SARSOP: Efficient Point-Based POMDP Planning by Regressing Optimally Reached States" — 离线 POMDP 求解器
6. **Silver & Veness 2010** "Monte-Carlo Planning in Large POMDPs" — **POMCP**，在线 MCTS 解 POMDP（[参考](https://papers.nips.cc/paper/4031-monte-carlo-planning-in-large-pomdps)）
7. **Watkins 1989** Q-learning 博士论文 — model-free RL 起点
8. **McMahan et al. 2013** "Solving POMDPs with QA" — 用于航空避撞应用
9. **Kochenderfer 2015** *Decision Making Under Uncertainty: Theory and Application*, MIT Press — 前一本教材，航空案例多

### 🟢 P2（拓展）
10. **Bertsekas** *Dynamic Programming and Optimal Control* — 理论深井
11. **Kaelbling, Littman & Moore 1996** "Reinforcement Learning: A Survey"
12. **Oliehoek & Amato 2016** *A Concise Introduction to Decentralized POMDPs* — 多智能体扩展
13. **Mnih 2015** DQN（[arXiv:1312.5602](https://arxiv.org/abs/1312.5602)）— 深度 RL
14. **Schulman 2017** PPO（[arXiv:1707.06347](https://arxiv.org/abs/1707.06347)）

---

## 🎯 学习路径（按角色）

| 角色 | 推荐路线 |
|------|----------|
| **机器人/自动驾驶研究** | CS238 → CS237A（运动规划）→ POMDP final project |
| **RL 方向** | CS238（理论根基）→ CS234（RL 专题）→ 读 PPO/SAC |
| **航空/安全系统** | CS238 → 读 Kochenderfer 的 TCAS/ACAS-Xu 论文 |
| **AI 入门决策理论** | CS238（3 单元）+ 教材通读，跳过 final project |
| **想发论文** | 选 4 单元版本，final project 扩写成会议投稿 |

### 评测与成绩构成（官网数据）
- Projects 20%（Project1 10% + Project2 10%）
- 3 次 Quiz 45%（各 15%）
- Final Project 35%（proposal 5% + status 5% + paper/video 20% + peer review 5%）
- **亮点政策**：作业 72 小时内迟交**零惩罚**（quiz 除外）；quiz < 70% 可写 reflection 找回一半分数

---

## 💡 反思与批判

1. **POMDP 的可解性陷阱**：理论优雅，但 belief 空间随状态数指数膨胀。真实系统（如自动驾驶）几乎都靠**强近似 + 在线规划**，离线精确解只对小问题可行——课程的 Julia 作业容易让学生高估 POMDP 的实用规模。
2. **Julia 的双刃剑**：算法表达优美、科学计算生态强，但工业界 RL 栈（Gym/Stable-Baselines/Ray）几乎全是 Python。学完要主动做 Python 移植练习。
3. **理性公理的局限**：课程从 von Neumann–Morgenstern 效用公理出发推导「最优」，但**人类不是期望效用最大化者**（前景理论）。医疗、金融等高 stakes 场景必须叠加行为经济学修正。
4. **exploration 的现实代价**：UCB/Thompson 在仿真里漂亮，但在医疗（不能随便试药）或航空（不能碰撞）中，纯探索式 RL 不可接受——需要 offline RL / 保守策略，这是课程的弱项。
5. **「模型已知」假设**：MDP 章节假设 $T$、$R$ 已知，但真实世界模型本身最难估计。课程后半的 model uncertainty 章节补救，但深度有限。

---

## 🚀 扩展阅读

完成后推荐：
1. **CS234** Reinforcement Learning（Python 生态，深度 RL 专题）
2. **CS237A** Principles of Robot Autonomy I（把决策接到运动规划上）
3. **CS227A** Robot Perception（部分可观测的感知端）
4. 教材配套：`POMDPs.jl` 文档 + `SARSOP.jl`
5. 经典书：Thrun, Burgard, Fox *Probabilistic Robotics*（状态估计侧）
6. 应用深读：Kochenderfer 的 **ACAS Xu**（[arXiv:1810.07647](https://arxiv.org/abs/1810.07647) 附近系列）——课程思想的最佳工业落地。

---

**对应代码**：`supplementary/grad_projects.py::cs238_demo`（POMDP + 贝叶斯滤波）
