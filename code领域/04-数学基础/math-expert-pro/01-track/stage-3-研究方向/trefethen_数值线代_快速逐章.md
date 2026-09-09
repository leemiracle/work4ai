# Lloyd N. Trefethen, David Bau III《数值线代》 · 快速逐章精读

> 基于原书：*Numerical Linear Algebra*（Lloyd N. Trefethen & David Bau III, SIAM, 1997）/ 读于：2026-07-03
> 定位：**数值线性代数最经典的「直觉先行」教材**，40 讲精炼覆盖 SVD/QR/特征值/迭代法全谱系，每一讲只讲一个核心概念。
> 本文为**快速逐章精读**，按原书 4 大部分 + 12 主题组织，每主题 1 个飞腾锚点 + 1 个关键定理 + 1 道自测题。
> 关联：[Kress 数值分析 GTM181](kress_数值分析_GTM181_快速逐章.md) · [Nocedal-Wright 数值优化](nocedal_wright_数值优化_快速逐章.md) · [C-数值分析](C-数值分析_快速逐章.md) · [Hoffman-Kunse 线性代数](../stage-1-本科核心/hoffman_kunze_线性代数_快速逐章.md)

---

## §0 引言：为什么 Trefethen-Bau 是数值线代的「黄金入口」

Lloyd N. Trefethen（Oxford/Cornell，数值分析大家）与 David Bau III（前 UIUC，Google 工程师）合著的《Numerical Linear Algebra》（SIAM, 1997）是**数值线代领域公认的入门圣经**——全书仅 370 页、40 讲，每一讲聚焦一个核心概念，用最少的篇幅把 SVD、QR 分解、特征值算法、迭代法讲得既严格又透彻。它的最大特色是**直觉先行**：先给几何图像与物理动机，再补定理证明，让读者「先看见森林，再看清每棵树」。

一句话定位：本书是 stage-3 方向 §3B（数值分析）的**核心奠基教材**，填补了本仓库数值线代方向的缺口。
已读的 [Kress GTM181](kress_数值分析_GTM181_快速逐章.md) 第 1 章线代是快速概览，
[Nocedal-Wright](nocedal_wright_数值优化_快速逐章.md) 从优化视角零散引用 CG/SVD，
而 Trefethen-Bau 是**系统性地从矩阵运算的「几何本质」出发**——把 SVD 作为全书枢纽、条件数与向后稳定性作为质量保证、迭代法作为大规模计算的工程出口。
读完本书，读者面对任何矩阵计算问题（深度学习中的 SVD 降维、二阶优化 K-FAC 中的特征值、大规模 PDE 中的 CG 求解）都能追溯到底层数学结构。

全书三大支柱——**SVD（几何）、条件数（敏感度）、向后稳定性（误差控制）**——贯穿 40 讲，构成了数值线代的「宪法」。
飞腾锚点则把抽象的浮点误差分析钉到真实硬件：
**FP16 3.81×**（条件数决定低精度何时安全）、
**Iron Law <2%**（向后稳定的误差上限）、
**UDOT 16.9×**（SVD 核心内积运算）、
**Schmidt 正交化**（QR 分解 / Arnoldi 迭代的共同内核）。

### 四本数值线代教材对比

| 书 | 风格 | 严格性 | 适合谁 |
|:---|:-----|:-------|:-------|
| **Trefethen-Bau**（本书） | 直觉先行，40 讲精炼，几何驱动 | 中高（定理 + 证明，侧重直觉与洞察） | 初入数值线代的研究生 / AI 工程师 |
| Golub-Van Loan《Matrix Computations》 | 百科全书式算法手册，全面厚重 | 高（覆盖极广，严谨系统） | 需查阅算法细节的从业者 / 参考工具书 |
| Demmel《Applied Numerical Linear Algebra》 | 任务驱动，算法 + 软件工程视角 | 高（含自动调优 / 通信最优） | 想理解「算法为何这样设计」的工程师 |
| Higham《Accuracy and Stability》 | 误差分析纵深，精雕细琢 | 极高（浮点分析的终极参考） | 专攻数值稳定性 / 精度保证的专家 |

> **阅读策略**：**Trefethen-Bau 建直觉骨架** → Demmel 补算法工程细节 → Golub-Van Loan 作手册查询 → Higham 深挖误差分析。

---

## §1 全书骨架：4 部分 + 12 主题（飞腾锚点分布）

原书 40 讲分 3 个物理部分（Fundamentals / QR Algorithm / Iterative Methods），
本文按任务要求重组为 **4 大部分 + 12 主题**（每主题合并原书多讲，标注对应 Lecture 号），便于快速建立认知地图。

