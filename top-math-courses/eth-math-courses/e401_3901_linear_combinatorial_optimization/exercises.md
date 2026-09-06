# ETH 401-3901 · 习题集

---

### Q1.1（基础）
0-1 背包问题：$\max 60x_1 + 100x_2 + 120x_3$ s.t. $10x_1 + 20x_2 + 30x_3 \leq 50$, $x \in \{0,1\}^3$。求 LP 松弛解和 ILP 解。

<details><summary>解</summary>

LP 松弛：$x = (1, 1, 2/3)$，值 $280 - 40/3 \approx 240$。
ILP 解：$x = (1, 0, 1)$（取 1,3），值 $180$；或 $x = (0, 1, 1)$，值 $220$ ← 最优。

整数间隙：$240/220 = 1.09$（LP 松弛比 ILP 多 9%）。
</details>

### Q1.2（中等）
证明最大流-最小割定理是 LP 强对偶的特例。

<details><summary>解</summary>

最大流写成 LP：$\max \sum_v f_{sv}$ s.t. 流量守恒 + 容量约束。其对偶问题的变量对应每个顶点的势，约束对应割。强对偶 $\max|f| = \min\text{cut}$。

**ML 关联**：图分割 / 社区检测用最小割。
</details>

### Q1.3（中等）
次模函数 $f(A) = |A|$（基数）是否次模？$f(A) = \max_{i \in A} w_i$（最大值）呢？

<details><summary>解</summary>

$|A|$ 次模（边际 $= 1$ 常数，$\geq$ 满足）。

$\max_{i \in A} w_i$ 次模：$A \subseteq B$ 时加 $v$ 的边际 $\max(A\cup\{v\}) - \max(A) \geq \max(B\cup\{v\}) - \max(B)$（B 已有大元素，边际更小）。✓

**ML 关联**：影响力最大化用次模函数（覆盖函数）。
</details>

### Q1.4（开放）
LP 松弛的整数间隙在最坏情况下能多大？给一个例子。

<details><summary>提示</summary>

独立集问题：$\max \sum x_i$ s.t. $x_i + x_j \leq 1$（相邻顶点）。LP 松弛给 $x_i = 1/2$（全赋半值），间隙可达 $\Omega(n)$。

完美图（二部图）上间隙为 0（König 定理）。一般图独立集是 NP-hard。
</details>

### Q1.5（开放 — ML）
如何用 GNN 加速分支定界？2024 的最新结果如何？

<details><summary>提示</summary>

GNN 学一个策略：给定 ILP 状态，预测下一个分支变量。Gasse et al. 2019 首次用 GNN+ILP。2024 的进展：更大模型、跨问题泛化、GPU 加速 MILP（cuPDLP, SCIP-GPU）。⚠️ 具体加速比需跟踪最新论文。
</details>

### Q1.6（开放）
次模最大化有 $(1-1/e) \approx 0.632$ 近似比（贪心）。为什么这是信息论最优？

<details><summary>提示</summary>

Nemhauser-Wolsey-Fisher 1978 证明贪心达 $(1-1/e)$，且 Feige 1998 证明除非 P=NP 无法改进。$(1-1/e)$ 来自 $\lim_{k\to\infty}(1-1/k)^k = 1/e$。
</details>
