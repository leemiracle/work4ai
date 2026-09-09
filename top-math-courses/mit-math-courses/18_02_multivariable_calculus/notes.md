# MIT 18.02 · 章节笔记

> **教材**：Edwards & Penney, *Multivariable Calculus*；OCW Auroux 讲义
> **视频**：OCW 18.02 Prof. Denis Auroux 35 讲 — ocw.mit.edu/courses/18-02-multivariable-calculus-fall-2007
> **定位**：单变量 → 多变量的飞跃。梯度/Jacobian/Hessian 是深度学习优化的数学语言

---

## 核心框架：多变量微积分的"四级火箭"

每一级都是 18.01 单变量概念的**多维推广**：

| 层级 | 数学对象 | 单变量对应 | ML 角色 |
|---|---|---|---|
| **1. 偏导数** | $\frac{\partial f}{\partial x_i}$ | $f'(x)$ | 参数级梯度 |
| **2. 梯度向量** | $\nabla f$ | $f'(x)$（标量） | 优化方向信号 |
| **3. Jacobian 矩阵** | $J = \frac{\partial \mathbf{y}}{\partial \mathbf{x}}$ | 链式法则系数 | **反向传播** ★ |
| **4. Hessian 矩阵** | $H = \nabla^2 f$ | $f''(x)$ | 二阶优化 / 曲率 |

---

## 第 1 章：向量与点积（Vectors & Dot Product）

### 1.1 向量

$\mathbf{v} = (v_1, v_2, \dots, v_n) \in \mathbb{R}^n$

- 长度：$\|\mathbf{v}\| = \sqrt{v_1^2 + \cdots + v_n^2}$
- 加法/数乘：逐分量运算

### 1.2 点积

$$\mathbf{a} \cdot \mathbf{b} = a_1b_1 + \cdots + a_nb_n = \|\mathbf{a}\|\|\mathbf{b}\|\cos\theta$$

- **Cauchy-Schwarz**：$|\mathbf{a}\cdot\mathbf{b}| \leq \|\mathbf{a}\|\|\mathbf{b}\|$
- **ML 关联**：attention score $= \mathbf{q}\cdot\mathbf{k}$（dot-product attention）

### 1.3 叉积（仅 $\mathbb{R}^3$）

$$\mathbf{a} \times \mathbf{b} = \begin{vmatrix}\mathbf{i} & \mathbf{j} & \mathbf{k}\\a_1&a_2&a_3\\b_1&b_2&b_3\end{vmatrix}$$

$\|\mathbf{a}\times\mathbf{b}\| = \|\mathbf{a}\|\|\mathbf{b}\|\sin\theta$（平行四边形面积）

---

## 第 2 章：偏导数与梯度（Partial Derivatives & Gradient）★★★

### 2.1 直觉

> **比喻**：偏导 = "只动一个变量，其他固定"的瞬时变化率。梯度 = 把所有偏导打包成向量 = "最陡上升方向"。

### 2.2 偏导数定义

$$\frac{\partial f}{\partial x_i} = \lim_{h\to 0}\frac{f(\dots, x_i + h, \dots) - f(\dots, x_i, \dots)}{h}$$

### 2.3 梯度向量 ★★★

$$\nabla f = \left(\frac{\partial f}{\partial x_1}, \frac{\partial f}{\partial x_2}, \dots, \frac{\partial f}{\partial x_n}\right)$$

**核心性质**：
- $\nabla f$ 指向 $f$ **增加最快**的方向
- $-\nabla f$ 指向 $f$ **减少最快**的方向 → **梯度下降方向**
- $\nabla f = \mathbf{0}$ → 临界点（可能是极值）

### 2.4 方向导数

$$D_{\mathbf{u}}f = \nabla f \cdot \mathbf{u}, \quad \|\mathbf{u}\| = 1$$

**ML 关联**：线搜索中的搜索方向。最大方向导数 $= \|\nabla f\|$（沿梯度方向）。

### 2.5 梯度下降公式 ★

$$\boxed{\mathbf{w}_{t+1} = \mathbf{w}_t - \eta\,\nabla f(\mathbf{w}_t)}$$

