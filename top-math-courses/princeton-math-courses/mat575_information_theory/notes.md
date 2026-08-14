# Princeton MAT 575 · 信息论笔记（Cover & Thomas *Elements of Information Theory* 2nd ed）

> **教材**：Cover & Thomas, *Elements of Information Theory* (2nd ed, Wiley, 2006)
> **一手核实**：Cover (Stanford EE376A) 历年讲义 + Cover & Thomas 目录
> **Princeton 页面**：MAT 575 = 研究生信息论

---

## 费曼三层讲透

### 🟢 直觉层

- **熵 $H(X)$** = "平均惊讶程度"：事件越稀有（$p$ 越小），$\log(1/p)$ 越大，你越惊讶；熵是所有事件惊讶度的**期望**
- **KL 散度** = "用错模型的代价"：如果你以为世界是 $q$ 但实际是 $p$，你编码时多花的比特数
- **互信息 $I(X;Y)$** = "知道 $Y$ 后对 $X$ 的不确定性的减少量"：$Y$ 给你提供了多少关于 $X$ 的信息

---

### 🔵 数学层

## 核心框架

```
熵 H(X) → 联合熵 H(X,Y) → 条件熵 H(Y|X) → 互信息 I(X;Y)
    ↓           ↓                ↓                ↓
  惊讶度     不确定性叠加      剩余不确定性     信息共享量
    ↓
KL 散度 → 交叉熵 → 数据处理不等 → 信道容量 → 率失真
```

---

## 第 2 章：Entropy, Relative Entropy, and Mutual Information ★★★

### 2.1 熵

> 对离散随机变量 $X$，概率分布 $p(x)$：
> $$H(X) = -\sum_{x \in \mathcal{X}} p(x) \log p(x) = \mathbb{E}\left[\log \frac{1}{p(X)}\right]$$

**直觉**：$\log(1/p(x))$ 是事件 $x$ 的"惊讶度"（surprisal / information content）。熵是惊讶度的期望。

**单位**：$\log$ 以 2 为底 → 比特（bits）；以 $e$ 为底 → 奈特（nats）。

**性质**：
- $H(X) \geq 0$（非负）
- $H(X) \leq \log|\mathcal{X}|$（均匀分布最大）
- 均匀分布 $U(1,\dots,n)$：$H = \log n$

**ML 关联**：决策树（ID3/C4.5）选择信息增益最大的特征；熵用于不确定性度量。

### 2.2 联合熵与条件熵

**联合熵**：
$$H(X, Y) = -\sum_{x,y} p(x,y) \log p(x,y)$$

**条件熵（链式法则）**：
$$H(X, Y) = H(X) + H(Y|X)$$
$$H(Y|X) = \sum_x p(x) H(Y|X=x) = -\sum_{x,y} p(x,y) \log p(y|x)$$

**直觉**：$H(Y|X)$ = 知道 $X$ 后 $Y$ 的**剩余不确定性**。

### 2.3 互信息 ★

$$I(X;Y) = H(X) - H(X|Y) = H(Y) - H(Y|X) = H(X) + H(Y) - H(X,Y)$$

**直觉**：互信息 = 知道 $Y$ 后对 $X$ 的不确定性的减少量。

**性质**：
- $I(X;Y) = I(Y;X) \geq 0$（对称、非负）
- $I(X;Y) = 0 \iff X \perp Y$（独立）
- $I(X;X) = H(X)$（自信息 = 熵）

**ML 关联**：表示学习（最大化特征与标签的互信息）、对比学习 InfoNCE、信息瓶颈。

### 2.4 KL 散度（相对熵）★★★

$$\text{KL}(p \| q) = \sum_x p(x) \log \frac{p(x)}{q(x)} = \mathbb{E}_p\left[\log \frac{p(X)}{q(X)}\right]$$

**直觉**：KL = "用分布 $q$ 编码来自 $p$ 的数据时，比最优编码多花的比特数"。

**关键性质**：
1. **非负性（Gibbs 不等式）**：$\text{KL}(p\|q) \geq 0$，等号当且仅当 $p = q$ a.s.
2. **非对称**：$\text{KL}(p\|q) \neq \text{KL}(q\|p)$（这是 VAE 用 forward KL 的原因）
3. **链式法则**：$\text{KL}(p(x,y)\|q(x,y)) = \text{KL}(p(x)\|q(x)) + \text{KL}(p(y|x)\|q(y|x))$

