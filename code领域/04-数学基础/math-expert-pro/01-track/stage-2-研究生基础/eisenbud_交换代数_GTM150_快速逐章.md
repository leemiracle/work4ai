# Eisenbud《交换代数:代数几何观点》(GTM150) · 快速逐章精读

> 基于原书:Commutative Algebra with a View Toward Algebraic Geometry, GTM150 (David Eisenbud, 1995)
> 读于:2026-07-02 / stage-2 研究生基础 · 交换代数主线
> 定位:**现代交换代数权威**,几何动机驱动,计算导向,Atiyah-MacDonald 的扩充与现代化。
> 本文为**快速逐章精读**,每主题 1 个飞腾锚点 + 1 个关键定理 + 1-2 道自测题,按 6 大部分约 20 主题归并。

---

## §0 引言:Eisenbud 是什么,为什么读它

David Eisenbud 的《Commutative Algebra with a View Toward Algebraic Geometry》
(GTM150, Springer, 1995)是**现代交换代数的权威教材**。
副标题「with a View Toward Algebraic Geometry」点明全书灵魂:
**每个代数概念都从几何动机出发**——环 $R$ 是几何对象的函数环,理想 $I$ 是方程组,
素理想 $\mathfrak p\in\mathrm{Spec}\,R$ 是几何上的「点」,局部化 $R_{\mathfrak p}$ 是「放大镜看点附近」。
本仓库已精读 Atiyah-MacDonald(AM,128 页极简经典)与 Hartshorne(代数几何圣经)。
Eisenbud 恰是 **AM 的扩充与现代化**:把 AM 浓缩的 11 章铺展成几何动机驱动的全谱系,
补足 AM 略去的 **Gröbner 基、Hilbert 函数、CM/Gorenstein 环、平坦性的计算面**,
例子密度与算法导向远超 AM。读 Eisenbud 后,Hartshorne 第 I-II 章所需的交换代数弹药
(正则序列、深度、维数定理、完备化)一次配齐。三大特色:① 几何动机全程贯穿;
② 计算导向(Gröbner/结式/Hilbert 函数占独立大章);③ 现代同调视角(Tor/Ext/深度/CM/Gorenstein 一气呵成)。

| 书 | 风格 | 几何动机处理 | 适合谁 |
|---|---|---|---|
| **Eisenbud GTM150** | 计算导向·例极丰富·算法味浓 | 全书副标题级贯穿 ⭐ | 读 AM 后求扩充·计算代数几何方向者 |
| **Atiyah-MacDonald** | 精炼极简·密度极高·习题为核心 | 埋种子于习题·不展开 | 速成交换代数骨架·首次系统学 |
| **Matsumura《交换环论》** | 全面标准参考·定义定理为主 | 弱·偏纯代数 | 查阅标准结果·研究生案头工具书 |
| **Bourbaki《交换代数》** | 形式化·包罗万象·极度抽象 | 中·结构化呈现 | 追求绝对严格·系统构建基础者 |

> 🟢 事实可作锚点:Hilbert 基定理、Nakayama 引理、维数定理、Gröbner 基停机性都是严格定理。
> 🟡 类比(环=几何对象、局部化=放大镜)仅供直觉,**绝不在严格证明中引用**。

---

## §1 全书骨架(6 部分约 20 主题,飞腾锚点分布)

| 部分 | 核心主题 | 主力飞腾锚点 |
|---|---|---|
| **第1部分 根基** | 多项式环/Noether环/局部化/准素分解/I-adic完备化 | Iron Law<2%[Lab00] + TLB 4.81×[E04] ⭐⭐ |
| **第2部分 模与线性代数** | 模/Cayley-Hamilton/Nakayama/平坦性/Tor与Ext | matmul 15×[V03] ⭐ |
| **第3部分 维度理论** | Krull维数/Noether正规化/零点定理/正则环/深度 | FP16 3.81×[L01] |
| **第4部分 几何工具** | Gröbner基/消元/结式/Hilbert函数 | GEMM 9.45G[Lab05] + UDOT 16.9×[E05] |
| **第5部分 专题** | Cohen-Macaulay/Gorenstein/完全交/相交重数 | Schmidt 正交化 |
| **第6部分 退化族与同调** | 形变/导出范畴预告/上同调维数 | 分支预测[Lab02] |

---

# 第 1 部分 · 根基 (Roots)

### 第 1 主题 · 多项式环与消元思想

- **核心**:Eisenbud 开篇从几何动机讲代数。多项式环 $k[x_1,\dots,x_n]$ 是代数几何原型环,
  理想 $I$ 对应零点集 $V(I)$,方程组「几何化」为代数簇。「多解一个方程就少一个自由度」的
  **消元直觉**贯穿全书——这是维数论的几何源头,也是第 4 部分 Gröbner 基的伏笔。
  全书基本词典:环↔几何对象,理想↔方程组,素理想↔不可约子簇的点。
