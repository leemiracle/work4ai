# Gene H. Golub, Charles F. Van Loan《矩阵计算》 · 快速逐章精读

> 基于原书：*Matrix Computations*（Gene H. Golub & Charles F. Van Loan, 4th ed., Johns Hopkins University Press, 2013）/ 读于：2026-07-03
> 定位：**数值线性代数领域的「圣经」级百科手册**，12 部分覆盖从矩阵乘法到随机化方法的全谱系，LAPACK / NumPy / PyTorch `torch.linalg` 的算法蓝本。
> 本文为**快速逐章精读**，12 部分（Part）各 1 个飞腾锚点 + 1 个关键定理 + 1 道自测题。
> 关联：[trefethen 数值线代]（直觉版）· [demmel 应用数值线代]（工程版）· [nocedal_wright 数值优化] · [Nesterov 凸优化] · [Hoffman-Kunse 线性代数]

---

## §0 引言：Golub-Van Loan 是数值线代的「百科全书」

Gene H. Golub（Stanford，SVD 计算、正则化、随机化方法的先驱）与 Charles F. Van Loan
（Cornell，矩阵计算记号体系的奠基者）合著的《Matrix Computations》（初版 1983，第四版 2013）
是**数值线性代数领域引用最高的百科全书式参考书**——
全书 12 部分约 750 页，从最基本的矩阵-向量乘法一路讲到大规模稀疏求解、矩阵函数、张量分解与随机化方法，
几乎每一个现代矩阵算法都能在此找到原始描述或关键引文。

一句话定位：本书是 stage-3 §3B 数值方向的**终极手册**，
与刚完成的 [trefethen 数值线代]（直觉先行、40 讲建立概念骨架）
和 [demmel 应用数值线代]（算法 + 复杂度 + 并行三轴）构成**数值线代三套**——
Trefethen 是入门读物（当课本读），Demmel 是工程教材（理解「为何这样设计」），
Golub-Van Loan 是百科手册（按需查阅算法细节）。

GVL 的最大特色是**统一记号 + 全谱系覆盖 + 算法伪代码**：
全书采用自创的 4 级分块矩阵记号（如 $A_{ij}$ 表示分块），
每个算法都给出可实现的伪代码（带 flop 计数），
并标注其在 LAPACK 中的对应例程名（如 `dgesdd`、`dposv`、`dsyevd`）。
读完本书，读者面对任何 `numpy.linalg` / `torch.linalg` 调用都能追溯到底层算法的每一步。
全书逻辑主线是「**从稠密到稀疏、从精确到迭代、从小规模到大规模**」：
Part 1-9 是稠密直接算法（$O(n^3)$），Part 10-11 是稀疏迭代算法（Krylov 子空间），
Part 12 是前沿专题（张量、随机化）。

### 四本数值线代教材对比

| 书 | 风格 | 严格性 | 适合谁 |
|:---|:-----|:------|:------|
| **Golub-Van Loan（本书）** | 百科全书式，统一分块记号 + 伪代码 + flop 计数 | 极全（覆盖最广，算法细节最详） | 需查阅具体算法细节的从业者 / 研究者案头手册 |
| **Trefethen-Bau** | 直觉先行，40 讲精炼，几何驱动 | 中高（侧重直觉与核心洞察） | 初入数值线代的研究生 / AI 工程师建骨架 |
| **Demmel** | 算法 + 复杂度 + 并行三轴综合 | 高（理论 + LAPACK 接口双线） | 想理解「LAPACK 为何这样写」的工程师 |
| **Higham《Functions of Matrices》** | 矩阵函数 + 精度分析纵深 | 极高（GVL Part 9 的专精扩展） | 专攻矩阵函数 / 精度理论的专家 |

> **阅读策略**：Trefethen 建直觉 → Demmel 补工程细节 → **Golub-Van Loan 当手册按需查** → Higham 深挖矩阵函数。
> 三套互补：先「看见森林」（TB），再「种好每棵树」（Demmel），最后「拥有一座植物园目录」（GVL）。

---

## §1 全书 12 部分骨架一览（飞腾锚点分布）

| 部分 | 标题 | 核心概念 | 飞腾锚点 |
|:----:|:-----|:--------|:--------|
| 1 | Matrix Multiplication 矩阵乘法 | GEMM、Strassen、cache-blocking、BLAS 分级 | matmul 15× ⭐ |
| 2 | Matrix Analysis 矩阵分析 | 范数、条件数、SVD 存在性、子空间 | UDOT 16.9× ⭐ |
| 3 | General Linear Systems 一般线性方程组 | LU 选主元、Cholesky、向后稳定性、迭代精化 | Iron Law <2% ⭐ |
| 4 | Special Linear Systems 特殊线性方程组 | Toeplitz、Vandermonde、banded、对称不定 | TLB 4.81× ⭐ |
| 5 | Orthogonalization & Least Squares 正交化与最小二乘 | Householder、Givens、QR、SVD 伪逆 | Schmidt 正交化 ⭐ |
| 6 | Modified Least Squares 修正最小二乘 | QR 更新、秩一修正、行/列增删 | GEMM 9.45G ⭐ |
| 7 | Unsymmetric Eigenvalue 非对称特征值 | QR 算法、Schur 形、Hessenberg、不变子空间 | 分支预测 ⭐ |
| 8 | Symmetric Eigenvalue 对称特征值 | Jacobi、三对角化、分治、SVD 计算 | matmul 15× ⭐ |
| 9 | Functions of Matrices 矩阵函数 | 指数、Padé、Schur-Parlett、矩阵符号 | FP16 3.81× ⭐ |
| 10 | Large Sparse Eigenvalue 大规模稀疏特征值 | Lanczos、Arnoldi、Krylov 子空间、breakdown | Schmidt 正交化 ⭐ |
| 11 | Large Sparse Linear Systems 大规模稀疏线性方程组 | CG、GMRES、MINRES、预条件 | TLB 4.81× ⭐ |
| 12 | Special Topics 专题 | 张量分解、随机化 SVD、低秩逼近 | GEMM 9.45G ⭐ |

