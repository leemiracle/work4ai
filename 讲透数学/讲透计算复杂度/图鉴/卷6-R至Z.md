# 图鉴 · 卷6（R · S · T · U · V · W · X · Y · Z）

> 125 条（R 20 + S 40 + T 11 + U 14 + V 7 + W 11 + X 6 + Y 7 + Z 9）· 2026-09-06 快照自 [complexityzoo.net](https://complexityzoo.net/)。体例见[卷1](卷1-符号与A至B.md)。

---

## R（20 条）

### R — Recursive Languages
图灵机可解的语言——丘奇-图灵论题的"可有效计算"代名词（Tur36/Chu41）。= RE ∩ coRE；严格含 PR（Kle71）。
- 主题章 [00-复杂度动物园地图](../00-复杂度动物园地图.md)（可计算性地平线） · [原文](https://complexityzoo.net/Complexity_Zoo:R#r)

### RBQP — Strict Quantum RP
见证可被 FBQP 找到的 NP 问题（如无平方因子数在 coRBQP——分解即证书）。含 RP 与 ZBQP；含于 BQP 与 RQP。
- [原文](https://complexityzoo.net/Complexity_Zoo:R#rbqp)

### RE — Recursively Enumerable Languages
递归可枚举：yes 可在有穷时间内被图灵机确认（no 可能永不停机）；等价地 yes 实例可被逐一列出。停机问题是 RE-完全；Post 问题（存在既非 R 又非 RE-完全的中介度）由 Muc56 解决——RE 有无穷多个互不等价的 Turing 度，其结构被研究到超乎想象（Sho99）。**MIP* = RE 让这个可计算性边界类重新回到复杂度舞台中央**。
- 主题章 [05-交互证明与计数](../05-交互证明与计数.md)（MIP*=RE 落点） · [原文](https://complexityzoo.net/Complexity_Zoo:R#re)

### REG — Regular Languages
正则语言：DFA = NFA = DSPACE(O(1)) = DSPACE(o(log log n))（She59/HLS65）。含 parity、不含 majority——"有限自动机不会数数"。含于 NC¹。
- 主题章 [00-复杂度动物园地图](../00-复杂度动物园地图.md) · [原文](https://complexityzoo.net/Complexity_Zoo:R#reg)

### RevSPACE(f(n)) — Reversible f(n)-Space
可逆图灵机（每格局至多一个前驱）的 f(n) 空间。**= DSPACE(f)**（LMT97）——可逆性不损计算力，量子计算的地基之一。
- 主题章 [04-随机与量子](../04-随机与量子.md) · [原文](https://complexityzoo.net/Complexity_Zoo:R#revspace)

### RG — Refereed Games
裁判博弈：概率多项式时间验证者与两个竞争的全能证明者对弈（可向证明者隐藏信息）。公币 RG = SAPTIME = PSPACE（Pap83）；**RG = EXP**（FK97b，且对任意 oracle RG ⊆ EXP——KM92）。
- 主题章 [05-交互证明与计数](../05-交互证明与计数.md) · [原文](https://complexityzoo.net/Complexity_Zoo:R#rg)

### RG(1) — One-turn Refereed Games
无回传消息的裁判博弈（分布策略版 S₂P）。含 S₂P（可视为其随机化版）；含于 RG(2)。
- [原文](https://complexityzoo.net/Complexity_Zoo:R#rg1)

### RG(2) — Two-turn Refereed Games
双方一问一答（并行）。**= PSPACE**（FK97b）。
- [原文](https://complexityzoo.net/Complexity_Zoo:R#rg2)

### RG(k) — k-turn Refereed Games
k 轮版；RG(poly)=RG。常数 k≥2 时是否都等于 PSPACE 是 open。
- [原文](https://complexityzoo.net/Complexity_Zoo:R#rgk)

### R_HL — Randomized Halting Logarithmic-Space
RP 的对数空间全停机版。含无向可达性（AKL+79）；含于 RL。
- [原文](https://complexityzoo.net/Complexity_Zoo:R#rhl)

### R_HSPACE(f(n)) — One-Sided Error Halting Probabilistic f(n)-Space
RP 之于 BP_HSPACE。
- [原文](https://complexityzoo.net/Complexity_Zoo:R#rhspace)

### RL — Randomized Logarithmic-Space
单侧误差随机对数空间（概率 1 停机 + 多项式时间，否则就是 NL）。含 R_HL；含于 SC（Nis92）；RL = L 有强证据（RTV05）。
- 主题章 [02-空间类](../02-空间类.md) · [原文](https://complexityzoo.net/Complexity_Zoo:R#rl)

### RNC — Randomized NC
随机并行类（对 NC 如 RP 对 P）。**二部图最大匹配在内**（MVV87——随机并行赢了确定并行至今没赢的一仗）；含于 QNC。
- 主题章 [03-电路类](../03-电路类.md) · [原文](https://complexityzoo.net/Complexity_Zoo:R#rnc)

### RNC¹ — Randomized NC1
NC 塔第一层的随机版。含于 BP•L。
- [原文](https://complexityzoo.net/Complexity_Zoo:R#rnc1)

### RP — Randomized Polynomial-Time
单侧误差随机多项式时间：yes 时 ≥1/2 路径接受、no 全拒绝（Gil77）。素性检测曾住此（AH87）后被 AKS02 接进 P；与 ZPP 同 p-测度且零一律（非零则 ZPP=BPP=EXP）。
- 主题章 [04-随机与量子](../04-随机与量子.md)（主角） · [原文](https://complexityzoo.net/Complexity_Zoo:R#rp)

### RP^cc — Communication Complexity RP
单侧误差通信版。含 EQUALITY 的补。
- [原文](https://complexityzoo.net/Complexity_Zoo:R#rpcc)

### RP_k^cc — Randomized P_k^cc
k 人 NOF 共享随机单侧误差版。k ≤ (1−δ)log n 时 ≠ NP_k^cc（DP08）。
- [原文](https://complexityzoo.net/Complexity_Zoo:R#rpkcc)

### RPP — Restricted Pseudo Polynomial-Time
(x,m) 在 poly(n+m) 时间与 O(m+log n) 空间同时可解的类（Mon80）。与 FPT 相望。
- [原文](https://complexityzoo.net/Complexity_Zoo:R#rpp)

### RQP — One-sided Error Extension of EQP
no 时概率 0 接受、yes 时 ≥1/2 的量子类（EQP 式精确概率警告适用）。含 ZQP 与 RBQP；含于 BQP。
- [原文](https://complexityzoo.net/Complexity_Zoo:R#rqp)

### RSPACE(f(n)) — Randomized f(n)-Space
RL 的 f(n) 空间版（时间限 2^{O(f)}）。含于 NSPACE(f) 与 BPSPACE(f)。
- [原文](https://complexityzoo.net/Complexity_Zoo:R#rspace)

---

## S（40 条）

### S₂E — Symmetric Linear-Exponent Hierarchy 第二层
指数谓词版 S₂P。**需要近最大规模电路 Ω(2^n/n)**（Li23；对更一般的 O₂E 也成立）。
- [原文](https://complexityzoo.net/Complexity_Zoo:S#s2e)

### S₂-EXP•P^NP — Don't Ask
（原页标题即"别问"。动物园笼中之类：卷入 AM[polylog]、coNP 与 EH 的塌缩丑闻。）EH 塌缩的常见落点。
- [原文](https://complexityzoo.net/Complexity_Zoo:S#s2exppnp)

### S₂P — Second Level of the Symmetric Hierarchy
对称层级第二层：yes 时 ∃y∀z P 成立、no 时 ∃z∀y ¬P（RS98）——证明者与反驳者**同时**出招的多项式时间裁判。NP^RP ⊆ S₂P ⊆ ZPP^NP（Cai01）；**NP ⊆ P/poly ⇒ PH = S₂P**（Sengupta，经 Cai01；乃至 = O₂P，CR06）。
- 主题章 [01-时间类](../01-时间类.md)（PH 的对称表亲） · [原文](https://complexityzoo.net/Complexity_Zoo:S#s2p)

### SAC — Semi-Unbounded-Fanin AC
深度 O(log^k n)、无界 OR + 有界 AND 电路塔（BCD+89）。SAC^k（k>0）对补封闭。
- 主题章 [03-电路类](../03-电路类.md) · [原文](https://complexityzoo.net/Complexity_Zoo:S#sac)

### SAC⁰ — Semi-Unbounded-Fanin AC⁰
常数深度版。不对补封闭（BCD+89）；不含于 ⊕SAC⁰（K23）。
- [原文](https://complexityzoo.net/Complexity_Zoo:S#sac0)

### SAC¹ — Semi-Unbounded-Fanin AC¹
深度 O(log n) 版。= LOGCFL/poly（Ven91）；含于 ⊕SAC¹（GW96）。
- [原文](https://complexityzoo.net/Complexity_Zoo:S#sac1)

### SAPTIME — Stochastic Alternating Polynomial-Time
带 ∃/∀/随机三种量词的多项式时间（Pap83）。**= PSPACE**。
- [原文](https://complexityzoo.net/Complexity_Zoo:S#saptime)

### SBP — Small Bounded-Error Probability
#P 函数 f 与 FP 函数 g 满足 yes: f>g、no: f<g/2（BGM02）。含 MA、WAPP、∃BPP；含于 AM 与 BPP_path；oracle 下 ⊄ Σ₂P、不对交封闭（GLM+15）；SAT 亚指数路径数 ⇒ SBP = AM（Vol20）。
- 主题章 [05-交互证明与计数](../05-交互证明与计数.md) · [原文](https://complexityzoo.net/Complexity_Zoo:S#sbp)

### SBP^cc — Communication Complexity SBP
yes 接受率 ≥α、no ≤α/2 的通信版（代价含 log(1/α)）。不含 coNP^cc（Raz92/GW14）；度量 = corruption bound。
- [原文](https://complexityzoo.net/Complexity_Zoo:S#sbpcc)

### SBQP — Small Bounded-Error Quantum Polynomial-Time
yes 接受率 ≥2^{−p}、no ≤2^{−p−1} 的量子类（Kup09）。= A₀PP。
- [原文](https://complexityzoo.net/Complexity_Zoo:S#sbqp)

### SC — Steve's Class
（纪念 Stephen Cook。）多项式时间 + 多对数空间**同时**满足。可能小于 P ∩ polyL（后者只须两个分别的算法）；DCFL 在内（Coo79）；含 RL 与 BPL（Nis92）；= DTISP(poly, polylog)。
- 主题章 [02-空间类](../02-空间类.md)（时间×空间双预算） · [原文](https://complexityzoo.net/Complexity_Zoo:S#sc)

### SE — Subexponentially-Solvable Search Problems
对每个 ε>0 都有 O(2^{εn}) 算法的 FNP 搜索问题（IPZ01）。k-SAT/着色/集合覆盖/团/顶点覆盖之一在 SE 则全在。
- [原文](https://complexityzoo.net/Complexity_Zoo:S#se)

### SEH — Strong Exponential Hierarchy
NE、NP^NE、NP^NP^NE、…之并（Hem89）。**塌缩到 P^NE**；与 EH 不可比较（已知）。
- [原文](https://complexityzoo.net/Complexity_Zoo:S#seh)

### SelfNP — Self-Witnessing NP
全体 yes 实例的合法证据之并恰等于语言自身的 NP（HT03）。其多一归约闭包 = NP；SAT 在内。
- [原文](https://complexityzoo.net/Complexity_Zoo:S#selfnp)

### SF_k — Width-k Bottleneck Turing Machines
多项式时间后只剩 k 值保险存储的瓶颈图灵机（CF91）。SF₂ 同时含 ⊕P 与 NP；SF₅ = PSPACE；SF₂–SF₄ 的复杂度被 Ogi94 等细究。
- [原文](https://complexityzoo.net/Complexity_Zoo:S#sfk)

### Σ₂P — NP With NP Oracle
PH 第二层存在侧（= NP^coNP）。完全问题：最小等价 DNF、最短蕴含词（Uma98）、完美图 2-团-着色（FMF16）；Σ₂P ∩ Π₂P 有无 n^k 电路的问题（Kan82）。
- 主题章 [01-时间类](../01-时间类.md) · [原文](https://complexityzoo.net/Complexity_Zoo:S#sigma2p)

### SIZE(f(n)) — Circuit Size f(n)
CSIZE(f(n)) 的别名条目。
- [原文](https://complexityzoo.net/Complexity_Zoo:S#size)

### SKC — Statistical Knowledge Complexity
SZK 的知识复杂度层级推广（GP91）：hint 式/严格 oracle 式/平均 oracle 式/熵式四种刻画。
- [原文](https://complexityzoo.net/Complexity_Zoo:S#skc)

### SL — Symmetric Logarithmic-Space
对称非确定对数空间（转移可逆，LP82）；USTCON（无向 s-t 连通）对其 L-归约完全。SL = coSL、SL^SL = SL（NT95）；**Reingold 2004：SL = L（乃至相对任何 oracle）**——确定性随机漫步算法，一举吞并此前所有部分结果。
- 主题章 [02-空间类](../02-空间类.md)（Reingold 定理主角） · [原文](https://complexityzoo.net/Complexity_Zoo:S#sl)

### SLICEWISE PSPACE — Parametrized PSPACE
FPT 的空间版：空间 f(k)p(|x|)。P = PSPACE ⇒ FPT = SLICEWISE PSPACE（DF99）。
- [原文](https://complexityzoo.net/Complexity_Zoo:S#slicewisepspace)

### S^≠ — Exclusive Stochastic Languages
概率有限自动机以"接受概率 ≠p ⇔ 在语言中"定义的类（Yakaryılmaz-Say）。= NQL。
- [原文](https://complexityzoo.net/Complexity_Zoo:S#sneq)

### SNP — Strict NP
二阶全称量词（顶点上、无存在量词）图论谓词可归约到的类（承 Fagin 定理语境）。k-SAT 在内、一般 SAT 不在（不许说"子句中存在满足文字"）。含 MMSNP。
- 主题章 [00-复杂度动物园地图](../00-复杂度动物园地图.md)（Fagin 谱系） · [原文](https://complexityzoo.net/Complexity_Zoo:S#snp)

### SO — Second-Order Logic
二阶逻辑：FO 上再对关系变量量化。**SO = PH**（量词交替 k 次即第 k 层）；∃SO = NP（Fagin 定理）、∀SO = coNP——描述复杂度的中轴线。
- 主题章 [00-复杂度动物园地图](../00-复杂度动物园地图.md)（Fagin 定理主角） · [原文](https://complexityzoo.net/Complexity_Zoo:S#so)

### SO(Horn) — Second-order in Horn form
无量词部分为 Horn 范式的二阶逻辑。**= P**（Grä92）。
- 主题章 [01-时间类](../01-时间类.md)（P 的又一个逻辑化身） · [原文](https://complexityzoo.net/Complexity_Zoo:S#sohorn)

### SO(Krom) — Second-order in Krom form
每子句至多两文字的二阶逻辑。**= NL**（Grä92）。
- 主题章 [02-空间类](../02-空间类.md) · [原文](https://complexityzoo.net/Complexity_Zoo:S#sokrom)

### SO[LFP] — Second-Order with LFP
带最小不动点的二阶逻辑。**= EXPTIME**。
- [原文](https://complexityzoo.net/Complexity_Zoo:S#solfp)

### SO[t(n)] — Iterated Second-Order Logic
二阶量词块迭代 t(n) 次。SO[n^{O(1)}] = PSPACE = SO(TC)；SO[2^{n^{O(1)}}] = EXPTIME = SO(LFP)。
- [原文](https://complexityzoo.net/Complexity_Zoo:S#sot)

### SO[TC] — Second-Order with Transitive Closure
带传递闭包的二阶逻辑。= PSPACE。
- [原文](https://complexityzoo.net/Complexity_Zoo:S#sotc)

### SP — Semi-Efficient Parallel
并行比串行快 n^ε 因子的 P 问题（KRS90）。亦为 XP_uniform 别名。
- [原文](https://complexityzoo.net/Complexity_Zoo:S#sp)

### span-L — Span Logarithmic-Space
NL 机接受路径**输出值集合**的大小（AJ93）。span-L ⊆ FP ⟺ FP = #P；span-L ⊆ FPRAS（ACJ+21）。
- [原文](https://complexityzoo.net/Complexity_Zoo:S#spanl)

### span-P — Span Polynomial-Time
NP 机接受路径输出集合大小（KST+89）。含 #P 与 OptP；span-P = #P ⟺ UP = NP。
- [原文](https://complexityzoo.net/Complexity_Zoo:S#spanp)

### SPARSE — Sparse Languages
每长度 n 的 yes 实例数多项式有界。SPARSE ∩ NPC ≠ ∅ ⇒ P = NP（Mah82）。含 TALLY。
- [原文](https://complexityzoo.net/Complexity_Zoo:S#sparse)

### SPL — Stoic PL
对 PL 如 SPP 对 PP。伪随机假设下含最大/完美匹配（ARZ99）；含 UL；= 对 GapL low 的问题集。
- 主题章 [02-空间类](../02-空间类.md) · [原文](https://complexityzoo.net/Complexity_Zoo:S#spl)

### SPP — Stoic PP
no ⇔ 接受数=拒绝数、yes ⇔ 差 1（FFK94）。**对 PP 完全 low**（PP^SPP = PP）；黑箱群的一窝问题在内；置换群隐藏子群问题在 FP^SPP（Vin04/AK02）——量子计算关心的 HSP 被经典 SPP 圈住。
- 主题章 [05-交互证明与计数](../05-交互证明与计数.md) · [原文](https://complexityzoo.net/Complexity_Zoo:S#spp)

### SQG — Short Quantum Games
验证者可先处理 yes 方答案再出题给 no 方的量子裁判博弈（GW05）。含 QIP；**= PSPACE**（GW10）——量子信息+顺序处理仍不破 PSPACE。
- [原文](https://complexityzoo.net/Complexity_Zoo:S#sqg)

### StoqMA — Stoquastic MA
验证者电路仅 {X, CX, CCX} 门、初态 |0⟩/|+⟩、Hadamard 基测量的 MA（ stoquastic——无符号障碍，量子蒙特卡洛可模拟的领地）。有自然完全问题；横场 Ising 模型完全（BH16）；无强误差缩减（AGL21），猜想有之则 = MA。
- [原文](https://complexityzoo.net/Complexity_Zoo:S#stoqma)

### SUBEXP — Deterministic Subexponential-Time
∩_{ε>0} DTIME(2^{n^ε})（算法可随 ε 变）。
- 主题章 [01-时间类](../01-时间类.md) · [原文](https://complexityzoo.net/Complexity_Zoo:S#subexp)

### symP — Alternate Name for S₂P
S₂P 别名条目。
- [原文](https://complexityzoo.net/Complexity_Zoo:S#symp)

### SZK — Statistical Zero Knowledge
统计零知识：与全能证明者交互后，除答案外**统计上什么都学不到**（视图可被模拟）（GMR89 引入 ZK 概念）。= HVSZK（GSV98）；有自然完全问题（统计距离 SD、熵差熵逼近）；SZK 内有平均困难语言 ⇒ 单向函数存在（Ost91）。
- 主题章 [05-交互证明与计数](../05-交互证明与计数.md) · [原文](https://complexityzoo.net/Complexity_Zoo:S#szk)

### SZK_h — SZK With Limited Help
双方可访问可信第三方串的 SZK（BG03）。= SZK。
- [原文](https://complexityzoo.net/Complexity_Zoo:S#szkh)

---

## T（11 条）

### TALLY — Tally Languages
yes 实例全形如 0^n（一元编码）。TALLY ∩ NPC ≠ ∅ ⇒ P = NP（Mah82）。含于 SPARSE。
- [原文](https://complexityzoo.net/Complexity_Zoo:T#tally)

### TC — Threshold Circuits
多项式大小、深度 O(log^i n)、含 majority 门的电路塔（MAJ 可换 THR/MOD_{p_n} 等价）。TC^i ⊇ AC^i（乃至 ACC^i）、⊆ NC^{i+1}——**NC = AC = TC**。
- 主题章 [03-电路类](../03-电路类.md) · [原文](https://complexityzoo.net/Complexity_Zoo:T#tc)

### TC⁰ — Constant-Depth Threshold Circuits
常数深度阈值电路——**神经网络的最接近复杂度类化身**。含 ACC⁰；含于 NC¹；深度 3 严格强于深度 2（HMP+93）；整数除法在 U_D-uniform TC⁰ 且 AC⁰ 归约下完全（Hes01，承 BCH86/CDL01）；**TC⁰ =? NC¹ 是电路复杂度最著名的 open 之一**（牵动 CH =? PSPACE）。
- 主题章 [03-电路类](../03-电路类.md)（主角） · [原文](https://complexityzoo.net/Complexity_Zoo:T#tc0)

### TC⁰(FOLL) — TC⁰ reducible to FOLL
TC⁰ Turing 归约到 FOLL 的类。阿贝尔群 G 与任意群 H（乘法表给入）的同构判定在内（CTW13）。
- [原文](https://complexityzoo.net/Complexity_Zoo:T#tc0foll)

### TC¹ — Log-depth Threshold Circuits
对数深度阈值电路（含于 CL——催化空间）。等价于 mod p_n 的算术 AC¹ 类比（RT92）。
- [原文](https://complexityzoo.net/Complexity_Zoo:T#tc1)

### TFNP — Total Function NP
全函数 NP：F(x,y) 的 y **保证存在**，找出任一即可（MP91）——"没有理由找不到"的世界，NP ∩ coNP 的函数面。子类按"为什么保证有解"分家：PPA（叶子偶数）、PPAD（有向源汇）、PPP（鸽笼）、PLS（局部最优）等。
- 主题章 [06-参数化与优化](../06-参数化与优化.md)（主角） · [原文](https://complexityzoo.net/Complexity_Zoo:T#tfnp)

### Θ₂P — Alternate name for P^NP[log]
P^NP[log] 的别名条目。
- [原文](https://complexityzoo.net/Complexity_Zoo:T#theta2p)

### TI — Tensor Isomorphism
张量同构问题类（GQ19）：多项式时间 Turing 归约到张量同构。含 GI；问题本身在 NP ∩ coAM（乃至 SZK）；代码等价、3-形式等价、class-2&指数 p 的矩阵 p-群同构等皆 TI-完全（GQ19/GQ21）；酉/正交/辛群作用版也已定义（CGQ+24）。
- 主题章 [01-时间类](../01-时间类.md)（同构问题宇宙） · [原文](https://complexityzoo.net/Complexity_Zoo:T#ti)

### TOWER — Iterated Exponential Time
DTIME(F₃(p(n)))（p 取遍初等函数，F₃=指数塔）（Sch16）。"只比 ELEMENTARY 大一点点"——但**有自然完全问题**：SFEq（无星号正则表达式等价）与 WS1S 可满足性（ELEMENTARY 和 PR 都没有完全问题）。
- 主题章 [01-时间类](../01-时间类.md)（初等之外的第一站） · [原文](https://complexityzoo.net/Complexity_Zoo:T#tower)

### TreeBQP — BQP Restricted To Tree States
每步量子态都指数接近树状态（加法+张量积的多项式树）的 BQP（Aar03b）。含 BPP；含于 BQP 与 PH 第三层——为 BQP ≠ TreeBQP 提供弱证据。
- 主题章 [04-随机与量子](../04-随机与量子.md) · [原文](https://complexityzoo.net/Complexity_Zoo:T#treebqp)

### TREE-REGULAR — Regular Tree-Valued Languages
输入为树的"正则语言"（自叶向根的树自动机，Koz92）。
- [原文](https://complexityzoo.net/Complexity_Zoo:T#treeregular)

---

## U（14 条）

### UAM^cc — Unambiguous Arthur-Merlin Communication Complexity
每个 yes 输入与随机结果对应唯一可接受证明的 AM^cc。不含 NP^cc；⊄ SBP^cc（GPW16a/GLM+15）；含于 PostBPP^cc。
- [原文](https://complexityzoo.net/Complexity_Zoo:U#uamcc)

### UAP — Unambiguous Alternating Polynomial-Time
每个存在量词至多一条 yes 路径、全称量词至多一条 no 路径的 AP（NR98）。含 UP 与图同构；UAP^UAP = UAP；虽 AP = PSPACE，UAP ⊆ SPP 远小。
- [原文](https://complexityzoo.net/Complexity_Zoo:U#uap)

### UCC — Unique Connected Component
L-归约到"无向图是否有唯一连通分量"的类。**= L**（Rei04）；有向版 = NL。
- 主题章 [02-空间类](../02-空间类.md) · [原文](https://complexityzoo.net/Complexity_Zoo:U#ucc)

### UCFL — Unambiguous CFL
每词恰一个最左推导的文法给出的 CFL。严格含 DCFL、严格含于 CFL。
- [原文](https://complexityzoo.net/Complexity_Zoo:U#ucfl)

### UE — Unambiguous E
E 的 UP 版。
- [原文](https://complexityzoo.net/Complexity_Zoo:U#ue)

### UL — Unambiguous L
对 L 如 UP 对 P。有向**平面图**可达性在内（SES05）；UL = NL ⇒ FNL ⊆ #L。
- 主题章 [02-空间类](../02-空间类.md) · [原文](https://complexityzoo.net/Complexity_Zoo:U#ul)

### UL/poly — Nonuniform UL
非一致 UL。**= NL/poly**（RA00——推论：对补封闭）。
- [原文](https://complexityzoo.net/Complexity_Zoo:U#ulpoly)

### UP — Unambiguous Polynomial-Time
yes ⇔ 恰一条接受路径（Val76）。**最坏情形单向函数存在 ⟺ P ≠ UP**（GS88/Ko85）；最坏情形单向置换 ⟺ P ≠ UP ∩ coUP（HT03）；oracle 下 P = UP ≠ NP 可并存；不信有完全问题（有 oracle 证无完全集，Sip82/HH86）。
- 主题章 [01-时间类](../01-时间类.md)（密码学的复杂度地基） · [原文](https://complexityzoo.net/Complexity_Zoo:U#up)

### UP^cc — Communication Complexity UP
唯一接受计算的通信版（Yan91）。total 函数版 = P^cc；Clique-vs-Independent-Set 问题的 log² 协议本质最优（GPW15）。
- [原文](https://complexityzoo.net/Complexity_Zoo:U#upcc)

### UPostBPP^cc — Unrestricted PostBPP^cc
私随机、不计 α 的 PostBPP^cc。含 P^NPcc（故 ≠ PostBPP^cc）；含于 UPP^cc。
- [原文](https://complexityzoo.net/Complexity_Zoo:U#upostbppcc)

### UPP^cc — Unrestricted Communication Analogue of PP
私随机、接受概率仅偏 1/2 侧、不计随机位数（BFS86）。不含 ⊕P^cc（For02）、不含 PH^cc（RS10）；度量 = 符号秩的对数（PS86）。
- [原文](https://complexityzoo.net/Complexity_Zoo:U#uppcc)

### US — Unique Polynomial-Time
（原页："最美国的计数类"——unique 嘛。）yes ⇔ 恰一条接受路径（多路径合法，只是判为 no）（BG82）。含 coNP。
- [原文](https://complexityzoo.net/Complexity_Zoo:U#us)

### USBP^cc — Unrestricted SBP^cc
私随机不计 α 的 SBP^cc。= SBP^cc（GLM+15）。
- [原文](https://complexityzoo.net/Complexity_Zoo:U#usbpcc)

### UWAPP^cc — Unrestricted WAPP^cc
私随机不计 α 的 WAPP^cc。可被 WAPP^cc（稍大 ε）高效模拟（GLM+15）。
- [原文](https://complexityzoo.net/Complexity_Zoo:U#uwappcc)

---

## V（7 条）

### VC_k — Verification Class With Circuit of Depth k
按验证方式分层的语言类（HN06）：VC₀=可压缩、VC₁=局部验证、VC_{k≥2}=深度 k 电路验证。VC₀ ⊆ VC_OR ⊆ VC₁ ⊆ VC₂ ⊆ …
- [原文](https://complexityzoo.net/Complexity_Zoo:V#vck)

### VC_OR — Verification Class With OR
可表示为 m 个 SAT 实例之 OR 的验证类（HN06）。
- [原文](https://complexityzoo.net/Complexity_Zoo:V#vcor)

### VNC_k — Valiant NC Over Field k
Valiant 代数复杂度的并行版（深度 polylog 的直线程序）。**VNC = VP**（VSB+83）——代数世界里并行与串行无差（对比布尔世界 NC =? P）。
- [原文](https://complexityzoo.net/Complexity_Zoo:V#vnc)

### VNP_k — Valiant NP Over Field k
Valiant 代数版"NP"：多项式 p ∈ VP 对 {0,1} 求和得到目标 q。permanent 是 VNP-完全（Valiant）——**代数世界的 #P-完全**；VP =? VNP 是代数复杂度的 P vs NP；VP = VNP ⇒（布尔侧）NC³/poly = P/poly = NP/poly = PH/poly 且 #P/poly = FP/poly，PH 塌到 Σ₂P。
- 主题章 [05-交互证明与计数](../05-交互证明与计数.md)（代数计数世界） · [原文](https://complexityzoo.net/Complexity_Zoo:V#vnp)

### VP_k — Valiant P Over Field k
Valiant 代数 P：多项式大小直线程序（+、−、×）可算的多项式族（非一致）（Val79b）。行列式在 VP；含 VNC；含于 VNP 与 VQP。
- 主题章 [03-电路类](../03-电路类.md)（代数电路） · [原文](https://complexityzoo.net/Complexity_Zoo:V#vp)

### VPL — Visibly Pushdown Languages
可见下推语言：压/弹由特殊字母触发（输入里"看得见"）（AM04）。非确定性不增能力、对全部布尔运算封闭；严格含 REG、严格含于 DCFL——**XML 解析的理论根基**。
- [原文](https://complexityzoo.net/Complexity_Zoo:V#vpl)

### VQP_k — Valiant QP Over Field k
拟多项式代数版。行列式 VQP-完全（qp-投影下）；**行列式是否 VP-完全 open**——代数复杂度的悬念。
- [原文](https://complexityzoo.net/Complexity_Zoo:V#vqp)

---

## W（11 条）

### W[1] — Weighted Analogue of NP
固定参数可归约到 Weighted-3SAT（Hamming 权 k 的满足赋值）的类（DF99）。**FPT = W[1] ⇒ NP ⊆ DTIME(2^{o(n)})**——W[1] 是参数化世界的"NP"；clique 是 W[1]-完全的典范。
- 主题章 [06-参数化与优化](../06-参数化与优化.md)（主角） · [原文](https://complexityzoo.net/Complexity_Zoo:W#w1)

### WAPP — Weak Almost-Wide PP
#P 函数落在 2^{p} 的 (1±ε)/2 邻域（BGM02）。含于 AWPP 与 SBP。
- [原文](https://complexityzoo.net/Complexity_Zoo:W#wapp)

### WAPP^cc — Communication Complexity WAPP
yes 接受率 ∈ [(1−ε)α, α]、no ∈ [0, α]。ε 不可高效放大（GLM+15）；度量 = 单侧光滑矩形界 / 近似非负秩（KMSY14）。
- [原文](https://complexityzoo.net/Complexity_Zoo:W#wappcc)

### WHILE — While programs and some restrictions
理论程序语言 WHILE（Jon98）：**语法上保证多项式时间**——写程序即证复杂度；语法限制版恰为 L。P 的语言化身。
- 主题章 [07-复杂度→代码](../07-复杂度→代码.md)（语言保证复杂度的范式） · [原文](https://complexityzoo.net/Complexity_Zoo:W#while)

### WLC⁰ — Linear Wires Constant-Depth Circuits
线性数目**线**、常数深度无界扇入电路。含于 LC⁰（故严格含于 AC⁰）。
- [原文](https://complexityzoo.net/Complexity_Zoo:W#wlc0)

### W[P] — Weighted Circuit Satisfiability
参数化归约到 Weighted-Circuit-SAT（不限深电路、权 k 赋值）的类（DF99）。含 W[SAT]——参数化塔顶。
- 主题章 [06-参数化与优化](../06-参数化与优化.md) · [原文](https://complexityzoo.net/Complexity_Zoo:W#wp)

### WPP — Wide PP
no ⇔ 接受数=拒绝数、yes ⇔ 差恰为 FP 可算的 f(x)（FFK94）。含于 C_=P ∩ coC_=P 与 AWPP；含 SPP 与 LWPP。
- [原文](https://complexityzoo.net/Complexity_Zoo:W#wpp)

### W[SAT] — Weighted Satisfiability
参数化归约到 Weighted-SAT（不限深公式）的类（DF99）。含全体 W[t]；含于 W[P]。
- [原文](https://complexityzoo.net/Complexity_Zoo:W#wsat)

### W[*] — Union of W[t]'s
全体 W[t] 之并。
- [原文](https://complexityzoo.net/Complexity_Zoo:W#wstar)

### W^*[t] — W[t] With Parameter-Dependent Depth
深度可随 k 变的 W[t]。W^*[1]=W[1]（DFT96）、W^*[2]=W[2]（DF97），更大 t open。
- [原文](https://complexityzoo.net/Complexity_Zoo:W#wstart)

### W[t] — Nondeterministic Fixed-Parameter Hierarchy
weft-t（路径上无界扇入门 ≤t 个）电路的加权可满足性塔（DF99）。FPT ⊆ W[1] ⊆ W[2] ⊆ … ⊆ W[SAT] ⊆ W[P]——**参数化世界的层谱**；每层有典范完全问题（clique 在 W[1]、dominating set 在 W[2]）。
- 主题章 [06-参数化与优化](../06-参数化与优化.md)（主角） · [原文](https://complexityzoo.net/Complexity_Zoo:W#wt)

---

## X（6 条）

### XL — Fixed-Parameter Logspace for Each Parameter
空间 O(f(k)·log n)、算法可随 k 变（参数化逐片版 L）。完全问题：k 头两向 DFA 接受问题。
- [原文](https://complexityzoo.net/Complexity_Zoo:X#xl)

### XNL — Fixed-Parameter Nondeterministic Logspace
XL 的非确定版（对 XL 如 NL 对 L）。完全问题：k 头两向 NFA 接受问题。
- [原文](https://complexityzoo.net/Complexity_Zoo:X#xnl)

### XNLP — Fixed-Parameter Nondeterministic Logspace and Polytime
空间 O(f(k)log n) **且**时间 O(f(k)n^c) 的非确定参数化类。含于 XNL；非确定使它逃出 FPT——参数化对数空间理论的新贵。
- [原文](https://complexityzoo.net/Complexity_Zoo:X#xnlp)

### XOR-MIP*[2,1] — MIP*[2,1] With 1-Bit Proofs
两证明者各发 1 比特、验证者取 XOR 的 MIP*（CHT+04，动机是 Bell/CHSH 不等式）。含于 NEXP 与 QIP[2]。
- 主题章 [05-交互证明与计数](../05-交互证明与计数.md)（Bell 不等式接口） · [原文](https://complexityzoo.net/Complexity_Zoo:X#xormipstar21)

### XP — Fixed-Parameter Tractable for Each Parameter
时间 O(|x|^{f(k)})、算法可随 k 变（DF99）。严格含 FPT（对角化）——参数化世界的 EXP。
- 主题章 [06-参数化与优化](../06-参数化与优化.md) · [原文](https://complexityzoo.net/Complexity_Zoo:X#xp)

### XP_uniform — Uniform XP
算法须统一（可拿 k 当输入）的 XP。FPT = XP_uniform ⇒ EPTAS = PTAS。
- [原文](https://complexityzoo.net/Complexity_Zoo:X#xpuniform)

---

## Y（7 条）

### YACC — Yet Another Complexity Class
"又一个复杂度类"——对复杂度类泛滥的讥讽用语。动物园以自嘲收录之。
- 主题章 [00-复杂度动物园地图](../00-复杂度动物园地图.md)（610 个类的自我调侃） · [原文](https://complexityzoo.net/Complexity_Zoo:Y#yacc)

### YP — Your Polynomial-Time / Yaroslav-Percival
存在多项式大小建议 s_n 使机器全对、且坏建议下只说"不知道"的类（Aaronson 博客定义，名字来历见原页）。含 ZPP 与 P^{TALLY∩NP∩coNP}；含于 NP ∩ coNP 与 YPP；= ONP ∩ coONP。
- [原文](https://complexityzoo.net/Complexity_Zoo:Y#yp)

### YP* — Yaroslav-Percival Star
s_n 可在无输入时多项式时间验证的 YP（AD14）。
- [原文](https://complexityzoo.net/Complexity_Zoo:Y#yp*)

### YPP — Yaroslav BPP
YP 的随机版（对 YP 如 MA 对 NP）。含 BPP 与 YP；含于 MA 与 P/poly。
- [原文](https://complexityzoo.net/Complexity_Zoo:Y#ypp)

### YQP — Yaroslav BQP
YP 的量子版（对 YPP 如 BQP 对 BPP、QMA 对 MA）；建议为量子态。含 BQP 与 YPP；含于 QMA 与 BQP/qpoly。
- 主题章 [04-随机与量子](../04-随机与量子.md)（量子建议的语义边界） · [原文](https://complexityzoo.net/Complexity_Zoo:Y#yqp)

### YQP* — Yaroslav BQP star
建议可验证的 YQP（AD14）。含于 APP、对 PP low（Yir24）。
- [原文](https://complexityzoo.net/Complexity_Zoo:Y#yqp*)

### YQP*/poly — YQP* With Polynomial-Size Advice
= BQP/qpoly（AD14）。
- [原文](https://complexityzoo.net/Complexity_Zoo:Y#yqp*/poly)

---

## Z（9 条）

### ZAM^cc — Zero-Information Arthur-Merlin Communication Complexity
证明分布不泄露输入信息且唯一的 AM^cc。含于 coNP^cc；每函数有 O(2^n) 上界（O(n) 是否够 open）；与密码学"私同步消息"协议近亲。
- [原文](https://complexityzoo.net/Complexity_Zoo:Z#zamcc)

### ZBQP — Strict Quantum ZPP
= RBQP ∩ coRBQP：正负见证都可 FBQP 找到的 NP ∩ coNP。无平方因子数在内（分解即双向证书）；与 EQP/ZQP 不同，**量子真机存在时它实践上推广 ZPP**（给带证明的答案）。ZBQP^ZBQP = ZBQP。
- [原文](https://complexityzoo.net/Complexity_Zoo:Z#zbqp)

### ZK — Zero-Knowledge (see CZK)
零知识总括条：从 PZK/SZK 到 CZK 及非交互各式的范式统称（GMR89 引入；GMW91 展示其普适性）。
- 主题章 [05-交互证明与计数](../05-交互证明与计数.md) · [原文](https://complexityzoo.net/Complexity_Zoo:Z#zk)

### ZP•L — Zero-Error Probabilistic L with Two-Way Randomness
随机带可反复读的零误差对数空间（对 BP•L 如 ZPP 对 BPP）。含 BPL（Nis93）；含于 RNC 与 BP•L。
- [原文](https://complexityzoo.net/Complexity_Zoo:Z#zpdotl)

### ZPE — Zero-Error Probabilistic E
2^{O(n)} 时间的 ZPP。ZPE = EE ⟺ ZPP = EXP（IKW01）。
- [原文](https://complexityzoo.net/Complexity_Zoo:Z#zpe)

### ZPP — Zero-Error Probabilistic Polynomial-Time
零误差、期望多项式时间（= RP ∩ coRP，两定义等价 Gil77）。素性检测的老家（SS77/AH87，后被 AKS 接走）；ZPP = P 是否需要超多项式电路下界未知（对比 BPP/RP——KI02）；有 oracle 使 ZPP = EXP。
- 主题章 [04-随机与量子](../04-随机与量子.md)（主角） · [原文](https://complexityzoo.net/Complexity_Zoo:Z#zpp)

### ZPP^cc — Communication Complexity ZPP
total 函数版 = P^cc；partial 函数版不含 ⊕P^cc（GPW16b）。
- [原文](https://complexityzoo.net/Complexity_Zoo:Z#zppcc)

### ZPTIME(f(n)) — Zero-Error Probabilistic f(n)-Time
f(n) 时间 ZPP。超多项式可构造 f：ZPTIME(f)^NP ⊄ P/poly（KW98）。
- [原文](https://complexityzoo.net/Complexity_Zoo:Z#zptime)

### ZQP — Zero-Error Extension of EQP
可答 yes/no/也许的量子类（错误方向概率 0、"也许" ≤1/2）（BW03/Nis02）。= RQP ∩ coRQP；含 EQP 与 ZBQP；有 oracle 使 ZQP^ZQP ⊋ ZQP。
- [原文](https://complexityzoo.net/Complexity_Zoo:Z#zqp)
