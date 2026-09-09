# Pugh《Real Mathematical Analysis》(UTM, 2nd Ed, 2015) · 快速逐章精读

> 原书:`Real Mathematical Analysis (Charles C. Pugh, UTM 系列, Springer, 2nd ed., 2015)` / 6 正章 + 附录
> 读于:2026-07-02 / stage-2 研究生基础 · 实分析直观严格双轨
> 本文为**快速逐章精读**,每章 1 个飞腾锚点 + 1 个关键定理 + 1 道自测题,用于建立全书骨架。

---

## §0 引言:Pugh 是什么,为什么读它

Charles C. Pugh 是 UC Berkeley 资深教授,本书是他多年 Math 104(实分析)课程的结晶,
收录于 Springer **UTM**(Undergraduate Texts in Mathematics)系列。它的核心气质可以用一句话概括
——**「Hardy《纯数学教程》的现代版」**:继承 Hardy(1908)以直觉引导、图示驱动、motivation
优先的教学传统,但用 21 世纪的严格语言重写。

### 四书对比表(Pugh / Rudin / Tao / Hardy)

| 维度 | **Pugh** UTM | **Rudin** PMA | **Tao** 分析引论 | **Hardy** 纯数学教程 |
|------|----------|-----------|-------------|-----------------|
| **风格** | 直观与严格并重,**图极多**(200+ 幅手绘),叙事流畅 | 紧凑抽象,定义-定理-证明三段式,几乎不解释动机 | 对话式引导,从朴素到严格,逐层搭建 | 经典英式散文,优雅但老派(1908 初版) |
| **实数构造** | 🟢 **Dedekind 分割亲手构造**(从 $\mathbb{Q}$ 造 $\mathbb{R}$) | LUB 公理(假设 $\mathbb{R}$ 存在) | 从 $\mathbb{Q}$ Cauchy 序列逐步构造 | Dedekind 分割 + Cauchy 序列 |
| **拓扑** | Ch2 度量空间,**图示驱动** | Ch2 基本拓扑(抽象、紧凑) | 分散嵌入各章 | 无独立拓扑章 |
| **函数空间** | Ch4 独立(图示极丰富) | Ch7(抽象紧凑) | 不含 | 不含 |
| **Lebesgue** | Ch6 独立(约 50 页,完整) | Ch11 预告(仅约 20 页) | 不含 | 不含(1908 年书) |
| **多元** | Ch5(Fréchet 导数 + 反/隐函数) | Ch9-10(含微分形式,更广) | 不含(仅 Vol I 单变量) | 不含 |
| **页数 / 定位** | ~480 页 / 本科高年级 + 研究生入门 | ~340 页 / 研究生标准 | 两卷 ~600 页 / 零基础渐进 | ~500 页 / 经典文学性 |
| **习题** | 多且**启发性**强(非纯计算) | 少而硬核(正文延伸) | 分级习题(易→难标注) | 经典难题 |
| **适合谁** | 要直觉**又要**严格;图示思维者 | 已有直觉、要研究级紧凑度 | 纯零基础补严格性 | 欣赏经典文笔与历史 |

**Pugh 的灵魂**:它与 Rudin PMA 形成**完美互补**。Rudin 像「冰山」——只露出精炼结论,
冰下的推导动机留给读者;Pugh 像「导游」——每一步都画图、解释「为什么这样定义」。
Pugh 的两大标志性特征:

1. **实数用 Dedekind 分割构造**(而非 Rudin 的公理假设),让学生亲眼看到 $\sqrt{2}$
   如何从 $\mathbb{Q}$ 的「缝隙」中被「补上」;
2. **函数空间(Ch4)与 Lebesgue(Ch6)独立成章**,分量远超 Rudin 的预告,
   接近研究生教材的深度。

代价:全书略「松散」,某些地方不如 Rudin 经济。但它的可读性是 Rudin 无法比拟的。

