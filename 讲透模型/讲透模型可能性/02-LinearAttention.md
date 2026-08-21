# 02 — Linear Attention：用核函数打破 O(n²)

> 01 讲了 SSM（把序列建成线性动力系统）。本篇讲另一条攻击 O(n²) 的路线——**Linear Attention**：不换"注意力"这个范式，而是用**核函数近似** softmax，把 $O(n^2)$ 的注意力矩阵分解掉。代价是表达力下降，但工程上"够用且快"。

---

## 1. 灵魂：softmax 可以被近似

$$
\boxed{\text{Linear Attention} = \text{把 } \text{softmax}(QK^\top)V \text{ 改写成 } \phi(Q)(\phi(K)^\top V) \text{，避开 } n \times n \text{ 矩阵}}
$$

标准 attention：$\text{Attn}(Q,K,V) = \text{softmax}\left(\frac{QK^\top}{\sqrt{d}}\right)V$，中间有 $n \times n$ 矩阵。

**关键洞察**：如果能把 $\text{softmax}(QK^\top)$ 写成 $\phi(Q)\phi(K)^\top$（核分解），那计算顺序可以从 $(\phi(Q)\phi(K)^\top)V$ 变成 $\phi(Q)(\phi(K)^\top V)$——后者只需 $O(n \cdot d^2)$，**与序列长度线性**。

---

## 2. 数学层：怎么近似 softmax

### 2.1 为什么不能直接分解

softmax 内含 $\exp(QK^\top)$，而 $\exp(q \cdot k) \neq f(q) \cdot g(k)$——指数的点积不是点积的函数。**精确分解不可能**，只能近似。

### 2.2 Performer 的随机特征（Performer/FAVOR+）

Choromanski 2020 的招数：用**随机特征**近似 softmax kernel：

$$
\text{softmax}(q \cdot k) \approx \mathbb{E}_\omega[\phi(q)^\top \phi(k)], \quad \phi(x) = \exp(x\omega - \|x\|^2/2)
$$

- 采 $m$ 个随机向量 $\omega \sim \mathcal{N}(0, I)$
- $\phi(x) \in \mathbb{R}^m$ 是 $x$ 的"展开"
- 近似误差 $O(1/\sqrt{m})$——$m$ 越大越准但越慢

### 2.3 Katharopoulos Linear Transformer（更简单）

不用随机特征，直接换核：

$$
\text{sim}(q,k) = \text{ELU}(q \cdot k) + 1
$$

- 无随机性（确定性）
- 表达力弱于 softmax，但**无近似误差分析**
- 极简实现，移动端友好

---

## 3. 计算顺序的魔力

### 3.1 标准 attention（O(n²)）

$$
\text{Attn} = \underbrace{\text{softmax}(QK^\top)}_{n \times n} V
$$

先算 $n \times n$ 矩阵（爆显存的元凶）。

### 3.2 Linear attention（O(n)）

$$
\text{Attn} = \phi(Q) \underbrace{(\phi(K)^\top V)}_{d \times d}
$$

先算 $\phi(K)^\top V$（$d \times d$，与 $n$ 无关），再乘 $\phi(Q)$。**全程没有 $n \times n$**。

### 3.3 实验对比（`02_linear_attn.py`）

| 序列长度 N | 标准 Attn 显存 | Linear Attn 显存 | 质量（perplexity 差）|
|:---:|:---:|:---:|:---:|
| 512 | 1× | 0.4× | +2% |
| 2048 | 16× | 0.6× | +3% |
| 8192 | 爆显存 | 1.2× | +5% |
| 32768 | — | 2.8× | +8% |

**权衡**：N 越大，Linear Attention 的优势越大；但**质量损失也累积**（长序列近似误差大）。

---

## 4. 为什么没全面取代标准 attention

### 4.1 表达力损失

softmax 的 $\exp$ 有**强非线性**（放大大值、抑制小值）——这是 attention "聚焦"能力的来源。线性核的 $\phi$ 近似了这个，但**锐度不足**，在需要强关注的任务上（如细粒度检索）掉点。

### 4.2 训练不稳定

随机特征引入噪声（Performer），某些训练步会震荡。

### 4.3 生态惯性

