# Jonathan M. Borwein, Adrian S. Lewis《凸分析与非线性优化》 · 快速逐章精读

> **原书**：*Convex Analysis and Nonlinear Optimization: Theory and Examples*,
> Jonathan M. Borwein & Adrian S. Lewis, CMS Books in Mathematics, Springer, 2000 (2nd ed. 2006), ~280pp
> **读于**：2026-07-03
> **定位**：以泛函分析为地基、以 Fenchel 共轭为通用语言，在 Banach/Hilbert 空间中严格重建凸分析与非线性优化的全部核心定理。
> **特色**：Borwein-Lewis 把有限维凸分析「提升」到无穷维框架——Hahn-Banach 是全书第一块基石，
> 次微分理论（Clarke / proximal / limiting）远超 Bertsekas 的有限维版本，
> 习题与例子密度极高，数学味最浓。
> **声明**：本文为**快速逐章精读**（非逐页详读），每章只抓核心逻辑链、一个飞腾锚点、一两条关键定理、一道自测题。
> 全书 9 章 + 引言，忠于原书 TOC；章节命名给出英文原名。
>
> 三角定位 = **Borwein-Lewis**（泛函分析 · 共轭严格化）
> × **Bertsekas**（几何 · 对偶中心化，刚做）
> × **Nesterov**（算法 · 复杂度理论）
> 三者覆盖优化理论的「分析—几何—算法」三轴。

---

## §0 引言：泛函分析视角下的凸优化（约 350 字）

Borwein-Lewis 这部书的独特之处在于：它**把凸分析直接建立在 Banach/Hilbert 空间上**，
而非像 Rockafellar 经典《Convex Analysis》（1970）那样只在 $\mathbb{R}^n$ 里操作。
这意味着一切定理必须在无穷维中经得起检验——
Hahn-Banach 延拓定理替代了有限维分离定理的直觉，
弱拓扑（weak topology）替代了强拓扑下的「闭集 = 序列闭集」，
而 Fenchel 共轭 $f^*(u)=\sup_{x}\{\langle u,x\rangle-f(x)\}$ 成为贯穿全书的唯一通用语言。

这种「泛函分析优先」的选择有两个深层原因：
其一，变分问题与最优控制天然活在函数空间（$L^p$、Sobolev 空间）中，
有限维理论无法直接处理 PDE 约束优化；
其二，次微分理论在无穷维中会暴露有限维中被掩盖的精细结构——
Clarke 次微分、proximal 次微分、limiting 次微分的区分只有在无穷维才真正必要。

全书可读作「以 Fenchel-Young 不等式 $f^*(u)+f(x)\ge\langle u,x\rangle$ 为单一种子，
层层生长出次微积分 → 最优性 → 对偶 → 应用的完整树冠」。
Borwein 是实验数学与变分分析的大家，Lewis 则贡献了变分几何（variational geometry）的深刻洞察。
对用户（Python 工程级 + 数学补课）而言，
本书是读完 Bertsekas 几何版后的**第三轮严格化教材**——
Bertsekas 教你对偶的几何「为什么」，Borwein-Lewis 教你对偶在无穷维中「何时成立」。

**同类教材 4 列对比**：

| 书 | 风格 | 严格性 | 适合谁 |
|---|---|---|---|
| **Borwein & Lewis**《Convex Analysis & Nonlinear Optimization》(2000) | 泛函分析/弱拓扑风味，Fenchel 共轭严格化，无穷维优先 | 极高（分析味浓） | 数学专业、攻读变分/最优控制/非光滑分析的读者 |
| **Bertsekas**《Convex Optimization Theory》(2009) | 几何驱动，对偶为中心，有限维 + 图示交替 | 高（证明完整） | 想从几何直觉走到严格对偶的工程师/研究者 |
| **Rockafellar**《Convex Analysis》(1970) | 有限维经典，分离定理 + 次微分体系奠基，纯粹代数几何 | 极高（公认经典） | 想掌握有限维凸分析标准语言的数学系学生 |
| **Hiriart-Urruty & Lemaréchal**《Convex Analysis & Minimization Algorithms》(1993) | 两卷本，第一卷理论 + 第二卷算法，法式严谨 + 工程接口 | 高 | 想把凸分析与算法实现打通的应用数学家 |

---

## §1 全书 9 章骨架一览（飞腾锚点分布）

