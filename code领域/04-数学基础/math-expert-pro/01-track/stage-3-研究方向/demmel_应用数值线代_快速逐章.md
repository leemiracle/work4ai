# James W. Demmel《应用数值线性代数》 · 快速逐章精读

> 基于原书：*Applied Numerical Linear Algebra*（James W. Demmel, SIAM, 1997）/ 读于：2026-07-03
> 定位：**数值线性代数「算法 + 算术复杂度 + 并行性」三轴综合教材**（UC Berkeley / LAPACK 核心开发者），比 Trefethen 更工程化、比 Golub-Van Loan 更紧凑。
> 本文为**快速逐章精读**，每章 1 个飞腾锚点 + 1 个关键定理 + 1 道自测题。
> 关联：[trefethen 数值线代]（同期）· [nocedal_wright 数值优化] · [kress 数值分析 GTM181] · [研究入门](C-数值分析与科学计算_研究入门.md)

---

## §0 引言：Demmel 是数值线代的「三轴综合教材」

James W. Demmel（UC Berkeley，LAPACK/ScaLAPACK 核心开发者，2010 年 ACM/IEEE von Neumann 奖得主）
的《Applied Numerical Linear Algebra》（SIAM 1997）是数值线性代数方向最具特色的教材
——它不像 Trefethen 那样以概念直觉见长，也不像 Golub-Van Loan《Matrix Computations》那样以百科全书式广度著称，
而是以**「算法描述 + 算术复杂度分析 + 并行实现」三轴并重**为核心竞争力。
Demmel 本人既是算法理论家（特征值**相对精度**理论的奠基者），又是 LAPACK/ScaLAPACK 的核心开发者，
这让全书始终在「数学最优」与「机器最优」之间做权衡——这正是「应用数学研究型工程师」需要的能力。

一句话定位：本书是 stage-3 §3B 数值方向的核心教材，与 [trefethen 数值线代]（同期生成）互补
——Trefethen 是入门直觉版（概念第一），Demmel 是工程纵深版（复杂度 + 并行第一）。

全书三轴贯穿始终：

- **精度轴**——条件数 $\kappa$、向后稳定性、Eckart-Young 低秩逼近；
- **速度轴**——算术复杂度 $O(n^3)$ vs $O(n^2)$ vs $O(n)$、Level 3 BLAS 的 cache 复用；
- **并行轴**——分块算法（block algorithm）、分布式数据布局、负载均衡。

每章都追问同一个核心问题：「这个算法在真实机器上能跑多快多准？」
飞腾锚点把这三轴钉到工程肉身：FP16 对应精度轴、matmul/GEMM 对应速度轴、TLB 对应并行轴。

附录给出线性代数与浮点运算的基础回顾（向量/矩阵范数、谱定理、IEEE 754），已在精度轴的讨论中带过，此处不单列章节。

### 四本数值线代教材对比

| 书 | 风格 | 严格性 | 适合谁 |
|:---|:-----|:------|:------|
| **Demmel（本书）** | 算法 + 复杂度 + 并行三轴综合 | 理论 + 工程双线（定理配 LAPACK 接口） | 想理解「为什么 LAPACK 这样写」的研究生/工程师 |
| **Trefethen-Bau** | 概念直觉优先，极简讲座体 | 严格但选择性（只讲核心思想） | 初学者建立直觉、快速入门 |
| **Golub-Van Loan** | 百科全书式，4 级分块统一记号 | 最全面但章节密集，当手册用 | 研究者案头参考、按需查阅 |
| **Higham** | 纯 backward error 分析，逐算法拆解 | 分析味最浓，证明最细 | 专攻精度/稳定性理论的研究者 |

> **阅读策略**：Trefethen 建立直觉（概念第一） → **Demmel 工程纵深（复杂度 + 并行第一）**
> → Golub-Van Loan 当手册查（广度第一）→ Higham 锐化精度理论。

---

## §1 全书 6 章骨架一览（飞腾锚点分布）

