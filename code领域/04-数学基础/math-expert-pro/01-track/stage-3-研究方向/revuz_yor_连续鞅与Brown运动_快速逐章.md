# Daniel Revuz, Marc Yor《连续鞅与 Brown 运动》 · 快速逐章精读

> **原书名**：Continuous Martingales and Brownian Motion（Grundlehren der math. Wissenschaften, vol. 293）　**著者**：Daniel Revuz, Marc Yor　**出版社**：Springer　**版次**：3rd ed, 1999
> **读于**：2026-07-03
> **定位**：连续鞅论与现代 Brown 运动研究的「百科全书级」专著，以「连续局部鞅 = 时间变换的 Brown 运动」(Dambis-Dubins-Schwarz) 为统一骨架，深入局部时、excursion 理论、Bessel/Ray-Knight、Skorokhod 嵌入等 Karatzas-Shreve 仅浅尝的专题。
> **特色**：抽象度比 GTM113 更高一档，习题即定理，是「做随机过程研究的人」案头必备的纵深手册。
> **声明**：本文为「快速逐章精读」，每章给核心逻辑串联 + 飞腾锚点 + 关键定理 + 自测题，非逐页翻译。

---

## §0 引言：Revuz-Yor 是什么，为什么读它

Daniel Revuz 与已故的 Marc Yor（1949–2014，法国概率学派代表人物，Bertoin、Le Gall 的同代人）合著的这部《连续鞅与 Brown 运动》是**现代连续时间随机过程研究的标准参考**。它与 Karatzas-Shreve（GTM113）并称随机分析两大经典，但二者的「气质」截然不同：K&S 是「从 Brown 运动严格构造 Itô 积分、为金融数学铺路」的工程化教材，主线清晰、面向应用；Revuz-Yor 则是「以连续鞅为宇宙中心」的研究手册，把局部时（local time）、excursion（远足）、Bessel 过程、Ray-Knight 定理、Skorokhod 嵌入、概率位势论这些「高级专题」系统化、深度化——其中 excursion 理论与 Bessel 过程的篇幅几乎是同类教材的总和。

全书的精神浓缩为一句：**「一切连续局部鞅都是换了时钟的 Brown 运动，而 Brown 运动的全部深刻结构都藏在它的局部时与 excursion 里。」** 这条主线由 **Dambis-Dubins-Schwarz 定理**（Ch 5）奠基：连续局部鞅 $M_t$ 满足 $M_t = \beta_{\langle M\rangle_t}$，其中 $\beta$ 是某 Brown 运动、$\langle M\rangle_t$ 是二次变差（新时钟）。于是整本书的后半部（Ch 8–13）都在「解剖」Brown 运动的精细结构——局部时 $L_t^a$ 测量路径在 $a$ 点逗留的「时间密度」，excursion 律刻画路径离开 $0$ 的「片段集合」，Bessel 过程给出 $|M_t|$（反射鞅）的分布族，Ray-Knight 把局部时沿时间推平成「空间中的 BESQ 过程」。这套工具是研究扩散过程遍历性、随机控制、score-based 生成模型（反向 SDE）的硬通货。

**读书策略**：本书不适合零基础首读，前置必须读完 Karatzas-Shreve 或 Williams+Shreve 随机分析金融 II。建议路径是「K&S 打底 → Revuz-Yor 专题深化」。本书 Ch 0–7 与 K&S 高度重叠（可快速略读对照），真正值得逐章精读的是 Ch 4（Lévy 刻画 + BDG）、Ch 5（Itô 公式 + DDS）、Ch 8（局部时 / Tanaka）、Ch 9（excursion）、Ch 10（Bessel / Ray-Knight）、Ch 12（Skorokhod 嵌入）——这六章是本书相对所有同类教材的「不可替代价值」。对做 Diffusion ML 模型的人，Ch 7（Itô 流）+ Ch 13（渐近）直接关联反向 SDE 的数值求解与 score 匹配的一致性分析。

| 书 | 风格 | 严格性 | 适合谁 |
|---|---|---|---|
| **Revuz-Yor《连续鞅与 BM》** | 连续鞅中心化、专题纵深、习题即定理 | 极高（研究级，抽象最深） | 已读 K&S、做随机过程研究者 |
| **Williams《概率与鞅》** | 离散鞅中心化、文学化、直觉先行 | 高（完整测度论） | 想用最短路径从测度到鞅者 |
| **Karatzas-Shreve GTM113** | Brown 运动 + Itô 积分 + SDE 系统化 | 极高（金融数学圣经） | 金融数学 / 随机分析应用者 |
| **Feller《概率论》卷二** | 经典直觉派、从离散升级到测度 + 扩散 | 中-高（直觉丰富） | 想理解概率思想演进史者 |

**阅读门槛与破解**：本书以「最高抽象、最密习题」著称。三大门槛：①**抽象度陡升**——连续局部鞅、半鞅、局部时、excursion 律层层叠加，Ch 9（excursion）与 Ch 10（Ray-Knight）尤甚；破解法：先用 K&S（已读）建立 Itô 积分手感，本书 Ch 0–5 与 K&S 对照略读，真正精读只投在 Ch 4–5 + Ch 8–10 + Ch 12。②**习题即定理**——大量习题是正文未证的重要结果（Pitman $2M-X$ 定理、Bougerol 恒等式、Burkholder-Gundy 精确常数），无答案；破解法：选做「构造性」习题（计算局部时、验证 excursion 分布），跳过「存在唯一性」难题。③**符号密集**——$\mathcal{F}_T$、$\langle M\rangle$、$L_t^a$、$n(de)$、BESQ$(\delta)$ 等符号贯穿全书；破解法：首读时建一张「符号速查卡」，每章开头核对。关键提醒：**手推 Itô 公式 + Tanaka 公式是最低门槛的硬通货**，务必各做 10 道以上；DDS 定理与 Ray-Knight 定理的「换时钟/换变量」思想比公式本身更重要。

---

## §1 全书 13 章骨架一览（飞腾锚点分布）

| 章 | 标题 | 核心概念 | 飞腾锚点 |
|:--:|------|----------|----------|
| 0 | Preliminaries | 测度论回顾、单调类定理、条件期望刻画 | TLB 4.81× |
| 1 | Introduction | 高斯变量、0-1 律、过程引论 | Schmidt 正交化 |
| 2 | Stochastic Processes | 可分性、循序可测、停时、$\mathcal{F}_T$ | UDOT 16.9× |
| 3 | Martingales | Doob 不等式、收敛、可选停时、UI | Iron Law <2% |
| 4 | Continuous Martingales & BM | Lévy 刻画、BDG、二次变差 ⭐ | FP16 3.81× |
| 5 | Stochastic Integration | Itô 积分、半鞅、Itô 公式、DDS ⭐⭐ | matmul 15× |
| 6 | Linear SDEs | OU 过程、Itô vs Stratonovich | Schmidt 正交化 |
| 7 | General SDEs | 强/弱解、Yamada-Watanabe、Itô 流 ⭐ | 分支预测 0.71/3.14 |
| 8 | Local Times | Tanaka 公式、occupation 公式、逆局部时 ⭐⭐ | GEMM 9.45 GFLOPS |
| 9 | Excursion Theory | Itô 律、Poisson 点过程、局部时作时钟 ⭐⭐ | TLB 4.81× |
| 10 | Bessel & Ray-Knight | BES$(\delta)$、Ray-Knight 定理 ⭐⭐ | Iron Law <2% |
| 11 | Probabilistic Potential Theory | Dirichlet 问题、Green 函数、容量 | UDOT 16.9× |
| 12 | Skorokhod Embedding | 给分布嵌入 BM、Azéma-Yor ⭐ | FP16 3.81× |
| 13 | Asymptotic Results | 重对数律 LIL、重对数律、局部时渐近 | GEMM 9.45 GFLOPS |