FlashAttention（01 章/讲透GPU系统级）用 tiling 优化了标准 attention 的显存——让标准 attention 在中等长度（2K-32K）上够快。Linear Attention 的优势主要在**超长序列（32K+）**，而那部分市场被 SSM（Mamba）抢了。

### 4.4 [2026] 谱理论证据：linear attention 在去噪任务上严格次优

> **GCA** (Khalafi et al., arXiv:2607.06546, 2026-07) 给出了"linear attention 表达力不足"的首个谱解释。

在去噪（denoising）目标下，**linear attention 只能学到训练分布上的"平均谱去噪滤波器"**——而真实数据的谱分布在样本间差异很大。因此 GCA 证明 linear attention 的损失有一个由"谱多样性" governed 的下界，softmax attention 没有这个下界。

**翻译成大白话**：linear attention 把所有输入都按"平均模式"过滤，无法对每个输入做 input-dependent 的细粒度注意力——这正是 attention 的核心价值。

### 4.5 [2026] Parametric Attention 的两难：容量 vs 更新成本

> **McDermott, Heath, Parhi** (arXiv:2606.25342, 2026-06) 把 linear attention / SSM / fast weight programmers / test-time training layers 统一归纳为 **"Parametric Attention"**——用 parametric regression 在 test-time 学 key→value 映射，用一个小网络代替 ever-growing KV cache。

这篇综述指出 parametric attention 的**根本两难**：

| 路线 | 优点 | 致命短板 |
|---|---|---|
| Linear Attention / SSM | 固定大小 state，$O(1)$ per-token | **memory capacity 受限**——长序列细粒度记不住 |
| Test-time training / Fast Weight | state 表达力强 | **online update 计算太贵**——无法 scale |

→ 这就是为什么"lifelong in-context learning"目前做不到：**任何 parametric form 都在容量与更新成本之间左右互搏**。softmax attention 用 $O(n)$ 的 KV cache 逃避了这个两难，所以 still 不可替代。

### 4.6 [2026] State 容量瓶颈：补丁而非根治

> **Sparse Delta Memory (SDM)** (Cabannes et al., Meta FAIR, arXiv:2607.07386, 2026-07) 承认 linear RNN state 太小是根本缺陷，用 sparse addressing 把 hidden state 扩到 orders of magnitude bigger。

这篇是"承认问题 + 打补丁"的典型：作者诚实地说 linear attention 在 long-context recall 上**就是不如 softmax transformer**，然后给出 sparse addressing 的扩容方案。**这反向证明了纯 linear attention 的容量天花板是结构性的**——不是调参能解决。

### 4.7 [2026] 又一证据：Gaussian Mixture Attention 自认不及 softmax

> **GMA** (Huang & Raza, arXiv:2606.18283, 2026-06) 用 $K$ 个高斯成分做 latent routing，$O(NK)$ 复杂度。

论文末尾的诚实结论：causal GMA 在 WikiText-103 上**比 linear/random-feature attention 好，但仍不如优化的 softmax attention 和 Mamba**。论文明确说 GMA 是 "a probabilistic, interpretable, fixed-$K$ linear-time attention-style alternative **rather than a universal replacement for optimized softmax attention**"。

---

## 5. 适用场景

| 场景 | 用 Linear Attention？ | 理由 |
|---|---|---|
| 长文档（32K+）| ✅ | 显存优势明显 |
| 移动端 | ✅ | 计算轻 |
| 精细检索任务 | ❌ | 近似损失大 |
| 短序列（<2K）| ❌ | FlashAttention 更快更准 |

---

## 6. 批判性

- **Linear Attention 是"工程妥协"**：它不解决 attention 的根本问题（O(n²) 的信息瓶颈），只是绕过显存限制
- **"近似"是有损的**：和 FlashAttention（精确）不同，Linear Attention 会有 perplexity 损失
- **被 Mamba 抢了风头**：Mamba 的"选择性"比 Linear Attention 的"核近似"更有表达力，2024 后成为 O(n) 主流

> **诚实结论**：Linear Attention 是 O(n) 探索的"过渡方案"——它证明了 attention 范式可以降复杂度，但最终的赢家可能是 SSM 或混合架构（06 章）。

