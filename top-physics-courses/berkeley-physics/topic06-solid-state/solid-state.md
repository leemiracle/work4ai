# Topic 06: 固体物理 — 从晶体结构到超导

> **UC Berkeley 课程映射**：141A (Solid State Physics, Kittel Ch 1-9) → 141B (Solid State Physics II, Kittel Ch 10-17 / Ashcroft & Mermin)
>
> **教材体系**：
> - **主教材**：Charles Kittel "Introduction to Solid State Physics" 9ed（Berkeley 141A，全球最广泛使用的固体物理教材）
> - **研究生标准**：Ashcroft & Mermin "Solid State Physics"（141B/研究生，更深入）
> - **进阶**：Marder "Condensed Matter Physics" / Chaikin & Lubensky "Principles of Condensed Matter Physics"
> - **Berkeley 特色**：Kittel 本人是 Berkeley 教授，固体物理泰斗；课程与 **LBNL（劳伦斯伯克利国家实验室）** 深度关联

---

## 目录

1. [§1 晶体结构](#1-晶体结构)
2. [§2 倒格子与衍射](#2-倒格子与衍射)
3. [§3 能带理论](#3-能带理论)
4. [§4 声子与晶格热学](#4-声子与晶格热学)
5. [§5 超导电性](#5-超导电性)
6. [§6 Berkeley 特色：LBNL 与凝聚态](#6-berkeley-特色lbnl-与凝聚态)
7. [习题集](#习题集)
8. [Python 演示](#python-演示)

---

## §1 晶体结构

### 1.1 Bravais 格子

**直觉**：固体的核心图像是"原子在空间周期排列"。一个 Bravais 格子是平移对称的离散点阵——从任意格点看出去，环境完全相同。

$$\mathbf{R} = n_1\mathbf{a}_1 + n_2\mathbf{a}_2 + n_3\mathbf{a}_3, \quad n_i \in \mathbb{Z}$$

其中 $\mathbf{a}_i$ 是原胞基矢。

**Kittel 的核心事实**：三维共有 **14 种 Bravais 格子**（分属 7 大晶系）。最常见的是：

| 结构 | 原子/原胞 | 堆积率 | 例子 |
|------|----------|--------|------|
| 简单立方 (SC) | 1 | 52% | Po（罕）|
| 体心立方 (BCC) | 2 | 68% | Fe, Cr, Na |
| 面心立方 (FCC) | 4 | 74% | Cu, Al, Au |
| 六方密堆 (HCP) | 2 | 74% | Mg, Zn, Ti |

**反直觉发现**：FCC 和 HCP 的堆积率相同（都是密堆积 74%），但结构不同——FCC 的堆叠顺序是 ABCABC，HCP 是 ABAB。这个看似微小的差别导致金属力学性质（如滑移系）截然不同。

### 1.2 Miller 指数

晶面用三个整数 $(hkl)$ 标记——晶面在三个晶轴上的截距倒数（化为互质整数）。

例：FCC 铜的 (111) 面是原子最密排的面，正是位错滑移面——决定了铜的延展性。

### 1.3 原胞与 Wigner-Seitz 原胞

**Wigner-Seitz 原胞**：围绕一个格点，到该格点比到其他格点都近的所有点的集合。这是唯一由格子本身决定（不依赖基矢选取）的原胞，也是倒空间第一布里渊区的定义基础。

---

## §2 倒格子与衍射

### 2.1 倒格子

**直觉**：正格子描述原子的真实位置；倒格子描述晶体的"周期性波矢"。两者通过傅里叶变换对偶。

倒格子基矢：

$$\mathbf{b}_1 = 2\pi\frac{\mathbf{a}_2\times\mathbf{a}_3}{\mathbf{a}_1\cdot(\mathbf{a}_2\times\mathbf{a}_3)}, \quad \text{（循环）}$$

满足正交关系 $\mathbf{a}_i\cdot\mathbf{b}_j = 2\pi\delta_{ij}$。

**反直觉**：正格子是 FCC 的晶体，倒格子是 BCC！反之亦然。这种对偶性简化了衍射分析。

### 2.2 布里渊区

**第一布里渊区**（First Brillouin Zone, FBZ）= 倒格子的 Wigner-Seitz 原胞。它是倒空间中"基本周期单元"，所有独特的电子态波矢都在 FBZ 内。

| 晶格 | 第一布里渊区形状 |
|------|----------------|
| SC | 立方体 |
| BCC | 截角八面体（14 面体）|
| FCC | 截角八面体（菱面十二面体，12 面）|

布里渊区的高对称点用字母标记：$\Gamma$（中心）、$X$、$L$、$K$、$W$ 等——这些是能带图（§3）的横轴。

### 2.3 衍射与 Bragg 定律

$$\boxed{2d\sin\theta = n\lambda}$$

其中 $d$ 是晶面间距，$\theta$ 是掠射角，$\lambda$ 是波长。

**Laue 条件**（更一般）：衍射峰出现在散射波矢改变 $\Delta\mathbf{k} = \mathbf{G}$（倒格子矢量）时。

$$\boxed{\mathbf{k}' - \mathbf{k} = \mathbf{G}}$$

### 2.4 LBNL 的 Advanced Light Source (ALS)

**Berkeley 特色**：LBNL 的 **Advanced Light Source (ALS)** 是世界顶级同步辐射光源（1993 建成），其软 X 射线波段的衍射、光电子能谱（ARPES）是研究凝聚态电子结构的利器。

ARPES（角分辨光电子能谱）直接"拍照"能带——测量光电子的角度和能量，反推出晶体中电子的色散关系 $E(\mathbf{k})$。这是验证能带理论（§3）最直接的实验。Berkeley 凝聚态实验组（如 Alessandra Lanzara 组）大量使用 ALS。

---

## §3 能带理论

### 3.1 自由电子气（Drude-Sommerfeld 模型）

**起点**：把金属中的电子当作自由电子气体（忽略离子势），用量子力学（Fermi-Dirac 统计，Topic 04）处理。

自由电子色散：$E = \frac{\hbar^2 k^2}{2m}$

Fermi 波矢：$k_F = (3\pi^2 n)^{1/3}$（$n$ = 电子密度）

Fermi 能：$\epsilon_F = \frac{\hbar^2}{2m}(3\pi^2 n)^{2/3}$

对铜：$\epsilon_F \approx 7$ eV，Fermi 温度 $T_F \approx 80000$ K。

**反直觉**：Fermi 速度 $v_F = \hbar k_F/m \approx 10^6$ m/s——即使在绝对零度，电子也在高速运动！常温下只有 Fermi 面附近 $k_B T/\epsilon_F \sim 0.3\%$ 的电子能参与输运。

### 3.2 近自由电子模型（NFE）与能隙

**Kittel Ch 7 核心**：在周期势 $V(\mathbf{r}) = V(\mathbf{r}+\mathbf{R})$ 中，电子不再是完全自由的。周期势在布里渊区边界（Bragg 面）处产生反射，导致**能隙**。

在 Bragg 条件 $k = G/2$ 处，两个简并平面波 $e^{ikx}$ 和 $e^{i(k-G)x}$ 耦合，简并解除：

$$E_\pm = \frac{\hbar^2}{2m}\left(\frac{G}{2}\right)^2 \pm |V_G|$$

能隙 $= 2|V_G|$。这就是**能带**的起源——周期势把连续的自由电子谱切割成一系列允许带，带间是禁带。

### 3.3 Bloch 定理

$$\boxed{\psi_{\mathbf{k}}(\mathbf{r}) = e^{i\mathbf{k}\cdot\mathbf{r}} u_{\mathbf{k}}(\mathbf{r}), \quad u_{\mathbf{k}}(\mathbf{r}) = u_{\mathbf{k}}(\mathbf{r}+\mathbf{R})}$$

**深刻含义**：周期势中的电子波函数是"平面波 $e^{ik\cdot r}$ × 周期函数 $u_k(r)$"。电子不是局域在原子周围，而是"自由穿梭"整个晶体——只是被周期函数调制。这就是为什么金属导电（电子非局域）而绝缘体不导电（虽然也是 Bloch 态，但能带填满）。

### 3.4 紧束缚模型（Tight-Binding）

从另一极端出发——原子轨道的线性组合（LCAO）。设每个原子有一个轨道 $\phi(\mathbf{r}-\mathbf{R})$：

$$\psi_{\mathbf{k}}(\mathbf{r}) = \sum_{\mathbf{R}} e^{i\mathbf{k}\cdot\mathbf{R}}\phi(\mathbf{r}-\mathbf{R})$$

一维紧束缚能带（最近邻跃迁 $t$）：

$$\boxed{E(k) = \epsilon_0 - 2t\cos(ka)}$$

**反直觉发现**：带宽 $= 4t$（从 $-2t$ 到 $+2t$）。跃迁 $t$ 越大，带越宽，电子越"自由"。绝缘体对应 $t\to 0$（电子被钉在原子上）。

### 3.5 导体、绝缘体、半导体

关键判据：**看最高占据带是否填满**。

| 类型 | 能带填充 | 禁带 $E_g$ | 例子 |
|------|---------|-----------|------|
| 金属 | 最高带半满 | 无 | Na, Cu |
| 绝缘体 | 带全满 | $E_g \gg k_BT$ ($\sim 5$ eV) | 金刚石 |
| 半导体 | 带全满 | $E_g \sim 1$ eV | Si (1.1), GaAs (1.4) |

**半导体原理**：$E_g$ 与 $k_BT$（常温 $\approx 0.026$ eV）可比，少量电子被热激发到导带，留下空穴——两者都参与导电。这就是现代电子学（晶体管、芯片）的物理基础。

### 3.6 有效质量

在能带极值附近展开 $E(k)$：

$$\frac{1}{m^*} = \frac{1}{\hbar^2}\frac{d^2E}{dk^2}$$

**反直觉**：有效质量 $m^*$ 可以是**负的**（在能带顶部）！这就是空穴——带正电的"准粒子"。GaAs 中电子 $m^* \approx 0.067 m_e$（比真空中轻 15 倍），这是高频器件的基础。

---

## §4 声子与晶格热学

### 4.1 一维原子链与色散关系

**Kittel Ch 4**：一维单原子链（力常数 $\beta$，原子质量 $M$，间距 $a$）的色散：

$$\boxed{\omega(k) = 2\sqrt{\frac{\beta}{M}}\left|\sin\left(\frac{ka}{2}\right)\right|}$$

**反直觉发现**：$\omega(k)$ 在 $k=0$ 附近是线性的（$\omega \approx c_s|k|$，声波），但在布里渊区边界 $k=\pi/a$ 处变平——这是 Bragg 反射的结果（与能隙同源）。波矢超过 $\pi/a$ 没有新振动模式（布里渊区外等价于区内）。

### 4.2 声学声子与光学声子

双原子链（如 NaCl，两原子质量 $M_1, M_2$）有两支：

- **声学支**（acoustic）：$\omega \to 0$ 当 $k\to 0$（两原子同向运动），对应声波。
- **光学支**（optical）：$\omega \neq 0$ 当 $k\to 0$（两原子反向运动），可被红外光激发——这就是"光学"声子的由来。

### 4.3 声子比热：Debye 模型 vs Einstein 模型

| 模型 | 假设 | 低温 $C_V$ |
|------|------|-----------|
| Einstein | 所有声子同频 $\omega_0$ | $\propto e^{-T_E/T}$（指数，错）|
| Debye | 声子谱 $\omega = c_s k$ 截止 $\omega_D$ | $\boxed{C_V \propto T^3}$（正确！）|

**Debye $T^3$ 律**：低温下只有长波声子被激发（低频态密度 $\propto \omega^2$），积分给出 $C_V \propto T^3$。这是凝聚态的标志性结果，与 Fermi 电子气的 $C_V \propto T$（Topic 04）形成对比。

Debye 温度：$\Theta_D = \hbar\omega_D/k_B$（典型 $\sim 100$–$400$ K）。

---

## §5 超导电性

### 5.1 实验现象

| 现象 | 描述 | 发现 |
|------|------|------|
| **零电阻** | $T < T_c$ 时电阻突降为零 | Kamerlingh Onnes 1911 (Hg, $T_c=4.2$ K) |
| **Meissner 效应** | 完全排斥磁场（$B=0$ 体内）| Meissner & Ochsenfeld 1933 |
| **能隙** | 准粒子激发需能量 $\Delta$ | 实验 1950s |
| **磁通量子化** | 磁通 $\Phi = n\Phi_0$, $\Phi_0 = h/2e$ | Deaver & Fairbank 1961 |

**反直觉**：Meissner 效应不是"完美导电"（零电阻维持磁通）——它是**主动排斥磁通**。把超导体降温过 $T_c$，原本穿过的磁场被踢出。这意味着超导是热力学相变，不只是电学性质突变。

### 5.2 London 方程

$$\boxed{\frac{\partial \mathbf{J}_s}{\partial t} = \frac{n_s e^2}{m}\mathbf{E}, \qquad \nabla\times\mathbf{J}_s = -\frac{n_s e^2}{m}\mathbf{B}}$$

第一个方程给出零电阻（电流无衰减地加速）；第二个结合 Maxwell 方程给出 Meissner 效应——磁场在超导体表面指数衰减，穿透深度 $\lambda_L = \sqrt{m/(\mu_0 n_s e^2)}$（典型 $\sim 100$ nm）。

### 5.3 BCS 理论（1957）

**Bardeen, Cooper, Schrieffer**（Berkeley 旧金山湾区连接：Schrieffer 是 Illinois，但 BCS 影响整个凝聚态社区）。核心思想：

1. **Cooper 对**：两个电子通过晶格振动（声子）媒介产生有效吸引力，形成束缚对。
2. **凝聚**：所有 Cooper 对凝聚到同一个量子态（宏观相干波函数）。
3. **能隙**：拆散一个 Cooper 对需要能量 $2\Delta$。

BCS 能隙方程（简化）：

$$\boxed{\Delta \approx 1.76\, k_B T_c \quad \text{(弱耦合极限)}}$$

**反直觉发现**：两个电子都是费米子（自旋 1/2），但配对后作为玻色子（整数自旋），可以凝聚——这就是 BEC（Topic 04）的精神在超导中的体现。但 Cooper 对很大（相干长度 $\xi \sim 1000$ Å），远大于对内距离——所以是"重叠的集体态"，不是独立的分子。

### 5.4 高温超导（铜氧化物）

1986 年 Bednorz & Müller 发现铜氧化物超导（La-Ba-Cu-O, $T_c=35$ K），掀起高潮。1987 年 YBCO 达 $T_c=92$ K（液氮温区！）。这些超导体**不能用 BCS 理论解释**——配对机制至今未明（可能非声子媒介）。

**Berkeley/LBNL 的角色**：LBNL 的 **Marvin Cohen** 组长期用第一性原理计算（密度泛函 DFT）预测超导材料；Berkeley 凝聚态实验组研究铜氧化物和铁基超导体的电子结构（ARPES @ ALS）。

---

## §6 Berkeley 特色：LBNL 与凝聚态

### Kittel 与 Berkeley 固体物理传统

**Charles Kittel**（1911-2019），Berkeley 教授（1951-1978）。他的《Introduction to Solid State Physics》自 1953 年初版以来更新至 9 版，是全球固体物理教学的标杆。Kittel 也是 Berkeley Physics Course 统计物理卷（Vol. 5 之前与 Kroemer 合著 Thermal Physics）的作者（见 Topic 04）。

Kittel 的教材特色：
1. **物理直觉优先**：每章从实验现象引入，再讲理论。
2. **图示丰富**：大量晶体结构图、能带图、实验数据。
3. **覆盖全面但不深**：适合本科入门，研究生转 Ashcroft & Mermin。

### LBNL（劳伦斯伯克利国家实验室）

UC Berkeley 与 **LBNL（Lawrence Berkeley National Laboratory）** 的紧密关联是 Berkeley 凝聚态物理的核心优势。LBNL 由 Berkeley 校友 **Ernest Lawrence**（诺贝尔奖 1939，回旋加速器发明者）创立（1931）。

LBNL 的凝聚态相关大科学装置：

| 装置 | 功能 | Berkeley 141 连接 |
|------|------|-----------------|
| **Advanced Light Source (ALS)** | 同步辐射光源（软X射线）| 能带 ARPES、衍射 |
| **Molecular Foundry** | 纳米材料合成与表征 | 纳米结构、二维材料 |
| **88-inch Cyclotron** | 离子束（核物理，见 Topic 07）| 材料辐照 |
| **NERSC 超算** | 大规模计算（DFT/量子模拟）| 第一性原理能带计算 |

### Berkeley 凝聚态研究前沿

| Berkeley 141 内容 | 研究前沿连接（Berkeley/LBNL）|
|-------------------|------------------------------|
| 能带理论 | 拓扑绝缘体（LBNL, Berkeley Ashvin Vishwanath 组）|
| 超导 | 铜氧化物/铁基 ARPES（Alessandra Lanzara 组）|
| 声子 | 超声/热输运（Berkeley 实验组）|
| 二维材料 | 石墨烯/过渡金属硫化物（Berkeley Feng Wang 组）|
| 强关联 | Hubbard 模型、量子自旋液体（Vishwanath, Yao 组）|
| 第一性原理 | DFT 预测新材料（LBNL Marvin Cohen 组）|

---

## 习题集

### 基础题（Kittel Ch 1-4）

**习题 6.1**：FCC 的堆积率是多少？证明 FCC 原胞有 4 个原子。
> **解**：原子半径 $r = a\sqrt{2}/4$（$a$ = 立方边长）。堆积率 $= 4 \cdot \frac{4}{3}\pi r^3/a^3 = \frac{\pi}{3\sqrt{2}} \approx 0.74$。

**习题 6.2**：写出简单立方格子的倒格子，并验证 $\mathbf{a}_i\cdot\mathbf{b}_j = 2\pi\delta_{ij}$。
> **解**：SC 的倒格子也是 SC，$\mathbf{b}_i = (2\pi/a)\hat{e}_i$。

**习题 6.3**：用 Bragg 定律计算铜（FCC, $a=3.61$ Å）的 (111) 面间距 $d_{111}$。
> **解**：$d_{hkl} = a/\sqrt{h^2+k^2+l^2} = 3.61/\sqrt{3} = 2.08$ Å。

### 中级题（能带与声子）

**习题 6.4**（自由电子气）：计算铜（$n=8.5\times10^{28}$ m$^{-3}$）的 Fermi 能和 Fermi 波矢。
> **解**：$k_F=(3\pi^2 n)^{1/3}=1.36\times10^{10}$ m$^{-1}$，$\epsilon_F=\hbar^2 k_F^2/(2m)=7.0$ eV。

**习题 6.5**（紧束缚）：一维紧束缚能带 $E(k)=\epsilon_0-2t\cos(ka)$。求电子的有效质量（带底和带顶）。
> **解**：$1/m^*=(1/\hbar^2)d^2E/dk^2=2ta^2\cos(ka)/\hbar^2$。带底($k=0$)：$m^*=\hbar^2/(2ta^2)>0$。带顶($k=\pi/a$)：$m^*<0$（空穴）。

**习题 6.6**（Debye 模型）：推导三维 Debye 模型的低温比热 $C_V \propto T^3$。
> **提示**：态密度 $g(\omega)\propto\omega^2$（三维），$C_V = \int_0^{\omega_D} g(\omega)\frac{\partial}{\partial T}[\hbar\omega\,n_B(\omega)]d\omega$，低温截断 $\omega_D\to\infty$ 无影响。

### 挑战题

**习题 6.7**（能隙估算）：近自由电子模型中，假设周期势傅里叶分量 $V_G = 1$ eV，估算第一布里渊区边界的能隙。
> **解**：能隙 $= 2|V_G| = 2$ eV。

**习题 6.8**（BCS）：解释为什么同位素效应（$T_c \propto M^{-1/2}$）支持声子配对机制。
> **提示**：声子频率 $\omega_D \propto \sqrt{\beta/M} \propto M^{-1/2}$，BCS 给 $T_c \propto \omega_D$。

**习题 6.9**（Meissner）：从 London 方程 $\nabla^2\mathbf{B}=\mathbf{B}/\lambda_L^2$ 出发，证明磁场在超导体表面指数衰减。
> **解**：半空间解 $B(x)=B(0)e^{-x/\lambda_L}$，$\lambda_L=\sqrt{m/(\mu_0 n_s e^2)}$。

---

## Python 演示

### 演示 1：能带结构（自由电子 vs 近自由电子 vs 紧束缚）

```python
"""
能带结构对比 — Berkeley 141A Kittel Ch 7
展示周期势如何把连续谱切成能带。
纯 NumPy。
"""
import numpy as np
import matplotlib.pyplot as plt

k = np.linspace(-np.pi, np.pi, 500)  # 波矢 (a=1)
a = 1.0

# 1. 自由电子 E = ℏ²k²/2m (归一化 ℏ²/2m = 1)
E_free = k**2

# 2. 近自由电子 (折叠到第一布里渊区)
# 自由电子能带折叠: E_n(k) = (k + n*2π/a)²
fig, axes = plt.subplots(1, 3, figsize=(15, 5))

ax = axes[0]
for n in [-2, -1, 0, 1, 2]:
    E_fold = (k + n*2*np.pi/a)**2
    ax.plot(k, E_fold, 'b-', linewidth=1.5)
ax.axvline(np.pi, color='gray', ls='--', alpha=0.5)
ax.axvline(-np.pi, color='gray', ls='--', alpha=0.5)
ax.set_xlabel('k'); ax.set_ylabel('E (free electron)')
ax.set_title('Free Electron\n(folded into BZ)')
ax.set_ylim(0, 50); ax.grid(alpha=0.3)

# 3. 近自由电子 + 能隙 (在交叉处打开间隙)
ax = axes[1]
# 手动在 BZ 边界打开能隙
for n in [-2, -1, 0, 1, 2]:
    E_fold = (k + n*2*np.pi/a)**2
    ax.plot(k, E_fold, 'b-', linewidth=1, alpha=0.5)
# 在 k=±π 处画能隙
gap = 2.0
ax.plot([np.pi, np.pi], [(np.pi)**2 - gap/2, (np.pi)**2 + gap/2], 'r-', linewidth=3)
ax.plot([-np.pi, -np.pi], [(np.pi)**2 - gap/2, (np.pi)**2 + gap/2], 'r-', linewidth=3)
ax.axvline(np.pi, color='gray', ls='--', alpha=0.5)
ax.axvline(-np.pi, color='gray', ls='--', alpha=0.5)
ax.set_xlabel('k'); ax.set_ylabel('E')
ax.set_title('Nearly-Free Electron\n(gaps open at BZ boundary)')
ax.set_ylim(0, 50); ax.grid(alpha=0.3)

# 4. 紧束缚能带
ax = axes[2]
t_vals = [1.0, 0.5, 0.2]
for t in t_vals:
    E_tb = -2*t*np.cos(k*a)  # ε₀=0
    ax.plot(k, E_tb, linewidth=2, label=f't = {t}')
ax.axvline(np.pi, color='gray', ls='--', alpha=0.5)
ax.axvline(-np.pi, color='gray', ls='--', alpha=0.5)
ax.set_xlabel('k'); ax.set_ylabel('E (tight-binding)')
ax.set_title('Tight-Binding Band\n(bandwidth = 4t)')
ax.legend(); ax.grid(alpha=0.3)
ax.annotate('m* > 0 (band bottom)', xy=(0, -2), fontsize=9, color='green')
ax.annotate("m* < 0 (hole, band top)", xy=(0.2, 1.5), fontsize=9, color='red')

plt.tight_layout()
plt.savefig('band_structure.png', dpi=150)
plt.show()
print("反直觉: 带顶有效质量为负 → 空穴带正电导电 (半导体的核心概念)")
```

**反直觉发现**：
1. **能带的起源纯粹是周期势 + 量子力学**——没有"原子间的化学键"概念，只有波动方程 + 边界条件。
2. **紧束缚带越窄（$t$ 小），电子越"重"（$m^*$ 大）**——绝缘体就是跃迁极弱的极限。

### 演示 2：声子色散与 Debye 模型

```python
"""
声子色散 + Debye 比热 — Berkeley 141A Kittel Ch 4-5
"""
import numpy as np
import matplotlib.pyplot as plt

a = 1.0; beta = 1.0; M = 1.0

# --- 1. 一维单原子链色散 ---
k = np.linspace(-np.pi/a, np.pi/a, 300)
omega = 2*np.sqrt(beta/M)*np.abs(np.sin(k*a/2))

# --- 2. 双原子链 (声学支 + 光学支) ---
M1, M2 = 1.0, 1.5
# ω² = β/M1M2 * [M1+M2 ± √((M1+M2)² - 4M1M2 sin²(ka))]
disc = (M1+M2)**2 - 4*M1*M2*np.sin(k*a/2)**2
omega_opt = np.sqrt(beta/(M1*M2) * (M1+M2 + np.sqrt(np.maximum(disc,0))))
omega_ac = np.sqrt(beta/(M1*M2) * (M1+M2 - np.sqrt(np.maximum(disc,0))))

fig, axes = plt.subplots(1, 2, figsize=(13, 5))

ax = axes[0]
ax.plot(k, omega, 'b-', linewidth=2.5, label='Single atom chain')
ax.plot(k, omega_ac, 'g-', linewidth=2, label='Acoustic branch (diatomic)')
ax.plot(k, omega_opt, 'r-', linewidth=2, label='Optical branch (diatomic)')
ax.set_xlabel('k'); ax.set_ylabel(r'$\omega(k)$')
ax.set_title('Phonon Dispersion\n(acoustic vs optical)')
ax.legend(); ax.grid(alpha=0.3)

# --- 3. Debye 模型比热 C_V ∝ T³ (低温) ---
ax = axes[1]
Theta_D = 343.0  # K (铜)
T = np.linspace(1, 400, 300)
# Debye 函数近似: C_V/(3NkB) = 完整 Debye 函数
# 简化: 低温 T³ 律, 高温 → 3 (Dulong-Petit)
def debye_cv(T, Theta_D):
    x = Theta_D / T
    # 数值积分 Debye 函数 D(x) = 3/x³ ∫₀ˣ t⁴eᵗ/(eᵗ-1)² dt
    t = np.linspace(0.001, np.minimum(x, 50), 500)
    integrand = t**4 * np.exp(t) / (np.exp(t) - 1)**2
    D = 3.0/x**3 * np.trapz(integrand, t)
    return np.minimum(D, 1.0)  # 归一化到 3NkB

Cv = np.array([debye_cv(t, Theta_D) for t in T])
ax.plot(T, Cv, 'b-', linewidth=2.5, label=f'Debye (Θ_D={Theta_D:.0f} K)')
# T³ 律拟合 (低温)
T_low = T[T < Theta_D/10]
ax.plot(T_low, (T_low/Theta_D)**3 * (np.pi**4/5), 'r--', linewidth=2, label=r'$T^3$ law (low T)')
ax.axhline(1.0, color='gray', ls=':', alpha=0.5, label='Dulong-Petit (high T)')
ax.set_xlabel('Temperature (K)'); ax.set_ylabel(r'$C_V / 3Nk_B$')
ax.set_title('Debye Specific Heat\n(low T: $T^3$, high T: Dulong-Petit)')
ax.legend(); ax.grid(alpha=0.3)

plt.tight_layout()
plt.savefig('phonons_debye.png', dpi=150)
plt.show()
print("反直觉: 声学支 k→0 是声波(线性), 光学支 k→0 仍有有限频率(可被红外光激发)")
```

**反直觉发现**：
1. **双原子链多出一条光学支**——两个原子反向振动，频率不为零（$k\to 0$），可被红外光直接激发。
2. **Debye $T^3$ 律的根源**：低温只有长波声子被激发，三维态密度 $\propto \omega^2$，积分给出 $T^3$。

### 演示 3：FCC 晶体结构可视化

```python
"""
FCC 晶体结构可视化 — Berkeley 141A Kittel Ch 1
"""
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

fig = plt.figure(figsize=(14, 5))

# --- FCC ---
ax = fig.add_subplot(131, projection='3d')
a = 1.0
# FCC: 顶点 + 面心
corners = np.array([[i,j,k] for i in [0,a] for j in [0,a] for k in [0,a]], dtype=float)
face_centers = np.array([
    [a/2,a/2,0],[a/2,a/2,a],[a/2,0,a/2],[a/2,a,a/2],
    [0,a/2,a/2],[a,a/2,a/2]
])
atoms = np.vstack([corners, face_centers])
# 扩展几个原胞看堆积
all_atoms = []
for dx in range(2):
    for dy in range(2):
        for dz in range(2):
            all_atoms.append(atoms + [dx*a, dy*a, dz*a])
all_atoms = np.vstack(all_atoms)
ax.scatter(all_atoms[:,0], all_atoms[:,1], all_atoms[:,2], s=80, c='steelblue', edgecolors='k')
ax.set_title('FCC Structure\n(Cu, Al, Au)')
ax.set_xlabel('x'); ax.set_ylabel('y'); ax.set_zlabel('z')

# --- 第一布里渊区 (FCC 的倒格子是 BCC, BZ 是截角八面体) ---
ax = fig.add_subplot(132)
# 简化: 画 BCC 倒格子的 Wigner-Seitz (菱面十二面体近似用多边形)
theta = np.linspace(0, 2*np.pi, 100)
# 截角八面体投影近似
r1 = 1.0; r2 = 0.7
x_bz = np.concatenate([r1*np.cos(theta[:25]), r2*np.cos(theta[25:50]),
                       r1*np.cos(theta[50:75]), r2*np.cos(theta[75:])])
y_bz = np.concatenate([r1*np.sin(theta[:25]), r2*np.sin(theta[25:50]),
                       r1*np.sin(theta[50:75]), r2*np.sin(theta[75:])])
ax.fill(x_bz, y_bz, alpha=0.3, color='orange')
ax.plot(x_bz, y_bz, 'b-', linewidth=2)
ax.plot(0,0,'ko',markersize=8); ax.annotate('$\\Gamma$', (0.05,0.05), fontsize=12)
ax.plot(1,0,'r^',markersize=10); ax.annotate('$X$', (1.05,0), fontsize=12)
ax.plot(0.5,0.5*np.sqrt(3),'gs',markersize=10); ax.annotate('$L$', (0.55,0.55), fontsize=12)
ax.set_title('FCC Brillouin Zone\n(BZ of FCC lattice)')
ax.set_aspect('equal'); ax.set_xlim(-1.5,1.5); ax.set_ylim(-1.5,1.5)
ax.grid(alpha=0.3); ax.set_xticks([]); ax.set_yticks([])

# --- 能带填充: 金属 vs 绝缘体 vs 半导体 ---
ax = fig.add_subplot(133)
# 画两个带 (价带填满, 导带空)
k = np.linspace(0,1,100)
E_val = -np.cos(k*np.pi)
E_cond = 1 + 0.5*np.cos(k*np.pi)
ax.fill_between(k, E_val, alpha=0.4, color='blue', label='Valence (filled)')
ax.plot(k, E_cond, 'r-', linewidth=2, label='Conduction (empty)')
gap_positions = [0.5]
for gap_x in gap_positions:
    ax.annotate('', xy=(gap_x, 1.0), xytext=(gap_x, 0.0),
                arrowprops=dict(arrowstyle='<->', color='green', lw=2))
    ax.text(gap_x+0.02, 0.5, '$E_g$', color='green', fontsize=14, fontweight='bold')
ax.set_xlabel('k'); ax.set_ylabel('E')
ax.set_title('Band Filling\n(metal: overlap; insulator: large $E_g$)')
ax.legend(loc='upper right'); ax.set_xticks([]); ax.grid(alpha=0.3)

plt.tight_layout()
plt.savefig('fcc_crystal_bz.png', dpi=150)
plt.show()
print("FCC: 74% 填充率(最高), 倒格子是 BCC, BZ 是菱面十二面体")
```

---

## 学习路径建议

```
141A (Kittel Ch 1-5)   →  晶体结构 + 倒格子 + 声子 + 热学
      ↓
141A (Kittel Ch 6-9)   →  自由电子气 + 能带 + 半导体
      ↓
141B (Kittel Ch 10-17)  →  超导 + 磁性 + 光学性质 + 介电
      ↓
研究生 (Ashcroft & Mermin) →  Green 函数 + 强关联 + 拓扑物态
```

**Kittel 教材学习节奏**（Berkeley 141A 一学期 15 周）：
- 周 1-3：Ch 1-2（晶体结构 + 倒格子）
- 周 4-5：Ch 3-4（晶体结合 + 声子）
- 周 6-7：Ch 5（热学性质，Debye 模型）
- 周 8-10：Ch 6-7（自由电子气 + 能带）
- 周 11-12：Ch 8（半导体）
- 周 13-14：Ch 9（费米面 + 输运）
- 周 15：Ch 10 引入（超导导引）

---

> **文件信息**：Berkeley Physics · Topic 06 Solid State Physics · 2026-08-12
>
> **教材交叉引用**：Kittel (141A) / Ashcroft & Mermin (141B/研究生) / Marder (进阶) · LBNL ALS/Molecular Foundry 关联

---

## 🎯 费曼式入口（白话版）

> **一句话解释**：固体物理研究"为什么不同的材料性质天差地别"——为什么铜导电而玻璃不导电？为什么磁铁有磁性？为什么硅可以做芯片而沙子（也是硅）不行？答案藏在原子如何排列、电子如何在晶格中运动。
>
> **生活类比**：想象一个巨大的停车场，车位整齐排列（晶格）。电子像车在里面找车位停。在金属里，车位没停满，车可以自由移动（导电）；在绝缘体里，车位全满或全空，车动不了（不导电）；半导体介于两者之间——稍微给点能量（光、热），车就能移动。改变停车场的设计（掺杂、应变、堆叠），材料的性质可以天翻地覆——这就是现代材料工程的魔力。
>
> **反直觉发现**：
> - **能带 = 无数原子的"交通拥堵"**：孤立原子的电子能级是离散的线条。但当 $10^{23}$ 个原子组成晶体，每个能级分裂成 $10^{23}$ 条线，挤在一起变成连续的"带"。带和带之间的间隙（禁带）决定了材料是导体还是绝缘体。
> - **声子是粒子的"幻觉"**：晶体中原子的集体振动，表现得像一种粒子——叫声子。它不是真正的粒子，但有动量、有能量、能"碰撞"。热传导、超导、热膨胀都靠声子。
> - **莫尔(moiré)魔法**：把两层石墨烯旋转 1.1°，原本导电的石墨烯突然变成绝缘体甚至超导体！这种"扭一下就变天"的现象叫魔角石墨烯，2018 年发现，开创了"twistronics"新领域。
> - **拓扑绝缘体**：材料内部是绝缘体，但表面是完美导体——电子在表面跑没有电阻。这不是杂质效应，而是材料的拓扑性质——像甜甜圈的洞数，连续变形不会改变。

---

## 🔗 衔接：从哪来，到哪去

### 前置知识
- **Topic 01 经典力学**：晶格振动（声子）= 耦合振子链；有效势与晶体结合
- **Topic 02 电磁学**：电子-离子电磁相互作用；Coulomb 力决定晶体结合类型
- **Topic 03 量子力学**：能带 = 周期势中的薛定谔方程解；自旋 → 磁性
- **Topic 04 统计物理**：Fermi-Dirac 分布 → 电子统计；Bose-Einstein → 声子热容(Debye 模型)
- **Topic 05 数学方法**：倒格子 = 傅里叶变换；布里渊区 = 倒空间原胞

### 本主题解决了什么危机
- **经典电子论的失败**（Drude 模型 1900）：经典理论预言金属的电子比热应为 $\frac{3}{2}k_B$，但实验只有它的 1/100。答案需要量子力学——Fermi-Dirac 统计使绝大多数电子"冻结"在费米面以下，只有费米面附近的电子参与热运动。
- **超导之谜**（1911-1957）：零电阻和完全抗磁性（Meissner 效应）是什么机制？1957 年 BCS 理论给出答案：电子通过声子介导配对（Cooper pair），凝聚成宏观量子态。但高温超导（铜基，1986）至今没有公认理论！
- **半导体工程**：纯硅导电性很差，但掺入百万分之一的杂质（磷/硼）就能让它变成 n 型/p 型半导体。PN 结 = 二极管 = 芯片的基础。没有固体物理就没有现代电子学。

### 本主题留下的新危机
- **高温超导机制未解**：铜基超导体（$T_c = 164$ K）和铁基超导体（2008）的机制不能用 BCS 理论解释。这是凝聚态物理最大的未解之谜。
- **强关联电子系统**：当电子-电子相互作用很强（如过渡金属氧化物），能带论失效。$N$ 体量子系统无法精确求解——需要新理论框架。
- **拓扑物态的边界**：拓扑绝缘体、拓扑半金属、分数量子霍尔效应……拓扑物态的"动物园"还在不断扩大，统一理论尚在探索。
- **量子材料的计算瓶颈**：预言新材料的性质需要量子力学计算，但计算量随系统大小指数增长。AI/ML 正在填补这个空缺。

### 后续主题
- → Berkeley **141B**：超导、磁性、光学性质、介电性质
- → 研究生 **230**：凝聚态多体理论（Green 函数、Feynman 图）
- → **Topic 07 粒子物理**：凝聚态中的"涌现粒子"（声子、磁子、任意子）与高能粒子物理的深层平行
- → LBNL **ALS (Advanced Light Source)** + **Molecular Foundry**：实验表征与材料合成

---

## 🏭 理论联系实际：5 个应用

1. **半导体芯片（CPU/GPU/存储）**：台积电 3nm 芯片上的晶体管只有几十个原子宽。每个晶体管的工作原理是量子力学的能带工程——掺杂、栅极氧化层、量子隧穿效应都被精确利用。Berkeley EECS 与材料系联合开发下一代 2nm 工艺。

2. **LED 照明与激光**：发光二极管的效率是白炽灯的 20 倍。核心是半导体能带工程——电子从导带跃迁到价带，释放的光子能量等于禁带宽度 $E_g$。蓝光 LED（氮化镓）的发明获得 2014 年诺贝尔物理学奖。

3. **太阳能电池**：光伏效应 = 半导体吸收光子产生电子-空穴对。钙钛矿太阳能电池效率从 2009 年的 3.8% 飙升到 2025 年的 26%+。Berkeley 的材料科学家开发新型钙钛矿/硅叠层电池，效率突破 30%。

4. **高温超导电缆**：液氮温度（77 K）工作的钇钡铜氧(YBCO)超导线缆，电流密度是铜线的 100 倍且零损耗。已在芝加哥、上海等城市铺设超导电网。Berkeley LBNL 是高温超导材料研究的全球中心之一。

5. **量子点显示(QLED)与量子传感**：纳米级半导体晶粒（量子点）的发光颜色由尺寸决定——量子约束效应。三星 QLED 电视利用此原理。NV 色心（金刚石中的量子缺陷）可检测纳米级磁场，用于绘制神经元活动和探测暗物质。Berkeley 的量子材料组在此领域领先。

---

## 🔬 最新研究前沿（2024-2026）

1. **首次绘制固体的"量子几何"地图**（2025-06-06, Quanta Magazine）：物理学家用新方法绘制了晶体隐藏的量子几何形状——波函数的"内部结构"首次被可视化。这一方法预计将变得无处不在，对拓扑材料和量子计算有深远影响。LBNL ALS 的实验数据支持此突破。

2. **魔角石墨烯的"twistronics"革命**（2024-2025）：把两层或三层石墨烯以特定"魔角"堆叠，可以产生超导、铁磁性、拓扑绝缘态等多种物相——仅靠旋转角度就能调控。Berkeley 的 Feng Wang 组在此领域发表多篇 Nature 论文，展示了三层魔角石墨烯中的超导机制。

3. **拓扑量子计算与任意子**（2024-2025）：拓扑材料中的非阿贝尔任意子被提议用于容错量子计算——信息编码在拓扑性质中，天然抵抗局部噪声。Microsoft 的拓扑量子计算机项目持续推进。Berkeley 的凝聚态理论组研究分数量子霍尔态中的任意子激发。

4. **AI 驱动的材料发现**（2024-2025）：Google DeepMind 的 GNoME 模型预测了 220 万种新晶体结构——相当于人类近 800 年的实验发现量。Berkeley 的 Materials Project 数据库与 LBNL Molecular Foundry 合作，用 AI 筛选高效电池、超导、拓扑材料候选。

5. **二维材料的异质结构"乐高"**（2024-2026）：像搭乐高一样，将不同的二维材料（石墨烯、氮化硼、过渡金属硫族化合物）逐层堆叠，精确控制层间扭转角度和间距——创造出自然界不存在的物相。Berkeley 的 CIFAR 量子材料项目和 LBNL 的用户设施支撑此领域研究。

---

## 🗺️ 学习 Roadmap（Berkeley 路径）

```
 7A/7B — 基础物理
      ↓
 141A — Introduction to Solid State Physics (Kittel)
      │  晶体结构(布拉维格子) · 倒格子(X射线衍射) · 晶体结合 · 声子(Debye模型)
      │  · 自由电子气(Fermi能级/Sommerfeld) · 能带(紧束缚/近自由电子) · 半导体
      │  ✅ 知识检查：能否画出 FCC 的布里渊区？能否解释为什么硅是半导体而铜是金属？
      ↓
 141B — Solid State Physics II (Kittel / Ashcroft & Mermin)
      │  超导(BCS理论) · 磁性(铁磁/反铁磁/自旋) · 光学性质 · 介电性质 · 超流
      │  ✅ 知识检查：能否解释 Cooper 配对的物理图像？能否区分铁磁和反铁磁？
      ↓
 研究生 (Ashcroft & Mermin / Marder)
      │  Green 函数 · 强关联电子 · 拓扑物态 · 量子霍尔效应
      │  ✅ 知识检查：能否解释量子反常霍尔效应的机制？
      ↓
 研究前沿 → 量子材料 · 拓扑计算 · AI材料发现 · twistronics
      │
      │  🔬 LBNL 关联：ALS (Advanced Light Source) · Molecular Foundry ·(superconducting quantum materials)
```

**核心教材节奏**：
| 阶段 | 教材 | 周数 | 核心概念 |
|------|------|------|----------|
| 141A | Kittel Ch 1-9 | 15 周 | 晶体 + 声子 + 能带 + 半导体 |
| 141B | Kittel Ch 10-17 | 15 周 | 超导 + 磁性 + 光学 |
| 研究生 | Ashcroft & Mermin | — | 多体理论 + 拓扑 |

**费曼学习法检查点**：
- [ ] 能否用白话解释"为什么金属导电而绝缘体不导电"？（能带填充 + 禁带）
- [ ] 能否解释为什么魔角石墨烯转 1.1° 就能超导？（莫尔超晶格→平带→强关联）
- [ ] 能否解释声子为什么不是"真正的粒子"但行为像粒子？（集体激发=准粒子）
- [ ] 能否描述 BCS 超导理论的核心图像？（电子-声子-电子配对→凝聚）
