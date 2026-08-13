# MIT 18.01 — Calculus

> **学校**：MIT | **学院**：Mathematics (Course 18) | **学期**：Fall/Spring | **学分**：12 units (5-0-7)
> **一手来源**：[catalog.mit.edu/subjects/18/#18.01](https://catalog.mit.edu/subjects/18/) + [OCW 18.01](https://ocw.mit.edu/courses/18-01-single-variable-calculus-fall-2006/)（2026-08 核实）

## 课程信息
- **编号**：18.01 / 18.01A（含 IAP 延伸版）
- **名称**：Single Variable Calculus
- **先修**：高中微积分基础
- **教材**：Strang, *Calculus*（Wellesley-Cambridge Press）+ Herman 等在线补充
- **视频**：[OCW Prof. David Jerison 18.01](https://ocw.mit.edu/courses/18-01-single-variable-calculus-fall-2006/)
- **附属**：18.01A = 18.01 + IAP 复习（秋季入学的延伸版本）

## 教学大纲
1. **Limits & continuity**（极限与连续）
2. **Derivatives**（导数：定义、求导法则、链式法则、隐函数）
3. **Applications of derivatives**（极值、最优化、Newton 迭代法）
4. **Integration**（不定积分、定积分、微积分基本定理）
5. **Techniques of integration**（换元、分部、部分分式）
6. **Improper integrals**（反常积分收敛性）
7. **Sequences and series**（级数收敛判定）
8. **Taylor series**（Taylor 展开、收敛半径）

## 与 ML 的关联
- 梯度 / 偏导的基础（→ 反向传播、优化器）
- Taylor 展开用于数值优化分析（→ Newton 法）
- **学完本课后**：能看懂 ML 论文里的 ∇/∂ 符号

## 参考资源
- **教材（免费 PDF）**：[MIT OpenCourseWare 18.01 Strang](https://ocw.mit.edu/resources/18-01-single-variable-calculus-fall-2006/textbook/)
- **视频**：[OCW Jerison 35 讲](https://www.youtube.com/playlist?list=PL5900DBC7A7FE7C29)
- **习题集**：[OCW 18.01 problem sets](https://ocw.mit.edu/courses/18-01-single-variable-calculus-fall-2006/assignments/)
- **配合**：3Blue1Brown *Essence of Calculus*（YouTube）

## 学习建议
- **节奏**：每周 3-5 小时，8-10 周完成
- **重点**：积分技巧与 Taylor 展开（这两块在 ML 论文里最常出现）
- **跳过**：高中已掌握的部分

📌 **下一步**：→ [18.02 多变量微积分](../18_02_multivariable_calculus/)

---

## 📍 在数学全景中的位置

18.01 是**整个 MIT 数学序列的起点**。前置只需高中微积分直觉（极限、求导速算）；本课把这些直觉**严格化**——从 ε-δ 极限定义出发，建立导数 → 微分 → 积分 → 级数的完整链条。学完后顺接到 **18.02 多变量微积分**（把导数推广到偏导/梯度）、**18.03 微分方程**（导数定义方程）和 **18.06 线性代数**。可以说：18.01 的"导数"概念，是后续所有课（优化、概率、动力系统）的共同语言。

## 🔬 理论联系实际

| 微积分概念 | ML / 工程应用 | 公式对应 |
|---|---|---|
| **导数 $f'(x)$** | 梯度下降的信号源 | $x_{t+1} = x_t - \eta f'(x_t)$ → SGD |
| **链式法则** | **反向传播** | $\frac{dL}{dw} = \frac{dL}{dy}\frac{dy}{dw}$，autograd 的核心 |
| **Taylor 展开** | Newton 法（二阶优化） | $f(x) \approx f(x_0) + f'(x_0)\Delta + \tfrac{1}{2}f''(x_0)\Delta^2$ |
| **定积分** | 概率密度归一化 / 期望 | $\int p(x)\,dx = 1$，$E[X] = \int x\,p(x)\,dx$ |
| **反常积分收敛** | KL 散度 / 熵的存在性 | $D_{KL} = \int p(x)\ln\frac{p(x)}{q(x)}\,dx$ 须收敛 |

## 🆕 2024-2026 最新研究

1. **Adam 优化器十年回顾与修正**：Adam（[arXiv:1412.6980](https://arxiv.org/abs/1412.6980), Kingma & Ba, ICLR 2015）至今仍是深度学习默认优化器。2024 年的研究聚焦于"学习率调度与导数缩放"的精确分析——例如 **Schedule-Free** 优化器无需调学习率（Defazio et al., 2024），其理论基础正是导数方向的自适应步长。
2. **自动微分（autodiff）的系统化**：PyTorch/JAX 的反向传播本质是链式法则的程序化实现。2024-2025 年的 **micrograd**（Karpathy）和 **JAX 的 transpose 规则**展示了如何用最少的微积分原语（前向导数 + 反向转置）构建完整的 autodiff 系统，使得 18.01 学的链式法则直接可编程。
3. **Adam 的"信噪比"视角**（⚠️ 具体论文 ID 待核实）：2024 年有研究将 Adam 的动量估计重新解释为"梯度信噪比"的自适应，这与 18.01 中导数作为"变化率"的直觉一致——优化器本质是在噪声中提取真正的导数信号。
