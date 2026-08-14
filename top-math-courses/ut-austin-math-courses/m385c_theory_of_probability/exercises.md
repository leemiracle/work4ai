# UT Austin M 385C · 习题集（Durrett *Probability: Theory and Examples*）

> **难度分级**：🟢 基础（概念核对）/ 🔵 进阶（定理应用 / 计算）/ 🔴 挑战（证明 / Prelim 风格）
> **用法**：先看【提示】自己想，再看【答案】核对。每题标注 ML 关联。对应 Prelim 风格。

---

## 🟢 基础题

### Q1（收敛模式蕴含）画蕴含图并给反例

四种收敛：a.s.、$L^p$、依概率($P$)、依分布($d$)。
(a) 写出全部蕴含关系。
(b) 给出"a.s. 但非 $L^1$"的反例。
(c) 给出"依概率但非 a.s."的反例。

**【提示】** (b) $X_n=n\mathbf{1}_{(0,1/n)}$；(c) 滑动窗口独立事件。

**【答案】**
(a) $a.s.\Rightarrow P\Rightarrow d$；$L^p\Rightarrow P$（$p\geq1$）。即 a.s. 与 $L^p$ 各自蕴含 $P$，但 a.s. 与 $L^p$ **互不蕴含**。

(b) $\Omega=[0,1]$ 均匀测度，$X_n=n\mathbf{1}_{(0,1/n)}$。$X_n\to0$ 点态（故 a.s.），但 $E[X_n]=1$ 不趋于 0（非 $L^1$ 收敛）。原因：无一致可积性。

(c) 令 $A_n$ 为 $[0,1]$ 上长度 $1/n$ 的滑动区间（$A_1=[0,1],A_2=[0,1/2],A_3=[1/2,1],A_4=[0,1/3],\dots$ 依次填满）。$X_n=\mathbf{1}_{A_n}$，$P(|X_n|>\epsilon)=P(A_n)\to0$（依概率→0），但每个点被无穷多个 $A_n$ 覆盖，故 $X_n\not\to0$ a.s.。$\square$

**【ML 关联】** 收敛模式 = SGD 收敛类型分析（a.s. 收敛 vs 均方收敛）。

---

### Q2（Borel-Cantelli）无限猴子

(a) 猴子每秒随机敲一个字母（26 个等概率）。求"无限时间里敲出 *HAMLET* 全文"的概率。
(b) 若有无穷多只猴子各自独立敲，证明几乎必然至少一只敲出 *HAMLET*。

**【提示】** (a) $A_n$=从第 $n$ 位起连续 6 位是 HAMLET，$\sum P(A_n)=\infty$ 但**不独立**；改用独立分组。(b) 第二 Borel-Cantelli。

**【答案】**
(a) 单次敲出 6 字特定序列概率 $p=(1/26)^6\approx 2.9\times10^{-9}$。考虑不重叠的 6 字块（第 $1,7,13,\dots$ 位起），这些事件独立，$\sum P=\infty$。由第二 Borel-Cantelli，无限次发生 a.s.。→ **概率 = 1**（无限时间里几乎必然敲出任意有限文本）。

(b) 每只猴子敲出 HAMLET 概率 = 1（由 (a)）。无穷多只独立 → 至少一只敲出概率 $=1-(1-1)^\infty=1$。（更直接：每只都 a.s. 敲出。）

**【ML 关联】** Borel-Cantelli = "稀有事件在足够多独立尝试下几乎必然发生"——这是大模型采样生成（temperature 采样、best-of-N）的理论基础。

---

## 🔵 进阶题

### Q3（CLT + 特征函数）Gamma 分布的渐近正态

$X_i\stackrel{iid}{\sim}\text{Gamma}(\alpha,\lambda)$（密度 $\frac{\lambda^\alpha x^{\alpha-1}e^{-\lambda x}}{\Gamma(\alpha)}$）。
(a) 用 MGF 求均值方差。
(b) 用 CLT 写出 $S_n=\sum_{i=1}^n X_i$ 的渐近分布。
(c) 用 Berry-Esseen 估计 (b) 的近似误差量级。

**【提示】** Gamma MGF $M(t)=(1-t/\lambda)^{-\alpha}$；$E[X^3]$ 有限。

**【答案】**
(a) $M(t)=(1-t/\lambda)^{-\alpha}$。$M'(0)=\alpha/\lambda$，$M''(0)=\alpha(\alpha+1)/\lambda^2$。故 $E[X]=\alpha/\lambda$，$\text{Var}=\alpha/\lambda^2$。

