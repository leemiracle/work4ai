# Hirsch《Differential Topology》(GTM33) · 快速逐章精读

> 基于原书：`Differential Topology` (Morris W. Hirsch, GTM33, Springer, 1976) / 读于：2026-07-02
> 定位：**Berkeley 教授的系统全面微分拓扑**，微分拓扑黄金时代的「公理化总成」。用函数空间拓扑 + 逼近 + 横截性三大引擎，系统推出 Whitney 嵌入/浸入定理、Thom 配边理论、Morse 理论与曲面分类。抽象、现代、可作研究方向案头查阅。
> 本文为**快速逐章精读**，每章 1 个飞腾锚点 + 1 个关键定理 + 1 道自测题。
> 前置：已读 **Milnor** 从可微观点看拓扑（度论灵魂）/ **Guillemin-Pollack** 微分拓扑（横截/相交）/ **Lee** 光滑流形 GTM218（抽象 atlas/Stokes/Lie 群），以及 Bott-Tu / Spivak / Petersen 黎曼几何。

---

## §0 引言：Hirsch GTM33 是什么，为什么读它

Morris W. Hirsch（UC Berkeley 教授，Smale 的长期合作者）的《Differential Topology》(GTM33, 1976) 是 stage-2 微分拓扑主线的**系统总成教材**。Hirsch 本人深植于 Berkeley 几何拓扑学派——与 Stephen Smale 合作发展了**动力系统**（结构稳定性）与**微分拓扑**，本书正是这一黄金时代（1950s-1970s，Milnor 度论 1965 / Thom 配边 1954 / Smale h-配边与高维 Poincaré 猜想 1961 / Whitney 嵌入经典化）方法论的**公理化收束**。

**全书核心策略**：与 Milnor（60 页单线度论）、G&P（220 页友好横截/相交）不同，Hirsch 用**三个抽象引擎**驱动整本微分拓扑：

- **函数空间拓扑**（Ch2）——在 $C^r(M,N)$ 上定义弱/强（Whitney）拓扑，使「映射的微扰」成为可操作的对象；
- **逼近定理**（Ch2）——连续映射可被光滑映射逼近，光滑映射可被「generic」映射逼近；
- **横截性 + Sard**（Ch3）——Thom 横截定理保证「横截是稠密开（generic）」，Sard 定理保证「正则值稠密」。

这三者组合，使 Hirsch 能**纯拓扑地**（不用代数拓扑、不用微分形式）推出全套不变量：Whitney 嵌入/浸入定理、度与 Euler 示性数、Morse 理论、Thom 配边、曲面分类。Hirsch 在序言明言：「我刻意避免代数拓扑与微分形式，先让读者看到几何分析的原始材料如何蒸馏为数值不变量（度、Euler 数、亏格、配边类），再学同调/同伦才会自然。」

**Hirsch 与 G&P / Milnor 的关键差异**：

- Milnor/G&P 用**子流形 $\subset\mathbb{R}^N$ 的具体定义**；Hirsch **两者兼用**——先从子流形起步（Ch1 §0），随即引入**抽象微分结构**（atlas，Ch1 §1），更现代、更内蕴。
- G&P 的横截性是**终点**（相交理论的基础）；Hirsch 的横截性是**工具**——用来证 Whitney 嵌入（投影降维靠横截）、Thom 配边（Pontryagin-Thom 构造靠横截）、Morse 理论（generic 性质）。
- Hirsch 独有（G&P/Milnor 无或浅）：**函数空间拓扑与逼近**（Ch2 全章）、**向量丛与管状邻域的系统理论**（Ch4 全章）、**Thom 配边理论的完整发展**（Ch7）、**Whitney 嵌入/浸入定理的完整证明**（Ch1§3 + Ch2 逼近的联合应用）、**同痕与曲面分类**（Ch8-9）。

**叙事弧线**分六步推进：

1. **Ch1** 建立流形（子流形 + 抽象 atlas）、切丛、浸入/嵌入、带边流形（含 neat 子流形）的工具箱；
2. **Ch2** 函数空间 $C^r(M,N)$ 的弱/强拓扑 + 逼近定理 + jet 空间 + Baire 性质——为「generic」论证奠基；
3. **Ch3** Sard 定理 + 横截性 + Thom 横截定理（横截是稠密开）——全书的方法论引擎；
4. **Ch4** 向量丛 + 管状邻域（嵌入子流形的法丛邻域）+ collar——几何结构；
5. **Ch5-6** 度、相交数、Euler 示性数（Poincaré-Hopf）+ Morse 理论（流形↔CW 复形）——数值不变量；
6. **Ch7-9** Thom 配边（Pontryagin-Thom 构造）+ 同痕 + 曲面分类——分类理论。

**与已读教材的关系**：

- Milnor 从可微观点 $=$ Hirsch Ch5「度」的灵魂浓缩；G&P 横截/相交 $=$ Hirsch Ch3 + Ch5 的友好版；已读两者后读 Hirsch $=$ 补全**函数空间、向量丛、管状邻域、Whitney 嵌入、Thom 配边、同痕、曲面分类**这七大块；
- Lee GTM218 $=$ 抽象流形 + Stokes 积分论的完整版；Hirsch Ch1 的抽象微分结构与 Lee 重叠，但 Hirsch 不用微分形式，纯横截/逼近推进；
- Bott-Tu $=$ de Rham 上同调（积分侧），Hirsch $=$ 相交/配边（计数侧），互补。

**与四本微分拓扑/流形教材的对比**（决定你该读哪本）：

| 维度 | **Hirsch** GTM33 (1976) | **Milnor** 从可微观点 (1965) | **Guillemin-Pollack** (1974) | **Lee** GTM218 (2012) |
|---|---|---|---|---|
| 流形定义 | 子流形 + 抽象 atlas（兼用） | 子流形 $\subset\mathbb{R}^N$ | 子流形 $\subset\mathbb{R}^N$ | 抽象 atlas（现代标准） |
| 篇幅/风格 | ~240 页，系统公理化 | ~60 页，极致凝练像诗 | ~220 页，友好图多习题丰富 | ~700 页，百科全书递归铺垫 |
| **函数空间/逼近** | ★核心章（Ch2 全章） | 无 | 无 | 无 |
| **横截性** | 有（Ch3，作工具） | 几乎不提 | ★核心章（终点） | 有（积分论侧） |
| **相交理论** | 有（Ch5） | 无（仅度） | ★核心（Ch3-4 双章） | 无 |
| Whitney 嵌入/浸入 | ★完整证明 | 无 | 简略引用 | 有（Ch6，用 Sard） |
| 向量丛/管状邻域 | ★核心章（Ch4） | 无 | 无 | 有（Ch10） |
| **Thom 配边** | ★核心章（Ch7） | §7 框架配边雏形 | 无 | 无 |
| Morse 理论 | 有（Ch6） | §7 引论 | 附录引论 | 无（超出范围） |
| 曲面分类/同痕 | ★Ch8-9 | 无 | 无 | 有（部分） |
| 微分形式/de Rham | 无（刻意回避） | 无 | 无 | ★核心 |
| 习题 | 多、偏理论、含未解题 | 少而精 | 丰富手算直觉导向 | 极多系统 |
| 适合谁 | 研究方向案头查阅、求系统全面 | terse 大师精读、追度论灵魂 | 自学者首选、需横截/相交 | 系统学全套光滑流形基础 |

