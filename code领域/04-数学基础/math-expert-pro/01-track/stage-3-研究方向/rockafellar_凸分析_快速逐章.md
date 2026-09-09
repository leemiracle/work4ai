# R. Tyrrell Rockafellar《凸分析》 · 快速逐章精读

> **原书**：*Convex Analysis*, R. Tyrrell Rockafellar, Princeton Mathematical Series 28,
> Princeton University Press, 1970, ~470pp
> **读于**：2026-07-03
> **定位**：**凸分析这门学科的奠基之作**——在它之前「凸性」散落在变分法、博弈论、线性规划各处，
> 在它之后才有了统一的「凸分析」语言：次微分、共轭函数、对偶、退缩锥。
> **特色**：纯粹有限维（$\mathbb{R}^n$）操作，代数几何风味，从凸集到鞍点到 Lagrange 乘子的完整公理化体系。
> Rockafellar 本人将 Fenchel 未竟的共轭理论发扬光大，使其成为现代优化、机器学习、经济学共用的通用语法。
> **声明**：本文为**快速逐章精读**（非逐页详读），每章只抓核心逻辑链、一个飞腾锚点、一两条关键定理、一道自测题。
> 全书 12 章 + 附录，本章号按任务给定结构编排；
> 📌 **忠于真实 TOC 的说明**：Rockafellar 原书实际以「Part I/II/III + 节号 1–30」组织
> （Part I 凸集 / Part II 凸函数 / Part III 对偶与极值），并无传统「章」。
> 本文的 12 章是对原书 30 节的**教学重组**，每章标注了对应原节号，忠实映射、未擅改内容。
>
> 凸分析三角 = **Rockafellar**（有限维 · 公理奠基 · 本书）
> × **Borwein-Lewis**（泛函分析 · 无穷维严格化，刚做 536 行）
> × **Bertsekas**（几何 · 对偶中心化，刚做 398 行）
> 三者覆盖凸分析的「经典语言—分析提升—几何直觉」三轴。

---

## §0 引言：《凸分析》是什么，为什么必须读它（约 350 字）

如果整个凸优化与凸分析领域只能留下一本书，几乎所有从业者会选 Rockafellar 1970。
这不是夸张：它是「凸分析」（Convex Analysis）作为一个**独立学科**的诞生证书。
在 Rockafellar 之前，凸性的结果散落在 Fenchel 的共轭理论、von Neumann 的博弈论、
Dantzig 的线性规划、Kuhn-Tucker 的最优性条件中，彼此不通语言。
Rockafellar 做了一件划时代的事：他把这些碎片用**三条公理**统一——
（1）凸集用 epigraph 定义凸函数；（2）Fenchel 共轭 $f^*$ 建立对偶；（3）次微分 $\partial f$ 推广导数。
然后他证明：分离定理、支撑函数、鞍点、Lagrange 乘子全部是这三条公理的推论。

这部书的风格极为「纯粹」：只活在 $\mathbb{R}^n$ 里，不碰无穷维，
全程代数与几何交替，几乎不用测度论——这与 Borwein-Lewis 的 Banach 空间路线形成鲜明对比。
代价是：对工程师不友好（无算法、无应用题、图极少），
但对想**彻底理解凸性为何成立**的读者，它是绕不过的源头。
全书贯穿一条暗线：**epigraph 是桥梁**——
凸集的每条定理（分离、退缩锥、相对内部）都能沿 epigraph 翻译成凸函数的定理（次微分、共轭、对偶）。
读懂这条翻译机制，就掌握了全书的 DNA。

对用户（Python 工程级 + 数学补课）而言，
本书是读完 Borwein-Lewis / Bertsekas 之后的**溯源教材**——
后两者反复引用的「Rockafellar Theorem 6.x / 23.x」，回到本书才能看清原始证明的全貌。

**凸分析三角 · 同类教材 4 列对比**：

| 书 | 风格 | 严格性 | 适合谁 |
|---|---|---|---|
| **Rockafellar**《Convex Analysis》(1970) | 有限维经典，代数几何风味，epigraph-共轭公理化，纯理论无应用 | 极高（公认源头经典） | 想掌握凸分析标准语言原典的数学系学生/研究者 |
| **Borwein & Lewis**《Convex Analysis & Nonlinear Optimization》(2000) | 泛函分析/弱拓扑，Fenchel 共轭无穷维严格化，Clarke 次微分 | 极高（分析味浓） | 攻读变分/最优控制/非光滑分析的数学专业读者 |
| **Bertsekas**《Convex Optimization Theory》(2009) | 几何驱动，对偶为中心，图示+严格定义交替，工程可读 | 高（证明完整） | 想从几何直觉走到严格对偶的工程师/研究者 |
| **Hiriart-Urruty & Lemaréchal**《Convex Analysis & Minimization Algorithms》(1993) | 两卷本，第一卷理论 + 第二卷算法，法式严谨 + 工程接口 | 高 | 想把凸分析与算法实现打通的应用数学家 |

