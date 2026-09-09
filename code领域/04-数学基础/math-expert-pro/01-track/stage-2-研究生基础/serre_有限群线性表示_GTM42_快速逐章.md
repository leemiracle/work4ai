# Serre《有限群的线性表示》(GTM42) · 快速逐章精读

> 基于原书：Linear Representations of Finite Groups (GTM42, J.-P. Serre, 1977, 郝鈃新中译) / 读于：2026-07-02
> 定位：**表示论最薄最锋利的经典**，Serre（Fields Medal 1954 史上最年轻得主 + Abel Prize 2003 首位得主）用极简公理化笔法给出有限群表示的全部核心。全程无可挑剔。
> 本文为**快速逐章精读**，每章 1 个飞腾锚点 + 1 个关键定理 + 1 道自测题。

---

## §0 引言：Serre 是什么，为什么读它

Serre《Linear Representations of Finite Groups》(GTM 42) 是表示论领域**最薄、最锋利**的经典。它由两部法语讲义合并而成（Part I–II 初等+特征理论，Part III 诱导表示引论），全书不到 180 页，却完整覆盖有限群线性表示的核心：从 $\rho:G\to\mathrm{GL}(V)$ 的定义出发，经 Maschke 完全可约、Schur 引理、特征的正交关系，抵达 $\sum d_i^2=|G|$、不可约个数 = 共轭类个数，最后用特征理论证明 **Burnside $p^aq^b$ 定理**与 **Frobenius 群**的存在性。Serre 的笔法是**公理化极简**——每个定理只给「最小充分」的假设，证明一步不多、一字不废，读它像看一把手术刀。

读它的核心理由：当你在 Fulton-Harris（GTM129，例子驱动、几何直觉）里「看见」表示之后，Serre 会用**最短路径**把同一理论重新拧紧。Part I 的 Ch1–4 给出一般理论（含紧群 $\mathrm{SU}(2)$、$\mathrm{SO}(3)$）；Part II 的 Ch5–7 把特征理论做到底——正交关系、不可约个数、特征表可逆；Part III 的 Ch8–12 是专题，**对称群 $S_n$、交错群 $A_n$、诱导表示、Mackey 准则、应用**。Serre 最令人叹服之处：他证明 $\sum d_i^2=|G|$ 只用正则表示 $\mathbb{C}[G]$ 的一次分解；他证 Burnside 定理只用正交关系的一道列求和——**每一步都是「杀鸡用牛刀」的极致精准**。与 Humphreys GTM9（李代数结构）、Hall GTM222（李群+物理）形成互补：那两本讲连续对称，Serre 讲离散对称的最锋利版本。

| 书 | 风格 | 严格性 | 适合谁 |
|---|---|---|---|
| **Serre** GTM42 | 极简公理化，纯有限群+紧群 | ★★★★★ 每步无可挑剔 | 追求最短最锋利路径理解表示论 |
| **Fulton-Harris** GTM129 | 例子驱动，几何直觉，有限群+李代数双线 | ★★★★ 计算详尽 | 第一次学，想「看见」表示 |
| **Hall** GTM222 | 矩阵群+物理，李群入门 | ★★★★ 极友好 | 物理背景或从 $\mathrm{SU}(2)$ 入门 |
| **Isaacs**《Character Theory of Finite Groups》 | 纯特征理论，专著级深度 | ★★★★★ 专著 | 深入特征理论、做有限群研究 |

**建议路线**：Hall 热身（矩阵群+物理）→ Fulton-Harris 攻例子与几何（GTM129）→ **Serre 攻极简锋利（本书）** → Isaacs 攻特征理论的专著深度。

**零基础工程师阅读建议**：Ch1–2 是甜区——只需线性代数与群论基础，务必手算 $S_3$ 特征表（三行三列，十分钟）。Ch3 诱导表示 + Frobenius 互反是全书枢纽。Ch7（$\sum d_i^2=|G|$、不可约个数 = 共轭类）是「群指纹」理论。Ch12 的 Burnside 定理是特征理论的**收官秀**——三行证明干翻一个困扰群论界六十年的难题。全书精读约 30–50 小时（每周 10–20h，2–4 周）——它薄，但每页都值得反复读。

**全书的两大「顿悟时刻」**：第一次顿悟在 Ch2——发现「迹」$\chi_\rho(g)=\mathrm{Tr}(\rho(g))$ 这个一维摘要居然**无损压缩**了表示的全部不可约信息。第二次顿悟在 Ch12——发现特征的正交关系可以直接**证明群论定理**（Burnside $p^aq^b$ 可解），表示论不再是「工具」而成了「证明的引擎」。

---

## §1 全书 12 章骨架一览（3 部分 · 飞腾锚点分布）

| 部分 | 章 | 标题 | 核心概念 | 飞腾锚点 |
|---|---|---|---|---|
| **Part I** | 1 | 一般理论 | 线性表示 $\rho$，Maschke，群代数 $\mathbb{C}[G]$ | **matmul ⭐表示矩阵** |
| 一般理论 | 2 | 特征理论 | 特征 $\chi_\rho=\mathrm{Tr}$，正交关系 | **Schmidt ⭐特征L2正交核心** |
| | 3 | 子群·积·诱导 | 诱导 $\mathrm{Ind}_H^G$，Frobenius 互反 | **UDOT ⭐特征求和** |
| | 4 | 紧群 | Haar 测度，Peter-Weyl，$\mathrm{SU}(2)$ | **Iron Law <2% ⭐正合** |
| **Part II** | 5 | 特征 | 等型分解，投影，矩阵系数 | **GEMM ⭐特征表** |
| 特征理论 | 6 | 正交关系 | 行/列正交，中心 idempotent，判等 | **分支预测 ⭐Schur** |
| | 7 | 不可约个数 | $k$=共轭类，$\sum d_i^2=|G|$ | **TLB 诱导** |
| **Part III** | 8 | 对称群 $S_n$ | Young 图，Specht 模，Frobenius 公式 | **FP16** |
| 专题 | 9 | 交错群 $A_n$ | 限制 $\mathrm{Res}$，自共轭分拆分裂 | **GEMM ⭐特征表** |
| | 10 | 诱导表示 | 诱导的两种构造，Artin/Brauer 定理 | **matmul ⭐表示矩阵** |
| | 11 | Mackey 准则 | 双陪集，Mackey 不可约判据 | **分支预测 ⭐Schur** |
| | 12 | 应用 | Burnside $p^aq^b$，Frobenius 群 | **Iron Law <2% ⭐正合** |

---

### 第 1 章 · Generalities on Linear Representations（表示的一般理论）