- **飞腾锚点**:**FP16 3.81×[L01]** —— 变元个数 $n$ = 自由度 = 几何维度的上界,
  如同浮点有效位数是精度上界。🟢$V(I)$ 与 $I(V)$ 的对应是严格代数几何(事实锚点);3.81× 仅为精度类比。
- **关键定理**:**理想的零点对应**。$V(I)=\{x\in\mathbb A^n:f(x)=0,\ \forall f\in I\}$;
  $V(I)\subseteq V(J)\iff\sqrt{J}\subseteq\sqrt{I}$,理想包含反向对应几何包含。
- **自测**:在 $\mathbb A^2$ 上,$V(x,y)$ 是什么?(点 $(0,0)$);
  $V(x)\cap V(y)$ 用理想如何表示?(对应 $V(x)+(y)=V(x,y)$。)

---

### 第 2 主题 · Noether 环与 Hilbert 基定理 ⭐

- **核心**:确立「Noether 条件 = 有限性」纲领。Noether 环三等价:每理想有限生成 /
  理想升链终止 / 非空理想集有极大元。**Hilbert 基定理**把有限性传播到 $k[x_1,\dots,x_n]$,
  奠定计算代数几何根基:每个理想由有限多项式生成,故 Gröbner 基算法有有限输出。
  Eisenbud 强调有限性是代数几何能「真算」的前提(无穷变元环 $k[x_1,x_2,\dots]$ 即反例)。
- **飞腾锚点**:**Iron Law<2%[Lab00]** —— 理想升链 $I_1\subseteq I_2\subseteq\cdots$ 必终止,
  如同要求零误差:<2% 容差都不允许,链必须「撞墙停下」。
  🟢升链终止是严格定理(事实锚点);<2% 仅为有限性类比。
- **关键定理**:**Hilbert 基定理**。$R$ Noether $\Rightarrow$ $R[x]$ Noether;
  迭代得 $k[x_1,\dots,x_n]$ Noether,故每个理想由有限多个多项式生成——Gröbner 基因此有限输出。
- **自测**:用三等价定义证 $\mathbb Z$ 是 Noether(每理想 $n\mathbb Z$ 主理想);
  非例 $k[x_1,x_2,\dots]$,理想 $(x_1,x_2,\dots)$ 非有限生成,升链不终止。

---

### 第 3 主题 · 局部化与素谱 $\mathrm{Spec}\,R$ ⭐⭐

- **核心**:对乘法闭集 $S$ 构造分式环 $S^{-1}R=\{r/s\}$(从 $\mathbb Z$ 造 $\mathbb Q$ 是原型);
  最重要的是在素理想 $\mathfrak p$ 处局部化 $R_{\mathfrak p}$(取 $S=R\setminus\mathfrak p$),
  得唯一极大理想 $\mathfrak pR_{\mathfrak p}$ 的局部环——「只看点附近」。
  **素谱** $\mathrm{Spec}\,R$ 配 Zariski 拓扑(闭集 $V(I)$)成几何空间,是概形理论地基。
  局部化是正合函子,「性质在所有 $R_{\mathfrak p}$ 成立 $\iff$ 全局成立」(局部性质原则)。
- **飞腾锚点**:**TLB 4.81×[E04]** ⭐⭐ —— 局部化 $R_{\mathfrak p}$ 如同查表:
  给定点 $\mathfrak p$(虚拟地址),快速返回该点局部信息(物理页),无需遍历全局。
  🟢局部化正合、局部性质原则是严格定理(事实锚点);TLB 仅为快速查询类比。
- **关键定理**:**局部性质原则**。性质 $P$ 对 $R$-模/理想成立 $\iff$ 对所有 $R_{\mathfrak p}$ 成立;
  许多全局证明被「化归到局部环」逐点验证再拼回。
- **自测**:$S=\mathbb Z\setminus(p)$ 时 $S^{-1}\mathbb Z=\mathbb Z_{(p)}$,验证其唯一极大理想为 $p\mathbb Z_{(p)}$;
  再问 $\mathrm{Spec}\,\mathbb Z$ 是什么?(闭点 $\{(p)\}$ 加 Generic 点 $\{(0)\}$,后者闭包是全空间。)

---

### 第 4 主题 · 相伴素与准素分解

- **核心**:把「素理想=不可约」推广为「准素理想=准不可约」($R/\mathfrak q$ 中零因子皆幂零)。
  Noether 环中每个理想有准素分解 $\mathfrak a=\bigcap\mathfrak q_i$(Lasker-Noether 定理),
  是唯一分解在理想层面的类比。Eisenbud 引入**相伴素**
  $\mathrm{Ass}(M)=\{\mathfrak p:\mathfrak p=\mathrm{ann}(m),\ 0\neq m\in M\}$——
  「能成为某元素零化子」的素理想,精确刻画零因子结构,是准素分解的内在骨架。
- **飞腾锚点**:**GEMM 9.45G[Lab05]** —— 准素分解把理想拆成「主成分」,
  计算需反复做理想运算(交、根、商),如同 GEMM 批量矩阵吞吐。
  🟢相伴素与唯一性定理是严格结论(事实锚点);9.45G 仅为吞吐类比。
