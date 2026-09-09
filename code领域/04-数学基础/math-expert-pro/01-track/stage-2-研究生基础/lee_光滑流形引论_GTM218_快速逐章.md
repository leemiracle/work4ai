# Lee《光滑流形引论》(GTM218, 2nd Ed) · 快速逐章精读

> 基于原书:`Introduction to Smooth Manifolds` (John M. Lee, GTM218, 2nd ed., Springer, 2012) / 22 章 + 附录 A-D
> 读于:2026-07-02 / stage-2 研究生基础 · 光滑流形主桥梁
> 定位:**最友好的光滑流形入门**,拓扑流形 → 切空间 / 微分形式 / Stokes / de Rham / Lie 群 / Frobenius。
> 本文为**快速逐章精读**(按主题重组为 18 单元),每章 1 个飞腾锚点 🟢/🟡 + 1 个关键定理 + 1 道自测题。
> 前置:本仓库已读 Lee《拓扑流形》GTM202(stage-2)、Petersen《黎曼几何》GTM171、do Carmo、Spivak《流形上的微积分》。

---

## §0 引言:Lee GTM218 是什么,为什么读它

John M. Lee(Washington 大学教授)的《Introduction to Smooth Manifolds》(GTM218,第 2 版 2012)是**最友好的光滑流形入门教材**,也是**自学者首选**。
它承接 Lee 自己的《拓扑流形》(GTM202,已读)——在拓扑流形 $M^n$(Hausdorff + 第二可数 + 局部 $\cong\mathbb R^n$)上叠加**光滑结构**,引入**切空间**、**微分形式**、**Stokes 定理**与 **de Rham 上同调**,
最终抵达 **Lie 群**、**Frobenius 定理**与**辛流形**引论。
Lee 的招牌是「**每一步都有动机**」:每个定义先给直觉再给严格形式,每个定理配完整证明与丰富图示,习题梯度极佳,前置只需多元微积分 + 线性代数 + 点集拓扑。

原书共 **22 章 + 附录 A-D**(拓扑 / 线性代数 / 微积分 / ODE 回顾)。第 2 版大幅重组:把**秩定理**与**流的基本定理**前移以便全书引用,
新增 **Sard 定理与横截性**(原书 ch6)、**度理论**(degree theory)与**接触结构**(contact structures)。
本文按主题**重组为 18 单元**:将原书打散后按「流形结构(ch1-5)→ 丛与形式(ch6-8)→ 积分与同调(ch9-11)→ 高级工具(ch12-18)」的逻辑重新排列,
其中第 18 单元(Morse 理论)**超出本书范围**,作为微分拓扑的延伸指针附上。

本仓库已精读 **Lee《拓扑流形》GTM202**(拓扑地基 + CW 复形 + $\pi_1$ + 曲面分类)、**Spivak《流形上的微积分》**(浓缩版光滑流形,Stokes 为核心)、**Petersen/do Carmo**(黎曼几何下游)。
GTM218 是**光滑流形主线的核心**:它把 Spivak 的浓缩框架展开为完整体系,补上 Spivak 未深入的**子流形理论、Sard 定理、Lie 群、向量丛、Frobenius 定理**,
为 Petersen 黎曼几何提供了严格的流形语言基础。

对比四本主流教材:

| 书 | 风格 | 严格性/侧重 | 适合谁 |
|---|---|---|---|
| **Lee** GTM218(2012) | 最友好,递归式铺垫,证明完整,图示丰富,自洽 | 严谨清晰,覆盖广(子流形/Sard/Lie 群/de Rham/Frobenius) | 自学者、想一站式打通光滑流形的读者 ⭐ |
| **Warner** GTM94(1983) | 经典 GTM,简洁正式,层论(sheaf)视角 | 极严谨,偏代数,含谱序列与层上同调 | 有扎实基础、想快速到 de Rham 的读者 |
| **Spivak** 微分几何卷 1(1979) | 对话式,历史叙事,几何直觉极强 | 较松散,偏哲学,多变量微积分→流形 | 想先抓直觉与历史脉络的读者 |
| **Boothby**(1986/2003) | 实用导向,含黎曼几何基础,篇幅适中 | 适中,偏应用,含联络与曲率 | 工程/物理背景、想同时学黎曼度量的读者 |

> 🟢 事实可作锚点:Stokes 定理、Sard 定理、de Rham 同伦不变性、Frobenius 定理均为严格定理。
> 🟡 类比(「切空间=无穷小探针」「形式=面积元素」)仅供直觉,**绝不在严格证明中引用**。

---

## §1 全书骨架一览(18 单元,飞腾锚点分布)

| 章 | 标题(对应原书) | 核心概念 | 飞腾锚点 |
|---|---|---|---|
| 1 | 拓扑流形回顾(ch1 §1) | $M^n$ 公理/Hausdorff/第二可数/仿紧 | TLB⭐局部坐标 |
| 2 | 光滑流形定义(ch1 §2 + ch2) | 光滑图册/光滑结构/微分同胚/单位分解 | TLB⭐局部坐标 |
| 3 | 切向量与微分(ch3) | 导子/切空间/微分 $df_p$/链式法则/切丛 $TM$ | FP16 |
| 4 | 浸入与嵌入(ch4) | 秩/浸入/淹没/嵌入/常秩定理 | 分支预测 |
| 5 | 子流形(ch5) | 嵌入子流形/正则水平集/切片坐标/带边子流形 | 分支预测 |
| 6 | 切丛与向量丛(ch10) | 向量丛/转移函数/截面/局部标架/拉回丛 | matmul⭐切丛矩阵 |
| 7 | 余切丛与微分形式(ch11 + ch14) | 余切空间/$k$-形式/楔积/外微分 $d^2=0$/拉回 | GEMM⭐张量 |
| 8 | 定向(ch15) | 可定向/体积形式/定向图册 | Schmidt⭐正交标架 |
| 9 | 流形上积分(ch16 前半) | 单位分解/带边流形/边界定向(外法向优先) | UDOT⭐积分 |
| 10 | Stokes 定理(ch16 后半) | $\int_M d\omega=\int_{\partial M}\omega$(统一 FTC/Green/散度) | UDOT⭐积分 ⭐ |
| 11 | de Rham 上同调(ch17-18) | $H^k_{\mathrm{dR}}$/Poincaré/同伦不变性/de Rham 定理 | Iron Law⭐正合 |
| 12 | Sard 定理与横截(ch6) | 临界值测度零/Whitney 嵌入/横截性 | FP16 |
| 13 | Lie 群引论(ch7) | Lie 群/李代数 $\mathfrak g$/指数映射/Lie 子群 | Schmidt⭐正交标架 |
| 14 | 李群作用(ch20) | 轨道/稳定子/齐性空间 $G/H$/商流形定理 | Schmidt⭐正交标架 |
| 15 | 纤维丛(ch10 延伸) | 纤维丛/主丛/Hopf 纤维/标架丛 | Iron Law⭐正合 |
| 16 | 张量场(ch12-13) | $(r,s)$-张量场/黎曼度量/缩并/指标升降 | GEMM⭐张量 |
| 17 | 流与 Frobenius(ch8-9 + ch19) | 积分曲线/流/对合分布/叶状结构 | matmul⭐切丛矩阵 |
| 18 | Morse 与指标(**超出本书**) | Morse 函数/指标/Morse 不等式/CW 复形 | Iron Law⭐正合 |