| 部分 | 主题 | 核心概念 | 飞腾锚点 |
|:----:|:-----|:--------|:--------|
| **§I 基础** | 1. 矩阵-向量乘法与范数 (Lec 1-3) | 线性映射、$\ell^p$ 范数、算子范数 | matmul 15× ⭐ |
| (Lec 1-12) | 2. SVD——全书枢纽 (Lec 4-6) | $A=U\Sigma V^*$、低秩逼近、几何 | UDOT 16.9× ⭐ |
| | 3. QR 分解与 Gram-Schmidt (Lec 7-9) | 正交三角化、CGS vs MGS | Schmidt 正交化 ⭐ |
| | 4. Householder 三角化与最小二乘 (Lec 10-11) | 反射变换、$\min\|Ax-b\|$ | GEMM 9.45G ⭐ |
| **§II QR 算法** | 5. 特征值问题与 Hessenberg 化 (Lec 25-27) | 谱、相似变换、上 Hessenberg | 分支预测 |
| (Lec 25-30) | 6. Rayleigh 商迭代与 QR 算法 (Lec 28-30) | 位移策略、Schur 分解、Francis | matmul 15× ⭐ |
| **§III 条件与稳定** | 7. 条件数——问题的敏感度 (Lec 12) | $\kappa(A)=\|A\|\|A^{-1}\|$ | FP16 3.81× ⭐ |
| (Lec 12-24) | 8. 浮点算术与向后稳定性 (Lec 13-15) | $\epsilon_{\rm mach}$、向后误差 | Iron Law <2% ⭐ |
| | 9. 稳定性分析与直接法 (Lec 16-24) | Householder/回代/LU/Cholesky 稳定性 | UDOT 16.9× ⭐ |
| **§IV 迭代法** | 10. Arnoldi 迭代与 GMRES (Lec 31-33) | Krylov 子空间、非对称迭代 | Schmidt 正交化 ⭐ |
| (Lec 31-40) | 11. Lanczos 迭代与共轭梯度 CG (Lec 34-36) | 三对角化、对称正定、收敛率 | TLB 4.81× ⭐ |
| | 12. 预条件与 FFT 加速 (Lec 38-39) | 预条件子、$O(n\log n)$ 蝶形 | GEMM 9.45G ⭐ |

---

# §I 基础（Lec 1-12）

---

## 主题 1 · 矩阵-向量乘法与范数（Lec 1-3）

- **核心**：全书从最基本操作出发——矩阵-向量乘法 $y=Ax$ 的本质是「$A$ 的列的线性组合」
  （$y=\sum_j x_j a_j$，列视角），也是「$A$ 的行与 $x$ 的内积」（行视角），代价 $\sim 2mn$ flops。
  范数衡量向量/矩阵的「大小」：$\ell^1$、$\ell^2$、$\ell^\infty$ 三族，
  矩阵诱导范数 $\|A\|=\max_{\|x\|=1}\|Ax\|$。
  正交矩阵 $Q$（$Q^*Q=I$）保持范数不变 $\|Qx\|=\|x\|$，是数值稳定的「免费变换」——
  全书反复利用正交变换来保证数值稳定性。
- **飞腾锚点**：**matmul 15× [V03]**（矩阵乘法）🟢。
  $y=Ax$ 是 GEMV（矩阵-向量），$AB$ 是 GEMM（矩阵-矩阵），后者经循环重排 + 向量化达 15× 加速。
  数值线代所有算法的底层都是这两种操作——SVD、QR、特征值分解的 $O(n^3)$ 成本中，GEMM 占 90%+，
  飞腾 matmul 优化直接决定整体吞吐。
- **关键定理**：**范数次可可乘性** $\|AB\|\le\|A\|\|B\|$。
  矩阵 2-范数 $\|A\|_2=\sigma_{\max}(A)$（最大奇异值），
  Frobenius 范数 $\|A\|_F=\sqrt{\sum_{ij}|a_{ij}|^2}=\sqrt{\sum_i\sigma_i^2}$。
  正交变换保 2-范数与 F-范数：$\|QA\|_2=\|A\|_2$，$\|QA\|_F=\|A\|_F$。
- **自测**：$A=\begin{pmatrix}1&2\\3&4\end{pmatrix}$，计算 $\|A\|_F$ 和 $\|A\|_\infty$（行和范数）。
  （答：$\|A\|_F=\sqrt{1+4+9+16}=\sqrt{30}\approx5.48$；$\|A\|_\infty=\max(3,7)=7$。）

---

## 主题 2 · SVD——全书枢纽（Lec 4-6）⭐⭐⭐

- **核心**：**奇异值分解（SVD）是全书最重要的工具**。
  任何矩阵 $A\in\mathbb{R}^{m\times n}$ 都可分解为 $A=U\Sigma V^*$，
  其中 $U,V$ 正交、$\Sigma$ 对角非负。
  几何意义：任何线性变换 = 旋转（$V^*$）+ 缩放（$\Sigma$）+ 旋转（$U$）。
  SVD 直接揭示矩阵的「几何骨架」：奇异值 $\sigma_1\ge\cdots\ge\sigma_r>0$ 衡量各方向的「能量」。
  **截断 SVD** $A_k=\sum_{i=1}^k\sigma_i u_i v_i^*$ 是最佳秩-$k$ 逼近（Eckart-Young 定理），
  是 PCA 降维、推荐系统、图像压缩的数学根基。
- **飞腾锚点**：**UDOT 16.9× [E05]**（向量内积）🟢。
  SVD 的核心运算是向量内积 $u^Tv$——双对角化过程中大量点积累加，
  飞腾 INT8 UDOT 指令达 16.9× 加速。
  奇异值本身就是 $A^TA$ 特征值的平方根，每个特征值计算涉及点积。
  AI 锚点：**PyTorch `torch.linalg.svd`** 底层调 LAPACK `dgesdd`，随机化 SVD 是大模型推理加速前沿。