> **前置**:已读 Rudin PMA(stage-1)、Royden/Folland 实分析(stage-2)。
> 本文重在提炼 Pugh **区别于** Rudin 的独特视角与图示直觉,避免重复 Rudin 已覆盖的内容。

---

## §1 全书 6 章 + 附录骨架一览(飞腾锚点分布)

| 章 | 标题 | 核心概念 | 飞腾锚点 |
|:-:|------|---------|---------|
| 1 | Real Numbers(实数) | Dedekind 分割构造 $\mathbb{R}$ | **FP16 3.81×[Lab01]** |
| 2 | A Taste of Topology(拓扑初尝) | 度量空间、紧致、连通、完备 | **TLB 4.81×[E04]** |
| 3 | Functions of a Real Variable(一元实函数) | 极限/连续/微分/Riemann 积分/**FTC**/级数 | **UDOT 16.9×[E05]** |
| 4 | Function Spaces(函数空间) | 一致收敛/Arzelà-Ascoli/Stone-Weierstrass/压缩映射 | **Iron Law<2%[Lab00]** |
| 5 | Multivariable Calculus(多元微积分) | Fréchet 导数/反函数/隐函数定理/多重积分 | **GEMM 9.45G[Lab05]** |
| 6 | Lebesgue Theory(Lebesgue 理论) | 测度/Lebesgue 积分/MCT-Fatou-DCT/$L^p$ | **分支预测[Lab02]** |
| 附录 | Appendices(附录) | Lebesgue 其他途径/复指数/推荐阅读 | **Schmidt 正交化** |

> 锚点池 8 选 7,本章分散到不同硬件概念;未用的 **matmul 15×[V03]** 留给交叉引用。

---

### 第 1 章 · Real Numbers(实数)

- **核心**:本章是 Pugh 与 Rudin 的**最大分野**。Pugh 不假设 $\mathbb{R}$ 存在,
  而是用 **Dedekind 分割**(Dedekind cut)从 $\mathbb{Q}$ **亲手构造** $\mathbb{R}$。
  一个分割 $A|A^c$ 把 $\mathbb{Q}$ 切成两段(下段 $A$ 无最大元),每个分割就定义一个实数。
  例如 $\sqrt{2}$ 就是分割 $\{q\in\mathbb{Q}:q^2<2\text{ 或 } q<0\}$。
  Pugh 接着证明全体分割构成**完备有序域**——$\mathbb{Q}$ 的每个「缝隙」都被填上。
  这是 Rudin 绝对不会做的事(Rudin Ch1 直接用 LUB 公理假设 $\mathbb{R}$ 存在)。
- **飞腾锚点**:**FP16 3.81×[Lab01]** 🟢 —— Dedekind 分割的精神是「无洞」:
  $\mathbb{R}$ 的每个有界子集有最小上界。但 **FP16/FP32 是有限离散集,有缝隙**——
  FP16 仅 65536 个值,$\sup$ 可能落在两个 FP16 之间被截断。
  LUB 性质在浮点上**不成立**,这正是 FP16 加速 3.81× 的精度代价。
  Pugh 用 Dedekind 分割让你「看见」这个缝隙被填上,而 Rudin 只公理地假设它不存在。
- **关键定理**:
  - **Theorem(分割构成完备有序域)**:全体 Dedekind 分割在自然序
    $A<B \Leftrightarrow A\subsetneq B$ 和加法 $A+B=\{a+b:a\in A,b\in B\}$ 下
    构成完备有序域,$\mathbb{Q}$ 以 $q\mapsto\{x\in\mathbb{Q}:x<q\}$ 嵌入稠密。
  - **Archimedes 性质**:$\forall x>0,\exists n\in\mathbb{N},\,nx>1$。
  - **稠密性**:$\mathbb{Q}$ 在 $\mathbb{R}$ 中稠密。
