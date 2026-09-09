# Rotman《同调代数引论》· 快速逐章精读

> 基于原书:`An Introduction to Homological Algebra` (Joseph J. Rotman, 2nd Ed, 2009, UTM, Springer) / 读于:2026-07-02
> 定位:**友好现代版同调代数**,比 Weibel 更易懂,两段式结构(先工具预备·后同调本体)+ 历史注记丰富。
> 本文为**快速逐章精读**,每章 1 个飞腾锚点 + 1 个关键定理 + 1 道自测题;侧重与 Weibel 的「友好增量」。

---

## §0 引言:Rotman 同调代数是什么,为什么读它

Joseph J. Rotman 的《An Introduction to Homological Algebra》第二版(2009, UTM)是**同调代数最友好的现代教材之一**。
相对 Weibel(1988)的「假设你会范畴论,直接上复形」的进阶写法,Rotman 采用**两段式**:前半彻底夯实工具
(范畴/函子/伴随/$\mathrm{Hom}$/张量/投射·内射·平坦模/正合性),后半才进入同调代数本体(链复形/导出函子/Tor/Ext/谱序列)。
这种「先把工具讲透再动手」的教学哲学,正是它比 Weibel 更易懂的根本原因。Rotman 全书穿插大量**历史注记(marginalia)**
——追溯 Cartan-Eilenberg(1956)、Grothendieck 学派的谱序列与导出函子起源,把每个定义的「为什么这样定义」讲清楚。
第二版(2009)相对第一版(1979)大幅重写,引入更现代的范畴论语言与导出范畴引论,与 Weibel 形成互补对照。

为什么读它?本仓库已精读 Weibel(同调代数标准,密度高跳跃大)、Mac Lane 范畴论(GTM5,Abel 范畴/伴随/极限)、
Eisenbud 交换代数(GTM150,正则环/深度/合冲)。Rotman 是**把 Weibel 跳过的细节补全、把 Mac Lane 的范畴语言落到同调计算、
把 Eisenbud 的交换代数直觉接到 Tor/Ext** 的「友好对照版」。它的核心使命与 Weibel 同源:把「不保持正合的函子」
(张量积右正合不左正合、$\mathrm{Hom}$ 左正合不右正合)补全成**导出函子**,让断裂的正合序列重新接上;
但 Rotman 给出更多**可算的例子**与 **Yoneda 的 $n$-扩张描述**(Weibel 着墨较少),适合查漏补缺与建立直觉。

对比四本主流教材:

| 书 | 风格 | 严格性 | 适合谁 |
|---|---|---|---|
| **Rotman《同调代数引论》2nd (2009, UTM)** | 友好现代版,两段式(工具+本体),历史注记丰富,计算导向,证明完整不跳跃 | 严谨且详尽,习题有提示 | 想要「读得下去」、要详细动机与例子的入门进阶者 |
| Weibel《同调代数引论》(1988) | 现代标准,全谱系 10 章,从复形到导出范畴,密度高 | 严谨,习题多,跳跃大 | 有范畴/抽代基础、想快进的进阶者 |
| Mac Lane《Homology》(1963) | 经典奠基,范畴论语言开山,群上调与同调详尽 | 古典严格,记号偏老 | 想追溯历史源头、慢读经典的读者 |
| Gelfand-Manin《方法》(1996/2003) | 几何观点,以导出范畴为纲,现代但抽象 | 现代严格,跳跃大,哲学性强 | 几何/代数几何方向的研究者 |

读完 Weibel 再读 Rotman,「友好增量」集中在四处,这也是本文逐章标注的重心:

1. **工具预备更厚**(Ch1):Weibel 假设你会范畴/模/$\mathrm{Hom}$/张量/特殊模,Rotman 把它们(含 Baer 判据、$\mathrm{Hom}$-张量伴随、正向/逆向极限)在 Ch1 全部讲透,占近全书四分之一篇幅;
2. **Yoneda $n$-扩张视角**(Ch2):Rotman 把 $\mathrm{Ext}^n$ 与「长度 $n$ 的正合序列等价类」对接,复合为 Yoneda 积——Weibel 几乎只用导出函子定义,丢掉了这层几何直觉;
3. **历史注记(marginalia)**:全书穿插追溯 Cartan-Eilenberg(1956)、Grothendieck 谱序列与导出函子、Verdier 导出范畴的起源,把「为何这样定义」讲清楚;
4. **图追踪基本功**(Ch10 附录):五引理/九引理/3×3 引理详加操练,Weibel 默认你会、Rotman 把它当基本功反复练。