- **关键定理**：**SVD 存在性 + Eckart-Young 最佳逼近**。
  $A=U\Sigma V^*$，$\|A\|_2=\sigma_1$，$\|A\|_F=(\sum\sigma_i^2)^{1/2}$。
  对任意秩-$k$ 矩阵 $B$：
  $\|A-A_k\|_2=\sigma_{k+1}$，$\|A-A_k\|_F=(\sum_{i>k}\sigma_i^2)^{1/2}$
  ——截断 SVD 在所有秩-$k$ 逼近中误差最小。
- **自测**：$A=\begin{pmatrix}3&0\\0&1\end{pmatrix}$，写出 SVD，计算 $\|A\|_2$ 和秩-1 最佳逼近 $A_1$。
  （答：$U=I,\Sigma=\text{diag}(3,1),V=I$；$\|A\|_2=3$；
  $A_1=\begin{pmatrix}3&0\\0&0\end{pmatrix}$，$\|A-A_1\|_2=1=\sigma_2$。）

---

## 主题 3 · QR 分解与 Gram-Schmidt 正交化（Lec 7-9）⭐⭐

- **核心**：任何列满秩矩阵 $A$ 可分解为 $A=QR$（$Q$ 正交、$R$ 上三角），
  这是求解线性方程组和最小二乘的数值基石。
  **经典 Gram-Schmidt（CGS）**逐列正交化 $\mathbf{q}_k=\mathbf{a}_k-\sum_{j<k}\langle\mathbf{a}_k,\mathbf{q}_j\rangle\mathbf{q}_j$，
  但数值不稳定（舍入误差导致 $\mathbf{q}_k$ 不正交）。
  **修正 Gram-Schmidt（MGS）**改为逐个减去已求方向分量，数学等价但数值更稳——代价仅改变运算顺序。
  QR 分解也可由 Householder 反射（主题 4）实现，稳定性更优。
- **飞腾锚点**：**Schmidt 正交化**（QR 分解）🟢。
  Gram-Schmidt 的核心运算就是正交投影 $\langle\mathbf{a},\mathbf{q}\rangle\mathbf{q}$——
  每个投影是一个内积 + 标量乘。飞腾向量化 UDOT 加速内积累加。
  CGS 与 MGS 的差异在于循环嵌套顺序（列外层 vs 分量外层），
  这种「数学等价但数值不等价」的现象是向后误差分析的经典案例。
- **关键定理**：**QR 分解的存在性与（近似）唯一性**。
  $A\in\mathbb{R}^{m\times n}$（$m\ge n$，列满秩）存在 $A=QR$，$R$ 对角元为正当 $A$ 各列线性无关。
  **MGS 的稳定性**：$\|I-Q^TQ\|=O(\epsilon\kappa(A))$，
  而 CGS 达 $O(\epsilon\kappa(A)^2)$——MGS 把条件数的幂次降了一阶。
- **自测**：用 MGS 对 $A=\begin{pmatrix}1&1\\0&1\\0&0\end{pmatrix}$ 做 QR 分解。
  （答：$\mathbf{q}_1=(1,0,0)^T$；
  $\mathbf{a}_2-\langle\mathbf{a}_2,\mathbf{q}_1\rangle\mathbf{q}_1=(0,1,0)^T=\mathbf{q}_2$；
  $R=\begin{pmatrix}1&1\\0&1\end{pmatrix}$，$Q=\begin{pmatrix}1&0\\0&1\\0&0\end{pmatrix}$。）

---

## 主题 4 · Householder 三角化与最小二乘（Lec 10-11）⭐⭐⭐

- **核心**：**Householder 反射** $P=I-2\frac{vv^*}{\|v\|^2}$
  是「关于超平面 $v^\perp$ 的镜面反射」，正交且对称（$P=P^*=P^{-1}$）。
  用一连串 Householder 反射可将 $A$ 化为上三角：$Q^*A=R$（$Q=P_1P_2\cdots P_{n-1}$）。
  这比 Gram-Schmidt **数值更稳定**（正交性误差仅 $O(\epsilon)$，无 $\kappa(A)$ 因子），
  是 LAPACK QR 分解的标准实现。
  最小二乘 $\min_x\|Ax-b\|_2$ 经 QR 后化为上三角回代 $R\hat{x}=Q^*b$，
  优于正规方程 $A^TAx=A^Tb$（后者条件数平方 $\kappa(A^TA)=\kappa(A)^2$）。
- **飞腾锚点**：**GEMM 9.45 GFLOPS [Lab05]**（高维矩阵吞吐）🟢。
  Householder 三角化每步将反射 $P_k=I-2v_kv_k^*$ 作用于子矩阵 $A[k{:},k{:}]$，
  核心是 $v_k^*A_{\rm sub}$（GEMV）+ 外积修正（rank-1 更新），整体 $O(n^3)$ 中 GEMM 占主导。
  飞腾 GEMM 9.45 GFLOPS 让 $n=10^4$ 的 QR 从小时级降到分钟级。
- **关键定理**：**Householder QR 的向后稳定性**。
  浮点计算得 $\tilde{Q}\tilde{R}$，存在 $\Delta A$ 使 $\tilde{Q}\tilde{R}=A+\Delta A$，
  $\|\Delta A\|/\|A\|=O(\epsilon)$——
  向后误差与 $\kappa(A)$ 无关，是数值线代最优雅的稳定性结果之一。
