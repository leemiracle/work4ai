# do Carmo《黎曼几何》(1992) · 快速逐章精读

> 基于原书：Riemannian Geometry, Manfredo P. do Carmo, Birkhäuser, 1992 (英译版) / 读于：2026-07-02
> 定位：**黎曼几何经典入门教材**，以局部理论+整体定理为主线，从度量到曲率到比较定理，一切证明可手算。
> 本文为**快速逐章精读**，每章 1 个飞腾锚点 + 1 个关键定理 + 1 道自测题。
> 前置：do Carmo《曲线与曲面的微分几何》(stage-2 已读，ch4-5 内蕴几何=本书入口)；Munkres 拓扑(紧致/覆叠)；线性代数(LADR)。

---

## §0 引言：do Carmo 是什么，为什么读它

do Carmo《黎曼几何》(1992) 是 stage-2 几何主线的**经典入门教材**，衔接自然：上接作者本人的《曲线与曲面的微分几何》(stage-2 已读，其 ch4「第一基本形式 / Theorema Egregium」与 ch5「抽象曲面」即黎曼度量的二维雏形)，本书把一切推广到**任意维光滑流形**——给 $n$ 维流形 $M$ 配上黎曼度量 $g$，用 Levi-Civita 联络 $\nabla$ 做微分，用曲率张量 $R$ 刻画几何，最终回答「曲率如何控制拓扑」。

**do Carmo 的独特价值**：这是一本「证明可手算」的书。Levi-Civita 联络从 Koszul 公式一步步推出，Jacobi 方程的解在球面/双曲面上逐项验证，第二基本形式与 Gauss 方程的每一步缩并都不跳步。对零基础补课的工程师，这意味着不需要先读 Lee 或 Petersen 来「补背景」——do Carmo 自包含，从流形回顾(度量/切丛/向量场)讲起。全书不含收敛理论(GH 距离 / Cheeger-Colding)，但**局部理论与基础比较定理的覆盖深度超过 Petersen**——Jacobi 场的变分刻画、Morse 指数定理、等距浸入的 Gauss/Codazzi 方程都给出完整证明。

**核心命题**：全书沿着「度量 $\to$ 联络 $\to$ 测地线 $\to$ 曲率 $\to$ 变分 $\to$ 比较」的逻辑链展开。曲率分三层——截面 $K$（最精细）、Ricci $\mathrm{Ric}$（体积增长率）、标量 $\mathrm{scal}$（平均），每一层都对应一组比较定理：Bonnet-Myers（正 Ricci $\to$ 紧致）、Cartan-Hadamard（负截面 $\to$ 指数映射微分同胚）。do Carmo 把这些定理证明到「能用」的程度，为 Petersen GTM171(现代比较几何)与 Jost(几何分析)铺路。

| 书 | 风格 | 主线侧重 | 适合谁 |
|---|---|---|---|
| **do Carmo** 黎曼几何 (1992) | 经典巴西学派，证明详尽可手算 | 局部理论+基础比较+子流形，不含收敛 | 第一门课，需要逐行验证 |
| **Petersen** GTM171 (2016) | 现代比较几何，按曲率类型分层 | 比较定理为核心(Ch5-7)，含 GH 收敛(Ch9) | 研究导向，进现代几何分析 |
| **Lee** GTM176 (2nd 2018) | 极度友好，自学者最佳，递归式铺垫 | 基础+几何直觉，覆盖到 Jacobi 场与比较 | 自学零基础，怕抽象 |
| **Jost** 黎曼几何与几何分析 (7th 2017) | PDE/几何分析融合，物理味重 | 调和映射/Yang-Mills/极小曲面 | 想做几何分析/数学物理 |

**建议路线**：do Carmo 先读(经典+可手算) → Petersen 补比较几何纵深 → Jost 攻几何分析。与 do Carmo《曲线与曲面》ch4(内蕴几何)、ch5(整体/抽象) 直接衔接。

**零基础工程师阅读建议**：第 1-3 章是「甜区」——只需多元微积分(Spivak stage-1)与线性代数(LADR stage-1)，务必手算每一个度量与 Christoffel 符号(球面 $S^2$、双曲平面 $\mathbb{H}^2$ 是标准习题)。第 4-5 章引入曲率与 Jacobi 场，建议配合 `scipy.integrate.solve_ivp` 数值解测地线方程来建立直觉。第 7-8 章(变分+Morse 指数)是全书的「分析硬核」，建议纸笔画第二变分的符号变化。第 9-10 章(比较定理)是 payoff——曲率条件直接钉死拓扑。全书精读约 70-90 小时(每周 10-20h，5-9 周)。

> 🟢 事实可作锚点：Levi-Civita 基本定理、Hopf-Rinow、Bonnet-Myers、Cartan-Hadamard、Morse 指数定理均为严格定理。
> 🟡 类比（度量=「曲面居民的尺子」、曲率=「空间的弹簧」）仅供直觉，**绝不在严格证明中引用**。

**章号说明**：原书 Birkhäuser 版分约 11 章正文章节 + 附录。本文按主题重组为 13 章以便精读：将「测地线」(原 Ch3)与「完备/Hopf-Rinow」(原 Ch7)合并为本文 Ch3，将「等距浸入」(原 Ch6)拆为基础(Ch6 第二基本形式)与进阶(Ch11 Gauss 方程)，增补「共形/Killing 场」(原附录/散见各章)为 Ch13。各章标题保留英文原名以方便查阅原书。

---

## §1 全书 13 章骨架一览

| 章 | 标题 | 核心概念 | 飞腾锚点 |
|---|---|---|---|
| 1 | 黎曼度量 | 度量 $g$、距离 $d(p,q)$、度量存在性 | **TLB 4.81×[E04]** ⭐主力 |
| 2 | 仿射联络; Levi-Civita | 联络 $\nabla$、挠率、Koszul 公式 | **Schmidt 正交化** ⭐ |
| 3 | 测地线; 完备; Hopf-Rinow | 测地线方程、$\exp_p$、Gauss 引理、完备性 | **FP16 3.81×[L01]** |
| 4 | 曲率 | $R$、截面 $K$、Ricci、标量、Bianchi | **matmul 15×[V03]** |
| 5 | Jacobi 场; 共轭点 | Jacobi 方程、$\exp_p$ 退化、最短临界 | **UDOT 16.9×[E05]** |
| 6 | 等距浸入; 第二基本形式 | $\alpha(X,Y)$、Gauss 公式、极小子流形 | **GEMM 9.45G[Lab05]** |
| 7 | 变分 | 能量泛函、第一/第二变分、指标形式 | **UDOT 16.9×[E05]** |
| 8 | Morse 指数 | 指标定理、共轭点计数、稳定/不稳定 | **Iron Law <2%[Lab00]** |
| 9 | Synge; 基本群 | 正曲率约束 $\pi_1$、定向性 | **分支预测[Lab02]** |
| 10 | Bonnet-Myers; Hadamard | 正 Ricci→紧致、负截面→微分同胚 | **Iron Law <2%[Lab00]** |
| 11 | 子流形; Gauss 方程 | Gauss/Codazzi 方程、曲率关系 | **matmul 15×[V03]** |
| 12 | 空间形式 | 常曲率分类 $\mathbb{R}^n$/$S^n$/$\mathbb{H}^n$ | **Schmidt 正交化** ⭐ |
| 13 | 共形; Killing 场 | 共形变换 $\lambda^2 g$、Killing 方程 | **TLB 4.81×[E04]** ⭐主力 |

