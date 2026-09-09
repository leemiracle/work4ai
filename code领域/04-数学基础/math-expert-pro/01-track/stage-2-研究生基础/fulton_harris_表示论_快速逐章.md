# Fulton-Harris《表示论:初阶教程》(GTM129) · 快速逐章精读

> 基于原书：Representation Theory: A First Course (GTM129, Fulton & Harris) / 读于：2026-07-02
> 定位：**最受欢迎的表示论入门**，有限群+李代数双线，例子丰富。
> 本文为**快速逐章精读**，每章 1 个飞腾锚点 + 1 个关键定理 + 1 道自测题。

---

## §0 引言：Fulton-Harris 是什么，为什么读它

Fulton-Harris《Representation Theory: A First Course》(GTM 129) 是表示论领域**最受欢迎的入门教材**，自 1991 年出版以来几乎成为所有表示论课程的标配。它的最大特色是**双线叙事**：Part I 用**特征理论**(character theory) 处理**有限群**的表示——从 $S_3$ 的小特征表出发，一路走到 $S_n$、$A_n$ 的 Young 图与诱导表示；Part II–III 转向**李代数**的表示——从 $\mathfrak{sl}(2;\mathbb{C})$ 的对称幂 $V_n = \mathrm{Sym}^n(\mathbb{C}^2)$ 开始，经过 $\mathfrak{sl}(3;\mathbb{C})$ 的根系 $A_2$，抵达**半单李代数的 Cartan 分类**与 **Weyl 特征公式**。

读它的核心理由：本书的**几何直觉极强**——把抽象的「权」画成格点上的图，把「根系」画成欧氏空间中的向量集合，把「Weyl 群」看作反射对称群，让读者「看见」表示。同时，例子极其丰富：每个定理几乎都配 $S_3$、$S_4$、$\mathfrak{sl}_2$、$\mathfrak{sl}_3$ 的具体计算，每一步都「看得见、摸得着」。与本仓库已精读的 Humphreys《李代数》(纯代数结构) 和 Hall《李群》(矩阵群+物理应用) 形成互补：Humphreys 讲「李代数长什么样」，Hall 讲「李群怎么算」，Fulton-Harris 讲「表示怎么分类、特征怎么算」——它是把**有限群的组合世界**与**李代数的几何世界**统一在同一框架下的那一本。

| 书 | 风格 | 严格性 | 适合谁 |
|---|---|---|---|
| **Fulton-Harris** GTM129 | 例子驱动，几何直觉，双线（有限群+李代数） | ★★★★ 计算详尽，证明完整 | 第一次学表示论，想要「看得见」的人 |
| **Serre**《线性表示》 | 极简，公理化，纯有限群 | ★★★★★ 每步无可挑剔 | 追求最短路径理解有限群表示 |
| **Humphreys** GTM9 | 纯代数，李代数结构为主 | ★★★★★ 标准教材 | 有抽代基础，专攻李代数结构 |
| **Hall** GTM222 | 矩阵群+物理，李群入门 | ★★★★ 极其友好 | 物理背景或想从 $SU(2)$ 入门 |

**建议路线**：Hall 通读（矩阵群+物理热身）→ Humphreys 补李代数深度 → **Fulton-Harris 攻表示论纵深（本书）** → Serre 补有限群表示的极致精简。

**零基础工程师阅读建议**：Ch1–3 是「甜区」——只需线性代数和基础群论，务必手算 $S_3$ 的特征表（三行三列，十分钟即可完成）。Ch9–10 是全书精华——$\mathfrak{sl}(2)$ 的对称幂 $V_n$ 和 $\mathfrak{sl}(3)$ 的权格点图，建议纸笔绘制权图。Ch14–15 是巅峰——根系、Dynkin 图、Weyl 公式，需配合 Humphreys Ch3–4 交叉读。附录的 Schur 函数与 Littlewood-Richardson 规则是组合表示论的入口。全书精读约 50–70 小时（每周 10–20h，4–6 周）。

**全书的两大「顿悟时刻」**：第一次顿悟在 Ch2——发现「迹」(trace) 居然是表示论的万能钥匙，一切归结为特征的正交性。第二次顿悟在 Ch15——发现 Weyl 特征公式把有限群特征的正交关系「升级」为根系反射的交替和，有限群与李代数在此统一。

---

## §1 全书 12 核心章节骨架一览（飞腾锚点分布）

| 章 | 标题 | 核心概念 | 飞腾锚点 |
|---|---|---|---|
| 1 | 群的表示 | 线性表示，Maschke 定理，$S_3$/$S_4$ | **matmul 15×[V03]** ⭐ |
| 2 | 特征理论 | 特征，Schur 引理，正交关系 | **Schmidt 正交化** ⭐ |
| 3 | 有限群的例子 | $S_n$，诱导表示，Frobenius 互反 | **UDOT 16.9×[E05]** |
| 9 | $\mathfrak{sl}(2)$ 的表示 | 对称幂 $V_n$，最高权 | **FP16 3.81×[L01]** |
| 10 | $\mathfrak{sl}(3)$ 的表示 | 根系 $A_2$，权格点，夸克 | **分支预测[Lab02]** |
| 11 | 表示论基本定理 | Weyl 完全可约，最高权分类 | **Iron Law <2%[Lab00]** |
| 14 | 半单李代数的结构 | Killing 型，Cartan 分类，Dynkin 图 | **TLB 4.81×[E04]** |
| 15 | 半单李代数的表示 | Weyl 特征公式，维数公式 | **GEMM 9.45G[Lab05]** |
| 16 | 再论表示论 | 实表示，Clifford 代数，Spin 群 | **Schmidt 正交化** |
| 17 | 抽象/几何 | 齐性空间，Borel-Weil 定理 | **matmul 15×[V03]** |
| 附录 | 张量与组合 | Schur 函数，对称/反对称幂 | **UDOT 16.9×[E05]** |
| 总体 | 回顾与统一 | 有限群+李代数统一视角 | **FP16 3.81×[L01]** |

---

### 第 1 章 · Representations of Groups（群的表示）

- **核心**：群的「线性表示」是一个同态 $\rho: G \to \mathrm{GL}(V)$，把每个群元素变成可逆矩阵。
  - **不可约表示**(irreducible)：没有真不变子空间 $W \subset V$（$\rho(g)W \subseteq W\ \forall g$）的表示，是表示的「原子」。
  - **完全可约**：$V = W \oplus W'$，其中 $W, W'$ 均为子表示。在 $\mathbb{C}$ 上，Maschke 定理保证有限群的表示**总是完全可约**。
  - 第一个完整例子 $S_3$：三个不可约——平凡表示 $\mathbf{1}$、符号表示 $\boldsymbol{\varepsilon}$、2 维标准表示 $\mathbf{2}$。$\dim\mathbf{1}^2 + \dim\boldsymbol{\varepsilon}^2 + \dim\mathbf{2}^2 = 1+1+4 = 6 = |S_3|$。
  - $S_4$ 有 5 个不可约（平凡 $\mathbf{1}$、符号 $\boldsymbol{\varepsilon}$、3 维标准 $\mathbf{3}$、$\boldsymbol{\varepsilon}\otimes\mathbf{3}$、2 维 $\mathbf{2}$，后者来自 $S_4/V_4 \cong S_3$），$\sum d_i^2 = 1+1+9+9+4 = 24 = |S_4|$。
