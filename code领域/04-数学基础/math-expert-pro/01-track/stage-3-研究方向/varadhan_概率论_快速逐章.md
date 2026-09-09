# S. R. Srinivasa Varadhan《概率论》 · 快速逐章精读

> **原书名**：Probability Theory　**著者**：S. R. Srinivasa Varadhan　**出版社**：Courant Lecture Notes in Mathematics, 7 / American Mathematical Society　**年份**：2001（Courant Institute 讲义）
> **读于**：2026-07-03
> **定位**：**Courant 学派的现代概率讲义**，由大偏差理论奠基者本人执笔，以一条紧凑的分析主线从 Kolmogorov 公理直通 Brown 运动、Itô 公式与「大偏差」——全书第 10 章是作者毕生研究的浓缩。
> **特色**：讲义体、密度高、分析味浓（Courant 的 PDE/泛函底色），不堆砌细节而追求「主线一气呵成」；**末章大偏差**是本书区别于所有同类教材的招牌，把 Cramér 定理与 Varadhan 变分公式作为收束。
> **声明**：本文为「快速逐章精读」，每章给核心逻辑串联 + 飞腾锚点 + 关键定理 + 自测题，非逐页翻译。

---

## §0 引言：Varadhan 的「通向大偏差」路线（约 350 字）

现代概率经典的组织各有取舍：Shiryaev（GTM95）以 Kolmogorov 公理为骨架、体系最完备但厚重；Breiman 走测度论直通车、密度极高；Loève（GTM45）是百科式权威、最难通读；Williams 以鞅为中心、却把弱收敛与过程论压到最薄。Varadhan 这本 Courant 讲义走的是**第五条路——一条由分析学家设计、终点明确指向「大偏差」的单线工程**。全书不到 140 页正文，却从概率空间 $(\Omega,\mathcal{F},P)$ 一路推进到 Prohorov 胎紧、Skorokhod 嵌入、Itô 公式，最后以 **Cramér 大偏差定理与 Varadhan 变分公式**收束——后者正是作者本人（2007 年 Abel 奖、2008 年 Steele 奖）的看家本领。

Varadhan 的个人印记有两处。其一是 **Courant 学派的分析底色**：他天然地把概率测度看作「分布」、把弱收敛看作「泛函分析」、把 Brown 运动看作「热方程的核」，因此第 5 章 Prohorov 定理与 Skorokhod 嵌入的处理带有泛函/度量空间的清晰几何，第 8-9 章的 Itô 微积分则始终隐含与 PDE（Feynman-Kac、热传导）的对话——这是 Courant 学派「概率与 PDE 是同一枚硬币两面」的传统。其二是 **第 10 章大偏差**——这是其余概率教材要么略去、要么只给 CLT 特例的硬骨头。Varadhan 给出 rate function、Cramér 定理、Varadhan 引理、Laplace 原理的完整链条，把「稀有事件概率的指数衰减」严格化。CLT 只告诉你「$\bar X_n$ 在 $\mu$ 的 $1/\sqrt n$ 邻域内」，大偏差告诉你「$\bar X_n$ 跑到 $x\neq\mu$ 的概率精确地是 $e^{-nI(x)}$」——这是「典型事件」之外「稀有事件」的完整概率图景。

代价是节奏快、例题少、几乎无图示——它假设读者已有测度论/泛函的底子，不适合纯零基础通读。对做 ML 的人，这一章是 **PAC-Bayes 界、稀有事件模拟（rare-event simulation）、强化学习策略梯度的熵正则**的理论母体。建议配 Williams（鞅的直觉化叙述）、Durrett（现代例子）做「左手直觉、右手严格」的对照阅读，再以 Breiman（遍历/无穷可分补强）做第三角。

**读书策略**：前 4 章可与已读 Williams/Shiryaev 笔记做「测度复习」；中段 Ch 5（Prohorov + Skorokhod）与末章 Ch 10（Cramér + Varadhan）是本书招牌，值得逐节手推；建议每章用 Python 验证——Ch 4 跑 $\sqrt n(\bar X_n-\mu)$ 看 CLT、Ch 10 跑 $P(\bar X_n\ge a)$ 取对数验证斜率 $=-I(a)$。

| 书 | 风格 | 严格性 | 适合谁 |
|---|---|---|---|
| **Varadhan《概率论》** | Courant 讲义体、分析味浓、主线直达大偏差 | 极高（Polish 空间 + Prohorov + Itô + 大偏差完整链） | 想以最短路径读懂「大偏差」、有分析底子的研究者 |
| **Breiman《概率论》** | 测度论直通、高密度、过程/鞅/遍历并重 | 极高（Prohorov/Lévy-Khintchine） | 想一本读完即达研究级概率装备者 |
| **Loève《概率论》GTM45** | 测度论百科、极全极厚、独立性为唯一代数支柱 | 极高（概率论百科全书） | 需权威查阅、做概率深度研究者 |
| **Shiryaev《概率》GTM95** | 测度公理化、定理-证明体系、叙事线性全面 | 极高（Kolmogorov 公理完备 + 数理统计） | 追求体系完整、做概率/统计研究者 |

---

## §1 全书 10 章骨架一览（飞腾锚点分布）

| 章 | 标题 | 核心概念 | 飞腾锚点 |
|:--:|------|----------|----------|
| 1 | Introduction | 概率为何需要测度、全书路线图、大偏差预告 | 分支预测 0.71/3.14 |
| 2 | Probability Spaces and Random Variables | $(\Omega,\mathcal{F},P)$、可测函数、Lebesgue 期望、收敛定理 | TLB 4.81× |
| 3 | Independence and Dependence | 独立性、Borel-Cantelli、0-1 律、三级数定理 | FP16 3.81× |
| 4 | Limit Theorems | WLLN/SLLN、特征函数、Lindeberg CLT | UDOT 16.9× |
| 5 | Convergence of Probability Measures | 弱收敛、Prohorov 定理、Skorokhod 嵌入、Donsker | matmul 15× |
| 6 | Conditional Expectation and Martingales | 条件期望（R-N 投影）、Doob 分解、可选停时、收敛 | Schmidt 正交化 |
| 7 | Markov Chains and Stopping Times | Markov 性、转移核、停时、强 Markov 性 | GEMM 9.45G |
| 8 | Stochastic Processes and Brownian Motion | Kolmogorov 相容性、Brown 运动、路径连续性 | Iron Law <2% |
| 9 | Stochastic Calculus and Itô Formula | Itô 积分、二次变差、Itô 公式、SDE | UDOT 16.9× |
| 10 | Large Deviations | rate function、Cramér 定理、Varadhan 引理、Laplace 原理 | TLB 4.81× |

