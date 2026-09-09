# Bott-Tu《代数拓扑中的微分形式》(GTM82) · 快速逐章精读

> 基于原书:`Differential Forms in Algebraic Topology`, GTM82 (Raoul Bott & Loring W. Tu, Springer, 1982) / 读于:2026-07-02
> 定位:**de Rham 视角的代数拓扑经典**,用微分形式统一 de Rham / Čech / 谱序列三大上同调机器。
> 本文为**快速逐章精读**,每章 1 个飞腾锚点 🟢/🟡 + 1 个关键定理 + 1 道自测题。
> 前置:本仓库已读 Fulton 代数拓扑(GTM153)、Gamelin 复分析、Petersen 黎曼几何(GTM171)。

---

## §0 引言:Bott-Tu 是什么,为什么读它

Raoul Bott 与 Loring W. Tu 的《代数拓扑中的微分形式》(GTM82, 1982)是**以微分形式为主线的代数拓扑经典**,
哈佛 MIT 数十年的标准研究生教材。与 Hatcher 从基本群/奇异同调切入不同,Bott-Tu 全程用光滑流形上的
**微分形式**(de Rham 上同调)作为计算工具,再用 Čech 上同调与谱序列把局部拼接成全局。
全书三章层层递进:第1章建立 de Rham 上同调(de Rham 复形 / Poincaré 引理 / Mayer-Vietoris / Poincaré 对偶 / de Rham 定理),
第2章引入 Čech-de Rham 双复形与**谱序列**(「收敛机器」),
第3章把谱序列用于纤维丛与示性类(Serre 谱序列 / Chern-Weil 示性类 / 有理同伦论)。

Bott 本人是 Bott 周期性、Atiyah-Bott 不动点定理的创造者,这使得第3章「示性类」带有大师手笔——
用曲率形式直接算 Chern 类,把抽象公理变成可手算的微分形式。
前置:多元微积分、Fulton 代数拓扑(同调/上同调概念)、Petersen 黎曼几何(流形/切丛/微分形式基础)。

对比四本主流教材:

| 书 | 风格 | 严格性 | 适合谁 |
|---|---|---|---|
| **Bott-Tu** GTM82 (1982) | de Rham/微分形式主线,谱序列为核心计算工具,Chern-Weil 示性类大师手笔 | 严谨精炼,证明流畅 | 已读流形/微分形式,想用「分析工具」算拓扑的读者 |
| **Hatcher**《Algebraic Topology》(2002,免费) | 基本群+奇异同调主线,几何直觉流淌,图极多 | 叙述松散,常留给读者 | 喜欢看图悟道的第一本代数拓扑 |
| **Bredon**《Topology and Geometry》GTM139 (1993) | 几何味重,流形/李群导向,同调与微分形式并举 | 严谨偏几何 | 想从微分几何/李群切入的研究者 |
| **Warner** GTM94 (1983) | 光滑流形上的分析,de Rham + Hodge 理论,偏 PDE/分析 | 严谨偏分析 | 想深入 Hodge 理论/几何分析 |

**建议路线**:Fulton 代数拓扑(奇异同调直觉)→ Bott-Tu(用微分形式重做上同调 + 谱序列)→ Milnor-Stasheff《示性类》。
对零基础补课的工程师,第1章是「甜区」(只需多元微积分与线性代数);第2章谱序列是全书最硬的骨头;
第3章示性类是回报最丰的终点。

> 🟢 事实可作锚点:Poincaré 引理、Mayer-Vietoris、de Rham 定理、Thom 同构、Serre 谱序列、Chern-Weil 均为严格定理。
> 🟡 类比(微分形式 = 流形上的「代数探测器」、谱序列 = 「逐页逼近的收敛机器」)仅供直觉,**绝不在严格证明中引用**。

---

## §1 全书 3 章 + 附录骨架一览(飞腾锚点分布)

| 章 | 标题 | 核心概念 | 飞腾锚点 |
|---|---|---|---|
| 1 | de Rham 上同调 | de Rham 复形/$d^2=0$/Poincaré 引理/Mayer-Vietoris/紧支撑/Poincaré 对偶/de Rham 定理 | **Iron Law<2%[Lab00]** ⭐ |
| 2 | Čech 上同调与谱序列 | Čech 复形/好覆盖/双复形/$E_r^{p,q}$/$d_r$/收敛到 de Rham/Künneth/Thom 同构 | **GEMM 9.45G[Lab05]** ⭐ |
| 3 | 谱序列的应用与纤维丛 | 路径纤维丛/Serre 谱序列/Gysin 序列/有理同伦/Chern 类/Pontryagin/Euler 类 | **TLB 4.81×[E04]** ⭐ |
| 附录 | 李群/李代数/向量丛回顾 | 李群/李代数/向量丛/截面/联络/曲率 | **matmul 15×[V03]** |

