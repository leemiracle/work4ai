# David Williams《概率与鞅》 · 快速逐章精读

> **原书名**：Probability with Martingales　**著者**：David Williams　**出版社**：Cambridge Mathematical Textbooks　**年份**：1991
> **读于**：2026-07-03
> **定位**：以「鞅」为现代概率论统一骨架的革命性教材，用条件期望把测度、积分、收敛、大数定律、似然比串成一条主线。
> **特色**：文学化叙述（每章配诗/箴言）与硬核严格证明并存，先建直觉再补技术，是「从测度到鞅」最短且最有趣的一条路。
> **声明**：本文为「快速逐章精读」，每章给核心逻辑串联 + 飞腾锚点 + 关键定理 + 自测题，非逐页翻译。

---

## §0 引言：Williams 的「以鞅统一概率」路线

现代概率论教材的组织方式有两条代表路线。一条是 Shiryaev（GTM95）式的**测度论骨架**：先 $\sigma$-代数、再积分、再收敛、最后才碰鞅——鞅只是高级应用。另一条正是 Williams 开创的**鞅中心化路线**：他看准了「条件期望 + 鞅」是连接测度积分与极限定理的最短桥梁，于是把全书组织成「测度地基（Ch 0-8）→ 条件期望（Ch 11）→ 鞅（Ch 12-15）」的三段式结构，让 Borel-Cantelli、大数定律、Radon-Nikodym 这些「散落」的定理全部成为鞅论的推论或陪衬。

Williams 的赌注是：**一旦掌握条件期望的 Radon-Nikodym 本质和鞅的塔性质，整本概率论就坍缩为少数几条深刻原理的推演**。他的叙述极具个人风格——每章以诗歌或哲学箴言开场，正文穿插「Why?」「Check it!」的对话式催促，证明严格却不枯燥。代价是前 8 章的测度积分基础推进较快，对零基础读者略有门槛；但一旦越过条件期望这道坎，后半部的鞅论如行云流水。对做深度学习的人，鞅论直接关联 SGD 收敛证明与时序差分学习 TD($\lambda$) 的理论分析，是概率研究方向必读。

**读书策略**：Ch 0-5 配合 Shiryaev/Billingsley 已读笔记做「测度积分复习」，重点吃透 $\pi$-$\lambda$ 定理与控制收敛定理这两件反复使用的工具；Ch 9-10 大数定律可对照 Feller 卷一已读的组合直觉；真正值得逐章手推的是 Ch 11-15（条件期望→鞅→UI 鞅→倒向鞅→RN），这是 Williams 全书精华，也是概率研究的核心工具箱。建议每章用 Python 跑 Monte Carlo 验证「理论鞅收敛 vs 模拟样本路径」，特别是 Ch 12 的可选停时与 Ch 13 的 UI 收敛——亲手模拟一条鞅路径并观察「公平游戏长时间无系统漂移」是内化鞅论的最佳方式。

| 书 | 风格 | 严格性 | 适合谁 |
|---|---|---|---|
| **Williams《概率与鞅》** | 鞅中心化、文学化、直觉先于技术 | 高（完整测度论 + 严格证明） | 想用最短路径从测度抵达鞅论核心者 |
| **Shiryaev《概率》GTM95** | 测度论公理化、定理-证明体系、全面 | 极高（Kolmogorov 公理完备） | 追求体系完整、做概率/统计研究者 |
| **Durrett《概率：理论与例子》** | 现代风格、例子驱动、鞅与极限并重 | 高（用测度但克制） | 研究生、准备做概率研究 |
| **Billingsley《概率与测度》** | 测度论详尽、收敛定理为重心 | 高 | 喜欢慢节奏、想彻底吃透测度者 |

---

## §1 全书 16 章骨架一览（飞腾锚点分布）

| 章 | 标题 | 核心概念 | 飞腾锚点 |
|:--:|------|----------|----------|
| 0 | A Branch of Life | 哲学导引、概率直觉 | （导引，无锚点） |
| 1 | Measure Spaces | $\sigma$-代数、可测性、$\pi$-$\lambda$ 定理 | TLB 4.81× |
| 2 | Events | 样本空间、事件 $\sigma$-代数 | UDOT 16.9× |
| 3 | Random Variables | 可测函数、分布、独立性预备 | FP16 3.81× |
| 4 | Independence | 独立 $\sigma$-代数、BC 预备 | matmul 15× |
| 5 | Integration | Lebesgue 积分、单调/控制收敛 | Iron Law <2% |
| 6 | Expectation | $L^p$、Jensen、Hölder、Minkowski | Schmidt 正交化 |
| 7 | Convergence of RVs | a.s.、$L^p$、依概率、依分布及关系 | GEMM 9.45 GFLOPS |
| 8 | Product Measure, Fubini | 乘积测度、Fubini-Tonelli | matmul 15× |
| 9 | Borel-Cantelli Lemmas | 引理与逆定理、$0$-$1$ 律 | 分支预测 0.71/3.14 |
| 10 | Laws of Large Numbers | 弱/强 SLLN、Kolmogorov 三级数 | Iron Law <2% |
| 11 | Conditional Expectation | RN 视角、Jensen 条件版、鞅塔性质 | Schmidt 正交化 |
| 12 | Martingales | 定义、停时、可选停时、Doob 分解 | TLB 4.81× |
| 13 | UI Martingales | 鞅收敛定理、$L^1$ 收敛、上穿不等式 | FP16 3.81× |
| 14 | Backwards Martingales | Hewitt-Savage $0$-$1$ 律、SLLN 新证 | GEMM 9.45 GFLOPS |
| 15 | RN via Martingales / Likelihood Ratio | 似然比、Kakutani 定理 | matmul 15× |
| E | Exercises | 综述题（见 §0 引言带过） | — |

> **飞腾锚点复用说明**：15 章 > 8 个锚点，故合理复用（同一锚点隔数章再出现，标注不同角度），保证相邻章绝不重复。TLB 在 Ch 1（$\sigma$-代数分层）/ Ch 12（filtration 信息塔）双用，前者是「可测集的层级生成」、后者是「信息随时间递增」；Schmidt 正交化在 Ch 6（$L^2$ 内积）/ Ch 11（条件期望=正交投影）呼应，前者建空间、后者做投影；matmul 在 Ch 4（独立张量积）/ Ch 8（Fubini 双重求和）/ Ch 15（似然比矩阵化）三用；Iron Law 在 Ch 5（积分收敛界）/ Ch 10（大数律误差）双用。

---

## 第 0 章 · A Branch of Life（导引：哲学与概率直觉）

**核心**：Williams 以哲学箴言开场，强调概率论是「生活的一个分支」——它不是纯数学游戏，而是刻画不确定性世界的语言。本章不讲定理，只播种直觉：为什么需要测度？为什么独立性是奢侈品？为什么鞅是「公平游戏」的数学化身？这是全书唯一「软」的一章，但它定下了「直觉先行、严格随后」的基调。Williams 反复强调：好的概率论家必须同时握住「严格测度」与「赌博直觉」两端，缺一不可。

**飞腾锚点**：（导引章，不分配锚点，留待 Ch 1 起逐章展开。）

**关键定理**：无。本章给出全书「路线图」：测度→积分→期望→收敛→条件期望→鞅。

