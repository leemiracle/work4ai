# Stanford CME 364A · 习题集（精选 + 解题思路）

> **来源**：Boyd & Vandenberghe *Convex Optimization* 课后习题 + 自编
> **参考**：[web.stanford.edu/~boyd/cvxbook](https://web.stanford.edu/~boyd/cvxbook)

---

## 第 1 章 · 凸集与凸函数

### Q1.1（基础）
判断以下集合是否凸：
(a) $\{x \in \mathbb{R}^2 : x_1^2 + x_2^2 \leq 1\}$（单位圆盘）
(b) $\{x \in \mathbb{R}^2 : x_1 x_2 \geq 1, x_1 > 0\}$
(c) $\{X \in \mathbb{S}^2 : X \succeq 0\}$（半正定锥）

<details><summary>解</summary>

(a) 凸。$\|x\|_2 \leq 1$ 是范数球（凸集）。
(b) 凸。这是双曲线的一支——可验证它是凸集（$xy \geq 1$ 在 $x>0$ 时上水平集是凸的）。
(c) 凸。半正定锥是凸锥：$X, Y \succeq 0 \Rightarrow \theta X + (1-\theta)Y \succeq 0$（特征值非负保持）。

**ML 关联**：(c) 是 SDP（半正定规划）的可行域。
</details>

### Q1.2（基础）
用二阶条件验证 $f(x) = -\log x$（$\text{dom} = \mathbb{R}_{++}$）是凸函数。

<details><summary>解</summary>

$f'(x) = -1/x$，$f''(x) = 1/x^2 > 0$（$\forall x > 0$）。二阶条件 $f'' \geq 0$ 满足，故凸。实际上是严格凸。

**ML 关联**：$-\log$ 是交叉熵损失 / KL 散度的核心。
</details>

### Q1.3（中等）
证明：$f(x) = \log\left(\sum_{i=1}^m e^{a_i^T x + b_i}\right)$ 是凸函数（log-sum-exp）。

<details><summary>解</summary>

**方法 1（上确界）**：$\log\sum e^{z_i} = \sup_{u \geq 0, \mathbf{1}^Tu=1} u^Tz$（由凸共轭 / Gibbs 不等式），是仿射函数的上确界 → 凸。

**方法 2（Hessian）**：$\nabla^2 f = \frac{1}{(\sum e^{z_i})^2}\left[(\sum e^{z_i})\text{diag}(e^{z_i} a_i a_i^T) - (e^{z_i}a_i)(e^{z_i}a_i)^T\right]$，可证半正定（Cauchy-Schwarz）。

**ML 关联**：log-sum-exp = softmax + cross-entropy 的光滑 max，是 logistic 回归多分类损失。
</details>

---

## 第 2 章 · 拉格朗日对偶与 KKT

### Q2.1（基础）
求 $\min x^2$ s.t. $x \geq 1$ 的 KKT 条件并求解。

<details><summary>解</summary>

约束写成 $1 - x \leq 0$。拉格朗日函数：$\mathcal{L} = x^2 + \lambda(1 - x)$。

KKT：
1. 平稳性：$2x - \lambda = 0 \Rightarrow \lambda = 2x$
2. 原可行：$1 - x \leq 0 \Rightarrow x \geq 1$
3. 对偶可行：$\lambda \geq 0$
4. 互补松弛：$\lambda(1-x) = 0$

若 $\lambda = 0$：$x = 0$，但 $x \geq 1$ 矛盾。故 $\lambda > 0$，则 $x = 1$，$\lambda = 2$。

最优解 $x^\star = 1$，$f^\star = 1$。

**ML 关联**：投影梯度 = 把约束当"墙"。
</details>

### Q2.2（中等 — SVM 对偶推导）
对软间隔 SVM $\min \frac12\|w\|^2 + C\sum\xi_i$ s.t. $y_i(w^Tx_i+b)\geq 1-\xi_i$, $\xi_i\geq 0$，推导对偶问题。

<details><summary>解</summary>

拉格朗日函数（乘子 $\alpha_i \geq 0$ 对分类约束，$\mu_i \geq 0$ 对 $\xi_i \geq 0$）：
$$\mathcal{L} = \frac12\|w\|^2 + C\sum\xi_i - \sum\alpha_i[y_i(w^Tx_i+b)-1+\xi_i] - \sum\mu_i\xi_i$$

驻点条件：
- $\partial/\partial w = 0 \Rightarrow w = \sum\alpha_i y_i x_i$
- $\partial/\partial b = 0 \Rightarrow \sum\alpha_i y_i = 0$
- $\partial/\partial\xi_i = 0 \Rightarrow C - \alpha_i - \mu_i = 0 \Rightarrow \alpha_i \leq C$

代回得对偶：
$$\max_\alpha \sum\alpha_i - \frac12\sum_{ij}\alpha_i\alpha_j y_i y_j x_i^Tx_j \quad \text{s.t.} \quad 0 \leq \alpha_i \leq C,\ \sum\alpha_i y_i = 0$$

**关键差异**（vs 硬间隔）：多了上界 $\alpha_i \leq C$。$\alpha_i = C$ 对应的样本是**间隔违例**。
</details>

### Q2.3（中等）
解释 KKT 互补松弛 $\alpha_i^\star[y_i(w^Tx_i+b)-1+\xi_i] = 0$ 在 SVM 中的物理意义。

<details><summary>解</summary>

- $\alpha_i \in (0, C)$：$\xi_i = 0$ 且 $y_i(w^Tx_i+b) = 1$ → 严格在间隔边界上的**支持向量**
- $\alpha_i = 0$：样本对 $w$ 无贡献（被正确分类且在间隔外）
- $\alpha_i = C$：$\xi_i > 0$ 可能有 → **间隔违例**或边界内的样本

→ SVM 的稀疏性来自大部分 $\alpha_i = 0$。
</details>

---

## 第 3 章 · 算法

### Q3.1（基础）
对 $f(x) = \frac12 x^T A x$（$A = \text{diag}(100, 1)$），分析 GD 的条件数 $\kappa$ 和收敛速率。

<details><summary>解</summary>

特征值 $\lambda_1 = 100, \lambda_2 = 1$。条件数 $\kappa = L/m = 100$。

强凸收敛速率：$f(x_k) - f^\star \leq (1 - 1/\kappa)^k (f(x_0) - f^\star)$。

$\kappa$ 大 → 沿"窄方向"震荡，沿"宽方向"慢爬——**病态问题**。

**ML 关联**：Hessian 病态是深度学习训练慢的元凶。Adam 用对角预条件部分缓解。
</details>

### Q3.2（中等）
证明：对 $L$-平滑凸函数，GD 固定步长 $\eta = 1/L$ 满足 $f(x_k) - f^\star \leq \frac{L\|x_0 - x^\star\|^2}{2k}$。

<details><summary>解</summary>

由 $L$-平滑：$f(y) \leq f(x) + \nabla f(x)^T(y-x) + \frac{L}{2}\|y-x\|^2$。

代入 $y = x_{k+1} = x_k - \frac1L\nabla f(x_k)$：
$$f(x_{k+1}) \leq f(x_k) - \frac{1}{2L}\|\nabla f(x_k)\|^2$$

由凸性 $f^\star \geq f(x_k) + \nabla f(x_k)^T(x^\star - x_k) \geq f(x_k) - \|\nabla f(x_k)\|\|x_k - x^\star\|$。

结合并对 $k$ 求和（telescoping）得 $O(1/k)$ 界。
</details>

### Q3.3（开放）
Adam 的有效步长如何随训练自适应？为什么 Adam 对稀疏梯度友好？

<details><summary>提示</summary>

考虑 $v_t = \beta_2 v_{t-1} + (1-\beta_2)g_t^2$。对稀疏梯度（很多 $g_t = 0$），$v_t$ 趋小，$\eta/\sqrt{v_t}$ 趋大——**对稀疏参数自动放大步长**。这是 Adam 在 NLP/CV 训练中优于 SGD 的关键。

进一步阅读：Reddi et al. [1804.04825](https://arxiv.org/abs/1804.04825) 指出 Adam 在凸设定可能不收敛（AMSGrad 修复）。
</details>

### Q3.4（开放）
比较 LP 松弛 + rounding 与整数规划的精度-效率权衡，举一个 ML 应用。

<details><summary>提示</summary>

例：k-means 聚类的 LP 松驰（SDP relaxation）。整数解的 0-1 矩阵 $X$（每行恰好一个 1）松弛为 $X \succeq 0$, $X\mathbf{1}=\mathbf{1}$, $X_{ii}=1$。LP 松弛多项式时间，rounding（如随机化）给近似比保证。见 ETH 401-3901 的组合优化视角。
</details>

### Q3.5（开放 — RLHF）
DPO 损失是凸的吗？为什么把 RLHF 转化为 DPO 后训练更稳定？

<details><summary>提示</summary>

DPO 损失 $\mathcal{L} = -\log\sigma(\beta(\Delta_w - \Delta_l))$ 对 $\Delta = \log\pi_\theta - \log\pi_{\text{ref}}$ 是凸的（logistic loss 凸）。但 $\log\pi_\theta(y|x)$ 对 $\theta$（神经网络参数）非凸——所以 DPO 只是**部分凸化**，仍需 SGD 训练。稳定性来自：消除了 RLHF 的 reward model + PPO 两阶段，减少非凸性来源。详见 [2305.18290](https://arxiv.org/abs/2305.18290) ⚠️（具体稳定性分析需查最新 follow-up）。
</details>
