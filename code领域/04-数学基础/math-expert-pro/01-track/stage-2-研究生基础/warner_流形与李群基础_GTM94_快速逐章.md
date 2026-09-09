# Frank W. Warner《流形与李群基础》(GTM 94) · 快速逐章精读

> 基于原书：Foundations of Differentiable Manifolds and Lie Groups, Frank W. Warner, GTM 94, Springer, 1983 / 读于：2026-07-03
> 定位：**少数「微分流形 + 李群 + 紧李群表示」一站式打通的书**，以光滑流形、微分形式、Stokes 积分为 Part I，李群、Lie 代数、Peter-Weyl 表示为 Part II，用「流形 + 微分形式 + 李群」三柱贯穿现代微分几何与表示论。
> 本文为**快速逐章精读**，每章 1 个飞腾锚点 + 1 个关键定理 + 1 道自测题。

---

## §0 引言：Warner 是什么，为什么读它

Warner《流形与李群基础》(GTM 94, 1983) 是一本定位独特的研究生教材。它最难得的地方在于**用一本书把两条通常分家的大线合起来讲**：Part I（Ch 1–4）给微分流形、切丛、微分形式、外微分、Stokes 定理、de Rham 上同调与 Poincaré 对偶的完整分析-拓扑基础；Part II（Ch 5–6）给李群、Lie 代数、指数映射、伴随表示、homogeneous 空间 $G/H$，最终推向紧李群表示论的顶峰——Haar 测度、Peter-Weyl 定理、最大环面、Weyl 群、Weyl 特征公式。市面上大多数书要么只讲流形（Lee、Spivak、Bott-Tu），要么只讲李群/表示（Hall、Fulton-Harris、Serre 有限群线性表示），Warner 是少数能让读者**一本书看到「光滑流形 → 微分形式 → de Rham 上同调 → 李群作用 → 紧群表示」完整链条**的著作。

**读 Warner 的价值**：当 Lee GTM218 在 Ch 1–8 仔细铺垫光滑结构、切丛、张量场，到 Ch 21 才简略涉及李群；Hall《李群李代数》则直接从矩阵群 $GL(n)$ 入手讲表示，对光滑流形语言只是借用——Warner 把这两块用一个统一的「光滑流形 + 群作用」框架串起来：李群 $G$ 本身就是流形（Ch 1 的语言直接适用），Lie 代数 $\mathfrak{g}$ 是左不变向量场（Ch 3 向量场的特例），homogeneous 空间 $G/H$ 是 $G$ 作用在流形上的商（Ch 1 子流形 + Ch 2 商拓扑）。这种「几何↔代数无缝衔接」让读者看清**李群的几何本质（光滑对称性）与代数本质（Lie 代数/表示）是同一对象的两面**。

代价是 Part I 与 Lee/Bott-Tu 有重叠，Part II 与 Fulton-Harris/Hall 有重叠——若已精读过那些专著，Warner 是「巩固 + 衔接」性质；但对想用最少书数打通两块的读者，Warner 是最优选。严格性高、符号现代、定理完整、证明不偷懒，是 GTM 丛书的标杆写法。1983 年成书，至今仍是标准参考。

| 书 | 风格 | 严格性 | 适合谁 |
|---|---|---|---|
| **Warner** GTM94 (1983) | 流形+李群+表示一站式，现代符号，三柱贯通 | 高，自包含，定理完整证明不偷懒 | 想用最少书数打通几何↔代数的读者 |
| **Lee** GTM218 光滑流形 (2012) | 友好递归，每概念先铺垫，习题丰富 | 高，自包含，最现代 | 自学零基础，怕抽象，专攻流形 |
| **Lee** GTM202 拓扑流形 (2011) | 同 Lee 风格，侧重拓扑流形与基本群 | 高，自包含 | 先建拓扑再上光滑，配 GTM218 |
| **Kobayashi-Nomizu** 卷I (1963) | 主丛联络(Cartan 形式语言)，百科全书 | 极高，最抽象，符号密集 | 研究者权威参考，需要主丛框架 |
| **Spivak** 微分几何 5 卷 (1979) | 几何直觉 + 历史叙事，最详尽，娓娓道来 | 高，叙事流畅 | 建立直觉后的纵深阅读 |

**建议路线**：Lee GTM218 先读（建光滑流形严格基础，现代友好）→ Warner Part I 对照（同一内容的 1983 经典版，互补）→ Warner Part II 攻李群 + 紧李群表示（Lee GTM218 没有的纵深）→ Fulton-Harris/Hall 扩展表示论 → Kobayashi-Nomizu 卷I 补主丛联络统一框架。Warner 在这条链上居「流形→李群桥梁」枢纽位。

**与现代教材的定位差异**：Warner（1983）成书早于 Lee（2012/2011）、Fulton-Harris（1991）的流行，符号风格承 Chevalley-Lang 传统，定理陈述简洁直接、不冗余铺垫。相比 Lee 每概念先讲「为什么需要它」的友好递归，Warner 更接近「研究者参考手册」的密度——适合已建基本直觉后回头精读，提取标准陈述与证明骨架。这种「高密度 + 一站式」特质使它在「用最少书数打通几何↔代数」的读者群中不可替代；而 Bott-Tu（de Rham 专题）、KN 卷I（主丛联络专题）则是它在各方向上的纵深补全。

> 🟢 事实可作锚点：Stokes 定理、de Rham 定理、Poincaré 对偶、Lie 三定理、Peter-Weyl 定理、最大环面定理、Weyl 特征公式均为严格定理。
> 🟡 类比（流形=「局部像 $\mathbb{R}^n$ 的空间」、李群=「带光滑对称的流形」、表示=「对称性如何作用在向量上」）仅供直觉，**绝不在严格证明中引用**。

---

## §1 全书骨架一览（飞腾锚点分布）

> **忠于原书说明**：Warner GTM94 原书正文止于第 6 章（紧李群与表示论），无独立第 7 章。下表「延伸」一行为紧李群表示论之后的自然方向（复流形、Kähler、对称空间），**不在原书正文内**，标注为延伸指引，参 Kobayashi-Nomizu 卷II / Helgason / Griffiths-Harris。

