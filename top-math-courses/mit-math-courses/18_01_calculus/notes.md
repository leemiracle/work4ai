# MIT 18.01 · 章节笔记

> **教材**：Strang, *Calculus* (Wellesley-Cambridge Press) + Herman 在线补充
> **视频**：OCW 18.01 Prof. David Jerison 35 讲 — ocw.mit.edu/courses/18-01-single-variable-calculus-fall-2006
> **定位**：单变量微积分——从极限到 Taylor 级数，是 ML 梯度优化的数学根基

---

## 核心框架：微积分的"四问"

Strang 的微积分围绕**四个递进问题**展开，这也是后续 ML 全栈的骨架：

| 问题 | 数学对象 | ML 对应 |
|---|---|---|
| **变化有多快？** | 导数 $f'(x)$ | 梯度信号 → SGD/Adam |
| **累计了多少？** | 积分 $\int f\,dx$ | 概率归一化 / 期望 / 损失 |
| **一阶近似够吗？** | Taylor 级数 | 二阶优化 / 收敛分析 |
| **局部 → 全局？** | 链式法则 | **反向传播** ★ |

---

## 第 1 章：极限与连续（Limits & Continuity）

### 1.1 直觉

极限回答一个问题：当 $x$ **无限逼近** $a$ 时，$f(x)$ 趋向哪里？**不是问 $f(a)$ 等于多少**，而是问"邻域行为"。

> **比喻**：导数 = 瞬时速度。你不可能在"零时间"内拍照测速，但你可以取越来越短的时间间隔，看速度趋向什么——这就是极限。

### 1.2 ε-δ 定义

$$\lim_{x \to a} f(x) = L \iff \forall \varepsilon > 0,\ \exists \delta > 0:\ 0 < |x - a| < \delta \Rightarrow |f(x) - L| < \varepsilon$$

**关键**：$\delta$ 依赖于 $\varepsilon$（你给我精度要求，我给你范围）。这是"我可以任意精确地逼近"的严格化。

### 1.3 极限运算法则

$$\lim(f + g) = \lim f + \lim g, \quad \lim(f \cdot g) = \lim f \cdot \lim g$$

**重要极限**（"0/0" 型用 L'Hôpital 或变形）：

$$\lim_{x \to 0} \frac{\sin x}{x} = 1, \quad \lim_{x \to 0} \frac{1 - \cos x}{x} = 0, \quad \lim_{x \to 0}(1+x)^{1/x} = e$$

### 1.4 连续性

$f$ 在 $a$ 处连续 $\iff \lim_{x\to a} f(x) = f(a)$。

- 连续函数的复合仍连续
- **介值定理（IVT）**：连续函数在 $[a,b]$ 上取遍 $f(a)$ 与 $f(b)$ 之间的所有值
- **ML 关联**：神经网络激活函数的连续性保证输出不"跳跃"；ReLU 在 0 处不可导但不影响 subgradient

---

## 第 2 章：导数（Derivatives）★★★

### 2.1 直觉

**导数 = 几何斜率 = 物理瞬时速度 = ML 梯度信号**。

> **一句话**：导数是"无穷小变化率"——把 $\frac{\Delta y}{\Delta x}$ 的 $\Delta x \to 0$。

### 2.2 定义

$$f'(x) = \lim_{\Delta x \to 0} \frac{f(x + \Delta x) - f(x)}{\Delta x}$$

等价的对称形式（数值微分更稳定）：

$$f'(x) = \lim_{h \to 0} \frac{f(x+h) - f(x-h)}{2h}$$

### 2.3 求导法则（四大法则）

| 法则 | 公式 | ML 关联 |
|---|---|---|
| **乘法法则** | $(fg)' = f'g + fg'$ | 乘法节点 |
| **商法则** | $(f/g)' = \frac{f'g - fg'}{g^2}$ | softmax 分母 |
| **链式法则** ★ | $(f \circ g)'(x) = f'(g(x)) \cdot g'(x)$ | **反向传播** |
| **幂法则** | $(x^n)' = nx^{n-1}$ | 多项式回归 |

### 2.4 链式法则深度解析 ★★★

**这是反向传播的数学根基**。

$$\frac{d}{dx} f(g(x)) = f'(g(x)) \cdot g'(x)$$

**多层复合**：$y = f_3(f_2(f_1(x)))$

$$\frac{dy}{dx} = \frac{df_3}{df_2} \cdot \frac{df_2}{df_1} \cdot \frac{df_1}{dx}$$

**ML 对应**：神经网络 $L = \ell(\sigma(W_2 \sigma(W_1 x)))$ 的梯度

$$\frac{\partial L}{\partial W_1} = \frac{\partial L}{\partial \ell} \cdot \frac{\partial \ell}{\partial \sigma} \cdot \frac{\partial \sigma}{\partial W_1}$$

这正是**反向传播**——从输出端开始，逐层乘以局部导数（Jacobian）。

