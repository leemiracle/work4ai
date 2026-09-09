# Fulton《代数拓扑第一课》(GTM153) · 快速逐章精读

> 基于原书:`Algebraic Topology: A First Course` (William Fulton, GTM153, Springer, 1995) / 读于:2026-07-02
> 定位:**最几何直觉友好的代数拓扑入门**,基本群 $\pi_1$ + 复叠空间 + 奇异同调的几何主线。
> 本文为**快速逐章精读**,每章 1 个飞腾锚点 🟢/🟡 + 1 个关键定理 + 1 道自测题。

---

## §0 引言:Fulton 是什么,为什么读它

William Fulton 的《Algebraic Topology: A First Course》(GTM153, 1995)是**最几何直觉友好的代数拓扑入门**。
Fulton 本人是代数几何/代数曲线大师(与 Harris 合著表示论),这使得本书与同类教材相比有一条独特暗线:
它**从复分析自然进入**——用环绕数(winding number)、Cauchy 积分公式、$\mathbb{C}\setminus\{0\}$ 的指数覆叠
$e^{2\pi it}:\mathbb{R}\to S^1$,把"绕原点几圈"的复分析直觉直接翻译成基本群 $\pi_1(S^1)\cong\mathbb{Z}$ 的代数。
全书的几何主线是:空间(Ch1)→ 用环路分类"洞"(Ch2 基本群)→ 用复叠空间"展开洞"(Ch3)→
用 van Kampen 拼接(Ch4-5)→ 把"洞计数"升级为同调群 $H_n$(Ch6-8)→ 上同调与对偶(Ch9-10)→ 专题预告(Ch11)。

本仓库已精读 Munkres《拓扑学》(点集 Part I + 代数拓扑 Part II,含 $\pi_1$/覆叠/曲面分类)。Fulton 是**代数拓扑的第二本**:
Munkres 给了 $\pi_1$ 与覆叠的**严格骨架**,Fulton 则补上更深的**几何动机**(复分析入口)并推进到**奇异同调与上同调**——
这是 Munkres Part II 尚未覆盖的高半部分。前置:Munkres 拓扑 ch1-9、抽象代数(群与商)。

对比四本主流教材:

| 书 | 风格 | 严格性 | 适合谁 |
|---|---|---|---|
| **Fulton**《A First Course》(GTM153,1995) | 几何友好,复分析动机,基本群+奇异同调主线,图多 | 严谨清晰,证明完整 | 已读点集拓扑、要"几何直觉更深"的第二本 |
| **Hatcher**《Algebraic Topology》(2002,免费) | 图示极丰富,几何直觉流淌,但证明常"留给读者" | 叙述松散,需自行补全 | 喜欢看图悟道、能接受省略的读者 |
| **Bredon**《Topology and Geometry》(GTM139) | 几何味重,流形/李群导向,同调与微分形式并举 | 严谨偏几何 | 想从流形几何切入的研究者 |
| **Munkres**《Elements of Algebraic Topology》(1984) | 单纯同调为纲,计算细致,组合严格 | 极严谨,古典 | 想扎实掌握单纯同调计算的读者 |

---

## §1 全书 11 章骨架一览(飞腾锚点分布)

| 章 | 标题 | 核心概念 | 飞腾锚点 |
|---|---|---|---|
| 1 | 拓扑空间回顾与道路连通 | 拓扑/连续/连通/道路连通 | 分支预测[Lab02] |
| 2 | 同伦与基本群 | $\pi_1$/同伦不变性/$\pi_1(S^1)=\mathbb Z$/收缩 | FP16 3.81×[L01] ⭐ |
| 3 | 复叠空间 | 复叠/提升/复叠变换/Galois 对应 | TLB 4.81×[E04] ⭐ |
| 4 | van Kampen 定理 | 自由群/Seifert-van Kampen/应用 | 分支预测[Lab02] |
| 5 | 应用:基本群计算 | 曲面/图/结点基本群 | matmul 15×[V03] |
| 6 | 奇异同调 | 链复形/同调群/同伦不变量/正合序列 | UDOT 16.9×[E05] |
| 7 | 同调的计算 | 球面/胞腔同调/CW 复形 | GEMM 9.45G[Lab05] |
| 8 | Mayer-Vietoris 序列 | 拼接两块的长正合序列 | Iron Law<2%[Lab00] ⭐ |
| 9 | 上同调 | 上链/上同调/Kronecker 配对 | UDOT 16.9×[E05] |
| 10 | 杯积与 Poincaré 对偶 | $\smile$ 积/流形/Poincaré 对偶 | Schmidt 正交化 ⭐ |
| 11 | 专题:纤维丛与示性类预告 | 纤维丛/Stiefel-Whitney/Chern/Euler 类 | GEMM 9.45G[Lab05] |

---

### 第 1 章 · 拓扑空间回顾与道路连通

