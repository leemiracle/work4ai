# Princeton MAT 215 · 习题集

> **来源**：Rudin *Principles* Ch 1-7 习题 + Tao *Analysis I* + 自编 ML 关联题
> **分级**：⭐ 基础 / ⭐⭐ 中等 / ⭐⭐⭐ 开放（ML 关联）

---

## 第 1 章 · 实数系统与完备性

### Q1.1 ⭐（ε-δ 极限）
用 ε-δ 定义证明 $\lim_{x \to 3} (2x + 1) = 7$。

<details><summary>解</summary>

要 $|2x+1-7| = |2x-6| = 2|x-3| < \epsilon$。

取 $\delta = \epsilon/2$。则 $|x-3| < \delta \Rightarrow |2x+1-7| = 2|x-3| < 2\delta = \epsilon$ ✓

**策略**：先倒推（解不等式找 δ），再正向书写。
</details>

### Q1.2 ⭐⭐（上确界）
设 $A = \{1 - 1/n : n \in \mathbb{N}\}$。求 $\sup A$ 并用定义证明。

<details><summary>解</summary>

$\sup A = 1$。

1. **上界**：$1 - 1/n < 1, \forall n$ ✓
2. **最小上界**：$\forall \epsilon > 0$, 取 $n > 1/\epsilon$, 则 $1 - 1/n > 1 - \epsilon$。所以 $1 - \epsilon \in A$，即 $1$ 是最小的上界。
</details>

---

## 第 2 章 · 序列与级数

### Q2.1 ⭐（Cauchy 列）
证明 $s_n = \frac{n}{n+1}$ 是 Cauchy 列。

<details><summary>解</summary>

$|s_n - s_m| = \left|\frac{n}{n+1} - \frac{m}{m+1}\right| = \frac{|n-m|}{(n+1)(m+1)}$

假设 $m > n$: $\frac{m-n}{(n+1)(m+1)} < \frac{m}{(n+1)m} = \frac{1}{n+1}$

所以 $\forall \epsilon$, 取 $N = 1/\epsilon$, 则 $n, m > N \Rightarrow |s_n - s_m| < \epsilon$ ✓
</details>

### Q2.2 ⭐⭐（级数收敛）
判断 $\sum_{n=1}^\infty \frac{n^2}{2^n}$ 的收敛性，并求和。

<details><summary>解</summary>

**比值判别法**：$\frac{a_{n+1}}{a_n} = \frac{(n+1)^2 / 2^{n+1}}{n^2 / 2^n} = \frac{(n+1)^2}{2n^2} \to \frac{1}{2} < 1$。收敛。

**求和**：利用 $\sum_{n=0}^\infty x^n = \frac{1}{1-x}$ 求导：
- $\sum n x^n = \frac{x}{(1-x)^2}$
- $\sum n^2 x^n = \frac{x(1+x)}{(1-x)^3}$

代入 $x = 1/2$: $\sum n^2 / 2^n = \frac{(1/2)(3/2)}{(1/2)^3} = 6$。

**ML 关联**：几何级数收敛是 attention mechanism softmax 归一化的数学基础。
</details>

---

## 第 3 章 · 连续性

### Q3.1 ⭐⭐（一致连续）
$f(x) = \sqrt{x}$ 在 $[0, \infty)$ 上一致连续，但 $f(x) = x^2$ 在 $\mathbb{R}$ 上不一致连续。

<details><summary>解</summary>

**$\sqrt{x}$ 一致连续**：$|\sqrt{x} - \sqrt{y}| \leq \sqrt{|x-y|}$（因为有理化解）。取 $\delta = \epsilon^2$。

**$x^2$ 不一致连续**：取 $x_n = n, y_n = n + 1/n$。$|x_n - y_n| = 1/n \to 0$ 但 $|x_n^2 - y_n^2| = |2n \cdot 1/n + 1/n^2| \to 2 \neq 0$。

**ML 关联**：Lipschitz 连续 = 一致连续的特例。GAN 的梯度惩罚要求判别器 Lipschitz。
</details>

### Q3.2 ⭐⭐⭐（开放题：ReLU 与 ε-δ）
用 ε-δ 证明 $\text{ReLU}(x) = \max(0, x)$ 在 $x = 0$ 处连续但不可微。解释为什么 PyTorch 的 `relu` 仍能反向传播。

