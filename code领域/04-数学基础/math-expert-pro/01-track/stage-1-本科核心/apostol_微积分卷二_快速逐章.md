# Apostol《Calculus, Volume II》第2版 · 快速逐章精读

> 基于原书：`Calculus, Volume II: Multi-Variable Calculus and Linear Algebra, with Applications (2nd ed., 1969)` by Tom M. Apostol / 读于：2026-07-02
> 定位：**Caltech 经典**，把线性代数、多元微积分、常微分方程、向量分析、概率与数值计算**一体化**的本科巨著，理论与计算并重。全书用线性代数作骨架统一后续所有主题——这是 1969 年极为前卫的「大综合」设计。
> 本文为**快速逐章精读**，每章 1 个飞腾锚点 + 1 个关键定理 + 1 道自测题。
> 前置：本仓库已读 Apostol《数学分析》(stage-1，实分析严格化) / Spivak 单变量 Calculus(stage-1，ε-δ 语言) / Thomas 多元微积分(stage-1，偏导/重积分/线面积分的计算直觉)。

---

## §0 引言：Apostol 卷二是什么，为什么读它

Tom M. Apostol(Caltech 教授，*Project Mathematics!* 创办人)的《Calculus》两卷本是 20 世纪北美最具个性的微积分教材。Vol.1 用「积分先行」颠覆传统；Vol.2(1969) 则走了一条更罕见的路——**先用 5 章严格建立线性代数（线性空间→线性变换→行列式→特征值），再用这套代数骨架统一多元微积分、ODE、向量分析**。在 1969 年，把线性代数与微积分深度交织（而非各自独立成书）是相当前卫的应用数学理念，体现了 Caltech「数学是连续的、不该被人为切割」的教学哲学。

**全书核心命题**：多元微积分的真正语言不是「一堆公式」，而是**线性代数**。多元函数的导数(Df)是线性映射（矩阵）、重积分的换元依赖行列式、ODE 系统的解由矩阵指数 $e^{At}$ 给出、向量积分定理（Green/Gauss/Stokes）本质是行列式与外微分的组合。Apostol 的策略分五块推进：

1. **Ch1-5 线性代数**：从公理化线性空间出发，经线性变换/矩阵、行列式，到特征值与对角化——这是全书代数引擎；
2. **Ch5-6 常微分方程**：一阶 ODE 的存在唯一性，到线性 ODE 系统的 $e^{At}$ 解法（直接调用 Ch4 特征值）；
3. **Ch7-11 多元微积分与向量分析**：向量场(grad/curl/div)、线积分、重积分、三大积分定理(Green/Gauss/Stokes)、微分形式统一；
4. **Ch12-14 应用**：概率论、数值计算、最优化——三块纯应用章，体现「数学为应用服务」。

**与已读教材的关系**：

- 已读 **Apostol 数学分析** = 卷二的实分析升级版（测度论、Fourier），卷二是其多元+线代+ODE 的工程化前身；
- 已读 **Spivak 单变量** = 卷二多元微积分的 $\varepsilon$-$\delta$ 严格性源头，卷二把它推广到 $n$ 维；
- 已读 **Thomas 多元** = 卷二的「计算直觉版」，卷二补上线性代数严格性与 ODE。

**与三本同类经典的对比**（决定你该读哪本）：

| 书 | 风格 | 主线侧重 | 适合谁 |
|:-:|------|---------|--------|
| **Apostol 卷二** (1969) | 公理化线性代数开路，理论严格但计算实例充足；**最全面**（线代+多元+ODE+概率+数值+优化全收） | 线性代数作骨架统一多元微积分+ODE+向量分析 | 想要线代+微积分+ODE 一站式严格训练，理论与计算平衡 |
| **Spivak** Manifolds (1965) | 极致凝练 120 页，证明优雅但跳跃大 | 微分形式 → Stokes 统一为唯一主线（Ch5 占 1/4 篇幅） | 已读单变量 Spivak，喜欢「一个定理统一一切」 |
| **Courant** 卷二 (1934) | 物理直觉驱动，应用（力学/电磁）极其丰富，老派叙事 | 多元微积分+变分法+ODE，**物理应用**为脉络 | 需要物理直觉和经典力学/电磁学的真实应用背景 |
| **Thomas** 多元 (现代) | 计算导向，工程友好，图示多 | 偏导技巧/重积分换序/线面积分参数化的**工程计算** | 工程师，只要会用多元微积分做计算 |

**建议路线**：Thomas 多元（计算直觉，已完成）→ Apostol 卷二（严格化 + 线代 + ODE + 应用大综合）→ Spivak Manifolds（Stokes 统一的纯粹形式化）。若 Apostol 某章卡住（如 Ch4 Cayley-Hamilton、Ch6 矩阵指数），可切 Strang 线性代数（直观）或 Halmos《有限维向量空间》（抽象严格）对照。

**Apostol 卷二的叙事弧线**：全书有一条清晰的「从代数到分析到应用」弧线——Ch1-5 是纯代数（抽象线性空间），Ch7-11 用代数工具重讲多元微积分（导数=矩阵、积分=Jacobian），Ch12-14 落地到概率/数值/优化。读者需要接受这种「先建代数引擎再驱动分析」的结构——它使后续每个多元概念都能找到线性代数根基。

**零基础工程师阅读建议**：

- **Ch1-5 线代是甜区**——配合 Halmos《有限维向量空间》或本仓库 LADR 笔记，务必手算每个基变换与特征分解；
- **Ch5-6 ODE** 的矩阵指数 $e^{At}$ 是第一个硬骨头，建议手算 $2\times2$ 案例验证对角化 $e^{At}=Pe^{\Lambda t}P^{-1}$；
- **Ch9-10 多重积分+三大定理**是分析核心，务必死磕换元公式（Jacobian）与 Green/Gauss/Stokes 三大定理的几何意义；
- **Ch11 微分形式**是高潮，Apostol 比同时代教材更早把外微分写进本科，是 Spivak Manifolds 的前置。

全书精读约 60-80 小时（每周 10-20h，4-5 周）。

> 🟢 事实可作锚点：Apostol 的秩-零度定理、Cayley-Hamilton、换元公式、三大积分定理、ODE 存在唯一性均为严格定理。
> 🟡 类比（矩阵指数 = 「ODE 的状态转移」、外微分 = 「方向敏感的体积元素」）仅供直觉，**绝不在严格证明中引用**。

---

## §1 全书 14 章骨架一览（飞腾锚点分布）

