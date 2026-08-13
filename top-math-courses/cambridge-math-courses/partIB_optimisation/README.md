# Cambridge Part IB — Optimisation

> **学校**：Cambridge | **学期**：Easter (大二)
> **一手来源**：[maths.cam.ac.uk/undergrad/files/coursesIB.pdf](https://www.maths.cam.ac.uk/undergrad/files/coursesIB.pdf)

## 课程信息
- **学期**：Easter (12 lectures)
- **教材**：自编讲义
- **特色**：本科优化入门

## 教学大纲
1. Lagrangian & KKT 条件 ★
2. Linear programming
3. Simplex method
4. Duality
5. Quadratic programming
6. Convex optimization 入门

## 与 ML 的关联
- SVM 推导
- 学完后：能读 Boyd *Convex Optimization*

📌 **下一步**：→ [Part IB Numerical Analysis](../partIB_numerical_analysis/)

---

## 📍 在数学全景中的位置

- **前置**：线代 + 多变量微积分
- **本课**：LP / 单纯形法 / KKT / 对偶 → 凸优化入门
- **后续**：[Stanford CME 364A](../../stanford-math-courses/cme364A_convex_optimization/)（凸优化完整版）/ [ETH 401-3901](../../eth-math-courses/e401_3901_linear_combinatorial_optimization/)（整数规划）

---

## 🔬 理论联系实际

1. **SVM = 凸 QP + KKT** → [CME 364A](../../stanford-math-courses/cme364A_convex_optimization/) 完整推导
2. **LP 对偶 → 零和博弈 Nash 均衡**（von Neumann minimax）
3. **Lasso 稀疏性 = $\ell_1$ KKT 软阈值**
4. **LP 松弛 + rounding → 近似算法**（聚类）
5. **GAN 训练 = minimax 博弈**

---

## 🆕 2024-2026 最新研究

- **GPU LP 求解器**：cuPDLP-C（2023），GPU 加速超大规模 LP
- **GNN + 分支定界**：机器学习辅助组合优化
- **次模优化**：离散凸函数与连续凸优化的类比
