# B. A. Dubrovin, A. T. Fomenko, S. P. Novikov《现代几何：方法与应用》 · 快速逐章精读

> 基于原书：Modern Geometry: Methods and Applications, 3 Vols (GTM 93/104/124), B. A. Dubrovin, A. T. Fomenko, S. P. Novikov, Springer, 1984–1990 / 读于：2026-07-03
> 定位：**俄罗斯学派几何百科，以变换群为骨、物理应用为肉**，把曲面几何↔张量↔同调↔Lie 群↔时空↔变分↔规范场织成一张网，是「数学家与物理学家共读」的现代几何蓝本。
> 本文为**快速逐章精读**，每章 1 个飞腾锚点 + 1 个关键定理 + 1 道自测题。

---

## §0 引言：《现代几何》是什么，为什么读它

Dubrovin-Fomenko-Novikov《现代几何：方法与应用》(3 卷本, 1984–1990) 是**俄罗斯学派几何教材的标杆**，与西方纯数学路线（do Carmo、Kobayashi-Nomizu）的根本区别在于**物理应用导向**。全书以 Klein 的「Erlangen 纲领」——「几何 = 变换群的不变量」——为隐含主线：从平面的等距/仿射/共形变换（Ch 1），到曲面的内蕴几何（Ch 2），再到 Lie 群作为对称的载体（Ch 6）、规范场作为联络（Ch 10），「群」始终是组织几何的脊柱。这使得「张量」不是孤立的代数练习（Ch 3-4），而是为相对论（Ch 7）、变分（Ch 8）、PDE（Ch 9）服务的语言。

DFN 的另一鲜明特征是**拓扑与几何的早期融合**：在曲面理论刚结束时（Ch 5）就引入同调论与 de Rham 上同调，让 Gauss-Bonnet 定理（$\int K\,dA=2\pi\chi$）成为「曲率积分=拓扑不变量」的第一个见证，并为 Ch 10 的示性类、规范场拓扑荷铺垫。Novikov（Fields 奖得主，叶状结构/孤立子）的影子在 Ch 9（可积系统）与 Ch 10（规范场）尤为明显。

读 DFN 的价值：当 Lee/do Carmo 把几何当作自洽的纯数学展开时，DFN 每章都指向一个物理出口——空间-时间度量即广义相对论，测地线即自由下落，变分即光学路径，规范场即 Yang-Mills。对目标是「应用数学研究型工程师」的读者，DFN 是**把几何从抽象拉回物理世界**的最佳桥梁。代价是跨度极大（3 卷覆盖了西方 5-6 门课的内容），需要按主题选读而非逐页精读。

| 书 | 风格 | 严格性 | 适合谁 |
|---|---|---|---|
| **Dubrovin-Fomenko-Novikov** (1984–90) | 俄罗斯学派，变换群+物理应用，几何拓扑物理一体化 | 高，定理完整，证明适中，跨度大 | 物理导向的应用数学/理论物理/工程 |
| **Spivak** 微分几何 5 卷 (1979) | 历史叙事+几何直觉，最详尽，纯数学 | 高，叙事流畅，篇幅浩繁 | 建立直觉后的纵深阅读 |
| **Lee** 三件套 (GTM218/202/176) | 友好递归，每概念先铺垫，自包含 | 高，最易自学 | 自学零基础，怕抽象 |
| **Kobayashi-Nomizu** 双子卷 (1963/69) | 主丛联络(Cartan)，百科全书，最抽象 | 极高，符号密集 | 研究者权威参考 |

**建议路线**：Lee GTM218 先读建立光滑流形基础 → DFN 卷 I（Ch 1-4）建立曲面+张量+物理直觉 → do Carmo 补黎曼几何可手算细节 → DFN 卷 II-III 选读同调/Lie 群/规范场（按研究方向）。与 Bott-Tu GTM82（de Rham）配套读 DFN Ch 5/10 最顺。

> 🟢 事实可作锚点：Theorema Egregium、Gauss 方程、Gauss-Bonnet、de Rham 定理、Lie 第三定理、Poincaré-Hopf 指标定理、Euler-Lagrange、Yang-Mills 方程均为严格定理。
> 🟡 类比（联络=「标架搬运规则」、曲率=「搬运的不可积性」、规范场=「相位连接」）仅供直觉，**绝不在严格证明中引用**。

---

## §1 全书 10 主题骨架一览（飞腾锚点分布）

| 章 | 标题 | 核心概念 | 飞腾锚点 |
|:-:|------|---------|---------|
| 1 | Geometry in Regions of a Plane（平面区域几何） | 坐标系、度量、长度/角度/面积、等距/仿射/共形变换、Erlangen 纲领 | **TLB 4.81×[E04]** ⭐ |
| 2 | General Theory of Surfaces（曲面一般理论） | 第一/第二基本形式、Gauss 曲率、Theorema Egregium、测地线、Gauss-Bonnet | **UDOT 16.9×[E05]** ⭐⭐ |
| 3 | Tensors: The Algebraic Theory（张量代数） | 多线性映射、变换律、张量积、缩并、外代数 | **matmul 15×[V03]** ⭐ |
| 4 | The Differential Calculus of Tensors（张量微分） | 协变导数、Christoffel、联络、平行移动、曲率张量、Levi-Civita | **GEMM 9.45G[Lab05]** ⭐⭐ |
| 5 | The Elements of Homology Theory（同调论基础） | 单纯复形、链复形、$\partial^2=0$、同调群、Betti 数、Euler 示性数、de Rham | **分支预测[Lab02]** ⭐ |
| 6 | Covariant Differentiation and the Lie Group（Lie 群） | Lie 群、Lie 代数、指数映射、Lie 三定理、双不变度量、Killing 场 | **Schmidt 正交化** ⭐⭐ |
| 7 | The Metric Structure of Space-Time（时空度量） | 伪 Riemann、Lorentz 度量、Minkowski、光锥、特殊/广义相对论 | **FP16 3.81×[L01]** ⭐⭐ |
| 8 | The Calculus of Variations and Geometric Optics（变分与光学） | 泛函、Euler-Lagrange、测地线极值、Fermat 原理、Hamilton-Jacobi | **Iron Law<2%[Lab00]** ⭐ |
| 9 | Geometric Theory of Differential Equations（微分方程几何理论） | 向量场与流、特征线、一阶 PDE、辛几何、完全可积（Liouville） | **UDOT 16.9×[E05]**（复用） |
| 10 | Lie Algebras, Cohomologies, and Gauge Fields（规范场） | Lie 代数上同调、de Rham、示性类、Chern-Weil、Yang-Mills 规范场 | **matmul 15×[V03]**（复用） |

