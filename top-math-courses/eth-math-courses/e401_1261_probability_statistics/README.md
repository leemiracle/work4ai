# ETH 401-1261 — Probability and Statistics

> **学校**：ETH Zurich | **学院**：D-MATH
> **一手来源**：[vvz.ethz.ch](https://www.vvz.ethz.ch)

## 课程信息
- **编号**：401-1261-00L（数学专业） / 401-1262-00L（工学院）
- **教材**：Klenke, *Probability Theory*；或 Georgia
- **特色**：本科概率统计

## 教学大纲
1. Probability spaces
2. Random variables
3. Joint distributions
4. Expectation, variance
5. LLN & CLT
6. Statistical inference 入门
7. Hypothesis testing

## 与 ML 的关联
- 标准概率统计

---

## 📍 在数学全景中的位置

```
本科数学基础                        ETH 概率统计序列
──────────                         ────────────────
Analysis I ──→  401-1261 Prob & Stats (本科) ──→  401-4651 Numerical SDE
线性代数 ─────────↗                               ↓
                                            401-3904 Convex Optimization
```

- **前置**：[Analysis I](../e401_0261_analysis_I/) + [线性代数](../e401_0131_linear_algebra/)
- **本课**：Klenke 式欧洲严格概率统计——概率论 + **统计推断（假设检验）**
- **后续**：[401-2611 Numerical Methods](../e401_2611_numerical_methods_cse/) → [401-3651 Numerical SDE](../e401_3651_numerical_sde/)

---

## 🔬 理论联系实际

| 概念 | ML / 工程应用 | 公式级对应 |
|---|---|---|
| **Bayes 定理** | 朴素贝叶斯 / 贝叶斯推断 | $P(H\|D) \propto P(D\|H)P(H)$ |
| **LLN + CLT** | SGD 收敛 + BatchNorm | $\bar{X}_n \to \mu$; $\bar{X}_n \approx \mathcal{N}(\mu,\sigma^2/n)$ |
| **MLE** | 所有参数估计 | $\hat\theta = \arg\max_\theta\prod p(x_i\|\theta)$ |
| **假设检验** | A/B 测试 / 模型选择 | $p$-value = $P(T\geq t\|H_0)$ |
| **置信区间** | 不确定性量化 | $\hat\theta \pm z_{\alpha/2}\cdot\text{SE}$ |
| **充分统计量** | 数据压缩 | $T(X)$ 包含 $\theta$ 的所有信息 |

**核心洞察**：ETH 的特色 = **概率 + 统计的统一**。不同于纯概率课，ETH 401-1261 同时覆盖假设检验和统计推断——这是 ML model selection 和 A/B testing 的数学基础。

---

## 🆕 2024-2026 最新研究

1. **选择性推断（Selective Inference）** ⭐
   - 2024 进展：在模型选择后做统计推断，控制 false coverage rate
   - **与本课关联**：假设检验 + 置信区间的现代推广

2. **大模型不确定性量化** ⭐
   - Conformal prediction 用统计方法保证覆盖率
   - **与本课关联**：置信区间 → 预测区间

3. **差分隐私与统计** ⭐
   - DP-SGD 的噪声校准需要概率统计基础
   - **与本课关联**：假设检验 + 隐私 budget

📌 **下一步**：→ [401-2611 Numerical Methods for CSE](../e401_2611_numerical_methods_cse/)