**自测**：写下你对「公平赌博」的直觉定义（比如「长期不输不赢」），读到 Ch 12 时再回来对照鞅的严格定义 $E[M_{n+1}|\mathcal{F}_n]=M_n$，看直觉哪里对、哪里错。多数人的直觉会遗漏「条件于信息」这一关键限定。

---

## 第 1 章 · Measure Spaces（测度空间）

**核心**：概率论的严格语言从这里开始。一个测度空间 $(S,\Sigma,m)$ 由集合 $S$、其上的 $\sigma$-代数 $\Sigma$（对可数并/交/补封闭的子集族）、以及测度 $m:\Sigma\to[0,\infty]$（可数可加）构成。$\sigma$-代数刻画「可观测的事件族」——并非所有子集都可测，这是 Banach-Tarski 悖论等「病态」的根源。本章的核心技术工具是 **$\pi$-$\lambda$ 定理**：若两个测度在一个生成 $\sigma$-代数的 $\pi$-系（对交封闭）上一致，则它们在整个 $\sigma$-代数上一致。这是证明「两个测度相等」的标准武器，全书反复使用——后续条件期望的唯一性、分布相等等都靠它。

**飞腾锚点**：🟢 TLB 4.81× [E04] —— Borel $\sigma$-代数 $\mathcal{B}$ 由开集逐层生成（开区间→开集并→Borel 集），正如 TLB（Translation Lookaside Buffer）分层翻译虚拟地址：基本开区间是「叶子页」，复合 Borel 集是高层「聚合页」。命中率提升 4.81× 对应把常用可测集预先「缓存」为 $\sigma$-代数的生成元，避免逐点验证可测性。$\pi$-$\lambda$ 定理的威力正在于：只需在「叶子」上验证，结论自动推广到整层。

**关键定理**（$\pi$-$\lambda$ 定理）：设 $\mathcal{I}$ 为 $\pi$-系，$d(\mathcal{I})$ 为包含 $\mathcal{I}$ 的最小 $\lambda$-系，则
$$d(\mathcal{I})=\sigma(\mathcal{I}).$$
推论：若测度 $\mu_1,\mu_2$ 在 $\pi$-系 $\mathcal{I}$ 上有限且一致，则 $\mu_1=\mu_2$ 于 $\sigma(\mathcal{I})$。重要性：这是「最小生成元决定整体」的数学表述，条件期望唯一性、分布等价判定全赖此。

**自测**：验证 $\{\emptyset,A,A^c,S\}$（$A\subseteq S$）是 $S$ 上最小的非平凡 $\sigma$-代数。再证：$\mathbb{R}$ 上由半开区间族 $\pi$-系 $\{(a,b]:a<b\}$ 生成的 $\sigma$-代数就是 Borel $\sigma$-代数（提示：用 $(a,b]=\bigcap_n(a,b+1/n)$ 表示开区间）。

---

## 第 2 章 · Events（事件）

**核心**：把测度空间特化为**概率空间** $(\Omega,\mathcal{F},P)$：$P(\Omega)=1$。样本空间 $\Omega$ 是所有可能结果的集合，事件 $\sigma$-代数 $\mathcal{F}$ 是「可问概率的问题」的族，概率测度 $P$ 给每个事件赋 $[0,1]$ 中的值。本章强调：选不同的 $\mathcal{F}$ 会改变「什么能被讨论」——$\mathcal{F}=\{\emptyset,\Omega\}$ 时什么都问不了，$\mathcal{F}=2^\Omega$ 时（不可数情形）会产生不可测集（如 $[0,1]$ 上的 Vitali 集）。完备化（completion）把零测集的子集补进 $\mathcal{F}$，是后续操作的常用便利，保证「零概率事件的子集仍可测」。

**飞腾锚点**：🟢 UDOT 16.9× [E05] —— 有限可加性 $P(\bigcup_{i=1}^n A_i)=\sum P(A_i)$（互斥时）本质是加权求和累加。无符号点积（UDOT）硬件指令用 16.9× 吞吐加速这类「概率值批量相加」，正如把一串互斥事件的概率压成单条向量累加指令。连续性（$A_n\uparrow A\Rightarrow P(A_n)\uparrow P(A)$）把有限加法提升为可数加法，对应累加器的「流式」长序列处理。

**关键定理**（概率的连续性）：若 $A_n\uparrow A$（递增），则 $P(A_n)\uparrow P(A)$；若 $A_n\downarrow A$ 且某 $P(A_n)<\infty$，则 $P(A_n)\downarrow P(A)$。这是「从有限可加到可数可加」的桥梁，也是后续 Borel-Cantelli、鞅收敛的技术支点。

**自测**：掷两枚公平骰子，$\Omega$ 有 36 点。取 $\mathcal{F}=2^\Omega$（有限情形全可测）。求「点数和为 7」的概率 $P(\{(i,j):i+j=7\})=6/36=1/6$。再写出使「点数和」可测的最小 $\sigma$-代数（即 $\sigma(S)=\{\text{和为$k$的集合}:k\}$ 的并交补闭包）。

---

## 第 3 章 · Random Variables（随机变量）

**核心**：随机变量 $X$ 是**可测函数** $X:(\Omega,\mathcal{F})\to(\mathbb{R},\mathcal{B})$——要求 $\{X\leq x\}\in\mathcal{F}$ 对所有 $x$，即「$X$ 落在某区间的概率可被讨论」。可测性是「函数与 $\sigma$-代数相容」的条件。$X$ 的**分布** $\mu_X(B)=P(X\in B)$ 把概率从 $\Omega$ 推到 $\mathbb{R}$ 上，分布函数 $F_X(x)=P(X\leq x)$ 是其等价描述。本章建立「随机变量 = 可测函数」「分布 = 像测度」的核心对应，为后续期望与收敛奠基。一个关键事实：可测函数对极限运算封闭，这保证极限操作不「逃出」$\sigma$-代数。

**飞腾锚点**：🟡 FP16 3.81× [L01] —— 可测函数 $X:\Omega\to\mathbb{R}$ 的数值实现受限于浮点精度：重尾分布（如 Cauchy）的极端取值在 FP16（3.81× 加速但动态范围窄，最大 $\sim 65504$）下会溢出或下溢，正揭示了「有限位浮点表示随机变量」的精度-范围权衡。模拟大偏差事件或重尾过程时需切回 FP32/FP64，否则分布尾部被「截断」导致期望估计偏倚。

**关键定理**（可测函数的封闭性）：若 $X,Y$ 可测，则 $X+Y$、$XY$、$\sup_n X_n$、$\inf_n X_n$、$\limsup X_n$、$\liminf X_n$ 均可测。可测函数的极限仍可测——这保证极限操作不「逃出」$\sigma$-代数，是后续收敛定理的前提。

**自测**：$X$ 取 $-1,0,2$ 概率各 $1/4,1/2,1/4$。写出分布函数 $F_X(x)$（阶梯函数，在 $-1,0,2$ 处跳跃），并验证 $E[X]=\int x\,dF_X=1/4$。再判断 $Y=X^2$ 是否可测（是），求 $Y$ 的分布（取 $0,1,4$ 概率 $1/2,1/4,1/4$）。

---

## 第 4 章 · Independence（独立性）

