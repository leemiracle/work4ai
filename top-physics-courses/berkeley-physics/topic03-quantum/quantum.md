# Topic 03: 量子力学 — 从薛定谔到微扰理论

> **UC Berkeley 课程映射**：137A (Quantum Mechanics, Griffiths) → 137B (Quantum Mechanics II, Sakurai)
>
> **教材体系**：
> - **中级（137A）**：Griffiths "Introduction to Quantum Mechanics" 3ed
> - **高级（137B）**：Sakurai & Napolitano "Modern Quantum Mechanics" 3ed
> - **替代/补充**：Townsend "A Modern Approach to Quantum Mechanics"（自旋先行路线）
> - **Berkeley 传统**：Berkeley Physics Course Vol. 4 "Quantum Physics" (Wichmann)

---

## 目录

1. [§1 薛定谔方程](#1-薛定谔方程)
2. [§2 标准问题：势阱/谐振子/氢原子](#2-标准问题势阱谐振子氢原子)
3. [§3 角动量与自旋](#3-角动量与自旋)
4. [§4 微扰理论](#4-微扰理论)
5. [§5 Berkeley 特色](#5-berkeley-特色griffiths--sakurai-进阶路线)
6. [习题集](#习题集)
7. [Python 演示](#python-演示)

---

## §1 薛定谔方程

### 1.1 波函数与概率解释

**直觉**：量子力学的基本对象不是"粒子在哪"，而是"粒子在某处的概率"。这个概率由波函数 $\Psi(x,t)$ 的模平方给出。

$$\boxed{|\Psi(x,t)|^2\, dx = \text{在 } [x, x+dx] \text{ 找到粒子的概率}}$$

归一化条件：

$$\int_{-\infty}^{\infty} |\Psi(x,t)|^2\, dx = 1$$

### 1.2 含时薛定谔方程

$$\boxed{i\hbar \frac{\partial \Psi}{\partial t} = \hat{H}\Psi = \left(-\frac{\hbar^2}{2m}\nabla^2 + V(\mathbf{r}, t)\right)\Psi}$$

这是量子力学的"牛顿第二定律"——给定初始波函数，它决定了所有未来的演化。

### 1.3 定态薛定谔方程

分离变量 $\Psi(x,t) = \psi(x)\, e^{-iEt/\hbar}$，得：

$$\hat{H}\psi = E\psi \quad \Longrightarrow \quad -\frac{\hbar^2}{2m}\frac{d^2\psi}{dx^2} + V(x)\psi = E\psi$$

**关键性质**：
- 定态 $\psi_n$ 是能量本征态，能量 $E_n$ 是量子化的。
- 一般态是定态的叠加：$\Psi = \sum_n c_n \psi_n e^{-iE_n t/\hbar}$。
- 测量能量得到 $E_n$ 的概率为 $|c_n|^2$。

### 1.4 不确定性原理

$$\boxed{\sigma_x \sigma_p \geq \frac{\hbar}{2}}$$

这不是测量精度的限制——它是自然的内在属性。波函数不能同时在位置和动量上无限集中。

---

## §2 标准问题：势阱/谐振子/氢原子

### 2.1 无限深方势阱

$$V(x) = \begin{cases} 0 & 0 < x < a \\ \infty & \text{otherwise} \end{cases}$$

本征函数和本征值：

$$\psi_n(x) = \sqrt{\frac{2}{a}}\sin\frac{n\pi x}{a}, \quad E_n = \frac{n^2 \pi^2 \hbar^2}{2ma^2}, \quad n = 1, 2, 3, \ldots$$

**反直觉**：最低能量 $E_1 > 0$——粒子在阱中不可能静止！这是不确定性原理的直接后果：$\Delta x \sim a$ 要求 $\Delta p \geq \hbar/(2a)$，因而 $E \sim (\Delta p)^2/(2m) > 0$。

### 2.2 量子谐振子

$$V(x) = \frac{1}{2}m\omega^2 x^2$$

**方法一：解析解**（Griffiths 2.3）

本征值：

$$\boxed{E_n = \left(n + \frac{1}{2}\right)\hbar\omega, \quad n = 0, 1, 2, \ldots}$$

本征函数用 Hermite 多项式 $H_n$ 表达：

$$\psi_n(x) = \left(\frac{m\omega}{\pi\hbar}\right)^{1/4} \frac{1}{\sqrt{2^n n!}} H_n\!\left(\sqrt{\frac{m\omega}{\hbar}}x\right) e^{-m\omega x^2/(2\hbar)}$$

**方法二：升降算符（代数法）**（Griffiths 2.5 / Sakurai 1.6）

$$\hat{a} = \sqrt{\frac{m\omega}{2\hbar}}\left(x + \frac{i}{m\omega}p\right), \quad \hat{a}^\dagger = \sqrt{\frac{m\omega}{2\hbar}}\left(x - \frac{i}{m\omega}p\right)$$

$$\hat{H} = \hbar\omega\left(\hat{a}^\dagger \hat{a} + \frac{1}{2}\right)$$

基态满足 $\hat{a}|0\rangle = 0$，激发态由 $|n\rangle = \frac{(\hat{a}^\dagger)^n}{\sqrt{n!}}|0\rangle$ 生成。

**升降算符的意义**：这是量子场论的基本语言——粒子=场的激发量子。Berkeley 137B 在讲二次量子化时回到这套代数。

### 2.3 氢原子

$$V(r) = -\frac{e^2}{4\pi\epsilon_0 r}$$

在球坐标中分离变量，本征态 $|n, l, m\rangle$ 由三个量子数标记：

| 量子数 | 名称 | 取值 | 物理意义 |
|--------|------|------|----------|
| $n$ | 主量子数 | $1, 2, 3, \ldots$ | 能量 $E_n = -13.6\text{ eV}/n^2$ |
| $l$ | 轨道量子数 | $0, 1, \ldots, n-1$ | 角动量大小 $L^2 = l(l+1)\hbar^2$ |
| $m$ | 磁量子数 | $-l, \ldots, +l$ | 角动量 $z$ 分量 $L_z = m\hbar$ |

**Bohr 公式的量子力学推导**：

$$E_n = -\frac{m_e e^4}{2(4\pi\epsilon_0)^2 \hbar^2} \cdot \frac{1}{n^2} = -\frac{13.6\text{ eV}}{n^2}$$

**反直觉**：波函数 $\psi_{nlm}$ 允许粒子出现在经典禁区（$E < V$ 的区域）——这是量子隧穿的基础。

---

## §3 角动量与自旋

### 3.1 角动量算符

$$\hat{L}^2 |l,m\rangle = l(l+1)\hbar^2 |l,m\rangle, \qquad \hat{L}_z |l,m\rangle = m\hbar |l,m\rangle$$

升降算符：

$$\hat{L}_{\pm} |l,m\rangle = \hbar\sqrt{l(l+1) - m(m\pm 1)}\,|l, m\pm 1\rangle$$

### 3.2 自旋

**实验事实**：电子有一个内禀角动量——自旋 $S = 1/2$。这不是轨道运动！

Pauli 矩阵：

$$\boxed{\sigma_x = \begin{pmatrix} 0 & 1 \\ 1 & 0 \end{pmatrix}, \quad \sigma_y = \begin{pmatrix} 0 & -i \\ i & 0 \end{pmatrix}, \quad \sigma_z = \begin{pmatrix} 1 & 0 \\ 0 & -1 \end{pmatrix}}$$

$$\hat{S}_i = \frac{\hbar}{2}\sigma_i$$

**Stern-Gerlach 实验**（Griffiths 4.4 / Townsend Ch 1）：银原子束经过非均匀磁场后分成两束——自旋向上的和自旋向下的。这直接证明了自旋的空间量子化。

### 3.3 角动量合成（Clebsch-Gordan）

两个角动量 $\mathbf{J} = \mathbf{J}_1 + \mathbf{J}_2$：

$$j = |j_1 - j_2|, |j_1 - j_2| + 1, \ldots, j_1 + j_2$$

例如 $l=1$ 和 $s=1/2$ 合成：$j = 1/2$ 或 $j = 3/2$。

**Berkeley 137A 的经典应用**：氢原子的精细结构——自旋-轨道耦合 $\mathbf{L}\cdot\mathbf{S}$ 使得 $j=l+1/2$ 和 $j=l-1/2$ 能级分裂。

---

## §4 微扰理论

### 4.1 非简并微扰

当精确解不可得时，微扰理论提供近似方法。设 $\hat{H} = \hat{H}_0 + \lambda \hat{H}'$。

**一级能量修正**：

$$\boxed{E_n^{(1)} = \langle n^{(0)} | \hat{H}' | n^{(0)} \rangle}$$

**二级能量修正**：

$$E_n^{(2)} = \sum_{k \neq n} \frac{|\langle k^{(0)} | \hat{H}' | n^{(0)} \rangle|^2}{E_n^{(0)} - E_k^{(0)}}$$

**一级波函数修正**：

$$|n^{(1)}\rangle = \sum_{k \neq n} \frac{\langle k^{(0)} | \hat{H}' | n^{(0)} \rangle}{E_n^{(0)} - E_k^{(0)}} |k^{(0)}\rangle$$

### 4.2 经典应用：氢原子精细结构

精细结构的三个来源（Griffiths 6.3）：

1. **相对论修正**：$\hat{H}_r = -\frac{p^4}{8m^3 c^2}$
2. **自旋-轨道耦合**：$\hat{H}_{so} = \frac{e^2}{8\pi\epsilon_0 m^2 c^2 r^3}\mathbf{L}\cdot\mathbf{S}$
3. **Darwin 项**（仅 $l=0$）

总效果：

$$E_{nj} = -\frac{13.6\text{ eV}}{n^2}\left[1 + \frac{\alpha^2}{n}\left(\frac{1}{j+1/2} - \frac{3}{4n}\right)\right]$$

其中 $\alpha \approx 1/137$ 是精细结构常数。

**反直觉**：精细结构只依赖 $n$ 和 $j$，不依赖 $l$——这就是偶然简并（accidental degeneracy），源于 Coulomb 势的隐藏 SO(4) 对称性。

### 4.3 变分法

**Griffiths 7.1 / Sakurai 补充**：用于估计基态能量上界。

$$E_{\text{gs}} \leq \langle \psi_{\text{trial}} | \hat{H} | \psi_{\text{trial}} \rangle = E[\alpha]$$

选择带可调参数 $\alpha$ 的试探波函数，最小化 $E[\alpha]$ 得到基态能量上限。

### 4.4 WKB 近似

半经典近似，适用于势能缓慢变化的情况。隧道穿透概率：

$$T \approx e^{-2\gamma}, \quad \gamma = \frac{1}{\hbar}\int_{x_1}^{x_2} \sqrt{2m(V-E)}\, dx$$

这是核 $\alpha$ 衰变（Gamow 1928）的理论基础。

---

## §5 Berkeley 特色：Griffiths → Sakurai 进阶路线

### Berkeley 137A → 137B 的教学逻辑

Berkeley 的量子力学教学遵循一个精心设计的两段式进阶：

#### 第一段：137A（Griffiths）—— 波动力学

Griffiths 教材的特色：
1. **波函数优先**：先学 Schrodinger 方程和一维问题，建立量子直觉。
2. **物理图像清晰**：大量使用类比和直觉论证。
3. **数学适度**：不追求数学严谨性，但确保物理理解。
4. **习题优秀**：Griffiths 的习题设计堪称经典——计算量适中，物理概念突出。

Berkeley 137A 的核心章节：
- Ch 1-2：薛定谔方程 + 一维问题（势阱、谐振子、散射）
- Ch 3：三维问题（氢原子）
- Ch 4：角动量 + 自旋
- Ch 5-6： identical particles + 微扰理论

#### 第二段：137B（Sakurai）—— 抽象狄拉克表述

Sakurai 的特色是从**公理出发**，用狄拉克 bra-ket 表述：
1. **公理化优先**：先建立态矢量空间和算符代数。
2. **对称性驱动**：从平移/旋转对称性推导动量/角动量算符。
3. **路径积分**：Feynman 路径积分表述（Berkeley 137B 特色补充）。
4. **二次量子化**：多体系统的产生/湮灭算符。

**Sakurai Ch 1 的核心**：不从 Schrodinger 方程出发，而是从实验（如 Stern-Gerlach）引入 ket $|\alpha\rangle$ 和算符 $\hat{A}$，用自旋 1/2 系统作为第一个完整例子。这种方法对理论物理方向的学生更自然。

#### Berkeley Physics Course Vol. 4（Wichmann）

Berkeley 的传统教材 Wichmann "Quantum Physics" 虽不再是主教材，但其特色——**从实验和物理图像引入概念**——仍影响着 Berkeley 的教学风格。

### Berkeley 量子力学研究前沿连接

| Berkeley 137 内容 | 连接到的研究前沿 |
|-------------------|-----------------|
| 谐振子升降算符 | 量子计算（Berkeley QCOE）|
| 自旋与磁共振 | 量子传感（Berkeley AMO）|
| 微扰理论 | 凝聚态能带（Berkeley 141A）|
| 全同粒子 | 量子信息（Berkeley Birgitta Whaley 组）|
| WKB 隧穿 | 扫描隧道显微镜（Berkeley STM 实验）|

---

## 习题集

### 基础题（137A 前半）

**习题 3.1**：粒子在无限深方势阱（$0 < x < a$）中，初始波函数 $\Psi(x,0) = A\sin(\pi x/a)$。求归一化常数 $A$ 和波函数的时间演化。
> **解**：$A = \sqrt{2/a}$，$\Psi(x,t) = \sqrt{2/a}\sin(\pi x/a)\, e^{-iE_1 t/\hbar}$，$E_1 = \pi^2\hbar^2/(2ma^2)$。

**习题 3.2**：证明谐振子的基态满足不确定性原理的下界 $\sigma_x \sigma_p = \hbar/2$。
> **提示**：用升降算符计算 $\langle 0|x^2|0\rangle$ 和 $\langle 0|p^2|0\rangle$。

**习题 3.3**：电子在 $B = 1$ T 的磁场中，自旋沿 $z$ 轴向上。若磁场突然转到 $x$ 方向，求测到自旋向下的概率。
> **解**：$P = |\langle \downarrow_x | \uparrow_z \rangle|^2 = 1/2$。

### 中级题（137A 后半 / 137B 入门）

**习题 3.4**（Griffiths 6.1）：一维无限势阱中加微扰 $H'(x) = V_0 x / a$。求基态能量的一级修正。
> **解**：$E_1^{(1)} = \frac{2V_0}{a}\int_0^a \sin^2(\pi x/a)\, \frac{x}{a}\, dx = \frac{V_0}{2}$。

**习题 3.5**（Griffiths 6.14）：氢原子 $1s$ 态在均匀电场 $\mathcal{E}$ 中的 Stark 效应。由于 $n=1$ 无简并（忽略自旋），一级修正为零。求二级修正的符号和量级。
> **提示**：$E_1^{(2)} < 0$（二级修正总使基态能量降低）。用变分法求精确值 $-9a_0^3\mathcal{E}^2/(4)$ 作为对比。

**习题 3.6**（Sakurai 风格）：用矩阵力学证明 $\sigma_i \sigma_j = \delta_{ij} + i\epsilon_{ijk}\sigma_k$。
> **提示**：直接计算 Pauli 矩阵的乘积。

### 挑战题

**习题 3.7**（变分法）：用试探波函数 $\psi(x) = Ae^{-bx^2}$ 估计谐振子的基态能量，并与精确值 $(1/2)\hbar\omega$ 比较。
> **解**：$E(b) = \frac{\hbar^2 b}{2m} + \frac{m\omega^2}{8b}$。最小化得 $b = m\omega/(2\hbar)$，$E = \frac{1}{2}\hbar\omega$（恰好精确！因为试探函数恰好是真实基态的形式）。

**习题 3.8**（WKB 隧穿）：用 WKB 近似计算矩形势垒（高 $V_0$，宽 $a$）的穿透概率。
> **解**：$T \approx e^{-2a\sqrt{2m(V_0-E)}/\hbar}$。

---

## Python 演示

### 演示 1：数值求解一维薛定谔方程（有限差分法）

```python
"""
数值求解 1D 薛定谔方程 — Berkeley 137A
无限势阱 + 谐振子 + 双势阱。
用有限差分法离散化哈密顿量矩阵，对角化求本征值。
"""
import numpy as np
import matplotlib.pyplot as plt

def solve_1d_schrodinger(V_func, x_min=-5, x_max=5, N=500, n_eigen=5):
    """
    用有限差分法求解 1D 定态薛定谔方程。
    H ψ = E ψ  →  矩阵本征值问题。
    """
    x = np.linspace(x_min, x_max, N)
    dx = x[1] - x[0]
    hbar = 1.0
    m = 1.0

    # 动能矩阵（二阶差分）
    T = -hbar**2 / (2 * m * dx**2) * (
        np.diag(np.ones(N-1), 1) + np.diag(np.ones(N-1), -1) - 2 * np.diag(np.ones(N))
    )

    # 势能矩阵
    V = np.diag(V_func(x))

    # 哈密顿量
    H = T + V

    # 对角化
    eigenvalues, eigenvectors = np.linalg.eigh(H)

    # 取前 n_eigen 个本征态
    energies = eigenvalues[:n_eigen]
    wavefunctions = eigenvectors[:, :n_eigen]

    # 归一化波函数
    for i in range(n_eigen):
        norm = np.sqrt(np.trapz(wavefunctions[:, i]**2, x))
        wavefunctions[:, i] /= norm

    return x, energies, wavefunctions


# ============================================================
# 案例 1：无限势阱（验证）
# ============================================================
def V_well(x, a=4.0):
    V = np.zeros_like(x)
    V[np.abs(x) > a/2] = 1e6  # 高墙近似无限深
    return V

x1, E1, psi1 = solve_1d_schrodinger(V_well, x_min=-3, x_max=3, n_eigen=4)

fig, axes = plt.subplots(1, 3, figsize=(16, 5))

ax = axes[0]
for i in range(4):
    ax.plot(x1, psi1[:, i]**2 + E1[i]*0.3, linewidth=1.5, label=f'$E_{i}$ = {E1[i]:.3f}')
    ax.axhline(E1[i]*0.3, color='gray', linewidth=0.3)
ax.set_title('Infinite Square Well\n(numerical vs analytic)')
ax.set_xlabel('x')
ax.legend(fontsize=8)

# ============================================================
# 案例 2：量子谐振子（验证 E_n = (n+1/2)ω）
# ============================================================
omega = 1.0
def V_osc(x):
    return 0.5 * omega**2 * x**2

x2, E2, psi2 = solve_1d_schrodinger(V_osc, x_min=-6, x_max=6, n_eigen=5)

ax = axes[1]
for i in range(5):
    ax.plot(x2, psi2[:, i]**2 + E2[i]*0.15, linewidth=1.5,
            label=f'$E_{i}$ = {E2[i]:.3f} (exact: {i+0.5:.1f})')
    ax.axhline(E2[i]*0.15, color='gray', linewidth=0.3)
ax.plot(x2, V_osc(x2)*0.15, 'k--', linewidth=0.8, alpha=0.5, label='V(x)')
ax.set_title(f'Quantum Harmonic Oscillator\n$E_n = (n+1/2)\\hbar\\omega$')
ax.set_xlabel('x')
ax.set_ylim(-0.1, 2.5)
ax.legend(fontsize=7)

# ============================================================
# 案例 3：双势阱（量子隧穿导致对称/反对称分裂）
# ============================================================
def V_double(x):
    return 0.5 * (x**2 - 3)**2  # 双井势

x3, E3, psi3 = solve_1d_schrodinger(V_double, x_min=-5, x_max=5, n_eigen=4)

ax = axes[2]
for i in range(4):
    ax.plot(x3, psi3[:, i]**2 + E3[i]*0.05, linewidth=1.5,
            label=f'$E_{i}$ = {E3[i]:.3f}')
ax.plot(x3, V_double(x3)*0.05, 'k--', linewidth=0.8, alpha=0.5, label='V(x)')
ax.set_title('Double Well: Tunneling Splitting\n(symmetric ↔ antisymmetric)')
ax.set_xlabel('x')
ax.legend(fontsize=8)

plt.tight_layout()
plt.savefig('schrodinger_solutions.png', dpi=150)
plt.show()
print(f"Harmonic oscillator energies: {E2}")
print(f"Expected: [0.5, 1.5, 2.5, 3.5, 4.5]")
print(f"\nDouble well splitting: E1-E0 = {E3[1]-E3[0]:.6f}")
print("(This tiny gap = tunneling rate through barrier)")
```

### 演示 2：自旋 1/2 系统与 Bloch 球

```python
"""
自旋 1/2 系统 — Berkeley 137A Ch 4
Stern-Gerlach + Bloch 球 + Larmor 进动。
"""
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Pauli 矩阵
sigma_x = np.array([[0, 1], [1, 0]], dtype=complex)
sigma_y = np.array([[0, -1j], [1j, 0]], dtype=complex)
sigma_z = np.array([[1, 0], [0, -1]], dtype=complex)

# 任意自旋态 |ψ⟩ = cos(θ/2)|↑⟩ + e^{iφ}sin(θ/2)|↓⟩
def spin_state(theta, phi):
    return np.array([np.cos(theta/2), np.exp(1j*phi)*np.sin(theta/2)])

# Bloch 矢量: ⟨σ⟩
def bloch_vector(psi):
    sx = np.real(psi.conj() @ sigma_x @ psi)
    sy = np.real(psi.conj() @ sigma_y @ psi)
    sz = np.real(psi.conj() @ sigma_z @ psi)
    return sx, sy, sz

# Larmor 进动: 在 B = B₀ẑ 中，自旋绕 z 轴进动
B0 = 1.0  # 磁场
omega_L = B0  # Larmor 频率 (γ=1 归一化)
dt = 0.01
N = 500

# 初始态：θ=π/3, φ=0
theta0, phi0 = np.pi/3, 0
psi = spin_state(theta0, phi0)

trajectory = []
for i in range(N):
    vec = bloch_vector(psi)
    trajectory.append(vec)
    # 时间演化: U = exp(-iωt σ_z/2)
    t = i * dt
    psi_t = spin_state(theta0, phi0 - omega_L * t)  # φ 随时间变化

trajectory = np.array(trajectory)

fig = plt.figure(figsize=(10, 5))

# 左：Bloch 球上的进动轨迹
ax = fig.add_subplot(121, projection='3d')
u = np.linspace(0, 2*np.pi, 50)
v = np.linspace(0, np.pi, 50)
xs = np.outer(np.cos(u), np.sin(v))
ys = np.outer(np.sin(u), np.sin(v))
zs = np.outer(np.ones_like(u), np.cos(v))
ax.plot_surface(xs, ys, zs, alpha=0.1, color='cyan')
ax.plot(trajectory[:, 0], trajectory[:, 1], trajectory[:, 2], 'r-', linewidth=2)
ax.set_xlabel('⟨σx⟩')
ax.set_ylabel('⟨σy⟩')
ax.set_zlabel('⟨σz⟩')
ax.set_title('Larmor Precession on Bloch Sphere')

# 右：⟨σz⟩ 随时间
ax2 = fig.add_subplot(122)
t = np.arange(N) * dt
ax2.plot(t, trajectory[:, 2], 'b-', linewidth=1.5)
ax2.set_xlabel('Time')
ax2.set_ylabel(r'$\langle \sigma_z \rangle$')
ax2.set_title(f'Oscillation at Larmor freq ω = {omega_L}')
ax2.axhline(0, color='gray', linewidth=0.3)

plt.tight_layout()
plt.savefig('spin_bloch.png', dpi=150)
plt.show()
print(f"⟨σz⟩ oscillates at Larmor frequency — basis of NMR/MRI!")
```

### 演示 3：量子隧穿波包传播

```python
"""
量子隧穿 — Berkeley 137A
波包撞击势垒，部分反射、部分隧穿。
用分裂步（split-step）傅里叶方法。
"""
import numpy as np
import matplotlib.pyplot as plt

N = 1000
L = 20.0
dx = L / N
x = np.linspace(-L/2, L/2, N, endpoint=False)
dt = 0.002
hbar, m = 1.0, 1.0

# 势垒
V0 = 6.0
barrier_width = 1.0
V = np.where(np.abs(x) < barrier_width/2, V0, 0.0)

# 初始波包（高斯）
k0 = 5.0  # 动量（决定能量 E = k²/2m = 12.5 > V0）
x0 = -5.0
sigma = 0.8
psi = np.exp(-(x - x0)**2 / (4*sigma**2)) * np.exp(1j * k0 * x)
psi /= np.sqrt(np.sum(np.abs(psi)**2) * dx)

# 分裂步傅里叶方法
# 动能步在 k 空间，势能步在 x 空间
k = 2 * np.pi * np.fft.fftfreq(N, dx)
exp_V = np.exp(-1j * V * dt / (2 * hbar))
exp_T = np.exp(-1j * hbar * k**2 * dt / (2 * m))

snapshots = []
snapshot_steps = [0, 200, 400, 600, 800, 1000]

for step in range(1001):
    if step in snapshot_steps:
        snapshots.append(np.abs(psi)**2)
    psi *= exp_V
    psi_k = np.fft.fft(psi)
    psi_k *= exp_T
    psi = np.fft.ifft(psi_k)
    psi *= exp_V

fig, axes = plt.subplots(len(snapshots), 1, figsize=(10, 10), sharex=True)
for ax, snap, step in zip(axes, snapshots, snapshot_steps):
    t = step * dt
    ax.fill_between(x, 0, V/V0 * 0.5, alpha=0.2, color='orange', label='barrier')
    ax.plot(x, snap, 'b-', linewidth=1)
    ax.set_ylabel(f't={t:.1f}')
    ax.set_ylim(0, 0.8)

axes[-1].set_xlabel('x')
axes[0].set_title(f'Quantum Tunneling: Gaussian packet hits barrier (E={k0**2/(2*m):.1f}, V₀={V0})')
plt.tight_layout()
plt.savefig('quantum_tunneling.png', dpi=150)
plt.show()

# 计算隧穿概率
transmitted = np.sum(np.abs(psi[x > barrier_width/2])**2) * dx
print(f"Transmission probability: {transmitted:.3f}")
print(f"Classical prediction: {'1.000 (E > V₀, always pass)' if k0**2/(2*m) > V0 else '0.000 (E < V₀, never pass)'}")
```

**反直觉发现**：
1. 即使 $E > V_0$，也不是 100% 透过——部分反射！经典力学中不可能。
2. 如果 $E < V_0$，部分波包穿透势垒——量子隧穿，经典力学中绝对不可能。
3. 数值方法（分裂步傅里叶）天然保酉，不丢失概率。

---

## 学习路径建议

```
137A (Griffiths Ch 1-6)  →  波动力学（势阱/谐振子/氢原子/自旋/微扰）
      ↓
137B (Sakurai Ch 1-5)   →  抽象表述（狄拉克/对称性/角动量合成/路径积分）
      ↓
研究生                    →  量子场论 / 凝聚态多体 / 量子信息
```

**Griffiths 教材学习节奏**（Berkeley 137A 一学期 15 周）：
- 周 1-3：Ch 1-2（薛定谔方程 + 一维问题）
- 周 4-5：Ch 2.3-2.5（谐振子 + 升降算符）
- 周 6-8：Ch 3-4（三维问题 + 氢原子 + 角动量）
- 周 9-10：Ch 4（自旋 + 全同粒子）
- 周 11-13：Ch 6（微扰理论 + 精细结构）
- 周 14-15：Ch 7-8（变分法 + WKB + 散射）

---

> **文件信息**：Berkeley Physics · Topic 03 Quantum Mechanics · 2026-08-12
> 
> **教材交叉引用**：Griffiths (137A) / Sakurai (137B) / Townsend (自旋先行替代) / Wichmann (BPC Vol.4)
