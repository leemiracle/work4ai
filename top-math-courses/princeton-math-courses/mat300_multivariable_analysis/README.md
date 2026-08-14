# Princeton MAT 300 — Multivariable Analysis I

> **学校**：Princeton | **学期**：Fall | **学分**：QCR
> **一手来源**：[math.princeton.edu/undergraduate](https://www.math.princeton.edu/undergraduate)

## 课程信息
- **编号**：MAT 300
- **先修**：MAT 215 + MAT 217（或同等证明能力）
- **教材**：常用 Pugh 或 Rudin 第 9 章 + Spivak *Calculus on Manifolds*
- **特色**：从 215 单变量扩展到多变量分析

## 教学大纲
1. **Metric spaces & topology in $\mathbb{R}^n$**
2. **Differentiability in $\mathbb{R}^n$**（total vs partial derivative）
3. **Inverse function theorem** ★
4. **Implicit function theorem** ★
5. **Multivariable Riemann 积分**
6. **Fubini 定理**
7. **Change of variables**（变量替换）
8. **Multivariable Taylor**

## 与 ML 的关联
- **Inverse / Implicit function theorem**：隐式神经表示、normalizing flow
- **多变量 Taylor**：Hessian 分析、二阶优化
- **学完本课后**：能严格推导 MLP 的 Jacobian / Hessian

## 参考资源
- **教材**：Spivak, *Calculus on Manifolds* (Westview, 1965) — 经典小书
- **替代教材**：Munkres, *Analysis on Manifolds*（更易读）
- **替代教材**：Pugh, *Real Mathematical Analysis*（Ch. 4-5）
- **MIT 对照**：18.100A Part II

## 学习建议
- **节奏**：每周 5-6 小时，12 周
- **重点**：Inverse/Implicit function theorem（ML 论文里反复出现）

## 📍 在数学全景中的位置

```
前置                         本课                         后续
───────────────────────────────────────────────────────────────
MAT 215 单变量分析     →   Princeton MAT 300       →   MAT 322 PDE
(ε-δ + 级数)               (多变量 + 微分形式)         MAT 429 拓扑
```

| 阶梯 | 课程 | 角色 |
|---|---|---|
| 基础 | MAT 215 | 单变量 ε-δ |
| **进阶 ★** | **MAT 300** | **Jacobian + Stokes 定理** |
| 高阶 | MAT 429 | 点集拓扑 |

## 🔬 理论联系实际
1. **链式法则 → 反向传播**: $\partial L/\partial \theta = \partial L/\partial z \cdot \partial z/\partial \theta$ ★★★
2. **反函数定理 → Normalizing Flows**: $p_Y(y) = p_X(f^{-1}(y)) |\det J_{f^{-1}}|$
3. **隐函数定理 → 等约束优化**: Lagrange 乘子法的几何基础
4. **Stokes 定理 → 流形优化**: 信息几何 / 自然梯度
5. **变量替换积分 → 密度变换**: 概率分布的 Jacobian 变换

## 🆕 2024-2026 最新研究
- **Normalizing Flows** (RealNVP, Glow): 反函数定理的工程化 ⚠️
- **Implicit layers** (DEQ, Neural ODEs): 隐函数定理 + 不动点迭代 ⚠️
- **信息几何**: Fisher 信息度量 = Riemann 流形上的内积 ⚠️

---

📌 **下一步**：→ [MAT 322 PDE](../mat322_pde/) 或 [MAT 345 Algebra I](../mat345_algebra_I/)