**建议路线**：Milnor 从可微观点（度论灵魂，60 页） $\to$ G&P（横截/相交，220 页） $\to$ **Hirsch 本书**（系统全面，补函数空间/向量丛/嵌入/配边） $\to$ Lee GTM218（抽象 atlas + Stokes 积分论）或直接进 stage-3（h-配边 / 特征类）。

**为什么是「经典」**：Hirsch 之所以是微分拓扑的**标准参考**，理由有三：**（一）系统全面**——是唯一一本在 240 页内覆盖函数空间、逼近、横截、向量丛、管状邻域、Whitney 嵌入、度、Morse、Thom 配边、同痕、曲面分类的教材；**（二）公理化现代**——把 G&P/Milnor 的具体子流形论证提升为抽象 atlas + 函数空间拓扑 + Baire 性质的现代框架，是后续研究（h-配边、特征类、Floer 同调）的直接语言；**（三）刻意不用代数拓扑/微分形式**——先让你看到「几何分析的原始材料如何蒸馏为数值不变量」，再学同调才自然。

**公理化风格的代价与收益**：Hirsch 的弱/强拓扑、jet 空间、multijet transversality 对初学者**抽象陡峭**——不如 G&P 友好。但收益是**表达力**：函数空间拓扑让你能严格表述「generic 映射」「开稠条件」，jet 空间让你能把「映射的局部行为」参数化，这些是 G&P 用直觉绕开的工具。建议：**已读 G&P/Milnor 后**再读 Hirsch，把直觉对应到形式化定义。

**Berkeley 学派与 Smale 的烙印**：Hirsch 在 Berkeley 与 **Stephen Smale**（Fields 1966，高维 Poincaré 猜想 + h-配边）长期合作，本书深植于 Berkeley 几何拓扑学派的方法论——「**先分析（逼近/Sard/横截），后代数（同调/同伦）**」。Smale 证明高维 Poincaré 猜想（$\dim\ge5$）的核心工具是 **h-配边定理**，而 h-配边的证明正是 Hirsch Ch7 配边理论 + Ch8 同痕的直接延伸。Hirsch 把这一学派「用微分方法硬算拓扑」的风格系统化为教材，使读者能自然过渡到研究前沿（特征类、h-配边、指标定理）。

**为什么 Hirsch 刻意回避微分形式与代数拓扑**：这是全书最重要的**哲学选择**。Hirsch 在序言明言：「先让读者看到几何分析的原始材料如何蒸馏为数值不变量（度、Euler 数、亏格、配边类），再学同调/同伦才会自然。」微分形式（Bott-Tu/Lee 的 de Rham）与奇异同调（Hatcher/Fulton）是强大的**黑箱机器**，但初学者容易「只见机器不见原料」。Hirsch 用横截原像的**计数**（而非链复形）定义度/Euler 数/配边类，让不变量的**几何来源**透明可见——读完 Hirsch 再学 de Rham/同调，会有「原来这些代数机器在算这个」的顿悟。代价是 Hirsch 无法处理需要积分/上同调环的问题（如 Poincaré 对偶的乘法结构），这些留给 Bott-Tu/Lee。

**关于习题**：Hirsch 有数百道习题，「从常规到未解决的开放题」，但正文证明**很少依赖习题**（可作纯正文阅读）。习题分三层：**（一）验证**（验证具体映射的横截性、计算度）；**（二）理论发展**（证明 multijet 横截、管状邻域唯一性）；**（三）开放问题**（部分标注未解决）。建议研究方向者重点做 Ch2（函数空间）+ Ch7（配边）习题。

> 🟢 事实可作锚点：Sard 定理、Thom 横截定理、Whitney 嵌入/浸入定理、管状邻域定理、Poincaré-Hopf 定理、Morse 引理与不等式、Thom 配边定理均为严格定理。
> 🟡 类比（「横截 $=$ 一般位置」「管状邻域 $=$ 子流形的胖化」)仅供直觉，**绝不在严格证明中引用**。

**工程师阅读建议**（已读 Milnor/G&P/Lee 后）：

- **Ch1-2 是「形式化补课」**——子流形/atlas 与 Lee 重叠可快过；**函数空间弱/强拓扑**（Ch2）是新内容，务必理解「generic $=$ 开稠」（机器学习鲁棒性的拓扑根源）。
- **Ch3-4 是「方法论核心」**——Thom 横截定理（Ch3）+ Sard（Ch3§1）是全书引擎，管状邻域（Ch4）是几何桥梁。
- **Ch5 度论**——已读 Milnor/G&P，可对照「向量丛 Euler 数 $e(\xi)$」这一更一般框架。
- **Ch6 Whitney 嵌入**——Hirsch 独有的完整证明，投影降维法是亮点（流形学习维数上界的理论根据）。
- **Ch7 Thom 配边**——G&P/Milnor 无的核心章，stage-3 h-配边的直接前驱，务必精读。
- **Ch8-9 Morse + 同痕 + 曲面**——Morse 与 Milnor《Morse Theory》衔接；曲面分类是全书应用收尾。

---

## §1 全书 9 章骨架一览

| 章 | 标题（对应原书） | 核心概念 | 飞腾锚点 |
|---|---|---|---|
| 1 | 流形与映射 (Ch1) | 子流形/抽象 atlas/切丛 $TM$/浸入嵌入/带边 neat 子流形 | **TLB 局部坐标卡** ⭐ |
| 2 | 函数空间与逼近 (Ch2) | $C^r(M,N)$ 弱/强拓扑/光滑逼近/jet $J^k$/Baire | **FP16 半精度逼近** |
| 3 | 横截性 Thom (Ch3§2) | $f\pitchfork Z$/Thom 横截定理/稠密开/multijet | **分支预测 临界点** ⭐ |
| 4 | Sard 定理与稠密横截 (Ch3§1) | Morse-Sard（临界值零测）/参数化 Sard/generic | **分支预测 临界点** |
| 5 | 度与向量场 (Ch5) | $\deg(f)$/相交数/Euler 数 $e(\xi)$/Poincaré-Hopf | **UDOT 度计数** ⭐ |
| 6 | 嵌入与浸入 Whitney (Ch1§3+Ch2) | $M^n\hookrightarrow\mathbb{R}^{2n+1}$/浸入 $\mathbb{R}^{2n}$/投影降维 | **matmul Jacobian** |
| 7 | 配边 Thom (Ch7) | 配边类/Pontryagin-Thom 构造/Thom 谱 $MO$ | **Iron Law 正合序列** ⭐ |
| 8 | Morse 理论 (Ch6) | Morse 函数/Morse 引理/附着胞腔/CW 复形 | **GEMM 张量** ⭐ |
| 9 | 向量丛+附录 (Ch4+App) | 向量丛/分类定理/管状邻域/collar/分析背景 | **Schmidt 正交标架** |