| 章 | 标题 | 核心概念 | 飞腾锚点 |
|:--:|:-----|:--------|:--------|
| 1 | Introduction | BLAS 三级、浮点、条件数、总纲不等式 | FP16 3.81× ⭐ |
| 2 | Linear Equation Solving | LU、选主元、稳定性、条件数估计、迭代精化 | matmul 15× ⭐ |
| 3 | Linear Least Squares | QR、SVD、正规方程、Eckart-Young、扰动 | Schmidt 正交化 |
| 4 | Nonsymmetric Eigenvalue | Hessenberg、QR 算法、Schur 分解、QZ | 分支预测 |
| 5 | Symmetric Eigenvalue & SVD | Jacobi、分治、二分、相对精度 | GEMM 9.45G ⭐ |
| 6 | Iterative Methods | CG、GMRES、预条件、并行实现 | TLB 4.81× ⭐ |

```
第1章 引言(BLAS/浮点/κ)── 三级 BLAS: cache 复用决定性能 ──────────────┐
第2章 线性方程组(LU/选主元)── 直接法 O(n³), 分块 LU = GEMM ────────────┤
第3章 最小二乘(QR/SVD)── 正规方程 κ² vs QR 稳定, Eckart-Young ────────┤  精度×速度
第4章 非对称特征值(QR算法/Schur)── Hessenberg 化 + 移位 QR 收敛 ─────┤  ×并行
第5章 对称特征值& SVD(Jacobi/分治)── 相对精度, Demmel 招牌 ──────────┤  三轴统一
第6章 迭代法(CG/GMRES/预条件)── Krylov 子空间, 大规模稀疏并行 ────────┘

总纲: 前向误差 ≤ 后向误差 × κ  ——  贯穿全书所有误差分析的「宪法」
```

---

### 第 1 章 · Introduction 引言

- **核心**：全书总纲章，建立三大基石。
  ① **BLAS 分级**：Level 1（向量-向量 $O(n)$）、Level 2（矩阵-向量 $O(n^2)$）、
  Level 3（矩阵-矩阵 $O(n^3)$）——Level 3 因 cache 复用率最高而性能最优，
  这是分块算法（block algorithm）的动机根源，也是 LAPACK 区别于 LINPACK 的根本。
  ② **浮点算术**：IEEE 754 标准、机器精度 $\epsilon_{\text{mach}}$、
  基本模型 $\text{fl}(a\circ b)=(a\circ b)(1+\delta)$，$|\delta|\le\epsilon_{\text{mach}}$。
  ③ **条件数与总纲不等式**：前向误差 $\le$ 后向误差 $\times\,\kappa$
  ——这一条公式贯穿全书所有误差分析，是 Demmel 反复回到的「宪法」。
- **飞腾锚点**：**FP16 3.81× [L01]** ⭐（数值精度）🟢。
  Demmel 在引言即强调浮点格式决定精度边界——FP16 的 $\epsilon_{\text{mach}}\approx9.8\times10^{-4}$
  比 FP64 的 $2.2\times10^{-16}$ 粗约 12 个数量级。
  总纲不等式中，FP16 的后向误差本身就大 $10^{12}$ 倍，
  病态问题（$\kappa>10^3$）在 FP16 下完全失效。
  混合精度算法（FP16 算 + FP64 校正）是 Demmel 后续工作的延伸——3.81× 加速是诱饵，精度边界是代价。
- **关键定理**：**总纲误差界**——若算法向后稳定（后向误差 $\|\Delta A\|\le O(n\epsilon_{\text{mach}})\|A\|$），则解的前向相对误差满足
$$\frac{\|\Delta x\|}{\|x\|}\le O(n\epsilon_{\text{mach}})\,\kappa(A)$$
$\kappa$ 大则输入微小扰动被巨幅放大——这是「病态（ill-conditioned）」的精确定义，与算法好坏无关。
- **自测**：$A=\begin{pmatrix}1&1\\1&1.0001\end{pmatrix}$，$\kappa(A)\approx4\times10^4$。
  用 FP64（$\epsilon\approx2.2\times10^{-16}$）和 FP16（$\epsilon\approx10^{-3}$）各解 $Ax=b$，$b=(2,2.0001)^T$，
  总纲不等式给出的前向误差界分别是多少？
  （提示：FP64 下 $\sim10^{-11}$ 安全；FP16 下 $\sim40$——完全失效，FP16 解无意义。）

---

### 第 2 章 · Linear Equation Solving 线性方程组求解

