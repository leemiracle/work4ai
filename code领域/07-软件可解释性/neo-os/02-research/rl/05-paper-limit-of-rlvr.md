# 精读 · Limit of RLVR（arXiv:2504.13837）

> **论文**：*Does Reinforcement Learning Really Incentivize Reasoning Capacity in LLMs Beyond the Base Model?*
> **作者**：Yang Yue (乐洋)¹*, Zhiqi Chen¹*, Rui Lu¹, Andrew Zhao¹, Zhaokai Wang², Yang Yue (乐阳)¹, Shiji Song¹, Gao Huang¹ (¹清华 LeapLab, ²上交)
> **核实**：arXiv:2504.13837 ✅ abs 一手核实 · v1 2025-04-18, v5 2025-11-24 · **NeurIPS 2025 Oral + ICML 2025 AI4MATH workshop best paper** · 31 pages 27 figures
> **精读日期**：2026-08-05
> **为何精读**：这是理解 RL 能力边界的**最关键论文**，也是你「系统域 AlphaProof」niche 的**理论锚点**（B1 调研标记）

---

## 一、TL;DR（论文的一句话 + 我的判断）

**论文核心 claim**：**当前 RLVR 只是「分布锐化器」（distribution sharpener），不是「新知发现器」。RLVR 训练的模型在小 k（pass@1）赢 base，但在大 k（pass@256/1024）被 base 反超——RLVR 没教会模型任何 base 采不到的新推理路径。**

**我的判断**：这是 2025 RL 领域**最重要的反方论文**。它用严格的 pass@k 实验证明了一个反直觉结论：所有人以为 RLVR 在「教推理」，实际上它只是「把 base 已有的正确路径的概率调高，代价是覆盖率收缩」。这对你的 Neo-OS（规则蒸馏 + Lean4）有直接启示——**RLVR 在系统域会更糟**（见 §六）。

---

## 二、动机层：论文要回答什么

### 2.1 背景：RLVR 的 2025 神话

2025 年 DeepSeek-R1 / Kimi-1.5 / o1 用 RLVR（Reinforcement Learning with Verifiable Rewards）训练出强推理模型。**主流信念**：像 AlphaGo 通过 self-play 发现新策略一样，RLVR 让 LLM「自主发展新推理模式」（枚举/自我反思/迭代精化），超越 base model。

### 2.2 论文的精确问题

> **RLVR 真的让 LLM 获得超越 base model 的新推理能力吗？还是只是更高效地采样 base 已有的推理路径？**

这是一个**可证伪的经验问题**——用 pass@k（大 k）可以回答。

### 2.3 为什么 pass@k 是对的度量

- pass@1（贪婪/单次采样）只反映「平均表现」
- **pass@k（大 k）**：给模型 k 次机会，只要有一次对就算「能解」。这反映**推理能力边界**（reasoning capacity boundary）
- 如果 RLVR 真教了新能力，RLVR model 应该在大 k 也赢 base（能解更多 base 解不了的问题）

---

## 三、方法层：实验设计（严谨且全面）

### 3.1 三域 × 多模型 × 6 算法

| 维度 | 覆盖 |
|------|------|
| **模型家族** | Qwen2.5 (7B/14B/32B-Base), Qwen2.5-Math-7B, LLaMA-3.1-8B, DeepSeek-R1-Distill-Qwen-7B/14B, Qwen2.5-VL-7B, Magistral-Medium（近前沿）|
| **RL 算法（6 种）** | PPO, GRPO, Reinforce++, RLOO, ReMax, DAPO |
| **数学 benchmark** | GSM8K, MATH500, Minerva, Olympiad, AIME24, AMC23 |
| **代码 benchmark** | LiveCodeBench v5, HumanEval+, MBPP+ |
| **视觉 benchmark** | MathVista, MathVision |
| **指标** | pass@k, k ∈ {1, 8, 16, 32, 64, 128, 256, 1024} |

### 3.2 采样协议

- temperature=0.6, top-p=0.95, max 16384 tokens
- **关键公平性**：base model 不用 few-shot（消除 in-context 混淆），用与 RLVR 训练相同的 zero-shot prompt
- 低方差无偏 pass@k 估计器（Appendix A.2）

---

## 四、核心发现层（精确数字）

### 🟥 发现 1：pass@k 反转（最重要的图——Figure 2）

**现象**：RLVR model 在小 k 赢 base，大 k 被 base 反超。**所有 benchmark、所有模型家族一致**。

精确数字：
- **Minerva 32B**：base 在 k=128 超 RLVR model **~9%**（base 能多解 9% 的问题）
- **Oat-Zero/DAPO**（强 RLVR model）：初始比 base 高 ~30%，但最终被 base 反超
- **AIME24**：同样的反转模式

**含义**：RLVR 提高了「一次就对」的概率（pass@1），但**缩小了「能给 k 次机会时能解的问题集合」**。

### 🟥 发现 2：覆盖率随训练收缩（Figure 1 right）

随 RL 训练进行（Omni-MATH-Rule 训练集）：
- pass@1：26.1 → 42.5（升）✅
- pass@256：**逐步下降**（推理边界变窄）🟥

