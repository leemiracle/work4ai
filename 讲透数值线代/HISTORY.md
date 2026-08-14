# 讲透数值线代 · 思想史

> **一句话定位**：所有其他章节讲"**怎么算**"——本篇问"**为什么这样算**"：为什么高斯消元统治了 150 年又被迭代法取代？为什么 SVD 被独立发现三次？为什么共轭梯度 1952 年发明却沉睡 20 年？为什么"丢掉精度"的随机化反而更准确？

> **博士级标准**：不是"年份 + 算法 + 论文"的维基百科——那是浅薄年代史。本篇是**思想史**（history of ideas）：为什么某算法在某时代诞生？为什么被遗忘又复兴？库恩范式转移如何在矩阵计算上演？你今天调用的 `np.linalg.svd` 背后是 150 年的曲折演化。

> **方法论来源**：[`讲透AI历史/00-为什么学AI历史.md`](../讲透AI历史/00-为什么学AI历史.md)（思想史 > 年代史）、[`top-math-courses/HISTORY_OF_IDEAS.md`](../top-math-courses/HISTORY_OF_IDEAS.md)（数学思想史方法）、[`top-math-courses/BREAKTHROUGHS_PART2_APPLIED_MATH.md`](../top-math-courses/BREAKTHROUGHS_PART2_APPLIED_MATH.md) §2（数值分析瓶颈突破史）

---

## 0. 方法论

### 0.1 年代史 vs 思想史

年代史告诉你"SVD 是 Golub 1965 年发明的"——这是**错的**。思想史告诉你 SVD 被 Beltrami（1873）、Jordan（1874）、Autonne（1915）独立发现，Eckart-Young（1936）证明了低秩逼近最优性，Golub-Kahan（1965）才给出了第一个**数值上可靠的算法**。理解这条链，你才能预测：下一个"SVD 级别"的工具可能已经躺在某篇被遗忘的论文里。

### 0.2 五条原则（贯穿本篇）

1. **思想史 > 年代史**——问"为什么此时"，不只"何时"
2. **路径依赖敏感**——`np.linalg.solve` 用 LU 分解而非其他，可能是 Wilkinson 一人 1948 年的选择
3. **失败与成功同等重要**——Chebyshev 半迭代法、块 Lanczos 非对称推广等"失败品"有深刻教训
4. **跨学科**——数值线代受弹道学（二战）、地震勘探、搜索引擎、量子计算的影响
5. **批判性**——当前"直接法 vs 迭代法"的分界可能是历史偶然

---

## 1. 前夜：高斯消元与经典迭代（1800–1950）

### 1.1 高斯消元：一个 2000 岁的算法

线性方程组的消元法，中国《九章算术》（约公元前 150 年）已有系统记载。西方文献中 Newton 和 Gauss 都用过类似方法。但**作为算法**的系统化，归功于 Gauss 在 1809 年 *Theoria Motus Corporum Coelestium* 中为计算小行星轨道所做的最小二乘法——他需要求解法方程 $A^TAx = A^Tb$，系统地使用了消元。

**思想史问题**：为什么消元法用了 2000 年才被"算法化"？答案：**手算时代不需要形式化**。每个计算员（human computer）有自己的技巧，直到电子计算机出现，你必须把过程写成**机器能执行的精确步骤**——这迫使"方法"变成"算法"。

### 1.2 经典迭代法的三剑客

| 方法 | 年份 | 提出者 | 核心思想 |
|------|------|--------|---------|
| Jacobi 迭代 | 1845 | Carl Jacobi | 同时更新所有分量 |
| Gauss-Seidel | 1874 | Philipp Seidel | 逐个更新，利用最新值 |
| Richardson 迭代 | 1910 | Lewis Richardson | $x_{k+1} = x_k + \omega(b - Ax_k)$ |

Jacobi 1845 年的论文处理的是天文观测中的线性方程组——他为了修正行星轨道数据，需要反复求解大型（当时算"大型"：约 40 个变量）方程组。Gauss-Seidel 迭代的命名有历史不公：Seidel（1874）独立提出，但 Gauss 的笔记中早有类似思想。

**思想史洞察**：1845–1910 这三代迭代法的共同模式是——**"迭代 = 在不动点附近反复修正"**。但它们的收敛性分析极其粗糙。Jacobi 不知道"谱半径 < 1"是收敛充要条件——那是 20 世纪线性代数成熟后才有的概念。**算法远走在理论前面**，这一模式在数值线代中反复出现。

### 1.3 为什么 1950 年前没有"数值线代"

因为**没有大规模机器计算**。1940 年代前的"数值分析"关注的是插值、数值微分、数值积分——微积分的离散化。矩阵计算只是数学的一个分支，不是独立的计算学科。

**转折信号**：1943 年，Harold Hotelling 发表了一篇可怕的短文——他证明 naive Gaussian 消元在最坏情况下误差增长因子为 $2^{n-1}$，"每多消去一行就丢掉一位精度"。这篇论文差点**杀死**高斯消元法。正是 Wilkinson 的向后误差分析（1950s 后期）才"拯救"了它——带 partial pivoting 的高斯消元在实践中是稳定的，Hotelling 的最坏情况几乎不会出现。

---

## 2. 第一次范式转移：计算机 + Householder/Lanczos（1950s）

### 2.1 电子计算机如何制造了一个新学科

**库恩范式转移的精确定义**：不是"有了更好的方法"，而是"问了完全不同的问题"。

**旧范式**（手算时代）："如何用最少的手工步骤求解一个小方程组？"——答案：聪明的消元顺序、表格法、检查和验证。

**新范式**（计算机时代）："如何让机器在有限精度下可靠地求解大规模问题？"——这暴露了三个前人从未遇到的挑战：