**单线主线**：流形（子流形 + atlas） $\to$（函数空间拓扑）$C^r(M,N)$ $\to$（逼近）光滑化 $\to$（Sard）正则值稠密 $\to$（Thom 横截）generic 映射 $\to$（投影降维）Whitney 嵌入 $\to$（计数）度/Euler 数 $\to$（法丛）管状邻域 $\to$（Pontryagin-Thom）配边分类 $\to$（Morse）流形↔CW 复形 $\to$（应用）曲面分类。**横截性 + 逼近是贯穿全书的双引擎**。

---

### §1 流形与映射（Manifolds and Maps, Ch1）⭐

> 子流形 $\subset\mathbb{R}^{n+k}$ / 抽象微分结构（atlas）/ 切丛 $TM$ / 浸入与嵌入 / 带边流形与 neat 子流形

- **核心**（约 80 字）：Hirsch **双轨起步**：先定义 $\mathbb{R}^{n+k}$ 中 $n$ 维子流形 $M$（局部是投影 $\mathbb{R}^{n+k}\to\mathbb{R}^k$ 的零集），再引入**抽象微分结构**——拓扑流形 $M$（Hausdorff + 第二可数）配光滑相容图册（atlas），过渡映射 $C^\infty$。切丛 $TM$ 是导子/等价类刻画。**浸入** $\mathrm{rank}(df)=\dim M$，**嵌入** $=$ 浸入 + 拓扑嵌入。**带边流形**用半空间 $\mathbb{H}^n$，**neat 子流形**（整洁子流形）要求边界横截相交——这是管状邻域理论的基础。
- **飞腾锚点**：**TLB 局部坐标卡** ⭐ —— 流形的本质是「局部像 $\mathbb{R}^n$」：每点有 chart（局部坐标卡），换卡 $C^\infty$ 过渡，恰似 CPU **TLB** 把虚拟地址翻译成物理地址。抽象 atlas $=$ 不依赖嵌入的内蕴「地址翻译表」。
  - 🟢 事实：浸入局部是嵌入（逆函数定理）；嵌入 $=$ 浸入 $+$ 单射拓扑嵌入。neat 子流形 $N^k\subset M^n$（带边）满足 $\partial N=N\cap\partial M$ 且横截。
  - 🟡 类比：子流形的隐式定义 $g^{-1}(0)=$「约束方程解集」，$\mathrm{rank}(Dg)$ 满秩 $=$ 约束独立。
- **几何/应用**：$S^n$ 是 $\mathbb{R}^{n+1}$ 中子流形（$g=\sum x_i^2-1$）；neat 子流形概念让「带边流形中的子流形」有干净理论（管状邻域、collar），G&P 只用带边流形本身，Hirsch 发展到子流形层级。
- **关键定理**：**局部嵌入定理**——$M^n$ 光滑 $\Rightarrow$ 每点有邻域嵌入 $\mathbb{R}^{2n}$（逆函数定理推论）。**neat 子流形的 collar 定理**（Ch4 §6 完整证明）。
- **自测**：验证 $M=\{(x,y,z)\in\mathbb{R}^3:z=x^2+y^2\}$（抛物面）是 2 维子流形：$g=z-x^2-y^2$，$Dg=(-2x,-2y,1)\neq0$ 处处满秩，$\mathrm{rank}=1=k$。附加：写出 neat 子流形 $N=[0,1]\times\{0\}\subset D^2$（闭盘直径）满足 $\partial N=\{0,1\}\times\{0\}=N\cap\partial D^2$ ✓。

---

### §2 函数空间与逼近（Function Spaces, Ch2）⭐⭐

> $C^r(M,N)$ 弱/强（Whitney）拓扑 / 光滑逼近定理 / jet 空间 $J^k(M,N)$ / Baire 性质

- **核心**（约 80 字）：Hirsch 在 $C^r(M,N)$（$M\to N$ 的 $C^r$ 映射集）上定义两种拓扑：**弱拓扑**（紧致开 + 导数）与**强拓扑**（Whitney 拓扑，允许整个 $M$ 上的微扰控制）。**逼近定理**：$C^r$ 映射在 $C^r$ 拓扑中稠密（$C^\infty$ 稠于 $C^r$）；连续映射可被光滑映射 $C^0$ 逼近。**jet 空间** $J^k(M,N)$ 参数化「映射在某点的 $k$ 阶泰勒展开」，是横截定理的舞台。**Baire 定理**：$C^r(M,N)$ 是 Baire 空间 $\Rightarrow$ 可数个开稠集之交仍稠密 $\Rightarrow$「generic 性质」（横截、浸入、Morse）可表述为开稠。
- **飞腾锚点**：**FP16 半精度逼近** —— 逼近定理 $=$ 用「光滑函数」逼近「粗糙函数」，恰似用 **FP16 半精度**逼近 FP32——损失可控精度换取结构与效率。$C^\infty$ 稠于 $C^r$ $=$ 高精度模型总可用光滑函数拟合到任意容差。
  - 🟢 事实：强拓扑比弱拓扑细（更多开集）；$M$ 紧致时弱=强。Baire 性质保证「generic」= 可数交稠密。
  - 🟡 类比：jet $J^k$ $=$ 映射的「$k$ 阶特征向量」，把无穷维映射空间局部坐标化为有限维 jet 空间。
- **几何/应用**：逼近定理是 Whitney 嵌入证明的关键——先把 $M$ 拓扑嵌入 $\mathbb{R}^N$，再用光滑逼近 + 投影降维。工程上，函数空间拓扑 $=$ 「参数空间的度量」，Baire 性质 $=$ 「性质对几乎所有参数成立」（类似 ML 中「随机初始化大概率满足条件」）。
- **关键定理**：**光滑逼近定理**——$\forall f\in C^r(M,N)$，$\varepsilon>0$，$\exists g\in C^\infty(M,N)$ 使 $d_{C^r}(f,g)<\varepsilon$（紧致情形）。**Baire 定理**：$C^r(M,N)$ 在弱/强拓扑下是 Baire 空间（可数个开稠集之交仍稠密 $\Rightarrow$ generic 性质 = 可数交）。**jet 消没定理**：$k$-jet $j^k f:M\to J^k(M,N)$ 是 $C^r$ 嵌入（$r>k$），把映射空间局部化为有限维流形——multijet 横截的舞台。
- **自测**：Weierstrass 逼近（连续函数被多项式逼近）是 Hirsch 逼近定理在 $\mathbb{R}$ 上的特例。附加：解释为何强拓扑下「$C^\infty$ 稠于 $C^r$」比弱拓扑更强（强拓扑允许非紧 $M$ 上一致逼近）。

