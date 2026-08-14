# 讲透 Transformer

> 配套实验: `experiments/transformer_overview.py` (3 个子实验, 已实跑验证)
> 产物图: `attention_heatmap.png` (注意力热力图) · `mini_gpt_training.png` (mini-GPT 训练曲线)
> 前置: 本文会用到你已学的三件套 — 激活函数 / 损失函数 / 优化器

---

## 全景图: Transformer 在解决什么问题?

**Transformer (Vaswani et al. 2017, *Attention Is All You Need*)** 是 GPT/BERT/所有现代大模型的骨架。它的两个历史性突破:

1. **全局视野**: 每个位置同时看到所有其他位置 (RNN 只能逐步传递, 远处信息会衰减)
2. **并行计算**: 所有位置同时处理 (RNN 必须按顺序, 无法用 GPU 并行)

**一句话**: Transformer = Self-Attention (全局视野 + 并行) + 残差/LayerNorm (让深堆叠可训练)。

---

## 灵魂洞察: 三件套如何组装成 Transformer

你前面学的三件套, 在 Transformer 里各司其职:

| 你学过的 | 在 Transformer 里的角色 |
|---------|------------------------|
| **激活函数** | FFN 里的 GELU (为什么不是 ReLU? 见下文) |
| **损失函数** | next-token 预测的 CrossEntropy |
| **优化器** | Adam (现代标配) + warmup 调度 |
| **新增: Self-Attention** | Transformer 的灵魂, 让每个 token 互相"看到" |

---

## 第一核心: Self-Attention (整个架构的灵魂)

### 直觉 — 搜索系统的比喻

Self-Attention 就像一个**信息检索系统**。对句子里的每个词, 我们问三个问题:

- **Query (Q, 我在找什么)**: "我是'it', 我需要找一个名词来明确我指代谁"
- **Key (K, 我有什么可被找)**: "我是'cat', 我的标签是'名词·动物'"
- **Value (V, 找到我给你什么)**: "如果你关注我, 我把'cat'的完整含义给你"

每个词用 Q 去和所有词的 K 做匹配 (点积 = 相似度), 匹配度高的词, 就多拿它的 V。最终每个词都变成"它最关心的那些词的加权融合"。

### 数学 — 就 4 步矩阵乘法

$$\text{Attention}(Q, K, V) = \text{softmax}\!\left(\frac{Q K^T}{\sqrt{d_k}}\right) V$$

**实验脚本逐行验证** (纯 numpy, 已实跑):
```python
Q = X @ W_Q          # (seq, d) 每个词投影成"查询"
K = X @ W_K          #         每个词投影成"被查标签"
V = X @ W_V          #         每个词投影成"提供的内容"
scores = Q @ K.T     # (seq, seq) 两两相似度矩阵
weights = softmax(scores / sqrt(d_k))   # 归一化成注意力权重
output = weights @ V # (seq, d)  加权融合 = Self-Attention 输出
```

> **顿悟**: Self-Attention 本质就是"3 次矩阵乘法 + 1 次 softmax"。没有循环, 没有递归, 所以**完全并行**。

### 为什么除以 $\sqrt{d_k}$? (连接你学的损失函数课)

**实测** (实验1): 当 $d_k = 512$ 时:
- 裸 $QK^T$ 的标准差 = **21.2** → softmax 输出近乎 one-hot (一个词独占全部注意力)
- 除以 $\sqrt{512} = 22.6$ 后, 标准差 = **0.9** → softmax 平滑, 多个词都能分配注意力

为什么这是灾难? softmax 在近 one-hot 时, **梯度趋于 0** (你学过的交叉熵课: 自信地错才重罚, 自信地对时梯度也小)。结果: 训练初期梯度消失, 模型学不动。除以 $\sqrt{d_k}$ 把分数压回合理范围, 让梯度正常流动。

---

## 第二核心: Multi-Head Attention (多视角)

### 直觉

一个 attention 头只能学一种"关系"。但语言里关系是多维的:
- 一个头学"语法关系" (主语-谓语)
- 一个头学"指代关系" (it → cat)
- 一个头学"相邻关系"
- ...

### 数学

