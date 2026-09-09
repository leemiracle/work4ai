# Jean-Baptiste Hiriart-Urruty, Claude Lemaréchal《凸分析与极小化算法 I: 基础》 · 快速逐章精读

> **原书**：*Convex Analysis and Minimization Algorithms I: Fundamentals*,
> J.-B. Hiriart-Urruty & C. Lemaréchal, Grundlehren der mathematischen Wissenschaften 305, Springer, 1993, ~430pp
> **读于**：2026-07-03
> **定位**：凸分析严格理论与**可实现极小化算法**之间最完整的桥梁——
> 在它之前 Rockafellar 只讲「为什么成立」却不讲「怎么算」，Borwein-Lewis/Bertsekas 也偏分析而轻算法。
> HUL 把有限维凸分析（与 Rockafellar 同级严谨）直接接到线搜索、Newton、共轭梯度、拟 Newton、次梯度、bundle 法。
> **特色**：Lemaréchal 是 **bundle method 的发明者之一**——非光滑凸优化最强大的工业级算法至今仍是他的遗产。
> 全书有一条独特的「理论 → 可实现算法」单链，每条定理都是后续某个优化器的合法性来源。
> **声明**：本文为**快速逐章精读**（非逐页详读），每章只抓核心逻辑链、一个飞腾锚点、一两条关键定理、一道自测题。
> 📌 **忠于真实 TOC 的说明**：HUL 原书为两卷——
> Vol I（Grundlehren 305, *Fundamentals*）含凸集/凸函数/次微分/共轭 + 可微函数极小化；
> Vol II（Grundlehren 306, *Advanced*）含非光滑优化（次梯度/bundle）、共轭梯度、拟 Newton、信赖域、次微分计算。
> 本文的 10 章是**两卷核心内容的合并教学地图**，每章标注真实归属，忠实映射、未擅改内容。
>
> 凸分析三角 = **Hiriart-Urruty & Lemaréchal**（有限维 · 理论+算法双链 · 本书）
> × **Rockafellar**（有限维 · 公理奠基 · 纯理论，同期生成 348 行）
> × **Borwein-Lewis**（泛函分析 · 无穷维严格化 · 刚做 536 行）
> 三者覆盖凸分析的「理论算法双链—公理源头—分析提升」三轴。

---

## §0 引言：当凸分析「会算」（约 350 字）

Hiriart-Urruty & Lemaréchal 这部两卷本是凸分析与优化算法之间最完整的桥梁。
Rockafellar 1970 奠定了凸分析的语言，但它**纯理论、无算法、对工程师几乎不可用**；
Borwein-Lewis 把理论提升到 Banach 空间，Bertsekas 用几何讲对偶——
三者都在「分析」一侧发力，却几乎没有一本告诉你「拿到一个凸函数，怎么写代码把它极小化」。
HUL 填补的正是这个缺口：第一卷用有限维严格重建凸集、凸函数、次微分、共轭（与 Rockafellar 同级严谨），
然后立刻把这套理论接到可微函数的线搜索、Newton、共轭梯度、拟 Newton，
再到非光滑的次梯度法与 bundle 法。

Lemaréchal 是 bundle method 的发明者之一——
这是非光滑凸优化最强大的实用算法，至今仍是黑箱优化的工业标准。
因此全书有一条独特的「理论 → 可实现算法」单链：
每一条定理（次微分、共轭、Moreau 分解）都不是为了优美而存在，
而是为后续某个算法（近端、bundle、信赖域）提供合法性。
HUL 的法式严谨 + 工程接口风格，使它成为「想理解 BFGS / Adam / 次梯度法为何能跑」的应用数学家的必读。

对用户（Python 工程级，`torch.optim.LBFGS` / `torch.optim.Adam` 的使用者）而言，
本书是**唯一能把「凸分析公理」直接接到「优化器代码」的教材**——
读完它，你看 PyTorch 优化器不再是黑箱，而是凸分析定理的工程化身。

**凸分析三角 · 同类教材 4 列对比**：

| 书 | 风格 | 严格性 | 适合谁 |
|---|---|---|---|
| **Hiriart-Urruty & Lemaréchal**《Convex Analysis & Minimization Algorithms I/II》(1993) | 两卷本，理论+算法双链，法式严谨 + 工程接口，bundle 法原典 | 高（理论+算法兼具） | 想把凸分析与优化器实现打通的应用数学家/工程师 |
| **Rockafellar**《Convex Analysis》(1970) | 有限维经典，代数几何风味，epigraph-共轭公理化，纯理论无应用 | 极高（公认源头经典） | 想掌握凸分析标准语言原典的数学系学生 |
| **Borwein & Lewis**《Convex Analysis & Nonlinear Optimization》(2000) | 泛函分析/弱拓扑，Fenchel 共轭无穷维严格化，Clarke 次微分 | 极高（分析味浓） | 攻读变分/最优控制/非光滑分析的数学专业读者 |
| **Bertsekas**《Convex Optimization Theory》(2009) | 几何驱动，对偶为中心，图示+严格定义交替，工程可读 | 高（证明完整） | 想从几何直觉走到严格对偶的工程师/研究者 |

