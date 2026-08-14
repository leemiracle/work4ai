# UC Berkeley MATH 218 · 概率论笔记（Durrett + Peres 学派视角）

> **教材**：Durrett, *Probability: Theory and Examples*；补充 Peres 讲义
> **一手核实**：Berkeley Math 218 课程大纲 + Durrett 5th ed
> **特色**：研究生测度论概率，强调集中不等式 + Brownian motion + 随机过程

---

## 费曼三层讲透

### 🟢 直觉层

- **概率 = 不确定性的度量**：σ-代数 $\mathcal{F}$ = "你能观测到的事件集合"，更大的 $\mathcal{F}$ = 更多信息
- **鞅 = 公平赌博**：你的期望财富永远等于当前财富——$E[X_{n+1}|\mathcal{F}_n] = X_n$
- **Brownian motion = 连续的随机游走**：每个瞬间都在随机抖动，路径处处连续但处处不可导
- **集中不等式 = "好事情不太可能太离谱"**：随机变量偏离期望的概率指数衰减

---

### 🔵 数学层

## 核心框架

```
测度论 → 概率空间 → 收敛模式 → LLN/CLT → 鞅 → Brownian → 随机过程
──────   ────────   ────────   ─────────   ──   ────────   ─────────
σ-代数    (Ω,F,P)    a.s./P/d    SLLN       停时    W_t        Markov
Lebesgue  独立性      Lp          CLT        可选停时  反射原理    遍历定理
积分      条件期望    Berry-Esseen  特征函数  鞅收敛   Ito积分     混合时间
```

---

## 第 1 章：概率空间与收敛模式 ★★★

### 1.1 概率空间

$(\Omega, \mathcal{F}, P)$：样本空间 + σ-代数 + 概率测度。

**滤波** $\mathcal{F}_0 \subseteq \mathcal{F}_1 \subseteq \cdots$：信息逐步揭示。$\mathcal{F}_n$ = "到时刻 $n$ 你知道的信息"。

### 1.2 四种收敛模式 ★★★

| 模式 | 定义 | ML 含义 |
|---|---|---|
| **a.s.** $X_n \xrightarrow{a.s.} X$ | $P(X_n \to X) = 1$ | SGD 确定性收敛 |
| **$L^p$** $X_n \xrightarrow{L^p} X$ | $E|X_n-X|^p \to 0$ | 均方收敛 |
| **依概率** $X_n \xrightarrow{P} X$ | $P(|X_n-X|>\epsilon) \to 0$ | 弱收敛保证 |
| **依分布** $X_n \xRightarrow{d} X$ | $F_n \to F$ 连续点 | CLT（渐近分布） |

**蕴含**：$a.s. \Rightarrow P \Rightarrow d$；$L^p \Rightarrow P$。

### 1.3 LLN + CLT

**SLLN**：$\frac{S_n}{n} \xrightarrow{a.s.} \mu$ → SGD 梯度收敛的理论根基

**CLT**：$\frac{S_n - n\mu}{\sigma\sqrt{n}} \xRightarrow{d} \mathcal{N}(0,1)$ → 梯度噪声正态化

**Berry-Esseen**：$\sup|F_n - \Phi| \leq C/\sqrt{n}$ → CLT 近似误差

---

## 第 2 章：集中不等式（Berkeley 学派核心）★★★

| 不等式 | 条件 | 结论 | ML 用途 |
|---|---|---|---|
| **Markov** | $X \geq 0$ | $P(X \geq a) \leq E[X]/a$ | 基础工具 |
| **Chebyshev** | — | $P(|X-\mu| \geq a) \leq \sigma^2/a^2$ | 弱界 |
| **Chernoff** | 独立 | $P(S_n \geq (1+\delta)\mu) \leq e^{-\mu\delta^2/3}$ | 强界 |
| **Hoeffding** ★ | $X_i \in [a_i,b_i]$ | $P(|S_n-ES_n| \geq t) \leq 2e^{-2t^2/\sum(b_i-a_i)^2}$ | **泛化界核心** |
| **Bernstein** | 亚高斯 | $P(|S_n| \geq t) \leq 2\exp\left(-\frac{t^2}{2(\sigma^2+Mt/3)}\right)$ | 重尾界 |
| **McDiarmid** ★ | Lipschitz $f$ | $P(|f-Ef| \geq t) \leq 2e^{-2t^2/\sum c_i^2}$ | **算法稳定性** |
| **Azuma** | 鞅差 $|D_i|\leq c_i$ | $P(|M_n-M_0| \geq t) \leq 2e^{-t^2/(2\sum c_i^2)}$ | **联机学习** |

### Hoeffding → 泛化界推导 ★

$X_i \in [0,1]$（0-1 损失），$\hat{R}(h) = \frac{1}{n}\sum\ell(h, x_i)$：

$$P(|\hat{R}(h) - R(h)| > \epsilon) \leq 2e^{-2n\epsilon^2}$$

Union bound over $|\mathcal{H}|$ 个假设：

$$P(\exists h: |\hat{R}-R| > \epsilon) \leq 2|\mathcal{H}|e^{-2n\epsilon^2}$$

令 $= \delta$：$\epsilon = \sqrt{\frac{\ln(2|\mathcal{H}|/\delta)}{2n}}$ → PAC 泛化界。

### McDiarmid → 算法稳定性 ★

如果算法 $A$ 对单个训练样本的改动 Lipschitz（改变一个样本最多改变输出 $c_i$），则泛化好。

**ML 关联**：这解释了为什么"稳定的算法泛化好"——SGD 的随机性实际上提供了隐式正则化。

---

## 第 3 章：鞅论 ★★★

