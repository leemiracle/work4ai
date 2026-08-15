---
card_id: LA-00
title: "讲透学习型 Agent：自我改进的原语与天花板"
universe: 讲透学习型Agent
burke:
  scene: "Agent 用一次就忘，无法越用越聪明"
  agent: "想让 Agent 持续进化的工程师"
  agency: "ICL / 经验回写 / RLHF / 持续微调 / self-play"
  act: "从'每次从零开始'到'从经验中积累改进'"
  purpose: "设计可持续进化的 AI 系统"
tension: "self-improvement 的天花板是 model collapse——在自己输出上训练会退化"
arc: [直觉(四层), 数学(极限), 代码(reflexion agent), 不足(失败模式), 应用(实践)]
status: in_progress
next_card: LA-01
refs:
  - "Zelikman et al., STaR, 2022"
  - "Yuan et al., Self-Rewarding LM, 2024"
  - "Shumailov et al., Model Collapse, 2024 (Nature)"
  - "Shinn et al., Reflexion, 2023"
  - "Sakana AI, Evolutionary Model Merging, 2024"
  - "DeepMind, AlphaProof, 2024"
updated: 2026-08-13
---
# 📈 讲透学习型 Agent：自我改进的原语与天花板

> **User Story**：作为一个想让 Agent 越用越聪明的人，我想理解 Agent 自我改进的原语与陷阱，以便设计可持续进化的系统。

## ⚠️ 与「人怎么学」的区别

work4ai 已有 `费曼学习法/` `故事化学习法/` `cs61a-learning/`——那些讲**人怎么学**。本宇宙讲**Agent 怎么自己学和改进**。同一个词「学习」，主体不同。

## 🎭 戏剧张力

自我改进听起来美好（AlphaGo 自己把自己练成神），但 2024 年 Shumailov 等人在 *Nature* 上钉死了它的天花板：

> **Model Collapse**：当一个模型持续在自己（或同类）的输出上训练，几代之后会不可逆地退化——尾部分布消失，输出越来越平庸，最终坍缩到少数模式。**AI 吃自己的尾巴，会中毒。**

整部「讲透学习型 Agent」在回答：**怎么让 Agent 进化而不 collapse？新信息从哪来？**

## 📚 五幕总览

| 幕 | 文件 | 一句话 |
|---|---|---|
| 直觉 | [`01-直觉-Agent学习四层.md`](01-直觉-Agent学习四层.md) | ICL / 经验回写 / 从反馈学 / 持续微调 |
| 数学 | [`02-数学-自我改进的形式化与极限.md`](02-数学-自我改进的形式化与极限.md) | Erev-Roth / bootstrap / Model Collapse 数学 / 信息论极限 |
| 代码 | [`03-代码-最小learning agent.md`](03-代码-最小learning%20agent.md) | numpy Reflexion 风格 agent，多次尝试成功率上升 |
| 不足 | [`04-不足-学习型Agent失败模式.md`](04-不足-学习型Agent失败模式.md) | collapse / 确认偏误 / 奖励黑客 / 灾难性遗忘 / 对齐退化 |
| 应用 | [`05-应用-学习型系统实践.md`](05-应用-学习型系统实践.md) | AlphaGo / STaR / Self-Rewarding / Reflexion / Sakana |

## 🗺️ Agent 学习的四层（核心分类）

| 层级 | 机制 | 时间尺度 | 是否改权重 | 典型 |
|---|---|---|---|---|
| **L1 上下文学习 ICL** | 把例子塞 prompt | 单次推理 | ❌ | GPT-3 few-shot |
| **L2 经验回写** | 把经验存进记忆/向量库 | 跨会话 | ❌ | mem0 / Reflexion |
| **L3 从反馈学** | 用人类/AI 反馈优化策略 | 训练 | ✅ | RLHF / RLAIF / Constitutional AI |
| **L4 持续微调/self-play** | 用自己生成的数据训练自己 | 多代 | ✅ | STaR / Self-Rewarding / AlphaGo |

**L4 是最强的，也是唯一会 Model Collapse 的**——因为它断了与真实世界的连接。

## 📊 2024-2026 关键进展

- **STaR / V-STaR**（Zelikman 2022-2024）：模型自己生成 reasoning，用对的当训练数据——「自我蒸馏 reasoning」。
- **Self-Rewarding LM**（Yuan 2024）：模型当自己的奖励模型，迭代提升。
- **AlphaProof**（DeepMind 2024）：在 Lean 里 self-play，达到奥数银牌水平——**真实世界的形式化信号防止了 collapse**。
- **Sakana AI evolutionary merging**（2024）：让多个模型「进化合并」，涌现更强模型。
- **Model Collapse**（Shumailov 2024, *Nature*）：理论上证明了自我训练的天花板。

## 💡 核心洞察

> **自我改进的天花板 = 缺乏外部负熵。** Schrödinger 说生命以负熵为食；Agent 也一样。L1-L3 都有外部信号（用户输入/反馈/真实数据），所以不会 collapse；L4 一旦完全封闭（只吃自己的输出），就违背了「耗散结构必须开放」的原理，必然退化。**所以可持续进化的 Agent，必须始终保留与真实世界的信号通道——这是 `故事原语/02-熵论辩证` 的直接推论。**

## 🔗 与其他宇宙

- **[`讲透数据/`](../讲透数据/)**：Model Collapse 的学习面：L4 自食输出的极限——数据宇宙补另一半诊断
- 与 **`讲透记忆/`**：L2 经验回写就是记忆层。
- 与 **`讲透世界模型/`**：model-based RL 的「学世界模型」是一种学习。
- 与 **`故事原语/02-熵论辩证`**：Model Collapse 是「封闭系统熵增」在 AI 上的铁证。

---
📌 **下一步**：`02`（Model Collapse 数学）和 `04`（失败模式）是工程师必读。
