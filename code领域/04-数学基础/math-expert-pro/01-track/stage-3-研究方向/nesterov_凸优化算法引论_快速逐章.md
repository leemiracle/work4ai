# Yurii Nesterov《凸优化算法引论：基础课程》 · 快速逐章精读

> **原书**：*Introductory Lectures on Convex Optimization: A Basic Course*,
> Yurii Nesterov, Springer (Kluwer), **Applied Optimization 87**, 2004（2018 更新版加入相对光滑等新进展）
> **读于**：2026-07-03
> **定位**：以「黑箱 oracle + 信息复杂性」为脊柱，把加速梯度与内点法统一在「下界 → 最优算法」框架下的现代优化理论顶峰。
> **特色**：Nesterov 用一阶 oracle 模型 + 复杂性下界定理，证明 NAG 的 $O(1/k^2)$ 率「不可能更快」，让加速从工程 trick 升格为数学定理。
> **声明**：本文为**快速逐章精读**（非逐页详读），套用八重视角骨架的精简版——
> 每章只抓核心逻辑链、一个飞腾锚点、一两条关键定理、一道可做的自测题。
> 附录 A（Preliminaries，凸分析预备）并入 §0 引言带过，不单列章节。
> **章节命名**：忠于原书真实 TOC（Ch1 引言方法论 / Ch2 光滑凸优化 / Ch3 非光滑凸优化 /
> Ch4 最优方法与复杂性理论 / Ch5 多项式时间内点法），与原书结构一致。
>
> 三源 = Nesterov 原书（复杂度最优性） × 已读 bertsekas_凸优化理论 / D-凸优化(Boyd) / nocedal_wright
> × 飞腾 D3000M（硬件锚点）

---

## §0 引言：Nesterov 的复杂度最优性视角（约 350 字）

Yurii Nesterov（CORE, UCLouvain，2023 von Neumann 理论奖得主）这部书与市面所有凸优化教材最大的不同在于：
它**不把算法当配方，而把算法当复杂度最优的数学对象**。
全书五章可以读作「为证明加速梯度法已到极限所做的层层铺垫」——

- **Ch1** 建立 **black-box oracle** 模型（算法只能问函数值/梯度，看不到内部结构），定义什么是「迭代复杂性」，
- **Ch2** 证明光滑凸优化下梯度法 $O(1/k)$，再用势函数技巧造出 **Nesterov 加速梯度（NAG）** 达 $O(1/k^2)$，
- **Ch3** 退到非光滑，次梯度法只有 $O(1/\sqrt{k})$，并给出「光滑化」技巧把非光滑伪装成光滑来加速，
- **Ch4** 给出**下界定理**：任何一阶方法在 $L$-光滑问题上做不到比 $\Omega(1/k^2)$ 更好——所以 NAG 已是最优，
- **Ch5** 换轨道到 **Self-Concordant 内点法**，证明它能 $O(\sqrt{\nu}\log(1/\epsilon))$ 步收敛——多项式时间。

这条「下界 → 最优算法」主线，让读者从一开始就建立
「收敛率不是经验，是信息论极限」的世界观。
附录 A（凸集/凸函数/次微分预备）按需查阅即可。
对用户（Python 工程级 + 做深度学习、每天用 Adam/SGD-momentum）而言，
本书是最该读的优化理论教材——
读完你会明白 PyTorch 里 `momentum=0.9` 和 NAdam 背后的 $O(1/k^2)$ 极限从何而来。

**同类教材 4 列对比**：

