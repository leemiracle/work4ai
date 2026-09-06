# UT Austin M 427L — Vector Calculus

> **学校**：UT Austin
> **一手来源**：[math.utexas.edu](https://math.utexas.edu) + catalog.utexas.edu

## 课程信息
- **编号**：M 427L
- **先修**：M 408D
- **教材**：Colley, *Vector Calculus*；或 Stewart 多变量部分

## 教学大纲
1. Vectors & 3D geometry
2. Partial derivatives, gradient
3. Multiple integrals
4. Line & surface integrals
5. Green's, Stokes', Divergence 定理

## 与 ML 的关联
- 梯度 / Jacobian / 多元 Taylor
- 学完后：能推导反向传播

📌 **下一步**：→ [M 340L Linear Algebra](../m340l_linear_algebra/)

---

## 📍 在数学全景中的位置

M 427L 是 UT Austin 的多变量/向量微积分课，定位与 [MIT 18.02](../../mit-math-courses/18_02_multivariable_calculus/) / [Berkeley MATH 53](../../berkeley-math-courses/math53_multivariable/) 对等。前置 M 408D（单变量微积分序列）；本课把单变量推广到多变量——偏导 → 梯度 → Jacobian → 重积分 → 三大定理（Green/Stokes/Divergence）。对 ML 从业者，核心收获是**梯度 = 优化方向**、**Jacobian = 反向传播**、**Hessian = 收敛分析**。

## 🔬 理论联系实际

| 向量微积分概念 | ML / 工程应用 | 公式对应 |
|---|---|---|
| **梯度 $\nabla f$** | 梯度下降 → SGD/Adam | $\mathbf{w}_{t+1} = \mathbf{w}_t - \eta\nabla f$ |
| **Jacobian 矩阵** | 反向传播 / autograd | $J = [\partial y_i/\partial x_j]$ |
| **Hessian** | 二阶优化 / 鞍点分析 | $\nabla^2 f = [\partial^2 f/\partial x_i\partial x_j]$ |
| **方向导数** | 线搜索方向 | $D_{\hat{\mathbf{u}}}f = \nabla f \cdot \hat{\mathbf{u}}$ |
| **多元链式法则** | 深层网络梯度传播 | $\frac{\partial L}{\partial w} = \frac{\partial L}{\partial y}\frac{\partial y}{\partial w}$ |
| **散度定理** | 扩散模型概率流 | $\nabla\cdot(p\mathbf{v})$ 连续性方程 |

## 🆕 2024-2026 最新研究

1. **Flow Matching 的向量场学习**（[arXiv:2210.02747](https://arxiv.org/abs/2210.02747)）：生成模型的核心是学习 $\mathbb{R}^n$ 上的向量场（梯度场），使 ODE $\dot{\mathbf{x}} = v_t(\mathbf{x})$ 把噪声变为数据。Stable Diffusion 3（2024）的 Rectified Flow 基于此框架。M 427L 的梯度/向量场概念是其直接基础。
2. **Adam 与条件数**（[arXiv:1412.6980](https://arxiv.org/abs/1412.6980)）：Adam 用梯度二阶矩自适应缩放步长，本质是对 Hessian 对角元的隐式估计——缓解条件数大的"狭谷"损失函数的收敛问题。
3. **扩散模型的散度/连续性方程**（[arXiv:2006.11239](https://arxiv.org/abs/2006.11239), [arXiv:2011.13456](https://arxiv.org/abs/2011.13456)）：DDPM 和 Score-SDE 用散度定理推导概率流 ODE $\frac{\partial p}{\partial t} + \nabla\cdot(p\mathbf{v}) = 0$——这是 M 427L 散度定理的直接 ML 应用。
