# Topic 03 · 量子力学（MIT 8.04 / 8.05 / 8.06）

> **教材**：Griffiths《Introduction to Quantum Mechanics》3ed + Sakurai & Napolitano《Modern Quantum Mechanics》3ed
>
> **覆盖课程**：
> - **8.04** Quantum Physics I（Griffiths 1-4 章：薛定谔方程、一维问题、自旋）
> - **8.05** Quantum Physics II（Griffiths 6-11 章 + Sakurai：算符、对易、角动量、微扰）
> - **8.06** Quantum Physics III（Sakurai：散射、多体、二次量子化入门）
>
> **宪法**：直觉 → 公式 → 代码(bash 跑通) → 不足 → 应用

---

## 目录

1. [薛定谔方程与波函数](#1-薛定谔方程与波函数)
2. [一维定态问题](#2-一维定态问题)
3. [算符与对易](#3-算符与对易)
4. [角动量与自旋](#4-角动量与自旋)
5. [氢原子](#5-氢原子)
6. [微扰理论](#6-微扰理论)
7. [Python 代码演示](#7-python-代码演示)
8. [习题与解答](#8-习题与解答)
9. [反直觉发现](#9-反直觉发现)
10. [不足与延伸](#10-不足与延伸)

---

## 1. 薛定谔方程与波函数

### 1.1 波函数的统计诠释

量子态由**波函数** $\Psi(\mathbf{r}, t)$ 描述。Born 诠释：

$$
|\Psi(\mathbf{r}, t)|^2\, d^3r = \text{在体积 } d^3r \text{ 中找到粒子的概率}
$$

归一化：$\int |\Psi|^2\, d^3r = 1$。

### 1.2 含时薛定谔方程

$$
\boxed{i\hbar\frac{\partial \Psi}{\partial t} = \hat{H}\Psi = \left(-\frac{\hbar^2}{2m}\nabla^2 + V(\mathbf{r}, t)\right)\Psi}
$$

这是量子力学的"牛顿第二定律"——给定初态 $\Psi(\mathbf{r}, 0)$ 决定全部未来。

### 1.3 定态薛定谔方程

势能不显含 $t$ 时，分离变量 $\Psi(\mathbf{r}, t) = \psi(\mathbf{r})\, e^{-iEt/\hbar}$，得**定态方程**（与时间无关的薛定谔方程）：

$$
\hat{H}\psi = E\psi \qquad \Longleftrightarrow \qquad -\frac{\hbar^2}{2m}\nabla^2\psi + V\psi = E\psi
$$

这是**本征值问题**：能量本征态 $\psi_n$，本征值 $E_n$。

### 1.4 概率守恒（连续性方程）

定义概率密度 $\rho = |\Psi|^2$，概率流 $\mathbf{j} = \frac{\hbar}{m}\text{Im}(\Psi^*\nabla\Psi)$。由薛定谔方程可推出：

$$
\frac{\partial \rho}{\partial t} + \nabla\cdot\mathbf{j} = 0
$$

形式同电荷守恒——概率"不会凭空消失"。

---

## 2. 一维定态问题

### 2.1 无限深势阱

$V(x) = 0$ for $0 < x < a$，外部 $V = \infty$。边界条件 $\psi(0) = \psi(a) = 0$。

通解 $\psi_n(x) = \sqrt{2/a}\sin(n\pi x/a)$，能级：

$$
E_n = \frac{n^2 \pi^2 \hbar^2}{2ma^2}, \qquad n = 1, 2, 3, \dots
$$

**关键特征**：
- **离散能级**（量子化）——经典是连续的。
- **零点能** $E_1 = \pi^2\hbar^2/(2ma^2) > 0$——海森堡不确定性原理的必然：$\Delta x \le a$ 强制 $\Delta p \ge \hbar/(2a)$，故 $E \ge (\Delta p)^2/2m$。
- 基态无节点，第 $n$ 态有 $n-1$ 个节点。

### 2.2 一维谐振子

$$
V(x) = \frac{1}{2}m\omega^2 x^2, \qquad \hat{H} = \frac{\hat{p}^2}{2m} + \frac{1}{2}m\omega^2\hat{x}^2
$$

**代数解法（升、降算符）**：定义 $a = \sqrt{\frac{m\omega}{2\hbar}}(\hat{x} + \frac{i\hat{p}}{m\omega})$，$a^\dagger$ 共轭。$[a, a^\dagger] = 1$。

$$
\hat{H} = \hbar\omega\left(a^\dagger a + \frac{1}{2}\right)
$$

$a^\dagger|n\rangle = \sqrt{n+1}|n+1\rangle$（升），$a|n\rangle = \sqrt{n}|n-1\rangle$（降）。能级：

$$
\boxed{E_n = \hbar\omega\left(n + \frac{1}{2}\right), \qquad n = 0, 1, 2, \dots}
$$

**等间距** $\hbar\omega$——这是振动光谱、声子、量子光学的"模"。

波函数：$\psi_n(x) = \frac{1}{\sqrt{2^n n!}}\left(\frac{m\omega}{\pi\hbar}\right)^{1/4} H_n(\xi)\, e^{-\xi^2/2}$，其中 $\xi = \sqrt{m\omega/\hbar}\, x$，$H_n$ 是 Hermite 多项式。

### 2.3 自由粒子与高斯波包

自由粒子 $V = 0$，平面波解 $\psi \propto e^{ikx}$，能量 $E = \hbar^2 k^2/2m$ 连续。

**波包**（局域化）：高斯初态 $\Psi(x, 0) = (2\pi\sigma^2)^{-1/4} e^{-x^2/(4\sigma^2)}e^{ik_0 x}$ 展开后随时间演化：

$$
\sigma(t) = \sigma\sqrt{1 + \left(\frac{\hbar t}{2m\sigma^2}\right)^2}
$$

波包**扩散**——这是自由粒子波函数不可避免的行为。

---

## 3. 算符与对易

### 3.1 可观测量作为厄米算符

每个物理量 $A$ 对应**厄米算符** $\hat{A}$，满足 $\hat{A}^\dagger = \hat{A}$。本征值实数，本征态正交完备。

测量得到本征值 $a_n$，测后态坍缩到本征态 $\phi_n$。态 $|\psi\rangle = \sum c_n \phi_n$ 测得 $a_n$ 的概率 $|c_n|^2$。

### 3.2 对易子与不确定性关系

**对易子** $[\hat{A}, \hat{B}] = \hat{A}\hat{B} - \hat{B}\hat{A}$。

**Robertson 不确定性关系**：

$$
\boxed{\Delta A\, \Delta B \ge \frac{1}{2}|\langle[\hat{A}, \hat{B}]\rangle|}
$$

其中 $\Delta A = \sqrt{\langle A^2\rangle - \langle A\rangle^2}$。

位置-动量：$[\hat{x}, \hat{p}] = i\hbar$，故 $\Delta x\, \Delta p \ge \hbar/2$。

### 3.3 守恒量与对易

若 $\hat{A}$ 不显含时间且 $[\hat{A}, \hat{H}] = 0$，则 $\frac{d}{dt}\langle A\rangle = 0$——$\hat{A}$ 是守恒量。

- $[\hat{H}, \hat{H}] = 0$ → 能量守恒。
- 中心场 $[\hat{H}, \hat{L}^2] = [\hat{H}, \hat{L}_z] = 0$ → 角动量守恒。
- 平移对称 $[\hat{H}, \hat{p}] = 0$ → 动量守恒。

### 3.4 同时对易与完全简并

若 $[\hat{A}, \hat{B}] = 0$，存在共同本征态完备集——可同时精确测量。

**完全对易集（CSCO）**：一组互相 commute 且本征值完全标定态的算符集合。如氢原子 $(\hat{H}, \hat{L}^2, \hat{L}_z)$。

---

## 4. 角动量与自旋

### 4.1 轨道角动量

$$
\hat{\mathbf{L}} = \hat{\mathbf{r}}\times\hat{\mathbf{p}}, \qquad [\hat{L}_i, \hat{L}_j] = i\hbar\epsilon_{ijk}\hat{L}_k
$$

球坐标下 $\hat{L}^2$ 与 $\hat{L}_z$ 的本征函数是**球谐函数** $Y_l^m(\theta, \phi)$：

$$
\hat{L}^2 Y_l^m = \hbar^2 l(l+1) Y_l^m, \qquad \hat{L}_z Y_l^m = \hbar m\, Y_l^m
$$

$l = 0, 1, 2, \dots$，$m = -l, \dots, l$。

### 4.2 一般角动量代数

仅用对易关系 $[\hat{J}_i, \hat{J}_j] = i\hbar\epsilon_{ijk}\hat{J}_k$ 和 $\hat{J}^2, \hat{J}_z$，Sakurai 通用代数给出：

$$
\hat{J}^2 |j, m\rangle = \hbar^2 j(j+1)|j,m\rangle, \qquad j = 0, \frac{1}{2}, 1, \frac{3}{2}, \dots
$$

$j$ 可取**半整数**——这就是**自旋**的来源（轨道角动量只有整数 $l$）。

升降算符 $\hat{J}_\pm |j,m\rangle = \hbar\sqrt{j(j+1) - m(m\pm 1)}\, |j, m\pm 1\rangle$。

### 4.3 自旋 1/2

$$
\hat{\mathbf{S}} = \frac{\hbar}{2}\boldsymbol{\sigma}, \qquad \sigma_x = \begin{pmatrix}0&1\\1&0\end{pmatrix}, \sigma_y = \begin{pmatrix}0&-i\\i&0\end{pmatrix}, \sigma_z = \begin{pmatrix}1&0\\0&-1\end{pmatrix}
$$

Pauli 矩阵满足 $[\sigma_i, \sigma_j] = 2i\epsilon_{ijk}\sigma_k$，$\{\sigma_i, \sigma_j\} = 2\delta_{ij}$。

$|\uparrow\rangle = (1,0)^T$，$|\downarrow\rangle = (0,1)^T$ 是 $\hat{S}_z$ 本征态。

### 4.4 角动量合成（Clebsch-Gordan）

两个角动量 $\hat{J} = \hat{J}_1 + \hat{J}_2$，$j$ 取值 $|j_1 - j_2|, |j_1-j_2|+1, \dots, j_1+j_2$。例如两个自旋 1/2 合成 $j=1$（三重态）和 $j=0$（单态）。

---

## 5. 氢原子

### 5.1 库仑势的薛定谔方程

$$
\hat{H} = -\frac{\hbar^2}{2\mu}\nabla^2 - \frac{e^2}{4\pi\epsilon_0 r}
$$

分离变量 $\psi(r,\theta,\phi) = R_{nl}(r)Y_l^m(\theta,\phi)$。径向方程解出：

$$
E_n = -\frac{\mu e^4}{2(4\pi\epsilon_0)^2\hbar^2}\cdot\frac{1}{n^2} = -\frac{13.6\text{ eV}}{n^2}, \qquad n = 1, 2, 3, \dots
$$

**只依赖主量子数 $n$**——这是库仑势的"偶然简并"（Runge-Lenz 矢量守恒）。一般中心势 $E$ 依赖 $n, l$。

### 5.2 量子数

- $n = 1, 2, \dots$（主量子数，能量）
- $l = 0, 1, \dots, n-1$（轨道角动量）
- $m = -l, \dots, l$（磁量子数）
- $m_s = \pm 1/2$（自旋）

总简并度（不计自旋）$\sum_{l=0}^{n-1}(2l+1) = n^2$，加自旋 $2n^2$——这就是元素周期表的来源。

### 5.3 玻尔半径与精细结构

玻尔半径 $a_0 = 4\pi\epsilon_0\hbar^2/(\mu e^2) \approx 0.529$ Å。

精细结构（相对论修正 + 自旋-轨道耦合）：

$$
E_{n,j} = E_n\left[1 + \frac{\alpha^2}{n}\left(\frac{1}{j+1/2} - \frac{3}{4n}\right)\right]
$$

简并部分解除，依赖 $j = l \pm 1/2$。$\alpha \approx 1/137$。

---

## 6. 微扰理论

### 6.1 非简并微扰

哈密顿 $\hat{H} = \hat{H}_0 + \lambda\hat{H}'$，已知 $\hat{H}_0|n^{(0)}\rangle = E_n^{(0)}|n^{(0)}\rangle$。

**一级能量修正**：

$$
E_n^{(1)} = \langle n^{(0)}|\hat{H}'|n^{(0)}\rangle
$$

**一级波函数修正**：

$$
|n^{(1)}\rangle = \sum_{m\neq n}\frac{\langle m^{(0)}|\hat{H}'|n^{(0)}\rangle}{E_n^{(0)} - E_m^{(0)}}|m^{(0)}\rangle
$$

**二级能量修正**：

$$
E_n^{(2)} = \sum_{m\neq n}\frac{|\langle m^{(0)}|\hat{H}'|n^{(0)}\rangle|^2}{E_n^{(0)} - E_m^{(0)}}
$$

### 6.2 Stark 效应（例）

均匀外电场 $\mathcal{E}$ 下氢原子 $n=2$ 能级（4 重简并：$l=0,m=0$；$l=1,m=-1,0,1$）。微扰 $\hat{H}' = e\mathcal{E} z$。简并微扰需对角化 $4\times 4$ 矩阵，得到线性 Stark 分裂 $\Delta E = \pm 3ea_0\mathcal{E}$（仅 $l=0$ 与 $l=1,m=0$ 耦合）。

### 6.3 含时微扰与跃迁

含时微扰 $\hat{H}'(t)$ 下，从态 $|i\rangle$ 跃迁到 $|f\rangle$ 的一阶跃迁概率：

$$
P_{i\to f}(t) = \frac{1}{\hbar^2}\left|\int_0^t H'_{fi}(t')e^{i\omega_{fi}t'}dt'\right|^2
$$

正弦微扰 $H'(t) = V\cos\omega t$ 长时间极限给出**费米黄金规则**：

$$
\Gamma_{i\to f} = \frac{2\pi}{\hbar}|V_{fi}|^2 \rho(E_f)
$$

其中 $\rho(E_f)$ 是末态密度。这是激光吸收、放射性衰变、散射的基础公式。

---

## 7. Python 代码演示

### 7.1 一维无限势阱本征态可视化

```python
"""
无限势阱本征态 + 时间演化
零依赖：numpy + matplotlib
"""
import numpy as np
import matplotlib.pyplot as plt

a = 1.0
x = np.linspace(0, a, 500)
n_list = [1, 2, 3, 4]

fig, axes = plt.subplots(2, 2, figsize=(11, 8))
for ax, n in zip(axes.flat, n_list):
    psi = np.sqrt(2/a) * np.sin(n*np.pi*x/a)
    prob = psi**2
    ax.plot(x, psi, 'b-', linewidth=2, label=f'ψ_{n}')
    ax.fill_between(x, prob, alpha=0.2, color='red', label=f'|ψ_{n}|²')
    ax.axhline(0, color='gray', linewidth=0.5)
    ax.set_title(f'n={n}: E_{n} = {n**2}·E₁ (等间距={n**2-(n-1)**2})')
    ax.set_xlabel('x/a'); ax.legend(loc='upper right'); ax.grid(alpha=0.3)
fig.suptitle('无限势阱本征态：节点数 = n−1，概率 |ψ|² 在阱壁为零', fontsize=13)
plt.tight_layout()
plt.savefig('infinite_well.png', dpi=110, bbox_inches='tight')
print("已保存 infinite_well.png")
print(f"零点能比例 E₁:E₂:E₃:E₄ = 1:4:9:16")
```

### 7.2 量子谐振子波函数（数值对角化）

```python
"""
量子谐振子：矩阵对角化求本征态
用有限维 Hilbert 空间表示哈密顿量
"""
import numpy as np
import matplotlib.pyplot as plt

# 用 N 维截断，位置基底离散
N = 200                      # 格点数
L = 10.0                     # 区间 [-L/2, L/2]
dx = L / N
x = np.linspace(-L/2, L/2, N, endpoint=False)

# 自然单位 ℏ = m = ω = 1
m, omega = 1.0, 1.0

# 动能算符 (中心差分)
T = np.zeros((N, N))
np.fill_diagonal(T, 2.0/dx**2)
np.fill_diagonal(T[1:, :-1], -1.0/dx**2)
np.fill_diagonal(T[:-1, 1:], -1.0/dx**2)
T *= 0.5 / m  # ℏ²/(2m) × (−∇²); 该矩阵本身已是 −∇² (正定), ℏ=1

# 势能（对角）
V_diag = 0.5 * m * omega**2 * x**2
V = np.diag(V_diag)

H = T + V
eigenvalues, eigenvectors = np.linalg.eigh(H)

# 归一化
for i in range(N):
    eigenvectors[:, i] /= np.sqrt(np.sum(np.abs(eigenvectors[:, i])**2) * dx)

fig, ax = plt.subplots(figsize=(9, 7))
# 画前 5 个本征态，竖直偏移
for n in range(5):
    psi_n = eigenvectors[:, n]
    E_n = eigenvalues[n]
    ax.plot(x, psi_n + E_n, label=f'n={n}: E={E_n:.3f} (理论 {n+0.5:.1f})')
    ax.axhline(E_n, color='gray', linewidth=0.5, linestyle='--')
ax.plot(x, 0.5*x**2, 'k-', linewidth=1, alpha=0.5, label='V(x)')
ax.set_xlabel('x'); ax.set_ylabel('ψ_n(x) + E_n')
ax.set_title('量子谐振子（数值对角化）: E_n = (n+1/2)ℏω')
ax.set_xlim(-5, 5); ax.set_ylim(-0.5, 5.5)
ax.legend(); ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig('qho.png', dpi=110, bbox_inches='tight')
print("已保存 qho.png")
for n in range(6):
    print(f"  E_{n} 数值 = {eigenvalues[n]:.4f}, 理论 = {n+0.5:.1f}, 误差 = {abs(eigenvalues[n]-(n+0.5))/(n+0.5)*100:.2f}%")
```

### 7.3 高斯波包扩散

```python
"""
自由高斯波包随时间扩散
解析公式 ψ(x,t) = (1+it/τ)^{-1/2} exp(...)
"""
import numpy as np
import matplotlib.pyplot as plt

x = np.linspace(-10, 15, 1000)
sigma0 = 0.5      # 初始宽度
k0 = 5.0          # 初始动量
tau = 2*sigma0**2 # 特征时间 (ℏ/m = 1)
t_list = [0, 0.5, 1.5, 3.0]

fig, ax = plt.subplots(figsize=(10, 6))
for t in t_list:
    sigma_t = sigma0 * np.sqrt(1 + (t/tau)**2)
    psi = (2*np.pi*sigma_t**2)**(-0.25) * np.exp(-(x - k0*t)**2/(2*sigma_t**2))
    ax.plot(x, np.abs(psi)**2, label=f't={t}: σ={sigma_t:.2f}')
ax.set_xlabel('x'); ax.set_ylabel('|ψ|²')
ax.set_title(f'自由高斯波包扩散（σ₀={sigma0}, k₀={k0}, τ=2σ₀²={tau}）')
ax.legend(); ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig('wavepacket.png', dpi=110, bbox_inches='tight')
print("已保存 wavepacket.png")
print(f"t=3 时 σ = {sigma0*np.sqrt(1+(3/tau)**2):.2f}, 是初始 {sigma0*np.sqrt(1+(3/tau)**2)/sigma0:.1f} 倍 — 波包必然扩散")
```

---

## 8. 习题与解答

### 习题 1（无限势阱）— 加了扰动

无限势阱 $[0,a]$ 中，粒子处于基态。突然将阱宽从 $a$ 扩展到 $2a$（势壁 $a$ 处瞬间移到 $2a$）。求粒子留在新基态的概率。

**解**：扩展瞬间波函数不变：$\psi(x, 0^+) = \sqrt{2/a}\sin(\pi x/a)$ for $0 < x < a$，外部为零。

新阱基态 $\phi_1(x) = \sqrt{1/a}\sin(\pi x/(2a))$ for $0 < x < 2a$。

重叠：

$$
c_1 = \int_0^a \sqrt{\frac{1}{a}}\sin\frac{\pi x}{2a}\cdot\sqrt{\frac{2}{a}}\sin\frac{\pi x}{a}\, dx
$$

用积化和差 $\sin A\sin B = \frac{1}{2}[\cos(A-B)-\cos(A+B)]$：

$$
c_1 = \frac{\sqrt{2}}{a}\cdot\frac{1}{2}\int_0^a\left[\cos\frac{\pi x}{2a} - \cos\frac{3\pi x}{2a}\right]dx = \frac{\sqrt{2}}{2a}\cdot\frac{2a}{\pi}\left[\sin\frac{\pi}{2} - \frac{1}{3}\sin\frac{3\pi}{2}\right]
$$

$$
= \frac{\sqrt{2}}{\pi}\left[1 + \frac{1}{3}\right] = \frac{4\sqrt{2}}{3\pi}
$$

$$
P = |c_1|^2 = \frac{32}{9\pi^2} \approx 0.36
$$

### 习题 2（谐振子）— 升降算符

证明谐振子基态 $\psi_0(x) \propto e^{-m\omega x^2/2\hbar}$，并用升降算符求 $\psi_1$。

**解**：基态满足降算符湮灭条件 $a\psi_0 = 0$：

$$
\left(\xi + \frac{d}{d\xi}\right)\psi_0 = 0 \implies \psi_0 = C\, e^{-\xi^2/2}, \quad \xi = \sqrt{m\omega/\hbar}\, x
$$

归一化 $C = (m\omega/\pi\hbar)^{1/4}$。

$\psi_1 = \frac{1}{\sqrt{1}}a^\dagger \psi_0 = \frac{1}{\sqrt{2}}\left(\xi - \frac{d}{d\xi}\right)e^{-\xi^2/2}\cdot (m\omega/\pi\hbar)^{1/4}$

$= \frac{1}{\sqrt{2}}(2\xi)e^{-\xi^2/2}\cdot C = \sqrt{2}\xi e^{-\xi^2/2} C$——正比于 $H_1(\xi) = 2\xi$，与解析公式一致。

### 习题 3（不确定性）— 谐振子基态

证明谐振子基态达到不确定性下界 $\Delta x\, \Delta p = \hbar/2$。

**解**：$\psi_0 \propto e^{-\alpha x^2}$（$\alpha = m\omega/2\hbar$）。

$\langle x\rangle = 0, \langle p\rangle = 0$（奇函数）。

$\langle x^2\rangle = \frac{\hbar}{2m\omega}$（直接积分或用 $E_0 = \frac{1}{2}\hbar\omega = \frac{1}{2}m\omega^2\langle x^2\rangle + \frac{\langle p^2\rangle}{2m}$ + 对称性）。

$\langle p^2\rangle = \frac{m\hbar\omega}{2}$。

$\Delta x\, \Delta p = \sqrt{\frac{\hbar}{2m\omega}}\sqrt{\frac{m\hbar\omega}{2}} = \frac{\hbar}{2}$ ✓。

——**高斯波包是最小不确定性态**。

### 习题 4（自旋 1/2）— 磁场中的进动

自旋 1/2 在均匀磁场 $\mathbf{B} = B_0\hat{z}$ 中，$\hat{H} = -\gamma \hat{\mathbf{S}}\cdot\mathbf{B} = -\gamma B_0 \hat{S}_z = -\omega_0 \hat{S}_z$，$\omega_0 = \gamma B_0$。初态 $|\psi(0)\rangle = |\uparrow_x\rangle = \frac{1}{\sqrt{2}}(|\uparrow\rangle + |\downarrow\rangle)$。求 $\langle S_x\rangle(t)$。

**解**：时间演化 $|\psi(t)\rangle = \frac{1}{\sqrt{2}}(e^{i\omega_0 t/2}|\uparrow\rangle + e^{-i\omega_0 t/2}|\downarrow\rangle)$。

$\hat{S}_x = \frac{\hbar}{2}\sigma_x$，$\langle\psi|\hat{S}_x|\psi\rangle = \frac{\hbar}{2}\cdot\frac{1}{2}\cdot 2\cos\omega_0 t = \frac{\hbar}{2}\cos\omega_0 t$。

**拉莫尔进动**——自旋以频率 $\omega_0 = \gamma B_0$ 绕磁场进动。这是 NMR / MRI 的物理基础。

### 习题 5（角动量）— 对易关系

证明 $[\hat{L}^2, \hat{L}_z] = 0$，并解释其物理意义。

**解**：用 $[\hat{L}^2, \hat{L}_i] = \sum_j[\hat{L}_j^2, \hat{L}_i] = \sum_j \hat{L}_j[\hat{L}_j,\hat{L}_i] + [\hat{L}_j,\hat{L}_i]\hat{L}_j$。

用 $[\hat{L}_i, \hat{L}_j] = i\hbar\epsilon_{ijk}\hat{L}_k$，$[\hat{L}_j^2, \hat{L}_i] = 2i\hbar\epsilon_{jik}\hat{L}_j\hat{L}_k = -2i\hbar\epsilon_{ijk}\hat{L}_j\hat{L}_k$。

求和 $\sum_{jk}\epsilon_{ijk}\hat{L}_j\hat{L}_k$ 中 $(j,k)$ 反对称、$\hat{L}_j\hat{L}_k$ 求和对称部分相消，结果为零。故 $[\hat{L}^2, \hat{L}_z] = 0$。

**物理**：$\hat{L}^2$ 与 $\hat{L}_z$ 可同时精确测量，可构成 CSCO 的一部分——这就是为什么球谐函数 $Y_l^m$ 是它们的共同本征函数。

### 习题 6（氢原子）— 期望值

氢原子基态 $\psi_{100} = \frac{1}{\sqrt{\pi a_0^3}}e^{-r/a_0}$，求 $\langle r\rangle, \langle r^2\rangle$。

**解**：$\langle r^k\rangle = \int_0^\infty r^k |\psi|^2 4\pi r^2 dr = \frac{4}{a_0^3}\int_0^\infty r^{k+2}e^{-2r/a_0}dr$。

用 $\int_0^\infty r^n e^{-\alpha r}dr = n!/\alpha^{n+1}$：

$$
\langle r\rangle = \frac{4}{a_0^3}\cdot\frac{3!}{(2/a_0)^4} = \frac{3a_0}{2}
$$

$$
\langle r^2\rangle = \frac{4}{a_0^3}\cdot\frac{4!}{(2/a_0)^5} = 3a_0^2
$$

注意 $\langle r\rangle \neq \sqrt{\langle r^2\rangle}$——量子涨落。

### 习题 7（微扰）— 谐振子加二次微扰

谐振子加 $\hat{H}' = \frac{1}{2}\alpha x^2$，求基态能量修正到二级。

**解**：注意 $\hat{H}'$ 也是谐振子形式。新哈密顿 $\hat{H} = \frac{p^2}{2m} + \frac{1}{2}(m\omega^2 + \alpha)x^2$，新频率 $\omega' = \sqrt{\omega^2 + \alpha/m}$。

精确：$E_0 = \frac{1}{2}\hbar\omega'$。

展开 $\omega' = \omega\sqrt{1 + \alpha/(m\omega^2)} \approx \omega(1 + \frac{\alpha}{2m\omega^2} - \frac{\alpha^2}{8m^2\omega^4})$。

$E_0 \approx \frac{\hbar\omega}{2} + \frac{\hbar\alpha}{4m\omega} - \frac{\hbar\alpha^2}{16m^2\omega^3}$。

对比微扰论：
- 一级：$E_0^{(1)} = \langle 0|\frac{1}{2}\alpha x^2|0\rangle = \frac{\alpha}{2}\cdot\frac{\hbar}{2m\omega} = \frac{\hbar\alpha}{4m\omega}$ ✓
- 二级：求和 $\sum_{n\neq 0}\frac{|\langle n|\frac{1}{2}\alpha x^2|0\rangle|^2}{E_0 - E_n}$。$\langle n|x^2|0\rangle \neq 0$ 仅 $n=2$：$x^2|0\rangle$ 含 $|2\rangle$ 分量 $\frac{\hbar}{2m\omega}\sqrt{2}$。结果 $-\frac{\hbar\alpha^2}{16m^2\omega^3}$ ✓。

### 习题 8（费米黄金规则）— 周期微扰

二能级系统 $\hat{H}_0 = E_1|1\rangle\langle 1| + E_2|2\rangle\langle 2|$，微扰 $\hat{H}'(t) = V(e^{i\omega t} + e^{-i\omega t})$，$V = V_0|1\rangle\langle 2| + \text{h.c.}$。求 $1\to 2$ 跃迁速率。

**解**：$\omega_{21} = (E_2 - E_1)/\hbar$。共振时 $\omega \approx \omega_{21}$：

$|c_2(t)|^2 = \frac{|V_0|^2}{\hbar^2}\left[\frac{\sin((\omega-\omega_{21})t/2)}{(\omega-\omega_{21})/2}\right]^2 \approx \frac{2\pi}{\hbar}|V_0|^2\delta(E_2 - E_1 - \hbar\omega)\cdot t$

速率 $\Gamma = \frac{2\pi}{\hbar}|V_0|^2\delta(E_2-E_1-\hbar\omega)$——费米黄金规则的简单版本。

---

## 9. 反直觉发现

### 9.1 隧穿效应：经典禁区可穿越

粒子能量 $E < V_0$ 的势垒，经典绝对无法穿过。但薛定谔方程给出指数衰减解 $\psi \propto e^{-\kappa x}$（$\kappa = \sqrt{2m(V_0-E)}/\hbar$），势垒另一侧有非零概率流——**粒子穿过"不可能穿过"的壁垒**。

这是扫描隧道显微镜、$\alpha$ 衰变、核聚变的物理。隧穿概率随势垒宽度指数敏感：STM 用 1 Å 探针-样品距离差产生 10 倍电流变化，是原子分辨的来源。

### 9.2 零点能：粒子永远不静止

谐振子最低能态 $E_0 = \hbar\omega/2 > 0$，没有"静止在阱底"的状态。这违反经典直觉"绝对零度下分子停止振动"。真实氦在 0 K 仍是液体（零点振动太大，无法凝固）——液氦超流性的根源。

### 9.3 测量改变系统

测量位置把波函数坍缩为 $\delta$ 函数——动量变得完全不确定。**测量不是"看一眼"而是"暴力干预"**。这是与经典力学最大的认识断裂：在经典力学中，"观测"对系统的影响可任意小；量子中不可能。

### 9.4 自旋没有经典对应

角动量量子化 $L_z = m\hbar$ 是经典波在球面上的边界条件。但**自旋 1/2 没有任何经典图像**：电子转两圈才回到原状（旋量表示），这是 SO(3) 群到 SU(2) 双覆盖的体现。Sakurai 的"扳手旋 720° 回到原状"演示是直观化手段，但本质上自旋是相对论量子力学（Dirac 方程）的必然。

### 9.5 薛定谔方程线性 → 叠加原理

$\Psi = c_1\psi_1 + c_2\psi_2$ 也是合法态。这就是量子计算的"量子比特"——同一时刻既是 0 又是 1。但测量后塌缩——叠加态的"实在性"是贝尔不等式实验争辩的核心（已证伪定域隐变量）。

---

## 10. 不足与延伸

| 本主题局限 | 延伸方向 | 课程 |
|-----------|---------|------|
| 非相对论 | 相对论量子力学 → Dirac 方程、自旋自然出现 | 8.06 / 8.323 |
| 单粒子 | 多粒子 → 全同粒子、二次量子化、泡利原理 | 8.06 |
| 微扰论弱耦合 | 强耦合 → 变分法、变分 Monte Carlo | 8.06 |
| 无场量子化 | 经典电磁场 → 光子（QED） | 8.323 |
| 不含纠缠信息论 | 纠缠、贝尔不等式、量子信息 | 6.443 JQC |
| 无多体 | 多体物理（凝聚态） → Hartree-Fock、Green 函数 | 8.511 |

**学习路径**：8.04（Griffiths 1-4 章）→ 8.05（Griffiths 后半 + Sakurai 角动量/微扰）→ 8.06（Sakurai 高级）→ 8.323（Peskin QFT）。

---

**参考**：
- Griffiths《Introduction to Quantum Mechanics》3ed, Ch 1-2 (薛定谔), Ch 3 (形式理论), Ch 4 (3D/氢原子), Ch 6 (对称), Ch 7-8 (微扰), Ch 9-10 (散射/全同)
- Sakurai & Napolitano《Modern Quantum Mechanics》3ed, Ch 1 (Dirac 形式), Ch 3 (角动量/自旋), Ch 5 (微扰)
- Feynman Lectures Vol 3 — 直觉化量子
- MIT OCW 8.04 (Zwiebach) / 8.05 (Zwiebach) / 8.06 (Adams)

---

## 🎯 费曼式入口（白话版）

> **一句话解释**：量子力学告诉你微观世界（原子、电子）的运行规则——和我们日常世界完全不同。在日常生活中，一个球可以同时在左边或右边，但在量子世界，一个电子可以**同时**在左边和右边（叠加态），直到你"看"它（测量）的瞬间，它才"选择"一个位置。
>
> **生活类比**：
> - 波函数 ≈ 天气预报的概率分布——它不是实体，而是告诉你"在各个位置找到电子的概率"
> - 叠加态 ≈ 一枚旋转中的硬币——在落下前，它既不是正面也不是反面，而是两者的叠加
> - 测量坍缩 ≈ 硬币落桌那一刻——瞬间从"叠加"变成"确定"
> - 不确定性原理 ≈ 你不可能同时知道一个人的精确位置和精确速度——这不是仪器不够好，是宇宙的规则
> - 量子隧穿 ≈ 穿墙术——小球撞墙有概率直接"穿过去"（概率随墙厚指数衰减）
> - 纠缠 ≈ 两个神奇的骰子，无论隔多远，一个显示 6 另一个也显示 6——但事先不知道哪个面朝上
>
> **反直觉发现**：你以为是"我们测量不够精确才不能同时确定位置和动量"？不！海森堡不确定性原理 $\Delta x \cdot \Delta p \ge \hbar/2$ 是宇宙的**根本法则**——粒子在被测量之前，根本没有确定的位置！更疯狂的是：双缝实验中，粒子"知道"两条缝是否都开着——即使是**单个**电子，它似乎同时穿过两条缝并与自己干涉。费曼说："双缝实验包含了量子力学唯一的秘密。"

---

## 🔗 衔接：这个主题从哪来，到哪去

### 前置知识
- **Topic 01 经典力学**：哈密顿量 $H = T + V$（量子力学的 $\hat{H}$ 直接来自经典哈密顿量）、泊松括号 → 对易子
- **Topic 02 电磁学**：电磁波的能量量子化 $E = h\nu$（光电效应的起点）、电子在原子中的轨道辐射问题
- **线性代数**：本征值/本征向量（量子态 = 向量、可观测量 = 矩阵、测量 = 求本征值）、希尔伯特空间
- **概率论**：波函数的统计诠释 $|\Psi|^2$ = 概率密度

### 本主题解决了什么危机
- **原子稳定性危机（1900-1925）**：经典电磁学预言——电子绕原子核旋转会辐射电磁波、损失能量、在 $10^{-11}$ 秒内坠入原子核。但现实中的原子是稳定的！玻尔（1913）强行假设"轨道量子化"，但说不清为什么。
- **黑体辐射与光电效应**：经典物理无法解释黑体辐射谱（紫外灾难），也无法解释光电效应（为什么低于阈值频率的光再强也打不出电子）。普朗克和爱因斯坦引入"量子" $E = h\nu$ 解决了危机。
- **德布罗意的洞见（1924）**：如果光波有粒子性（光子），那粒子（电子）也应该有波动性 $\lambda = h/p$！这被戴维森-革末实验（1927）证实。
- **薛定谔方程（1926）**：描述波函数如何演化——这是量子力学的"牛顿第二定律"。原子的稳定性自然来自驻波条件：只有特定波长"吻合"的轨道才能存在。

### 本主题留下的新危机
- **测量问题**：波函数是确定性的（薛定谔方程完全确定），但测量结果是随机的。**波函数什么时候坍缩？** 是意识导致的？是仪器导致的？还是根本没坍缩（多世界诠释）？至今没有共识。
- **非相对论限制**：薛定谔方程不满足洛伦兹不变性 → 狄拉克方程（1928）→ 反物质（正电子）→ **量子场论**。
- **引力与量子不兼容**：量子力学框架无法容纳引力。黑洞信息悖论（霍金辐射摧毁信息？）→ **量子引力**（弦论/圈量子引力）至今未解决。
- **量子-经典边界**：宏观物体（你、我、猫）为什么不表现量子行为？退相干理论给出了部分答案——环境的干扰使得叠加态极快退相干。

### 后续主题
- **Topic 06 凝聚态物理**：能带论 = 量子力学在固体中的应用。半导体、超导、拓扑绝缘体都是量子效应的宏观表现
- **Topic 07 粒子物理**：标准模型 = 量子力学 + 狭义相对论 → 量子场论（QED/QCD）
- **量子信息与计算**：量子纠缠 → 量子计算、量子通信、量子密码（BB84/QKD）

---

## 🏭 理论联系实际：5 个工业/生活应用

1. **半导体芯片（ transistor / MOSFET）**：你手机和电脑里的几十亿个晶体管，其工作原理是量子力学的能带论 + 隧穿效应。没有量子力学就没有芯片，就没有信息时代。
   - 实例：Apple M3 芯片（3nm 工艺，190 亿个晶体管）；量子隧穿限制了摩尔定律的极限

2. **激光（LASER）**：受激辐射 + 粒子数反转 = 相干光放大。激光器是量子力学最成功的工程应用之一——从光刻机到光纤通信到激光手术刀。
   - 实例：ASML EUV 光刻机（13.5nm 极紫外激光制造 3nm 芯片）

3. **核磁共振成像（MRI）**：质子自旋（量子力学概念）在磁场中分裂成两个能级（塞曼效应），射频脉冲使它们跃迁——弛豫过程中释放的信号被重建为图像。
   - 实例：医院 3T MRI，分辨率可达亚毫米级

4. **量子计算机**：利用叠加和纠缠进行并行计算。谷歌 2019 年实现"量子霸权"（53 qubit 超导量子处理器 Sycamore 用 200 秒完成了超算估计需要 1 万年的任务）。
   - 实例：IBM Condor（1121 qubit 超导量子计算机）；Atom Computing（1180 量子位中性原子量子计算机）

5. **原子钟与 GPS**：铯原子钟精度 $10^{-15}$（3000 万年误差不到 1 秒），利用的是电子在两个超精细能级之间的跃迁频率。GPS 卫星上的原子钟是实现米级定位的基础。
   - 实例：NIST-F2 铯喷泉原子钟；量子钟即将进入 $10^{-18}$ 精度（光晶格钟）

---

## 🔬 最新研究前沿（2024-2026）

> 基于 Nature 系列期刊搜索的真实结果

### 硅基量子处理器——可扩展量子计算的工程突破
- **发现**：两个独立团队展示了硅基量子处理器，直接解决了可扩展量子计算机的核心工程挑战——利用现有半导体工业的成熟制造工艺来构建量子比特。
- **来源**：Ares, N. "How silicon-chip technology is being re-engineered for quantum computing" *Nature* **655**, 1141 (2026)
- **日期**：2026 年 7 月
- **为什么重要**：如果硅自旋量子比特可以大规模集成，量子计算机将复制经典芯片的摩尔定律路线

### 量子计算在 NP 完全问题上的经验标度优势
- **发现**：通过将搜索空间缩减算法与量子求解器集成，在代表性 NP 完全问题上展示了经验标度优势——量子资源增长速度比经典对手更慢。
- **来源**：*Nature Computational Science* (2026)
- **日期**：2026 年 8 月
- **为什么重要**：这是量子计算在优化问题上的实际量子优势的初步证据

### 真空双折射——极端磁场中真空极化光
- **发现**：对磁星（magnetar）1E 1547.0−5408 的偏振测量提供了强有力的证据：真空双折射效应塑造了 X 射线的传播——真空本身（空无一物的空间）在超强磁场中能偏振光！这是量子电动力学（QED）在极端条件下的直接观测验证。
- **来源**：Stewart, R.E. et al. *Nature* (2026)
- **日期**：2026 年 8 月
- **为什么重要**：验证了 QED 预言的真空极化效应——"空"的空间并非真的空

### 3D 局域噪声浅量子电路击败无界扇入经典电路
- **发现**：描述了一个搜索问题，该问题可以被 3D 局部常数深度噪声量子电路高效求解，但常数深度无界扇入经典电路无法高效求解。即使量子电路不完美（NISQ 时代），也能超越经典。
- **来源**：Caha, L. et al. *Nature Communications* **17**, 8174 (2026)
- **日期**：2026 年 8 月
- **为什么重要**：证明了即使没有完全容错，有噪声的量子设备也有超越经典计算的潜力

---

## 🗺️ 学习 Roadmap（MIT 路径）

### 🎓 入门（2-3 周）
- 📖 读：Griffiths《Introduction to Quantum Mechanics》3ed Ch 1-2（波函数 + 薛定谔方程 + 一维势阱）
- 🎥 看：MIT OCW **8.04**（Barton Zwiebach——讲解极其清晰）
  - 重点视频：Lec 1-5（波函数 + 不确定性原理）、Lec 8-12（一维势阱 + 谐振子）
- ✍️ 做：
  - 推导无限深势阱的能级 $E_n = n^2\pi^2\hbar^2/(2ma^2)$
  - 运行 `physics_demos.py` 的 `quantum()` demo 观察波函数概率分布

### 🏗️ 进阶（4-6 周）
- 📖 读：Griffiths Ch 3-4（形式理论 + 3D + 氢原子）、Ch 6-8（对称 + 微扰）
- 💻 做：
  - 用 Python 数值求解薛定谔方程（有限差分法）画任意势阱的波函数
  - 用 `physics_demos.py` 模拟双缝干涉
- 🧪 实验：MIT Junior Lab 8.13/8.14（Frank-Hertz 实验、光电效应、电子衍射）

### 🔬 深造（持续）
- 📄 读：
  - Sakurai & Napolitano《Modern Quantum Mechanics》3ed——研究生标准教材
  - Feynman Lectures Vol 3——直觉化量子（最好的入门直觉书）
  - Nielsen & Chuang《Quantum Computation and Quantum Information》——量子信息圣经
- 🛠️ 项目：用 Qiskit（IBM 量子云平台）运行真正的贝尔不等式实验

### ✅ 知识检查
- [ ] 能推导海森堡不确定性原理 $\Delta x \cdot \Delta p \ge \hbar/2$
- [ ] 能写出氢原子能级公式 $E_n = -13.6\,\text{eV}/n^2$ 并解释玻尔半径
- [ ] 理解自旋 1/2 粒子需要用 SU(2) 而非 SO(3) 描述（转两圈才回到原样）
- [ ] 能解释 EPR 佯谬和贝尔不等式为什么排除了"局域隐变量"
- [ ] 理解为什么正则量子化 $\{q,p\} \to [\hat{q},\hat{p}]/i\hbar$ 把经典力学变成量子力学