**两条主线**:(1) **微分形式作为代数拓扑计算工具**——de Rham 复形(Ch1)把「拓扑洞」变成「闭/恰当形式的商」,
用积分(Stokes)与对偶(Poincaré)直接算;(2) **谱序列作为收敛机器**——Čech-de Rham 双复形(Ch2)生出的
$E_r^{p,q}$ 逐页逼近 de Rham 上同调,Ch3 把同一机器接到纤维丛上,算出示性类。

---

### 第 1 章 · de Rham 上同调 ⭐⭐⭐

> de Rham 复形 / Poincaré 引理 / Mayer-Vietoris / 紧支撑 / 定向与积分 / Stokes / Poincaré 对偶 / de Rham 定理

- **核心**:全书地基,也是全书「最可算」的一章。在光滑 $n$-流形 $M$ 上,$k$-形式空间 $\Omega^k(M)$
  配外微分 $d:\Omega^k\to\Omega^{k+1}$ 满足 $d^2=0$(铁律),构成 **de Rham 复形** $(\Omega^*(M),d)$。
  **de Rham 上同调** $H^k_{dR}(M)=\ker d^k/\mathrm{im}\,d^{k-1}$ 度量「闭但不恰当」的形式——即流形的 $k$ 阶拓扑洞。
  本章七大组件层层推进,从局部(Poincaré 引理)到拼接(Mayer-Vietoris)到对偶(Poincaré 对偶)到等同(de Rham 定理)。

- **关键子结果**:
  - **Poincaré 引理**:星形开集 $U\subset\mathbb{R}^n$ 上,闭 $k$-形式($k\ge1$)必恰当——
    $H^k_{dR}(U)=0$($k\ge1$),$H^0_{dR}(U)=\mathbb{R}$(常函数)。
    证明用「同伦算子」$K:\Omega^k\to\Omega^{k-1}$ 使 $\omega=dK\omega+Kd\omega$,即 $d$ 与 $K$ 链同伦。
    这把「可缩 → 无洞」从直觉变成构造性证明。
  - **Mayer-Vietoris 序列**:$M=U\cup V$ 给长正合序列
    $\cdots\to H^k_{dR}(M)\to H^k(U)\oplus H^k(V)\to H^k(U\cap V)\xrightarrow{\partial} H^{k+1}_{dR}(M)\to\cdots$。
    连接同态 $\partial$ 把「跨界闭形式」升一维。它是 de Rham 上同调的头号计算利器:
    把 $S^n$ 拆两个开圆盘归纳算球面上同调。
  - **紧支撑上同调**:限定在**紧支撑形式** $\Omega^*_c(M)$ 上,$H^*_{dR,c}(M)=\ker d/\mathrm{im}\,d$。
    关键反差:$H^1_{dR}(\mathbb{R})=0$(Poincaré 引理)但 $H^1_{dR,c}(\mathbb{R})=\mathbb{R}$——紧支撑逼出非平凡!
    一般 $H^n_{dR,c}(\mathbb{R}^n)=\mathbb{R}$,生成元是「鼓包形式」。
  - **Stokes 定理**:定向带边流形 $M$ 上 $\int_M d\omega=\int_{\partial M}\omega$。
    这是微积分基本定理的高维推广,「边界算子 $\partial$ 与外微分 $d$ 互为伴随」——Poincaré 对偶的基石。
  - **Poincaré 对偶**:紧致可定向 $n$-流形上,积分配对 $\int_M:\Omega^k\times\Omega^{n-k}\to\mathbb{R}$ 诱导同构
    $H^k_{dR}(M)\cong H^{n-k}_{dR}(M)$(贝蒂数对称 $\beta_k=\beta_{n-k}$)。
  - **de Rham 定理**:de Rham 上同调同构于奇异上同调,桥梁是积分 $\omega\mapsto(\sigma\mapsto\int_\sigma\omega)$——
    「微分形式的拓扑」与「经典代数拓扑」合流。

- **飞腾锚点**:**Iron Law<2%[Lab00]** ⭐ —— de Rham 复形的 $d^2=0$ 是铁律,Mayer-Vietoris 是处处 $\ker=\mathrm{im}$ 的正合序列。
  - 🟢事实:外微分 $d$ 的矩阵表示须满足 $D^2=0$(稀疏矩阵乘两次严格归零,数值实现须设容差 Iron Law <2%);
    Mayer-Vietoris 连接同态 $\partial$ 的正合性 $\mathrm{im}=\ker$ 是同调代数的「误差为零」铁律;
    $d^2=0$ 在离散化(de Rham 复形的有限元离散 FEEC)中是稳定性前提。
  - 🟡类比:上同调群 $H^k=\ker d/\mathrm{im}\,d$ 是「铁律偏差」——闭形式中减去恰当形式后剩下的余项就是 $k$ 阶洞。
    $H^k=0$ 表示该阶「无偏差(无洞)」,$H^k\ne0$ 即有洞,偏差的维数 = 贝蒂数 $\beta_k$。