- **飞腾锚点**：**matmul 15×[V03]** ⭐ —— 表示 $\rho(g)$ 本质上就是把群元变成矩阵。
  - 🟢事实：直和 $V_1 \oplus V_2$ = 分块对角矩阵，张量积 $V_1 \otimes V_2$ = **Kronecker 积** $\rho_1(g) \otimes \rho_2(g)$——两者都是密集矩阵操作。GPU tensor core 做 matmul 比标量快 15×。
  - 🟡类比：$S_4$ 中 $3\otimes3$ 维张量积表示分解为 $3\oplus3\oplus3$，在 GEMM 管线上等价于 $9\times9$ 矩阵的块对角化——Maschke 定理在数值上就是矩阵的分块对角化。
- **关键定理**：**Maschke 定理**：设 $G$ 为有限群，$\rho: G\to\mathrm{GL}(V)$ 为 $\mathbb{C}$ 上表示，则 $V$ 完全可约。证明核心：取任意子表示 $W\subset V$，用「**平均投影**」$P(v)=\frac{1}{|G|}\sum_{g\in G}\rho(g)\,P_0\bigl(\rho(g)^{-1}v\bigr)$ 构造 $G$-不变补空间 $W^\perp$，使 $V=W\oplus W^\perp$。
- **物理/应用**：分子对称群（如 $H_2O$ 的 $C_{2v}$）的振动模式用不可约表示分类——对称伸缩、反对称伸缩、弯曲振动分别属于不同不可约。
- **自测**：写出 $S_3$ 的 2 维标准表示的矩阵实现（取 $V=\mathbb{C}^2$，令 $(12)\mapsto\begin{pmatrix}0&1\\1&0\end{pmatrix}$，$(123)\mapsto\begin{pmatrix}\omega&0\\0&\omega^2\end{pmatrix}$，$\omega=e^{2\pi i/3}$）。验证 $\chi_{\mathrm{std}}\bigl((123)\bigr)=\omega+\omega^2=-1$。

---

### 第 2 章 · Character Theory（特征理论）

- **核心**：表示 $\rho$ 的**特征**(character) 定义为 $\chi_\rho(g)=\mathrm{Tr}\bigl(\rho(g)\bigr)$。
  - 特征是**类函数**（共轭类上取常数），不依赖于基的选择。把「表示」（一组矩阵）压缩成「一个数列」（每个共轭类一个数），同时**保留不可约分解的全部信息**。
  - **Schur 引理**：不可约表示间的交结算子(intertwiner) $T:V_i\to V_j$（满足 $T\rho_i(g)=\rho_j(g)T$）当 $i=j$ 时为标量 $\lambda\cdot\mathrm{Id}$，当 $i\ne j$ 时为零。这是整个正交理论的基石。
  - 由此推出**正交关系**：$\langle\chi_i,\chi_j\rangle_G=\frac{1}{|G|}\sum_g\overline{\chi_i(g)}\,\chi_j(g)=\delta_{ij}$。不可约特征构成类函数空间的**正交基**。
  - 核心推论：不可约表示的个数 $k$ = 共轭类的个数；$\sum_{i=1}^k d_i^2 = |G|$（Burnside 公式的推论）。
- **飞腾锚点**：**Schmidt 正交化** ⭐ —— 特征正交关系 $\langle\chi_i,\chi_j\rangle_G=\delta_{ij}$ 就是有限群上的 **$L^2$ 内积**，与 Gram-Schmidt 正交化完全同构。
  - 🟢事实：不可约特征是类函数空间的正交基；投影公式 $a_i=\langle\chi_V,\chi_i\rangle$ 给出第 $i$ 个不可约在 $V$ 中的重数——这是「表示的 Fourier 分解」。正交投影算子 $P_i=\frac{d_i}{|G|}\sum_g\overline{\chi_i(g)}\,\rho(g)$ 把 $V$ 投影到第 $i$ 个等型分量(isotypic component)。
  - 🟡类比：Schur 引理保证不同不可约「通道」间无串扰——这正是 OFDM（正交频分复用）中子载波正交性的数学版本。
- **关键定理**：**特征的正交关系**：行正交 $\frac{1}{|G|}\sum_g\overline{\chi_i(g)}\,\chi_j(g)=\delta_{ij}$；列正交 $\sum_{i=1}^k\overline{\chi_i(g)}\,\chi_i(h)=\frac{|G|}{|C_G(g)|}\,\delta_{g\sim h}$（$C_G(g)$ 为中心化子）。推论：不可约个数 $k$=共轭类个数；$\sum d_i^2=|G|$。
- **物理/应用**：分子振动光谱的选择定则——红外活性振动对应特征在恒等表示中出现的次数 $a_{\text{trivial}}=\langle\chi_{\text{vib}},\chi_{\text{trivial}}\rangle$。
- **自测**：验证 $S_3$ 特征表满足 $\langle\chi_i,\chi_j\rangle=\delta_{ij}$：

| | $e$ (1个) | $(12)$ (3个) | $(123)$ (2个) |
|---|---|---|---|
| 平凡 $\chi_1$ | 1 | 1 | 1 |
| 符号 $\chi_2$ | 1 | $-1$ | 1 |
| 标准 $\chi_3$ | 2 | 0 | $-1$ |

并用列正交验证第 2 列与第 3 列正交：$\sum_i\overline{\chi_i((12))}\,\chi_i((123))=1\cdot1+(-1)\cdot1+0\cdot(-1)=0$。

---

### 第 3 章 · Examples; Induced Representations（有限群的例子与诱导表示）

- **核心**：本章系统计算**对称群 $S_n$** 的表示，然后引入**诱导表示**。
  - **Young 图**：$n$ 的分拆 $\lambda\vdash n$（如 $3=2+1$）画成行长度递减的格点图。Specht 模 $S^\lambda$ 与不可约表示一一对应。$S_4$ 的 5 个分拆 $(4),(3{,}1),(2{,}2),(2{,}1{,}1),(1{,}1{,}1{,}1)$ 恰好对应 5 个不可约。
  - **诱导表示** $\mathrm{Ind}_H^G(W)$：给定子群 $H\le G$ 和 $H$ 的表示 $W$，诱导表示是 $G$ 作用在 $\bigoplus_{gH\in G/H}g\cdot W$ 上的表示，维度 $= [G:H]\cdot\dim W$。
  - **Frobenius 互反律**：$\langle\mathrm{Ind}\,\chi_W,\,\psi\rangle_G=\langle\chi_W,\,\mathrm{Res}\,\psi\rangle_H$——诱导与限制互为共轭（伴随），是表示论的核心对偶性。
  - **交替群 $A_n$**：$S_n$ 的不可约限制到 $A_n$ 后，要么保持不可约，要么分裂为两个等维不可约（对应「自共轭」Young 图），由此获得 $A_n$ 的特征表。
