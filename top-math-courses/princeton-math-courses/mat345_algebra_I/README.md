# Princeton MAT 345 — Algebra I

> **学校**：Princeton | **学期**：Fall | **学分**：QCR
> **一手来源**：[math.princeton.edu/undergraduate](https://www.math.princeton.edu/undergraduate)

## 课程信息
- **编号**：MAT 345
- **先修**：MAT 215 + 217（强烈推荐）
- **教材**：Artin, *Algebra*；或 Dummit & Foote
- **特色**：本科抽象代数（群 + 环）

## 教学大纲
1. **Groups**（群、子群、同态、商群）
2. **Symmetric group $S_n$**
3. **Group actions**（轨道、Sylow 定理）
4. **Rings**（环、理想、商环）
5. **Modules**
6. **Field extensions**
7. **Galois theory 入门**

## 与 ML 的关联
- **群论**：等变神经网络、群卷积网络（G-CNN）
- **Galois 理论**：基本不直接用于 ML
- **学完本课后**：理解 Cohen-Welling 等变网络

## 参考资源
- **教材**：Artin, *Algebra* (2nd ed, 2017)
- **替代**：Dummit & Foote, *Abstract Algebra*
- **MIT 对照**：[MIT 18.701](../../mit-math-courses/18_701_algebra_I/)

## 学习建议
- 每周 5-7 小时，12-14 周

📌 **下一步**：→ [MAT 429 Topology](../mat429_topology/) 或 [MAT 514 Probability](../mat514_probability/)

---

## 📍 在数学全景中的位置

- **前置**：线性代数 + MAT 215 分析（证明能力）
- **本课**：Artin 体系 → 矩阵群 → 群作用 → 表示论入门（与 MIT 18.701 同源）
- **交叉**：[MIT 18.701 Artin](../../mit-math-courses/18_701_algebra_I/) + [Berkeley 113](../../berkeley-math-courses/math113_abstract_algebra/)

## 🔬 理论联系实际
1. **矩阵群 → 表示论**：群的线性表示 = 深度学习的等变层基础
2. **群作用 → 等变神经网络**：CNN = $\mathbb{Z}^d$ 群卷积；AlphaFold = SE(3) 等变
3. **对称群 → DeepSets**：$S_n$ 不变性处理集合/点云数据
4. **有限域 → 纠错码**：Reed-Solomon 码 → QR 码/通信

## 🆕 2024-2026 最新研究
| 子主题 | 进展 | 参考 |
|---|---|---|
| SE(3)-等变网络 | AlphaFold 3 核心 | [Nature 2024](https://www.nature.com/articles/s41586-024-07487-w) ✅ |
| Galois 神经网络 | 用 Galois 群约束消息传递 | 研究中 ⚠️ |
| 表示论引导架构 | e3nn 库自动用不可约表示构造层 | 开源生态 ✅ |
