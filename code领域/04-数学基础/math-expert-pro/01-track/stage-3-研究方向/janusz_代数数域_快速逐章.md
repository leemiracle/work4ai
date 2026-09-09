# Gerald J. Janusz《代数数域》 · 快速逐章精读

> 基于原书：Algebraic Number Fields, 2nd Edition (AMS Graduate Studies in Mathematics Vol. 7, Gerald J. Janusz, 1996；初版 1973 Academic Press) / 读于：2026-07-03
> 定位：**面向初学者的「读得懂」的代数数论系统教材**，以具体数域例子驱动教学，节奏温和、计算详尽，是自学代数数论的第一本首选。
> 本文为**快速逐章精读**，全书 8 章，每章 1 个飞腾锚点（8 锚池一一对应、每锚恰好用 1 次）+ 1 个关键定理 + 1 道自测题。

---

## §0 引言：Janusz 代数数域是什么，为什么读它

Gerald J. Janusz《Algebraic Number Fields》（AMS GSM Vol. 7，初版 1973、二版 1996）是代数数论领域**最适合自学入门**的系统教材之一。与 Neukirch（现代公理化、整体+局部双线）、Lang GTM110（百科全书式高密度、代数+解析+类域论三合一）不同，Janusz 的笔法是**「手把手、多算例」**——每个概念给出后立刻配具体数域计算（$\mathbb{Q}(i)$、$\mathbb{Q}(\sqrt{2})$、$\mathbb{Q}(\zeta_5)$ 反复出现），证明步骤完整不跳，习题梯度合理。全书从代数预备（域论、Galois 理论回顾）出发，经代数整数、整基与判别式、理想理论、单位群、扩域分歧，到局部域与 $L$-函数类数公式，构成一条**自洽的「先整体后局部」教学线**。

读它的核心理由：作为数学零基础补课的工程师，直接啃 Lang 或 Neukirch 容易被高密度形式化压垮——Janusz 是最好的「缓坡道」。它用 $\mathbb{Q}(\sqrt{d})$ 的理想分解手算让你**先建立手感**，再用 Minkowski 几何把类群有限性「画」出来，最后才引入 $\zeta_K(s)$ 的解析类数公式——每一步都有计算锚点，不悬空。与 Marcus《Number Fields》（同样亲民、但更偏习题驱动）相比，Janusz 的正文更完整，适合「只读一本书」；与 Ireland-Rosen（整体数论骨架、初等优先）相比，Janusz 更系统地把局部域与 $L$-函数纳入。**最佳递进路线**：先 Janusz 建立整体骨架与计算手感 → 再 Neukirch 补局部域与类域论的系统对照 → 最后 Lang GTM110 做整合复习与查漏。

| 书 | 风格 | 严格性 | 适合谁 |
|---|---|---|---|
| **Janusz** GSM7 | 温和自学，具体数域例题驱动，证明完整不跳 | ★★★★☆ 友好 | 零基础自学代数数论第一本 |
| **Neukirch**《Algebraic Number Theory》 | 现代公理化，整体域+局部域双线并进，最系统自洽 | ★★★★★ 自洽 | 系统学数论，要整体与局部对照 |
| **Lang** GTM110 | 高密度形式化，代数+解析+类域论三合一，习题即正文 | ★★★★★ 每步需补 | 追求代数数论完整蓝图、已具成熟度 |
| **Marcus**《Number Fields》 | 习题驱动，大量手算练习，覆盖面与 Janusz 相近 | ★★★★☆ 友好 | 喜欢做题巩固、要更多计算练习 |

**阅读心法**：Janusz 的书**可以顺读**——不像 Lang 需要「自带成熟度补全」。建议每章读完立刻用 $\mathbb{Q}(\sqrt{2})$ 或 $\mathbb{Q}(\sqrt{-5})$ 做一遍手算（理想分解、类数、单位），把抽象定义变成肌肉记忆。Ch 1（代数预备）可快读复习，Ch 2–4（整数、整基、理想）是核心甜区，Ch 5（单位）与 Ch 6（扩域分歧）用 Minkowski 几何串联，Ch 7（局部域）引入 $p$-adic 视角，Ch 8（$L$-函数）是解析收官。全书精读约 50–70 小时（每周 10–20h，4–6 周）。

**Janusz 的三大教学特色**（区别于 Lang / Neukirch 的关键）：

| 特色 | 具体表现 | 对零基础读者的价值 |
|---|---|---|
| **例子先行** | 每个定义后立刻配 $\mathbb{Q}(\sqrt{d})$ 手算，而非先给最一般定理 | 把抽象概念锚定到可验证的具体计算 |
| **证明完整** | 不用「留作习题」「易证」压缩步骤，关键推导逐行写出 | 读者不需自带成熟度，可独立验证每步 |
| **梯度习题** | 从直接验证到中等难度的渐进习题，无突然跳跃 | 每章后能独立完成 60%–70% 习题，建立信心 |

**全书的「教学驱动」哲学**：Janusz 不追求最一般性，而追求**可理解性**。他先在 $\mathbb{Q}(\sqrt{d})$ 上把理想分解算给你看，再抽象到 Dedekind 域；先在二次域给类数公式，再推广到一般数域的 $\zeta_K$ 留数。这种「具体→抽象」的路径，正是零基础学习者最需要的认知脚手架。读完 Janusz，再读 Neukirch 或 Lang 时，你会发现那些「高观点」不过是 Janusz 手算例子的系统化推广。

**全书的两大「顿悟时刻」**：第一次顿悟在 Ch 4——发现 $\mathbb{Z}[\sqrt{-5}]$ 中元素 $6=2\cdot3=(1+\sqrt{-5})(1-\sqrt{-5})$ 不唯一分解，但理想 $(6)=\mathfrak{p}^2\mathfrak{q}_1\mathfrak{q}_2$ 唯一分解——「元素失败，理想成功」是 Dedekind 的天才补救。第二次顿悟在 Ch 8——发现 Dedekind $\zeta$ 函数 $\zeta_K(s)$ 在 $s=1$ 的留数竟**精确等于** $\frac{2^{r_1}(2\pi)^{r_2}h_KR_K}{w_K\sqrt{|d_K|}}$——「解析留数 = 代数不变量」把 Ch 1–6 的全部计算焊成一行公式。这两个顿悟分别代表代数补救（Ch 4）与解析统一（Ch 8），是全书认知的双重高潮。

---

## §1 全书 8 章骨架一览（飞腾锚点分布）

| 章 | 标题 | 核心概念 | 飞腾锚点 |
|:-:|------|---------|---------|
| 1 | Algebraic Preliminaries（代数预备） | 域论、Galois 理论回顾、有限扩张 | **matmul 15× [V03]** |
| 2 | Algebraic Numbers and Integers（代数数与代数整数） | 代数整数、整数环 $\mathcal{O}_K$、整闭包 | **TLB 4.81× [E04]** |
| 3 | Integral Bases and Discriminants（整基与判别式） | 迹、范数、判别式、整基存在 | **UDOT 16.9× [E05]** |
| 4 | Ideal Theory（理想理论） | Dedekind 整环、素理想唯一分解、类群、类数 | **GEMM 9.45G [Lab05]** |
| 5 | Units（单位群） | Dirichlet 单位定理、$S$-单位、Minkowski 几何 | **Schmidt 正交化** |
| 6 | Extensions of Number Fields（扩域） | 分歧、分解群、惯性群、Frobenius、Hilbert 类域 | **分支预测 [Lab02]** |
| 7 | Local Fields（局部域） | $p$-adic 数、Hensel 引理、局部域结构、Tame 分歧 | **FP16 3.81× [L01]** |
| 8 | L-functions and Class Number Formulas（$L$-函数与类数公式） | Dirichlet $L$-函数、Dedekind $\zeta$、解析类数公式 | **Iron Law <2% [Lab00]** |

