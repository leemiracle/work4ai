# 05 · RLVR 的极限（pass@k 反转 —— 2025 最重要的 RL 反方论文）

> 这是 RL 系列的**批判性核心**。[03](./03-RLHF-DPO-GRPO.md) 讲了 RLHF/DPO/GRPO 怎么训出 ChatGPT/DeepSeek-R1，[04](./04-RL与形式证明.md) 讲了 RL 怎么证定理。但本章用一篇 NeurIPS 2025 Oral 论文证明：**当前所有人以为 RL 在"教推理"，实际上它只是"把 base 已有的正确路径概率调高，代价是覆盖率收缩"**。这会颠覆你对 RL 增益的直觉。
>
> 精读论文：*Does Reinforcement Learning Really Incentivize Reasoning Capacity in LLMs Beyond the Base Model?*（Yue et al., 清华 LeapLab, arXiv:2504.13837 ✅, NeurIPS 2025 Oral + ICML 2025 AI4MATH best paper）

---

## 一、直觉：RLVR 到底教了什么？

### 1.1 2025 的主流神话

DeepSeek-R1 / Kimi-1.5 / o1 用 **RLVR（Reinforcement Learning with Verifiable Rewards）**——奖励是"答对=1/答错=0"的**可验证奖励**——训出强推理模型。**主流信念**：

> 像 AlphaGo 通过 self-play **发现新策略**一样，RLVR 让 LLM **自主发展新推理模式**（枚举、自我反思、迭代精化），超越 base model。

### 1.2 论文的精确质疑

> RLVR 真的让 LLM 获得超越 base model 的**新推理能力**吗？还是只是更高效地采样 base 已有的推理路径？

这是**可证伪的经验问题**。论文用 `pass@k`（大 k）回答。

### 1.3 为什么 pass@k 是对的度量

| 指标 | 反映什么 |
|------|---------|
| pass@1（贪婪/单次采样）| "平均表现" |
| **pass@k（大 k，k=256/1024）** | "**推理能力边界**"——给模型 k 次机会只要一次对就算"能解" |

> 🎯 **关键判断**：如果 RLVR 真教了新能力，RLVR model 应该在**大 k** 也赢 base（能解更多 base 解不了的问题）。反之如果只是锐化，大 k 会被 base 反超。

---

## 二、实验设计（严谨且全面）

论文覆盖**三域 × 多模型 × 6 算法**，是 RL 领域罕见的大规模严谨实验：

| 维度 | 覆盖 |
|------|------|
| **模型家族** | Qwen2.5 (7B/14B/32B-Base), Qwen2.5-Math-7B, LLaMA-3.1-8B, DeepSeek-R1-Distill-Qwen-7B/14B, Qwen2.5-VL-7B, Magistral-Medium |
| **RL 算法（6 种）** | PPO, GRPO, Reinforce++, RLOO, ReMax, DAPO |
| **数学 benchmark** | GSM8K, MATH500, Minerva, Olympiad, AIME24, AMC23 |
| **代码 benchmark** | LiveCodeBench v5, HumanEval+, MBPP+ |
| **视觉 benchmark** | MathVista, MathVision |
| **指标** | pass@k, $k \in \{1, 8, 16, 32, 64, 128, 256, 1024\}$ |

**采样协议**：temperature=0.6, top-p=0.95, max 16384 tokens；base 不用 few-shot（消除 in-context 混淆）；低方差无偏 pass@k 估计器。

---

## 三、核心发现（精确数字）

### 🟥 发现 1：pass@k 反转（最重要的图——Figure 2）

**现象**：RLVR model 在小 k 赢 base，**大 k 被 base 反超**。所有 benchmark、所有模型家族一致。

精确数字：
- **Minerva 32B**：base 在 k=128 超 RLVR model **~9%**（base 能多解 9% 的问题）
- **Oat-Zero / DAPO**（强 RLVR model）：初始比 base 高 ~30%，但最终被 base 反超
- **AIME24**：同样的反转模式

