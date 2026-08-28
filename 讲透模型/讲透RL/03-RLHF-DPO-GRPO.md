# 03 · RLHF / DPO / GRPO — LLM 对齐三件套

> **全景升级（2026-08-27）**：本章谱系已织入 SFT/RL 全景——2026 四大裁决（baseline 审判日/Quagmires/PEAR/SFT=RL 特例）+五级阶梯+决策树见 [102-SFT与RL全景2026-深读卡](../../前沿与媒体/102-SFT与RL全景2026-深读卡.md)；与 [#100 蒸馏](../../前沿与媒体/100-模型蒸馏全景2026-深读卡.md)/[#101 mid-training](../../前沿与媒体/101-MidTraining全景2026-深读卡.md) 构成训练全周期三部曲。

> 这是本系列最重要的一篇。ChatGPT 用 RLHF、Llama 用 DPO、DeepSeek-R1 用 GRPO——这三个算法是 **2022-2025 LLM 对齐的全部主线**。本章把它们的数学一次性讲透，重点是 **DPO 的优雅推导**（证明 RLHF 可以变成分类问题）和 **GRPO 的去 critic 创新**（DeepSeek-R1 的核心）。
>
> 配套：[`讲透微调`](../讲透微调/)（实战）+ [`讲透公开课/01-CS285`](../讲透公开课/01-前沿课实时清单.md) LLM RL 章节 + [`讲透公开课/03`](<../讲透公开课/03-AI Infra 源码导读清单.md>) 的 verl/AReaL（RL 后端）

---

## 一、RLHF（PPO）回顾 + 三个痛点

[00 篇](./00-为什么RL与MDP.md) 给了 RLHF 三阶段。这里聚焦第三阶段（PPO）的数学和它的问题。

### 1.1 RLHF 的优化目标

给定训练好的奖励模型 $r_\phi(x,y)$，用 PPO 优化策略 $\pi_\theta$，加 **KL 惩罚**防止偏离参考模型 $\pi_\text{ref}$（SFT 模型）太远：

$$
\max_\theta \; \mathbb{E}_{x \sim \mathcal{D}, \, y \sim \pi_\theta(\cdot|x)} \left[ r_\phi(x,y) - \beta \log \frac{\pi_\theta(y|x)}{\pi_\text{ref}(y|x)} \right]
$$

- $r_\phi(x,y)$：RM 给的奖励
- $\beta \log \frac{\pi_\theta}{\pi_\text{ref}}$：KL 惩罚，防止 $\pi_\theta$ 乱跑（避免 reward hacking）

### 1.2 PPO 在 LLM 上的三个痛点

| 痛点 | 说明 |
|------|------|
| **① 显存爆炸** | 同时要 **4 个模型**：actor $\pi_\theta$ + critic $V_\psi$ + reference $\pi_\text{ref}$（冻结）+ RM $r_\phi$（冻结）|
| **② critic 难训** | critic 是另一个大模型，训练不稳，常发散 |
| **③ 工程复杂** | rollout（采样）和训练分离，要复杂调度（见 03 的 verl/AReaL）|

DPO 解决 ①②（去 RM + 去 critic），GRPO 进一步解决 ②（去 critic）。

---

## 二、DPO：把 RLHF 变成分类（2023-05，NeurIPS 2023）

### 2.1 DPO 的核心洞察

DPO（Direct Preference Optimization）的关键发现：**RLHF 的 KL 约束目标有闭式最优解，能反推出"隐式奖励"——所以可以直接用偏好对训策略，不需要显式 RM。**

### 2.2 DPO 推导（全篇最优雅的数学）

**第 1 步**：RLHF 目标的闭式解

[2.1 的目标] 等价于：

$$
\max_\pi \; \mathbb{E}_{y \sim \pi}[r(x,y)] - \beta \cdot \text{KL}(\pi \| \pi_\text{ref})
$$

这是个**变分问题**，有闭式最优解（用 Lagrange 乘子）：

$$
\boxed{\pi^*(y|x) = \frac{1}{Z(x)} \pi_\text{ref}(y|x) \exp\left(\frac{r(x,y)}{\beta}\right)}
$$

其中 $Z(x) = \sum_y \pi_\text{ref}(y|x) \exp(r(x,y)/\beta)$ 是配分函数（保证 $\pi^*$ 是概率）。

**第 2 步**：反解奖励

从闭式解反解 $r$（两边取 log）：

$$
r(x,y) = \beta \log \frac{\pi^*(y|x)}{\pi_\text{ref}(y|x)} + \beta \log Z(x)
$$

**关键**：奖励 $r$ 可以用 $\pi^*$ 和 $\pi_\text{ref}$ 的**对数比**表示——**不需要显式 RM**。

**第 3 步**：代入偏好模型

人类偏好用 **Bradley-Terry 模型**（A 比 B 好的概率）：

$$
P(y_w \succ y_l | x) = \sigma(r(x, y_w) - r(x, y_l))
$$

（$y_w$ = 偏好回答，$y_l$ = 不偏好回答，$\sigma$ = sigmoid）

把第 2 步的 $r$ 代入（注意 $\beta \log Z(x)$ 项相消）：

$$
P(y_w \succ y_l | x) = \sigma\left(\beta \log \frac{\pi^*(y_w|x)}{\pi_\text{ref}(y_w|x)} - \beta \log \frac{\pi^*(y_l|x)}{\pi_\text{ref}(y_l|x)}\right)
$$

**第 4 步**：最大似然 → DPO 损失

用 $\pi_\theta$ 替 $\pi^*$，做最大似然（负对数似然）：

$$
\boxed{L_\text{DPO}(\theta) = -\mathbb{E}_{(x, y_w, y_l)} \left[ \log \sigma\left(\beta \log \frac{\pi_\theta(y_w|x)}{\pi_\text{ref}(y_w|x)} - \beta \log \frac{\pi_\theta(y_l|x)}{\pi_\text{ref}(y_l|x)} \right) \right]}
$$

**这就是 DPO 损失**——一个普通的二分类交叉熵！只需要偏好对 $(y_w, y_l)$，**不需要 RM、不需要 critic、不需要 RL 采样**。

### 2.3 DPO vs RLHF

| 维度 | RLHF（PPO）| DPO |
|------|-----------|-----|
| 需要 RM | 是 | **否**（隐式）|
| 需要 critic | 是 | **否** |
| 损失 | RL 目标 | **分类（交叉熵）** |
| 模型数 | 4 | **2**（$\pi_\theta$ + $\pi_\text{ref}$）|
| 工程复杂 | 高 | **低**（像 SFT）|
| 探索 | on-policy 采样 | **无**（用现有偏好对）|

> 🎯 **DPO 的优雅**：通过闭式解反推，把"带 KL 约束的策略优化"转化为"对偏好数据的分类"——**数学等价，工程简单 10 倍**。这是 2023-2025 对齐领域最重要的理论贡献。

### 2.4 DPO 的代价

DPO 不是没缺点：
- **无探索**：只用现有偏好对，不能发现"RM 没覆盖的好回答"
- **离线**：偏好数据是预先采的，不能在线改进
- **分布漂移**：$\pi_\theta$ 偏离 $\pi_\text{ref}$ 太远时，DPO 的等价性失效

所以 **DPO 在"偏好数据充分 + 偏离不大"时好，但需要强探索的场景（reasoning）仍要 PPO/GRPO**——这就是 DeepSeek-R1 用 GRPO 不用 DPO 的原因。

---

## 三、GRPO：去掉 critic（DeepSeek 2024-2025）

### 3.1 PPO 要 critic 的根

[02 篇](./02-策略梯度与PPO.md) 策略梯度要优势 $A(s,a) = Q(s,a) - V(s)$，PPO 用 critic $V_\psi$ 估 $V$。但 LLM 上 critic 是另一个大模型——**显存翻倍 + 训练不稳**。

### 3.2 GRPO 的创新：组内相对优势

GRPO（Group Relative Policy Optimization，DeepSeek）的核心：**对每个 prompt 采样一组回答，用组内奖励的标准化当优势，不需要 critic。**

**算法**：
```
for prompt x:
    采样 G 个回答 {y_1, ..., y_G} ~ π_θ(·|x)
    算每个奖励 r_i = r_φ(x, y_i)
    
    # 组内标准化当优势（关键创新！）
    A_i = (r_i - mean(r_1...r_G)) / std(r_1...r_G)
    
    # 用 PPO clip 目标，但优势用 A_i
    L = mean_i [ min(ratio_i · A_i, clip(ratio_i, 1-ε, 1+ε) · A_i) ]
    θ ← θ + α · ∇L
```

（$r_i$ 在 reasoning 任务里可以是"答对=1/答错=0"，或更细的规则奖励）

### 3.3 为什么 GRPO 有效

- **不需要 critic**：优势用组内统计估，省一半显存
- **天然 baseline**：减去组内均值 = 自动 baseline（[02 篇](./02-策略梯度与PPO.md) 2.1）
- **适合规则奖励**：reasoning 任务奖励明确（答对/答错），不需要训 RM

### 3.4 GRPO 的代价

- **采样贵**：每个 prompt 要采 $G$ 个回答（$G$=4~64），推理成本高
- **要规则奖励**：需要明确奖励函数（数学题有答案、代码有测试），开放任务难定义
- **方差**：组小时方差大

---

## 四、R1-Zero：纯 RL 训出 reasoning（DeepSeek 2025-01）

### 4.1 震撼

DeepSeek-R1 论文（2025-01-20）最颠覆的实验：**不做 SFT，直接从 base model 用 GRPO 训**——模型自己涌现出 reasoning（"wait, let me think..."的反思链），在 AIME 2024 达到顶级水平。

```
base model（DeepSeek-V3）
    ↓ 纯 GRPO（规则奖励：答对=1）
DeepSeek-R1-Zero（涌现 reasoning）
```

### 4.2 为什么震撼

- 之前共识：要 SFT + RLHF。R1-Zero 证明**纯 RL 也能训出能力**
- reasoning 是**涌现**的，不是教出来的——模型自己学会"先思考再答"
- 类比 AlphaGo：纯 self-play 也能超越人类

### 4.3 实际 R1（正式版）仍要 SFT + distillation

R1-Zero 虽然强，但有可读性问题（reasoning 乱、语言混乱）。正式 R1 加了：
- 少量 SFT（cold start）
- GRPO（多阶段，奖励加可读性）
- **distillation** 到小模型（把 R1 的能力蒸馏到 Qwen/Llama）

> 🎯 **方法论意义**：R1-Zero 证明 RL 的潜力被低估了——只要有明确的奖励信号 + 足够算力，**RL 能让模型自己学会推理**。这开启了大模型训练的"RL-first"新范式。

---

## 五、三件套对比 + 选型

| 维度 | RLHF（PPO）| DPO | GRPO |
|------|-----------|-----|------|
| **RM** | 要 | 不要 | 要（或规则奖励）|
| **critic** | 要 | 不要 | **不要** |
| **采样** | on-policy | 不采（离线）| on-policy（每 prompt 采 G 个）|
| **模型数** | 4 | 2 | 2-3 |
| **工程复杂** | 高 | 低 | 中 |
| **探索** | 有 | 无 | 有 |
| **适合** | 通用对齐 | 偏好数据充分 | **reasoning + 明确奖励** |
| **代表** | ChatGPT、GPT-4 | Llama-3、Zephyr | **DeepSeek-R1、Qwen reasoning** |

**选型建议**：
- **通用对话助手**（偏好数据多）：DPO（简单）或 PPO（最强）
- **reasoning 模型**（有规则奖励）：**GRPO**（DeepSeek 路线，2025 主流）
- **小团队 / 快速迭代**：DPO（工程最简单）
- **学术研究 / 想刷榜**：GRPO + 大量采样

### 5.1 产业实证锚点（GRPO 超参链，来自 DeepSeek 深读）

GRPO 不是纸面算法——它在 DeepSeek 生产线上经历了**三次超参演化**（2026-08-15 行号级深读实证，详见 [`讲透DeepSeek/02-数学-稀疏性与解析模型的统一语言.md`](../讲透DeepSeek/02-数学-稀疏性与解析模型的统一语言.md)）：

| 代际 | 组大小 G / 温度 β | 关键变化 |
|---|---|---|
| V1 | 64 / 0.04 | 基线组内归一化（无 critic，组统计替代价值基线）|
| V2 | 32 / 0.02 | 缩组降温——更稳但探索弱 |
| V3 | 32 + 一致性奖励 | 奖励函数本身演化（格式+正确+自评加权）|
| Math-V2 | — | **显式自评进奖励** R = R_format(0.76·R_proof + 0.24·R_self)——verifier 飞轮雏形 |

配合 R1 四阶段（cold start → reasoning RL → rejection sampling SFT → 全场景 RL），这是 §四 R1-Zero 叙事的工业版闭环。开放问题接 [`05-RLVR的极限`](05-RLVR的极限.md)：Math-V2 的自动标注替代人工，是否是 RLVR 下一站？

---

## 六、开放问题

1. **奖励设计**：reasoning 有规则奖励，但开放对话怎么定奖励？
2. **reward hacking**：模型钻奖励空子（答错但伪装对）——GRPO 尤其要防
3. **R1-Zero 的可复现性**：其他团队复现 R1-Zero 仍困难（超参/数据敏感）
4. **RL vs 蒸馏**：R1 用蒸馏传播能力，纯 RL 是否值得？
5. **长 horizon RL**：当前 LLM RL 都是 1 步（生成 + 评分），多步 Agent RL 还没解决

---

## 七、一句话总结

> 🎯 **三句话**：
> 1. **RLHF（PPO）** = RM + critic，工程重但探索强（ChatGPT）。
> 2. **DPO** 用闭式解反推，把 RLHF 变成分类——数学优雅，工程简单，但无探索（Llama-3）。
> 3. **GRPO** 去掉 critic（组内标准化当优势），配规则奖励训出 reasoning——DeepSeek-R1 的核心，2025 最重要 RL 创新。

📌 **下一步**：回到 [README](./README.md) 看全系列，或进 [04 Actor-Critic/SAC](.)（待写，机器人方向）。