- **飞腾锚点**：**UDOT 16.9×[E05]** —— 诱导表示的特征公式 $\chi_{\mathrm{Ind}}(g)=\frac{1}{|H|}\sum_{\substack{x\in G\\xgx^{-1}\in H}}\chi_W\bigl(xgx^{-1}\bigr)$ 本质上是群上的大规模求和——**点积累加**。
  - 🟢事实：Frobenius 互反律的验证需要大量 $\sum_g\overline{\chi(g)}\,\psi(g)$ 内积计算；UDOT 的点积加速器天然映射这种「群上求和」，16.9× 加速适合 $|G|$ 较大时的批量特征内积。
  - 🟡类比：Young 图的表格填充数(tabloid) 枚举是组合求和——每个 tabloid 贡献一项，类似点积展开中的逐项累加。
- **关键定理**：**Frobenius 互反律**：$\langle\mathrm{Ind}_H^G\,\chi_W,\,\psi\rangle_G=\langle\chi_W,\,\mathrm{Res}_H^G\,\psi\rangle_H$。诱导 $\mathrm{Ind}$ 与限制 $\mathrm{Res}$ 互为共轭操作。
- **物理/应用**：$S_n$ 的不可约表示通过 Young 图对应粒子物理中的置换对称性——玻色子/费米子的统计性质由 $S_n$ 的平凡/符号表示描述。
- **自测**：将 $S_3$ 的 2 维标准表示限制到 $A_3=\langle(123)\rangle\cong\mathbb{Z}/3$。$\chi_{\mathrm{std}}((123))=-1=\omega+\omega^2$，故 $\mathrm{Res}=\chi_\omega\oplus\chi_{\omega^2}$。再用 Frobenius 互反验证 $\langle\mathrm{Ind}_{A_3}^{S_3}\chi_\omega,\,\chi_{\mathrm{std}}\rangle_{S_3}=1$（故 $\mathrm{Ind}\,\chi_\omega=\chi_{\mathrm{std}}$，维度 $2=2\times1$）。

---

### 第 9 章 · Representations of $\mathfrak{sl}(2;\mathbb{C})$（$\mathfrak{sl}(2)$ 的表示）

- **核心**：从有限群跨入李代数——$\mathfrak{sl}(2)$ 是整个半单理论的**原型与试金石**。
  - 生成元：$H=\begin{pmatrix}1&0\\0&-1\end{pmatrix}$，$E=\begin{pmatrix}0&1\\0&0\end{pmatrix}$，$F=\begin{pmatrix}0&0\\1&0\end{pmatrix}$，满足 $[H,E]=2E$，$[H,F]=-2F$，$[E,F]=H$。
  - **对称幂构造**：$V_n=\mathrm{Sym}^n(\mathbb{C}^2)$ 是 $n+1$ 维不可约，$H$ 的特征值（权）为 $n,n-2,\ldots,-n$。$E$ 升权 $+2$（在权链上右移），$F$ 降权 $-2$（左移）。
  - **最高权向量** $v_0$：满足 $Ev_0=0$，$Hv_0=nv_0$。整个 $V_n$ 由反复作用 $F$ 生成：$v_k\propto F^k v_0$。
  - **Clebsch-Gordan 分解**：$V_m\otimes V_n=\bigoplus_{k=|m-n|}^{m+n}V_k$（步长 2），是 $\mathfrak{sl}(2)$ 最核心的计算工具。物理对应：自旋耦合 $j_1\otimes j_2=\bigoplus J$。
  - 关键定理：**$\mathfrak{sl}(2)$ 的所有有限维不可约**恰为 $\{V_n\}_{n\ge0}$。
- **飞腾锚点**：**FP16 3.81×[L01]** —— 权值 $n,n-2,\ldots,-n$ 是**等差数列**，步长固定 2，权值为精确整数/半整数。
  - 🟢事实：$H$ 在 $V_n$ 上是对角矩阵，对角元素为精确整数 $n-2k$；FP16 的 3.81× 吞吐适合批量权计算——但 $n$ 很大时需注意 FP16 数值范围（最大 65504）。对称幂 $\mathrm{Sym}^n$ 基向量数 $\binom{n+1}{1}=n+1$ 随 $n$ 线性增长。
  - 🟡类比：Clebsch-Gordan 系数的查表操作映射为低精度快速检索——FP16 足够存储这些有理系数。
- **关键定理**：**$\mathfrak{sl}(2)$ 分类定理**：每个有限维不可约 $\mathfrak{sl}(2)$-模 $\cong V_n=\mathrm{Sym}^n(\mathbb{C}^2)$，$\dim V_n=n+1$。权为 $n,n-2,\ldots,-n$（各重数 1）。
- **物理/应用**：$V_n$ 对应自旋 $j=n/2$ 的粒子（$2j+1=n+1$ 个磁量子态）。氢原子的角动量本征态 $|l,m\rangle$ 构成 $V_{2l}$，$m=-l,\ldots,l$。
- **自测**：分解 $V_1\otimes V_1=\mathbb{C}^2\otimes\mathbb{C}^2$。用 Clebsch-Gordan：$V_1\otimes V_1=V_2\oplus V_0$（维度 $4=3+1$）。物理：自旋 $\frac{1}{2}\otimes\frac{1}{2}=1\oplus0$（三重态+单态）。手算验证：$E$ 在 $V_2\oplus V_0$ 上的矩阵确实是两个分块。

---

### 第 10 章 · Representations of $\mathfrak{sl}(3;\mathbb{C})$（$\mathfrak{sl}(3)$ 的表示）

- **核心**：从 $\mathfrak{sl}(2)$ 的「一条权线」跳到 $\mathfrak{sl}(3)$ 的「二维权格点」——根系 $A_2$ 的几何首次登场。
  - **根系 $A_2$**：6 个根 $\pm\alpha_1,\pm\alpha_2,\pm(\alpha_1+\alpha_2)$ 排成**正六边形**。$\mathfrak{sl}(3)$ 的秩为 2，Cartan 子代数 $\mathfrak{h}\cong\mathbb{C}^2$。
  - 标准表示 $V=\mathbb{C}^3$ 的权为 $L_1,L_2,L_3$（$L_1+L_2+L_3=0$）；$V^*$ 的权为 $-L_1,-L_2,-L_3$，图形上是 $V$ 权图的中心反射。
  - **最高权 $(a,b)$** 参数化不可约：$\Gamma_{a,b}=\mathrm{Sym}^a(V)\otimes\mathrm{Sym}^b(V^*)$。维数 $\dim\Gamma_{a,b}=\frac{1}{2}(a+1)(b+1)(a+b+2)$。
  - **Weyl 群** $W\cong S_3$（6 个元素）作用在权格点上——权图具有正六边形对称性。
  - **物理彩蛋**：$\Gamma_{1,0}=\mathbf{3}$（夸克）、$\Gamma_{0,1}=\bar{\mathbf{3}}$（反夸克）、$\Gamma_{1,1}=\mathbf{8}$（胶子八重态）——SU(3) 夸克模型的数学基础。$\mathbf{3}\otimes\bar{\mathbf{3}}=\mathbf{8}\oplus\mathbf{1}$ 对应 $q\bar{q}$ 介子。