---

## §1 全书 10 章骨架一览（飞腾锚点分布）

| 章 | 标题（英文 / 中文） | 归属 | 核心概念 | 飞腾锚点 |
|:-:|------|:-:|---------|---------|
| 1 | Convex Sets / 凸集 | Vol I | 分离定理、Carathéodory、投影、Minkowski | FP16 3.81×（有限表示） |
| 2 | Convex Functions / 凸函数 | Vol I | epigraph、连续性、方向导数 | UDOT 16.9×（sup 累积） |
| 3 | Subdifferentiability of Finite Convex Functions / 有限凸函数次可微 | Vol I | 次微分 ∂f、方向导数对偶、Fermat | Iron Law <2%（误差带） |
| 4 | The Conjugate Convex Function / 共轭凸函数 | Vol I | Fenchel 共轭、Fenchel-Young、Moreau 分解 | matmul 15×（对偶基变换） |
| 5 | Minimization Algorithms for Differentiable Functions / 可微函数极小化 | Vol I | 线搜索、Wolfe 条件、最速下降、Newton | 分支预测（路径选择） |
| 6 | Nonsmooth Optimization: Subgradient Methods / 非光滑优化：次梯度法 | Vol II | 次梯度迭代、Polyak 步长、O(1/√k) | TLB 4.81×（稀疏访问） |
| 7 | Conjugate Gradient Methods / 共轭梯度法 | Vol II | Krylov 子空间、A-共轭、FR/PR | Schmidt 正交化（加权正交） |
| 8 | Quasi-Newton Methods / 拟 Newton 法 | Vol II | 割线方程、BFGS、DFP、超线性收敛 | GEMM 9.45G（Hessian 运算） |
| 9 | Trust-Region Methods / 信赖域法 | Vol II | 信赖域子问题、Cauchy 点、全局收敛 | FP16 3.81×（数值缩放·复用） |
| 10 | Computing the Subdifferential / 次微分计算 | Vol II | 和/链/max 规则、法锥、范数次微分 | UDOT 16.9×（批量枚举·复用） |

> **读法建议**：理论轴 **Ch1–Ch4 必读**（与 Rockafellar 同级，是算法轴的合法性来源）；
> 算法轴 **Ch5–Ch9** 是优化器的内部机理（Ch5 线搜索是一切算法的共享底座）；
> **Ch6 + Ch10** 是非光滑优化的核心，直接对应 L1 正则化与 Adam；
> 若只读三章，选 **Ch4（共轭/Moreau）+ Ch5（Wolfe 线搜索）+ Ch8（BFGS）**——这三者覆盖了深度学习优化器 90% 的数学。

---

### 第 1 章 · Convex Sets（凸集）· Vol I

- **核心**：本章建立凸集的几何字母表。凸组合 $\sum\lambda_i x_i$（$\lambda_i\ge0,\sum\lambda_i=1$）给出构造凸集的代数工具，
  **Carathéodory 定理**把「无穷组合」压缩到 $n+1$ 个点——这是有限维凸性能用线性代数处理的根本原因。
  **分离定理**（Hahn-Banach 在 $\mathbb{R}^n$ 的化身）说：不相交的凸集可用超平面分开，
  其推论**支撑超平面**给出每个边界点处的「切平面」。
  HUL 比 Rockafellar 更早强调**投影定理**（Minkowski）：
  到闭凸集 $C$ 的最近点 $P_C(x)$ 存在且唯一，且 $(x-P_C(x))\in N_C(P_C(x))$（法锥）——
  这是全书第一个存在性定理，也是 Ch4 Moreau 分解的几何源头。
- **飞腾锚点**：🟢 **FP16 3.81×[L01] → Carathéodory 的有限表示**。
  计算机无法精确存「无穷点的平均」，但 Carathéodory 保证只需 $n+1$ 个顶点的线性组合即可精确命中凸包内任一点，
  正如 FP16 用 3.81× 吞吐换取有限的有效位数——**有限性是凸集可计算的基石**。