> 一句话:Weibel 是「地图」(全景与终点),Rotman 是「路书」(每段为什么走、怎么走都写清)。

---

## §1 全书 10 章骨架一览(飞腾锚点分布)

| 章 | 标题 | 核心概念 | 飞腾锚点 |
|---|---|---|---|
| 1 | 预备:范畴·模·Hom·张量·导出函子 | 伴随/$\mathrm{Hom}$-张量伴随/特殊模/蛇引理 | Schmidt 正交化 |
| 2 | Tor 与 Ext | $\mathrm{Tor}_n$/$\mathrm{Ext}^n$/Yoneda $n$-扩张/分类扩张 | matmul 15×[V03] ⭐ |
| 3 | 谱序列 | $E^r$/$d_r$/收拢/Grothendieck 谱序列 | GEMM 9.45G[Lab05] |
| 4 | 群上同调 | $H^n(G,M)$/Bar 分解/转移/Tate 周期 | UDOT 16.9×[E05] |
| 5 | Lie 代数上同调 | $U(\mathfrak g)$/PBW/Chevalley-Eilenberg/Whitehead | FP16 3.81×[L01] |
| 6 | Hochschild 上同调 | $HH^n$/$HC_n$/Connes 算子 $B$/形变 | Iron Law<2%[Lab00] |
| 7 | 同伦与单纯 | 单纯对象/Dold-Kan/几何实现/单纯集 | 分支预测[Lab02] |
| 8 | 导出范畴引论 ⭐⭐ | 三角范畴/Verdier 局部化/$\mathbf{RF}$/$\mathbf{LF}$ | TLB 4.81×[E04] ⭐ |
| 9 | 层(Sheaf)上同调 | $\mathbf Rf_*/R^n\Gamma$/Čech/Grothendieck 消没 | GEMM 9.45G[Lab05] |
| 10 | 专题与附录 | 图追踪/五·九·3×3 引理/$K$-理论延伸 | matmul 15×[V03] |

---

### 第 1 章 · 预备:范畴·模·Hom·张量·链复形·导出函子

- **核心**:Rotman 的「友好」就体现在这一章——把 Weibel 默认你会的工具**全部讲透**。
  范畴/函子/自然变换/伴随函子;$R$-模与 $\mathrm{Hom}_R(M,N)$、张量积 $M\otimes_R N$;
  **$\mathrm{Hom}$-张量伴随** $\mathrm{Hom}_S(M\otimes_R N,P)\cong\mathrm{Hom}_R(M,\mathrm{Hom}_S(N,P))$
  揭示「$\mathrm{Hom}$ 左正合、$\otimes$ 右正合」的根源。
  投射/内射/平坦模的等价刻画(投射=直和项/提升性;内射=可扩性/Baer 判据;平坦=$-\otimes$ 正合)。
  链复形 $d^2=0$、同调 $H_n=\ker d/\mathrm{im}\,d$;**蛇引理**把核/余核串成正合六项序列,是导出函子长正合序列的引擎。
  投射分解/内射分解 → 右导出 $R^nF$、左导出 $L_nF$。Rotman 在此先建好全部「弹药库」。
  Weibel 把这些当「已知」一页带过,Rotman 用近全书四分之一篇幅铺好——这是它适合自学、适合 Weibel 受挫者回补的根本。

- **飞腾锚点**:**Schmidt 正交化** —— 投射/内射分解都是「最佳逼近」:把模抬到投射(或内射)层,逐层消除残差(合冲 syzygy)。
  🟡类比:每消解一轮像 Schmidt 正交化剥离一个非正交分量,直到残差为零(自由/投射),分解终止;分解长度即「需要几轮正交化」。
  🟢事实:Rotman 把 Baer 判据(内射性只需检验理想)讲成「只需正交化一组生成元」,把抽象存在性变成可执行算法。

- **关键定理**:**$\mathrm{Hom}$-张量伴随 + 蛇引理**。
  $$\mathrm{Hom}_S(M\otimes_R N,\,P)\ \cong\ \mathrm{Hom}_R\!\big(M,\,\mathrm{Hom}_S(N,P)\big)$$
  伴随关系决定了 $\mathrm{Hom}$ 左正合、$\otimes_R$ 右正合,是 $\mathrm{Ext}/\mathrm{Tor}$ 的逻辑前提;
  蛇引理给出连接同态 $\partial:\ker\gamma\to\mathrm{coker}\,\alpha$,驱动一切长正合序列。