> 🎯 **含义**：RLVR 提高了"一次就对"的概率（pass@1），但**缩小了"给 k 次机会时能解的问题集合"**。

### 🟥 发现 2：覆盖率随训练收缩（Figure 1 right）

随 RL 训练进行：
- pass@1：26.1 → 42.5（升）✅
- pass@256：**逐步下降**（推理边界变窄）🟥

**含义**：训练越久，模型越"专注"高 reward 路径，**放弃**了 base 原本能覆盖的边缘问题。

### 🟥 发现 3：RLVR 解的问题 ≈ base 的子集（Table 2）

| 情形（AIME24）| 占比 |
|--------------|------|
| base ✓, RLVR ✓（两者都能解）| 63.3% |
| base ✓, RLVR ✗（base 能解，RLVR 不能）| **13.3%** |
| **base ✗, RLVR ✓（RLVR 能解，base 不能）** | **0.0%** ⚠️ |
| base ✗, RLVR ✗（都不能）| 23.3% |

> 🟥 **最致命的数字**：AIME24 上 RLVR 能解而 base 不能的问题 = **0.0%**。RLVR 解的问题几乎是 base 的**子集**。

### 🟥 发现 4：Perplexity 证明 RLVR path 已在 base 分布内（Figure 6）

实验：base 和 RLVR model 各生成 16 个回答，用 base model 算这些回答的 perplexity。

结果：$\text{PPL}_\text{base}(Y_\text{RL} | x)$ 的分布紧贴 $\text{PPL}_\text{base}(Y_\text{base} | x)$ 的**低端**——RLVR 生成的回答正是 base **高概率生成**的回答。

> 🎯 **含义**：RLVR 没创造新路径，只是把 base 分布里"正确的"路径概率调高了。

### 发现 5：6 种 RL 算法差异小，都远离最优（Figure 8）

定义 **Sampling Efficiency Gap** $\Delta_{SE} = \text{base.pass@256} - \text{RL.pass@1}$（越小越好）：

| 算法 | $\Delta_{SE}$ |
|------|---------------|
| GRPO | 43.9 |
| RLOO | 42.6（最好）|
| 其他 | 42-44 |

所有算法都离最优（$\Delta_{SE}=0$）很远（40+ 分 gap）。**不是"GRPO 比 PPO 好"的问题，是当前 RLVR 范式整体离最优采样效率很远。**

### 🟢 发现 6：蒸馏不同——真能扩展边界（Figure 7）

DeepSeek-R1-Distill-Qwen-7B 的 pass@k 曲线**一致且显著高于** base（Qwen2.5-Math-7B）。

| 机制 | pass@k 表现 |
|------|------------|
| RLVR | 被base 反超（边界收缩）|
| **蒸馏** | **一致高于 base（边界扩展）** |

> 🎯 **核心对比**：蒸馏从 teacher 引入**新推理模式**，RLVR 不能。这是两种根本不同的能力提升机制。

---

## 四、数学解释：为什么 RLVR 会被困在 base 先验里

论文 §5 给出两个根本原因。

### 4.1 原因 1：动作空间指数级大

| | 传统 RL（AlphaGo/Atari）| RLVR for LLM |
|---|---|---|
| 动作空间 | Go: ~361 格; Atari: ~18 动作 | LLM: $V^T$（词表^序列长，**指数爆炸**）|
| 探索 | 可行（空间小）| **几乎不可能从零探索** |

### 4.2 原因 2：预训练先验是双刃剑

因为动作空间太大，RLVR **必须**从预训练 base model 开始（否则探索不到正 reward）。但：

```
先验引导采样
  → 偏离先验的输出大概率无意义
  → 负 reward
  → policy gradient 把概率拉回先验内
  → RLVR 被困在 base 先验里
```

> 🎯 **这是 RLVR 本质的数学描述**：policy gradient 在指数空间里，唯一能稳定提升 reward 的方向就是"强化 base 已有的高概率正确路径"。探索新路径的信号被噪声淹没。

### 4.3 形式化（直觉版）

