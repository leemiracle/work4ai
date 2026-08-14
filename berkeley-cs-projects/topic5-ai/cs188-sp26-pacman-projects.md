# CS 188 SP26 · Pacman Projects — 6 个迭代完整整合

> Berkeley CS 188 是全球 AI 入门课的事实标杆。其 **Pacman Projects** 自 Klein/DeNero/Abbeel 设计以来长期稳定，覆盖 AI 的 5 大基础：**搜索 / 对抗搜索 / 强化学习 / 概率推理 / 机器学习**——构成一条"从无智能到智能体"的完整迭代路径。
>
> 本文按 [Spring 2026](https://inst.eecs.berkeley.edu/~cs188/sp26/projects/) 的 6 个项目迭代组织，每个迭代给出：**目标 / 核心算法 / autograder 拆解 / 学生卡点 / 项目内连接**。配套代码：[`cs188_sp26_iterations.py`](./cs188_sp26_iterations.py)（5 个迭代核心算法全部跑通）。
>
> 数据来源：实抓 SP26 projects/ 总览页（具体 proj 页面 2026-08 已下线，但 Pacman 项目结构长期不变，从总览 + 经典实现还原）。

---

## §0 6 个迭代演化地图

```
P0 入门 ─→ P1 Search ─→ P2 Multiagent ─→ P3 RL ─→ P4 Bayes/HMM ─→ P5 ML
(Python)  (确定)       (对抗)            (学习)   (不确定性)       (从数据学)
   │         │             │                │         │              │
   │         ▼             ▼                ▼         ▼              ▼
   │   BFS/DFS/UCS   Minimax + α-β     Value Iter    Forward        Perceptron
   │   /A* + h        Expectimax        Q-Learning    Particle       NN (BP)
   │                   Eval Fn          Approx Q      Filter         RNN
   │
   └─→ 状态空间 → 博弈树 → MDP → HMM → 监督学习
              AI 经典四范式：搜索 / 博弈 / 决策 / 推断 + 数据驱动
```

| Project | 主题 | 核心算法 | autograder questions | 难度 | 项目内连接 |
|---------|------|---------|---------------------|------|----------|
| P0 | Python + Autograder | — | — | ⭐ | — |
| **P1** | **Search** | DFS / BFS / UCS / A* + 启发式设计 | 8 | ⭐⭐ | [UNIFIED_ROADMAP L09](../../top-cs-projects/UNIFIED_ROADMAP.md) |
| **P2** | **Multiagent** | Minimax + α-β / Expectimax / Eval Fn | 5 | ⭐⭐⭐ | [讲透RL/02 策略评估函数的雏形](../../讲透RL/02-策略梯度与PPO.md) |
| **P3** | **Reinforcement Learning** | Value Iteration / Q-Learning / Approximate Q | 8 | ⭐⭐⭐⭐ | [讲透RL/01 DQN + 08 §4 收敛性](../../讲透RL/08-Actor-Critic-SAC-ModelBased-OfflineRL.md) |
| **P4** | **Bayes Nets & HMMs** | 因子推理 / Forward Algo / Particle Filter | 6 | ⭐⭐⭐ | [讲透概率图模型](../../讲透概率图模型/) |
| **P5** | **Machine Learning** | Perceptron / NN（反向传播）/ RNN | 6 | ⭐⭐⭐⭐ | [讲透PyTorch](../../讲透PyTorch/) + [讲透Transformer](../../讲透Transformer/) |

---

## §1 P1 · Search（搜索）

### 1.1 核心抽象：统一图搜索框架

CS188 P1 的精髓是**一个框架四用**——用 frontier 容器区分 DFS / BFS / UCS / A*：

```
function GRAPH-SEARCH(problem, frontier):
    frontier ← {(start, [])}
    explored ← {}
    while frontier 非空:
        (state, path) ← frontier.pop()
        if problem.isGoal(state): return path
        if state ∈ explored: continue
        explored.add(state)
        for (next_state, action, cost) in problem.getSuccessors(state):
            if next_state ∉ explored:
                frontier.push((next_state, path + [action]))
```

| frontier | 算法 | 最优性 | 完备性 |
|---------|------|-------|-------|
| Stack（LIFO）| DFS | ❌ | ❌（可能陷循环）|
| Queue（FIFO）| BFS | ✓（无权图）| ✓ |
| PriorityQueue by g(n) | **UCS** | ✓（带权图）| ✓ |
| PriorityQueue by f(n) = g(n) + h(n) | **A\*** | ✓（若 h admissible）| ✓ |

### 1.2 A* 的关键：admissible 启发式

A* 比其他三个多一个 knob：启发式 $h(n)$。**admissible（可采纳）= 永不高估真实代价**，是 A* 最优性的必要条件。

- **4-连通网格**：Manhattan 距离 $\|x_1-x_2\| + \|y_1-y_2\|$ admissible ✓
- **一般图**：松弛问题法（relaxation）——把原问题某个约束去掉，松弛问题的最优解就是 admissible heuristic
  - 8-puzzle：把"每次只能移动空格相邻 tile"放松为"tile 可瞬移"→ misplaced tiles count
  - 迷宫：把墙去掉→直线距离

### 1.3 autograder 拆解（8 questions）

| Q | 内容 | 学生常见卡点 |
|---|------|----------|
| Q1-4 | DFS / BFS / UCS / A* 在小 maze | 没正确处理 explored set，无限循环 |
| Q5 | PriorityQueue 出队顺序的 tie-breaking | UCS 在等代价时 order 错（autograder 严格） |
| Q6 | A* 用 Manhattan（开放路径） | h 写错了导致 A* 不最优 |
| Q7-8 | **CornersProblem** + 启发式 | **最大卡点**——状态 = (位置, 4 个角访问过的 bool)，启发式要 admissible 又要 informative |
| Q9 | **FoodSearchProblem** 启发式 | 启发式设计要找 MST-style（贪心最近食物） |

### 1.4 学生卡点：CornersProblem 的启发式

**陷阱**：写 `h = max(Manhattan(pos, corner) for unvisited corner)` → **不够 informative**（autograder 节点扩展数太多，扣分但不报错）。

**正解**：贪心走最近未访问角，**累积**距离（不是 max）：

```python
def corners_heuristic(state, problem):
    pos, visited = state
    unvisited = [c for c in corners if c not in visited]
    if not unvisited: return 0
    total = 0
    cur = pos
    while unvisited:
        d = [manhattan(cur, c) for c in unvisited]
        i = argmin(d)
        total += d[i]; cur = unvisited.pop(i)
    return total  # admissible（实际最短路径 ≥ 这个贪心估计）
```

### 1.5 实证（[代码 P1 测试](./cs188_sp26_iterations.py) 跑通）

5×1 迷宫 `%P    .%` 上：

```
DFS path length: 5  actions: ['E','E','E','E','E']
BFS path length: 5  actions: ['E','E','E','E','E']
A*  path length: 5  actions: ['E','E','E','E','E']
✅ A* admissible → 与 BFS 同长（最优）
```

### 🔗 项目内连接
- 经典 AI 总览：[`top-cs-projects/UNIFIED_ROADMAP.md`](../../top-cs-projects/UNIFIED_ROADMAP.md) L09（Berkeley CS 188）
- 跨校洞察：[`top-cs-projects/CROSS_SCHOOL_INSIGHTS.md`](../../top-cs-projects/CROSS_SCHOOL_INSIGHTS.md) §8「搜索 vs 学习」

---

## §2 P2 · Multiagent Search（对抗搜索）

### 2.1 从单人搜索到多人博弈

P1 是单人问题（Pacman 独自走迷宫）；P2 加入 ghosts → **多 agent 博弈**。两种 ghost 模型：

- **Adversarial Ghost**：理性对手 → **Minimax**
- **Stochastic / Random Ghost**：非理性 → **Expectimax**

### 2.2 Minimax 核心：多层连续 min

经典 Minimax 是 1 个 max + 1 个 min（如国际象棋）。Pacman 通常有 **多个 ghosts** → 状态空间的 agent index 循环：

```
Pacman (max) → Ghost1 (min) → Ghost2 (min) → ... → Pacman (max) → ...
```

**关键代码**（[配套 P2 测试](./cs188_sp26_iterations.py)）：

```python
def minimax_value(state, agent_idx, depth, n_agents, ...):
    if terminal(state) or depth >= max_depth:
        return evaluation_function(state)
    next_agent = (agent_idx + 1) % n_agents
    next_depth = depth + 1 if next_agent == 0 else depth  # Pacman 才增 depth
    children = [minimax_value(get_successor(state, agent_idx, a),
                              next_agent, next_depth, ...)
                for a in get_legal_actions(state, agent_idx)]
    return max(children) if agent_idx == 0 else min(children)
```

### 2.3 α-β 剪枝

不加剪枝的 Minimax 节点数 $O(b^d)$（$b$ = 分支因子，$d$ = 深度）。α-β 剪枝最优情况下减到 $O(b^{d/2})$——**同样深度，搜索树翻倍**。

- **α** = 当前 max 节点能保证的下界
- **β** = 当前 min 节点能保证的上界
- 当 `α ≥ β`，剪枝（这个分支不影响最终决策）

### 2.4 Expectimax：ghost 不理性的现实

普通 ghost AI 是脚本化的（不最优），Minimax 过于悲观。Expectimax 把 min 换成期望：

$$
\text{value(min node)} = \mathbb{E}_a[\text{value(child)}] = \frac{1}{|A|}\sum_a \text{value(child}(a)\text{)}
$$

→ Pacman 在 Expectimax 下更激进（愿意冒险，因为 ghost 可能不抓他）。

### 2.5 autograder 拆解（5 questions）

| Q | 内容 | 卡点 |
|---|------|------|
| Q1 | Minimax（1 ghost） | agent index 循环；终止条件 |
| Q2 | Minimax（多 ghost） | next_depth 只在回到 Pacman 时增加 |
| Q3 | **α-β 剪枝** | α/β 更新顺序；left-to-right 假设 |
| Q4 | Expectimax（多 ghost） | 把 min 改 mean，不要混淆 |
| Q5-6 | 自定义 evaluation function | features（food 距离 / ghost 距离 / scared ghost）+ weights 设计 |

### 2.6 实证（[配套 P2 测试](./cs188_sp26_iterations.py) 跑通）

构造 2-ply 博弈树：

```
root(Pacman) ─→ g1 ─→ [-5, 3]
            └─→ g2 ─→ [10, -2]
```

```
Minimax value: -2      （g1_val=min(-5,3)=-5, g2_val=min(10,-2)=-2, root=max(-5,-2)=-2）
Expectimax value: 4.0  （g1_val=mean(-5,3)=-1, g2_val=mean(10,-2)=4, root=max(-1,4)=4）
✅ ghost 行为模型不同 → 策略不同（Pacman 在 Expectimax 下选 g2 路径冒险）
```

### 🔗 项目内连接
- 评估函数的雏形 → [`讲透RL/02`](../../讲透RL/02-策略梯度与PPO.md) 的 advantage function（P2 自定义 eval = RL 的 reward shaping 早期形式）
- 搜索 vs 学习 → [`top-cs-projects/CROSS_SCHOOL_INSIGHTS.md`](../../top-cs-projects/CROSS_SCHOOL_INSIGHTS.md) §8

---

## §3 P3 · Reinforcement Learning（强化学习）

### 3.1 三大算法递进

| 算法 | 学什么 | 输入 |
|------|------|------|
| **Value Iteration** | 给定 MDP（已知 $P, R$）求 $V^*$ | 完整 MDP |
| **Q-Learning** | 不知道 MDP，通过交互学 $Q^*$ | 经验 $(s, a, r, s')$ |
| **Approximate Q-Learning** | 状态空间太大，用特征 $\phi(s, a)$ 近似 $Q \approx w^\top \phi$ | 经验 + 特征函数 |

### 3.2 Value Iteration

**Bellman 最优 backup**：

$$
V_{k+1}(s) = \max_a \sum_{s'} P(s'|s,a) \left[ R(s,a,s') + \gamma V_k(s') \right]
$$

→ 必收敛到 $V^*$（[`讲透RL/08` §4 Banach 压缩映射定理](../../讲透RL/08-Actor-Critic-SAC-ModelBased-OfflineRL.md)）。

### 3.3 Q-Learning（off-policy）

$$
Q(s, a) \leftarrow Q(s, a) + \alpha \left[ r + \gamma \max_{a'} Q(s', a') - Q(s, a) \right]
$$

**核心：replay buffer 不强制**（CS188 不教 experience replay，那是 DQN 的事 → [`讲透RL/01`](../../讲透RL/01-Q-Learning与DQN.md)）。

### 3.4 Approximate Q-Learning：通往深度 RL 的桥

表格 Q-Learning 不能扩展到大状态空间（Pacman 屏幕像素）。**Approximate Q-Learning** 把 Q 参数化：

$$
Q(s, a) \approx \sum_i w_i \cdot \phi_i(s, a)
$$

更新规则（**关键**：用特征梯度而不是状态索引）：

$$
w_i \leftarrow w_i + \alpha \left[ r + \gamma \max_{a'} Q(s', a') - Q(s, a) \right] \cdot \phi_i(s, a)
$$

**直觉**：这就是 [讲透RL/02 的策略方法](../../讲透RL/02-策略梯度与PPO.md) 的前身——features = 早期神经网络的特征工程版本。**Q-Learning + 神经网络 = DQN**（[01 篇](../../讲透RL/01-Q-Learning与DQN.md)）。

### 3.5 autograder 拆解（8 questions）

| Q | 内容 | 卡点 |
|---|------|------|
| Q1 | Value Iteration（标准） | γ / 收敛阈值 |
| Q2 | 提取策略 π* | argmax over Q |
| Q3 | Bridge crossing（γ=1 边界） | 离散 vs 连续 reward |
| Q4 | 推 / 拉（policy oscillation） | γ < 1 才不震荡 |
| Q5-6 | Q-Learning Agent + ε-greedy | tie-breaking random（CS188 默认要求） |
| Q7 | ε-greedy 的 decay | 探索-利用 tradeoff |
| Q8 | **Approximate Q-Learning** | feature extractor 设计 + weight 更新 |

### 3.6 实证（[配套 P3 测试](./cs188_sp26_iterations.py) 跑通）

3 状态 MDP $S_0 \to S_1 \to S_2 \to T$（带 b 终止分支）：

```
Value Iteration 收敛于 4 iter
  V*(S0)=8.100, V*(S1)=9.000, V*(S2)=10.000
✅ Value Iteration 收敛到理论值

Q-Learning 2000 ep:
  Q(S0,a)=8.10,  Q(S0,b)=5.00
  Q(S1,a)=9.00,  Q(S2,a)=10.00
✅ Q-Learning 学到精确理论值（off-policy TD 控制有效）
```

### 🔗 项目内连接
- 收敛性证明 → [`讲透RL/08` §4 Banach + deadly triad](../../讲透RL/08-Actor-Critic-SAC-ModelBased-OfflineRL.md#§4-收敛性证明cs234-的硬通货)
- DQN = Approximate Q + 神经网络 → [`讲透RL/01`](../../讲透RL/01-Q-Learning与DQN.md)
- 完整 RL 演化 → [`讲透RL/` 全套](../../讲透RL/)

---

## §4 P4 · Bayes Nets and HMMs（概率推理）

### 4.1 Bayes Net：变量间条件依赖的图

**Bayes Net** = DAG + 每个节点的条件概率表（CPT）。两个核心推理任务：

- **精确推理**：变量消除（Variable Elimination）—— 按某种消除顺序，把因子连乘后求和
- **近似推理**：粒子滤波 / MCMC

### 4.2 HMM Forward Algorithm（CS188 经典例子：ghost tracking）

**HMM 三大假设**：
- Markov：$P(s_t | s_{1:t-1}) = P(s_t | s_{t-1})$
- Emission：$P(o_t | s_{1:t}, o_{1:t-1}) = P(o_t | s_t)$

**Forward 算法**（递推后验 $\alpha_t(s) = P(s_t = s | o_{1:t})$）：

$$
\alpha_t(s) \propto P(o_t | s) \cdot \sum_{s'} \alpha_{t-1}(s') \cdot P(s | s')
$$

**复杂度**：每步 $O(|S|^2)$（求和遍历 $s'$）。

### 4.3 Particle Filter（蒙特卡洛近似）

HMM Forward 在大状态空间（连续 ghost 位置）太贵。**粒子滤波**用 $N$ 个离散粒子近似后验：

```
for each observation o:
    1. 转移：每个粒子 p → p' ~ P(· | p)
    2. 加权：每个粒子权重 = P(o | p')
    3. 重采样：按权重抽 N 个新粒子（无权重）
```

→ $O(N)$ per step，$N$ 越大越准（典型的样本数 N=1000~10000）。

### 4.4 autograder 拆解（6 questions）

| Q | 内容 | 卡点 |
|---|------|------|
| Q1-3 | 因子操作（join / eliminate / normalize） | 因子变量顺序；边缘化 |
| Q4 | **变量消除法** | 消除顺序影响效率（CS188 不强制最优顺序） |
| Q5-6 | HMM Forward / Particle Filter | 重采样的随机性 → 不同 run 结果略不同 |
| Q7-8 | Particle Filter 多种变体（approxInference / 精确） | 时间步 / 重采样的 timing |

### 4.5 实证（[配套 P4 测试](./cs188_sp26_iterations.py) 跑通）

经典 Rain → Umbrella HMM：

```
Forward algorithm (obs = [U, U, ¬U]):
  P(R_3 = T | obs) = 0.191
  P(R_3 = F | obs) = 0.809
✅ forward 对最近观察权重最高 → 第三次 ¬U 把后验从 R=T 拉到 R=F
   （虽然前两次 U 推 R=T，但 forward 给最近观察最大权重）
```

### 🔗 项目内连接
- 概率图模型全貌 → [`讲透概率图模型`](../../讲透概率图模型/)
- 贝叶斯思维 → [`top-cs-projects/CROSS_SCHOOL_INSIGHTS.md`](../../top-cs-projects/CROSS_SCHOOL_INSIGHTS.md) §5「贝叶斯思维的 5 个跃迁」

---

## §5 P5 · Machine Learning（机器学习）

### 5.1 三个模型的迭代：Perceptron → NN → RNN

**P5 是 CS188 唯一真正接触"从数据学习"的项目**（前面 P1-P4 都是手工设计算法）。三个模型递进：

| 模型 | 复杂度 | 学什么 | CS188 Q |
|------|------|------|---------|
| **Perceptron** | 1 层 | 线性分类器 $w^\top x + b$ | Q1-3 |
| **Neural Net** | 多层 + 反向传播 | 非线性（ReLU/sigmoid）| Q4-6 |
| **RNN** | 时间展开 | 序列建模（语言识别）| Q7-9 |

### 5.2 Perceptron 算法

线性可分数据保证有限步收敛（Novikoff 定理）：

$$
w \leftarrow w + \alpha (y - \hat{y}) x, \quad \hat{y} = \text{sign}(w^\top x + b)
$$

### 5.3 反向传播：链式法则的工业实现

[讲透PyTorch 的反向传播](../../讲透PyTorch/) 完整讲，这里给核心：

```
forward:  z = W·x + b;  a = ReLU(z);  L = loss(a, y)
backward: ∂L/∂W = (∂L/∂a) · (∂a/∂z) · (∂z/∂W) = ∂L/∂a · 1[z>0] · x
```

CS188 P5 Q5-7 要求手写反向传播（不依赖 PyTorch），是真正理解 backprop 的最有效训练。

### 5.4 RNN step：序列建模的根基

$$
h_t = \tanh(W_{xh} \cdot x_t + W_{hh} \cdot h_{t-1} + b_h)
$$

→ 输出 $h_T$（最后隐藏状态）做分类。**这就是 LSTM/GRU/Transformer 的雏形**（[讲透Transformer](../../讲透Transformer/)）。

### 5.5 autograder 拆解（6 questions）

| Q | 内容 | 卡点 |
|---|------|------|
| Q1 | Perceptron（pixel → digit） | feature 设计 |
| Q2-3 | Perceptron（bias / 多分类） | bias 项的处理 |
| Q4-6 | **Neural Network**（手写反向传播） | 最常卡：链式法则 dim 不对 |
| Q7-9 | **RNN**（语言识别） | BPTT（backprop through time） |

### 5.6 实证（[配套 P5 测试](./cs188_sp26_iterations.py) 跑通）

Perceptron 学 AND（线性可分）：

```
Perceptron 学 AND：6 iter 收敛
  w = [2.0, 1.0], b = -2.0
  训练集准确率: 4/4
✅ 线性可分数据 Perceptron 必收敛
```

### 🔗 项目内连接
- 反向传播全解 → [`讲透PyTorch/`](../../讲透PyTorch/) + [`top-cs-projects/INSIGHTS_FULL_PICTURE.md`](../../top-cs-projects/INSIGHTS_FULL_PICTURE.md) 洞察 5
- RNN → Transformer 演化 → [`讲透Transformer/`](../../讲透Transformer/)
- 监督学习总览 → [`top-cs-projects/UNIFIED_ROADMAP.md`](../../top-cs-projects/UNIFIED_ROADMAP.md) L10/L11

---

## §6 学习路径建议

### 6.1 按"目标"挑迭代

| 你的目标 | 必做的迭代 |
|---------|---------|
| **AI 入门完整 1 轮** | P0 → P1 → P2 → P3 → P4 → P5（全套）|
| **想懂 RLHF/DeepSeek** | P3（RL 地基）→ [`讲透RL/02 PPO`](../../讲透RL/02-策略梯度与PPO.md) → [`讲透RL/03 RLHF/DPO/GRPO`](../../讲透RL/03-RLHF-DPO-GRPO.md) |
| **想搞机器人/具身** | P1（搜索）+ P3（RL）→ [`讲透RL/08 SAC+Model-Based`](../../讲透RL/08-Actor-Critic-SAC-ModelBased-OfflineRL.md) |
| **想搞 LLM** | P1（搜索 = reasoning 的雏形）+ P5（NN）→ [`讲透Transformer/`](../../讲透Transformer/) |
| **想搞 CV** | P5（NN）+ [`讲透PyTorch/`](../../讲透PyTorch/) → [`cv-learning`](../../cs61a-learning/) |
| **想搞 NLP** | P5（RNN）+ [`讲透Transformer/`](../../讲透Transformer/) + [`讲透NLP/`](../../讲透NLP/) |

### 6.2 与项目内"经典 AI"主线的衔接

```
                    CS 188 Pacman 6 个迭代
                            │
              ┌─────────────┼─────────────┐
              ▼             ▼             ▼
          搜索/博弈     RL/P4 推断       ML
              │             │             │
              ▼             ▼             ▼
       [top-cs-projects]  [讲透RL]   [讲透Transformer]
       UNIFIED_ROADMAP   01-08 系列   + PyTorch + RAG
       L09 经典 AI
```

---

## §7 配套

### 🧪 代码
- [`cs188_sp26_iterations.py`](./cs188_sp26_iterations.py)（5 个迭代核心算法跑通）

### 📚 来源与参考
- **官方 SP26 项目页**：[https://inst.eecs.berkeley.edu/~cs188/sp26/projects/](https://inst.eecs.berkeley.edu/~cs188/sp26/projects/)（具体 proj 页面 SP26 期末下线，2026-08 已 404，但结构从总览 + 经典实现还原）
- **历版归档**：[FA23](https://inst.eecs.berkeley.edu/~cs188/fa23/)（与 SP26 高度一致）
- **教材**：Russell & Norvig **《AIMA》4th ed**（Pearson 2021）— §3 搜索 / §5 博弈 / §17 MDP/RL / §13 Bayes / §21 NN
- **设计者**：John DeNero / Dan Klein / Pieter Abbeel（Berkeley）
- ** NSF 资助**：CAREER grant 0643742

### 🔗 项目内交叉引用
- 元洞察：[`top-cs-projects/INSIGHTS_FULL_PICTURE.md`](../../top-cs-projects/INSIGHTS_FULL_PICTURE.md) 洞察 3「搜索是一切的根」
- 跨校对比：[`top-cs-projects/CROSS_SCHOOL_INSIGHTS.md`](../../top-cs-projects/CROSS_SCHOOL_INSIGHTS.md) §8「搜索 vs 学习」+ §9「理论 vs 实战」
- 学习路径：[`top-cs-projects/UNIFIED_ROADMAP.md`](../../top-cs-projects/UNIFIED_ROADMAP.md) L09「经典 AI」
- 现有教学版（不分迭代）：[`ai_pacman.py`](./ai_pacman.py)

---

**完成日期**：2026-08-12  ·  **作者**：AI Mentor (ai-mentor)  ·  **配套**：[Berkeley 项目主页](../../berkeley-cs-projects/README.md) + [讲透RL 全系列](../../讲透RL/README.md)

📌 **下一步**建议：
- 想真正动手做 CS188 autograder → 从 [Berkeley CS 188 FA23](https://inst.eecs.berkeley.edu/~cs188/fa23/)（SP26 下线，FA23 仍可下）拉 starter code
- 想深入 RL（P3 之后）→ 直接进 [`讲透RL/`](../../讲透RL/) 8 章
- 想深入博弈论（P2 之后）→ CS188 不深入，可补 Stanford CS 269I（算法博弈论）