| 章 | 标题 | 核心概念 | 飞腾锚点 |
|:-:|------|---------|---------|
| 1 | Manifolds（流形） | 拓扑流形、光滑结构、$C^\infty$ 映射、切丛、张量场、单位分解 | **TLB 4.81×[E04]** ⭐ |
| 2 | Submanifolds and Foliations（子流形与叶状结构） | 秩定理、浸入/嵌入、正则子流形、Frobenius 定理、叶状结构 | **分支预测[Lab02]** |
| 3 | Vector Fields and Differential Forms（向量场与微分形式） | 向量场、流、Lie 导数、外微分 $d$、Cartan 公式、de Rham 复形 | **matmul 15×[V03]** ⭐ |
| 4 | Integration on Manifolds（流形上的积分） | 定向、积分、Stokes 定理、de Rham 定理、Poincaré 对偶 | **UDOT 16.9×[E05]** ⭐ + **Iron Law<2%** |
| 5 | Lie Groups（李群） | 李群、Lie 代数、指数映射、伴随表示、Lie 三定理、homogeneous 空间 | **GEMM 9.45G[Lab05]** |
| 6 | Compact Lie Groups and Their Representations（紧李群与表示）⭐⭐⭐ 高潮 | Haar 测度、Peter-Weyl、最大环面、Weyl 群、Weyl 特征公式 | **Schmidt 正交化** ⭐ |
| 延伸 | Further Topics（复流形/Kähler/对称空间，**非原书**） | 复流形、Kähler 度量、Hermite 形式、对称空间引论 | **FP16 3.81×[L01]** |

**三条主线**：

1. **光滑结构红线**——Ch 1 定义流形 $\to$ Ch 2 子流形/商 $\to$ Ch 3 切丛上的结构（向量场/形式）$\to$ Ch 4 形式的积分，是「从空间到分析」的奠基。
2. **李群红线**——Ch 5 李群本身是流形（Ch 1 语言直接用）+ 群结构 $\to$ Ch 6 紧李群的表示论，是「对称性如何线性化」。
3. **分析↔代数桥梁红线**——Ch 4 Stokes/de Rham（微分形式 ↔ 拓扑）与 Ch 6 Peter-Weyl（群 ↔ 正交函数系）共享「用分析对象刻画代数/拓扑结构」的思想，是 Warner 全书的方法论灵魂。

---

### 第 1 章 · Manifolds（流形）⭐

> 拓扑流形 / 光滑结构（极大图册）/ $C^\infty$ 映射 / 切向量与切丛 $TM$ / 张量代数与张量场 / 单位分解

- **核心**：本章是全书语言地基。
  - **拓扑流形** $M$ 是局部同胚于 $\mathbb{R}^n$ 的 Hausdorff、第二可数空间；**光滑结构**由相容坐标卡 $(U_\alpha,\varphi_\alpha)$ 的极大图册（atlas）定义，转移函数 $\varphi_\beta\circ\varphi_\alpha^{-1}$ 光滑。
  - **切丛** $TM=\bigsqcup T_pM$ 承载向量场；**张量场**是 $(r,s)$ 型多线性代数的光滑截面。
  - **单位分解** $\{\rho_\alpha\}$（从属于局部有限开覆盖）是 paracompactness 的 payoff：它保证 Riemann 度量可整体构造、积分可局部拼、de Rham 理论可用。
- **历史/动机**：Riemann（1854 演讲）提出高维流形概念；Weyl（1913）严格化；Whitney（1936）证明嵌入定理；Warner 在此沿用 Chevalley-Lang 的现代框架。
- **飞腾锚点**：**TLB 4.81×[E04]** ⭐ —— 流形只有局部坐标卡，转移函数 = 跨卡换页表。
  - 🟢事实：TLB 命中率高时内存访问快 4.81 倍；坐标卡的数据常驻缓存，转移函数是小矩阵查表，频繁 atlas 切换会触发 TLB miss。
  - 🟡类比：图册 = 内存页表；转移函数 = TLB 跨页映射；「流形 = 流数据」，跨卡拼接需换映射（换页）。
- **几何/应用**：光滑结构是 Ch 2 子流形、Ch 5 李群（李群本身是光滑流形）的前置；单位分解保证 Ch 4 积分可定义。
- **关键定理**：$$\text{光滑结构存在：paracompact 光滑流形上}\ \exists\ \text{从属于任意开覆盖的单位分解 } \{\rho_\alpha\},\quad \sum\rho_\alpha\equiv1.$$
  - （单位分解 → Riemann 度量 $g=\sum\rho_\alpha g_\alpha$ 整体存在 → Ch 4 积分可定义。）
- **自测**：写出球面 $S^2$ 的两个坐标卡（南北极球极投影）及转移函数；用单位分解说明为什么 paracompact 流形上一定有 Riemann 度量。
- **与 Lee / KN 对照**：Lee GTM218 Ch 1–3（光滑结构/切丛/张量）是 Warner Ch 1 的现代友好版，每个定义配动机与反例（如「光滑结构不唯一」的 exotic $\mathbb{R}^4$）；KN 卷I Ch I 的微分流形与 Warner 同一内容但更紧凑，直接服务于 Ch II 主丛联络。Warner Ch 1 的单位分解（paracompactness 的 payoff）是 Ch 4 积分与 Riemann 度量存在的基石——「单位分解 → 整体存在性」这条逻辑链是分析几何的核心。

---

### 第 2 章 · Submanifolds and Foliations（子流形与叶状结构）

> 秩定理 / 浸入与嵌入 / 正则子流形 / Frobenius 定理 / 叶状结构（foliation）

- **核心**：
  - **秩定理**：若 $f:M^m\to N^n$ 在 $p$ 处秩 $r$ 恒定，则存在坐标使 $f$ 局部化为标准投影 $(x_1,\dots,x_m)\mapsto(x_1,\dots,x_r,0,\dots,0)$。秩恒定 $=r$ 给**浸入**（$r=m$）与**淹没**（$r=n$）两个标准型。
  - **正则子流形**由单射浸入 + 嵌入拓扑给出；**Frobenius 定理**：分布 $D\subseteq TM$ 可积（过每点有极大积分流形）$\Leftrightarrow$ $D$ 闭于 Lie 括号 $[D,D]\subseteq D$。
  - **叶状结构**（foliation）把 $M$ 分解为互相局部平行的「叶子」（leaves），每叶是积分流形；这是 Ch 1 Frobenius 的几何结晶，也是 Ch 5 李群齐性空间 $G/H$（叶子 $=H$ 陪集）的原型。
- **飞腾锚点**：**分支预测[Lab02]** —— 秩的非恒定点（临界点）是「分支」：浸入 vs 淹没 vs 退化，叶状结构的叶分层是离散分类。
  - 🟢事实：分支预测命中 0.71 vs 失误 3.14 周期；秩判定（$df_p$ 的秩是否满）是判号分支，数值检测需稳定的奇异值阈值。
  - 🟡类比：Frobenius 可积 = 「分布处处闭于括号」是全局一致的分支判定；不可积分布 = 分支预测失败（局部积分曲面不存在）。
