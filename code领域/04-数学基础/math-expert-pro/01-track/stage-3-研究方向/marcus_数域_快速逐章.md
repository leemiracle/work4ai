# Daniel A. Marcus《数域》 · 快速逐章精读

> 基于原书：Number Fields, Universitext（Daniel A. Marcus, Springer 1977 初版 / 2018 再版）/ 读于：2026-07-03
> 定位：**以「习题驱动」著称的代数数论亲民入门经典**，把大量关键结论留作带提示的习题，逼读者亲手算出二次域类数、分圆域判别式与 $L$-函数留数，是「读 + 做」并重的最佳训练手册。
> 本文为**快速逐章精读**，全书 7 章（+ 附录习题提示），每章 1 个飞腾锚点（8 锚池用 7、弃 FP16）+ 1 个关键定理 + 1 道自测题。

---

## §0 引言：Marcus 数域是什么，为什么读它

Daniel A. Marcus《Number Fields》（Springer Universitext，1977 初版、2018 再版）是代数数论领域**最著名的「习题驱动」入门教材**，与 Janusz《Algebraic Number Fields》并列为「亲民入门双子」。Marcus 的笔法独树一帜：正文给定义与定理骨架，但**大量关键计算与证明被刻意留作带提示的习题**（书末附录给出 selected exercises 的 hints and answers）——读完一章不算完，必须亲手把 $\mathbb{Q}(\sqrt{-5})$ 的理想分解、$\mathbb{Q}(\zeta_5)$ 的判别式、$L(1,\chi_d)$ 的留数算出来，才算「学过」。这种「learning by doing」使它成为研究生 qualifying exam 的标准训练书：做完所有习题，你就拥有了完整的代数数论计算肌肉记忆。

读它的核心理由：作为数学零基础补课的工程师，**Marcus 与 Janusz 互为镜像**——Janusz 给你完整证明让你「读懂」，Marcus 把同样的内容拆成习题让你「做通」。两者覆盖面几乎重合（数域与代数整数、Galois 回顾、素数分解、类群与单位、分圆域、$L$-函数与类数公式、素数分布），但 Marcus 更紧凑（7 章 vs Janusz 8 章，省去独立局部域章，把 $p$-adic 精神融进分圆域与素数分解）、习题更密集、节奏更「上手即算」。与 Neukirch（抽象公理化、局部/全局双线类域论）相比，Marcus 完全停留在**整体代数数论 + 基础解析方法**，不碰 idèle 与类域论——这正是它适合「第一遍建手感」的原因。**最佳递进路线**：先 Marcus（或 Janusz）做习题建计算骨架 → 再 Neukirch 补局部域与类域论的系统对照 → 最后 Lang GTM110 做整合复习。

| 书 | 风格 | 严格性 | 适合谁 |
|---|---|---|---|
| **Marcus**《Number Fields》 | 习题驱动，大量带提示手算练习，证明与计算并重 | ★★★★☆ 友好 | 喜欢做题巩固、要练计算肌肉记忆的初学者 |
| **Janusz** GSM7 | 温和自学，例题丰富，证明完整不跳 | ★★★★☆ 友好 | 零基础系统自学代数数论第一本 |
| **Neukirch** G322 | 现代公理化，抽象类域论贯通局部/全局 | ★★★★★ 自洽 | 系统学数论，要统一框架与 idèle 语言 |
| **Ireland-Rosen** GTM84 | 初等优先，整体数论骨架，组合味浓 | ★★★☆☆ 平易 | 从初等数论自然过渡到代数数论 |

**阅读心法**：Marcus 不能「只读」——它是一本**半练习册**。建议每章正文读完后，至少独立完成 60% 习题（附录有提示，先别看）。Ch 1（数域与代数整数）一气建好 $\mathcal{O}_K$、迹/范数/判别式与理想唯一分解的脚手架；Ch 2（Galois 回顾）快读；Ch 3（素数分解）是计算核心甜区，Dedekind 分解定理要手算 $p=2,3,5$；Ch 4（类群与单位）用 Minkowski 几何一次焊死「类数有限 + 单位群结构」；Ch 5（分圆域）是 Ch 3 的精美应用；Ch 6（$L$-函数与类数公式）是解析高潮；Ch 7（素数分布）以 Chebotarev 密度收束。全书精读 + 做题约 50–70 小时（每周 10–20h，4–6 周）。

> **附录说明**：书末附录 Hints and Answers to Selected Exercises 是 Marcus 全书教学法的关键组成——不是答案全集，而是「关键习题的提示」，刻意点到为止。读者须靠提示补全过程，这正是「习题驱动」的收口。

---

## §1 全书 7 章骨架一览（飞腾锚点分布）

| 章 | 标题 | 核心概念 | 飞腾锚点 |
|:-:|------|---------|---------|
| 1 | Number Fields and Algebraic Integers（数域与代数整数） | $\mathcal{O}_K$、迹/范数、判别式、Dedekind 域、理想唯一分解 | **TLB 4.81× [E04]** |
| 2 | Galois Theory of Number Fields（数域的 Galois 理论回顾） | Galois 基本定理、正规闭包、Galois 表示 | **matmul 15× [V03]** |
| 3 | Decomposition of Primes（素数分解） | $(p)=\prod\mathfrak{P}_i^{e_i}$、split/inert/ramify、$\sum e_if_i=n$ | **分支预测 0.71 vs 3.14 [Lab02]** |
| 4 | The Ideal Class Group and Units（理想类群与单位群） | 类群有限、Minkowski 界、Dirichlet 单位定理、调节子 | **Schmidt 正交化** |
| 5 | Cyclotomic Fields（割圆域） | $\mathbb{Q}(\zeta_n)$、$\mathbb{Z}[\zeta_n]$、判别式、Gauss 和 | **UDOT 16.9× [E05]** |
| 6 | Dirichlet L-series and Class Number Formula（$L$-级数与类数公式） | Dirichlet $L$、Dedekind $\zeta_K$、解析类数公式 | **Iron Law <2% [Lab00]** |
| 7 | The Distribution of Primes（素数分布） | Dirichlet 等差数列素数定理、Frobenius 密度、Chebotarev | **GEMM 9.45 GFLOPS [Lab05]** |

**锚点池说明**：8 个飞腾锚点中本章用 7 个，弃用 **FP16 3.81×**——因 Marcus 全书停留在整体域、无独立 $p$-adic/局部域章（Hensel 提升不构成单章主线，相关内容散见 Ch 3/5），该锚点在 Janusz Ch 7、Neukirch Ch 3 有自然归宿。每章选 1、相邻章不重复；🟡工程类比仅供直觉，严格证明一律回原书。

---

### 第 1 章 · Number Fields and Algebraic Integers（数域与代数整数）

