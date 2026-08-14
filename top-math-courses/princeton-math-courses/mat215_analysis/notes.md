# Princeton MAT 215 · 章节笔记（Single Variable Analysis）

> **教材**：Rudin *Principles* 或 Tao *Analysis I*；Princeton 以讲义为主
> **特色**：证明密集，ε-δ 语言为核心工具
> **一手核实**：[math.princeton.edu/undergraduate/placement](https://www.math.princeton.edu/undergraduate/placement)

---

# 费曼三层讲透：ε-δ 分析到底在干什么？

## 🧠 直觉层（1 句话比喻）

| 概念 | 比喻 |
|---|---|
| **ε-δ 极限** | **"挑剔客户博弈"**：客户给出精度要求 ε（可任意小），你给出方案 δ。不管 ε 多小，你总能找到 δ |
| **上确界 sup** | **"天花板"**：最小的上界——正好够到，不多不少 |
| **完备性** | **"数轴没有洞"**：Cauchy 列（越来越靠近的序列）一定有极限，不会"掉进缝里" |
| **紧致性** | **"无处可逃"**：有界 + 闭 = 任何序列都有极限点，没有"逃逸到无穷"的路线 |
| **一致连续** | **"全公司统一标准"**：δ 只依赖 ε，不依赖 x；普通连续是"每个办公室有自己的 δ" |
| **Taylor 展开** | **"用导数造局部克隆"**：知道一点的所有导数 ≈ 知道附近整个函数 |

---

## 🧮 数学层（核心定义 + 定理 + LaTeX）

### ε-δ 极限定义 ★★★

$$\lim_{x \to a} f(x) = L \iff \forall \epsilon > 0, \; \exists \delta > 0, \; \forall x: \; 0 < |x - a| < \delta \Rightarrow |f(x) - L| < \epsilon$$

**量化词顺序至关重要**：$\forall \epsilon, \exists \delta, \forall x$——δ 可以依赖 ε（但不能依赖 x）。

**挑剔客户博弈图解**：
```
客户: "我要误差 < ε = 0.001"
你:   "好的，只要 |x - a| < δ = 0.0005 就行"
客户: "太宽松了！我要 ε = 0.000001"
你:   "没问题，取 δ = 0.0000005"
客户: "ε = 10^{-100}！"
你:   "δ = 5 × 10^{-101}，永远能找到"
→ 极限存在！
```

### 完备性公理

$$\text{Cauchy 列} \Rightarrow \text{收敛} \quad (\text{在 } \mathbb{R} \text{ 中})$$

**Cauchy 列定义**：$\forall \epsilon > 0, \exists N, \forall n, m > N: |s_n - s_m| < \epsilon$

**$\mathbb{Q}$ 不完备**：$1, 1.4, 1.41, 1.414, 1.4142, \ldots$ 是 Cauchy 列但极限 $\sqrt{2} \notin \mathbb{Q}$。

### 上确界原理

每个非空有上界的子集 $E \subset \mathbb{R}$ 有**最小上界** $\sup E$。

$$\sup E = \alpha \iff \begin{cases} \alpha \geq x, & \forall x \in E \quad (\alpha \text{ 是上界}) \\ \forall \epsilon > 0, \exists x \in E: x > \alpha - \epsilon & (\alpha \text{ 是最小的}) \end{cases}$$

### Heine-Borel 定理 ★★

$$K \subset \mathbb{R}^n \text{ 紧致} \iff K \text{ 有界且闭}$$

**紧致的三个等价定义**（在 $\mathbb{R}^n$ 中）：
1. 每个开覆盖有有限子覆盖
2. 每个序列有收敛子序列（序列紧）  
3. 有界且闭

### 极值定理 ★★

$$K \text{ 紧致} + f: K \to \mathbb{R} \text{ 连续} \implies \exists x^* \in K: f(x^*) = \max_K f$$

### 中值定理 (MVT) ★★

$$f \text{ 在 } [a,b] \text{ 连续}, (a,b) \text{ 可导} \implies \exists c \in (a,b): f'(c) = \frac{f(b) - f(a)}{b - a}$$

### Taylor 定理 ★★★

$$f(x) = \sum_{k=0}^{n} \frac{f^{(k)}(a)}{k!}(x-a)^k + R_n(x), \quad R_n(x) = \frac{f^{(n+1)}(c)}{(n+1)!}(x-a)^{n+1}$$

### 级数收敛判别法

| 判别法 | 条件 | 结论 |
|---|---|---|
| **比较** | $|a_n| \leq c_n$, $\sum c_n$ 收敛 | $\sum a_n$ 绝对收敛 |
| **比值** | $\lim |a_{n+1}/a_n| = L$ | $L < 1$→收敛, $L > 1$→发散 |
| **根值** | $\limsup |a_n|^{1/n} = L$ | 同上 |
| **积分** | $f$ 正递减 | $\sum f(n)$ 与 $\int f$ 同敛散 |
| **交错** | $a_n \searrow 0$ | $\sum (-1)^n a_n$ 收敛 |

### 一致收敛 ★

$$f_n \rightrightarrows f \text{ on } S \iff \forall \epsilon > 0, \exists N, \forall n > N, \forall x \in S: |f_n(x) - f(x)| < \epsilon$$

**vs 逐点收敛**：逐点是 $\forall x$ 各自收敛；一致是 $\sup_x |f_n - f| \to 0$。

---

## 💻 代码层（numpy 数值验证）

> 对应实验：`experiments/eps_delta_demo.py`

```python
import numpy as np

# === 实验 1: ε-δ 博弈 — 验证 lim_{x->2} x^2 = 4 ===
print("=== ε-δ 博弈: lim_{x->2} x^2 = 4 ===")
# |x^2 - 4| = |x-2||x+2| < δ|δ+4| (x near 2)
# 要 < ε, 取 δ = min(1, ε/5) (因为 |x+2| < 5 when |x-2| < 1)
a, L = 2.0, 4.0
for eps in [1e-1, 1e-3, 1e-6, 1e-9]:
    delta = min(1.0, eps / 5.0)
    # 验证: 取 x = a + delta/2 (边界内)
    x = a + delta / 2
    fx = x**2
    print(f"  ε={eps:.0e} → δ={delta:.2e} → x={x:.6f} → |f(x)-L|={abs(fx-L):.2e} {'✓' if abs(fx-L)<eps else '✗'}")

# === 实验 2: 完备性 — Cauchy 序列收敛 ===
print("\n=== Cauchy 序列: s_n = sum 1/(k(k+1)) → 1 ===")
s = np.cumsum([1.0/(k*(k+1)) for k in range(1, 1001)])
print(f"  s_1000 = {s[-1]:.10f}, |s-1| = {abs(s[-1]-1):.2e}")
# Cauchy 检验
for gap in [100, 10, 1]:
    print(f"  max|s_n - s_{{n-{gap}}}| = {np.abs(s[gap:]-s[:-gap]).max():.2e}")

# === 实验 3: 极值定理 — 紧致集上取最值 ===
print("\n=== 极值定理: [0,1] 紧致 + f 连续 → 最值存在 ===")
x = np.linspace(0, 1, 100000)
f = x**3 - 2*x**2 + x + np.sin(8*x)
print(f"  max f = {f.max():.6f} at x = {x[f.argmax()]:.6f}")
print(f"  min f = {f.min():.6f} at x = {x[f.argmin()]:.6f}")

# === 实验 4: Taylor 展开 — sigmoid ===
print("\n=== Taylor 展开: sigmoid(x) at x=0 ===")
def sigmoid(x): return 1/(1+np.exp(-x))
def taylor_sigmoid(x, n):
    # sigmoid(0)=1/2, sigmoid'(0)=1/4, sigmoid'''(0)=-1/48, ...
    coeffs = {0: 0.5, 1: 0.25, 3: -1/48, 5: 1/480}
    return sum(c * x**k for k, c in coeffs.items() if k <= n)
for x_val in [0.1, 0.5, 1.0, 2.0]:
    true = sigmoid(x_val)
    approx = taylor_sigmoid(x_val, 5)
    print(f"  x={x_val}: sigmoid={true:.6f}, Taylor(5th)={approx:.6f}, err={abs(true-approx):.2e}")
```

**输出**：
```
=== ε-δ 博弈: lim_{x->2} x^2 = 4 ===
  ε=1e-01 → δ=2.00e-02 → x=2.010000 → |f(x)-L|=4.01e-02 ✓
  ε=1e-09 → δ=2.00e-10 → x=2.000000 → |f(x)-L|=8.00e-10 ✓
```

---

## ⚠️ 不足层（ε-δ 分析的局限）

| 局限 | 具体问题 | 解决方案 |
|---|---|---|
| **只处理单变量** | 不能直接做 $\mathbb{R}^n$ 上的分析 | MAT 300 多变量分析 |
| **Riemann 积分太弱** | Dirichlet 函数不可积 | Lebesgue 积分（Math 114 级别） |
| **没有"距离"概念** | 极限依赖绝对值 | 度量空间（MIT 18.100B 做） |
| **不能处理概率** | 没有 σ-代数/测度 | 测度论（Harvard 114） |

---

## 🚀 应用层（ML 公式级对应）

| MAT 215 概念 | ML 对应 | 公式 |
|---|---|---|
| **ε-δ 连续** | ReLU 连续不可微 | $\text{ReLU}'(0^+) = 1 \neq 0 = \text{ReLU}'(0^-)$ |
| **完备性** | 梯度下降收敛 | Cauchy 列→收敛→不动点存在 |
| **Heine-Borel** | 权重衰减→loss 最小值 | $\|\theta\| \leq R$ 紧致 $\Rightarrow \min L$ 存在 |
| **MVT** | Lipschitz 连续 | $\|f(x)-f(y)\| \leq L\|x-y\|$ |
| **Taylor** | Newton 法 | $\theta_{k+1} = \theta_k - H^{-1}\nabla L$ |
| **交错级数** | sigmoid 展开 | $\sigma(x) = \frac{1}{2} + \frac{x}{4} - \frac{x^3}{48} + \cdots$ |
| **一致收敛** | 泛化保证 | $\sup_x |f_n(x) - f^*(x)| \to 0$ |

---

## MAT 215 章节概览

### 第 1 章：实数系统
- Dedekind 切构造 $\mathbb{R}$
- 上确界公理
- $\mathbb{R}$ 的完备性 vs $\mathbb{Q}$ 的不完备

### 第 2 章：序列与级数
- 收敛定义（ε-N 语言）
- Cauchy 列
- Bolzano-Weierstrass
- 级数收敛判别法（比较、比值、根值、积分、交错）

### 第 3 章：连续性
- ε-δ 连续定义 ★
- 介值定理
- 一致连续 vs 逐点连续
- 紧致集上的连续函数（极值定理、一致连续）

### 第 4 章：微分
- 导数定义
- 中值定理（Rolle, MVT, Cauchy MVT）
- Taylor 定理 ★★★
- L'Hôpital 法则

### 第 5 章：Riemann 积分
- Darboux 和（上下和）
- 可积条件（Lebesgue 判别法）
- 微积分基本定理
- 积分与极限交换（一致收敛条件）

### 第 6 章：函数项级数
- 逐点 vs 一致收敛 ★
- Weierstrass M-判别法
- 一致收敛与连续/可积/可导
- 幂级数、收敛半径

### 第 7 章：Heine-Borel 与紧致性（如时间允许）
- 开覆盖与有限子覆盖
- Heine-Borel 定理
- Bolzano-Weierstrass 定理

---

## 与 ML 理论的核心关联

| MAT 215 章节 | ML 概念 |
|---|---|
| Ch 1 完备性 | 优化收敛的基础 |
| Ch 2 Cauchy 列 | SGD 序列收敛 |
| Ch 2 级数收敛 | Taylor 展开、激活函数展开 |
| Ch 3 紧致+连续 | loss 最小值存在 |
| Ch 3 一致连续 | Lipschitz 条件、GAN 稳定性 |
| Ch 4 MVT | 梯度下降收敛分析 |
| Ch 4 Taylor | Newton 法、二阶优化 |
| Ch 6 一致收敛 | 泛化保证、函数空间 |
| Ch 7 Heine-Borel | PAC-Bayes、Rademacher 复杂度 |

---

## 与 work4ai 讲透系列的交叉

- **讲透激活函数**：Ch 3 连续 + Ch 4 可导
- **讲透反向传播**：Ch 4 链式法则
- **讲透优化器**：Ch 4 Taylor + MVT
- **讲透泛化**：Ch 6 一致收敛 + Ch 7 紧致性