- **自测**:写出 $\sqrt{2}$ 对应的 Dedekind 分割(注意负数部分)。
  为什么 $\mathbb{Q}$ 本身不满足 LUB?(与 Rudin PMA Ch1 / Spivak Ch29 如何呼应?)
  Dedekind 分割与 Tao 的 Cauchy 序列构造有什么本质区别?(提示:一个是「切」,一个是「逼近」)

---

### 第 2 章 · A Taste of Topology(拓扑初尝)

- **核心**:从 $\mathbb{R}$ 的具体距离 $d(x,y)=|x-y|$ 出发,**抽象到一般度量空间** $(X,d)$。
  Pugh 用大量图示讲解开集(含球邻域 $B_r(p)$)、闭集、内点、边界、聚点。
  核心概念是**紧致性**——Pugh 同时给两个定义:
  - **序列紧**(每个序列有收敛子列)
  - **开覆盖紧**(任意开覆盖有有限子覆盖)
  并证明度量空间中二者等价。**Heine-Borel**($\mathbb{R}^n$ 中紧致 ⟺ 有界闭)。
  连通性(不能分成两个非空分离的开集)与完备度量空间(Baire 纲预告)。
- **飞腾锚点**:**TLB 4.81×[E04]** 🟡 —— 度量空间的本质是「**距离 = 局部信息**」:
  收敛、连续只依赖邻域(局部),而非全局结构。这与 **TLB** 的精神同构——
  虚拟地址到物理地址的映射只需查「局部页表项」,TLB 4.81× 加速来自局部性命中。
  Pugh 的度量空间让你用「球邻域」思考一切,正如 TLB 让 CPU 只用局部缓存思考寻址。
  🟡 此为类比仅供直觉;度量空间的局部性与 TLB 的缓存局部性是不同层次的「局部」。
- **关键定理**:
  - **Heine-Borel 定理**:$\mathbb{R}^n$ 中子集 $K$ 紧致 ⟺ $K$ 闭且有界。
  - **Bolzano-Weierstrass**:$\mathbb{R}^n$ 中有界序列必有收敛子列。
  - **定理**:紧致度量空间上连续函数**一致连续**(Pugh 的图示证明比 Rudin 更直观)。
  - **Cantor 交集定理**:紧致集的嵌套非空闭子集序列,交集非空(完备性的拓扑化身)。
- **自测**:用开覆盖定义证明 $[0,1]$ 紧致而 $(0,1)$ 不紧致。
  度量空间中「序列紧 ⟺ 开覆盖紧」的证明关键步骤是什么?(提示:全有界 + 完备)
  Cantor 集是闭、不可数、但「很小」——它如何预示第 6 章的零测集概念?

---

### 第 3 章 · Functions of a Real Variable(一元实函数)

- **核心**:全书**最大最重的一章**(约 150 页),几乎是一部微型单变量分析。
  覆盖:极限($\varepsilon$-$\delta$)、连续(开集原像刻画)、
  微分(**中值定理 MVT**、Taylor 展开)、**Riemann 积分**(Darboux 上下和路线)、
  **微积分基本定理 FTC**、级数收敛判别法。
  Pugh 的特色是**每个定理配图示**:FTC 用「面积变化率」图直观解释积分与微分互逆,
  比 Rudin 纯代数推导更易吸收。Riemann 可积判据(间断点集「零测」)是 Ch6 Lebesgue 的伏笔。
- **飞腾锚点**:**UDOT 16.9×[E05]** 🟢 —— Riemann 和 $S=\sum_{i} f(t_i)\Delta x_i$
  本质是**加权的向量点积**(内积)。离散化积分 = 计算 $\sum w_i f_i$ = 一次点积。
  飞腾 **UDOT(无符号点积)** 指令把这种加权累加加速 16.9×——
  **积分的离散化就是点积,UDOT/GEMM 是积分的硬件化身**。
  数值积分(梯形/Simpson)和神经网络前向传播都是 Riemann 和的变体。