- **核心**：本章一气建好全书代数地基。**代数整数**是首一整系数多项式的根，数域 $K$ 的**代数整数环** $\mathcal{O}_K$ 是 $\mathbb{Z}$ 在 $K$ 中的整闭包。**迹** $\mathrm{Tr}_{K/\mathbb{Q}}(\alpha)=\sum_i\sigma_i(\alpha)$（共轭之和）、**范数** $\mathrm{N}_{K/\mathbb{Q}}(\alpha)=\prod_i\sigma_i(\alpha)$（共轭之积）、**判别式** $d_K=\det(\mathrm{Tr}(\omega_i\omega_j))$（整基 Gram 行列式）。核心事实：$\mathcal{O}_K$ 是秩 $n=[K:\mathbb{Q}]$ 的自由 $\mathbb{Z}$-模（**整基存在**），且是 **Dedekind 域**（Noether、整闭、非零素理想极大），故每个非零理想唯一分解为素理想之积。Marcus 把判别式的计算（$\mathbb{Q}(\sqrt d)$、$\mathbb{Q}(\zeta_p)$）留作习题，逼你手算建立坐标感。
- **飞腾锚点**：**TLB 4.81× [E04]** —— $\mathcal{O}_K$ 是 $\mathbb{Z}$ 的「分层扩展」：$\mathbb{Z}\subset\mathcal{O}_K$，每个理想分层落在 $\mathbb{Z}$-子模上，如 CPU 的 TLB（翻译后备缓冲）把虚拟地址分层映射到物理地址——整闭包 = 把 $\mathbb{Z}$ 的「地址空间」扩展到 $K$ 的整数层，Dedekind 域三层公理（Noether/整闭/素理想极大）是这层的「承重结构」。
  - 🟢事实：$\mathcal{O}_K\cap\mathbb{Q}=\mathbb{Z}$；$\mathcal{O}_K$ 是秩 $n$ 自由 $\mathbb{Z}$-模，判别式 $d_K$ 与整基选取无关。
  - 🟡类比：Dedekind 域 = 「可分层寻址的内存架构」，理想唯一分解 = 「每个地址可拆成页表项的素因子」。
- **关键定理**：**Dedekind 理想唯一分解定理**：设 $K$ 数域，$\mathcal{O}_K$（Dedekind 整环）的每个非零（分式）理想 $\mathfrak{a}$ 可唯一（差单位因子）写成
$$\mathfrak{a}=\mathfrak{p}_1^{e_1}\mathfrak{p}_2^{e_2}\cdots\mathfrak{p}_r^{e_r},\quad e_i\in\mathbb{Z},\ \mathfrak{p}_i\text{ 非零素理想}.$$
这是「元素不唯一分解时，理想来补救」的根本定理（$\mathbb{Z}[\sqrt{-5}]$ 是经典反例）。推论：$\mathcal{O}_K$ 是 PID $\Leftrightarrow$ 类群 $\mathrm{Cl}(K)=1$ $\Leftrightarrow$ UFD。
- **自测**：求 $\mathbb{Q}(\sqrt{-3})$ 与 $\mathbb{Q}(\sqrt{5})$ 的整数环与判别式。答：$-3\equiv1,5\equiv1\pmod4$，故 $\mathcal{O}=\mathbb{Z}[\frac{1+\sqrt d}{2}]$。$\mathbb{Q}(\sqrt{-3})$：$\omega=\frac{-1+\sqrt{-3}}{2}$（$x^2+x+1=0$，$\omega^3=1$，Eisenstein 整数），整基 $\{1,\omega\}$，$d_K=-3$。$\mathbb{Q}(\sqrt5)$：$\varphi=\frac{1+\sqrt5}{2}$（$x^2-x-1=0$，黄金比），整基 $\{1,\varphi\}$，$d_K=5$。

**迹、范数、判别式速记**（全书反复用到的三大不变量，Marcus 逼你手算 $\mathbb{Q}(\sqrt d)$）：

| 不变量 | 定义 | 性质 | 二次域 $\mathbb{Q}(\sqrt d)$ 公式 |
|---|---|---|---|
| **迹** $\mathrm{Tr}(\alpha)$ | $\sum_{i=1}^n\sigma_i(\alpha)$（共轭之和） | $\mathbb{Q}$-线性：$\mathrm{Tr}(\alpha+\beta)=\mathrm{Tr}(\alpha)+\mathrm{Tr}(\beta)$ | $\mathrm{Tr}(a+b\sqrt d)=2a$ |
| **范数** $\mathrm{N}(\alpha)$ | $\prod_{i=1}^n\sigma_i(\alpha)$（共轭之积） | 乘性：$\mathrm{N}(\alpha\beta)=\mathrm{N}(\alpha)\mathrm{N}(\beta)$ | $\mathrm{N}(a+b\sqrt d)=a^2-db^2$ |
| **判别式** $d_K$ | $\det(\mathrm{Tr}(\omega_i\omega_j))$（整基 Gram 行列式） | 与整基选取无关（差平方） | $d_K=4d$（$d\not\equiv1\pmod4$）或 $d$（$d\equiv1\pmod4$） |

核心：迹是「求和」（UDOT 累加），范数是「求积」，判别式是「内积矩阵的行列式」= 格体积²。$\alpha$ 是单位 $\Leftrightarrow\mathrm{N}(\alpha)=\pm1$。

---

### 第 2 章 · Galois Theory of Number Fields（数域的 Galois 理论回顾）

- **核心**：本章是**前置复习**，不引入新数论，而是把 Ch 3–7 要反复用的 Galois 工具整理好：有限扩张、极小多项式、分裂域、**Galois 理论基本定理**（子群↔中间域反序一一对应）、正规闭包。Marcus 先在 $\mathbb{Q}(\sqrt2)$、$\mathbb{Q}(\zeta_5)$ 上手算 Galois 群，再抽象到一般定理。核心信息：数域 $K/\mathbb{Q}$ 的 Galois 闭包 $L$ 的子群格决定 $K$ 的所有中间域，而 Ch 3 中素数 $p$ 在 $L$ 中的分解模式正是由 $\mathrm{Gal}(L/\mathbb{Q})$ 的共轭类控制的——这是 Ch 7 Chebotarev 密度的伏笔。
- **飞腾锚点**：**matmul 15× [V03]** —— 每个 $\sigma\in\mathrm{Gal}(L/K)$ 是 $L$（作为 $K$-向量空间）上的线性变换，在整基 $\{\omega_i\}$ 下表为 $n\times n$ 矩阵；Galois 群作用 = 矩阵群的子群，群运算即矩阵乘法（matmul）。
  - 🟢事实：$\sigma$ 在整基上的矩阵是整数矩阵、行列式 $=\pm1$（保体积的格自同构）；Galois 对应「正规子群↔Galois 中间域」如「分块对角化↔不变子空间」。
  - 🟡类比：子群↔子域的格 = 矩阵的不变子空间链，正规子群对应「可对角化」的对称结构。
