# UT Austin M 362K · 概率 I 章节笔记（Ross *A First Course in Probability*）

> **教材**：Ross, *A First Course in Probability*（Pitman *Probability* 为备选）
> **一手核实**：UT Austin M 362K 课程描述 + Ross 教材目录
> **定位**：本科应用概率（**无测度论，计算与建模导向**）；从计数到 CLT 的标准本科序列

---

## 费曼三层讲透

### 🟢 直觉层

- **概率 = 不确定性的度量**：抛硬币前不知道结果，但知道"长期频率趋于 0.5"。概率就是把这种"不确定性"变成可计算的数。
- **条件概率 = 信息更新**：知道"今天阴天"后，"明天下雨"的概率变了。$P(B|A)$ = 看到 $A$ 后对 $B$ 的修正信念。
- **Bayes = 反向推理**：医生看到检测阳性，要反推"真患病"概率。先验 + 似然 → 后验。
- **期望 = 长期平均**：赌场长期稳赚，因为期望收益为负（对你）。
- **方差 = 波动**：投资收益的方差越大，风险越高。CLT 告诉我们：很多独立小波动加起来，总波动近似正态。
- **Markov 链 = 只有"现在"决定"未来"**：明天的天气只依赖今天，不依赖昨天（无记忆性）。

**反例（警惕）**：
- 平均收入高不代表大多数人都高（**重尾分布**：少数富豪拉高均值）。→ 这正是 CLT 对重尾失效的直觉。
- "相关不等于因果"：冰淇淋销量和溺水率正相关，但不是因果（混淆变量 = 气温）。

---

### 🔵 数学层

## 核心框架

```
计数 → 概率公理 → 条件概率/Bayes → 随机变量 → 联合分布 → 期望/方差 → LLN/CLT → Markov 链
────   ─────────   ──────────────   ────────   ────────   ─────────   ────────   ─────────
排列   (Ω,F,P)     P(B|A)            离散/连续   协方差/相关   母函数       大数定律    平稳分布
组合   独立事件     全概率公式         分布函数     独立性        特征函数     中心极限    遍历入门
```

---

## 第 1 章：组合计数（Combinatorics）

### 1.1 计数基本法则

若任务 $A$ 有 $m$ 种做法，任务 $B$ 有 $n$ 种做法，则"先 $A$ 后 $B$"有 $m\times n$ 种。

### 1.2 排列与组合

- **排列**（有序）：$P(n,k)=\dfrac{n!}{(n-k)!}$
- **组合**（无序）：$\dbinom{n}{k}=\dfrac{n!}{k!(n-k)!}$

### 1.3 多项式系数

把 $n$ 个物品分成 $n_1,n_2,\dots,n_r$ 组：$\dbinom{n}{n_1,\dots,n_r}=\dfrac{n!}{n_1!\cdots n_r!}$

**ML 关联**：多项式系数 = 多项分布（文本分类的似然）；组合 = 二项分布的基础。

---

## 第 2 章：概率公理与性质 ★

### 2.1 概率空间（本科版）

样本空间 $\Omega$（所有可能结果），事件 $A\subseteq\Omega$，概率 $P$ 满足**三条公理**（Kolmogorov）：
1. **非负**：$P(A)\geq 0$
2. **归一**：$P(\Omega)=1$
3. **可数可加**：$A_i$ 互不相交 $\Rightarrow P(\bigcup A_i)=\sum P(A_i)$

### 2.2 基本性质

- $P(A^c)=1-P(A)$
- $A\subseteq B\Rightarrow P(A)\leq P(B)$
- **容斥**：$P(A\cup B)=P(A)+P(B)-P(AB)$

### 2.3 独立性

$A,B$ 独立 $\Leftrightarrow P(AB)=P(A)P(B)$。

**ML 关联**：朴素贝叶斯假设特征条件独立——$P(x_1,\dots,x_n|y)=\prod_i P(x_i|y)$，把指数级似然降到线性。

---

## 第 3 章：条件概率与 Bayes ★★

### 3.1 条件概率

$$P(B|A)=\frac{P(AB)}{P(A)}\quad(P(A)>0)$$

### 3.2 全概率公式（Law of Total Probability）

若 $B_i$ 划分 $\Omega$：

$$P(A)=\sum_i P(A|B_i)P(B_i)$$

