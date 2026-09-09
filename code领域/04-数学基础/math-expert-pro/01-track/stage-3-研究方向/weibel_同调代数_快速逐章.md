# Weibel《同调代数引论》· 快速逐章精读

> 基于原书:`An Introduction to Homological Algebra` (Charles A. Weibel, 1988, Cambridge) / 读于:2026-07-02
> 定位:**现代同调代数标准教材**,从链复形到导出范畴,高阶数学的通用胶水。
> 本文为**快速逐章精读**,每章 1 个飞腾锚点 + 1 个关键定理 + 1 道自测题。

---

## §0 引言:Weibel 同调代数是什么,为什么读它

Charles A. Weibel 的《An Introduction to Homological Algebra》(1988, Cambridge)是**现代同调代数的标准教材**,
覆盖从链复形(chain complex)到导出范畴(derived category)的全谱系,共 10 章。
同调代数起源于 1940 年代的代数拓扑——把拓扑空间的「洞」翻译成 Abel 群的同调群;
随后由 Cartan-Eilenberg(1956)、Grothendieck 学校发展成代数拓扑的**代数化**,
成为交换代数、代数几何(层上同调)、表示论、Lie 代数上同调、群上同调的**共同语言**。

为什么读它?本仓库已精读 Dummit/Artin 抽象代数(含正合序列基础)、Atiyah-MacDonald 交换代数(预告了 $\mathrm{Ext}/\mathrm{Tor}$)、
Mac Lane 范畴论(含 Abel 范畴)。Weibel 是**把这些工具系统化、推向谱序列与导出范畴**的进阶。
它的核心使命:把「不保持正合的函子」(如张量积左正合不右正合、$\mathrm{Hom}$ 右正合不左正合)补全成**导出函子**,
让断裂的正合序列重新接上。同调代数是「高阶数学的通用胶水」——
导出范畴更是现代代数几何(Hartshorne)、表示论、甚至数学物理(D-模、凝集态数学)的底层框架。
前置:Mac Lane 范畴论(本仓库已做)、Abel 范畴、抽象代数。

对比四本主流教材:

| 书 | 风格 | 严格性 | 适合谁 |
|---|---|---|---|
| Weibel《同调代数引论》(1988) | 现代标准,全谱系,10 章从复形到导出范畴,例子丰富 | 严谨,习题多,密度高 | 有范畴论/抽代基础的进阶者 |
| Hilton-Stammbach(GTM4 经典) | 经典老教材,群上同调与同调详尽,证明细致 | 严谨偏古典 | 偏群论背景、想慢读经典的读者 |
| Gelfand-Manin《方法》 | 几何观点,以导出范畴为纲,现代但抽象 | 现代严格,跳跃大 | 几何/代数几何方向的研究者 |
| 东北师大/北大讲义(中文数据) | 中文,循序渐进,计算导向 | 适中,例题多 | 中文入门、想先算后抽象者 |

---

## §1 全书 10 章骨架一览(飞腾锚点分布)

| 章 | 标题 | 核心概念 | 飞腾锚点 |
|---|---|---|---|
| 1 | Chain Complexes 链复形 | 链复形/链同伦/拟同构/长正合序列 | Iron Law<2%[Lab00] ⭐ |
| 2 | Derived Functors 导出函子 | 蛇引理/马蹄铁/$L_nF$·$R^nF$/δ-函子 | 分支预测[Lab02] |
| 3 | Tor 与 Ext | $\mathrm{Tor}_n$/$\mathrm{Ext}^n$/扩张分类/Künneth | matmul 15×[V03] ⭐ |
| 4 | Homological Dimension 同调维度 | 投射/整体维数/正则环/合冲定理 | Schmidt 正交化 |
| 5 | Spectral Sequences 谱序列 | $E^r$/$d_r$/收敛/Grothendieck 谱序列 | GEMM 9.45G[Lab05] |
| 6 | Group Cohomology 群上同调 | $H^n(G,M)$/Bar 分解/转移/周期 | UDOT 16.9×[E05] |
| 7 | Lie Algebra Homology Lie 代数同调 | $U(\mathfrak g)$/Chevalley-Eilenberg/Whitehead | FP16 3.81×[L01] |
| 8 | Hochschild 与循环同调 | $HH^n$/$HC_n$/Connes 算子 $B$ | Iron Law<2%[Lab00] |
| 9 | Simplicial Methods 单纯方法 | 单纯对象/Dold-Kan/几何实现 | 分支预测[Lab02] |
| 10 | Derived Categories 导出范畴 ⭐⭐ | 三角范畴/Verdier 局部化/$Rf_*$/$Lf^*$ | TLB 4.81×[E04] ⭐ |

