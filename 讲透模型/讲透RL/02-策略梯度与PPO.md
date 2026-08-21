# 02 · 策略梯度 / PPO — LLM 对齐的方法论根基

> 本章讲 RL 第二大流派：**策略方法**。直接学策略 $\pi_\theta(a|s)$，用梯度上升最大化期望回报。这条路线演化出 **PPO**——ChatGPT 的 RLHF、所有现代 LLM 后训练的核心算法。
>
> 本章把"REINFORCE → baseline → Actor-Critic → TRPO → PPO clip"的演化讲清楚，每一步都是解决上一步的问题。

---

## 一、策略梯度定理（REINFORCE）

### 1.1 目标函数

策略 $\pi_\theta(a|s)$ 是参数化的概率分布（比如神经网络的 softmax 输出）。目标是最大化期望回报：

$$
J(\theta) = \mathbb{E}_{\tau \sim \pi_\theta} \left[ \sum_{t=0}^{T} \gamma^t R_t \right]
$$

（$\tau$ 是一条轨迹 $s_0, a_0, r_1, s_1, a_1, ...$）

### 1.2 策略梯度定理（核心）

对 $J(\theta)$ 求梯度，用**对数微分技巧**（log-derivative trick）：

$$
\boxed{\nabla_\theta J(\theta) = \mathbb{E}_{\tau \sim \pi_\theta} \left[ \sum_{t=0}^{T} \nabla_\theta \log \pi_\theta(a_t | s_t) \cdot G_t \right]}
$$

其中 $G_t = \sum_{k=t}^{T} \gamma^{k-t} R_k$ 是从 $t$ 开始的回报。

**直觉**：
- $\nabla_\theta \log \pi_\theta(a_t|s_t)$：增加"在 $s_t$ 选 $a_t$ 的对数概率"的梯度方向
- $G_t$：权重——**回报高的动作，增大它的概率；回报低的，减小**

### 1.3 REINFORCE 算法

```
for episode:
    跑完一整局，得到轨迹 (s_0, a_0, r_1, ..., s_T)
    for t = 0, ..., T:
        G_t = 从 t 到 T 的累计回报
        θ ← θ + α · ∇_θ log π_θ(a_t|s_t) · G_t
```

**问题**：方差极大。$G_t$ 是多条随机奖励的累计，波动巨大——训练几乎不收敛。

---

## 二、降低方差：baseline + 优势函数

### 2.1 减一个 baseline

数学事实：对任何只依赖 $s$ 的函数 $b(s)$，

$$
\mathbb{E}\left[ \nabla_\theta \log \pi_\theta(a_t|s_t) \cdot b(s_t) \right] = 0
$$

（因为 $\sum_a \pi_\theta(a|s) \nabla_\theta \log \pi_\theta(a|s) = \nabla_\theta \sum_a \pi_\theta(a|s) = \nabla_\theta 1 = 0$）

所以减 baseline 不改变梯度期望，但能**降低方差**。最优 baseline 是 $V^\pi(s_t)$（状态值）。

### 2.2 优势函数

减 baseline 后，权重变成**优势函数**：

$$
A^\pi(s_t, a_t) = Q^\pi(s_t, a_t) - V^\pi(s_t)
$$

**直觉**：$A > 0$ 表示这个动作比平均好；$A < 0$ 表示比平均差。用 $A$ 代替 $G$ 作权重，方差大幅降低。

策略梯度变成：

$$
\nabla_\theta J(\theta) = \mathbb{E}\left[ \nabla_\theta \log \pi_\theta(a_t|s_t) \cdot A^\pi(s_t, a_t) \right]
$$

### 2.3 Actor-Critic

要算 $A$ 需要 $V^\pi$。所以训练**两个网络**：
- **Actor**（策略 $\pi_\theta$）：用策略梯度更新
- **Critic**（值函数 $V_\phi$）：用 TD 学习更新，估 $V^\pi$

```
for step:
    a ~ π_θ(·|s)
    执行 a，得到 r, s'
    δ = r + γ V_φ(s') - V_φ(s)          # TD error，作为 A 的估计
    φ ← φ + α · δ · ∇_φ V_φ(s)          # 更新 critic
    θ ← θ + α · δ · ∇_θ log π_θ(a|s)    # 更新 actor
```

这就是 **Advantage Actor-Critic（A2C）**。

---

## 三、on-policy 的限制 → importance sampling → TRPO

### 3.1 on-policy 的痛点

REINFORCE / A2C 都是 **on-policy**：梯度期望必须在**当前策略**下采样。问题是：
- 策略一更新，旧样本就**不能再用**（数据分布变了）
- 每次更新要重新跑环境采样——**样本效率低**

LLM 场景特别贵：每条轨迹是 LLM 生成的一段文本，采样成本极高。

### 3.2 Importance Sampling（重要性采样）

数学技巧：可以用**旧策略**采的样本估**新策略**的期望，只要乘一个重要性比：

