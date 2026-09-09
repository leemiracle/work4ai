# Nicholas J. Higham《数值算法的精度与稳定性》 · 快速逐章精读

> 基于原书：*Accuracy and Stability of Numerical Algorithms*（Nicholas J. Higham, 2nd ed., SIAM, 2002）/ 读于：2026-07-03
> 定位：**数值精度分析的终极参考**，逐算法拆解向后误差界，是 IEEE 754 浮点模型、混合精度训练、LAPACK 稳定性证明的理论地基。
> 本文为**快速逐章精读**，原书 4 大部分约 27 章合并为 12 主题，每主题 1 个飞腾锚点 + 1 个关键定理 + 1 道自测题。
> 关联：[trefethen 数值线代]（直觉版）· [demmel 应用数值线代]（工程版）· [golub_van_loan 矩阵计算]（手册版）· [nocedal_wright 数值优化] · [研究入门](C-数值分析与科学计算_研究入门.md)

---

## §0 引言：Higham 是数值精度分析的「最高法院」

Nicholas J. Higham（Manchester，Royal Society Fellow，SIAM Fellow，浮点算术与矩阵函数精度理论的领军人物）
所著《Accuracy and Stability of Numerical Algorithms》（初版 1996，第二版 2002）是**数值算法精度与稳定性分析的终极参考书**
——全书约 700 页、27 章、4 大部分，从最基础的 IEEE 754 浮点模型 $\mathrm{fl}(x)=x(1+\delta)$
一路推到每个核心数值算法的向后误差界，几乎每个定理都给出**逐分量（componentwise）**的精确常数
（而非 $O(n\epsilon)$ 的大 $O$ 估计）。

一句话定位：本书是 stage-3 §3B 数值方向的**精度理论纵深顶点**。
刚完成的 [trefethen 数值线代]（直觉先行）、[demmel 应用数值线代]（算法 + 复杂度 + 并行三轴）、
[golub_van_loan 矩阵计算]（百科手册）三套都是从「**算法**」侧讲数值线代，
而 Higham 单刀直入「**误差**」侧——它不教你怎么写算法，只教你怎么证明这个算法的浮点实现
满足 $\hat{L}\hat{U}=PA+\Delta A$ 且 $|\Delta A|\le n\epsilon|\hat L||\hat U|$（Wilkinson 经典界）。
读完本书，读者面对任何 `numpy.linalg.solve` 调用都能精确说出「这一步引入了多少浮点误差、放大了多少倍」。

全书的灵魂是两条公式：① **浮点基本模型** $\mathrm{fl}(a\circ b)=(a\circ b)(1+\delta)$，$|\delta|\le u$（unit roundoff），
把每一步算术运算的误差参数化；② **总纲不等式**「前向误差 $\le$ 后向误差 $\times\,\kappa$」，
把算法质量（后向误差）与问题难度（条件数 $\kappa$）分离——这是 Higham 反复回到的「宪法」。
飞腾锚点把抽象的 $u$、$\kappa$、$\Delta A$ 钉到真实硬件：
**FP16 3.81×**（unit roundoff 在 FP16 下粗 $10^{12}$ 倍）、
**Iron Law <2%**（向后稳定的工程判据）、
**UDOT 16.9×**（求和误差传递的内积内核）。

### 四本数值线代教材对比

| 书 | 风格 | 严格性 | 适合谁 |
|:---|:-----|:------|:------|
| **Higham（本书）** | 纯误差分析，逐算法拆解向后误差界，精确常数 | 极高（证明最细，常数为王） | 专攻精度/稳定性理论的研究者 / 混合精度算法设计者 |
| **Golub-Van Loan**（刚做） | 百科全书式，统一分块记号 + 伪代码 + flop 计数 | 极全（覆盖最广，算法细节最详） | 按需查阅算法细节的从业者案头手册 |
| **Trefethen-Bau**（刚做） | 直觉先行，40 讲精炼，几何驱动 | 中高（侧重直觉与核心洞察） | 初入数值线代的研究生建骨架 |
| **Demmel**（刚做） | 算法 + 复杂度 + 并行三轴综合 | 高（理论 + LAPACK 接口双线） | 想理解「LAPACK 为何这样写」的工程师 |

> **阅读策略**：Trefethen 建直觉 → Demmel 补工程 → Golub-Van Loan 当手册 → **Higham 锐化精度理论（精度分析的「最高法院」）**。
> 四者构成数值线代完整四象限：直觉(TB) × 工程(Demmel) × 广度(GVL) × **精度纵深(Higham)**。

---

## §1 全书 12 主题骨架一览（飞腾锚点分布）

原书 4 大部分约 27 章，本文按任务要求合并为 **4 部分 + 12 主题**（每主题标注对应原章节号），便于快速建立认知地图。

| 部分 | 主题 | 核心概念 | 飞腾锚点 |
|:----:|:-----|:--------|:--------|
| **§I 基础** (Ch 1-4) | 1. 误差模型与总纲 (Ch 1) | 前向/后向误差、条件数、精度宪法 | Iron Law <2% ⭐ |
| | 2. 浮点算术 IEEE 754 (Ch 2) | $\mathrm{fl}(x)=x(1+\delta)$、unit roundoff $u$ | FP16 3.81× ⭐ |
| | 3. 矩阵分析背景 (Ch 3) | 范数、谱、子空间、$\kappa(A)$ | matmul 15× ⭐ |
| | 4. 求和与误差传递 (Ch 4) | 递归/成对/补偿求和、运行误差分析 | UDOT 16.9× ⭐ |
| **§II 线性系统** (Ch 7-15) | 5. LU 与三角系统 (Ch 7-9) | 选主元、增长因子、Wilkinson 后向界 | Iron Law <2% ⭐ |
| | 6. Cholesky 与对称系统 (Ch 10-11) | SPD 稳定性、半正定扰动 | matmul 15× ⭐ |
| | 7. QR 与最小二乘 (Ch 12-13, 19-20) | Householder/Givens/SVD、向后稳定 | Schmidt 正交化 |
| | 8. 对称特征值与 SVD (Ch 14-15) | Weyl、相对精度、Jacobi | GEMM 9.45G ⭐ |
| **§III 其他主题** (Ch 16-26) | 9. 非对称特征值与迭代 (Ch 16-18) | Schur、QR 算法、Krylov | 分支预测 |
| | 10. 稀疏与特殊结构 + 迭代法 (Ch 21-22, 28) | Toeplitz/Vandermonde、CG/GMRES 稳定性 | TLB 4.81× ⭐ |
| | 11. 矩阵函数 (Ch 25-27) | $e^A$、scaling-squaring、Schur-Parlett | FP16 3.81× ⭐ |
| | 12. 条件数估计 (Ch 26) | Hager-Higham 算法、Skew 谱 | UDOT 16.9× ⭐ |