---

### §3 横截性 Thom（Transversality, Ch3§2）⭐⭐⭐

> 横截定义 $f\pitchfork Z$ / Thom 横截定理 / 稠密开性 / multijet transversality

- **核心**（约 80 字）：$f:M\to N$ **横截到**子流形 $Z\subset N$（$f\pitchfork Z$） $\iff$ $\forall x\in f^{-1}(Z)$：$df_x(T_xM)+T_{f(x)}Z=T_{f(x)}N$。正则值 $=$ 横截到点。三大结论：**（i）横截原像定理**：$f\pitchfork Z\Rightarrow f^{-1}(Z)$ 是余维 $=\mathrm{codim}Z$ 的子流形；**（ii）Thom 横截定理**：横截映射在 $C^r(M,N)$ 中**稠密开**（generic）；**（iii）multijet 横截**：映射族在不同点的行为独立横截。Thom 横截定理用**参数化 Sard**（把 $f$ 嵌入参数族 $F:M\times S\to N$，对参数用 Sard）证明。
- **飞腾锚点**：**分支预测 临界点** ⭐ —— 横截 $=$「一般位置」（generic），恰似 CPU **分支预测**走大概率路径。非横截 $=$ 退化临界点（分支翻转失败），微扰即变横截。Thom 定理：随机扰动几乎必然横截。
  - 🟢 事实：横截是开稠条件（强拓扑下）。$\dim M+\dim Z=\dim N$ 且 $f\pitchfork Z\Rightarrow f^{-1}(Z)$ 有限点集。
  - 🟡 类比：两曲线「横截相交」$=$ 不相切（切线张满平面），相切 $=$ 非横截退化。
- **几何/应用**：横截是 Hirsch 的**万能工具**——证 Whitney 嵌入（投影横截）、Thom 配边（子流形横截相交定义配边不变量）、Morse（generic 函数是非退化 Morse 函数）。G&P 把横截作为终点（相交理论），Hirsch 把横截作为**起点的工具**。
- **关键定理**：**Thom 横截定理**——$\forall f\in C^r(M,N)$，$\exists$ 任意接近 $f$ 的 $g\pitchfork Z$；且 $\{g:g\pitchfork Z\}$ 在 $C^r$ 中开稠。**横截原像定理**：$f\pitchfork Z\Rightarrow f^{-1}(Z)$ 光滑子流形，$\dim=m-n+\dim Z$。
- **自测**：$f:\mathbb{R}^2\to\mathbb{R}$，$f(x,y)=x^2-y^2$，$Z=\{0\}$。$(0,0)$ 处 $df=(0,0)$ 非横截（退化）；$Z=\{1\}$ 时 $f^{-1}(1)$（双曲线）$df\neq0$ 横截。附加：解释 multijet 横截为何保证「自映射的不同原像点行为独立」。

---

### §4 Sard 定理与稠密横截（Morse-Sard Theorem, Ch3§1）

> Morse-Sard 定理（临界值零测）/ 参数化 Sard / 稠密横截的引擎

- **核心**（约 80 字）：**Morse-Sard 定理**——$f:M^m\to N^n$ 是 $C^r$（$r>\max(m-n,0)$），则临界值集 $f(\mathrm{Crit}f)\subset N$ 的 Lebesgue 测度为零。$\Rightarrow$ 正则值在 $N$ 中**稠密**（补集是零测的「薄集」）。**参数化 Sard**（Thom 横截定理的引擎）：把映射族 $F:M\times S\to N$ 视为对参数 $s\in S$ 的族，对 $F$ 用 Sard $\Rightarrow$ 对 generic 参数 $s$，$f_s$ 横截——这是「横截是 generic」的严格根源。Sard 是**整个微分拓扑「generic」论证的地基**。
- **飞腾锚点**：**分支预测 临界点** —— Sard 定理 $=$「坏点（临界值）是稀疏的（零测）」，正则值稠密 $=$ 大概率路径。恰似 **分支预测**：临界值 $=$ 分支预测失误的稀有路径，generic 参数走正则路径。
  - 🟢 事实：$C^1$ 情形（$m\le n$）证明用 Fubini + 1 维情形；高阶 $C^r$ 用更精细的覆盖论证。零测 $\neq$ 离散（如 Cantor 集）。
  - 🟡 类比：临界值 $=$ 损失函数的「坏极值」（稀疏），正则值 $=$ 好区域（稠密），随机采样大概率落好区。
- **几何/应用**：Sard 保证度 $\deg(f)$ 总有正则值可选（Milnor 度论地基）；保证 Whitney 嵌入的投影方向存在（投影到好方向 $\Rightarrow$ 嵌入）；保证 Morse 函数 generic（非退化临界点）。工程上，Sard $=$ 「病态点是低维的」鲁棒性原理。
- **关键定理**：**Morse-Sard 定理**——$f\in C^r(U\subset\mathbb{R}^m,\mathbb{R}^n)$，$r>\max(m-n,0)$，则 $f(\mathrm{Crit}f)$ 的 Lebesgue 测度为零。**推论**：正则值集 $N\setminus f(\mathrm{Crit}f)$ 在 $N$ 中稠密。**参数化 Sard**（Thom 横截的引擎）：$F:M\times S\to N$，$F$ 横截到 $Z$ $\Rightarrow$ 对 generic $s\in S$，$f_s=F(\cdot,s)\pitchfork Z$。
- **自测**：$f:\mathbb{R}^2\to\mathbb{R}$，$f(x,y)=x^2+y^2$。$\mathrm{Crit}f=\{(0,0)\}$（$df=(0,0)$），$f(\mathrm{Crit})=\{0\}$（单点，零测 $\checkmark$）。附加：Peano 曲线（连续满射 $[0,1]\to[0,1]^2$）为何不违反 Sard？（非 $C^1$，Sard 需 $C^r$）。

---

### §5 度与向量场（Degrees, Intersection, Euler Characteristic, Ch5）⭐⭐

> 映射度 $\deg(f)$ / 相交数 / 向量丛的 Euler 数 $e(\xi)$ / Poincaré-Hopf 定理