- **核心**:本章是快速回顾(非重讲),把 Munkres Part I 的点集语言压缩成代数拓扑所需的"地基"。
  要点:拓扑与连续的等价刻画(开集原像开)、紧致、连通、**道路连通**(path connected)。
  关键升级是把"道路" $\gamma:[0,1]\to X$ 提升为一等公民——它是下一章基本群的原子单位。
  道路连通蕴含连通(反之不真);连续像保道路连通;乘积与商保道路连通。
  本章还复习**同伦等价** $X\simeq Y$(存在互逆连续映射到同伦),它是全书"同伦不变量"的等价关系地基——
  比同胚弱,却足以让 $\pi_1$、$H_n$ 都成不变量。
- **飞腾锚点**:**分支预测[Lab02]** —— 道路连通判定"两点间是否存在一条连续道路",
  像 CPU 分支预测判断"这条路径是否走得通"。
  🟡类比:道路 $\gamma$ 是一条从 $a$ 到 $b$ 的"执行轨迹",道路连通性 = 任两点都能找到一条不中断的轨迹相连;
  若某处"断点"则不连通,如同分支预测失败。
  🟢事实:连通分量是拓扑的等价类划分,实现上等同图论连通分量算法(并查集/DFS);
  同伦等价 $X\simeq Y$ 像"形状的可变形等价",仅保留可连续形变不变的量。
- **关键定理**:**道路连通 $\Rightarrow$ 连通**(逆不成立)。
  $$
  \forall\,a,b\in X,\ \exists\,\gamma:[0,1]\to X,\ \gamma(0)=a,\ \gamma(1)=b
  \ \Longrightarrow\ X\ \text{连通}.
  $$
- **自测**:举一个连通但非道路连通的空间
  (提示:拓扑正弦曲线 $S=\{(x,\sin\frac1x):0<x\le1\}\cup(\{0\}\times[-1,1])$),
  并说明它为何"连得上但走不过去"(沿 $x\to0$ 振荡无穷次,没有连续道路连到纵轴段)。

---

### 第 2 章 · 同伦与基本群

- **核心**:全书第一个核心章。**同伦**(homotopy)$F:X\times[0,1]\to Y$ 是"连续变形"——
  两映射 $f\simeq g$ 若能从 $f$ 连续形变到 $g$;同伦等价空间 $X\simeq Y$ 是代数拓扑的主等价关系。
  取基点 $x_0$ 的**环路**(loop)$\gamma:[0,1]\to X$, $\gamma(0)=\gamma(1)=x_0$,
  在道路同伦下的等价类带**道路复合**(先走 $\gamma$ 后走 $\eta$)构成**基本群** $\pi_1(X,x_0)$。
  核心结论:(i) 同伦等价空间有同构的 $\pi_1$(**同伦不变量**);(ii) $f\simeq g\Rightarrow f_*=g_*$;
  (iii) 收缩(retraction)$r:X\to A$ 给出 $\pi_1$ 的分解;
  (iv) 奠基计算 $\pi_1(S^1)\cong\mathbb Z$(用指数覆叠,环绕数=生成元)。
  Fulton 从复分析环绕数切入,使 $\pi_1(S^1)=\mathbb Z$ 极其自然——这是它区别于 Hatcher 的招牌。
- **飞腾锚点**:**FP16 3.81×[L01]** —— 同伦是"连续变形下不变",本质是**小扰动不变性**。
  🟡类比:同伦等价 $f\simeq g$ 像 FP16 精度容差——只要变形不超过"撕裂"阈值,映射视为等价;
  $\pi_1$ 抹去所有可连续形变(收缩到点)的环路,只留"真洞"。
  🟢事实:数值实现道路复合 $\gamma*\eta$(先 $\gamma$ 后 $\eta$)需参数重整化 $\gamma(2t)$、$\eta(2t-1)$,
  对浮点采样精度敏感(类 FP16);环绕数作为 $\pi_1(S^1)$ 生成元,其整数性是"变形下不变"的离散守恒量。
- **关键定理**:**$\pi_1(S^1)\cong\mathbb Z$**(用复叠 $p:\mathbb R\to S^1,\ p(t)=e^{2\pi it}$ 的道路提升证明:
  环路 $\gamma$ 唯一提升为 $\tilde\gamma(0)=0$ 的 $\tilde\gamma:[0,1]\to\mathbb R$,
  整数 $\tilde\gamma(1)\in\mathbb Z$ 即环绕数/生成元)。并一般地:
  $$
  \pi_1(X,x_0)=\{\text{基点 }x_0\text{ 的环路}\}\big/_{\text{道路同伦}},\qquad
  X\simeq Y\ \Rightarrow\ \pi_1(X)\cong\pi_1(Y).
  $$
- **自测**:用收缩证明 $\pi_1(S^n)=0$($n\ge2$)
  (提示:$S^n$ 去掉一点 $\cong\mathbb R^n$ 可缩,任一环路像可避开某点再收缩);
  并说明这为何推出 $\mathbb R^n$($n\ge2$)单连通而 $\mathbb R^2\setminus\{0\}$ 不单连通($\pi_1=\mathbb Z$)。