这是 18.02 最核心的 ML 公式。$\eta$ = 学习率，$\nabla f$ = 梯度。Adam（[arXiv:1412.6980](https://arxiv.org/abs/1412.6980)）在其基础上加入动量和自适应步长。

---

## 第 3 章：多元链式法则与 Jacobian ★★★

**这是反向传播的数学根基**。

### 3.1 多元链式法则

设 $L = L(\mathbf{y})$，$\mathbf{y} = \mathbf{y}(\mathbf{x})$，则：

$$\frac{\partial L}{\partial x_j} = \sum_i \frac{\partial L}{\partial y_i}\frac{\partial y_i}{\partial x_j}$$

矩阵形式：$\nabla_{\mathbf{x}} L = J_{\mathbf{y}\to\mathbf{x}}^T \cdot \nabla_{\mathbf{y}} L$

### 3.2 Jacobian 矩阵 ★★★

$$J = \frac{\partial \mathbf{y}}{\partial \mathbf{x}} = \begin{pmatrix}\frac{\partial y_1}{\partial x_1} & \cdots & \frac{\partial y_1}{\partial x_n}\\ \vdots & \ddots & \vdots\\ \frac{\partial y_m}{\partial x_1} & \cdots & \frac{\partial y_m}{\partial x_n}\end{pmatrix}$$

**几何意义**：Jacobian 是最佳局部线性近似——把非线性变换 $\mathbf{y}(\mathbf{x})$ 在一点附近用线性变换 $J$ 替代。

**ML 关联**：
- 反向传播 = Jacobian 矩阵的链式乘积
- $\frac{\partial L}{\partial \mathbf{W}_1} = \frac{\partial L}{\partial \mathbf{h}} \cdot \frac{\partial \mathbf{h}}{\partial \mathbf{W}_1}$

### 3.3 Hessian 矩阵

$$H = \nabla^2 f = \begin{pmatrix}\frac{\partial^2 f}{\partial x_1^2} & \frac{\partial^2 f}{\partial x_1 \partial x_2} & \cdots\\ \frac{\partial^2 f}{\partial x_2 \partial x_1} & \frac{\partial^2 f}{\partial x_2^2} & \cdots\\ \vdots & & \ddots\end{pmatrix}$$

**临界点分类**：
- $H$ 正定（所有特征值 $>0$）→ 局部最小
- $H$ 负定 → 局部最大
- $H$ 有正有负特征值 → 鞍点

**ML 关联**：深度学习损失曲面的鞍点分析。在高维空间中鞍点远多于局部极小。

---

## 第 4 章：多元 Taylor 展开与优化

### 4.1 二阶 Taylor 近似

$$f(\mathbf{x}) \approx f(\mathbf{x}_0) + \nabla f(\mathbf{x}_0)^T(\mathbf{x}-\mathbf{x}_0) + \frac{1}{2}(\mathbf{x}-\mathbf{x}_0)^T H (\mathbf{x}-\mathbf{x}_0)$$

### 4.2 Newton 优化法（多变量）

$$\mathbf{x}_{t+1} = \mathbf{x}_t - H^{-1}\nabla f(\mathbf{x}_t)$$

**为什么不用**：深度学习有数亿参数，$H$ 是 $n\times n$ 矩阵（$n \sim 10^9$），存储/求逆不可行。

### 4.3 Lagrange 乘子（约束优化）★

在约束 $g(\mathbf{x}) = 0$ 下最小化 $f(\mathbf{x})$：

$$\nabla f = \lambda \nabla g$$

**ML 关联**：SVM 的对偶推导，KKT 条件的基础。

---

## 第 5 章：重积分（Multiple Integrals）

### 5.1 二重积分

$$\iint_R f(x,y)\,dA = \lim \sum f(x_i, y_j)\Delta x\,\Delta y$$

### 5.2 极坐标/柱坐标/球坐标

- 极坐标：$dA = r\,dr\,d\theta$
- 球坐标：$dV = \rho^2\sin\phi\,d\rho\,d\phi\,d\theta$

### 5.3 ML 关联

- **概率归一化**：$\iint p(x,y)\,dx\,dy = 1$（联合密度）
- **边缘化**：$p(x) = \int p(x,y)\,dy$（变分推断的核心操作）

---

## 第 6 章：向量微积分三大定理

### 6.1 线积分

$$\int_C \mathbf{F}\cdot d\mathbf{r} = \int_C (P\,dx + Q\,dy + R\,dz)$$

### 6.2 Green 定理（2D）

$$\oint_C P\,dx + Q\,dy = \iint_D \left(\frac{\partial Q}{\partial x} - \frac{\partial P}{\partial y}\right)dA$$

**直觉**：边界上的环量 = 区域内的"旋转"（旋度）的积分。

### 6.3 Stokes 定理（3D）

$$\oint_C \mathbf{F}\cdot d\mathbf{r} = \iint_S (\nabla \times \mathbf{F})\cdot d\mathbf{S}$$

### 6.4 散度定理（Divergence / Gauss）

$$\iint_S \mathbf{F}\cdot d\mathbf{S} = \iiint_V (\nabla \cdot \mathbf{F})\,dV$$

**直觉**：穿过闭合曲面的"流量" = 内部"源头"的总量。

**ML 关联**：三大定理在 ML 中较少直接出现，但散度/旋度概念出现在：
- **概率流 ODE**（扩散模型）：连续性方程 $\frac{\partial p}{\partial t} + \nabla\cdot(p\mathbf{v}) = 0$
- **score matching** 中的散度计算

---

## 与 ML 的关联总表

| 18.02 概念 | ML 应用 | 具体公式 |
|---|---|---|
| 梯度 $\nabla f$ | 梯度下降 | $\mathbf{w} \leftarrow \mathbf{w} - \eta\nabla f$ |
| **Jacobian** $J$ | **反向传播** | $\nabla_\mathbf{x} L = J^T\nabla_\mathbf{y}L$ |
| Hessian $H$ | 二阶优化 / 鞍点 | $H$ 正定 → 局部最小 |
| 多元链式法则 | 深层网络梯度 | $\frac{\partial L}{\partial \mathbf{w}_l} = \frac{\partial L}{\partial \mathbf{h}_{l+1}}\frac{\partial \mathbf{h}_{l+1}}{\partial \mathbf{w}_l}$ |
| Lagrange 乘子 | SVM / 约束优化 | $\nabla f = \lambda\nabla g$ |
| 重积分 | 概率归一化/边缘化 | $\int p(\mathbf{x})\,d\mathbf{x} = 1$ |
| 散度定理 | 概率流 ODE | $\nabla\cdot(p\mathbf{v})$ 连续性方程 |

---

## 代码验证

### 验证 1：梯度下降在多变量函数上

```python
import numpy as np

def f(w):
    """Rosenbrock-like: f(w1,w2) = (1-w1)^2 + 100(w2-w1^2)^2"""
    return (1 - w[0])**2 + 100 * (w[1] - w[0]**2)**2

def grad_f(w):
    dfdw1 = -2*(1 - w[0]) - 400*w[0]*(w[1] - w[0]**2)
    dfdw2 = 200*(w[1] - w[0]**2)
    return np.array([dfdw1, dfdw2])

w = np.array([-1.2, 1.0])
lr = 0.001
for i in range(10000):
    w = w - lr * grad_f(w)
print(f"最小值点: {w}")          # 应接近 (1, 1)
print(f"梯度范数: {np.linalg.norm(grad_f(w)):.2e}")
```

### 验证 2：Jacobian = 反向传播

```python
import numpy as np

# 两层网络: h = ReLU(W1 x), y = W2 h
# 验证 Jacobian 链式法则
np.random.seed(42)
W1 = np.random.randn(3, 2)   # 2 -> 3
W2 = np.random.randn(1, 3)   # 3 -> 1
x = np.array([0.5, -0.3])

# 前向
a = W1 @ x                   # (3,)
h = np.maximum(a, 0)         # ReLU
y = W2 @ h                   # (1,)

# 反向（链式法则 = Jacobian 乘积）
dy_dh = W2                    # Jacobian dy/dh = W2  (1x3)
dh_da = np.diag((a > 0).astype(float))  # Jacobian dh/da = diag(ReLU')
da_dW1 = ...                  # 略

# dL/dW1 的局部导数（数值验证）
eps = 1e-7
grad_num = np.zeros_like(W1)
for i in range(W1.shape[0]):
    for j in range(W1.shape[1]):
        W1[i,j] += eps
        y_plus = W2 @ np.maximum(W1 @ x, 0)
        W1[i,j] -= 2*eps
        y_minus = W2 @ np.maximum(W1 @ x, 0)
        W1[i,j] += eps
        grad_num[i,j] = (y_plus - y_minus) / (2*eps)

print(f"数值 Jacobian dW1:\n{grad_num}")
```

### 验证 3：Hessian 特征值与临界点分类

```python
import numpy as np

# f(x,y) = x^2 + y^2 （凸，最小值在原点）
# Hessian = [[2,0],[0,2]]，正定 → 局部最小
H = np.array([[2, 0], [0, 2]])
eigenvalues = np.linalg.eigvalsh(H)
print(f"Hessian 特征值: {eigenvalues}")  # [2, 2] > 0 → 正定 → 局部最小

# f(x,y) = x^2 - y^2 （鞍点）
H_saddle = np.array([[2, 0], [0, -2]])
eig_saddle = np.linalg.eigvalsh(H_saddle)
print(f"鞍点 Hessian 特征值: {eig_saddle}")  # [-2, 2] 一正一负 → 鞍点
```

---

## 不足与局限

| 方法 | 局限 | 更高级的处理 |
|---|---|---|
| 梯度下降 | 高维鞍点停滞 | 动量 / Adam / 二阶方法 |
| Jacobian 计算随深度爆炸 | 计算图内存随深度线性增长 | 梯度检查点 / 可逆网络 |
| Hessian 存储 $O(n^2)$ | 大模型不可行 | Hessian-vector product ($O(n)$) / K-FAC |
| Lagrange 需要解析约束 | 复杂约束难以建模 | 罚函数 / 对偶方法 |

---

## 与 work4ai 讲透系列的交叉

- **讲透反向传播**：Jacobian 链式法则（第 3 章）= autograd 核心
- **讲透优化器**：梯度 + Hessian（第 2-3 章）= SGD → Adam → Newton
- **讲透 Attention**：点积 = attention score（第 1 章）
- **讲透 SVM**：Lagrange 乘子（第 4 章）
- **讲透扩散模型**：散度定理 + 概率流（第 6 章）