- **关键定理**:**第一/第二唯一性定理**。准素分解 $\mathfrak a=\bigcap_{i=1}^n\mathfrak q_i$ 中,
  根 $\sqrt{\mathfrak q_i}$ 集合(极小相伴素)由 $\mathfrak a$ 唯一确定,与分解选取无关;
  无嵌入素时各准素分量亦唯一。
- **自测**:在 $\mathbb Z$ 中 $(12)=(4)\cap(3)$ 是准素分解;
  验证 $(4)$ 是 $(2)$-准素(根为 $(2)$,商 $\mathbb Z/4\mathbb Z$ 中零因子 $2$ 幂零)。

---

### 第 5 主题 · 滤过、分次环与 $I$-adic 完备化

- **核心**:给环装上 $I$-adic 拓扑(基本邻域为 $I^n$),做完备化 $\hat R=\varprojlim R/I^n$
  (逆向极限),统一了 $p$-adic 数 $\mathbb Z_p$ 与形式幂级数 $k[[x]]$。
  引入**分次环** $\mathrm{gr}_I R=\bigoplus I^n/I^{n+1}$,它是研究切空间 $\mathfrak m/\mathfrak m^2$
  与维数(Hilbert-Samuel 多项式)的代数工具。**Krull 交定理**刻画「无穷小元素」何时不存在。
- **飞腾锚点**:**Iron Law<2%[Lab00]** —— 完备化 $\hat R=\varprojlim R/I^n$ 逐层逼近,
  每层 $R/I^n$ 是「前 $n$ 位精度」近似,误差严格随 $n\to\infty$ 趋零,不容近似。
  🟢Krull 交定理是严格定理(事实锚点)。
- **关键定理**:**Krull 交定理**。Noether 环 $R$、理想 $I$,则
  $\bigcap_n I^n=\{x:(1-a)x=0,\ \exists a\in I\}$;局部环中此交集为零(「无穷小元素不存在」)。
- **自测**:$\mathbb Z$ 在 $(p)$-adic 拓扑下完备化得 $\mathbb Z_p=\varprojlim\mathbb Z/p^n\mathbb Z$;
  写出前两层(模 $p$ 与模 $p^2$)的相容条件,理解「同余系逐层相容」。

---

# 第 2 部分 · 模与线性代数 (Modules)

### 第 6 主题 · 模、正合序列与张量积

- **核心**:把向量空间推广到环上——**模**(理想是模的特例)。
  核心工具是**正合序列** $0\to M'\to M\to M''\to 0$($\ker=\mathrm{im}$)与
  **张量积** $M\otimes_R N$(双线性映射的通用对象);张量积右正合但一般**不左正合**,
  这一「缺陷」直接催生平坦模(第 8 主题)与 Tor(第 9 主题)。Eisenbud 在此铺好后续同调工具语言。
- **飞腾锚点**:**matmul 15×[V03]** ⭐ —— 自由模 $R^n$ 的自同态环 = 矩阵环 $M_n(R)$,
  模同态 $\leftrightarrow$ 矩阵,张量积是双线性的线性化。
  🟢模同态↔矩阵是严格等价(事实锚点);15× 为加速类比。
- **关键定理**:**张量积的泛性质 + 右正合性**。双线性映射 $M\times N\to L$ 一一对应于
  线性映射 $M\otimes N\to L$;正合 $M'\to M\to M''\to0$ $\Rightarrow$ $-\otimes N$ 后仍右正合。
- **自测**:为何 $\mathbb Z/2\otimes_{\mathbb Z}\mathbb Z/3=0$?
  (提示:$1=3-2$,用双线性 $1\otimes1=1\otimes3-2\otimes1=0-0=0$。)

---

### 第 7 主题 · Cayley-Hamilton 与 Nakayama 引理 ⭐

- **核心**:**Cayley-Hamilton 定理**把「矩阵满足自身特征多项式」推广到环上模:
  $M$ 有限生成、自同态 $\varphi$ 满足 $\varphi(M)\subseteq IM$,则 $\varphi$ 满足以 $I$ 为系数的首一多项式。
  这直接推得 **Nakayama 引理**——局部环上「生成即非零」判据:$(R,\mathfrak m)$ 局部环,$M$ 有限生成,
  若 $M=\mathfrak m M$ 则 $M=0$;等价地「模掉极大理想检验生成元」(局部推理的瑞士军刀)。
- **飞腾锚点**:**matmul 15×[V03]** —— Cayley-Hamilton 本质是「矩阵被自身特征多项式零化」,
  $\det(\lambda I-A)$ 是特征值之积,与矩阵乘法同源。🟢Nakayama 引理是严格定理(事实锚点)。
- **关键定理**:**Nakayama 引理**。$(R,\mathfrak m)$ 局部环,$M$ 有限生成。
  若 $M=\mathfrak m M$,则 $M=0$;等价:若 $m_1,\dots,m_n$ 的像在 $M/\mathfrak m M$ 上生成,则在 $M$ 上生成。
