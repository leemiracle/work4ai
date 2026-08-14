# Harvard Math 114 · 习题集（Folland 精选）

> **来源**：Folland *Real Analysis* Ch 1-7 习题 + 自编 ML 关联题
> **分级**：⭐ 基础 / ⭐⭐ 中等 / ⭐⭐⭐ 开放（ML 关联）

---

## 第 1 章 · 测度

### Q1.1 ⭐（σ-代数）
证明：如果 $\mathcal{M}_1$ 和 $\mathcal{M}_2$ 都是 $X$ 上的 σ-代数，则 $\mathcal{M}_1 \cap \mathcal{M}_2$ 也是 σ-代数。

<details><summary>解</summary>

验证三条：
1. $X \in \mathcal{M}_1 \cap \mathcal{M}_2$ ✓
2. $A \in \mathcal{M}_1 \cap \mathcal{M}_2 \Rightarrow A \in \mathcal{M}_i \Rightarrow A^c \in \mathcal{M}_i \Rightarrow A^c \in \mathcal{M}_1 \cap \mathcal{M}_2$ ✓
3. 可数并类似。

**注意**：$\mathcal{M}_1 \cup \mathcal{M}_2$ 不一定是 σ-代数（反例：$\{A, A^c, \emptyset, X\}$ 和 $\{B, B^c, \emptyset, X\}$ 的并）。
</details>

### Q1.2 ⭐⭐（外测度）
设 $\mu^*$ 是 $\mathbb{R}$ 上的 Lebesgue 外测度。证明 $\mu^*(\{x\}) = 0$ 不成立，但 $\mu^*(\mathbb{Q} \cap [0,1]) = 0$。

<details><summary>解</summary>

- $\mu^*(\{x\}) = 0$：用区间 $[x, x + \epsilon]$ 覆盖，$\mu^* \leq \epsilon \to 0$。**修正**：实际上 $\mu^*(\{x\}) = 0$ 对单点集成立！
- $\mu^*(\mathbb{Q} \cap [0,1])$：枚举有理数 $q_1, q_2, \ldots$，用 $[q_n, q_n + \epsilon/2^n]$ 覆盖，总长 $\sum \epsilon/2^n = \epsilon \to 0$。所以测度为 0。
</details>

---

## 第 2 章 · 积分

### Q2.1 ⭐（简单函数积分）
计算 $\int_0^1 \mathbf{1}_\mathbb{Q} \, dm$（Dirichlet 函数的 Lebesgue 积分）。

<details><summary>解</summary>

$\mathbf{1}_\mathbb{Q}$ 是简单函数 $= 1 \cdot \mathbf{1}_{\mathbb{Q} \cap [0,1]} + 0 \cdot \mathbf{1}_{\mathbb{Q}^c \cap [0,1]}$。

$$\int_0^1 \mathbf{1}_\mathbb{Q} \, dm = 1 \cdot m(\mathbb{Q} \cap [0,1]) + 0 \cdot m(\mathbb{Q}^c \cap [0,1]) = 1 \cdot 0 + 0 \cdot 1 = 0$$

**对比 Riemann**：上和 = 1，下和 = 0，不可积。

**ML 关联**：这说明了为什么概率论必须用 Lebesgue 积分——离散分布和连续分布可以统一处理。
</details>

### Q2.2 ⭐⭐（DCT 应用）
设 $f_n(x) = \frac{n \sin(x/n)}{x} \mathbf{1}_{[0,1]}(x)$。求 $\lim_{n \to \infty} \int_0^1 f_n \, dm$。

<details><summary>解</summary>

1. $f_n(x) \to 1$ 逐点（因为 $\sin(t)/t \to 1$ as $t \to 0$）
2. $|f_n(x)| \leq \frac{n \cdot (x/n)}{x} = 1$（因为 $|\sin t| \leq |t|$）→ 被 $g = 1$ 控制
3. $g = 1 \in L^1([0,1])$ ✓

由 DCT：$\lim \int f_n = \int \lim f_n = \int_0^1 1 \, dm = 1$。

**ML 关联**：这就是 SGD 收敛证明中"极限与期望换序"的原型。
</details>

