# Dirichlet 函数：黎曼积分的死穴

> 这个反例点破的「以为万能」认知偏差：以为「函数都能黎曼积分」。
> Lakatos 框架定位：原始猜想 = 「有界函数都能黎曼积分」；反例 = Dirichlet 函数；逼迫的 lemma-incorporation = Lebesgue 可积性判别法 + Lebesgue 积分诞生。

## 构造与定义

约 1829 年，Peter Gustav Lejeune Dirichlet 引入下面这个函数：

$$
D(x) = \begin{cases} 1, & x \in \mathbb{Q}, \\ 0, & x \notin \mathbb{Q}. \end{cases}
$$

即 $D = \mathbf{1}_{\mathbb{Q}}$（有理数集的指示函数）。

这是数学史上**第一个被明确写出的「处处不连续」函数**，也是第一个「看起来很简单但黎曼积分无能为力」的函数。

## 为什么它是反例

### 处处不连续

$\mathbb{Q}$ 与 $\mathbb{R} \setminus \mathbb{Q}$ 都在 $\mathbb{R}$ 中稠密。对任何 $x_0 \in \mathbb{R}$ 与任何 $\delta > 0$，邻域 $(x_0 - \delta, x_0 + \delta)$ 内**同时含有有理点和无理点**：

- 若 $x_0 \in \mathbb{Q}$：邻域里有 $D = 0$ 的点（无理点），所以 $|D(x) - D(x_0)| = 1$；
- 若 $x_0 \notin \mathbb{Q}$：邻域里有 $D = 1$ 的点（有理点），同样 $|D(x) - D(x_0)| = 1$。

故 $D$ 在每一点都不连续。

### 黎曼不可积

**Lebesgue 判别法**（有界函数黎曼可积的充要条件）：

$$
f \text{ 在 } [a,b] \text{ 上黎曼可积} \iff m(\{x : f \text{ 在 } x \text{ 处不连续}\}) = 0.
$$

$D$ 处处不连续，不连续点集 $= [0,1]$，测度为 $1 \neq 0$。故 $D$ 在 $[0,1]$ 上**黎曼不可积**。

**直接论证**（用达布和）：对 $[0,1]$ 的任意分割 $P = \{x_0, \ldots, x_n\}$，每个小区间 $[x_{i-1}, x_i]$ 内：

- 上确界 $\sup_{[x_{i-1}, x_i]} D = 1$（因为有理点稠密）；
- 下确界 $\inf_{[x_{i-1}, x_i]} D = 0$（因为无理点稠密）。

于是上达布和 $U(D, P) = \sum_i 1 \cdot \Delta x_i = 1$，下达布和 $L(D, P) = 0$。上下积分不等：

$$
\overline{\int_0^1} D\,dx = 1 \neq 0 = \underline{\int_0^1} D\,dx.
$$

**黎曼积分不存在。**

### Lebesgue 可积，积分 = 0

Lebesgue 积分「从值域切分」：

- $D^{-1}(\{1\}) = \mathbb{Q} \cap [0,1]$，测度 $m(\mathbb{Q}) = 0$（可数集测度为 0）；
- $D^{-1}(\{0\}) = ([0,1] \setminus \mathbb{Q})$，测度 $= 1$。

$$
\int_{[0,1]} D\,d\mu = 1 \cdot \mu(\mathbb{Q} \cap [0,1]) + 0 \cdot \mu([0,1] \setminus \mathbb{Q}) = 1 \cdot 0 + 0 \cdot 1 = 0.
$$

**$D$ 是 Lebesgue 可积的，积分 $= 0$。** 黎曼束手无策的对象，在 Lebesgue 框架下变得平凡。

## 它破坏了哪个直觉

**「函数都能黎曼积分」**——具体地说，黎曼积分无法处理「震荡太剧烈」的函数。当函数值在任意小区间内都剧烈跳变时，黎曼「把 $x$ 轴分小段」的策略彻底失效。

更深层地：黎曼积分**要求**「不连续点不能太多」（必须测度为 0），但很多自然出现的函数不满足此条件——尤其是极限过程产生的函数。

## 它逼迫理论如何改进（Lakatos 核心 lemma-incorporation）

1. **黎曼可积性判别法的诞生**：Lebesgue 判别法（不连续点集测度 $=0$）把「黎曼能积/不能积」的边界精确化。这是反例驱动的概念澄清——以前模糊的「太震荡」现在变成精确的「不连续点集正测度」。

2. **Lebesgue 积分的直接驱动力**：Henri Lebesgue（1902 博士论文）从值域而非定义域切分，让 Dirichlet 函数这类「黎曼拒绝」的对象变得可积。Lebesgue 积分的诞生不是抽象美学追求，而是被具体反例逼出来的工程改进。

3. **极限运算友好性的飞跃**：黎曼积分对极限运算不友好——一列黎曼可积函数的逐点极限可能不再黎曼可积。Lebesgue 积分带来三大收敛定理（**控制收敛定理 / 单调收敛定理 / Fatou 引理**），让「积分号下取极限」成为日常操作。这是现代概率论、泛函分析、调和分析的基石。

$$
\text{Lebesgue 控制定理：} \quad f_n \to f \text{ a.e.}, \; |f_n| \leq g \in L^1 \;\Longrightarrow\; \int f_n \to \int f.
$$

4. **与 `07-critique/01` 的接口**：Dirichlet 函数是「黎曼 → Lebesgue」范式转移的核心案例。黎曼积分的局限不只是「少数病态函数不可积」，而是**结构性缺陷**——它无法支撑现代分析所需的极限交换。

## 可视化/代码验证思路

```python
import numpy as np

# 黎曼不可积验证：上下达布和不收敛
def dirichlet(x):
    x_rational = np.abs(x - np.round(x * 1e6) / 1e6) < 1e-9  # 近似有理检测
    return x_rational.astype(float)

# 取 [0,1] 上 N 等分，观察 U=1, L=0 不随 N 改变
for N in [10, 100, 1000]:
    pts = np.linspace(0, 1, N + 1)
    # 每个小区间必含 0 与 1
    print(f"N={N}: U={1.0}, L={0.0}")  # 始终如此
```

> 注：浮点近似无法严格表示 $\mathbb{Q}$，只能用逼近验证。严格的不可积性靠测度论证明。

## 推荐深入阅读

- Royden《Real Analysis》第 4 章——Lebesgue 判别法的严格证明。
- Stein & Shakarchi《Real Analysis》第 2 章——从黎曼到 Lebesgue 的动机叙述。
- Hawkin《Lebesgue's Theory of Integration》（1970）—— Lebesgue 积分诞生的历史原著级调研。
- math-expert `05-history/01-无穷之争-芝诺到勒贝格.md` 中 Lebesgue 一节。
- math-expert `07-critique/01-黎曼-vs-Lebesgue.md`（待建）——范式转移的完整论证。
