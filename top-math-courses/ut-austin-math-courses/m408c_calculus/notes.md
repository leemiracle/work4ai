# UT Austin M 408C · 章节笔记

> **教材**：Stewart, *Calculus: Early Transcendentals*
> **定位**：UT Austin 标准微积分序列第一学期。与 [MIT 18.01](../../mit-math-courses/18_01_calculus/) 对等
> **重点**：极限 → 导数 → 积分，为 ML 的梯度优化打基础

---

## 核心框架：微积分的四问（与 MIT 18.01 一致）

| 问题 | 数学对象 | ML 对应 |
|---|---|---|
| 变化有多快？ | 导数 $f'$ | 梯度信号 → SGD |
| 累计了多少？ | 积分 $\int$ | 概率归一化 |
| 近似够吗？ | Taylor | 二阶优化 |
| 局部→全局？ | 链式法则 | **反向传播** ★ |

---

## 第 1 章：极限与连续

### 1.1 极限定义

$$\lim_{x\to a}f(x) = L: \quad \forall\varepsilon>0,\ \exists\delta>0:\ 0<|x-a|<\delta \Rightarrow |f(x)-L|<\varepsilon$$

### 1.2 重要极限

$$\lim_{x\to 0}\frac{\sin x}{x} = 1, \quad \lim_{x\to 0}(1+x)^{1/x} = e$$

### 1.3 连续性

$f$ 在 $a$ 连续 $\iff \lim_{x\to a}f(x) = f(a)$。介值定理保证连续函数取遍中间值。

---

## 第 2 章：导数 ★★★

### 2.1 定义

$$f'(x) = \lim_{h\to 0}\frac{f(x+h)-f(x)}{h}$$

> **直觉**：导数 = 几何斜率 = 物理速度 = **ML 梯度信号**。

### 2.2 求导法则

| 法则 | 公式 | ML 关联 |
|---|---|---|
| 乘法 | $(fg)' = f'g + fg'$ | 乘法节点 |
| 商 | $(f/g)' = \frac{f'g - fg'}{g^2}$ | softmax |
| **链式** ★ | $(f\circ g)' = f'(g)\cdot g'$ | **反向传播** |
| 幂 | $(x^n)' = nx^{n-1}$ | 多项式 |

### 2.3 链式法则 → 反向传播

$$\frac{dL}{dw} = \frac{dL}{dy}\cdot\frac{dy}{dw}$$

多层网络：$\frac{\partial L}{\partial \mathbf{W}_1} = \frac{\partial L}{\partial \mathbf{h}}\cdot\frac{\partial \mathbf{h}}{\partial \mathbf{W}_1}$（逐层回溯 = "反向"）。

---

## 第 3 章：导数的应用

### 3.1 极值

$f'(x_0) = 0$ → 临界点。$f''(x_0) > 0$ → 最小；$f''(x_0) < 0$ → 最大。

### 3.2 梯度下降 ★

$$x_{t+1} = x_t - \eta f'(x_t)$$

SGD 用 mini-batch 噪声梯度 $\hat{g} \approx f'$。Adam（[arXiv:1412.6980](https://arxiv.org/abs/1412.6980)）加动量 + 自适应步长。

### 3.3 Newton 迭代法

求根：$x_{n+1} = x_n - f(x_n)/f'(x_n)$。
优化：$x_{n+1} = x_n - f''(x_n)^{-1}f'(x_n)$（二阶 Taylor 取导数为零）。

---

## 第 4 章：积分

### 4.1 微积分基本定理

$$\int_a^b f(x)\,dx = F(b) - F(a), \quad F' = f$$

### 4.2 换元/分部

- 换元：链式法则的逆
- 分部：$\int u\,dv = uv - \int v\,du$

### 4.3 ML 关联

概率归一化：$\int p(x)\,dx = 1$。期望：$E[X] = \int xp(x)\,dx$。

---

## 与 ML 的关联总表