- **核心**：群的「线性表示」是同态 $\rho: G \to \mathrm{GL}(V)$，把每个群元变成可逆矩阵。**不可约**表示（无真不变子空间）是表示的「原子」。**完全可约**：$V=W\oplus W'$，其中 $W,W'$ 均为子表示。群代数 $\mathbb{C}[G]$（基为群元、乘法为群乘法）承载**左正则表示**（$G$ 左平移作用），其不可约分解 $\mathbb{C}[G]\cong\bigoplus_i V_i^{\oplus d_i}$（$d_i=\dim V_i$）给出全书最常用的恒等式 $\sum_i d_i^2=|G|$。
- **飞腾锚点**：**matmul ⭐表示矩阵** —— 表示 $\rho(g)$ 本质是给每个群元赋一个可逆矩阵；直和 = 分块对角，张量积 = Kronecker 积 $\rho_1(g)\otimes\rho_2(g)$，全是密集矩阵操作。
  - 🟢事实：Maschke 的「平均投影」$P=\frac{1}{|G|}\sum_{g\in G}\rho(g)\,P_0\,\rho(g)^{-1}$ 数值上就是矩阵群上的平均化；GPU tensor core 做 matmul 比标量快 15×。
  - 🟡类比：正则表示 $\mathbb{C}[G]$ 中每个群元对应一个置换矩阵（每行每列恰一个 1），是稀疏 0-1 矩阵——群乘法表即矩阵乘法。
- **关键定理**：**Maschke 定理**：设 $G$ 有限群，$\rho:G\to\mathrm{GL}(V)$ 为 $\mathbb{C}$ 上表示，则 $V$ 完全可约。证：对子表示 $W\subset V$ 取任意投影 $P_0:V\twoheadrightarrow W$，令 $P=\frac{1}{|G|}\sum_{g\in G}\rho(g)\,P_0\,\rho(g)^{-1}$，则 $P$ 与 $\rho$ 交换，$\ker P$ 给出 $G$-不变补，$V=W\oplus\ker P$。
- **自测**：写出 $S_3$ 的全部不可约表示（平凡 $\mathbf{1}$、符号 $\boldsymbol\varepsilon$、2 维标准 $\mathbf{2}$），验证 $\sum d_i^2=1+1+4=6=|S_3|$。提示：标准表示取 $V=\{(x_1,x_2,x_3)\in\mathbb{C}^3:x_1+x_2+x_3=0\}$。

---

### 第 2 章 · Character Theory（特征理论）

- **核心**：表示 $\rho$ 的**特征** $\chi_\rho(g)=\mathrm{Tr}(\rho(g))$ 是**类函数**（共轭类上取常数），不依赖基的选择。把「一组矩阵」压缩成「每个共轭类一个数」，同时**保留不可约分解的全部信息**——这是表示论最神奇的「无损压缩」。**Schur 引理**：不可约表示间的交结算子(intertwiner) $T:V_i\to V_j$（满足 $T\rho_i=\rho_jT$）当 $i=j$ 为标量 $\lambda\mathrm{Id}$，当 $i\ne j$ 为零。由此推出**正交关系** $\langle\chi_i,\chi_j\rangle_G=\delta_{ij}$。特征是整个后续理论的万能钥匙。
- **飞腾锚点**：**Schmidt ⭐特征L2正交核心** —— 特征内积 $\langle\chi,\psi\rangle=\frac{1}{|G|}\sum_g\overline{\chi(g)}\psi(g)$ 就是有限群上的 $L^2$ 内积，与 Gram-Schmidt 正交化完全同构。
  - 🟢事实：不可约特征是类函数空间的正交基；重数公式 $a_i=\langle\chi_V,\chi_i\rangle$ 给出第 $i$ 个不可约在 $V$ 中出现次数——这是「表示的 Fourier 分解」。投影算子 $P_i=\frac{d_i}{|G|}\sum_g\overline{\chi_i(g)}\rho(g)$ 把 $V$ 投到第 $i$ 等型分量。
  - 🟡类比：Schur 引理保证不同不可约「通道」间无串扰——这正是 OFDM（正交频分复用）中子载波正交性的数学版本。
- **关键定理**：**特征的正交关系**：行正交 $\frac{1}{|G|}\sum_{g\in G}\overline{\chi_i(g)}\,\chi_j(g)=\delta_{ij}$；列正交 $\sum_{i=1}^{k}\overline{\chi_i(g)}\,\chi_i(h)=\frac{|G|}{|C_G(g)|}\delta_{g\sim h}$（$C_G(g)$ 为中心化子）。
- **自测**：写出 $S_3$ 特征表（$e$/(12)/(123) 三列），验证 $\langle\chi_3,\chi_3\rangle=\frac{1}{6}(1\cdot4+3\cdot0+2\cdot1)=1$，并用列正交验证 $\sum_i\overline{\chi_i((12))}\chi_i((123))=1-1+0=0$。

**$S_3$ 特征表**（表示论的「Hello World」，务必手算）：

| | $e$ (1个) | $(12)$ (3个) | $(123)$ (2个) |
|---|---|---|---|
| 平凡 $\chi_1$ | $1$ | $1$ | $1$ |
| 符号 $\chi_2$ | $1$ | $-1$ | $1$ |
| 标准 $\chi_3$ | $2$ | $0$ | $-1$ |

行正交：$\langle\chi_3,\chi_3\rangle=\frac16(1\cdot4+3\cdot0+2\cdot1)=1$；列正交第2/3列：$1\cdot1+(-1)\cdot1+0\cdot(-1)=0$。$\sum d_i^2=1+1+4=6=|S_3|$——特征表是「群的指纹」。

---

### 第 3 章 · Subgroups, Products, Induced Representations（子群、积、诱导表示）

- **核心**：Abel 群的不可约都是 1 维（可同时对角化）；直积 $G_1\times G_2$ 的不可约 = $\rho_1\boxtimes\rho_2$（外积）。**诱导表示** $\mathrm{Ind}_H^G(W)$：Serre 用函数观点——$W$-值函数 $f:G\to W$ 满足 $f(hg)=\rho_W(h)f(g)$，$G$ 右平移作用，维度 $=[G:H]\dim W$。**Frobenius 互反律**：$\langle\mathrm{Ind}\,\chi_W,\psi\rangle_G=\langle\chi_W,\mathrm{Res}\,\psi\rangle_H$——诱导与限制互为伴随，是表示论的核心对偶性，全书反复使用。
- **飞腾锚点**：**UDOT ⭐特征求和** —— 诱导特征公式 $\chi_{\mathrm{Ind}}(g)=\frac{1}{|H|}\sum_{\substack{x\in G\\xgx^{-1}\in H}}\chi_W(xgx^{-1})$ 本质是群上的大规模点积累加。
  - 🟢事实：互反律验证需大量 $\sum_g\overline{\chi(g)}\psi(g)$ 内积；UDOT 点积加速器天然映射「群上求和」，$|G|$ 大时 16.9× 加速适合批量特征内积。
  - 🟡类比：$\mathrm{Ind}$ 把子群信号「上采样」到全群，$\mathrm{Res}$ 反之「下采样」——信号处理的采样率转换。