1. **浮点误差**：机器只有有限精度（早期机器约 10 位），误差如何传播？
2. **复杂度**：$n = 100$ 的矩阵消元需要 $10^6$ 次运算——手算不可能，但机器几分钟可以
3. **算法可实现性**：方法必须在硬件上可编程，不能依赖"直觉判断"

### 2.2 Wilkinson 与 Turing：条件数的诞生

**1946–1948 年**，James Wilkinson 在伦敦 Teddington 的国家物理实验室（NPL）的 ACE 计算机上跑 $Ax = b$。他拿看似无害的 Hilbert 矩阵试验，发现解偏离真解 $10^{10}$ 倍。几乎同时，Alan Turing 在 Manchester Mark I 上独立撞到同一堵墙。1948 年前后，两人各自给出了刻画矩阵敏感性的同一公式：$\kappa(A) = \|A\| \|A^{-1}\|$。

**Wilkinson 的真正贡献不只是定义条件数**，而是发明了**向后误差分析**（backward error analysis）——这是数值线代史上最深的方法论革命。核心思想是**视角翻转**：

- **向前误差**（传统做法）：问"算出的 $\tilde{x}$ 离真解 $x$ 多远？"——极难追踪
- **向后误差**（Wilkinson）：问"$\tilde{x}$ 是哪个邻近问题的精确解？"——即找到 $\delta A$ 使得 $(A + \delta A)\tilde{x} = b$，$|\delta A| = O(\epsilon_{\text{mach}})$

这一翻转的意义在于：**把算法的稳定性和问题的病态性彻底分开**。向后误差小 = 算法好（稳定）；条件数大 = 问题难（病态）。总误差 $\leq$ 向后误差 $\times$ 条件数。这个框架至今统治一切数值分析。

> **方法论元模式**：向后误差分析 = **元层级跃迁**（参见 [`BREAKTHROUGHS_PART2_APPLIED_MATH.md`](../top-math-courses/BREAKTHROUGHS_PART2_APPLIED_MATH.md) §2）。不改变算法，改变**分析框架**——让不可能变可能。

### 2.3 Householder 1958：反射变换

Alston Householder 在 1958 年发表 *"Unitary Triangularization of a Nonsymmetric Matrix"*，引入了**Householder 反射**：$H = I - 2vv^T / (v^Tv)$，一个将任意向量反射到 $e_1$ 方向的正交变换。

**为什么这是革命？** 此前 QR 分解用 Gram-Schmidt 正交化——经典 Gram-Schmidt 数值不稳定（误差累积），修正版稍好但仍有问题。Householder 反射天然正交（$H^TH = I$ 精确成立），数值上**几乎不损失正交性**。

**思想史洞察**：Householder 的反射是几何直觉驱动的——"反射不改变长度"。但它的威力在于**有限精度下的鲁棒性**：即使浮点运算有误差，反射后的矩阵仍然近乎正交。这是"**算法的几何结构保护了数值精度**"的典范——这个思想后来在 Krylov 方法中以不同形式反复出现。

Householder 本人是橡树岭国家实验室的数学家，他的 1964 年专著 *The Theory of Matrices in Numerical Analysis* 是数值线代的第一本系统教材。Householder 在橡树岭的工作直接服务于核反应堆模拟——曼哈顿计划的遗产之一就是催生了大规模科学计算的需求。他的书奠定了"矩阵分析"作为独立学科的基础，但风格上更偏形式化理论，直到 Trefethen-Bau 1997 才以更平易近人的方式重新定义了该领域的教学范式（详见 §6）。

值得一提的是，Householder 反射不仅用于 QR 分解——它还是 **Givens 旋转**的"姐妹方法"。Givens 旋转（Wallace Givens，1958）用平面旋转逐个消零元素，对稀疏矩阵更友好（只影响两行）。两种方法今天共存于 LAPACK 中：稠密用 Householder，稀疏/带状用 Givens。**工具选择是问题结构决定的，不是"先进性"决定的**。

### 2.4 Lanczos 1950 与 Arnoldi 1951：Krylov 子空间的诞生

Cornelius Lanczos（匈牙利裔，曾与 Einstein 在普林斯顿研究统一场论）1950 年发表 *"An Iteration Method for the Solution of the Eigenvalue Problem of Linear Differential and Integral Operators"*。他提出了一种迭代方法来逼近大型矩阵的特征值——每次迭代只做一次矩阵-向量乘法，就能在**低维 Krylov 子空间**中提取特征信息。

**Krylov 子空间**的概念：$\mathcal{K}_k(A, b) = \text{span}\{b, Ab, A^2b, \ldots, A^{k-1}b\}$。俄罗斯力学家 Aleksey Krylov 在 1931 年用幂序列 $\{b, Ab, A^2b, \ldots\}$ 做特征值计算。Lanczos 的天才在于：不是用幂序列本身，而是**在这个子空间里做正交化**——将 $n$ 维特征值问题投影到 $k$ 维子空间（$k \ll n$）。

一年后，Walter Arnoldi（1951）给出了一般（非对称）矩阵的版本——Arnoldi 过程。Lanczos 过程是对称矩阵的特例。

**思想史问题**：为什么是 1950 年？因为原子弹、氢弹的设计需要求解超大特征值问题（中子输运方程离散化后的矩阵可能 $10^5 \times 10^5$），直接法完全不可行。**核武器催生了 Krylov 方法**——这不是夸张：LANL（洛斯阿拉莫斯）和苏联的原子能研究所都是迭代法发展的温床。

---

## 3. 第二次范式转移：Krylov 子空间方法的黄金时代（1970–2000）

### 3.1 共轭梯度的奇遇：发明于 1952，沉睡到 1972

**这是数值线代史上最戏剧性的"沉睡与复兴"**。