---

### 第 1 章 · Algebraic Preliminaries（代数预备：域论与 Galois 理论回顾）

- **核心**：本章是**前置复习**，不引入新数论，而是把后续 7 章要反复用的代数工具一次整理：域的有限扩张（$[K:\mathbb{Q}]<\infty$）、代数扩张与超越扩张、极小多项式、**Galois 理论基本定理**（子群↔中间域一一对应）、分裂域与正规扩张、可分性。Janusz 的处理比 Lang 温和得多——先给 $\mathbb{Q}(\sqrt{2})$、$\mathbb{Q}(\zeta_5)$ 的 Galois 群手算，再抽象到一般定理。本章的核心信息：数域 $K/\mathbb{Q}$ 总是有限可分扩张，其 Galois 闭包的子群格决定所有中间域。
- **飞腾锚点**：**matmul 15× [V03]** —— Galois 群的每个元素 $\sigma\in\mathrm{Gal}(L/K)$ 是 $L$（作为 $K$-向量空间）上的线性变换，可表为 $n\times n$ 矩阵；Galois 群作用 = 矩阵群的子群，群运算即矩阵乘法（matmul）。
  - 🟢事实：$\sigma$ 在整基 $\{\omega_1,\ldots,\omega_n\}$ 上的矩阵 $(\sigma(\omega_j)$ 坐标列$)$ 是整数矩阵，行列式 $=\pm1$（保体积，$\sigma$ 是格自同构）。
  - 🟡类比：Galois 对应「子群↔子域」如矩阵的「不变子空间↔不变因子」，正规子群↔Galois 中间域如分块对角化。
- **关键定理**：**Galois 理论基本定理**：设 $L/K$ 有限 Galois 扩张，$G=\mathrm{Gal}(L/K)$，则中间域 $K\subseteq M\subseteq L$ 与子群 $H\le G$ 之间有反序一一对应 $M\mapsto\mathrm{Gal}(L/M)$，$H\mapsto L^H$（不动点域），且 $[L:M]=|H|$，$M/K$ Galois $\Leftrightarrow$ $H\triangleleft G$。
- **自测**：$L=\mathbb{Q}(\zeta_5)$，$\mathrm{Gal}(L/\mathbb{Q})\cong(\mathbb{Z}/5)^*\cong\mathbb{Z}/4$（生成元 $\sigma_2:\zeta_5\mapsto\zeta_5^2$）。列出全部子群与对应中间域：$\langle\sigma_2\rangle$（全群，对应 $\mathbb{Q}$）、$\langle\sigma_2^2\rangle\cong\mathbb{Z}/2$（对应唯一的二次子域 $\mathbb{Q}(\sqrt5)$）、$\{1\}$（对应 $L$）。验证 $\mathbb{Q}(\sqrt5)=\mathbb{Q}(\zeta_5+\zeta_5^{-1})$（极大实子域）。

---

### 第 2 章 · Algebraic Numbers and Integers（代数数与代数整数）

- **核心**：**代数数**是 $\mathbb{Q}$ 上代数方程的根（即 $\overline{\mathbb{Q}}$ 的元素），**代数整数**是首一整系数多项式 $x^n+a_{n-1}x^{n-1}+\cdots+a_0\in\mathbb{Z}[x]$ 的根。关键事实：代数整数构成 $\overline{\mathbb{Q}}$ 的子环（和、积、差仍为整数），故数域 $K$ 的**代数整数环** $\mathcal{O}_K=\{x\in K:\text{代数整数}\}$ 良定义——它是 $\mathbb{Z}$ 在 $K$ 中的整闭包。经典例子：$\mathcal{O}_{\mathbb{Q}(i)}=\mathbb{Z}[i]$（Gauss 整数），$\mathcal{O}_{\mathbb{Q}(\sqrt{d})}=\mathbb{Z}[\frac{1+\sqrt{d}}{2}]$（$d\equiv1\pmod4$）或 $\mathbb{Z}[\sqrt{d}]$（否则）。本章建立「整性」的代数语言，为 Ch 3（整基）与 Ch 4（理想论）铺地基。
- **飞腾锚点**：**TLB 4.81× [E04]** —— $\mathcal{O}_K$ 是 $\mathbb{Z}$ 的「分层扩展」：$\mathbb{Z}\subset\mathcal{O}_K$，每个 $\mathcal{O}_K$-理想分层落在 $\mathbb{Z}$-子模上，如 CPU 的 TLB（翻译后备缓冲）把虚拟地址分层映射到物理地址——整闭包 = 把 $\mathbb{Z}$ 的「地址空间」扩展到 $K$ 的整数层。
  - 🟢事实：$\mathcal{O}_K\cap\mathbb{Q}=\mathbb{Z}$（有理代数整数恰为整数）；$\mathcal{O}_K$ 是 $\mathbb{Z}$ 上秩 $n=[K:\mathbb{Q}]$ 的自由 $\mathbb{Z}$-模（Ch 3 证）。
  - 🟡类比：整闭包 = 「把 $\mathbb{Z}$ 的因子分解能力扩展到 $K$」，但元素可能不再唯一分解——这正是 Ch 4 要用理想修复的「缺陷」。
- **关键定理**：**整性传递性**：设 $A\subseteq B\subseteq C$ 为环，$B$ 在 $A$ 上整，$C$ 在 $B$ 上整，则 $C$ 在 $A$ 上整。推论：$\mathcal{O}_K$ 是 $K$ 中所有代数整数的集合，且 $\mathcal{O}_K$ 整闭（在 $K$ 的分式域中）。
- **自测**：求 $\mathcal{O}_{\mathbb{Q}(\sqrt{-3})}$。答：$d=-3\equiv1\pmod4$，故 $\mathcal{O}_K=\mathbb{Z}[\frac{1+\sqrt{-3}}{2}]=\mathbb{Z}[\omega]$（$\omega=e^{2\pi i/3}=\frac{-1+\sqrt{-3}}{2}$，Eisenstein 整数）。验证 $\omega$ 满足首一整系数方程 $x^2+x+1=0$，是代数整数；而 $\frac{\sqrt{-3}}{2}$ 不是（极小多项式 $x^2+\frac34$ 非整系数）。比较 $\mathcal{O}_{\mathbb{Q}(\sqrt{5})}$：$5\equiv1\pmod4$，$\mathcal{O}=\mathbb{Z}[\frac{1+\sqrt5}{2}]$（黄金比例 $\varphi=\frac{1+\sqrt5}{2}$ 是整数）。

---

### 第 3 章 · Integral Bases and Discriminants（整基与判别式）