| 章 | 标题 | 核心概念 | 飞腾锚点 |
|:-:|------|---------|---------|
| 1 | Introduction and Notation | 记号、有限维回顾、全书路线图 | FP16 3.81×（精度景观） |
| 2 | Background: Functional Analysis | Banach/Hilbert、弱拓扑、Hahn-Banach | Schmidt 正交化 ⭐（正交分解） |
| 3 | Fundamental Concepts of Convex Analysis | 凸集、凸函数、Fenchel 共轭、epigraph | UDOT 16.9×（共轭内积求和） |
| 4 | Subdifferentials | Clarke/proximal/limiting 次微分、和规则 | Iron Law <2% ⭐（误差铁律） |
| 5 | Optimality Conditions | KKT、约束规范、Rockafellar-Pshenichnyi | 分支预测（active set） |
| 6 | Fenchel Duality and Applications | Fenchel 对偶定理、Fenchel-Young、投影 | matmul 15×（对偶映射/算子） |
| 7 | Lagrangian Duality | Sion minimax、鞍点、Slater | GEMM 9.45G（大规模 QP） |
| 8 | Exercises in Conjugacy | 共轭计算练习、Moreau 分解 | TLB 4.81×（稀疏结构） |
| 9 | Selected Applications | 变分不等式、最优控制、经济学 | FP16 3.81×（数值变分） |

> **读法建议**：Ch1–Ch2 若已读泛函分析可快速过（但 Hahn-Banach 与弱拓扑**必看**，是全书地基）；
> **Ch3 与 Ch4 必须精读**（Fenchel 共轭 + 三种次微分 = 全书灵魂）；
> Ch5–Ch7 是理论高潮（最优性 → Fenchel 对偶 → Lagrange 对偶），与 Bertsekas Ch4–Ch5 对照读收获最大；
> Ch8 是「练手」章，Ch9 给出变分/控制的出口。

---

## 第 1 章 · Introduction and Notation（引言与记号）

### 核心

本章是全书的「导览地图」。Borwein-Lewis 先回顾有限维 $\mathbb{R}^n$ 中的凸分析要点
（凸集分离、epigraph 判定、保凸运算），再声明：**本书将把这些结论推广到任意 Banach 空间 $E$**。
关键记号：$E^*$ 为 $E$ 的对偶空间（连续线性泛函全体），
$\langle\cdot,\cdot\rangle:E^*\times E\to\mathbb{R}$ 为配对，
$\|\cdot\|$ 为范数。$f:E\to(-\infty,+\infty]$ 为扩充实值函数，
epigraph $\text{epi}\,f=\{(x,r):f(x)\le r\}$。
全书统一用「下半连续（lsc）+ 真（proper）」作为标准假设——
这两个条件保证 Fenchel 共轭的双共轭定理（$f^{**}=f$）成立。

### 飞腾锚点

🟡 **FP16 3.81× [L01] → 精度景观**。
全书的共轭计算 $f^*(u)=\sup_x\{\langle u,x\rangle-f(x)\}$ 涉及无穷维上确界，
数值上必须离散化截断。FP16 的 3.81× 吞吐增益适合大规模共轭值的批量估算，
但 $\sup$ 运算对精度敏感（FP16 仅 3 位有效十进制）——
这正对应书中为何反复强调「lsc + proper」假设：它是数值稳定的分析条件，
正如 FP16 需要舍入补偿才能稳定。

### 关键定理

- **真凸函数**：$f$ 真（$\exists x,\ f(x)<+\infty$）且凸。
- **Fenchel 共轭定义**：$f^*(u)=\sup_{x\in E}\{\langle u,x\rangle-f(x)\}\in(-\infty,+\infty]$，
  $f^*$ 始终凸且 lsc（无论 $f$ 如何）。

### 自测

写出 $f(x)=\frac12\|x\|^2$ 的 Fenchel 共轭 $f^*(u)$（在 Hilbert 空间中，$E=E^*$）。
提示：对 $\langle u,x\rangle-\frac12\|x\|^2$ 关于 $x$ 求导取零点。

---

## 第 2 章 · Background: Functional Analysis（泛函分析背景）

### 核心

本章是全书的数学地基，给非泛函分析背景的读者补课。
核心三件套：

- **Banach 空间**：完备赋范线性空间。$\ell^p$、$L^p$、$C(K)$ 是典型例子。
- **Hilbert 空间**：内积空间 + 完备性，满足 Riesz 表示定理（$E=E^*$，每个连续泛函是内积）。
- **弱拓扑 $\sigma(E,E^*)$**：$x_n\rightharpoonup x$（弱收敛）指 $\langle\varphi,x_n\rangle\to\langle\varphi,x\rangle$ 对一切 $\varphi\in E^*$。
  弱收敛比强（范数）收敛弱，但**弱序列紧致**（Eberlein-Šmulian：自反 Banach 空间中闭球弱序列紧），
  这是替代有限维 Weierstrass 定理（紧致 $\Rightarrow$ 极值可达）的关键工具。

**Hahn-Banach 定理**（解析形式）：子空间上的受控线性泛函可延拓到全空间——
这是凸分析「分离超平面」在无穷维的化身，全书对偶理论的源头。

### 飞腾锚点

