# Oxford Part B B8.1 · Probability, Measure and Martingales 笔记（Williams）

> **教材**：Williams, *Probability with Martingales* (CUP, 1991)
> **一手核实**：Oxford Part B B8.1 课程大纲
> **特色**：测度论概率金课；Williams 式英式严格 + 直觉；为 Part C SDE 打基础

---

## 费曼三层讲透

### 🟢 直觉层

- **σ-代数 = 你知道的信息**：$\mathcal{F}_n$ = 时刻 $n$ 为止的观测
- **鞅 = 公平赌博**：$E[X_{n+1}|\mathcal{F}_n] = X_n$ → 期望财富不变
- **条件期望 = 最佳预测**：$E[Y|\mathcal{G}]$ = 已知 $\mathcal{G}$ 下 $Y$ 的最优 $L^2$ 估计

---

### 🔵 数学层

## 第 1 章：测度论基础

### σ-代数 + 测度

$(\Omega, \mathcal{F}, \mu)$。概率测度 $P(\Omega)=1$。

### Lebesgue 积分 + 三大收敛定理

| 定理 | 条件 | 结论 |
|---|---|---|
| MCT | $0 \leq f_n \uparrow f$ | $\int f_n \uparrow \int f$ |
| DCT | $\|f_n\| \leq g$, $f_n \to f$ | $\int f_n \to \int f$ |
| Fatou | $f_n \geq 0$ | $\int\liminf \leq \liminf\int$ |

**ML 关联**：DCT = 交换极限与积分的标准工具。

---

## 第 2 章：收敛模式 ★★★

| 模式 | 定义 | ML 关联 |
|---|---|---|
| a.s. | $P(X_n\to X)=1$ | SGD 确定性收敛 |
| $L^p$ | $E|X_n-X|^p\to 0$ | 均方收敛 |
| 依概率 | $P(|X_n-X|>\epsilon)\to 0$ | 弱保证 |
| 依分布 | $F_n\to F$ 连续点 | CLT |

蕴含：$a.s. \Rightarrow P \Rightarrow d$；$L^p \Rightarrow P$。

---

## 第 3 章：LLN + CLT（严格证明）★★

### SLLN

$\frac{S_n}{n}\xrightarrow{a.s.}\mu$（Williams 用鞅方法证明）

**证明思路**：截断 → Borel-Cantelli → Kronecker 引理

### CLT

$\frac{S_n-n\mu}{\sigma\sqrt{n}}\xRightarrow{d}\mathcal{N}(0,1)$（特征函数法）

---

## 第 4 章：条件期望 ★★

$E[X|\mathcal{G}]$：$\mathcal{G}$-可测且 $\int_A Y = \int_A X, \forall A \in \mathcal{G}$

**$L^2$ 投影视角**：$E[Y|\mathcal{G}]$ = $Y$ 到 $\mathcal{G}$-可测子空间的正交投影

**ML 关联**：回归 = 条件期望的估计。

---

## 第 5 章：鞅 ★★★

### 定义

$E[X_{n+1}|\mathcal{F}_n] = X_n$

### 经典例子

- 对称随机游走 $S_n = \sum X_i$（均值 0）
- Doob 鞅 $X_n = E[Y|\mathcal{F}_n]$
- 似然比 $L_n = \prod q(X_i)/p(X_i)$

### 可选停时 ★

$E[X_\tau] = E[X_0]$（条件下）

→ 对称游走首达 $\pm a$：$E[\tau] = a^2$（用 $S_n^2 - n$ 是鞅）

### 鞅收敛

$L^1$-有界下鞅 → a.s. 收敛

### Doob 分解 + 不等式

$X_n = M_n + A_n$；Doob 极大值不等式；Azuma-Hoeffding

**ML 关联**：
- RL TD 学习（鞅差序列 → 收敛）
- 联机学习 regret bound（Azuma-Hoeffding）
- MCMC 收敛

---

## 集中不等式

| 不等式 | 条件 | 结论 |
|---|---|---|
| Hoeffding ★ | $X_i \in [a_i,b_i]$ | $P(|S_n-ES_n|\geq t)\leq 2e^{-2t^2/\sum(b_i-a_i)^2}$ |
| McDiarmid | Lipschitz $f$ | $P(|f-Ef|\geq t)\leq 2e^{-2t^2/\sum c_i^2}$ |
| Azuma | 鞅差 | $P(|M_n-M_0|\geq t)\leq 2e^{-t^2/(2\sum c_i^2)}$ |

### Hoeffding → 泛化界

$P(|\hat{R}(h)-R(h)|>\epsilon)\leq 2e^{-2n\epsilon^2}$

Union bound：$\epsilon = \sqrt{\frac{\ln(2|\mathcal{H}|/\delta)}{2n}}$ → PAC 泛化界

---

## 频率派 vs 贝叶斯派

- **频率派**：概率 = 长期频率。MLE。参数固定。
- **贝叶斯派**：概率 = 信念。后验分布。参数随机。
- **Williams 视角**：$\sigma$-代数为两种学派提供统一框架。鞅 = "信息逐步揭示下的公平估计"。

---

## Diffusion Model 预览（Part C SDE 基础）★

### Brownian Motion

$W_t$：独立增量、$W_t-W_s \sim \mathcal{N}(0,t-s)$、连续路径

### Itô 引理

$df(W_t) = f'dW_t + \frac{1}{2}f''dt$（多出二阶项！）

### 前向 SDE（加噪）

$dX_t = -\frac{1}{2}\beta_t X_t\,dt + \sqrt{\beta_t}\,dW_t$

### 反向 SDE（生成）

$dX_t = \left[-\frac{1}{2}\beta_t X_t - \beta_t\nabla\log p_t(X_t)\right]dt + \sqrt{\beta_t}\,d\bar{W}_t$

→ Score matching 估计 $\nabla\log p_t$

---

## 🟠 不足层

1. **i.i.d. 假设**：鞅方法可以部分替代，但混合条件更一般
2. **CLT 对重尾失效**：Cauchy / Pareto 方差不存在
3. **Itô 积分非直觉**：$dW^2 = dt$ 让物理直觉失效
4. **条件期望存在性依赖选择公理**（RN 定理）

---

## 🔴 应用层

| 概念 | ML 场景 |
|---|---|
| SLLN | SGD 收敛 |
| CLT | BatchNorm |
| 鞅 + 可选停时 | RL / 期权定价 |
| 条件期望 = 投影 | 回归 |
| Hoeffding/McDiarmid | 泛化界 |
| Brownian + Itô | 扩散模型 SDE |

---

## 与 work4ai 讲透系列的交叉

- **讲透泛化**：集中不等式 + PAC-Bayes
- **讲透 SGD**：SLLN + CLT + 鞅
- **讲透扩散模型**：Brownian + 反向 SDE
- **讲透 RL**：鞅 → TD 学习
