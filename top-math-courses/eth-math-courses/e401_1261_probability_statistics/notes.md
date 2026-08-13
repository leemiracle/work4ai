# ETH 401-1261 · 概率统计笔记（Klenke + 欧洲严格 + 统计推断特色）

> **教材**：Klenke, *Probability Theory* (Springer)；配 Casella & Berger *Statistical Inference*
> **一手核实**：ETH Zurich 401-1261 课程大纲 (vvz.ethz.ch)
> **特色**：欧洲严格本科；**概率 + 统计统一**——MLE、假设检验、置信区间

---

## 费曼三层讲透

### 🟢 直觉层

- **概率 = 从模型到数据**：给定分布，预测数据长什么样（演绎）
- **统计 = 从数据到模型**：给定数据，推断分布参数（归纳）
- **MLE = 找最可能产生数据的参数**：$\hat\theta = \arg\max P(\text{data}|\theta)$
- **假设检验 = 质疑假设**：$p$-value = "如果假设成立，看到这么极端结果的概率"

---

### 🔵 数学层

## 第 1 章：概率空间与随机变量

### 公理与 Bayes

$P(H|D) = \frac{P(D|H)P(H)}{P(D)}$

### 常见分布

| 分布 | ML 关联 |
|---|---|
| Bernoulli / Binomial | 二分类 |
| Poisson | 稀疏事件 |
| Normal | CLT 核心 |
| Exponential | 无记忆性 → RL 几何折扣 |
| Multinomial | 多分类 / 混合分布 |

---

## 第 2 章：期望、方差与矩

- 线性性、方差公式、独立和方差
- 协方差与相关系数：$\rho = \text{Cov}(X,Y)/(\sigma_X\sigma_Y)$
- **条件方差公式**：$\text{Var}(Y) = E[\text{Var}(Y|X)] + \text{Var}(E[Y|X])$

---

## 第 3 章：极限定理 ★★

### LLN

$\bar{X}_n \xrightarrow{P} \mu$ → SGD 收敛

### CLT ★★★

$\frac{\bar{X}_n-\mu}{\sigma/\sqrt{n}} \xRightarrow{d}\mathcal{N}(0,1)$ → BatchNorm

---

## 第 4 章：统计推断 ★★（ETH 特色）

### 参数估计

#### 矩估计法

令样本矩 = 理论矩，解方程。

#### MLE ★★★

$\hat\theta_{\text{MLE}} = \arg\max_\theta\sum_{i=1}^n\log p(x_i|\theta)$

**性质**：
- 渐近正态：$\sqrt{n}(\hat\theta-\theta_0)\xrightarrow{d}\mathcal{N}(0, I^{-1})$（Fisher 信息矩阵）
- 渐近有效（Cramér-Rao 下界渐近达到）

**ML 关联**：MLE = 最大似然训练 = 所有分类/回归的基础。

#### Fisher 信息

$I(\theta) = -E\left[\frac{\partial^2\log p(X|\theta)}{\partial\theta^2}\right]$

**Cramér-Rao 下界**：$\text{Var}(\hat\theta)\geq 1/(nI(\theta))$

### 假设检验 ★

| 概念 | 定义 |
|---|---|
| 原假设 $H_0$ | 默认假设（如 $\mu=\mu_0$） |
| 统计量 $T$ | 检验统计量（如 $Z=(\bar{X}-\mu_0)/(\sigma/\sqrt{n})$） |
| $p$-value | $P(T\geq t|H_0)$ |
| 显著性水平 $\alpha$ | 拒绝 $H_0$ 的阈值（如 0.05） |
| 功效 $1-\beta$ | 正确拒绝错误 $H_0$ 的概率 |

**ML 关联**：A/B 测试 / 模型选择 / 早期停止。

### 置信区间

$P(\hat\theta-z_{\alpha/2}\cdot\text{SE}\leq\theta\leq\hat\theta+z_{\alpha/2}\cdot\text{SE})\geq 1-\alpha$

**ML 关联**：不确定性量化 / conformal prediction。

### 充分统计量

$T(X)$ 是充分的 $\iff$ $p(x|\theta) = g(T(x),\theta)\cdot h(x)$（因子分解定理）

**ML 关联**：数据压缩——充分统计量包含 $\theta$ 的所有信息。

---

## 第 5 章：贝叶斯推断简介

### 后验分布

$P(\theta|D) \propto P(D|\theta)P(\theta)$（似然 × 先验）

### MAP 估计

$\hat\theta_{\text{MAP}} = \arg\max_\theta [P(D|\theta)P(\theta)]$

**MLE = 均匀先验下的 MAP**。

---

## 频率派 vs 贝叶斯派 ★

| | 频率派 | 贝叶斯派 |
|---|---|---|
| 参数 | 固定未知 | 随机变量 |
| 估计 | MLE / 矩估计 | 后验均值 / MAP |
| 不确定性 | 置信区间 | 可信区间（credible interval） |
| 计算 | 分析 / 数值 | MCMC / 变分推断 |

**ML 关联**：
- 频率派：SGD / MLE → 日常训练
- 贝叶斯派：VAE / diffusion / Bayesian neural networks

---

## 🟠 不足层

1. **MLE 渐近性需要大样本**：小样本时偏差大
2. **假设检验可被操纵**：$p$-hacking / 多重检验问题
3. **正态假设**：重尾分布下 CLT 失效
4. **贝叶斯先验主观性**：不同先验 → 不同后验

---

## 🔴 应用层

| 概念 | ML 场景 |
|---|---|
| MLE | 分类 / 回归训练 |
| CLT | BatchNorm / 统计检验 |
| 假设检验 | A/B 测试 / 模型选择 |
| 置信区间 | 不确定性量化 |
| Bayes | VAE / diffusion / 贝叶斯推断 |
| 充分统计量 | 数据压缩 / summary statistics |

---

## 与 work4ai 讲透系列的交叉

- **讲透 MLE**：交叉熵 = 负对数似然
- **讲透 A/B 测试**：假设检验 + 功效分析
- **讲透 VAE**：贝叶斯变分推断
- **讲透 SGD**：LLN + CLT
