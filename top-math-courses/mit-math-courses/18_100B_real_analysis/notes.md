# MIT 18.100B · 章节笔记（Rudin *Principles of Mathematical Analysis* 3rd ed）

> **教材**：Walter Rudin, *Principles of Mathematical Analysis* (3rd ed, McGraw-Hill, 1976) — "Baby Rudin"
> **一手核实**：ISBN 978-0070542358；全球数学本科实分析标准教材
> **视频**：[OCW 18.100A Arthur Mattuck](https://ocw.mit.edu/courses/18-100a-real-analysis-fall-2020/)

---

## 18.100 A vs B 的区别（一手核实自 MIT 18.1x 官方）

| 版本 | 焦点 | 抽象度 | 适合 |
|---|---|---|---|
| 18.100**A** | 实数轴 $\mathbb{R}$，应用导向 | 低 | 工程师入门 |
| 18.100**B** ★ | 度量空间 $\mathbb{R}^n$，点集拓扑 | 高 | 数学专业严格训练 |
| 18.100**P** | = A + 写作 (CI-M) | - | 想练写作 |
| 18.100**Q** | = B + 写作 (CI-M) | - | 想练写作 |

**18.100B 用 Rudin 第 1-8 章**（$\mathbb{R}^n$ 上的分析）。

---

## 第 1 章：The Real and Complex Number Systems

### 1.1 有序域公理

$(\mathbb{R}, +, \cdot, <)$ 满足**域公理** + **序公理**。

### 1.2 上确界公理 ★（最重要的公理）

> **Dedekind 完备性**：$\mathbb{R}$ 的每个非空有上界的子集有**最小上界**（上确界 supremum）。

$$\exists\, \sup E \in \mathbb{R}, \quad \text{s.t. } \sup E \geq x, \forall x \in E \text{ 且 } \sup E \leq b, \forall b \text{ 为 } E \text{ 的上界}$$

**为什么重要**：这是 $\mathbb{R}$ 区别于 $\mathbb{Q}$ 的根本性质。$\mathbb{Q}$ 不完备（如 $\{q \in \mathbb{Q} : q^2 < 2\}$ 在 $\mathbb{Q}$ 中无上确界）。

**ML 关联**：梯度下降收敛性证明需要完备性。

### 1.3 实数域的扩张

$\mathbb{N} \subset \mathbb{Z} \subset \mathbb{Q} \subset \mathbb{R} \subset \mathbb{C}$

### 1.4 复数域 $\mathbb{C}$

$\mathbb{C} = \{a + bi : a, b \in \mathbb{R}\}$，$i^2 = -1$。

---

## 第 2 章：Basic Topology ★

### 2.1 度量空间

$(X, d)$，$d: X \times X \to [0, \infty)$ 满足：
1. $d(x,y) \geq 0$, $d(x,y) = 0 \iff x = y$
2. $d(x,y) = d(y,x)$
3. $d(x,z) \leq d(x,y) + d(y,z)$（三角不等式）

### 2.2 开集与闭集

- **开球**：$B_r(p) = \{q : d(p,q) < r\}$
- **开集**：每点都是内点
- **闭集**：补集是开集 / 包含所有极限点

### 2.3 紧致性 ★★★

> **定义**：$K$ 是紧致的 $\iff$ 每个开覆盖有有限子覆盖。

**Heine-Borel 定理**（$\mathbb{R}^n$ 中）：$K$ 紧致 $\iff$ $K$ 有界且闭。

**紧致性的关键推论**：
- **Bolzano-Weierstrass**：有界序列有收敛子序列
- 紧致集上的连续函数**取得最大值和最小值**
- 紧致集上的连续函数**一致连续**

**ML 关联**：
- 神经网络参数空间如果限制在紧致集上 → 训练收敛性保证
- PAC-Bayes 泛化界的证明

### 2.4 完备性

- **Cauchy 序列**：$d(x_n, x_m) \to 0$ as $n,m \to \infty$
- **完备**：每个 Cauchy 序列收敛
- $\mathbb{R}$ 完备，$\mathbb{Q}$ 不完备

### 2.5 连通性

$E$ 连通 $\iff$ 不能分成两个非空分离的开集。

---

## 第 3 章：Numerical Sequences and Series ★

### 3.1 收敛序列

$\{s_n\}$ 收敛于 $s$：$\forall \epsilon > 0, \exists N, \forall n > N: |s_n - s| < \epsilon$

### 3.2 子序列

**Bolzano-Weierstrass 定理** ★：$\mathbb{R}^n$ 中的每个有界序列有收敛子序列。

### 3.3 Cauchy 序列

$\{s_n\}$ 是 Cauchy $\iff$ 收敛（在完备度量空间中）。

### 3.4 上极限与下极限

$$\limsup_{n\to\infty} s_n = \inf_{n} \sup_{k \geq n} s_k$$

### 3.5 级数收敛判别法 ★

| 判别法 | 条件 | 结论 |
|---|---|---|
| **比较** | $|a_n| \leq c_n$, $\sum c_n$ 收敛 | $\sum a_n$ 绝对收敛 |
| **比值** | $\lim \|a_{n+1}/a_n\| = L < 1$ | $\sum a_n$ 绝对收敛 |
| **根值** | $\limsup \|a_n\|^{1/n} < 1$ | $\sum a_n$ 绝对收敛 |
| **积分** | $f$ 正递减, $\int_1^\infty f$ 收敛 | $\sum f(n)$ 收敛 |
| **交错** | $a_n$ 递减趋于 0 | $\sum (-1)^n a_n$ 收敛 |
| **Dirichlet** | 部分和有界 + $a_n \to 0$ | $\sum a_n b_n$ 收敛 |

### 3.6 特殊级数

- **几何级数**：$\sum r^n = \frac{1}{1-r}$ for $|r| < 1$
- **调和级数**：$\sum 1/n = \infty$
- **$p$-级数**：$\sum 1/n^p$ 收敛 $\iff p > 1$
- **绝对收敛 vs 条件收敛**：绝对收敛级数可以任意重排

**ML 关联**：Taylor 级数收敛域 → 激活函数的展开。

---

## 第 4 章：Continuity

### 4.1 连续函数

$f$ 在 $p$ 连续 $\iff \lim_{x \to p} f(x) = f(p)$

**等价定义**：
- $\epsilon$-$\delta$
- 开集的原像是开集
- 对每个 $p$ 的邻域 $V$，$f^{-1}(V)$ 是 $p$ 的邻域

### 4.2 连续性与紧致性

**定理** ★：紧致集上的连续函数像紧致。

**推论**：紧致集 $K$ 上的连续函数 $f$ 取得最大值和最小值。

**ML 关联**：loss function 如果连续 + 参数空间紧致 → 最小值存在。

### 4.3 一致连续 ★

$f$ 一致连续 $\iff \forall \epsilon > 0, \exists \delta > 0, \forall x,y: d(x,y) < \delta \Rightarrow d(f(x),f(y)) < \epsilon$

**定理**：紧致集上的连续函数一致连续。

**ML 关联**：
- Lipschitz 连续 = 一致连续的特殊情况
- GAN 训练稳定性与 Lipschitz 条件

### 4.4 间断

- **可去间断**：左右极限存在且相等
- **跳跃间断**：左右极限存在但不等
- **本性间断**：其他

### 4.5 单调函数

单调函数的间断都是跳跃间断（至多可数个）。

---

## 第 5 章：Differentiation

### 5.1 导数定义

$$f'(x) = \lim_{h \to 0} \frac{f(x+h) - f(x)}{h}$$

### 5.2 中值定理 ★

**Rolle 定理**：$f$ 在 $[a,b]$ 连续, $(a,b)$ 可导, $f(a) = f(b)$ $\Rightarrow$ $\exists c \in (a,b): f'(c) = 0$

**中值定理 (MVT)** ★：$f$ 在 $[a,b]$ 连续, $(a,b)$ 可导 $\Rightarrow$ $\exists c: f'(c) = \frac{f(b)-f(a)}{b-a}$

**ML 关联**：梯度下降的收敛分析。

### 5.3 Taylor 定理 ★★★

$$f(x) = \sum_{k=0}^{n} \frac{f^{(k)}(a)}{k!}(x-a)^k + \frac{f^{(n+1)}(c)}{(n+1)!}(x-a)^{n+1}$$

**ML 关联**：
- 二阶 Taylor 展开 → Newton 法
- 三阶展开 → 优化算法设计
- 神经网络 loss landscape 的局部近似

### 5.4 L'Hôpital 法则

$\lim f/g = \lim f'/g'$（当右端存在且 $\lim f = \lim g = 0$ 或 $\infty$）

---

## 第 6 章：The Riemann-Stieltjes Integral

### 6.1 Riemann 积分定义

通过**分割** + **Darboux 和**：
- **上和** $U(P,f) = \sum M_i \Delta x_i$
- **下和** $L(P,f) = \sum m_i \Delta x_i$
- $f$ 可积 $\iff \sup L = \inf U$

### 6.2 可积条件

**Lebesgue 判别法**：$f$ Riemann 可积 $\iff f$ 有界且不连续点集的 Lebesgue 测度为零。

### 6.3 积分性质

- 线性
- 单调性
- 三角不等式：$|\int f| \leq \int |f|$

### 6.4 积分与极限

**控制收敛定理的雏形**：如果 $f_n \to f$ 一致, 则 $\int f_n \to \int f$。

### 6.5 微积分基本定理 ★

$$F(x) = \int_a^x f(t) dt \implies F'(x) = f(x)$$

$$F(b) - F(a) = \int_a^b F'(x) dx$$

---

## 第 7 章：Sequences and Series of Functions ★★

### 7.1 逐点收敛 vs 一致收敛 ★

- **逐点**：$f_n(x) \to f(x)$ 对每个 $x$ 单独成立
- **一致** ★：$\sup_x |f_n(x) - f(x)| \to 0$

**关键区别**：一致收敛保持连续性、可积性、可导性。

### 7.2 一致收敛判别法

**Weierstrass M-判别法**：$|f_n(x)| \leq M_n$, $\sum M_n < \infty$ $\Rightarrow$ $\sum f_n$ 一致收敛。

### 7.3 一致收敛与连续/可积/可导

| 性质 | 逐点收敛 | 一致收敛 |
|---|---|---|
| 连续性保持 | ❌ | ✅ |
| 可积交换 | ❌ | ✅ |
| 可导交换 | ❌ | 需要导函数列一致收敛 |

### 7.4 等度连续与 Arzelà-Ascoli 定理 ★

**Arzelà-Ascoli**：函数族 $\{f_\alpha\}$ 在紧致集上一致有界 + 等度连续 $\iff$ 有一致收敛子序列。

**ML 关联**：神经网络函数空间的紧致性（覆盖数的推导）。

### 7.5 Stone-Weierstrass 定理 ★

多项式在 $C([a,b])$ 中稠密——任何连续函数可用多项式一致逼近。

**ML 关联**：**Universal Approximation Theorem** 的数学根源。

---

## 第 8 章：Some Special Functions

### 8.1 幂级数

$\sum c_n z^n$，收敛半径 $R = 1/\limsup |c_n|^{1/n}$

### 8.2 指数与对数

$$e^x = \sum_{n=0}^{\infty} \frac{x^n}{n!}, \quad \ln(1+x) = \sum_{n=1}^{\infty} \frac{(-1)^{n+1} x^n}{n}$$

### 8.3 三角函数

通过幂级数定义 $\sin, \cos$。

### 8.4 Fourier 级数

$$f(x) \sim \sum_{n=-\infty}^{\infty} c_n e^{inx}, \quad c_n = \frac{1}{2\pi}\int_{-\pi}^{\pi} f(x)e^{-inx} dx$$

---

## 第 9 章：Functions of Several Variables（$\mathbb{R}^n$）

### 9.1 线性变换

矩阵表示 + 范数 $\|A\| = \sup_{\|x\| \leq 1} \|Ax\|$

### 9.2 微分 ★

$f: \mathbb{R}^n \to \mathbb{R}^m$ 在 $x$ 可微 $\iff$ 存在线性映射 $A$ 使
$$\lim_{h \to 0} \frac{\|f(x+h) - f(x) - Ah\|}{\|h\|} = 0$$

$A = f'(x)$ = **Jacobian 矩阵** ★

### 9.3 反函数定理 ★★

$$\det f'(a) \neq 0 \implies f \text{ 在 } a \text{ 附近有可微逆函数}$$

**ML 关联**：normalizing flows、变分推断。

### 9.4 隐函数定理 ★★

$$F(x,y) = 0 \text{ 且 } \frac{\partial F}{\partial y} \neq 0 \implies y = g(x) \text{ 局部存在}$$

**ML 关联**：隐式神经表示。

### 9.5 高阶导数

$C^k$ 函数 + Schwarz 定理（混合偏导与顺序无关）。

### 9.6 偏导与方向导数

### 9.7 Lagrange 乘子法 ★

约束优化 $\max f$ s.t. $g = c$ $\Rightarrow$ $\nabla f = \lambda \nabla g$

**ML 关联**：SVM 的 KKT 条件推导。

---

## 与 ML 理论的核心关联

| Rudin 章节 | ML 概念 |
|---|---|
| Ch 1 完备性 | 收敛性证明的基础 |
| Ch 2 紧致性 | PAC-Bayes, Rademacher 复杂度 |
| Ch 2 Cauchy 序列 | SGD 收敛 |
| Ch 3 级数收敛 | Taylor 展开 |
| Ch 4 一致连续 | Lipschitz 条件, GAN 稳定性 |
| Ch 5 Taylor 定理 | Newton 法, 优化 |
| Ch 5 MVT | 梯度下降分析 |
| Ch 7 一致收敛 | Neural Network 函数空间 |
| Ch 7 Stone-Weierstrass | **Universal Approximation** |
| Ch 7 Arzelà-Ascoli | 覆盖数, 泛化界 |
| Ch 9 Jacobian | 反向传播的数学本质 |
| Ch 9 反函数定理 | Normalizing Flows |
| Ch 9 Lagrange 乘子 | SVM |

---

## 与 work4ai 讲透系列的交叉

- **讲透激活函数**：Ch 4 连续性 + Ch 5 可导性
- **讲透反向传播**：Ch 9 Jacobian + 链式法则
- **讲透泛化**：Ch 2 紧致性 + Ch 7 Arzelà-Ascoli
- **讲透优化器**：Ch 5 Taylor + MVT + Ch 9 梯度
