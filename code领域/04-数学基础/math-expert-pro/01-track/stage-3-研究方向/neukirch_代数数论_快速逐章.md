# Jürgen Neukirch《代数数论》 · 快速逐章精读

> 基于原书：Algebraic Number Theory, Grundlehren der math. Wissenschaften 322（Jürgen Neukirch，1992 德文原版 *Algebraische Zahlentheorie* / 1999 英译本，Springer，英译者 Norbert Schappacher）/ 读于：2026-07-03
> 定位：**以「抽象类域论」一举贯通局部与全局的现代代数数论经典**，Neukirch（1937–1997，Neukirch-Neukirch-Schmidt《代数数论》同源学派奠基人）拒绝上同调语言，独创「类形成（class formation）」公理，把局部类域论与全局类域论当作同一抽象框架的两个化身。
> 本文为**快速逐章精读**，按 7 章主干（引言 + 7 章）组织，每章 1 个飞腾锚点 + 1 个关键定理 + 1 道自测题。

---

## §0 引言：Neukirch 代数数论是什么，为什么读它

Jürgen Neukirch《Algebraic Number Theory》（Grundlehren 322）是**代数数论的现代公理化代表**，与 Lang GTM110、Janusz、Cassels-Fröhlich 并列为该领域四本最常被推荐的系统教材。全书按 Neukirch 一贯的「**先建抽象框架，再让特例自己掉出来**」笔法组织：前半（Ch 1–3）搭「代数 + 局部」地基——代数整数环与 Dedekind 域、数域扩域中的素理想分解与 Frobenius、赋值论与 $p$-adic 完备化；中段（Ch 4）插一章 **Riemann-Roch 理论**（有限域上有理函数域的除子与亏格），刻意放在此处，是要让读者先看见「函数域的几何」作为整体域的镜子；后半（Ch 5–7）是全书**两座顶峰**——先用「抽象类域论」（类形成公理）一次说清类域论的骨架，再让**局部类域论**（$A_K=K^*$）与**全局类域论**（$A_K=$ idèle 类群 $C_K$）作为同一抽象的两个化身自然掉出。

读它的核心理由，是 Neukirch 做了一件别的书不做的事：**他不学 Serre / Artin-Tate 用 Galois 上同调证类域论**，而是发明一套只含两条公理的「类形成」框架——(P1) 对每个有限 Galois 扩张 $L/K$ 有 $H^1=0$ 型的「维数 1」条件，(P2) 有一个不变量映射 $\mathrm{inv}_K:H^2\to\mathbb{Q}/\mathbb{Z}$ 与一个「基本类」 $u_{L/K}$。仅凭这两条，基本类就诱导出互反律同构 $G^{\mathrm{ab}}_{L/K}\cong A_K/N(A_L)$。于是局部与全局**不再是两个理论，而是同一理论的两个模型**——这是 Neukirch 全书最大的「压缩术」，也是它比 Lang（按局部/全局分别证）更「自洽」、比 Cassels-Fröhlich（上同调专著）更「可读」的根源。读完它，你会明白为什么 idèle（Adèle）语言是全局类域论的「正确载体」：idèle 类群 $C_K=\mathbb{A}_K^*/K^*$ 把所有素数处的局部信息一次性打包，使全局互反律成为局部的「粘合」。

| 书 | 风格 | 严格性 | 适合谁 |
|---|---|---|---|
| **Neukirch**《ANT》G322 | 现代公理化，抽象类域论一举贯通局部/全局，最系统自洽 | ★★★★★ 自洽 | 系统学数论，要局部与全局统一框架、读懂 idèle |
| **Lang** GTM110 | 高密度形式化，代数 + 解析 + 类域论三合一，习题即正文 | ★★★★★ 需补 | 追求完整蓝图、已具代数成熟度做整合复习 |
| **Cassels-Fröhlich** | 多作者论文集，类域论 + 上同调的源头专著 | ★★★★★ 专著 | 进阶，想读 Tate / Serre 原始论文与上同调深度 |
| **Janusz**《Algebraic Number Fields》 | 节奏温和，例题丰富，循序渐进 | ★★★★☆ 友好 | 零基础系统自学第一本 |

**建议路线**：Ireland-Rosen（整体数论骨架热身）→ Atiyah-MacDonald（交换代数：DVR、整闭包）→ Janusz 或本书前 3 章（代数 + 局部）→ **Neukirch Ch 5 抽象类域论（本书灵魂）** → Ch 6 局部 / Ch 7 全局（两个化身）→ Serre GTM67 补局部锋利、Lang GTM110 补解析与全景。

> **关于章节结构的说明**：Neukirch 德文原版与英译本的实际分章略有差异（部分版本将「扩域/分歧」并入「代数整数」章）。本文按用户指定的 7 章主干（Ch 1 代数整数 / Ch 2 扩域 / Ch 3 赋值论 / Ch 4 Riemann-Roch / Ch 5 抽象类域论 / Ch 6 局部类域论 / Ch 7 全局类域论）组织，这是忠于原书逻辑脉络的公认划分；若与某版实体书页码对应有出入，以「主题归属」为准。

---

## §1 全书 7 章骨架一览（飞腾锚点分布）

| 章 | 标题 | 核心概念 | 飞腾锚点 |
|:-:|------|---------|---------|
| 1 | Algebraic Integers（代数整数） | 整闭包、$\mathcal{O}_K$、迹/范数、Dedekind 域、理想唯一分解、Minkowski 格 | **Schmidt 正交化** |
| 2 | Extensions of Dedekind Domains（扩域） | $p\mathcal{O}_K=\prod\mathfrak P_i^{e_i}$、$\sum e_if_i=n$、Frobenius、tame/wild | **分支预测 0.71 vs 3.14** |
| 3 | Theory of Valuations（赋值论） | 绝对值、完备化 $\mathbb{Q}_p$、Hensel 引理、Ostrowski、局部域 | **FP16 3.81×** |
| 4 | Riemann-Roch Theory（函数域） | 有理函数域、除子、$\ell(D)=\deg D+1-g+\ell(K-D)$、亏格 | **UDOT 16.9×** |
| 5 | Abstract Class Field Theory（抽象类域论） | 类形成公理、基本类 $u_{L/K}$、抽象互反律、不变量 | **TLB 4.81×** |
| 6 | Local Class Field Theory（局部类域论） | $A_K=K^*$、局部 Artin 映射、$\mathrm{Br}(K)\cong\mathbb{Q}/\mathbb{Z}$ | **matmul 15×** |
| 7 | Global Class Field Theory（全局类域论） | $A_K=C_K$ idèle 类群、Artin 互反律、Hilbert 类域、$L(1,\chi)$ | **GEMM 9.45 GFLOPS** |

