# 04 — 长卷积：Hyena 与 H3

> 01-03 讲了 SSM / Linear Attention / RWKV 三条 O(n) 路线。本篇讲第四条——**长卷积**：用一个超长的 1D 卷积核（长度 = 序列长）替代 attention。Hyena（2023）证明它能接近 attention 质量，H3（2023）进一步把"attention 能做的归纳任务"用卷积复刻。

---

## 1. 灵魂：卷积是 attention 的"穷表亲"

$$
\boxed{\text{长卷积} = \text{一个长度 } n \text{ 的滤波器扫过序列，O(n \log n) via FFT}}
$$

- attention：每个位置看所有位置（动态权重）
- 卷积：每个位置看固定 pattern（静态权重）
- 卷积更便宜，但**不能按内容调整权重**——这是它的根本局限

---

## 2. Hyena（2023）：把 attention 分解成递归卷积

Hyena 的核心：attention 的 $\text{softmax}(QK^\top)V$ 可以被近似成一连串**矩阵乘 + 长卷积**的交替：

$$
y = (H \cdot \text{diag}(v))(H \cdot x)
$$

其中 $H$ 是一个**隐式定义的长卷积核**（通过一个小的 MLP 生成滤波器系数）。

- 用 FFT 实现长卷积：$O(n \log n)$
- 没有 $n \times n$ 矩阵
- 质量接近 attention（在语言/代码任务上）

---

## 3. H3（2023）：用卷积复刻 induction head

H3（Hungry Hungry Hippos）的目标更具体：**复刻 attention 的"归纳头"能力**（in-context learning 的神经基础）。

结构：两个 SSM + 一个局部 attention：
- M2D（multiplicative 2-directional）：处理"key"信号
- M1D（multiplicative 1-directional）：处理"value"信号
- 最后一步用 attention 做精确匹配

**结果**：在 induction task 上匹配 attention，但更便宜。

---

## 4. 为什么长卷积没成主流

- **表达力天花板**：卷积是**线性时不变（LTI）**系统，不能像 attention 那样"按内容选位置"。Hyena 靠 MLP 生成核缓解，但根本局限在
- **被 Mamba 抢了风头**：Mamba 的"选择性 SSM"（让 A,B,C 随输入变）本质上实现了"内容相关的卷积"——比 Hyena 的固定核更强
- **工程成熟度**：FlashAttention 让标准 attention 够快，长卷积的速度优势被压缩

---

## 5. 批判性

- **长卷积是"过渡方案"**：它证明了"非 attention 也能做语言建模"，但最终被 SSM（Mamba）和混合架构（Jamba）取代
- **FFT 卷积的实际开销**：理论 O(n log n)，但 FFT 的常数因子大，短序列上反而比 attention 慢

> **诚实结论**：Hyena/H3 是 O(n) 探索的重要一步，但它们像是"attention 的近似"而非"超越 attention 的新范式"。真正的突破来自 Mamba 的选择性机制。

---

## 📌 下一步

[05-稀疏注意力](05-稀疏注意力.md)——不一刀切 O(n)，而是"让 attention 只看一部分"，工程实用主义路线。

## ✍️ 练习

1. 卷积是 LTI（线性时不变）系统。attention 是 LTV（线性时变）吗？为什么这个区别决定了谁更强？
2. Hyena 用 MLP 生成卷积核，让核"随数据变"。这算"内容相关"吗？和 Mamba 的选择性比，谁更彻底？