> **飞腾锚点复用说明**：10 章 > 8 个锚点，故合理复用（同一锚点隔数章再出现、标注不同角度），保证相邻章绝不重复。UDOT 在 Ch 4（独立和累加=LLN）/ Ch 9（Itô 积分=二次变差加和）双用，前者是「$\frac1n\sum X_i$」、后者是「$\sum \Delta W^2\to t$」；TLB 在 Ch 2（σ-代数层级生成/扩张）/ Ch 10（大偏差=稀有事件的指数局部化）双用，前者是「分层度量构造」、后者是「指数尾部集中在最概然点」。

**七大关键定理速览**（本书主干的承重墙，每章详述其一）：

| 定理 | 所在章 | 一句话作用 |
|------|:------:|-----------|
| Kolmogorov 三级数定理 | Ch 3 | 独立和 a.s. 收敛的充要条件（LLN 之上的一般判据）|
| Prohorov 定理 | Ch 5 | 弱收敛的相对紧 ⟺ 胎紧，过程极限的存在性工具 |
| Skorokhod 嵌入定理 | Ch 5 | 用 a.s. 收敛表示弱收敛，CLT→Brown 桥的桥梁 |
| Doob 可选停时定理 | Ch 6 | 鞅在停时仍保持期望守恒，决策/最优停止的基石 |
| Itô 公式 | Ch 9 | 随机微积分的链式法则，多出「$(1/2)f''dt$」修正项 |
| Cramér 大偏差定理 | Ch 10 | 样本均值指数衰减 $P(\bar X\approx x)\asymp e^{-nI(x)}$ |
| Varadhan 变分公式（Laplace 原理）| Ch 10 | 指数积分的渐近 $=\sup\{f-I\}$，大偏差的「重心」 |

> 这七大定理构成 Varadhan 全书「测度→独立→极限→弱收敛→鞅→过程→Itô→大偏差」的主干，前四个是「存在性与收敛性」，末两个是作者本人的招牌——**CLT 描述「典型」事件趋于正态，大偏差描述「稀有」事件的指数衰减，二者是同一硬币的两面**。

---

### 第 1 章 · Introduction（引言）

**核心**：这是全书唯一的「非技术」章节，却定下 Courant 学派的基调。Varadhan 先指出概率论要同时处理「离散计数」与「连续密度」，又要容纳极限与无穷维过程，唯一自洽的地基是 **Kolmogorov 测度论公理**。他预告全书路线：概率空间 → 独立性 → 极限定理 → 弱收敛 → 鞅 → Markov/停时 → Brown 运动 → Itô 微积分 → 大偏差，并强调第 10 章大偏差是「稀有事件概率的精确渐近」，是一切 CLT 之外的概率现象的归宿。Varadhan 的立场鲜明：概率不是「模糊的频率直觉」，而是带独立性结构的、可严格分析的测度论。

**飞腾锚点**：🟡 分支预测 0.71 vs 3.14 [Lab02] —— 概率本质是「面对多个未来分支的不确定性」。CPU 分支预测器对「下一条指令走哪条路」连续下注（命中 0.71 周期、未命中 3.14 周期），正是「不确定未来」的微缩模型。本章预告的 Kolmogorov 公理 $P:\mathcal{F}\to[0,1]$，就是给每个「分支结局」赋可信度的严格框架——而第 10 章大偏差要刻画的，正是「预测器连续未命中」这类稀有尾部事件按 $\exp(-nI)$ 指数衰减的规律。

**关键定理**：本章无定理，给出全书路线图与「大偏差」这一终点的预告。

**自测**：用一句话写下你对「大数定律」的直觉（如「样本均值趋于期望」），读到第 4 章 SLLN 时回来对照其严格形式 $\bar X_n \to \mu$ a.s.，再到第 10 章看「均值偏离期望 $x\neq\mu$」的概率如何被 $e^{-nI(x)}$ 精确刻画——体会「典型事件」与「稀有事件」的二元结构。

**概率的两种面貌**：Varadhan 在本章暗示概率论的二元结构——「典型事件」（CLT 描述，$O(1/\sqrt n)$ 波动）与「稀有事件」（大偏差描述，指数衰减）。前者是统计渐近的日常，后者是稀有事件模拟、风险分析、统计力学的核心。理解这一二元结构，是读懂本书第 10 章为何「值得用整本书铺垫」的关键——CLT 与大偏差不是两套独立理论，而是同一概率结构在「中心」与「尾部」的两个渐近面。

---

### 第 2 章 · Probability Spaces and Random Variables（概率空间与随机变量）

**核心**：概率的严格语言在此落地。概率空间 $(\Omega,\mathcal{F},P)$ 由样本空间 $\Omega$、事件 $\sigma$-代数 $\mathcal{F}$（对可数并/交/补封闭）与概率测度 $P:\mathcal{F}\to[0,1]$（$P(\Omega)=1$、可数可加）构成。核心技术是 **Carathéodory 扩张定理**：在 field（域）上定义的可数可加集合函数可唯一扩张到 $\sigma(\text{field})$——这是构造 Lebesgue 测度、乘积测度的标准机器。**随机变量**是可测函数 $X:\Omega\to\mathbb{R}$（$\{X\le x\}\in\mathcal{F}$），其**分布**由 $F_X(x)=P(X\le x)$ 描述。**期望**定义为 Lebesgue 积分 $E[X]=\int_\Omega X\,dP$，由此自然引出**单调收敛**与**控制收敛定理（DCT）**——后两者是全书交换「极限与积分」的全部依据。

**飞腾锚点**：🟢 TLB 4.81× [E04] —— $\sigma$-代数是从「子集族」逐层生成（开区间 → Borel → 完备化），正如 CPU 的 TLB（转译旁路缓冲）把「虚拟地址」分层映射到物理页。Carathéodory 扩张「先在简单域上定义、再扩张到整个 $\sigma$-代数」的过程，与 TLB「先查页表项、再覆盖全部地址空间」同构；TLB 命中 4.81× 加速正是「分层构造」换取的效率。完备化把零测集子集补入 $\mathcal{F}$，对应「补全所有可寻址页」。

