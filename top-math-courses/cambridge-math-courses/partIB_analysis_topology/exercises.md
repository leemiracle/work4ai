# Cambridge Part IB Analysis & Topology · 习题集

> **分级**：⭐ 基础 / ⭐⭐ 中等 / ⭐⭐⭐ 开放

---

### Q1 ⭐（度量空间）
证明 $d(x, y) = |x - y| / (1 + |x - y|)$ 是 $\mathbb{R}$ 上的有界度量。

<details><summary>解</summary>
1. **正定**: $d \geq 0$, $d = 0 \iff x = y$ ✓
2. **对称**: $d(x,y) = d(y,x)$ ✓
3. **三角不等式**: 函数 $t \mapsto t/(1+t)$ 单调递增 + 次可加：
   $d(x,z) = \frac{|x-z|}{1+|x-z|} \leq \frac{|x-y|+|y-z|}{1+|x-y|+|y-z|} \leq \frac{|x-y|}{1+|x-y|} + \frac{|y-z|}{1+|y-z|} = d(x,y) + d(y,z)$ ✓
4. **有界**: $d < 1$ 对所有 $x, y$ ✓
</details>

### Q2 ⭐⭐（压缩映射）
$T: [1, \infty) \to [1, \infty)$, $T(x) = 1 + 1/x$。证明 $T$ 是压缩映射并求不动点。

<details><summary>解</summary>
$T'(x) = -1/x^2$, $|T'(x)| = 1/x^2 \leq 1$ for $x \geq 1$。在 $[1, \infty)$ 上 $|T'| \leq 1$，但需 $q < 1$。

更精确: 在 $[\sqrt{2}, \infty)$ 上 $|T'| \leq 1/2$，$T$ 将 $[1, \infty)$ 映入 $[1, 2] \subset [\sqrt{2}, \infty)$。所以在 $T^2$ 的意义上压缩。

不动点: $x = 1 + 1/x \Rightarrow x^2 = x + 1 \Rightarrow x = \phi = (1+\sqrt{5})/2$ (黄金比例)。

**ML 关联**: 迭代算法收敛——优化中不动点 = 临界点。
</details>

### Q3 ⭐⭐（一致收敛）
$f_n(x) = n x e^{-nx}$ 在 $[0, 1]$ 上。$f_n \to ?$ 一致收敛吗？

<details><summary>解</summary>
逐点: $f_n(x) \to 0$ for $x > 0$, $f_n(0) = 0$。所以 $f_n \to 0$ 逐点。

$\sup |f_n|$: $f_n'(x) = n(1-nx)e^{-nx} = 0 \Rightarrow x = 1/n$。$f_n(1/n) = n \cdot (1/n) \cdot e^{-1} = e^{-1}$。

$\sup |f_n| = 1/e \not\to 0$ → **不一致收敛**。

**ML 关联**: 逐点收敛 ≠ 一致收敛，类比训练集损失 ≠ 泛化损失。
</details>

### Q4 ⭐⭐⭐（开放：压缩映射 → SGD 收敛）
用压缩映射原理证明：对 $L$-smooth 凸 $f$，学习率 $\eta < 2/L$ 时梯度下降收敛。

<details><summary>解</summary>
梯度下降迭代: $\theta_{k+1} = T(\theta_k) = \theta_k - \eta \nabla f(\theta_k)$

**压缩性**:
$\|T(\theta) - T(\theta')\| = \|(\theta - \theta') - \eta(\nabla f(\theta) - \nabla f(\theta'))\|$

由 $L$-smooth: $\nabla f$ 是 $L$-Lipschitz。利用 $L$-smoothness 的 co-coercivity:
$$\|T\theta - T\theta'\|^2 \leq (1 - \eta L(2 - \eta L)) \|\theta - \theta'\|^2$$

当 $\eta < 2/L$: $q = 1 - \eta L(2 - \eta L) < 1$ → 压缩映射。

由 Banach 不动点: $\theta_k \to \theta^*$ (唯一不动点 = 最小值)。

**收敛速率**: $\|\theta_k - \theta^*\| \leq q^{k} \|\theta_0 - \theta^*\|$ — **线性收敛**。
</details>

### Q5 ⭐⭐（紧致性）
$K \subset \mathbb{R}^n$ 紧致, $f: K \to \mathbb{R}$ 连续。证明 $f$ 一致连续。

<details><summary>解（思路）</summary>
反证法: 假设不一致连续 → $\exists \epsilon_0$, $\forall \delta > 0$, $\exists x_\delta, y_\delta$: $d(x_\delta, y_\delta) < \delta$ 但 $|f(x_\delta) - f(y_\delta)| \geq \epsilon_0$。

取 $\delta = 1/n$ → 得序列 $(x_n, y_n)$。$K$ 紧致 → 子列 $x_{n_k} \to x^* \in K$。$d(x_{n_k}, y_{n_k}) \to 0$ → $y_{n_k} \to x^*$。

$f$ 连续 → $f(x_{n_k}) \to f(x^*)$ 且 $f(y_{n_k}) \to f(x^*)$ → 矛盾。

**ML 关联**: 紧致参数空间上 loss 一致连续 → 训练稳定。
</details>

### Q6 ⭐⭐⭐（开放：拓扑数据分析）
解释为什么 $[0,1]$ 和 $(0,1)$ 不同胚（但它们都是 $\mathbb{R}$ 的子集）。

<details><summary>解</summary>
**方法 1（紧致性）**: $[0,1]$ 紧致, $(0,1)$ 不紧致。紧致性是拓扑不变量（同胚保持）→ 不同胚。

**方法 2（去点连通性）**: $[0,1] \setminus \{1/2\}$ 不连通, $(0,1) \setminus \{1/2\}$ 也不连通。但 $[0,1] \setminus \{0\} = (0,1]$ 连通, $(0,1) \setminus \{0\}$... 不适用。

更好的方法: $[0,1]$ 去掉端点 $0$: $(0,1]$ 半开区间，去掉 $1/2$ 断成两段。$(0,1)$ 去掉任何点都断成两段。

最干净: **紧致性**。$[0,1]$ 紧致，$(0,1)$ 不紧致 → 不同胚。

**ML 关联**: 流形学习——数据的拓扑不变量决定了几何结构的本质特征。
</details>