- **自测**:用 Nakayama 证:局部环 $(R,\mathfrak m)$ 中,若 $\mathfrak m$ 由一个元素生成,
  则 $\dim_k\mathfrak m/\mathfrak m^2=1$(一维正则局部环,DVR 雏形)。

---

### 第 8 主题 · 平坦性 (Flatness)

- **核心**:**平坦模** = 保持张量积正合性的模($0\to M'\to M$ 正合 $\Rightarrow$
  $0\to M'\otimes N\to M\otimes N$ 正合)。平坦性是「连续族」的代数化身:
  平坦族中纤维「连续变化无跳变」,Hilbert 多项式沿纤维常值。
  局部化恒平坦,域上向量空间恒平坦,而 $\mathbb Z/n\mathbb Z$ 不平坦。
  这是 AM 着墨较少、Eisenbud 重点展开的现代枢纽。
- **飞腾锚点**:**TLB 4.81×[E04]** —— 平坦模如「无副作用查询」:
  张量后保持正合(信息无损),如同 TLB 命中不改变地址语义。
  🟢局部判据与忠实平坦判据是严格定理(事实锚点);TLB 为类比。
- **关键定理**:**平坦性的局部判据**。有限生成模 $M$ 在 Noether 局部环 $(R,\mathfrak m)$ 上
  平坦 $\iff$ $\mathrm{Tor}_1^R(R/\mathfrak m,M)=0$;把「全部正合」压缩到「检验一个 Tor」。
- **自测**:$\mathbb Z/n\mathbb Z$ 作为 $\mathbb Z$-模平坦吗?
  (不平坦:$0\to\mathbb Z\xrightarrow{\times n}\mathbb Z$ 张量 $\mathbb Z/n$ 后失正合,得 $\mathrm{Tor}_1\neq0$。)

---

### 第 9 主题 · Tor 与 Ext(同调工具)

- **核心**:$\mathrm{Tor}$ 补张量积的左正合失效,$\mathrm{Ext}$ 补 $\mathrm{Hom}$ 的左正合失效,
  均由「取自由分解→应用函子→取同调」构造。$\mathrm{Tor}_1^R(R/I,M)$ 度量 $M$ 沿 $I$ 的「挠」,
  $\mathrm{Ext}^1(M,N)$ 分类模的扩张。Eisenbud 把它们做成维数与深度的计算工具:
  深度由 Ext 消没点给出(第 12 主题),平坦性由 Tor 检验(第 8 主题)。
- **飞腾锚点**:**matmul 15×[V03]** —— 计算 Tor/Ext 需取自由分解(矩阵链)、
  应用函子、取同调,本质是一串矩阵运算。🟢Tor/Ext 定义与长正合序列是严格数学(事实锚点)。
- **关键定理**:**长正合序列**。短正合 $0\to M'\to M\to M''\to0$ 诱导
  $\cdots\to\mathrm{Tor}_1(M',N)\to\mathrm{Tor}_1(M,N)\to\mathrm{Tor}_1(M'',N)\to M'\otimes N\to\cdots$
  (Ext 同理,反变)。
- **自测**:计算 $\mathrm{Tor}_1^{\mathbb Z}(\mathbb Z/2,\mathbb Z/2)$。
  (答:$\cong\mathbb Z/2$,用分解 $0\to\mathbb Z\xrightarrow{\times2}\mathbb Z\to\mathbb Z/2\to0$,张量 $\mathbb Z/2$ 后核为 $\mathbb Z/2$。)

---

# 第 3 部分 · 维度理论 (Dimension Theory)

### 第 10 主题 · Krull 维数

- **核心**:$\dim R$ = 素理想严格链 $(0)\subsetneq\mathfrak p_1\subsetneq\cdots\subsetneq\mathfrak p_d$
  的最大长度,是几何维度的纯代数度量。$\dim k[x_1,\dots,x_n]=n$(曲面=2,曲线=1,点=0)。
  核心困难:素理想链「难以直接数」,必须给它**可计算的等价刻画**——
  Hilbert-Samuel 多项式次数、系统参数数、超越次数。Eisenbud 用整整一部分把这些等价定义打通。
- **飞腾锚点**:**FP16 3.81×[L01]** —— 维数是「自由度上界」,
  如同浮点有效位数是精度上界;维数越高参数越自由。
  🟢Krull 维数定义与 $\dim k[x_1,\dots,x_n]=n$ 是严格定理(事实锚点);3.81× 为类比。
- **关键定理**:**维数定理(多等价刻画)**。Noether 局部环 $(R,\mathfrak m)$:$\dim R$ =
  Hilbert-Samuel 多项式次数 = 系统参数数 = 最长素链长度;且 $\dim R\le\dim_k\mathfrak m/\mathfrak m^2$。
- **自测**:写出 $k[x,y,z]/(xy-z^2)$ 的维数。
  (答:$2$;一个方程在三维空间降一维,且 $xy-z^2$ 非零因子,故余维 1。)

---

### 第 11 主题 · Noether 正规化与 Hilbert 零点定理

- **核心**:**Noether 正规化**把任意仿射簇投影到超平面:存在代数无关元 $y_1,\dots,y_d$
  使 $R$ 在 $k[y_1,\dots,y_d]$ 上整,直接给出 $\dim R=d$ 且把「弯曲簇」拉直成多项式空间的有限覆盖。
  **Hilbert 零点定理**把代数(理想)与几何(零点集)彻底统一:代数闭域上,真理想必有零点(弱),
  零点集对应根理想(强)。两者合起来构成「方程↔空间」翻译机。
- **飞腾锚点**:**FP16 3.81×[L01]** —— 正规化是「坐标投影降维」,
  如同数值方法保留主成分降维;零点定理保证「无解」可由 $I=(1)$ 判定。
  🟢Noether 正规化与 Nullstellensatz 是严格定理(事实锚点)。
- **关键定理**:**Hilbert 零点定理**。代数闭域 $k$ 上:
  (弱)$I\subsetneq k[x_1,\dots,x_n]$ $\Rightarrow$ $V(I)\neq\varnothing$;
  (强)$I(V(J))=\sqrt{J}$,理想与零点集通过根理想一一对应。
- **自测**:$V(x^2+1)\subset\mathbb A^1_{\mathbb C}$ 非空(有解 $\pm i$)而在 $\mathbb R$ 上空——
  为何定理要求代数闭域?(因证明依赖 $k[x]$ 极大理想皆 $=(x-a)$。)

---

### 第 12 主题 · 正则序列与深度 (Depth)

- **核心**:$\mathfrak m$ 中的序列 $x_1,\dots,x_r$ **正则**,若每个 $x_i$ 是
  $M/(x_1,\dots,x_{i-1})M$ 的非零因子(逐步剥离不掉到零)。最大正则序列长度 = **深度** $\mathrm{depth}\,M$,
  有纯同调刻画:$\mathrm{depth}\,M=\min\{i:\mathrm{Ext}^i(k,M)\neq0\}$。
  深度衡量「无挠程度」,而差 $\dim M-\mathrm{depth}\,M$(「余深度」)是奇点的重要不变量——
  差越大奇点越深(CM 环即差为零者)。
- **飞腾锚点**:**分支预测[Lab02]** —— 正则序列每步「剥掉一层非零因子」,
  如同分支预测逐步确定执行路径,任一环为零因子则「预测失败」(序列中断)。
  🟢深度 = Ext 消没点是严格定理(事实锚点)。
- **关键定理**:**深度的 Ext 刻画**。$\mathrm{depth}_{\mathfrak m} M=\inf\{n:\mathrm{Ext}_R^n(R/\mathfrak m,M)\neq0\}$;
  正则序列长度与 Ext 消没点一致,使深度可计算。
- **自测**:正则局部环中深度 = 维数(定义性);
  给出深度 < 维数的例子(如 $R=k[x,y,z]/(xy,xz)$,原点处 $\dim=2$ 但 $\mathrm{depth}=1$,有奇点)。

---

### 第 13 主题 · 正则环与非奇异性

- **核心**:**正则局部环**满足 $\dim_k\mathfrak m/\mathfrak m^2=\dim R$(切空间维数 = 簇维数),
  是**非奇点**的代数化身,光滑代数簇的局部模型。正则环恒为整环,且正则局部环是 UFD
  (Auslander-Buchsbaum 定理),是「最好的」局部环;正则性局部化后保持。
  Eisenbud 把正则环作为奇点分阶的「零点基准」——CM、Gorenstein、完全交都是它的「退化近邻」。
- **飞腾锚点**:**Schmidt 正交化** —— 正则局部环的参数系(切空间基)如正交基:
  一组坐标使结构「最平整」,无奇点。🟢正则环恒为整环/UFD 是严格定理(事实锚点);Schmidt 为类比。
- **关键定理**:**正则局部环判据**。Noether 局部环 $(R,\mathfrak m)$ 正则 $\iff$
  $\mathfrak m$ 由 $\dim R$ 个元素生成(参数系存在) $\iff$ $\dim_k\mathfrak m/\mathfrak m^2=\dim R$。
- **自测**:$k[x,y]_{(x,y)}$ 正则($\dim=2$,切空间二维);
  $k[x,y]_{(x,y)}/(x^2-y^3)$ 正则吗?(否,曲线有尖点 cusp,切空间维数 $>$ 簇维数 $1$。)

---

# 第 4 部分 · 几何工具 (Geometric Tools)

### 第 14 主题 · Gröbner 基与 Buchberger 算法 ⭐

- **核心**:**Gröbner 基**是多项式理想的「计算友好基」:给定单项式序,
  它使成员判定 $f\in I?$ 归约为「除尽即成员」(余式 $\mathrm{rem}(f,G)=0\iff f\in I$)。
  **Buchberger 算法**由任意生成集构造 Gröbner 基,在 Noether 环上必然停机。
  这是 Eisenbud 区别于 AM 的**计算面核心**:理想运算(交、商、消元、准素分解)全可算法化,
  是 Macaulay2/Singular 的理论基石,让交换代数从「纸面推导」变成「可跑的程序」。
- **飞腾锚点**:**GEMM 9.45G[Lab05]** ⭐ —— Gröbner 基计算需反复做多项式除法与
  $S$-多项式约化,是密集符号矩阵吞吐,如同 GEMM 批量运算。
  🟢Buchberger 算法停机性是严格定理(事实锚点);9.45G 为吞吐类比。
- **关键定理**:**Buchberger 算法 + 停机性**。对任意生成集,反复加入
  $S$-多项式 $S(f_i,f_j)=\frac{\mathrm{lcm}(\mathrm{LT}_i,\mathrm{LT}_j)}{\mathrm{LT}_i}f_i-(\cdots)f_j$ 的余式,
  经有限步得 Gröbner 基(Noether 条件保证终止)。
- **自测**:理想 $I=(x^2,y^3)\subset k[x,y]$,验证 $\{x^2,y^3\}$ 在 lex 序($x>y$)下
  已是 Gröbner 基($S$-多项式 $y^3x^2-x^2y^3=0$,余式为零)。

---

### 第 15 主题 · 消元与结式 (Resultants)

- **核心**:**消元定理**用 Gröbner 基在消元序下求「消去某变元后」的理想
  $I\cap k[x_2,\dots,x_n]$,是解方程组投影降维的算法(几何上 = 投影到坐标面)。
  **结式** $\mathrm{Res}(f,g)$ 判定两多项式有无公根(Sylvester 矩阵的行列式构造),
  是经典消元工具,也是几何相交理论的计算入口——两曲线相交 ⟺ 结式为零。
  Eisenbud 把消元与结式做成从「解方程」到「数交点」的统一计算链。
- **飞腾锚点**:**GEMM 9.45G[Lab05]** —— 结式是 Sylvester 矩阵的行列式,
  消元是「矩阵批量投影」,同源于矩阵吞吐。
  🟢消元定理与结式判公根是严格结论(事实锚点)。
- **关键定理**:**消元定理**。$I\subset k[x_1,\dots,x_n]$ 在消元序($x_1>\cdots>x_n$)下的
  Gröbner 基 $G$,则 $G\cap k[x_{r+1},\dots,x_n]$ 是消元理想 $I\cap k[x_{r+1},\dots,x_n]$ 的 Gröbner 基。
- **自测**:用结式判定 $f=x^2-2$、$g=x^2-3$ 在 $\mathbb Q$ 上有无公根
  ($\mathrm{Res}(f,g)\neq0$,故无公根;根 $\pm\sqrt2,\pm\sqrt3$ 互不相同)。

---

### 第 16 主题 · Hilbert 函数与 Hilbert 多项式 ⭐

- **核心**:对分次环 $R=\bigoplus R_n$,**Hilbert 函数** $H_R(n)=\dim_k R_n$ 度量每度的「大小」;
  对大 $n$,它是多项式 $P_R(n)$——**Hilbert 多项式**,次数 $=\dim R$。
  这是把维数(素理想链长度)变成可计算的多项式次数的桥梁。
  对局部环用 $\ell(R/\mathfrak m^{n+1})$ 的 Hilbert-Samuel 多项式,首项系数 $\times d!$ = 重数,衡量奇点「多重性」。
- **飞腾锚点**:**UDOT 16.9×[E05]** ⭐ —— Hilbert 函数逐度累加 $\dim_k R_n$,
  如同点积(UDOT)逐项相乘累加;多项式次数给出维数,是「累加的增长率」。
  🟢Hilbert 多项式次数 = 维数是严格定理(事实锚点);16.9× 为吞吐类比。
- **关键定理**:**Hilbert-Samuel 多项式定理**。Noether 局部环 $(R,\mathfrak m)$,
  $\ell(R/\mathfrak m^{n+1})$ 对大 $n$ 是次数 $=\dim R$ 的多项式;
  首项系数 $e(R)\times(\dim R)!$ = 重数 multiplicity,是奇点的数值不变量。
- **自测**:$R=k[x,y]$ 的 $R_n$ 由 $n$ 次单项式张成,$\dim_k R_n=n+1$,
  故 $H_R(n)=n+1$(一次多项式);齐次环维数 = 多项式次数 + 1,故 $\dim R=2$。

---

# 第 5 部分 · 专题 (Special Topics)

### 第 17 主题 · Cohen-Macaulay 环

- **核心**:**Cohen-Macaulay (CM) 环**满足 $\mathrm{depth}\,M=\dim M$(深度 = 维数),
  是「深度达到上限」的环,介于正则环与一般 Noether 环之间。
  CM 环有优良的消元与相交性质:参数系恒为正则序列(逐个剥离不掉零),是几何「好」簇的代数化身。
  多数光滑簇局部是 CM,且 CM 性在一般超平面截面下保持(「切一刀仍是 CM」),
  使维数、相交、投影都表现良好。
- **飞腾锚点**:**Schmidt 正交化** —— CM 环中参数系(坐标)如正交基:
  逐个剥离都是非零因子,结构「方正」无嵌套挠。
  🟢CM 环深度 = 维数是严格定义(事实锚点);正交化为类比。
- **关键定理**:**CM 环的等价刻画**。Noether 局部环 $R$ 是 CM $\iff$
  存在长度 $=\dim R$ 的正则序列 $\iff$ 每个参数系都是正则序列;
  且 正则环 $\Rightarrow$ CM $\Rightarrow$ 相交重数只依赖维数。
- **自测**:$k[x,y,z]/(xy)$ 是 CM 吗?($\dim=2$,但 $\mathrm{depth}=1$
  因 $xy=0$ 使 $x$ 在 $y$ 处为零因子——非 CM,是「两平面相交」退化例子。)

---

### 第 18 主题 · Gorenstein 环

- **核心**:**Gorenstein 环**是 CM 环的精致子类:不仅深度 = 维数,且「对偶」性质极好——
  有限内射维数($\mathrm{id}_R R<\infty$)。它是 Serre 对偶与相交理论的最佳舞台:
  Gorenstein 局部环中典范模 $\omega_R$ 存在且秩为 1,提供类似 Poincaré 对偶的结构,
  使上同调的对偶公式干净成立。正则环 $\Rightarrow$ Gorenstein $\Rightarrow$ CM,是奇点分阶的第二层。
- **飞腾锚点**:**Schmidt 正交化** —— Gorenstein 环有「自对偶」结构,
  如同在函数空间中找到对偶基,内积非退化(典范模 $\cong R$)。
  🟢Gorenstein = 有限内射维数是严格定义(事实锚点);正交化为类比。
- **关键定理**:**Gorenstein 判据**。Noether 局部环 $R$ Gorenstein $\iff$ $\mathrm{id}_R R<\infty$ $\iff$
  $R$ 是 CM 且典范模 $\omega_R\cong R$;对偶模运算封闭,适合 Serre 对偶。
- **自测**:Artinian 局部环 $k[x]/(x^n)$ 是 Gorenstein 吗?
  (是,socle $(0:x)$ 一维 $=k$,典范模为自身;它也是 CM。)

---

### 第 19 主题 · 完全交与相交重数

- **核心**:**完全交**(complete intersection) = 由正则序列定义的理想 $I=(x_1,\dots,x_r)$
  造出的商环 $R/I$,是 Gorenstein 环的重要来源(完全交 $\Rightarrow$ Gorenstein)。
  **相交重数** $\chi(M,N)=\sum_i(-1)^i\ell(\mathrm{Tor}_i(M,N))$ 用 Tor 的交错和定义,
  度量两子簇在某点相交的「重数」。Serre 给出使其非负且达维数上界的公式,
  把几何相交翻译成纯同调计算,是衔接 Hartshorne 相交理论的关键。
- **飞腾锚点**:**分支预测[Lab02]** —— 相交重数用 Tor 的交错和(带符号分支求和)定义,
  如同分支预测中各路径贡献的带符号累加。
  🟢Serre 相交公式与重数非负性是严格定理(事实锚点)。
- **关键定理**:**Serre 相交公式 + 重数上界**。$\dim M+\dim N\le\dim R$ 时,
  $\chi(M,N)=\sum_i(-1)^i\ell(\mathrm{Tor}_i^R(M,N))$;正则环上 $\chi(M,N)\ge0$(Serre 自证非负性)。
- **自测**:两平面在三维空间交于直线时重数为 1(预期相交);
  两平面重合时重数「无穷」——说明正则环中需用长度有限化处理,Tor 高阶项起修正作用。

---

# 第 6 部分 · 退化族与同调 (Degenerations & Homology)

### 第 20 主题 · 形变理论、导出范畴与上同调维数预告

- **核心**:**形变理论**研究环/簇在参数变化下如何「连续弯曲」:平坦族是平坦性的几何舞台,
  要求纤维随参数「连续无跳变」。**Hilbert 概形**参数化所有子簇,是模空间(moduli)理论的基石。
  Eisenbud 末章预告**导出范畴**与**上同调维数**——把同调代数推向层上同调与 Serre 对偶,
  衔接 Hartshorne 第 III 章。这是「从环到族、从同调到几何」的过渡门户,为读 Hartshorne 层上同调做语言准备。
- **飞腾锚点**:**分支预测[Lab02]** —— 平坦族中纤维「连续无跳变」,
  如同分支预测假定路径平滑;若平坦性破坏则纤维「跳维」(预测失败,如 $t=0$ 时抛物线退化成二重线)。
  🟢平坦族 = 逐纤维同维是严格结论(事实锚点)。
- **关键定理**:**平坦族保持 Hilbert 多项式**。$R\to S$ 平坦、$S$ 有限表现,
  则 Hilbert 多项式沿纤维常值——平坦族各纤维「形状(维数 + 重数)不变」,
  是模空间稳定性与 GIT 的代数根基。
- **自测**:$k[t,x,y]/(ty-x^2)$ 作为 $k[t]$-代数是平坦族;$t\neq0$ 时光滑抛物线,
  $t=0$ 时退化成二重直线——为何 Hilbert 多项式仍相同?
  ($ty-x^2$ 在整环 $k[t,x,y]$ 中非零因子 $\Rightarrow$ 商平坦 $\Rightarrow$ 多项式守恒。)

---

## §9 思想主线(约 220 字)

Eisenbud 的《交换代数》有一条鲜明的**「几何动机驱动 + 计算落地」**主线:
**每个代数概念都先回答「几何上是什么」,再给「怎么算」**。
第 1 部分确立根基——多项式环 = 几何对象,局部化 = 看点的放大镜,Noether 条件 = 有限性的算法保证;
第 2 部分把向量空间升格为模,Nakayama 引理成为局部推理的「生成即非零」判据,平坦性刻画「连续族」;
第 3 部分维度论把抽象的素理想链长度翻译成可计算的 Hilbert 多项式次数,正则环 = 非奇点;
第 4 部分以 Gröbner 基与 Hilbert 函数补足 AM 缺失的计算面,让代数能「真跑」;
第 5-6 部分用 CM/Gorenstein/完全交给奇点分阶,以平坦族与导出范畴预告通向 Hartshorne。
一句话贯穿:**环是几何,局部化看细节,维数数自由度,同调量奇点,平坦保连续**——这是一条从「方程」到「空间」到「形变」的完整攀升。

---

## §10 与本仓库其他笔记的交叉引用

**与同级教材对比**:
- **Atiyah-MacDonald**(本仓库已精读,Eisenbud 直接前身):AM 是 128 页极简骨架,
  Eisenbud 是其「扩充+现代化」。AM 用习题埋下 $\mathrm{Spec}$、Hilbert 函数种子,
  Eisenbud 把种子长成大树并补足计算面(Gröbner、CM/Gorenstein)。
  AM 第 11 章维数论 ↔ Eisenbud 第 3 部分;AM 第 10 章完备化 ↔ Eisenbud 第 1 部分。
- **Hartshorne《代数几何》**(本仓库已精读,stage-3):Eisenbud 是 Hartshorne 第 I-II 章的
  「交换代数弹药库」。Hartshorne 需要的正则序列/深度/Serre 对偶/相交重数,
  在 Eisenbud 第 3-5 部分一次配齐。
- **Weibel《同调代数》**(本仓库已精读):Eisenbud 第 2、5 部分的 Tor/Ext/导出范畴是 Weibel 的应用预告,
  Weibel 给谱序列与导出函子的完整理论。
- **Hungerford / Dummit / Artin**(本仓库已精读):提供一般环/模/域/Galois 骨架,
  Eisenbud 专攻交换环并接入代数几何。

**AI 锚点法(数学 ↔ 工程/Python 映射)**:
- **Noether 升链 = 算法停机保证**:Noether 条件保证 Gröbner 基/SymPy 理想运算必然终止——
  没有它符号计算会「无限发散」(类比 `while True` 无终止条件)。
- **局部化 $R_{\mathfrak p}$ = 局部缓存/上下文**:在点 $\mathfrak p$ 处查局部信息而不重算全局,
  如同函数局部变量遮蔽全局;Python 装饰器局部增强函数同理。
- **平坦性 = 无副作用纯函数**:平坦模保正合(信息无损),如同纯函数无副作用、可并行;
  平坦族 = 可微分的连续参数族(神经网络权重随训练连续变化)。
- **Gröbner 基 = 规范化/NF**:把任意生成集化为「规范基」使成员判定归约,
  如同 `numpy.linalg.qr` 化矩阵为正交规范形;`sympy.polys.groebner()` 是直接 Python 落地。
- **Hilbert 函数 = 增长率/复杂度**:$H_R(n)$ 渐近多项式次数给出维数,
  如同算法复杂度 $O(n^d)$ 的次数 $d$ 揭示规模。
- **CM/Gorenstein = 对称/可逆结构**:Gorenstein 自对偶性如同对称矩阵(可逆+对称),
  典范模 $\cong R$ 如同「空间与对偶自然同构」。

---

> **结语**:读 Eisenbud,是在给 AM 的骨架**长肉并装上计算引擎**。
> 当你在第 1 部分看到局部化如何「聚焦看点」,在第 4 部分用 Gröbner 基让理想「真跑起来」,
> 在第 5 部分用 CM/Gorenstein 给奇点分阶时,你会明白:「几何动机不是装饰,而是让每个抽象都落在可计算、可可视化的土地上」。
> 这正是一个编程思维扎实、却要补数学的读者最需要的——**让代数先有几何图景,再有算法落地**。