- **核心**：解 $Ax=b$ 的直接法全谱系。
  ① **LU 分解** $PA=LU$（部分选主元），复杂度 $\frac{2}{3}n^3+O(n^2)$；
  选主元确保 $|l_{ij}|\le1$，但增长因子 $\rho=\frac{\max|u_{ij}|}{\max|a_{ij}|}$ 理论可达 $2^{n-1}$（最坏）。
  ② **稳定性**：部分选主元 LU 实践中向后稳定，$\|\hat L\|\|\hat U\|\le O(n)\|A\|$ 几乎总成立（最坏理论界远差于此）。
  ③ **条件数估计**：Hager 算法（LAPACK `xLACON`）只需 $O(n^2)$ 而非精确求 $\|A^{-1}\|$ 的 $O(n^3)$。
  ④ **迭代精化**：$x\leftarrow x+\hat A^{-1}(b-Ax)$ 一步可把精度提升到接近机器精度。
  ⑤ **分块 LU**：把 LU 改写为 Level 3 BLAS（GEMM）以利用 cache——高性能实现的核心。
- **飞腾锚点**：**matmul 15× [V03]** ⭐（LU 的 GEMM 内核）🟢。
  分块 LU 把消元切成 $b\times b$ 子块，核心运算是子块三角求解 + 矩阵乘（GEMM）——这正是 matmul。
  飞腾 NEON GEMM 经循环重排 + 向量化达 15× 加速，$n=1000$ 的 LU 从分钟级降到秒级。
  Demmel 反复强调「算法必须重写为 Level 3 BLAS 形式才有竞争力」
  ——这是 LAPACK 区别于 LINPACK（仅 Level 1）的根本设计决策。
- **关键定理**：**选主元 LU 稳定性界**——部分选主元 LU 满足 $\hat A+\Delta A=\hat L\hat U$，其中
$$\|\Delta A\|\le n\epsilon_{\text{mach}}\,\|\hat L\|\,\|\hat U\|$$
若增长因子 $\rho$ 有界，则 $\|\hat L\|\|\hat U\|\le O(n)\|A\|$（实践中几乎总成立），LU 向后稳定。
最坏情况下 $\rho=2^{n-1}$ 使该界退化——这是「部分选主元理论上不保证稳定」的根源。
- **自测**：① $A=\begin{pmatrix}10^{-20}&1\\1&1\end{pmatrix}$，分别用不选主元和部分选主元做 LU，
  解 $Ax=(1,2)^T$，比较结果精度。
  ② 对 Wilkinson 反例矩阵（$w_{ij}=-1$ if $i>j$，其余 $1$），$n=5$ 手算部分选主元 LU，
  验证 $\max|u_{ij}|$ 远大于 $\max|a_{ij}|=1$。

---

### 第 3 章 · Linear Least Squares Problems 线性最小二乘

- **核心**：超定系统 $\min_x\|Ax-b\|_2$（$A\in\mathbb{R}^{m\times n}$，$m\ge n$）的三条解路。
  ① **正规方程** $A^TAx=A^Tb$——简单但 $\kappa(A^TA)=\kappa(A)^2$，条件数**平方放大**，数值危险。
  ② **QR 分解** $A=QR$（Householder 反射），解 $Rx=Q^Tb$——$\kappa$ 不放大，数值稳定，是 LAPACK 默认方法。
  ③ **SVD** $A=U\Sigma V^T$，解 $x=V\Sigma^+U^Tb$（伪逆）——最稳且自动处理秩亏损。
  ④ **扰动理论**：解的敏感度由 $\kappa(A)$ 和残差共同支配，残差小时 $\sim\kappa$，残差大时 $\sim\kappa^2$（平方效应再现）。
  ⑤ **Eckart-Young**：SVD 给出 Frobenius 范数和谱范数下的最优低秩逼近。
- **飞腾锚点**：**Schmidt 正交化**（QR 分解的数学内核）🟢。
  QR 分解本质是正交化——Householder 反射是比经典 Gram-Schmidt 更数值稳定的正交化手段
  （避免「逐步失去正交性」的经典 GS 病态）。
  改进 Gram-Schmidt + 一步迭代精化可达 Householder 级精度。
  QR 是最小二乘的稳定基石，也是第 4 章 Hessenberg 化、第 6 章 Arnoldi 过程的共用工具。
  AI 锚点：**PyTorch `torch.linalg.qr`** 用于正交初始化和 RNN 梯度稳定性。