| 章 | 标题 | 核心概念 | 飞腾锚点 |
|:-:|------|---------|---------|
| 1 | 线性空间 | 公理化向量空间、子空间、基与维数 | **Schmidt 正交** |
| 2 | 线性变换与矩阵 | 线性映射↔矩阵、复合=矩阵乘、秩-零度 | **matmul 15×[V03]** ⭐线性代数 |
| 3 | 行列式 | 多重线性交替公理、$\det(AB)=\det A\det B$、Cramer | **GEMM 大规模** |
| 4 | 特征值与特征向量 | 特征多项式、对角化、Cayley-Hamilton | **TLB 局部** |
| 5 | 常微分方程 | 一阶 ODE、存在唯一性(Picard)、分离变量 | **分支预测** ⭐ODE 分支 |
| 6 | 线性微分方程组 | 矩阵指数 $e^{At}$、状态转移、$x'=Ax$ | **matmul 15×[V03]** ⭐线性代数 |
| 7 | 向量分析 | 梯度/散度/旋度、方向导数、链式法则 | **FP16 3.81×[L01]** |
| 8 | 线积分 | 线积分定义、保守场、势函数、路径无关 | **UDOT 16.9×[E05]** ⭐积分 |
| 9 | 多重积分 | Fubini、换元(Jacobian)、重积分 | **UDOT 16.9×[E05]** ⭐积分 |
| 10 | 向量积分定理 | Green / Gauss 散度 / Stokes | **TLB 局部** |
| 11 | 微分形式 | 外微分 $d$、$d^2=0$、统一 Stokes | **Iron Law <2%[Lab00]** ⭐误差 |
| 12 | 概率论引论 | 概率公理、期望、方差、大数定律 | **GEMM 大规模** |
| 13 | 数值计算 | Newton 法、插值、数值积分、误差界 | **Iron Law <2%[Lab00]** ⭐误差 |
| 14 | 最优化引论 | 极值、Lagrange 乘子、梯度下降 | **分支预测** ⭐ODE 分支 |

**两条主线**：

1. **代数主线**——线性空间(Ch1) → 线性变换/矩阵(Ch2) → 行列式(Ch3) → 特征值(Ch4) → 矩阵指数驱动 ODE(Ch6) → Jacobian 驱动重积分(Ch9) → 外微分统一(Ch11)。线性代数是全书引擎。
2. **分析主线**——一阶 ODE(Ch5) → 线性 ODE 系统(Ch6) → 向量场微积分(Ch7) → 线积分(Ch8) → 重积分(Ch9) → 三大定理(Ch10) → 微分形式统一(Ch11)。

两条线在 **Ch11 微分形式 + Ch6 矩阵指数**处交汇——线性代数（外代数、特征值）与分析（积分定理、ODE）合流。

---

### 第 1 章 · Linear Spaces（线性空间）⭐

> 公理化向量空间 / 子空间 / 线性无关 / 基与维数 / 有限维空间基存在定理

- **核心**：用 8 条公理（加法交换群 + 标量域作用 + 分配/结合）定义线性空间，比 $\mathbb{R}^n$ 更抽象。子空间、线性组合、张成空间、线性无关、基、维数 $\dim V$。Apostol 先证「有限生成空间必有有限基」，维数良定义。这是全书代数地基——后续矩阵、行列式、特征值都建立在「线性空间」之上。
- **飞腾锚点**：**Schmidt 正交** —— 线性空间的核心是「基底选择」，内积空间下 Gram-Schmidt 给出标准正交基，使后续矩阵表示、QR 分解、最小二乘在最简坐标架下运算。
  - 🟢事实：标准正交基下内积退化为点积 $\langle x,y\rangle=x\cdot y$，坐标变换不引入范数失真。
  - 🟡类比：基 = 「坐标系」，正交基 = 「校准过的直角坐标系」，计算最简。
- **几何/应用**：线性空间统一了 $\mathbb{R}^n$、多项式空间、函数空间（$C[a,b]$）、解空间；ML 中特征空间是 $\mathbb{R}^d$，词向量(word embedding)是线性空间的点；ODE 齐次解集是线性子空间（叠加原理）。
- **关键定理**：**基存在定理**（有限生成线性空间必有基，且任两组基元素个数相同 = $\dim V$）+ **维数公式**（$W_1,W_2$ 子空间则 $\dim(W_1+W_2)=\dim W_1+\dim W_2-\dim(W_1\cap W_2)$）。
- **自测**：证明多项式空间 $P_n$（次数 $\le n$）的维数是 $n+1$；$\mathbb{R}^{3\times3}$（$3\times3$ 实矩阵）的维数是多少？

---

### 第 2 章 · Linear Transformations and Matrices（线性变换与矩阵）⭐⭐

> 线性映射 $T:V\to W$ / 核(kernel)与像(image) / 矩阵表示 / 矩阵乘法=复合 / 秩-零度定理