1952 年，Magnus Hestenes 和 Eduard Stiefel 在美国国家标准局（NBS）各自独立发明了**共轭梯度法**（Conjugate Gradient, CG）。他们在同一个月内递交了论文，编辑意识到后让他们合写一篇——这就是经典论文 *"Methods of Conjugate Gradients for Solving Linear Systems"*（1952, NBS Journal of Research）。

CG 解决 $Ax = b$（$A$ 对称正定）的思想极其优美：在 $k$ 步内构造 $A$-共轭的搜索方向，理论上 $n$ 步精确收敛——它既是**迭代法**（每步逼近），又是**直接法**（$n$ 步终结）。

**但接下来 20 年，CG 几乎被遗忘了。** 原因：
1. 1950s 的矩阵太小（$n < 100$），CG 的 $n$ 步精确收敛不如 LU 分解简单
2. 人们把它当"复杂的直接法"，而非"快速的迭代法"
3. 浮点误差使得 CG 的正交性在有限精度下退化——它不像理论上那么"精确"

**复兴时刻：1970s**。石油勘探、结构工程、流体力学需要求解 $n = 10^5 \sim 10^7$ 的**稀疏**线性系统。直接法（LU/QR）需要 $O(n^3)$ 运算和 $O(n^2)$ 存储——完全不可行。人们重新发现了 CG：**对稀疏矩阵，CG 每步只需 $O(\text{nnz})$（非零元个数）运算和 $O(n)$ 存储**，而且通常在 $O(\sqrt{\kappa})$ 步（远小于 $n$）内收敛到足够精度。

> **博士级洞察**：CG 的沉睡-复兴揭示了一个深刻模式——**算法的价值取决于问题规模**。一个方法在 $n = 50$ 时"无用"，在 $n = 10^6$ 时可能"唯一可用"。今天的量子算法、亚线性算法也可能在等待它们的"规模时机"。

### 3.2 CG 家族的爆发（1975–2000）

CG 成功后，Krylov 子空间方法经历了"寒武纪大爆发"：

| 方法 | 年份 | 提出者 | 适用矩阵 |
|------|------|--------|---------|
| CG | 1952 | Hestenes-Stiefel | 对称正定 |
| MINRES | 1975 | Paige-Saunders | 对称（可能不定）|
| SYMMLQ | 1975 | Paige-Saunders | 对称（可能不定）|
| BiCG | 1976 | Fletcher | 非对称 |
| BiCGSTAB | 1992 | van der Vorst | 非对称（更稳定）|
| GMRES | 1986 | Saad-Schultz | 非对称（一般）|
| QMR | 1991 | Freund-Nachtigal | 非对称（拟最小残量）|
| TFQMR | 1993 | Freund | 非对称（无转置）|

**GMRES**（Saad-Schultz 1986）是最重要的非对称 Krylov 方法。核心思想：在扩大的 Krylov 子空间中最小化残量 $\|b - Ax_k\|_2$。理论上 GMRES 在 $n$ 步内精确收敛——但存储量随步数线性增长（需保存所有 Krylov 基向量）。实践中用 **重启 GMRES**（GMRES(m)：每 $m$ 步重启），代价是可能不收敛。

Youcef Saad（明尼苏达大学）后来在 2003 年出版了 *Iterative Methods for Sparse Linear Systems* 第二版，成为 Krylov 方法的百科全书。他的贡献不只是 GMRES——还有对预处理理论的系统化，以及特征值域与收敛性关系的深刻分析。

Henk van der Vorst 的 BiCGSTAB（1992）解决了 BiCG（双共轭梯度）的不稳定问题——它在每次迭代中混合了一个 GMRES 式的稳定化步骤，代价是需要两次矩阵-向量乘积（$A$ 和 $A^T$）。后来又出现了 BiCGSTAB(l) 和 IDR(s) 等变体，但 **GMRES(m) 仍是非对称问题的工业标准**。

**思想史洞察**：Krylov 方法的黄金时代（1975–2000）对应的是**有限元方法的爆炸**。工程中的 PDE 离散化产生了海量稀疏线性系统——桥梁设计、飞机机翼、油藏模拟、天气预报——每一个都是 $10^5 \sim 10^8$ 维的 $Ax = b$。**没有 Krylov 方法，现代工程仿真不可能**。更微妙的是：有限元矩阵的特殊结构（对称正定、稀疏、带状）恰好让 CG 大放异彩——**工具与问题的匹配创造了历史**。

### 3.3 预处理：Krylov 方法的"外挂"

CG 收敛速度依赖于 $\sqrt{\kappa(A)}$。如果 $\kappa = 10^{10}$，则需要 $10^5$ 步——太慢。**预处理**（preconditioning）的思想：找一个近似逆 $M^{-1} \approx A^{-1}$，求解 $M^{-1}Ax = M^{-1}b$，使得 $\kappa(M^{-1}A) \ll \kappa(A)$。

预处理至今仍是**半艺术半科学**——不存在通用的最优预处理。好的预处理依赖于问题的物理结构（如多重网格、区域分解、不完全 LU 分解 ILU）。这是数值线代中**最难系统化**的部分，也是博士论文最丰富的矿藏。

> **反常识**：预处理比迭代算法本身更决定性能。一个差的预处理 + 好的 Krylov 方法 = 慢。一个好的预处理 + 最简单的 Richardson 迭代 = 快。**预处理是王，算法是臣**。

---

## 4. 第三次范式转移：随机化与并行（2010+）

### 4.1 随机化数值线代：用掷骰子做数学

**范式转移**：从"精确但慢"到"大概率正确且极快"。

