# Dimitri Bertsekas《凸优化理论》 · 快速逐章精读

> **原书**：*Convex Optimization Theory*, Dimitri P. Bertsekas, Athena Scientific, 2009, ~260pp
> **读于**：2026-07-03
> **定位**：以「对偶」为中心轴线，从凸几何一路推到算法收敛的严格理论教材。
> **特色**：Bertsekas 用大量几何图示 + 投影 / 分离定理把抽象的对偶变成可视直觉，证明完整、结构干净。
> **声明**：本文为**快速逐章精读**（非逐页详读），套用八重视角骨架的精简版——
> 每章只抓核心逻辑链、一个飞腾锚点、一两条关键定理、一道可做的自测题。
> 附录 A（Mathematical Background，含线性代数、实分析、拓扑复习）并入 §0，不单列章节。
> **章节命名**：忠于原书 TOC（Ch1 基本凸性 / Ch2 凸优化问题 / Ch3 多面体凸性 /
> Ch4 对偶 / Ch5 锥对偶与次梯度 / Ch6 算法）。本文沿用任务给定标题，与原书结构一致。
>
> 三源 = Bertsekas 原书（严格对偶） × 已读 D-凸优化(Boyd 风格)/Nocedal-Wright（方法互补）
> × 飞腾 D3000M（硬件锚点）

---

## §0 引言：Bertsekas 的对偶中心化视角（约 350 字）

Dimitri Bertsekas（MIT）的这部书与市面所有凸优化教材最大的不同在于：
它**不把对偶当附录，而把对偶当脊柱**。
全书六章可以读作「为理解 Lagrange 对偶所做的层层铺垫」——

- **Ch1** 凸几何给出分离定理（对偶的几何源头），
- **Ch2** 给出最优性条件（对偶的靶向），
- **Ch3** 多面体给出 Farkas 引理（线性对偶的代数化身），
- **Ch4** 正面建立 Lagrange 对偶与 KKT（全书高潮），
- **Ch5** 把对偶推广到锥与不可微函数（共轭语言），
- **Ch6** 让算法在对偶空间里跑（对偶上升、近端）。

这种「对偶优先」的结构，使读者从一开始就建立
「每个原问题都有一个对偶影子」的几何直觉，
而非 Boyd 那样「先学会识别凸性、对偶留到最后当工具」。

与同类教材对比：

- **Boyd & Vandenberghe** 是「应用工程派」，海量例子、凸性识别为纲，对偶只占两章、证明略省；
- **Nesterov** 是「复杂度理论派」，把黑箱 oracle 与 $O(1/k^2)$ 加速率当主线，对偶是副产品；
- **Borwein & Lewis** 是「泛函分析派」，测度论与 Fenchel-Moreau 共轭严格化，数学味最浓、最不友好工程师。

Bertsekas 恰好卡在三者之间：比 Boyd 严格、比 Nesterov 几何、比 Borwein 可读。
附录 A（线性代数、实分析、拓扑复习）按需查阅即可。
对用户（Python 工程级 + 数学补课）而言，
本书最适合做「读完 Boyd 简版后补严格性」的第二轮教材——
D-凸优化笔记教你怎么用，本文教你为什么成立。

**同类教材 4 列对比**：

| 书 | 风格 | 严格性 | 适合谁 |
|---|---|---|---|
| **Bertsekas**《Convex Optimization Theory》(2009) | 几何驱动，对偶为中心，图示+严格定义交替 | 高（定理证明完整） | 想从几何直觉走到严格对偶的工程师/研究者 |
| **Boyd & Vandenberghe**《Convex Optimization》(2004) | 应用驱动，例题海量，凸性识别为纲 | 中高（略省证明细节） | 需要把实际问题建模成凸优化的实践者 |
| **Nesterov**《Introductory Lectures on Convex Optimization》(2004) | 复杂度驱动，黑箱 oracle，收敛率为主线 | 高（算法理论） | 研究一阶加速方法/收敛率的学者 |
| **Borwein & Lewis**《Convex Analysis & Nonlinear Optimization》(2000) | 泛函分析/测度论风味，Fenchel 共轭严格化 | 极高（分析味浓） | 数学专业、攻读变分/控制论的读者 |

---

## §1 全书 6 章骨架一览