- **关键定理**:
  - **FTC(微积分基本定理)**:若 $f$ 在 $[a,b]$ 连续,$F(x)=\int_a^x f(t)\,dt$,则 $F'=f$;
    若 $f=F'$ 则 $\int_a^b f=F(b)-F(a)$。积分与微分互逆。
  - **Riemann 可积判据**:$f$ 在 $[a,b]$ Riemann 可积 ⟺ $f$ 有界且间断点集可被
    任意小总长的区间覆盖(Pugh 的朴素零测概念,Ch6 升级为 Lebesgue 零测)。
  - **中值定理 MVT**:$\exists c\in(a,b),\,f'(c)=\frac{f(b)-f(a)}{b-a}$。
  - **Taylor 定理**:带 Lagrange 余项的 Taylor 展开。
- **自测**:Thomae 函数($x=p/q$ 取 $1/q$、无理点取 0)在哪里连续?
  为什么它 Riemann 可积而 Dirichlet 函数($\chi_\mathbb{Q}$)不可积?
  用可积判据解释。Pugh 的 FTC 图示如何解释 $(\int_a^x f)'=f$?(提示:面积随上限的瞬时变化率)

---

### 第 4 章 · Function Spaces(函数空间)

- **核心**:把「函数」视为空间中的「点」,研究**函数序列的收敛**。
  核心概念是**一致收敛**(uniform convergence,$\sup_x|f_n-f|\to 0$)取代逐点收敛
  ——只有一致收敛才保证极限与连续/积分/求导可交换。
  引入**等度连续**(equicontinuity)与 **Arzelà-Ascoli 定理**。
  **Stone-Weierstrass**(连续函数可用多项式一致逼近)。
  **压缩映射原理** + **Picard 迭代**证 ODE 存在唯一性。
  Pugh 用动画式图示展示 $f_n\rightrightarrows f$ 的过程,远比 Rudin 抽象的 $\varepsilon$-$N$ 定义直观。
- **飞腾锚点**:**Iron Law<2%[Lab00]** 🟡 —— 一致收敛 = 逼近误差「**全局一致可控**」:
  $\exists N,\forall n>N,\forall x,\,|f_n(x)-f(x)|<\varepsilon$。
  这与 **Iron Law 误差<2%** 同构——在最坏点误差也被压进预算。
  逐点收敛不保证连续性($f_n=x^n$ 在 $[0,1]$ 极限不连续),
  对应「训练 loss 收敛 ≠ 模型行为稳定」。
  Stone-Weierstrass 是**万能逼近定理**鼻祖,MLP 通用近似的合法性源于此。
  压缩映射 Picard 迭代 = 数值求解器收敛保证。
- **关键定理**:
  - **Arzelà-Ascoli 定理**:$C(K)$ 中函数族有一致收敛子列
    ⟺ 等度连续 + 逐点有界($K$ 紧致)。这是泛函分析的入口。
  - **Stone-Weierstrass**:多项式(或更一般的分离点子代数)在 $C(K,\mathbb{R})$ 中一致稠密。
  - **压缩映射原理**:完备空间上 $d(Tx,Ty)\le c\cdot d(x,y),\,c<1$
    ⟹ 唯一不动点 ⟹ **Picard ODE 存在唯一**:$y'=f(x,y),y(x_0)=y_0$ 局部唯一解。
- **自测**:举一个逐点收敛但**不**一致收敛的函数列,说明极限为何「丢了连续性」。
  Arzelà-Ascoli 中「等度连续」为什么不能省?(提示:去掉后构造无紧子列的反例)
  压缩映射原理如何保证 Picard 迭代 $y_{n+1}=y_0+\int_{x_0}^x f(t,y_n)\,dt$ 收敛?

---

### 第 5 章 · Multivariable Calculus(多元微积分)

