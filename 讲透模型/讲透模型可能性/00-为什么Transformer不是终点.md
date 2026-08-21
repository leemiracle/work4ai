# 00 — 为什么 Transformer 不是终点？

> 这是「讲透模型可能性」开篇。本篇用实测数字回答一个根本问题：**Transformer+Attention 这么强，为什么还要探索其他架构？** 答案是 O(n²) 复杂度 + 单一归纳偏置 + 缺乏世界模型。
>
> 配套实验：`experiments/00_why_not_transformer.py`。

---

## 1. 灵魂：Transformer 是赢家，但不是终点

$$
\boxed{\text{Transformer+Attention 是 2017-2024 的赢家，不是 AI 架构的终点}}
$$

- **O(n²) 复杂度**限制了它走向百万 token
- **单架构**无法覆盖所有智能形态（时序/图/物理/类脑）
- **Mamba、RWKV、Diffusion、SNN、Predictive Coding**——每种"非主流"架构都在回答一个 Transformer 答不好的问题

---

## 2. Attention 的 O(n²) 复杂度实测

### 2.1 标准注意力公式

$$
\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^\top}{\sqrt{d}}\right) V
$$

中间结果 $QK^\top$ 是 $n \times n$ 矩阵——**随序列长度平方增长**。

### 2.2 实测：序列长度 vs 资源消耗

| 序列长度 N | Attention FLOPs | Attention 内存 | Mamba FLOPs | **Attn/Mamba 比** |
|:------:|:----------:|:----------:|:--------:|:------------:|
| 512 | 68M | 393K | 2.2M | **30×** |
| 2K | 1.1G | 4.7M | 8.9M | **122×** |
| 8K | 17G | 69M | 36M | **488×** |
| 32K | 278G | 1.1G | 143M | **1950×** |
| 128K | **4.4T** | **17G** | 570M | **7800×** |

### 2.3 关键观察

- **N=512**：Attention 已经是 Mamba 的 30 倍
- **N=131072**（128K context）：Attention FLOPs 比 Mamba 多 **7800 倍**！
- 内存：Attention 17 GB vs Mamba 8 MB（差 2000 倍）

**这就是为什么 GPT-4 长上下文这么贵**——128K context 调用一次相当于 32K 的 ~16 倍成本。也是 **Mamba 等 SSM 兴起的根本原因**。

---

## 3. Transformer 的五大瓶颈

### 3.1 O(n²) 复杂度（最严重）

长上下文（128K/1M token）成本极高。GPT-4 从 32K → 128K → 1M 的演进全是工程难题。

### 3.2 KV Cache 巨大

