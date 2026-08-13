# Stanford MATH 51 · 多变量部分章节笔记

> **教材**：Stanford 自编讲义（Custom）
> **范围**：本笔记聚焦**多变量微积分部分**（第 4-7 单元）。线代部分见其他笔记
> **特色**：线代 + 多变量并行讲授，SVD 与梯度优化有机融合
> **对照**：多变量部分 ≈ [MIT 18.02](../../mit-math-courses/18_02_multivariable_calculus/)

---

## 核心框架：MATH 51 的"梯度 + 矩阵"双线

| 概念 | 数学形式 | ML 对应 |
|---|---|---|
| **偏导 / 梯度** | $\nabla f$ | 优化方向信号 |
| **多元链式法则** | Jacobian 乘积 | 反向传播 |
| **二阶导 / Hessian** | $H = \nabla^2 f$ | 曲率 / 二阶优化 |
| **SVD + 梯度**（特色） | PCA 主成分上的梯度 | 数据降维 + 优化 |

---

## 第 1 节：多变量微分

### 1.1 偏导与梯度

$$\nabla f = \left(\frac{\partial f}{\partial x_1}, \dots, \frac{\partial f}{\partial x_n}\right)$$

$\nabla f$ = 最陡上升方向，$-\nabla f$ = **梯度下降方向**。

### 1.2 方向导数

$$D_{\hat{\mathbf{u}}}f = \nabla f \cdot \hat{\mathbf{u}}$$

### 1.3 多元链式法则 ★

$$\frac{\partial L}{\partial x_j} = \sum_i \frac{\partial L}{\partial y_i}\frac{\partial y_i}{\partial x_j}$$

矩阵形式：$\nabla_\mathbf{x} L = J^T \nabla_\mathbf{y} L$。**这是反向传播**。

---

## 第 2 节：多变量优化

### 2.1 临界点与 Hessian

$\nabla f = \mathbf{0}$ → 临界点。$H$ 正定 → 局部最小；不定 → 鞍点。

### 2.2 梯度下降

$$\mathbf{w}_{t+1} = \mathbf{w}_t - \eta\nabla f(\mathbf{w}_t)$$