**两条主线**：(1) **曲率分层**——截面 $K$(Ch4,9,10) → Ricci(Ch10) → 标量，曲率越弱结论越微妙、工具越深；(2) **变分→比较范式**——能量泛函(Ch7) → Jacobi 场(Ch5) → Morse 指数(Ch8) → 比较定理(Ch9,10)，测地线稳定性是全书引擎。

---

### 第 1 章 · Riemannian Metrics（黎曼度量）⭐

> 流形回顾(切丛/向量场) / 度量定义 / 距离 / Riemannian immersion & submersion / 度量存在性(单位分解)

- **核心**：**黎曼度量** $g$ 是切丛 $TM$ 的光滑截面，每点 $p$ 给出 $T_pM$ 上的正定对称双线性型 $g_p$。局部坐标 $g=\sum g_{ij}\,dx^i\otimes dx^j$，$(g_{ij})$ 正定。有了 $g$，曲线 $\gamma$ 有长度 $L(\gamma)=\int_a^b|\dot\gamma|\,dt$，**黎曼距离** $d(p,q)=\inf_{\gamma:p\to q}L(\gamma)$。$d$ 使 $M$ 成度量空间，度量拓扑=流形拓扑；单位分解保证任何光滑流形均可配度量。
- **飞腾锚点**：**TLB 4.81×[E04]** ⭐主力 —— 流形只有局部坐标卡，度量的局部性 = 内存局部性。
  - 🟢事实：TLB 命中率高时内存访问快 4.81 倍；$g_{ij}$ 是 $n\times n$ 对称正定矩阵，逐点存储命中缓存。
  - 🟡类比：坐标卡的转移函数 = 内存页表的 TLB 映射切换；「流形=流数据」，跨卡拼接需换映射。
- **几何/应用**：广义相对论中时空=洛伦兹流形(伪黎曼度量号差 $(-,+,+,+)$)，$g_{\mu\nu}$ 即引力势；流形学习(Isomap)用图最短路估计 $d(p,q)$ 反推低维度量。
- **关键定理**：$$\text{任何仿紧 Hausdorff 光滑流形 } M \text{ 上存在 Riemannian 度量(单位分解拼接局部欧氏度量)。}$$
- **自测**：写出球面 $S^2$ 在球坐标 $(\theta,\varphi)$ 下的 $g=d\theta^2+\sin^2\theta\,d\varphi^2$；验证 $d(p,q)=\inf$ 大圆弧长。

---

### 第 2 章 · Affine Connections; Riemannian Connections（仿射联络; Levi-Civita 联络）⭐⭐

> 仿射联络 $\nabla$ / 挠率张量 $T$ / Levi-Civita 基本定理 / Koszul 公式 / Christoffel 符号 / 平行移动

- **核心**：**仿射联络** $\nabla$（$TM$ 上的协变导数）使流形上能对向量场求导。一般联络有**挠率** $T(X,Y)=\nabla_X Y-\nabla_Y X-[X,Y]$。**Levi-Civita 基本定理**：度量 $g$ 唯一确定无挠($T=0$)且度量相容($\nabla g=0$)的联络，Koszul 公式给出显式 Christoffel 符号 $\Gamma_{ij}^k=\tfrac12 g^{kl}(\partial_i g_{jl}+\partial_j g_{il}-\partial_l g_{ij})$。平行移动 $\nabla_{\dot\gamma}V=0$ 沿曲线搬运向量，保内积。
- **飞腾锚点**：**Schmidt 正交化** ⭐ —— 无挠+度量相容 = 平行移动保持内积 = 标架连续正交化。
  - 🟢事实：Schmidt 正交化保证平行移动的基保持正交，坐标变换不引入混叠。
  - 🟡类比：Frenet 标架(do Carmo《曲线与曲面》ch1)是沿曲线的正交化；Levi-Civita 联络是其流形推广。
- **几何/应用**：测地线方程就是 $\nabla_{\dot\gamma}\dot\gamma=0$；自然梯度法用 Levi-Civita 联络修正参数空间的梯度方向。
- **关键定理**：$$\text{Levi-Civita 基本定理：度量 } g \text{ 唯一确定无挠度量相容联络 } \nabla\text{（Koszul 公式给出表达）。}$$
- **自测**：用 Koszul 公式验证欧氏空间($g=\delta_{ij}$)的 $\Gamma_{ij}^k\equiv0$；写出 $S^2$ 的 Christoffel 符号并验证赤道是测地线。

---

### 第 3 章 · Geodesics; Completeness; Hopf-Rinow（测地线; 完备; Hopf-Rinow）⭐⭐⭐

> 测地线方程 / 指数映射 $\exp_p$ / Gauss 引理 / 凸邻域 / 测地完备与度量完备

- **核心**：**测地线** $\nabla_{\dot\gamma}\dot\gamma=0$，坐标下 $\ddot\gamma^k+\Gamma_{ij}^k\dot\gamma^i\dot\gamma^j=0$，是二阶 ODE。**指数映射** $\exp_p(v)=\gamma_v(1)$（初速 $v$ 的测地线走单位时间到终点），Gauss 引理保证 $\exp_p$ 径向保内积，是小邻域「最短=测地线」的来源。**Hopf-Rinow 定理**：测地完备 $\Leftrightarrow$ 度量完备 $\Leftrightarrow$ 闭有界紧；且完备 $\Rightarrow$ **任意两点可被最短测地线连接**。这是全书从局部走向整体的第一个「整体」定理。
- **飞腾锚点**：**FP16 3.81×[L01]** —— 测地线方程是二阶 ODE，数值解($\ddot\gamma^k=-\Gamma_{ij}^k\dot\gamma^i\dot\gamma^j$)是密集浮点积分。
  - 🟢事实：FP16 吞吐是 FP32 的 3.81 倍；`solve_ivp` 解测地线方程时可受益于半精度加速。
  - 🟡类比：完备性=「没有边界掉下去」——像缓冲区不会越界，每条测地线可无限延伸。
