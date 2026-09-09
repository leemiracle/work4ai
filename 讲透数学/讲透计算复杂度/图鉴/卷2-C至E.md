# 图鉴 · 卷2（C · D · E）

> 82 条 · 2026-09-06 快照自 [complexityzoo.net](https://complexityzoo.net/)。体例见[卷1](卷1-符号与A至B.md)与[总目](00-总目与口径.md)。

---

## C（43 条）

### CC — Comparator Circuits
比较器门（双输入，两输出线分别取 min/max，扇出 ≤1）电路求值问题（CCVP）在对数空间多一归约下的类。目前只知 NL ⊆ CC ⊆ P——**既不知是否在 NC、也不知是否 P-完全**的少数自然类之一。稳定婚姻、稳定室友、字典序极大匹配对其完全（Sub94）。
- 主题章 [03-电路类](../03-电路类.md) · [原文](https://complexityzoo.net/Complexity_Zoo:C#cc)

### CC⁰ — Constant-Depth MOD_m Circuits
只含 MOD_m 门（常数 m）的常数深度电路。任意对称函数可由深度 3、大小 2^{O(n^a)} 的 CC⁰ 电路计算（CW22）；对比 AC⁰ 深度 d 算对称函数需 2^{O(n^{1/(d-1)})}（Hås87）。
- [原文](https://complexityzoo.net/Complexity_Zoo:C#cc0)

### C_=AC⁰ — Exact-Counting AC⁰
DiffAC⁰ 函数 f 满足 yes ⇔ f(x)=0 的类。对数空间一致下 = TC⁰ = PAC⁰（ABL98）。
- [原文](https://complexityzoo.net/Complexity_Zoo:C#cequalsac0)

### C_=L — Exact-Counting L
对 L 如 C_=P 对 P。C_=L^{C_=L} = L^{C_=L}（ABO99）。
- [原文](https://complexityzoo.net/Complexity_Zoo:C#cequalsl)

### C_=P — Exact-Counting Polynomial-Time
NP 机接受路径数恰等于拒绝路径数 ⇔ yes。= coNQP（FGH+98）。
- 主题章 [05-交互证明与计数](../05-交互证明与计数.md)（计数世界成员） · [原文](https://complexityzoo.net/Complexity_Zoo:C#cequalsp)

### CFL — Context-Free Languages
上下文无关语言。⊊ LOGCFL；⊋ DCFL 与 UCFL（Bra77）。≠ QCFL（MC00）。
- [原文](https://complexityzoo.net/Complexity_Zoo:C#cfl)

### CH — Counting Hierarchy
C_kP 之并（C₀P=P，C₁P=PP，C_{k+1}P = PP^{C_kP}，Wag86）。含于 PSPACE；严格含 DLOGTIME-uniform TC⁰（CMTV98）。**是否存在 oracle 使 CH 无限（甚至 ≠ PSPACE）是 open**——与 TC⁰ =? NC¹ 密切相关（padding 论证：TC⁰=NC¹ ⇒ CH=PSPACE）。
- 主题章 [05-交互证明与计数](../05-交互证明与计数.md)（Toda 定理的舞台） · [原文](https://complexityzoo.net/Complexity_Zoo:C#ch)

### Check — Checkable Languages
宣称解决它的多项式时间程序可被高效**检查**的类（BK89）：存在 BPP 检查器 C，程序全对则通过、在 x 上错则抓住。= frIP ∩ cofrip；含于 NEXP ∩ coNEXP（FRS88）；若 NEE ⊄ BPEE 则 NP ⊄ Check（BG94）。
- [原文](https://complexityzoo.net/Complexity_Zoo:C#check)

### C_kP — k-th Level of CH
C₀P=P，C₁P=PP，C_{k+1}P=PP^{C_kP}。并即计数层级 CH。
- [原文](https://complexityzoo.net/Complexity_Zoo:C#ckp)

### CL — Catalytic Logspace
催化对数空间：O(log n) 工作带 + 多项式大小催化带（**用完必须原样归还**）。含 TC¹；含于 ZPP（BCKLS14）——"借来的空间"也能算出东西。
- 主题章 [02-空间类](../02-空间类.md) · [原文](https://complexityzoo.net/Complexity_Zoo:C#cl)

### CLOG — Continuous Logarithmic-Time
常微分方程（向量场由 NC¹ 公式给出）对数收敛时间可解的连续问题。n 整数取最大值在内（BSF02）——宜视为 NC¹ 的连续时间类比。含于 CP。
- [原文](https://complexityzoo.net/Complexity_Zoo:C#clog)

### CL#P — Cluster Sharp-P
#P 函数中其 NP 见证机的接受路径在多项式可判邻接的全序下**连成一段**者（HHK+05）。
- [原文](https://complexityzoo.net/Complexity_Zoo:C#clsharpp)

### CNP — Continuous NP
CP 的非确定类比（SF98，与奇怪吸引子有关——原页作者自注）。CP =? CNP 为作者所提问题。
- [原文](https://complexityzoo.net/Complexity_Zoo:C#cnp)

### coAM — Complement of AM
AM 的补（动物园原页无正文）。
- [原文](https://complexityzoo.net/Complexity_Zoo:C#coam)

### coC_=P — Complement of C_=P
= NQP（FGH+98）。
- [原文](https://complexityzoo.net/Complexity_Zoo:C#cocequalsp)

### cofrip — Complement of frIP
frIP 的补（原页无正文）。
- [原文](https://complexityzoo.net/Complexity_Zoo:C#cofrip)

### Coh — Coherent Languages
可高效**自归约**（autoreducible：只用 L-oracle 问 x 以外的点）的问题（Yao90b）。若 NEE ⊄ BPEE，则 Coh ∩ NP ⊄ compNP/Check/frIP 任一（BG94）。
- [原文](https://complexityzoo.net/Complexity_Zoo:C#coh)

### coMA — Complement of MA
MA 的补（原页无正文）。
- [原文](https://complexityzoo.net/Complexity_Zoo:C#coma)

### coMod_kP — Complement of Mod_kP
Mod_kP 的补（原页无正文）。
- [原文](https://complexityzoo.net/Complexity_Zoo:C#comodkp)

### compIP — Competitive IP Proof System
compNP 的交互证明版：yes 的证明只靠 L 自身 oracle 即可在多项式时间构造。若 NEE ⊄ BPEE 则 NP ∩ Coh ⊄ compIP（BG94）。
- [原文](https://complexityzoo.net/Complexity_Zoo:C#compip)

### compNP — Competitive NP Proof System
L ∈ NP 且 yes 证明可只用 L-oracle 多项式时间构造。含 NPC；含于 frIP；若 NEE ⊄ BPEE 则 ≠ NP（BG94）。
- [原文](https://complexityzoo.net/Complexity_Zoo:C#compnp)

### coNE — Complement of NE
NE 的补（原页无正文）。
- [原文](https://complexityzoo.net/Complexity_Zoo:C#cone)

### coNEXP — Complement of NEXP
含于 NEXP/poly（folklore，见 Fortnow 博客）。
- [原文](https://complexityzoo.net/Complexity_Zoo:C#conexp)

### coNL — Complement of NL
**= NL**（Imm88/Sze87，Immerman-Szelepcsényi 定理）——非确定空间对补封闭，1987 年前没人敢信。
- 主题章 [02-空间类](../02-空间类.md)（本章主角定理） · [原文](https://complexityzoo.net/Complexity_Zoo:C#conl)

### coNP — Complement of NP
NP 的补。NP = coNP ⇔ 不相容布尔公式有多项式大小的不相容证明；NP ≠ coNP ⇒ P ≠ NP（反向未知）。coNP 每个问题都有 IP 证明（证明者可限 BPP^#P）。coNP = SO-A（全称二阶查询）。
- 主题章 [01-时间类](../01-时间类.md) · [原文](https://complexityzoo.net/Complexity_Zoo:C#conp)

### coNPC — coNP-Complete
coNP 中最难者（在某归约下）。
- [原文](https://complexityzoo.net/Complexity_Zoo:C#conpc)

### coNP^cc — Complement of NP^cc
NP^cc 的补（原页无正文）。
- [原文](https://complexityzoo.net/Complexity_Zoo:C#conpcc)

### coNP/poly — Complement of NP/poly
若 NP ⊆ coNP/poly 则 PH 塌到 S₂P^NP（CCH+01）。NP^NP^NP^{(coNP/poly ∩ NP)} = NP^NP^NP（HNO+96）——动物园原页戏称"应 Luis Antuñes 建议，此标本已锁入笼中"。
- [原文](https://complexityzoo.net/Complexity_Zoo:C#conppoly)

### coNQP — Complement of NQP
= C_=P（FGH+98）。
- [原文](https://complexityzoo.net/Complexity_Zoo:C#conqp)

### coRE — Complement of RE
RE 的补，≠ RE。"给定可计算谓词 P，P 对所有正整数都真吗"是其完全问题。
- [原文](https://complexityzoo.net/Complexity_Zoo:C#core)

### coRNC — Complement of RNC
含二部图完美匹配判定（Kar86）。
- [原文](https://complexityzoo.net/Complexity_Zoo:C#cornc)

### coRP — Complement of RP
素性检测在其内（SS77）；ZPP = RP ∩ coRP。
- 主题章 [04-随机与量子](../04-随机与量子.md) · [原文](https://complexityzoo.net/Complexity_Zoo:C#corp)

### coSL — Complement of SL
SL 的补（原页无正文；事实上 SL 对补封闭——见卷6 SL 条）。
- [原文](https://complexityzoo.net/Complexity_Zoo:C#cosl)

### coSPARSE — Complement of SPARSE
SPARSE 的补（原页无正文）。
- [原文](https://complexityzoo.net/Complexity_Zoo:C#cosparse)

### coUCC — Complement of UCC
彩色图（每色至多两顶点）是否有非平凡自同构对其 L-归约完全（Tor00）。
- [原文](https://complexityzoo.net/Complexity_Zoo:C#coucc)

### coUP — Complement of UP
UP 的补（原页无正文）。
- [原文](https://complexityzoo.net/Complexity_Zoo:C#coup)

### CP — Continuous P
CLOG 的多项式收敛版（BSF02/SF98）。P-完全的最大流可在 CP 内；作者据此主张"P ⊆ CP"但难以形式化（CP 非标准意义复杂度类）；"CP ⊆ P"（ODE 可被图灵机高效积分）为 open。含于 CNP。
- [原文](https://complexityzoo.net/Complexity_Zoo:C#cp)

### cq-Σ_2 — Classical-Quantum-Σ_2P
Σ₂P 的有界误差量子推广：第一证明经典、第二证明量子、验证者为量子电路（GK14）。完全问题：QUANTUM SUCCINCT SET COVER、QUANTUM IRREDUNDANT、cq-Σ₂LH。
- [原文](https://complexityzoo.net/Complexity_Zoo:C#cqsigma2)

### CSIZE(f(n)) — Circuit Size f(n)
大小 O(f(n)) 的（非一致）布尔电路族。常记 SIZE(f(n))；CSIZE(poly) = P/poly。
- 主题章 [03-电路类](../03-电路类.md) · [原文](https://complexityzoo.net/Complexity_Zoo:C#csize)

### CSL — Context Sensitive Languages
上下文有关文法生成的语言。**= NSPACE(n)**（Kur64）。
- [原文](https://complexityzoo.net/Complexity_Zoo:C#csl)

### CSP — Constraint Satisfaction Problems
固定模板约束满足问题类（FV93）；3SAT 即 {0,1} 上含 C₀–C₃ 子句关系的模板。MMSNP 可随机归约到 CSP。
- [原文](https://complexityzoo.net/Complexity_Zoo:C#csp)

### CSPACE — Catalytic Space
催化图灵机（工作带 s + 催化带 c，催化带用毕须还原初态 τ）的类（BCKLS14）。主变体为 CL；也有催化分支程序非一致版（GKM15）。
- [原文](https://complexityzoo.net/Complexity_Zoo:C#cspace)

### CZK — Computational Zero-Knowledge
计算零知识：验证者视图与可模拟分布只需对 BPP **计算不可区分**（不必统计接近）。是否对补封闭未知；在单向函数假设下含 NP（BGG+90，且该蕴含不相对化！）；无单向函数则 CZK = AVBPP（OW93）。含 PZK 与 SZK。
- 主题章 [05-交互证明与计数](../05-交互证明与计数.md) · [原文](https://complexityzoo.net/Complexity_Zoo:C#czk)

---

## D（18 条）

### DCFL — Deterministic CFL
确定性下推自动机接受的语言。严格含于 CFL（GG66）；含于 UCFL（也严格）；严格含 REG。
- [原文](https://complexityzoo.net/Complexity_Zoo:D#dcfl)

### Δ₂P — P With NP Oracle
PH 第二层的确定性级：P^NP。Δ₂P-完全问题：布尔公式的字典序最后满足赋值是否以 1 结尾（Kre88）。含 BH；存在 oracle 使 Δ₂P ⊄ PP、也使 Δ₂P ⊆ P/poly（乃至线性大小电路）。若 P = NP，任何多项式大小电路可在 Δ₂P^C 内学习（Aar06）。
- 主题章 [01-时间类](../01-时间类.md)（PH 塔楼第二层） · [原文](https://complexityzoo.net/Complexity_Zoo:D#delta2p)

### δ-BPP — δ-Semi-Random BPP
随机源每比特可为任意历史依赖、只保证以 [δ,1−δ] 概率为 1。**任意 δ>0：δ-BPP = BPP**（VV85/Zuc91）——轻度偏置的随机源免费可用。
- [原文](https://complexityzoo.net/Complexity_Zoo:D#deltabpp)

### δ-RP — δ-Semi-Random RP
RP 版半随机源。任意 δ>0：δ-RP = RP（VV85）。
- [原文](https://complexityzoo.net/Complexity_Zoo:D#deltarp)

### DET — Determinant
对数空间归约到 n×n 整数矩阵行列式计算的类（Coo85）。含于 NC²；含 NL 与 PL（BCP83）；图同构对 DET 硬（Tor00）。函数版 = GapL（行列式是 GapL-完全）。
- 主题章 [02-空间类](../02-空间类.md) · [原文](https://complexityzoo.net/Complexity_Zoo:D#det)

### DiffAC⁰ — Difference #AC⁰
两个 #AC⁰ 函数之差。对数空间一致下 = GapAC⁰（ABL98）。
- [原文](https://complexityzoo.net/Complexity_Zoo:D#diffac0)

### DisNP — Disjoint NP Pairs
yes 实例集非空且不相交的 NP 问题对 (A,B)。存在最优命题证明系统 ⇒ DisNP 有完全对（Raz94）；存在 oracle 使无完全对（GSS+03）；P ≠ UP ⇒ 有 P-不可分离对（GS88）。
- [原文](https://complexityzoo.net/Complexity_Zoo:D#disnp)

### DistNP — Distributional NP
分布问题 (A,μ)：A ∈ NP、μ 的累积分布多项式可算（亦记 (NP,P-computable)/RNP）。有完全问题（Lev86，不像 NP 那样直接）；DistNP-完全亦是 (NP,P-samplable)-完全（IL90）。
- 主题章 [01-时间类](../01-时间类.md)（平均情形复杂度） · [原文](https://complexityzoo.net/Complexity_Zoo:D#distnp)

### DistributionPH — Distribution PH
证明者发送（独立）概率分布/混态、验证者从每份证明抽一个样本的中道模型（GY24）。**塌缩为标准 PH**；允许相关则如 QEPH 两层塌平。
- [原文](https://complexityzoo.net/Complexity_Zoo:D#distributionph)

### DP — Difference Polynomial-Time
D^p = BH₂（布尔层级第二层）：一个 NP 语言与一个 coNP 语言之交。完全问题：Exact-Clique、SAT-UNSAT（PY84）。含 NP 与 coNP；含于 Δ₂P。
- [原文](https://complexityzoo.net/Complexity_Zoo:D#dp)

### DQC1 — Deterministic Quantum Computing with 1 Clean Bit
仅 1 个干净量子比特、其余最大混合态的 BQP（禁强测量）。若 DQC1 = BQP 需非逐门模拟（ASV00）；辫迹闭包的 Jones 多项式（五次单位根处）逼近对其完全（SJ08）。
- 主题章 [04-随机与量子](../04-随机与量子.md)（"1 个干净 qubit 能干什么"） · [原文](https://complexityzoo.net/Complexity_Zoo:D#dqc1)

### DQP — Dynamical Quantum Polynomial-Time
带"动力学模拟器"oracle 的 BQP：给多项式大小量子电路，返回满足对称性与局域性公理的经典历史样本（对抗性可选分布）（Aar05）。含 BQP 与 SZK；含于 EXP；oracle 下不含 NP。
- [原文](https://complexityzoo.net/Complexity_Zoo:D#dqp)

### D#P — Alternate Name for P^#P
P^#P 的别名条目。
- [原文](https://complexityzoo.net/Complexity_Zoo:D#dsharpp)

### DSPACE(f(n)) — Deterministic f(n)-Space
确定性 f(n) 空间。**空间谱系定理**：可构造 f > log n 时 DSPACE(f) ⊊ DSPACE(f log f)（HLS65）。DSPACE(n) ≠ NP（但谁含谁都未知！）。
- 主题章 [02-空间类](../02-空间类.md) · [原文](https://complexityzoo.net/Complexity_Zoo:D#dspace)

### DTIME(f(n)) — Deterministic f(n)-Time
确定性 f(n) 时间。**时间谱系定理**：可构造 f > n 时 DTIME(f) ⊊ DTIME(f log f log log f)（HS65）——推论 P ⊊ EXP。DTIME(n) ⊊ NTIME(n)（PPS+83）。任意可构造超多项式 f：DTIME(f)^PP ⊄ P/poly（All96）。
- 主题章 [01-时间类](../01-时间类.md)（谱系定理本尊） · [原文](https://complexityzoo.net/Complexity_Zoo:D#dtime)

### DTISP(t(n),s(n)) — Simultaneous Time-Space
同时限 O(t(n)) 时间与 O(s(n)) 空间。SC = DTISP(poly, polylog)。BPSPACE(s) ⊆ DTISP(2^{O(s)}, s²)（Nis92）。
- [原文](https://complexityzoo.net/Complexity_Zoo:D#dtisp)

### Dyn-FO — Dynamic FO
一阶谓词维护的多项式大小数据结构、每步更新（增删边等）FO 可算的**动态问题**类（HI02 有完全问题）。
- [原文](https://complexityzoo.net/Complexity_Zoo:D#dynfo)

### Dyn-ThC⁰ — Dynamic Threshold Circuits
Dyn-FO 的带 COUNT 谓词版（均匀 TC⁰ 而非 AC⁰ 的动态版，HI02）。
- [原文](https://complexityzoo.net/Complexity_Zoo:D#dynthc0)

---

## E（21 条）

### E — Exponential Time With Linear Exponent
DTIME(2^{O(n)})。相对任意 oracle 都 ≠ NP（Boo72）与 ≠ PSPACE（Boo74）；却有 oracle 使 E ⊆ NP、也有使 PSPACE ⊆ E。BPP 难问题在 E 中……（原页续）稀疏塌缩集不存在性等结论——E 是"指数世界的 P"，谱系定理在此最好用。
- 主题章 [01-时间类](../01-时间类.md) · [原文](https://complexityzoo.net/Complexity_Zoo:E#e)

### EE — Double-Exponential Time With Linear Exponent
DTIME(2^{2^{O(n)}})。**EE = BPE ⟺ EXP = BPP**（IKW01）。含于 EEXP 与 NEE。
- [原文](https://complexityzoo.net/Complexity_Zoo:E#ee)

### EEE — Triple-Exponential Time With Linear Exponent
DTIME(2^{2^{2^{O(n)}}})。EEE = BPEE 是否蕴含 EE = BPE 未知（IKW01）。
- [原文](https://complexityzoo.net/Complexity_Zoo:E#eee)

### EESPACE — Double-Exponential Space With Linear Exponent
DSPACE(2^{2^{O(n)}})。不含于 BQP/qpoly（NY03）。
- [原文](https://complexityzoo.net/Complexity_Zoo:E#eespace)

### EEXP — Double-Exponential Time
DTIME(2^{2^{p(n)}})（p 多项式），即 2-EXP。含 EE；含于 NEEXP。
- [原文](https://complexityzoo.net/Complexity_Zoo:E#eexp)

### EH — Exponential-Time Hierarchy With Linear Exponent
E 版 PH：E、NE、NE^NP、…之并（Har87）。若 coNP ⊆ AM[polylog] 则 EH 塌到 S₂-EXP•P^NP（SS04）乃至 AM_EXP（PV04）。与 SEH 不可比较（已知）。
- 主题章 [01-时间类](../01-时间类.md) · [原文](https://complexityzoo.net/Complexity_Zoo:E#eh)

### ELEMENTARY — Finitely Iterated Exponential Time
DTIME(2^n) ∪ DTIME(2^{2^n}) ∪ …（有限层指数塔）之并。含于 PR 与 TOWER。**初等递归的复杂度天花板**。
- 主题章 [01-时间类](../01-时间类.md) · [原文](https://complexityzoo.net/Complexity_Zoo:E#elementary)

### EL_kP — Extended Low Hierarchy
低层级扩张：Σ_kP^A ⊆ Σ_{k-1}P^{A,NP} 的 A（BBS86）。
- [原文](https://complexityzoo.net/Complexity_Zoo:E#elkp)

### EP — NP with 2^k Accepting Paths
NP 机：no 全拒绝、yes 时接受路径数为 2 的幂（BHR00）。含 UP；含于 C_=P 与 Mod_kP（奇 k）。
- [原文](https://complexityzoo.net/Complexity_Zoo:E#ep)

### EPTAS — Efficient PTAS
时间 f(ε)·p(n) 的近似方案（ε 只惩罚 f）。含 FPTAS、含于 PTAS。FPT = XP_uniform ⇒ EPTAS = PTAS；EPTAS = PTAS ⇒ FPT = W[P]；FPT ⊊ W[1] ⇒ 存在 PTAS ∖ EPTAS 的自然问题（CT97）——**近似方案与参数化复杂度的握手处**。
- 主题章 [06-参数化与优化](../06-参数化与优化.md) · [原文](https://complexityzoo.net/Complexity_Zoo:E#eptas)

### k-EQBP — Width-k Exact Quantum Branching Programs
宽 k、零误差量子分支程序（每步作用依赖单输入比特的酉矩阵）（AMP02）。NC¹ ⊆ 2-EQBP。
- [原文](https://complexityzoo.net/Complexity_Zoo:E#eqbp)

### EQP — Exact Quantum Polynomial-Time
零误差（概率 1 正确）多项式时间量子计算。无通用 QTM 理论；门集取有限集（BV97 定义，无限门集另见 EQP_K）。P^{||NP[2k]} ⊆ EQP^{||NP[k]}（BD99）。
- 主题章 [04-随机与量子](../04-随机与量子.md) · [原文](https://complexityzoo.net/Complexity_Zoo:E#eqp)

### EQP_K — Exact Quantum Polynomial-Time with Gate Set K
门集取自 K 的 EQP（K 有限或可数）。超越门可用代数门无损替换（ADH97）；Simon 算法在 EQP_Q；Z/p 上离散对数在 EQP_Q̄（无限门，MZ03）。EQP ⊆ LWPP。
- [原文](https://complexityzoo.net/Complexity_Zoo:E#eqpk)

### EQTIME(f(n)) — Exact Quantum f(n)-Time
EQP 的 f(n) 时间版（BV97）。
- [原文](https://complexityzoo.net/Complexity_Zoo:E#eqtime)

### ESPACE — Exponential Space With Linear Exponent
DSPACE(2^{O(n)})。若 E = ESPACE（甚至 E 在 ESPACE 中非零测度）则 P = BPP（HY84/Lut91）；不含于 P/poly（Kan82）与 BQP/mpoly（NY03）。
- [原文](https://complexityzoo.net/Complexity_Zoo:E#espace)

### ∃BPP — BPP With Existential Operator
NP^BPP 等价定义。含 NP 与 BPP；含于 MA 与 SBP。**看似显然等于 MA，却有 oracle 使其不等**（FFK+93）——差别在于 ∃BPP 要求每个 y 的接受概率都远离 1/2，MA 允许"坏 y"任意。
- [原文](https://complexityzoo.net/Complexity_Zoo:E#existsbpp)

### ∃NISZK — NISZK With Existential Operator
含 NP 与 NISZK；含于 PH 第三层。
- [原文](https://complexityzoo.net/Complexity_Zoo:E#existsniszk)

### ∃R — Existential Theory of the Reals
可归约到"整系数多元多项式组有实解"的问题（半代数集非空性，Sha10）。含 NP、含于 PSPACE；**离散与计算几何一大批问题住在这里**。
- 主题章 [00-复杂度动物园地图](../00-复杂度动物园地图.md) · [原文](https://complexityzoo.net/Complexity_Zoo:E#existsreals)

### EXP — Exponential Time
∪_p DTIME(2^{p(n)})，= P^E。L = P ⇒ PSPACE = EXP；EXP ⊆ P/poly ⇒ EXP = MA（BFL91）；多一归约完全问题在 EXP 中测度 0（May94/JL95）；oracle 下 EXP = NP = ZPP 等各种世界并存。描述复杂度：EXP = SO(2^{n^{O(1)}}) = SO(LFP)。
- 主题章 [01-时间类](../01-时间类.md)（指数世界主角） · [原文](https://complexityzoo.net/Complexity_Zoo:E#exp)

### EXP/poly — Exponential Time With Polynomial Advice
EXP + 多项式建议。含 BQP/qpoly（Aar04b）。
- [原文](https://complexityzoo.net/Complexity_Zoo:E#exppoly)

### EXPSPACE — Exponential Space
∪_p DSPACE(2^{p(n)})。实数上只含加法与比较的一阶命题可在 EXPSPACE 内判定（Ber80）。
- 主题章 [02-空间类](../02-空间类.md) · [原文](https://complexityzoo.net/Complexity_Zoo:E#expspace)