- **自测**:用 Baer 判据判断 $\mathbb Z$ 作为 $\mathbb Z$-模是否内射。(提示:$\mathbb Z$ 是 PID,只需检验理想 $n\mathbb Z$;
  实际 $\mathbb Z$ **不**内射,因 $1\in\mathbb Z$ 无法扩张到 $n\mathbb Z$ 之外;真正的内射 $\mathbb Z$-模是可除群如 $\mathbb Q$。)

---

### 第 2 章 · Tor 与 Ext

- **核心**:最重要的两个导出函子。$\mathrm{Tor}_n^R(M,N)=L_n(-\otimes_R N)(M)$,度量张量积「撕裂」模的程度;
  $\mathrm{Ext}_R^n(M,N)=R^n\mathrm{Hom}(M,-)(N)$。PID 上 $\mathrm{Tor}_n=\mathrm{Ext}^n=0$($n\ge2$),只剩 $n=0,1$。
  **Rotman 的特色增量**是 **Yoneda 的 $n$-扩张描述**:$\mathrm{Ext}^n_R(M,N)$ 由长正合序列
  $0\to N\to X_{n-1}\to\cdots\to X_0\to M\to 0$ 的等价类给出,复合为 Yoneda 积——
  这把「导出函子」与「扩张的几何直觉」直接对接,Weibel 着墨较少。最深刻结论:$\mathrm{Ext}^1_R(M,N)$
  一一分类短正合扩张 $0\to N\to X\to M\to 0$(Baer)。Rotman 配大量可算例子,把抽象 Ext 变成手算题。

- **飞腾锚点**:**matmul 15×[V03]** —— $\mathrm{Ext}$ 的计算本质是「把短正合序列跑成长正合序列」的链式矩阵运算。
  🟢事实:取投射分解后 $\mathrm{Ext}^n_R(M,N)$ 是复形 $\mathrm{Hom}(P_\bullet,N)$ 的上同调,实现上是链式矩阵核/像求商,与张量核流水线同构。
  🟡类比:Yoneda 的 $n$-扩张像把一个「等式」拆成长度 $n$ 的链,Ext 度量这条链闭合的「自由度」。

- **关键定理**:**$\mathrm{Ext}^1$ 分类扩张(Yoneda 特殊情形)**。
  $$\mathrm{Ext}^1_R(M,N)\ \longleftrightarrow\ \{\text{扩张 }0\to N\to X\to M\to 0\}/_{\text{等价}},\qquad
  \mathrm{Ext}^1_R(M,N)=0\Leftrightarrow X\cong N\oplus M.$$

- **自测**:计算 $\mathrm{Ext}^1_\mathbb Z(\mathbb Z/2,\mathbb Z)$ 与 $\mathrm{Ext}^1_\mathbb Z(\mathbb Z/2,\mathbb Z/2)$。
  (答案:前者 $\cong\mathbb Z/2$;后者 $\cong\mathbb Z/2$,扩张为 $\mathbb Z/2\oplus\mathbb Z/2$ 与 $\mathbb Z/4$。)

---

### 第 3 章 · 谱序列

- **核心**:全书的「计算枢纽」。谱序列是「逐页逼近同调」的算法,把无法一次算完的双复形分解成一族页面。
  双分次模族 $E^r_{p,q}$($r\ge2$)配双阶微分 $d_r:E^r_{p,q}\to E^r_{p-r,q+r-1}$,$d_r^2=0$,下一页 $E^{r+1}=H(E^r,d_r)$;
  某页 $d_r=0$ 后序列**收拢**(collapse),**收敛**于滤过目标的关联分次 $E^\infty_{p,q}\cong\mathrm{gr}_p H_{p+q}$。
  **Rotman 的特色增量**:详尽的逐页手算例子(行收拢/列收拢),以及 Cartan-Eilenberg 复形的两个谱序列,
  把抽象收敛讲成可追踪的表格演算。最有力的是 **Grothendieck 谱序列**:函子复合 $G\circ F$ 的导出由 $E_2$ 页逼近。
  应用场景:纤维化的 Leray-Serre 谱序列(拓扑)、Lyndon-Hochschild-Serre 谱序列(群)、层的 Leray 谱序列(几何)。

- **飞腾锚点**:**GEMM 9.45G[Lab05]** —— 谱序列页 $E^r_{p,q}$ 是双指标二维阵列,每一页是一次「高维吞吐」的全阵运算。
  🟢事实:$E^{r+1}$ 由 $E^r$ 的同调给出,实现上是分块矩阵核/像求商,与高维 GEMM 吞吐同构。
  🟡类比:谱序列像多尺度分析(小波),先粗(低 $r$)后细(高 $r$),逐页修正直到收敛,误差随 $r$ 递减。