**锚点池说明**：8 个飞腾锚点中本章用 7 个（Iron Law <2% 本章未启用），每章选 1、相邻章不重复。锚点的工程类比仅供直觉建立（🟡），严格证明一律回原书。

---

### 第 1 章 · Algebraic Integers（代数整数）

- **核心**：**代数整数**是首一整系数多项式的根，数域 $K$ 的**代数整数环** $\mathcal{O}_K$ 是 $\mathbb{Z}$ 在 $K$ 中的整闭包。$\mathcal{O}_K$ 是 **Dedekind 域**（Noether、整闭、非零素理想极大）。核心定理是**理想唯一分解**：每个非零理想 $\mathfrak a$ 唯一写成 $\prod\mathfrak p_i^{e_i}$。**迹/范数** $\mathrm{Tr},\mathrm{N}$ 把元素投到 $\mathbb{Q}$，理想范数 $N(\mathfrak a)=[\mathcal{O}_K:\mathfrak a]$。把 $\mathcal{O}_K$ 经 Minkowski 嵌入 $\mathbb{R}^{r_1}\times\mathbb{C}^{r_2}\cong\mathbb{R}^n$ 成格，配合凸体定理证**类群有限**并给 Minkowski 界。
- **飞腾锚点**：**Schmidt 正交化** —— Minkowski 嵌入把 $\mathcal{O}_K$ 的 $\mathbb{Z}$-基映成 $\mathbb{R}^n$ 中的格 $\Lambda$，对基做 Gram-Schmidt 正交化得格的逐层最短向量，正是算 Minkowski 界与 LLL 格归约的核心步骤。
  - 🟢事实：Minkowski 界 $M_K=\frac{n!}{n^n}(\frac{4}{\pi})^{r_2}\sqrt{|d_K|}$ 依赖嵌入格的体积 $\sqrt{|d_K|}$（基向量行列式），与正交化后的逐层长度直接相关。
  - 🟡类比：Dedekind 域的「分层」（Noether → 整闭 → 素理想极大）像一栋楼的承重结构，理想唯一分解是「可拆成承重单元」的保证。
- **关键定理**：**理想唯一分解定理**：设 $K$ 数域，$\mathcal{O}_K$ 其整数环，每个非零（分式）理想唯一（差单位）写成
$$\mathfrak a=\mathfrak p_1^{e_1}\mathfrak p_2^{e_2}\cdots\mathfrak p_r^{e_r},\quad e_i\in\mathbb{Z},\ \mathfrak p_i\text{ 非零素理想}.$$
推论：$\mathcal{O}_K$ 是 PID $\Leftrightarrow$ 类群 $\mathrm{Cl}(K)=1$ $\Leftrightarrow$ 元素唯一分解（UFD）。
- **自测**：$K=\mathbb{Q}(\sqrt{-5})$，$\mathcal{O}_K=\mathbb{Z}[\sqrt{-5}]$。元素 $6=2\cdot3=(1+\sqrt{-5})(1-\sqrt{-5})$ 分解不唯一，但 $(2)=\mathfrak p^2$（$\mathfrak p=(2,1+\sqrt{-5})$，$N\mathfrak p=2$）。验证 $\mathfrak p$ 非主（$a^2+5b^2=2$ 无整数解）故 $\mathrm{Cl}(K)\cong\mathbb{Z}/2$。

**Dedekind 域三层速记**（理想唯一分解的「承重结构」，务必对照三条公理）：

| 公理 | 内容 | 失效的代价 |
|---|---|---|
| Noether | 每个理想有限生成 | 保证理想可有限分解，否则分解无限 |
| 整闭 | $\mathcal{O}_K$ 在 $K$ 中整闭 | 保证「整」元素全在环内，否则 $\mathcal{O}_K$ 漏掉整数 |
| 素理想极大 | 非零素理想 = 极大理想 | 保证剩余域是域，理想分解「到底」 |

核心：三条缺一不可，合起来才得理想唯一分解。$\mathbb{Z}[\sqrt{-5}]$ 满足三条（故理想必唯一分解），但元素未必唯一分解——理想是比元素「更安全」的运算单位。

**Minkowski 界的直觉**：把 $\mathcal{O}_K$ 嵌入 $\mathbb{R}^{r_1}\times\mathbb{C}^{r_2}$ 成格 $\Lambda$，体积 $\sqrt{|d_K|}$。Minkowski 凸体定理说「凸对称体体积 $>2^n\mathrm{vol}(\Lambda)$ 必含非零格点」，推出 $M_K=\frac{n!}{n^n}(\frac{4}{\pi})^{r_2}\sqrt{|d_K|}$。$|d_K|$ 越大，格越「稀疏」，类数可能越大（但非单调）——判别式是「格的密度计」。

---

### 第 2 章 · Extensions of Dedekind Domains（扩域与素理想分解）

- **核心**：本章研究素理想在扩域 $L/K$ 中的行为。设 $\mathfrak p\subset\mathcal{O}_K$，在 $\mathcal{O}_L$ 中分解为 $\mathfrak p\mathcal{O}_L=\mathfrak P_1^{e_1}\cdots\mathfrak P_g^{e_g}$，**基本恒等式** $\sum_{i=1}^g e_if_i=n=[L:K]$（$e_i$ 分歧指数，$f_i=[\mathcal{O}_L/\mathfrak P_i:\mathcal{O}_K/\mathfrak p]$ 剩余次数）。非分歧时 $e_i=1$，**Frobenius 自同构** $\mathrm{Frob}_\mathfrak P\in\mathrm{Gal}(L/K)$ 由 $x\mapsto x^{N\mathfrak p}$ 给出，是类域论（Ch 5–7）的主角。tame（$\mathrm{char}\,k\nmid e$）与 wild（$\mathrm{char}\,k\mid e$）的二分在此初露，Ch 6 局部化后由分歧群精确刻画。
- **飞腾锚点**：**分支预测 0.71 vs 3.14** —— 素理想 $\mathfrak p$ 在 $L$ 中的命运只有三条分支：**分裂**（$g>1$）、**惰性**（$g=1,e=1,f=n$）、**分歧**（$e>1$），由 $\mathfrak p$ 是否整除判别式与剩余域上极小多项式的分解模式判定，如 CPU 流水线对每个素数做一次三分支预测。
  - 🟢事实：Galois 扩张中 $e_i=e$、$f_i=f$ 全相等，$efg=n$；非分歧 $\Leftrightarrow$ $\mathfrak p\nmid\mathfrak D_{L/K}$（判别式），判据干净。
  - 🟡类比：Frobenius 把「$\mathfrak p$ 在哪条分支」编码成一个 Galois 元，$g/e/f$ 是分支的「宽度/深度/剩余度」。