- **关键定理**：**Frobenius 互反律**：$\langle\mathrm{Ind}_H^G\chi_W,\psi\rangle_G=\langle\chi_W,\mathrm{Res}_H^G\psi\rangle_H$。诱导 $\mathrm{Ind}$ 与限制 $\mathrm{Res}$ 是共轭对（伴随算子）。
- **自测**：设 $A_3\cong\mathbb{Z}/3$，$\chi_\omega$ 为其不可约（$\omega=e^{2\pi i/3}$）。验证 $\mathrm{Ind}_{A_3}^{S_3}\chi_\omega=\chi_{\mathrm{std}}$（维度 $2=2\times1$），并用互反律证 $\langle\mathrm{Ind}\chi_\omega,\chi_{\mathrm{std}}\rangle=\langle\chi_\omega,\mathrm{Res}\chi_{\mathrm{std}}\rangle=1$。

---

### 第 4 章 · Compact Groups（紧群）

- **核心**：从有限群跨入**拓扑群**。**Haar 测度**：紧群 $G$ 上唯一（归一化）的左不变概率测度 $dg$，使 $\int_G f(gx)\,dg=\int_G f(g)\,dg$。有限群的 Haar = 计数测度 $\frac{1}{|G|}\sum$。Maschke 的「平均」升级为 Haar 积分 $\int_G \rho(g)A\rho(g)^{-1}\,dg$——紧群的表示同样完全可约。**Peter-Weyl 定理**：不可约的矩阵系数 $\sqrt{d_i}\rho_i(g)_{kl}$ 构成 $L^2(G)$ 正交基，$G=S^1$ 退化为经典 Fourier 级数。本章给出 $\mathrm{SU}(2)$、$\mathrm{SO}(3)$ 的表示（$n+1$ 维 $V_n$，自旋 $j=n/2$），是连续对称的入门。
- **飞腾锚点**：**Iron Law <2% ⭐正合** —— Haar 积分的「平均投影」给出精确的 $G$-不变补，完全可约 = 矩阵精确分块对角化，残余误差可控（酉技巧）。
  - 🟢事实：$\mathrm{SU}(2)$ 的每个表示配 $G$-不变 Hermit 内积（Haar 平均得到），故酉表示，正交补给出分解——Iron Law 般的「精确正合」。注意：无限维表示不再完全可约，酉技巧仅限有限维。
  - 🟡类比：Peter-Weyl 把有限群的「特征表正交」升级为紧群的「连续 Fourier」，正交性是同一结构的连续极限——$S^1$ 退化为 $\{e^{in\theta}\}$。
- **关键定理**：**Peter-Weyl 定理**：设 $G$ 紧致群，$\{\rho_i\}$ 遍历不可约，则矩阵系数 $\sqrt{d_i}\rho_i(g)_{kl}$ 构成 $L^2(G,dg)$ 的正交基。有限群特征正交(Ch2) 是其特例。
- **$\mathrm{SU}(2)$ 表示一览**：不可约 $V_n$（$n=0,1,2,\ldots$），维度 $n+1$，权为 $n,n-2,\ldots,-n$（自旋 $j=n/2$，磁量子数 $m=-j,\ldots,j$）。$V_1=\mathbb{C}^2$（自旋 $\frac12$，电子），$V_2$（自旋 $1$，三维旋转），$V_3$（自旋 $\frac32$）。$\mathrm{SU}(2)\cong S^3$（单位四元数），是 $\mathrm{SO}(3)$ 的通用双重覆盖。
- **自测**：为什么 $\mathrm{SU}(2)$ 的不可约都是奇数维 $2j+1$（$j=0,\frac12,1,\ldots$），而 $\mathrm{SO}(3)$ 只取整数 $j$？（$\mathrm{SU}(2)\to\mathrm{SO}(3)$ 是双重覆盖，$\ker=\{\pm I\}$，$\mathrm{SO}(3)$ 只保留 $j\in\mathbb{Z}$ 的表示，$j$ 半整数时 $-I$ 作用为 $-1$ 非平凡。）

---

### 第 5 章 · Characters（特征——深入）

- **核心**：Part II 重新深入特征，把 Part I 的骨架拧到最紧。**等型分量**(isotypic component)：$V$ 中所有同构于 $V_i$ 的子表示之和 $V(i)=V_i^{\oplus a_i}$，$V=\bigoplus_i V(i)$。**投影算子** $p_i=\frac{d_i}{|G|}\sum_g\overline{\chi_i(g)}\rho(g)$ 把 $V$ 投影到第 $i$ 等型分量，是「表示的 Fourier 滤波器」。**中心 idempotent** $e_i=\frac{d_i}{|G|}\sum_g\overline{\chi_i(g)}g\in\mathbb{C}[G]$ 满足 $e_i^2=e_i$，$e_ie_j=0$，$\sum e_i=1$——群代数的「谱分解」。**矩阵系数** $\rho_i(g)_{kl}$：表示论的「坐标函数」，是 Peter-Weyl 的离散版。
- **飞腾锚点**：**GEMM ⭐特征表** —— 等型分解 $V=\bigoplus V(i)$ 把任意表示排成块对角大矩阵，特征表是「基变换矩阵」，GEMM 高吞吐适合批量计算所有等型分量。
  - 🟢事实：中心 idempotent $e_i$ 的计算 = 把群代数元素 $\frac{d_i}{|G|}\sum\overline{\chi_i(g)}g$ 排成向量做矩阵乘；$p_i$ 投影是「滤波」到第 $i$ 不可约通道。
  - 🟡类比：$p_i$ = FFT 把信号分解到各谐波后取出某一频率分量；等型分解 = 表示的「频谱分解」。
- **关键定理**：**等型分解定理**：$V=\bigoplus_{i=1}^k V(i)$，$V(i)=p_iV$，重数 $a_i=\langle\chi_V,\chi_i\rangle=\dim V(i)/d_i$。投影 $p_i=\frac{d_i}{|G|}\sum_g\overline{\chi_i(g)}\rho(g)$ 与 $\rho$ 交换。
- **自测**：对正则表示 $\mathbb{C}[G]$，每个不可约 $V_i$ 出现几次？（$a_i=d_i$，因 $\langle\chi_{\mathrm{reg}},\chi_i\rangle=\chi_i(e)=d_i$，故 $\mathbb{C}[G]\cong\bigoplus V_i^{\oplus d_i}$，$\sum d_i^2=|G|$。）