> **飞腾锚点复用说明**：13 章 > 8 锚点，故合理复用（同一锚点隔数章再出现，标注不同角度），保证相邻章绝不重复。TLB 在 Ch 0（$\sigma$-代数分层）/ Ch 9（局部时作 excursion 时钟分层）双用，前者是「可测集层级生成」、后者是「时间按局部时分层」；Schmidt 正交化在 Ch 1（高斯向量协方差对角化）/ Ch 6（OU 过程稳态谱分解）呼应；UDOT 在 Ch 2（过程样本路径累加）/ Ch 11（Green 函数期望积分）双用；Iron Law 在 Ch 3（Doob 极大值误差界）/ Ch 10（Ray-Knight 收敛）双用；FP16 在 Ch 4（连续路径模拟）/ Ch 12（嵌入分位数精度）双用；GEMM 在 Ch 8（occupation 高维积分）/ Ch 13（渐近大样本模拟）双用。

**章节难度与精读权重**（每周 10-20h 预算下的建议投入，基于「与 K&S 重叠度」划分）：

| 章 | 难度 | 与 K&S 重叠 | 建议投入 | 优先级 |
|:--:|:---:|:---:|:---|:---:|
| 0 | ★★ | 高 | 5%（略读回查工具） | 低 |
| 1 | ★★ | 中 | 5%（高斯 + 0-1 律复习） | 低 |
| 2 | ★★★ | 高 | 8%（停时 / 循序可测，略读） | 中 |
| 3 | ★★★ | 高 | 8%（Doob 不等式 + 收敛，略读） | 中 |
| 4 | ★★★★ | 中 | **15%（Lévy 刻画 + BDG 手推）** | 高 |
| 5 | ★★★★★ | 中 | **18%（Itô 积分 + Itô 公式 + DDS ⭐主力）** | 最高 |
| 6 | ★★★ | 低 | 8%（OU 显式解 + Stratonovich） | 中 |
| 7 | ★★★★ | 中 | 8%（强弱解 + Yamada-Watanabe） | 高 |
| 8 | ★★★★★ | 低 | **12%（Tanaka + occupation ⭐独家）** | 最高 |
| 9 | ★★★★★★ | 极低 | **8%（Itô 律，最抽象）** | 高 |
| 10 | ★★★★★ | 极低 | **8%（Bessel + Ray-Knight ⭐独家）** | 高 |
| 11 | ★★★★ | 低 | 5%（Dirichlet 概率解） | 中 |
| 12 | ★★★★ | 极低 | **7%（Skorokhod 嵌入 ⭐思想性）** | 高 |
| 13 | ★★★ | 中 | 3%（LIL 查阅） | 低 |

> **核心判断**：Ch 0–3 与 Williams / K&S 高度重叠，首读略读即可（合计 ~26%）；真正值得逐章精读、且 K&S 未触及的是 **Ch 4–5（连续鞅核心）+ Ch 8–10（局部时/excursion/Bessel 三连）+ Ch 12（Skorokhod）**——这六章占本书「不可替代价值」的 90%。建议把 70% 时间投在这六章。

---

## 第 0 章 · Preliminaries（预备）

**核心**：本章是工具箱回顾，不引入新概念，但把全书反复使用的三件「地基工具」摆到位：(i) **单调类定理**——证明「某性质对所有有界可测函数成立」的标准套路（先证示性函数、再线性组合、再单调极限）；(ii) **条件期望的等价刻画**——$Y=E[X|\mathcal{G}]$ $\iff$ $Y$ 是 $\mathcal{G}$-可测且 $\int_A Y=\int_A X$ 对所有 $A\in\mathcal{G}$，这是后续定义鞅、停时处条件期望的「宪法」；(iii) **正则条件概率**（regular conditional distribution）——保证连续时间过程在停时处仍有良好条件分布。本章节奏快，建议首读略过、二刷按需回查。

**飞腾锚点**：🟡 TLB 4.81× [E04] —— 单调类定理的核心是「分层生成 + 逐层传播」：先在生成 $\pi$-系（叶子页）上验证性质，再经线性/极限运算传播到整个 $\sigma$-代数（聚合页）。这与 TLB 多级页表「叶子页验证 → 高层页聚合」的层级翻译同构——命中率提升 4.81× 对应把常用可测集预先「缓存」为生成元，避免逐点验证可测性。条件期望的唯一性也靠此：两测度在生成元上一致即在全空间一致。

**关键定理**（单调类定理）：设 $\mathcal{H}$ 为「对有界逐点极限封闭」的函数族（单调类），若 $\mathcal{H}$ 包含某 $\pi$-系 $\mathcal{C}$ 的所有示性函数，则 $\mathcal{H}$ 包含所有 $\sigma(\mathcal{C})$-可测有界函数。重要性：这是「从示性函数推广到一般可测函数」的合法性引擎，Itô 公式、Fubini、鞅性质的全空间验证全靠它。

**自测**：用单调类定理证明：若 $X,Y$ 独立，$f$ 有界可测，则 $E[f(X,Y)|\sigma(X)]=g(X)$，其中 $g(x)=E[f(x,Y)]$。（提示：先对 $f=\mathbf{1}_{A\times B}$ 验证，再单调类推广。）

---

## 第 1 章 · Introduction（引言：高斯变量与 0-1 律）

**核心**：本章用「高斯」与「0-1 律」两个主题为全书预热。高斯随机变量是 Brown 运动、OU 过程、线性 SDE 解的分布族——全书反复出现的「正态骨架」。关键事实：高斯向量不相关 $\iff$ 独立（一般随机变量不成立），这让协方差矩阵完全决定联合分布。0-1 律（Kolmogorov 尾 $\sigma$-代数、Hewitt-Savage 可交换事件）是「极限事件的概率非 0 即 1」的深刻结论，是后续 LIL、遍历定理、鞅收敛的哲学基础。本章还给出几个「过程的雏形」（独立增量过程、马氏过程预告），为 Ch 2 正式定义铺垫。

**飞腾锚点**：🟢 Schmidt 正交化 —— 高斯向量 $X\sim N(0,\Sigma)$ 的不相关 $\iff$ 独立，意味着协方差矩阵 $\Sigma$ 的对角化 = 分解为独立高斯分量。Schmidt 正交化是「协方差谱分解 → 独立高斯基」的算法：把相关高斯向量投影到 $\Sigma$ 的特征向量正交基上，得到独立 $N(0,\lambda_i)$ 分量。这是 Karhunen-Loève 展开的前奏（Ch 6 OU 过程的稳态分布正是这样分解），也是条件期望 $L^2$ 正交投影在高斯情形的离散原型。

**关键定理**（高斯不相关 $\iff$ 独立）：$(X_1,\dots,X_n)$ 联合高斯，则 $X_i$ 两两不相关 $\iff$ 相互独立。重要性：这把「独立性」翻译为「协方差矩阵对角」，是线性 SDE（Ch 6）解的高斯性、Kalman 滤波正态假设合法性的根基。

**自测**：$(X,Y)$ 联合高斯，$Var(X)=Var(Y)=1$，$Cov(X,Y)=\rho$。求条件分布 $Y|X=x$。（答：$N(\rho x,\,1-\rho^2)$。）验证 $\rho=0$ 时退化为无条件 $N(0,1)$（独立性）。

---

## 第 2 章 · Stochastic Processes（随机过程：可测性与停时）

**核心**：本章把「过程」严格化为 $X:(\Omega\times\mathbb{R}_+,\mathcal{F}\otimes\mathcal{B})\to\mathbb{R}$，并区分四种可测性：**可测**（$\mathcal{F}\otimes\mathcal{B}$-可测）、**适应**（$X_t$ 是 $\mathcal{F}_t$-可测）、**循序可测**（progressive，在 $[0,t]\times\Omega$ 上 $\mathcal{B}([0,t])\otimes\mathcal{F}_t$-可测）、**可料**（predictable，左连续适应）。循序可测是 Itô 积分被积函数的最低门槛——保证 $X_s(\omega)$ 在「不偷看未来」的前提下可积。**停时** $T$（$\{T\leq t\}\in\mathcal{F}_t$）是「不预知未来的随机时间」，停时 $\sigma$-代数 $\mathcal{F}_T=\{A:A\cap\{T\leq t\}\in\mathcal{F}_t\}$ 刻画「到时刻 $T$ 为止可观测的信息」。强马氏性（停时处仍马氏）是 Ch 7 弱解存在性的关键。