| 书 | 风格 | 严格性 | 适合谁 |
|---|---|---|---|
| **Nesterov**《Introductory Lectures on Convex Optimization》(2004) | 复杂度/信息论驱动，黑箱 oracle，收敛率与下界为主线 | 高（含最优性证明） | 想懂一阶方法为何「已到极限」、做加速/收敛率研究的人 |
| **Boyd & Vandenberghe**《Convex Optimization》(2004) | 应用驱动，例题海量，凸性识别为纲 | 中高（略省证明细节） | 需要把实际问题建模成凸优化的实践者 |
| **Bertsekas**《Convex Optimization Theory》(2009) | 几何驱动，对偶为中心，分离/KKT/鞍点 | 高（定理证明完整） | 想从几何直觉走到严格对偶的读者 |
| **Nocedal & Wright**《Numerical Optimization》(2006) | 数值实现驱动，算法实现与调参细节 | 中高（偏工程实现） | 要落地实现求解器、做大规模数值优化的人 |

---

## §1 全书 5 章骨架一览（飞腾锚点分布）

| 章 | 标题 | 核心概念 | 飞腾锚点 |
|:-:|------|---------|---------|
| 1 | Introduction: Methodological Issues | black-box oracle、一阶/零阶信息、迭代复杂性模型 | Iron Law <2% |
| 2 | Smooth Convex Optimization | $C^1_L$ 光滑、梯度法 $O(1/k)$、**NAG** $O(1/k^2)$、势函数 | FP16 3.81× |
| 3 | Nonsmooth Convex Optimization | 次梯度 $O(1/\sqrt{k})$、smoothing、极小极大 | UDOT 16.9× |
| 4 | Optimal Methods & Complexity Theory | 信息复杂性、**下界定理**、Chebyshev/Krylov | matmul 15× |
| 5 | Polynomial-Time Methods (Interior-Point) | **Self-Concordant**、路径跟踪、对偶界、$\nu$-barrier | GEMM 9.45 GFLOPS |

> **读法建议**：Ch1 建模型可速读但别跳（oracle 概念贯穿全书）；**Ch2 必精读**（NAG 与势函数证明是本书灵魂）；
> Ch3 的 smoothing 技巧是「用光滑换速度」的工程启示；**Ch4 下界定理**是研究级核心，决定你能否写论文；
> Ch5 与 nocedal_wright 第 16 章（约束优化内点法）互补着读——Nesterov 给严格 self-concordance 理论，N&W 给数值实现。

---

### 第 1 章 · Introduction: Methodological Issues（引言：方法论）

#### 核心（概念逻辑串联）

Nesterov 开篇即立「**方法论**」：一个迭代法的好坏，只有在**统一的复杂度模型**下比较才有意义。
他引入 **black-box（oracle）模型**——算法对目标函数 $f$ 的全部知识，
来自一个 oracle，每次调用返回 $f(x)$（零阶）或 $(f(x),\nabla f(x))$（一阶）。
算法在「函数族 + oracle 类型 + 维度 + 距离度量」的框架下被评判，
收敛率 $k$ 步后的最坏误差即为「**迭代复杂性**」。

这套模型把「这个算法好不好」从「跑得快不快」（机器、实现）剥离，
变成「在给定信息量下，理论上能到多准」——
后者只依赖数学，是**算法本质**的度量。
本章还预告全书的核心论点：对每一类问题，
存在一个**最优方法**，其收敛率匹配复杂性下界，任何方法都超越不了。

#### 飞腾锚点

🟢 **Iron Law <2% [Lab00] → 收敛率/停机准则**。
「性能 = 指令数 × CPI × 时钟」的铁律说：算法总成本由「调用次数」与「每次成本」决定。
Nesterov 的迭代复杂性正是「步数 $k$ × 单步 oracle 成本」的抽象版——
停机准则 $\|\nabla f\|\le\epsilon$ 转译成「需要 $k=O(\sqrt{L/\epsilon})$ 步」（光滑），
每步的 CPI 由 oracle 的函数值/梯度计算决定。
加速就是把「步数」那一项开平方，与硬件「减少 CPI」是互补的两条优化轴。

#### 关键定理

- **Black-box oracle 模型**：算法第 $k$ 步的查询点 $x_k$ 只能依赖前 $k-1$ 次 oracle 返回值，
  即 $x_k \in x_0 + \mathrm{span}\{g_0,\dots,g_{k-1}\}$（一阶情形，$g_i=\nabla f(x_i)$）。
