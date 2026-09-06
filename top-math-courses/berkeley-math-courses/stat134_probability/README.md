# UC Berkeley STAT 134 — Concepts of Probability

> **学校**：Berkeley | **学院**：Statistics
> **一手来源**：[stat.berkeley.edu](https://stat.berkeley.edu)

## 课程信息
- **编号**：STAT 134 / 135（统计学续课）
- **先修**：MATH 53 + 54
- **教材**：**Pitman, *Probability*** ★
- **特色**：**本科概率（应用，无测度论）**——直觉极佳

## 教学大纲
1. Conditional probability, Bayes
2. Random variables
3. Joint distributions
4. Expectation, variance, covariance
5. Discrete distributions (binomial, Poisson, geometric, hypergeometric)
6. Continuous distributions (normal, exponential, gamma, beta)
7. **Law of large numbers**
8. **Central limit theorem**
9. **Generating functions**
10. Markov chains 入门

## 与 ML 的关联
- **本科应用概率的最佳入门**
- 学完后：能读应用 ML 论文
- 进阶：[Math 218 / MIT 18.175](../math218_probability_graduate/)（测度论版）

## 参考资源
- Pitman, *Probability* (Springer)
- 替代：Rice, *Mathematical Statistics and Data Analysis*

## 学习建议
- **节奏**：每周 3-5 小时，10-12 周
- **配合**：3Blue1Brown 概率本质

---

## 📍 在数学全景中的位置

```
微积分/线代                     本科应用概率                       测度论概率
──────────                     ──────────                       ──────────
MATH 53 多变量 ──→  Berkeley Stat 134 (Pitman) ──→  MIT 18.175 / Math 218 (测度论)
MATH 54 线代ODE          ↑                              ↓
                    Bayes + CLT + LLN              Stanford Stat 200 (数理统计)
                    （无测度论，直觉优先）            Cambridge Part II (Williams)
```

- **前置**：[MATH 53](../math53_multivariable/) + [MATH 54](../math54_linear_alg_ode/)
- **本课**：Pitman 式概率——条件概率、Bayes 定理、常见分布、LLN、CLT、母函数（**无测度论，直觉极佳**）
- **后续**：[MIT 18.175](../../mit-math-courses/18_175_probability/) 或 [Math 218](../math218_probability_graduate/)（测度论版）

---

## 🔬 理论联系实际

| 概率概念 | ML / 工程应用 | 公式级对应 |
|---|---|---|
| **Bayes 定理** | 朴素贝叶斯 / 变分推断 | $P(\theta|D) = \frac{P(D|\theta)P(\theta)}{P(D)}$ → 后验 = 似然 × 先验 |
| **大数定律 LLN** | SGD 收敛 | $\bar{X}_n \xrightarrow{P} \mu$ → mini-batch 梯度平均收敛到真实梯度 |
| **中心极限定理 CLT** | Batch Normalization | $\bar{X}_n \approx \mathcal{N}(\mu, \sigma^2/n)$ → 梯度噪声正态分布 |
| **Poisson 分布** | 事件计数 / 稀疏数据 | $P(X=k) = e^{-\lambda}\lambda^k/k!$ → 点击率建模、排队论 |
| **指数分布 / 无记忆性** | 生存分析 / RL 时序差分 | $P(X > s+t \| X > s) = P(X > t)$ → 几何折扣的连续类比 |
| **母函数** | 概率分布卷积 | $G_X(s) = E[s^X]$ → 独立随机变量和的分布推导工具 |
| **Chebyshev 不等式** | 集中不等式入门 | $P(|X-\mu| \geq k\sigma) \leq 1/k^2$ → 泛化界的雏形 |

**核心洞察**：Stat 134 是"概率直觉的建立课"——Bayes 定理是贝叶斯推断的引擎，CLT 是统计推断（假设检验、置信区间）的数学基础。

---

## 🆕 2024-2026 最新研究

1. **大语言模型的不确定性量化** ⭐
   - 2024 热点：用 conformal prediction 为 LLM 输出构造分布无关的置信区间
   - 核心概率工具：交换排列（exchangeability = i.i.d. 的弱化）+ Chebyshev/Hoeffding 不等式
   - **与本课关联**：CLT + Bayes 定理是不确定性量化的概率基础

2. **Diffusion model 的概率直觉** ⭐
   - DDPM（Ho et al., arXiv:2006.11239）✅ 的前向过程 = 逐步加高斯噪声
   - 每步 $q(x_t|x_{t-1}) = \mathcal{N}(\sqrt{1-\beta_t}x_{t-1}, \beta_t I)$ → 正态分布叠加
   - **与本课关联**：正态分布的性质（线性变换、卷积）直接用于推导

3. **因果推断中的概率基础** ⭐
   - 2024-2025 进展：do-calculus（Pearl）需要条件概率的精确理解
   - **与本课关联**：Bayes 定理 + 条件独立性 → 因果图 (DAG) 的概率语义

📌 **下一步**：→ [MATH 218 Probability Theory graduate](../math218_probability_graduate/)
