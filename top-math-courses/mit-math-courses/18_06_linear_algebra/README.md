# MIT 18.06 — Linear Algebra

> **学校**：MIT | **学期**：Spring | **学分**：12 units
> **一手来源**：[catalog.mit.edu/subjects/18/#18.06](https://catalog.mit.edu/subjects/18/) + [math.mit.edu/~gs/linearalgebra/ila6/](https://math.mit.edu/~gs/linearalgebra/ila6/)（2026-08 核实）

## 课程信息
- **编号**：18.06（也有 CI 版本 18.06CI；新变体 18.C06[J] Linear Algebra and Optimization）
- **先修**：18.02 多变量微积分（不强制）
- **教材**：**Strang, *Introduction to Linear Algebra* (6th edition, 2022, Wellesley-Cambridge Press)** ★
  - 注意：不是 *Linear Algebra and Its Applications*（1988 旧版，已退役）
- **视频**：[OCW Strang 18.06 经典 34 讲](https://ocw.mit.edu/courses/18-06-linear-algebra-spring-2010/)
- **GitHub**：[mitmath/1806](https://github.com/mitmath/1806/) (Spring 2025 现行版)

## 教学大纲（6th edition 目录）
1. **Vectors and Matrices**（向量、矩阵、列空间、AB/CR 乘法）
2. **Solving Linear Equations Ax = b**（消元、A=LU、矩阵求逆）
3. **The Four Fundamental Subspaces**（四个基本子空间：列/行/零/左零空间）
4. **Orthogonality**（正交、Gram-Schmidt、A=QR）
5. **Determinants**
6. **Eigenvalues and Eigenvectors**（Ax=λx、对角化、Spectral Theorem）
7. **Singular Value Decomposition (SVD)** ★
8. **Linear Transformations**
9. **Linear Algebra in Engineering & Deep Learning**（Strang 新增深度学习章）

## 与 ML 的关联（**所有方向的核心**）
- **矩阵运算**：PyTorch / NumPy 的底层
- **特征值 / SVD**：PCA、协方差、低秩近似（→ Transformer 参数压缩）
- **Fourier 矩阵**：信号处理 / 卷积
- **Markov 矩阵**：马尔可夫链、强化学习
- **学完本课后**：能解释 attention 为什么要 softmax + 矩阵乘法

## 参考资源
- **教材（PDF）**：[math.mit.edu/~gs/linearalgebra/ila6/ila6outline.pdf](https://math.mit.edu/~gs/linearalgebra/ila6/ila6outline.pdf)
- **视频**：[OCW 34 讲完整](https://ocw.mit.edu/courses/18-06-linear-algebra-spring-2010/video_galleries/video-lectures/)
- **视频（新版）**：[OCW 18.06SC 2011](https://ocw.mit.edu/courses/18-06sc-linear-algebra-fall-2011/)
- **习题**：[OCW 18.06 problem sets + solutions](https://ocw.mit.edu/courses/18-06-linear-algebra-spring-2010/assignments/)
- **MIT 现行版**：[github.com/mitmath/1806](https://github.com/mitmath/1806/)

## 学习建议
- **节奏**：每周 3-4 小时，10-12 周完成
- **重点**：第 1-7 章（前 7 章已覆盖本科线代的核心）
- **配合**：[3Blue1Brown *Essence of Linear Algebra*](https://www.youtube.com/playlist?list=PLZHQObOWTQDPD3MizzM2xVFitgF8hE_ab)（视觉直觉）
- **进阶**：学完后读 [Axler *Linear Algebra Done Right*](../../berkeley-math-courses/math110_linear_algebra/) 做严格化

---

## 📍 在数学全景中的位置

18.06 是整条数学/ML 主线的**咽喉要道**——上承微积分的语言，下接优化、概率、数值三大支柱。

```
微积分语言                本课（线代 = "多变量"的骨架）           后续支柱
─────────                ──────────────────────────              ────────
18.01 单变量微积分  ──┐
18.02 多变量微积分  ──┼──▶  18.06 线性代数 (Strang)  ──┬──▶  Berkeley 110 (Axler 严格化)
18.03 微分方程      ──┘     ┃ 五个分解·四个子空间·SVD  │     Princeton MAT 217 (荣誉)
                       ┃                          ├──▶  Stanford CME 364A (数值/凸优化)
                       ┃                          │     UT Austin M 383E (数值线代)
                       ┃                          ├──▶  MIT 18.175 (概率/协方差)
                       ┃                          │     Oxford C7.1 (随机矩阵)
                       ┃                          └──▶  work4ai: 讲透 Transformer / 反向传播
```

- **前置**：只需会矩阵乘法和求导（18.02 多变量微积分提供"梯度"语言，但不强制）。
- **本课独有**：Strang 的**五个矩阵分解统一框架**（CR/LU/QR/S=QΛQ⁻¹/A=UΣVᵀ）和**四个基本子空间**，是其它任何线代课没有的"工程师视角全景图"。
- **后续**：学完 18.06 → (1) Berkeley 110 / Princeton 217 做严格证明；(2) Stanford CME 364A 把"正定矩阵→凸函数→优化"走通；(3) UT Austin M 383E 学数值稳定的 SVD/QR 算法。

> 一句话：**18.06 教你"看见"矩阵，后续课教你"证明"和"计算"矩阵。**

---

## 🔬 理论联系实际（公式级 ML/工程对应）

线代不是抽象体操——它是 ML 每一步运算的底层语法。以下是 5 个**精确到公式**的对应：

1. **SVD → PCA → 数据降维 / LoRA 低秩压缩**
   - 数据矩阵 SVD：$X = U\Sigma V^T$。PCA 主成分 = $V$ 的列（右奇异向量）。
   - **LoRA**（参数高效微调）：冻结权重 $W_0$，只学低秩更新 $W = W_0 + \Delta W \approx W_0 + BA$，其中 $B\in\mathbb{R}^{d\times r}, A\in\mathbb{R}^{r\times k}$，秩 $r \ll \min(d,k)$。参数量从 $dk$ 降到 $r(d+k)$。理论根基就是 **Eckart-Young 定理**：$A_k=\sum_{i=1}^k\sigma_i u_i v_i^T$ 是 Frobenius 意义下最优秩-$k$ 近似。→ [LoRA arXiv:2106.09685](https://arxiv.org/abs/2106.09685)

2. **谱定理 → 协方差矩阵 → 高斯分布的几何**
   - 对称矩阵 $S = Q\Lambda Q^T$，特征值全实、特征向量正交。
   - 样本协方差 $\Sigma = \frac{1}{n}X^TX$ 是对称半正定 → 谱分解给出主轴方向（$Q$）与各方向方差（$\Lambda$）。
   - 多元高斯 $\mathcal{N}(\mu,\Sigma)$ 的等概率面是**椭球**，椭球轴 = $\Sigma$ 的特征向量，轴长 $\propto \sqrt{\lambda_i}$。→ 这就是 PCA 的几何本质。

3. **正定矩阵 → Hessian → 局部极小值判定**
   - $f$ 的 Hessian $H = \nabla^2 f$ 在临界点 $\nabla f=0$ 处：$H$ 正定 ⟺ 局部极小；负定 ⟺ 局部极大；不定 ⟺ 鞍点。
   - 深度学习优化理论（损失景观分析）的核心就是 Hessian 的谱：$\lambda_{\min}(H)>0$ 保证收敛性，条件数 $\kappa=\lambda_{\max}/\lambda_{\min}$ 决定梯度下降收敛速度。

4. **四个基本子空间 → 超/欠定系统 → 正则化**
   - 最小二乘 $A^TA\hat{x}=A^Tb$ 的可解性取决于 $A^TA$ 是否可逆（即 $A$ 是否列满秩）。
   - 当 $A$ 列不满秩（特征共线性），$A^TA$ 奇异 → 岭回归加 $\lambda I$：$\hat{x}=(A^TA+\lambda I)^{-1}A^Tb$。$\lambda I$ 把所有特征值抬高 $\lambda$，保证正定可逆。→ 这就是 L2 正则化的线代解释。

5. **图拉普拉斯 $L=D-A$ → 谱聚类 / GNN**
   - 无向图的拉普拉斯 $L$ 对称半正定，最小特征值 $=0$（对应常向量）。
   - 第 2 小特征值 $\lambda_2$（Fiedler 值）衡量图连通性；用前 $k$ 个特征向量做聚类 = **谱聚类**。GNN 消息传递的频域分析也建立在 $L$ 的谱上。

---

## 🆕 2024-2026 最新研究（线代在 ML 的前沿）

1. **LoRA / QLoRA 低秩理论的大爆发（2023-2026）**
   - QLoRA（[arXiv:2305.14314](https://arxiv.org/abs/2305.14314)）：把冻结权重 4-bit 量化 + 低秩适配器，单卡 48GB 微调 65B 模型。核心是** NF4 数据类型**——对正态分布权重信息论最优，本质是"权重分布的量化格点 = 最优量化基"。
   - 后续衍生：DoRA（Decomposed LoRA，把 $W$ 拆成方向 × 幅度）、GaLore、PiSSA（用主奇异向量初始化 $A,B$）等，都在改进低秩近似的"秩分配"策略。这些方法的理论上限仍是 **Eckart-Young 定理**。

2. **随机矩阵理论（RMT）解释 LLM 权重谱（2024-2025）**
   - 用 **Marchenko-Pastur 定律**分析预训练权重的奇异值分布：去噪后的"信号"奇异值 vs 噪声奇异值的分界，可用 MP 律的边缘 $\sigma_\pm = (1\pm\sqrt{c})$ 来判定。→ 这解释了为什么 LoRA 用很小的秩 $r$ 就够：大部分奇异值是"噪声"。
   - Oxford 的 [Part C C7.1 Random Matrix Theory](../../oxford-math-courses/partC_c7_1_random_matrix_theory/) 正是这条线的数学基础。

3. **Tensor Decomposition（张量分解）超越矩阵 SVD（2024-2026）**
   - 多模态/长序列建模需要处理 $>2$ 阶张量。**Tucker 分解**和 **CP 分解**是 SVD 的高阶推广：$\mathcal{X}\approx\mathcal{G}\times_1 U_1 \times_2 U_2 \cdots \times_N U_N$。
   - 应用：高效 Transformer（用张量分解压缩注意力头）、持续学习（用正交子空间避免灾难性遗忘）。⚠️ 该方向理论仍在快速演化，部分收敛性证明尚未完善。

📌 **下一步**：→ [18.03 微分方程](../18_03_differential_equations/) 或直接 [18.100B 实分析](../18_100B_real_analysis/)