- **复杂性目标**：对函数族 $\mathcal{F}$，定义 $\mathrm{Compl}(\mathcal{F},k)
  =\inf_{\text{方法}}\sup_{f\in\mathcal{F}}[f(x_k)-f^*]$，求其随 $k$ 的渐近阶。
- **最优方法**：若某方法对 $\mathcal{F}$ 达到 $\mathrm{Compl}$ 的阶，称其「最优」——本书任务即构造之。

#### 自测

举一个实际优化问题（如深度学习训练 $\min\ \frac1n\sum_i\ell(f_\theta(x_i),y_i)$），
指出它的 oracle 是零阶还是一阶？一次 oracle 调用的「成本」由什么决定？
把停机 $\epsilon=10^{-3}$ 代入 $O(1/k^2)$，估计至少需多少步？

---

### 第 2 章 · Smooth Convex Optimization（光滑凸优化）⭐ 全书高潮之一

#### 核心

$f$ 称 $L$-光滑（$f\in C^1_L$），若梯度 Lipschitz：
$$|f(y)-f(x)-\langle\nabla f(x),y-x\rangle|\le\tfrac{L}{2}\|y-x\|^2,\ \forall x,y.$$
普通梯度下降 $x_{k+1}=x_k-\tfrac1L\nabla f(x_k)$ 利用此不等式得 $O(1/k)$ 收敛。
但 Nesterov 问：能否更快？答案是 **Nesterov 加速梯度（NAG, 1983）**——
在梯度步前注入一个「动量方向」：
$$x_{k+1}=y_k-\tfrac1L\nabla f(y_k),\qquad
y_{k+1}=x_{k+1}+\tfrac{\alpha_k-1}{\alpha_{k+1}}(x_{k+1}-x_k),$$
其中 $\alpha_0=1,\ \alpha_{k+1}=\tfrac{1+\sqrt{1+4\alpha_k^2}}{2}$。
收敛率从 $O(1/k)$ 跃升到 $\mathbf{O(1/k^2)}$——「免费」的加速。
证明核心是 Nesterov 独创的**估计序列 / 势函数**技巧，
构造一对 $(\phi_k,x_k)$ 使 $\phi_k$ 始终上界 $f(x_k)$ 且 $\phi_k$ 以 $O(1/k^2)$ 收敛。

#### 飞腾锚点

🟡 **FP16 3.81× [L01] → 梯度数值精度 / loss scale trick**。
深度学习训练中梯度 $\nabla f$ 动辄 $10^{-3}\sim10^{-6}$ 量级，
FP16 的最小正规数约 $6\times10^{-5}$，梯度常**下溢归零**——
NAG 的动量累积 $y_{k+1}=x_{k+1}+\beta(x_{k+1}-x_k)$ 一旦梯度为零，加速失效。
解法是 **loss scaling**：前向损失乘 $S=2^{16}$，梯度反传后再除回——
等价于在 FP16 的 3.81× 吞吐下保住梯度精度。
这正是「数学上的 $O(1/k^2)$」必须配「硬件上的数值补救」才落得地的真实案例。

#### 关键定理

- **光滑性下降引理**：$f\in C^1_L$ $\Rightarrow$
  $f\big(x-\tfrac1L\nabla f(x)\big)\le f(x)-\tfrac{1}{2L}\|\nabla f(x)\|^2$。
- **NAG 收敛率**：$f\in C^1_L$ 凸，NAG 迭代满足
  $$f(x_k)-f^* \;\le\; \frac{4L\,\|x_0-x^*\|^2}{(k+2)^2} \;=\; O\!\left(\frac{L}{k^2}\right).$$
- **强凸加速**：若 $f$ 还是 $\mu$-强凸，NAG 收敛率 $O\big((1-\sqrt{\mu/L})^k\big)$（线性收敛）。

#### 自测

