# 05 · 从 GPT-1 到 GPT-3：大模型的崛起（2018-2020）

> **时间**：2018-2020，2 年
> **核心冲突**：BERT 完爆 GPT，OpenAI 坚持 scale 路线。2 年后反超。
> **嵌入概念**：Next token prediction、Scaling Laws、涌现、In-context learning

---

## 🎬 故事

### 2018 · OpenAI 的反共识押注

2018 年，**OpenAI**（2015 由 Sam Altman / Elon Musk 等创立）。研究员 **Alec Radford** + **Ilya Sutskever**（Transformer 8 人之一，2015 加入 OpenAI）。

他们要做语言模型。**关键决定**：**用 decoder-only Transformer**（GPT 路线），不用 encoder（BERT 路线）。

**当时这是反共识**。同期 BERT（Google，2018）双向 encoder，**11 个 NLP 任务 SOTA**，所有人都觉得 encoder 是未来。

但 OpenAI 看到 BERT 看不到的：**生成**。

### GPT-1 · 2018 · 1.17 亿参数

GPT-1 = "Generative Pre-trained Transformer"。

预训练任务：**next token prediction (NTP)**——给前 N 个词，预测第 N+1 个词。

```
输入：The cat sat on the
预测：mat
```

就这么简单。**没有特殊任务，没有监督信号，就是猜下一个词**。

GPT-1 在 GLUE（NLP benchmark）上效果一般。**没人觉得这是革命**。

### 2019 · GPT-2 的 PR 大战

2019 年 2 月，OpenAI 发布 GPT-2：**15 亿参数**（13 倍于 GPT-1）。

**他们做了一个前所未有的决定**：**只发论文 + demo，不发模型**——理由"太危险"。

实际原因可能是双重的：
1. **真担心滥用**（生成 fake news / 钓鱼邮件）
2. **PR 战术**——制造话题

NYT、Guardian 全部报道。**OpenAI 一夜成名**。

2019 年 11 月，他们"心软"发了完整 GPT-2。**圈外人才发现：这玩意儿真的能写连贯文章**。

GPT-2 的关键发现：**zero-shot 能力**。给它一段 prompt，它能续写——**不需要微调**。

### 2020 · GPT-3 改变一切

2020 年 5 月，GPT-3 论文挂 arXiv：**1750 亿参数**（100 倍于 GPT-2）。

GPT-3 让人**真正震惊**的不是参数量，是**涌现**：
- **Few-shot learning**：给它 3 个翻译例子，它就会翻译。不用更新权重。
- **In-context learning**：在 prompt 里"教"它，它就学。
- **写代码**：让它写 React 组件，它写了——**没人专门训过它写代码**。
- **数学推理**：能解一些 GSM8K 题。

**这些都是涌现出来的能力**——GPT-2 没有，GPT-3 突然有。

### 2020 · Scaling Laws 的诞生

2020 年 1 月，**Jared Kaplan**（Johns Hopkins，与 Anthropic 合作者）发 **Scaling Laws for Neural Language Models**。

**核心发现**：**loss 与参数量 N、数据量 D、算力 C 是幂律关系**：

```
L(N) = (N_c / N)^α_N
L(D) = (D_c / D)^α_D
L(C) = (C_c / C)^α_C
```

**含义**：**扩大模型 = 等比例降 loss，可预测**。

这是 LLM 圈最重要的发现。**意味着 scale 是路径**——只要钱够、卡够、数据够，loss 一定能降。

### 2022 · Chinchilla 反转

2022 年 4 月，DeepMind 发 **Chinchilla**：**70B 参数 + 4 倍数据**。

**Chinchilla 70B > GPT-3 175B**。**反直觉发现**：之前所有公司都"模型大、数据少"，但 Chinchilla 证明**应该是"模型小、数据多"**。

**Compute-optimal 比例** = 20 tokens / 参数。

GPT-3 是 350B 模型配 6B 数据——**严重欠训练**。Chinchilla 让所有公司重写 scaling 策略。Llama / Qwen 都按 Chinchilla 训。

### Scaling Laws 的真正含义

GPT-3 + Scaling Laws + Chinchilla = **大模型时代的理论基础**。

**之前 AI 圈认为**：要解决一个任务，需要专门设计模型 / 数据。
**GPT-3 后**：通用大模型 + 通用数据，能力**涌现**出来。

