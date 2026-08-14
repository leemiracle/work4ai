# Harvard Math 25a/b · 章节笔记

> **教材**：Hubbard & Hubbard, *Vector Calculus, Linear Algebra, and Differential Forms* (5th ed)；配 Rudin *Principles of Mathematical Analysis* 第 1-7 章
> **定位**：Math 55 的"友好版"——严格证明导向的多变量分析 + 线代 + 微分形式
> **对照**：比 [MIT 18.02](../../mit-math-courses/18_02_multivariable_calculus/) 严格得多，强调 Inverse/Implicit Function Theorem

---

## 核心框架：从 $\mathbb{R}$ 到 $\mathbb{R}^n$ 的严格化五步

| 步骤 | 数学对象 | 严格化要点 |
|---|---|---|
| **1. 拓扑** | 开集/闭集/紧致 | $\mathbb{R}^n$ 的度量拓扑 |
| **2. 微分** | 全导数（Fréchet） | 线性近似 $+$ $o(\|\mathbf{h}\|)$ |
| **3. 高阶导** | Hessian / Taylor | 多重线性映射 |
| **4. 反函数/隐函数** | IFT / ImFT | 局部可逆性定理 |
| **5. 积分 + 形式** | 微分形式 / Stokes | 流形上的微积分 |

---

## 第 1 章：$\mathbb{R}^n$ 的拓扑

### 1.1 度量与开集

$d(\mathbf{x}, \mathbf{y}) = \|\mathbf{x}-\mathbf{y}\|$。

- **开集**：每个点有邻域包含在内
- **紧致**：闭且有界（Heine-Borel）

### 1.2 关键定理

- **Bolzano-Weierstrass**：有界序列有收敛子列
- **极值定理**：紧致集上连续函数取到最大/最小值

**ML 关联**：损失函数若定义在紧致参数空间上则必有最小值——但深度学习参数空间非紧致，所以不保证全局最优。

---

## 第 2 章：多变量微分（严格版）★★★

### 2.1 Fréchet 全导数

$f: \mathbb{R}^n \to \mathbb{R}^m$ 在 $\mathbf{a}$ 处可微，若存在线性映射 $Df(\mathbf{a}): \mathbb{R}^n \to \mathbb{R}^m$ 使得：

$$\lim_{\mathbf{h}\to\mathbf{0}} \frac{\|f(\mathbf{a}+\mathbf{h}) - f(\mathbf{a}) - Df(\mathbf{a})\mathbf{h}\|}{\|\mathbf{h}\|} = 0$$

$Df(\mathbf{a})$ 就是 **Jacobian 矩阵**。关键：这不是"偏导数存在"——而是**整体线性近似**存在。

### 2.2 链式法则（严格版）

若 $f: \mathbb{R}^n\to\mathbb{R}^m$，$g: \mathbb{R}^m\to\mathbb{R}^p$ 都可微，则：

$$D(g\circ f)(\mathbf{a}) = Dg(f(\mathbf{a}))\cdot Df(\mathbf{a})$$

**Jacobian 矩阵的乘积**。**ML 关联**：反向传播 = 链式法则的程序化实现。

### 2.3 方向导数 vs 全导数

偏导存在 $\not\Rightarrow$ 可微！经典反例：$f(x,y) = \frac{xy}{x^2+y^2}$（$(0,0)$ 处）。

---

## 第 3 章：高阶导数与 Taylor 公式

### 3.1 二阶导 = 双线性映射

$D^2f(\mathbf{a})$ 是一个双线性映射，其矩阵表示是 **Hessian**。

### 3.2 Schwarz 定理（混合偏导对称）

$$\frac{\partial^2 f}{\partial x_i \partial x_j} = \frac{\partial^2 f}{\partial x_j \partial x_i}$$

（当二阶偏导连续时）

### 3.3 多变量 Taylor 公式

$$f(\mathbf{a}+\mathbf{h}) = f(\mathbf{a}) + Df(\mathbf{a})\mathbf{h} + \frac{1}{2}\mathbf{h}^T H(\mathbf{a})\mathbf{h} + o(\|\mathbf{h}\|^2)$$

**ML 关联**：loss landscape 的二阶近似，收敛速率分析。

---

## 第 4 章：Inverse & Implicit Function Theorems ★★★

### 4.1 Inverse Function Theorem (IFT)

若 $f: \mathbb{R}^n\to\mathbb{R}^n$ 在 $\mathbf{a}$ 处可微且 $\det Df(\mathbf{a}) \neq 0$，则 $f$ 在 $\mathbf{a}$ 附近**局部可逆**。

**ML 关联**：标准化流（Normalizing Flows）要求变换可逆且 $\det J$ 可计算——IFT 保证这一点。

### 4.2 Implicit Function Theorem (ImFT)

