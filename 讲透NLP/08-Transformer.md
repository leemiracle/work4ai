# Ch8 — Transformer：Attention 为何革命性

> SLP3 Chapter 8 对应。本文是**导引版**——讲清楚 self-attention 的核心公式、三大架构分野、以及为什么 attention 对 NLP 是分水岭。
>
> 深度版（FlashAttention / RoPE / GQA / MLA / 训练并行 / KV Cache / 16 篇）→ [`../讲透Transformer/`](../讲透Transformer/README.md)
>
> 配套实验：[`experiments/08_attention_demo.py`](../experiments/08_attention_demo.py)（纯 NumPy，从零实现 self-attention + 两个反直觉发现）

---

## 全景：一句话 + 一张图

**Transformer = Self-Attention（全局视野 + 并行计算）+ 残差/LayerNorm（让深堆叠可训练）+ FFN（逐位置非线性变换）。**

其中，self-attention 是灵魂。

```
                         Self-Attention
                    ┌──────────────────────┐
  词嵌入序列 ──────►│  每个词同时看到       │──────► 上下文融合后的表示
  (N, d_model)      │  所有其他词           │       (N, d_model)
                    └──────────────────────┘
                              │
                    ┌─────────┴──────────┐
                    ▼                    ▼
              + 残差 + LayerNorm    × L 层堆叠
                    ▼
              FFN（两层 MLP + 激活）
                    ▼
              + 残差 + LayerNorm
```

本章只讲 5 件事，每件都做到直觉→数学→代码三层讲透：

1. **Self-Attention**：核心公式 $\text{softmax}(QK^T/\sqrt{d_k})V$
2. **$\sqrt{d_k}$ 缩放**：为什么不能省（实验铁证）
3. **Multi-Head**：多头不是越多越好（秩瓶颈）
4. **位置编码**：attention 本身不知道顺序
5. **三大架构**：BERT vs GPT vs T5，以及为什么 GPT 赢了

---

## 1. Self-Attention：整个架构的灵魂

### 直觉 — 信息检索的比喻

想象句子 *"The cat sat on the mat because **it** was tired."* 里的 **"it"** 指代谁？

Self-attention 是一个**信息检索系统**。每个词同时扮演三个角色：

| 角色 | 含义 | 比喻 |
|------|------|------|
| **Query (Q)** | "我在找什么" | "我是 *it*，我在找一个名词来确认指代" |
| **Key (K)** | "我有什么可被匹配" | "我是 *cat*，我的标签是'名词·动物·单数'" |
| **Value (V)** | "匹配后我给你什么" | "如果你关注我，我把 *cat* 的完整语义给你" |

每个词用自己的 Q 去和**所有词**的 K 做匹配（点积 = 相似度），匹配度高的词就多拿它的 V。最终每个词变成"它最关心的那些词的加权融合"。

> **NLP 顿悟**：这就是"指代消解"（coreference resolution）的天然机制。传统 NLP 用专门的规则/CRF pipeline 做指代消解；attention 把它变成了一个**可微的矩阵乘法**，融进了表示学习里。

### 数学 — 就 4 步矩阵乘法

给定输入序列的嵌入矩阵 $X \in \mathbb{R}^{N \times d_{\text{model}}}$（$N$ 个 token，每个 $d_{\text{model}}$ 维）：

**Step 1：投影出 Q, K, V**

$$Q = X W^Q, \quad K = X W^K, \quad V = X W^V$$

其中 $W^Q, W^K \in \mathbb{R}^{d_{\text{model}} \times d_k}$，$W^V \in \mathbb{R}^{d_{\text{model}} \times d_v}$ 是可学习参数。

**Step 2：计算相似度**

$$S = Q K^\top \in \mathbb{R}^{N \times N}$$

$S_{ij}$ = 第 $i$ 个 token 的 query 和第 $j$ 个 token 的 key 的点积 = 它们有多"相关"。

**Step 3：缩放 + softmax → 注意力权重**

$$A = \text{softmax}\!\left(\frac{S}{\sqrt{d_k}}\right) = \text{softmax}\!\left(\frac{QK^\top}{\sqrt{d_k}}\right)$$

$A_{ij}$ = 第 $i$ 个 token 分配给第 $j$ 个 token 的注意力比例（每行之和 = 1）。

**Step 4：加权聚合 Value**

$$\text{Output} = A V \in \mathbb{R}^{N \times d_v}$$

合起来就是那个著名公式：

