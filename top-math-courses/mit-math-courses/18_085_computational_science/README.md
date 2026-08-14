# MIT 18.085 — Computational Science and Engineering I

> **学校**：MIT | **学期**：Fall | **学分**：12 units
> **一手来源**：[catalog.mit.edu/subjects/18/#18.085](https://catalog.mit.edu/subjects/18/) + [OCW 18.085 Prof. Strang](https://ocw.mit.edu/courses/18-085-computational-science-and-engineering-i-fall-2008/)

## 课程信息
- **编号**：18.085 / 18.0851（研究生版本）
- **先修**：18.06 线性代数（**强烈推荐**）
- **教材**：**Strang, *Computational Science and Engineering* (Wellesley-Cambridge, 2007)** ★
- **视频**：[OCW Strang 18.085 完整讲座](https://ocw.mit.edu/courses/18-085-computational-science-and-engineering-i-fall-2008/video_galleries/video-lectures/)
- **配书**：Strang, *Introduction to Linear Algebra*（同作者，章节呼应）

## 教学大纲
1. **Four subspaces from A = CR**（复习线代）
2. **Differential equations as L u = f**（微分方程 = 线性算子）
3. **Finite differences**（差分：forward / backward / centered）
4. **Boundary value problems**（边值问题，离散化）
5. **Laplace's equation & Poisson's equation**
6. **Finite element method (FEM) 入门**
7. **Graph Laplacian**（图拉普拉斯矩阵）
8. **Fourier series & FFT**（傅里叶分析、快速 Fourier 变换）
9. **Spectral methods**（谱方法）
10. **Computational linear algebra**（迭代法、Krylov 子空间）

## 与 ML 的关联（**应用数学工程师必修**）
- **图拉普拉斯**（Graph Laplacian）：图神经网络、谱聚类
- **FFT**：信号处理、卷积加速
- **Krylov 子空间**：求解大矩阵线性系统（语言模型的 attention 加速）
- **离散化方法**：把连续 ML 模型（如 diffusion）变成可训的离散算法
- **学完本课后**：能解释 Transformer 的 attention 为何是 $O(n^2)$ 与能否降到 $O(n)$

## 参考资源
- **教材（免费 PDF 部分）**：[math.mit.edu/~gs/cse/](https://math.mit.edu/~gs/cse/)
- **视频**：[OCW Strang 18.085 30+ 讲](https://www.youtube.com/playlist?list=PLUHGAjyLQQ40qI80S8SQjyXgdO7SlZ7nO)
- **习题集**：[OCW 18.085 assignments](https://ocw.mit.edu/courses/18-085-computational-science-and-engineering-i-fall-2008/assignments/)
- **GitHub**：[ocw-18.085-resources](https://ocw.mit.edu/courses/18-085-computational-science-and-engineering-i-fall-2008/)

## 学习建议
- **节奏**：每周 4-5 小时，10-12 周完成
- **Strang 风格**：直觉先行，证明够用即可
- **重点**：Fourier / Laplacian / FEM（这三个在 ML 里出现频率最高）
- **配合**：[UT Austin M 383E Numerical Methods I](../../ut-austin-math-courses/math_ga_2010_numerical_methods_I/)（更现代的数值线代）

📌 **下一步**：→ [18.701 代数 I](../18_701_algebra_I/) 或 [UT Austin M 383E](../../ut-austin-math-courses/math_ga_2010_numerical_methods_I/)

---

## 📍 在数学全景中的位置

- **前置**：[MIT 18.06 线代](../18_06_linear_algebra/)（四子空间、SVD）
- **本课**：用线代统一应用数学——**差分 → 矩阵 → PDE / FFT / FEM / 图拉普拉斯**
- **后续**：[UT Austin M 383E 数值线代](../../ut-austin-math-courses/m383e_numerical_linear_algebra/)（Trefethen & Bau）/ [ETH 401-3651 SDE](../../eth-math-courses/e401_3651_numerical_sde/)（diffusion）

---

## 🔬 理论联系实际

1. **图拉普拉斯 $L = D - A$ → 谱聚类、GNN 正则化**
2. **FFT → CNN 卷积加速**（conv = IFFT(FFT·FFT)）
3. **泊松方程离散化 → 图半监督学习**
4. **热方程 → diffusion model 的 PDE 根基**（→ [ETH 401-3651](../../eth-math-courses/e401_3651_numerical_sde/)）
5. **Krylov 子空间 → attention 线性近似**（→ [M 383E](../../ut-austin-math-courses/m383e_numerical_linear_algebra/)）

---

## 🆕 2024-2026 最新研究

- **GNN = 图上的谱卷积**：ChebNet、GCN 与图拉普拉斯特征基的深度联系
- **PINN（物理信息神经网络）**：用神经网络解 PDE，与传统 FEM 互补
- **Neural Operator（FNO, DeepONet）**：学习参数化 PDE 的解算子
- **线性 attention**：Krylov 子空间 / 核技巧把 $O(n^2)$ 降到 $O(n)$
- **图上扩散模型**：score-based 生成在图结构数据上的推广
