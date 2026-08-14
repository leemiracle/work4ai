# Topic 08 · 广义相对论与宇宙学（MIT 8.962 / 8.286 / 8.901）

> **教材**：Sean M. Carroll《Spacetime and Geometry》+ Scott Dodelson《Modern Cosmology》
>
> **覆盖课程**：
> - **8.962** General Relativity（Carroll：等效原理 / 微分几何 / Einstein 方程 / 黑洞 / 引力波）
> - **8.286** The Early Universe（Dodelson：FLRW 宇宙学 / 暴胀 / CMB / 大爆炸核合成）
> - **8.901** Astrophysics（黑洞天体物理 / 暗物质 / 宇宙学常数）
>
> **宪法**：直觉 → 公式 → 代码(bash 跑通) → 不足 → 应用

---

## 目录

1. [等效原理](#1-等效原理)
2. [微分几何基础](#2-微分几何基础)
3. [爱因斯坦场方程](#3-爱因斯坦场方程)
4. [史瓦西解与黑洞](#4-史瓦西解与黑洞)
5. [引力波](#5-引力波)
6. [FLRW 宇宙学](#6-flrw-宇宙学)
7. [暗物质与暗能量](#7-暗物质与暗能量)
8. [Python 代码演示](#8-python-代码演示)
9. [习题与解答](#9-习题与解答)
10. [反直觉发现](#10-反直觉发现)
11. [不足与延伸](#11-不足与延伸)

---

## 1. 等效原理

### 1.1 三种表述

**弱等效原理（WEP）**：惯性质量 $m_i$ = 引力质量 $m_g$。

$$
m_i\mathbf{a} = -m_g\nabla\Phi \implies \mathbf{a} = -\nabla\Phi \quad (\text{与材料无关})
$$

→ 所有物体在引力场中下落相同。Galileo 的比萨斜塔实验（Eötvös 精度 $10^{-15}$）。

**爱因斯坦等效原理（EEP）**：在局部自由下落参考系中，**一切物理定律**（不只是力学）退化为狭义相对论形式。

**强等效原理（SEP）**：EEP 对引力自身也成立（包括引力能量下落）。广义相对论满足 SEP，但许多修改引力理论不满足。

### 1.2 引力 = 时空弯曲

EEP 的深刻推论：**引力不是力，而是时空几何**。

自由下落的物体走"直线"（测地线）——是时空本身被质量弯曲了。

爱因斯坦的洞见：如果 $m_i = m_g$，那么引力效应可以完全消除（自由下落参考系）。这暗示引力是运动学（几何）效应，不是动力学（力）效应。

### 1.3 引力红移

从引力势 $\Phi_1$ 处发射光子，在 $\Phi_2$ 处接收。频率移动：

$$
\frac{\Delta\nu}{\nu} = -\frac{\Delta\Phi}{c^2}
$$

→ 光从引力势高处（离质量远）传到低处蓝移，反之红移。这不是多普勒效应——是时钟在不同引力势下快慢不同（引力时间膨胀）。

GPS 卫星（离地 20000 km）的时钟每天比地面快约 38 μs——必须修正引力红移（否则导航误差累积 ~10 km/天）。

---

## 2. 微分几何基础

### 2.1 度规张量

时空的几何完全由**度规张量** $g_{\mu\nu}$ 描述——它定义时空间隔：

$$
ds^2 = g_{\mu\nu}\,dx^\mu\,dx^\nu
$$

- 狭义相对论（Minkowski）：$ds^2 = -c^2dt^2 + dx^2 + dy^2 + dz^2$，度规 $\eta_{\mu\nu} = \text{diag}(-1,+1,+1,+1)$
- 球面：$ds^2 = R^2(d\theta^2 + \sin^2\theta\,d\phi^2)$

**度规决定一切**：距离、角度、面积、曲率——全部从 $g_{\mu\nu}$ 推出。

### 2.2 协变导数与联络

普通偏导数 $\partial_\mu$ 在弯曲时空中不是张量（变换出额外项）。需要**协变导数**：

$$
\nabla_\mu V^\nu = \partial_\mu V^\nu + \Gamma^\nu_{\mu\lambda}V^\lambda
$$

$\Gamma^\nu_{\mu\lambda}$ 是**克里斯托费尔符号**（联络），由度规导数给出：

$$
\Gamma^\lambda_{\mu\nu} = \frac{1}{2}g^{\lambda\sigma}(\partial_\mu g_{\nu\sigma} + \partial_\nu g_{\mu\sigma} - \partial_\sigma g_{\mu\nu})
$$

直觉：$\Gamma$ 编码了坐标基矢量如何随位置变化——是"弯曲"的体现。

### 2.3 测地线方程

自由粒子在弯曲时空中走"最直"的路径（测地线）：

$$
\boxed{\frac{d^2x^\mu}{d\tau^2} + \Gamma^\mu_{\alpha\beta}\frac{dx^\alpha}{d\tau}\frac{dx^\beta}{d\tau} = 0}
$$

$\tau$ 是固有时。$\Gamma$ 项就扮演了"引力加速度"的角色——牛顿引力方程 $d^2\mathbf{x}/dt^2 = -\nabla\Phi$ 是测地线方程的弱场极限。

### 2.4 黎曼曲率张量

曲率的最完整描述：

$$
R^\rho_{\;\;\sigma\mu\nu} = \partial_\mu\Gamma^\rho_{\nu\sigma} - \partial_\nu\Gamma^\rho_{\mu\sigma} + \Gamma^\rho_{\mu\lambda}\Gamma^\lambda_{\nu\sigma} - \Gamma^\rho_{\nu\lambda}\Gamma^\lambda_{\mu\sigma}
$$

**直观判据**：沿闭合回路平行移动矢量，回来时是否改变方向。如果改变→该区域有曲率。

**缩并**：

- **里奇张量**：$R_{\mu\nu} = R^\lambda_{\;\;\mu\lambda\nu}$
- **标量曲率**：$R = g^{\mu\nu}R_{\mu\nu}$

平坦时空：$R^\rho_{\;\;\sigma\mu\nu} = 0$。球面：$R > 0$（正曲率）。马鞍面：$R < 0$（负曲率）。

---

## 3. 爱因斯坦场方程

### 3.1 方程的形式

$$
\boxed{G_{\mu\nu} + \Lambda g_{\mu\nu} = \frac{8\pi G}{c^4}T_{\mu\nu}}
$$

- $G_{\mu\nu} = R_{\mu\nu} - \frac{1}{2}Rg_{\mu\nu}$：**爱因斯坦张量**（几何侧）
- $\Lambda$：**宇宙学常数**（暗能量）
- $T_{\mu\nu}$：**能动张量**（物质侧）

**核心思想**：物质告诉时空如何弯曲（$T \to G$），时空告诉物质如何运动（$g_{\mu\nu}\to$ 测地线）。

Wheeler 的经典总结："Spacetime tells matter how to move; matter tells spacetime how to curve."

### 3.2 推导思路

爱因斯坦花了 8 年（1907-1915）找到这个方程。关键约束：

1. **广义协变性**：方程在任意坐标变换下形式不变。
2. **能量-动量守恒**：$\nabla_\mu T^{\mu\nu} = 0$（自动满足，因为 $\nabla_\mu G^{\mu\nu} = 0$）。
3. **弱场极限**：必须退化为牛顿引力 $\nabla^2\Phi = 4\pi G\rho$。

系数 $8\pi G/c^4$ 极小（$\sim 10^{-43}$ N$^{-1}$）——意味着**需要天文级能量才能产生可测量的时空弯曲**。这就是引力为什么这么弱。

### 3.3 能动张量

不同物质的能动张量：

| 物质 | $T_{\mu\nu}$ | 状态方程 $w = p/\rho$ |
|------|-------------|----------------------|
| 真空能 | $-\rho_{\text{vac}}g_{\mu\nu}$ | $w = -1$ |
| 宇宙学常数 | $-\frac{\Lambda c^4}{8\pi G}g_{\mu\nu}$ | $w = -1$ |
| 辐射 | $\text{diag}(\rho, p, p, p)$, $p=\rho/3$ | $w = 1/3$ |
| 尘埃（无压物质） | $\text{diag}(\rho, 0, 0, 0)$ | $w = 0$ |

### 3.4 施瓦茨席尔德解的预言

球对称真空的解（Schwarzschild 1916）：

$$
ds^2 = -\left(1-\frac{2GM}{c^2r}\right)c^2dt^2 + \left(1-\frac{2GM}{c^2r}\right)^{-1}dr^2 + r^2d\Omega^2
$$

三大经典检验：

1. **水星近日点进动**：牛顿力学预测 532"/百年，观测 574"/百年，差 43"——广义相对论精确填补。
2. **光线偏折**：经过太阳边缘偏折 $1.75''$（Eddington 1919 日全食验证）。
3. **引力时间延迟**：雷达信号往返延迟（Shapiro 1964 验证）。

---

## 4. 史瓦西解与黑洞

### 4.1 事件视界

Schwarzschild 半径（引力半径）：

$$
r_s = \frac{2GM}{c^2}
$$

对太阳 $r_s \approx 3$ km，对地球 $r_s \approx 9$ mm。

$r = r_s$ 处 $g_{tt}\to 0$，$g_{rr}\to\infty$——**事件视界**。一旦越过，无法返回。

### 4.2 黑洞的性质

**无毛定理**：稳态黑洞完全由三个量描述——质量 $M$、电荷 $Q$、角动量 $J$。所有其他信息（头发）在坍缩中辐射掉。

Kerr 度规（旋转黑洞）：

$$
ds^2 = -\left(1-\frac{r_s r}{\Sigma}\right)c^2dt^2 + \frac{\Sigma}{\Delta}dr^2 + \Sigma\,d\theta^2 + \left(r^2+a^2+\frac{r_s r a^2}{\Sigma}\sin^2\theta\right)\sin^2\theta\,d\phi^2 - \frac{2r_s r a\sin^2\theta}{\Sigma}\,c\,dt\,d\phi
$$

其中 $\Sigma = r^2 + a^2\cos^2\theta$，$\Delta = r^2 - r_sr + a^2$，$a = J/(Mc)$。

旋转黑洞有**能层**（ergosphere）——在其中不可能静止，被拖拽旋转（坐标系拖拽效应 / Lense-Thirring 效应）。

### 4.3 引力时间膨胀

在引力势 $\Phi(r)$ 处的固有时 $d\tau$ 与无穷远处坐标时 $dt$ 的关系：

$$
d\tau = \sqrt{1 - \frac{r_s}{r}}\,dt
$$

→ 靠近视界，时钟越来越慢（外观察者视角）。$r\to r_s$ 时 $d\tau\to 0$——外观察者永远看不到物体穿越视界（无限红移）。

但从自由下落者的视角，穿越视界毫无异常——只是无法回头。

### 4.4 黑洞热力学

Bekenstein-Hawking 熵：

$$
S_{\text{BH}} = \frac{k_B c^3 A}{4G\hbar} = \frac{k_B A}{4\ell_P^2}
$$

$A$ 是视界面积，$\ell_P = \sqrt{G\hbar/c^3} \approx 1.6\times 10^{-35}$ m 是普朗克长度。

Hawking 温度（霍金辐射）：

$$
T_H = \frac{\hbar c^3}{8\pi G M k_B}
$$

→ 黑洞越小越"热"。太阳质量黑洞 $T_H\sim 10^{-7}$ K（远低于 CMB 2.7 K → 目前在吸热增长而非蒸发）。

---

## 5. 引力波

### 5.1 线性化引力

弱场近似 $g_{\mu\nu} = \eta_{\mu\nu} + h_{\mu\nu}$（$|h_{\mu\nu}|\ll 1$）。在适当规范（TT 规范）下，真空场方程退化为**波动方程**：

$$
\Box\bar{h}_{\mu\nu} = 0 \implies \bar{h}_{\mu\nu} = A_{\mu\nu}e^{ik_\alpha x^\alpha}
$$

→ **引力波**以光速传播！横波、自旋 2（张量波）。

### 5.2 引力波探测

LIGO 激光干涉仪：两臂各 4 km，引力波通过时拉伸/压缩臂长 $\Delta L/L \sim h \sim 10^{-21}$。

→ $\Delta L \sim 4\times 10^3\times 10^{-21} = 4\times 10^{-18}$ m = 质子直径的 $10^4$ 分之一。

2015 年 9 月 14 日首次直接探测到 GW150914——两个黑洞（29 + 36 太阳质量）合并，释放 3 个太阳质量的引力波能量（2017 诺奖）。

### 5.3 引力波源

- **致密双星合并**（黑洞-黑洞、中子星-中子星、混合）：LIGO/Virgo 探测频段 10-1000 Hz。
- **超大质量黑洞合并**：脉冲星计时阵列（PTA）探测纳赫兹频段。2023 年 NANOGrav 报告首批随机引力波背景证据。
- **宇宙暴胀原初引力波**：CMB B 模偏振（BICEP-Array 寻找中）。

---

## 6. FLRW 宇宙学

### 6.1 宇宙学原理

在大尺度（>100 Mpc）上，宇宙是**均匀且各向同性**的。度规（Friedmann-Lemaître-Robertson-Walker, FLRW）：

$$
ds^2 = -c^2dt^2 + a^2(t)\left[\frac{dr^2}{1-kr^2} + r^2d\Omega^2\right]
$$

- $a(t)$：**尺度因子**（宇宙膨胀/收缩）
- $k$：空间曲率（$+1$ 球面, $0$ 平坦, $-1$ 双曲）

### 6.2 哈勃定律

遥远星系退行速度与距离成正比：

$$
v = H_0 d, \qquad H_0 \approx 70\text{ km/s/Mpc}
$$

哈勃常数 $H_0$ 的精确值仍有争议（Hubble tension）：CMB 推出 $67.4\pm 0.5$，造父变星-超新星推出 $73.0\pm 1.0$ km/s/Mpc——差异 ~5σ。

### 6.3 Friedmann 方程

将 FLRW 度规代入 Einstein 方程：

$$
\boxed{\left(\frac{\dot{a}}{a}\right)^2 = \frac{8\pi G}{3}\rho - \frac{kc^2}{a^2} + \frac{\Lambda c^2}{3}}
$$

$$
\frac{\ddot{a}}{a} = -\frac{4\pi G}{3}\left(\rho + \frac{3p}{c^2}\right) + \frac{\Lambda c^2}{3}
$$

关键参数：

- **临界密度** $\rho_c = 3H^2/(8\pi G)$
- **密度参数** $\Omega = \rho/\rho_c$（$\Omega > 1$ 闭合, $= 1$ 平坦, $< 1$ 开放）

当前宇宙 $\Omega_{\text{total}} \approx 1.00\pm 0.01$ → **空间平坦**。

### 6.4 宇宙的组分

| 组分 | $\Omega$ | 状态方程 $w$ | 密度演化 $\rho(a)$ |
|------|---------|------------|-------------------|
| 辐射（光子+相对论中微子） | $\sim 5\times 10^{-5}$ | $1/3$ | $a^{-4}$ |
| 物质（重子+暗物质） | $\sim 0.31$ | $0$ | $a^{-3}$ |
| 暗能量（Λ） | $\sim 0.69$ | $-1$ | $a^0$（常数） |
| 曲率 | $\sim 0$ | $-1/3$ | $a^{-2}$ |

### 6.5 宇宙演化历史

1. **暴胀** ($t < 10^{-32}$ s)：指数膨胀 $a\sim e^{Ht}$，解决视界和平坦性问题。
2. **辐射主导** ($t < 50{,}000$ 年)：$\rho \propto a^{-4}$ 主导，$a(t)\propto t^{1/2}$。
3. **物质主导** ($50{,}000$ 年 $< t < 5$ Gyr)：$\rho \propto a^{-3}$ 主导，$a(t)\propto t^{2/3}$。
4. **暗能量主导** ($t > 5$ Gyr)：$\Lambda$ 主导，$a(t)\propto e^{Ht}$，加速膨胀。

→ 宇宙在加速膨胀！1998 年超新星观测发现（2011 诺奖，Perlmutter/Schmidt/Riess）。

### 6.6 大爆炸核合成 (BBN)

宇宙年龄 1 秒到 3 分钟（$T\sim 10^{10}\to 10^9$ K），质子和中子聚变形成轻核：

| 核 | 丰度（按质量） |
|----|--------------|
| $^1$H | ~75% |
| $^4$He | ~25% |
| D, $^3$He | ~$10^{-5}$ |
| $^7$Li | ~$10^{-10}$ |

这些丰度精确依赖于重子密度 $\Omega_b h^2$。BBN 预言与观测吻合——大爆炸模型最强证据之一。

### 6.7 宇宙微波背景 (CMB)

宇宙年龄 38 万年时（$T\sim 3000$ K），电子与质子复合成中性氢，光子与物质退耦→自由传播至今。

- **温度**：$T_{\text{CMB}} = 2.7255\pm 0.0006$ K（几乎完美各向同性）
- **涨落**：$\Delta T/T \sim 10^{-5}$（原初密度涨落的遗迹）

COBE（1989）/ WMAP（2003）/ Planck（2013）的 CMB 各向异性测量精确确定宇宙学参数——这是精确宇宙学的基石。

---

## 7. 暗物质与暗能量

### 7.1 暗物质的证据

1. **星系旋转曲线**：外围恒星速度 $v(r)$ 不下降（$v\sim$ const 而非 $v\propto r^{-1/2}$）→ 有看不见的引力源（暗物质晕）。Rubin & Ford 1970s。
2. **引力透镜**：遥远星系光线被前景质量弯曲——测出的质量远超可见物质。
3. **CMB 峰位**：声学峰位置精确给出 $\Omega_m \approx 0.31$，而重子 $\Omega_b\approx 0.05$ → 暗物质 $\Omega_{\text{DM}}\approx 0.26$。
4. **子弹星系团**（1E 0657-558）：两个星系团碰撞，X 射线气体（重子物质）被减速在中间，引力中心（用引力透镜测）在两侧——直接显示暗物质几乎无碰撞地穿过。

### 7.2 暗物质候选

| 候选 | 质量 | 探测方法 |
|------|------|---------|
| WIMP（弱相互作用大质量粒子） | GeV-TeV | 直接探测（液氙）、间接探测（γ射线）、对撞机 |
| 轴子（Axion） | $\mu$eV-meV | 腔探测（ADMX） |
| 惰性中微子 | keV | X 射线谱线 |
| 原初黑洞 | $10^{-16}\sim 10^2\,M_\odot$ | 微透镜 |

目前无直接探测确认——暗物质是粒子物理和宇宙学最大的谜团之一。

### 7.3 暗能量

宇宙加速膨胀的来源。最简单的解释是**宇宙学常数** $\Lambda$（真空能）。

但量子场论预测真空能密度 $\rho_{\text{vac}}\sim M_P^4$，比观测值大 $10^{120}$ 倍——**物理学最差预测**。

→ "宇宙学常数问题"是理论物理最大的未解问题之一。可能的替代方案：精质场（quintessence, $w\neq -1$）、修改引力。

---

## 8. Python 代码演示

### 8.1 史瓦西度规与引力时间膨胀

```python
"""
(a) Schwarzschild 度规分量 g_tt 和 g_rr vs r/r_s
(b) 引力时间膨胀: dτ/dt = √(1 - r_s/r)
"""
import numpy as np
import matplotlib.pyplot as plt

r_rs = np.linspace(1.01, 10, 500)  # r/r_s, 从视界外开始

g_tt = -(1 - 1/r_rs)
g_rr = 1 / (1 - 1/r_rs)

fig, axes = plt.subplots(1, 2, figsize=(13, 5))

# (a) 度规分量
axes[0].plot(r_rs, g_rr, 'r-', linewidth=2, label='$g_{rr}$')
axes[0].plot(r_rs, g_tt, 'b-', linewidth=2, label='$g_{tt}$')
axes[0].axvline(1.0, color='gray', linestyle='--', alpha=0.7, label='事件视界 $r=r_s$')
axes[0].axhline(0, color='gray', linewidth=0.5)
axes[0].fill_betweenx([-2, 30], 1.0, 1.05, color='black', alpha=0.3)
axes[0].set_xlabel('$r/r_s$'); axes[0].set_ylabel('度规分量')
axes[0].set_title('Schwarzschild 度规分量')
axes[0].set_ylim(-1.5, 10); axes[0].set_xlim(0.8, 6)
axes[0].legend(fontsize=9); axes[0].grid(alpha=0.3)

# (b) 时间膨胀
dtau_dt = np.sqrt(1 - 1/r_rs)
axes[1].plot(r_rs, dtau_dt, 'g-', linewidth=2)
axes[1].axvline(1.0, color='gray', linestyle='--', alpha=0.7, label='事件视界')
axes[1].axhline(0, color='gray', linewidth=0.5)
axes[1].fill_between(r_rs, dtau_dt, 1, alpha=0.1, color='green')
axes[1].set_xlabel('$r/r_s$'); axes[1].set_ylabel('$d\\tau/dt$ (固有/坐标)')
axes[1].set_title('引力时间膨胀: 靠近视界时钟冻结')
axes[1].set_ylim(-0.1, 1.1); axes[1].set_xlim(0.8, 8)
axes[1].legend(fontsize=9); axes[1].grid(alpha=0.3)

# 标注 GPS 轨道
r_gps = (6371 + 20000) / (2*9.870e-3)  # r_s(earth) ≈ 8.87 mm ≈ 9mm
axes[1].annotate('GPS 卫星\n在此附近\n(地球 r_s≈9mm)', xy=(5, 0.9), fontsize=8, color='purple')

plt.tight_layout()
plt.savefig('schwarzschild_metric.png', dpi=110, bbox_inches='tight')
print("已保存 schwarzschild_metric.png")
print(f"r=2r_s: dτ/dt = √(1-1/2) = {np.sqrt(0.5):.4f} (慢 29%)")
print(f"r=1.01r_s: dτ/dt = √(1-1/1.01) = {np.sqrt(1/1.01*0.01):.4f} (几乎冻结)")
```

### 8.2 FLRW 宇宙膨胀模拟

```python
"""
Friedmann 方程数值积分: a(t) 膨胀历史
三种宇宙: 物质主导/辐射主导/Λ主导/混合(当前宇宙)
"""
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint

def friedmann(a, t, Omega_m, Omega_r, Omega_L):
    """da/dt = a * H0 * sqrt(Omega_m/a³ + Omega_r/a⁴ + Omega_L + (1-Omega_total)/a²)"""
    if a <= 0:
        return 0
    H0 = 1.0  # 归一化
    matter = Omega_m / a**3
    rad = Omega_r / a**4
    lam = Omega_L
    curvature = (1 - Omega_m - Omega_r - Omega_L) / a**2
    H = H0 * np.sqrt(max(matter + rad + lam + curvature, 0))
    return a * H

t = np.linspace(0.01, 3.0, 1000)

# 三种宇宙模型
models = [
    ('物质主导 (Ω_m=1)', 1.0, 0.0, 0.0, 'blue'),
    ('辐射→物质→Λ (当前)', 0.31, 1e-4, 0.69, 'green'),
    ('纯Λ (de Sitter)', 0.0, 0.0, 1.0, 'red'),
    ('开放 (Ω_m=0.3)', 0.3, 0.0, 0.0, 'orange'),
]

fig, axes = plt.subplots(1, 2, figsize=(13, 5))

for label, Om, Or, OL, color in models:
    a0 = 0.01  # 初始尺度因子
    sol = odeint(friedmann, a0, t, args=(Om, Or, OL))
    a_t = sol.flatten()
    a_t[a_t < 0] = np.nan
    axes[0].plot(t, a_t, color=color, linewidth=2, label=label)

axes[0].set_xlabel('时间 t / H₀⁻¹ (≈140亿年)')
axes[0].set_ylabel('尺度因子 a(t)')
axes[0].set_title('宇宙膨胀历史 a(t)')
axes[0].axhline(1.0, color='gray', linewidth=0.5, linestyle=':')
axes[0].legend(fontsize=8); axes[0].grid(alpha=0.3)
axes[0].set_ylim(0, 3)

# (b) 各组分密度随 a 演化
a_arr = np.logspace(-6, 1, 500)
rho_rad = 1e-4 / a_arr**4     # 归一化: Ω_r = 1e-4 今天
rho_matter = 0.31 / a_arr**3
rho_lambda = 0.69 * np.ones_like(a_arr)
rho_curv = (1 - 0.31 - 1e-4 - 0.69) / a_arr**2

axes[1].loglog(a_arr, rho_rad, 'r-', linewidth=2, label='辐射 $\\propto a^{-4}$')
axes[1].loglog(a_arr, rho_matter, 'b-', linewidth=2, label='物质 $\\propto a^{-3}$')
axes[1].loglog(a_arr, np.abs(rho_curv), 'y--', linewidth=1.5, label='|曲率| $\\propto a^{-2}$')
axes[1].loglog(a_arr, rho_lambda, 'g-', linewidth=2, label='暗能量 $\\propto a^0$')

# 标注相等点
axes[1].axvline(1.0, color='gray', linestyle=':', alpha=0.5)
axes[1].fill_between(a_arr, rho_lambda, alpha=0.05, color='green')
axes[1].set_xlabel('尺度因子 a')
axes[1].set_ylabel('能量密度 Ω(a)')
axes[1].set_title('各组分密度随膨胀演化')
axes[1].legend(fontsize=9, loc='upper right'); axes[1].grid(alpha=0.3)
axes[1].set_xlim(1e-6, 10); axes[1].set_ylim(1e-8, 1e5)
axes[1].annotate('辐射=物质\na≈0.0003\n(t≈5万年)', xy=(0.0003, 0.01), fontsize=7, color='purple')
axes[1].annotate('物质=Λ\na≈0.7\n(t≈90亿年)', xy=(0.7, 0.5), fontsize=7, color='darkgreen')

plt.tight_layout()
plt.savefig('flrw_cosmology.png', dpi=110, bbox_inches='tight')
print("已保存 flrw_cosmology.png")
print("宇宙演化三阶段: 辐射→物质→暗能量")
print("当前宇宙正在加速膨胀 (ä > 0 since a ≈ 0.7)")
```

### 8.3 星系旋转曲线（暗物质证据）

```python
"""
星系旋转曲线 v(r):
- 仅可见物质 (v ∝ r^{-1/2} 外围下降)
- + 暗物质晕 NFW profile (v ∝ const 外围持平)
观测: 旋转曲线持平 → 暗物质存在的经典证据
"""
import numpy as np
import matplotlib.pyplot as plt

# 距离 (kpc)
r = np.linspace(0.5, 30, 500)

# 可见物质: 指数盘 + 核球
R_d = 3.0   # 盘标度 (kpc)
M_bulge = 5e9   # 核球质量 (M_sun)
M_disk = 5e10   # 盘质量
v_bulge = 200 * np.sqrt(M_bulge/5e9) * r / (r + 0.5)**1.5  # 核球贡献
v_disk = 220 * np.sqrt(M_disk/5e10) * (1 - np.exp(-r/R_d) * (1 + r/R_d))  # 盘贡献
v_visible = np.sqrt(v_bulge**2 + v_disk**2)

# 暗物质: NFW profile (简化为等温球 v ≈ const)
rho0_dm = 0.3  # GeV/cm³ → 归一化
r_s = 15.0     # 特征半径 (kpc)
v_dm = 180 * np.sqrt(1 - np.log(1 + r/r_s) / (r/r_s)) * np.sqrt(r / (r + 3))
v_dm = np.minimum(v_dm, 200)  # 截断
v_dm[r < 5] *= r[r < 5] / 5  # 内部线性上升

v_total = np.sqrt(v_visible**2 + v_dm**2)

fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(r, v_visible, 'b--', linewidth=2, label='仅可见物质 (开普勒下降)')
ax.plot(r, v_dm, 'r:', linewidth=2, label='暗物质晕')
ax.plot(r, v_total, 'k-', linewidth=2.5, label='可见+暗物质 (总)')

# 模拟观测数据点
r_obs = np.array([3, 5, 8, 12, 16, 20, 25, 30])
v_obs = np.array([190, 205, 210, 215, 213, 208, 210, 205])
v_err = np.array([10]*8)
ax.errorbar(r_obs, v_obs, yerr=v_err, fmt='ko', capsize=4, markersize=6, label='观测数据')

ax.set_xlabel('半径 r (kpc)')
ax.set_ylabel('旋转速度 v (km/s)')
ax.set_title('星系旋转曲线: 持平的外围速度是暗物质的经典证据')
ax.legend(fontsize=10); ax.grid(alpha=0.3)
ax.set_xlim(0, 32); ax.set_ylim(0, 260)
ax.annotate('可见物质预言:\nv ∝ r⁻¹/² (下降)', xy=(25, 100), fontsize=10, color='blue')
ax.annotate('观测: v ≈ const\n→ 暗物质', xy=(22, 215), fontsize=10, color='red')

plt.tight_layout()
plt.savefig('rotation_curve.png', dpi=110, bbox_inches='tight')
print("已保存 rotation_curve.png")
print(f"r=30 kpc: 可见物质 v={v_visible[-1]:.0f} km/s, 观测 v≈205 km/s")
print(f"→ 需要 {v_total[-1]/v_visible[-1]:.1f}x 的额外引力 = 暗物质")
```

---

## 9. 习题与解答

### 习题 1（引力红移）— GPS 修正

GPS 卫星在 $r = 26{,}560$ km 高度。求卫星钟相对地面钟的引力时间膨胀率。

**解**：

$$
\frac{d\tau_{\text{sat}}}{dt} = \sqrt{1-\frac{2GM}{c^2r_{\text{sat}}}}, \quad \frac{d\tau_{\text{ground}}}{dt} = \sqrt{1-\frac{2GM}{c^2R_\oplus}}
$$

差 $\Delta(d\tau/dt) \approx \frac{GM}{c^2}\left(\frac{1}{R_\oplus} - \frac{1}{r_{\text{sat}}}\right)$

$= \frac{3.986\times 10^{14}}{9\times 10^{16}}\left(\frac{1}{6.371\times 10^6} - \frac{1}{26.56\times 10^6}\right) = 4.43\times 10^{-3}\times 1.19\times 10^{-7} = 5.3\times 10^{-10}$

每天差 $86400\times 5.3\times 10^{-10} = 45.8$ μs（加狭义相对论运动效应 −7.2 μs → 净 +38.6 μs/天）。

### 习题 2（史瓦西半径）

求 1 太阳质量黑洞的 $r_s$。

**解**：$r_s = 2GM/c^2 = 2\times 6.674\times 10^{-11}\times 1.989\times 10^{30}/(3\times 10^8)^2 = 2.95$ km ✓。

### 习题 3（水星近日点进动）

广义相对论预测每百年进动 43"。推导进动公式。

**解**：Schwarzschild 度规中轨道方程的修正项（$r^{-3}$ 项）使椭圆缓慢进动。每圈进动：

$$
\Delta\phi = \frac{6\pi GM}{c^2 a(1-e^2)}
$$

水星 $a = 5.79\times 10^{10}$ m, $e = 0.206$：

$\Delta\phi = \frac{6\pi\times 1.327\times 10^{20}}{9\times 10^{16}\times 5.79\times 10^{10}\times 0.958} = 5.02\times 10^{-7}$ rad/圈

水星每年 ~415 圈 → $5.02\times 10^{-7}\times 415\times 100 = 2.08\times 10^{-2}$ rad/世纪 $= 4.3\times 10^{2}$"/世纪 ≈ 43" ✓。

### 习题 4（Friedmann 方程）— 平坦宇宙

$\Omega_m + \Omega_\Lambda = 1$, $k = 0$。求物质主导时期 $a(t)$。

**解**：$\dot{a}/a = H_0\sqrt{\Omega_m/a^3}$

$$
a^{1/2}da = H_0\sqrt{\Omega_m}\,dt \implies \frac{2}{3}a^{3/2} = H_0\sqrt{\Omega_m}\,t
$$

$$
a(t) = \left(\frac{3}{2}H_0\sqrt{\Omega_m}\,t\right)^{2/3} \propto t^{2/3}
$$

### 习题 5（哈勃年龄）

$H_0 = 70$ km/s/Mpc。估计宇宙年龄（平坦物质主导）。

**解**：$t_0 = 2/(3H_0)$。

$H_0^{-1} = 1/70\times 3.086\times 10^{19}$ km / (km/s) $= 4.41\times 10^{17}$ s $= 14.0$ Gyr。

$t_0 = 2/3\times 14.0 = 9.3$ Gyr（物质主导）。加暗能量修正实际 ~13.8 Gyr ✓。

### 习题 6（光度距离）

Ia 型超新星峰值光度 $L = 10^{43}$ erg/s，观测峰值流量 $F = 10^{-14}$ erg/(s·cm²)。求光度距离。

**解**：$d_L = \sqrt{L/(4\pi F)} = \sqrt{10^{43}/(4\pi\times 10^{-14})} = \sqrt{10^{57}/12.6} = 2.8\times 10^{27}$ cm $= 910$ Mpc。

$z\approx 0.2$（哈勃定律 $v = H_0 d = 70\times 910 = 63{,}700$ km/s → $z = 0.21$）。

### 习题 7（Bekenstein-Hawking 熵）

1 太阳质量黑洞的熵。

**解**：

$$
S_{\text{BH}} = \frac{k_B c^3 A}{4G\hbar}, \quad A = 4\pi r_s^2 = 4\pi(2GM/c^2)^2 = \frac{16\pi G^2M^2}{c^4}
$$

$$
S_{\text{BH}} = \frac{4\pi k_B GM^2}{\hbar c} = \frac{4\pi\times 6.674\times 10^{-11}\times (1.989\times 10^{30})^2}{1.055\times 10^{-34}\times 3\times 10^8} k_B \approx 1.05\times 10^{77}\,k_B
$$

→ 比太阳热力学熵（$\sim 10^{58}k_B$）大 $10^{19}$ 倍！黑洞是宇宙中已知最大熵的物体。

### 习题 8（Hawking 温度与寿命）

太阳质量黑洞的 Hawking 温度和蒸发时间。

**解**：

$$
T_H = \frac{\hbar c^3}{8\pi GMk_B} = \frac{1.055\times 10^{-34}\times 2.7\times 10^{25}}{8\pi\times 6.674\times 10^{-11}\times 1.989\times 10^{30}\times 1.381\times 10^{-23}}
$$

$T_H\approx 6.2\times 10^{-8}$ K（远低于 CMB 2.7 K）。

蒸发时间 $\tau \sim 5120\pi G^2M^3/(\hbar c^4) \approx 10^{67}$ 年（远超宇宙年龄 $1.38\times 10^{10}$ 年）。

---

## 10. 反直觉发现

### 10.1 引力是最弱的力

两个电子之间的引力/电磁力比：$Gm_e^2/(e^2/4\pi\epsilon_0) = 4\pi\epsilon_0 Gm_e^2/e^2 \approx 2.4\times 10^{-43}$。

→ 引力比电磁力弱 $10^{43}$ 倍。但引力在天文尺度主导——因为它只有同号（无屏蔽），叠加到宏观量。

### 10.2 时间不是绝对的

牛顿假设时间对一切观察者相同。广义相对论粉碎了这一点：
- 不同引力势处时钟快慢不同（引力红移）。
- 加速参考系中时钟快慢不同（双生子佯谬）。
- 黑洞视界附近时钟几乎冻结（无限红移）。

GPS 必须同时修正引力红移和狭义相对论运动效应——否则每天累积 10 km 误差。

### 10.3 宇宙在加速膨胀

1998 年前的共识：宇宙膨胀在减速（引力拖拽）。超新星观测颠覆了这一点：遥远超新星比预期暗→比预期远→**膨胀在加速**。

这意味着存在一种推动空间本身膨胀的"负压"能量——**暗能量**，占宇宙能量的 69%。它的本质完全未知。

### 10.4 黑洞不是黑的

Hawking（1974）用量子场论在弯曲时空中的效应证明：黑洞会因量子涨落**辐射**（热辐射），温度 $T_H \propto 1/M$。

→ 黑洞会慢慢蒸发。太阳质量黑洞的蒸发时间 $10^{67}$ 年——宇宙寿命的 $10^{57}$ 倍。但原理深刻：量子力学 + 引力 = 黑洞辐射，这是量子引力的第一个线索。

### 10.5 暗物质：85% 的物质看不见

所有可见物质（恒星、星系、气体）只占宇宙物质的 ~15%。其余 85% 是暗物质——我们只知道它有引力、不发光、几乎不碰撞。子弹星系团直接展示了暗物质和普通物质在碰撞中分离。

→ 我们对宇宙 85% 的物质组成一无所知。

---

## 11. 不足与延伸

| 本主题局限 | 延伸方向 | 课程 |
|-----------|---------|------|
| 经典广义相对论 | 量子引力（弦论 / 圈量子引力） | 8.821 / 8.831 |
| 施瓦茨席尔德黑洞 | Kerr 旋转黑洞、黑洞微扰、准正模 | 8.962 续 |
| 微扰宇宙学 | 非线性结构形成、数值宇宙学 | 8.901 / 8.286 续 |
| $\Lambda$CDM 标准模型 | 暗能量本质、修改引力、暴胀模型 | 8.286 续 |
| 经典 CMB | 原初引力波、CMB 光谱畸变 | 8.302 |
| 不含规范引力 | 全息原理、AdS/CFT、黑洞信息悖论 | 8.831 |

**学习路径**：8.962（Carroll GR 基础）→ 8.286（Dodelson 宇宙学）→ 8.901（天体物理）→ 8.821/8.831（弦论 / 量子引力）。

---

**参考**：
- Carroll《Spacetime and Geometry》Ch 2-4 (微分几何/Einstein方程), Ch 5 (Schwarzschild), Ch 6 (黑洞), Ch 7 (FLRW), Ch 8 (引力波)
- Dodelson & Schmidt《Modern Cosmology》2ed, Ch 3-4 (FLRW), Ch 5-6 (CMB), Ch 7-8 (结构形成)
- Weinberg《Gravitation and Cosmology》— 经典参考
- Schutz《A First Course in General Relativity》— 入门友好
- Ryden《Introduction to Cosmology》2ed — 本科宇宙学
- MIT OCW 8.962 (Faraoni) / 8.286 (Kaiser) / 8.901 (Schechter)

---

## 🎯 费曼式入口（白话版）

> **一句话解释**：广义相对论是爱因斯坦对引力的终极理解——引力不是"力"，而是**时空的弯曲**。想象一张蹦床（时空），上面放一个保龄球（恒星），蹦床凹陷下去。一个弹珠（行星）滚过时会沿着凹陷的边缘转圈——这就是"引力"。物质告诉时空怎么弯曲，弯曲的时空告诉物质怎么运动。
>
> **生活类比**：
> - 时空弯曲 ≈ 蹦床上的保龄球：质量越大凹陷越深
> - 引力红移 ≈ 爬楼梯上发出的光越往上越"累"（频率降低）——光子克服引力势损失能量
> - 黑洞 ≈ 蹦床上球太重把布戳穿了——时空被无限拉伸的"洞"，进去就出不来
> - 引力波 ≈ 在蹦床上跳动产生的涟漪——两个黑洞旋转合并时，时空本身在振荡
> - 宇宙膨胀 ≈ 在气球上画点然后吹气球：点之间的距离都在增大，但点本身没动（是空间在膨胀）
> - 引力时间膨胀 ≈ 在山顶的时钟比海平面的时钟快——引力越强时间越慢（GPS 必须校正！）
>
> **反直觉发现**：你以为引力是物体之间的吸引力（像磁铁）？不！爱因斯坦说：**引力不存在**。物体只是在弯曲的时空中走"直线"（测地线）——我们误把这种几何效应叫"引力"。更反直觉的是：**时间不是绝对的**。在黑洞附近，时间流逝会变慢到一个黑洞观察者看来你永远在"冻结"在视界上。而宇宙正在**加速膨胀**——暗能量推动的，我们至今不知道暗能量是什么。最震撼的是：两个黑洞合并时产生的引力波，让整个地球在一个方向上膨胀 $10^{-21}$ 米（质子大小的千分之一）后恢复——LIGO 测到了这个信号（2015 年 9 月 14 日），人类第一次"听"到了时空的涟漪。

---

## 🔗 衔接：这个主题从哪来，到哪去

### 前置知识
- **Topic 01 经典力学**：最小作用量原理（爱因斯坦-希尔伯特作用量）、能量/动量守恒
- **Topic 02 电磁学**：洛伦兹力、电磁波在弯曲时空中的传播
- **Topic 05 数学方法**：张量分析（度规张量 $g_{\mu\nu}$、黎曼曲率张量 $R^\rho_{\sigma\mu\nu}$）、微分几何（流形、联络、测地线）

### 本主题解决了什么危机
- **牛顿引力的超距作用之谜**：牛顿自己写道："一个物体可以不通过任何介质、跨越真空作用于另一个物体，这对我来说是极大的荒谬。" 引力如何瞬间传播？爱因斯坦（1915）回答：引力不是瞬间作用的，它通过时空几何以光速传播——引力波就是时空扰动的传播。
- **水星近日点进动（1859-1915）**：勒维耶发现水星轨道每世纪有 43 角秒的进动无法用牛顿引力解释。56 年的困惑！爱因斯坦的广义相对论完美预言了这 43 角秒——这是他"心悸了几天"的伟大时刻。
- **狭义相对论与引力的矛盾**：狭义相对论说"所有惯性系等价"，但引力使得自由下落的参考系局域地消除了引力（等效原理）——这暗示引力是时空几何。
- **宇宙学问题**：牛顿引力下的宇宙要么有限（边缘在哪？）要么无限（星光叠加天空应该全亮——奥尔勃斯佯谬）。广义相对论给出了有限无界的宇宙模型（FLRW 度规）。

### 本主题留下的新危机
- **奇点问题**：广义相对论预言在黑洞中心（$r=0$）和宇宙大爆炸（$t=0$）存在物理量发散的奇点。物理量无穷大意味着理论在那里失效 → 需要**量子引力**。
- **暗物质（1933-至今）**：兹威基观测到星系团的速度远超可见物质能提供的引力 → 85% 的物质不可见。是什么？WIMPs？轴子？修改引力（MOND）？60 多年未解。
- **暗能量（1998-至今）**：超新星观测发现宇宙在**加速**膨胀 → 需要一种压强为负的能量（暗能量）占宇宙 68%。是宇宙学常数？标量场？还是广义相对论在大尺度上需要修改？
- **哈勃张力（2013-至今）**：用早期宇宙（CMB）推算的哈勃常数 $H_0 \approx 67$ km/s/Mpc，与晚期宇宙（造父变星/超新星）测量的 $H_0 \approx 73$ 不一致——5σ 偏差！可能暗示新物理。
- **黑洞信息悖论**：霍金辐射（1974）是热辐射——不携带掉入黑洞的信息。如果黑洞最终蒸发，信息去哪了？量子力学说不信息可以消失，广义相对论说可以。这个矛盾至今是理论物理最深层的危机。

### 后续主题
- **量子引力**：弦论（自然界基本实体是弦而非点粒子）、圈量子引力（时空本身是量子化的）
- **全息原理 / AdS-CFT 对偶**：引力理论可以等价于低维无引力量子场论——可能是理解量子引力的关键
- **宇宙学前沿**：原初引力波（暴胀的证据）、暗能量本质、大尺度结构形成

---

## 🏭 理论联系实际：5 个工业/生活应用

1. **GPS 卫星导航（最精确的日常 GR 应用）**：卫星在 2 万公里高度，引力比地面弱 → 时钟每天快 45 μs（广义相对论效应）；卫星以 4 km/s 运动 → 时钟每天慢 7 μs（狭义相对论效应）。净效应：快 38 μs/天 = 光速 × 38 μs ≈ 11.4 km/天。不做校正 GPS 在几分钟内就失效。
   - 实例：你手机里的 GPS 导航，每一秒都在验证爱因斯坦

2. **引力波天文学（LIGO/Virgo/KAGRA）**：2015 年首次直接探测到引力波（GW150914，两个 30 倍太阳质量黑洞合并）。引力波打开了观测宇宙的全新窗口——不再只"看"光，还能"听"时空的振动。
   - 实例：LIGO（美国，4km 臂长激光干涉仪）；中国"天琴计划"（太空引力波探测）；LISA（ESA/NASA 太空引力波天线，2030s 发射）

3. **黑洞成像**：2019 年事件视界望远镜（EHT）首次拍到 M87* 黑洞照片——一个发光的"甜甜圈"环绕黑暗的中心。2022 年拍到银河系中心黑洞 Sgr A*。这直接验证了广义相对论对极端时空的预言。
   - 实例：EHT（全球 8 个射电望远镜组成地球大小的虚拟望远镜）

4. **精确宇宙学——暗能量探测**：通过 Ia 型超新星、重子声学振荡（BAO）、弱引力透测三个"探针"精确测量暗能量状态方程 $w = p/\rho$。未来的 LSST（薇拉·鲁宾天文台）和欧几里得卫星将把暗能量测量精度提升到 1%。
   - 实例：ESA 欧几里得空间望远镜（2023 年发射，绘制 15 亿星系的三维分布图）

5. **相对论性效应在粒子加速器中**：在 LHC 中质子被加速到 7 TeV（$\gamma \approx 7500$），其相对论质量是静止质量的 7500 倍。同步辐射（高速带电粒子在磁场中辐射）是相对论效应的直接工程后果，被用于产生超亮 X 射线。
   - 实例：LHC 磁铁需要超导以约束高能粒子束；同步辐射光源（如上海 SSRF）用于蛋白质结构解析

---

## 🔬 最新研究前沿（2024-2026）

> 基于 Nature 系列期刊搜索的真实结果

### 真空双折射——磁星验证量子电动力学在极端引力场中的预言
- **发现**：对磁星（magnetar）1E 1547.0−5408 的 X 射线偏振测量提供了真空双折射的强有力证据——在超强磁场（$10^{14}$-$10^{15}$ Gauss）中，真空本身（空无一物的空间）能像水晶一样偏振光。这是广义相对论天体物理环境对 QED 预言的直接验证。
- **来源**：Stewart, R.E. et al. "Vacuum birefringence and the polarized X-ray emission from a radio magnetar" *Nature* (2026)
- **日期**：2026 年 8 月
- **为什么重要**：首次在极端天体物理环境中观测到真空极化——验证了 QED 在超强场下的预言，也展示了极端引力场中的电磁辐射

### 原初潮汐扭矩印记的高显著性探测
- **发现**：将星系运动学与原初密度场重建结合，成功探测到原初潮汐扭矩在当今星系自转中的大量印记——强化了"星系角动量起源于极早期大尺度潮汐力"的证据。
- **来源**：Sheng, M.-J. et al. *Nature Astronomy* (2026)
- **日期**：2026 年 8 月
- **为什么重要**：连接了宇宙学微扰论（早期宇宙）与观测天文学（当今星系）——验证了结构形成的引力理论

### 凯尔文-亥姆霍兹不稳定性驱动太阳等离子体混合
- **发现**：高空间分辨率的太阳光球层观测揭示了远比之前认知更复杂和动态的太阳场景——无处不在的凯尔文-亥姆霍兹不稳定性驱动太阳上的等离子体混合。
- **来源**：Kuridze, D. et al. *Nature* (2026)
- **日期**：2026 年 8 月
- **为什么重要**：磁流体力学（MHD = 广义相对论的等离子体物理延伸）在太阳物理中的直接应用——影响太阳耀斑和日冕物质抛射的预测

### 银河系外盘的波纹——宇宙学度规的局部检验
- **发现**：利用超过 3 万个分子云，揭示了银河系外分子盘上叠加在弯曲之上的广泛波纹——为银河系的三维结构和动力学提供了新洞见。
- **来源**：Sun, Y. et al. *Nature Astronomy* (2026)
- **日期**：2026 年 8 月
- **为什么重要**：银河系结构的研究直接检验了引力理论在星系尺度上的适用性——波纹可能是暗物质子结构的信号

### 原恒星外流揭示环向磁场
- **发现**：首次在数百天文单位尺度上直接观测到毫高斯级的环向磁场——它正在准直一颗原恒星的外流。这是天体物理磁场在恒星形成中作用的关键观测证据。
- **来源**：Ching, T.-C. et al. *Nature Communications* **17**, 7616 (2026)
- **日期**：2026 年 8 月
- **为什么重要**：磁流体力学（引力 + 电磁力 + 等离子体）在恒星形成中的核心作用——直接影响行星系统和生命起源的理论

---

## 🗺️ 学习 Roadmap（MIT 路径）

### 🎓 入门（2-3 周）
- 📖 读： Schutz《A First Course in General Relativity》Ch 1-4（等效原理 + 张量分析 + 测地线）
- 🎥 看：MIT OCW **8.962**（General Relativity）
  - 重点视频：等效原理、施瓦茨席尔德解、引力红移
- ✍️ 做：
  - 推导施瓦茨席尔德度规的外部解
  - 运行 `physics_demos.py` 的 `gr_cosmology()` demo 观察时空弯曲和引力波

### 🏗️ 进阶（4-6 周）
- 📖 读：Carroll《Spacetime and Geometry》Ch 5-8（施瓦茨席尔德 + 黑洞 + FLRW + 引力波）
- 💻 做：
  - 用 Python 数值积分测地线方程，画光子绕黑洞的轨迹
  - 模拟 FLRW 宇宙的膨胀（不同 $\Omega_m, \Omega_\Lambda$ 组合）
- 🧪 实验：MIT LIGO 实验室参观；分析公开的引力波数据（GWOSC）

### 🔬 深造（持续）
- 📄 读：
  - Weinberg《Gravitation and Cosmology》——经典权威
  - Dodelson & Schmidt《Modern Cosmology》2ed——宇宙学标准教材
  - Poisson & Will《Gravity: Newtonian, Post-Newtonian, Relativistic》——引力波理论
  - arXiv: gr-qc / astro-ph.CO 板块
- 🛠️ 项目：用 Einstein Toolkit（数值相对论软件）模拟双黑洞合并的引力波波形

### ✅ 知识检查
- [ ] 能解释等效原理的三种表述（弱/爱因斯坦/强）及其区别
- [ ] 能写出爱因斯坦场方程 $G_{\mu\nu} + \Lambda g_{\mu\nu} = \frac{8\pi G}{c^4}T_{\mu\nu}$ 并解释每一项的物理含义
- [ ] 能推导施瓦茨席尔德半径 $r_s = 2GM/c^2$ 并解释为什么光是逃不出黑洞的
- [ ] 能解释哈勃定律 $v = H_0 d$ 和宇宙加速膨胀的证据
- [ ] 理解哈勃张力（$H_0 \approx 67$ vs $73$ km/s/Mpc）为什么可能是新物理的信号