- **核心**:把单变量微积分推广到 $\mathbb{R}^n$。核心是 **Fréchet 全导数**
  ——$f$ 在 $a$ 处可微意味着 $f(a+h)=f(a)+df_a(h)+o(\|h\|)$,
  其中 $df_a$ 是**线性映射**(雅可比矩阵)。
  **链式法则** = 线性映射复合 = 矩阵乘。
  两大支柱:**反函数定理**(Jacobian 可逆 ⟹ 局部微分同胚)
  与**隐函数定理**(解方程 $F(x,y)=0$)。
  多重 Riemann 积分 + **Fubini**(累次积分换序)。
  Pugh 用体积变形图直观解释「Jacobian 行列式 = 体积变换系数」,比 Rudin 更具象。
- **飞腾锚点**:**GEMM 9.45G[Lab05]** 🟢 —— 多元微积分的核心运算全是**雅可比矩阵**:
  链式法则 = 矩阵乘,反函数 = 矩阵求逆,Jacobian 行列式 = 体积变换系数。
  整个多元微分的算力开销集中在 **GEMM(矩阵乘)**。
  飞腾 GEMM 9.45 GFLOPS 直接决定神经网络反向传播(Jacobian-向量积)、
  Newton 法($J^{-1}F$)、Kalman 滤波的吞吐。
  隐函数定理 = 「非线性方程在非退化点处可局部线性化」,是所有迭代求解器的合法性根基。
- **关键定理**:
  - **反函数定理**:若 $df_a$ 可逆($\det J(a)\ne0$),则 $f$ 在 $a$ 局部微分同胚
    (局部有光滑逆)。
  - **隐函数定理**:若 $F(a,b)=0$ 且 $\partial F/\partial y$ 在 $(a,b)$ 可逆,
    则局部存在 $y=g(x)$ 使 $F(x,g(x))=0$,且 $g$ 光滑。
  - **链式法则**:$d(g\circ f)_a=dg_{f(a)}\circ df_a$(线性映射的复合)。
  - **Fubini 定理**:多重积分可化为累次积分 $\int\int f\,dA=\int[\int f\,dy]\,dx$。
- **自测**:用隐函数定理说明为什么 $F(x,y)=0$ 在 $\partial F/\partial y\ne0$ 处可局部解出 $y=g(x)$。
  Newton 迭代 $x_{n+1}=x_n-[J(x_n)]^{-1}F(x_n)$ 如何依赖反函数定理?
  Jacobian 行列式 $|\det J|$ 在换元积分中起什么作用?(提示:体积变换系数)

---

### 第 6 章 · Lebesgue Theory(Lebesgue 理论)

- **核心**:Pugh 的 Lebesgue 理论独立成章(约 50 页),
  **远比 Rudin PMA Ch11 的 20 页预告完整**,接近研究生教材深度。
  从**外测度** $m^*(A)=\inf\sum|I_k|$(用区间覆盖取下确界)出发,
  Carathéodory 准则筛出可测集,建立 **Lebesgue 测度**的可数可加性。
  可测函数 → 用**简单函数**逼近 → 定义 **Lebesgue 积分**。
  三大收敛定理(**MCT 单调收敛、Fatou 引理、DCT 控制收敛**)让「极限穿过积分号」合法。
  $L^p$ 空间 + **Riesz-Fischer 完备性**。Lebesgue 版 FTC(绝对连续函数)。
- **飞腾锚点**:**分支预测[Lab02]** 🟡 —— Lebesgue 可测函数 = 「**结构可预测**」的函数:
  它几乎处处连续、对极限运算封闭。这如同 **CPU 分支预测器**——
  处理器靠「可预测性」获利(预取、流水线不停顿),
  Lebesgue 理论靠「可测性」保证积分存在与极限交换。
  **DCT(控制收敛定理)**:若 $|f_n|\le g$($g$ 可积)且 $f_n\to f$ a.e.,
  则 $\int f_n\to\int f$——「控制函数」= 全局误差预算,
  是概率论(期望收敛)与 ML(经验风险→期望风险)的核心工具。
  Cantor 集不可数却测度 0,颠覆「闭集必有一定大小」的直觉。