---

### 第 1 章 · Chain Complexes(链复形)

- **核心**:全书的原子单位是**链复形**——一串 Abel 群(或 $R$-模)配上满足 $d^2=0$ 的微分。
  形如 $C_\bullet:\ \cdots\to C_{n+1}\xrightarrow{d_{n+1}} C_n\xrightarrow{d_n} C_{n-1}\to\cdots$,核心条件 $d_n\circ d_{n+1}=0$ 保证 $\mathrm{im}\,d_{n+1}\subseteq\ker d_n$。
  **同调群** $H_n(C_\bullet)=\ker d_n/\mathrm{im}\,d_{n+1}$ 度量「洞」:链(闭)但不是边界(恰当)的元素。
  链映射 $f:C_\bullet\to D_\bullet$ 诱导同调映射 $H_n(f)$;**链同伦** $f\simeq g$ 是比同构更弱的等价,它保证 $H_n(f)=H_n(g)$。
  短正合序列 $0\to A_\bullet\to B_\bullet\to C_\bullet\to 0$ 经蛇引理给出**长正合同调序列**;
  **拟同构**(quasi-isomorphism)指在同调层诱导同构的链映射,是后续导出范畴「只翻转它」的核心。

- **飞腾锚点**:**Iron Law<2%[Lab00]** —— 正合性 $\ker d_n=\mathrm{im}\,d_{n+1}$ 是同调代数的「误差为零」铁律。
  🟢事实:数值实现复形时,浮点误差会让 $\ker\approx\mathrm{im}$ 但不相等,正合性检验必须设容差(类 Iron Law 的 $<2\%$);
  $d^2=0$ 在代码里要刻意保证(稀疏矩阵乘两次归零)。🟡类比:同调群 $H_n$ 是「铁律偏差」的可计算量化——
  偏差为零($H_n=0$)即正合(无洞),偏差非零即「洞」。

- **关键定理**:**长正合同调序列**。短正合的复形序列
  $0\to A_\bullet\to B_\bullet\to C_\bullet\to 0$ 诱导
  $$\cdots\to H_n(A)\xrightarrow{H_n(i)} H_n(B)\xrightarrow{H_n(p)} H_n(C)\xrightarrow{\partial} H_{n-1}(A)\to\cdots$$
  其中连接同态 $\partial$ 由「追图(snake)」构造。这是同调代数最频繁出现的工具。

- **自测**:计算复形 $\cdots\to 0\to \mathbb Z\xrightarrow{\times 2}\mathbb Z\xrightarrow{\pi}\mathbb Z/2\to 0$ 的各阶同调。
  (提示:$\ker(\times 2)=0$, $\mathrm{im}=2\mathbb Z$。)

---

### 第 2 章 · Derived Functors(导出函子)

- **核心**:正合函子保持短正合序列,但大多数有用函子(如 $-\otimes N$ 右正合不左正合、$\mathrm{Hom}(M,-)$ 左正合不右正合)会「漏掉」信息。
  导出函子的任务:用**分解**补回漏掉的部分。
  **投射分解**(projective resolution)$\cdots\to P_1\to P_0\to M\to 0$($P_i$ 投射)把模「抬到」正合的投射层;
  **内射分解**(injective resolution)$0\to N\to I^0\to I^1\to\cdots$($I^i$ 内射)是镜像。
  **蛇引理**(snake lemma)把核/余核串成正合六项序列,**马蹄铁引理**(horseshoe)保证两个分解能拼成第三个。
  右正合函子 $F$ 用投射分解定义**左导出** $L_nF$;左正合函子 $G$ 用内射分解定义**右导出** $R^nG$。
  它们自动给长正合序列。**δ-函子**(Cartan-Eilenberg)把这套性质公理化,成为「保持长正合序列的函子族」的抽象刻画。