- **核心**（约 80 字）：**度** $\deg(f)$（$f:M^n\to N^n$ 紧致定向无边，同伦不变量）：选正则值 $y$，$\deg(f)=\sum_{x\in f^{-1}(y)}\mathrm{sign}(df_x)$。**相交数** $I(f,Z)$ 推广度（$f$ 与子流形 $Z$ 横截相交的带符号计数）。**Euler 数** $e(\xi)$（定向 $n$ 平面向量丛 $\xi\to M^n$）$=$ 零截面自相交数；$e(TM)=\chi(M)$（Euler 示性数）。**Poincaré-Hopf**：紧致流形上向量场（孤立零点）的指标和 $=$ Euler 示性数。Hirsch 把 Milnor/G&P 的度论**纳入向量丛 Euler 数的统一框架**。
- **飞腾锚点**：**UDOT 度计数** ⭐ —— 度 $=$ 横截原像的「带符号计数」，恰似 **UDOT**（统一设计）的指令计数：每个原像点 $=$ 一条指令，符号 $\pm1$$=$ 正向/反向执行，净计数 $=$ 拓扑不变量。
  - 🟢 事实：度与正则值选取无关（同伦不变性，1 维带边流形边界定理）。$\deg(\mathrm{id})=1$，$\deg(z^k:S^1\to S^1)=k$。
  - 🟡 类比：Euler 数 $=$ 「零截面穿过的次数」，$\chi\neq0\Rightarrow$ 向量场必有零点（毛球定理）。
- **几何/应用**：度论统一 Brouwer 不动点（$\deg=\pm1\neq0$）、代数基本定理（$\deg=n$）、Hopf 分类（$[S^n,S^n]\cong\mathbb{Z}$）。Poincaré-Hopf $=$ 毛球定理（$\chi(S^{2k})=2\neq0$）。Hirsch 的向量丛 Euler 数 $e(\xi)$ 比 Milnor/G&P 更一般（任意向量丛，不限于切丛）。
- **关键定理**：**Poincaré-Hopf 定理**——紧致定向无边 $M^n$，向量场 $v$ 有孤立零点 $\Rightarrow$ $\sum_{p:v(p)=0}\mathrm{ind}_p(v)=\chi(M)$。**$e(TM)=\chi(M)$**。
- **自测**：$f(z)=z^3:S^1\to S^1$，正则值 $1$ 的原像 $=$ 3 个三次单位根，每点 $\mathrm{sign}=+1$，$\deg=3$。$S^2$：$\chi=2\Rightarrow$ 任何向量场有零点（毛球）。$T^2$：$\chi=0\Rightarrow$ 可有无零点场。附加：验证 $e(TM)=\chi(M)$ 与 G&P「$\chi=I(\Delta,\Delta)$」的一致性。

---

### §6 嵌入与浸入 Whitney（Embeddings & Immersions, Ch1§3 + Ch2 逼近）

> Whitney 嵌入定理 $M^n\hookrightarrow\mathbb{R}^{2n+1}$ / 浸入定理 / 投影降维法

- **核心**（约 80 字）：**Whitney 嵌入定理**——任何 $n$ 维光滑流形（Hausdorff + 第二可数）可**嵌入** $\mathbb{R}^{2n+1}$（强拓扑下 generic 嵌入），可**浸入** $\mathbb{R}^{2n}$。Hirsch 的证明用**逼近 + 投影降维**三步：**（i）** 先用单位分解把 $M$ 拓扑嵌入某 $\mathbb{R}^N$（$N\gg n$），光滑逼近得光滑嵌入；**（ii）** 若 $N>2n+1$，找一个方向 $v$ 使投影 $\pi_v:\mathbb{R}^N\to v^\perp$ 仍保持嵌入（横截条件：$v$ 不平行于任何割线/切线）；**（iii）** 用 Sard（投影方向的「坏方向」零测）逐步降到 $\mathbb{R}^{2n+1}$。浸入到 $\mathbb{R}^{2n}$ 用消去自相交点。
- **飞腾锚点**：**matmul Jacobian** —— Whitney 嵌入的投影降维 $=$ 线性代数（投影是秩 $N-1$ 的线性映射），关键是投影方向使 **Jacobian** 仍满秩（浸入）且无自相交（嵌入）。恰似 **matmul**：高维数据投影到低维仍保结构 $=$ 满秩映射保信息。
  - 🟢 事实：$2n+1$ 来自「割线方向」空间维数 $\le 2n$（两点 $\Rightarrow\dim\le2n$），Sard 保证好方向存在。$2n$ 浸入需消去二重点（ Whitney trick）。
  - 🟡 类比：嵌入 $=$ 流形「无损放入」欧氏空间，投影降维 $=$ PCA 降维保结构。
- **几何/应用**：Whitney 嵌入是 G&P/Milnor「子流形定义够用」的**理论保证**——任何抽象流形可嵌入 $\mathbb{R}^{2n+1}$，故子流形定义不损失一般性。工程上，流形学习（ISOMAP/t-SNE）假设数据在低维流形上，Whitney 定理给出嵌入维数的上界 $2n+1$。
- **关键定理**：**Whitney 嵌入定理**——$M^n$ 光滑（第二可数） $\Rightarrow$ $\exists$ 嵌入 $M^n\hookrightarrow\mathbb{R}^{2n+1}$；$\exists$ 浸入 $M^n\to\mathbb{R}^{2n}$。
- **自测**：$S^1$ 可嵌入 $\mathbb{R}^2$（$2\cdot1+1=3$，实际 $\mathbb{R}^2$ 够）。$T^2$ 嵌入 $\mathbb{R}^3$（$2\cdot2+1=5$，实际 $\mathbb{R}^3$ 够）。附加：解释为何 $2n+1$ 是「割线流形」$\mathrm{Sec}(M)=\{(x,y):x\neq y\}/(x\sim y)$ 的维数 $\le2n$ 决定的。

---

### §7 配边 Thom（Cobordism, Ch7）⭐⭐⭐

> 配边等价类 / Pontryagin-Thom 构造 / Thom 谱 $MO$ / Thom 配边定理

- **核心**（约 80 字）：两 $n$ 维流形 $M_0,M_1$ **配边**（$M_0\sim M_1$） $\iff$ $\exists$ $(n+1)$ 维紧致流形 $W$，$\partial W=M_0\sqcup M_1$（$M_0$ 反向定向）。配边类构成**配边环** $\mathfrak{N}_n$（不交并 $=$ 加，积 $=$ 乘）。**Pontryagin-Thom 构造**：$n$ 维流形 $M^n\subset\mathbb{R}^{n+k}$ 的标架法丛 $\Rightarrow$ 映射 $S^{n+k}\to S^k$（Thom 空间 $MO(k)=\mathrm{Th}(\gamma^k)$），建立**配边类 $\cong$ 同伦群** $\mathfrak{N}_n\cong\pi_{n+k}(MO(k))$（$k\gg n$）。**Thom 配边定理**：非定向配边环 $\mathfrak{N}_*\cong\mathbb{Z}_2[x_2,x_4,x_5,\ldots]$（偶数维 + 部分 odd 生成元的多项式环）。
- **飞腾锚点**：**Iron Law 正合序列** ⭐ —— Pontryagin-Thom 构造把「几何配边」翻译为「同伦群」，配边环 $=$ Thom 谱 $MO$ 的稳定同伦群，恰似 **Iron Law 正合序列**：把几何对象映射到代数不变量，序列的正合性 $=$ 信息无损翻译。
  - 🟢 事实：Thom 谱 $MO=\{MO(k)\}$ 的稳定同伦群 $=$ 非定向配边环。定向配边 $\Omega_*^{SO}$ 用 $MSO$ 谱。
  - 🟡 类比：配边 $=$ 「两个流形可作某个高维流形的边界」，$=$ 「同伦等价的几何版」。