设 base 分布为 $p_0(y|x)$，RLVR 优化后的分布为 $p_\theta(y|x)$。KL 正则化的 RL 目标：

$$
\max_\theta \; \mathbb{E}_{y \sim p_\theta}[r(x,y)] - \beta \cdot \text{KL}(p_\theta \| p_0)
$$

这个目标的解倾向于**在 $p_0$ 的高概率区域重新分配权重**（把 $p_0$ 里 reward 高的部分的概率调高，把 reward 低的部分调低），而**不创造 $p_0$ 几乎不支持的路径**——因为提升一个 $p_0 \approx 0$ 的路径的概率，KL 惩罚极大，reward 收益不确定。

这就是"分布锐化"的数学含义。

---

## 五、论文建议的未来方向

论文 §5 Discussion 指出突破 RLVR 边界的四个方向：

1. **高层抽象探索**（AlphaEvolve 式程序级，而非 token 级）——动作空间从 $V^T$ 降到"程序片段"，探索可行
2. **更大规模数据策展**——让 base 先验本身就覆盖更多
3. **细粒度过程信号**（process reward，不只是 outcome）
4. **多轮 agent-环境交互**

> 📌 **关键**：论文**不否认更好的 RL 可能存在**，只证明"当前 RLVR 范式（outcome reward + token 级）是锐化器"。未来突破点在"高层动作空间 + 过程奖励 + agent 交互"。

---

## 六、为什么这个结论重要（对每个 RL 从业者）

### 6.1 颠覆了"RL 教 reasoning"的叙事

2025 主流叙事：DeepSeek-R1 / o1 用 RL 训出 reasoning。这篇论文说：**reasoning 能力本来就在 base 里**（预训练给的），RL 只是让它"更频繁地表现出来"。R1-Zero 涌现的"wait, let me think..."反思链，base model 采样足够多次也能采到——RL 只是提高了它的概率。

### 6.2 解释了 R1-Zero 可复现性困难

很多团队复现 R1-Zero 失败。这篇论文给了一个解释：**RLVR 的增益高度依赖 base 的先验**。不同 base model 的先验不同，同样的 RL 配方在 A 上有效（A 的先验里有正确路径），在 B 上无效（B 的先验里没有）。这不是超参问题，是**根本机制**问题。

### 6.3 指出"蒸馏 > RL"的工程含义

如果目标是"让模型会更多 reasoning 模式"：
- ❌ RLVR：只能锐化 base 已有的
- ✅ **蒸馏**：从 teacher 引入 base 没有的新模式

> 🎯 **工程含义**：与其花大算力 RLVR，不如找一个强 teacher 蒸馏——后者真正扩展能力边界。DeepSeek-R1 正式版也是用 R1 蒸馏到小模型传播能力，不是让小模型自己 RL。
>
> 📎 **深化（2026-08-27）**：本发现（蒸馏扩边界 vs RLVR 榨取）已织入蒸馏全景——OPD 解耦定理证明"OPD=dense-reward on-policy RL"，蒸馏与 RL 是假对立，真光谱是 reward 密度与来源。见 [100-模型蒸馏全景2026-深读卡 §四](../../前沿与媒体/100-模型蒸馏全景2026-深读卡.md)。

---

## 七、局限与反-反方（批判性）

### 7.1 论文自承的局限

1. **Magistral-Medium 规模未披露**——近前沿但非最强
2. **DeepSeek-R1-Zero 无法自测**（吞吐限制 50 tokens/s）
3. **随机猜测问题**（大 k 数学题可能蒙对）——论文用人工检查 CoT 缓解
4. **未来 RL 范式可能突破**（论文不否认）

### 7.2 反-反方：Diversity Collapse（arXiv:2606.15455）

- 认为 Limit of RLVR 的结论是 **overtraining 掩盖**了真实 gain
- BBG（只更新零成功 bucket）可让 pass@256 反超 base
- **争论未定论**，但共识是"当前 RL 配方有问题"

### 7.3 我的判断