- **飞腾锚点**：**分支预测[Lab02]** —— 权格点构成三角网格，**Weyl 室**(fundamental chamber) 的选择决定最高权归属——本质是**条件分支**。
  - 🟢事实：Weyl 群 $W\cong S_3$ 的每个反射是分支判断「权 $\mu$ 是否在根 $\alpha$ 的正侧 $\langle\mu,\alpha\rangle>0$」。分支预测准确率高 = 根系规整（$A_n$ 型格点均匀对称）。
  - 🟡类比：CPU 分支预测器猜测 if-else 走向；Weyl 群反射就是在权格点上「翻转分支」。$\Gamma_{a,b}$ 的权图中，Weyl 群轨道 = 六边形/六角星对称图案。
- **关键定理**：**$\mathfrak{sl}(3)$ 最高权分类**：不可约 ↔ 支配整权 $(a,b)$（$a,b\ge0$）一一对应。$\dim\Gamma_{a,b}=\frac{(a+1)(b+1)(a+b+2)}{2}$。
- **物理/应用**：$\Gamma_{1,0}=\mathbf{3}$（三种色荷的夸克 $u,d,s$），$\Gamma_{1,1}=\mathbf{8}$（Gell-Mann 的八正道 Eightfold Way——胶子/介子八重态），$\Gamma_{2,2}=\mathbf{27}$。
- **自测**：计算 $\mathbf{3}\otimes\bar{\mathbf{3}}=\Gamma_{1,0}\otimes\Gamma_{0,1}$ 分解。（答案：$\Gamma_{1,1}\oplus\Gamma_{0,0}=\mathbf{8}\oplus\mathbf{1}$，维度 $9=8+1$。物理：$q\bar{q}=$ 八重态 $\oplus$ 单态。验证 $\dim\Gamma_{1,1}=\frac{1}{2}\cdot2\cdot2\cdot4=8$。）

---

### 第 11 章 · The Fundamental Theorem（表示论基本定理）

- **核心**：把 $\mathfrak{sl}(2)$、$\mathfrak{sl}(3)$ 的经验**提升为一般定理**——两个支柱解决核心分类问题。
  - **(1) Weyl 完全可约定理**：半单李代数的每个有限维表示都是不可约的直和。这是李代数版的 Maschke 定理，但证明用 **Weyl 的「酉技巧」**(unitary trick)：$\mathfrak{g}\rightsquigarrow$ 紧致群 $G$（如 $\mathfrak{sl}(n)\rightsquigarrow\mathrm{SU}(n)$）$\rightsquigarrow$ 取 $G$-不变 Hermit 内积（用 Haar 测度平均）$\rightsquigarrow$ 正交补给出 $G$-不变分解 $\rightsquigarrow$ 回到 $\mathfrak{g}$。
  - **(2) 最高权定理**：不可约表示与**支配整权** $\Lambda^+$ 一一对应。合起来：有限维表示 = 不可约直和，不可约由最高权完全确定——**表示论的核心分类问题在此彻底解决**。
  - 关键区别：有限群用「平均投影」(Maschke) 保证完全可约；半单李代数用「酉技巧」(Weyl) 保证。前者是纯代数，后者借道紧致群的调和分析。
- **飞腾锚点**：**Iron Law <2%[Lab00]** —— Weyl 完全可约保证分解 $V=\bigoplus V_i$ **精确**（无残余误差），类比 Iron Law 的 <2% 误差控制。
  - 🟢事实：酉技巧的数值实现中，$G$-不变内积的构造误差反映在补空间投影残余项上；完全可约 = 矩阵精确分块对角化，残余范数 $<\epsilon$。注意：**无限维表示不再完全可约**，酉技巧失效——Iron Law 的保证仅限有限维。
  - 🟡类比：Weyl 酉技巧把「李代数问题」转化为「紧致群问题」再转回，类似 Lab00 中用「精确格式」替代「近似格式」以保证误差有界。
- **关键定理**：**Weyl 完全可约定理**：设 $\mathfrak{g}$ 为特征 0 代数闭域上半单李代数，则每个有限维 $\mathfrak{g}$-模完全可约。推论：不可约由最高权 $\lambda\in\Lambda^+$ 唯一分类。
- **物理/应用**：Weyl 的酉技巧把 $\mathfrak{sl}(n)$ 的问题归结为紧群 $\mathrm{SU}(n)$——这正是粒子物理中规范对称性「可以从李代数直接读出表示」的数学根基。
- **自测**：为什么 $\mathfrak{sl}(2)$ 的表示总是完全可约，而 Borel 子代数 $\mathfrak{b}=\langle H,E\rangle$（非半单）的表示不一定？给出 $\mathfrak{b}$ 上 2 维**不可分解但非不可约**的表示。（提示：令 $H=\begin{pmatrix}1&0\\0&0\end{pmatrix}$，$E=\begin{pmatrix}0&1\\0&0\end{pmatrix}$，有不变子空间 $\langle e_1\rangle$ 但无 $E$-不变补。）

---

### 第 14 章 · The Structure of Semisimple Lie Algebras（半单李代数的结构）

- **核心**：本章是**结构论的集大成**——把 $\mathfrak{sl}(2)$、$\mathfrak{sl}(3)$ 的经验抽象成一般理论。
  - **Killing 型**：$B(X,Y)=\mathrm{Tr}\bigl(\mathrm{ad}_X\,\mathrm{ad}_Y\bigr)$ 是李代数上的不变对称双线性型。**Cartan 判据**：$\mathfrak{g}$ 半单当且仅当 $B$ 非退化。
  - **Cartan 子代数** $\mathfrak{h}$：极大环面（可同时对角化）子代数。$\mathfrak{g}$ 分解为 $\mathfrak{h}\oplus\bigoplus_{\alpha\in\Phi}\mathfrak{g}_\alpha$（根空间分解），$\Phi\subset\mathfrak{h}^*$ 为根系。
  - **根系公理**：$\Phi$ 张满 $\mathfrak{h}^*$；对反射 $s_\alpha(\beta)=\beta-\langle\beta,\alpha^\vee\rangle\alpha$ 封闭（$\alpha^\vee=2\alpha/\langle\alpha,\alpha\rangle$）；整性 $\langle\alpha,\beta^\vee\rangle\in\mathbb{Z}$。
  - **Dynkin 图**：节点 = 单根，边数 = 夹角编码（无连 $=90°$、单连 $=120°$、双连 $=135°$、三连 $=150°$）。箭头指向较短根。
  - **Cartan 分类定理**：不可约根系只有 $A_n(n\ge1)$, $B_n(n\ge2)$, $C_n(n\ge3)$, $D_n(n\ge4)$ 四族经典系列，加 $E_6,E_7,E_8,F_4,G_2$ 五个例外。
- **飞腾锚点**：**TLB 4.81×[E04]** —— 根系 $\Phi$ 的几何具有极强**局部结构**：每个根的行为由相邻单根决定（局部性 = TLB 页表局部性）。
  - 🟢事实：Cartan 子代数 $\mathfrak{h}$ 是所有权计算的「热路径」(hot path)——所有权的计算都访问 $\mathfrak{h}^*$。Dynkin 图的连通性 = 内存布局连续性；TLB 命中率高的根系（小秩、连通链）检索加速 4.81×。
  - 🟡类比：Dynkin 图的分类（$A_n$ 链 → $D_n$ 分叉 → $E_8$ 复杂图）类似 CPU 分支预测树——简单链命中率高，复杂分叉可能 cache miss。