- **关键定理**:**de Rham 定理** + **Poincaré 对偶**。
  $$
  H^k_{dR}(M)\ \xrightarrow{\ \omega\mapsto\big[\sigma\mapsto\textstyle\int_\sigma\omega\big]\ }\ H^k_{sing}(M;\mathbb{R}),\qquad\forall\,k\ge0\quad\text{(de Rham 定理,同构)}.
  $$
  $$
  M\ \text{紧致可定向 }n\text{-流形}\ \Longrightarrow\ H^k_{dR}(M)\cong H^{n-k}_{dR}(M)\quad\text{(Poincaré 对偶)}.
  $$

- **自测**:用 Mayer-Vietoris 把 $S^1$ 拆成两个开区间 $U,V$(交是两段 $U\cap V\simeq\{$ 两点 $\}$),
  算出 $H^0_{dR}(S^1)=\mathbb{R}$、$H^1_{dR}(S^1)=\mathbb{R}$;
  再验证紧支撑反差 $H^1_{dR,c}(\mathbb{R})=\mathbb{R}$(构造鼓包 $1$-形式 $f(x)\,dx$,$f$ 紧支撑且 $\int f\,dx\ne0$),
  说明它与 $H^1_{dR}(\mathbb{R})=0$ 的区别(紧支撑挖掉了「可缩到零」的退路)。

---

### 第 2 章 · Čech 上同调与谱序列 ⭐⭐⭐

> Čech 复形 / 好覆盖 / Čech-de Rham 双复形 / 谱序列 $E_r^{p,q}$ / 微分 $d_r$ / 收敛 / Künneth 公式 / Thom 同构

- **核心**:全书最精妙也最硬的一章——引入**谱序列**这个「收敛机器」,把 de Rham 上同调(微分形式视角)
  与 Čech 上同调(组合拼接视角)用**双复形**统一起来。出发点是给流形 $M$ 一个**好覆盖**(good cover)
  $\mathcal{U}=\{U_\alpha\}$——每个有限交 $U_{\alpha_0}\cap\cdots\cap U_{\alpha_q}$ 都可缩($\simeq\mathbb{R}^n$)。
  Bott-Tu 的招牌是:多数教材把谱序列讲得晦涩,本书用「双复形的两个滤波」给出最清晰的几何画面。

- **关键子结果**:
  - **好覆盖**:开覆盖使所有有限交可缩。关键定理:**任何流形有好覆盖**
    (用黎曼度量取测地凸邻域,Petersen GTM171 Ch2 的工具)。好覆盖的 nerve(神经复形)编码 $M$ 的同伦型(nerve 定理)。
  - **Čech 复形**:好覆盖 $\mathcal{U}$ 的 $q+1$ 重交上的常值函数构成 $C^q(\mathcal{U},\mathbb{R})$,
    其上同调 $H^*(\mathcal{U},\mathbb{R})$ 编码「局部数据能否拼成全局」——拼接障碍 = Čech 上同调类。
  - **Čech-de Rham 双复形** $K^{p,q}=C^p(\mathcal{U},\Omega^q)$:把两个复形叠加成一张二维网格——
    横向是 Čech 微分 $\delta$(拼接),纵向是 de Rham 微分 $d$(微分形式)。
    **广义 Mayer-Vietoris 原理**:双复形 $K$ 在「除一个角外」处处 acyclic(局部 Poincaré 引理),
    故总上同调 $H^*(K)$ 同时等于 de Rham(按列滤波)与 Čech(按行滤波)——
    由此 $H^*_{dR}(M)\cong H^*(\mathcal{U},\mathbb{R})$,这是 de Rham 定理的「双复形证明」,比第1章更深刻。
  - **谱序列的构造**:双复形 $K$ 有两个滤波(按列 $F_I$、按行 $F_{II}$),各生一个谱序列。
    按列滤波的谱序列从「先纵向(de Rham)再横向(Čech)」的 iterated 上同调出发,
    第2页 $E_2^{p,q}=H^p_\delta H^q_d(K)$ 逐页逼近 $H^{p+q}_{dR}(M)$。
    好覆盖使 $E_2^{p,q}=0$ 当 $q>0$(局部 Poincaré),故谱序列在第2页**坍缩**(degenerate),立即给 Čech = de Rham。
  - **Künneth 公式**:谱序列应用于投影 $M\times N$,取「柱形好覆盖」,谱序列坍缩给
    $H^*_{dR}(M\times N)\cong H^*_{dR}(M)\otimes H^*_{dR}(N)$(域上张量积,无 $\mathrm{Tor}$)。
  - **Thom 同构**:定向秩 $n$ 向量丛 $\pi:E\to M$ 上,$H^k(M)\cong H^{k+n}_{cv}(E)$($cv$=紧垂直支撑),
    由 $\omega\mapsto\pi^*\omega\wedge\Phi$ 给出,$\Phi\in H^n_{cv}(E)$ 是 **Thom 类**。
    Thom 类是第3章 Euler 类、Gysin 序列的种子。