把 $d_{model}$ 维拆成 $h$ 个头, 每头 $d_k = d_{model}/h$ 维, 各自独立做 attention, 最后拼接:
$$\text{MultiHead}(Q,K,V) = \text{Concat}(\text{head}_1, \ldots, \text{head}_h) W^O$$

> **实验脚本里的实现**: `(B,T,C)` → `view(B,T,h,C/h).transpose` → 每头独立 SDPA → 拼回。这就是多头。

---

## 第三核心: Positional Encoding (补回顺序信息)

### 问题

Self-Attention 是个"词袋模型"——它让每个词看到所有词, 但**完全不在乎词的顺序**。"狗咬人"和"人咬狗"在 attention 眼里一样! 这显然不行。

### 解法

给每个位置加一个**位置向量** $\text{pos\_emb}$, 让模型能区分"第 1 个词"和"第 3 个词":
$$\text{input} = \text{token\_emb}(x) + \text{pos\_emb}(\text{position})$$

**原论文用 sin/cos 公式** (固定), **现代 GPT 用可学习参数** (实验脚本里就是 `nn.Parameter`)。

---

## 完整架构: 把积木拼起来

### 一个 Transformer Block

```
x ──┬──> LayerNorm ──> Causal Self-Attention ──┐
    │                                           │
    └───────────────(残差)──────────────────>(+)──┬──> LayerNorm ──> FFN ──┐
                                                  │                         │
                                                  └─────────(残差)───────>(+)──> out
```

- **残差连接**: `x + Sublayer(x)`, 让深网络梯度能回流 (ResNet 的思想)
- **LayerNorm**: 归一化每个位置的特征, 稳定训练
- **FFN (前馈网络)**: 两层 MLP, 中间是**你学的激活函数**!

### FFN 里为什么用 GELU 不用 ReLU?

| 激活 | 在 Transformer 里的表现 |
|------|----------------------|
| ReLU | 原论文用的, 但 0 点不可导, 死 ReLU 问题 |
| **GELU** | BERT/GPT 标配。处处可导, 概率性门控, 训练更稳 |
| **SwiGLU** | LLaMA 等新模型用, 把 FFN 的第一层激活换成 gated, 效果更好 |

### 三种架构变体

| 架构 | Attention 类型 | 代表 | 任务 |
|------|--------------|------|------|
| **Encoder-Only** | 全连接 (双向) | BERT | 理解 (分类/填空) |
| **Decoder-Only** | Causal (单向) | **GPT/LLaMA** | 生成 |
| **Encoder-Decoder** | 交叉注意力 | T5/原始 Transformer | 翻译/seq2seq |

> **现代大模型 (GPT/LLaMA) 几乎全是 Decoder-Only**。原因: 生成任务通用性最强, 且 causal mask 让训练能 scale。

### Causal Mask (Decoder 的关键)

Decoder 生成时, 每个词**只能看前面的词**(不能偷看未来)。实现: 把注意力矩阵的**上三角置为 $-\infty$**, softmax 后这些位置权重 = 0。

**实测** (实验2 热力图右图): causal mask 让注意力矩阵变成下三角, 每个 query 只对它之前的 keys 有权重。这是 GPT 自回归生成的数学保证。

---

## 实验回顾: mini-GPT (106K 参数学语言)

**实测** (实验3): 一个 d_model=64 / 4头 / 2层 / 106,651 参数的迷你 GPT, 字符级训练 200 步:

```
步数   loss
   0   3.4706   (= 随机猜测, ln(27词表)=3.30)
 100   0.4701
 200   0.1328   (模型几乎能预测每个下一个字符)
```

**生成样本** (温度=0.3, 从 't' 开始):
> "tion instead of recurrence it enables palllel train"

它学会了语料里的 "instead of recurrence it enables parallel training"! 一个 10 万参数的玩具模型, 用你学的全部知识 (Self-Attention + GELU + CrossEntropy + Adam), 就能学到真实的语言规律。这就是 Transformer 的力量。

---

## 计算复杂度: Transformer 的阿喀琉斯之踵

| 层 | 复杂度 | 瓶颈 |
|----|--------|------|
| Self-Attention | $O(n^2 \cdot d)$ | **序列长度平方** — 长文本爆炸 |
| FFN | $O(n \cdot d^2)$ | 与序列长度线性 |