- **关键定理**：**Cartan 分类定理**：不可约根系恰为 $A_n,B_n,C_n,D_n$（经典四族）$+E_6,E_7,E_8,F_4,G_2$（五个例外），由 Dynkin 图唯一确定。$\mathfrak{sl}(n+1)=A_n$，$\mathfrak{so}(2n+1)=B_n$，$\mathfrak{sp}(2n)=C_n$，$\mathfrak{so}(2n)=D_n$。
- **物理/应用**：$A_n=\mathfrak{sl}(n+1)$ 对应规范场论的大统一群（$\mathrm{SU}(5)$ 大统一 = $A_4$）；$D_n=\mathfrak{so}(2n)$ 对应弦论中的规范对称；$E_8$ 出现在异构弦(heterotic string) 与 Garrett Lisi 的「万物理论」尝试中。
- **自测**：画 $A_2$（$\mathfrak{sl}(3)$）、$B_2$（$\mathfrak{so}(5)$）、$G_2$ 的 Dynkin 图。$G_2$ 三重边对应根长比 $\sqrt{3}:1$，单根夹角 $150°$。验证 $\mathfrak{sl}(n)$ 的 Killing 型 $B(X,Y)=2n\,\mathrm{tr}(XY)$。

---

### 第 15 章 · Representations of Semisimple Lie Algebras（半单李代数的表示）

- **核心**：本章是**表示论的巅峰**——用根系语言统一所有半单李代数的表示。
  - **权格** $\Lambda$：所有整权的格点。**支配整权** $\Lambda^+$：在 Weyl 室内的整权。不可约 $V_\lambda$ 由 $\lambda\in\Lambda^+$ 唯一确定。
  - **Weyl 群** $W$：根系反射 $s_\alpha$ 生成的有限群（$A_n$ 的 $W\cong S_{n+1}$）。Weyl 群是「权空间的对称群」，把权图变成高度对称的几何图形。
  - **Weyl 向量** $\rho$：$\rho=\frac{1}{2}\sum_{\alpha>0}\alpha$（半正根和），满足 $s_\alpha(\rho)=\rho-\alpha$ 对所有单根 $\alpha$。是 Weyl 公式的关键辅助量。
  - **Weyl 特征公式**：$\chi_\lambda=\frac{\sum_{w\in W}\varepsilon(w)\,e^{w(\lambda+\rho)}}{\sum_{w\in W}\varepsilon(w)\,e^{w(\rho)}}$，给出不可约特征的精确表达式。
  - **Weyl 维数公式**：$\dim V_\lambda=\prod_{\alpha\in\Phi^+}\frac{\langle\lambda+\rho,\,\alpha^\vee\rangle}{\langle\rho,\,\alpha^\vee\rangle}$——纯根系几何决定维数。一切归结为根系的几何。
- **飞腾锚点**：**GEMM 9.45G[Lab05]** —— Weyl 特征公式需对**整个 Weyl 群** $W$ 求和（$|W|$ 项），每项含指数 $e^{w(\lambda+\rho)}$——**高维批量吞吐**。
  - 🟢事实：把 $|W|\times|\text{权空间}|$ 排成大矩阵，一次 GEMM 完成所有 Weyl 群元素的反射。$E_8$ 的 $|W|=696{,}729{,}600$——GEMM 的 9.45G 吞吐在此至关重要。
  - 🟡类比：Weyl 维数公式的连乘 $\prod_{\alpha>0}$ 可向量化为点积——每个正根贡献一个比值因子，批量计算类似 GEMM 行向量乘法。
- **关键定理**：**Weyl 维数公式**：$\dim V_\lambda=\prod_{\alpha\in\Phi^+}\frac{\langle\lambda+\rho,\,\alpha^\vee\rangle}{\langle\rho,\,\alpha^\vee\rangle}$，$\alpha^\vee=2\alpha/\langle\alpha,\alpha\rangle$ 为余根(coroot)。
- **物理/应用**：Weyl 维数公式直接给出粒子物理中表示的维度——如 $E_8$ 的伴随表示 $248$ 维、$\mathfrak{sl}(5)$ 的 $\Gamma_{1,0,0,0}=\mathbf{5}$ 维（$\mathrm{SU}(5)$ 大统一的 $\mathbf{5}$ 表示）。
- **自测**：用 Weyl 维数公式验证 $\mathfrak{sl}(3)$ 的 $\Gamma_{1,1}$（$\mathbf{8}$）维数。正根 $\alpha_1,\alpha_2,\alpha_1+\alpha_2$；$\rho=\omega_1+\omega_2$；$\lambda=\omega_1+\omega_2$（$\omega_i$ 基本权）。逐项：$\frac{\langle2\omega_1+2\omega_2,\,\alpha_1^\vee\rangle}{\langle\omega_1+\omega_2,\,\alpha_1^\vee\rangle}\cdot\frac{\cdots}{\cdots}\cdot\frac{\cdots}{\cdots}=\frac{2}{1}\cdot\frac{2}{1}\cdot\frac{4}{2}=8$。

---

### 第 16 章 · More on Representations; Clifford Algebras（再论表示论；Clifford 代数）

- **核心**：本章处理两个「实战」问题——实/复/四元数型分类与 Spin 群。
  - **(1) Frobenius-Schur 指标**：复不可约分三类——**实型**(real type，$\mathrm{FS}=+1$，来自实表示)、**复型**(complex type，$\mathrm{FS}=0$，$V\not\cong V^*$)、**四元数型**(quaternionic type，$\mathrm{FS}=-1$，有不变反埃尔米特型)。指标 $\mathrm{FS}(\chi)=\frac{1}{|G|}\sum_g\chi(g^2)\in\{+1,0,-1\}$。
  - **(2) Clifford 代数** $\mathrm{Cl}(n)$：由 $v^2=-\|v\|^2$ 定义的外代数升级版。生成元满足 $\gamma_i\gamma_j+\gamma_j\gamma_i=-2\delta_{ij}I$——Dirac 矩阵的正交关系。
  - **Spin 群** $\mathrm{Spin}(n)\subset\mathrm{Cl}(n)$：$\mathrm{SO}(n)$ 的**通用双重覆盖**（$1\to\mathbb{Z}/2\to\mathrm{Spin}(n)\to\mathrm{SO}(n)\to1$）。$\mathrm{Spin}(3)\cong\mathrm{SU}(2)$，$\mathrm{Spin}(n)$ 单连通。
  - **Spin 表示**：物理学中**费米子**的数学家园——Dirac 方程的旋量(spinor)就是 Spin 表示。$\mathrm{Spin}(3)\cong\mathrm{SU}(2)$ 的 2 维旋量描述电子自旋。