---

### Part 1 · Matrix Multiplication 矩阵乘法

- **核心**：全书最根本的操作。矩阵乘 $C=AB$（$A\in\mathbb{R}^{m\times p}$，$B\in\mathbb{R}^{p\times n}$）
  朴素代价 $2mnp$ flops（$n\times n$ 时 $\sim2n^3$）。GVL 讨论三条加速路线：
  ① **BLAS 分级**——Level 1（向量-向量 $O(n)$）、Level 2（矩阵-向量 $O(n^2)$），
  Level 3（矩阵-矩阵 $O(n^3)$ = GEMM）因 cache 复用率最高而性能最优，
  这是 LAPACK 区别于 LINPACK 的根本设计。
  ② **分块算法**（tile/block）：把大矩阵切为 $b\times b$ 子块，使每个子块乘法在 L1/L2 cache 内完成。
  ③ **Strassen 算法**：递归地将 $n\times n$ 矩阵切成 $2\times 2$ 分块，
  用 7 次（而非朴素 8 次）子矩阵乘法完成，递归深度 $\log_2 n$。
- **飞腾锚点**：**matmul 15× [V03]** ⭐（矩阵乘法向量化）🟢。
  GEMM 是所有数值线代算法的底层燃料——SVD、QR、特征值分解的 $O(n^3)$ 成本中 GEMM 占 90%+。
  飞腾 D3000M 经循环重排 + NEON 向量化达 15× 加速，
  $n=10^4$ 的乘法从小时级降到分钟级。
  GVL 强调「凡能写成 GEMM 形式的算法才有竞争力」，这正是 LAPACK 分块设计的动机根源。
- **关键定理**：**Strassen 复杂度**。
  将 $n\times n$ 矩阵乘分解为 7 个 $\frac{n}{2}\times\frac{n}{2}$ 子矩阵乘加（S1-S7 公式），
  递归得 $T(n)=7T(n/2)+O(n^2)\Rightarrow O(n^{\log_2 7})=O(n^{2.807})$，
  比朴素 $O(n^3)$ 快，但常数大且数值稳定性略差（向后误差仍 $O(\epsilon)$ 但常数增大），
  实践中 $n\gtrsim100$ 才有优势。
- **自测**：朴素 $4\times4$ 矩阵乘需多少次乘法？
  Strassen 把 $4\times4$（= 2 层递归）分解为多少次 $1\times1$ 乘法？
  （答：朴素 $4^3=64$ 次；Strassen 两层 $7^2=49$ 次，节省 $23\%$。）

---

### Part 2 · Matrix Analysis 矩阵分析

- **核心**：为后续所有算法建立分析语言。
  ① **范数**：向量 $\ell^p$ 范数、矩阵诱导范数 $\|A\|=\max_{\|x\|=1}\|Ax\|$、
  Frobenius 范数 $\|A\|_F=\sqrt{\sum_{ij}|a_{ij}|^2}$；关键性质 $\|AB\|\le\|A\|\|B\|$。
  ② **SVD 存在性**：任何 $A=U\Sigma V^*$（$U,V$ 正交，$\Sigma$ 对角非负），
  奇异值 $\sigma_1\ge\cdots\ge\sigma_r>0$ 揭示矩阵的「几何骨架」
  （旋转 $V^*$ → 缩放 $\Sigma$ → 旋转 $U$）。
  ③ **条件数** $\kappa(A)=\sigma_{\max}/\sigma_{\min}$。
  ④ **四个基本子空间** $\mathcal{R}(A)$、$\mathcal{N}(A)$、$\mathcal{R}(A^*)$、$\mathcal{N}(A^*)$，
  及正交分解 $\mathbb{R}^n=\mathcal{R}(A^*)\oplus\mathcal{N}(A)$。
- **飞腾锚点**：**UDOT 16.9× [E05]** ⭐（向量内积 / 范数计算）🟢。
  范数 $\|x\|_2=\sqrt{x^*x}$ 本质是内积；Frobenius 范数是全体元素平方和。
  奇异值计算涉及 $A^*A$ 的特征值（$\sigma_i^2$），每步大量点积累加。
  飞腾 INT8 UDOT 点积指令达 16.9× 加速。
  AI 锚点：**PyTorch `torch.linalg.norm`** 底层即批量内积。
- **关键定理**：**SVD 存在性与极值**。
  $\forall A\in\mathbb{R}^{m\times n}$，存在正交 $U,V$ 使 $A=U\Sigma V^*$，且
  $\|A\|_2=\sigma_1$，$\|A\|_F=(\sum\sigma_i^2)^{1/2}$，$\kappa(A)=\sigma_1/\sigma_r$。
  SVD 是全书核心分解——Part 5 的最小二乘、Part 8 的对称特征值、Part 12 的低秩逼近都建立在它之上。
