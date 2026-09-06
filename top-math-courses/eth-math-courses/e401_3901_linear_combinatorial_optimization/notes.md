# ETH 401-3901 · 费曼三层讲透：线性与组合优化

> **教材**：Matoušek & Gärtner, *Understanding and Using Linear Programming*；Vanderbei *LP*（免费 PDF）
> **教授**：Rico Zenklusen
> **特色**：ETH 优化核心课——**LP / ILP / 网络流 / 次模优化**

---

## 🧠 直觉层

| 概念 | 比喻 |
|---|---|
| **整数规划（ILP）** | "顶点必须是整数格点"——多面体上的离散优化 |
| **LP 松弛** | "先不管整数约束，求连续最优，再四舍五入"——rounding |
| **分支定界** | "把搜索树分成两半（x=0 或 x=1），用 LP 松弛剪枝" |
| **割平面** | "往多面体切一刀，砍掉非整数解"——Gomory 割 |
| **最大流** | "水管网络里最多流多少水"——Ford-Fulkerson |
| **最小割** | "切断源到汇的最小代价"=最大流（强对偶）|
| **匹配** | "配对游戏"——二部图匹配 = LP（Hall 定理）|
| **次模函数** | "离散版的凸函数"——边际递减 |

> **一句话总结**：**组合优化 = "LP 松弛 + rounding 或 分支定界 + 割平面"**。核心思想是把 NP-hard 的整数问题松弛成多项式时间的 LP，用 LP 解做近似。

---

## 🧮 数学层

### 1. 整数线性规划（ILP）

$$\min c^Tx \quad \text{s.t.} \quad Ax \leq b, \; x \in \mathbb{Z}^n$$

**NP-hard**（旅行商、装箱、图着色等）。

### 2. LP 松弛 ★

$$\min c^Tx \quad \text{s.t.} \quad Ax \leq b, \; x \geq 0 \quad (\text{去掉整数约束})$$

LP 松弛给 ILP 的**下界**（min 问题）。

**近似比**：若 rounding 后的目标 $\leq \alpha \cdot \text{LP}$，则算法有 $\alpha$-近似。

### 3. 分支定界（Branch and Bound）★

1. 解 LP 松弛，得下界 $z_{LP}$
2. 若 $x_{LP}$ 已整数 → 最优
3. 否则选一个分数变量 $x_i$，分支：$x_i \leq \lfloor x_i \rfloor$ 和 $x_i \geq \lceil x_i \rceil$
4. 递归，用 LP 松弛剪枝（若 $z_{LP} \geq$ 当前最优，剪掉）

### 4. 割平面法（Cutting Planes / Gomory）

从 LP 松弛解生成**有效不等式**（割），砍掉非整数顶点：
$$\sum_j \hat{a}_j x_j \geq \lceil \hat{b} \rceil \quad \text{(Gomory 割)}$$

逐步加割直到 LP 解为整数。**收敛有限步**（Gomory 1958）。

### 5. 网络流

#### 最大流
$$\max |f| \quad \text{s.t.} \quad \begin{cases} 0 \leq f_e \leq c_e & \text{(容量)} \\ \sum_{\text{in}} f = \sum_{\text{out}} f & \text{(流量守恒)} \end{cases}$$

#### 最大流-最小割定理 ★
$$\max_{\text{flow}} |f| = \min_{\text{cut}} \sum_{e \in \text{cut}} c_e$$

> **这是 LP 强对偶的特殊情况！** Ford-Fulkerson 算法 = 增广路径法。

### 6. 二部图匹配

最大匹配 = 特殊的最大流（源连左部、右部连汇，中间容量 1）。

**König 定理**（二部图）：最大匹配数 = 最小顶点覆盖数（强对偶的体现）。

### 7. 次模函数

$f: 2^V \to \mathbb{R}$ **次模**：$\forall A \subseteq B, v \notin B$:
$$f(A \cup \{v\}) - f(A) \geq f(B \cup \{v\}) - f(B) \quad \text{(边际递减)}$$

> **离散凸性**：次模 = 离散凸函数。最小化次模函数多项式时间（与连续凸优化类比）。

**ML 关联**：特征选择（覆盖函数）、影响力最大化（社交网络）、聚类。