**核心**：独立性是概率论中最强也最奢侈的结构假设。事件 $A,B$ 独立指 $P(A\cap B)=P(A)P(B)$；$\sigma$-代数 $\mathcal{G},\mathcal{H}$ 独立指其中任取事件均独立；随机变量独立指其生成 $\sigma$-代数独立。本章给出独立性的多种等价刻画（用示性函数、用分布分解），并为下一章的 Borel-Cantelli 做准备。关键洞察：独立性使得「联合 = 边缘的乘积」，从而乘积测度（Ch 8）成为处理独立结构的天然框架。Williams 特别强调：真实世界中完全独立极罕见，独立性是「可计算性」的代价，工程建模常需检验其是否近似成立。

**飞腾锚点**：🟡 matmul 15× [V03] —— 独立随机变量的联合分布 $P((X,Y)\in A\times B)=P(X\in A)P(Y\in B)$ 是边缘分布的（张量）乘积，正如独立子系统的状态空间是张量积空间。矩阵化运算（matmul 15× 加速）服务于「联合分布 = 边缘分布外积」的批量计算，把 $\mathcal{F}\otimes\mathcal{G}$ 的结构展开。这与 Ch 8 的乘积测度、Fubini 一脉相承。

**关键定理**（独立性等价刻画）：$X,Y$ 独立 $\iff$ 联合分布 $\mu_{(X,Y)}=\mu_X\otimes\mu_Y$（乘积测度）$\iff$ 对有界可测 $f,g$，$E[f(X)g(Y)]=E[f(X)]\,E[g(Y)]$。后者把「独立性」翻译为「期望分解」，是工程中最实用的判据。

**自测**：掷三枚公平硬币，$X_i\in\{-1,+1\}$。验证 $X_1,X_2,X_3$ 两两独立。再判断 $X_1X_2$ 与 $X_2X_3$ 是否独立（不独立，因 $(X_1X_2)(X_2X_3)=X_1X_3$ 提供了信息耦合）。这说明「两两独立」弱于「相互独立」。

---

## 第 5 章 · Integration（积分）

**核心**：Lebesgue 积分是期望的严格基础。对非负可测 $f$，先用简单函数 $s_n\uparrow f$ 逼近，定义 $\int f=\lim\int s_n$；一般 $f=f^+-f^-$ 分别积分。三大收敛定理是本章灵魂：**单调收敛**（$0\leq f_n\uparrow f\Rightarrow\int f_n\uparrow\int f$）、**Fatou 引理**（$\int\liminf f_n\leq\liminf\int f_n$）、**控制收敛定理**（$|f_n|\leq g$，$g$ 可积，$f_n\to f$ 则 $\int f_n\to\int f$）。它们把「极限穿过积分号」的交换合法化，是后续所有极限定理的技术引擎。三者各有适用场景：单调收敛处理非负递增、Fatou 处理一般下极限、控制收敛处理有界收敛，强度递增、条件递严。

**飞腾锚点**：🟡 Iron Law <2% [Lab00] —— 控制收敛定理保证积分极限误差可控：$|\int f_n-\int f|\to0$，正如性能铁律要求 CPI 误差 $<2\%$ 才可信。简单函数逼近 $s_n\uparrow f$ 的截断误差类比「指令数估计误差」，单调收敛确保误差单调下降不反弹；控制函数 $g$ 的存在性则类比「误差预算有上界」——无界漂移（如无控制函数）会破坏误差铁律。

**关键定理**（控制收敛定理，DCT）：若 $f_n\to f$ a.s.，$|f_n|\leq g$，$\int g<\infty$，则
$$\lim_{n\to\infty}\int f_n\,d\mu=\int f\,d\mu.$$
重要性：DCT 是全概率论最常用的「换序工具」，期望、特征函数、条件期望的大量性质都依赖它。

**自测**：$\Omega=[0,1]$，$f_n(x)=n\cdot\mathbf{1}_{(0,1/n)}(x)$。$f_n\to 0$ 点态，但 $\int f_n=1\not\to 0$。这说明缺「控制函数」时 DCT 失效——找一个 $g$ 控制 $f_n$ 吗？（找不到，因 $\sup_n f_n(x)=1/x$ 在 $0$ 附近无界，不可积。）这个反例深刻揭示「点态收敛 $\neq$ 积分收敛」。

**三大收敛定理速查**：

| 定理 | 条件 | 结论 | 适用场景 |
|------|------|------|----------|
| 单调收敛 MCT | $0\leq f_n\uparrow f$ | $\int f_n\uparrow\int f$ | 非负逼近、定义积分 |
| Fatou 引理 | $f_n\geq0$ | $\int\liminf f_n\leq\liminf\int f_n$ | 排除「质量泄漏」 |
| 控制收敛 DCT | $|f_n|\leq g\in L^1$，$f_n\to f$ | $\int f_n\to\int f$ | 换序、期望交换 |

> 强度关系：MCT 最弱（需单调非负）< Fatou（仅需非负）< DCT 最强（需控制函数）；三者条件递严、结论递强。工程中 DCT 用得最多，但「找到控制函数 $g$」常是难点。

---

## 第 6 章 · Expectation（期望）

**核心**：期望 $E[X]=\int X\,dP$ 是 Lebesgue 积分在概率空间的特例。本章建立 $L^p$ 空间（$\|X\|_p=(E|X|^p)^{1/p}$）与三大经典不等式：**Jensen**（凸 $\varphi$：$\varphi(E[X])\leq E[\varphi(X)]$）、**Hölder**（$\|XY\|_1\leq\|X\|_p\|Y\|_q$，$1/p+1/q=1$）、**Minkowski**（$\|X+Y\|_p\leq\|X\|_p+\|Y\|_p$）。$L^2$ 是内积空间，为下一章条件期望的「正交投影」解释埋下伏笔。期望的线性性（无需独立）是最常用工具。$L^p$ 空间的完备性（Riesz-Fisher 定理）保证 Cauchy 序列收敛，是 Hilbert/Banach 空间结构的基础。

**飞腾锚点**：🟢 Schmidt 正交化 —— $L^2(\Omega,\mathcal{F},P)$ 是 Hilbert 空间，内积 $\langle X,Y\rangle=E[XY]$，范数 $\|X\|_2=\sqrt{E[X^2]}$。Hölder 不等式 $p=q=2$ 即 Cauchy-Schwarz $|E[XY]|\leq\|X\|_2\|Y\|_2$，几何上是对偶配对。Schmidt 正交化是 $L^2$ 中构造正交基的算法，为 Ch 11 条件期望（=正交投影）提供离散原型——条件期望就是把随机变量投影到「已知信息」生成的子空间。

**关键定理**（Jensen 不等式）：$\varphi$ 凸，$X$ 可积，则
$$\varphi(E[X])\leq E[\varphi(X)].$$
（严格凸时等号成立 $\iff X$ a.s. 常数。）重要性：这是证明 $L^p$ 嵌入（$p\geq q\Rightarrow L^p\subseteq L^q$ 有限测度）、鞅凸性（$|M_n|^p$ 是下鞅）、信息论 Gibbs 不等式的基础。

**自测**：$X\sim N(0,1)$，验证 Jensen：$\varphi(x)=x^2$ 凸，$E[X]^2=0\leq E[X^2]=1$。再用 Hölder（$p=q=2$）证明 $|E[X]|^2\leq E[X^2]$（即 Cauchy-Schwarz 的特例）。进一步：$\varphi(x)=e^x$ 凸，验证 $e^{E[X]}\leq E[e^X]$，取 $X\sim N(0,1)$ 算两端值（$1$ vs $\sqrt{e}$）。