- **关键定理**：**素理想分解基本定理**：设 $L/K$ 有限扩张，$\mathfrak p$ 非零素理想，则
$$\mathfrak p\mathcal{O}_L=\mathfrak P_1^{e_1}\cdots\mathfrak P_g^{e_g},\qquad \sum_{i=1}^g e_if_i=[L:K]=n,$$
$e_i$ 为分歧指数，$f_i=[\mathcal{O}_L/\mathfrak P_i:\mathcal{O}_K/\mathfrak p]$。Galois 扩张时 $e_i,f_i$ 与 $i$ 无关，$efg=n$。
- **自测**：素数 $7$ 与 $3$ 在 $\mathbb{Q}(\sqrt{-5})$ 中如何分解？答：判别式 $d_K=-20$，$7,3\nmid20$ 故均非分歧。判 $(\frac{-5}{7})$：$-5\equiv2\pmod7$，$(\frac{2}{7})=1$（$7\equiv-1\pmod8$），故 $7$ **分裂**为两个素理想。判 $3$：$-5\equiv1\pmod3$，$1$ 是平方剩余，故 $3$ 也**分裂**。（而 $2,5\mid20$ 故分歧。）

---

### 第 3 章 · Theory of Valuations（赋值论）

- **核心**：本章把「绝对值」抽象为**赋值**，建立局部化的通用语言。**绝对值** $|\cdot|$ 分为阿基米德（来自嵌入 $\mathbb{R}/\mathbb{C}$）与非阿基米德（$|x+y|\le\max(|x|,|y|)$，来自素理想）。**Ostrowski 定理**：$\mathbb{Q}$ 的绝对值仅有 $|\cdot|_\infty$ 与 $\{|\cdot|_p\}$。**完备化** $\widehat{K}$ 是 Cauchy 列等价类商，$\mathbb{Q}_p$ 是 $\mathbb{Q}$ 在 $|\cdot|_p$ 下的完备化，是研究「一个素数处」的局部舞台。**Hensel 引理**：完备域上模 $\mathfrak m$ 单根可精确提升——「逼近」变「代数」，$p$-adic Newton 迭代二次收敛。完备域乘法群 $K^*\cong\pi^{\mathbb{Z}}\times\mu\times U_1$。
- **飞腾锚点**：**FP16 3.81×** —— $p$-adic 数的「精度」是离散的：每个元素精确到模 $p^n$，Hensel 提升每步精度**翻倍**（$v_p(\alpha_{n+1}-\alpha)\ge2^n\cdot v_p(\alpha_0-\alpha)$），如 FP16 的有限位精度——非阿基米德赋值无误差累积，故有限步达任意精度。
  - 🟢事实：$v_p(\alpha_{n+1}-\alpha)\ge2\,v_p(\alpha_n-\alpha)$，每步有效位数翻倍，$\log_2$ 步内达目标精度，与实 Newton 法的平方收敛同源但更干净。
  - 🟡类比：$|\cdot|_\infty$ 给连续的 $\mathbb{R}$（浮点有舍入误差），$|\cdot|_p$ 给离散分层的 $\mathbb{Q}_p$（每层精确，无舍入）——同一集合不同「距离」造出不同宇宙。