- **飞腾锚点**:**GEMM 9.45G[Lab05]** ⭐ —— 谱序列是一张 $(p,q)$ 双指标的「页」,每页是双分次线性代数,$d_r$ 是跨 $r$ 步的矩阵运算。
  - 🟢事实:每页 $E_r^{p,q}$ 是一个二维网格,同调运算 $\ker d_r/\mathrm{im}\,d_r$ 是分块矩阵的核/像商(密集 GEMM);
    $d_r:E_r^{p,q}\to E_r^{p+r,q-r+1}$ 的双指标位移像 GEMM 双索引页寻址,翻页 = 矩阵分块消元。
    好覆盖使 $E_2$ 页大量为零(稀疏),谱序列「坍缩」= 稀疏 GEMM 提前结束。
  - 🟡类比:谱序列像「逐页化简的 Excel 表格」——初始页 $E_0$ 是双复形原始数据,
    每翻一页 $d_r$ 把跨 $r$ 格的项消掉,最终页只剩「压不扁的余项」就是目标上同调。
    坍缩(degenerate)= 某页起 $d_r=0$,表格冻结,提前出答案。

- **关键定理**:**Čech-de Rham 同构(广义 Mayer-Vietoris)+ 谱序列收敛 + Thom 同构**。好覆盖 $\mathcal{U}$ 下:
  $$
  H^*_{dR}(M)\ \cong\ H^*(\mathcal{U},\mathbb{R}),\qquad E_2^{p,q}=H^p_\delta\big(H^q_d(K)\big)\ \Rightarrow\ H^{p+q}_{dR}(M).
  $$
  $$
  \text{定向秩 }n\text{ 向量丛 }E\to M:\quad \smile\,\Phi:\ H^k(M)\xrightarrow{\ \sim\ }H^{k+n}_{cv}(E)\quad(\Phi=\text{Thom 类}).
  $$

- **自测**:取 $S^2$ 的好覆盖 $\mathcal{U}=\{U_0,U_1,U_2\}$(三个开半球,两两交 $\simeq\mathbb{R}$,三重交 $\simeq\mathbb{R}$),
  写出 Čech 复形 $C^0\to C^1\to C^2$,算出 $H^0(\mathcal{U})=\mathbb{R}$、$H^2(\mathcal{U})=\mathbb{R}$、$H^1=0$,与 $H^*_{dR}(S^2)$ 核对;
  再说明谱序列为何在第2页坍缩(好覆盖使 $E_2^{p,q}=0$ 当 $q>0$,只剩底行 $E_2^{p,0}=H^p(\mathcal{U})$)。

---

### 第 3 章 · 谱序列的应用与纤维丛 ⭐⭐⭐

> 路径纤维丛 / Serre 谱序列 / Gysin 序列 / 有理同伦论 / Chern-Weil 示性类 / Pontryagin 类 / Euler 类

- **核心**:全书回报最丰的一章——把第2章的谱序列机器接到**纤维丛**上,算出示性类,
  并用微分形式刻画有理同伦型。开篇用**路径纤维丛** $\Omega S^n\to PS^n\to S^n$
  ($PS^n$=路径空间可缩;$\Omega S^n$=环路空间)作示范:总空间可缩,谱序列从底 $S^n$ 与纤维 $\Omega S^n$
  出发逼近 $H^*(PS^n)$,反推出 $H^*(\Omega S^n)$——「用谱序列从底空间反推纤维上同调」的经典。
  章后半转向**示性类的微分形式构造**(Chern-Weil 理论):给向量丛配联络与曲率 $\Theta$,
  不变多项式 $P(\Theta)$ 的 de Rham 类就是示性类。Bott 的大师手笔在此闪光——
  示性类不再是抽象公理,而是可手算的微分形式。