- **几何/应用**：Hopf-Rinow 保证算法在完备流形上「距离可达」(全局收敛)；GPS 卫星轨道是伪黎曼时空的测地线。
- **关键定理**：$$\text{Hopf-Rinow：测地完备 } \Leftrightarrow \text{ 度量完备 } \Leftrightarrow \text{ 闭有界紧；完备 } \Rightarrow \forall\, p,q\ \exists\text{ 最短测地线连接。}$$
- **自测**：球面 $S^2$ 是测地完备的吗？双曲平面 $\mathbb{H}^2$ 呢？去掉原点的平面 $\mathbb{R}^2\setminus\{0\}$ 呢？

---

### 第 4 章 · Curvature（曲率）⭐⭐

> 曲率张量 $R$ / 对称性与 Bianchi 恒等式 / 截面曲率 $K$ / Ricci 与标量曲率 / 法坐标局部公式

- **核心**：**曲率张量** $R(X,Y)Z=\nabla_X\nabla_Y Z-\nabla_Y\nabla_X Z-\nabla_{[X,Y]}Z$ 度量联络的非交换性。三组**对称性**：反交换、对偶对称、第一第二 Bianchi 恒等式，使独立分量从 $n^4$ 降至 $\frac{n^2(n^2-1)}{12}$（$n=2$ 仅 1 个=Gauss 曲率）。三层级：**截面曲率** $K=\frac{\langle R(X,Y)Y,X\rangle}{|X|^2|Y|^2-\langle X,Y\rangle^2}$；**Ricci** $\mathrm{Ric}(X,Y)=\mathrm{tr}(V\mapsto R(V,X)Y)$；**标量** $\mathrm{scal}=\mathrm{tr}_g\mathrm{Ric}$。法坐标下 $g_{ij}=\delta_{ij}-\tfrac13 R_{ikjl}x^kx^l+O(|x|^3)$——曲率=度量的「二阶加速度」。
- **飞腾锚点**：**matmul 15×[V03]** —— $R$ 是 $(1,3)$ 型张量，$n^4$ 个分量，Ricci 缩并 $\mathrm{Ric}_{ij}=g^{kl}R_{kilj}$ 是密集多线性代数。
  - 🟢事实：tensor core 做缩并比标量快 15 倍。
  - 🟡类比：Ricci 缩并就是 `einsum('kl,kilj->ij', g_inv, R)`，是批量矩阵乘+迹收缩。
- **几何/应用**：Einstein 方程 $R_{\mu\nu}-\tfrac12 Rg_{\mu\nu}=8\pi T_{\mu\nu}$ 中 Ricci 张量直接是物质能量的响应；信息几何中 Fisher 度量的曲率衡量统计模型族的「弯曲」。
- **关键定理**：$$R \text{ 满足三组对称性，使 } n^4 \text{ 分量降至 } \frac{n^2(n^2-1)}{12}\text{；常截面曲率 } K\equiv k \Rightarrow \mathrm{Ric}=(n-1)k\,g,\ \mathrm{scal}=n(n-1)k.$$
- **自测**：验证常曲率 $R(X,Y)Z=k(\langle Y,Z\rangle X-\langle X,Z\rangle Y)$ 推出 $\mathrm{Ric}=(n-1)k\,g$；$n=2$ 时 $K$ 恢复 Gauss 曲率。

---

### 第 5 章 · Jacobi Fields; Conjugate Points（Jacobi 场; 共轭点）⭐⭐

> Jacobi 方程 / 测地线变分 / 共轭点($\exp_p$ 退化) / 越过共轭点后不再最短

- **核心**：**Jacobi 方程** $\nabla_{\dot\gamma}\nabla_{\dot\gamma}J+R(J,\dot\gamma)\dot\gamma=0$；Jacobi 场 $J$ 是测地线变分 $\gamma_s(t)$ 的变分向量场 $\partial\gamma_s/\partial s|_{s=0}$。$J(0)=0$ 时 $J(t)=d(\exp_p)_{tv}\cdot tw$ 刻画 $\exp_p$ 的微分。**共轭点**($\exp_p$ 退化处)是测地线停止最短的临界位置——越过第一共轭点后 $\gamma$ 不再最短。球面 $S^2$($K=1$) 从北极出发的测地线在 $t=\pi$(南极)出现第一共轭点。
- **飞腾锚点**：**UDOT 16.9×[E05]** —— Jacobi 方程 $J''+R(J,\dot\gamma)\dot\gamma=0$ 的系数含 $g$ 内积，离散化是逐点点积积累。
  - 🟢事实：UDOT(专用点积指令)比通用浮点快 16.9 倍。
  - 🟡类比：Jacobi 场=「测地线束的发散/汇聚」——透镜方程、引力透镜的本质；共轭点=光学中焦点的几何推广。
- **几何/应用**：Jacobi 场是 Rauch 比较定理(Ch10)的基石；共轭点在机器人路径规划中对应路径多义性，在广义相对论中对应引力透镜多像。
- **关键定理**：$$J''+R(J,\dot\gamma)\dot\gamma=0,\quad J(0)=0 \Rightarrow J(t)=d(\exp_p)_{tv}\cdot(tw);\ \exp_p \text{ 在共轭点退化。}$$
- **自测**：球面 $S^2$($K=1$)上 Jacobi 方程 $J''+J=0$，$J(0)=0$，求第一共轭点位置。(答：$t=\pi$。)

---

### 第 6 章 · Isometric Immersions; The Second Fundamental Form（等距浸入; 第二基本形式）⭐⭐

> 等距浸入定义 / 第二基本形式 $\alpha$ / Gauss 公式 / 极小与全测地子流形 / 法曲率

- **核心**：等距浸入 $f:\bar M^n\to M^{n+k}$ 使 $g=f^*\bar g$。**第二基本形式** $\alpha(X,Y)=(\bar\nabla_X Y-\nabla_X Y)^\perp$ 取值于法丛，度量子流形在环境流形中的「外弯曲」。**Gauss 公式** $\bar\nabla_X Y=\nabla_X Y+\alpha(X,Y)$ 拆分协变导数为切向(内蕴 Levi-Civita)+法向(外弯曲)。$\alpha\equiv0$ ⟺ 全测地子流形(测地线在子流形内)；$\mathrm{tr}\,\alpha=0$ ⟺ 极小子流形。这是 do Carmo《曲线与曲面》ch6(第二基本形式)的任意维推广。
- **飞腾锚点**：**GEMM 9.45G[Lab05]** —— $\alpha$ 有 $k$ 个法分量，每个是 $n\times n$ 对称双线性型，计算是密集 GEMM。
  - 🟢事实：GEMM 每秒 9.45G 次运算，$\alpha_{ij}^\lambda=\bar\Gamma_{ij}^\lambda-\Gamma_{ij}^\lambda$($\lambda$=法指标)是批量缩并。
  - 🟡类比：第二基本形式=曲面的「弯曲检测器」——do Carmo ch6 中 $S^2\subset\mathbb{R}^3$ 的 $\alpha$ 恰是形状算子；这里是任意余维推广。
