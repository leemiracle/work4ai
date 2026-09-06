# Cambridge Part IB Optimisation · 习题集

> **来源**：Cambridge Tripos Past Papers + Boyd 习题 + 自编

---

## 第 1 章 · 线性规划

### Q1.1（基础）
用图解法求 $\max 3x + 2y$ s.t. $x + y \leq 4$, $x \leq 3$, $y \leq 2$, $x,y \geq 0$。

<details><summary>解</summary>

可行域顶点：$(0,0), (3,0), (3,1), (2,2), (0,2)$。
- $(0,0)$: $0$
- $(3,0)$: $9$
- $(3,1)$: $11$ ← 最优
- $(2,2)$: $10$
- $(0,2)$: $4$

最优解 $(3,1)$，值 $11$。约束 $x+y \leq 4$ 活跃。
</details>

### Q1.2（中等）
写出 $\min c^Tx$ s.t. $Ax \geq b$, $x \geq 0$ 的对偶问题，并解释弱对偶。

<details><summary>解</summary>

对偶：$\max b^Ty$ s.t. $A^Ty \leq c$, $y \geq 0$。

弱对偶：对任意原可行 $x$ 和对偶可行 $y$，$b^Ty \leq c^Tx$。
证明：$b^Ty \leq (Ax)^Ty = x^T(A^Ty) \leq x^Tc = c^Tx$（用 $Ax \geq b$, $A^Ty \leq c$, $x,y \geq 0$）。

**ML 关联**：SVM 对偶 = QP 对偶，见 [CME 364A](../../stanford-math-courses/cme364A_convex_optimization/)。
</details>

### Q1.3（中等）
Klee-Minty 反例说明单纯形法可以走 $2^n - 1$ 步。描述其构造思想。

<details><summary>解</summary>

Klee-Minty (1972)：在 $n$ 维立方体上稍作扰动，使单纯形法遍历所有 $2^n$ 个顶点。这证明单纯形法**理论最坏指数复杂度**，但实际中（平均情形）是 $O(n)$ 步——Simplex 的"反常效率"是实践奇迹。
</details>

---

## 第 2 章 · KKT 与对偶

### Q2.1（基础）
求 $\min x^2 + y^2$ s.t. $x + y = 1$ 的 KKT 解。

<details><summary>解</summary>

$\mathcal{L} = x^2 + y^2 + \nu(x + y - 1)$。
$\nabla = 0$: $2x + \nu = 0$, $2y + \nu = 0$ → $x = y$。
$x + y = 1$ → $x = y = 0.5$, $\nu = -1$。
最优值 $0.5$。
</details>

### Q2.2（中等）
求 $\min x^2 + y^2$ s.t. $x + y \geq 1$ 的 KKT 解，并解释互补松弛。

<details><summary>解</summary>

$\mathcal{L} = x^2 + y^2 - \lambda(x + y - 1)$, $\lambda \geq 0$。
$\nabla = 0$: $2x - \lambda = 0$, $2y - \lambda = 0$ → $x = y = \lambda/2$。
互补松弛：$\lambda(x + y - 1) = 0$。
若 $\lambda = 0$：$x = y = 0$，但 $0 + 0 < 1$ 矛盾。
故 $\lambda > 0$，$x + y = 1$，$x = y = 0.5$，$\lambda = 1$。

约束活跃，$\lambda = 1$ = 影子价格（放宽约束到 $x + y \geq 0.99$，目标降约 $0.01$）。
</details>

### Q2.3（开放）
KKT 互补松弛如何解释 Lasso 的稀疏性？

<details><summary>提示</summary>

Lasso: $\min \frac{1}{2n}\|Xw-y\|^2 + \lambda\|w\|_1$。$\ell_1$ 范数 $|w_i|$ 在 $w_i = 0$ 处不可微，其次梯度 $g_i \in [-1, 1]$。

KKT（次梯度版）：$\frac1n X_i^T(Xw-y) + \lambda g_i = 0$。若 $|\frac1n X_i^T(Xw-y)| < \lambda$，则 $w_i = 0$（次梯度 $g_i$ 吸收梯度）→ **自动稀疏**。而 $\ell_2$ 正则的 Ridge 不行（$w_i$ 只是缩小不到 0）。

详见 [Stanford CME 364A](../../stanford-math-courses/cme364A_convex_optimization/)。
</details>

### Q2.4（开放）
零和博弈的 Nash 均衡与 LP 对偶有什么关系？

<details><summary>提示</summary>

两人零和博弈的支付矩阵 $A$：行玩家 $\max_v \min_i \sum_j A_{ij} p_j$，列玩家 $\min_u \max_j \sum_i A_{ij} q_i$。

minimax 定理 = LP 强对偶。Nash 均衡 = LP 对偶的解。von Neumann 1928 → LP 对偶的雏形。

**ML 关联**：GAN 的训练 = minimax 博弈（生成器 vs 判别器）。
</details>

### Q2.5（开放 — RLHF）
DPO 如何用凸优化"绕过"RLHF 的非凸性？

<details><summary>提示</summary>

RLHF = RL（PPO）+ reward model，两阶段非凸。DPO（[2305.18290](https://arxiv.org/abs/2305.18290)）用 Bradley-Terry 模型把偏好建模凸化：$\mathcal{L} = -\log\sigma(\beta(\Delta_w - \Delta_l))$，logistic loss 对 $\Delta$ 凸。

但仍需 SGD 训练神经网络，所以只是"部分凸化"。详见 [CME 364A](../../stanford-math-courses/cme364A_convex_optimization/) notes.md 应用层。
</details>
