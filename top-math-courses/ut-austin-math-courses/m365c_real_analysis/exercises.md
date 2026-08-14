# UT Austin M 365C · 习题集

> **分级**：⭐ 基础 / ⭐⭐ 中等 / ⭐⭐⭐ 开放

---

### Q1 ⭐（开集/闭集）
$\{1/n : n \in \mathbb{N}\}$ 是 $\mathbb{R}$ 中的开集还是闭集？

<details><summary>解</summary>
**既不开也不闭**（作为集合本身）：
- 不开: $1/1 = 1$ 不是内点（$(1-\epsilon, 1+\epsilon)$ 包含 $1/n$ 外的点）
- 不闭: 极限点 $0 \notin S$

但 $S \cup \{0\}$ 是闭集。

**ML 关联**: 离散数据点 + 极限点 → 紧致集（加极限点后）。
</details>

### Q2 ⭐⭐（紧致性 + 极值定理）
$f(x, y) = x^2 + y^2 - xy$ 在 $\{(x,y) : x^2 + y^2 \leq 1\}$ 上取最小值吗？

<details><summary>解</summary>
1. **定义域紧致**: $x^2+y^2 \leq 1$ = 闭单位圆盘 → 有界+闭 → 紧致 (Heine-Borel) ✓
2. **$f$ 连续**: 多项式 → 连续 ✓
3. **极值定理**: 紧致集上连续函数取最值 → $f$ 有最小值 ✓

$\nabla f = (2x - y, 2y - x) = 0 \Rightarrow x = y = 0$。$f(0,0) = 0$ → 最小值。

**ML 关联**: 权重衰减约束 $\|\theta\| \leq R$ = 紧致集 → loss 最小值存在。
</details>

### Q3 ⭐⭐（MVT）
证明: $\sqrt{1+x} < 1 + x/2$ for $x > 0$。

<details><summary>解</summary>
MVT on $f(t) = \sqrt{1+t}$ on $[0, x]$: $\exists c \in (0,x)$:
$$\frac{\sqrt{1+x} - 1}{x} = f'(c) = \frac{1}{2\sqrt{1+c}} < \frac{1}{2}$$
所以 $\sqrt{1+x} < 1 + x/2$ ✓

**ML 关联**: 不等式证明 = 分析基本功 → ML 论文中的理论界。
</details>

### Q4 ⭐⭐⭐（开放：紧致性与正则化）
用紧致性理论解释为什么权重衰减 $L(\theta) + \lambda\|\theta\|^2$ 保证最优解存在。

<details><summary>解</summary>
1. **无正则化**: 参数空间 $\mathbb{R}^d$ 不紧致 → inf 可能不可达（如 $L(\theta) = e^{-\theta^2}$, inf = 0 但无最小值点）。
2. **有权重衰减**: 最小化 $L(\theta) + \lambda\|\theta\|^2$。

等价视角: 设正则化后最优值为 $L^*$。则最优 $\theta$ 满足 $\|\theta\|^2 \leq (L^* - L(0))/\lambda =: R^2$（否则正则化项太大）。

所以搜索区域 = $\{\theta : \|\theta\| \leq R\}$ = **紧致集**（有界+闭）。

$L(\theta)$ 连续 → 紧致集上取最小值 → **最优解存在** ✓

**深层**: 权重衰减不仅是正则化技巧——它从拓扑上保证了优化的良定义性。
</details>

### Q5 ⭐（级数收敛）
$\sum_{n=1}^\infty \frac{(-1)^n}{\sqrt{n}}$ 收敛吗？绝对收敛吗？

<details><summary>解</summary>
**收敛**: $1/\sqrt{n} \searrow 0$ → Leibniz 判别法 → 收敛 ✓
**不绝对收敛**: $\sum 1/\sqrt{n}$ 发散（$p$-级数 $p = 1/2 < 1$）→ 条件收敛。
</details>

### Q6 ⭐⭐⭐（开放：一致收敛与泛化）
$f_n \rightrightarrows f$ 保证 $\int f_n \to \int f$。类比到 ML 中"训练损失一致收敛 → 泛化"。

<details><summary>解（类比）</summary>
| 数学 | ML |
|---|---|
| $f_n$ | 经验损失 $\hat{L}_n(\theta)$ |
| $f$ | 真实损失 $L(\theta)$ |
| $f_n \rightrightarrows f$ | $\sup_\theta |\hat{L}_n(\theta) - L(\theta)| \to 0$ |
| $\int f_n \to \int f$ | $\hat{L}_n(\hat\theta_n) \to L(\theta^*)$ |

**关键定理**: 一致收敛 + 紧致假设空间 → 经验风险最小化（ERM）一致。

$\sup_\theta |\hat{L}_n - L| \leq O(\sqrt{d \log(1/\epsilon) / n})$（覆盖数界）

→ 样本量 $n \gg d$ 时泛化。

**深度联系**: 分析学的一致收敛定理 = 机器学习的泛化保证。
</details>