---

### 第 6 章 · Orthogonality Relations（正交关系）

- **核心**：系统应用正交关系。**表示等价判定**：两个表示等价 $\Leftrightarrow$ 特征相同（$\chi_\rho=\chi_{\rho'}$）。这是「特征是群的指纹」的精确化——一维函数完全决定表示。**列正交**的威力：$\sum_i\chi_i(g)\overline{\chi_i(h)}=0$ 当 $g,h$ 不共轭，$=\frac{|G|}{|C(g)|}$ 当共轭。由此特征表是**可逆方阵**（行列非零），任意类函数可表为不可约特征的线性组合。Serre 在此给出**重数计算的统一公式**：$V$ 中 $V_i$ 的重数 $a_i=\langle\chi_V,\chi_i\rangle$，一次内积搞定。
- **飞腾锚点**：**分支预测 ⭐Schur** —— Schur 引理在每个交结算子处做一次「分支判断」：$i=j$ 走标量分支，$i\ne j$ 走零分支，准确率 100%（因表示严格不可约）。
  - 🟢事实：判等定理 $V\cong V'\Leftrightarrow\chi_V=\chi_{V'}$ 的证明逐项检查 Schur 分支，每个分支确定唯一——无可失配；正交基的唯一性由此保证。
  - 🟡类比：CPU 分支预测器在结构化数据（规整共轭类）上命中率高；Schur 引理的「分支」永不误判——表示论是「完美可预测」的系统。
- **关键定理**：**判等定理**：$\rho_1\cong\rho_2$ 当且仅当 $\chi_{\rho_1}=\chi_{\rho_2}$（作为类函数逐点相等）。推论：特征表的行线性无关，是不可约特征基，类函数空间维数 = 不可约个数。
- **自测**：$S_4$ 有 5 个共轭类（$e$、$(12)$、$(123)$、$(12)(34)$、$(1234)$），故有 5 个不可约。用 $\sum d_i^2=24$ 猜出维数 $(1,1,2,3,3)$，写出对应（平凡、符号、2 维来自 $S_4/V_4\cong S_3$、标准 3 维、符号$\otimes$标准）。

**$S_4$ 特征表**（$k=5$ 个共轭类 $\Leftrightarrow$ 5 个不可约，$\sum d_i^2=24$）：

| | $e$ (1) | $(12)$ (6) | $(12)(34)$ (3) | $(123)$ (8) | $(1234)$ (6) |
|---|---|---|---|---|---|
| 平凡 $\chi_1$ | $1$ | $1$ | $1$ | $1$ | $1$ |
| 符号 $\chi_2$ | $1$ | $-1$ | $1$ | $1$ | $-1$ |
| 2 维 $\chi_3$ | $2$ | $0$ | $2$ | $-1$ | $0$ |
| 标准 $\chi_4$ | $3$ | $1$ | $-1$ | $0$ | $-1$ |
| 符号$\otimes$标准 $\chi_5$ | $3$ | $-1$ | $-1$ | $0$ | $1$ |

验证 $\sum d_i^2=1+1+4+9+9=24=|S_4|$。2 维 $\chi_3$ 来自商 $S_4/V_4\cong S_3$ 的标准表示；$\chi_5=\chi_2\cdot\chi_4$。

---

### 第 7 章 · The Number of Irreducible Representations（不可约表示的个数）

- **核心**：本章是「群指纹」理论的**收官**。由行正交，不可约特征 $\{\chi_i\}$ 在类函数空间 $\mathcal{C}(G)$（维数 = 共轭类个数 $r$）中线性无关，故不可约个数 $k\le r$。再由列正交可证 $\{\chi_i\}$ 实际**张满** $\mathcal{C}(G)$，故 $k=r$。合起来：**不可约表示的个数 = 共轭类的个数**，且 $\sum d_i^2=|G|$（来自正则表示分解）。特征表是 $r\times r$ 可逆方阵——群的「完整指纹」。Serre 在此还给出**生成函数**观点：特征表作为类函数空间的基变换矩阵，其逆矩阵编码群的共轭类结构。
- **飞腾锚点**：**TLB 诱导** —— 共轭类结构由群的「局部对称」（中心化子 $C_G(g)$）决定，类函数空间的热路径是共轭类，TLB 局部性高、命中率高。
  - 🟢事实：$k=r$ 的证明中，列正交 $\sum_i\chi_i(g)\overline{\chi_i(h)}\propto\delta_{g\sim h}$ 表明特征表行张满——每个类函数可表为 $\sum c_i\chi_i$，访问模式局部。
  - 🟡类比：共轭类像内存页，中心化子大小 = 页内局部性；特征表可逆 = 页表完备，每个类函数都能「寻址」无缺页。
- **关键定理**：**不可约个数定理**：有限群 $G$ 的不可约复表示个数 $k$ 等于 $G$ 的共轭类个数 $r$；且 $\sum_{i=1}^k d_i^2=|G|$（$d_i=\dim V_i$）。特征表为 $r\times r$ 可逆方阵。
- **自测**：四元数群 $Q_8=\{\pm1,\pm i,\pm j,\pm k\}$ 有 5 个共轭类（$\{1\},\{-1\},\{\pm i\},\{\pm j\},\{\pm k\}$），故 5 个不可约。由 $\sum d_i^2=8$ 得维数 $(1,1,1,1,2)$。那个 2 维不可约是什么？（$Q_8\to\mathrm{SU}(2)$ 的自然 2 维表示，$i,j,k\mapsto$ Pauli 矩阵。）注意：$Q_8$ 的换位子群 $[Q_8,Q_8]=\{\pm1\}$，商 $Q_8/\{\pm1\}\cong(\mathbb{Z}/2)^2$，四个 1 维表示均来自此商——故「非交换群的 1 维表示 = 交换化的表示」。

---

### 第 8 章 · Representations of Symmetric Groups $S_n$（对称群的表示）