- **几何/应用**：极小曲面(肥皂膜)的数学基础；广义相对论中类空超曲面的外曲率($K_{ij}$)进入 ADM 形式。
- **关键定理**：$$\text{Gauss 公式：}\bar\nabla_X Y=\nabla_X Y+\alpha(X,Y);\quad \alpha\equiv0 \Leftrightarrow \text{全测地},\quad \mathrm{tr}\,\alpha=0 \Leftrightarrow \text{极小。}$$
- **自测**：$S^2\subset\mathbb{R}^3$ 的第二基本形式 $\alpha(X,Y)=\langle X,Y\rangle N$($N$=单位法向量)，验证 $\mathrm{tr}\,\alpha=2\neq0$(非极小)；$S^2$ 的测地线(大圆)在 $S^2$ 内是测地线吗？

---

### 第 7 章 · Variations of Energy（变分）⭐⭐

> 能量泛函 $E$ / 第一变分(测地线=临界点) / 第二变分(指数形式) / 指标形式 $I$

- **核心**：**能量泛函** $E(\gamma)=\tfrac12\int_a^b|\dot\gamma|^2\,dt$。**第一变分** $\delta E=\langle V,\dot\gamma\rangle\big|_a^b-\int\langle V,\nabla_{\dot\gamma}\dot\gamma\rangle\,dt$——固定端点时零当且仅当 $\nabla_{\dot\gamma}\dot\gamma=0$，即**测地线=能量临界点**。**第二变分** $I(V,V)=\int_a^b(|\nabla_{\dot\gamma}V|^2-\langle R(V,\dot\gamma)\dot\gamma,V\rangle)\,dt$——「动能-势能」结构，正曲率=硬弹簧(能量上升→不稳定)。指标形式 $I$ 的正定性决定测地线的稳定性，是 Morse 指数定理(Ch8)的直接对象。
- **飞腾锚点**：**UDOT 16.9×[E05]** —— $E=\tfrac12\int|\dot\gamma|^2\,dt$ 离散化是逐点求 $g(\dot\gamma,\dot\gamma)$ 再积分=点积累加。
  - 🟢事实：UDOT 比 FP32 快 16.9 倍，对 $\sum g_{ij}\dot\gamma^i\dot\gamma^j\Delta t$ 直接加速。
  - 🟡类比：第二变分「动能-势能」结构——负曲率=软弹簧(稳定)，正曲率=硬弹簧(不稳定)。
- **几何/应用**：变分法是「最短路径」的严格化——第一变分给出 Euler-Lagrange 方程(测地线)，第二变分给出稳定性判据。
- **关键定理**：$$\delta E=0 \Leftrightarrow \nabla_{\dot\gamma}\dot\gamma=0;\qquad I(V,V)=\int(|\nabla_{\dot\gamma}V|^2-\langle R(V,\dot\gamma)\dot\gamma,V\rangle)\,dt.$$
- **自测**：固定端点的变分中，第一变分为零推出什么方程？第二变分在 $K>0$ 球面上(对垂直变分场 $V$)是正还是负？

---

### 第 8 章 · The Morse Index Theorem（Morse 指数定理）⭐

> 指标形式 $I$ 的惯性律 / 共轭点计数 / Morse 指数 = $(0,b)$ 内共轭点重数之和

- **核心**：**指标** $\mathrm{Ind}(\gamma)$ = 指标形式 $I$ 在固定端点变分空间上的**负子空间维数**(即第二变分为负的方向个数)。**Morse 指数定理**：$\mathrm{Ind}(\gamma)=$ 沿 $\gamma$ 在 $(0,b)$ 内的**共轭点重数之和**。这把「测地线稳定性」(分析量)与「共轭点分布」(几何量)精确等价。共轭点越多，测地线越不稳定(指标越大)。球面上从北极到超过南极的点，指标 $\geq1$——越过南极后不再最短。
- **飞腾锚点**：**Iron Law <2%[Lab00]** —— 指标=稳定性判据，本质是「误差预算」：负方向个数 = 测地线偏离最短的「危险度」。
  - 🟢事实：数值优化要求相对误差 <2%；Morse 指数给出精确的「负曲率方向数」=能量泛函 Hessian 的负特征值个数。
  - 🟡类比：指标=0(稳定，最短)，指标>0(不稳定，有共轭点)——类比 Hessian 正定(局部极小)vs 不定(鞍点)。
- **几何/应用**：Morse 理论把「测地线空间」的拓扑与流形本身的拓扑联系起来——临界点(测地线)的指标分布反映 $\Omega(M;p,q)$ 的同调群。
- **关键定理**：$$\mathrm{Ind}(\gamma)=\sum_{t\in(0,b)}\text{(共轭点 } t \text{ 的重数)};\quad \mathrm{Ind}=0 \Rightarrow \gamma \text{ 局部最短。}$$
- **自测**：球面 $S^2$ 上从北极到 $(\theta_0,\varphi_0)$($\theta_0>\pi$)的测地线，指标是多少？(答：$\geq1$，因 $t=\pi$ 处有共轭点。)

---

### 第 9 章 · The Fundamental Group; Synge's Theorem（基本群; Synge 定理）⭐⭐

> Synge 定理 / 正截面曲率对 $\pi_1$ 与定向性的约束 / 紧正曲率流形的拓扑刚性

- **核心**：**Synge 定理**：设 $M$ 紧致、截面曲率 $K>0$。① 若 $\dim M$ 为**偶数**且 $M$ 可定向 $\Rightarrow$ $M$ 单连通($\pi_1=0$)；② 若 $\dim M$ 为**奇数** $\Rightarrow$ $M$ 可定向。正截面曲率对拓扑施加强约束——偶数维正曲率流形「太弯」以致不能有非平凡覆叠。证明用沿闭合测地线的平行移动(标架旋转)，正曲率使旋转角度恰好保证缩短矛盾。这是「曲率控制拓扑」最直接的范例之一。
- **飞腾锚点**：**分支预测[Lab02]** —— 正曲率空间中邻近测地线汇聚(=预测命中)，$K>0$ 时闭合测地线上的标架旋转被曲率锁定。
  - 🟢事实：分支预测命中率决定流水线效率；正曲率下沿闭合测地线的标架旋转角度被 $K>0$ 约束为「不够一圈」(偶数维)。
  - 🟡类比：Synge「正曲率逼单连通」可类比强约束下搜索收敛到唯一解——覆叠对应的「另一支」被曲率抹消。
- **几何/应用**：已知紧正曲率例子极少(球面 $S^n$、$\mathbb{CP}^n$、少数齐性空间)，Synge 定理解释了为何——拓扑约束极强。
- **关键定理**：$$M \text{ 紧},\ K>0:\ \dim M \text{ 偶且可定向} \Rightarrow \pi_1(M)=0;\quad \dim M \text{ 奇} \Rightarrow M \text{ 可定向。}$$
- **自测**：用 Synge 证明 $\mathbb{RP}^2$(不可定向、$\pi_1=\mathbb{Z}_2$)不可能承载 $K>0$ 度量；$\mathbb{RP}^3$($\dim=3$ 奇)为何不矛盾？