- **几何/应用**：Thom 配边理论是 1954 年 Fields 级工作，把「流形分类」问题转化为「同伦群计算」——这是**代数拓扑反哺微分拓扑**的典范。Milnor 怪球面（1956）的 28 种微分结构 $=$ 配边群 $\Theta_7$ 的计算。stage-3 的 h-配边定理（Smale，证高维 Poincaré 猜想）直接延续此线。
- **关键定理**：**Thom 配边定理**——$\mathfrak{N}_n\cong\pi_{n+k}(MO(k))$（$k\ge n+1$），且 $\mathfrak{N}_*\cong\mathbb{Z}_2[x_{2i}:i\neq2^j-1]\otimes\mathbb{Z}_2[x_{2^j-1}]$（多项式环）。**Pontryagin-Thom 构造**是同构的构造。
- **自测**：$\mathbb{RP}^2$ 不配边于 $\emptyset$（$w_1(\mathbb{RP}^2)\neq0$，Stiefel-Whitney 数非零）。$S^n$ 配边于 $\emptyset$（$D^{n+1}$ 的边界）。附加：解释 Pontryagin-Thom 为何把「子流形的标架法丛」编码为「映射到 Thom 空间」。

---

### §8 Morse 理论（Morse Theory, Ch6）⭐⭐

> Morse 函数 / Morse 引理 / 过临界水平附着胞腔 / 流形↔CW 复形

- **核心**（约 80 字）：$f:M^n\to\mathbb{R}$ 是 **Morse 函数** $\iff$ 所有临界点非退化（Hessian 非奇异）。**Morse 引理**：非退化临界点 $p$ 附近，$f=f(p)-x_1^2-\cdots-x_\lambda^2+x_{\lambda+1}^2+\cdots+x_n^2$（$\lambda=$ Morse 指标 $=$ Hessian 负惯性指数）。**核心机制**：当参数 $t$ 越过临界水平 $f(p)$ 时，下水平集 $M^t=\{f\le t\}$ 的拓扑**附着一个 $\lambda$ 维胞腔**（handle）。$\Rightarrow$ $M$ 同伦等价于 CW 复形，胞腔数 $c_\lambda\ge\beta_\lambda$（Betti 数，**Morse 不等式**）。generic 函数是 Morse 函数（横截/Sard 保证）。
- **飞腾锚点**：**GEMM 张量** ⭐ —— Morse 指标 $\lambda=$ Hessian 负特征值个数 $=$ 鞍点阶数，恰似 **GEMM 张量**的惯性指数：Hessian 是对称矩阵（2 阶张量），负惯性指数 $=$ 「下降方向数」。loss landscape 的鞍点指标 $\mu$ 受 Morse 不等式约束。
  - 🟢 事实：Morse 引理是坐标变换（$C^\infty$ 微分同胚）把 $f$ 化为标准二次型。Morse 不等式：$c_\mu-c_{\mu-1}+\cdots\pm c_0\ge\beta_\mu-\beta_{\mu-1}+\cdots\pm\beta_0$。
  - 🟡 类比：Morse 函数 $=$「地形高度」，临界点 $=$ 峰/谷/鞍，过临界水平 $=$「地形突变」（附着洞穴）。
- **几何/应用**：Morse 理论把流形拓扑与「函数的临界点」挂钩——$S^2$ 高度函数 2 临界点（极小+极大）$\Rightarrow S^2\simeq e^0\cup e^2$。$T^2$ 高度函数 4 临界点（1 极小 +2 鞍 +1 极大）$\Rightarrow c_0-c_1+c_2=1-2+1=0=\chi(T^2)$。ML loss landscape：高维非凸优化鞍点远多于极小（Dauphin 2014），拓扑根源 $=$ Morse 不等式。
- **关键定理**：**Morse 引理**——$p$ 非退化临界点 $\Rightarrow\exists$ 局部坐标使 $f=f(p)-\sum_1^\lambda x_i^2+\sum_{\lambda+1}^n x_i^2$。**Morse 不等式**：$c_\lambda\ge\beta_\lambda$（临界点数 $\ge$ Betti 数）。
- **自测**：环面高度函数 4 临界点：指标 $0,1,1,2$（极小/鞍/鞍/极大），$c_0=1,c_1=2,c_2=1$，验证 $c_0-c_1+c_2=0=\chi(T^2)$。附加：用 `numpy.linalg.eigvalsh` 算 Hessian 负特征值个数 $=$ Morse 指标，验证 $f(x,y)=x^2-y^2$ 在 $(0,0)$ 指标 $=1$（鞍点）。

---

### §9 向量丛与管状邻域 + 附录（Vector Bundles & Tubular Neighborhoods, Ch4 + Appendix）⭐⭐

> 向量丛 / 转移函数 / 分类定理（Grassmann 流形） / 管状邻域 / collar / 分析拓扑附录

- **核心**（约 80 字）：**向量丛** $\xi=(E,\pi,M,F)$：总空间 $E$、底 $M$、纤维 $F\cong\mathbb{R}^k$、局部平凡化，转移函数取值 $\mathrm{GL}(k)$。运算：直和 $\oplus$、张量积 $\otimes$、拉回 $f^*\xi$。**分类定理**：$k$ 平面向量丛的同伦类 $\cong$ $[M,\mathrm{Gr}_k(\mathbb{R}^\infty)]$（映射到无穷 Grassmann 流形），万有丛 $\gamma^k\to\mathrm{Gr}_k$。**管状邻域定理**：嵌入子流形 $N\subset M$ 有法丛 $\nu$，$\exists$ 开邻域 $U\supset N$ 微分同胚于 $\nu$（「子流形的胖化」）。**collar neighborhood**：带边流形 $\partial M$ 有邻域 $\cong\partial M\times[0,1)$（collar 定理）。附录回顾分析/点集拓扑背景（Stone-Weierstrass 逼近、Tietze 扩张、仿紧性、单位分解存在性）——这些是函数空间拓扑与逼近定理的分析地基。
- **飞腾锚点**：**Schmidt 正交标架** —— 向量丛 $=$ 「每点贴一个向量空间」，局部用**标架**（$k$ 个无关向量）坐标化，转移函数 $=$ 标架变换（$\mathrm{GL}(k)$），恰似 **Schmidt 正交化**给每点选正交基。管状邻域 $=$ 法丛的标架化「胖化」。
  - 🟢 事实：管状邻域在同痕意义下唯一（Ch8）。分类定理 $=$ Grassmann 流形是「丛的分类空间」。
  - 🟡 类比：向量丛 $=$ 「参数化的线性空间族」，Möbius 带 $=$ $S^1$ 上非平凡线丛（扭转一次）。
