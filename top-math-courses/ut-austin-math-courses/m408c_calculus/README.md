# UT Austin M 408C — Differential and Integral Calculus

> **学校**：UT Austin | **学期**：Fall/Spring | **学分**：3
> **一手来源**：[math.utexas.edu/academics/undergraduate-courses](https://math.utexas.edu/academics/undergraduate-courses) + [catalog.utexas.edu](https://catalog.utexas.edu/general-information/coursesatoz/m/)

## 课程信息
- **编号**：M 408C（标准微积分序列第一学期）
- **先修**：高中微积分
- **教材**：Stewart, *Calculus: Early Transcendentals*
- **特色**：UT Austin 标准微积分（工程师/科学家方向）

## 教学大纲
1. Limits & continuity
2. Derivatives（定义、法则、链式法则）
3. Applications of derivatives（极值、最优化、相关变化率）
4. Integration（不定/定积分、微积分基本定理）
5. Techniques of integration
6. Applications of integration（面积、体积）

## 与 ML 的关联
- 梯度 / 偏导的基础
- 学完后：能看懂 ML 论文的 ∇ 符号

📌 **下一步**：→ [M 427L Vector Calculus](../m427l_vector_calculus/)

---

## 📍 在数学全景中的位置

M 408C 是 UT Austin 标准微积分序列的第一学期，定位与 [MIT 18.01](../../mit-math-courses/18_01_calculus/) 对等。前置高中微积分；本课建立极限 → 导数 → 积分 → 积分技巧的完整链条。学完后顺接 **M 408D**（序列第二学期，含级数/Taylor）和 **M 427L 向量微积分**。对 ML 从业者，核心是**导数 = 梯度信号**和**链式法则 = 反向传播**。

## 🔬 理论联系实际

| 微积分概念 | ML / 工程应用 | 公式对应 |
|---|---|---|
| **导数 $f'(x)$** | 梯度下降信号源 | $x_{t+1} = x_t - \eta f'(x_t)$ → SGD |
| **链式法则** | **反向传播** | $\frac{dL}{dw} = \frac{dL}{dy}\frac{dy}{dw}$ |
| **极值/最优化** | 模型训练 = 最小化损失 | $f'(x_0) = 0$ → 临界点 |
| **积分** | 概率密度归一化 | $\int p(x)\,dx = 1$ |
| **Newton 迭代法** | 二阶优化 / 求根 | $x_{n+1} = x_n - f(x_n)/f'(x_n)$ |

## 🆕 2024-2026 最新研究

1. **Adam 优化器与导数信号**（[arXiv:1412.6980](https://arxiv.org/abs/1412.6980)）：Adam 至今是深度学习默认优化器，核心是对导数（梯度）的一阶/二阶矩做自适应估计——本质是在噪声中提取真正的导数信号。2024 年 Schedule-Free 优化器延续此思路。
2. **自动微分的微积分基础**：PyTorch/JAX 的 autograd 本质是链式法则的程序化实现。2024-2025 年 micrograd（Karpathy）和 JAX 的差异化规则展示了如何用最少的微积分原语构建完整 autodiff——M 408C 的链式法则是其数学根基。
3. **Taylor 展开与数值优化**：二阶 Taylor 近似 → Newton 法在非凸优化中的局部收敛保证（⚠️ 理论方向 2024+ 活跃）。