- **自测**：构造一个 Householder 反射将 $\mathbf{x}=(3,4)^T$ 映为 $\|\mathbf{x}\|\mathbf{e}_1=(5,0)^T$。
  （答：$v=\mathbf{x}-5\mathbf{e}_1=(-2,4)^T$，
  $P=I-2vv^T/\|v\|^2=\frac{1}{5}\begin{pmatrix}3&4\\4&-3\end{pmatrix}$，
  验证 $P\mathbf{x}=(5,0)^T$。）

---

# §II QR 算法与特征值（Lec 25-30）

---

## 主题 5 · 特征值问题与 Hessenberg 化（Lec 25-27）⭐⭐

- **核心**：特征值问题 $Ax=\lambda x$ 是数值线代第二大主题。
  直接计算特征多项式 $\det(\lambda I-A)$ 的根是**数值灾难**
  （Wilkinson 的经典反例：根对系数极度敏感）。
  正确策略分两步：
  ① 通过正交相似变换将 $A$ 化为**上 Hessenberg 形** $H=Q^*AQ$
  （上三角加下次对角线），这一步精确（$O(n^3)$，无误差积累），
  为迭代压缩到 $O(n^2\cdot\text{迭代数})$ 奠基；
  ② 在 Hessenberg 形上跑 QR 迭代。
  Hessenberg 化的关键洞察：正交相似变换保谱（$\sigma(H)=\sigma(A)$）且保 Hessenberg 结构不变。
- **飞腾锚点**：**分支预测 0.71 vs 3.14 [Lab02]**（Hessenberg 化分支）🟡。
  Hessenberg 化中每列的 Householder 向量需判断符号选择（$\text{sign}$ 以避免相消），
  这类条件分支数据依赖，预测器命中率低。
  QR 迭代的 deflation（收缩）判断（子对角元是否足够小）同理。
  标 🟡 因分支影响的是效率而非正确性。
- **关键定理**：**Hessenberg 化定理**。
  任意 $A\in\mathbb{R}^{n\times n}$ 存在正交 $Q$ 使 $Q^*AQ=H$ 为上 Hessenberg，
  通过 $n-2$ 个 Householder 反射实现，代价 $\frac{10}{3}n^3+O(n^2)$。
  关键：后续 QR 迭代保持 Hessenberg 结构，每步仅 $O(n^2)$ 而非 $O(n^3)$。
- **自测**：将 $A=\begin{pmatrix}1&2&3\\4&5&6\\7&8&9\end{pmatrix}$ 的第一列下部分 $(4,7)^T$
  用一个 Householder 反射零化，写出反射向量 $v$。

---

## 主题 6 · Rayleigh 商迭代与 QR 算法（Lec 28-30）⭐⭐⭐

- **核心**：**Rayleigh 商** $r(x)=\frac{x^*Ax}{x^*x}$
  给出当前方向上的最优特征值估计（对对称 $A$，$r(x)$ 是最接近 $x$ 方向投影的特征值）。
  **Rayleigh 商迭代**（RQI）每步用 $r(x_k)$ 做位移解 $(A-r_k I)y=x_k$ 再归一化，
  对对称矩阵**三次收敛**（每步位数三倍！），是单特征值最快的方法。
  **QR 算法**则求全部特征值：反复 $A_k=Q_kR_k$，$A_{k+1}=R_kQ_k=Q_k^*A_kQ_k$，
  无位移时收敛到上三角（Schur 形），加 **Wilkinson 位移**后对对称矩阵三次收敛、对一般矩阵二次收敛。
  这是 LAPACK `dgeev` 的核心。
- **飞腾锚点**：**matmul 15× [V03]**（相似变换）🟢。
  QR 迭代每步 $A_{k+1}=R_kQ_k=Q_k^*A_kQ_k$ 是两个矩阵乘（matmul），Hessenberg 形下每步 $O(n^2)$。
  大规模特征值计算（$n>10^3$）中 matmul 向量化直接决定速度。
  AI 锚点：**cuSOLVER 的 `syevd`** 底层即分治 QR 算法，GPU 并行化 matmul。
- **关键定理**：**QR 算法收敛定理**。
  带合适位移的 QR 算法使 $A_k$ 的下三角收敛到零（$A_k\to$ 上三角 = Schur 形），对角元收敛到特征值。
  对称情形：三次收敛 $\frac{|\lambda_{k+1}-\lambda|}{|\lambda_k-\lambda|^3}\to C$。
- **自测**：$A=\begin{pmatrix}2&1\\1&2\end{pmatrix}$（特征值 3, 1），从 $x_0=(1,0)^T$ 做 1 步 RQI：
  $r_0=2$，解 $(A-2I)y=x_0$。
  （答：$(A-2I)=\begin{pmatrix}0&1\\1&0\end{pmatrix}$，$y=(0,1)^T$，$x_1=(0,1)^T$，$r_1=2$——
  注意 $r_0=\lambda_2=2$ 恰好是中间值导致停滞；改用位移 $\mu\ne\lambda$ 即可继续收敛。）

---

# §III 条件、稳定与直接法（Lec 12-24）

---