- **关键定理**:**Grothendieck 谱序列**。
  $$E_2^{p,q}=R^pG\big(R^qF(M)\big)\ \Longrightarrow\ R^{p+q}(G\circ F)(M).$$
  当 $R^qF(M)$ 为 $G$-无环,序列在第 2 页退化,得 $R^n(GF)\cong G(R^nF)$。

- **自测**:写出双复形 $C_{\bullet,\bullet}$ 的两个谱序列(${}^I E$ 与 ${}^{II}E$)的 $E^2$ 页,并说明列收拢条件。
  (提示:${}^I E^2_{p,q}=H_p^h H_q^v(C)$,${}^{II}E^2_{p,q}=H_q^v H_p^h(C)$。)

---

### 第 4 章 · 群上同调

- **核心**:把群 $G$ 看作范畴,群上同调是同调代数在「一个对象」上的特化。设 $M$ 是 $G$-模($\mathbb ZG$-模),
  $H^n(G,M)=\mathrm{Ext}^n_{\mathbb ZG}(\mathbb Z,M)$,$H_n(G,M)=\mathrm{Tor}^{\mathbb ZG}_n(\mathbb Z,M)$。
  **Bar 分解**给标准自由 $\mathbb ZG$-分解,$n$ 阶基为 $[g_1|\cdots|g_n]$,把抽象 Ext 变成可写上链复形。
  群扩张 $1\to M\to E\to G\to 1$ 由 $H^2(G,M)$ 分类;$H^1(G,M)=\mathrm{Der}(G,M)/\mathrm{Inn}$ 为交叉同态。
  **Rotman 的特色增量**:更详尽的有限群算例、**转移映射**(transfer)联系子群、有限群的 **Tate 上同调**及其周期性 $\hat H^n\cong\hat H^{n+h}$。
  应用场景:类域论(用 $H^2$ 分类 Brauer 群)、Galois 上同调($G=\mathrm{Gal}(L/K)$)、群扩张可裂性判定。

- **飞腾锚点**:**UDOT 16.9×[E05]** —— Bar 上链 $C^n(G,M)$ 的元素是 $G^n\to M$ 的函数,微分是对群元的嵌套求和。
  🟢事实:微分类似点积累加(UDOT),对每个 $[g_1|\cdots|g_n]$ 做 $n+1$ 项交错和;
  🟡类比:Bar 分解像「把群元素乘法历史编码成可累加的字」,上同调是这些字循环求和的「闭合度」。

- **关键定理**:**群扩张由 $H^2$ 分类**。$H^n(G,M)\cong\mathrm{Ext}^n_{\mathbb ZG}(\mathbb Z,M)$,且
  $H^2(G,M)=0\Leftrightarrow$ 所有扩张 $1\to M\to E\to G\to 1$ 可裂。

- **自测**:计算 $H^n(\mathbb Z/2,\mathbb Z)$(平凡作用)与 $H^n(\mathbb Z,\mathbb Z)$。
  (答案:前者 $H^0=\mathbb Z$,$H^{2k}=\mathbb Z/2$($k\ge1$),$H^{2k+1}=0$;后者 $H^0=\mathbb Z$,$H^1=\mathbb Z$,$H^{n\ge2}=0$。)

---

### 第 5 章 · Lie 代数上同调

- **核心**:域 $k$ 上 Lie 代数 $\mathfrak g$ 的同调,通过**泛包络代数** $U(\mathfrak g)$ 归约到结合代数。
  **PBW 定理**:$U(\mathfrak g)\cong S(\mathfrak g)$(对称代数)作为滤过向量空间——Rotman 给出完整证明(Weibel 多半引用)。
  $H_n(\mathfrak g,M)=\mathrm{Tor}^{U(\mathfrak g)}_n(k,M)$,$H^n(\mathfrak g,M)=\mathrm{Ext}^n_{U(\mathfrak g)}(k,M)$。
  **Chevalley-Eilenberg 复形**用外代数 $\wedge^n\mathfrak g^*$ 做上链,微分由 Lie 括号诱导。
  半单标志:**Whitehead 引理**——$\mathfrak g$ 半单 $\Rightarrow H^1=H^2=0$($M$ 有限维非平凡),
  由此推出 Levi 分解与 Weyl 完全可约。这是 Lie 理论与同调代数最美的交汇。

