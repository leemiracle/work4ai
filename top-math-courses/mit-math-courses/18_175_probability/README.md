# MIT 18.175 — Theory of Probability

> **学校**：MIT | **学期**：Spring（研究生+本科高年级）| **学分**：12 units
> **一手来源**：[catalog.mit.edu/subjects/18/#18.175](https://catalog.mit.edu/subjects/18/) + Prof. Dudley / Prof. Sheffield 历年讲义

## 课程信息
- **编号**：18.175（同号研究生/本科合上）
- **先修**：18.100 实分析（**必须**）
- **教材**：**Durrett, *Probability: Theory and Examples* (5th ed, Cambridge, 2019)** ★
- **备选教材**：Billingsley, *Probability and Measure*；Williams, *Probability with Martingales*；Varadhan, *Probability Theory*

## 教学大纲
1. **Probability spaces**（概率空间、σ-代数、Borel 集）
2. **Random variables & distributions**（随机变量、分布函数、密度）
3. **Expectation**（期望、积分、$L^p$ 空间）
4. **Conditional probability & expectation**（条件期望、martingales 引入）
5. **Modes of convergence**（a.s. / in probability / in $L^p$ / in distribution）
6. **Laws of Large Numbers**（弱大数 / 强大数）
7. **Central Limit Theorem**（特征函数、CLT、Berry-Esseen）
8. **Martingales**（停时、可选停时定理、收敛定理）
9. **Brownian motion**（Brown 运动入门，如时间允许）

## 与 ML 的关联（**ML 理论核心**）
- **集中不等式**（Hoeffding / Bernstein / McDiarmid）：泛化界
- **大数定律 + CLT**：SGD 收敛证明
- **Martingales**：强化学习的理论基础
- **学完本课后**：能读懂 Bartlett / Belkin / Mohri 等 ML 理论论文

## 参考资源
- **教材（开放获取）：Durrett 5th ed PDF**：[services.math.duke.edu/~rtd/PTE/PTE5_011119.pdf](https://services.math.duke.edu/~rtd/PTE/PTE5_011119.pdf)
- **视频**：[MIT 18.175 by Sheffield (2020)](https://www.youtube.com/playlist?list=PLUl4u3cNGP62UU6O3I_PjRV6UhMxFR7-A)（MIT 18.175 / Statistics 213 Harvard 部分视频）
- **替代教材**：Williams, *Probability with Martingales*（Cambridge, 1991）—— 更适合自学的英国版
- **习题集**：Durrett 教材附录习题

## 学习建议
- **节奏**：每周 5-7 小时，14-16 周完成
- **核心**：第 1-7 章（标准 ML 理论用的概率工具）
- **配合**：[Berkeley Stat 134](../../berkeley-math-courses/stat134_probability/)（先学应用版再上 18.175）
- **进阶**：[Berkeley Math 218 随机过程](../../berkeley-math-courses/math218_probability_graduate/)

---

## 📍 在数学全景中的位置

```
本科应用概率                          测度论概率                      随机过程 / 信息论
─────────────                       ──────────                      ─────────────────
Berkeley Stat 134 ─┐
Stanford Stat 116 ─┼──→  MIT 18.175 ──────→  Berkeley Math 218（随机过程 / Brownian）
Cambridge Part IA ─┘    Princeton MAT 514      Princeton MAT 575（信息论）
                        Stanford Math 230A     Oxford Part C C8.1（SDE）
                        Cambridge Part II      ETH 401-3651（数值 SDE）
                        Oxford Part B B8.1
                        UT Austin M 385C
```

- **前置**：[MIT 18.100 实分析](../18_100B_real_analysis/)（Lebesgue 积分、$L^p$ 空间）+ 本科概率（[Stat 134](../../berkeley-math-courses/stat134_probability/) 或 [Stat 116](../../stanford-math-courses/stat116_probability_theory)）
- **本课**：从概率公理到 SLLN + CLT + 鞅，建立 ML 理论的分析语言
- **后续**：随机过程（[Math 218](../../berkeley-math-courses/math218_probability_graduate/) Brownian motion → 扩散模型 SDE）、信息论（[MAT 575](../../princeton-math-courses/mat575_information_theory/)）

---

## 🔬 理论联系实际

| 概率概念 | ML / 工程应用 | 公式级对应 |
|---|---|---|
| **强大数定律 SLLN** | SGD 收敛 | $\frac{1}{n}\sum_{i=1}^n \nabla \ell(\theta; x_i) \xrightarrow{a.s.} \nabla L(\theta)$ → 梯度平均收敛到真实梯度 |
| **中心极限定理 CLT** | Batch Normalization 稳定性 | $\bar{X}_n \approx \mathcal{N}(\mu, \sigma^2/n)$ → mini-batch 梯度噪声正态分布，BN 归一化抑制方差 |
| **Hoeffding 不等式** | 泛化界（PAC 学习） | $P(|\hat{R}(h) - R(h)| > \epsilon) \leq 2e^{-2n\epsilon^2}$ → 样本数 $n$ 与泛化误差的定量关系 |
| **Berry-Esseen** | 有限样本校正 | $|F_n - \Phi| \leq C/\sqrt{n}$ → 小 batch 下 CLT 近似误差的精确常数 |
| **鞅 + 可选停时** | RLHF 收敛 / 期权定价 | $E[X_\tau] = E[X_0]$ → 随机近似算法（如 RL 中的 TD 学习）的期望不变性 |
| **Doob 鞅分解** | 联机学习 regret bound | $f - Ef = \sum D_i$（鞅差）+ Azuma 不等式 → regret $O(\sqrt{T})$ |
| **Markov 链遍历定理** | MCMC / PageRank | $\pi P^n \to \pi^*$（平稳分布）→ 贝叶斯后验采样 / 网页排名 |
| **Brownian motion** | Diffusion model（SDE 基础） | $dX_t = f(X_t)dt + \sigma dW_t$ → 分数扩散模型的前向加噪过程 |

**核心洞察**：ML 理论的两大支柱——**集中不等式**（Hoeffding / McDiarmid → 泛化界）与**随机逼近**（SLLN + 鞅 → SGD / RL 收敛）——都建立在本课的框架上。

---

## 🆕 2024-2026 最新研究

1. **Diffusion model 的 SDE / Score matching 基础** ⭐
   - Song et al. (arXiv:2011.13456) 将扩散模型统一为 SDE：前向 $dX_t = f(X_t)dt + g(t)dW_t$，反向 SDE 需要 **score function** $\nabla \log p_t(x)$
   - 2024-2025 进展：Flow Matching（Lipman et al., arXiv:2210.02747）、Rectified Flow 成为 Stable Diffusion 3 的底层框架
   - **与本课关联**：反向 SDE 的推导依赖 Girsanov 定理（测度变换）+ Brownian motion 的鞅性质

2. **Conformal prediction（保形预测）** ⭐
   - 2024 年成为大模型不确定性量化的标准工具（Amazon / Google 生产部署）
   - 核心：用**交换排列不变性**（exchangeability → i.i.d. 的弱化）构造分布无关的预测区间
   - **与本课关联**：交换排列不变性 = i.i.d. 假设的推广；覆盖率保证用 Hoeffding / DKW 不等式

3. **信息论泛化界（Information-theoretic generalization bounds）** ⭐
   - 2024-2025 热点：用**互信息** $I(W; S)$（算法输出 $W$ 与训练集 $S$ 的互信息）控制泛化误差
   - Russo & Zou (2016), Xu & Raginsky (2017): $|E[R(W)] - E[\hat{R}(W,S)]| \leq \sqrt{2\sigma^2 I(W;S)/n}$
   - **与本课关联**：KL 散度 + Pinsker 不等式 + 鞅方法 → PAC-Bayes 的信息论推广

📌 **下一步**：→ [18.085 计算科学与工程](../18_085_computational_science/) 或 [18.901 拓扑](../18_901_topology/)