> $O(n^2)$ 是 Self-Attention 的根本代价: 序列翻倍, 计算量 ×4。这就是为什么长上下文 (100K+ token) 极贵, 也是 FlashAttention / 稀疏注意力 / 线性注意力 等研究的动机。

---

## 速查表

```
理解 Transformer 的 5 个积木:
  1. Self-Attention   每个词看到所有词 (全局视野 + 并行)  ← 灵魂
  2. Multi-Head       多个头学多种关系
  3. Positional Emb   补回顺序信息
  4. 残差 + LayerNorm 让深堆叠可训练
  5. FFN              每层独立的非线性变换 (你学的 GELU)

训练一个 GPT:
  - 架构: Decoder-Only, causal mask
  - 激活: GELU (或 SwiGLU)
  - 损失: next-token CrossEntropy
  - 优化: AdamW + warmup + cosine decay
```

---

## 参考文献

- Vaswani et al. 2017, *Attention Is All You Need* — Transformer 开山之作
- Radford et al. 2018, *Improving Language Understanding by Generative Pre-Training* (GPT-1)
- Karpathy, *nanoGPT* — 最清晰的参考实现 (本实验的灵感来源)
- Dao et al. 2022, *FlashAttention: Fast and Memory-Efficient Exact Attention* — 解决 $O(n^2)$ 的工程突破
- Shazeer 2020, *GLU Variants Improve Transformer* — SwiGLU

---

> **下一步**: 跑 `python3 experiments/transformer_overview.py`, 重点看 mini-GPT 的生成结果 — 一个 10 万参数的玩具, 真的学会了"语言"。

---

## 费曼回炉记录（L2 自检 · 已迭代）

- **F2 卡壳点**：
  - **卡点 A**：长期背 $\text{softmax}(QK^T/\sqrt{d})V$ 但说不清 Q/K/V 是什么。重读"搜索系统比喻"才钉死：**Q 是"我在找什么"、K 是"我有什么标签"、V 是"找到我我给你什么"**——每个词用 Q 去和所有词的 K 配对（点积 = 相似度），匹配高的多拿它的 V。本质就是 3 次矩阵乘法 + 1 次 softmax，没有循环没有递归，所以能完全并行。
  - **卡点 B**：一直不理解为什么公式里要除以 $\sqrt{d_k}$，以为是凑出来的常数。重读第 1 节实测才顿悟：$d_k=512$ 时裸 $QK^T$ 标准差 21.2，softmax 输出近乎 one-hot——**梯度趋零，模型学不动**。除以 $\sqrt{512} \approx 22.6$ 后标准差变 0.9，softmax 平滑，多词都能分到注意力，梯度正常流动。**这一刀是为了救梯度**，不是仪式。

- **F3 术语翻译**：
  - "Self-Attention" → **每个字去和其他所有字"互相点名"**——点谁名、谁就把信息递过来，最后每个字都变成"它最关心的那些字的融合"。
  - "Causal Mask" → **只能看前面，不许偷看后面**——把注意力矩阵的上三角设成 $-\infty$，softmax 后那些位置就变 0，这是 GPT 自回归生成的数学保证。
  - "Multi-Head" → **派多组人，每组盯一种关系**——一个头看主谓、一个头看指代、一个头看相邻，最后把各组发现拼起来。

- **F4 回炉**：
  - **v1（错误直觉）**：以为 Transformer 的核心是"很多层"或"参数大"，注意力只是其中一个部件。
  - **v2（修正后）**：钉死 **Self-Attention 才是灵魂**——它同时解决了 RNN 的两个死穴（远处信息衰减 + 无法并行）。第 3 节 mini-GPT 实验里 10 万参数的玩具就能学到 "instead of recurrence it enables parallel training"——这就是注意力的力量。diff 在于把 Transformer 从"很深的大网络"重定义为**"用注意力替代循环"的架构革命**——深度只是次要红利。

<!--
元理论引用：故事即世界迭代器-元理论.md §断言 3
L2 不达标 = KL 散度未修复 = 章节在漂移而非迭代
-->
