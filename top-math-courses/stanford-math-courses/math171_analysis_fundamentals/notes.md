# Stanford MATH 171 · 章节笔记（Rudin / Pugh — Metric Spaces）

> **教材**：Rudin *Principles* 或 Pugh *Real Mathematical Analysis*
> **特色**：MATH 115 的进阶版——度量空间 + Stone-Weierstrass + Arzelà-Ascoli + 反函数定理

---

# 费曼三层讲透：度量空间分析的核心

## 🧠 直觉层

| 概念 | 比喻 |
|---|---|
| **度量空间** | **"有尺子的空间"**：$(X, d)$ 有距离函数 $d$ |
| **完备度量空间** | **"没有洞的空间"**：Cauchy 列收敛 → Banach 空间 |
| **Stone-Weierstrass** | **"万能积木"**：多项式（或神经网络）能逼近任何连续函数 |
| **Arzelà-Ascoli** | **"一致有界+平滑=紧致"**：控制了大小和平滑度就能压缩函数族 |
| **反函数定理** | **"Jacobian 非零→局部可逆"**：线性近似可逆则非线性也可逆 |

---

## 🧮 数学层

### 度量空间 $(X, d)$

$d: X \times X \to [0, \infty)$，满足：正定性、对称性、三角不等式。

### Stone-Weierstrass 定理 ★★★

**代数 $\mathcal{A} \subset C(K)$** 分离点 + 含常数 $\implies \mathcal{A}$ 在 $C(K)$ 中稠密（一致拓扑）。

**ML 推论**（Universal Approximation）：$\sigma$ 非多项式连续 → $\text{span}\{\sigma(w \cdot x + b)\}$ 在 $C(K)$ 中稠密。

### Arzelà-Ascoli 定理 ★★

$\{f_\alpha\} \subset C(K)$ 一致有界 + 等度连续 $\iff$ 有一致收敛子序列。

**ML 应用**：覆盖数 $\mathcal{N}(\epsilon, \mathcal{F})$ 的估计 → 泛化界。

### 反函数 / 隐函数定理 ★★

$Df(a)$ 可逆 $\implies f$ 在 $a$ 附近有可微逆函数。

**ML 应用**：Normalizing Flows、变分推断。

### 压缩映射原理 ★

$T: X \to X$, $d(Tx, Ty) \leq q \cdot d(x,y)$, $q < 1$ $\implies$ 唯一不动点。

**ML 应用**：SGD 收敛 $T(\theta) = \theta - \eta \nabla L(\theta)$，当 $\eta L_{\text{lipschitz}} < 1$ 时是压缩映射。

---

## 💻 代码层

```python
import numpy as np
import matplotlib.pyplot as plt
# Arzelà-Ascoli: 等度连续函数族有紧致闭包
# Lipschitz ≤ L 的函数族在 [0,1] 上等度连续
L = 2.0
x = np.linspace(0, 1, 200)
np.random.seed(42)
for _ in range(10):
    # 随机生成 Lipschitz ≤ L 的函数
    y = np.cumsum(np.random.uniform(-L, L, len(x))) * (x[1]-x[0])
    y = np.clip(y, 0, 1)
    plt.plot(x, y, alpha=0.5)
plt.title("Lipschitz ≤ L 的函数族 (等度连续 → Arzelà-Ascoli)")
# 这些函数的闭包是紧致的 → 有收敛子序列
```

---

## ⚠️ 不足层

| 局限 | 解决 |
|---|---|
| 不涉及 Lebesgue 积分 | Harvard Math 114 / Stanford Math 205 |
| 度量空间有限维 | 泛函分析（无穷维 Banach/Hilbert） |
| 不做测度论 | Stanford Math 230A 概率 |

---

## 🚀 应用层

| 概念 | ML 对应 |
|---|---|
| Stone-Weierstrass | **Universal Approximation Theorem** |
| Arzelà-Ascoli | 覆盖数 → 泛化界 |
| 压缩映射 | SGD 收敛 |
| 反函数定理 | Normalizing Flows |
| 隐函数定理 | 隐式神经表示 |

---

## 章节概览

| 章 | 内容 | 关键 |
|---|---|---|
| 1-2 | 度量空间 | 完备性、紧致性 ★ |
| 3 | 连续映射 | 一致连续、Lipschitz |
| 4 | 微分 | 多变量 Taylor、Jacobian |
| 5 | 反/隐函数定理 ★★ | Normalizing Flows |
| 6 | 一致收敛 | Weierstrass M-判别法 |
| 7 | Stone-Weierstrass ★★★ | UAT 的祖先 |
| 8 | Arzelà-Ascoli ★★ | 泛化界基础 |
| 9 | Lebesgue 积分入门 | 预告测度论 |