### 3.1 定义

$E[X_{n+1}|\mathcal{F}_n] = X_n$（公平赌博）

### 3.2 可选停时 ★

$E[X_\tau] = E[X_0]$（条件：$\tau$ 有界或一致可积）

**应用**：对称随机游走首达 $\pm a$ 时间 $E[\tau] = a^2$（用 $S_n^2 - n$ 也是鞅）

### 3.3 鞅收敛定理

$L^1$-有界下鞅 $\Rightarrow$ a.s. 收敛

### 3.4 Doob 分解

$X_n = M_n + A_n$（鞅 + 可料增序列）

**ML 关联**：SGD 中梯度噪声是鞅差 → Azuma-Hoeffding → 收敛速率分析。

---

## 第 4 章：Brownian Motion ★★

### 定义

$W_t$ 满足：
1. $W_0 = 0$
2. 增量独立：$W_t - W_s \perp W_s$（$s < t$）
3. 增量正态：$W_t - W_s \sim \mathcal{N}(0, t-s)$
4. 路径连续

### 关键性质

- **自相似**：$W_{at} \stackrel{d}{=} \sqrt{a}\,W_t$
- **反射原理**：$P(\max_{s\leq t} W_s \geq a) = 2P(W_t \geq a)$
- **不可导**：$W_t$ 处处连续但处处不可导（Hölder $< 1/2$）

### Itô 积分入门

$$\int_0^t f(W_s)\,dW_s \neq \text{Riemann积分}$$

**Itô 引理**（随机微积分的链式法则）：

$$df(W_t) = f'(W_t)\,dW_t + \frac{1}{2}f''(W_t)\,dt$$

多出 $\frac{1}{2}f''dt$ 项！这是因为 $dW_t^2 = dt$（非零）。

**ML 关联**：扩散模型 = 反向 Itô SDE。Score matching = 估计 SDE 的漂移项。

---

## 第 5 章：Markov 链与混合时间

### 遍历定理

不可约 + 非周期 + 正常返 → $\frac{1}{n}\sum f(X_k) \xrightarrow{a.s.} E_\pi[f]$

### 混合时间

$$t_{\text{mix}}(\epsilon) = \min\{t : \max_x \|P^t(x,\cdot) - \pi\|_{\text{TV}} \leq \epsilon\}$$

**ML 关联**：MCMC 采样效率 = 混合时间。Langevin Monte Carlo 的混合时间 $\propto d$（维度）。

---

## Diffusion Model 的 SDE 基础 ★★★

### 前向 SDE（加噪）

$$dX_t = -\frac{1}{2}\beta(t)X_t\,dt + \sqrt{\beta(t)}\,dW_t$$

边际分布：$X_t | X_0 \sim \mathcal{N}(\sqrt{\bar\alpha_t}X_0, (1-\bar\alpha_t)I)$

### 反向 SDE（去噪 / 生成）

Anderson (1982) 的反向 SDE：

$$dX_t = \left[-\frac{1}{2}\beta(t)X_t - \beta(t)\nabla\log p_t(X_t)\right]dt + \sqrt{\beta(t)}\,d\bar{W}_t$$

关键：反向 SDE 需要 **score function** $\nabla\log p_t(x)$

### Score Matching

训练神经网络 $s_\theta(x,t) \approx \nabla\log p_t(x)$：

$$\mathcal{L} = E_{t,x_0,\epsilon}\left[\|s_\theta(\sqrt{\bar\alpha_t}x_0 + \sqrt{1-\bar\alpha_t}\epsilon, t) + \frac{\epsilon}{\sqrt{1-\bar\alpha_t}}\|^2\right]$$

**ML 关联**：这就是 DDPM（Ho et al., arXiv:2006.11239 ✅）的噪声预测目标。

---

## 🟠 不足层（局限性）

1. **i.i.d. 假设**：集中不等式通常需要独立性。时间序列 / 图数据需要鞅方法或混合条件替代。

2. **高维灾难**：高维空间中集中不等式的常数可能很大。$O(\sqrt{d/n})$ 的界在高维下很松。

3. **Brownian 运动的理想化**：真实噪声不一定是高斯的。重尾噪声（如 Cauchy）需要 Lévy 过程替代。

4. **Itô 积分的非直觉性**：$dW_t^2 = dt$ 导致 Itô 引理多出二阶项，让物理直觉失效。Stratonovich 积分更物理但不那么数学方便。

---

## 🔴 应用层（ML 公式级对应）

| 概念 | 公式 | ML 场景 |
|---|---|---|
| SLLN | $\frac{S_n}{n}\xrightarrow{a.s.}\mu$ | SGD 收敛 |
| Hoeffding | $P(\|\hat{R}-R\|>\epsilon)\leq 2e^{-2n\epsilon^2}$ | 泛化界 |
| Azuma | $P(\|M_n-M_0\|\geq t)\leq 2e^{-t^2/(2\sum c_i^2)}$ | 联机学习 regret |
| 鞅 + 可选停时 | $E[X_\tau]=E[X_0]$ | RL TD 学习 |
| Brownian + Itô | $df = f'dW + \frac{1}{2}f''dt$ | 扩散模型 SDE |
| Markov 遍历 | $\frac{1}{n}\sum f(X_k)\to E_\pi[f]$ | MCMC |

---

## 与 work4ai 讲透系列的交叉

- **讲透泛化**：集中不等式 + PAC-Bayes
- **讲透 SGD**：SLLN + CLT + 鞅方法
- **讲透扩散模型**：Brownian + 反向 SDE + score matching
- **讲透强化学习**：鞅 → TD，Markov 链 → MDP