| 章 | 标题 | 核心概念 | 飞腾锚点 |
|---|---|---|---|
| 1 | Convex Sets and Functions | 分离定理、epigraph、保凸运算、二阶条件 | Schmidt 正交化（投影分解） |
| 2 | Convex Optimization Problems | 解的存在性、最优性条件、投影变分不等式 | 分支预测 0.71 vs 3.14（active set） |
| 3 | Polyhedral Convexity | Farkas 引理、Minkowski-Weyl、极点/极方向 | TLB 4.81×（稀疏内存局部性） |
| 4 | Duality | Lagrange 对偶、强/弱对偶、Slater、KKT、鞍点 | UDOT 16.9×（对偶内积吞吐） |
| 5 | Conic Duality & Subgradients | 正规锥、次微分、Fenchel 共轭、锥对偶 | FP16 3.81×（次梯度精度/鲁棒） |
| 6 | Algorithms | 次梯度法、近端算法、对偶上升 | matmul 15×（QP/二阶矩阵吞吐） |

> **读法建议**：Ch1–Ch2 可快速过（若已读 Boyd）；**Ch3 与 Ch4 必须精读**（全书灵魂）；
> Ch5 为 SDP/SOCP 铺路（做机器学习/信号处理的人重点看次梯度）；Ch6 与 Nocedal-Wright 互补着读。

---

## 第 1 章 · Convex Sets and Functions（凸集与凸函数）

### 核心（概念逻辑串联）

凸集用「线段封闭」定义——
$\forall x,y\in C,\ \lambda\in[0,1]\Rightarrow \lambda x+(1-\lambda)y\in C$。
由此推出全书地基「**分离超平面定理**」：两个不相交凸集可被一张超平面劈开，
这是有限维的 Hahn-Banach，也是对偶理论的几何源头。

凸函数靠 **epigraph（上图）** 判定：
$\text{epi}\,f=\{(x,t):f(x)\le t\}$ 是凸集 $\Leftrightarrow$ $f$ 凸。
这把「函数凸性」转化为「集合凸性」，统一了两个语言。
然后系统梳理**保凸运算**（非负加权和、仿射复合、逐点上确界、透视），
把「这函数凸不凸」变成可操作的判定流水线。
一阶条件 $\nabla f(x)^T(y-x)\le f(y)-f(x)$ 与二阶条件 $\nabla^2 f\succeq 0$
给出与微积分的接口，为 Ch2 最优性条件铺路。

### 飞腾锚点

🟢 **Schmidt 正交化 → 投影/正交分解**。
投影算子 $P_C(x)=\arg\min_{z\in C}\|z-x\|$ 把 $x$ 拆成「最近点 + 残差」两部分，
与 Gram-Schmidt 正交化中「投影到已生成子空间、取残差为新基向量」的逻辑同构。
投影是凸优化迭代法（投影梯度、近端）的砖石，
也对应分离定理中「超平面法向量」的几何来源——
残差方向就是分离超平面的法向。

### 关键定理

- **分离定理**：若 $C_1,C_2$ 为不相交非空闭凸集且至少其一紧致，
  则存在超平面严格分离二者。
- **凸函数二阶条件**：$f$ 二阶连续可微则凸 $\Leftrightarrow$ $\nabla^2 f(x)\succeq 0,\ \forall x$。
- **Jensen 不等式**：$f\big(\sum_i \lambda_i x_i\big)\le \sum_i \lambda_i f(x_i)$，$\lambda_i\ge0,\ \sum\lambda_i=1$。
- **保凸运算**：$f,g$ 凸 $\Rightarrow$ $f+g$ 凸、$\max(f,g)$ 凸；$h$ 凸且非减、$g$ 凸 $\Rightarrow$ $h(g(x))$ 凸。

### 自测

1. 判断 $f(x,y)=x^2/y$（定义域 $y>0$）是否凸？
   提示：算 Hessian $\nabla^2 f$ 并验证半正定性，留意 $\det(\nabla^2 f)$ 的符号。
2. 用 epigraph 语言证明 $f(x)=e^x$ 凸，并与二阶条件对照。

---

## 第 2 章 · Convex Optimization Problems（凸优化问题）

### 核心

标准形 $\min_{x\in X} f(x)$。
解的**存在性**靠 Weierstrass（$X$ 紧致 + $f$ 连续 $\Rightarrow$ 极值可达）；
无约束时最优性即 $\nabla f(x^*)=0$。
有约束时，最优性由「投影梯度为零」刻画的**变分不等式**给出——
$x^*$ 最优 $\Leftrightarrow$ $\nabla f(x^*)^T(x-x^*)\ge 0,\ \forall x\in X$，
几何上即「梯度与可行方向成钝角」。