---

### 第 10 章 · Bonnet-Myers; The Hadamard Theorem（Bonnet-Myers; Hadamard 定理）⭐⭐⭐

> Bonnet-Myers(正 Ricci→紧致) / Cartan-Hadamard(负截面→微分同胚) / Sturm 比较引理

- **核心**：本章是全书「比较范式」的 payoff，两大重磅定理：
  - ① **Bonnet-Myers**：$\mathrm{Ric}\geq(n-1)k>0\Rightarrow M$ 紧致且 $\mathrm{diam}\leq\pi/\sqrt{k}$。用 Jacobi 场+Sturm 比较证明：正 Ricci 使 Jacobi 场在 $t=\pi/\sqrt{k}$ 前必有零点(=共轭点)，故直径有上界。正 Ricci「箍住」流形。
  - ② **Cartan-Hadamard**：$K\leq0$ 且完备单连通 $\Rightarrow\exp_p$ 是整体微分同胚。负曲率使 Jacobi 场无共轭点($J$ 永不为零)，$\exp_p$ 非退化；单连通+完备 $\Rightarrow$ 覆叠映射 $\Rightarrow$ 同胚。$M\cong\mathbb{R}^n$。
- **飞腾锚点**：**Iron Law <2%[Lab00]** —— Sturm 比较本质是「误差界」：Jacobi 场与模型场的偏差被曲率差控制。
  - 🟢事实：Jacobi 方程是线性 ODE，Sturm 比较给出零点的夹逼——$\mathrm{Ric}\geq(n-1)k$ 把零点「提前」到 $\leq\pi/\sqrt{k}$。
  - 🟡类比：Bonnet-Myers 的「正曲率→紧致」可类比「强凸($\lambda>0$)→有限步收敛」；Cartan-Hadamard「负曲率→摊开」可类比「凹函数→全局最优唯一」。
- **几何/应用**：Bonnet-Myers 说明正曲率宇宙必然紧致(有限大小)；Cartan-Hadamard 是双曲几何整体存在性的理论根据。
- **关键定理**：$$\mathrm{Ric}\geq(n-1)k>0 \Rightarrow \mathrm{diam}(M)\leq\frac{\pi}{\sqrt{k}};\qquad K\leq0,\ \tilde M\text{ 完备单连通} \Rightarrow \exp_p\text{ 是微分同胚},\ \tilde M\cong\mathbb{R}^n.$$
- **自测**：用 Cartan-Hadamard 解释 $\mathbb{H}^2$($K=-1$)为何整体微分同胚于 $\mathbb{R}^2$；用 Bonnet-Myers 证明 $S^n$($\mathrm{Ric}=n-1$)直径恰好 $\pi$。

---

### 第 11 章 · Submanifolds; The Gauss Equation（子流形; Gauss 方程）⭐⭐

> Gauss 方程(曲率关系) / Codazzi 方程 / 完全可积性条件 / 基本定理

- **核心**：**Gauss 方程**把子流形的内蕴曲率与环境流形曲率+第二基本形式联系起来：$$\langle R(X,Y)Z,W\rangle=\langle\bar R(X,Y)Z,W\rangle+\langle\alpha(X,Z),\alpha(Y,W)\rangle-\langle\alpha(X,W),\alpha(Y,Z)\rangle$$ 这正是 do Carmo《曲线与曲面》中 Theorema Egregium 的任意维+任意余维推广——$n=2$、$k=1$ 时恢复「Gauss 曲率=内蕴量」。**Codazzi 方程** $(\bar\nabla_X\alpha)(Y,Z)=(\bar\nabla_Y\alpha)(X,Z)$ 是第二基本形式的对称性约束。Gauss+Codazzi 合称**基本方程**，是子流形完全可积的充要条件(基本定理：给定满足基本方程的 $\alpha$，子流形由 $\alpha$ 唯一确定，至多差等距)。
- **飞腾锚点**：**matmul 15×[V03]** —— Gauss 方程右侧是 $\alpha$ 分量的双线性配对+缩并，是密集多线性代数。
  - 🟢事实：$\langle\alpha(X,Z),\alpha(Y,W)\rangle$ 是法丛内积=批量缩并，tensor core 加速 15 倍。
  - 🟡类比：Gauss 方程=「内蕴曲率=外曲率+弯曲修正」——弯曲修正项 $\alpha\wedge\alpha$ 是子流形「弯曲的自交叉」。
- **几何/应用**：Theorema Egregium(Gauss 曲率内蕴)的任意维推广——$n=2,\ k=1$ 代入 Gauss 方程即得 $K=K_{\text{ambient}}+\det(\alpha)/\det(g)$。
- **关键定理**：$$\langle R(X,Y)Z,W\rangle=\langle\bar R(X,Y)Z,W\rangle+\langle\alpha(X,Z),\alpha(Y,W)\rangle-\langle\alpha(X,W),\alpha(Y,Z)\rangle.$$
- **自测**：在 $\mathbb{R}^3$ 中($\bar R=0$)，$S^2$ 的 $\alpha(X,Y)=\langle X,Y\rangle N$，用 Gauss 方程推出 $\langle R(X,Y)Y,X\rangle=|X|^2|Y|^2-\langle X,Y\rangle^2$(即 $K=1$)。

---

### 第 12 章 · Spaces of Constant Curvature（空间形式）⭐

> 空间形式定义 / 常曲率流形分类 / 完备单连通常曲率 $\Leftrightarrow$ $\mathbb{R}^n$/$S^n$/$\mathbb{H}^n$ / Klingenberg

- **核心**：**空间形式**(space form)是截面曲率 $K$ 恒为常数的完备黎曼流形。由 Cartan-Hadamard(Ch10)和 Hopf-Rinow(Ch3)，完备单连通常曲率流形恰有三类：**欧氏空间** $\mathbb{E}^n$($K=0$)、**球面** $S^n$($K=1/c^2>0$)、**双曲空间** $\mathbb{H}^n$($K=-1/c^2<0$)，$\exp_p$ 均为微分同胚。一般空间形式=上述三种的商(覆叠)，如 $\mathbb{RP}^n=S^n/\{\pm\mathrm{id}\}$、平坦环面 $T^n=\mathbb{R}^n/\mathbb{Z}^n$。Klingenberg 定理给出 injectivity radius 的下界估计($\mathrm{inj}\geq\min\{\frac12\mathrm{diam},\frac{\pi}{\sqrt{\sup K}}\}$)。空间形式是全书所有比较定理的**基准模型**。
- **飞腾锚点**：**Schmidt 正交化** ⭐ —— 常曲率流形高度齐性，等距群 transitively 作用，每点的迷向群保正交标架。
  - 🟢事实：$S^n$ 的等距群 $\mathrm{O}(n+1)$ 保标准正交基，平行移动=Schmidt 正交化的群作用。
  - 🟡类比：空间形式=「最均匀的空间」——每一点局部几何完全相同，没有「特殊位置」，正交标架在群作用下自然标准化。