- **核心**：本章引入数域的三大数值不变量：**迹** $\mathrm{Tr}_{K/\mathbb{Q}}(\alpha)=\sum_{i=1}^n\sigma_i(\alpha)$（$n$ 个共轭之和）、**范数** $\mathrm{N}_{K/\mathbb{Q}}(\alpha)=\prod_{i=1}^n\sigma_i(\alpha)$（共轭之积）、**判别式** $d(\alpha_1,\ldots,\alpha_n)=\det(\mathrm{Tr}(\alpha_i\alpha_j))$。核心定理：$\mathcal{O}_K$ 作为 $\mathbb{Z}$-模是秩 $n$ 自由的，故存在**整基** $\{\omega_1,\ldots,\omega_n\}$（$\mathcal{O}_K=\mathbb{Z}\omega_1\oplus\cdots\oplus\mathbb{Z}\omega_n$），判别式 $d_K=d(\omega_1,\ldots,\omega_n)$ 与整基选取无关（差平方=单位平方）。判别式是数域的基本不变量：$|d_K|$ 越大，域越「扭曲」，类数（Ch 4）与单位（Ch 5）都受其控制。
- **飞腾锚点**：**UDOT 16.9× [E05]** —— 迹 $\mathrm{Tr}(\alpha)=\sum_i\sigma_i(\alpha)$ 是「$n$ 个共轭的点积累加」，如 UDOT（无符号点积累加）对向量做高效求和；判别式矩阵 $(\mathrm{Tr}(\alpha_i\alpha_j))$ 是共轭对的内积矩阵，其行列式 = 格的体积平方。
  - 🟢事实：$\mathrm{Tr}$、$\mathrm{N}$ 是 $\mathbb{Q}$-线性（迹）/乘性（范数）：$\mathrm{N}(\alpha\beta)=\mathrm{N}(\alpha)\mathrm{N}(\beta)$，$\mathrm{Tr}(\alpha+\beta)=\mathrm{Tr}(\alpha)+\mathrm{Tr}(\beta)$。
  - 🟡类比：判别式矩阵 = Gram 矩阵（内积表），行列式 = 格体积²，如协方差矩阵的行列式衡量数据「散布」。
- **关键定理**：**整基存在定理**：设 $K$ 数域，$n=[K:\mathbb{Q}]$，则 $\mathcal{O}_K$ 是秩 $n$ 的自由 $\mathbb{Z}$-模，即存在整基 $\{\omega_1,\ldots,\omega_n\}$ 使 $\mathcal{O}_K=\bigoplus_{i=1}^n\mathbb{Z}\omega_i$。数域判别式 $d_K=\det(\mathrm{Tr}(\omega_i\omega_j))$ 是整基的判别式，与基选取无关。
- **自测**：求 $\mathbb{Q}(\sqrt{2})$ 与 $\mathbb{Q}(\zeta_5)$ 的整基与判别式。(a) $\mathbb{Q}(\sqrt{2})$：$2\not\equiv1\pmod4$，$\mathcal{O}_K=\mathbb{Z}[\sqrt2]$，整基 $\{1,\sqrt2\}$。$\mathrm{Tr}(1)=2$，$\mathrm{Tr}(\sqrt2)=0$，$\mathrm{Tr}(2)=4$，故 $d_K=\det\begin{pmatrix}2&0\\0&4\end{pmatrix}=8$。(b) $\mathbb{Q}(\zeta_5)$：整基 $\{1,\zeta_5,\zeta_5^2,\zeta_5^3\}$，$d_K=(-1)^{(5-1)/2}5^{5-2}/5^{[5/5]}\cdots$，分圆域判别式公式给 $d_K=5^3=125$（正，因 $5\equiv1\pmod4$）。

**迹、范数、判别式速记**（全书反复用到的三大不变量，务必手算 $\mathbb{Q}(\sqrt{d})$）：

| 不变量 | 定义 | 性质 | 二次域 $\mathbb{Q}(\sqrt{d})$ 公式 |
|---|---|---|---|
| **迹** $\mathrm{Tr}(\alpha)$ | $\sum_{i=1}^n\sigma_i(\alpha)$（共轭之和） | $\mathbb{Q}$-线性：$\mathrm{Tr}(\alpha+\beta)=\mathrm{Tr}(\alpha)+\mathrm{Tr}(\beta)$ | $\mathrm{Tr}(a+b\sqrt{d})=2a$ |
| **范数** $\mathrm{N}(\alpha)$ | $\prod_{i=1}^n\sigma_i(\alpha)$（共轭之积） | 乘性：$\mathrm{N}(\alpha\beta)=\mathrm{N}(\alpha)\mathrm{N}(\beta)$ | $\mathrm{N}(a+b\sqrt{d})=a^2-db^2$ |
| **判别式** $d_K$ | $\det(\mathrm{Tr}(\omega_i\omega_j))$（整基 Gram 行列式） | 与整基选取无关（差平方） | $d_K=4d$（$d\not\equiv1\pmod4$）或 $d$（$d\equiv1\pmod4$） |

核心：迹是「求和」（UDOT 累加），范数是「求积」，判别式是「内积矩阵的行列式」= 格体积²。$\alpha$ 是单位 $\Leftrightarrow\mathrm{N}(\alpha)=\pm1$。

---

### 第 4 章 · Ideal Theory（理想理论：Dedekind 整环与类群）

- **核心**：本章是全书的**代数核心**。$\mathcal{O}_K$ 不一定是 UFD（$\mathbb{Z}[\sqrt{-5}]$ 中 $6=2\cdot3=(1+\sqrt{-5})(1-\sqrt{-5})$ 不唯一分解），但 $\mathcal{O}_K$ 恒为 **Dedekind 整环**：Noether、整闭、非零素理想极大。Dedekind 整环的**核心补偿定理**是**理想唯一分解**——每个非零（分式）理想唯一写成素理想幂之积 $\mathfrak{a}=\prod\mathfrak{p}_i^{e_i}$。理想范数 $N(\mathfrak{a})=[\mathcal{O}_K:\mathfrak{a}]$（有限指标）。**理想类群** $\mathrm{Cl}(K)=\{\text{分式理想}\}/\{\text{主理想}\}$ 衡量「离 PID 多远」，其阶 $h_K=|\mathrm{Cl}(K)|$ 为**类数**。本章用 Minkowski 几何（Ch 5 详述）证明 $h_K<\infty$。
- **飞腾锚点**：**GEMM 9.45 GFLOPS [Lab05]** —— 理想类群 $\mathrm{Cl}(K)$ 是有限 Abel 群，其结构（循环分解 $\cong\mathbb{Z}/n_1\times\cdots\times\mathbb{Z}/n_k$）由理想乘法表决定——理想间的乘法/逆运算如群元素乘法表（Cayley 表），是密集的矩阵运算（GEMM）。
  - 🟢事实：$N(\mathfrak{a}\mathfrak{b})=N(\mathfrak{a})N(\mathfrak{b})$（范数乘性）；$\mathfrak{a}$ 主 $\Leftrightarrow\exists\alpha:\mathfrak{a}=(\alpha)$；$\mathrm{Cl}(K)=1\Leftrightarrow\mathcal{O}_K$ 是 PID $\Leftrightarrow$ UFD。
  - 🟡类比：类群 = 理想乘法的「商结构」，如矩阵群的商——把主理想「模掉」后剩下的非平凡部分。
