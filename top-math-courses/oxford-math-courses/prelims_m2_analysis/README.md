# Oxford Prelims M2 — Analysis I/II/III

> **学校**：Oxford | **学期**：Prelims
> **一手来源**：[Prelims synopses PDF](https://www.maths.ox.ac.uk/system/files/attachments/Prelims%20Mathematics%20Synopses%202024-25.pdf)

## 课程信息
- **学期**：Year 1（I=Michaelmas, II=Lent, III=Trinity）
- **教材**：Bartle & Sherbert；Spivak *Calculus*；Hart *Guide to Analysis*
- **特色**：本科分析三段制

## 教学大纲
- **I**：Sequences & series（实数构造、收敛）
- **II**：Continuity & differentiability（ε-δ）
- **III**：Integration（Riemann）

## 与 ML 的关联
- 实分析入门

## 📍 在数学全景中的位置

```
前置                         本课                         后续
───────────────────────────────────────────────────────────────
A-Level / MAT         →   Oxford Prelims M2       →   Part A Analysis
(微积分基础)               (实分析三段制)              Part A Topology
```

| 阶梯 | 课程 | 角色 |
|---|---|---|
| **基础 ★** | **Prelims M2** | **ε-δ + Riemann 积分 + 级数** |
| 进阶 | Part A Analysis | 度量空间 |
| 高阶 | Part B | 泛函分析 |

## 🔬 理论联系实际
1. **完备性公理 → 优化良定义**: sup/inf 存在 → 最优解存在
2. **MVT → SGD 分析**: $\exists c: \nabla L(c) = 0$ → 临界点可达
3. **Taylor 展开 → 牛顿法**: 二阶近似 → 二次收敛
4. **级数收敛 → softmax**: $e^x = \sum x^k/k!$ 保证收敛
5. **Riemann 积分 → 期望近似**: $E[X] = \int x \, dF$ 的离散近似

## 🆕 2024-2026 最新研究
- **形式化分析**: Lean 证明 ML 优化的分析基础 ⚠️
- **自动微分**: Taylor 展开的计算图实现 ⚠️
- **数值稳定**: softmax / log-sum-exp trick ⚠️

---

📌 **下一步**：→ [Part A A0 Linear Algebra](../partA_a0_linear_algebra/)
