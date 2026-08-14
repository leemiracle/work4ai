# Oxford Part A A12 — Numerical Analysis

> **学校**：Oxford | **学院**：Mathematical Institute
> **一手来源**：[courses.maths.ox.ac.uk](https://courses.maths.ox.ac.uk/)

## 课程信息
- **编号**：A12
- **教材**：Süli & Mayers, *An Introduction to Numerical Analysis*
- **特色**：本科数值分析

## 教学大纲
1. Polynomial interpolation
2. Numerical integration
3. Solution of nonlinear equations
4. Linear systems
5. ODE 数值方法

## 与 ML 的关联
- 标准 NA 入门

📌 **下一步**：→ [Part B B8.1 Probability, Measure and Martingales](../partB_b8_1_probability_measure_martingales/)

---

## 📍 在数学全景中的位置

- **前置**：[Part A 线性代数](../partA_a0_linear_algebra/) + 分析基础
- **本课**：Süli-Mayers 体系 → 误差分析 + 插值 + 求积 + 求根 + ODE + 数值线代
- **交叉**：[Cambridge Part IB NA](../../cambridge-math-courses/partIB_numerical_analysis/) + [UT Austin M 383E Trefethen](../../ut-austin-math-courses/m383e_numerical_linear_algebra/)

## 🔬 理论联系实际
1. **条件数 → 训练稳定性**：$\kappa(A) = \sigma_{\max}/\sigma_{\min}$，大条件数 → 梯度下降慢
2. **Newton 法 → 牛顿优化**：$x_{n+1} = x_n - H^{-1}\nabla f$，二次收敛
3. **QR 分解 → 线性回归**：比正规方程更数值稳定的最小二乘实现
4. **RK4 → Neural ODE**：用高阶 ODE 求解器做可逆前向传播

## 🆕 2024-2026 最新研究
| 子主题 | 进展 | 参考 |
|---|---|---|
| Neural ODE | 用 ODE 求解器做可逆网络 | [Chen et al. NeurIPS 2018, 1806.07366](https://arxiv.org/abs/1806.07366) ✅ |
| 自动微分 | Newton 法 + 反向传播的结合 | JAX/PyTorch 生态 |
| 混合精度训练 | fp16/bf16 下的数值稳定性 | ⚠️ 2024 |