2011 年，Nathan Halko、Per-Gunnar Martinsson 和 Joel Tropp 发表了长文 *"Finding Structure with Randomness: Probabilistic Algorithms for Constructing Approximate Matrix Decompositions"*（SIAM Review）。这不是发明——而是**系统化了**此前散落的随机化思想（随机投影、随机采样），给出了完整的理论保证框架。

**随机化 SVD** 的核心思想极其简单：

1. 生成随机矩阵 $\Omega \in \mathbb{R}^{n \times (k+p)}$（$k$ = 目标秩，$p$ = 少量过采样）
2. $Y = A\Omega$（随机采样列空间）
3. $QR$ 分解 $Y = QR$
4. $B = Q^TA$（投影到低维）
5. 对小矩阵 $B$ 做精确 SVD

**反直觉**：这比"精确 SVD 更准确"？是的——对极大矩阵（$n = 10^6$），精确 SVD 的浮点误差积累可能超过随机算法的概率误差。**随机性成了"降噪"工具**——这是 Erdős 概率方法（参见 [`BREAKTHROUGHS_PART2_APPLIED_MATH.md`](../top-math-courses/BREAKTHROUGHS_PART2_APPLIED_MATH.md) §7）在矩阵计算中的回响。

Joel Tropp（Caltech）后来证明了一系列集中不等式，给出了随机 SVD 的**严格误差界**：以高概率，$\|A - A_k\| \leq (1 + \epsilon)\sigma_{k+1}$。这使得随机方法从"启发式"升级为"有保证的算法"。

Per-Gunnar Martinsson（当时在科罗拉多大学，后转布里斯托大学）此前在快速直接法（fast direct solvers）领域深耕多年，他的跨界视野是将随机化与经典分解结合的关键。Tropp 的随机矩阵理论背景（他证明了矩阵 Bernstein 不等式等核心工具）提供了理论保证。**三个不同背景的人的合作催生了一个新范式**——这再次印证了思想史的一个模式：**重大突破常常发生在学科交叉处**。

随机化 NLA 的先驱还包括 Petros Drineas 和 Michael Mahoney（两者都从理论计算机科学进入该领域，关注随机采样和稀疏化），以及 Tammy Kolda（张量分解中的随机化）。这个领域仍在快速演进——2020 年后的趋势是"随机 + 结构"（利用矩阵的低秩或稀疏结构来设计更好的随机采样策略）。

### 4.2 通信避免算法：Demmel 的远见

James Demmel（UC Berkeley）从 2008 年起系统推动**通信避免算法**（Communication-Avoiding Algorithms）。核心观察：在现代计算机上，**数据搬运（通信）比运算贵 $100 \sim 1000$ 倍**。传统算法优化了运算量（flop count），却产生了海量通信——这是 40 年前的度量标准留下的遗产。

Demmel 的贡献：重新设计 LU、QR、SVD，使它们在**通信最优**（communication-optimal）的意义下接近理论下界。这不是"改进常数因子"——而是**改变算法的 I/O 复杂度阶**。CA-GEMM、TSQR（Tall-Skinny QR）等算法现在已是高性能计算库的标配。

**思想史洞察**：Demmel 的工作揭示了一个被忽视的真相——**算法的"好坏"依赖于硬件架构**。在 1950 年代的串行机器上最优的算法，在 2020 年代的 GPU 集群上可能灾难性地慢。这迫使我们重新评估一切经典算法。

### 4.3 张量分解：矩阵之外的宇宙

矩阵是二维的。现实数据常常是高维的——视频（时间 × 宽 × 高 × 通道 × 批量）、量子态、推荐系统的上下文。

**张量分解**（tensor decomposition）是数值线代的高维推广，但难度急剧上升——张量秩是 NP-hard 计算的（Håstad 1990 证明），张量的"SVD"不存在唯一最优分解。

**Tensor Train（TT）格式**（Oseledets 2011）是最成功的突破之一：将 $d$ 维张量分解为 $d$ 个三维张量的链式乘积，使得存储和运算从指数级降到多项式级。这在化学、量子物理、参数化 PDE 中有广泛应用。

---

## 5. SVD 的故事：被独立发现三次的最美分解

### 5.1 三次发现

| 发现者 | 年份 | 出发点 |
|--------|------|--------|
| Eugenio Beltrami | 1873 | 双线性型的规范化 |
| Camille Jordan | 1874 | 双线性型的独立研究 |
| (Autonne) | 1915 | 复矩阵的推广 |

Beltrami 1873 年的论文 *Saggio di interpretazione della geometria non-euclidea*（关于非欧几何的解释）中，他从双线性型 $x^TAy$ 出发，用代数推导给出了 SVD。Jordan 1874 年在同一年的 *Journal de Mathématiques Pures et Appliquées* 中独立得到了相同结果——两人互不知晓。Sylvester 1889 年从特征值角度重新发现。

### 5.2 从理论到计算

SVD 的理论优美，但**如何计算它？** 这是 90 年的空窗。

- **Eckart-Young 1936**：证明截断 SVD 是最优低秩逼近（$\min_{\text{rank}(B) \leq k} \|A - B\|_F = \sqrt{\sigma_{k+1}^2 + \cdots}$）。这个定理是 PCA、压缩、降维的数学基石。Carl Eckart 是圣地亚哥加州大学的物理海洋学家——他证明这个定理是为了处理声纳信号的数据压缩。**基础数学常常在应用中诞生**。
- **Golub-Kahan 1965**：第一个**数值可靠的** SVD 算法。核心思想：先将 $A$ 双对角化（bidiagonalization），再对双对角矩阵用隐式 QR 迭代。论文标题：*"Calculating the Singular Values and Pseudo-Inverse of a Matrix"*（SIAM J. Numer. Anal.）。为什么双对角化？因为直接对 $A^TA$ 求特征值会**平方条件数**（$\kappa(A^TA) = \kappa(A)^2$），小奇异值在浮点下被噪声淹没。Golub-Kahan 的天才是绕过了 $A^TA$，直接在 $A$ 上操作。
- **Golub-Reinsch 1970**：完善了算法（加上 pivoting 和收敛加速），形成了今天 LAPACK/MKL 中 `dgesvd` 的原型。Reinsch 是 Golub 的学生，他们的 1970 论文 *"Singular Value Decomposition and Least Squares Solutions"*（Numerische Mathematik）是数值线代史上被引用最多的论文之一。

