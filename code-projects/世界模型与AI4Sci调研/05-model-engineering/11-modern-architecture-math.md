# 第十一章 · 现代大模型架构的完整数学推导（2024–2026 SOTA）

> 本文是 `05-model-engineering` 卷的架构数学深度篇。前面几章给了 Mamba / MLA / Lightning Attention 的「概览」，但**没有完整数学推导**。本章把这些当下 SOTA 架构拆到「每一步代数变形都写出来」的程度。
>
> 阅读前提：你已经会算 $\text{softmax}(QK^\top)V$，知道什么是反向传播。本章不再复习这些。
>
> 一手核实：所有 arXiv ID 均通过 `export.arxiv.org/api/query` 校验（2026-07-20）。

---

## ⚠️ 开篇勘误（重要）

用户原命题把「Lightning Attention」归给 **Kimi K2**。这是事实错误，必须先纠正：

- **Lightning Attention 是 MiniMax 的技术**（OpenNLPLab 团队：Zhen Qin、Yiran Zhong 等）。论文链：
  - Lightning Attention 原版（TransNormerLLM）：[arXiv:2405.17381](https://arxiv.org/abs/2405.17381)（ICML 2024）
  - Lightning Attention-2：[arXiv:2401.04658](https://arxiv.org/abs/2401.04658)
  - MiniMax-01（Lightning Attention + MoE 工业化）：[arXiv:2501.08313](https://arxiv.org/abs/2501.08313)（456B 总参/45.9B 激活）
  - MiniMax-M1（Lightning Attention + 推理模型）：[arXiv:2506.13585](https://arxiv.org/abs/2506.13585)
- **Kimi K2**（[arXiv:2507.20534](https://arxiv.org/abs/2507.20534)，Moonshot AI，2025-07）用的是**标准注意力 + MoE + MuonClip 优化器**（1T 总参/32B 激活），**不是 Lightning Attention**。

所以第二节我会写「Lightning Attention（MiniMax）」，而不是「（Kimi K2）」。这是本章最重要的归属性纠正——架构创新是谁的，必须说清楚，否则后面读论文会处处错位。

---

## 一、Multi-Head Latent Attention (MLA) 完整数学（DeepSeek-V2/V3）

> 论文：DeepSeek-V2: A Strong, Economical, and Efficient Mixture-of-Experts Language Model，DeepSeek-AI，[arXiv:2405.04434](https://arxiv.org/abs/2405.04434)（2024-05）
> 论文：DeepSeek-V3 Technical Report，DeepSeek-AI，[arXiv:2412.19437](https://arxiv.org/abs/2412.19437)（2024-12，671B 总参/37B 激活）
> 论文：Insights into DeepSeek-V3（硬件视角），[arXiv:2505.09343](https://arxiv.org/abs/2505.09343)（ISCA 2025）

MLA 是 DeepSeek-V2 提出并在 V3、V3.1、R1 中沿用的注意力机制。它的唯一动机：**在长上下文推理时，把 KV cache 压到原来的零头**。V2 官方数字：KV cache 减少 **93.3%**（即 ~14× 压缩，论文常用「~9×」指代典型配置下的对比），生成吞吐 5.76×。

### 1.1 标准 MHA 的 KV cache 问题

设单层、batch=1。标准多头注意力有 $n_h$ 个头，每头维度 $d_h$，隐藏维度 $d = n_h d_h$。对序列位置 $t$，输入隐藏向量 $h_t \in \mathbb{R}^d$，生成所有头的 K、V：

$$
K_t = W^{UK} h_t \in \mathbb{R}^{d}, \quad V_t = W^{UV} h_t \in \mathbb{R}^{d}
$$

其中 $W^{UK}, W^{UV} \in \mathbb{R}^{d \times d}$。**推理时每生成一个 token，必须把这一层的 $K_t, V_t$ 存进 KV cache 供后续 token 检索**。对于一个长度为 $L$ 的序列、$N$ 层，KV cache 总大小：

$$
\text{KV cache} = 2 \cdot N \cdot L \cdot d \quad (\text{元素数，FP16 则 }\times 2 \text{ 字节})
$$

例如 70B 模型、$N=80$、$d=8192$、$L=128\text{K}$、FP16：$2 \times 80 \times 131072 \times 8192 \times 2 \approx 343\,\text{GB}$——**光 KV cache 就比模型权重还大**。这就是长上下文推理的内存墙。

### 1.2 MQA 与 GQA 的简化（铺垫）

在讲 MLA 之前，先看两个「砍 KV cache」的前辈，它们是理解 MLA 的台阶。

**Multi-Query Attention (MQA)**（Shazeer, 2019）：所有 query 头**共享同一组 K、V**。即 $W^{UK}, W^{UV}$ 只产出一个 $d_h$ 维的 K/V，$n_h$ 个 query 头都用它。KV cache 直接除以 $n_h$。代价：质量下降明显。

**Grouped-Query Attention (GQA)**（Ainslie et al., 2023）：折中。把 $n_h$ 个 query 头分成 $n_g$ 组，每组共享一对 K/V。KV cache 除以 $n_h / n_g$。Llama 2 70B、Llama 3、Mistral 都用 GQA。

> 论文：GQA: Training Generalized Multi-Query Transformer Models from Multi-Head Checkpoints，[arXiv:2305.13245](https://arxiv.org/abs/2305.13245)（Ainslie et al., 2023）

MQA 是 GQA 的极端情形（$n_g = 1$），MHA 是另一极端（$n_g = n_h$）。但无论 MQA/GQA，本质都是**「减少 K/V 头的数量」**——这是「数量维度」的压缩。MLA 走的是另一条路：**「维度维度」的低秩压缩**。

### 1.3 MLA 核心思想：低秩压缩 KV

观察：K、V 矩阵各 $d$ 维，但它们其实「信息量」远没那么大——大量的列是高度相关的。MLA 假设：**存在一个低维 latent 向量 $c_t \in \mathbb{R}^{d_c}$（$d_c \ll d$），使得 K、V 都可以由它线性恢复**。

**第一步：下采样到 latent（Down-projection）**

$$
c_t = W^{DKV} h_t \in \mathbb{R}^{d_c}
$$

其中 $W^{DKV} \in \mathbb{R}^{d_c \times d}$，$d_c$ 是压缩维度（V2 配置 $d_c = 512$，而 $d = 5120$，压缩 10×）。

**第二步：上采样回 K、V（Up-projection）**

$$
k_t = W^{UK} c_t \in \mathbb{R}^{d_h n_h}, \quad v_t = W^{UV} c_t \in \mathbb{R}^{d_h n_h}
$$

其中 $W^{UK}, W^{UV} \in \mathbb{R}^{(d_h n_h) \times d_c}$。

**关键收益**：推理时 KV cache **只存 $c_t$**（$d_c$ 维），不存 $k_t, v_t$（各 $d_h n_h$ 维）。需要 K、V 时再临时上采样。V2 配置下，每层每 token：

- 原始：$2 d_h n_h = 2 \times 128 \times 128 = 32768$ 元素
- MLA：$d_c = 512$ 元素
- 压缩比 $\approx 64\times$（这是「9×」说法在不同归一化口径下的差异，论文 headline 93.3% 是端到端实测）

Q 侧类似也有一个 latent 压缩（$c_t^Q = W^{DQ} h_t$，再上采样 $q_t = W^{UQ} c_t^Q$），但 Q 不进 cache，所以 Q 的压缩主要省计算、不省 cache。

### 1.4 MLA 完整前向公式（含 RoPE）

完整的 MLA（带旋转位置编码 RoPE）每一步：

**Query 路径：**
$$
c_t^Q = W^{DQ} h_t \in \mathbb{R}^{d_c'}, \quad q_t = W^{UQ} c_t^Q \in \mathbb{R}^{d_h' n_h}
$$
其中 $d_h' n_h$ 拆成两部分：一部分走 RoPE（$q_t^{(R)} \in \mathbb{R}^{d_h^R n_h}$），一部分不走（$q_t^{(C)}$）。DeepSeek 把 RoPE 单独拎出来处理，这是为了配合下面的「吸收技巧」。

**KV 路径：**
$$
c_t = W^{DKV} h_t \in \mathbb{R}^{d_c}
$$
$$
k_t^{(C)} = W^{UK} c_t \in \mathbb{R}^{d_h' n_h} \quad (\text{不带 RoPE 的部分})
$$
$$
k_t^{(R)} = \text{RoPE}(W^{KR} h_t) \in \mathbb{R}^{d_h^R} \quad (\text{带 RoPE 的部分，低秩})
$$
$$
v_t = W^{UV} c_t \in \mathbb{R}^{d_h' n_h}
$$

**Attention 输出**（单头视角，省略头下标）：
$$
o_t = \sum_{i=1}^{t} \text{softmax}_t\!\left(\frac{\langle q_t, k_i \rangle}{\sqrt{d_h'}}\right) v_i
$$

其中 $\langle q_t, k_i \rangle$ 是内积，要分两部分算（带 RoPE 的和不带的）。

### 1.5 ⭐ 吸收技巧（Absorption Trick）—— MLA 的真正杀招

朴素 MLA 推理时，对每个新 query 仍要先把所有历史 $c_i$ 上采样成 $k_i = W^{UK} c_i$、$v_i = W^{UV} c_i$，再做 attention。**这等于把压缩省下的计算又花回去了**，没意义。

吸收技巧的数学观察：attention 的核心运算是 query 和 key 的内积，而 key 是 latent 的线性函数：

$$
\langle q_t, k_i^{(C)} \rangle = q_t^\top (W^{UK} c_i) = (q_t^\top W^{UK})\, c_i = \underbrace{(W^{UK\top} q_t)}_{\tilde q_t}\,^\top c_i
$$

**把 $W^{UK}$ 从 key 侧「吸收」到 query 侧**：预先计算 $\tilde q_t = W^{UK\top} q_t$（这只在当前 token 算一次），然后用 $\tilde q_t$ 直接和缓存的 $c_i$ 做内积。同理，输出侧：

$$
o_t = \sum_i \alpha_{ti}\, v_i = \sum_i \alpha_{ti}\, (W^{UV} c_i) = W^{UV} \left(\sum_i \alpha_{ti} c_i\right)
$$

即先用 $c_i$ 算出 latent 空间的加权和 $\sum_i \alpha_{ti} c_i$，最后再用 $W^{UV}$ 一次性上采样回 $v$ 空间。

**结论：推理全程不需要显式计算/缓存 $k_i, v_i$，只操作 $c_i$。** $W^{UK}, W^{UV}$ 这些矩阵不进 cache，只在当前 token 的少量矩阵乘里用一次。这就是 MLA 能实现「KV cache 压缩 + 不增加计算」的根本原因。

> 注意：带 RoPE 的部分 $k^{(R)}$ 无法被吸收（RoPE 是位置相关的非线性交织），所以 DeepSeek 把 RoPE 部分单独做成一个低秩旁路（$d_h^R$ 很小，如 64），单独缓存。这是 MLA 公式看起来「啰嗦」的原因。

### 1.6 MLA 的低秩视角：它与 LoRA 是同构的

把 MLA 翻译成矩阵分解语言：原始注意力里 $W^{UK}_{\text{full}} \in \mathbb{R}^{d \times d}$（满秩），MLA 用 $W^{UK} \cdot W^{DKV}$（$\mathbb{R}^{(d_h n_h)\times d_c} \cdot \mathbb{R}^{d_c \times d}$）来近似它，rank $\le d_c$。**这和 LoRA（低秩适配）的 $BA$ 分解是同一个数学结构**——只不过 LoRA 用它来省微调参数，MLA 用它来省推理 cache。一个数学技巧，两个战场。

这也回答了一个常见疑问：「MLA 会不会掉点？」——低秩近似确实损失表达力，但 V2/V3 实测在同等规模下质量与 MHA 持平甚至更好。可能的解释：attention 的 K/V 本身就存在大量冗余，$d_c$ 维足以捕获主要信息；且端到端训练让模型主动学会在 latent 空间里组织信息。

### 1.7 MLA PyTorch 参考实现（教学版）

```python
import torch
import torch.nn as nn
import torch.nn.functional as F

class MLA(nn.Module):
    """Multi-head Latent Attention（教学版，省略 RoPE 旁路与吸收技巧）。
    展示 low-rank KV compression 的核心结构。"""
    def __init__(self, d=5120, n_h=128, d_h=128, d_c=512):
        super().__init__()
        self.n_h, self.d_h = n_h, d_h
        # Q 路径
        self.W_DQ = nn.Linear(d, d_c, bias=False)
        self.W_UQ = nn.Linear(d_c, n_h * d_h, bias=False)
        # KV 路径（共享 latent）
        self.W_DKV = nn.Linear(d, d_c, bias=False)
        self.W_UK = nn.Linear(d_c, n_h * d_h, bias=False)
        self.W_UV = nn.Linear(d_c, n_h * d_h, bias=False)
        self.W_O = nn.Linear(n_h * d_h, d, bias=False)

    def forward(self, h):
        # h: [B, L, d]
        B, L, _ = h.shape
        q = self.W_UQ(self.W_DQ(h))          # [B, L, n_h*d_h]
        c = self.W_DKV(h)                    # [B, L, d_c]  <- 这才是要 cache 的
        k = self.W_UK(c)                     # [B, L, n_h*d_h]  训练时显式，推理时用吸收技巧省掉
        v = self.W_UV(c)                     # [B, L, n_h*d_h]

        def split(x):  # -> [B, n_h, L, d_h]
            return x.view(B, L, self.n_h, self.d_h).transpose(1, 2)
        q, k, v = split(q), split(k), split(v)
        o = F.scaled_dot_product_attention(q, k, v)  # [B, n_h, L, d_h]
        o = o.transpose(1, 2).reshape(B, L, -1)
        return self.W_O(o), c   # 返回输出 + latent（推理只 cache c）

# 推理时吸收技巧的核心（伪代码）：
#   q_tilde = W_UK.weight @ q   # 把上采样吸收进 query，只算一次
#   scores = q_tilde @ c.T      # 直接和 latent 算，不展开 K
#   latent_sum = softmax(scores) @ c
#   o = W_UV(latent_sum)        # 最后再上采样 V
```

### 1.8 MLA 的 KV cache 节省量化

以 DeepSeek-V2 配置（$d_c = 512$，$d_h n_h = 128 \times 128 = 16384$）：

| 方案 | 每层每 token cache（元素） | 相对 MHA |
|------|--------------------------|---------|
| MHA | $2 \times 16384 = 32768$ | 1× |
| GQA（$n_g=8$） | $2 \times 16384/16 = 2048$ | 16× 省 |
| **MLA** | **512**（仅 latent $c$） | **64× 省** |

论文端到端 headline 是「KV cache 减少 93.3%」（≈14×），差异来自：headline 把 Q 的 latent、RoPE 旁路、以及多 batch 的归一化都算进去了。无论哪个口径，MLA 都是当前**单位表达力下 KV cache 最省**的注意力。

---

## 二、Lightning Attention（MiniMax）完整数学

> 论文：Various Lengths, Constant Speed: Efficient Language Modeling with Lightning Attention，Qin et al.，[arXiv:2405.17381](https://arxiv.org/abs/2405.17381)（ICML 2024）
> 论文：Lightning Attention-2，[arXiv:2401.04658](https://arxiv.org/abs/2401.04658)
> 论文：MiniMax-01: Scaling Foundation Models with Lightning Attention，[arXiv:2501.08313](https://arxiv.org/abs/2501.08313)（456B 总参/45.9B 激活，1M 训练上下文）
> 论文：MiniMax-M1，[arXiv:2506.13585](https://arxiv.org/abs/2506.13585)（Lightning Attention + 推理，CISPO 算法）

Lightning Attention 是**线性注意力（Linear Attention）的高效实现**。要理解它，必须先吃透线性注意力的数学，再理解「为什么朴素线性注意力在 causal 场景下不快」以及「Lightning Attention 怎么绕过这个坎」。

### 2.1 从 Softmax Attention 到 Linear Attention

**标准（softmax）注意力**，对 query $q_t$：

$$
o_t = \frac{\sum_{i=1}^{t} \exp(q_t^\top k_i)\, v_i}{\sum_{j=1}^{t} \exp(q_t^\top k_j)}
$$

矩阵形式（整段序列，$L$ 个 token）：

$$
O = \text{softmax}\!\left(\frac{Q K^\top}{\sqrt{d}}\right) V
$$

计算量：$Q K^\top$ 是 $[L, d] \times [d, L] = O(L^2 d)$。**这就是 $O(L^2)$ 瓶颈**。

**Linear Attention 的核心 trick**（Katharopoulos et al., 2020）：用一个非负核函数 $\phi(\cdot)$ 近似 $\exp$，使得 $\exp(q^\top k) \approx \phi(q)^\top \phi(k)$。然后利用**矩阵乘法结合律**重排计算顺序：

$$
O = \underbrace{(Q K^\top)}_{O(L^2 d)} V \quad \longrightarrow \quad O = Q \underbrace{(K^\top V)}_{O(L d^2)}
$$

> 论文：Transformers are RNNs: Fast Autoregressive Transformers with Linear Attention，Katharopoulos et al.，[arXiv:2006.16236](https://arxiv.org/abs/2006.16236)（ICML 2020，在长序列自回归上比标准 Transformer 快 4000×）

推导（核化 + 结合律）：

$$
\text{sim}(q_t, k_i) = \phi(q_t)^\top \phi(k_i)
$$
$$
o_t = \frac{1}{Z_t} \sum_{i=1}^{t} \phi(q_t)^\top \phi(k_i)\, v_i = \frac{1}{Z_t}\, \phi(q_t)^\top \underbrace{\left(\sum_{i=1}^{t} \phi(k_i) v_i^\top\right)}_{S_t \in \mathbb{R}^{d \times d}}
$$

其中归一化项 $Z_t = \sum_{i=1}^{t} \phi(q_t)^\top \phi(k_i) = \phi(q_t)^\top \left(\sum_{i=1}^{t} \phi(k_i)\right)$。

**关键**：$S_t = \sum_{i=1}^{t} \phi(k_i) v_i^\top$ 是一个累加和，且 $S_t = S_{t-1} + \phi(k_t) v_t^\top$——**这是一个递推！** 于是线性注意力天然是一个 RNN：

$$
\boxed{S_t = S_{t-1} + \phi(k_t) v_t^\top, \qquad o_t = \phi(q_t)^\top S_t / Z_t}
$$

推理时（生成）每步 $O(d^2)$，与序列长度无关——这就是「Transformers are RNNs」的含义。

常用的 $\phi$ 选择：
- $\phi(x) = \text{elu}(x) + 1$（Katharopoulos 原文，保证非负）
- $\phi(x) = \text{ReLU}(x)$（Performer 用 +ve random features 近似 softmax）

### 2.2 ⭐ 朴素线性注意力的「cumsum 陷阱」

线性注意力在**非因果（双向）**场景下确实漂亮：直接 $O = \phi(Q)(\phi(K)^\top V)$，一次矩阵乘 $O(L d^2)$，对 $L$ 是线性的。

但在**因果（自回归）**场景下，朴素实现会撞墙。看累加形式：

$$
S_t = \sum_{i=1}^{t} \phi(k_i) v_i^\top
$$

向量化地写成全序列：$S_{1:L} = \text{cumsum}_{i=1}^{L}\big(\phi(k_i) v_i^\top\big)$。问题在于 $\phi(k_i) v_i^\top$ 是一个 $d \times d$ 的外积，对每个 $i$ 都要算一个 $d^2$ 矩阵再累加——**GPU 上 cumsum 是串行的、不可并行**，而且 $d^2$ 的中间矩阵吃满显存。结果是：理论上 $O(L)$，实测比标准 attention 还慢。

> 这正是 Lightning Attention-2（2401.04658）摘要里说的：「due to the issue with cumulative summation (cumsum), current linear attention algorithms cannot demonstrate their theoretical computational benefits in a causal setting」。

### 2.3 ⭐ Lightning Attention 的 left/right chunk 分解

Lightning Attention 的天才想法：**不要全局 cumsum，而是把序列切成 chunk，chunk 内用标准 attention，chunk 间用线性 attention 的递推/矩阵形式**。这样既绕开 cumsum 串行，又保持线性复杂度。

把长度 $L$ 的序列切成大小为 $B$ 的 chunk（共 $L/B$ 块）。对当前 chunk（query chunk $Q_c \in \mathbb{R}^{B \times d}$），输出分两部分：

**Intra-chunk（chunk 内，left part）——用标准 attention：**

$$
O^{\text{intra}}_c = \text{softmax}\!\left(\frac{Q_c K_c^\top}{\sqrt{d}}\right) V_c \cdot M
$$

其中 $M$ 是下三角 causal mask（只看 chunk 内当前及之前 token）。这部分是 $O(B^2 d)$，但 $B$ 是固定常数（如 64/128），所以对 $L$ 仍是 $O(L \cdot B^2 d / B) = O(L B d)$，线性。

**Inter-chunk（chunk 间，right part）——用线性 attention 矩阵形式：**

对当前 chunk 之前的所有 chunk，用核化线性注意力。当前 chunk 之前累积的状态矩阵 $S_{\text{prev}} \in \mathbb{R}^{d \times d}$（之前所有 $\phi(k)v^\top$ 之和）：

$$
O^{\text{inter}}_c = \phi(Q_c)\, S_{\text{prev}}
$$

这是 $[B, d] \times [d, d] = O(B d^2)$。然后更新 $S_{\text{prev}} \mathrel{+}= \phi(K_c)^\top V_c$（加当前 chunk 的贡献）。

**合并：**

$$
\boxed{O_c = O^{\text{intra}}_c + O^{\text{inter}}_c}
$$

为什么这样能避开 cumsum？因为：
1. Intra-chunk 用标准 attention + causal mask，**根本不用 cumsum**（softmax 天然处理因果）。
2. Inter-chunk 用矩阵乘 $\phi(Q_c) S_{\text{prev}}$，**也不用逐 token cumsum**——只在 chunk 边界更新一次 $S_{\text{prev}}$。

**复杂度分析：**
- 每层总计算：$O(L B d) + O((L/B) \cdot B d^2) = O(L d (B + d))$，对 $L$ 线性。✓
- 训练时配合 tiling 技术（forward + backward 都 IO-aware），常数极小。

MiniMax-01 报告：训练上下文 1M token，推理可外推到 4M，且**速度对序列长度近似常数**（这是「Lightning」之名）。

### 2.4 Lightning Attention 的代价

线性注意力（含 Lightning）的软肋：**$\phi(q)^\top \phi(k)$ 近似 softmax 的质量有限**。MiniMax 的解法是混合架构——每隔若干层插一层标准 softmax attention（MiniMax-M1 的 hybrid 设计），用少量全注意力补回表达力。这与第九节 Jamba 的「Mamba+Transformer 混合」是同一种思路。

### 2.5 Linear Attention 的 NumPy 实现（最小可跑版）

```python
import numpy as np

def elu_plus_one(x):
    return np.where(x > 0, x + 1, np.exp(x))   # phi(x) = elu(x)+1, 非负

def linear_attention_causal(Q, K, V):
    """因果线性注意力，递推(RNN)形式。Q,K,V: [L, d]"""
    L, d = Q.shape
    phi_Q, phi_K = elu_plus_one(Q), elu_plus_one(K)
    S = np.zeros((d, d))      # 状态矩阵
    z = np.zeros(d)           # 归一化项的累加
    O = np.zeros((L, d))
    for t in range(L):
        S += np.outer(phi_K[t], V[t])     # S_t = S_{t-1} + phi(k_t) v_t^T
        z += phi_K[t]                      # z_t = z_{t-1} + phi(k_t)
        num = phi_Q[t] @ S                 # 分子 = phi(q_t)^T S_t
        den = phi_Q[t] @ z + 1e-8          # 分母
        O[t] = num / den
    return O

# 验证: 与标准 attention 在小规模上行为一致(非完全等价)
def standard_attention(Q, K, V):
    L = Q.shape[0]
    O = np.zeros_like(Q)
    for t in range(L):
        scores = Q[t] @ K[:t+1].T / np.sqrt(Q.shape[1])
        w = np.exp(scores - scores.max()); w /= w.sum()
        O[t] = w @ V[:t+1]
    return O

if __name__ == "__main__":
    np.random.seed(0)
    Q, K, V = [np.random.randn(32, 8) for _ in range(3)]
    print("linear:", linear_attention_causal(Q,K,V)[0,:3])
    print("softmax:", standard_attention(Q,K,V)[0,:3])
    # 注意: 两者数值不同(线性是近似), 但定性相关
```

跑这段你会看到线性注意力与 softmax 注意力输出**不同**（线性是近似），这正是它需要混合架构的原因。

---

## 三、Mamba / S6 完整推导

> 论文：Mamba: Linear-Time Sequence Modeling with Selective State Spaces，Gu & Dao，[arXiv:2312.00752](https://arxiv.org/abs/2312.00752)（2023-12）
> 论文：Efficiently Modeling Long Sequences with Structured State Spaces (S4)，Gu, Goel & Ré，[arXiv:2111.00396](https://arxiv.org/abs/2111.00396)（ICLR 2022 Outstanding Paper HM）
> 论文：Transformers are SSMs: ... Structured State Space Duality (Mamba-2)，Dao & Gu，[arXiv:2405.21060](https://arxiv.org/abs/2405.21060)（ICML 2024）

Mamba 是 State Space Model（SSM）家族里第一个在语言建模上**真正打过同规模 Transformer**的架构（Mamba-3B ≈ Transformer-6B）。它的数学从连续动力系统出发，经过 S4 的结构化参数化，到 S6 的选择性机制，每一步都有清晰的动机。

### 3.1 连续 State Space Model（基础）

SSM 描述一个连续时间线性动力系统：

$$
\dot{x}(t) = A\, x(t) + B\, u(t), \qquad y(t) = C\, x(t) + D\, u(t)
$$

- $u(t) \in \mathbb{R}$：输入信号（1 维，对应序列的一个标量通道）
- $x(t) \in \mathbb{R}^{N}$：隐状态（$N$ 是状态维度，S4 默认 $N=64$）
- $y(t) \in \mathbb{R}$：输出
- $A \in \mathbb{R}^{N \times N}, B \in \mathbb{R}^{N \times 1}, C \in \mathbb{R}^{1 \times N}$：参数

直觉：输入 $u(t)$ 通过 $B$ 注入状态 $x$，状态按 $A$ 演化（$A$ 决定记忆衰减/振荡），再通过 $C$ 读出。这就是一个连续 RNN。$D$ 通常是残差跳跃，常合并进后续归一化。

### 3.2 离散化（连续 → 序列）

神经网络处理的是离散序列 $\{u_k\}$。需要把连续 SSM 离散化：给定步长 $\Delta$，求 $\bar A, \bar B$ 使得 $x_k \approx \bar A\, x_{k-1} + \bar B\, u_k$。

**零阶保持（Zero-Order Hold, ZOH）离散化**（S4/Mamba 用）——假设输入在 $[k\Delta, (k+1)\Delta)$ 内为常数：

$$
\bar A = \exp(\Delta A), \qquad \bar B = (\Delta A)^{-1}(\exp(\Delta A) - I) \cdot \Delta B
$$

证明（简要）：$\dot x = Ax + Bu$ 的解 $x(t) = e^{At}x(0) + \int_0^t e^{A(t-\tau)}B\,u(\tau)d\tau$。ZOH 下 $u$ 在区间内常数 $= u_k$，积分得 $x_{k+1} = e^{A\Delta}x_k + \int_0^\Delta e^{A(\Delta-\tau)}B\,d\tau \cdot u_k$，即得上式。

简化形式（一阶 / 双线性近似，也常用）：$\bar A = (I + \Delta A/2)^{-1}(I - \Delta A/2)$。

**离散递推：**
$$
\boxed{x_k = \bar A\, x_{k-1} + \bar B\, u_k, \qquad y_k = C\, x_k}
$$

这又是一个 RNN！与线性注意力的递推 $S_t = S_{t-1} + \phi(k_t)v_t^\top$ 形式上同构（SSM 是更一般的形式：状态更新带转移矩阵 $\bar A$，而线性注意力相当于 $\bar A = I$）。

### 3.3 卷积视角（S4 的效率来源）

当 $A, B, C$ **与输入无关**（LTI 系统，线性时不变）时，整个序列的输出可以写成卷积。展开递推（设 $x_{-1}=0$）：

$$
y_k = C \bar A^k \bar B\, u_0 + C \bar A^{k-1} \bar B\, u_1 + \cdots + C \bar B\, u_k
$$

即 $y_k = \sum_{j=0}^{k} \overline{K}_j\, u_{k-j}$，其中卷积核：

$$
\overline{K}_j = C\, \bar A^j\, \bar B, \quad j = 0, 1, \ldots, L-1
$$

写成向量 $\overline{K} = (C\bar B,\ C\bar A\bar B,\ \ldots,\ C\bar A^{L-1}\bar B) \in \mathbb{R}^L$，则 $y = \overline K * u$（因果卷积）。

**意义**：训练时整个序列可以用一次 FFT 卷积 $O(L \log L)$ 算完，高度并行——这是 S4 在长序列上高效的根本。而推理（生成）时退回递推形式 $O(N)$ 每步。这就是 S4「训练像 CNN，推理像 RNN」的双形态。

### 3.4 S4 的结构化参数化：HiPPO 矩阵 + DPLR

朴素 SSM 的问题：$N \times N$ 的 $A$ 有 $N^2$ 参数，且 $\bar A^j$ 计算量爆炸（$O(N^3)$ 每次）。S4 的两个关键设计：

**(1) HiPPO 矩阵**（Gu et al., 2020，Mamba 前身 LP/LSSL 的工作）：用一个**固定**的特殊矩阵 $A_{\text{HiPPO}}$ 初始化，使 SSM 能最优地压缩历史输入。HiPPO 矩阵源于「用正交多项式近似历史信号的最近邻投影」，其元素：

$$
A_{ij} = -\begin{cases} \sqrt{(2i+1)(2j+1)} & i > j \\ i+1 & i = j \\ 0 & i < j \end{cases}
$$

（这是 HiPPO-LegS 变体）。这个矩阵让状态 $x$ 的每个分量记忆输入历史的不同时间尺度——**长程记忆的数学根源**。

**(2) 对角加低秩（DPLR）参数化**：令 $A = \Lambda - P P^\top$，其中 $\Lambda$ 对角、$P \in \mathbb{R}^{N \times 1}$。这样：
- $A$ 可对角化（经低秩修正后稳定），$V^{-1} A V = \Lambda$
- 卷积核 $\overline K$ 的计算化归为 **Cauchy 核**（柯西矩阵）的求解，用 FFT 在 $O(N \log N)$ 完成

这是 S4 论文的核心算法贡献：把看似 $O(N^3 L)$ 的卷积核构造降到 $O(N + L)$ 量级。

> S4 在 Long Range Arena 的 Path-X（长度 16K）任务上，是当时**唯一能解决**该任务的模型（其他全部随机猜）。这是 SSM 家族第一次震惊社区。

### 3.5 ⭐ Mamba / S6：选择性 State Space

S4 的致命弱点：**$A, B, C$ 是固定的，与输入无关**。这让它无法做「内容相关推理」——比如「看到一个特定 token 就选择性遗忘之前的内容」（这是 attention 天然能做到的）。Mamba 的核心创新：**让 SSM 参数变成输入的函数**（selective）。

在 Mamba（S6）中，离散化步长 $\Delta$、输入矩阵 $B$、输出矩阵 $C$ 都由输入 $u_t$ 经线性层生成：

$$
B_t = \text{Linear}_B(u_t) \in \mathbb{R}^{N}, \quad C_t = \text{Linear}_C(u_t) \in \mathbb{R}^{N}, \quad \Delta_t = \text{softplus}(\text{Linear}_\Delta(u_t)) \in \mathbb{R}
$$

而 $\bar A_t = \exp(\Delta_t A)$，$\bar B_t = \Delta_t B_t$（用简化离散化）。递推变成：

$$
\boxed{x_t = \bar A_t\, x_{t-1} + \bar B_t\, u_t = \exp(\Delta_t A)\, x_{t-1} + \Delta_t B_t\, u_t}
$$

**为什么这叫「选择性」？** $\Delta_t$ 控制状态更新的「步长」：
- $\Delta_t$ 大 → $\exp(\Delta_t A)$ 衰减快 → **遗忘**旧状态，写入新信息
- $\Delta_t$ 小 → $\exp(\Delta_t A) \approx I$ → **保持**旧状态，忽略当前输入

模型学会根据 $u_t$ 的内容动态调节 $\Delta_t$，从而实现「这个 token 重要就记住、不重要就忽略」——这是 S4 做不到的，是 Mamba 在语言上能打赢 Transformer 的关键。

**代价**：$A_t, B_t, C_t$ 依赖 $t$，**卷积视角失效**（卷积要求 LTI）。训练时只能用**并行扫描（parallel scan）**算法（前缀和的硬件友好版），配合硬件感知实现（在 GPU SRAM 里分块计算，类似 FlashAttention 的 tiling）。Mamba 论文用 CUDA 实现了 selective scan，比朴素递推快几个数量级。

### 3.6 Mamba Block（完整前向）

Mamba 把 selective SSM 包成一个残差 block（替代 Transformer 的 attention+MLP）。设输入 $u \in \mathbb{R}^{L \times D}$（$D$ 是模型宽度）：

```
u -> LayerNorm -> Linear(D -> E)         # 扩展到 E 维 (如 E=2D)
   -> conv1d (causal) -> SiLU
   -> split 成 x(E) 和 gate(E)
   -> 对 x: 投影到 SSM 参数 (B, C, Δ), 跑 selective scan 得 y
   -> y = y * SiLU(gate)                 # 门控
   -> Linear(E -> D)                     # 投影回 D
   -> + u                                # 残差
```

其中 selective scan 内部把 $D$ 维并行处理成 $D$ 个独立 SSM（每维一个状态 $x \in \mathbb{R}^N$）。

### 3.7 ⭐ Mamba-2：State Space Duality（SSD）

Mamba-2（Dao & Gu, 2024）的重大理论贡献：**揭示 SSM 与 Attention 的对偶关系**。

把 selective SSM 的递推展开成矩阵形式。设 $\bar A_{i:j} = \bar A_j \bar A_{j-1} \cdots \bar A_i$（连乘），则：

$$
y_t = \sum_{i=1}^{t} C_t^\top \bar A_{i+1:t}\, \bar B_i\, u_i
$$

写成全序列的矩阵乘 $y = M u$，其中 $M \in \mathbb{R}^{L \times L}$：

$$
M_{t,i} = C_t^\top \bar A_{i+1:t} \bar B_i \quad (i \le t), \quad M_{t,i} = 0 \quad (i > t)
$$

这个 $M$ 是一个**下三角的 semiseparable 矩阵**（半可分矩阵）——它的任意子矩阵都满足低秩性质。Mamba-2 证明：

> **Attention（带 causal mask）也是用一个矩阵乘作用在 $V$ 上：$O = \text{softmax}(QK^\top \odot M_{\text{causal}}) V$。如果去掉 softmax、把 $Q,C$ 与 $K,B$ 对应，则 SSM 的 $M$ 矩阵就是一种「结构化的 attention 矩阵」。**

这就是 **Structured State Space Duality (SSD)**：

$$
\underbrace{\text{Attention}}_{\text{稠密 } L\times L \text{ 矩阵}} \quad \longleftrightarrow \quad \underbrace{\text{SSM}}_{\text{semiseparable } L\times L \text{ 矩阵}}
$$

SSM 的矩阵是 semiseparable（结构化、低参数），所以可以用 $O(L)$ 而非 $O(L^2)$ 算；attention 的矩阵是稠密的，所以必须 $O(L^2)$。但两者在「序列混合」这个功能上是同源的。

Mamba-2 基于此设计了 SSD 算法：用「块分解」（类似 Lightning Attention 的 intra/inter chunk）把 semiseparable 矩阵乘法降到 $O(L N)$，且比 Mamba-1 的 selective scan 快 2–8×，还能用更大的状态维度 $N$（Mamba-2 用 $N=128$ 或 $256$，而 Mamba-1 限于 $N=16$）。

### 3.8 Mamba block 的 PyTorch 实现（selective scan 简化版）

```python
import torch
import torch.nn as nn
import torch.nn.functional as F

class MambaBlock(nn.Module):
    """Mamba/S6 block 教学版。selective scan 用 Python 循环(慢但清晰)。"""
    def __init__(self, D=512, E=1024, N=16):
        super().__init__()
        self.D, self.E, self.N = D, E, N
        self.norm = nn.LayerNorm(D)
        self.in_proj = nn.Linear(D, 2*E, bias=False)      # x 和 gate
        self.conv1d = nn.Conv1d(E, E, 3, padding=1, groups=E)
        # SSM 参数投影
        self.x_to_B = nn.Linear(E, N, bias=False)
        self.x_to_C = nn.Linear(E, N, bias=False)
        self.x_to_dt = nn.Linear(E, 1, bias=False)
        # A 是可学习参数(log(-A) 形式, 保证负实部稳定)
        self.A_log = nn.Parameter(torch.randn(N))
        self.D_res = nn.Parameter(torch.ones(E))
        self.out_proj = nn.Linear(E, D, bias=False)

    def forward(self, u):  # u: [B, L, D]
        B_, L, _ = u.shape
        xz = self.in_proj(self.norm(u))                   # [B,L,2E]
        x, z = xz.chunk(2, dim=-1)                        # 各 [B,L,E]
        x = self.conv1d(x.transpose(1,2)).transpose(1,2)  # causal conv1d
        x = F.silu(x)
        # SSM 参数(输入相关)
        Bb = self.x_to_B(x)                               # [B,L,N]
        Cc = self.x_to_C(x)                               # [B,L,N]
        dt = F.softplus(self.x_to_dt(x))                  # [B,L,1]
        A = -torch.exp(self.A_log)                        # [N], 负实部
        # selective scan (教学: 逐 token, 慢)
        h = torch.zeros(B_, self.N, device=u.device)
        ys = []
        for t in range(L):
            Abar = torch.exp(dt[:,t] * A)                 # [B,N]
            Bbar = dt[:,t] * Bb[:,t]                       # [B,N]
            h = Abar * h + Bbar * x[:,t].unsqueeze(-1)    # 不对, x是E维; 真实: 每个E通道独立N维SSM
            # 简化: 这里把E维当成batch, 真实实现要把 [B,E,N] 一起算
            ys.append((Cc[:,t] * h).sum(-1, keepdim=True))
        y = torch.cat(ys, dim=1) + self.D_res * x
        y = y * F.silu(z)                                 # 门控
        return u + self.out_proj(y)
```

> 注：上面是教学版（逐 token 循环，慢）。真实 Mamba 用 `mamba_ssm` 包的 CUDA `selective_scan_fn`，把 $[B, L, E, N]$ 的扫描并行化。

---

## 四、MoE 负载均衡算法详解

> 论文：Switch Transformer（Fedus et al., 2021），[arXiv:2101.03961](https://arxiv.org/abs/2101.03961)
> 论文：DeepSeekMoE: Towards Ultimate Expert Specialization（Dai et al., 2024-01），[arXiv:2401.06066](https://arxiv.org/abs/2401.06066)
> 论文：DeepSeek-V3（auxiliary-loss-free balancing + MTP），[arXiv:2412.19437](https://arxiv.org/abs/2412.19437)
> 论文：On DeepSeekMoE 理论分析（shared experts + sigmoid gating），[arXiv:2505.10860](https://arxiv.org/abs/2505.10860)
> 论文：Expert Choice Routing（Zhou et al., NeurIPS 2022），[arXiv:2202.09368](https://arxiv.org/abs/2202.09368)

Mixture-of-Experts（MoE）让模型总参数量大、单 token 计算量小（稀疏激活）。DeepSeek-V3 用 671B 总参但每 token 仅激活 37B。MoE 的数学核心是**路由（routing）**，而路由最大的工程难题是**负载均衡（load balancing）**。

### 4.1 基本 Top-K 路由（Mixtral / GShard）

设有 $N$ 个专家 $\{E_1, \ldots, E_N\}$，每个是独立的 FFN。对 token $u$，路由器（一个线性层 + softmax）算出分配概率：

$$
g(u) = \text{softmax}(W_g\, u) \in \mathbb{R}^{N}, \quad g_i(u) = \frac{\exp((W_g u)_i)}{\sum_j \exp((W_g u)_j)}
$$

Top-K 选择：选概率最大的 $K$ 个专家，输出：

$$
y(u) = \sum_{i \in \text{TopK}(g(u), K)} g_i(u)\, E_i(u)
$$

**Mixtral 8x7B**：$N=8$，$K=2$。每个 token 走 2 个专家。

### 4.2 ⭐ 负载不均的恶性循环（数学推导）

朴素 top-K 路由会**自发塌缩**。设专家 $i$ 当前被选中的频率为 $f_i$，被选中的 token 多 → 专家 $i$ 训练得多 → $E_i$ 质量提升 → 更多 token 倾向选它 → $f_i$ 更大……这是正反馈。

形式化：路由器对专家 $i$ 的 logit $l_i$ 更新近似为 $\Delta l_i \propto f_i \cdot \text{收益}_i$。若初始 $f_i$ 略大，$l_i$ 持续增长，最终 $\text{softmax}(l)$ 塌缩成 one-hot——**只有少数专家被用，其余饿死**。这就是「路由塌缩（routing collapse）」。

后果：
1. 有效专家数 $\ll N$，模型容量浪费（671B 模型实际只用几十 B）
2. 饿死的专家没训练，分布式训练时其所在 GPU 空转，浪费算力
3. 训练不稳定（少数专家过载）

### 4.3 Switch Transformer 的辅助损失均衡

Switch Transformer（$K=1$，每 token 只走 1 个专家）提出经典的 **auxiliary load balancing loss**：

$$
\mathcal{L}_{\text{aux}} = \alpha \cdot N \sum_{i=1}^{N} f_i \cdot P_i
$$

其中：
- $f_i = \frac{1}{T}\sum_{t=1}^{T} \mathbb{1}[\text{argmax}\, g(E_{i}(u_t)) = i]$：专家 $i$ 被**选中**的 token 比例（硬计数）
- $P_i = \frac{1}{T}\sum_{t=1}^{T} g_i(u_t)$：专家 $i$ 的**平均路由概率**（软分配）
- $\alpha$ 是权重（如 0.01），$N$ 是专家数

**为什么是 $f_i \cdot P_i$？** 看拉格朗日松弛：约束是「每个专家被选频率相等」$\Leftrightarrow f_i = 1/N$。当均匀时 $f_i = P_i = 1/N$，$\mathcal{L}_{\text{aux}} = N \cdot N \cdot (1/N)^2 = 1$（最小值，由 AM-GM 不等式 $f_i P_i \ge (\text{均衡时})$）。不均时 $> 1$，梯度推动路由器把概率重新摊开。

$f_i$ 用硬计数（不可微，取 $\arg\max$），$P_i$ 用软概率（可微，提供梯度），这是「直通估计」式的技巧。

### 4.4 DeepSeekMoE：细粒度专家 + 共享专家

DeepSeekMoE（2401.06066）的两个创新：

**(1) 细粒度专家分割（fine-grained segmentation）**：把 $N$ 个专家细分成 $mN$ 个更小的专家，激活 $mK$ 个。例：原本 $N=8, K=2$ → 细化成 $N'=64, K'=16$（每个专家小 8×）。

数学动机：$K$ 个专家的组合数 $\binom{N}{K}$，细化后 $\binom{mN}{mK} \gg \binom{N}{K}$，**可能的专家组合指数增长**，每个 token 能用更精细的「专家混合」表达。论文理论（2505.10860）证明这降低了专家估计的样本复杂度。

**(2) 共享专家（shared experts）**：固定 $K_s$ 个专家**始终激活**（不参与路由），专门捕获「公共知识」。路由只从 $mN - K_s$ 个 routed experts 里选 $mK - K_s$ 个。

$$
y(u) = \underbrace{\sum_{s=1}^{K_s} E_s^{\text{shared}}(u)}_{\text{公共知识}} + \underbrace{\sum_{i \in \text{TopK}(g(u))} g_i(u)\, E_i^{\text{routed}}(u)}_{\text{专业知识}}
$$

动机：避免每个 routed expert 都重复学习「the、is、的」这类公共模式（冗余），让 routed expert 专注差异化知识。

### 4.5 Expert Choice Routing（反向路由）

传统路由是「token 选 expert」。Expert Choice（Zhou et al., 2022）反转：**expert 选 token**。

设 $S = \text{softmax}(u W_g) \in \mathbb{R}^{T \times N}$（$T$ 个 token，$N$ 个专家）。传统：每行 top-K（每 token 选 $K$ expert）。Expert Choice：每列 top-$(T \cdot K / N)$（每 expert 选固定数量 token）。

数学优势：**天然负载均衡**——每个 expert 恰好处理 $TK/N$ 个 token，无需 auxiliary loss。代价：失去因果性（expert 看全部 token 才能选），自回归生成时不直接适用。

### 4.6 ⭐ DeepSeek-V3 的 Auxiliary-Loss-Free 负载均衡

V3（2412.19437）发现 auxiliary loss 有副作用：它会干扰主任务梯度，导致质量下降。提出 **auxiliary-loss-free** 方案——用**偏置项（bias）**而非损失来调节路由：

$$
g_i(u) = \text{softmax}_i\!\big((W_g u)_i + b_i\big), \quad \text{TopK over } g_i
$$

其中 $b_i$ 是**每个专家一个可学习偏置**，但它**不参与梯度反传**（无 $\nabla_{b_i}$）。取而代之的是一个**显式更新规则**：

$$
b_i \mathrel{\leftarrow} b_i + \gamma\, (\bar f_i - 1/N)
$$

其中 $\bar f_i$ 是专家 $i$ 的实际被选频率（EMA 平滑），$\gamma$ 是更新步长，$1/N$ 是目标频率。

**直觉**：如果专家 $i$ 被选太多（$\bar f_i > 1/N$），就**降低**它的偏置 $b_i$（让它没那么容易被选）；反之提高。这是一个**控制论式的反馈回路**，把负载均衡从「梯度优化」降级成「直接调旋钮」——不影响主损失梯度，零干扰。

V3 报告：auxiliary-loss-free 在保持均衡的同时，质量优于 auxiliary loss 方案。这是 2024–2026 MoE 训练的一个标准 trick，被后续许多模型借鉴。

### 4.7 DeepSeek-V3 的 Multi-Token Prediction (MTP)

顺带提一个 V3 的另一个架构创新：MTP。传统 next-token prediction 只预测 $u_{t+1}$，MTP 额外预测 $u_{t+2}, \ldots, u_{t+k}$（用 $k$ 个串行的预测头）。这给训练提供更密集的信号（一个 token 见到多个未来目标），提升数据效率。推理时可丢弃多余的 MTP 头（speculative decoding 风格加速），或保留做 beam search。这是 V3「2.788M H800 小时训完 671B」效率的一部分来源。

---

## 五、Grouped Query Attention (GQA)

> 论文：GQA: Training Generalized Multi-Query Transformer Models from Multi-Head Checkpoints，Ainslie et al., 2023，[arXiv:2305.13245](https://arxiv.org/abs/2305.13245)
> 论文：Fast Transformer Decoding with One Summary Vector per Head (MQA)，Shazeer, 2019

### 5.1 从 MHA 到 MQA 到 GQA 的统一视角

把注意力的「Q/K/V 头数」参数化。设 query 头数 $n_h$（固定），KV 头数 $n_{kv}$：

- **MHA**：$n_{kv} = n_h$。每对 Q-K 独立。质量最高，KV cache 最大。
- **MQA**：$n_{kv} = 1$。所有 Q 头共享一组 K/V。KV cache 最小，质量掉点明显。
- **GQA**：$n_{kv} = n_g$，$1 < n_g < n_h$。$n_g$ 组，每组内 Q 头共享 K/V。中间方案。

数学上，GQA 把 $n_h$ 个 Q 头分成 $n_g$ 组，组 $g$ 的所有 Q 头用同一对 $K_g, V_g$：

$$
\text{head}_{i}(Q) = \text{Attn}(Q_i,\ K_{\lfloor i / (n_h/n_g) \rfloor},\ V_{\lfloor i / (n_h/n_g) \rfloor})
$$

KV cache：$\propto n_{kv}$。GQA 把它从 $n_h$ 降到 $n_g$，比例 $n_h / n_g$。

### 5.2 GQA 的质量–速度 tradeoff

GQA 论文的核心实验：把一个已训练的 MHA 模型，按 Q 头相似度聚类成 $n_g$ 组（avg-uptraining），转成 GQA 微调。结果：
- $n_g = n_h$（MHA）：质量上限
- $n_g = 1$（MQA）：质量下限，但推理最快
- **$n_g = 8$ 左右是甜点**：质量几乎追平 MHA，KV cache 减 8× 以上

Llama 2 70B、Llama 3 全系列、Mistral 7B 都用 GQA（典型 $n_h=32, n_g=8$）。

### 5.3 为什么 GQA 不像 MLA 那样激进

GQA 是「数量维度」压缩（减少 KV 头数），MLA 是「维度维度」压缩（低秩 latent）。GQA 实现极简（改个 reshape），工程风险低，是当前**默认选择**；MLA 压缩更狠但实现复杂（吸收技巧 + RoPE 旁路），目前主要 DeepSeek 系在用。二者不互斥——理论上可以组合（GQA 的每组内再用 latent 压缩），但尚无主流模型这么做。

---

## 六、Sliding Window Attention

> 论文：Mistral 7B，Jiang et al., 2023，[arXiv:2310.06825](https://arxiv.org/abs/2310.06825)
> 论文：Longformer，Beltagy et al., 2020，[arXiv:2004.05150](https://arxiv.org/abs/2004.05150)
> 论文：BigBird，Zaheer et al., 2020，[arXiv:2007.14062](https://arxiv.org/abs/2007.14062)

### 6.1 Sliding Window 的数学

每个 token 只 attend 窗口 $w$ 内的前序 token（causal 版）：

$$
A^{\text{SWA}}_{t,i} = \begin{cases} \text{softmax}(q_t^\top k_i / \sqrt{d}) & t - w < i \le t \\ 0 & \text{否则} \end{cases}
$$

每层 attention 复杂度从 $O(L^2 d)$ 降到 $O(L w d)$，对 $L$ 线性。KV cache 也只保留最近 $w$ 个 token（FIFO）。

**多层堆叠的等效感受野**：$N$ 层 SWA 堆叠后，顶层 token 能「间接看到」$N w$ 个 token 前（信息逐层向外扩散）。Mistral 7B 用 $w=4096$，32 层 → 理论感受野 $32 \times 4096 = 131072$，配合 8K 训练上下文够用。

### 6.2 Longformer / BigBird 的稀疏模式

- **Longformer**：sliding window + 少量「global token」（如 [CLS]、文档标题），全局 token attend 所有位置。模式 = 窗口带 + 全局列。
- **BigBird**：sliding window + global + **随机连接**。理论上证明这种稀疏模式是 Turing-complete 的（能模拟任意图灵机），且有 $O(L)$ 复杂度。

### 6.3 Mistral 8x7B 的混合（SWA + full）

Mistral 8x7B（MoE）部分层用 sliding window，部分层用 full attention，混合配置。这是「局部细粒度 + 全局粗粒度」的工程平衡——后来 NSA 把这个思路系统化了（见第七节）。

---

## 七、Native Sparse Attention (NSA, DeepSeek)

> 论文：Native Sparse Attention: Hardware-Aligned and Natively Trainable Sparse Attention，Yuan et al., DeepSeek，[arXiv:2502.11089](https://arxiv.org/abs/2502.11089)（2025-02-16）

NSA 是 DeepSeek 2025 年提出的**可端到端训练的稀疏注意力**。与 Longformer/BigBird（手工固定稀疏模式）不同，NSA 的稀疏模式是**可学习的**，且从预训练阶段就稀疏（natively trainable），而非事后补救。

### 7.1 NSA 的三分支结构

NSA 把每个 token 的注意力分成三个并行分支，最后加权融合：

$$
O = g_1 \cdot O^{\text{comp}} + g_2 \cdot O^{\text{slct}} + g_3 \cdot O^{\text{slide}}
$$

其中 $g_1, g_2, g_3$ 是学习到的门控（对每个 query 独立）。

**(1) 压缩分支（Compression / coarse-grained）**：把历史 token 分块（block size $l$），每块用 MLP 压缩成一个「摘要 token」：

$$
\tilde K_j = \text{MLP}_K(K_{(j-1)l+1 : jl}), \quad \tilde V_j = \text{MLP}_V(V_{(j-1)l+1 : jl})
$$

然后 query 对这些摘要做 attention——**全局粗粒度上下文**。

**(2) 选择分支（Selection / fine-grained）**：根据 query 与各摘要块的相关性，**选出 top-n 个最重要的块**，对它们做 full attention（不压缩）——**局部细粒度精度**。这是「内容相关」的稀疏（像 attention 本身的 retrieval，但只在块级）。

**(3) 滑动窗口分支（Sliding）**：标准的局部 sliding window attention——**当前邻域的精确信息**。

### 7.2 NSA 的硬件对齐

NSA 的关键工程贡献：三个分支都设计成**arithmetic intensity 平衡**的（计算/访存比合理），在现代 GPU/Tensor Core 上跑得满。具体：
- Compression 是块级 attention，矩阵规整，适合 Tensor Core
- Selection 的 top-n 选择用高效的 gather 操作
- 整体用 tiling 配合 FlashAttention 风格的 SRAM 分块

论文报告：在 64K 序列上，解码、前向、反向都显著快于 full attention，且**质量持平甚至略优**（因为可学习的稀疏模式比手工的更合理）。

### 7.3 NSA 与 Linear Attention 的关系

NSA 仍保留 softmax（不是 linear attention），只是稀疏化。它的贡献在于「稀疏模式可端到端学习」，而 Lightning Attention / Mamba 是改变注意力函数本身（线性化/SSM）。两者正交，理论上可组合（如 NSA + MLA 已有探索：[arXiv:2511.00819](https://arxiv.org/abs/2511.00819)）。

---

## 八、注意力/序列模型家族对比表

| 架构 | 核心机制 | 训练复杂度 | 推理复杂度/token | KV/状态大小 | 代表模型 | 主要论文 |
|------|---------|-----------|----------------|-----------|---------|---------|
| **MHA** | 全 softmax attention | $O(L^2 d)$ | $O(L d)$ | $2Nd$ | GPT-3, Llama 1 | Vaswani 2017 |
| **GQA** | 分组共享 KV | $O(L^2 d)$ | $O(L d)$ | $2 N_{kv} d$ | Llama 2/3, Mistral | [2305.13245](https://arxiv.org/abs/2305.13245) |
| **MQA** | 单 KV | $O(L^2 d)$ | $O(L d)$ | $2d$ | PaLM, Falcon | Shazeer 2019 |
| **MLA** | 低秩 latent KV + 吸收 | $O(L^2 d)$ | $O(L d_c)$, $d_c\!\ll\!d$ | $d_c$ | DeepSeek-V2/V3/R1 | [2405.04434](https://arxiv.org/abs/2405.04434) |
| **SWA** | 局部窗口 | $O(L w d)$ | $O(w d)$ | $2 w d$ | Mistral, Longformer | [2310.06825](https://arxiv.org/abs/2310.06825) |
| **NSA** | 学习式三分支稀疏 | $\approx O(L \log L)$ | $\approx O(L d)$ (亚线性) | 稀疏 | DeepSeek NSA | [2502.11089](https://arxiv.org/abs/2502.11089) |
| **Linear Attn** | 核化 $\phi(Q)(\phi(K)^\top V)$ | $O(L d^2)$ | $O(d^2)$ | $d^2$ (状态矩阵) | Linear Transformer | [2006.16236](https://arxiv.org/abs/2006.16236) |
| **Lightning Attn** | chunk 分解 linear attn | $O(L d^2)$ | $O(d^2)$ | $d^2$ | MiniMax-01/M1 | [2405.17381](https://arxiv.org/abs/2405.17381) |
| **S4** | 结构化 SSM (HiPPO+DPLR) | $O(L N + N)$ | $O(N)$ | $N$ | S4 | [2111.00396](https://arxiv.org/abs/2111.00396) |
| **Mamba/S6** | 选择性 SSM | $O(L N)$ (parallel scan) | $O(N)$ | $N$ | Mamba, Jamba | [2312.00752](https://arxiv.org/abs/2312.00752) |
| **Mamba-2** | SSD (semiseparable) | $O(L N)$ | $O(N)$ | $N$ | Mamba-2 | [2405.21060](https://arxiv.org/abs/2405.21060) |

**读这张表的几个洞察：**
1. **Transformer 系（MHA/GQA/MLA/SWA/NSA）**保留 softmax，区别在「看多少、怎么共享 KV」。
2. **Linear/SMM 系（Linear Attn/Lightning/Mamba）**改变注意力函数本身，从 $O(L^2)$ 降到 $O(L)$，代价是表达力（需混合架构补）。
3. **推理状态大小**：Transformer 系随序列长（KV cache），Linear/SSM 系固定（$d^2$ 或 $N$）——这是 SSM 系在「无限长上下文」场景的根本优势。

---

## 九、混合架构（Jamba、Zamba）

> 论文：Jamba: A Hybrid Transformer-Mamba Language Model，Lieber et al., AI21，[arXiv:2403.19887](https://arxiv.org/abs/2403.19887)
> 论文：Zyphra Zamba2（Zyphra 技术 blog，无 arXiv；核心思想见 blog）

### 9.1 Jamba：Mamba + Transformer + MoE

Jamba（AI21, 2024）把三种模块交错堆叠：

```
[Mamba block] × a → [Transformer attention block] × b → 重复
```

外加 MoE FFN（部分层用 MoE，部分用 dense FFN）。设计动机：
- **Mamba 层**：处理长程依赖，$O(L)$，无 KV cache 增长
- **Transformer 层**：每隔几层插一层，提供「精准检索」（attention 的强项是精确回忆特定 token，Mamba 弱）
- **MoE**：扩容不增算力

Jamba 关键配置：约 1:8 的 Transformer:Mamba 比例（大部分层是 Mamba，稀疏插 Transformer）。实测：256K 上下文质量接近纯 Transformer，显存占用远低。

数学上，Jamba 的混合理由来自 SSD 对偶（3.7 节）：既然 SSM 和 attention 是同源（semiseparable vs dense matrix），那它们的混合就是「结构化矩阵 + 稠密矩阵」的混合——稠密层补结构化层无法表达的精确关联。

### 9.2 Zamba（Zyphra）

Zamba（Zyphra）思路类似但更激进：用一个**共享的 Transformer attention 块**（参数共享）穿插在 Mamba block 之间。即所有「Transformer 层」共用同一组 Q/K/V 权重——大幅省参数。Zamba2 进一步优化了 MoE 部分。定位是「小而精」（7B–13B 量级）。

### 9.3 何时用混合 vs 纯架构

| 场景 | 推荐架构 | 理由 |
|------|---------|------|
| 短上下文（<8K）、要最强质量 | 纯 Transformer + GQA/MLA | attention 的表达力上限最高 |
| 长上下文（>128K）、显存受限 | 混合（Jamba 式）或纯 Mamba | SSM 的固定状态省显存 |
| 超长上下文（>1M）、需常量速度 | Lightning Attention（MiniMax）| chunk 分解保证速度恒定 |
| 多模态（视频/音频，超长 token） | Mamba 或混合 | 媒体 token 序列极长，$O(L)$ 必须 |
| Agent / 工具调用（需精确检索） | 纯 Transformer 或高 Transformer 比例混合 | 精确回忆历史步骤，attention 强 |

经验法则：**attention 擅长「精确回忆」，SSM/Linear 擅长「长程摘要」**。任务要前者就多 attention，要后者就多 SSM。

---

## 十、架构选择决策树

```
你的序列长度 L 和模态？
│
├─ L < 8K, 纯文本
│   └─► Transformer + GQA（默认）。Llama 3 风格。
│        质量优先，KV cache 不是瓶颈。
│
├─ 8K ≤ L ≤ 128K, 纯文本
│   ├─ 要极致质量、显存够
│   │   └─► Transformer + MLA（DeepSeek 风格）
│   │        或 Transformer + GQA + SWA（Mistral 风格）
│   └─ 显存紧张、可接受小幅掉点
│       └─► 混合 Jamba 式（Mamba 主 + 少量 attention）
│
├─ 128K < L ≤ 1M
│   ├─► NSA（学习式稀疏）or Lightning Attention（MiniMax）
│        或 Mamba-2（SSD 大状态）
│
├─ L > 1M（超长文档、视频、基因组）
│   └─► 纯 Mamba / 纯 Lightning Attention
│        Transformer 在这个尺度显存爆，不可行
│
├─ 多模态（视频/音频 token 海量）
│   └─► Mamba 或 Lightning Attention（线性复杂度必须）
│
└─ Agent / 需精确检索历史
    └─► Transformer 系（attention 检索强）
         可配 MLA 省显存，但不要纯 SSM
```

**硬件维度补充：**
- 显存带宽受限（如边缘部署）：优先 SSM（状态小）
- 算力受限（如低成本训练）：MoE（稀疏激活）+ 任意 attention
- 推理延迟敏感：SSM/Lightning（$O(1)$ per token）> Transformer（$O(L)$ per token）

---

## 十一、给「应用数学研究型工程师」的建议

基于你的目标（ML 理论 / 概率随机过程 / 数值分析 / 优化理论方向，每周 10–20h），这套架构数学是绝佳的研究切入点。三个层次的建议：

### 11.1 工程层：实现两个 minimal

**(1) Minimal Mamba（1 天）**
用 NumPy 实现一个 S6 selective scan，在 toy 序列（如 copy task、induction task）上验证它比朴素 RNN 强。关键点：
- 手写 $\bar A_t = \exp(\Delta_t A)$ 的递推
- 实现「选择性」：让 $\Delta_t$ 依赖输入，观察模型能否学会「遇到特定 token 就重置状态」
- 对比：固定 $\Delta$（退化成 S4）vs 可学 $\Delta$（S6），看在 induction task 上的差异

进阶：接上 PyTorch autograd，在 sWAG/enwik8 小语料上训一个 tiny Mamba（$D=64$），对比同规模 Transformer。

**(2) Minimal MLA（半天）**
实现一个带吸收技巧的 MLA 推理。关键点：
- 训练时正常上采样 K/V
- 推理时切到「只 cache latent + 吸收 $W^{UK}$ 到 query」路径
- 量测两种路径的 KV cache 大小和延迟

这两个实现会让你**从公式理解跃迁到工程直觉**——你会亲身体会到 selective scan 为什么需要 CUDA、吸收技巧为什么省访存。

### 11.2 数学层：SSM 表达力的开放问题

这是真正的研究入口。SSM 的表达力理论还远未成熟，几个有深度的方向：

**(1) SSM 的近似下界**
SSM 能逼近的函数类是什么？已知：线性时不变 SSM（S4）等价于「指数衰减核的卷积」，能逼近的函数受 $A$ 的谱限制。但**选择性 SSM（Mamba）的函数类远未被刻画**。

具体问题：给定一个需要「精确计数」的任务（如「第 $n$ 个括号是否闭合」），SSM 需要多大的状态维度 $N$ 才能解？现有结果（如 Sarrof et al., 2025 的工作）暗示 SSM 在这类「需要精确栈」的任务上**本质上弱于 attention**——这是一个可证明的分离。你能形式化这个下界吗？

**(2) SSD 对偶的泛化**
Mamba-2 证明 SSM ≈ semiseparable attention matrix。问题：**还有哪些矩阵结构能对应高效的序列模型？** 比如 quasiseparable、banded、低秩 + 稀疏……每发现一种结构 + 对应的 $O(L)$ 算法，就是一个新架构。这是代数（矩阵分析）与 ML 的交叉。

**(3) Linear Attention 的核函数最优性**
$\phi(\cdot)$ 选 ELU+1 是经验选择。**理论上最优的核是什么？** 这与再生核希尔伯特空间（RKHS）、核方法近似（random features）深度相关。能否构造一个 $\phi$ 使 linear attention 的表达力逼近 softmax？这是函数分析 + ML。

### 11.3 路径层：把架构数学纳入你的 6–8 年规划

这些架构的数学（线性代数、动力系统、核方法、矩阵结构）恰好落在你「应用数学研究型工程师」的候选方向交集：
- **动力系统 + 数值分析**：SSM 的离散化（ZOH、双线性）、HiPPO 矩阵的稳定性、parallel scan 的数值误差——全是数值分析问题
- **优化理论**：MoE 路由的均衡（博弈论/凸优化）、auxiliary-loss-free 的反馈控制——控制论 + 优化
- **概率/信息论**：Linear Attention 核函数与 KL 散度、attention 的信息瓶颈——信息论

建议：把本章当作「读论文的脚手架」。选一个方向（我推荐 **SSM 表达力下界**，因为它开放、深刻、与你的数学审美契合），深读 Mamba / Mamba-2 原文 + 几篇 SSM 理论论文（如 On the Expressive Power of SSMs），用半年时间写出一篇有形式化结果的 note。这是从「学架构」到「研究架构」的跨越。

---

## 📌 进一步阅读

**核心论文（全部一手核实）：**
1. DeepSeek-V2（MLA 原始论文）：[arXiv:2405.04434](https://arxiv.org/abs/2405.04434)
2. DeepSeek-V3（auxiliary-loss-free + MTP）：[arXiv:2412.19437](https://arxiv.org/abs/2412.19437)
3. DeepSeek-V3 硬件视角（ISCA 2025）：[arXiv:2505.09343](https://arxiv.org/abs/2505.09343)
4. DeepSeekMoE（细粒度 + 共享专家）：[arXiv:2401.06066](https://arxiv.org/abs/2401.06066)
5. DeepSeekMoE 理论分析：[arXiv:2505.10860](https://arxiv.org/abs/2505.10860)
6. S4（结构化 SSM 开山）：[arXiv:2111.00396](https://arxiv.org/abs/2111.00396)
7. Mamba / S6（选择性 SSM）：[arXiv:2312.00752](https://arxiv.org/abs/2312.00752)
8. Mamba-2（SSD 对偶）：[arXiv:2405.21060](https://arxiv.org/abs/2405.21060)
9. Linear Attention（Katharopoulos）：[arXiv:2006.16236](https://arxiv.org/abs/2006.16236)
10. Lightning Attention（TransNormerLLM）：[arXiv:2405.17381](https://arxiv.org/abs/2405.17381)
11. Lightning Attention-2：[arXiv:2401.04658](https://arxiv.org/abs/2401.04658)
12. MiniMax-01（Lightning Attention 工业化）：[arXiv:2501.08313](https://arxiv.org/abs/2501.08313)
13. MiniMax-M1（Lightning + 推理）：[arXiv:2506.13585](https://arxiv.org/abs/2506.13585)
14. NSA（Native Sparse Attention）：[arXiv:2502.11089](https://arxiv.org/abs/2502.11089)
15. GQA：[arXiv:2305.13245](https://arxiv.org/abs/2305.13245)
16. Switch Transformer：[arXiv:2101.03961](https://arxiv.org/abs/2101.03961)
17. Expert Choice Routing：[arXiv:2202.09368](https://arxiv.org/abs/2202.09368)
18. Mistral 7B（SWA + GQA）：[arXiv:2310.06825](https://arxiv.org/abs/2310.06825)
19. Jamba（Mamba+Transformer+MoE 混合）：[arXiv:2403.19887](https://arxiv.org/abs/2403.19887)
20. Kimi K2（澄清：MuonClip，非 Lightning Attention）：[arXiv:2507.20534](https://arxiv.org/abs/2507.20534)

**配套阅读：**
- FlashAttention（理解 MLA/NSA 的 tiling 思想来源）：[arXiv:2205.14135](https://arxiv.org/abs/2205.14135)
- HiPPO（S4 的记忆矩阵来源）：[arXiv:2008.07669](https://arxiv.org/abs/2008.07669)
- Zoo of SSM/Lin-Attn 综述：搜索 "state space models survey 2025"

---

## ✍️ 思考题（5 道）

**题 1（MLA 吸收技巧）**：MLA 的吸收技巧把 $W^{UK}$ 从 key 侧移到 query 侧（$\tilde q = W^{UK\top} q$）。证明这个代数等价性，并解释：为什么带 RoPE 的 key 部分 $k^{(R)}$ **不能**被吸收？（提示：RoPE 是 $q, k$ 同时乘以位置相关的旋转矩阵 $R_t$，$\langle R_t q, R_i k \rangle = q^\top R_t^\top R_i k$，这个 $R_t^\top R_i$ 依赖两个位置，无法吸收进单侧。）

**题 2（Linear Attention 的表达力极限）**：考虑「Induction Heads」任务——序列中出现 `A B ... A` 时，模型应输出 `B`（回忆 A 后面跟什么）。证明：朴素 Linear Attention（$\phi = \text{ELU}+1$，固定状态矩阵 $S$）**无法**精确完成这个任务，而 softmax attention 可以。（提示：Linear Attention 的状态 $S$ 是所有历史 $(k,v)$ 对的无权累加，无法「按 query 选择性检索」某个特定的 $A \to B$ 关联；softmax 的 $\exp(q^\top k)$ 能放大匹配的 key。这就是 Mamba 论文里「content-based reasoning」弱点的具体体现。）

**题 3（Mamba 选择性的必要性）**：在选择性 SSM 中，$\Delta_t = \text{softplus}(\text{Linear}(u_t))$。考虑一个「选择性复制」任务：序列里有特殊 token `<ignore>`，模型应忽略 `<ignore>` 之前的内容。证明：若 $\Delta_t$ 固定（S4），SSM 无法做选择性遗忘；若 $\Delta_t$ 可变（S6），模型可以学会让 `<ignore>` 触发大 $\Delta_t$ → $\exp(\Delta A)$ 衰减 → 遗忘。请写出当 $\Delta_t \to \infty$ 时状态 $x_t$ 的极限行为。

**题 4（MoE 均衡损失的最优性）**：推导 Switch Transformer 的 $\mathcal{L}_{\text{aux}} = \alpha N \sum_i f_i P_i$ 在 $f_i = P_i = 1/N$ 时取最小值 1，并用 AM-GM 或拉格朗日法证明这是全局最小。然后讨论：为什么 DeepSeek-V3 放弃它改用 auxiliary-loss-free（bias 更新）？（提示：$\mathcal{L}_{\text{aux}}$ 的梯度会注入主损失，干扰表示学习；bias 更新是「外环控制」，零梯度干扰。）

**题 5（SSD 对偶的研究延伸）**：Mamba-2 证明 SSM 对应 semiseparable matrix。请回答：(a) 什么是 semiseparable matrix（给出准确定义，秩 ≤ $r$ 的条件）？(b) Attention 的矩阵 $\text{softmax}(QK^\top)$ 是稠密的，它属于哪个已知的结构化矩阵类？（提示：低秩——因为 $QK^\top$ 本身 rank ≤ $d$，但 softmax 破坏了低秩。）(c) 提出一个**新的**矩阵结构（如 banded semiseparable、Toeplitz + 低秩），它能否对应一种新的 $O(L)$ 序列模型？这是开放题，目的是训练你「从矩阵结构反推算法」的研究直觉。

---

> **本章小结**：现代大模型架构的本质，是**在「表达力」与「计算/访存成本」之间寻找数学最优的折中**。Transformer 用稠密 $O(L^2)$ 矩阵换最强表达力；Mamba/Linear Attention 用结构化矩阵（semiseparable / 低秩）换 $O(L)$ 效率；MLA 用低秩分解换 KV cache 压缩；MoE 用稀疏激活换「大模型小算力」。理解这些折中的数学——线性代数、动力系统、核方法、矩阵结构——你就掌握了「设计下一个架构」的语言。对一个目标是数学专家的工程师，这恰恰是最肥沃的研究土壤。

<!-- delegate 直接写入，2026-07-20 -->