- **几何/应用**：叶状结构是动力系统（不变流形）、规范理论（D-brane）、机器学习（流形假设下数据的叶状）的共同语言；homogeneous 空间 $G/H$ 的陪集就是最规整的叶状结构。
- **关键定理**：$$\text{Frobenius：}D\text{ 可积}\Leftrightarrow[D,D]\subseteq D;\quad \text{秩定理：rank 恒定}\Rightarrow f\text{ 局部标准型。}$$
- **自测**：用 Frobenius 判定 $\mathbb{R}^3$ 上的分布 $D=\mathrm{span}\{\partial_x,\ \partial_y+x\partial_z\}$ 是否可积；若可积，求其积分曲面族。
- **与 Lee GTM218 / KN 对照**：Lee Ch 5–6（子流形）+ Ch 19（Frobenius/叶状结构）是 Warner Ch 2 的现代友好版，证明更细、反例更丰富；KN 卷I Ch I 的 Frobenius 定理与 Warner 同一结论，但 KN 置于 Lie 群作用与主丛框架下。Warner Ch 2 的叶状结构是 Ch 5 齐性空间 $G/H$（叶子 $=H$ 陪集）的几何原型——这种「叶状 ↔ 齐性空间」的串联是 Warner 一站式写法的独到之处。

---

### 第 3 章 · Vector Fields and Differential Forms（向量场与微分形式）⭐

> 向量场 = 切丛截面 / 积分曲线与流 / Lie 导数 $\mathcal{L}_X$ / 外微分 $d$ / Cartan 魔公式 / de Rham 复形

- **核心**：
  - **向量场** $X\in\Gamma(TM)$ 是切丛的光滑截面；**积分曲线**满足 ODE $\dot\gamma=X(\gamma)$，整体存在性由完备性保证；向量场的**流** $\phi_t$ 给单参数微分同胚群。
  - **Lie 导数** $\mathcal{L}_X$ 度量张量场沿 $X$ 的流的变化率；**外微分** $d:\Omega^k\to\Omega^{k+1}$ 满足 $d^2=0$，给 **de Rham 复形**。
  - **Cartan 魔公式** $\mathcal{L}_X=i_X d+d\,i_X$ 把 Lie 导数拆成外微分 + 内积，是计算 de Rham 上同调与辛几何的核心工具。
  - **de Rham 上同调** $H^k_{\mathrm{dR}}(M)=\ker d_k/\mathrm{im}\,d_{k-1}$（闭形式模恰当形式）是流形的整体拓扑不变量，Ch 4 证明它 $\cong$ 奇异上同调。
- **历史/动机**：Lie（1880s）引入向量场流；Cartan（1920s）发展外微分与活动标架；de Rham（1931）证明上同调定理。
- **飞腾锚点**：**matmul 15×[V03]** ⭐ —— 外代数楔积 $\wedge$、张量缩并是多线性代数，密集矩阵乘加速 15 倍。
  - 🟢事实：$(r,s)$ 型张量场有 $n^{r+s}$ 分量，Lie 导数 $\mathcal{L}_X T$ 涉及 Christoffel 类联络系数的批量缩并，tensor core 加速。
  - 🟡类比：楔积 $\alpha\wedge\beta$ = 反称化的 `einsum`；Cartan 公式 = 「微分 + 投影」两步算子复合；$d^2=0$ = 投影算子的幂等性。
- **几何/应用**：de Rham 复形是辛几何、Hodge 理论、规范理论的公共骨架；Cartan 公式在 Hamilton 力学（辛流形上 $\mathcal{L}_{X_H}\omega=0$）与电磁学（$dF=0$）处处出现。
- **关键定理**：$$d^2=0;\quad \text{Cartan 魔公式：}\mathcal{L}_X=i_X\circ d+d\circ i_X;\quad \text{Poincaré 引理：}\mathbb{R}^n\text{ 上 }H^k_{\mathrm{dR}}=0\ (k>0).$$
- **自测**：在 $\mathbb{R}^3$ 上验证 $d^2=0$（取 $\omega=xdy$，算 $d\omega$ 再算 $d(d\omega)$）；用 Cartan 公式计算 $\mathcal{L}_{\partial_x}(x\,dy)$。
- **与 Bott-Tu / Lee 对照**：Warner Ch 3 是 Bott-Tu Ch 1（de Rham）+ Lee Ch 14–17（向量场/微分形式/Lie 导数）的精要浓缩。Bott-Tu 更深入（Čech-de Rham 复形、谱序列、示性类），Lee 更详尽（每公式配手算反例），Warner 给最干净的标准版以便尽快进入 Ch 4 Stokes 与 Ch 6 表示论。Cartan 魔公式 $\mathcal{L}_X=i_X d+d\,i_X$ 在三书中都居核心，是辛几何（$\mathcal{L}_{X_H}\omega=0$ 给 Hamilton 流）与电磁学（$dF=0$）的公共工具。

---

### 第 4 章 · Integration on Manifolds（流形上的积分）⭐⭐ 全书 Part I 高潮

> 定向 / 流形上的积分 / Stokes 定理 / de Rham 定理 / Poincaré 对偶

- **核心**：本章是「分析 ↔ 拓扑」的桥梁，全书 Part I 的高潮。
  - **定向**由处处非零的体积形式（或坐标卡的相容类）给出；**积分**用单位分解把局部 $\int_U f\,\omega$ 拼成整体 $\int_M\omega$，与坐标卡选取无关。
  - **Stokes 定理**是微积分基本定理的高维推广，把「边界的积分」与「内部的微分」统一：$$\int_M d\omega=\int_{\partial M}\omega.$$
    它是 de Rham 理论、Gauss-Bonnet、电荷守恒（$dF=0$）、留数定理的公共源泉。
  - **de Rham 定理**：$H^k_{\mathrm{dR}}(M)\cong H^k_{\mathrm{sing}}(M;\mathbb{R})$（闭形式模恰当 $\cong$ 奇异上同调），把分析对象（形式）与拓扑对象（链）严格等同。
  - **Poincaré 对偶**：紧可定向 $n$ 维流形上 $H^k\cong H_{n-k}$（上同调与同调互为对偶），配对由积分 $\int_M\alpha\wedge\beta$ 给出。
- **飞腾锚点**：**UDOT 16.9×[E05]** ⭐ —— 积分本质是点积累加（黎曼和），de Rham 上链复形的边缘算子是求和，UDOT 无符号点积累加快 16.9 倍。附 **Iron Law<2%[Lab00]**：离散 Stokes 的数值误差受性能铁律（指令数×CPI×时钟）约束。
  - 🟢事实：$\int_M\omega=\lim\sum f(p_i)\omega(p_i)\Delta V$ 是大批量点积，UDOT 加速；Stokes 离散化（有限元/有限体积）的误差控制是 Iron Law 的应用。
  - 🟡类比：积分 = 加权求和（UDOT）；de Rham 边缘算子 $\partial$ = 求和（上链到上边缘）；Stokes = 「求和与微分交换」的连续极限。
