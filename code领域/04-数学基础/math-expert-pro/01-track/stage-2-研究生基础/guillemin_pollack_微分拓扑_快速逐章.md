# Guillemin & Pollack《Differential Topology》· 快速逐章精读

> 基于原书：Differential Topology (Victor Guillemin & Alan Pollack, Prentice-Hall, 1974) / 读于：2026-07-02
> 定位：**Berkeley 经典微分拓扑入门**，Milnor《从可微观点看拓扑》的「友好扩写版」。在 Milnor 度论地基上新增**横截性**与**相交理论**两大支柱，图多、直觉先行、习题丰富，自学者首选。
> 本文为**快速逐章精读**，每章 1 个飞腾锚点 + 1 个关键定理 + 1 道自测题。
> 前置：已读 Milnor 从可微观点看拓扑（度论灵魂）/ Petersen 黎曼几何 GTM171 / do Carmo 黎曼几何（切空间/向量场/高维流形）/ Spivak 流形微积分（$df$/Jacobian）/ Bott-Tu 微分形式 GTM82（de Rham）/ Fulton+Hatcher 代数拓扑（同伦群/Euler 示性数）。

---

## §0 引言：G&P 是什么，为什么读它

Guillemin & Pollack 的《Differential Topology》(1974) 是 stage-2 微分拓扑主线的**核心教材**。两位作者均为 MIT 几何拓扑学家（Pollack 是 Milnor 的学生），本书源自他们在 MIT 的讲稿，被 Berkeley、MIT 等顶尖院校用作微分拓扑标准教材近半个世纪。

**历史定位**：本书诞生于微分拓扑的「黄金时代」（1950s-1970s）——Milnor(1965) 奠基、Thom 配边理论(1954)、Smale 高维 Poincaré 猜想(1961)、Milnor 怪球面(1956) 之后。G&P(1974) 的目标是把这一前沿领域的**入门门槛**降到本科生可达——用 Milnor 的度论为地基，补入横截性/相交理论，使之成为「读完 Spivak 流形微积分即可上手」的友好教材。它填补了 Milnor(太 terse) 与 Hirsch(太抽象) 之间的空白，成为半个世纪以来**最流行的微分拓扑入门书**。

**全书核心策略**：以 Milnor 的「光滑映射 + 正则值 + Sard 定理」为地基，但将其推广为更强的工具——**横截性 (transversality)**。Milnor 的正则值 $y$（$df$ 满射到 $T_yN$）是横截性的特例（横截到一个点）；G&P 将其推广为「$f\pitchfork Z$」——映射 $f:M\to N$ 横截到子流形 $Z\subset N$，即 $df(T_xM)+T_zZ=T_zN$ 对一切 $x\in f^{-1}(Z)$ 成立。当 $\dim M+\dim Z=\dim N$ 时，横截原像是**有限点集**，对其计数（mod 2 或带符号）就得到**相交数**——比 Milnor 度论更一般的框架（度 $=$ 相交于一点的特例）。横截性的深远意义在于：Thom 横截定理保证「横截是一般位置」(generic)——任意映射经微扰即横截，于是相交数**总能定义**。

**G&P 与 Milnor 的关键差异**：Milnor 的「正则值」是 $df$ 满射到一个点；G&P 的「横截性」$f\pitchfork Z$ 要求 $df(T_xM)$ 与子流形 $Z$ 的切空间**张满** $T_zN$。当 $Z$ 退化为一点时，横截性 $=$ 正则值——故 G&P 的框架严格包含 Milnor。但横截性的威力在于它处理**任意维数**的子流形：两条曲线在曲面上相交、两个曲面在 $\mathbb{R}^3$ 中相交、一个曲面与一条曲线相交——这些都不是「度」（同维映射）能直接处理的，横截性 + 相交理论才是正确的语言。

**G&P 与 Milnor 的关系**：Milnor(60 页) 用「正则值 $\to$ 度」单线推进；G&P(220 页) 在同一地基上加入三块新内容：

- **横截性 Ch2**——Milnor 几乎不提，G&P 用整章发展，是相交理论的引擎；
- **相交理论 Ch3-4**——Milnor 无，G&P 用横截原像的计数定义相交数 $I(f,Z)$，度 $\deg(f)=I(f,\{y\})$ 是其特例；
- **带边流形**——G&P 在 Ch1 仔细发展（$\partial M$），为相交数的良定义铺路（同伦过程中原像是 1 维带边流形，边界点**成对消亡**，保证 mod 2 守恒）；
- **Lefschetz 不动点**——G&P 独有，Lefschetz 数 $L(f)=$ 图与对角线的相交数，推广 Brouwer 不动点。

**叙事弧线**分五步推进：

1. **Ch1** 建立「子流形 $\subset\mathbb{R}^N$ + 光滑映射 + 切空间 + Sard 定理 + 带边流形」的工具箱；
2. **Ch2** 引入**横截性**——全书的核心概念，连接 Ch1 正则值与 Ch3-4 相交理论；
3. **Ch3-4** 定义**相交数**（先 mod 2 无需定向，再定向带符号），度是其特例；
4. **Ch5** 应用：环绕数、Brouwer 不动点、Borsuk-Ulam、代数基本定理、Hopf 分类；
5. **Ch6** 向量场指标与 Euler 示性数（Poincaré-Hopf），$\chi(M)=$ 对角线自相交数，Morse 理论引论。

**与已读教材的关系**：

- Milnor 从可微观点 $=$ G&P 的**灵魂浓缩**；已读 Milnor 后读 G&P $=$ 补全横截性 $+$ 相交理论 $+$ Lefschetz 不动点；
- Petersen/do Carmo 黎曼几何 $=$ 提供**切空间、向量场、度量**的几何语言（G&P 不依赖度量，纯光滑结构即可）；
- Bott-Tu $=$ de Rham 上同调（积分侧），G&P $=$ 相交理论（计数侧），两者是微分拓扑的**两大互补支柱**；
- Fulton/Hatcher $=$ 同调群/同伦群（代数机器），G&P 用微分方法重新抵达同一结论。

**G&P 习题的教学价值**：G&P 被广泛赞誉为「习题最好的微分拓扑教材」。每章习题分三个层次：**（一）手算验证**（如验证 $S^n$ 是子流形、计算具体映射的度）；**（二）理论推导**（如证明横截的稳定性、mod 2 相交数的良定义）；**（三）挑战题**（如计算环面高度函数的 Morse 指标、验证 Lefschetz 定理的具体实例）。这种「从手到脑」的梯度设计，使读者在每个抽象概念后立即有**可操作的练习**巩固——这是 G&P 比 Milnor（习题少）、Hirsch（习题偏理论）更适合**自学**的根本原因。建议：每章至少完成第一层全部 $+$ 第二层半数习题。

**与三本相关教材的对比**（决定你该读哪本）：

| 维度 | **G&P** 微分拓扑 (1974) | **Milnor** 从可微观点 (1965) | **Hirsch** 微分拓扑 GTM33 (1976) | **Lee** 光滑流形 (2012) |
|---|---|---|---|---|
| 流形定义 | 子流形 $\subset\mathbb{R}^N$（具体） | 子流形 $\subset\mathbb{R}^N$（具体） | 抽象 atlas $+$ 子流形 | 抽象 atlas（现代标准） |
| 篇幅/风格 | ~220 页，友好图多习题丰富 | ~60 页，极致凝练像诗 | ~240 页，系统公理化 | ~700 页，百科全书 |
| **横截性** | ★核心章（Ch2 全章发展） | 几乎不提（隐于正则值） | 有，但更抽象形式化 | 有，积分论侧附带 |
| **相交理论** | ★核心（Ch3-4 双章） | 无（仅度 $=$ 相交于点） | 无 | 无 |
| 定向度/度 | 有（Ch4-5） | ★核心（§3-4） | 有（一章） | 有（积分章） |
| 向量场/Euler | Ch6 Poincaré-Hopf | §6 Poincaré-Hopf | 有 | 有 |
| Morse 理论 | 附录引论 | §7 引论 | 无 | 无 |
| Lefschetz 不动点 | ★独有 | 无 | 无 | 无 |
| 带边流形 | Ch1 仔细发展 | 简略提及 | 有 | 有 |
| 习题 | 丰富手算、直觉导向 | 少而精 | 多、偏理论 | 极多、系统 |
| 适合谁 | 自学者首选、需横截/相交/Lefschetz | terse 大师精读、追度论灵魂 | 研究方向案头查阅 | 系统学全套光滑流形基础 |

