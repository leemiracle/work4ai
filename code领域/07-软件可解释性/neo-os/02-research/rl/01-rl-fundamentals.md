# A · 强化学习领域本身 —— 三层讲透 + 2024-2026 SOTA

> **探索维度 A**：RL 这个领域本身（基础 + 前沿）
> **学习风格**：直觉 → 数学 → 代码 → 不足 → 应用（继承 work4ai 三层宪法）
> **日期**：2026-08-05
> **SOTA 来源**：websearch 2025-2026（DeepSeek-R1/GRPO/RLVR/AlphaProof 时代）

---

## 一、TL;DR（5 条）

1. **RL 的本质是「从延迟奖励中学习序列决策」**——不是预测标签（监督学习），不是找结构（无监督），是在环境里**试错 + 最大化长期累积回报**。这让它天然适合「没有教师信号、但有成败反馈」的场景（游戏/控制/证明/推理）。

2. **数学骨架只有 4 件**：MDP（问题建模）→ Bellman 方程（最优性刻画）→ 策略梯度（可优化的目标）→ PPO/GRPO（稳定训练的工程化）。后面所有花哨算法（DQN/SAC/RLHF/RLVR）都是这 4 件的变体。

3. **2025 是 RL 的「二次复兴」**：DeepSeek-R1（2025-01）用 RLVR（Reinforcement Learning with Verifiable Rewards）训练出推理能力匹敌 o1 的开源模型，证明「RL + 可验证 reward」是激活 LLM 推理的关键。**GRPO**（Group Relative Policy Optimization）取代 PPO 成为 LLM reasoning 的标准 RL 算法。

4. **RLVR 的关键洞察**：RL 不是教模型新知识，而是**增加正确推理路径的概率**——base model 已隐含正确路径，RLVR 用可验证 reward 把它们「挤」出来。这解释了为什么 RLVR 在数学/代码（有客观答案）上有效，在开放生成上难。

5. **RL 的根本难点是「信用分配」**（credit assignment）：哪个动作导致了最终成败？延迟奖励让这个归因极难。这是 RL 70 年的核心战场——从 TD-learning 到 PPO 的 clip 到 GRPO 的组相对优势，都是在更稳定地估计信用。

---

## 二、直觉层：RL 是什么 & 为什么需要它

### 2.1 一句话定义

> **强化学习是 agent 在环境里通过试错，学习一个策略 π(a|s)（在状态 s 选动作 a），以最大化长期累积折扣回报。**

### 2.2 为什么需要 RL（vs 监督学习）

| 场景 | 监督学习 | RL |
|------|---------|-----|
| 数据 | (x, y) 配对，有正确答案 | 只有 reward，无「正确动作」|
| 目标 | 预测 y | 最大化累积回报 |
| 决策 | 单步 | **序列**（当前动作影响未来状态）|
| 反馈 | 立即 | **延迟**（最后才知道成败）|

**RL 的独特价值**：当「正确答案」不存在或无法标注，但「好坏」可评估时（如下棋赢/输、证明成立/不成立、代码通过/失败测试）。

### 2.3 三个核心比喻

- **婴儿学走路**：没有教师说「左脚抬高 30 度」，只有「摔倒了/走通了」的反馈 → 试错
- **训练狗**：做对给零食（reward+），做错不理（reward 0）→ 强化成功行为
- **下棋**：每一步没有对错标签，只有最后赢输 → 信用分配回溯到关键步

---

## 三、数学层：4 件骨架

### 3.1 第一件：MDP（马尔可夫决策过程）—— 问题建模

RL 把问题建模为 **MDP 五元组** $(S, A, P, R, \gamma)$：

