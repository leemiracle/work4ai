# MIT 18.100B · 习题集（Rudin 精选）

> **来源**：Rudin *Principles* Ch 1-8 习题 + OCW 18.100 习题 + 自编

---

## 第 1 章 · 实数系统

### Q1.1（完备性）
证明 $\sqrt{2} \notin \mathbb{Q}$。

<details><summary>解</summary>

反证：设 $\sqrt{2} = p/q$（既约），$p^2 = 2q^2$。所以 $2|p$（$p$ 偶数）。设 $p = 2k$，则 $4k^2 = 2q^2$，$2|q$。矛盾（既约）。
</details>

### Q1.2（上确界）
设 $A = \{x \in \mathbb{Q} : x^2 < 2\}$。证明 $\sup A = \sqrt{2}$（但 $\sqrt{2} \notin A$）。

<details><summary>解</summary>

1. $x^2 < 2 \Rightarrow x \leq \sqrt{2}$（$\sqrt{2}$ 是上界）
2. $\forall \epsilon > 0$, $(\sqrt{2} - \epsilon)^2 < 2$（对足够小 $\epsilon$）→ $\sqrt{2} - \epsilon \in A$
3. 所以 $\sup A = \sqrt{2}$
4. 但 $\sqrt{2} \notin \mathbb{Q} \Rightarrow \sqrt{2} \notin A$
</details>

---

## 第 2 章 · 基础拓扑

### Q2.1（开集）
证明开集的任意并是开集，有限交是开集。

<details><summary>解</summary>

**任意并**：$x \in \bigcup_\alpha U_\alpha \Rightarrow x \in U_\beta$（某个 $\beta$）$\Rightarrow \exists r: B_r(x) \subset U_\beta \subset \bigcup U_\alpha$。

**有限交**：$x \in \bigcap_{i=1}^n U_i \Rightarrow \exists r_i: B_{r_i}(x) \subset U_i$。取 $r = \min r_i > 0$（有限个 min）$\Rightarrow B_r(x) \subset \bigcap U_i$。

**为什么"无限交"不成立**：$U_n = (-1/n, 1/n)$，$\bigcap U_n = \{0\}$（不是开集）。
</details>

### Q2.2（紧致性 — Heine-Borel）
证明 $[0,1]$ 是紧致的。

<details><summary>解（思路）</summary>

用**二分法**：假设 $[0,1]$ 有开覆盖 $\{G_\alpha\}$ 无有限子覆盖。

将 $[0,1]$ 二等分：$[0,1/2]$ 或 $[1/2,1]$ 至少一个不能被有限覆盖。记为 $I_1$。

继续二分得到 $I_1 \supset I_2 \supset \cdots$，长度 $\to 0$。

**完备性**：$\bigcap I_n \neq \emptyset$，设 $x \in \bigcap I_n$。

$x \in G_\beta$（某个 $\beta$），$G_\beta$ 开 $\Rightarrow B_r(x) \subset G_\beta$。

当 $n$ 足够大时 $I_n \subset B_r(x) \subset G_\beta$，但 $I_n$ 不能被有限覆盖——矛盾。

**ML 关联**：参数空间紧致 → loss 最小值存在。
</details>

---

## 第 3 章 · 序列与级数

### Q3.1（Cauchy 列）
证明 Cauchy 序列收敛（在 $\mathbb{R}$ 中）。

<details><summary>解（思路）</summary>

1. Cauchy $\Rightarrow$ 有界（取 $N$ 使 $n,m > N$ 时 $|s_n - s_m| < 1$，则 $\{s_n\}$ 有界）
2. 有界 $\Rightarrow$ 有收敛子序列 $s_{n_k} \to s$（Bolzano-Weierstrass）
3. Cauchy + 子列收敛 $\Rightarrow$ 全列收敛 $s_n \to s$

（$|s_n - s| \leq |s_n - s_{n_k}| + |s_{n_k} - s|$ 两项均可小）
</details>

### Q3.2（交错级数）
证明 $\sum (-1)^n / n$ 收敛但不绝对收敛。

<details><summary>解</summary>

收敛：$1/n$ 递减趋于 0，由**交错级数判别法**收敛。

不绝对收敛：$\sum 1/n$ 是发散的调和级数。
</details>

---

## 第 4 章 · 连续性

### Q4.1（一致连续）
$f(x) = 1/x$ 在 $(0,1)$ 上连续但不一致连续。

<details><summary>解</summary>

连续：显然（$\epsilon$-$\delta$ 对每个 $x$ 成立）。

不一致连续：取 $x_n = 1/n, y_n = 1/(n+1)$。$|x_n - y_n| = 1/(n(n+1)) \to 0$，但 $|f(x_n) - f(y_n)| = 1 \not\to 0$。

**ML 关联**：非紧致集上的连续函数不一定一致连续 → Lipschitz 条件的重要性。
</details>

### Q4.2（连续函数取最值）★
紧致集 $K$ 上的连续函数 $f$ 取得最大值。

<details><summary>解（思路）</summary>

1. $f(K)$ 紧致（紧致集的连续像是紧致的）
2. 紧致 $\Rightarrow$ 有界 → $\sup f(K)$ 存在
3. 紧致 $\Rightarrow$ 闭 → $\sup f(K) \in f(K)$
4. 所以 $\exists x^* \in K: f(x^*) = \sup f(K)$