**飞腾锚点**：🟡 UDOT 16.9× [E05] —— 一个过程 $\{X_t\}$ 是 $t$-参数的函数族，对其进行采样、积分、停时判定，本质是「沿 $t$ 的加权累加」。停时 $T=\inf\{t:X_t\in A\}$ 的数值实现需扫描 $t$ 网格、对条件 $X_t\in A$ 累计求和判定首个触发点。UDOT 无符号点积 16.9× 加速这类「过程样本路径的批量数值处理」——把整条路径的逐点判定压成向量累加指令，正如 Itô 积分 $\int X_s\,dW_s$ 的离散化是双索引求和。

**关键定理**（停时 $\sigma$-代数与强马氏性）：$S\leq T$ 停时 $\Rightarrow$ $\mathcal{F}_S\subseteq\mathcal{F}_T$；$X$ 循序可测、$T$ 停时 $\Rightarrow$ $X_T\mathbf{1}_{\{T<\infty\}}$ 是 $\mathcal{F}_T$-可测（「停时处的过程值可观测」）。重要性：这是 Ch 5 Itô 积分在停时处良好定义、Ch 7 弱解存在性的前提。

**自测**：$W$ 是 Brown 运动，$T_a=\inf\{t:W_t=a\}$（首达 $a$ 时刻）。验证 $T_a$ 是停时（$\{T_a\leq t\}=\{\sup_{s\leq t}W_s\geq a\}\in\mathcal{F}_t$）。再证 $\mathcal{F}_{T_a}\not=\mathcal{F}_{T_b}$（$a<b$），即「到达不同水平的信息量不同」。

---

## 第 3 章 · Martingales（鞅：Doob 不等式、收敛、可选停时）

**核心**：本章是离散鞅论的「浓缩版」（Williams 已系统讲过，这里复习 + 升级到连续时间框架的预备）。核心三件套：(i) **可选停时定理**——有界停时 $S\leq T$ 下 $E[M_T|\mathcal{F}_S]=M_S$（公平游戏无必胜策略）；(ii) **Doob 极大值不等式**（$L^p$ 版）——下鞅 $X$ 满足 $\|\sup_{s\leq t}X_s\|_p\leq\frac{p}{p-1}\|X_t\|_p$（$p>1$），把「最大值」控制在「终值」的常数倍内；(iii) **鞅收敛定理**——$L^1$ 有界上鞅 a.s. 收敛、UI 鞅 $L^1$ 收敛。本章为 Ch 4 连续鞅的 BDG 不等式（极大值 $\leftrightarrow$ 二次变差）做铺垫。

**飞腾锚点**：🟡 Iron Law <2% [Lab00] —— Doob 极大值不等式 $\|\sup|M|\|_p\leq\frac{p}{p-1}\|M\|_p$ 是一条「极大值误差铁律」：给定可容许极大值偏差 $\varepsilon$，鞅的 $L^p$ 范数决定极大值超界的概率界。这正类比性能工程中 CPI 必须 $<2\%$ 才可信——「鞅的最大波动被其能量控制」与「指令的最大延迟被 CPI 控制」同构。$p=2$ 时系数为 2，工程中常据此估计「最坏路径波动是 RMS 波动的 2 倍」。

**关键定理**（Doob $L^p$ 极大值不等式）：$\{M_s\}_{s\leq t}$ 非负下鞅，$p>1$，则
$$E\Big[\sup_{s\leq t}M_s^p\Big]\leq\Big(\frac{p}{p-1}\Big)^p E[M_t^p].$$
重要性：这是「控制鞅最大波动」的核心工具，是 BDG 不等式（Ch 4）、SGD 收敛证明、集中不等式的母体。$p\to1$ 时系数发散，提示 $L^1$ 情形需换用 Doob 上穿不等式。

**自测**：$W$ Brown 运动，$M_t=W_t^2-t$ 是鞅（验证 $E[M_t|\mathcal{F}_s]=M_s$）。用 Doob 不等式（$p=2$）估计 $E[\sup_{s\leq T}M_s^2]$ 的上界。（答：$\leq 4\,E[M_T^2]=4\,E[(W_T^2-T)^2]$，对 $T=1$ 算出 $E[W_1^4]=3$，$E[M_1^2]=3-1=2$，故界为 $8$。）

---

## 第 4 章 · Continuous Martingales and Brownian Motion（连续鞅与 BM：Lévy 刻画、BDG）⭐

**核心**：**全书枢纽章**。Brown 运动 $W$ 是「连续、$W_0=0$、独立平稳增量 $W_t-W_s\sim N(0,t-s)$」的过程。**Lévy 刻画定理**给出逆向判据：若连续局部鞅 $M$ 满足 $M_0=0$ 且 $M_t^2-t$ 也是局部鞅，则 $M$ 就是 Brown 运动——「平方减时间仍是鞅」唯一刻画了 Brown 性。**二次变差** $\langle M\rangle_t$ 是连续局部鞅的「内蕴时钟」：$M_t^2-\langle M\rangle_t$ 是鞅。**BDG 不等式**把极大值与二次变差挂钩：$E[\sup_{s\leq t}|M_s|^p]\asymp E[\langle M\rangle_t^{p/2}]$（常数 $c_p,C_p$ 与 $t$ 无关）。本章还证明 BM 的经典性质：路径连续但无处可导、反射原理、首达时分布。

**飞腾锚点**：🟡 FP16 3.81× [L01] —— Brown 路径「连续但处处不可导」是反直觉的：数值模拟时，高频抖动在 FP16（3.81× 加速但精度低、动态范围窄）下可能被精度损失「平滑掉」，制造「假光滑」的伪路径，影响二次变差 $\langle W\rangle_t=t$ 的数值验证。模拟 BDG 不等式、Lévy 刻画时，需在「精度（FP64，准确捕获高频抖动）」与「速度（FP16，快速长链）」间权衡——这正是「连续但不可导」对数值实现的硬约束：精度不足会让 $M_t^2-t$ 「假鞅」。

**关键定理**（Lévy 刻画定理）：$\{M_t\}$ 连续、$M_0=0$、适应某 filtration。则 $M$ 是 Brown 运动 $\iff$ $M$ 与 $M_t^2-t$ 都是（局部）鞅。重要性：这是「从鞅性质反推 Brown 性」的唯一工具——Ch 5 DDS 定理、Ch 7 Girsanov 定理、Ch 12 Skorokhod 嵌入的正确性全靠它。它把「独立高斯增量」替换为「鞅 + 二次变差」的内蕴刻画，是现代随机分析的基石。

**关键定理**（BDG 不等式）：$M$ 连续局部鞅，$M_0=0$，$p>0$，则存在常数 $0<c_p<C_p<\infty$（仅依赖 $p$）使
$$c_p\,E[\langle M\rangle_t^{p/2}]\leq E\Big[\sup_{s\leq t}|M_s|^p\Big]\leq C_p\,E[\langle M\rangle_t^{p/2}].$$
重要性：BDG 把「鞅的最大波动」与「二次变差」双向控制，是 SDE 解矩估计、随机分析收敛证明的核心不等式。$p=2$ 时 $C_2=4$（Doob），是金融风险管理 VaR 估计的理论依据。

**自测**：用 Lévy 刻画证明：若 $W$ 是 BM，则 $\tilde W_t=\int_0^t \mathrm{sgn}(W_s)\,dW_s$ 也是 BM（Lévy 变换）。（提示：$\tilde W$ 连续局部鞅，$\tilde W_t^2=\int\mathrm{sgn}^2\,d\langle W\rangle-2\int\tilde W\,\mathrm{sgn}\,dW$，故 $\tilde W_t^2-t$ 是鞅。）

**连续鞅三大刻画速查**（务必区分，Ch 4–5 反复使用）：

| 刻画 | 陈述 | 方向 | 用途 |
|------|------|------|------|
| **定义** | 连续、独立平稳高斯增量 | 直接 | 构造 BM |
| **Lévy 刻画** | $M$ 与 $M^2-t$ 均局部鞅 | 反推 | 从鞅性质证明 Brown 性 |
| **DDS 定理**（Ch 5） | $M_t=\beta_{\langle M\rangle_t}$ | 归约 | 把连续局部鞅化为 BM |

> BDG 常数速查：$p=2$ 时 $c_2=1$、$C_2=4$；$p=1$ 时 $c_1=\sqrt{2/\pi}$、$C_1=\sqrt{8}$；$p=4$ 时 $C_4\leq 4^4$。工程中常取「$\sup\|M\|_p\leq C_p\|\sqrt{\langle M\rangle}\|_p$」的实用形式做矩估计。

