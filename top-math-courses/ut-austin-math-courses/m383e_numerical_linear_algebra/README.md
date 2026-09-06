# UT Austin M 383E — Numerical Analysis: Linear Algebra

> **学校**：UT Austin | **学期**：Fall (研究生)
> **一手来源**：[catalog.utexas.edu](https://catalog.utexas.edu/general-information/coursesatoz/m/) + [math.utexas.edu/information/graduate-students/preliminary-exams](https://math.utexas.edu/information/graduate-students/preliminary-exams)

## 课程信息
- **编号**：M 383E / CSEM 383E / CS 383C（三院互认）
- **先修**：M 341（线代）+ M 365C（实分析推荐）+ 编程基础
- **教材**：**Trefethen & Bau, *Numerical Linear Algebra*** ★；配 Demmel
- **特色**：**UT Austin Numerical Analysis Prelim**——**数值线代顶级课**

## 教学大纲
1. **Matrix-vector / matrix-matrix 乘法复杂度**
2. **QR factorization**（Gram-Schmidt, Householder）★
3. **Conditioning & stability** ★
4. **SVD 与应用**（PCA, 低秩近似, 伪逆）★
5. **LU factorization** + pivoting
6. **Eigenvalue computation** (QR algorithm, power iteration)
7. **Iterative methods** (Krylov 子空间, CG, GMRES)
8. **Preconditioning**
9. **Sparse matrices**
10. **Applications**: PageRank, recommender systems, ML

## 与 ML 的关联（**ML 工程师必修**）
- **SVD** → Transformer 低秩 / PCA / 协方差
- **数值稳定性** → PyTorch 算子设计
- **Krylov** → attention 加速
- 学完后：理解 `torch.linalg.*` 实现细节

## 参考资源
- **Trefethen & Bau, *Numerical Linear Algebra*** (SIAM, 1997) ★
- Demmel, *Applied Numerical Linear Algebra* (SIAM)
- Quarteroni, *Numerical Mathematics* (Springer)
- MIT 对照：[MIT 18.335J](../../mit-math-courses/)

## 学习建议
- **Trefethen & Bau 是 ML 工程师的最佳数值入门书**（361 页）
- **节奏**：每周 5-7 小时，12-14 周

📌 **下一步**：→ [M 385C Theory of Probability](../m385c_theory_of_probability/)

---

## 📍 在数学全景中的位置

- **前置**：[M 341 / M 340L 线性代数](../m340l_linear_algebra/)
- **本课**：QR / SVD / 条件数 / Krylov 子空间 / 迭代法——**数值线代核心**
- **后续**：[MIT 18.085 CSE](../../mit-math-courses/18_085_computational_science/)（应用）/ [ETH 401-3651 SDE](../../eth-math-courses/e401_3651_numerical_sde/)（随机数值）

---

## 🔬 理论联系实际

1. **SVD → PCA / Transformer 低秩 / LoRA 微调**（Eckart-Young 定理）
2. **条件数 → 神经网络训练稳定性**（梯度爆炸 = 大条件数）
3. **Krylov 子空间 → attention 线性近似**（Performer, Linear Attention）
4. **随机化 SVD → 大规模推荐系统**（Halko-Martinsson-Tropp 2009）
5. **QR 算法 → PageRank**（幂迭代法求特征值）

---

## 🆕 2024-2026 最新研究

- **随机化 SVD**（arXiv 0909.4061）：$O(mn\log k)$ 代替 $O(mn^2)$，已验证 11.6× 加速
- **Transformer 低秩**：权重矩阵的 SVD 分析 → LoRA 微调（Hu et al. 2021）
- **Krylov Attention**：用 Krylov 子空间把 $O(n^2)$ attention 降到 $O(n)$
- **量子线性代数**：HHL 算法的条件数依赖性（数值稳定性的量子推广）
- **混合精度 SVD**：fp16/bf16 下的 Householder QR 稳定性分析