**证明非负性**（KL ≥ 0）：

利用 $\ln t \leq t - 1$（Jensen 不等式的推论）：
$$-\text{KL}(p\|q) = \sum p(x) \ln \frac{q(x)}{p(x)} \leq \sum p(x)\left(\frac{q(x)}{p(x)} - 1\right) = \sum q(x) - \sum p(x) = 1 - 1 = 0$$

**ML 关联**：KL 散度是 VAE / diffusion / RLHF / DPO 的统一语言。

### 2.5 交叉熵

$$H(p, q) = -\sum_x p(x) \log q(x) = H(p) + \text{KL}(p\|q)$$

**关键分解**：交叉熵 = 真实熵 + KL 散度。

**ML 关联** ★★★：分类任务的 cross-entropy loss：
$$\mathcal{L}_{\text{CE}} = -\sum_y p_{\text{true}}(y) \log q_\theta(y) = H(p_{\text{true}}) + \text{KL}(p_{\text{true}} \| q_\theta)$$

最小化 cross-entropy = 最小化 KL → 让模型分布 $q_\theta$ 逼近真实分布 $p_{\text{true}}$。

当 $p_{\text{true}}$ 是 one-hot（真实标签）：$H(p_{\text{true}}) = 0$，所以 $\mathcal{L}_{\text{CE}} = \text{KL}$。

### 2.6 Jensen 不等式与凸性

$\text{KL}(p\|q)$ 对 $(p,q)$ 对是**凸**的（在 $q$ 固定时对 $p$ 凸，反之亦然）。

这是变分推断中 ELBO 推导的数学基础。

---

## 第 3 章：Asymptotic Equipartition Property (AEP)

### 3.1 AEP ★

> 若 $X_1, X_2, \dots$ i.i.d. $\sim p(x)$，则
> $$-\frac{1}{n}\log p(X_1, \dots, X_n) \xrightarrow{P} H(X)$$

**证明**：由 SLLN，$-\frac{1}{n}\sum \log p(X_i) \xrightarrow{a.s.} \mathbb{E}[-\log p(X)] = H(X)$。

**ML 关联**：AEP 是信息论的大数定律——"典型序列"的概念。

### 3.2 典型集

**典型集** $\mathcal{A}_\epsilon^{(n)}$：所有概率在 $2^{-n(H \pm \epsilon)}$ 的序列。

**关键定理**：$|\mathcal{A}_\epsilon^{(n)}| \approx 2^{nH}$，且典型集概率 $\to 1$。

→ 数据压缩的理论基础：只需 $nH$ 比特就能无歧义编码 $n$ 个样本。

---

## 第 5 章：Data Compression（数据压缩）

### 5.1 编码定理

> 任何无歧义编码的平均码长 $\bar{L}$ 满足：
> $$H(X) \leq \bar{L} < H(X) + 1$$

### 5.2 Huffman 编码

贪心算法：每次合并概率最小的两个节点。最优前缀码。

**ML 关联**：模型量化、LLM 权重压缩（如 GPTQ、AWQ）。

### 5.3 算术编码

将序列映射到 $[0,1)$ 区间的一个子区间。码长 $\approx nH$（比 Huffman 更接近熵）。

---

## 第 7 章：Channel Capacity（信道容量）★★

### 7.1 定义

> 信道容量：
> $$C = \max_{p(x)} I(X; Y)$$

**Shannon 信道编码定理**：如果传输速率 $R < C$，则存在编码使错误概率任意小；如果 $R > C$，则不可能可靠传输。

### 7.2 BSC（二元对称信道）

$$C = 1 - H(p)$$

其中 $p$ 是翻转概率，$H(p) = -p\log p - (1-p)\log(1-p)$。

### 7.3 AWGN（加性高斯白噪声信道）

$$C = \frac{1}{2}\log_2\left(1 + \frac{P}{N}\right)$$

$P$ = 信号功率，$N$ = 噪声功率。这就是 **Shannon-Hartley 定理**。

**ML 关联**：信息瓶颈方法 $C_\beta = I(Z;Y) - \beta I(Z;X)$ 是信道容量的推广。

---

## 第 8 章：Differential Entropy（微分熵）

### 8.1 定义

> 对连续随机变量 $X$，密度 $f(x)$：
> $$h(X) = -\int_{-\infty}^{\infty} f(x) \log f(x) \, dx$$

