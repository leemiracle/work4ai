# UT Austin M 378K — Numerical Analysis

> **学校**：UT Austin
> **一手来源**：[catalog.utexas.edu](https://catalog.utexas.edu/general-information/coursesatoz/m/)

## 课程信息
- **编号**：M 378K / M 348（简化版）
- **先修**：M 340L + M 325K（推荐）
- **教材**：Burden & Faires, *Numerical Analysis*；或 Sauer

## 教学大纲
1. **Floating-point arithmetic**
2. **Roots of equations**（bisection, Newton）
3. **Linear systems**（LU, condition number）
4. **Interpolation** (Lagrange, spline)
5. **Numerical integration**
6. **ODE 数值方法**（Euler, Runge-Kutta）
7. **Eigenvalue 数值方法**

## 与 ML 的关联
- 神经网络数值稳定性
- 学完后：理解 PyTorch 算子实现

## 参考资源
- Burden & Faires, *Numerical Analysis* (10th)
- Sauer, *Numerical Analysis*

📌 **下一步**：→ [M 383E Numerical Linear Algebra graduate](../m383e_numerical_linear_algebra/)

---

## 📍 在数学全景中的位置

- **前置**：线性代数 + 微积分 + 编程
- **本课**：Burden-Faires 体系 → 求根 + 插值 + 积分 + ODE + 线性系统（本科级 NA）
- **后续**：[M 383E Trefethen & Bau](../m383e_numerical_linear_algebra/)（研究生级，招牌课）

## 🔬 理论联系实际
1. **条件数 → 训练数值稳定性**：大 $\kappa$ → 梯度消失/爆炸
2. **Newton 法 → 优化**：二阶方法 $H^{-1}\nabla f$
3. **RK4 → Neural ODE**：高阶 ODE 求解器
4. **迭代法 → 大规模优化**：Jacobi/Gauss-Seidel → 共轭梯度

## 🆕 2024-2026 最新研究
| 子主题 | 进展 | 参考 |
|---|---|---|
| Neural ODE | 数值 ODE 求解器作为可逆层 | [1806.07366](https://arxiv.org/abs/1806.07366) ✅ |
| 混合精度 | fp16 数值稳定性分析 | ⚠️ 2024 |
| 可微分物理 | 数值方法 + 自动微分 | JAX 生态 ✅ |
