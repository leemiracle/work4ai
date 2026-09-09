# 图鉴 · 卷5（P · Q）

> 131 条（P 87 + Q 44）· 2026-09-06 快照自 [complexityzoo.net](https://complexityzoo.net/)。体例见[卷1](卷1-符号与A至B.md)。P 区按 span id 字母序（k-PBP 打头）。

---

## P（87 条）

### k-PBP — Polynomial-Size Width-k Branching Program
多项式大小、宽度 k 的分支程序（分层、每层 ≤k 顶点）。**k≥5 常数时 k-PBP = NC¹**（Barrington 定理 Bar89）；4-PBP ⊆ ACC⁰（BT88）。含于 k-EQBP 与 PBP。
- 主题章 [03-电路类](../03-电路类.md)（Barrington 奇迹） · [原文](https://complexityzoo.net/Complexity_Zoo:P#kpbp)

### P — Polynomial-Time
"开天辟地的那个类"（原页语）。图灵机多项式时间可解的判定问题（Edm65/Cob64/Rab60）。含线性规划（Kha79）、一般图最大匹配（Edm65）、素性检测（AKS02——无条件改进了依赖广义黎曼猜想的 Mil76）。P-完全问题典范：电路求值（归约限 L）。重要子类 L/NL/NC/SC；P ⊆ NP；= FO(LFP) = SO(Horn)；= 对数空间一致多项式电路；logspace 验证者的 IP 也可算 P（GKR15）。
- 主题章 [01-时间类](../01-时间类.md)（主角） · [原文](https://complexityzoo.net/Complexity_Zoo:P#p)

### PAC⁰ — Probabilistic AC⁰
（原页玩笑：计算复杂度研究的"政治行动委员会"。）DiffAC⁰ 函数 f 满足 yes ⇔ f(x)>0。logspace 一致下 = TC⁰ = C_=AC⁰（ABL98）。
- [原文](https://complexityzoo.net/Complexity_Zoo:P#pac0)

### para- — Parameterized Complexity（前缀）
para-C：存在可算 π(k) 使 (Q,k)∈para-L ⟺ (Q,π(k))∈L 的参数化版。para-P 即 FPT（命名公约的违例者）；para-L = DSPACE(f(k)+log n)。
- 主题章 [06-参数化与优化](../06-参数化与优化.md) · [原文](https://complexityzoo.net/Complexity_Zoo:P#para)

### para-L — Parameterized Logspace
DSPACE(f(k)+log n)。参数化顶点覆盖对其完全（Elberfeld et al. 2012）。
- [原文](https://complexityzoo.net/Complexity_Zoo:P#paral)

### para-NL — Parameterized Nondeterministic Logspace
NDSPACE(f(k)+log n)。自然完全问题未知（对比 para-NL[f log] 有很多）。
- [原文](https://complexityzoo.net/Complexity_Zoo:P#paranl)

### para-NL[f log] — Parameterized NL, O(f(k) log n) 分支数
参数化距离问题（有向图长 ≤k 的路径）完全（Elberfeld et al. 2012）。含于 XL。
- [原文](https://complexityzoo.net/Complexity_Zoo:P#paranlflog)

### para-P — Parameterized Polynomial time
FPT 的不常用别名（与其他 para- 类对齐）。逐片对应 XP。
- [原文](https://complexityzoo.net/Complexity_Zoo:P#parap)

### PBP — Polynomial-Size Branching Program
不限宽的多项式大小分支程序。**= L/poly**（Cob66）。含 P-OBDD 与 BP_d(P)。
- 主题章 [03-电路类](../03-电路类.md) · [原文](https://complexityzoo.net/Complexity_Zoo:P#pbp)

### P_C — Polynomial-Time Over The Complex Numbers
复数域图灵机版 P（BCS+97）。
- [原文](https://complexityzoo.net/Complexity_Zoo:P#pc)

### P^cc — Communication Complexity P
Alice/Bob 通信 polylog(n) 位可算的（函数族）类（BFS86）。EQUALITY 使其严格小于 BPP^cc、≠ NP^cc；total 函数版 P^cc = NP^cc ∩ coNP^cc = UP^cc。
- [原文](https://complexityzoo.net/Complexity_Zoo:P#pcc)

### PCD(r(n),q(n)) — Probabilistically Checkable Debate
两位辩手交替写辩论带、验证者随机抽查的证明系统（CFL+93）。**PCD(log n, 1) = PSPACE**——被用于证某些问题连近似都 PSPACE-难。含于 GPCD。
- [原文](https://complexityzoo.net/Complexity_Zoo:P#pcd)

### P-Close — Problems Close to P
多项式时间算法只在与答案不符的稀疏实例集上出错的问题（Yes83）。含 Almost-P；含于 P/poly（Sch86）。
- [原文](https://complexityzoo.net/Complexity_Zoo:P#pclose)

### PCP(r(n),q(n)) — Probabilistically Checkable Proof
概率可查证明：验证者掷 O(r(n)) 随机币、只查 O(q(n)) 位证明（AS98）。**PCP 定理：NP = PCP(O(log n), O(1))——证明可常数位随机抽查**；PCP(poly,poly) = NEXP；PCP(0,0)=P、PCP(0,poly)=coNP、PCP(log,0)=NP（For94）。
- 主题章 [05-交互证明与计数](../05-交互证明与计数.md)（主角） · [原文](https://complexityzoo.net/Complexity_Zoo:P#pcp)

### P_CTC — P With Closed Timelike Curves
可访问闭合类时曲线比特的 P。**= PSPACE**（Aar05c）。
- [原文](https://complexityzoo.net/Complexity_Zoo:P#pctc)

### PDQP — Product Dynamical Quantum Polynomial time
允许不塌缩测量的 BQP 推广（ABFL14；多半物理不可实现）。含 SZK（故含图同构）；无序搜索快于 BQP；oracle 下 ≠ BQP 且可不含 NP。
- [原文](https://complexityzoo.net/Complexity_Zoo:P#pdqp)

### PermUP — Self-Permuting UP
输入到唯一证据的映射是置换的 UP（HT03）。其对一一归约的闭包 = UP；PermUP = UP ⇒ E = UE。
- [原文](https://complexityzoo.net/Complexity_Zoo:P#permup)

### PEXP — Probabilistic Exponential-Time
EXP 的 PP 版。不含于 P/poly（BFT98）。
- [原文](https://complexityzoo.net/Complexity_Zoo:P#pexp)

### PF — Alternate Name for FP
FP 的别名条目。
- [原文](https://complexityzoo.net/Complexity_Zoo:P#pf)

### PFCHK(t(n)) — Proof-Checker
带无限长证明串 oracle 的 O(t(n)) 时间非确定机（yes：存在证明使全路径接受）（For94）。
- [原文](https://complexityzoo.net/Complexity_Zoo:P#pfchk)

### PH — Polynomial-Time Hierarchy
多项式层谱：Δ_i/Σ_i/Π_i 以 P、NP、coNP 叠 oracle 定义，或等价地由交替量词 ∃y∀z∃w… 定义。Σ_kP 有典范完全问题（Σ_k-SAT）；**若 PH 任一层塌缩则整体塌到该层**；PH ⊆ P^#P（Toda）、⊆ IP；= 二阶逻辑 SO 查询；= 指数处理器常数时间的并行 RAM（Imm89）。
- 主题章 [01-时间类](../01-时间类.md)（主角） · [原文](https://complexityzoo.net/Complexity_Zoo:P#ph)

### PH^cc — Communication Complexity PH
通信版 PH（BFS86）。BPP^cc ⊆ Σ₂^cc ∩ Π₂^cc；Σ₂^cc =? Π₂^cc 未知。
- [原文](https://complexityzoo.net/Complexity_Zoo:P#phcc)

### Φ₂P — 对称层级第二层（另定义）
∀y∃z 与 ∀z∃y 双向都成立的谓词类（Can96）。= S₂P。
- [原文](https://complexityzoo.net/Complexity_Zoo:P#phi2p)

### PhP — Physical Polynomial-Time
Valiant 定义"物理世界实践中可造的多项式资源计算机"（Val03）。含 P 与 BPP；是否含 BQP 开放（无不容置疑的可扩展量子计算演示）——原页：动物园管理员反而更不愿把 DTIME(n^1000) 收进 PhP 而不是 BQTIME(n²)。
- 主题章 [00-复杂度动物园地图](../00-复杂度动物园地图.md)（类 = 物理契约的反思） · [原文](https://complexityzoo.net/Complexity_Zoo:P#php)

### Π₂P — coNP With NP Oracle
Σ₂P 的补，PH 第二层。Π₂P ∩ Σ₂P 中有无法用 n^k 大小电路解决的问题（任意固定 k，Kan82）。
- 主题章 [01-时间类](../01-时间类.md) · [原文](https://complexityzoo.net/Complexity_Zoo:P#pi2p)

### PINC — Incremental Polynomial-Time
第 k 个输出位在 poly(n,k) 时间内可算的函数类（JY88）。严格含于 PIO。
- [原文](https://complexityzoo.net/Complexity_Zoo:P#pinc)

### PIO — Polynomial Input Output
时间 poly(n,m) 可算的（输出可指数长的）函数类（Yan81）。允许讨论"输出写不完"时的高效可计算性。
- [原文](https://complexityzoo.net/Complexity_Zoo:P#pio)

### P^K — P With Kolmogorov-Complexity Oracle
带最短程序长度 oracle 的 P（ABK+02 类似定义）。**含 PSPACE**；是否含全部 R 或任何 PSPACE 外的递归问题未知。
- 主题章 [00-复杂度动物园地图](../00-复杂度动物园地图.md)（Kolmogorov 桥） · [原文](https://complexityzoo.net/Complexity_Zoo:P#pk)

### PKC — Perfect Knowledge Complexity
PZK 的知识复杂度版（GP91）。
- [原文](https://complexityzoo.net/Complexity_Zoo:P#pkc)

### P_k^cc — P^cc in NOF model, k players
k 人额上数（number-on-forehead）确定性 polylog 通信版。平凡含于各随机/非确定版。
- [原文](https://complexityzoo.net/Complexity_Zoo:P#pkcc)

### PL — Probabilistic L
对 L 如 PP 对 P（无界误差随机对数空间）。含 BPL；含于 DET（Coo85）；PL^PL = PL。
- 主题章 [02-空间类](../02-空间类.md) · [原文](https://complexityzoo.net/Complexity_Zoo:P#pl)

### PL₁ — Polynomially-Bounded L₁ Spectral Norm
傅里叶系数绝对值之和多项式有界的布尔函数类（BS90）。严格含于 PT₁。
- [原文](https://complexityzoo.net/Complexity_Zoo:P#pl1)

### PLF — Polynomial Leaf
（原页：管理员相信就是 PPA。）Pap90 定义。
- [原文](https://complexityzoo.net/Complexity_Zoo:P#plf)

### PL_∞ — Polynomially-Bounded L_∞⁻¹ Spectral Norm
最小非零傅里叶系数倒数多项式有界的函数类（BS90）。严格含 PT₁。
- [原文](https://complexityzoo.net/Complexity_Zoo:P#plinfinity)

### PLL — Polynomial Local Lemma
由 Lovász 局部引理保证有解的 TFNP 子类（Pap94b）。
- [原文](https://complexityzoo.net/Complexity_Zoo:P#pll)

### P-LOCAL — LOCAL 模型 polylog 轮
n 点图上分布式 LOCAL 模型 poly(log n) 轮可解的局部可查问题（确定性）。**P-LOCAL = P-RLOCAL**（RG20——去随机化在分布式世界成立）。
- [原文](https://complexityzoo.net/Complexity_Zoo:P#plocal)

### P/log — P With Logarithmic Advice
O(log n) 建议版 P。严格含于 IC[log,poly]；NP ⊆ P/log ⇒ P = NP。
- [原文](https://complexityzoo.net/Complexity_Zoo:P#plog)

### PLS — Polynomial Local Search
由"有限 DAG 必有汇点"保证有解的 TFNP 子类（Pap94b）：给解算代价、给更优邻居，求局部最优。oracle 下与 PPA/PPP 互不包含；FBQP ⊄ PLS 有 oracle 证据（Aar03）；CT07 猜想 PPAD ∈ P ⇒ PLS ∈ P。
- 主题章 [06-参数化与优化](../06-参数化与优化.md)（局部搜索的复杂度化身） · [原文](https://complexityzoo.net/Complexity_Zoo:P#pls)

### P^NP — P With Oracle Access To NP
即 Δ₂P。
- [原文](https://complexityzoo.net/Complexity_Zoo:P#pnp)

### P^NPcc — Communication Complexity P^NP
通信版。⊄ PP^cc（BVW07）；partial 函数下不含 BPP^cc（PPS14）。
- [原文](https://complexityzoo.net/Complexity_Zoo:P#pnpcc)

### P^NP[k] — P With k NP Queries（常数 k）
= P 带 2^k−1 次并行（非自适应）NP 询问（BH91/Hem89）。P^NP[1] = P^NP[2] ⇒ PH 塌到 Δ₃P（Kadin）。
- 主题章 [01-时间类](../01-时间类.md) · [原文](https://complexityzoo.net/Complexity_Zoo:P#pnpk)

### P^NP[log] — P With Log NP Queries
O(log n) 次 NP 询问（= Θ₂P = P^||NP，BH91/Hem89）。含于 PP（BHW89）；**1876 年 Charles Dodgson（路易斯·卡罗）提出的选举制胜者判定对其完全**（HHR97）。
- 主题章 [01-时间类](../01-时间类.md) · [原文](https://complexityzoo.net/Complexity_Zoo:P#pnplog)

### P^NP[log^2] — P With Log² NP Queries
log² 次询问版。某时序逻辑的模型检测对其完全（Sch03）；log^k 自适应 = log^{k-1} 轮非自适应（CS92）。
- [原文](https://complexityzoo.net/Complexity_Zoo:P#pnplog2)

### P-OBDD — Polynomial-Size Ordered Binary Decision Diagram
变量序固定的多项式大小 OBDD。含于 PBP 与 BPP-OBDD。
- 主题章 [03-电路类](../03-电路类.md) · [原文](https://complexityzoo.net/Complexity_Zoo:P#pobdd)

### PODN — Polynomial Odd Degree Node
由"有限图奇度点必偶数个"保证的 TFNP 子类。= PPA（Pap90）。
- [原文](https://complexityzoo.net/Complexity_Zoo:P#podn)

### polyL — Polylogarithmic Space
DSPACE((log n)^c)。与 P 的包含关系三个都未知，但 **polyL ≠ P**（polyL 在 logspace 多一归约下无完全问题）。
- 主题章 [02-空间类](../02-空间类.md) · [原文](https://complexityzoo.net/Complexity_Zoo:P#polyl)

### PostBPP — BPP With Postselection
BPP_path 的别名。
- [原文](https://complexityzoo.net/Complexity_Zoo:P#postbpp)

### PostBPP^cc — Communication Complexity PostBPP
可 abort（非 abort 概率 ≥α）的随机协议，代价含 log(1/α)。真含于 PP^cc（Kla03）；度量 = 扩展差异界（GL14）。
- [原文](https://complexityzoo.net/Complexity_Zoo:P#postbppcc)

### PostBQP — BQP With Postselection
"一次不行就再试"（原页谚语）——条件于第一量子比特测得 1 的 BQP（Aar05b）。**PostBQP = PP**——测量后选择把量子机抬到 PP，一步登天。
- 主题章 [04-随机与量子](../04-随机与量子.md)（主角定理） · [原文](https://complexityzoo.net/Complexity_Zoo:P#postbqp)

### PP — Probabilistic Polynomial-Time
无界误差概率类：yes ⇔ ≥1/2 路径接受（Gil77）。**对并、交封闭（BRS91，悬了 14 年的 open）**；P^PP[log] = PP、对多项式真值表归约封闭（FR96）；含 P^NP[log] 与 QMA、MA、QCMA 等；含 BQP（即量子多项式时间 ⊆ 一次计数）；PP 推广为 CH。存在 PP 语言连带量子建议的 n^k 量子电路都没有（Aar06/Yir24）。
- 主题章 [05-交互证明与计数](../05-交互证明与计数.md)（主角） · [原文](https://complexityzoo.net/Complexity_Zoo:P#pp)

### PPA — Polynomial Parity Argument
由"最大度 2 的图叶子数必偶"保证有解的 TFNP 子类（Pap94b）：给一片叶子找另一片。含 PPAD；oracle 下与 PLS/PPP 互不包含。
- 主题章 [06-参数化与优化](../06-参数化与优化.md)（TFNP 家族） · [原文](https://complexityzoo.net/Complexity_Zoo:P#ppa)

### PPAD — Polynomial Parity Argument (Directed)
有向版 PPA：给源找汇（Pap94b）。**NASH（纳什均衡计算）PPAD-完全**（DGP05 四人、DP05/CD05 三人）——博弈论与复杂度 2005 年的历史性握手；oracle 下 PPP ⊄ PPAD、PPAD ⊄ BQP（Li11）。
- 主题章 [06-参数化与优化](../06-参数化与优化.md)（⇄ 讲透博弈论） · [原文](https://complexityzoo.net/Complexity_Zoo:P#ppad)

### PPADS — Polynomial Parity Argument (Directed, Sink)
有向找汇版。含 PPAD；含于 PPP。
- [原文](https://complexityzoo.net/Complexity_Zoo:P#ppads)

### P^||NP — P With Parallel Queries To NP
= P^NP[log]（BH91/Hem89）。
- [原文](https://complexityzoo.net/Complexity_Zoo:P#pparnp)

### P^||QMA — P With Parallel Queries To QMA
非自适应多项式次 QMA 询问。= P^QMA[log]（GPY19）。
- [原文](https://complexityzoo.net/Complexity_Zoo:P#pparqma)

### PP^cc — Communication Complexity PP
通信代价 + log(1/偏差) 版 PP（BFS86）。真含于 UPP^cc（BVW07）；度量 = 差异界（Kla07）。
- [原文](https://complexityzoo.net/Complexity_Zoo:P#ppcc)

### P/poly — Nonuniform Polynomial-Time
多项式大小电路族（各长度电路可完全不同），等价地：多项式时间机 + 只依长度的可信建议串。**含 BPP（Adleman 去随机化 Adl78/KL82）**；NP ⊆ P/poly ⇒ PH 塌到 Σ₂P（Karp-Lipton）——"分离 P 与 NP 的一大努力方向"；自然证明障碍（RR97）禁止用自然方法把 NP 排出 P/poly（若 P/poly 内有足够硬的 PRG）；E 中测度 0（May94b）。
- 主题章 [03-电路类](../03-电路类.md)（主角） · [原文](https://complexityzoo.net/Complexity_Zoo:P#ppoly)

### PPP — Polynomial Pigeonhole Principle
由鸽笼原理保证有解的 TFNP 子类（Pap94b）：给把 n 位映 n 位的电路，找映到 0^n 的输入或一对撞像。含 PPADS；oracle 下与 PPA/PPAD/PLS 互不包含。
- [原文](https://complexityzoo.net/Complexity_Zoo:P#ppp)

### P^PP — P With PP Oracle
计数层级 CH 的一层；= P^#P（"留给游客的练习"——原页语）；含 PP^PH（Toda）。**Toda 定理推论：PH 中任何问题都可由一串 permanent 计算解决**。
- 主题章 [05-交互证明与计数](../05-交互证明与计数.md) · [原文](https://complexityzoo.net/Complexity_Zoo:P#ppp2)

### PP/poly — Nonuniform PP
含 BQP/qpoly（Aar04b）；PP/poly = P/poly ⇒ PP ⊆ P/poly（对任何语法定义的类都对）。
- [原文](https://complexityzoo.net/Complexity_Zoo:P#pppoly)

### PPSPACE — Probabilistic PSPACE
IPP 的公币版；亦可定义为概率 PSPACE。= PSPACE（Pap83）。
- [原文](https://complexityzoo.net/Complexity_Zoo:P#ppspace)

### P^QMA[log] — P With Log QMA Queries
O(log n) 次 QMA 询问（Amb14）。= P^||QMA（GPY19）；**局部哈密顿量基态的局部可观测量/局部关联估计对其完全**（Amb14/GY16；2D 与 1D 也完全 GPY19）；含于 PP。
- 主题章 [04-随机与量子](../04-随机与量子.md) · [原文](https://complexityzoo.net/Complexity_Zoo:P#pqmalog)

### PQP — Probabilistic Quantum Polynomial-Time
误差 <1/2（不要求有界远离）的量子多项式时间（Wat09）。**= PP = PP^BPP = PostBQP**。
- [原文](https://complexityzoo.net/Complexity_Zoo:P#pqp)

### PQUERY — PSPACE With Polynomial Queries
多项式空间 + 多项式次 oracle 询问。= PSPACE 但相对某些 oracle 不等于 PSPACE^A（Kur83）——当年被郑重其事地当作反对相信相对化结果的论据（原页 !!）。
- [原文](https://complexityzoo.net/Complexity_Zoo:P#pquery)

### PR — Primitive Recursive Functions
本原递归函数（加乘幂迭代塔……但不许对角化整个系列——1928 年 Ackermann 函数证明 PR ⊊ R）。等价：只许确定循环（次数先定）的理想化 ALGOL 程序。停机问题可被 PR 函数"枚举式"输出。严格含 ELEMENTARY。
- 主题章 [00-复杂度动物园地图](../00-复杂度动物园地图.md)（可计算性边界） · [原文](https://complexityzoo.net/Complexity_Zoo:P#pr)

### P_R — Polynomial-Time Over The Reals
实数域版 P（BCS+97）。
- [原文](https://complexityzoo.net/Complexity_Zoo:P#pr2)

### Pr_HSPACE(f(n)) — Unbounded-Error Halting Probabilistic f(n)-Space
PP 的空间版（全停机）。= PrSPACE(f)（Jun85）。
- [原文](https://complexityzoo.net/Complexity_Zoo:P#prhspace)

### P-RLOCAL — Randomized LOCAL, polylog 轮
随机化 LOCAL 模型 polylog 轮。= P-LOCAL（RG20）。
- [原文](https://complexityzoo.net/Complexity_Zoo:P#prlocal)

### PromiseBPP — Promise-Problem BPP
承诺问题版 BPP（BF99）。
- [原文](https://complexityzoo.net/Complexity_Zoo:P#promisebpp)

### PromiseBQP — Promise-Problem BQP
承诺版 BQP。若 PromiseBQP = PromiseP 则 BQP/mpoly = P/poly。
- [原文](https://complexityzoo.net/Complexity_Zoo:P#promisebqp)

### PromiseP — Promise-Problem P
P 机可解的承诺问题。
- [原文](https://complexityzoo.net/Complexity_Zoo:P#promisep)

### PromiseRP — Promise-Problem RP
承诺版 RP（BF99）；BPP ⊆ RP^PromiseRP[1]（一次询问！）。
- [原文](https://complexityzoo.net/Complexity_Zoo:P#promiserp)

### PromiseUP — Promise-Problem UP
承诺版 UP；VV86 主结果即 NP ⊆ RP^PromiseUP。
- [原文](https://complexityzoo.net/Complexity_Zoo:P#promiseup)

### PrSPACE(f(n)) — Unbounded-Error Probabilistic f(n)-Space
PP 的概率 1 停机空间版。⊆ DSPACE(f²)（BCP83）；= Pr_HSPACE(f)（Jun85）。
- [原文](https://complexityzoo.net/Complexity_Zoo:P#prspace)

### P-Sel — P-Selective Sets
给一 yes 一 no 两实例能多项式时间挑出 yes 的类（Sel79）。NP ⊆ P-Sel ⇒ P = NP；存在不可递归的 P-选择集。
- [原文](https://complexityzoo.net/Complexity_Zoo:P#psel)

### P^#P — P With #P Oracle
（原页：这个类太重要，值得单开条目。）含 PH（Toda）；含于 CH 与 PSPACE；= P^PP。
- 主题章 [05-交互证明与计数](../05-交互证明与计数.md)（Toda 定理主角） · [原文](https://complexityzoo.net/Complexity_Zoo:P#psharpp)

### P^#P[1] — P With Single #P Query
单次 #P 询问。含 PH 与 MP（进而 ModPH）（Tod89/GKR+95）。
- [原文](https://complexityzoo.net/Complexity_Zoo:P#psharpp1)

### PSK — Polynomial Sink
（原页："S 和 K 就代表这俩字母，别问。"）给入出度 ≤1 的有向图一个源、求一个汇。= PPADS（Pap90）。
- [原文](https://complexityzoo.net/Complexity_Zoo:P#psk)

### PSPACE — Polynomial-Space
多项式空间可解的判定问题。**= NPSPACE（Savitch）= AP（CKS81）= IP（Shamir）**= CZK（单向函数存在假设下，BGG+90）；典范完全问题 QBF；描述复杂度：FO(2^{n^{O(1)}})=FO(PFP)=SO(n^{O(1)})=SO(TC)。随机 oracle 下 PSPACE^A ⊋ IP^A 概率 1（CCG+94）——IP=PSPACE 不相对化。
- 主题章 [02-空间类](../02-空间类.md)（主角） · [原文](https://complexityzoo.net/Complexity_Zoo:P#pspace)

### PSPACE^cc — Communication Complexity PSPACE
按 PSPACE=AP 类比定义的公式版通信类（叶为矩形）。含 PH^cc。
- [原文](https://complexityzoo.net/Complexity_Zoo:P#pspacecc)

### PSPACE/poly — PSPACE With Polynomial Advice
含 QMA/qpoly（Aar06b）。
- [原文](https://complexityzoo.net/Complexity_Zoo:P#pspacepoly)

### PT₁ — Polynomial Threshold Functions
f(x)=sgn(p(x))、p 项数多项式有界的多项式阈值函数类（BS90）。严格含 PL₁、严格含于 PL_∞。
- 主题章 [03-电路类](../03-电路类.md)（TC⁰ 的函数面） · [原文](https://complexityzoo.net/Complexity_Zoo:P#pt1)

### PTAPE — Archaic for PSPACE
PSPACE 的古称条目。
- [原文](https://complexityzoo.net/Complexity_Zoo:P#ptape)

### PTAS — Polynomial-Time Approximation Scheme
任意 ε>0 有 poly 时间 (1+ε) 近似的 NPO 子类（指数可强依赖 ε）。含 FPTAS、含于 APX；欧氏平面 TSP 在 PTAS（Aro96）。
- 主题章 [06-参数化与优化](../06-参数化与优化.md) · [原文](https://complexityzoo.net/Complexity_Zoo:P#ptas)

### PT/WK(f(n),g(n)) — Parallel Time f(n) / Work g(n)
深度 ≤f(n)、大小 ≤g(n) 的电路类。∪_k PT/WK(log^k n, n^k) = NC——**并行时间与总功的权衡坐标**。
- [原文](https://complexityzoo.net/Complexity_Zoo:P#ptwk)

### PureSuperQMA — A pure-state analog of SuperQMA
见证为纯态、验证者可直接读多项式个可测量概率的 QMA 变体（KR24）。纯态边缘问题完全；QMA-难；含于 PSPACE 与 QMA(2)；**是否 = SuperQMA = QMA 竟未知**。
- [原文](https://complexityzoo.net/Complexity_Zoo:P#puresuperqma)

### PZK — Perfect Zero Knowledge
完美零知识：视图分布与可模拟分布**完全相同**（SZK 的加强）。含于 SZK；有 oracle 与 SZK/coPZK/NIPZK/coSBP 分离。
- 主题章 [05-交互证明与计数](../05-交互证明与计数.md) · [原文](https://complexityzoo.net/Complexity_Zoo:P#pzk)

---

## Q（44 条）

### Q — Quasi-Realtime Languages
多带非确定图灵机线性时间（乃至恰 n 步）可解的类（BG69）。含 GCSL。
- [原文](https://complexityzoo.net/Complexity_Zoo:Q#q)

### QAC⁰ — Quantum AC⁰
常数深度多项式大小量子电路（层 = 单比特门×Toffoli 或 C×CNOT）（Moo99）。含于 QAC_f⁰；**是否含经典 AC⁰ 竟不显然**（量子门扇出不再免费）。
- 主题章 [04-随机与量子](../04-随机与量子.md) · [原文](https://complexityzoo.net/Complexity_Zoo:Q#qac0)

### QAC⁰[m] — Quantum AC⁰[m]
加 Mod-m 门的 QAC⁰（Moo99）。
- [原文](https://complexityzoo.net/Complexity_Zoo:Q#qac0m)

### QACC⁰ — Quantum ACC⁰
任意 m 的 Mod 门都许的 QAC⁰（Moo99）。**= QAC⁰[p]（任一素数 p）**（GHP00）。
- [原文](https://complexityzoo.net/Complexity_Zoo:Q#qacc0)

### QAC_f⁰ — QAC⁰ With Fanout
加量子扇出门（一步 CNOT 到任意多目标）的 QAC⁰。= QAC⁰[2] = QACC⁰（Moo99）；= QNC_f⁰（Tak12）。
- [原文](https://complexityzoo.net/Complexity_Zoo:Q#qacwf0)

### QAM — Quantum AM
公币量子 AM：Arthur 发随机经典串、Merlin 回量子证书（MW05）。含 QMA；含于 QIP[2] 与 BP•PP。
- 主题章 [04-随机与量子](../04-随机与量子.md) · [原文](https://complexityzoo.net/Complexity_Zoo:Q#qam)

### QCFL — Quantum CFL
量子上下文无关语言（MC00）。≠ CFL。
- [原文](https://complexityzoo.net/Complexity_Zoo:Q#qcfl)

### QCMA — Quantum Classical MA
量子验证者 + **经典**证明（= 经典见证的 QMA 子类；Watrous 称 MQA）（AN02）。含 MA；含于 QMA；黑箱群非成员资格有多项式 QCMA 查询复杂度（AK06）；量子 oracle 分离 QCMA 与 QMA（经典 oracle 分离未知）；GROUND STATE CONNECTIVITY（基态空间有无能量势垒）QCMA-完全（GS15）。
- 主题章 [04-随机与量子](../04-随机与量子.md)（量子证明的经典面） · [原文](https://complexityzoo.net/Complexity_Zoo:Q#qcma)

### QCPH — Quantum Classical PH
证明全经典、验证者量子的 PH 推广（GSSSY18）。含于 P^PP^PP。
- [原文](https://complexityzoo.net/Complexity_Zoo:Q#qcph)

### QEPH — Entangled Quantum PH
证明者可纠缠早晚期证明的 QPH 变体（GY24）。塌缩到 QRG(1)——**多项式轮也只两层**（对比 PH 多项式轮 = PSPACE）。
- [原文](https://complexityzoo.net/Complexity_Zoo:Q#qeph)

### QH — Query Hierarchy Over NP
QH_k = P^NP[k]，QH 为其并。**QH = BH**（Wag88）——两个层级同生共死。
- [原文](https://complexityzoo.net/Complexity_Zoo:Q#qh)

### QIP — Quantum IP
量子交互证明：BQP 验证者、全能（但遵量子力学线性性）证明者、可交量子消息（Wat99）。QIP[k]=QIP[3]=QIP（k>3，KW00）；**QIP = IP = PSPACE（JJUW09）——单证明者交互证明量子零增益**。QIP(1) 即 QMA。
- 主题章 [04-随机与量子](../04-随机与量子.md)（主角） · [原文](https://complexityzoo.net/Complexity_Zoo:Q#qip)

### QIP[2] — 2-Message Quantum IP
两消息量子 IP。含 QSZK（Wat02）。
- [原文](https://complexityzoo.net/Complexity_Zoo:Q#qip2)

### QL — Quasi-Linear
多带确定图灵机 n(log n)^k 时间（Sch78）。
- [原文](https://complexityzoo.net/Complexity_Zoo:Q#ql)

### QMA — Quantum MA
一消息量子交互证明：BQP 验证者收量子态证明（Wat00）。= QIP(1)；群非成员资格在内（Wat00）；**局部哈密顿量问题 QMA-完全**（Kitaev——量子版 Cook-Levin）；含于 PP（进而 A₀PP，Vya03）；1D 粒子线基态能量逼近 QMA-完全（AGK07）。
- 主题章 [04-随机与量子](../04-随机与量子.md)（主角） · [原文](https://complexityzoo.net/Complexity_Zoo:Q#qma)

### QMA-plus — QMA With Super-Verifier
验证者可直接读测量概率（而非采样）的 QMA（AR03）。= QMA。
- [原文](https://complexityzoo.net/Complexity_Zoo:Q#qma-plus)

### QMA⁺ — QMA With Non-Negative Amplitudes
见证须为非负振幅态的 QMA（JW23）。**对 gap 敏感：某常数 gap 下 = QMA，另一常数 gap 下 = NEXP**（BFM23）——完备/可靠性之差竟藏着指数鸿沟。
- [原文](https://complexityzoo.net/Complexity_Zoo:Q#qma-plus-new)

### QMA₁ — One-Sided QMA
yes 时存在概率 1 接受态的 QMA（Bra06）。量子 k-SAT（k≥4）QMA₁-完全；量子 2-SAT 在 P；量子 3-SAT QMA₁-完全（GN13）。
- [原文](https://complexityzoo.net/Complexity_Zoo:Q#qma1)

### QMA(2) — Quantum MA With Two Unentangled Certificates
两份保证不纠缠的量子证书（KMY01）。QMA_log(2) 有 3-着色协议（完美完备、1−1/poly 可靠性，BT09）——QMA 单证书做这事会塌缩 NP ⊆ BQP；含于 NEXP（其后改进至 P^PP^PP，GSSSY18）；可分稀疏哈密顿量问题完全（CS12）。**QMA(2) vs QMA 是量子证明论的中央 open 之一**。
- 主题章 [04-随机与量子](../04-随机与量子.md) · [原文](https://complexityzoo.net/Complexity_Zoo:Q#qma2)

### QMA⁺(2) — QMA(2) With Non-Negative Amplitudes
两份非负振幅证书的 QMA(2)（JW23）——为证 QMA(2)=NEXP 而生。某 gap 下 = QMA(2)、另一 gap 下 = NEXP；截至 2025 仍 open。
- [原文](https://complexityzoo.net/Complexity_Zoo:Q#qma2-plus-new)

### QMA_log — QMA With Logarithmic-Size Proofs
O(log n) 量子比特证明的 QMA。**= BQP**（MW05）。
- [原文](https://complexityzoo.net/Complexity_Zoo:Q#qmalog)

### QMAM — Quantum Merlin-Arthur-Merlin
公币量子 MAM 协议（MW05）。QMAM = QIP(3) = QIP = PSPACE。
- [原文](https://complexityzoo.net/Complexity_Zoo:Q#qmam)

### QMA/qpoly — QMA With Polynomial-Size Quantum Advice
量子建议版 QMA。含于 PSPACE/poly（Aar06b）。
- [原文](https://complexityzoo.net/Complexity_Zoo:Q#qmaqpoly)

### QMIP — Quantum Multi-Prover Interactive Proofs
量子 MIP：消息与验证全量子、证明者共享无限先验纠缠（KM02）。**= MIP* = RE**（RUV12/JNVWY20）；含 NEXP。
- 主题章 [05-交互证明与计数](../05-交互证明与计数.md)（MIP*=RE 语境） · [原文](https://complexityzoo.net/Complexity_Zoo:Q#qmip)

### QMIP_le — QMIP With Limited Prior Entanglement
证明者只共享多项式对 EPR 的 QMIP。含于 NEXP（KM02）。
- [原文](https://complexityzoo.net/Complexity_Zoo:Q#qmiple)

### QMIP_ne — QMIP With No Prior Entanglement
无先验纠缠版。**= NEXP**（KM02）。
- [原文](https://complexityzoo.net/Complexity_Zoo:Q#qmipne)

### QNC — Quantum NC
polylog 深度有界误差量子电路（对 NC 如 BQP 对 P）。分解在 ZPP^QNC 中（CW00）；与 BPP 不可比较（已知）。
- 主题章 [04-随机与量子](../04-随机与量子.md)（量子并行谱系） · [原文](https://complexityzoo.net/Complexity_Zoo:Q#qnc)

### QNC⁰ — Quantum NC⁰
常数深度、无扇出的量子电路（Spa02）。含于 QNC_f⁰。
- [原文](https://complexityzoo.net/Complexity_Zoo:Q#qnc0)

### QNC⁰/🐱 — Quantum NC⁰ With Cat-State Advice
外加猫态 (|0^n⟩+|1^n⟩)/√2 作建议的 QNC⁰（WKST19）。含于 QNC⁰/qpoly 与 BQP——**常数深度 + 猫态 = 惊人的计算力**（动物园里最萌的条目）。
- 主题章 [04-随机与量子](../04-随机与量子.md) · [原文](https://complexityzoo.net/Complexity_Zoo:Q#qnc0cat)

### QNC⁰/qpoly — Quantum NC⁰ With Quantum Advice
多项式大小量子建议版 QNC⁰。含 QNC⁰ 与 QNC⁰/🐱。
- [原文](https://complexityzoo.net/Complexity_Zoo:Q#qnc0qpoly)

### QNC¹ — Quantum NC¹
对数深度 QNC。（原页自曝：本条曾错写成"精确版 QNC"，是编辑把 QMA₁/QCMA₁ 的下标习惯张冠李戴了。）与 ASV00 的单干净比特模拟关系不明。
- [原文](https://complexityzoo.net/Complexity_Zoo:Q#qnc1)

### QNC_f⁰ — Quantum NC⁰ With Unbounded Fanout
无界扇出量子电路（Spa02）。含 QNC⁰；含于 QACC⁰；= QAC_f⁰（Tak12）。
- [原文](https://complexityzoo.net/Complexity_Zoo:Q#qncf0)

### QP — Quasipolynomial-Time
DTIME(2^{polylog n})。
- [原文](https://complexityzoo.net/Complexity_Zoo:Q#qp)

### QPH — Quantum PH
证明为不纠缠混态、验证者量子的 PH 推广（GSSSY18）。含 QMA(2)、PH、QCPH；QΣ₂/QΣ₃ 分别含于 EXP/NEXP；QΣ₂=QΠ₂ 是否塌缩层级未知。
- [原文](https://complexityzoo.net/Complexity_Zoo:Q#qph)

### QPIP — Quantum Prover Interactive Proof
证明者为 BQP（非全能）的 IP，经典消息。= BQP（Mah18）；验证者带 k 量子比特的 QPIP_k：BQP = QPIP_c（某常数 c，ABOE08）——**让量子机证明自己的计算正确**。
- 主题章 [04-随机与量子](../04-随机与量子.md)（量子验证的实战面） · [原文](https://complexityzoo.net/Complexity_Zoo:Q#qpip)

### QPLIN — Linear Quasipolynomial-Time
DTIME(n^{O(log n)})。对 QP 如 E 对 EXP。
- [原文](https://complexityzoo.net/Complexity_Zoo:Q#qplin)

### QPSPACE — Quasipolynomial-Space
DSPACE(2^{polylog n})。不含于 Check（BG94 引 Beigel-Feigenbaum/Krawczyk）。
- [原文](https://complexityzoo.net/Complexity_Zoo:Q#qpspace)

### qq-QAM — quantum-quantum QAM
Arthur 发 EPR 对的 QAM（KGN19）。最大熵/最小迹距离估计完全；低能高纠缠态判定完全、自由能可加逼近可算（GK25）。
- [原文](https://complexityzoo.net/Complexity_Zoo:Q#qqqam)

### QRG — Quantum Refereed Games
量子裁判博弈（Gut05）。含于 EXP（GW07）⇒ **QRG = RG = EXP——零和量子博弈不比经典难**。
- [原文](https://complexityzoo.net/Complexity_Zoo:Q#qrg)

### QRG(1) — One-turn Quantum Refereed Games
无回传消息的量子裁判博弈（JW09）。含于 PSPACE；含 QMA 与 P^QRG(1)。
- [原文](https://complexityzoo.net/Complexity_Zoo:Q#qrg1)

### QRG(2) — Two-turn Quantum Refereed Games
双方各一问一答（并行）。**= RG(2) = PSPACE**（JW09）。
- [原文](https://complexityzoo.net/Complexity_Zoo:Q#qrg2)

### QRG(k) — k-turn Quantum Refereed Games
k 轮版；QRG(poly)=QRG。中间 k 所知甚少：QRG(k) =? RG(k) 都 open。
- [原文](https://complexityzoo.net/Complexity_Zoo:Q#qrgk)

### QRL — Quantum Regular Languages
Moore-Crutchfield 量子有限自动机（每符号酉变换、**只在最后测量**）正概率接受的语言（MC00）。与 NQL 的区别恰在测量时机。
- [原文](https://complexityzoo.net/Complexity_Zoo:Q#qrl)

### QSZK — Quantum Statistical Zero-Knowledge
量子统计零知识（Wat02）：Arthur 视图各步混态与可自备态迹距离 ≤1/10。含于 QIP(2)；诚实与一般验证者等价（Wat09b）；oracle 下不含 UP∩coUP。
- 主题章 [05-交互证明与计数](../05-交互证明与计数.md) · [原文](https://complexityzoo.net/Complexity_Zoo:Q#qszk)