- **飞腾锚点**:**分支预测[Lab02]** —— 蛇引理的本质是「在 $\ker$ 与 $\mathrm{coker}$ 两个分支间切换」。
  🟡类比:连接同态 $\partial$ 像 CPU 分支预测——给定 $c\in C$,先「预测」它来自 $B$ 的原像(抬一层),再「跳转」到 $A$ 的核(降一层),
  两步分支切换构成 $\partial$。Grothendieck 把这种分支逻辑抽象成 δ-函子的「机器」。

- **关键定理**:**导出函子的长正合序列**。若 $0\to M'\to M\to M''\to 0$ 正合且 $F$ 右正合,则
  $$\cdots\to L_nF(M')\to L_nF(M)\to L_nF(M'')\xrightarrow{\delta} L_{n-1}F(M')\to\cdots\to L_0F(M'')\to 0$$
  即 $F$「丢失的正合性」被 $L_nF$ 系统地补回。

- **自测**:设 $F=-\otimes_\mathbb Z\mathbb Z/2$,取 $M=\mathbb Z/4$ 的投射分解 $0\to\mathbb Z\xrightarrow{\times 4}\mathbb Z\to\mathbb Z/4\to 0$,
  计算 $L_nF(\mathbb Z/4)$($n=0,1$)。

---

### 第 3 章 · Tor 与 Ext

- **核心**:最重要的两个导出函子有了专名。
  **$\mathrm{Tor}_n^R(M,N)=L_n(-\otimes_R N)(M)$**——张量积的左导出,度量张量「撕裂」模的程度;
  **$\mathrm{Ext}_R^n(M,N)=R^n\mathrm{Hom}(M,-)(N)$**——$\mathrm{Hom}$ 的右导出。
  在主理想整区(PID)上,$\mathrm{Tor}_n=0$($n\ge 2$),$\mathrm{Ext}^n=0$($n\ge 2$),只剩 $n=0,1$ 两层。
  最深刻的结论:**$\mathrm{Ext}^1_R(M,N)$ 一一对应于短正合扩张 $0\to N\to X\to M\to 0$ 的等价类**(Baer),
  把「模的扩张」这个几何直觉变成可计算的群。
  **Künneth 公式**把两个复形的张量积的同调,分解为各自同调的张量积加上 $\mathrm{Tor}$ 修正项。

- **飞腾锚点**:**matmul 15×[V03]** —— $\mathrm{Ext}$ 的计算本质是「把短正合序列跑成长正合序列」的矩阵运算。
  🟢事实:取投射分解后,$\mathrm{Ext}^n_R(M,N)$ 是复形 $\mathrm{Hom}(P_\bullet,N)$ 的上同调,
  实现上是链式矩阵的核/像求商——与张量核(matmul)流水线同构。
  🟡类比:$\mathrm{Ext}^1$ 分类扩张,像参数搜索空间里的「等价类索引」。

- **关键定理**:**$\mathrm{Ext}^1$ 分类扩张**。
  $$\mathrm{Ext}^1_R(M,N)\ \longleftrightarrow\ \{\text{扩张 }0\to N\to X\to M\to 0\}/_{\text{等价}}$$
  特别 $\mathrm{Ext}^1_R(M,N)=0$ $\Leftrightarrow$ 所有扩张可裂($X\cong N\oplus M$)。

- **自测**:计算 $\mathrm{Ext}^1_\mathbb Z(\mathbb Z/2,\mathbb Z/2)$,并列出 $\mathbb Z/2$ 被 $\mathbb Z/2$ 的所有扩张。
  (答案:$\cong\mathbb Z/2$,扩张为 $\mathbb Z/2\oplus\mathbb Z/2$ 与 $\mathbb Z/4$ 两类。)

---

### 第 4 章 · Homological Dimension(同调维度)

