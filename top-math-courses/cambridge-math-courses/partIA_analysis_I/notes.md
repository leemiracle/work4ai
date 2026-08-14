# Cambridge Part IA Analysis I · 章节笔记

> **教材**：Cambridge lecture notes + Tao *Analysis I* + Rudin *PMA* Ch.1-5
> **特色**：Cambridge Tripos IA——严格单变量实分析，从 $\mathbb{R}$ 构造到 Riemann 积分

---

# 费曼三层讲透：单变量实分析

## 🧠 直觉层

| 概念 | 比喻 |
|---|---|
| **实数 $\mathbb{R}$** | **"填满所有缝隙的数轴"**——Dedekind 切割补全 $\mathbb{Q}$ 的洞 |
| **ε-δ 连续** | **"客户给精度 ε，我给策略 δ"** |
| **可微** | **"有切线"**——线性近似的极限 |
| **Riemann 积分** | **"无限细条面积求和"**——Darboux 上下和夹逼 |
| **级数收敛** | **"无穷项加起来有意义"**——部分列有极限 |

---

## 🧮 数学层

### 实数公理

$\mathbb{R}$ 是**完备有序域**：$\mathbb{Q}$ 的 Cauchy 完备化。

**上确界公理**: 每个非空有界子集有上确界 $\sup S$。

### ε-δ 连续

$$f: A \to \mathbb{R} \text{ 在 } c \text{ 连续} \iff \forall \epsilon > 0, \exists \delta > 0: |x-c| < \delta \Rightarrow |f(x)-f(c)| < \epsilon$$

### 可微 + Taylor 展开

$f'(c) = \lim_{h \to 0} \frac{f(c+h)-f(c)}{h}$

Taylor: $f(x) = \sum_{k=0}^n \frac{f^{(k)}(c)}{k!}(x-c)^k + R_n(x)$

### 中值定理 ★

$f$ 在 $[a,b]$ 连续，$(a,b)$ 可微 $\implies \exists c \in (a,b): f'(c) = \frac{f(b)-f(a)}{b-a}$

**ML 应用**: SGD 收敛分析的基础——梯度中值为零的点。

### Riemann 积分

Darboux 上下和: $\underline{S}(f, P) \leq \int_a^b f \leq \overline{S}(f, P)$

$f$ Riemann 可积 $\iff \forall \epsilon, \exists P: \overline{S} - \underline{S} < \epsilon$

### 级数收敛判别

| 判别法 | 条件 |
|---|---|
| 比值法 | $\lim |a_{n+1}/a_n| < 1$ |
| 根值法 | $\limsup |a_n|^{1/n} < 1$ |
| 积分判别 | $\sum f(n)$ ↔ $\int f$ |
| 交错 | $a_n \searrow 0$ |

---

## 💻 代码层

```python
import numpy as np
import matplotlib.pyplot as plt

# ε-δ 连续性: f(x) = x^2 在 x=2 处
# 给定 ε, 找 δ: |x-2| < δ → |x²-4| < ε
eps = 0.1
delta = min(eps / 5, 1)  # δ = ε/(|x|+|c|) ≈ ε/5
x = np.linspace(2 - delta, 2 + delta, 100)
y = x**2
print(f"ε = {eps}, δ = {delta:.4f}")
print(f"max|f(x)-f(2)| = {max(abs(y - 4)):.6f} < ε = {eps}? {max(abs(y-4)) < eps}")

# Riemann 积分可视化
fig, ax = plt.subplots(1, 1, figsize=(8, 4))
x = np.linspace(0, 1, 200)
for n, color in [(5, 'red'), (20, 'blue'), (100, 'green')]:
    xi = np.linspace(0, 1, n+1)
    yi = xi**2  # 积分 x^2
    for i in range(n):
        mid = (xi[i] + xi[i+1]) / 2
        ax.bar(mid, mid**2, width=1/n, alpha=0.3, color=color)
ax.plot(x, x**2, 'k-', linewidth=2)
ax.set_title("Riemann 和逼近 ∫₀¹ x² dx = 1/3")
plt.savefig("riemann_sum.png", dpi=100)
print("Riemann 和演示已保存")
```

---

## ⚠️ 不足层
- 只做 Riemann 积分 → Part IB 做 Lebesgue 预告
- 单变量 → 多变量在 Part IB
- 度量空间概念在 Part IB 才引入

---

## 🚀 应用层

| 概念 | ML 对应 |
|---|---|
| 上确界公理 | 优化问题的 sup/inf 存在 |
| 中值定理 | SGD 收敛分析 |
| Taylor 展开 | 牛顿法 / 二阶优化 |
| Riemann 积分 | 期望 $E[X] = \int x \, dF$ 的离散近似 |
| 级数收敛 | 幂级数 → 特征展开 |

---

## 章节概览（Cambridge IA）

| 章 | 内容 | 关键 |
|---|---|---|
| 1 | 实数构造 | Dedekind 切割 |
| 2 | 序列 | Cauchy、单调收敛 ★ |
| 3 | 级数 | 判别法、绝对收敛 |
| 4 | 连续性 | ε-δ、IVT ★ |
| 5 | 可微性 | MVT、Taylor ★ |
| 6 | Riemann 积分 | Darboux、微积分基本定理 |