- **飞腾锚点**:**FP16 3.81×[L01]** —— Chevalley-Eilenberg 微分是 $\wedge\mathfrak g$ 上的交替双线性运算(Lie 括号的线性化)。
  🟡类比:半单情形上同调「接近正合」($H^1=H^2=0$),像浮点精度下的「近似零残差」;
  🟢事实:数值实现时,结构常数 $c_{ij}^k$ 的反对称求和对精度敏感,需类 FP16 的容差控制。

- **关键定理**:**Whitehead 引理**。$\mathfrak g$ 半单、$M$ 有限维非平凡 $\Rightarrow H^1(\mathfrak g,M)=H^2(\mathfrak g,M)=0$;
  推论(Weyl):有限维 $\mathfrak g$-模完全可约。

- **自测**:对 $\mathfrak g=\mathfrak{sl}_2(k)$(char $k\ne2$),用 CE 复形算低阶同调。
  (答案:$H_0=k$,$H_1=H_2=0$,$H_3=k$。)

---

### 第 6 章 · Hochschild 上同调

- **核心**:结合 $k$-代数 $A$ 的同调理论。$HH^n(A,M)=\mathrm{Ext}^n_{A\otimes A^{op}}(A,M)$,
  标准 bar 复形 $C^n(A,M)=\mathrm{Hom}_k(A^{\otimes n},M)$;取 $M=A$ 得 $HH^n(A,A)$ 控制 $A$ 的**形变**
  (Gerstenhaber:$HH^2$=无穷小形变,$HH^3$=障碍)。**循环同调** $HC_n(A)$ 由 Connes 引入,
  在 Hochschild 复形上叠加循环对称,由 **Connes 算子 $B$**($B:HC_n\to HC_{n-1}$)与边界 $b$ 构成 $(b,B)$-双复形。
  **Rotman 的特色增量**:相对同调与到非交换几何(Connes)、$K$-理论的对接叙述。
  应用场景:$HH^2$ 控制结合代数的形变(量子化),循环同调 $HC_n$ 是 de Rham 上同调的非交换推广。

- **飞腾锚点**:**Iron Law<2%[Lab00]** —— $(b,B)$-双复形的核心是 $B^2=b^2=Bb+bB=0$ 的「双重正合性」铁律。
  🟢事实:总复形的正合性必须严格(误差为零),任何数值扰动都会破坏 $HC_n$ 的周期性结构。
  🟡类比:$HH^2$ 分类形变像「参数空间的容差带」,零障碍($HH^3=0$)意味着形变可积分类似 Iron Law 的零误差。

- **关键定理**:**Connes 精确序列(SBI)**。
  $$\cdots\to HH_n(A)\xrightarrow{I}HC_n(A)\xrightarrow{S}HC_{n-2}(A)\xrightarrow{B}HH_{n-1}(A)\to\cdots$$

- **自测**:计算 $HH_n(k[x])$ 与 $HC_n(k[x])$。
  (答案:$HH_0=k[x]$,$HH_1=k[x]dx$,$HH_{n\ge2}=0$;$HC_{2k}\cong k[x]$,$HC_{2k+1}\cong k[x]\,dx$。)

---

### 第 7 章 · 同伦与单纯方法

- **核心**:用**单纯对象**给链复形一个「组合几何」模型。单纯 $R$-模是反变函子 $X:\boldsymbol\Delta^{op}\to R\text{-Mod}$,
  带面映射 $d_i:X_n\to X_{n-1}$($0\le i\le n$)与退化映射 $s_i:X_n\to X_{n+1}$,满足单纯恒等式 $d_id_j=d_{j-1}d_i$($i<j$)等。
  **Dold-Kan 对应**:单纯 $R$-模范畴 $\cong$ 非负分次链复形范畴——任一链复形可(同伦意义下)唯一提升为单纯模。
  单纯集(simplicial set)的几何实现是 CW 复形,是同伦论的组合模型。**Rotman 的特色增量**:
  把单纯方法与同伦论的联系讲得比 Weibel 更具体,为高阶范畴(∞-范畴、单纯 ∞-群胚)埋下种子。

- **飞腾锚点**:**分支预测[Lab02]** —— 面映射 $d_i$、退化映射 $s_i$ 是一组「带下标分支」的操作,需按 $i<j$ 等条件选不同分支。
  🟡类比:Dold-Kan 对应像「把链复形的线性流水线展开成带分支的单纯网格」,每个面映射是一次条件分支;
  反过来链复形是单纯网格的「规范化(去分支)投影」。