---

## 第 7 章 · Convergence of Random Variables（收敛模式）

**核心**：本章是全书「关系图」最密集的一章。四种收敛模式：**几乎必然（a.s.）**（$P(X_n\to X)=1$）、**$L^p$ 收敛**（$E|X_n-X|^p\to0$）、**依概率**（$\forall\varepsilon,\;P(|X_n-X|>\varepsilon)\to0$）、**依分布**（$F_n(x)\to F(x)$ 于 $F$ 连续点）。关系链：a.s. 或 $L^p$ $\Rightarrow$ 依概率 $\Rightarrow$ 依分布；$L^p$ 与 a.s. 互不蕴含（各有反例）。Skorokhod 表示定理把依分布收敛提升为 a.s. 收敛（构造新概率空间），是技术利器。这张关系图是后续所有极限定理（BC、LLN、CLT）的判别框架——知道一个收敛「属于哪一级」就决定了能用哪些工具。

**飞腾锚点**：🟡 GEMM 9.45 GFLOPS [Lab05] —— 收敛模式的验证常靠 Monte Carlo 大样本模拟：生成 $N$ 条样本路径判断「依概率收敛到 $X$」的频率。GEMM 9.45 GFLOPS 的吞吐决定大样本（$N=10^6$）收敛验证的速度——底层矩阵吞吐上限制约了「经验频率逼近理论概率」的精度。a.s. 收敛需要「几乎每条路径」都收敛，模拟代价远高于依概率（只需统计频率）。

**关键定理**（收敛关系图）：
$$\text{a.s.}\Rightarrow\text{依概率}\Rightarrow\text{依分布};\qquad L^p\Rightarrow\text{依概率};\qquad L^p\nLeftrightarrow\text{a.s.}$$
反例：$X_n=\mathbf{1}_{[k/2^m,(k+1)/2^m]}$（游走区间，$n=2^m+k$）依概率 $\to0$ 但不 a.s. $\to0$（每点无穷次被覆盖）；$L^p$ 与 a.s. 各有独立反例。

**自测**：$\Omega=[0,1]$，$X_n=\mathbf{1}_{[0,1/n]}$。证明 $X_n\to 0$ 依概率、a.s.、且 $L^1$（$\int X_n=1/n\to0$）三者同时成立。再构造游走区间序列 $X_{2^m+k}=\mathbf{1}_{[k/2^m,(k+1)/2^m]}$，证明它依概率 $\to0$ 但不 a.s. $\to0$（每点被无穷次覆盖）。

**四收敛模式速查**：

| 模式 | 定义 | 强度 | 典型反例/备注 |
|------|------|:----:|--------------|
| a.s. 收敛 | $P(X_n\to X)=1$ | 最强 | 蕴含依概率；不被 $L^p$ 蕴含 |
| $L^p$ 收敛 | $E|X_n-X|^p\to0$ | 强 | 蕴含依概率；不蕴含 a.s. |
| 依概率 | $P(|X_n-X|>\varepsilon)\to0$ | 中 | a.s.、$L^p$ 均蕴含之 |
| 依分布 | $F_n(x)\to F(x)$（连续点） | 最弱 | 只关分布形状，不关样本点 |

> Skorokhod 表示：依分布收敛可经「换概率空间」提升为 a.s. 收敛，是证明依分布结果的技术利器。

---

## 第 8 章 · Product Measure, Fubini（乘积测度与 Fubini 定理）

**核心**：两个测度空间 $(S_1,\Sigma_1,\mu_1)$、$(S_2,\Sigma_2,\mu_2)$ 可构造乘积空间 $(S_1\times S_2,\Sigma_1\otimes\Sigma_2,\mu_1\times\mu_2)$，其中乘积测度由 $\mu_1\times\mu_2(A_1\times A_2)=\mu_1(A_1)\mu_2(A_2)$ 在矩形上定义再经 Carathéodory 扩张。**Fubini 定理**（及 Tonelli 版本）允许交换积分次序：$\int\int f\,d\mu_1\,d\mu_2=\int f\,d(\mu_1\times\mu_2)=\int\int f\,d\mu_2\,d\mu_1$，前提是 $f$ 可积（Fubini）或非负（Tonelli）。这是处理「多随机变量联合期望」的核心工具，独立结构下尤其强大——独立和的期望等于期望之和、方差可加等性质都源自 Fubini + 独立性。

**飞腾锚点**：🟢 matmul 15× [V03] —— Fubini 定理 $\sum_i\sum_j a_{ij}=\sum_j\sum_i a_{ij}$ 本质是双重求和交换次序，与矩阵乘法 $C_{ik}=\sum_j A_{ij}B_{jk}$ 的行列累加同构。matmul 15× 加速直接服务于「累次积分 = 矩阵运算」的批量计算，把 Fubini 的换序压成单条矩阵乘指令。连续情形下 $\int\int f(x,y)\,dx\,dy$ 离散化为网格求和后同样受惠。

**关键定理**（Fubini-Tonelli）：$f\geq0$ 可测（Tonelli）或 $f$ 可积（Fubini），则
$$\int_{S_1\times S_2} f\,d(\mu_1\times\mu_2)=\int_{S_1}\!\Big(\int_{S_2}f\,d\mu_2\Big)d\mu_1=\int_{S_2}\!\Big(\int_{S_1}f\,d\mu_1\Big)d\mu_2.$$
重要性：独立随机变量和的期望、卷积分布、二维均匀采样全赖此。

**自测**：$X,Y$ 独立，$X,Y\sim U[0,1]$。用 Fubini 算 $E[XY]$。（$E[XY]=\int_0^1\int_0^1 xy\,dx\,dy=(1/2)^2=1/4$，验证 $=E[X]E[Y]$。）再算 $E[\max(X,Y)]$（需分 $x>y$ 与 $x\leq y$ 两区域，答案 $2/3$）。

---

## 第 9 章 · The Borel-Cantelli Lemmas（Borel-Cantelli 引理）

**核心**：Borel-Cantelli 引理判定「事件无穷多次发生」。**第一引理**（无需独立）：若 $\sum P(A_n)<\infty$，则 $P(A_n\text{ i.o.})=0$——收敛级数意味着事件最终停止。**第二引理**（需独立）：若 $A_n$ 独立且 $\sum P(A_n)=\infty$，则 $P(A_n\text{ i.o.})=1$——发散级数下独立事件必然无穷多次发生。两者合称 Borel-Cantelli 的「$0$-$1$ 律」：在独立条件下，「无穷多次」只有 0 或 1 两种可能，无中间地带。这是强大数律、Kolmogorov $0$-$1$ 律的关键引理，也是「几乎必然」与「依概率」之间最强的一座桥梁。

**飞腾锚点**：🟡 分支预测 0.71 vs 3.14 [Lab02] —— $A_n$ 是否「无穷多次发生」是一个极限判定（limsup 事件 $\bigcap_N\bigcup_{n\geq N}A_n$），分支预测器对「下一次是否触发」的连续赌注，正如 BC 引理在「级数收敛/发散」的边界上判定命运的 $0$-$1$：预测命中（0.71 周期）类比级数收敛后事件「不再发生」的稳态，未命中（3.14 周期）类比发散级数下事件「持续触发」的活跃态。