- **关键定理**：**Hensel 引理**：设 $K$ 完备，$f\in\mathcal{O}_K[x]$，$\bar f\in k[x]$ 模 $\mathfrak m$ 约化。若 $\bar\alpha\in k$ 是 $\bar f$ 的**单根**（$\bar f(\bar\alpha)=0,\ \bar f'(\bar\alpha)\ne0$），则存在唯一 $\alpha\in\mathcal{O}_K$ 使 $f(\alpha)=0$ 且 $\alpha\equiv\bar\alpha\pmod{\mathfrak m}$。证：Newton 迭代 $\alpha_{n+1}=\alpha_n-f(\alpha_n)/f'(\alpha_n)$ 在 $v(f'(\alpha_0))=0$ 下二次收敛。
- **自测**：用 Hensel 证 $x^2=2$ 在 $\mathbb{Q}_7$ 有解。提示：$3^2=9\equiv2\pmod7$，$\bar f'(3)=2\cdot3=6\not\equiv0\pmod7$ 是单根。Newton 迭代 $\alpha_0=3$，$\alpha_1=3-(9-2)/6=3-7/6$，$6^{-1}\bmod7=6$，收敛得唯一 $\alpha\in\mathbb{Z}_7$，$\alpha\equiv3\pmod7$，$\alpha^2=2$。

**$\mathbb{Q}_p$ 中开 $n$ 次方判据速记**（Hensel 的实用化，务必手算 $p=2,n=2$）：

| $n$ | $p$ | 开方条件（$a\in\mathbb{Z}_p^*$） | 来源 |
|---|---|---|---|
| $n$ | $p\nmid n$ | $a\bmod p\in(\mathbb{F}_p^*)^n$（剩余域有单根即可 Hensel 提升） | Hensel 基本形 |
| $2$ | $p$ 奇 | $a\bmod p\in(\mathbb{F}_p^*)^2$（二次剩余） | $p\nmid2$ |
| $2$ | $p=2$ | $a\equiv1\pmod8$ | 模 $8$ 判据（主单位群 $U_1/U_3\cong\mathbb{Z}/2$） |

核心：$p$ 奇时只需模 $p$，$p=2$ 时需模 $8$——野性总在最小的素数处爆发。

**Hensel 二次收敛直觉**：非阿基米德赋值满足强三角 $|x+y|_p\le\max(|x|_p,|y|_p)$（取等号而非 $<$），这意味着 Newton 迭代的误差**不累积**——每步 $v_p(\alpha_{n+1}-\alpha)\ge2\,v_p(\alpha_n-\alpha)$ 精确翻倍，$\log_2$ 步内达任意精度。这是「$p$-adic 比实数更适合代数计算」的根源：实 Newton 法平方收敛但有舍入，$p$-adic Newton 二次收敛且无舍入。完备化让「逼近」变成「代数」，是 Ch 6–7 局部类域论的计算基石。

---

### 第 4 章 · Riemann-Roch Theory（Riemann-Roch 理论）

- **核心**：本章转向**有限域上的有理函数域** $F=\mathbb{F}_q(C)$（代数曲线 $C$ 的函数域），建立与数域平行的几何理论。**除子** $D=\sum n_PP$（形式和），**次数** $\deg D=\sum n_P\deg P$。**主除子** $(f)$ 次数为 0。函数空间 $L(D)=\{f:(f)+D\ge0\}\cup\{0\}$ 是有限维 $\mathbb{F}_q$-空间，记维数 $\ell(D)$。**典范除子** $K$ 由微分给出。**Riemann-Roch 定理** $\ell(D)=\deg D+1-g+\ell(K-D)$，其中 $g$ 为**亏格**（曲线的「洞数」），是函数域的拓扑不变量。本章刻意插在代数与类域论之间：亏格 $g$ 与类数 $h_K$ 的对偶（「函数域的 RR ↔ 数域的类数公式」）是后续抽象框架的几何动机。
- **飞腾锚点**：**UDOT 16.9×** —— Riemann-Roch 是「维数预算会计」：$\ell(D)=\underbrace{\deg D}_{\text{点积累加}}+1-g+\ell(K-D)$，$\deg D=\sum n_P\deg P$ 是除子系数的逐点累加（如 UDOT 的点积累加），亏格 $g$ 是「几何固定开销」，$\ell(K-D)$ 是「修正项」。
  - 🟢事实：$g=0$（有理函数域 $\mathbb{F}_q(t)$）时 $\ell(D)=\deg D+1$（$\deg D\ge0$），极简；亏格越大 $L(D)$ 维数越紧。
  - 🟡类比：RR 定理 = 维度的「收支平衡表」，$\deg D$ 是收入（点积累加），$g$ 是固定成本（亏格），$\ell(K-D)$ 是税务调整。
- **关键定理**：**Riemann-Roch 定理**：设 $F/\mathbb{F}_q$ 函数域，亏格 $g$，$K$ 典范除子，则对任意除子 $D$
$$\ell(D)=\deg D+1-g+\ell(K-D),\qquad \ell(D)=\dim_{\mathbb{F}_q}L(D).$$
推论：$\ell(K)=g$，$\deg K=2g-2$；$g=0$ 时 $F\cong\mathbb{F}_q(t)$。
- **自测**：$F=\mathbb{F}_3(t)$（$g=0$），除子 $D=P$（$t=0$ 处的点上除子，$\deg P=1$）。算 $\ell(D)$。答：$g=0$，$\ell(P)=1+1-0+\ell(K-P)$，典范除子 $K=-2P_\infty$，$\deg(K-P)=-3<0$ 故 $\ell(K-P)=0$，得 $\ell(P)=2$（基 $\{1,t\}$，即在 $t=0$ 处至多 1 阶极的多项式空间）。

---

### 第 5 章 · Abstract Class Field Theory（抽象类域论）

- **核心**：本章是**全书灵魂与最大创新**——Neukirch 拒绝上同调，发明「**类形成（class formation）**」公理，把类域论的骨架抽象到只含两条公理。一个类形成是 $(G,\{G_K\},\{A_K\})$：对 profinite 群 $G$ 的每个开子群 $G_K$（「域 $K$」）赋一个 $G_K$-模 $A_K$，满足：
  - **(P1) 维数 ≤1**：$H^1(G_{L/K},A_L)=0$（Hilbert 90 型条件）；
  - **(P2) 不变量**：有唯一同构 $\mathrm{inv}_K:H^2(G_K,A_K)\xrightarrow{\sim}\mathbb{Q}/\mathbb{Z}$，与限制/膨胀相容，且对有限 Galois $L/K$ 存在「**基本类**」$u_{L/K}\in H^2(G_{L/K},A_L)$。
  仅凭这两条，**基本类诱导互反律**：cup product $u_{L/K}\cup -$ 给同构 $G_{L/K}^{\mathrm{ab}}\cong A_K/N_{L/K}(A_L)$。于是「理想类群 ↔ Abel 扩张」的对应不必分别证局部与全局——它是公理的**直接推论**。Ch 6、Ch 7 只需验证局部 / 全局各自构成类形成，互反律即自动掉出。
- **飞腾锚点**：**TLB 4.81×** —— 类形成是一个「地址翻译表（TLB）」：把每个扩张 $L/K$ 的「范群 $N(A_L)$」（地址）映射到「Galois 群 $G^{\mathrm{ab}}$」（页号），基本类 $u_{L/K}$ 是翻译条目；局部化（Ch 6）与全局化（Ch 7）只是同一张表的两个实例化。
  - 🟢事实：互反律同构 $G^{\mathrm{ab}}_{L/K}\cong A_K/N(A_L)$ 是基本类的 cup product，tower 相容性由公理 (P2) 的限制相容性直接保证，无需逐扩张重证。
  - 🟡类比：抽象类域论 =「一次写好翻译协议（公理），局部/全局各填一张表」——这就是 Neukirch 比上同调派「更自洽」的根源。
- **关键定理**：**抽象互反律（类形成主定理）**：设 $(G,\{G_K\},\{A_K\})$ 是类形成，$u_{L/K}\in H^2(G_{L/K},A_L)$ 基本类。则 cup product 诱导同构
$$G_{L/K}^{\,\mathrm{ab}}\xrightarrow{\ \sim\ }A_K\big/N_{L/K}(A_L),\qquad \sigma\mapsto u_{L/K}\cup\sigma,$$
且与 tower 相容（取极限得 $G_K^{\mathrm{ab}}\cong A_K/\bigcap_L N(A_L)$）。推论：存在性定理——$A_K$ 的每个有限指标开子群恰是某有限 Abel 扩张的范群。
- **自测**：验证「$\mathbb{Q}_p$ 处的类形成」的 $A_K$ 是什么？答：取 $G=G_{\mathbb{Q}_p}$（绝对 Galois 群），$A_K=K^*=\mathbb{Q}_p^*$（$G_K$ 作用为 Galois 作用）。(P1) 即局部 Hilbert 90（$H^1(G_{L/K},L^*)=0$）；(P2) 的不变量 $\mathrm{inv}_{\mathbb{Q}_p}:H^2(G_{\mathbb{Q}_p},\overline{\mathbb{Q}_p}^{\,*})\cong\mathrm{Br}(\mathbb{Q}_p)\cong\mathbb{Q}/\mathbb{Z}$ 由非分歧不变量给出。代入主定理得 Ch 6 的局部互反律。

**类形成两公理速记 + 两个化身的载体**（Neukirch 全书最核心的抽象，对照 $A_K$ 选型）：

| 模型 | $G$（profinite 群） | $A_K$（载体模） | (P1) | (P2) 不变量 |
|---|---|---|---|---|
| **局部**（Ch 6） | $G_K$，$K$ 局部域 | $A_K=K^*$ | $H^1(G_{L/K},L^*)=0$（局部 Hilbert 90） | $\mathrm{Br}(K)\cong\mathbb{Q}/\mathbb{Z}$（非分歧） |
| **全局**（Ch 7） | $G_K$，$K$ 数域 | $A_K=C_K=\mathbb{A}_K^*/K^*$（idèle 类群） | $H^1(G_{L/K},C_L)=0$（全局 Hilbert 90） | $\mathrm{inv}_K=\sum_v\mathrm{inv}_{K_v}$（局部和） |

核心：$A_K$ 的选择是关键——局部用 $K^*$（乘法群），全局用 $C_K$（idèle 类群，模掉主 idèle）。基本类 $u_{L/K}\in H^2$ 在两模型中分别是局部/全局规范类，代入即得各自的互反律。**这就是 Neukirch 的「统一」：换载体 $A_K$，同一公理产出两套理论。**

---

### 第 6 章 · Local Class Field Theory（局部类域论）

- **核心**：本章是 Ch 5 抽象框架的**第一个化身**：取 $G=G_K$（局部域 $K$ 的绝对 Galois 群），$A_K=K^*$，验证它构成类形成（(P1) 局部 Hilbert 90，(P2) $\mathrm{Br}(K)=H^2(G_K,K^*)\cong\mathbb{Q}/\mathbb{Z}$ 由非分歧不变量给出）。代入 Ch 5 主定理得**局部 Artin 互反律**：对有限 Abel 扩张 $L/K$，
$$K^*\big/N_{L/K}(L^*)\xrightarrow{\ \sim\ }\mathrm{Gal}(L/K),\qquad \pi\mapsto\mathrm{Frob}_{L/K}$$
（$\pi$ 为 uniformizer），即「乘法群 = 交换 Galois 群」。**Brauer 群** $\mathrm{Br}(K)\cong\mathbb{Q}/\mathbb{Z}$：中心单 $K$-代数（如四元数）的 Morita 类被「相位」$\mathbb{Q}/\mathbb{Z}$ 完全分类。存在性定理：$K^*$ 的每个有限指标闭子群恰是某 Abel 扩张的范群（Lubin-Tate 形式群给显式构造）。与 Serre GTM67 用上同调证的版本是同一结论，Neukirch 用抽象框架「免费」得到。
- **飞腾锚点**：**matmul 15×** —— 局部互反律 $\theta:K^*/N(L^*)\xrightarrow{\sim}\mathrm{Gal}(L/K)$ 是「乘法群（一维）→ Galois 群（表示矩阵）」的同态，把一维的范数商映成 Galois 群的交换化；如把标量运算（matmul 的单点）提升为群表示矩阵的批量运算。
  - 🟢事实：非分歧扩张 $L/K$，$[L:K]=f$ 时 $\theta(\pi)=\mathrm{Frob}$（$x\mapsto x^p$ on $\mathbb{F}_{p^f}$，阶 $f$），单位群 $U_K\subset N(L^*)$ 被「吃掉」，$\theta$ 只看见 uniformizer 的赋值。
  - 🟡类比：$\mathrm{Br}(K)\cong\mathbb{Q}/\mathbb{Z}$ = 把所有中心单代数打分到「绕一圈的相位」，四元数代数 $\mathrm{inv}=\frac12$（半圈）。
- **关键定理**：**局部 Artin 互反律**：设 $L/K$ 有限 Abel 扩张（$K$ 局部域），则 Artin 映射（范剩余符号）
$$\theta_{L/K}:K^*\big/N_{L/K}(L^*)\xrightarrow{\ \sim\ }\mathrm{Gal}(L/K)$$
是同构，与 tower 相容。取极限 $\theta:K^*\to\mathrm{Gal}(K^{\mathrm{ab}}/K)$，核 $=\bigcap_L N(L^*)$。等价地 $\mathrm{Br}(K)=H^2(G_K,K^*)\cong\mathbb{Q}/\mathbb{Z}$。
- **自测**：$\mathbb{Q}_5$ 的唯一非分歧 2 次扩张 $L/\mathbb{Q}_5$（剩余域 $\mathbb{F}_{25}$）。写出 Artin 映射在 uniformizer $5$ 与单位 $u\in\mathbb{Z}_5^*$ 上的值。答：非分歧，$\theta(5)=\mathrm{Frob}$（$x\mapsto x^5$ on $\mathbb{F}_{25}$，阶 2）；$\theta(u)=1$（单位全在范群 $N(L^*))$，因非分歧范数 $N:U_K\to U_K$ 满）。$K^*/N(L^*)\cong\mathbb{Z}/2$ 由 $v_5$ 诱导。