**关键定理**（控制收敛定理 DCT）：若 $|X_n|\le Y$，$EY<\infty$，且 $X_n\to X$ a.s.，则
$$\lim_{n\to\infty}E[X_n]=E[\lim_{n\to\infty}X_n]=E[X].$$
重要性：DCT 是全书交换「$\lim$ 与 $E$」的标准工具，CLT、鞅收敛、大偏差的证明处处依赖它；没有「控制函数 $Y$」则结论可谬（反例：$X_n=n\mathbf{1}_{(0,1/n)}$）。

**自测**：$\Omega=[0,1]$ 配 Lebesgue 测度，$X_n(\omega)=n\mathbf{1}_{(0,1/n)}(\omega)$。验证 $X_n\to0$ 处处成立、但 $E[X_n]=1\not\to0=E[0]$——说明缺「控制函数」时「极限与期望不可交换」。再取 $Y\equiv1$ 作控制，证 $X_n\mathbf{1}_{(0,1/n)}$ 不被 $Y$ 控制（实际被 $n$ 不被 1 控制），故 DCT 不适用。

**收敛定理三件套速查**：单调收敛（MCT，$0\le X_n\uparrow X\Rightarrow E[X_n]\uparrow E[X]$）、Fatou 引理（$E[\liminf X_n]\le\liminf E[X_n]$，可负）、控制收敛（DCT，需控制函数）。三者层层递进，是全书交换「$\lim$ 与 $E$」的全部依据——CLT、鞅收敛、大偏差证明处处依赖。

---

### 第 3 章 · Independence and Dependence（独立与依赖）

**核心**：独立性是概率区别于一般测度论的**唯一代数特征**。事件族 $\{A_i\}$ 独立指 $P(\cap A_{i_j})=\prod P(A_{i_j})$；$\sigma$-代数族独立则要求其上任意有限选择独立；随机变量独立等价于联合分布等于边缘乘积。**Borel-Cantelli 引理**两半是尾事件的钥匙：$\sum P(A_n)<\infty\Rightarrow P(A_n\text{ i.o.})=0$（无独立性），而 $\sum P(A_n)=\infty$ + 独立 $\Rightarrow P(A_n\text{ i.o.})=1$（需独立性）。由此引出 **Kolmogorov 0-1 律**：尾 $\sigma$-代数上的事件概率只能是 0 或 1。本章高潮是 **Kolmogorov 三级数定理**——独立和 a.s. 收敛的充要判据，是大数律之上的「通用收敛手册」。

**飞腾锚点**：🟡 FP16 3.81× [L01] —— 独立性意味着联合分布按乘积分解 $P_{X,Y}=P_X\otimes P_Y$，而乘积在有限精度下逐因子累乘会累积误差。FP16 的 3.81× 精度劣势（相对 FP32）正体现在「长乘积链的尾数漂移」上——独立变量的期望虽可分 $E[\prod X_i]=\prod E[X_i]$，但模拟「独立样本的乘积统计量」时 FP16 的 11-bit 尾数会把 $\prod$ 的精度吃掉。三级数定理中「方差级数 $\sum\mathrm{Var}(X_n^A)$ 收敛」的条件，本质是「累加噪声的总能量有界」，与浮点累加的误差有界同构。

**关键定理**（Kolmogorov 三级数定理）：$\{X_n\}$ 独立。$\sum X_n$ a.s. 收敛 $\iff$ 存在 $A>0$ 使下列三级数同时收敛：
$$\textstyle\sum_n P(|X_n|>A)<\infty,\quad \sum_n E[X_n^A]\ \text{收敛},\quad \sum_n \mathrm{Var}(X_n^A)<\infty,$$
其中 $X_n^A=X_n\mathbf{1}_{\{|X_n|\le A\}}$。重要性：它是判断「无穷多个随机扰动之和是否稳定」的总判据——SLLN、鞅收敛、随机级数理论都退化为它的推论。

**自测**：$X_n$ 独立、$X_n=\pm n$ 各以概率 $\frac{1}{2n^2}$、否则为 $0$（概率 $1-\frac1{n^2}$）。用三级数定理判断 $\sum X_n$ 是否 a.s. 收敛：取 $A=1$，则 (1) $\sum P(|X_n|>1)=\sum\frac1{n^2}<\infty$ ✓；(2) $E[X_n^A]=0$（对称）✓；(3) $\mathrm{Var}(X_n^A)=0$（截断后恒 0）✓——故 a.s. 收敛。

**三级数定理的地位**：它是 LLN 的「上位定理」。SLLN（ iid、$E|X_1|<\infty\Rightarrow\bar X_n\to\mu$ a.s.）只是三级数定理在「$X_n=\frac1n(Y_n-\mu)$」这一特殊截断下的推论——把「均值收敛」化为「加权和 a.s. 收敛」。Varadhan 在本章把三级数作为独立性的「总结算」，比直接证 SLLN 更具一般性，也为第 10 章大偏差的「独立和指数渐近」铺好测度地基。

---

### 第 4 章 · Limit Theorems（极限定理：LLN、CLT）

**核心**：本章是「独立同结构」下的渐近定律。**弱大数律（WLLN）**：$\bar X_n\xrightarrow{P}\mu$；**强大数律（SLLN，Kolmogorov）**：$\bar X_n\to\mu$ a.s.（仅需 $E|X_1|<\infty$）。证明 SLLN 用 Kolmogorov 不等式（纯测度论的尾和工具）。**中心极限定理（CLT）**的核心工具是**特征函数** $\phi_X(t)=E[e^{itX}]$——它是分布的 Fourier 变换，满足「$\phi_n\to\phi$ 逐点 ⟺ $P_n\Rightarrow P$」。**Lindeberg-Lévy CLT**：iid、方差 $\sigma^2$，则 $\sqrt{n}(\bar X_n-\mu)/\sigma\Rightarrow N(0,1)$。更精细的 **Lindeberg-Feller CLT** 给出「非同分布」情形的充要条件——「无单点主导」。

**飞腾锚点**：🟢 UDOT 16.9× [E05] —— 样本均值 $\bar X_n=\frac1n\sum X_i$ 与样本方差 $S_n^2=\frac1n\sum(X_i-\bar X)^2$ 的核心运算是「点积累加」。UDOT（无符号点积累加）16.9× 加速正是为「$\sum$」这一概率统计第一算子而设：LLN 说累加结果趋于期望、CLT 说累加噪声按 $\sqrt{n}$ 放大后成正态。Monte Carlo 模拟 $N=10^6$ 次取均值的精度 $\sim 1/\sqrt{N}$，背后是 CLT；而 UDOT 把这 $10^6$ 次累加压成毫秒级。