- **关键定理**:
  - **DCT(控制收敛定理)**:$f_n\to f$ a.e.,$|f_n|\le g\in L^1$
    ⟹ $\int f_n\to\int f$。全书最后的「大招」。
  - **MCT(单调收敛)** + **Fatou 引理**:三者互相等价地刻画「极限与积分可交换」。
  - **Riesz-Fischer 定理**:$L^p$ 在 $1\le p\le\infty$ 下完备(Cauchy 列 ⟹ 收敛)。
  - **Lebesgue FTC**:$F$ 绝对连续 ⟺ $F'=f$ a.e. 且 $F(x)-F(a)=\int_a^x f$。
    Cantor-Lebesgue 函数连续但**不**绝对连续(FTC 失败),是经典反例。
- **自测**:为什么 $\int_0^1\mathbb{1}_\mathbb{Q}\,dx$(Dirichlet)Riemann 不可积但 Lebesgue $=0$?
  DCT 的「控制函数 $g$」为什么不能省?(构造 $f_n=n\chi_{(0,1/n)}$)
  Cantor-Lebesgue 函数 $F'=0$ a.e. 但 $F$ 不恒常数——为何不违反 FTC?(答:$F$ 不绝对连续)

---

### 附录 · Appendices(附录与补充)

- **核心**:Pugh 的附录是「给学生指路」式的导师建议。
  - **附录 A**:Lebesgue 积分的**其他构造途径**(如 Daniell 积分——从泛函而非测度出发),
    拓宽视野,说明「测度论不是唯一通往积分的路」。
  - **附录 B**:**复指数 $e^{ix}$ 的严格定义**(用幂级数而非几何),
    Euler 公式 $e^{ix}=\cos x+i\sin x$ 的分析基础。
  - **推荐阅读**:Pugh 亲自点评 Rudin、Royden、Hardy 等经典,
    给出「读完本书后该往哪走」的路线图——这种导师式建议是 UTM 教材的人情味。
- **飞腾锚点**:**Schmidt 正交化** 🟡 —— 复指数 $e^{ix}$ 的幂级数定义 $\sum(ix)^n/n!$
  把「旋转」分解为正交分量($\cos$ 与 $\sin$)。这如同 **Gram-Schmidt 正交化**——
  把一个方向投影到正交基,分离出「实部」与「虚部」两个正交分量。
  Fourier 分析(把函数分解为 $e^{inx}$ 正交基)正是这种正交分解的推广,
  也是调和分析(stage-2 已读 Folland Ch10)的起点。
- **关键定理**:
  - **Euler 公式** $e^{ix}=\cos x+i\sin x$(用幂级数定义 $e^z=\sum z^n/n!$ 证明,
    三角函数也由幂级数定义,避免循环论证)。
  - **De Moivre 定理** $(e^{ix})^n=e^{inx}$。
- **自测**:用幂级数(而非几何)证明 $e^{i\pi}+1=0$。
  Pugh 为什么要「重新定义」三角函数?
  (答:避免循环论证——几何定义依赖弧长,弧长依赖积分,积分依赖连续性理论)

---

## §9 全书逻辑主线:度量 → 一元 → 函数空间 → 多元 → Lebesgue

```
第1章 Dedekind 分割构造 ℝ(完备有序域)─────────┐
    │  「从 ℚ 的缝隙里造出 ℝ」(vs Rudin 公理假设)│
    │                                           │
    ├─→ 第2章 度量空间拓扑(紧致 = 完备的几何化身)│
    │       │  「距离 = 局部信息」(TLB 局部性)   │
    │       │                                   │
    │       └─→ 第3章 一元实函数(极限/连续/微分)│
    │            │  Riemann 积分 + FTC           │
    │            │  「积分 = 加权点积」(UDOT)    │
    │            │                              │
    │            └─→ 第4章 函数空间              │
    │                 │  一致收敛 / Arzelà-Ascoli│
    │                 │  Stone-Weierstrass      │
    │                 │  压缩映射 → Picard ODE   │
    │                 │  「误差全局可控」(Iron)  │
    │                 │                         │
    │                 ├─→ 第5章 多元微积分       │
    │                 │    Fréchet 导数          │
    │                 │    反/隐函数定理         │
    │                 │    「雅可比 = GEMM」      │
    │                 │                         │
    │                 └─→ 第6章 Lebesgue 理论 ⭐高潮
    │                      外测度 → 可测函数     │
    │                      MCT/Fatou/DCT         │
    │                      Lp 完备(Riesz-Fischer)│
    │                      「可测 = 可预测」      │
    │                                              
    └─→ 附录:复指数(正交分解)/ Daniell 积分 / 推荐阅读
```