**关键定理**（Borel-Cantelli 双引理）：
$$\sum P(A_n)<\infty\Rightarrow P(A_n\text{ i.o.})=0;\qquad A_n\text{ 独立},\,\sum P(A_n)=\infty\Rightarrow P(A_n\text{ i.o.})=1.$$
重要性：第二引理的独立性不可省——存在相依反例使 $\sum P(A_n)=\infty$ 但 $P(A_n\text{ i.o.})=0$。

**自测**：掷公平硬币，$A_n=\{$第 $n$ 次正面$\}$，$P(A_n)=1/2$，$\sum=\infty$ 且独立。由 BC 第二引理，正面无穷多次发生（a.s.）。现令 $B_n=\{$第 $n$ 至 $n+99$ 次连续正面$\}$，估计 $P(B_n)\approx(1/2)^{100}$，判断 $\sum_n P(B_n)$ 是否发散（$\approx n/2^{100}\to\infty$，发散），故 $B_n$ 也 i.o.——即任意长连续正面串会无穷多次出现。

---

## 第 10 章 · Laws of Large Numbers（大数定律）

**核心**：大数定律是概率论对「频率稳定」承诺的兑现。**弱大数律**（WLLN）：$\bar X_n\xrightarrow{P}\mu$；**强大数律**（SLLN）：$\bar X_n\xrightarrow{\text{a.s.}}\mu$。Williams 的特色是用 **Kolmogorov 三级数定理**给出 SLLN 的精细判据——三级数（截尾概率级数、截尾期望级数、截尾方差级数）同时收敛是 $\sum X_n$ a.s. 收敛的充要条件。这比 Chebyshev 的粗界精确得多，也是独立随机变量级数收敛的终极工具。SLLN 是 Ch 14 倒向鞅证明的预热——那里会用更优雅的方式重证。

**飞腾锚点**：🟡 Iron Law <2% [Lab00] —— SLLN 保证 $\bar X_n\to\mu$ a.s.，收敛速度由 Kolmogorov 极大值不等式 $P(\max_{k\leq n}|S_k|>\varepsilon)\leq Var(S_n)/\varepsilon^2$ 控制——这是一条「误差铁律」：给定可接受误差 $\varepsilon$，方差决定最小 $n$，正如性能工程中 CPI 必须 $<2\%$ 才可信。「采样多少次才够」的工程决策直接套用此界，是 A/B 测试、民意调查样本量计算的理论基础。

**关键定理**（Kolmogorov 三级数定理）：独立 $X_n$，$\sum X_n$ a.s. 收敛 $\iff$ 对某 $c>0$，下列三级数均收敛：
$$\sum P(|X_n|>c),\quad \sum E[X_n^{(c)}],\quad \sum Var(X_n^{(c)}),$$
其中 $X_n^{(c)}=X_n\mathbf{1}_{\{|X_n|\leq c\}}$ 为截尾。重要性：SLLN 是其推论；它是判定「独立扰动求和是否收敛」的最强工具，比二阶矩方法精细得多。

**自测**：$X_i$ iid，$E[X_i]=\mu$，$Var=\sigma^2<\infty$。用 SLLN 说明 $\bar X_n\xrightarrow{\text{a.s.}}\mu$。给定 $\sigma^2=1$，$\varepsilon=0.1$，用 Kolmogorov 不等式估计需 $n\geq$ 多少使 $P(\max_{k\leq n}|\bar X_k-\mu|>0.1)\leq 0.05$。（解 $\sigma^2/(n\varepsilon^2)\leq0.05$ 得 $n\geq1/(0.01\times0.05)=2000$。）

---

## 第 11 章 · Conditional Expectation（条件期望）

**核心**：**这是全书的枢纽章**。给定子 $\sigma$-代数 $\mathcal{G}\subseteq\mathcal{F}$，条件期望 $Y=E[X|\mathcal{G}]$ 是满足 (i) $Y$ 是 $\mathcal{G}$-可测、(ii) $\int_A Y=\int_A X$ 对所有 $A\in\mathcal{G}$ 的唯一（a.s.）随机变量。**Radon-Nikodym 定理**保证其存在性：$Y=d\nu/d\mu|_\mathcal{G}$，其中 $\nu(A)=\int_A X\,dP$。关键性质：**塔性质** $E[E[X|\mathcal{G}]|\mathcal{H}]=E[X|\mathcal{H}]$（$\mathcal{H}\subseteq\mathcal{G}$，信息更粗则投影更远）、**Jensen 条件版** $\varphi(E[X|\mathcal{G}])\leq E[\varphi(X)|\mathcal{G}]$、独立性下 $E[X|\mathcal{G}]=E[X]$。条件期望是鞅的定义原料，也是信号处理（Kalman 滤波）、强化学习（值函数估计）、统计推断（后验期望）的数学基础。

**飞腾锚点**：🟢 Schmidt 正交化 —— 在 $L^2$ 中，条件期望 $E[X|\mathcal{G}]$ 就是 $X$ 向「$\mathcal{G}$-可测子空间」的**正交投影**：$X-E[X|\mathcal{G}]\perp\mathcal{G}$（即与所有 $\mathcal{G}$-可测随机变量不相关）。这是条件期望最直观的几何解释，也是最小均方估计（MMSE）的数学核心：$E[X|\mathcal{G}]=\arg\min_{Y\in\mathcal{G}}E[(X-Y)^2]$。Schmidt 正交化正是构造此类正交投影的算法——把 $X$ 分解为「可由 $\mathcal{G}$ 解释的部分」与「正交残差」，这正是 Kalman 滤波、线性回归的本质。

**关键定理**（条件期望的 RN 存在性与塔性质）：$X$ 可积，$\mathcal{G}\subseteq\mathcal{F}$，则存在唯一 a.s. 的 $\mathcal{G}$-可测 $E[X|\mathcal{G}]$ 使
$$\int_A E[X|\mathcal{G}]\,dP=\int_A X\,dP,\quad\forall A\in\mathcal{G};\qquad \mathcal{H}\subseteq\mathcal{G}\Rightarrow E[E[X|\mathcal{G}]|\mathcal{H}]=E[X|\mathcal{H}].$$
重要性：塔性质是「信息递减时投影嵌套」的表述，是 Ch 12 鞅定义、Ch 14 倒向鞅的直接原料。

**自测**：掷两枚公平硬币 $X_1,X_2\in\{0,1\}$，$S=X_1+X_2$。计算 $E[S|\sigma(X_1)]$。（答：$X_1+1/2$，因 $E[X_2|X_1]=E[X_2]=1/2$，独立性使条件期望退化为无条件。）验证塔性质 $E[E[S|\sigma(X_1)]|\{\emptyset,\Omega\}]=E[S]=1$。

**条件期望五大性质清单**（务必内化，全书反复使用）：