- **关键定理**:**Dold-Kan 对应**。正规化函子 $N$ 给范畴等价
  $$N:\{\text{单纯 }R\text{-模}\}\xrightarrow{\sim}\{\text{非负分次链复形}\},\qquad H_*(X)\cong H_*(N(X)).$$

- **自测**:写出链复形 $\cdots0\to M\xrightarrow{0}M\to0$($d_1=0$)对应的单纯模前三层 $X_0,X_1,X_2$。
  (提示:用 $N$ 的逆 $X_n=\bigoplus_{[n]\twoheadrightarrow[k]}N_k$。)

---

### 第 8 章 · 导出范畴引论 ⭐⭐

- **核心**:现代视角的顶峰,Verdier(1963)对同调代数的重构。传统导出函子用 $\delta$-函子+长正合序列「笨重」;
  导出范畴把这套提升为范畴语言。起点:**三角范畴**——带平移 $[1]$ 与 distinguished triangles $X\to Y\to Z\to X[1]$,
  满足四条公理(TR1–TR4),是正合三角形的范畴化。链复形**同伦范畴** $K(\mathcal A)$ 天然三角。
  **Verdier 局部化** $D(\mathcal A)=K(\mathcal A)[\mathrm{qis}^{-1}]$——只把拟同构翻转成同构,得到导出范畴(态射成「屋顶」)。
  现代导出函子 $\mathbf{LF}:D^-(\mathcal A)\to D^-(\mathcal B)$ 由「逐对象取分解再施 $F$」给出,$R^nF=H^n(\mathbf{RF})$。
  **Rotman 2nd ed 增量**:作为「引论」温和引入(Weibel Ch10 更浓缩),适合作导出范畴的入门跳板。
  导出范畴的现代意义:它让 $Rf_*$、$\mathbf Lf^*$、Serre/Grothendieck 对偶有了统一舞台,
  是 Hartshorne 代数几何、表示论、数学物理(D-模、凝集态数学)的底层框架——读完 Rotman Ch8 即可衔接。

- **飞腾锚点**:**TLB 4.81×[E04]** —— Verdier 局部化是「寻址重构」:不搬数据,只改「哪些态射算同构」的地址表(翻转拟同构)。
  🟢事实:导出范畴态射是屋顶 $X\xleftarrow{\mathrm{qis}}Z\to Y$,像 TLB 命中——经中间对象 $Z$ 重定向访问,避免每对象显式存全部分解。
  🟡类比:导出范畴像把所有同伦等价复形「合并寻址」,只保留同调这一不变量——高阶抽象的统一寻址层。

- **关键定理**:**Verdier 局部化 + 导出范畴**。
  $$D(\mathcal A)=K(\mathcal A)\big[\mathrm{qis}^{-1}\big],$$
  短正合 $0\to X\to Y\to Z\to 0$ 在 $D(\mathcal A)$ 中成 distinguished triangle $X\to Y\to Z\to X[1]$。

- **自测**:在 $D(\mathcal{Ab})$ 中,证明 $0\to\mathbb Z\xrightarrow{\times2}\mathbb Z\to\mathbb Z/2\to0$ 给出 distinguished triangle
  $\mathbb Z\xrightarrow{\times2}\mathbb Z\to\mathbb Z/2\to\mathbb Z[1]$,并说明 $\mathbb Z/2\cong\mathrm{Cone}(\times2)$。

---

### 第 9 章 · 层(Sheaf)上同调

- **核心**:Rotman 聚焦模层同调代数,层上同调是其**自然下游出口**(对接 Hartshorne/Iversen),此处作为「读 Rotman 后的应用落地」补充。
  (注:Rotman 本体不设层论专章,本章是把 Rotman 的导出函子语言投射到层论——是读完 Rotman 的「出口」而非「原书内容」。)
  拓扑空间 $X$ 上 Abel 层 $\mathcal F$;**Grothendieck 的洞见**:层上同调 $H^n(X,\mathcal F)=R^n\Gamma(\mathcal F)$,
  其中 $\Gamma(\mathcal F)=\mathcal F(X)$ 为整体截面函子(左正合)。用内射分解计算。
  **Čech 上同调** $\check H^n(\mathfrak U,\mathcal F)$ 对开覆盖 $\mathfrak U$ 用交集 $\mathcal F(U_{i_0\cdots i_n})$ 构复形,
  通过 **Čech-导出谱序列** $\check H^p(\mathfrak U,R^q\Gamma)\Rightarrow H^{p+q}(X,\mathcal F)$ 与导出上同调比较。
  里程碑:**Grothendieck 消没定理**——仿射概形 $X=\mathrm{Spec}\,A$ 上拟凝聚层 $\tilde M$ 有 $H^{n>0}(X,\tilde M)=0$。

