# Princeton MAT 514 · 概率论笔记（Durrett + Radon-Nikodym → 信息论桥梁）

> **教材**：Durrett, *Probability: Theory and Examples*；Billingsley, *Probability and Measure*
> **一手核实**：Princeton MAT 514 课程大纲
> **特色**：测度论概率，强调 Radon-Nikodym 导数 → 为 MAT 575 信息论打基础

---

## 费曼三层讲透

### 🟢 直觉层

- **概率 = 不确定性的度量**，但频率派和贝叶斯派对"概率是什么"有根本分歧
- **Radon-Nikodym 导数 $dP/dQ$** = "测度 $P$ 相对于 $Q$ 的密度"——KL 散度 $\text{KL}(P\|Q) = \int\log\frac{dP}{dQ}\,dP$ 的基础
- **鞅 = 公平赌博**：$E[X_{n+1}|\mathcal{F}_n] = X_n$ → RL 理论基础

---

### 🔵 数学层

## 第 1 章：测度论基础 + 概率空间

### σ-代数

$\mathcal{F}$：对补集和可数并封闭。$\mathcal{F}$ = "可观测事件集"。

### 概率空间

$(\Omega, \mathcal{F}, P)$。滤波 $\mathcal{F}_n \uparrow$ = 信息流。

### Lebesgue 积分 + 三大定理

MCT（单调收敛）、DCT（控制收敛）、Fatou 引理。

### Radon-Nikodym 定理 ★★

> 若 $P \ll Q$（$Q(A)=0 \Rightarrow P(A)=0$，绝对连续），则存在 $dP/dQ$ 使得
> $$P(A) = \int_A \frac{dP}{dQ}\,dQ$$

**KL 散度的测度论定义**：

$$\text{KL}(P\|Q) = \int \log\frac{dP}{dQ}\,dP = E_P\left[\log\frac{dP}{dQ}\right]$$

**ML 关联**：这是 VAE / diffusion / RLHF 中 KL 项的严格定义基础。

---

## 第 2 章：收敛模式 ★★★

| 模式 | 定义 | ML 关联 |
|---|---|---|
| a.s. | $P(X_n\to X)=1$ | SGD 确定性收敛 |
| $L^p$ | $E|X_n-X|^p\to 0$ | 均方收敛 |
| 依概率 | $P(|X_n-X|>\epsilon)\to 0$ | 弱收敛保证 |
| 依分布 | $F_n\to F$ 连续点 | CLT |

蕴含：$a.s. \Rightarrow P \Rightarrow d$；$L^p \Rightarrow P$。

---

## 第 3 章：LLN + CLT ★★

**SLLN**：$\frac{S_n}{n}\xrightarrow{a.s.}\mu$ → SGD 梯度收敛

**CLT**：$\frac{S_n-n\mu}{\sigma\sqrt{n}}\xRightarrow{d}\mathcal{N}(0,1)$ → 梯度噪声正态化

**Berry-Esseen**：$\sup|F_n-\Phi|\leq C/\sqrt{n}$ → CLT 收敛速度

---

## 第 4 章：条件期望 ★★

$E[X|\mathcal{G}]$ = $\mathcal{G}$-可测的最佳 $L^2$ 逼近（正交投影）

**塔性质**：$E[E[X|\mathcal{G}]] = E[X]$

**ML 关联**：回归 = 条件期望估计；贝叶斯后验 = 条件分布。

---

## 第 5 章：鞅 ★★★

### 定义

$E[X_{n+1}|\mathcal{F}_n] = X_n$

### 可选停时

$E[X_\tau]=E[X_0]$（条件下）→ 对称游走 $E[\tau]=a^2$

### 鞅收敛

$L^1$-有界下鞅 → a.s. 收敛

### 应用

- RL TD 学习（鞅差序列）
- 联机学习 regret bound（Azuma-Hoeffding）
- MCMC 收敛

---

## KL 散度：概率论 → 信息论的桥梁 ★★★

### 测度论定义

$$\text{KL}(P\|Q) = \int\log\frac{dP}{dQ}\,dP$$

### 离散情况

$$\text{KL}(p\|q) = \sum_x p(x)\log\frac{p(x)}{q(x)}$$

### 性质

1. $\text{KL}(P\|Q) \geq 0$（Gibbs 不等式，用 Jensen 证明）
2. $\text{KL}(P\|Q) = 0 \iff P = Q$
3. 非对称：$\text{KL}(P\|Q) \neq \text{KL}(Q\|P)$

### Cross-entropy 分解

$$H(p,q) = H(p) + \text{KL}(p\|q)$$

→ 分类 loss 的信息论本质

### Pinsker 不等式

$$\text{TV}(P,Q) \leq \sqrt{\text{KL}(P\|Q)/2}$$

→ 连接信息论（KL）与概率论（全变差）→ PAC-Bayes 泛化界

---

## ML 中的 KL 散度应用

| 应用 | KL 表达式 |
|---|---|
| **VAE ELBO** | $\text{ELBO} = E_q[\log p(x\|z)] - \text{KL}(q(z\|x)\|p(z))$ |
| **Diffusion** | $\sum_t \text{KL}(q(x_{t-1}\|x_t,x_0)\|p_\theta(x_{t-1}\|x_t))$ |
| **RLHF** | $\max E[r] - \beta\text{KL}(\pi_\theta\|\pi_{\text{ref}})$ |
| **DPO** | $\log\frac{\pi_\theta(y_w)}{\pi_{\text{ref}}(y_w)} - \log\frac{\pi_\theta(y_l)}{\pi_{\text{ref}}(y_l)}$（隐式 KL） |
| **Cross-entropy** | $-\sum p\log q = H(p) + \text{KL}(p\|q)$ |

---

## 频率派 vs 贝叶斯派

- **频率派**：概率 = 长期频率。MLE。参数固定。
- **贝叶斯派**：概率 = 信念。后验。参数随机。
- **MAT 514 视角**：Radon-Nikodym 导数为两种学派提供统一的测度论框架——后验 $P(\theta|D)$ 对先验 $P(\theta)$ 的 RN 导数 = 似然比。

---

## 🟠 不足层

1. **Radon-Nikodym 需要绝对连续**：$P \ll Q$ 不满足时 KL 无定义（无穷大）
2. **i.i.d. 假设**：现实数据有依赖性
3. **CLT 对重尾失效**：Cauchy 方差不存在
4. **条件期望存在性依赖选择公理**：严格定义需要 RN 定理

---

## 🔴 应用层

| 概念 | ML 场景 |
|---|---|
| SLLN | SGD 收敛 |
| CLT | BatchNorm |
| KL 散度 (RN 导数) | VAE / diffusion / RLHF / DPO |
| Cross-entropy = H + KL | 分类 loss |
| Pinsker 不等式 | PAC-Bayes 泛化界 |
| 鞅 + 可选停时 | RL / 期权定价 |

---

## 与 work4ai 讲透系列的交叉

- **讲透 VAE**：KL + ELBO + Radon-Nikodym
- **讲透 RLHF/DPO**：KL 正则化
- **讲透泛化**：PAC-Bayes + Pinsker
- **讲透 SGD**：SLLN + CLT