- **关键定理**：**Carathéodory 定理**：$x\in\operatorname{conv}(S)\subseteq\mathbb{R}^n$ $\Rightarrow$
  $\exists x_1,\dots,x_{n+1}\in S,\ \lambda_i\ge0,\sum\lambda_i=1$ 使 $x=\sum\lambda_i x_i$。
  **投影定理**：$C$ 闭凸、$x\notin C$，则 $P_C(x)=\arg\min_{y\in C}\|y-x\|$ 存在唯一，且 $x-P_C(x)\in N_C(P_C(x))$。
- **自测**：设 $C$ 为单位圆盘、$x=(2,0)$。求 $P_C(x)$，验证 $(x-P_C(x))$ 与 $P_C(x)$ 处的法向量同向。
  再问：$P_C(x)$ 在 $C$ 边界，支撑超平面法向量是什么？

---

### 第 2 章 · Convex Functions（凸函数）· Vol I

- **核心**：HUL 的天才一笔与 Rockafellar 一致：**用凸集定义凸函数**——
  $f$ 凸 $\iff$ epigraph $\operatorname{epi}f=\{(x,\alpha):f(x)\le\alpha\}$ 凸。
  但 HUL 更强调**分析性质**：凸函数有一个惊人事实——
  它在有效域内部**自动连续**且**局部 Lipschitz**（无需任何额外假设），
  这是凸函数独有的「拓扑福利」，光滑函数反而要逐条验证。
  **方向导数** $f'(x;d)=\lim_{t\downarrow0}\frac{f(x+td)-f(x)}{t}$ 对凸函数**处处存在**（单侧），
  这为 Ch3 的次微分铺设桥梁：方向导数是次微分的支撑函数。
- **飞腾锚点**：🟢 **UDOT 16.9×[E05] → epigraph 的 sup 累积**。
  epigraph 判定 $f(x)\le\alpha$ 与方向导数比值的计算本质是无符号点积累加（dot product），
  UDOT 16.9× 正是这类 sup / 求和运算在硬件上的加速比——
  凸函数的连续性定理保证这些数值运算「不会爆炸」，是稳定的批量求和基础。
- **关键定理**：**凸函数连续性**：$f$ 凸真函数、$\operatorname{int}(\operatorname{dom}f)\neq\varnothing$，
  则 $f$ 在 $\operatorname{int}(\operatorname{dom}f)$ 上连续且局部 Lipschitz。
  **方向导数存在**：凸函数 $f$ 在 $\operatorname{int}(\operatorname{dom}f)$ 处单侧方向导数 $f'(x;d)$ 对一切 $d$ 存在。
- **自测**：证明 $f(x)=|x|$ 在 $\mathbb{R}$ 上连续且局部 Lipschitz。
  求方向导数 $f'(0;d)$（分 $d>0$、$d<0$、$d=0$ 讨论）。

---

### 第 3 章 · Subdifferentiability of Finite Convex Functions（有限凸函数次可微）· Vol I

- **核心**：梯度要求可微，而优化核心函数常不可微（$|x|$、$\max$、指示函数）。
  **次微分**推广梯度：
  $$\partial f(x)=\{u:\ f(y)\ge f(x)+\langle u,y-x\rangle,\ \forall y\}.$$
  对凸函数，它在 $\operatorname{int}(\operatorname{dom}f)$ 处**非空、紧凸**。
  次微分与方向导数的对偶是全章钥匙：
  $f'(x;d)=\sup_{u\in\partial f(x)}\langle u,d\rangle$（次微分作为方向导数的支撑函数）。
  由此立即推出**Fermat 法则**：$x^*$ 极小 $\iff 0\in\partial f(x^*)$——
  非光滑最优性条件，推广 $f'(x)=0$。
- **飞腾锚点**：🟢 **Iron Law <2%⭐[Lab00] → 次梯度即「可接受斜率范围」**。
  次微分不是一个斜率，而是一个**误差带 / 子梯度集合**（对 $|x|$ 在 $0$ 是 $[-1,1]$），
  优化器只要落在带内即可保证下降——
  正如性能铁律「误差 <2% 是可接受边界」：次梯度的鲁棒性来自它是一个**范围**而非一个点，
  这解释了次梯度法为何在非光滑世界仍能收敛（虽慢）。
- **关键定理**：**方向导数-次微分对偶**：
  $f'(x;d)=\sup_{u\in\partial f(x)}\langle u,d\rangle$（$d\mapsto f'(x;d)$ 是 $\partial f(x)$ 的支撑函数）。
  **Fermat 法则**：$x^*$ 是凸函数 $f$ 的极小点 $\iff 0\in\partial f(x^*)$。
- **自测**：求 $f(x)=|x|$ 在 $0$ 的 $\partial f(0)$。
  用方向导数公式验证 $f'(0;d)=\sup_{u\in[-1,1]}\langle u,d\rangle=|d|$。

---