- **几何/应用**：空间形式是宇宙学模型的基础——Einstein 静态宇宙($S^3\times\mathbb{R}$)、de Sitter/anti-de Sitter 空间；双曲空间 $\mathbb{H}^n$ 是双曲几何与 Mostow 刚性的舞台。
- **关键定理**：$$\text{完备单连通常截面曲率流形恰为 } \mathbb{E}^n(K=0),\ S^n(K>0),\ \mathbb{H}^n(K<0)\text{ 三类；一般空间形式为其商。}$$
- **自测**：平坦环面 $T^2=\mathbb{R}^2/\mathbb{Z}^2$ 的 $K\equiv0$ 但不完备单连通，它的万有覆叠是什么？(答：$\mathbb{R}^2$，$K=0$。)

---

### 第 13 章 · Conformal Transformations; Killing Fields（共形变换; Killing 场）⭐

> 共形映射 $f^*g=\lambda^2 g$ / Killing 场(无穷小等距) / Killing 方程 / 共形 Killing 场

- **核心**：**共形变换** $f:(M,g)\to(\bar M,\bar g)$ 满足 $f^*\bar g=\lambda^2 g$($\lambda:M\to\mathbb{R}_+$)，保角度但不保距离——是 Möbius 变换($S^n$)、Liouville 定理($\mathbb{R}^n,\ n\geq3$)的几何推广。**Killing 场** $X$ 是无穷小等距：$\mathcal{L}_X g=0$，等价于 **Killing 方程** $\nabla_i X_j+\nabla_j X_i=0$。Killing 场构成 Lie 代数 $\mathfrak{kill}(M,g)$，其维数 $\leq\frac{n(n+1)}{2}$($=\dim\mathrm{O}(n+1)$，等号=空间形式)。共形 Killing 场 $Y$ 满足 $\mathcal{L}_Y g=\mu\,g$，是二者(等距+共形)的公共推广。
- **飞腾锚点**：**TLB 4.81×[E04]** ⭐主力 —— 共形变换局部缩放度量($g\to\lambda^2 g$)，是逐点的局部操作=高缓存命中率。
  - 🟢事实：$\lambda^2(p)\cdot g_{ij}(p)$ 逐点计算，$g_{ij}$ 与 $\lambda$ 同址访问，TLB 命中率高。
  - 🟡类比：共形变换=「保角度的弹性变形」——地图投影(墨卡托=共形投影)的数学本质；Killing 场=「刚性旋转/平移」(无弹性)。
- **几何/应用**：Killing 场对应物理中的守恒律(能动量)；共形变换是共形场论(CFT)与弦论的对称性语言；Yamabe 问题(共形类中找常标量曲率度量)连接 PDE 与几何。
- **关键定理**：$$\mathcal{L}_X g=0 \Leftrightarrow \nabla_i X_j+\nabla_j X_i=0;\qquad f^*\bar g=\lambda^2 g \text{ (共形)};\qquad \dim\mathfrak{kill}(M,g)\leq\frac{n(n+1)}{2}.$$
- **自测**：$\mathbb{R}^2$ 上 $X=-y\partial_x+x\partial_y$(旋转)是 Killing 场吗？验证 $\nabla_i X_j+\nabla_j X_i=0$。(答：是。)

---

## §9 全书思想主线

do Carmo 全书有一条铁律般的主线：**曲率控制拓扑**。这条主线沿着「度量 $\to$ 联络 $\to$ 测地线 $\to$ 曲率 $\to$ 变分 $\to$ 比较」的逻辑链展开，每一环都是前一环的自然深化。

**度量与联络**(Ch1-2) 是地基——给流形配上「尺子」($g$)和「微分规则」($\nabla$)。Levi-Civita 基本定理保证唯一的无挠度量相容联络，使一切几何量内蕴地定义。这是 do Carmo《曲线与曲面》ch4(Theorema Egregium) 从 $n=2$ 嵌入 $\mathbb{R}^3$ 到任意维纯内蕴的推广。

**测地线与完备性**(Ch3) 是第一条「局部 $\to$ 整体」的桥梁——Hopf-Rinow 把「每条测地线可无限延伸」(测地完备)与「闭有界紧」(度量完备)和「任意两点可被最短测地线连接」三位一体，是全书从局部走向整体的第一个整体定理。

**曲率分层**(Ch4) 把「弯曲」拆解为三个层级。截面曲率 $K$ 最精细(每点每个二维切片一个数)，Ricci 是截面曲率的迹(控制体积增长)，标量是全平均。常曲率($K\equiv k$) 时三者精确关联：$\mathrm{Ric}=(n-1)k\,g$，$\mathrm{scal}=n(n-1)k$。

**变分与比较**(Ch5-8,10) 是全书的「分析引擎」。Jacobi 场(Ch5)刻画测地线束的发散/汇聚，能量泛函(Ch7)给出变分框架，Morse 指数定理(Ch8)把「测地线稳定性」与「共轭点分布」精确等价。这些工具在 Ch10 结出硕果：Bonnet-Myers(正 Ricci $\to$ 紧致)与 Cartan-Hadamard(负截面 $\to$ 微分同胚)是「曲率条件直接钉死拓扑」的两个典范。

**子流形与对称**(Ch6,11-13) 拓展视野。Gauss 方程(Ch11)揭示内蕴曲率=外曲率+弯曲修正，是 Theorema Egregium 的任意维推广。空间形式(Ch12)给出比较定理的三个基准模型($\mathbb{R}^n$/$S^n$/$\mathbb{H}^n$)。共形与 Killing(Ch13)引入对称性语言。

**与 Petersen 的区别**：do Carmo 把局部理论、变分、子流形讲得比 Petersen **更深更细**(Gauss/Codazzi 完整推导、Morse 指数定理独立成章)，但**不含收敛理论**(GH 距离/Cheeger-Colding)。因此 do Carmo 是「经典黎曼几何百科全书」，Petersen 是「现代比较几何入口」——二者互补，建议 do Carmo 先读建立经典功底，Petersen 再读攻现代纵深。

### 全书脉络一览（红线串联）

> 下表把十三章的核心定理、曲率层级与飞腾锚点集中对照，与 §1 骨架表互补：§1 按「学什么」排列，本表按「为什么」排列。