**局部 Artin 映射在不同扩张上的取值**（局部互反律的「查表」用法）：

| 扩张 $L/K$ | $G=\mathrm{Gal}(L/K)$ | $\theta$ 在 $\mathcal{O}_K^*$（单位）上 | $\theta$ 在 uniformizer $\pi$ 上 |
|---|---|---|---|
| 非分歧（$e=1,f=n$） | $\cong\mathbb{Z}/n$（Frob 生成） | 平凡（单位全在范群） | $\pi\mapsto\mathrm{Frob}$（生成元） |
| 全分歧 tame | 惯性群 $\cong\mu_n(k)$ | $\theta\|_{U_0}\twoheadrightarrow\mu_n$ | $\pi\mapsto1$ |
| 全分歧 wild | $p$-群 | 高度非平凡（主单位群满射） | $\pi\mapsto1$ |

核心：非分歧扩张的 Artin 映射只「看见」uniformizer 的赋值（$v_K:K^*\to\mathbb{Z}$），单位群被范数吃掉；分歧扩张则「看见」单位群结构——分歧越深，互反律越精细。

---

### 第 7 章 · Global Class Field Theory（全局类域论）

- **核心**：本章是 Ch 5 抽象框架的**第二个化身，也是全书顶峰**。取 $G=G_K$（数域 $K$ 的绝对 Galois 群），$A_K=C_K=\mathbb{A}_K^*/K^*$（**idèle 类群**——Adèle 群模掉主 idèle），验证它构成类形成。(P2) 的全局不变量 $\mathrm{inv}_K:H^2(G_K,C_K)\xrightarrow{\sim}\mathbb{Q}/\mathbb{Z}$ 由「局部不变量之和」$\sum_v\mathrm{inv}_{K_v}=0$（Hasse-Brauer-Noether）给出。代入主定理得**全局 Artin 互反律**：对有限 Abel 扩张 $L/K$，
$$C_K\big/N_{L/K}(C_L)\xrightarrow{\ \sim\ }\mathrm{Gal}(L/K),\qquad \mathfrak p\mapsto\mathrm{Frob}_\mathfrak p.$$
特例 **Hilbert 类域** $H$：$K$ 的极大非分歧 Abel 扩张，$\mathrm{Gal}(H/K)\cong\mathrm{Cl}(K)$（理想类群），$[H:K]=h_K$——「类群 = 非分歧 Abel Galois 群」。**解析侧**：Dirichlet $L$-函数 $L(s,\chi)$ 在 $s=1$ 非零（$\chi\ne1$）给出类数有限；类数公式 $\mathrm{Res}_{s=1}\zeta_K(s)=\frac{2^{r_1}(2\pi)^{r_2}h_KR_K}{w_K\sqrt{|d_K|}}$ 把代数不变量与解析留数焊死。
- **飞腾锚点**：**GEMM 9.45 GFLOPS** —— 全局 Artin $L$-函数 $L(s,\rho)=\prod_\mathfrak p\det(1-\rho(\mathrm{Frob}_\mathfrak p)N\mathfrak p^{-s})^{-1}$ 的 Euler 乘积对每个素理想做一次表示矩阵 $\rho(\mathrm{Frob}_\mathfrak p)$ 的特征多项式（GEMM 矩阵计算），再连乘；idèle 类群 $C_K$ 把所有素数处的局部信息（$\prod_v K_v^*$）打包成全局，如高维矩阵吞吐。
  - 🟢事实：$\mathrm{Gal}(H/K)\cong\mathrm{Cl}(K)$ 是精确同构，$[H:K]=h_K$；非分歧素理想 $\mathfrak p$ 在 $H$ 中完全分裂 $\Leftrightarrow$ $\mathfrak p$ 主。Hasse 原理：局部非分歧的代数整体非分歧。
  - 🟡类比：idèle 类群 =「把每个素数处的局部 Galois 群（局部页）拼成全局 Galois 群（全册）」，Artin 互反律是「局部页 → 全册」的装订线。