**建议路线**：Milnor 从可微观点（度论灵魂，60 页一口气） $\to$ **G&P 本书**（补全横截/相交/Lefschetz，220 页深读） $\to$ Hirsch GTM33（系统全面，研究方向）或 Lee 光滑流形（现代抽象基础，补积分论）。

**为什么 G&P 用子流形 $\subset\mathbb{R}^N$ 而非抽象 atlas**：这是一个深思熟虑的**教学选择**。抽象流形（Lee/Hirsch 的 atlas 定义）更现代、更内蕴（不依赖嵌入），但对初学者引入了拓扑学开销（ Hausdorff/第二可数公理、光滑相容图册等）。G&P 的子流形定义直接建立在读者已有的 $\mathbb{R}^N$ 微积分（Spivak 流形微积分）之上——流形是 $\mathbb{R}^N$ 中「光滑弯曲的曲面」，切空间是 $\mathbb{R}^N$ 的线性子空间，一切都在熟悉的欧氏空间中进行。Whitney 嵌入定理（任何抽象流形可嵌入 $\mathbb{R}^{2n+1}$）保证这个定义「够用」——不损失一般性。代价：有些结论（如切丛的内蕴定义、李群的结构）用抽象语言更自然，故读完 G&P 后建议补 Lee 光滑流形（抽象 atlas）。

**为什么是「经典」**：G&P 被奉为经典，理由有三：**（一）横截性作为统一框架**——把正则值、子流形相交、嵌入、不动点统一到「横截 $\to$ 原像是子流形 $\to$ 计数得不变量」的范式；**（二）习题的卓越设计**——每章习题从手算到理论，把抽象概念落到实处；**（三）Euler 示性数 $=$ 对角线自相交**这一洞见——把 $\chi(M)$ 从同调的定义中解放出来，纯用相交理论得到，是 G&P 最优雅的结论之一。

> 🟢 事实可作锚点：Preimage 定理、Sard 定理、Transversality 定理、相交数的良定义与同伦不变性、Poincaré-Hopf 定理、Morse 引理均为严格定理。
> 🟡 类比（横截 $=$「一般位置相交」、相交数 $=$「两个子流形穿过的次数」、Euler 示性数 $=$「对角线和自己的交点数」）仅供直觉，**绝不在严格证明中引用**。

**工程师阅读建议**：

- **Ch1 是「甜区」**——子流形定义与 Spivak 流形微积分重叠，可快速过；**带边流形**（$\partial M$）是新内容，务必理解（相交理论的地基）。
- **Ch2 横截性是全书关键**——Milnor 没有这章，G&P 的灵魂在此。理解「$f\pitchfork Z \Leftrightarrow df(T_xM)+T_zZ=T_zN$」。
- **Ch3-4 相交理论**——mod 2 先（无需定向），定向后（带符号）。核心隐藏引理：「紧致 1 维带边流形的边界点数是偶数」。
- **Ch5 应用**——已读 Milnor 的会感到熟悉（度/Brouwer/Hopf），但相交理论框架是全新视角。
- **Ch6**——$\chi(M)=$ 对角线自相交是 G&P 独门绝技，务必理解；Morse 理论引论读后转 Milnor《Morse Theory》(1963)。

**关于隐藏引理与边界定理**：G&P 最大的教学贡献之一是完整证明了 Milnor 藏在脚注的**1 维流形分类定理**——「紧致 1 维光滑流形（可能带边）微分同胚于若干圆 $S^1$ 与闭区间 $[0,1]$ 的不交并」。推论：紧致 1 维流形的边界点数是偶数。这个看似平凡的引理是 **mod 2 相交数同伦不变性的核心**：同伦 $F:M\times[0,1]\to N$ 横截到 $Z$ 时，$F^{-1}(Z)$ 是 1 维带边流形，其边界 $=$（$t=0$ 的原像）$\sqcup$（$t=1$ 的原像），边界点成对 $\Rightarrow$ 两侧 mod 2 计数相等。G&P 用整节详细推导，而 Milnor 一句话带过——这正是 G&P「友好」的体现。

**带边流形为什么重要**：相交理论的良定义依赖「同伦不变性」，而同伦不变性的证明依赖「1 维带边流形的边界定理」。没有带边流形的概念，就无法表述「$F^{-1}(Z)$ 是 1 维带边流形，边界成对」这一论证。G&P 在 Ch1 仔细发展 $\partial M$（半空间局部模型、边界是低 1 维流形、collar neighborhood），正是为 Ch3 铺路。这是 G&P 相比 Milnor 的另一处「扩写」。

---

## §1 全书 6 章骨架一览

| 章 | 标题 | 核心概念 | 飞腾锚点 |
|---|---|---|---|
| 1 | 流形与光滑映射 | 子流形 $\subset\mathbb{R}^N$/切空间/$df$/带边流形/Sard | **TLB 局部坐标卡** ⭐ |
| 2 | 横截性 Transversality | $f\pitchfork Z$/横截稳定性/Thom 横截定理 | **分支预测 临界点** |
| 3 | 相交理论模 2 | $I_2(f,Z)$/1 维流形分类/自相交 | **Iron Law 逼近** ⭐ |
| 4 | 定向相交理论 | 定向/带符号相交数/度 $\deg(f)=I(f,\{y\})$ | **Schmidt 正交标架** |
| 5 | 环绕数与度 | $W(f,z)$/Brouwer/Borsuk-Ulam/Hopf/代数基本定理 | **UDOT 度计数** |
| 6 | 向量场指标 $+$ Morse 引论 | Poincaré-Hopf/$\chi=$ 对角自相交/Morse 引理 | **matmul Jacobian** ⭐ |

**单线主线**：子流形 $\subset\mathbb{R}^N$ $\to$（Sard）正则值 $\to$（推广）横截性 $f\pitchfork Z$ $\to$（计数）相交数 $I(f,Z)$ $\to$（特例）度 $\deg$ $\to$（应用）Brouwer/Borsuk-Ulam/Hopf $\to$（几何）$\chi(M)=$ 向量场指标和 $=$ 对角线自相交。横截性是贯穿全书的**核心概念**，相交数是核心不变量。

---

### §1 流形与光滑映射（Manifolds & Smooth Maps）⭐

> 子流形 $\subset\mathbb{R}^N$ 的定义 / 切空间 $T_xM$ / 光滑映射的微分 $df$ / 带边流形 / Preimage 定理 / Sard 定理

- **核心**（约 80 字）：G&P 用**具体定义**：$M\subset\mathbb{R}^N$ 是 $k$ 维光滑子流形 $\iff$ 每点 $x\in M$ 有邻域 $U$ 与光滑 $g:U\to\mathbb{R}^{N-k}$，使 $M\cap U=g^{-1}(0)$ 且 $0$ 为正则值（$\mathrm{rank}(Dg)=N-k$）。切空间 $T_xM=\ker Dg(x)$。光滑映射 $f:M\to N$ 的**微分** $df_x:T_xM\to T_{f(x)}N$。**带边流形** $M$：局部同胚于半空间 $\mathbb{H}^k$，边界 $\partial M$ 是 $k-1$ 维流形（相交理论的地基）。**Preimage 定理**：正则值 $y$ 的原像 $f^{-1}(y)$ 是子流形。**Sard 定理**：临界值零测。
- **飞腾锚点**：**TLB 局部坐标卡** ⭐ —— 流形的本质是「局部像 $\mathbb{R}^k$」：每点有局部坐标卡（chart），换卡光滑过渡，恰似 CPU 的 **TLB** 把每段虚拟地址翻译成物理地址。带边流形则多了「半空间」坐标卡（一半是边界），如同内存映射的边界页。
  - 🟢 事实：$df_x$ 的秩 $\le\min(\dim M,\dim N)$；逆函数定理保证 $\det df\neq0$ 处局部微分同胚。带边流形的边界 $\partial M$ 自身是无边流形。
  - 🟡 类比：子流形的隐式定义 $g^{-1}(0)=$「约束方程的解集」，$\mathrm{rank}(Dg)=N-k=$ 约束独立（无冗余约束）。
