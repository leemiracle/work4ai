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

📌 **下一步**：→ [18.03 微分方程](../18_03_differential_equations/) 或直接 [18.100B 实分析](../18_100B_real_analysis/)