**含义**：训练越久，模型越「专注于」高 reward 路径，**放弃了** base 原本能覆盖的边缘问题。

### 🟥 发现 3：RLVR 解的问题 ≈ base 解的问题的子集（Table 2）

| 情形 | AIME24 | MATH500 |
|------|--------|---------|
| base ✓, RLVR ✓（两者都能解）| 63.3% | 92.4% |
| base ✓, RLVR ✗（base 能解，RLVR 不能）| **13.3%** | 3.6% |
| base ✗, RLVR ✓（RLVR 能解，base 不能）| **0.0%** | 1.0% |
| base ✗, RLVR ✗（两者都不能）| 23.3% | 3.0% |

**关键**：AIME24 上 RLVR 能解而 base 不能的问题 = **0.0%**。RLVR 解的问题几乎是 base 的子集。

### 🟥 发现 4：Perplexity 证明 RLVR path 已在 base 分布内（Figure 6）

实验：base 和 RLVR model 各生成 16 个回答（Y_base, Y_RL），用 base model 算这些回答的 perplexity。

结果：**PPL_base(Y_RL | x) 的分布紧贴 PPL_base(Y_base | x) 的低端**——RLVR 生成的回答正是 base 高概率生成的回答。

**含义**：RLVR 没有创造新路径，只是把 base 分布里「正确的」路径的概率调高了。

### 发现 5：6 种 RL 算法差异小，都远离最优（Figure 8）

定义 **Sampling Efficiency Gap** Δ_SE = base.pass@256 − RL.pass@1（越小越好）。

- GRPO：43.9 | RLOO：42.6（最好）| 其他都在 42-44
- **所有算法都离最优（Δ_SE=0）很远**（40+ 分 gap）

**含义**：不是「GRPO 比 PPO 好」的问题，是**当前 RLVR 范式整体**离最优采样效率很远。

### 🟢 发现 6：蒸馏不同——真能扩展边界（Figure 7）

DeepSeek-R1-Distill-Qwen-7B 的 pass@k 曲线**一致且显著高于** base model（Qwen2.5-Math-7B）。

**对比**：
- RLVR：pass@k 被base 反超（边界收缩）
- 蒸馏：pass@k 一致高于 base（边界扩展）

**含义**：蒸馏从 teacher 引入**新推理模式**，RLVR 不能。这是两种根本不同的能力提升机制。

---

## 五、理论解释层（§5 Discussion——论文的「为什么」）

论文给出 RLVR 被困在 base 先验里的**两个根本原因**：

### 原因 1：动作空间指数级大

| | 传统 RL（AlphaGo/Atari）| RLVR for LLM |
|---|---|---|
| 动作空间 | Go: ~361 格; Atari: ~18 动作 | LLM: $V^T$（词表^序列长，指数爆炸）|
| 探索 | 可行（空间小）| **几乎不可能从零探索**（空间天文数字）|

### 原因 2：预训练先验是双刃剑

因为动作空间太大，RLVR **必须**从预训练 base model 开始（否则探索不到正 reward）。但：

> 先验引导采样 → 偏离先验的输出大概率无意义 → 负 reward → policy gradient 把概率**拉回先验内** → RLVR 被困在 base 先验里

**这是 R5§6 命门的另一面**：在 Neo-OS，trace 是「先验」；RLVR 会把规则蒸馏困在 trace 的 bug 模式里（完美证明错误规则）。

### 论文建议的未来方向

1. **高层抽象探索**（AlphaEvolve 式程序级，而非 token 级）
2. **更大规模数据策展**
3. **细粒度过程信号**（process reward，不只是 outcome）
4. **多轮 agent-环境交互**

---

## 六、🟥 对 Neo-OS 的启示（你最关心的）

### 6.1 RLVR 在系统域会更糟（三个叠加因素）

| 因素 | 数学域（AlphaProof 等）| 系统域（Neo-OS）| 后果 |
|------|------------------|---------------|------|
| reward 稀疏度 | Lean 证明成立（二元但可达）| trace 保持 Inv（更稀疏，长程）| RLVR 信号更弱 |
| base 先验可信度 | mathlib 是 ground truth | **trace 可能 buggy**（R5§6）| RLVR 困在 buggy 先验 |
| 动作空间 | Lean tactic（结构化）| OS 事件序列（组合爆炸）| 探索更难 |

**结论**：Limit of RLVR 的「分布锐化」结论在系统域会**更严重**——不只「不发现新规则」，还会**固化 trace 里的 bug**。

### 6.2 蒸馏是引入新规则模式的正确路径

论文证明蒸馏能扩展推理边界（发现 6）。对 Neo-OS：
- **从 dsyme 716 定理蒸馏**（ground truth）→ 引入正确的规则模式
- **从 seLe4n 的 Lean4 spec 蒸馏** → 引入 OS 不变式模式
- 这比 RLVR（从 trace 锐化）**更可信**

这与对抗层 v2.0 的 provenance 设计一致：**多源去相关 + ground truth 蒸馏** > RLVR 锐化。