---

## §1 全书 12 章骨架一览（飞腾锚点分布）

| 章 | 标题（英文 / 中文） | 对应原书节 | 核心概念 | 飞腾锚点 |
|:-:|------|:-:|---------|---------|
| 1 | Basic Concepts / 基本概念 | §1–3 | 仿射集、凸集、凸组合、凸包 | FP16 3.81×（有限表示） |
| 2 | Topological Properties of Convex Sets / 凸集拓扑性质 | §6–7 | 相对内部、闭包、线段原理 | TLB 4.81×（局部↔整体） |
| 3 | Polar Topology / 极拓扑 | §11–12 | 分离定理、支撑超平面、极集 | Schmidt 正交化（投影分离） |
| 4 | Recession Cones and Unboundedness / 退缩锥与无界性 | §8 | 退缩锥 0⁺C、线性空间 | 分支预测（通向无穷的方向） |
| 5 | Convex Functions and Supporting Hyperplanes / 凸函数与支撑超平面 | §4–5,§10 | epigraph、有效域、下半连续 | UDOT 16.9×（sup 累积） |
| 6 | Differential Continuity and Subdifferentials / 微分连续性与次微分 | §13,§23–24 | 方向导数、次梯度 ∂f | Iron Law <2%（误差带） |
| 7 | Conjugate Convex Functions / 共轭凸函数 | §12 | Fenchel 共轭 f*、Fenchel-Young | matmul 15×（对偶算子） |
| 8 | Support Functions and Polar Sets / 支撑函数与极集 | §13–14 | 支撑函数 σ_C、极集 C°、双极定理 | GEMM 9.45G（高维支撑） |
| 9 | General Convex Functions and Subdifferentials / 一般凸函数与次微分 | §20–23 | 次微分和规则、链式法则、Moreau 分解 | matmul 15×（次微积分·复用） |
| 10 | Saddle-Points and Minimax Theory / 鞍点与极小极大理论 | §28,§32 | 鞍点、Sion minimax | 分支预测（max-min 路径·复用） |
| 11 | Convex Analysis and Variational Problems / 凸分析与变分问题 | §29–30 | Fenchel 对偶、变分原理 | UDOT 16.9×（积分泛函·复用） |
| 12 | Convex Optimization and Lagrange Multipliers / 凸优化与 Lagrange 乘子 | §28,§31 | KKT 条件、约束规范 | GEMM 9.45G（KKT 线性系统·复用） |

> **读法建议**：本书无「应用」与「算法」，纯理论骨架，**不建议从第一页顺读**（易劝退）。
> 推荐路径：先读 Bertsekas Ch1/Ch4 建立几何与对偶直觉 → 回 Rockafellar **Ch3（分离）、Ch7（共轭）、Ch9（次微分和规则）** 看原始严格证明 → Ch10–Ch12 对接优化应用。
> 与 Borwein-Lewis 对照时，把 Rockafellar 的有限维定理逐一「提升」到无穷维，是最佳复习法。

---

### 第 1 章 · Basic Concepts（基本概念）
- **核心**：本章建立全部后续工作的字母表。先定义**仿射集**（过任意两点直线仍在其中），
  再定义**凸集**（过任意两点线段仍在其中）与**凸锥**（对非负组合封闭）。
  凸组合 $\sum\lambda_i x_i$（$\lambda_i\ge0,\sum\lambda_i=1$）给出构造凸集的代数工具，
  而**凸包** $\operatorname{conv} S$（所有凸组合）是最小的凸集。
  Carathéodory 定理把「无穷组合」压缩到「有限组合」：$\mathbb{R}^n$ 中凸包里任一点至多需要 $n+1$ 个点的凸组合——
  这是有限维凸性能用线性代数处理的根本原因。
- **飞腾锚点**：**FP16 3.81×[L01]** —— 🟢【事实】凸包的有限表示（$n+1$ 点）与浮点有限精度同构：
  计算机无法精确存「无穷点的平均」，但 Carathéodory 保证只需 $n+1$ 个顶点的线性组合即可精确命中凸包内任一点，
  正如 FP16 用 3.81× 速度换取有限的有效位数——有限性是凸集可计算的基石。