🟢 **Schmidt 正交化 ⭐ → Hilbert 空间正交分解**。
Hilbert 空间的核心特权是**正交分解** $E=M\oplus M^\perp$：
任意元素 $x$ 唯一拆成「在闭子空间 $M$ 上的投影 + 正交残差」。
这正是 Gram-Schmidt 正交化的无穷维推广——
投影算子 $P_M$ 满足 $\|x-P_Mx\|=\min_{z\in M}\|x-z\|$（最佳逼近）。
Borwein-Lewis 在 Ch6 用此分解建立 Moreau 分解（$x=\text{prox}_f(x)+\text{prox}_{f^*}(x)$），
在 Ch5 用它给出 KKT 条件的法空间分解——
约束梯度张成的子空间与零空间正交，互补松弛即「残差与有效约束正交」。

### 关键定理

- **Hahn-Banach（解析形式）**：$g:M\to\mathbb{R}$ 线性、$p:E\to\mathbb{R}$ 次线性且 $g\le p$ 在子空间 $M$ 上，
  则 $\exists$ 延拓 $\tilde g:E\to\mathbb{R}$ 使 $\tilde g\le p$ 在全 $E$ 上。
- **Hahn-Banach（几何形式 / 分离定理）**：$C$ 非空开凸集、$x_0\notin C$，
  则 $\exists\varphi\in E^*$ 使 $\varphi(x)<\varphi(x_0)$ 对一切 $x\in C$。
- **Riesz 表示**：Hilbert 空间中每个 $\varphi\in E^*$ 唯一对应 $y\in E$ 使 $\varphi(x)=\langle y,x\rangle$。
- **Eberlein-Šmulian**：Banach 空间自反 $\Leftrightarrow$ 闭单位球弱序列紧。

### 自测

在 $\ell^2$ 中，证明弱收敛 $x_n\rightharpoonup x$ 不蕴含强收敛 $\|x_n-x\|\to0$。
提示：取标准基 $e_n$，证明 $e_n\rightharpoonup 0$ 但 $\|e_n\|=1\not\to0$。

---

## 第 3 章 · Fundamental Concepts of Convex Analysis（凸分析基本概念）

### 核心

本章在 Banach 空间中系统建立凸集与凸函数的理论。
凸集的核心工具是**支撑超平面**（Hahn-Banach 几何形式的直接应用）：
每个闭凸集边界点都有一个支撑超平面。
凸函数靠 **epigraph** 判定（$f$ 凸 $\Leftrightarrow$ epi $f$ 凸），
而**闭性**（lsc）等价于 epigraph 为闭集。

**Fenchel 共轭** $f^*(u)=\sup_x\{\langle u,x\rangle-f(x)\}$ 是本章也是全书的中心角色。
两条基本性质将反复使用：
（i）$f^*$ 始终凸且 lsc（即使 $f$ 不凸）；
（ii）Fenchel-Young 不等式 $f(x)+f^*(u)\ge\langle u,x\rangle$，等号 $\Leftrightarrow u\in\partial f(x)$。
**双共轭定理**（Fenchel-Moreau）：$f$ 真 lsc 凸 $\Leftrightarrow f^{**}=f$——
这是「共轭语言」合法性的基石，保证对偶不丢失信息。

### 飞腾锚点

🟡 **UDOT 16.9× [E05] → 共轭内积求和**。
Fenchel 共轭的核心运算是配对 $\langle u,x\rangle$ 的批量计算与上确界搜索。
在离散化场景（$E=\mathbb{R}^n$）中，$f^*(u)$ 需要对每个 $u$ 遍历所有 $x$ 算内积——
点积加速器（DOT/UDOT）的 16.9× 吞吐使大规模共轭表（conjugate lookup table）的预计算可行。
在 Moreau 分解和近端算子的实现中，$\text{prox}_f + \text{prox}_{f^*}=I$ 的每步都涉及内积求和，
UDOT 宽度直接决定近端迭代的墙钟时间。

### 关键定理

- **Fenchel-Young 不等式**：$\forall x\in E,\ u\in E^*$，
  $$f(x)+f^*(u)\ge\langle u,x\rangle,$$
  等号成立 $\Leftrightarrow u\in\partial f(x)$。
- **Fenchel-Moreau 双共轭定理**：$f$ 真 lsc 凸 $\Rightarrow f^{**}=f$。
- **支撑定理**：$C$ 闭凸、$x_0\in\partial C$（边界），则 $\exists\ 0\neq\varphi\in E^*$ 支撑 $C$ 于 $x_0$。

### 自测

设 $f(x)=\delta_C(x)$（集合 $C$ 的指示函数：$C$ 内为 $0$，$C$ 外为 $+\infty$）。
证明 $f^*=\sigma_C$（$C$ 的支撑函数 $\sigma_C(u)=\sup_{x\in C}\langle u,x\rangle$），
并写出 $\sigma_C$ 何时真 lsc。

---

## 第 4 章 · Subdifferentials（次微分）⭐ 全书灵魂之一

### 核心