**凸性的红利**：局部最优即全局最优，凸函数没有「假极值」。
本章把「可行域几何」与「目标梯度」用最优性条件焊接，
投影算子 $P_X$ 成为核心工具，为 Ch4 的 Lagrange 对偶搭好舞台——
对偶本质上是把约束「外罚」进目标后，在无约束空间求下确界。

### 飞腾锚点

🟡 **分支预测 0.71 vs 3.14 [Lab02] → active set 选择**。
有效约束集（active set）的判定本质是条件分支：
哪些不等式约束 $g_i(x^*)=0$（取等）。
分支预测失配惩罚（条件分支 $\sim3.14$ cycles vs 无分支 $\sim0.71$）
正对应 active set 频繁切换导致的计算抖动——
这是 QP / active-set 求解器调优中「让分支可预测」的隐性瓶颈，
也是为何 warm-start（沿用上一步 active set）能显著加速。

### 关键定理

- **存在性（Weierstrass）**：$X$ 紧致、$f$ 连续下半紧致 $\Rightarrow$ 最优解 $x^*$ 存在。
- **投影最优性（变分不等式）**：$x^*\in X$ 最优 $\Leftrightarrow$
  $$\nabla f(x^*)^T(x-x^*)\ge 0,\quad \forall x\in X$$
  等价地 $x^*=P_X(x^*-\alpha\nabla f(x^*))$ 对一切 $\alpha>0$ 成立（投影梯度法停机判据）。
- **全局最优**：凸优化中局部最优 $\Leftrightarrow$ 全局最优（凸函数无鞍点外的假极值）。

### 自测

求 $\min\ x_1^2+x_2^2$ s.t. $x_1+x_2\ge 2$ 的最优解。
先用几何直觉（投影到直线 $x_1+x_2=2$），再用 KKT 验证，并写出有效约束。

---

## 第 3 章 · Polyhedral Convexity（多面体凸性）

### 核心

多面体 $P=\{x:Ax\le b\}$ 是有限个线性不等式刻画的凸集——
LP、QP、网络流的可行域都是它。
**Farkas 引理**给出「$Ax\le b$ 有解」与
「不存在 $y\ge0$ 使 $A^Ty=0,\ b^Ty<0$」的对偶等价——
这是线性规划对偶的代数源头，也是「不可行的证明」即「对偶解」。

**Minkowski-Weyl 定理**把多面体拆成
「极点凸组合 + 极方向非负组合」，
LP 的最优值必在极点取到——这正是单纯形法（simplex）的几何根基。
本章让「线性代数结构」与「凸几何」精确对接：
$A$ 的行空间决定约束法向，极点对应有效约束梯度的满秩组合。

### 飞腾锚点

🟢 **TLB 4.81× [E04] → 稀疏内存局部性**。
大规模 LP/QP 的约束矩阵 $A$ 高度稀疏（非零元 $\ll 1\%$），
稀疏存储（CSR/CSC）让 TLB 命中率从随机访问的 4.81× 惩罚中解救出来。
Interior Point 法每步解的 KKT 线性系统 $(AD^2A^T)\Delta y = r$，
其块状/对角结构正是「多面体稀疏性」在数据布局上的投影——
求解器 70% 时间耗在 TLB 友好的符号分解上，而非数值计算。

### 关键定理

- **Farkas 引理**：下列恰一成立——
  (i) $\exists x\ge0,\ Ax=b$；(ii) $\exists y,\ A^Ty\ge0,\ b^Ty<0$。
- **Minkowski-Weyl**：$P$ 是多面体 $\Leftrightarrow$ $P$ 可表为有限极点凸组合加极方向非负组合。
- **极点刻画**：$\bar x\in P$ 是极点 $\Leftrightarrow$ $\bar x$ 处有效约束的梯度列张满 $\mathbb{R}^n$（线性无关）。
- **LP 最优性**：线性目标在多面体上的最优值（若有限）必在极点达到。

### 自测

给定 $P=\{(x_1,x_2): x_1\ge0,\ x_2\ge0,\ x_1+x_2\le 1\}$：
列出全部极点与极方向；并解释 $\min\ -x_1-x_2$ 在 $P$ 上的最优解
为何是整条边 $\{(t,1-t):t\in[0,1]\}$（极值点退化情形）。

---

## 第 4 章 · Duality（对偶）⭐ 全书高潮

