# Patrick Billingsley《概率测度的收敛》 · 快速逐章精读

> 原书：`Convergence of Probability Measures, 2nd Edition (Patrick Billingsley, Wiley, 1999)` / 读于：2026-07-03
> 定位：**弱收敛理论的「世界级原典」**，把极限定理从 $\mathbb{R}$ 推广到一般度量空间，Donsker 不变原理与经验过程两大巅峰定理的诞生地。
> 本文为**快速逐章精读**，每章 1 个飞腾锚点 + 1 个关键定理 + 1–2 道自测题。

---

## §0 引言：概率测度的收敛是什么，为什么读它

Patrick Billingsley（1925–2011）的《Convergence of Probability Measures》自 1968 年首版、1999 年推出第二版，
被公认为**弱收敛（weak convergence）理论的奠基之作**。
如果说他的另一本《Probability and Measure》是「测度论与概率论的双向桥梁」，
那么本书则是把这座桥的「概率端」向前推进到了**一般度量空间**——
不再局限于实直线上随机变量的分布收敛，
而是研究度量空间上**概率测度序列**的弱收敛。

本书的核心问题是：
给定度量空间 $(S,d)$ 上的概率测度列 $\{\mu_n\}$，何时 $\mu_n\Rightarrow\mu$（弱收敛）？
$\mu_n\Rightarrow\mu$ 的特征是什么？
函数作用后 $h(X_n)\Rightarrow h(X)$ 何时成立（连续映射）？
序列何时有弱收敛子列（Prohorov 紧性）？
随机过程列（轨道空间 $C[0,1]$ 或 $D[0,1]$）何时弱收敛到极限过程（Donsker）？
经验测度 $\hat\mu_n=\frac1n\sum\delta_{X_i}$ 何时弱收敛到真实分布（Glivenko-Cantelli / Sanov）？

全书精神浓缩为一句：
**「弱收敛 = 分布收敛的度量空间推广；Prohorov 紧性是它的 Arzelà-Ascoli。」**

**与四本同类经典的对比**（决定你该读哪本）：

| 维度 | **本书 Billingsley CPM** | **Billingsley 概率与测度** | **Varadhan 弱收敛** | **Pollard 用户指南** |
|:---|:---|:---|:---|:---|
| **定位** | 弱收敛原典（度量空间） | 测度↔概率桥梁（螺旋教学） | 弱收敛理论纵深 | 弱收敛现代讲法 |
| **空间** | 一般度量空间 $C,D$ 为主 | 实直线 $\mathbb{R}$ 为主 | 完备可分度量空间 | 可分度量空间 |
| **核心** | Portmanteau/Prohorov/Donsker | Carathéodory/DCT/CLT | 相对熵/大偏差/鞅 CLT | 测度弱收敛+经验过程 |
| **证明风格** | 经典分析、计算详尽 | 螺旋直觉、先尝后证 | 抽象凝练、几何洞见 | 简洁现代、练习导向 |
| **随机过程** | Donsker 不变原理 ⭐（顶峰） | Brown 存在 + LIL（引论） | 鞅 + 随机过程弱收敛 | 经验过程为主 |
| **大偏差** | Sanov（一章） | 无 | 全书贯穿 ⭐ | 略提 |
| **难度** | ★★★★（需测度+概率前置） | ★★★★（测度陡坡） | ★★★★★（硬核抽象） | ★★★（最佳现代入门） |
| **适合谁** | 概率极限定理/统计渐近研究者 | 测度↔概率两栖学习者 | 弱收敛/大偏差方向研究者 | 一年级研究生首选现代版 |

**读本书的正确姿势**：它是《Probability and Measure》第 4–5 部分（极限定理 + 随机过程引论）的**自然升级**——
那里 CLT 在 $\mathbb{R}$ 上成立，本书把 CLT 升级为 $C[0,1]$ 上的 Donsker 定理；
那里 Brown 运动是单一过程，本书研究「过程序列」何时收敛到 Brown。
前置：读本书前必须掌握 Billingsley《概率与测度》或等价测度论概率论基础。