---

## 💻 代码层

```python
import numpy as np
from scipy.optimize import linprog

# ILP 通过 LP 松弛 + rounding (近似)
# 例: 0-1 背包 max 60x1 + 100x2 + 120x3  s.t. 10x1+20x2+30x3 ≤ 50, x∈{0,1}
# LP 松弛
c = [-60, -100, -120]  # max → min(-c)
A_ub = [[10, 20, 30]]; b_ub = [50]
res = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=[(0,1)]*3)
print(f"LP 松弛解: {np.round(res.x, 2)}, 值: {-res.fun:.1f}")
# 可能非整数 → rounding

# 精确 ILP (用 pulp 或 scipy.milp)
from scipy.optimize import milp, LinearConstraint, Bounds
res_ilp = milp(c, constraints=LinearConstraint(A_ub, -np.inf, b_ub),
               integrality=[1,1,1], bounds=Bounds(0, 1))
print(f"ILP 解: {res_ilp.x}, 值: {-res_ilp.fun:.1f}")
```

### 最大流（Ford-Fulkerson 简化）

```python
def max_flow_bfs(capacity, s, t):
    """BFS 找增广路径 (Edmonds-Karp)"""
    n = len(capacity); flow = np.zeros_like(capacity)
    while True:
        # BFS 找 s→t 路径
        parent = [-1]*n; parent[s] = s; queue = [s]
        while queue and parent[t] == -1:
            u = queue.pop(0)
            for v in range(n):
                if parent[v] == -1 and capacity[u,v] - flow[u,v] > 0:
                    parent[v] = u; queue.append(v)
        if parent[t] == -1: break  # 无增广路径
        # 找瓶颈容量
        bottleneck = float('inf'); v = t
        while v != s:
            u = parent[v]; bottleneck = min(bottleneck, capacity[u,v]-flow[u,v]); v = u
        v = t
        while v != s:
            u = parent[v]; flow[u,v] += bottleneck; flow[v,u] -= bottleneck; v = u
    return flow, sum(flow[s])
```

---

## ⚠️ 不足层

| 局限 | 说明 |
|---|---|
| **ILP 是 NP-hard** | 一般 ILP 无多项式算法，依赖分支定界（最坏指数）|
| **LP 松弛可能松** | 整数间隙（integrality gap）大时 rounding 差 |
| **割平面收敛慢** | Gomory 割理论有限步，实际需大量割 |
| **网络流要求特殊结构** | 一般图问题不能直接转流 |
| **次模最大化 NP-hard** | 只有最小化多项式时间（最大化有 $(1-1/e)$ 贪心近似）|

---

## 🔬 应用层

1. **特征选择 = 次模优化**：稀疏回归、特征覆盖
2. **设施选址 = ILP**：k-median, k-center
3. **最大流 → 图分割、社区检测**
4. **匹配 → 推荐系统、稳定婚姻**
5. **TSP / VRP → 物流路径规划**
6. **次模 → 影响力最大化**（Kempe-Kleinberg-Tardos 2003）

---

## 🆕 2024-2026 最新研究

- **ML + 组合优化**：GNN 预测分支变量（MILP 加速 10-100×）
- **TSP 破纪录**：2024 的 Concorde 求解更多 TSP 实例
- **次模神经网络**：用次模函数设计可解释 ML
- **量子优化**：QAOA 求解组合问题（尚处早期）

---

## 📚 参考结构

| 章 | 主题 | 重要性 |
|---|---|---|
| 1-3 | LP 建模与单纯形法 | ★★ |
| 4-5 | **LP 对偶与强对偶** | ★★★ |
| 6-7 | **ILP + 分支定界** | ★★★ |
| 8 | Gomory 割平面 | ★★ |
| 9-10 | **网络流 + 最大流最小割** | ★★★ |
| 11 | 匹配 | ★★ |
| 12 | 次模优化 | ★★ |

---

## 与 work4ai 讲透系列的交叉

- **讲透 LP 对偶** → SVM 对偶推导（[CME 364A](../../stanford-math-courses/cme364A_convex_optimization/)）
- **讲透图算法**：最大流 → 图分割 / GNN
- **讲透组合优化 + ML**：GNN 辅助 ILP（2024 前沿）