(b) $E[S_n]=n\alpha/\lambda$，$\text{Var}(S_n)=n\alpha/\lambda^2$。CLT：
$$\frac{S_n-n\alpha/\lambda}{\sqrt{n\alpha}/\lambda}\xRightarrow{d}N(0,1)$$

(c) Berry-Esseen：$\sup|F_n-\Phi|\leq C\,E|X|^3/(\sigma^3\sqrt n)$。Gamma 三阶矩有限，故误差 $=O(1/\sqrt n)$。

**【ML 关联】** Gamma 分布 = 贝叶斯推断中正态精度的共轭先验；CLT 给出后验采样的渐近正态近似（Laplace 近似）。

---

### Q4（鞅 + 可选停时）首达时间

对称随机游走 $S_n=\sum_{i=1}^n X_i$，$X_i=\pm1$ 等概率。$\tau=\inf\{n:|S_n|=a\}$。
(a) 证明 $S_n$ 和 $S_n^2-n$ 都是鞅。
(b) 用可选停时证明 $E[\tau]=a^2$。
(c) 验证可选停时定理的条件成立。

**【提示】** (a) 直接验 $E[S_{n+1}|\mathcal{F}_n]$；(b) 在 $S_n^2-n$ 上用可选停时；(c) $\tau<\infty$ a.s. 且 $E[\tau]<\infty$。

**【答案】**
(a) $E[S_{n+1}|\mathcal{F}_n]=S_n+E[X_{n+1}]=S_n+0=S_n$ ✓。
$E[S_{n+1}^2-(n+1)|\mathcal{F}_n]=S_n^2+2S_nE[X_{n+1}]+E[X_{n+1}^2]-n-1=S_n^2+0+1-n-1=S_n^2-n$ ✓。

(b) $S_n^2-n$ 是鞅，可选停时（条件满足见 (c)）：$E[S_\tau^2-\tau]=E[S_0^2-0]=0$。停时处 $S_\tau^2=a^2$，故 $E[\tau]=a^2$。

(c) 对称游走在有限状态 $\{-a,\dots,a\}$ 上常返，$\tau<\infty$ a.s.；且 $E[\tau]=a^2<\infty$；$|S_n^2-n|$ 在 $\tau$ 前有界于 $a^2$（$|S_n|\leq a$ for $n\leq\tau$），一致可积条件满足。$\square$

**【ML 关联】** 可选停时 = RL 中 TD 学习收敛性的工具（TD 误差在真值处是鞅差，$E[\text{TD error}]=0$）；也用于期权定价（首达障碍期权）。

---

### Q5（Hoeffding → PAC 界）所需样本数

有限假设类 $\|\mathcal H\|=10^6$，0-1 损失。要使**所有**假设 $h\in\mathcal H$ 同时满足 $|\hat R(h)-R(h)|\leq 0.05$（概率 $\geq 95\%$），至少需多少样本 $n$？

**【提示】** Union bound + Hoeffding，令 $2\|\mathcal H\|e^{-2n\epsilon^2}=\delta=0.05$。

**【答案】**
$$2|\mathcal H|e^{-2n\epsilon^2}\leq\delta\Rightarrow n\geq\frac{\ln(2|\mathcal H|/\delta)}{2\epsilon^2}=\frac{\ln(2\times10^6/0.05)}{2\times0.05^2}$$
$$\ln(4\times10^7)\approx 17.5\Rightarrow n\geq\frac{17.5}{0.005}=3500$$

→ 约 **3500** 样本。

**【ML 关联】** 这就是 PAC 学习的样本复杂度。注意 $n\propto\ln|\mathcal H|$（对假设类大小对数依赖），这是有限类可学习的核心。

---

## 🔴 挑战题（Prelim 风格）

### Q6（Doob 鞅 + Azuma）联机学习 regret

联机学习：每轮 $t$，算法（基于历史 $\mathcal{F}_{t-1}$）选 $a_t$，对手选损失 $\ell_t(a_t)\in[0,1]$。定义 regret $R_T=\sum_{t=1}^T\ell_t(a_t)-\min_a\sum_t\ell_t(a)$。
用 Doob 鞅 + Azuma 证明：对固定最优动作 $a^*$，$\sum_t\ell_t(a_t)-\sum_t\ell_t(a^*)=O(\sqrt T)$（高概率）。