取 $f(x)=\tfrac12\|Ax-b\|^2$，$A\in\mathbb{R}^{m\times n}$。
(1) 证明 $f$ 是 $L$-光滑并求 $L=\lambda_{\max}(A^TA)$。
(2) 写出 NAG 迭代的两步公式，对比普通梯度下降（提示：$x_{k+1}-x_k$ 即动量项）。

---

### 第 3 章 · Nonsmooth Convex Optimization（非光滑凸优化）

#### 核心

当 $f$ 不可微（如 $f(x)=\|x\|_1$、$\max_i x_i$、ReLU），梯度不存在，只能用**次梯度** $g\in\partial f(x)$。
次梯度法 $x_{k+1}=x_k-\alpha_k g_k$ 用递减步长 $\alpha_k\to0,\ \sum\alpha_k=\infty$ 收敛，
但速率骤降至 $O(1/\sqrt{k})$——比光滑慢一个 $k$ 的量级。
Nesterov 的关键洞察：**非光滑的慢是本质的**（Ch4 下界定理将证明 $1/\sqrt{k}$ 不可破），
但若函数有**可利用的结构**（如 $f(x)=\max_{u\in Q}\langle Ax,u\rangle$ 是内层 max），
可用 **smoothing 技巧**——把 max 换成光滑的 entropy-regularized 版本，
$g_\mu(x)=\mu\log\sum_i e^{\langle a_i,x\rangle/\mu}$，
光滑度 $L_\mu=O(\|A\|^2/\mu)$，加速后达 $O(1/k)$，且 $\mu$ 可随 $k$ 调到最优。
这把「不可微」变成「可微化的伪装」，是 SVM、博弈论、鲁棒优化的实用加速套路。

#### 飞腾锚点

🟡 **UDOT 16.9× [E05] → 次梯度/Gram 求和吞吐**。
次梯度法对复合目标 $f(x)=\sum_{i=1}^m f_i(x)$（如 $\ell_1$、SVM hinge 损失）的每次迭代，
核心是批量内积 $\langle g_i,x\rangle$ 与分量求和 $\sum g_i$。
点积指令（DOT）加速器比标量循环快约 16.9×——
这正是 mini-batch SGD、次梯度下降在 GPU 上「向量化即提速」的硬件根因。
但次梯度方向噪声大，UDOT 的快速求和反而放大方向方差，
需配随机化（SGD）或束方法稳方向——硬件「快」与算法「稳」的张力。

#### 关键定理

- **次梯度收敛率**：$f$ 凸、$G$-Lipschitz（$\|g\|\le G$），$R=\|x_0-x^*\|$，取步长 $\alpha_k=\frac{R}{G\sqrt{k}}$，
  则平均迭代 $\bar x_k=\tfrac1k\sum_{i<k}x_i$ 满足
  $$f(\bar x_k)-f^* \;\le\; \frac{GR}{\sqrt{k}} \;=\; O\!\left(\frac{1}{\sqrt{k}}\right).$$
- **极小极大 / 鞍点情形**：$f(x)=\max_{u\in Q}\phi(x,u)$，对 $u$-space 加 entropy 正则得光滑 $\tilde f_\mu$，
  $L_\mu\le\|A\|^2/\mu$；NAG 在 $\tilde f_\mu$ 上达 $O(\|A\|R/k)$，调 $\mu\sim\|A\|/k$ 最优。

#### 自测

取 $f(x)=\|x\|_1$，$x\in\mathbb{R}^n$，$x_0=0$，$x^*=0$。
(1) 求 $x_0$ 处的次微分 $\partial f(0)$。
(2) 取 $g=(1,\dots,1)\in\partial f(0)$、步长 $\alpha_1=1/\sqrt{1}$，写出 $x_1$，观察次梯度法的「方向偏」。

---

### 第 4 章 · Optimal Methods and Complexity Theory（最优方法与复杂性理论）⭐ 研究级核心

#### 核心