$$\boxed{\text{Attention}(Q, K, V) = \text{softmax}\!\left(\frac{QK^\top}{\sqrt{d_k}}\right) V}$$

> **并行性顿悟**：全程只有 3 次矩阵乘法 + 1 次 softmax。没有 `for` 循环，没有递归。GPU 可以对所有 $N$ 个位置**同时**计算——这就是 Transformer 能用 GPU 大规模并行的根本原因。

### 代码 — 纯 NumPy 四行

```python
Q, K, V = X @ W_Q, X @ W_K, X @ W_V     # 投影
scores = Q @ K.T                         # (N, N) 两两相似度
weights = softmax(scores / sqrt(d_k))    # 缩放 + 归一化
output  = weights @ V                    # (N, d_v) 加权融合
```

实验 `08_attention_demo.py` Part 1 逐行验证了这四步。

---

## 2. 为什么必须除以 $\sqrt{d_k}$？

### 反直觉发现（实验铁证）

"注意力越集中越好"——直觉上不缩放似乎能让分数更鲜明。**错。**

实验测量了 $d_k = 64$ 时 query 0 对 6 个 key 的注意力分布：

| 模式 | 最大权重 | 含义 |
|------|---------|------|
| **不缩放** | **99.0%** | 一个 token 独占全部注意力 → softmax 几乎变成 one-hot |
| **÷ √64 = 8** | **38.3%** | 注意力分散到多个 token → softmax 处于"活跃区" |

不缩放时的柱状图：

```
key 3: ███████████████████████████████████   99.0%   ← 独占!
其他:  (几乎不可见)                           1.0%
```

### 数学解释

若 $Q, K$ 的各分量 $\sim \mathcal{N}(0,1)$（训练初期近似如此），则点积 $Q \cdot K = \sum_{i=1}^{d_k} Q_i K_i$ 的期望为 0、方差为 $d_k$。

| $d_k$ | $\text{std}(QK^\top)$ | 不缩放时最大权重 | ÷ √d 后最大权重 |
|-------|----------------------|----------------|----------------|
| 64 | $\approx 8$ | ~79% | ~42% |
| 256 | $\approx 16$ | ~88% | ~37% |
| 1024 | $\approx 32$ | **~99.6%** | ~46% |

**为什么是灾难？** softmax 在近 one-hot 区域梯度趋于 0（参考[讲透信息论]的交叉熵课：自信地对/错时梯度都小）。训练初期 $W^Q, W^K$ 接近随机，scores 本来就大，再不缩放 → 梯度消失 → 模型根本学不动。

除以 $\sqrt{d_k}$ 把 scores 的方差稳定在 $\approx 1$，让 softmax 处于梯度活跃的区间。**这就是 Vaswani et al. 2017 论文中 $\sqrt{d_k}$ 的唯一原因。**

> **连接你学过的知识**：这里的"softmax 温度"概念，和[讲透信息论/07-Transformer的信息流]里"1/√d 是 softmax 温度"完全一致——温度低→分布尖锐→信息集中→梯度死。

---

## 3. Multi-Head Attention：多视角还是分组？

### 直觉

一个 attention 头只能学一种"关系"。但语言里关系是多维的：

- 一个头学"语法依存"（主语→谓语）
- 一个头学"指代关系"（it → cat）
- 一个头学"相邻位置"（big → red → dog 的修饰链）
- 一个头学"长距离对齐"（翻译里的源-目标对齐）

### 数学

把 $d_{\text{model}}$ 维拆成 $h$ 个头，每头 $d_k = d_{\text{model}} / h$ 维，各自独立做 attention，最后拼接：

$$\text{MultiHead}(Q,K,V) = \text{Concat}(\text{head}_1, \ldots, \text{head}_h)\, W^O$$

$$\text{head}_i = \text{Attention}(Q W_i^Q,\; K W_i^K,\; V W_i^V)$$

### 反直觉发现：head_dim 太小 = 秩瓶颈

"头越多 → 视角越多 → 越好？"**不一定。**

**数学铁证**：每个头的分数矩阵 $S_h = Q_h K_h^\top$ 的秩满足

$$\text{rank}(S_h) \leq \text{head\_dim}$$

这意味着每个头最多能表达 head\_dim 种**独立的 token 关系模式**。实验用有效秩（effective rank = exp(奇异值熵)，Roy & Vetterli 2007）测量：