---

## 第 5 章 · Stochastic Integration（随机积分：Itô 积分、半鞅、DDS）⭐⭐

**核心**：**全书技术核心章**。Itô 积分对「连续局部鞅 $M$」与「$M$-可料被积过程 $H$」（$\int_0^t H_s^2\,d\langle M\rangle_s<\infty$）定义为随机黎曼和的极限：$\int_0^t H_s\,dM_s=\lim\sum H_{t_i}(M_{t_{i+1}}-M_{t_i})$，结果是连续局部鞅，二次变差 $\langle\int H\,dM\rangle_t=\int H^2\,d\langle M\rangle$。**半鞅** $X=M+A$（局部鞅 + 有限变差过程）是 Itô 积分的最大可积类。**Itô 公式**是随机微积分的链式法则：$C^2$ 函数 $f$ 下 $df(X_t)=f'(X_t)\,dX_t+\frac12 f''(X_t)\,d\langle X\rangle_t$——多出的 $\frac12$ 项是 Itô 与经典微积分的根本分歧。**Dambis-Dubins-Schwarz 定理**：连续局部鞅 $M$ 满足 $M_t=\beta_{\langle M\rangle_t}$（$\beta$ 为某 BM），把「所有连续局部鞅」统一为「换了时钟的 Brown 运动」。

**飞腾锚点**：🟢 matmul 15× [V03] —— Itô 积分 $\int_0^t H_s\,dM_s=\sum_i H_{t_i}(M_{t_{i+1}}-M_{t_i})$ 是被积函数 $H$ 与鞅增量 $\Delta M$ 的**双线性型**，离散化后正是矩阵乘法 $C_{ik}=\sum_j A_{ij}B_{jk}$ 的结构。matmul 15× 加速直接服务于「Itô 积分 = 双索引求和」的批量数值实现，把整条积分路径压成矩阵运算。二次变差 $\langle M\rangle_t=\sum(\Delta M)^2$ 则是「自伴双线性型」的迹，同样受惠于矩阵吞吐。

**关键定理**（Itô 公式）：$X$ 连续半鞅，$f\in C^2$，则
$$f(X_t)=f(X_0)+\int_0^t f'(X_s)\,dX_s+\frac12\int_0^t f''(X_s)\,d\langle X\rangle_s.$$
重要性：这是随机微积分的「链式法则」，多出的 $\frac12 f''\,d\langle X\rangle$ 项是 Black-Scholes 方程、Tanaka 公式（Ch 8）、反向 SDE 的来源。手算 Itô 公式是本章最低门槛的硬通货，务必做 10 道以上。

**关键定理**（Dambis-Dubins-Schwarz, DDS）：$M$ 连续局部鞅，$M_0=0$，$\langle M\rangle_\infty=\infty$。令 $T(s)=\inf\{t:\langle M\rangle_t>s\}$，$\beta_s=M_{T(s)}$，则 $\beta$ 是 BM 且 $M_t=\beta_{\langle M\rangle_t}$。重要性：DDS 把「连续局部鞅」完全归约为「Brown 运动 + 时间变换」，是 Ch 4 Lévy 刻画的逆命题，也是 Ch 10 Bessel 过程、Ch 12 Skorokhod 嵌入的理论枢纽。

**自测**：用 Itô 公式计算 $W_t^2$。（答：$W_t^2=2\int_0^t W_s\,dW_s+t$，故 $W_t^2-t$ 是鞅——Lévy 刻画的反向验证。）再算 $e^{\sigma W_t-\sigma^2 t/2}$（答：它等于 $1+\int_0^t\sigma e^{\sigma W_s-\sigma^2 s/2}\,dW_s$，是鞅——Black-Scholes 的贴现资产价格）。

**Itô 积分五大性质清单**（务必内化，全书反复使用）：

1. **局部鞅性**：$H$ 可料、$\int H^2\,d\langle M\rangle<\infty$，则 $\int H\,dM$ 是连续局部鞅（Itô 积分保持鞅性——这是「Itô 取左端点」的根本理由）。
2. **二次变差**：$\langle\int H\,dM\rangle_t=\int_0^t H_s^2\,d\langle M\rangle_s$（「能量守恒」——被积函数平方加权二次变差）。
3. **Itô 等距**：$E[(\int H\,dM)^2]=E[\int H^2\,d\langle M\rangle]$（$L^2$ 情形，Itô 积分是 $L^2$ 等距）。
4. **分部积分**：$X_tY_t=X_0Y_0+\int X\,dY+\int Y\,dX+\langle X,Y\rangle_t$（多出协变差项，经典乘法法则的随机修正）。
5. **线性性 + 局部化**：$\int(aH+bK)\,dM=a\int H\,dM+b\int K\,dM$；可料停时可截断积分。

> 性质 1 是 Ch 4 Lévy 刻画可用性的根基；性质 2 是 BDG 不等式的输入；性质 3 是 $L^2$ 理论的核心；性质 4（分部积分）是 Itô 公式多元版、Black-Scholes delta-hedging 的来源；性质 5 保证 Itô 积分在停时处行为良好。

---

## 第 6 章 · Linear SDEs（线性 SDE：OU 过程、Itô 与 Stratonovich）

**核心**：线性 SDE 是少数有显式解的 SDE，是「可解析处理的随机系统」的代表。**Ornstein-Uhlenbeck 过程** $dX_t=-\lambda X_t\,dt+\sigma\,dW_t$ 的解 $X_t=e^{-\lambda t}X_0+\sigma\int_0^t e^{-\lambda(t-s)}\,dW_s$ 是平稳高斯过程，稳态分布 $N(0,\sigma^2/(2\lambda))$——这是「噪声驱动下的回归系统」的标准模型（物理学 Langevin 方程、神经元膜电位、利率模型 Vasicek）。**Itô 与 Stratonovich** 积分的区别在于「被积函数取值点」：Itô 取左端点（不偷看未来，鞅性质好），Stratonovich 取中点（链式法则与经典微积分一致，物理建模友好）。二者的转换公式 $\int X\circ dW=\int X\,dW+\frac12\langle X,W\rangle$ 是物理学家与概率学家对话的桥梁。

**飞腾锚点**：🟢 Schmidt 正交化 —— OU 过程的稳态是高斯分布，其协方差函数 $C(s,t)=\frac{\sigma^2}{2\lambda}e^{-\lambda|s-t|}$ 的谱分解（Karhunen-Loève 展开）把 $X_t$ 表示为正交高斯基的线性组合：$X_t=\sum_k \sqrt{\lambda_k}\xi_k e_k(t)$（$\xi_k$ iid $N(0,1)$，$e_k$ 正交）。Schmidt 正交化是构造这类正交基的算法——OU 过程的「模态分解」正是协方差算子特征向量的正交化，也是 PCA、Fredholm 积分方程数值解的母体。

**关键定理**（OU 过程显式解与稳态）：$dX_t=-\lambda X_t\,dt+\sigma\,dW_t$ 的解为 $X_t=e^{-\lambda t}X_0+\sigma\int_0^t e^{-\lambda(t-s)}\,dW_s$；当 $X_0\sim N(0,\sigma^2/(2\lambda))$ 时 $\{X_t\}$ 平稳，稳态协方差 $C(\tau)=\frac{\sigma^2}{2\lambda}e^{-\lambda|\tau|}$。重要性：OU 过程是「噪声 + 阻尼」系统的原型，是 Langevin 动力学、Vasicek 利率模型、Kalman-Bucy 滤波连续时间版的数学骨架。

**自测**：验证 OU 解的高斯性（$X_t$ 是 Itô 积分 $\int e^{-\lambda(t-s)}\,dW_s$，被积函数确定性 $\Rightarrow$ 高斯）。求 $E[X_t]$ 与 $Var(X_t)$（答：$E[X_t]=e^{-\lambda t}X_0$，$Var=\frac{\sigma^2}{2\lambda}(1-e^{-2\lambda t})$）。$t\to\infty$ 时方差收敛到 $\sigma^2/(2\lambda)$（稳态）。

**Itô vs Stratonovich 速查**：