- **关键定理**：**Galois 理论基本定理**：设 $L/K$ 有限 Galois 扩张，$G=\mathrm{Gal}(L/K)$，则中间域 $K\subseteq M\subseteq L$ 与子群 $H\le G$ 反序一一对应 $M\leftrightarrow\mathrm{Gal}(L/M)$，且 $[L:M]=|H|$，$M/K$ Galois $\Leftrightarrow$ $H\triangleleft G$。
- **自测**：$L=\mathbb{Q}(\zeta_7)$，$\mathrm{Gal}(L/\mathbb{Q})\cong(\mathbb{Z}/7)^*\cong\mathbb{Z}/6$（生成元 $\sigma_3:\zeta_7\mapsto\zeta_7^3$，$\mathrm{ord}(3\bmod7)=6$）。列出全部子群与对应中间域：$\langle\sigma_3^2\rangle\cong\mathbb{Z}/3$↔唯一的二次子域（$7\equiv3\pmod4$，应为 $\mathbb{Q}(\sqrt{-7})$）；$\langle\sigma_3^3\rangle\cong\mathbb{Z}/2$↔三次子域。验证 $\mathbb{Q}(\sqrt{-7})=\mathbb{Q}(\sqrt{(-1)^{(7-1)/2}7})$。

---

### 第 3 章 · Decomposition of Primes（素数分解：split/inert/ramify）

- **核心**：本章是全书的**计算核心**。给定素数 $p$ 与数域 $K=\mathbb{Q}(\alpha)$（$\alpha$ 极小多项式 $f$），$p$ 在 $\mathcal{O}_K$ 中的分解 $(p)=\prod_{i=1}^g\mathfrak{P}_i^{e_i}$ 由 $f(x)\bmod p$ 的因子分解控制——**Dedekind 分解定理**（$p\nmid[\mathcal{O}_K:\mathbb{Z}[\alpha]]$ 时）：若 $\bar f=\prod\bar f_i^{e_i}\in\mathbb{F}_p[x]$，$\deg\bar f_i=f_i$，则 $\mathfrak{P}_i=(p,f_i(\alpha))$，$N\mathfrak{P}_i=p^{f_i}$。基本恒等式 $\sum e_if_i=[K:\mathbb{Q}]=n$。三分类型：**分裂**（$e_i=1,g>1$）、**惯性**（$e=g=1,f=n$）、**分歧**（某 $e_i>1$）。对 Galois 扩张，**分解群** $D_{\mathfrak{P}}$、**惯性群** $I_{\mathfrak{P}}$、非分歧时的 **Frobenius** $\mathrm{Frob}_{\mathfrak{P}}(x)\equiv x^{N\mathfrak{p}}$ 登场。Marcus 把每个类型都配 $\mathbb{Q}(\sqrt d)$ 手算习题。
- **飞腾锚点**：**分支预测 0.71 vs 3.14 [Lab02]** —— 素数 $p$ 在 $K$ 中的分解模式是「分支判断」：$e>1$ 分歧（判别式整除，难预测路径，0.71 慢）、$e=1,g>1$ 分裂（多路分支）、$e=1,g=1,f=n$ 惯性（单一可预测路径，3.14 快）。Frobenius 是「分支标签」，决定 $p$ 走哪条路。
  - 🟢事实：$p$ 在 $K$ 中分歧 $\Leftrightarrow p\mid d_K$（判别式整除判据）；Galois 扩张中同一 $p$ 的所有 $\mathfrak{P}_i$ 有相同 $(e,f)$。
  - 🟡类比：分解群 = 固定一个分支的稳定子，惯性群 = 分支内的微扰群，如流水线的主分支与微操作。
- **关键定理**：**Dedekind 分解定理 + 基本恒等式**：设 $K=\mathbb{Q}(\alpha)$，$\alpha$ 整性极小多项式 $f$，$p\nmid[\mathcal{O}_K:\mathbb{Z}[\alpha]]$。若 $f\bmod p=\prod_{i=1}^g\bar f_i^{e_i}$（$\bar f_i$ 互异不可约，$\deg\bar f_i=f_i$），则
$$(p)=\prod_{i=1}^g\mathfrak{P}_i^{e_i},\quad \mathfrak{P}_i=(p,f_i(\alpha)),\quad \boxed{\ \sum_{i=1}^g e_if_i=n.\ }$$
- **自测**：在 $K=\mathbb{Q}(\sqrt{-5})$，$\mathcal{O}_K=\mathbb{Z}[\sqrt{-5}]$，$f(x)=x^2+5$，$d_K=-20$。分解 $(2),(3),(7)$。(2)：$x^2+5\equiv x^2+1\equiv(x+1)^2\pmod2$，故 $(2)=\mathfrak{p}^2$（分歧，$2\mid d_K$），$\mathfrak{p}=(2,1+\sqrt{-5})$。(3)：$x^2+5\equiv x^2-1\equiv(x-1)(x+1)\pmod3$，故 $(3)=\mathfrak{q}_1\mathfrak{q}_2$（分裂，$e=1,f=1,g=2$）。(7)：$x^2+5\equiv x^2+5$，$-5\equiv2$，$(\frac{2}{7})=1$（$7\equiv-1\pmod8$），故 $(7)$ 也分裂。

**二次域 $\mathbb{Q}(\sqrt d)$ 中素数 $p$ 的分解判据速记**（Marcus Ch 3 最实用的手算工具，务必验 $p=2,3,5,7$）：

| 条件 | 分解模式 | $e,f,g$ | 记忆 |
|---|---|---|---|
| $p\mid d_K$（判别式） | **分歧** $(p)=\mathfrak{p}^2$ | $e=2,f=1,g=1$ | 整除判别式必分歧 |
| $(\frac{d}{p})=1$（$p$ 奇） | **分裂** $(p)=\mathfrak{p}_1\mathfrak{p}_2$ | $e=1,f=1,g=2$ | 二次剩余 = 分裂 |
| $(\frac{d}{p})=-1$（$p$ 奇） | **惯性** $(p)$ 保持素理想 | $e=1,f=2,g=1$ | 非剩余 = 惯性 |
| $p=2$ | 由 $d\bmod8$ 决定 | 见下 | 2 的情形最微妙 |

$p=2$ 的三分（$d_K$ 为判别式）：$2\mid d_K$ 时分歧；$2\nmid d_K$ 时 $d\equiv1\pmod8$ 则分裂，否则惯性。核心口诀：**「整除判别式必分歧，Legendre 符号定分裂/惯性」**。

**Dedekind 分解定理的「陷阱」**：定理要求 $p\nmid[\mathcal{O}_K:\mathbb{Z}[\alpha]]$（指数）。若 $p$ 整除该指数（即 $\mathbb{Z}[\alpha]$ 在 $p$ 处不是「极大」），单纯分解 $\bar f$ 会给出错误的 $e_i$——需用 Dedekind 准则补正或换生成元。这是 Marcus 习题里反复强调的计算细节。

---

### 第 4 章 · The Ideal Class Group and Units（理想类群与单位群）