Limit of RLVR 的**实验设计严谨**（6 算法 × 3 域 × 多模型，pass@k 大 k），**核心结论稳健**（pass@k 反转在所有设置一致）。反-反方只说"有更好的 RL 配方"，没否定"当前 RLVR 是锐化器"。

> 📌 **作为理论锚点，这篇论文足够硬**。它是理解 RL 能力边界的最关键论文，没有之一。

---

## 八、对你项目的启示

### 8.1 别把 RLVR 当"能力来源"

如果你训一个 reasoning 模型：
- **base 选型最重要**：RLVR 只能锐化，所以 base 必须先有 reasoning 潜力（预训练数据决定）
- **蒸馏是更可靠的能力注入路径**：从强 teacher 蒸馏 > 自己 RLVR
- **RLVR 适合"性能榨取"**：base 已有能力，RLVR 让它稳定输出（pass@1 提升）

### 8.2 系统域 / 形式化域会更糟

详见 [04 篇](./04-RL与形式证明.md) 和 [06 篇](./06-RL与系统软件.md)：

| 因素 | 数学域 | 系统域 | 后果 |
|------|--------|--------|------|
| reward 稀疏度 | Lean 证明（二元但可达）| trace 保持 Inv（更稀疏，长程）| RLVR 信号更弱 |
| base 先验可信度 | mathlib 是 ground truth | **trace 可能 buggy** | RLVR 固化 bug |
| 动作空间 | Lean tactic（结构化）| OS 事件序列（组合爆炸）| 探索更难 |

**结论**：Limit of RLVR 的"分布锐化"结论在系统域会**更严重**——不只"不发现新规则"，还会**固化 trace 里的 bug**。

### 8.3 如何设计能扩展边界的 RL

论文给的四个方向（[§五](#五论文建议的未来方向)）就是工程指引：
1. 动作空间从 token 级升到**程序/规则级**（AlphaEvolve 式）
2. 用**过程奖励**替代 outcome 奖励（每一步给信号，不只是最终）
3. 加**多轮 agent-环境交互**（让模型能看到反馈再调整）
4. 接受**蒸馏优先于 RL**作为能力注入主路径

---

## 九、一句话总结

> 🎯 **三句话**：
> 1. **核心结论**：RLVR 是"分布锐化器"不是"发现器"——pass@1 赢 base，但 pass@k（大 k）被 base 反超；RLVR 能解而 base 不能的问题在 AIME24 上 = **0.0%**。
> 2. **数学根因**：LLM 动作空间 $V^T$ 指数爆炸，policy gradient 唯一稳定方向是"强化 base 已有高概率正确路径"，探索新路径的信号被淹没——这是 KL 正则化目标的必然解。
> 3. **工程含义**：base 选型决定 reasoning 上限（RL 只能榨取），**蒸馏比 RL 更能扩展能力边界**；想突破 RLVR 必须改动作空间（程序级）+ 加过程奖励 + agent 交互。

📌 **下一步**：回到 [04 RL 与形式证明](./04-RL与形式证明.md) 看这个结论在形式化域的具体表现，或进 [06 RL 与系统软件](./06-RL与系统软件.md) 看生产系统里 RL 的真实定位。

---

## 附：关键引用（已核实）

| 工作 | arXiv | 在本论文的角色 |
|------|-------|-------------|
| **本论文（Limit of RLVR）** | **2504.13837** ✅ | NeurIPS 2025 Oral + ICML 2025 best paper，核心 |
| DeepSeek-R1 | guo2025deepseek-r1 | RLVR 代表，被检验 |
| PPO | schulman2017ppo | 6 算法之一（[02 篇](./02-策略梯度与PPO.md)）|
| GRPO | shao2024deepseekmath | 6 算法之一（[03 篇](./03-RLHF-DPO-GRPO.md)）|
| DAPO | yu2025dapo | 6 算法之一 |
| AlphaEvolve | novikov2025alphaevolve | 论文建议的未来方向（程序级探索）|
| pass@k 原始 | chen2021evaluating (HumanEval) | 指标来源 |
| Diversity Collapse | 2606.15455 ⚠️ | 反-反方（争论中）|
