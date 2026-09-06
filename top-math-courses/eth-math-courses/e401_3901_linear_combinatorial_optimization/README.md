# ETH 401-3901 — Linear & Combinatorial Optimization

> **学校**：ETH Zurich | **教授**：R. Zenklusen
> **一手来源**：[vvz.ethz.ch/Vorlesungsverzeichnis/lerneinheit.view?lerneinheitId=193687](https://www.vvz.ethz.ch/Vorlesungsverzeichnis/lerneinheit.view?lang=en&lerneinheitId=193687&semkez=2025W)（**一手核实**）

## 课程信息
- **编号**：401-3901-00L (4 hrs V + 2 hrs U)
- **教授**：Rico Zenklusen
- **教材**：Matoušek & Gärtner, *Understanding and Using Linear Programming*；或 Vanderbei
- **特色**：ETH 优化核心课

## 教学大纲
1. **Linear programming 建模**
2. **Simplex method** ★
3. **Duality**（LP 强对偶定理）
4. **Integer LP**（ILP）
5. **Branch & bound**
6. **Cutting planes**（Gomory）
7. **Network flows**（max flow, min cut, Ford-Fulkerson）
8. **Matching**
9. **Submodular optimization 入门**

## 与 ML 的关联
- 整数规划用于结构化决策
- 网络流用于图算法
- 学完后：能读组合优化 ML 论文

## 参考资源
- Matoušek & Gärtner, *Understanding and Using Linear Programming* (Springer)
- Vanderbei, *Linear Programming* (4th ed, 免费 PDF)
- Stanford 对照：[MS&E 211](../../stanford-math-courses/)

📌 **下一步**：→ [401-3904 Convex Optimization](../e401_3904_convex_optimization/)

---

## 📍 在数学全景中的位置

- **前置**：线代 + 基础算法
- **本课**：LP / ILP / 网络流 / 次模优化
- **后续**：[ETH 401-3904 凸优化](../e401_3904_convex_optimization/)（连续版）/ [Cambridge Part IB Optimisation](../../cambridge-math-courses/partIB_optimisation/)

---

## 🔬 理论联系实际

1. **最大流 → 图分割、社区检测、GNN**
2. **匹配 → 推荐系统、稳定婚姻**
3. **次模优化 → 特征选择、影响力最大化**（社交网络）
4. **ILP + ML → GNN 加速分支定界**（2024 前沿）
5. **LP 松弛 → SVM / Lasso 的理论基础**（[CME 364A](../../stanford-math-courses/cme364A_convex_optimization/)）

---

## 🆕 2024-2026 最新研究

- **GNN + MILP**：机器学习预测分支变量，加速 10-100×（Gasse 2019 → 2024）
- **GPU LP/ILP**：cuPDLP-C、SCIP-GPU
- **次模神经网络**：可解释 ML 的新范式
- **QAOA 量子优化**：组合问题的量子启发算法（早期阶段）