**Gene Golub**（斯坦福，1932–2007）是数值线代领域的"教父"——他不只是发明了 SVD 算法，还培养了整整一代研究者，创建了 SIAM 的矩阵计算社区。他的教科书 *Matrix Computations*（与 Charles Van Loan 合著，1983 年初版）至今是该领域的圣经。Golub 的风格是"算法优先"——先找一个能工作的算法，再回头分析理论。这与 Trefethen 的"理论优先"风格形成互补。

### 5.3 Mirsky 定理与 SVD 的唯一性

SVD 不是唯一的——当有重奇异值时，$U$ 和 $V$ 的对应列可以旋转。但**截断 SVD 给出的低秩逼近在 Frobenius 范数下是最优的**（Eckart-Young 1936），且这个最优解**在谱范数下也最优**（Mirsky 1960 推广）。Mirsky 的推广说明：无论你用哪种酉不变范数（Frobenius、谱、Schatten-p），截断 SVD 都给出同一个最优低秩逼近。**SVD 的"最优性"是普遍的，不依赖于范数选择**——这解释了为什么 PCA、LoRA、推荐系统都建立在它之上。

### 5.3 为什么 SVD 如此重要

> **博士级总结**：SVD 的地位类似于傅里叶变换之于信号处理——它是矩阵的"频谱分解"。PCA 是 SVD 的统计包装；推荐系统是 SVD 的工程包装；LoRA 是 SVD 的 ML 包装。理解 SVD 的几何意义（旋转-伸缩-旋转）和代数性质（Eckart-Young），你就理解了现代数据科学 80% 的"线性"部分。

---

## 6. 教材革命：Trefethen-Bau 1997

### 6.1 一本教材如何改变一个学科

1997 年，Lloyd Trefethen 和 David Bau 出版了 *Numerical Linear Algebra*（SIAM）。这本 361 页的书（比 Golub-Van Loan 短一半多）**重新定义了数值线代的教学方式**。

**革命性体现在三处**：

1. **"算法 = 矩阵分解"的统一哲学**。全书围绕 SVD、QR、LU、Cholesky 四大分解组织——不是罗列算法，而是展示每个算法背后都是"将矩阵分解为结构化因子的乘积"。

2. **向后误差 + 条件数的分析框架贯穿始终**。每个算法都问两个问题：① 它是 backward stable 吗？② 问题本身是 well-conditioned 吗？这让数值线代从"工程师的技巧集"变成了"有理论框架的学科"。

3. **风格革新**。短小精悍、定理-证明-评论的结构、每章有"lecture"的叙事节奏。与 Wilkinson 1965 的 *The Algebraic Eigenvalue Problem*（662 页，密不透风）或 Householder 1964 的形式化风格形成鲜明对比。

### 6.2 教材谱系

```
Wilkinson (1965) ← 古典，密不透风
  ↓
Householder (1964) ← 矩阵论视角
  ↓
Stewart (1973) ← 桥梁
  ↓
Golub-Van Loan (1983) ← 权威参考书
  ↓
Trefethen-Bau (1997) ← 教学革命 ← 今天几乎所有 NLA 课的教材
  ↓
Saad (2003) ← Krylov 专门化
Martinsson (2019) ← 随机化时代的新教材
```

Trefethen 本人（牛津/康奈尔）后来转向了逼近论和随机化算法。Bau 在 MIT 做信号处理。两人合写的这本书已经成为 SIAM 历史上最畅销的教材之一。

> **反常识**：Trefethen-Bau 之前，数值线代是"数值分析"的一个子领域——被数值积分、ODE 求解器、插值等主题稀释。Trefethen-Bau 之后，数值线代**独立成科**——今天它可能是应用数学中最实用、就业最广的方向之一。

---

## 7. 与机器学习的合流

### 7.1 百年数学驱动十年 AI

| ML 技术 | 数值线代根基 | 年代差 |
|---------|------------|--------|
| PCA | SVD（Golub 1965）/ Eckart-Young 1936 | ~70 年 |
| LoRA | 低秩逼近 = 截断 SVD | ~60 年 |
| 推荐系统 | 矩阵补全 = 带约束 SVD | ~45 年 |
| PageRank | 幂迭代法 | ~50 年 |
| 词嵌入 | 共现矩阵 SVD（Levy-Goldberg 2014 证 word2vec ≈ SVD）| ~50 年 |
| GAN 谱归一化 | 每层除以最大奇异值 | ~50 年 |
| 注意力 | softmax 矩阵积（数值稳定性 = 经典问题）| — |

### 7.2 优化器与 Krylov 的暗线

**Adam = 自适应 Krylov？** 这个类比是启发性的，但不完全精确。Adam（Kingma-Ba 2015）维护梯度的一阶矩和二阶矩——自适应地缩放每个参数的学习率。这在精神上类似**对角预处理** + **动量加速**。

更精确的类比：CG 是"在 Krylov 子空间中最优地选择搜索方向"，而 Adam 是"在坐标空间中用历史梯度信息自适应缩放"——两者的"最优"标准不同（CG 是全局最优，Adam 是启发式）。

