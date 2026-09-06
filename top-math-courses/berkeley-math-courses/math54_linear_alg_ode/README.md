# UC Berkeley MATH 54 — Linear Algebra and Differential Equations

> **学校**：Berkeley
> **一手来源**：[math.berkeley.edu/courses](https://math.berkeley.edu/courses)

## 课程信息
- **编号**：MATH 54 / N54
- **先修**：MATH 53
- **教材**：Lay, Lay, McDonald, *Linear Algebra and Its Applications*
- **特色**：**工学院线代 + ODE 一锅炖**

## 教学大纲
**线代部分**：
1. Linear equations, matrices
2. Determinants
3. Vector spaces
4. Eigenvalues & eigenvectors
5. Orthogonality & least squares
6. Symmetric matrices & quadratic forms

**ODE 部分**：
7. First-order ODE
8. Second-order linear ODE
9. Linear systems
10. Laplace 变换

## 与 ML 的关联
- 工程师线代基础
- 学完后：能从矩阵视角理解神经网络权重

📌 **下一步**：→ [MATH 104 Analysis](../math104_analysis/) 或 [MATH 110 Linear Algebra 严格版](../math110_linear_algebra/)

---

## 📍 在数学全景中的位置

MATH 54 是 Berkeley 工学院的"线代 + ODE 一锅炖"组合课。前置 MATH 53；本笔记**只聚焦 ODE 部分**（第 7-10 单元），线代部分归其他 agent 管理。ODE 部分覆盖一阶/二阶 ODE、线性系统、Laplace 变换——与 [MIT 18.03](../../mit-math-courses/18_03_differential_equations/) 内容重叠但更紧凑。学完后能理解 Neural ODE、RNN 稳定性、扩散模型的 SDE 基础。

## 🔬 理论联系实际（ODE 部分）

| ODE 概念 | ML / 工程应用 | 公式对应 |
|---|---|---|
| **一阶线性 ODE** | Neural ODE | $\dot{\mathbf{h}} = f_\theta(\mathbf{h}, t)$ |
| **二阶 ODE（阻尼振荡）** | 物理仿真 / 动力系统 | $\ddot{x} + p\dot{x} + qx = 0$ |
| **线性系统 + 特征值** | RNN/Mamba 连续化 | $\dot{\mathbf{x}} = A\mathbf{x}$，特征值 → 稳定性 |
| **Laplace 变换** | 信号处理 / 控制论 | $\mathcal{L}\{f\}(s) = \int_0^\infty e^{-st}f(t)\,dt$ |
| **Euler/数值法** | Neural ODE solver | $\mathbf{h}_{n+1} = \mathbf{h}_n + hf(\mathbf{h}_n)$ |

## 🆕 2024-2026 最新研究

1. **Neural ODE**（[arXiv:1806.07366](https://arxiv.org/abs/1806.07366)）：把 ResNet 的离散层重新解读为 ODE $\dot{\mathbf{h}} = f(\mathbf{h})$ 的 Euler 离散化，用 adjoint 方法实现 $O(1)$ 内存训练。2024-2025 年的连续标准化流和扩散模型都基于此框架。
2. **Mamba = 离散化的线性 ODE**（[arXiv:2312.00752](https://arxiv.org/abs/2312.00752)）：Mamba 的状态空间模型 $\dot{\mathbf{h}} = A\mathbf{h} + B\mathbf{x}$ 是线性常系数 ODE，ZOH 离散化后变 RNN。MATH 54 的线性 ODE 系统 + 特征值分析是其直接数学基础。
3. **扩散模型的 SDE/ODE 视角**（[arXiv:2006.11239](https://arxiv.org/abs/2006.11239), [arXiv:2011.13456](https://arxiv.org/abs/2011.13456)）：DDPM 和 Score-SDE 把生成建模归结为求解反向时间 ODE/SDE，依赖 MATH 54 的一阶 ODE 和数值求解概念。
