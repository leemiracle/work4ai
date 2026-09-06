# Oxford Prelims M2 · 章节笔记（Analysis I）

> **教材**：Oxford lecture notes + Bartle *Introduction to Real Analysis* + Tao *Analysis I*
> **特色**：Oxford 第一年数学必修——从 $\mathbb{R}$ 严格构造到级数收敛

---

# 费曼三层讲透：实分析入门

## 🧠 直觉层

| 概念 | 比喻 |
|---|---|
| **上确界** | **"最小上界"**——天花板中的最低者 |
| **ε-δ 连续** | **"客户给精度，我给策略"** |
| **可微** | **"有切线"**：差商有极限 |
| **MVT** | **"平均速度 = 某时刻瞬时速度"** |
| **级数收敛** | **"无穷项相加有意义"**：部分列有极限 |

---

## 🧮 数学层

### 实数完备性

**上确界公理**: $\emptyset \neq S \subset \mathbb{R}$ 有上界 $\implies \sup S \in \mathbb{R}$。

**等价**: Cauchy 完备 $\iff$ 单调收敛定理 $\iff$ 上确界公理 $\iff$ Bolzano-Weierstrass $\iff$ 嵌套区间定理。

### ε-δ 连续

$$\forall \epsilon > 0, \exists \delta > 0: |x - c| < \delta \implies |f(x) - f(c)| < \epsilon$$

**间断类型**: 可去 / 跳跃 / 本性（无穷振荡如 $\sin(1/x)$）。

### 可微与中值定理 ★

**MVT**: $f$ 在 $[a,b]$ 连续 + $(a,b)$ 可微 $\implies \exists c: f'(c) = \frac{f(b)-f(a)}{b-a}$

**推论**: $f' > 0 \Rightarrow$ 严格递增; $f' = 0 \Rightarrow$ 常数。

**ML 应用**: MVT 保证梯度路径上 $\nabla L$ 每个值都出现——优化可达性。

### Taylor 展开

$$f(x) = \sum_{k=0}^n \frac{f^{(k)}(a)}{k!}(x-a)^k + R_n(x)$$

$R_n = \frac{f^{(n+1)}(c)}{(n+1)!}(x-a)^{n+1}$（Lagrange 余项）

### Riemann 积分

$f$ Riemann 可积 $\iff$ Darboux 上下积分相等 $\iff \forall \epsilon, \exists P: U(f,P) - L(f,P) < \epsilon$

**微积分基本定理**: $F(x) = \int_a^x f(t) \, dt \Rightarrow F' = f$（$f$ 连续）

### 级数收敛

| 判别 | 条件 | 结论 |
|---|---|---|
| 比值 | $\lim|a_{n+1}/a_n|$ | $<1$ 收敛, $>1$ 发散 |
| 比较 | $|a_n| \leq b_n$ | $\sum b_n$ 收敛 → $\sum a_n$ 绝对收敛 |
| 交错 | $a_n \searrow 0$ | $\sum (-1)^n a_n$ 收敛 |
| 积分 | $f$ 正递减 | $\sum f(n) \leftrightarrow \int f$ 同敛散 |

**幂级数**: $\sum c_n x^n$, 收敛半径 $R = 1/\limsup |c_n|^{1/n}$。

---

## 💻 代码层

```python
import numpy as np
import matplotlib.pyplot as plt

# Taylor 展开: sin(x) 的逼近
x = np.linspace(-np.pi, np.pi, 200)
sin_exact = np.sin(x)

# n 阶 Taylor 展开
import math
fig, ax = plt.subplots(figsize=(8, 5))
for n in [1, 3, 5, 7]:
    taylor = sum((-1)**k * x**(2*k+1) / math.factorial(2*k+1) for k in range((n+1)//2))
    ax.plot(x, taylor, label=f'Taylor n={n}', alpha=0.7)
ax.plot(x, sin_exact, 'k-', linewidth=2, label='sin(x) 精确')
ax.legend()
ax.set_title("sin(x) 的 Taylor 展开：阶数越高越精确")
ax.set_ylim(-2, 2)
plt.tight_layout()
plt.savefig("taylor_sin.png", dpi=100)

# 级数收敛速度
partial_sums = np.cumsum([1/(k*k) for k in range(1, 101)])
print(f"Σ1/n² 前 100 项 = {partial_sums[-1]:.6f}")
print(f"精确值 π²/6 = {np.pi**2/6:.6f}")
print(f"误差 = {abs(partial_sums[-1] - np.pi**2/6):.2e}")
```

---

## ⚠️ 不足层
- Oxford M2 只做单变量 → M2 Part 2 做多变量
- 不涉及度量空间 / 拓扑（Part A/B 课程）
- 只做 Riemann 积分

---

## 🚀 应用层

| 概念 | ML 对应 |
|---|---|
| 上确界公理 | sup/inf 优化 |
| MVT | 优化路径可达性 |
| Taylor 展开 | 二阶优化 / 牛顿法 |
| 幂级数 | 特征展开 / softmax |
| 级数收敛 | 学习率调度收敛性 |

---

## 章节概览

| 章 | 内容 | 关键 |
|---|---|---|
| 1 | 实数 | 完备性公理 ★ |
| 2 | 序列 | Cauchy、单调收敛 |
| 3 | 级数 | 判别法、幂级数 |
| 4 | 连续性 | ε-δ、IVT ★ |
| 5 | 可微 | MVT、Taylor ★ |
| 6 | 积分 | Darboux、微积分基本定理 |