### 核心

Lagrange 函数 $L(x,\lambda,\mu)=f(x)+\sum_i\lambda_i g_i(x)+\sum_j\mu_j h_j(x)$
把约束「外罚」进目标。
对偶函数 $q(\lambda)=\inf_x L(x,\lambda)$ 始终凹、始终给出原问题下界
（弱对偶 $q\le p^*$，无需凸性）。
当原问题凸且满足 **Slater 条件**（存在严格可行点）时，
下界紧致——**强对偶** $d^*=p^*$ 成立，对偶间隙为零。

**鞍点** $(x^*,\lambda^*)$ 同时是原最优与对偶最优；
minimax 定理刻画零和博弈均衡，是 KKT 的另一副面孔。
**经济解释**：$\lambda_i^*$ 是第 $i$ 个约束的「影子价格」——
放松该约束一点点，最优值改善 $\lambda_i^*$ 那么多。
本章是全书灵魂，前 3 章皆为此铺路。

### 飞腾锚点

🟡 **UDOT 16.9× [E05] → 对偶内积吞吐**。
Lagrangian 的计算核心是内积 $\lambda^T g(x)$ 与分量求和——
点积指令（DOT）加速器在算对偶函数值时比标量循环快约 16.9×。
对偶上升法（dual ascent）每步的 $\lambda\gets[\lambda+\alpha g(x_k)]^+$
就是批量内积 + 向量更新，吞吐受限于点积指令宽度，而非算术逻辑单元。
这也是为何向量化（SIMD/AVX）的对偶求解器比标量实现快一个数量级。

### 关键定理

- **弱对偶**：$q(\lambda)\le p^*$ 对一切 $\lambda\ge0$ 恒成立，无需凸性。
- **强对偶（Slater 约束规格）**：若 $f,g_i$ 凸、$h_j$ 仿射，
  且 $\exists\tilde x$ 使 $g_i(\tilde x)<0,\ h_j(\tilde x)=0$，则 $d^*=p^*$（对偶间隙为零）。
- **KKT 充要条件**（凸 + Slater 下）：$x^*$ 最优 $\Leftrightarrow$ 存在 $\lambda^*\ge0,\mu^*$ 满足
  $$\nabla f(x^*)+\sum_i\lambda_i^*\nabla g_i(x^*)+\sum_j\mu_j^*\nabla h_j(x^*)=0 \quad\text{(平稳性)}$$
  $$\lambda_i^* g_i(x^*)=0\ \forall i \quad\text{(互补松弛)},\qquad g_i(x^*)\le0,\ h_j(x^*)=0 \quad\text{(可行)}$$
- **鞍点定理**：$(x^*,\lambda^*)$ 是 $L$ 的鞍点 $\Leftrightarrow$ $x^*$ 原最优、$\lambda^*$ 对偶最优且无间隙。

### 自测

对 $\min\ \tfrac12\|x\|^2$ s.t. $Ax=b$（等式约束）：
写出 Lagrange 对偶问题，求出对偶最优 $\mu^*$，并验证 $p^*=d^*$。
（提示：对偶变量 $\mu$ 维数 = $A$ 行数；解涉及 $A^\dagger$。）

---

## 第 5 章 · Conic Duality and Subgradients（锥对偶与次梯度）

### 核心

把不等式约束推广到**锥约束** $g(x)\in K$
（$K$ 为正规锥 proper cone，如非负卦限、二阶锥、半定锥 $\mathbb{S}^n_+$）。
锥对偶是**半定规划（SDP）**、**二阶锥规划（SOCP）**的统一理论框架——
现代鲁棒优化、核方法（SDP 松弛）、相位恢复的对偶都建在此上。

当函数不可微（如 $|x|$、$\max(0,x)$），梯度不存在，
用**次梯度** $g\in\partial f(x)$ 替代：
次微分 $\partial f$ 是闭凸集，满足 $f(y)\ge f(x)+g^T(y-x)$。
**Fenchel 共轭** $f^*(y)=\sup_x(y^Tx-f(x))$ 给出对偶的「共轭语言」，
是凸分析的普适工具——
原问题与对偶问题的关系变成 $f$ 与 $f^*$ 的对偶，
$y\in\partial f(x) \Leftrightarrow x\in\partial f^*(y)$（互反性）。

### 飞腾锚点