| 积分 | 取值点 | 链式法则 | 性质 | 适用 |
|------|--------|----------|------|------|
| Itô $\int X\,dW$ | 左端点 $X_t$ | 多 $\frac12 f''\,d\langle X\rangle$ 项 | 鞅性好 | 概率、金融 |
| Stratonovich $\int X\circ dW$ | 中点 $\frac12(X_t+X_{t+dt})$ | 经典链式法则 | 物理友好 | 物理、几何 |

> 转换：$\int_0^t X_s\circ dW_s=\int_0^t X_s\,dW_s+\frac12\langle X,W\rangle_t$。SDE 从 Stratonovich 转 Itô 需加 Wong-Zakai 修正项。

---

## 第 7 章 · General SDEs（一般 SDE：强/弱解、Itô 流）⭐

**核心**：一般 SDE $dX_t=b(X_t)\,dt+\sigma(X_t)\,dW_t$ 的解理论远比线性情形复杂。**强解**：给定概率空间和 BM $W$，存在唯一适应过程 $X$（路径唯一）；**弱解**：只保证存在某概率空间、某 BM、某 $X$ 满足方程（分布存在，路径不一定唯一）。**Yamada-Watanabe 定理**：强解存在 + 路径唯一 $\iff$ 弱解存在 + 分布唯一（「强」与「弱」的精确关系）。**Itô 流** $X_t(x)$ 是把初始条件 $x$ 映到 $t$ 时刻状态的随机流，在系数光滑时关于 $x$ 是微分同胚——这是随机动力系统、随机微分几何的入口。本章还给出 Itô 解的矩估计、马氏性、Feller 性。

**飞腾锚点**：🟡 分支预测 0.71 vs 3.14 [Lab02] —— 强解与弱解的区别在于「路径是否唯一」。强解是「给定 BM，路径确定」（预测命中 0.71 周期，单一路径），弱解是「分布存在但路径可多重」（未命中 3.14 周期，分支展开）。Itô 流 $X_t(x)$ 关于 $x$ 的微分同胚性意味着「初始条件的微小扰动只产生微小路径分裂」——分支预测器对「下次扰动方向」的连续判定，正如 SDE 解对「噪声实现」的条件响应。

**关键定理**（强解存在唯一性）：$b,\sigma$ Lipschitz + 线性增长，则 SDE 存在唯一强解，且 $E[\sup_{s\leq t}|X_s|^2]<\infty$。Yamada-Watanabe：强解 + 路径唯一 $\iff$ 弱解 + 分布唯一。重要性：这是「SDE 良定性」的标准充分条件，是反向 SDE 数值解、Diffusion 模型采样合法性的前提。不满足 Lipschitz（如 $\sigma(x)=\sqrt{|x|}$）时需更精细的 Yamada-Watanabe 单边条件。

**自测**：$dX_t=|X_t|^\alpha\,dW_t$。$\alpha$ 在什么范围有路径唯一性？（Yamada-Watanabe：$\alpha\geq 1/2$ 唯一，$\alpha<1/2$ 可能不唯一。）这是「系数非光滑时唯一性」的经典判据。

**强解 vs 弱解速查**（务必区分，Ch 7 反复使用）：

| 概念 | 给定 | 保证 | 类比 |
|------|------|------|------|
| **强解** | 概率空间 + BM $W$ | 路径唯一（$\mathcal{F}^W$-可测） | 确定性算法 |
| **弱解** | 仅方程 | 存在某空间、某 BM、某 $X$ 满足分布 | 蒙特卡洛采样 |
| **路径唯一** | 给定 $W$ | 至多一个 $X$ 适应 $W$ | 函数（单值） |
| **分布唯一** | — | 所有解同分布 | 法则唯一 |

> Yamada-Watanabe 核心结论：弱解存在 + 路径唯一 $\Rightarrow$ 强解存在 + 分布唯一（反之亦然）。直觉：路径唯一保证「能从 BM 显式构造 $X$」，从而弱解升级为强解。工程含义：Diffusion 模型采样若系数 Lipschitz，则「不同随机种子产生不同样本」但「样本分布唯一」——这是 score-based 生成模型可重复性的数学保证。

---

## 第 8 章 · Local Times（局部时：Tanaka 公式、Occupation 公式）⭐⭐

**核心**：**本书相对所有同类教材最具深度的专题之一**。局部时 $L_t^a$ 是半鞅 $X$ 在水平 $a$ 处「逗留的时间密度」，严格定义为使 occupation 公式成立的唯一过程：$\int_0^t f(X_s)\,d\langle X\rangle_s=\int_\mathbb{R} f(a)L_t^a\,da$ 对所有有界可测 $f$。**Tanaka 公式**是 $|x|$ 的 Itô 公式（$|x|$ 在 $0$ 处不可导，需修正）：
$$|X_t|=|X_0|+\int_0^t \mathrm{sgn}(X_s)\,dX_s+L_t^0,$$
多出的 $L_t^0$ 正是局部时——它补偿了 $|X|$ 在 $0$ 处的「不可导损失」。BM 的局部时 $L_t^a$ 关于 $t$ 连续增、关于 $a$ 连续但 Hausdorff 维数 $1/2$（「空间方向比时间方向粗糙」）。**逆局部时** $L_t^{a-1}$ 的跳跃点构成 Poisson 点过程，是 Ch 9 excursion 理论的时钟。

**飞腾锚点**：🟡 GEMM 9.45 GFLOPS [Lab05] —— occupation 公式 $\int_0^t f(X_s)\,ds=\int f(a)L_t^a\,da$ 把「沿时间的积分」转换为「沿空间的积分」，数值实现需在 $(t,a)$ 二维网格上双重积分，是高维数值积分的典型负载。GEMM 9.45 GFLOPS 的吞吐服务于「局部时 $L_t^a$ 在 $(t,a)$ 平面上的大规模数值逼近」——把 occupation 网格的逐点累加压成矩阵吞吐，正如把「路径在每点的逗留密度」批量计算。

**关键定理**（Tanaka 公式）：$X$ 连续半鞅，则存在唯一连续增过程 $L_t^a$（局部时）使
$$|X_t-a|=|X_0-a|+\int_0^t \mathrm{sgn}(X_s-a)\,dX_s+L_t^a,\qquad L_t^a=\lim_{\varepsilon\downarrow0}\frac{1}{2\varepsilon}\int_0^t\mathbf{1}_{\{|X_s-a|<\varepsilon\}}\,d\langle X\rangle_s.$$
重要性：Tanaka 公式是「凸函数的 Itô 公式」，把 $C^2$ 的 Itô 公式推广到凸 $f$（$f''$ 退化为测度 $f''(da)\,dL_t^a$）。局部时是 Ch 9 excursion、Ch 10 Ray-Knight、Ch 11 位势论的核心工具。

**自测**：用 Tanaka 公式证明：$W_t^+=\frac12(W_t+|W_t|)=\int_0^t\mathbf{1}_{\{W_s>0\}}\,dW_s+\frac12 L_t^0$（正部分解）。这给出「BM 正部 = 局部鞅 + 局部时半份」，是反射原理的鞅论版本。

**局部时四性质速查**（BM $W$ 的 $L_t^a$）：

| 性质 | 陈述 | 几何直觉 |
|------|------|----------|
| 时间连续增 | 固定 $a$，$L_t^a$ 关于 $t$ 连续不减 | 「在 $a$ 处累积逗留」 |
| 空间 $1/2$-Hölder | 固定 $t$，$a\mapsto L_t^a$ 连续但 Hausdorff 维数 $1/2$ | 「空间方向比时间粗糙」 |
| Occupation 公式 | $\int_0^t f(W_s)\,ds=\int f(a)L_t^a\,da$ | 「时间积分 = 局部时加权的空间积分」 |
| 逆局部时跳跃 | $L_t^0$ 的逆 $\tau_l=\inf\{t:L_t^0>l\}$ 的跳跃是 i.i.d. | Ch 9 excursion 的 Poisson 时钟来源 |

> 记忆口诀：局部时「时间光滑、空间粗糙」——这正是 BM 路径「时间连续、空间不可导」的对偶。Ray-Knight（Ch 10）正是利用这种对偶，把「粗糙的空间过程」翻译为「光滑的 BESQ」。

---

## 第 9 章 · Excursion Theory（Excursion 理论：Itô 律）⭐⭐