- **关键定理**：**全局 Artin 互反律**：设 $L/K$ 有限 Abel 扩张（$K$ 数域），则 Artin 映射诱导同构
$$C_K\big/N_{L/K}(C_L)\xrightarrow{\ \sim\ }\mathrm{Gal}(L/K),\qquad \mathfrak p\mapsto\mathrm{Frob}_\mathfrak p\ (\mathfrak p\text{ 非分歧}),$$
$C_K=\mathbb{A}_K^*/K^*$ 为 idèle 类群。特例（Hilbert 类域 $H$）：$\mathrm{Cl}(K)\cong\mathrm{Gal}(H/K)$，$[H:K]=h_K$。配合 Dirichlet $L(1,\chi)\ne0$（$\chi\ne\mathbf{1}$）得类数有限。
- **自测**：求 $\mathbb{Q}(\sqrt{-5})$ 的 Hilbert 类域 $H$ 的次数与 Galois 群。答：$h_K=2$（Ch 1 自测），故 $[H:K]=2$，$\mathrm{Gal}(H/K)\cong\mathbb{Z}/2$。事实上 $H=\mathbb{Q}(\sqrt{-5},\sqrt{-1})=\mathbb{Q}(\sqrt5,i)$（$-5$ 的类数 2 对应二次类域扩张）。验证：素理想 $\mathfrak p=(2,1+\sqrt{-5})$ 在 $H$ 中完全分裂 $\Leftrightarrow$ $\mathfrak p$ 主——但 $\mathfrak p$ 非主，故 $\mathfrak p$ 在 $H$ 中**不**完全分裂，Frobenius 是非平凡元，吻合互反律。

**全局互反律的三种语言对照**（同一理论的三个面孔，Neukirch 选 idèle 语言）：

| 语言 | 载体 | 互反律陈述 | 优点 |
|---|---|---|---|
| **idèle 类群**（Neukirch） | $C_K=\mathbb{A}_K^*/K^*$ | $C_K/N(C_L)\cong\mathrm{Gal}(L/K)$ | 局部信息一次性打包，局部↔全局统一 |
| **理想/射线类群**（古典） | $I_K^{\mathfrak m}/P_{\mathfrak m}$ | 射线类群 $\cong\mathrm{Gal}(L/K)$ | 计算友好，给显式 Hilbert 类域 |
| **上同调**（Serre/Artin-Tate） | $H^2(G_K,C_K)\cong\mathbb{Q}/\mathbb{Z}$ | cup product 给互反律 | 唯一性、tower 相容性干净 |

核心：Neukirch 用 idèle 类群 $C_K$ 是因为它**天然编码所有素数处的局部信息**——$C_K=\mathbb{A}_K^*/K^*=\prod_v' K_v^*/K^*$（限制直积模主 idèle），使全局互反律成为局部互反律的「粘合」。这是「读完 Neukirch 才真正理解 idèle 为何存在」的根源。

---

## §9 全书思想主线：Neukirch 两段式——代数局部地基 → 抽象类域论顶峰

Neukirch 的全书是**两段式收束**，后一段比前一段远更整合。**第一段（Ch 1–4，地基）**搭「代数 + 局部 + 几何」三块基石：Ch 1 给代数整数环与理想唯一分解（Dedekind 域），Ch 2 研究素理想在扩域中的分解与 Frobenius（互反律的主角在此登场），Ch 3 用赋值论与完备化建立「一个素数处」的局部语言（Hensel 让逼近变代数），Ch 4 插入函数域的 Riemann-Roch 作为「几何镜子」——亏格 $g$ 与类数 $h_K$ 的对偶，为抽象框架提供几何动机。这一段的灵魂是**「局部化让全局问题可看」**——把数域的困难分解到每个素数处，再用完备化精确化。**第二段（Ch 5–7，顶峰）**是全书灵魂：Neukirch 发明**抽象类域论**（类形成公理），仅凭 (P1) 维数≤1 + (P2) 不变量两条公理，基本类就诱导出互反律同构 $G^{\mathrm{ab}}\cong A_K/N(A_L)$。于是局部类域论（$A_K=K^*$，Ch 6）与全局类域论（$A_K=C_K$ idèle 类群，Ch 7）**不再是两个理论，而是同一抽象的两个化身**——这是 Neukirch 比上同调派（Serre / Artin-Tate）「更自洽」、比 Lang（分别证局部全局）「更统一」的根源。

