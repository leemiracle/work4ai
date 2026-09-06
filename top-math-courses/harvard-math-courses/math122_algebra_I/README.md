# Harvard Math 122 — Algebra I: Theory of Groups and Vector Spaces

> **学校**：Harvard
> **一手来源**：Harvard Undergraduate Brochure 2025-2026

## 课程信息
- **编号**：Math 122
- **先修**：Math 21b 或 Math 23b 或 Math 25b
- **教材**：Artin, *Algebra*
- **特色**：本科抽象代数（群 + 线性群）

## 教学大纲
1. **Groups**
2. **Symmetric groups $S_n$**
3. **Group actions**（Sylow 定理）
4. **Linear groups**（$GL_n$ 等）
5. **Representation 入门**（有限群表示）

## 与 ML 的关联
- **群表示论**：等变神经网络
- **学完本课后**：理解 GNN 中的群等变

## 参考资源
- Artin, *Algebra* (2nd ed, Pearson, 2017)
- MIT 对照：[MIT 18.701 Algebra I](../../mit-math-courses/18_701_algebra_I/)

📌 **下一步**：→ [Harvard Math 131 Topology I](../math131_topology_I/)

---

## 📍 在数学全景中的位置

- **前置**：线性代数 + 证明能力
- **本课**：Dummit-Foote 体系 → 群/环/域/模/Galois（最全面的本科代数教材）
- **交叉**：[MIT 18.701](../../mit-math-courses/18_701_algebra_I/)（Artin 体系）+ [Berkeley 113](../../berkeley-math-courses/math113_abstract_algebra/)（ML 应用视角）

## 🔬 理论联系实际
1. **群作用 → 等变神经网络**：G-CNN, SE(3)-Transformer, AlphaFold
2. **模论 → Jordan 标准形**：矩阵分解的理论基础 → SVD/PCA
3. **Noether 环 → 代数优化**：多项式约束优化
4. **可解群 → 根式可解性**：五次方程无根式解

## 🆕 2024-2026 最新研究
| 子主题 | 进展 | 参考 |
|---|---|---|
| 等变 Transformer | AlphaFold 3 用扩散+等变架构 | [Nature 2024](https://www.nature.com/articles/s41586-024-07487-w) ✅ |
| E(3)-等变扩散 | 分子生成 | [Hoogeboom 2022, 2203.17061](https://arxiv.org/abs/2203.17061) ✅ |
| 自动对称发现 | 从数据学习群结构 | ⚠️ ICLR 2024 |