---

## §1 全书 5 章骨架一览（飞腾锚点分布）

```
第1章 弱收敛(Weak Convergence)      ── Portmanteau定理/Prohorov紧性/连续映射/Skorokhod表示
                                        (弱收敛的定义与四大等价刻画,全书地基)
第2章 随机变量函数的极限定理          ── h(X_n)⇒h(X)/矩收敛/Delta方法/投影方法
                                        (从分布收敛推函数收敛,统计渐近的工具)
第3章 度量空间中的分布收敛            ── 完备可分空间/特征泛函/Prohorov定理完整版
                                        (从R推广到Polish空间,C与D的拓扑预备)
第4章 随机过程与弱收敛 ⭐⭐            ── Donsker不变原理/C空间Prohorov/Brown泛函
                                        (全书顶峰:把CLT升级为函数空间上的CLT)
第5章 经验分布函数                    ── Glivenko-Cantelli/Donsker经验过程/Sanov大偏差
                                        (统计学渐近理论的数学基础)
附录                                 ── Skorokhod拓扑/Tightness刻画/鞅中心极限定理
```

**飞腾锚点分布表**（5 章各 1 个，相邻不重复）：

| 章 | 锚点 | 数据 | 概念映射 |
|:-:|------|------|----------|
| 1 | TLB 缓存 [E04] | 4.81× | Portmanteau 四等价（开集↔闭集↔连续函数）|
| 2 | UDOT 点积 [E05] | 16.9× | 矩泛函 $h(X)=E[\varphi(X)]$ 的求和 |
| 3 | Iron Law [Lab00] | <2% | 收敛判据（误差受控）|
| 4 | GEMM NEON [Lab05] | 9.45G | Donsker 不变原理（高维正态轨道流）⭐ |
| 5 | matmul [V03] | 15× | 经验测度矩阵（$\frac1n\sum$ 加权）|

---

## 第 1 章 · Weak Convergence（弱收敛）

- **核心**：本章定义全书的核心概念——**弱收敛** $\mu_n\Rightarrow\mu$：
  对一切有界连续函数 $f\in C_b(S)$，$\int f\,d\mu_n\to\int f\,d\mu$。
  随即给出 **Portmanteau 定理**（「大口袋定理」）的**四条等价刻画**：
  (i) $\int f\,d\mu_n\to\int f\,d\mu$（$\forall f\in C_b$）；
  (ii) $\limsup\mu_n(F)\le\mu(F)$（$\forall$ 闭集 $F$）；
  (iii) $\liminf\mu_n(G)\ge\mu(G)$（$\forall$ 开集 $G$）；
  (iv) $\mu_n(A)\to\mu(A)$（$\forall$ $\mu$-连续集 $A$，即 $\mu(\partial A)=0$）。
  这四条揭示了弱收敛「连续函数」「开闭集」「边界不增」三个视角的统一。
  **连续映射定理**：若 $h$ 连续，$X_n\Rightarrow X$ 则 $h(X_n)\Rightarrow h(X)$——
  这是所有函数极限定理的总根源（第 2 章把它精细化）。
  **Skorokhod 表示定理**：若 $\mu_n\Rightarrow\mu$ 且空间可分完备，
  则存在同一空间上的 $X_n\Rightarrow X$ a.s.，使 $X_n\sim\mu_n$、$X\sim\mu$——
  把「分布收敛」翻译成「几乎必然收敛」，是强大的工具。
  **Prohorov 定理**（本章版）：若 $\{\mu_n\}$ 一致胎紧（tight），
  则存在弱收敛子列——这就是弱收敛的 **Arzelà-Ascoli**。