| 章 | 曲率层级 | 核心定理 | 飞腾/工程锚点 |
|---|---|---|---|
| 1 | 度量(无曲率) | 度量存在性 | TLB 4.81×[E04] 局部坐标 |
| 2 | 联络(无曲率) | Levi-Civita 基本定理 | Schmidt 正交化 标架 |
| 3 | 测地线(无曲率) | Hopf-Rinow | FP16 3.81×[L01] ODE 数值解 |
| 4 | 全曲率 $R$ | 对称性+Bianchi | matmul 15×[V03] 多线性 |
| 5 | 变分(全曲率) | Jacobi 方程+共轭点 | UDOT 16.9×[E05] 点积积累 |
| 6 | 子流形外曲率 | Gauss 公式+第二基本形式 | GEMM 9.45G[Lab05] 批量缩并 |
| 7 | 变分 | 第一第二变分 | UDOT 16.9×[E05] 能量积分 |
| 8 | 变分指标 | Morse 指数=共轭点重数和 | Iron Law<2%[Lab00] 误差预算 |
| 9 | 截面 $K$ | Synge 定理 | 分支预测[Lab02] 标架旋转 |
| 10 | Ricci+截面 | Bonnet-Myers/Hadamard | Iron Law<2%[Lab00] Sturm 比较 |
| 11 | 子流形内蕴 | Gauss 方程 | matmul 15×[V03] 多线性 |
| 12 | 常曲率 | 空间形式分类 | Schmidt 正交化 齐性空间 |
| 13 | 对称性 | Killing 方程/共形 | TLB 4.81×[E04] 局部缩放 |

**三条红线**：
1. **曲率分层红线**——截面 $K$(Ch4,9) → Ricci(Ch10) → 标量，每弱一级，结论从「钉死 $\pi_1$」到「箍住直径」到「留拓扑痕迹」，工具从 ODE 比较到 Sturm 振荡。
2. **变分→比较红线**——能量泛函(Ch7) → Jacobi 场(Ch5) → Morse 指数(Ch8) → Bonnet-Myers/Hadamard(Ch10)，测地线稳定性分析是全书比较定理的引擎。
3. **局部→整体红线**——局部曲率(Ch4) → 子流形关系(Ch6,11) → 整体刚性(Ch9,10) → 空间形式分类(Ch12)，曲率从「一点的微分」长成「整个流形的拓扑约束」。

**读法建议**：第一遍精读 Ch1-4(度量/联络/测地线/曲率，工程/物理应用最密)；第二遍死磕 Ch7-8+Ch10(变分+Morse 指数+比较定理，全书灵魂)；第三遍选读 Ch6+Ch11(子流形/Gauss 方程)与 Ch12-13(空间形式/对称)。配套横切查 `04-concepts` 中「导数/极限/对称」概念页。

---

## §10 与本仓库其他笔记的交叉引用

**与 Petersen《黎曼几何》GTM171 对比**(stage-2)：do Carmo = 经典入门(证明可手算，局部理论+基础比较+子流形)；Petersen = 现代比较几何(含 GH 收敛/Cheeger-Colding/Ricci 流引)。do Carmo Ch1-4(度量/联络/测地线/曲率) $\leftrightarrow$ Petersen Ch1-3；do Carmo Ch5+Ch7+Ch8(Jacobi/变分/Morse) $\leftrightarrow$ Petersen Ch4；do Carmo Ch10(Bonnet-Myers/Hadamard) $\leftrightarrow$ Petersen Ch5。建议：do Carmo 先读(经典功底)，Petersen 再读(现代纵深)，对照 Bonnet-Myers 的两种证法(do Carmo 用 Sturm 比较，Petersen 用 Bishop-Gromov 体积比较)。

**与 do Carmo《曲线与曲面的微分几何》对比**(stage-2)：《曲线与曲面》= $n=2$、嵌入 $\mathbb{R}^3$ 的特例；本书=任意 $n$、纯内蕴。《曲线与曲面》ch4(第一基本形式/Theorema Egregium/测地线) $\leftrightarrow$ 本书 Ch1-4；《曲线与曲面》ch6(第二基本形式) $\leftrightarrow$ 本书 Ch6+Ch11；《曲线与曲面》ch5(Hopf-Rinow/Bonnet/抽象曲面) $\leftrightarrow$ 本书 Ch3+Ch10+Ch12。建议先读《曲线与曲面》(二维直觉)，再读本书(任意维严格化)。

**与 Lee《黎曼流形》GTM176 对比**：Lee 更友好(递归式铺垫每个概念)，适合第一遍打基础；do Carmo 更紧凑(假设流形已知)，适合第二遍巩固。Lee Ch1-8 $\leftrightarrow$ do Carmo Ch1-10。建议 Lee Ch1-6 与 do Carmo Ch1-4 交叉对照。

**与 Hall《李群李代数》对比**(stage-2)：本书 Ch12 空间形式(球面 $S^n=\mathrm{SO}(n+1)/\mathrm{SO}(n)$) 与 Ch13 Killing 场(Lie 代数)直接用 Hall Ch7(Cartan 分类)。读本书 Ch12-13 前建议复习 Hall Ch6-7(根系/Cartan)。

**与 Bott-Tu《微分形式》GTM82 对比**(stage-2)：do Carmo 全书不用微分形式(de Rham 上同调)，而 Bott-Tu 是形式语言的入口。二者互补：do Carmo 给度量几何的内蕴直觉(长度/曲率)，Bott-Tu 给上同调工具(Stokes/谱序列)。建议 do Carmo Ch4(曲率)后补读 Bott-Tu Ch1(de Rham)，建立「曲率=微分形式的几何」直觉。

**AI 锚点（数学 ↔ 工程）**：
- 🟢 **流形 = 数据流形假设**：流形学习(Isomap/t-SNE/UMAP)假设高维数据活在低维黎曼流形上；do Carmo Ch1(度量)+Ch3(测地线)是数学基础。测地距离 $d(p,q)$ = Isomap 用图最短路估计的「本征距离」。
- 🟢 **曲率 = 空间弯曲**：信息几何中 Fisher 度量 $g_{ij}$ 是黎曼度量，曲率衡量「概率分布空间」的弯曲；流形上优化(自然梯度法)用 Levi-Civita 联络(Ch2)修正梯度。
- 🟢 **第二基本形式 = 子流形检测**：Ch6+Ch11 的 $\alpha$ 与 Gauss 方程在主成分分析(PCA)的流形推广中刻画数据子流形与环境的偏差。
- 🟡 **比较定理 = 误差界**：Bonnet-Myers/Hadamard 的 Sturm 比较可类比先验误差估计——给参考解(模型空间)，真实解偏差被曲率控制(=Iron Law <2%)。
- 🟡 **Morse 指数 = 稳定性分析**：Ch8 的指标=能量泛函 Hessian 的负特征值个数，与优化中鞍点检测/escape direction 计数同构。
- 🟡 **Killing 场 = 对称性自动微分**：Ch13 的 $\nabla_i X_j+\nabla_j X_i=0$ 是等变神经网络中对称性约束的连续版——Killing 场刻画「保持度量不变的变换」，等变网络要求特征在群作用下协变。
- 🟢 **共形变换 = 尺度不变性**：Ch13 的 $f^*g=\lambda^2 g$ 在共形场论(CFT)与尺度不变物理中是核心对称性；计算机视觉中尺度空间(SIFT)隐含共形结构。