1. **塔性质**：$\mathcal{H}\subseteq\mathcal{G}\Rightarrow E[E[X|\mathcal{G}]|\mathcal{H}]=E[X|\mathcal{H}]$（信息越粗投影越远）。
2. **取出已知**：$Y$ 是 $\mathcal{G}$-可测 $\Rightarrow E[XY|\mathcal{G}]=Y\,E[X|\mathcal{G}]$（已知量可提出条件号外）。
3. **独立性退化**：$X$ 与 $\mathcal{G}$ 独立 $\Rightarrow E[X|\mathcal{G}]=E[X]$（无条件期望）。
4. **Jensen 条件版**：$\varphi$ 凸 $\Rightarrow \varphi(E[X|\mathcal{G}])\leq E[\varphi(X)|\mathcal{G}]$。
5. **$L^2$ 正交投影**：$E[X|\mathcal{G}]=\arg\min_{Y\in\mathcal{G}}E[(X-Y)^2]$（MMSE 最优）。

> 性质 1-4 是代数运算规则，性质 5 是几何解释。Ch 12 鞅的定义 $E[M_{n+1}|\mathcal{F}_n]=M_n$ 直接用性质 3（独立增量的条件期望退化）。

---

## 第 12 章 · Martingales（鞅）

**核心**：**全书高潮开始**。给定 filtration（递增 $\sigma$-代数流）$\{\mathcal{F}_n\}$，过程 $\{M_n\}$ 是**鞅**若 $M_n$ 是 $\mathcal{F}_n$-可测、可积，且 $E[M_{n+1}|\mathcal{F}_n]=M_n$（公平游戏：给定当前信息，下一时刻期望不变）。上鞅（$\leq$，不利博弈）、下鞅（$\geq$，有利博弈）是其变体。**停时** $T$ 是「不预知未来」的随机时间（$\{T=n\}\in\mathcal{F}_n$）。**Doob 可选停时定理**：有界停时下 $E[M_T]=E[M_0]$——公平游戏任何「不偷看未来」的策略都不改变期望。**Doob 分解**把任何可积适应过程唯一拆为鞅 + 可料过程（可预测的漂移）。鞅是连接概率论与分析（调和函数、位势论、Dirichlet 问题）的桥梁。

**飞腾锚点**：🟢 TLB 4.81× [E04] —— filtration $\{\mathcal{F}_n\}$ 是**递增的信息塔**：$\mathcal{F}_0\subseteq\mathcal{F}_1\subseteq\cdots$，每一步揭示更多信息，正如 TLB 的层级缓存（信息逐层加载）。鞅性质 $E[M_{n+1}|\mathcal{F}_n]=M_n$ 要求「关于当前信息层的最优预测等于现值」——只有与信息层「对齐」的预测才公平。TLB 命中率 4.81× 对应把「最近用过的信息层」缓存，正如鞅论中「$\mathcal{F}_n$-可测」要求 $M_n$ 只用当前层信息。「可观测的信息层级」决定鞅定义，正如「可寻址的页层级」决定内存访问。

**关键定理**（Doob 可选停时定理）：$\{M_n\}$ 鞅，$T$ 有界停时（$T\leq N$），则
$$E[M_T]=E[M_0].$$
推广：$S\leq T$ 有界停时，$E[M_T|\mathcal{F}_S]=M_S$。重要性：这是「公平游戏无必胜策略」的数学表述——任何不偷看未来的停时策略都不改变期望，是赌博系统不可能性定理、美式期权定价的基础。

**自测**：$X_i$ iid，$E[X_i]=0$，$S_n=\sum_{i=1}^n X_i$。验证 $\{S_n\}$ 关于 $\mathcal{F}_n=\sigma(X_1,\dots,X_n)$ 是鞅。（$E[S_{n+1}|\mathcal{F}_n]=S_n+E[X_{n+1}]=S_n$。）取停时 $T=\min\{n:S_n\geq 1\}\wedge 10$，问 $E[S_T]$ 是否等于 $0$？（有界停时，由可选停时定理，是。）再问：$T'=\min\{n:S_n\geq 1\}$（无界）是否也满足 $E[S_{T'}]=0$？（需额外条件，如 $T'<\infty$ a.s. 且 UI，否则可能失效——这是赌徒破产悖论的根源。）

**鞅三类型对比**（关于 filtration $\mathcal{F}_n$）：

| 类型 | 条件期望关系 | 直觉 | 典型例子 |
|------|-------------|------|----------|
| 鞅 (martingale) | $E[M_{n+1}\|\mathcal{F}_n]=M_n$ | 公平游戏 | 独立零均值和 $S_n=\sum X_i$ |
| 上鞅 (supermartingale) | $E[M_{n+1}\|\mathcal{F}_n]\leq M_n$ | 不利博弈（递减趋势） | 赌场中赌徒资本、非负超鞅 |
| 下鞅 (submartingale) | $E[M_{n+1}\|\mathcal{F}_n]\geq M_n$ | 有利博弈（递增趋势） | $|M_n|$（鞅的绝对值）、$M_n^2$（$L^2$ 鞅） |

> 记忆：super = 「superior 过去」（期望 $\leq$ 现值，在下降）；sub = 「inferior 过去」（期望 $\geq$ 现值，在上升）。Doob 分解：任何适应过程 = 鞅 + 可料漂移。

---

## 第 13 章 · UI Martingales（一致可积鞅）

**核心**：**本章是鞅论的精华**。一致可积（UI）族 $\{X_i\}$ 要求 $\sup_i E[|X_i|\mathbf{1}_{|X_i|>K}]\to0$（$K\to\infty$），比「$L^1$ 有界」更强——它要求尾部一致小，不仅是「平均有界」而是「极端值对期望的贡献一致可控」。**鞅收敛定理**：UI 上鞅 a.s. 收敛到某 $X_\infty$ 且 $L^1$ 收敛（$E|M_n-X_\infty|\to0$），并满足 $M_n=E[X_\infty|\mathcal{F}_n]$（鞅的「反向表示」）。**Levy 上穿/下穿不等式**给出收敛振荡次数的界，是证明 a.s. 收敛的关键工具。UI 是「$L^1$ 收敛」与「a.s. 收敛」同时成立的充要条件，是连接鞅论与遍历定理、调和分析的枢纽。

**飞腾锚点**：🟡 FP16 3.81× [L01] —— UI 要求尾部积分 $\sup_n E[|M_n|\mathbf{1}_{|M_n|>K}]$ 一致小，数值上对「极端取值的加权」敏感。FP16（3.81× 加速但精度低、动态范围窄）下，鞅尾部的极端跳变可能因精度损失而被低估，影响 UI 判定。模拟长程鞅收敛时，需在「精度（FP64，准确捕获尾部）」与「速度（FP16，快速跑长链）」间权衡——这正是 UI 条件「尾部一致可控」的工程映射：精度不足会导致「假 UI」判定。

**关键定理**（UI 鞅收敛定理）：$\{M_n,\mathcal{F}_n\}$ UI 鞅 $\iff$ 存在 $X_\infty\in L^1$ 使 $M_n\xrightarrow{L^1}X_\infty$ 且 $M_n=E[X_\infty|\mathcal{F}_n]$。Levy 上穿不等式：$E[\text{$[a,b]$ 上穿次数}]\leq\frac{E[(M_n-a)^-]}{b-a}$，蕴含 a.s. 收敛。重要性：UI 是「a.s. 收敛 + $L^1$ 收敛同时成立」的充要条件，非 UI 的 $L^1$ 有界鞅可 a.s. 收敛但不 $L^1$ 收敛。