- **核心**:用「最短分解长度」给环和模定一个数值不变量。
  **投射维数** $\mathrm{pd}(M)$=$M$ 最短投射分解的长度;$\mathrm{pd}(M)=0$ $\Leftrightarrow$ $M$ 投射。
  类似有**内射维数** $\mathrm{id}$、**平坦维数** $\mathrm{fd}$。
  取上确界得环的**整体维数**(global dimension)$\mathrm{gl.dim}\,R=\sup_M\mathrm{pd}(M)$。
  PID(如 $\mathbb Z$、$k[x]$)的 $\mathrm{gl.dim}=1$。
  里程碑:**正则环**(regular ring)的刻画——Serre 定理:$R$ 正则 $\Leftrightarrow$ $\mathrm{gl.dim}\,R<\infty$ $\Leftrightarrow$ $\mathrm{gl.dim}\,R=\mathrm{Krull.dim}\,R$。
  **Hilbert 合冲定理**(syzygy):多项式环 $k[x_1,\dots,x_n]$ 的 $\mathrm{gl.dim}=n$。
  这把「几何维数」(Krull 维数)与「代数复杂度」(同调维数)划了等号,是代数几何的基石。

- **飞腾锚点**:**Schmidt 正交化** —— 投射/内射分解都是「最佳逼近」:投射模像在已知基底上做投影,逐层消除「非正交残差」(syzygy,即合冲)。
  🟡类比:每一次消解(syzygy 计算)像 Schmidt 正交化剥离一个非正交分量,直到残差为零(自由/投射),分解终止;
  分解长度即「需要几轮正交化」,即同调维数。

- **关键定理**:**Hilbert 合冲定理 + Serre 定理**。
  $$\mathrm{gl.dim}\,k[x_1,\dots,x_n]=n,\qquad R\text{ 正则}\Leftrightarrow\mathrm{gl.dim}\,R=\mathrm{Krull.dim}\,R.$$

- **自测**:求 $\mathrm{pd}_\mathbb Z(\mathbb Z/2)$ 与 $\mathrm{gl.dim}\,\mathbb Z$。
  (答案:$\mathrm{pd}=1$(分解 $0\to\mathbb Z\xrightarrow{\times2}\mathbb Z\to\mathbb Z/2\to 0$),$\mathrm{gl.dim}\,\mathbb Z=1$。)

---

### 第 5 章 · Spectral Sequences(谱序列)

- **核心**:全书枢纽。谱序列是「逐页逼近同调」的算法,把无法一次算完的复杂双复形分解成一族页面。
  一个谱序列是双分次模族 $E^r_{p,q}$($r=2,3,\dots$)配双阶微分 $d_r:E^r_{p,q}\to E^r_{p-r,q+r-1}$,满足 $d_r^2=0$,
  下一页 $E^{r+1}=H(E^r,d_r)$。若某页后 $d_r=0$,序列**收拢**(collapse)。
  它**收敛**于某个滤过目标的关联分次:$E^\infty_{p,q}\cong \mathrm{gr}_p H_{p+q}$。
  两种典型收拢:**行收拢**(水平 $d_r$ 先死)与**列收拢**(竖直)。
  最有用的是 **Grothendieck 谱序列**:函子复合 $G\circ F$ 的导出 $= R(G\circ F)$ 由 $R^pG\circ R^qF$ 的 $E_2$ 页逼近,
  $$E_2^{p,q}=R^pG(R^qF(M))\ \Rightarrow\ R^{p+q}(GF)(M).$$
  纤维化(fibration)的 Leray-Serre 谱序列是其拓扑版本。

- **飞腾锚点**:**GEMM 9.45G[Lab05]** —— 谱序列页 $E^r_{p,q}$ 是双指标二维阵列,每一页是一次「高维吞吐」的全阵运算。
  🟢事实:$E^{r+1}$ 由 $E^r$ 的同调给出,实现上是分块矩阵的核/像求商,与高维 GEMM 吞吐同构。
  🟡类比:谱序列像多尺度分析(小波),先粗(低 $r$)后细(高 $r$),逐页修正直到收敛——收敛误差随 $r$ 递减(配合 Iron Law<2%)。