| M 408C 概念 | ML 应用 |
|---|---|
| 导数 $f'$ | 梯度下降 / SGD / Adam |
| 链式法则 | 反向传播 |
| Taylor 二阶 | Newton 法 |
| 凸性 $f'' > 0$ | 凸优化 |
| 积分 | 概率归一化 |

---

## 代码验证

### 验证 1：数值导数 + 梯度下降

```python
import numpy as np

def num_deriv(f, x, h=1e-5):
    return (f(x+h) - f(x-h)) / (2*h)

f = lambda x: x**2 + 2*x + 1   # min at x = -1
x = 3.0
for _ in range(100):
    x = x - 0.1 * num_deriv(f, x)
print(f"梯度下降: x = {x:.6f}")  # 应接近 -1
```

### 验证 2：链式法则 = 反向传播雏形

```python
import numpy as np

# y = sigmoid(w*x + b), L = (y - target)^2
def sigmoid(z): return 1 / (1 + np.exp(-z))

w, b, x, target = 2.0, -0.5, 1.0, 1.0
z = w*x + b
y = sigmoid(z)
L = (y - target)**2

# 链式法则: dL/dw = dL/dy * dy/dz * dz/dw
dL_dy = 2*(y - target)
dy_dz = y * (1 - y)         # sigmoid 导数
dz_dw = x
grad_w = dL_dy * dy_dz * dz_dw

# 数值验证
eps = 1e-7
grad_num = ((sigmoid((w+eps)*x + b) - target)**2 - (sigmoid(w*x + b) - target)**2) / eps
print(f"链式法则梯度: {grad_w:.8f}")
print(f"数值梯度:     {grad_num:.8f}")
```

### 验证 3：Newton 法一步收敛

```python
import numpy as np

# f(x) = x^2, min at 0. Newton: x1 = x0 - f'(x0)/f''(x0)
f = lambda x: x**2
fp = lambda x: 2*x
fpp = lambda x: 2.0

x0 = 10.0
x_newton = x0 - fp(x0) / fpp(x0)  # 一步: 10 - 20/2 = 0

# 梯度下降对比
x_gd = x0
for _ in range(50):
    x_gd = x_gd - 0.1 * fp(x_gd)  # 50步后

print(f"Newton 1步: {x_newton:.1f}  (直接到 0)")
print(f"GD 50步:   {x_gd:.6f}  (仍在收敛)")
print(f"GD 需要:   {int(np.ceil(np.log(0.01/10) / np.log(0.8)))} 步达到 |x|<0.01")
```

---

## 深度专题：Taylor 展开与数值稳定性

### 为什么 softmax 要减最大值？

$$\text{softmax}(z_i) = \frac{e^{z_i}}{\sum_j e^{z_j}}$$

当 $z_i$ 很大时，$e^{z_i}$ 溢出。标准技巧：减去最大值 $\hat{z} = z - \max(z)$：

$$\text{softmax}(z_i) = \frac{e^{z_i - M}}{\sum_j e^{z_j - M}}, \quad M = \max_j z_j$$

**为什么等价**：分子分母同除 $e^M$。**为什么用 Taylor**：$e^{z_i} = e^M \cdot e^{z_i - M}$，$e^{z_i - M} \leq 1$ 不溢出。

### 对数似然导数（交叉熵）

$$L = -\sum_i y_i \ln \hat{y}_i, \quad \hat{y}_i = \text{softmax}(z_i)$$

$$\frac{\partial L}{\partial z_j} = \hat{y}_j - y_j$$

这个简洁结果依赖链式法则 + softmax 导数——正是 M 408C 第 2-3 章的核心技巧。

---

## 深度专题：导数符号与优化直觉