<details><summary>解</summary>

**连续性**：$|\text{ReLU}(x) - \text{ReLU}(0)| = |\text{ReLU}(x)| \leq |x|$。取 $\delta = \epsilon$，则 $|x| < \delta \Rightarrow |\text{ReLU}(x)| < \epsilon$ ✓

**不可微**：左导数 $= \lim_{h \to 0^-} \frac{\text{ReLU}(h) - 0}{h} = \frac{0}{h} = 0$。右导数 $= \lim_{h \to 0^+} \frac{h}{h} = 1$。$0 \neq 1$ → 不可微。

**PyTorch 仍能反向传播**：PyTorch 的 `autograd` 对 ReLU 在 $x = 0$ 使用**次梯度**约定 $\text{ReLU}'(0) = 0$。这不是数学定理，而是工程选择——选择 $[0, 1]$ 中任意值作为次梯度都合法。实际中 $x = 0$ 的概率为 0（连续分布），所以约定不影响训练。

**深层原因**：深度学习不需要处处可微，只需要"几乎处处可微"（a.e. 可微）。ReLU a.e. 可微（除 $x = 0$），所以反向传播在实践中有效。
</details>

---

## 第 4 章 · 微分

### Q4.1 ⭐（MVT 应用）
用中值定理证明 $|\sin x - \sin y| \leq |x - y|$。

<details><summary>解</summary>

$f = \sin$。由 MVT：$\exists c$ 介于 $x, y$ 之间：$\frac{\sin x - \sin y}{x - y} = \cos c$。

$|\cos c| \leq 1 \Rightarrow |\sin x - \sin y| \leq |x - y|$。

**ML 关联**：这就是 1-Lipschitz 条件。GAN 的 WGAN 要求判别器 1-Lipschitz。
</details>

### Q4.2 ⭐⭐（Taylor 定理）
求 $\cos x$ 在 $x = 0$ 的 4 阶 Taylor 展开，并估计 $x = 0.3$ 时的误差。

<details><summary>解</summary>

$\cos x = 1 - \frac{x^2}{2} + \frac{x^4}{24} - R_5(x)$

余项：$|R_5(x)| = \frac{|\cos^{(5)}(c)|}{5!}|x|^5 = \frac{|\sin c|}{120}|x|^5 \leq \frac{|x|^5}{120}$

$x = 0.3$: $|R_5| \leq \frac{0.3^5}{120} = \frac{0.00243}{120} \approx 2 \times 10^{-5}$。

**ML 关联**：Taylor 展开是 Newton 法和二阶优化的数学基础。
</details>

---

## 第 5 章 · Riemann 积分

### Q5.1 ⭐（可积性）
证明单调函数在 $[a,b]$ 上 Riemann 可积。

<details><summary>解（思路）</summary>

设 $f$ 递增。对分割 $P = \{x_0, \ldots, x_n\}$，$\Delta x_i = (b-a)/n$：

$U(P,f) - L(P,f) = \sum (M_i - m_i)\Delta x_i = \sum (f(x_i) - f(x_{i-1}))\Delta x_i$

$= \Delta x \sum (f(x_i) - f(x_{i-1})) = \Delta x (f(b) - f(a)) = \frac{(b-a)(f(b)-f(a))}{n} \to 0$

所以 $f$ 可积。

**ML 关联**：累积分布函数 (CDF) 是单调的，所以一定可积——这是概率论的隐含假设。
</details>

### Q5.2 ⭐⭐（Dirichlet 函数不可积）
证明 Dirichlet 函数 $f = \mathbf{1}_\mathbb{Q}$ 在 $[0,1]$ 上 Riemann 不可积。

<details><summary>解</summary>

任何分割 $P$：每个子区间 $[x_{i-1}, x_i]$ 都含有有理数（$M_i = 1$）和无理数（$m_i = 0$）。

$U(P,f) = \sum 1 \cdot \Delta x_i = 1$, $L(P,f) = \sum 0 \cdot \Delta x_i = 0$。

$\inf_P U(P,f) = 1 \neq 0 = \sup_P L(P,f)$ → 不可积。