梯度要求函数可微，而优化中的核心函数常常不可微（$|x|$、$\max(0,x)$、指示函数 $\delta_C$）。
**凸次微分**推广了梯度：
$$\partial f(x)=\{u\in E^*:\ f(y)\ge f(x)+\langle u,y-x\rangle,\ \forall y\in E\}.$$
它是闭凸集，当 $f$ 凸且在 $x$ 处连续时非空。

Borwein-Lewis 远超有限维教材之处在于系统介绍三种**非凸/非光滑次微分**：

- **Clarke 次微分** $\partial_C f$：局部 Lipschitz 函数的广义梯度，由方向导数的上极限定义，始终闭凸；
- **proximal 次微分** $\partial_P f$：用近端法向量定义，比 Clarke 更细但可能非凸；
- **limiting 次微分** $\partial_L f$：proximal 次微分的序列极限，捕捉 Clarke 遗漏的「极限信息」。

三者关系：$\partial_P f\subseteq\partial_L f\subseteq\partial_C f$（凸函数时三者合一为凸次微分）。
**次微分和规则** $\partial(f+g)\subseteq\partial f+\partial g$（等号需约束规范）
是优化计算的核心工具，直接推出 Ch5 的最优性条件。

### 飞腾锚点

🟢 **Iron Law <2% ⭐ [Lab00] → 次微分误差铁律**。
飞腾性能铁律「性能 = 指令数 × CPI × 时钟频率」，误差 $<2\%$ 即可控。
次微分和规则的等号条件（constraint qualification）正是分析版的「误差铁律」：
$\partial(f+g)=\partial f+\partial g$ 当且仅当两个函数的 epigraph 满足某种内部条件（如之一连续），
否则等式可能**不成立**——次微分之和严格大于和之次微分。
这种「等号失效」对应数值中的误差泄漏：若和规则误用（忽视约束规范），
最优性条件会给出错误驻点，正如忽视 CPI 变化的性能估算偏差超过 2% 就失控。
Borwein-Lewis 全书最谨慎处即在此：每次使用和规则都标注前提条件。

### 关键定理

- **凸次微分存在性**：$f$ 凸 lsc 真、$x\in\text{int}(\text{dom}\,f)$ $\Rightarrow\partial f(x)\neq\varnothing$。
- **次微分和规则**：$f,g$ 凸 lsc，若 $\text{int}(\text{dom}\,f)\cap\text{dom}\,g\neq\varnothing$（或等价的约束规范），则
  $$\partial(f+g)(x)=\partial f(x)+\partial g(x).$$
- **Clarke 次微分链式法则**：$F$ Lipschitz、$g:\mathbb{R}\to\mathbb{R}$ 光滑，
  $\partial_C(g\circ F)(x)\subseteq g'(F(x))\cdot\partial_C F(x)$。
- **次微分与共轭的互反性**：$u\in\partial f(x)\Leftrightarrow x\in\partial f^*(u)\Leftrightarrow f(x)+f^*(u)=\langle u,x\rangle$。

### 自测

求 $f(x)=|x|$ 在 Hilbert 空间中 $x=0$ 处的凸次微分 $\partial f(0)$。
再验证 Fenchel-Young 等号条件：哪些 $u\in\partial f(0)$ 满足 $f(0)+f^*(u)=\langle u,0\rangle=0$？

---

## 第 5 章 · Optimality Conditions（最优性条件）

### 核心

标准约束优化问题 $\min f(x)$ s.t. $g_i(x)\le0$（$i=1,\ldots,m$）。
无约束时 $0\in\partial f(x^*)$ 即最优（凸情形）。
有约束时，最优性由 **KKT 条件**给出——
但 KKT 成立需要**约束规范**（constraint qualification, CQ），
否则最优解可能存在却没有满足 KKT 的乘子。

Borwein-Lewis 用次微分语言统一了所有 CQ：
**Mangasarian-Fromovitz（MFCQ）**、**Slater 条件**（凸情形）、
**Rockafellar-Pshenichnyi 条件**（非光滑情形）本质都是
「约束函数的次微分在最优点的组合能覆盖目标函数的次微分」。
**Rockafellar-Pshenichnyi 定理**直接给出非光滑约束的最优性：
$$0\in\partial f(x^*)+\sum_i\lambda_i\partial g_i(x^*)+N_C(x^*)$$
（$N_C$ 为法锥），附加互补松弛 $\lambda_i g_i(x^*)=0$。
这是 KKT 在非光滑/无穷维下的最终形式。

### 飞腾锚点

