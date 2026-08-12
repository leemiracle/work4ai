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