本章是全书的理论制高点：**证明 Ch2/Ch3 的收敛率已是信息论极限**，无法超越。
Nesterov 沿用 Nemirovsky-Yudin（1983）的思路，构造一个「**最坏函数**」——
一条使任何一阶方法都只能爬到 $O(1/k^2)$（光滑）或 $O(1/\sqrt{k})$（非光滑）的硬实例。
对光滑情形，最坏函数取二次型 $f(x)=\tfrac12 x^T A x$，$A$ 的特征值精心安排，
使算法前 $k$ 步的查询点被「卡」在 Krylov 子空间 $\mathrm{span}\{g_0,Ag_0,\dots,A^{k-1}g_0\}$ 内，
其逼近精度受 **Chebyshev 多项式**约束——这是 $\Omega(1/k^2)$ 下界的代数根。
于是「最优方法」有了精确含义：NAG 在 $L$-光滑类上匹配下界，**已无改进空间**（常数因子除外）。
本章还讨论 cutting-plane / bundle 方法的下界，统一了光滑与非光滑的复杂性图景。

#### 飞腾锚点

🟢 **matmul 15× [V03] → Hessian-vector / Jacobian 吞吐**。
下界证明中的二次型 $Ax$、Hessian-vector 乘积 $\nabla^2 f(x)\,h$，
以及最优二阶方法（cubic-regularized Newton、共轭梯度 CG）的每步核心，
都是矩阵-向量乘——专用矩阵核相对标量循环约 15× 加速。
这意味着：理论上「最优」的二阶方法在硬件上才有性价比——
加速（NAG）省步数、matmul 单元省每步成本，两者叠加是大规模优化的双重红利。
Krylov/CG 与 NAG 的「多项式加速」数学同构（都是 Chebyshev 多项式驱动），硬件实现也同源。

#### 关键定理

- **光滑下界定理（Nemirovsky-Yudin / Nesterov）**：对任意一阶方法，
  存在 $L$-光滑凸 $f:\mathbb{R}^n\to\mathbb{R}$（$n\ge k+1$）使
  $$f(x_k)-f^* \;\ge\; \frac{L\,\|x_0-x^*\|^2}{8(k+1)^2} \;=\; \Omega\!\left(\frac{L}{k^2}\right).$$
  故 NAG 的 $O(L/k^2)$ 在阶上**已最优**。
- **非光滑下界定理**：任意一阶方法存在 $G$-Lipschitz 凸 $f$ 使 $f(x_k)-f^*\ge\Omega(GR/\sqrt{k})$，
  故次梯度法的 $O(1/\sqrt{k})$ 已最优。
- **信息复杂性**：最优步数 $k^*(\epsilon)\asymp\sqrt{L/\epsilon}$（光滑）、$k^*\asymp(GR/\epsilon)^2$（非光滑）。

#### 自测

解释为何二次型 $f(x)=\tfrac12 x^T Ax$ 是「构造下界」的好选择：
(1) 算法第 $k$ 步的 $x_k$ 落在哪个子空间？为何（提示：递推 $x_{k+1}=x_k-\alpha_k Ax_k$）？
(2) 由此说明「步数 $k$ 能利用的信息维度 = $k$」，与 Chebyshev 多项式的极小极大性质如何联系？

---

### 第 5 章 · Polynomial-Time Methods / Interior-Point（多项式时间内点法）

#### 核心

前四章是一阶方法的舞台，本章换轨道到**二阶 + 结构**——**Self-Concordant（自协调）内点法**。
Nesterov（与 Nemirovsky 1994 合著的 *Interior-Point Polynomial Algorithms*）定义：
凸函数 $F$ 自协调，若
$$\big|D^3 F(x)[h,h,h]\big|\;\le\;2\,\big(D^2 F(x)[h,h]\big)^{3/2},\quad\forall x,h.$$
这一「三阶导被二阶导控制」的条件，使 **Newton 步**在该函数类上获得与函数本身无关的统一收敛性——
用局部范数 $\|h\|_x=\sqrt{h^T\nabla^2 F(x)h}$ 度量的 **Newton 减量** $\lambda(x)=\|\nabla F(x)\|_x^*$，
满足阻尼 Newton 步 $x^+=x-\frac{1}{1+\lambda(x)}[\nabla^2F(x)]^{-1}\nabla F(x)$ 每步必降。
带 $\nu$-self-concordant barrier 的可行域，沿中心路径跟踪，
需 $O(\sqrt{\nu}\log(1/\epsilon))$ 步达 $\epsilon$ 精度——**与维数无关的多项式时间**。
这是 LP/SOCP/SDP 求解器（Mosek、Gurobi 的 IPM）的理论地基。