- **几何/应用**：Stokes 是 Maxwell 方程（$\int_{\partial V}\!F=\int_V\!dF$）、复分析留数（$\oint_{\partial D}\!\omega=\int_D\!d\omega$）、电磁学 Gauss 定律的统一形式；de Rham 定理是 Hodge 理论、示性类、指标定理的前置。
- **关键定理**：$$\boxed{\text{Stokes：}\int_M d\omega=\int_{\partial M}\omega;}\quad \text{de Rham：}H^k_{\mathrm{dR}}(M)\cong H^k_{\mathrm{sing}}(M;\mathbb{R});\quad \text{Poincaré 对偶：}H^k\cong H_{n-k}.$$
- **自测**：对 $M=[0,1]$（带边 1 维流形）验证 Stokes 退化为微积分基本定理 $\int_0^1 f'(x)dx=f(1)-f(0)$；计算 $S^1$ 的 $H^1_{\mathrm{dR}}$（提示：闭 1 形式 $c\,d\theta$ 模恰当）。
- **与 Bott-Tu / Spivak 对照**：Warner Ch 4 的 Stokes 证明用单位分解 + 局部化到 $\mathbb{R}^n$ 的微积分基本定理，是最干净的标准版；Bott-Tu Ch 1 给同一证明但额外发展 Mayer-Vietoris 长正合序列与 Poincaré 对偶的层论视角；Spivak《流形上的微积分》给 Stokes 的最直觉版（配图示）。de Rham 定理 $H^k_{\mathrm{dR}}\cong H^k_{\mathrm{sing}}$ 是 Warner Ch 4 的皇冠，证明用「好的覆盖」（good cover）+ Čech-de Rham 双复形——这是 Bott-Tu 的核心方法，Warner 给精要版。

---

### 第 5 章 · Lie Groups（李群）⭐⭐ Part II 入口

> 李群 $G$ / Lie 代数 $\mathfrak{g}$ / 指数映射 $\exp$ / Lie 三定理 / 伴随表示 $\mathrm{Ad},\mathrm{ad}$ / 闭子群定理 / homogeneous 空间 $G/H$

- **核心**：李群 = 群 + 光滑流形，乘法与逆光滑。本章是 Part II 的地基。
  - **Lie 代数** $\mathfrak{g}$ = 左不变向量场（同构于 $T_eG$），括号由向量场括号诱导；$\mathfrak{g}$ 是 $G$ 在单位元的「无穷小对称」。
  - **指数映射** $\exp:\mathfrak{g}\to G$ 由左不变向量场的流定义，矩阵情形即矩阵指数 $e^X=\sum X^k/k!$；它是 Lie 代数（线性）与李群（非线性）的局部微分同胚桥梁。
  - **Lie 三定理**：① 局部同构 ↔ Lie 代数同构；② 连通单连通时 Lie 群同态 ↔ Lie 代数同态（一一对应）；③ 每个有限维实 Lie 代数是某 Lie 群的 Lie 代数（存在性）。
  - **伴随表示** $\mathrm{Ad}:G\to GL(\mathfrak{g})$（$g\mapsto$ 共轭作用在 $\mathfrak{g}$ 上的微分），其微分 $\mathrm{ad}:\mathfrak{g}\to\mathfrak{gl}(\mathfrak{g})$ 即 $\mathrm{ad}_X(Y)=[X,Y]$。
  - **闭子群定理**（Cartan）：$G$ 的闭子群自动是 Lie 子群（光滑结构继承）——这是齐性空间理论的关键。
  - **homogeneous 空间** $G/H$（$H$ 闭子群）是光滑流形，叶子 = $H$ 陪集；球面 $S^n=SO(n+1)/SO(n)$、双曲空间、Grassmann 流形都是此类。
- **历史/动机**：Lie（1880s）研究连续变换群；Cartan（1930）分类半单 Lie 代数；闭子群定理是 Cartan 的深刻贡献。
- **飞腾锚点**：**GEMM 9.45G[Lab05]** —— 线性李群（$GL(n), SO(n), SU(n)$）的群运算 = 矩阵乘，伴随表示 $\mathrm{Ad}(g)X=gXg^{-1}$ 是矩阵共轭，GEMM 每秒 9.45G 运算。
  - 🟢事实：矩阵群的乘法、逆、指数（$e^X$ 用 Padé 逼近，内部是 GEMM）都是密集矩阵吞吐；表示矩阵的张量积 $\pi\otimes\pi'$ 维度爆炸，GEMM 加速。
  - 🟡类比：$\exp$ = 矩阵指数（数值上 $e^X$ 用缩放-平方 + GEMM）；$\mathrm{Ad}$ = 共轭（两次 GEMM）；homogeneous 空间 = 群作用的商，叶子索引 = 陪集查表。
- **几何/应用**：李群是规范理论（$U(1), SU(3)$）、相对论（Lorentz 群 $SO(1,3)$）、机器人（$SE(3)$ 刚体运动）、量子力学（旋转 $SU(2)$）的对称性语言；homogeneous 空间是 Riemann 对称空间（延伸章）的原型。
- **关键定理**：$$\text{Lie 第二定理：}\ G,\tilde G\text{ 连通单连通}\Rightarrow \mathrm{Hom}_{Lie}(G,\tilde G)\cong\mathrm{Hom}_{Lie\text{-alg}}(\mathfrak{g},\tilde{\mathfrak{g}});$$
  $$\text{Lie 第三定理：}\ \forall\ \mathfrak{g}\ \exists\ G,\ \mathrm{Lie}(G)=\mathfrak{g};\quad \text{闭子群定理：}H\leq G\text{ 闭}\Rightarrow H\text{ 是 Lie 子群。}$$
- **自测**：写出 $SO(3)$ 的 Lie 代数 $\mathfrak{so}(3)$（$3\times3$ 反称矩阵，基 $L_x,L_y,L_z$，换位 $[L_x,L_y]=L_z$）；验证 $SU(2)\to SO(3)$ 是 2:1 覆叠（Lie 代数同构但群不同构）。
- **与 Hall / Fulton-Harris 对照**：Warner Ch 5 是 Hall《李群李代数》Ch 1–5（矩阵群友好入门）+ Fulton-Harris Ch I（Lie 代数基础）的浓缩。Hall 从 $GL(n)$ 矩阵群直接入手，几何门槛最低、可手算；Fulton-Harris 侧重根系/最高权分类与表示构造；Warner 给 Lie 三定理 + 闭子群定理 + homogeneous 空间的标准抽象版，是 Ch 6 紧李群表示论的直接前置。读法：Hall 先建矩阵群直觉 $\to$ Warner Ch 5 补抽象框架与齐性空间 $G/H$ $\to$ Fulton-Harris 攻根系分类与表示构造。

---

### 第 6 章 · Compact Lie Groups and Their Representations（紧李群与表示）⭐⭐⭐ 全书高潮

> Haar 测度 / Peter-Weyl 定理 / 最大环面 / Weyl 群 / Weyl 积分公式 / Weyl 特征公式

