# Cambridge Part IA — Probability

> **学校**：Cambridge | **课程**：Part IA | **学期**：Lent (大一春)
> **一手来源**：[maths.cam.ac.uk/undergrad](https://www.maths.cam.ac.uk/undergrad)

## 课程信息
- **学期**：Lent (24 lectures)
- **教材**：自编讲义；配 Ross *Probability Models*
- **特色**：本科概率（无测度论）

## 教学大纲
1. Probability spaces, events
2. Conditional probability, Bayes
3. Random variables (discrete/continuous)
4. Joint distributions
5. Expectation, variance
6. Generating functions
7. **LLN** & **CLT** ★
8. Markov chains 入门

## 与 ML 的关联
- 本科应用概率标准课
- 学完后：能读应用 ML 论文

## 参考资源
- Cambridge 讲义（注册学生可访问）
- 替代：Pitman *Probability*

---

## 📍 在数学全景中的位置

```
微积分/分析                         Cambridge 概率论序列
──────────                         ──────────────────
Part IA Analysis I ──→  Part IA Probability (大一春) ──→  Part IB Markov Chains
Part IB Analysis ──────────────↗                        ↘
                                                    Part II Probability & Measure (Williams)
```

- **前置**：[Part IA Analysis I](../partIA_analysis_I/)（基础微积分 rigor）
- **本课**：Cambridge 大一概率——条件概率、Bayes、常见分布、母函数、LLN、CLT（**无测度论，Cambridge 式严格**）
- **后续**：[Part IB Markov Chains](../partIB_markov_chains/) → [Part II Probability and Measure](../partII_probability_measure/)（Williams 测度论版）

---

## 🔬 理论联系实际

| 概念 | ML / 工程应用 | 公式级对应 |
|---|---|---|
| **Bayes 定理** | 朴素贝叶斯 / 贝叶斯推断 | $P(H|D) = \frac{P(D|H)P(H)}{P(D)}$ |
| **LLN** | SGD 收敛 | $\bar{X}_n \xrightarrow{P} \mu$ |
| **CLT** | BatchNorm / 统计检验 | $\bar{X}_n \approx \mathcal{N}(\mu, \sigma^2/n)$ |
| **母函数** | 分布卷积 / 独立和推导 | $G_{X+Y}(s) = G_X(s)G_Y(s)$ |
| **Chebyshev** | 集中不等式入门 | $P(|X-\mu|\geq k\sigma) \leq 1/k^2$ |
| **Markov 链入门** | MCMC / PageRank | $\pi P = \pi$（平稳分布） |

**核心洞察**：Cambridge Part IA 的特色 = **母函数（generating functions）**。Cambridge 传统强调用母函数统一处理离散分布——它是特征函数的无测度论版本。

---

## 🆕 2024-2026 最新研究

1. **大模型不确定性量化** ⭐
   - Conformal prediction 需要 CLT + Bayes 的概率直觉
   - **与本课关联**：LLN + CLT 是覆盖率保证的基础

2. **Diffusion model 的概率直觉** ⭐
   - DDPM（Ho et al., arXiv:2006.11239 ✅）的前向过程 = 正态分布的逐步叠加
   - **与本课关联**：正态分布的线性变换 + 卷积性质

3. **因果推断的概率基础** ⭐
   - do-calculus（Pearl）= 条件概率的精确操作
   - **与本课关联**：Bayes 定理 + 条件独立性

📌 **下一步**：→ [Part IB Markov Chains](../partIB_markov_chains/) 或 [Part IB Linear Algebra](../partIB_linear_algebra/)