**三条主线**：

1. **变换群红线**——Ch 1 平面变换 $\to$ Ch 6 Lie 群 $\to$ Ch 10 规范群，「几何=群的不变量」（Erlangen）从有限维到无穷维；
2. **曲率↔拓扑红线**——Ch 2 Gauss 曲率 $\to$ Ch 4 曲率张量 $\to$ Ch 5 同调/Euler 示性数 $\to$ Ch 10 示性类，「整体不变量由局部几何积分给出」；
3. **几何↔物理红线**——Ch 7 时空度量 $\to$ Ch 8 变分光学 $\to$ Ch 9 可积 PDE $\to$ Ch 10 规范场，每一章都对应一个物理理论。

---

### 第 1 章 · Geometry in Regions of a Plane（平面区域几何）⭐

> 坐标系与度量 / 长度·角度·面积公式 / 等距变换·仿射变换·共形变换 / 变换群的不变量（Erlangen 纲领）

- **核心**：本章是全书的「2D 实验室」。从 Euclid 度量 $ds^2=dx^2+dy^2$ 出发，导出弧长 $\int\sqrt{\dot x^2+\dot y^2}\,dt$、夹角 $\cos\theta=\frac{\langle u,v\rangle}{|u||v|}$、面积 $\int dx\wedge dy$。
  - **变换群视角**：等距群（保距离，刚体运动）、仿射群（保直线与平行，$x\mapsto Ax+b$）、共形群（保角度，复解析 $w=f(z)$）逐级扩大。
  - Klein 的 **Erlangen 纲领**（1872）：每种几何就是某个变换群的不变量理论——这一思想贯穿全书（Ch 6 的 Lie 群是其严格化）。
  - 换坐标下的度量变换 $g'_{ij}=\frac{\partial x^k}{\partial x'^i}\frac{\partial x^l}{\partial x'^j}g_{kl}$ 是 Ch 3 张量变换律的 2D 原型。
- **历史/动机**：Euler 与 Gauss 用内在坐标研究曲面；Klein 用群论统一各几何分支。DFN 从平面起手是为了让变换群思想「可视可算」。
- **飞腾锚点**：**TLB 4.81×[E04]** ⭐ —— 坐标变换 = 跨页地址重映射，局部坐标卡常驻缓存。
  - 🟢事实：换坐标时度量分量 $g_{ij}$ 按 Jacobian 矩阵缩并，数据局部性高时 TLB 命中快 4.81 倍；极坐标/球面坐标的查表与坐标卡换页同构。
  - 🟡类比：坐标系 = 内存页表；坐标变换 = TLB 跨页映射；「换坐标不改变几何本身」=「换地址不改变数据」。
- **几何/应用**：保角变换是复分析与流体力学的工具（流线绕柱）；仿射变换是计算机图形学的基石。
- **关键定理**：$$\text{换变量面积公式：}\int_D f\,dx\,dy=\int_{D'}f(x(u,v),y(u,v))\,\bigl|\det\frac{\partial(x,y)}{\partial(u,v)}\bigr|\,du\,dv;\quad \text{共形映射保角：}w=f(z)\text{ 解析}\Rightarrow\text{保角。}$$
- **自测**：写出极坐标下度量 $ds^2=dr^2+r^2d\theta^2$；验证 $w=z^2$ 在 $z\neq0$ 处保角（解析且导数非零）。

---

### 第 2 章 · General Theory of Surfaces（曲面一般理论）⭐⭐

> $\mathbb{R}^3$ 中曲面 / 第一基本形式 $g_{ij}$ / 第二基本形式 $b_{ij}$ / 法曲率·主曲率 / Gauss 曲率 $K$ / 平均曲率 $H$ / Theorema Egregium / 测地线 / Gauss 方程 / Gauss-Bonnet 定理

- **核心**：本章是经典微分几何的心脏。
  - **第一基本形式** $I=g_{ij}dx^idx^j$ 给内蕴度量（长度、角度、面积）；**第二基本形式** $II=b_{ij}dx^idx^j$ 描写曲面在 $\mathbb{R}^3$ 中的弯曲（外蕴）。
  - **Gauss 曲率** $K=\kappa_1\kappa_2=\frac{b_{11}b_{22}-b_{12}^2}{g_{11}g_{22}-g_{12}^2}$ 是主曲率乘积；**Theorema Egregium**（绝妙定理）断言 $K$ 只依赖 $g_{ij}$ 及其导数，与 $b_{ij}$（嵌入方式）无关——「内蕴」概念由此诞生。
  - **Gauss 方程**（环境 $\mathbb{R}^3$ 平坦时）：$\langle R(X,Y)Y,X\rangle=\langle\alpha(X,Y),\alpha(Y,X)\rangle-\langle\alpha(X,X),\alpha(Y,Y)\rangle$，把内蕴曲率 $R$ 与外蕴 $\alpha$（即 $b$）精确挂钩。
  - **测地线**是「测地曲率 $=0$」的曲线；**Gauss-Bonnet** $\int_M K\,dA=2\pi\chi(M)$ 把曲率积分锁定为拓扑不变量——Ch 5 同调论的第一个应用。
- **历史/动机**：Gauss（1827《关于曲面的一般研究》）发现 Theorema Egregium，催生 Riemann 的高维几何；测地线对应「最短路径」。
- **飞腾锚点**：**UDOT 16.9×[E05]** ⭐⭐ —— 面分与曲率积分是密集求和/点积累加。
  - 🟢事实：第一基本形式分量 $g_{ij}=\langle r_i,r_j\rangle$ 是点积缩并，面积 $\int\sqrt{\det g}\,du\,dv$ 是求和，UDOT 加速 16.9 倍。
  - 🟡类比：$K=\det(b)/\det(g)$ 是两个矩阵行列式之比；Gauss-Bonnet 的积分 = 加权点积求和。
- **几何/应用**：地图投影（保形/等积）的基础；测地线是 GPS 最短路径；$H=0$ 的极小曲面描摹肥皂膜。
- **关键定理**：$$\boxed{\text{Theorema Egregium：}K\text{ 由 }g_{ij}\text{ 及其一/二阶导数决定，与嵌入无关。}}\quad \int_M K\,dA=2\pi\chi(M).$$
  - Gauss 方程（$\mathbb{R}^3$ 平坦）：$R_{ijkl}=b_{ik}b_{jl}-b_{il}b_{jk}$。
- **自测**：半径 $a$ 的球面，$b_{ij}=\frac1a g_{ij}$，用 Gauss 方程推出 $K=1/a^2$；环面 $T^2$（$\chi=0$），Gauss-Bonnet 推 $\int K\,dA=0$，正负曲率区如何抵消？

---

### 第 3 章 · Tensors: The Algebraic Theory（张量代数）⭐

> 多线性映射 / 张量的变换律 / 张量积 $\otimes$ / 缩并 / 对称与反对称张量 / 外代数 $\Lambda^*$

- **核心**：本章是张量的纯代数奠基，为 Ch 4 的微分与 Ch 7 的相对论铺设符号语言。
  - 张量定义为多线性映射 $T:(V^*)^p\times V^q\to\mathbb{R}$，等价地由**变换律** $\tilde T^{i_1\cdots i_p}_{j_1\cdots j_q}=\frac{\partial\tilde x^{i_1}}{\partial x^{k_1}}\cdots\frac{\partial x^{l_q}}{\partial\tilde x^{j_q}}T^{k_1\cdots}_{\cdots l_q}$ 刻画。
  - **张量积** $\otimes$ 扩张类型；**缩并**（一对上下指标求和）降秩；迹 $\mathrm{tr}$ 是 $(1,1)$ 张量的缩并。
  - 度量 $g_{ij}$ 是 $(0,2)$ 张量，用于升降指标 $T^i=g^{ij}T_j$。
  - **外代数** $\Lambda^k V^*$ 由反对称化得到，$k$-形式是 Ch 5 de Rham 上同调与 Ch 10 示性类的代数载体。
- **历史/动机**：Ricci 与 Levi-Civita（1900）为微分几何发明绝对微分法；Einstein 学张量是为了写广义相对论。DFN 先讲代数再讲微分，符合物理学家学习路径。
- **飞腾锚点**：**matmul 15×[V03]** ⭐ —— 张量运算（积、缩并、升降指标）是密集多线性代数。
  - 🟢事实：$g^{ij}T_j$ 是矩阵-向量乘，$A^i_jB^j_k$ 是矩阵乘，tensor core 加速 15 倍；外积的反对称化是带符号的批量缩并。
  - 🟡类比：张量 = 多维数组 `ndarray`；缩并 = `einsum('ij,jk->ik')`；变换律 = 换基矩阵的双边作用。
- **几何/应用**：惯性张量（力学）、应力张量（弹性体）、Riemann 曲率张量（$R^l_{ijk}$，$(1,3)$ 型）都靠本章语言。
- **关键定理**：$$\text{变换律：}\tilde T^i_j=\frac{\partial\tilde x^i}{\partial x^k}\frac{\partial x^l}{\partial\tilde x^j}T^k_l;\quad \text{缩并降秩：}C^i_i=\mathrm{tr}(T).$$
- **自测**：证明度量 $g_{ij}$ 是 $(0,2)$ 张量（按变换律验证）；对 $(1,1)$ 张量 $T^i_j=\delta^i_j$，缩并得 $n$（维数）。

---

### 第 4 章 The Differential Calculus of Tensors（张量微分）⭐⭐

> 协变导数 $\nabla$ / Christoffel 符号 $\Gamma^k_{ij}$ / 联络 / 平行移动 / 测地线方程 / 曲率张量 $R^l_{ijk}$ / Levi-Civita 联络 / Bianchi 恒等式

- **核心**：本章把 Ch 3 的代数张量「微分化」——核心是让张量分量的导数仍是张量。
  - **协变导数** $\nabla_k T^{i\cdots}_{j\cdots}=\partial_k T^{i\cdots}_{j\cdots}+\Gamma^i_{km}T^{m\cdots}-\Gamma^m_{kj}T^{i\cdots}_{m\cdots}$（每指标一项 $\Gamma$，上正下负）。
  - **Christoffel 符号** $\Gamma^k_{ij}=\frac12 g^{kl}(\partial_i g_{jl}+\partial_j g_{il}-\partial_l g_{ij})$（Levi-Civita，度量唯一确定）。
  - **平行移动** $\nabla_{\dot\gamma}V=0$；**测地线** $\ddot x^k+\Gamma^k_{ij}\dot x^i\dot x^j=0$（自由粒子轨迹）。
  - **曲率张量** $R^l_{\ ij}^{\ k}V_k=(\nabla_i\nabla_j-\nabla_j\nabla_i)V^l$，即「协变导数不可交换的程度」——联络的不可积性。
  - **Bianchi 恒等式**（第一/第二）是曲率的代数与微分相容条件，是规范场方程的几何原型。
- **与 KN 对照**：KN 用主丛联络形式 $\omega$（Cartan），DFN 用分量 $\Gamma^k_{ij}$（Ricci），两者等价但 DFN 更接近物理学家与工程师的运算习惯。
- **历史/动机**：Christoffel（1869）引入 $\Gamma$；Levi-Civita（1917）定义平行移动；Einstein 用它写引力场方程。
- **飞腾锚点**：**GEMM 9.45G[Lab05]** ⭐⭐ —— $\Gamma$ 有 $n^3$ 分量，曲率张量有 $n^4$，缩并极密集。
  - 🟢事实：$R^l_{ijk}=\partial_i\Gamma^l_{jk}-\partial_j\Gamma^l_{ik}+\Gamma^l_{im}\Gamma^m_{jk}-\Gamma^l_{jm}\Gamma^m_{ik}$ 是四重求和，GEMM 每秒 9.45G 运算支撑实时计算。
  - 🟡类比：协变导数 = 「带修正项的梯度」（修正坐标弯曲）；曲率 = 「绕一圈标架旋转量」。
- **几何/应用**：广义相对论中测地线 = 自由下落；曲率 = 引力潮汐；机器学习自然梯度用 $\Gamma$ 修正参数空间。
- **关键定理**：$$R^l_{\ ij}^{\ k}V_k=(\nabla_i\nabla_j-\nabla_j\nabla_i)V^l;\quad \text{第二 Bianchi：}\nabla_{[m}R_{|ij|kl]}=0.$$
- **自测**：球面 $S^2$（$ds^2=d\theta^2+\sin^2\theta\,d\varphi^2$）算 $\Gamma^\varphi_{\theta\varphi}=\cot\theta$，验证赤道大圆是测地线；$\mathbb{R}^n$ 平坦 $g_{ij}=\delta_{ij}\Rightarrow\Gamma=0,R=0$。

---

### 第 5 章 · The Elements of Homology Theory（同调论基础）⭐

> 单纯复形 / 链群 $C_k$ / 边缘算子 $\partial$ / $\partial^2=0$ / 同调群 $H_k=\ker\partial_k/\mathrm{im}\,\partial_{k+1}$ / Betti 数 $b_k$ / Euler 示性数 $\chi=\sum(-1)^k b_k$ / de Rham 上同调

- **核心**：本章从几何走向拓扑——同调把「洞」计数化。
  - **单纯复形**把流形三角剖分；**链**是单形的整系数线性组合；**边缘算子** $\partial_k:C_k\to C_{k-1}$ 取边界。
  - 关键恒等式 $\partial^2=0$（边界的边界为空）$\Rightarrow\ker\partial_k\supset\mathrm{im}\,\partial_{k+1}$，定义**同调群** $H_k$（「闭但非边」的等价类）。
  - **Betti 数** $b_k=\dim H_k$：$b_0$=连通分量，$b_1$=独立环（隧道），$b_2$=封闭腔。
  - **Euler 示性数** $\chi=\sum(-1)^k b_k$ 是拓扑不变量——Gauss-Bonnet 把它与曲率积分挂钩（Ch 2）。
  - **de Rham 上同调** $H^k_{dR}=\ker d/\mathrm{im}\,d$（$d^2=0$ 的对偶版），**de Rham 定理** $H^k_{dR}(M)\cong H^k(M;\mathbb{R})$ 把微分形式与拓扑桥接。
- **历史/动机**：Poincaré（1895）创立同调；de Rham（1931）建立形式版。DFN 早期引入是为让 Ch 10 示性类（Chern-Euler 类）有落脚点。
- **飞腾锚点**：**分支预测[Lab02]** ⭐ —— 链复形是离散判定（是否闭/是否边），拓扑类型靠分支识别。
  - 🟢事实：分支预测命中 0.71 vs 失误 3.14 周期；同调计算（Smith 标准形）含大量「$\partial v=0$?」的判号分支，命中率影响算速。
  - 🟡类比：$\partial^2=0$ = 「边缘的边缘为空」的铁律（类比 Iron Law 的不可违背性）；同调类 = 「绕不出去的洞」的计数。
- **几何/应用**：Poincaré-Hopf 指标定理 $\sum\mathrm{ind}(p)=\chi(M)$（向量场奇点指标和=示性数）；数据拓扑分析（TDA）用持续同调检测点云的「形状」。
- **关键定理**：$$\boxed{\partial^2=0;\quad H^k_{dR}(M)\cong H^k(M;\mathbb{R})\text{（de Rham 定理）；}\quad \sum_p\mathrm{ind}_p(X)=\chi(M)\text{（Poincaré-Hopf）。}}$$
- **自测**：算 $S^2$ 的 $H_0=\mathbb{Z},H_1=0,H_2=\mathbb{Z}$，$\chi=2$；环面 $T^2$ 的 $H_1=\mathbb{Z}^2$，$\chi=0$；Poincaré 引理：$\mathbb{R}^n$ 上 $H^k_{dR}=0\,(k>0)$。

---

### 第 6 章 · Covariant Differentiation and the Lie Group（协变微分与 Lie 群）⭐⭐

> Lie 群 $G$ / Lie 代数 $\mathfrak{g}$（左不变向量场） / 指数映射 $\exp$ / Lie 三定理 / 伴随表示 $\mathrm{ad}$ / 双不变度量 / Killing 向量场（无穷小等距） / 齐性空间 $G/H$

- **核心**：本章把「变换群」（Ch 1 的 Erlangen）提升到连续（Lie）群。
  - **Lie 群** = 群 + 光滑流形（乘法/求逆光滑），如 $\mathrm{SO}(n),\mathrm{SU}(n),\mathrm{GL}(n)$。
  - **Lie 代数** $\mathfrak{g}=T_eG$ = 左不变向量场，带括号 $[X,Y]=XY-YX$（反称 + Jacobi）。
  - **指数映射** $\exp:\mathfrak{g}\to G$，$\exp(tX)$ 是 $X$ 的积分曲线（矩阵情形即矩阵指数）。
  - **Lie 第三定理**：Lie 子群 $\leftrightarrow$ Lie 子代数（一一对应），是「局部=全局」的桥梁。
  - **Killing 向量场**（无穷小等距，$\mathcal{L}_Xg=0$）生成等距群；其维数上界 $\frac{n(n+1)}2$（最大对称空间）。
  - **齐性空间** $G/H$（如球面 $S^n=\mathrm{SO}(n+1)/\mathrm{SO}(n)$）用群商描写对称流形。
- **历史/动机**：Lie（1880s）把 Galois 的离散对称推广到连续；Killing（1888）分类复单 Lie 代数。DFN 在此为 Ch 10 规范群（$G=SU(n)$ 等）铺垫。
- **飞腾锚点**：**Schmidt 正交化** ⭐⭐ —— 双不变度量 + 紧群的 Haar 测度与正交结构。
  - 🟢事实：紧 Lie 群上双不变度量使 $\exp$ 保内积（局部），伴随表示 $\mathrm{ad}_X$ 反称（$\langle\mathrm{ad}_X Y,Z\rangle=-\langle Y,\mathrm{ad}_X Z\rangle$），是连续正交化的代数对应。
  - 🟡类比：Lie 代数 = 群的「速度场」；指数映射 = 「速度积分成位移」；Killing 场 = 「对称方向」。
- **几何/应用**：规范对称（$SU(3)$ 色、$U(1)\times SU(2)$ 电弱）的数学语言；机器人运动学用 $\mathrm{SE}(3)$ Lie 群；等变神经网络用群对称性约束权重。
- **关键定理**：$$\boxed{\text{Lie 第三定理：}H<G\text{ Lie 子群}\Leftrightarrow\mathfrak h<\mathfrak g\text{ Lie 子代数。}}\quad \mathcal{L}_X g=0\text{（Killing 方程）。}$$
- **自测**：$\mathrm{SO}(3)$ 的 $\mathfrak{so}(3)$ 由三个反称矩阵生成，$[J_i,J_j]=\epsilon_{ijk}J_k$；球面 $S^2$ 上 Killing 场有 3 个（绕三轴旋转），达最大对称维数。

---

### 第 7 章 · The Metric Structure of Space-Time（时空度量结构）⭐⭐

> 伪 Riemann 几何 / Lorentz 度量（号差 $(-,+,+,+)$） / Minkowski 空间 / 光锥·类时/类空/类光 / 特殊相对论 / 广义相对论与 Einstein 方程

- **核心**：本章把 Riemann 度量（正定）推广到**不定**度量，几何直接变为物理。
  - **Minkowski 空间** $\mathbb{R}^{1,3}$，$ds^2=-c^2dt^2+dx^2+dy^2+dz^2$，号差 $(-,+,+,+)$。
  - **光锥**分时空为类时（$ds^2<0$，物质）、类光（$ds^2=0$，光）、类空（$ds^2>0$，不可达）三区——因果结构由此而来。
  - **特殊相对论**：Lorentz 变换是保 $ds^2$ 的线性变换（$G=\mathrm{O}(1,3)$），时间膨胀/长度收缩是推论。
  - **广义相对论**：时空是 4 维 Lorentz 流形 $(M,g_{\mu\nu})$，自由粒子走测地线，引力 = 曲率。
  - **Einstein 场方程** $R_{\mu\nu}-\frac12 Rg_{\mu\nu}+\Lambda g_{\mu\nu}=\frac{8\pi G}{c^4}T_{\mu\nu}$：物质能量动量 $T$ 决定时空曲率。
- **与 Ch 4 对照**：Ch 4 的联络/曲率在 Lorentz 度量下完全适用，只是号差改变符号约定；Levi-Civita 仍唯一（无挠+度量相容）。
- **历史/动机**：Minkowski（1908）把时间纳入几何；Einstein（1915）用 Riemann 几何写引力。DFN 的物理特色在此章最浓。
- **飞腾锚点**：**FP16 3.81×[L01]** ⭐⭐ —— 不定度量的数值稳定性要求保号差，半精度的可用性依赖度量的良好条件。
  - 🟢事实：Lorentz 度量有负特征值，数值上需小心符号（伪逆、特征值排序）；度量相容 $\nabla g=0$ 保证光锥结构沿测地线保持，FP16 吞吐 3.81 倍但需保号差稳定。
  - 🟡类比：正定度量 = 「距离总是正」的安全世界；不定度量 = 「距离可负可零」的相对论世界，因果锥是「不可逾越的边界」。
- **几何/应用**：GPS 钟差校正（引力红移+狭相效应，约 38 微秒/天）；黑洞（Schwarzschild 度量）、引力波、宇宙膨胀（FLRW 度量）。
- **关键定理**：$$\boxed{ds^2=-c^2dt^2+d\mathbf{x}^2;\quad R_{\mu\nu}-\tfrac12Rg_{\mu\nu}+\Lambda g_{\mu\nu}=\tfrac{8\pi G}{c^4}T_{\mu\nu}\text{（Einstein 方程）。}}$$
- **自测**：写 Schwarzschild 度量 $ds^2=-(1-\frac{2GM}{c^2r})c^2dt^2+(1-\frac{2GM}{c^2r})^{-1}dr^2+r^2d\Omega^2$，求视界 $r_s=2GM/c^2$；验证 Minkowski 平坦（$g_{\mu\nu}=\eta_{\mu\nu}\Rightarrow R=0$）。

---

### 第 8 章 · The Calculus of Variations and Geometric Optics（变分法与几何光学）⭐

> 泛函 $S[\gamma]=\int L\,dt$ / Euler-Lagrange 方程 / 测地线为长度/能量极值 / Fermat 原理 / Hamilton 正则方程 / Hamilton-Jacobi 方程 / 几何光学与波前

- **核心**：本章把「极值」与「几何」绑定——许多几何对象是变分问题的解。
  - **Euler-Lagrange 方程** $\frac{d}{dt}\frac{\partial L}{\partial\dot q}-\frac{\partial L}{\partial q}=0$ 是泛函极值的必要条件。
  - **测地线**是弧长泛函 $\int\sqrt{g_{ij}\dot x^i\dot x^j}\,dt$ 或能量泛函 $\int g_{ij}\dot x^i\dot x^j\,dt$ 的极值——Ch 4 测地线方程的变分来源。
  - **Fermat 原理**（$\delta\int n\,ds=0$，$n$=折射率）导出光线方程；**eikonal 方程** $|\nabla S|^2=n^2$ 是几何光学的核心。
  - **Hamilton 正则方程** $\dot q=\partial H/\partial p,\ \dot p=-\partial H/\partial q$；**Hamilton-Jacobi** 把动力学归约为一个一阶 PDE。
  - **Legendre 变换**连结 Lagrange 量 $L(q,\dot q)$ 与 Hamilton 量 $H(q,p)$——Ch 9 辛几何的入口。
- **历史/动机**：Euler/Lagrange（1750s）奠基变分；Hamilton（1834）重构力学；Fermat/Huygens 用变分统一光学。DFN 用此章为 Ch 9 可积系统与力学几何化铺路。
- **飞腾锚点**：**Iron Law<2%[Lab00]** ⭐ —— 变分极值的数值求解依赖误差控制铁律。
  - 🟢事实：性能=指令数×CPI×时钟，优化算法的迭代收敛误差必须 <2% 才算稳定；变分法的离散化（有限元/差分）误差控制同此铁律。
  - 🟡类比：极值条件 $\delta S=0$ = 「梯度的精度门」；数值变分中误差累积会偏离真极值，需 Iron Law 约束步长。
- **几何/应用**：最速降线（brachistochrone=摆线）；最小作用量原理是整个物理学的变分基础；最优控制（Pontryagin 极大值原理）是其推广。
- **关键定理**：$$\boxed{\frac{d}{dt}\frac{\partial L}{\partial\dot q^i}-\frac{\partial L}{\partial q^i}=0\text{（Euler-Lagrange）；}\quad \delta\int n\,ds=0\text{（Fermat）。}}$$
- **自测**：用变分法推导球面测地线是大圆（取 $L=\dot\theta^2+\sin^2\theta\,\dot\varphi^2$）；brachistochrone 在均匀重力下是摆线参数方程 $x=a(\theta-\sin\theta),y=a(1-\cos\theta)$。

---

### 第 9 章 · Geometric Theory of Differential Equations（微分方程的几何理论）⭐

> 向量场与流 / 一阶 PDE 的特征线法 / 一阶偏微分方程 / Hamilton-Jacobi / 辛结构 $\omega$ / Poisson 括号 / 完全可积系统（Liouville 定理）/ Frobenius 可积性

- **核心**：本章把 PDE「几何化」——方程的解空间是流形上的几何对象。
  - **向量场** $X$ 的积分曲线（流 $\phi_t$）是一阶 ODE $\dot x=X(x)$ 的解；**特征线法**把一阶 PDE $a^i\partial_i u=f$ 归约为沿 $a$ 的 ODE。
  - **辛流形** $(M^{2n},\omega)$，$\omega=dp_i\wedge dq^i$；Hamilton 流 $\dot q=\partial H/\partial p,\dot p=-\partial H/\partial q$ 保 $\omega$（Liouville 定理：相体积不变）。
  - **Poisson 括号** $\{f,g\}=\omega(X_f,X_g)$ 使函数成 Lie 代数；**完全可积**（$n$ 个对合首次积分）$\Rightarrow$ 解可显式（Arnold-Liouville 定理，作用-角变量）。
  - **Frobenius 定理**（分布可积 $\Leftrightarrow$ 闭于括号）统一特征线法与叶状结构。
- **历史/动机**：Hamilton/Jacobi 几何化力学；Arnold（DFN 同时代的俄罗斯学派巨匠）的《经典力学的数学方法》深化此章；Novikov 本人对可积系统（KdV）有奠基贡献。
- **飞腾锚点**：**UDOT 16.9×[E05]**（复用，不同角度）—— 流的数值积分与辛格式是密集求和。
  - 🟢事实：辛 Euler/Runge-Kutta 格式保 $\omega$（避免能量漂移），每步是点积累加，UDOT 加速 16.9 倍；作用-角变量下的可积流是 FFT 友好的线性旋转。
  - 🟡类比：特征线 = 「信息沿向量场流动」；辛结构 = 「相空间体积的守恒铁律」；可积 = 「可对角化为独立振子」。
- **几何/应用**：辛数值积分（分子动力学保能量）；KAM 定理（近可积系统的稳定性）；几何力学（刚体、流体）。
- **关键定理**：$$\boxed{\text{Liouville 完全可积：}n\text{ 个对合首次积分}\Rightarrow\text{作用-角变量，解为准周期。}}\quad \phi_t^*\omega=\omega\text{（Hamilton 流保辛）。}$$
- **自测**：谐振子 $H=\frac12(p^2+\omega^2q^2)$，作用 $I=H/\omega$，角 $\theta=\omega t$，验证可积；用特征线法解输运方程 $u_t+cu_x=0$（解沿 $x-ct=\text{const}$）。

---

### 第 10 章 · Lie Algebras, Cohomologies, and Gauge Fields（Lie 代数、上同调与规范场）⭐⭐

> Lie 代数上同调 / de Rham 上同调（复习） / 示性类（Chern·Euler·Pontryagin） / Chern-Weil 理论 / 主丛上的联络 / Yang-Mills 方程 / 规范场的拓扑荷

- **核心**：本章是全书的物理-几何-拓扑大综合，把 Ch 4 联络、Ch 5 同调、Ch 6 Lie 群汇流到规范场论。
  - **Lie 代数上同调** $H^*(\mathfrak g)$ 用 Chevalley-Eilenberg 复形（$d\alpha(X_0,\ldots,X_k)=\sum(-1)^i\alpha([X_i,\ldots])$）度量代数的「洞」。
  - **Chern-Weil 理论**：从联络的曲率 $\Omega$ 构造闭形式（如 $\mathrm{tr}(\Omega\wedge\cdots\wedge\Omega)$），其 de Rham 类即**示性类**（Chern 类、Euler 类、Pontryagin 类）——拓扑不变量的几何实现。
  - **规范场** = 主丛 $P(M,G)$ 上的联络（Ch 4 的物理版），结构群 $G=U(1)$（电磁）、$SU(2)$（电弱）、$SU(3)$（色）、$SU(n)$（Yang-Mills）。
  - **Yang-Mills 方程** $D^{\mu}F_{\mu\nu}=J_\nu$（协变散度=源）+ Bianchi $D_{[\mu}F_{\nu\rho]}=0$（齐次），是 Maxwell 方程的非交换推广。
  - **拓扑荷**：瞬子数（第二 Chern 类积分）、磁单极荷（第一 Chern 类）由示性类给出——「物理守恒量=拓扑不变量」。
- **与 Ch 4/5/6 对照**：Ch 4 给联络/曲率，Ch 5 给上同调语言，Ch 6 给 Lie 群/代数——三者在 Ch 10 合一为规范几何。这与 Kobayashi-Nomizu 卷 II 的示性类理论遥相呼应。
- **历史/动机**：Yang-Mills（1954）推广 Maxwell；Chern（1940s）/Weil 用微分形式实现示性类；Donaldson（1983）用 Yang-Mills 瞬子分类 4 维流形拓扑（Fields 奖）。Novikov 在规范场拓扑方面有重要贡献。
- **飞腾锚点**：**matmul 15×[V03]**（复用，不同角度）—— 规范势 $A_\mu$ 是取值 Lie 代数的矩阵，结构群表示是密集矩阵运算。
  - 🟢事实：$G=SU(n)$ 的规范势 $A_\mu=A_\mu^a T_a$（$T_a$ 是 $\mathfrak{su}(n)$ 的 $n\times n$ 反 Hermite 基），曲率 $F=dA+A\wedge A$ 含矩阵乘 $A\wedge A$，tensor core 加速 15 倍；格点规范理论的 Monte Carlo 是海量 GEMM。
  - 🟡类比：规范变换 $A\mapsto g^{-1}Ag+g^{-1}dg$ = 「换标架」；规范不变量 = Erlangen 不变量的无穷维版；瞬子 = 「规范场的拓扑纽结」。
- **几何/应用**：标准模型（$SU(3)\times SU(2)\times U(1)$）；规范/引力统一（Kaluza-Klein、弦论）；拓扑量子计算（任意子辫子群）；几何深度学习中的等变/规范等变网络。
- **关键定理**：$$\boxed{D^\mu F_{\mu\nu}=J_\nu\text{（Yang-Mills）；}\quad D_{[\mu}F_{\nu\rho]}=0\text{（Bianchi）；}\quad c_k=\Bigl[\mathrm{tr}\bigl(\tfrac{i}{2\pi}\Omega\bigr)^k\Bigr]\in H^{2k}_{dR}\text{（Chern-Weil）。}}$$
- **自测**：$U(1)$ 退化：$A_\mu$ 是普通 1-形式，$F_{\mu\nu}=\partial_\mu A_\nu-\partial_\nu A_\mu$，Yang-Mills 退化为 Maxwell；$SU(2)$ BPST 瞬子 $A_\mu=\frac{2}{x^2+\rho^2}\eta_{\mu\nu}x^\nu\sigma$（'t Hooft 符号），第二 Chern 数 $=1$。

---

## §9 全书思想主线（约 220 字）

Dubrovin-Fomenko-Novikov 全书有一条贯穿的主线：**以「变换群」为骨、「曲率↔拓扑」为血、「物理应用」为肉**。这条线沿着「平面变换（Ch 1）→ 曲面内蕴几何（Ch 2）→ 张量代数（Ch 3）→ 张量微分/联络（Ch 4）→ 同调/拓扑（Ch 5）→ Lie 群（Ch 6）→ 时空度量（Ch 7）→ 变分/光学（Ch 8）→ PDE/可积（Ch 9）→ 规范场（Ch 10）」展开。

DFN 与 Kobayashi-Nomizu 的根本区别在于**抽象层次与物理浓度**：
KN 用最抽象的主丛联络形式 $\omega$ 统一一切，纯数学百科；
DFN 用张量分量 $\Gamma^k_{ij}$（Ricci 路线）讲联络，每章直指一个物理出口——
Ch 7 时空度量即广义相对论，Ch 8 变分即光学路径，Ch 10 规范场即 Yang-Mills。
与 Lee 三件套对照：Lee 是最友好的纯数学自学路径，DFN 则是「数学家与物理学家共读」的应用导向蓝本。
与 Spivak 5 卷对照：Spivak 以历史叙事最详尽，DFN 以拓扑-物理融合最紧凑。

三条红线在 Ch 10 汇流：变换群（规范群 $G$）、曲率↔拓扑（Chern-Weil 示性类）、几何↔物理（标准模型）——
「整体不变量由局部几何积分给出」这一信念，从 Gauss-Bonnet（Ch 2/5）到 Chern 类（Ch 10）一脉相承。
Poincaré-Hopf 指标定理（向量场奇点和=示性数）与 Gauss-Bonnet 同源，是「局部→整体」的典范。

---

## §10 与本仓库其他笔记的交叉引用

**与 Kobayashi-Nomizu《微分几何基础》对比**(stage-2 刚做)：
KN = 主丛联络形式(Cartan)，最抽象，纯数学百科；
DFN = 张量分量(Ricci) + 物理应用，跨度更大。
KN Ch II（主丛联络/结构方程）$\leftrightarrow$ DFN Ch 4（协变导数）+ Ch 10（规范场）；
KN Ch IV（Levi-Civita）$\leftrightarrow$ DFN Ch 4；
KN Ch VI（Gauss 方程）$\leftrightarrow$ DFN Ch 2。
建议：DFN Ch 4 先读建立分量运算直觉，KN Ch II 再读补主丛抽象框架；DFN Ch 10 与 KN 卷 II 示性类配套。

**与 Lee 三件套对比**(stage-2 已读)：
Lee GTM218（光滑流形）给 DFN Ch 1-4 的严格现代基础；
Lee GTM202（拓扑流形）给 DFN Ch 5 同调的友好版；
Lee GTM176（黎曼流形）给 DFN Ch 2/4 的可手算细节。
DFN 的物理章（Ch 7/8/9/10）是 Lee 系列没有的特色。

**与 Bott-Tu《微分形式》GTM82 对比**(stage-2 已读)：
DFN Ch 5 的 de Rham 上同调 + Ch 10 的 Chern-Weil 示性类
是 Bott-Tu de Rham 理论在「带联络的主丛」上的应用。
建议 Bott-Tu Ch 1（de Rham）+ DFN Ch 5/10 配套读。

**与 do Carmo《黎曼几何》对比**(stage-2 已读)：
do Carmo Ch 2（Levi-Civita/Koszul）$\leftrightarrow$ DFN Ch 4；
do Carmo Ch 4（曲率）$\leftrightarrow$ DFN Ch 2/4；
do Carmo Ch 10（Bonnet-Myers）$\leftrightarrow$ DFN Ch 2（Gauss-Bonnet）。
do Carmo 证明可手算，DFN 物理动机更强。

**与 Spivak《微分几何》5 卷对比**(stage-2 已读)：
Spivak 卷 II-III（曲面理论）$\leftrightarrow$ DFN Ch 1-2；
Spivak 卷 IV-V（规范理论/物理）$\leftrightarrow$ DFN Ch 7/10。
Spivak 历史叙事最详尽，DFN 最紧凑实用。

**AI 锚点（数学 ↔ 工程）**：

- 🟢 **规范场 = 等变/规范等变神经网络**：DFN Ch 10 的主丛联络（结构群 $G$ 作用于特征空间）是规范等变网络（Gauge Equivariant NN）的数学原型；$G=SO(3)$ 等变 CNN 用于分子/蛋白质结构预测。Yang-Mills 方程的「协变性」= 权重共享的对称约束。
- 🟢 **时空度量 = 相对论性机器学习**：DFN Ch 7 的 Lorentz 几何用于物理信息神经网络（PINN）求解 Einstein 方程；双曲嵌入（Poincaré 球）用负曲率几何表示层次数据，与 DFN Ch 2 的常曲率空间形式同源。
- 🟢 **变分法 = 优化与最优控制**：DFN Ch 8 的 Euler-Lagrange 是所有梯度下降的连续原型；最优控制（强化学习的 Pontryagin 原理）是其推广；测地线（变分极值）= 自然梯度法的参数空间最短路径。
- 🟢 **同调 = 拓扑数据分析（TDA）**：DFN Ch 5 的同调群是 TDA（持续同调）检测点云「洞」的理论基础；用于材料微观结构、神经网络损失景观的拓扑特征提取；Poincaré-Hopf 定理解释向量场（梯度场）奇点与数据拓扑的关系。
- 🟡 **可积系统 = 可解释动力学**：DFN Ch 9 的 Liouville 可积（作用-角变量）类比神经ODE 的可解结构；KAM 定理（近可积稳定性）为扰动下的训练稳定性提供几何直觉；辛数值积分保相体积，对应保结构的神经网络设计。
- 🟡 **变换群 = 对称性约束学习**：DFN 全书主轴的「几何=群的不变量」直接落地为等变机器学习（深度对称网络）：用群对称性减少参数、提升样本效率，从卷积（平移群）到球面 CNN（旋转群）到规范等变网络（规范群）。

---

## §11 自测答案要点（供核对）

1. **Ch 1** 极坐标 $x=r\cos\theta,y=r\sin\theta$，$dx=\cos\theta\,dr-r\sin\theta\,d\theta$，$dy=\sin\theta\,dr+r\cos\theta\,d\theta$，$ds^2=dx^2+dy^2=dr^2+r^2d\theta^2$ ✓。$w=z^2$，$dw=2z\,dz$，$z\neq0$ 时 $dw\neq0$，保角（共形）✓。
2. **Ch 2** 球面 $b_{ij}=\frac1a g_{ij}$，Gauss 方程 $R_{ijkl}=b_{ik}b_{jl}-b_{il}b_{jk}=\frac1{a^2}(g_{ik}g_{jl}-g_{il}g_{jk})$，截面曲率 $K=\frac1{a^2}$ ✓。环面 $\chi=0\Rightarrow\int K\,dA=0$，外环面 $K>0$（外凸）、内环面 $K<0$（内凹鞍），正负抵消 ✓。
3. **Ch 3** $g_{ij}=\langle\partial_i,\partial_j\rangle$，换基 $\tilde\partial_i=\frac{\partial x^k}{\partial\tilde x^i}\partial_k$，$\tilde g_{ij}=\frac{\partial x^k}{\partial\tilde x^i}\frac{\partial x^l}{\partial\tilde x^j}g_{kl}$ ✓（$(0,2)$ 张量）。$\delta^i_i=n$ ✓。
4. **Ch 4** 球面 $\Gamma^\varphi_{\theta\varphi}=\frac12 g^{\varphi\varphi}\partial_\theta g_{\varphi\varphi}=\frac{1}{2\sin^2\theta}\cdot2\sin\theta\cos\theta=\cot\theta$ ✓。赤道 $\theta=\pi/2$，$\dot\theta=0$，测地线方程 $\ddot\theta+\sin\theta\cos\theta\,\dot\varphi^2=0$ 满足，$\varphi$ 线性 $\Rightarrow$ 大圆 ✓。$\mathbb{R}^n$：$g_{ij}=\delta_{ij}\Rightarrow\Gamma^k_{ij}=0\Rightarrow R=0$ ✓。
5. **Ch 5** $S^2$：$b_0=1$（连通），$b_1=0$（无环），$b_2=1$（封闭球面），$\chi=1-0+1=2$ ✓。$T^2$：$b_0=1,b_1=2$（两环），$b_2=1$，$\chi=1-2+1=0$ ✓。Poincaré 引理：$\mathbb{R}^n$ 上闭形式 $\alpha=d\beta$（星形域），$H^k_{dR}=0\,(k>0)$ ✓。
6. **Ch 6** $\mathfrak{so}(3)$：$(J_i)_{jk}=-\epsilon_{ijk}$，$[J_i,J_j]=\epsilon_{ijk}J_k$ ✓。$S^2$：$\dim\mathrm{SO}(3)=3$，$\dim\mathrm{SO}(2)=1$（稳定子），$\dim S^2=3-1=2$ ✓，3 个 Killing 场达最大对称 $\frac{n(n+1)}2=\frac{2\cdot3}2=3$ ✓。
7. **Ch 7** Schwarzschild：$g_{tt}=-(1-\frac{2GM}{c^2r})$，视界 $g_{tt}=0\Rightarrow r_s=\frac{2GM}{c^2}$ ✓。Minkowski：$g_{\mu\nu}=\eta_{\mu\nu}$ 常数 $\Rightarrow\Gamma=0\Rightarrow R=0$ 平坦 ✓。
8. **Ch 8** 球面 $L=g_{ij}\dot x^i\dot x^j=\dot\theta^2+\sin^2\theta\,\dot\varphi^2$，Euler-Lagrange $\theta$ 分量 $\ddot\theta-\sin\theta\cos\theta\,\dot\varphi^2=0$（与 Ch 4 测地线一致），$\varphi$ 守恒 $\frac{d}{dt}(\sin^2\theta\,\dot\varphi)=0$ ✓。Brachistochrone $T=\int\frac{ds}{v}=\int\frac{\sqrt{1+y'^2}}{\sqrt{2gy}}dx$，Euler-Lagrange 给摆线 ✓。
9. **Ch 9** 谐振子 $H=\frac12(p^2+\omega^2q^2)$，作用 $I=H/\omega$（守恒），角 $\theta=\omega t+\theta_0$，可积（1 自由度必有 1 个对合积分）✓。输运 $u_t+cu_x=0$，特征 $x-ct=\text{const}$，$u(x,t)=u_0(x-ct)$ ✓。
10. **Ch 10** $U(1)$ 交换：$A\wedge A=0$，$F_{\mu\nu}=\partial_\mu A_\nu-\partial_\nu A_\mu$，$D^\mu F_{\mu\nu}=\partial^\mu F_{\mu\nu}=J_\nu$（Maxwell）✓。Bianchi $\partial_{[\mu}F_{\nu\rho]}=0$（$\nabla\cdot\mathbf{B}=0,\nabla\times\mathbf{E}+\partial_t\mathbf{B}=0$）✓。BPST 瞬子第二 Chern 数 $c_2=\frac1{8\pi^2}\int\mathrm{tr}(F\wedge F)=1$ ✓。

> **核对原则**：每题的核心是「张量分量语言 ↔ 物理方程」的翻译。Ch 1-4 属「奠基」（几何+张量），Ch 5-6 属「拓扑+对称」，Ch 7-10 属「物理应用」。DFN 的特色是 Ch 7-10 把前六章的几何直接变成物理理论——时空、光学、可积系统、规范场，每一章都是「数学↔物理」的双向通道。

---

> **下一步**：沿 `01-track/stage-2` 精读 DFN Ch 2（Theorema Egregium + Gauss-Bonnet，全书第一个「曲率↔拓扑」见证）+ Ch 4（协变导数，与 do Carmo Ch2/KN ChIV 对照三种语言）+ Ch 10（规范场，全书物理-几何-拓扑大综合，需 Bott-Tu 配合）。
>
> **stage-3 前瞻**：Arnold《经典力学的数学方法》（辛几何深化 Ch 9）→ Donaldson 4 维拓扑（Yang-Mills 瞬子，Ch 10）→ Ricci 流（Perelman）→ 弦论/镜像对称（Calabi-Yau，Ch 7/10 的前沿）。
>
> **实操验证**(建议用 Python/SciPy)：
> - 球面 Christoffel 符号计算（Ch 4）→ 验证赤道大圆是测地线
> - `numpy.einsum` 实现曲率张量 $R^l_{ijk}$（Ch 4）→ 验证 $S^2$ 的 $K=1$
> - 单纯同调计算（Ch 5）→ 用 `gudhi`/`ripser` 算 $S^2/T^2$ 的 Betti 数
> - Schwarzschild 测地线数值积分（Ch 7）→ 验证行星轨道近日点进动
> - $U(1)$ 规范场 $F=dA$ 数值验证（Ch 10）→ 退化 Maxwell 方程
> - 辛 Euler 格式积分谐振子（Ch 9）→ 验证能量守恒（对比普通 Euler 的能量漂移）