### 2.5 隐函数求导

$y$ 由方程 $F(x, y) = 0$ 隐式定义时：

$$\frac{dy}{dx} = -\frac{\partial F/\partial x}{\partial F/\partial y}$$

### 2.6 高阶导数

$$f''(x) = \frac{d}{dx}f'(x)$$

- $f'' > 0$：凸（convex）→ **凸优化** 的前提
- $f'' < 0$：凹（concave）

---

## 第 3 章：导数的应用

### 3.1 极值与临界点

$f'(x_0) = 0$ → $x_0$ 是临界点。

**二阶判别**：
- $f''(x_0) > 0$ → 局部最小值
- $f''(x_0) < 0$ → 局部最大值
- $f''(x_0) = 0$ → 不确定

### 3.2 最优化 → ML 训练 ★

**梯度下降**（一阶方法）：

$$x_{t+1} = x_t - \eta f'(x_t)$$

- $\eta$ = 学习率（步长）
- $f'(x_t)$ = 梯度信号（18.01 的导数！）
- 收敛条件：$|f'(x)|$ 很小

**随机梯度下降（SGD）**：用 mini-batch 的噪声梯度估计 $\hat{g} \approx f'(x)$。

**Adam 优化器**（[arXiv:1412.6980](https://arxiv.org/abs/1412.6980)）：在导数基础上引入一阶矩（动量）和二阶矩（自适应学习率）。

### 3.3 Newton 迭代法

求 $f(x) = 0$ 的根：

$$x_{n+1} = x_n - \frac{f(x_n)}{f'(x_n)}$$

**ML 关联**：Newton 法在优化中变成（二阶 Taylor 展开取导数为零）：

$$x_{n+1} = x_n - [f''(x_n)]^{-1} f'(x_n)$$

这是 **Newton 优化法** / 拟 Newton 法（BFGS, L-BFGS）的基础。

---

## 第 4 章：积分（Integration）

### 4.1 直觉

**积分 = 累积量 = 曲线下面积 = 概率归一化**。

> **比喻**：导数是"瞬时速度"，积分是"总里程"——把所有瞬时速度乘以时间微元，累加起来。

### 4.2 定积分（Riemann 和的极限）

$$\int_a^b f(x)\,dx = \lim_{n \to \infty} \sum_{i=1}^n f(x_i^*) \Delta x$$

### 4.3 微积分基本定理（FTC）★★★

**将"求导"和"积分"这对互逆操作统一起来**：

$$\int_a^b f(x)\,dx = F(b) - F(a), \quad \text{其中 } F'(x) = f(x)$$

或等价地：

$$\frac{d}{dx}\int_a^x f(t)\,dt = f(x)$$

**意义**：积分 = 找"原函数" $F$ 然后代入上下限。

### 4.4 换元积分法（Substitution）

链式法则的逆运算：

$$\int f(g(x))g'(x)\,dx = \int f(u)\,du \quad (u = g(x))$$

### 4.5 分部积分（Integration by Parts）

乘法法则的逆运算：

$$\int u\,dv = uv - \int v\,du$$

---

## 第 5 章：反常积分（Improper Integrals）

### 5.1 定义

积分区间无穷或被积函数无界：

$$\int_a^{\infty} f(x)\,dx = \lim_{b \to \infty} \int_a^b f(x)\,dx$$

### 5.2 收敛判别

- **比较判别**：$0 \leq f \leq g$，$g$ 收敛 → $f$ 收敛
- **p-积分**：$\int_1^{\infty} \frac{1}{x^p}\,dx$ 在 $p > 1$ 时收敛
- **ML 关联**：KL 散度 $D_{KL}(p\|q) = \int p\ln(p/q)\,dx$ 的存在性依赖反常积分收敛

---

## 第 6 章：级数与 Taylor 展开 ★★★

### 6.1 数值级数收敛

$\sum_{n=1}^{\infty} a_n$ 收敛 $\iff$ 部分和 $S_N = \sum_{n=1}^N a_n$ 有极限。

**判别法**：
- 比值判别：$\lim |a_{n+1}/a_n| < 1$ → 收敛
- 根值判别：$\lim \sqrt[n]{|a_n|} < 1$ → 收敛

### 6.2 幂级数

$$\sum_{n=0}^{\infty} c_n(x-a)^n$$

收敛半径 $R$：$|x - a| < R$ 时收敛。

### 6.3 Taylor 级数 ★★★

**用多项式无限逼近光滑函数**——这是数值优化的理论核心。

$$f(x) = \sum_{n=0}^{\infty} \frac{f^{(n)}(a)}{n!}(x-a)^n$$

常用 Taylor 展开（在 $a=0$ 处，即 Maclaurin）：

| 函数 | Taylor 展开 | ML 用途 |
|---|---|---|
| $e^x$ | $1 + x + \frac{x^2}{2} + \cdots$ | softmax / 指数族 |
| $\ln(1+x)$ | $x - \frac{x^2}{2} + \frac{x^3}{3} - \cdots$ | 对数似然 |
| $\frac{1}{1-x}$ | $1 + x + x^2 + \cdots$ | 几何级数 / Dropout 分析 |
| $(1+x)^\alpha$ | $1 + \alpha x + \frac{\alpha(\alpha-1)}{2}x^2 + \cdots$ | 二项近似 |

### 6.4 Taylor 近似与优化

$$f(x) \approx f(x_0) + f'(x_0)(x - x_0) + \frac{1}{2}f''(x_0)(x-x_0)^2$$

- **一阶 Taylor**（保留 $f'$）→ 梯度下降
- **二阶 Taylor**（保留 $f''$）→ Newton 法
- **ML 关联**：深度学习的损失曲面分析（loss landscape）常用二阶 Taylor 近似 + Hessian

---

## 与 ML 的关联总表

| 18.01 概念 | ML 应用 | 具体公式 |
|---|---|---|
| 导数 $f'$ | 梯度下降 | $x \leftarrow x - \eta f'(x)$ |
| 链式法则 | **反向传播** | $\frac{dL}{dw} = \frac{dL}{dy}\frac{dy}{dw}$ |
| Taylor 二阶 | Newton 优化 | $x \leftarrow x - f''(x)^{-1}f'(x)$ |
| 凸性 $f'' > 0$ | 凸优化 | 保证全局最优 |
| 积分 | 概率归一化 | $\int p(x)\,dx = 1$ |
| 反常积分收敛 | KL 散度存在性 | $\int p\ln\frac{p}{q}$ 须收敛 |
| Taylor 展开 | loss landscape | $L \approx L_0 + g^T\Delta + \tfrac{1}{2}\Delta^T H \Delta$ |

---

## 代码验证

### 验证 1：数值导数 vs 解析导数

```python
import numpy as np

def f(x):
    return x**3 + 2*x**2 + 1      # f(x) = x³ + 2x² + 1

def f_prime(x):
    return 3*x**2 + 4*x           # 解析导数 f'(x) = 3x² + 4x

# 中心差分（数值导数）
h = 1e-6
x0 = 2.0
numerical = (f(x0 + h) - f(x0 - h)) / (2 * h)
analytical = f_prime(x0)

print(f"解析导数: {analytical}")    # 20.0
print(f"数值导数: {numerical:.8f}")  # 20.00000000
print(f"误差: {abs(numerical - analytical):.2e}")
```

### 验证 2：链式法则 = 反向传播的雏形

```python
import numpy as np

# y = σ(wx + b)，验证链式法则
def sigmoid(z): return 1 / (1 + np.exp(-z))

w, b, x = 2.0, -1.0, 0.5
z = w * x + b
y = sigmoid(z)

# 前向：y = σ(z), z = wx + b
# 链式法则：dy/dw = dy/dz * dz/dw = y(1-y) * x
dy_dz = y * (1 - y)       # σ'(z) = σ(z)(1-σ(z))
dz_dw = x                 # ∂z/∂w = x
grad_chain = dy_dz * dz_dw

# 数值验证
eps = 1e-7
grad_num = (sigmoid((w+eps)*x + b) - sigmoid(w*x + b)) / eps
print(f"链式法则梯度: {grad_chain:.8f}")  # 应与数值梯度一致
print(f"数值梯度:     {grad_num:.8f}")
```

### 验证 3：Taylor 展开逼近精度

```python
import numpy as np
import math

def exp_taylor(x, n_terms):
    """e^x 的 n 阶 Taylor 近似"""
    return sum(x**k / math.factorial(k) for k in range(n_terms))

x = 1.0
for n in [1, 3, 5, 10, 15]:
    approx = exp_taylor(x, n)
    print(f"n={n:2d}: Taylor≈{approx:.8f}, 真值={np.exp(x):.8f}, 误差={abs(approx-np.exp(x)):.2e}")
```

---

## 不足与局限

| 方法 | 局限 | 更高级的处理 |
|---|---|---|
| Riemann 积分 | 处理不了 Dirichlet 函数（处处不连续） | Lebesgue 积分（测度论） |
| 导数 | 不连续点不可导（ReLU 在 0 处） | subgradient / 弱导数 |
| Taylor 级数 | 只在收敛半径内有效；非解析函数发散 | 渐近展开 / Padé 近似 |
| Newton 法 | 需要 $f''$ 可逆；不保证全局收敛 | L-BFGS / trust-region |

---

## 与 work4ai 讲透系列的交叉

- **讲透反向传播**：链式法则（第 2 章）= autograd 的数学核心
- **讲透优化器**：梯度下降 + Taylor 二阶（第 3、6 章）= SGD → Adam → Newton
- **讲透 softmax**：$e^x$ 的 Taylor 展开保证数值稳定性
- **讲透交叉熵**：$\ln(1+x)$ 的 Taylor → 对数似然导数