- **几何/应用**：$S^k=g^{-1}(0)$，$g=\sum x_i^2-1$，$\nabla g=2x\neq0$ 在球面上，故 $S^k$ 是 $k$ 维子流形。Preimage 定理是「隐函数定理的几何版」——正则值约束独立，原像是干净子流形。带边流形 $D^k$（闭球）的边界 $\partial D^k=S^{k-1}$，这是 Ch3-4 相交理论中「1 维带边流形的边界点成对消亡」引理的来源。
- **关键定理**：**Preimage 定理**——$f:M^m\to N^n$ 光滑，$y\in N$ 正则值 $\Longrightarrow$ $f^{-1}(y)$ 为 $m-n$ 维光滑子流形（或空）。**Sard 定理**——$C^r$ 映射（$r>\max(m-n,0)$）的临界值集 Lebesgue 测度为零。
- **自测**：$f:\mathbb{R}^3\to\mathbb{R}$，$f(x,y,z)=x^2+y^2+z^2$，验证 $c>0$ 是正则值（$df=(2x,2y,2z)\neq0$ 在 $f^{-1}(c)=S^2_{\sqrt{c}}$ 上），故 $f^{-1}(c)$ 是 $3-1=2$ 维子流形（球面）；$c=0$ 是临界值（$df=0$ 在原点）。附加：闭球 $D^3=\{x^2+y^2+z^2\le1\}$ 是带边流形，$\partial D^3=S^2$，验证 $D^3$ 局部同胚于半空间 $\mathbb{H}^3$（边界点同胚于 $\{z=0\}\subset\mathbb{H}^3$，内部点同胚于 $\mathbb{R}^3$）。

---

### §2 横截性 Transversality（Transversality）⭐⭐⭐

> 横截定义 $f\pitchfork Z$ / 横截原像定理 / 横截稳定性 / Thom 横截定理（横截是「一般的」）

- **核心**（约 80 字）：$f:M\to N$ **横截到**子流形 $Z\subset N$（记 $f\pitchfork Z$） $\iff$ 对一切 $x\in f^{-1}(Z)$：$df_x(T_xM)+T_{f(x)}Z=T_{f(x)}N$（像空间与 $Z$ 的切空间**张满**整个 $T_{f(x)}N$）。正则值 $=$ 横截到一个点（$Z=\{y\}$）的特例。三大结论：**（i）横截原像定理**：$f\pitchfork Z\Longrightarrow f^{-1}(Z)$ 是 $M$ 中余维 $=$ codim$(Z)$ 的子流形；**（ii）稳定性**：横截在小扰动下保持（$\pitchfork$ 是开稠条件）；**（iii）Thom 横截定理**：任何光滑映射经任意小扰动可变横截——故「横截是一般位置」。
- **飞腾锚点**：**分支预测 临界点** —— 横截 $=$ 子流形处于「一般位置」（generic position），恰似 CPU **分支预测**在临界点走「大概率路径」。退化相交（非横截）是「不稳定的特殊情况」，微扰即变横截（分支翻转到一般路径）。Thom 定理保证：随机扰动一下，几乎必然横截。
  - 🟢 事实：$\dim M+\dim Z=\dim N$ 且 $f\pitchfork Z$ 时，$f^{-1}(Z)$ 是 $0$ 维 $=$ 有限点集 $\to$ 可计数 $\to$ 相交数（Ch3-4）。横截是开稠条件（$C^\infty$ 拓扑下）。
  - 🟡 类比：两条曲线在 $\mathbb{R}^2$ 中「横截相交」$=$ 在交点处不相切（切线张满平面），「相切」是非横截的退化情形（微扰即不相切）。
- **几何/应用**：横截性是 G&P **独有于 Milnor** 的核心概念。Milnor 只用「正则值」（横截到点），G&P 推广到「横截到子流形」，由此得到相交理论。横截原像定理是 Preimage 定理的推广——Preimage 定理说「正则值原像是子流形」，横截原像定理说「横截子流形的原像是子流形」。应用极广：嵌入定理（Whitney）、配边（Thom）、不动点（Lefschetz）都以横截性为基石。工程上，机器人路径规划中「路径避开障碍」可表述为横截条件；优化中约束曲面与目标等高面的横截相交保证正则性（Lagrange 乘子的非退化条件本质是横截性）。
- **关键定理**：**横截原像定理**——$f\pitchfork Z$ $\Longrightarrow$ $f^{-1}(Z)$ 是 $M$ 中光滑子流形，$\dim f^{-1}(Z)=\dim M-\dim N+\dim Z$。**Thom 横截定理**——$\forall f:M\to N$，$\exists$ 任意接近 $f$ 的 $g\pitchfork Z$（横截是 generic 的）。
- **自测**：$f:\mathbb{R}^2\to\mathbb{R}$，$f(x,y)=x^2-y^2$，$Z=\{0\}$。$df=(2x,-2y)$，$f^{-1}(0)=\{y=\pm x\}$（两条交叉直线），在交点 $(0,0)$ 处 $df=0$ 非横截！但 $Z=\{1\}$ 时 $f^{-1}(1)=\{x^2-y^2=1\}$（双曲线），$df\neq0$ 横截。附加：$g:\mathbb{R}^2\to\mathbb{R}^2$，$g(x,y)=(x,y)$（恒等），$Z=\{y=0\}$（$x$ 轴），$g^{-1}(Z)=Z$（$1$ 维子流形），验证横截：$dg=I$（恒等），$dg(T_x\mathbb{R}^2)+T_zZ=\mathbb{R}^2+0=\mathbb{R}^2=T_z\mathbb{R}^2$ ✓。

---

### §3 相交理论模 2（Intersection Theory Mod 2）⭐⭐

> $I_2(f,Z)=\#f^{-1}(Z)\bmod 2$ / 良定义（1 维流形分类）/ 同伦不变 / 自相交 / 边界定理

- **核心**（约 80 字）：设 $\dim M+\dim Z=\dim N$，$f:M\to N$ 横截到 $Z$（$f\pitchfork Z$），则 $f^{-1}(Z)$ 有限。定义**模 2 相交数** $I_2(f,Z)=\#f^{-1}(Z)\pmod{2}\in\mathbb{Z}_2$。两个深刻事实：**（i）良定义**——与横截扰动无关（关键引理：紧致 1 维带边流形的边界点数是偶数，故同伦过程中原像点的创生/消亡成对）；**（ii）同伦不变性**——$f_t$ 横截同伦 $\Rightarrow$ $I_2(f_0,Z)=I_2(f_1,Z)$。**自相交** $I_2(M)=$ 嵌入 $M\hookrightarrow M\times M$（对角线 $\Delta$）与 $\Delta$ 的 mod 2 相交数。**边界定理**：$f:\partial W\to N$（$\partial W$ 为紧 $W$ 的边界）$\Rightarrow$ $I_2(f,Z)=0$。
- **飞腾锚点**：**Iron Law 逼近** ⭐ —— mod 2 相交数是**最粗糙的逼近**（只保留奇偶性，丢弃一切细节），恰如 **Iron Law** 用 $<2\%$ 的极简先验界抓住本质。这种「粗粒化」换来的是巨大的**鲁棒性**：同伦不变、对不可定向流形也成立。精细信息（定向、正负号）在 Ch4 补回。
  - 🟢 事实：mod 2 相交数无需定向，对不可定向流形（$\mathbb{RP}^2$、Möbius 带）同样有效。$\deg_2(f)=I_2(f,\{y\})$ 是 Milnor 的 mod 2 度的推广。
  - 🟡 类比：$I_2=1=$「穿过奇数次」（本质上不可消除），$I_2=0=$「穿过偶数次或不相交」（可消除）。两条曲线在曲面上相交奇数次 $=$ 拓扑非平凡。