- **关键定理**：**Dedekind 理想唯一分解定理**：设 $K$ 数域，$\mathcal{O}_K$ 其整数环（Dedekind 整环），则每个非零分式理想 $\mathfrak{a}$ 可唯一（差单位因子）写成
$$\mathfrak{a}=\mathfrak{p}_1^{e_1}\mathfrak{p}_2^{e_2}\cdots\mathfrak{p}_r^{e_r},\quad e_i\in\mathbb{Z},\ \mathfrak{p}_i\text{ 非零素理想}.$$
推论：理想乘法群（分式理想）是自由 Abel 群（以素理想为基），类群是其商。
- **自测**：在 $K=\mathbb{Q}(\sqrt{-5})$，$\mathcal{O}_K=\mathbb{Z}[\sqrt{-5}]$ 中分解理想 $(2)$、$(3)$、$(7)$。提示：$d_K=-20$，素数 $p$ 分歧 $\Leftrightarrow p\mid d_K$，故 $2,5$ 分歧。(2)：$x^2+5\equiv x^2+1\equiv(x+1)^2\pmod2$，故 $(2)=\mathfrak{p}^2$，$\mathfrak{p}=(2,1+\sqrt{-5})$，$N\mathfrak{p}=2$。(3)：$x^2+5\equiv x^2-1\equiv(x-1)(x+1)\pmod3$，故 $(3)=\mathfrak{q}_1\mathfrak{q}_2$（分裂），$\mathfrak{q}_1=(3,1+\sqrt{-5})$，$\mathfrak{q}_2=(3,1-\sqrt{-5})$。(7)：$x^2+5\equiv x^2+5\pmod7$，$-5\equiv2$，$(\frac{2}{7})=1$（$7\equiv\pm1\pmod8$），故 $(7)$ 也分裂。验证 $\mathfrak{p}$ 非主（$|N\alpha|=2$ 无解 $a^2+5b^2=2$），故 $\mathrm{Cl}(K)\ne1$。

**二次域 $\mathbb{Q}(\sqrt{d})$ 中素数 $p$ 的分解判据速记**（Janusz 最实用的计算工具，务必手算 $p=2,3,5,7$）：

| 条件 | 分解模式 | $e,f,g$ | 记忆 |
|---|---|---|---|
| $p\mid d_K$（判别式） | **分歧** $(p)=\mathfrak{p}^2$ | $e=2,f=1,g=1$ | 判别式整除 = 分歧 |
| $(\frac{d}{p})=1$（$p$ 奇） | **分裂** $(p)=\mathfrak{p}_1\mathfrak{p}_2$ | $e=1,f=1,g=2$ | 二次剩余 = 分裂 |
| $(\frac{d}{p})=-1$（$p$ 奇） | **惯性** $(p)$ 保持素理想 | $e=1,f=2,g=1$ | 非剩余 = 惯性 |
| $p=2$ | 由 $d\bmod8$ 决定 | 见下 | 2 的情形最微妙 |

$p=2$ 的三分：（$d_K$ 为判别式）$2\mid d_K$ 时分歧；$2\nmid d_K$ 时 $d\equiv1\pmod8$ 则分裂，否则惯性。核心口诀：**「整除判别式必分歧，Legendre 符号定分裂/惯性」**。

**Ch 4 常见陷阱**：(1) 理想唯一分解 $\ne$ 元素唯一分解——$\mathbb{Z}[\sqrt{-5}]$ 是反例，理想补救是 Dedekind 的核心贡献。(2) 类群 $\mathrm{Cl}(K)$ 衡量的是**分式理想**模主理想的商，不是元素分解的困难程度（两者相关但不等价）。(3) $\mathcal{O}_K$ 是 PID $\Leftrightarrow\mathrm{Cl}(K)=1$ $\Leftrightarrow$ UFD——这三个等价条件仅对 Dedekind 整环成立，一般整环未必。

---

### 第 5 章 · Units（单位群：Dirichlet 单位定理）

- **核心**：**单位**是 $\mathcal{O}_K$ 中乘法可逆元（范数 $\pm1$ 的代数整数），全体单位构成乘法群 $\mathcal{O}_K^*$。**Dirichlet 单位定理**是代数数论三大基本定理之一：$\mathcal{O}_K^*\cong\mu(K)\times\mathbb{Z}^{r_1+r_2-1}$，其中 $\mu(K)$ 是有限单位根群（挠部），$r_1$ 是实嵌入数、$2r_2$ 是复嵌入数，秩 $r_1+r_2-1$ 称**单位秩**。证明核心是 **Minkowski 几何嵌入**：把 $\mathcal{O}_K$ 嵌入 $\mathbb{R}^{r_1}\times\mathbb{C}^{r_2}\cong\mathbb{R}^n$ 成格 $\Lambda$，单位对应格中范数 1 的点，经对数映射 $\log|\sigma_i(\cdot)|$ 落在超平面 $\sum x_i=0$（$\cong\mathbb{R}^{r_1+r_2-1}$）的格上。**调节子** $R_K$ 是该单位对数格的体积。
- **飞腾锚点**：**Schmidt 正交化** —— Minkowski 嵌入把 $\mathcal{O}_K$ 映成 $\mathbb{R}^n$ 中的格，单位的对数像落在 $\sum x_i=0$ 超平面上——对单位对数向量做 Schmidt 正交化，得到单位格的一组正交基，其体积就是调节子 $R_K$。
  - 🟢事实：$\mathbb{Q}(\sqrt2)$ 单位秩 $=2+0-1=1$，$\mathcal{O}^*\cong\{\pm1\}\times\langle1+\sqrt2\rangle$；$\mathbb{Q}(i)$ 秩 $=0+1-1=0$，$\mathcal{O}^*=\mu=\{\pm1,\pm i\}$（有限）。
  - 🟡类比：单位群 =「有限离散根 + 自由连续参数」，如模型的偏置（离散）+ 权重（连续自由度）。
- **关键定理**：**Dirichlet 单位定理**：设 $K$ 数域，$r_1$ 实嵌入，$r_2$ 复嵌入对，则
$$\mathcal{O}_K^*\cong\mu(K)\times\mathbb{Z}^{r_1+r_2-1},$$
$\mu(K)$ 为 $K$ 中单位根全体（有限循环群），$r_1+r_2-1$ 为单位秩。$R_k$ 为调节子（单位对数格体积），在 Ch 8 类数公式中与 $h_K$ 配对。
- **自测**：求 $\mathbb{Q}(\sqrt{2})$ 的基本单位。答：秩 $=1$。$u=1+\sqrt2$，$|u|=1+\sqrt2\approx2.414$，$|u'|=|1-\sqrt2|\approx0.414$，$\mathrm{N}(u)=u\cdot u'=(1+\sqrt2)(1-\sqrt2)=-1$（单位 ✓）。$u$ 是最小 $>1$ 的单位（基本单位），$\mathcal{O}^*=\{\pm(1+\sqrt2)^n:n\in\mathbb{Z}\}$。验证 $(1+\sqrt2)^2=3+2\sqrt2$，$\mathrm{N}=1$（正范数单位）。

---

### 第 6 章 · Extensions of Number Fields（扩域：分歧与 Frobenius）

- **核心**：设 $L/K$ 数域扩张，素理想 $\mathfrak{p}\subset\mathcal{O}_K$ 在 $\mathcal{O}_L$ 中分解为 $\mathfrak{p}\mathcal{O}_L=\mathfrak{P}_1^{e_1}\cdots\mathfrak{P}_g^{e_g}$。$e_i$ 为**分歧指数**，$f_i=[\mathcal{O}_L/\mathfrak{P}_i:\mathcal{O}_K/\mathfrak{p}]$ 为**剩余次数**，基本等式 $\sum e_if_i=[L:K]$。$\mathfrak{p}$ **非分歧**若所有 $e_i=1$ 且剩余域扩张可分。对 Galois 扩张，**分解群** $D_{\mathfrak{P}}=\{\sigma:\sigma(\mathfrak{P})=\mathfrak{P}\}$、**惯性群** $I_{\mathfrak{P}}=\{\sigma:\sigma(a)\equiv a\pmod{\mathfrak{P}}\}$。非分歧时 **Frobenius 元素** $\mathrm{Frob}_{\mathfrak{P}}\in D/I$ 满足 $\mathrm{Frob}(x)=x^{N\mathfrak{p}}$。**Hilbert 类域** $H$ 是 $K$ 的极大非分歧 Abel 扩张，$\mathrm{Gal}(H/K)\cong\mathrm{Cl}(K)$。
- **飞腾锚点**：**分支预测 0.71 vs 3.14 [Lab02]** —— 素理想 $\mathfrak{p}$ 在 $L$ 中的分解模式（分歧/分裂/惯性）是「分支判断」：$e>1$ 分歧（难预测路径，0.71 慢）、$e=1,g>1$ 分裂（多路分支）、$e=1,g=1$ 惯性（单一可预测路径，3.14 快）。Frobenius 是「分支标签」，决定素数走哪条路。
  - 🟢事实：$p$ 在 $L/K$ 中分歧 $\Leftrightarrow p\mid d_{L/K}$（判别式整除判据）；Galois 扩张中同一 $\mathfrak{p}$ 的所有 $\mathfrak{P}_i$ 有相同 $e,f$。
  - 🟡类比：分解群 = 「固定一个分支的稳定子」，惯性群 = 「分支内的微扰群」，如流水线的「主分支」与「微操作」。