- **关键子结果**:
  - **Serre 谱序列**:纤维丛 $F\to E\xrightarrow{\pi}B$,$B$ 单连通时,
    $E_2^{p,q}=H^p(B;H^q_{dR}(F))\Rightarrow H^{p+q}_{dR}(E)$——底与纤维的上同调「拼」出总空间的上同调。
    微分 $d_r$ 横移 $r$、纵移 $-(r-1)$。关键应用:从已知的底 $B$ 与纤维 $F$ 算 $E$(如 Hopf 纤维化 $S^1\to S^3\to S^2$),
    或反推($E$ 可缩时反算 $F$,即算 $K(\mathbb{Z},n)$ 的上同调)。
  - **Gysin 序列**:球面丛 $S^{n-1}\to E\to B$ 的 Serre 谱序列坍缩为长正合 **Gysin 序列**
    $\cdots\to H^k(B)\xrightarrow{\smile e}H^{k+n}(B)\xrightarrow{\pi^*}H^{k+n}(E)\to H^{k+1}(B)\to\cdots$,
    扭曲项是 **Euler 类** $e\in H^n(B)$。它把「球面丛的非平凡性」编码进一个上同调类。
  - **Chern-Weil 理论**:复向量丛 $E\to M$ 配联络 $\nabla$,曲率 $\Theta\in\Omega^2(\mathrm{End}\,E)$。
    全曲率形式 $\det(I+\frac{i}{2\pi}\Theta)=1+c_1+c_2+\cdots$ 的系数 $c_k\in H^{2k}_{dR}(M)$ 是 **Chern 类**,
    与联络选取无关(不变多项式 + Bianchi 恒等式 $\nabla\Theta=0$ 保证)。
    这是示性类的「可计算」定义——给联络算曲率,展开行列式即得。
  - **Pontryagin 类与 Euler 类**:实丛的 Pontryagin 类 $p_k=(-1)^k c_{2k}(E\otimes\mathbb{C})\in H^{4k}$;
    定向实秩 $n$ 丛的 Euler 类 $e\in H^n$ 是「Thom 类在零截面的拉回」,$e$ 模 $2$ = 顶 Stiefel-Whitney 类。
    Euler 类的积分 $\int_M e=$ Euler 示性数 $\chi(M)$(Gauss-Bonnet 的高维推广)。
  - **有理同伦论**(Sullivan):给 $M$ 配一个自由微分分次代数(最小模型)$(\wedge V,d)$,其上同调 = $H^*_{dR}(M)$。
    定理:$\pi_*(M)\otimes\mathbb{Q}$ 由最小模型完全决定——「de Rham 数据足够恢复有理同伦型」。
    这是 Bott-Tu 对「微分形式能做多少拓扑」的终极回答。

- **飞腾锚点**:**TLB 4.81×[E04]** ⭐ —— 纤维丛是「局部平凡($U\times F$)但全局可能扭曲」,好覆盖把局部数据拼成全局,谱序列是局部→整体的寻址管道。
  - 🟢事实:纤维丛的局部平凡化 = TLB 页表(每点 $b\in B$ 查「地址」得纤维 $F$ 的拷贝);
    迁移函数 $g_{\alpha\beta}:U_\alpha\cap U_\beta\to G$ = 跨页的地址重映射;
    好覆盖使谱序列在第2页坍缩(局部信息一致),TLB 命中率高(局部性好)。
    Serre 谱序列把「底 $B$ 的页」与「纤维 $F$ 的页」拼成「总 $E$ 的页」——双索引高命中寻址。
  - 🟡类比:示性类度量「丛的扭曲」,像 TLB 缺页率度量「地址映射的非平凡性」——
    平凡丛(扭曲为零)对应示性类全为零,非平凡丛(Hopf 纤维化)有非零 Chern 类($c_1\ne0$)。
    Euler 类的积分 = Euler 示性数,是「扭曲的总量统计」。

- **关键定理**:**Serre 谱序列 + Chern-Weil 示性类构造**。
  $$
  F\to E\xrightarrow{\pi}B\ (B\ \text{单连通})\ \Longrightarrow\ E_2^{p,q}=H^p\big(B;\,H^q_{dR}(F)\big)\ \Rightarrow\ H^{p+q}_{dR}(E)\quad\text{(Serre 谱序列)}.
  $$
  $$
  c(E)=\det\!\Big(I+\frac{i}{2\pi}\Theta\Big)=1+c_1+c_2+\cdots,\quad c_k\in H^{2k}_{dR}(M),\ \Theta=\text{曲率}\quad\text{(Chern-Weil,与联络无关)}.
  $$

- **自测**:用 Serre 谱序列算 Hopf 纤维化 $S^1\to S^3\to S^2$:底 $H^*(S^2)=\mathbb{R}[u]/u^2$($|u|=2$),
  纤维 $H^*(S^1)=\mathbb{R}[a]/a^2$($|a|=1$),$E_2$ 页只有 $(0,0),(2,0),(0,1),(2,1)$ 四格非零,
  $d_2(a)=u$ 逼出 $H^*(S^3)=\mathbb{R}$ 在 $0,3$ 阶(谱序列把 $a$ 与 $u$ 配对消掉,剩 $a\cdot u$ 在 $(2,1)$ 即 $3$ 阶);
  再说明 $S^2$ 上 Hopf 丛的伴随复线丛的 $c_1\ne0$(第一 Chern 类 = Euler 类 = 生成元 $u$)。

---

### 附录 · 李群 / 李代数 / 向量丛回顾

> 李群与李代数 / 指数映射 / 伴随表示 / 向量丛 / 截面 / 联络与曲率