$$
\mathbb{E}_{a \sim \pi_\text{old}}\left[ \frac{\pi_\text{new}(a|s)}{\pi_\text{old}(a|s)} \cdot f(a) \right] = \mathbb{E}_{a \sim \pi_\text{new}}[f(a)]
$$

定义重要性比 $r_t(\theta) = \frac{\pi_\theta(a_t|s_t)}{\pi_{\theta_\text{old}}(a_t|s_t)}$，目标变成：

$$
J(\theta) = \mathbb{E}\left[ r_t(\theta) \cdot A_t \right]
$$

**问题**：如果 $\theta$ 偏离 $\theta_\text{old}$ 太远，$r_t$ 估计的方差爆炸——更新不稳。

### 3.3 TRPO（Trust Region Policy Optimization）

TRPO 的解法：加约束，**新旧策略的 KL 散度不超过 $\delta$**：

$$
\max_\theta \mathbb{E}[r_t(\theta) A_t] \quad \text{s.t.} \quad \mathbb{E}[\text{KL}(\pi_{\theta_\text{old}} \| \pi_\theta)] \le \delta
$$

用约束优化（二阶方法）求解——**很稳定，但实现复杂、计算贵**。

---

## 四、PPO：简单又好用的当前主流

### 4.1 PPO 的核心创新（OpenAI 2017）

PPO（Proximal Policy Optimization）把 TRPO 的**硬约束改成软约束**——clip（截断）重要性比：

$$
\boxed{L^\text{CLIP}(\theta) = \mathbb{E}_t\left[ \min\left( r_t(\theta) A_t, \; \text{clip}(r_t(\theta), 1-\epsilon, 1+\epsilon) A_t \right) \right]}
$$

**直觉**：
- $r_t > 1$ 表示新策略比旧更可能选这个动作
- 如果 $A_t > 0$（好动作），想增大 $r_t$，但 clip 在 $1+\epsilon$ 封顶——**别让策略走太远**
- 如果 $A_t < 0$（差动作），想减小 $r_t$，clip 在 $1-\epsilon$ 封底
- 取 min 保证是**悲观估计**（保守更新）

$\epsilon$ 通常 = 0.1 或 0.2。

### 4.2 PPO 完整算法

```
for iteration:
    # 1. 用当前策略 π_θ_old 采样一批轨迹
    rollout → 得到 (s, a, r, s') × N
    
    # 2. 用 critic 估优势 A_t（用 GAE）
    算每个 A_t
    
    # 3. 多个 epoch 重用这批数据（on-policy + importance sampling）
    for epoch = 1..K:    # 通常 K=4-10
        for mini-batch:
            r_t = π_θ(a|s) / π_θ_old(a|s)
            L = min(r_t·A_t, clip(r_t, 1-ε, 1+ε)·A_t)
            L -= β·KL(π_θ_old || π_θ)     # 可选：KL 惩罚
            θ ← θ + α·∇L
    
    # 4. 更新 θ_old = θ
```

### 4.3 为什么 PPO 是主流

- **简单**：clip 比 TRPO 的约束优化好实现 10 倍
- **稳定**：clip 防止策略崩溃
- **样本够用**：虽然 on-policy，但 mini-batch 多 epoch 重用，效率可接受
- **可扩展**：百亿参数 LLM 也能跑（配 LoRA + 人类反馈）

> 🎯 **PPO = ChatGPT 的 RLHF 算法**（2022 InstructGPT 论文用的就是 PPO）。直到 2024 DPO/GRPO 出现前，PPO 是 LLM 对齐的唯一选择。

---

## 五、PPO 的 LLM 时代挑战

PPO 在 LLM 上有几个问题，催生了 DPO/GRPO（[03 篇](./03-RLHF-DPO-GRPO.md)）：

1. **要 4 个模型同时在显存**：actor + critic + reference（冻结的 SFT 模型，算 KL）+ reward model——显存爆炸
2. **critic 难训**：critic 是另一个大模型，训练不稳
3. **超参敏感**：KL 系数、clip ε、学习率都要调
4. **工程复杂**：要分布式 rollout + 训练分离（见 [`讲透公开课/03`](<../讲透公开课/03-AI Infra 源码导读清单.md>) 的 verl/AReaL）

DPO（去 RM）/ GRPO（去 critic）就是来解决这些的。

---

## 六、一句话总结

> 🎯 **三句话**：
> 1. 策略梯度定理：$\nabla J = \mathbb{E}[\nabla \log \pi \cdot A]$，用优势 $A$ 作权重增减动作概率。
> 2. 演化：REINFORCE（方差大）→ Actor-Critic（加 baseline）→ TRPO（KL 约束）→ **PPO（clip）**。
> 3. PPO 是 ChatGPT RLHF 的算法，但在 LLM 上显存重 + critic 难训——催生 DPO/GRPO（[03 篇](./03-RLHF-DPO-GRPO.md)）。

📌 **下一步**：[03 RLHF/DPO/GRPO](./03-RLHF-DPO-GRPO.md)——LLM 对齐的当前前沿，DeepSeek-R1 的 GRPO 是 2025 最重要的 RL 创新。