但在**二阶优化**中，Krylov 方法有直接应用：K-FAC（Martens 2015）用 Kronecker 分解近似 Fisher 信息矩阵，Hessian-free 优化（Martens 2010）用 CG 求解 Newton 方向——这些都是 Krylov 思想在深度学习中的直系后代。

### 7.3 随机化方法的合流

随机化数值线代（Halko-Martinsson-Tropp 2011）与随机优化（SGD、随机投影）正在**合流**。随机 SVD 用于大规模 PCA，随机投影用于 Johnson-Lindenstrauss 降维，随机 sketching 用于快速最小二乘——"随机"已成为现代计算的核心范式。这呼应了 [`BREAKTHROUGHS_PART2_APPLIED_MATH.md`](../top-math-courses/BREAKTHROUGHS_PART2_APPLIED_MATH.md) §7 中 Erdős 概率方法的元模式：**用随机性证明确定性结论**。

---

## 8. 思想史反思：5 个反常识

### 8.1 SVD 被独立发现三次

Beltrami（1873）、Jordan（1874）、Sylvester（1889）各自从不同出发点（双线性型、几何、特征值）得到了同一个分解。这提示我们：**好的数学结构是不可避免的**——它会从多个方向被"发现"。今天 LoRA、PCA、推荐系统"重新发明"了 SVD 的不同面。

### 8.2 共轭梯度沉睡了 20 年

CG 1952 年发明，1970 年代才被大规模使用——不是因为"更好"了，而是**问题规模变了**。这揭示了一个预测原则：**关注那些"理论优雅但当前无用"的算法——它们在规模时机到来时会爆发**。

### 8.3 QR 算法与 QR 分解只是名字相同

QR **算法**（求特征值，迭代 $A_{k+1} = R_kQ_k$）和 QR **分解**（$A = QR$）是两个不同的东西——名字相同纯属历史巧合（Francis 1961 用 QR 分解迭代求特征值，因此叫"QR 算法"）。**同名不代表同物**——在数值线代中，名称的混淆比比皆是。

### 8.4 随机化让结果更准（而非更差）

对极大矩阵，随机 SVD 的概率误差可能**小于**确定性 SVD 的浮点误差积累。这打破了"精确 = 好，近似 = 差"的直觉。**随机性是降噪工具**——当确定性误差的累积超过随机误差的统计水平时，随机方法反而更可靠。

### 8.5 直接法没有被迭代法淘汰

直觉认为迭代法（CG/GMRES）已经取代了直接法（LU/QR）。现实：对**中等规模、稠密**矩阵（$n < 10^4$），LU/QR 仍然是最快最可靠的选择。对**超大规模、稀疏**矩阵，迭代法才占优。两者不是"新 vs 旧"，而是"不同问题规模的工具"。LAPACK（直接法库）和 PETSc（迭代法库）和平共存——**问题结构决定算法选择**，而非"先进"取代"落后"。

更深一层：2000 年后出现了**快速直接法**（fast direct solvers）——利用矩阵的**低秩结构**（off-diagonal blocks 可以低秩近似），将传统 $O(n^3)$ 的直接法加速到 $O(n \log n)$ 或 $O(n)$。代表人物包括 Leslie Greengard（FMM 方法）、Vladimir Rokhlin（基于面板的快速直接法）、以及 Martinsson。这些方法融合了"直接法的可靠性"和"迭代法的速度"——**两分法（直接 vs 迭代）正在瓦解**。

### 8.6 特征多项式是计算特征值的错误方法

教科书教你：矩阵的特征值是 $\det(A - \lambda I) = 0$ 的根。但**没有人通过计算特征多项式来求特征值**——因为展开行列式是 $O(n!)$ 或至少 $O(n^3)$ 的操作，然后求多项式根是数值不稳定的（Wilkinson 的经典反例：一个看似无害的 20 次多项式的根在浮点下完全不可靠）。

实际用的是 **QR 算法**（Francis-Kublanovskaya 1961）：反复做 $A_k = Q_kR_k$，$A_{k+1} = R_kQ_k$，矩阵收敛到上三角（Schur 形式）。加上 shift 策略后，QR 算法是 $O(n^3)$ 的且极稳定。**教科书的"定义"和实践的"算法"之间存在鸿沟**——这个鸿沟正是数值线代存在的理由。

---

## 9. 关键人物谱系

### 9.1 三大学派

| 学派 | 核心 | 代表 | 特色 |
|------|------|------|------|
| **斯坦福** | Golub → Van Loan, Heath, Trefethen（早期）| 矩阵分解、SVD | "算法优先" |
| **牛津/康奈尔** | Trefethen → Bau, Embree, Chapman | 逼近论、伪谱、教学 | "理论优先" |
| **明尼苏达** | Saad → Elman, Schultz | Krylov 方法、预处理 | "大规模优先" |

### 9.2 当代谱系

```
Turing/Wilkinson (NPL, 1940s)
  ├── Wilkinson → NAG, LAPACK 社区
  ├── Householder (Oak Ridge) → 数值线代理论化
  └── Lanczos → LANL → 特征值算法
       │
Golub (Stanford, 1960s-2007)
  ├── Van Loan → Matrix Computations 教材
  ├── Heath → 并行计算
  ├── Demmel (Berkeley) → 通信避免 + LAPACK/ScaLAPACK
  └── Gu → 扰动理论
       │
Trefethen (Oxford/Cornell)
  ├── Bau (MIT) → 信号处理
  └── Embree (Va Tech) → Krylov + 伪谱
       │
Saad (Minnesota)
  ├── GMRES (1986)
  └── 预处理理论
       │
Martinsson (Colorado/Bristol) → 随机化 + 快速直接法
Tropp (Caltech) → 随机矩阵理论 + 集中不等式
       │
Oseledets (Skoltech) → 张量分解 + TT 格式
```