| 导数符号 | 几何意义 | 优化含义 |
|---|---|---|
| $f'(x) > 0$ | 函数上升 | 朝 $-x$ 方向走减小 $f$ |
| $f'(x) < 0$ | 函数下降 | 朝 $+x$ 方向走减小 $f$ |
| $f'(x) = 0$ | 临界点 | 可能极值（检查 $f''$） |
| $f'(x) \to 0$ | 平坦 | 接近极值 / 鞍点 |
| $f''(x) > 0$ | 凸（碗口向上） | 局部最小 |
| $f''(x) < 0$ | 凹（碗口向下） | 局部最大 |

**梯度下降的本质**：$x_{new} = x - \eta f'(x)$。若 $f' > 0$，则 $x$ 减小（正确方向）；若 $f' < 0$，则 $x$ 增大（正确方向）。**导数的符号自动指引正确方向**。

---

## 深度专题：积分与概率论

### 概率密度 = 归一化积分

连续随机变量 $X$ 的密度 $p(x)$ 满足：

$$\int_{-\infty}^{+\infty} p(x)\,dx = 1$$

这就是微积分基本定理在概率中的应用——概率"总面积" = 1。

### 期望与方差

$$E[X] = \int x\,p(x)\,dx, \quad \text{Var}(X) = \int (x - E[X])^2 p(x)\,dx$$

**ML 联系**：交叉熵损失 $L = -\int y(x)\ln\hat{y}(x)\,dx$，KL 散度 $D_{KL} = \int p\ln\frac{p}{q}\,dx$。

### 变量替换公式

若 $Y = g(X)$，则 $p_Y(y) = p_X(g^{-1}(y)) \cdot |(g^{-1})'(y)|$。

这是 Normalizing Flow 的基础——M 408C 的一维换元在多维推广为 Jacobian 行列式。

---

## 深度专题：中值定理与梯度下降收敛

### 中值定理

$$f(b) - f(a) = f'(c)(b - a), \quad c \in (a, b)$$

**含义**：函数值的变化 = 某点导数 × 区间长度。

### 在优化中的应用

梯度下降每步：$f(w_{k+1}) - f(w_k) \approx f'(w_k)(-\eta f'(w_k)) = -\eta[f'(w_k)]^2$

- 若 $f'(w_k) \neq 0$，则 $f$ **单调下降**
- 下降量 $\propto \eta \cdot |f'|^2$（梯度越大，下降越快）
- 接近极值时 $f' \to 0$，下降变慢（自动减速）

**这就是为什么梯度下降"自然减速"的微积分原因**。

---

## 深度专题：Taylor 展开精度阶

### Euler 法 = 一阶 Taylor

$$x(t+h) \approx x(t) + h \cdot x'(t) + O(h^2)$$

局部截断误差 $O(h^2)$，全局误差 $O(h)$。

### RK4 = 四阶 Taylor

$$x(t+h) = x(t) + h\sum_{i=1}^{4}b_i k_i + O(h^5)$$

全局误差 $O(h^4)$——**误差随 $h$ 减小按 4 次方下降**。

**ML 联系**：Neural ODE 默认使用 RK4 求解器，因为ODE 网络的精度直接影响梯度计算。

---

## 不足与局限

| 方法 | 局限 | 更高级处理 |
|---|---|---|
| Riemann 积分 | 病态函数失效 | Lebesgue 积分 |
| 导数 | 不连续点不可导 | subgradient |
| Taylor | 收敛半径有限 | 渐近展开 |
| Newton 法 | 需 $f''$ 可逆 | L-BFGS |

---

## 与 work4ai 讲透系列的交叉

- **讲透反向传播**：链式法则（第 2 章）
- **讲透优化器**：梯度下降 + Taylor（第 3 章）
- **讲透 softmax/交叉熵**：$e^x$ 和 $\ln$ 的导数（第 2 章）
- **讲透凸优化**：$f'' > 0$ 与全局最优（第 2 章）
- **讲透概率论**：积分 = 概率归一化（第 4 章）
- **讲透 Neural ODE**：Taylor = 数值求解器（第 4 章）
