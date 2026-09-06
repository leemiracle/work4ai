# UC Berkeley MATH 53 · 章节笔记

> **教材**：Stewart, *Multivariable Calculus*
> **定位**：Berkeley 工学院标准多变量微积分。梯度/Jacobian/Hessian 是深度学习的优化语言
> **对照**：与 [MIT 18.02](../../mit-math-courses/18_02_multivariable_calculus/) 内容等价，Stewart 更偏计算

---

## 核心框架：从单变量到多变量的三步跨越

| 步骤 | 数学对象 | 一句话直觉 |
|---|---|---|
| **1. 偏导** | $\frac{\partial f}{\partial x_i}$ | "只动一个变量"的变化率 |
| **2. 梯度** | $\nabla f$ | 偏导打包成向量 = 最陡上升方向 |
| **3. 二阶导** | Hessian $H$ | 曲率信息 → 极值分类 |

---

## 第 1 章：向量与 3D 几何

### 1.1 向量运算

$$\mathbf{a} \cdot \mathbf{b} = \|\mathbf{a}\|\|\mathbf{b}\|\cos\theta$$

**ML 关联**：cosine similarity $= \frac{\mathbf{a}\cdot\mathbf{b}}{\|\mathbf{a}\|\|\mathbf{b}\|}$ → 词向量相似度、attention score。

### 1.2 叉积（$\mathbb{R}^3$）

$\|\mathbf{a}\times\mathbf{b}\| = \|\mathbf{a}\|\|\mathbf{b}\|\sin\theta$（平行四边形面积）

---

## 第 2 章：偏导数与梯度 ★★★

### 2.1 偏导数

$$\frac{\partial f}{\partial x} = \lim_{h\to 0}\frac{f(x+h, y) - f(x,y)}{h}$$

### 2.2 梯度

$$\nabla f = \left(\frac{\partial f}{\partial x},\ \frac{\partial f}{\partial y},\ \frac{\partial f}{\partial z}\right)$$

**核心定理**：$\nabla f$ 指向 $f$ 增长最快的方向，$-\nabla f$ 是**梯度下降方向**。

### 2.3 方向导数

$$D_{\hat{\mathbf{u}}}f = \nabla f \cdot \hat{\mathbf{u}}$$

### 2.4 链式法则（多元）

若 $z = f(x, y)$，$x = x(t)$，$y = y(t)$：

$$\frac{dz}{dt} = \frac{\partial f}{\partial x}\frac{dx}{dt} + \frac{\partial f}{\partial y}\frac{dy}{dt}$$

**ML 关联**：这是反向传播的雏形。$\frac{\partial L}{\partial w} = \frac{\partial L}{\partial y}\frac{\partial y}{\partial w}$。

---

## 第 3 章：多变量优化

### 3.1 临界点

$\nabla f = \mathbf{0}$ → 临界点。

### 3.2 二阶判别（Hessian 判别法，2D）

$$D = f_{xx}f_{yy} - (f_{xy})^2$$

| 条件 | 结论 |
|---|---|
| $D > 0$，$f_{xx} > 0$ | 局部最小 |
| $D > 0$，$f_{xx} < 0$ | 局部最大 |
| $D < 0$ | 鞍点 |
| $D = 0$ | 不确定 |

### 3.3 Lagrange 乘子

约束 $g(\mathbf{x}) = k$ 下优化 $f$：解方程组 $\nabla f = \lambda\nabla g$，$g = k$。

**ML 关联**：SVM 的对偶问题推导。

---

## 第 4 章：重积分

### 4.1 二重积分

$$\iint_R f(x,y)\,dA$$

### 4.2 极坐标

$$\iint f\,dA = \iint f(r\cos\theta, r\sin\theta)\,r\,dr\,d\theta$$

### 4.3 ML 关联

- **概率归一化**：$\iint p(x,y)\,dx\,dy = 1$
- **边缘分布**：$p(x) = \int p(x,y)\,dy$（变分推断的核心操作）

---

## 第 5 章：向量微积分（Green/Stokes/Divergence）

### 5.1 Green 定理

$$\oint_C P\,dx + Q\,dy = \iint_D \left(\frac{\partial Q}{\partial x} - \frac{\partial P}{\partial y}\right)dA$$

### 5.2 散度定理

$$\iint_S \mathbf{F}\cdot d\mathbf{S} = \iiint_V (\nabla\cdot\mathbf{F})\,dV$$

**ML 关联**：扩散模型中的概率流连续性方程 $\frac{\partial p}{\partial t} + \nabla\cdot(p\mathbf{v}) = 0$。

---

## 与 ML 的关联总表

| MATH 53 概念 | ML 应用 |
|---|---|
| 梯度 $\nabla f$ | 梯度下降 / SGD / Adam |
| 链式法则 | 反向传播 |
| Hessian | 二阶优化 / 鞍点分析 |
| Lagrange 乘子 | SVM / KKT 条件 |
| 重积分 | 概率归一化 / 边缘化 |

---

## 代码验证

### 验证 1：梯度下降 + 数值梯度

```python
import numpy as np

def numerical_grad(f, w, h=1e-5):
    """数值梯度（中心差分）"""
    grad = np.zeros_like(w)
    for i in range(len(w)):
        wp, wm = w.copy(), w.copy()
        wp[i] += h; wm[i] -= h
        grad[i] = (f(wp) - f(wm)) / (2*h)
    return grad

f = lambda w: (w[0]-1)**2 + 4*(w[1]-2)**2   # 椭球, min at (1,2)
w = np.array([0.0, 0.0])
for i in range(100):
    w = w - 0.1 * numerical_grad(f, w)
print(f"梯度下降结果: {w}")  # 应接近 (1, 2)
```