- **关键定理**:**Grothendieck 谱序列**。
  $$E_2^{p,q}=R^pG\big(R^qF(M)\big)\ \Longrightarrow\ R^{p+q}(G\circ F)(M).$$
  当 $R^qF(M)$ 对 $G$ 是 $G$-无环时,序列在第 2 页退化,得 $R^n(GF)\cong G(R^nF)$。

- **自测**:写出 Leray-Serre 谱序列的 $E^2$ 页 $E^2_{p,q}=H_p(B;H_q(F))\Rightarrow H_{p+q}(E)$,并说明纤维化 $F\to E\to B$ 中 $E^2$ 页的含义。

---

### 第 6 章 · Group Cohomology and Homology(群上同调与同调)

- **核心**:把群 $G$ 看作范畴,群同调是同调代数在「一个对象」的范畴上的特化。
  设 $M$ 是 $G$-模(即 $\mathbb ZG$-模)。定义
  **群上同调** $H^n(G,M)=\mathrm{Ext}^n_{\mathbb ZG}(\mathbb Z,M)$、**群同调** $H_n(G,M)=\mathrm{Tor}^{\mathbb Z}_n(\mathbb Z,M)$($\mathbb Z$ 取平凡作用)。
  **Bar 分解**(bar resolution)给出标准自由 $\mathbb ZG$-分解 $0\to\mathbb Z\to\mathbb{ZG}\to\cdots$,$n$ 阶基为 $[g_1|\dots|g_n]$,
  把抽象的 $\mathrm{Ext}$ 变成可写的上链复形。
  群的扩张 $0\to M\to E\to G\to 1$ 由 $H^2(G,M)$ 分类;$H^1(G,M)=\mathrm{Der}(G,M)/\mathrm{Inn}$ 是交叉同态。
  **转移映射**(transfer)联系子群;有限群的 **Tate 上同调**有周期性 $\hat H^n\cong\hat H^{n+h}$。

- **飞腾锚点**:**UDOT 16.9×[E05]** —— Bar 分解的上链是「字的累加」:$C^n(G,M)$ 的元素是 $G^n\to M$ 的函数,微分是对群元的嵌套求和。
  🟢事实:微分类似点积累加(UDOT),对每个 $[g_1|\dots|g_n]$ 做 $n+1$ 项交错和;
  🟡类比:Bar 分解像「把群元素的乘法历史编码成可累加的字」,上同调是这些字循环求和的「闭合度」。

- **关键定理**:**$H^n(G,M)\cong\mathrm{Ext}^n_{\mathbb ZG}(\mathbb Z,M)$**,且群扩张由 $H^2$ 分类。
  特别 $H^2(G,M)=0$ $\Leftrightarrow$ 所有扩张 $1\to M\to E\to G\to 1$ 可裂。

- **自测**:计算 $H^n(\mathbb Z/2,\mathbb Z)$(平凡作用)与 $H^n(\mathbb Z,\mathbb Z)$。
  (答案:前者 $H^{2k}=\mathbb Z/2\ (k\ge1)$,$H^{2k+1}=0$,$H^0=\mathbb Z$;后者 $H^0=\mathbb Z$,$H^1=\mathbb Z$,$H^{n\ge2}=0$。)

---

### 第 7 章 · Lie Algebra Homology(Lie 代数同调)

- **核心**:域 $k$ 上 Lie 代数 $\mathfrak g$ 的同调,通过**泛包络代数** $U(\mathfrak g)$ 归约到结合代数。
  PBW 定理:$U(\mathfrak g)\cong S(\mathfrak g)$(对称代数)作为滤过向量空间。
  定义 $H_n(\mathfrak g,M)=\mathrm{Tor}^{U(\mathfrak g)}_n(k,M)$、$H^n(\mathfrak g,M)=\mathrm{Ext}^n_{U(\mathfrak g)}(k,M)$。
  **Chevalley-Eilenberg 复形**给出显式计算:用外代数 $\wedge^n\mathfrak g^*$ 做上链,微分由 Lie 括号诱导。
  半单 Lie 代数的标志性结果——**Whitehead 引理**:$\mathfrak g$ 半单 $\Rightarrow$ $H^1(\mathfrak g,M)=H^2(\mathfrak g,M)=0$($M$ 有限维非平凡),
  由此推出 Levi 分解与 Weyl 完全可约定理。这是 Lie 理论与同调代数最美的交汇。