### Q2.3 ⭐⭐⭐（开放题：ML 中的 DCT）
mini-batch SGD 更新 $\theta_{k+1} = \theta_k - \frac{\eta}{|B|}\sum_{i \in B_k} \nabla \ell(\theta_k; x_i)$。解释当 $|B_k| \to \infty$ 时，为什么 $\frac{1}{|B|}\sum \nabla \ell \to E[\nabla \ell]$，并用 DCT 语言表述。

<details><summary>解（思路）</summary>

1. **强大数定律**：$\frac{1}{n}\sum_{i=1}^n \nabla \ell(\theta; x_i) \xrightarrow{a.s.} E[\nabla \ell]$（i.i.d. 假设下）
2. **DCT 视角**：如果 $|\nabla \ell(\theta; x)| \leq g(x)$ 且 $E[g] < \infty$（梯度有界假设），则 DCT 保证积分（期望）收敛。
3. **工程意义**：这就是为什么 batch size 大时 SGD 接近全梯度下降——DCT 是理论保证。

**实际验证**：batch size $\uparrow$ → 梯度方差 $\downarrow$ → 更新更稳定。
</details>

---

## 第 3 章 · Radon-Nikodym

### Q3.1 ⭐⭐（绝对连续）
$\nu \ll \mu$ 但 $\mu \ll \nu$ 不成立。给出例子。

<details><summary>解</summary>

设 $\mu = m$（Lebesgue 测度），$\nu$ = 在 $\{0\}$ 处的点质量 1。

- $\nu \ll \mu$：$\mu(A) = 0 \Rightarrow 0 \notin A \Rightarrow \nu(A) = 0$ ✓
- $\mu \ll \nu$ 不成立：$\mu(\{0\}) = 0$ 但 $\nu(\{0\}) = 1 \neq 0$... 

**修正**：$\nu(\{0\}) = 1$ 但 $\mu(\{0\}) = 0$，所以 $\nu \not\ll \mu$。反过来 $\mu \ll \nu$ 要求 $\nu(A) = 0 \Rightarrow \mu(A) = 0$，但 $\nu(\mathbb{R} \setminus \{0\}) = 0$ 而 $\mu(\mathbb{R} \setminus \{0\}) = \infty$。

**正确例子**：$\mu = m + \delta_0$，$\nu = m$。则 $\nu \ll \mu$（$\mu(A)=0 \Rightarrow m(A)=0 \Rightarrow \nu(A)=0$），但 $\mu \not\ll \nu$（$\nu(\{0\})=0$ 但 $\mu(\{0\})=1$）。
</details>

---

## 第 5 章 · Banach / Hilbert 空间

### Q5.1 ⭐（Banach 空间）
证明 $L^1([0,1])$ 是完备的（Banach 空间）。

<details><summary>解（思路）</summary>

设 $\{f_n\}$ 是 $L^1$ 中的 Cauchy 列。取子列 $f_{n_k}$ 使 $\|f_{n_{k+1}} - f_{n_k}\|_1 < 2^{-k}$。

令 $g_K = \sum_{k=1}^K |f_{n_{k+1}} - f_{n_k}|$，$g = \sum_{k=1}^\infty |f_{n_{k+1}} - f_{n_k}|$。

由 MCT：$\int g = \lim \int g_K \leq \sum 2^{-k} = 1 < \infty$。所以 $g < \infty$ a.e. → $f_{n_k}$ a.e. 收敛到某 $f$。

由 Fatou：$\|f - f_{n_k}\|_1 \leq \liminf \|f_m - f_{n_k}\|_1 \to 0$。

**ML 关联**：完备性保证了 Cauchy 列（如梯度下降序列）有极限。
</details>

### Q5.2 ⭐⭐⭐（开放题：RKHS）
高斯核 $k(x,y) = e^{-\|x-y\|^2/(2\sigma^2)}$ 定义了一个 RKHS $\mathcal{H}$。解释为什么 $\mathcal{H}$ 是 Hilbert 空间，以及 SVM 如何利用这个结构。

<details><summary>解（思路）</summary>

