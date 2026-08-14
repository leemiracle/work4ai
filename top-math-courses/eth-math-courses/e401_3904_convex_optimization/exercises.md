# ETH 401-3904 · 习题集（Bubeck 复杂度视角 + Boyd 共享）

> 核心凸优化习题（KKT/SVM/对偶）见 [Stanford CME 364A exercises.md](../../stanford-math-courses/cme364A_convex_optimization/exercises.md)。本习题集聚焦 ETH 特色：**算法复杂度**。

---

## 第 1 章 · 复杂度下界

### Q1.1（基础）
$L$-平滑凸函数上，GD 的迭代复杂度是多少？要达 $\epsilon$ 精度需几步？

<details><summary>解</summary>

$f(x_k) - f^\star \leq \frac{L\|x_0-x^\star\|^2}{2k}$。要 $\leq\epsilon$ 需 $k \geq \frac{L\|x_0-x^\star\|^2}{2\epsilon} = O(L/\epsilon)$ 步。
</details>

### Q1.2（中等）
证明 Nesterov 加速在一维二次函数 $f(x) = \frac{L}{2}x^2$ 上达到 $O(1/k^2)$ 收敛。

<details><summary>解</summary>

Nesterov 迭代：$y_k = x_k + \frac{k-1}{k+2}(x_k - x_{k-1})$，$x_{k+1} = y_k - \frac{1}{L}Ly_k = 0$。一步收敛（因为 $f$ 已是二次精确）。

对一般 $L$-平滑凸函数，用势能函数 $\Phi_k = k^2(f(x_k) - f^\star) + \frac{L}{2}\|x_k - x^\star\|^2$ 证明 $\Phi_k$ 单调递减，得 $f(x_k) - f^\star = O(\Phi_0 / k^2) = O(L/k^2)$。
</details>

### Q1.3（开放）
为什么 Nesterov 加速在 SGD（随机梯度）中不如在 GD 中有效？

<details><summary>提示</summary>

加速的 $O(1/k^2)$ 依赖**精确梯度**。SGD 的方差 $\sigma^2$ 导致加速方法的不动点不稳定——动量累积噪声。理论上 SGD 的 $O(1/\sqrt{k})$ 下界不变（Nemirovski-Yudin 1983）。需要方差缩减（SVRG）才能恢复加速。

**ML 关联**：深度学习实践中 Adam 比 Nesterov + SGD 更常用，部分因为噪声鲁棒性。
</details>

### Q1.4（中等 — 强凸）
$\kappa = L/m$ 条件数下，GD 和 Nesterov 加速的迭代复杂度分别是多少？

<details><summary>解</summary>

- GD：$O(\kappa\log(1/\epsilon))$（线性收敛率 $1 - 1/\kappa$）
- Nesterov：$O(\sqrt{\kappa}\log(1/\epsilon))$（收敛率 $1 - 1/\sqrt{\kappa}$）

$\kappa = 10^4$ 时：GD 需 $\sim 10^4$ 步，Nesterov 只需 $\sim 100$ 步——**百倍加速**。
</details>

### Q1.5（开放 — 非凸）
非凸优化（深度学习）有类似的信息论下界吗？

<details><summary>提示</summary>

**部分有**。非凸 $L$-平滑的 lower bound：找 $\epsilon$-驻点需 $\Omega(1/\epsilon^2)$ 步（Cartis-Gould-Toint 2010）。但找全局最优是 NP-hard。

实际中 SGD 找到的不是全局最优而是"宽局部最小"（flat minima），泛化更好——这与损失景观（loss landscape）的随机矩阵理论有关，见 [Oxford C7.1](../../oxford-math-courses/partC_c7_1_random_matrix_theory/)。⚠️ 具体结果跟踪最新理论。
</details>

---

## 第 2 章 · Boyd 共享习题（见 CME 364A）

SVM 对偶推导、KKT 互补松弛、Lasso 稀疏性、RLHF/DPO 凸化等核心习题，请参阅：
- [Stanford CME 364A exercises.md](../../stanford-math-courses/cme364A_convex_optimization/exercises.md)

---

## 第 3 章 · ETH 特色：分布式与在线优化

### Q3.1（开放）
联邦学习中，通信复杂度与本地计算复杂度的权衡如何用凸优化理论刻画？

<details><summary>提示</summary>

FedAvg = 本地 GD + 周期通信。凸损失下：$T$ 轮通信 + $\tau$ 本地步 → 误差 $O(1/\sqrt{T\tau})$（Non-IID 有额外项）。通信下界：$\Omega(1/\epsilon^2)$ bits（信息论）。加速：量化 + 稀疏化。⚠️ 精确界见最新 federated learning 理论文献。
</details>