**三条主线**:(1) **结构主线**——拓扑流形(Ch1)→ 光滑结构(Ch2)→ 切空间(Ch3)→ 子流形(Ch5),逐层加结构;
(2) **积分主线**——形式(Ch7)→ 定向(Ch8)→ 积分(Ch9)→ **Stokes**(Ch10)→ **de Rham**(Ch11),微分流形上的微积分直达拓扑;
(3) **工具主线**——Sard(Ch12)/Lie 群(Ch13-14)/纤维丛(Ch15)/张量(Ch16)/Frobenius(Ch17),为几何与物理提供语言。

---

## 第一篇 · 流形结构

### 第 1 章 · 拓扑流形回顾

- **核心**:快速回顾 GTM202 的拓扑流形公理:$M^n$ = Hausdorff + 第二可数 + 每点有邻域 $\cong\mathbb R^n$ 的开集。
  拓扑流形自动**局部紧致**、**仿紧**(第二可数蕴含)、**局部道路连通**。经典例子:球面 $S^n$、环面 $T^n$、射影空间 $\mathbb RP^n$。
  本章不是重讲点集拓扑,而是把 GTM202 的语言压缩成「为光滑结构服务」的地基——每条拓扑性质后文光滑流形直接继承。
- **飞腾锚点**:**TLB⭐局部坐标** —— 流形「每点有 $\mathbb R^n$ 邻域」= 局部地址分页。
  🟡类比:坐标卡(chart)把流形分页成欧氏页,局部用 $\mathbb R^n$ 寻址,页间用转移映射(transition map)拼接,如同 TLB 页表保证地址一致;
  🟢事实:局部 $\cong\mathbb R^n$ 是流形学习(manifold learning)的几何基础——高维数据局部近似线性,正是流形公理的离散实现。
- **关键定理**:**拓扑流形的基本性质**。$M^n$ 局部紧致 + 仿紧 + 局部道路连通;
  $$M^n\ \text{仿紧}\ \Longrightarrow\ \exists\ \text{局部有限开覆盖}\ \{U_\alpha\},\ \overline{U_\alpha}\ \text{紧致}.$$
- **自测**:「双原点直线」(两条 $\mathbb R$ 除原点外等同,保留两个原点)是局部 $\cong\mathbb R$ 却**非 Hausdorff**——为何不满足流形公理?

---

### 第 2 章 · 光滑流形定义

- **核心**:**光滑图册**(smooth atlas):任意两卡的转移映射 $\psi\circ\varphi^{-1}$ 光滑($C^\infty$)。**极大光滑图册** = **光滑结构**(maximal atlas)。
  关键例子:$\mathbb R^n$、$S^n$(球极投影两卡)、$\mathbb RP^n$($n+1$ 个齐次坐标卡)、$\mathbb CP^n$、积流形 $M\times N$、$GL(n,\mathbb R)$(作为 $\mathbb R^{n^2}$ 开集 = Lie 群原型)。
  **光滑映射**与**微分同胚**(diffeomorphism)。**单位分解**(partition of unity)保证光滑函数可局部拼接——流形分析的基石。
- **飞腾锚点**:**TLB⭐局部坐标** —— 光滑结构 = 转移映射相容的坐标卡族。
  🟢事实:两卡 $(U,\varphi),(V,\psi)$ 光滑相容当且仅当 $\psi\circ\varphi^{-1}$ 是 $C^\infty$ 微分同胚,
  实现上等同 TLB 页表一致性约束(同一地址映射不矛盾);🟡类比:光滑结构像一套「坐标系典」,所有卡的「翻译规则」须 $C^\infty$ 兼容。
- **关键定理**:**光滑相容是图册上的等价关系**;光滑结构 = 极大光滑图册。每个拓扑流形(维数 $\le3$)有唯一光滑结构(高维存在怪异结构,如 Milnor 怪球)。
- **自测**:用球极投影(北极/南极)给 $S^n$ 定义两个卡,写出转移映射 $\psi\circ\varphi^{-1}:\mathbb R^n\setminus\{0\}\to\mathbb R^n\setminus\{0\}$,验证它是 $C^\infty$。

---

### 第 3 章 · 切向量与微分