- **关键定理**：**Carathéodory 定理**：若 $x\in\operatorname{conv}(S)\subseteq\mathbb{R}^n$，则存在
  $x_1,\dots,x_{n+1}\in S$ 与 $\lambda_i\ge0$，$\sum\lambda_i=1$，使 $x=\sum_{i=1}^{n+1}\lambda_i x_i$。
  它把无限维的凸组合降为有限维，是后续线性规划（极点）与凸包计算的基石。
- **自测**：设 $S=\{(0,0),(1,0),(0,1),(1,1)\}$（正方形四顶点）。写出中心点 $(0.5,0.5)$ 的一种凸组合。
  再问：边界点 $(0.3,0)$ 用 Carathéodory 需要几个顶点？为什么不是 4 个？

---

### 第 2 章 · Topological Properties of Convex Sets（凸集拓扑性质）
- **核心**：普通「内部」对凸集不够用——$\mathbb{R}^3$ 中一张平面对自身有内部，
  但在 $\mathbb{R}^3$ 中内部为空。Rockafellar 引入**相对内部** $\operatorname{ri}(C)$：
  内部相对于 $C$ 的仿射包 $\operatorname{aff}(C)$ 来取。
  对凸集而言，相对内部**永远非空**（只要 $C\neq\varnothing$），这是凸集独有的拓扑福利。
  **线段原理**是全章最有用的工具：若 $x\in\operatorname{ri}C$、$y\in\operatorname{cl}C$，
  则开线段 $[x,y)\subseteq\operatorname{ri}C$——它把「相对内部」和「闭包」用一条线段连起来。
  闭包与相对内部的交换律 $\operatorname{ri}(\operatorname{cl}C)=\operatorname{ri}(C)$ 体现了凸集拓扑的「干净」。
- **飞腾锚点**：**TLB 4.81×[E04]** —— 🟢【事实】相对内部 = 在仿射包这一「更小的地址空间」里取内部，
  正如 TLB 在「页」这一局部寻址层级上获得 4.81× 加速——
  必须先把视角限制到正确的「子空间」（仿射包 / 页），才能看到真实的「内部」与性能。
- **关键定理**：**相对内部非空 + 线段原理**：对非空凸集 $C\subseteq\mathbb{R}^n$，
  $\operatorname{ri}(C)\neq\varnothing$；且 $\forall x\in\operatorname{ri}C,\ \forall y\in\operatorname{cl}C$，
  有 $[x,y)\subseteq\operatorname{ri}C$。线段原理是证明次微分非空、对偶间隙为零的关键引理。
- **自测**：令 $C=\{(x_1,x_2):x_2=0,\ 0\le x_1\le1\}\subseteq\mathbb{R}^2$。
  求 $\operatorname{aff}(C)$、$\operatorname{ri}(C)$、$\operatorname{cl}(C)$。验证 $\operatorname{int}(C)=\varnothing$ 但 $\operatorname{ri}(C)\neq\varnothing$。

---

### 第 3 章 · Polar Topology（极拓扑：分离超平面与对偶）
- **核心**：这是全书的**第一座高峰**。分离定理说：不相交的凸集可以用超平面分开。
  严格分离（闭凸集外的点）、支撑超平面（边界点处的切平面）是它的两个层级。
  Hahn-Banach 定理在有限维中的化身，正是这条分离定理。
  它的意义在于：**凸集的几何对偶化**——每个凸集 $C$ 对应一个由所有分离/支撑超平面法向量组成的空间（极锥），
  从而把「点的语言」翻译成「法向量的语言」。这条翻译贯穿全书，最终在共轭函数中达到顶峰。
- **飞腾锚点**：**Schmidt 正交化** —— 🟡【类比】分离超平面的法向量 $u$ 把空间「投影」成两侧：
  $\langle u,x\rangle\le\alpha$ 与 $\langle u,x\rangle>\alpha$，
  正如 Schmidt 正交化把向量投影到正交补——分离的本质是沿法向量的「投影分层」。
- **关键定理**：**分离定理**：设 $C$ 为非空闭凸集，$x\notin C$，则 $\exists\,u\neq0,\alpha$ 使
  $\langle u,x\rangle>\alpha\ge\sup_{y\in C}\langle u,y\rangle$（严格分离）。
  推论——支撑超平面：在闭凸集 $C$ 的每个边界点 $x$ 处，$\exists\,u\neq0$ 使
  $\langle u,x\rangle\ge\langle u,y\rangle,\ \forall y\in C$。