### 第 4 章 · The Conjugate Convex Function（共轭凸函数：Fenchel）· Vol I ⭐ 全书灵魂

- **核心**：本章是全书的**理论高潮**，也是后续近端 / bundle 算法的合法性来源。
  **Fenchel 共轭** $f^*(s)=\sup_x\{\langle s,x\rangle-f(x)\}$ 是函数的「对偶函数」，
  $f^*$ 永远是闭凸函数（即使 $f$ 不凸）。
  **Fenchel-Young 不等式** $f(x)+f^*(s)\ge\langle s,x\rangle$ 是凸分析的中心不等式，
  等号条件 $f(x)+f^*(s)=\langle s,x\rangle\iff s\in\partial f(x)$ 把共轭与次微分焊死。
  **双共轭定理**（Fenchel-Moreau）：闭真凸函数 $f^{**}=f$（自对偶）。
  HUL 在此章系统引入 **Moreau 分解** $x=\operatorname{prox}_f(x)+\operatorname{prox}_{f^*}(x)$——
  把近端算子与共轭对称配对，这是近端梯度法（ISTA/FISTA）的全部优雅所在。
- **飞腾锚点**：🟡 **matmul 15×[V03] → 共轭 = 函数空间的对偶基变换**。
  共轭 $f^*(s)=\sup_x\{\langle s,x\rangle-f(x)\}$ 把「原空间 $x$」经线性泛函 $\langle s,\cdot\rangle$ 映到「对偶空间 $s$」，
  类似矩阵乘法把向量从一组基变到另一组基（15× 加速）——
  近端算子每步涉及 $f$ 与 $f^*$ 的交替计算，共轭是函数空间的「对偶基变换」。
- **关键定理**：**Fenchel-Young 不等式**：$\forall x,s$，$f(x)+f^*(s)\ge\langle s,x\rangle$，
  等号 $\iff s\in\partial f(x)$。
  **Fenchel-Moreau 双共轭**：$f$ 闭真凸 $\Rightarrow f^{**}=f$。
  **Moreau 分解**：Hilbert 空间中，$x=\operatorname{prox}_f(x)+\operatorname{prox}_{f^*}(x)$，
  其中 $\operatorname{prox}_f(x)=\arg\min_u\{f(u)+\tfrac12\|u-x\|^2\}$。
- **自测**：求 $f(x)=\tfrac12\|x\|^2$ 的共轭 $f^*(s)$ 与 $\operatorname{prox}_f(x)$。
  验证 Moreau 分解 $x=\operatorname{prox}_f(x)+\operatorname{prox}_{f^*}(x)$ 成立（提示：此时 $f=f^*$，prox 各占一半）。

---

### 第 5 章 · Minimization Algorithms for Differentiable Functions（可微函数极小化算法）· Vol I

- **核心**：本章是一切优化算法的**共享底座**——线搜索框架。
  标准迭代 $x_{k+1}=x_k-\alpha_k d_k$，其中 $d_k$ 是方向、$\alpha_k$ 是步长。
  HUL 系统讲授**Wolfe 条件**：充分下降（$f(x_k+\alpha d)\le f(x_k)+c_1\alpha\nabla f^Td$）
  + 曲率条件（$\nabla f(x_k+\alpha d)^Td\ge c_2\nabla f(x_k)^Td$），
  两者合在一起既保证每步下降、又防止步长过小，是几乎所有现代线搜索的工业标准。
  **最速下降** $d_k=-\nabla f_k$ 线性收敛（凸 $L$-光滑下 $f(x_k)-f^*\le(1-\mu/L)^k\cdots$）；
  **Newton** $d_k=-[\nabla^2 f_k]^{-1}\nabla f_k$ 在极小点附近**二次收敛**。
- **飞腾锚点**：🟡 **分支预测 0.71 vs 3.14[Lab02] → 线搜索的方向/步长决策**。
  线搜索每步要做「沿这个方向走多远」的判定，本质是条件分支——
  Wolfe 曲率条件判对（步长可接受）时 0.71 cycles（轨迹稳定），
  判错（回溯 backtrack）时 3.14 cycles（反复试探）。
  这是为何回溯线搜索（backtracking）的分支模式高度可预测，而精确线搜索在病态问题上反复回溯代价高昂。
- **关键定理**：**Wolfe 条件**：$0<c_1<c_2<1$，步长 $\alpha$ 满足
  $f(x_k+\alpha d_k)\le f(x_k)+c_1\alpha\nabla f_k^Td_k$ 且 $|\nabla f(x_k+\alpha d_k)^Td_k|\le c_2|\nabla f_k^Td_k|$。
  **最速下降收敛**：$f$ 凸 $L$-光滑、$\mu$-强凸 $\Rightarrow$ 线性收敛，速率 $(1-\mu/L)$。
  **Newton 局部收敛**：$\nabla^2 f^*$ 正定且 Lipschitz $\Rightarrow\|x_{k+1}-x^*\|=O(\|x_k-x^*\|^2)$（二次）。