- **几何/应用**：mod 2 相交理论是 G&P **独有于 Milnor** 的内容。Milnor 只处理同维映射的度（$=$ 相交于一点的特例），G&P 处理任意维数的子流形相交。1 维流形分类引理（「紧致 1 维流形 $=$ 若干 $S^1$ 与弧的不交并」）是 Milnor 藏在脚注里的隐藏引理，G&P 用整节详细证明——这是相交数良定义的基石。

**边界定理的直观理解**：mod 2 相交数的同伦不变性可以这样「看」——同伦 $F:M\times[0,1]\to N$ 横截到 $Z$（$\dim M+\dim Z=\dim N$）时，$F^{-1}(Z)$ 是 $M\times[0,1]$ 中的 1 维子流形（维数 $=(\dim M+1)+\dim Z-\dim N=1$）。它的边界落在 $M\times\{0\}$ 与 $M\times\{1\}$ 上——即 $f_0^{-1}(Z)$ 与 $f_1^{-1}(Z)$。1 维流形的边界点成对（每个弧段两端各一点），故 $f_0^{-1}(Z)$ 与 $f_1^{-1}(Z)$ 的点数 mod 2 相等。这就是「同伦不变性」的几何图景：弧段把两端的点配对消亡，保 mod 2 守恒。
- **关键定理**：$I_2(f,Z)$ 良定义（不依赖横截扰动的选取），同伦不变。**边界定理**——$W$ 紧致带边，$f:\partial W\to N$，$\dim\partial W+\dim Z=\dim N$，$f\pitchfork Z$ $\Rightarrow$ $I_2(f,Z)=0$。
- **自测**：$\mathbb{R}^2$ 中两条直线 $L_1:y=0$、$L_2:x=0$，横截相交于原点，$\#=1$，$I_2(L_1,L_2)=1$。若 $L_2$ 平移为 $y=1$（不相交），$\#=0$，$I_2=0$。验证同伦 $L_{2,t}:y=t$（$t:0\to1$）在 $t=0$ 时 $I_2=1$，$t>0$ 时 $I_2=0$——但 $t=0$ 处 $L_2$ 与 $L_1$ 非横截（重合），需扰动后才适用。

---

### §4 定向相交理论（Oriented Intersection Theory）⭐⭐

> 定向 / 带符号相交数 $I(f,Z)\in\mathbb{Z}$ / 度 $\deg(f)=I(f,\{y\})$ / 环绕数引论

- **核心**（约 80 字）：给 $M,N,Z$ 配**定向**（切空间标架的相容等价类，沿路径连续不翻转）。$f:M\to N$ 横截到定向子流形 $Z$，定义**定向相交数** $I(f,Z)=\sum_{x\in f^{-1}(Z)}\mathrm{sign}_x\in\mathbb{Z}$，其中 $\mathrm{sign}_x=+1$ 若 $df_x(T_xM)\oplus T_zZ$ 的定向与 $T_zN$ 相容，$-1$ 否则。同样良定义、同伦不变。**度**是特例：$\deg(f)=I(f,\{y\})$（相交于一点）。$I(f,Z)\bmod 2=I_2(f,Z)$（定向细化 mod 2）。**环绕数**(linking number)：$A,B\subset\mathbb{R}^{n+k+1}$ 不相交紧致子流形，$\mathrm{lk}(A,B)=$ 度的推广。

**定向的精确定义**：$n$ 维向量空间 $V$ 的定向 $=$ 有序基的等价类（两个基等价 $\iff$ 过渡矩阵 $\det>0$），恰有两个等价类（$+$ 与 $-$）。流形 $M$ 的定向 $=$ 每点切空间 $T_xM$ 选一个等价类，且沿路径连续不翻转。可定向 $\iff$ 存在整体连续选择（如 $S^n$ 用外法向诱导定向）。不可定向（Möbius 带、$\mathbb{RP}^{2k}$）$=$ 绕一圈后定向翻转。$\mathrm{sign}_x$ 判定：$df_x(T_xM)\oplus T_zZ$ 给 $T_zN$ 的两组基，若定向相容则 $+1$，否则 $-1$——本质是直和定向的线性代数（$\det$ 符号）。
- **飞腾锚点**：**Schmidt 正交标架** —— 定向 $=$ 切空间**标架**的相容等价类，沿流形连续不翻转，类比 Gram-Schmidt 把任意基校准成一致的定向标架。$\mathrm{sign}_x$ 判定两个子空间的标架「拼起来」是否与全空间定向一致——本质是线性代数中直和定向的判定（$\det$ 符号）。
  - 🟢 事实：可定向流形（$S^n$、$\mathbb{R}^n$、$T^n$）才有定向相交数；$\mathbb{RP}^{2k}$ 不可定向只能用 $I_2$。$\deg$ 同伦不变：$f\simeq g\Rightarrow\deg(f)=\deg(g)$。
  - 🟡 类比：$\mathrm{sign}=+1$ 的交点「正向穿过」，$-1$「反向穿过」，净穿过次数 $=$ 定向相交数。
- **几何/应用**：定向相交数是 G&P 的核心不变量，统一了 Milnor 的度（$=$ 相交于点）、环绕数（$=$ 相交的推广）、Lefschetz 数（$=$ 图与对角线相交）。DNA 拓扑学用环绕数量化双螺旋缠绕；电磁学中载流线圈的互感与环绕数相关。G&P 把这些统一到「横截原像的带符号计数」这一个框架下。
- **关键定理**：$I(f,Z)=\sum_{x\in f^{-1}(Z)}\mathrm{sign}_x$ 良定义、同伦不变。度 $\boxed{\deg(f)=I(f,\{y\})=\sum_{x\in f^{-1}(y)}\mathrm{sign}(df_x)}$。
- **自测**：$f:S^1\to S^1$，$f(z)=z^k$，正则值 $1$ 的原像 $=k$ 个 $k$ 次单位根，每点 $\mathrm{sign}=+1$（保定向），$\deg(f)=k$。$f(z)=\bar{z}=z^{-1}$（复共轭），$\deg=-1$（反定向，反向绕一圈）。

---

### §5 环绕数与度：Brouwer、Borsuk-Ulam、Hopf（Winding & Degree）⭐⭐

> 环绕数 $W(f,z)$ / 代数基本定理 / Brouwer 不动点 / Borsuk-Ulam / Hopf 分类 / Lefschetz 不动点

- **核心**（约 80 字）：**环绕数** $W(f,z)$：$f:S^n\to\mathbb{R}^{n+1}$ 不经过 $z$，$W(f,z)=\deg(\hat{f})$，$\hat{f}(x)=(f(x)-z)/|f(x)-z|:S^n\to S^n$。**四大经典应用**：**（i）代数基本定理**——$\mathbb{C}$ 上非常值多项式必有根（用度论证：$z\mapsto p(z)$ 在大圆上的环绕数 $=\deg p\neq0$）；**（ii）Brouwer 不动点**——$f:D^n\to D^n$ 必有不动点（若否，构造 $g:\partial D^n\to\partial D^n$ 使 $\deg(g)\neq0$ 但 $g$ 同伦于常映射 $\deg=0$，矛盾）；**（iii）Borsuk-Ulam**——奇映射 $f:S^n\to S^n$（$f(-x)=-f(x)$）的度为奇数；**（iv）Hopf 定理**——$[S^n,S^n]\cong\mathbb{Z}$（按度完全分类）。**Lefschetz 不动点**（G&P 独有）：$L(f)=I(\mathrm{graph}(f),\Delta)$，$L(f)\neq0\Rightarrow f$ 有不动点。
- **飞腾锚点**：**UDOT 度计数** —— 度 $=$ 正则值原像的带符号净计数，恰似 **UDOT**（user-mode 计数指令）对事件做精确计数。环绕数 $=$ 映射绕某点的「净圈数」。Brouwer 不动点的度论证 $=$「如果没不动点就能构造矛盾计数」。
  - 🟢 事实：代数基本定理用度论证比代数证明更短更直观。Lefschetz 推广 Brouwer：$L(\mathrm{id})=\chi(M)$，故 $\chi(M)\neq0\Rightarrow$ 恒等映射的不动点（平凡），但对一般 $f$，$L(f)\neq0$ 给出非平凡不动点。
  - 🟡 类比：环绕数 $=$ 「绳子绕柱子几圈」，度 $=$ 「球面映射把球面包几层」，Lefschetz 数 $=$ 「映射的图与对角线交叉几次」。