- **核心**：$S_n$ 的不可约与 $n$ 的**分拆** $\lambda\vdash n$ 一一对应（$n$ 的分拆数 $p(n)$ = 不可约个数）。**Young 图**：$\lambda=(\lambda_1\ge\cdots\ge\lambda_k)$ 画成行长度递减的格点。**tabloid**（行等价类）张成置换模 $M^\lambda$。**Specht 模** $S^\lambda\subseteq M^\lambda$ 由 polytabloid 生成，$S^\lambda$ 恰为不可约。$S_4$ 的 5 个分拆 $(4),(3{,}1),(2{,}2),(2{,}1{,}1),(1^4)$ 对应 5 个不可约，维数 $(1,3,2,3,1)$。**Frobenius 特征公式**给出特征表的系数——把特征表与对称函数（Schur 函数）联系起来。
- **飞腾锚点**：**FP16** —— Young 图的填充数(tabloid)枚举是组合整数计数，权值为精确整数，FP16 的 3.81× 吞吐适合大批量组合枚举。
  - 🟢事实：Specht 模的 polytabloid 是整数系数线性组合，$\sum d_\lambda^2=n!$，所有数据精确整数——低精度计算无误差。
  - 🟡类比：分拆 $\lambda\vdash n$ 的计数是整数划分问题，类似背包 DP，可用位运算/低精度加速；维数由 hook-length 公式 $d_\lambda=n!/\prod\mathrm{hook}$ 给出。
- **关键定理**：**$S_n$ 不可约分类定理**：$S_n$ 的不可约复表示与分拆 $\lambda\vdash n$ 一一对应，由 Specht 模 $S^\lambda$ 实现。$\sum_{\lambda\vdash n}(\dim S^\lambda)^2=n!$。
- **自测**：列出 $S_4$ 的 5 个 Young 图，用 hook-length 公式标出各 Specht 模维数 $(1,3,2,3,1)$，验证 $\sum=1+9+4+9+1=24=4!$。

**$S_4$ 的 5 个 Young 图与 Specht 模维数**（hook-length 公式 $d_\lambda=n!/\prod\mathrm{hook}$）：

| 分拆 $\lambda$ | Young 图 | hook 积 | $\dim S^\lambda=d_\lambda$ |
|---|---|---|---|
| $(4)$ | $\square\square\square\square$ | $4\cdot3\cdot2\cdot1=24$ | $1$（平凡） |
| $(3{,}1)$ | 3+1 行 | $4\cdot2\cdot1\cdot1=8$ | $3$（标准） |
| $(2{,}2)$ | $2\times2$ 方 | $3\cdot2\cdot2\cdot1=12$ | $2$（自共轭） |
| $(2{,}1{,}1)$ | 2+1+1 行 | $4\cdot2\cdot1\cdot1=8$ | $3$（符号$\otimes$标准） |
| $(1^4)$ | 单列 4 格 | $4\cdot3\cdot2\cdot1=24$ | $1$（符号） |

验证 $\sum d_\lambda^2=1+9+4+9+1=24=4!$。$(2{,}2)$ 自共轭（转置 = 自身），限制到 $A_4$ 分裂。

---

### 第 9 章 · Representations of Alternating Groups $A_n$（交错群的表示）

- **核心**：由 $S_n$ 的表示限制到 $A_n$（指标 2 子群）。这是 **Clifford 理论**的最简特例：$\mathrm{Res}_{A_n}^{S_n}S^\lambda$ 要么保持不可约（一般情况），要么**分裂为两个等维不可约**（当 $\lambda$ 是**自共轭**(self-conjugate) 分拆，即 Young 图关于主对角线对称时）。自共轭分拆数 = 分裂数。由此从 $S_n$ 特征表「读出」$A_n$ 特征表：非自共轭分拆两两合并行（$\lambda$ 与 $\lambda'$ 配对），自共轭分拆一行为二。共轭类的分裂也有规则：cycle type 全奇长度的 $S_n$-类在 $A_n$ 中一分为二。
- **飞腾锚点**：**GEMM ⭐特征表** —— $A_n$ 特征表是 $S_n$ 特征表的「子表变换」：合并行 + 分裂行 + 分裂列，本质是矩阵的行列操作，GEMM 高吞吐。
  - 🟢事实：$S_n$ 的共轭类限制到 $A_n$ 可能一分为二（当 cycle type 全奇长度时），分裂规则精确——整数矩阵运算，低误差。
  - 🟡类比：限制 $\mathrm{Res}$ = 对特征表做行/列重排，类似矩阵的 block partition；自共轭分拆的分裂 = 一个矩阵行「裂变」为两行。
- **关键定理**：**自共轭分拆分裂定理**：$\lambda\vdash n$ 自共轭（$\lambda=\lambda^T$）$\Leftrightarrow$ $\mathrm{Res}_{A_n}^{S_n}S^\lambda$ 分裂为两个不等价不可约（各 $\frac12\dim S^\lambda$ 维）；否则 $\mathrm{Res}$ 保持不可约。
- **自测**：$A_4$ 有 4 个共轭类，故 4 个不可约。$S_4$ 的 5 个不可约限制到 $A_4$：平凡+符号合并、标准+符号$\otimes$标准合并（$A_4$ 上符号平凡），2 维 $(2{,}2)$ 自共轭（$2\times2$ 方图）分裂为两个 1 维——给 $A_4$ 的 $(1,1,1,3)$ 维数，$\sum=1+1+1+9=12=|A_4|$。

---

### 第 10 章 · Induced Representations（诱导表示——Part III 引论）

- **核心**：Part III 深入诱导表示的构造与定理。Serre 给出诱导的**两种构造**：(i) 函数观点 $f:G\to W$，$f(hg)=h\cdot f(g)$，$G$ 右平移；(ii) 模观点 $\mathrm{Ind}_H^G W=\mathbb{C}[G]\otimes_{\mathbb{C}[H]}W$。两者等价。**Frobenius 互反**贯穿全程。两大里程碑定理：**Artin 定理**——每个特征是**循环子群**诱导特征的有理系数线性组合（$\chi=\sum a_i\mathrm{Ind}_{C_i}^G\varphi_i$，$a_i\in\mathbb{Q}$）；**Brauer 定理**——每个特征是**初等子群**（循环群 $\times$ $p$-群之积）诱导特征的**整数**线性组合。Brauer 定理是特征理论的基石，它把任意表示「分解」为可控的小群诱导。
- **飞腾锚点**：**matmul ⭐表示矩阵** —— 诱导表示 $\mathrm{Ind}_H^G W$ 的矩阵是 $W$ 矩阵在陪集上的「分块扩张」，本质是 Kronecker 式的矩阵扩充，密集矩阵操作。
  - 🟢事实：$\mathbb{C}[G]\otimes_{\mathbb{C}[H]}W$ 的矩阵实现 = 把 $W$ 的 $\dim W\times\dim W$ 矩阵扩张到 $[G:H]\dim W$ 维，分块结构清晰。
  - 🟡类比：诱导 = 数据增广，从小群 $H$ 的表示「升格」到大群 $G$，类似用小数据集通过对称性增广到大集。
