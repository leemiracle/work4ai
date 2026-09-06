# Oxford Part A A0 — Linear Algebra

> **学校**：Oxford | **学期**：Part A (Year 2)
> **一手来源**：[courses.maths.ox.ac.uk](https://courses.maths.ox.ac.uk/)

## 课程信息
- **编号**：A0
- **学期**：Year 2 核心
- **教材**：自编讲义；配 Axler
- **特色**：Part A 线代核心

## 教学大纲
1. Vector spaces 深入
2. Linear maps, dual
3. Bilinear forms
4. Jordan normal form
5. Spectral theory for symmetric matrices

## 与 ML 的关联
- 进阶线代（part A 标准）

---

## 📍 在数学全景中的位置

Oxford Part A A0 是 Year 2 核心线代——把 Prelims M1 的入门升级到**对偶空间、Jordan 形式、双线性形式、谱理论**，是 Oxford 数学生的必修骨干。

```
Year 1 入门                   本课（Year 2 核心）                       Oxford 后续
──────────                    ──────────────                            ───────────
Prelims M1 线代 ──▶  Part A A0 线代深化 (对偶/Jordan/谱)  ──┬──▶  Part C C7.1 随机矩阵
                                                            ├──▶  Part B 概率测度/鞅
                                                            └──▶  研究生: 泛函/表示论
Berkeley 110 ◀──(同等深度)── Princeton 217 ◀──(同样抽象)──┘
```

- **前置**：Prelims M1。
- **本课特色**：**对偶空间 + Jordan 标准型 + 双线性/二次型 + 对称矩阵谱理论**——与 Berkeley 110 / Princeton 217 同深度，但 Oxford 的几何/公理化味道更浓。
- **后续**：Part C C7.1 随机矩阵理论（直接连 LLM 权重谱）；Part B 概率测度（连 LoRA 的低秩统计）。

> 一句话：**A0 是"Oxford 数学生的线代成人礼"——从计算彻底转向结构与对偶。**

---

## 🔬 理论联系实际（公式级 ML/工程对应）

1. **Jordan 标准型 → 动力系统/RNN 稳定性**
   - $A=PJP^{-1}$，Jordan 块决定 $e^{At}$ / $A^k$ 的多项式-指数增长模式。→ RNN 长程依赖 $\nabla=\prod W^T$ 的衰减分析。

2. **对称矩阵谱理论 → PCA / 协方差**
   - Oxford 版实谱定理：对称矩阵有正交特征基，特征值全实。→ 协方差对角化 = PCA。

3. **双线性/二次型 → 凸优化 / SVM / Mahalanobis**
   - 二次型 $q=\mathbf{x}^TS\mathbf{x}$ 的惯性指数（Sylvester 惯性律）判定正定/负定。→ Hessian 凸性、SVM 二次规划、Mahalanobis 距离。

4. **对偶空间 → 线性泛函 / 核方法**
   - $V^*$（对偶）+ Riesz 表示 → 核回归 $f(\mathbf{x})=\sum\alpha_iK(\mathbf{x}_i,\mathbf{x})$。

5. **极分解 / SVD → 低秩近似（LoRA）**
   - 任何矩阵 = 旋转 × 伸缩 × 旋转。→ Eckart-Young → LoRA $W_0+BA$。

---

## 🆕 2024-2026 最新研究（线代理论在 ML 的前沿）

1. **Jordan 形式 + Neural ODE / 深度均衡模型稳定性（2024-2025）**
   - DEQ 不动点收敛需 Jacobian 谱半径 $<1$，Jordan 块结构决定收敛速率。

2. **Oxford C7.1 随机矩阵 → LLM 权重谱（2024-2026）**
   - Marchenko-Pastur 律区分 LLM 权重的"信号奇异值"与"噪声奇异值"，为 LoRA 选秩提供理论。

3. **低秩微调 LoRA/QLoRA 的谱理论（2023-2026）**
   - LoRA（[arXiv:2106.09685](https://arxiv.org/abs/2106.09685)）与 QLoRA（[arXiv:2305.14314](https://arxiv.org/abs/2305.14314)）的低秩更新，根基是 A0 的谱理论 + 奇异值。

📌 **下一步**：→ [Part A A8 Probability](../partA_a8_probability/)