- **飞腾锚点**🟢：**TLB 缓存命中 4.81× 加速 [Expert_04 实测]**——
  Portmanteau 定理说弱收敛有四条等价「寻址路径」：
  连续函数、闭集、开集、连续集，
  它们从不同入口指向同一结论（弱收敛）。
  这如同 CPU 多级页表/TLB 分层寻址——
  虚拟页号、物理页号、缓存行从不同层级映射到同一数据，
  TLB 命中时加速 4.81×。
  🟢 Portmanteau 四等价为定理事实；🟡 TLB 为类比。

- **关键定理**：**Portmanteau 定理**——
  对度量空间 $(S,d)$ 上的概率测度列，以下等价：
  $$\mu_n\Rightarrow\mu \iff \forall f\in C_b(S):\int f\,d\mu_n\to\int f\,d\mu$$
  $$\iff \forall\text{闭}F:\limsup_{n}\mu_n(F)\le\mu(F)$$
  $$\iff \forall\text{开}G:\liminf_{n}\mu_n(G)\ge\mu(G)$$
  $$\iff \forall A\text{ s.t. }\mu(\partial A)=0:\mu_n(A)\to\mu(A).$$
  这四条是验证弱收敛的「瑞士军刀」。
  （Prohorov 紧性：胎紧 $\Rightarrow$ 子列弱收敛。）

- **自测**：
  1. 用 Portmanteau 第 (iv) 条证明：
     若 $X_n\Rightarrow X$，则 $P(X_n\le x)\to P(X\le x)$ 在 $P(X=x)=0$ 的 $x$ 处成立。
  2. 用 Skorokhod 表示把「$\mu_n\Rightarrow\mu$」转化为 a.s. 收敛，
     由此推出连续映射定理。

---

## 第 2 章 · Limit Theorems for Functionals of Random Variables（随机变量函数的极限定理）

