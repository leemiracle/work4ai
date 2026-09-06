# MIT 18.03 — Differential Equations

> **学校**：MIT | **学期**：Spring | **学分**：12 units
> **一手来源**：[catalog.mit.edu/subjects/18/#18.03](https://catalog.mit.edu/subjects/18/) + [OCW 18.03 Prof. Arthur Mattuck](https://ocw.mit.edu/courses/18-03-differential-equations-spring-2010/)

## 课程信息
- **编号**：18.03 / 18.032（honors，前身 18.034）
- **先修**：18.01 + 18.02
- **教材**：Boyce & DiPrima, *Elementary Differential Equations and Boundary Value Problems*；Edwards & Penney
- **视频**：[OCW Mattuck 18.03 经典 33 讲](https://ocw.mit.edu/courses/18-03-differential-equations-spring-2010/video_galleries/video-lectures/)

## 教学大纲
1. **First-order ODE**（一阶：可分离 / 线性 / 全微分 / 积分因子）
2. **Second-order linear ODE**（齐次 / 非齐次 / 阻尼振荡）
3. **Linear ODE 系统与矩阵**
4. **Laplace 变换**
5. **Fourier 级数入门**
6. **PDE 入门**：热传导 / 波动 / Laplace
7. **非线性系统 & 稳定性**（相平面、相位图）
8. **数值方法**（Euler / Runge-Kutta）

## 与 ML 的关联
- **ODE / 动力系统**：神经 ODE（Neural ODE, Chen 2018）
- **PDE**：扩散模型（DDPM）的数学基础
- **稳定性分析**：GAN 训练稳定性
- **学完本课后**：理解 Neural ODE / Score-Based Models 的数学

## 参考资源
- **视频**：[OCW Mattuck 33 讲](https://www.youtube.com/playlist?list=PLyIrvM2 OL_OHHXzygwmskEKgRX6L_Vwh)
- **习题**：[OCW 18.03 problem sets](https://ocw.mit.edu/courses/18-03-differential-equations-spring-2010/assignments/)
- **MIT 现行版**：[18.031/18.032 新版](https://math.mit.edu/classes/18.03/)

## 学习建议
- **节奏**：每周 3-5 小时，10-12 周完成
- **重点**：一阶/二阶 ODE + Laplace（ML 论文里最常用）
- **跳过**：复杂 PDE 数值方法（留到 18.085 / UT Austin M 383E）

📌 **下一步**：→ [18.06 线性代数](../18_06_linear_algebra/) 或 [18.100B 实分析](../18_100B_real_analysis/)

---

## 📍 在数学全景中的位置

18.03 是从**静态**数学（微积分/线代）走向**动态**数学（变化过程）的桥梁。前置 18.01 + 18.02；本课研究"导数定义的方程"——已知变化率求函数本身。一阶/二阶 ODE + 线性系统 + Laplace 变换是经典内容，而**数值 ODE 求解器**（Euler/Runge-Kutta）直接连接到现代 ML 的 Neural ODE。学完后可以理解连续深度模型、扩散模型（SDE）和动力系统稳定性。

## 🔬 理论联系实际

| ODE 概念 | ML / 工程应用 | 公式对应 |
|---|---|---|
| **一阶 ODE** $\dot{x}=f(x,t)$ | Neural ODE 的核心方程 | $\frac{d\mathbf{h}(t)}{dt} = f_\theta(\mathbf{h}(t), t)$ |
| **Euler 法 / RK4** | Neural ODE 的数值求解 | $\mathbf{h}_{t+\Delta t} = \mathbf{h}_t + \Delta t \cdot f(\mathbf{h}_t)$ |
| **线性系统 $\dot{\mathbf{x}}=A\mathbf{x}$** | 连续动力系统 / RNN 连续化 | 特征值 → 稳定性/振荡 |
| **稳定性分析** | GAN 训练 / 收敛性 | 特征值实部 $<0$ → 稳定 |
| **Laplace 变换** | 信号处理 / 控制论 | $\mathcal{L}\{f\}(s) = \int_0^\infty e^{-st}f(t)\,dt$ |
| **热传导方程（PDE）** | 扩散模型（DDPM） | $\frac{\partial u}{\partial t} = D\nabla^2 u$ |

## 🆕 2024-2026 最新研究

1. **Neural ODE 与连续深度模型**：[arXiv:1806.07366](https://arxiv.org/abs/1806.07366)（Chen et al., NeurIPS 2018）把残差网络重新解读为 ODE 的 Euler 离散化——ResNet 的 $\mathbf{h}_{l+1} = \mathbf{h}_l + f(\mathbf{h}_l)$ 正是 $\dot{\mathbf{h}} = f(\mathbf{h})$ 的一步 Euler 法。2024-2025 年的连续标准化流（CNF）和扩散模型都基于这一框架。
2. **Flow Matching / 扩散模型的 ODE 视角**：[arXiv:2210.02747](https://arxiv.org/abs/2210.02747)（Flow Matching, ICLR 2023）和 [arXiv:2006.11239](https://arxiv.org/abs/2006.11239)（DDPM）把生成建模归结为求解一个 ODE/SDE——从噪声到数据的概率流。2024 年 Stable Diffusion 3 采用 Rectified Flow 使这条 ODE 路径更"直"、采样更少步。
3. **Mamba / 状态空间模型 = 离散化的线性 ODE**：[arXiv:2312.00752](https://arxiv.org/abs/2312.00752)（Mamba, Gu & Dao, 2023）核心方程 $\dot{\mathbf{h}}(t) = A\mathbf{h}(t) + B\mathbf{x}(t)$ 是一个**线性常系数 ODE**，通过零阶保持（ZOH）离散化得到 RNN 形式。Mamba 的"选择性"是让 $A, B$ 依赖输入——即 ODE 的系数变成时变的。