每生成 1 个 token，要读**全部历史 K/V**。70B 模型 + 32K 上下文：**KV cache ~40 GB**。[vLLM 的 PagedAttention](https://arxiv.org/abs/2309.06180) 就是为解决这个问题（详见 [`../讲透KV Cache/`](../讲透KV Cache/)）。

### 3.3 归纳偏置单一

Transformer 假设"任意两 token 可能相关"。对**时序数据**（金融/EEG）、**图数据**（分子/社交网络）、**物理系统**（流体/粒子）不是最优。GNN/SNN/Equivariant 各有更适合的偏置。

### 3.4 缺乏"世界模型"

Transformer 学的是**token 联合分布**，不是**世界因果**。Yann LeCun 反复批评："LLM 没有世界模型"。JEPA 等架构在补这个。

### 3.5 样本效率低

Transformer 需要**万亿 token** 才学到"常识"。人类小孩只用**几亿 token** 就学会语言。脑启发（SNN/Predictive Coding）想解决这个差距。

---

## 4. 超越 Transformer 的六大方向

```
┌──────────────────────────────────────────────────────────┐
│ 方向 1: 亚二次复杂度                                       │
│   SSM (S4/Mamba) / Linear Attention / RWKV / 长卷积 / 稀疏│
├──────────────────────────────────────────────────────────┤
│ 方向 2: 生成模型新架构                                     │
│   DiT (Diffusion Transformer) / Flow Matching / Sora     │
├──────────────────────────────────────────────────────────┤
│ 方向 3: 非深度学习范式                                     │
│   Neuro-Symbolic / Hopfield / 可微编程                    │
├──────────────────────────────────────────────────────────┤
│ 方向 4: 脑启发与生物学                                     │
│   SNN / Predictive Coding / Hyperdimensional Computing   │
├──────────────────────────────────────────────────────────┤
│ 方向 5: 物理/科学启发                                      │
│   Equivariant NN / GNN / PINN / Neural ODE              │
├──────────────────────────────────────────────────────────┤
│ 方向 6: 记忆增强与外部存储                                 │
│   Memory Networks / NTM / DNC / RAG                      │
└──────────────────────────────────────────────────────────┘
```

---

## 5. 现状：哪些"非主流"架构已生产可用？

| 架构 | 代表 | 状态 | 应用 |
|------|------|:--:|------|
| **Mamba (SSM)** | Jamba 256K | ✅ 商用 | 长文本 |
| **RWKV** | RWKV-6 | ✅ 开源商用 | 中文社区/边缘 |
| **DiT (Diffusion)** | Sora, SD3 | ✅ 主流 | 视频/图像 |
| **Flow Matching** | Flux, SD3 | ✅ 新主流 | 图像 |
| **GNN** | AlphaFold | ✅ 科学 | 药物/材料 |
| **Equivariant NN** | AlphaFold 2 | ✅ 科学 | 分子结构 |
| SNN | Intel Loihi | 🟡 神经形态硬件 | 边缘/低功耗 |
| Neural ODE/PINN | 研究中 | 🟡 | 物理仿真 |
| Hopfield | 现代 attention | ✅ 已融入 LLM | Transformer 内部 |
| Predictive Coding | 研究阶段 | 🔴 实验 | 脑启发 |
| Neuro-Symbolic | DeepProblog | 🟡 研究 | 推理 |
| 量子 ML | IBM QML | 🔴 早期 | 未来 |

**关键**：Transformer 没被替代，但**互补架构**已生产化。

---

## 6. 一个反直觉观点：Transformer 已经是 Hopfield Network

[Ramsauer 2020](https://arxiv.org/abs/2008.02217) 证明：**现代 Hopfield Network 的检索步骤等价于 attention**。

也就是说，Transformer 的 attention 不是凭空发明的——它是 1982 年 Hopfield Network 的现代化身。**了解 Hopfield 历史能让你看懂 attention 的本质**（本系列 11 篇详解）。

---

## 7. 本系列的 16 篇规划

| 篇章 | 主题 | 为什么重要 |
|:--:|------|----------|
| **00** | 为什么 Transformer 不是终点 | 本篇 |
| 01 | State Space Models (S4/Mamba) | O(n) + 任意长上下文 |
| 02 | Linear Attention (Performer) | 核函数近似 |
| 03 | RWKV 与现代 RNN | RNN+Transformer 混血 |
| 04 | 长卷积 (Hyena/H3) | FFT 加速 |
| 05 | 稀疏注意力 | 工程妥协 |
| 06 | 混合架构 (Jamba) | 务实派 |
| 07 | Diffusion 架构演化 (DiT/Sora) | 生成模型新主流 |
| 08 | Flow Matching | 比 Diffusion 直接 |
| 09 | 能量模型与 Score-based | 物理直觉 |
| 10 | 神经符号 AI | 推理能力补强 |
| 11 | Hopfield 复兴 | attention 的根 |
| 12 | Spiking NN | 能效 1000× |
| 13 | Predictive Coding | 脑启发 |
| 14 | Equivariant NN / GNN | 物理/分子 |
| 15 | Memory Networks | 外部记忆 |
| 16 | 未来：推理时计算 + 量子 ML + AGI | 综述 |

---

## 8. 一句话总结

> **Transformer+Attention 不是 AI 架构的终点。O(n²) 复杂度实测：N=131072 时 attention FLOPs 是 Mamba 的 7800 倍——这是 GPT-4 长上下文贵的根本原因。五大瓶颈：O(n²) 复杂度 / KV Cache 巨大 / 归纳偏置单一 / 缺乏世界模型 / 样本效率低。六大方向：亚二次复杂度（SSM/Linear/RWKV/长卷积/稀疏）、生成新架构（DiT/Flow Matching）、非深度范式（Neuro-Symbolic/Hopfield）、脑启发（SNN/Predictive Coding）、物理启发（Equivariant/GNN/PINN）、记忆增强（Memory Nets/NTM）。生产现状：Mamba/RWKV/DiT/GNN 已商用，SNN/量子 ML 在早期。本系列 16 篇系统探索模型设计的可能性空间。**

---

## ✍️ 练习（`00_why_not_transformer.py`）

1. **手算复杂度**：手算 N=4096, d=64 时 attention 的 FLOPs，验证 ≈ 4.3G。
2. **加 GPU 实测**：用 PyTorch + CUDA 重测，看真实 GPU 下 attention vs Mamba 的速度比。
3. **接长上下文**：跑 Llama-3 70B 在 32K vs 128K 上下文下的延迟对比。
4. **加 FlashAttention**：用 FlashAttention 重测，看 O(n²) 内存怎么变 O(n)。
5. **画 N vs 时间曲线**：把 N 从 512 扫到 65536，画 attention 时间的指数曲线。

---

## 📌 下一步

下一篇 **01-State Space Models (S4/Mamba)** 把 SSM 彻底拆透：连续状态空间方程 → 离散化 → 并行训练（parallel scan）→ Mamba 的选择性机制——**让 O(n) 复杂度成为现实**。

---

## 费曼回炉记录（L2 自检 · 已迭代）

- **F2 卡壳点**：
  - **卡点 A**：长期以为 "Attention 是 O(n²)" 只是一句口号，没直觉这到底多贵。重读第 2 节那张实测表才被钉死：**N=128K 时 attention 的 FLOPs 是 Mamba 的 7800 倍**，内存差 2000 倍。这不是"贵一点"，是"贵到你根本跑不起"。GPT-4 长上下文那么贵不是定价问题，是物理问题。
  - **卡点 B**：以为"Transformer 一统天下 = 它就是最优架构"。重读第 3 节才看清五大瓶颈里最致命的是**归纳偏置单一**——它假设"任意两 token 可能相关"，对时序、图、物理这些有结构的数据不是最优。所以 Mamba 走时序、GNN 走图、Equivariant NN 走对称性——各有各的归纳偏置主场。

- **F3 术语翻译**：
  - "O(n²) 复杂度" → **句子长一倍，算力涨四倍**——所以长文本账单是平方级往上涨的。
  - "归纳偏置（Inductive Bias）" → **模型对"题目长什么样"事先打的赌**——Transformer 赌"任意两字都可能相关"，CNN 赌"挪个位置还是同一样东西"。
  - "KV Cache" → **模型为已读过的字临时存的笔记本**——每生成一个新字都要翻这本笔记本，所以笔记本越长，翻得越慢。

- **F4 回炉**：
  - **v1（错误直觉）**：以为 Transformer 已经"赢了"，其他架构都是陪跑。
  - **v2（修正后）**：钉死"Transformer 是赢家，但不是终点"。第 5 节那张表显示 Mamba/RWKV/DiT/GNN 都已**生产商用**——不是替代 Transformer，而是**互补**：长文本走 Mamba、视频走 DiT、分子走 GNN。diff 在于把视野从"单一架构统治一切"升级为**架构多样性是常态**——选择正确的归纳偏置比"用最强的那个"更重要。

<!--
元理论引用：故事即世界迭代器-元理论.md §断言 3
L2 不达标 = KL 散度未修复 = 章节在漂移而非迭代
-->