> **通关标志**:你能用一句话串联全书——
> **「Dedekind 分割填满 ℚ 的缝隙得到完备 ℝ;度量空间把完备性几何化为紧致;
> 一元微积分建立 FTC;函数空间把收敛升级为一致收敛;多元用 Fréchet 导数把微积分线性化;
> Lebesgue 把积分扩张到最一般的可测函数,用 DCT 解锁极限交换。」**

---

## §10 与本仓库其他笔记的交叉引用

- **Rudin PMA**(stage-1):Pugh 与 Rudin **完美互补**。
  Rudin 公理假设 $\mathbb{R}$(Ch1 LUB),Pugh Dedekind 构造 $\mathbb{R}$(Ch1);
  Rudin Ch11 仅 Lebesgue 预告,Pugh Ch6 独立完整。
  **建议**:先 Rudin 建骨架,卡住时翻 Pugh 补图示直觉。
- **Royden 全 20 章**(stage-2):Pugh Ch6 的 Lebesgue 理论 ≈ Royden Part I(Ch2-8)的浓缩版。
  读 Pugh Ch6 后直接进 Royden 深化(符号测度、Radon-Nikodym、Fubini)。
  Pugh 的 DCT 对应 Royden Ch4 DCT,Pugh 的 $L^p$ 对应 Royden Ch7-8。
- **Folland 实分析**(stage-2):Pugh 的度量空间(Ch2)是 Folland Ch6(Topology)的直觉前奏;
  Pugh 的函数空间(Ch4)预演 Folland Ch7-8(Banach/Hilbert)。
  Stone-Weierstrass 在两者都出现,Folland 更抽象。matmul 15×[V03] 锚点在 Folland Ch10
  (Fourier 高维)中复用,Pugh 附录的复指数是其种子。
- **Spivak Calculus**(stage-1):Pugh Ch1 的 Dedekind 分割 ≈ Spivak Ch29(实数构造);
  Pugh Ch3 的 FTC ≈ Spivak 全书核心。Spivak 给单变量极致直觉,Pugh 给一般框架 + 函数空间。
- **Tao 分析引论**:Tao 从 $\mathbb{Q}$ 的 Cauchy 序列构造 $\mathbb{R}$
  (与 Pugh 的 Dedekind 分割是**等价但不同的构造**);Tao 不含函数空间和 Lebesgue,Pugh 补齐了这两块。
- **Hardy 纯数学教程**:Pugh 自称继承 Hardy 传统——图示、motivation、叙事流畅。
  读 Pugh 可视为「现代化重读 Hardy」。
- **00-META/CONCEPT-INDEX**:查「极限/连续/积分/收敛/紧致」等概念时,跑三维交叉
  ——Pugh = 图示直觉轴,Rudin = 严格抽象轴,飞腾 = 工程锚点轴。

---

> 📌 **本笔记定位**:快速逐章骨架,非精读手册。
> Pugh 的核心价值是**图示直觉 + Dedekind 构造 + 独立的函数空间/Lebesgue 章**
> ——当 Rudin 太干时,Pugh 是最好的「解药」。
> 需深读某章时,在同目录建 `pugh_chXX_精读笔记.md`(参照 `NOTES_TEMPLATE.md` 八重视角)。
> 飞腾锚点实验细节见 `10-personal/` 下飞腾实验档案。