**关键定理**（Lindeberg CLT）：$\{X_{n,k}\}$ 行间独立、三角阵列，记 $s_n^2=\sum_k\mathrm{Var}(X_{n,k})$。若对任意 $\varepsilon>0$ 满足 **Lindeberg 条件**
$$\frac{1}{s_n^2}\sum_k E\!\left[X_{n,k}^2\mathbf{1}_{\{|X_{n,k}|>\varepsilon s_n\}}\right]\to0,$$
则 $\frac{1}{s_n}\sum_k(X_{n,k}-EX_{n,k})\Rightarrow N(0,1)$。重要性：它是 CLT 的「最一般」形式，iid 情形是其特例；Lindeberg 条件「无单点主导」直接对应 mini-batch SGD 中「批量内无离群点主导梯度」。

**自测**：$X_i\overset{iid}{\sim}\mathrm{Bernoulli}(0.3)$。用 Python 模拟 $n=10,100,1000,10000$ 的 $\bar X_n$，画直方图观察「分布收紧到 0.3」（LLN）；再画 $\sqrt{n}(\bar X_n-0.3)$ 的直方图观察「趋于正态 $N(0,0.21)$」（CLT，方差 $\sigma^2=0.3\times0.7=0.21$）。

**特征函数法要点**：$\phi_X(t)=E[e^{itX}]$ 是分布的 Fourier 变换，满足唯一性（分布由 $\phi$ 完全决定）、反演（$F$ 可由 $\phi$ 积分恢复）、连续性定理（$\phi_n\to\phi$ 逐点 ⟺ $P_n\Rightarrow P$）。CLT 的标准证法就是「独立和的特征函数 = 边缘特征函数之积」，取对数展开 $\log\phi_{\bar X_n}(t)=-t^2/2+o(1)$ 即得 $N(0,1)$ 极限。Varadhan 在本章把这套 Fourier 分析的工具磨利，为第 5 章弱收敛铺路。

---

### 第 5 章 · Convergence of Probability Measures（概率测度收敛：Prohorov、Skorokhod）

**核心**：本章把「随机变量序列收敛」升级为「分布序列收敛」，是全书最具 Courant 分析味的一章。**弱收敛（依分布收敛）**$P_n\Rightarrow P$ 定义为 $\int f\,dP_n\to\int f\,dP$（对所有有界连续 $f$）。核心工具是 **Prohorov 定理**：在 Polish（完备可分度量）空间上，分布族相对紧 $\iff$ 胎紧（tight，质量不逃逸到无穷）。这给出弱收敛极限的存在性判据。**Skorokhod 表示定理**更进一步：$P_n\Rightarrow P$ 可用「同一空间上的 a.s. 收敛」表示——存在 $X_n\sim P_n$、$X\sim P$ 使 $X_n\to X$ a.s.，把「弱」（分布层）的收敛转化为「强」（几乎必然层）。**Donsker 不变原理**作为应用：部分和过程 $\Rightarrow$ Brown 运动，是泛函 CLT。

**飞腾锚点**：🟢 matmul 15× [V03] —— 弱收敛 $\int f\,dP_n\to\int f\,dP$ 是「线性泛函序列的逐点收敛」，本质是把测度看作 Hilbert 空间上的线性算子。Prohorov 胎紧「质量紧致、不逃逸」与矩阵列的「谱有界」同构——matmul 15× 加速的迭代算法（如 PageRank）正是「转移矩阵幂序列 $M^n$」在弱收敛到稳态分布 $\pi$，胎紧保证 $\{M^n\delta_x\}$ 不发散。Donsker 原理把离散随机游走「连续化」为 Brown 运动，恰是 matmul 把「逐步转移」压成「批量矩阵幂」的连续极限。

**关键定理**（Prohorov 定理）：设 $S$ 为 Polish 空间，$\{P_\alpha\}$ 是 $\mathcal{P}(S)$ 中的分布族。则 $\{P_\alpha\}$ 相对紧（任一序列有弱收敛子列）$\iff$ $\{P_\alpha\}$ 胎紧（$\forall\varepsilon>0$，存在紧 $K_\varepsilon$ 使 $P_\alpha(K_\varepsilon)>1-\varepsilon$ 对所有 $\alpha$）。重要性：它是「证明极限分布存在」的标准机器——先证胎紧、再证有限维相容，即得弱收敛。

**自测**：$P_n=\frac12\delta_{-1}+\frac12\delta_{+n}$（一半质量固定在 $-1$、一半逃到 $+n$）。验证 $\{P_n\}$ **不胎紧**（紧集 $K$ 必有界，$n\to\infty$ 时 $P_n(K)\to 1/2<1-\varepsilon$），故由 Prohorov 它无弱收敛子列。再改为 $P_n=\frac12\delta_{-1}+\frac12\delta_{+1}$，验证胎紧且 $P_n\Rightarrow P_1$。

**Prohorov → Skorokhod → Donsker 三连环**：本章的递进逻辑是——Prohorov 定理给出「弱收敛极限的存在性」（先证胎紧、再证有限维相容）；Skorokhod 嵌入把「弱收敛」转化为「a.s. 收敛」（让概率不等式可直接搬到分布层）；Donsker 不变原理作为应用，把「离散随机游走的部分和过程」弱收敛到 Brown 运动，是「泛函 CLT」。这三连环是 Varadhan 全书最具 Courant 分析味的部分，也是第 8 章 Brown 运动严格存在的理论前置。

---

### 第 6 章 · Conditional Expectation and Martingales（条件期望与鞅）

**核心**：**条件期望** $E[X\mid\mathcal{G}]$ 定义为 $X$ 在 $L^2(\mathcal{G})$ 中的正交投影（或等价地，Radon-Nikodym 导数 $\frac{d\nu}{dP}|_\mathcal{G}$，其中 $\nu(A)=E[X\mathbf{1}_A]$）。它是「给定部分信息 $\mathcal{G}$ 时对 $X$ 的最优估计」，满足 Jensen、塔性质 $E[E[X|\mathcal{G}]|\mathcal{H}]=E[X|\mathcal{H}]$（$\mathcal{H}\subseteq\mathcal{G}$）。**鞅**是「关于 filtration $\{\mathcal{F}_n\}$ 的公平游戏」：$E[X_{n+1}|\mathcal{F}_n]=X_n$；上鞅/下鞅对应「偏向不利/有利」。**Doob 分解**把任一适应过程拆为「鞅 + 可料」两部分。**可选停时定理**保证「在停时 $\tau$ 仍保持期望守恒」（需有界或一致可积）。**Doob 收敛定理**：$L^1$ 有界上鞅 a.s. 收敛。

