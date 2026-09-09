# 图鉴 · 卷3（F · G · H · I · K · L）

> 73 条（F 32 + G 11 + H 11 + I 5 + K 1 + L 13；无 J——J 页不存在） · 2026-09-06 快照自 [complexityzoo.net](https://complexityzoo.net/)。体例见[卷1](卷1-符号与A至B.md)。

---

## F（32 条）

### FBPP — Function BPP
对 BPP 如 FNP 对 NP（FP 的随机类比）。
- [原文](https://complexityzoo.net/Complexity_Zoo:F#fbpp)

### FBQP — Function BQP
对 BQP 如 FNP 对 NP。oracle 下 PLS ⊄ FBQP（Aar03）；确定性求 mod p 的二次非剩余在内（Drp21）。
- [原文](https://complexityzoo.net/Complexity_Zoo:F#fbqp)

### FERT — Fixed Error Randomized Time
参数化随机类：(x,k) 由概率多项式时间机判定，yes 接受率 ≥ 1/2 + min(f(k), 1/|x|^c)、no ≤ 1/2（KW15）。含 BPP；含于 para-PP 与 FPERT。
- [原文](https://complexityzoo.net/Complexity_Zoo:F#fert)

### Few — FewP With Flexible Acceptance Mechanism
接受路径数多项式有界、答案由多项式谓词 Q(x,a) 判定的类（亦称 FewPaths，CH89）。含 FewP；含于 P^FewP（Kob89）与 SPP（FFK94）。
- [原文](https://complexityzoo.net/Complexity_Zoo:F#few)

### FewEXP — NEXP With Few Witnesses
yes 实例至多指数条接受路径的 NEXP。含于 MIP[NP^FewEXP]（证明者限 NP^FewEXP 的 MIP，AKS+94）；"FewEXP 搜索可 EXP 解" ⟺ "FewEXP 判定可 EXP/poly 解"（AKR+03）。
- [原文](https://complexityzoo.net/Complexity_Zoo:F#fewexp)

### FewP — NP With Few Witnesses
no 全拒绝、yes 时接受路径数多项式有界（AR88）。含于 ⊕P（CH89）；oracle 下 P、UP、FewP、NP 四者互异（Rub88）；oracle 下无 Turing-完全集（HJV93）。
- 主题章 [01-时间类](../01-时间类.md)（唯一证据谱系） · [原文](https://complexityzoo.net/Complexity_Zoo:F#fewp)

### FH — Fourier Hierarchy
多项式大小量子电路至多 k 次傅里叶变换、其余门保持计算基（Shi03）。FH₀=P，FH₁=BPP，FH₂ 含分解（Kitaev 相位估计）；层级是否无限（即便 oracle 下）是 open。
- 主题章 [04-随机与量子](../04-随机与量子.md) · [原文](https://complexityzoo.net/Complexity_Zoo:F#fh)

### FIXP — Fixed Point
不动点问题类：实例 I 对应代数电路（{+,−,×,/,max,min}）算出的连续函数 F_I，解为 F_I 的不动点（EY07）。各变体均在 PSPACE；**≥3 人纳什均衡是 FIXP-完全**；Linear-FIXP = PPAD。
- 主题章 [06-参数化与优化](../06-参数化与优化.md)（⇄ 讲透博弈论均衡计算） · [原文](https://complexityzoo.net/Complexity_Zoo:F#fixp)

### FNL — Function NL
对 NL 如 FNP 对 NP（AJ93）。若 NL = UL 则 FNL ⊆ #L。
- [原文](https://complexityzoo.net/Complexity_Zoo:F#fnl)

### FNL/poly — Nonuniform FNL
FNL 的非一致版；含于 #L/poly（RA00）。
- [原文](https://complexityzoo.net/Complexity_Zoo:F#fnlpoly)

### FNP — Function NP
函数版 NP：给 x 与多项式谓词 F(x,y)，存在 y 满足则输出任一这样的 y，否则输出 no。FP = FNP ⟺ P = NP。含 TFNP；自归约性是其基本问题——若 NE ≠ coNE 则存在 NP 问题无 FNP 问题可归约到它（BG94/Impagliazzo-Sudan）。
- 主题章 [07-复杂度→代码](../07-复杂度→代码.md) · [原文](https://complexityzoo.net/Complexity_Zoo:F#fnp)

### FO — First-Order Logic
一阶逻辑：最小逻辑类，描述复杂度之基。**FO = AC⁰**（Imm98）。输入为结构（串的位置/图的顶点），公式固定、只量词一阶变量。
- 主题章 [00-复杂度动物园地图](../00-复杂度动物园地图.md)（逻辑即复杂度） · [原文](https://complexityzoo.net/Complexity_Zoo:F#fo)

### FO(DTC) — First-Order with Deterministic Transitive Closure
带确定性传递闭包的一阶逻辑。**= L**（Imm98）。
- 主题章 [02-空间类](../02-空间类.md) · [原文](https://complexityzoo.net/Complexity_Zoo:F#fodtc)

### FO(LFP) — First-Order with Least Fixed Point
带最小不动点算子（P 只正出现保证单调、n^k 步内必达不动点）的一阶逻辑。**= P**（Imm82）；等价于 FO[n^{O(1)}]。
- 主题章 [01-时间类](../01-时间类.md)（P 的逻辑化身） · [原文](https://complexityzoo.net/Complexity_Zoo:F#folfp)

### FOLL — First-Order log log n
深度 O(log log n) 的均匀多项式 AC 电路 = FO(log log n)（BKL+00）。有限群上许多问题在内；与 L、NL 的比较未知。
- [原文](https://complexityzoo.net/Complexity_Zoo:F#foll)

### FO(PFP) — First-Order with Partial Fixed Point
带部分不动点算子（迭代至循环，循环则视为 false）的一阶逻辑。**= PSPACE**（Imm98）。
- 主题章 [02-空间类](../02-空间类.md) · [原文](https://complexityzoo.net/Complexity_Zoo:F#fopfp)

### FO[t(n)] — Iterated First-Order Logic
量词块迭代 t(n) 次的 FO。FO[log n]=NC¹、FO[(log n)^{O(1)}]=NC、FO[n^{O(1)}]=P=FO(LFP)、FO[2^{n^{O(1)}}]=PSPACE=FO(PFP)——**整个 P–PSPACE 主干在逻辑侧的翻译**。
- 主题章 [00-复杂度动物园地图](../00-复杂度动物园地图.md) · [原文](https://complexityzoo.net/Complexity_Zoo:F#fot)

### FO(TC) — First-Order with Transitive Closure
带传递闭包算子的一阶逻辑。**= NL**（Imm98）。
- 主题章 [02-空间类](../02-空间类.md) · [原文](https://complexityzoo.net/Complexity_Zoo:F#fotc)

### FP — Function Polynomial-Time
多项式时间可算函数类（或 FNP 中多项式时间可解出 y 者）。FP = FNP ⟺ P = NP；FP^NP = FP^NP[log] ⇒ P = NP（Kre88）——判定与函数版本互相咬合。
- 主题章 [07-复杂度→代码](../07-复杂度→代码.md) · [原文](https://complexityzoo.net/Complexity_Zoo:F#fp)

### FPERT — Fixed Parameter and Error Randomized Time
时间 f₁(k₁)·p(|x|)、误差随 k₂ 参数化的随机类（KW15）。含 FERT 与 FPT；含于 para-NP^PP。
- [原文](https://complexityzoo.net/Complexity_Zoo:F#fpert)

### FPL — Fixed Parameter Linear
时间 f(k)|x| 的参数化类。含于 FPT。
- [原文](https://complexityzoo.net/Complexity_Zoo:F#fpl)

### FP^NP[log] — FP With Logarithmically Many NP Queries
输出图最大团的大小对其完全。
- [原文](https://complexityzoo.net/Complexity_Zoo:F#fpnplog)

### FPR — Fixed-Parameter Randomized
对 FPT 如 RP 对 P（AR01）。若 Resolution 可自动化则 W[P] ⊆ FPR——证明系统自动化与参数化类的握手。
- [原文](https://complexityzoo.net/Complexity_Zoo:F#fpr)

### FPRAS — Fully Polynomial Randomized Approximation Scheme
#P 计数问题中可在 poly(n,1/ε,log 1/δ) 时间内 (1±ε) 乘性逼近者。**非负矩阵 permanent 在内**（JSV01）——一般 permanent #P-完全，非负情形却可随机近似。
- 主题章 [05-交互证明与计数](../05-交互证明与计数.md) · [原文](https://complexityzoo.net/Complexity_Zoo:F#fpras)

### FPT — Fixed-Parameter Tractable
(x,k) 型问题可在 f(k)·p(|x|) 时间内解（f 任意）。**参数化复杂度理论的基本类**（Downey-Fellows）。分 FPT 与 W[2] 可证"无 f(k)n^{O(1)} 大小的 CNF 证明系统"。含 FPTAS 与 EPTAS（除非 FPT = W[1]，Baz95/CC97）。
- 主题章 [06-参数化与优化](../06-参数化与优化.md)（主角） · [原文](https://complexityzoo.net/Complexity_Zoo:F#fpt)

### FPTAS — Fully Polynomial-Time Approximation Scheme
poly(n,1/ε) 时间的 (1+ε) 近似方案。含于 PTAS；含于 FPT（CC97）——**能近似的都能参数化**。
- 主题章 [06-参数化与优化](../06-参数化与优化.md) · [原文](https://complexityzoo.net/Complexity_Zoo:F#fptas)

### FPT_nu — FPT (nonuniform)
算法可随 k 变化（等价：多项式长度建议依 k 而定）的 FPT（DF99）。
- [原文](https://complexityzoo.net/Complexity_Zoo:F#fptnu)

### FPT_su — FPT (strongly uniform)
f 须递归的 FPT（DF99）。
- [原文](https://complexityzoo.net/Complexity_Zoo:F#fptsu)

### FQMA — Function QMA
输出 QMA 问题的量子证据（输出为量子态）（JWB03）。3-局部哈密顿量的态制备 FQMA-完全；与 FNP/NP 不同，FQMA 归约到 QMA 并不显然。
- [原文](https://complexityzoo.net/Complexity_Zoo:F#fqma)

### frIP — Function-Restricted IP
有"判定器"（yes 时 D^L 通过、no 时对任何 oracle 都拒绝）的问题类（BK89/BG94）。含 compIP 与 Check；含于 MIP = NEXP；若 NEE ⊄ BPEE 则 NP ∩ Coh ⊄ frIP。
- [原文](https://complexityzoo.net/Complexity_Zoo:F#frip)

### F-TAPE(f(n)) — Provable DSPACE(f(n)) For F
在形式系统 F 的公理下**可证明** O(f(n)) 空间可解的问题（Har78）。与 F-TIME 平行的结果，某些更锐。
- [原文](https://complexityzoo.net/Complexity_Zoo:F#ftape)

### F-TIME(f(n)) — Provable DTIME(f(n)) For F
在形式系统 F 下可证明 O(f(n)) 时间可解的问题（Har78）。存在递归 f 使 F-TIME(f) ⊊ DTIME(f)——**真可解 ≠ 可证明可解**（哥德尔式鸿沟在复杂度里的化身）。
- 主题章 [00-复杂度动物园地图](../00-复杂度动物园地图.md) · [原文](https://complexityzoo.net/Complexity_Zoo:F#ftime)

---

## G（11 条）

### GA — Graph Automorphism
多项式时间 Turing 归约到图自同构问题的类。含 P；含于 GI。详见 KST93。
- [原文](https://complexityzoo.net/Complexity_Zoo:G#ga)

### GAN-SPACE(f(n)) — Games Against Nature f(n)-Space
带存在与随机两种量词的 f(n) 空间机。含 NSPACE 与 BPSPACE；含于 AUC-SPACE；GAN-SPACE(log n) ⊆ P（线性规划）。
- [原文](https://complexityzoo.net/Complexity_Zoo:G#ganspace)

### GapAC⁰ — Gap #AC⁰
常数深度算术电路 + 常数 −1（比 #AC⁰ 多了减法）。logspace 一致下 = DiffAC⁰（ABL98）。
- [原文](https://complexityzoo.net/Complexity_Zoo:G#gapac0)

### GapL — Gap Logarithmic-Space
#L 函数的差闭包（对 L 如 GapP 对 P）。**行列式是 GapL-完全**（Vin91/Dam91/Tod91）。
- [原文](https://complexityzoo.net/Complexity_Zoo:G#gapl)

### GapP — Gap Polynomial-Time
NP 机接受路径数减拒绝路径数（= #P 的减法闭包，FFK94/Gup95）。PP、AWPP、WPP 等一族类的 GapP 刻画之基。
- 主题章 [05-交互证明与计数](../05-交互证明与计数.md) · [原文](https://complexityzoo.net/Complexity_Zoo:G#gapp)

### GC(s(n),C) — Guess and Check
猜 s(n) 位再以类 C 验证（CC93）。GC(p(n),P) = NP；最短蕴含词是 GC(log²n, coNP)-完全（Uma98）。
- [原文](https://complexityzoo.net/Complexity_Zoo:G#gc)

### GCSL — Growing CSL
右部严格增长（或左部为起始符）的上下文有关文法（DW86）。含于 LOGCFL；无圈 CSL 与之等价（Nie02）。
- [原文](https://complexityzoo.net/Complexity_Zoo:G#gcsl)

### GI — Graph Isomorphism
多项式时间 Turing 归约到图同构问题的类。含 GA；含于 Δ₂P；**GI 问题本身在 NP ∩ coAM（乃至 SZK）**——若 GI 是 NP-完全则 PH 塌到 Σ₂P（这就是"GI 几乎肯定不是 NP-完全"的复杂度语义）。许多问题 GI-完全：有界树宽图同构、CFG 同构（ZKT85）、半单李代数共轭（Gro12）。
- 主题章 [01-时间类](../01-时间类.md)（NP 内部结构的主角之一） · [原文](https://complexityzoo.net/Complexity_Zoo:G#gi)

### GLO — Guaranteed Local Optima
局部最优与全局最优比值常数有界的 NPO 问题（AP95）。严格含于 APX；MaxSNP ⊄ GLO（KMS+99）。
- [原文](https://complexityzoo.net/Complexity_Zoo:G#glo)

### GPCD(r(n),q(n)) — Generalized Probabilistically Checkable Debate
验证者非自适应查 O(q(n)) 轮辩论的 PCD 推广（CFL+93）。PCD(log n, q) = GPCD(log n, q)。
- [原文](https://complexityzoo.net/Complexity_Zoo:G#gpcd)

### G[t] — Stratification of FPT
深度 t 无界扇入参数化电路族可解的 (x,k) 类（DF99）。均匀 G[P] = FPT。
- [原文](https://complexityzoo.net/Complexity_Zoo:G#gt)

---

## H（11 条）

### HalfP — RP With Exactly Half Acceptance
yes ⇔ 恰一半路径接受、no 全拒绝（候选证据数限 2 的幂）。含于 RP、EP、Mod_kP（奇 k）；**Deutsch-Jozsa 算法使其含于 EQP**（BB92/BS00）——量子确定性优势的第一块试验田。
- 主题章 [04-随机与量子](../04-随机与量子.md) · [原文](https://complexityzoo.net/Complexity_Zoo:H#halfp)

### HeurBPP — Heuristic BPP
1−1/poly(n) 比例实例可被 BPP 机解的类。有严格谱系定理：HeurBPP ≠ HeurBPTIME(n^c)（FS04）。
- [原文](https://complexityzoo.net/Complexity_Zoo:H#heurbpp)

### HeurBPTIME(f(n)) — Heuristic BPTIME
HeurDTIME 的随机时间版；HeurBPP 为其多项式层并。
- [原文](https://complexityzoo.net/Complexity_Zoo:H#heurbptime)

### HeurDTIME_δ(f(n)) — Heuristic DTIME
分布问题 (L,D)：对 D 支撑内所有 x 以 f(n) 时间运行、失败概率 ≤ δ(n) 的启发式算法类（BT06）。
- [原文](https://complexityzoo.net/Complexity_Zoo:H#heurdtime)

### HeurNTIME_δ(f(n)) — Heuristic DTIME 的非确定版
NP ⊄ HeurNTIME_{1/2+1/n^a}(n^c)（任意常数 a,c，Per07）。
- [原文](https://complexityzoo.net/Complexity_Zoo:H#heurntime)

### HeurP — Heuristic P
分布问题被 P 机（带 δ 参数的启发式算法）可解的类（Imp95 称 HP；BT06 的元组式定义）。
- [原文](https://complexityzoo.net/Complexity_Zoo:H#heurp)

### HeurPP — Heuristic PP
HeurP 的 PP 版（Ill95 称 HPP）。
- [原文](https://complexityzoo.net/Complexity_Zoo:H#heurpp)

### H_kP — High Hierarchy In NP
NP 中给 Σ_kP 做 oracle 能顶到 Σ_{k+1}P 的问题（Sch83）。H₀ = NP 在 Cook 归约下的完全问题；H₁ = 强非确定归约下的完全问题。
- [原文](https://complexityzoo.net/Complexity_Zoo:H#hkp)

### HO — High-Order Logic
高阶逻辑：SO 之上再对高阶变量量化。Σ^i_j 层级满足 Σ^i_j = exp₂^{i-1}(n^{O(1)})^{Σ_{j-1}^P}（HT06）——高阶逻辑量词层数与指数时间层级对齐。
- [原文](https://complexityzoo.net/Complexity_Zoo:H#ho)

### HVPZK — Honest-Verifier PZK
诚实验证者版完美零知识。含于 PP（BHCTV17）；有 oracle 使不对补封闭。
- [原文](https://complexityzoo.net/Complexity_Zoo:H#hvpzk)

### HVSZK — Honest-Verifier SZK
诚实验证者版统计零知识。**= SZK**（GSV98）——诚实验证者假设免费。
- 主题章 [05-交互证明与计数](../05-交互证明与计数.md) · [原文](https://complexityzoo.net/Complexity_Zoo:H#hvszk)

---

## I（5 条）

### IC[log,poly] — Logarithmic Instance Complexity, Polynomial Time
每个 n 比特输入 x 都有 O(log n) 大小程序在 x 上正确作答（其他处可答"不知道"）（OKS+94）。NP ⊆ IC[log,poly] ⇒ P = NP；严格含 P/log、严格含于 P/poly。
- [原文](https://complexityzoo.net/Complexity_Zoo:I#iclogpoly)

### IOP — Interactive Oracle Proof
PCP 与 IP 的合体：多轮交互 + 验证者只随机抽查证明符号。解的类仍是 NEXP；可经 Merkle 树（BCS 编译器）转回 IP。
- 主题章 [05-交互证明与计数](../05-交互证明与计数.md) · [原文](https://complexityzoo.net/Complexity_Zoo:I#iop)

### IP — Interactive Proof Systems
概率多项式时间验证者与全能证明者多轮对话，yes 时存在策略使接受 ≥2/3、no 时任何策略接受 ≤2/3（GMR89）。**IP = PSPACE**（Shamir）——"对话的力量 = 多项式空间"；对数空间验证者版 (IP ∩ …) 见 GKR15。
- 主题章 [05-交互证明与计数](../05-交互证明与计数.md)（主角） · [原文](https://complexityzoo.net/Complexity_Zoo:I#ip)

### IPP — Unbounded IP
把 2/3−1/3 换成"严格大于/小于 1/2"的 IP。**相对所有 oracle 都 = PSPACE**（CCG+94）——而 IP 相对随机 oracle 严格小于 PSPACE，作者以此反驳随机 oracle 假设：定义的微小改动能剧变类的相对化行为。
- [原文](https://complexityzoo.net/Complexity_Zoo:I#ipp)

### IP[polylog] — IP With Polylog Rounds
AM[polylog] 的别名条目。
- [原文](https://complexityzoo.net/Complexity_Zoo:I#ippolylog)

---

## K（1 条）

### K — Feasibly Recursive Functions
基本整数运算（+, −, ×, ⌊x/y⌋）在复合与多项式长和/积下的闭包（Con73，曾误称与 FP 重合）。= U_D-uniform FTC⁰（Hes01）。
- [原文](https://complexityzoo.net/Complexity_Zoo:K#k)

---

## L（13 条）

### L — Logarithmic Space
对数空间（输入不计入）可解的判定问题。含 NC¹；**Reingold：L = SL**（Rei04）——无向图连通性确定对数空间可解；L = FO(DTC)（Imm83）。
- 主题章 [02-空间类](../02-空间类.md)（主角） · [原文](https://complexityzoo.net/Complexity_Zoo:L#l)

### L/poly — Nonuniform Logarithmic Space
非一致对数空间。**= PBP**（多项式大小分支程序，Cob66）。
- [原文](https://complexityzoo.net/Complexity_Zoo:L#l/poly)

### LC⁰ — Linear Size Constant-Depth Circuits
线性数目**门**、常数深度无界扇入电路。严格含于 AC⁰（CR96）。
- [原文](https://complexityzoo.net/Complexity_Zoo:L#lc0)

### LH — Logarithmic Time Hierarchy
对数时间交替机的 alternation 层级。**LH = AC⁰ = FO**（Imm98）。
- [原文](https://complexityzoo.net/Complexity_Zoo:L#lh)

### LIN — Linear Time
线性时间。严格含于 NLIN（PPS+83）。
- [原文](https://complexityzoo.net/Complexity_Zoo:L#lin)

### L_kP — Low Hierarchy In NP
给 Σ_kP 做 oracle 毫无增益的 NP 问题（Sch83）。L₁P = NP ∩ coNP。
- [原文](https://complexityzoo.net/Complexity_Zoo:L#lkp)

### LOGCFL — Logarithmically Reducible to CFL
对数空间归约到 CFL 成员判定。= 均匀 SAC¹（Ven91）；对补封闭（BCD+89）；含 NL 与有界树宽图识别（Wan94）。
- [原文](https://complexityzoo.net/Complexity_Zoo:L#logcfl)

### LogFew — Logspace-Bounded Few
NL 机接受路径数 f(x)、答案由 L 谓词 R(x,f(x)) 判定（BDH+92）。含于 Mod_kL（k>1）。
- [原文](https://complexityzoo.net/Complexity_Zoo:L#logfew)

### LogFewNL — Logspace-Bounded FewP
NL 版 FewP。含于 ModZ_kL（k>1，BDH+92）。
- [原文](https://complexityzoo.net/Complexity_Zoo:L#logfewnl)

### LOGLOG — loglog Space
O(log log n) 空间（双向输入访问）。子对数空间类的最小非平凡层——更小只含正则语言。其交替层级无限（BGR93）。
- [原文](https://complexityzoo.net/Complexity_Zoo:L#loglog)

### LOGNP — Logarithmically-Restricted NP
∃ 大小 log n 的集合 S 使得 ∀x∃y∀j∈S: φ(I,s_j,x,y,j) 型逻辑类（PY96）。VC 维问题完全；含 LOGSNP；含于 β₂P。
- [原文](https://complexityzoo.net/Complexity_Zoo:L#lognp)

### LOGSNP — Logarithmically-Restricted SNP
LOGNP 去掉 ∀y（PY96）。若 P = LOGSNP 则 NTIME(f) ⊆ DTIME(g^{√g}) 型结论（FK97）。
- [原文](https://complexityzoo.net/Complexity_Zoo:L#logsnp)

### LWPP — Length-Dependent Wide PP
no ⇔ 接受数恰等于拒绝数；yes 时差为 FP 可算的 f(|x|)（FFK94）。对 PP 与 C_=P low；含 SPP 与图同构；含黑箱可解群的一窝问题（群交、群分解、陪集交、双陪集归属，Vin04）。
- [原文](https://complexityzoo.net/Complexity_Zoo:L#lwpp)
