# UC Berkeley MATH 185 · 复分析 精读笔记

> **教材**：Brown & Churchill, *Complex Variables and Applications*；或 Stein-Shakarchi, *Complex Analysis*
> **参考**：[math.berkeley.edu/courses](https://math.berkeley.edu/courses)

---

## 〇、费曼直觉层：复分析到底在研究什么？

### 一句话直觉

> **复分析 = 微积分 + 一个神奇的定理（Cauchy 定理）→ 一切变得优美。**

实分析中，一个函数可导需要左右导数相等——条件苛刻。复分析中，一个函数**复可导**（holomorphic）条件更强，强到带来一连串惊人的后果：无穷可导、幂级数展开、积分完全由奇点决定。

**核心魔法**：如果一个复函数在你区域内部可导，那它的环路积分 = 0（Cauchy 定理）。反过来，这推出它**自动无穷次可导**——实分析中完全不存在的事。

### 三个核心直觉

| 定理 | 直觉 | ML/工程对应 |
|---|---|---|
| **Cauchy 积分定理** | 可导函数沿闭合路径积分为 0 | 留数定理 → 拉普拉斯逆变换 |
| **Cauchy 积分公式** | 函数值由边界完全决定 | 信号处理（Z 变换）|
| **留数定理** | 环路积分 = 内部奇点的"贡献"之和 | 控制论稳定性判据 |

### 为什么 ML 工程师该学复分析？

1. **Z 变换 / 傅里叶变换**：数字信号处理的基础（滤波器设计、频域分析）
2. **生成函数**：概率分布的特征函数 / 矩母函数
3. **留数 = 反变换**：拉普拉斯逆变换、Z 逆变换都靠留数计算
4. **稳定性判据**：系统极点是否在左半平面 / 单位圆内 → 因果/稳定

---

## 一、数学层：核心定义与定理

### 1.1 复可导与全纯函数

**定义**：$f: \mathbb{C} \to \mathbb{C}$ 在 $z_0$ 处复可导，如果极限
$$f'(z_0) = \lim_{h \to 0} \frac{f(z_0 + h) - f(z_0)}{h}$$
存在（$h$ 沿任意路径趋近 0 时极限相同）。

**全纯（holomorphic）**：在开集 $U$ 上处处复可导。

**Cauchy-Riemann 方程** ★：$f = u + iv$ 全纯 $\iff$ $\frac{\partial u}{\partial x} = \frac{\partial v}{\partial y}$, $\frac{\partial u}{\partial y} = -\frac{\partial v}{\partial x}$。

### 1.2 Cauchy 积分定理 ★

**定理**：若 $f$ 在简单闭合曲线 $\gamma$ 及其内部全纯，则
$$\oint_\gamma f(z)\,dz = 0$$

**直觉**：全纯函数"没有涡旋"——环路积分无积累。

**后果**：路径无关性——全纯函数的积分只依赖端点，不依赖路径。

### 1.3 Cauchy 积分公式 ★

**定理**：$f$ 在圆盘 $|z - z_0| < R$ 内全纯，则对 $|z - z_0| < R$：
$$f(z) = \frac{1}{2\pi i}\oint_\gamma \frac{f(\zeta)}{\zeta - z}\,d\zeta$$

**惊人后果**：函数在**内部**的值完全由**边界**值决定！

**推论**：全纯函数无穷次可导：
$$f^{(n)}(z) = \frac{n!}{2\pi i}\oint_\gamma \frac{f(\zeta)}{(\zeta - z)^{n+1}}\,d\zeta$$

### 1.4 泰勒级数与 Laurent 级数

**泰勒级数**：全纯函数 = 收敛幂级数：
$$f(z) = \sum_{n=0}^\infty \frac{f^{(n)}(z_0)}{n!}(z - z_0)^n$$

**Laurent 级数** ★：带负幂项的展开（在环域内）：
$$f(z) = \sum_{n=-\infty}^\infty a_n(z - z_0)^n$$

负幂项的存在 = 函数在 $z_0$ 处有**奇点**。

### 1.5 留数定理 ★

**留数（Residue）**：Laurent 展开中 $a_{-1}$ 项（$\frac{1}{z-z_0}$ 的系数）。

**定理（留数定理）**：$f$ 在 $\gamma$ 内部除有限个奇点 $z_1, \ldots, z_k$ 外全纯，则：
$$\oint_\gamma f(z)\,dz = 2\pi i \sum_{j=1}^k \mathrm{Res}(f, z_j)$$

**留数计算**：
- 一阶极点：$\mathrm{Res}(f, z_0) = \lim_{z \to z_0}(z - z_0)f(z)$
- $m$ 阶极点：$\mathrm{Res}(f, z_0) = \frac{1}{(m-1)!}\lim_{z \to z_0}\frac{d^{m-1}}{dz^{m-1}}[(z-z_0)^m f(z)]$

### 1.6 共形映射

**定义**：$f$ 全纯且 $f'(z) \neq 0$ → $f$ 是**共形映射**（保角映射）——保持角度和方向。

**Riemann 映射定理**：任何单连通开集（不是全 $\mathbb{C}$）可共形映射到单位圆盘。

**应用**：把复杂区域的问题变换到简单区域（如单位圆盘）上解决。

### 1.7 Fourier / Laplace / Z 变换（工程联系）

- **Fourier 变换**：$\hat{f}(\omega) = \int f(t)e^{-i\omega t}dt$——实轴上的分析
- **Laplace 变换**：$F(s) = \int_0^\infty f(t)e^{-st}dt$——半平面的分析，留数做逆变换
- **Z 变换**：$X(z) = \sum x[n]z^{-n}$——离散序列的复分析

---

## 二、代码层

### 2.1 Cauchy 积分公式的数值验证

```python
import numpy as np

# f(z) = e^z 在原点附近全纯
# Cauchy 积分公式: f(0) = (1/2πi) ∮ e^z/z dz (沿单位圆)
N = 10000
theta = np.linspace(0, 2*np.pi, N, endpoint=False)
dz = theta[1] - theta[0]
# 沿单位圆积分 e^z / z
z = np.exp(1j * theta)
integrand = np.exp(z) / z * 1j * z  # dz = i*e^{iθ} dθ
integral = np.sum(integrand) * dz / (2 * np.pi * 1j)
print(f"Cauchy 积分公式: f(0) = e^0 = 1")
print(f"数值积分 = {integral.real:.8f} + {integral.imag:.8f}i")
print(f"误差 = {abs(integral - 1.0):.2e}")
```

### 2.2 留数计算与逆变换

```python
# 用留数计算实积分: ∫_{-∞}^∞ dx/(1+x^2) = π
# f(z) = 1/(1+z^2), 极点 z=i (上半平面), 留数 = 1/(2i)
residue_at_i = 1.0 / (2j)  # lim_{z→i} (z-i)/(z^2+1) = 1/(i-(-i)) = 1/(2i)
integral = 2 * np.pi * 1j * residue_at_i
print(f"∫ dx/(1+x²) = 2πi × Res = {integral.real:.6f} = π ✓")
```

### 2.3 共形映射可视化

```python
import matplotlib.pyplot as plt

# w = z^2: 把上半平面共形映射到全平面（去掉负实轴）
# 可视化: 网格线如何变形
x = np.linspace(-2, 2, 20)
y = np.linspace(0.01, 2, 10)
X, Y = np.meshgrid(x, y)
Z = X + 1j * Y
W = Z**2

fig, axes = plt.subplots(1, 2, figsize=(12, 5))
for xi in x:
    axes[0].plot([xi]*len(y), y, 'b-', alpha=0.3)
    w = (xi + 1j*np.array(y))**2
    axes[1].plot(w.real, w.imag, 'b-', alpha=0.3)
for yi in y:
    axes[0].plot(x, [yi]*len(x), 'r-', alpha=0.3)
    w = (np.array(x) + 1j*yi)**2
    axes[1].plot(w.real, w.imag, 'r-', alpha=0.3)
axes[0].set_title('z-平面'); axes[1].set_title('w = z² 平面')
plt.savefig('conformal_map.png', dpi=150); plt.show()
```

---

## 三、与 ML/工程的联系

### 3.1 信号处理

- **滤波器设计**：传递函数 $H(z)$ 的极点位置决定滤波器特性
- **稳定性**：极点全在单位圆内 → 因果稳定系统
- **Z 变换 = 离散信号的复分析**

### 3.2 量子力学

- 波函数 $\psi(z) \in \mathbb{C}$：复值是量子力学的本质
- 解析延拓 → 量子场论的 Wick 旋转

### 3.3 概率论

- **特征函数** $\phi_X(t) = \mathbb{E}[e^{itX}]$：分布的"傅里叶变换"
- **矩母函数**：复分析 → 唯一确定分布

### 3.4 控制论

- Nyquist 稳定性判据：用开环传递函数的频域响应（复值）判断闭环稳定性
- 核心工具：辐角原理（Argument Principle，留数定理的推论）

---

## 四、不足层与边界

1. **复分析偏"过于优美"**：全纯函数的性质太好了，现实中的函数通常不满足。机器学习中几乎不直接用复值函数。
2. **多复变更难**：单复变复分析有 Cauchy 定理的完整理论；多复变（$n > 1$）的性质完全不同，远更复杂。
3. **与 ML 的联系是间接的**：复分析主要通过信号处理、控制论、概率论间接影响 ML——不像优化/PDE/SDE 那样直接。

---

## 五、应用层速查

| 应用 | 复分析工具 | 效果 |
|---|---|---|
| **信号处理** | Z 变换 + 留数 | 滤波器设计 |
| **控制论** | Nyquist 判据 + 辐角原理 | 稳定性分析 |
| **概率论** | 特征函数 + Fourier 逆变换 | 分布唯一性 |
| **积分计算** | 留数定理 | 化实积分为留数求和 |
| **流体力学** | 共形映射 | 翼型设计 |

---

## 六、推荐路径

1. **Brown-Churchill** 第 1-5 章：复数 → 全纯 → Cauchy 定理 → 级数 → 留数 → **核心**
2. **第 6-7 章**：共形映射 + Laplace 变换 → 工程应用
3. **跳过**：多复变、Riemann 面（除非做纯数/弦论）
4. **交叉**：概率论（特征函数）+ 信号处理（Z 变换）

---

## 术语对照

| 英文 | 中文 |
|---|---|
| Holomorphic / analytic | 全纯 / 解析 |
| Cauchy-Riemann equations | 柯西-黎曼方程 |
| Cauchy's theorem | 柯西积分定理 |
| Cauchy integral formula | 柯西积分公式 |
| Residue | 留数 |
| Residue theorem | 留数定理 |
| Laurent series | 洛朗级数 |
| Pole | 极点 |
| Essential singularity | 本性奇点 |
| Conformal mapping | 共形映射（保角映射）|
| Riemann mapping theorem | 黎曼映射定理 |
| Argument principle | 辐角原理 |
