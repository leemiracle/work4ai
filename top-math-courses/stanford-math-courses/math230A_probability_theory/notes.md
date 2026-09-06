# Stanford MATH 230A · 概率论 I 笔记（Durrett + Stanford 序列视角）

> **教材**：Durrett, *Probability: Theory and Examples* (5th ed)
> **一手核实**：Stanford Math 230A 课程大纲
> **特色**：3 学期序列的第 1 学期；严格测度论概率；为 230B 随机过程打基础

---

## 费曼三层讲透

### 🟢 直觉层

- **σ-代数 = 你知道的信息**：$\mathcal{F}_n$ = 到时刻 $n$ 为止你观测到的所有事件
- **鞅 = 公平赌博**：$E[X_{n+1}|\mathcal{F}_n] = X_n$ → 无论怎么下注，期望财富不变
- **条件期望 = 最佳预测**：$E[Y|\mathcal{G}]$ = 在已知 $\mathcal{G}$ 下对 $Y$ 的最优 $L^2$ 估计

---

### 🔵 数学层

## 第 1 章：概率空间与测度论速成

### σ-代数与概率空间

$(\Omega, \mathcal{F}, P)$。滤波 $\mathcal{F}_0 \subseteq \mathcal{F}_1 \subseteq \cdots$ = 信息流。

### Lebesgue 积分 + 三大收敛定理

| 定理 | 条件 | 结论 |
|---|---|---|
| MCT | $0 \leq f_n \uparrow f$ | $\int f_n \uparrow \int f$ |
| DCT | $\|f_n\| \leq g, f_n \to f$ | $\int f_n \to \int f$ |
| Fatou | $f_n \geq 0$ | $\int\liminf \leq \liminf\int$ |

---

## 第 2 章：收敛模式 ★★★

| 模式 | 定义 | 蕴含 |
|---|---|---|
| a.s. | $P(X_n \to X) = 1$ | → P → d |
| $L^p$ | $E|X_n - X|^p \to 0$ | → P |
| 依概率 | $P(|X_n - X| > \epsilon) \to 0$ | → d |
| 依分布 | $F_n \to F$ 连续点 | — |

**ML 关联**：a.s. 收敛（SGD 确定性）> 依概率收敛 > 依分布收敛（CLT）。

---

## 第 3 章：LLN + CLT ★★

### SLLN

$\frac{S_n}{n} \xrightarrow{a.s.} \mu$ → SGD 梯度收敛的理论根基

### CLT

$\frac{S_n - n\mu}{\sigma\sqrt{n}} \xRightarrow{d} \mathcal{N}(0,1)$ → 梯度噪声正态化 / BatchNorm

### Berry-Esseen

$\sup|F_n - \Phi| \leq CE|X-\mu|^3/(\sigma^3\sqrt{n})$ → 收敛速度 $O(1/\sqrt{n})$

---

## 第 4 章：条件期望 ★★

$Y = E[X|\mathcal{G}]$：$\mathcal{G}$-可测且 $\int_A Y = \int_A X, \forall A \in \mathcal{G}$

**几何直觉**：$L^2$ 中的正交投影 → 回归 = 条件期望的逼近

**塔性质**：$E[E[X|\mathcal{G}]] = E[X]$

---

## 第 5 章：鞅 ★★★

### 定义

$E[X_{n+1}|\mathcal{F}_n] = X_n$

### 可选停时

$E[X_\tau] = E[X_0]$（条件下）→ 对称游走首达 $\pm a$ 时间 $E[\tau] = a^2$

### 鞅收敛

$L^1$-有界下鞅 → a.s. 收敛

### Doob 分解 + 不等式

$X_n = M_n + A_n$；Doob 极大值不等式；Azuma-Hoeffding

---

## 集中不等式速查

| 不等式 | 条件 | 结论 |
|---|---|---|
| Hoeffding ★ | $X_i \in [a_i,b_i]$ | $P(|S_n-ES_n|\geq t) \leq 2e^{-2t^2/\sum(b_i-a_i)^2}$ |
| McDiarmid ★ | Lipschitz $f$ | $P(|f-Ef|\geq t) \leq 2e^{-2t^2/\sum c_i^2}$ |
| Azuma | 鞅差 $|D_i|\leq c_i$ | $P(|M_n-M_0|\geq t) \leq 2e^{-t^2/(2\sum c_i^2)}$ |

### Hoeffding → PAC 泛化界 ★

$$P(|\hat{R}(h) - R(h)| > \epsilon) \leq 2e^{-2n\epsilon^2}$$

Union bound over $|\mathcal{H}|$：$\epsilon = \sqrt{\frac{\ln(2|\mathcal{H}|/\delta)}{2n}}$

---

## Diffusion Model 的 SDE 基础（Math 230B 预览）★

### Brownian Motion

$W_t$：独立增量、$W_t-W_s \sim \mathcal{N}(0,t-s)$、连续路径

### Itô 引理

$$df(W_t) = f'(W_t)\,dW_t + \frac{1}{2}f''(W_t)\,dt$$

### 前向 SDE（扩散模型加噪）

$$dX_t = -\frac{1}{2}\beta_t X_t\,dt + \sqrt{\beta_t}\,dW_t$$

### 反向 SDE（生成）

$$dX_t = \left[-\frac{1}{2}\beta_t X_t - \beta_t\nabla\log p_t(X_t)\right]dt + \sqrt{\beta_t}\,d\bar{W}_t$$

→ 需要 score function $\nabla\log p_t$ → 用神经网络估计（score matching）

---

## 频率派 vs 贝叶斯派

- **频率派**：概率 = 长期频率。MLE。参数固定。
- **贝叶斯派**：概率 = 信念。后验分布。参数随机。
- **ML 实践**：SGD = 频率派；VAE/diffusion = 贝叶斯派根源

---

## 🟠 不足层

1. **i.i.d. 假设**：时间序列/图数据不满足
2. **CLT 对重尾失效**：Cauchy 方差不存在
3. **高维集中不等式松**：$O(\sqrt{d/n})$ 在高维下很松
4. **Brownian 运动理想化**：真实噪声非高斯时需 Lévy 过程

---

## 🔴 应用层

| 概念 | ML 场景 |
|---|---|
| SLLN | SGD 收敛 |
| CLT | BatchNorm / 梯度噪声 |
| 鞅 + 可选停时 | RL TD 学习 |
| Hoeffding/McDiarmid | 泛化界 |
| Brownian + Itô | 扩散模型 SDE |
| 条件期望 = 投影 | 回归分析 |

---

## 与 work4ai 讲透系列的交叉

- **讲透泛化**：集中不等式 + PAC-Bayes
- **讲透 SGD**：SLLN + CLT + 鞅
- **讲透扩散模型**：Brownian + 反向 SDE
- **讲透 RL**：鞅 → TD 学习