## 主题 7 · 条件数——问题的敏感度（Lec 12）⭐⭐⭐

- **核心**：**条件数** $\kappa(A)=\|A\|\|A^{-1}\|=\sigma_{\max}/\sigma_{\min}$
  衡量「输入扰动被放大多少倍」，是**问题本身的属性**（与算法无关）。
  解 $Ax=b$ 时，若 $b$ 有扰动 $\delta b$，则 $\frac{\|\delta x\|}{\|x\|}\le\kappa(A)\frac{\|\delta b\|}{\|b\|}$。
  $\kappa\approx1$ 良态（扰动不放大），$\kappa\gg1$ 病态（小扰动酿大祸）。
  条件数是数值分析的「宪法」——全书反复回到 $\kappa$ 判断问题是否可信。
- **飞腾锚点**：**FP16 3.81× [L01]**（低精度何时安全）🟢。
  条件数直接决定何时可用低精度浮点：
  FP16 的 $\epsilon_{\rm mach}\approx10^{-3}$，若 $\kappa(A)=10^2$
  则解的相对误差 $\sim\kappa\cdot\epsilon\sim10\%$——已不可接受。
  经验法则：**可用精度位数 $\ge\log_{10}\kappa+\text{要求有效位数}$**，
  $\kappa>10^3$ 就必须 FP32/FP64。
  这是混合精度训练（FP16 前向 + FP32 主权重）的数学根基。
- **关键定理**：**条件数定理**。
  $\kappa(A)=\|A\|\|A^{-1}\|$。
  扰动界（右端）：$\frac{\|\delta x\|}{\|x\|}\le\kappa(A)\frac{\|\delta b\|}{\|b\|}$。
  扰动界（矩阵）：$\frac{\|\delta x\|}{\|x\|}\le\frac{\kappa(A)\|\delta A\|/\|A\|}{1-\kappa\|\delta A\|/\|A\|}$
  （当 $\kappa\|\delta A\|/\|A\|\to1$ 时爆炸）。
  SVD 视角：$\kappa(A)=\sigma_1/\sigma_n$。
- **自测**：$A=\begin{pmatrix}1&1\\1&1.001\end{pmatrix}$，$\det(A)=0.001$，估算 $\kappa(A)$。
  若 $b$ 有 0.1% 扰动，$\mathbf{x}$ 最坏相对误差多少？
  （答：$\kappa\approx\sigma_{\max}/\sigma_{\min}\approx 2000$；
  $0.1\%\times2000=200\%$——解完全不可信。）

---

## 主题 8 · 浮点算术与向后稳定性（Lec 13-15）⭐⭐⭐

- **核心**：**浮点算术**的基本事实：计算机实数用 $\text{fl}(x)=x(1+\delta)$，
  $|\delta|\le\epsilon_{\rm mach}$（IEEE 双精 $\epsilon\approx2.2\times10^{-16}$，FP16 $\approx10^{-3}$）近似。
  **向后稳定性**是 Trefethen 全书的核心概念：
  算法向后稳定当且仅当它精确求解了某个邻近问题——
  $\tilde{x}=(A+\Delta A)^{-1}b$，$\|\Delta A\|/\|A\|=O(\epsilon)$。
  **向后稳定 ≠ 前向精确**：前向误差 = 向后误差 $\times\kappa$，
  病态问题即使向后稳定算法也可能前向不准——但这不是算法的错，是问题的错。
- **飞腾锚点**：**Iron Law <2% [Lab00]**（误差传递铁律）🟢。
  向后稳定的本质是「每步浮点误差 $\le O(\epsilon)$ 且不放大」，对应 Iron Law 的 <2% 误差上限。
  向后稳定算法（Householder QR、选主元 LU）满足 Iron Law，
  非稳定算法（CGS、正规方程）违反 Iron Law（误差随 $\kappa$ 增长）。
  Iron Law 是「算法是否值得信任」的硬件级判据。
- **关键定理**：**向后稳定性定义**。
  算法 $\tilde{f}$ 对问题 $f$ 向后稳定，
  若 $\forall x$ 存在 $\tilde{x}$ 使 $\tilde{f}(x)=f(\tilde{x})$ 且 $\|\tilde{x}-x\|/\|x\|=O(\epsilon)$。
  **前向误差界**：$\frac{\|\tilde{f}(x)-f(x)\|}{\|f(x)\|}\le O(\epsilon)\cdot\kappa$。
  一句话：**向后误差是算法属性，条件数是问题属性，前向误差是两者之积**。
- **自测**：为何 Householder QR 求最小二乘向后稳定，而正规方程 $A^TAx=A^Tb$ 不向后稳定？
  （提示：正规方程的条件数 $\kappa(A^TA)=\kappa(A)^2$，
  向后误差 $\sim\epsilon\kappa(A)^2$，$\kappa$ 大时违反 Iron Law。）

---

## 主题 9 · 稳定性分析与直接法（Lec 16-24）⭐⭐