- **飞腾锚点**：**Schmidt 正交化** —— Frobenius-Schur 指标 $\frac{1}{|G|}\sum_g\chi(g^2)$ 本质是特征在「平方映射」下的内积——正交投影变体。
  - 🟢事实：实型/复型/四元数型的判定 = 寻找 $G$-不变双线性型/半双线性型——Gram-Schmidt 正交化的推广。实型有不变对称双线性型，四元数型有不变反埃尔米特型。
  - 🟡类比：Clifford 代数中 $\gamma_i\gamma_j+\gamma_j\gamma_i=-2\delta_{ij}$ 的正交关系，类比 Schmidt 正交化——Dirac 矩阵 $\gamma_\mu$ 是 Clifford 代数的正交基。
- **关键定理**：**Frobenius-Schur 指标定理**：$\mathrm{FS}(V_i)=\frac{1}{|G|}\sum_{g\in G}\chi_i(g^2)$。$+1$ $\Leftrightarrow$ 实型；$-1$ $\Leftrightarrow$ 四元数型；$0$ $\Leftrightarrow$ 复型。
- **物理/应用**：Spin 群 $\mathrm{Spin}(3)\cong\mathrm{SU}(2)$ 描述电子自旋（旋量），$\mathrm{Spin}(n)$ 在弦论与超对称中描述费米子。Dirac 矩阵 $\gamma_\mu$ 是 $\mathrm{Cl}(1,3)$ 的表示。
- **自测**：$S_3$ 的三个不可约 FS 指标各多少？平凡 $\mathrm{FS}=\frac{1}{6}(1\cdot1+3\cdot1+2\cdot1)=1$；符号同 $=1$；标准 $\mathrm{FS}=\frac{1}{6}(1\cdot2+3\cdot2+2\cdot(-1))=\frac{6}{6}=1$——均为实型。验证 $\mathrm{SU}(2)$ 的 2 维标准表示 $\mathrm{FS}=-1$（四元数型，因 $\mathrm{SU}(2)\cong\mathrm{Sp}(1)$）。

---

### 第 17 章 · Lie Groups and Homogeneous Spaces（李群与齐性空间）

- **核心**：本章把表示从代数拉回**几何**——Borel-Weil 定理给出不可约的几何实现。
  - **齐性空间** $G/H$：群 $G$ 模掉子群 $H$ 的高度对称流形。球面 $S^n=\mathrm{SO}(n+1)/\mathrm{SO}(n)$，射影空间 $\mathbb{CP}^n=\mathrm{SU}(n+1)/U(n)$，**旗流形** $G/B$（$B$ 为 Borel 子群，上三角）。
  - **线丛** $\mathcal{L}_\lambda=G\times_B\mathbb{C}_{-\lambda}$：旗流形 $G/B$ 上由权 $\lambda$ 决定的等变线丛。
  - **Borel-Weil 定理**：$H^0(G/B,\mathcal{L}_\lambda)$（全纯截面空间）作为 $G$-表示不可约，最高权为 $\lambda$。表示不再只是抽象向量空间，而是「**函数空间**」——几何表示论的起点。
  - 后续发展：Atiyah-Bott（不动点定理）、Beilinson-Bernstein（局部化定理）都从这里出发，将表示论与代数几何、D-模深刻联系。
- **飞腾锚点**：**matmul 15×[V03]** —— Borel-Weil 把表示实现为截面空间，$G$ 在截面上作用是矩阵变换。
  - 🟢事实：齐性空间上函数用球谐/矩阵系数展开后，$G$ 的作用化为有限维矩阵——V03 的 15× matmul 直接利好「函数空间上的群作用」计算。
  - 🟡类比：旗流形 $G/B$ 上线丛 $\mathcal{L}_\lambda$ 类似神经网络特征映射——「截面」=流形上的特征场，群作用是等变变换(equivariant transform)。
- **关键定理**：**Borel-Weil 定理**：设 $G$ 连通复半单李群，$B$ Borel 子群，$\lambda$ 支配整权。则 $H^0(G/B,\mathcal{L}_\lambda)$ 不可约，最高权 $\lambda$；遍历 $\lambda\in\Lambda^+$ 给出所有不可约。
- **物理/应用**：Borel-Weil 在共形场论(CFT) 中给出 Virasoro 代数表示的几何构造；在弦论中描述闭弦在旗流形上的传播。
- **自测**：对 $G=\mathrm{SL}(2;\mathbb{C})$，旗流形 $G/B\cong\mathbb{CP}^1$。线丛 $\mathcal{L}_n=\mathcal{O}(n)$ 的截面 $H^0(\mathbb{CP}^1,\mathcal{O}(n))$ 维数多少？对应哪个 $\mathfrak{sl}(2)$ 不可约？（答案：$\dim=n+1$，对应 $V_n$——Borel-Weil 重现第 9 章 $V_n=\mathrm{Sym}^n(\mathbb{C}^2)$。）

---

### 附录与专题 · Tensors, Symmetric Powers, Schur Functions（张量、对称幂与 Schur 函数）

- **核心**：表示论与**组合数学**的深度交叉——「表示 = 对称函数 = 组合」的三位一体。
  - **对称幂 $\mathrm{Sym}^n(V)$ / 外幂 $\wedge^n V$**：构造新表示的基本操作。$\mathrm{Sym}^n$ 对应完全对称张量（$S_n$ 的平凡表示），$\wedge^n$ 对应完全反对称（$S_n$ 的符号表示）。
  - **Schur 函数** $s_\lambda(x_1,\ldots,x_k)$：对称函数理论的基石，同时是 $\mathrm{GL}(n)$ 不可约 $\lambda$ 的**特征多项式**。$s_\lambda$ 的系数 = 不可约特征在矩阵对角元上的值。
  - **Littlewood-Richardson 规则**：$V_\lambda\otimes V_\mu=\bigoplus_\nu c_{\lambda\mu}^\nu V_\nu$，系数 $c_{\lambda\mu}^\nu$ 由 LR-表(LR-tableaux) 的组合计数决定——纯组合地计算张量积分解。
  - 这是与**表示稳定性**(representation stability)、**代数组合论**接轨的桥梁。
- **飞腾锚点**：**UDOT 16.9×[E05]** —— Schur 函数 $s_\lambda=\sum_T x^T$ 对所有半标准 Young 表 $T$ 求和——**大规模点积累加**。
  - 🟢事实：LR 系数 $c_{\lambda\mu}^\nu$ 的计算涉及 LR-表的枚举求和，本质是组合计数；UDOT 点积加速器天然适合批量组合求和。
  - 🟡类比：$\mathrm{Sym}^n$ = 多项式特征映射（ML 中的 polynomial features），$\wedge^n$ = 行列式/Plücker 坐标——两者都是基本非线性特征构造。
- **关键定理**：**Littlewood-Richardson 规则**：$V_\lambda\otimes V_\mu=\bigoplus_\nu c_{\lambda\mu}^\nu V_\nu$，$c_{\lambda\mu}^\nu$ = 满足 LR-规则的格点排列数。
- **物理/应用**：LR 规则在量子信息中描述多粒子系统的对称化——如三个夸克 $qqq$ 的味道波函数用 LR 规则分解为 $\mathbf{10}\oplus\mathbf{8}\oplus\mathbf{8}\oplus\mathbf{1}$（重子十重态 + 八重态 + 八重态 + 单态）。
- **自测**：用 LR 规则计算 $\mathfrak{sl}(3)$ 中 $\mathbf{3}\otimes\mathbf{3}=\Gamma_{1,0}\otimes\Gamma_{1,0}$。（答案：$\Gamma_{2,0}\oplus\Gamma_{0,1}=\mathbf{6}\oplus\bar{\mathbf{3}}$，维度 $9=6+3$。$\dim\Gamma_{2,0}=\frac{1}{2}\cdot3\cdot1\cdot4=6$。）

