# 11 · 让 AI 思考：推理模型与 AlphaProof（2024-2026）

> **时间**：2024-2026，2 年
> **核心冲突**：LLM 会"快思考"，不会"慢思考"。怎么让它真正推理？
> **嵌入概念**：Test-time scaling、o1、R1、Lean 4、形式化数学、AlphaProof

---

## 🎬 故事

### 2024 · System 1 vs System 2

Daniel Kahneman（诺贝尔经济学奖得主）2011 年的畅销书《Thinking, Fast and Slow》：

- **System 1**：快思考。直觉反应。5+5=10。
- **System 2**：慢思考。仔细推理。17×24=408。

2024 年之前，**所有 LLM 都是 System 1**——它们生成 token 快，但没有"想很久"的能力。

### 2024 年 9 月 · OpenAI o1

**OpenAI o1** 发布。号称 "Strawberry" 项目。

o1 的核心：**test-time scaling**——回答前**生成大量 "thinking tokens"**，然后才出答案。

**例子**：解一道数学题：
- GPT-4o：直接给答案（可能错）
- o1：先想 10000 个 token（"我需要先列方程..."、"然后..."、"验证一下..."），然后才给答案

**结果**：o1 数学 / 代码 / 推理**大幅超越 GPT-4o**。

### Test-time Compute 是新维度

传统 scaling：训更大模型（compute 用于训练）
**o1 新维度**：推理时多算（compute 用于推理）

**反直觉**：用同一个 base model，**推理时多算 100 倍**，效果可以**超过参数大 10 倍的模型**。

**这就是 RL 的胜利**——o1 用 RL 训练"如何思考"。

### 2024 年 7 月 · AlphaProof IMO 银牌

DeepMind **AlphaProof** + **AlphaGeometry 2**：IMO 2024 银牌水平（4/6 题）。

**AlphaProof 的秘密**：
- 用 **Lean 4**（形式化数学语言）当推理环境
- **RL with Verifiable Rewards**（RLVR）——Lean 通过 / 不通过就是 reward
- 把非形式化数学翻译成 Lean，再让 Lean verifier 检查

### 2025 年 11 月 · AlphaProof Nature 论文

DeepMind 在 Nature 发表：**"AlphaProof formalizes mathematical proofs at Olympiad level"**（arXiv: 2405.20363，最终 Nature 版本）。

**Tao 评价**："This is like a top-25 student in IMO."

### Lean 4：形式化数学的标准

**Lean**（2013 由 Leonardo de Moura 微软研究院创建）：
- 函数式编程语言
- **定理证明器**（theorem prover）
- 类似 Haskell 但更强类型系统

**Lean 4**（2021）：完全用 Lean 自己写，可编译成 C。

**Mathlib**（Lean 数学库）：100 万+ 行代码，覆盖本科-研究生数学。

**为什么 Lean 重要**：
- 形式化证明**100% 正确**（计算机验证）
- AI 用 Lean 不用担心幻觉——通过 verifier 就是对的
- **数学家可以和 AI 协作**（AI 提猜想，Lean 验证）

### 2024-2025 · Tao 与 Lean

**Terence Tao**（Fields Medal）2024 起全力推 Lean：
- **Tao Analysis I Lean companion**：把他的实分析教材形式化
- **Equational Theories Project**：大规模证明等式理论

Tao 2024 年 blog：
> "Lean is going to change how mathematics is done in the next decade."

### 2024-2025 · AI for Math 工具

- **LeanDojo**（Caltech）：开源 Lean ML 环境
- **LeanCopilot**：VS Code 内 LLM 补全 Lean
- **Mathlib 嵌入模型**：学 Lean 数学库

**这是 AI × 数学的新范式**：
- 形式化作为"裁判"
- RL 让 AI 搜索证明
- 数学家 + AI 协作

### 2025 年 1 月 · DeepSeek R1 开源 o1 级

**DeepSeek R1**：开源 o1 级推理模型。

**核心方法**：**GRPO + RLVR**
- **GRPO**（Group Relative Policy Optimization）：不用 reward model
- **RLVR**：数学对错就是 reward

R1 一发布，**开源圈震动**——**首次有开源模型接近 o1**。

### 推理模型的三种路径