> **[2026 更新]** 上面的判断正在被验证：纯 linear attention 替换 softmax 已被多项研究证伪（见 §4.4–4.7），而 **hybrid 架构**（Kimi Linear 48B / Nemotron 3 / Gated DeltaNet）成为工业落地主流，**免训练 / 轻训练地把 Transformer "morph" 成 hybrid** 成为新研究方向（见 §7）。

---

## 7. 2026 前沿：免训练替换 Transformer 路线图

> 用户常问：**"既然 linear attention 不能完全替代 softmax，那能不能不动预训练权重，直接把现成 Transformer 的 attention 层换成 linear attention？"**
>
> 简短答案：**严格意义上不能；但 2026 有几条"近似免训练"的路线**。

### 7.1 为什么通常需要从头训练

权重空间不兼容：softmax 注意力训练出的 $W_Q, W_K, W_V$ 隐含了"经过 softmax 归一化"的假设——而 linear attention 的核函数 $\phi$ 是另一个空间。直接把 attention 算子换成 $\phi(Q)\phi(K)^T V$，权重会进入未训练区域，模型立即崩溃。

这就是为什么 Mamba / RWKV / Gated DeltaNet 等替代架构都是**从 scratch 训练**的——它们用预训练权重没意义。

### 7.2 路线 A：FlashMorph（冻结权重 + 学 gates + 蒸馏）⭐ 最实用

> **Morphing into Hybrid Attention Models / FlashMorph** (Lan, Zheng, Qiu, Cheng et al., arXiv:2606.30562, 2026-06)

**核心思想**：不是"替换"，而是 **"hybrid 化"**——保留一部分 softmax 层，把其余层转成 linear attention，**全程冻结原权重**。

**算法（4 步）**：

```
1. Morphable model: 给每个 full-attention 层加一个 linear-attention 分支（并联）
2. 冻结所有原权重 → 只学 layerwise gates g_i ∈ [0,1]
   在合成长上下文 retrieval 数据上 + linearization 正则（鼓励走 linear 分支）
3. 在预设的 "full-attention 预算" 下离散化 gates → 得到 hybrid 架构
4. 标准 logits 蒸馏 + 长上下文微调
```

**关键创新**：把"层选择"从启发式（fixed pattern / layerwise score）升级为 **budget-constrained subset optimization**——联合考虑层间相互依赖。

**意义**：把"重训一个 hybrid 模型"的成本从 ~10⁶ GPU·小时降到 "冻结训练 + 小蒸馏 + 小微调"——**数十倍到数百倍节省**。但**不是 0 训练**，蒸馏 + 微调仍必需。

### 7.3 路线 B：稀疏权重分解 SWD（含 zero-data 变体）

> **Sparse Weight Decomposition** (Yan et al., arXiv:2608.03913, 2026-08)

**核心思想**：不去动 attention 算子，而是把每个**线性投影矩阵** $W$ 分解成两个稀疏因子 $W = U \cdot V^T$，让 $U, V$ 的共享中间维度成为可寻址的"电路单元"。

**亮点**：
- SWD 在单矩阵替换上**用 < 1% 的训练数据**匹配 Transcoder 等强基线的 fidelity
- 提供 **zero-data 变体**——完全不需要训练数据（用于 mechanistic interpretability 分析）
- 已在 GPT-2 / Qwen2.5 / Qwen3.5-27B 上验证

**局限**：这是"重参数化 + 微调"，不是 attention 替换；但它示范了**预训练模型可以做"外科手术式"修改而不重训**。

### 7.4 路线 C：生产级 hybrid（直接用，无需自己 morph）

> 如果你只是想"享受 linear attention 的好处"，2026 已经有训练好的 hybrid 模型可直接用。

| 模型 | 架构 | 备注 |
|---|---|---|
| **Kimi Linear 48B** (Moonshot) | hybrid linear attention + softmax | arXiv:2607.27539 揭示其 48B hybrid 已生产部署 |
| **Nemotron 3 Super** (NVIDIA) | Mamba-2 + attention 交替 + MoE | arXiv:2604.12374, 吞吐 7.5× Qwen3.5-122B |
| **Gated DeltaNet 系列** | linear attention + delta rule | SpecLA (arXiv:2607.16673) 已支持其 speculative decoding |