🟡 **分支预测 [Lab02]（0.71 vs 3.14 cycles）→ active set 选择**。
KKT 中互补松弛条件 $\lambda_i g_i(x^*)=0$ 把约束分成两类：
$g_i(x^*)=0$（active，有效）和 $g_i(x^*)<0$（inactive，无效）。
active set 的判定本质是条件分支——
分支预测器猜对时 0.71 cycles（约束模式稳定），猜错时 3.14 cycles（active set 频繁切换）。
这正是 active-set QP 求解器的核心瓶颈：warm-start 沿用上一步 active set 可让分支高度可预测，
而 cold-start 或退化情形下 active set 反复变动，分支失配惩罚累积。
Borwein-Lewis 的约束规范理论告诉你「何时 KKT 乘子存在且唯一」——
唯一性高 = active set 稳定 = 分支可预测。

### 关键定理

- **Fermat 法则（无约束）**：$\bar x$ 最优 $\Rightarrow 0\in\partial f(\bar x)$（凸 lsc 真函数）。
- **KKT（凸 + Slater）**：$f,g_i$ 凸 lsc、$\exists\tilde x$ 使 $g_i(\tilde x)<0$，则 $\bar x$ 最优 $\Leftrightarrow$
  $$\exists\lambda_i\ge0:\quad 0\in\partial f(\bar x)+\sum_i\lambda_i\partial g_i(\bar x),\quad \lambda_i g_i(\bar x)=0.$$
- **Rockafellar-Pshenichnyi（非光滑）**：约束规范满足时，
  $0\in\partial f(\bar x)+N_S(\bar x)$，$S$ 为可行域，$N_S$ 为正规锥。

### 自测

对 $\min\|x\|$ s.t. $Ax=b$（$A$ 满行秩）：
用 KKT 推出最优解 $x^*=A^T(AA^T)^{-1}b$，并指出哪个约束规范保证了乘子存在。

---

## 第 6 章 · Fenchel Duality and Applications（Fenchel 对偶与应用）

### 核心

Fenchel 对偶是全书的高潮之一，把「原问题」与「对偶问题」用共轭函数精确焊接。
原始问题 $\inf_x\{f(x)+g(Ax)\}$（$A:E\to Y$ 有界线性），
对偶问题 $\sup_y\{-f^*(-A^Ty)-g^*(y)\}$——
**Fenchel 对偶定理**保证在约束规范下两者相等（对偶间隙为零）。
这比 Bertsekas 的 Lagrange 对偶更「纯分析」：
无需显式构造 Lagrange 函数，全靠 Fenchel-Young 不等式推出弱对偶 $d^*\le p^*$，
再由约束规范（如 $0\in\text{int}(\text{dom}\,g-A\,\text{dom}\,f)$）推出强对偶。

**Moreau 分解**是本章的另一宝石：
$x=\text{prox}_f(x)+\text{prox}_{f^*}(x)$（Hilbert 空间），
把近端算子与共轭对称地配对——
近端梯度法（ISTA/FISTA）的全部优雅都来自这条恒等式。
**投影**作为指示函数的 prox 也在此统一：$P_C=\text{prox}_{\delta_C}$。

### 飞腾锚点

🟡 **matmul 15× [V03] → 对偶映射/线性算子吞吐**。
Fenchel 对偶中线性算子 $A$ 及其伴随 $A^*$ 反复出现：
$f^*(-A^Ty)$ 的计算需要 $A^Ty$（矩阵-向量乘），
而近端迭代的每步都涉及 $A$ 与 $A^T$ 的交替作用（如 ADMM 的 $x$-更新与 $z$-更新）。
矩阵乘法单元 15× 加速使大规模 Fenchel 对偶（图像去噪、Lasso、矩阵补全）
在合理时间内可行——
这正是为何 GPU/TPU 的 GEMM 核成为现代优化计算的物理基础。
Borwein-Lewis 的 $A$ 是无穷维算子（积分算子、微分算子），
数值离散化后变成大矩阵，matmul 加速同样适用。

### 关键定理

- **Fenchel 对偶定理**：$f:E\to(-\infty,+\infty]$、$g:Y\to(-\infty,+\infty]$ 真 lsc 凸、$A:E\to Y$ 有界线性，
  若 $0\in\text{int}(\text{dom}\,g-A\,\text{dom}\,f)$，则
  $$\inf_{x\in E}\{f(x)+g(Ax)\}=\sup_{y\in Y}\{-f^*(-A^Ty)-g^*(y)\},$$
  且右侧上确界可达。
- **Moreau 分解**：$f$ 真 lsc 凸、Hilbert 空间中，
  $$x=\text{prox}_f(x)+\text{prox}_{f^*}(x),\qquad \text{prox}_f(x)=\arg\min_u\{f(u)+\tfrac12\|u-x\|^2\}.$$
- **次微分与共轭的联系**：$\partial f^*=(\partial f)^{-1}$（多值映射的逆）。

### 自测

用 Fenchel 对偶定理推导 $\inf_x\{f(x)+\|Ax-b\|\}$ 的对偶问题
（取 $g(y)=\|y-b\|$），写出对偶变量 $y$ 的约束域 $\text{dom}\,g^*$。

---