**飞腾锚点**：🟢 Schmidt 正交化 —— 条件期望 $E[X|\mathcal{G}]$ 是 $X$ 在子空间 $L^2(\mathcal{G})$（「$\mathcal{G}$-可测函数」全体）上的**正交投影**，残差 $X-E[X|\mathcal{G}]$ 与 $L^2(\mathcal{G})$ 正交。这与 Schmidt 正交化「投影到已生成子空间、残差正交」完全同构：filtration $\mathcal{F}_n$ 是逐步「增广的子空间」，鞅差 $X_n-E[X_n|\mathcal{F}_{n-1}]$ 就是每步的正交残差——鞅是「不断把新信息正交分解」的过程。Doob $L^2$ 不等式 $E[\max_{k\le n}M_k^2]\le4E[M_n^2]$ 正是用正交几何控制「路径峰值」。

**关键定理**（Doob 可选停时定理）：$\{M_n\}$ 是鞅（或一致可积下鞅），$\tau$ 是有界停时（$\tau\le N$）。则 $E[M_\tau]=E[M_0]$。重要性：它是「最优停止」「决策时序」「似然比检验」的理论基石——保证「在合适的随机时刻停下，期望不变」。

**自测**：对称随机游走 $S_n=\sum_{i=1}^n\xi_i$，$\xi_i=\pm1$ 等概，是关于自然 filtration 的鞅。停时 $\tau=\min\{n:S_n=+5\}$。问：$E[S_\tau]\stackrel{?}{=}E[S_0]=0$？（提示：$\tau$ 几乎必然有限但 $E[\tau]=\infty$，故可选停时不适用——这是「无界停时」的经典陷阱。）

**鞅收敛与不等式速查**：Doob $L^p$ 不等式 $E[(\max_{k\le n}|M_k|)^p]\le(\frac{p}{p-1})^pE[|M_n|^p]$（$p>1$）控制「路径峰值」；Doob 收敛定理 $L^1$ 有界上鞅 a.s. 收敛；一致可积鞅在 $L^1$ 收敛。三者构成「鞅论三大工具」，与第 4 章特征函数法、第 10 章大偏差并列为全书的渐近分析支柱。Varadhan 把鞅作为「连接第 5 章弱收敛与第 7 章停时」的枢纽——可选停时是决策论、最优停止、序贯检验的理论母体。

---

### 第 7 章 · Markov Chains and Stopping Times（Markov 链与停时）

**核心**：**Markov 性**是「给定现在，过去与未来无关」：$P(X_{n+1}\in A|\mathcal{F}_n)=P(X_{n+1}\in A|X_n)$。离散状态空间的 Markov 链由**转移矩阵** $P=(p_{ij})$ 刻画，$n$ 步转移 $P^{(n)}=P^n$ 满足 Chapman-Kolmogorov 方程 $P^{(m+n)}=P^{(m)}P^{(n)}$。**停时** $\tau$（$\{\tau\le n\}\in\mathcal{F}_n$）允许「只看过去即可判定是否停」；**强 Markov 性**把 Markov 性推广到停时：$P(X_{\tau+1}\in A|\mathcal{F}_\tau)=P(X_{\tau+1}\in A|X_\tau)$。本章讨论**常返/非常返**（是否必然返回）、**遍历性**与**不变分布** $\pi P=\pi$，以及 Markov 链的遍历定理——「时间平均趋于空间平均」。

**飞腾锚点**：🟢 GEMM 9.45 GFLOPS [Lab05] —— 转移矩阵的 $n$ 步幂 $P^n$ 是高吞吐矩阵乘法（GEMM）的天然任务。Chapman-Kolmogorov 方程 $P^{(m+n)}=P^{(m)}P^{(n)}$ 就是矩阵乘法结合律；快速幂把 $P^{2^k}$ 算到 $O(\log n)$ 次乘法，是 PageRank、MCMC 稳态分布迭代的加速核心。强 Markov 性保证「首达时 $\tau$ 后从 $X_\tau$ 重新开始」，使「分段模拟」合法——这与 GEMM 把「逐步转移」批量压成「矩阵幂」同构。

**关键定理**（Markov 链遍历定理）：不可约、非周期、正常返的 Markov 链有唯一不变分布 $\pi$，且对任意初始分布、任意有界 $f$，
$$\frac1n\sum_{k=0}^{n-1}f(X_k)\xrightarrow{a.s.}\int f\,d\pi.$$
重要性：它是 MCMC（Metropolis-Hastings、Gibbs、HMC）采样有效的理论基石——「按转移核迭代足够久，样本经验分布趋于目标分布 $\pi$」。

**自测**：状态 $\{0,1\}$，$P=\begin{pmatrix}0.5&0.5\\0.3&0.7\end{pmatrix}$。求平稳分布（解 $\pi P=\pi$ 得 $\pi=(0.375,0.625)$）。停时 $\tau=\min\{n:X_n=1\}$，用强 Markov 性求「从 0 出发首达 1 的期望时间」（解 $h(0)=1+0.5h(0)+0.5\cdot0$ 得 $h(0)=2$）。

**Markov 链分类与收敛速率**：状态按常返性分「正常返（期望返回有限）/ 零常返（返回但期望无穷）/ 非常返（不返回）」；按周期分「周期 / 非周期」。不可约 + 非周期 + 正常返 ⟹ 遍历 ⟹ 收敛到唯一 $\pi$。收敛速率由「谱隙」$1-\lambda_2$（$\lambda_2$ 为转移矩阵次大特征值）决定——谱隙越大收敛越快，这是 MCMC 算法「混合时间」分析的核心。Varadhan 在本章把离散 Markov 链作为第 8 章连续时间过程（Brown 运动）的离散预演，停时与强 Markov 性是连接二者的桥梁。

---

### 第 8 章 · Stochastic Processes and Brownian Motion（随机过程与 Brown 运动）

**核心**：**随机过程**是指标集（通常时间 $T\subseteq\mathbb{R}_+$）上的随机变量族 $\{X_t\}$。其存在性由 **Kolmogorov 相容性（一致性）定理**保证：给定的有限维分布族只要满足相容性（边缘一致、对称），就存在一个过程以之为有限维分布。**Brown 运动** $\{W_t\}$ 是核心过程：$W_0=0$、独立增量、增量 $W_t-W_s\sim N(0,t-s)$、路径连续。**Kolmogorov 连续性准则**给出路径连续的充分条件（$E|X_t-X_s|^\alpha\le C|t-s|^{1+\beta}$）。Brown 运动的不变性质（反射原理、首达时分布、重对数律）是后续 Itô 微积分的舞台。

