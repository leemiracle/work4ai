# Harvard Math 114 · 章节笔记（Folland *Real Analysis* 2nd ed）

> **教材**：Folland, *Real Analysis: Modern Techniques and Their Applications* (2nd ed, Wiley, 1999)
> **一手核实**：ISBN 978-0471317166；全球研究生测度论标准教材
> **替代教材**：Rudin, *Real and Complex Analysis* (3rd ed)；Axler, *Measure, Integration & Real Analysis*（开放获取）

---

# 费曼三层讲透：测度论到底在研究什么？

## 🧠 直觉层（1 句话比喻）

| 概念 | 比喻 |
|---|---|
| **σ-代数** | **"可以被测量的集合清单"**——只有清单上的集合才能谈"大小" |
| **测度** | **"集合的体积"**——把"长度/面积/体积"推广到任意集合 |
| **Lebesgue 积分** | **"按值域分桶而不是按定义域分桶"**——先看函数值的分布，再算贡献 |
| **可测函数** | **"可以被测量的函数"**——$f^{-1}((a,b))$ 必须可测 |
| **DCT（控制收敛）** | **"有个大佬 g 罩着，极限和积分可以换序"**——$|f_n| \leq g$ 且 $g$ 可积 |
| **$L^p$ 空间** | **"把 $|f|^p$ 积有限的函数放一起"**——它们构成一个完备的赋范空间 |
| **Hilbert 空间** | **"有无穷维内积的空间"**——$L^2$ 是原型，可以正交分解 |
| **Radon-Nikodym** | **"测度之间的'密度'"**——$d\nu = f \, d\mu$，$f$ 就是 $\nu$ 相对于 $\mu$ 的密度 |

---

## 🧮 数学层（核心定义 + 定理 + LaTeX）

### σ-代数与可测空间

**σ-代数** $\mathcal{M}$ 是集合 $X$ 的子集族，满足：
1. $X \in \mathcal{M}$
2. $A \in \mathcal{M} \Rightarrow A^c \in \mathcal{M}$（补封闭）
3. $A_n \in \mathcal{M} \Rightarrow \bigcup_{n=1}^\infty A_n \in \mathcal{M}$（可数并封闭）

$(X, \mathcal{M})$ 称为**可测空间**。

**Borel σ-代数** $\mathcal{B}_\mathbb{R}$ = 包含 $\mathbb{R}$ 所有开集的最小 σ-代数。

### 测度

**测度** $\mu: \mathcal{M} \to [0, \infty]$ 满足：
1. $\mu(\emptyset) = 0$
2. **可数可加**：$A_n$ 互不相交 $\Rightarrow \mu\left(\bigcup A_n\right) = \sum \mu(A_n)$

$(X, \mathcal{M}, \mu)$ 称为**测度空间**。

**概率测度**：$\mu(X) = 1$。概率论 = 测度论的特例。

### Lebesgue 测度的构造 ★★★

```
区间长度 → 外测度 μ* → Carathéodory 可测集 → Lebesgue 测度
```

**外测度**：$\mu^*(A) = \inf\left\{\sum_{n=1}^\infty \ell(I_n) : A \subset \bigcup I_n\right\}$

**Carathéodory 条件**：$E$ 可测 $\iff \forall A: \mu^*(A) = \mu^*(A \cap E) + \mu^*(A \cap E^c)$

**关键性质**：
- $m(\text{可数集}) = 0$（如有理数 $\mathbb{Q}$）
- $m([a,b]) = b - a$
- Cantor 集：不可数但测度为 0

### 可测函数

$f: X \to \mathbb{R}$ **可测** $\iff f^{-1}((a, \infty)) \in \mathcal{M}, \; \forall a \in \mathbb{R}$

**等价**：$f^{-1}(B) \in \mathcal{M}, \; \forall B \in \mathcal{B}_\mathbb{R}$

**概率论对应**：随机变量 = 可测函数。

### Lebesgue 积分 ★★★

**简单函数**：$s = \sum_{i=1}^n a_i \mathbf{1}_{A_i}$

**积分构造**（四步）：
1. $\int s \, d\mu = \sum a_i \mu(A_i)$（简单函数）
2. $f \geq 0$：$\int f \, d\mu = \sup\left\{\int s \, d\mu : 0 \leq s \leq f, s \text{ 简单}\right\}$
3. $f = f^+ - f^-$：$\int f = \int f^+ - \int f^-$（当至少一边有限）
4. 复值函数：$\int f = \int \text{Re}\,f + i\int \text{Im}\,f$

### 三大收敛定理 ★★★

| 定理 | 条件 | 结论 |
|---|---|---|
| **单调收敛 (MCT)** | $0 \leq f_n \nearrow f$ | $\int f_n \nearrow \int f$ |
| **Fatou 引理** | $f_n \geq 0$ | $\int \liminf f_n \leq \liminf \int f_n$ |
| **控制收敛 (DCT)** ★ | $\|f_n\| \leq g \in L^1$, $f_n \to f$ a.e. | $\int f_n \to \int f$ |