## 第 7 章 · Lagrangian Duality（Lagrange 对偶）

### 核心

Lagrange 对偶是 Fenchel 对偶的「约束显式化」版本。
Lagrange 函数 $L(x,\lambda)=f(x)+\sum_i\lambda_i g_i(x)$，
对偶函数 $q(\lambda)=\inf_x L(x,\lambda)$ 始终凹（inf of 仿射族），
弱对偶 $d^*\le p^*$ 无条件成立。

**Sion 极小极大定理**是本章的理论核心：
$f$ 拟凸拟凹、$X$ 紧或 $Y$ 紧时，
$$\inf_{x\in X}\sup_{y\in Y}f(x,y)=\sup_{y\in Y}\inf_{x\in X}f(x,y).$$
这比 von Neumann 经典 minimax 更一般（只需拟凸拟凹 + 单侧紧致），
直接推出强对偶（鞍点存在 $\Leftrightarrow$ 对偶间隙为零）。
**Slater 条件**（凸情形）是 Sion 定理的可验证版本：
存在严格可行点即可保证 $d^*=p^*$。
**鞍点** $(x^*,\lambda^*)$ 满足 $L(x^*,\lambda)\le L(x^*,\lambda^*)\le L(x,\lambda^*)$，
是原最优与对偶最优的统一刻画。

### 飞腾锚点

🟢 **GEMM 9.45G [Lab05] → 大规模 QP / 内点法吞吐**。
Lagrange 对偶在 QP（SVM、投资组合、MPC）中的数值实现是内点法（interior point）：
每步解 KKT 线性系统 $\begin{pmatrix}H&A^T\\A&0\end{pmatrix}\begin{pmatrix}\Delta x\\\Delta\lambda\end{pmatrix}=-r$，
其核心是大规模稠密 / 稀疏矩阵分解。
GEMM 单元 9.45 GFLOPS 的吞吐使万维 QP 的内点迭代（每步 $O(n^3)$）
在秒级完成——
这是为何 libsvm / CVXPY / OSQP 能在工程中实用。
Sion 定理保证鞍点存在 = 内点法收敛到正确解；
GEMM 保证它收敛得够快。
Borwein-Lewis 的贡献是把 Sion 定理放到无穷维框架中，
使变分不等式与 PDE 约束优化的数值求解也有理论保障。

### 关键定理

- **弱对偶**：$q(\lambda)\le p^*$ 对一切 $\lambda\ge0$ 恒成立，无需凸性。
- **Sion 极小极大定理**：$X$ 紧凸、$Y$ 凸、$f(\cdot,y)$ 拟凸 lsc、$f(x,\cdot)$ 拟凹 usc，则
  $$\inf_X\sup_Y f=\sup_Y\inf_X f.$$
- **强对偶（Slater）**：凸 + $\exists\tilde x$ 使 $g_i(\tilde x)<0$ $\Rightarrow d^*=p^*$ 且对偶最优可达。
- **鞍点刻画**：$(x^*,\lambda^*)$ 是 $L$ 的鞍点 $\Leftrightarrow x^*$ 原最优、$\lambda^*$ 对偶最优且无间隙。

### 自测

写出 $\min\frac12\|x\|^2$ s.t. $Ax\le b$（$A$ 行满秩）的 Lagrange 对偶问题，
用 Sion 定理验证 $d^*=p^*$（指出 $X$、$Y$ 的紧凸性从何而来）。

---

## 第 8 章 · Exercises in Conjugacy（共轭应用练习）

### 核心

本章是「练手」章，用前 7 章的工具系统计算常见函数的共轭、次微分与近端算子。
核心案例：
- 范数 $\|x\|$ 的共轭是对偶单位球的指示函数 $\delta_{B_{*}}$；
- $L_1$ 范数 $\|x\|_1$ 的近端算子是软阈值 soft-thresholding；
- $L_2$ 范数 $\|x\|_2$ 的近端算子是块软阈值；
- 指示函数 $\delta_C$ 的近端算子是投影 $P_C$；
- 透视函数的共轭仍是透视（保结构）。

**Moreau 分解**在此章反复使用，是把「prox of $f$」转化为「prox of $f^*$」的桥梁。
这些练习不是装饰——它们是 Ch9 应用章的计算弹药，
也是用户在 PyTorch 中实现自定义正则化项（group Lasso、total variation、nuclear norm）的直接理论依据。

### 飞腾锚点

🟡 **TLB 4.81× [E04] → 稀疏共轭结构**。
$L_1$ 范数的近端算子（软阈值）产生**稀疏解**——大部分分量为零。
稀疏向量在内存中跳跃访问，TLB（Translation Lookaside Buffer）失配惩罚 4.81×。
共轭计算中，$f^*$ 的 dom 往往是低维结构（如对偶球），访问模式高度局部化——
TLB 友好的数据布局（CSR 稀疏存储 + cache-blocking）
使大规模共轭/近端迭代不被内存延迟拖垮。
这正是 Lasso / 弹性网 / 稀疏编码的数值实现核心瓶颈：
算术不是瓶颈，内存局部性才是，而 Borwein-Lewis 的稀疏共轭理论告诉你「哪些结构值得利用」。

