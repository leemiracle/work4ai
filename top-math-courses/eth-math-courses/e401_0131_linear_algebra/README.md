# ETH 401-0131-00 — Linear Algebra I (Eng. Stream)

> **学校**：ETH Zurich | **学院**：D-MATH
> **一手来源**：[igl.ethz.ch/teaching/linear-algebra/la2022/](https://igl.ethz.ch/teaching/linear-algebra/la2022/) + [vvz.ethz.ch](https://www.vvz.ethz.ch)

## 课程信息
- **编号**：401-0131-00L
- **学期**：Autumn (HS)
- **教材**：**Strang, *Introduction to Linear Algebra*** (6th ed)；Fischer *Lineare Algebra*（德）
- **特色**：**ETH 工学院线代**——与 Strang 同步

## 教学大纲
1. Complex numbers intro
2. Vectors, matrices
3. Norms, scalar products
4. LU decomposition
5. Vector spaces & linear maps
6. Least squares, QR
7. Determinants
8. Eigenvalues, eigenvectors
9. **SVD** ★
10. Applications

## 与 ML 的关联
- 与 [MIT 18.06](../../mit-math-courses/18_06_linear_algebra/) 同类（Strang 教材）

---

## 📍 在数学全景中的位置

ETH 401-0131 是 D-MATH 工学院的线代——与 MIT 18.06 同用 Strang 教材，但 ETH 的欧洲风格多一份严谨，且是 ETH 应用数学体系（数值/优化/SDE）的入口。

```
ETH 工学院数学体系             本课（线代入口）                          ETH 后续
──────────────                ──────────────                            ─────────
高中/入学考试 ──▶  401-0131 线代 (Strang/Fischer)  ──┬──▶  401-0261 Analysis I
                                                     ├──▶  401-2611 数值方法 CSE
                                                     ├──▶  401-3904 凸优化 (Boyd/Bubeck)
                                                     └──▶  401-3651 SDE 数值
MIT 18.06 (Strang) ◀──(同教材)── UT Austin M 340L ◀──(同难度)──┘
```

- **前置**：高中数学（ETH 入学门槛已较高）。
- **本课特色**：**Strang 直觉 + Fischer 德式严谨**双轨。覆盖 LU/QR/特征值/SVD，含复数与范数的早期引入（欧洲传统）。
- **后续**：ETH 数值方法（401-2611，Quarteroni）/ 凸优化（401-3904，Bubeck）/ SDE 数值（401-3651）全建立在线代之上。

> 一句话：**ETH 线代是"欧洲应用数学的第一块基石"——Strang 的直觉 + 欧洲的严谨。**

---

## 🔬 理论联系实际（公式级 ML/工程对应）

1. **LU/QR 分解 → 数值稳定的线性求解**
   - ETH 强调工程实现：QR 比 normal equation $A^TA$ 数值更稳定（避免条件数平方）。

2. **SVD → 数据压缩 / PCA / LoRA**
   - $A=U\Sigma V^T$，低秩近似 $A_k$。→ Eckart-Young → LoRA $W_0+BA$。

3. **特征值 → 结构工程 / 谱方法**
   - ETH 工程传统：特征值 = 振动模态（弹性力学）、稳定性（PDE 谱方法）。

4. **范数与条件数 → 数值稳定性**
   - $\kappa(A)=\sigma_{\max}/\sigma_{\min}$ → 梯度下降收敛速率、BatchNorm 的动机。

5. **最小二乘 → 信号拟合 / 回归**
   - $A^TA\hat{x}=A^Tb$ → 测量数据的最佳拟合（ETH 工程核心）。

---

## 🆕 2024-2026 最新研究（线代在 ML/工程的前沿）

1. **LoRA/QLoRA 低秩微调（2023-2026）**
   - LoRA（[arXiv:2106.09685](https://arxiv.org/abs/2106.09685)）与 QLoRA（[arXiv:2305.14314](https://arxiv.org/abs/2305.14314)）：低秩更新 $W_0+BA$，根基是 ETH 线代教的 SVD + Eckart-Young。

2. **条件数与 LLM 训练稳定性（2024-2025）**
   - 大模型训练的梯度条件数分析，回归到 ETH 线代的范数/谱理论。

3. **ETH 数值线代（401-2611）→ 大规模 SVD 算法（2024-2026）**
   - 随机化 SVD、流式 SVD 用于超大规模推荐系统/LLM 权重分析。

📌 **下一步**：→ [401-0261 Analysis I](../e401_0261_analysis_I/)