**与已读教材的呼应**：本书与 **Lang GTM110** 形成「互补」——Lang 把代数、解析、类域论三线分别讲透（Ch 9 局部、Ch 10 全局各成一章），Neukirch 用抽象框架把两线焊成一根，读 Lang 后读 Neukirch 能看清「为什么局部与全局是同一回事」。与 **Janusz**（同期生成笔记）形成「对照」——Janusz 节奏温和适合第一遍系统学，Neukirch 抽象度高适合第二遍「提纯」。与 **Silverman 椭圆曲线 GTM106** 形成「应用」——椭圆曲线的复乘理论（Hilbert 类域的显式生成）直接用 Neukirch 的 Hilbert 类域 $\mathrm{Gal}(H/K)\cong\mathrm{Cl}(K)$。Neukirch 的「压缩术」可复刻：(1) 用 idèle 类群 $C_K$ 而非理想类群作全局类域论的载体，把所有局部信息一次性打包；(2) 用抽象公理（类形成）代替具体上同调计算，让局部全局统一；(3) 把 Frobenius $\mathrm{Frob}_\mathfrak p$ 作为「素理想 ↔ Galois 元」的翻译器贯穿 Ch 2 至 Ch 7。这三步压缩使本书成为「读完一遍即建立全局视野」的范本。

---

## §10 与本仓库其他笔记的交叉引用

### 与已精读书目的呼应

| 本书 | 关系 | 交叉点 |
|---|---|---|
| **Lang** GTM110 代数数论 | 互补 | Lang 分别证局部（Ch 9）/全局（Ch 10）类域论，Neukirch 用抽象框架统一；Lang 给解析全景，Neukirch 给代数自洽 |
| **Janusz** 代数数域 | 对照 | Janusz 节奏温和适合第一遍，Neukirch 抽象度高适合第二遍提纯；两书覆盖相近但深度梯度不同 |
| **Serre** GTM67 局部域 | 上同调 vs 抽象 | Serre 用 Galois 上同调证局部类域论（$H^2\cong\mathbb{Q}/\mathbb{Z}$），Neukirch 用类形成公理「免费」得到；Neukirch Ch 6 = Serre Ch III 的抽象版 |
| **Silverman** GTM106 椭圆曲线 | 应用 | Silverman 复乘理论用 Hilbert 类域 $\mathrm{Gal}(H/K)\cong\mathrm{Cl}(K)$（Neukirch Ch 7）；椭圆曲线的 Tate 局部分析用 Ch 3 完备化 |
| **Ireland-Rosen** GTM84 | 前置 | IR 给整体数论入门骨架（Dedekind 域、类数、分圆域），Neukirch Ch 1–2 是其升级；IR 的初等类数公式 ↔ Neukirch Ch 7 解析公式 |
| **Washington** 分圆域（候选） | 深化 | Washington 用 Iwasawa 理论深化 Neukirch Ch 7 的分圆域类域论；$\mathbb{Z}_p$-扩张的类数渐近是 Neukirch 之后的专题 |

### AI/工程锚点法：代数数论的工程落地

| 数学概念 | AI/工程对应 | 锚点说明 |
|---|---|---|
| **Minkowski 嵌入 / 格 $\Lambda$** | LLL 格归约 / 格密码 | 🟢$\mathcal{O}_K\hookrightarrow\mathbb{R}^n$ 成格，Gram-Schmidt 正交化是 LLL 算法的核心步骤；格归约在 ML（特征选择）与密码学（NTRU、LWE）中是基础工具 |
| **素理想分解（split/inert/ramify）** | 分支预测 / 模式分类 | 🟡每个素数的三分支判定 = 一次模式分类；Frobenius 把分类结果编码成 Galois 元 |
| **$p$-adic 完备化 / Hensel 提升** | Newton 法 / 数值精度 | 🟢Hensel = 模 $p$ 版 Newton，二次收敛、无误差累积；$p$-adic 数值方法用于编码理论与计算数论 |
| **Riemann-Roch（函数域）** | 维度预算 / 信息率 | 🟡RR 定理 $\ell(D)=\deg D+1-g+\ell(K-D)$ 是「可用函数维数」的预算公式；Goppa 几何码用 RR 算码的参数 $[n,k,d]$ |
| **类形成 / 抽象互反律** | 协议抽象 / 接口设计 | 🟡类形成 =「一次定义协议（公理），局部/全局各实现」——与软件工程的接口抽象同构 |
| **Artin $L$-函数 Euler 积** | 矩阵特征值分解 / GEMM | 🟡$L(s,\rho)=\prod_\mathfrak p\det(1-\rho(\mathrm{Frob}_\mathfrak p)N\mathfrak p^{-s})^{-1}$ = 按素数做表示矩阵分解再连乘 |
| **Hilbert 类域 $\mathrm{Gal}(H/K)\cong\mathrm{Cl}(K)$** | 密码学 / 椭圆曲线 | 🟢类域论是椭圆曲线密码（ECC）的代数底座；复乘用 Hilbert 类域显式生成类多项式，用于 ECC 参数选取 |
| **Dirichlet $L(1,\chi)\ne0$** | 解析数论 / RSA 安全 | 🟢$L(1,\chi)$ 非零保证类数有限；素数分布（Dirichlet 定理）是 RSA 大素数生成的理论基础 |

**锚点法的统一视角**：Neukirch 全书可用两句话锚定——**「局部化让全局可看（Ch 1–3），抽象公理让局部全局统一（Ch 5–7）」**。第一步是几何（Minkowski 格、完备化）让数域的困难分解到素数处；第二步是代数（类形成公理）让局部与全局成为同一理论的两面。这两步压缩贯穿全书，掌握这条主线，全书的「为什么用 idèle、为什么用抽象公理」就豁然开朗。

### 代数数论学习常见误区（跨章汇总）

| 误区 | 正确理解 | 出处 |
|---|---|---|
| 元素唯一分解 = 理想唯一分解 | 仅理想必唯一分解；元素未必（$\mathbb{Z}[\sqrt{-5}]$） | Ch 1 |
| Frobenius 对任意扩张定义 | 仅**非分歧**素理想有 Frobenius；分歧时需惯性群 | Ch 2 |
| Hensel 能提升任何根 | 仅提升**单根**（$\bar f'\ne0$），重根需更强工具 | Ch 3 |
| 完备化 = 闭包 | 完备化是 Cauchy 列等价类，比拓扑闭包强（保代数结构） | Ch 3 |
| Riemann-Roch 仅对数域 | RR 是**函数域**（有限域上曲线）定理；数域的对应是类数公式 | Ch 4 |
| Neukirch 用上同调证类域论 | Neukirch **拒绝上同调**，用抽象类形成公理；上同调派是 Serre/Artin-Tate | Ch 5 |
| 局部与全局是两个理论 | 是同一抽象（类形成）的两个化身：$A_K=K^*$（局部）、$A_K=C_K$（全局） | Ch 5–7 |
| Hilbert 类域 = 极大扩张 | 仅**极大非分歧 Abel** 扩张；含分歧的更大扩张由射线类域给 | Ch 7 |
| 全局互反律用理想类群 | Neukirch 用 **idèle 类群** $C_K$ 作载体，理想类群是其在模 $\mathfrak m$ 后的商 | Ch 7 |

