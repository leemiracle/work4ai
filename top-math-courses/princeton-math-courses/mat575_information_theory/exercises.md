# Princeton MAT 575 · 信息论习题集（Cover & Thomas 精选 + ML 应用）

---

## 基础题

### Q1.1（熵的计算）
掷一枚不均匀骰子，$P(X=i) = i/21$，$i=1,\dots,6$。计算 $H(X)$ 并与均匀骰子的熵比较。

<details><summary>解</summary>

$H(X) = -\sum_{i=1}^{6} \frac{i}{21}\log_2\frac{i}{21}$

$= -\frac{1}{21}\left[1\log\frac{1}{21} + 2\log\frac{2}{21} + \cdots + 6\log\frac{6}{21}\right]$

逐项计算：$H(X) \approx 2.39$ bits

均匀骰子：$H = \log_2 6 \approx 2.58$ bits

**结论**：不均匀分布的熵更小 ✓（均匀分布最大熵）

**ML 关联**：不均匀标签分布（类别不平衡）的信息量更少。
</details>

### Q1.2（KL 散度计算）
$p = (0.5, 0.5)$，$q = (0.9, 0.1)$。计算 $\text{KL}(p\|q)$ 和 $\text{KL}(q\|p)$，验证非对称性。

<details><summary>解</summary>

$\text{KL}(p\|q) = 0.5\log\frac{0.5}{0.9} + 0.5\log\frac{0.5}{0.1}$

$= 0.5\log\frac{5}{9} + 0.5\log 5 = 0.5[\log 5 - \log 9 + \log 5] = \log 5 - \log 3 \approx 0.737$ bits

$\text{KL}(q\|p) = 0.9\log\frac{0.9}{0.5} + 0.1\log\frac{0.1}{0.5}$

$= 0.9\log 1.8 + 0.1\log 0.2 \approx 0.9(0.848) + 0.1(-2.322) \approx 0.531$ bits

**结论**：$\text{KL}(p\|q) = 0.737 \neq 0.531 = \text{KL}(q\|p)$ ✓ 非对称

**ML 关联**：VAE 使用 $\text{KL}(q\|p)$（forward KL），是 mean-seeking 的。
</details>

---

## 中等题

### Q2.1（交叉熵 = 熵 + KL）★
证明 $H(p,q) = H(p) + \text{KL}(p\|q)$，并解释为什么分类任务用 cross-entropy 而非 MSE。

<details><summary>解</summary>

$H(p,q) = -\sum_x p(x)\log q(x)$

$= -\sum_x p(x)\log p(x) + \sum_x p(x)\log p(x) - \sum_x p(x)\log q(x)$

$= H(p) + \sum_x p(x)\log\frac{p(x)}{q(x)} = H(p) + \text{KL}(p\|q)$

**为什么用 cross-entropy 而非 MSE**：
1. Cross-entropy 的梯度与 softmax 输出匹配（不会饱和），MSE 对 softmax 的梯度会消失
2. 最大似然估计 = 最小化 cross-entropy = 最小化 KL$(p_{\text{true}}\|q_\theta)$
3. Cross-entropy 是信息论最优编码的代价
</details>

### Q2.2（数据处理不等式）
$X \to Y \to Z$ 是 Markov 链。证明 $I(X;Z) \leq I(X;Y)$。

<details><summary>解</summary>

由 Markov 链：$p(z|x,y) = p(z|y)$（给定 $Y$，$Z$ 与 $X$ 独立）。

$I(X;Y,Z) = I(X;Y) + I(X;Z|Y) = I(X;Y) + 0$（Markov 性）

又 $I(X;Y,Z) = I(X;Z) + I(X;Y|Z)$

所以 $I(X;Y) = I(X;Z) + I(X;Y|Z)$

因为 $I(X;Y|Z) \geq 0$，所以 $I(X;Z) \leq I(X;Y)$ ✓

**ML 关联**：深层特征压缩 → 不能增加信息量。信息瓶颈的理论基础。
</details>

### Q2.3（高斯 KL 的闭式解）★
计算 $\text{KL}(\mathcal{N}(\mu_1,\sigma_1^2) \| \mathcal{N}(\mu_0,\sigma_0^2))$。

<details><summary>解</summary>

$\text{KL} = \int \mathcal{N}(x;\mu_1,\sigma_1^2)\log\frac{\mathcal{N}(x;\mu_1,\sigma_1^2)}{\mathcal{N}(x;\mu_0,\sigma_0^2)}\,dx$

$= \log\frac{\sigma_0}{\sigma_1} + \frac{\sigma_1^2 + (\mu_1-\mu_0)^2}{2\sigma_0^2} - \frac{1}{2}$

**VAE 特例**：$\mu_0=0, \sigma_0=1$：

$\text{KL}(\mathcal{N}(\mu,\sigma^2)\|\mathcal{N}(0,1)) = \frac{1}{2}(\mu^2 + \sigma^2 - \log\sigma^2 - 1)$

**ML 关联**：这就是 VAE 损失函数中的 KL 项，有闭式解所以计算高效。
</details>

### Q2.4（信道容量）
BSC 信道翻转概率 $p = 0.1$，计算容量 $C$。

