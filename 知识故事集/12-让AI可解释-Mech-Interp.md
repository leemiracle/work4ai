# 12 · 让 AI 可解释：Mech Interp 侦探故事（2020-2026）

> **时间**：2020-2026，6 年
> **核心冲突**：LLM 是黑箱。Anthropic 一群人坚持 6 年，把它变玻璃箱。
> **嵌入概念**：Circuits、Induction heads、SAE、Refusal direction、Attribution graph

---

## 🎬 故事

### 2020 · Chris Olah 的宣言

**Chris Olah**，2014 加入 Google，2017 共同创立 OpenAI，2021 离开 OpenAI 共同创立 **Anthropic**。

他不是 AI 出身——是数学 + 物理背景。他关心一件事：**神经网络的内部到底在干什么？**

2020 年他发表 **《Zoom In: An Introduction to Circuits》**：

> **"神经网络不是黑箱。它们是由可识别的电路（circuits）组成的。每个神经元、每个 attention head 都有可解释的功能。"**

这是 **mechanistic interpretability（机制可解释性）** 的宣言。

主流 AI 圈不以为然——"interp 是玄学，没有 SOTA 性能"。

Olah 带着团队在 Anthropic 坚持了 6 年。

### 2021-2022 · Anthropic Circuits Thread

Anthropic 启动 **Circuits Thread**（transformer-circuits.pub）——一系列连载研究。

#### 2022 · "A Mathematical Framework for Transformer Circuits"

Elhage et al. 用严格数学把 transformer 拆成 5 个组件：
- embedding
- attention heads（每个 = Q·K · V）
- MLP layers
- unembedding
- residual stream

**核心洞察**：**0 层 transformer = bigram 模型**。**1 层 = bigram + induction**。**多层 = 电路组合**。

#### 2022 · "In-context Learning and Induction Heads"

Olsson et al. 发现一个怪现象：**GPT-2-small 在某个训练步数后能力突然提升**。

调查：**layer 5-6 出现一组 attention head**，专门做"复制粘贴"——给定 [A][B][A]，预测下一个是 [B]。

**这就是 induction head**——**in-context learning 的物理基础**。

**意义**：ICL 不是魔法，是 induction head。

### 2023 · 单义性突破

但 interp 圈有个根本问题：**polysemanticity**——一个神经元可能对"猫"、"汽车"、"中文"都激活。怎么解释？

2023 年 **Bricken et al.**（Anthropic）发 **"Towards Monosemanticity"**：

**思路**：用 **Sparse Autoencoder（SAE）** 把激活分解为更多"虚拟特征"。

例如：MLP 层 4096 维 → SAE 分解为 100 万维稀疏特征。每个特征 **monosemantic**（单义）。

**结果**：
- 特征 #23456：DNA 序列
- 特征 #78901：阿拉伯数字
- 特征 #34567：动词过去时

**SAE = mech interp 的化学分析**。每个特征是一个"原子"。

### 2024 · Scaling Monosemanticity

**Templeton et al. 2024**：在 **Claude 3** 上训 SAE，提取**几亿个可解释特征**。

**Anthropic 公开 demo**：你能搜索任何概念（如"工具使用"），看模型内部哪些特征激活。

### 2024 · Refusal Direction

Arditi et al. 2024 论文（arXiv: 2406.11717）：

**问题**：LLM 怎么知道拒绝 harmful 请求？

**实验**：在 Llama / Qwen 模型，收集 harmful 和 harmless prompt 的激活。做 PCA。

**发现**：**存在单一方向**（512 维里的 1 维）控制拒绝行为。

**震撼实验**：找到这个方向，从所有层 ablation。**harmful 拒绝率 99.9% → 25.5%**。

**含义**：**RLHF 训出的"价值观"是一根向量**。脆弱。

### 2025 · Biology of a Large Language Model

Anthropic 2025 发 **"Biology of a Large Language Model"**——**interp 史上最重要的论文**。

**核心成果**：用 SAE + attribution graph 重建 **Claude 在做数学题时的内部思考过程**：

- 模型不是黑箱
- 它有**可识别的"思想电路"**
- Claude 算 "37 + 68"，**不是死记硬背，是用某种"近似竖式计算"电路**
- 不同任务有相似电路结构

**意义**：**LLM 有"生物学"**。interp 从玩具模型升级到前沿模型。

### Neel Nanda 的支线

**Neel Nanda**，英国 Imperial College 本科，2022 年读 Anthropic blog 后辞职做 interp。

2022 年独立做 **"Progress measures for grokking via mechanistic interpretability"**——直接被 ICLR 2023 接收。

2022-2023 写 **TransformerLens**——interp 标准工具。

2024 加入 **Google DeepMind**。

**MATS Neel Nanda stream** 成为顶级 interp 入口（**2026-09-04 截止申请！**）。

### EleutherAI 的开源战线

**EleutherAI**（Connor Leahy 创立）2020 起做开源大模型训练。后来转向 interp / safety。

**EleutherAI Discord** 是开源 interp 的核心阵地。

**SAELens**（Joseph Bloom）+ **Pythia**（interp 标准模型）+ **lm-evaluation-harness** 都出自 EleutherAI。