- **飞腾锚点**:**FP16 3.81×[L01]** —— Chevalley-Eilenberg 复形的微分是 $\wedge\mathfrak g$ 上的交替双线性运算(Lie 括号的线性化)。
  🟡类比:半单情形上同调「接近正合」($H^1=H^2=0$),像浮点精度下的「近似零残差」;
  🟢事实:数值实现 Lie 代数上同调时,结构常数 $c_{ij}^k$ 的反对称求和对精度敏感,需类 FP16 的容差控制。

- **关键定理**:**Whitehead 引理**。$\mathfrak g$ 半单、$M$ 有限维非平凡 $\Rightarrow$
  $$H^1(\mathfrak g,M)=0,\qquad H^2(\mathfrak g,M)=0.$$
  推论(Weyl):有限维 $\mathfrak g$-模完全可约。

- **自测**:对 $\mathfrak g=\mathfrak{sl}_2(k)$(char $k\ne 2$),用 Chevalley-Eilenberg 复形计算 $H_n(\mathfrak{sl}_2,k)$ 的低阶项。
  (答案:$H_0=k$,$H_1=H_2=0$(半单),$H_3=k$。)

---

### 第 8 章 · Hochschild and Cyclic Homology(Hochschild 与循环同调)

- **核心**:结合 $k$-代数 $A$ 的同调理论。
  **Hochschild 上同调** $HH^n(A,M)=\mathrm{Ext}^n_{A\otimes A^{op}}(A,M)$,用标准 bar 复形 $C^n(A,M)=\mathrm{Hom}_k(A^{\otimes n},M)$;
  取 $M=A$ 得 $HH^n(A,A)$,控制 $A$ 的形变(Gerstenhaber,$HH^2$=无穷小形变,$HH^3$=障碍)。
  **循环同调** $HC_n(A)$ 由 Connes 引入,在 Hochschild 复形上叠加循环对称性,由 **Connes 算子 $B$**($B:HC_n\to HC_{n-1}$,度 $-1$)
  与 Hochschild 边界 $b$ 构成 $(b,B)$-双复形。Connes 精确序列连接两者:
  $\cdots\to HH_n\xrightarrow{B}HC_{n-1}\to HC_{n+1}\to HH_{n+1}\to\cdots$。
  循环同调与非交换几何(Connes)、$K$-理论、拓扑空间奇异同调(de Rham 比较)深刻相关。

- **飞腾锚点**:**Iron Law<2%[Lab00]** —— 循环同调的核心是 Connes 算子 $B$ 与 Hochschild 边界 $b$ 满足 $B^2=b^2=Bb+bB=0$,
  这是双复形的「双重正合性」铁律。🟢事实:$(b,B)$-双复形的总复形正合性必须严格(误差为零),
  类似谱序列收敛的误差递减——任何数值扰动都会破坏 $HC_n$ 的周期性结构。

- **关键定理**:**Connes 精确序列(SBI 序列)**。
  $$\cdots\to HH_n(A)\xrightarrow{I}HC_n(A)\xrightarrow{S}HC_{n-2}(A)\xrightarrow{B}HH_{n-1}(A)\to\cdots$$
  它把循环同调层层「降维」到 Hochschild 同调,$S$ 为周期移位算子。

- **自测**:计算 $HH_n(k[x])$ 与 $HC_n(k[x])$。
  (答案:$HH_0=k[x]$,$HH_1=k[x]\cdot dx$,$HH_{n\ge2}=0$;$HC_{2k}\cong k[x]$, $HC_{2k+1}\cong k[x]\,dx$。)

---

### 第 9 · Simplicial Methods in Homological Algebra(同调代数的单纯方法)