---

### 总体回顾 · The Unifying View（表示论的统一视角）

- **核心**：回顾全书，两大主线在**根系 + 权格**处合流。
  - **有限群主线**(Ch1–3)：表示 → 特征 → 正交关系 → 特征表。核心 = **群上的 Fourier 分析**——不可约特征是类函数空间的正交基。特征表是「群的指纹」。
  - **李代数主线**(Ch9–11,14–15)：表示 → 权分解 → 最高权 → Weyl 特征公式。核心 = **根系几何**——不可约由支配整权参数化。
  - **共同骨架**：Schur 引理（不可约间交结算子 = 标量）、完全可约（Maschke/Weyl）、正交性（特征/权的内积）——两线共享的三大支柱。
  - **Peter-Weyl 定理**在紧致群上统一两者：不可约的矩阵系数构成 $L^2(G)$ 的正交基。$G=S^1$ 退化为经典 Fourier 级数。
- **飞腾锚点**：**FP16 3.81×[L01]** —— 有限群特征表是「小而精」的精确整数矩阵；李代数权格点是「大而广」的浮点矩阵。
  - 🟢事实：FP16 的 3.81× 加速适合大批量权格点计算（高维李代数如 $E_8$ 的 248 维）；有限群特征表数据小、值精确，用 INT8 甚至位运算即可。两种精度的切换映射了表示论的两条主线。
  - 🟡类比：Peter-Weyl 中 $L^2(G)$ 的矩阵系数正交基 = 频域 Fourier 基——「特征正交」与「Fourier 正交」是同一数学结构的不同实例。
- **关键定理**：**Peter-Weyl 定理**：设 $G$ 紧致群，$\{\rho_i\}$ 遍历不可约表示，则矩阵系数 $\sqrt{d_i}\,\rho_i(g)_{kl}$ 构成 $L^2(G)$（关于 Haar 测度）的正交基。有限群类函数正交(Ch2)是其特例。
- **物理/应用**：Peter-Weyl 定理在信号处理中对应「紧致群上的广义 Fourier 分析」——球面调和函数是 $\mathrm{SO}(3)$ 的 Peter-Weyl 展开的特例。
- **自测**：用 Peter-Weyl 解释——为什么 $S^1$ 的不可约都是 1 维（参数 $n\in\mathbb{Z}$），而 $\mathrm{SU}(2)$ 的不可约可以是任意维 $V_n$？（$S^1$ 是 Abel 群，不可约必 1 维；$\mathrm{SU}(2)$ 非交换，有高维不可约 $V_n$，$n=0,1,2,\ldots$）

---

## §9 全书思想主线（约 200 字）

Fulton-Harris 的双线叙事——**有限群(Ch1–3，特征正交) ↔ 李代数(Ch9–11，最高权)**——最终在 **Ch14–15（根系 + Dynkin 图）**处合流。有限群这边，核心是**特征**(迹函数) 与**正交关系**($\langle\chi_i,\chi_j\rangle=\delta_{ij}$)，本质是群上的 Fourier 分析；不可约个数 = 共轭类个数，$\sum d_i^2=|G|$，特征表是「群的指纹」。李代数这边，核心是**权**与**最高权**，本质是 Cartan 子代数上的格点几何；不可约由支配整权参数化，Weyl 特征公式给出精确表达式。两座桥梁：**Schur 引理**（不可约间交结算子是标量）贯穿全书——有限群和李代数都靠它推出正交性；**Weyl 特征公式**把有限群特征的「行列正交」升级为根系反射的「交替和」。与 Humphreys（纯李代数结构，无表示）互补：Humphreys 讲根系「长什么样」，Fulton-Harris 讲根系「怎么分类表示」。与 Hall（李群+物理）呼应：Hall 的 $\mathrm{SU}(2)$ 旋量是 Fulton-Harris $V_n$ 的物理化身。

---

## §10 与本仓库其他笔记的交叉引用

### 与已精读书目的呼应

| 本书 | 关系 | 交叉点 |
|---|---|---|
| **Humphreys《李代数》GTM9** | 结构互补 | Humphreys Ch1–3（可解/幂零/半单判定、Killing 型）→ FH Ch14 直接用；Humphreys 不讲表示，FH 补上 |
| **Hall《李群》GTM222** | 物理互补 | Hall Ch4–5（$\mathrm{SU}(2)$/$\mathrm{SU}(3)$ 的表示）→ FH Ch9–10 的代数版本；Hall 的 BCH 公式 ↔ FH 的指数映射 |
| **Dummit & Foote《抽象代数》** | 基础前置 | D&F Part I（群论基础）↔ FH Ch1–3 的有限群；D&F 的模论 ↔ FH 的表示 = 模观点 |
| **Serre《线性表示》** | 精简对照 | Serre 的有限群表示极简证明 ↔ FH Ch1–3 的详细展开；Serre 是 FH Part I 的「精华浓缩版」 |

### AI/工程锚点法：表示论的工程落地

| 数学概念 | AI/工程对应 | 锚点说明 |
|---|---|---|
| **表示 = 群在向量空间上的作用** | 特征提取 / 嵌入 | 🟢群表示 $\rho:G\to\mathrm{GL}(V)$ = 把对称性编码成线性变换；等变神经网络(equivariant NN) 的数学基础 |
| **特征 $\chi=\mathrm{Tr}(\rho)$** | Fourier 变换在群上的推广 | 🟢特征是「压缩表示」的一维摘要；有限群特征表 = 群上 DFT 矩阵；紧群 Peter-Weyl = 连续 Fourier |
| **不可约表示 = 基本构件** | 基函数 / 原子特征 | 🟢不可约是表示空间的「原子」，任意表示 = 不可约直和 = 任意信号 = 基函数线性组合 |
| **Schur 引理 = 不可约间无混合** | 正交基 / 信息不泄漏 | 🟢Schur 引理保证不同不可约「通道」间无串扰 = OFDM 正交频分复用的数学版 |
| **诱导表示 $\mathrm{Ind}_H^G$** | 数据增广 / 扩充 | 🟡类比：从小群 $H$ 的表示「升格」到大群 $G$，类似用小数据集增广到大集 |
| **对称幂 $\mathrm{Sym}^n$ / 外幂 $\wedge^n$** | 多项式特征 / 高阶统计量 | 🟢$\mathrm{Sym}^n(V)$ = $n$ 次多项式特征映射；$\wedge^n V$ = 行列式推广 |
| **Weyl 特征公式** | 闭式解 / 解析公式 | 🟢用根系几何给出精确特征，无需逐元素计算；类似用 FFT 替代 DFT 加速 |
| **Dynkin 图分类** | 架构分类 / 拓扑编码 | 🟡类比：Dynkin 图用最少边编码李代数 = 计算图用最少节点编码网络结构 |
| **Borel-Weil 几何实现** | 流形上的函数空间 | 🟡类比：表示 = 流形上的截面 = 特征映射在流形上的推广(manifold learning) |
| **Littlewood-Richardson 规则** | 组合枚举 / 动态规划 | 🟢LR 系数 $c_{\lambda\mu}^\nu$ 的组合计算 = 网格路径计数，可向量化为矩阵运算 |
| **Weyl 群 = 根系反射群** | 数据增强 / 对称变换 | 🟡类比：Weyl 群作用在权格上翻转，类似数据增强中翻转/旋转图像以扩增训练集 |
| **特征表 = 群的 DFT 矩阵** | 频域分析 / 谱方法 | 🟢有限群特征表的行正交 = DFT 矩阵的酉性；紧群的 Peter-Weyl = 连续 Fourier 变换 |
| **诱导表示的伴随性** | 升采样 / 上采样 | 🟡类比：$\mathrm{Ind}_H^G$ 把子群信号「上采样」到全群，$\mathrm{Res}$ 反之「下采样」 |