### 验证 2：方向导数 = 梯度投影

```python
import numpy as np

# f(x,y) = x^2 + y^2, gradient at (3,4) = (6,8)
f = lambda xy: xy[0]**2 + xy[1]**2
pt = np.array([3.0, 4.0])
grad = numerical_grad(f, pt)  # ≈ (6, 8)

# 方向 u = (1,0)
u1 = np.array([1.0, 0.0])
dir_deriv_1 = np.dot(grad, u1)  # ≈ 6 (= df/dx)

# 方向 u = (0,1)
u2 = np.array([0.0, 1.0])
dir_deriv_2 = np.dot(grad, u2)  # ≈ 8 (= df/dy)

# 方向 u = (3,4)/5 (gradient direction)
u3 = grad / np.linalg.norm(grad)
dir_deriv_3 = np.dot(grad, u3)  # ≈ 10 (= ||grad||, 最大方向导数)

print(f"梯度方向的方向导数 {dir_deriv_3:.1f} = ||grad|| {np.linalg.norm(grad):.1f} (最大!)")
```

### 验证 3：Hessian 判别与鞍点

```python
import numpy as np

def numerical_hessian(f, w, h=1e-4):
    """数值 Hessian（二阶中心差分）"""
    n = len(w)
    H = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            wpp, wpm, wmp, wmm = [w.copy() for _ in range(4)]
            wpp[i]+=h; wpp[j]+=h; wpm[i]+=h; wpm[j]-=h
            wmp[i]-=h; wmp[j]+=h; wmm[i]-=h; wmm[j]-=h
            H[i,j] = (f(wpp) - f(wpm) - f(wmp) + f(wmm)) / (4*h**2)
    return H

# f(x,y) = x^2 - y^2 (鞍点在原点)
f_saddle = lambda w: w[0]**2 - w[1]**2
H = numerical_hessian(f_saddle, np.array([0.0, 0.0]))
eigvals = np.linalg.eigvalsh(H)
print(f"鞍点 Hessian:\n{H}")
print(f"特征值: {eigvals}  (一正一负 → 鞍点)")
```

---

## 深度专题：条件数与优化器选择

### 为什么梯度下降在某些函数上极慢？

考虑 $f(x,y) = x^2 + Cy^2$（$C$ 很大）。

Hessian $= \text{diag}(2, 2C)$，条件数 $= C$。

- $y$ 方向梯度大（$2Cy$），$x$ 方向梯度小（$2x$）
- 固定学习率 $\eta$：若 $\eta$ 适配 $y$（小），则 $x$ 极慢；若 $\eta$ 适配 $x$（大），则 $y$ 发散
- **这就是"狭谷"问题**——loss landscape 呈狭长椭圆

### Adam 的解决方案（[arXiv:1412.6980](https://arxiv.org/abs/1412.6980)）

Adam 对每个参数 $i$ 自适应缩放：

$$\Delta w_i = -\eta \cdot \frac{\hat{m}_i}{\sqrt{\hat{v}_i} + \epsilon}$$

其中 $\hat{m}_i$ = 梯度一阶矩（动量），$\hat{v}_i$ = 梯度二阶矩。

- $y$ 方向梯度大 → $v_y$ 大 → 步长被 $\sqrt{v_y}$ 缩小
- $x$ 方向梯度小 → $v_x$ 小 → 步长相对放大
- **效果**：各方向有效步长趋于一致，缓解条件数问题

---

## 深度专题：Lagrange 乘子 → SVM 推导

支持向量机（SVM）的硬间隔最大化：

$$\min_{\mathbf{w}, b} \frac{1}{2}\|\mathbf{w}\|^2 \quad \text{s.t.}\ y_i(\mathbf{w}^T\mathbf{x}_i + b) \geq 1$$

Lagrange 函数：$L = \frac{1}{2}\|\mathbf{w}\|^2 - \sum_i \alpha_i[y_i(\mathbf{w}^T\mathbf{x}_i + b) - 1]$

KKT 条件 $\nabla_\mathbf{w} L = 0$ → $\mathbf{w} = \sum_i \alpha_i y_i \mathbf{x}_i$

**关键**：$\alpha_i > 0$ 仅对**支持向量**（边界上的点）。这就是 MATH 53 的 Lagrange 乘子在最优化中的直接应用。

---

## 不足与局限

| 方法 | 局限 | 更高级处理 |
|---|---|---|
| 梯度下降 | 条件数大时收敛慢 | Adam / 二阶方法 |
| Lagrange 乘子 | 需解析约束 | 罚函数 / 对偶 |
| Green/Stokes | 仅光滑场 | 分布理论 |
| 数值 Hessian | $O(n^2)$ 次 $f$ 评估 | Hessian-vector product ($O(n)$) |

---

## 与 work4ai 讲透系列的交叉

- **讲透反向传播**：多元链式法则（第 2 章）
- **讲透优化器**：梯度 + Hessian（第 2-3 章）= SGD → Adam
- **讲透 SVM**：Lagrange 乘子（第 3 章）
- **讲透扩散模型**：散度定理 / 连续性方程（第 5 章）
