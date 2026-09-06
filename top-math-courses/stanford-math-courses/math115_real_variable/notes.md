# Stanford MATH 115 · 章节笔记

> **教材**：Ross *Elementary Analysis* 或 Rudin *Principles*
> **特色**：本科实分析入门，Stanford 数学专业基础课

---

# 费曼三层讲透：微积分的严格化

## 🧠 直觉层

| 概念 | 比喻 |
|---|---|
| **ε-δ 极限** | **"精度承诺"**：你要求 ε 精度，我保证 δ 范围内满足 |
| **完备性** | **"没有洞的数轴"**：Cauchy 列不会"扑空" |
| **紧致性** | **"跑不掉的空间"**：有界+闭 = 序列总有极限点 |
| **Dedekind 切** | **"切一刀分成两半"**：每个切定义一个实数 |

---

## 🧮 数学层

### Dedekind 切构造 $\mathbb{R}$

**切** $(A, B)$：$A \cup B = \mathbb{Q}$, $A \cap B = \emptyset$, $\forall a \in A, b \in B: a < b$。

每个切定义一个实数。$\sqrt{2}$ = $(\{q \in \mathbb{Q} : q^2 < 2 \text{ 或 } q < 0\}, \{q : q^2 \geq 2, q > 0\})$。

### ε-δ 极限

$$\lim_{x \to a} f(x) = L \iff \forall \epsilon > 0, \exists \delta > 0: 0 < |x-a| < \delta \Rightarrow |f(x)-L| < \epsilon$$

### 紧致性（Heine-Borel）

$K \subset \mathbb{R}^n$ 紧致 $\iff$ $K$ 有界且闭。

### 4 种收敛模式（预告后续）

$$L^p \Rightarrow \text{依概率} \Rightarrow \text{依分布}; \quad \text{a.s.} \Rightarrow \text{依概率}$$

### Taylor 定理

$$f(x) = \sum_{k=0}^n \frac{f^{(k)}(a)}{k!}(x-a)^k + R_n(x)$$

---

## 💻 代码层

```python
import numpy as np
# Dedekind 切: 用有理数逼近 sqrt(2)
qs = [q for q in np.linspace(0, 2, 10000)]
lower = max(q for q in qs if q**2 < 2)
upper = min(q for q in qs if q**2 >= 2)
print(f"sqrt(2) 的下逼近: {lower:.6f}")
print(f"sqrt(2) 的上逼近: {upper:.6f}")
print(f"实际 sqrt(2): {np.sqrt(2):.6f}")
```

---

## ⚠️ 不足层
- 只做单变量，不做度量空间 → Stanford Math 171 补
- Riemann 积分，无 Lebesgue

---

## 🚀 应用层

| 概念 | ML 对应 |
|---|---|
| Dedekind 切 | 浮点数表示的严格基础 |
| 紧致性 | loss 最小值存在性 |
| Taylor | 二阶优化（Newton 法） |

---

## 章节概览

| 章 | 内容 | 关键定理 |
|---|---|---|
| 1-2 | $\mathbb{R}$ 构造 | Dedekind 切 ★ |
| 3-4 | 序列收敛 | ε-N, Cauchy 列 |
| 5-6 | 连续性 | 介值定理、极值定理 |
| 7-8 | 微分 | MVT、Taylor ★ |
| 9-10 | Riemann 积分 | 微积分基本定理 |
| 11 | 函数序列 | 一致收敛 ★ |
| 12 | 度量空间（可选） | 预告 Math 171 |