- **核心**:全书奠基。三种等价定义切向量 $v\in T_pM$:
  (i) **几何**:穿过 $p$ 的光滑曲线 $\gamma(t)$ 的等价类($\gamma(0)=p$,$\gamma'(0)$ 相同);
  (ii) **代数**:芽 $C^\infty(p)$ 上的**导子**(derivation)$v:C^\infty(p)\to\mathbb R$ 满足 Leibniz 律 $v(fg)=v(f)g(p)+f(p)v(g)$;
  (iii) **物理**:方向导数算子。
  **微分** $df_p:T_pM\to T_{f(p)}N$ 是线性映射,**链式法则** $d(g\circ f)_p=dg_{f(p)}\circ df_p$。**切丛** $TM=\bigsqcup_p T_pM$。
- **飞腾锚点**:**FP16** —— 切向量 = 方向导数算子,是有限差分近似的连续极限。
  🟢事实:导子 $v(f)=\frac{d}{dt}f(\gamma(t))\big|_0$ 在数值上用 $f(p+\epsilon v)$ 近似,精度受 FP16 有效位约束;
  🟡类比:导子满足 Leibniz 律(乘积法则)是「无穷小分配律」,FP16 的截断误差决定了数值导数的精度上限。
- **关键定理**:**三种切空间定义等价**;$\dim T_pM=\dim M$;坐标基 $\left\{\left.\frac{\partial}{\partial x^i}\right|_p\right\}$。
  $$T_pM\cong\mathrm{Der}\,C^\infty(p),\qquad df_p\left(\left.\frac{\partial}{\partial x^i}\right|_p\right)=\frac{\partial f^j}{\partial x^i}\left.\frac{\partial}{\partial y^j}\right|_{f(p)}.$$
- **自测**:用导子定义验证 $\frac{\partial}{\partial x^i}$ 构成 $T_p\mathbb R^n$ 的基,且 $v(fg)=v(f)g(p)+f(p)v(g)$;再说明 $df_p$ 的矩阵在坐标下恰为 Jacobian。

---

### 第 4 章 · 浸入与嵌入

- **核心**:光滑映射 $f:M^m\to N^n$ 的**秩**(rank $=\mathrm{rank}\,df_p$)。
  **浸入**(immersion:$\mathrm{rank}\,df_p=m$ 处处,即 $df_p$ 单射)、**淹没**(submersion:$\mathrm{rank}\,df_p=n$ 处处,即 $df_p$ 满射)、
  **嵌入**(embedding:浸入 + 单射 + 同胚到像)。
  **常秩定理**(rank theorem):$\mathrm{rank}\,df\equiv r$ 处处时,局部存在坐标使 $f$ 有标准型 $(x^1,...,x^m)\mapsto(x^1,...,x^r,0,...,0)$。
  第 2 版把秩定理前移,使全书都能引用。
- **飞腾锚点**:**分支预测** —— 秩条件决定映射的局部行为,是三分支判定。
  🟡类比:「满射?(submersion)」「单射?(immersion)」「同胚到像?(embedding)」是 CPU 分支预测器的三个分支;
  🟢事实:常秩定理给出每个分支的**局部标准型**,实现上等同矩阵秩判定 + 局部坐标线性化,是子流形定理(ch5)的计算引擎。
- **关键定理**:**常秩定理**。若 $f:M^m\to N^n$ 处处 $\mathrm{rank}\,df_p=r$,则存在 $p$ 和 $f(p)$ 附近的坐标卡使
  $$f(x^1,...,x^m)=(x^1,...,x^r,0,...,0).$$
  (推论:淹没局部投影 $\pi(x)=(x^1,...,x^n)$;浸入局部嵌入 $\iota(x)=(x^1,...,x^m,0,...,0)$。)
- **自测**:给一个浸入但非嵌入的例子:稠密缠绕环面映射 $\gamma:\mathbb R\to T^2$, $\gamma(t)=(e^{it},e^{i\alpha t})$($\alpha$ 无理)——处处浸入但像稠密,非嵌入。

---

### 第 5 章 · 子流形

- **核心**:**嵌入子流形**(embedded submanifold):$S\subseteq M$ 每点有**切片坐标**(slice chart)$(U,\varphi)$ 使 $S\cap U=\{x^{k+1}=...=x^n=0\}$,
  $\dim S=k$。**浸入子流形**(immersed submanifold):拓扑更弱,可能自交。**正则水平集定理**(regular level set):
  若 $F:M^n\to N^k$ 且 $q$ 是正则值($df_p$ 处处满射),则 $F^{-1}(q)$ 是 $\dim n-k$ 嵌入子流形。
  带边子流形与带边流形($M$ 局部 $\cong\mathbb H^n=\{x^n\ge0\}$)。
- **飞腾锚点**:**分支预测** —— 子流形分类(embedded vs immersed vs initial)是「嵌入程度」的分支判定。
  🟢事实:正则水平集是最常见的子流形构造法——Jacobian 满秩 $\Rightarrow$ 光滑子流形,实现上是线性代数的秩判定分支;
  🟡类比:嵌入子流形像「干净地坐在流形里」,浸入子流形像「折叠塞入」,切片坐标是「展平」操作。
- **关键定理**:**正则水平集定理**。$q\in N$ 是 $F:M^n\to N^k$ 的正则值($\mathrm{rank}\,dF_p=k$ 对所有 $p\in F^{-1}(q)$)则
  $$F^{-1}(q)\ \text{是}\ M\ \text{的}\ (n-k)\ \text{维嵌入子流形},\qquad T_p(F^{-1}(q))=\ker\,dF_p.$$
- **自测**:用正则水平集证明 $S^n=\{x\in\mathbb R^{n+1}:|x|^2=1\}$ 是 $\mathbb R^{n+1}$ 的 $n$ 维子流形(取 $F=|x|^2$,$\mathrm{rank}\,dF=1$ 处处),并写出 $T_pS^n=\{v:v\cdot p=0\}$。

---

## 第二篇 · 丛与微分形式

### 第 6 章 · 切丛与向量丛

- **核心**:**向量丛**(vector bundle)$\pi:E\to M$:每点 $p$ 的纤维 $E_p\cong\mathbb R^r$,有**局部平凡化**(local trivialization)
  $\Phi_\alpha:\pi^{-1}(U_\alpha)\xrightarrow{\,\cong\,}U_\alpha\times\mathbb R^r$,**转移函数**(transition function)$g_{\alpha\beta}:U_\alpha\cap U_\beta\to GL(r,\mathbb R)$。
  切丛 $TM$ 是 rank $=n$ 的向量丛,余切丛 $T^*M$ 也是。**截面**(section)$s:M\to E$,$\pi\circ s=\mathrm{id}$。**局部标架**(local frame)。
- **飞腾锚点**:**matmul⭐切丛矩阵** —— 向量丛 = 参数化向量空间族,转移函数 $g_{\alpha\beta}\in GL(r,\mathbb R)$ 是矩阵。
  🟢事实:截面在卡间变换 $s_\beta=g_{\beta\alpha}\cdot s_\alpha$ 是矩阵-向量乘法(matmul),
  切丛转移函数恰为 Jacobian $\frac{\partial y^i}{\partial x^j}$;🟡类比:向量丛像「每点挂一个 $\mathbb R^r$」,截面是「光滑地选向量」,转移函数是换卡时的矩阵变换。
- **关键定理**:**向量丛由转移函数刻画**(cocycle 条件)。
  $$g_{\alpha\beta}\cdot g_{\beta\gamma}\cdot g_{\gamma\alpha}=\mathrm{id}\quad(\text{在}\ U_\alpha\cap U_\beta\cap U_\gamma\ \text{上});\qquad TM\ \text{的转移函数}\ =\ \left(\frac{\partial y^i}{\partial x^j}\right).$$
- **自测**:验证切丛 $TM$ 的 cocycle 条件(用链式法则 $\frac{\partial z^i}{\partial x^j}=\frac{\partial z^i}{\partial y^k}\frac{\partial y^k}{\partial x^j}$);再说明平凡丛 $E=M\times\mathbb R^r$ 的转移函数恒为 $\mathrm{id}$。

---

### 第 7 章 · 余切丛与微分形式

- **核心**:**余切空间** $T^*_pM=(T_pM)^*$,光滑函数 $f$ 的**微分** $df_p\in T^*_pM$ 是 $df_p(v)=v(f)$。
  **余切丛** $T^*M=\bigsqcup T^*_pM$。**微分 $k$-形式** $\omega\in\Omega^k(M)$:每点是 $\Lambda^k T^*_pM$ 的元素,
  **楔积** $\wedge$ 满足反交换 $\alpha\wedge\beta=(-1)^{kl}\beta\wedge\alpha$。**外微分**(exterior derivative)$d:\Omega^k\to\Omega^{k+1}$ 满足 $d^2=0$。**拉回** $f^*\omega$。
- **飞腾锚点**:**GEMM⭐张量** —— 微分形式是余切空间的反称张量,$k$-形式有 $\binom{n}{k}$ 个分量。
  🟢事实:楔积 $\alpha\wedge\beta$ 是分块反对称 GEMM 运算,$d\omega$ 是反称微分算子,实现上等同 `numpy.einsum` 的反对称化缩并;
  🟡类比:$k$-形式像「有向 $k$ 维面积元素」,楔积把低维面积拼成高维,外微分是「求面积元的边界」,与计算机图形学的法向量计算同构。
- **关键定理**:**外微分的性质**。
  $$d^2=0;\qquad d(\alpha\wedge\beta)=d\alpha\wedge\beta+(-1)^{\deg\alpha}\,\alpha\wedge d\beta;\qquad f^*(d\omega)=d(f^*\omega).$$
- **自测**:在 $\mathbb R^3$ 中验证 $d(x\,dy)=dx\wedge dy$ 且 $d(dx\wedge dy)=0$;再说明 $d^2=0$ 的几何意义是「边界的边界为零」($\partial^2=\varnothing$)。

---

### 第 8 章 · 定向

- **核心**:**向量空间的定向** = 有序基的等价类(两组基等价 $\Leftrightarrow$ 过渡矩阵 $\det>0$)。
  **流形的定向** = 切空间定向的连续相容选择。三种等价刻画:
  (i) 存在**定向图册**(所有转移映射的 Jac $\det>0$);
  (ii) 存在处处非零的**体积形式**(volume form = 处处非零的 $n$-形式);
  (iii) 切丛的结构群可约化为 $GL^+(n,\mathbb R)$。
  $\mathbb RP^2$、Möbius 带不可定向;$S^n$、$T^n$、$\mathbb CP^n$ 可定向。
- **飞腾锚点**:**Schmidt⭐正交标架** —— 定向 = 标架的「手性」(orientation)选择。
  🟢事实:Schmidt 正交化保持定向($\det>0$),保定向的坐标卡族给流形定向;不可定向流形(Möbius 带)「绕一圈回来标架翻转」,无法全局一致 Schmidt;
  🟡类比:定向像「左手系 vs 右手系」的全局选择,体积形式是「度量定向」的体积元素,与 Petersen ch1 黎曼度量下的体积形式 $\sqrt{\det g}\,dx^1\wedge\cdots\wedge dx^n$ 对接。
- **关键定理**:**可定向的等价刻画**。
  $$M\ \text{可定向}\ \Longleftrightarrow\ \exists\ \text{处处非零}\ n\text{-形式}\ \Longleftrightarrow\ \exists\ \text{定向图册}\ (\det\,\mathrm{Jac}>0).$$
- **自测**:证明 $S^1$ 可定向(给出体积形式 $d\theta$);说明 Möbius 带不可定向(取 Möbius 参数化,验证绕一圈后定向翻转 $\det<0$)。

---

## 第三篇 · 积分与上同调

### 第 9 章 · 流形上积分

- **核心**:在定向 $n$-流形 $M$ 上积分 $n$-形式 $\omega$:用**单位分解** $\{\psi_i\}$ 把整体积分分解为局部坐标卡上的 $\mathbb R^n$ 积分,
  $\int_M\omega=\sum_i\int_{U_i}\psi_i\omega$(局部有限保证收敛)。**带边流形**(manifold with boundary):局部模型 $\mathbb H^n=\{x^n\ge0\}$,
  边界 $\partial M$ 是 $(n-1)$ 维流形。**边界的定向**:外法向优先约定(outward-normal-first)——$\partial M$ 的定向由「$(n,\text{外法向});(\text{其余},\partial M\text{的定向})$」给出。
- **飞腾锚点**:**UDOT⭐积分** —— 积分 $n$-形式 $\omega=f\,dx^1\wedge\cdots\wedge dx^n$ 局部化为 $\int f\,dx^1\cdots dx^n$,是逐点求值 + 累加。
  🟢事实:UDOT(专用点积指令)比通用浮点快 16.9 倍,对 $\sum f_i\cdot\mathrm{vol}_i$ 直接加速;单位分解 $\{\psi_i\}$ 保证局部积分之和不依赖分解(有限覆盖);
  🟡类比:积分像「加权求和」,单位分解是「分配权重」,权重之和恒为 1,类比 softmax 的归一化。
- **关键定理**:**积分良定义**。$\int_M\omega=\sum_i\int_{U_i}\psi_i\omega$ 不依赖单位分解的选择(若 $\{\tilde\psi_j\}$ 是另一单位分解,则 $\sum_i\psi_i=\sum_j\tilde\psi_j=1$ 保证一致)。
- **自测**:在 $S^1$ 上 $\int_{S^1}d\theta=2\pi$(用标准定向);若反向定向,$\int_{-S^1}d\theta=-2\pi$——说明为何积分需要定向。

---

### 第 10 章 · Stokes 定理 ⭐

- **核心**:全书的高潮。**Stokes 定理** $\int_M d\omega=\int_{\partial M}\omega$,统一了:
  微积分基本定理($n=1$)、Green 公式($n=2$,$\mathbb R^2$)、经典 Stokes($n=3$,$\mathbb R^3$)、散度定理($\omega$ 为 $2$-形式)。
  深层对应:$d^2=0 \leftrightarrow \partial^2=\varnothing$(边界的边界为零)。证明分三步:局部 $\mathbb R^n$ 情形 $\to$ 单位分解拼接 $\to$ 边界定向验证。
  Stokes 是 de Rham 上同调(ch11)的基石——「闭形式在闭链上积分」在同调类上良定义。
- **飞腾锚点**:**UDOT⭐积分** —— Stokes 把「内部的微分」翻译为「边界的积分」,是高维分部积分。
  🟢事实:$\int_M d\omega=\int_{\partial M}\omega$ 离散化后 $\sum_{\text{内部}}d\omega_i=\sum_{\text{边界}}\omega_j$,内部贡献两两抵消,只剩边界项(UDOT 累加);
  🟡类比:Stokes 像有限差分中的边界修正——内部微分的「邻居差」在求和时抵消,只剩最外层边界,与离散散度定理同构。
- **关键定理**:**Stokes 定理**。若 $M$ 是带边紧致定向 $n$-流形,$\omega\in\Omega^{n-1}(M)$,则
  $$\int_M d\omega=\int_{\partial M}\omega,\qquad(\partial M=\varnothing\ \text{时右边为零}).$$
- **自测**:由 Stokes 推散度定理 $\int_D\nabla\cdot\mathbf F\,dV=\int_{\partial D}\mathbf F\cdot\mathbf n\,dS$(取 $\omega=F_1\,dy\wedge dz+F_2\,dz\wedge dx+F_3\,dx\wedge dy$),
  再说明 $M$ 紧致无边($\partial M=\varnothing$)时 $\int_M d\omega=0$ 对一切 $\omega$ 成立。

---

### 第 11 章 · de Rham 上同调

- **核心**:**de Rham 上同调群** $H^k_{\mathrm{dR}}(M)=\ker(d:\Omega^k\to\Omega^{k+1})\,/\,\mathrm{im}(d:\Omega^{k-1}\to\Omega^k)$,
  度量「闭但非恰当」的形式等价类 = $k$ 维「洞」。核心工具:
  **Poincaré 引理**($H^k_{\mathrm{dR}}(\mathbb R^n)=0$,$k\ge1$:星形区域上闭=恰当);
  **同伦不变性**($X\simeq Y\Rightarrow H^*_{\mathrm{dR}}(X)\cong H^*_{\mathrm{dR}}(Y)$:可缩空间上同调为零);
  **Mayer-Vietoris 长正合序列**(把 $M=A\cup B$ 的上同调拆解为 $A,B,A\cap B$ 的);$H^0=\mathbb R^{\#\text{连通分量}}$。
  **de Rham 定理**(原书 ch18):$H^k_{\mathrm{dR}}(M)\cong H^k_{\mathrm{sing}}(M;\mathbb R)$(与奇异同调的对偶)。
- **飞腾锚点**:**Iron Law⭐正合** —— de Rham 复形 $0\to\Omega^0\xrightarrow{d}\Omega^1\xrightarrow{d}\cdots\xrightarrow{d}\Omega^n\to0$ 的「正合性」度量拓扑障碍。
  🟢事实:正合(该维 $\ker=\mathrm{im}$,即 $H^k=0$)意味着该维无洞,误差为零(Iron Law $<2\%$);非正合($H^k\ne0$)意味着有 $k$ 维洞;
  🟡类比:Mayer-Vietoris 长正合序列像拼接两模块的接口,连接映射须「信息无丢失」(正合),与同调代数(Weibel ch1)的链复形同构。
- **关键定理**:**Poincaré 引理 + 同伦不变性**。
  $$H^k_{\mathrm{dR}}(\mathbb R^n)=0\ (k\ge1);\qquad X\simeq Y\ \Longrightarrow\ H^k_{\mathrm{dR}}(X)\cong H^k_{\mathrm{dR}}(Y).$$
- **自测**:算 $H^0_{\mathrm{dR}}(S^1)=\mathbb R$(连通),$H^1_{\mathrm{dR}}(S^1)=\mathbb R$($d\theta$ 是闭非恰当 $1$-形式:若 $d\theta=df$ 则 $\int_{S^1}d\theta=0$,矛盾);用 Mayer-Vietoris 验证。

---

## 第四篇 · 高级工具

### 第 12 章 · Sard 定理与横截

- **核心**:**临界点**($p$ 处 $df_p$ 不满射)、**临界值**($f(\text{临界点})$)。**Sard 定理**:$C^\infty$ 映射的临界值集**测度为零**——「坏值」虽多但可忽略。
  应用:**Whitney 嵌入定理**(任意光滑 $n$-流形可嵌入 $\mathbb R^{2n+1}$,浸入 $\mathbb R^{2n}$)——光滑流形「本质上住在欧氏空间」。
  **横截性**(transversality):$f:M\to N$ 与子流形 $W\subseteq N$ 横截($f\pitchfork W$)当且仅当 $df_p(T_pM)+T_{f(p)}W=T_{f(p)}N$;
  横截相交是**稳定**的(小扰动下保持),且**横截原像**是子流形。
- **飞腾锚点**:**FP16** —— Sard 定理说临界值集「测度零」,即「坏点」虽多但几乎不出现。
  🟢事实:数值上 FP16 的精度容差决定了「测度零」的近似——有限精度下临界值不会精确命中;
  🟡类比:Whitney 嵌入定理保证流形可嵌入低维欧氏空间,流形学习(Isomap/t-SNE)本质是在数据上恢复这种嵌入的离散近似,Sard 定理保证嵌入映射「几乎处处好」。
- **关键定理**:**Sard 定理 + Whitney 嵌入定理**。
  $$f\in C^\infty(M^m,N^n)\ \Longrightarrow\ \text{临界值集}\ C(f)\subseteq N\ \text{测度为零};\qquad \forall\ M^n,\ \exists\ \text{嵌入}\ M^n\hookrightarrow\mathbb R^{2n+1}.$$
- **自测**:用 Sard 说明 $f:\mathbb R\to\mathbb R$ 的 $C^\infty$ 函数临界值集($\{f(p):f'(p)=0\}$)测度为零;再用 Whitney 说明 $S^1$ 可嵌入 $\mathbb R^3$(实际 $\mathbb R^2$ 即可)。

---

### 第 13 章 · Lie 群引论

- **核心**:**Lie 群** $G$:光滑流形 + 群结构(乘法 $G\times G\to G$、逆 $G\to G$ 均 $C^\infty$)。**Lie 代数** $\mathfrak g=T_eG$ = 左不变向量场空间,
  Lie 括号 $[X,Y]=XY-YX$。**指数映射** $\exp:\mathfrak g\to G$, $\exp(X)=\gamma_X(1)$($X$ 的积分曲线走单位时间)。
  **Lie 子群** = 闭子群(Cartan 闭子群定理)。**伴随表示** $\mathrm{Ad}:G\to GL(\mathfrak g)$。
  经典例子:$GL(n,\mathbb R)$($\mathfrak{gl}=\mathfrak M_n(\mathbb R)$)、$O(n)$($\mathfrak{so}(n)=\{A:A^T+A=0\}$)、$SL(n)$、$U(n)$、$SU(n)$。
- **飞腾锚点**:**Schmidt⭐正交标架** —— Lie 群 = 带光滑结构的对称群,李代数 $\mathfrak g=T_eG$ 是「无穷小对称」。
  🟢事实:$O(n)$ 的李代数 $\mathfrak{so}(n)$ = 反称矩阵,正是 Schmidt 正交化的无穷小版本(保度量 $=$ 保正交),$\exp(tA)$ 是正交化流;
  🟡类比:Lie 代数像「对称群的切空间」——在单位元处线性化群结构,Lie 括号度量非交换性,与 Hall(stage-2)的李代数理论对接。
- **关键定理**:**Lie 对应(初步)**。$G$ 的连通 Lie 子群 $\leftrightarrow$ $\mathfrak g$ 的李子代数;
  $$\exp(tX)=\gamma_X(1)\ \text{是}\ X\ \text{的积分曲线};\qquad \exp(A)=e^A=\sum_{k=0}^\infty\frac{A^k}{k!}\quad(GL(n,\mathbb R)\ \text{上}).$$
- **自测**:验证 $GL(n,\mathbb R)$ 的李代数 $=\mathfrak M_n(\mathbb R)$(全矩阵),$\exp(A)=e^A$;再验证 $O(n)$ 的李代数 $=\{A:A^T+A=0\}$(对 $e^{tA}$ 求导,用 $e^{tA^T}e^{tA}=I$)。

---

### 第 14 章 · 李群作用

- **核心**:Lie 群 $G$ 在流形 $M$ 上的**光滑作用** $\theta:G\times M\to M$。**轨道** $G\cdot p=\{\theta_g(p):g\in G\}$, **稳定子** $G_p=\{g:\theta_g(p)=p\}$。
  **齐性空间**(homogeneous space)$G/H$($H$ 闭子群):$G/H$ 是光滑流形。**商流形定理**:自由 + 正当(free + proper)作用 $\Rightarrow$ $M/G$ 是流形且 $\pi:M\to M/G$ 是主丛。
  **Orbit-Stabilizer**:$G/G_p\cong G\cdot p$(轨道微分同胚于商)。例子:$SO(3)$ 传递作用在 $S^2$ 上,$SO(3)/SO(2)\cong S^2$。
- **飞腾锚点**:**Schmidt⭐正交标架** —— 群作用在标架上:$O(n)$ 作用 = 标架的正交变换。
  🟢事实:轨道 = 对称等价类,稳定子 = 不动的子群(标架的对称性),$G/G_p\cong G\cdot p$ 把「对称商」与「几何轨道」对偶;
  🟡类比:齐性空间 $G/H$ 像「对称群取商」——$S^2=SO(3)/SO(2)$ 意味着球面 $=$ 「旋转群取掉绕轴旋转的商」,与 Hall 的根系/旗流形对接。
- **关键定理**:**商流形定理 + Orbit-Stabilizer**。
  $$G\ \text{自由正当作用}\ \Rightarrow\ M/G\ \text{是流形},\ \pi:M\to M/G\ \text{主}\ G\text{-丛};\qquad G/G_p\cong G\cdot p.$$
- **自测**:$SO(3)$ 在 $S^2$ 上传递,北极 $(0,0,1)$ 的稳定子 $\cong SO(2)$(绕 $z$ 轴旋转),验证 $SO(3)/SO(2)\cong S^2$;再说明 $SO(3)$ 在 $S^2$ 上的作用自由吗?(否:有两点不动 $\Leftrightarrow$ 轴两端,但一般点稳定子 $=\{e\}$ 的共轭类。)

---

### 第 15 章 · 纤维丛

- **核心**:**纤维丛**(fiber bundle)$\pi:E\to B$ 以 $F$ 为纤维、$G$ 为结构群(转移函数取值在 $G\subseteq\mathrm{Diff}(F)$)。
  **主丛**(principal $G$-bundle):纤维 $=G$ 自身,$G$ 右作用自由传递。向量丛是 $F=\mathbb R^r$、$G=GL(r,\mathbb R)$ 的特例。
  **Hopf 纤维** $S^1\to S^3\to S^2$:经典非平凡主 $S^1$-丛。**标架丛**(frame bundle)$\mathrm{Fr}(TM)$:切丛的 $GL(n,\mathbb R)$ 主丛。
  Lee 在向量丛基础上延伸到一般纤维丛与主丛,为联络与规范理论(gauge theory)铺路。
- **飞腾锚点**:**Iron Law⭐正合** —— 纤维丛的同伦长正合序列度量纤维-底-全空间的关系。
  🟢事实:$\cdots\to\pi_k(F)\to\pi_k(E)\to\pi_k(B)\to\pi_{k-1}(F)\to\cdots$ 是长正合序列,连接映射的精确性(Iron Law $\ker=\mathrm{im}$)保证信息无丢失;
  🟡类比:Hopf 纤维 $S^1\to S^3\to S^2$ 说明 $S^3\ne S^2\times S^1$(非平凡丛),物理上对应磁单极(Berry 相位),与规范理论的丛结构对接。
- **关键定理**:**纤维丛的同伦长正合序列**(fibration sequence)。
  $$\cdots\to\pi_k(F)\to\pi_k(E)\to\pi_k(B)\xrightarrow{\,\partial\,}\pi_{k-1}(F)\to\cdots\qquad(\text{Hopf 纤维}:\ \pi_2(S^2)\cong\pi_1(S^1)\cong\mathbb Z).$$
- **自测**:$TM$ 的标架丛 $\mathrm{Fr}(TM)$ 是 $GL(n,\mathbb R)$ 主丛;$M$ 可定向 $\Leftrightarrow$ 结构群可约化为 $GL^+(n,\mathbb R)$;配度量 $g$ $\Rightarrow$ 可约化为 $O(n)$。

---

### 第 16 章 · 张量场

- **核心**:**$(r,s)$ 型张量** = $r$ 重反变 + $s$ 重协变的多重线性算子($T_pM$ 的 $r$ 重张量积 $+$ $T^*_pM$ 的 $s$ 重张量积)。
  **张量丛** $T^{r,s}(M)$。**张量场** = 光滑截面。**黎曼度量** $g$ 是 $(0,2)$ 型对称正定张量场(原书 ch13)。
  **缩并**(contraction):对一对协变-反变指标求迹。**拉回** $f^*$ 作用于协变张量(向后拉)。**升降指标**:用 $g$ 的逆 $g^{ij}$ 提升、$g_{ij}$ 降低指标。
- **飞腾锚点**:**GEMM⭐张量** —— 张量场是多线性运算的参数化族,度量 $g_{ij}$ 是对称矩阵场。
  🟢事实:张量分量的计算是密集 GEMM——$R_{ijkl}=g_{im}R^m{}_{jkl}$(升降指标)等同 `numpy.einsum`,缩并 $= $ 矩阵乘 + 迹;
  🟡类比:黎曼度量 $g$ 像「每点的内积矩阵」,Petersen ch1 的 $g=\sum g_{ij}\,dx^i\otimes dx^j$ 正是此处 $(0,2)$-张量场的具体化,度量的存在性由单位分解保证。
- **关键定理**:**张量场 = 张量丛的光滑截面;黎曼度量存在性**。
  $$\Gamma(T^{r,s}(M))=\Gamma\big((TM)^{\otimes r}\otimes(T^*M)^{\otimes s}\big);\qquad \forall\ M^n,\ \exists\ \text{黎曼度量}\ g\ (\text{单位分解拼接局部欧氏度量}).$$
- **自测**:在 $\mathbb R^n$ 上 $g=\delta_{ij}\,dx^i\otimes dx^j$,写出逆 $g^{ij}=\delta^{ij}$,验证 $g_{ik}g^{kj}=\delta_i^j$;再用单位分解说明任意光滑流形可配度量。

---

### 第 17 章 · 流与 Frobenius

- **核心**:向量场 $X$ 的**积分曲线** $\gamma'(t)=X_{\gamma(t)}$(ODE),**存在唯一性**(初值 $\gamma(0)=p$)由附录 D 的 ODE 理论保证。
  **流**(flow)$\Phi_t:M\to M$ 是微分同胚,$\frac{d}{dt}\big|_0\Phi_t(p)=X_p$。**完备**(complete)向量场:流对所有 $t\in\mathbb R$ 定义(紧致流形上所有向量场完备)。
  **Frobenius 定理**:**分布**(distribution)$D\subseteq TM$(每点给子空间 $D_p\subseteq T_pM$);
  $D$ **可积**(过每点有积分子流形切于 $D$)$\Leftrightarrow$ $D$ **对合**(involutive:局部标架 $\{X_i\}$ 满足 $[X_i,X_j]\in D$)。
  可积分布给**叶状结构**(foliation)。第 2 版把流的基本定理前移到 ch9 以便全书引用。
- **飞腾锚点**:**matmul⭐切丛矩阵** —— 分布 $D$ 是 $TM$ 的子丛,可积性判据 $[X_i,X_j]\in D$ 是 Lie 括号的封闭性。
  🟢事实:子空间族 $D_p\subseteq T_pM$ 在 Lie 括号下封闭,实现上是「子空间族在交换子下不变」,与矩阵 Lie 代数的子代数判据($[A,B]\in\mathfrak h$)同构(matmul);
  🟡类比:Frobenius 定理像「局部积分子空间 $\Leftrightarrow$ 括号封闭」,流是向量场的「时间演化」,Frobenius 是「多个流能否拼成子流形」的判据,与 Hamilton 力学的可积性对接。
- **关键定理**:**Frobenius 定理**。$D\subseteq TM$ 是秩 $k$ 分布,则以下等价:
  $$D\ \text{可积}\ \Longleftrightarrow\ D\ \text{对合}\ \big([X_i,X_j]\in\Gamma(D)\ \forall\ \text{局部标架}\ \{X_i\}\big)\ \Longleftrightarrow\ \exists\ \text{叶状结构}.$$
- **自测**:$\mathbb R^3$ 中 $D=\mathrm{span}\{\partial_x,\partial_y\}$ 可积(叶 $=\{z=\mathrm{const}\}$);
  $\mathbb R^3$ 中 $D=\mathrm{span}\{\partial_x,\ \partial_y+x\partial_z\}$:$[\partial_x,\partial_y+x\partial_z]=\partial_z\notin D$(检查:若 $\partial_z=a\partial_x+b(\partial_y+x\partial_z)$ 则 $\partial_y$ 分量 $b=0$ 但 $\partial_z$ 分量 $bx=1$ 矛盾),
  故 $D$ **不对合**,Frobenius 推 $D$ 不可积——这恰是 $\mathbb R^3$ 的**接触分布**(contact distribution $\ker(dz-x\,dy)$),连接原书 ch22 辛流形。

---

### 第 18 章 · Morse 理论与指标(超出本书)

- **核心**:Lee GTM218 **不覆盖** Morse 理论(原书 ch22 是辛流形 Symplectic Manifolds,非 Morse)。
  但 Morse 理论是光滑流形与微分拓扑的**自然延伸**,故作为指针附上。**Morse 函数** $f:M\to\mathbb R$:所有临界点($df_p=0$)**非退化**(Hessian 非奇异)。
  **Morse 引理**:临界点附近 $f$ 有标准型 $f=-x_1^2-\cdots-x_\lambda^2+x_{\lambda+1}^2+\cdots+x_n^2+f(p)$($\lambda$ = 指标 index = 负 Hessian 特征值个数)。
  **Morse 不等式**:各指标临界点数 $c_\lambda\ge\beta_\lambda$(Betti 数),且 $\sum(-1)^\lambda c_\lambda=\chi(M)$。
  流形的拓扑由 Morse 函数的临界点完全决定(从每个指标 $\lambda$ 临界点粘一个 $\lambda$-胞腔)。经典参考:**Milnor《Morse Theory》**(1963)。
- **飞腾锚点**:**Iron Law⭐正合** —— Morse 理论把流形拆解为临界点的 CW 复形,Morse 复形的链群由临界点生成。
  🟢事实:Morse 不等式 $c_\lambda\ge\beta_\lambda$ 是 CW 复形 Euler 示性数 $\chi=\sum(-1)^\lambda c_\lambda=\sum(-1)^\lambda\beta_\lambda$ 的精确化,
  正合序列连接 Morse 复形与同调($\ker/\mathrm{im}$,Iron Law);🟡类比:Morse 函数像「地形高度图」,临界点(峰/谷/鞍)决定地形的拓扑骨架,指标 = 该点的「不稳定方向数」。
- **关键定理**:**Morse 引理 + Morse 不等式**。
  $$f\in C^\infty(M^n),\ p\ \text{非退化临界点}(\text{指标}\ \lambda)\ \Rightarrow\ \exists\ \text{局部坐标使}\ f=-\sum_{i=1}^{\lambda}x_i^2+\sum_{i=\lambda+1}^{n}x_i^2+f(p).$$
- **自测**:环面 $T^2$ 上高度函数 $f$ 是 Morse 函数:4 个临界点(min $\lambda=0$: 1 个,saddle $\lambda=1$: 2 个,max $\lambda=2$: 1 个),
  验证 Morse 不等式 $\beta_0=1\le c_0=1$,$\beta_1=2\le c_1=2$,$\beta_0-\beta_1+\beta_2=1-2+1=0=\chi(T^2)$。

---

## §9 全书思想主线(约 200 字)

Lee GTM218 的 22 章是一条「**拓扑流形 → 光滑流形 → 流形上的微积分 → 拓扑**」的上升阶梯。
**第一篇**(Ch1-5)在拓扑流形 $M^n$ 上叠加光滑结构,定义切空间(导子)、微分 $df_p$(Jacobian 的坐标无关版)、子流形(切片坐标 / 正则水平集)——建立「可微」的语言。
**第二篇**(Ch6-8)把切空间打包成**向量丛**(参数化向量空间族),引入**余切丛**与**微分形式**(反称张量),定义**定向**(标架的手性)——为积分铺路。
**第三篇**(Ch9-11)是全书高潮:定向流形上积分 $n$-形式(单位分解),**Stokes 定理** $\int_M d\omega=\int_{\partial M}\omega$ 统一一切微积分定理,
**de Rham 上同调** $H^k=\ker/\mathrm{im}$ 把「闭但非恰当」形式变成拓扑不变量——$d^2=0\leftrightarrow\partial^2=\varnothing$ 的对偶是全书灵魂。
**第四篇**(Ch12-18)是工具箱:Sard 定理(临界值测度零 $\to$ Whitney 嵌入)、Lie 群(对称的微分流形)、纤维丛、张量场、Frobenius 定理(叶状结构),为 Petersen 黎曼几何与 Hall 李群理论提供严格基础。

全书贯穿一条铁律:$d^2=0\leftrightarrow\partial^2=\varnothing$——外微分的「平方为零」与边界的「边界为空」是同一枚硬币的两面,
Stokes 定理 $\int_M d\omega=\int_{\partial M}\omega$ 正是这对偶的积分表述。de Rham 上同调 $H^k=\ker d/\mathrm{im}\,d$ 把这对偶升华为拓扑不变量,
使「分析对象(形式)」度量「拓扑对象(洞)」。这条从「光滑」到「形式」到「同调」的逻辑链,正是现代微分几何的灵魂。

### 三条红线

1. **结构红线**——拓扑流形(Ch1)→ 光滑结构(Ch2)→ 切空间(Ch3)→ 积分/ch5 子流形,每加一层结构,可做的运算就多一层。
2. **微积分红线**——切空间(Ch3)→ 微分形式(Ch7)→ 积分(Ch9)→ **Stokes**(Ch10)→ **de Rham**(Ch11),微分流形上的微积分直达拓扑。
3. **对称红线**——Lie 群(Ch13)→ 李群作用(Ch14)→ 纤维丛(Ch15)→ Frobenius(Ch17),对称性用流形语言精确化,连接 Hall 与 Petersen。

**读法建议**:第一遍精读 Ch1-5(光滑结构 + 切空间 + 子流形,工程/物理应用最密,对应 GTM202 ch11);
第二遍死磕 Ch7-11(形式 → Stokes → de Rham,全书灵魂,与 Spivak 交叉对照);
第三遍选读 Ch12-14(Sard + Lie 群,为 Petersen 黎曼几何与 Hall 李群理论铺路)。全书精读约 80-120 小时(每周 10-20h,8-12 周)。

---

## §10 与本仓库其他笔记的交叉引用

- **Lee《拓扑流形》GTM202**(stage-2):GTM218 是 GTM202 的**直接下游**。GTM202 给了拓扑流形公理(Hausdorff + 第二可数 + 局部 $\cong\mathbb R^n$)、CW 复形、$\pi_1$、曲面分类;
  GTM218 在此拓扑地基上叠加**光滑结构**,把「连续」升级为「光滑」。读 GTM218 Ch1-2 前应有 GTM202 ch11(拓扑流形)打底。
- **Spivak《流形上的微积分》**(stage-2):Spivak 是 GTM218 的**浓缩前驱**。Spivak 用 $\sim$130 页讲了 GTM218 前 16 章的核心(切空间、形式、Stokes),
  但省略了子流形理论细节、Sard 定理、Lie 群、向量丛、Frobenius。GTM218 是 Spivak 的「展开版」,建议交叉对照 Stokes 定理证明(两者思路互补)。
- **Petersen《黎曼几何》GTM171 / do Carmo**(stage-2):GTM218 是它们的**直接前置**。GTM218 的切丛(ch6)、张量场(ch16)、黎曼度量(ch13)是 Petersen ch1(度量)、ch2(Levi-Civita 联络)的语言基础;
  GTM218 的子流形理论(ch5)对接 do Carmo 的曲面论(嵌入 $\mathbb R^3$ 的特例)。建议:GTM218 $\to$ Petersen(do Carmo 提供二维直觉)。
- **Bott-Tu《微分形式》GTM82**(stage-2):GTM218 ch11(de Rham 上同调)是 Bott-Tu 的**入门版**。Bott-Tu 用层论与 Cech-de Rham 双复形深化 de Rham 理论,
  含谱序列与示性类。建议:GTM218 ch11 $\to$ Bott-Tu ch1-2(de Rham 基础)$\to$ Bott-Tu ch3(谱序列)。
- **Hall《李群李代数》**(stage-2):GTM218 ch7(Lie 群)、ch14(李群作用)是 Hall 的**微分流形视角**。Hall 从矩阵群切入,强调表示论与 Cartan 分类;
  GTM218 给 Lie 群的流形定义($G$ = 光滑流形 + 群结构)。建议:GTM218 ch7 $\to$ Hall ch1-3($SU(n)$、$SO(n)$、根系)$\to$ Hall ch7(Cartan 分类)。
- **AI 锚点(飞腾 D3000M 映射)**:
  - **光滑流形 = 数据流形假设**(ch1-2 TLB⭐:流形学习 Isomap/t-SNE/UMAP 假设高维数据活在低维光滑流形上,局部 $\cong\mathbb R^n$ = 流形公理);
  - **切空间 = 无穷小线性化**(ch3 FP16:切空间是流形的局部线性近似,自动微分的 Jacobian 是微分的离散版);
  - **微分形式 = 反称张量**(ch7 GEMM⭐:$k$-形式计算是 GEMM + 反对称化,`numpy.einsum` 是工程实现);
  - **Stokes = 分部积分的高维版**(ch10 UDOT⭐:散度定理是 Stokes 在 $\mathbb R^3$ 的特例,PDE 有限元的边界积分同源);
  - **de Rham = 拓扑障碍检测器**(ch11 Iron Law⭐:$H^k\ne0$ 标记 $k$ 维洞,正合 $H^k=0$ = 无洞,与同调代数的 $\ker/\mathrm{im}$ 同构);
  - **Sard = 几乎处处好**(ch12 FP16:临界值测度零保证嵌入映射「几乎处处正则」,是流形学习的理论保证);
  - **Lie 群 = 对称的微分流形**(ch13 Schmidt⭐:$O(n)$ = 保度量的变换群,正交化 = Lie 代数流,与自然梯度法的参数空间对称对接)。

---

> **下一步**:沿 `01-track/stage-2` 精读 Lee Ch1-5(光滑结构 / 切空间 / 子流形),遇关键概念查 `00-META/CONCEPT-INDEX` 中「导数 / 线性 / 积分」视角;
> Ch7-11(形式 / Stokes / de Rham)死磕 $d^2=0$ 与 $\partial^2=\varnothing$ 的对偶,与 Spivak《流形上的微积分》交叉对照。
> **实操验证**(建议用 Python/NumPy):
> - `numpy.einsum` 实现 $k$-形式的外微分与楔积(ch7)→ 验证 $d^2=0$
> - 在 $S^2$ 上数值积分体积形式(ch9)→ 验证 $\int_{S^2}\sin\theta\,d\theta\wedge d\varphi=4\pi$
> - 用 `scipy.linalg.expm` 实现 Lie 群指数映射(ch13)→ 验证 $\exp(tA)\in O(n)$ 当 $A^T+A=0$