- **核心**：本章把第 1 章的连续映射定理**精细化**为统计渐近可用的工具。
  核心问题：已知 $X_n\Rightarrow X$，何时 $h(X_n)\Rightarrow h(X)$？
  当 $h$ 连续时连续映射定理直接给出结论；
  但统计中大量需要 $h$ **不连续**或**仅在某点连续**的情形
  （如 $h(x)=x^2$ 在 $X=0$ 退化时，或分位数函数）。
  **矩收敛**：$\int\varphi\,d\mu_n\to\int\varphi\,d\mu$ 需要 $\{\varphi(X_n)\}$ 一致可积——
  即弱收敛本身不保证矩收敛，需额外胎紧条件。
  **Delta 方法**：若 $\sqrt n(T_n-\theta)\Rightarrow N(0,\sigma^2)$ 且 $h$ 在 $\theta$ 可微，
  则 $\sqrt n(h(T_n)-h(\theta))\Rightarrow N(0,[h'(\theta)]^2\sigma^2)$——
  这是统计中「变换后的渐近分布」标准工具。
  本章为第 4–5 章的过程极限定理铺路：
  把「实值随机变量的函数收敛」搞清楚，
  才能推广到「过程值随机元的泛函收敛」。

- **飞腾锚点**🟢：**INT8 UDOT（点积）16.9× 加速 [Expert_05 实测]**——
  矩泛函 $E[\varphi(X)]=\int\varphi\,d\mu$ 离散化为 $\sum\varphi(x_i)/n$，
  本质是大量样本值的加权求和。
  Delta 方法中渐近方差 $[h'(\theta)]^2\sigma^2$ 的估计也依赖样本矩求和。
  UDOT 硬件指令加速的正是这种大规模加权求和，
  是矩收敛/Delta 方法的工程肉身。
  🟢 矩为积分求和为事实；🟡 16.9× 为类比。

- **关键定理**：**Delta 方法**——
  若 $a_n(T_n-\theta)\Rightarrow X$（$a_n\to\infty$）且 $h$ 在 $\theta$ 可微（导数 $h'$），
  则
  $$a_n(h(T_n)-h(\theta))\Rightarrow h'(\theta)\cdot X.$$
  特别地 $a_n=\sqrt n$、$X\sim N(0,\sigma^2)$ 给出统计渐近正态的变换律。
  （矩收敛：$X_n\Rightarrow X$ + $\{X_n^r\}$ 一致可积 $\Rightarrow E[X_n^r]\to E[X^r]$。）

- **自测**：
  1. 设 $\sqrt n(\bar X_n-\mu)\Rightarrow N(0,\sigma^2)$，
     用 Delta 方法求 $\sqrt n(\bar X_n^2-\mu^2)$ 的渐近分布。
  2. 举一个 $X_n\Rightarrow X$ 但 $E[X_n]\not\to E[X]$ 的例子，
     说明一致可积条件不可省。

---

## 第 3 章 · Convergence in Distribution in Metric Spaces（度量空间中的分布收敛）

- **核心**：本章把弱收敛从 $\mathbb{R}$ 彻底推广到**完备可分度量空间**（Polish 空间）。
  首先讨论**特征泛函**（$S$ 上有界连续函数的积分）
  作为弱收敛的判据——
  在 $\mathbb{R}$ 上特征函数唯一决定分布，
  在一般空间上需要找到足够「丰富」的函数类。
  **Prohorov 定理完整版**：在 Polish 空间上，
  胎紧 $\iff$ 相对序列紧（每个序列有弱收敛子列）——
  这是验证弱收敛存在性的核心工具，
  地位相当于实分析中的 Arzelà-Ascoli 定理。
  本章还讨论**乘积空间**上的弱收敛
  （联合分布 $\Rightarrow$ 各分量弱收敛 + 联合决定），
  为第 4 章的过程收敛（轨道是「无穷维」随机元）做拓扑预备。
  特别地，本章明确 $C[0,1]$（连续函数空间，一致范数）
  与 $D[0,1]$（右连左极函数空间，Skorokhod 拓扑）的结构——
  这两个空间是随机过程的「舞台」。

- **飞腾锚点**🟢：**Iron Law（铁律）误差 <2% [Lab00 实测]**——
  Prohorov 定理的胎紧条件要求：
  对每个 $\epsilon>0$ 存在紧集 $K$ 使 $\sup_n\mu_n(K^c)<\epsilon$——
  即「质量不能逃逸到无穷远」，误差被紧集钉住。
  飞腾实验纪律「跑多次取中位数、误差 <2%」正是胎紧的工程兑现：
  只要质量集中在紧集（可控范围）内，弱收敛子列就存在。
  🟢 胎紧条件为定理；🟡 <2% 为类比阈值。

- **关键定理**：**Prohorov 定理**（Polish 空间完整版）——
  设 $(S,d)$ 完备可分，$\{\mu_n\}$ 为其上概率测度列。则
  $$\{\mu_n\}\text{ 胎紧}\iff\{\mu_n\}\text{ 相对序列紧}$$
  （胎紧：$\forall\epsilon>0,\exists\text{紧}K:\sup_n\mu_n(K^c)<\epsilon$）。
  这是证明 Donsker 定理（第 4 章）时「先证胎紧、再识别有限维分布」策略的基石。

- **自测**：
  1. 在 $\mathbb{R}$ 上，证明 $\{\delta_n\}$（点集中于 $n$）不是胎紧的，
     因而没有弱收敛子列。
  2. 说明为何 Prohorov 定理需要「完备可分」（提示：考虑非完备空间上的反例）。

---

## 第 4 章 · Stochastic Processes and Weak Convergence（随机过程与弱收敛）⭐⭐ 全书顶峰

- **核心**：本章是全书的**最高峰**——
  把经典 CLT 从 $\mathbb{R}$ 升级为**函数空间上的 CLT**，即 **Donsker 不变原理**。
  设 $X_i$ i.i.d.，$E[X_i]=0$，$\text{Var}=\sigma^2$，
  定义**部分和过程**
  $$S_n(t)=\frac{1}{\sigma\sqrt n}\sum_{i=1}^{\lfloor nt\rfloor}X_i,\quad t\in[0,1]$$
  （线性插值使其连续）。
  **Donsker 定理**：$S_n\Rightarrow W$（在 $C[0,1]$ 上弱收敛到标准 Brown 运动）。
  证明分两步（这是弱收敛证明的标准范式）：
  (1) **胎紧性**：用 Prohorov 定理 + 随机过程的模连续性界，证 $\{S_n\}$ 在 $C[0,1]$ 胎紧；
  (2) **识别有限维分布**：证任一有限维 $(S_n(t_1),\dots,S_n(t_k))$ 的联合分布弱收敛到 $(W(t_1),\dots,W(t_k))$——
  这一步本质是经典的多维 CLT。
  两步合一即得 Donsker。
  本章还讨论 **Brown 泛函的极限定理**：
  由连续映射定理，$\sup_t S_n(t)\Rightarrow\sup_t W(t)$，
  而 $\sup_t W(t)$ 的分布已知（反射原理给出 $\sup W\doteq|W(1)|$）——
  这就**一次证明了 Kolmogorov-Smirnov 统计量、反正弦律等一系列经典结论**。
  不变原理的威力：一个 Donsker 定理 = 无数个具体极限定理。

- **飞腾锚点**🟡：**GEMM NEON FP32：9.45 GFLOPS [Lab05 实测]**——
  Donsker 的部分和过程 $S_n(t)$ 是「随时间累积的独立增量」，
  极限 Brown 运动的增量 $W(t)-W(s)\sim N(0,t-s)$ 是连续正态分布沿时间的「流动」。
  高维正态流（每条轨道是 $\mathbb{R}^{[0,1]}$ 中的一个点）
  与 GEMM 处理的高维矩阵运算同构——
  每个时间点的部分和都是一次矩阵-向量乘积。
  不变原理保证了「换一组 i.i.d.（只要均值方差同），极限还是 Brown」——
  这正是硬件 benchmark「换数据不变结论」的数学根基。
  🟢 Donsker 为定理；🟡 GEMM 数为类比。

- **关键定理**：**Donsker 不变原理**——
  若 $X_i$ i.i.d.，$E[X_i]=0$，$\text{Var}(X_i)=\sigma^2$，
  则部分和过程 $S_n(t)=\frac{1}{\sigma\sqrt n}\sum_{i=1}^{\lfloor nt\rfloor}X_i$
  在 $C[0,1]$（一致范数）上弱收敛到标准 Brown 运动 $W$：
  $$S_n\Rightarrow W.$$
  证明 = 胎紧性（Prohorov）+ 有限维分布识别（多维 CLT）。
  推论（连续映射）：$\sup_t S_n(t)\Rightarrow\sup_t W(t)\doteq|N(0,1)|$。

- **自测**：
  1. 用 Donsker 定理 + 连续映射定理证明：
     $\frac{1}{\sigma\sqrt n}\max_{k\le n}\sum_{i=1}^k X_i\Rightarrow\sup_{0\le t\le1}W(t)$，
     并用反射原理给出右边的精确分布。
  2. 说明「胎紧性」证明中为何需要 $X_i$ 的二阶矩存在（联系 Chebyshev/模连续性）。

---

## 第 5 章 · Empirical Distribution Functions（经验分布函数）

- **核心**：本章把弱收敛理论应用于**统计学最基础的对象——经验分布**。
  设 $X_i$ i.i.d. $\sim F$，**经验分布函数**
  $$F_n(x)=\frac{1}{n}\sum_{i=1}^n\mathbf{1}_{\{X_i\le x\}}.$$
  **Glivenko-Cantelli 定理**（强大数律的「一致版」）：
  $\sup_x|F_n(x)-F(x)|\xrightarrow{a.s.}0$——
  经验分布几乎必然一致收敛到真实分布，
  这是统计推断「用样本估分布」的数学合法性根基。
  **Donsker 经验过程定理**（Donsker 的第二形式）：
  经验过程 $\sqrt n(F_n-F)\Rightarrow G_F$（$C$ 或 $D$ 上的 Brown 桥），
  其中 $G_F$ 是均值为 0、协方差 $\text{Cov}(G_F(s),G_F(t))=F(\min(s,t))-F(s)F(t)$ 的高斯过程。
  由此推出 **Kolmogorov-Smirnov 统计量**
  $\sqrt n\sup_x|F_n(x)-F(x)|\Rightarrow\sup_t|G_F(t)|$
  的极限分布（与 $F$ 无关，分布无关/分布自由）——
  这是非参数检验的数学核心。
  本章还讨论 **Sanov 大偏差定理**：
  经验测度 $\hat\mu_n$ 偏离真实分布 $\mu$ 的大偏差速率由**相对熵**（KL 散度）刻画
  $P(\hat\mu_n\approx\nu)\asymp e^{-nD(\nu\|\mu)}$——
  这是大偏差理论与信息论接轨的入口。

- **飞腾锚点**🟢：**matmul 15× 加速 [Vector_03 实测]**——
  经验分布 $F_n(x)=\frac1n\sum\mathbf{1}_{X_i\le x}$ 本质是「指示向量的加权平均」，
  可写成矩阵-向量乘积形式（指示矩阵 $\times$ 权重向量）。
  matmul 加速的正是这种批量加权求和。
  Glivenko-Cantelli 的「一致收敛」保证：样本够多时，经验分布矩阵的每一行都接近真实——
  这是机器学习中「经验风险趋近期望风险」（ERM 可学习性）的数学原形。
  🟢 Glivenko-Cantelli 为定理；🟡 matmul 为类比。

- **关键定理**：**Glivenko-Cantelli + Donsker 经验过程**——
  (i) $\sup_x|F_n(x)-F(x)|\xrightarrow{a.s.}0$（一致强收敛）。
  (ii) $\sqrt n(F_n-F)\Rightarrow G_F$（Brown 桥，弱收敛到高斯过程）。
  推论：$\sqrt n\sup_x|F_n(x)-F(x)|\Rightarrow\sup_{0\le t\le1}|B(t)|$
  （$B$ 为 Brown 桥），极限分布与 $F$ 无关（K-S 检验）。
  （Sanov：$P(\hat\mu_n\approx\nu)\asymp e^{-nD(\nu\|\mu)}$。）

- **自测**：
  1. 用 Donsker 经验过程定理说明：
     为何 K-S 统计量的极限分布与真实分布 $F$ 无关（「分布自由」）？
  2. 对离散分布（如 Bernoulli），$F_n$ 在跳跃点处的行为如何？
     说明 Skorokhod 拓扑（$D$ 空间）比一致拓扑更合适。

---

## §9 全书思想主线（约 200 字）

Billingsley 全书的思想主线是
**「把分布收敛从实直线推广到度量空间」**，贯穿三条递进的主线：

1. **弱收敛的刻画与紧性**（地基）：
   Portmanteau 定理给出弱收敛的四条等价路径，
   Prohorov 定理给出「胎紧 $\iff$ 相对紧」——
   它们是弱收敛的 Arzelà-Ascoli。
   第 1、3 章把这套工具在 $\mathbb{R}$ 与一般 Polish 空间上建好。

2. **函数与泛函的极限定理**（工具）：
   连续映射定理（第 1 章）+ Delta 方法（第 2 章）
   把「分布收敛」传递给「函数收敛」，
   是统计渐近理论的标准工具链。

3. **过程与经验的极限定理**（巅峰）：
   Donsker 不变原理（第 4 章）把 CLT 升级为函数空间 CLT，
   一个定理一次证明无数结论；
   Glivenko-Cantelli 与经验过程（第 5 章）给出统计学的数学根基。
   Sanov 大偏差打开信息论通道。

**一句话**：Billingsley 教你看清——
**弱收敛是分布收敛的几何化，Prohorov 紧性是它的 Arzelà-Ascoli，Donsker 是它的 CLT 之王。**

---

## §10 与本仓库其他笔记的交叉引用

**与已读书的衔接**：

| 书 | 关系 | 衔接点 |
|:---|:---|:---|
| **Billingsley 概率与测度**（已读） | 前置↔升级 | 概率与测度第 4 部分 CLT（$\mathbb{R}$ 上）→ 本书第 4 章 Donsker（$C[0,1]$ 上）；第 5 部分 Brown 存在 → 本书研究过程序列的收敛。两书是 Billingsley 的「姊妹篇」 |
| **Shiryaev GTM95**（已读） | $\mathbb{R}$↔度量空间 | Shiryaev 在 $\mathbb{R}$ 上严格证 CLT/特征函数；本书把同一套极限定理搬到 Polish 空间。Shiryaev 是本书的实直线前置 |
| **Durrett 概率论**（已读） | 入门↔原典 | Durrett 用现代简洁语言讲弱收敛与 Donsker；本书是 Durrett 第 7–8 章的「原典纵深」 |
| **Williams 概率与鞅**（已读） | 鞅↔弱收敛 | Williams 的鞅收敛定理 ↔ 本书附录的鞅 CLT；两者在「极限行为」上互补 |

**与未读书的衔接**：

| 书 | 关系 | 衔接点 |
|:---|:---|:---|
| **Varadhan《弱收敛》**（同期生成） | 经典↔抽象 | Varadhan 更抽象（大偏差/相对熵贯穿）；本书更经典计算化。两者是弱收敛的「双塔」 |
| **Pollard《弱收敛用户指南》**（同期生成） | 原典↔现代 | Pollard 是本书的现代简化版；本书是 Pollard 的历史原典。先 Pollard 入门再回本书 |
| **van der Vaart《渐近统计》** | 理论↔应用 | 本书第 4–5 章的 Donsker / 经验过程 = van der Vaart 渐近统计的数学基础 |

**AI/工程锚点法**（每个抽象找工程落地，防研究级数学悬空）：

| 概念 | AI/工程映射 | 飞腾锚点 |
|:---|:---|:---|
| **弱收敛 = 分布收敛** | GAN/扩散模型的「生成分布收敛到真实分布」本质是测度弱收敛；Wasserstein 距离是弱收敛的度量 | TLB 4.81×[E04]：Portmanteau 四等价（第 1 章）|
| **Donsker = 函数 CLT** | 随机梯度下降的「训练轨迹」在步长→0 时弱收敛到 SDE（随机微分方程）；这是 SGD 分析的数学根基 | GEMM 9.45G[Lab05]：高维正态轨道流 ⭐ |
| **Glivenko-Cantelli = ERM** | 机器学习可学习性的根基：经验风险 $\frac1n\sum\ell\xrightarrow{a.s.}$ 期望风险，一致收敛保证泛化 | matmul 15×[V03]：经验测度加权矩阵 ⭐ |
| **K-S 检验 = 分布自由** | A/B 测试、两样本检验中 K-S 统计量不依赖分布形式；非参数方法的核心 | UDOT 16.9×[E05]：指示函数求和（第 5 章）|
| **Sanov = 大偏差 = 信息论** | 大偏差速率 = KL 散度；与信息论、PAC-Bayes 泛化界、变分推断同源 | （第 5 章 Sanov 定理）|
| **Prohorov 紧性 = Arzelà-Ascoli** | 优化中「紧集上连续函数取到极值」；神经网络参数空间的紧性保证可优化性 | Iron Law[Lab00]：胎紧↔误差 <2% |

---

> **下一步**：① 亲笔推导 Donsker 不变原理的两步证明（胎紧 + 有限维识别，第 4 章核心）；
> ② 用连续映射定理从 Donsker 推出 K-S 统计量的极限分布（第 5 章核心）；
> ③ 衔接 Varadhan/Pollard 从本书进入大偏差与现代经验过程理论（阶段 3 研究方向纵深）。