- **核心**：本章用 **Minkowski 几何嵌入**一次焊死两大结构定理。把 $\mathcal{O}_K$ 嵌入 $\mathbb{R}^{r_1}\times\mathbb{C}^{r_2}\cong\mathbb{R}^n$ 成格 $\Lambda$（体积 $\sqrt{|d_K|}$），Minkowski 凸体定理给出：每个理想类含范数 $\le M_K$ 的整理想，其中**Minkowski 界**
$$M_K=\frac{n!}{n^n}\left(\frac{4}{\pi}\right)^{r_2}\sqrt{|d_K|}.$$
因 $M_K$ 有限，**类群 $\mathrm{Cl}(K)$ 有限**（只需检查有限多个素理想幂）。同一几何给出 **Dirichlet 单位定理**：$\mathcal{O}_K^\times\cong\mu(K)\times\mathbb{Z}^{r_1+r_2-1}$，单位经对数映射落在超平面 $\sum x_i=0$（$\cong\mathbb{R}^{r_1+r_2-1}$）的格上，其体积为**调节子** $R_K$。Marcus 的习题让你对二次域逐个验证：虚二次秩 0（单位有限）、实二次秩 1（求基本单位）。
- **飞腾锚点**：**Schmidt 正交化** —— Minkowski 嵌入把 $\mathcal{O}_K$ 的 $\mathbb{Z}$-基映成 $\mathbb{R}^n$ 中格 $\Lambda$，对基做 Gram-Schmidt 正交化得逐层最短向量——正是算 Minkowski 界与单位对数格体积（调节子 $R_K$）的核心步骤，也是 LLL 格归约的算法骨架。
  - 🟢事实：$M_K\propto\sqrt{|d_K|}$ 依赖嵌入格体积；$\mathbb{Q}(\sqrt2)$ 单位秩 $=2+0-1=1$，基本单位 $1+\sqrt2$；$\mathbb{Q}(i)$ 秩 $=0$，$\mathcal{O}^\times=\{\pm1,\pm i\}$（有限）。
  - 🟡类比：类群有限 = 「格中只有有限多种形状的胞腔」，Minkowski 界 = 胞腔最大尺寸的精确上界。
- **关键定理**：**Dirichlet 单位定理**：设 $K$ 数域，$r_1$ 实嵌入，$r_2$ 复嵌入对，则
$$\mathcal{O}_K^\times\cong\mu(K)\times\mathbb{Z}^{r_1+r_2-1},$$
$\mu(K)$ 为 $K$ 中单位根全体（有限循环群），单位秩 $=r_1+r_2-1$。配合 Minkowski 界得类群 $\mathrm{Cl}(K)$ 有限。
- **自测**：求 $\mathbb{Q}(\sqrt2)$ 的基本单位与类数。答：秩 $=1$，$u=1+\sqrt2$，$\mathrm{N}(u)=(1+\sqrt2)(1-\sqrt2)=-1$（单位 ✓）。$M_K=\frac{2!}{2^2}(\frac4\pi)^0\sqrt8=\frac12\cdot2\sqrt2=\sqrt2<2$，故每类含范数 $<2$ 的整理想，只有 $(1)$（$N=1$），$h=1$（PID）。验证 $\mathcal{O}^\times=\{\pm(1+\sqrt2)^m:m\in\mathbb{Z}\}$。

**Minkowski 界与类数计算速记**（Marcus Ch 4 的核心算法，把「无穷多理想类」缩成「有限手算」）：

| 数域 $K$ | $r_1,r_2$ | $d_K$ | $M_K$ | 需查素理想 $N\le M_K$ | $h_K$ |
|---|---|---|---|---|---|
| $\mathbb{Q}$ | $1,0$ | $1$ | — | — | $1$ |
| $\mathbb{Q}(i)$ | $0,1$ | $-4$ | $\frac{2!}{4}(\frac4\pi)\cdot2=\frac2\pi<1$ | 无 | $1$ |
| $\mathbb{Q}(\sqrt2)$ | $2,0$ | $8$ | $\frac12\sqrt8=\sqrt2<2$ | 无（$N=2$ 超 $M_K$） | $1$ |
| $\mathbb{Q}(\sqrt{-5})$ | $0,1$ | $-20$ | $\frac12(\frac4\pi)\sqrt{20}=\frac{2\sqrt5}{\pi}\approx1.42<2$ | 无 | $2$（$\mathfrak{p}=(2,1+\sqrt{-5})$ 非主，阶 2） |
| $\mathbb{Q}(\zeta_5)$ | $0,2$ | $125$ | $\frac{4!}{5^4}(\frac4\pi)^2\sqrt{125}\approx2.06$ | 仅 $N=2$（$2$ 惯性，主） | $1$ |

核心：$M_K$ 给出「每个理想类都有代表元 $N\le M_K$」的精确上界，故只需检查素数 $p\le M_K$ 的素理想分解即可判定类群结构。**注意**：$M_K$ 是上界非精确值，$h_K$ 仍需逐一验证哪些素理想主/非主。

---

### 第 5 章 · Cyclotomic Fields（割圆域 $\mathbb{Q}(\zeta_n)$）

- **核心**：割圆域是素数分解理论（Ch 3）最美的试验场。$\zeta_n=e^{2\pi i/n}$，割圆多项式 $\Phi_n(x)=\prod_{(k,n)=1}(x-\zeta_n^k)$，$[\mathbb{Q}(\zeta_n):\mathbb{Q}]=\varphi(n)$。核心事实：$\mathbb{Q}(\zeta_n)$ 的整数环恰为 $\mathbb{Z}[\zeta_n]$（整基 $\{1,\zeta_n,\ldots,\zeta_n^{\varphi(n)-1}\}$），$\mathrm{Gal}(\mathbb{Q}(\zeta_n)/\mathbb{Q})\cong(\mathbb{Z}/n)^*$（Abel 群！）。素数 $p$ 的分解：$p\nmid n$ 时由 $p\bmod n$ 在 $(\mathbb{Z}/n)^*$ 中的阶决定（$f=$ 该阶，$g=\varphi(n)/f$）；$p\mid n$ 时分歧。**Kronecker-Weber 定理**（每个 Abel 扩张 $\subset$ 某割圆域）的影子在此浮现。Marcus 用 **Gauss 和** $g=\sum_a\chi(a)\zeta_p^a$ 给出 $g^2=\chi(-1)p$，把二次域 $\mathbb{Q}(\sqrt{p^*})$（$p^*=(-1)^{(p-1)/2}p$）嵌入 $\mathbb{Q}(\zeta_p)$，一举导出二次互反律。
- **飞腾锚点**：**UDOT 16.9× [E05]** —— Gauss 和 $g=\sum_{a=1}^{p-1}\chi(a)\zeta_p^a$ 是「特征值点积累加」（UDOT 无符号点积），把乘法特征 $\chi$ 与加法特征 $\zeta_p^a$ 的内积压缩成一个数，其平方 $g^2=\chi(-1)p$ 是数论的「内积恒等式」；割圆域判别式 $\prod$ 迹同样涉及共轭求和。
  - 🟢事实：$\mathrm{Gal}(\mathbb{Q}(\zeta_p)/\mathbb{Q})\cong(\mathbb{Z}/p)^*\cong\mathbb{Z}/(p-1)$；$d_{\mathbb{Q}(\zeta_p)}=(-1)^{(p-1)/2}p^{p-2}$（如 $p=5$ 给 $5^3=125$）。
  - 🟡类比：Gauss 和 = 「乘法结构与加法结构的傅里叶变换」，$g^2=p$ = Parseval 型恒等式。
