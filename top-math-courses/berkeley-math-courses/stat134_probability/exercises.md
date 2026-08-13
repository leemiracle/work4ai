# UC Berkeley STAT 134 · 习题集（Pitman 精选 + ML 应用）

---

## 基础题

### Q1.1（条件概率）
掷两枚骰子，已知总和 $\geq 10$，求两枚都是 6 的概率。

<details><summary>解</summary>

$P(\text{都是6} | \text{总和} \geq 10) = \frac{P(\text{都是6} \cap \text{总和} \geq 10)}{P(\text{总和} \geq 10)}$

$= \frac{P(\text{都是6})}{P(\text{总和} \geq 10)} = \frac{1/36}{3/36} = \frac{1}{3}$

（总和 $\geq 10$: (4,6),(5,5),(5,6),(6,4),(6,5),(6,6) 共 6 个... 等等，让我重算）

$P(\text{总和} \geq 10)$: 总和为 10,11,12。10 有 3 种，11 有 2 种，12 有 1 种 = 6 种。

$= \frac{1/36}{6/36} = \frac{1}{6}$

**ML 关联**：条件概率 = "缩小样本空间后的概率"。
</details>

### Q1.2（Bayes 定理）
疾病发病率 1%。检测灵敏度 95%，特异度 90%。检测阳性时真正患病的概率？

<details><summary>解</summary>

$P(D) = 0.01$, $P(+|D) = 0.95$, $P(-|\bar{D}) = 0.90 \Rightarrow P(+|\bar{D}) = 0.10$

$P(D|+) = \frac{P(+|D)P(D)}{P(+|D)P(D) + P(+|\bar{D})P(\bar{D})}$

$= \frac{0.95 \times 0.01}{0.95 \times 0.01 + 0.10 \times 0.99} = \frac{0.0095}{0.0095 + 0.099} = \frac{0.0095}{0.1085} \approx 0.0876$

**结论**：阳性后真正患病概率仅 8.76%！（先验太低）

**ML 关联**：类别不平衡数据中，Precision-Recall 的概率本质。
</details>

---

## 中等题

### Q2.1（CLT 应用）
$X_1, \dots, X_{100}$ i.i.d. Uniform(0,1)。估计 $P(\bar{X}_{100} > 0.55)$。

<details><summary>解</summary>

$\mu = 1/2$, $\sigma^2 = 1/12$

$P(\bar{X}_{100} > 0.55) = P\left(\frac{\bar{X}_{100} - 0.5}{\sqrt{1/1200}} > \frac{0.05}{\sqrt{1/1200}}\right)$

$\approx P(Z > 0.05 \times \sqrt{1200}) = P(Z > 1.732) \approx 0.0416$

**ML 关联**：假设检验——"模型 A 的平均表现是否显著优于 0.5？"
</details>

### Q2.2（Poisson 近似）
一个网站每分钟平均收到 3 个请求。用 Poisson 分布求一分钟内收到 $\geq 6$ 个请求的概率。

<details><summary>解</summary>

$X \sim \text{Poisson}(3)$

$P(X \geq 6) = 1 - P(X \leq 5) = 1 - \sum_{k=0}^{5} \frac{e^{-3}3^k}{k!}$

$= 1 - e^{-3}(1 + 3 + 4.5 + 4.5 + 3.375 + 2.025) = 1 - 0.0498 \times 18.4 \approx 1 - 0.916 = 0.084$

**ML 关联**：Poisson 分布建模稀疏事件（点击率、请求量）。
</details>

### Q2.3（期望的线性性）
盒子里有 $n$ 个球，编号 $1$ 到 $n$。随机抽取 $k$ 个（不放回）。求抽取号码之和的期望。

<details><summary>解</summary>

令 $X_i$ = 第 $i$ 个抽出的号码。$S = X_1 + \cdots + X_k$。

$E[X_i] = \frac{n+1}{2}$（对称性：每个位置等可能抽到任何号码）

$E[S] = \sum_{i=1}^{k} E[X_i] = k \cdot \frac{n+1}{2}$

**注意**：不需要 $X_i$ 独立！期望的线性性总是成立。

**ML 关联**：期望线性性是梯度计算的基础（$E[\sum] = \sum E[\cdot]$）。
</details>

---

## 开放题

### Q3.1（朴素贝叶斯分类器）
给定训练数据，推导朴素贝叶斯的预测公式，并解释"朴素"假设的影响。

<details><summary>解（思路）</summary>

预测：$\hat{y} = \arg\max_y P(y|x) = \arg\max_y P(y)\prod_j P(x_j|y)$

（用 Bayes 定理 + 条件独立假设 $x_j \perp x_k | y$）

**"朴素"假设**：特征在给定类别下条件独立。现实中通常不成立（如文本中词之间有依赖），但实践中朴素贝叶斯仍然有效。

**为什么有效**：即使独立性假设被违反，分类决策（argmax）可能不受影响——只需要正确的相对排序。
</details>

### Q3.2（CLT 与 SGD 噪声）★
解释为什么 mini-batch SGD 的梯度噪声 $\delta_t = \nabla L(\theta_t) - \frac{1}{B}\sum_{i \in B_t}\nabla\ell(\theta_t; x_i)$ 近似服从正态分布。

<details><summary>解（思路）</summary>

$\frac{1}{B}\sum_{i \in B_t}\nabla\ell_i$ 是 $B$ 个 i.i.d. 随机变量的平均。

由 CLT：$\frac{1}{B}\sum\nabla\ell_i \approx \mathcal{N}(\nabla L, \Sigma/B)$

所以 $\delta_t = \nabla L - \frac{1}{B}\sum\nabla\ell_i \approx \mathcal{N}(0, \Sigma/B)$

**结论**：梯度噪声方差 $\propto 1/B$ → batch size 越大，噪声越小。

**推论**：SGD 的连续时间极限是 SDE $d\theta = -\nabla L\,dt + \sqrt{\Sigma/B}\,dW$ → Langevin dynamics。
</details>

### Q-Final（Bayes 估计 vs MLE）★
数据 $X_1, \dots, X_n \sim \text{Bernoulli}(\theta)$。先验 $\theta \sim \text{Beta}(\alpha,\beta)$。比较 MLE 和 Bayes (MAP) 估计。

<details><summary>解（思路）</summary>

**MLE**：$\hat{\theta}_{\text{MLE}} = \bar{X}_n = \frac{k}{n}$（$k$ = 成功次数）

**MAP**：后验 $\theta|D \sim \text{Beta}(\alpha+k, \beta+n-k)$

$\hat{\theta}_{\text{MAP}} = \frac{\alpha+k-1}{\alpha+\beta+n-2}$（后验众数）

**后验均值**：$E[\theta|D] = \frac{\alpha+k}{\alpha+\beta+n}$

**差异**：
- $n \to \infty$ 时，两者趋同（先验被数据淹没）
- 小样本时，先验起到正则化作用（防止 $\hat{\theta}=0$ 或 $1$ 的极端估计）
- Beta(1,1) 先验（均匀）→ MAP ≈ MLE

**ML 关联**：$L^2$ 正则化 = 高斯先验 MAP；$L^1$ 正则化 = 拉普拉斯先验 MAP。
</details>
