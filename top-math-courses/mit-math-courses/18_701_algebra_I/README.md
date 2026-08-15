# MIT 18.701 — Algebra I

> **学校**：MIT | **学期**：Fall | **学分**：12 units
> **一手来源**：[catalog.mit.edu/subjects/18/#18.701](https://catalog.mit.edu/subjects/18/) + [OCW 18.701 Prof. Artin](https://ocw.mit.edu/courses/18-701-algebra-i-fall-2010/)

## 课程信息
- **编号**：18.701（本科纯数学序列）
- **先修**：18.100 实分析（必须）+ 18.700 线代（推荐）
- **教材**：**Artin, *Algebra* (2nd ed, Pearson, 2017)** ★
- **视频**：[OCW 18.701-18.702 by Artin (1995, 经典)](https://ocw.mit.edu/courses/18-701-algebra-i-fall-2010/video_galleries/video-lectures/)
- **特色**：**Michael Artin 亲自为这门课写的教材**

## 教学大纲
1. **Group theory 基础**（群定义、对称群、循环群）
2. **Subgroups & cosets**（子群、陪集、Lagrange 定理）
3. **Homomorphisms & isomorphisms**
4. **The symmetric group $S_n$**
5. **Matrix groups**（$GL_n$, $O_n$, $SL_n$）
6. **Group actions**（轨道、稳定子、Sylow 定理）
7. **Rings**（环、理想、商环）
8. **Factorization in rings**（PID、UFD、Euclidean 域）
9. **Modules over rings**
10. **Field extensions & Galois theory 入门**

## 与 ML 的关联
- **表示论**：深度学习的几何理论（群等变神经网络）
- **张量代数**：Transformer 的 attention 张量化
- **Galois 理论**：基本不直接用于 ML，但培养数学成熟度
- **学完本课后**：能理解 GNN 中的群等变（E(n) Equivariant GNN 等）

## 参考资源
- **教材**：Artin, *Algebra* (2nd ed, 2017) ISBN 978-0134689609
- **视频**：[OCW 18.701 Fall 2010](https://ocw.mit.edu/courses/18-701-algebra-i-fall-2010/)
- **替代教材**：Dummit & Foote, *Abstract Algebra*（更全但更难读）
- **替代教材**（更现代）：Vakil, *The Rising Sea*（FOAG，抽象代数 → 代数几何）

## 学习建议
- **节奏**：每周 5-7 小时，14-16 周完成
- **难度**：本科纯数学最难的课之一（与 18.100B 并列）
- **重点**：群论与群作用（在 ML 中最多出现）
- **跳过**：纯数论部分（除非你做密码学）

📌 **下一步**：→ [18.901 拓扑](../18_901_topology/) 或 [Berkeley Math 113](../../berkeley-math-courses/math113_abstract_algebra/)

---

## 📍 在数学全景中的位置

- **前置**：[18.06 线性代数](../18_06_linear_algebra/)（矩阵/线性变换）
- **本课**：群 / 环 / 域 / 群作用 / 表示论入门——抽象代数的根基
- **后续**：[Harvard Math 122](../../harvard-math-courses/math122_algebra_I)（Dummit-Foote 体系）/ [Princeton MAT 345](../../princeton-math-courses/mat345_algebra_I)

---

## 🔬 理论联系实际

1. **群表示论 → 等变神经网络**（Cohen-Welling G-CNN, SE(3)-equivariant）
2. **CNN 平移等变 = $\mathbb{Z}^d$ 群卷积**
3. **AlphaFold 2/3 → SE(3)-等变网络**做分子结构预测
4. **密码学 → RSA / 椭圆曲线**（有限域群）
5. **张量分解 → 对称性降维**（CP/Tucker）

---

## 🆕 2024-2026 最新研究

- **几何深度学习**（Bronstein et al.）：统一 GNN、CNN、Transformer 的群论框架
- **Equivariant Transformer**：用群论设计对称 attention
- **AlphaFold 3**（2024）：SE(3)-等变扩散模型预测分子相互作用
- **拓扑数据分析 + ML**：用群论分析神经网络损失景观的对称性
- **量子机器学习**：有限群表示论是量子算法（QFT）的基础
