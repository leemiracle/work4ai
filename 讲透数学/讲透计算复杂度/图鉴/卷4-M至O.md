# 图鉴 · 卷4（M · N · O）

> 99 条（M 36 + N 58 + O 5） · 2026-09-06 快照自 [complexityzoo.net](https://complexityzoo.net/)。体例见[卷1](卷1-符号与A至B.md)。

---

## M（36 条）

### MA — Merlin-Arthur
Merlin（无界算力）先发多项式大小证明、Arthur 以 BPP 验证的单向协议（Bab85）。NP ⊆ MA ⊆ AM ⊆ Σ₂P；在 EXP ∉ P/poly 假设下 MA = NP；MA 无 n^k 大小算术电路。
- 主题章 [05-交互证明与计数](../05-交互证明与计数.md) · [原文](https://complexityzoo.net/Complexity_Zoo:M#ma)

### MAC⁰ — Majority of AC⁰
根上一个无界扇入 majority 门的 AC⁰。严格含于 TC⁰（ABF+94）。
- [原文](https://complexityzoo.net/Complexity_Zoo:M#mac0)

### MA^cc — Communication Complexity MA
Alice+Bob 合体当 Arthur 的通信版（Merlin 消息长度计入代价）。不含 coNP^cc（Kla03）；显式函数 MA^cc 复杂度 ω(√n) 的下界是 open。
- [原文](https://complexityzoo.net/Complexity_Zoo:M#macc)

### MA_E — Exponential-Time MA With Linear Exponent
E 版 MA。MA_E = NEE ⇒ MA = NEXP ∩ coNEXP（IKW01）。
- [原文](https://complexityzoo.net/Complexity_Zoo:M#mae)

### MA_EXP — Exponential-Time MA
EXP 版 Arthur、指数长 Merlin 消息。**有无多项式大小电路的问题**（BFT98）；oracle 下又可全有电路——相对化障碍现场。MVW99：现技术能证到的 MA_EXP 电路下界是"半指数"（f(f(n))=2^n，不可用标准渐进记号表达）。
- 主题章 [03-电路类](../03-电路类.md)（下界技术天花板） · [原文](https://complexityzoo.net/Complexity_Zoo:M#maexp)

### mAL — Monotone AL
单调交替对数空间。按定义 = mP（GS90）。
- [原文](https://complexityzoo.net/Complexity_Zoo:M#mal)

### MA_POLYLOG — MA With Polylog Verifier
Arthur 只用 polylog 时间随机访问证明的 MA（SM03）。用于证：EXP 有多项式电路 ⇒ EXP = MA。
- [原文](https://complexityzoo.net/Complexity_Zoo:M#mapolylog)

### MA' — Sparse MA
每个输入长度 n 的 Merlin 证明都属于某稀疏集 S_n 的 MA（KST93）。若 GI ∈ P/poly 则 GI 补在 MA'。
- [原文](https://complexityzoo.net/Complexity_Zoo:M#maprime)

### MaxNP — Maximization NP
对 NP 如 MaxSNP 对 SNP。PTAS 归约闭包 = APX（KMS+99/CT94）。
- 主题章 [06-参数化与优化](../06-参数化与优化.md) · [原文](https://complexityzoo.net/Complexity_Zoo:M#maxnp)

### MaxPB — MaxNP Polynomially Bounded
代价函数多项式有界的 MaxNP（KT94）。PTAS 归约闭包 = NPOPB（CKS+99）。
- [原文](https://complexityzoo.net/Complexity_Zoo:M#maxpb)

### MaxSNP — Maximization SNP
L-归约（线性归约，非对数空间！）到 MaxSNP₀ 的优化问题（PY88）。**Max3SAT 是 MaxSNP-完全**；MaxSNP 内问题都有固定比值近似。PTAS 归约闭包 = APX。
- 主题章 [06-参数化与优化](../06-参数化与优化.md)（PCP 之前的近似理论地基） · [原文](https://complexityzoo.net/Complexity_Zoo:M#maxsnp)

### MaxSNP₀ — Generating Class of MaxSNP
"找关系使 SNP 谓词成立的 k 元组集最大"型函数问题（PY88）。Max-Cut 可如此表达。
- [原文](https://complexityzoo.net/Complexity_Zoo:M#maxsnp0)

### mcoNL — Complement of mNL
单调 NL 的补，**≠ mNL**（GS90）——单调世界失去了 Immerman-Szelepcsényi。
- [原文](https://complexityzoo.net/Complexity_Zoo:M#mconl)

### MinPB — MinNP Polynomially Bounded
最小化版 MaxPB。
- [原文](https://complexityzoo.net/Complexity_Zoo:M#minpb)

### MIP — Multi-Prover Interactive Proof
验证者可与多个（互不通信的）证明者对质——"分开审讯室里的嫌疑人"（BGK+88）。MIP[k]=MIP[2]=MIP（k>2）；**MIP = NEXP**（BFL91，著名不相对化结果）。NE 甚至有拟线性时间验证者的 MIP（CM23）。
- 主题章 [05-交互证明与计数](../05-交互证明与计数.md)（主角） · [原文](https://complexityzoo.net/Complexity_Zoo:M#mip)

### MIP_EXP — Exponential-Time MIP
MIP 的指数版。非相对化世界 = NEEXP；oracle 下 = P/poly ∩ P^NP ∩ ⊕P（BFT98）。
- [原文](https://complexityzoo.net/Complexity_Zoo:M#mipexp)

### MIP^ns — MIP with Non-Signaling Provers
证明者可用非定域（no-signaling）策略。2 证明者版 = PSPACE（Ito10）；polylog 证明者版 = EXP（KRR13）。
- [原文](https://complexityzoo.net/Complexity_Zoo:M#mipns)

### MIP* — MIP With Entangled Provers
证明者可共享任意多纠缠量子比特（验证者与消息仍经典，CHT+04）。**2012：NEXP ⊆ MIP*（IV12）；2020：MIP* = RE（JNVWY20）**——纠缠让"分而治之的审讯"彻底失效，可判定性边界被击穿；顺带推翻了 Connes 嵌入猜想。QMIP = MIP*（RUV12）。
- 主题章 [05-交互证明与计数](../05-交互证明与计数.md)（近年前沿主角） · [原文](https://complexityzoo.net/Complexity_Zoo:M#mipstar)

### (M_k)P — Acceptance Mechanism by Monoid M_k
各计算路径输出幺半群 M_k 的元素，接受 ⇔ 乘积为单位元（Her97）。G 非可解群（如 S₅）⇒ (G)P = PSPACE；(Z_k)P = coMod_kP。
- [原文](https://complexityzoo.net/Complexity_Zoo:M#mkp)

### mL — Monotone L
单调对数宽、多项式大小分层电路。严格含 mNC¹（GS91）；含于 mNL 与 mcoNL（非一致版）。
- [原文](https://complexityzoo.net/Complexity_Zoo:M#ml)

### MM — Problems reducible to matrix multiplication
线性时间归约到方阵乘法的问题集。最优算法 O(n^{2.376})（Coppersmith–Winograd）；平凡下界 Ω(n²)。
- 主题章 [07-复杂度→代码](../07-复杂度→代码.md) · [原文](https://complexityzoo.net/Complexity_Zoo:M#mm)

### MMSNP — Monadic Monotone SNP
SNP 的单调单原子限制（FV93）。疑似二分法（无 NP-中间语言）；疑似恰好捕获固定模板 CSP。
- [原文](https://complexityzoo.net/Complexity_Zoo:M#mmsnp)

### mNC¹ — Monotone NC¹
只用 AND/OR 的 NC¹ 电路。严格含于 mL 与 mNL（KW88/GS91）；严格含 mTC⁰（Yao89）。
- 主题章 [03-电路类](../03-电路类.md)（单调电路下界谱系） · [原文](https://complexityzoo.net/Complexity_Zoo:M#mnc1)

### mNL — Monotone NL
单调非确定对数空间。≠ mcoNL（GS90）；严格含 mNC¹（KW88）。
- [原文](https://complexityzoo.net/Complexity_Zoo:M#mnl)

### mNP — Monotone NP
yes 可在 mP 中验证（单调性只约束输入位、不管猜测位）。"平凡"地恰为 NP 中单调问题全体；严格含 mP（Raz85）。
- [原文](https://complexityzoo.net/Complexity_Zoo:M#mnp)

### Mod_kL — Mod-k L
接受路径数 ≡0 (mod k) ⇔ no。素数 k：含 SL（KW93）；Mod_kL^{Mod_kL} = Mod_kL（HRV00）；含 LogFew（k>1）。
- [原文](https://complexityzoo.net/Complexity_Zoo:M#modkl)

### Mod_kP — Mod-k Polynomial-Time
NP 机接受路径数被 k 整除 ⇔ no（CH89/Her90）。Mod₂P = ⊕P；每个 Mod_kP 含图同构（AK02）；Mod_kP = 素因子 Mod_pP 之并；k 非素数幂时 oracle 下不对交/补封闭（BBR94）。
- 主题章 [05-交互证明与计数](../05-交互证明与计数.md) · [原文](https://complexityzoo.net/Complexity_Zoo:M#modkp)

### ModL — Mod L
GapL 函数 f 与 FL 函数 g（g(x)=0^{p^α}）满足 x∈L ⇔ f(x) ≡ 0 (mod |g(x)|)（AV04）。FL^ModL = FL^GapL。
- [原文](https://complexityzoo.net/Complexity_Zoo:M#modl)

### ModP — Mod_kP With Arbitrary k
k 随输入可变（0^k 多项式时间可算）的 Mod_kP。含于 AmpMP（KT96）。
- [原文](https://complexityzoo.net/Complexity_Zoo:M#modp)

### ModPH — Modular Counting Hierarchy
P 在 ∃、∀、Mod_k 算子下的闭包（GKR+95）。含 PH 与各 Mod_kP；含于且 low 于 AmpMP 与 MP。素数 m：ModPH_m = BP·Mod_mP（Toda 定理推论）。
- [原文](https://complexityzoo.net/Complexity_Zoo:M#modph)

### ModZ_kL — Restricted Mod_kL
yes ⇔ 接受路径数 ≢0 (mod k)、no ⇔ 无接受路径（BDH+92）。含 LogFewNL（k>1）；含于 Mod_kL 与 NL。
- [原文](https://complexityzoo.net/Complexity_Zoo:M#modzkl)

### mP — Monotone P
单调（0 输入能转则 1 输入也能转）非确定图灵机 + 交替机定义的多项式类（GS90）：mP = mAL。单调化的代价惨重：存在单调且在 P 中的问题需超多项式大小单调电路（Raz85b）——mP ⊊ MONO ∩ P。
- 主题章 [03-电路类](../03-电路类.md)（单调下界的意义） · [原文](https://complexityzoo.net/Complexity_Zoo:M#mp)

### MP — Middle-Bit P
#P 函数 f(x) 的**中间位**为 1 ⇔ yes（GKR+95）。含 AmpMP 与 ModPH（二者对其 low）；含于 P^#P[1]；MP^ModP = MP^#P（KT96）。
- 主题章 [05-交互证明与计数](../05-交互证明与计数.md) · [原文](https://complexityzoo.net/Complexity_Zoo:M#mp2)

### MPC — Monotone Planar Circuits
单调分层平面电路（可平面嵌入无交叉、有界扇入 AND/OR，DC89）。可设宽 n、深 n³（BLM+99）。
- [原文](https://complexityzoo.net/Complexity_Zoo:M#mpc)

### mP/poly — Monotone P/poly
无非门的非一致多项式电路（GS90 定义允许整取反输入）。
- [原文](https://complexityzoo.net/Complexity_Zoo:M#mppoly)

### mTC⁰ — Monotone TC⁰
无 NOT 的 TC⁰。严格含于 mNC¹（Yao89）。
- [原文](https://complexityzoo.net/Complexity_Zoo:M#mtc0)

---

## N（58 条）

### naCQP — non-adaptive Collapse-free Quantum Polynomial time
PDQP 的会议版别名（ABFL14）。
- [原文](https://complexityzoo.net/Complexity_Zoo:N#naCQP)

### NAuxPDA^p — Nondeterministic Auxiliary Pushdown Automata
对数空间+多项式时间+辅助下推的非确定机。**= LOGCFL**（Sud78）。
- [原文](https://complexityzoo.net/Complexity_Zoo:N#nauxpdap)

### NC — Nick's Class
（纪念 Nick Pippenger。）NC^i = 多项式大小、深度 O(log^i n)、扇入 2 的均匀电路族；NC 为其并。NC = AC；含 NL（NL ⊆ NC²）；描述复杂度 FO[(log n)^{O(1)}]。随机 oracle 下 NC^A ⊊ P^A 概率 1（Mil92）。**"高效并行计算"的复杂度化身**。
- 主题章 [03-电路类](../03-电路类.md)（并行谱系主角） · [原文](https://complexityzoo.net/Complexity_Zoo:N#nc)

### NC⁰ — Level 0 of NC
每个输出位只依赖常数个输入位（通常谈函数版）。**存在 NC⁰ 的单向函数与伪随机生成器**（AIK04，每输出位仅依赖 4 个输入位；依赖 2 位不可能，3 位 open）——密码学最底座的惊喜。
- 主题章 [03-电路类](../03-电路类.md) · [原文](https://complexityzoo.net/Complexity_Zoo:N#nc0)

### NC¹ — Level 1 of NC
深度 O(log n) 扇入 2 电路 = 多项式大小公式。**= 5-PBP**（Barrington 定理，宽度 5 分支程序模拟公式——宽度 5 必要除非 NC¹ = ACC⁰）；3 量子比特（1 纯态 2 最大混合）即可模拟（ASV00）；含 TC⁰ 与整数除法（BCH86）；U_{E*}-uniform NC¹ = ALOGTIME。
- 主题章 [03-电路类](../03-电路类.md)（Barrington 奇迹主角） · [原文](https://complexityzoo.net/Complexity_Zoo:N#nc1)

### NC² — Level 2 of NC
含 AC¹ 与 DET（都含 NL）。截至 2022-06 尚不知 NC² 中有不在 AC¹∪DET 的问题（cstheory 提问）——塔上层的空旷。
- [原文](https://complexityzoo.net/Complexity_Zoo:N#nc2)

### NE — Nondeterministic E
NTIME(2^{O(n)})。P^NE = NP^NE（Hem89）；有拟线性时间验证者的 MIP（CM23）。
- [原文](https://complexityzoo.net/Complexity_Zoo:N#ne)

### Nearly-P — Languages Superpolynomially Close to P
每层 n 与某 P 语言至多差 2^n/n^k 个输入的问题（NS05/Yam99）——"离 P 只差超多项式"地带。
- [原文](https://complexityzoo.net/Complexity_Zoo:N#nearlyp)

### NEE — Nondeterministic EE
NTIME(2^{2^{O(n)}})。MA_E = NEE ⇒ MA = NEXP ∩ coNEXP（IKW01）。
- [原文](https://complexityzoo.net/Complexity_Zoo:N#nee)

### NEEE — Nondeterministic EEE
NTIME(2^{2^{2^{O(n)}}})。
- [原文](https://complexityzoo.net/Complexity_Zoo:N#neee)

### NEEXP — Nondeterministic EEXP
NTIME(2^{2^{p(n)}})。= MIP_EXP（非相对化）。
- [原文](https://complexityzoo.net/Complexity_Zoo:N#neexp)

### NE/poly — Nonuniform NE
含 coNE（如 NEXP/poly 含 coNEXP）。
- [原文](https://complexityzoo.net/Complexity_Zoo:N#nepoly)

### NEXP — Nondeterministic EXP
NTIME(2^{p(n)})。**= MIP**（BFL91，并非对所有 oracle 成立）；⊆ MIP*（IV12）；NEXP ∈ P/poly ⟺ NEXP = MA（IKW01）；KI02：P=RP ⇒ NEXP 无多项式算术电路；实数加法理论对其困难（FR74）。
- 主题章 [05-交互证明与计数](../05-交互证明与计数.md) · [原文](https://complexityzoo.net/Complexity_Zoo:N#nexp)

### NEXP/poly — Nonuniform NEXP
含 coNEXP（folklore）。
- [原文](https://complexityzoo.net/Complexity_Zoo:N#nexppoly)

### NIPZK — Non-Interactive PZK
非交互完美零知识（BFM88/DDPY98，M08）。含于 PZK 与 coSBP；完全问题 Uniform(UN)；有 oracle 与 PZK/coNIPZK/SBP 分离。
- [原文](https://complexityzoo.net/Complexity_Zoo:N#nipzk)

### NIQSZK — Non-Interactive QSZK
QSZK 的非交互版（Kob02）。完全问题：电路制备态与最大混合态的迹距离 ≥2/3 还是 ≤1/3。
- [原文](https://complexityzoo.net/Complexity_Zoo:N#niqszk)

### NISZK — Non-Interactive SZK
非交互统计零知识（DDP+98）。含于 SZK；有自然完全问题：SDU（与均匀分布统计距离）与 EA（熵逼近）；NISZK = SZK ⟺ NISZK 对补封闭。
- 主题章 [05-交互证明与计数](../05-交互证明与计数.md) · [原文](https://complexityzoo.net/Complexity_Zoo:N#niszk)

### NISZK_h — NISZK With Limited Help
带有限帮助的非交互 SZK（BG03）。含 GI；完全问题：两电路值域几乎相等/几乎不相交。
- [原文](https://complexityzoo.net/Complexity_Zoo:N#niszkh)

### NL — Nondeterministic Logarithmic-Space
对 L 如 NP 对 P。**= coNL**（Imm88/Sze87 突破）；⊆ LOGCFL、NC²、UL/poly；有向图可达性 FO-归约完全；= SO(krom) = FO(TC)。二部图完美匹配判定对 NL 难（KUW86）。
- 主题章 [02-空间类](../02-空间类.md)（主角） · [原文](https://complexityzoo.net/Complexity_Zoo:N#nl)

### NLIN — Nondeterministic LIN
LIN 的非确定版。
- [原文](https://complexityzoo.net/Complexity_Zoo:N#nlin)

### NLO — NL Optimization Problems
对数空间优化问题类（TAN07）：对 NPO 如 OptL 对"结构化/非结构化"。对数空间近似类成层级 ⟺ L ≠ NL。
- [原文](https://complexityzoo.net/Complexity_Zoo:N#nlo)

### NLOG — NL With Nondeterministic Oracle Tape
oracle 时代价可在单向带上非确定性书写的 NL 变体（LL76）。虽 NLOG ⊆ P，却有 oracle 使其不然——oracle 访问机制的定义要小心。
- [原文](https://complexityzoo.net/Complexity_Zoo:N#nlog)

### NL/poly — Nonuniform NL
非一致 NL。含于 ⊕L/poly 与 SAC¹；**= UL/poly**（RA00）。
- [原文](https://complexityzoo.net/Complexity_Zoo:N#nlpoly)

### NLT — Nearly Linear Time
RAM 上 n(log n)^{O(1)} 时间的函数类（GS89）。
- [原文](https://complexityzoo.net/Complexity_Zoo:N#nlt)

### NMCL — Nondeterministic Moore-Crutchfield Languages
QRL 的别名（Yakaryilmaz-Say）。勿与 NQL（量子有限自动机版）混淆。
- [原文](https://complexityzoo.net/Complexity_Zoo:N#nmcl)

### NNC(f(n)) — NC with O(f(n)) Nondeterministic Gates
带 O(f(n)) 个非确定门的 NC（Wol94）。NNC(poly)=NP、NNC(log)=NC、NNC(polylog) ⊆ DSPACE(polylog)。
- [原文](https://complexityzoo.net/Complexity_Zoo:N#nnc)

### NNLT — Nondeterministic Nearly Linear Time
非确定 RAM 上 n(log n)^{O(1)}。= NQL（GS89）。
- [原文](https://complexityzoo.net/Complexity_Zoo:N#nnlt)

### NONE — The Empty Class
不含任何语言的类（ALL 的对立面，但 ≠ coALL = ALL；对多项式 Turing 归约封闭 :-)——动物园原页的数学幽默）。= SPARSE ∩ coSPARSE = TALLY ∩ coTALLY。
- 主题章 [00-复杂度动物园地图](../00-复杂度动物园地图.md) · [原文](https://complexityzoo.net/Complexity_Zoo:N#none)

### NP — Nondeterministic Polynomial-Time
"破灭的希望与闲置的梦想之类"（原页语）。yes ⇔ 存在可 P 验证的多项式长证明。P vs NP：所有现有技术相对化，成立与否须待"非自然"的证明技术——有人提议得动用代数几何级的传统数学（MS02/Reg02）。
- 主题章 [01-时间类](../01-时间类.md)（主角） · [原文](https://complexityzoo.net/Complexity_Zoo:N#np)

### NPC — NP-Complete
NP 中最难者：Karp（多一）归约与 Cook（Turing）归约为准。BKS95：若能对任意 k 个布尔公式在多项式时间内排除 2^k 种可满足组合中的哪怕一种，则 P = NP。
- 主题章 [01-时间类](../01-时间类.md)（Cook-Levin 主场） · [原文](https://complexityzoo.net/Complexity_Zoo:N#npc)

### NP_C — NP Over The Complex Numbers
复数域图灵机版 NP（BCS+97）。P_C =? NP_C 未知；若 P/poly ≠ NP/poly 则 P_C ≠ NP_C；构造整数所需加减乘次数的 polylog 下界 ⇒ P_C ≠ NP_C。
- [原文](https://complexityzoo.net/Complexity_Zoo:N#npc2)

### NP^cc — Communication Complexity NP
非确定通信版。EQUALITY 使其 ≠ P^cc、≠ coNP^cc、不含 BPP^cc；SET-INTERSECTION 为典范完全问题；度量 = 通信矩阵 1-格矩形覆盖数的对数。
- [原文](https://complexityzoo.net/Complexity_Zoo:N#npcc)

### NPI — NP-Intermediate
NP 中既非 NP-完全也非 P 的问题集（疑含分解与图同构）。**P ≠ NP ⇒ NPI 非空且含无限多个多项式等价类**（Ladner 定理）。
- 主题章 [01-时间类](../01-时间类.md)（Ladner 主场） · [原文](https://complexityzoo.net/Complexity_Zoo:N#npi)

### NP ∩ coNP — The intersection of NP and coNP
NP 与 coNP 之交。**含整数分解**（Pra75）；在某 NE∩coNE 难度假设下含 GI（MV99）；= P^{NP∩coNP}（Bra79）；若其中问题 NP-难（Turing）则 NP = coNP；**不信有完全问题**；= Low(NP)（Sch83）。
- 主题章 [01-时间类](../01-时间类.md) · [原文](https://complexityzoo.net/Complexity_Zoo:N#npiconp)

### (NP ∩ coNP)/poly — Nonuniform NP ∩ coNP
带建议版（单语言+建议 vs 两语言+好建议合一——两种语义！oracle 下可分）。NP ⊆ (NP∩coNP)/poly ⇒ PH 塌到 S₂P^{NP∩coNP}（CCH+01）。
- [原文](https://complexityzoo.net/Complexity_Zoo:N#npiconppoly)

### NP_k^cc — NP^cc in NOF model
k 人 number-on-forehead 版。k ≤ (1−δ)log n 时 ⊄ BPP_k^cc、≠ RP_k^cc（DP08）。
- [原文](https://complexityzoo.net/Complexity_Zoo:N#npkcc)

### NP/log — NP With Logarithmic Advice
O(log n) 建议版 NP。EXP ⊆ NP/log ⟺ EXP = P^{||NP}（FK05）。
- [原文](https://complexityzoo.net/Complexity_Zoo:N#nplog)

### NPMV — NP Multiple Value
NP 机全部接受路径输出构成的多值（可部分）函数（BLS84）。含 NPSV 与 NPMV_t。
- [原文](https://complexityzoo.net/Complexity_Zoo:N#npmv)

### NPMV-sel — NPMV Selective
NPMV 的 P-Sel 式可选版（HHN+95）。
- [原文](https://complexityzoo.net/Complexity_Zoo:N#npmvsel)

### NPMV_t — NPMV Total
处处有定义的 NPMV 多值函数。
- [原文](https://complexityzoo.net/Complexity_Zoo:N#npmvt)

### NPMV_t-sel — NPMV_t Selective
NPMV_t 的可选版（HHN+95）。
- [原文](https://complexityzoo.net/Complexity_Zoo:N#npmvtsel)

### NPO — NP Optimization
"找 n 比特串 x 最大化 FP 可算代价 C(x)"的函数问题类（ACG+99）。含 APX 与 NPOPB。
- 主题章 [06-参数化与优化](../06-参数化与优化.md) · [原文](https://complexityzoo.net/Complexity_Zoo:N#npo)

### NPOPB — NPO Polynomially Bounded
代价多项式有界的 NPO。= MaxPB 的 PTAS 归约闭包（CKS+99）。
- [原文](https://complexityzoo.net/Complexity_Zoo:N#npopb)

### NP/poly — Nonuniform NP
非一致 NP。含 AM；若含 coNP 则 PH 塌到第三层；NP/poly-自然证明在伪随机假设下无法把电路族排出 P/poly（Rud97）。
- 主题章 [03-电路类](../03-电路类.md)（Karp-Lipton 语境） · [原文](https://complexityzoo.net/Complexity_Zoo:N#nppoly)

### (NP,P-samplable) — Average NP With Samplable Distributions
分布只需多项式可采样的平均情形 NP（CDF 不必可算）。DistNP-完全 ⇒ (NP,P-samplable)-完全（IL90）。
- [原文](https://complexityzoo.net/Complexity_Zoo:N#nppsamp)

### NP_R — NP Over The Reals
实数域版 NP（BCS+97）。P_R =? NP_R 未知；实数情形多一个比较算子，与复数情形难有已知蕴含。
- [原文](https://complexityzoo.net/Complexity_Zoo:N#npr)

### NPSPACE — Nondeterministic PSPACE
**= PSPACE**（Savitch 的推论 Sav70）。但若允许向 oracle 带写无限长串则不相对化：有 oracle 使 NPSPACE ⊄ EXP（GTW+91）。
- 主题章 [02-空间类](../02-空间类.md)（Savitch 定理推论） · [原文](https://complexityzoo.net/Complexity_Zoo:N#npspace)

### NPSV — NP Single Value
所有接受路径同输出的单值 NPMV（BLS84）。FP = NPSV ⟺ P = NP。
- [原文](https://complexityzoo.net/Complexity_Zoo:N#npsv)

### NPSV-sel — NPSV Selective
NPSV 的可选版（HHN+95）。
- [原文](https://complexityzoo.net/Complexity_Zoo:N#npsvsel)

### NPSV_t — NPSV Total
处处有定义的 NPSV。含于 NPMV_t。
- [原文](https://complexityzoo.net/Complexity_Zoo:N#npsvt)

### NPSV_t-sel — NPSV_t Selective
亦称 NP-sel（HHN+95）。
- [原文](https://complexityzoo.net/Complexity_Zoo:N#npsvtsel)

### NQL — Nondet Quasi-Linear
多带非确定图灵机 n(log n)^k 时间。= NNLT；**SAT 在拟线性时间归约下 NQL-完全**（Sch78）。与下条重名无关。
- [原文](https://complexityzoo.net/Complexity_Zoo:N#nql)

### NQL — Nondeterministic Quantum Languages
Kondacs-Watrous 量子有限自动机逐步测量、正概率接受的语言类。= S^≠；勿与上一 NQL 混淆（动物园原页吐槽"不幸的撞名"）。
- [原文](https://complexityzoo.net/Complexity_Zoo:N#nql_2)

### NQP — Nondeterministic Quantum Polynomial-Time
QTM 多项式时间、Accept 态振幅非零 ⇔ yes（ADH97）。看似有精确振幅的技术麻烦，**结果 = coC_=P**（FGH+98）。
- 主题章 [04-随机与量子](../04-随机与量子.md) · [原文](https://complexityzoo.net/Complexity_Zoo:N#nqp)

### NSPACE(f(n)) — Nondeterministic f(n)-Space
非确定 f(n) 空间。**⊆ DSPACE(f²)**（Savitch 定理 Sav70，乃至 RevSPACE(f²)，CP95）；NSPACE(n^k) ⊊ NSPACE(n^{k+ε})（Iba72）。
- 主题章 [02-空间类](../02-空间类.md)（Savitch 主场） · [原文](https://complexityzoo.net/Complexity_Zoo:N#nspace)

### NT — Near-Testable
"x 与其字典序前驱 x−1 的答案是否一致"可多项式时间判定的类（GHJ+91）。含于 E 与 ⊕P；P、NT、NT*、⊕P 四者要么全等要么严格嵌套（随机 oracle 下相异）。
- [原文](https://complexityzoo.net/Complexity_Zoo:N#nt)

### NTIME(f(n)) — Nondeterministic f(n)-Time
非确定 f(n) 时间。**非确定时间谱系定理**：f(n+1)=o(g) ⇒ NTIME(f) ≠ NTIME(g)（SFM78，比确定版更强）；NTIME(n) ⊋ DTIME(n)；超多项式可构造 f：NTIME(f)^NP ⊄ P/poly（Kan82）。
- 主题章 [01-时间类](../01-时间类.md) · [原文](https://complexityzoo.net/Complexity_Zoo:N#ntime)

### NT* — Near-Testable With Forest Ordering
森林序前驱函数版 NT（GHJ+91）。含于 ⊕P；与 NT 的包含要么都严格要么都相等。
- [原文](https://complexityzoo.net/Complexity_Zoo:N#ntstar)

---

## O（5 条）

### OCL — One-Counter Languages
非确定单计数器自动机（可增减、可测零）接受的语言；等价于单元素栈字母表的下推自动机。REG ⊊ OCL ⊊ CFL；⊆ NL；{a^n b^n} 与单括号 Dyck 语言在内，双括号 Dyck 不在。（**条目注**：此条目占用了原 O₂P 的 span id `o2p`——主页的 O2P 链接已过时；对称类 O₂P 本尊见 S₂P 家族。）
- [原文](https://complexityzoo.net/Complexity_Zoo:O#o2p)

### OIP — Oblivious IP
交互时只知道输入长度、事后才见具体输入的 IP。**= IP ∩ P/poly**（GM15）。
- [原文](https://complexityzoo.net/Complexity_Zoo:O#oip)

### OMA — Oblivious MA
输入盲 MA：每个长度 n 共享一份多项式大小见证。NP ⊆ OMA ⟺ NP ⊆ P/poly；EXP ⊆ P/poly ⟺ EXP = OMA（FSW09）；BPP ⊆ OMA（GM15）。
- [原文](https://complexityzoo.net/Complexity_Zoo:O#oma)

### ONP — Oblivious NP
输入盲 NP。NP 有 n^k 电路 ⟺ ONP/1 有 n^k 电路 ⟺ NP = ONP ⟺ NP ⊆ P/poly（FSW09/GM15）。
- [原文](https://complexityzoo.net/Complexity_Zoo:O#onp)

### OptP — Optimum Polynomial-Time
取 NP 机所有接受路径输出的最大/小的函数类（Kre88）。MaxSAT（满足子句数）、最大团大小、色数都是 OptP[log n]-完全。
- [原文](https://complexityzoo.net/Complexity_Zoo:O#optp)