---

## §11 自测答案要点（供核对）

1. **Ch 1** $\mathbb{Q}(\sqrt{-5})$：$(2)=\mathfrak p^2$（$\mathfrak p=(2,1+\sqrt{-5})$），$\mathfrak p$ 非主（$|N\alpha|=2$ 需 $a^2+5b^2=2$ 无解），$\mathfrak p^2=(2)$ 主故 $\mathfrak p$ 阶 2，$\mathrm{Cl}\cong\mathbb{Z}/2$。
2. **Ch 2** $7,3$ 在 $\mathbb{Q}(\sqrt{-5})$：$d_K=-20$，$7,3\nmid20$ 非分歧。$(\frac{-5}{7})=(\frac{2}{7})=1$（$7\equiv-1\pmod8$）故 $7$ 分裂；$(\frac{-5}{3})=(\frac{1}{3})=1$ 故 $3$ 分裂；$2,5\mid20$ 分歧。
3. **Ch 3** $x^2=2$ 在 $\mathbb{Q}_7$：$\bar\alpha=3$ 单根（$\bar f'(3)=6\not\equiv0$），Hensel Newton 迭代 $\alpha_0=3$，$6^{-1}\bmod7=6$，收敛得 $\alpha\in\mathbb{Z}_7$，$\alpha\equiv3\pmod7$。
4. **Ch 4** $\mathbb{F}_3(t)$，$D=P_{t=0}$：$g=0$，$\ell(D)=\deg D+1+\ell(K-D)$，$K=-2P_\infty$，$\deg(K-P)=-3<0$ 故 $\ell(K-P)=0$，$\ell(D)=2$（基 $\{1,t\}$）。
5. **Ch 5** $\mathbb{Q}_p$ 类形成：$G=G_{\mathbb{Q}_p}$，$A_K=K^*$。(P1) 局部 Hilbert 90 $H^1(G_{L/K},L^*)=0$；(P2) $\mathrm{Br}(\mathbb{Q}_p)=H^2(G_{\mathbb{Q}_p},\overline{\mathbb{Q}_p}^{\,*})\cong\mathbb{Q}/\mathbb{Z}$（非分歧不变量）。代入主定理得 Ch 6 局部互反律。
6. **Ch 6** $\mathbb{Q}_5$ 非分歧 2 次 $L$：$\theta(5)=\mathrm{Frob}$（$x\mapsto x^5$ on $\mathbb{F}_{25}$，阶 2），$\theta(u)=1$（$u\in\mathbb{Z}_5^*$，单位在范群），$K^*/N(L^*)\cong\mathbb{Z}/2$。
7. **Ch 7** $\mathbb{Q}(\sqrt{-5})$ Hilbert 类域：$h_K=2$ 故 $[H:K]=2$，$\mathrm{Gal}(H/K)\cong\mathbb{Z}/2$，$H=\mathbb{Q}(\sqrt5,i)$。$\mathfrak p=(2,1+\sqrt{-5})$ 非主，故在 $H$ 中不完全分裂，Frobenius 非平凡 ✓。

---

## §12 延展阅读与后续方向

读完 Neukirch，自然有三个深入方向：

1. **类域论的构造面（Lubin-Tate）**：Serre GTM67 之后 / Neukirch 未讲的「存在性定理的显式构造」——Lubin-Tate 形式群用形式群对数显式生成局部 Abel 扩张，补 Neukirch Ch 6 的「构造缺口」。
2. **Iwasawa 理论**：Washington《分圆域》（GTM83）把 Neukirch Ch 7 的分圆类域论深化为 $\mathbb{Z}_p$-扩张上的类数渐近（Iwasawa 公式 $p^{\mu p^n+\lambda n+\nu}$），主猜想（Mazur-Wiles）是顶峰。
3. **算术几何 / Langlands**：Silverman《Advanced Topics》（椭圆曲线复乘 + Hilbert 类域显式生成）、Hartshorne GTM52（概形语言底座）；Langlands 纲领把 Artin $L$-函数推广为自守 $L$-函数。

**与已读笔记的闭环**：Ireland-Rosen（整体骨架）→ Serre GTM67（局部锋利，上同调版）→ **Neukirch（抽象统一，本书）** → Lang GTM110（解析全景）→ Silverman（算术几何应用）。四书合起来是「代数数论 + 算术几何」标准研究入门组合。

**研究者方向取舍建议**：若偏**计算/算术几何**（椭圆曲线、密码），优先 Ch 1（理想论）+ Ch 7（Hilbert 类域，ECC 底座）+ Ch 3（Hensel，Tate 算法）；Ch 4–6 按需。若偏**纯代数数论/类域论**，Ch 5 抽象框架是灵魂，Ch 6–7 是两个化身必精读。若偏**ML 理论/格归约**，Ch 1 Minkowski 格 + LLL 是格密码（LWE/NTRU）与 ML 特征选择的代数桥梁。本书的「抽象统一」结构允许按方向取舍，但 Ch 5（抽象类域论）+ Ch 7（Hilbert 类域 + idèle）是所有方向共享的两大焊接点。

> **一句话总结**：Neukirch 用「类形成」两条公理一举贯通局部与全局类域论——读完它，你看类域论不再是「局部一套、全局一套」，而是同一抽象框架的两个化身，乘法群与 Galois 群互为镜像。

---

> **精读纪律**：本文为快速逐章精读，每章取 1 个飞腾锚点 + 1 个关键定理 + 1 道自测题。深入计算与完整证明请回原书（Neukirch 的抽象类域论 Ch 5 是全书最原创、最值得逐字精读的一章）。🟢 = 事实锚点（可直接引用），🟡 = 类比锚点（仅供直觉，不可引用于严格证明）。
>
> **实操验证建议**（SageMath / PARI-GP）：
> - `K = NumberField(x^2+5)` → `.class_group()` 验证 Ch 1 / Ch 7 类数与 Hilbert 类域
> - `K.ideal(7).factor()` / `K.ideal(3).factor()` → 验证 Ch 2 素理想分裂
> - `Qp(7)` → `Zp(7)` 验证 Ch 3 Hensel 提升 $x^2=2$
> - `L = FunctionField(GF(3),'t')` → 用 Riemann-Roch 算 $\ell(D)$ 验证 Ch 4
> - `hilbert_class_polynomial(D)` → 验证 Ch 7 Hilbert 类域（如 $D=-20$ 给 $x^2-4$，$H=\mathbb{Q}(\sqrt5,i)$）
> - `gp.` 中 `bnrclassunit` / `artln` → 验证 Ch 6–7 Artin 互反律与 idèle 类群商