**注意**：微分熵可以为负（与离散熵不同！），也不是坐标变换不变的。

### 8.2 常见分布的微分熵

| 分布 | 微分熵 |
|---|---|
| $\text{Uniform}(a,b)$ | $\log(b-a)$ |
| $\text{Normal}(\mu, \sigma^2)$ | $\frac{1}{2}\log(2\pi e \sigma^2)$ |
| $\text{Exponential}(\lambda)$ | $1 - \log\lambda$ |

**关键**：正态分布在方差固定时**最大化**微分熵（最大熵原理）。

**ML 关联**：VAE 的 KL 项中，编码器输出 $q(z|x) = \mathcal{N}(\mu, \sigma^2)$ 与先验 $p(z) = \mathcal{N}(0,1)$ 的 KL 散度：
$$\text{KL}(\mathcal{N}(\mu,\sigma^2) \| \mathcal{N}(0,1)) = \frac{1}{2}(\mu^2 + \sigma^2 - \log\sigma^2 - 1)$$

### 8.3 连续 KL 散度

$$\text{KL}(f \| g) = \int f(x) \log \frac{f(x)}{g(x)} \, dx$$

**关键**：连续 KL 散度**非负**且**坐标不变**（与微分熵不同）。

---

## 第 9-10 章：Gaussian Channel & Rate-Distortion Theory

### 率失真函数

$$R(D) = \min_{p(\hat{x}|x):\, \mathbb{E}[d(X,\hat{X})] \leq D} I(X; \hat{X})$$

**直觉**：在允许失真 $D$ 的条件下，最少需要多少信息来表示 $X$。

**ML 关联**：知识蒸馏 = 一种率失真优化（教师网络 → 学生网络的压缩）。

---

## KL 散度在 ML 中的核心应用（公式级对应）★★★

### 1. Cross-entropy = $H(p) + \text{KL}(p\|q)$

$$\mathcal{L}_{\text{CE}}(\theta) = -\sum_y p(y|x)\log q_\theta(y|x) = H(p(\cdot|x)) + \text{KL}(p(\cdot|x) \| q_\theta(\cdot|x))$$

最小化 cross-entropy = 最小化模型分布与真实分布的 KL。

### 2. VAE ELBO = 重建项 − KL 项 ★

$$\log p(x) \geq \text{ELBO} = \mathbb{E}_{q(z|x)}[\log p(x|z)] - \text{KL}(q(z|x) \| p(z))$$

- 重建项：编码器→解码器的重建质量
- KL 项：编码器输出 $q(z|x)$ 与先验 $p(z)$ 的接近程度（正则化）
- **ELBO − log p(x) = KL(q(z|x) ‖ p(z|x))**（证据下界与真实对数似然的差距）

### 3. Diffusion Model = 一串 KL 退化 ★

正向：$q(x_t|x_{t-1}) = \mathcal{N}(\sqrt{1-\beta_t}x_{t-1}, \beta_t I)$

反向 ELBO：
$$\mathcal{L} = \mathbb{E}_q\left[\sum_t \text{KL}(q(x_{t-1}|x_t, x_0) \| p_\theta(x_{t-1}|x_t))\right]$$

每一步都是两个高斯之间的 KL（有闭式解）。

### 4. RLHF = 奖励最大化 − KL 正则化 ★

$$\max_\theta\, \mathbb{E}_{x \sim D, y \sim \pi_\theta(\cdot|x)}[r_\phi(x,y)] - \beta\, \text{KL}(\pi_\theta(\cdot|x) \| \pi_{\text{ref}}(\cdot|x))$$

KL 项防止策略 $\pi_\theta$ 偏离参考模型 $\pi_{\text{ref}}$ 太远（防止 reward hacking）。

### 5. DPO = 隐式 KL 约束 ★

DPO（Direct Preference Optimization）直接优化偏好对数比：
$$\mathcal{L}_{\text{DPO}} = -\log\sigma\left(\beta\log\frac{\pi_\theta(y_w|x)}{\pi_{\text{ref}}(y_w|x)} - \beta\log\frac{\pi_\theta(y_l|x)}{\pi_{\text{ref}}(y_l|x)}\right)$$

这里 $\beta$ 对应 RLHF 中的 KL 约束强度，$y_w/y_l$ 是偏好/非偏好回答。

---