- **核心**:为第3章示性类(Chern-Weil)与主丛补充前置工具,快速回顾三大块。
  (i) **李群** $G$ 是带光滑结构的群,其**李代数** $\mathfrak{g}=T_eG$ 用括号 $[X,Y]$ 编码群的局部结构;
  **指数映射** $\exp:\mathfrak{g}\to G$ 把线性化的李代数还原成群;
  **伴随表示** $\mathrm{Ad}:G\to GL(\mathfrak{g})$ 描述群对自身李代数的作用(接 Hall《李群李代数》stage-2)。
  (ii) **向量丛** $E\to M$ 是「每点挂一片向量空间」的层叠结构,局部平凡($E|_U\cong U\times\mathbb{R}^k$)、全局可能扭曲;
  **截面** $s:M\to E$($\pi\circ s=\mathrm{id}$)是丛上的「函数推广」(切向量场 = 切丛截面);
  **联络** $\nabla$ 给截面的方向导数,**曲率** $\Theta=\nabla^2$ 度量联络的非交换性。
  这套语言是 Petersen GTM171 Ch2-3 的浓缩版,这里用于第3章把联络/曲率接到 Chern-Weil 上。

- **飞腾锚点**:**matmul 15×[V03]** —— 向量丛的纤维是 $k$ 维向量空间,曲率 $\Theta\in\Omega^2(\mathrm{End}\,E)$ 逐点是 $k\times k$ 矩阵。
  - 🟢事实:曲率 $\Theta$ 是取值于 $\mathfrak{gl}(k)$ 的 $2$-形式,局部是 $k\times k$ 矩阵的 $2$-形式;
    Chern-Weil 的 $\det(I+\frac{i}{2\pi}\Theta)$ 是矩阵多项式,实现上是批量 matmul($k\times k$ 矩阵幂和 + 行列式);
    联络 $\nabla=d+A$($A$=联络形式)的协变导数是矩阵值 $1$-形式加法。
  - 🟡类比:向量丛像张量的「通道维度」——底空间 $M$ 是空间维,纤维 $\mathbb{R}^k$ 是通道维,
    曲率是「通道间的旋转/扭曲」(类 CNN 的通道注意力);联络 = 沿底空间移动时的「通道对齐规则」。

- **关键概念**:**曲率 = 联络的平方** $\Theta=\nabla^2$,Bianchi 恒等式 $\nabla\Theta=0$ 保证
  不变多项式 $P(\Theta)$ 闭($dP(\Theta)=0$),故 $P(\Theta)$ 定义 de Rham 类(Chern-Weil 的可计算性根基)。

- **自测**:验证平凡丛 $E=M\times\mathbb{R}^k$ 取平凡联络 $\nabla=d$(联络形式 $A=0$)时曲率 $\Theta=0$,
  故所有 Chern 类 $c_k=0$($k\ge1$);说明非平凡联络(如 $S^2$ 上带磁单极的复线丛)如何给出 $c_1\ne0$。

---

## §9 思想主线

Bott-Tu 全书有两条交织的主线。

**第一条:微分形式作为代数拓扑的计算工具。** de Rham 复形(Ch1)把「拓扑洞」变成「闭/恰当形式的商」
$H^k=\ker d/\mathrm{im}\,d$——这是纯分析对象,却忠实度量拓扑。积分(Stokes 定理)与配对(Poincaré 对偶)
让上同调可手算,de Rham 定理钉死它与奇异上同调等价。「微分形式 = 流形上的代数探测器,积分 = 探测器的读数」
是第1章的灵魂。

**第二条:谱序列作为收敛机器。** Čech-de Rham 双复形(Ch2)把「局部好覆盖的数据」生出的 $(p,q)$ 网格
$E_r^{p,q}$ 逐页化简,最终收敛到全局 de Rham 上同调——「局部 → 整体」的机械化桥梁。
第3章把同一机器接到纤维丛上:Serre 谱序列从底与纤维拼出总空间,Chern-Weil 理论把联络曲率变成示性类。

**两条主线合流于一个命题:用微分形式的代数(可计算、可手算)忠实捕获流形的拓扑与丛的扭曲。**
这正是 Bott-Tu 区别于 Hatcher(纯组合)、Warner(纯分析)的独特气质。

### 全书脉络一览(红线串联)

> 下表把三章的核心机器、产出与飞腾锚点集中对照,与 §1 骨架表互补:§1 按「学什么」排,本表按「为什么」排。

| 章 | 核心机器 | 关键产出 | 飞腾/工程锚点 |
|---|---|---|---|
| 1 | de Rham 复形 $d^2=0$ | 上同调 $H^*_{dR}$ / Poincaré 对偶 / de Rham 定理 | Iron Law<2%[Lab00] 正合铁律 |
| 2 | Čech-de Rham 双复形 → 谱序列 | $E_r^{p,q}\Rightarrow H^*_{dR}$ / Künneth / Thom 类 | GEMM 9.45G[Lab05] 双索引页 |
| 3 | Serre 谱序列 + Chern-Weil | 示性类 $c_k,p_k,e$ / 有理同伦型 | TLB 4.81×[E04] 局部→整体 |
| 附录 | 李群/李代数/向量丛/联络 | 曲率 $\Theta=\nabla^2$(Chern-Weil 的原料) | matmul 15×[V03] 矩阵值形式 |

