# Topic 06 · 凝聚态物理（MIT 8.231 / 8.332 / 8.511）

> **教材**：Charles Kittel《Introduction to Solid State Physics》9ed → Ashcroft & Mermin《Solid State Physics》→ John Marder《Condensed Matter Physics》
>
> **覆盖课程**：
> - **8.231** Physics of Solids I（Kittel 本科导论：晶体结构 / 声子 / 自由电子 / 能带入门）
> - **8.332** Quantum Theory of Solids（Ashcroft & Mermin 研究生能带 / 费米面 / 输运）
> - **8.511** Statistical Mechanics（Marder 多体 / 相变 / 超导导引）
>
> **宪法**：直觉 → 公式 → 代码(bash 跑通) → 不足 → 应用

---

## 目录

1. [晶体结构](#1-晶体结构)
2. [倒格子与衍射](#2-倒格子与衍射)
3. [声子：晶格振动](#3-声子晶格振动)
4. [自由电子模型](#4-自由电子模型)
5. [能带论](#5-能带论)
6. [费米面与输运](#6-费米面与输运)
7. [超导电性](#7-超导电性)
8. [Python 代码演示](#8-python-代码演示)
9. [习题与解答](#9-习题与解答)
10. [反直觉发现](#10-反直觉发现)
11. [不足与延伸](#11-不足与延伸)

---

## 1. 晶体结构

### 1.1 布拉伐格子

晶体中原子的平衡位置具有**平移对称性**：存在基矢 $\mathbf{a}_1, \mathbf{a}_2, \mathbf{a}_3$，使得格点集合

$$
\mathbf{R} = n_1\mathbf{a}_1 + n_2\mathbf{a}_2 + n_3\mathbf{a}_3, \qquad n_i \in \mathbb{Z}
$$

遍历所有等效位置。满足此条件的格子称为**布拉伐格子（Bravais lattice）**。

三维共有 **14 种布拉伐格子**（7 大晶系），从简单三斜到面心立方（FCC）。

| 结构 | 每原胞格点数 | 致密度 | 典型材料 |
|------|------------|--------|---------|
| 简单立方 (SC) | 1 | 52% | $\alpha$-Po（罕见） |
| 体心立方 (BCC) | 2 | 68% | Fe, Cr, Na, W |
| 面心立方 (FCC) | 4 | 74% | Cu, Al, Au, Ni |
| 六方密排 (HCP) | 2 | 74% | Mg, Zn, Ti |

### 1.2 基元与结构

实际晶体 = 布拉伐格子 + **基元**（每个格点上放什么原子）。

金刚石结构（Si, Ge）= FCC 格子 + 2 原子基元（两原子在 $(0,0,0)$ 和 $(a/4, a/4, a/4)$，均为同种元素）。

NaCl 结构 = FCC 格子 + 2 原子基元（Na 在 $(0,0,0)$，Cl 在 $(a/2,0,0)$）。

### 1.3 密勒指数

晶面用**密勒指数** $(hkl)$ 标记：截距 $\frac{a_1}{h}, \frac{a_2}{k}, \frac{a_3}{l}$ 决定一簇平行等距平面。

FCC 的密排面是 $(111)$，解理面常是 $(100)$ 或 $(111)$——这些指数决定衍射峰、滑移系、表面能。

---

## 2. 倒格子与衍射

### 2.1 倒格子

对正格子基矢 $\mathbf{a}_i$，定义倒格子基矢：

$$
\mathbf{b}_1 = 2\pi\frac{\mathbf{a}_2\times\mathbf{a}_3}{\mathbf{a}_1\cdot(\mathbf{a}_2\times\mathbf{a}_3)}, \quad \mathbf{b}_2 = 2\pi\frac{\mathbf{a}_3\times\mathbf{a}_1}{V_c}, \quad \mathbf{b}_3 = 2\pi\frac{\mathbf{a}_1\times\mathbf{a}_2}{V_c}
$$

满足 $\mathbf{a}_i\cdot\mathbf{b}_j = 2\pi\delta_{ij}$。

倒格矢 $\mathbf{G} = h\mathbf{b}_1 + k\mathbf{b}_2 + l\mathbf{b}_3$——**密勒指数 $(hkl)$ 自动成为倒格子坐标**。

### 2.2 布里渊区

倒格子中的**Wigner-Seitz 原胞**就是**第一布里渊区**（BZ）——所有动量态的"基本域"。

- SC 正格子 → SC 倒格子
- BCC 正格子 → FCC 倒格子（互易关系！）
- FCC 正格子 → BCC 倒格子

布里渊区的高对称点：$\Gamma$（中心）、$X$（面心）、$L$（六角面心）、$K$（边中点）——能带图都在这些方向上画。

### 2.3 X 射线衍射：Bragg 定律

$$
2d\sin\theta = n\lambda
$$

$d$ 是晶面间距，$\theta$ 是掠射角，$\lambda$ 是 X 射线波长。满足此条件时各层反射相长干涉——**实验确定晶体结构的核心方法**。

更一般地，**Laue 条件**：$\mathbf{k}' - \mathbf{k} = \mathbf{G}$（散射波矢差 = 倒格矢）。Bragg 定律是 Laue 条件的实空间表述。

---

## 3. 声子：晶格振动

### 3.1 一维原子链

最简模型：$N$ 个质量 $M$ 的原子，弹簧常数 $K$，间距 $a$。位移 $u_n$ 的运动方程：

$$
M\ddot{u}_n = K(u_{n+1} - 2u_n + u_{n-1})
$$

代入行波解 $u_n = Ae^{i(kna - \omega t)}$，得**色散关系**：

$$
\boxed{\omega(k) = 2\sqrt{\frac{K}{M}}\left|\sin\frac{ka}{2}\right|}
$$

**物理**：
- $k\to 0$（长波）：$\omega \approx c|k|$，线性色散，声速 $c = a\sqrt{K/M}$——**声学声子**。
- $k = \pi/a$（布里渊区边界）：$\omega = 2\sqrt{K/M}$，群速 $d\omega/dk = 0$——驻波。

### 3.2 双原子链：光学声子

两种原子 $M_1, M_2$ 交替排列。色散关系分裂成两条支：

$$
\omega_\pm^2 = K\left(\frac{1}{M_1}+\frac{1}{M_2}\right) \pm K\sqrt{\left(\frac{1}{M_1}+\frac{1}{M_2}\right)^2 - \frac{4\sin^2(ka/2)}{M_1 M_2}}
$$

- **声学支** $\omega_-$：$k\to 0$ 时 $\omega\to 0$，相邻原子同向运动。
- **光学支** $\omega_+$：$k\to 0$ 时 $\omega\to\sqrt{2K(1/M_1+1/M_2)} \neq 0$，相邻原子反向运动。

红外光可以直接激发光学声子（离子晶体）——因此叫"光学"。

### 3.3 德拜模型

将三维声子近似为各向同性线性色散 $\omega = c_sk$，截止于德拜频率 $\omega_D$（由总模式数 $3N$ 确定）。

低温比热：

$$
C_V = \frac{12\pi^4}{5}Nk_B\left(\frac{T}{\Theta_D}\right)^3 \propto T^3 \qquad (T\ll\Theta_D)
$$

高温 $C_V\to 3Nk_B$（Dulong-Petit 经典极限）。

---

## 4. 自由电子模型

### 4.1 Drude 模型（经典）

电子是经典粒子，在碰撞间自由飞行，碰撞频率 $\tau^{-1}$。Drude 推导出电导率：

$$
\sigma = \frac{ne^2\tau}{m}
$$

成功解释了 Ohm 定律，但无法解释电子比热远小于 $3k_B/2$ 的实验事实。

### 4.2 Sommerfeld 模型（量子自由电子）

电子填满费米海。基态下所有 $|\mathbf{k}| < k_F$ 的态被占据：

$$
k_F = (3\pi^2 n)^{1/3}
$$

费米能 $E_F = \hbar^2k_F^2/(2m)$。铜中 $E_F \approx 7$ eV，对应费米温度 $T_F \approx 80{,}000$ K。

**关键修正**：只有费米面附近 $\sim k_BT$ 窄带内的电子可以参与热激发，所以电子比热：

$$
C_e = \gamma T, \qquad \gamma = \frac{\pi^2}{2}\frac{nk_B^2}{E_F} = \frac{\pi^2}{3}k_B^2 g(E_F)
$$

→ **$T$ 线性**（不同于声子的 $T^3$），且系数由费米面态密度 $g(E_F)$ 决定。

### 4.3 金属总比热

$$
C_V = \underbrace{\gamma T}_{\text{电子}} + \underbrace{AT^3}_{\text{声子}}
$$

低温 $\gamma T$ 主导，高温 $AT^3$ 主导。$C_V/T$ vs $T^2$ 是一条直线——实验验证电子+声子两通道贡献。

---

## 5. 能带论

### 5.1 Bloch 定理

周期势 $V(\mathbf{r}+\mathbf{R}) = V(\mathbf{r})$ 中的电子波函数：

$$
\psi_{\mathbf{k}}(\mathbf{r}) = e^{i\mathbf{k}\cdot\mathbf{r}}\,u_{\mathbf{k}}(\mathbf{r})
$$

其中 $u_{\mathbf{k}}(\mathbf{r}+\mathbf{R}) = u_{\mathbf{k}}(\mathbf{r})$。这就是 **Bloch 定理**——周期势中的电子是"被周期函数调制的平面波"。

### 5.2 近自由电子：能隙的起源

微弱周期势 $V_\mathbf{G}e^{i\mathbf{G}\cdot\mathbf{r}}$ 对自由电子的微扰。当 $\mathbf{k}$ 满足 **Bragg 条件** $2\mathbf{k}\cdot\mathbf{G} = G^2$ 时，发生简并微扰分裂：

$$
E_\pm = \frac{\hbar^2}{2m}\left|\mathbf{k}\right|^2 \pm |V_\mathbf{G}|
$$

→ **能隙** $E_g = 2|V_\mathbf{G}|$ 出现在布里渊区边界。

**直觉**：Bragg 反射使电子无法传播——能量被"禁"在能隙中。整个固体物理的核心：**周期势 + 量子力学 = 能带**。

### 5.3 紧束缚模型

从原子轨道出发，电子在近邻原子间跳跃（hopping $t$）。一维链：

$$
E(k) = \epsilon_0 - 2t\cos(ka)
$$

这是最简单的能带——带宽 $4t$。$t$ 越大（轨道重叠越强），带越宽。

### 5.4 导体、绝缘体、半导体

| 类型 | 能带填充 | $T=0$ 行为 |
|------|---------|-----------|
| 金属 | 最高带半满 | 导电 |
| 绝缘体 | 最高带满，能隙 $E_g \gg k_BT$ | 不导电 |
| 半导体 | $E_g \sim 1$ eV，少量热激发 | 弱导电，温度依赖 |

Si 的 $E_g = 1.12$ eV，Ge 的 $E_g = 0.67$ eV，金刚石的 $E_g = 5.5$ eV——同是 IV 族，能隙差异造就了截然不同的材料性质。

---

## 6. 费米面与输运

### 6.1 费米面

$T=0$ 时电子在动量空间占据一个区域，其边界是**费米面**。

- 自由电子：费米面是球面，半径 $k_F$。
- 近自由电子：费米面接近球面，但在布里渊区边界附近畸变（被能隙"压扁"）。

费米面的形状决定了金属的几乎所有电子性质——电导、热导、磁化率、超导配对。

### 6.2 有效质量

在能带底 $k_0$ 附近展开：

$$
E(k) \approx E(k_0) + \frac{1}{2}\frac{d^2E}{dk^2}\bigg|_{k_0}(k-k_0)^2
$$

类比自由电子 $E = \hbar^2k^2/(2m)$，定义**有效质量**：

$$
m^* = \hbar^2\left(\frac{d^2E}{dk^2}\right)^{-1}
$$

→ 能带越窄（$d^2E/dk^2$ 越小），有效质量越大，电子越"重"。在某些窄带材料中 $m^*/m_e$ 可达 $10^2$—$10^3$。

### 6.3 半经典运动方程

Bloch 电子在外场中的运动：

$$
\hbar\dot{\mathbf{k}} = -e(\mathbf{E} + \mathbf{v}\times\mathbf{B}), \qquad \mathbf{v} = \frac{1}{\hbar}\nabla_k E(\mathbf{k})
$$

形式同牛顿方程，但加速度涉及 $m^*$ 而非 $m_e$。

### 6.4 Hall 效应

磁场中的偏转产生横向电场。Hall 系数：

$$
R_H = \frac{1}{ne} \quad (\text{单载流子})
$$

实验测 $R_H$ 即可得载流子密度 $n$。但在某些材料中 $R_H$ 符号"反常"（正 Hall 系数）——需要**空穴**概念：能带顶附近的空态行为像正电荷。

---

## 7. 超导电性

### 7.1 实验现象

1. **零电阻**（$T < T_c$）：Kammerlingh Onnes 1911 年在汞中发现（$T_c = 4.2$ K）。
2. **Meissner 效应**：完全排斥磁场（$B = 0$），不是理想导体的简单推论——是独立的实验事实。
3. **临界磁场**：$H_c(T) = H_c(0)[1 - (T/T_c)^2]$。

### 7.2 Cooper 对与 BCS 理论

**Cooper 不稳定性**（1956）：费米面附近两个电子通过声子媒介的吸引相互作用，形成束缚态——**Cooper 对**。

Cooper 对是玻色子（自旋 0 或 1），不受泡利原理限制，可以凝聚到同一量子态——这就是超导。

BCS 基态（1957，Bardeen-Cooper-Schrieffer）：

$$
|\Psi_{\text{BCS}}\rangle = \prod_{\mathbf{k}}\left(u_{\mathbf{k}} + v_{\mathbf{k}}\,c^\dagger_{\mathbf{k}\uparrow}c^\dagger_{-\mathbf{k}\downarrow}\right)|0\rangle
$$

能隙方程（自洽）：

$$
\Delta = 2\hbar\omega_D\,e^{-1/(g(E_F)V)} \quad (\text{弱耦合})
$$

→ 超导能隙 $\Delta$ 指数依赖耦合强度 $V$。$T_c \approx 1.14\,\Theta_D\,e^{-1/(g(E_F)V)}$。

### 7.3 BCS 预言与验证

- **能隙**：$2\Delta(0) = 3.52\,k_BT_c$（ universality）——实验精确验证。
- **同位素效应**：$T_c \propto M^{-1/2}$（$\Theta_D \propto M^{-1/2}$）——声子媒介的直接证据。
- **比热跳跃**：$T_c$ 处 $C_e$ 从 $\gamma T$ 跃升，跃变量 $\Delta C/\gamma T_c = 1.43$。

### 7.4 高温超导：铜氧化物

1986 年 Bednorz-Müller 发现铜氧化物 La-Ba-Cu-O 的 $T_c = 30$ K（1987 诺奖）。随后 YBCO ($T_c = 92$ K) 突破液氮温区。

**机制未明**——BCS 的声子配对机制无法解释 $T_c > 100$ K（声子能量太低）。可能是反铁磁涨落配对，但**尚未定论**——凝聚态物理最大的开放问题之一。

---

## 8. Python 代码演示

### 8.1 一维原子链的声子色散

```python
"""
一维单原子链和双原子链的声子色散关系
单原子: ω = 2√(K/M)|sin(ka/2)|
双原子: 声学支 + 光学支
"""
import numpy as np
import matplotlib.pyplot as plt

ka = np.linspace(-np.pi, np.pi, 500)
K, M = 1.0, 1.0

# 单原子链
omega_mono = 2*np.sqrt(K/M)*np.abs(np.sin(ka/2))

# 双原子链 (M1=1, M2=2)
M1, M2 = 1.0, 2.0
C = K*(1/M1 + 1/M2)
D = K*np.sqrt((1/M1 + 1/M2)**2 - 4*np.sin(ka/2)**2/(M1*M2))
omega_acoustic = np.sqrt(np.maximum(C - D, 0))   # 声学支
omega_optical = np.sqrt(C + D)                     # 光学支

fig, axes = plt.subplots(1, 2, figsize=(13, 5))

axes[0].plot(ka/np.pi, omega_mono, 'b-', linewidth=2)
axes[0].set_xlabel('ka/π'); axes[0].set_ylabel('ω / √(K/M)')
axes[0].set_title('单原子链声子色散')
axes[0].axvline(0, color='gray', linewidth=0.5)
axes[0].grid(alpha=0.3)
axes[0].annotate('线性: ω=c|k|', xy=(0.05, 0.3), fontsize=10, color='blue')

axes[1].plot(ka/np.pi, omega_acoustic, 'b-', linewidth=2, label='声学支 (同相)')
axes[1].plot(ka/np.pi, omega_optical, 'r-', linewidth=2, label='光学支 (反相)')
axes[1].fill_between(ka/np.pi, omega_acoustic.max(), omega_optical.min(),
                     alpha=0.1, color='green', label='带隙')
axes[1].set_xlabel('ka/π'); axes[1].set_ylabel('ω / √(K/M₁)')
axes[1].set_title(f'双原子链 (M₁={M1}, M₂={M2}): 声学+光学支')
axes[1].legend(fontsize=9); axes[1].grid(alpha=0.3)

plt.tight_layout()
plt.savefig('phonon_dispersion.png', dpi=110, bbox_inches='tight')
print("已保存 phonon_dispersion.png")
print(f"光学支 k=0 频率: {np.sqrt(2*K*(1/M1+1/M2)):.4f} √(K/M₁)")
print(f"带隙宽度: {omega_optical.min() - omega_acoustic.max():.4f} √(K/M₁)")
```

### 8.2 紧束缚能带与有效质量

```python
"""
紧束缚模型能带: E(k) = ε₀ - 2t cos(ka)
1D, 2D正方格, 2D蜂巢格(石墨烯)
展示有效质量随k的变化
"""
import numpy as np
import matplotlib.pyplot as plt

t = 1.0  # hopping

# 1D 链
kx_1d = np.linspace(-np.pi, np.pi, 500)
E_1d = -2*t*np.cos(kx_1d)

# 2D 正方格子
kx = np.linspace(-np.pi, np.pi, 300)
ky = np.linspace(-np.pi, np.pi, 300)
KX, KY = np.meshgrid(kx, ky)
E_sq = -2*t*(np.cos(KX) + np.cos(KY))

# 有效质量 (1D): m* = ℏ² / (d²E/dk²) = ℏ² / (2t cos(ka))
# 在 k=0 (带底): m* = ℏ²/(2t); 在 k=π (带顶): m* = -ℏ²/(2t)
m_eff = 1.0 / (2*t*np.cos(kx_1d))  # 以 ℏ²=a=1 为单位

fig, axes = plt.subplots(1, 3, figsize=(15, 5))

# 1D 能带
axes[0].plot(kx_1d/np.pi, E_1d, 'b-', linewidth=2)
axes[0].set_xlabel('ka/π'); axes[0].set_ylabel('E/t')
axes[0].set_title('1D 紧束缚能带: E = -2t cos(ka)')
axes[0].axhline(0, color='gray', linewidth=0.5)
axes[0].grid(alpha=0.3)

# 2D 正方格等能面
contour = axes[1].contourf(KX/np.pi, KY/np.pi, E_sq, levels=30, cmap='RdBu_r')
axes[1].set_xlabel('kₓa/π'); axes[1].set_ylabel('k_ya/π')
axes[1].set_title('2D 正方格等能面')
plt.colorbar(contour, ax=axes[1], label='E/t')

# 有效质量
axes[2].plot(kx_1d[:250]/np.pi, m_eff[:250], 'r-', linewidth=2)
axes[2].set_xlabel('ka/π'); axes[2].set_ylabel('m* (ℏ²/a²t 单位)')
axes[2].set_title('有效质量 vs k (带底→带顶)')
axes[2].axhline(0, color='gray', linewidth=0.5)
axes[2].annotate('带底: m* = +1/(2t)\n(电子)', xy=(0.05, 0.5), fontsize=9, color='blue')
axes[2].grid(alpha=0.3)

plt.tight_layout()
plt.savefig('tight_binding_bands.png', dpi=110, bbox_inches='tight')
print("已保存 tight_binding_bands.png")
print("带宽 = 4t =", 4*t, "(1D)")
print("带底有效质量 m* = ℏ²/(2ta²) — 越窄的带 → 越重的电子")
```

### 8.3 自由电子费米面与德拜比热

```python
"""
(a) 2D 自由电子费米圆 (不同填充)
(b) 德拜声子比热 C_V/T vs T (电子γT + 声子 AT³ 拆分)
"""
import numpy as np
import matplotlib.pyplot as plt

fig, axes = plt.subplots(1, 2, figsize=(13, 5))

# (a) 2D 费米圆
k = np.linspace(-1.5, 1.5, 300)
KX, KY = np.meshgrid(k, k)
for n, (kf, label) in enumerate([(0.5, '稀疏电子'), (0.9, '半满'), (1.3, '近满')]):
    color = ['blue', 'green', 'red'][n]
    occupied = KX**2 + KY**2 < kf**2
    axes[0].contourf(KX, KY, occupied.astype(float), levels=[0.5, 1.5],
                     colors=[color], alpha=0.2+0.2*n)
    theta = np.linspace(0, 2*np.pi, 200)
    axes[0].plot(kf*np.cos(theta), kf*np.sin(theta), color=color,
                 linewidth=1.5, label=f'k_F={kf}, n∝k_F²={kf**2:.2f}')
axes[0].set_xlabel('kₓ'); axes[0].set_ylabel('k_y')
axes[0].set_title('2D 自由电子费米面 (T=0)')
axes[0].set_aspect('equal'); axes[0].legend(fontsize=9); axes[0].grid(alpha=0.3)

# (b) 金属低温比热: C/T = γ + AT²
T = np.linspace(0.1, 10, 200)
gamma = 0.7  # mJ/(mol·K²), 电子比热系数 (铜的量级)
Theta_D = 400  # K
A_coeff = 12*np.pi**4/5 * 8.314 / Theta_D**3  # ≈ 234*R/Θ_D³

C_total = gamma*T + A_coeff*T**3
C_elec = gamma*T
C_phonon = A_coeff*T**3

axes[1].plot(T**2, C_total/T, 'k-', linewidth=2, label='C/T 总和')
axes[1].plot(T**2, np.full_like(T, gamma), 'b--', label=f'γ = {gamma} (电子)')
axes[1].plot(T**2, A_coeff*T**2, 'r--', label=f'AT² (声子, Θ_D={Theta_D}K)')
axes[1].set_xlabel('T² (K²)'); axes[1].set_ylabel('C/T (mJ/mol·K²)')
axes[1].set_title('金属比热: C/T vs T² (直线验证 γ+AT²)')
axes[1].legend(fontsize=9); axes[1].grid(alpha=0.3)

plt.tight_layout()
plt.savefig('fermi_specific_heat.png', dpi=110, bbox_inches='tight')
print("已保存 fermi_specific_heat.png")
print(f"电子系数 γ = {gamma} mJ/(mol·K²)")
print(f"德拜温度 Θ_D = {Theta_D} K")
print(f"T=1K: 电子贡献/声子贡献 = {gamma*1/(A_coeff*1**3):.1f} (电子主导)")
print(f"T=5K: 电子贡献/声子贡献 = {gamma*5/(A_coeff*5**3):.1f}")
```

---

## 9. 习题与解答

### 习题 1（晶体密度）— FCC

铜是 FCC，晶格常数 $a = 3.61$ Å，原子量 63.55。求密度。

**解**：FCC 每原胞 4 个原子。体积 $a^3 = (3.61\times 10^{-10})^3 = 4.71\times 10^{-29}$ m³。

$$
\rho = \frac{4 \times 63.55 \times 1.66\times 10^{-27}}{4.71\times 10^{-29}} = 8960\text{ kg/m}^3 = 8.96\text{ g/cm}^3 \quad \checkmark
$$

### 习题 2（Bragg 衍射）

铜靶 X 射线 $K_\alpha$（$\lambda = 1.54$ Å）照射 NaCl（$a = 5.64$ Å），求 $(200)$ 面一级 Bragg 角。

**解**：$d_{200} = a/\sqrt{2^2+0+0} = 5.64/2 = 2.82$ Å。

$$
\sin\theta = \frac{\lambda}{2d} = \frac{1.54}{2\times 2.82} = 0.273, \quad \theta = 15.8°
$$

### 习题 3（声子色散）— 极限

一维单原子链，$K = 10$ N/m，$M = 10^{-25}$ kg，$a = 3$ Å。求声速和截止频率。

**解**：长波声速 $c = a\sqrt{K/M}$：

$$
c = 3\times 10^{-10}\sqrt{10/10^{-25}} = 3\times 10^{-10}\times 10^{13} = 3000\text{ m/s}
$$

截止频率 $\omega_{\max} = 2\sqrt{K/M} = 2\times 10^{13}$ rad/s，$f_{\max}\approx 3.2$ THz。

### 习题 4（费米能）

钾（BCC，$a = 5.23$ Å）的价电子数为 1。求费米能和费米温度。

**解**：BCC 每原胞 2 原子，电子密度 $n = 2/a^3 = 2/(5.23\times 10^{-10})^3 = 1.40\times 10^{28}$ m$^{-3}$。

$$
k_F = (3\pi^2 n)^{1/3} = 7.84\times 10^9\text{ m}^{-1}
$$

$$
E_F = \frac{\hbar^2 k_F^2}{2m_e} = \frac{(1.055\times 10^{-34})^2 \times (7.84\times 10^9)^2}{2\times 9.11\times 10^{-31}} = 3.4\times 10^{-19}\text{ J} = 2.1\text{ eV}
$$

$T_F = E_F/k_B \approx 24{,}000$ K。

### 习题 5（能隙估计）

某绝缘体 $E_g = 5$ eV。室温 ($k_BT \approx 0.026$ eV) 下导带电子浓度的玻尔兹曼因子。

**解**：

$$
e^{-E_g/(2k_BT)} = e^{-5/(2\times 0.026)} = e^{-96} \approx 10^{-42}
$$

→ 绝缘体导电率极低（$10^{-42}$ 量级）。

### 习题 6（Hall 系数）

铜的 Hall 系数实验值 $R_H = -5.5\times 10^{-11}$ m³/C。求载流子密度。

**解**：$n = 1/(e|R_H|) = 1/(1.6\times 10^{-19}\times 5.5\times 10^{-11}) = 1.14\times 10^{29}$ m$^{-3}$。

铜是 FCC，每原胞 4 原子，$a = 3.61$ Å，原子密度 $4/a^3 = 8.5\times 10^{28}$ m$^{-3}$。$n/e \approx 1.3$ → 约 1 个传导电子/原子 ✓。

### 习题 7（BCS 能隙）

铝的 $T_c = 1.19$ K，$\Theta_D = 428$ K。用 BCS 弱耦合公式估算 $E_F$ 附近的耦合参数 $N(0)V$。

**解**：$T_c = 1.14\,\Theta_D\,e^{-1/(N(0)V)}$

$$
\ln\frac{1.14\times 428}{1.19} = \ln 410 = 6.02 = \frac{1}{N(0)V}
$$

$$
N(0)V = 0.166
$$

弱耦合 ✓（BCS 适用条件 $N(0)V \ll 1$）。

### 习题 8（Drude 电导率）

铜的电导率 $\sigma = 5.96\times 10^7$ S/m，$n = 8.5\times 10^{28}$ m$^{-3}$。求弛豫时间。

**解**：$\tau = \sigma m/(ne^2) = 5.96\times 10^7\times 9.11\times 10^{-31}/(8.5\times 10^{28}\times (1.6\times 10^{-19})^2)$

$$
\tau = 2.5\times 10^{-14}\text{ s}
$$

→ 弛豫时间 ~25 fs，自由程 $v_F\tau \approx 1.57\times 10^6\times 2.5\times 10^{-14} \approx 39$ nm。

---

## 10. 反直觉发现

### 10.1 能带：周期势的魔法

自由电子能穿过任何金属——但周期势（晶格）恰好把某些能量区间变成**禁区**（能隙）。一维近自由电子模型中，无限弱周期势 $V_G\to 0$ 的极限下，能隙 $E_g = 2|V_G|\to 0$，但能带结构已经存在——它决定了一个材料是导体还是绝缘体。

两个完全由碳组成的材料——金刚石（绝缘体，$E_g = 5.5$ eV）和石墨（半金属）——差异完全来自晶格结构。

### 10.2 费米温度远高于熔点

铜的费米温度 $T_F \approx 80{,}000$ K，而铜的熔点只有 1358 K。即使把铜加热到汽化，电子气仍然"很冷"——大部分电子仍在费米海深处，只有表面 $\sim T/T_F \sim 1\%$ 被激发。这就是为什么金属的电子比热如此小（$\sim \gamma T$，$\gamma$ 很小）。

### 10.3 空穴：不存在的正电荷

半导体 p 型材料中的"空穴"不是真实的正电荷粒子——它是价带顶缺少一个电子。但它的行为完全像一个质量为 $m_h^* > 0$、电荷为 $+e$ 的粒子：正 Hall 系数、正有效质量、正漂移方向。

把"无"当"有"来处理——这是多体物理的核心思想（准粒子）。

### 10.4 超导态的热力学一致性

Meissner 效应**不是**零电阻的推论。零电阻只意味着磁场不能改变（冻结），而 Meissner 效应是**主动排斥**已有磁场——这是热力学平衡态的性质。

这意味着超导-正常相变是真正的**热力学相变**（有潜热和比热跳跃），可以用磁化率当序参量做 Landau 理论——而不是某种"电阻为零的特殊金属"。

---

## 11. 不足与延伸

| 本主题局限 | 延伸方向 | 课程 |
|-----------|---------|------|
| 独立电子近似 | 电子-电子相互作用、Fermi 液体理论、Hubbard 模型 | 8.511 → 8.512 |
| 简单能带 | 拓扑物态（拓扑绝缘体、Weyl 半金属）、Berry 相位 | 8.513 |
| 常规 BCS 超导 | 高温超导、非常规超导（重费米子、有机超导） | 8.514 |
| 理想晶体 | 无序系统（Anderson 定域化）、准晶、玻璃 | 8.515 |
| 平衡态 | 非平衡输运、量子霍尔效应、石墨烯器件 | 8.514/8.516 |
| 块体 | 低维系统（2D 材料、量子点、纳米线） | 8.231 续 |

**学习路径**：8.231（Kittel）→ 8.332（Ashcroft & Mermin）→ 8.511（统计力学/多体）→ 8.512（相变/输运）。

---

**参考**：
- Kittel《Introduction to Solid State Physics》9ed, Ch 1-5 (结构/衍射/声子), Ch 6-8 (能带/费米面), Ch 10-12 (超导/磁性)
- Ashcroft & Mermin《Solid State Physics》Ch 4-8 (能带/费米面/输运), Ch 33-34 (BCS), Ch 26-27 (声子)
- Marder《Condensed Matter Physics》— 研究生综合教材
- Girvin & Yang《Modern Condensed Matter Physics》— 现代视角（拓扑、量子霍尔）
- MIT OCW 8.231 (Lee) / 8.511 (Senthil)

---

## 🎯 费曼式入口（白话版）

> **一句话解释**：凝聚态物理研究"一大堆原子堆在一起会发生什么"。单个铜原子不导电（它是绝缘的！），但 $10^{23}$ 个铜原子按规则排列就变成了导体——集体行为涌现出了个体完全没有的性质。凝聚态物理就是研究这种"多即是不同"（More is Different，安德森语）的学问。
>
> **生活类比**：
> - 能带 ≈ 公路系统：原子轨道 = 单条小路，合在一起 = 多车道高速。有些能量区间路通了（导带 → 导电），有些区间被堵死（带隙 → 绝缘）
> - 声子 ≈ 体育场人浪：原子不孤立振动，它们互相带动，形成集体振动模式
> - 费米面 ≈ 拥挤电梯：泡利不相容 = 每个人占一个位置，低层先坐满，最后一个人只能站在最高层（费米能级）
> - 超导 ≈ 在没有阻力的冰面上滑行：电子配对（库珀对）后集体凝聚，电阻瞬间降为零
> - 拓扑绝缘体 ≈ 有围墙的高速公路：表面是导体（围墙上可以走），内部是绝缘体（墙内不能走）——拓扑保护让表面态不被杂质破坏
>
> **反直觉发现**：你以为金、银、铜天生就是金属？不！一个孤立的铜原子是绝缘体！金属导电的性质纯粹来自 $10^{23}$ 个原子的集体量子行为。更反直觉的是超导：两个电子（都带负电、互相排斥！）竟然在晶格振动的"牵线搭桥"下配成一对——这就是 BCS 理论的核心。而 2025-2026 年最热门的镍氧化物超导体在 100K（-173°C）就超导——机制可能与铜基超导完全不同，至今争议不断。凝聚态物理是发现全新物态最多产的领域。

---

## 🔗 衔接：这个主题从哪来，到哪去

### 前置知识
- **Topic 03 量子力学**：薛定谔方程、本征值问题（能带本质是周期势中的本征值）、费米子（泡利不相容）
- **Topic 04 统计物理**：费米-狄拉克分布（电子占据能级的方式）、玻色-爱因斯坦分布（声子）、配分函数（比热容）
- **Topic 05 数学方法**：群论（晶体对称性 → 能带结构）、傅里叶分析（倒格子）、特殊函数

### 本主题解决了什么危机
- **经典电子论的失败（1900s）**：德鲁德模型用经典力学+电磁学处理金属电子，预言比热应该很大（每个电子贡献 $3k_B/2$），但实验发现电子比热极小。泡利和索末菲用量子力学+费米-狄拉克统计解决了：只有费米面附近的电子才能参与热激发 → 比热 $\propto T$ 而非常数。
- **能带论的诞生（1928-1931）**：布洛赫证明了——在周期势中运动的电子不会散射（不存在电阻！）！电阻来自杂质和声子散射。这完美解释了为什么纯金属在低温下电阻趋近于零。
- **超导之谜（1911-1957）**：昂尼斯 1911 年发现汞在 4.2K 电阻突然消失，46 年无人能解释。巴丁-库珀-施里弗（BCS，1957）给出了答案：电子通过声子交换形成库珀对，凝聚成宏观量子态。

### 本主题留下的新危机
- **高温超导的机制不明**：铜氧化物在 134K（常压）超导、镍氧化物在 100K 超导——这远超 BCS 理论预言的极限（~40K，McMillan 极限）。是磁涨落配对？还是全新的机制？至今没有共识。
- **关联电子系统**：莫特绝缘体、重费米子、量子自旋液体——这些系统中电子-电子相互作用极强，微扰论和能带论全部失效。需要全新的理论工具。
- **室温超导的追寻**：2023 年 LK-99 闹剧后，理论家和实验家仍在追寻真正的室温超导体。氢化物在超高压（百万大气压）下接近室温超导，但无法实用。

### 后续主题
- **拓扑物态**：量子霍尔效应、拓扑绝缘体、Weyl 半金属——用拓扑不变量（Berry 相位、陈数）分类物态
- **量子材料与器件**：石墨烯、过渡金属硫族化物（TMD）、莫尔超晶格——二维量子材料
- **量子计算硬件**：超导量子比特（约瑟夫森结）、拓扑量子比特（马约拉纳费米子）

---

## 🏭 理论联系实际：5 个工业/生活应用

1. **半导体芯片（MOSFET/FinFET/GAAFET）**：能带论 + pn 结 = transistor。硅的带隙 1.12 eV 恰好适合室温下开关。掺杂（磷给电子 = n 型，硼抢电子 = p 型）控制导电性。
   - 实例：台积电 2nm GAAFET 工艺；每个芯片含数百亿晶体管

2. **LED 照明与太阳能电池**：LED 利用半导体带隙发光（电子从导带跃迁到价带释放光子，颜色由带隙决定）。太阳能电池反向工作——光子激发电子越过带隙产生电流。
   - 实例：蓝光 LED（氮化镓，2014 年诺贝尔物理学奖）；钙钛矿太阳能电池效率突破 26%

3. **超导磁体（MRI/粒子加速器/核聚变）**：超导线圈产生极强磁场且无焦耳热损耗。NbTi/Nb₃Sn 超导线在液氦温度（4K）工作。
   - 实例：ITER 核聚变反应堆（超导磁体产生 13T 磁场约束等离子体）；LHC 超导磁体

4. **硬盘存储与自旋电子学**：硬盘利用铁磁性材料（磁畴方向编码 0/1）。巨磁阻效应（GMR，2007 年诺贝尔奖）使硬盘密度提升 100 倍。自旋阀、MRAM（磁性随机存储器）是自旋电子学的产物。
   - 实例：希捷 20TB 氦气硬盘；三星 MRAM 芯片

5. **石墨烯与二维材料**：单层碳原子（石墨烯）的电子行为如同无质量狄拉克费米子——有效光速 $v_F \approx 10^6$ m/s。石墨烯透明、导电、极强（200 倍钢强度）。
   - 实例：石墨烯电池（华为/三星研究）；可折叠 OLED 屏幕的透明电极

---

## 🔬 最新研究前沿（2024-2026）

> 基于 Nature 系列期刊搜索的真实结果

### 镍氧化物高压超导达到 100K
- **发现**：在 La₃₋ₓNdₓNi₂O₇ 中通过创纪录的稀土 Nd 替代（x=2.4）产生化学压力，射频传输实验在 33 GPa 高压下观测到高达 100.5 K 的超导信号——这是镍基超导体中最高温度的超导迹象。
- **来源**：Qiu, Z. et al. *Nature Communications* (2026)
- **日期**：2026 年 8 月
- **为什么重要**：镍氧化物超导是继铜基超导之后的第三类非常规超导家族，100K 突破液氮温度门槛，机制可能完全不同

### 维格纳晶体极化子在单层半导体中的光谱学观测
- **发现**：在原子级薄层过渡金属硫族化物中观测到了电子维格纳晶体的集体激发（极化子）的光学特征——首次直接探测了维格纳晶体（电子自发排列成晶格）的内部动力学。
- **来源**：Wang, L. et al. *Nature Physics* (2026)
- **日期**：2026 年 8 月
- **为什么重要**：维格纳晶体是强关联电子系统的极端形态——电子之间的库仑排斥超过动能，自组装成晶格

### 超导金属超氢化物的长期稳定性
- **发现**：研究了超导金属超氢化物（如 H₃S、LaH₁₀）的长期稳定性——这些材料在超高压下接近室温超导，但稳定性是实用化的关键瓶颈。
- **来源**：Minkov, V.S. et al. *Nature Communications* **17**, 8171 (2026)
- **日期**：2026 年 8 月
- **为什么重要**：室温超导的实用化取决于材料的稳定性——高压下的发现能否推广到常压？

### 拓扑材料：Mn(Bi,Sb)₂Te₄ 中磁场诱导的拓扑相变
- **发现**：对 Mn(Bi,Sb)₂Te₄ 合金施加磁场可以同时诱导磁性相变和拓扑相变，产生出乎意料的强红外圆二色性。
- **来源**：Akrap, A. & Orlita, M. "Twisting light the Weyl way" *Nature Materials* (2026)
- **日期**：2026 年 8 月
- **为什么重要**：磁性 + 拓扑的耦合打开了轴子绝缘体、拓扑磁电效应等全新物态的大门

### 轨道电子学变得抗无序
- **发现**：揭示了轨道角动量传输对晶体无序的弹性——在多种无序薄膜中都发现了轨道弛豫过程。这意味着"轨道电子学"（用电子的轨道角动量而非电荷/自旋传输信息）可能在工程上可行。
- **来源**：DuttaGupta, S. *Nature Physics* **22**, 1176 (2026)
- **日期**：2026 年 8 月
- **为什么重要**：电荷 → 自旋（自旋电子学）→ 轨道（轨道电子学），每一代都降低功耗并增加信息密度

---

## 🗺️ 学习 Roadmap（MIT 路径）

### 🎓 入门（2-3 周）
- 📖 读：Kittel《Introduction to Solid State Physics》9ed Ch 1-5（晶体结构 + 倒格子 + 声子 + 热容）
- 🎥 看：MIT OCW **8.231**（Physics of Solids I）
  - 重点：布洛赫定理、能带概念、费米面
- ✍️ 做：
  - 画 FCC/BCC/HCP 的维格纳-赛兹原胞
  - 运行 `physics_demos.py` 的 `solid_state()` demo 观察能带和费米面

### 🏗️ 进阶（4-6 周）
- 📖 读：Ashcroft & Mermin Ch 4-8（能带 + 费米面 + 输运）、Ch 33-34（BCS 超导）
- 💻 做：
  - 用紧束缚模型（tight-binding）数值计算石墨烯能带（含 Dirac 锥）
  - 模拟伊辛模型的磁化曲线
- 🧪 实验：MIT Junior Lab（X 射线衍射、霍尔效应、超导转变）

### 🔬 深造（持续）
- 📄 读：
  - Marder《Condensed Matter Physics》——研究生综合教材
  - Girvin & Yang《Modern Condensed Matter Physics》——含拓扑、量子霍尔
  - Coleman《Introduction to Many-Body Physics》——多体理论
  - arXiv: cond-mat 板块每日新作
- 🛠️ 项目：用 DFT（密度泛函理论）软件（如 Quantum ESPRESSO）计算硅的能带结构

### ✅ 知识检查
- [ ] 能解释为什么金属导电而绝缘体不导电（用能带 + 带隙）
- [ ] 能写出布洛赫定理 $\psi_k(r) = e^{ik\cdot r}u_k(r)$ 并解释物理含义
- [ ] 理解 BCS 理论：库珀对如何形成、为什么超导能隙 $\Delta \propto e^{-1/N(0)V}$
- [ ] 能解释拓扑绝缘体与普通绝缘体的区别（Z₂ 拓扑不变量）
- [ ] 能画石墨烯的能带结构并标出狄拉克点
