# Harvard Math 25a/b — Honors Multivariable Mathematics

> **学校**：Harvard | **学院**：Department of Mathematics
> **一手来源**：[math.harvard.edu/undergraduate](https://www.math.harvard.edu/undergraduate) + Undergraduate Brochure 2025-2026

## 课程信息
- **编号**：Math 25a (Fall) / Math 25b (Spring)
- **先修**：单变量微积分 + 证明能力（不强制）
- **教材**：Hubbard & Hubbard, *Vector Calculus, Linear Algebra, and Differential Forms*；配 Rudin 第 1-7 章
- **特色**：**理论与应用并重**；Math 55 的"友好版"

## 教学大纲
1. **Linear algebra with proofs**（25a 前半）
2. **Multivariable calculus 严格版**（25a 后半 + 25b）
3. **Topology of $\mathbb{R}^n$**
4. **Inverse/Implicit function theorem**
5. **Integration in $\mathbb{R}^n$**
6. **Differential forms**
7. **Stokes 定理**

## 与 ML 的关联
- **严格线代 + 多变量分析**
- **学完本课后**：能 ε-δ 证明 + 理解 Hessian

## 参考资源
- Hubbard & Hubbard *Vector Calculus* (5th ed)
- 替代：Munkres *Analysis on Manifolds*
- MIT 对照：[MIT 18.100A](../../mit-math-courses/)（更易）

📌 **下一步**：→ [Harvard Math 55](../math55_honors_abstract/)（更难版本）

---

## 📍 在数学全景中的位置

Harvard Math 25a/b 是 Math 55 的"友好版"——理论严格但不像 Math 55 那样极限硬核。前置单变量微积分 + 证明能力；本课用 Hubbard & Hubbard 的《Vector Calculus, Linear Algebra, and Differential Forms》把**线代 + 多变量分析 + 微分形式**统一讲授，配 Rudin 前 7 章做 ε-δ 严格化。与 MIT 18.02 的差异：25 强调**证明**（Inverse/Implicit Function Theorem 的完整证明、微分形式的 Stokes 定理），18.02 强调**计算与几何直觉**。学完后能从第一性原理理解 Hessian、优化收敛性、流形上的梯度——为读研究级 ML 理论论文（如优化理论、信息几何）打下基础。

## 🔬 理论联系实际

| 严格数学概念 | ML / 工程应用 | 公式对应 |
|---|---|---|
| **ε-δ 连续/可微** | 激活函数光滑性分析 | $|f(x)-f(a)|<\varepsilon$ 的严格化 |
| **全导数（Fréchet）** | Jacobian 的严格定义 | $Df(\mathbf{a}) = $ 最佳线性近似 |
| **Inverse Function Theorem** | 可逆变换 / 标准化流 | $f$ 局部可逆 $\iff$ $\det J \neq 0$ |
| **Implicit Function Theorem** | 约束优化 / 流形参数化 | $F(\mathbf{x})=0$ 隐式定义曲面 |
| **Hessian + 二阶变分** | 优化收敛速率证明 | $H \succ 0$ → 局部最小 + 收敛率 |
| **微分形式 + Stokes** | 流形上的概率/统计 | $\int_{\partial M}\omega = \int_M d\omega$ |

## 🆕 2024-2026 最新研究

1. **信息几何 = 流形上的微积分**：将参数空间视为黎曼流形，用 Fisher 信息矩阵作为度量——这依赖 Math 25 的微分形式/流形基础。自然梯度下降（natural gradient）是其在优化中的应用。2024 年的信息几何优化理论研究直接用到 Math 25 的概念。
2. **标准化流与 Inverse Function Theorem**：Normalizing Flows 的核心是可逆变换 + 变量替换公式 $\det J$——Math 25 的 Inverse Function Theorem 和 Jacobian 行列式是其严格基础。Flow Matching（[arXiv:2210.02747](https://arxiv.org/abs/2210.02747)）延续了这一传统。
3. **优化的严格收敛证明**（⚠️ 理论方向 2024+）：非凸优化的收敛证明（如 SGD 收敛到近似局部最小）依赖 Hessian 的谱分析 + 鞍点逃逸论证——这正是 Math 25 用 ε-δ 严格化的二阶分析。