**飞腾锚点**：🟢 Iron Law <2% [Lab00] —— Brown 路径「处处连续但处处不可微」是概率论最反直觉的现象之一：性能铁律「性能 = 指令数 × CPI × 时钟」中，Brown 路径的「瞬时速度」$dW_t/dt$ 不存在（变差无穷），正如「把 CPI 当常数」的模型在抖动剧烈的路径上误差爆炸（>2%）。控制 Brown 路径模拟的误差，需要用「二次变差 $\sum\Delta W^2\to t$」这一严格量代替「导数」——这正是第 9 章 Itô 积分的动机。Iron Law 提醒：在「不可微」的现实里，必须用「积分变差」而非「微分」。

**关键定理**（Kolmogorov 连续性准则）：若存在 $\alpha,\beta,C>0$ 使 $E|X_t-X_s|^\alpha\le C|t-s|^{1+\beta}$ 对所有 $s,t$，则 $X$ 有连续修正，且满足 Hölder 连续（指数 $<\beta/\alpha$）。重要性：它是「从有限维分布证明路径连续」的标准工具——Brown 运动满足 $\alpha=4,\beta=1$（$E|W_t-W_s|^4=3(t-s)^2$），故路径连续。

**自测**：验证 Brown 增量正态性：用 Python 模拟 $W_{k}=W_{k-1}+\sqrt{\Delta t}\,Z_k$，$Z_k\sim N(0,1)$，$\Delta t=0.01$，跑 10000 条路径。画 $W_{0.5}$ 的直方图（应近 $N(0,0.5)$），验证反射原理 $P(\max_{s\le t}W_s\ge a)=2P(W_t\ge a)$。

**Brown 运动核心不变性质**：标度不变 $W_{ct}\overset{d}{=}\sqrt c\,W_t$、时间逆转 $\{W_{T-t}-W_T\}\overset{d}{=}\{-W_t\}$、首达时 $\tau_a=\inf\{t:W_t=a\}$ 与 $\tau_a\overset{d}{=}a^2/W_1^2$、重对数律 $\limsup_{t\to\infty}\frac{W_t}{\sqrt{2t\log\log t}}=1$ a.s.。这些不变性质是第 9 章 Itô 微积分的「素材库」——Itô 公式正是对这些路径性质的系统微分刻画。

---

### 第 9 章 · Stochastic Calculus and Itô Formula（随机积分与 Itô 公式）

**核心**：Brown 路径不可微，故「$\int f\,dW$」不能用 Riemann-Stieltjes 定义。**Itô 积分**定义为简单过程逼近的 $L^2$ 极限：$\int_0^t H_s\,dW_s=\lim\sum H_{t_i}(W_{t_{i+1}}-W_{t_i})$，关键是用**左端点**取值（非中点），由此产生非零的「二次变差」修正。核心事实是 **二次变差** $\langle W\rangle_t=t$（即 $\sum(\Delta W)^2\to t$）。本章高潮是 **Itô 公式**——随机微积分的链式法则，比经典链式法则多出一项 $\frac12 f''(W_t)\,dt$。**Itô 过程** $dX_t=\mu_t\,dt+\sigma_t\,dW_t$ 是带漂移与扩散的随机过程，**随机微分方程（SDE）** 定义其动力学，并与 PDE（Feynman-Kac、热方程）形成对偶。

**飞腾锚点**：🟢 UDOT 16.9× [E05] —— Itô 积分是「左端点加权的增量平方累加」$\sum H_{t_i}\Delta W_{t_i}$，二次变差 $\sum(\Delta W)^2\to t$ 是纯点积累加。UDOT 16.9× 加速直接服务于「高频路径的变差累加」——模拟 Itô 积分需把 $[0,T]$ 切成 $10^6$ 段逐段累加，UDOT 把这 $10^6$ 次乘加压成毫秒。但 Itô 与 Riemann 的区别正在「左端点」带来 $dt$ 修正项，模拟时若误用中点（Stratonovich）会得到不同结果——精度误差（FP16）会污染二次变差的 $L^2$ 收敛。

**关键定理**（Itô 公式）：$f\in C^2$，$\{W_t\}$ Brown 运动，则
$$df(W_t)=f'(W_t)\,dW_t+\tfrac12 f''(W_t)\,dt.$$
重要性：它是随机微积分的「链式法则」，多出的 $\frac12 f''dt$ 项来自二次变差 $\langle W\rangle_t=t$——这一项是 Black-Scholes 期权定价、Feynman-Kac 公式、扩散生成模型的数学根基。

**自测**：取 $f(x)=x^2$，用 Itô 公式得 $d(W_t^2)=2W_t\,dW_t+dt$，积分得 $W_t^2=2\int_0^t W_s\,dW_s+t$，故 $E[W_t^2]=t$（Itô 积分期望为 0）。再用 Python 模拟验证 $\sum_{i}(W_{t_{i+1}}-W_{t_i})^2\to t$（二次变差）。

**Itô 积分 vs Stratonovich 积分**：Itô 用「左端点」取值，产生 $dt$ 修正项，是「非预期」（adapted）积分，金融与 Markov 过程的标准选择；Stratonovich 用「中点」，满足经典链式法则（无修正项），是物理与随机微分几何的选择。二者关系由 $H\circ dW=H\,dW+\frac12\langle H,W\rangle$ 转化。本章末尾预告 **Feynman-Kac 公式**——把 SDE 的期望与抛物型 PDE 的解对偶起来，是「概率 ↔ PDE」的桥梁，也是 Courant 学派分析底色的集中体现。

---

### 第 10 章 · Large Deviations（大偏差：Cramér、Varadhan 引理）

**核心**：本章是全书的招牌，也是 Varadhan 毕生研究的浓缩。CLT 描述「典型」事件（$\bar X_n$ 在 $\mu$ 附近 $\pm O(1/\sqrt{n})$），而**大偏差理论**描述「稀有」事件（$\bar X_n$ 偏离 $\mu$ 到 $x\neq\mu$）的概率按 $e^{-nI(x)}$ 指数衰减。**rate function**（速率函数）$I:\mathbb{R}\to[0,\infty]$ 刻画偏离的「代价」，满足水平集 $\{I\le c\}$ 紧。**Cramér 定理**给出 iid 情形：$I(x)=\sup_\lambda\{\lambda x-\log M(\lambda)\}$（$M(\lambda)=E[e^{\lambda X}]$ 为矩母函数），即 $I$ 是 $\log M$ 的 Legendre-Fenchel 变换。**Varadhan 引理**把指数积分的渐近给出：$\frac1n\log E[e^{nf(Z_n)}]\to\sup_z\{f(z)-I(z)\}$——这是大偏差的「重心」。**Laplace 原理**是其等价对偶，**压缩原理**把大偏差从一空间传到另一空间。