- **关键定理**：**Eckart-Young 低秩逼近定理**——设 $A=U\Sigma V^T$，$\sigma_1\ge\cdots\ge\sigma_r>0$，取前 $k$ 个分量 $A_k=\sum_{i=1}^k\sigma_i u_iv_i^T$，则
$$A_k=\arg\min_{\text{rank}(B)\le k}\|A-B\|_F=\arg\min_{\text{rank}(B)\le k}\|A-B\|_2$$
且 $\|A-A_k\|_2=\sigma_{k+1}$。这是 PCA 降维、推荐系统矩阵分解、神经网络压缩（低秩分解）的数学根基。
- **自测**：① $A=\begin{pmatrix}1&1\\1&2\\1&3\end{pmatrix}$，$b=(1,2,2)^T$。
  分别用正规方程（$A^TA$）和 QR 分解求最小二乘解，比较精度。
  ② 对上述 $A$ 做 SVD，验证秩 1 最佳逼近 $A_1$ 满足 $\|A-A_1\|_F=\sigma_2$。

---

### 第 4 章 · Nonsymmetric Eigenvalue Problems 非对称特征值问题

- **核心**：求 $Ax=\lambda x$（$A$ 一般方阵）的工业级算法，是数值线代中最精巧的章节。
  ① **Schur 分解** $A=QTQ^H$（$T$ 上三角，$Q$ 酉）——特征值是 $T$ 对角元，是所有非对称特征值计算的理论终点与目标。
  ② **Hessenberg 化**——先用 Householder 把 $A$ 约化为上 Hessenberg 阵（$h_{ij}=0$ 当 $i>j+1$），
  代价 $\frac{10}{3}n^3$，使后续 QR 迭代每步只需 $O(n^2)$ 而非 $O(n^3)$。
  ③ **QR 算法**——对 Hessenberg 阵反复做带移位的 QR 分解 $H_k-\mu I=Q_kR_k$，$H_{k+1}=R_kQ_k+\mu I$，
  $H_k\to T$ 收敛到 Schur 形式。
  ④ **Francis 双移位**技巧处理实矩阵的复特征对（避免复运算）。
  ⑤ **QZ 算法**解广义特征值 $Ax=\lambda Bx$（推广到矩阵束 $A-\lambda B$）。
- **飞腾锚点**：**分支预测 0.71 vs 3.14 [Lab02]**（Schur 收缩与分裂）🟢。
  QR 算法的收敛过程是「子问题逐步分裂」——当某个次对角元 $|h_{i,i-1}|$ 足够小
  （$<\epsilon(|h_{ii}|+|h_{i+1,i+1}|)$），矩阵分裂为两个独立子问题，递归处理。
  这个「检测收敛 → 分割 → 递归」是数据依赖的条件分支，分支预测器无法预测下次分裂发生在哪个位置。
  Schur 分解后按模排序特征值也涉及分支交换。
  飞腾实测分支密集代码 IPC 仅 0.71 vs 理论 3.14——QR 算法的实际效率被不可预测分支拖累。
- **关键定理**：**QR 算法收敛性**——对不可约上 Hessenberg 阵，带 Wilkinson 移位的 QR 算法
  使最后那个次对角元**三次收敛**（$|h_{n,n-1}^{(k)}|\to0$），速度正比于移位后相邻特征值之比的立方。
  总复杂度：Hessenberg 化 $O(n^3)$ + 每步 QR 迭代 $O(n^2)$ + 总迭代步数 $O(n)$（平均每个特征值约 2-3 步）$\Rightarrow$ 全特征值 $O(n^3)$。
- **自测**：① $A=\begin{pmatrix}2&1\\1&0\end{pmatrix}$（特征值 $1\pm\sqrt2$），从 $A$ 出发做 3 步**无移位** QR 迭代
  （$A=Q_1R_1$，$A_1=R_1Q_1$，……），观察次对角元是否缩小？
  ② 说明上 Hessenberg 形式在 QR 迭代下保持不变（$H$ 的 QR 因子 $Q,R$ 满足 $RQ$ 仍 Hessenberg）。

---

### 第 5 章 · Symmetric Eigenvalue Problems and SVD 对称特征值与 SVD