**自测**：$M_n=E[X|\mathcal{F}_n]$（$X\in L^1$，$\mathcal{F}_n\uparrow\mathcal{F}$）。证明 $\{M_n\}$ 是 UI 鞅（用 $|M_n|\leq E[|X||\mathcal{F}_n]$ 与 Jensen，再证 UI：$E[|M_n|\mathbf{1}_{|M_n|>K}]\leq E[|X|\mathbf{1}_{|X|>K'}]$，后者 $\to0$）。这构造了「所有 UI 鞅都形如 $E[X_\infty|\mathcal{F}_n]$」的反向刻画。

**UI 判据与收敛层次**：

| 条件 | a.s. 收敛 | $L^1$ 收敛 | 反向表示 |
|------|:---------:|:---------:|----------|
| 鞅 + $L^1$ 有界（$\sup E|M_n|<\infty$） | ✅（Doob） | ❌（不一定） | ❌ |
| 鞅 + 一致可积 (UI) | ✅ | ✅ | $M_n=E[X_\infty\|\mathcal{F}_n]$ |
| $M_n=E[X\|\mathcal{F}_n]$，$X\in L^1$ | ✅ | ✅ | 天然 UI |

> 经典反例：$S_n=$ 对称随机游走首达 $+1$ 前，$L^1$ 有界鞅 a.s. 收敛但不 $L^1$ 收敛。UI 是「a.s. + $L^1$ 双收敛」的精确充要条件。

---

## 第 14 章 · Backwards Martingales（倒向鞅）

**核心**：倒向鞅是**时间反向**的鞅：$\{M_{-n}\}$ 关于递减 filtration $\{\mathcal{F}_{-n}\}$（$\mathcal{F}_{-n}\supseteq\mathcal{F}_{-(n+1)}$）满足 $E[M_{-n}|\mathcal{F}_{-(n+1)}]=M_{-(n+1)}$。倒向鞅天然 UI（因 $M_{-n}=E[M_{-1}|\mathcal{F}_{-n}]$，同 Ch 13 的构造），故总收敛。**Hewitt-Savage $0$-$1$ 律**：可交换事件（对有限置换不变）的概率非 0 即 1。本章最精彩的应用是**用倒向鞅重新证明 SLLN**：对称平均 $M_{-n}=\frac{S_n}{n}=E[X_1|\mathcal{T}_n]$（$\mathcal{T}_n$ 为尾对称 $\sigma$-代数）是倒向鞅，收敛到 $E[X_1|\bigcap\mathcal{T}_n]$，再由 Hewitt-Savage 得该极限为常数 $E[X_1]$。这是 SLLN 最优雅的证明——无需三级数定理的繁琐，直接由鞅收敛 + 0-1 律一步到位。

**飞腾锚点**：🟡 GEMM 9.45 GFLOPS [Lab05] —— 倒向鞅的对称平均 $M_{-n}=\bar X_n$ 涉及「逆时间」的样本均值阵列计算，$n$ 从大到小（信息递减、样本数增加）。GEMM 9.45 GFLOPS 的吞吐支持大规模对称平均的可逆阵列模拟——「正向加信息、反向减信息」的双向矩阵运算，正如倒向鞅把 SLLN 嵌入鞅收敛框架：同一组样本均值，正向看是 LLN，反向看是倒向鞅收敛。

**关键定理**（倒向鞅收敛 + Hewitt-Savage $0$-$1$ 律）：UI 倒向鞅 $\{M_{-n}\}$ a.s. 且 $L^1$ 收敛到 $M_{-\infty}=E[M_{-1}|\bigcap_n\mathcal{F}_{-n}]$。可交换事件概率 $\in\{0,1\}$。SLLN：$\bar X_n\xrightarrow{\text{a.s.}}E[X_1]$（仅需 $E|X_1|<\infty$，比三级数条件弱）。重要性：倒向鞅把 SLLN 的条件降到最弱（$L^1$ 即可），证明也最美。

**自测**：$X_1,X_2,\dots$ iid，$E[X_i]=\mu$。令 $\mathcal{F}_{-n}=\sigma(\bar X_n,\bar X_{n+1},\dots)$（对称尾 $\sigma$-代数）。证明 $M_{-n}=\bar X_n$ 是倒向鞅（$E[\bar X_n|\mathcal{F}_{-(n+1)}]=\bar X_{n+1}$），用 Hewitt-Savage 推出 $\bar X_n\to E[X_1|\bigcap\mathcal{F}_{-n}]$，而 $\bigcap\mathcal{F}_{-n}$ 是可交换 $\sigma$-代数故极限为常数 $\mu$。

---

## 第 15 章 · The Radon-Nikodym Theorem via Martingales / Likelihood Ratio

**核心**：**全书收官章，用鞅论反哺测度论**。本章用倒向鞅证明 **Radon-Nikodym 定理**：若 $\nu\ll\mu$（绝对连续），则存在 RN 导数 $f=d\nu/d\mu$ 使 $\nu(A)=\int_A f\,d\mu$。鞅证法的优雅在于：把测度分解到有限划分 $\{\mathcal{F}_n\}$ 上，条件期望序列 $M_n=E_\mu[f|\mathcal{F}_n]$（$f=d\nu/d\mu$）构成 UI 鞅，其 $L^1$ 极限就是 RN 导数。应用：**似然比** $L=dQ/dP$ 是统计假设检验的核心量；**Kakutani 定理**判定两个乘积测度是否相互奇异——独立同分布序列下，$Q$ 与 $P$ 要么等价（相互绝对连续）要么奇异（支撑在不相交集上），判据是 Hellinger 积分 $\prod E_P[\sqrt{dQ_n/dP_n}]$ 的收敛性。本章把「测度论硬骨头 RN 定理」化为鞅论的推论，完美闭环全书。

**飞腾锚点**：🟡 matmul 15× [V03] —— 似然比 $L=dQ/dP$ 在离散样本下是 $L(\omega)=Q(\omega)/P(\omega)$ 的逐点比值，批量计算时矩阵化为一组比值的向量运算。Kakutani 定理的 Hellinger 积分 $\prod_n E_P[\sqrt{dQ_n/dP_n}]$ 是无穷连乘积，可对数化为 $\sum_n\log E_P[\sqrt{Z_n}]$ 后矩阵化求和。matmul 15× 加速服务于「多假设似然比」的批量检验，正如统计推断中并行计算各候选分布的似然——分类问题中 softmax 概率的对比本质就是似然比的矩阵化。

**关键定理**（RN 定理 + Kakutani）：$\nu\ll\mu$ $\Rightarrow$ $\exists\,f=d\nu/d\mu\in L^1(\mu)$。Kakutani：$P=\otimes P_n$，$Q=\otimes Q_n$（乘积测度），令 $Z_n=dQ_n/dP_n$，则 $Q\sim P$（等价）$\iff$ $\prod_n E_P[\sqrt{Z_n}]>0$；否则 $Q\perp P$（奇异）。重要性：Kakutani 给出「无穷维分布可区分」的精确判据，是渐近统计、信息几何的基础。

**自测**：$P=N(0,1)$，$Q=N(1,1)$。算单点似然比 $L(x)=dQ/dP=\frac{\phi(x-1)}{\phi(x)}=e^{x-1/2}$（$\phi$ 为标准正态密度）。若 $X_1,\dots,X_n$ iid，联合似然比 $L_n=\prod L(X_i)=e^{\sum X_i-n/2}$。在 $Q$ 下 $\sum X_i\sim N(n,n)$，$\sum X_i\to\infty$，故 $L_n\to\infty$。用 Kakutani：$E_P[\sqrt{Z}]=E_P[e^{(X-1/2)/2}]=e^{-1/8}<1$，$\prod=e^{-n/8}\to0$，故 $P\perp Q$（两分布支撑渐近分离）。

---

## 第 E 章 · Exercises（综述题）

**核心**：Williams 的习题极具特色——不仅有计算题，更有「证明或反驳」的辨析题与联系多章的综合题。许多习题是正文的延伸（如鞅的 Azuma-Hoeffding 界雏形、倒向鞅的遍历定理应用、似然比的 Neyman-Pearson 引理）。**建议**：Ch 11-15 的习题务必手做，这是检验鞅论是否真正内化的试金石。Williams 在习题中埋了不少「陷阱」（看似显然实则需 UI 条件、看似需独立实则仅需不相关），逐题辨析能极大加深对「条件」「充要」的敏感度。

---

## §9 全书思想主线

Williams 用一条主线贯穿 16 章：**「测度地基 → 条件期望 → 鞅」三步走，把概率论的一切收敛现象统一在鞅论框架下**。前半部（Ch 0-8）铺设测度积分基础——$\sigma$-代数、Lebesgue 积分、$L^p$ 空间、收敛模式、Fubini——这些是「语言」，Williams 推进紧凑但不省略技术。中段（Ch 9-10）用 Borel-Cantelli 与大数定律展示「经典」收敛定理的力量。真正的飞跃在 Ch 11：条件期望经 Radon-Nikodym 获得存在性，经塔性质获得「信息嵌套」结构，经 $L^2$ 投影获得几何直觉——这一章是全书「承上启下」的枢纽。一旦条件期望就位，Ch 12-15 的鞅论如水到渠成：可选停时定理统一赌博策略、UI 鞅收敛定理统一 a.s. 与 $L^1$ 收敛、倒向鞅重证 SLLN 与 Hewitt-Savage $0$-$1$ 律、最后用鞅论反哺测度论证明 RN 定理本身——形成完美闭环。

与 Shiryaev（GTM95）以测度公理为骨架、Durrett 以例子驱动、Billingsley 以测度详尽见长、Karatzas-Shreve 专攻连续时间随机分析不同，Williams 的统一性来自「条件期望是概率论的中心操作，鞅是其自然产物」这一洞见。读完 Williams，你会发现 Borel-Cantelli、大数定律、似然比不再是孤立定理，而是鞅这棵大树的枝叶。与已读的 Feller 卷一（组合直觉派）形成完美互补：Feller 给离散手感与 Arcsine 律的震撼，Williams 给现代框架与「以鞅统一一切」的优雅；与已读的 Shiryaev/Billingsley/Durrett/Karatzas-Shreve 形成「经典测度→鞅→连续鞅」的完整阶梯。

---

## §10 与本仓库其他笔记的交叉引用

**与仓库已读经典的对话**：
- **↔ Feller《概率论》卷一**：Feller 用组合计数建立概率直觉（Arcsine 律、随机游走、分支过程），Williams 用鞅论重写这些结果——Feller 第 X 章的 SLLN 在 Williams Ch 14 由倒向鞅优雅重证；Feller 第 XIV 章赌徒破产在 Williams Ch 12 由可选停时定理一统。Feller 给手感，Williams 给框架，二者是「离散直觉」与「现代严格」的两极互补。
- **↔ Shiryaev《概率》GTM95**：Shiryaev 以 Kolmogorov 公理为骨架，体系最完备但鞅论出现较晚（散落于后半部）；Williams 把鞅前置为中心。读 Shiryaev 的 Ch II-IV（测度积分）可补 Williams 前半部的技术细节，读 Williams Ch 11-15 可补 Shiryaev 鞅论的「直觉驱动力」与「以鞅统一」的视角。
- **↔ Durrett《概率：理论与例子》**：Durrett 同样以鞅为重要主线，但用更多现代例子（Markov 链、Brown 运动预演、Ergodic 定理）驱动。Williams 更紧凑哲学，Durrett 更面向研究前沿。两者可互为参照——Williams 学框架，Durrett 学应用。
- **↔ Billingsley《概率与测度》**：Billingsley 的测度论与收敛定理（弱收敛、Prohorov 定理、特征函数）比 Williams 更详尽，但鞅论较薄。Billingsley 补 Williams 的「测度深度与弱收敛理论」，Williams 补 Billingsley 的「鞅高度」。
- **↔ Karatzas & Shreve《Brown 运动与随机微积分》GTM113**：K&S 专攻连续时间鞅与 Itô 积分，是 Williams 离散鞅论的连续化升级。读 Williams Ch 12-13 后再读 K&S，能看清「离散鞅 → 连续鞅 → 半鞅 → Itô 公式」的抽象阶梯。

**AI / 工程锚点**：
- 🟢 **Ch 11 条件期望 → 深度学习中的最小均方估计与 Kalman 滤波**：条件期望 $E[X|\mathcal{G}]$ 在 $L^2$ 是正交投影，正是线性 MMSE 与 Kalman 滤波的数学核心。PyTorch 中 `nn.Linear` 的最小二乘拟合、自编码器的瓶颈层本质都是向数据子空间的投影——条件期望是它们的严格母体。
- 🟢 **Ch 12-13 鞅与可选停时 → 强化学习中的时序差分学习 TD($\lambda$)**：TD 误差 $\delta_t=R_t+\gamma V(S_{t+1})-V(S_t)$ 在期望意义下构成鞅差序列，可选停时定理保证 TD 学习的收敛性；$\lambda$-回报的资格迹（eligibility trace）分析直接用到鞅收敛。这是 Sutton-Barto 强化学习（仓库已读）第 12 章的理论基石。
- 🟢 **Ch 12 鞅 → SGD 收敛证明**：随机梯度下降 $w_{t+1}=w_t-\eta_t g_t$ 在凸情形下，$\{f(w_t)-f^*\}$ 是上鞅（或其变形），鞅收敛定理给出 SGD a.s. 收敛到最优的条件（步长满足 Robbins-Monro 条件 $\sum\eta_t=\infty,\sum\eta_t^2<\infty$）。非凸情形下，梯度噪声的鞅差结构支撑「逃离鞍点」的分析。
- 🟢 **Ch 15 似然比 → 金融数学 Black-Scholes 与统计假设检验**：测度变换 $dQ/dP$（等价鞅测度，equivalent martingale measure）是 Black-Scholes 定价的核心——把贴现资产价格变成鞅；似然比检验（Neyman-Pearson 引理）直接用 Kakutani 框架判定分布奇异性，是分类器阈值设计的理论依据。
- 🟡 **Ch 5 控制收敛定理 → 深度学习中的梯度噪声分析**：mini-batch 梯度 $\hat g_n\to\nabla f$（依概率，随 batch 增大），DCT 保证 $E[\hat g_n]\to E[\nabla f]$（期望可交换），支撑「批量平均消除梯度方差」的理论依据。BatchNorm 的「批统计量收敛到总体统计量」也依赖此。