**核心**：**本书最抽象也最美的专题章**。Excursion 理论刻画连续半鞅「离开某水平后的片段集合」。对 BM 在 $0$ 处的 excursion：每次 $W$ 离开 $0$（从 $0$ 出发、回到 $0$）的一个「片段」$e$ 是 $(0,\infty)$ 上连续、起点终点为 $0$ 的过程。**Itô 测度** $n$ 是 excursion 空间上的 $\sigma$-有限测度，使「按局部时 $L_t^0$ 索引的 excursion 点过程」是 Poisson 点过程（强度 $n$）。这把「BM 离开 $0$ 的复杂行为」化为「Poisson 过程 + i.i.d. 片段」——极其优雅。**Lévy 描述定理**：BM 的零集 $\{t:W_t=0\}$ 是闭、无孤立点、Lebesgue 测度零的「完美集」（Cantor 集式的分形结构）。Excursion 理论是 Markov 过程现代理论的支柱，也是分支过程、Lévy 过程的通用工具。

**飞腾锚点**：🟡 TLB 4.81× [E04] —— excursion 理论的核心是「按局部时 $L_t^0$（而非物理时间 $t$）索引片段」。局部时作为「信息时钟」把 BM 的零集分层管理：每个 excursion 是一个「页」，局部时是「页索引」，Itô 测度 $n$ 是「页的分布」。这与 TLB 多级页表「物理地址 vs 虚拟地址」的双层索引同构——命中率 4.81× 对应把「常用 excursion 长度」预先缓存，正如 BM 的零集虽 Lebesgue 测度零却「按局部时密集填充」。

**关键定理**（Itô excursion 律）：BM 的 excursion 按 $L_t^0$ 索引构成参数集 $\mathbb{R}_+$ 上的 Poisson 点过程，强度测度为 Itô 测度 $n$。$n$ 在「符号」（正/负 excursion）上对称，$n$-测度下 excursion 长度 $\zeta$ 满足 $n(\zeta>\varepsilon)=1/\sqrt{2\pi\varepsilon}$。重要性：这把「BM 离开 $0$」化为可计算的 Poisson 模型，是 Williams 分解、Ray-Knight 定理（Ch 10）、Markov 过程重生点的理论基础。

**自测**：用 Itô 律证明：BM 在 $[0,t]$ 上「最长正 excursion 长度」与「最长负 excursion 长度」的联合分布可由 Poisson 极值分布给出。（提示：按 $L_t^0$ 索引，正/负 excursion 长度是两个独立 Poisson 过程的极大值。）

**Excursion 理论三关键速查**（务必内化，Ch 9–10 反复使用）：

| 对象 | 定义 | 关键性质 |
|------|------|----------|
| **Itô 测度 $n$** | excursion 空间上的 $\sigma$-有限测度 | $n(\text{正 excursion})=n(\text{负 excursion})=\frac12 n$（对称） |
| **Poisson 点过程** | 按 $L^0$ 索引的 excursion 集合 | 强度 $n$；长度 $\zeta$ 满足 $n(\zeta>\varepsilon)=1/\sqrt{2\pi\varepsilon}$ |
| **BM 零集 $\{W=0\}$** | BM 取值为 $0$ 的时刻集 | 闭、无孤立点、Lebesgue 测度零（Cantor 集式分形） |

> **直觉**：物理时间 $t$ 下，BM「一半时间在 $0$ 附近」但零集测度为零——这看似矛盾，正是 excursion 理论的魔力：零集虽「测度零」却「按局部时密集」，每个 $0$ 点都是两个 excursion 的接缝。Williams 分解、Markov 过程的重生点（regeneration）全建立在此结构上。

---

## 第 10 章 · Bessel Processes and Ray-Knight Theorems（Bessel 与 Ray-Knight）⭐⭐

**核心**：**本书另一独家深度专题**。**Bessel 过程** $R^{(\delta)}$ 是 $\delta$-维 Bessel 过程，满足 SDE $dR_t=\frac{\delta-1}{2R_t}\,dt+dW_t$，几何上是 $\delta$-维 BM 模的分布（$R_t=|\mathbf{B}_t^{(\delta)}|$）。$\delta=1$ 退化为反射 BM $|W|$，$\delta=2$ 是 2-维 BM 模（平面 BM 距原点），$\delta\geq2$ 不碰 $0$，$\delta<2$ 会碰 $0$。$\delta$ 不必整数——**BESQ($\delta$)（平方 Bessel）** $X_t=R_t^2$ 满足 $dX_t=\delta\,dt+2\sqrt{X_t}\,dW_t$，是「平方 BM 的自然推广」。**Ray-Knight 定理**给出局部时沿空间方向的分布：BM 的局部时 $(L_T^a)_{a\geq0}$（$T$ 为首达 $1$ 时刻）在 $a\in[0,1]$ 上是 BESQ(2)、在 $a\geq1$ 上是 BESQ(0)（从 $0$ 出发）——「时间上的局部时 = 空间上的 BESQ」。

**飞腾锚点**：🟡 Iron Law <2% [Lab00] —— Ray-Knight 定理是「时间-空间对偶」的深刻结果：BM 的局部时 $L_t^a$ 作为「时间过程」（固定 $a$，变 $t$）难以直接分析，但作为「空间过程」（固定 $T$，变 $a$）却是 BESQ——一个可显式求解的 Markov 过程。这种「换变量降复杂度」的策略正类比性能工程中「换坐标系降低 CPI 误差」——Ray-Knight 把「不可显式」化为「可显式」，误差控制从 $>2\%$ 降到 $<2\%$。

**关键定理**（Ray-Knight 定理）：$W$ BM，$T_1=\inf\{t:W_t=1\}$。则 $(L_{T_1}^a)_{0\leq a\leq 1}$ 是 BESQ(2) 过程（从 $0$ 出发），$(L_{T_1}^{1+a})_{a\geq0}$ 是 BESQ(0) 过程（从 $L_{T_1}^1$ 出发）。重要性：Ray-Knight 把「局部时的时间分布」翻译为「BESQ 的空间分布」，是研究 BM 几何、扩散过程可达性、Bougerol 恒等式的核心工具。第二 Ray-Knight 定理给出 $T_r=\inf\{t:L_t^0=r\}$ 时 $(L_{T_r}^a)_{a\in\mathbb{R}}$ 的 BESQ 描述。

**自测**：用 Ray-Knight 证明：$E[L_{T_1}^0]=1$。（提示：BESQ(2) 从 $0$ 出发，$E[X_a]=2a$，故 $E[L_{T_1}^0]=E[X_0]=0$？错——注意 $a=0$ 是边界，需用 occupation 公式 $\int_0^{T_1}f(W_s)ds=\int_0^1 f(a)L_{T_1}^a\,da$ 取 $f=1$ 得 $T_1=\int_0^1 L_{T_1}^a\,da$，再求期望。）

---

## 第 11 章 · Probabilistic Potential Theory（概率位势论）

**核心**：本章用 Brown 运动（更一般地，扩散过程）求解经典位势论问题。**Dirichlet 问题**：在区域 $D$ 边界 $\partial D$ 上给定函数 $g$，求 $D$ 内调和函数 $h$（$\Delta h=0$）使 $h|_{\partial D}=g$。概率解：$h(x)=E_x[g(W_{\tau_D})]$（$\tau_D$ 为 BM 首出 $D$ 时刻）——「调和函数 = BM 首出边界的期望」。**Newtonian/Coulomb 位势** $G(x,y)=E_x[\int_0^\infty \mathbf{1}_{\{W_s\in dy\}}ds]/dy$ 是 Green 函数，刻画 BM 在 $y$ 处的期望逗留密度。**容量**（capacity）度量「集被 BM 击中的难易」，是 Sobolev 嵌入、Hausdorff 维数的概率对应。本章把「分析位势论」概率化，是 PDE 与概率的桥梁。

**飞腾锚点**：🟢 UDOT 16.9× [E05] —— Green 函数 $G(x,y)=\int_0^\infty p_s(x,y)\,ds$（$p_s$ 为转移密度）是「沿时间的期望逗留积分」，本质是加权累加。Dirichlet 解 $h(x)=E_x[g(W_{\tau_D})]=\int_{\partial D}g(y)\,P_x(W_{\tau_D}\in dy)$ 是边界函数的加权积分。UDOT 无符号点积 16.9× 加速这类「Green 核 × 边界函数」的批量数值积分——位势论的数值实现（有限差分、Monte Carlo）核心负载就是大规模加权求和。