- **自测**：写出 Wolfe 条件两式，解释为何「曲率条件」必要（没有它会怎样）。
  对 $f(x)=\tfrac12 x^2$，最速下降以固定步长 $\alpha=1$ 走一步是否满足充分下降？

---

### 第 6 章 · Nonsmooth Optimization: Subgradient Methods（非光滑优化：次梯度法）· Vol II

- **核心**：当 $f$ 不可微（如 $f(x)=\|x\|_1$），梯度不存在，但**次梯度存在**。
  **次梯度法** $x_{k+1}=x_k-t_k g_k$，$g_k\in\partial f(x_k)$。
  关键反直觉事实：**$f(x_k)$ 不是单调下降的**！
  次梯度 $g_k$ 只保证它是 $x_k$ 处的支撑斜率，不保证指向全局下降方向。
  收敛完全依赖步长选择：**递减步长** $t_k\to0$ 且 $\sum t_k=\infty,\ \sum t_k^2<\infty$；
  **Polyak 步长** $t_k=\frac{f(x_k)-f^*}{\|g_k\|^2}$（需知最优值 $f^*$ 或其估计）。
  收敛速率仅 $O(1/\sqrt{k})$——比光滑的线性收敛慢得多，这是非光滑优化的**本质代价**。
- **飞腾锚点**：🟡 **TLB 4.81×[E04] → 稀疏次梯度的内存访问**。
  L1 正则化的次梯度 $g\in\partial\|x\|_1$ 在零分量处任意取 $[-1,1]$，
  产生**稀疏解**——大部分分量为零，内存中跳跃访问，TLB 失配惩罚 4.81×。
  次梯度法的瓶颈不是算术而是**稀疏访问模式**：TLB 友好的数据布局（CSR 稀疏存储）
  使大规模次梯度迭代不被内存延迟拖垮——这正是 Lasso 训练的工程核心。
- **关键定理**：**次梯度法收敛**：$\sum t_k=\infty$、$\sum t_k^2<\infty$ $\Rightarrow x_k\to x^*$（a.s. 或确定性地 $f(x_k)\to f^*$）。
  **Polyak 步长**：$t_k=\frac{f(x_k)-f^*}{\|g_k\|^2}$ $\Rightarrow f(x_k)-f^*=O(1/\sqrt{k})$。
- **自测**：用次梯度法极小化 $f(x)=\|x\|_1$（$x\in\mathbb{R}^n$），取 $t_k=1/\sqrt{k}$。
  写出每步更新（零分量处 $g_k$ 如何选），预期 $f(x_k)-0$ 的收敛速率量级。

---

### 第 7 章 · Conjugate Gradient Methods（共轭梯度法）· Vol II

- **核心**：**共轭梯度（CG）**是解大对称正定（spd）线性系统 $Ax=b$ 的最优迭代法。
  核心思想：在 **Krylov 子空间** $\mathcal{K}_k=\operatorname{span}\{b,Ab,\dots,A^{k-1}b\}$ 内逐步极小化 $\tfrac12 x^TAx-b^Tx$。
  关键概念是 **A-共轭**（$\langle p_i,Ap_j\rangle=0$，$i\neq j$）——
  这是标准正交在「$A$-加权内积」下的推广，每步用类似 Gram-Schmidt 的方式构造新方向。
  CG 的惊人性质：**$n$ 步精确收敛**（无舍入误差时）。
  对非线性问题，**Fletcher-Reeves / Polak-Ribière** 把 CG 推广为通用非线性优化器（需配线搜索）。
- **飞腾锚点**：🟡 **Schmidt 正交化 → A-共轭 = 加权正交**。
  CG 的「A-共轭」本质是 Gram-Schmidt 正交化在 $A$-内积 $\langle u,v\rangle_A=u^TAv$ 下的版本——
  每步把新方向对已有方向做 $A$-加权正交化（共轭化）。
  正如 Schmidt 正交化给出最优逼近（投影），CG 的共轭化给出 Krylov 子空间内的最优逼近——
  CG 的「$n$ 步收敛」与 Gram-Schmidt「$n$ 步得正交基」同构。
- **关键定理**：**CG 谱收敛界**：$A$ spd、$\kappa=\lambda_{\max}/\lambda_{\min}$，
  $$\|x_k-x^*\|_A\le 2\Big(\frac{\sqrt\kappa-1}{\sqrt\kappa+1}\Big)^k\|x_0-x^*\|_A.$$
  **$n$ 步终止**：精确算术下 $\mathcal{K}_n=\mathbb{R}^n$，故 $x_n=x^*$。