#### 飞腾锚点

🟢 **GEMM 9.45 GFLOPS [Lab05] → 大规模 QP / SDP 二阶矩阵吞吐**。
内点法每步需解线性系统 $[\nabla^2 F(x)]\Delta x=-\nabla F(x)$（KKT 系统），
对大规模 QP/SDP 这是 $O(n^3)$ 的稠密或块稀疏矩阵分解——
专用 GEMM 单元约 9.45 GFLOPS 的吞吐，使内点法能在工程时间尺度上跑完。
IPM 的步数虽多项式（$O(\sqrt{\nu}\log(1/\epsilon))$），但**每步成本**完全由矩阵分解主导——
GEMM 的硬件加速是把「理论多项式时间」变成「实际可解」的关键，
也是为何 GPU/TPU 上做大模型二阶优化（K-FAC、natural gradient）近年来才可行。

#### 关键定理

- **Self-Concordance 定义**：凸开集上 $F\in C^3$ 自协调 $\Leftrightarrow$
  上述三阶/二阶导不等式成立（标准自协调再加 $\nabla^2 F(x)\preceq0$ 退化的边界控制）。
- **阻尼 Newton 下降**：$\lambda(x)=\lambda$ 时，
  $$F(x)-F(x^+) \;\ge\; \lambda - \ln(1+\lambda)\;\ge\;0,\qquad \lambda(x^+)\le\Big(\tfrac{\lambda}{1+\lambda}\Big)^2\big(<\lambda\big).$$
  故 $\lambda\le\tfrac14$ 后进入二次收敛区。
- **多项式迭代界**：对 $\nu$-self-concordant barrier，路径跟踪法达 $\epsilon$ 中心性需
  $$k \;=\; O\!\left(\sqrt{\nu}\,\ln\frac{\nu}{\epsilon}\right)\quad\text{步 Newton}.$$

#### 自测

取对数障碍函数 $F(x)=-\sum_{i=1}^n\ln x_i$（$x_i>0$），这是标准 $n$-self-concordant barrier。
(1) 求 $\nabla^2 F(x)$ 与局部范数 $\|\cdot\|_x$。
(2) 在 $x=\mathbf{1}$ 处计算 Newton 减量 $\lambda(x)$，验证阻尼 Newton 步使 $F$ 严格下降。

---

## §9 全书思想主线（约 200 字）

Nesterov 用「**复杂性下界 → 最优算法 → 自协调内点**」三步贯穿全书：

- **Ch1** 立 oracle 模型，定义「什么是算法的本质好坏」（步数 × 单步成本）；
- **Ch2** 光滑场景造出 NAG 把 $O(1/k)$ 抬到 $O(1/k^2)$；
- **Ch3** 非光滑场景认命 $O(1/\sqrt{k})$，但用 smoothing 把可结构化的非光滑偷渡回光滑加速；
- **Ch4** 下界定理锁死「再快不可能」，让 NAG/次梯度封顶为最优；
- **Ch5** 换 self-concordant + 二阶，得 $O(\sqrt{\nu}\log(1/\epsilon))$ 多项式时间。

