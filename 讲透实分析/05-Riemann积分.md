# 05 - Riemann 积分：从"面积"到微积分基本定理（配 Tao Ch 11）

> 你高中就会算 $\int_0^1 x^2 dx = 1/3$。本章告诉你**为什么**这样算——Riemann 和的极限 + 微积分基本定理。

---

## 一、直觉：面积怎么定义

### 1.1 古希腊的穷竭法

Archimedes 算抛物线面积（故事 2）：用多边形逼近。这就是积分的雏形。

### 1.2 Riemann 的严格化（1854）

把区间 $[a, b]$ 切成 $n$ 份，每份取一点 $\xi_i$，求和：

$$S_n = \sum_{i=1}^n f(\xi_i) \Delta x_i$$

如果 $n \to \infty$（最细分割）时 $S_n$ 收敛到唯一极限，则 $f$ **Riemann 可积**，极限 = $\int_a^b f(x) dx$。

### 1.3 反直觉：不是所有函数都可积

- Dirichlet 函数（$\mathbb{Q}$ 上 1，否则 0）**不可积**——Riemann 和依赖 $\xi_i$ 选择
- 阶跃函数可积
- 连续函数可积
- 间断点"少"的函数可积

---

## 二、数学层

### 2.1 Darboux 积分（等价但更简洁）

**上和** $U(f, P) = \sum M_i \Delta x_i$，$M_i = \sup_{[x_{i-1}, x_i]} f$
**下和** $L(f, P) = \sum m_i \Delta x_i$，$m_i = \inf$

$$f \text{ Riemann 可积} \iff \inf_P U(f, P) = \sup_P L(f, P)$$

### 2.2 Lebesgue 判据（最深刻）⭐

**定理**：$f$ 在 $[a,b]$ 有界。$f$ Riemann 可积 $\iff$ $f$ 的间断点集**测度为 0**。

**反直觉**：$\mathbb{Q} \cap [0,1]$ 是可数集（测度 0），但 Dirichlet 函数处处间断——**间断点集是全集 $[0,1]$**，测度 1，所以不可积。

### 2.3 微积分基本定理（FTC）⭐⭐⭐

**FTC Part 1**：$f$ 连续，$F(x) = \int_a^x f(t) dt$。则 $F'(x) = f(x)$。

→ **积分的导数是原函数**。

**FTC Part 2**：$F$ 是 $f$ 的原函数（$F' = f$）。则 $\int_a^b f(x) dx = F(b) - F(a)$。

→ **微分和积分互逆**。这是微积分最美结果。

**反直觉**：FTC 把"无穷小求和"（积分）变成"找原函数"（微分逆运算）。这就是为什么你会算 $\int x^2 dx = x^3/3 + C$——因为 $(x^3/3)' = x^2$。

---

## 三、应用

| 应用 | 用什么 |
|------|-------|
| **概率论**：$\mathbb{E}X = \int x f(x) dx$ | 连续随机变量的期望 |
| **ML 损失**：$L = \frac{1}{N}\sum \ell(y, \hat{y})$ | 离散版积分 |
| **物理**：功 = $\int F dx$ | 变力做功 |
| **泛函分析**：$L^p$ 空间 | 积分定义函数空间 |

---

## 四、实验：Riemann 和收敛 + FTC

跑 `python3 -u experiments/05_integration.py`：

- $\int_0^\pi \sin x \, dx = 2$ 的 Riemann 和收敛
- FTC 验证：$(\int_0^x t^2 dt)' = x^2$

详见实验脚本。

---

## 五、不足

- Riemann 积分对"坏函数"失效（如 Dirichlet）→ Lebesgue 积分补救（见 08 章）
- 高维推广麻烦（Fubini 定理需要条件）
- 数值积分效率低（实际用 Monte Carlo / 自适应）

---

📌 **下一步**：读 [`06-无穷级数.md`](06-无穷级数.md)（待写）。跑 `experiments/05_integration.py`。

## ✍️ 练习

1. 用 Riemann 和的定义证 $\int_0^1 x \, dx = 1/2$。
2. 解释为什么 Dirichlet 函数不可积。
3. 🐍 在实验里加 $\int_0^1 1/x \, dx$ 的 Riemann 和（会发散——为什么？）。
4. ⚡ 在 Lean companion Ch 11 找 sorry 填。
5. 思考：FTC Part 1 怎么证？（提示：用 $F(x+h) - F(x) = \int_x^{x+h} f$ + 连续性）