- **自测**：对 $A=\operatorname{diag}(1,100)$、$b=(1,1)$，从 $x_0=(0,0)$ 跑 2 步 CG。
  验证第 2 步 $x_2=x^*=A^{-1}b$（精确收敛），并解释为何 $\kappa=100$ 时第 1 步误差仍大。

---

### 第 8 章 · Quasi-Newton Methods（拟 Newton 法：BFGS、DFP）· Vol II

- **核心**：Newton 法要算 Hessian $\nabla^2 f$（昂贵且可能非正定），**拟 Newton** 用低秩更新构造 Hessian 的近似。
  理论锚点是**割线方程** $B_{k+1}s_k=y_k$，其中 $s_k=x_{k+1}-x_k$、$y_k=\nabla f_{k+1}-\nabla f_k$——
  要求近似 Hessian $B_{k+1}$ 沿 $s_k$ 方向的曲率与真实梯差一致。
  在「满足割线方程 + 秩最小（最保守）」准则下得到两个经典**秩-2 更新**：
  **DFP**（Davidon-Fletcher-Powell）更新逆 $H=B^{-1}$；
  **BFGS**（Broyden-Fletcher-Goldfarb-Shanno）更新 $H$ 本身——
  BFGS 数值更鲁棒，是实际首选。配 Wolfe 线搜索，BFGS 全局收敛且**超线性收敛**（快于线性、略慢于二次）。
- **飞腾锚点**：🟢 **GEMM 9.45G⭐[Lab05] → Hessian 近似的矩阵运算**。
  BFGS 每步涉及矩阵-向量积 $H_k g_k$（求方向）和秩-2 外积更新 $s_k s_k^T/(s_k^Ty_k)$。
  大规模拟 Newton 的核心是稠密矩阵吞吐——GEMM 单元 9.45 GFLOPS 使万维 BFGS 在工程中可行。
  这正是 `scipy.optimize.minimize(method='BFGS')` 与 `torch.optim.LBFGS` 的计算内核：
  LBFGS（有限内存 BFGS）通过只存最近 $m$ 对 $(s,y)$ 避免存 $n\times n$ 矩阵，本质是用 GEMM 友好的结构换取内存。
- **关键定理**：**BFGS 更新公式**（更新逆 Hessian 近似 $H\approx[\nabla^2 f]^{-1}$）：
  $$H_{k+1}=H_k+\frac{1+y_k^T H_k y_k/(s_k^T y_k)}{s_k^T y_k}s_k s_k^T-\frac{H_k y_k s_k^T+s_k y_k^T H_k}{s_k^T y_k}.$$
  **超线性收敛**：$f$ 二次连续可微、$\nabla^2 f^*$ 正定、Wolfe 线搜索 $\Rightarrow\lim_{k\to\infty}\frac{\|x_{k+1}-x^*\|}{\|x_k-x^*\|}=0$。
- **自测**：写出 BFGS 的割线方程 $B_{k+1}s_k=y_k$。
  解释 Wolfe 曲率条件为何保证 $s_k^T y_k>0$（这是 BFGS 更新分母为正、数值稳定的来源），
  以及为何 DFP 在这个性质上不如 BFGS 鲁棒。

---

### 第 9 章 · Trust-Region Methods（信赖域法）· Vol II

- **核心**：信赖域是**线搜索的对偶策略**。
  线搜索先定方向再找步长；信赖域先定「这一步信任模型多大范围」（半径 $\Delta_k$），
  在信赖域 $\|d\|\le\Delta_k$ 内解**二次模型子问题** $\min m_k(d)=f_k+g_k^Td+\tfrac12 d^TB_kd$。
  根据实际下降与预测下降之比 $\rho_k$ 更新半径：$\rho$ 接近 1（模型准）则扩大 $\Delta$，
  $\rho$ 小（模型差）则缩小 $\Delta$。
  关键是 **Cauchy 点**（沿最速下降方向在域内的极小）保证每步**至少不差于最速下降**，
  这是全局收敛的基石。信赖域比线搜索**更鲁棒**——能处理 Hessian 非正定、负曲率方向，
  这是为何解困难非线性问题（如深度学习二阶方法 KFAC/BFGS）时常信赖域优于线搜索。
- **飞腾锚点**：🟡 **FP16 3.81×[L01]（复用·不同角度）→ 信赖域半径的数值缩放**。
  信赖域半径 $\Delta_k$ 的动态调整本质是**数值尺度控制**——模型只在局部可信，超出范围要用低精度快速试探。
  FP16 的 3.81× 吞吐适合信赖域子问题的大批量试探（多个候选 $d$ 并行评估），
  而 $\rho_k$ 的判定需要更高精度（FP32/FP64）——这是混合精度优化的天然场景：
  探测用 FP16，确认用 FP32，正如信赖域「先粗后细」的哲学。