| head\_dim | 理论秩上限 | 实测有效秩 | 诊断 |
|-----------|-----------|-----------|------|
| 2 | 2 | 1.97 | ⚠ 只能表达 ~2 种关系模式 |
| 8 | 8 | 7.41 | 中等 |
| 64 | 16 | 12.61 | ✓ 接近 N=16 上限 |

固定 $d_{\text{model}}=64$ 改变头数：

| 头数 | head\_dim | 每头有效秩 | 总有效秩 | 解读 |
|------|-----------|-----------|---------|------|
| 1 | 64 | 12.3 | 12.3 | 1 个强头 |
| 8 | 8 | 6.7 | 53.8 | 8 个中等头 |
| 32 | 2 | **1.9** | 62.1 | 32 个残废头 |

**三个结论**：
1. 总有效秩随头数增加趋近 $d_{\text{model}}$（12→62），但**每头骤降**（12→2）。
2. 多头是"重新分配容量"，不是"增加容量"。
3. head\_dim=2 时，32 个头每个只能看 ~2 个"方向"——这不是"32 个不同视角"，是"32 个浅薄视角"。（随机投影的有效秩是**理论上限**；真实训练中退化更严重，因为小头学不出区分度，容易坍缩成相同模式。）

> **经验法则**：head\_dim ≥ 32（最好 ≥ 64）。BERT-base（768/12头=64）、GPT-2（768/12头=64）、LLaMA-7B（4096/32头=128）全部满足。

---

## 4. 位置编码：补回顺序信息

### 问题

Self-attention 是个"词袋模型"——它让每个词看到所有词，但**完全不在乎顺序**。"狗咬人"和"人咬狗"在 attention 眼里一样！

### 解法

给每个位置加一个**位置编码**向量：

$$\text{input}_i = \text{token\_emb}(x_i) + \text{pos\_enc}(i)$$

原论文用 sin/cos 固定编码：

$$\text{pos\_enc}(i, 2k) = \sin\!\left(\frac{i}{10000^{2k/d}}\right), \quad \text{pos\_enc}(i, 2k{+}1) = \cos\!\left(\frac{i}{10000^{2k/d}}\right)$$

不同维度用不同频率的正弦/余弦波，让模型能区分"第 1 个词"和"第 3 个词"。

### 演化路线

| 时代 | 方法 | 代表 |
|------|------|------|
| 2017 | sin/cos 固定编码 | 原始 Transformer |
| 2018-2020 | **可学习位置编码** | BERT, GPT-2 |
| 2021- | **RoPE**（旋转位置编码） | LLaMA, Qwen, DeepSeek |
| 2025- | iRoPE / 各种 RoPE 变体 | LLaMA 4 |

> 深入 RoPE → [`../讲透Transformer/02-位置编码演进.md`](../讲透Transformer/02-位置编码演进.md)

---

## 5. 三大架构：BERT vs GPT vs T5

Transformer 有三种"组装方式"，取决于用哪种 attention mask：

### 对照表

| | **Encoder-Only** | **Decoder-Only** | **Encoder-Decoder** |
|---|---|---|---|
| **代表** | BERT | **GPT / LLaMA** | T5 / 原始 Transformer |
| **Attention** | 全连接（双向） | **Causal（单向）** | 自注意 + **交叉注意** |
| **能看到** | 所有 token | 只能看前面的 token | Encoder 看全部；Decoder 看 Encoder + 自己前面的 |
| **擅长** | 理解（分类、填空、NER） | **生成**（对话、写作、代码） | 翻译、摘要（seq2seq） |
| **训练目标** | Masked LM（遮住 15% 猜） | Next-token prediction | Span corruption（遮住片段重建） |
| **2026 现状** | 被 LLM 收编（分类用 LLM 也行） | **绝对主流**（所有大模型） | 翻译仍有用，但 LLM 也能翻译 |

### Causal Mask：Decoder 的关键

Decoder 生成时，每个词**只能看前面的词**（不能偷看未来）。实现方法：把注意力矩阵的**上三角置为 $-\infty$**，softmax 后这些位置权重 = 0。

```
Causal mask (4×4 示例):
        key→  k0   k1   k2   k3
query↓
  q0         [w]   -∞   -∞   -∞     ← q0 只看 k0
  q1         [w]  [w]   -∞   -∞     ← q1 看 k0, k1
  q2         [w]  [w]  [w]   -∞
  q3         [w]  [w]  [w]  [w]     ← q3 看全部
```

### 为什么 GPT（Decoder-Only）赢了？