- **关键定理**：**割圆域基本定理**：$\mathcal{O}_{\mathbb{Q}(\zeta_n)}=\mathbb{Z}[\zeta_n]$，$\mathrm{Gal}(\mathbb{Q}(\zeta_n)/\mathbb{Q})\cong(\mathbb{Z}/n)^*$。**Gauss 和平方**：对奇素数 $p$，二次特征 $\chi$ 的 Gauss 和 $g=\sum_{a=1}^{p-1}\chi(a)\zeta_p^a$ 满足 $g^2=\chi(-1)\,p=(-1)^{(p-1)/2}p$，故 $\mathbb{Q}(\sqrt{(-1)^{(p-1)/2}p})\subset\mathbb{Q}(\zeta_p)$。
- **自测**：用 Gauss 和导出 $p=5$ 时 $\mathbb{Q}(\sqrt5)\subset\mathbb{Q}(\zeta_5)$。答：$5\equiv1\pmod4$，$\chi(-1)=1$，$g^2=5$，故 $g=\pm\sqrt5\in\mathbb{Q}(\zeta_5)$，$\mathbb{Q}(\sqrt5)\subset\mathbb{Q}(\zeta_5)$ ✓（与 Ch 2 自测的 $\zeta_7\to\mathbb{Q}(\sqrt{-7})$ 对照：$7\equiv3\pmod4$，$g^2=-7$）。又 $\mathbb{Q}(\zeta_8)$：$\varphi(8)=4$，$\mathrm{Gal}\cong(\mathbb{Z}/8)^*\cong\mathbb{Z}/2\times\mathbb{Z}/2$（非循环），含三个二次子域 $\mathbb{Q}(i),\mathbb{Q}(\sqrt2),\mathbb{Q}(\sqrt{-2})$。

---

### 第 6 章 · The Dirichlet L-series and Class Number Formula（$L$-级数与类数公式）

- **核心**：本章是**解析高潮**——用 $L$-函数把 Ch 1–5 的代数不变量（类数 $h_K$、调节子 $R_K$、判别式 $d_K$）焊成一行公式。**Dirichlet 特征** $\chi:(\mathbb{Z}/m)^*\to\mathbb{C}^*$，**Dirichlet $L$-函数** $L(s,\chi)=\sum_{n\ge1}\chi(n)n^{-s}=\prod_p(1-\chi(p)p^{-s})^{-1}$（$\mathrm{Re}\,s>1$），延拓到 $\mathbb{C}\setminus\{1\}$。**Dedekind $\zeta$ 函数** $\zeta_K(s)=\sum_{\mathfrak{a}}N(\mathfrak{a})^{-s}=\prod_{\mathfrak{p}}(1-N(\mathfrak{p})^{-s})^{-1}$。**解析类数公式**（$s=1$ 留数）：
$$\operatorname*{Res}_{s=1}\zeta_K(s)=\frac{2^{r_1}(2\pi)^{r_2}h_KR_K}{w_K\sqrt{|d_K|}}.$$
对割圆域 $K=\mathbb{Q}(\zeta_m)$，因 Galois 群 Abel，$\zeta_K$ 完全分解为 Dirichlet $L$-函数之积，给出**割圆域类数公式**（Marcus 的精美特例）。Marcus 在二次域上让你手算 $L(1,\chi_d)$，验证类数。
- **飞腾锚点**：**Iron Law <2% [Lab00]** —— 类数公式两侧严格相等（解析留数 = 代数不变量），零容差——$h_K$ 是精确正整数，$L(1,\chi)$ 收敛到精确值；任何数值误差超 2% 就摧毁公式的自洽性（Iron Law：性能 = 指令数 $\times$ CPI $\times$ 时钟，误差铁律）。
  - 🟢事实：$\mathrm{Res}_{s=1}\zeta_\mathbb{Q}(s)=1$；$\zeta_{\mathbb{Q}(i)}=\zeta(s)L(s,\chi_{-4})$，$L(1,\chi_{-4})=1-\frac13+\frac15-\cdots=\frac\pi4$（Leibniz），留数吻合。
  - 🟡类比：$\zeta_K(s)$ = 数域的「解析签名」，$s=1$ 留数 = 唯一指纹，精确锁定类数——如 loss 极值唯一确定参数。
- **关键定理**：**解析类数公式**：设 $K$ 数域，$r_1$ 实嵌入，$2r_2$ 复嵌入，$h_K$ 类数，$R_K$ 调节子，$w_K$ 单位根数，则
$$\operatorname*{Res}_{s=1}\zeta_K(s)=\frac{2^{r_1}(2\pi)^{r_2}h_KR_K}{w_K\sqrt{|d_K|}}.$$
这是「解析留数 = 代数不变量」的精确陈述。割圆域特例（$\mathrm{Gal}$ Abel）：$\zeta_{\mathbb{Q}(\zeta_m)}=\prod_{\chi}L(s,\chi)$，类数由 $L(1,\chi)$ 之积给出。
- **自测**：对 $K=\mathbb{Q}(\sqrt{-5})$ 验证类数 $h=2$。提示：$r_1=0,r_2=1,w=2$（$\{\pm1\}$），$d=-20$，虚二次秩 0 故 $R=1$。$\mathrm{Res}\,\zeta_K=\frac{(2\pi)^1\cdot h\cdot1}{2\cdot\sqrt{20}}=\frac{\pi h}{2\sqrt{20}}=\frac{\pi h}{4\sqrt5}$。又 $\zeta_K=\zeta(s)L(s,\chi_{-20})$，$L(1,\chi_{-20})=\frac{2\pi}{w\sqrt{|d|}}h=\frac{2\pi}{2\sqrt{20}}\cdot2=\frac{2\pi}{\sqrt{20}}=\frac\pi{\sqrt5}$，解出 $h=2$ ✓（与 Ch 3 的 $\mathrm{Cl}\cong\mathbb{Z}/2$ 一致）。

**类数公式特例速记**（把一般公式代入具体数域，Marcus Ch 6 习题核心）：

| 数域 $K$ | $r_1,r_2$ | $d_K$ | $w_K$ | $h_K$ | $\mathrm{Res}_{s=1}\zeta_K$ |
|---|---|---|---|---|---|
| $\mathbb{Q}$ | $1,0$ | $1$ | $2$ | $1$ | $1$ |
| $\mathbb{Q}(i)$ | $0,1$ | $-4$ | $4$ | $1$ | $\pi/4$（Leibniz） |
| $\mathbb{Q}(\sqrt{-5})$ | $0,1$ | $-20$ | $2$ | $2$ | $\pi/\sqrt5$ |
| $\mathbb{Q}(\sqrt2)$ | $2,0$ | $8$ | $2$ | $1$ | $\frac{2\log(1+\sqrt2)}{\sqrt8}$ |

