# Cambridge Part II · 费曼三层讲透：高级数值分析

> **教材**：Iserles, *A First Course in the Numerical Analysis of Differential Equations* (2nd ed)
> **特色**：Cambridge Part II（四年级）——**Krylov 深入 / 谱方法 / 刚性 PDE / 有限元理论**

---

## 🧠 直觉层

| 概念 | 比喻 |
|---|---|
| **谱方法** | "用全局三角/多项式近似"——精度 $O(e^{-n})$（指数收敛）|
| **CG 收敛** | "$n$ 步精确（理论）→ 实际 $\ll n$ 步"——条件数决定速度 |
| ** preconditioning** | "先做变换改善条件数，再求解"——$M^{-1}A$ 代替 $A$ |
| **有限元误差估计** | "$h$ 减半，误差减 $h^p$ 倍"——收束阶 |

> **一句话总结**：Part II NA = **"高阶数值方法 + 严格收束分析"**。从 Part IB 的"会算"升级到"能证明收束速度"。

---

## 🧮 数学层

### 1. Krylov 子空间深入 ★★

**CG 迭代**（对称正定 $A$）：
- 第 $k$ 步精确解 $\mathbf{x}_k$ 最小化 $\|\mathbf{x} - \mathbf{x}_*\|_A$ 在 $\mathcal{K}_k$ 上
- **Chebyshev 界**：$\|\mathbf{e}_k\|_A \leq 2\left(\frac{\sqrt{\kappa}-1}{\sqrt{\kappa}+1}\right)^k \|\mathbf{e}_0\|_A$
- 条件数 $\kappa$ 小 → 快速收束

**GMRES**（非对称）：最小化 $\|b - A\mathbf{x}_k\|$ 在 $\mathcal{K}_k$ 上。

### 2. 预处理 ★

找 $M \approx A^{-1}$，解 $M^{-1}A\mathbf{x} = M^{-1}b$，条件数改善。

**不完全 Cholesky**：$M = \tilde{L}\tilde{L}^T$（$\tilde{L}$ 保持稀疏性）。

### 3. 谱方法 ★★

**伪谱法**：用 Chebyshev 节点 $x_k = \cos(k\pi/n)$，微分矩阵 $D_n$。
$$u'(x_i) \approx \sum_j (D_n)_{ij} u(x_j)$$

**指数收敛**：若解解析，误差 $O(e^{-cn})$（vs 有限元 $O(h^p)$）。

### 4. PDE 数值方法

**抛物型**（热方程）：CFL 条件 $\Delta t \leq C\Delta x^2$（显式）/ 无条件稳定（隐式 Crank-Nicolson）。

**双曲型**（波方程/对流）：迎风格案（upwind）保稳定性。

**椭圆型**（Poisson）：FEM 的变分框架，Bramble-Hilbert 引理给误差界。

### 5. 有限元理论 ★

**Céa 引理**：$\|u - u_h\|_{H^1} \leq \frac{M}{\alpha}\|u - v_h\|_{H^1}, \forall v_h \in V_h$

→ FEM 解是 Galerkin 投影，误差 $\leq C \cdot h^p$（$p$ = 基函数阶）。

---

## 💻 代码层

```python
import numpy as np

# CG 收束速度 vs 条件数
def conjugate_gradient(A, b, max_iter=1000, tol=1e-10):
    x = np.zeros_like(b); r = b - A @ x; p = r.copy()
    residuals = []
    for k in range(max_iter):
        alpha = r @ r / (p @ A @ p)
        x += alpha * p; r_new = r - alpha * (A @ p)
        beta = (r_new @ r_new) / (r @ r)
        p = r_new + beta * p; r = r_new
        residuals.append(np.linalg.norm(r))
        if residuals[-1] < tol: break
    return x, residuals

# 测试不同条件数
for kappa in [10, 100, 1000]:
    # 构造条件数 = kappa 的 SPD 矩阵
    n = 100; eigenvalues = np.linspace(1, kappa, n)
    A = np.diag(eigenvalues); b = np.random.randn(n)
    _, res = conjugate_gradient(A, b)
    print(f"κ={kappa}: {len(res)} 步收束")
    # 验证: 步数 ∝ √κ
```

---

## ⚠️ 不足层
- 谱方法对不规则区域/间断解不友好
- 预处理器设计是"黑魔法"，无通用方案
- FEM 对高维问题（PDE 维度 > 3）遭遇维数灾难

---

## 🔬 应用层
1. **CG → 大规模线性系统**（PageRank / 推荐）
2. **谱方法 → 高精度流体仿真** → 天气/气候模型
3. **FEM → 工程仿真**（结构力学 / 电磁场）
4. **预处理 → 深度网络 Hessian 逆**（自然梯度 / K-FAC）

---

## 🆕 2024-2026
- **Neural Operator (FNO)**：用 Fourier 变换学习 PDE 解算子
- **DeepONet**：用神经网络学习无穷维算子
- **GPU CG**：cuSPARSE / cuSOLVER 的并行 Krylov 方法
- **随机化预处理**：用随机投影加速稀疏系统求解

---

## 交叉引用
- [Cambridge Part IB NA](../partIB_numerical_analysis/) — ODE/插值基础
- [UT Austin M 383E](../../ut-austin-math-courses/m383e_numerical_linear_algebra/) — 线代数值深入
- [MIT 18.085](../../mit-math-courses/18_085_computational_science/) — 差分/FEM 应用
- [ETH 401-2611](../../eth-math-courses/e401_2611_numerical_methods_cse/) — CSE 视角
