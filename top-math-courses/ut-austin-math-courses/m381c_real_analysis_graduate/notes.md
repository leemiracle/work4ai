# UT Austin M 381C · 章节笔记（Royden & Fitzpatrick / Folland）

> **教材**：Royden & Fitzpatrick *Real Analysis* 或 Folland *Real Analysis*
> **特色**：**UT Austin 研究生实分析**——测度论 + Lebesgue 积分 + 泛函分析基础

---

# 费曼三层讲透：测度论与 Lebesgue 积分

## 🧠 直觉层

| 概念 | 比喻 |
|---|---|
| **σ-代数** | **"可测事件的家族"**：可数并/交/补封闭 |
| **测度 $\mu$** | **"体积/概率的推广"**：$\mu(\bigcup A_i) = \sum \mu(A_i)$ |
| **Lebesgue 积分** | **"按值域分割求和"**——Riemann 是按定义域 |
| **$L^p$ 空间** | **"能量有限的函数空间"**：$\int |f|^p < \infty$ |
| **可测函数** | **"可以积分的函数"**：原像可测 |
| **Radon-Nikodym** | **"测度的导数"**：$d\nu = f \, d\mu$ |
| **压缩映射** | **"每次拉近"**：Banach 不动点 |

---

## 🧮 数学层

### σ-代数与测度

$(X, \mathcal{M}, \mu)$: $\mathcal{M}$ = σ-代数, $\mu: \mathcal{M} \to [0, \infty]$, $\mu(\emptyset) = 0$, 可数可加。

**Borel σ-代数** $\mathcal{B}(\mathbb{R})$: 由开集生成的最小 σ-代数。

**Lebesgue 测度** $m$: $\mathbb{R}^n$ 上唯一的平移不变、正则 Borel 测度，$m([0,1]^n) = 1$。

### 可测函数

$f: X \to \mathbb{R}$ **可测** $\iff$ $\{f > a\} \in \mathcal{M}, \forall a$。

可测函数列的极限、上下确界、sum/product 都可测。

### Lebesgue 积分 ★★★

**简单函数**: $\phi = \sum_{i=1}^n c_i \mathbf{1}_{A_i}$, $\int \phi = \sum c_i \mu(A_i)$

**非负可测**: $\int f = \sup\{\int \phi : 0 \leq \phi \leq f, \phi \text{ 简单}\}$

**一般可测**: $\int f = \int f^+ - \int f^-$ (若至少一个有限)

### 三大收敛定理 ★★★

**MCT (Monotone Convergence)**:
$$0 \leq f_n \nearrow f \implies \int f_n \nearrow \int f$$

**Fatou 引理**:
$$\int \liminf f_n \leq \liminf \int f_n$$

**DCT (Dominated Convergence)** ★★★:
$$|f_n| \leq g \in L^1, \quad f_n \to f \text{ a.e.} \implies \int f_n \to \int f$$

**ML 应用**: SGD —— mini-batch 梯度 $g_n \to \nabla L$ a.s., $|g_n| \leq G$ → $\int g_n \to \int \nabla L$ (DCT 合法化梯度换序)。

### $L^p$ 空间 ★★

$L^p(\mu) = \{f : \|f\|_p = (\int |f|^p)^{1/p} < \infty\}$

**完备**: $L^p$ 是 Banach 空间 ($1 \leq p \leq \infty$)。
$L^2$ 是 Hilbert 空间（内积 $\langle f, g \rangle = \int f\bar{g}$）。

**Hölder**: $\|fg\|_1 \leq \|f\|_p \|g\|_q$ ($1/p + 1/q = 1$)
**Minkowski**: $\|f+g\|_p \leq \|f\|_p + \|g\|_p$

**对偶**: $(L^p)^* \cong L^q$ ($1 < p < \infty$)

### 4 种收敛模式 ★★★

$$\boxed{L^p \Rightarrow \text{依概率} \Rightarrow \text{依分布}; \quad \text{a.s.} \Rightarrow \text{依概率}}$$

| 模式 | 定义 | 反例 |
|---|---|---|
| **依分布** | $F_n(x) \to F(x)$ 连续点 | 最弱 |
| **依概率** | $\mu(|f_n - f| > \epsilon) \to 0$ | ← Lp/a.s. |
| **$L^p$** | $\|f_n - f\|_p \to 0$ | 滑动区间 |
| **a.s.** | $\mu(\{f_n \not\to f\}) = 0$ | 滑动区间 |

### Radon-Nikodym 定理 ★★

$\nu \ll \mu$ (绝对连续) $\implies \exists f \geq 0: \nu(E) = \int_E f \, d\mu$

$f = \frac{d\nu}{d\mu}$ = Radon-Nikodym 导数。

**ML 应用**: 变分推断 $\text{KL}(q \| p) = \int \log\frac{dq/dp}{1} \, dp$；Score-based diffusion。

### 压缩映射原理