- **核心**：本章是 Warner 全书的 payoff，把 Part I 的分析工具（积分、正交系）与 Part II 的代数对象（李群、表示）完美结合。
  - **Haar 测度**：紧群上有唯一（规范）左不变测度 $dg$，使 $L^2(G)$ 成 Hilbert 空间——这是「在群上做调和分析」的基础。
  - **Peter-Weyl 定理**（1927）：紧李群 $G$ 的 $L^2(G)$ 分解为有限维不可约表示的直和，矩阵系数 $\sqrt{\dim\pi}\,\pi_{ij}(g)$ 构成 $L^2(G)$ 的正交基。这是紧群上的「Fourier 级数推广」——$S^1$ 退化为经典 Fourier 级数，$SU(2)$ 给 spin 表示分解。
  - **最大环面** $T$：$G$ 中极大连通交换子群（$\cong$ 环面 $S^1\times\cdots\times S^1$）；**最大环面定理**：最大环面两两共轭，每个元素共轭于 $T$ 中某元素——「分类共轭类只需分类 $T/W$」。
  - **Weyl 群** $W=N(T)/T$（正规化子模环面）是有限反射群，作用在 $T$ 的 Lie 代数 $\mathfrak{t}$ 上；对 $SU(n)$ 是 $S_n$（置换群）。
  - **Weyl 积分公式**：把 $G$ 上的积分约化为 $T/W$ 上的积分（带 Weyl 判别式 $|\Delta(e^{iH})|^2$）。
  - **Weyl 特征公式**：不可约表示 $\pi_\lambda$ 的特征 $\chi_\lambda$ 在 $T$ 上由最高权 $\lambda$ 显式给出（见关键定理）——这是紧李群表示论的皇冠定理。
- **历史/动机**：Peter-Weyl（1927）把 Fourier 分析推广到紧群；Weyl（1925–26）用最大环面 + 特征公式完成紧半单 Lie 群分类。
- **飞腾锚点**：**Schmidt 正交化** ⭐ —— Peter-Weyl 的矩阵系数是 $L^2(G)$ 的正交基（Schur 正交关系），Weyl 特征公式的分子分母都是 $W$-交错指数和，本质是正交系的构造。
  - 🟢事实：Schur 正交关系 $\int_G \pi_{ij}(g)\overline{\pi'_{kl}(g)}\,dg=\frac{\delta_{\pi\pi'}\delta_{ik}\delta_{jl}}{\dim\pi}$ 是正交投影的精确表述；Peter-Weyl = 「群上的 Schmidt 正交化」。
  - 🟡类比：Peter-Weyl 之于紧李群 = Fourier 级数之于 $S^1$ = Schmidt 正交化之于任意内积空间；最高权 $\lambda$ 标记不可约表示 = 频率 $n$ 标记 $e^{in\theta}$。
- **几何/应用**：Peter-Weyl 是量子化学（分子对称群）、粒子物理（$SU(3)$ 夸克模型、八重道）、信号处理（球面调和 = $SO(3)$ 表示）的数学基础；Weyl 特征公式是计算任何紧群表示特征的通用算法。
- **关键定理**：$$\text{Peter-Weyl：}L^2(G)\cong\widehat{\bigoplus_{\pi\in\hat G}}\ V_\pi\otimes V_\pi^*\ \text{（矩阵系数正交基）};$$
  $$\boxed{\text{Weyl 特征公式：}\chi_\lambda(e^H)=\frac{\sum_{w\in W}\varepsilon(w)\,e^{i\langle w(\lambda+\rho),H\rangle}}{\sum_{w\in W}\varepsilon(w)\,e^{i\langle w\rho,H\rangle}},\quad \rho=\frac12\sum_{\alpha>0}\alpha.}$$
- **自测**：对 $SU(2)$（$\cong S^3$），最大环面 $T=\mathrm{diag}(e^{i\theta},e^{-i\theta})\cong S^1$，Weyl 群 $W\cong\mathbb{Z}_2$（$\theta\mapsto-\theta$）；用 Weyl 特征公式算 spin-$j$ 表示的特征 $\chi_j(\theta)=\frac{\sin((2j+1)\theta/2)}{\sin(\theta/2)}$，验证 $j=\frac12$ 给 $\chi_{1/2}(\theta)=2\cos(\theta/2)$。
- **与 Fulton-Harris / Serre 对照**：Warner Ch 6 是 Fulton-Harris Ch III（紧李群）+ Serre《有限群线性表示》GTM42 紧致情形的浓缩。Fulton-Harris 用最高权 + 根系图（Dynkin 图）构造表示，几何直觉强；Serre 用特征标理论，代数最干净；Warner 给 Peter-Weyl 的分析证明（Hilbert 空间正交分解）+ Weyl 特征公式标准推导，是「分析→代数」方法的典范。读法：Warner 先读建 Peter-Weyl 分析框架 $\to$ Fulton-Harris 攻根系构造 $\to$ Serre 补特征标代数。

---

### §延伸 · Further Topics（复流形 / Kähler / 对称空间，**非 GTM94 原书正文**）

> ⚠️ **忠于原书说明**：Warner GTM94 原书正文止于第 6 章（紧李群与表示论）。以下「复流形、Kähler 几何、对称空间」是紧李群表示论之后的**自然延伸方向**，不在原书内，列此作为读完本书后的下一步指引。参 Griffiths-Harris《代数几何原理》、Kobayashi-Nomizu 卷II、Helgason《对称空间》。

- **复流形与 Kähler 几何**：复流形是带复相容光滑结构（转移函数全纯）的流形；**Kähler 流形**是 Riemann 度量 + 复结构 + Hermite 形式相容（$\omega$ 闭）的流形，是代数几何（射影簇）、弦理论（Calabi-Yau）、Hodge 理论（$h^{p,q}$）的公共舞台。Warner Ch 1–4 的实流形框架可直接复本化到复情形。
- **对称空间**：Riemann 对称空间 $G/K$（$K$ 紧子群）是曲率 $\nabla R=0$ 的齐性 Riemann 流形，分类由紧李群的对合自同构给出。这是 Warner Ch 5 homogeneous 空间 + Ch 6 紧李群的深度融合，也是 Kobayashi-Nomizu 卷II 的核心专题。
- **飞腾锚点**：**FP16 3.81×[L01]** —— Kähler 度量 $g$ 与 Hermite 形式 $\omega$ 的数值表示需保持相容性（$\nabla g=0,\nabla J=0$），FP16 半精度的数值稳定性依赖这种相容性，吞吐是 FP32 的 3.81 倍。
- **进阶书目**：Griffiths-Harris（代数几何/Kähler）、Kobayashi-Nomizu 卷II（子流形/对称空间/示性类）、Helgason（对称空间/非交换调和分析）、Wells《复流形微分分析》。
- **为何这些方向紧接 Warner**：复流形把 Warner Ch 1 光滑结构「复化」（转移函数全纯），Kähler 几何把 Warner Ch 4 de Rham 上同调「精细化」为 Hodge 分解 $H^k=\bigoplus H^{p,q}$，对称空间把 Warner Ch 5 齐性空间 $G/H$ + Ch 6 紧李群分类「深度化」为曲率对称的 Riemann 几何。三者在 stage-3 分别对应代数几何（Hartshorne/Vakil）、规范理论（Donaldson）、Ricci 流（Hamilton-Perelman）方向——Warner 是它们共同的「实流形 + 李群」入口。