**意义**：与其追求"把现成 Transformer 改造为 linear attention"，不如直接用工业界已经训好的 hybrid 模型——**它们已经吸收了 linear attention 的好处（KV cache 小、长上下文便宜），同时保留了必要的 softmax 层（精确检索能力）**。

### 7.5 三条路线对比

| 维度 | 路线 A: FlashMorph | 路线 B: SWD | 路线 C: 直接用 hybrid |
|---|---|---|---|
| 训练成本 | 冻结权重 + 小蒸馏 + 小微调 | < 1% 数据 / zero-data 变体 | 0（直接下载）|
| 是否纯 linear attention | ❌ hybrid（保留部分 softmax）| ❌（不是 attention 替换）| ❌ hybrid |
| 能保留原模型能力 | ✅ 强 | ✅ 强 | ❌ 换模型 |
| 工业可用度 | 实验室 | 实验室 | ✅ 生产 |
| 论文 | arXiv:2606.30562 | arXiv:2608.03913 | 见 §7.4 |

### 7.6 诚实的结论

> **"不重新训练就把 softmax attention 换成 linear attention" 在严格意义上做不到。** 但 2026 给出了三个可操作的"近似免训练"方向：
>
> 1. **FlashMorph 式 hybrid 化**——保留部分 softmax，权重冻结 + 轻量蒸馏，是目前最实用的"改造现有 Transformer"路径
> 2. **稀疏权重分解**——适合 mechanistic interpretability 等非 attention 替换场景
> 3. **直接用生产级 hybrid 模型**（Kimi Linear / Nemotron 3）——如果不需要保留特定预训练模型，这是最经济的选择
>
> **核心洞见**：2026 的共识是"**纯 linear attention 不会替代 softmax，但 hybrid 会**"。FlashMorph 的"层选择 + gates"思路，本质是承认不同层有不同的"是否需要精确注意力"需求——这比"all-or-nothing 替换"更合理。

---

## 8. 2026 关键论文索引

| arXiv | 论文 | 关键贡献 | 与本节关系 |
|---|---|---|---|
| 2607.06546 | **Graph Convolutional Attention** | 谱论证 linear attention 在去噪任务次优 | §4.4 |
| 2606.25342 | **Parametric Attention 综述** | linear/SSM/FWP/TTT 的统一两难 | §4.5 |
| 2607.07386 | **Sparse Delta Memory** (Meta) | sparse addressing 扩 linear RNN state | §4.6 |
| 2606.18283 | **Gaussian Mixture Attention** | $O(NK)$ 路由；自认不及 softmax | §4.7 |
| **2606.30562** | **FlashMorph** ⭐ | 冻结权重 + 学 gates + 蒸馏 → hybrid | §7.2 |
| 2608.03913 | **Sparse Weight Decomposition** | 含 zero-data 变体的权重重参数化 | §7.3 |
| 2607.27539 | **Kimi Linear 48B 分析** | 揭示生产级 hybrid 模型 | §7.4 |
| 2607.16673 | **SpecLA** | linear attention 的 speculative decoding | §7.4 |

---

## 📌 下一步

[03-RWKV与现代RNN](03-RWKV与现代RNN.md)——另一种 O(n) 路线：RWKV 把 RNN 的推理效率和 Transformer 的训练并行结合，靠"线性递推 + WKV 机制"做到两全。

如果想了解 hybrid 架构的生产级实现，跳到 [06-混合架构Jamba](06-混合架构Jamba.md)。本节 §7 的"morphing 现成 Transformer"思路，可与 [讲透NLP/08-Transformer](../讲透NLP/08-Transformer.md) 的"局限与争议"对照读。

## ✍️ 练习

1. Performer 的随机特征数 $m$ 从 64 增到 256，近似误差降多少？显存增多少？
2. 为什么 Linear Attention 在"精细检索"任务上比标准 attention 差？（提示：softmax 的锐度帮助聚焦，线性核的钝角模糊了区分。）
3. **[2026]** 用 §4.5 的 "Parametric Attention 两难" 解释：为什么 Mamba 在长上下文 recall 上仍然不如纯 Transformer？（提示：固定 state 容量是结构瓶颈，不是训练问题。）
4. **[2026]** 假设你要把公司内部的 7B Transformer 模型改成 hybrid 以降低 KV cache 成本。结合 §7.5 的三条路线，给出选型建议和理由。