- **几何/应用**：本章与 Milnor §3-5 高度重叠，但 G&P 用**相交理论框架**（而非纯度论）重新组织，并新增 **Lefschetz 不动点定理**。Lefschetz 定理把 Brouwer 推广到任意流形上的自映射：$L(f)=$ 图 $\Gamma_f=\{(x,f(x))\}\subset M\times M$ 与对角线 $\Delta$ 的相交数。$L(f)\neq0\Rightarrow f$ 有不动点（图必与对角线相交）。$L(\mathrm{id})=\chi(M)$（恒等映射的图 $=$ 对角线，自相交 $=\chi$）。Brouwer 是 $M=D^n$ 的特例（$\chi(D^n)=1\neq0$）。Brouwer 不动点是 Nash 均衡（博弈论）、Arrow-Debreu 一般均衡（经济学）的基础。Borsuk-Ulam 推论：「$S^n\to\mathbb{R}^n$ 必有 $f(x)=f(-x)$」（地球上必有对跖点同温同压）。Hopf 分类是同伦论的核心：$\pi_n(S^n)\cong\mathbb{Z}$。
- **关键定理**：**代数基本定理**——$\mathbb{C}$ 上非常值多项式有根。**Brouwer**——$f:D^n\to D^n$ 连续 $\Rightarrow\exists x,f(x)=x$。**Borsuk-Ulam**——奇映射 $f:S^n\to S^n$ 有奇数度。**Hopf**——$f,g:S^n\to S^n$ 同伦 $\iff\deg(f)=\deg(g)$，即 $\boxed{[S^n,S^n]\cong\mathbb{Z}}$。**Lefschetz**——$L(f)\neq0\Rightarrow f$ 有不动点。
- **自测**：用度论证证明代数基本定理：$p(z)=z^n+c_{n-1}z^{n-1}+\cdots+c_0$，在 $|z|=R$（$R$ 充分大）上 $\hat{p}(z)=p(z)/|p(z)|:S^1\to S^1$ 的度 $\approx n$（$z^n$ 主导），$\deg=n\neq0\Rightarrow p$ 在 $D_R$ 内有零点。附加：验证 Borsuk-Ulam 推论——$f:S^2\to\mathbb{R}^2$（如温度+气压映射）必有 $f(x)=f(-x)$（地球上必有对跖点同温同压），因为若 $f(x)\neq f(-x)$ 对一切 $x$，可构造奇映射矛盾 Borsuk-Ulam。

---

### §6 向量场指标与 Morse 理论引论（Vector Fields, Euler Characteristic, Morse）⭐⭐⭐

> 向量场零点指标 $\mathrm{ind}(v,x)$ / Poincaré-Hopf / $\chi(M)=$ 对角线自相交 / Morse 引理 $+$ 不等式

- **核心**（约 80 字）：$M^n$ 紧致定向，向量场 $v$ 有孤立零点 $x$。取小球面 $S_\epsilon\subset M$，$v/|v|:S_\epsilon\to S^{n-1}$，定义**指标** $\mathrm{ind}(v,x)=\deg(v/|v|)\in\mathbb{Z}$。**Poincaré-Hopf 定理**：$\sum_x\mathrm{ind}(v,x)=\chi(M)$。G&P 的**独门洞见**：$\chi(M)=I(\Delta,\Delta)$——Euler 示性数 $=$ 对角线 $\Delta\subset M\times M$ 的**自相交数**！这把 $\chi$ 从同调定义中解放出来，纯用相交理论得到。推论：$\chi(M)=0\iff M$ 上有处处非零向量场（毛球定理：$\chi(S^{2k})=2\neq0$，偶数维球面「梳不平」）。**Morse 理论引论**（附录）：Morse 函数 $f:M\to\mathbb{R}$（所有临界点非退化），Morse 引理给出局部标准型 $f=f(p)-\sum_{i\le\mu}x_i^2+\sum_{i>\mu}x_i^2$，Morse 不等式 $c_\mu\ge\beta_\mu$，$\sum(-1)^\mu c_\mu=\chi(M)$。
- **飞腾锚点**：**matmul Jacobian** ⭐ —— 向量场指标 $\mathrm{ind}(v,x)=\deg(v/|v|)$，在非退化零点处 $v(x)\approx A(x-x_0)$（$A=df$ 是 $v$ 的 Jacobian），$\mathrm{ind}=\mathrm{sign}\det A$——本质是对 $v$ 的 Jacobian 矩阵做行列式符号判定（$=$ matmul 式线性映射的定向保持/翻转）。Morse 指标 $\mu=$ Hessian（对称矩阵）的负惯性指数 $=$ 负特征值个数。
  - 🟢 事实：$\chi(S^n)=1+(-1)^n$（偶 $\to2$，奇 $\to0$）。非退化零点处 $\mathrm{ind}=\mathrm{sign}\det(Dv)$；退化零点需扰动到非退化再计数。$\chi(M)=I(\Delta,\Delta)$ 是 G&P 最优雅的定理之一。
  - 🟡 类比：$\mathrm{ind}=+1=$ 源/汇（向量向外/内辐射），$\mathrm{ind}=-1=$ 鞍点，$\mathrm{ind}=0=$ 可消去的零点对。Morse 函数 $=$ 地形高度，临界点 $=$ 峰/鞍/谷。
- **几何/应用**：Poincaré-Hopf 是「局部 $\leftrightarrow$ 全局」桥梁的典范。$\chi(M)=I(\Delta,\Delta)$ 这一 G&P 独门洞见把 Euler 示性数从同调群（Betti 数交替和）解放为纯相交理论的对象——对角线与自身的相交数。直观理解：$\Delta=\{(x,x):x\in M\}\subset M\times M$，将 $\Delta$ 略微扰动为 $\Delta'$（横截于自身），$\Delta\cap\Delta'$ 的交点数（带符号）$=$ 切丛的 Euler 类 $=$ Euler 示性数。这揭示了 $\chi(M)$ 的本质：它度量切丛 $TM$ 的「拓扑扭转」。Morse 理论深化：每个指标 $\mu$ 的临界点对应 attaching 一个 $\mu$-handle，流形同伦等价于 CW 复形。环面 $T^2$ 的高度函数有 4 临界点（1 极大 $\mu=2$ + 2 鞍 $\mu=1$ + 1 极小 $\mu=0$），$c_0-c_1+c_2=0=\chi(T^2)$。ML loss landscape 的「鞍点远多于极小」（Dauphin et al. 2014）正是 Morse 不等式 $c_\mu\ge\beta_\mu$ 的实证——高维空间中 $\mu$ 居中的鞍点指数占比最大。
- **关键定理**：**Poincaré-Hopf**——$M^n$ 紧致定向，$v$ 光滑向量场孤立零点 $\Rightarrow\boxed{\sum_x\mathrm{ind}(v,x)=\chi(M)}$。**Euler $=$ 自相交**——$\boxed{\chi(M)=I(\Delta,\Delta)}$（对角线在 $M\times M$ 中的自相交数）。**Morse 引理**——非退化临界点 $p$ 附近 $\exists$ 坐标使 $f=f(p)-\sum_{i\le\mu}x_i^2+\sum_{i>\mu}x_i^2$。**Morse 不等式**——$c_\mu\ge\beta_\mu$，$\sum_\mu(-1)^\mu c_\mu=\chi(M)$。