**关键定理**（Dirichlet 问题的概率解）：$D$ 有界正则区域，$g\in C(\partial D)$。则 $h(x)=E_x[g(W_{\tau_D})]$ 是 Dirichlet 问题的唯一有界解（$\Delta h=0$ 于 $D$ 内，$h|_{\partial D}=g$）。重要性：这把「解 PDE」化为「算 BM 首出的期望」，是 Feynman-Kac 公式、扩散过程遍历理论、机器学习中「用 SDE 求解 PDE」（如 score-based 生成模型中分数匹配对应反向热方程）的概率基础。

**自测**：$D=(0,1)$，$g(0)=0,g(1)=1$。求 Dirichlet 问题的解。（答：$h(x)=x$，因 $E_x[W_{\tau_D}]=x$——BM 从 $x$ 出发首出 $(0,1)$ 时击中 $1$ 的概率为 $x$。验证 $\Delta h=h''=0$。）

---

## 第 12 章 · The Skorokhod Embedding Problem（Skorokhod 嵌入问题）⭐

**核心**：**本书最具思想性的专题之一**。Skorokhod 嵌入问题：给定概率分布 $\mu$（均值 $0$、方差有限），找停时 $T$ 使 $W_T\sim\mu$ 且 $\{W_{t\wedge T}\}$ 是 UI 鞅（「公平嵌入」）。这是「把任意分布嵌入 BM」的深刻问题，是 Brown 运动「通用性」的极致体现。**Dubins 嵌入**（用凸函数构造）、**Azéma-Yor 嵌入**（用停时 $T_{H}=\inf\{t:W_t\leq H(\sup_{s\leq t}W_s)\}$，$H$ 为分位函数）是两种经典解。Skorokhod 嵌入是「证明 CLT、构造渐近最优停时、鞅论 Hardy-Littlewood 不等式」的统一工具，也是金融中美式期权最优执行的理论基础。

**飞腾锚点**：🟡 FP16 3.81× [L01] —— Skorokhod 嵌入的数值实现需精确计算分布 $\mu$ 的分位数与停时判定。重尾分布（如 Cauchy、稳定分布）的分位数在 FP16（3.81× 加速但精度低、动态范围窄）下误差大，影响嵌入的正确性——「停时 $T$ 是否在正确时刻触发」对数值精度敏感。模拟嵌入时需在「精度（FP64，准确捕获分位数）」与「速度（FP16，快速长链）」间权衡，这正是「分布嵌入」对数值实现的硬约束。

**关键定理**（Azéma-Yor 嵌入）：$\mu$ 均值 $0$、方差有限。令 $H(x)=E_\mu[X|X\geq x]$ 的广义逆，$T=\inf\{t:W_t\leq H^{-1}(\sup_{s\leq t}W_s)\}$。则 $W_T\sim\mu$ 且 $\{W_{t\wedge T}\}$ UI 鞅。重要性：Azéma-Yor 嵌入是「渐近最优」的（在所有嵌入中 $E[T]$ 最小之一），是 Brown 桥、户田分解、美式期权最优执行的理论核心。

**自测**：$\mu=\frac12(\delta_{-1}+\delta_{+1})$（$\pm1$ 等概率）。找一个停时 $T$ 使 $W_T\sim\mu$。（答：$T=T_1\wedge T_{-1}$，即首达 $\pm1$ 时刻。验证 $P(W_T=1)=1/2$，UI 性由有界停时保证。）

---

## 第 13 章 · Asymptotic Results（渐近结果）