- **自测**：$A=\begin{pmatrix}3&0\\0&2\end{pmatrix}$，写出 SVD，求 $\|A\|_2$、$\|A\|_F$、$\kappa(A)$。
  （答：$U=I,\Sigma=\text{diag}(3,2),V=I$；$\|A\|_2=3$；$\|A\|_F=\sqrt{13}$；$\kappa=3/2$。）

---

### Part 3 · General Linear Systems 一般线性方程组

- **核心**：解 $Ax=b$ 的直接法全谱系，全书最实用的章节。
  ① **LU 分解** $PA=LU$（部分选主元），复杂度 $\frac{2}{3}n^3$；选主元确保乘子 $|l_{ij}|\le1$。
  ② **向后稳定性**：浮点结果满足 $(A+\Delta A)\hat{x}=b$，
  $\|\Delta A\|\le O(n^3\epsilon)\|A\|$（Wilkinson 经典界，增长因子 $\rho$ 有界时远优于此）。
  ③ **Cholesky 分解** $A=LL^*$（SPD），无需选主元即稳定，代价 $\frac{1}{3}n^3$（比 LU 快 2 倍）。
  ④ **迭代精化** $x\leftarrow x+A^{-1}(b-Ax)$ 一步提升到接近机器精度。
  ⑤ **条件数估计**（Hager 算法，$O(n^2)$）。⑥ **分块 LU**：核心运算是 GEMM，利用 cache。
- **飞腾锚点**：**Iron Law <2% [Lab00]** ⭐（向后稳定的误差上限）🟢。
  向后稳定性是 Part 3 的灵魂：稳定算法精确求解了某个邻近问题（$\|\Delta A\|=O(\epsilon)\|A\|$），
  对应 Iron Law 的 <2% 误差上限。
  选主元 LU 满足 Iron Law；不选主元时增长因子可达 $2^{n-1}$，违反 Iron Law。
  前向误差 = 向后误差 $\times\kappa$——这是贯穿 GVL 全书的「宪法不等式」。
- **关键定理**：**选主元 LU 的向后稳定性（Wilkinson）**。
  部分选主元 $PA=LU$，浮点结果满足 $\hat{L}\hat{U}=PA+\Delta A$，其中
  $|\Delta A|\le n\epsilon_{\rm mach}|\hat{L}||\hat{U}|$。
  若增长因子 $\rho=\max|u_{ij}|/\max|a_{ij}|$ 有界（实践中 $\rho\sim O(n)$），则向后稳定。
  不选主元时 $\rho$ 可达 $2^{n-1}$（指数爆炸）——选主元是「免费的保险」。
- **自测**：$A=\begin{pmatrix}10^{-20}&1\\1&1\end{pmatrix}$，不选主元做 LU 解 $Ax=(1,2)^T$ 会怎样？选主元后呢？
  （答：不选主元乘子 $=10^{20}$，$U_{22}$ 完全失真；选主元交换行后乘子 $\approx1$，结果精确。）

---

### Part 4 · Special Linear Systems 特殊线性方程组

- **核心**：当 $A$ 有特殊结构时，可把 $O(n^3)$ 降到 $O(n^2)$ 甚至 $O(n\log n)$。
  ① **Toeplitz 系统**（$a_{i-j}$ 只依赖下标差）：**Levinson 递归** $O(n^2)$、
  超快速算法 $O(n\log^2 n)$，用于信号处理（FIR 滤波）。
  ② **Vandermonde 系统**（$a_{ij}=\alpha_j^{i-1}$）：多项式插值，$O(n^2)$。
  ③ **banded 系统**（带宽 $p$）：$O(np^2)$，追赶法是三对角特例 $O(n)$。
  ④ **对称不定系统**：**Bunch-Kaufman** 选主元分解，$O(n^3)$ 但稳定。
  ⑤ **块三对角**：循环约化法。结构利用的核心是「非零元位置有规律，可预测访存」。
- **飞腾锚点**：**TLB 4.81× [E04]** ⭐（结构化矩阵的访存局部性）🟢。
  Toeplitz/Vandermonde/banded 矩阵的非零元虽稀疏但分布有规律，
  cache-blocking（按带宽分块连续存储）把 TLB 命中率提升 4.81×。
  Levinson 递归每步是 $O(n)$ 向量运算，对 cache 局部性敏感。
  AI 锚点：**Toeplitz 矩阵用于 CNN 卷积**——卷积核循环延拓后即为 Toeplitz-block，
  cuDNN 的 Winograd 卷积利用此结构加速。
- **关键定理**：**Levinson-Durbin 递归复杂度**。
  对称正定 Toeplitz 系统 $Tx=b$ 可在 $O(n^2)$ 内精确求解（而非通用 $O(n^3)$），
  每步递推维护两个 $O(n)$ 向量（前向/后向预测器），总代价 $2n^2+O(n)$ flops。
- **自测**：Toeplitz 三对角 $T=\begin{pmatrix}2&1&0\\1&2&1\\0&1&2\end{pmatrix}$，
  用追赶法解 $Tx=(1,2,1)^T$。
  （答：前消后追得 $x=(1/3,1/3,1/3)^T$，代价仅 $O(n)$。）

---

### Part 5 · Orthogonalization and Least Squares 正交化与最小二乘