- **核心**:用**单纯对象**(simplicial object)给链复形一个「组合几何」的模型。
  单纯 $R$-模是反变函子 $X:\boldsymbol\Delta^{op}\to R\text{-Mod}$,带面映射 $d_i:X_n\to X_{n-1}$($0\le i\le n$)与退化映射 $s_i:X_n\to X_{n+1}$,
  满足单纯恒等式 $d_id_j=d_{j-1}d_i$($i<j$)等。
  **Dold-Kan 对应**是核心定理:**单纯 $R$-模范畴 $\cong$ 非负分次链复形范畴**——
  任一链复形都可唯一(同伦意义下)提升为单纯模,反之亦然。
  这让链复形获得「几何实现」:单纯集(simplicial set)的几何实现是 CW 复形,是同伦论的组合模型。
  单纯方法也是高阶范畴论(∞-范畴、单纯 ∞-群胚)的现代表达基础。

- **飞腾锚点**:**分支预测[Lab02]** —— 单纯对象的面映射 $d_i$、退化映射 $s_i$ 是一组「带下标分支」的操作,
  需按 $i<j$ 等条件选择不同分支(单纯恒等式)。
  🟡类比:Dold-Kan 对应像「把链复形的线性流水线展开成带分支的单纯网格」,
  每个面映射是一次条件分支;反过来链复形是单纯网格的「规范化(去分支)投影」。

- **关键定理**:**Dold-Kan 对应**。正规化函子 $N$ 给出范畴等价
  $$N:\{\text{单纯 }R\text{-模}\}\ \xrightarrow{\ \sim\ }\ \{\text{非负分次链复形}\},\qquad H_*(X)\cong H_*(N(X)).$$

- **自测**:写出对应于链复形 $\cdots0\to M\xrightarrow{0}M\to0$(仅在 $0,1$ 处非零,$d_1=0$)的单纯 $R$-模的前三层 $X_0,X_1,X_2$。
  (提示:用 $N$ 的逆——$X_n=\bigoplus_{[n]\twoheadrightarrow[k]}N_k$。)

---

### 第 10 章 · Derived Categories(导出范畴)⭐⭐

- **核心**:全书的现代顶峰,也是 Grothendieck 学派(Verdier,1963)对同调代数的重构。
  传统导出函子(第 2 章)用 $\delta$-函子+长正合序列,「笨重」;导出范畴把这套提升为范畴语言。
  起点:**三角范畴**(triangulated category)——带平移函子 $[1]$ 与「 distinguished triangles」 $X\to Y\to Z\to X[1]$,满足四条公理(TR1–TR4),
  是正合三角形(短正合序列)的范畴化。
  链复形的**同伦范畴** $K(\mathcal A)$(同伦类为态射)天然三角。
  **Verdier 局部化**:$D(\mathcal A)=K(\mathcal A)[\mathrm{qis}^{-1}]$——在 $K(\mathcal A)$ 里「只把拟同构翻转成同构」,
  得到**导出范畴** $D(\mathcal A)$。这是局部化,不是商——态射变多(成「屋顶/rooftop」)。
  现代导出函子:$F:\mathcal A\to\mathcal B$ 的导出 $\mathbf LF:D^-(\mathcal A)\to D^-(\mathcal B)$ 由「逐对象取投射分解再施 $F$」给出,
  $R^nF=H^n(\mathbf RF)$。层论里 $Rf_*$、$\mathbf Lf^*$ 是 Grothendieck 对偶定理的舞台。

- **飞腾锚点**:**TLB 4.81×[E04]** —— Verdier 局部化是「寻址重构」:不搬数据,只改「哪些态射算同构」的地址表(翻转拟同构)。
  🟢事实:导出范畴的态射是「屋顶」$X\xleftarrow{\mathrm{qis}}Z\to Y$,像 TLB 命中——通过中间对象 $Z$ 重定向访问,
  避免在每个对象上显式存全部分解(节省「内存」)。
  🟡类比:导出范畴像把所有同伦等价的复形「合并寻址」,只保留同调这一不变量——高阶抽象的统一寻址层。