### 9.3 跨学科影响

- **Wilkinson → 高性能计算（HPC）**：LAPACK/ScaLAPACK/MAGMA 的误差分析全部基于 Wilkinson 框架
- **Golub → 数据科学**：Google 的第一个推荐系统用 SVD；Netflix Prize 用矩阵补全
- **Tropp → 压缩感知**：随机矩阵理论是压缩感知（Candès-Tao 2006）的数学基础
- **Demmel → AI 硬件**：通信避免算法影响了 GPU 上的矩阵乘法内核设计

---

## 10. 失败方向

### 10.1 经典 Gram-Schmidt 的失败

经典 Gram-Schmidt 正交化在有限精度下**灾难性地不稳定**——误差在每一步累积，最终基向量几乎线性相关。Björck 1967 的修正版（Modified GS）好很多，但 Householder 反射仍然更优。经典 GS 至今只作为**反面教材**存在。

**教训**：一个"理论上正确"的算法可能是数值灾难。判断算法不能只看数学，必须看**有限精度行为**。

### 10.2 块 Lanczos 非对称推广的困难

Lanczos 过程在对称矩阵上极其优雅（三项递推）。自然的推广到非对称情况是**非对称 Lanczos**（look-ahead Lanczos）——但它在实践中极其脆弱：breakdown（除零）和 near-breakdown（几乎除零）频繁发生。这个方向耗费了大量研究精力，最终被 GMRES 等方法超越。

**教训**：对称性是一种"免费的午餐"——一旦打破，很多优雅的结构立刻崩塌。不要低估对称性。

### 10.3 Chebyshev 半迭代的边缘化

Chebyshev 半迭代法（用 Chebyshev 多项式加速 Richardson 迭代）在 1950–60 年代被广泛研究，理论上与 CG 非常接近。但它需要估计特征值范围（需要预知谱的上下界），而 CG 自适应地获取这些信息——CG 最终胜出。Chebyshev 方法今天只在特殊场景（如预处理设计）中残存。

**教训**：自适应方法通常胜过需要先验信息的方法——即使理论复杂度相同。

---

## 11. 路径依赖与偶然性

### 11.1 如果 Wilkinson 没去 NPL

Wilkinson 1946 年加入 NPL 是因为 Turing 招募他参与 ACE 计算机。如果 Wilkinson 去了剑桥做纯数学，**向后误差分析可能推迟 10–15 年**——没有它，数值线代会是一团无原则的"经验技巧"。

### 11.2 如果 Hestenes 和 Stiefel 不在同一个研究所

CG 的诞生是一个传奇巧合：Hestenes（数学家）和 Stiefel（访问学者，瑞士人）在 1951 年的 NBS 各自独立发明了同一方法。如果他们不在同一个机构，可能会各自发表——而合写论文带来的交叉验证和更完整理论可能丧失。

### 11.3 BLAS 标准化的关键作用

1979 年，Lawson-Hanson-Kincaid-Krogh 发起了 **BLAS**（Basic Linear Algebra Subprograms）标准化。这个看似"工程"的决定深远影响了整个学科：BLAS 使得算法可以硬件无关地表达，而硬件厂商只需优化 BLAS 内核。没有 BLAS，LAPACK 不可能存在，GPU 上的 cuBLAS/cuSOLVER 也不可能。**标准化创造了可移植性，可移植性创造了生态**。

### 11.4 LAPACK 作为路径依赖

LAPACK（1992）基于 BLAS 设计，成为事实标准。所有现代库（MKL、OpenBLAS、cuSOLVER、rocSOLVER）都是 LAPACK 接口的实现。这意味着 1965 年 Golub-Kahan 的 SVD 算法结构至今仍支配着每一台 GPU 的矩阵运算——**一个 60 年前的算法决定着今天 AI 训练的基础设施**。

---

## 12. 开放问题

1. **最优预处理**：预处理是"半艺术半科学"——不存在通用的最优预处理。能否系统化预处理设计？这是数值线代最深的开放问题之一。

2. **张量分解的"正确"定义**：矩阵秩有清晰的定义（非零奇异值个数），但张量秩是 NP-hard 计算的。高维数据的"低秩结构"到底是什么？CP 分解、Tucker 分解、Tensor Train 各有优劣——没有统一框架。

3. **量子线性代数**：HHL 算法（Harrow-Hassidim-Lloyd 2009）理论上在量子计算机上指数加速 $Ax = b$——但常数因子极大、输出是量子态（无法经典读取）、条件数依赖严重。量子 NLA 能否实用化？

4. **AI 辅助算法发现**：能否用 ML 自动发现更好的数值算法？Google DeepMind 的 AlphaTensor（2022）用 RL 发现了更快的矩阵乘法——这是开端还是噱头？

5. **异构架构上的最优算法**：GPU、TPU、NPU、量子混合——不同架构有不同的通信/计算比。是否存在"跨架构最优"的算法框架？

6. **混合精度算法的理论基础**：FP8/BF16/FP32/FP64 混合使用已成为训练大模型的标准——但哪些操作可以低精度、哪些必须高精度？缺乏系统理论。

---

## 13. 配套资源

### 13.1 教材（按难度递增）

| 书 | 作者 | 定位 | 年份 |
|---|------|------|------|
| *Numerical Linear Algebra* | Trefethen-Bau | 入门圣经 | 1997 |
| *Applied Numerical Linear Algebra* | Demmel | 工程视角 | 1997 |
| *Matrix Computations* 4e | Golub-Van Loan | 权威参考 | 2013 |
| *Iterative Methods for Sparse Linear Systems* 2e | Saad | Krylov 圣经 | 2003 |
| *Fast Direct Solvers for Elliptic PDEs* | Martinsson | 随机化时代 | 2019 |
| *Randomized Methods for Matrix Computations* | Martinsson-Tropp（讲义/预印）| 前沿 | 2020+ |