核心：虚二次域用 $L(1,\chi_d)$（收敛级数），实二次域用基本单位 $\varepsilon$ 的对数 $\log\varepsilon$（调节子 $R=\log\varepsilon$）。类数公式把「代数结构」与「解析留数」精确焊死，是 Marcus Ch 6 的解析高潮。**割圆域特例**（$\mathrm{Gal}$ Abel）：$\zeta_{\mathbb{Q}(\zeta_m)}=\prod_\chi L(s,\chi)$，类数由若干 $L(1,\chi)$ 之积给出——Marcus 的精美收官。

---

### 第 7 章 · The Distribution of Primes（素数分布：Chebotarev 密度）

- **核心**：本章把 Ch 6 的解析方法推向素数分布。**Dirichlet 等差数列素数定理**：对 $(a,m)=1$，等差数列 $\{a+km\}$ 含无穷多素数，且密度均匀（$\pi(x;a,m)\sim\frac{1}{\varphi(m)}\frac{x}{\ln x}$）——这是 $L(s,\chi)$ 在 $\mathrm{Re}\,s=1$ 不零的解析推论。Marcus 进而陈述（并部分论证）**Frobenius 密度定理**与更强形式 **Chebotarev 密度定理**：对 $L/\mathbb{Q}$ 有限 Galois 扩张，$\mathrm{Frob}_p$ 的共轭类 $C\subset\mathrm{Gal}(L/\mathbb{Q})$ 中素数的自然密度 $=\frac{|C|}{|G|}$。这是「素数按 Galois 群共轭类均匀分布」的精确陈述——把 Ch 3 的 Frobenius 与 Ch 6 的 $L$-函数焊在一起，是全书的终极统一。Dirichlet 定理是 $G=(\mathbb{Z}/m)^*$（Abel，共轭类=元素）的特例。
- **飞腾锚点**：**GEMM 9.45 GFLOPS [Lab05]** —— Chebotarev 密度把素数按 $|G|\times|G|$ 的共轭类表均匀分布，验证密度 = 把全体素数的 Frobenius 标签统计成「$|G|$ 维频率矩阵」，是密集的矩阵化计数（GEMM）；Artin $L$-函数的计算涉及 Galois 表示矩阵的高维吞吐。
  - 🟢事实：Dirichlet 定理密度 $\frac{1}{\varphi(m)}$ 是 Chebotarev 在 $G=(\mathbb{Z}/m)^*$ Abel 时的特例；Chebotarev 需要 Artin $L$-函数的解析性（Artin 互反律保证分解为 Hecke $L$）。
  - 🟡类比：Frobenius = 素数的「染色标签」，Chebotarev = 「所有颜色按群结构均匀出现」，如矩阵各行列的均匀统计。
- **关键定理**：**Chebotarev 密度定理**：设 $L/\mathbb{Q}$ 有限 Galois 扩张，$G=\mathrm{Gal}(L/\mathbb{Q})$。对每个共轭类 $C\subset G$，在 $L$ 中非分歧且 $\mathrm{Frob}_p\in C$ 的素数 $p$ 的自然密度
$$\delta(C)=\lim_{x\to\infty}\frac{|\{p\le x:\mathrm{Frob}_p\in C\}|}{|\{p\le x\}|}=\frac{|C|}{|G|}.$$
Dirichlet 等差数列素数定理是 $G$ Abel、$C$ 为单元素的特例。
- **自测**：对 $L=\mathbb{Q}(\zeta_5)$，$G\cong\mathbb{Z}/4$（Abel，共轭类=元素），用 Chebotarev 求 $p$ 在 $L$ 中完全分裂的密度。答：完全分裂 $\Leftrightarrow\mathrm{Frob}_p=1\Leftrightarrow p\equiv1\pmod5$，密度 $=\frac{1}{4}$。验证：$f=\mathrm{ord}(p\bmod5)$，$g=4/f$；$p\equiv1$ 时 $f=1,g=4$（完全分裂）。又惯性（$g=1,f=4$）对应 $\mathrm{ord}(p\bmod5)=4$，即 $p\equiv2,3\pmod5$，密度 $\frac24=\frac12$。

**Chebotarev 密度分布速记**（$L=\mathbb{Q}(\zeta_5)$，$G\cong(\mathbb{Z}/5)^*\cong\mathbb{Z}/4$，Abel 故共轭类=元素）：

| Frobenius 标签 | $p\bmod5$ | 分解 $(p)=$ | $e,f,g$ | 密度 $\frac{|C|}{|G|}$ |
|---|---|---|---|---|
| 恒等（完全分裂） | $1$ | $\mathfrak{P}_1\mathfrak{P}_2\mathfrak{P}_3\mathfrak{P}_4$ | $1,1,4$ | $\frac14$ |
| 二阶（部分分裂） | $4$ | $\mathfrak{P}_1\mathfrak{P}_2$（$f=2$） | $1,2,2$ | $\frac14$ |
| 四阶（惯性） | $2,3$ | $\mathfrak{P}$（$f=4$） | $1,4,1$ | $\frac24=\frac12$ |

核心：素数按 Frobenius「均匀染色」，密度恰好是 $|C|/|G|$——Dirichlet 等差数列素数定理是这个表在 Abel 群上的特例。Chebotarev 是 Marcus 全书的终极统一：把 Ch 3（Frobenius）与 Ch 6（$L$-函数）焊成一个密度定理。

---

## §9 全书思想主线：Marcus 的「习题驱动」教学哲学

Marcus 的全书贯穿一条主线：**以大量带提示的习题逼读者亲手算，从「手算肌肉记忆」自然生长到「理论驾驭」**。这不是「先抽象定义后举例」的欧几里得式写法，也非 Janusz「例题 + 完整证明」的温和叙述，而是**「定义 + 骨架定理 + 一堆算出来的习题」的训练手册**——Marcus 把判别式公式、类数计算、$L(1,\chi)$ 求值、分圆域 Galois 群手算大量留作习题（附录给提示），逼你「做」而非「读」。全书 7 章可分三层：**第一层（Ch 1–2，代数地基）**搭好 $\mathcal{O}_K$、迹/范数/判别式、Dedekind 域与 Galois 工具；**第二层（Ch 3–4，计算核心）**用 Dedekind 分解定理把素数 $p$「切开」（split/inert/ramify），用 Minkowski 几何一次焊死类群有限与单位群结构——这两章是 Marcus 的灵魂，每个定理都配 $\mathbb{Q}(\sqrt d)$ 手算习题；**第三层（Ch 5–7，应用与解析收官）**用分圆域展示 Ch 3 的威力，用 $L$-函数留数给类数公式，用 Chebotarev 密度把 Frobenius 与素数分布统一。

