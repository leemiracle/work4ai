# Cambridge Part II — Probability and Measure

> **学校**：Cambridge | **学期**：Michaelmas (大三秋)
> **一手来源**：[maths.cam.ac.uk/undergrad/files/coursesII.pdf](https://www.maths.cam.ac.uk/undergrad/files/coursesII.pdf)

## 课程信息
- **学期**：Michaelmas (24 lectures, D-course)
- **教材**：**Williams, *Probability with Martingales*** ★ — **本科测度论概率的金课**
- **特色**：**ML 理论核心课**——把 Part IA/IB 的概率严格化

## 教学大纲
1. **Measure spaces, σ-algebras** ★
2. **Lebesgue 积分**
3. Convergence theorems (MCT, DCT, Fatou)
4. **$L^p$ spaces**
5. **Probability spaces** 严格化
6. **Conditional expectation**（严格）
7. **Martingales**（停时、收敛、可选停时）★
8. **Strong Law of Large Numbers**（严格证明）
9. **Central Limit Theorem**（严格证明）
10. **Brownian motion 入门**

## 与 ML 的关联（**ML 理论基础的核心**）
- **集中不等式** → 泛化界
- **鞅论** → RL 理论
- **学完后**：能读所有 ML 理论论文

## 参考资源
- Williams, *Probability with Martingales* (CUP) ★ — 自学友好
- 替代：Durrett, *Probability: Theory and Examples*
- 替代：Shiryaev, *Probability*

## 学习建议
- **节奏**：每周 6-8 小时，14-16 周
- **Williams 写法**：英式幽默 + 直觉 + 严格证明

---

## 📍 在数学全景中的位置

```
本科概率（无测度论）                    测度论概率                        随机过程 / ML 理论
──────────────                       ──────────                       ─────────────────
Part IA Probability ─┐               Cambridge Part II ──→  Part II Math of ML
Part IB Markov ──────┤──→  Williams *Probability with    ──→  Oxford Part C C8.1 (SDE)
Oxford Part A A8 ────┘     Martingales* (本课)                → diffusion model 理论
                                                                → MCMC 贝叶斯推断
```

- **前置**：[Part IA Probability](../partIA_probability/) + [Part IB Analysis & Topology](../partIB_analysis_topology/)（Lebesgue 积分入门）
- **本课**：Williams 式测度论概率——从 σ-代数到 SLLN/CLT 的严格证明 + 鞅论
- **后续**：[Part II Mathematics of Machine Learning](../partII_mathematics_machine_learning/)（ML 理论）、Oxford Part C SDE（扩散模型）

---

## 🔬 理论联系实际

| 测度论概率概念 | ML / 工程应用 | 公式级对应 |
|---|---|---|
| **SLLN（严格证明）** | SGD 收敛 | $\frac{S_n}{n}\xrightarrow{a.s.}\mu$ → 梯度平均收敛到期望梯度 |
| **DCT（控制收敛定理）** | 交换极限与积分 | $\lim\int f_n = \int \lim f_n$ → 经验风险泛函的极限分析 |
| **鞅收敛定理** | RLHF / RL 算法收敛 | $L^1$-有界鞅 $\to$ a.s. 收敛 → TD 学习的值函数收敛 |
| **可选停时定理** | 期权定价 / RL 停止准则 | $E[X_\tau]=E[X_0]$ → 随机逼近算法的期望不变性 |
| **条件期望 = 投影** | 最小二乘 / 回归 | $E[Y|\mathcal{G}]$ = $L^2$ 投影到 $\mathcal{G}$-可测子空间 |
| **Markov 链遍历定理** | MCMC / PageRank | $\pi P^n \to \pi^*$ → 贝叶斯后验采样的理论基础 |
| **Radon-Nikodym 导数** | KL 散度 / 变分推断 | $\frac{dP}{dQ}$ 存在 $\iff P \ll Q$ → KL$(P\|Q)$ 的定义域 |

**核心洞察**：Williams 教材的英式风格——"严格但充满直觉"。$\sigma$-代数 $\mathcal{F}$ = "你当前知道的信息"，条件期望 $E[\cdot|\mathcal{F}]$ = "在你已知信息下的最佳预测"。

---

## 🆕 2024-2026 最新研究

1. **MCMC 变分推断融合** ⭐
   - 2024 进展：将 MCMC（精确但慢）与变分推断（快但近似）融合，如 Hamiltonian Monte Carlo + Normalizing Flows
   - **与本课关联**：MCMC 的遍历定理保证采样收敛到后验；变分推断的 ELBO 用测度论定义 KL 散度

2. **Diffusion model = 反向 SDE + score matching** ⭐
   - Score-based diffusion（Song et al., arXiv:2011.13456）将生成建模统一为 SDE 反向
   - **与本课关联**：反向 SDE 的推导依赖 Girsanov 定理（测度变换）+ Brownian 运动的鞅性质
   - 2025 进展：Flow Matching / Rectified Flow（Stable Diffusion 3 底层）简化了 SDE 框架

3. **Conformal prediction（保形预测）的测度论基础** ⭐
   - 2024 年成为大模型不确定性量化的标准工具
   - 核心：**交换排列不变性**（exchangeability）是 i.i.d. 的推广，覆盖率保证用遍历定理
   - **与本课关联**：exchangeability + De Finetti 定理（无穷可交换序列 = 条件 i.i.d.）

📌 **下一步**：→ [Part II Mathematics of Machine Learning](../partII_mathematics_machine_learning/)
