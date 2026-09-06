# UT Austin M 340L — Matrices and Matrix Calculations

> **学校**：UT Austin
> **一手来源**：[catalog.utexas.edu](https://catalog.utexas.edu/general-information/coursesatoz/m/)

## 课程信息
- **编号**：M 340L（应用线代；区别于 M 341 理论版）
- **先修**：M 408D 或同等多变量微积分
- **教材**：Lay, *Linear Algebra and Its Applications*

## 教学大纲
1. Linear systems, matrices
2. Determinants
3. Vector spaces
4. Eigenvalues, eigenvectors
5. Orthogonality
6. Symmetric matrices & SVD

## 与 ML 的关联
- 工程师线代基础
- M 341 是更严格的理论版本（Axler）

---

## 📍 在数学全景中的位置

UT Austin M 340L 是应用线代——用 Lay 教材，面向工程/数据科学学生，是 UT 应用数学强校（金融数学、数据科学）的入门基石。

```
应用线代入门                  本课（应用线代）                          UT Austin 后续
──────────                    ──────────────                            ─────────────
M 408D 微积分 ──▶  M 340L 矩阵与矩阵计算 (Lay)  ──┬──▶  M 383E 数值线代 (Trefethen & Bau) ★
                                                  ├──▶  M 362K 概率
                                                  └──▶  数据科学/金融数学
MIT 18.06 (Strang) ◀──(同难度)── ETH 401-0131 ◀──(同应用导向)──┘
```

- **前置**：M 408D（多变量微积分）。
- **本课特色**：**最友好的应用线代**——Lay 教材以"概念驱动 + 应用导向"著称，比 Strang 更温和，适合工程师。区别于 M 341（理论版，用 Axler）。
- **后续**：M 383E 数值线代（Trefethen & Bau，UT 的招牌课）——把 340L 的理论变成可计算的高效算法。

> 一句话：**M 340L 是"给工程师的线代快车道"——足够实用，直接通向 UT 招牌的数值线代。**

---

## 🔬 理论联系实际（公式级 ML/工程对应）

1. **线性方程组 → 线性回归 / 数据拟合**
   - Lay 用大量工程/经济实例。$A\hat{x}\approx b$ 的最小二乘解 = 线性回归闭式解。

2. **特征值 → PageRank / Markov / 振动**
   - 转移矩阵特征值 $=1$ → 稳态。PageRank = 最大特征向量。UT 数据科学强校的传统应用。

3. **正交性 / QR → 数值稳定求解**
   - Gram-Schmidt / QR → 稳定最小二乘（避免 $A^TA$ 的条件数放大）。

4. **对称矩阵 / SVD → PCA / 数据科学**
   - Lay 重点讲 SVD 的应用（推荐系统、图像压缩、PCA）。→ UT 数据科学核心工具。

5. **行列式 / 体积 → 概率密度变换**
   - $|\det J|$ 在变量替换概率密度中出现（UT 概率课 M 362K 的前置）。

---

## 🆕 2024-2026 最新研究（线代在 ML/数据科学的前沿）

1. **SVD → LoRA/QLoRA 低秩微调（2023-2026）**
   - LoRA（[arXiv:2106.09685](https://arxiv.org/abs/2106.09685)）与 QLoRA（[arXiv:2305.14314](https://arxiv.org/abs/2305.14314)）的全部数学 = 340L 教的 SVD 低秩近似 + Eckart-Young。M 340L 的 SVD 章节就是理解 LoRA 的直接入口。

2. **PCA → 数据科学降维（持续核心）**
   - UT Austin 数据科学方向的核心：高维数据的 PCA 降维、t-SNE/UMAP 的线代基础。

3. **数值线代（M 383E 后续）→ 大规模 SVD/随机化算法（2024-2026）**
   - 推荐系统、LLM 权重分析需要的超大规模 SVD，由 M 383E 的随机化算法实现。

📌 **下一步**：→ [M 341 理论版](../m340l_linear_algebra/) 或 [M 365C Real Analysis](../m365c_real_analysis/)