- **飞腾锚点**:**GEMM 9.45G[Lab05]** —— Čech 复形对开覆盖的多重交集 $\mathcal F(U_{i_0\cdots i_n})$ 是双指标嵌套阵列,与双复形高维吞吐同构。
  🟢事实:加细覆盖取正向极限时,Čech 收敛于导出上同调,实现上是嵌套矩阵核/像求商的高维运算。
  🟡类比:层上同调像「从局部截面拼全局」,缺口(非零 $H^n$)度量局部到全局的「拼接障碍」。

- **关键定理**:**Grothendieck 消没定理(仿射)** + **Leray 谱序列**。
  $$X=\mathrm{Spec}\,A,\ \mathcal F=\tilde M\ \Rightarrow\ H^{n>0}(X,\tilde M)=0;\qquad
  E_2^{p,q}=H^p(X,R^qf_*\mathcal F)\Rightarrow H^{p+q}(Y,f_*\mathcal F).$$

- **自测**:说明为何 $H^n(\mathrm{Spec}\,A,\tilde M)=0$($n>0$)等价于「拟凝聚层由整体截面生成」的局部性质可全局化。
  (提示:用 Čech 对仿射开覆盖收拢,$E_2$ 页 $R^q\Gamma=0$($q>0$)。)

---

### 第 10 章 · 专题与附录

- **核心**:Rotman 的**附录**是「图追踪技术」的训练场——同调代数最频繁的证明工具。
  **五引理**(five lemma):正合交换图中若四个外围同构,则中间也同构;
  **九引理 / 3×3 引理**:三行三列的正合交换图,两行(列)短正合 $\Rightarrow$ 第三行(列)也短正合;
  **图追踪**(diagram chasing)是这一切的通用方法。这些是 Weibel 默认你会、Rotman 详加操练的「基本功」。
  延伸专题指向:代数 $K$-理论(用导出范畴刻画投射模类群 $K_0$)、étale 上同调、同伦代数的现代发展(∞-范畴)。
  图追踪是同调代数的「肌肉」——所有长正合序列的构造最终都归结为在交换图里逐元素追来源与去向。
  这一章把全书从「计算」收束回「方法论的统一」:所有同调理论都由「分解 + 导出函子 + 长正合序列」三件套驱动。

- **飞腾锚点**:**matmul 15×[V03]** —— 图追踪的本质是「在核/像/余核之间反复追」,每一步是一次矩阵式的核/像定位运算。
  🟢事实:3×3 引理的实现是把九个对象排成矩阵,沿行/列做正合性检验,与分块矩阵运算同构;
  🟡类比:图追踪像「在正合交换图里走迷宫」,每一步用正合性($\ker=\mathrm{im}$)排除死路,直到锁定目标同构。

- **关键定理**:**3×3 引理(九引理)**。交换图三行三列,若三列均为短正合序列且上下两行短正合,
  则中间一行也短正合;$0$ 在四角时,中间正合性由图追踪逐元素完成。

- **自测**:用五引理证明:若 $0\to A'\to A\to A''\to0$ 与 $0\to B'\to B\to B''\to0$ 正合,且 $A'\to B',A\to B,A''\to B''$ 均同构,则(无显式 $A'\to B'$ 时)中间亦然。
  (提示:画交换图,对 $0\to A'\to A\to A''\to0$ 与 $0\to B'\to B\to B''\to0$ 施五引理。)

---

## §9 全书思想主线(约 200 字)