- **关键定理**：**信赖域全局收敛**：若每步取 Cauchy 点（或保证至少 Cauchy 下降），
  则 $\liminf_{k\to\infty}\|g_k\|=0$（收敛到稳定点）。若再假设 $\{x_k\}$ 有界，则 $\lim_{k\to\infty}\|g_k\|=0$。
- **自测**：对 Rosenbrock 函数 $f(x,y)=(1-x)^2+100(y-x^2)^2$，
  比较线搜索 Newton（初始 Hessian 可能非正定导致方向上升）与信赖域 Newton（限制步长不离开可信区）的鲁棒性。
  指出信赖域在何处「挽救」了 Newton。

---

### 第 10 章 · Computing the Subdifferential（次微分计算）· Vol II

- **核心**：Ch3 给了次微分的**定义**，本章给次微分的**计算规则**——把非光滑理论变成可算的工具箱。
  核心规则：
  - **和规则** $\partial(f+g)(x)\supseteq\partial f(x)+\partial g(x)$（正则条件下取等）；
  - **链式法则** $\partial(g\circ A)(x)\supseteq A^*\partial g(Ax)$；
  - **max 规则** $\partial(\max_i f_i)(x)=\operatorname{conv}\bigcup_{i\in I(x)}\partial f_i(x)$（$I(x)$ 为有效指标集）；
  - **指示函数** $\partial\delta_C(x)=N_C(x)$（法锥），把约束优化翻译成无约束；
  - **范数** $\partial\|\cdot\|(0)=\{u:\|u\|_*\le1\}$（对偶单位球）。
  这些规则是 Ch6 次梯度法、近端算法、bundle 法的**计算弹药**——
  算法每步都要具体算出一个次梯度，规则告诉你怎么算。
- **飞腾锚点**：🟢 **UDOT 16.9×[E05]（复用·不同角度）→ max 函数次微分的批量枚举**。
  max 规则 $\partial(\max_i f_i)=\operatorname{conv}\bigcup\partial f_i$ 需要对所有分量算梯度再取凸包，
  本质是批量点积 + 取 max——UDOT 的主战场。
  对 $\max(x_1,\dots,x_n)$，需对 $n$ 个分量各算一次内积再判有效集 $I(x)$，
  16.9× 吞吐使大规模 max-out 网络（如 ReLU、max-pooling）的次微分反向传播在工程中可行。
- **关键定理**：**次微分和规则**：$\operatorname{ri}(\operatorname{dom}f)\cap\operatorname{ri}(\operatorname{dom}g)\neq\varnothing$ 时
  $\partial(f+g)(x)=\partial f(x)+\partial g(x)$。
  **指示函数→法锥**：$\partial\delta_C(x)=N_C(x)=\{u:\langle u,y-x\rangle\le0,\ \forall y\in C\}$。
  **范数次微分**：$\partial\|x\|=\{u:\|u\|_*\le1\}$（$x=0$），$\partial\|x\|=\{x/\|x\|\}$（$x\neq0$）。
- **自测**：求 $f(x)=\max(x_1,\dots,x_n)$ 在 $x=(1,1,\dots,1)$（全分量相等）的 $\partial f(x)$。
  再求 $\delta_{[0,1]^n}$ 的次微分（即方体 $[0,1]^n$ 的法锥），指出边界点与内点的区别。

---

## §9 全书思想主线（约 200 字）

HUL 的主线是「**有限维凸分析的严格理论，直接长出可实现的极小化算法**」：
- **Ch1–Ch4 理论轴**（Vol I）：凸集（分离/投影）→ 凸函数（连续/方向导数）→ 次微分（Fermat）→ 共轭（Fenchel-Young/Moreau）。
  这条轴与 Rockafellar 同级严谨，但 HUL 始终为算法埋伏笔——投影定理长出 Moreau 分解，次微分长出次梯度法。
- **Ch5–Ch9 算法轴**：线搜索（Wolfe）是一切算法的底座，可微世界用最速下降/Newton/CG/BFGS（线性→二次→超线性收敛），
  非光滑世界用次梯度（$O(1/\sqrt{k})$），信赖域作为鲁棒统一器兜底。
- **Ch6 + Ch10** 是 Lemaréchal 的真正遗产：非光滑凸优化的完整工具链——次梯度法是入门，bundle 法（Vol II 进阶）是工业标准。