**ML 关联**：这说明了为什么概率论需要 Lebesgue 积分（Dirichlet 函数 Lebesgue 可积，值为 0）。
</details>

---

## 第 6 章 · 函数项级数

### Q6.1 ⭐⭐（一致收敛）
$f_n(x) = \frac{x}{1 + nx^2}$ 在 $\mathbb{R}$ 上一致收敛吗？

<details><summary>解</summary>

逐点极限：$f_n(x) \to 0$ for all $x$。

$\sup_x |f_n(x)|$: $f_n'(x) = \frac{1 - nx^2}{(1+nx^2)^2} = 0 \Rightarrow x = 1/\sqrt{n}$。

$f_n(1/\sqrt{n}) = \frac{1/\sqrt{n}}{1 + n \cdot 1/n} = \frac{1}{2\sqrt{n}} \to 0$

所以**一致收敛**到 0 ✓。

**ML 关联**：一致收敛保证极限保持连续/可微——泛化保证的数学语言。
</details>

---

## 第 7 章 · Heine-Borel 紧致性

### Q7.1 ⭐⭐（紧致性应用）
用极值定理证明：如果 $f: [0,1] \to \mathbb{R}$ 连续且 $f(0) < 0 < f(1)$，则 $\exists c \in (0,1): f(c) = 0$。

<details><summary>解</summary>

1. $f$ 连续 + $[0,1]$ 紧致 → $f$ 取得最大值和最小值。
2. $f(0) < 0$ → 最小值 $< 0$。$f(1) > 0$ → 最大值 $> 0$。
3. 由**介值定理**（连续函数取中间值）：$\exists c: f(c) = 0$。

**ML 关联**：这保证了 loss function 在合理条件下有零点——对抗训练 (GAN) 中判别器损失的平衡点存在性。
</details>

### Q7.2 ⭐⭐⭐（开放题：紧致性与神经网络泛化）
解释为什么权重衰减（weight decay）从数学上保证了神经网络 loss 最小值的存在。

<details><summary>解（思路）</summary>

1. **无正则化**：参数空间 $\Theta = \mathbb{R}^d$（非紧致）→ loss 最小值可能不存在（梯度下降可能"逃逸"到无穷）。
2. **有权重衰减** $\lambda\|\theta\|^2$：等价于约束 $\|\theta\| \leq R$（某 $R$ 取决于 $\lambda$）。
3. $\Theta_R = \{\theta : \|\theta\| \leq R\}$ 是**紧致集**（Heine-Borel：有界+闭）。
4. $L: \Theta_R \to \mathbb{R}$ 连续 → 由**极值定理**：$\exists \theta^* \in \Theta_R: L(\theta^*) = \min_{\Theta_R} L$。
5. 所以训练有理论保证——最小值一定存在。

**深层意义**：这就是为什么实际训练中总是加 weight decay——不只是正则化，更是数学保证。
</details>

---

## 综合大题

### Q-Final ⭐⭐⭐（ε-δ 从头到尾）
设 $f_n(x) = \frac{\sin(nx)}{\sqrt{n}}$。证明 $f_n \rightrightarrows 0$ on $\mathbb{R}$，并讨论 $\{f_n'\}$ 的收敛性。

<details><summary>解</summary>

**一致收敛到 0**：$|f_n(x)| = \frac{|\sin(nx)|}{\sqrt{n}} \leq \frac{1}{\sqrt{n}} \to 0$。这是对 $x$ 无关的上界，所以一致收敛。

**导数**：$f_n'(x) = \frac{n\cos(nx)}{\sqrt{n}} = \sqrt{n}\cos(nx)$。

$\sup_x |f_n'(x)| = \sqrt{n} \to \infty$。所以 $\{f_n'\}$ **不一致收敛**（甚至不逐点收敛，因为 $\sqrt{n}\cos(nx)$ 振荡）。

**教训**：一致收敛不保证导数也一致收敛——导数收敛需要额外条件（导数列一致收敛 + 原函数列在某点收敛）。

**ML 关联**：这就是为什么"loss 收敛"不等于"梯度收敛"——训练中 loss 可能下降但梯度仍振荡（SGD 的方差）。
</details>