- **自测**：给 $C=\{x:x_1^2+x_2^2\le1\}$（单位圆盘），边界点 $x_0=(1,0)$。
  求该点处的支撑超平面（法向量 $u$ 与常数 $\alpha$）。

---

### 第 4 章 · Recession Cones and Unboundedness（退缩锥与无界性）
- **核心**：如何描述一个凸集「往哪个方向无穷延伸」？**退缩锥**（recession cone）
  $0^+C=\{y:x+ty\in C,\ \forall x\in C,\ \forall t\ge0\}$ 给出答案：
  沿 $y$ 方向走多远都不会离开 $C$ 的全体方向。
  凸集有界 $\iff 0^+C=\{0\}$；若 $0^+C$ 含一条直线（$y$ 与 $-y$ 都在），则 $C$ 含一条完整的线。
  **线性空间**（lineality space）是退缩锥中最大的子空间，刻画「$C$ 中平坦的、无界的方向」。
  这些概念在判断优化问题解是否存在（目标函数沿无界方向是否下降）时至关重要。
- **飞腾锚点**：**分支预测 0.71 vs 3.14[Lab02]** —— 🟡【类比】退缩锥 = 凸集「通向无穷的分支路径」：
  预测器识别沿哪条方向（$y$）走下去始终安全（不撞分支失败），
  而有界集没有这样的「安全方向」（每次都要重新计算，类似高误预测率 3.14）。
- **关键定理**：**退缩锥刻画**：对闭凸集 $C$，$y\in 0^+C\iff \exists x$ 使 $\{x+ty:t\ge0\}\subseteq C$。
  特别地 $C$ 有界 $\iff 0^+C=\{0\}$；$C$ 不含直线 $\iff 0^+C$ 为尖锥（pointed cone）。
  这是判断凸优化解存在性（目标函数水平集是否有界）的代数判据。
- **自测**：令 $C=\{(x,t):t\ge x^2\}=\operatorname{epi}(x^2)$（抛物线上方）。求 $0^+C$。
  它是尖锥吗？$C$ 有界吗？

---

### 第 5 章 · Convex Functions and Supporting Hyperplanes（凸函数与支撑超平面）
- **核心**：Rockafellar 的天才一笔：**用凸集定义凸函数**。
  函数 $f$ 凸 $\iff$ 其上方图（epigraph）$\operatorname{epi}f=\{(x,\alpha):f(x)\le\alpha\}$ 是凸集。
  这把第 1–4 章全部凸集定理瞬间变成凸函数定理——
  退缩锥描述函数在无穷远处的行为，相对内部给出有效域的性质。
  **有效域** $\operatorname{dom}f=\{x:f(x)<+\infty\}$ 是函数「有意义」的区域，
  扩充值 $+\infty$ 让任意函数（如指示函数 $\delta_C$）都纳入凸函数框架。
  **下半连续**（lsc）的闭包操作 $\operatorname{cl}f$ 保证共轭的二次共轭能回到自身。
- **飞腾锚点**：**UDOT 16.9×[E05]** —— 🟢【事实】epigraph 定义中 $f(x)\le\alpha$ 的 $\sup$ 判定、
  以及支撑超平面 $\sup_{x\in C}\langle u,x\rangle$ 的计算，
  本质是无符号点积累加（dot product）——UDOT 16.9× 正是这类 sup/求和运算在硬件上的加速比。
- **关键定理**：**epigraph 凸性等价**：$f:\mathbb{R}^n\to(-\infty,+\infty]$ 凸
  $\iff \operatorname{epi}f$ 为凸集。由此定义**真凸函数**（proper）：
  $f\not\equiv+\infty$ 且 $f(x)>-\infty,\forall x$。
  闭凸函数（epigraph 为闭凸集）是共轭理论的对象。
- **自测**：判断 $f(x)=|x|$ 的 epigraph 是否凸。写出 $\operatorname{dom}f$。
  再判断指示函数 $\delta_{[0,1]}(x)$（$x\in[0,1]$ 时为 $0$，否则 $+\infty$）是否为真凸函数。

---