<details><summary>解</summary>

$C = 1 - H(p) = 1 - [-0.1\log_2 0.1 - 0.9\log_2 0.9]$

$= 1 - [0.1 \times 3.322 + 0.9 \times 0.152] = 1 - [0.332 + 0.137] = 1 - 0.469 = 0.531$ bits

**ML 关联**：标签噪声（如 label smoothing $p=0.1$）降低了有效信息传输率。
</details>

---

## 开放题

### Q3.1（VAE ELBO 推导）★
用 Jensen 不等式推导 VAE 的 ELBO，并解释为什么变分推断是近似后验。

<details><summary>解（思路）</summary>

目标：最大化 $\log p(x) = \log\int p(x,z)\,dz$

引入变分分布 $q(z)$：
$$\log p(x) = \log\int \frac{p(x,z)}{q(z)}q(z)\,dz = \log\mathbb{E}_{q(z)}\left[\frac{p(x,z)}{q(z)}\right]$$

Jensen 不等式（$\log$ 是凹函数）：
$$\log\mathbb{E}[f] \geq \mathbb{E}[\log f]$$

$$\log p(x) \geq \mathbb{E}_{q(z)}\left[\log\frac{p(x,z)}{q(z)}\right] = \mathbb{E}_{q(z)}[\log p(x|z)] - \text{KL}(q(z)\|p(z))$$

**为什么是近似**：ELBO 与 $\log p(x)$ 的差距 = $\text{KL}(q(z|x)\|p(z|x))$，只有当 $q(z|x) = p(z|x)$ 时才相等。通常后验 $p(z|x)$ 不可计算（intractable），所以用参数化 $q_\phi(z|x)$ 近似。
</details>

### Q3.2（信息瓶颈方法）★
信息瓶颈目标为 $\min_{p(z|x)} I(Z;X) - \beta I(Z;Y)$，解释它如何推广了 PCA 和 rate-distortion。

<details><summary>解（思路）</summary>

- $I(Z;X)$：表示 $Z$ 压缩了多少输入信息（率）
- $I(Z;Y)$：表示 $Z$ 保留了多少关于标签的信息（相关度）
- $\beta$：权衡压缩与相关度

**与 rate-distortion 的关系**：率失真是 $I(Z;X)$ 在给定失真约束下的最小化（无监督）。信息瓶颈增加了 $I(Z;Y)$ 项（监督）。

**与 PCA 的关系**：PCA 最小化重建误差 ≈ 最大化 $I(Z;X)$（无监督信息瓶颈的退化情况）。

**ML 关联**：深度学习可解释性——训练动态的"压缩阶段"假说。
</details>

### Q3.3（RLHF 中的 KL 正则化）★
RLHF 目标 $\max_\theta \mathbb{E}[r(x,y)] - \beta\,\text{KL}(\pi_\theta\|π_{\text{ref}})$。解释 KL 项的作用，并推导 DPO 是如何隐式处理它的。

<details><summary>解（思路）</summary>

**KL 项的作用**：
1. 防止 $\pi_\theta$ 偏离 $\pi_{\text{ref}}$ 太远 → 防止 reward hacking
2. 保证生成多样性 → KL = 0 时 $\pi_\theta = \pi_{\text{ref}}$
3. 正则化 → 等价于以 $\pi_{\text{ref}}$ 为先验的贝叶斯优化

**DPO 推导**：最优策略有闭式解：
$$\pi^*(y|x) = \frac{1}{Z(x)}\pi_{\text{ref}}(y|x)\exp\left(\frac{r(x,y)}{\beta}\right)$$

代入消去 $r$，得到 DPO 损失（只用偏好数据，无需显式 reward model）。
</details>

### Q-Final（信息论泛化界）★
用 PAC-Bayes 推导：泛化误差 $\leq \hat{R}(h) + \sqrt{\frac{\text{KL}(Q\|P) + \ln(2\sqrt{n}/\delta)}{2n}}$，解释 $\text{KL}(Q\|P)$ 的含义。

<details><summary>解（思路）</summary>

设先验 $P$（不依赖数据），后验 $Q$（学习后的策略分布）。

对每个 $h \in \text{supp}(Q)$，用 Hoeffding：$P(R(h) - \hat{R}(h) > \epsilon) \leq e^{-2n\epsilon^2}$

对 $Q$ 取期望（不是 $P$），需要改变测度：
$$\mathbb{E}_Q[e^{-2n\epsilon^2}] \leq e^{-2n\epsilon^2} \cdot e^{\text{KL}(Q\|P)}$$

（用了 $\mathbb{E}_Q[f] \leq e^{\text{KL}(Q\|P)} \sup f$）

令右边 $= \delta$，解 $\epsilon$。

**$\text{KL}(Q\|P)$ 的含义**：后验 $Q$（学到的）与先验 $P$（假设空间）的"距离"。如果 $Q$ 离 $P$ 很远（过拟合），KL 大，泛化界松。如果 $Q \approx P$（简单模型），泛化好。

**ML 关联**：这解释了为什么"简单模型泛化好"——它们的后验接近先验，KL 小。
</details>
