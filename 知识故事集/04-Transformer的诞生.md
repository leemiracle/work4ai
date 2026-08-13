# 04 · Transformer 的诞生（2017）

> **时间**：2017，1 年
> **核心冲突**：RNN 处理长序列太慢。能不能完全不用循环？
> **嵌入概念**：Self-attention、Multi-head、Positional encoding

---

## 🎬 故事

### 2014 · Bahdanau 的天才 idea

Dzmitry Bahdanau，Montreal 大学博士生。导师 Bengio。

2014 年做机器翻译。当时主流是 **RNN encoder-decoder**：
- 一个 RNN 读源语言（如英文），把整句话压缩成一个固定向量
- 另一个 RNN 把这个向量解压成目标语言（如法文）

**问题**：长句子记不住。RNN 把 30 词压缩成 500 维向量，必然丢信息。

Bahdanau 的 idea：**不压缩成 1 个向量。让 decoder 每生成一个词时，"看" encoder 的所有隐藏状态，加权求和**。

**这就是 attention 的诞生**。论文叫 **"Neural Machine Translation by Jointly Learning to Align and Translate"**（2014）。

Attention 一开始是 RNN 的"补丁"。

### 2017 · Google Brain 的 8 人

2017 年，Google Brain 8 个研究员：
- **Ashish Vaswani**（队长，当时在 Google）
- **Noam Shazeer**（后来搞 PaLM / Gemini）
- **Niki Parmar**（后来 AI21 Labs）
- **Jakob Uszkoreit**（后来 Lila / Inceptive）
- **Llion Jones**（后来 Sakana AI）
- **Aidan Gomez**（后来 Cohere CEO）
- **Łukasz Kaiser**（后来 Google DeepMind）
- **Illia Polosukhin**（后来 NEAR Protocol）

他们在做翻译。**问题**：RNN + attention 训得慢。RNN 必须一个词一个词处理（顺序依赖），无法并行。

**Vaswani 的疯狂 idea**：**attention 这么有效，为什么还要 RNN？**

**论文标题就是宣言**：**《Attention Is All You Need》**。

### 2017 年 6 月 12 日 · 论文挂 arXiv

**Transformer** 诞生。**仅用 attention，不用循环**。

核心公式：
```
Attention(Q, K, V) = softmax(Q · K^T / √d_k) · V
```

什么意思？
- **Q（query）**：每个词问"我应该看谁？"
- **K（key）**：每个词的"标签"——别人怎么找到我
- **V（value）**：每个词的"内容"——我有什么信息

attention = **每个词用 Q 找到所有词的 K，按相似度加权取 V**。

**Transformer 一发，整个 NLP 圈震动**。3 年后，几乎所有 NLP 任务都被 Transformer 统治。

### Multi-Head Attention 的妙处

一个 attention head 只能学一种关系（比如"主谓关系"）。**Transformer 用多个 head 并行**（原论文 8 个），每个 head 学不同关系：
- Head 1：主谓关系
- Head 2：修饰关系
- Head 3：长距离依赖
- ...

最后 concat 起来，过一层线性变换。

**Multi-head = 让 transformer 同时从多视角看句子**。

### Positional Encoding 的反直觉

attention 本身**没有顺序感**——给"猫追狗"和"狗追猫"，attention 算出一样的相似度矩阵。

但语言是有顺序的！怎么办？

**Transformer 的解决方案**：**给每个位置加上一个独特的"位置向量"**。原论文用 **sinusoidal**（正弦余弦）—— 每个位置一个独特相位。

后来发展：
- **Learned PE**：让模型自己学位置向量
- **RoPE（Rotary Position Embedding）**：旋转位置编码，2021 由 Su Jianlin 提出，现在主流 LLM 都用
- **ALiBi**：attention 时直接加距离惩罚

### 2018 · BERT 和 GPT 同时登场

Transformer 一出，两个阵营同时启动：

**阵营 A：Google BERT**（2018）— **双向 encoder**。掩码语言模型。11 个 NLP 任务 SOTA。

**阵营 B：OpenAI GPT**（2018）— **decoder-only**。next token prediction。

OpenAI 选 decoder-only 是反共识的——BERT 当时效果好得多。但**时间证明 OpenAI 是对的**：decoder-only + 大数据 + scaling = GPT-3 / ChatGPT。

