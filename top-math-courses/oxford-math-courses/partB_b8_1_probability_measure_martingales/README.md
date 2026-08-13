# Oxford Part B B8.1 — Probability, Measure and Martingales

> **学校**：Oxford | **学院**：Statistics
> **一手来源**：[courses.maths.ox.ac.uk](https://courses.maths.ox.ac.uk/)

## 课程信息
- **编号**：B8.1
- **学期**：Part B (Year 3)
- **教材**：Williams, *Probability with Martingales*；或 Shiryaev
- **特色**：**Oxford 测度论概率金课**

## 教学大纲
1. Measure spaces, σ-algebras
2. Lebesgue 积分
3. Convergence theorems
4. $L^p$ spaces
5. **Probability spaces**
6. **Conditional expectation**
7. **Martingales**（停时、收敛）★
8. **Strong Law, CLT**

## 与 ML 的关联（**ML 理论核心**）
- 与 [Cambridge Part II Probability and Measure](../../cambridge-math-courses/partII_probability_measure/) 同类
- 学完后：能读 ML 理论论文

## 参考资源
- Williams, *Probability with Martingales* (CUP)
- Shiryaev, *Probability* (Springer)

---

## 📍 在数学全景中的位置

```
本科概率                          Oxford 测度论概率                      高级随机过程
──────────                        ────────────────                      ────────────
Part A A8 ──→  Part B B8.1 (Williams 测度论) ──→  Part C C8.1 (SDE → 扩散模型)
                          ↓                          ↓
                    鞅 + 条件期望                Brownian motion + Itô 积分
                    SLLN + CLT 严格证明           反向 SDE / Score matching
```

- **前置**：[Part A A8 Probability](../partA_a8_probability/) + [Part A 分析]
- **本课**：Williams 式测度论概率——σ-代数、Lebesgue 积分、鞅论、SLLN/CLT 严格证明
- **后续**：[Part C C8.1 SDE](../partC_c8_1_sde/)（扩散模型理论基础）

---

## 🔬 理论联系实际

| 概念 | ML / 工程应用 | 公式级对应 |
|---|---|---|
| **SLLN（严格证明）** | SGD 收敛 | $\frac{S_n}{n}\xrightarrow{a.s.}\mu$ |
| **鞅 + 可选停时** | RL / 期权定价 | $E[X_\tau]=E[X_0]$ |
| **条件期望 = $L^2$ 投影** | 回归 / 最小二乘 | $E[Y|\mathcal{G}]$ = 正交投影 |
| **DCT（控制收敛）** | 交换极限与积分 | $\lim\int f_n = \int\lim f_n$ |
| **Doob 分解** | 联机学习 | $X_n = M_n + A_n$（鞅 + 可料） |
| **Azuma-Hoeffding** | regret bound | $P(|M_n-M_0|\geq t) \leq 2e^{-t^2/(2\sum c_i^2)}$ |

**核心洞察**：Oxford B8.1 与 [Cambridge Part II](../../cambridge-math-courses/partII_probability_measure/) 使用同一本教材（Williams），但 Oxford 的视角更偏向**随机过程分析**，为 Part C SDE 课程做准备。

---

## 🆕 2024-2026 最新研究

1. **Diffusion model 的 SDE 理论** ⭐
   - 反向 SDE 推导需要 Girsanov 定理（测度变换）+ Brownian 运动的鞅性质
   - **与本课关联**：B8.1 的鞅论 + Radon-Nikodym 导数 → Part C SDE

2. **信息论泛化界** ⭐
   - PAC-Bayes 的信息论推广需要测度变换（Donsker-Varadhan）
   - **与本课关联**：B8.1 的测度论基础

3. **MCMC 收敛分析** ⭐
   - 鞅方法分析 Markov 链的混合时间
   - **与本课关联**：B8.1 的鞅收敛定理

📌 **下一步**：→ [Part C C7.1 Random Matrix Theory](../partC_c7_1_random_matrix_theory/) 或 [Part C C8.1 SDE](../partC_c8_1_sde/)