**三条红线**:
1. **可计算性红线**——de Rham 复形(Ch1,积分可算)→ Chern-Weil(Ch3,曲率可算),全书强调「能手算的拓扑」。
2. **局部→整体红线**——Poincaré 引理(局部无洞,Ch1)→ Mayer-Vietoris(拼接,Ch1)→ 谱序列(逐页收敛,Ch2-3),局部数据逐级合成全局不变量。
3. **统一性红线**——de Rham = Čech = 奇异(三套上同调合流),de Rham 代数决定有理同伦型(Ch3),微分形式一统天下。

---

## §10 与本仓库其他笔记的交叉引用

- **Fulton《代数拓扑》GTM153**(stage-2):Bott-Tu 是 Fulton 的**微分形式下游**。
  Fulton Ch6-10 给了奇异同调/上同调/杯积/Poincaré 对偶的组合骨架;Bott-Tu Ch1 用 de Rham 上同调**重做同一套结构**——
  Poincaré 对偶(Fulton Ch10)变成「积分配对 $H^k\cong H^{n-k}$」(更可算),
  Mayer-Vietoris(Fulton Ch8)变成 de Rham 版的长正合序列。
  读 Bott-Tu 前应有 Fulton Ch6-10 的上同调概念打底,否则 de Rham 视角缺乏「拓扑洞」的直觉锚点。
- **Weibel《同调代数》**(stage-3):Bott-Tu Ch2 的谱序列是 Weibel Ch5(谱序列)的**几何原型**。
  Bott-Tu 的双复形、$E_r^{p,q}$、$d_r$、收敛($\Rightarrow$)在 Weibel 里抽象为一般 Abel 范畴的谱序列;
  读 Bott-Tu Ch2 后再读 Weibel Ch5,会看到「逐页化简的双指标网格」如何变成纯代数的「滤波复形的关联分次」。
- **Petersen《黎曼几何》GTM171**(stage-2):Petersen Ch1-3(度量/联络/曲率)是 Bott-Tu **附录与 Ch3 的前置**。
  Bott-Tu 附录的「向量丛 + 联络 + 曲率」是 Petersen Ch2(Levi-Civita 联络)+Ch3(曲率张量 $R$)的浓缩;
  Ch3 的 Chern-Weil 理论直接用 Petersen 的曲率形式语言。读 Bott-Tu Ch3 前建议复习 Petersen Ch2-3。
- **Gamelin 复分析**(stage-2):Bott-Tu Ch1 的 de Rham 复形与 Stokes 定理是 Gamelin 的 Cauchy 定理($\oint f\,dz=0$)的**高维推广**。
  Gamelin 的全纯 $1$-形式 $f(z)\,dz$ 是闭形式($d(f\,dz)=0$ 当 $f$ 全纯),Cauchy 积分公式 = 「闭形式的环路积分」,
  与 de Rham 上同调的积分配对同源。
- **AI 锚点(飞腾 D3000M 映射)**:
  - 🟢 **de Rham 复形 $d^2=0$ = 铁律正合**(闭/恰当的商 = 拓扑洞,数值须 $D^2=0$ 严格归零,类 Iron Law <2%,Ch1);
  - 🟢 **谱序列 $E_r^{p,q}$ = 逐页化简的双索引网格**(每页双分次线性代数,$d_r$ 跨 $r$ 步消元,翻页 = 分块矩阵 GEMM,Ch2);
  - 🟢 **纤维丛 = 局部平凡的层叠寻址**(局部平凡化 = TLB 页表,迁移函数 = 地址重映射,示性类 = 扭曲度量,Ch3 TLB);
  - 🟡 **Chern-Weil = 曲率的不变量提取**(联络曲率 $\Theta$ 取行列式/幂和 = 矩阵 matmul 提取拓扑不变量,附录 matmul);
  - 🟡 **Serre 谱序列 = 底×纤维 → 总空间的「卷积」**(底 $B$ 与纤维 $F$ 的上同调「卷积」出总空间 $E$,像双线性融合,Ch3)。

> **下一步**:沿 `01-track/stage-2` 精读 Bott-Tu Ch1(de Rham 上同调,手算 $S^1,S^2$ 的 $H^*_{dR}$),
> 遇关键概念查 `00-META/CONCEPT-INDEX` 中「极限/特征值/对称」视角;
> Ch2 谱序列是全书难关,建议纸笔画 $E_r^{p,q}$ 网格逐页翻;Ch3 示性类配 Petersen Ch2-3 联读。
>
> **stage-3 前瞻**:Chern-Weil 示性类 → Milnor-Stasheff《示性类》/ Atiyah-Singer 指标定理;
> 有理同伦论 → Sullivan 最小模型 / 代数拓扑研究方向;谱序列 → Weibel 同调代数 Ch5。
>
> **实操验证**(建议用 Python/SciPy):
> - 用 `scipy.sparse` 实现 de Rham 复形的 $d$ 矩阵,验证 $D^2=0$(Ch1)
> - 用 Dijkstra / 单位分解在三角网格上数值积分 Stokes 定理(Ch1)
> - 用 `numpy.einsum` 实现 Chern-Weil 行列式 $\det(I+\frac{i}{2\pi}\Theta)$(Ch3)
> - 用谱序列网格($E_r^{p,q}$ 字典)手算 Hopf 纤维化 $S^1\to S^3\to S^2$(Ch3)