这条主线与已读教材形成清晰分工：
**bertsekas_凸优化理论**（刚做完）给「对偶为何成立」的几何地基，
**D-凸优化（Boyd）**给「怎么把问题建模成凸」的工程手册，
**nocedal_wright** 给「怎么把算法跑稳」的数值实现，
而**本书 Nesterov** 回答最深一问——「为何这就是最快的」。
读完本书，你会把 PyTorch 里 `SGD(momentum=0.9)`、`Adam`、
NAdam 的 $O(1/k^2)$ 极限视为定理而非经验，
也会理解为何 SVM 的 QP 求解器必走内点法（多项式时间保证）。

---

## §10 交叉引用（与已读笔记 / AI 工程锚点）

1. **bertsekas_凸优化理论（本仓库，刚做完）**
   ：Bertsekas 给「对偶几何 + KKT + 鞍点」的地基，Nesterov 给「一阶方法的复杂度上限」。
   二者互补——Bertsekas Ch6 的近端/对偶上升没有最优性证明，
   本文 **Ch4** 下界定理补上「为何不能再快」。建议先 Bertsekas 后本书。

2. **D-凸优化 / boyd 简版（本仓库）**
   ：Boyd 教你「识别凸性、建模、用 cvxpy」，
   本文 **Ch1 oracle 模型**解释「为何凸性 + 一阶信息足够定复杂度」，
   **Ch2 NAG** 解释 cvxpy 之外、深度学习训练场上的加速本质。Boyd 是「用」，Nesterov 是「为何」。

3. **nocedal_wright_数值优化（本仓库，已读）**
   ：N&W 第 3 章（线搜索）、第 5 章（CG）、第 16 章（约束/IPM）是数值实现版；
   本文 **Ch5 self-concordance** 是 N&W IPM 章节的严格理论地基——
   N&W 说「步长用信赖域」，Nesterov 说「步长 $\tfrac{1}{1+\lambda}$ 来自自协调下降保证」。

4. **PyTorch NAdam / SGD(momentum)（AI 锚点）**
   ：`torch.optim.SGD(momentum=0.9)` 的动量项 $v_{k+1}=\mu v_k-\eta\nabla f$
   是 Heavy-Ball 法，与 **Ch2 NAG** 的 $y_{k+1}=x_{k+1}+\beta(x_{k+1}-x_k)$ 数学相近但 NAG 多一步「先看梯度再算动量」，
   理论上才有 $O(1/k^2)$；`NAdam`=Nesterov + Adam 自适应步长。
   本文 Ch2 让你分清「momentum（经验加速）」与「NAG（最优加速）」。

5. **Adam / 深度学习优化器（AI 锚点）**
   ：Adam $\approx$ 对角预条件 + 动量次梯度，落在本文 **Ch3 非光滑** 框架（神经网络损失多非凸/非光滑）。
   本文 **Ch4 下界** 提醒：Adam 的经验快不能违背 $O(1/\sqrt{k})$（非光滑）或 $O(1/k^2)$（光滑）的信息极限——
   它优化的是常数与自适应，不改变阶。

6. **SVM-QP 内点法 / 大规模优化（AI 锚点）**
   ：SVM 对偶 QP $\max_\alpha\sum\alpha_i-\tfrac12\alpha^TQ\alpha$（$Q_{ij}=y_iy_jx_i^Tx_j$），
   工业求解器（LIBSVM 的 SMO 是次优 active-set；大规模用 Mosek IPM），
   其 $O(\sqrt{\nu}\log(1/\epsilon))$ 多项式时间保证正是本文 **Ch5 self-concordant IPM** 的直接产物——
   也是为何量子化学（SCF 迭代的 SDP 子问题）、鲁棒控制（LMIs）都走内点法。

---

> **下一步**：沿 01-track/stage-1 精读做题；遇优化概念查 04-concepts/D-凸优化 跑三维交叉。
> 本笔记定位为 stage-3 优化方向的「复杂度最优性」研究入门第一教材。
> 建议配合已读 bertsekas_凸优化理论（对偶地基）与 nocedal_wright（数值实现）三方对照：
> bertsekas 讲「对偶为何成立」、Nesterov 讲「算法为何最快」、nocedal_wright 讲「算法怎么跑稳」。