## 数据处理不等（Data Processing Inequality）★★

如果 $X \to Y \to Z$（Markov 链），则：
$$I(X; Z) \leq I(X; Y)$$

**直觉**：后处理不会增加信息量。你不可能从 $Y$ 中"挤出"更多关于 $X$ 的信息。

**ML 关联**：
- 表示学习：深层特征 $Z = f(Y)$ 对标签 $X$ 的信息 $I(Z;X) \leq I(Y;X)$（瓶颈可能丢失信息）
- 信息瓶颈：$Z$ 应保留关于 $Y$（任务）的信息但压缩关于 $X$（输入）的信息

---

## Pinsker 不等式

$$\text{TV}(P, Q) \leq \sqrt{\frac{1}{2}\text{KL}(P \| Q)}$$

其中 $\text{TV}(P,Q) = \sup_A |P(A) - Q(A)|$ 是全变差距离。

**ML 关联**：连接 KL 散度（信息论）与全变差（概率论）→ PAC-Bayes 泛化界的桥梁。

---

## 与 ML 理论的核心关联总表

| 信息论概念 | ML 应用 |
|---|---|
| 熵 $H(X)$ | 决策树、不确定性度量 |
| **Cross-entropy** ★ | 分类损失函数 |
| **KL 散度** ★★★ | VAE / diffusion / RLHF / DPO |
| **互信息 $I(X;Y)$** ★ | 表示学习、对比学习 InfoNCE |
| 数据处理不等 | 信息瓶颈、深度学习容量 |
| 信道容量 | 多任务学习瓶颈 |
| 率失真 | 模型蒸馏、有损压缩 |
| Pinsker 不等式 | PAC-Bayes 泛化界 |
| 最大熵原理 | 正则化、先验选择 |

---

## 🟠 不足层（局限性）

1. **离散 vs 连续的鸿沟**：微分熵 $h(X)$ 可以为负、不是坐标不变的，与离散熵 $H(X)$ 性质不同。连续 KL 散度才是"好的"量。

2. **KL 散度不对称**：$\text{KL}(p\|q) \neq \text{KL}(q\|p)$。选择 forward 还是 reverse KL 有重大后果：
   - Forward KL $\text{KL}(p\|q)$（mean-seeking / zero-avoiding）：VAE 用这个
   - Reverse KL $\text{KL}(q\|p)$（mode-seeking）：EM / 变分推断常用

3. **互信息难以估计**：高维空间中 $I(X;Y)$ 的估计是 NP-hard，实际中用 InfoNCE / MINE 等变分下界近似（有偏差）。

4. **Shannon 信息论的工程局限**：信道编码定理保证**存在性**但不给出**实用编码**——LDPC / Polar 码直到几十年后才被发现。

---

## 🔴 应用层（ML 公式级对应）

| 概念 | 公式 | ML 场景 |
|---|---|---|
| Cross-entropy | $\mathcal{L} = H(p) + \text{KL}(p\|q_\theta)$ | 分类任务损失 |
| VAE ELBO | $= \mathbb{E}_q[\log p(x\|z)] - \text{KL}(q(z\|x)\|p(z))$ | 变分推断 |
| Diffusion KL | $= \sum_t \text{KL}(q(x_{t-1}\|x_t,x_0)\|p_\theta(x_{t-1}\|x_t))$ | 扩散模型 |
| RLHF | $\max\, \mathbb{E}[r] - \beta\,\text{KL}(\pi_\theta\|\pi_{\text{ref}})$ | 对齐训练 |
| DPO | $\log\sigma(\beta[\log\frac{\pi_\theta(y_w)}{\pi_{\text{ref}}(y_w)} - \log\frac{\pi_\theta(y_l)}{\pi_{\text{ref}}(y_l)}])$ | 直接偏好优化 |
| InfoNCE | $= -\mathbb{E}[\log\frac{e^{f(x,y^+)/\tau}}{\sum_j e^{f(x,y_j)/\tau}}] \approx I(X;Y) - \log K$ | 对比学习 |

---

## 与 work4ai 讲透系列的交叉

- **讲透 VAE**：KL 散度 + ELBO + 变分推断
- **讲透 diffusion**：KL 退化链 + score matching
- **讲透 RLHF/DPO**：KL 正则化 + 隐式偏好优化
- **讲透泛化**：信息论泛化界 + PAC-Bayes + Pinsker