- **核心**：线性变换 $T$ 保持加法与标量乘（$T(ax+by)=aT(x)+bT(y)$）；选基后 $T$ 对应矩阵 $[T]$；**复合对应矩阵乘法** $[S\circ T]=[S][T]$。核 $\ker T$（映到零的子空间）与像 $\operatorname{im}T$；**秩-零度定理** $\dim V=\dim\ker T+\dim\operatorname{im}T$ 是线性代数第一定理——它把「映射丢失多少信息」($\dim\ker$) 与「保留多少信息」($\operatorname{rank}$) 量化。
- **飞腾锚点**：**matmul 15×[V03]** ⭐线性代数 —— 线性变换 = 矩阵，复合 = 矩阵乘；一切线性代数计算（基变换、特征分解、ODE 系统）最终退化为密集矩阵乘 = matmul。
  - 🟢事实：$T(v)=[T]_{\mathcal{B}'}^{\mathcal{B}}\cdot[v]_{\mathcal{B}}$，基变换 = 矩阵乘；神经网络的每一层 $y=\sigma(Wx+b)$ 的 Jacobian 是 $W$ 的扰动。
  - 🟡类比：矩阵 = 「线性变换的坐标记录」；矩阵乘 = 「变换的接力赛」。
- **几何/应用**：秩-零度定理是「信息守恒律」——满射(像=全空间)当且仅当核最小；ML 中 $W$ 降维（PCA）时 $\dim\ker>0$ 意味着信息有损；可逆变换 ⟺ $\ker T=\{0\}$ ⟺ 方阵满秩。
- **关键定理**：**秩-零度定理**(rank-nullity) $\dim V=\dim\ker T+\operatorname{rank}T$；**矩阵乘法对应复合** $[S\circ T]=[S][T]$。
- **自测**：$T:\mathbb{R}^3\to\mathbb{R}^2$, $T(x,y,z)=(x+y,y+z)$，求 $\ker T$、$\operatorname{im}T$ 并验证秩-零度定理。

---

### 第 3 章 · Determinants（行列式）⭐⭐

> 行列式公理化（多重线性+交替+归一）/ $\det(AB)=\det A\det B$ / 伴随矩阵 / Cramer 法则 / 体积解释

- **核心**：Apostol 不用 Leibniz 展开式定义 $\det$，而用三条公理（对行多重线性 + 交替 + $\det I=1$）**唯一刻画**行列式，再推出展开公式与乘法公式。几何上 $|\det A|$ = 线性变换的体积缩放因子。伴随矩阵 $A^*$ 给出 $A^{-1}=A^*/\det A$（$\det\neq0$ 时）；Cramer 法则用行列式解 $Ax=b$。
- **飞腾锚点**：**GEMM 大规模** —— $\det$ 的展开式（$n!$ 项）计算上昂贵，实际用 LU 分解 $\det A=\prod U_{ii}$（$O(n^3)$）；大规模矩阵的行列式/求逆本质是 GEMM 大规模密集运算。
  - 🟢事实：$\det(AB)=\det A\det B$ 使「复合变换的体积缩放 = 各步缩放之积」；ML 中高斯分布归一化常数 $1/\sqrt{(2\pi)^n\det\Sigma}$ 依赖 $\det$。
  - 🟡类比：$\det$ = 「线性变换的体积敏感度」；$\det=0$ = 「把空间压扁」（降维，信息损失）。
- **几何/应用**：$\det$ 判断可逆性（$\det\neq0$ ⟺ 可逆）；换元公式的 Jacobian 行列式（Ch9）；概率分布变换的体积校正（normalizing flow）。
- **关键定理**：**乘法公式** $\det(AB)=\det A\cdot\det B$；**Cramer 法则**（$A$ 可逆则 $x_i=\det A_i/\det A$，$A_i$ 为换第 $i$ 列）。
- **自测**：用三条公理推出「两行相同则 $\det=0$」；验证旋转矩阵 $\begin{pmatrix}\cos\theta&-\sin\theta\\\sin\theta&\cos\theta\end{pmatrix}$ 的 $\det=1$（保面积保定向）。

---

### 第 4 章 · Eigenvalues and Eigenvectors（特征值与特征向量）⭐⭐⭐

> 特征值/特征向量 / 特征多项式 / 代数重数与几何重数 / 对角化 / Cayley-Hamilton 定理

- **核心**：$Av=\lambda v$（特征向量方向上 $A$ 只缩放）；特征多项式 $p(\lambda)=\det(A-\lambda I)$；代数重数（根的重数）vs 几何重数（特征空间维数），后者 $\le$ 前者；**对角化** $A=PDP^{-1}$（$D$ 对角）当且仅当 $A$ 有 $n$ 个线性无关特征向量；**Cayley-Hamilton 定理**——矩阵满足自己的特征多项式 $p(A)=0$，这是本章的灵魂定理，给出 $A^{-1}$ 用 $A$ 的多项式表达的途径。
- **飞腾锚点**：**TLB 局部** —— 幂迭代法 $v_{k+1}=Av_k/\|Av_k\|$ 求（按模）最大特征值，本质是反复矩阵-向量乘，向量 $v_k$ 的访问局部性决定 TLB 命中率与收敛速度。
  - 🟢事实：Cayley-Hamilton 保证 $A^{-1}$（$\det\neq0$ 时）是 $A$ 的多项式，$2\times2$ 可显式写 $A^{-1}=(\operatorname{tr}A\cdot I-A)/\det A$。
  - 🟡类比：特征向量 = 「变换的不动方向」（只缩放不旋转）；PageRank 就是幂迭代求 Google 矩阵最大特征值 1 的特征向量。
- **几何/应用**：对称矩阵特征值全实、可正交对角化（谱定理预告）；主成分分析(PCA)用协方差矩阵特征值排序；Google PageRank；振动的固有频率 = 刚度矩阵特征值。
- **关键定理**：**Cayley-Hamilton 定理** $p(A)=0$（$p$ 为 $A$ 的特征多项式）；**对角化判据**（$n$ 个线性无关特征向量 ⟺ 可对角化）。
- **自测**：$A=\begin{pmatrix}2&1\\0&2\end{pmatrix}$ 能否对角化？（提示：代数重数 2，几何重数 1）。用 Cayley-Hamilton 求 $A^{-1}$（$\det\neq0$）。

---

### 第 5 · Linear Differential Equations（常微分方程）⭐⭐

> 一阶 ODE / 存在唯一性（Picard-Lindelöf）/ 分离变量 / 一阶线性 ODE / 积分因子 / 二阶线性

- **核心**：一阶 ODE $y'=f(t,y)$；**Picard-Lindelöf 存在唯一性定理**（$f$ 关于 $y$ Lipschitz ⟹ 局部唯一解）；分离变量法、一阶线性 $y'+p(t)y=q(t)$ 的积分因子法（解 $y=e^{-\int p}(C+\int qe^{\int p})$）；二阶常系数线性 ODE $y''+ay'+by=0$ 用特征方程 $r^2+ar+b=0$ 求解。本章是 Ch6 线性 ODE 系统的单变量原型。
- **飞腾锚点**：**分支预测** ⭐ODE 分支 —— ODE 求解器（Runge-Kutta）每步依据 $f(t,y)$ 的局部行为分支（刚性/非刚性、显式/隐式），判别根/判别式（$r^2+ar+b=0$ 的实根/复根/重根）决定解的结构（指数/振荡/临界）——一连串条件分支。
  - 🟢事实：Picard 迭代 $y_{n+1}(t)=y_0+\int_0^t f(s,y_n(s))ds$ 收敛到唯一解，是存在性证明的构造性核心，也是数值 ODE（Euler/RK）的理论根基。
  - 🟡类比：存在唯一性 = 「只要力场光滑，轨迹就唯一确定」（决定论）；复根 = 振荡（如弹簧-质量-阻尼系统）。
- **几何/应用**：ODE 是物理建模的核心语言（牛顿第二定律 $F=ma$ 是二阶 ODE）；RLC 电路、种群动力学（Logistic）、传染病 SIR 模型；ML 中梯度下降轨迹是 ODE $x'(t)=-\nabla f$。
- **关键定理**：**Picard-Lindelöf 存在唯一性**（$f$ 连续且对 $y$ Lipschitz ⟹ 初值问题局部唯一解）；**一阶线性 ODE 通解** $y=e^{-\int p}(C+\int qe^{\int p}\,dt)$。
- **自测**：解 $y'+2y=e^{-t}$；判断 $y'=\sqrt{y}$（$y(0)=0$）是否满足存在唯一性（不满足，$f$ 在 $y=0$ 非 Lipschitz）。

---

### 第 6 章 · Systems of Differential Equations（线性微分方程组）⭐⭐⭐

> 一阶线性 ODE 系统 $\mathbf{x}'=A\mathbf{x}$ / 矩阵指数 $e^{At}$ / 状态转移矩阵 / 对角化解法 / 非齐次

- **核心**：一阶线性常系数系统 $\mathbf{x}'=A\mathbf{x}$ 的解由**矩阵指数** $e^{At}=\sum_{k=0}^\infty \frac{(At)^k}{k!}$ 给出：$\mathbf{x}(t)=e^{At}\mathbf{x}(0)$。当 $A$ 可对角化（$A=PDP^{-1}$），$e^{At}=Pe^{\Lambda t}P^{-1}$（$e^{\Lambda t}$ 对角元 $e^{\lambda_i t}$）——**直接调用 Ch4 特征值**。非齐次 $\mathbf{x}'=A\mathbf{x}+\mathbf{b}(t)$ 用变动常数法。本章是线性代数（Ch1-4）与 ODE（Ch5）的合流。
- **飞腾锚点**：**matmul 15×[V03]** ⭐线性代数 —— $e^{At}$ 的计算（缩放-平方法 $e^{A}=e^{A/2^s})^{2^s}$）本质是密集矩阵乘幂（matmul）；大规模 ODE 系统（如化学反应网络）的数值积分完全靠 matmul 驱动。
  - 🟢事实：特征值实部 $>0$ ⟹ 解指数增长（不稳定），实部 $<0$ ⟹ 衰减（稳定），纯虚 ⟹ 振荡；这是线性系统稳定性判据。
  - 🟡类比：矩阵指数 = 「ODE 的状态转移矩阵」——把初态「搬运」到 $t$ 时刻；$e^{At}$ = 线性变换的「时间演化算子」。