### 6.3 「先验双刃剑」= R5§6 命门的理论基础

论文 §5 的「先验双刃剑」解释，**正是 R5§6 命门（trace 固化 bug → 完美证明错误规则）的理论基础**：
- 数学域：先验（mathlib）可信 → RLVR 锐化无害（只是不扩展）
- 系统域：先验（trace）**可能 buggy** → RLVR 锐化**有害**（固化 bug）

**这是你的论文的核心论点**：系统域 AlphaProof 必须修正 RLVR 的先验假设——引入独立 ground truth（dsyme/人工审计）打破「先验=trace」的循环。

### 6.4 position paper 的理论武器

B2 建议的 position paper「Why RL is the wrong default for formal rule learning in system software」现在有了**理论锚点**：
- Limit of RLVR 证明 RLVR 不扩展边界（数学域）
- 你的贡献：在系统域，不只「不扩展」，还「固化 bug」（因为先验不可信）
- 这是 Limit of RLVR 的**系统域扩展**——站在巨人的肩膀上

---

## 七、局限与反-反方

### 7.1 论文自承的局限
1. **Magistral-Medium 规模未披露**——近前沿但非最强
2. **DeepSeek-R1-Zero 无法自测**（吞吐限制 50 tokens/s）
3. **随机猜测问题**（大 k 数学题可能蒙对）——论文用人工检查 CoT 缓解
4. **未来 RL 范式可能突破**（论文不否认更好的 RL 可能存在）

### 7.2 反-反方（Diversity Collapse, arXiv:2606.15455）
- 认为 Limit of RLVR 的结论是 **overtraining 掩盖**了真实 gain
- BBG（只更新零成功 bucket）可让 pass@256 反超 base
- **争论未定论**，但共识是「当前 RL 配方有问题」

### 7.3 我的判断
Limit of RLVR 的**实验设计严谨**（6 算法 × 3 域 × 多模型，pass@k 大 k），**核心结论稳健**（pass@k 反转在所有设置一致）。反-反方只说「有更好的 RL 配方」，没否定「当前 RLVR 是锐化器」。**作为你的理论锚点，这篇论文足够硬**。

---

## 八、复现规划（最小实验，对标你的 niche）

### 8.1 系统域 pass@k 实验（你的 niche 的直接验证）

**目标**：在系统域（Lean4 规则蒸馏）复现 Limit of RLVR 的 pass@k 反转。

**最小设置**：
1. Base model：Qwen2.5-7B（或 DeepSeek-Prover-V2-7B）
2. RLVR 训练：GRPO + Lean4 reward（LeanDojo-v2 + Pantograph）
3. 数据：SpinlockPreempt v2 的规则 + dsyme 716 定理子集
4. 指标：pass@k（k=1, 8, 32, 128, 256）on 持出测试集
5. 假设：**RLVR model 在大 k 被 base 反超**（复现 Limit of RLVR）

**预期价值**：
- 若复现 → **系统域首次实证 RLVR 是锐化器**（论文级贡献）
- 若未复现 → 系统域与数学域不同，值得深究（也是论文）

### 8.2 「先验双刃剑」在系统域的验证

**额外实验**：用 buggy trace（人为注入错误规则）作 base 先验，跑 RLVR，观察是否：
- RLVR 强化 buggy 规则（pass@1 升但规则错）
- Lean4 仍证明通过（数学级 soundness，语义零价值）

**这直接验证 R5§6 命门**，是对抗层设计的实验支撑。

---

## 九、📌 下一步

1. **立即**：把本精读笔记的 §六（对 Neo-OS 启示）整合进 position paper 大纲——Limit of RLVR 是理论锚点
2. **Phase 1.5**：跑 §8.1 的系统域 pass@k 实验（LeanDojo-v2 + SpinlockPreempt）——这是你 niche 的首个实证
3. **持续跟踪**：Diversity Collapse（arXiv:2606.15455）后续 + Limit of RLVR v6+——反方争论的演进
4. **深化**：读论文 §5 Discussion 的「先验双刃剑」+ AlphaEvolve 的程序级探索（B2 标记的高层抽象方向）

---

## 附：关键引用（已核实）

| 工作 | arXiv | 在本论文的角色 |
|------|-------|-------------|
| **本论文** | **2504.13837** | NeurIPS 2025 Oral，核心 |
| DeepSeek-R1 | guo2025deepseek-r1 | RLVR 代表，被检验 |
| PPO | schulman2017ppo | 6 算法之一 |
| GRPO | shao2024deepseekmath | 6 算法之一，DeepSeek 系标准 |
| DAPO | yu2025dapo | 6 算法之一 |
| AlphaEvolve | novikov2025alphaevolve | 论文建议的未来方向（程序级探索）|
| pass@k 原始 | chen2021evaluating (HumanEval) | 指标来源 |
| Diversity Collapse | 2606.15455 | 反-反方（B1 标记）|

---

*本精读笔记作为 Limit of RLVR 的存档。核心价值：它为你的「系统域 AlphaProof」niche 提供了理论锚点——RLVR 是锐化器而非发现器，在系统域因先验不可信而更危险。*