1. **RKHS 定义**：$\mathcal{H}$ 是函数空间，内积 $\langle f, g \rangle_\mathcal{H}$ 满足**再生性**：$f(x) = \langle f, k(x, \cdot) \rangle_\mathcal{H}$。
2. **Hilbert 空间**：$\mathcal{H}$ 配以内积是完备的（由 $L^2$ 的完备性保证）。
3. **SVM**：在 $\mathcal{H}$ 中找最大间隔超平面：$\min \|w\|_\mathcal{H}^2$ s.t. $y_i \langle w, \phi(x_i) \rangle \geq 1$。
4. **核技巧**：$\langle \phi(x), \phi(y) \rangle = k(x,y)$，不需要显式计算 $\phi$。

**连接**：Math 114 的 Hilbert 空间理论 + Riesz 表示定理是 SVM 的数学基础。
</details>

---

## 第 6 章 · $L^p$ 空间

### Q6.1 ⭐（Hölder 不等式）
用 Hölder 证明 $\|fg\|_1 \leq \|f\|_2 \|g\|_2$（$p = q = 2$ 的特例 = Cauchy-Schwarz）。

<details><summary>解</summary>

Young 不等式：$ab \leq \frac{a^p}{p} + \frac{b^q}{q}$（$\frac{1}{p} + \frac{1}{q} = 1$）。

令 $a = |f|/\|f\|_p$, $b = |g|/\|g\|_q$：

$$\frac{|fg|}{\|f\|_p \|g\|_q} \leq \frac{|f|^p}{p\|f\|_p^p} + \frac{|g|^q}{q\|g\|_q^q}$$

两边积分：$\frac{\|fg\|_1}{\|f\|_p \|g\|_q} \leq \frac{1}{p} + \frac{1}{q} = 1$。

**ML 关联**：Cauchy-Schwarz 在内积空间中无处不在（注意力机制的 softmax 归一化）。
</details>

### Q6.2 ⭐⭐（4 种收敛模式）
构造 $X_n \to 0$ 依概率但 $X_n \not\to 0$ a.s. 的例子。

<details><summary>解</summary>

在概率空间 $([0,1], \mathcal{B}, m)$ 上：

定义 $X_n = \mathbf{1}_{[k/2^m, (k+1)/2^m]}$，其中 $n = 2^m + k$, $0 \leq k < 2^m$（即把 $[0,1]$ 不断二分，按二进分解排列区间）。

- **依概率**：$P(X_n > \epsilon) = 1/2^m \to 0$ ✓
- **不 a.s.**：对任何 $x \in [0,1]$，$X_n(x)$ 有无穷多个 1（每个尺度 $2^{-m}$ 都有覆盖 $x$ 的区间），所以 $X_n(x) \not\to 0$。

**ML 关联**：这说明训练中 loss 依概率下降不等于每条路径都收敛——variance reduction 技术的理论动机。
</details>

---

## 综合大题

### Q-Final ⭐⭐⭐（从测度论到 GAN）
Wasserstein GAN 的损失 $W_1(\mu, \nu) = \inf_{\gamma \in \Pi(\mu,\nu)} E_{(x,y)\sim\gamma}[\|x-y\|]$。解释 $\Pi(\mu, \nu)$（耦合）的测度论定义，以及为什么 Kantorovich 对偶 $W_1 = \sup_{\|f\|_L \leq 1} E_\mu[f] - E_\nu[f]$ 用到了 Radon 测度理论。

<details><summary>解（思路）</summary>

1. **$\Pi(\mu, \nu)$**：所有边缘分布为 $\mu$ 和 $\nu$ 的联合测度 $\gamma$。即 $\gamma(A \times \mathbb{R}) = \mu(A)$, $\gamma(\mathbb{R} \times B) = \nu(B)$。
2. **Kantorovich 对偶**：$W_1(\mu,\nu) = \sup_{f \in \text{Lip}_1} \left(\int f \, d\mu - \int f \, d\nu\right)$
3. **Radon 测度理论**：$\mu, \nu$ 是 Radon 测度（$C_0(X)^*$ 的元素，Riesz 表示定理），$f$ 是 Lipschitz 连续函数。对偶公式的严格推导依赖 Riesz 表示 + 弱收敛。

**ML 关联**：这就是 WGAN 比原始 GAN 更稳定的数学原因——Wasserstein 距离比 KL 散度更光滑。
</details>