**【提示】** 令 $D_t=E[\ell_t(a_t)-\ell_t(a^*)|\mathcal{F}_{t-1}]$，构造鞅差 $M_t=(\ell_t(a_t)-\ell_t(a^*))-D_t$，用 Azuma。

**【答案】**
$M_t=\ell_t(a_t)-\ell_t(a^*)-D_t$，其中 $D_t=E[\ell_t(a_t)-\ell_t(a^*)|\mathcal{F}_{t-1}]$。则 $E[M_t|\mathcal{F}_{t-1}]=0$，$\{M_t\}$ 是鞅差序列，$|M_t|\leq 1$（损失 $\in[0,1]$）。

$S_T=\sum_{t=1}^T M_t=\sum_t(\ell_t(a_t)-\ell_t(a^*))-\sum_t D_t$ 是鞅。Azuma：
$$P(|S_T|\geq u)\leq 2e^{-u^2/(2T)}$$

若算法保证 $\sum_t D_t\leq C$（如 Follow-the-Regularized-Leader 给 $D_T=O(\sqrt T)$），则 $\sum_t\ell_t(a_t)-\sum_t\ell_t(a^*)=S_T+\sum_tD_t\leq O(\sqrt T)+u$。取 $u=O(\sqrt T)$（高概率），总 regret $=O(\sqrt T)$。$\square$

**【ML 关联】** $O(\sqrt T)$ regret = 联机学习 / 多臂老虎机的最优速率；鞅 + Azuma 是推导的核心工具。

---

### Q7（Itô 引理）二次变差

(a) 用 Itô 引理证明 $(dW_t)^2=dt$（形式上），即对 $f(x)=x^2$，$d(W_t^2)=2W_t\,dW_t+dt$。
(b) 证明 $\int_0^t W_s\,dW_s=\frac{1}{2}W_t^2-\frac{1}{2}t$。
(c) 解释为什么 Itô 积分多出 $-\frac12 t$（对比 Riemann 积分 $\int_0^t x\,dx=\frac12 t^2$）。

**【提示】** (a) Itô 引理 $df(W_t)=f'dW+\frac12f''dt$；(b) 整理 (a)；(c) $W_t$ 的二次变差非零。

**【答案】**
(a) $f(x)=x^2$，$f'=2x,f''=2$。Itô 引理：
$$d(W_t^2)=2W_t\,dW_t+\frac{1}{2}\cdot2\,dt=2W_t\,dW_t+dt$$
形式上 $(dW_t)^2=dt$（因为多出的 $dt$ 项来自 $f''/2$）。

(b) 积分 (a)：$W_t^2=\int_0^t2W_s\,dW_s+t$，故
$$\int_0^t W_s\,dW_s=\frac{1}{2}W_t^2-\frac{1}{2}t$$

(c) Riemann 积分 $\int_0^t x\,dx=\frac12 t^2$（无修正项）。但 $W_t$ 的**二次变差** $\langle W\rangle_t=t\neq0$，路径"抖动太剧烈"，导致 Itô 积分必须用中点（不可预测）规则，多出 $-\frac12t$ 修正。这是 Itô vs Stratonovich 的本质区别。

**【ML 关联】** 扩散模型反向 SDE 的推导依赖 Itô 引理；DDPM（Ho et al., arXiv:2006.11239 ✅）的反向过程 $dx=[\dots]dt+\sqrt{\beta_t}d\bar W_t$ 多出的漂移项 $-\beta_t\nabla\log p_t$ 正来自 Itô 框架。

---

## 速查：本习题覆盖的知识地图

| 题 | 章节 | 核心概念 | ML 出口 |
|---|---|---|---|
| Q1 | 第 2 章 | 收敛模式 + 反例 | SGD 收敛类型 |
| Q2 | 第 3 章 | Borel-Cantelli | 采样生成（best-of-N）|
| Q3 | 第 4 章 | CLT + Berry-Esseen | Laplace 近似 |
| Q4 | 第 6 章 | 鞅 + 可选停时 | RL TD 学习 / 期权 |
| Q5 | 集中不等式 | Hoeffding → PAC | 样本复杂度 |
| Q6 | 第 6 章 + Azuma | Doob 鞅 → regret | 联机学习 |
| Q7 | 第 7 章 | Itô 引理 | 扩散模型 SDE |
