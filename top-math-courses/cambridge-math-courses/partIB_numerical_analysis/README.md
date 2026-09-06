# Cambridge Part IB — Numerical Analysis

> **学校**：Cambridge | **学期**：Lent (大二春)
> **一手来源**：[maths.cam.ac.uk/undergrad/files/coursesIB.pdf](https://www.maths.cam.ac.uk/undergrad/files/coursesIB.pdf)

## 课程信息
- **学期**：Lent (16 lectures)
- **教材**：Iserles, *A First Course in the Numerical Analysis of Differential Equations*
- **特色**：本科数值分析（Cambridge 强项之一）

## 教学大纲
1. **Round-off error & conditioning**
2. Polynomial interpolation
3. **Quadrature** (numerical integration)
4. **Solution of nonlinear equations** (Newton, fixed point)
5. **ODE 数值方法** (Euler, Runge-Kutta)
6. **Linear systems** (LU, QR)
7. **Eigenvalues 数值方法**
8. **Finite difference for PDE**

## 与 ML 的关联
- 神经网络反向传播的数值稳定性
- 学完后：理解 PyTorch 算子的数值实现

## 参考资源
- Iserles, *A First Course in NDE* (2nd ed, CUP)
- Trefethen & Bau, *Numerical Linear Algebra*

📌 **下一步**：→ [Part II Probability and Measure](../partII_probability_measure/) 或 [Part II Numerical Analysis](../partII_numerical_analysis/)

---

## 📍 在数学全景中的位置

- **前置**：Part IA Analysis I + Part IB Linear Algebra
- **本课**：插值 / 求积 / ODE 收敛性证明——**严格数值分析**
- **后续**：[Cambridge Part II NA](../partII_numerical_analysis/)（Krylov/谱方法）/ [UT Austin M 383E](../../ut-austin-math-courses/m383e_numerical_linear_algebra/)（数值线代）

---

## 🔬 理论联系实际

1. **Gauss 求积 → 贝叶斯积分 / 物理仿真**
2. **RK4 → Neural ODE**（Chen 2018，连续深度网络）
3. **稳定性分析 → 深度网络训练**（stiff 梯度流）
4. **Chebyshev 插值 → 谱方法**（高精度 PDE）

---

## 🆕 2024-2026 最新研究

- **Neural ODE**：连续深度网络用自适应 RK / DOP853 求解
- **JAX Diffrax**：可微 ODE/SDE 求解器，自动微分一体化
- **Physics-Informed NN**：神经网络 + 数值方法互补解 PDE
- **自适应步长学习率**：数值 ODE 的步长自适应启发了学习率调度
