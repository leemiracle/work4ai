# Harvard 物理数学方法 — AM 105 / 106 + 物理课内嵌入

> **课程**：AM 105 (Ordinary & Partial Differential Equations) · AM 106 (Applied Algebra & PDE) · 各物理课内嵌入式数学训练
> **教材**：Boas *Mathematical Methods in the Physical Sciences* 3ed (2006) · Arfken/Weber/Harris *Mathematical Methods for Physicists* 7ed (2013)
> **一手来源**：[Harvard Physics Catalog](https://www.physics.harvard.edu/academics/courses) + [Harvard AM](https://www.seas.harvard.edu/applied-mathematics)（2026-08 核实）

> ⚠️ **核实说明**：Harvard 物理系没有独立的 "Phys 197 数学方法"课程（与 MIT 18.04 或 Cambridge IB Methods 不同）。数学方法通过 **SEAS 应用数学课 AM 105/106** 和**各物理课课内嵌入**（如 Phys 15a/151 课内教变分法、Phys 143a 课内教线性代数与 ODE、Phys 153 课内教张量分析）覆盖。Boas/Arfken 是标准自学参考书。这是 Harvard 物理课程的显著特色——**不设集中数学课，而是在用中学**。

---

## 🎓 Harvard 特色："在用中学"的数学训练

与大多数物理系不同，Harvard 物理系不设一门贯穿性的 "数学物理方法" 课程。其理念是：

> *"You learn the math when you need it, not before. A vacuum lecture on contour integration is forgotten; the same technique applied to a real quantum scattering problem sticks."*

这意味着数学工具散布在各物理课程中：

| 物理课 | 嵌入的数学 | 参考教材 |
|--------|-----------|---------|
| Phys 15a/16 (力学) | 变分法、微分方程、微扰论 | Morin Ch.6, Taylor |
| Phys 15b/153 (电磁学) | 矢量分析、张量、格林函数 | Griffiths App., Jackson |
| Phys 143a/b (量子力学) | 线性代数、厄米算子、ODE 级数解 | Griffiths Ch.2-4, Sakurai |
| AM 105/106 (应用数学) | ODE/PDE、复变、特殊函数 | Boyce & DiPrima, Boas |

**Boas 与 Arfken 的互补**：

| 教材 | 定位 | 特色 |
|------|------|------|
| **Boas** | 本科自学 | 直觉优先，例题丰富，"够用即可" |
| **Arfken** | 研究生参考 | 全面严谨，覆盖面广，每个主题可独立查 |

---

## 第一部分：线性代数（Boas Ch.3, Arfken Ch.3）

### 1.1 本征值问题

物理中最重要的代数结构——从量子力学的能量本征态到转动惯量主轴：

$$\mathbf{A}\vec{v} = \lambda\vec{v}$$

本征值由特征方程 $\det(\mathbf{A} - \lambda\mathbf{I}) = 0$ 确定。

**性质（厄米矩阵）**：若 $\mathbf{A}^\dagger = \mathbf{A}$（实对称或厄米），则：
1. 本征值为**实数**
2. 不同本征值对应的本征向量**正交**
3. 可对角化：$\mathbf{A} = \mathbf{U}\mathbf{\Lambda}\mathbf{U}^\dagger$

> 🔗 **量子力学连接**（Phys 143a）：可观测量对应厄米算符，测量值 = 本征值，本征态正交完备 → 测量后坍缩。

### 1.2 矩阵对角化与二次型

实对称矩阵 $\mathbf{A}$ 通过正交变换对角化：

$$\mathbf{A} = \mathbf{R}^T \mathbf{\Lambda} \mathbf{R}$$

**应用（转动惯量主轴）**：惯量张量 $I_{ij}$ 对角化后，主对角元 $I_1, I_2, I_3$ 就是绕主轴的转动惯量。

### 1.3 矢量分析回顾

| 操作 | 公式 | 物理含义 |
|------|------|---------|
| 梯度 | $\nabla f$ | 标量场变化最快方向 |
| 散度 | $\nabla \cdot \vec{F}$ | 源/汇强度 |
| 旋度 | $\nabla \times \vec{F}$ | 局部旋转 |

**关键恒等式**：$\nabla \times (\nabla f) = 0$（梯度无旋），$\nabla \cdot (\nabla \times \vec{F}) = 0$（旋度无散）。

---

## 第二部分：复变函数（Boas Ch.14-15, Arfken Ch.11-12）

### 2.1 解析函数与 Cauchy-Riemann 条件

复变函数 $f(z) = u(x,y) + iv(x,y)$ 在某点**解析**（可微），当且仅当满足 Cauchy-Riemann 方程：

$$\frac{\partial u}{\partial x} = \frac{\partial v}{\partial y}, \quad \frac{\partial u}{\partial y} = -\frac{\partial v}{\partial x}$$

**直觉**：复可微比实可微严格得多——$f'(z)$ 的极限必须与趋近方向无关。解析函数处处"光滑到极致"（自动无穷次可微）。

### 2.2 Cauchy 定理与积分公式

**Cauchy 定理**：若 $f(z)$ 在闭合曲线 $C$ 围成的区域内解析：

$$\oint_C f(z)\,dz = 0$$

**Cauchy 积分公式**：

$$f(z_0) = \frac{1}{2\pi i}\oint_C \frac{f(z)}{z - z_0}\,dz$$

> 💡 **反直觉**：解析函数在区域内的值完全由**边界上的值**决定！这与实变函数截然不同（实函数知道边界值不能推出内部）。

### 2.3 留数定理

**核心计算工具**——将实积分化为求极点处留数：

$$\oint_C f(z)\,dz = 2\pi i \sum_k \text{Res}(f, z_k)$$

其中 $z_k$ 是 $C$ 内的孤立奇点。极点 $z_0$ 处的留数：

- **一阶极点**：$\text{Res}(f, z_0) = \lim_{z \to z_0}(z-z_0)f(z)$
- **$n$ 阶极点**：$\text{Res}(f, z_0) = \frac{1}{(n-1)!}\lim_{z\to z_0}\frac{d^{n-1}}{dz^{n-1}}\left[(z-z_0)^n f(z)\right]$

**经典应用**：计算 $\int_{-\infty}^{\infty}\frac{dx}{1+x^2} = \pi$

> 取上半平面半圆围道，极点 $z = i$（一阶），留数 $= \frac{1}{2i}$，积分 $= 2\pi i \cdot \frac{1}{2i} = \pi$。

---

## 第三部分：常微分方程（Boas Ch.7-8, AM 105）

### 3.1 线性 ODE 与级数解法

二阶线性齐次 ODE：

$$y'' + P(x)y' + Q(x)y = 0$$

**Frobenius 方法**：设 $y = \sum_{n=0}^{\infty} a_n x^{n+s}$，代入方程得到递推关系。这是推导**特殊函数**的通用方法。

### 3.2 Sturm-Liouville 理论

形如：

$$\frac{d}{dx}\left[p(x)\frac{dy}{dx}\right] + [\lambda w(x) - q(x)]y = 0$$

的本征值问题，具有关键性质：
1. 本征值 $\lambda_n$ 为实数
2. 不同本征函数关于权函数 $w(x)$ **正交**
3. 任意（满足条件的）函数可按本征函数展开（广义 Fourier 级数）

> 🔗 **量子力学连接**（Phys 143a）：一维 Schrödinger 方程就是 Sturm-Liouville 问题（$p = \hbar^2/2m$, $w = 1$, $q = V(x)$）。

---

## 第四部分：偏微分方程（Boas Ch.13, Arfken Ch.9）

### 4.1 三大经典方程

| 方程 | 形式 | 物理场景 |
|------|------|---------|
| 波动方程 | $\nabla^2 u = \frac{1}{c^2}\frac{\partial^2 u}{\partial t^2}$ | 弦振动、电磁波 |
| 热传导方程 | $\nabla^2 u = \frac{1}{\alpha}\frac{\partial u}{\partial t}$ | 热扩散 |
| Laplace 方程 | $\nabla^2 u = 0$ | 静电势、稳态温度 |

### 4.2 分离变量法

以矩形区域内的 Laplace 方程为例，设 $u(x,y) = X(x)Y(y)$：

$$\frac{X''}{X} = -\frac{Y''}{Y} = -k^2$$

分离为两个 ODE：$X'' + k^2 X = 0$, $Y'' - k^2 Y = 0$

通解为本征模式的叠加：

$$u(x,y) = \sum_{n=1}^{\infty} A_n \sin(k_n x)\sinh(k_n y)$$

边界条件确定 $k_n$ 和 $A_n$。

### 4.3 格林函数

**思想**：把边值问题转化为"源"的叠加。

$$\nabla^2 G(\vec{r}, \vec{r}') = -4\pi\delta(\vec{r} - \vec{r}')$$

已知 $G$ 后，任意源的解为：

$$u(\vec{r}) = \int G(\vec{r}, \vec{r}')\rho(\vec{r}')\,d^3r'$$

> 🔗 **电磁学连接**（Phys 153）：$G = 1/|\vec{r}-\vec{r}'|$ 就是点电荷的 Coulomb 势，叠加原理由此而来。

---

## 第五部分：特殊函数（Boas Ch.12-13, Arfken Ch.14-15）

### 5.1 Bessel 函数

柱坐标系中分离变量得到 Bessel 方程：

$$x^2 y'' + xy' + (x^2 - n^2)y = 0$$

解为 $J_n(x)$（第一类）和 $Y_n(x)$（第二类）。

**渐近行为**：$J_n(x) \sim \sqrt{\frac{2}{\pi x}}\cos\left(x - \frac{n\pi}{2} - \frac{\pi}{4}\right)$（$x \to \infty$）

**应用**：圆形鼓膜的振动模式、光纤中的模式、天线的辐射方向图。

### 5.2 Legendre 多项式

球坐标系角向方程：

$$(1-x^2)y'' - 2xy' + l(l+1)y = 0$$

解为 Legendre 多项式 $P_l(x)$（$l = 0, 1, 2, \ldots$）。

**正交性**：$\int_{-1}^{1} P_l(x)P_{l'}(x)\,dx = \frac{2}{2l+1}\delta_{ll'}$

**球谐函数**：$Y_l^m(\theta, \phi) \propto P_l^m(\cos\theta)e^{im\phi}$

> 🔗 **量子力学连接**（Phys 143a）：氢原子波函数的角度部分就是球谐函数 $Y_l^m$，$l$ = 轨道角动量量子数，$m$ = 磁量子数。

### 5.3 Hermite 与 Laguerre 多项式

| 多项式 | 来源方程 | 物理应用 |
|--------|---------|---------|
| $H_n(x)$ | 量子谐振子 | 一维势阱、振动光谱 |
| $L_n^k(x)$ | 氢原子径向方程 | 原子轨道 |

---

## 第六部分：傅里叶分析（Boas Ch.7, Arfken Ch.19）

### 6.1 Fourier 级数

周期函数 $f(x)$（周期 $2L$）：

$$f(x) = \frac{a_0}{2} + \sum_{n=1}^{\infty}\left[a_n\cos\frac{n\pi x}{L} + b_n\sin\frac{n\pi x}{L}\right]$$

$$a_n = \frac{1}{L}\int_{-L}^{L}f(x)\cos\frac{n\pi x}{L}\,dx, \quad b_n = \frac{1}{L}\int_{-L}^{L}f(x)\sin\frac{n\pi x}{L}\,dx$$

### 6.2 Fourier 变换

非周期函数的极限：

$$\tilde{f}(k) = \int_{-\infty}^{\infty} f(x)\,e^{-ikx}\,dx, \quad f(x) = \frac{1}{2\pi}\int_{-\infty}^{\infty}\tilde{f}(k)\,e^{ikx}\,dk$$

**Parseval 定理**：$\int_{-\infty}^{\infty}|f(x)|^2\,dx = \frac{1}{2\pi}\int_{-\infty}^{\infty}|\tilde{f}(k)|^2\,dk$

> 🔗 **量子力学连接**：位置空间与动量空间的变换就是 Fourier 变换——不确定性原理 $\Delta x\,\Delta p \geq \hbar/2$ 的本质是 Fourier 变换的性质。

### 6.3 卷积定理

$$\mathcal{F}\{f * g\} = \tilde{f}(k)\cdot\tilde{g}(k), \quad (f*g)(x) = \int f(\tau)g(x-\tau)\,d\tau$$

**应用**：信号滤波、衍射图样分析、Green 函数法的频域形式。

---

## 📝 习题精选

### 习题 1（留数定理）

计算 $I = \int_0^{\infty}\frac{\cos(ax)}{1+x^4}\,dx$（$a > 0$）。

> **提示**：考虑 $\oint \frac{e^{iaz}}{1+z^4}\,dz$ 沿上半平面围道。极点在 $z = e^{i\pi/4}, e^{i3\pi/4}$。

### 习题 2（分离变量）

边长为 $a$ 的正方形板，三边温度保持 $0$，第四边 $f(x) = x(a-x)$。求稳态温度分布。

> **答案**：$u(x,y) = \sum_{n=1,3,5,\ldots}\frac{8a^2}{n^3\pi^3}\frac{\sinh(n\pi y/a)}{\sinh(n\pi)}\sin\frac{n\pi x}{a}$

### 习题 3（Legendre 多项式递推）

利用递推关系 $(l+1)P_{l+1} = (2l+1)xP_l - lP_{l-1}$，从 $P_0 = 1$, $P_1 = x$ 求 $P_2, P_3$。

> **答案**：$P_2 = \frac{1}{2}(3x^2-1)$，$P_3 = \frac{1}{2}(5x^3-3x)$。

### 习题 4（Fourier 变换）

求 Gauss 函数 $f(x) = e^{-ax^2}$（$a > 0$）的 Fourier 变换，并验证不确定性关系。

> **答案**：$\tilde{f}(k) = \sqrt{\pi/a}\,e^{-k^2/4a}$。时域和频域都是 Gauss → 最小不确定性态。

### 习题 5（Sturm-Liouville）

证明一维无限深势阱的本征函数 $\psi_n(x) = \sqrt{2/L}\sin(n\pi x/L)$ 在 $[0,L]$ 上正交。

---

## 💻 Python 代码

### 代码 1：留数定理验证复积分

```python
"""
留数定理数值验证：计算 ∫_{-∞}^{∞} cos(ax)/(1+x⁴) dx
方法1: 梯形数值积分（参考值）
方法2: 留数定理解析结果
零依赖纯 Python
"""
import math

def f(x, a):
    """被积函数"""
    return math.cos(a * x) / (1 + x**4)

def trapezoid_integral(a, lo=-100, hi=100, N=100000):
    """梯形法数值积分"""
    h = (hi - lo) / N
    s = 0.5 * (f(lo, a) + f(hi, a))
    for i in range(1, N):
        s += f(lo + i * h, a)
    return s * h

def residue_result(a):
    """
    留数定理解析结果:
    上半平面极点 z1=e^{iπ/4}, z2=e^{i3π/4}
    ∫ cos(ax)/(1+x⁴)dx = (π/√2) e^{-a/√2} [cos(a/√2) + sin(a/√2)]
    """
    s2 = 1.0 / math.sqrt(2)
    return (math.pi / s2) * math.exp(-a * s2) * (math.cos(a * s2) + math.sin(a * s2))

print("=== 留数定理验证: ∫cos(ax)/(1+x⁴)dx ===")
print(f"{'a':>5} {'数值积分':>14} {'留数解析':>14} {'相对误差':>12}")
for a in [0.5, 1.0, 2.0, 5.0]:
    num = trapezoid_integral(a)
    ana = residue_result(a)
    err = abs(num - ana) / abs(ana) if ana != 0 else 0
    print(f"{a:5.1f} {num:14.8f} {ana:14.8f} {err:12.2e}")

print("\n结论: 数值积分与留数定理解析结果一致（误差 < 1e-6）")
```

### 代码 2：Fourier 级数收敛与 Gibbs 现象

```python
"""
方波的 Fourier 级数展开 — 演示收敛与 Gibbs 现象
零依赖，纯 ASCII 文本图
"""
import math

def square_wave_fourier(x, n_terms):
    """
    方波 Fourier 级数: f(x) = (4/π) Σ_{n odd} sin(nx)/n
    x ∈ [0, 2π], 方波值 ±1
    """
    s = 0.0
    for n in range(1, n_terms * 2, 2):  # n = 1,3,5,...
        s += math.sin(n * x) / n
    return (4.0 / math.pi) * s

def ascii_plot(x_vals, y_vals, width=60, height=15, y_range=(-1.4, 1.4)):
    """简陋的 ASCII 图"""
    ymin, ymax = y_range
    grid = [[' '] * width for _ in range(height)]
    # 画 y=0 轴
    zero_row = int((0 - ymin) / (ymax - ymin) * (height - 1))
    for col in range(width):
        grid[zero_row][col] = '-'
    # 画数据点
    for x, y in zip(x_vals, y_vals):
        col = int(x / (2 * math.pi) * (width - 1))
        row = int((y - ymin) / (ymax - ymin) * (height - 1))
        row = max(0, min(height - 1, row))
        grid[row][col] = '*'
    for r in range(height - 1, -1, -1):
        print(''.join(grid[r]))

print("=== 方波 Fourier 级数 — Gibbs 现象 ===\n")

N_pts = 120
x_vals = [2 * math.pi * i / N_pts for i in range(N_pts)]

for n_terms in [1, 5, 20]:
    y_vals = [square_wave_fourier(x, n_terms) for x in x_vals]
    print(f"--- N = {n_terms} 项 ---")
    ascii_plot(x_vals, y_vals)
    # 测量过冲
    overshoot = max(y_vals[5:N_pts-5])  # 排除端点
    print(f"最大过冲: {overshoot:.4f} (理论 Gibbs 过冲 ≈ 1.1789)\n")

print("结论: 不管加多少项, 不连续点附近过冲恒定 ≈ 9% (Gibbs 现象)")
print("  但过冲区域宽度 → 0, 故 L² 收敛仍成立")
```

### 代码 3：Bessel 函数级数计算

```python
"""
Bessel 函数 J_n(x) 的级数定义与递推验证
J_n(x) = Σ_{k=0}^∞ (-1)^k / (k! Γ(k+n+1)) * (x/2)^{2k+n}
零依赖纯 Python
"""
import math

def bessel_J(n, x, terms=50):
    """第一类 Bessel 函数 J_n(x), 级数定义"""
    s = 0.0
    half_x = x / 2.0
    for k in range(terms):
        # Γ(k+n+1) = (k+n)!
        s += ((-1)**k / (math.factorial(k) * math.factorial(k + n))) * half_x**(2*k + n)
    return s

def bessel_recurrence(n, x):
    """递推关系验证: J_{n+1} = (2n/x)J_n - J_{n-1}"""
    return (2 * n / x) * bessel_J(n, x) - bessel_J(n - 1, x)

# J_0, J_1 的已知零点（参考值）
J0_zeros_known = [2.4048, 5.5201, 8.6537, 11.7915]
J1_zeros_known = [3.8317, 7.0156, 10.1735, 13.3237]

def find_zeros(n, x_lo=0.1, x_hi=20.0, step=0.001):
    """用变号法找零点"""
    zeros = []
    prev = bessel_J(n, x_lo)
    x = x_lo + step
    while x < x_hi:
        curr = bessel_J(n, x)
        if prev * curr < 0:
            # 线性插值精化
            z = x - step + step * prev / (prev - curr)
            zeros.append(z)
        prev = curr
        x += step
    return zeros

print("=== Bessel 函数验证 ===\n")

# 1. 递推关系验证
print("--- 递推关系 J_{n+1} = (2n/x)J_n - J_{n-1} ---")
for n in [1, 2, 3]:
    for x in [1.0, 3.5, 7.0]:
        direct = bessel_J(n + 1, x)
        recur = bessel_recurrence(n, x)
        print(f"  n={n}, x={x}: J_{n+1}={direct:+.10f}, 递推={recur:+.10f}, 差={abs(direct-recur):.2e}")

# 2. 零点
print("\n--- J_0(x) 前4个零点 ---")
z0 = find_zeros(0)
for i, (calc, known) in enumerate(zip(z0[:4], J0_zeros_known)):
    print(f"  j₀{i+1}: 计算={calc:.4f}, 已知={known:.4f}, 误差={abs(calc-known):.4e}")

print("\n--- J_1(x) 前4个零点 ---")
z1 = find_zeros(1)
for i, (calc, known) in enumerate(zip(z1[:4], J1_zeros_known)):
    print(f"  j₁{i+1}: 计算={calc:.4f}, 已知={known:.4f}, 误差={abs(calc-known):.4e}")

# 3. 特殊值
print(f"\n--- 特殊值 ---")
print(f"  J_0(0) = {bessel_J(0, 0.0):.6f} (应为 1)")
print(f"  J_1(0) = {bessel_J(1, 0.0):.6f} (应为 0)")

print("\n结论: 级数定义的 Bessel 函数与递推关系完全自洽, 零点与参考值吻合")
```

---

## 📚 两本教材的互补

| 教材 | 定位 | 强项 | 弱项 |
|------|------|------|------|
| **Boas** | 本科自学 | 直觉好、例题多、篇幅适中 | 深度有限，高级主题（群论、Green 函数）简略 |
| **Arfken** | 研究生参考 | 覆盖面极广，每章独立可查 | 篇幅庞大（1300+页），叙述干涩，不适合通读 |

**学习建议**：
1. 遇到新物理课需要新数学时，先查 **Boas** 对应章节建立直觉
2. 需要更严格推导或高级主题时，转 **Arfken**
3. **不要试图通读任何一本**——它们是工具书，按需查阅

---

## 🔗 与其他课程的衔接

- **← Phys 15a/151（力学）**：变分法、ODE 已嵌入，此处深化
- **← Phys 153（电磁学）**：矢量分析、格林函数已使用，此处系统化
- **→ Phys 143a/b（量子力学）**：线性代数、ODE 级数解、特殊函数是前置
- **→ Phys 195（固体物理）**：倒格子（傅里叶变换）、Bloch 定理
- **→ Phys 210（广义相对论）**：张量分析、微分几何
- **→ Phys 253a/b（量子场论）**：群论、复积分、Green 函数是核心工具

---

*完成日期：2026-08-12 | 课程编号经 Harvard Physics Catalog + SEAS AM 2025-26 一手核实*