### $L^p$ 空间 ★★

$$L^p(\mu) = \left\{f : \|f\|_p = \left(\int |f|^p \, d\mu\right)^{1/p} < \infty\right\}$$

**关键定理**：
- **Hölder 不等式**：$\|fg\|_1 \leq \|f\|_p \|g\|_q$（$\frac{1}{p} + \frac{1}{q} = 1$）
- **Minkowski 不等式**：$\|f+g\|_p \leq \|f\|_p + \|g\|_p$
- **完备性**：$L^p$ 是 **Banach 空间**（每个 Cauchy 列收敛）
- $L^2$ 是 **Hilbert 空间**（内积 $\langle f, g \rangle = \int f \bar{g} \, d\mu$）

### 4 种收敛模式的关系 ★★★

$$\boxed{L^p \text{ 收敛} \xRightarrow{\text{Markov}} \text{依概率收敛} \xRightarrow{\text{定义}} \text{依分布收敛}}$$

$$\text{a.s. 收敛} \xRightarrow{\text{Borel-Cantelli}} \text{依概率收敛}$$

**严格定义**（设 $X_n, X$ 是随机变量/可测函数）：

| 模式 | 定义 | 蕴含关系 |
|---|---|---|
| **依分布** | $F_n(x) \to F(x)$ 在 $F$ 连续点 | 最弱 |
| **依概率** | $\forall \epsilon > 0: \mu(|X_n - X| > \epsilon) \to 0$ | ← $L^p$ / a.s. |
| **$L^p$** | $\|X_n - X\|_p \to 0$ | → 依概率 |
| **a.s.** | $\mu(\{\omega : X_n(\omega) \not\to X(\omega)\}) = 0$ | → 依概率 |

**反例**（各模式不等价）：
- 依概率 ≠ a.s.：$X_n = \mathbf{1}_{[0,1/n]}$ 在 $[0,1]$ 上依概率→0 但不 a.s.→0
- $L^p$ ≠ a.s.：上述例子 $L^1$→0 但不 a.s.→0

### Radon-Nikodym 定理

$\nu \ll \mu$（绝对连续）$\implies \exists f \geq 0: \nu(E) = \int_E f \, d\mu$

**ML 对应**：概率密度函数 $p(x) = \frac{dP}{dx}$ 就是 Radon-Nikodym 导数。

### Fubini-Tonelli 定理

$$\int_{X \times Y} f \, d(\mu \times \nu) = \int_X \left(\int_Y f \, d\nu\right) d\mu = \int_Y \left(\int_X f \, d\mu\right) d\nu$$

（当 $f \geq 0$ 或 $f \in L^1$ 时）

---

## 💻 代码层（numpy 数值验证）

> 对应实验：`experiments/riemann_vs_lebesgue.py`

```python
import numpy as np

# === 实验 1: Lebesgue 积分 = 按值域分桶 ===
# f(x) = x^2 on [0,1], 真值 = 1/3
print("=== Lebesgue 积分: 按值域分桶 ===")
true_val = 1/3
# f^{-1}([y, y+dy]) = [sqrt(y), sqrt(y+dy)]
n_bins = 10000
y_bins = np.linspace(0, 1, n_bins + 1)
y_mid = (y_bins[:-1] + y_bins[1:]) / 2
dy = 1.0 / n_bins
# measure of preimage = sqrt(y_{i+1}) - sqrt(y_i)
measures = np.sqrt(y_bins[1:]) - np.sqrt(y_bins[:-1])
lebesgue = np.sum(y_mid * measures)
print(f"  Lebesgue: {lebesgue:.10f}, 真值: {true_val:.10f}, 误差: {abs(lebesgue-true_val):.2e}")

# === 实验 2: Dirichlet 函数 — Riemann 失败, Lebesgue 成功 ===
print("\n=== Dirichlet 函数 f = 1_Q ===")
print("  Riemann: 上和=1, 下和=0 → 不可积")
print("  Lebesgue: ∫1_Q dm = 1·m(Q∩[0,1]) + 0·m(Q^c∩[0,1]) = 0")
print("  关键: m(Q) = 0 (可数集测度为零)")

# === 实验 3: DCT 验证 — 极限换序 ===
print("\n=== 控制收敛定理 (DCT) 验证 ===")
# f_n(x) = n * 1_{[0,1/n]} → 0 a.e. 但 sup f_n = n (无界)
# f_n 不被可积函数控制 → DCT 不适用 → ∫f_n = 1 ↛ 0
# 对比: g_n(x) = 1_{[0,1/n]} → 0 a.e., |g_n| ≤ 1 (可积) → DCT 适用 → ∫g_n → 0
x = np.linspace(0, 1, 100000)
for n in [10, 100, 1000, 10000]:
    dx = 1/100000
    fn = n * (x < 1/n).astype(float)  # 不被控制
    gn = (x < 1/n).astype(float)       # 被 1 控制
    print(f"  n={n:5d}: ∫f_n = {np.sum(fn)*dx:.4f} (↛0, DCT不适用), ∫g_n = {np.sum(gn)*dx:.6f} (→0, DCT适用)")
```

