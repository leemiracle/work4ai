# 11 — Hopfield Network 复兴：从联想记忆到 Attention

> 10 讲神经符号。本篇讲 **Hopfield Network**——1982 年的老架构，2020 年被 Ramsauer 等人"现代化"后发现：**它和 Transformer 的 attention 本质等价**。这不是巧合，是"联想记忆"和"注意力"的数学同构。

---

## 1. 灵魂：联想记忆

$$
\boxed{\text{Hopfield Network} = \text{给一个损坏的模式，检索出最接近的存储模式}}
$$

- 存 $N$ 个模式 $\{x_1, \ldots, x_N\}$
- 输入一个"破损"查询 $q$
- 输出"最接近"的存储模式 $x^*$

**这和 attention 做的事几乎一样**：query 检索最相关的 key。

---

## 2. 经典 Hopfield（1982）

### 2.1 能量函数

$$
E = -\frac{1}{2} \sum_{ij} w_{ij} s_i s_j, \quad w_{ij} = \sum_k x_k^{(i)} x_k^{(j)}
$$

- $s$ 是神经元状态（±1，二值）
- $w$ 是权重（存储模式的外积和）
- 检索：更新 $s$ 直到 $E$ 最小（收敛到最近的存储模式）

### 2.2 容量极限

经典 Hopfield 存 $N$ 个模式需要约 $0.14 \times d$ 个神经元（$d$ = 模式维度）。**容量小**——存不了多少。

---

## 3. 现代 Hopfield（Ramsauer 2020）：容量指数爆炸

### 3.1 连续 + 新能量函数

Ramsauer 把二值改成连续，新能量函数：

$$
E = -\text{lse}(\beta, X^T q) + \frac{1}{2} q^T q + \frac{1}{2\beta} \log N
$$

其中 $\text{lse}(\beta, z) = \frac{1}{\beta} \log \sum_i e^{\beta z_i}$（log-sum-exp）。

### 3.2 检索 = Attention

检索公式：

$$
x^{\text{retrieved}} = X \cdot \text{softmax}(\beta X^T q)
$$

**这和 attention $\text{softmax}(QK^T)V$ 完全一样！**

- $q$ = query
- $X$ 的列 = keys = values
- $\beta$ = 温度的倒数

### 3.3 容量飞跃

现代 Hopfield 的容量：$N_{\max} \sim e^{d/2}$（指数级），远超经典版的 $0.14d$。

---

## 4. 这个"等价"的意义

### 4.1 Attention 是"超大容量联想记忆"

Transformer 的 attention 本质是**现代 Hopfield 的检索**——每个 head 是一个联想记忆模块，存 $N$ 个 key-value，query 检索最相关的。

### 4.2 为什么 attention 这么强

现代 Hopfield 的指数容量解释了：为什么 Transformer 能"记住"海量 in-context 例子——它的容量是 $e^{d/2}$，远超 RNN 的 $O(d)$。

### 4.3 新视角：从"记忆"看 attention

- Attention 不是"加权平均"，是**检索最接近的存储模式**
- LayerNorm 是 Hopfield 能量函数的一部分（解释了为什么 Transformer 要 LayerNorm）

---

## 5. 批判性

- **等价是"事后解释"**：知道 attention=Hopfield 不能帮你设计更好的 attention
- **容量理论是上界**：实际能存多少还取决于训练（权重不是真的存了 $e^{d/2}$ 个模式）
- **但提供了设计原则**：现代 Hopfield 理论指导了 Dense Associated Memory 等新架构

> **诚实结论**：Hopfield-Attention 等价是**深刻的数学洞察**，它揭示了 attention 的本质（联想记忆），但不直接产生工程突破。价值在"理解"，不在"改进"。

---

## 📌 下一步

[12-SpikingNN](12-SpikingNN.md)——另一种"老架构复兴"：脉冲神经网络，能效比 NN 高 1000×。

## ✍️ 练习

1. 现代 Hopfield 的检索公式 $X \cdot \text{softmax}(\beta X^T q)$ 和 attention 一样。为什么 attention 用 $\sqrt{d}$ 缩放而 Hopfield 用 $\beta$？（提示：都是温度控制，$\beta = 1/\sqrt{d}$ 近似。）
2. 经典 Hopfield 容量 0.14d，现代 $e^{d/2}$。为什么连续化能指数爆炸？（提示：lse 的平滑性让模式不互相干扰。）
