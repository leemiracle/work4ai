# Princeton MAT 514 — Theory of Probability

> **学校**：Princeton | **学期**：Fall (研究生)
> **一手来源**：[math.princeton.edu/graduate](https://www.math.princeton.edu/graduate)

## 课程信息
- **编号**：MAT 514
- **先修**：实分析（MAT 215 或 320 或同等）
- **教材**：Durrett, *Probability: Theory and Examples*；Billingsley *Probability and Measure*
- **特色**：研究生测度论概率

## 教学大纲
1. **Probability spaces & measure theory 速成**
2. **Random variables & expectation**
3. **Modes of convergence**
4. **LLN & CLT**
5. **Conditional expectation**
6. **Martingales**
7. **Brownian motion 入门**

## 与 ML 的关联
- **核心 ML 理论工具**
- **学完本课后**：能读懂所有 ML 理论论文

## 参考资源
- **教材**：Durrett, *Probability: Theory and Examples* (5th ed, 免费 PDF)
- **MIT 对照**：[MIT 18.175](../../mit-math-courses/18_175_probability/)

---

## 📍 在数学全景中的位置

```
本科概率                          Princeton 研究生概率论 → 信息论序列
──────────                        ────────────────────────────────
MAT 215 分析 ──→  MAT 514 概率 ──→  MAT 575 信息论 (Cover & Thomas)
                          ↓                    ↓
                    Durrett 教材          熵 / KL / 互信息
                    SLLN + CLT + 鞅       VAE / diffusion / RLHF
```

- **前置**：[MAT 215 分析](../mat215_analysis/)（实分析，Lebesgue 积分）
- **本课**：测度论概率——概率空间、收敛模式、SLLN、CLT、鞅；**为 MAT 575 信息论打基础**
- **后续**：[MAT 575 信息论](../mat575_information_theory/)（熵、KL 散度、信道编码）

---

## 🔬 理论联系实际

| 概念 | ML / 工程应用 | 公式级对应 |
|---|---|---|
| **SLLN** | SGD 收敛 | $\frac{S_n}{n}\xrightarrow{a.s.}\mu$ → 梯度平均收敛 |
| **CLT** | BatchNorm / 泛化 | $\bar{X}_n \approx \mathcal{N}(\mu,\sigma^2/n)$ |
| **KL 散度** | VAE / RLHF / DPO | $\text{KL}(p\|q) = \sum p\log(p/q)$ → 信息论语言 |
| **鞅 + 可选停时** | RL / 期权定价 | $E[X_\tau]=E[X_0]$ → TD 学习收敛 |
| **Radon-Nikodym 导数** | KL 定义域 / 测度变换 | $\frac{dP}{dQ}$ 存在 $\iff P \ll Q$ |
| **Hoeffding** | 泛化界 | $P(\|\hat{R}-R\|>\epsilon)\leq 2e^{-2n\epsilon^2}$ |

**核心洞察**：MAT 514 的独特定位 = **概率论 → 信息论的桥梁**。Radon-Nikodym 导数 $dP/dQ$ 是 KL 散度 $\text{KL}(P\|Q) = \int\log\frac{dP}{dQ}\,dP$ 的测度论基础。理解这一点是后续 MAT 575 的关键。

---

## 🆕 2024-2026 最新研究

1. **信息论泛化界** ⭐
   - 2024 热点：用互信息 $I(W;S)$ 控制泛化误差
   - **与本课关联**：MAT 514 的 KL 散度 + Pinsker 不等式 → MAT 575 的信息论泛化界

2. **Diffusion model 的测度变换** ⭐
   - 反向 SDE 的推导依赖 Girsanov 定理（Radon-Nikodym 导数）
   - **与本课关联**：MAT 514 的测度论基础 → 理解 Girsanov 定理

3. **Conformal prediction 的测度论基础** ⭐
   - exchangeability 的严格定义需要测度论
   - **与本课关联**：De Finetti 定理（无穷可交换序列 = 条件 i.i.d.）

📌 **下一步**：→ [MAT 575 Information Theory](../mat575_information_theory/)