- **几何/应用**：耦合振子、电路网络、控制论的状态空间模型；特征值决定系统定性（稳定/振荡/发散）；ML 中连续深度网络（Neural ODE）的隐藏状态演化 $h'(t)=f(h(t),\theta)$。
- **关键定理**：**矩阵指数解** $\mathbf{x}(t)=e^{At}\mathbf{x}_0$（$\mathbf{x}'=A\mathbf{x}$）；**对角化解法** $A=PDP^{-1}\Rightarrow e^{At}=P\operatorname{diag}(e^{\lambda_i t})P^{-1}$。
- **自测**：解 $\mathbf{x}'=\begin{pmatrix}0&1\\-1&0\end{pmatrix}\mathbf{x}$（提示：特征值 $\pm i$，解为旋转）；写出 $e^{At}$ 并解释其几何意义（圆周运动）。

---

### 第 7 章 · Vector Calculus / Vector Analysis（向量分析）⭐⭐

> 标量场与向量场 / 梯度 $\nabla f$ / 方向导数 / 散度 $\nabla\cdot\mathbf{F}$ / 旋度 $\nabla\times\mathbf{F}$ / 链式法则 / Hessian

- **核心**：标量场 $f:\mathbb{R}^n\to\mathbb{R}$ 的**梯度** $\nabla f=(\partial f/\partial x_1,\ldots)$ 指向最快上升方向；方向导数 $D_\mathbf{v}f=\nabla f\cdot\mathbf{v}$；向量场 $\mathbf{F}$ 的**散度** $\nabla\cdot\mathbf{F}=\sum\partial F_i/\partial x_i$（源/汇强度）与**旋度** $\nabla\times\mathbf{F}$（环流强度）；多元链式法则 $\frac{df}{dt}=\nabla f\cdot\mathbf{r}'(t)$；Hessian 矩阵 $H_{ij}=\partial^2f/\partial x_i\partial x_j$（对称）。
- **飞腾锚点**：**FP16 3.81×[L01]** —— 梯度/散度/旋度的有限差分离散（$\partial f/\partial x\approx[f(x+h)-f(x)]/h$）是逐点运算，混合精度训练用 FP16 计算 $\nabla f$ 加速 3.81×，代价是导数数值误差放大（FP16 精度缝隙）。
  - 🟢事实：$\nabla f$ 是 $Df$ 的转置（$m=1$ 时）；Hessian 对称（Clairaut）$\Rightarrow$ 特征值全实（Ch4）；梯度下降 $x_{k+1}=x_k-\eta\nabla f$。
  - 🟡类比：梯度 = 「山坡最陡上升方向」；散度 = 「每点的净流出量」（正=源，负=汇）；旋度 = 「每点的小漩涡强度」。
- **几何/应用**：梯度下降是 ML 训练的引擎；散度定理（Ch10）将体积积分转为曲面积分（电磁学 Gauss 定律）；旋度是流体涡旋、磁场（Ampère 定律）的语言。
- **关键定理**：**链式法则**（$f(\mathbf{r}(t))$ 的导数 $=\nabla f\cdot\mathbf{r}'$）；**$\nabla\times(\nabla f)=0$**（保守场无旋）+ **$\nabla\cdot(\nabla\times\mathbf{F})=0$**（散度无源场的旋度恒零）。
- **自测**：求 $f(x,y,z)=x^2y+z^3$ 在 $(1,2,1)$ 沿 $\mathbf{v}=(1,1,1)/\sqrt3$ 的方向导数；验证 $\nabla\times(\nabla f)=0$。

---

### 第 8 章 · Line Integrals（线积分）⭐

> 标量场线积分 / 向量场线积分 $\int_C\mathbf{F}\cdot d\mathbf{r}$ / 保守场 / 势函数 / 路径无关 / $\oint\nabla f\cdot d\mathbf{r}=0$

- **核心**：向量场沿曲线 $C$ 的线积分 $\int_C\mathbf{F}\cdot d\mathbf{r}=\int_a^b\mathbf{F}(\mathbf{r}(t))\cdot\mathbf{r}'(t)\,dt$ = 力沿路径做功。**保守场**（$\mathbf{F}=\nabla f$）的线积分**路径无关**，只依赖端点 $\int_C\nabla f=f(\text{终})-f(\text{起})$；$\mathbf{F}$ 保守 ⟺ $\oint_C\mathbf{F}\cdot d\mathbf{r}=0$（任意闭曲线）⟺ $\nabla\times\mathbf{F}=0$（单连通域）。势函数 $f$ 的存在性 = 保守性。
- **飞腾锚点**：**UDOT 16.9×[E05]** ⭐积分 —— 线积分 $\int\mathbf{F}\cdot d\mathbf{r}$ 离散化为 $\sum\mathbf{F}(\mathbf{r}_i)\cdot\Delta\mathbf{r}_i$ = 加权点积累加，正是 UDOT（无符号点积/内积）指令的核心场景。
  - 🟢事实：保守场线积分 = 势函数差（与路径无关），这是「势能」概念（重力、静电）的数学基础。
  - 🟡类比：保守场 = 「能量守恒的力场」（绕一圈做功为零）；非保守场 = 「有摩擦/耗散」（如磁场对运动电荷做功转化为路径）。
- **几何/应用**：物理中保守力（重力、库仑力）做功 = 势能差；静电势 $\phi$ 满足 $\mathbf{E}=-\nabla\phi$；ML 中沿梯度方向的「功」= 损失下降量。
- **关键定理**：**保守场等价条件**（$\mathbf{F}=\nabla f$ ⟺ 路径无关 ⟺ 任意闭曲线积分为零 ⟺ $\nabla\times\mathbf{F}=0$（单连通））；**势函数求法** $f=\int F_x\,dx+g(y,z)$。
- **自测**：判断 $\mathbf{F}=(2xy,x^2)$ 是否保守并求势函数；计算 $\int_C(2xy\,dx+x^2\,dy)$ 沿 $C:y=x^2$ 从 $(0,0)$ 到 $(1,1)$。

