# 图鉴 · 卷1（符号区 + A + B）

> 100 条 · 2026-09-06 快照自 [complexityzoo.net](https://complexityzoo.net/)。
> 定义从原页 wikitext 蒸馏（口径见[总目](00-总目与口径.md)）；原文短则词条短，不注水。
> 「主题章」标记地标类（本系列 00–07 章展开讲）；其余类以本词条为家。

---

## 符号区（17 条）

### 0-1-NP_C — Binary Restriction of NP Over The Complex Numbers
复数域 NP 与 {0,1}*（二元串集合）的交。含 NP；含于 PSPACE；在扩展黎曼猜想下含于 AM。
- [原文](https://complexityzoo.net/Complexity_Zoo:Symbols#01npc)

### 1NAuxPDA^p — One-Way NAuxPDA^p
单向辅助下推自动机类。严格包含 CFL、严格含于 LOGCFL（Bra77）——即 CFL 在单向对数空间归约下的闭包。
- [原文](https://complexityzoo.net/Complexity_Zoo:Symbols#1nauxpdap)

### 2-EXP — Double-Exponential Time
即 EEXP（2^2^poly(n) 时间）。
- 主题章 [01-时间类](../01-时间类.md) · [原文](https://complexityzoo.net/Complexity_Zoo:Symbols#2exp)

### 3SUM-hard — Problems hard for 3SUM
3SUM（给定整数集，是否存在 a+b=c）可在亚二次时间归约到它的问题全体（实 RAM 模型）。计算几何大量问题属此（三点共线等）；较弱模型下有 Ω(n²) 下界。
- 主题章 [06-参数化与优化](../06-参数化与优化.md)（细粒度复杂度三巨头之一） · [原文](https://complexityzoo.net/Complexity_Zoo:Symbols#3sumhard)

### ⊕EXP — Parity EXP
⊕P 的指数时间类比。存在 oracle 使 ⊕EXP = ZPP（BBF98）。
- [原文](https://complexityzoo.net/Complexity_Zoo:Symbols#parityexp)

### ⊕L — Parity L
对 L 的关系如同 ⊕P 对 P：非确定对数空间机，接受路径数的奇偶性决定答案。含 SL（KW93）；解 Z₂ 上线性方程组对其完全（Dam90）；模拟稳定子电路对其完全（AG04）；⊕L^⊕L = ⊕L。
- [原文](https://complexityzoo.net/Complexity_Zoo:Symbols#parityl)

### ⊕L/poly — Nonuniform ⊕L
⊕L 的非一致版本（对 ⊕L 如 P/poly 对 P）。含 NL/poly（GW96）。
- [原文](https://complexityzoo.net/Complexity_Zoo:Symbols#paritylpoly)

### ⊕P — Parity P
NP 机接受路径数为奇 ⇔ yes。含 FewP（CH89）；图同构含于 ⊕P 且对 ⊕P low（AK02）；存在 oracle 使 P = ⊕P 但 P ≠ NP（甚至 NP = EXP）。
- 关键关系：⊕P = Mod_{2^m}P（任意正整数 m）；PH ⊆ P^⊕P（Toda 链的一环）
- 主题章 [05-交互证明与计数](../05-交互证明与计数.md) · [原文](https://complexityzoo.net/Complexity_Zoo:Symbols#parityp)

### ⊕P^cc — Communication Complexity ⊕P
⊕P 的通信复杂度版。Associated 度量 = 通信矩阵在 GF(2) 上秩的对数；不含于 UPP^cc（For02）。
- [原文](https://complexityzoo.net/Complexity_Zoo:Symbols#paritypcc)

### ⊕SAC^0 — AC^0 With Unbounded Parity Gates
（动物园原页无正文——定义见 ⊕SAC¹ 的深度常数版。）
- [原文](https://complexityzoo.net/Complexity_Zoo:Symbols#paritysac0)

### ⊕SAC^1 — AC^1 With Unbounded Parity Gates
多项式大小、多对数深度、无界扇入 XOR 门 + 有界扇入 AND 门的非一致电路族。含 SAC¹（GW96）。
- [原文](https://complexityzoo.net/Complexity_Zoo:Symbols#paritysac1)

### #AC^0 — Sharp-AC^0
常数深度、多项式大小算术电路（加法/乘法门、常数 0/1）可计算的 {0,1}^n → 非负整数函数类。含于 GapAC⁰。
- [原文](https://complexityzoo.net/Complexity_Zoo:Symbols#sharpac0)

### #GA — Sharp-GA（图自同构计数）
可 Karp 归约到"数一张图的自同构个数"的问题类。GA 的计数侧对应物。
- [原文](https://complexityzoo.net/Complexity_Zoo:Symbols#sharpga)

### #L — Sharp-L
对 L 如同 #P 对 P：数非确定对数空间机的接受路径。含于 DET 的函数版（AJ93）；行列式是 GapL 完全（GapL = 两个 #L 函数之差）。
- [原文](https://complexityzoo.net/Complexity_Zoo:Symbols#sharpl)

### #L/poly — Nonuniform #L
#L 的非一致版本。
- [原文](https://complexityzoo.net/Complexity_Zoo:Symbols#sharplpoly)

### #P — Sharp-P / Number-P
函数类：计算 NP 机的接受路径数。典范完全问题 #SAT；permanent（完美匹配计数）#P 完全（Val79）——**而其判定版在 P 里**，计数与判定在此分道扬镳。PH ⊆ P^#P，单次询问足矣（Tod89）。
- 主题章 [05-交互证明与计数](../05-交互证明与计数.md)（Toda 定理主角） · [原文](https://complexityzoo.net/Complexity_Zoo:Symbols#sharpp)

### #W[t] — Sharp-W[t]
参数化计数版 #P：固定参数 parsimonious 可归约到 #WSAT 的参数化计数问题。存在 #W[1] 完全问题其判定版在 FPT（FG02）——**计数可比判定严格难，即便在参数化世界**。#W[1] 完全：数图中定长路径/回路；#W[2] 完全：极大无弦路径（CF07）。
- 主题章 [06-参数化与优化](../06-参数化与优化.md) · [原文](https://complexityzoo.net/Complexity_Zoo:Symbols#sharpwt)

---

## A（40 条）

### A₀PP — One-Sided Analog of AWPP
SBP 的 GapP 版。含 QMA、AWPP、coC=P；含于 PP；若 A₀PP = PP 则 PH ⊆ PP。= SBQP（Kup09）。
- [原文](https://complexityzoo.net/Complexity_Zoo:A#a0pp)

### AC — Unbounded Fanin Polylogarithmic-Depth Circuits
AC^i = 多项式大小、深度 O(log^i n)、无界扇入 AND/OR/NOT 电路；AC 为其全体并。**AC = NC**；AC¹ 含 NL。随机 oracle 下 AC^i ⊊ AC^{i+1}、AC^A ⊊ P^A 概率 1（Mil92）。FO-uniform 深度 t 的 AC = FO[t]。
- 主题章 [03-电路类](../03-电路类.md) · [原文](https://complexityzoo.net/Complexity_Zoo:A#ac)

### AC⁰ — Unbounded Fanin Constant-Depth Circuits
常数深度无界扇入电路——**动物园里被研究得最透的类**。parity 与 majority 都不在 AC⁰ 里（FSS84）：常数深度数不清 n 个比特的奇偶。AC⁰ 内存在对 AC⁰ 统计测试伪随机的函数（NW94），但不存在对 QP 测试伪随机的（LMN93）。深度 k 均匀 AC⁰ 的完全问题：宽 k 网格图可达性（BLM+98）。
- 关键关系：AC⁰ ⊊ NC¹；等于一阶逻辑 FO；与交替对数时间层级对应
- 主题章 [03-电路类](../03-电路类.md)（parity 指数下界主战场） · [原文](https://complexityzoo.net/Complexity_Zoo:A#ac0)

### AC⁰[m] — AC⁰ With MOD m Gates
AC⁰ 加 MOD m 门。m 为素数幂 p^k 时，MOD_q ∉ AC⁰[m]（q 为异于 p 的素数，Raz87/Smo87），故 AC⁰[m] ⊊ NC¹；**m 为互异素数乘积（如 6）时，连 AC⁰[6] 与 NP 的关系都未知**。
- 主题章 [03-电路类](../03-电路类.md) · [原文](https://complexityzoo.net/Complexity_Zoo:A#ac0m)

### AC¹ — Unbounded Fanin Log-Depth Circuits
深度 O(log n) 的 AC 电路层。含 NL（故含 NC¹）；含于 NC²。DET 满足同样包含关系，但 AC¹ 与 DET 互不包含（已知）。
- [原文](https://complexityzoo.net/Complexity_Zoo:A#ac1)

### ACC⁰ — AC⁰ With Arbitrary MOD Gates
AC⁰ 加任意 MOD m 门。含于 TC⁰；可被拟多项式大小、深度 3 的阈值电路模拟（Yao90）。**已知仅有的两个非平凡下界**（Wil11）：NTIME[2^n] 无多项式大小非一致 ACC⁰ 电路，E^NP 无 2^{n^O(1)} 大小 ACC⁰ 电路。含 4-PBP。
- 主题章 [03-电路类](../03-电路类.md)（Williams 2010 突破主角） · [原文](https://complexityzoo.net/Complexity_Zoo:A#acc0)

### Ack — Ackermann Time
DTIME(F_ω(p(n)))（p 取遍本原递归函数；F_ω 为 Ackermann 阶增长）。改 NTIME/NSPACE 不变类。Petri 网可达性（Ler22）、向量加法系统（CO22）、带生成/销毁结点的机器人穿迷宫（Ani+23）在其下本原递归归约完全——**2022 年才驯服的"超多项式但本原递归"地带**。
- 主题章 [01-时间类](../01-时间类.md) · [原文](https://complexityzoo.net/Complexity_Zoo:A#ackermann)

### AH — Arithmetic Hierarchy
PH 在可计算性理论中的类比：Δᵢ/Σᵢ/Πᵢ 以 R、RE、coRE 为基逐层叠加 oracle 定义，也可由算术公式量词层数定义。**每一层严格包含下层**（可判定与可枚举的世界里层级定理无条件成立——对比 PH 的悬而未决）。
- 主题章 [01-时间类](../01-时间类.md)（PH 的可计算性镜像） · [原文](https://complexityzoo.net/Complexity_Zoo:A#ah)

### AL — Alternating L
多项式时间交替图灵机的对数空间版。**AL = P**（CKS81）——交替把空间换成了时间。
- 主题章 [02-空间类](../02-空间类.md) · [原文](https://complexityzoo.net/Complexity_Zoo:A#al)

### AlgP/poly — Polynomial-Size Algebraic Circuits
多项式大小代数电路（整数上 +、−、×、常数 ±1）可算的多重多项式（非一致）。若 BPP ⊆ NE，则或 NEXP ∉ P/poly、或矩阵 permanent 多项式 ∉ AlgP/poly（KI02）。
- [原文](https://complexityzoo.net/Complexity_Zoo:A#algppoly)

### ALL — The Class of All Languages
字面意义的"所有语言"。近期动物园的捣蛋鬼：PP/rpoly = ALL、PostBQP/qpoly = ALL、QIP/qpoly = ALL、IP(2)/rpoly = ALL、MA_EXP/rpoly = ALL、PDQP/qpoly = ALL（Aar04b/Raz05/Aar18）——**随机/量子建议串会让类爆炸到 ALL**，建议的威力没有经典直觉的上限。
- 主题章 [00-复杂度动物园地图](../00-复杂度动物园地图.md) · [原文](https://complexityzoo.net/Complexity_Zoo:A#all)

### Almost-NP — Languages Almost Surely in NP^A
对均匀随机 oracle A，以概率 1 落在 NP^A 的语言类。**= AM**（NW94）。
- [原文](https://complexityzoo.net/Complexity_Zoo:A#almostnp)

### Almost-P — Languages Almost Surely in P^A
同上取 P^A。**= BPP**（BG81）——随机 oracle 的透镜把随机性类照成了确定性类。
- 主题章 [04-随机与量子](../04-随机与量子.md) · [原文](https://complexityzoo.net/Complexity_Zoo:A#almostp)

### Almost-PSPACE — Languages Almost Surely in PSPACE^A
PSPACE 版。**不等于 PSPACE**（意外：PSPACE 已等于 BPPSPACE、PPSPACE，却保不住随机 oracle）= BP^exp⋅PSPACE ⊆ NEXP^NP ∩ coNEXP^NP（BVW98）。
- [原文](https://complexityzoo.net/Complexity_Zoo:A#almostpspace)

### ALOGTIME — Logarithmic Time Alternating RAM
随机存取交替图灵机的对数时间类。= U_{E*}-uniform NC¹。
- [原文](https://complexityzoo.net/Complexity_Zoo:A#alogtime)

### AM — Arthur-Merlin
Arthur（多项式时间随机验证者，**公开随机币**）出题、Merlin 作答的单轮博弈验证类。MA ⊆ AM ⊆ Π₂P；若 coNP ⊆ AM 则 PH 塌缩到 AM；在去随机化假设下 AM = NP。
- 关键关系：BP•NP = AM = Almost-NP
- 主题章 [05-交互证明与计数](../05-交互证明与计数.md) · [原文](https://complexityzoo.net/Complexity_Zoo:A#am)

### AM^cc — Communication Complexity AM
Alice+Bob 合体当 Arthur 的通信版。**找出一个不属于 AM^cc 的显式两方函数是 open 问题**；含于 PH^cc。
- [原文](https://complexityzoo.net/Complexity_Zoo:A#amcc)

### AM_EXP — Exponential-Time AM
指数时间 Arthur。含 MA_EXP；含于 EH（乃至 S₂-EXP•P^NP）；若 coNP ⊆ AM[polylog] 则 EH 塌到 AM_EXP（PV04）。
- [原文](https://complexityzoo.net/Complexity_Zoo:A#amexp)

### AM ∩ coAM — The intersection of AM and coAM
yes 与 no 都有 AM 协议。若 EXP 对 AM 协议也需指数时间，则 AM ∩ coAM = NP ∩ coNP（GST03）。**图同构在此类中**——"既有 yes 证明又有 no 证明"的问题带。
- [原文](https://complexityzoo.net/Complexity_Zoo:A#amicoam)

### AmpMP — Amplifiable MP
#P 函数 f(x,0^m) 的**中间位**为 1 ⇔ yes，且中间位两侧 m 位全 0。含 PH、ModPH；含于 MP。
- [原文](https://complexityzoo.net/Complexity_Zoo:A#ampmp)

### AM[polylog] — AM With Polylog Rounds
Arthur-Merlin 交互 polylog 轮。是否含于 PH 未知；若含 coNP 则 EH 塌缩（SS04）。
- [原文](https://complexityzoo.net/Complexity_Zoo:A#ampolylog)

### AmpP-BQP — BQP Restricted To AmpP States
每步量子态都指数接近 AmpP 态（振幅可由经典多项式电路计算）的 BQP。含于 PH 第三层（Aar03b）。
- [原文](https://complexityzoo.net/Complexity_Zoo:A#amppbqp)

### AP — Alternating P
交替图灵机（AND/OR 状态，接受 ⇔ 计算 AND-OR 树取值 1）多项式时间。**AP = PSPACE**（CKS81）——多项式层谱系的时间换空间总定理。
- 主题章 [02-空间类](../02-空间类.md)（交替 = 空间的等价形式） · [原文](https://complexityzoo.net/Complexity_Zoo:A#ap)

### APP — Amplified PP
GapP 函数比值可放大到 2^{-poly(n)} 精度的类（Li93）。含于 PP 且对 PP low；对交、并、补封闭；含 AWPP、FewP、YQP*、YMA*、YP*。
- [原文](https://complexityzoo.net/Complexity_Zoo:A#app)

### APSPACE — Alternating PSPACE
多项式空间交替机。**= EXP**（CKS81）。
- 主题章 [02-空间类](../02-空间类.md) · [原文](https://complexityzoo.net/Complexity_Zoo:A#apspace)

### APX — Approximable
NPO 中 admits 常数因子近似算法的问题。含 PTAS；等于 MaxSNP 与 MaxNP 在 PTAS 归约下的闭包（KMS+99/CT94）。
- 主题章 [06-参数化与优化](../06-参数化与优化.md)（PCP⇒APX 难度链落点） · [原文](https://complexityzoo.net/Complexity_Zoo:A#apx)

### ASPACE(f(n)) — Alternating SPACE
交替机 f(n) 空间。APSPACE = ASPACE(poly)，AL = ASPACE(log)；ASPACE(log f) = DTIME(poly f)（CKS81）。
- [原文](https://complexityzoo.net/Complexity_Zoo:A#aspace)

### ATIME(f(n)) — Alternating TIME
交替机 f(n) 时间。AP = ATIME(poly)，ALOGTIME = ATIME(log)；ATIME(poly f) = SPACE(poly f)（CKS81）。
- [原文](https://complexityzoo.net/Complexity_Zoo:A#atime)

### AUC-SPACE(f(n)) — Randomized Alternating f(n)-Space
带存在、全称、随机三种量词的 f(n) 空间机。poly 版 = SAPTIME = PSPACE（Pap83）；log 版含于 NP ∩ coNP 且有自然完全问题（Con92）。
- [原文](https://complexityzoo.net/Complexity_Zoo:A#aucspace)

### AuxPDA — Auxiliary Pushdown Automata
带对数工作带的下推自动机（不限时）。**= P**（Coo71b）。
- [原文](https://complexityzoo.net/Complexity_Zoo:A#auxpda)

### AVBPP — Average-Case BPP
输入取自可高效采样分布时有良好平均表现 BPP 算法的问题（OW93）。注意不等于 AvgP 的 BPP 版。
- [原文](https://complexityzoo.net/Complexity_Zoo:A#avbpp)

### AvgE — Average Exponential-Time With Linear Exponent
E 的 AvgP 式平均情形版。
- [原文](https://complexityzoo.net/Complexity_Zoo:A#avge)

### AvgP — Average Polynomial-Time
分布问题 (A,μ)：运行时间在 μ-平均意义下多项式（Lev86 的精心定义——更朴素的定义不满足封闭性）。**AvgP = DistNP ⇒ EXP = NEXP**（BCG+92）；严格含于 HeurP（NS05）。
- 主题章 [01-时间类](../01-时间类.md) · [原文](https://complexityzoo.net/Complexity_Zoo:A#avgp)

### AW[P] — Alternating W[P]
AW[SAT] 把公式换成电路；对 AW[SAT] 如 W[P] 对 W[SAT]（DF99）。
- [原文](https://complexityzoo.net/Complexity_Zoo:A#awp)

### AWPP — Almost WPP
NP 机接受与拒绝路径差被 FP 函数 f 双侧夹住的类（FFK94）。**含 BQP**（FR98，BQP 的经典上界之一）、WAPP、LWPP、WPP；含于 APP。
- 主题章 [04-随机与量子](../04-随机与量子.md)（BQP 的经典围栏） · [原文](https://complexityzoo.net/Complexity_Zoo:A#awpp)

### AW[SAT] — Alternating W[SAT]
参数化 QBFSAT（∃/∀ 交替、Hamming 权 k 的赋值）；对 W[SAT] 如 PSPACE 对 NP（DF99）。
- [原文](https://complexityzoo.net/Complexity_Zoo:A#awsat)

### AW[*] — Alternating W[*]
全体 AW[t] 之并。
- [原文](https://complexityzoo.net/Complexity_Zoo:A#awstar)

### AW[t] — Alternating W[t]
AW[SAT] 限公式深度 t。对所有 t：AW[t] = AW[*]（DFT98）——参数化交替层一夜拉平。
- [原文](https://complexityzoo.net/Complexity_Zoo:A#awt)

### AxP — Approximable in Polynomial Time
{0,1}^n → [0,1] 实值函数可在 poly(n,1/ε) 时间内 ε-逼近者（文献常称 AP，此处避撞名）。AxP 机器集在 RE 中（KRC00）。
- [原文](https://complexityzoo.net/Complexity_Zoo:A#axp)

### AxPP — Approximable in Probabilistic Polynomial Time
AxP 的随机版。**逼近电路接受概率是 AxPP 完全**——作者论证它比 BPP 更自然（BPP 被认为没有完全问题）；AxPP = AxP ⇒ BPP = P。
- [原文](https://complexityzoo.net/Complexity_Zoo:A#axpp)

---

## B（43 条）

### BC_=P — Bounded-Error C_=P
NP 机：yes ⇔ 恰一半路径接受；no 时接受比例 ≤1/4 或 ≥3/4。可高效放大、对布尔运算封闭；coRP ⊆ BC_=P ⊆ BPP（Wat15）。
- [原文](https://complexityzoo.net/Complexity_Zoo:B#bcequalsp)

### βFOLL — Limited-Nondeterminism FOLL
FOLL 电路 + O(log^k n) 非确定输入位的并。β₂FOLL 含拟群同构（乘法表输入）（CTW13）；β_kFO((log log n)^c) 算不了 parity——由此排除 GI 到拟群同构的 AC⁰ 多一归约。
- [原文](https://complexityzoo.net/Complexity_Zoo:B#betafoll)

### βMAC⁰ — Limited-Nondeterminism MAC⁰
MAC⁰ 电路 + O(log^k n) 非确定位。β_kMAC⁰ ⊆ β_kTC⁰；β₁MAC⁰ ⊆ TC⁰。
- [原文](https://complexityzoo.net/Complexity_Zoo:B#betamac0)

### βP — Limited-Nondeterminism NP
NP 机只用 O(log^k n) 次非确定转移（等价地：证据长 O(log^k n)），全体 k 之并（KF84）。存在 oracle 使 β_kP 间**任意一致的包含结构**都实现得了（BG98）；β₂P 含 LOGNP、LOGSNP。
- [原文](https://complexityzoo.net/Complexity_Zoo:B#betap)

### BH — Boolean Hierarchy Over NP
含 NP 且对交、并、补封闭的最小类；BH₁=NP，BH₂=NP∧coNP 型交错的逐层构造。含于 Δ₂P（乃至 P^NP[log]）；**BH 任一层塌缩 ⇒ PH 塌到 Σ₃P**（Kad88）。
- 主题章 [01-时间类](../01-时间类.md) · [原文](https://complexityzoo.net/Complexity_Zoo:B#bh)

### BLQP — Bounded-Error Lorentz Quantum Polynomial-Time
洛伦兹量子计算机（qubit + 双曲比特 hybit，态经洛伦兹而非酉变换，ZW26b）。多项式时间解 NP-难最大独立集；能模拟"测量后选择"量子计算而反向不可行。**= P^#P**。
- [原文](https://complexityzoo.net/Complexity_Zoo:B#blqp)

### BNQP — Bounded-Error Non-Hermitian Quantum Polynomial-Time
非厄米量子计算（含非酉线性门 G = diag(g^−1,g)，ZW26）。多项式时间解 NP-难 MIS；**= P^#P**——非酉门的"超能力"实为指数物理开销（BL25：距酉性多项式远的门即得 PostBQP = PP）。
- [原文](https://complexityzoo.net/Complexity_Zoo:B#bnqp)

### BP•L — Bounded-Error Probabilistic L with Two Way Access to Randomness
随机带可反复读的对数空间随机类。含 BPL、ZP•L、RNC¹；含于 BPP；**是否含于 P 是 open**（Nis93）。
- [原文](https://complexityzoo.net/Complexity_Zoo:B#bpdotl)

### BP_d(P) — Polynomial Size d-Times-Only Branching Program
每个输入位至多读 d 次的多项式大小分支程序。BP_d(P) ⊋ BP_{d-1}(P)（d>1，Tha98）——**读序受限分支程序的严格层级**；含于 PBP。
- [原文](https://complexityzoo.net/Complexity_Zoo:B#bpdp)

### BPE — Bounded-Error Probabilistic E
E 的 BPP 版。**EE = BPE ⟺ EXP = BPP**（IKW01）。
- [原文](https://complexityzoo.net/Complexity_Zoo:B#bpe)

### BPEE — Bounded-Error Probabilistic EE
EE 的 BPP 版。
- [原文](https://complexityzoo.net/Complexity_Zoo:B#bpee)

### BP_HSPACE(f(n)) — Bounded-Error Halting Probabilistic f(n)-Space
对所有随机带设置都停机的概率 f(n) 空间类。含于 DSPACE(f^{3/2})（SZ95）。
- [原文](https://complexityzoo.net/Complexity_Zoo:B#bphspace)

### BPL — Bounded-Error Probabilistic L
随机比特单向读、双侧有界的对数空间随机类。含于 SC、PL、BP•L、DET、NC²、P（Nis92/Coo85/BCP83）——**随机对数空间被围得很死**。
- 主题章 [02-空间类](../02-空间类.md) · [原文](https://complexityzoo.net/Complexity_Zoo:B#bpl)

### BP•NP — Probabilistic NP
**= AM**。
- [原文](https://complexityzoo.net/Complexity_Zoo:B#bpnp)

### BPP — Bounded-Error Probabilistic Polynomial-Time
yes 时 ≥2/3 路径接受、no 时 ≤1/3（Gil77）。带真随机源计算机的"可行问题"代名词。含于 Σ₂P ∩ Π₂P（Lau83）乃至 ZPP^NP；= Almost-P；除非 BPP = EXP 否则 p-测度为零（零一律）。
- 关键关系：BPP ⊆ P/poly（Adleman 去随机化）；去随机化猜想：BPP = P
- 主题章 [04-随机与量子](../04-随机与量子.md) · [原文](https://complexityzoo.net/Complexity_Zoo:B#bpp)

### BPP^cc — Communication Complexity BPP
有界误差通信版。由 EQUALITY 问题：≠ P^cc 且不含于 NP^cc。
- [原文](https://complexityzoo.net/Complexity_Zoo:B#bppcc)

### BPP_k^cc — BPP^cc in NOF model, k players
k 人 number-on-forehead 模型。k ≤ (1−δ)·log n 时 NP_k^cc ⊄ BPP_k^cc（DP08）。
- [原文](https://complexityzoo.net/Complexity_Zoo:B#bppkcc)

### BPP^KT — BPP With Time-Bounded Kolmogorov Complexity Oracle
带时限 Kolmogorov 复杂度 oracle 的 BPP。**在此类中可分解整数、算离散对数、在不可忽略比例输入上反转任意单向函数**（ABK+02）。
- 主题章 [00-复杂度动物园地图](../00-复杂度动物园地图.md)（Kolmogorov 桥） · [原文](https://complexityzoo.net/Complexity_Zoo:B#bppkt)

### BPP/log — BPP With Logarithmic Karp-Lipton Advice
语义 BPP 机 + O(log n) 建议位（坏建议也须以 ≥2/3 概率给出某答案）。含于 BPP/mlog。
- [原文](https://complexityzoo.net/Complexity_Zoo:B#bpplog)

### BPP/mlog — BPP With Logarithmic Deterministic Merlin-Like Advice
语法 BPP 机 + O(log n) 确定建议（坏建议可以摆烂）。含于 BPP/rlog。
- [原文](https://complexityzoo.net/Complexity_Zoo:B#bppmlog)

### BPP-OBDD — Polynomial-Size Bounded-Error Ordered Binary Decision Diagram
概率转移 OBDD。**算不了整数乘法**（AK96）；严格含于 BQP-OBDD（NHK00）。
- [原文](https://complexityzoo.net/Complexity_Zoo:B#bppobdd)

### BPP_path — Threshold BPP
路径可不等长的 BPP + 对随机路径性质的后选择刻画（HHT97）。**NP ⊆ BPP_path 几乎显然**（后选择让"好随机串"免费可得）；含 MA、P^NP[log]；含于 PP、BPP^NP。
- [原文](https://complexityzoo.net/Complexity_Zoo:B#bpppath)

### BPP/rlog — BPP With Logarithmic Probabilistically Sampled Random Advice
建议为依输入长度分布的 O(log n) 随机串。**严格含 BPP/mlog**（指纹术可认出有限稀疏语言）。
- [原文](https://complexityzoo.net/Complexity_Zoo:B#bpprlog)

### BPP//log — BPP With Logarithmic Randomness-Dependent Advice
建议可依赖机器自己的随机币（TV02）。若 EXP ∈ BPP//log 则 EXP = BPP；PSPACE 同理。
- [原文](https://complexityzoo.net/Complexity_Zoo:B#bppsslog)

### BPQP — Bounded-Error Probabilistic QP
拟多项式时间随机类的并（CNS99）。若 #P 无亚指数随机算法或 EXP 无亚指数电路，则 BPQP 层级严格。
- [原文](https://complexityzoo.net/Complexity_Zoo:B#bpqp)

### BPSPACE(f(n)) — Bounded-Error Probabilistic f(n)-Space
以概率 1 停机的概率 f(n) 空间。含 RSPACE 与 BP_HSPACE。
- [原文](https://complexityzoo.net/Complexity_Zoo:B#bpspace)

### BPTIME(f(n)) — Bounded-Error Probabilistic f(n)-Time
BPP 的 f(n) 时间版。BPTIME(n^{log n}) ≠ BPTIME(2^{n^ε})（KV88）；**带 1 位建议即有严格层级**（FS04 改进 Bar02 的 log n 位）——无建议的随机时间谱系至今 open。
- [原文](https://complexityzoo.net/Complexity_Zoo:B#bptime)

### BQL — Bounded-Error Quantum Logspace
O(log n) 量子比特、多项式时间的量子类。中间测量与否不改变类（FR21）；含于 DET（FR21）。
- 主题章 [02-空间类](../02-空间类.md)（量子对数空间） · [原文](https://complexityzoo.net/Complexity_Zoo:B#bql)

### BQNC — Alternate Name for QNC
QNC 的别名条目。
- [原文](https://complexityzoo.net/Complexity_Zoo:B#bqnc)

### BQNP — Alternate Name for QMA
QMA 的别名条目。
- [原文](https://complexityzoo.net/Complexity_Zoo:B#bqnp)

### BQP — Bounded-Error Quantum Polynomial-Time
量子图灵机多项式时间、误差 ≤1/3（等价定义：均匀多项式大小量子电路族，Yao93；振幅须高效可算否则可夹带难题答案）。量子计算机"可行问题"代名词；**整数分解在内**。已知围栏：含于 PP；oracle 下 P ≠ BQP、BQP ⊄ PH（Forrelation）、PPAD ⊄ BQP；若随机 oracle 下 P = BQP 则 BQP = BPP（FR98）。
- 主题章 [04-随机与量子](../04-随机与量子.md)（主角） · [原文](https://complexityzoo.net/Complexity_Zoo:B#bqp)

### BQP_CTC — BQP With Closed Timelike Curves
可访问闭合类时曲线（CTC）qubit 的 BQP。**= PSPACE**（Aar05c/AW09）——穿越时间的计算力恰好是多顶多项式空间。
- 主题章 [04-随机与量子](../04-随机与量子.md) · [原文](https://complexityzoo.net/Complexity_Zoo:B#bqpctc)

### BQP/log — BQP With Logarithmic Karp-Lipton Advice
BQP/poly 的 O(log n) 建议版。含于 BQP/mlog。
- [原文](https://complexityzoo.net/Complexity_Zoo:B#bqplog)

### BQP/mlog — BQP With Logarithmic Deterministic Merlin-Like Advice
语法 BQP 机 + O(log n) 经典建议。严格含于 BQP/qlog（NY03）——**O(log n) 量子建议 > O(log n) 经典建议，无条件**。
- [原文](https://complexityzoo.net/Complexity_Zoo:B#bqpmlog)

### BQP/mpoly — BQP With Polynomial-Size Deterministic Merlin-Like Advice
非一致多项式大小量子电路版 BQP（如 P/poly 之于 P）。含 BQP/qlog；含于 BQP/qpoly；不含 ESPACE（NY03）。
- [原文](https://complexityzoo.net/Complexity_Zoo:B#bqpmpoly)

### BQP-OBDD — Polynomial-Size Bounded-Error Quantum Ordered Binary Decision Diagram
酉转移 OBDD。严格含 BPP-OBDD（NHK00）。
- [原文](https://complexityzoo.net/Complexity_Zoo:B#bqpobdd)

### BQP/poly — BQP With Polynomial-Size Karp-Lipton Advice
坏建议下也须给出答案的语义版（对 BQP/mpoly 如 ∃BPP 对 MA）。含于 BQP/mpoly；含 BQP/log。
- [原文](https://complexityzoo.net/Complexity_Zoo:B#bqppoly)

### BQP/qlog — BQP With Logarithmic-Size Quantum Advice
O(log n) 量子态建议版。严格含 BQP/mlog（NY03）；含于 BQP/mpoly。
- [原文](https://complexityzoo.net/Complexity_Zoo:B#bqpqlog)

### BQP/qpoly — BQP With Polynomial-Size Quantum Advice
多项式大小量子态 ψ_n 作建议（NY03）。= YQP/poly（AD14）；不含 EESPACE；除非 CH 塌缩否则不含 PP；oracle 下不含 NP（AK06）。**量子建议的诡异之处：要求"坏建议也有界输出"反而让量子建议不可用（连续性论证）**。
- 主题章 [04-随机与量子](../04-随机与量子.md) · [原文](https://complexityzoo.net/Complexity_Zoo:B#bqpqpoly)

### BQPSPACE — Bounded-Error Quantum PSPACE
**= PSPACE = PPSPACE**——多项式空间层面量子毫无增益。
- [原文](https://complexityzoo.net/Complexity_Zoo:B#bqpspace)

### BQP_tt/poly — BQP/mpoly With Truth-Table Queries
只许非自适应 oracle 询问的 BQP/mpoly。oracle 下 P ⊄ BQP_tt/poly（NY03b）。
- [原文](https://complexityzoo.net/Complexity_Zoo:B#bqpttpoly)

### BQTIME(f(n)) — Bounded-Error Quantum f(n)-Time
BQP 的 f(n) 时间版（BV97）。
- [原文](https://complexityzoo.net/Complexity_Zoo:B#bqtime)

### k-BWBP — Bounded-Width Branching Program
k-PBP（限宽分支程序）的别名条目。
- [原文](https://complexityzoo.net/Complexity_Zoo:B#bwbp)