- **关键定理**：**Hilbert 类域定理**：设 $K$ 数域，$h_K$ 类数，则存在唯一的极大非分歧 Abel 扩张 $H/K$（Hilbert 类域），满足 $\mathrm{Gal}(H/K)\cong\mathrm{Cl}(K)$，故 $[H:K]=h_K$。非分歧素理想 $\mathfrak{p}$ 在 $H$ 中完全分裂 $\Leftrightarrow$ $\mathfrak{p}$ 主。
- **自测**：素数 $p$ 在 $\mathbb{Q}(\zeta_5)$ 中如何分解？答：$d_K=125=5^3$，唯分歧素为 $5$。$(5)=\mathfrak{P}^4$（全分歧，$e=4,f=1,g=1$），因 $5=(1-\zeta_5)^4\cdot(\text{单位})$，$1-\zeta_5$ 是唯一（差单位）在 $5$ 上分歧的素元。$p\ne5$ 时非分歧，分解模式由 $p\bmod5$ 决定：$\mathrm{Frob}_p$ 的阶 $=$ $p\bmod5$ 在 $(\mathbb{Z}/5)^*\cong\mathbb{Z}/4$ 中的阶，$g=4/\mathrm{ord}(p\bmod5)$。

---

### 第 7 章 · Local Fields（局部域：$p$-adic 数与 Hensel 引理）

- **核心**：本章从「整体域」切换到「局部域」——在一个素数处放大观察。$p$-adic 赋值 $v_p:\mathbb{Q}^*\to\mathbb{Z}$，$v_p(p^n\cdot a/b)=n$（$p\nmid a,b$）。$p$-adic 绝对值 $|x|_p=p^{-v_p(x)}$，满足强三角不等式 $|x+y|_p\le\max(|x|_p,|y|_p)$（非阿基米德）。**完备化** $\mathbb{Q}_p=\widehat{\mathbb{Q}}$（$|\cdot|_p$ 下 Cauchy 列等价类），$\mathbb{Z}_p=\{x:v_p(x)\ge0\}$ 为 $p$-adic 整数环。**Ostrowski 定理**：$\mathbb{Q}$ 的非平凡绝对值仅有 $|\cdot|_\infty$ 与 $\{|\cdot|_p\}$。**Hensel 引理**：完备域上模 $\mathfrak{m}$ 的单根可精确提升为精确根。局部域结构：$\mathbb{Q}_p^*\cong p^{\mathbb{Z}}\times\mu_{p-1}\times(1+p\mathbb{Z}_p)$。
- **飞腾锚点**：**FP16 3.81× [L01]** —— $p$-adic 数是「有限精度 + 无限展开」的数系，如 FP16 浮点的有限尾数 + 指数范围；Hensel 提升每步精度翻倍（$v_p$-adic 二次收敛），如 Newton 法从 FP16 逐步提升到精确值。
  - 🟢事实：$\mathbb{Z}_p=\varprojlim\mathbb{Z}/p^n$，每个 $p$-adic 整数是相容系 $(a_n\bmod p^n)$；Hensel 迭代 $\alpha_{n+1}=\alpha_n-f(\alpha_n)/f'(\alpha_n)$ 每步 $v_p$-精度翻倍。
  - 🟡类比：$|\cdot|_p$ 的强三角 $|x+y|\le\max$ 意味着「误差不累积」（每步精确翻倍），比实数 Newton 法更干净——$p$-adic 比 $\mathbb{R}$ 更适合代数计算。
- **关键定理**：**Hensel 引理**：设 $K$ 完备（赋值 $v$，剩余域 $k$），$f\in\mathcal{O}_K[x]$，$\bar f\in k[x]$ 为模 $\mathfrak{m}$ 约化。若 $\bar\alpha\in k$ 是 $\bar f$ 的**单根**（$\bar f(\bar\alpha)=0,\ \bar f'(\bar\alpha)\ne0$），则存在唯一 $\alpha\in\mathcal{O}_K$ 使 $f(\alpha)=0$ 且 $\alpha\equiv\bar\alpha\pmod{\mathfrak{m}}$。
- **自测**：用 Hensel 证 $x^2\equiv2\pmod7$ 有解 $\Rightarrow$ $x^2=2$ 在 $\mathbb{Q}_7$ 有解。提示：$3^2=9\equiv2\pmod7$，$\bar f'(3)=2\cdot3=6\not\equiv0\pmod7$（单根 ✓）。Newton 迭代 $\alpha_0=3$，$\alpha_1=3-(9-2)/6=3-7/6$，$6^{-1}\bmod49=41$（$6\cdot41=246=5\cdot49+1$），$\alpha_1\equiv3-7\cdot41\equiv3-287\equiv3-287+294\equiv10\pmod{49}$，验证 $10^2=100\equiv2\pmod{49}$ ✓，继续提升得 $\alpha\in\mathbb{Z}_7$。

**$\mathbb{Q}_p^*$ 结构定理速记**（局部域乘法群的完整分解，务必手算 $p=2,3$）：

| 因子 | 结构 | 含义 |
|---|---|---|
| $p^{\mathbb{Z}}$ | 离散（赋值部分） | $v_p(x)$ 决定，$p$ 的幂次 |
| $\mu_{p-1}$（$p$ 奇） | 有限循环，阶 $p-1$ | Teichmüller 代表元，剩余域 $\mathbb{F}_p^*$ 的提升 |
| $1+p\mathbb{Z}_p$（$p$ 奇） | $\cong\mathbb{Z}_p$（$p$-adic 对数同构） | 主单位群，$\log:1+p\mathbb{Z}_p\xrightarrow{\sim}p\mathbb{Z}_p$ |

故 $\mathbb{Q}_p^*\cong\mathbb{Z}\times\mathbb{Z}/(p-1)\times\mathbb{Z}_p$（$p$ 奇）。$p=2$ 时 $\mu_{p-1}=\{1\}$，$1+2\mathbb{Z}_2$ 更复杂（需 $1+4\mathbb{Z}_2\cong\mathbb{Z}_2$，因子 $1+2\mathbb{Z}_2/\{\pm1\}$）。

**$\mathbb{Q}_p$ 中开 $n$ 次方判据**（Hensel 的实用化速记）：

| $n$ | $p$ | $a\in\mathbb{Z}_p^*$ 开 $n$ 次方条件 | 来源 |
|---|---|---|---|
| 任意 | $p\nmid n$ | $a\bmod p\in(\mathbb{F}_p^*)^n$ | Hensel 基本形 |
| $2$ | $p$ 奇 | $a\bmod p\in(\mathbb{F}_p^*)^2$（二次剩余） | $p\nmid2$ |
| $2$ | $p=2$ | $a\equiv1\pmod8$ | 模 $8$ 判据 |