- **核心**：超定系统 $\min_x\|Ax-b\|_2$ 的三条解路与正交化工具。
  ① **Householder 反射** $P=I-2vv^*/\|v\|^2$：镜面反射，正交对称（$P=P^*=P^{-1}$），
  是最稳定的 QR 实现方式（LAPACK 默认 `dgeqrf`）。
  ② **Givens 旋转**：平面旋转 $G(i,j,\theta)$，
  适合稀疏/结构化 QR（逐元素零化，不动整列）。
  ③ **QR 分解** $A=QR$ → 最小二乘解 $R\hat{x}=Q^Tb$，$\kappa$ 不放大。
  ④ **SVD 伪逆** $x=V\Sigma^+U^Tb$：最稳且自动处理秩亏损。
  ⑤ **经典/修正 Gram-Schmidt**：CGS 数值不稳（误差 $O(\epsilon\kappa^2)$），
  MGS 改善一阶（$O(\epsilon\kappa)$）——数学等价但数值不等价的经典案例。
- **飞腾锚点**：**Schmidt 正交化** ⭐（QR 分解的数学内核）🟢。
  Gram-Schmidt、Householder、Givens 三种 QR 实现的数学内核都是正交投影——
  核心运算 $\langle\mathbf{a},\mathbf{q}\rangle\mathbf{q}$ 是内积 + 标量乘。
  CGS 与 MGS 的差异仅在循环嵌套顺序，却导致数值稳定性天壤之别。
  AI 锚点：**PyTorch `torch.linalg.qr`** 用于正交初始化、RNN 梯度稳定性。
- **关键定理**：**最小二乘 QR 稳定性**。
  Householder QR 得 $\hat{x}$ 满足 $(A+\Delta A)\hat{x}=b+\delta b$，
  $\|\Delta A\|/\|A\|=O(\epsilon)$——**向后误差与 $\kappa(A)$ 无关**。
  对比：正规方程 $A^TAx=A^Tb$ 的向后误差 $\sim O(\epsilon\kappa^2)$，病态时完全失真。
  这是「为什么永远优先 QR 而非正规方程」的严格证明。
- **自测**：构造 Householder 向量 $v$ 将 $\mathbf{x}=(1,2,2)^T$ 映为 $\|\mathbf{x}\|\mathbf{e}_1=(3,0,0)^T$。
  （答：$v=(-2,2,2)^T$，$\|v\|^2=12$，$P=I-\frac{2}{12}vv^T$，验证 $P\mathbf{x}=(3,0,0)^T$。）

---

### Part 6 · Modified Least Squares Problems 修正最小二乘

- **核心**：当数据动态变化时（增加/删除行或列），
  **增量更新 QR 分解**远比重算 $O(mn^2)$ 高效。
  ① **行追加**（在线学习 / 流式数据）：
  新行 $\mathbf{a}^T$ 追加后用 Givens 旋转零化，代价 $O(n^2)$。
  ② **列追加/删除**：子空间追踪、变量选择。
  ③ **秩一修正** $A+\mathbf{u}\mathbf{v}^T$ 的 QR 更新：
  用 Householder 恢复上三角性。
  ④ **Cholesky 更新** $A+\mathbf{u}\mathbf{u}^T$ 的 $O(n^2)$ 修正（rank-1 update）。
  ⑤ **downdating**（删除数据）：需双曲旋转，数值更敏感。
- **飞腾锚点**：**GEMM 9.45 GFLOPS [Lab05]** ⭐（秩一修正与分块更新）🟢。
  QR 更新的核心是外积修正 $A\leftarrow A-\mathbf{u}\mathbf{v}^T$（rank-1 GEMM），
  批量更新时重组为分块 GEMM 以利用 cache。
  在线最小二乘（递推 LS / RLS）在信号处理和在线学习中广泛应用，
  飞腾 GEMM 9.45 GFLOPS 使 $n=10^3$ 的实时 QR 更新在毫秒级完成。
  AI 锚点：**在线线性回归 / 流式 PCA**。
- **关键定理**：**秩一 Cholesky 更新公式**。
  若 $A=LL^*$（SPD），则 $A+\sigma\mathbf{v}\mathbf{v}^T=\bar{L}\bar{L}^*$
  （$\sigma>0$）的修正 Cholesky 因子可在 $O(n^2)$ 内算出，重算需 $O(n^3)$——快 $n$ 倍。
  downdating（$\sigma<0$）需保证正定性。
- **自测**：$A=\begin{pmatrix}4&2\\2&5\end{pmatrix}=LL^T$，$L=\begin{pmatrix}2&0\\1&2\end{pmatrix}$。
  对 $A+\mathbf{v}\mathbf{v}^T$，$\mathbf{v}=(1,0)^T$，做秩一 Cholesky 更新。
  （答：$\bar A=\begin{pmatrix}5&2\\2&5\end{pmatrix}$，
  $\bar L=\begin{pmatrix}\sqrt5&0\\2/\sqrt5&\sqrt{21/5}\end{pmatrix}$，验证 $\bar L\bar L^T=\bar A$。）

---

### Part 7 · Unsymmetric Eigenvalue Problem 非对称特征值

- **核心**：求 $Ax=\lambda x$（$A$ 一般方阵）的工业级算法，GVL 全书最精巧的章节。
  ① **Schur 分解** $A=QTQ^*$（$T$ 上三角，$Q$ 酉）：
  特征值是 $T$ 对角元，是所有计算的理论终点。
  ② **幂法** $x_{k+1}=Ax_k/\|Ax_k\|$ 收敛到主特征值，线性收敛率 $|\lambda_2/\lambda_1|$。
  ③ **Hessenberg 化**：先用 Householder 把 $A$ 约化为上 Hessenberg $H=Q^*AQ$
  （$h_{ij}=0$ 当 $i>j+1$），代价 $\frac{10}{3}n^3$，使后续迭代每步 $O(n^2)$。
  ④ **QR 算法**：对 $H$ 反复做带移位 QR $H_k-\mu I=Q_kR_k$，$H_{k+1}=R_kQ_k+\mu I$，$H_k\to T$。
  ⑤ **Francis 双移位**处理实矩阵复特征对（避免复运算）。