Rotman 的 10 章是一条「先夯实工具,再展开应用,最后收束于方法论」的友好上升线。
**第 1 章预备**(范畴/模/Hom/张量/特殊模/蛇引理)把 Weibel 默认你会的弹药库全部讲透,这是 Rotman「友好」的根基;
**Tor/Ext**(Ch2)给出旗舰实例,Rotman 的增量是 **Yoneda 的 $n$-扩张描述**,把导出函子与扩张直觉直接对接;
**谱序列**(Ch3)是计算枢纽,Rotman 用逐页手算把抽象收敛变可追踪;
**Ch4–Ch6** 把同调代数撒向群、Lie 代数、结合代数三大应用场,展示「通用语言」威力;
**单纯方法**(Ch7)给链复形一个组合几何模型(Dold-Kan),**导出范畴**(Ch8)是现代视角顶峰——Verdier 把整套理论重构为三角范畴+局部化;
**层上同调**(Ch9)作为下游出口对接代数几何,**附录**(Ch10)用图追踪把全书收束回方法论的统一。
相对 Weibel 的「快进」,Rotman 的关键词是「动机、例子、完整证明、历史注记」。
换言之,Weibel 是「地图」(告诉你全景与终点),Rotman 是「路书」(每段路为什么走、怎么走都写清)。
对已读 Weibel 的读者,Rotman 的最大价值不在「新知识」,而在把 Weibel 留下的三类缺口补上:
(a)范畴/模层预备的细节空洞(Ch1)、(b)Ext 的几何直觉缺口(Yoneda 扩张,Ch2)、(c)图追踪的肌肉记忆(Ch10)。
读完两书,同调代数的「分解—导出—长正合序列」三件套就从「会用」升级到「会讲清为什么」;
而导出范畴(Ch8)与层上同调(Ch9)则把视野推到现代代数几何的门口,为 Hartshorne 备好底层语言。
具体路线建议:Ch1(预备)精读不跳、Ch2(Tor/Ext)重点抓 Yoneda、Ch3–Ch6 与 Weibel 交叉速读、Ch7–Ch8(单纯+导出范畴)精读、Ch9–Ch10 按需(接 Hartshorne 时回看)。

---

## §10 与本仓库其他笔记的交叉引用

- **Weibel《同调代数》**:Rotman 是 Weibel 的「友好对照版」。两书覆盖同源,但 Rotman 把 Weibel 跳过的范畴/模/特殊模预备
  (Weibel 假设你会)在 Ch1 详讲;Tor/Ext 处 Rotman 多了 **Yoneda $n$-扩张**视角;导出范畴处 Weibel Ch10 更浓缩、Rotman 更温和。
  已读 Weibel 者,读 Rotman 的价值在于「查漏补缺 + 建立 Yoneda 直觉 + 补图追踪基本功」。
  实用读法:以 Weibel 为主干快速通读,遇卡点立即切到 Rotman 对应章节看详细推导与例子,
  最后用 Rotman Ch2 的 Yoneda 扩张与 Ch10 的图追踪习题做收尾巩固。
- **Mac Lane《范畴论》(GTM5)**:Rotman Ch1 的范畴/伴随/极限直接建在 Mac Lane 之上。Mac Lane 第 12 章 Abel 范畴是 Rotman 的工作台;
  导出范畴的三角结构是「Abel 范畴+同伦」的范畴化。读 Rotman 前应有 Mac Lane 第 IV–XII 章打底。
- **Eisenbud《交换代数》(GTM150)**:正则环、深度、合冲在 Eisenbud 已建;Rotman Tor/Ext 把 Eisenbud 的「同调维数」直觉接到
  导出函子——Serre 定理(正则 $\Leftrightarrow$ $\mathrm{gl.dim}=\mathrm{Krull.dim}$)是两书最直接交汇。
- **Hartshorne《代数几何》**:层上同调 $H^i(X,\mathcal F)$、$\mathbf Rf_*$、Serre 对偶,全部是 Rotman Ch8/Ch9 的应用;
  读 Hartshorne III 章前,Rotman Ch8(导出范畴)+ Ch9(层上同调)是必备弹药。Grothendieck 消没定理是 III.3 的基石。
- **Hatcher《代数拓扑》**:Rotman Ch7 单纯方法(Dold-Kan、单纯集几何实现)与 Hatcher 的奇异同调、CW 复形同伦论同源;
  导出范畴 Ch8 的三角结构是代数拓扑「正合序列→同伦纤维序列」的代数化镜像。两者互为几何/代数两面。
- **AI 锚点(飞腾 D3000M 映射)**:
  - **分解=最佳逼近正交化**(投射/内射分解逐层消残差,Ch1 Schmidt);
  - **Ext=参数扩展的分类**($\mathrm{Ext}^1$ 索引所有扩张,Ch2 matmul;Yoneda 把等式拆成长度 $n$ 的链);
  - **谱序列=多尺度分析**(逐页逼近如小波,Ch3 GEMM;Ch9 层上同调用同锚,Čech 嵌套阵列);
  - **导出范畴=高阶抽象统一寻址**(Verdier 局部化只翻转拟同构如 TLB 地址重构,Ch8);
  - **图追踪=核/像反复定位运算**(3×3 引理如分块矩阵正合性检验,Ch10 matmul)。
