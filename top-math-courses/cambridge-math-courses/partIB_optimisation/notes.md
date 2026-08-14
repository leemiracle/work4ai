# Cambridge Part IB · 费曼三层讲透：优化（本科入门）

> **教材**：自编讲义；Boyd & Vandenberghe *Convex Optimization* 补充
> **特色**：Cambridge 本科优化入门——**LP / KKT / 单纯形法**

---

## 🧠 直觉层

| 概念 | 比喻 |
|---|---|
| **优化问题** | "在限制里找最好"——$\min f(x)$ s.t. 约束 |
| **线性规划（LP）** | "目标函数和约束都是直的"——可行域是多面体，最优在顶点 |
| **单纯形法** | "沿多面体的边跳到更优的顶点"——永远朝目标值下降的方向跳 |
| **拉格朗日乘子** | "约束的影子价格"——$\lambda$ 告诉你放宽约束能赚多少 |
| **KKT** | "拉格朗日乘子 + 互补松弛"——最优解的通关密码 |
| **对偶** | "从反面看问题"——原问题 min ↔ 对偶问题 max，强对偶时相等 |

> **一句话总结**：**LP = "可行域是多面体，最优在顶点"**。单纯形法沿边跳，永远找更优顶点。**KKT = 拉格朗日乘子 + 互补松弛**，是所有约束优化的核心。

---

## 🧮 数学层

### 1. 线性规划（LP）

$$\min c^Tx \quad \text{s.t.} \quad Ax \leq b, \; x \geq 0$$

**标准形式**：$\min c^Tx$ s.t. $Ax = b$, $x \geq 0$（加松弛变量转化）。

**几何**：可行域 = 多面体 $\{x : Ax \leq b\}$。最优解在**顶点**（极点）。

**顶点条件**：$x$ 是多面体顶点 $\iff$ $x$ 处有 $n$ 个线性独立的活跃约束。

### 2. 单纯形法 ★

1. 从一个顶点 $x_0$ 开始
2. 检查相邻顶点是否有更小目标值
3. 若有，跳到最陡下降的相邻顶点
4. 重复直到所有相邻顶点都不更优 → 当前顶点最优

**代价**：实际中 $O(n)$ 步（理论最坏 $2^n$，有反例）。

### 3. LP 对偶 ★★

**原问题**：$\min c^Tx$ s.t. $Ax \geq b$, $x \geq 0$

**对偶问题**：$\max b^Ty$ s.t. $A^Ty \leq c$, $y \geq 0$

**弱对偶**：$b^Ty \leq c^Tx$（对偶永远给下界）

**强对偶定理**（LP 的核心）：若原问题有最优解，则 $d^\star = p^\star$。

> **ML 关联**：SVM 的对偶推导 = LP 对偶的二次推广。

### 4. 拉格朗日函数与 KKT

对一般约束优化 $\min f(x)$ s.t. $g_i(x) \leq 0$, $h_j(x) = 0$：

**拉格朗日函数**：
$$\mathcal{L}(x, \lambda, \nu) = f(x) + \sum_i \lambda_i g_i(x) + \sum_j \nu_j h_j(x)$$

**KKT 条件**（凸问题 + Slater 下充要）：
1. 平稳性：$\nabla_x \mathcal{L} = 0$
2. 原可行：$g_i(x) \leq 0$, $h_j(x) = 0$
3. 对偶可行：$\lambda_i \geq 0$
4. **互补松弛**：$\lambda_i g_i(x) = 0$

> **互补松弛的直觉**：约束没激活（$g_i < 0$）→ $\lambda_i = 0$（乘子"沉默"）；约束激活（$g_i = 0$）→ $\lambda_i$ 可能非零。

### 5. 二次规划（QP）

$$\min \frac12 x^T P x + q^Tx \quad \text{s.t.} \quad Gx \leq h \quad (P \succeq 0)$$

**SVM** = 凸 QP（$P = $ 核矩阵，约束 = 间隔约束）。详见 [Stanford CME 364A](../../stanford-math-courses/cme364A_convex_optimization/notes.md)。

### 6. 凸优化入门

凸集 + 凸函数 → **局部最优 = 全局最优**。核心工具：KKT + 对偶。

---

## 💻 代码层

```python
import numpy as np
from scipy.optimize import linprog

# LP 例子: 资源分配
# max 3x + 2y  s.t.  x + y ≤ 4,  x ≤ 3,  y ≤ 2,  x,y ≥ 0
c = [-3, -2]  # linprog 做 min, 取负
A_ub = [[1, 1], [1, 0], [0, 1]]
b_ub = [4, 3, 2]
res = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=[(0, None), (0, None)])
print(f"最优解: x={res.x}, 最优值={-res.fun}")

# 单纯形法验证: 最优在顶点 (3, 1)
# 验证: 3(3) + 2(1) = 11, 约束 x+y=4 活跃, λ=2 (影子价格)
```

### 手写 KKT 检查

```python
# QP 例子: min 0.5(x² + y²) s.t. x + y ≥ 1
# KKT: x - λ = 0, y - λ = 0, x+y ≥ 1, λ(x+y-1)=0, λ≥0
# 解: x=y=λ, 2λ≥1, λ(2λ-1)=0 → λ=0.5, x=y=0.5
print("KKT 解: x=y=0.5, λ=0.5")
print("验证: f(0.5,0.5)=0.25, 约束 0.5+0.5=1 ✓ (活跃)")
```

---

## ⚠️ 不足层

| 局限 | 说明 |
|---|---|
| **单纯形法最坏指数复杂度** | Klee-Minty 反例 $2^n$ 步（实际中很少触发）|
| **KKT 对非凸只是必要条件** | 深度学习非凸，KKT 不保证全局最优 |
| **整数变量不凸** | ILP 需分支定界 + 凸松弛，见 [ETH 401-3901](../../eth-math-courses/e401_3901_linear_combinatorial_optimization/) |
| **LP 的内点法 vs 单纯形法** | 大规模 LP 用内点法（多项式时间），但单纯形法实际更快 |

---

## 🔬 应用层

1. **SVM = 凸 QP + KKT** → [Stanford CME 364A](../../stanford-math-courses/cme364A_convex_optimization/) 完整推导
2. **LP 用于资源分配、运输、排班**
3. **LP 松弛 + rounding → 近似算法**（聚类、设施选址）
4. **Lasso = QP**：$\ell_1$ 正则化 → 稀疏解
5. **LP 对偶 → 博弈论**：零和博弈的 Nash 均衡 = LP 解

---

## 🆕 2024-2026 最新研究

- **LP 内点法的 GPU 加速**：cuPDLP-C（2023-2024），GPU 上求解超大规模 LP
- **组合优化的 ML 辅助**：GNN + 分支定界加速 ILP
- **次模优化的凸松弛**：子模函数 = 离散凸函数，与连续凸优化有深刻类比

---

## 📚 参考结构

| 章 | 主题 | 重要性 |
|---|---|---|
| 1 | LP 建模与标准形式 | ★★ |
| 2 | 单纯形法 | ★★ |
| 3 | LP 对偶 | ★★★ |
| 4 | KKT 条件 | ★★★ |
| 5 | QP 与凸优化 | ★★ |

---

## 与 work4ai 讲透系列的交叉

- **讲透 SVM**：KKT 第 4 节 → [CME 364A](../../stanford-math-courses/cme364A_convex_optimization/) SVM 完整推导
- **讲透 LP 对偶**：第 3 节 → 博弈论 / 经济学
- **讲透正则化**：QP 第 5 节 → Lasso / Ridge