### 学习路径建议（基于本仓库已有笔记）

1. **先修**：Dummit & Foote Part I（群论基础）+ Humphreys Ch1–3（李代数结构、Killing 型、Cartan 判据）
2. **并行**：Hall Ch4–5（$\mathrm{SU}(2)$/$\mathrm{SU}(3)$ 的矩阵实现）——FH Ch9–10 的计算版
3. **本书核心路线**：Ch1–3（有限群，甜区）→ Ch9（$\mathfrak{sl}(2)$，原型）→ Ch10（$\mathfrak{sl}(3)$，根系首登场）→ Ch14（Cartan 分类）→ Ch15（Weyl 公式，巅峰）
4. **可选深入**：附录 Schur 函数 + Ch17 Borel-Weil（几何表示论入口）
5. **验证工具**：配合 `sympy` 计算特征表、`matplotlib` 画根系/权图——见文末实操建议

---

## §11 自测答案要点（供核对）

1. **Ch1** $S_3$ 标准表示：$(12)$ 的迹 $=0$，$(123)$ 的迹 $=\omega+\omega^2=-1$。Maschke：$V=\mathbf{2}\oplus\mathbf{1}^{\oplus 0}$ 或 $V=\mathbf{2}\oplus\boldsymbol{\varepsilon}$（取决于构造）。
2. **Ch2** 行正交验证：$\langle\chi_3,\chi_3\rangle=\frac{1}{6}(1\cdot4+3\cdot0+2\cdot1)=\frac{6}{6}=1$。列正交：$\sum_i\overline{\chi_i(e)}\chi_i((12))=1\cdot1+1\cdot(-1)+2\cdot0=0\ne\frac{6}{1}$（需在同类内才非零）。$\sum d_i^2=1+1+4=6=|S_3|$。
3. **Ch3** $\mathrm{Res}_{A_3}^{S_3}\chi_{\mathrm{std}}=(-1,-1)=\chi_\omega+\chi_{\omega^2}$（在 $\mathbb{Z}/3$ 上 $\omega+\omega^2=-1$）。$\mathrm{Ind}_{A_3}^{S_3}\chi_\omega$ 的维度 $=[S_3:A_3]\cdot1=2=\dim\chi_{\mathrm{std}}$；Frobenius 互反验证包含一次。
4. **Ch9** $V_1\otimes V_1=V_2\oplus V_0$：维度 $4=3+1$。$V_2$ 的权 $2,0,-2$（自旋 $1$），$V_0$ 权 $0$（自旋 $0$）。
5. **Ch10** $\mathbf{3}\otimes\bar{\mathbf{3}}=\Gamma_{1,1}\oplus\Gamma_{0,0}=\mathbf{8}\oplus\mathbf{1}$。$\dim\Gamma_{1,1}=\frac{1}{2}\cdot2\cdot2\cdot4=8$，$\dim\Gamma_{0,0}=1$，总计 $9=3\times3$。
6. **Ch11** $\mathfrak{b}$ 的 2 维表示：$H=\mathrm{diag}(1,0)$，$E=\begin{pmatrix}0&1\\0&0\end{pmatrix}$。不变子空间 $\langle e_1\rangle$ 存在，但不存在 $E$-不变补（$E$ 把任何含 $e_2$ 的向量映到 $e_1$ 方向），故不可分解。
7. **Ch14** $A_2$：两节点单连（$\mathfrak{sl}(3)$）；$B_2$：两节点双连（$\mathfrak{so}(5)$）；$G_2$：两节点三重连（箭头指向短根）。$G_2$ 根长比 $\sqrt{3}:1$，夹角 $150°$。
8. **Ch15** $\Gamma_{1,1}$ 维数 $=8$：$\frac{2}{1}\cdot\frac{2}{1}\cdot\frac{4}{2}=8$（正根 $\alpha_1,\alpha_2,\alpha_1+\alpha_2$，$\lambda+\rho=2\omega_1+2\omega_2$）。
9. **Ch16** $S_3$ 三不可约 FS 均 $=1$（实型）。$\mathrm{SU}(2)$ 的 $V_1$（2 维）：$\mathrm{FS}=-1$（四元数型），因 $\mathrm{SU}(2)\cong\mathrm{Sp}(1)$（单位四元数），2 维表示是四元数作用。
10. **Ch17** $\mathrm{SL}(2)$：$G/B=\mathbb{CP}^1$，$\mathcal{O}(n)$ 截面 $=$ $n$ 次齐次多项式 $=$ $n+1$ 维 $=$ $V_n$。
11. **附录** $\mathbf{3}\otimes\mathbf{3}=\Gamma_{2,0}\oplus\Gamma_{0,1}=\mathbf{6}\oplus\bar{\mathbf{3}}$。$\dim\Gamma_{2,0}=\frac{1}{2}\cdot3\cdot1\cdot4=6$。

---

> **精读纪律**：本文为快速逐章精读，每章取 1 个飞腾锚点 + 1 个关键定理 + 1 道自测题。深入计算与完整证明请回原书。🟢 = 事实锚点（可直接引用），🟡 = 类比锚点（仅供直觉，不可引用于严格证明）。
>
> **实操验证建议**（Python/SymPy）：
> - `numpy.kron` 实现 $V_1\otimes V_1$ 的 Kronecker 积 → 验证 Ch1 张量积与 Ch9 Clebsch-Gordan 分解
> - 构造 $S_3$ 特征表矩阵 → 验证 Ch2 行/列正交关系 $\langle\chi_i,\chi_j\rangle=\delta_{ij}$
> - `sympy` 计算 $\mathfrak{sl}(2)$ 的 $H$ 在 $V_n$ 上的对角矩阵 → 验证 Ch9 权值 $n,n-2,\ldots,-n$
> - 画 $A_2$ 根系正六边形（matplotlib）→ 可视化 Ch10 权格点与 Weyl 室
> - 实现 Weyl 维数公式的连乘 → 验证 Ch15 $\Gamma_{a,b}$ 维数公式