1. **生成是通用任务**：next-token prediction 可以建模任何序列（文本、代码、数学、甚至图像 token），而 BERT 的 MLM 只能填空。
2. **Causal mask 让训练高效**：一条序列里每个位置都是一个训练样本（预测下一个），数据效率高。
3. **Scale 友好**：decoder-only 架构在 scale up（更多参数/数据/算力）时收益最稳定，涌现能力最明显。

> 详细分析 → [`../讲透Transformer/06-架构演进与MoE.md`](../讲透Transformer/06-架构演进与MoE.md)

---

## 6. NLP 视角：Attention 为何是分水岭

### RNN 的根本困境：必须按顺序

RNN/LSTM 处理一个 $N$ 词的句子：

```
RNN:  h₁ = f(x₁, h₀) → h₂ = f(x₂, h₁) → h₃ = f(x₃, h₂) → ... → h_N
```

- **必须等 $h_{i-1}$ 算完才能算 $h_i$** → 无法并行，GPU 利用率极低
- **长距离衰减**：$h_1$ 的信息要经过 $N-1$ 次非线性变换才到达 $h_N$，信息严重衰减（即使 LSTM 的门控也只缓解不根治）
- 第 1 个词和第 100 个词的"距离" = 99 步

### Attention：一步看全部

```
Attention:  output = softmax(QK^T / √d) V
```

- **所有位置同时计算** → 完全并行，GPU 满载
- **任意两个词的距离 = 1**（一次矩阵乘法）：第 1 个词和第 100 个词的"距离" = 常数 O(1)
- **全局视野**：每个词直接看到所有词，不需要"传递"

### 历史脉络

| 时期 | 主流方法 | 瓶颈 |
|------|---------|------|
| ~2013 | RNN/LSTM | 按顺序处理、长距离衰减、无法并行 |
| 2014-2017 | RNN + Attention（Bahdanau, Luong） | Attention 只做"对齐"，RNN 仍是骨架 |
| **2017** | **Transformer（纯 attention）** | "Attention Is All You Need"——扔掉 RNN |
| 2018 | BERT（encoder-only） | 刷爆所有 NLP 理解任务 |
| 2018- | GPT 系列（decoder-only） | 生成能力随 scale 涌现 |
| 2020+ | **LLM 时代** | 所有 NLP 任务被 next-token prediction 收编 |

> **SLP3 的价值正在这里**：Ch 13（RNN/LSTM）→ Ch 8（Transformer）的顺序让你亲历这场革命——先理解 attention 之前 NLP 的困境，才能真正理解 attention 为何是"分水岭"而非"渐进改进"。

---

## 7. 计算复杂度：$O(N^2)$ 是代价

| 层 | 复杂度 | 瓶颈 |
|----|--------|------|
| Self-Attention | $O(N^2 \cdot d)$ | **序列长度平方** |
| FFN | $O(N \cdot d^2)$ | 与序列长度线性 |

$O(N^2)$ 意味着序列翻倍，注意力计算量 ×4。这就是为什么长上下文（100K+ token）极贵，也是 FlashAttention、稀疏注意力、线性注意力等研究的动机。

> 深入 → [`../讲透Transformer/09-推理优化.md`](../讲透Transformer/09-推理优化.md) · [`../讲透Transformer/15-长上下文.md`](../讲透Transformer/15-长上下文.md)

---

## 8. 一个 Transformer Block 的完整结构

把前面学的积木拼起来（一个标准 block）：

```
x ──┬──> LayerNorm ──> Multi-Head Self-Attention ──┐
    │                                                │
    └───────────────(残差)───────────────────────(+)──┬──> LayerNorm ──> FFN ──┐
                                                       │                      │
                                                       └────────(残差)──────(+)──> out
```

- **残差连接**（ResNet）：$x + \text{SubLayer}(x)$，让深网络梯度能回流
- **LayerNorm**：归一化每个位置的特征维，稳定训练（现代模型用 RMSNorm）
- **FFN**：两层 MLP + 激活函数（GELU / SwiGLU）
- 堆叠 $L$ 个这样的 block → 完整 Transformer

> FFN 里的激活函数（GELU vs ReLU vs SwiGLU）→ [`../讲透激活函数/`](../讲透激活函数/README.md)
> 残差 + LayerNorm 深入 → [`../讲透Transformer/05-归一化与残差.md`](../讲透Transformer/05-归一化与残差.md)

---

## 局限与争议