### 第 6 章 · Differential Continuity and Subdifferentials（微分连续性与次微分）
- **核心**：凸函数不必处处可导（如 $|x|$ 在 $0$），但凸函数有一个惊人性质：
  **处处存在单侧方向导数** $f'(x;d)=\lim_{t\downarrow0}\frac{f(x+td)-f(x)}{t}$。
  Rockafellar 用**次微分** $\partial f(x)=\{u:f(y)\ge f(x)+\langle u,y-x\rangle,\ \forall y\}$
  推广梯度：次梯度 $u$ 是「在 $x$ 处支撑 epigraph 的超平面的斜率」。
  对可微凸函数，$\partial f(x)=\{\nabla f(x)\}$（唯一）；对 $|x|$ 在 $0$，$\partial f(0)=[-1,1]$（多值）。
  次微分把微积分从光滑世界推进到非光滑世界，是非光滑优化的数学基础。
- **飞腾锚点**：**Iron Law <2%[Lab00]** —— 🟢【事实】次微分给出非光滑函数在每点的**误差带 / 子梯度集合**，
  类似性能铁律「误差 < 2% 是可接受边界」：次梯度不是唯一斜率，而是一个可接受范围（对 $|x|$ 是 $[-1,1]$），
  优化器只需落在带内即可保证下降——这正是次梯度法的鲁棒性来源。
- **关键定理**：**次微分定义与可微情形**：
  $\partial f(x)=\{u:f(y)\ge f(x)+\langle u,y-x\rangle,\ \forall y\}$。
  凸函数 $f$ 在 $x$ 可微 $\iff \partial f(x)$ 为单点 $\{\nabla f(x)\}$。
  $x$ 是 $f$ 的极小点 $\iff 0\in\partial f(x)$（非光滑最优性条件，推广 $f'(x)=0$）。
- **自测**：求 $f(x)=|x|$ 在 $x=0$ 的 $\partial f(0)$。
  再用 $0\in\partial f(x)$ 验证 $x=0$ 是极小点。

---

### 第 7 章 · Conjugate Convex Functions（共轭凸函数：Fenchel 不等式）
- **核心**：这是全书的**第二座高峰**，也是 Rockafellar 最核心的贡献。
  **Fenchel 共轭** $f^*(u)=\sup_x\{\langle u,x\rangle-f(x)\}$ 是凸函数的「对偶函数」。
  它把一个关于 $x$ 的函数变成关于对偶变量 $u$ 的函数，且 $f^*$ 永远是闭凸函数（即使 $f$ 不是）。
  **Fenchel-Young 不等式** $f(x)+f^*(u)\ge\langle u,x\rangle$ 是凸分析的中心不等式，
  它的等号条件 $f(x)+f^*(u)=\langle u,x\rangle\iff u\in\partial f(x)$ 把共轭与次微分焊死在一起。
  二次共轭 $f^{**}\le f$，当 $f$ 为闭真凸时取等——这就是 Fenchel-Moreau 定理（自对偶性）。
- **飞腾锚点**：**matmul 15×[V03]** —— 🟡【类比】共轭 $f^*(u)=\sup_x\{\langle u,x\rangle-f(x)\}$
  把「原空间 $x$」经线性泛函 $\langle u,\cdot\rangle$ 映到「对偶空间 $u$」，
  类似矩阵乘法把向量从一组基变到另一组基（15× 加速）——共轭是函数空间的「对偶基变换」。
- **关键定理**：**Fenchel-Young 不等式**：
  $f(x)+f^*(u)\ge\langle u,x\rangle,\quad\forall x,u$；
  等号成立 $\iff u\in\partial f(x)$。
  **Fenchel-Moreau 定理（二次共轭）**：$f^{**}=\operatorname{cl}(\operatorname{conv}f)$，
  故闭真凸函数满足 $f^{**}=f$（自对偶）。
- **自测**：求 $f(x)=\tfrac12\|x\|^2$ 的共轭 $f^*(u)$。
  验证 Fenchel-Young 取等时 $u=x$（提示：对二次函数 $\partial f(x)=\{x\}$）。

---

### 第 8 章 · Support Functions and Polar Sets（支撑函数与极集）
- **核心**：每个凸集 $C$ 对应一个**支撑函数** $\sigma_C(u)=\sup_{x\in C}\langle u,x\rangle$——
  它回答「沿方向 $u$ 看，$C$ 最远到哪」。支撑函数是正齐次闭凸函数，且与 $C$ 的闭凸包一一对应。
  **极集** $C^\circ=\{u:\langle u,x\rangle\le1,\ \forall x\in C\}$ 是 $C$ 的「对偶凸集」。
  **双极定理** $C^{\circ\circ}=\operatorname{cl}\operatorname{conv}(C\cup\{0\})$ 是分离定理的对偶化身：
  一个点在 $C$ 的闭凸包里 $\iff$ 它满足所有定义 $C^\circ$ 的不等式。
  这建立了「集合↔不等式系统」的完全对偶，是线性规划对偶性的几何根源。