### 3.3 Bayes 定理 ★★★

$$P(B_j|A)=\frac{P(A|B_j)P(B_j)}{\sum_i P(A|B_i)P(B_i)}$$

**术语**：
- $P(B_j)$ = **先验**（看到数据前的信念）
- $P(A|B_j)$ = **似然**（数据对假设的支持度）
- $P(B_j|A)$ = **后验**（看到数据后的修正信念）

**ML 关联**：
- **朴素贝叶斯分类器**：$y^*=\arg\max_y P(y)\prod_i P(x_i|y)$
- **贝叶斯推断**：后验 $\propto$ 似然 $\times$ 先验，这是变分推断 / MCMC 的全部出发点
- **生成模型**（VAE / diffusion）：建模 $P(x|z)$（似然）+ $P(z)$（先验）

### 3.4 先验对后验的影响（反例）

罕见病（患病率 $10^{-3}$），检测灵敏度 99%、特异度 99%：

$$P(\text{病}|+)=\frac{0.99\times 10^{-3}}{0.99\times 10^{-3}+0.01\times 0.999}\approx 9\%$$

→ 阳性不等于患病！低先验让后验远低于直觉。这是**基础率忽视（base-rate neglect）**。

---

## 第 4 章：随机变量（离散）★

### 4.1 定义与分布

随机变量 $X:\Omega\to\mathbb{R}$。离散型：PMF $p(x)=P(X=x)$。

### 4.2 重要离散分布

| 分布 | PMF | 期望 | 方差 | ML 场景 |
|---|---|---|---|---|
| **Bernoulli($p$)** | $p^x(1-p)^{1-x}$ | $p$ | $p(1-p)$ | 二分类（logistic 回归标签）|
| **Binomial($n,p$)** | $\binom{n}{x}p^x(1-p)^{n-x}$ | $np$ | $np(1-p)$ | $n$ 次伯努利试验 |
| **Geometric($p$)** | $(1-p)^{x-1}p$ | $1/p$ | $(1-p)/p^2$ | 首次成功等待时间 |
| **Poisson($\lambda$)** | $e^{-\lambda}\lambda^x/x!$ | $\lambda$ | $\lambda$ | 稀有事件计数（文本词频）|
| **NegBinom($r,p$)** | $\binom{x-1}{r-1}p^r(1-p)^{x-r}$ | $r/p$ | $r(1-p)/p^2$ | 第 $r$ 次成功等待 |

**Poisson 近似**：$n$ 大 $p$ 小，$\lambda=np$ 时 Binomial $\approx$ Poisson。

---

## 第 5 章：随机变量（连续）★

### 5.1 PDF 与 CDF

$F(x)=P(X\leq x)$，$f(x)=F'(x)$，$P(a\leq X\leq b)=\int_a^b f(x)dx$。

### 5.2 重要连续分布

| 分布 | PDF | 期望 | 方差 | ML 场景 |
|---|---|---|---|---|
| **Uniform($a,b$)** | $1/(b-a)$ | $(a+b)/2$ | $(b-a)^2/12$ | 初始化 / 随机搜索 |
| **Normal($\mu,\sigma^2$)** | $\frac{1}{\sqrt{2\pi}\sigma}e^{-(x-\mu)^2/2\sigma^2}$ | $\mu$ | $\sigma^2$ | 噪声 / 初始化 / BatchNorm |
| **Exponential($\lambda$)** | $\lambda e^{-\lambda x}$ | $1/\lambda$ | $1/\lambda^2$ | 等待时间 / 无记忆性 |
| **Gamma($\alpha,\lambda$)** | $\frac{\lambda^\alpha x^{\alpha-1}e^{-\lambda x}}{\Gamma(\alpha)}$ | $\alpha/\lambda$ | $\alpha/\lambda^2$ | 正态精度先验（贝叶斯）|

### 5.3 正态分布的特殊地位

- 独立正态的和仍正态：$X\sim N(\mu_1,\sigma_1^2)$, $Y\sim N(\mu_2,\sigma_2^2)$ 独立 $\Rightarrow X+Y\sim N(\mu_1+\mu_2,\sigma_1^2+\sigma^2_2)$
- 标准化：$Z=(X-\mu)/\sigma\sim N(0,1)$
- **ML 关联**：扩散模型前向加噪 = 正态叠加；权重初始化（He / Xavier）用正态。