核心：$p$ 奇时只需模 $p$ 判（单根 Hensel），$p=2$ 时需模 $8$——「野性总在最小的素数处爆发」。

**Ch 7 常见陷阱**：(1) Hensel 引理要求**单根**（$\bar f'(\bar\alpha)\ne0$），重根无法提升——这是「光滑性」的代数化身。(2) 完备化 $\mathbb{Q}_p$ 与原域 $\mathbb{Q}$ 的代数扩张不一定一致：$\mathbb{Q}_p$ 可能有 $\mathbb{Q}$ 中没有的代数元。(3) $K^*$ 分裂 $K^*\cong\pi^{\mathbb{Z}}\times\mu\times U_1$ 需要 $K$ **完备**——非完备域（如 $\mathbb{Q}$）乘法群结构远更复杂。

---

### 第 8 章 · L-functions and Class Number Formulas（$L$-函数与类数公式）

- **核心**：本章是全书的**解析收官**——用 $L$-函数把 Ch 1–6 的代数不变量（类数 $h_K$、调节子 $R_K$、判别式 $d_K$）焊成一行公式。**Dirichlet $L$-函数** $L(s,\chi)=\sum_{n=1}^\infty\chi(n)n^{-s}=\prod_p(1-\chi(p)p^{-s})^{-1}$（$\chi$ Dirichlet 特征）。**Dedekind $\zeta$ 函数** $\zeta_K(s)=\sum_{\mathfrak{a}}N(\mathfrak{a})^{-s}=\prod_{\mathfrak{p}}(1-N(\mathfrak{p})^{-s})^{-1}$（$\mathrm{Re}\,s>1$），延拓到 $\mathbb{C}\setminus\{1\}$。**解析类数公式**（$s=1$ 留数）：$\mathrm{Res}_{s=1}\zeta_K(s)=\frac{2^{r_1}(2\pi)^{r_2}h_KR_K}{w_K\sqrt{|d_K|}}$——「解析留数 = 代数不变量」。Janusz 先在二次域手算验证（$L(1,\chi_d)$ 给类数），再推广到一般数域。
- **飞腾锚点**：**Iron Law <2% [Lab00]** —— 类数公式两侧严格相等（解析留数 = 代数不变量），零容差——$h_K$ 是精确正整数，$L(1,\chi)$ 收敛到精确值；任何数值误差超 2% 就摧毁公式的自洽性（Iron Law：性能 = 指令数 $\times$ CPI $\times$ 时钟，误差铁律）。
  - 🟢事实：$\mathrm{Res}_{s=1}\zeta_\mathbb{Q}(s)=1$（$h=R=w=1,d=1$）；$\zeta_{\mathbb{Q}(i)}(s)=\zeta(s)L(s,\chi_{-4})$，$L(1,\chi_{-4})=\frac{\pi}{4}$（Leibniz 级数），留数吻合。
  - 🟡类比：$\zeta_K(s)$ = 数域的「解析签名」，留数 = 签名的「指纹」，唯一确定类数——如 loss 极值唯一确定模型参数。
- **关键定理**：**解析类数公式**：设 $K$ 数域，$r_1$ 实嵌入，$2r_2$ 复嵌入，$h_K$ 类数，$R_K$ 调节子，$w_K$ 单位根数，$d_K$ 判别式，则
$$\operatorname*{Res}_{s=1}\zeta_K(s)=\frac{2^{r_1}(2\pi)^{r_2}h_KR_K}{w_K\sqrt{|d_K|}}.$$
这是「解析留数 = 代数不变量」的精确陈述，焊死 Ch 1–6 的代数骨架与解析方法。
- **自测**：对 $K=\mathbb{Q}(i)$（Gauss 整数环），用类数公式验证 $h=1$。提示：$r_1=0,r_2=1,h=1,R=1$（秩 0，调节子定义 $=1$），$w=4$（$\{\pm1,\pm i\}$），$d=-4$。$\mathrm{Res}\,\zeta_K=\frac{(2\pi)^1\cdot1\cdot1}{4\cdot\sqrt4}=\frac{2\pi}{8}=\frac{\pi}{4}$。又 $\zeta_{\mathbb{Q}(i)}(s)=\zeta(s)L(s,\chi_{-4})$，$\mathrm{Res}_{s=1}\zeta(s)=1$，$L(1,\chi_{-4})=1-\frac13+\frac15-\cdots=\frac{\pi}{4}$（Leibniz），吻合 ✓。

**类数公式特例速记**（把一般公式代入具体数域，务必手算验证）：

| 数域 $K$ | $r_1,r_2$ | $d_K$ | $w_K$ | $h_K$ | $\mathrm{Res}_{s=1}\zeta_K$ |
|---|---|---|---|---|---|
| $\mathbb{Q}$ | $1,0$ | $1$ | $2$ | $1$ | $1$ |
| $\mathbb{Q}(i)$ | $0,1$ | $-4$ | $4$ | $1$ | $\pi/4$ |
| $\mathbb{Q}(\sqrt{-5})$ | $0,1$ | $-20$ | $2$ | $2$ | $\pi/\sqrt{20}\cdot2$ |
| $\mathbb{Q}(\sqrt2)$ | $2,0$ | $8$ | $2$ | $1$ | $\frac{2\log(1+\sqrt2)}{\sqrt8}$ |

核心：虚二次域用 $L(1,\chi_d)$（收敛级数），实二次域用基本单位 $\varepsilon$ 的对数 $\log\varepsilon$（调节子 $R=\log\varepsilon$）。类数公式把「代数结构」与「解析留数」精确焊死，是 Janusz 全书的解析高潮。

**Ch 8 常见陷阱**：(1) 类数公式需要 $\zeta_K(s)$ 的解析延拓——整体域成立（非函数域）。(2) 调节子 $R_K$ 在单位秩为 0 时（如虚二次域）定义为 1，不是 0。(3) Dedekind $\zeta_K(s)\ne$ Riemann $\zeta(s)$——前者对所有理想求和，后者仅对自然数（$\zeta_\mathbb{Q}=\zeta$）；$\zeta_K=\zeta\cdot\prod_{\rho\ne1}L(s,\rho)^{\dim\rho}$（Artin 分解）。

---

## §9 全书思想主线：Janusz 的「具体数域例子」教学驱动

Janusz 的全书贯穿一条主线：**以具体数域（$\mathbb{Q}(i)$、$\mathbb{Q}(\sqrt{2})$、$\mathbb{Q}(\sqrt{-5})$、$\mathbb{Q}(\zeta_5)$）的计算为驱动，从「手感」自然生长到「理论」**。这不是「先抽象定义后举例」的欧几里得式写法，而是「先算给你看、再提炼定义」的 Pólya 式写法。全书 8 章可分为三层：**第一层（Ch 1–3，代数地基）**用域论、整性、迹/范数/判别式搭好 $\mathcal{O}_K$ 的脚手架；**第二层（Ch 4–6，理想与几何核心）**用 Dedekind 理想分解修复「元素不唯一分解」的缺陷，用 Minkowski 几何证明类群有限与单位群结构，用分歧与 Frobenius 把素数分解「分层切开」——这一层是 Janusz 全书的灵魂，每个定理都配二次域手算；**第三层（Ch 7–8，局部与解析收官）**引入 $p$-adic 局部域与 $\zeta_K$ 解析方法，用 Hensel 提升与类数公式把局部精确化与全局不变量统一。