- **飞腾锚点**：**分支预测 0.71 vs 3.14 [Lab02]** ⭐（QR 算法 deflation 与分裂）🟢。
  QR 算法的收敛是「子问题逐步分裂」——
  当次对角元 $|h_{i,i-1}|<\epsilon(|h_{ii}|+|h_{i+1,i+1}|)$ 时矩阵分裂为独立子块，递归处理。
  这个「检测收敛 → 分割 → 递归」是数据依赖的条件分支，预测器命中率低。
  飞腾实测分支密集代码 IPC 仅 0.71 vs 理论 3.14。
  AI 锚点：**cuSOLVER `geev`** 底层即 Francis 双移位 QR。
- **关键定理**：**QR 算法收敛性**。
  对不可约上 Hessenberg 阵，带 Wilkinson 移位的 QR 算法
  使最后次对角元**二次收敛**（一般矩阵）或**三次收敛**（对称矩阵）。
  总复杂度：Hessenberg 化 $\frac{10}{3}n^3$ + 迭代 $\sim25n^2$（平均每特征值约 2-3 步）$\Rightarrow O(n^3)$。
  无位移时仅在 $|\lambda_i|>|\lambda_{i+1}|$（谱分离）时才收敛。
- **自测**：$A=\begin{pmatrix}2&1\\1&0\end{pmatrix}$（特征值 $1\pm\sqrt2$），
  做 2 步无移位 QR 迭代，观察次对角元是否缩小？
  （答：$A_1\approx\begin{pmatrix}2.17&1.00\\0.14&-0.17\end{pmatrix}$，次对角元 $1\to0.14$，在收敛中。）

---

### Part 8 · Symmetric Eigenvalue Problem 对称特征值

- **核心**：$A=A^T$ 享有特殊结构——特征值全实、特征向量正交、$A=Q\Lambda Q^T$。
  四大算法各擅胜场。
  ① **Jacobi 方法**：用旋转 $J^TAJ$ 逐步消去最大非对角元，
  古老（1846）但精度极高（可达**相对精度**，Demmel 招牌）。
  ② **对称 QR**：先三对角化 $A\to T$（Householder，$\frac{4}{3}n^3$），
  再对三对角阵做隐式移位 QR。
  ③ **分治法（Cuppen 1981）**：把三对角阵 $\begin{pmatrix}T_1&\beta\mathbf{v}\\\beta\mathbf{v}^T&T_2\end{pmatrix}$
  分两半递归解，用秩一修正缝合（secular equation），$O(n^{2.3})$，是 LAPACK 默认（`dsyevd`）。
  ④ **二分法 + 反迭代**：用 Sturm 序列隔离特征值。
  ⑤ **SVD 计算**：Golub-Kahan 双对角化后做隐式 QR（Golub 1965 首创）。
- **飞腾锚点**：**matmul 15× [V03]** ⭐（三对角化与分治的 GEMM 内核）🟢。
  三对角化 $A=QTQ^T$ 的核心 $Q^TAQ$ 是标准 GEMM；
  分治法的秩一修正缝合 $V(\Lambda+\rho\mathbf{v}\mathbf{v}^T)V^T$ 也依赖矩阵乘。
  工业级对称特征值计算（$n>10^3$）中 GEMM 占主导。
  AI 锚点：**K-FAC 二阶优化**的 Kronecker 因子特征值分解、
  谱归一化（spectral normalization for GANs）。
- **关键定理**：**对称特征值扰动（Weyl 不等式）**。
  设 $A=A^T$，$\tilde A=A+\delta A$，按序特征值满足
  $|\tilde\lambda_i-\lambda_i|\le\|\delta A\|_2$（$\forall\,i$，绝对界）。
  对称问题的特征值扰动仅与 $\|\delta A\|$ 有关（不含 $\kappa$），
  比非对称问题（可任意敏感）温和得多——这是「对称是免费的数值保险」的严格表达。
- **自测**：$A=\begin{pmatrix}2&1\\1&2\end{pmatrix}$（特征值 1, 3），
  用 Jacobi 旋转（此处 $\theta=\pi/4$）消去 $a_{12}$。
  （答：$J=\frac{1}{\sqrt2}\begin{pmatrix}1&-1\\1&1\end{pmatrix}$，
  $J^TAJ=\text{diag}(3,1)$，一步对角化。）

---

### Part 9 · Functions of Matrices 矩阵函数

- **核心**：$f(A)$ 的定义与计算——把标量函数（指数、对数、平方根、符号函数）推广到矩阵。
  ① **定义**：若 $f$ 的 Taylor 级数收敛，则 $f(A)=\sum c_k A^k$（如 $e^A=\sum A^k/k!$）。
  ② **Schur-Parlett 方法**：先做 Schur 分解 $A=QTQ^*$，
  在三角阵 $T$ 上用 Parlett 递推计算 $f(T)$ 的对角块——通用方法。
  ③ **矩阵指数** $e^A$：**scaling-and-squaring + Padé 逼近**
  （$e^A\approx(e^{A/2^s})^{2^s}$，$e^{A/2^s}$ 用 Padé 有理逼近），是 MATLAB `expm` 的算法。
  ④ **矩阵符号** $\text{sign}(A)$：Newton 迭代 $X_{k+1}=\frac12(X_k+X_k^{-1})$。
  ⑤ **条件数**：$f(A)$ 的敏感度由 Fréchet 导数衡量。
