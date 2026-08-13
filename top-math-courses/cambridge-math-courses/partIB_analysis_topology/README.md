# Cambridge Part IB — Analysis and Topology

> **学校**：Cambridge | **学期**：Michaelmas/Lent (大二)
> **一手来源**：[maths.cam.ac.uk/undergrad/files/coursesIB.pdf](https://www.maths.cam.ac.uk/undergrad/files/coursesIB.pdf)

## 课程信息
- **学期**：Michaelmas + Lent (24 lectures)
- **教材**：Sutherland, *Introduction to Metric and Topological Spaces* ★
- **特色**：本科拓扑与分析融合

## 教学大纲
1. **Metric spaces** ★
2. Convergence in metric spaces
3. Completeness
4. Compactness
5. **Topological spaces** ★
6. Continuity in topological spaces
7. Connectedness
8. **Tychonoff 定理**（简介）
9. **Bolzano-Weierstrass**
10. **Heine-Borel**

## 与 ML 的关联
- 紧致性 → 泛函分析预备
- 学完后：能读泛函分析（[Part II Linear Analysis](../)）

## 参考资源
- Sutherland, *Introduction to Metric and Topological Spaces* (OUP) ★
- Munkres, *Topology*（替代）

## 📍 在数学全景中的位置

```
前置                         本课                         后续
───────────────────────────────────────────────────────────────
Part IA Analysis I     →   Cambridge Part IB       →   Part II Linear Analysis
(单变量 ε-δ)               Analysis & Topology         Part II Measure & Prob
```

| 阶梯 | 课程 | 角色 |
|---|---|---|
| 基础 | Part IA | 单变量 |
| **进阶 ★** | **Part IB** | **度量空间 + 拓扑 + 多变量分析** |
| 高阶 | Part II | 泛函 + 测度 |

## 🔬 理论联系实际
1. **压缩映射 → SGD 收敛**: $\eta < 2/L$ → 线性收敛 $O(q^n)$
2. **紧致 + 连续 → 一致连续**: 参数空间正则化 → 训练稳定
3. **一致收敛 → 泛化**: 逐点收敛 ≠ 泛化保证
4. **反函数定理 → Normalizing Flows**: Jacobian 行列式 = 密度变换
5. **链式法则 → 反向传播**: 多变量链式法则的工程化

## 🆕 2024-2026 最新研究
- **Neural ODEs**: 压缩映射 + 度量空间上的流 ⚠️
- **Normalizing Flows**: 反函数定理的工程化 ⚠️
- **流形假设**: 拓扑不变量 → 数据几何 ⚠️

---

📌 **下一步**：→ [Part IB Markov Chains](../partIB_markov_chains/)