- **核心**：$A=A^T$ 的特征值问题享有特殊结构——特征值全实、特征向量正交、$A=Q\Lambda Q^T$。四大算法各擅胜场。
  ① **Jacobi 方法**——用一系列旋转 $J^TAJ$ 逐步消去最大非对角元，古老但精度极高（可达到相对精度）。
  ② **对称 QR**——先三对角化 $A\to T$（Householder），再对三对角阵做带 Wilkinson 移位的隐式 QR，每步 $O(n^2)$。
  ③ **分治法（Cuppen）**——把三对角阵 $\begin{pmatrix}T_1&\beta v\\\beta v^T&T_2\end{pmatrix}$ 分成两半递归解，
  用秩一修正缝合，总复杂度 $O(n^{2.3})$，是 LAPACK 默认（`xsyevd`）。
  ④ **二分法 + 反迭代**——用 Sturm 序列（三对角阵符号计数）隔离特征值，反迭代求特征向量，适合只求部分特征值。
  ⑤ **相对精度（Demmel 招牌）**——Demmel-Veselić 证明对称正定问题的特征值可计算到**相对精度** $O(\epsilon)$
  而非绝对精度 $O(\epsilon\|A\|)$——即使最小特征值也有相对保证。
  ⑥ SVD 可化为对称特征值问题或用 Golub-Kahan 双对角化后对双对角阵做隐式 QR。
- **飞腾锚点**：**GEMM 9.45 GFLOPS [Lab05]** ⭐（工业级特征值 / SVD）🟢。
  三对角化 $A=QTQ^T$ 的核心运算是 $Q^TAQ$——标准 GEMM。
  分治法的秩一修正缝合 $V(\Lambda+\rho vv^T)V^T$ 也依赖矩阵乘。
  工业级 SVD（推荐系统 $10^6\times10^6$ 矩阵分解、PageRank 谱分析）用随机化 + 分块 GEMM 加速。
  飞腾 GEMM 9.45 GFLOPS 决定了 $n=10^3$ 全特征值计算从小时级降到分钟级。
  AI 锚点：**TensorFlow `tf.linalg.svd`** / PyTorch `torch.linalg.svd`
  用于推荐系统 ALS、谱归一化（spectral norm）、PCA 白化。
- **关键定理**：**对称特征值扰动（Weyl 不等式 + 相对精度）**——设 $A=A^T$，$\tilde A=A+\delta A$，则按序特征值满足
$$|\tilde\lambda_i-\lambda_i|\le\|\delta A\|_2 \quad\text{（Weyl，绝对界）}$$
**更强地**（Demmel-Veselić），若 $A$ 对称正定，存在算法使特征值可达**相对精度**：
$$|\tilde\lambda_i-\lambda_i|\le O(n\epsilon)\,\lambda_i,\quad\forall\,i$$
即使最小特征值 $\lambda_{\min}$ 也有 $O(n\epsilon)$ 相对误差——这是一般矩阵做不到的「免费午餐」。
- **自测**：① $A=\begin{pmatrix}2&1\\1&2\end{pmatrix}$（特征值 1, 3），
  用 Jacobi 旋转 $J=\begin{pmatrix}\cos\theta&-\sin\theta\\\sin\theta&\cos\theta\end{pmatrix}$
  （$\tan2\theta=\frac{2a_{12}}{a_{11}-a_{22}}$）消去 $a_{12}$，验证一步即对角化。
  ② 同一矩阵加扰动 $\delta A=10^{-6}I$，Weyl 不等式给出 $|\tilde\lambda_i-\lambda_i|\le10^{-6}$，验证。

---

### 第 6 章 · Iterative Methods for Linear Systems 线性方程组迭代法

- **核心**：当 $n>10^4$，直接法 $O(n^3)$ 不可行（存储 + 时间），改用迭代法
  （每步只需一次矩阵-向量乘 $O(n^2)$ 或稀疏时 $O(\text{nnz})$）。
  ① **CG（共轭梯度）**——$A$ 对称正定时的最优方法，在 Krylov 子空间 $\mathcal{K}_k=\text{span}\{b,Ab,\ldots,A^{k-1}b\}$
  上最小化 $A$-范数误差，最多 $n$ 步精确收敛。
  ② **GMRES**——$A$ 一般非对称时，最小化残差 $\|r_k\|_2$ 于 Krylov 子空间，
  但存储量随步数线性增长（实际用重启 GMRES($m$)）。
  ③ **BiCGStab / QMR / TFQMR**——双共轭梯度族，避免 GMRES 存储爆炸但牺牲最优性。
  ④ **预条件（preconditioning）**——解 $M^{-1}Ax=M^{-1}b$（$\kappa(M^{-1}A)\ll\kappa(A)$），
  是不完全 Cholesky / ILU、区域分解、多重网格的核心思想。
  ⑤ **并行实现**——SpMV（稀疏矩阵-向量乘）的通信开销是并行瓶颈。
  ⑥ **迭代法与特征值的联系**：CG/GMRES 的收敛速度由 $A$ 的谱分布（条件数 / 特征值聚集度）决定。