---

### 第 3 章 · 复叠空间

- **核心**:代数拓扑最优雅的篇章。**复叠空间**(covering space)$p:\tilde X\to X$
  是"局部同胚但全局多叶"的映射(每点 $x$ 有均匀邻域 $U$ 使 $p^{-1}(U)$ 是若干同胚拷贝之并)。
  两个核心定理:**道路提升**(任给 $\tilde x_0\mapsto x_0$ 与道路 $\gamma$,唯一提升为 $\tilde\gamma$)、
  **同伦提升**(同伦唯一提升)。由此得**复叠对应定理**:
  $X$ 的复叠空间(道路连通)等价类 $\leftrightarrow$ $\pi_1(X)$ 的子群共轭类——这是拓扑版的 Galois 对应。
  **万有复叠**(单连通)对应平凡子群,它"展开所有洞";
  **复叠变换群** $\mathrm{Deck}(p)\cong\pi_1(X)/p_*\pi_1(\tilde X)$ 度量底空间的对称性。
  Fulton 用 $S^1$ 的复叠 $\mathbb R$ 与环面的复叠 $\mathbb R^2$ 反复示范,几何画面极强。
- **飞腾锚点**:**TLB 4.81×[E04]** —— 复叠是"局部地址 → 全局"的多叶映射,提升定理 = 通过地址映射重定向访问。
  🟡类比:复叠 $p:\tilde X\to X$ 像 TLB 地址翻译——底空间点是"虚拟地址",复叠空间点是"物理页",
  提升定理保证给定一条虚拟地址轨迹能唯一还原到物理轨迹;复叠变换群 = 保持 $p$ 的"地址重映射对称群"。
  🟢事实:万有复叠"展开所有洞",工程上等同把环面 $\mathbb R^2/\mathbb Z^2$ 整个铺开为平面贴图(UV 映射/纹理展开);
  $n$ 叶复叠对应 $\pi_1$ 的指数 $n$ 子群,是"洞的层数"的代数编码。
- **关键定理**:**复叠对应定理**(拓扑-代数 Galois 对应)。设 $X$ 局部道路连通半局部单连通,则
  $$
  \{\text{道路连通复叠 }(\tilde X,p)\}\big/_{\text{等价}}\ \longleftrightarrow\
  \{\pi_1(X,x_0)\text{ 的子群共轭类}\},\quad (\tilde X,p)\mapsto p_*\pi_1(\tilde X,\tilde x_0).
  $$
  万有复叠 $\leftrightarrow$ 平凡子群;$n$ 叶正则复叠 $\leftrightarrow$ 指数 $n$ 正规子群,
  且 $\mathrm{Deck}(p)\cong\pi_1(X)/p_*\pi_1(\tilde X)$。
- **自测**:$\pi_1(S^1)=\mathbb Z$ 的子群 $n\mathbb Z$ 对应 $n$ 叶复叠 $p_n:S^1\to S^1,\ z\mapsto z^n$——
  验证 $p_{n*}\pi_1(S^1)=n\mathbb Z$,
  并说明 $\mathrm{Deck}(p_n)\cong\mathbb Z/n\mathbb Z$(旋转 $\frac{2\pi}{n}$ 的对称群)。

---

### 第 4 章 · van Kampen 定理

- **核心**:计算复杂空间 $\pi_1$ 的核心工具,需先备**自由群** $F(S)$(生成元集 $S$ 无关系)
  与**自由积** $G*H$(两群生成元交替拼接成的字,无跨群关系)。
  **Seifert-van Kampen 定理**:若 $X=A^\circ\cup B^\circ$ 且 $A,B,A\cap B$ 道路连通(基点在交中),
  则 $\pi_1(X)$ 是 $\pi_1(A)*\pi_1(B)$ 模去"交中环路在两边表达相同"这一关系所得商群——
  即**合并** $\pi_1(A),\pi_1(B)$,把交的 $\pi_1$ 粘合。
  应用密集:圆楔 $\pi_1=\mathbb Z*\mathbb Z$(二元自由群);粘一个二维胞腔 = 在展示中加一个关系;
  环面 $\pi_1(T^2)=\mathbb Z\times\mathbb Z$(两生成元交换,因胞腔粘合给交换关系 $aba^{-1}b^{-1}=1$)。
  van Kampen 把"剪贴空间"变成"读展示式"的机械操作。
- **飞腾锚点**:**分支预测[Lab02]** —— 自由积 $G*H$ 的字是"交替选取 $G$ 或 $H$ 生成元"的分支拼接。
  🟡类比:van Kampen 像 CPU 分支预测把两个子程序的控制流合并——
  $A$ 的环路走 $A$ 分支、$B$ 的走 $B$ 分支,交 $C$ 中的环路是两分支都要"命中"的公共路径,模去重复即得 $\pi_1(X)$。
  🟢事实:展示式 $\langle\text{生成元}\mid\text{关系}\rangle$ 的化简是符号重写系统,
  实现上等同关系矩阵的行/列消元(matmul);粘胞腔加关系 = 矩阵加约束行。