---

## §8 全书脉络一览（红线串联）

> §1 骨架表按「学什么」排列，本表按「为什么」排列，集中对照核心定理、飞腾锚点与「三柱」归属。

| 章 | 三柱归属 | 核心定理 | 飞腾/工程锚点 |
|:-:|---|---|---|
| 1 | 流形（空间柱） | 单位分解存在 / 光滑结构 / paracompact | TLB 4.81×[E04] atlas 坐标卡 |
| 2 | 子流形（空间柱） | 秩定理 + Frobenius 可积定理 | 分支预测[Lab02] 叶分类 |
| 3 | 微分形式（分析柱） | $d^2=0$ + Cartan 魔公式 | matmul 15×[V03] 楔积缩并 |
| 4 | 积分（拓扑柱）⭐ | Stokes + de Rham 定理 + Poincaré 对偶 | UDOT 16.9×[E05] 积分累加 + Iron Law<2% |
| 5 | 李群（对称柱） | Lie 三定理 + 闭子群定理 + homogeneous 空间 | GEMM 9.45G[Lab05] 群运算/伴随 |
| 6 | 紧李群表示（高潮）⭐⭐⭐ | Peter-Weyl + 最大环面 + Weyl 特征公式 | Schmidt 正交化 正交系 |
| 延伸 | 复/Kähler/对称（非原书） | Kähler 相容 / 对称空间 $G/K$ | FP16 3.81×[L01] Hermite 精度 |

**三条红线**：

1. **光滑结构红线**——Ch 1 定义流形 $\to$ Ch 2 子流形/叶状结构 $\to$ Ch 3 切丛截面（向量场/形式）$\to$ Ch 4 形式的积分，是「从空间到分析」的奠基。
2. **李群红线**——Ch 5 李群本身是光滑流形（Ch 1 语言直接用）+ 群结构 $\to$ Ch 6 紧李群表示论，是「连续对称性如何线性化」。
3. **分析↔代数↔拓扑桥梁红线**——Ch 4 Stokes/de Rham（微分形式 ↔ 拓扑）与 Ch 6 Peter-Weyl（紧群 ↔ 正交函数系）共享「用分析对象刻画代数/拓扑结构」的方法论，是 Warner 全书的方法论灵魂。

**读法建议**：第一遍精读 Ch 4（Stokes/de Rham，Part I 高潮）+ Ch 6（Peter-Weyl/Weyl 特征公式，Part II 高潮，全书皇冠定理）；Ch 1–3 与 Lee GTM218 重叠可速读，Ch 5 与 Hall《李群李代数》重叠可对照矩阵群友好版；延伸章作读毕指引，非原书正文。

---

## §9 全书思想主线

Warner 全书有一条贯穿的方法论主线：**以「光滑流形 + 微分形式 + 李群」三柱贯穿现代微分几何与表示论**。Part I（Ch 1–4）建「空间 + 分析」柱：光滑流形是舞台，微分形式是函数的推广，Stokes 定理把「边界的积分」与「内部的微分」统一，de Rham 定理把分析对象（形式）严格等同于拓扑对象（同调）。Part II（Ch 5–6）建「对称性 + 表示」柱：李群是「带光滑对称的流形」（Ch 1 语言直接适用），Lie 代数是其无穷小化，Peter-Weyl 把紧群上的函数论化为正交表示分解，Weyl 特征公式给出不可约表示的显式分类。

**与 Kobayashi-Nomizu「联络中心」互补**：KN 以主丛联络 $\omega$ 为中心，统一度量↔曲率↔拓扑（Riemann/Yang-Mills 共享框架）；Warner 不深入联络理论，而是把「流形基础 + 李群表示」一站式打通——KN 假设 Warner Ch 1–3 的全部语言，Warner 假设 KN 没有的紧李群表示论纵深。两书正交互补：**Warner 给「入口 + 桥梁」，KN 给「纵深 + 统一框架」**。与 Lee GTM218（只流形，最现代友好）呼应：Warner Part I 是 Lee 的 1983 经典版；与 Bott-Tu（de Rham 形式深化）呼应：Warner Ch 3–4 是 Bott-Tu 的精要前奏；与 Fulton-Harris/Hall（只表示论）呼应：Warner Ch 6 是它们的紧致情形浓缩。

**de Rham 理论的方法论核心**：Warner Ch 3–4 把外微分 $d$（$d^2=0$）、de Rham 复形、Stokes 定理、de Rham 定理、Poincaré 对偶串成一条完整的「分析→拓扑」链——闭形式模恰当形式（$H^k_{\mathrm{dR}}=\ker d/\mathrm{im}\,d$）这个纯分析定义的对象，竟严格同构于奇异上同调（纯拓扑）。这个「分析 = 拓扑」的奇迹是 Hodge 理论、Atiyah-Singer 指标定理、Chern-Weil 示性类的共同源头，Warner 用 Mayer-Vietoris + 单位分解给了它最干净的标准证明。这一链与 Ch 6 Peter-Weyl（「分析 = 代数」）遥相呼应，共同构成 Warner 全书的方法论双柱。

Warner 全书最深的方法论洞见在 Ch 4 与 Ch 6 的对照：**Stokes 定理与 Peter-Weyl 定理共享「用分析对象刻画代数/拓扑结构」的思想**——前者用积分（形式）刻画拓扑（同调），后者用积分（Haar 测度）刻画代数（表示分解）。这种「分析↔代数↔拓扑」三位一体，是 20 世纪几何与表示论的核心范式，也是 Warner 这本书的方法论灵魂。

---

## §10 与本仓库其他笔记的交叉引用

**与 Kobayashi-Nomizu《微分几何基础》卷I 对比**（stage-2，刚做）：
KN 以主丛联络 $\omega$ 为中心，统一度量↔曲率↔拓扑（Cartan 形式语言，最抽象）；
Warner 不深入联络，但给 KN 假设的全部前置：光滑流形（Ch 1）、切丛/张量场（Ch 1–3）、外微分（Ch 3）、李群与 Lie 代数（Ch 5）。
KN Ch I（微分流形）$\leftrightarrow$ Warner Ch 1–3；
KN Ch II（主丛联络）需要 Warner Ch 5（李群）作为前置（主丛 = 流形上的李群自由作用）。
建议：Warner 先读建流形 + 李群基础 $\to$ KN 卷I 攻主丛联络统一框架，二者正交互补。

