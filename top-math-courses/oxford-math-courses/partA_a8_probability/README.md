# Oxford Part A A8 — Probability

> **学校**：Oxford | **学院**：Statistics
> **一手来源**：[courses.maths.ox.ac.uk](https://courses.maths.ox.ac.uk/)

## 课程信息
- **编号**：A8
- **学期**：Part A
- **教材**：Grimmett & Stirzaker, *Probability and Random Processes*
- **特色**：本科应用概率

## 教学大纲
1. Probability spaces
2. Random variables
3. Joint distributions
4. Generating functions
5. LLN & CLT
6. Markov chains

## 与 ML 的关联
- 本科概率（应用版）

---

## 📍 在数学全景中的位置

```
本科数学基础                       Oxford 概率论序列
──────────                        ────────────────
Prelims M1 线代 ──→  Part A A8 Probability (本科应用) ──→  Part B B8.1 (测度论)
Prelims M2 分析 ─────────↗                              ↓
                                                   Part C C8.1 (SDE → 扩散模型)
```

- **前置**：[Prelims M1 线性代数](../prelims_m1_linear_algebra/) + [Prelims M2 分析](../prelims_m2_analysis/)
- **本课**：Grimmett & Stirzaker 风格——条件概率、常见分布、母函数、LLN/CLT、**Markov 链**
- **后续**：[Part B B8.1 Probability, Measure and Martingales](../partB_b8_1_probability_measure_martingales/)（Williams 测度论版）

---

## 🔬 理论联系实际

| 概念 | ML / 工程应用 | 公式级对应 |
|---|---|---|
| **Bayes 定理** | 朴素贝叶斯 / 贝叶斯推断 | $P(H|D) \propto P(D|H)P(H)$ |
| **LLN + CLT** | SGD 收敛 + BatchNorm | $\bar{X}_n \to \mu$; $\bar{X}_n \approx \mathcal{N}(\mu,\sigma^2/n)$ |
| **Markov 链** ★ | MCMC / PageRank / RL | $\pi P = \pi$（平稳分布） |
| **母函数** | 分布卷积 | $G_{X+Y} = G_X G_Y$（独立时） |
| **Chebyshev** | 集中不等式入门 | $P(|X-\mu|\geq k\sigma) \leq 1/k^2$ |
| **Poisson 过程** | 事件流建模 | $N(t) \sim \text{Poisson}(\lambda t)$ |

**核心洞察**：Oxford A8 的特色 = **Markov 链强调**。Grimmett & Stirzaker 的《Probability and Random Processes》是 Markov 链的标准教材——平稳分布、首次通过时间、遍历定理。

---

## 🆕 2024-2026 最新研究

1. **MCMC 在大模型贝叶斯推断中的应用** ⭐
   - 2024 进展：Hamiltonian Monte Carlo + Normalizing Flows 融合
   - **与本课关联**：Markov 链遍历定理 = MCMC 收敛保证

2. **强化学习中的 Markov 性** ⭐
   - MDP（Markov 决策过程）= Markov 链 + 奖励 + 决策
   - **与本课关联**：Markov 性 → 状态转移只需当前状态

3. **PageRank 的概率基础** ⭐
   - 网页排名 = 随机游走的平稳分布
   - **与本课关联**：Markov 链 + 遍历定理

📌 **下一步**：→ [Part A A12 Numerical Analysis](../partA_a12_numerical_analysis/)