$(X, d)$ 完备 + $T$ 压缩 → 唯一不动点。

**ML 应用**: SGD $\theta_{k+1} = \theta_k - \eta \nabla L(\theta_k)$, 当 $\eta L_{lip} < 1$ 时收敛。

---

## 💻 代码层

```python
import numpy as np
import matplotlib.pyplot as plt

# Lebesgue vs Riemann: Dirichlet 函数
# f(x) = 1_Q(x): Riemann 不可积但 Lebesgue 可积
x = np.linspace(0, 1, 1000)
# 模拟: Q ∩ [0,1] 的密度
is_rational = np.random.random(1000) < 0.0001  # 极稀疏
dirichlet = is_rational.astype(float)
print(f"Dirichlet 函数在 1000 个点中有 {sum(is_rational)} 个有理数")
print(f"Riemann: 上和=1, 下和=0 → 不可积")
print(f"Lebesgue: ∫f = 1 × μ(Q∩[0,1]) = 1 × 0 = 0 → 可积")

# 4 种收敛模式演示: 滑动区间
fig, axes = plt.subplots(2, 2, figsize=(10, 8))
# 依概率但非 a.s.
t = np.linspace(0, 1, 1000)
for trial in range(5):
    n = 2**trial
    width = 1/n
    fn = np.zeros_like(t)
    start = (trial * 0.137) % (1 - width)  # 滑动位置
    fn[(t >= start) & (t < start + width)] = 1
    axes[0,0].plot(t, fn, alpha=0.5)
axes[0,0].set_title("依概率→0 (区间宽度→0)")
axes[0,0].set_ylim(-0.1, 1.1)

# Lp 范数
f_abs = np.abs(np.sin(2*np.pi*t))
for p in [1, 2, 5, 100]:
    lp_norm = (np.trapz(f_abs**p, t))**(1/p)
    axes[0,1].plot(t, f_abs**p, alpha=0.5, label=f'p={p}, ||f||_p={lp_norm:.3f}')
axes[0,1].legend()
axes[0,1].set_title("Lp 范数: p 增大 → sup 范数")

# DCT: f_n → f 且 |f_n| ≤ g
for n in [1, 5, 20]:
    fn = np.exp(-n * (t - 0.5)**2) * n**0.5  # 高度=√n
    axes[1,0].plot(t, fn, label=f'n={n}')
g = 2 * np.ones_like(t)  # 控制函数
axes[1,0].plot(t, g, 'k--', label='g (控制函数)')
axes[1,0].legend()
axes[1,0].set_title("DCT: |f_n| ≤ g ∈ L¹")

# Radon-Nikodym: 离散近似
mu = np.ones(100)  # 基础测度
f = 2 * np.exp(-5 * (np.linspace(0, 1, 100) - 0.5)**2)  # RN 导数
nu = f * mu  # dν = f dμ
axes[1,1].bar(np.linspace(0, 1, 100), nu, alpha=0.5, label='ν = f·μ')
axes[1,1].plot(np.linspace(0, 1, 100), f, 'r-', label='f = dν/dμ')
axes[1,1].legend()
axes[1,1].set_title("Radon-Nikodym: dν = f dμ")

plt.tight_layout()
plt.savefig("measure_theory_demo.png", dpi=100)
print("\n测度论演示已保存")
```

---

## ⚠️ 不足层
- 不涉及深算子谱理论（M 382C 泛函分析）
- 不做深概率论（M 385C 概率论）
- 不做偏微分方程

---

## 🚀 应用层

| 概念 | ML 对应 |
|---|---|
| Lebesgue 积分 | 期望 $E[X] = \int X \, dP$ |
| DCT | SGD: mini-batch → 全梯度的换序 |
| MCT | 单调序列极限的合法性 |
| $L^p$ 空间 | 函数空间优化 / RKHS |
| 4 种收敛 | 概率论基础（大数定律、CLT） |
| Radon-Nikodym | 变分推断 / KL 散度 / Score-based diffusion |
| 压缩映射 | SGD 收敛分析 |
| Fubini 定理 | 多重积分换序 |

---

## 章节概览（Royden/Folland）

| 章 | 内容 | 关键 |
|---|---|---|
| 1-2 | σ-代数 + 测度 | Carathéodory 扩张 ★ |
| 3 | 可测函数 | Borel/Lebesgue 可测 |
| 4 | Lebesgue 积分 ★★★ | MCT, Fatou, DCT |
| 5-6 | $L^p$ 空间 ★★ | 完备性, Hölder, 对偶 |
| 7 | 收敛模式 ★★★ | 依分布/概率/Lp/a.s. |
| 8 | Radon-Nikodym ★★ | 绝对连续, 导数 |
| 9 | Fubini-Tonelli | 乘积测度 |
| 10 | 度量空间 + 压缩映射 | Banach 不动点 |
| 11 | Hilbert 空间简介 | 正交, Riesz 表示 |