- **飞腾锚点**：**GEMM 9.45G[Lab05]** —— 🟢【事实】支撑函数 $\sup_{x\in C}\langle u,x\rangle$
  在高维凸集（如多面体顶点集）上的计算是批量点积取 max，正是 GEMM 高吞吐（9.45 GFLOPS）的用武之地——
  多面体的支撑函数 = 顶点矩阵乘 $u$ 后取 max，工程上直接调用 GEMM 内核。
- **关键定理**：**双极定理**：$C^{\circ\circ}=\operatorname{cl}\operatorname{conv}(C\cup\{0\})$。
  即 $x\in\operatorname{cl}\operatorname{conv}(C\cup\{0\})\iff\langle u,x\rangle\le1,\ \forall u\in C^\circ$。
  这等价于「凸集 = 其所有支撑超平面的交」，是 Farkas 引理的几何版。
- **自测**：令 $C=$ 单位球 $\{x:\|x\|\le1\}$。求 $C^\circ$（提示：用 Cauchy-Schwarz）。
  验证 $C^{\circ\circ}=C$（自对偶）。

---

### 第 9 章 · General Convex Functions and Subdifferentials（一般凸函数与次微分）
- **核心**：本章把单函数的次微分推广到**函数运算**的次微分——即次微积分（subdifferential calculus）。
  核心是**和规则**：$\partial(f+g)(x)\supseteq\partial f(x)+\partial g(x)$，
  在正则条件（如有效域相对内部相交 $\operatorname{ri}(\operatorname{dom}f)\cap\operatorname{ri}(\operatorname{dom}g)\neq\varnothing$）下取等。
  链式法则把复合 $\partial(g\circ A)(x)\supseteq A^*\partial g(Ax)$ 也建立了。
  本章还给出著名的 **Moreau 分解**：对闭凸锥 $K$，每个 $x$ 唯一分解为
  $x=P_K x+P_{K^\circ}x$（到 $K$ 与到极锥 $K^\circ$ 的正交投影之和），这是投影梯度法的理论根基。
  📌 对应原书 §20–§23（次微分运算）与锥投影部分。
- **飞腾锚点**：**matmul 15×[V03]**（复用 · 不同角度）—— 🟡【类比】和规则 $\partial(f+g)=\partial f+\partial g$
  把「函数相加」的次微分变成「次微分集合相加」（Minkowski 和），正如矩阵乘法把线性变换复合变成矩阵相乘——
  次微积分 = 非光滑世界的「矩阵乘法」，15× 加速的 GEMM 内核是其计算出口。
- **关键定理**：**次微分和规则 + Moreau 分解**。
  和规则：若 $\operatorname{ri}(\operatorname{dom}f)\cap\operatorname{ri}(\operatorname{dom}g)\neq\varnothing$，则
  $\partial(f+g)(x)=\partial f(x)+\partial g(x)$。
  Moreau 分解：对闭凸锥 $K$，$\forall x$，$x=P_K(x)+P_{K^\circ}(x)$，$P_K(x)\perp P_{K^\circ}(x)$。
- **自测**：用 Moreau 分解把 $x=(1,1)$ 分解到 $K=\mathbb{R}_+^2$（第一象限）与 $K^\circ$（极锥）。
  （提示：$K^\circ=\mathbb{R}_-^2$，验证两部分之和为 $(1,1)$。）

---

### 第 10 章 · Saddle-Points and Minimax Theory（鞍点与极小极大理论）
- **核心**：博弈论与对偶的交汇点。对函数 $K(x,y)$（$x$ 凸、$y$ 凹），
  **鞍点** $(x^*,y^*)$ 满足 $K(x^*,y)\le K(x^*,y^*)\le K(x,y^*)$——
  即 $x^*$ 是关于 $x$ 的极小点、$y^*$ 是关于 $y$ 的极大点。
  minimax 定理回答核心问题：何时 $\inf_x\sup_y K=\sup_y\inf_x K$？
  von Neumann（紧集 + 双线性）与 Sion（凸-凹 + 紧 + 半连续）给出充分条件。
  鞍点存在 $\iff$ minimax 等式成立，而 Lagrange 对偶的最优对偶间隙为零，正是鞍点定理的应用。
  📌 对应原书 §28（鞍点）与 §32（minimax）。