若 $F: \mathbb{R}^{n+k}\to\mathbb{R}^k$，$F(\mathbf{a}) = 0$，且 $\det \frac{\partial F}{\partial \mathbf{y}} \neq 0$，则方程 $F(\mathbf{x}, \mathbf{y}) = 0$ 局部定义 $\mathbf{y} = g(\mathbf{x})$。

**ML 关联**：约束优化中，约束 $g(\mathbf{x}) = 0$ 定义一个流形，ImFT 保证可以参数化。

---

## 第 5 章：积分与微分形式

### 5.1 $\mathbb{R}^n$ 上的积分

Riemann 积分的多维推广。Fubini 定理（重积分 = 累次积分）。

### 5.2 变量替换

$$\int_{f(U)} g(\mathbf{y})\,d\mathbf{y} = \int_U g(f(\mathbf{x}))|\det Df(\mathbf{x})|\,d\mathbf{x}$$

**ML 关联**：标准化流的似然计算 $p_Y(\mathbf{y}) = p_X(\mathbf{x})/|\det J|$。

### 5.3 微分形式与外微分

- $k$-形式：$\omega = \sum a_{i_1\dots i_k}\,dx_{i_1}\wedge\dots\wedge dx_{i_k}$
- 外微分 $d\omega$：提升形式阶数

### 5.4 广义 Stokes 定理 ★★★

$$\boxed{\int_{\partial M} \omega = \int_M d\omega}$$

**这是微积分的最高定理**——Green/Stokes/Divergence/FTC 都是它的特例：
- $\dim M = 1$：微积分基本定理
- $\dim M = 2$（$\mathbb{R}^2$）：Green 定理
- $\dim M = 2$（$\mathbb{R}^3$）：经典 Stokes
- $\dim M = 3$：散度定理

---

## 与 ML 的关联总表

| Math 25 概念 | ML 应用 |
|---|---|
| Fréchet 全导数 = Jacobian | 反向传播（严格定义） |
| 链式法则（矩阵乘积） | autograd |
| Hessian + Taylor | 优化收敛分析 |
| IFT | Normalizing Flows 可逆性 |
| 变量替换 $|\det J|$ | Flow 似然计算 |
| ImFT | 约束流形参数化 |
| 微分形式 / Stokes | 流形上的概率/统计 |

---

## 代码验证

### Jacobian 数值验证 + 变量替换

```python
import numpy as np

def f(xy):
    x, y = xy
    return np.array([x**2 - y, x*y])

# 解析 Jacobian
def jacobian(xy):
    x, y = xy
    return np.array([[2*x, -1], [y, x]])

# 数值 Jacobian
def num_jacobian(f, xy, h=1e-6):
    n, m = len(xy), len(f(xy))
    J = np.zeros((m, n))
    for j in range(n):
        xp, xm = xy.copy(), xy.copy()
        xp[j] += h; xm[j] -= h
        J[:, j] = (f(xp) - f(xm)) / (2*h)
    return J

xy = np.array([1.0, 2.0])
print(f"解析 Jacobian:\n{jacobian(xy)}")
print(f"数值 Jacobian:\n{num_jacobian(f, xy)}")
print(f"|det J| = {abs(np.linalg.det(jacobian(xy))):.4f}")  # 变量替换的体积因子
```

### 验证 2：隐函数定理验证

```python
import numpy as np

# F(x,y) = x^2 + y^2 - 1 = 0 (单位圆)
# 隐函数定理: dy/dx = -F_x/F_y = -2x/(2y) = -x/y
F = lambda xy: xy[0]**2 + xy[1]**2 - 1

def num_deriv(F, pt, i, h=1e-7):
    pp, pm = pt.copy(), pt.copy()
    pp[i] += h; pm[i] -= h
    return (F(pp) - F(pm)) / (2*h)

pt = np.array([0.6, 0.8])  # 在单位圆上
dFdx = num_deriv(F, pt, 0)  # 2*0.6 = 1.2
dFdy = num_deriv(F, pt, 1)  # 2*0.8 = 1.6
dydx_implicit = -dFdx / dFdy  # 隐函数定理

# 直接验证: y = √(1-x²), dy/dx = -x/√(1-x²) = -x/y
dydx_direct = -pt[0] / pt[1]
print(f"隐函数定理 dy/dx = {dydx_implicit:.6f}")
print(f"直接求导 dy/dx   = {dydx_direct:.6f}")
print(f"IFT 适用 (F_y ≠ 0): {abs(dFdy) > 1e-6}")
```

### 验证 3：Normalizing Flow 变量替换

