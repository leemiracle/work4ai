# 01 · Q-Learning / DQN — 值函数方法

> 本章讲 RL 的第一大流派：**值函数方法**。核心是 Q-Learning——直接学最优动作值函数 $Q^*$，然后贪心选动作。DQN（DeepMind 2015，Nature）把它和深度学习结合，打响深度 RL 第一枪。
>
> 配套：[`讲透公开课/01-CS285`](../讲透公开课/01-前沿课实时清单.md) Lecture 6-8

---

## 一、Q-Learning：从 Bellman 最优方程推导

### 1.1 出发点：最优 Bellman 方程

[00 篇](./00-为什么RL与MDP.md) 给出了最优 Bellman 方程：

$$
Q^*(s,a) = \sum_{s'} P(s'|s,a) \left[ R(s,a,s') + \gamma \max_{a'} Q^*(s', a') \right]
$$

**直觉**：在 $(s,a)$ 的最优价值 = 即时奖励 + 下一状态的最优价值（取 max）。

### 1.2 Q-Learning 更新规则

我们不知道 $P$ 和 $R$，但能采样到转移 $(s, a, r, s')$。用它们做**时序差分（TD）学习**：

$$
\boxed{Q(s,a) \leftarrow Q(s,a) + \alpha \underbrace{\left[ r + \gamma \max_{a'} Q(s', a') - Q(s,a) \right]}_{\text{TD error } \delta}}
$$

- $\alpha$ 是学习率
- TD error $\delta = r + \gamma \max_{a'} Q(s',a') - Q(s,a)$——"实际看到的 + 预估的下一步"和"当前估计"的差
- **off-policy**：$Q$ 学的是最优策略 $\pi^*$，但采样的可以是任何策略（探索策略）

### 1.3 为什么 Q-Learning 收敛

Q-Learning 是在解 Bellman 最优方程——可以证明在表格情况（状态/动作有限）下，满足一定条件时 $Q \to Q^*$ 收敛。**但当 $Q$ 用神经网络表示时（DQN），会不稳定**——这是 DQN 要解决的核心问题。

---

## 二、DQN：深度 Q 网络（DeepMind 2015 Nature）

### 2.1 问题：用神经网络近似 Q 会崩

直接把 $Q(s,a)$ 换成 $Q_\theta(s,a)$，用 Q-Learning 更新 $\theta$——会发散。原因：
1. **相邻样本相关**：连续采样的 $(s,a,r,s')$ 高度相关，梯度方向同质化
2. **移动目标**：更新 $\theta$ 时，target $r + \gamma \max Q_\theta(s',a')$ 也在变——追一个移动的靶子

### 2.2 DQN 的两大稳定化创新

**创新 1：Experience Replay（经验回放）**

把每次转移 $(s,a,r,s')$ 存进一个 buffer，训练时**随机抽样**——打破样本相关性。

```
buffer = []
for each step:
    存 (s, a, r, s') 进 buffer
    从 buffer 随机抽 batch → 训练 Q_θ
```

**创新 2：Target Network（目标网络）**

维护两个网络：
- **online 网络** $Q_\theta$：每步更新
- **target 网络** $Q_{\theta^-}$：每 N 步把 $\theta$ 复制给 $\theta^-$，期间固定

target 用 $Q_{\theta^-}$ 算：$y = r + \gamma \max_{a'} Q_{\theta^-}(s', a')$——**靶子固定 N 步**，稳定。

### 2.3 DQN 完整算法

```
初始化 online Q_θ 和 target Q_{θ^-}（θ^- = θ）
初始化空 replay buffer B

for episode = 1, 2, ...:
    for t = 0, 1, ...:
        # 1. 选动作（ε-greedy 探索）
        with prob ε: a = 随机
        else: a = argmax_a Q_θ(s, a)
        
        # 2. 执行，观察 r, s'
        执行 a，得到 r, s'
        
        # 3. 存进 buffer
        B.append((s, a, r, s'))
        
        # 4. 从 buffer 随机抽 batch，训练
        batch = random_sample(B)
        for (s,a,r,s') in batch:
            y = r + γ·max_a' Q_{θ^-}(s', a')    # 用 target 网络
            L = (y - Q_θ(s, a))²                 # MSE
            ∇_θ L 更新 θ
        
        # 5. 每 N 步同步 target
        if t % N == 0: θ^- = θ
```

### 2.4 DQN 的成绩

DeepMind 2015 Nature 论文：**一个 DQN 架构打 49 款 Atari 游戏**，输入像素，输出离散动作，**多数游戏超人类水平**。这是深度 RL 的"ImageNet 时刻"——证明通用深度 RL 可行。

---

## 三、DQN 的后续改进（Rainbow）

DQN 之后，一系列改进：

| 改进 | 创新 |
|------|------|
| **Double DQN** | 解决 Q 值**过高估计**（用 online 网络选 a'，target 网络估值）|
| **Dueling DQN** | 把 $Q(s,a)$ 拆成 $V(s) + A(s,a)$（优势和状态值分开学）|
| **Prioritized Replay** | 按 TD error 大小优先回放重要的样本 |
| **Noisy Nets** | 用参数噪声代替 ε-greedy 探索 |
| **Distributional RL** | 学 return 的分布，不只是期望（C51/QR-DQN）|
| **Rainbow**（2017）| 上述全结合，SOTA |

---

## 四、Q-Learning 家族的局限

1. **离散动作**：$\max_a$ 要求动作有限——连续动作要 discretize，维度爆炸
2. **过估计**：$\max$ 操作会放大噪声
3. **样本效率低**：off-policy 名义上高，但实际 RL 仍要海量交互

> 🎯 **LLM 时代为什么不用 DQN**：LLM 的动作空间是词表（~10 万 token），$\max_a Q(s,a)$ 算不动。所以 LLM 对齐用**策略方法**（PPO/GRPO）——见 [02 篇](./02-策略梯度与PPO.md)。

---

## 五、一句话总结

> 🎯 **三句话**：
> 1. Q-Learning 用 TD 学习解 Bellman 最优方程，off-policy、学 $Q^*$。
> 2. DQN 把 Q 用神经网络表示，靠 **experience replay + target network** 两大稳定化在 Atari 打赢人类——深度 RL 的 ImageNet 时刻。
> 3. 局限：离散动作 + 过估计 + 样本效率低——所以 LLM 时代转向策略方法（PPO/GRPO）。

📌 **下一步**：[02 策略梯度/PPO](./02-策略梯度与PPO.md) 学 LLM 对齐用的策略方法。
