# Stanford STAT 116 — Probability Theory

> **学校**：Stanford | **学院**：Statistics
> **一手来源**：[stat.stanford.edu](https://stat.stanford.edu)

## 课程信息
- **编号**：STAT 116（本科）
- **先修**：MATH 51 + 一点编程
- **教材**：Ross, *Introduction to Probability Models*；或 Bertsekas & Tsitsiklis
- **特色**：本科概率（无测度论）

## 教学大纲
1. Sample space, events, axioms
2. Conditional probability, Bayes
3. Random variables (discrete & continuous)
4. Joint distributions
5. Expectation & variance
6. **Law of large numbers**
7. **Central limit theorem**
8. **Moment-generating functions**
9. **Markov chains 入门**
10. **Exponential distribution & Poisson process**

## 与 ML 的关联
- 概率论的"直觉版本"（无测度）
- 学完后：能读应用 ML 论文
- 进阶：[MATH 230A](../math230A_probability_theory/)（测度论版）

## 参考资源
- Bertsekas & Tsitsiklis, *Introduction to Probability* (2nd ed)
- Ross, *A First Course in Probability*
- Berkeley 对照：[Stat 134](../../berkeley-math-courses/stat134_probability/)

---

## 📍 在数学全景中的位置

```
微积分/线代                     本科概率（Ross/Bertsekas 风格）           测度论概率
──────────                     ──────────────────────                    ──────────
MATH 51 ──→  Stanford Stat 116 ──→  Stanford Math 230A (研究生测度论)
                    ↑                           ↓
              Bayes + CLT + Poisson        Berkeley Math 218 / MIT 18.175
              母函数 + Markov 链
```

- **前置**：[MATH 51](../math51_linear_multivariable/) + 一点编程
- **本课**：Ross / Bertsekas 风格——条件概率、常见分布、母函数、Poisson 过程、Markov 链入门
- **后续**：[Math 230A](../math230A_probability_theory/)（研究生测度论版）

---

## 🔬 理论联系实际

| 概率概念 | ML / 工程应用 | 公式级对应 |
|---|---|---|
| **Bayes 定理** | 朴素贝叶斯 / 贝叶斯推断 | $P(\theta|D) \propto P(D|\theta)P(\theta)$ |
| **CLT** | 统计假设检验 / BatchNorm | $\bar{X}_n \approx \mathcal{N}(\mu, \sigma^2/n)$ |
| **Poisson 过程** | 事件流建模 / 排队论 | $N(t) \sim \text{Poisson}(\lambda t)$ → 点击流、API 请求 |
| **指数分布 + 无记忆性** | 生存分析 / RL 几何折扣 | $P(X>s+t\|X>s) = P(X>t)$ → $\gamma^t$ 的连续类比 |
| **矩母函数 MGF** | 分布卷积 / CLT 证明 | $M_{X+Y}(t) = M_X(t)M_Y(t)$（独立时） |
| **Markov 链** | MCMC / PageRank / RL | $\pi P = \pi$ → 平稳分布 / 网页排名 |
| **Chebyshev 不等式** | 集中不等式入门 | $P(|X-\mu| \geq k\sigma) \leq 1/k^2$ |

**核心洞察**：Stanford Stat 116 的特色 = **Poisson 过程 + Markov 链入门**。Ross 的《概率模型》强调"建模思维"——用概率分布描述现实世界的随机现象。

---

## 🆕 2024-2026 最新研究

1. **Conformal prediction（保形预测）** ⭐
   - 2024 年成为 LLM 不确定性量化的标准工具（Stanford 统计系主导）
   - 核心：用**交换排列不变性**（= i.i.d. 的弱化）构造分布无关的预测区间
   - **与本课关联**：CLT + Chebyshev 不等式是覆盖率保证的基础

2. **大模型采样的概率视角** ⭐
   - Temperature sampling / Top-p (nucleus) sampling 的概率本质
   - 温度 $T$ 调整：$p_T(y|x) \propto p(y|x)^{1/T}$ → 低温更确定，高温更随机
   - **与本课关联**：多项分布采样 + Boltzmann 分布

3. **Poisson 过程在流式学习中的应用** ⭐
   - 数据以 Poisson 过程到达 → 在线学习的理论基础
   - 2024 进展：Poisson 到达 + SGD 的收敛分析
   - **与本课关联**：Poisson 过程的独立增量性 → 在线梯度计算的独立性

📌 **下一步**：→ 进入 [Berkeley 数学](../../berkeley-math-courses/)