- **飞腾锚点**：**FP16 3.81× [L01]** ⭐（矩阵函数的精度要求）🟢。
  矩阵函数对精度极度敏感——$e^A$ 的 scaling-and-squaring 需要 $2^s$ 次乘法，
  每次引入 $O(\epsilon)$ 误差，FP16（$\epsilon\approx10^{-3}$）下累积误差可达数个量级。
  实践中矩阵指数计算几乎必须 FP64。
  AI 锚点：**Neural ODE** 的 $e^{At}$ 求解（`torchdiffeq`）、连续深度模型。
- **关键定理**：**矩阵指数的 scaling-and-squaring + Padé**。
  取 $s$ 使 $\|A/2^s\|\le\frac12$，用 $[m/m]$ Padé 逼近
  $e^{A/2^s}\approx D^{-1}N$（$N=\sum_{k=0}^m c_k(A/2^s)^k$，$D=\sum(-1)^k c_k(A/2^s)^k$），
  然后 $e^A=(e^{A/2^s})^{2^s}$。误差 $\le O(\epsilon)$（向后稳定），是 Higham 2009 改进版。
- **自测**：$A=\begin{pmatrix}0&1\\0&0\end{pmatrix}$（$A^2=0$），用 Taylor 级数算 $e^A$。
  （答：$e^A=I+A=\begin{pmatrix}1&1\\0&1\end{pmatrix}$——幂零矩阵的指数只需两项。）

---

### Part 10 · Large Sparse Eigenvalue Problems 大规模稀疏特征值

- **核心**：当 $A$ 大型稀疏（$n>10^4$），直接法 $O(n^3)$ 不可行，
  改用 Krylov 子空间迭代法——只做矩阵-向量乘 $Av$，不分解 $A$。
  ① **Lanczos 迭代**（对称 $A$）：对 Krylov 子空间 $\mathcal{K}_k=\text{span}\{b,Ab,\ldots,A^{k-1}b\}$
  做 Gram-Schmidt，得三对角阵 $T_k$，
  只需**三项递推**（内存 $O(n)$），特征值逼近极端特征值（端点优先收敛）。
  ② **Arnoldi 迭代**（非对称 $A$）：Hessenberg 阵 $\tilde H_k$，需存储全部历史向量（内存 $O(kn)$）。
  ③ **Lanczos breakdown**：有限精度下正交性丧失，出现**「幽灵特征值」**（ghost eigenvalues）。
  ④ **隐式重启 Arnoldi（IRAM/ARPACK）**：限制内存，周期性「清洗」不良方向。
- **飞腾锚点**：**Schmidt 正交化** ⭐（Lanczos/Arnoldi = Krylov 子空间上的正交化）🟢。
  Lanczos 的数学内核就是 MGS 作用于 $\{b,Ab,A^2b,\ldots\}$。
  有限精度下「三项递推」不再保证正交性，误差累积导致幽灵特征值——
  这是 GVL 重点讨论的「理论 vs 实践」鸿沟。
  完全重正交化可修复但代价 $O(kn)$。
- **关键定理**：**Lanczos 端点收敛 + breakdown**。
  精确算术下，Lanczos 三对角阵 $T_k$ 的特征值（Ritz 值 $\theta_i$）
  逐步逼近 $A$ 的极端特征值，$k\ll n$ 即可达高精度。
  但**有限精度下** $\mathbf{q}_k$ 间的正交性以 $O(\epsilon)$ 速率丧失，导致：
  ① Ritz 值收敛后仍出现「幽灵」复制品；② 收敛特征值的重数被高估——需重正交化或隐式重启。
- **自测**：$A=\text{diag}(1,2,3,4)$，$b=(1,1,1,1)^T$，做 2 步 Lanczos 求 $T_2$ 特征值。
  （答：$\mathbf{q}_1=\frac12(1,1,1,1)^T$，
  $T_2$ 特征值 $\approx1.29,4.71$——逼近端点 $\lambda_{\min}=1$ 和 $\lambda_{\max}=4$。）

---

### Part 11 · Large Sparse Linear Systems 大规模稀疏线性方程组

- **核心**：大型稀疏 $Ax=b$ 的迭代法。
  ① **CG（共轭梯度，对称正定）**：在 Krylov 子空间沿 $A$-共轭方向搜索，
  理论 $n$ 步终结，实际 $O(\sqrt\kappa)$ 步达高精度。
  ② **MINRES**（对称不定）：最小化残差 $\|r_k\|_2$。
  ③ **GMRES**（非对称）：最小化残差，但存储 $O(kn)$（实际用重启 GMRES($m$)）。
  ④ **预条件** $M^{-1}Ax=M^{-1}b$：
  选 $M\approx A$ 但 $M^{-1}$ 易算（不完全 Cholesky/ILU、区域分解、多重网格），降 $\kappa$ 加速。
  ⑤ **多重网格（multigrid）**：对椭圆 PDE 离散化可达 $O(n)$ 复杂度——最优。
  ⑥ **SpMV** 是所有迭代法的瓶颈。
- **飞腾锚点**：**TLB 4.81× [E04]** ⭐（稀疏 SpMV 的访存局部性）🟢。
  CG/GMRES 每步核心是 SpMV $Ap_k$——
  大型稀疏 $A$（PDE 离散化）的非零元分布不规则，TLB 缺失惩罚大。
  cache-blocking（CSR → BCSR 分块存储）把 TLB 命中率提升 4.81×。
  AI 锚点：**CG 用于 Hessian-free 二阶优化**（Martens 2010）、
  **GMRES 用于牛顿-Krylov 方法**。
