# MIT 18.02 — Multivariable Calculus

> **学校**：MIT | **学期**：Fall/Spring | **学分**：12 units
> **一手来源**：[catalog.mit.edu/subjects/18/#18.02](https://catalog.mit.edu/subjects/18/) + [OCW 18.02 Prof. Denis Auroux](https://ocw.mit.edu/courses/18-02-multivariable-calculus-fall-2007/)

## 课程信息
- **编号**：18.02 / 18.02A
- **先修**：18.01 单变量微积分
- **教材**：Edwards & Penney, *Multivariable Calculus*；OCW Auroux 讲义
- **视频**：[Auroux 18.02 双语字幕](https://ocw.mit.edu/courses/18-02-multivariable-calculus-fall-2007/video_galleries/video-lectures/)

## 教学大纲
1. **Vectors and matrices**（点积、叉积、矩阵）
2. **Partial derivatives**（偏导数、链式法则、梯度）
3. **Directional derivatives & gradient**
4. **Lagrange multipliers**（约束优化基础）
5. **Double and triple integrals**
6. **Polar, cylindrical, spherical coordinates**
7. **Line integrals**（线积分）
8. **Surface integrals & flux**
9. **Green's, Stokes', Divergence Theorems**（三大定理）

## 与 ML 的关联
- **梯度 / 偏导**（ML 论文的核心工具）
- **多元 Taylor 展开**（数值优化、Hessian 分析）
- **Lagrange 乘子**（SVM 推导）
- **学完本课后**：能读懂反向传播的链式法则证明

## 参考资源
- **教材**：[OCW 18.02 Readings](https://ocw.mit.edu/courses/18-02-multivariable-calculus-fall-2007/readings/)
- **视频**：[Auroux 完整 35 讲](https://www.youtube.com/playlist?list=PL4C4C8A7D06566F38)
- **习题**：[OCW 18.02 assignments](https://ocw.mit.edu/courses/18-02-multivariable-calculus-fall-2007/assignments/)

## 学习建议
- **重点**：偏导 + 梯度 + 链式法则（ML 必备）
- **跳过**：Green/Stokes/Divergence 三大定理（高阶几何用得到）

📌 **下一步**：→ [18.06 线性代数](../18_06_linear_algebra/) 或 [18.03 微分方程](../18_03_differential_equations/)

---

## 📍 在数学全景中的位置

18.02 是 18.01 单变量微积分的**多维推广**。前置是 18.01（单变量极限/导数/积分/Taylor）；本课把导数推广为**偏导 → 梯度 → Jacobian → Hessian**，把积分推广为**重积分 → 线/面积分**，并用三大定理（Green/Stokes/Divergence）统一它们。学完后顺接到 **18.06 线性代数**（梯度/矩阵结合 → 矩阵微积分）、**18.03 微分方程**（梯度场 → 动力系统）。18.02 的核心——**多元链式法则**——是反向传播的直接数学语言。

## 🔬 理论联系实际

| 多变量概念 | ML / 工程应用 | 公式对应 |
|---|---|---|
| **梯度 $\nabla f$** | 梯度下降 → SGD/Adam | $\mathbf{w}_{t+1} = \mathbf{w}_t - \eta \nabla f(\mathbf{w}_t)$ |
| **Jacobian 矩阵** | **反向传播** / autograd | $\frac{\partial \mathbf{y}}{\partial \mathbf{x}} = [\partial y_i/\partial x_j]$ |
| **Hessian 矩阵** | 二阶优化 / 收敛分析 | $\nabla^2 f = [\partial^2 f/\partial x_i \partial x_j]$ |
| **多元链式法则** | 深层网络梯度传播 | $\frac{\partial L}{\partial \mathbf{w}_1} = \frac{\partial L}{\partial \mathbf{h}} \cdot \frac{\partial \mathbf{h}}{\partial \mathbf{w}_1}$ |
| **Lagrange 乘子** | SVM / 约束优化 | $\nabla f = \lambda \nabla g$（KKT 条件的基础） |
| **方向导数 $D_{\mathbf{u}}f$** | 线搜索方向 | $D_{\mathbf{u}}f = \nabla f \cdot \mathbf{u}$ |

## 🆕 2024-2026 最新研究

1. **Flow Matching 与向量场**：Flow Matching（[arXiv:2210.02747](https://arxiv.org/abs/2210.02747), Lipman et al., ICLR 2023）把生成模型的核心数学归结为**学习一个向量场（即梯度场）**，使得 ODE $\frac{d\mathbf{x}}{dt} = v_t(\mathbf{x})$ 把噪声分布变换为数据分布。Stable Diffusion 3（2024）采用的 Rectified Flow 正是这一框架。18.02 的梯度/向量场概念是其直接基础。
2. **Jacobian-free 反向传播替代方案**（⚠️ 具体方向 2024+ 活跃）：自动微分/反向传播本质是 Jacobian 矩阵的链式乘积。2024-2025 年对大模型的梯度计算有 memory-efficient 的研究（如 reversible layers），核心数学仍是 18.02 的多元链式法则的工程优化。
3. **Hessian-free 优化的复兴**：二阶方法（K-FAC, Shampoo）在 LLM 训练中重新受到关注（2024），它们用 Hessian 的低秩/结构化近似——这依赖 18.02 的 Hessian 概念和特征值分析。