- **飞腾锚点**：**TLB 4.81× [E04]** ⭐（稀疏矩阵 cache-blocking）🟢。
  迭代法核心运算 SpMV $y=Ax$（$A$ 稀疏）是典型不规则访存——非零元分布不规则，TLB 缺失严重。
  cache-blocking（把稀疏矩阵分块存入连续内存，如 CSR → BCSR）把 TLB 命中率提升 4.81×。
  预条件子的不完全分解也需分块存储。
  并行实现中，进程间通信延迟 $\gg$ 计算，负载均衡 + 通信最小化是并行 CG/GMRES 的工程核心。
  AI 锚点：**CG 用于 Hessian-free 二阶优化**（大模型训练，避免显式存 Hessian），
  **GMRES 用于非对称 Jacobi 系统**（牛顿-Krylov 方法）。
- **关键定理**：**CG 收敛界（$A$-范数）**——设 $A$ 对称正定，$\kappa=\lambda_{\max}/\lambda_{\min}$，令 $\rho=\frac{\sqrt\kappa-1}{\sqrt\kappa+1}<1$，则 CG 第 $k$ 步误差满足
$$\|x_k-x^\ast\|_A\le 2\rho^{\,k}\,\|x_0-x^\ast\|_A$$
即约 $\sqrt\kappa$ 步内误差减小 $e^{-1}$ 倍（精确算术下 $\le n$ 步终结）。预条件降 $\kappa$ 直接加速收敛——这是预条件的量化动机。
- **自测**：① $A=\text{diag}(1,100)$（$\kappa=100$），$b=(1,1)^T$。用 CG 从 $x_0=0$ 做 2 步，
  验证 $x_2=x^\ast$（CG $\le n=2$ 步精确收敛）。
  ② 用 Jacobi 预条件 $M=\text{diag}(A)$，预条件后 $\kappa(M^{-1}A)=1$，
  CG 一步收敛——预条件把 $n$ 步压到 1 步。

---

## §9 全书思想主线：精度 × 速度 × 并行三轴统一

Demmel 全书的灵魂可浓缩为一个核心追问：
「**给定一台真实机器，一个矩阵算法能跑多快多准？**」
围绕这一追问，6 章形成清晰的三轴结构。

**精度轴**（条件数 $\kappa$）：第 1 章建立总纲不等式「前向误差 $\le$ 后向误差 $\times\kappa$」，
此后每章都在回答「这个算法的后向误差多大、这个问题的 $\kappa$ 多大」。
第 2 章 LU 的选主元稳定性 $\|\Delta A\|\le O(n\epsilon)\|A\|$（$\rho$ 有界时）、
第 3 章 Eckart-Young 最优低秩逼近、
第 5 章对称问题的**相对精度**（Demmel 招牌）——都是精度轴的不同切面。

**速度轴**（算术复杂度 + BLAS 分级）：Demmel 始终追问「这个算法能否重写为 Level 3 BLAS？」
分块 LU（第 2 章）、分块 QR（第 3 章）、分块 Hessenberg 化（第 4 章）、三对角化的 GEMM 内核（第 5 章）
——都是把 $O(n^3)$ 算法重写成 cache 友好的分块形式。
飞腾 matmul 15× / GEMM 9.45 GFLOPS 正是这一轴的工程体现。

**并行轴**（分布式 + 通信）：第 6 章迭代法的 SpMV 通信瓶颈、TLB 4.81× 的 cache-blocking、
预条件的并行可扩展性——把「单机最优」推到「分布式最优」。
这与 [nocedal_wright 数值优化] 的 L-BFGS 大规模优化、[Nesterov 凸优化] 的复杂度下界遥相呼应：
Nocedal 问「收敛几步」，Demmel 问「每步几秒」。