- **关键定理**：**Brauer 定理（特征诱导定理）**：$G$ 的每个特征是形如 $\mathrm{Ind}_E^G\varphi$ 的特征在 $E$ 取遍**初等子群**（$E=C\times P$，$C$ 循环、$P$ 为 $p$-群）、$\varphi$ 取遍 $E$ 的一维特征时的 $\mathbb{Z}$-线性组合。
- **自测**：用 Artin 定理解释——为什么 $S_3$ 的 2 维标准特征可写为循环群诱导特征的 $\mathbb{Q}$-组合？（$\chi_{\mathrm{std}}=\mathrm{Ind}_{\langle(123)\rangle}^{S_3}\chi_\omega$，单一循环群诱导即可，系数为整数 1——比 Artin 更强。）

> **Artin vs Brauder 对比**：Artin 定理用循环子群 + 有理系数（弱：系数是分数）；Brauer 定理用初等子群 + 整数系数（强：系数是整数）。Brauer 的「初等子群」= 循环群 $\times$ $p$-群的直积，覆盖面更广。Brauer 定理的整数性是关键——它保证特征表的「算术无亏损」，是 Brauer 特征块理论(Brauer blocks)的起点。

---

### 第 11 章 · Mackey's Criterion（Mackey 准则）

- **核心**：Mackey 的核心问题是：**何时诱导表示不可约？** 给出干净的判据。设 $H\le G$，$\theta$ 为 $H$ 的不可约表示。对 $s\in G$，定义共轭表示 $\theta^s$（在 $s^{-1}Hs\cap H$ 上）。**Mackey 不可约判据**：$\mathrm{Ind}_H^G\theta$ 不可约 $\Leftrightarrow$ (i) $\theta$ 不可约；(ii) 对每个 $s\in G\setminus H$，$\mathrm{Res}_{H\cap sHs^{-1}}\theta$ 与 $\mathrm{Res}_{H\cap sHs^{-1}}\theta^s$ **不相交**（无公共不可约）。核心工具是**双陪集**(double coset) $H\backslash G/H$ 的分解：$G=\bigsqcup Hs_iH$，只需检查有限个代表元 $s_i$。这是 Clifford 理论与 Mackey 机器的起点。
- **飞腾锚点**：**分支预测 ⭐Schur** —— Mackey 判据对每个双陪集代表元 $s$ 做一次「分支判断」：限制表示是否相交？相交则 $\mathrm{Ind}$ 可约，不相交则继续——结构化判断，命中率高。
  - 🟢事实：双陪集分解 $G=\bigsqcup HsH$ 把 Mackey 检查化为有限次交算，每次检查 $\langle\mathrm{Res}\,\theta,\mathrm{Res}\,\theta^s\rangle_{H\cap sHs^{-1}}=0$，精确可判。
  - 🟡类比：双陪集 = 分支树节点，每个代表元 $s$ 是一个 if-else；判据 = 全部分支都「不相交」才通过（短路求值的 AND）。
- **关键定理**：**Mackey 不可约判据**：设 $H\le G$，$\theta$ 为 $H$ 不可约表示。$\mathrm{Ind}_H^G\theta$ 不可约 $\Leftrightarrow$ 对每个 $s\in G\setminus H$，$\mathrm{Res}_{H\cap sHs^{-1}}\theta$ 与 $\mathrm{Res}_{H\cap sHs^{-1}}\theta^s$ 无公共不可约分量。
- **自测**：设 $G=S_3$，$H=\langle(12)\rangle\cong\mathbb{Z}/2$，$\theta$ 为 $H$ 的非平凡（符号）表示。$\mathrm{Ind}_H^G\theta$ 是否不可约？（算特征 $\chi(e)=3,\chi(12)=1,\chi(123)=0$，$\langle\chi,\chi\rangle=\frac16(9+3\cdot1+0)=2\ne1$，故可约 $=\chi_{\mathrm{std}}\oplus\boldsymbol\varepsilon$，维 $3=2+1$。Mackey 检查 $s=(123)$：$H\cap sHs^{-1}=\{e\}$，但 $(13)$ 亦为代表元，须全查。）

---

### 第 12 章 · Applications（应用）

- **核心**：特征理论的**收官秀**——用正交关系证明纯群论定理。**Burnside $p^aq^b$ 定理**：阶为 $p^aq^b$（$p,q$ 素数）的群必可解。证明只用列正交的一道求和与代数整数论：若 $G$ 非交换单群，取非中心元 $g$，其共轭类大小 $c=|G|/|C(g)|>1$ 整除 $|G|=p^aq^b$，推出某不可约特征使 $\chi_i(g)/d_i$ 为非有理代数整数，矛盾。**Frobenius 群定理**：若 $H\le G$ 满足 $H\cap gHg^{-1}=\{e\}$（$\forall g\notin H$），则 $N=(G\setminus\bigcup gHg^{-1})\cup\{e\}$ 是正规子群——纯特征理论证明，至今**无纯群论证明**。
- **飞腾锚点**：**Iron Law <2% ⭐正合** —— Burnside 定理的证明依赖代数整数的**精确算术**（$\chi(g)$ 是代数整数，$|C(g)|$ 整除 $|G|$），零容差——正合性即 Iron Law。
  - 🟢事实：$\chi_i(g)$ 是单位根之和（代数整数），$\frac{|C(g)|}{|G|}\frac{d_i}{\chi_i(g)}$ 经列正交也是代数整数，逐项精确——任何近似都会摧毁证明。
  - 🟡类比：特征理论的「应用」= 用调和分析工具（正交、代数整数）解决纯代数问题，类似用 Fourier 分析证明数论定理（如解析数论）。
- **关键定理**：**Burnside $p^aq^b$ 定理**：若 $|G|=p^aq^b$（$p,q$ 素数），则 $G$ 可解。证：设 $G$ 非交换单，取非中心元 $g$，共轭类 $C$ 大小 $c>1$ 含素因子 $p$；由列正交 $\sum_i d_i\chi_i(g)=0$，存在 $i\ge1$ 使 $\chi_i(g)/d_i$ 非有理，但 $\frac{c\cdot\chi_i(g)}{d_i}$ 是代数整数且 $|c\chi_i(g)/d_i|<1$（取模估计），只能是 $0$，推出 $\chi_i(g)=0$ 与 $d_i\mid c$，最终矛盾。
- **自测**：用 Burnside 定理判断：阶为 12 的群是否可解？（$12=2^2\times3=p^2q$，是 $p^aq^b$ 型 $\Rightarrow$ 可解。验证 $A_4$（阶 12）确实可解：$V_4\triangleleft A_4$，$A_4/V_4\cong\mathbb{Z}/3$，$V_4\cong(\mathbb{Z}/2)^2$ 均交换，合成因子皆交换。）