### 5.4 随机变量的函数

$Y=g(X)$ 的分布：$f_Y(y)=f_X(g^{-1}(y))\left|\frac{d}{dy}g^{-1}(y)\right|$（单调 $g$）。

---

## 第 6 章：联合分布 ★

### 6.1 联合 / 边缘 / 条件

- 联合：$f(x,y)$
- 边缘：$f_X(x)=\int f(x,y)dy$
- 条件：$f(x|y)=f(x,y)/f_Y(y)$

### 6.2 协方差与相关

$$\text{Cov}(X,Y)=E[(X-\mu_X)(Y-\mu_Y)]=E[XY]-E[X]E[Y]$$

$$\rho(X,Y)=\frac{\text{Cov}(X,Y)}{\sigma_X\sigma_Y}\in[-1,1]$$

**注意**：$\rho=0$（不相关）**不**蕴含独立（除非联合正态）。

### 6.3 独立 vs 不相关（反例）

$X\sim N(0,1)$, $Y=X^2$。则 $\text{Cov}(X,Y)=E[X^3]-E[X]E[X^2]=0$（不相关），但 $Y$ 完全由 $X$ 决定（**强依赖**）。→ "不相关"远弱于"独立"。

---

## 第 7 章：期望与方差 ★

### 7.1 期望的性质

- 线性：$E[aX+bY]=aE[X]+bE[Y]$（**不需要独立**）
- 独立乘积：$E[XY]=E[X]E[Y]$（需独立）
- **Jensen 不等式**：$\varphi$ 凸 $\Rightarrow E[\varphi(X)]\geq \varphi(E[X])$

**ML 关联**：交叉熵 = $H(p)+\text{KL}(p\|q)\geq H(p)$（Jensen 的特例）；EM 算法用 Jensen 推导 ELBO。

### 7.2 方差的性质

- $\text{Var}(aX+b)=a^2\text{Var}(X)$
- 独立和：$\text{Var}(X+Y)=\text{Var}(X)+\text{Var}(Y)$
- **$\text{Var}(X)=E[X^2]-(E[X])^2$**

### 7.3 矩与矩母函数

- $k$ 阶矩：$E[X^k]$
- **矩母函数 MGF**：$M_X(t)=E[e^{tX}]$
- $E[X^k]=M_X^{(k)}(0)$
- 独立和的 MGF 相乘：$M_{X+Y}(t)=M_X(t)M_Y(t)$

**ML 关联**：MGF 是 Chernoff / Hoeffding 集中不等式的推导工具（研究生 385C 的起点）。

---

## 第 8 章：极限定理 LLN & CLT ★★★

### 8.1 大数定律（LLN）

设 $X_1,\dots,X_n$ i.i.d.，$E[X_i]=\mu$，$S_n=\sum X_i$：

> **弱大数（WLLN）**：$\dfrac{S_n}{n}\xrightarrow{P}\mu$
> **强大数（SLLN）**：$\dfrac{S_n}{n}\xrightarrow{a.s.}\mu$

**ML 关联**：SGD 收敛的理论根基——"小批量梯度的平均收敛到真实梯度"。

### 8.2 中心极限定理（CLT）★★★

$X_i$ i.i.d.，$E[X_i]=\mu$，$\text{Var}=\sigma^2\in(0,\infty)$：

$$\frac{S_n-n\mu}{\sigma\sqrt{n}}\xrightarrow{d}N(0,1)$$

即 $\bar{X}_n\approx N(\mu,\sigma^2/n)$（$n$ 大时）。

**ML 关联**：
- mini-batch 梯度噪声近似正态 $\Rightarrow$ BatchNorm 归一化抑制方差
- 参数估计的渐近正态性（MLE 渐近正态）
- 权重初始化（He / Xavier 控制激活方差）

### 8.3 CLT 的失效（重尾）⚠️

若 $X$ 服从 Cauchy 分布（方差不存在），CLT **失效**——样本均值 $\bar{X}_n$ 与单个 $X_1$ 同分布（不收敛）。

→ 工程教训：长尾数据（金融收益、网络流量）不能盲目套用 CLT；需用稳定分布或重尾理论。

---

