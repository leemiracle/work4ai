# UC Berkeley MATH 218 — Probability Theory (Graduate)

> **学校**：Berkeley | **学期**：Spring
> **一手来源**：[math.berkeley.edu/courses](https://math.berkeley.edu/courses)

## 课程信息
- **编号**：MATH 218（研究生，本科可申请）
- **先修**：MATH 104 + 105 + STAT 134 或同等
- **教材**：**Durrett, *Probability: Theory and Examples***；Billingsley
- **特色**：**Berkeley 概率论核心**——Peres / Sly / Mossel 学派的招牌课

## 教学大纲
1. Probability spaces, σ-algebras
2. Random variables, expectation
3. $L^p$ spaces
4. Convergence modes (a.s. / prob / $L^p$ / dist)
5. LLN & CLT
6. **Martingales**（停时、收敛、可选停时）
7. **Brownian motion** ★
8. **Markov chains**（高级）
9. **Stochastic processes** 入门

## 与 ML 的关联（**ML 理论核心**）
- **集中不等式** → 泛化界
- **鞅** → 强化学习理论
- **Brownian motion** → 扩散模型
- **学完后**：能读懂 Bartlett / Belkin / Mohri 等

## 参考资源
- Durrett, *Probability: Theory and Examples* (免费 PDF)
- Williams, *Probability with Martingales*（更易）
- 替代：Shiryaev, *Probability*

## 学习建议
- **节奏**：每周 6-8 小时，14-16 周
- **核心**：第 4-7 章（ML 理论用的工具）

---

## 📍 在数学全景中的位置

```
本科概率                          Berkeley 概率论序列                    随机过程 / ML 理论
────────                          ────────────────                      ─────────────────
Stat 134 (Pitman) ──→  Math 218 (Peres / Sly 学派) ──→  随机过程 / Brownian motion
MIT 18.175 ─────────→     ↑                                    ↓
Cambridge Part II ────────┘                              集中不等式 / 泛化界
                                                        鞅论 / RL 理论
```

- **前置**：[MATH 104 分析](../math104_analysis/) + [MATH 105](../) + [Stat 134](../stat134_probability/) 或 [MIT 18.175](../../mit-math-courses/18_175_probability/)
- **本课**：Peres / Sly / Mossel 学派的招牌——集中不等式、鞅论、Brownian motion、随机过程
- **后续**：随机过程专题、[Part II Mathematics of ML](../../cambridge-math-courses/partII_mathematics_machine_learning/)（ML 理论）

---

## 🔬 理论联系实际

| Math 218 特色概念 | ML / 工程应用 | 公式级对应 |
|---|---|---|
| **集中不等式**（Hoeffding/McDiarmid/Bernstein）| 泛化界 | $P(\|\hat{R}-R\|>\epsilon)\leq 2e^{-2n\epsilon^2}$ → PAC-Bayes / VC 理论 |
| **Brownian motion** | Diffusion model | $dX_t = \sigma dW_t$ → 前向加噪 SDE |
| **鞅 + Azuma-Hoeffding** | RL regret bound | $P(\|M_n-M_0\|\geq t) \leq 2e^{-t^2/(2\sum c_i^2)}$ → 联机学习 |
| **Markov 链混合时间** | MCMC 效率 | $t_{\text{mix}} = \min\{t: \max_x \|P^t(x,\cdot)-\pi\|_{\text{TV}} \leq 1/4\}$ |
| **大偏差原理** | 罕见事件估计 | $P(\bar{X}_n \notin [a,b]) \approx e^{-nI}$ → 变分推断 |
| **随机过程遍历定理** | 平稳分布采样 | $\frac{1}{n}\sum f(X_k) \to E_\pi[f]$ → 贝叶斯后验采样 |

**核心洞察**：Berkeley 概率论学派的特色 = **集中不等式 + 组合概率 + 随机过程**。Peres 的《布朗运动》讲义是随机几何与扩散模型理论的桥梁。

---

## 🆕 2024-2026 最新研究

1. **Diffusion model 的 SDE 理论** ⭐
   - Song et al. (arXiv:2011.13456) 将扩散模型统一为 SDE 框架；Score matching = 估计 $\nabla\log p_t(x)$
   - 2025 进展：Flow Matching / Rectified Flow（Stable Diffusion 3 底层）简化了 SDE
   - **与本课关联**：前向 SDE $dX_t = f(X_t)dt + g(t)dW_t$ 依赖 Brownian 运动；反向 SDE 需要 Girsanov 定理

2. **Markov 链混合时间与采样效率** ⭐
   - 2024 进展：Langevin Monte Carlo 的混合时间分析（Vempala, Wibisono）
   - 非对数凹分布的采样复杂度 → $O(d\epsilon^{-2})$ vs $O(d\epsilon^{-4})$ 的最新改进
   - **与本课关联**：遍历定理保证收敛，混合时间量化"多快收敛"

3. **信息论泛化界** ⭐
   - 2024 热点：用 $I(W;S)$（算法输出与训练数据的互信息）控制泛化
   - PAC-Bayes 的信息论推广：KL$(Q\|P)$ → 互信息
   - **与本课关联**：集中不等式 + Pinsker 不等式 → 泛化界的桥梁

📌 **下一步**：→ [MATH 202A Topology & Analysis graduate](../math202A_topology_analysis/)