**Burnside $p^aq^b$ 定理证明步骤分解**（特征理论「杀鸡用牛刀」的极致，Serre 三行证）：

| 步 | 论证 | 工具 |
|---|---|---|
| 1 | 反设 $G$ 非交换单群，取非中心元 $g\in G$ | 群论 |
| 2 | 共轭类 $C_g$ 大小 $c=\|G\|/\|C_G(g)\|>1$，$c\mid p^aq^b$ | 共轭类 |
| 3 | 列正交：$\sum_i d_i\chi_i(g)=0$（$i=1$ 为平凡，$d_1\chi_1(g)=1$） | 正交关系 |
| 4 | 存在 $i\ge2$ 使 $\chi_i(g)\ne0$ 且 $d_i\nmid c$，则 $\frac{c\cdot\chi_i(g)}{d_i}$ 是模 $<\sqrt{c}$ 的代数整数 | 代数整数论 |
| 5 | 唯一代数整数且绝对值 $<1$ 的是 $0$，故 $\chi_i(g)=0$，与 $d_i\mid c$ 矛盾 | 收尾 |

核心：第 4 步用「代数整数的绝对值下界」——纯算术。表示论到此戛然而止，余下是数论。

---

## §9 全书思想主线：Serre 三段式——一般 → 特征 → 专题

Serre 的全书是**三段式递进**，每段都比前一段更锋利。**Part I（Ch1–4，一般理论）**搭脚手架：线性表示 $\rho:G\to\mathrm{GL}(V)$ → Maschke 完全可约（平均投影）→ 群代数 $\mathbb{C}[G]$ → 紧群（Haar 测度、Peter-Weyl）。这一段的灵魂是**「平均化」**——无论是 $\frac1{|G|}\sum$（有限群）还是 $\int_G\,dg$（紧群），「平均」给出不变补，保证完全可约。**Part II（Ch5–7，特征理论）**拧紧核心：特征 $\chi_\rho=\mathrm{Tr}$ 把「矩阵组」压缩成「类函数」，Schur 引理推出正交关系 $\langle\chi_i,\chi_j\rangle=\delta_{ij}$，最终 $\sum d_i^2=|G|$ 且不可约个数 $=$ 共轭类个数——特征表成为「群的完整指纹」。**Part III（Ch8–12，专题）**是锋刃出鞘：$S_n$ 的 Young 图（组合）、$A_n$ 的限制分裂、诱导表示 + Brauer 定理、Mackey 不可约判据，最后用特征理论的三行证明干翻 Burnside $p^aq^b$ 定理——**表示论从「描述工具」升级为「证明引擎」**。

Serre 的极简体现在：每个定理只给最小假设，每步证明一字不废，全书 180 页走完别人 500 页的路。与 Fulton-Harris（例子驱动、看得见）互补：FH 给你「直觉」，Serre 给你「刀」。与 Humphreys/Hall（李代数/李群，连续对称）互补：那两本讲「连续对称怎么分类」，Serre 讲「离散对称怎么分类、怎么用来证明定理」。读 Serre 的最佳方式是**先读 FH 建立直觉，再用 Serre 拧紧逻辑**——你会发现 FH 用三页算的东西，Serre 用三行证完。

**Serre 的「极简方法论」可复刻**：(1) 每个概念先给最小定义，延后引入结构；(2) 证明只写「不可省略」的步骤，把常规推导留给读者；(3) 用一个最强工具（正交关系）贯穿全书，反复用在不同问题。这种「单工具、多战场」的风格，正是研究级数学写作的范本——值得在自己的笔记与证明中模仿。

---

## §10 与本仓库其他笔记的交叉引用

### 与已精读书目的呼应

| 本书 | 关系 | 交叉点 |
|---|---|---|
| **Fulton-Harris** GTM129 | 详略互补 | FH Ch1–3（有限群，例子丰富）↔ Serre Ch1–7（极简证明）；FH 的 $S_3$ 手算 ↔ Serre 的正交关系三行证 |
| **Humphreys** GTM9 | 离散↔连续 | Humphreys 讲李代数（连续对称），Serre 讲有限群（离散对称）；Serre Ch4 紧群是两者的桥（$\mathrm{SU}(2)$、Haar） |
| **Hall** GTM222 | 物理互补 | Hall Ch4–5（$\mathrm{SU}(2)$/$\mathrm{SU}(3)$ 矩阵实现）↔ Serre Ch4（$\mathrm{SU}(2)$ 的 $V_n$，Peter-Weyl）；Hall 的旋量 ↔ Serre 的紧群表示 |
| **Dummit & Foote** | 基础前置 | D&F Part I（群论、共轭类、Sylow）↔ Serre 全书；D&F 的模论 ↔ Serre 的「表示 = 模」观点 |
| **Isaacs**《Character Theory》 | 深度延伸 | Isaacs 是 Serre Part II 的专著级展开——Serre 给骨架，Isaacs 给血肉（$\pi$-特殊类、M-群、Brauer 诱导块） |

### AI/工程锚点法：表示论的工程落地

| 数学概念 | AI/工程对应 | 锚点说明 |
|---|---|---|
| **表示 = 群在向量空间上的作用** | 特征提取 / 嵌入 | 🟢$\rho:G\to\mathrm{GL}(V)$ = 把对称性编码成线性变换；等变神经网络(equivariant NN) 的数学基础 |
| **特征 $\chi=\mathrm{Tr}(\rho)$ = Fourier 在群上** | 频域分析 / 谱方法 | 🟢特征表 = 群上 DFT 矩阵；正交关系 = Fourier 基的正交性；「特征提取」一词的数学根源 |
| **正交 = 有限群上的 Fourier** | FFT / 谱分解 | 🟢$\langle\chi,\psi\rangle=\frac1{|G|}\sum\overline{\chi(g)}\psi(g)$ 是 DFT 内积；Peter-Weyl = 连续 Fourier |
| **Schur 引理 = 不可约间无混合** | 正交基 / 信息不泄漏 | 🟢不同不可约「通道」无串扰 = OFDM 正交频分复用；等变网络不同不可约特征解耦 |
| **$S_n$ 表示 = 对称** | 对称破缺 / 数据增强 | 🟡$S_n$ 的平凡/符号表示 = 玻色子/费米子统计；Young 对称化 = 张量网络的对称投影 |
| **诱导表示 $\mathrm{Ind}_H^G$** | 升采样 / 数据增广 | 🟡从小群表示「升格」到大群 = 用小数据集增广；$\mathrm{Res}$ = 下采样 |
| **Mackey 不可约判据** | 正交性检验 / 解耦判定 | 🟢双陪集逐项检查「是否相交」= 通道间正交性检验，工程上的「无串扰验证」 |
| **Burnside $p^aq^b$** | 有限性证明 / 结构定理 | 🟡用调和分析工具证纯代数定理 = 用频域分析证时域性质，跨域证明范式 |
| **等型分解 + 投影 $p_i$** | 滤波器组 / 通道分离 | 🟢$p_i=\frac{d_i}{|G|}\sum\overline{\chi_i(g)}\rho(g)$ 把表示「滤波」到第 $i$ 不可约通道 |

