# UT Austin M 362K — Probability I

> **学校**：UT Austin
> **一手来源**：[catalog.utexas.edu](https://catalog.utexas.edu/general-information/coursesatoz/m/)

## 课程信息
- **编号**：M 362K
- **先修**：M 408D + M 325K（或 proof 入门）
- **教材**：Ross, *A First Course in Probability*；或 Pitman

## 教学大纲
1. Combinatorics
2. Probability spaces, axioms
3. Conditional probability, Bayes
4. Random variables (discrete + continuous)
5. Joint distributions
6. Expectation, variance
7. **LLN & CLT** ★
8. Moment generating functions
9. Markov chains 入门

## 与 ML 的关联
- 本科应用概率
- 学完后：能读 ML 论文的概率部分

---

## 📍 在数学全景中的位置

```
本科微积分                          UT Austin 概率论序列                      ML 理论
──────────                         ──────────────────                       ────────
M 408D 微积分 ──→  M 362K 概率 I (本科应用) ──→  M 385C 概率论 (研究生测度论) ──→  集中不等式 / 泛化界
M 325K 离散数学 ──↗   (Ross, 无测度论)            (Durrett, σ-代数/鞅)             鞅 → RL / 扩散模型
```

- **前置**：[M 408D 微积分](../m408c_calculus/)（积分、级数）+ [M 325K 离散数学](../)（组合计数、证明入门）
- **本课**：本科应用概率——组合计数、概率公理、条件概率/Bayes、离散+连续随机变量、联合分布、期望方差、母函数、LLN/CLT、Markov 链入门（**无测度论，计算导向**）
- **后续**：[M 385C 概率论（研究生）](../m385c_theory_of_probability/)（测度论版）→ ML 理论（集中不等式、鞅、扩散模型 SDE）

---

## 🔬 理论联系实际

| 概率概念 | ML / 工程应用 | 公式级对应 |
|---|---|---|
| **Bayes 定理** | 朴素贝叶斯 / 贝叶斯推断 | $P(H\|D) = \dfrac{P(D\|H)P(H)}{P(D)}$ → 分类器 $y^*=\arg\max_y P(y)\prod_i P(x_i\|y)$ |
| **条件概率 / 独立性** | 朴素贝叶斯独立性假设 | $P(x_1,\dots,x_n\|y)=\prod_i P(x_i\|y)$ → 特征条件独立简化似然 |
| **期望 / 方差** | 风险最小化 / BatchNorm | $R(\theta)=E[\ell(\theta;X)]$；$\text{Var}=\sigma^2$ → BN 用 $\bar{X}\approx E$ 归一化 |
| **大数定律 LLN** | SGD 收敛 | $\dfrac{1}{n}\sum\nabla\ell(\theta;x_i)\xrightarrow{P}\nabla L(\theta)$ → 小批量梯度收敛到真实梯度 |
| **中心极限定理 CLT** | BatchNorm 稳定性 / 参数初始化 | $\bar{X}_n\approx\mathcal{N}(\mu,\sigma^2/n)$ → mini-batch 梯度噪声正态分布 |
| **矩母函数 MGF** | Chernoff 界 / 分布卷积 | $M_X(t)=E[e^{tX}]$ → $P(S_n\geq a)\leq\inf_t e^{-ta}M_S(t)$（集中不等式起点）|
| **Markov 链** | MCMC / PageRank / RL | $\pi P=\pi$（平稳分布）→ PageRank 求最大特征向量；MDP 的转移核 |
| **Chebyshev 不等式** | 弱泛化界入门 | $P(\|X-\mu\|\geq k\sigma)\leq 1/k^2$ → 样本均值偏离的概率上界 |

**核心洞察**：M 362K 的全部应用都归结为两件事——**Bayes 定理**（朴素贝叶斯、贝叶斯推断、变分推断的起点）与 **LLN + CLT**（SGD 收敛、BatchNorm、参数初始化的理论根基）。这两条是从本科概率通向 ML 的主干道。

---

## 🆕 2024-2026 最新研究

1. **大模型不确定性量化：Conformal Prediction** ⭐
   - 2024-2025 成为大模型生产部署的标准工具（Amazon / Google）
   - 核心：用 i.i.d. 样本的**交换排列不变性**构造分布无关的预测区间，覆盖率保证用 LLN + Hoeffding
   - **与本课关联**：LLN + Chebyshev 是覆盖率保证的基础；本科生能从 M 362K 直接连通工业级不确定性量化

2. **Diffusion model 的概率直觉** ⭐
   - DDPM（Ho et al., arXiv:2006.11239 ✅）的前向过程 = 正态分布的逐步叠加；2024-2025 的 Flow Matching / Rectified Flow 成为 Stable Diffusion 3 底层
   - **与本课关联**：正态分布的线性变换、独立正态的和仍是正态（MGF 卷积性质）、条件概率用于反向去噪

3. **因果推断的概率基础** ⭐
   - do-calculus（Pearl）= 条件概率的精确操作；2024 年因果 + 大模型成为热点
   - **与本课关联**：M 362K 的条件概率 / Bayes / 条件独立性是 do-calculus 的全部概率基础

📌 **下一步**：→ [M 378K Numerical Analysis](../m378k_numerical_analysis/) 或 [M 385C Theory of Probability graduate](../m385c_theory_of_probability/)