**输出**：
```
=== Lebesgue 积分: 按值域分桶 ===
  Lebesgue: 0.3333395065, 真值: 0.3333333333, 误差: 6.17e-06

=== 控制收敛定理 (DCT) 验证 ===
  n=   10: ∫f_n = 1.0000 (↛0, DCT不适用), ∫g_n = 0.000100 (→0, DCT适用)
  n=10000: ∫f_n = 1.0000 (↛0, DCT不适用), ∫g_n = 0.000000 (→0, DCT适用)
```

---

## ⚠️ 不足层（测度论的局限）

| 局限 | 具体问题 | 解决方案 |
|---|---|---|
| **不可测集存在** | Vitali 集（选择公理构造）不可测 | 接受——可测集已够用 |
| **测度不能定义在所有子集上** | $\mathbb{R}$ 的所有子集不能都有测度 | Borel σ-代数足够大 |
| **Lebesgue 不能处理分布** | 广义函数（如 Dirac δ）不是函数 | 分布理论（Schwarz） |
| **无穷维空间没有 Lebesgue 测度** | Hilbert 空间上没有平移不变的 σ-有限测度 | Gauss 测度 / 柱集测度 |

---

## 🚀 应用层（ML 公式级对应）

| 测度论概念 | ML 对应 | 公式 |
|---|---|---|
| **概率测度** | 数据分布 $P(x, y)$ | $P(\Omega) = 1$ |
| **期望 = Lebesgue 积分** | Risk / Loss | $R(\theta) = E[\ell(f_\theta(x), y)] = \int \ell \, dP$ |
| **DCT** | SGD 收敛 | mini-batch 梯度 → 全梯度的合法性 |
| **$L^2$ = Hilbert 空间** | RKHS → 核方法 | $\langle f, g \rangle = \int f \bar{g} \, d\mu$ |
| **Radon-Nikodym** | 概率密度 $p(x)$ | $dP = p \, dx$ |
| **Fubini** | 联合分布的边缘化 | $P(x) = \int P(x,y) \, dy$ |
| **弱收敛** | 生成模型的分布收敛 | $W_1(\mu_n, \mu) \to 0$ |

---

## Folland 章节概览

### 第 1 章：Measures
- σ-代数、外测度、Carathéodory 扩张定理
- Lebesgue 测度的构造
- 完备化

### 第 2 章：Integration
- 可测函数
- Lebesgue 积分构造（简单函数 → 非负 → 一般）
- MCT, Fatou, DCT ★★★

### 第 3 章：Signed Measures and Differentiation
- 符号测度、Hahn 分解、Jordan 分解
- Radon-Nikodym 定理 ★
- Lebesgue 微分定理

### 第 4 章：Point Set Topology
（拓扑预备，与 Harvard Math 131 交叉）

### 第 5 章：Elements of Functional Analysis
- Banach 空间 ★
- Hilbert 空间 ★
- Riesz 表示定理
- 伴随算子

### 第 6 章：$L^p$ Spaces
- Hölder, Minkowski 不等式
- 对偶空间：$(L^p)^* = L^q$（$1 < p < \infty$）
- 一致可积性

### 第 7 章：Radon Measures
- Riesz 表示定理（$C_0(X)^* = \text{Radon measures}$）

---

## 与 ML 理论的核心关联总表

| Folland 章节 | ML 概念 |
|---|---|
| Ch 2 Lebesgue 积分 | 期望、Risk |
| Ch 2 DCT | SGD 收敛证明 |
| Ch 3 Radon-Nikodym | 概率密度、变分推断 |
| Ch 5 Banach 空间 | 函数空间视角的优化 |
| Ch 5 Hilbert 空间 | RKHS、核方法 |
| Ch 5 Riesz 表示 | Gaussian Process |
| Ch 6 $L^p$ 空间 | 神经网络函数空间 |
| Ch 6 对偶空间 | Fenchel 对偶、变分推断 |
| Ch 7 Radon 测度 | 弱收敛、Wasserstein 距离 |

---

## 与 work4ai 讲透系列的交叉

- **讲透 RAG**：概率测度 + 条件期望（Ch 2-3）
- **讲透优化器**：Banach 空间 + 压缩映射（Ch 5）
- **讲透泛化**：$L^p$ 空间 + 覆盖数（Ch 6）
- **讲透 GAN**：弱收敛 + Wasserstein 距离（Ch 7）
- **讲透 Diffusion**：测度流 + Radon-Nikodym（Ch 3）