**飞腾锚点**：🟡 TLB 4.81× [E04] —— 大偏差说「稀有事件概率集中在 $I$ 的最小值点（最概然点）」，正如 TLB 把「全地址空间的访问」集中在「少数热页」上——$P(\bar X_n\approx x)\asymp e^{-nI(x)}$ 在 $I$ 的谷底（$x=\mu$，$I=0$）集中了几乎全部质量，偏离谷底 $I>0$ 处质量指数衰减。这与 TLB「热页命中 4.81×、冷页极少访问」的局部化结构同构。压缩原理「大偏差经映射后 rate function 取下确界 $I'(y)=\inf_{x:g(x)=y}I(x)$」恰是「把多页映射到同一缓存行」的概率版本。

**关键定理**（Cramér 大偏差定理）：$X_i$ iid，存在 $\lambda_0>0$ 使 $M(\lambda)=E[e^{\lambda X_1}]<\infty$ 对 $|\lambda|<\lambda_0$。记 $I(x)=\sup_\lambda\{\lambda x-\log M(\lambda)\}$（凸的 rate function）。则样本均值 $\bar X_n$ 满足 LDP：对开集 $G$、闭集 $F$，
$$-\inf_{x\in G}I(x)\le\liminf_{n}\tfrac1n\log P(\bar X_n\in G),\quad \limsup_{n}\tfrac1n\log P(\bar X_n\in F)\le-\inf_{x\in F}I(x).$$
重要性：它精确给出「样本均值落入区间 $A$」的指数衰减率 $- \inf_{x\in A}I(x)$——CLT 只给 $O(1/\sqrt n)$ 局部，Cramér 给全局指数律。

**关键定理**（Varadhan 变分公式 / Laplace 原理）：$\{Z_n\}$ 满足速度 $I$ 的 LDP，$f$ 连续。则
$$\lim_{n\to\infty}\frac1n\log E\!\left[e^{nf(Z_n)}\right]=\sup_{z}\{f(z)-I(z)\}.$$
重要性：它是大偏差的「对偶重心」——指数积分的渐近由「$f$ 的收益减 $I$ 的代价」的最大值主导。这一公式是 PAC-Bayes 界、自由能渐近、强化学习最大熵正则的理论母体。

**自测**：$X_i\sim N(0,1)$。$M(\lambda)=e^{\lambda^2/2}$，$I(x)=\sup_\lambda\{\lambda x-\lambda^2/2\}=x^2/2$。验证 Cramér：$P(\bar X_n\ge a)\asymp e^{-n a^2/2}$（$a>0$）。再用 Varadhan 公式取 $f(z)=z$：$\frac1n\log E[e^{n\bar X_n}]=\sup_z\{z-z^2/2\}=1/2$（在 $z=1$ 取得），对照直接计算 $E[e^{n\bar X_n}]=e^{n/2}$，吻合。

**大偏差核心要素速查**：

| 概念 | 数学对象 | 直觉 |
|------|----------|------|
| rate function $I$ | 下半连续、水平集紧 | 偏离 $\mu$ 到 $x$ 的「指数代价」 |
| Cramér 定理 | $I=\log M$ 的 Legendre 变换 | iid 样本均值的精确指数衰减 |
| Varadhan 引理 | $\frac1n\log E[e^{nf}]=\sup(f-I)$ | 指数积分的「重心」 |
| 压缩原理 | $I'(y)=\inf_{g(x)=y}I(x)$ | 大偏差经映射传递 |
| CLT vs LDP | CLT 局部 $O(1/\sqrt n)$、LDP 全局 $e^{-nI}$ | 「典型」与「稀有」的二元 |

> Cramér 定理与 Varadhan 引理是「同一硬币两面」：Cramér 说「概率衰减率是 $I$」，Varadhan 说「指数积分增长率是 $\sup(f-I)$」——后者是前者的对偶。二者合称 **Laplace 原理**，是稀有事件模拟、PAC-Bayes、统计力学的统一框架。

---

## §9 全书思想主线（约 200 字）

Varadhan 用一条主线贯穿 10 章：**「测度 → 独立 → 极限定理 → 弱收敛 → 鞅 → 过程 → Itô → 大偏差」**——前 9 章是为第 10 章铺路。前半（Ch 1-4）是标准测度论概率：概率空间、独立性、Borel-Cantelli、三级数、LLN/CLT，Varadhan 推进紧凑但完整。中段（Ch 5-7）是 Courant 分析味最浓的部分：Prohorov 胎紧定理（弱收敛的存在性）、Skorokhod 嵌入（弱↔强转化）、Markov 链与停时——这一段把「分布层」与「路径层」打通。后段（Ch 8-9）建起 Brown 运动与 Itô 微积分，为连续时间大偏差（Freidlin-Wentzell）留接口。末章（Ch 10）大偏差是全书灵魂：Cramér 定理 + Varadhan 引理把「稀有事件」严格化，是 CLT 之外的「另一面概率」。

与 Breiman（测度直通车、遍历/无穷可分见长）、Loève（百科式、独立性为支柱）、Shiryaev（体系最全、含数理统计）相比，Varadhan 的独特价值在于**终点明确指向大偏差**——这是其余教材略去的硬骨头。对做 ML 的人，第 10 章是 PAC-Bayes、稀有事件模拟、熵正则的理论母体，第 9 章是扩散生成模型与 Black-Scholes 的数学根基。

**阅读策略（分阶段）**：前 4 章可与已读 Williams/Shiryaev 笔记做「测度复习」，重点吃透 Carathéodory 扩张、DCT、三级数这三件反复使用的工具（Ch 2/3/4）。中段 Ch 5（Prohorov + Skorokhod）与末章 Ch 10（Cramér + Varadhan）是本书招牌，值得逐节手推——Ch 5 的「Prohorov 胎紧 → 有限维相容 → 弱收敛」三步法是研究级概率的标准机器，Ch 10 的「rate function → Cramér → Varadhan 引理」是大偏差的完整链条。建议每章用 Python 验证：Ch 4 跑 $\sqrt n(\bar X_n-\mu)$ 看 CLT 收紧、Ch 5 跑部分和过程路径验证 Donsker、Ch 9 跑 Itô 积分验证二次变差 $\to t$、Ch 10 跑 $P(\bar X_n\ge a)$ 对 $n$ 取对数验证斜率 $=-I(a)$。若第 10 章意犹未尽，可续读 Dembo-Zeitouni《Large Deviations Techniques》做纵深。