**核心**：本章汇集 BM 与半鞅的渐近定理。**重对数律（LIL）**：$\limsup_{t\to\infty}\frac{W_t}{\sqrt{2t\log\log t}}=1$ a.s.——BM 的「长期波动幅度」精确为 $\sqrt{2t\log\log t}$。**Chung 重对数律**：$\liminf_{t\to\infty}\sqrt{\frac{8\log\log t}{\pi^2 t}}\sup_{s\leq t}|W_s|=1$——BM 「最大游走」的下界。**Strassen 泛函重对数律**：$\frac{W_{nt}}{\sqrt{2n\log\log n}}$ 的轨道在 $C[0,1]$ 中以 a.s. 紧集 $\{f:\int(f')^2\leq 1\}$ 为极限点集——LIL 的泛函升级。本章还给出局部时的渐近、不变原理（Donsker）、强逼近（KMT 近似 BM 为随机游走）。这些是「长期行为」的精确刻画，是统计推断、Monte Carlo 收敛速度的理论基础。

**飞腾锚点**：🟡 GEMM 9.45 GFLOPS [Lab05] —— LIL 的数值验证需大规模长链 BM 模拟（$t\sim10^6$），计算 $\sup_{s\leq t}W_s/\sqrt{2t\log\log t}$ 的收敛。Strassen 泛函 LIL 更需在 $C[0,1]$ 上构造轨道簇，是大规模样本路径模拟的典型负载。GEMM 9.45 GFLOPS 的吞吐服务于「百万级 BM 路径的批量生成与极值计算」——渐近结果的数值验证本质是「大样本统计」，底层矩阵吞吐决定可验证的 $t$ 上限。

**关键定理**（重对数律 LIL）：$W$ BM，则
$$\limsup_{t\to\infty}\frac{W_t}{\sqrt{2t\log\log t}}=1,\qquad \liminf_{t\to\infty}\frac{W_t}{\sqrt{2t\log\log t}}=-1\quad\text{a.s.}$$
重要性：LIL 是 BM「长期波动」的精确渐近，比 SLLN（$\bar X_n\to0$）精细——它给出波动的「振幅」而非「趋势」。LIL 是 Monte Carlo 收敛速度、强逼近（KMT）、自适应算法步长设计的理论依据。

**自测**：用 LIL 估计：$t=10^6$ 时 $W_t$ 的典型波动幅度。（答：$\sqrt{2\times10^6\log\log 10^6}\approx\sqrt{2\times10^6\times2.6}\approx2280$。）再问：$W_t/t\to0$（SLLN）但 $W_t/\sqrt{t}\not\to0$（LIL 给出 $\limsup=\infty$），这矛盾吗？（不矛盾：SLLN 是「趋势」，LIL 是「波动振幅」，二者尺度不同。）

---

## §9 全书思想主线

Revuz-Yor 用一条主线贯穿 13 章：**「连续局部鞅是换了时钟的 Brown 运动，而 Brown 运动的全部深刻结构藏在它的局部时、excursion 与 Bessel 几何里。」** 前半部（Ch 0–5）铺设语言与核心工具：Ch 0–3 复习测度、过程、停时、鞅（与 Williams/K&S 重叠，可略读对照）；Ch 4 用 Lévy 刻画定理把「Brown 性」内蕴化为「鞅 + 二次变差」，BDG 不等式把极大值与二次变差双向绑定；Ch 5 构造 Itô 积分、给出 Itô 公式（多出的 $\frac12 f''\,d\langle X\rangle$ 项），并以 DDS 定理把「一切连续局部鞅」归约为「Brown 运动 + 时间变换」——这是全书的思想枢纽。后半部（Ch 6–13）则是「解剖 Brown 运动」的纵深专题：Ch 6–7 给出可解（线性）与一般 SDE，Ch 8 Tanaka 公式引出局部时（凸函数的 Itô 公式），Ch 9 用 Itô excursion 律把「BM 离开 $0$」化为 Poisson 点过程，Ch 10 Ray-Knight 把局部时翻译为 BESQ，Ch 11 用 BM 解 Dirichlet 问题（概率位势论），Ch 12 Skorokhod 嵌入把「任意分布嵌入 BM」，Ch 13 LIL 给出长期渐近。这条主线比 Karatzas-Shreve（止于 SDE + 金融）走得更远：K&S 关心「构造积分、定价期权」，Revuz-Yor 关心「理解 Brown 运动的内蕴几何」——前者是工程师的随机分析，后者是研究者的随机过程。

**历史脉络**：本书的「连续鞅中心化」视角源于法国概率学派的长期积累。Lévy（1939, 1948）首先注意到 BM 的鞅性质；Itô（1944–1951）据此构造随机积分；Doob（1953）与 Meyer（1976, 1978）把鞅论系统化为「测度论 + 信息流」的框架；Dambis（1965）、Dubins-Schwarz（1965）独立证明「连续局部鞅 = 时间变换的 BM」；Itô（1970）、Maisonneuve（1975）建立 excursion 理论；Ray（1963）、Knight（1963）发现局部时的 BESQ 刻画；Azéma-Yor（1979）给出渐近最优 Skorokhod 嵌入。Revuz（1975 初版）与 Yor 合作的第二版（1991）、第三版（1999）把这些分散成果整合为一部「连续鞅百科」。Marc Yor 本人在 excursion 理论、Bessel 过程、局部时对偶上的贡献（Bougerol 恒等式、Pitman $2M-X$ 定理）是本书后半部的灵魂——读 Revuz-Yor 等于读 Yor 的研究世界观。

---

## §10 与本仓库其他笔记的交叉引用

**与仓库已读经典的对话**：
- **↔ Karatzas-Shreve《Brown 运动与随机计算》GTM113**：K&S 是「工程化随机分析」（Itô 积分 → SDE → Black-Scholes），Revuz-Yor 是「研究化随机过程」（局部时 → excursion → Bessel → Ray-Knight → Skorokhod）。二者 Ch 0–5 高度重叠，但 Revuz-Yor 的 Ch 8–13 几乎是 K&S 未触及的纵深。建议路径：K&S 打底（已读）→ Revuz-Yor 专题深化。Itô 公式在两书中表述一致，但 Revuz-Yor 把它推广为 Tanaka 公式（凸函数版），K&S 止于 $C^2$。
- **↔ Williams《概率与鞅》**：Williams 的离散鞅论（Ch 12–15）是 Revuz-Yor 连续鞅论的「离散原型」。Williams 的可选停时定理、UI 鞅收敛在 Revuz-Yor Ch 3 升级为连续时间版本；Williams 的倒向鞅 + Hewitt-Savage 在 Revuz-Yor Ch 1 复现。读 Williams 后读 Revuz-Yor，能看清「离散鞅 → 连续鞅 → 半鞅」的抽象阶梯。
- **↔ Shreve《随机分析金融 II》**：Shreve II 是「金融驱动的随机分析入门」（离散时间 → 连续时间 → Black-Scholes → 测度变换），工程友好但深度有限。Revuz-Yor 是 Shreve II 的「研究级纵深」——Shreve II 的 Girsanov 定理在 Revuz-Yor Ch 7 给出抽象框架，Shreve II 的局部时仅提及，Revuz-Yor Ch 8 系统展开。
- **↔ Feller《概率论》卷二**：Feller 卷二 Part I（概率测度 + 母函数）+ Part II（变差）是 Revuz-Yor Ch 0–2 的「直觉版前身」。Feller 用组合与母函数建立扩散直觉，Revuz-Yor 用 Itô 积分重写——Feller 第 XIV 章的扩散过程在 Revuz-Yor Ch 6–7 严格化。Feller 给手感，Revuz-Yor 给框架。
- **↔ Durrett《概率：理论与例子》**：Durrett 的鞅论（Ch 4–5）与 Revuz-Yor Ch 3 重叠，但 Durrett 是离散为主、连续为辅，Revuz-Yor 全程连续时间。Durrett 的 BDG（Ch 4 习题）在 Revuz-Yor Ch 4 完整证明。

**AI / 工程锚点**：
- 🟢 **Ch 4 Lévy 刻画 + Ch 5 Itô 公式 → Diffusion 生成模型（score-based SDE）**：Song-Ermon（2019）的反向 SDE $d\mathbf{x}=f(\mathbf{x},t)dt-g(t)^2\nabla_\mathbf{x}\log p_t(\mathbf{x})dt+g(t)d\bar{\mathbf{W}}$ 的合法性全靠 Itô 公式与反向 Itô 积分（Anderson 1982）。Revuz-Yor Ch 5 的 Itô 公式 + Ch 7 的 SDE 解理论是 score-based 模型的数学母体。
- 🟢 **Ch 7 SDE 解理论 → 连续时间强化学习**：连续时间 RL（如 Munos、Bauer-Doumert 的 diffusion-based policy）中，策略 $\pi$ 诱导的状态过程是 SDE 的解。Yamada-Watanabe 的强弱解对应「确定性策略 vs 随机策略」，Itô 流的微分同胚性保证「策略扰动 → 状态扰动」的 Lipschitz 连续。
- 🟢 **Ch 6 线性 SDE + Ch 8 局部时 → 金融高阶模型**：OU 过程（Vasicek 利率）、CIR 过程（$dX=(\kappa-\theta X)dt+\sigma\sqrt{X}dW$，平方 Bessel 的漂移变形）是利率衍生品定价的核心。局部时是美式期权最优执行边界（obstacle problem）的概率刻画。
- 🟢 **Ch 5 DDS 定理 + Ch 12 Skorokhod 嵌入 → 随机优化与方差减少**：DDS 定理把「任意连续局部鞅」化为 BM，使「鞅的最优停止」化为「BM 的最优停止」；Skorokhod 嵌入是「给定目标分布，设计停时」的通用工具，是 Monte Carlo 方差减少、最优实验设计的理论基础。
- 🟡 **Ch 13 LIL → 大数律与自适应步长**：LIL $\sqrt{2t\log\log t}$ 的精确渐近是 SGD 自适应步长（Adam、RMSProp 的「长期波动」估计）、Bandit 算法探索-利用平衡（UCB 的 $\sqrt{\log t/n}$ 项）的理论来源。

> **一句话总结**：Revuz-Yor 是「已经会用 Itô 积分、想理解 Brown 运动为什么这么深刻」的研究者必读。Williams 给离散鞅的优雅，Karatzas-Shreve 给连续鞅的工程，Revuz-Yor 给连续鞅的「灵魂解剖」——局部时、excursion、Bessel、Ray-Knight、Skorokhod，这些是随机过程研究的「内功心法」。

---

## 附：推荐精读顺序（每周 10–20h，约 14 周计划）

基于「与已读 K&S / Williams 重叠度」与「本书独家价值」划分三档：

**第一档 · 必精读（独家价值，约 9 周）**：
- **Ch 4 连续鞅与 BM**（2 周）——Lévy 刻画 + BDG 手推 10 题，这是全书方法论基石。
- **Ch 5 随机积分**（2 周）——Itô 公式 + DDS 定理，每节配 K&S 对照阅读，体会「换时钟」思想。
- **Ch 8 局部时**（2 周）——Tanaka 公式 + occupation 公式，手算 BM 局部时 $L_t^0$ 的 occupation 积分。
- **Ch 10 Bessel 与 Ray-Knight**（2 周）——BESQ 显式解 + 第一 Ray-Knight，理解「时间-空间对偶」。
- **Ch 12 Skorokhod 嵌入**（1 周）——Azéma-Yor 嵌入构造，体会「任意分布嵌入 BM」的思想冲击。

**第二档 · 选精读（专题深化，约 3 周）**：
- **Ch 9 Excursion 理论**（2 周）——最抽象，建议配合 Le Gall《Brown 运动、鞅与随机分析》或 Bertoin《Lévy 过程》的 excursion 章节辅助。
- **Ch 7 一般 SDE**（1 周）——Yamada-Watanabe 定理 + Itô 流微分同胚，重点抓「强弱解」区别。

**第三档 · 略读或回查（与 K&S 重叠，约 2 周）**：
- Ch 0–3、Ch 6、Ch 11、Ch 13——与 Williams / K&S / Feller 重叠度高，首读略读、二刷按专题回查。

> **关键提醒**：本书习题无答案且极难，不要执着于「全做」。建议每章选 3–5 道「计算型」习题（Itô 公式、Tanaka、Ray-Knight 分布），跳过「构造反例型」难题。Python 验证：用 `numpy` + Euler-Maruyama 模拟 BM 路径，数值验证 $L_t^0=\lim_{\varepsilon\to0}\frac{1}{2\varepsilon}\int\mathbf{1}_{|W_s|<\varepsilon}ds$ 的 occupation 极限，是内化局部时的最佳方式。
