# Stanford MATH 51 — Linear Algebra, Multivariable Calculus, and Modern Applications

> **学校**：Stanford | **学院**：Mathematics
> **一手来源**：[mathematics.stanford.edu/academics/introductory-math-courses](https://mathematics.stanford.edu/academics/introductory-math-courses)

## 课程信息
- **编号**：MATH 51（5 units）/ 51ACE（加 1 单位辅导）
- **先修**：单变量微积分
- **教材**：自编讲义（Stanford Custom）
- **特色**：**工学院线代 + 多变量标准序列**——线代和多变量**并行**讲授

## 教学大纲
1. Linear systems & matrices
2. Vector spaces, linear transformations
3. Eigenvalues & diagonalization
4. Multivariable differentiation
5. Gradients & optimization
6. Lagrange multipliers
7. Multivariable integration
8. SVD & PCA applications

## 与 ML 的关联
- **工学院线代 + 多变量基础**——CS/工程系通用
- 学完后：能看懂 PyTorch 的 backward 实现

## 参考资源
- Stanford Canvas 课程页面（需注册）
- 配合：3Blue1Brown 线代本质

📌 **下一步**：→ [MATH 113 Linear Algebra Theory](../math113_linear_algebra_theory/)（严格版）

---

## 📍 在数学全景中的位置（多变量部分）

MATH 51 是 Stanford 工学院/CS 系的核心数学课——把**线代和多变量微积分并行**讲授。前置单变量微积分；本笔记聚焦**多变量微积分部分**（第 4-7 单元：多元微分/梯度/优化/积分）。线代部分归其他 agent。多变量部分与 [MIT 18.02](../../mit-math-courses/18_02_multivariable_calculus/) / [Berkeley MATH 53](../../berkeley-math-courses/math53_multivariable/) 内容等价。MATH 51 的特色是把线代（SVD/PCA）与多变量（梯度优化）**有机融合**，第 8 单元直接讲 SVD 在数据降维中的应用。

## 🔬 理论联系实际（多变量部分）

| 概念 | ML / 工程应用 | 公式对应 |
|---|---|---|
| **多元微分 / 梯度** | 梯度下降 → SGD/Adam | $\mathbf{w} \leftarrow \mathbf{w} - \eta\nabla f$ |
| **多元链式法则** | 反向传播 / autograd | $\frac{\partial L}{\partial \mathbf{w}} = J^T\frac{\partial L}{\partial \mathbf{y}}$ |
| **Lagrange 乘子** | SVM / 约束优化 | $\nabla f = \lambda\nabla g$ |
| **多元 Taylor（二阶）** | Newton 法 / loss landscape | $f \approx f_0 + \nabla f^T\Delta + \frac{1}{2}\Delta^T H\Delta$ |
| **SVD + 梯度** | PCA + 优化（MATH 51 特色） | 梯度在 PCA 主成分上的投影 |

## 🆕 2024-2026 最新研究

1. **Adam 与自适应梯度**（[arXiv:1412.6980](https://arxiv.org/abs/1412.6980)）：Adam 用梯度的一阶/二阶矩做自适应步长，本质是对 Hessian 对角元的隐式估计。2024 年 Schedule-Free 等新优化器延续了"梯度信号处理"的思路——直接依赖 MATH 51 的梯度概念。
2. **Flow Matching 的向量场 = 梯度场**（[arXiv:2210.02747](https://arxiv.org/abs/2210.02747)）：生成模型学习 $\mathbb{R}^n$ 上的向量场，这是多变量微分/梯度概念的直接工程应用。Stable Diffusion 3（2024）基于 Rectified Flow。
3. **二阶优化的工程复兴**（⚠️ 2024+）：K-FAC/Shampoo 在 LLM 训练中用 Hessian 的结构化近似，依赖 MATH 51 的 Hessian + 特征值分析（与线代 SVD 结合）。