- **关键定理**：**CG 收敛率**。对称正定 $A$，$\kappa=\lambda_{\max}/\lambda_{\min}$，CG 第 $k$ 步误差满足
$$\|x_k-x^*\|_A\le 2\left(\frac{\sqrt\kappa-1}{\sqrt\kappa+1}\right)^k\|x_0-x^*\|_A$$
  收敛速度 $\propto\sqrt\kappa$（而非最速下降的 $\propto\kappa$）——
  $\kappa=10^4$ 时 CG 约 200 步 vs 最速下降 20000 步。预条件降 $\kappa$ 直接加速：$\kappa\to1$ 时 1 步收敛。
- **自测**：$A=\text{diag}(1,10^4)$（$\kappa=10^4$），CG 需约多少步达 $10^{-6}$ 精度？
  若用 Jacobi 预条件 $M=A$，迭代几步？
  （答：无预条件 $\rho\approx0.98$，需 $\sim700$ 步；
  Jacobi 预条件后 $M^{-1}A=I$，$\kappa=1$，**1 步精确收敛**。）

---

### Part 12 · Special Topics 专题

- **核心**：前沿交叉专题（第四版新增），体现数值线代最新发展。
  ① **张量分解**：CP 分解（$T\approx\sum\lambda_r\mathbf{a}_r\circ\mathbf{b}_r\circ\mathbf{c}_r$）、
  Tucker 分解（高阶 SVD/HOSVD），用于推荐系统、神经压缩。
  ② **随机化矩阵方法**：用随机投影（Johnson-Lindenstrauss）把高维矩阵降到低维再计算——
  随机化 SVD $A\approx Q(Q^TA)$ 仅需 $O(mnk)$（$k\ll n$）。
  ③ **低秩逼近**：interpolated decomposition、CUR 分解（列/行抽样的可解释低秩逼近）。
  ④ **核方法近似**：Nyström 方法。⑤ **通信规避算法**（communication-avoiding）。
- **飞腾锚点**：**GEMM 9.45 GFLOPS [Lab05]** ⭐（随机投影与张量收缩）🟢。
  随机化 SVD 的核心是 $A\Omega$（随机投影，一次 GEMM）$+$ 小矩阵 $Q^TA$ 的 SVD；
  张量收缩本质是高维 GEMM。
  飞腾 GEMM 9.45 GFLOPS 使 $m=10^6$ 的随机化 SVD 在秒级完成（vs 精确 SVD 小时级）。
  AI 锚点：**Transformer attention 矩阵化**（$QK^T$ 是批量 GEMM）、
  **Performer 随机化 attention**（核近似降 $O(n^2)\to O(n)$）。
- **关键定理**：**随机化 SVD 近似保证**。对 $A\in\mathbb{R}^{m\times n}$，
  取随机高斯矩阵 $\Omega\in\mathbb{R}^{n\times k}$（$k=r+p$），$Y=A\Omega$，对 $Y$ 做 QR 得 $Q$，则期望误差
$$\mathbb{E}\,\|A-QQ^TA\|_2\le\left(1+\frac{4\sqrt{k}}{p-1}\sqrt{\min(m,n)}\right)\sigma_{r+1}$$
  $O(mnk)$ 代价近似达到 Eckart-Young 的 $O(mn^2)$ 精确最优——大矩阵时代的实用突破。
- **自测**：$A=\text{diag}(1,2,10^{-6})$（$\sigma_3$ 很小），
  取 $k=2$ 做随机化秩-2 逼近，$\|A-QQ^TA\|_2$ 期望约多少？
  （答：$\approx\sigma_3=10^{-6}$，截断效果与精确 SVD 相当。）

---

## §9 全书思想主线：从稠密到稀疏、从精确到迭代、从小到大

Golub-Van Loan 全书贯穿着一条清晰的发展主线：**算法随矩阵规模与结构的演变**。

**前半部（Part 1-9）**处理**稠密矩阵的直接算法**，核心复杂度 $O(n^3)$。
逻辑链是「乘法（Part 1）→ 分析工具（Part 2）→ 解方程（Part 3-4）
→ 最小二乘（Part 5-6）→ 特征值（Part 7-8）→ 矩阵函数（Part 9）」——
每一步都建立在前一步的分解之上（LU → QR → Schur → 函数），
形成从「解」到「谱」到「函数」的完整链条。
这一半部的灵魂是**向后稳定性**：
所有算法都应精确求解某个邻近问题（$\|\Delta A\|=O(\epsilon)\|A\|$），
前向误差 = 向后误差 $\times\kappa$。

**后半部（Part 10-11）**转向**大规模稀疏矩阵的迭代算法**（Krylov 子空间），
核心复杂度 $O(k\cdot\text{nnz})$（$k\ll n$）。当 $n>10^4$ 时直接法不可行，只能用迭代法。
这一半部的灵魂是**条件数决定收敛速度**：
CG 的 $\sqrt\kappa$、GMRES 的谱聚集度、预条件降 $\kappa$ 加速。
**Part 12**展望**随机化与张量方法**——大数据时代 $O(mnk)$ 近似取代 $O(mn^2)$ 精确。