```
§I 基础:   fl(x)=x(1+δ) ─→ 前向误差 ≤ 后向误差 × κ ─── 精度宪法(贯穿全书)
§II 线代:  LU ─→ Cholesky ─→ QR ─→ 特征值/SVD  每个算法都给出精确后向误差界
§III 其他: 非对称特征值 ─→ 稀疏/迭代 ─→ 矩阵函数 ─→ 条件数估计  深化精度工具箱

主线: 误差模型(§I) ─→ 逐算法拆解(§II) ─→ 进阶工具(§III)  始终回到「这个算法有多稳定」
```

---

### 主题 1 · 误差模型与总纲（Ch 1 Introduction）

- **核心**：Higham 全书的「宪法章」，建立三大基石。
  ① **前向误差 vs 后向误差**的分离——前向误差 $\|\hat{x}-x\|$ 是「算出来与真解的差距」，
  后向误差 $\eta(\hat{x})=\min\{\epsilon:\hat{x}\text{ 精确解}(A+\Delta A)\hat{x}=b,\ \|\Delta A\|\le\epsilon\|A\|\}$
  是「算法相当于精确求解了哪个邻近问题」。这一分离是精度分析的灵魂：算法质量（后向误差）与问题难度（条件数）独立评估。
  ② **条件数** $\kappa(A)=\|A\|\|A^{-1}\|$ 量化问题对扰动的敏感度。
  ③ **总纲不等式**：前向误差 $\le$ 后向误差 $\times\,\kappa$——贯穿全书 27 章的统一判据。
- **飞腾锚点**：**Iron Law <2% [Lab00]** ⭐（向后稳定的工程判据）🟢。
  Iron Law「性能 = 指令数 × CPI × 时钟周期」是性能分析的铁律；
  Higham 的「前向误差 $\le$ 后向误差 $\times\kappa$」是精度分析的铁律——二者同构。
  向后稳定的算法（后向误差 $\sim n\epsilon$）满足「$<2\%$ 误差」的工程判据当 $\kappa$ 不太大；
  病态问题（$\kappa\to\infty$）即使算法完美，前向误差仍爆炸——这与「即使 CPU 再快，受限于指令数」同构。
- **关键定理**：**总纲不等式**——设问题 $f$ 的条件数为 $\kappa_f$，算法 $\tilde f$ 的后向误差为 $\eta$，则前向误差满足
$$\frac{\|\tilde{f}(x)-f(x)\|}{\|f(x)\|}\le \kappa_f\cdot\eta + O(\eta^2)$$
  即「输出误差 = 问题敏感度 × 算法后向误差」。$\kappa$ 大则输入微小扰动被巨幅放大——这是「病态（ill-conditioned）」的精确定义，与算法好坏无关。
- **自测**：$A=\begin{pmatrix}1&1\\1&1.0001\end{pmatrix}$，$\kappa(A)\approx4\times10^4$。
  若后向误差 $\eta\sim10^{-16}$（FP64），前向误差界约 $4\times10^{-12}$；
  若 FP16（$\eta\sim10^{-3}$），前向误差界 $\sim40$——完全失效。
  解释：FP16 解此系统为何无意义？

---

### 主题 2 · 浮点算术 IEEE 754（Ch 2 Floating Point Arithmetic）

- **核心**：本书的「公理章」，把浮点运算参数化为可分析的形式。
  ① **IEEE 754 模型**：每个浮点数 $x$ 满足 $x=\pm m\cdot\beta^{e-p}$（$\beta$ 基数、$p$ 尾数位、$e$ 指数）；
  FP64（$p=53,\beta=2$）的 unit roundoff $u=2^{-53}\approx1.11\times10^{-16}$。
  ② **基本算术模型**：$\mathrm{fl}(a\circ b)=(a\circ b)(1+\delta)$，$|\delta|\le u$（$\circ\in\{+,-,\times,\div\}$）——
  把每一步运算的误差统一参数化为 $\delta$，这是 Wilkinson 经典建模。
  ③ **$\gamma$ 记号**：$\gamma_n=nu/(1-nu)\approx nu$，简化 $n$ 步运算的累积误差表达。
  ④ ** cancellation（抵消）**：相近数相减导致有效位灾难性损失，是浮点误差的头号杀手。
- **飞腾锚点**：**FP16 3.81× [L01]** ⭐（unit roundoff 与精度边界）🟢。
  FP16 的 $u=2^{-11}\approx4.88\times10^{-4}$ 比 FP64 粗约 $10^{12}$ 倍。
  Higham 的 $\gamma_n=nu$ 在 FP16 下：$n=10^3$ 步累积误差 $\gamma_{10^3}\approx0.49$——约 50% 误差！
  而 FP64 下 $\gamma_{10^3}\approx10^{-13}$。
  混合精度训练（FP16 前向 + FP32 主权重 + FP16 梯度）正是利用 Higham 模型设计：
  前向误差 $\le$ 后向误差 $\times\kappa$，只要 $\kappa$ 不爆（批量归一化控 $\kappa$），FP16 安全。
