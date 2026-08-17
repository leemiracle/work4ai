# 01 · 为什么需要 harness：模型已够聪明，harness 让它可靠

> **核心论点**：agent 在生产环境不可靠，根因通常不是模型笨，而是模型周围的环境（harness）没修好。
> **本文是什么**：三个硬证据 + 一个公式 + 何时该投资 harness 的判断。

---

## 🎯 一个公式

```
Agent = Model + Harness

Model：决定"写什么"（能力上限）
Harness：决定"何时/何地/怎么写"（可靠性下限）
```

生产事故的分布：多数失败发生在 Harness 侧——上下文爆了、状态丢了、验证缺了、跑飞了没刹车。

---

## 🔨 三个硬证据（全部一手核实）

### 证据 1：Anthropic 对照实验（同模型同任务，只改 harness）

| 配置 | 成本/时长 | 产出 |
|---|---|---|
| 无 harness（裸模型 + 提示词）| $9 / 20 min | **不可用** |
| 全套 harness（planner+generator+evaluator）| $200 / 6 h | **可玩的游戏** |

模型没变，harness 变了。（来源：walkinglabs 教程转述 Anthropic 实验，见 [harness精华笔记](../../harness精华合入-总入口.md) §一）

### 证据 2：order-of-magnitude（10×）提升

Meng et al. 2026 综述（preprints 202604.0428，110+ 文献 × 23 系统调研）：**"recent studies demonstrate order-of-magnitude reliability gains achieved through harness redesign alone, with the underlying model held fixed"**——模型不动，仅重设计 harness，可靠性数量级提升。

### 证据 3：AHE 自动进化 harness（arXiv:2604.25850，2026-04）

| 指标 | 数字 |
|---|---|
| Terminal-Bench 2（GPT-5.4-high 底座）| 69.7% → **77.0%**（10 轮进化，超人工设计 Codex 71.9%）|
| 冻结迁移 SWE-bench-verified | 最高聚合成功 + **省 12% token** |
| 跨 3 个模型家族迁移 | +5.1 ~ +10.1pp |
| **消融** | 增益定位在 **tools / middleware / 长期记忆**；仅改 system prompt **负收益** |

---

## 🧭 四范式演化：harness 为什么是现在

（Guo et al. 2026, arXiv:2606.20683 的历史动量）

```
Phase 1  Prompt Engineering     "怎么问"        → 撞墙：表达问题解决不了信息问题
Phase 2  Context Engineering    "给什么信息"    → 撞墙：前馈结构检测不了漂移、恢复不了错误
Phase 3  Harness Engineering    "怎么闭环"      → ★当前：反馈驱动的运行时成为设计对象
Phase 4  Co-evolution           "模型-harness 共同进化"（agent-native 训练 + 可学习 harness）
```

每次迁移都是前一范式的天花板变成后一范式的地板。2026 上半年四篇 harness 综述密集出现（Meng 六组件 / Li 七层 / Ning code 中心 / Guo 耦合视角）——**harness 正在成为独立学科**。

---

## 🩺 判断：你的问题该换模型还是修 harness

```
症状 → 先跑同模型对照实验（同任务，SWE-bench 式）：
├─ 加了 harness 后明显变好 → 修 harness（本手册全部章节）
├─ 加了 harness 还是不行 → 模型能力真缺 → 换/加模型（08 章多模型）
└─ 时好时坏 → 状态/验证缺失 → 05/06 章
```

**经验律**：模型能力不足时 harness 无米之炊（$9→$200 实验的前提是"模型已够聪明"）；模型够用时 harness 是唯一杠杆。

---

## ⚠️ 边界（诚实声明）

- harness 收益**随模型能力饱和而衰减**（AHE 跨模型迁移：离饱和越远获益越大）——它是对能力缺口的功能补偿，不是普适增益
- "10×" 是 benchmark 分布上的数字，你的任务分布不同——抄完参数要用自己任务回归（见 10 章）
- harness 有维护税：六组件每件都是要人管的代码

---

## 📌 本周必做

1. [ ] 把你最不可靠的一个 agent 任务写成对照实验：裸模型 vs +验证脚本 vs +完整四文件
2. [ ] 数一数你的项目里六组件（E/T/C/S/L/V）各缺哪件（用 03 章矩阵）

## 📚 推荐深读

- walkinglabs/learn-harness-engineering（11.4k★，教程本体）
- [harness三综述合并解析](../../harness三综述合并解析.md) §1.3 证据链
- AHE: arXiv:2604.25850（消融部分必读）

---

**版本**：v1.0（2026-08-17）
**核心隐喻**：模型是骑手，harness 是路。骑手已经会骑了；翻车多半是路的问题。