## 第 9 章：Markov 链入门 ★

### 9.1 定义

$\{X_n\}$ 满足 **Markov 性**（无记忆性）：

$$P(X_{n+1}=j|X_n=i,X_{n-1},\dots,X_0)=P(X_{n+1}=j|X_n=i)=P_{ij}$$

只有"现在"决定"未来"。

### 9.2 平稳分布

$\pi$ 满足 $\pi=\pi P$（$\pi$ 是 $P$ 特征值 1 的左特征向量）。

### 9.3 遍历定理

不可约 + 非周期 + 正常返 $\Rightarrow$ $\dfrac{1}{n}\sum_{k=1}^n f(X_k)\to E_\pi[f]$（时间平均 = 空间平均）。

**ML 关联**：
- **MCMC**（Metropolis-Hastings）：构造 Markov 链使其平稳分布 = 目标后验，从而采样
- **PageRank**：网页排名 = 转移矩阵的最大特征向量（平稳分布）
- **强化学习**：MDP = 带 reward 的 Markov 链

---

## 🟠 不足层（局限性）

1. **i.i.d. 假设**：LLN/CLT 都需要独立同分布。时间序列、图数据、对抗样本违反 i.i.d. → 泛化失效。
2. **CLT 对重尾失效**：Cauchy / Pareto（方差无穷）→ 样本均值不收敛。金融、网络的极端事件需重尾理论。
3. **频率派 vs 贝叶斯派之争**：
   - 频率派：概率 = 长期频率；MLE；参数固定。（M 362K 默认视角）
   - 贝叶斯派：概率 = 信念；后验分布；参数随机。（Bayes 定理为两者桥梁）
   - 争议：先验的主观性 vs 长期频率的 i.i.d. 假设。
4. **朴素贝叶斯独立性假设过强**：文本特征之间显然相关（"New York"），朴素贝叶斯仍能用是因为**排序不变**（即使概率估计错，分类往往对）。
5. **相关 ≠ 因果**：M 362K 教条件概率，但不教因果。$P(Y|X)\neq P(Y|\text{do}(X))$（Pearl do-calculus，需额外学习）。

---

## 🔴 应用层（ML 公式级对应）

| 本课概念 | ML 公式 | 场景 |
|---|---|---|
| Bayes 定理 | $P(y\|x)=\dfrac{P(x\|y)P(y)}{P(x)}$ | 朴素贝叶斯 / 贝叶斯推断 |
| 独立性假设 | $P(x_1,\dots,x_n\|y)=\prod_i P(x_i\|y)$ | 朴素贝叶斯分类器 |
| LLN | $\dfrac{1}{n}\sum\nabla\ell\xrightarrow{P}\nabla L$ | SGD 收敛 |
| CLT | $\bar{X}_n\approx N(\mu,\sigma^2/n)$ | BatchNorm / 权重初始化 |
| MLE = 似然最大化 | $\hat\theta=\arg\max_\theta\prod p(x_i\|\theta)$ | 所有参数估计 |
| 交叉熵 = $H(p)+\text{KL}(p\|q)$ | $\mathcal{L}=-\sum p\log q$ | 分类损失函数 |
| Markov 平稳分布 | $\pi=\pi P$ | PageRank / MCMC |
| Markov 遍历 | $\tfrac{1}{n}\sum f(X_k)\to E_\pi f$ | MCMC 采样 |

### 从本科概率到 ML 的三条主干道

1. **Bayes 道**：Bayes 定理 → 朴素贝叶斯 → 贝叶斯推断 → 变分推断（VAE ELBO）/ 扩散模型
2. **极限道**：LLN → SGD 收敛；CLT → BatchNorm / 参数初始化 / MLE 渐近正态
3. **Markov 道**：Markov 链 → MCMC（贝叶斯采样）/ PageRank / 强化学习 MDP

---

## 与 work4ai 讲透系列的交叉

- **讲透朴素贝叶斯**：第 3 章 Bayes + 第 2 章独立性
- **讲透 SGD**：第 8 章 LLN + CLT
- **讲透 BatchNorm**：第 8 章 CLT（梯度噪声正态化）
- **讲透 MCMC**：第 9 章 Markov 链 + 平稳分布
- **讲透交叉熵**：第 7 章 Jensen 不等式 + 熵（连接信息论）