1. **$O(N^2)$ 复杂度**：序列长度是硬约束。虽然 FlashAttention 在工程上缓解了显存问题，但计算量仍是平方级。线性注意力（Linformer/Performers/RWKV/SSM）是活跃研究方向，但目前还无法在大规模上全面替代标准 attention。

2. **位置编码仍是开放问题**：RoPE 在长上下文上的外推能力有限（需要 NTK-aware / YaRN 等 scaling 技巧）。对于"第 1 个 token 和第 100 万个 token 的关系"这类超长距离依赖，现有方法都不够好。

3. **Multi-head 的冗余**：研究表明训练后很多 attention head 是冗余的（可以剪枝而不掉点），说明"多头"在实践中并未完全发挥理论上的"多视角"作用。GQA/MQA 等变体就是在 head 间共享 KV 来减少冗余。

4. **Attention ≠ 理解**：attention 权重高不等于模型"真正理解"了那个 token（attention 可解释性争议）。Anthropic 的 mechanistic interpretability 研究表明，注意力模式比直觉复杂得多。

5. **RNN 未死**：在端侧/低延迟场景（流式 ASR、实时翻译），RNN/SSM（Mamba 等）因为 $O(N)$ 复杂度和恒定内存仍有优势。Attention 不是万能的。

---

## 📌 下一步

1. **跑实验**：`python3 experiments/08_attention_demo.py`——看 √d 缩放如何从 99% 饱和拯救到 38% 分散，看 head\_dim=2 的有效秩只有 1.9。

2. **深入**：本文是导引版。要真正搞懂 Transformer 的每个组件，去 [`../讲透Transformer/`](../讲透Transformer/README.md)：
   - [01-Self-Attention深度](../讲透Transformer/01-Self-Attention深度.md)：KV Cache + FlashAttention 原理
   - [02-位置编码演进](../讲透Transformer/02-位置编码演进.md)：sin/cos → RoPE → iRoPE
   - [03-注意力变体](../讲透Transformer/03-注意力变体.md)：MHA → MQA → GQA → MLA
   - [06-架构演进与MoE](../讲透Transformer/06-架构演进与MoE.md)：四时代 + LLaMA 配方 + MoE 革命

3. **横向连接**：
   - Ch 10（BERT）：encoder-only 的 masked language model
   - Ch 13（RNN/LSTM）：attention 之前如何处理序列——理解"为什么需要 attention"
   - [`../讲透基础模型/`](../讲透基础模型/README.md)：mini-GPT 从零训练实验

---

## ✍️ 练习

1. **手推公式**：写出 $d_k=4$, $N=3$ 时的 $QK^\top$ 矩阵（手算或代码），验证 $\text{softmax}$ 每行之和确实为 1。

2. **去掉 √d**：在实验脚本中把 `scale=True` 改成 `False`，观察 $d_k=1024$ 时最大注意力权重是多少。再想想：如果训练初期梯度确实消失了，模型最终能自己学会"缩小 $W^Q, W^K$"来补偿吗？（提示：能，但学习速度极慢——所以缩放是从一开始就帮模型省事。）

3. **head\_dim 实验**：在实验脚本 Part 3b 中把 `d_model` 改成 32，再跑一遍。观察：总有效秩的上限变成了多少？per-head 有效秩在 head\_dim=4 时是多少？

4. **Causal mask**：在 `attention_weights` 函数中加上 causal mask（把上三角 scores 设为 $-\infty$），验证 softmax 后上三角权重是否精确为 0。

5. **思考题**：如果 attention 是"全局视野+并行"，为什么原始 Transformer 论文做机器翻译时用的是 encoder-decoder 而不是 decoder-only？（提示：2017 年的算力、训练数据量、以及翻译任务的 seq2seq 本质。）

---

## 参考文献

- Vaswani et al. 2017, *Attention Is All You Need* — Transformer 开山之作
- Devlin et al. 2018, *BERT: Pre-training of Deep Bidirectional Transformers* — encoder-only
- Radford et al. 2018-2020, *GPT / GPT-2 / GPT-3* — decoder-only 的 scale 之路
- Raffel et al. 2020, *Exploring the Limits of Transfer Learning with T5* — encoder-decoder
- Roy & Vetterli 2007, *The Effective Rank: A Measure of Effective Dimensionality* — 有效秩定义
- SLP3 Chapter 8 — 本章的理论基础
- [`../讲透Transformer/`](../讲透Transformer/README.md) — 深度版 16 篇