**$\chi=I(\Delta,\Delta)$ 的深层含义**：对角线 $\Delta\subset M\times M$ 的法丛同构于切丛 $TM$（因为 $T_{(x,x)}(M\times M)/T_{(x,x)}\Delta\cong T_xM$）。对角线自相交数 $=$ 法丛的 Euler 类 $e(TM)$ 在底流形上的取值 $=\chi(M)$。这揭示了 Euler 示性数的**本质**：它度量切丛 $TM$ 的「拓扑扭转」——$\chi\neq0$ 意味着切丛非平凡到「无法有处处非零截面」（即向量场必有零点）。这是 Poincaré-Hopf 定理的「丛论」解释，也是 stage-3 特征类（Stiefel-Whitney/Chern/Euler 类）的起点。
- **自测**：$S^2$ 上 $\chi=2$，任何向量场指标和 $=2\neq0\Rightarrow$ 必有零点（毛球定理）。$T^2$ 上 $\chi=0$，可取处处非零向量场（沿经线常速流），指标和 $=0$（无零点）。验证 $v(x,y)=(-y,x)$（旋转场）在原点 $\mathrm{ind}=+1$，$v=(x,-y)$（鞍点）$\mathrm{ind}=-1$。

---

## §9 主线：横截性 → 相交理论 → 度 → 应用 → Euler 示性数

| 阶段 | 章 | 核心工具 | 目标 | 飞腾锚点 |
|---|---|---|---|---|
| 工具箱 | 1 | 子流形/$df$/带边流形/Sard | 「正则值稠密 + 带边流形地基」 | TLB |
| 核心概念 | 2 | 横截性 $f\pitchfork Z$/Thom 定理 | 「横截是一般位置」 | 分支预测 |
| 相交数 | 3-4 | mod 2 / 定向计数 | 拓扑不变量 $I(f,Z)\in\mathbb{Z}$ | Iron Law / Schmidt |
| 应用 | 5 | 度/环绕数/Lefschetz | Brouwer/Borsuk-Ulam/Hopf | UDOT |
| 几何 | 6 | 向量场指标/Morse | $\chi(M)=\sum\mathrm{ind}=I(\Delta,\Delta)$ | matmul |

**一条红线**：全书围绕**「横截性 + 相交数」**这一对概念展开。Ch1 的 Sard 定理 + 带边流形铺路；Ch2 横截性把正则值推广到子流形，Thom 定理保证「横截是 generic 的」；Ch3-4 用横截原像的计数定义相交数 $I(f,Z)$（mod 2 先、定向后），度 $\deg=I(f,\{y\})$ 是特例；Ch5 把度用于 Brouwer/Borsuk-Ulam/Hopf/Lefschetz；Ch6 把相交理论用于对角线，得到 $\chi(M)=I(\Delta,\Delta)$，并引入 Morse 理论。

**G&P 的设计哲学**：横截性是所有后续章节的**引擎**——Ch2 的 Thom 横截定理保证「任意映射可扰动为横截」，于是 Ch3-4 的相交数**总有定义对象**（横截映射稠密）。这与 Milnor 的「Sard 定理保证正则值稠密」平行，但更一般（横截到子流形 $\supset$ 正则值 $=$ 横截到点）。1 维带边流形的边界定理是 Ch3 mod 2 守恒的基石，G&P 把 Milnor 藏在脚注的引理完整证明。$\chi(M)=I(\Delta,\Delta)$ 是全书的**美学巅峰**——用纯相交理论得到 Euler 示性数。

**G&P vs Milnor 的互补关系**：G&P 不是 Milnor 的替代品，而是**补充**。Milnor 的优势在「度论的极致凝练」（60 页直击灵魂）；G&P 的优势在「框架的完整性」（横截性 $+$ 相交理论 $+$ Lefschetz $+$ $\chi=I(\Delta,\Delta)$）。最佳策略：先读 Milnor 建立度论直觉（快，1-2 周），再读 G&P 补全框架（慢，3-4 周）。Milnor 像一首诗——每行不可删减；G&P 像一部小说——情节丰满、细节充实。两者合在一起，才是微分拓扑入门的**完整图景**。

**三条红线**：

1. **横截性红线**——$df$ 满射(Ch1 正则值) $\to$ $f\pitchfork Z$(Ch2 推广到子流形) $\to$ Thom 定理「横截 generic」(Ch2) $\to$ 相交数良定义(Ch3-4) $\to$ 对角线自相交 $f\pitchfork\Delta$(Ch6 $\chi$)。
2. **计数红线**——mod 2 计数 $I_2$(Ch3) $\to$ 带符号计数 $I$(Ch4) $\to$ 度 $\deg=I(f,\{y\})$(Ch4-5) $\to$ Hopf 分类 $[S^n,S^n]=\mathbb{Z}$(Ch5) $\to$ 指标和 $\sum\mathrm{ind}=\chi$(Ch6)。计数从 mod 2 经整数升级为同伦分类，再到拓扑不变量 $\chi$。
3. **微分 $\leftrightarrow$ 拓扑红线**——$df$/Sard(Ch1 微积分) $\to$ 横截 $df(T_xM)+T_zZ=T_zN$(Ch2 线性代数) $\to$ 相交数 $I$(Ch3-4 拓扑) $\to$ $\chi(M)$(Ch6 拓扑不变量) $\to$ Betti 数(同调)。G&P 的精髓：**用微分工具直接产出拓扑不变量**，绕过代数拓扑的链复形机器。

**与 Milnor 的关键差异**：Milnor 单线「正则值 $\to$ 度」；G&P 双线「横截性 $\to$ 相交数」（更一般的框架，度是特例）$+$「带边流形 $\to$ 边界定理」（更严格的良定义证明）。已读 Milnor 后读 G&P，核心新增 $=$ Ch2 横截性 $+$ Ch3-4 相交理论 $+$ Ch5 Lefschetz $+$ Ch6 $\chi=I(\Delta,\Delta)$。

**时间预算**（每周 10-20h）：

| 章 | 难度 | 预估时间 | 重点 |
|---|---|---|---|
| 1 | ⭐ | 4-6h | 带边流形（新于 Milnor）、Preimage 定理 |
| 2 | ⭐⭐⭐ | 8-10h | 横截定义、Thom 横截定理（全书关键） |
| 3 | ⭐⭐ | 6-8h | mod 2 相交数、1 维流形分类引理 |
| 4 | ⭐⭐ | 6-8h | 定向相交数、度 $=$ 相交于点 |
| 5 | ⭐⭐ | 6-8h | Brouwer/Borsuk-Ulam/Hopf/Lefschetz |
| 6 | ⭐⭐⭐ | 8-10h | $\chi=I(\Delta,\Delta)$、Poincaré-Hopf、Morse 引理 |
| **合计** | | **38-50h** | **3-4 周** |

**读法建议**：

- **Ch1 精读带边流形部分**（快速过子流形/$df$/Sard——已读 Milnor/Spivak），重点放在 $\partial M$ 的定义与 collar neighborhood——这是 Ch3 相交数良定义的隐藏地基。
- **Ch2 横截性死磕**（全书最关键、Milnor 没有的内容）：反复理解 $f\pitchfork Z\iff df(T_xM)+T_zZ=T_zN$，手算多个例子（曲线相交、曲面与曲线相交），理解 Thom 横截定理「横截是 generic」的威力。
- **Ch3-4 相交理论**——mod 2 先（享受「无需定向」的简洁），定向后（理解 sign 的线性代数本质 $=$ 直和定向判定）。**1 维流形分类引理**务必精读（Milnor 脚注 vs G&P 整节的对比）。
- **Ch5 应用**——已读 Milnor 的可快速过（度/Brouwer/Hopf 与 Milnor §3-5 重叠），**重点放在 Lefschetz 不动点**（G&P 独有）：$L(f)=I(\mathrm{graph}(f),\Delta)$。
- **Ch6**——$\chi(M)=I(\Delta,\Delta)$ 是全书皇冠明珠，务必理解「为什么对角线的自相交数 $=$ Euler 示性数」。Morse 理论引论读后转 Milnor《Morse Theory》(1963) 深入。

