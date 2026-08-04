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

---

## 📌 下一步

[03-RWKV与现代RNN](03-RWKV与现代RNN.md)——另一种 O(n) 路线：RWKV 把 RNN 的推理效率和 Transformer 的训练并行结合，靠"线性递推 + WKV 机制"做到两全。

## ✍️ 练习

1. Performer 的随机特征数 $m$ 从 64 增到 256，近似误差降多少？显存增多少？
2. 为什么 Linear Attention 在"精细检索"任务上比标准 attention 差？（提示：softmax 的锐度帮助聚焦，线性核的钝角模糊了区分。）