---

## §11 自测答案要点(供核对)

1. **Ch1** $S^1$ 拆 $U,V$(开区间),$U\cap V=$ 两段(同伦于两点)。Mayer-Vietoris:$0\to H^0(S^1)\to H^0(U)\oplus H^0(V)\to H^0(U\cap V)=\mathbb{R}^2\xrightarrow{\partial}H^1(S^1)\to0$。$H^0(U)\oplus H^0(V)=\mathbb{R}^2\to\mathbb{R}^2$ 的像是一维(常函数),故 $\ker\partial$ 给 $H^0(S^1)=\mathbb{R}$,$\mathrm{coker}$ 给 $H^1(S^1)=\mathbb{R}$。紧支撑:$H^1_{dR,c}(\mathbb{R})=\mathbb{R}$ 因鼓包 $f(x)dx$($\int f\ne0$)闭且非恰当(紧支撑下无整体原函数),而 $H^1_{dR}(\mathbb{R})=0$ 因 $\frac{dx}{1+x^2}=d(\arctan x)$ 恰当(无紧支撑约束)。
2. **Ch2** $S^2$ 三开半球好覆盖:$C^0=\mathbb{R}^3,C^1=\mathbb{R}^3,C^2=\mathbb{R}$(三重交非空)。Čech 微分 $\delta:C^0\to C^1$ 是 $(f_\alpha)\mapsto(f_\beta-f_\alpha)$,$\delta:C^1\to C^2$ 类似。$\ker\delta^0=$ 常值($1$ 维)=$H^0$;$H^2=\mathrm{coker}\,\delta^1=\mathbb{R}$(交替和);$H^1=0$。谱序列第2页坍缩:好覆盖使 $H^q_d(U_{\alpha_0\cdots\alpha_p})=0$($q>0$),故 $E_2^{p,q}=0$($q>0$),只剩 $E_2^{p,0}=H^p(\mathcal{U})$,$d_2=0$,冻结出答案。
3. **Ch3** Hopf 纤维化 $S^1\to S^3\to S^2$:Serre 谱序列 $E_2^{p,q}=H^p(S^2)\otimes H^q(S^1)$。非零格:$(0,0),(2,0),(0,1),(2,1)$。$d_2:E_2^{0,1}\to E_2^{2,0}$ 必须是同构(否则 $E_\infty$ 会给 $H^2(S^3)\ne0$,矛盾),即 $d_2(a)=u$。坍缩后 $E_\infty$ 只剩 $(0,0)$ 与 $(2,1)$,即 $H^0(S^3)=\mathbb{R},H^3(S^3)=\mathbb{R}$,其余 $=0$。Hopf 丛的 $c_1$:标准联络曲率 $\Theta=du$(面积形式),$c_1=\frac{i}{2\pi}\mathrm{tr}\,\Theta=\frac{1}{2\pi}u\ne0$。
4. **附录** 平凡丛 $\nabla=d$($A=0$):$\Theta=dA+A\wedge A=0$,故 $c(E)=\det(I+0)=1$,即 $c_k=0$($k\ge1$)。磁单极丛($S^2$ 上 tautological 线丛):取球极联络 $A=\frac{1}{2}(1-\cos\theta)d\varphi$,曲率 $\Theta=dA=\frac{1}{2}\sin\theta\,d\theta\wedge d\varphi$(面积形式之半),$c_1=\frac{i}{2\pi}\Theta=\frac{1}{4\pi}\sin\theta\,d\theta\wedge d\varphi\ne0$。

> **核对原则**:Ch1 的核心是「$d^2=0$ 铁律 + 拼接正合性」;Ch2 的核心是「好覆盖使谱序列在第2页坍缩」;Ch3 的核心是「Serre 谱序列的微分 $d_r$ 逼出上同调关系 + Chern-Weil 把曲率变成示性类」。若结论不依赖谱序列(如 Ch1),属「奠基」;依赖谱序列(Ch2-3),属「收敛机器」。

> **读法建议**:第一遍精读 Ch1(de Rham 上同调,手算 $S^1,S^2$,对应 CONCEPT-INDEX「极限/特征值」视角);
> 第二遍死磕 Ch2 谱序列(纸笔画 $E_r^{p,q}$ 网格);第三遍选读 Ch3 示性类(配 Petersen Ch2-3,作为 stage-3 示性类/指标定理的跳板)。