- **飞腾锚点**：**分支预测 0.71 vs 3.14[Lab02]**（复用）—— 🟡【类比】鞍点 = $\inf\sup$ 与 $\sup\inf$ 两条路径交汇的成功预测点（0.71 低误预测 = 有鞍点 = 对偶间隙为零）；
  若无鞍点，两条路径分叉（对偶间隙 > 0，类似 3.14 高误预测率），minimax 等式破裂。
- **关键定理**：**Sion minimax 定理**：设 $C,D$ 为 $\mathbb{R}^n$ 中非空紧凸集，
  $K(\cdot,y)$ 凸下半连续、$K(x,\cdot)$ 凹上半连续，则
  $$\min_{x\in C}\max_{y\in D}K(x,y)=\max_{y\in D}\min_{x\in C}K(x,y).$$
  鞍点存在的充要条件是上式两端相等。
- **自测**：验证 $K(x,y)=xy$ 在 $x,y\in[0,1]$ 上的鞍点。
  计算 $\inf_x\sup_y xy$ 与 $\sup_y\inf_x xy$，它们相等吗？鞍点是什么？

---

### 第 11 章 · Convex Analysis and Variational Problems（凸分析与变分问题）
- **核心**：本章把前 10 章的工具用于**变分/对偶问题**。
  Fenchel 对偶定理是核心：原始问题 $\inf_x\{f(x)+g(Ax)\}$ 的对偶为
  $\sup_y\{-f^*(A^Ty)-g^*(-y)\}$，强对偶（无间隙）在正则条件下成立。
  这是把「带约束的 $\inf$」翻译成「对偶空间 $\sup$」的系统方法，
  也是 SVM、Lasso、稀疏优化等机器学习模型对偶推导的统一框架。
  对变分问题（积分泛函 $F[u]=\int L(x,u,\nabla u)$），凸性保证 Euler-Lagrange 方程的解即全局最优。
  📌 对应原书 §29–§30（对偶问题与变分）。
- **飞腾锚点**：**UDOT 16.9×[E05]**（复用 · 不同角度）—— 🟢【事实】变分泛函 $F[u]=\int L\,dx$ 的数值离散化变成大规模点积求和（UDOT 16.9× 的主战场）；
  Fenchel 对偶 $f^*(A^Ty)$ 中 $A^Ty$ 也是矩阵-向量积后取 sup——
  凸分析的对偶在工程上密集调用点积累加硬件。
- **关键定理**：**Fenchel 对偶定理**：
  $$\inf_x\{f(x)+g(Ax)\}=\sup_y\{-f^*(A^Ty)-g^*(-y)\},$$
  在 $\operatorname{ri}(\operatorname{dom}g)\cap A\operatorname{ri}(\operatorname{dom}f)\neq\varnothing$ 时强对偶成立（等号）。
  这是 Lagrange 对偶的更一般形式。
- **自测**：用 Fenchel 对偶重写 $\min_x\|x\|_1\ \text{s.t.}\ Ax=b$。
  （提示：令 $f=\|\cdot\|_1$、$g=\delta_{\{b\}}$，写出对偶变量 $y$ 与对偶目标。）

---

### 第 12 章 · Convex Optimization and Lagrange Multipliers（凸优化与 Lagrange 乘子）
- **核心**：全书的**终点站**。把约束优化 $\min f(x)\ \text{s.t.}\ g_i(x)\le0$ 的最优性条件统一为 **KKT 条件**。
  Lagrange 函数 $L(x,\lambda)=f(x)+\sum\lambda_i g_i(x)$，KKT 四条：
  （1）驻点 $0\in\partial_x L$；（2）原可行 $g_i(x^*)\le0$；
  （3）对偶可行 $\lambda_i\ge0$；（4）互补松弛 $\lambda_i g_i(x^*)=0$。
  在**约束规范**（如 Slater 条件：$\exists$ 严格内点 $g_i(\bar x)<0$）下，
  KKT 是最优性的**充要条件**，且对偶间隙为零。Slater 条件是凸优化强对偶的实用判据。
  KKT 把分离定理（Ch3）、共轭（Ch7）、鞍点（Ch10）全部收束到一个公式——全书闭环。
  📌 对应原书 §28（Lagrange 乘子）与 §31（最优性条件）。
- **飞腾锚点**：**GEMM 9.45G[Lab05]**（复用 · 不同角度）—— 🟢【事实】KKT 系统是线性方程/不等式组（$\nabla f+A^T\lambda=0$ 等），
  求解大规模凸 QP（如 SVM 训练、模型预测控制）密集调用 GEMM 内核（9.45 GFLOPS 吞吐）——
  KKT 条件从理论到工程实现，最后一公里全在矩阵吞吐硬件上。