- **核心**：把主题 8 的向后稳定性框架应用于具体算法。
  **Householder QR 向后稳定**（$\|\Delta A\|=O(\epsilon)\|A\|$，与 $\kappa$ 无关）；
  **回代法向后稳定**（$\tilde{x}=(R+\Delta R)^{-1}(Q^*b+\delta b)$）；
  **带部分选主元的高斯消元 $PA=LU$** 向后稳定
  （Wilkinson 经典证明，$\|\Delta A\|\le O(n^3\epsilon)\|A\|$，实际远小于此界）；
  **Cholesky 分解**（对称正定）无需选主元即稳定。
  最小二乘：Householder QR 稳定，正规方程不稳定（$\kappa^2$），MGS 介于二者之间。
- **飞腾锚点**：**UDOT 16.9× [E05]**（回代与分解的内积）🟢。
  高斯消元的每步消元是行间线性组合（内积 + 外积），
  回代求解 $Ux=y$ 每个分量 $\sum$ 内积。Cholesky 分解同理。
  这些 $O(n^3)$ 操作的核心是密集点积/外积，UDOT 向量化直接加速。
  AI 锚点：**`torch.linalg.cholesky`** 是对称正定系统求解的工业标准（比通用 LU 快 2 倍）。
- **关键定理**：**高斯消元的向后稳定性**（Wilkinson）。
  带部分选主元 $PA=LU$，浮点结果满足 $\tilde{L}\tilde{U}=PA+\Delta A$，
  $\|\Delta A\|\le 6n^3\mu\|A\|+O(\epsilon^2)$（$\mu$ 为增长因子，实践中 $\mu$ 很小）。
  **选主元的必要性**：不选主元时 $\mu$ 可达 $2^{n-1}$（指数爆炸），选主元后实践中 $\mu\sim O(n)$。
- **自测**：$A=\begin{pmatrix}10^{-20}&1\\1&1\end{pmatrix}$，不选主元做 LU 会发生什么？选主元呢？
  （答：不选主元，乘子 $=10^{20}$，$\Delta A$ 爆炸，$U_{22}\approx-10^{20}$ 完全失真；
  选主元交换行后乘子 $\approx1$，结果精确。）

---

# §IV 迭代法（Lec 31-40）

---

## 主题 10 · Arnoldi 迭代与 GMRES（Lec 31-33）⭐⭐⭐

- **核心**：当 $A$ 大型稀疏（$n>10^4$，如 PDE 离散），直接法 $O(n^3)$ 不可行，
  改用**迭代法**——只做矩阵-向量乘 $Av$，不分解 $A$。
  **Arnoldi 迭代**是非对称 $A$ 的核心：从 $\mathbf{q}_1$ 出发，
  对 Krylov 子空间 $\mathcal{K}_k=\text{span}\{\mathbf{q}_1,A\mathbf{q}_1,\ldots,A^{k-1}\mathbf{q}_1\}$
  做 Gram-Schmidt 正交化，得 $AQ_k=Q_{k+1}\tilde{H}_k$（$H$ 上 Hessenberg）。
  **GMRES**（Saad-Schultz 1986）在每个 Krylov 子空间中找最小残差 $\min_{x\in\mathcal{K}_k}\|b-Ax\|_2$，
  是求解大型非对称稀疏系统的工业标准。
- **飞腾锚点**：**Schmidt 正交化**（Arnoldi = Krylov 子空间上的 Gram-Schmidt）🟢。
  Arnoldi 迭代的数学内核就是**修正 Gram-Schmidt 作用于 $\{b,Ab,A^2b,\ldots\}$**——
  每步 $A\mathbf{q}_k$ 后减去已有方向的分量。
  这是 MGS 稳定性分析（主题 3）的直接延续。
  GMRES 的最小残差通过 Hessenberg 阵的最小二乘求解。
- **关键定理**：**Arnoldi 分解**。
  $AQ_k=Q_{k+1}\tilde{H}_k$，$Q_k^*Q_k=I$，$\tilde{H}_k$ 为 $(k+1)\times k$ 上 Hessenberg。
  **GMRES 残差递减**：
  $\|r_k\|_2\le\|r_0\|_2\prod_{j=1}^k\frac{|\lambda_j-\lambda|_{\rm far}}{|\lambda_j-\lambda|_{\rm near}}$
  （特征值聚集则收敛快）。
  GMRES 每 $k$ 步需存储全部 $Q_k$，内存 $O(kn)$——重启 GMRES($m$) 限制内存。
- **自测**：$A=\begin{pmatrix}1&1\\0&2\end{pmatrix}$，$b=(1,1)^T$，$\mathbf{q}_1=b/\|b\|$，做 1 步 Arnoldi 求 $\tilde{H}_1$。
  （答：$\mathbf{q}_1=\frac{1}{\sqrt2}(1,1)^T$，
  $A\mathbf{q}_1=\frac{1}{\sqrt2}(2,2)^T=\sqrt2\,\mathbf{q}_1$，
  故 $h_{11}=\sqrt2$，$h_{21}=0$——1 步即收敛因 $b$ 恰为特征向量方向。）

---

## 主题 11 · Lanczos 迭代与共轭梯度 CG（Lec 34-36）⭐⭐⭐

- **核心**：当 $A$ **对称**时，Arnoldi 退化为 **Lanczos 迭代**：
  Hessenberg 阵 $H$ 变为**三对角阵** $T_k$，只需三项递推（不需存储全部历史向量），内存 $O(n)$。
  对称正定时，Lanczos 自然导出**共轭梯度法（CG）**：
  $Ax=b$ 的解等价于 $\min\frac12 x^TAx-b^Tx$，
  CG 在 Krylov 子空间中沿 $A$-共轭方向逐步精确搜索，
  理论 $n$ 步收敛，实际 $O(\sqrt\kappa)$ 步达高精度。
  CG 是大规模 PDE / 优化 / 深度学习二阶方法的核心求解器。