- **关键定理**:**Seifert-van Kampen 定理**。设 $X=A^\circ\cup B^\circ$,$C=A\cap B$ 道路连通,基点 $x_0\in C$,则含入诱导的序列正合:
  $$
  \pi_1(C)\xrightarrow{(i_*,j_*)}\pi_1(A)*\pi_1(B)\xrightarrow{k_*-l_*}\pi_1(X)\to 1,
  $$
  即 $\pi_1(X)\cong\big(\pi_1(A)*\pi_1(B)\big)/N$,$N$ 为 $i_*(c)\,j_*(c)^{-1}$($c\in\pi_1(C)$)
  生成的正规闭包(粘合交中双重表达的环路)。
- **自测**:用 van Kampen 算"8 字空间"(两圆楔 $S^1\vee S^1$)的 $\pi_1\cong\mathbb Z*\mathbb Z$(二元自由群),
  并说明它为何**非交换**(取 $a,b$ 两环路,$ab\ne ba$ 因无关系强制交换)。

---

### 第 5 章 · 应用:基本群计算

- **核心**:把 Ch2-4 的工具用于经典对象,练成"读胞腔粘贴 → 写 $\pi_1$ 展示式"的本能。
  (i) **曲面基本群**:亏格 $g$ 可定向曲面 $\Sigma_g$ 的标准 $4g$ 边多边形表示给
  $\pi_1(\Sigma_g)=\langle a_1,b_1,\dots,a_g,b_g\mid \prod_{i=1}^g[a_i,b_i]=1\rangle$;
  (ii) **图的基本群**:连通图的 $\pi_1$ 是自由群,秩 = $1-\chi$($\chi=V-E$);
  (iii) **结点(knot)补空间**:结点群 $\pi_1(S^3\setminus K)$ 刻画结点(三叶结 $\ne$ 未打结);
  (iv) 不可定向曲面(射影面 $\mathbb RP^2$、克莱因瓶)的 $\pi_1$。
  本章是 van Kampen 的密集训练场,每个胞腔粘贴都对应展示式里一个生成元或关系。
- **飞腾锚点**:**matmul 15×[V03]** —— 胞腔粘贴本质是关联矩阵:每个胞腔的粘贴映射给一行"边界关系",读 $\pi_1$ = 解这些关系。
  🟢事实:把 $4g$ 边多边形按词 $a_1b_1a_1^{-1}b_1^{-1}\cdots a_gb_ga_g^{-1}b_g^{-1}$ 粘合成 $\Sigma_g$,
  生成元间的交换关系由粘贴图编码,等同稀疏关联矩阵的化简(matmul 流水线);
  🟡类比:曲面分类像把"形状字典"用 $\pi_1$ 的展示式索引,同构的展示式 ↔ 同胚的曲面。
- **关键定理**:**曲面基本群展示式**。亏格 $g$ 可定向闭曲面
  $$
  \pi_1(\Sigma_g)=\langle a_1,b_1,\dots,a_g,b_g\ \big|\ [a_1,b_1][a_2,b_2]\cdots[a_g,b_g]=1\rangle,\quad g\ge0.
  $$
  特别 $\pi_1(S^2)=1$($g=0$),$\pi_1(T^2)=\mathbb Z^2$
  ($g=1$,关系 $[a,b]=aba^{-1}b^{-1}=1\Rightarrow ab=ba$ 交换)。交换化 $H_1=\pi_1^{\text{ab}}$ 给 $\mathbb Z^{2g}$。