**与 Lee《光滑流形引论》GTM218 对比**（stage-2 已读）：Lee 是 Warner Part I（Ch 1–4）的现代友好版，每概念先铺垫、习题丰富、符号最现代。建议 Lee 先读（建光滑流形严格基础）$\to$ Warner Part I 对照（同一内容的 1983 经典版）$\to$ Warner Part II 攻李群（Lee GTM218 Ch 21 仅简略涉及）。Lee GTM176《黎曼流形》则是 Warner 之后 Riemann 度量的友好纵深。

**与 Lee《拓扑流形引论》GTM202 对比**（stage-2 已读）：Lee GTM202 给拓扑流形、基本群、覆盖空间的严格基础——是 Warner Ch 1 拓扑层（Hausdorff、第二可数、局部欧氏）与 Ch 5 $SU(2)\to SO(3)$ 覆叠（覆叠空间理论）的前置。建议读 Warner Ch 1 前先过 Lee GTM202 Ch 1–4（拓扑流形 + 紧致性 + 基本群 + 覆叠），Warner 直接假设这些拓扑语言。GTM202（拓扑）+ GTM218（光滑）+ Warner（李群）三书构成「流形→李群」的完整阶梯。

**与 Bott-Tu《微分形式代数拓扑》GTM82 对比**（stage-2 已读）：
Warner Ch 3–4（外微分、de Rham、Stokes、Poincaré 对偶）是 Bott-Tu Ch 1（de Rham 理论）的精要前奏。
Bott-Tu 更深入（Čech-de Rham、谱序列、示性类），Warner 给最干净的标准版。
建议 Warner Ch 3–4 + Bott-Tu Ch 1 配套读。

**与 Fulton-Harris《表示论》对比**（stage-3 已读）+ **Hall《李群李代数》对比**（stage-2 已读）：
Warner Ch 5（李群）$\leftrightarrow$ Hall Ch 1–5（矩阵群友好入门）；
Warner Ch 6（紧李群表示）$\leftrightarrow$ Fulton-Harris Ch III（紧李群，Peter-Weyl/Weyl 特征公式）。
Warner Part II 是 Hall + Fulton-Harris 紧致情形的浓缩一站式版；读 Warner 后可跳读 Hall 的矩阵群入门，直接攻 Fulton-Harris。

**与 Spivak《流形上的微积分》对比**（stage-2 已读）：Spivak 是光滑流形 + 外微分 + Stokes 的单卷精华，给 Warner Ch 1–4 的几何直觉入口。Spivak 的 Stokes 定理证明（最干净版）$\leftrightarrow$ Warner Ch 4。

**与 Milnor《从可微观点看拓扑》对比**（stage-2 已读）：Milnor 用 Morse 理论（光滑函数临界点指标）研究流形拓扑，与 Warner Ch 3–4（光滑流形 + 形式）共享「用光滑结构提取拓扑」的哲学——Milnor 的「函数版」与 Warner 的「形式版」是同一思想的两条路径，对照阅读最能体会「光滑结构蕴含拓扑信息」的统一思想。

**AI 锚点（数学 ↔ 工程）**：

- 🟢 **等变神经网络（Equivariant NN）/ 李群深度学习**：Warner Ch 5–6 是等变神经网络的数学基础。等变 NN 要求 $f(g\cdot x)=g\cdot f(x)$（$g\in G$ 紧李群），其设计与 Peter-Weyl 分解（Warner Ch 6）直接相关——网络层在不可约表示 $V_\pi$ 上作用。球面 CNN（$SO(3)$ 等变）、分子性质预测（$E(3)$ 等变 GNN）都依赖 Warner 的紧李群表示论。Weyl 特征公式给出计算任意紧群表示特征的通用算法。
- 🟢 **李群在图神经网络（GNN）中的应用**：GNN 的消息传递在节点对称群下不变；当对称性是连续李群（如分子的 $SE(3)$），需 Lie 代数（Warner Ch 5）描述无穷小对称，指数映射 $\exp$（Ch 5）给出从 Lie 代数到群的提升（连续旋转的离散化）。
- 🟢 **对称性与物理（规范理论/粒子物理）**：Warner Ch 5 的李群 + homogeneous 空间是规范理论的语言——$U(1)$（电磁）、$SU(2)$（弱）、$SU(3)$（强 QCD）都是 Lie 群，夸克模型八重道（Gell-Mann）是 $SU(3)$ 表示论（Warner Ch 6）的应用。Lie 代数的根系/最高权分类（Ch 6 前置）直接对应粒子分类。
- 🟡 **Kähler 几何与弦理论**：延伸章的 Kähler 流形是弦理论紧致化（Calabi-Yau 流形）的舞台；Calabi-Yau 的 Hodge 数 $h^{p,q}$（来自 Warner Ch 4 de Rham 上同调的复本化）决定物理模型的世代数。这是「纯数学流形理论 $\to$ 理论物理」的最深刻落地之一。
- 🟡 **de Rham 上同调与拓扑数据分析（TDA）**：Warner Ch 3–4 的 de Rham 复形（$d^2=0$，闭模恰当）是持续同调（persistent homology）的连续原型；TDA 用离散复形（Warner de Rham 的组合版本）分析高维数据的「洞」结构，应用于点云形状识别。
- 🟡 **Haar 测度与生成模型**：Warner Ch 6 的 Haar 测度是「在流形/群上做概率」的基础；流形上的生成模型（如球面 GAN、SO(3) 上的姿态分布）需 Haar 测度定义均匀先验，Peter-Weyl 给出球面上的「Fourier 特征」（球面调和）用于等变生成。
- 🟡 **球面调和与信号处理**：球面调和 $Y_l^m$ 是 $SO(3)$ 不可约表示（Warner Ch 6 Peter-Weyl 的 $S^2\cong SO(3)/SO(2)$ 情形）的矩阵系数，是宇宙微波背景辐射（CMB）角功率谱、球面 CNN、3D 分子形状描述符的数学基础——「紧齐性空间上的调和分析」直接落地天文/化学/深度学习。

---

## §11 自测答案要点（供核对）

1. **Ch 1** $S^2$ 球极投影：北极 $N$ 去掉的卡 $U_N$，$(x,y)=(\frac{X}{1-Z},\frac{Y}{1-Z})$；转移函数是 Möbius 变换 $(x,y)\mapsto(\frac{x}{x^2+y^2},\frac{y}{x^2+y^2})$（倒数）。单位分解 $\{\rho_N,\rho_S\}$（从属于 $\{U_N,U_S\}$）$\Rightarrow g=\rho_N g_{\mathbb{R}^2}+\rho_S g_{\mathbb{R}^2}$ 整体光滑正定。✓
2. **Ch 2** $D=\mathrm{span}\{\partial_x,\partial_y+x\partial_z\}$：算 $[\partial_x,\partial_y+x\partial_z]=\partial_z$。但 $\partial_z\notin D$ $\Rightarrow$ $[D,D]\not\subseteq D$ $\Rightarrow$ **不可积**（Frobenius 失败）。（若取 $D=\mathrm{span}\{\partial_x,\partial_y\}$，则 $[\cdot,\cdot]\subset D$，可积，叶 $=$ 水平面 $z=c$。）✓
3. **Ch 3** $\omega=x\,dy$：$d\omega=dx\wedge dy$，$d(d\omega)=d(dx\wedge dy)=d^2x\wedge dy-dx\wedge d(dy)=0$ ✓（$d^2=0$）。
   Cartan：$\mathcal{L}_{\partial_x}(x\,dy)=i_{\partial_x}d(x\,dy)+d(i_{\partial_x}x\,dy)=i_{\partial_x}(dx\wedge dy)+d(0)=dy+0=dy$ ✓（直接算 $\mathcal{L}_{\partial_x}(x\,dy)=(\partial_x x)dy=dy$）。
