# 讲透 RL（强化学习）

> 强化学习是 AI 的"**决策维度**"——监督学习学"是什么"，RL 学"**怎么做才能拿最多奖励**"。从 AlphaGo 到 ChatGPT 的 RLHF，RL 是让 AI 从"懂"到"会做"的关键。
>
> 2024-2026 RL 重新成为显学：DeepSeek-R1 用 GRPO 训出 reasoning、所有 LLM 后训练都用 RLHF/DPO。本系列从 MDP 地基讲到 GRPO，把 RL 在 LLM 时代的方法论钻透。
>
> 配套：[`讲透公开课/01-CS285 Spring 2026`](../讲透公开课/01-前沿课实时清单.md)（Berkeley 深度 RL，2026 版新增 LLM RL 章节）+ [`讲透微调`](../讲透微调/)（RLHF/DPO 实战）+ [`讲透AI应用全景/02-AI4Math`](../讲透AI应用全景/02-AI4Math.md)（AlphaProof 用 RL）

---

## 篇目

| # | 标题 | 状态 | 核心 |
|---|------|------|------|
| **00** | [为什么 RL + MDP 地基](./00-为什么RL与MDP.md) | ✅ | RL vs 监督、MDP 五元组、两大流派、RLHF 复兴 |
| **01** | Q-Learning / DQN 家族 | ✅ | Bellman 方程、值函数方法、DQN 的经验回放/target 网络 |
| **02** | 策略梯度 / PPO | ✅ | REINFORCE → importance sampling → PPO clip |
| **03** | RLHF / DPO / GRPO | ✅ | LLM 对齐三件套、DPO 的数学转化、GRPO 去 critic |
| 04 | Actor-Critic / SAC | 🟡 | 连续控制、最大熵 RL |
| 05 | Offline RL / Model-based RL | 🟡 | CS285 重点，机器人方向 |

---

## 怎么用

- **想懂 ChatGPT/DeepSeek 怎么训的**：00 → 03（RLHF/DPO/GRPO 是当前 LLM 对齐核心）
- **想学经典 RL**：00 → 01 → 02（值函数 + 策略梯度两大主线）
- **想搞机器人/游戏 AI**：01 → 02 → 04 → 05
- **想做 Agent 决策**：00 + 02（PPO 是 Agent 工具调用 RL 的基础）+ 配 [`讲透Agent`](../讲透Agent/)

---

## 配套

- 课：[`讲透公开课/01`](../讲透公开课/01-前沿课实时清单.md) 的 CS285 Spring 2026（新增 LLM RL）
- 数学：[`讲透公开课/02`](../讲透公开课/02-数理计算机神课清单.md) 的 Stat 110（概率/MDP）
- 实战：[`讲透微调`](../讲透微调/) 的 RLHF/DPO 部分
- 源码：[`讲透公开课/03`](<../讲透公开课/03-AI Infra 源码导读清单.md>) 的 T5（verl/AReaL/Miles，RL 后端）