- **自测**:克莱因瓶 $K$ 是两射影面的连通和($K=\mathbb RP^2\#\mathbb RP^2$),
  写出 $\pi_1(K)=\langle a,b\mid aba^{-1}b=1\rangle$,
  并化其交换化得 $H_1(K)\cong\mathbb Z\oplus\mathbb Z/2$(说明 $\mathbb Z/2$ 挠项的来源)。

---

### 第 6 章 · 奇异同调

- **核心**:从 $\pi_1$(只看 1 维环路)升级到**全维度的洞计数**。
  **奇异 $n$-单形**是连续映射 $\sigma:\Delta^n\to X$(标准 $n$-单形 $\Delta^n$ 的连续像),
  **奇异链群** $C_n(X)$ 是其有限线性组合(自由 Abel 群)。
  **边界算子** $\partial_n:C_n\to C_{n-1}$ 取单形的有向面之和,
  核心性质 $\partial^2=0$(边界的边界为零),故 $\mathrm{im}\,\partial_{n+1}\subseteq\ker\partial_n$。
  **奇异同调群** $H_n(X)=\ker\partial_n/\mathrm{im}\partial_{n+1}$
  度量"$n$ 维闭链(无边界)但非边界(不围更高维洞)"的等价类——即 $n$ 维洞。
  关键性质:同伦不变性($X\simeq Y\Rightarrow H_n(X)\cong H_n(Y)$)、
  $H_0$=道路连通分量数、对好对的同伦长正合序列、切除定理。
  奇异同调"定义好但难算",可算性留到 Ch7。
- **飞腾锚点**:**UDOT 16.9×[E05]** —— 奇异链是奇异单形的有限和,边界算子是线性求和,同调群的核/像商 = 点积累加的"闭合度"。
  🟢事实:$\partial_n\sigma=\sum_{i=0}^n(-1)^i\sigma|_{[v_0,\dots,\hat v_i,\dots,v_n]}$
  是交错点积式求和,实现上等同 UDOT 累加;
  $\partial^2=0$ 在代码里须严格保证(稀疏边界矩阵乘两次归零,配合 Iron Law $<2\%$);
  🟡类比:同调群 $H_n$ 是"铁律偏差"的可计算量化——偏差为零($H_n=0$)即正合(该维无洞),偏差非零即"洞"。
- **关键定理**:**同伦不变性 + $H_n$ 的定义**。
  $$
  H_n(X)=Z_n(X)/B_n(X),\quad Z_n=\ker\partial_n\ (\text{闭链}),\ B_n=\mathrm{im}\,\partial_{n+1}\ (\text{边界}),\qquad
  X\simeq Y\ \Rightarrow\ H_n(X)\cong H_n(Y).
  $$
- **自测**:计算点空间 $H_0(\mathrm{pt})=\mathbb Z$、$H_{n\ge1}(\mathrm{pt})=0$;
  再由同伦不变性推出可缩空间(如 $\mathbb R^n$、凸集)的同调与点空间相同($\tilde H_*=0$)。

---

### 第 7 章 · 同调的计算

- **核心**:奇异同调"定义好但难算",本章给可算的模型。
  (i) **球面**:$\tilde H_n(S^k)=\mathbb Z$($n=k$)、$0$(否则),由 Mayer-Vietoris(下章)或胞腔结构;
  (ii) **CW 复形**:用**胞腔链复形** $C_n^{CW}=\mathbb Z\{\text{$n$-胞腔}\}$,
  边界由粘贴映射的度数(degree)给出,核心定理 **$H_n^{CW}(X)\cong H_n^{\text{奇异}}(X)$**
  (胞腔同调 = 奇异同调)——把"无穷维奇异链"压缩成"有限维胞腔链",计算量骤降;
  (iii) **Euler 示性数** $\chi(X)=\sum(-1)^n\#\{n\text{-胞腔}\}=\sum(-1)^n\mathrm{rank}\,H_n(X)$
  是同伦不变量(柯朗《数学是什么》$V-E+F=2$ 的严格化与高维推广);
  (iv) 贝蒂数 $\beta_n=\mathrm{rank}\,H_n$ 是各维洞的个数。
- **飞腾锚点**:**GEMM 9.45G[Lab05]** —— CW 复形把空间拆成各维胞腔的"高维吞吐",胞腔链复形是分维矩阵。
  🟢事实:胞腔边界矩阵的秩计算($\ker/\mathrm{im}$ 求商)是分块矩阵的高维 GEMM 运算;
  每加一个 $k$-胞腔 = 矩阵加一行/列,贝蒂数 $\beta_n=\mathrm{rank}\,H_n$ 由这些矩阵的秩差给出;
  🟡类比:胞腔结构像把形状"分块网格化",同调计算 = 网格关联矩阵的秩分析,
  与 3D 建模的多边形网格拓扑分析同构。
- **关键定理**:**胞腔同调 = 奇异同调 + Euler 示性数**。
  $$
  H_n^{CW}(X)\cong H_n^{\text{奇异}}(X),\qquad
  \chi(X)=\sum_n(-1)^n\,c_n=\sum_n(-1)^n\,\beta_n\quad(c_n=\#n\text{-胞腔},\ \beta_n=\mathrm{rank}\,H_n).
  $$
- **自测**:用 CW 结构(两个 0-胞腔、两个 1-胞腔、一个 2-胞腔)算环面 $T^2$ 的
  $H_0=\mathbb Z,\ H_1=\mathbb Z^2,\ H_2=\mathbb Z$,$\chi=0$;
  并对比球面 $S^2$($\chi=2$)说明 $\chi$ 区分两者。

---

### 第 8 章 · Mayer-Vietoris 序列

- **核心**:同调版的 van Kampen——把空间拆成两块 $X=A\cup B$ 后,
  $H_n(X)$ 由 $H_n(A),H_n(B),H_n(A\cap B)$ 通过一条**长正合序列**连接。
  **Mayer-Vietoris 序列**:
  $\cdots\to H_n(A\cap B)\to H_n(A)\oplus H_n(B)\to H_n(X)\xrightarrow{\partial}H_{n-1}(A\cap B)\to\cdots$,
  连接同态 $\partial$ 把"跨界闭链"降一维归到交的同调。
  它是**计算利器**(配 Ch7 胞腔结构,几乎可算任何 CW 复形的同调),
  也是**正合代数的范本**——每处 $\ker=\mathrm{im}$ 都是 Iron Law。
  配合**切除定理**(挖掉"无害"子集不变同调),Mayer-Vietoris 把"拼接"变成机械化计算:
  把 $S^n$ 拆两个开圆盘,归纳算球面同调;把曲面拆成简单块逐块算。
- **飞腾锚点**:**Iron Law<2%[Lab00]** —— Mayer-Vietoris 是一条处处 $\ker=\mathrm{im}$ 的正合序列,正合性是同调代数的"误差为零"铁律。
  🟢事实:正合性 $H_n(A)\oplus H_n(B)\to H_n(X)\xrightarrow{\partial}H_{n-1}(A\cap B)$
  要求 $\mathrm{im}=\ker$ 严格成立,数值实现须设容差(类 Iron Law $<2\%$);
  $\partial^2=0$ 在边界矩阵上须严格保证;
  🟡类比:连接同态 $\partial$ 像"跨界事务的回滚记录"——
  跨界闭链降一维归档到交的同调,正合性保证无信息丢失(误差为零)。
- **关键定理**:**Mayer-Vietoris 长正合序列**。若 $X=A^\circ\cup B^\circ$,则
  $$
  \cdots\to H_n(A\cap B)\xrightarrow{(i_*,j_*)}H_n(A)\oplus H_n(B)\xrightarrow{k_*-l_*}H_n(X)\xrightarrow{\partial}H_{n-1}(A\cap B)\to\cdots
  $$
  处处正合($\ker=\mathrm{im}$)。
- **自测**:用 Mayer-Vietoris 把 $S^n$ 拆成两个开圆盘 $U,V$(交 $\simeq S^{n-1}$),
  归纳证明 $\tilde H_n(S^n)=\mathbb Z$、$\tilde H_k(S^n)=0$($k\ne n$);
  并说明连接同态 $\partial$ 在归纳步如何把 $H_n(S^n)$ 与 $H_{n-1}(S^{n-1})$ 对应。

---

### 第 9 章 · 上同调

- **核心**:同调的"对偶"。对 Abel 群 $G$(系数),定义**上链群** $C^n(X;G)=\mathrm{Hom}(C_n(X),G)$,
  **上微分** $\delta^n=\mathrm{Hom}(\partial_n,G)$ 满足 $\delta^2=0$,
  **上同调群** $H^n(X;G)=\ker\delta^n/\mathrm{im}\delta^{n+1}$。
  上同调比同调多出**乘法结构**(杯积,下章),因此更"代数"、信息更丰富(同调的 $\oplus$ + 上同调的环)。
  关键工具:**Kronecker 配对** $\langle\varphi,c\rangle=\varphi(c)\in G$
  (上链吃链吐标量,内积式配对)诱导 $H^n(X;G)\times H_n(X)\to G$;
  **泛系数定理**(UCT)在主理想整区上把 $H^n$ 用 $H_n$ 表出——这是通向 Weibel 同调代数 $\mathrm{Ext}$ 的桥。
  Fulton 强调上同调"对偶"视角:$C^n$ 是 $C_n$ 的线性泛函,$\delta$ 是 $\partial$ 的转置。
- **飞腾锚点**:**UDOT 16.9×[E05]** —— Kronecker 配对 $\langle\varphi,c\rangle$ 是上链(线性泛函)与链的内积,本质点积。
  🟢事实:$\varphi\in C^n=\mathrm{Hom}(C_n,G)$ 是 $C_n$ 上的线性泛函,在链基上即一行系数,
  $\langle\varphi,c\rangle$ 是该行与链列的点积(UDOT);上微分 $\delta$ 是 $\partial$ 的转置矩阵,
  计算上同调 = 转置链复形的同调。
  🟡类比:上同调像"对偶空间"——链是向量、上链是对偶向量,Kronecker 配对是两者的内积;
  $\mathrm{Ext}$ 项度量"对偶化丢失的挠信息"。
- **关键定理**:**泛系数定理(UCT)**(主理想整区 $R$ 上)。短正合
  $$
  0\to\mathrm{Ext}^1_R\big(H_{n-1}(X),G\big)\to H^n(X;G)\xrightarrow{h}\mathrm{Hom}_R\big(H_n(X),G\big)\to 0
  $$
  (在域上 $\mathrm{Ext}=0$,$H^n\cong\mathrm{Hom}(H_n,G)\cong H_n$ 的对偶;
  挠项由 $\mathrm{Ext}$ 补回,如 $H^2(\mathbb RP^2;\mathbb Z)\cong\mathbb Z/2$ 尽管 $H_2=0$)。
- **自测**:取 $G=\mathbb Z$,用 UCT 由 $H_1(\mathbb RP^2)=\mathbb Z/2$、$H_2=0$ 推出
  $H^2(\mathbb RP^2;\mathbb Z)\cong\mathrm{Ext}^1(\mathbb Z/2,\mathbb Z)\cong\mathbb Z/2$;
  并说明为何 $H^2\ne H_2$(挠项的"位置移动")。

---

### 第 10 章 · 杯积与 Poincaré 对偶

- **核心**:上同调独有同调没有的**环结构**,全书几何顶峰。
  **杯积**(cup product)$\smile:C^p\times C^q\to C^{p+q}$ 把两上链"拼接"成高维上链
  (用单形顶点分裂 $[v_0,\dots,v_p]\smile[v_p,\dots,v_{p+q}]$ 定义),
  诱导 $H^p(X)\times H^q(X)\to H^{p+q}(X)$,
  使 $H^*(X)=\bigoplus H^n$ 成**分级环**(graded ring)——
  这是上同调优于同调的关键(同调只有 $\oplus$ 无乘法)。
  对**可定向 $n$ 维流形**,**Poincaré 对偶**:与基本类 $[M]\in H_n(M)$ 的杯积给同构
  $H^k(M)\xrightarrow{\smile[M]}H_{n-k}(M)$(贝蒂数对称 $\beta_k=\beta_{n-k}$,流形的深刻对称性)。
  不可定向时用 $\mathbb Z/2$ 系数。Fulton 用环面、曲面的杯积表反复示范,几何画面极强。
- **飞腾锚点**:**Schmidt 正交化** —— Poincaré 对偶是同调与上同调的"维数配对/正交对应",对偶基互为正交补。
  🟡类比:$H^k$ 与 $H_{n-k}$ 在基本类 $[M]$ 下配对,
  像 Schmidt 正交化把一组基配成对偶正交基——每维"洞"与"余维洞"一一对应;
  🟢事实:杯积计算是上链系数的分块乘法,
  正交对偶关系保证 $\beta_k=\beta_{n-k}$(流形 Euler 示性数的对称约束,如奇数维紧致可定向流形 $\chi=0$)。
- **关键定理**:**Poincaré 对偶**。$M$ 紧致可定向 $n$ 维流形,则与基本类 $[M]\in H_n(M;\mathbb Z)$ 的杯积给同构
  $$
  D:H^k(M;\mathbb Z)\xrightarrow{\ \alpha\mapsto\alpha\smile[M]\ }H_{n-k}(M;\mathbb Z),\qquad \forall\,0\le k\le n.
  $$
  推论:贝蒂数对称 $\beta_k=\beta_{n-k}$;奇数维紧致可定向流形 $\chi(M)=0$。
- **自测**:用 Poincaré 对偶说明紧致可定向曲面 $\Sigma_g$($n=2$)满足
  $\beta_0=\beta_2=1,\ \beta_1=2g$,$\chi=2-2g$;
  并验证环面 $\chi(T^2)=0$、球面 $\chi(S^2)=2$。

---

### 第 11 章 · 专题:纤维丛与示性类预告

- **核心**:眺望更远的地平线,把全书工具推向微分拓扑与代数几何。
  **纤维丛**(fiber bundle)$F\to E\xrightarrow{p}B$(局部乘积 $U\times F$,整体可能扭曲)
  是复叠空间的"连续纤维"推广(复叠 = 离散纤维的丛);
  切丛、Möbius 带(不可定向直线丛)、Hopf 纤维化 $S^1\to S^3\to S^2$ 是核心例子。
  **示性类**(characteristic class)是给每个丛贴一个上同调类、度量其"扭曲"的全局不变量:
  **Stiefel-Whitney 类** $w_i\in H^i(B;\mathbb Z/2)$(实丛,$w_1=0\Leftrightarrow$ 可定向)、
  **Chern 类** $c_i\in H^{2i}(B;\mathbb Z)$(复丛,代数几何里的陈类)、
  **Euler 类** $e\in H^n(B;\mathbb Z)$(可定向实丛,Euler 示性数的推广,$e$ 模 2 $=w_n$)。
  本章把这些主题"预告"并指向 Milnor-Stasheff《示性类》、Bott-Tu《微分形式与代数拓扑》。
- **飞腾锚点**:**GEMM 9.45G[Lab05]** —— 纤维丛是"底空间每点挂一片高维纤维",示性类是这种层叠结构的高维不变量。
  🟡类比:丛像 GPU 的张量层级——底空间 $B$ 是外层索引,纤维 $F$ 是每点的内层数据,
  示性类度量"层叠扭曲"(平凡丛扭曲为零,非平凡丛有非零示性类);
  🟢事实:示性类的计算归结为结构群的 Lie 代数上同调(Chern-Weil 理论,用曲率形式的行列式/幂和),
  是高维 GEMM 式的全局运算。
- **关键定理**:**示性类的公理与代表**(预告)。
  实 $n$-丛 $\xi$ 的 Stiefel-Whitney 类 $w_i(\xi)\in H^i(B;\mathbb Z/2)$ 满足
  $w_0=1$、$w(\xi\oplus\eta)=w(\xi)\smile w(\eta)$(Whitney 和公式);
  复 $n$-丛的 Chern 类 $c_i\in H^{2i}$ 满足 $c_0=1$、$c(\xi\oplus\eta)=c(\xi)c(\eta)$;
  Euler 类 $e(\xi)\in H^n(B;\mathbb Z)$ 满足 $e\bmod 2=w_n$。
- **自测**:$\mathbb RP^n$ 的切丛的 $w_1$ 为何刻画不可定向性?并说明 $w_1=0\Leftrightarrow$ 可定向
  (指向 Milnor-Stasheff §4);
  再说明 Hopf 纤维化 $S^1\to S^3\to S^2$ 为何是非平凡 $S^1$-丛(底 $S^2$ 上 $c_1\ne0$)。

---

## §9 全书思想主线(约 200 字)

Fulton 的 11 章是一条"从一维环路到全维对偶"的上升阶梯。
**Ch1-2** 把空间用环路分类:$\pi_1$ 是"一维洞的群",同伦不变量,奠基计算 $\pi_1(S^1)=\mathbb Z$(环绕数=生成元)。
**Ch3-5** 用复叠空间"展开洞"(Galois 对应)、用 van Kampen"拼接群",
实现曲面/图/结点基本群的机械化计算——把"剪贴胞腔"变成"读展示式"。
**Ch6-8** 把视角从"群"升级到"全维 Abel 群":奇异同调 $H_n$ 数各维洞,
胞腔同调把它变成可算的矩阵,Mayer-Vietoris 用正合序列拼接两块——核心铁律是处处 $\ker=\mathrm{im}$(Iron Law)。
**Ch9-10** 取对偶得上同调,杯积赋环结构,Poincaré 对偶揭示流形的维数对称($\beta_k=\beta_{n-k}$)。
**Ch11** 以纤维丛/示性类眺望微分拓扑与代数几何。
全书一以贯之的命题是:**用代数结构(群、环、正合序列)忠实度量几何形状(洞、扭曲、对称)**。

---

## §10 与本仓库其他笔记的交叉引用

- **Munkres《拓扑学》**(stage-2):Fulton 是 Munkres Part II($\pi_1$/覆叠/曲面分类)的**直接下游**。
  Munkres 给了点集地基(连通/紧致 ch3、分离 ch4)与 $\pi_1$ 骨架(ch9-13);
  Fulton 补更深的几何动机(复分析环绕数入口)并推进到 Munkres 未覆盖的
  **奇异同调、上同调、Poincaré 对偶**(Fulton Ch6-10)。读 Fulton Ch6 前应有 Munkres Part I 的连通/紧致打底。
- **Weibel《同调代数》**(stage-3):Fulton Ch6-10 的奇异同调是 Weibel 链复形的**几何原型**。
  Fulton 的链复形 $\partial^2=0$、长正合序列(Mayer-Vietoris, Ch8)、$\mathrm{Ext}$(泛系数定理, Ch9)
  在 Weibel Ch1/Ch2/Ch3 抽象化;读 Fulton 同调部分后再读 Weibel,
  会看到"几何洞"如何变成"代数正合性"——$H_n=\ker/\mathrm{im}$ 是 Weibel 全书的原子。
- **Hartshorne《代数几何》**(stage-3):层上同调 $H^i(X,\mathcal F)$、Serre 对偶、
  Chern 类(Hartshorne 附录 A)的**几何直觉全部来自 Fulton**。
  Fulton Ch10 的 Poincaré 对偶是 Serre 对偶的拓扑蓝本(都是"与基本类配对给同构");
  Ch11 的 Chern 类直接进入代数几何(示性类 = 陈类,陈数控制代数曲面的几何)。
- **AI 锚点(飞腾 D3000M 映射)**:
  - **$\pi_1$ = 洞的分类器**(环路分类一维洞,像拓扑数据的"等价类标号",Ch2 FP16);
  - **复叠空间 = 地址映射寻址**(提升定理通过 $\tilde X\to X$ 重定向,像 TLB 地址翻译,Ch3 TLB);
  - **同调 $H_n$ = 数据缺口度量**($n$ 维闭链/边界的商 = 流图中"闭合但非平凡"的缺口,Ch6 UDOT);
  - **Mayer-Vietoris = 正合拼接的无损铁律**(跨界同调的 $\ker=\mathrm{im}$ 校验,类 Iron Law $<2\%$,Ch8);
  - **Poincaré 对偶 = 维数对称的对偶寻址**(同调与上同调的正交配对,类 Schmidt 正交化,Ch10)。