Adam（[arXiv:1412.6980](https://arxiv.org/abs/1412.6980)）：加一阶矩（动量）+ 二阶矩（自适应步长）。

### 2.3 Lagrange 乘子

$$\nabla f = \lambda\nabla g \quad \text{(约束 } g = 0\text{)}$$

**ML 关联**：SVM 对偶推导、KKT 条件。

### 2.4 二阶 Taylor + Newton

$$f \approx f_0 + \nabla f^T\Delta + \frac{1}{2}\Delta^T H\Delta \implies \Delta = -H^{-1}\nabla f$$

---

## 第 3 节：多变量积分

### 3.1 重积分

$$\int\cdots\int f(\mathbf{x})\,d\mathbf{x}$$

### 3.2 ML 关联

- 概率归一化：$\int p(\mathbf{x})\,d\mathbf{x} = 1$
- 期望：$E[g(\mathbf{X})] = \int g(\mathbf{x})p(\mathbf{x})\,d\mathbf{x}$

---

## 第 4 节：SVD + 梯度（MATH 51 特色）★

MATH 51 把线代和多变量融合，关键洞察：

- **PCA** = 对数据协方差矩阵做 SVD → 找最大方差方向
- **梯度**在 PCA 主成分上分解 → 理解各方向收敛速度（条件数）
- **Newton 法** = 在 Hessian 特征基下各方向用 $1/\lambda_i$ 步长

**ML 关联**：LoRA（低秩适配）= SVD 低秩近似 + 梯度更新。

---

## 与 ML 的关联总表

| MATH 51 概念 | ML 应用 |
|---|---|
| 梯度 $\nabla f$ | SGD / Adam |
| 多元链式法则 | 反向传播 |
| Hessian | 二阶优化 / 鞍点 |
| Lagrange 乘子 | SVM |
| SVD + 梯度 | PCA + 优化 / LoRA |

---

## 代码验证

### 验证 1：数值梯度 + 梯度下降

```python
import numpy as np

def num_grad(f, w, h=1e-5):
    g = np.zeros_like(w)
    for i in range(len(w)):
        wp, wm = w.copy(), w.copy()
        wp[i] += h; wm[i] -= h
        g[i] = (f(wp) - f(wm)) / (2*h)
    return g

f = lambda w: w @ w + np.sum(np.cos(w))   # 非凸测试函数
w = np.array([2.0, 2.0])
for _ in range(500):
    w = w - 0.1 * num_grad(f, w)
print(f"优化结果: {w}, f = {f(w):.4f}")
```

### 验证 2：Jacobian 与反向传播链式法则

```python
import numpy as np

# 两层网络: z = W2 @ sigmoid(W1 @ x)
def sigmoid(z): return 1 / (1 + np.exp(-z))

W1 = np.array([[1.0, -0.5], [0.3, 0.8]])
W2 = np.array([[1.0, -1.0]])
x = np.array([0.5, 1.0])

# 前向传播
h = sigmoid(W1 @ x)
z = W2 @ h  # scalar

# Jacobian 链式法则: dz/dx = J_zh @ J_hx
J_zh = W2                          # 1×2
J_hx = np.diag(h * (1-h)) @ W1     # 2×2 (sigmoid 导数)
dz_dx = J_zh @ J_hx                # 1×2

# 数值验证
eps = 1e-7
for i in range(2):
    xp, xm = x.copy(), x.copy()
    xp[i] += eps; xm[i] -= eps
    num = (W2 @ sigmoid(W1 @ xp) - W2 @ sigmoid(W1 @ xm)) / (2*eps)
    print(f"dx[{i}]: Jacobian={dz_dx[0,i]:.6f}, 数值={num[0]:.6f}")
```

### 验证 3：PCA 与 SVD 的联系

```python
import numpy as np

# 生成数据中心
np.random.seed(42)
X = np.random.randn(100, 3) @ np.array([[3,0,0],[0,1,0],[0,0,0.1]]) + np.array([5,-2,1])
X_centered = X - X.mean(axis=0)

# SVD 分解
U, S, Vt = np.linalg.svd(X_centered, full_matrices=False)
print(f"奇异值: {S}")
print(f"PCA 主成分 (第一方向):\n{Vt[0]}")
print(f"解释方差比: {(S**2 / (S**2).sum())}")

# 降维到 1D
X_1d = X_centered @ Vt[0]
print(f"降维后形状: {X_1d.shape}, 保留信息: {(S[0]**2 / (S**2).sum())*100:.1f}%")
```

---

## 深度专题：Hessian 与损失曲面几何

### 损失曲面的三种临界点

| 临界点类型 | Hessian 特征值 | 深度学习中的角色 |
|---|---|---|
| 局部最小 | 全正 | 可能过拟合 |
| 鞍点 | 有正有负 | **最常见的停滞点** |
| 局部最大 | 全负 | 极少出现 |

### 高维空间几乎都是鞍点

随机 $n \times n$ 对称矩阵中，所有特征值同号的概率随 $n$ 指数下降。因此在百万维参数空间中：

$$P(\text{所有特征值} > 0) \sim 2^{-n} \to 0$$

**结论**：高维 loss landscape 中的临界点几乎全是鞍点而非局部最小。这是为什么 SGD 能逃离的原因。

### 条件数与学习率上限

Hessian 最大特征值 $\lambda_{max}$ 和最小特征值 $\lambda_{min}$ 之比 $= \kappa$。

梯度下降稳定条件：$\eta < \frac{2}{\lambda_{max}}$。

收敛速度：$\propto \left(\frac{\kappa - 1}{\kappa + 1}\right)^{2k}$（$k$ 步后）。

- $\kappa = 1$（完美球形）：1 步收敛
- $\kappa = 10^6$（狭谷）：极慢，需 Adam 或预处理

---

## 深度专题：正则化 = 约束优化

### L2 正则化与 Lagrange 乘子的联系

正则化损失：$L_{reg} = L_{data} + \frac{\lambda}{2}\|\mathbf{w}\|^2$

等价于约束优化：$\min L_{data}$ s.t. $\|\mathbf{w}\|^2 \leq R^2$

Lagrange 函数：$\mathcal{L} = L_{data} + \frac{\alpha}{2}(\|\mathbf{w}\|^2 - R^2)$

KKT 互补条件：$\alpha(\|\mathbf{w}\|^2 - R^2) = 0$

**$\alpha$ 就是正则化系数 $\lambda$**。正则化是约束优化的松弛形式。

### L1 正则化与稀疏性

L1 约束 $\|\mathbf{w}\|_1 \leq R$ 的可行域是菱形（有尖角），最优解倾向于落在顶点上 → 稀疏解（部分 $w_i = 0$）。

---

## 不足与局限

| 方法 | 局限 | 更高级处理 |
|---|---|---|
| 梯度下降 | 条件数敏感 | Adam / 预处理 |
| Newton 法 | $H^{-1}$ 不可行 | Hessian-vector product |
| Lagrange | 需解析约束 | 罚函数 / 对偶 |
| PCA (SVD) | 仅线性降维 | Autoencoder / VAE |

---

## 深度专题：SVD 降维实战——LoRA 的数学基础

### LoRA = 低秩近似

LoRA（Low-Rank Adaptation）将权重更新参数化为低秩：

$$\Delta W = AB, \quad A \in \mathbb{R}^{m \times r}, B \in \mathbb{R}^{r \times n}, r \ll \min(m,n)$$

**MATH 51 联系**：SVD 告诉我们 $W = U\Sigma V^T$。LoRA 的假设是 $\Delta W$ 的有效秩很低（类似于只用前 $r$ 个奇异值近似）。

### 从 PCA 到 LoRA

| 概念 | PCA | LoRA |
|---|---|---|
| 分解 | $X = U\Sigma V^T$ | $\Delta W = AB$ |
| 降维 | 保留前 $r$ 个奇异向量 | 秩 $r$ 分解 |
| 目标 | 数据方差最大化 | 微调参数最小化 |
| 共同数学 | 低秩近似 | 低秩近似 |

---

## 学习路线图

```
MATH 51
├── 线性代数部分 → 18.06 / Math 110（完整覆盖）
└── 多元微积分部分（本 notes 重点）
    ├── 偏导数 + 梯度 → 讲透优化器
    ├── 链式法则 → 讲透反向传播
    ├── Hessian + 凸性 → 讲透凸优化
    ├── Lagrange 乘子 → 讲透 SVM
    ├── SVD + PCA → 讲透 LoRA / 降维
    └── 正则化 = 约束优化 → 讲透 L1/L2
```

---

## 与 work4ai 讲透系列的交叉

- **讲透反向传播**：多元链式法则（第 1 节）
- **讲透优化器**：梯度 + Hessian（第 2 节）
- **讲透 PCA/LoRA**：SVD + 梯度（第 4 节）
- **讲透 SVM**：Lagrange 乘子（第 2 节）
- **讲透 L1/L2 正则化**：约束优化与 KKT（第 2 节）