---

## §10 与本仓库其他笔记的交叉引用

**与 Milnor 从可微观点看拓扑对比**(stage-2，已读)：Milnor 是 G&P 的灵魂浓缩（60 页 vs 220 页）。已读 Milnor 后读 G&P $=$ 补三块新内容：**横截性**(Ch2，Milnor 几乎不提)、**相交理论**(Ch3-4，度 $=$ 相交于一点的特例，G&P 推广到任意维子流形)、**Lefschetz 不动点**(Ch5，Milnor 无)。此外 G&P 仔细证明了 Milnor 藏在脚注的「1 维流形分类」引理。建议：Milnor 为主（度论直觉），G&P 为辅（横截 $+$ 相交 $+$ Lefschetz 细节）。

**与 Bott-Tu 微分形式 GTM82 对比**(stage-2，已读)：Bott-Tu 用 de Rham 上同调（积分 $+$ $d^2=0$）做拓扑，G&P 用相交理论（横截计数）做拓扑——两者是**微分拓扑的两大互补支柱**：de Rham 管「上同调」（流形上有多少洞），相交理论管「子流形如何交叉」（映射/嵌入的拓扑障碍）。Poincaré-Hopf（$\sum\mathrm{ind}=\chi$）可视为交汇：指标是相交理论的应用，$\chi$ 又等于 de Rham Betti 数交替和。Gauss-Bonnet（Petersen）$=$ 几何侧，$\chi=I(\Delta,\Delta)$（G&P）$=$ 相交侧，$H^*_{dR}$（Bott-Tu）$=$ 上同调侧，三者殊途同归。

**与 Petersen/do Carmo 黎曼几何对比**(stage-2，已读)：Petersen/do Carmo 给切空间、向量场、度量的**几何语言**，G&P Ch6 向量场是其特例——但**不依赖黎曼度量**，纯光滑结构即可定义指标。Petersen 的 Gauss-Bonnet（$\int K\,dA=2\pi\chi$）是 Poincaré-Hopf 的几何实现（曲率 $=$ 向量场指标的连续分布）。建议：G&P 先读（相交理论直觉），Petersen 再读（叠加度量与曲率）。

**与 Hirsch 微分拓扑 GTM33 对比**(stage-2)：Hirsch(1976) 比 G&P 更系统全面——涵盖 Whitney 嵌入定理、Smale 浸入定理、函数空间拓扑、Thom 配边理论的完整发展。G&P 的横截性/相交理论在 Hirsch 中只是一小部分。建议：G&P 为入门（友好），Hirsch 为研究方向案头查阅。

**与 Lee 光滑流形对比**(stage-2)：Lee 用**抽象 atlas 定义**（现代标准），G&P 用**子流形 $\subset\mathbb{R}^N$ 定义**（具体传统）。Lee 的优势：内蕴定义（不依赖嵌入），积分论（Stokes 定理）完整。G&P 的优势：横截性/相交理论深入（Lee 几乎不涉及）。建议：G&P 先读（横截/相交），Lee 补读（抽象流形基础 $+$ Stokes 积分论）。

**与 Spivak 流形微积分对比**(stage-2，已读)：Spivak 在 $\mathbb{R}^n$ 中建立 $df$/Jacobian/逆函数定理/Stokes 定理的**微积分地基**，G&P 假设读者已掌握，直接用于「横截性判据 $df(T_xM)+T_zZ=T_zN$」。Spivak 的 Stokes 定理（积分侧）与 G&P 的相交理论（计数侧）是流形上**两大互补工具**——前者管「积分」（流形上的微积分基本定理），后者管「映射/子流形的拓扑障碍」。建议：Spivak 先读（$df$ 地基），G&P 再读（横截 $+$ 相交灵魂）。

**G&P 独有的三个定理**（Milnor/Lee/Hirsch 均无或不强调）：

1. **$\chi(M)=I(\Delta,\Delta)$**——Euler 示性数 $=$ 对角线自相交数。这是全书最优雅的结论，把 $\chi$ 从同调解放为纯相交理论。
2. **Lefschetz 不动点定理**——$L(f)=I(\Gamma_f,\Delta)\neq0\Rightarrow f$ 有不动点。推广 Brouwer（$M=D^n$ 的特例）到任意流形。
3. **Thom 横截定理的完整证明**——G&P 用参数化 Sard 定理（把 $f$ 嵌入参数族 $F:M\times S\to N$，对参数用 Sard）给出初等证明，是理解「横截是 generic」的最佳途径。

**AI 锚点（数学 $\leftrightarrow$ 工程）**：

- 🟢 **横截性 $=$ 「一般位置」 $=$ 鲁棒性**：$f\pitchfork Z$ 意味着相交是「稳定的」（微扰不变），类比机器学习中「正则条件」——非退化临界点、满秩 Jacobian、可识别参数。退化情形（非横截）$=$ 「病态」（ill-conditioned），微扰即变。
- 🟢 **Sard 定理 $=$ 「坏点是稀疏的」**：临界值零测 $\Rightarrow$ 正则值稠密。ML 中损失函数的「坏极值」（梯度为零的非最优点）也是低维的——随机搜索大概率落在「好区域」。
- 🟢 **$\chi(M)=I(\Delta,\Delta)$ $=$ 全局拓扑的局部计算**：Euler 示性数可以用「对角线和自己的交点数」局部地算出来，类似 GEMM/matmul 把全局矩阵运算分解为局部块的累乘累加。
- 🟡 **相交数 $=$ 拓扑障碍的计数**：$I(f,Z)\neq0\Rightarrow f$ 的像「必须穿过」$Z$（不可消除）。优化中，梯度场 $\nabla L$ 的零点（极小/鞍）受 $\chi$ 约束——$\chi\neq0$ 的可行域上任何梯度场必有零点。
- 🟢 **Morse 指标 $=$ Hessian 负惯性指数 $=$ 鞍点阶数**：loss landscape 的「鞍点指标」$\mu=$ Hessian 负特征值个数。Morse 不等式 $c_\mu\ge\beta_\mu$ 说「临界点数 $\ge$ 洞数」——高维非凸优化中鞍点远多于极小的拓扑根源（Dauphin 2014）。
- 🟡 **横截 $=$ 「满秩」 $=$ 可识别性**：$f\pitchfork Z$ 的条件 $df(T_xM)+T_zZ=T_zN$ 本质是切空间张满，类比满秩矩阵 $=$ 可逆 $=$ 信息无损。非横截（退化相交）$=$ 秩亏损 $=$ 信息丢失。
- 🟢 **Lefschetz 数 $=$ 「映射与恒等的偏差」**：$L(f)=I(\Gamma_f,\Delta)$ 度量 $f$ 的图与对角线（恒等映射的图）的交叉——$L(f)\neq0$ 意味着 $f$ 与恒等「纠缠」不可分离 $\Rightarrow$ 必有不动点。神经网络的自回归映射（$x_{t+1}=f(x_t)$）的不动点存在性受 Lefschetz 数约束。

**「三位一体」总结表**：G&P 全书可压缩为三个核心概念 $+$ 三个核心定理 $+$ 三个独门洞见：

| 层次 | 内容 | 章节 |
|---|---|---|
| 三概念 | 横截性 $f\pitchfork Z$ / 相交数 $I(f,Z)$ / 度 $\deg(f)$ | Ch2 / Ch3-4 / Ch4-5 |
| 三定理 | Thom 横截定理（横截 generic）/ Poincaré-Hopf（$\sum\mathrm{ind}=\chi$）/ Morse 不等式（$c_\mu\ge\beta_\mu$） | Ch2 / Ch6 / Ch6 |
| 三独门 | $\chi=I(\Delta,\Delta)$ / Lefschetz 不动点 / 1 维流形分类完整证明 | Ch6 / Ch5 / Ch3 |

---

## §11 自测答案要点（供核对）