这与已读教材呼应：
**Trefethen-Bau** 是 GVL Part 1-11 的浓缩直觉版（同一结构，40 讲精炼）；
**Demmel** 是 GVL 的工程深化版（补上复杂度 + 并行轴）；
**Nocedal-Wright** 第 5 章 CG 与 GVL Part 11 同源（优化视角 vs 线代视角）；
**Nesterov** 复杂度下界与 CG 收敛率同根（$\sqrt\kappa$ 信息复杂度）。

---

## §10 交叉引用与飞腾锚点速查

### 与本仓库其他笔记的交叉

| 本书概念 | 关联书 / 方向 | 接口 |
|:-------|:------------|:-----|
| SVD / QR / LU（Part 2-5） | **[trefethen 数值线代]**（刚做） | TB 讲概念直觉（40 讲），GVL 给百科细节 + 伪代码 + flop 计数；TB 是入门，GVL 是手册 |
| 算法复杂度 / BLAS / 并行 | **[demmel 应用数值线代]**（刚做） | Demmel 讲「为何这样设计」（复杂度 + 并行三轴），GVL 给「算法全谱系」 |
| CG 收敛率 $\sqrt\kappa$ | **[nocedal_wright 数值优化]** Ch5 | NW 从优化视角（$\min\frac12x^TAx$），GVL Part 11 从线代视角（Krylov 子空间），同一定理 |
| 条件数 / 收敛复杂度 | **[Nesterov 凸优化]** | Nesterov 一阶最优 $O(1/\sqrt\kappa)$ ↔ CG 的 $O(\sqrt\kappa)$ 步，信息复杂度同源 |
| 范数 / 子空间 / SVD 存在性 | **[Hoffman-Kunse 线性代数]**（stage-1） | HK 纯数学存在性证明，GVL 补「如何高效数值计算 + 误差控制」 |

### AI / 工程锚点（数值线代 = 深度学习底层）

| 算法（本书部分） | AI / 工程落地 |
|:----------|:------------|
| **GEMM**（Part 1） | **cuBLAS** GEMM 是 PyTorch 所有矩阵运算底层；**Transformer attention** $QK^T$ / $AV$ 是批量 GEMM |
| **SVD**（Part 2, 5, 8） | **PyTorch `torch.linalg.svd`** = LAPACK `dgesdd`；PCA 降维、谱归一化（GAN）、推荐系统 ALS |
| **LU / Cholesky**（Part 3） | **`torch.linalg.solve` / `cholesky`** = LAPACK `dgesv`/`dposv`；协方差矩阵求逆、高斯过程回归 |
| **QR 分解**（Part 5） | **cuSOLVER `geqrf`**；SLAM 后端优化、正交初始化 |
| **特征值 / Schur**（Part 7-8） | **cuSOLVER `syevd`** 分治 QR；**K-FAC 二阶优化**的 Kronecker 因子特征值、Hessian 谱分析（泛化研究） |
| **矩阵指数**（Part 9） | **Neural ODE** 的 ODE 求解器（`torchdiffeq`）；连续深度模型、扩散模型 score matching |
| **CG / GMRES**（Part 11） | **Hessian-free 二阶优化**（Martens 2010）；大规模 PDE 求解（FEniCS / PETSc） |
| **随机化 SVD**（Part 12） | **Performer 随机化 attention**（核近似降 $O(n^2)\to O(n)$）；大模型推理加速 |
| **张量分解**（Part 12） | 神经网络压缩（Tucker/CP 低秩分解权重）；推荐系统 |
| **cuDNN**（全谱系） | GPU 上 BLAS/LAPACK 实现，PyTorch / TensorFlow 底层所有矩阵运算 |

### 飞腾锚点速查（12 部分，8 锚点，相邻不重复）

| 锚点 | 部分 | 角度 |
|:-----|:-----|:-----|
| **matmul 15× ⭐** | Part 1, 8 | GEMM 向量化 / 对称特征值分治 GEMM 内核 |
| **UDOT 16.9× ⭐** | Part 2 | 范数 / SVD 内积累加 |
| **Iron Law <2% ⭐** | Part 3 | LU 向后稳定性 = $O(\epsilon)$ 误差上限 |
| **TLB 4.81× ⭐** | Part 4, 11 | 结构化矩阵访存 / 稀疏 SpMV cache-blocking |
| **Schmidt 正交化 ⭐** | Part 5, 10 | QR 分解正交投影 / Lanczos-Arnoldi = Krylov MGS |
| **GEMM 9.45G ⭐** | Part 6, 12 | 秩一修正 / 随机投影与张量收缩 |
| **分支预测** | Part 7 | QR 算法 deflation 与 Schur 分裂 |
| **FP16 3.81× ⭐** | Part 9 | 矩阵函数 scaling-squaring 的精度要求 |

---

> **下一步**：精读 Part 1（Strassen + GEMM，飞腾 matmul 锚点）
> + Part 3（LU 稳定性 + 向后误差，Iron Law 锚点）
> + Part 11（CG 收敛率 $2((\sqrt\kappa-1)/(\sqrt\kappa+1))^k$，ML 二阶优化接口）
> + Part 12（随机化 SVD，大模型推理加速前沿）。
> 研究选题「**飞腾 D3000M 上 Strassen vs 朴素 GEMM 的交叉点分析**」——
> $O(n^{2.807})$ 的常数与精度代价在国产 ARM NEON 上何时值得切换？
> 能否用 cuDNN Tensor Core 的 $4\times4\times4$ 分块对应飞腾 SVE 分块？
> 衔接 [trefethen]（直觉版）第 7/8 章稳定性 + [demmel]（工程版）第 2 章分块 LU + [nocedal_wright] 第 5 章 CG。