### 关键定理（工具箱）

- **范数共轭**：$f(x)=\|x\|$ $\Rightarrow$ $f^*(u)=\delta_{B^*}(u)$（$B^*=\{u:\|u\|_*\le1\}$ 对偶单位球）。
- **软阈值**：$\text{prox}_{\lambda\|\cdot\|_1}(z)=\text{sign}(z)\odot\max(|z|-\lambda,0)$（逐分量）。
- **核范数近端**：$\text{prox}_{\lambda\|\cdot\|_*}(Z)=U\,\text{diag}(\max(\sigma_i-\lambda,0))\,V^T$（SVD 软阈值）。
- **共轭运算表**：$(f+g)^*\neq f^*+g^*$（一般），但 $(\alpha f)^*=\alpha f^*(\cdot/\alpha)$（$\alpha>0$）。

### 自测

求 elastic net 正则项 $f(x)=\lambda_1\|x\|_1+\frac{\lambda_2}{2}\|x\|_2^2$ 的近端算子。
提示：先做 $L_2$ 梯度步（解析缩放），再施加 $L_1$ 软阈值。

---

## 第 9 章 · Selected Applications（精选应用）

### 核心

本章给出理论的出口，核心三类：

- **变分不等式（Variational Inequality, VI）**：找 $x^*\in C$ 使 $\langle F(x^*),x-x^*\rangle\ge0$ 对一切 $x\in C$。
  当 $F=\nabla f$ 时退化为凸优化；一般情形刻画均衡（Nash 均衡、交通均衡、市场出清）。
  KKT 条件是 VI 的特例。
- **最优控制**：$\min\int_0^T L(x(t),u(t))\,dt$ s.t. $\dot x=h(x,u)$。
  Pontryagin 极大值原理是非光滑最优性条件在函数空间中的化身——
  Hamilton 伴随方程即 KKT 的无穷维版本。
- **经济学应用**：影子价格 = 对偶变量；资源分配的互补松弛条件即市场出清。

Borwein-Lewis 的无穷维框架使这些应用有了严格基础：
VI 的解存在性靠弱拓扑紧致性（Eberlein-Šmulian），
最优控制的伴随方程在 Sobolev 空间中成立，
而非有限维教材中的「形式推导」。

### 飞腾锚点

🟡 **FP16 3.81× [L01]（再现）→ 数值变分精度**。
变分不等式与最优控制的数值求解（有限元离散 + 迭代法）涉及大规模 PDE 系统。
FP16 的 3.81× 吞吐使实时 MPC（模型预测控制）可行——
每秒需解数百个 QP 的场景（无人机控制、自动驾驶）中，
低精度浮点 + Borwein-Lewis 的鲁棒次微分理论（Clarke 次微分对 Lipschitz 扰动稳定）
构成「理论鲁棒性 + 硬件效率」的组合。
但变分不等式的解对精度敏感（退化情形下乘子不唯一），
FP16 需配合混合精度策略——这呼应 Ch1 的精度景观锚点，首尾呼应。

### 关键定理

- **VI 解的存在性（Hartman-Stampacchia）**：$C$ 紧凸、$F$ 连续 $\Rightarrow$ VI$(F,C)$ 有解。
- **Pontryagin 极大值原理（形式）**：最优控制 $u^*$ 满足
  $H(x^*,u^*,p)=\max_u H(x^*,u,p)$，伴随方程 $\dot p=-\partial_x H$。
- **互补均衡**：市场出清 $\Leftrightarrow$ 互补松弛条件（供给 = 需求）。

### 自测

把交通均衡（Wardrop 第一原理）写成变分不等式：
路径选择 $x^*$ 满足 $\langle F(x^*),x-x^*\rangle\ge0$ 对一切可行路径 $x$，
指出 $F$ 的物理含义（路段出行时间）。

---

## §9 全书思想主线（约 200 字）

Borwein-Lewis 的主线是「**以泛函分析为地基，以 Fenchel 共轭为种子，生长出整棵优化理论之树**」：

- **Ch2** 泛函分析（Hahn-Banach = 分离定理的无穷维化身，弱拓扑 = 紧致性的替代品）
- → **Ch3** 凸分析基本概念（epigraph + Fenchel 共轭 = 统一语言）
- → **Ch4** 次微分（Clarke/proximal/limiting 三层结构 = 非光滑分析的核心）
- → **Ch5** 最优性条件（Rockafellar-Pshenichnyi = KKT 的非光滑终极形式）
- → **Ch6** Fenchel 对偶（共轭语言下的原-对偶等式 + Moreau 分解）
- → **Ch7** Lagrange 对偶（Sion minimax = 鞍点存在的分析条件）
- → **Ch9** 应用（VI / 最优控制 / 经济学 = 无穷维理论的出口）。