- **几何/应用**：管状邻域是**相交理论/配边理论的几何基础**——子流形的法丛编码「周围空间如何包裹子流形」。分类定理把「丛的分类」变为「同伦论」（映射到 Grassmann），是特征类（Stiefel-Whitney/Chern）的舞台。工程上，向量丛 $=$ 参数化的线性模型族（如神经网络每层的权重空间随输入变化）。
- **关键定理**：**管状邻域定理**——闭嵌入子流形 $N^k\subset M^n$（neat） $\Rightarrow$ 法丛 $\nu_{N/M}$ 有开邻域 $U\overset{\mathrm{diff}}{\cong}\nu$。**向量丛分类定理**：$\mathrm{Vect}_k(M)\cong[M,\mathrm{Gr}_k(\mathbb{R}^N)]$（$N\gg k,\dim M$）。
- **自测**：Möbius 带 $=$ $S^1$ 上线丛，转移函数在两 chart 间用 $-1$（扭转），非平凡（$\neq$ 圆柱 $S^1\times\mathbb{R}$）。$TS^2$ 法丛（$S^2\subset\mathbb{R}^3$）$\cong$ 法线丛，管状邻域 $=$ $S^2$ 的「厚壳」。附加：解释为何 $TS^2\oplus\nu\cong\mathbb{R}^3$（平凡 3 丛，嵌入诱导）。

---

## §10 主线总结与交叉引用

**全书主线**：Hirsch 的微分拓扑是「**函数空间拓扑 $\to$ 逼近 $\to$ Sard $\to$ 横截 $\to$ 几何结构（嵌入/丛）$\to$ 不变量（度/Euler）$\to$ 分类（配边/Morse/曲面）**」的**公理化链条**。横截性 + 逼近是双引擎，generic 性质（Baire）是粘合剂，管状邻域 + 法丛是几何桥梁，配边 + Morse 是分类高潮。与 G&P（横截/相交为终点）、Milnor（度为单线）不同，Hirsch 把这些工具**组合使用**：Whitney 嵌入 $=$ 逼近 $+$ Sard $+$ 横截；Thom 配边 $=$ 横截 $+$ 法丛 $+$ 同伦；Morse $=$ Sard（generic）$+$ 胞腔附着。

**与本仓库其他笔记的交叉引用**：

- **Milnor 从可微观点**(stage-2，已读)：Milnor 是 Hirsch Ch5「度」的灵魂浓缩。已读 Milnor 后读 Hirsch $=$ 补**函数空间（Ch2）、向量丛/管状邻域（Ch4）、Whitney 嵌入（Ch6）、Thom 配边（Ch7）、同痕/曲面（Ch8-9）**七大块。建议：Milnor 给度论直觉，Hirsch 给系统框架。
- **Guillemin-Pollack**(stage-2，已读)：G&P 的横截/相交是 Hirsch Ch3+Ch5 的友好版。Hirsch 比 G&P 多了函数空间拓扑（generic 论证的严格基础）、管状邻域（相交理论的几何根基）、Thom 配边（G&P 完全无）。建议：G&P 先读（直觉），Hirsch 再读（系统 + 研究语言）。
- **Lee GTM218**(stage-2，已读)：Lee Ch1 抽象 atlas $\cong$ Hirsch Ch1 §1；Lee Ch10 向量丛 $\cong$ Hirsch Ch4（但 Hirsch 多管状邻域/collar）。Lee 有 Stokes/de Rham（Hirsch 刻意回避），Hirsch 有配边/同痕/曲面分类（Lee 无）。建议：Hirsch（计数侧）+ Lee（积分侧）$=$ 微分拓扑 $+$ 微分几何的完整基础。
- **Bott-Tu GTM82**(stage-2，已读)：Bott-Tu 用 de Rham（积分侧），Hirsch 用横截/相交（计数侧），互补。Thom 配边（Hirsch Ch7）的定向版 $\Omega_*^{SO}$ 用 Stiefel-Whitney/Chern 特征类（Bott-Tu / stage-3）。
- **Petersen/do Carmo**(黎曼几何)：提供切丛/度量的几何语言，Hirsch 的向量丛是其抽象化（不依赖度量）。

**Hirsch 独有的四大块**（Milnor/G&P/Lee 无或不深入）：**（1）函数空间弱/强拓扑 + 逼近 + Baire**（Ch2，generic 论证基础）；**（2）管状邻域 + collar 完整理论**（Ch4，几何结构）；**（3）Thom 配边 + Pontryagin-Thom 构造**（Ch7，分类理论巅峰）；**（4）同痕 + 曲面分类**（Ch8-9，微分拓扑的经典应用）。

**研究脉络（Hirsch → stage-3）**：Hirsch 全书是「**微分拓扑的方法论总成**」，每个核心定理都是一条研究分支的起点：

- **函数空间拓扑（Ch2）** $\to$ 无穷维流形 / Fredholm 理论 / Floer 同调（无穷维 Morse）；
- **Whitney 嵌入（Ch6）** $\to$ 嵌入/浸入分类（Smale-Hirsch 定理：浸入类 $\cong$ 切丛的单同伦类）；
- **Thom 配边（Ch7）** $\to$ h-配边定理（Smale，高维 Poincaré 猜想）/ 特征类（Stiefel-Whitney/Chern/Pontryagin）/ 指标定理（Atiyah-Singer）；
- **Morse 理论（Ch8）** $\to$ Milnor《Morse Theory》/ 辛拓扑（Floer）/ 规范场论（Donaldson/Seiberg-Witten）。

读完 Hirsch，stage-3 的自然顺序是：**特征类（Bott-Tu/Milnor-Stasheff） $\to$ h-配边（Milnor） $\to$ 指标定理（Atiyah-Singer） $\to$ 规范场论**。Hirsch 的横截/逼近/配边语言贯穿全程。

**AI 锚点（数学 $\leftrightarrow$ 工程）**：