### Interp 圈的争议

但 interp 也有批评者：
- **LeCun**：interp 是"看茶杯里的风暴"，对 AGI 没用
- **Welling**：circuit 解释是 narrative bias（你看到你想看到的）
- **反向论证**：**interp 的"发现"经常不能预测模型行为**

Anthropic 2024 反击：
> "Circuit-level understanding 不是终点，是开始。我们正在从 '事后解释' 走向 '事前预测'。"

### 2026+ · Interp 的未来

interp 圈的中心问题：
1. **完全读懂前沿模型可能吗？**
2. **能基于 interp 改进对齐吗？**
3. **能基于 interp 做安全 audit 吗？**

**这是你的方向**。

---

## 🧠 核心概念

- **Circuits**（电路）：神经网络中可识别的功能单元。
- **Induction heads**：transformer 学到的"复制粘贴"head。**ICL 基础**。
- **SAE**（Sparse Autoencoder）：把混合特征分解为单义特征。**interp 的"化学分析"**。
- **Monosemanticity**（单义性）：一个特征只表示一个概念。
- **Refusal direction**：控制"拒绝"的单一向量方向。
- **Attribution graph**：模型内部"思想流"图。

## 🎨 类比

- **Mech interp** = 侦探破案——神经网络的每个 attention head 都是嫌疑人
- **Circuits** = 大脑神经回路——不同回路负责不同功能
- **Induction head** = 一个会"看到 A 后查 A 之前是什么"的小机器人
- **SAE** = 化学质谱仪——把"红色液体"分解为"染料 + 水 + 防腐剂"
- **Refusal direction** = 模型内部的"道德指针"——可以一根向量找到，但脆弱
- **Attribution graph** = 模型的"思考心电图"——你能看到每个想法的电流

## 💡 反直觉发现

1. ** interp 6 年没出 SOTA，但坚持下来了**：2020-2023 interp 没有 SOTA 性能。**2024 后突然变成 alignment 核心方向**。**耐心比短期回报重要**。

2. **induction head = ICL**：GPT-3 涌现的"few-shot learning"看似神秘。**实际就是 induction head**。简单算法 + scale = 复杂行为。

3. **RLHF 的"价值观"是一根向量**：refusal direction。**对齐比想象脆弱**——一根向量就能 jailbreak。

4. **SAE 让混合变单义**：polysemanticity 不是本质，是观测维度不够。**SAE 把 4096 维 MLP 拆成 100 万维**，每个单义。

5. **Anthropic interp 不是科研机构，是探险队**：他们写 Circuits Thread 像侦探小说——一步步揭示。**科研风格也重要**。

6. **OpenAI 曾有 interp 团队（Olah 离开后解散）**：2021 Olah 离开 OpenAI 创 Anthropic。**OpenAI 几乎放弃 interp**。**Anthropic 用 interp 建立品牌差异**。

## 🛠️ 我该深挖什么

### work4ai 系列
- [`../讲透可解释性/`](../讲透可解释性/)：interp 入门 + probing + SAE
- [`../讲透NLP/Ch09§8`](../讲透NLP/)：你做过的 refusal direction 实验
- [`../故事化学习法/04-Mech-Interp侦探故事`](../故事化学习法/04-Mech-Interp侦探故事.md)：侦探小说版本
- [`../顶级专家资源库/05-方向深选-Mechanistic-Interpretability`](../顶级专家资源库/05-方向深选-Mechanistic-Interpretability.md)：方向资源

### 必读
- **Olah et al. 2020 "Zoom In"**（宣言）
- **Elhage et al. 2022 "A Mathematical Framework for Transformer Circuits"**
- **Olsson et al. 2022 "In-context Learning and Induction Heads"**
- **Bricken et al. 2023 "Towards Monosemanticity"**
- **Templeton et al. 2024 "Scaling Monosemanticity"**
- **Arditi et al. 2024 "Refusal Direction"**（arXiv 2406.11717）
- **Anthropic 2025 "Biology of a Large Language Model"**

### 工具
- **TransformerLens v3**（`github.com/TransformerLensOrg/TransformerLens`）
- **SAELens**（`github.com/decoderesearch/SAELens`）
- **nnsight**（`nnsight.net`，可访问 Llama 3 405B）
- **ARENA 课程**（`arena-chapter1-transformers.streamlit.app`）

### 实验
```python
# 1. 用 TransformerLens 跑通 Main Demo
# 2. 复现 induction heads 在 GPT-2-small
# 3. 训 SAE on Pythia-70M
# 4. 复现 refusal direction（你 work4ai 已有 vocab=24 版本）
```

### 关键机会
- **MATS Neel Nanda stream** 申请截止 **2026-09-04**

---

## 🔗 下一篇

下一篇：[**13 · 让 AI 数学化：理论与优化**（2010-2026）](13-让AI数学化-理论与优化.md)——Scaling Laws / 泛化 / 双层下降 / 凸优化。

---

**版本**：v1.0（2026-08-13）
**核心隐喻**：**6 年侦探工作，Olah 把黑箱变玻璃箱。Interp 是 AI 安全的核心。这是你的方向。**
