# Stanford CME 108 — Introduction to Scientific Computing

> **学校**：Stanford | **学院**：ICME
> **一手来源**：[icme.stanford.edu](https://icme.stanford.edu)

## 课程信息
- **编号**：CME 108 / CME 308（高阶版）
- **先修**：MATH 51 + 编程基础
- **教材**：Quarteroni, *Numerical Mathematics*；Heath, *Scientific Computing*
- **特色**：**应用数学工程师的数值入门**

## 教学大纲
1. **Floating-point arithmetic**（浮点数误差）
2. **Linear systems**（条件数、稳定性）
3. **Eigenvalues & SVD**（数值版）
4. **Nonlinear equations**（Newton, fixed-point）
5. **Optimization**（gradient descent 入门）
6. **Interpolation & approximation**
7. **Numerical integration**（quadrature）
8. **ODE & PDE 数值方法**
9. **Monte Carlo methods**

## 与 ML 的关联
- **条件数** → 神经网络梯度的稳定性
- **SVD 数值版** → Transformer 低秩
- **Monte Carlo** → 推断、扩散模型

## 参考资源
- Quarteroni, *Numerical Mathematics*
- Heath, *Scientific Computing*
- MIT 对照：[MIT 18.085](../../mit-math-courses/18_085_computational_science/)
- UT Austin 对照：M 383E（待写/未落盘）

📌 **下一步**：→ [STAT 116 Probability Theory](../stat116_probability_theory/)

---

## 📍 在数学全景中的位置

- **前置**：[Math 51 线代 + 多变量](../math51_linear_multivariable/)
- **本课**：误差分析 / 插值 / 数值积分 / ODE 求解 / 稀疏矩阵——**工程计算基础**
- **后续**：[CME 364A 凸优化](../cme364A_convex_optimization/) / [UT Austin M 383E 数值线代](../../ut-austin-math-courses/m383e_numerical_linear_algebra/)（线代深入）

---

## 🔬 理论联系实际

1. **浮点误差 → 混合精度训练**（fp16/bf16 的数值稳定性与 loss scaling）
2. **ODE 求解 → Neural ODE**（Chen 2018，连续深度网络）
3. **稀疏矩阵 → 大规模推荐系统**
4. **数值积分 → 贝叶斯推断**（MCMC quadrature）
5. **误差传播 → 梯度爆炸/消失的数值根源**

---

## 🆕 2024-2026 最新研究

- **Neural ODE**（Chen 2018 → 2024）：连续深度网络 + 伴随法反向传播，内存 $O(1)$
- **混合精度科学计算**：Tensor Core 的矩阵乘精度分析（fp16/bf16 下的 Householder QR）
- **JAX / Diffrax**：可微物理引擎，自动微分 + ODE/SDE 求解器一体化
- **Physics-Informed NN**：神经网络解 PDE，与传统数值方法互补