| 符号 | 含义 | 例子（CartPole）|
|------|------|---------------|
| $S$ | 状态空间 | 杆的位置/速度/角度/角速度 |
| $A$ | 动作空间 | 向左/向右推 |
| $P(s'\|s,a)$ | 转移概率 | 物理模拟器（确定性）|
| $R(s,a)$ | 即时奖励 | 杆直立 +1，倒下 0 |
| $\gamma \in [0,1)$ | 折扣因子 | 0.99（重视未来但避免无限）|

**关键假设**——**马尔可夫性**：未来只依赖当前状态，不依赖历史。$P(s_{t+1} | s_t, a_t, s_{t-1}, ...) = P(s_{t+1} | s_t, a_t)$。

**目标**：找策略 $\pi^*(a|s)$ 最大化期望回报：
$$J(\pi) = \mathbb{E}_\pi\left[\sum_{t=0}^{\infty} \gamma^t R(s_t, a_t)\right]$$

### 3.2 第二件：Bellman 方程 —— 最优性刻画

定义**值函数**（状态 s 下遵循 π 的期望回报）：
$$V^\pi(s) = \mathbb{E}_\pi\left[\sum_{t=0}^{\infty} \gamma^t R(s_t, a_t) \Big| s_0 = s\right]$$

**Bellman 方程**（递归分解，RL 的「微积分基本定理」）：
$$V^\pi(s) = \sum_a \pi(a|s) \sum_{s'} P(s'|s,a) \left[R(s,a) + \gamma V^\pi(s')\right]$$

直觉：当前状态的价值 = 即时奖励 + γ × 下一状态价值（按策略和转移加权）。

**Bellman 最优方程**（最优策略满足）：
$$V^*(s) = \max_a \sum_{s'} P(s'|s,a) \left[R(s,a) + \gamma V^*(s')\right]$$

**Q 函数**（状态-动作价值）：
$$Q^*(s,a) = R(s,a) + \gamma \sum_{s'} P(s'|s,a) \max_{a'} Q^*(s', a')$$

有了 $Q^*$，最优策略就是 $\pi^*(s) = \arg\max_a Q^*(s,a)$。

### 3.3 第三件：策略梯度 —— 可优化的目标

**值函数方法**（DQN/Q-learning）的问题：动作空间连续时 $\arg\max_a$ 不可行。

**策略梯度**：直接参数化策略 $\pi_\theta(a|s)$，对 $J(\pi_\theta)$ 求梯度上升。

**策略梯度定理**（REINFORCE 的理论基础）：
$$\nabla_\theta J(\pi_\theta) = \mathbb{E}_{\tau \sim \pi_\theta}\left[\sum_t \nabla_\theta \log \pi_\theta(a_t|s_t) \cdot G_t\right]$$

其中 $G_t = \sum_{k=t}^{T} \gamma^{k-t} R_k$ 是从时刻 t 起的回报。

直觉：**增大产生高回报轨迹的动作概率，降低低回报的**。$\nabla \log \pi$ 是「向动作 a 倾斜」的方向，$G_t$ 是「该倾多少」的权重。

**问题**：方差爆炸（$G_t$ 抖动大）→ 引入 baseline（减 $V(s_t)$）得 advantage $A_t = G_t - V(s_t)$。

### 3.4 第四件：PPO 与 GRPO —— 稳定训练的工程化

**REINFORCE 的问题**：单步更新可能把策略「推坏」（破坏性大的更新）。

**TRPO/PPO 的核心**（信任区域 / clip）：限制策略更新幅度。

**PPO 的 clipped objective**（2017，OpenAI，至今仍是 RLHF 主力）：
$$L^{CLIP}(\theta) = \mathbb{E}_t\left[\min\left(r_t(\theta) \hat{A}_t,\; \text{clip}(r_t(\theta), 1-\epsilon, 1+\epsilon) \hat{A}_t\right)\right]$$

其中 $r_t(\theta) = \frac{\pi_\theta(a_t|s_t)}{\pi_{\theta_{old}}(a_t|s_t)}$ 是重要性采样比，$\epsilon \approx 0.2$。

直觉：**如果新策略相对旧策略的比值 $r_t$ 偏离 1 太多（>1.2 或 <0.8），就 clip 住**——防止破坏性大更新。

---

### 🟥 2025 标准：GRPO（Group Relative Policy Optimization）

DeepSeek-R1（2025-01）让 **GRPO** 成为 LLM reasoning 的新标准。**关键创新：移除 value function**。

**GRPO 的机制**（对比 PPO）：
- PPO：需要训练一个 critic $V_\phi(s)$ 估计 advantage → 两个网络，critic 难训
- GRPO：**对同一 prompt 采样 G 个回答，用组内回报的相对优势作 advantage**：
$$\hat{A}_i = \frac{R_i - \text{mean}(R_1...R_G)}{\text{std}(R_1...R_G)}$$
- 不需 critic，低方差，对稀疏 reward（数学/代码）特别稳。

**为什么 GRPO 在 LLM reasoning 上碾压 PPO**：LLM 的「状态」是 token 序列，critic 难以准确估计；组内相对优势直接用可验证 reward（答案对/错），简单且稳定。

### 🟥 2025 范式：RLVR（RL with Verifiable Rewards）

RLVR 是 2025 的核心范式转移：**从主观 reward（人类偏好 RLHF）到客观 reward（可验证答案）**。

- RLHF：reward model 学习人类偏好，主观，会幻觉
- RLVR：reward = 数学答案对错 / 代码通过测试 / 证明成立，**客观，不会幻觉**

**RLVR 的关键发现**（2025 研究）：RLVR **不扩展**推理能力，而是**增加正确推理路径的概率**——base model 已隐含正确路径，RLVR 把它们挤出来。这解释了 RLVR 在数学/代码有效（有客观答案），在开放生成难（无客观 reward）。

---

## 四、代码层：最小策略梯度（纯 numpy，可跑）

为了在无 gym 环境验证 RL 核心机制，用**最简单的 k-armed bandit**（RL 的「hello world」）：

```python
# rl_bandit.py —— 最小 RL：k-armed bandit + ε-greedy + reward 更新
# 验证「试错 → 信用分配 → 策略改进」核心循环
import numpy as np

def bandit(k=10, steps=1000, eps=0.1, seed=42):
    rng = np.random.default_rng(seed)
    true_q = rng.normal(0, 1, k)  # 每个臂的真实期望（agent 不知道）
    Q = np.zeros(k)  # 估计值
    N = np.zeros(k)  # 拉次数
    rewards = []
    for t in range(steps):
        # ε-greedy：以 ε 概率探索，否则选当前最优
        a = rng.integers(k) if rng.random() < eps else Q.argmax()
        r = rng.normal(true_q[a], 1)  # 拉臂，得带噪 reward
        N[a] += 1
        Q[a] += (r - Q[a]) / N[a]  # 增量更新均值（信用分配）
        rewards.append(r)
    return np.mean(rewards), Q, true_q

avg_r, Q_est, true_q = bandit()
print(f"平均 reward: {avg_r:.3f}（最优 {true_q.max():.3f}）")
print(f"估计 Q: {np.round(Q_est, 2)}")
print(f"真实 Q: {np.round(true_q, 2)}")
print(f"选中臂: {Q_est.argmax()}（真实最优 {true_q.argmax()}）")
```

**这个 30 行证明了 RL 的核心**：agent 不知道世界（true_q），通过试错（ε-greedy）+ 信用分配（增量更新 Q）→ 收敛到最优臂。

---

## 五、SOTA 全景（2024-2026）

### 5.1 RLVR 时代（2025- 至今）

DeepSeek-R1（2025-01-20）开启 **reasoning model 时代**：
- GRPO + RLVR 训练出推理能力匹敌 OpenAI o1 的开源模型
- 首次公开展示「RL 激活 LLM 推理」的完整长链思维
- 引发 2025 全年的 RL for reasoning 爆发

**2025 reasoning model 爆发**（Nathan Lambert 表）：DeepSeek-R1 / Kimi-1.5 / Phi-4 / Qwen3 / GLM-4.5 / Seed-Thinking / MiMo / Skywork OR-1 / Hunyuan-TurboS / MiniMax-M1 / Nemotron / Ring-1T / DeepSeek V3.2 —— 20+ 个模型用 RLVR 训练推理。

### 5.2 算法进展（2025-2026）

| 算法 | 核心创新 | 解决什么问题 |
|------|---------|------------|
| **GRPO**（DeepSeek）| 组相对优势，移除 critic | critic 难训，稀疏 reward |
| **DAPO** | 高价值采样减 rollout | 采样效率 |
| **VAPO** | PPO 适配推理 | AIME SOTA |
| **VinePPO** | Monte Carlo 无偏估计 | value net 不准 |
| **GMPO** | 几何均值替算术均值 | reward outlier 稳定性 |
| **TreePO** | 树搜索 rollout | 探索不足 |
| **PAPO** | 多模态 RLVR | 感知+推理统一 |
| **PVPO**（2026）| 预估 value baseline + 组采样 | agentic 多步稳定 |
| **MINER**（2026）| intrinsic uncertainty reward | positive homogeneous 浪费 |
| **KARL**（2026）| curiosity-driven knowledge exploration | 知识密集 agent |

### 5.3 Agentic RL（LLM as POMDP policy）

2025-2026 的另一主线：LLM 作为 **POMDP 中的 policy** $\pi_\theta(a|s)$，支持：
- **长程规划**：分解任务为子目标序列
- **工具使用**：学习何时调 API/搜索/计算器
- **持久记忆**：跨轮保持上下文

应用：软件工程（SWE-RL，代码修复/PR 管理）、科学发现、Web 导航、机器人、金融分析。

### 5.4 经典 RL（非 LLM）的前沿

- **AlphaProof**（Nature 2025）：RL + Lean4 + autoformalization，IMO 银牌（详见 B1）
- **世界模型**：DreamerV3 / V-JEPA 2 / Cosmos —— 模型学习世界动力学，用想象规划
- **机器人 RL**：TRPO/PPO/SAC + 模仿学习 + domain randomization
- **离线 RL**：Decision Transformer —— RL 重新表述为序列建模

### 5.5 反方观点（2025 争议）

**「RLVR 真的扩展推理吗？」**——2025 关键争议：
- 一派：RLVR 只是激活 base model 已有能力，不创造新能力（pass@k 不变，pass@1 升）
- 另一派：RLVR + 推理时扩展（test-time scaling）确实提升上界
- **未决**：2026 的研究方向是更强的 verifier + 更可解释的推理链

---

## 六、批判：RL 的根本失败模式

1. **信用分配难**：延迟奖励让归因困难，长程任务尤甚
2. **稀疏 reward**：很多任务反馈稀疏（证明成立/不成立），训练信号弱
3. **样本效率低**：RL 需要海量交互（百万步），远高于监督学习
4. **reward hacking**：agent 找到 reward 的漏洞而非真正解决任务（OpenAI 的 boat racing 例子）
5. **泛化差**：训练环境的策略难迁移到新环境（sim-to-real gap）
6. **不稳定**：超参敏感，训练易崩溃（PPO 的 clip 是缓解，非根治）
7. **可复现性差**：不同 seed 结果差异大

**这些失败模式正是 2025-2026 研究的核心战场**——GRPO（稳定）、RLVR（客观 reward 减 hacking）、MINER（效率）、curiosity-driven（探索）都是在攻这些点。

---

## 七、RL 的数学深度（接 D：作为应用数学方向）

RL 的数学涉及：
- **概率随机过程**：MDP 是随机过程；Bellman 方程是它的泛函方程
- **动态规划**：Bellman 方程的最优性原理
- **优化**：策略梯度是随机优化；PPO 的 clip 是信任区域
- **测度论**：连续状态空间的严格处理
- **博弈论**：多 agent RL = 博弈论；RLHF 的偏好模型
- **信息论**：探索 vs 利用的形式化（KL 散度、熵正则）

**对应用数学方向的契合**：RL 是概率随机过程 + 优化 + 博弈论的**交汇点**——如果你的方向是这些之一，RL 是它们的「应用熔炉」。（D 会深入展开）

---

## 八、📌 下一步（接 B/C/D）

- **B**（并行调研中）：RL+形式化证明 / RL+系统 / RL+科学发现 的 SOTA
- **C**：RL 接入 Neo-OS 的方案（规则蒸馏 reward / 对抗层 Attacker / commit active learning）
- **D**：RL 作为你应用数学方向的评估（契合度 + 6-8 年路径）

**学习建议**（如果你想深入 RL）：
1. **动手**：先跑 CartPole（stable-baselines3 PPO）→ 再读 GRPO 论文
2. **数学**：Sutton & Barto《RL导论》前 9 章（MDP/Bellman/DP/MC/TD/Q-learning/PG）
3. **前沿**：DeepSeek-R1 技术报告 + GRPO 论文（arXiv:2402.03300，需核实）+ AlphaProof Nature 论文
4. **代码**：cleanrl（单文件 RL 实现）是理解算法的最佳途径

---

*A 文档作为 RL 领域的基础 + 前沿参考。B 的三个应用方向调研在并行；C/D 基于本 A 的概念基础展开。*