**与同类教材的方法论对比**：Janusz 走**「温和自学」**路线——证明完整、计算详尽、节奏友好，适合「零基础第一遍」。Neukirch 走**「系统对照」**路线——整体域与局部域双线并进、最自洽，适合「系统学习与全景视野」。Lang GTM110 走**「百科整合」**路线——代数+解析+类域论三合一、密度最高，适合「整合复习与查漏」。三书不冲突而互补：第一遍用 **Janusz 建立计算手感**（本书），第二遍用 Neukirch 补系统与局部理论，第三遍用 Lang 做整合复习。**Janusz 之所以是起点**，因为它是唯一一本让零基础读者「读完就能手算二次域类数与分圆域 Galois 群」的教材——其他书要么太快（Lang），要么太抽象（Neukirch）。与已读的 Silverman GTM106（椭圆曲线，局部域应用）和 Ireland-Rosen（初等数论骨架）呼应：Janusz 补上了它们之间缺失的「系统代数数论」中间层。

**Janusz 的「压缩术」可复刻**：(1) 用具体数域（$\mathbb{Q}(\sqrt{d})$）作每个概念的第一个例子，建立直觉后再抽象；(2) 用 Minkowski 几何把类群有限性与单位群结构用同一个格论证统一；(3) 用 $\zeta_K$ 留数把代数不变量（类数、调节子、判别式）焊成一行。这三步「具体例子→几何统一→解析收官」正是 Janusz 全书的教学主线。

**代数数论学习常见误区（跨章汇总）**：

| 误区 | 正确理解 | 出处 |
|---|---|---|
| 元素唯一分解 = 理想唯一分解 | 仅理想必唯一分解；元素未必（$\mathbb{Z}[\sqrt{-5}]$） | Ch 4 |
| 迹/范数是元素本身的不变量 | 是扩张 $K/\mathbb{Q}$ 的不变量，依赖嵌入选取 | Ch 3 |
| 判别式越大类数越大 | $M_K\propto\sqrt{|d_K|}$ 是上界，但非单调（有例外） | Ch 4–5 |
| Hensel 能提升任何根 | 仅提升**单根**（$\bar f'\ne0$），重根需更精细工具 | Ch 7 |
| $p$ 分歧 $\Leftrightarrow p\mid d$ | 正确的是 $p\mid d_K$（判别式），$d_K$ 可能 $\ne d$ | Ch 6 |
| $\zeta_K=\zeta$ | 仅 $K=\mathbb{Q}$ 时成立；一般 $\zeta_K$ 对所有理想求和 | Ch 8 |
| 调节子秩 0 时 $R=0$ | 定义 $R=1$（空行列式约定），否则类数公式失效 | Ch 5, 8 |

---

## §10 与本仓库其他笔记的交叉引用

### 与已精读书目的呼应

| 本书 | 关系 | 交叉点 |
|---|---|---|
| **Neukirch**《代数数论》（同期生成） | 系统进阶 | Janusz Ch 4–6（理想、单位、分歧）= Neukirch 整体域部分的温和版；Janusz 建手感后，Neukirch 补局部域双线与类域论系统 |
| **Lang** GTM110 代数数论 | 整合复习 | Janusz Ch 1–8 = Lang Ch 1–8 的「慢速版」；Janusz 建骨架后，Lang 补类域论（Ch 9–13）与上同调附录 |
| **Ireland-Rosen** GTM84 | 初等前置 | IR Ch 12–14（代数整数、Dedekind 域）是 Janusz Ch 2–4 的初等热身；IR 的分圆域（Ch 13）↔ Janusz Ch 6 |
| **Silverman** GTM106 椭圆曲线 | 局部应用 | Silverman Ch VII（椭圆曲线局部约化）用 Janusz Ch 7（局部域、Hensel）；Tate 算法 ↔ 分歧分层 |
| **Serre** GTM67 局部域 | 局部深化 | Serre Ch I–II（DVR、分歧群）= Janusz Ch 7 的极简锋利版；Janusz 建 $p$-adic 直觉后，Serre 攻局部类域论 |
| **Atiyah-MacDonald** | 交换代数前置 | AM Ch 9（DVR、整闭包、完备化）↔ Janusz Ch 2–4, 7 |

### AI/工程锚点法：代数数论的工程落地

| 数学概念 | AI/工程对应 | 锚点说明 |
|---|---|---|
| **Galois 群作用 = 矩阵群** | matmul / 线性变换 | 🟢$\sigma\in\mathrm{Gal}(L/K)$ 在整基上是整数矩阵，$\det=\pm1$；群运算 = matmul |
| **$\mathcal{O}_K$ 整闭包 = $\mathbb{Z}$ 的分层扩展** | TLB 分层寻址 / 内存局部性 | 🟡$\mathbb{Z}\subset\mathcal{O}_K$ 如虚拟地址↔物理地址分层映射 |
| **迹 = 共轭求和** | UDOT 点积累加 / 向量内积 | 🟢$\mathrm{Tr}(\alpha)=\sum_i\sigma_i(\alpha)$ 是高效求和；判别式 = Gram 矩阵列式 |
| **理想类群 Cayley 表** | GEMM 密集矩阵运算 | 🟡类群是有限 Abel 群，理想乘法/逆如群元素 Cayley 表的密集矩阵运算 |
| **Minkowski 嵌入正交化** | Schmidt 正交化 / 格归约 | 🟢单位对数格的 Schmidt 正交化体积 = 调节子 $R_K$ |
| **分歧判定** | 分支预测 / 路径选择 | 🟡$e>1$ 分歧（慢路径 0.71）/ $e=1$ 非分歧（快路径 3.14），Frobenius = 分支标签 |
| **Hensel 提升 = 精度翻倍** | FP16 逐步提升 / Newton 二次收敛 | 🟢$p$-adic Newton 每步 $v_p$-精度翻倍，如 FP16→FP32→精确 |
| **类数公式（解析留数）** | Iron Law 精度铁律 / loss 极值 | 🟢$\mathrm{Res}_{s=1}\zeta_K$ 两侧严格相等，零容差；如性能铁律不可近似 |
| **RSA 密码学** | 大整数分解 / 素数搜索 | 🟡类群与理想分解是「$\mathcal{O}_K$ 上的因子分解」，RSA 依赖 $\mathbb{Z}$ 上分解的困难性 |
| **格密码 NTRU** | 格归约 / Minkowski 界 | 🟡NTRU 安全性依赖格中最近向量问题（CVP），Minkowski 几何给出格点存在界 |
| **椭圆曲线密码学** | 素数域上群运算 / Frobenius | 🟢椭圆曲线点群结构用 Frobenius 自同构分析（Silverman GTM106） |

**锚点法的统一视角**：Janusz 全书可用三句话锚定——**「整基让 $\mathcal{O}_K$ 可计算（Ch 3），理想分解让因子唯一（Ch 4），$\zeta$ 留数让类数可算（Ch 8）」**。第一步是线性代数（迹/范数/判别式给坐标），第二步是代数（理想修复分解），第三步是分析（解析留数给精确不变量）。这三步从「坐标→分解→秤量」贯穿全书，掌握这条主线，全书的「为什么这样组织」就豁然开朗。

---

## §11 自测答案要点（供核对）