- **飞腾锚点**：**TLB 4.81× [E04]**（稀疏矩阵-向量乘）🟢。
  CG/Lanczos 每步核心运算 $Ap_k$（稀疏矩阵-向量乘，SpMV），
  大型稀疏 $A$（PDE 离散化）的非零元分布不规则，TLB 缺失惩罚大——
  4.81× 加速来自对齐缓存行 / 页着色。
  AI 锚点：**CG 是 Hessian-free 二阶优化（K-FAC / 牛顿-CG）的求解器**，
  也是大规模 PDE 求解的默认迭代法。
- **关键定理**：**CG 收敛率**。对称正定 $A$，CG 第 $k$ 步误差满足
$$\|x_k-x^*\|_A\le 2\left(\frac{\sqrt\kappa-1}{\sqrt\kappa+1}\right)^k\|x_0-x^*\|_A$$
  收敛速度 $\propto\sqrt\kappa$（而非最速下降的 $\propto\kappa$）——
  $\kappa=10^4$ 时 CG 约 200 步收敛 vs 最速下降 20000 步。
  Lanczos 三对角化的特征值收敛到 $A$ 的极端特征值（端点优先）。
- **自测**：$A=\begin{pmatrix}4&1\\1&3\end{pmatrix}$（$\kappa\approx2$），$b=(1,0)^T$，$x_0=0$，做 1 步 CG。
  （答：$r_0=b=(1,0)^T$，$p_0=r_0$；
  $\alpha_0=\frac{r_0^Tr_0}{p_0^TAp_0}=\frac{1}{4}$；
  $x_1=(\frac14,0)^T$；$r_1=r_0-\alpha_0 Ap_0=(0,-\frac14)^T$。）

---

## 主题 12 · 预条件与 FFT 加速（Lec 38-39）⭐⭐

- **核心**：CG 收敛率依赖 $\kappa$，实际中 $A$ 常病态（$\kappa\gg1$），需**预条件**：
  将 $Ax=b$ 转化为 $M^{-1}Ax=M^{-1}b$（左预条件），
  选 $M\approx A$ 但 $M^{-1}$ 易算（如不完全 Cholesky $M=\tilde L\tilde L^T\approx A$），
  使 $\kappa(M^{-1}A)\ll\kappa(A)$。
  好的预条件子可将 CG 迭代数降一个数量级——「预条件是艺术，求解是科学」。
  **FFT** 将循环卷积 / 三角插值从 $O(n^2)$ 降到 $O(n\log n)$
  （Cooley-Tukey 蝶形分解），是 Toeplitz 系统、谱方法、信号处理的加速基石。
- **飞腾锚点**：**GEMM 9.45 GFLOPS [Lab05]**（预条件与 FFT 的矩阵运算）🟢。
  不完全 Cholesky 的分解与回代是 $O(n^2)$ 的三角运算（GEMM 密集型）；
  FFT 的蝶形分解本质是分块矩阵乘（$\log n$ 层，每层 $n/2$ 个蝶形），GPU cuFFT 的并行化就是 GEMM 化。
  AI 锚点：**FFT 在 CNN Winograd 卷积**中把 $O(n^2)$ 卷积降到 $O(n\log n)$；
  预条件是地球物理 / 油气模拟的核心技术。
- **关键定理**：**预条件 CG 收敛率**。
  预条件 $M^{-1}A$ 后 CG 收敛率依赖 $\kappa(M^{-1}A)$：
  若 $\kappa(M^{-1}A)\le C$ 则 $O(\sqrt C)$ 步收敛。
  **FFT 复杂度**：$n=2^m$ 点 DFT 经 Cooley-Tukey 分解为 $\frac{n}{2}\log_2 n$ 次蝶形运算，总 $O(n\log n)$。
- **自测**：$A=\text{diag}(10^4,1)$，$\kappa=10^4$，CG 需约多少步达 $10^{-6}$ 精度？
  若用 Jacobi 预条件 $M=\text{diag}(10^4,1)=A$，迭代几步？
  （答：无预条件 $\frac{\sqrt{10^4}-1}{\sqrt{10^4}+1}\approx0.98$，需 $\sim$700 步；
  Jacobi 预条件后 $M^{-1}A=I$，$\kappa=1$，**1 步精确收敛**——预条件的极端威力。）

---

## §9 全书思想主线：SVD + 条件数 + 向后稳定三柱擎天

Trefethen-Bau 全书贯穿着一条不可动摇的主线：
**用三个概念——SVD（几何结构）、条件数（问题敏感度）、向后稳定性（算法质量）——统摄全部数值线代**。

SVD 揭示矩阵的「几何骨架」（旋转 + 缩放 + 旋转），任何矩阵运算都应从 SVD 的视角理解；
条件数 $\kappa$ 判断「这个问题值得信任吗」，把算法的失败归因于「病态问题」还是「劣质算法」；
向后稳定性则给出「算法本身是否忠实」的判据——
三者的乘法关系 $\text{前向误差}\le\text{向后误差}\times\kappa$ 是全书的「宪法不等式」。

