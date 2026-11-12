# 02 — Rademacher 复杂度：比 VC 维更紧的复杂度度量

> 「讲透统计学习理论」进阶章。01 讲了 VC 维——它给的是**最坏情况**界，对深度学习太松。本篇讲 **Rademacher 复杂度**——一种**数据相关**的复杂度度量，比 VC 维紧得多，能更好地解释泛化。

---

## 1. 灵魂：复杂度应该依赖数据

$$
\boxed{\text{VC 维} = \text{假设类的固有能力（最坏情况）} \quad \text{Rademacher} = \text{假设类在特定数据上的复杂度}}
$$

VC 维不管你有什么数据，给的是固定的复杂度。但实际中，**有些数据更容易学**（结构清晰）——Rademacher 捕捉了这个。

---

## 2. Rademacher 复杂度定义

### 2.1 经验 Rademacher 复杂度

给定数据 $S = (x_1, \ldots, x_n)$ 和假设类 $\mathcal{H}$（实值函数）：

$$
\hat{\mathfrak{R}}_S(\mathcal{H}) = \mathbb{E}_\sigma \left[ \sup_{h \in \mathcal{H}} \frac{1}{n} \sum_{i=1}^n \sigma_i h(x_i) \right]
$$

其中 $\sigma_i \in \{-1, +1\}$ 是**独立随机标签**（Rademacher 变量）。

### 2.2 直觉

"给数据随机打标签，假设类 $\mathcal{H}$ 最多能拟合得多好？"

- 如果 $\mathcal{H}$ 能拟合**任意**随机标签 → Rademacher 大（过拟合能力强 → 复杂度高）
- 如果 $\mathcal{H}$ 拟合不了随机标签 → Rademacher 小（简单 → 泛化好）

---

## 3. Rademacher 泛化界

$$
\text{以概率 } 1-\delta: \quad R(\hat{h}) \leq \hat{R}(\hat{h}) + 2\hat{\mathfrak{R}}_S(\mathcal{H}) + \sqrt{\frac{\log(1/\delta)}{2n}}
$$

**和 VC 界对比**：

| 界 | 复杂度项 | 数据依赖 | 松紧 |
|---|---|---|---|
| VC | $\sqrt{d_{VC}/n}$ | 无（固定） | 松（最坏情况）|
| **Rademacher** | $\hat{\mathfrak{R}}_S(\mathcal{H})$ | **有**（随数据变） | **更紧** |

---

## 4. 为什么 Rademacher 解释了深度学习

### 4.1 神经网络的 Rademacher 复杂度

Bartlett et al. (2017) 证明：**深度网络的 Rademacher 复杂度由权重范数控制**，而非参数量。

$$
\hat{\mathfrak{R}}_S(\mathcal{H}) \leq \frac{B \cdot \text{(权重范数)}}{\sqrt{n}}
$$

其中 $B$ 是层数/宽度的函数。

### 4.2 关键洞察

- **参数多但权重范数小** → Rademacher 小 → 泛化好
- SGD + weight decay 自然找到**范数小**的解 → 泛化好
- 这解释了"过参数化仍泛化"——**有效复杂度**（由范数决定）远低于参数量

> 🎯 这比 VC 维深刻得多：VC 维说"参数多=复杂"，Rademacher 说"**范数小=简单**"——而 SGD 恰好找范数小的解。

---

## 5. PAC-Bayes（更紧的界）

Rademacher 还不是最紧的。**PAC-Bayes 界**考虑假设的**分布**（而非单个假设）：

$$
R(Q) \leq \hat{R}(Q) + \sqrt{\frac{D_{KL}(Q \| P) + \log(1/\delta)}{n}}
$$

- $Q$：后验（SGD 找到的解的分布）
- $P$：先验
- $D_{KL}$：后验偏离先验的程度

**直觉**：SGD 找的解如果和"先验"接近（KL 小）→ 泛化好。这和**最小描述长度（MDL）**呼应。

---

## 6. 批判性

- **Rademacher 仍是上界**——实际泛化间隙可能更小
- **计算 Rademacher 复杂度本身是 NP-hard**（对一般假设类）——实践中只能估
- **深度学习的泛化仍是开放问题**——Rademacher/PAC-Bayes 比 VC 好，但仍不能完全解释"为什么 GPT 泛化"

> **诚实结论**：Rademacher 复杂度是经典 SLT 到现代深度学习理论的桥梁——它引入了"数据相关复杂度"和"范数控制"两个关键思想。但深度学习的泛化之谜仍未完全解开。

---

## 📌 下一步

[03-PAC-Bayes深入](03-PACBayes.md)（待补）——最紧的泛化界 + 在深度学习的应用。

## ✍️ 练习

1. VC 维说"参数多=复杂"，Rademacher 说"范数小=简单"。一个 10 亿参数但权重都是 0.001 的网络，按哪个复杂？
2. SGD + weight decay 为什么找范数小的解？（提示：weight decay = L2 正则 = 惩罚大范数。）
3. Rademacher 给的是"随机标签能拟合多好"。如果一个网络连随机标签都能 100% 拟合（Zhang et al. 2017 的发现），它的 Rademacher 多大？这对泛化意味着什么？