1. **Ch 1** $\mathbb{Q}(\zeta_5)$ Galois 对应：$\mathrm{Gal}\cong(\mathbb{Z}/5)^*=\{1,2,3,4\}\cong\mathbb{Z}/4$（$\sigma_2:\zeta\mapsto\zeta^2$，阶 4）。子群：$\{1\}$↔$\mathbb{Q}(\zeta_5)$；$\{1,4\}=\langle\sigma_2^2\rangle\cong\mathbb{Z}/2$↔$\mathbb{Q}(\zeta_5+\zeta_5^{-1})=\mathbb{Q}(\sqrt5)$（$\zeta+\zeta^{-1}=2\cos(2\pi/5)=\frac{\sqrt5-1}{2}$）；全群↔$\mathbb{Q}$。
2. **Ch 3** $\mathbb{Q}(\sqrt2)$ 判别式：$\{1,\sqrt2\}$ 整基，$\mathrm{Tr}(1)=1+1=2$（两共轭 $1,1$），$\mathrm{Tr}(\sqrt2)=\sqrt2+(-\sqrt2)=0$，$\mathrm{Tr}(\sqrt2\cdot\sqrt2)=\mathrm{Tr}(2)=4$。$d_K=\det\begin{pmatrix}2&0\\0&4\end{pmatrix}=8$。$\mathbb{Q}(\zeta_5)$：分圆域判别式 $d_K=\frac{5^4}{5^1}=5^3=125$（公式 $d_{\mathbb{Q}(\zeta_p)}=(-1)^{(p-1)/2}p^{p-2}$，$p=5$ 给 $5^3=125$）。
3. **Ch 4** $\mathbb{Q}(\sqrt{-5})$：$(2)=\mathfrak{p}^2$（$\mathfrak{p}=(2,1+\sqrt{-5})$），$(3)=\mathfrak{q}_1\mathfrak{q}_2$。$\mathfrak{p}$ 非主（$|N\alpha|=2$ 无解），$\mathfrak{p}^2=(2)$ 主，故 $\mathfrak{p}$ 阶 2，$\mathrm{Cl}\cong\mathbb{Z}/2$。$6$ 的两分解：$(2)(3)=\mathfrak{p}^2\mathfrak{q}_1\mathfrak{q}_2=(1+\sqrt{-5})(1-\sqrt{-5})=\mathfrak{p}\mathfrak{q}_1\cdot\mathfrak{p}\mathfrak{q}_2$（同一理想类的不同元素表示）。
4. **Ch 5** $\mathbb{Q}(\sqrt2)$ 基本单位 $1+\sqrt2$：$\mathrm{N}=-1$（单位 ✓），$|1+\sqrt2|>1$，$|1-\sqrt2|<1$。若 $v<u$ 也为单位且 $|v|>1$，则 $|v'|=1/|v|<1/(1+\sqrt2)=\sqrt2-1$，但 $|v|+|v'|$ 须给出整数迹 $a+b\sqrt2$ 的系数约束，矛盾。
5. **Ch 6** $\mathbb{Q}(\zeta_5)$：$(5)=(1-\zeta_5)^4$（全分歧，$e=4$）。$p=2$：$\mathrm{Frob}_2$ 阶 $=\mathrm{ord}(2\bmod5)=4$（$2^1=2,2^2=4,2^3=3,2^4=1\pmod5$），故 $f=4,g=1$（$2$ 惯性，$(2)$ 在 $\mathbb{Q}(\zeta_5)$ 中保持素理想）。$p=11$：$11\equiv1\pmod5$，$\mathrm{Frob}_{11}$ 阶 $=1$，完全分裂 $(11)=\mathfrak{P}_1\cdots\mathfrak{P}_4$。
6. **Ch 7** $x^2=2$ 在 $\mathbb{Q}_7$：$3^2\equiv2\pmod7$，$f'(3)=6\not\equiv0$，Hensel 提升得唯一 $\alpha\in\mathbb{Z}_7$。$\mathbb{Q}_3^*$ 结构：$\cong3^{\mathbb{Z}}\times\mu_2\times(1+3\mathbb{Z}_3)\cong\mathbb{Z}\times\mathbb{Z}/2\times\mathbb{Z}_3$（$p=3$ 奇，$\log:1+3\mathbb{Z}_3\xrightarrow{\sim}3\mathbb{Z}_3$）。
7. **Ch 8** $\mathbb{Q}(i)$ 类数公式：$\mathrm{Res}\,\zeta_{\mathbb{Q}(i)}=\frac{(2\pi)^1\cdot1\cdot1}{4\cdot2}=\frac{\pi}{4}$。$\zeta_{\mathbb{Q}(i)}=\zeta\cdot L(s,\chi_{-4})$，$L(1,\chi_{-4})=1-\frac13+\frac15-\cdots=\frac{\pi}{4}$ ✓。

---

## §12 延展阅读与后续方向

读完 Janusz，自然有三个深入方向：

1. **系统进阶**：Neukirch《Algebraic Number Theory》（整体+局部双线、类域论系统化），把 Janusz 的温和骨架升级为研究级框架。
2. **整合复习**：Lang GTM110（代数+解析+类域论三合一），把 Janusz 的碎片粘成完整蓝图；详见本仓库 `lang_代数数论_GTM110_快速逐章.md`。
3. **局部深化**：Serre GTM67《Local Fields》（局部域极简经典），把 Janusz Ch 7 的 $p$-adic 直觉推进到局部类域论；详见本仓库 `serre_局部域_GTM67_快速逐章.md`。

**与已读笔记的闭环**：Ireland-Rosen（初等数论骨架）→ **Janusz（系统代数数论第一本）** → Silverman GTM106（局部域应用于椭圆曲线）→ Serre GTM67（局部域锋利）→ Lang GTM110（全景整合）。五者合起来，恰好是「代数数论 + 算术几何」的标准研究入门组合。

**研究者方向取舍建议**：若方向偏向**计算/算术几何**，优先吃透 Janusz Ch 4（理想论）+ Ch 6（分歧、Frobenius）——是 Tate 算法与椭圆曲线局部分析的地基。若偏向**解析数论**（$L$-函数、素数分布），Ch 8 类数公式 + Dirichlet $L$-函数是核心入口，后续接 Lang Ch 8 Artin $L$ 函数与 Tenenbaum 解析数论。若偏向**密码学应用**，Ch 4（类群、理想分解）+ Ch 7（局部域、Hensel）是 RSA/NTRU/格密码的数学底座。

> **一句话总结**：Janusz GSM7 用具体数域例子驱动教学，让你「读完就能手算二次域类数与分圆域 Galois 群」——它是代数数论自学之路最温和的缓坡道，先 Janusz 后 Neukirch/Lang，事半功倍。

---

> **精读纪律**：本文为快速逐章精读，每章取 1 个飞腾锚点 + 1 个关键定理 + 1 道自测题。深入计算与完整证明请回原书（Janusz 的证明完整不跳，尤以 Ch 4 理想论、Ch 5 单位定理、Ch 8 类数公式最值得逐字精读）。🟢 = 事实锚点（可直接引用），🟡 = 类比锚点（仅供直觉，不可引用于严格证明）。
>
> **实操验证建议**（SageMath / PARI-GP）：
> - `K = NumberField(x^2+5)` → `.class_group()` / `.class_number()` 验证 Ch 4 类数
> - `K.units()` → 验证 Ch 5 Dirichlet 单位定理与基本单位
> - `K.integral_basis()` / `K.discriminant()` → 验证 Ch 3 整基与判别式
> - `Qp(7)` → `Zp(7)` 验证 Ch 7 Hensel 提升 $x^2=2$
> - `zetak(K, 1)` 或 `L(s, chi)` → 验证 Ch 8 类数公式留数
> - `galois_group(L/K)` → 验证 Ch 1/6 Galois 对应与 Frobenius