**与同类教材的方法论对比**：Marcus 走**「习题驱动」**路线——你做完所有习题就拥有完整计算肌肉记忆，最适合「练手 + 备考」。Janusz 走**「温和自学」**路线——证明完整、例题丰富，适合「读懂 + 第一遍」。Neukirch 走**「公理化驱动」**路线——抽象类域论一举贯通局部/全局，适合「系统整合 + 第二遍」。三书不冲突而互补：**Marcus/Janusz 建计算手感（第一遍）→ Neukirch 补局部域与类域论系统（第二遍）→ Lang GTM110 做全景整合（第三遍）**。Marcus 与 Janusz 是「亲民入门双子」——选其一即可，喜欢做题选 Marcus，喜欢读完整证明选 Janusz。与已读的 Silverman GTM106（椭圆曲线，用 Frobenius 分析点群）和 Ireland-Rosen（初等数论骨架）呼应：Marcus 补上了它们之间缺失的「整体代数数论计算训练」中间层。

**Marcus 的「压缩术」可复刻**：(1) 把关键计算留作带提示习题，逼读者主动算而非被动读；(2) 用 Minkowski 几何把类群有限性与单位群结构用同一格论证统一；(3) 用 Chebotarev 密度把 Ch 3 的 Frobenius 与 Ch 6 的 $L$-函数焊成一个定理。这三步「习题练手→几何统一→密度收束」正是 Marcus 全书的教学主线。

**代数数论学习常见误区（跨章汇总）**：

| 误区 | 正确理解 | 出处 |
|---|---|---|
| 元素唯一分解 = 理想唯一分解 | 仅理想必唯一分解；元素未必（$\mathbb{Z}[\sqrt{-5}]$） | Ch 1 |
| Dedekind 分解定理无条件成立 | 需 $p\nmid[\mathcal{O}_K:\mathbb{Z}[\alpha]]$；否则要用更精细工具 | Ch 3 |
| 迹/范数是元素本身的不变量 | 是扩张 $K/\mathbb{Q}$ 的不变量，依赖嵌入选取 | Ch 1 |
| 分歧 $\Leftrightarrow p\mid d$（域参数） | 正确的是 $p\mid d_K$（判别式），$d_K$ 可能 $\ne d$ | Ch 3 |
| 调节子秩 0 时 $R=0$ | 定义 $R=1$（空行列式约定），否则类数公式失效 | Ch 4, 6 |
| $\zeta_K=\zeta$ | 仅 $K=\mathbb{Q}$ 时成立；一般 $\zeta_K$ 对所有理想求和 | Ch 6 |
| Dirichlet 定理涵盖所有等差数列 | 仅 $(a,m)=1$ 时无穷；$(a,m)>1$ 至多一个素数 | Ch 7 |

---

## §10 与本仓库其他笔记的交叉引用

### 与已精读书目的呼应

| 本书 | 关系 | 交叉点 |
|---|---|---|
| **Janusz** GSM7（同期生成） | 亲民双子 | Marcus Ch 1–6 ≈ Janusz Ch 2–8（覆盖面近乎重合）；Marcus 习题驱动 + Janusz 证明完整，二者互补可二选一 |
| **Neukirch** G322（同期生成） | 系统进阶 | Marcus 全书停留在整体域；Marcus 建手感后，Neukirch 补局部域双线（Ch 3 赋值论）与类域论系统（Ch 5–7） |
| **Ireland-Rosen** GTM84 | 初等前置 | IR Ch 12–14（代数整数、Dedekind 域）是 Marcus Ch 1–3 的初等热身；IR 的分圆域（Ch 13）↔ Marcus Ch 5 |
| **Silverman** GTM106 椭圆曲线 | 局部应用 | Silverman Ch VII（椭圆曲线局部约化）用 Marcus Ch 3 的分歧/Frobenius；Tate 算法 ↔ 分歧分层 |
| **Serre** GTM67 局部域 | 局部深化 | Marcus 弃用的 FP16/Hensel 锚点在 Serre 有归宿：Marcus 无局部域章，建手感后接 Serre 攻 $p$-adic 锋利 |

### AI/工程锚点法：代数数论的工程落地

| 数学概念 | AI/工程对应 | 锚点说明 |
|---|---|---|
| **$\mathcal{O}_K$ Dedekind 域 = $\mathbb{Z}$ 分层扩展** | TLB 分层寻址 / 内存局部性 | 🟡$\mathbb{Z}\subset\mathcal{O}_K$ 如虚拟地址↔物理地址分层映射，理想唯一分解 = 页表素因子分解 |
| **Galois 群作用 = 整数矩阵群** | matmul 线性变换 | 🟢$\sigma\in\mathrm{Gal}(L/K)$ 在整基上是 $\det=\pm1$ 的整数矩阵，群运算 = matmul |
| **素数分解 split/inert/ramify** | 分支预测 / 路径选择 | 🟡$e>1$ 分歧（慢路径 0.71）/ 非分歧（快路径 3.14），Frobenius = 分支标签 |
| **Minkowski 嵌入正交化** | Schmidt 正交化 / LLL 格归约 | 🟢单位对数格的 Gram-Schmidt 体积 = 调节子 $R_K$；Minkowski 界依赖格几何 |
| **Gauss 和 = 特征点积累加** | UDOT 点积 / FFT 内积 | 🟢$g=\sum\chi(a)\zeta_p^a$ 是乘法/加法特征的「傅里叶内积」，$g^2=p$ 是 Parseval 型恒等式 |
| **类数公式（解析留数）** | Iron Law 精度铁律 / loss 极值 | 🟢$\mathrm{Res}_{s=1}\zeta_K$ 两侧严格相等，零容差，如性能铁律不可近似 |
| **Chebotarev 密度** | GEMM 矩阵化计数 / 高维吞吐 | 🟡Frobenius 标签按 $|G|\times|G|$ 共轭类表均匀统计，是密集矩阵化计数 |
| **RSA / 素数分布** | 大整数分解 / 素数搜索 | 🟡Dirichlet/Chebotarev 密度刻画素数分布，是 RSA 素数生成的「供给保证」 |
| **格密码 LWE / NTRU** | 格归约 / Minkowski 界 | 🟡NTRU 安全性依赖格中最近向量问题（CVP），Minkowski 几何给格点存在界（Ch 4） |
| **椭圆曲线密码 ECC** | Frobenius / 素域群运算 | 🟢椭圆曲线点数 $=p+1-\mathrm{tr}(\mathrm{Frob})$（Hasse），Frobenius 是核心工具（Silverman GTM106） |
| **Hensel 提升 / 数值算法** | FP16 逐步提升 / Newton 二次收敛 | 🟢（弃用锚点）$p$-adic Newton 每步精度翻倍；Marcus 无单章，见 Janusz Ch 7 / Serre GTM67 |

**锚点法的统一视角**：Marcus 全书可用三句话锚定——**「整基让 $\mathcal{O}_K$ 可计算（Ch 1），Dedekind 分解让素数可切（Ch 3），$\zeta$ 留数让类数可秤（Ch 6）」**。第一步是线性代数（迹/范数/判别式给坐标），第二步是代数（素理想分解），第三步是分析（解析留数给精确不变量），终局（Ch 7）用 Chebotarev 把代数与解析焊成密度定理。掌握这条主线，全书的「为什么这样组织」就豁然开朗。