4. **Ch 4** $M=[0,1]$，$\omega=f(x)$ 是 0 形式，$d\omega=f'(x)dx$，$\int_{[0,1]}f'(x)dx=\int_{\{1\}}f-\int_{\{0\}}f=f(1)-f(0)=\int_{\partial[0,1]}f$ ✓（Stokes = 微积分基本定理）。
   $S^1$：$H^1_{\mathrm{dR}}(S^1)=\mathbb{R}$（生成元 $d\theta$，闭但非恰当，因 $\int_{S^1}d\theta=2\pi\neq0$ 而恰当形式积分为 0）。✓
5. **Ch 5** $\mathfrak{so}(3)$：基 $L_x=\begin{pmatrix}0&0&0\\0&0&-1\\0&1&0\end{pmatrix}$，$L_y,L_z$ 轮换；$[L_x,L_y]=L_z$ ✓。
   $SU(2)\to SO(3)$：$\mathfrak{su}(2)\cong\mathfrak{so}(3)$（同构），但 $SU(2)$ 单连通而 $SO(3)\cong\mathbb{R}P^3$（基本群 $\mathbb{Z}_2$），覆盖 $2:1$ ✓（Lie 第二定理：Lie 代数同构 $\not\Rightarrow$ 群同构，需单连通）。
6. **Ch 6** $SU(2)$ spin-$j$：最高权 $\lambda=2j$（根系 $A_1$，$\alpha=1$，$\rho=\frac12$），Weyl 公式分子 $\sin((2j+1)\theta/2)$，分母 $\sin(\theta/2)$，故 $\chi_j(\theta)=\frac{\sin((2j+1)\theta/2)}{\sin(\theta/2)}$ ✓。
   $j=\frac12$：$\chi_{1/2}(\theta)=\frac{\sin\theta}{\sin(\theta/2)}=2\cos(\theta/2)$ ✓（二维表示，特征在 $\theta=0$ 取 $2=\dim$）。

> **核对原则**：Ch 1–4 属「流形 + 分析奠基」，自测题与 Lee/Bott-Tu 重叠处可直接交叉验证；Ch 5–6 属「李群 + 表示」，自测题与 Hall/Fulton-Harris 重叠处可对照。Warner 全书最深洞见在 Ch 4（Stokes/de Rham）↔ Ch 6（Peter-Weyl）的方法论对照——「用分析对象刻画代数/拓扑结构」。

> **方法论收束**：Warner 的自测题刻意设计成「能在 Python/NumPy 里数值验证」的形式——这是「应用数学研究型工程师」的读法：每个抽象定理找一个数值锚点。Ch 1 的球极投影转移函数可直接 `matplotlib` 绘制；Ch 3 的 $d^2=0$ 用 `sympy.diff` 自动验证；Ch 4 的 Stokes 用 `scipy.integrate` 数值积分核对；Ch 6 的 Weyl 特征公式用 `numpy` 算 spin-$j$ 表示矩阵再取迹。这种「定理 ↔ 代码」的双向验证，是把 Warner 的抽象框架内化为工程直觉的最快路径——也是本项目「AI 锚点法」的核心实践：飞腾 D3000M 的 TLB/UDOT/matmul/Schmidt 锚点，把流形坐标卡、积分累加、群运算矩阵乘、Peter-Weyl 正交分解逐一锚定到硬件实测性能。

---

> **下一步**：沿 `01-track/stage-2` 精读 Warner Ch 4（Stokes/de Rham，Part I 高潮，需 Lee Ch 1–16 前置）+ Ch 6（Peter-Weyl/Weyl 特征公式，Part II 高潮，需 Fulton-Harris Ch III 配合）；Ch 5（李群）与 Hall《李群李代数》对照矩阵群友好版。
>
> **stage-3 前瞻**：延伸章方向 → 复流形/Kähler 几何（Griffiths-Harris / Huybrechts）→ 对称空间（Helgason / Kobayashi-Nomizu 卷II）→ Ricci 流 → 规范理论（Yang-Mills/Donaldson）；Warner 的「流形 + 李群」基础是以上所有方向的公共语言。等变神经网络（Equivariant NN）是「紧李群表示论 → 深度学习」的直接工程出口。
>
> **实操验证**（建议用 Python/SciPy）：
> - `scipy.integrate.solve_ivp` 验证向量场流（Ch 3）→ 在 $S^2$ 上算旋转场的积分曲线
> - 用单位分解数值构造 Riemann 度量（Ch 1）→ 验证 $g$ 正定光滑
> - 数值验证 Stokes（Ch 4）：对 $S^2$ 上的 1 形式 $\omega$，算 $\int_{S^2}d\omega=0$（无边）vs $\int_{\partial M}\omega$
> - 实现 $SU(2)$ 的 spin-$j$ 表示矩阵（Ch 6）→ 用 Weyl 公式验证特征 $\chi_j(\theta)$
> - 实现 Peter-Weyl 分解（Ch 6）：对 $SO(3)$ 上的函数做球面调和展开，验证正交性（Schur 关系）
> - 数值验证 Lie 第二定理（Ch 5）：对 $\mathfrak{su}(2)\cong\mathfrak{so}(3)$，`scipy.linalg.expm` 算指数映射，验证 $SU(2)\to SO(3)$ 是 2:1 覆叠
> - 用 `sympy` 符号验证 Cartan 魔公式（Ch 3）：$\mathcal{L}_X\omega\equiv(i_Xd+di_X)\omega$ 恒等

---

> **版本说明**：本文为 `math-expert-pro` 项目 stage-2 研究生基础「快速逐章」系列，归 §3B 几何/拓扑方向深化。Warner GTM94 是「微分流形 + 李群 + 紧李群表示」一站式桥梁，与 Kobayashi-Nomizu 卷I（联络中心化）正交互补——**Warner 给「入口 + 桥梁」，KN 给「纵深 + 统一框架」**。AI 工程主锚点：等变神经网络（Equivariant NN）/ 紧李群在 GNN 中的应用 / 球面调和信号处理。写作日期 2026-07-03。