这条主线与已读教材形成呼应：
**Nocedal-Wright 数值优化**中的 CG 收敛率 $\le2((\sqrt\kappa-1)/(\sqrt\kappa+1))^k$
正是本书主题 11 的定理——优化视角关注「$\kappa$ 如何影响迭代步数」，
数值线代视角关注「$\kappa$ 如何定义问题敏感度」，同一公式双重视角。
**Kress GTM181** 第 1 章线代是本书的浓缩概览，本书则是其系统展开。
**Nesterov 凸优化**中的复杂度下界（$O(1/\sqrt\kappa)$）与 CG 收敛率同源——
最优一阶方法与 Krylov 方法共享「条件数决定信息复杂度」的深刻联系。
**C-数值分析**（Burden）给出本科直觉，本书补上严格框架。

---

## §10 交叉引用与飞腾锚点速查

### 与本仓库其他笔记的交叉

| 本书概念 | 关联书 / 方向 | 接口 |
|:-------|:------------|:-----|
| CG 收敛率 $\sqrt\kappa$ | **[Nocedal-Wright 数值优化] 第 5 章** | NW 从优化视角（$\min\frac12x^TAx$），TB 从线代视角（Krylov 子空间），同一定理 |
| 条件数 $\kappa$ | **[Kress GTM181] 第 1 章** | Kress 浓缩版，TB 系统展开；GTM181 §0 总纲「向后误差×$\kappa$=前向误差」同源 |
| 高斯消元 / LU / Cholesky | **[C-数值分析 Burden] 第 6-7 章** | Burden 工程入门（怎么算），TB 严格框架（为什么稳） |
| SVD / 范数 / 四子空间 | **[Hoffman-Kunse 线代] / [Strang 线代]** | 纯数学线代给出存在性证明，TB 补上「如何高效数值计算 + 误差控制」 |
| 复杂度 $\kappa$ 下界 | **[Nesterov 凸优化算法]** | Nesterov 一阶最优 $O(1/\sqrt\kappa)$ ↔ CG 的 $O(\sqrt\kappa)$ 步，信息复杂度同源 |

### AI / 工程锚点（数值线代 = 深度学习底层）

| 算法 | AI / 工程落地 |
|:-----|:------------|
| **SVD**（主题 2） | PyTorch `torch.linalg.svd` = LAPACK `dgesdd`；PCA 降维、推荐系统、随机化 SVD 加速大模型推理 |
| **QR 分解**（主题 3-4） | cuSOLVER `geqrf`；最小二乘拟合、SLAM 后端优化 |
| **特征值 / QR 算法**（主题 5-6） | cuSOLVER `syevd` 分治 QR；协方差矩阵谱分析、K-FAC 二阶优化的 Kronecker 特征值 |
| **CG**（主题 11） | Hessian-free 二阶优化（Martens 2010）；大规模 PDE 求解（FEniCS/PETSc 默认）；LLM 训练隐式信任域 |
| **GMRES**（主题 10） | 非对称稀疏系统（Navier-Stokes CFD、电路仿真 SPICE）的工业标准 |
| **混合精度**（主题 7-8） | FP16 条件数判据 → `torch.cuda.amp` 混合精度训练的理论门槛 |
| **FFT**（主题 12） | cuFFT；CNN Winograd 卷积 $O(n\log n)$、谱方法 PDE、音频 STFT |

### 飞腾锚点速查（12 主题，8 锚点，相邻不重复）

| 锚点 | 主题 | 角度 |
|:-----|:-----|:-----|
| **matmul 15× ⭐** | 主题 1, 6 | 矩阵-向量乘 / QR 迭代相似变换 |
| **UDOT 16.9× ⭐** | 主题 2, 9 | SVD 内积 / 回代与分解点积 |
| **Schmidt 正交化 ⭐** | 主题 3, 10 | QR 分解 / Arnoldi = Krylov 上的 MGS |
| **GEMM 9.45G ⭐** | 主题 4, 12 | Householder 子矩阵 / 预条件分解与 FFT 蝶形 |
| **分支预测** | 主题 5 | Hessenberg 化的符号选择与 deflation 判断 |
| **FP16 3.81× ⭐** | 主题 7 | 条件数决定低精度何时安全 |
| **Iron Law <2% ⭐** | 主题 8 | 向后稳定性 = $O(\epsilon)$ 的硬件级判据 |
| **TLB 4.81× ⭐** | 主题 11 | CG/Lanczos 稀疏 SpMV 的访存局部性 |

---

> **下一步**：精读 Lec 4-5（SVD，全书枢纽）+ Lec 12-15（条件数与向后稳定性，质量保证框架）
> + Lec 36（CG，ML 二阶优化接口）。
> 研究选题「**飞腾 FP16 条件数门槛下的混合精度 SVD**」——
> 当 $\kappa(A)>\epsilon_{\rm FP16}^{-1}\approx10^3$ 时截断 SVD 在哪些奇异值上失真？
> 能否用 Iron Law 判据自适应切换精度？
> 衔接 [Nocedal-Wright] 第 5 章 CG（收敛率 × $\kappa$）与 [Kress] 第 1 章（GEMM 内核）。