三轴的统一判据是**「精度 × 速度」的 Pareto 前沿**：
精度要求高时选 SVD（第 3 章），速度要求高时选迭代法（第 6 章），
兼有时选分块 QR + 预条件 CG。
这正是「应用数学研究型工程师」的核心判断力——不是会用 `numpy.linalg.solve`，
而是知道**在什么条件下用什么方法、为什么**。

---

## §10 交叉引用与飞腾锚点速查

### 与路径其他书的交叉

| 本书概念 | 关联书 / 方向 | 接口 |
|:--------|:------------|:-----|
| LU / QR / SVD 直接法 | **[trefethen 数值线代]**（同期生成） | Trefethen 讲概念直觉，Demmel 讲复杂度 + 并行 + LAPACK 接口，互补 |
| 迭代法 CG / GMRES | **[nocedal_wright 数值优化]** Ch5 CG | NW 的 CG 是优化的 Krylov 视角，Demmel 是 $Ax=b$ 的数值线代视角 |
| 条件数 / 稳定性 / 误差传播 | **[kress 数值分析 GTM181]** Ch1 | Kress 是全数值分析（线代 → PDE），Demmel 专攻线代纵深 |
| QR 分解 / Householder | **[hoffman_kunze 线性代数]** | HK 讲线性代数的纯数学，Demmel 讲数值实现与稳定性 |
| 复杂度 / 收敛率 | **[Nesterov 凸优化]** | Nesterov 的复杂度下界 → Demmel 的算法可达性验证 |
| SVD / 矩阵计算手册 | **[golub_van_loan]** | GVL 百科全书（当手册查），Demmel 教材（当课本读） |

### AI / 工程锚点（数值线代 = 深度学习底层）

| 算法 / 概念 | AI / 工程落地 |
|:---------|:------------|
| **SVD 降维 / PCA**（第 3 章） | 推荐系统矩阵分解（ALS）、数据白化、模型低秩压缩 |
| **cuBLAS / cuSOLVER**（第 1-2 章） | GPU 上 BLAS/LAPACK 实现，PyTorch 底层所有矩阵运算 |
| **CG 二阶优化**（第 6 章） | Hessian-free training（大神经网络二阶方法，避免存 Hessian） |
| **Hessian-vector product**（第 5-6 章） | 影响函数（influence function）、Hessian 谱分析（泛化研究） |
| **混合精度 / FP16**（第 1 章） | 混合精度训练（NVIDIA Tensor Core）、量化推理 |
| **tf.linalg.eig / svd**（第 4-5 章） | TensorFlow / PyTorch 谱归一化（GAN 稳定性）、PCA |

### 飞腾锚点速查（每章 1 个，共 6 个）

| 锚点 | 章节 | 主题 |
|:-----|:-----|:-----|
| **FP16 3.81× ⭐** | Ch1 | 浮点精度 / 混合精度 / 总纲误差界 |
| **matmul 15× ⭐** | Ch2 | LU 分解的 GEMM 内核 / 分块算法 |
| **Schmidt 正交化** | Ch3 | QR 分解 / Householder 反射 |
| **分支预测** | Ch4 | QR 算法 Schur 收缩 / Hessenberg 分裂 |
| **GEMM 9.45G ⭐** | Ch5 | 三对角化 / 分治法 / 工业级 SVD |
| **TLB 4.81× ⭐** | Ch6 | SpMV cache-blocking / 稀疏矩阵 / 并行 |

---

> **下一步**：精读 Demmel 第 2 章（LU 稳定性 + 条件数估计，飞腾 matmul 锚点）
> + 第 3 章（QR / SVD + Eckart-Young，PCA 降维的数学根基）
> + 第 6 章（CG 收敛界，Hessian-free 二阶优化）；
> 研究选题「**飞腾无 BF16 硬件下混合精度 SVD 的相对精度退化**」
> ——当 FP16 舍入破坏 Demmel-Veselić 相对精度条件（第 5 章），奇异值最小分量的相对误差退化多少？
> 能否用迭代精化补偿？衔接 [trefethen]（同期）第 7/8 章概念侧 + [nocedal_wright] 第 5 章 CG 优化侧。