```python
import numpy as np

# 变量替换公式: p_Y(y) = p_X(x) |det(∂x/∂y)|
# Flow: y = x + tanh(x), 求 p_Y

# 解析: dy/dx = 1 + sech²(x) = 2 - tanh²(x)
# 所以 dx/dy = 1/(2 - tanh²(x))
x = 0.5
dy_dx = 1 + (1 - np.tanh(x)**2)  # sech² = 1 - tanh²
dx_dy = 1 / dy_dx
p_X = np.exp(-x**2/2) / np.sqrt(2*np.pi)  # 标准正态

y = x + np.tanh(x)
p_Y = p_X * abs(dx_dy)  # 变量替换公式

# 数值验证（Monte Carlo）
N = 1000000
samples = np.random.randn(N)
y_samples = samples + np.tanh(samples)
# 估计 p_Y(y) 附近的密度
bandwidth = 0.05
count = np.sum(np.abs(y_samples - y) < bandwidth)
p_Y_mc = count / (N * 2 * bandwidth)
print(f"变量替换 p_Y = {p_Y:.6f}")
print(f"Monte Carlo p_Y = {p_Y_mc:.6f}")
```

---

## 深度专题：Fréchet 导数与泛函分析视角

### 从有限维到无限维

Fréchet 导数是方向导数在 Banach 空间的推广：

$$\|f(\mathbf{x} + \mathbf{h}) - f(\mathbf{x}) - Df(\mathbf{x})\mathbf{h}\| = o(\|\mathbf{h}\|)$$

$Df(\mathbf{x})$ 是有界线性算子。在有限维中，它就是 Jacobian 矩阵。

### 在深度学习中的意义

- **反向传播是 Fréchet 导数的链式法则**：$D(f \circ g)(\mathbf{x}) = Df(g(\mathbf{x})) \circ Dg(\mathbf{x})$
- **Hessian 是二阶 Fréchet 导数**：$D^2f(\mathbf{x})(\mathbf{h}, \mathbf{k}) = \mathbf{h}^T H \mathbf{k}$
- **Neural ODE 的伴随方法**是无穷维 Fréchet 导数的自动微分

### 紧算子与 SVD

在函数空间中，紧算子的谱分解推广了 SVD。积分算子：

$$(Tf)(x) = \int K(x,y)f(y)dy$$

的特征函数对应于核 PCA 的主成分——无限维的"特征脸"。

---

## 深度专题：隐函数定理与 Normalizing Flow

### IFT 保证 Flow 可逆

Normalizing Flow 的核心：变换 $y = f(x)$ 必须可逆。IFT 告诉我们：

- 若 $\det J_f \neq 0$（Jacobian 行列式非零），则局部可逆
- 逆变换的 Jacobian：$J_{f^{-1}}(y) = [J_f(x)]^{-1}$

### Real NVP（耦合层）的巧妙设计

Real NVP 将 $\mathbf{x}$ 分成两半 $[\mathbf{x}_1, \mathbf{x}_2]$：

$$\mathbf{y}_1 = \mathbf{x}_1, \quad \mathbf{y}_2 = \mathbf{x}_2 \odot \exp(s(\mathbf{x}_1)) + t(\mathbf{x}_1)$$

Jacobian 是三角矩阵：

$$J = \begin{pmatrix} I & 0 \\ \cdot & \text{diag}(\exp(s)) \end{pmatrix}, \quad \det J = \prod_i \exp(s_i)$$

**三角行列式 $O(n)$ 可计算**——这是 Normalizing Flow 可行的关键。

---

## 深度专题：微分形式与几何理解

### 从线积分到微分形式

1-形式：$\omega = P\,dx + Q\,dy$

2-形式：$dx \wedge dy = -dy \wedge dx$（反对称）

外微分 $d$：$d\omega = (Q_x - P_y)\,dx \wedge dy$ = 旋度的推广。

### Stokes 定理的统一视角

$$\int_M d\omega = \int_{\partial M} \omega$$

这一个公式统一了：
- 微积分基本定理（0-形式）
- Green 定理（1-形式，$\mathbb{R}^2$）
- Stokes 定理（1-形式，$\mathbb{R}^3$）
- 散度定理（2-形式，$\mathbb{R}^3$）

**ML 联系**：连续性方程 $\nabla \cdot \mathbf{J} = 0$（概率守恒）在微分形式语言中就是 $d\omega = 0$——闭形式。扩散模型和 Flow Matching 都隐含使用了这个结构。

---

## 不足与局限

| 方法 | 局限 | 更高级处理 |
|---|---|---|
| Fréchet 导数 | 需要光滑性 | 弱导数 / Sobolev 空间 |
| IFT | 需要 $\det J \neq 0$ | 临界点理论 / Morse 理论 |
| Riemann 积分 | 处理不了病态函数 | Lebesgue 积分 |
| 微分形式 | 需要流形结构 | de Rham 上同调 |

---

## 与 work4ai 讲透系列的交叉

- **讲透反向传播**：Fréchet 全导数 + 链式法则（第 2 章）
- **讲透 Normalizing Flows**：IFT + 变量替换（第 4-5 章）
- **讲透优化收敛**：Hessian + Taylor（第 3 章）
- **讲透信息几何**：微分形式 / 流形（第 5 章）
- **讲透 Neural ODE**：伴随方法 = 无穷维 Fréchet 导数（第 4 章）