**ML 关联**：loss landscape 上的全局最优存在性。
</details>

---

## 第 5 章 · 微分

### Q5.1（中值定理应用）
$|f(b) - f(a)| \leq M|b - a|$（$|f'| \leq M$）。用此证明 $|\sin x - \sin y| \leq |x - y|$。

<details><summary>解</summary>

$f = \sin$, $|f'| = |\cos| \leq 1 = M$。由 MVT 直接得。

**ML 关联**：Lipschitz 条件 → GAN 判别器的梯度惩罚。
</details>

### Q5.2（Taylor 定理）★
$e^x$ 的 $n$ 阶 Taylor 余项 $R_n(x) = e^c x^{n+1}/(n+1)!$，$c$ 介于 $0$ 和 $x$ 之间。证明 $R_n(x) \to 0$。

<details><summary>解</summary>

$|R_n(x)| \leq e^{|x|}|x|^{n+1}/(n+1)! \to 0$（$e^{|x|}$ 固定, $|x|^{n+1}/(n+1)! \to 0$ 因 $(n+1)!$ 增长远快于幂函数）。

**ML 关联**：Taylor 展开用于 Newton 法、loss landscape 分析。
</details>

---

## 第 6 章 · Riemann 积分

### Q6.1（可积性）
Dirichlet 函数 $f(x) = \begin{cases} 1 & x \in \mathbb{Q} \\ 0 & x \notin \mathbb{Q} \end{cases}$ 在 $[0,1]$ 上不可积。

<details><summary>解</summary>

任何分割 $P$ 的每个子区间都有有理数和无理数 → $M_i = 1, m_i = 0$ → $U(P,f) = 1, L(P,f) = 0$ → $\inf U = 1 \neq 0 = \sup L$。

**ML 关联**：病态函数的不可积性 → Lebesgue 积分的动机。
</details>

### Q6.2（微积分基本定理）
$F(x) = \int_a^x f(t)dt$ 证明 $F' = f$（$f$ 连续时）。

<details><summary>解（思路）</summary>

$$\frac{F(x+h) - F(x)}{h} = \frac{1}{h}\int_x^{x+h} f(t)dt$$

由 MVT for integrals: $\int_x^{x+h} f(t)dt = h \cdot f(c_h)$（某个 $c_h \in [x,x+h]$）。

$h \to 0 \Rightarrow c_h \to x \Rightarrow f(c_h) \to f(x)$（$f$ 连续）。
</details>

---

## 第 7 章 · 函数序列

### Q7.1（一致收敛）★
$f_n(x) = x^n$ 在 $[0,1]$ 上逐点收敛但不一致收敛。

<details><summary>解</summary>

逐点极限：$f(x) = \begin{cases} 0 & x < 1 \\ 1 & x = 1 \end{cases}$（不连续）。

但 $f_n$ 连续 → 如果一致收敛, 极限必须连续 → 矛盾。

所以不一致收敛。

**ML 关联**：神经网络的 training/validation gap 类似不一致收敛。
</details>

### Q7.2（Stone-Weierstrass）★
任何 $[0,1]$ 上的连续函数可用多项式一致逼近。

<details><summary>解（思路：Bernstein 多项式）</summary>

$$B_n(f)(x) = \sum_{k=0}^n f(k/n)\binom{n}{k}x^k(1-x)^{n-k}$$

可以证明 $\|B_n(f) - f\|_\infty \to 0$。

**ML 关联**：**Universal Approximation Theorem** 的祖先。
</details>

---

## 第 8 章 · 特殊函数

### Q8.1（$e$ 的无理性）
证明 $e = \sum 1/n!$ 是无理数。

<details><summary>解（思路）</summary>

设 $e = p/q$。则 $q! \cdot e$ 是整数。但

$$q! \cdot e = q!\sum_{n=0}^q \frac{1}{n!} + q!\sum_{n=q+1}^\infty \frac{1}{n!}$$

前一部分是整数。后一部分：

$$0 < q!\sum_{n=q+1}^\infty \frac{1}{n!} < \frac{1}{q+1} + \frac{1}{(q+1)^2} + \cdots = \frac{1}{q}$$

当 $q \geq 2$ 时 $0 < \text{后一部分} < 1$，不是整数——矛盾。
</details>

---

## 综合大题

### Q-Final ★（机器学习中的 Arzelà-Ascoli）
用 Arzelà-Ascoli 定理证明：一族 Lipschitz 常数 $\leq L$ 的 $[0,1] \to [0,1]$ 函数有紧致的闭包（在一致拓扑下）。

<details><summary>解</summary>

**验证 Arzelà-Ascoli 三条件**：
1. **一致有界**：$f([0,1]) \subset [0,1]$ ✓
2. **等度连续**：Lipschitz $\leq L$ $\Rightarrow |f(x) - f(y)| \leq L|x-y|$, 取 $\delta = \epsilon/L$ 对所有 $f$ 成立 ✓
3. **$[0,1]$ 紧致** ✓

由 Arzelà-Ascoli：每个序列有一致收敛子序列 → 闭包紧致。

**ML 关联**：这就是**泛化界**中覆盖数 (covering number) 的推导基础——神经网络假设空间的"大小"用等度连续 + 有界控制。
</details>