### 学习路径建议（基于本仓库已有笔记）

1. **先修**：Dummit & Foote Part I（群论：共轭类、中心化子、Sylow 定理）+ 线性代数（迹、特征值、Kronecker 积）
2. **并行**：Hall Ch4（$\mathrm{SU}(2)$ 的矩阵实现）——Serre Ch4 紧群的计算版热身
3. **本书核心路线**：Ch1–2（一般理论+特征，甜区）→ Ch3（诱导+互反，枢纽）→ Ch7（$\sum d_i^2=|G|$，指纹理论）→ Ch12（Burnside，收官秀）
4. **可选深入**：Ch8–9（$S_n$/$A_n$ 的 Young 图）→ Ch10–11（Brauer 定理 + Mackey）→ Isaacs 专著
5. **验证工具**：配合 `sympy` 计算 $S_4$ 特征表、`numpy.kron` 实现 Kronecker 积、`matplotlib` 画 Young 图——见文末实操建议

---

## §11 自测答案要点（供核对）

1. **Ch1** $S_3$ 三不可约：$\mathbf{1}(1)$、$\boldsymbol\varepsilon(1)$、$\mathbf{2}(2)$，$\sum d_i^2=1+1+4=6$。标准表示 $V=\{x_1+x_2+x_3=0\}$，$(12)$ 迹 $0$，$(123)$ 迹 $-1$。
2. **Ch2** $\langle\chi_3,\chi_3\rangle=\frac16(4+0+2)=1$；列正交 $(12)$ vs $(123)$：$1\cdot1+(-1)\cdot1+0\cdot(-1)=0$。
3. **Ch3** $\mathrm{Ind}_{A_3}^{S_3}\chi_\omega$ 维度 $=2$，由互反律 $\langle\mathrm{Ind}\chi_\omega,\chi_{\mathrm{std}}\rangle=\langle\chi_\omega,\mathrm{Res}\chi_{\mathrm{std}}\rangle=1$（$\mathrm{Res}\chi_{\mathrm{std}}$ 含 $\chi_\omega$ 一次），故 $\mathrm{Ind}=\chi_{\mathrm{std}}$。
4. **Ch4** $\mathrm{SU}(2)$ 不可约 $V_n$（$n=0,1,2,\ldots$，维 $n+1=2j+1$）；$\mathrm{SO}(3)$ 只取偶 $n$（$j\in\mathbb{Z}$），因 $-I\in\mathrm{SU}(2)$ 在半整数 $j$ 作用为 $-1$。
5. **Ch5** 正则表示 $\mathbb{C}[G]$ 中 $V_i$ 出现 $d_i$ 次，$\sum d_i^2=|G|$。
6. **Ch6** $S_4$ 五不可约维数 $(1,1,2,3,3)$，$\sum=1+1+4+9+9=24$。2 维来自 $S_4/V_4\cong S_3$ 的标准表示提升。
7. **Ch7** $Q_8$ 五共轭类 → 五不可约 $(1,1,1,1,2)$，$\sum=1+1+1+1+4=8$。2 维 = $Q_8\hookrightarrow\mathrm{SU}(2)$（$i,j,k\mapsto$ Pauli 矩阵 $i\sigma_x,i\sigma_y,i\sigma_z$）。
8. **Ch8** $S_4$ 五 Young 图 $(4),(3{,}1),(2{,}2),(2{,}1{,}1),(1^4)$，维数 $(1,3,2,3,1)$，$\sum=24$。hook-length：$(3{,}1)$ 的 hook 积 $=4\cdot1\cdot2\cdot1=8$，$d=24/8=3$。
9. **Ch9** $A_4$ 四不可约维数 $(1,1,1,3)$，$\sum=12$。三个 1 维来自 $A_4/V_4\cong\mathbb{Z}/3$；3 维为标准限制。
10. **Ch10** $\chi_{\mathrm{std}}=\mathrm{Ind}_{\langle(123)\rangle}^{S_3}\chi_\omega$，单一循环群诱导，系数 1（满足 Brauer 的整数性）。
11. **Ch11** $\mathrm{Ind}_{\langle(12)\rangle}^{S_3}\boldsymbol\varepsilon$ 维 3，特征 $\chi(e)=3,\chi(12)=1,\chi(123)=0$，$\langle\chi,\chi\rangle=\frac16(9+3+0)=2\ne1$，可约 $=\chi_{\mathrm{std}}\oplus\boldsymbol\varepsilon$（维 $3=2+1$）。
12. **Ch12** $12=2^2\times3$ 是 $p^aq^b$ 型 $\Rightarrow$ 可解。$A_4$ 可解：$V_4\triangleleft A_4$，商 $\mathbb{Z}/3$，$V_4\cong(\mathbb{Z}/2)^2$ 交换，合成因子皆交换。

---

> **精读纪律**：本文为快速逐章精读，每章取 1 个飞腾锚点 + 1 个关键定理 + 1 道自测题。深入计算与完整证明请回原书（Serre 的证明每步都值得逐字精读）。🟢 = 事实锚点（可直接引用），🟡 = 类比锚点（仅供直觉，不可引用于严格证明）。
>
> **实操验证建议**（Python/SymPy）：
> - `numpy.kron` 实现张量积 → 验证 Ch1 直和/张量积的矩阵形式
> - 构造 $S_3$、$S_4$ 特征表矩阵 → 验证 Ch2/Ch6 行/列正交 $\langle\chi_i,\chi_j\rangle=\delta_{ij}$
> - `sympy` 计算 $\sum d_i^2$ → 验证 Ch7 $|G|$ 等式
> - 枚举 $n=4,5$ 的分拆 $\lambda\vdash n$ → 验证 Ch8 Specht 模维数与 $\sum=n!$
> - 实现诱导特征公式 $\chi_{\mathrm{Ind}}(g)=\frac1{|H|}\sum_{xgx^{-1}\in H}\chi_W(xgx^{-1})$ → 验证 Ch3/Ch10 Frobenius 互反
