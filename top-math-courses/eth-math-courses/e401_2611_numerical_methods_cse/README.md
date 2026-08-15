# ETH 401-2611 — Numerical Methods for CSE

> **学校**：ETH Zurich | **学院**：D-MATH (与 R. Hiptmair 等关联)
> **一手来源**：[vvz.ethz.ch](https://www.vvz.ethz.ch) + [math.ethz.ch/studies/course-websites](https://math.ethz.ch/studies/course-websites/course-list-d-math.html)

## 课程信息
- **编号**：401-2611-00L
- **教材**：Quarteroni, *Numerical Mathematics*；Süli & Mayers
- **特色**：**ETH 应用数学招牌课**——CSE 硕士核心

## 教学大纲
1. Floating-point arithmetic
2. **Linear systems**（LU, QR, conditioning）
3. **Eigenvalue / SVD 数值方法**
4. **Iterative methods**（Krylov, CG, GMRES）
5. **Nonlinear equations**（Newton）
6. **Polynomial interpolation**
7. **Numerical integration**（Gaussian quadrature）
8. **ODE**（Runge-Kutta, multistep）
9. **PDE 数值方法**（finite differences, finite elements 入门）
10. **FFT & spectral methods**

## 与 ML 的关联
- 数值方法的标准训练
- 学完后：能理解 PyTorch 算子的底层

## 参考资源
- Quarteroni, *Numerical Mathematics* (2nd ed, Springer)
- Trefethen & Bau, *Numerical Linear Algebra*
- MIT 对照：[18.085 CSE](../../mit-math-courses/18_085_computational_science/)
- UT Austin 对照：M 383E（待写/未落盘）

📌 **下一步**：→ [401-3651 Numerical Solution of SDEs](../e401_3651_numerical_sde/)

---

## 📍 在数学全景中的位置

- **前置**：线性代数 + 多元微积分 + 编程能力
- **本课**：插值 → 数值积分 → ODE/PDE 数值解 → FEM/FDM → 谱方法
- **交叉**：[UT Austin M 383E Trefethen](../../ut-austin-math-courses/m383e_numerical_linear_algebra/)（数值线代）+ [Princeton MAT 322](../../princeton-math-courses/mat322_pde/)（PDE 理论）

## 🔬 理论联系实际
1. **FEM → PINN / Neural Operators**：PDE 数值方法启发用 NN 解 PDE（Fourier Neural Operator [2010.08895](https://arxiv.org/abs/2010.08895) ✅）
2. **CG/GMRES → 注意力加速**：大规模稀疏线性系统的 Krylov 方法
3. **Chebyshev 逼近 → 谱归一化**：GAN 的 Lipschitz 约束与算子范数估计
4. **数值积分 → 蒙特卡洛方法**：高维积分的随机化

## 🆕 2024-2026 最新研究
| 子主题 | 进展 | 参考 |
|---|---|---|
| Fourier Neural Operator | 频域学习 PDE 解算子 | [Li et al. 2021, 2010.08895](https://arxiv.org/abs/2010.08895) ✅ |
| Physics-Informed NN | 数值方法的神经化 | [Raissi et al. 2019](https://arxiv.org/abs/1711.10561) ✅ |
| 自适应网格 + ML | 用 ML 引导网格加密 | ⚠️ 2024 |