- **关键定理**：**IEEE 754 基本算术模型**——对所有 $\circ\in\{+,-,\times,\div\}$（无上溢/下溢），浮点结果满足
$$\mathrm{fl}(a\circ b)=\frac{a\circ b}{1+\delta}=(a\circ b)(1+\delta'),\quad |\delta|=|\delta'|\le u$$
  其中 $u$ 是 unit roundoff（FP64 $\approx1.11\times10^{-16}$，FP32 $\approx6\times10^{-8}$，FP16 $\approx4.88\times10^{-4}$）。
  这条公式是全书所有误差分析的起点——把「浮点的不确定性」转化为可计算的 $u$。
- **自测**：用 FP64 计算 $1.0+10^{-17}$ 结果是多少？为什么？
  （答：$10^{-17}<u=1.11\times10^{-16}$，加法结果仍是 $1.0$——有效位丢失。）
  再算 $1.0+10^{-15}-1.0$，结果约 $9.99\times10^{-16}$（损失约 1 位精度）。

---

### 主题 3 · 矩阵分析背景（Ch 3 Background: Matrix Analysis）

- **核心**：为后续所有算法的分析提供数学语言。
  ① **范数**：向量 $\ell^p$（$p=1,2,\infty$）、矩阵诱导范数 $\|A\|=\max_{\|x\|=1}\|Ax\|$、
  Frobenius 范数 $\|A\|_F=\sqrt{\sum_{ij}|a_{ij}|^2}$；关键次乘性 $\|AB\|\le\|A\|\|B\|$。
  ② **谱**：特征值 $\lambda_i$、奇异值 $\sigma_1\ge\cdots\ge\sigma_r>0$、谱半径 $\rho(A)=\max|\lambda_i|$。
  ③ **SVD 存在性**：任何 $A=U\Sigma V^*$，$\|A\|_2=\sigma_1$，$\|A\|_F=(\sum\sigma_i^2)^{1/2}$。
  ④ **条件数** $\kappa_p(A)=\|A\|_p\|A^{-1}\|_p$；2-范数下 $\kappa_2(A)=\sigma_1/\sigma_r$。
  ⑤ **四个基本子空间**及正交分解。⑥ **扰动理论**：$(A+\Delta A)^{-1}-A^{-1}\approx-A^{-1}\Delta AA^{-1}$。
- **飞腾锚点**：**matmul 15× [V03]** ⭐（矩阵范数与诱导算子）🟢。
  矩阵诱导范数 $\|A\|=\max_{\|x\|=1}\|Ax\|$ 的计算本质是「在单位球上最大化 $\|Ax\|$」，
  2-范数计算需 SVD（$\|A\|_2=\sigma_1$），但幂迭代近似只需反复矩阵-向量乘 $Av$——GEMM 内核。
  Frobenius 范数是全体元素平方和（一次 UDOT 扫描）。
  Higham 在此章定义的范数工具是后续所有「$\|\Delta A\|\le n\epsilon\|A\|$」类界的语言基础。
  飞腾 matmul 15× 加速使大规模 $\|A\|_2$ 的幂迭代在毫秒级完成。
- **关键定理**：**Neumann 级数（逆的扰动展开）**——若 $\|\Delta A\|<1/\|A^{-1}\|$（即 $\kappa(A)\|\Delta A\|/\|A\|<1$），则 $A+\Delta A$ 非奇异且
$$(A+\Delta A)^{-1}=A^{-1}\sum_{k=0}^{\infty}(-\Delta A\,A^{-1})^k=A^{-1}-A^{-1}\Delta AA^{-1}+O(\|\Delta A\|^2)$$
  一阶项 $\|\Delta A^{-1}\|\le\|A^{-1}\|^2\|\Delta A\|=\kappa(A)\|\Delta A\|/\|A\|$——这就是「求逆的条件数 = $\kappa$」的来源。
- **自测**：$A=\begin{pmatrix}3&0\\0&2\end{pmatrix}$，$\Delta A=\begin{pmatrix}0&0.01\\0.01&0\end{pmatrix}$。
  用 Neumann 一阶展开估 $\|(A+\Delta A)^{-1}-A^{-1}\|$，与精确值比较。
  （答：$\kappa(A)=3/2$，一阶界 $\sim0.01\cdot3/2/3\approx0.005$。）

---

### 主题 4 · 求和与误差传递（Ch 4 Summation）

- **核心**：最简单的数值运算却蕴含全部精度分析的精髓。
  ① **递归求和** $s_n=((\cdots((x_1+x_2)+x_3)+\cdots)+x_n)$：
  Higham 给出精确后向误差界 $|\hat{s}_n-\sum x_i|\le(n-1)u\sum|x_i|+O(u^2)=\gamma_{n-1}\sum|x_i|$——
  误差正比于**绝对值之和**而非平方和，这是 componentwise 稳定性的体现。
  ② **成对求和（pairwise / cascade）**：二分树形相加，深度 $\log_2 n$，误差界 $\gamma_{\log_2 n}\sum|x_i|$——
  NumPy `sum` 的默认实现，比朴素递归稳定。
  ③ **Kahan 补偿求和**：用额外变量跟踪舍入误差，理论误差 $\le 2u\sum|x_i|+O(nu^2)$——几乎 $O(1)$ 误差！
  ④ **运行误差分析（running error analysis）**：随算随记录误差界，比先验界紧。
  ⑤ **求和顺序的影响**：从小到大相加误差最小（避免大数吞小数）。
- **飞腾锚点**：**UDOT 16.9× [E05]** ⭐（内积累加 = 求和的硬件实现）🟢。
  求和是所有数值算法的底层燃料——内积 $\sum a_i b_i$、范数 $\sqrt{\sum|x_i|^2}$、矩阵乘 $c_{ij}=\sum a_{ik}b_{kj}$
  本质都是「浮点加法序列」。
  飞腾 INT8 UDOT 点积指令把求和向量化达 16.9× 加速，但向量化的求和顺序与朴素递归不同——
  Higham 的成对求和误差界 $\gamma_{\log n}$ 正好匹配向量化的树形归约结构。
  这是「硬件优化与数值稳定性协同」的经典案例：SIMD 求和既快又稳。
  AI 锚点：**PyTorch `torch.sum`** 默认成对求和，FP16 训练稳定性的关键。
- **关键定理**：**递归求和的后向误差界（Higham）**——浮点递归求和 $\hat{s}_n$ 满足
$$\hat{s}_n=\sum_{i=1}^{n}x_i(1+\gamma_{i-1}),\quad \gamma_{i-1}=\frac{(i-1)u}{1-(i-1)u}\approx(i-1)u$$
  即「每个加权的 $x_i$ 都带一个 $O(iu)$ 的相对扰动」——componentwise 后向稳定。
  前向绝对误差界 $\le\gamma_{n-1}\sum|x_i|$（注意是绝对值之和，不是 $\sum|x_i|$ 的相对误差）。
  对比 Kahan 补偿求和：误差降至 $O(u)$，几乎与 $n$ 无关。
- **自测**：求 $\sum_{i=1}^{10^6}10^{-8}$（理论值 $=0.01$），FP32（$u\approx6\times10^{-8}$）下：
  朴素递归 vs 成对求和 vs Kahan 补偿，哪个结果最准？
  （提示：朴素递归 $\gamma_{10^6}\approx0.06$，6% 误差；成对 $\gamma_{20}\approx10^{-6}$；Kahan $\sim u$。）

---

### 主题 5 · LU 分解与三角系统（Ch 7-9 LU / Triangular Systems）

- **核心**：解 $Ax=b$ 的直接法，精度分析的经典战场。
  ① **LU 分解** $PA=LU$（部分选主元），复杂度 $\frac{2}{3}n^3$。
  ② **Wilkinson 经典后向界**：$\hat{L}\hat{U}=PA+\Delta A$，$|\Delta A|\le n\epsilon_{\rm mach}|\hat{L}||\hat{U}|$——
  这是 componentwise 界，比 normwise 界紧。
  ③ **增长因子** $\rho=\max|u_{ij}|/\max|a_{ij}|$：部分选主元下 $\rho\le2^{n-1}$（最坏，Wilkinson 反例），
  实践中 $\rho\sim O(n)$ 几乎总成立——这是「理论上不保证但实际稳定」的经典案例。
  ④ **三角系统求解** $Ly=b$ / $Ux=y$：componentwise 后向稳定，$|\Delta b|\le n\epsilon|L||y|$。
  ⑤ **完全选主元** $\rho$ 更小但代价高 $O(n^2)$ 搜索，实际中部分选主元已足够。
- **飞腾锚点**：**Iron Law <2% [Lab00]** ⭐（向后稳定 = 误差可控）🟢。
  LU 的向后稳定性直接对应 Iron Law 的「$<2\%$ 误差」判据：
  当 $\rho\sim O(n)$ 时，$\|\Delta A\|/\|A\|\le n^2\epsilon$，FP64 下 $n=10^3$ 时 $\sim10^{-10}$——远低于 2%。
  但 Wilkinson 反例（$w_{ij}=-1$ if $i>j$ else $1$）使 $\rho=2^{n-1}$，FP64 下 $n=60$ 时 $\rho\sim10^{18}$——误差爆炸，违反 Iron Law。
  Higham 用精确常数区分「理论最坏」与「实践典型」，这正是精度分析的核心价值。
  全完全选主元（complete pivoting）可把 $\rho$ 降到 $O(n)$ 但代价是 $O(n^2)$ 搜索——Iron Law 的精度轴与速度轴权衡。
- **关键定理**：**Wilkinson 后向误差界（componentwise）**——部分选主元 LU 的浮点结果满足
$$\hat{L}\hat{U}=PA+\Delta A,\quad |\Delta A|\le n\,u\,|\hat{L}||\hat{U}|$$
  若增长因子 $\rho=\max|u_{ij}|/\max|a_{ij}|$ 有界（实践中 $\rho\sim O(n)$），则 $\|\Delta A\|_\infty/\|A\|_\infty\le nu\cdot\rho$——向后稳定。
  Wilkinson 反例证明 $\rho$ 可达 $2^{n-1}$（指数爆炸），但 50 年实践从未遇到——这是「理论与经验的鸿沟」。
- **自测**：$A=\begin{pmatrix}10^{-20}&1\\1&1\end{pmatrix}$。
  ① 不选主元做 LU：乘子 $l_{21}=10^{20}$，$u_{22}=1-10^{20}$，结果完全失真。
  ② 部分选主元（交换行）：乘子 $l_{21}\approx1$，结果精确。
  计算两种情形的 $\rho$，说明选主元的作用。

---

### 主题 6 · Cholesky 与对称系统（Ch 10-11 Symmetric / SPD）

- **核心**：$A$ 对称正定（SPD）时享有「免费的数值保险」。
  ① **Cholesky 分解** $A=LL^T$（$L$ 下三角，对角正），无需选主元即 componentwise 向后稳定，
  $|\Delta A|\le nu|L||L^T|$，代价 $\frac{1}{3}n^3$（比 LU 快 2 倍）。
  ② **为何无需选主元**：SPD 保证所有主子式正，消元过程中对角元恒正，乘子 $|l_{ij}|\le\sqrt{a_{jj}/a_{ii}}$ 有界——
  增长因子 $\rho\le1$（LU 的 $\le2^{n-1}$ 形成鲜明对比）。
  ③ **半正定扰动**：$A+\Delta A$ 仍 SPD 当 $\|\Delta A\|_2<\lambda_{\min}(A)$（最小特征值）。
  ④ **对称不定系统**（$A$ 对称但有不定）：Bunch-Kaufman 选主元，块对角 $2\times2$ 主元。
  ⑤ **Cholesky 的 componentwise 后向稳定性**比 LU 更强——SPD 结构是天然的精度保护。
- **飞腾锚点**：**matmul 15× [V03]** ⭐（分块 Cholesky 的 GEMM 内核）🟢。
  分块 Cholesky 把 $A$ 切为 $b\times b$ 子块，核心运算是子块三角求解 + 矩阵乘（GEMM）——
  这是 LAPACK `dpotrf` 高性能实现的关键。
  飞腾 NEON GEMM 经循环重排 + 向量化达 15× 加速，$n=10^4$ 的 Cholesky 从小时级降到秒级。
  Higham 强调：SPD 问题的「免费稳定性」使 FP16/FP32 混合精度 Cholesky 在 $\kappa<1/u_{\rm low}$ 时安全——
  这是混合精度 PDE 求解器的理论基础。
  AI 锚点：**高斯过程回归**的协方差矩阵求逆（SPD）、**K-FAC** 的 Kronecker 因子分解。
- **关键定理**：**Cholesky 的 componentwise 后向稳定性**——若 $A$ 对称正定，浮点 Cholesky $\hat{L}$ 满足
$$\hat{L}\hat{L}^T=A+\Delta A,\quad |\Delta A|\le\gamma_{n+1}|L||L^T|,\quad \gamma_{n+1}=\frac{(n+1)u}{1-(n+1)u}$$
  且 $|l_{ij}|\le\sqrt{a_{ii}}$（增长因子 $\rho\le1$），故 $\|\Delta A\|/\|A\|\le\gamma_{n+1}$——**无选主元即稳定**。
  对比 LU 的 $\rho\le2^{n-1}$，SPD 结构带来指数级的稳定性提升。
- **自测**：$A=\begin{pmatrix}4&2&0\\2&5&2\\0&2&5\end{pmatrix}$（SPD）。
  ① 手算 Cholesky $L$，验证 $LL^T=A$。
  ② 若 $A$ 改为 $\begin{pmatrix}1&2\\2&1\end{pmatrix}$（不定），Cholesky 为何失败？
  （答：$l_{22}=\sqrt{1-4}$ 虚数——主元非正。）

---

### 主题 7 · QR 与最小二乘（Ch 12-13, 19-20 Orthogonalization & Least Squares）

- **核心**：超定系统 $\min_x\|Ax-b\|_2$ 的稳定解路。
  ① **Householder 反射** $P=I-2vv^*/\|v\|^2$：镜面反射，正交对称（$P=P^*=P^{-1}$），
  是最稳定的 QR 实现方式（LAPACK 默认 `dgeqrf`）。
  ② **Givens 旋转**：平面旋转，适合稀疏/结构化 QR（逐元素零化）。
  ③ **QR 分解** $A=QR$ → 最小二乘解 $R\hat{x}=Q^Tb$。
  ④ **Householder QR 向后稳定**：$\|\Delta A\|/\|A\|=O(nu)$，与 $\kappa(A)$ 无关。
  ⑤ **正规方程** $A^TAx=A^Tb$ 的 componentwise 后向误差 $\sim\kappa(A)^2$——病态时完全失真。
  ⑥ **SVD 伪逆** $x=V\Sigma^+U^Tb$：最稳且自动处理秩亏损。
  ⑦ **经典 vs 改进 Gram-Schmidt**：CGS 数值不稳（$O(\kappa^2)$），MGS 改善（$O(\kappa)$）——数学等价但数值不等价。
- **飞腾锚点**：**Schmidt 正交化**（QR 分解的数学内核）🟢。
  Householder、Givens、Gram-Schmidt 三种 QR 实现的数学内核都是正交投影——
  核心运算 $\langle a,q\rangle q$ 是内积 + 标量乘。
  Higham 重点分析 CGS vs MGS 的精度差异：CGS 的后向误差 $\sim\kappa^2$（与正规方程同级，危险），
  MGS 的后向误差 $\sim\kappa$（与 Householder 同级，安全）——「循环顺序一改，稳定性天壤之别」。
  这正是 Higham 全书的核心洞察：数学等价的算法，浮点实现下精度可能相差 $\kappa$ 倍。
  AI 锚点：**PyTorch `torch.linalg.qr`** 用于正交初始化、RNN 梯度稳定性。
- **关键定理**：**Householder QR 的后向稳定性**——Householder QR 得 $\hat{Q},\hat{R}$ 满足
$$A+\Delta A=\hat{Q}\hat{R},\quad \|\Delta A\|_F\le\gamma_{mn}\|A\|_F$$
  即后向误差与 $\kappa(A)$ **无关**，仅正比于 $nu$。
  对比正规方程 $A^TAx=A^Tb$ 的后向误差 $\sim\kappa(A)^2\cdot u$（条件数平方放大）——
  这是「永远优先 QR 而非正规方程」的严格证明。
  最小二乘解的前向误差：$\|\hat{x}-x\|/\|x\|\le\gamma_{mn}\kappa(A)$（残差小时）或 $\gamma_{mn}\kappa(A)^2$（残差大时）。
- **自测**：构造 Householder 向量 $v$ 将 $\mathbf{x}=(1,2,2)^T$ 映为 $\|\mathbf{x}\|\mathbf{e}_1=(3,0,0)^T$。
  （答：$v=x-\|x\|e_1=(-2,2,2)^T$，$\|v\|^2=12$，$P=I-\frac{2}{12}vv^T$，验证 $Px=(3,0,0)^T$。）

---

### 主题 8 · 对称特征值与 SVD（Ch 14-15 Symmetric Eigenvalue / SVD）

- **核心**：$A=A^T$ 的特征值问题享有最强稳定性保证。
  ① **对称 QR 算法**：先三对角化 $A\to T$（Householder），再隐式移位 QR，componentwise 后向稳定。
  ② **Jacobi 方法**：$J^TAJ$ 逐步消非对角元，精度极高，可达**相对精度**。
  ③ **Weyl 不等式**：$|\tilde{\lambda}_i-\lambda_i|\le\|\Delta A\|_2$（绝对界，与 $\kappa$ 无关）——
  对称问题的特征值扰动仅与 $\|\Delta A\|$ 有关。
  ④ **相对精度（Demmel-Higham-Veselić）**：SPD 矩阵的特征值可计算到 $|\tilde{\lambda}_i-\lambda_i|\le O(nu)\lambda_i$，
  即使最小特征值也有相对保证——一般矩阵做不到。
  ⑤ **SVD 向后稳定**：$A=U\Sigma V^T$ 的浮点实现满足 componentwise 后向误差 $O(nu)$。
  ⑥ **奇异值扰动**：Weyl 不等式对 SVD 同样成立，$|\tilde{\sigma}_i-\sigma_i|\le\|\Delta A\|_2$。
- **飞腾锚点**：**GEMM 9.45 GFLOPS [Lab05]** ⭐（工业级特征值/SVD 的 GEMM 内核）🟢。
  三对角化 $A=QTQ^T$ 的核心 $Q^TAQ$ 是标准 GEMM；
  分治法（Cuppen）的秩一修正缝合 $V(\Lambda+\rho vv^T)V^T$ 也依赖矩阵乘。
  工业级对称特征值计算（$n>10^3$）中 GEMM 占主导。
  Higham 强调：对称问题的「免费稳定性」使 FP16 SVD 在 $\kappa<1/u_{\rm low}$ 时相对精度仍可控——
  这是混合精度 PCA、推荐系统的精度保证。
  AI 锚点：**谱归一化**（GAN 稳定性）、**PCA 白化**、**推荐系统 ALS**。
- **关键定理**：**Weyl 不等式（对称特征值扰动）**——设 $A=A^T$，$\tilde{A}=A+\Delta A$，按序特征值满足
$$|\tilde{\lambda}_i-\lambda_i|\le\|\Delta A\|_2,\quad\forall i$$
  **更强地**（Demmel-Veselić-Higham）：若 $A$ 对称正定，存在算法使特征值达**相对精度**：
$$|\tilde{\lambda}_i-\lambda_i|\le O(nu)\,\lambda_i,\quad\forall i$$
  即使最小特征值 $\lambda_{\min}$ 也有 $O(nu)$ 相对误差——一般矩阵（非对称）的特征值扰动可任意大（$\kappa\to\infty$）。
- **自测**：$A=\begin{pmatrix}2&1\\1&2\end{pmatrix}$（特征值 1, 3）。
  ① 用 Jacobi 旋转（$\theta=\pi/4$）消去 $a_{12}$，验证一步对角化。
  ② 加扰动 $\Delta A=10^{-6}I$，Weyl 给出 $|\tilde{\lambda}_i-\lambda_i|\le10^{-6}$，验证。
  ③ 若 $A$ 改为非对称 $\begin{pmatrix}1&10^6\\0&1\end{pmatrix}$，特征值扰动为何可任意大？

---

### 主题 9 · 非对称特征值与迭代法（Ch 16-18 Nonsymmetric Eigenvalue）

- **核心**：一般方阵 $A$ 的特征值问题——数值分析中最棘手的领域。
  ① **Schur 分解** $A=QTQ^*$（$T$ 上三角，$Q$ 酉）：特征值是 $T$ 对角元。
  ② **QR 算法**：Hessenberg 化 + 带移位 QR 迭代，收敛到 Schur 形式。
  ③ **非对称特征值的病态性**：与对称问题不同，非对称特征值对扰动可任意敏感——
  $A=\begin{pmatrix}0&1\\0&0\end{pmatrix}+\epsilon\begin{pmatrix}0&0\\1&0\end{pmatrix}$ 的特征值从 $\{0,0\}$ 跳到 $\{\pm\sqrt{\epsilon}\}$。
  ④ **Bauer-Fike 定理**：若 $A$ 可对角化 $A=X\Lambda X^{-1}$，则扰动后特征值满足
  $\min_i|\tilde{\lambda}-\lambda_i|\le\kappa_2(X)\|\Delta A\|_2$——条件数由特征向量矩阵 $X$ 的条件数决定。
  ⑤ **伪特征值（pseudospectrum）**：刻画非正规矩阵的特征值敏感度，是 Higham-Trefethen 的延伸。
  ⑥ **幂法 / 反迭代 / Rayleigh 商迭代**：迭代法求部分特征值。
- **飞腾锚点**：**分支预测 0.71 vs 3.14 [Lab02]** ⭐（QR 算法 deflation 与分裂）🟢。
  QR 算法的收敛是「子问题逐步分裂」——当次对角元 $|h_{i,i-1}|<u(|h_{ii}|+|h_{i+1,i+1}|)$ 时矩阵分裂为独立子块，递归处理。
  这个「检测收敛 → 分割 → 递归」是数据依赖的条件分支，预测器命中率低。
  飞腾实测分支密集代码 IPC 仅 0.71 vs 理论 3.14。
  Higham 强调：非对称特征值的病态性（Bauer-Fike 的 $\kappa(X)$）使 FP16/FP32 求特征值极其危险——
  即使算法向后稳定，前向误差 = 后向误差 $\times\kappa(X)$ 可能爆炸。
  AI 锚点：**cuSOLVER `geev`** 底层即 Francis 双移位 QR；**Hessian 谱分析**（泛化研究）。
- **关键定理**：**Bauer-Fike 定理**——若 $A$ 可对角化 $A=X\Lambda X^{-1}$（$\Lambda$ 对角），扰动 $\tilde{A}=A+\Delta A$，则对 $\tilde{A}$ 的任一特征值 $\tilde{\lambda}$：
$$\min_{i}|\tilde{\lambda}-\lambda_i|\le\kappa_p(X)\|\Delta A\|_p$$
  其中 $\kappa_p(X)=\|X\|_p\|X^{-1}\|_p$ 是特征向量矩阵的条件数。
  对称矩阵 $X$ 正交（$\kappa_2(X)=1$）→ 退化为 Weyl；非正规矩阵 $\kappa(X)$ 可任意大 → 特征值病态。
- **自测**：$A=\begin{pmatrix}0&1\\0&0\end{pmatrix}$（幂零，特征值 $\{0,0\}$）。
  ① 加扰动 $\Delta A=\begin{pmatrix}0&0\\\epsilon&0\end{pmatrix}$，特征值变为 $\{\pm\sqrt{\epsilon}\}$——解释为何「任意小扰动使特征值离开原点」。
  ② 计算 $X$（$A$ 的特征向量矩阵），$\kappa(X)$ 为何无穷？

---

### 主题 10 · 稀疏与特殊结构 + 迭代法（Ch 21-22, 28 Sparse / Iterative）

- **核心**：大规模稀疏问题与特殊结构的精度保证。
  ① **Toeplitz 系统**（$a_{i-j}$ 只依赖下标差）：Levinson 递归 $O(n^2)$，
  但 Higham 指出 Toeplitz 求解的 componentwise 后向稳定性**不保证**——某些 Toeplitz 矩阵的 Levinson 解后向误差 $\sim\kappa$。
  ② **Vandermonde 系统**（$a_{ij}=\alpha_j^{i-1}$）：Björck-Pereyra 算法 $O(n^2)$，对正节点 componentwise 稳定。
  ③ **半定规划（SDP）的内点法**：大规模优化，精度由 KKT 系统的 $\kappa$ 决定。
  ④ **CG（共轭梯度）**：对称正定 $Ax=b$ 的 Krylov 子空间法，理论 $n$ 步终结，实际 $O(\sqrt\kappa)$ 步。
  ⑤ **GMRES**：非对称 $Ax=b$，最小化残差，存储 $O(kn)$（实际重启 GMRES($m$)）。
  ⑥ **迭代法的稳定性**：CG/GMRES 的浮点实现满足「$\hat{x}_k$ 接近 $\mathcal{K}_k$ 内的精确解」，
  但有限精度下 Krylov 子空间的正交性丧失（Lanczos breakdown），导致「幽灵特征值」。
  ⑦ **预条件** $M^{-1}Ax=M^{-1}b$ 降 $\kappa$ 加速。
- **飞腾锚点**：**TLB 4.81× [E04]** ⭐（稀疏 SpMV 的访存局部性）🟢。
  CG/GMRES 每步核心是 SpMV $Ap_k$——大型稀疏 $A$（PDE 离散化）的非零元分布不规则，TLB 缺失惩罚大。
  cache-blocking（CSR → BCSR 分块存储）把 TLB 命中率提升 4.81×。
  Higham 分析迭代法的精度：CG 在有限精度下的收敛与精确算术几乎一致（Greenbaum 1989），
  但 Lanczos（对称特征值）的正交性丧失导致幽灵特征值——需重正交化。
  Toeplitz/Vandermonde 的特殊结构虽加速但精度不保证，这是「速度与精度的权衡」。
  AI 锚点：**CG 用于 Hessian-free 二阶优化**（Martens 2010）、**GMRES 用于牛顿-Krylov**。
- **关键定理**：**CG 收敛率**——对称正定 $A$，$\kappa=\lambda_{\max}/\lambda_{\min}$，CG 第 $k$ 步 $A$-范数误差满足
$$\|x_k-x^*\|_A\le 2\left(\frac{\sqrt{\kappa}-1}{\sqrt{\kappa}+1}\right)^k\|x_0-x^*\|_A$$
  收敛速度 $\propto\sqrt{\kappa}$（而非最速下降的 $\propto\kappa$）——
  $\kappa=10^4$ 时 CG 约 200 步 vs 最速下降 20000 步。
  **有限精度下**（Greenbaum）：CG 的实际收敛与精确算术几乎一致，但正交性以 $O(u)$ 速率丧失。
  预条件降 $\kappa$ 直接加速：$\kappa\to1$ 时 1 步收敛。
- **自测**：$A=\text{diag}(1,10^4)$（$\kappa=10^4$），CG 需约多少步达 $10^{-6}$ 精度？
  若用 Jacobi 预条件 $M=A$，迭代几步？
  （答：无预条件 $\rho\approx0.98$，需 $\sim700$ 步；Jacobi 预条件后 $M^{-1}A=I$，$\kappa=1$，**1 步精确收敛**。）

---

### 主题 11 · 矩阵函数（Ch 25-27 Functions of Matrices）

- **核心**：$f(A)$ 的定义、计算与精度——Higham 的招牌领域（另有专著《Functions of Matrices》, 2008）。
  ① **定义**：若 $f$ 的 Taylor 级数收敛，则 $f(A)=\sum c_k A^k$（如 $e^A=\sum A^k/k!$）。
  ② **Schur-Parlett 方法**：先 Schur 分解 $A=QTQ^*$，在三角阵 $T$ 上用 Parlett 递推计算 $f(T)$——通用方法。
  ③ **矩阵指数** $e^A$：**scaling-and-squaring + Padé 逼近**（$e^A\approx(e^{A/2^s})^{2^s}$），是 MATLAB `expm` 的算法（Higham 2009 改进版）。
  ④ **矩阵对数** $\log A$：逆缩放-平方法，精度由 $\kappa(V)$（特征向量）决定。
  ⑤ **矩阵符号** $\text{sign}(A)$：Newton 迭代 $X_{k+1}=\frac{1}{2}(X_k+X_k^{-1})$。
  ⑥ **条件数**：$f(A)$ 的敏感度由 **Fréchet 导数**衡量——$f(A+E)-f(A)=L_f(A,E)+O(\|E\|^2)$。
  ⑦ **精度分析**：scaling-and-squaring + Padé 的 componentwise 后向误差 $O(nu)$——向后稳定。
- **飞腾锚点**：**FP16 3.81× [L01]** ⭐（矩阵函数的精度要求）🟢。
  矩阵函数对精度极度敏感——$e^A$ 的 scaling-and-squaring 需 $2^s$ 次乘法，
  每次引入 $O(u)$ 误差，FP16（$u\approx4.88\times10^{-4}$）下累积误差可达数个量级。
  Higham 的后向误差界 $\|\Delta A\|/\|A\|\le\gamma_n$ 在 FP16 下 $\gamma_n\approx nu$，$n=10^3$ 时 $\sim0.49$——50% 误差！
  实践中矩阵指数计算几乎必须 FP64。
  混合精度的矩阵函数（FP16 前向 + FP32/FP64 校正）是活跃研究方向。
  AI 锚点：**Neural ODE** 的 $e^{At}$ 求解（`torchdiffeq`）、**连续深度模型**、**扩散模型 score matching**。
- **关键定理**：**矩阵指数的 scaling-and-squaring + Padé 后向稳定性**——取 $s$ 使 $\|A/2^s\|\le\frac{1}{2}$，用 $[m/m]$ Padé 逼近 $e^{A/2^s}\approx D^{-1}N$，然后 $e^A=(e^{A/2^s})^{2^s}$。浮点结果满足
$$(A+\Delta A)\text{ 的精确指数}=\hat{e}^A,\quad \|\Delta A\|/\|A\|\le O(nu)$$
  即向后稳定。Higham（2009）改进了 Padé 阶数选择，使 MATLAB `expm` 成为工业标准。
  Fréchet 导数条件数：$\kappa_{e^A}=\frac{\|L_{e^A}(A,E)\|}{\|e^A\|}\cdot\frac{\|A\|}{\|E\|}$，量化 $e^A$ 对扰动的敏感度。
- **自测**：$A=\begin{pmatrix}0&1\\0&0\end{pmatrix}$（$A^2=0$，幂零），用 Taylor 级数算 $e^A$。
  （答：$e^A=I+A=\begin{pmatrix}1&1\\0&1\end{pmatrix}$——幂零矩阵的指数只需两项。）
  再算 $\log(I+A)$（$A$ 同上），验证 $\log(e^A)=A$。

---

### 主题 12 · 条件数估计（Ch 26 Condition Number Estimation）

- **核心**：精度分析的最后一块拼图——如何在 $O(n^2)$ 内估计 $\kappa(A)$（而非精确求 $\|A^{-1}\|$ 的 $O(n^3)$）。
  ① **Hager 算法**（1984）：利用 $\|A^{-1}\|_1=\max_{\|x\|_\infty\le1}\|A^{-1}x\|_1$ 的对偶，
  用梯度上升在单纯形上最大化 $\|A^{-1}x\|_1$，只需几次 $A^{-1}v$ 求解（$O(n^2)$）。
  ② **Higham 改进**：处理 Hager 算法的退化情形，给出 LAPACK `xLACON` 的鲁棒实现。
  ③ **componentwise 条件数**：$\kappa_{\rm comp}=\||A^{-1}||A||x|\,/\,\|x\|$，比 normwise 更紧。
  ④ **Skew 谱（Laso 1992）**：估计 $\kappa$ 的同时给出特征值分布信息。
  ⑤ **条件数估计的精度**：估计值通常在真实值的因子 2-10 内——对工程判据足够。
  ⑥ **应用**：LAPACK 在每次 `dgesv` 后可选调用 `dtrcon` 估计 $\kappa$，警告用户解的可靠性。
- **飞腾锚点**：**UDOT 16.9× [E05]** ⭐（条件数估计的内积内核）🟢。
  Hager 算法的核心是反复求解 $A^{-1}v$（即解 $Ay=v$）——已 LU 分解后每步 $O(n^2)$，
  其中三角求解 + 内积累加（UDOT 加速 16.9×）。
  Higham 的改进版需 5-10 次 $A^{-1}v$ 迭代，总代价 $O(n^2)$——比精确求 $\|A^{-1}\|$ 的 $O(n^3)$ 快 $n$ 倍。
  这是「精度分析的工程化」：不追求精确 $\kappa$，只要量级估计（用于判断「解可信吗」）。
  AI 锚点：**PyTorch `torch.linalg.cond`** 底层即 Hager-Higham 算法；
  **混合精度训练**中实时监控 $\kappa$ 决定是否切换 FP32。
- **关键定理**：**Hager-Higham 条件数估计算法**——$\|A^{-1}\|_1=\max_{\|x\|_\infty\le1}\|A^{-1}x\|_1$ 可通过对偶转化为 $\max_{\|y\|_1\le1,\ \mathrm{sign}(y)=\mathrm{sign}(A^{-T}z)}y^Tz$（$z$ 为 $A^{-1}x$ 的符号向量）。
  算法步骤：① 初始化 $x=(1/n,\ldots,1/n)^T$；② 解 $Ay=x$，记 $y$；③ 解 $A^Tz=\mathrm{sign}(y)$；④ 若 $\|z\|_1>\|x\|_1$，更新 $x$ 回 ②；否则终止，$\|A^{-1}\|_1\approx\|z\|_1$。
  收敛性：通常 4-7 次迭代，估计值在真实值的因子 10 内（Higham 证明）。
- **自测**：$A=\begin{pmatrix}1&1\\1&1+\epsilon\end{pmatrix}$，$\epsilon=10^{-10}$。
  ① 精确计算 $\kappa_\infty(A)\approx4\times10^{10}$。
  ② 用 Hager 算法（手算 2 步）估计 $\kappa$，与精确值比较。
  ③ 解释为何 LAPACK 在解 $Ax=b$ 后会警告「矩阵接近奇异」。

---

## §9 全书思想主线：从误差模型到逐算法精度保证

Higham 全书的灵魂可浓缩为一条追问：
「**这个算法的浮点实现，精确求解了哪个邻近问题？那个邻近问题离原问题多远？**」

围绕这一追问，全书 27 章形成清晰的「公理 → 工具 → 逐算法拆解」三层结构。

**第一层（Ch 1-4，主题 1-4）：误差模型的公理化**。
Ch 1 建立前向/后向误差分离与总纲不等式「前向误差 $\le$ 后向误差 $\times\kappa$」，
Ch 2 给出 IEEE 754 浮点模型 $\mathrm{fl}(a\circ b)=(a\circ b)(1+\delta)$（$|\delta|\le u$），
Ch 3 补矩阵分析工具（范数、SVD、Neumann 级数），
Ch 4 用求和问题示范全部分析框架（componentwise 后向误差、$\gamma_n$ 记号、运行误差分析）。
这一层是「公理层」——后续所有算法的误差分析都是这几条公理的推论。

**第二层（Ch 7-15，主题 5-8）：线性系统的逐算法拆解**。
每个核心算法都给出精确的 componentwise 后向误差界：
LU 的 Wilkinson 界 $|\Delta A|\le nu|L||U|$、
Cholesky 的 $|\Delta A|\le\gamma_{n+1}|L||L^T|$（$\rho\le1$，免费稳定）、
QR 的 $\|\Delta A\|\le\gamma_{mn}\|A\|$（与 $\kappa$ 无关）、
对称特征值的 Weyl + 相对精度。
这一层的核心洞察是「**对称结构是免费的数值保险**」：
对称问题的稳定性界比一般问题指数级强（$\rho\le1$ vs $\le2^{n-1}$）。

**第三层（Ch 16-26，主题 9-12）：进阶工具与精度极限**。
非对称特征值的 Bauer-Fike 病态性（$\kappa(X)$ 可爆炸）、
稀疏/迭代法的有限精度正交性丧失、
矩阵函数的 Fréchet 导数条件数、
条件数估计的 $O(n^2)$ 工程化。
这一层揭示「**精度分析的边界**」：
哪些问题本质病态（非正规矩阵、矩阵函数）、
哪些可工程化估计（Hager-Higham $\kappa$ 估计）。

这与已读教材呼应：
**Trefethen-Bau** 是 Higham Ch 1-4 的直觉浓缩版（同一公理，40 讲精炼）；
**Demmel** 是 Higham 的工程应用版（补上复杂度 + 并行轴，但精度常数不如 Higham 精确）；
**Golub-Van Loan** 是 Higham 的算法百科版（广度第一，但误差分析不如 Higham 系统）；
**Nocedal-Wright** 的 CG 收敛率与 Higham 主题 10 同源（优化视角 vs 数值视角）。
Higham 是四象限中的「精度纵深顶点」——当其他书说「这个算法稳定」时，
Higham 给出「稳定到什么常数、在什么条件下退化」的精确答案。

---

## §10 交叉引用与飞腾锚点速查

### 与本仓库其他笔记的交叉

| 本书概念 | 关联书 / 方向 | 接口 |
|:--------|:------------|:-----|
| 浮点模型 / IEEE 754 / $u$ | **[trefethen 数值线代]** Lec 13-15 | TB 讲概念直觉（$\epsilon_{\rm mach}$），Higham 给精确常数与 $\gamma_n$ 记号 |
| LU / QR / Cholesky 后向误差 | **[demmel 应用数值线代]** Ch 2-3 | Demmel 给算法 + LAPACK 接口，Higham 给逐分量常数（$\le nu\|L\|\|U\|$） |
| SVD / 矩阵函数 / 条件数 | **[golub_van_loan 矩阵计算]** Part 2,5,9 | GVL 给算法全谱系 + 伪代码，Higham 给每个算法的精度保证 |
| CG 收敛率 / Krylov 稳定性 | **[nocedal_wright 数值优化]** Ch 5 | NW 从优化视角（$\min\frac{1}{2}x^TAx$），Higham 从精度视角（有限精度正交性丧失） |
| 条件数 / 收敛复杂度 | **[Nesterov 凸优化]** | Nesterov 一阶最优 $O(1/\sqrt{\kappa})$ ↔ CG 的 $O(\sqrt{\kappa})$ 步，精度边界同源 |
| 范数 / SVD / 子空间 | **[Hoffman-Kunse 线性代数]**（stage-1） | HK 纯数学存在性，Higham 补「浮点实现有多稳定」 |
| 数值分析总览 | **[kress 数值分析 GTM181]** | Kress 是全数值分析（线代 + 插值 + PDE），Higham 专攻线代精度纵深 |

### AI / 工程锚点（精度理论 = 混合精度训练的地基）

| 算法 / 概念（本书主题） | AI / 工程落地 |
|:---------|:------------|
| **IEEE 754 浮点模型**（主题 2） | **FP16/BF16 混合精度训练**（NVIDIA Tensor Core）；$\mathrm{fl}(a\circ b)=(a\circ b)(1+\delta)$ 是精度分析起点 |
| **总纲不等式**（主题 1） | **混合精度的安全判据**：FP16 安全当 $\kappa\cdot u_{\rm FP16}<1$，即 $\kappa<2048$ |
| **向后稳定性**（主题 5-8） | **LAPACK / cuSOLVER** 所有例程的精度保证；`numpy.linalg.solve` 的可靠性根基 |
| **对称相对精度**（主题 8） | **FP16 SVD / PCA** 的精度保证（SPD 矩阵的免费稳定性） |
| **非对称病态性**（主题 9） | **Hessian 谱分析**的非正规性警告；**RNN 梯度爆炸**的精度根源 |
| **矩阵指数**（主题 11） | **Neural ODE** 的 ODE 求解器（`torchdiffeq`）；连续深度模型、扩散模型 |
| **条件数估计**（主题 12） | **PyTorch `torch.linalg.cond`**（Hager-Higham）；实时监控 $\kappa$ 决定精度切换 |
| **求和稳定性**（主题 4） | **PyTorch `torch.sum`** 默认成对求和（$\gamma_{\log n}$）；FP16 训练稳定性的关键 |

### 飞腾锚点速查（12 主题，8 锚点，相邻不重复）

| 锚点 | 主题 | 角度 |
|:-----|:-----|:-----|
| **Iron Law <2% ⭐** | 主题 1, 5 | 总纲误差界 / LU 向后稳定性 = $O(nu)$ 误差上限 |
| **FP16 3.81× ⭐** | 主题 2, 11 | unit roundoff 精度边界 / 矩阵函数 scaling-squaring 精度要求 |
| **matmul 15× ⭐** | 主题 3, 6 | 矩阵范数 GEMM 内核 / 分块 Cholesky GEMM |
| **UDOT 16.9× ⭐** | 主题 4, 12 | 求和内积累加 / Hager 条件数估计的三角求解 |
| **Schmidt 正交化** | 主题 7 | QR 分解正交投影 / CGS vs MGS 精度差异 |
| **GEMM 9.45G ⭐** | 主题 8 | 三对角化 / 对称特征值分治 GEMM 内核 |
| **分支预测** | 主题 9 | QR 算法 deflation / Schur 分裂 |
| **TLB 4.81× ⭐** | 主题 10 | 稀疏 SpMV cache-blocking / 迭代法访存局部性 |

---

> **下一步**：精读主题 2（IEEE 754 模型 $\mathrm{fl}(a\circ b)=(a\circ b)(1+\delta)$，FP16 锚点）
> + 主题 5（Wilkinson 后向界 $|\Delta A|\le nu|L||U|$，Iron Law 锚点）
> + 主题 8（对称相对精度 $|\tilde{\lambda}_i-\lambda_i|\le O(nu)\lambda_i$，Demmel-Higham 招牌）
> + 主题 11（矩阵指数 scaling-squaring + Padé，Neural ODE 接口）。
> 研究选题「**飞腾无 BF16 硬件下混合精度训练的精度边界**」——
> 当 FP16 的 $u\approx4.88\times10^{-4}$ 遇上 $\kappa\sim10^3$ 的 Transformer attention 矩阵，
> Higham 总纲不等式给出前向误差 $\sim0.49$（50%）——
> 能否用迭代精化（FP32 校正）把误差压回 $O(u_{\rm FP32})$？
> 与 Demmel-Veselić 相对精度（主题 8）协同：哪些层安全用 FP16、哪些必须 FP32？
> 衔接 [demmel]（工程版）第 1 章混合精度 + [golub_van_loan]（手册版）Part 9 矩阵函数 + [nocedal_wright] 第 5 章 CG。