**路径 A**：o1 路径——RL + thinking tokens（OpenAI 闭源）
**路径 B**：R1 路径——GRPO + RLVR（DeepSeek 开源）
**路径 C**：AlphaProof 路径——Lean + RL（DeepMind 专攻数学）

**3 种路径都验证了 RL 在推理时的威力**。

---

## 🧠 核心概念

- **Test-time scaling**：推理时多算。新 scaling 维度。
- **System 1 / System 2**（Kahneman）：快思考 / 慢思考。LLM 之前只有 System 1。
- **o1**（OpenAI）：闭源 RL 推理模型。
- **R1**（DeepSeek）：开源 RL 推理模型。GRPO。
- **Lean 4**：形式化数学语言 + 定理证明器。
- **Mathlib**：Lean 数学库，100 万行。
- **AlphaProof**：DeepMind IMO 银牌。Lean + RL。
- **RLVR**（RL with Verifiable Rewards）：规则驱动 RL。

## 🎨 类比

- **System 1** = 直觉：你看到 5+5 立刻说 10
- **System 2** = 算草稿：你算 17×24 时在纸上列竖式
- **o1 / R1** = 强制 LLM 用 System 2——给"草稿纸"（thinking tokens）
- **Test-time scaling** = 不是让模型更聪明（参数多），是让模型**想更久**（推理多算）
- **Lean** = 一个**绝对严格的数学老师**：任何证明必须 100% 严谨才通过
- **AlphaProof** = AI 在 Lean 老师指导下证明——错了 Lean 立刻说，AI 不断改
- **RLVR** = 用规则当裁判（不用主观偏好）：数学对错明确，避免了 RLHF 的 reward hacking

## 💡 反直觉发现

1. **推理时多算 > 训练时多算**（在推理任务上）：o1 用 GPT-4 级 base model + RL，超过 10 倍参数的模型。

2. **Lean 让 AI 数学"零幻觉"**：通过 Lean verifier = 100% 正确。**这是 RL 的理想环境**——不需要学人类偏好，规则就是 truth。

3. **AlphaProof 是 AI 数学分水岭**：2024 之前 AI 数学不行。**2024 IMO 银牌 → 2025 Nature 论文 → 2026+ 形式化数学范式**。

4. **DeepSeek 开源震撼**：R1 2025-01 开源后，**所有公司都跟进 RLVR**。**开源不再是追赶者，开始引领方向**。

5. **Tao 50 岁拥抱 AI**：Tao 不是 AI 出身，**但 2024 起他成为 AI for Math 的布道者**。**顶级数学家也在 adapt**。

6. **test-time scaling 重新定义成本**：之前 LLM 成本 = 参数 × token。**o1 后 = 推理时多算 100-1000 倍 token**。**新的成本结构**。

## 🛠️ 我该深挖什么

### work4ai 系列
- [`../讲透Lean4数学/`](../讲透Lean4数学/)：Lean 4 入门 + 数学应用
- [`../讲透实分析/`](../讲透实分析/)：Tao Analysis I Lean companion
- [`../讲透RL/05 RLVR极限`](../讲透RL/)：RLVR 深度
- [`../讲透神经符号/`](../讲透神经符号/)：LLM + Lean 闭环

### 必读
- **OpenAI 2024 "Learning to Reason with LLMs"**（o1 blog）
- **DeepSeek 2025 "DeepSeek-R1: Incentivizing Reasoning Capability"**（arXiv 2501.12948）
- **DeepMind 2025 "AlphaProof"**（Nature s41586-025-09833-y）
- **Tao blog "Lean 资源"**（terrytao.wordpress.com）

### 实验
```python
# 1. 装 Lean 4 + 跑通 Mathlib
# 2. 完成 NNG（Natural Number Game）—— Lean 入门
# 3. 让 LLM 帮你写 Lean 证明，看哪些它能写对
```

---

## 🔗 下一篇

下一篇：[**12 · 让 AI 可解释：Mech Interp 侦探故事**（2020-2026）](12-让AI可解释-Mech-Interp.md)——黑箱如何变玻璃箱。

---

**版本**：v1.0（2026-08-13）
**核心隐喻**：**LLM 之前只会"脱口而出"。o1 / R1 / AlphaProof 让它学会"打草稿"。这是从 System 1 到 System 2 的进化。**