---

## §11 自测答案要点（供核对）

1. **Ch 1** $\mathbb{Q}(\sqrt{-3})$：$-3\equiv1\pmod4$，$\omega=\frac{-1+\sqrt{-3}}{2}$（$x^2+x+1=0$，$\omega^3=1$），整基 $\{1,\omega\}$，$d_K=-3$。$\mathbb{Q}(\sqrt5)$：$\varphi=\frac{1+\sqrt5}{2}$（$x^2-x-1=0$），$d_K=5$。
2. **Ch 2** $\mathbb{Q}(\zeta_7)$：$\mathrm{Gal}\cong(\mathbb{Z}/7)^*\cong\mathbb{Z}/6$。$\langle\sigma_3^2\rangle\cong\mathbb{Z}/3$↔二次子域 $\mathbb{Q}(\sqrt{-7})$（$7\equiv3\pmod4$，$(-1)^3\cdot7=-7$）；$\langle\sigma_3^3\rangle\cong\mathbb{Z}/2$↔三次子域。
3. **Ch 3** $\mathbb{Q}(\sqrt{-5})$：$(2)=\mathfrak{p}^2$（$\mathfrak{p}=(2,1+\sqrt{-5})$，$N=2$）；$(3)=\mathfrak{q}_1\mathfrak{q}_2$（$\mathfrak{q}_i=(3,1\pm\sqrt{-5})$，$N=3$）；$(7)$ 也分裂（$(\frac2 7)=1$）。$\mathfrak{p}$ 非主（$a^2+5b^2=2$ 无解），$\mathrm{Cl}\cong\mathbb{Z}/2$。
4. **Ch 4** $\mathbb{Q}(\sqrt2)$：基本单位 $1+\sqrt2$（$\mathrm{N}=-1$）；$M_K=\sqrt2<2\Rightarrow h=1$（PID）。
5. **Ch 5** $\mathbb{Q}(\zeta_5)$：$g^2=\chi(-1)5=5$（$5\equiv1\pmod4$），$\mathbb{Q}(\sqrt5)\subset\mathbb{Q}(\zeta_5)$ ✓。$\mathbb{Q}(\zeta_8)$：$\mathrm{Gal}\cong(\mathbb{Z}/8)^*\cong\mathbb{Z}/2\times\mathbb{Z}/2$，三二次子域 $\mathbb{Q}(i),\mathbb{Q}(\sqrt2),\mathbb{Q}(\sqrt{-2})$。
6. **Ch 6** $\mathbb{Q}(\sqrt{-5})$：$h=2$。$\mathrm{Res}\,\zeta_K=\frac{\pi h}{4\sqrt5}$，$L(1,\chi_{-20})=\frac{2\pi h}{2\sqrt{20}}=\frac\pi{\sqrt5}$，解 $h=2$ ✓。
7. **Ch 7** $\mathbb{Q}(\zeta_5)$：完全分裂（$p\equiv1\bmod5$）密度 $\frac14$；惯性（$\mathrm{ord}(p\bmod5)=4$，即 $p\equiv2,3$）密度 $\frac12$；部分分裂（$f=2$，$p\equiv4$）密度 $\frac14$。

---

## §12 延展阅读与后续方向

读完 Marcus，自然有三个深入方向：

1. **局部深化**：Serre GTM67《Local Fields》——把 Marcus 弃用的 $p$-adic/Hensel 补成锋利的局部类域论；详见本仓库 `serre_局部域_GTM67_快速逐章.md`。
2. **系统进阶**：Neukirch《Algebraic Number Theory》——整体+局部双线、抽象类域论系统化，把 Marcus 的计算骨架升级为研究级框架。
3. **整合复习**：Lang GTM110（代数+解析+类域论三合一），把 Marcus 的碎片粘成完整蓝图。
4. **割圆域纵深**：Washington《Introduction to Cyclotomic Fields》GTM83——Marcus Ch 5 的自然延伸，深入割圆域类数公式、$p$-adic $L$-函数与 Iwasawa 理论（本仓库待做候选）。

**与已读笔记的闭环**：Ireland-Rosen（初等数论骨架）→ **Marcus（习题驱动建计算肌肉）** → Janusz（完整证明温和自学，可选镜像）→ Silverman GTM106（Frobenius 应用于椭圆曲线）→ Serre GTM67（局部域锋利）→ Neukirch/Lang（全景整合）。多者合起来，恰好是「代数数论 + 算术几何」的标准研究入门组合。

**研究者方向取舍建议**：若偏向**计算/算术几何**，优先吃透 Marcus Ch 3（Dedekind 分解、Frobenius）+ Ch 5（割圆域）——是 Tate 算法与椭圆曲线局部分析的地基。若偏向**解析数论**（$L$-函数、素数分布），Ch 6 类数公式 + Ch 7 Chebotarev 是核心入口，后续接 Lang Artin $L$-函数与 Tenenbaum 解析数论。若偏向**密码学应用**（用户出口），Ch 3（素数分解）+ Ch 4（类群、Minkowski 格）是 RSA/格密码 LWE/ECC 的数学底座——素数分布（Chebotarev）保证密钥生成供给，格几何（Minkowski）刻画 NTRU 安全边界。

> **一句话总结**：Marcus《Number Fields》用习题驱动教学，让你「做完习题就拥有完整的代数数论计算肌肉记忆」——它与 Janusz 是亲民入门双子，喜欢做题选 Marcus，先 Marcus/Janusz 建手感，后 Neukirch/Lang 升系统，事半功倍。

---

> **精读纪律**：本文为快速逐章精读，每章取 1 个飞腾锚点 + 1 个关键定理 + 1 道自测题。深入计算与完整证明请回原书（Marcus 把大量结论留作带提示习题，附录 Hints 是教学法关键，务必独立完成 $\ge 60\%$）。🟢 = 事实锚点（可直接引用），🟡 = 类比锚点（仅供直觉，不可引用于严格证明）。
>
> **实操验证建议**（SageMath / PARI-GP）：
> - `K = NumberField(x^2+5)` → `.class_group()` / `.class_number()` 验证 Ch 1/4 类数
> - `K.integral_basis()` / `K.discriminant()` → 验证 Ch 1 整基与判别式
> - `factor(p*K)` 或 `ideal(2).factor()` → 验证 Ch 3 素数分解 split/inert/ramify
> - `K.units()` → 验证 Ch 4 Dirichlet 单位定理与基本单位
> - `CyclotomicField(5)` → `.galois_group()` / `.discriminant()` 验证 Ch 5 割圆域
> - `L(s, chi)` / `zetak(K, 1)` → 验证 Ch 6 类数公式留数
> - Chebotarev 密度：统计小素数 $p$ 的 `factor(p*L)` 模式，对照 $|C|/|G|$
