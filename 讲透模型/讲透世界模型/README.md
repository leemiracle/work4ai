---
card_id: WM-00
title: "讲透世界模型：智能即预测"
universe: 讲透世界模型
burke:
  scene: "Agent 要在没见过的情境下做对选择"
  agent: "想造能在复杂世界行动的 Agent 的研究者"
  agency: "MDP transition / MCTS / JEPA / diffusion world model"
  act: "从'只能反应'到'能预测未来并据此规划'"
  purpose: "获得泛化与长程规划能力"
tension: "像素级预测清晰但无用，抽象预测有用但难训——世界模型的根本两难"
arc: [直觉(智能即预测), 数学(MDP+MCTS+JEPA), 代码(gridworld MCTS), 不足(失败模式), 应用(2024-2026浪潮)]
status: done
next_card: WM-01
refs:
  - "Ha & Schmidhuber, World Models, 2018"
  - "LeCun, JEPA, 2022"
  - "Schrittwieser et al., MuZero, 2020"
  - "NVIDIA Cosmos, 2025"
  - "V-JEPA 2 (Meta), 2025"
  - "Genie 2 (DeepMind), 2024"
  - "Sora (OpenAI), 2024"
updated: 2026-08-15
---
# 🌍 讲透世界模型：智能即预测

> **User Story**：作为一个想让 Agent 在复杂世界行动的人，我想理解预测与规划的原语，以便它在没见过的情景做对选择。

## 🎭 戏剧张力

世界模型的根本两难（LeCun JEPA 的核心动机）：

> **在像素空间预测未来**（如 Sora 生成视频）→ 清晰可衡量，但对决策几乎无用（像素太多、无关细节太多）。
> **在抽象表征空间预测未来**（如 JEPA）→ 对决策有用，但缺乏监督信号、极难训练（什么叫「预测对了」？）。

整部「讲透世界模型」围绕这个两难展开：**预测什么，用什么粒度，怎么知道预测对了？**

## 📚 目录宪法（2026-08-15 重构：消双号，两层分层）

### 基础层（00 + 五幕主线）

| # | 文件 | 一句话 |
|---|---|---|
| 00 | [00-什么是世界模型.md](00-什么是世界模型.md) | 概念入门：四派统一框架（视频生成/RL 内部模型/认知架构/具身）+ 判定标准 |
| 直觉 | [01-直觉-智能即预测.md](01-直觉-智能即预测.md) | 预测编码 + 自由能原理 + LLM 也是某种世界模型 |
| 数学 | [02-数学-预测与规划的形式化.md](02-数学-预测与规划的形式化.md) | MDP transition / value iteration / MCTS / JEPA loss / diffusion |
| 代码 | [03-代码-最小世界模型+MCTS.md](03-代码-最小世界模型+MCTS.md) | gridworld 世界模型 + MCTS 200 行 |
| 不足 | [04-不足-预测的失败模式.md](04-不足-预测的失败模式.md) | distribution shift / model exploitation / 想象力的诅咒 |
| 应用 | [05-应用-2024-2026世界模型浪潮.md](05-应用-2024-2026世界模型浪潮.md) | Cosmos/Sora2/Genie2/V-JEPA2/Dreamer V3/机器人 VLA |

### 研究生层（[`advanced/`](advanced/)，深读线）

| 文件 | 一句话 |
|---|---|
| [advanced/02-JEPA数学与LeCun路线.md](advanced/02-JEPA数学与LeCun路线.md) | JEPA vs diffusion 的数学对决；LeCun 路线全解 |
| [advanced/03-视频生成是世界模型吗.md](advanced/03-视频生成是世界模型吗.md) | Sora 之辩：8 级判定标准（L1-L8）+ 反事实实验设计 |
| [advanced/04-开放问题与研究方向.md](advanced/04-开放问题与研究方向.md) | 方向 1-5：LLM 是 World Model 吗 / scaling 够不够 / 因果必需性 |
| [advanced/05-论文清单.md](advanced/05-论文清单.md) | 30+ 篇必读论文地图（研究生层入口） |

### 辅助

| 文件 | 一句话 |
|---|---|
| [HISTORY.md](HISTORY.md) | 领域编年 + 四派格局 + 学习路径复盘 |
| [00-讲透笔记-算法经验枢纽.md](00-讲透笔记-算法经验枢纽.md) | 跨单元算法经验索引（WM1-WM7：Sora 物理涌现 / LLM=语言世界模型…） |

> **消双号说明**：原根目录下 02-JEPA/03-视频/04-开放/05-论文清单与五幕主线同号并存（两个 02/03/04/05），2026-08-15 移入 `advanced/` 物理消歧（仿 `讲透基础模型/advanced/` 先例）；全库 30+ 处入链与文件内互链已同步修正。这些文件的互链原按子目录编号编写（01-JEPA/02-视频/00-论文清单），拍平到根目录时曾整体失效，本次随迁移一并修复。

## 🗺️ 2024-2026 世界模型浪潮（关键节点）

| 系统 | 机构 | 路线 | 意义 |
|---|---|---|---|
| **Sora / Sora 2** | OpenAI | 像素级 diffusion | 视频生成；「是不是世界模型」争议巨大 |
| **Genie 2** | DeepMind | 可交互 3D 世界模型 | 从图像学出可控游戏世界 |
| **V-JEPA 2** | Meta | 抽象表征预测（JEPA） | LeCun 路线的最新验证 |
| **NVIDIA Cosmos** | NVIDIA | 物理世界基础模型 | 给机器人/自动驾驶当「世界模拟器」 |
| **Dreamer V3** | DeepMind | latent 想象 + actor-critic | model-based RL 的 SOTA |
| **1X World Model** | 1X | 机器人本体世界模型 | 真实机器人数据训练 |
| **World Labs** | Fei-Fei Li | 空间智能 3D 世界模型 | 2024 成立，估值快速破百亿 |

## 💡 核心洞察

> **LLM 的 next-token prediction 其实是一种「语言世界模型」**——它预测「在这个语言宇宙里，下一个观测是什么」。争论「LLM 是不是世界模型」是错的问题；正确的问题是：**它在哪个粒度上预测，预测对决策有多有用？** 语言粒度对语言任务有用，对开机器人没用——这就是为什么世界模型在 2024-2026 全面转向视觉/物理/具身。

## 🔗 与其他宇宙

- **[`讲透视频/`](../讲透视频/)**：视频生成=像素级世界模型，JEPA 流=抽象级世界模型——两条路线之争
- 与 **`讲透记忆/`**：记忆是「过去的世界模型」，世界模型是「对未来的记忆」。
- 与 **`讲透RL/`**（已有）：model-based RL 的「model」就是世界模型。
- 与 **`讲透多模态/`**：视觉/物理世界模型依赖多模态。

---
📌 **下一步**：`advanced/02`（JEPA vs diffusion 的数学对比）和 `04-不足`（model exploitation）是核心。