1. **Ch1** $f(x,y,z)=x^2+y^2+z^2$：$df=(2x,2y,2z)$，$c>0$ 时 $f^{-1}(c)$ 上 $df\neq0$（球面上点非零），$\mathrm{rank}=1=N-k=3-2$，$c$ 正则值，$f^{-1}(c)=S^2_{\sqrt{c}}$ 是 $3-1=2$ 维子流形；$c=0$ 时 $df=(0,0,0)$，$0$ 临界值。
2. **Ch2** $f(x,y)=x^2-y^2$ 与 $Z=\{0\}$：$f^{-1}(0)=\{y=\pm x\}$（两条交叉直线），在原点 $df=(2x,-2y)=(0,0)$ 非横截（退化）。加微扰 $Z=\{\epsilon\}$（$\epsilon\neq0$）则 $f^{-1}(\epsilon)=\{x^2-y^2=\epsilon\}$（双曲线），$df\neq0$ 横截——体现「横截 $=$ generic，非横截 $=$ 退化特例」。
3. **Ch3** 两条直线 $L_1(y=0)$、$L_2(x=0)$ 在 $\mathbb{R}^2$ 中横截相交于原点，$I_2=1$（奇数次，拓扑非平凡）。$L_2$ 平移为 $y=1$（不相交）$I_2=0$（可消除）。注意：同伦 $y=t$ 在 $t=0$ 处非横截（重合），需扰动后才可计数——这正是横截性「generic」条件的必要性。**边界定理验证**：$W=[0,1]\times S^1$（柱面），$\partial W=\{0\}\times S^1\sqcup\{1\}\times S^1$，$f:\partial W\to\mathbb{R}^2$，若 $f$ 横截到点 $z$，则 $I_2(f,z)=0$——因为柱面的两条边界圆「方向相反」，贡献的 mod 2 计数必然相消。
4. **Ch4** $f(z)=z^k:S^1\to S^1$：正则值 $1$ 的原像 $=k$ 个 $k$ 次单位根 $e^{2\pi ij/k}$（$j=0,\ldots,k-1$），每点 $df=kz^{k-1}$ 保定向（$\mathrm{sign}=+1$），$\deg=k$。$f(z)=\bar{z}$：$\deg=-1$（反向绕一圈，$\mathrm{sign}=-1$ 一个点）。**环绕数验证**：两个链环 $A=S^1\times\{0\}$、$B=\{0\}\times S^1$ 在 $\mathbb{R}^3$ 中（坐标 $(x,y,z)$，$A$ 在 $z=0$ 平面单位圆，$B$ 在 $y=0$ 平面单位圆），$\mathrm{lk}(A,B)=1$（标准 Hopf 链环绕一圈）。
5. **Ch5** 代数基本定理：$p(z)=z^n+\cdots$，在 $|z|=R$（$R\gg$ 系数）上 $p(z)\approx z^n$，$\hat{p}=p/|p|:S^1\to S^1$ 的度 $\approx n$。$\deg=n\neq0\Rightarrow\hat{p}$ 非零伦 $\Rightarrow p$ 在 $D_R$ 内有零点（否则 $\hat{p}$ 可缩到 $p(0)/|p(0)|$，常映射 $\deg=0$，矛盾）。
6. **Ch6** $S^2$：$\chi=2\neq0\Rightarrow$ 任何向量场有零点（毛球定理）。$T^2$：$\chi=0\Rightarrow$ 可有非零场。$\chi=I(\Delta,\Delta)$：对角线 $\Delta=\{(x,x)\}\subset M\times M$，$\dim\Delta=\dim M$，$\dim(M\times M)=2\dim M$，互补维数 $\dim\Delta+\dim\Delta=2\dim M=\dim(M\times M)$，自相交数 $=$ Euler 示性数（$T^2$ 上 $I(\Delta,\Delta)=0$，$S^2$ 上 $=2$）。环面高度函数 4 临界点：$c_0=1$（极小）、$c_1=2$（鞍）、$c_2=1$（极大），$c_0-c_1+c_2=0=\chi(T^2)$ ✓。$v=(-y,x)$（旋转场）$\mathrm{ind}=+1$，$v=(x,-y)$（鞍点）$\mathrm{ind}=-1$，验证 $\mathrm{ind}=\mathrm{sign}\det(Dv)$（$Dv=\begin{pmatrix}0&-1\\1&0\end{pmatrix}$，$\det=1\Rightarrow+1$；$Dv=\begin{pmatrix}1&0\\0&-1\end{pmatrix}$，$\det=-1\Rightarrow-1$）。

> **核对原则**：每章的核心是「横截性 $+$ 相交数」这一对概念。Ch1 的 Sard 定理 $+$ 带边流形铺路；Ch2 横截性保证「任意映射可扰动为横截」（Thom 定理），于是 Ch3-4 相交数**总有定义对象**；Ch3-4 的相交数给出 Ch5 的度（$=$ 相交于点）与不动点（Lefschetz $=$ 图与对角线相交）；Ch6 把相交理论用于对角线自相交，得到 $\chi(M)=I(\Delta,\Delta)$，并推广到 Morse 理论（Hessian 惯性指数）。全书是从「横截性」到「拓扑不变量」的**双线逻辑链**（横截 $+$ 带边流形），相交数是核心不变量。

---

> **下一步**：沿 `01-track/stage-2` 精读 G&P **Ch2 横截性**（全书关键，Milnor 没有的核心概念），遇 Thom 横截定理查 `00-META/CONCEPT-INDEX`；Ch3-4 相交理论与 Milnor §3-4 度论交叉对照；Ch6 $\chi=I(\Delta,\Delta)$ 与 Bott-Tu de Rham $+$ Petersen Gauss-Bonnet 三视角对照验证；Morse 理论延伸到 Milnor《Morse Theory》(1963)。
>
> **stage-3 前瞻**：Hirsch GTM33（Whitney 嵌入/Smale 浸入/函数空间） $\to$ Thom 配边理论 $\to$ 特征类（Stiefel-Whitney/Chern） $\to$ h-配边定理（Milnor） $\to$ Floer 同调（无穷维 Morse） $\to$ 辛拓扑与规范场论。
>
> **一句话总结**：G&P 的全部精华在于——**把 Milnor 的「正则值 $\to$ 度」推广为「横截性 $\to$ 相交数」，用横截原像的计数统一了度、环绕数、不动点、Euler 示性数**。横截性是「一般位置」的严格化，相交数是横截原像的计数不变量，$\chi(M)=I(\Delta,\Delta)$ 是全书的皇冠明珠。理解了「横截 $\to$ 相交 $\to$ 计数」这一范式，就理解了为什么 G&P 是微分拓扑的最佳入门。
>
> **实操验证**（建议用 Python/NumPy）：
> - Ch1：用 `numpy.linalg.matrix_rank` 验证 $S^2$ 上每点 $df=(2x,2y,2z)$ 秩 $=1$（$0$ 是正则值）
> - Ch2：数值验证横截稳定性——对 $f(x,y)=x^2-y^2$ 与 $Z=\{0\}$ 加微扰 $+\epsilon$，观察非横截 $\to$ 横截的转变
> - Ch3：采样计数 $f:S^1\to S^1$，$f(z)=z^k$ 的 $\#f^{-1}(1)\bmod2=k\bmod2$
> - Ch6：用 `numpy.linalg.eigvalsh` 计算 Hessian 特征值，验证 Morse 指标 $=$ 负特征值个数（环面高度函数 4 临界点）
> - Ch6 附加：数值模拟 $S^2$ 上向量场（如 $v=(-y,x,0)$ 投影到切平面），验证必有零点（毛球定理）；$T^2$ 上沿经线常速流无零点
> - Ch5：数值验证代数基本定理——$p(z)=z^3-1$，采样 $|z|=2$ 上 $\hat{p}=p/|p|:S^1\to S^1$ 的度 $=3$（$z^3$ 主导），验证 $\deg\neq0\Rightarrow p$ 有零点
> - Ch4：数值验证定向度——$f:S^1\to S^1$，$f(z)=z^k$，采样正则值原像，每点计算 $\mathrm{sign}(df)$，累加验证 $\deg=k$