---

### 第 9 章 · Multiple Integrals（多重积分）⭐⭐

> 二重/三重积分 / 累次积分 / Fubini 定理 / 换元公式(Jacobian) / 极坐标与球坐标 / 应用（质心、转动惯量）

- **核心**：$\iint_D f\,dA$ 由 Riemann 和极限定义；**Fubini 定理**把二重积分降为累次一维积分 $\iint_D f\,dxdy=\int[\int f\,dy]dx$；**换元公式** $\iint_{D'}f(x,y)\,dxdy=\iint_D f(g(u,v))|\det Dg|\,dudv$，$|\det Dg|$ = Jacobian = 坐标变换下的面积微元缩放（**直接调用 Ch3 行列式**）。极坐标 $dA=r\,drd\theta$、球坐标 $dV=\rho^2\sin\phi\,d\rho d\phi d\theta$。
- **飞腾锚点**：**UDOT 16.9×[E05]** ⭐积分 —— 重积分的数值离散（梯形/Simpson 嵌套）= 多维加权求和 = 密集点积累加，UDOT 加速；Monte Carlo 积分 $\frac1N\sum f(\mathbf{x}_i)$ 也是点积累加。
  - 🟢事实：换元的 $|\det Dg|$ 保证面积/体积守恒（极坐标 $r\,drd\theta$ 补偿远离原点的网格拉伸）。
  - 🟡类比：Fubini = 「逐列再逐行求和」(分治)；换元 = 「换坐标系时校正网格扭曲」。
- **几何/应用**：质心 $\bar{x}=\iint x\rho\,dA/\iint\rho\,dA$、转动惯量 $I=\iint r^2\rho\,dA$；概率论（Ch12）中联合密度积分；Monte Carlo、数值积分；ML 中高斯分布归一化。
- **关键定理**：**Fubini 定理**（$f$ 连续 ⟹ 累次积分可换序且等于重积分）；**换元公式** $\iint_{g(D)}f=\iint_D(f\circ g)|\det Dg|$。
- **自测**：用极坐标算单位圆面积（得 $\pi$）；用球坐标算单位球体积（得 $4\pi/3$）；为何极坐标 $dA=r\,drd\theta$ 多了个 $r$？

---

### 第 10 章 · Vector Integral Theorems（向量积分定理：Green / Gauss / Stokes）⭐⭐⭐

> Green 定理（平面）/ Gauss 散度定理（三维体积↔曲面）/ Stokes 定理（曲面↔边界曲线）/ 统一视角

- **核心**：三大定理把「区域内部积分」转化为「边界积分」：
  - **Green**（$\mathbb{R}^2$）：$\oint_{\partial D}P\,dx+Q\,dy=\iint_D(\partial_x Q-\partial_y P)\,dA$
  - **Gauss 散度**（$\mathbb{R}^3$）：$\oiint_{\partial V}\mathbf{F}\cdot d\mathbf{S}=\iiint_V\nabla\cdot\mathbf{F}\,dV$（通量=总源强）
  - **Stokes**（$\mathbb{R}^3$ 曲面）：$\oint_{\partial S}\mathbf{F}\cdot d\mathbf{r}=\iint_S(\nabla\times\mathbf{F})\cdot d\mathbf{S}$（环量=总旋度）
  三者形式统一为「内部微分 ⟺ 边界积分」。Apostol 强调三者都是 FTC 的高维推广。
- **飞腾锚点**：**TLB 局部** —— Fubini 换序与分区积分将二维积分切分为条带，每条带 = 一个内存局部块；数值实现曲面/体积网格的局部性决定 TLB 命中与缓存效率。
  - 🟢事实：Green 是 Stokes 在平面（$\mathbb{R}^2$）的特例；Gauss 是 Stokes 在三维体积的「高维版」；三者最终被 Ch11 微分形式的 $\int_M d\omega=\int_{\partial M}\omega$ 统一。
  - 🟡类比：Gauss = 「流域总流量 = 出口流量之和」（河流汇入湖）；Stokes = 「漩涡总强度 = 沿边界的环流」。
- **几何/应用**：Maxwell 方程组（Gauss 电定律 $\nabla\cdot\mathbf{E}=\rho/\varepsilon_0$、Faraday $\nabla\times\mathbf{E}=-\partial_t\mathbf{B}$）；流体通量；Green 在平面热传导/电场；这是工程电磁、流体力学的数学基础。
- **关键定理**：**Gauss 散度定理** $\oiint_{\partial V}\mathbf{F}\cdot d\mathbf{S}=\iiint_V\nabla\cdot\mathbf{F}\,dV$；**Stokes 定理** $\oint_{\partial S}\mathbf{F}\cdot d\mathbf{r}=\iint_S(\nabla\times\mathbf{F})\cdot d\mathbf{S}$。
- **自测**：用 Green 算 $\oint_{x^2+y^2=1}(x\,dy-y\,dx)$（应得 $2\pi$ = 面积公式）；用 Gauss 验证点电荷电场穿过球面的通量 = $q/\varepsilon_0$。

---

### 第 11 章 · Differential Forms（微分形式）⭐⭐⭐⭐

> wedge 积 ∧ / 微分形式 / 外微分 $d$ / $d^2=0$ / 统一 Stokes 定理 $\int_M d\omega=\int_{\partial M}\omega$

- **核心**：$k$-形式 $\omega=\sum a_I\,dx^{i_1}\wedge\cdots\wedge dx^{i_k}$，wedge 反对称（$dx\wedge dy=-dy\wedge dx$）；**外微分** $d$ 满足 $d(df)=\sum\partial_i f\,dx^i$，核心性质 **$d^2=0$**。$\mathbb{R}^3$ 中：$d$ 对 0-形式 = grad，1-形式 = curl，2-形式 = div——**三算子统一为 $d$**。**统一 Stokes 定理** $\int_M d\omega=\int_{\partial M}\omega$ 一行收编 FTC / Green / Gauss / 经典 Stokes。Apostol 比同时代更早把外微分写进本科，是 Spivak Manifolds 的前置。
- **飞腾锚点**：**Iron Law <2%[Lab00]** ⭐误差 —— 外微分把 grad/curl/div 收编为一个算子 $d$，$d^2=0$ 即 $\nabla\times\nabla f=0$、$\nabla\cdot\nabla\times\mathbf{F}=0$——「恒等式零误差」是结构对称性的体现，类比数值逼近的「铁律 <2% 误差」靠结构保证而非巧合。
  - 🟢事实：$d^2=0$ ⟹ 「边界的边界为空」$\partial(\partial M)=\varnothing$（Ch10 三定理符号正确性的根源）；de Rham 上同调 $H^k=\ker d/\operatorname{im}d$ 从此出发。
  - 🟡类比：微分形式 = 「带方向与体积的积分元素」；$d$ = 「方向敏感的求导」；统一 Stokes = 「内部导数的积分 = 边界积分」。
- **几何/应用**：Maxwell 方程组用形式写为 $dF=0$、$d{*}F=J$（规范场论语言）；de Rham 上同调是拓扑不变量（流形「洞」的计数）；这是现代微分几何（Spivak Manifolds、Bott-Tu）的起点。
- **关键定理**：**统一 Stokes 定理** $\boxed{\int_M d\omega=\int_{\partial M}\omega}$（$k$ 形式在 $k$ 维带边流形）；推论 $d^2=0$。
- **自测**：写出 $\omega=P\,dx+Q\,dy$ 的 $d\omega$ 并代入统一 Stokes 得 Green 定理；验证 $d(df)=0$ 即 $\nabla\times(\nabla f)=0$。

---

### 第 12 章 · Introduction to Probability Theory（概率论引论）⭐

> 概率公理（Kolmogorov）/ 随机变量 / 期望与方差 / 大数定律 / 中心极限定理

- **核心**：Kolmogorov 三公理（非负、规范、可列可加）定义概率空间；随机变量、分布函数、密度；**期望** $E[X]=\int x\,f(x)dx$（积分，调用 Ch9）、**方差** $\operatorname{Var}(X)=E[(X-\mu)^2]$；**大数定律**（频率收敛到概率）与**中心极限定理**（和的分布趋正态）。本章是应用章，把前面积分工具用于概率。
- **飞腾锚点**：**GEMM 大规模** —— 期望/方差/协方差的计算 $E[XX^T]=\int xx^Tf(x)dx$ 离散化后是大规模外积累加（协方差矩阵）；统计推断、MCMC 采样本质是大规模密集运算。
  - 🟢事实：$E[X]=\int xf$（连续）或 $\sum xp$（离散）= 加权平均 = 内积；方差 = 二阶矩。
  - 🟡类比：大数定律 = 「样本越多估计越准」（赌场长期盈利的数学根基）；中心极限 = 「很多独立小扰动之和趋正态」。
- **几何/应用**：统计推断（极大似然、贝叶斯）；ML 中期望风险最小化、KL 散度；金融（期权定价 Black-Scholes 用 CLT）；蒙特卡洛。
- **关键定理**：**大数定律**（$X_i$ 独立同分布则 $\bar{X}_n\to\mu$ a.s.）；**中心极限定理**（$\sqrt{n}(\bar{X}_n-\mu)/\sigma\to\mathcal{N}(0,1)$）。
- **自测**：$X\sim\text{Exp}(\lambda)$，求 $E[X]$ 与 $\operatorname{Var}(X)$；用 CLT 解释为何多次掷骰子和近似正态。

---

### 第 13 章 · Numerical Computation（数值计算）⭐⭐

> 误差来源（截断/舍入）/ Newton 迭代 / 插值（Lagrange）/ 数值积分（梯形/Simpson）/ ODE 数值解（Euler/RK）/ 条件数

- **核心**：**截断误差**（方法近似，如 Taylor 截断）vs **舍入误差**（浮点有限位）；**Newton 迭代** $x_{n+1}=x_n-f(x_n)/f'(x_n)$（二次收敛，需 $\det Df\neq0$，调用 Ch2-4）；**Lagrange 插值**；数值积分（梯形 $O(h^2)$、Simpson $O(h^4)$）；**Euler 法** $y_{n+1}=y_n+hf(t_n,y_n)$ 与 Runge-Kutta；**条件数** $\kappa$ 衡量问题对扰动的敏感度。本章是「理论与计算的桥梁」。
- **飞腾锚点**：**Iron Law <2%[Lab00]** ⭐误差 —— 数值计算的核心是误差控制：截断误差 $O(h^k)$ + 舍入误差 $O(\varepsilon/h)$ 的权衡使最优步长存在（如数值微分 $h\sim\sqrt\varepsilon$）；「铁律 <2%」= 误差预算的结构性约束，靠算法设计（如 RK 高阶、条件预优）保证。
  - 🟢事实：Newton 法二次收敛 $|e_{n+1}|\le C|e_n|^2$（$\det Df\neq0$ 处）；病态问题（$\kappa\gg1$）即使算法正确结果误差也大。
  - 🟡类比：截断误差 = 「砍掉 Taylor 高阶项的代价」；舍入误差 = 「浮点有限位的代价」；两者此消彼长。
- **几何/应用**：科学计算（PDE 数值解、CFD）；ML 中优化器（Adam = 梯度下降 + 自适应步长）；计算机图形学（Newton 求交）；libm 数学库。
- **关键定理**：**Newton 二次收敛**（$f\in C^2$, $f'(r)\neq0$ ⟹ 迭代二次收敛到根）；**Simpson 误差** $O(h^4)$。
- **自测**：用 Newton 法求 $\sqrt{2}$（迭代 $x_{n+1}=(x_n+2/x_n)/2$）；为何数值微分 $f'(x)\approx[f(x+h)-f(x)]/h$ 的最优步长是 $h\sim\sqrt\varepsilon$？

---

### 第 14 章 · Introduction to Optimization（最优化引论）⭐

> 无约束极值 / 临界点与 Hessian 判别 / 约束优化 / Lagrange 乘子 / 梯度下降法

- **核心**：无约束极值的必要条件 $\nabla f=0$（临界点），充分条件用 **Hessian** 判别（正定=极小，负定=极大，不定=鞍点，调用 Ch4 特征值）；**约束优化** $\min f$ s.t. $g=0$ 用 **Lagrange 乘子** $\nabla f=\lambda\nabla g$；**梯度下降** $x_{k+1}=x_k-\eta\nabla f$（一阶迭代法）。本章把微积分（Ch7 梯度）与线性代数（Ch4 特征值）用于最优。
- **飞腾锚点**：**分支预测** ⭐ODE 分支 —— 梯度下降/牛顿法的迭代每步依据 Hessian/梯度局部信息分支（线搜索步长、正定判别、收敛判据），条件分支命中率决定收敛效率；约束激活集(active set)的判定也是分支密集。
  - 🟢事实：凸函数（Hessian 半正定）的临界点 = 全局最小；Lagrange 乘子 $\lambda$ = 约束的「影子价格」（约束放松一点点目标改善多少）。
  - 🟡类比：梯度下降 = 「蒙眼下山，每步沿最陡方向」；Hessian 正定 = 「谷底碗状」（所有方向都向上）。
- **几何/应用**：ML 训练（SGD/Adam = 梯度下降变体）；运筹（线性/非线性规划）；经济（效用最大化、Lagrange 乘子=边际价值）；控制（LQR）。
- **关键定理**：**Lagrange 乘子定理**（$\min f$ s.t. $g=0$ 的解满足 $\nabla f=\lambda\nabla g$）；**二阶充分条件**（Hessian 正定 ⟹ 极小）。
- **自测**：用 Lagrange 乘子求 $f=x^2+y^2$ 在 $xy=1$ 下的最小值；判断 $f(x,y)=x^2-y^2$ 原点的临界点类型（鞍点）。

---

## §9 主线：线性代数 → 多元微积分 → 向量分析 → ODE → 应用

| 阶段 | 章 | 核心工具 | 统一目标 | 飞腾锚点 |
|:-:|:-:|------|---------|---------|
| 线性代数 | 1-4 | 线性空间/矩阵/行列式/特征值 | 代数引擎：一切后续主题的骨架 | Schmidt / matmul / GEMM / TLB |
| 多元微积分 | 9 | Jacobian/Fubini/换元 | $\mathbb{R}^n$ 上重积分（Jacobian 调用 Ch3） | UDOT 积分 |
| 向量分析 | 7,8,10 | 梯度/散度/旋度/三大定理 | 「内部微分 ⟺ 边界积分」 | FP16 / UDOT / TLB |
| ODE | 5,6 | Picard 存在性/矩阵指数 $e^{At}$ | ODE 系统解（特征值调用 Ch4） | 分支预测 / matmul |
| 统一与应用 | 11-14 | 外微分 $d$/概率/数值/优化 | 形式统一 + 落地应用 | Iron Law / GEMM / 分支预测 |

**三条红线**：

1. **线性代数红线**——线性空间(Ch1) → 矩阵(Ch2) → 行列式(Ch3，驱动 Ch9 换元) → 特征值(Ch4，驱动 Ch6 矩阵指数与 Ch14 Hessian 判别) → 外代数(Ch11，wedge 积是行列式的高维推广)。线性代数是贯穿全书的代数引擎，**没有 Ch1-4，Ch6/9/11/14 都无法成立**。
2. **微积分红线**——一阶 ODE(Ch5) → 多元梯度(Ch7) → 线积分(Ch8) → 重积分(Ch9) → 三大定理(Ch10) → 微分形式统一(Ch11)。从「单变量积分」升为「流形上积分」，Stokes 统一是终点。
3. **应用红线**——Ch12 概率（用 Ch9 积分算期望）→ Ch13 数值（用 Ch2-4 矩阵做 Newton）→ Ch14 优化（用 Ch7 梯度 + Ch4 特征值判 Hessian）。三章把前面的理论工具落地为可计算的工程方法。

**Apostol 卷二的设计哲学**：全书不是「线代一本 + 多元微积分一本 + ODE 一本」的拼贴，而是用**线性代数作骨架**统一一切——多元导数 = 矩阵(Jacobian)、重积分换元 = 行列式、ODE 系统解 = 矩阵指数、向量积分定理 = 外微分(wedge 是行列式推广)、Hessian 判别 = 特征值。这种「大综合」在 1969 年前卫，至今仍是培养「应用数学研究型工程师」的理想蓝本——它教会读者用同一套代数语言理解分析、ODE、应用。

**读法建议**：

- **第一遍**精读 Ch1-4（线代引擎，甜区，配 Halmos/LADR）；
- **第二遍** Ch5-6（ODE，矩阵指数是硬骨头，手算 $2\times2$）；
- **第三遍** Ch7-10（向量分析 + 三大定理，核心分析，配合 Spivak Manifolds Ch4-5）；
- **第四遍** Ch11（微分形式，全书高潮，是 Spivak Manifolds 的前置）；
- **应用章** Ch12-14 按需选读（概率/数值/优化各与对应应用领域衔接）。

**时间预算**（每周 10-20h）：

| 章 | 难度 | 预估时间 | 重点 |
|:-:|:-:|---|---|
| 1-4 | ⭐⭐ | 18-24h | 线代公理化、秩-零度、Cayley-Hamilton |
| 5-6 | ⭐⭐⭐ | 12-16h | Picard 存在性、矩阵指数 $e^{At}$ |
| 7-10 | ⭐⭐⭐ | 16-22h | Jacobian 换元、Green/Gauss/Stokes |
| 11 | ⭐⭐⭐⭐ | 8-12h | wedge 积手算、$d^2=0$、统一 Stokes |
| 12-14 | ⭐ | 8-12h | 应用章按需选读 |
| **合计** | | **60-80h** | **4-5 周** |

---

## §10 与本仓库其他笔记的交叉引用

**与 Apostol《数学分析》对比**(stage-1 已读)：数学分析是卷二的实分析升级——卷二的多元微积分(Ch7-10)在数学分析 Ch14-15 升级为 Lebesgue 多重积分；卷二的 ODE(Ch5-6)在数学分析中没有对应（数学分析不做 ODE 系统）。卷二是数学分析的「多元+线代+ODE 应用」前身。建议：卷二先读（建立多元直觉+线代骨架），数学分析再读（测度论严格化）。

**与 Spivak《Calculus on Manifolds》对比**(stage-2 已读)：卷二 Ch11（微分形式）+ Ch10（三大定理）≈ Spivak Manifolds Ch5 的「慢速版」——卷二在 $\mathbb{R}^3$ 分章讲 Green/Gauss/Stokes 再用形式统一，Spivak 在任意维流形直接给 $\int_M d\omega=\int_{\partial M}\omega$。卷二更易入门（先具体后抽象），Spivak 更锋利（一步到位）。建议：卷二 Ch11 先读（建立 wedge 直觉），Spivak Ch5 再读（任意维统一）。

**与 Thomas 多元微积分对比**(stage-1 已读)：Thomas 教「怎么算」（偏导技巧、重积分换序、线面积分参数化），卷二教「为什么」（导数为何是线性映射、换元为何要 Jacobian、Green/Gauss/Stokes 为何统一）。Thomas → 卷二 = 计算→严格。建议：Thomas 已练计算直觉，卷二补线代骨架 + 严格性。

**与 Halmos《有限维向量空间》对比**(stage-1 已读)：卷二 Ch1-4（线代）与 Halmos 范围高度重合（线性空间→变换→行列式→特征值），但卷二更偏计算（矩阵运算实例多），Halmos 更抽象（坐标无关、内积空间公理化）。建议：卷二 Ch1-4 与 Halmos 对照阅读——卷二给计算肌肉，Halmos 给抽象骨架。

**与 Courant《微积分》卷二对比**：Courant 卷二(1934)是同时代经典，物理直觉驱动（力学、变分法、电磁应用极丰富），但线代处理不如卷二系统（Courant 时代线代尚未公理化成熟）。卷二的线代部分(Ch1-5)是 Courant 所缺。建议：需物理应用背景读 Courant，需线代严格骨架读卷二。

**AI 锚点（数学 ↔ 工程）**：

- 🟢 **Jacobian = 反向传播**：卷二 Ch7 的 $\nabla f=Df^T$，神经网络反向传播 = Chain Rule 逐层连乘 Jacobian；Ch9 换元的 $|\det Dg|$ = VAE reparameterization trick 的 log-likelihood 修正。
- 🟢 **矩阵指数 = Neural ODE**：卷二 Ch6 的 $e^{At}$ 是 Neural ODE 隐藏状态演化的离散化基础；特征值实部符号 = 系统稳定性（控制论）。
- 🟢 **Cayley-Hamilton = 特征值约束**：卷二 Ch4 的 $p(A)=0$ 保证 $A$ 的任意幂可降次为低阶多项式，用于模型降阶、系统辨识。
- 🟢 **Hessian = 二阶优化**：卷二 Ch14 的 Hessian 正定判据 = 信赖域/牛顿法收敛条件；PCA = 协方差矩阵特征分解（Ch4）。
- 🟡 **梯度下降 = ODE 轨迹**：卷二 Ch14 的 $x_{k+1}=x_k-\eta\nabla f$ 是 ODE $x'(t)=-\nabla f$ 的 Euler 离散——优化与 ODE 的深层联系。
- 🟡 **$d^2=0$ = 守恒律结构**：卷二 Ch11 的 $d^2=0$（$\nabla\times\nabla f=0$）是「保守力无旋」的结构保证，Maxwell 方程组用形式写为 $dF=0$。

---

## §11 自测答案要点（供核对）

1. **Ch1** 维数：$P_n$ 基 $\{1,x,\ldots,x^n\}$ 共 $n+1$ 个 ⟹ $\dim P_n=n+1$；$\mathbb{R}^{3\times3}$ 基 $\{E_{ij}\}$ 共 9 个 ⟹ $\dim=9$。
2. **Ch2** 秩-零度：$T(x,y,z)=(x+y,y+z)$，$\ker T=\{(t,0,-t):t\in\mathbb{R}\}$（$\dim=1$），$\operatorname{im}T=\{(a,b):a,b\in\mathbb{R}\}$（$\dim=2$），$1+2=3=\dim\mathbb{R}^3$ ✓。
3. **Ch3** 行列式：两行相同则交换两行后矩阵不变，但交替性要求变号 ⟹ $\det=-\det=0$；旋转矩阵 $\det=\cos^2\theta+\sin^2\theta=1$。
4. **Ch4** 对角化：$A=\begin{pmatrix}2&1\\0&2\end{pmatrix}$ 特征值 $\lambda=2$（二重），$\ker(A-2I)=\{(t,0)\}$（$\dim=1<2$），几何重数 1 < 代数重数 2 ⟹ **不可对角化**（亏损矩阵）。
5. **Ch5** ODE：$y'+2y=e^{-t}$，积分因子 $e^{2t}$，$(ye^{2t})'=e^t$，$ye^{2t}=e^t+C$，$y=e^{-t}+Ce^{-2t}$。$y'=\sqrt y$ 在 $y=0$ 处 $\partial f/\partial y=1/(2\sqrt y)\to\infty$，非 Lipschitz ⟹ 唯一性失效（有平凡解 $y\equiv0$ 与非平凡解）。
6. **Ch6** 旋转系统：$A=\begin{pmatrix}0&1\\-1&0\end{pmatrix}$，特征值 $\pm i$，$e^{At}=\begin{pmatrix}\cos t&\sin t\\-\sin t&\cos t\end{pmatrix}$（旋转矩阵），解为圆周运动 $\mathbf{x}(t)=e^{At}\mathbf{x}_0$。
7. **Ch7** 方向导数：$\nabla f=(2xy,x^2,3z^2)$，$\nabla f(1,2,1)=(4,1,3)$，沿 $\mathbf{v}=(1,1,1)/\sqrt3$ 的方向导数 $=(4+1+3)/\sqrt3=8/\sqrt3$。
8. **Ch9** 极坐标：$\int_0^{2\pi}\int_0^1 r\,drd\theta=2\pi\cdot\frac12=\pi$；球坐标 $\int_0^{2\pi}\int_0^\pi\int_0^1\rho^2\sin\phi\,d\rho d\phi d\theta=\frac{4\pi}{3}$。$dA=r\,drd\theta$ 的 $r$ 补偿远离原点的网格拉伸（$|\det Dg|=r$）。
9. **Ch10** Green：$\oint(x\,dy-y\,dx)$，$P=-y,Q=x$，$\partial_x Q-\partial_y P=1-(-1)=2$，$\iint_D2\,dA=2\cdot\pi=2\pi$（面积公式 $A=\frac12\oint x\,dy-y\,dx$）。
10. **Ch11** 外微分：$d\omega=d(P\,dx+Q\,dy)=(\partial_x Q-\partial_y P)\,dx\wedge dy$，统一 Stokes 得 Green 定理；$d(df)=\sum_{i<j}(\partial_j\partial_i f-\partial_i\partial_j f)dx^j\wedge dx^i=0$（Clairaut 对称）。

> **核对原则**：卷二的核心是「线性代数统一一切」。Ch1-4 建立代数引擎；Ch6 ODE 用矩阵指数、Ch9 换元用行列式、Ch11 外微分用 wedge（行列式推广）、Ch14 Hessian 用特征值——每个分析/应用主题都回扣 Ch1-4。全书是一条「以线代为骨架驱动分析与 ODE」的单线逻辑链。
>
> **与测度论的关系**：卷二只讲 Riemann 积分（Ch9），不讲 Lebesgue——这是本科教材的合理选择。若需 Lebesgue 多重积分的完整理论（Fubini 的最弱条件、控制收敛），参看本仓库 Apostol《数学分析》Ch10/15 与 Royden/Folland 测度论笔记（stage-2）。

---

> **下一步**：沿 `01-track/stage-1` 精读卷二 Ch1-4（线代引擎）与 Ch7-11（多元微积分+形式），遇关键概念查 `00-META/CONCEPT-INDEX` 中「积分/导数/线性/特征值」视角；Ch11 微分形式与本仓库 Spivak Manifolds（stage-2）交叉对照，作为 stage-1→stage-2 的桥梁。
>
> **一句话总结**：Apostol 卷二的全部精华在于——**用线性代数作骨架，把多元微积分、ODE、向量分析、概率数值优化统一在一套语言下**。理解了「每个分析概念都对应一个代数对象」（导数=矩阵、换元=行列式、ODE=矩阵指数、积分定理=外微分），就理解了为什么应用数学研究型工程师必须先吃透线性代数。
>
> **实操验证**(建议用 Python/NumPy/SymPy)：
> - `numpy.linalg.eig` 验证 Ch4 对角化与 Cayley-Hamilton（验证 $p(A)=0$）
> - `scipy.linalg.expm` 计算 Ch6 矩阵指数 $e^{At}$，对比对角化 $Pe^{\Lambda t}P^{-1}$
> - `sympy.integrate` + 极坐标换元（Ch9）验证圆面积 $\pi$、球体积 $4\pi/3$
> - 实现 `exterior_derivative(omega)`（Ch11）验证 $d^2=0$（即 $\nabla\times\nabla f=0$、$\nabla\cdot\nabla\times\mathbf{F}=0$）
> - `scipy.integrate.solve_ivp`（Ch5-6）验证 ODE 数值解与矩阵指数解析解一致
