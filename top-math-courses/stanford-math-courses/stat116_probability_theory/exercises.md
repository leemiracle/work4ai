# Stanford STAT 116 · 习题集（Ross / Bertsekas 精选 + ML 应用）

---

## 基础题

### Q1.1（Bayes 定理）
三种疾病 A, B, C 的发病率分别为 50%, 30%, 20%。某症状在 A 下出现概率 90%，B 下 60%，C 下 30%。观察到该症状，最可能哪种病？

<details><summary>解</summary>

$P(A|S) \propto 0.5 \times 0.9 = 0.45$

$P(B|S) \propto 0.3 \times 0.6 = 0.18$

$P(C|S) \propto 0.2 \times 0.3 = 0.06$

归一化：$0.45 + 0.18 + 0.06 = 0.69$

$P(A|S) = 0.45/0.69 \approx 0.652$ → 最可能是 A

**ML 关联**：朴素贝叶斯分类器的预测过程。
</details>

### Q1.2（Poisson 分布）
客服中心每分钟平均 2 个电话。5 分钟内恰好接到 8 个的概率？

<details><summary>解</summary>

$N(5) \sim \text{Poisson}(10)$

$P(N(5)=8) = e^{-10}10^8/8! = e^{-10} \times 10^8/40320 \approx 0.1126$

**ML 关联**：Poisson 回归建模计数数据。
</details>

---

## 中等题

### Q2.1（CLT + 正态近似）
100 个 Uniform(0,1) 的和 $S_{100}$。用 CLT 估计 $P(S_{100} > 55)$。

<details><summary>解</summary>

$\mu = 50$, $\sigma^2 = 100/12 \approx 8.33$, $\sigma \approx 2.89$

$P(S_{100} > 55) = P\left(\frac{S-50}{2.89} > \frac{5}{2.89}\right) \approx P(Z > 1.73) \approx 0.042$

**ML 关联**：假设检验 / 置信区间。
</details>

### Q2.2（Poisson 过程叠加）
两个独立 Poisson 过程，参数 $\lambda_1 = 3$, $\lambda_2 = 5$。叠加后第一个事件来自过程 1 的概率？

<details><summary>解</summary>

叠加后是参数 $\lambda_1 + \lambda_2 = 8$ 的 Poisson 过程。

第一个事件来自过程 1 的概率 = $\lambda_1 / (\lambda_1 + \lambda_2) = 3/8$

**直觉**：到达速率的比值。

**ML 关联**：多源事件流的竞争分析。
</details>

### Q2.3（Markov 链平稳分布）
转移矩阵 $P = \begin{pmatrix} 0.9 & 0.1 \\ 0.5 & 0.5 \end{pmatrix}$，求平稳分布并计算平均在状态 1 停留的时间比例。

<details><summary>解</summary>

$\pi P = \pi$：

$0.9\pi_1 + 0.5\pi_2 = \pi_1 \Rightarrow 0.5\pi_2 = 0.1\pi_1 \Rightarrow \pi_1 = 5\pi_2$

$\pi_1 + \pi_2 = 1 \Rightarrow \pi_1 = 5/6, \pi_2 = 1/6$

平均在状态 1 停留比例 = $5/6 \approx 83.3\%$

**ML 关联**：PageRank = Markov 链平稳分布。
</details>

---

## 开放题

### Q3.1（PageRank 推导）★
网页链接图构成 Markov 链。解释 PageRank 如何用平稳分布给网页排名。

<details><summary>解（思路）</summary>

1. 构建邻接矩阵 $A$：$A_{ij} = 1/\text{outdeg}(j)$ 如果 $j \to i$ 有链接
2. 添加阻尼因子：$P = \alpha A + (1-\alpha)\frac{1}{N}\mathbf{1}\mathbf{1}^T$（$\alpha \approx 0.85$）
3. PageRank = $P$ 的平稳分布 $\pi^*$（最大特征值 1 对应的特征向量）
4. 求解：幂迭代 $\pi^{(t+1)} = \pi^{(t)} P$ 直到收敛

**$\alpha$ 的作用**：防止"悬挂节点"（没有出链的网页）；模拟"随机跳转到任意网页"的概率。

**ML 关联**：Markov 链平稳分布 → 推荐系统 / 社交网络排名。
</details>

### Q3.2（MCMC 采样原理）★
Metropolis-Hastings 用 Markov 链从不可归一化分布 $\tilde{\pi}(x)$ 采样。解释遍历定理如何保证采样正确。

<details><summary>解（思路）</summary>

构造转移核使 $\pi$ 是平稳分布（细致平衡 $\pi(x)P(x,y) = \pi(y)P(y,x)$）。

遍历定理：$\frac{1}{N}\sum_{i=1}^N f(X_i) \xrightarrow{a.s.} E_\pi[f(X)]$

→ 样本均值收敛到目标分布的期望。

**ML 关联**：贝叶斯推断中从后验分布 $\pi(\theta|D)$ 采样。
</details>

### Q-Final（温度采样的概率本质）★
LLM 的温度采样 $p_T(y) \propto p(y)^{1/T}$。解释 $T$ 如何影响生成质量与多样性。

<details><summary>解（思路）</summary>

$T \to 0$：$p_T(y)$ 趋于 one-hot（贪心解码），确定性最高，多样性最低

$T = 1$：原始分布

$T \to \infty$：$p_T(y)$ 趋于均匀分布，完全随机

**信息论视角**：$H(p_T) = \frac{1}{T}H(p) + \log Z(T)$（$Z$ 是归一化常数）

低温 → 低熵 → 高确定性；高温 → 高熵 → 高多样性。

**ML 关联**：Top-p (nucleus) sampling 是温度采样的改进版。
</details>