🟡 **FP16 3.81× [L01] → 次梯度精度/鲁棒**。
次梯度法步长粗放（$\alpha_k\to0$ 但 $\sum\alpha_k=\infty$），
只需次优精度的场景（鲁棒优化、分布式对偶、联邦学习）中，
低精度浮点 FP16/BF16 的 3.81× 吞吐增益划算。
但次梯度累积方向噪声大，
FP16 的舍入误差需用 Kahan 求和或随机舍入补偿——
这是「理论鲁棒性」与「数值稳定性」的权衡点，
也是为何 BF16（更宽指数位）在训练中比 FP16 更受青睐。

### 关键定理

- **次微分定义**：$\partial f(x)=\{g: f(y)\ge f(x)+g^T(y-x),\ \forall y\}$，
  凸函数的 $\partial f(x)$ 非空闭凸。
- **次微分运算法则**：$\partial(\alpha f)=\alpha\partial f$（$\alpha>0$）；
  $\partial(f+g)\supseteq\partial f+\partial g$（等号在连续点处成立）。
- **Fenchel 对偶定理**（约束规格下）：
  $$\inf_x\big[f(x)+h(Ax)\big]=\sup_y\big[-f^*(-A^Ty)-h^*(y)\big]$$
- **Fenchel-Young 不等式**：$f(x)+f^*(y)\ge x^Ty$，等号 $\Leftrightarrow$ $y\in\partial f(x)$。

### 自测

1. 求 $f(x)=|x|$ 在 $x=0$ 的次微分 $\partial f(0)$。
   （提示：它是闭区间 $[-1,1]$。）
2. 求 ReLU 函数 $f(x)=\max(0,x)$ 的 Fenchel 共轭 $f^*$。
   （提示：分段求 $\sup_x(yx-\max(0,x))$，注意 $y$ 的取值范围。）

---

## 第 6 章 · Algorithms（算法）

### 核心

本章把前 5 章的理论变成可跑的迭代。

- **次梯度法** $x_{k+1}=P_X(x_k-\alpha_k g_k)$（$g_k\in\partial f(x_k)$）：
  收敛慢（$O(1/\sqrt{k})$）但适用于不可微。
- **近端算法** $x_{k+1}=\text{prox}_{\alpha f}(x_k)
  =\arg\min_u\{f(u)+\frac{1}{2\alpha}\|u-x_k\|^2\}$：
  对复合目标 $f(x)+g(x)$ 拆分光滑项与稀疏项（如 Lasso 的 $L_1$）。
- **对偶上升法** $\lambda_{k+1}=[\lambda_k+\alpha_k g(x_k)]^+$：
  在对偶空间迭代，可分解大规模耦合问题（ADMM 的雏形）。

Bertsekas 强调：算法选择取决于问题的**可微性与结构**，
而非「哪个收敛快」的口号。
光滑用梯度法、强凸加加速、不可微用次梯度/束方法、
复合结构用近端、可分离用 ADMM。

### 飞腾锚点

🟢 **matmul 15× [V03] → QP/二阶矩阵吞吐**。
QP 求解（SVM、投资组合、模型预测控制）每步需解线性系统 $H\Delta x=-g$
或 Hessian-vector 乘积，矩阵乘法 / Cholesky 分解是吞吐瓶颈。
专用矩阵乘法核（tensor core / GEMM 单元）相对标量循环约 15× 加速，
使大规模二阶方法（Newton、Interior Point、natural gradient）
在合理时间内可行——
这是为何 GPU 训练大模型能承受每步二阶信息的成本估算。

### 关键定理

- **次梯度收敛**：步长 $\sum\alpha_k=\infty,\ \sum\alpha_k^2<\infty$
  $\Rightarrow$ $x_k\to x^*$（a.s.）；最优值收敛率 $O(1/\sqrt{k})$。
- **近端算子性质**：$\text{prox}_{\alpha f}$ 是 firmly nonexpansive（$\tfrac12$-平均非扩张），
  $x=\text{prox}_{\alpha f}(x)$ $\Leftrightarrow$ $0\in\partial f(x)$。
- **近端梯度收敛**：$f$ $L$-光滑、$g$ 凸时，
  $x_{k+1}=\text{prox}_{\alpha g}(x_k-\alpha\nabla f(x_k))$ 收敛率 $O(1/k)$；
  加速版 FISTA 达 $O(1/k^2)$。

### 自测