- 🟢 **函数空间拓扑 $=$ 「参数空间度量」**：$C^r(M,N)$ 的弱/强拓扑 $=$ 映射空间的「loss 地形」，Baire 性质 $=$ 「好性质对几乎所有参数成立」（随机初始化鲁棒性）。
- 🟢 **逼近定理 $=$ 「光滑模型可拟合任意连续函数」**：$C^\infty$ 稠于 $C^r$ $=$ 万能逼近定理（神经网络万能逼近的拓扑版）。
- 🟢 **Whitney 嵌入 $=$ 「流形学习的维数上界」**：数据流形维数 $n$ $\Rightarrow$ 嵌入维数 $\le2n+1$（ISOMAP/t-SNE 的理论根据）。
- 🟢 **Thom 配边 $=$ 「几何 $\to$ 代数的无损翻译」**：Pontryagin-Thom 把流形分类翻译为同伦群计算，类比把几何问题编码为代数（代数化思想）。
- 🟡 **管状邻域 $=$ 「子流形的胖化」**：法丛的微分同胚邻域，类比数据的「局部线性近似」（流形学习的切空间估计）。

**「三位一体」总结**：Hirsch 全书可压缩为三引擎 $+$ 三结构 $+$ 三分类：

| 层次 | 内容 | 章节 |
|---|---|---|
| 三引擎 | 函数空间拓扑/逼近 / Sard / Thom 横截 | Ch2 / Ch3§1 / Ch3§2 |
| 三结构 | 向量丛+管状邻域 / 嵌入浸入 / neat 带边子流形 | Ch4 / Ch1§3+Ch6 / Ch1§4 |
| 三分类 | 度+Euler（Poincaré-Hopf）/ Thom 配边 / Morse+CW 复形 | Ch5 / Ch7 / Ch6+Ch8-9 |

---

## §11 自测答案要点（供核对）

1. **§1** 抛物面 $z=x^2+y^2$：$g=z-x^2-y^2$，$Dg=(-2x,-2y,1)\neq0$ 处处，$\mathrm{rank}=1=k$，故 2 维子流形。neat 子流形 $[0,1]\times\{0\}\subset D^2$：$\partial N=\{(0,0),(1,0)\}=N\cap\partial D^2$ ✓（边界横截）。
2. **§2** Weierstrass 逼近是 $C^0$ 逼近的 $\mathbb{R}$ 特例；强拓扑下非紧 $M$ 也能一致逼近（弱拓扑仅紧致一致）。
3. **§3** $f(x,y)=x^2-y^2$ 与 $Z=\{0\}$：原点 $df=(0,0)$ 非横截；$Z=\{1\}$ 双曲线 $df\neq0$ 横截。multijet 横截保证自映射不同原像点行为独立。
4. **§4** $f=x^2+y^2$：$\mathrm{Crit}=\{(0,0)\}$，$f(\mathrm{Crit})=\{0\}$ 零测 ✓。Peano 曲线非 $C^1$，不满足 Sard 的 $C^r$ 假设。
5. **§5** $f(z)=z^3$：$\deg=3$（3 原像 $\times$ $+1$）。$S^2$：$\chi=2$ 毛球；$T^2$：$\chi=0$ 可无零点场。$e(TM)=\chi(M)$ 与 G&P $\chi=I(\Delta,\Delta)$ 一致（零截面自相交 $=$ 对角线自相交）。
6. **§6** $S^1\hookrightarrow\mathbb{R}^2$（$2n+1=3$，实际 2 够）；$T^2\hookrightarrow\mathbb{R}^3$。$2n+1$ 来自割线流形 $\dim\le2n$，Sard 保证好投影方向存在。
7. **§7** $\mathbb{RP}^2$ 不配边于 $\emptyset$（$w_1\neq0$）；$S^n$ 配边于 $\emptyset$（$D^{n+1}$ 边界）。Pontryagin-Thom：标架法丛 $\to$ Thom 空间映射，同构。
8. **§8** 环面 4 临界点指标 $0,1,1,2$，$c_0-c_1+c_2=0=\chi(T^2)$。$f=x^2-y^2$ Hessian $\mathrm{diag}(2,-2)$，负特征值 1 个 $\Rightarrow$ 指标 $=1$（鞍）。
9. **§9** Möbius 带转移函数 $-1$（扭转，非平凡）；$TS^2\oplus\nu\cong\mathbb{R}^3$（嵌入 $\mathbb{R}^3$ 诱导切+法 $=$ 平凡 3 丛）。

> **核对原则**：全书核心是「**逼近 $+$ Sard $\to$ 横截（generic）$\to$ 几何结构（嵌入/丛）$\to$ 不变量（度/Euler）$\to$ 分类（配边/Morse/曲面）**」。函数空间拓扑让 generic 严格化，Sard 保证正则值稠密，Thom 横截保证横截是 generic，三者合力推出 Whitney 嵌入/Thom 配边/Morse 不等式。

---

> **下一步**：沿 `01-track/stage-2` 精读 Hirsch **Ch2 函数空间 + Ch7 配边**（G&P/Milnor 无的核心块），遇横截/Pontryagin-Thom 查 `00-META/CONCEPT-INDEX`；Ch7 配边与 Bott-Tu 特征类交叉；Ch8 Morse 与 Milnor《Morse Theory》衔接。
>
> **stage-3 前瞻**：h-配边定理（Smale $\to$ 高维 Poincaré 猜想） $\to$ 特征类（Stiefel-Whitney/Chern/Pontryagin） $\to$ 指标定理（Atiyah-Singer） $\to$ Floer 同调（无穷维 Morse） $\to$ 辛拓扑/规范场论（Donaldson/Seiberg-Witten）。
>
> **一句话总结**：Hirsch 的全部精华在于——**用函数空间拓扑 + 逼近 + Sard + Thom 横截四大引擎，纯拓扑地（不用代数拓扑/微分形式）推出 Whitney 嵌入、Thom 配边、Morse 理论与曲面分类**。它是微分拓扑黄金时代的「公理化总成」，是 G&P/Milnor 的友好直觉过渡到研究级严格语言的桥梁。
>
> **实操验证**（建议用 Python/NumPy）：
> - §2：用 `scipy.optimize.approx_fprime` 数值验证光滑逼近（对 Weierstrass 函数加光滑扰动）
> - §4：采样验证 Sard——$f(x,y)=x^2+y^2$ 的临界值集 $\{0\}$ 零测
> - §5：$f(z)=z^k:S^1\to S^1$ 采样正则值原像，累加 $\mathrm{sign}(df)$ 验证 $\deg=k$
> - §8：`numpy.linalg.eigvalsh` 算 Hessian 负特征值个数 $=$ Morse 指标（环面高度函数 4 临界点）
> - §7：数值模拟 Pontryagin-Thom——$S^1\subset\mathbb{R}^2$ 的法丛标架 $\to$ 映射 $S^2\to S^1$（Hopf 度 $=$ 配边类）
> - §9：用 `numpy` 构造 Möbius 带转移函数 $g_{12}=-1$（扭转），与圆柱 $g_{12}=+1$ 对比，验证非平凡丛