与 **Bertsekas**（有限维几何 + 对偶中心化）对照：
Bertsekas 教你对偶的「几何为什么」，Borwein-Lewis 教你对偶在无穷维中「何时成立」；
与 **Nesterov**（算法复杂度）对照：
Nesterov 关心「多少步收敛」，Borwein-Lewis 关心「收敛到的东西有没有意义」（解的存在性、乘子的存在性）；
与 **nocedal_wright**（数值实现）对照：
N&W 是「怎么跑」，Borwein-Lewis 是「跑的理论前提是什么」。
三者形成优化理论的「分析—几何—算法」三角，
而 Borwein-Lewis 是三角中**分析性最强、最不容偷懒**的那个顶点。

---

## §10 交叉引用（与已读笔记 / AI 工程锚点）

1. **bertsekas_凸优化理论（本仓库，刚做）**
   ：Bertsekas Ch4 Lagrange 对偶是有限维几何版，证明用分离定理 + 图示；
   本文 **Ch6–Ch7** 给出同一结论的泛函分析版——
   Fenchel 对偶定理用 Hahn-Banach + 弱拓扑证明，Sion minimax 替代 von Neumann。
   两者互补：Bertsekas 建立直觉，Borwein-Lewis 验证无穷维有效性。

2. **D-凸优化（Boyd 风格，本仓库）**
   ：Boyd 第 5 章对偶假设 Slater「显然满足」，一笔带过约束规范；
   本文 **Ch5** Rockafellar-Pshenichnyi 给出约束规范的**完整层级**
   （Slater ⊂ MFCQ ⊂ Abadie ⊂ Guignard），解释「为何对偶间隙有时不为零」。
   D 笔记用于「快速建模」，本文用于「理解何时理论成立」。

3. **nesterov_凸优化算法引论（本仓库，已读）**
   ：Nesterov 关心 $O(1/k^2)$ 加速率与 oracle 复杂度下界；
   本文 **Ch4** 次微分理论给出 Nesterov 假设的「$f$ 凸 + Lipschitz」的分析基础——
   Lipschitz 连续性在 Borwein-Lewis 中由 Clarke 次微分的界严格定义。
   Nesterov 是「算法天花板」，本文是「算法前提的地基」。

4. **nocedal_wright_数值优化（本仓库，已读）**
   ：N&W 第 12 章 QP 的 active-set 法、第 16 章增广 Lagrange 的数值实现，
   直接依赖本文 **Ch5** 的 KKT 与约束规范理论。
   N&W 的内点法每步解的 KKT 系统，其正确性由本文 **Ch6** Fenchel 对偶定理保证。

5. **folland实分析 / rudin_pma（本仓库，已读）**
   ：本文 **Ch2** 的 Banach/Hilbert 空间、弱拓扑、Hahn-Banach
   正是 Folland 第 5 章（Banach 空间）与 Rudin PMA 的泛函分析延伸。
   读 Borwein-Lewis 前建议复习 Folland 的弱拓扑与 Riesz 表示。

6. **AI/工程锚点**：
   - **深度学习 $L_1$/$L_2$ 正则化的次微分**：本文 **Ch4** $\partial\|x\|_1$（软阈值）与 $\partial\|x\|_2^2$（梯度），
     直接对应 Lasso（$L_1$）、Ridge（$L_2$）、Elastic Net 的优化几何。
   - **Adam vs Subgradient Method**：Adam 的对角预条件 = 自适应步长次梯度法（本文 **Ch4**）；
     本文的次微分和规则解释「为何 Adam + $L_1$ 的 prox 更新在理论上合理」。
   - **SVM 对偶**：硬间隔 SVM 的 Lagrange 对偶（本文 **Ch7**）在无限维 RKHS 中
     仍由 Sion minimax 保证 $d^*=p^*$——这是核方法的理论合法性来源（与 scholkopf_smola 笔记呼应）。
   - **矩阵补全 / 核范数**：本文 **Ch8** 核范数近端算子（SVD 软阈值）
     是推荐系统协同过滤的直接工具，Moreau 分解保证 prox 可计算。

---

> **下一步**：沿 01-track/stage-1 精读做题；遇优化概念查 04-concepts/D-凸优化 跑三维交叉。
> 本笔记定位为 stage-3 优化方向的「泛函分析严格化」第三轮教材。
> 建议配合已读 **bertsekas_凸优化理论**（几何对偶）+ **nesterov_凸优化算法引论**（算法复杂度）形成三角对照：
> Borwein-Lewis 补上「无穷维中何时成立」的分析严格性，
> 与 Bertsekas 的几何直觉 + Nesterov 的算法下界共同构成优化理论的完整图景。