### 13.2 关键原始论文

| 论文 | 年份 | 意义 |
|------|------|------|
| Lanczos, "An Iteration Method..." | 1950 | Lanczos 迭代 |
| Hestenes-Stiefel, "Methods of Conjugate Gradients..." | 1952 | CG |
| Householder, "Unitary Triangularization..." | 1958 | Householder 反射 |
| Golub-Kahan, "Calculating the Singular Values..." | 1965 | SVD 算法 |
| Saad-Schultz, "GMRES..." | 1986 | GMRES |
| Halko-Martinsson-Tropp, "Finding Structure with Randomness" | 2011 | 随机化 NLA |
| Demmel et al., "Communication-Optimal Parallel Recursive..." | 2008 | 通信避免 |

### 13.3 软件

| 库 | 语言 | 定位 |
|---|------|------|
| LAPACK | Fortran/C | 直接法标准库 |
| PETSc | C | 迭代法 + 预处理 |
| SciPy `linalg` / `sparse.linalg` | Python | LAPACK 封装 |
| cuSOLVER / cuBLAS | CUDA | GPU 加速 |
| JAX `lax.linalg` | Python | 可微分线代 |
| Elemental | C++ | 分布式（已停维）|

---

## 14. 费曼回炉

### F1：一句话讲清数值线代思想史

> "数值线代从'精确计算'的幻想中醒来，先学会了测量病态（条件数），再学会了控制误差（向后稳定性），然后发现了规模的力量（Krylov），最后拥抱了随机性（随机投影）。每一步都是从'更强'到'更聪明'的范式迁移。"

### F2：卡壳点（L2 自检）

- **长期混淆**：把"QR 算法"（特征值迭代）和"QR 分解"当成一回事。重读 Francis 1961 原始论文后才理解——QR **算法**每步做一次 QR **分解**并交换因子顺序 $A_{k+1} = R_k Q_k$，因此得名。但"QR 分解"本身（$A = QR$）可以用来做最小二乘、正交化等完全无关的事。**同名不同义**。
- **长期低估**：预处理的重要性。一直以为"选对迭代法就行"，后来发现在实际工程中，**预处理的选择比迭代法的选择重要 10 倍以上**。ILU、多重网格、区域分解——这些"外挂"才是真正决定收敛速度的。
- **长期误解**：以为随机化 SVD 是"偷懒"。读到 Tropp 的集中不等式后才意识到——随机方法有**严格的概率误差界**，在极大矩阵上可能比确定性方法**更准确**（因为浮点误差累积更少）。

### F3：术语翻译

- **条件数 $\kappa(A)$** → 矩阵"对误差有多敏感"的度量。$\kappa = 1$ 完美（正交矩阵），$\kappa = 10^{13}$ 意味着你输入的第 13 位有效数字以后全是噪声。
- **向后稳定性** → 算法算出的 $\tilde{x}$ 等价于"对扰动后的 $A + \delta A$ 求精确解"——算法把误差推回给输入，而不是让输出爆炸。
- **Krylov 子空间** → 由 $\{b, Ab, A^2b, \ldots\}$ 张成的空间——"矩阵反复作用在初始向量上产生的信息流"。
- **预处理** → 找一个近似逆 $M^{-1}$ 让 $\kappa(M^{-1}A)$ 变小——相当于"把难问题翻译成等价的简单问题"。

### F4：回炉

v1 把数值线代史写成"Gauss → Jacobi → Lanczos → Golub"的线性进步。v2 加入 Kuhn 范式视角后，意识到这根本不是线性进步——而是**三次范式转移**：(1) 计算机时代暴露浮点问题（条件数/向后稳定性）→ (2) 大规模稀疏问题催生 Krylov 方法 → (3) 超大规模 + 并行催生随机化和通信避免。每次转移都伴随"旧方法在新问题上的失效"——Hotelling 1943 的高斯消元悲观论、CG 的 20 年沉睡、经典 Gram-Schmidt 的灾难。**diff 是从"英雄叙事"升级为"问题驱动演化"**。

---

### ✍️ 思考题

1. **方法论题**：选一个当前热门方向（如 LoRA / 随机投影 / 量子线性代数），用思想史视角分析——它的"前世"是什么？可能在等待什么"规模时机"？
2. **反事实题**：如果 Wilkinson 1948 年没有去 NPL，向后误差分析可能推迟多久？对 LAPACK 标准化有什么连锁影响？
3. **判断题**：随机化 NLA 会完全取代确定性 NLA 吗？基于历史规律给出你的预测。
4. **批判题**：Trefethen-Bau 1997 的"算法 = 矩阵分解"框架有无盲区？什么类型的算法无法归入此框架？
5. **延伸题**：AlphaTensor（DeepMind 2022）用 RL 发现了更快的矩阵乘法。这是数值线代的新范式，还是又一场"用更多算力优化常数"的包装？
---

📌 **下一步**

1. 回到 [`00-数值线代是什么.md`](00-数值线代是什么.md) 重读条件数/向后稳定性——现在你知道 Wilkinson 是谁了
2. 读 [`01-SVD.md`](01-SVD.md) 配本篇 §5——理解 SVD 三次发现 + Golub 算法
3. 读 [`02-06-进阶合集.md`](02-06-进阶合集.md) 配本篇 §3——理解 Krylov 黄金时代
4. 读 Trefethen-Bau 前言 + Lecture 1-5，体会教材革命的"算法 = 分解"哲学
5. 思考开放问题——尤其是 #1（最优预处理）和 #4（AI 发现算法）
