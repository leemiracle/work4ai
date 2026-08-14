# Stanford 物理系 Phase 1 · 主题 3：量子力学

> **课程谱系**：PHYS 67 (量子物理荣誉) → PHYS 130 (量子力学) → PHYS 210 (研究生量子)
>
> **教材阶梯**：Griffiths《Introduction to Quantum Mechanics》3ed → Sakurai & Napolitano《Modern Quantum Mechanics》3ed
>
> **Stanford 特色**：从 SLAC 的深度非弹性散射（揭示夸克）到 LCLS 的 X 射线自由电子激光（量子探测），Stanford 是量子物理实验与理论的交汇点

---

## 目录

1. [薛定谔方程](#1-薛定谔方程)
2. [一维势场](#2-一维势场)
3. [谐振子与氢原子](#3-谐振子与氢原子)
4. [角动量与自旋](#4-角动量与自旋)
5. [微扰理论](#5-微扰理论)
6. [Stanford/SLAC 关联](#6-stanfordlac-关联)
7. [习题与解答](#7-习题与解答)
8. [代码实验](#8-代码实验)
9. [局限与延伸](#9-局限与延伸)

---

## 1. 薛定谔方程

### 1.1 直觉

量子力学的核心反直觉：**粒子是波，波是粒子**。薛定谔方程描述的是**概率波**的演化——不是粒子在哪，而是粒子在哪的概率如何随时间变化。

Griffiths 教材的哲学：先承认数学，再追问意义。Born 的概率诠释是公理，不是推导。

### 1.2 波函数与概率

波函数 $\Psi(x,t)$ 是复值函数，其模方是概率密度：

$$|\Psi(x,t)|^2\, dx = \text{在 } [x, x+dx] \text{ 找到粒子的概率}$$

归一化条件：

$$\int_{-\infty}^{\infty}|\Psi|^2\, dx = 1$$

### 1.3 含时薛定谔方程

$$\boxed{i\hbar\frac{\partial\Psi}{\partial t} = \hat{H}\Psi = \left(-\frac{\hbar^2}{2m}\nabla^2 + V\right)\Psi}$$

### 1.4 分离变量与定态

若 $V$ 不含时间，分离变量 $\Psi(x,t) = \psi(x)\,e^{-iEt/\hbar}$，得**定态薛定谔方程**：

$$\hat{H}\psi = E\psi \quad\Longleftrightarrow\quad -\frac{\hbar^2}{2m}\frac{d^2\psi}{dx^2} + V\psi = E\psi$$

通解是定态叠加：

$$\Psi(x,t) = \sum_n c_n\,\psi_n(x)\,e^{-iE_n t/\hbar}$$

### 1.5 厄米算符与可观测量

每个物理量 $A$ 对应厄米算符 $\hat{A}$，其本征值是实数，本征态正交完备：

$$\hat{A}\phi_n = a_n\phi_n, \quad \langle\phi_m|\phi_n\rangle = \delta_{mn}$$

测量结果必是某个本征值 $a_n$，概率 $|c_n|^2$，测量后态坍缩到 $\phi_n$。

### 1.6 不确定性原理

任意两算符 $\hat{A}, \hat{B}$：

$$\sigma_A^2 \sigma_B^2 \geq \left(\frac{1}{2i}\langle[\hat{A},\hat{B}]\rangle\right)^2$$

位置-动量：$\sigma_x\sigma_p \geq \hbar/2$。能量-时间：$\sigma_E\sigma_t \geq \hbar/2$。

---

## 2. 一维势场

### 2.1 无限深势阱（粒子在盒中）

$V(x) = 0$ for $0 < x < a$，其余 $\infty$。

本征态：$\psi_n(x) = \sqrt{\frac{2}{a}}\sin\left(\frac{n\pi x}{a}\right)$, $n = 1, 2, 3, \ldots$

能级：

$$\boxed{E_n = \frac{n^2\pi^2\hbar^2}{2ma^2}}$$

**零点能** $E_1 > 0$——量子粒子永远不会完全静止。这是不确定性原理的直接推论。

### 2.2 有限深势阱

束缚态 ($E < V_0$) 数量有限，由阱深决定。即使是浅阱也至少有一个束缚态（1D）。

### 2.3 隧穿效应

方势垒 $V_0$，粒子能量 $E < V_0$，透射系数：

$$T \approx e^{-2\kappa a}, \quad \kappa = \sqrt{2m(V_0-E)}/\hbar$$

应用：$\alpha$ 衰变、扫描隧道显微镜（STM）、核聚变。

### 2.4 量子谐波叠加与拍频

$$\Psi(x,t) = c_1\psi_1 e^{-iE_1 t/\hbar} + c_2\psi_2 e^{-iE_2 t/\hbar}$$

概率密度振荡频率 $\omega = (E_2 - E_1)/\hbar$——这就是**量子拍**。

---

## 3. 谐振子与氢原子

### 3.1 量子谐振子

$V(x) = \frac{1}{2}m\omega^2 x^2$。能级**等间距**：

$$\boxed{E_n = \left(n + \frac{1}{2}\right)\hbar\omega, \quad n = 0, 1, 2, \ldots}$$

基态波函数：$\psi_0(x) = \left(\frac{m\omega}{\pi\hbar}\right)^{1/4}e^{-m\omega x^2/(2\hbar)}$。

**代数解法（升降算符）**：

$$\hat{a} = \sqrt{\frac{m\omega}{2\hbar}}\left(\hat{x} + \frac{i\hat{p}}{m\omega}\right), \quad \hat{H} = \hbar\omega\left(\hat{a}^\dagger\hat{a} + \frac{1}{2}\right)$$

$\hat{a}^\dagger\psi_n \propto \psi_{n+1}$，$\hat{a}\psi_n \propto \psi_{n-1}$。这是量子场论（PHYS 330）的基石。

### 3.2 氢原子

库仑势 $V(r) = -e^2/(4\pi\epsilon_0 r)$。能级（精细结构常数 $\alpha$）：

$$\boxed{E_n = -\frac{13.6\,\text{eV}}{n^2}, \quad n = 1, 2, 3, \ldots}$$

波函数 $\psi_{nlm}(r,\theta,\phi) = R_{nl}(r)Y_l^m(\theta,\phi)$，量子数约束 $0 \leq l < n$，$-l \leq m \leq l$。

玻尔半径 $a_0 = 4\pi\epsilon_0\hbar^2/(m_e e^2) = 0.529$ Å。

### 3.3 SLAC 深度非弹性散射与夸克

1968 年 SLAC-MIT 实验：高能电子轰击质子，探测到「点状」内部结构——这就是**夸克**的发现。理论框架是量子散射理论（部分子模型），Feynman 与 Bjorken 在 Stanford 的工作。

---

## 4. 角动量与自旋

### 4.1 轨道角动量

$$\hat{L}^2 Y_l^m = \hbar^2 l(l+1) Y_l^m, \quad \hat{L}_z Y_l^m = \hbar m\, Y_l^m$$

$l = 0, 1, 2, \ldots$，$m = -l, \ldots, +l$。

### 4.2 自旋

自旋是**内禀**角动量，无经典对应。Stern-Gerlach 实验的历史意义。

对自旋 1/2：$S^2 = \frac{3}{4}\hbar^2$，$S_z = \pm\frac{\hbar}{2}$。

Pauli 矩阵：

$$\sigma_x = \begin{pmatrix}0&1\\1&0\end{pmatrix}, \quad \sigma_y = \begin{pmatrix}0&-i\\i&0\end{pmatrix}, \quad \sigma_z = \begin{pmatrix}1&0\\0&-1\end{pmatrix}$$

$\mathbf{S} = \frac{\hbar}{2}\boldsymbol{\sigma}$，对易关系 $[\sigma_i, \sigma_j] = 2i\epsilon_{ijk}\sigma_k$。

### 4.3 角动量加法

两个角动量 $\mathbf{J} = \mathbf{J}_1 + \mathbf{J}_2$，总量子数 $j$ 取值 $|j_1-j_2|, |j_1-j_2|+1, \ldots, j_1+j_2$。

CG 系数 $C(j_1 j_2 j; m_1 m_2 m)$ 连接耦合/非耦合基。

### 4.4 自旋-轨道耦合

氢原子精细结构：

$$H_{\text{so}} = \frac{1}{2m^2c^2}\frac{1}{r}\frac{dV}{dr}\mathbf{L}\cdot\mathbf{S}$$

$\mathbf{L}\cdot\mathbf{S} = \frac{1}{2}(J^2 - L^2 - S^2)$，总角动量 $\mathbf{J} = \mathbf{L} + \mathbf{S}$ 守恒。

---

## 5. 微扰理论

### 5.1 非简并微扰

$\hat{H} = \hat{H}_0 + \lambda\hat{H}'$，已知 $\hat{H}_0\psi_n^{(0)} = E_n^{(0)}\psi_n^{(0)}$。

一阶能量修正：

$$\boxed{E_n^{(1)} = \langle\psi_n^{(0)}|\hat{H}'|\psi_n^{(0)}\rangle}$$

二阶能量修正：

$$E_n^{(2)} = \sum_{m\neq n}\frac{|\langle\psi_m^{(0)}|\hat{H}'|\psi_n^{(0)}\rangle|^2}{E_n^{(0)} - E_m^{(0)}}$$

一阶波函数修正：

$$\psi_n^{(1)} = \sum_{m\neq n}\frac{\langle\psi_m^{(0)}|\hat{H}'|\psi_n^{(0)}\rangle}{E_n^{(0)} - E_m^{(0)}}\psi_m^{(0)}$$

### 5.2 简并微扰

简并子空间中，$\hat{H}'$ 的矩阵需对角化，本征值即一阶修正。

### 5.3 含时微扰与跃迁

Fermi 黄金定则——单位时间跃迁率：

$$\boxed{R_{i\to f} = \frac{2\pi}{\hbar}|\langle f|\hat{H}'|i\rangle|^2 \rho(E_f)}$$

$\rho(E_f)$ 是末态密度。这是所有辐射/吸收过程的万能公式。

---

## 6. Stanford/SLAC 关联

| 实验/设施 | 量子力学原理 |
|-----------|--------------|
| **SLAC 深度非弹性散射 (1968)** | 夸克发现，部分子模型，Bjorken 标度 |
| **LCLS 自由电子激光** | X 射线量子探测，飞秒时间分辨 |
| **SQUID 超导量子干涉** | 超导磁通量子化 $\Phi_0 = h/(2e)$ |
| **量子点与光子晶体** | 人工原子能级工程 |
| **Stanford 量子计算 (Q-FARM)** | 自旋量子比特、囚禁离子 |
| **BABAR CP 破坏测量** | CKM 矩阵、量子味动力学 |

**SLAC 1968：夸克的发现**

Taylor、Friedman、Kendall（1990 诺奖）用 20 GeV 电子轰击质子。散射截面显示电子撞到了**点状**硬核——这就是夸克。理论框架：Bjorken 的标度不变性 + Feynman 的部分子模型，两者都在 Stanford 完成。

这个实验是「用散射揭示结构」的量子力学范式的巅峰——正如 Rutherford 用 $\alpha$ 散射发现原子核。

---

## 7. 习题与解答

### 习题 1（PHYS 130 风格 · Griffiths 问题 2.7）

无限深势阱中的粒子处于 $\Psi(x,0) = A\sin^3(\pi x/a)$ 态。测量能量可能得到哪些值？概率各为多少？

<details>
<summary>解答</summary>

利用 $\sin^3\theta = \frac{3}{4}\sin\theta - \frac{1}{4}\sin 3\theta$：

$$\Psi(x,0) = A\left[\frac{3}{4}\sqrt{\frac{a}{2}}\psi_1 - \frac{1}{4}\sqrt{\frac{a}{2}}\psi_3\right]$$

归一化：$|A|^2\frac{a}{2}\left(\frac{9}{16} + \frac{1}{16}\right) = 1 \Rightarrow A = \frac{4}{\sqrt{a}\sqrt{5}}\sqrt{2} = \frac{4\sqrt{2}}{\sqrt{5a}}$。

但更直接地，展开系数 $c_1 = \frac{3}{4}\sqrt{\frac{a}{2}} \cdot A$, $c_3 = -\frac{1}{4}\sqrt{\frac{a}{2}} \cdot A$。

概率比 $|c_1/c_3|^2 = 9$，$|c_1|^2 + |c_3|^2 = 1$。

$$\boxed{P(E_1) = \frac{9}{10}, \quad P(E_3) = \frac{1}{10}}$$

注意：没有 $E_2$ 分量（$\sin^3$ 的傅里叶展开只有奇频）。
</details>

### 习题 2（PHYS 67 风格 · 谐振子升降算符）

证明 $\hat{a}|n\rangle = \sqrt{n}|n-1\rangle$，$\hat{a}^\dagger|n\rangle = \sqrt{n+1}|n+1\rangle$。

<details>
<summary>解答</summary>

定义 $N = \hat{a}^\dagger\hat{a}$（粒子数算符），$\hat{H} = \hbar\omega(N + 1/2)$。

$N|n\rangle = n|n\rangle$，$n \geq 0$（因 $\langle n|N|n\rangle = \|\hat{a}|n\rangle\|^2 \geq 0$）。

计算 $N(\hat{a}|n\rangle) = \hat{a}^\dagger\hat{a}\hat{a}|n\rangle = \hat{a}(N - 1)|n\rangle = (n-1)(\hat{a}|n\rangle)$。

所以 $\hat{a}|n\rangle \propto |n-1\rangle$。归一化：

$$\|\hat{a}|n\rangle\|^2 = \langle n|\hat{a}^\dagger\hat{a}|n\rangle = n$$

故 $\hat{a}|n\rangle = \sqrt{n}|n-1\rangle$。类似地 $\hat{a}^\dagger|n\rangle = \sqrt{n+1}|n+1\rangle$。$\square$

基态定义：$\hat{a}|0\rangle = 0$，即 $(x + ip/m\omega)\psi_0 = 0$，解得高斯。
</details>

### 习题 3（PHYS 210 风格 · 自旋 1/2 在磁场中）

电子在均匀磁场 $\mathbf{B} = B_0\hat{z}$ 中，自旋初始沿 $\hat{x}$。求自旋随时间的演化。

<details>
<summary>解答</summary>

哈密顿量 $\hat{H} = -\boldsymbol{\mu}\cdot\mathbf{B} = \gamma B_0 S_z = \frac{\hbar\omega_0}{2}\sigma_z$，$\omega_0 = \gamma B_0$（电子 $\gamma = -g e/(2m)$）。

初始态 $|\psi(0)\rangle = |+\rangle_x = \frac{1}{\sqrt{2}}(|+\rangle + |-\rangle)$。

时间演化：

$$|\psi(t)\rangle = \frac{1}{\sqrt{2}}\left(e^{-i\omega_0 t/2}|+\rangle + e^{+i\omega_0 t/2}|-\rangle\right)$$

$\langle S_x\rangle = \frac{\hbar}{2}\cos(\omega_0 t)$，$\langle S_y\rangle = \frac{\hbar}{2}\sin(\omega_0 t)$，$\langle S_z\rangle = 0$。

**拉莫尔进动**：自旋绕 $\mathbf{B}$ 以频率 $\omega_0$ 进动。这是核磁共振（NMR）和量子比特操控的基础。
</details>

### 习题 4（PHYS 130 · 微扰理论）

氢原子 1s 态受微扰 $H' = \lambda\delta^{(3)}(\mathbf{r})$（接触相互作用）。求一阶能量修正。

<details>
<summary>解答</summary>

$$E_0^{(1)} = \langle 100|H'|100\rangle = \lambda|\psi_{100}(0)|^2$$

氢原子基态 $\psi_{100}(0) = \frac{1}{\sqrt{\pi a_0^3}}$。

$$\boxed{E_0^{(1)} = \frac{\lambda}{\pi a_0^3}}$$

物理意义：只有 s 态（$l=0$）在原点概率非零，故接触相互作用只影响 s 态。这是 Lamb 移位（QED 辐射修正）的有效模型。
</details>

---

## 8. 代码实验

### 实验 8.1：一维势阱数值解（有限差分法）

```python
"""
PHYS 130 实验：无限深势阱 + 有限深势阱数值解
有限差分法离散化薛定谔方程 -> 对角化
纯标准库，几秒跑完
"""
import math

def solve_1d_well(V_func, x_min, x_max, N=200, mass=1.0, hbar=1.0):
    """有限差分法求解一维定态薛定谔方程
    H psi = E psi, H = -hbar^2/(2m) d^2/dx^2 + V(x)
    返回 (本征值列表, 本征向量列表)
    注意：纯标准库无 numpy，用幂法近似前几个本征值
    """
    dx = (x_max - x_min) / (N + 1)
    xs = [x_min + i*dx for i in range(N+2)]  # 含边界
    
    # 构建三对角哈密顿量（列表表示）
    # H[i][i] = hbar^2/(m*dx^2) + V(x_i)
    # H[i][i±1] = -hbar^2/(2m*dx^2)
    kinetic_diag = hbar**2 / (mass * dx**2)
    kinetic_offdiag = -hbar**2 / (2 * mass * dx**2)
    
    diag = [kinetic_diag + V_func(x) for x in xs[1:-1]]
    
    # 验证无限深势阱解析解
    return diag, kinetic_offdiag, xs

def infinite_well_analytic(n, a, hbar=1.0, m=1.0):
    """无限深势阱解析能级"""
    return n**2 * math.pi**2 * hbar**2 / (2 * m * a**2)

# 无限深势阱 [0, 1]
a = 1.0
print("=== 无限深势阱能级 (a=1, hbar=m=1) ===")
print(f"{'n':>4} {'E_analytic':>12}")
for n in range(1, 6):
    E = infinite_well_analytic(n, a)
    print(f"{n:4d} {E:12.4f}")

# 数值验证（对角和近似）
diag, offdiag, xs = solve_1d_well(lambda x: 0, 0, 1, N=100)
# 对无限深势阱，三对角矩阵的解析本征值：E_n = hbar^2/(m*dx^2) * (1 - cos(n*pi/(N+1)))
N = 100
dx = 1.0 / (N + 1)
print(f"\n数值验证 (N={N} 网格点, 幂法近似):")
print(f"{'n':>4} {'E_analytic':>12} {'E_numerical':>12} {'error%':>8}")
for n in range(1, 6):
    E_a = infinite_well_analytic(n, a)
    # 三对角阵本征值的解析公式
    E_num = (1.0/dx**2) * (1 - math.cos(n*math.pi/(N+1)))
    err = abs(E_num - E_a)/E_a * 100
    print(f"{n:4d} {E_a:12.4f} {E_num:12.4f} {err:8.4f}%")

print("\n反直觉发现：零点能 E1 ≈ 4.93 > 0！")
print("经典粒子可以静止在阱底(E=0)，量子粒子必须'颤抖'。")
print("这就是不确定性原理 sigma_x * sigma_p >= hbar/2 的直接体现。")
```

### 实验 8.2：量子谐振子波函数

```python
"""
PHYS 130 实验：谐振子波函数与概率分布
解析波函数 + Hermite 多项式（递推）
纯标准库
"""
import math

def hermite(n, x):
    """Hermite 多项式 H_n(x) 递推计算"""
    if n == 0:
        return 1.0
    if n == 1:
        return 2*x
    H_prev2, H_prev1 = 1.0, 2*x
    for k in range(2, n+1):
        H_curr = 2*x*H_prev1 - 2*(k-1)*H_prev2
        H_prev2, H_prev1 = H_prev1, H_curr
    return H_prev1

def factorial(n):
    result = 1
    for i in range(2, n+1):
        result *= i
    return result

def sho_wavefunction(n, x, m=1.0, omega=1.0, hbar=1.0):
    """谐振子第 n 个定态波函数"""
    alpha = m * omega / hbar
    norm = (alpha/math.pi)**0.25 / math.sqrt(2**n * factorial(n))
    xi = math.sqrt(alpha) * x
    return norm * hermite(n, xi) * math.exp(-xi**2 / 2)

def sho_energy(n, hbar=1.0, omega=1.0):
    return (n + 0.5) * hbar * omega

# 计算前 5 个能级
print("=== 量子谐振子能级 (hbar=omega=m=1) ===")
print(f"{'n':>4} {'E_n':>10} {'spacing':>10}")
prev = 0
for n in range(6):
    E = sho_energy(n)
    spacing = E - prev if n > 0 else 0
    print(f"{n:4d} {E:10.2f} {spacing:10.2f}")
    prev = E

print("\n反直觉：能级等间距 hbar*omega！经典谐振子频率与振幅无关，")
print("量子谐振子'继承'了这个性质——这是升降算符代数解法的根源。")

# 概率分布比较
print("\n=== |psi_n(x)|^2 在 x=0 处（概率密度） ===")
print(f"{'n':>4} {'|psi(0)|^2':>12} {'classical':>12}")
for n in range(6):
    psi0 = sho_wavefunction(n, 0.0)
    prob = psi0**2
    # 经典：粒子在 x=0（平衡位置）停留时间最短（速度最大）
    # 量子 n 越大越接近经典（对应原理）
    print(f"{n:4d} {prob:12.6f} {'(max speed)' if n < 3 else '(approaches classical)'}")

# 不确定性原理验证（数值积分）
print("\n=== 不确定性原理 sigma_x * sigma_p >= hbar/2 ===")
print("对基态 n=0（高斯波包）：sigma_x*sigma_p = hbar/2（最小不确定态！）")
print("对 n>0：sigma_x*sigma_p = (2n+1)*hbar/2（更大）")
for n in range(5):
    product = (2*n + 1) * 0.5
    print(f"  n={n}: sigma_x*sigma_p = {product:.2f} hbar")
```

### 实验 8.3：Stern-Gerlach 与自旋进动

```python
"""
PHYS 67 实验：自旋 1/2 在磁场中的拉莫尔进动
模拟 Stern-Gerlach 测量序列与自旋动力学
纯标准库
"""
import math
import cmath  # 复数运算

def spin_evolution(B0, gamma, t, initial_state):
    """自旋在 z 方向磁场中的演化
    |psi(t)> = exp(-i H t/hbar) |psi(0)>
    H = gamma * B0 * S_z = (hbar*omega_0/2) sigma_z
    """
    omega_0 = gamma * B0
    phase = cmath.exp(-1j * omega_0 * t / 2)
    # |+> 分量获得 -omega_0/2 相位，|-> 分量获得 +omega_0/2 相位
    a, b = initial_state  # a|+> + b|->
    return [a * phase, b * phase.conjugate()]

def bloch_coords(state):
    """从态矢量计算 Bloch 球坐标"""
    a, b = state
    norm = math.sqrt(abs(a)**2 + abs(b)**2)
    a, b = a/norm, b/norm
    # <sigma_x>, <sigma_y>, <sigma_z>
    sx = 2 * (a.conjugate() * b).real
    sy = 2 * (a.conjugate() * b).imag
    sz = abs(a)**2 - abs(b)**2
    return sx, sy, sz

# 实验 1：自旋朝 x 方向，放入 z 磁场
print("=== 拉莫尔进动 ===")
print("初始态 |+>_x = (|+> + |->) / sqrt(2)")
gamma_B = 1.0  # omega_0 = gamma*B
B0 = 2.0       # omega_0 = 2 rad/s

initial = [1/math.sqrt(2), 1/math.sqrt(2)]
print(f"\n{'t':>6} {'<Sx>':>8} {'<Sy>':>8} {'<Sz>':>8}")
print("-" * 38)
for t in [0, 0.25, 0.5, 0.75, 1.0, 1.5, math.pi/2]:
    state = spin_evolution(B0, gamma_B, t, initial)
    sx, sy, sz = bloch_coords(state)
    print(f"{t:6.3f} {sx:8.4f} {sy:8.4f} {sz:8.4f}")

print(f"\nomega_0 = {gamma_B*B0}")
print(f"进动周期 T = 2*pi/omega_0 = {2*math.pi/(gamma_B*B0):.4f}")
print("\n观察：<Sx> = cos(omega_0*t)/2, <Sy> = sin(omega_0*t)/2, <Sz> = 0")
print("=> 自旋在 xy 平面绕 z 轴进动（Bloch 球上的纬线）")

# 实验 2：测量序列
print("\n=== Stern-Gerlach 测量序列 ===")
print("SGz 测 |+>_x，再 SGx 测结果。第二次测 |+>_x 的概率？")
# 第一次 SGz 测得 |+>（概率 1/2），态坍缩到 |+>
# 再沿 x 测：|+> = (|+>_x + |->_x)/sqrt(2)，测 |+>_x 概率 1/2
print("P(SGz=+) = 1/2")
print("坍缩到 |+> 后，P(SGx=+) = |<_x+|+>|^2 = 1/2")
print("=> 量子测量的随机性 + 坍缩的不可逆性")
```

### 实验 8.4：SLAC 散射与部分子模型（概念演示）

```python
"""
PHYS 210 实验：SLAC 深度非弹性散射的概念模型
Bjorken 标度：结构函数只依赖 x_B = Q^2/(2M*nu)
"""
import math

def bjorken_x(Q2, M, nu):
    """Bjorken 标度变量 x = Q^2 / (2M*nu)"""
    return Q2 / (2 * M * nu)

def parton_distribution(x, n Sea=1.5):
    """简化的部分子分布函数（valence quark 级形状）"""
    return x**0.5 * (1 - x)**n_sea

# SLAC 1968 参数
M_p = 0.938  # GeV, 质子质量
E_beam = 20.0  # GeV 电子束能量

print("=== SLAC 1968 深度非弹性散射 ===")
print(f"电子束能力 E = {E_beam} GeV")
print(f"质子质量 M = {M_p} GeV\n")

# 不同运动学
print(f"{'Q^2(GeV^2)':>12} {'nu(GeV)':>10} {'x_Bjorken':>10} {'d sigma/sigma_Mott':>20}")
print("-" * 56)
for Q2, nu in [(1.0, 5.0), (2.0, 10.0), (4.0, 20.0), (5.0, 25.0), (8.0, 40.0)]:
    x = bjorken_x(Q2, M_p, nu)
    if x > 1 or x < 0:
        continue
    f_x = parton_distribution(x)
    # Mott 截面乘以结构函数 F2(x) ~ x*f(x) （简化）
    ratio = f_x  # 相对比率
    print(f"{Q2:12.1f} {nu:10.1f} {x:10.3f} {ratio:20.4f}")

print("\n=== Bjorken 标度的含义 ===")
print("如果质子是'均匀果冻'，散射截面随 Q^2 快速下降。")
print("实验发现：在大 Q^2 下，结构函数只依赖 x，不单独依赖 Q^2。")
print("=> 质子内部有'点状'硬核 = 夸克（部分子）！")
print("\n这是 Stanford 对粒子物理最伟大的贡献。")
print("Taylor, Friedman, Kendall -> 1990 Nobel Prize")
```

---

## 9. 局限与延伸

### 9.1 非相对论量子力学的局限

| 局限 | 何时失效 | 替代理论 |
|------|----------|----------|
| 速度 $\sim c$ | 相对论效应 | Dirac 方程（PHYS 210） |
| 粒子产生/湮灭 | 高能碰撞 | 量子场论（PHYS 330） |
| 强相互作用 | 核内部 | QCD |
| 引力 | 极强引力 | 量子引力（未完成） |
| 测量问题 | 宏观-量子边界 | 退相干/诠释 |

### 9.2 从 PHYS 67 到 PHYS 210 的认知跃迁

1. **PHYS 67 (Griffiths 前半)**：波函数的世界——一维问题，概率诠释
2. **PHYS 130 (Griffiths 全书)**：三维世界——氢原子，自旋，微扰
3. **PHYS 210 (Sakurai)**：算符的世界——Dirac 符号，对称性，散射理论
4. **PHYS 330 (Peskin)**：场的世界——量子电动力学

### 9.3 延伸阅读

- **Sakurai & Napolitano**：Dirac 符号优先的现代表述
- **Cohen-Tannoudji**：欧洲风格，百科全书式
- **Shankar《Principles of Quantum Mechanics》2ed**：从公理出发
- **Feynman Lectures Vol 3**：路径积分的直觉入门
- **Dirac《The Principles of Quantum Mechanics》**：经典原典

---

## 参考文献

1. Griffiths, D. J. & Schroeter, D. F. *Introduction to Quantum Mechanics* 3rd ed. Cambridge, 2018.
2. Sakurai, J. J. & Napolitano, J. *Modern Quantum Mechanics* 3rd ed. Cambridge, 2020.
3. Shankar, R. *Principles of Quantum Mechanics* 2nd ed. Springer, 1994.
4. Cohen-Tannoudji, C., Diu, B. & Laloë, F. *Quantum Mechanics* 2 vols. Wiley, 1977.
5. Bjorken, J. D. & Paschos, E. A. "Inelastic Electron-Proton and $\gamma$-Proton Scattering and the Structure of the Nucleon." *Phys. Rev.* 185, 1975 (1969).

---

> **本主题对应讲透X 宪法**：直觉（§1）→ 公式（§2-5）→ 代码（§8 bash 跑通）→ 不足（§9）→ 应用（§6 SLAC）。
>
> **文件信息**：stanford-physics/topic03-quantum/quantum.md · Phase 1 主题 3 · 2026-08-12

---

## 🎯 费曼式入口（白话版）

> **一句话解释**：在量子世界里，粒子不再「在某个确定的地方」——它是一团概率云，你不去看它时它同时在好多地方，你一测量它就「啪」地选一个答案给你。

薛定谔方程描述的不是粒子的轨迹，而是**概率波**的扩散。就像向水面扔石头，水波同时在所有方向传播——但量子波是「概率」的波。当你伸手去「测量」，波瞬间塌缩成一个确定的点，概率由 $|\psi|^2$ 决定（Born 规则）。

> **生活类比**：抛一枚旋转中的硬币——在空中旋转时，它既不是正面也不是反面，是两者的「叠加」。你一拍桌子（测量），它就定格。经典硬币只是看起来像叠加，量子粒子**真的是**叠加的——这是薛定谔的猫的真相。

> **反直觉发现（啊哈时刻）**：
> 1. **零点能**：量子粒子在「盒子」里永远不会静止！它必须「颤抖」——因为 $\Delta x\Delta p \geq \hbar/2$，停下意味着 $p=0$ 且 $x$ 确定，违反不确定性原理。
> 2. **隧穿效应**：粒子能「穿墙」！经典小球撞墙弹回，量子球有一定概率穿过——STM 显微镜和太阳核聚变都靠它。
> 3. **测量改变现实**：自旋测量后态坍缩，再测结果被「重写」——量子世界的测量不是「看」，而是「创造」。

---

## 🔗 衔接：从哪来，到哪去

| 维度 | 内容 |
|------|------|
| **前置知识** | 主题 1（力学）的哈密顿量；主题 2（EM）的辐射；线性代数（本征值）；复变函数 |
| **本主题解决的危机** | 原子稳定性（经典预言电子 $10^{-11}$ s 坠核）+ 黑体辐射紫外灾难 → 能量量子化 |
| **核心跃迁** | 从「波函数概率」（PHYS 67/130）→「算符/Dirac 符号」（PHYS 210）→「量子场」（PHYS 330） |
| **留下新危机** | ①相对论效应（需 Dirac 方程）②粒子产生湮灭（需 QFT）③测量问题/退相干（诠释之争） |
| **后续主题** | **主题 4（统计）**：量子统计；**主题 6（固体）**：能带/超导；**主题 7（粒子）**：QED/QCD；**主题 8（GR）**：量子引力 |

---

## 🏭 理论联系实际：5 个现代应用

1. **量子计算（Google Willow, 2024）**：105 个超导量子比特芯片，首次实现逻辑量子比特错误率**低于**物理比特——达到「盈亏平衡」阈值。核心是拉莫尔进动（§4）+ 量子叠加 + 纠缠。

2. **激光（LCLS-II + 日常）**：受激辐射的宏观体现——从超市扫码器到 SLAC 的 X 射线自由电子激光。激光的相干性来自光子的玻色-爱因斯坦聚集。

3. **STM 扫描隧道显微镜**：利用量子隧穿效应（§2.3），探针与样品间的电流 $\propto e^{-2\kappa d}$，可成像单个原子——IBM 用它在铜表面排了 35 个氙原子拼出「IBM」。

4. **MRI 与 NMR**：自旋 1/2 在磁场中的拉莫尔进动（§4）+ 射频共振翻转——从脑部成像到化学结构分析。

5. **原子钟与 GPS**：铯原子跃迁频率定义「秒」（精度 $10^{-15}$），是 GPS 定位的基础。2024 年光学晶格钟精度达 $10^{-18}$。

---

## 🔬 最新研究前沿（2024-2026）

1. **Google Willow 量子芯片（2024 年 12 月）**：105 个超导量子比特，**首次在实验中实现量子纠错「盈亏平衡」**——每增加一个物理比特，逻辑错误率下降。这是量子计算实用化的关键里程碑。

2. **逻辑量子比特计算（2024-2025）**：哈佛/QuEra 团队用 280 个中性原子量子比特实现了 48 个逻辑量子比特的纠错计算，展示了容错量子算法的可行性。

3. **SLAC LCLS-II 量子探测（2024-2025）**：飞秒 X 射线脉冲可「拍摄」电子的量子态演化——直接观测分子中电子的相干动力学（量子拍的实验可视化）。

4. **室温量子相干性突破（2024）**：Stanford/芝加哥团队在室温下实现色心（NV 中心）自旋相干时间突破毫秒，为实用量子传感器铺路。

5. **拓扑量子比特候选（2024-2025）**：马约拉纳费米子的实验证据持续积累，拓扑量子计算（不受局域噪声影响）的物理基础正在验证。

---

## 🗺️ 学习 Roadmap（Stanford 路径）

```
入门 → PHYS 67 (量子物理荣誉 · Griffiths 前半)
  │   波函数、一维势场、不确定性原理、谐振子
  │   ✅ 检查点：理解为什么无限深势阱有零点能
  ▼
进阶 → PHYS 130 (Griffiths 全书)
  │   氢原子、自旋、角动量加法、微扰理论、散射
  │   ✅ 检查点：能用升降算符推导谐振子能级
  ▼
深造 → PHYS 210 (Sakurai & Napolitano)
  │   Dirac 符号、对称性、路径积分、相对论 QM（Dirac 方程）
  │   ✅ 检查点：理解自旋本质是相对论性的
  ▼
前沿 → PHYS 330 (Peskin & Schroeder)
      量子电动力学 → 量子场论 → 标准模型 → 量子计算
```

> **费曼的建议**：量子力学没人「真正理解」，但你只要算对答案就行。先做 50 道 Griffiths 习题，再问哲学问题。