- **关键定理**：**KKT 条件（凸情形）**：设 $f,g_i$ 凸，Slater 条件成立。
  则 $x^*$ 最优 $\iff \exists\lambda_i\ge0$ 使
  $$0\in\partial f(x^*)+\sum_i\lambda_i\partial g_i(x^*),\quad \lambda_i g_i(x^*)=0,\quad g_i(x^*)\le0.$$
  这是非光滑凸优化的最优性充要条件。
- **自测**：写 $\min\ \tfrac12 x^2\ \text{s.t.}\ x\ge1$ 的 KKT 条件并求解。
  （提示：约束 $g(x)=1-x\le0$，$\lambda\ge0$，求 $\lambda$ 与 $x^*$。）

---

## §9 全书思想主线（约 200 字）

Rockafellar 1970 的暗线是**「epigraph 是桥梁，共轭是引擎」**。
全书可以读作一条单链：凸集的分离定理（Ch3）沿 epigraph（Ch5）翻译成凸函数的支撑性，
再经 Fenchel 共轭（Ch7）建立函数空间的对偶，
次微分（Ch6/Ch9）把共轭的等号条件具象化，
最终在鞍点（Ch10）与 KKT（Ch12）中把对偶应用于优化。
这条链上每个环节都是「有限维 + 代数几何」的纯粹操作——
没有测度论、没有弱拓扑、没有算法——但正是这种纯粹，
让它成为所有后续凸分析教材（Borwein-Lewis 的无穷维、Bertsekas 的几何、Boyd 的应用）的共同祖本。
读懂 Rockafellar，就是读懂凸性的**为什么**，而非仅仅**怎么用**。

与已读教材呼应：本书 = Borwein-Lewis / Bertsekas / Nesterov 三者的**公理源头**。
后三者各自取走一条轴（分析提升 / 几何直觉 / 算法复杂度），
而 Rockafellar 留下了完整的有限维公理体系本身。

---

## §10 与本仓库其他笔记的交叉引用

**与凸分析/优化三角的对照**：
- **`borwein_lewis_凸分析与非线性优化`**（刚做，536 行）：把 Rockafellar 的有限维定理「提升」到 Banach 空间。
  对照读法——Rockafellar Ch3 分离定理 → Borwein-Lewis Ch2 Hahn-Banach；
  Rockafellar Ch7 共轭 → Borwein-Lewis Ch6 Fenchel 对偶。
- **`bertsekas_凸优化理论`**（刚做，398 行）：同一套对偶理论的几何可读版。
  对照读法——Rockafellar Ch10 鞍点 = Bertsekas Ch4 Lagrange 对偶；
  Rockafellar Ch12 KKT = Bertsekas Ch2 最优性条件。
- **`nesterov_凸优化算法引论`**（332 行）：补本书缺失的「算法轴」——Rockafellar 只讲理论，Nesterov 讲 $O(1/k^2)$ 加速率。
- **`D-凸优化` / `D-优化理论_研究入门`**（Boyd 风格）：应用层，本书是其严格性根基。

**AI / 工程锚点（数学落到工程）**：
- 🟢 **次梯度下降**（PyTorch `torch.optim.SGD` + L1 正则）：非光滑优化用 $\partial f$，对应 Ch6/Ch9。Lasso 训练就是次梯度法。
- 🟢 **SVM 对偶**：硬间隔 SVM 的对偶推导是 Fenchel 对偶（Ch11）的教科书案例，KKT 互补松弛对应支持向量稀疏性（Ch12）。
- 🟢 **近端算子 / Moreau 分解**（Ch9）：`sklearn` / `proxTV` 中的 proximal gradient 算法，理论基础即 Moreau 分解 $x=P_Kx+P_{K^\circ}x$。
- 🟢 **KKT 求解器**（OSQP / CVXPY）：凸 QP 求解器内部解 KKT 线性系统，对应 Ch12，工程上调用 GEMM 内核（9.45G）。
- 🟡 **共轭函数与变分推断**：VAE 中的 ELBO 可视为 Fenchel 对偶的概率版，Rockafellar Ch7 是其分析基础（直觉类比，非严格）。

> **总结**：Rockafellar 1970 是凸分析的「公理层」，
> Borwein-Lewis 是「分析提升层」，Bertsekas 是「几何可读层」，Nesterov 是「算法层」，
> 四者合起来构成优化理论方向从公理到算法的完整光谱。
