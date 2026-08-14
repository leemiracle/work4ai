# Cambridge Part IB — Linear Algebra

> **学校**：Cambridge | **学期**：Michaelmas (大二秋)
> **一手来源**：[maths.cam.ac.uk/undergrad/files/coursesIB.pdf](https://www.maths.cam.ac.uk/undergrad/files/coursesIB.pdf)

## 课程信息
- **学期**：Michaelmas (24 lectures)
- **教材**：Blyth & Robertson, *Basic Linear Algebra*；Cameron *Linear Algebra*
- **特色**：**Cambridge 线代核心**——从向量空间到 Jordan 形式

## 教学大纲
1. Vector spaces, linear maps
2. Bases, dimension
3. Matrices, rank
4. Determinants
5. Eigenvalues, eigenvectors
6. Diagonalizability
7. **Jordan normal form** ★
8. Bilinear & quadratic forms
9. Inner product spaces
10. Dual spaces

## 与 ML 的关联
- 谱定理 → PCA
- Jordan 形式 → Neural ODE 稳定性

## 参考资源
- Blyth & Robertson *Basic Linear Algebra* (Springer)
- Past Tripos papers: [maths.cam.ac.uk/undergrad/pastpapers](https://www.maths.cam.ac.uk/undergrad/pastpapers)

---

## 📍 在数学全景中的位置

Cambridge Part IB Linear Algebra 是 Tripos 体系的核心——Michaelmas 学期 24 讲，从向量空间一路推到 Jordan 标准型与对偶空间，节奏极快、覆盖极广。

```
Cambridge Tripos 路径            本课（Part IB 核心）                      Cambridge 后续
──────────────                  ──────────────                            ─────────────
Part IA (Vectors & Matrices) ──▶  Part IB 线代 (Jordan/对偶/双线性) ──┬──▶  Part II: 表示论/代数
                                                                     ├──▶  Part II: ML 数学
                                                                     └──▶  Part III: 研究生
Berkeley 110 ◀──(同等深度)── Princeton 217 ◀──(同样严格)── Oxford A0 ┘
```

- **前置**：Part IA Vectors & Matrices（Year 1 入门）。
- **本课特色**：**Tripos 速成 + 完整严格**——一学期讲完对偶空间、Jordan 标准型、双线性/二次型、内积空间。Cambridge 用 4 年完成本科+硕士，节奏是全英最快。
- **后续**：Part II Mathematics of Machine Learning（直接应用谱理论/SVD）；Part III 研究生专题。

> 一句话：**Part IB 是"Cambridge 式的线代速成"——同样的深度，只用别人一半的时间。**

---

## 🔬 理论联系实际（公式级 ML/工程对应）

1. **Jordan 标准型 → 动力系统 / Neural ODE 稳定性**
   - Cambridge 对 Jordan 形式的处理极完整（含广义特征向量与极小多项式）。→ $e^{At}$ / $\prod W$ 的收敛性分析。ML 中 RNN 梯度流 $\nabla=\prod(\text{diag}(\sigma')W^T)$ 的稳定性直接用 Jordan 谱。

2. **谱定理（对称/Hermitian）→ PCA / 协方差**
   - Part IB 给出实/复谱定理的完整证明。→ 协方差对角化 → PCA。

3. **双线性与二次型 → 凸性 / SVM / 优化**
   - Sylvester 惯性律、配极化 → 二次型分类 → Hessian 凸性判定。SVM 对偶 = 半正定二次规划。

4. **对偶空间与对偶映射 → 核方法 / 反向传播**
   - $T^*:W^*\to V^*$（对偶映射）。→ 伴随 = 反向传播中梯度的对偶；核方法的特征空间对偶。

5. **SVD / 极分解 → 低秩近似（LoRA）**
   - Eckart-Young → LoRA $W_0+BA$。

---

## 🆕 2024-2026 最新研究（线代理论在 ML 的前沿）

1. **Jordan 形式 + 深度网络稳定性 / DEQ（2024-2025）**
   - 深度均衡模型不动点收敛 = Jacobian 谱半径 $<1$；Jordan 块决定收敛速率。Part IB 的 Jordan 理论是分析基础。⚠️ 非线性全局稳定性仍是开放问题。

2. **Cambridge Part II Mathematics of ML（2024-2026）**
   - 直接承接 Part IB 的谱理论/SVD，用线代分析神经网络泛化、矩阵补全、谱聚类。

3. **低秩微调 LoRA/QLoRA（2023-2026）**
   - LoRA（[arXiv:2106.09685](https://arxiv.org/abs/2106.09685)）与 QLoRA（[arXiv:2305.14314](https://arxiv.org/abs/2305.14314)）的低秩更新理论根基 = Part IB 的奇异值/谱定理。

📌 **下一步**：→ [Part IB Analysis and Topology](../partIB_analysis_topology/)