与已读教材呼应：本书 = Rockafellar 的理论 + nocedal_wright 的算法，合二为一。
Rockafellar 只讲「为什么」，HUL 讲「为什么 + 怎么算」；
Nesterov 讲「复杂度下界」，HUL 讲「实现细节」；
Borwein-Lewis 讲「无穷维严格性」，HUL 讲「有限维可用性」。
**HUL 是凸优化三角中唯一贯通理论与代码的那一极。**

---

## §10 与本仓库其他笔记的交叉引用

**与凸分析/优化三角的对照**：
- **`rockafellar_凸分析`**（刚做，348 行）：HUL 的 Ch1–Ch4 与 Rockafellar 同级严谨。
  对照读法——Rockafellar Ch3 分离 = HUL Ch1；Rockafellar Ch7 共轭 = HUL Ch4；
  但 HUL 多了投影定理→Moreau 分解的工程伏笔，Rockafellar 纯理论无此接口。
- **`borwein_lewis_凸分析与非线性优化`**（刚做，536 行）：Borwein-Lewis 把 HUL 的有限维定理「提升」到 Banach 空间。
  对照读法——HUL Ch3 次微分（有限维）→ Borwein-Lewis Ch4 Clarke/proximal/limiting（无穷维三层）；
  HUL 算法只在有限维有效，Borwein-Lewis 给出无穷维中算法成立的前提。
- **`bertsekas_凸优化理论`**（已读，398 行）：Bertsekas 聚焦对偶，HUL 聚焦算法。
  对照读法——Bertsekas Ch4 Lagrange 对偶是 HUL 缺席的对偶深度，HUL Ch5–Ch9 是 Bertsekas 缺席的算法实现。
- **`nesterov_凸优化算法引论`**（已读，332 行）：Nesterov 讲 $O(1/k^2)$ 复杂度下界，HUL 讲实现细节。
  两者互补：Nesterov 是「算法天花板」，HUL 是「算法工程学」。
- **`nocedal_wright_数值优化`**（已读）：N&W 是现代数值优化的标准教材，HUL（1993）是其欧洲先驱。
  N&W 的 CG（Ch5）、BFGS（Ch6）、信赖域（Ch4）可直接对照 HUL Ch7/Ch8/Ch9 的原典推导。

**AI / 工程锚点（数学落到工程）**：
- 🟢 **`torch.optim.LBFGS`**（PyTorch）：有限内存 BFGS 的实现，对应 Ch8 BFGS 更新公式 + Wolfe 线搜索。
  读完 Ch8，你看 LBFGS 不再是黑箱——它的 `max_iter`、`history_size` 参数直接对应割线对的存储数 $m$。
- 🟢 **`torch.optim.Adam` vs 次梯度法**：Adam 的对角预条件 = 自适应步长次梯度法（Ch6）。
  Adam 的「动量 + 自适应步长」本质是 Polyak 步长的工程启发式版本——
  Ch6 的 $O(1/\sqrt{k})$ 速率解释了为何 Adam 在非光滑损失（如带 L1 的训练）上仍能收敛。
- 🟢 **ReLU / max-out 的反向传播**：ReLU 的次微分 $\partial\max(0,x)$ 在 $x=0$ 是 $[0,1]$，
  反向传播取 $1$（次梯度的一种选择）——对应 Ch10 max 规则。
  理解次微分才能理解为何 ReLU 的「0 处梯度取 0」是合法的次梯度选择。
- 🟢 **Lasso / 近端梯度（ISTA/FISTA）**：L1 正则化的近端算子 = 软阈值，
  理论合法性来自 Ch4 Moreau 分解 + Ch10 范数次微分。
  `sklearn.linear_model.Lasso` 内部就是近端梯度法，每步的软阈值即 $\operatorname{prox}_{\lambda\|\cdot\|_1}$。
- 🟡 **二阶深度学习（KFAC / Shampoo）**：近似 Fisher 矩阵的拟 Newton 变体，
  数值稳定性依赖信赖域思想（Ch9）——当 Fisher 近似不正定时，信赖域比线搜索更鲁棒。

---

> **下一步**：沿 01-track/stage-1 精读做题；遇优化概念查 04-concepts 跑三维交叉。
> 本笔记定位为 stage-3 优化方向的「理论算法双链」核心教材。
> 建议配合已读 **rockafellar_凸分析**（公理源头）+ **borwein_lewis**（无穷维严格化）+ **bertsekas**（几何对偶）
> 形成凸分析三角：HUL 补上「理论如何变成可跑的优化器」这一极，
> 与三者的「公理—分析—几何」共同构成凸优化方向的完整光谱。
> 算法轴再接 **nesterov**（复杂度下界）与 **nocedal_wright**（现代实现），五者闭环。