---

## §10 与本仓库其他笔记的交叉引用

**与仓库已读经典的对话**：
- **↔ breiman_概率**：Breiman 是「测度直通车」，遍历/无穷可分见长，但**无大偏差**；Varadhan 是「通向大偏差的专线」，弱收敛（Prohorov/Skorokhod）比 Breiman 更系统。读 Breiman Ch 9-12 学「遍历 + 无穷可分」，读 Varadhan Ch 5、Ch 10 补「弱收敛严格化 + 大偏差」——二者在 Ch 4 LLN/CLT 完全重叠可互证，在 Ch 5/10 上互补。
- **↔ loeve_概率论I_GTM45**：Loève 是百科式、独立性为唯一代数支柱，把三级数/0-1 律榨到极致；Varadhan 更紧凑，同样以独立性（Ch 3）起手但快速推进到弱收敛与大偏差。读 Loève Ch 4/7 学「独立性最严格推导」，读 Varadhan 学「独立性之后往哪走」。
- **↔ shiryaev_概率GTM95**：Shiryaev 体系最完备（含数理统计、最优滤波），但厚重难通读；Varadhan 是 Shiryaev 的「分析压缩版 + 大偏差扩展」，10 章覆盖 Shiryaev 大半内容并多出第 10 章。读 Varadhan 建主线，遇细节查 Shiryaev。
- **↔ williams_概率与鞅**：Williams 以鞅为中心、把 LLN/似然比都化为鞅论推论；Varadhan 的 Ch 6 鞅论是「为中段停时与末章变分铺路」的工具章，不追求 Williams 那种「以鞅统一」的优雅，但 Prohorov/Skorokhod 比 Williams 扎实。二者互补：Williams 给鞅的直觉化叙述，Varadhan 给弱收敛与大偏差的纵深。
- **↔ shreve_随机分析金融卷II / karatzas_shreve_GTM113**：Shreve II 与 Karatzas-Shreve 是 Itô 微积分的金融/纯数学深耕，比 Varadhan Ch 9 详细数倍。读 Varadhan Ch 9 建骨架，深入读 Shreve II——尤其 Black-Scholes、Feynman-Kac、Girsanov 在 Shreve II 有完整展开。
- **↔ feller_概率论卷一/卷二**：Feller 是组合直觉派，卷一无测度论、卷二以 Laplace/特征函数分析见长；Varadhan 是测度分析派。读 Feller 卷一补「计数手感」，读 Varadhan 补「测度严格 + 大偏差」。
- **↔ durrett_概率论**：Durrett 是现代研究级教材，用更多当代例子（Markov 链、Brown 运动预演）驱动，但**无大偏差专章**；Varadhan 更紧凑且终点明确。读 Durrett 补「应用直觉与现代记号」，读 Varadhan 补「弱收敛严格化与大偏差」——二者在 Ch 5 弱收敛上重叠可互证，在 Ch 10 上互补。
- **↔ vershynin_高维概率 / wainwright_高维统计**：这两本是高维统计的现代教材，集中不等式（concentration）是核心工具。集中不等式刻画「$\bar X_n$ 偏离 $\mu$ 的尾部」的**非渐近**界，而 Varadhan Ch 10 大偏差是**渐近精确**率——前者是后者的「有限 $n$ 版本」。读 Varadhan Ch 10 建大偏差直觉，读 vershynin/wainwright 学非渐近应用，二者是「渐近精确 vs 非渐近可用」的互补。

**AI / 工程锚点**：
- 🟢 **Ch 10 Cramér/Varadhan → PAC-Bayes 泛化界**：PAC-Bayes 界 $\mathrm{KL}(Q\|P)+\frac{\log(1/\delta)}n$ 的指数衰减本质是大偏差——McAllester、Catoni 的 PAC-Bayes 推导直接用 Cramér 型 LDP。读本章后可回看 `mohri_机器学习理论基础` 的 PAC-Bayes 章。
- 🟢 **Ch 10 Varadhan 引理 → 最大熵强化学习 & 策略梯度**：Soft Actor-Critic 的「熵正则 $E[\log\pi]$」+ 报酬的权衡，本质是 Varadhan 公式 $\sup(f-I)$ 的变分——$I$ 即相对熵。这是「最大熵原理统一强化学习与最优控制」的数学母体。
- 🟢 **Ch 5 Prohorov + Ch 8 Donsker → 轨迹优化 & 稀有事件模拟**：Prohorov 胎紧是「证明 MCMC/重要性采样收敛」的标准工具；Donsker 不变原理把「离散随机游走」连续化为 Brown 运动，是序贯分析、A/B 测试序贯检验的理论基础。
- 🟢 **Ch 9 Itô 公式 → 扩散生成模型（DDPM/Score-based）**：扩散模型的反向去噪 SDE $dX_t=f\,dt+g\,dW_t$ 直接用 Itô 公式推导 score matching；Song-Yang 的 score-based 生成框架建立在 Itô 微积分与 Fokker-Planck 方程之上。读本章后可回看 `goodfellow_深度学习` / `bishop_深度学习` 的生成模型章。
- 🟡 **Ch 7 Markov 链遍历定理 → MCMC 收敛诊断**：遍历定理保证「时间平均趋于 $\pi$」，是 Metropolis-Hastings、HMC、Gibbs 采样有效的理论基石；R-hat 诊断、ESS（有效样本量）估计都依赖遍历速率。
- 🟡 **Ch 10 大偏差 → 强化学习探索 & 罕见事件估计**：大偏差给出「罕见回报轨迹」的指数衰减率，是重要性采样（importance sampling）选择「tilting 测度」的理论依据——最优 tilting 恰由 rate function 的极小化点决定。策略梯度中「罕见高回报轨迹」的方差控制，本质是大偏差的变分问题。

> **一句话总结本书在专家路径中的位置**：Varadhan 是「概率随机过程」候选方向的**大偏差入口**——读完本书，你不仅掌握了从测度到 Itô 的标准装备，更获得了理解 PAC-Bayes、扩散模型、最大熵强化学习的「稀有事件语言」。它是 Breiman（测度直通车）与 Williams（鞅中心化）之后，补齐「分布层渐近 + 稀有事件」的最后一块拼图。