**这是范式转变**：
- 不再"针对任务设计模型"
- 而是"训一个超大通用模型，让任务自己涌现"

### Ilya Sutskever 的远见

Ilya Sutskever（OpenAI 首席科学家，2024 离职创 SSI）后来说：

> "I always believed that if you scale up, things will work. The question was how much."

2018 年他押注 decoder-only + scale。**4 年后赢了一切**。2022 ChatGPT 是这个押注的高潮。

---

## 🧠 核心概念

- **Next Token Prediction (NTP)**：给前 N 个词，预测下一个。**所有 LLM 的训练目标**。
- **Scaling Laws**：loss = 幂律 (参数 / 数据 / 算力)。**scale 可预测**。
- **涌现（Emergent Abilities）**：规模到一定阈值，新能力突然出现。GPT-3 涌现 in-context learning。
- **In-context Learning (ICL)**：不更新权重，靠 prompt 学习。**few-shot 的本质**。
- **Chinchilla 比例**：compute-optimal = 20 tokens / 参数。**正确训法**。

## 🎨 类比

- **NTP** = 训练一个"接话天才"：你说前半句，他接后半句。学到后来，他什么都懂了。
- **Scaling Laws** = 加水加糖浆，糖水浓度按幂律上升——可以预测
- **涌现** = 水从 99°C 到 100°C 突然变气——同样的水，到阈值就状态改变
- **In-context Learning** = 实习生：你给 3 个例子，他秒懂，不用培训
- **Chinchilla 反转** = 大家都买大锅（参数），但忘了买足够米（数据）。Chinchilla 证明：**锅 70B + 米 4 倍 > 锅 175B + 米标准量**

## 💡 反直觉发现

1. **简单目标产生复杂能力**：NTP 是最简单的训练目标。**但 GPT-3 涌现出翻译 / 写代码 / 数学**。简单规则 + 大规模 = 复杂行为。

2. **BERT 路线输了**：2018 BERT 完爆 GPT-1。**所有人都觉得双向 encoder 是未来**。但生成是 LLM 的灵魂——decoder-only 赢了。

3. **Scaling Laws 之前没人敢 scale**：2018 GPT-1 时所有人都怕"训练大模型浪费钱"。Kaplan Scaling Laws 让 scale 变成"科学投资"。

4. **Chinchilla 揭露 GPT-3 严重欠训练**：**模型大不代表训得好**。Llama 2 70B 比很多 175B 模型强——因为按 Chinchilla 训。

5. **GPT-2 的 PR 是战术**："太危险"是真担心，也是 PR。**这给 OpenAI 带来 100 万美元捐款 + 全球关注**。

6. **能力涌现不可预测**：GPT-2 没人想到会"写代码"。GPT-3 没人想到会"in-context learning"。**scale 出来的东西经常 surprise**。

## 🛠️ 我该深挖什么

### work4ai 系列
- [`../讲透LLM/`](../讲透LLM/)：LLM 全栈
- [`../讲透基础模型/`](../讲透基础模型/)：NTP / 规模律 / 涌现 / 对齐（含博士级 advanced）
- [`../讲透Prompt/`](../讲透Prompt/)：ICL / CoT / 结构化输出

### 必读
- **Radford et al. 2018 "Improving Language Understanding by Generative Pre-Training"**（GPT-1）
- **Radford et al. 2019 "Language Models are Unsupervised Multitask Learners"**（GPT-2）
- **Brown et al. 2020 "Language Models are Few-Shot Learners"**（GPT-3）
- **Kaplan et al. 2020 "Scaling Laws for Neural Language Models"**
- **Hoffmann et al. 2022 "Training Compute-Optimal Large Language Models"**（Chinchilla）

### 实验
```python
# 1. 用 Karpathy nanoGPT.py 从零训一个 GPT on Shakespeare（30 分钟）
# 2. 观察：参数从 1M → 10M，loss 按幂律下降
# 3. 验证 ICL：训完后给几个例子，看模型是否秒懂新任务
```

---

## 🔗 下一篇

下一篇：[**06 · ChatGPT 与 RLHF 的诞生**（2022）](06-ChatGPT与RLHF的诞生.md)——GPT-3.5 怎么变成"听话"的 ChatGPT。

---

**版本**：v1.0（2026-08-13）
**核心隐喻**：**NTP 是接话游戏，scale 是水到渠成。OpenAI 押注 scale 4 年，赢了所有。**