写出 Lasso 问题 $\min\ \frac{1}{2n}\|Ax-b\|^2+\lambda\|x\|_1$ 的 ISTA（近端梯度）迭代公式，
并指出软阈值算子 $\text{soft}(z,\gamma)=\text{sign}(z)\max(|z|-\gamma,0)$ 的来源。
（提示：$L_1$ 范数的 prox 即软阈值；先做梯度步再 prox $L_1$。）

---

## §9 全书思想主线（约 200 字）

Bertsekas 把「**对偶**」当作贯穿全书的脊柱：

- **Ch1** 凸几何（分离定理 = 对偶的几何源头）
- → **Ch2** 最优性（投影变分不等式 = 对偶的靶向）
- → **Ch3** 多面体（Farkas 引理 = 线性对偶的代数化身）
- → **Ch4** Lagrange 对偶（强对偶 + KKT + 鞍点 = 全书高潮）
- → **Ch5** 锥对偶 + 次梯度（共轭语言推广到 SDP/SOCP 与不可微）
- → **Ch6** 算法（对偶上升 + 近端 = 让对偶理论跑起来）。

这条主线让读者始终看见「每个原问题背后都有一个对偶影子」。
与 **Boyd**（先建模凸性、对偶留作工具）的应用主线不同，
Bertsekas 是「先吃透对偶几何、再设计算法」；
与用户已读的 **Nocedal & Wright**（数值算法优先、对偶一笔带过）互补——
Bertsekas 补上了 N&W 轻描淡写的对偶地基。
读完本书，再回看深度学习中的 Adam（对角预条件次梯度）、
近端 SGD、SVM 对偶，
会发现它们全是 Ch4–Ch6 的特例。

---

## §10 交叉引用（与已读笔记 / AI 工程锚点）

1. **D-凸优化（概念横切，本仓库）**
   ：D 笔记第 4 章 KKT 是 Boyd 工程速查版；
   本文 **Ch4** KKT 给出完整证明与 Slater 充要性，二者互补——
   D 用于「快速回忆条件」，本文用于「理解为何成立」。

2. **nocedal_wright_数值优化（本仓库，已读）**
   ：N&W 第 12 章（线性约束 QP）、第 16 章（罚/增广 Lagrange）的算法
   ↔ 本文 **Ch6** 对偶上升/近端；
   N&W 偏数值实现，本文偏几何与对偶理论。
   N&W 的 KKT 在 Ch12 一笔带过，本文 Ch4 是其严格地基。

3. **boyd 简版（D-凸优化笔记主体）**
   ：Boyd 第 5 章对偶是工程速查表，假设 Slater「显然满足」；
   本文 **Ch4** 明确写出 Slater 的几何含义（严格可行点 = 多面体内部点），
   解释「为何对偶间隙有时不为零」。

4. **SVM 对偶（AI 锚点）**
   ：硬间隔 SVM $\min\ \frac12\|w\|^2$ s.t. $y_i(w^Tx_i+b)\ge1$ 的对偶为
   $$\max_\alpha\ \sum_i\alpha_i-\frac12\sum_{i,j}\alpha_i\alpha_j y_i y_j\, x_i^Tx_j$$
   强对偶成立（凸 + Slater）。$\alpha_i^*>0$ 恰对应支持向量——
   这是 **Ch4** 强对偶 + 互补松弛的直接产物，
   也是「对偶变量 = 约束重要性」的最美范例。

5. **深度学习优化（AI 锚点）**
   ：Adam $\approx$ 对角预条件 + 动量次梯度（**Ch6**）；
   近端 SGD 处理 $L_1$/group Lasso 正则（**Ch6** 近端算子）；
   二阶 natural gradient 是 Fisher 信息矩阵下的 Newton（**Ch6** 二阶方法）。
   用户的 PyTorch 实战与本文 Ch6 一一对应。

6. **Lasso / 压缩感知（AI 锚点）**
   ：ISTA/FISTA 是近端梯度法（**Ch6**），软阈值 $\text{soft}$ 是 $L_1$ 范数的 prox；
   Lasso 对偶揭示「$\lambda$ = 噪声水平的对偶价格」（**Ch4** 互补松弛）。
   本文 Ch5 次微分给出 $\partial\|x\|_1$ 的严格刻画。

---

> **下一步**：沿 01-track/stage-1 精读做题；遇优化概念查 04-concepts/D-凸优化 跑三维交叉。
> 本笔记定位为 stage-3 优化方向的「理论严格性补强」第二轮教材。
> 建议配合已读 nocedal_wright 数值优化笔记的算法实现章节交叉阅读。