- **关键定理**:**Verdier 局部化 + 导出范畴**。
  $$D(\mathcal A)=K(\mathcal A)\big[\mathrm{qis}^{-1}\big],$$
  且短正合序列 $0\to X\to Y\to Z\to 0$ 在 $D(\mathcal A)$ 中成为 distinguished triangle $X\to Y\to Z\to X[1]$。
  由此导出函子 $\mathbf{RF},\mathbf{LF}$ 是「最优逼近」,自动给长正合序列。

- **自测**:在 $D(\mathcal{Ab})$ 中,证明短正合序列 $0\to\mathbb Z\xrightarrow{\times2}\mathbb Z\to\mathbb Z/2\to 0$ 给出 distinguished triangle
  $\mathbb Z\xrightarrow{\times2}\mathbb Z\to\mathbb Z/2\to\mathbb Z[1]$,并说明 $\mathbb Z/2\cong\mathrm{Cone}(\times2)$。

---

## §9 全书思想主线(约 200 字)

Weibel 的 10 章是一条清晰的上升螺旋:**链复形(Ch1)**给出原子结构 $d^2=0$;
**导出函子(Ch2)**把「非正合函子」补全——核心命题是「用分解把断裂的正合性接上」;
**Tor/Ext(Ch3)**是这套机制的两大旗舰实例,$\mathrm{Ext}^1$ 直接分类模的扩张;
**同调维度(Ch4)**把「分解多长」凝成一个数值不变量,在正则环处与 Krull 维数会师;
**谱序列(Ch5)**是全书枢纽的「计算利器」,把不可一次算完的双复形拆成逐页逼近;
**Ch6–Ch8**把同调代数撒向群、Lie 代数、结合代数三大应用场,展示其「通用语言」威力;
**单纯方法(Ch9)**给链复形一个组合几何模型(Dold-Kan);
**导出范畴(Ch10)**是现代视角的顶峰——Verdier 把整套理论重构为三角范畴+局部化,让 Hartshorne 代数几何、
表示论、数学物理有了统一底层。从「具体计算」到「范畴重构」,正是同调代数 70 年的进化轨迹。

---

## §10 与本仓库其他笔记的交叉引用

- **Mac Lane《范畴论》(GTM5)**:Weibel 是 Mac Lane 的下游。Mac Lane 第 12 章的 Abel 范畴、加性范畴是 Weibel 的工作台;
  导出范畴的三角结构是「Abel 范畴+同伦」的范畴化。读 Weibel 前应有 Mac Lane 第 12 章打底。
- **Dummit/Artin 抽象代数**:正合序列、自由/投射/内射模、$R$-模的张量积与 $\mathrm{Hom}$,都在抽代里先见;
  Weibel 把这些「静态」对象升级成「动态」的复形与导出函子。
- **Atiyah-MacDonald 交换代数**:Noether 环、局部化、Krull 维数在 AM 已建;
  Weibel 第 4 章的 Serre 定理把 AM 的「正则局部环」用同调维数重新刻画,是两者最直接交汇。
- **Hartshorne《代数几何》**:层上同调 $H^i(X,\mathcal F)$、$\mathbf Rf_*$、Serre 对偶,全部是 Weibel 第 10 章导出范畴的应用;
  读 Hartshorne III 章前,Weibel Ch2/Ch5/Ch10 是必备弹药。
- **AI 锚点(飞腾 D3000M 映射)**:
  - **同调=数据流图的正合性检测**($\ker=\mathrm{im}$ 的「零误差」校验,Ch1 Iron Law);
  - **Ext=参数扩展的分类**($\mathrm{Ext}^1$ 索引所有扩张,像超参空间的等价类标号,Ch3 matmul);
  - **谱序列=多尺度分析**(逐页逼近,像小波/多分辨率,Ch5 GEMM);
  - **导出范畴=高阶抽象的统一寻址**(Verdier 局部化只翻转拟同构,像 TLB 地址重构,Ch10 TLB);
  - **Tor=张量积的导出=数据融合**(张量积撕裂模,$\mathrm{Tor}$ 度量撕裂程度,像融合时的对齐损失)。