---

## §11 自测答案要点（供核对）

1. **Ch1** $S^2$ 的 $g=d\theta^2+\sin^2\theta\,d\varphi^2$ 与《曲线与曲面》ch2 一致($E=1,F=0,G=\sin^2\theta$)；$d(p,q)=\inf$ 大圆弧长 $=\arccos(p\cdot q)$($R=1$)。
2. **Ch2** $g=\delta_{ij}\Rightarrow g_{ij,k}=0\Rightarrow\Gamma_{ij}^k=0$，测地线 $\ddot\gamma^k=0$ 即匀速直线。$S^2$ 的 $\Gamma_{\varphi\varphi}^\theta=-\sin\theta\cos\theta$，赤道($\theta=\pi/2$)上 $\dot\varphi=\text{const}$ 是测地线。
3. **Ch3** $S^2$ 完备(紧致 $\Rightarrow$ 度量完备 $\Rightarrow$ 测地完备，Hopf-Rinow)；$\mathbb{H}^2$ 完备(标准度量)；$\mathbb{R}^2\setminus\{0\}$ **不完备**(穿过原点的测地线断在 $0$)。
4. **Ch4** 常曲率 $R(X,Y)Z=k(\langle Y,Z\rangle X-\langle X,Z\rangle Y)$，取迹 $\mathrm{Ric}=(n-1)k\,g$，再取迹 $\mathrm{scal}=n(n-1)k$。$n=2$ 时 $K=k$。
5. **Ch5** $S^2$($K=1$)：$J''+J=0$，$J(0)=0\Rightarrow J(t)=c\sin t$，第一零点 $t=\pi$(到南极距离)。
6. **Ch6** $\alpha(X,Y)=\langle X,Y\rangle N$，$\mathrm{tr}\,\alpha=\mathrm{tr}(\mathrm{id})\cdot N=2N\neq0$(非极小)。$S^2$ 的测地线(大圆)在 $S^2$ 内是测地线(全测地性需要 $\alpha\equiv0$，不成立——大圆是 $S^2$ 内蕴测地线但 $\alpha\neq0$ 是外在弯曲)。
7. **Ch7** 第一变分为零 $\Rightarrow\nabla_{\dot\gamma}\dot\gamma=0$(测地线方程)。$K>0$ 球面上第二变分(垂直变分 $V$)$I(V,V)=\int(|V'|^2-\langle R(V,\dot\gamma)\dot\gamma,V\rangle)\,dt$，末项为负 $\Rightarrow$ 不稳定。
8. **Ch8** $\theta_0>\pi$ 时共轭点 $t=\pi\in(0,\theta_0)$，重数 1(球面 $S^2$ 余维 1)，故 $\mathrm{Ind}\geq1$。
9. **Ch9** $\mathbb{RP}^2$：偶数维(2)、不可定向($w_1\neq0$) $\Rightarrow$ Synge 要求偶数维正曲率可定向，矛盾。$\mathbb{RP}^3$($\dim=3$ 奇) $\Rightarrow$ Synge 只要求可定向，不矛盾($\mathbb{RP}^3$ 确实可定向)。
10. **Ch10** $\mathbb{H}^2$：完备单连通 $K=-1\leq0\Rightarrow\exp_p$ 微分同胚 $\Rightarrow\mathbb{H}^2\cong\mathbb{R}^2$。$S^n$：$\mathrm{Ric}=n-1=(n-1)\cdot1\Rightarrow k=1\Rightarrow\mathrm{diam}\leq\pi$，取等。
11. **Ch11** $\mathbb{R}^3$ 中 $\bar R=0$：$\langle R(X,Y)Y,X\rangle=0+\langle\alpha(X,Y),\alpha(Y,X)\rangle-\langle\alpha(X,X),\alpha(Y,Y)\rangle$，代入 $\alpha=\langle\cdot,\cdot\rangle N$ 得 $\langle X,Y\rangle^2-|X|^2|Y|^2$，绝对值后 $K=1$。
12. **Ch12** $T^2=\mathbb{R}^2/\mathbb{Z}^2$ 万有覆叠 $\mathbb{R}^2$($K=0$)，$T^2$ 非单连通($\pi_1=\mathbb{Z}^2$)故不等于 $\mathbb{R}^2$，是商。
13. **Ch13** $X=-y\partial_x+x\partial_y$ 在 $\mathbb{R}^2$ 中 $X^i=(-y,x)$，$\nabla_i X_j=\partial_i X_j$($\Gamma=0$)：$\partial_x(-y)+\partial_y(x)=0+0=0$，$\nabla_x X_y+\nabla_y X_x=1+(-1)=0$ ✓，故是 Killing 场。

> **核对原则**：每题的核心是「曲率条件 → 拓扑/几何结论」的因果链。Ch1-3 属「奠基」(无曲率比较)，Ch4-13 属「比较」——依赖截面(Ch9,11)最强，Ricci(Ch10)次之，标量最弱但工具(指标定理)最深。Morse 指数(Ch8)是变分(Ch7)与比较(Ch10)之间的分析桥梁。

---

> **下一步**：沿 `01-track/stage-2` 精读 do Carmo Ch1-4(度量/联络/测地线/曲率)，遇关键概念查 `00-META/CONCEPT-INDEX` 中「导数/极限/对称」视角；Ch7-8+Ch10(变分+Morse+比较)死磕第二变分符号，与 Petersen Ch4-5 对照。Ch12-13 选读，作为 stage-3(几何分析/李群)的跳板。
>
> **stage-3 前瞻**：Ricci 流(Hamilton/Perelman) → PDE/几何分析方向；Kähler 几何 → Calabi-Yau/弦论 → 代数几何(Hartshorne)；共形几何 → Yamabe 问题/CFT。三条路径在 stage-3 展开。
>
> **实操验证**(建议用 Python/SciPy)：
> - `scipy.integrate.solve_ivp` 解测地线方程(Ch3) → 验证球面大圆是测地线
> - `numpy.einsum('kl,kilj->ij', g_inv, R)` 实现 Ricci 缩并(Ch4) → 验证 $S^n$ 的 $\mathrm{Ric}=(n-1)g$
> - 用 Dijkstra/Isomap 在点云上估计测地距离(Ch1) → 模拟流形学习
> - `scipy.sparse.linalg.eigsh` 算指标形式 $I$ 的特征值(Ch8) → 体验 Morse 指数=负特征值个数
> - 实现 Gauss 方程数值验证(Ch11)：对 $S^2\subset\mathbb{R}^3$ 算 $\langle R(X,Y)Y,X\rangle$ 并验证 $K=1$
> - 用 `scipy.integrate.odeint` 解 Jacobi 方程(Ch5) $J''+J=0$ → 验证 $S^2$ 第一共轭点在 $t=\pi$
