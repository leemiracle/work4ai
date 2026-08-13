# Cambridge Part IA — Analysis I

> **学校**：Cambridge | **课程**：Mathematical Tripos Part IA | **学期**：Michaelmas (大一秋)
> **一手来源**：[maths.cam.ac.uk/undergrad/full-list-undergraduate-courses](https://www.maths.cam.ac.uk/undergrad/full-list-undergraduate-courses)

## 课程信息
- **学院**：Faculty of Mathematics
- **学期**：Michaelmas (24 lectures)
- **先修**：高中数学
- **教材**：自编讲义（Cambridge 不指定）；常用 Garling, *A Course in Mathematical Analysis* Vol 1
- **特色**：**Cambridge 数学第一课**——本科分析起点

## 教学大纲
1. Real numbers（Dedekind 切）
2. Sequences & convergence
3. Series & convergence tests
4. Continuity
5. Differentiation
6. Mean value theorem
7. Taylor 定理
8. Riemann 积分入门

## 与 ML 的关联
- 实分析的英式训练
- 学完后：能 ε-δ 证明

## 📍 在数学全景中的位置

```
前置                         本课                         后续
───────────────────────────────────────────────────────────────
A-Level / STEP        →   Cambridge Part IA       →   Part IB Analysis II
(微积分基础)               Analysis I                  Part IB Metrics
```

| 阶梯 | 课程 | 角色 |
|---|---|---|
| **基础 ★** | **Part IA Analysis I** | **单变量 ε-δ + Riemann 积分** |
| 进阶 | Part IB Analysis II | 多变量 + 度量空间 |
| 高阶 | Part IB Metrics | Lebesgue 预告 |

## 🔬 理论联系实际
1. **ε-δ 连续 → ReLU 分析**: 连续但不可微 → 次梯度
2. **中值定理 → SGD**: $\exists c: \nabla L(c) = 0$ → 临界点存在
3. **Taylor 展开 → 二阶优化**: $L(\theta+d) \approx L + \nabla L^T d + \frac{1}{2}d^T H d$
4. **Riemann 积分 → 期望近似**: $E[X] \approx \sum x_i p(x_i) \Delta x$
5. **级数收敛 → softmax 稳定性**: $e^x$ 的级数保证收敛

## 🆕 2024-2026 最新研究
- **自动 ε-δ 证明**: Lean/Coq 形式化验证 ML 的分析基础 ⚠️
- **Softplus vs ReLU**: 数值稳定性的连续可微分析 ⚠️

---

📌 **下一步**：→ [Part IA Probability](../partIA_probability/)
