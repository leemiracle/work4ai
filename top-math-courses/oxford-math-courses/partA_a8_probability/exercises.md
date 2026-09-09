# Oxford Part A A8 · 习题集（Grimmett & Stirzaker + Markov 链 + ML 应用）

---

## 基础题

### Q1.1（Bayes 定理）
医学检测：发病率 5%，灵敏度 98%，特异度 92%。检测阳性后患病概率？

<details><summary>解</summary>

$P(D|+) = \frac{0.98 \times 0.05}{0.98 \times 0.05 + 0.08 \times 0.95} = \frac{0.049}{0.049+0.076} = \frac{0.049}{0.125} \approx 0.392$

**ML 关联**：Precision 的概率本质——类别不平衡时的假阳性影响。
</details>

### Q1.2（Markov 链基本计算）
天气 Markov 链：晴→晴 0.7, 晴→雨 0.3, 雨→晴 0.4, 雨→雨 0.6。今天是晴天，后天是雨天的概率？

<details><summary>解</summary>

$P^{(2)} = P^2$：

$P = \begin{pmatrix} 0.7 & 0.3 \\ 0.4 & 0.6 \end{pmatrix}$

$P^2 = \begin{pmatrix} 0.7\times0.7+0.3\times0.4 & 0.7\times0.3+0.3\times0.6 \\ \ldots & \ldots \end{pmatrix} = \begin{pmatrix} 0.61 & 0.39 \\ 0.52 & 0.48 \end{pmatrix}$

从晴天出发，后天下雨概率 = $0.39$

**ML 关联**：n 步转移概率 = 转移矩阵的幂。
</details>

---

## 中等题

### Q2.1（平稳分布求解）★
求上述天气 Markov 链的平稳分布。

<details><summary>解</summary>

$\pi P = \pi$：

$0.7\pi_1 + 0.4\pi_2 = \pi_1 \Rightarrow 0.4\pi_2 = 0.3\pi_1 \Rightarrow \pi_1 = \frac{4}{3}\pi_2$

$\pi_1 + \pi_2 = 1 \Rightarrow \pi_1 = 4/7, \pi_2 = 3/7$

长期来看：晴天 57.1%，雨天 42.9%。

**ML 关联**：PageRank = Markov 链的平稳分布。
</details>

### Q2.2（CLT 应用）
$X_1, \dots, X_{25}$ i.i.d. Exponential(2)。估计 $P(\bar{X}_{25} > 0.6)$。

<details><summary>解</summary>

$\mu = 0.5$, $\sigma^2 = 0.25$, $\sigma = 0.5$

$P(\bar{X}_{25} > 0.6) = P\left(Z > \frac{0.1}{0.5/5}\right) = P(Z > 1) \approx 0.159$

**ML 关联**：A/B 测试的显著性。
</details>

### Q2.3（首次返回时间）
对称随机游走在 $\mathbb{Z}$ 上。从 0 出发首次返回 0 的平均时间？

<details><summary>解</summary>

对称游走在 1 维是零常返（$E[\tau_{00}] = \infty$）！

虽然 $P(\text{返回}) = 1$（常返），但 $E[\tau_{00}] = \infty$（零常返）。

**ML 关联**：这是"常返但不正常返"的经典反例——MCMC 中需要确保正常返。
</details>

---

## 开放题

### Q3.1（MCMC 采样原理）★
Metropolis-Hastings 用 Markov 链从目标分布采样。解释遍历定理如何保证采样正确。

<details><summary>解（思路）</summary>

1. 构造转移核使 $\pi$ 是平稳分布（细致平衡 $\pi_i P_{ij} = \pi_j P_{ji}$）
2. 不可约 + 非周期 → 遍历定理适用
3. $\frac{1}{N}\sum f(X_k) \xrightarrow{a.s.} E_\pi[f]$

→ 样本均值 → 后验期望

**ML 关联**：贝叶斯推断的核心采样工具。
</details>

### Q3.2（PageRank 推导）★
网页链接图如何构成 Markov 链？PageRank 如何用平稳分布排名？

<details><summary>解（思路）</summary>

1. 邻接矩阵 $A$：$A_{ij} = 1/\text{outdeg}(j)$ 如果 $j \to i$
2. 阻尼因子：$P = \alpha A + (1-\alpha)\frac{1}{N}\mathbf{1}\mathbf{1}^T$
3. PageRank = $\pi^*$（$P$ 的平稳分布）
4. 幂迭代 $\pi^{(t+1)} = \pi^{(t)} P$ → 收敛

**ML 关联**：推荐系统 / 社交网络排名。
</details>

### Q-Final（强化学习的 Markov 性）★
解释 MDP（Markov Decision Process）为什么是 Markov 链的推广，以及 Bellman 方程的概率基础。

<details><summary>解（思路）</summary>

MDP = Markov 链 + 策略 $\pi(a|s)$ + 奖励 $r(s,a)$ + 折扣 $\gamma$

状态转移：$P(s'|s,a)$（给定状态-动作后只依赖当前）

Bellman 方程：$V(s) = E[r + \gamma V(s')] = \sum_a \pi(a|s)\sum_{s'} P(s'|s,a)[r(s,a,s')+\gamma V(s')]$

**Markov 性**：$V(s)$ 只依赖当前状态 $s$，不需要历史。

**ML 关联**：Q-learning / Policy Gradient 的理论基础。
</details>