### 为什么 GPT 选 decoder-only？

**Aidan Gomez（Transformer 8 人之一）后来说**：decoder-only 的好处是**生成自然**。BERT 的双向 encoder 不能直接生成（你需要 mask），但 GPT 可以一个 token 一个 token 生成。

**生成是 LLM 的核心能力**——所以 decoder-only 赢了。

### Transformer 的真正胜利

Transformer 杀死的不仅是 RNN，是**整个领域的范式**：
- 2018 后 NLP 90% 任务用 Transformer
- 2020 后视觉（ViT）也用 Transformer
- 2022 后语音（Whisper）也用 Transformer
- 2024 后生物（AlphaFold 3）也用 Transformer

**Transformer 是 AI 的"统一场论"——一个架构统治所有模态**。

---

## 🧠 核心概念

- **Self-attention**：每个词"看"所有其他词，加权平均。**没有顺序依赖**。
- **Multi-head attention**：多个 attention 并行，每个学不同关系。
- **Positional encoding**：注入位置信息（attention 本身无序）。
- **Encoder vs Decoder vs Encoder-Decoder**：BERT 用 encoder（理解）；GPT 用 decoder（生成）；T5 用 encoder-decoder（翻译 / 总结）。
- **Decoder-only**：GPT/Claude/Llama/Gemini 都是 decoder-only。**LLM 的统一架构**。

## 🎨 类比

- **Self-attention** = 一个**图书馆员同时翻所有书**，根据"主题相似度"给每本打分，加权取所需信息
- **Q, K, V** = 图书馆员的"问句"（query）vs 每本书的"标题"（key）vs 每本书的"内容"（value）
- **Multi-head** = 8 个图书馆员同时工作，每人专注一类问题（语法 / 语义 / 引用 / ...）
- **Positional encoding** = 给每本书标"第 N 章"，因为图书馆员光看书名判断不了顺序
- **Decoder-only** = 一个只会"接话"的语言天才。你给前半句，他续写后半句。

## 💡 反直觉发现

1. **简单公式统治一切**：Attention 公式只有 4 个变量 + 1 个 softmax。**整个 LLM 时代建立在一个公式上**。

2. **RNN 不是被算法淘汰，是被并行淘汰**：RNN 数学上没问题。**问题是不能并行训练**——GPU 跑 RNN 必须一个词一个词，效率低。

3. **decoder-only 反共识赢了**：2018 BERT 完爆 GPT-1。**所有人都觉得双向 encoder 是未来**。OpenAI 坚持 decoder-only + scale，**4 年后（ChatGPT 2022）反超**。

4. **位置编码被严重低估**：2017 论文只有 1 段讲位置编码。**2021 RoPE 出现后，所有 LLM 都换 PE**。小细节决定大模型。

5. **8 个作者后来分散去创立 6+ AI 公司**：Cohere / AI21 / Sakana / NEAR / Lila / Inceptive。**Transformer 论文是 AI 圈最重要的人才孵化器**。

## 🛠️ 我该深挖什么

### work4ai 系列
- [`../讲透Transformer/`](../讲透Transformer/)：self-attention / multi-head / MoE / 推理优化
- [`../讲透基础模型/`](../讲透基础模型/)：attention 在 LLM 中的角色

### 必读
- **Vaswani et al. 2017 "Attention Is All You Need"**（原文，10 页，必读 5 遍）
- **Bahdanau et al. 2014**（attention 起源）
- **Su et al. 2021 "RoFormer"**（RoPE）
- **Karpathy "Let's build GPT"**（YouTube 视频，从零写 transformer）

### 实验
```python
# 1. 用 numpy 从零写 self-attention（10 行）
# 2. 用 PyTorch 实现 mini-GPT（参考 Karpathy nanoGPT）
# 3. 训练一个 char-level transformer on Shakespeare
```

---

## 🔗 下一篇

下一篇：[**05 · 从 GPT-1 到 GPT-3：大模型的崛起**（2018-2020）](05-从GPT-1到GPT-3.md)——OpenAI 怎么用 scale 路线反超所有人。

---

**版本**：v1.0（2026-08-13）
**核心隐喻**：**Attention 一统江湖。8 个人的论文，10 年的范式。简单公式杀死了所有前辈。**
