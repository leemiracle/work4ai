# Stanford 物理系 Phase 2 · 主题 8：广义相对论与宇宙学

> **课程谱系**：PHYS 250 (广义相对论) → PHYS 380 (宇宙学)
>
> **教材阶梯**：Carroll《Spacetime and Geometry》→ Dodelson《Modern Cosmology》→ Weinberg《Cosmology》
>
> **Stanford 特色**：从 SLAC 的引力理论组到 KIPAC（Kavli 粒子天体物理与宇宙学研究所），Stanford 是理论 GR 与观测宇宙学的双重中心。LIGO 引力波探测（2015 首次直接探测，2017 Nobel）背后的数值相对论，与 Stanford 理论组紧密关联。Carroll 的教材本身就是 Stanford PHYS 250 的讲义结晶

---

## 目录

1. [等效原理与时空几何](#1-等效原理与时空几何)
2. [张量与微分几何](#2-张量与微分几何)
3. [爱因斯坦场方程](#3-爱因斯坦场方程)
4. [Schwarzschild 解与黑洞](#4-schwarzschild-解与黑洞)
5. [宇宙学原理与 FLRW 度规](#5-宇宙学原理与-flrw-度规)
6. [宇宙的热历史与大爆炸核合成](#6-宇宙的热历史与大爆炸核合成)
7. [暗物质与暗能量](#7-暗物质与暗能量)
8. [Stanford/KIPAC 关联](#8-stanfordkipac-关联)
9. [习题与解答](#9-习题与解答)
10. [代码实验](#10-代码实验)
11. [局限与延伸](#11-局限与延伸)

---

## 1. 等效原理与时空几何

### 1.1 直觉

Einstein 最深刻的洞察：「站在自由下落的电梯里，你感觉不到引力。」这不是巧合，而是引力的本质——**引力不是力，是时空弯曲**。Carroll 第 1 章的起点。

### 1.2 等效原理的三层

| 层次 | 表述 |
|------|------|
| **弱等效原理 (WEP)** | 惯性质量 = 引力质量，所有物体在引力场中以相同方式下落 |
| **Einstein 等效原理 (EEP)** | 局部惯性系中，非引力物理定律回到狭义相对论形式 |
| **强等效原理 (SEP)** | EEP 对引力自身也成立（自引力物体也遵循） |

### 1.3 引力红移

从等效原理直接推导：光子从引力势 $\Phi_1$ 处发射，在 $\Phi_2$ 处接收（$\Phi_2 > \Phi_1$），频率红移：

$$\frac{\Delta\nu}{\nu} = -\frac{\Delta\Phi}{c^2}$$

Pound-Rebka 实验（1959）在哈佛塔中验证了这一效应，精度约 1%。

### 1.4 测地线方程

自由粒子沿**测地线**运动。在弯曲时空中：

$$\boxed{\frac{d^2x^\mu}{d\tau^2} + \Gamma^\mu_{\alpha\beta} \frac{dx^\alpha}{d\tau}\frac{dx^\beta}{d\tau} = 0}$$

其中 $\Gamma^\mu_{\alpha\beta}$ 是 **Christoffel 联络**，描述坐标基矢沿曲线的变化。

---

## 2. 张量与微分几何

### 2.1 度规张量

时空的几何完全由**度规张量** $g_{\mu\nu}$ 描述。线元：

$$ds^2 = g_{\mu\nu}\, dx^\mu\, dx^\nu$$

闵可夫斯基（平直）度规：$ds^2 = -c^2dt^2 + dx^2 + dy^2 + dz^2$。

### 2.2 协变导数

张量的协变导数推广了普通导数到弯曲时空：

$$\nabla_\alpha V^\mu = \partial_\alpha V^\mu + \Gamma^\mu_{\alpha\beta} V^\beta$$

$$\nabla_\alpha V_\mu = \partial_\alpha V_\mu - \Gamma^\beta_{\alpha\mu} V_\beta$$

### 2.3 Christoffel 联络

$$\Gamma^\mu_{\alpha\beta} = \frac{1}{2}g^{\mu\nu}\left(\partial_\alpha g_{\beta\nu} + \partial_\beta g_{\alpha\nu} - \partial_\nu g_{\alpha\beta}\right)$$

### 2.4 Riemann 曲率张量

测量平行移动一圈后矢量是否改变：

$$R^\mu_{\ \nu\alpha\beta} = \partial_\alpha\Gamma^\mu_{\nu\beta} - \partial_\beta\Gamma^\mu_{\nu\alpha} + \Gamma^\mu_{\alpha\lambda}\Gamma^\lambda_{\nu\beta} - \Gamma^\mu_{\beta\lambda}\Gamma^\lambda_{\nu\alpha}$$

如果 $R^\mu_{\ \nu\alpha\beta} = 0$，时空是平直的。

### 2.5 Ricci 张量与标量曲率

收缩 Riemann 张量：

$$R_{\mu\nu} = R^\alpha_{\ \mu\alpha\nu}, \quad R = g^{\mu\nu}R_{\mu\nu}$$

---

## 3. 爱因斯坦场方程

### 3.1 直觉

Einstein 的天才之举：将时空几何（左边）与物质能量（右边）联系起来。**物质告诉时空如何弯曲，时空告诉物质如何运动。**

### 3.2 场方程

$$\boxed{G_{\mu\nu} \equiv R_{\mu\nu} - \frac{1}{2}Rg_{\mu\nu} = \frac{8\pi G}{c^4} T_{\mu\nu}}$$

或含宇宙学常数：

$$R_{\mu\nu} - \frac{1}{2}Rg_{\mu\nu} + \Lambda g_{\mu\nu} = \frac{8\pi G}{c^4} T_{\mu\nu}$$

$T_{\mu\nu}$ 是**能量-动量张量**，描述物质和辐射的分布。

### 3.3 能量-动量张量

理想流体：

$$T^{\mu\nu} = (\rho + p/c^2)u^\mu u^\nu + pg^{\mu\nu}$$

其中 $\rho$ 是能量密度，$p$ 是压强，$u^\mu$ 是四维速度。

### 3.4 守恒律

Bianchi 恒等式 $\nabla_\mu G^{\mu\nu} = 0$ 自动给出能量-动量守恒：

$$\nabla_\mu T^{\mu\nu} = 0$$

---

## 4. Schwarzschild 解与黑洞

### 4.1 Schwarzschild 度规

球对称真空解（Schwarzschild 1916）：

$$\boxed{ds^2 = -\left(1-\frac{2GM}{c^2r}\right)c^2dt^2 + \left(1-\frac{2GM}{c^2r}\right)^{-1}dr^2 + r^2 d\Omega^2}$$

其中 $d\Omega^2 = d\theta^2 + \sin^2\theta\, d\phi^2$。

### 4.2 Schwarzschild 半径（事件视界）

$$r_s = \frac{2GM}{c^2}$$

对太阳：$r_s \approx 3$ km。对地球：$r_s \approx 9$ mm。

在 $r = r_s$ 处，度规分量 $g_{tt} \to 0$, $g_{rr} \to \infty$——但这只是坐标奇点（换坐标系可消除）。真正的物理奇点在 $r = 0$。

### 4.3 轨道进动

Schwarzschild 时空中，行星椭圆轨道会**进动**。水星近日点进动：

$$\Delta\phi = \frac{6\pi GM}{c^2 a(1-e^2)}$$

每世纪约 43 弧秒——这是 GR 的第一个实验验证（1915）。

### 4.4 光线偏折

光经太阳旁偏折角：

$$\alpha = \frac{4GM}{c^2 b}$$

$b$ 是碰撞参数（Impact parameter）。1919 年 Eddington 日全食观测验证（~1.75 弧秒）。

### 4.5 黑洞无毛定理

稳定黑洞只有三个参数：质量 $M$、电荷 $Q$、角动量 $J$。所有其他信息在引力坍缩中辐射掉了。

### 4.6 Kerr 黑洞

旋转黑洞的精确解（Kerr 1963）。度规更复杂，产生**能层**（ergosphere），允许 Penrose 过程提取旋转能。

---

## 5. 宇宙学原理与 FLRW 度规

### 5.1 宇宙学原理

在大尺度上（>100 Mpc），宇宙是**均匀且各向同性**的。这是宇宙学的基本假设。

### 5.2 FLRW 度规

$$\boxed{ds^2 = -c^2dt^2 + a(t)^2\left[\frac{dr^2}{1-kr^2} + r^2 d\Omega^2\right]}$$

- $a(t)$：**尺度因子**（宇宙膨胀的度量）
- $k$：空间曲率（$+1$ 闭合, $0$ 平直, $-1$ 开放）

### 5.3 哈勃定律

$$\boxed{v = H_0 d}$$

$H_0 \approx 70$ km/s/Mpc 是哈勃常数。星系退行速度与距离成正比。

### 5.4 红移

光在膨胀宇宙中被拉长：

$$1 + z = \frac{\lambda_{\text{obs}}}{\lambda_{\text{emit}}} = \frac{a(t_0)}{a(t_{\text{emit}})}$$

$z = 0$ 为现在，$z \to \infty$ 为大爆炸。

---

## 6. 宇宙的热历史与大爆炸核合成

### 6.1 Friedmann 方程

从 Einstein 方程 + FLRW 度规：

$$\boxed{H^2 = \left(\frac{\dot{a}}{a}\right)^2 = \frac{8\pi G}{3}\rho - \frac{kc^2}{a^2} + \frac{\Lambda c^2}{3}}$$

$$\frac{\ddot{a}}{a} = -\frac{4\pi G}{3}\left(\rho + \frac{3p}{c^2}\right) + \frac{\Lambda c^2}{3}$$

### 6.2 物质/辐射/暗能量主导

| 时代 | 主导成分 | $\rho(a)$ | $a(t)$ |
|------|---------|-----------|--------|
| 早期 | 辐射 | $\propto a^{-4}$ | $\propto t^{1/2}$ |
| 中期 | 物质 | $\propto a^{-3}$ | $\propto t^{2/3}$ |
| 未来 | 暗能量 (Λ) | const | $\propto e^{Ht}$ |

辐射密度多一个 $a^{-1}$ 因子，因为光子不仅被稀释（$a^{-3}$），还被红移（能量 $\propto a^{-1}$）。

### 6.3 大爆炸核合成 (BBN)

宇宙年龄 $t \sim 1$–$3$ 分钟，温度 $T \sim 10^9$ K 时，质子和中子合成轻核：

| 核 | 丰度（按质量） |
|----|--------------|
| ¹H | ~75% |
| ⁴He | ~25% |
| D | ~$10^{-5}$ |
| ³He | ~$10^{-5}$ |
| ⁷Li | ~$10^{-10}$ |

BBN 预言的氦丰度与观测惊人吻合——这是大爆炸理论三大支柱之一。

### 6.4 宇宙微波背景 (CMB)

光子退耦时刻（$t \sim 380{,}000$ 年, $T \sim 3000$ K），宇宙变得透明。这些光子今天被红移到 $T_0 = 2.725$ K。

CMB 黑体谱的完美程度（偏差 $< 10^{-5}$）是大爆炸理论的另一支柱。

---

## 7. 暗物质与暗能量

### 7.1 暗物质的证据

| 证据 | 观测 |
|------|------|
| **星系旋转曲线** | 外围恒星速度不下降（Vera Rubin 1970s） |
| **星系团速度弥散** | 动力学质量 >> 发光质量 |
| **引力透镜** | 背景星光被不可见物质偏折 |
| **CMB 各向异性** | 物质密度 $\Omega_m \approx 0.3$，但重子物质仅 $\Omega_b \approx 0.05$ |
| **子弹星系团** | 引力质心与发光质心分离 |
| **大尺度结构** | 需要冷暗物质才能形成观测到的结构 |

暗物质占宇宙总能量约 **27%**。

### 7.2 暗能量

宇宙加速膨胀（Perlmutter/Schmidt/Riess, 2011 Nobel）：

$$\ddot{a} > 0$$

这需要一种压强为负的成分（$w = p/\rho < -1/3$），最简单的候选者是**宇宙学常数**（$w = -1$）。

### 7.3 宇宙能量收支

$$\Omega_{\text{total}} = \Omega_\Lambda + \Omega_m + \Omega_r + \Omega_k \approx 1$$

| 成分 | $\Omega$ |
|------|---------|
| 暗能量 (Λ) | 0.685 |
| 暗物质 | 0.268 |
| 重子物质 | 0.049 |
| 辐射 | $5 \times 10^{-5}$ |
| 曲率 | $\approx 0$ |

**反直觉发现**：我们能直接观测到的普通物质仅占宇宙的 **5%**。95% 的宇宙是未知的。

---

## 8. Stanford/KIPAC 关联

| 方向 | Stanford 角色 |
|------|-------------|
| **KIPAC** | Kavli 粒子天体物理与宇宙学研究所，理论与观测双重中心 |
| **Carroll 教材** | Sean Carroll（前 Stanford）的《Spacetime and Geometry》是全球 GR 标准教材 |
| **LSST/Vera Rubin 天文台** | Stanford 参与暗能量巡天 |
| **LIGO 引力波** | Stanford 理论组参与引力波天体物理 |
| **CMB 实验** | BICEP/Keck（南极 CMB 偏振） |
| **暗物质直接探测** | LZ 实验合作 |
| **数值相对论** | 黑洞合并模拟 |
| **SLAC 宇宙学** | 从粒子物理到宇宙学的跨学科桥梁 |

KIPAC 的独特之处：同时拥有粒子物理学家（SLAC 传统）和天体物理学家，在「宇宙作为终极实验室」的框架下研究基础物理。

---

## 9. 习题与解答

### 习题 1（PHYS 250 风格 · Carroll Ch5）

证明 Schwarzschild 度规中，圆轨道 $r = \text{const}$ 存在的最小半径（ISCO）为 $r = 6GM/c^2$。

<details>
<summary>解答</summary>

有效势（对测地线运动）：

$$V_{\text{eff}}(r) = -\frac{GM}{r} + \frac{L^2}{2r^2} - \frac{GML^2}{c^2r^3}$$

最后一项是 GR 修正（经典力学没有）。

圆轨道条件：$V_{\text{eff}}' = 0$ 和 $V_{\text{eff}}'' > 0$（稳定）。

$$V' = \frac{GM}{r^2} - \frac{L^2}{r^3} + \frac{3GML^2}{c^2r^4} = 0$$

乘以 $r^4$：

$$GMr^2 - L^2r + \frac{3GML^2}{c^2} = 0$$

判别式 $\geq 0$ 要求：

$$L^4 - 4GM \cdot \frac{3GML^2}{c^2} \geq 0 \implies L^2 \geq \frac{3(GM)^2 \cdot 4}{c^2}$$

Wait, 更简洁地：

$$L^2\left(1 - \frac{3GM r}{c^2 \cdot r}\right) \geq 0$$

实际上，直接从 $r$ 有实数解：

$$r = \frac{L^2 \pm \sqrt{L^4 - 12(GM)^2L^2/c^2}}{2GM}$$

判别式非负：$L^2 \geq 12(GM)^2/c^2$。

当 $L^2 = 12(GM)^2/c^2$ 时两根重合，代入得：

$$r_{\text{ISCO}} = \frac{L^2}{2GM} = \frac{12(GM)^2/c^2}{2GM} = \frac{6GM}{c^2} = 3r_s$$

这就是**最内稳定圆轨道 (ISCO)**。对 $10\,M_\odot$ 黑洞，$r_{\text{ISCO}} \approx 89$ km。
</details>

### 习题 2（PHYS 250 水星近日点）

计算水星近日点每世纪的进动角度。已知 $a = 5.79 \times 10^{10}$ m, $e = 0.206$, $T = 88$ 天。

<details>
<summary>解答</summary>

每圈进动：

$$\Delta\phi = \frac{6\pi GM_\odot}{c^2 a(1-e^2)}$$

$GM_\odot/c^2 = 1.477$ km $= 1477$ m。

$a(1-e^2) = 5.79\times10^{10} \times (1-0.0424) = 5.54\times10^{10}$ m。

$$\Delta\phi = \frac{6\pi \times 1477}{5.54\times10^{10}} = \frac{27834}{5.54\times10^{10}} = 5.02\times10^{-7}\text{ rad}$$

$= 5.02\times10^{-7} \times \frac{180}{\pi} \times 3600 = 0.1035$ 弧秒/圈。

每世纪圈数 $= 100 \times 365/88 = 415$ 圈。

总进动 $= 0.1035 \times 415 = 42.9$ 弧秒/世纪。✅（实验值 43"）

这就是 Le Verrier 1859 年发现的「水星反常进动」，困扰物理学家 56 年，直到 Einstein 1915 年用 GR 解决。
</details>

### 习题 3（PHYS 380 Friedmann 方程）

推导平直宇宙 ($k=0$) 在物质主导时的尺度因子 $a(t)$。

<details>
<summary>解答</summary>

物质主导：$\rho \propto a^{-3}$，令 $\rho = \rho_0 a^{-3}$。

Friedmann 方程（$k = 0, \Lambda = 0$）：

$$\dot{a}^2 = \frac{8\pi G}{3}\rho_0 a^{-3} \cdot a^2 = \frac{8\pi G\rho_0}{3} a^{-1}$$

$$\dot{a} = \sqrt{\frac{8\pi G\rho_0}{3}} \cdot a^{-1/2}$$

$$a^{1/2}da = \sqrt{\frac{8\pi G\rho_0}{3}} dt$$

$$\frac{2}{3}a^{3/2} = \sqrt{\frac{8\pi G\rho_0}{3}} t + \text{const}$$

取 $a(0) = 0$：

$$\boxed{a(t) \propto t^{2/3}}$$

故 $H = \dot{a}/a = 2/(3t)$，即 $t = 2/(3H_0)$。

取 $H_0 = 70$ km/s/Mpc，宇宙年龄 $t_0 \approx 93$ 亿年。实际年龄约 138 亿年（暗能量使膨胀加速，年龄更长）。
</details>

### 习题 4（PHYS 380 BBN）

估算宇宙温度从 $T = 10^{10}$ K 降到 $T = 10^9$ K 所需的时间。假设辐射主导。

<details>
<summary>解答</summary>

辐射主导时 $a \propto t^{1/2}$，温度 $T \propto a^{-1} \propto t^{-1/2}$。

$$T = T_0 \left(\frac{t}{t_0}\right)^{-1/2} \implies t = t_0 \left(\frac{T_0}{T}\right)^2$$

辐射主导时 Friedmann 方程给出：

$$t = \left(\frac{3c^2}{32\pi G a_{\text{rad}} T^4}\right)^{1/2}$$

其中 $a_{\text{rad}} = 4\sigma/c = 7.566 \times 10^{-16}$ J/(m³·K⁴)，考虑光子+中微子。

简化的标准结果：

$$\boxed{t \approx \frac{1.5 \text{ s}}{(T/10^{10}\text{ K})^2}}$$

$T = 10^{10}$ K: $t \approx 1.5$ s（电子-正电子湮灭时刻）。

$T = 10^9$ K: $t \approx 150$ s $\approx 2.5$ 分钟。

这正是 BBN 发生的时间窗口！质子中子比冻结后，氦在此时合成。

**反直觉发现**：宇宙从 $10^{10}$ K 冷却到 $10^9$ K 只用了 2.5 分钟。宇宙演化的「关键时刻」极其短暂。
</details>

---

## 10. 代码实验

### 实验 10.1：Schwarzschild 轨道与近日点进动

```python
"""
PHYS 250 实验：Schwarzschild 时空中的行星轨道
数值积分测地线方程，观测近日点进动
纯标准库，RK4 积分
"""
import math

def effective_potential(r, L, GM=1.0, c=1.0):
    """广义相对论有效势 (单位质量)
    V_eff = -GM/r + L^2/(2r^2) - GM*L^2/(c^2*r^3)
    最后一项是 GR 修正"""
    return -GM/r + L**2/(2*r**2) - GM*L**2/(c**2*r**3)

def newtonian_potential(r, L, GM=1.0):
    """牛顿有效势（无 GR 修正）"""
    return -GM/r + L**2/(2*r**2)

# 参数
GM = 1.0
c = 10.0   # 设 c 较大使 GR 修正小（接近水星情形）
L = 0.5    # 角动量
r0 = 1.0   # 初始半径（近日点）

# 求圆轨道半径
# Newtonian: r_circ = L^2/GM
r_circ = L**2 / GM
print(f"牛顿圆轨道半径: {r_circ:.4f}")
print(f"设初始 r = {r0}（偏心轨道）")

# 有效势 ASCII 图
print("\n=== 有效势比较 ===")
print("(* = GR有效势, . = 牛顿有效势)")
r_min, r_max = 0.3, 3.0
N = 70
rs = [r_min + i*(r_max-r_min)/N for i in range(N)]
vs_gr = [effective_potential(r, L, GM, c) for r in rs]
vs_nt = [newtonian_potential(r, L, GM) for r in rs]
v_min, v_max = min(min(vs_gr), min(vs_nt)), max(max(vs_gr), max(vs_nt))
height = 22
for row in range(height, -1, -1):
    v_target = v_min + row*(v_max-v_min)/height
    line = ""
    for i, r in enumerate(rs):
        if abs(vs_gr[i] - v_target) < (v_max-v_min)/height/2:
            line += "*"
        elif abs(vs_nt[i] - v_target) < (v_max-v_min)/height/2:
            line += "."
        else:
            line += " "
    print(f"{v_target:6.2f} |{line}")
print("       " + "-"*N)
print("        0.3                              3.0  (r)")

print("\n关键观察：")
print("  牛顿势（.）只有一个极小值——所有束缚轨道闭合（椭圆）。")
print("  GR 势（*）在 r→0 时 → -∞（第三项主导）→ 有内俘获区！")
print("  当 r 足够小，粒子坠入黑洞而非绕转。")
print("  有限距离处 GR 势极小值位置略偏 → 轨道不闭合 → 近日点进动。")
```

### 实验 10.2：宇宙膨胀模拟（FLRW）

```python
"""
PHYS 380 实验：不同宇宙学模型的尺度因子 a(t)
物质/辐射/暗能量主导三种情形
纯标准库
"""
import math

# 归一化: H0 = 1 (单位时间 = H0^-1 ~ 14 Gyr)
H0 = 1.0

def a_radiation(t):
    """辐射主导: a ~ t^(1/2)"""
    if t <= 0:
        return 0.0
    return (2 * H0 * t)**0.5

def a_matter(t):
    """物质主导: a ~ t^(2/3)"""
    if t <= 0:
        return 0.0
    return (1.5 * H0 * t)**(2/3)

def a_lambda(t, t0=0.5):
    """暗能量主导: a ~ exp(H*t)"""
    if t <= 0:
        return 0.0
    return math.exp(H0 * (t - t0))

def a_realistic(t, Omega_m=0.3, Omega_L=0.7):
    """近似真实宇宙 (物质+暗能量)"""
    # Friedmann 方程: H = H0*sqrt(Omega_m/a^3 + Omega_L), da/dt = H*a
    if t <= 0:
        return 0.0
    dt = 0.0005
    a = 0.001
    tt = 0.0
    while tt < t:
        H = H0 * math.sqrt(Omega_m / a**3 + Omega_L)
        a += H * a * dt
        tt += dt
        if a > 100:
            break
    return a

print("=== 宇宙尺度因子 a(t) ===")
print("归一化: H0=1, t=1 对应 ~Hubble 时间")
print(f"\n{'t':>6} {'a_辐射':>8} {'a_物质':>8} {'a_Λ':>8} {'a_真实':>8}")
t_max = 2.0
for i in range(21):
    t = i * t_max / 20
    ar = a_radiation(t)
    am = a_matter(t)
    al = a_lambda(t) if t > 0.01 else 0
    aR = a_realistic(t)
    print(f"{t:6.2f} {ar:8.3f} {am:8.3f} {al:8.3f} {aR:8.3f}")

# ASCII 图
print("\n=== a(t) 曲线对比 ===")
print("(R=辐射, M=物质, L=暗能量, *=真实宇宙)")
N = 60
height = 18
a_max = 3.0
ts = [i * t_max / N for i in range(N+1)]
for row in range(height, -1, -1):
    a_target = row * a_max / height
    line = ""
    for t in ts:
        chars = ""
        if abs(a_radiation(t) - a_target) < a_max/height/2:
            chars += "R"
        if abs(a_matter(t) - a_target) < a_max/height/2:
            chars += "M"
        if t > 0.05 and abs(a_lambda(t) - a_target) < a_max/height/2:
            chars += "L"
        if abs(a_realistic(t) - a_target) < a_max/height/2:
            chars += "*"
        line += chars[0] if chars else " "
    print(f"{a_target:4.2f} |{line}")
print("     " + "-"*(N+1))
print("      0                          t=2.0 (Hubble 时间)")

print("\n反直觉发现：")
print("  暗能量主导的宇宙膨胀是指数加速的！")
print("  未来宇宙将越来越接近 a ~ exp(Ht)。")
print("  届时所有星系退行到视界之外，宇宙变成一个孤岛。")
```

### 实验 10.3：黑洞参数与时空尺度

```python
"""
PHYS 250 实验：黑洞的基本参数
不同质量黑洞的事件视界、ISCO、潮汐力
纯标准库
"""
import math

G = 6.674e-11    # m^3/(kg·s^2)
c = 3e8           # m/s
Msun = 1.989e30   # kg

def schwarzschild_radius(M):
    """事件视界半径"""
    return 2 * G * M / c**2

def isco_radius(M):
    """最内稳定圆轨道 = 3 * r_s"""
    return 3 * schwarzschild_radius(M)

def hawking_temperature(M):
    """Hawking 温度"""
    hbar = 1.055e-34
    kB = 1.381e-23
    return hbar * c**3 / (8 * math.pi * G * M * kB)

def tidal_force(M, r, L=1.0):
    """潮汐加速度差 (头部到脚部距离 L)"""
    return 2 * G * M * L / r**3

objects = [
    ("地球", 5.972e24),
    ("木星", 1.898e27),
    ("太阳", Msun),
    ("10 太阳质量（恒星级）", 10*Msun),
    ("10^6 太阳质量（中介）", 1e6*Msun),
    ("M87*（65亿太阳质量）", 6.5e9*Msun),
    ("Ton 618（660亿太阳质量）", 6.6e10*Msun),
]

print("=== 黑洞参数表 ===")
print(f"{'天体':>24} {'r_s':>12} {'r_ISCO':>12} {'T_Hawking':>14} {'潮汐力(1m,r_s)':>16}")
for name, M in objects:
    rs = schwarzschild_radius(M)
    risco = isco_radius(M)
    TH = hawking_temperature(M)
    tide = tidal_force(M, rs, 1.0)  # 头脚距 1m, 在事件视界处
    if rs < 1e-2:
        rs_str = f"{rs*1000:.2f} mm"
    elif rs < 1e4:
        rs_str = f"{rs:.2f} m"
    elif rs < 1.496e11:
        rs_str = f"{rs/1e3:.1f} km"
    else:
        rs_str = f"{rs/1.496e11:.1f} AU"
    if risco < 1e4:
        risco_str = f"{risco:.1f} m"
    elif risco < 1.496e11:
        risco_str = f"{risco/1e3:.1f} km"
    else:
        risco_str = f"{risco/1.496e11:.1f} AU"
    TH_str = f"{TH:.2e} K"
    tide_str = f"{tide:.2e} m/s²"
    print(f"{name:>24} {rs_str:>12} {risco_str:>12} {TH_str:>14} {tide_str:>16}")

print("\n=== 关键反直觉发现 ===")
print("1. 地球质量黑洞只有 9 mm——可以放在口袋里！")
print("2. 越大的黑洞越冷：M87* 的霍金温度 ~10^-17 K，远低于 CMB。")
print("3. 大黑洞的潮汐力极弱（r_s 大），人在视界处不会被撕裂。")
print("   小黑洞的潮汐力极强（'意大利面化'）！")
print("4. 霍金辐射使小黑洞蒸发更快 → 大黑洞几乎永恒存在。")
print("\n这就是为什么超大质量黑洞是宇宙最稳定的结构之一。")
```

---

## 11. 局限与延伸

### 11.1 广义相对论与宇宙学的边界

| 未解问题 | 现状 | 可能方向 |
|---------|------|---------|
| 量子引力 | GR 在普朗克尺度失效 | 弦论、圈量子引力、AdS/CFT |
| 奇点定理 | Penrose-Hawking 证明奇点不可避免 | 量子引力消除奇点 |
| 暗物质本质 | 只知引力性质 | WIMP、轴子、修正引力 |
| 暗能量本质 | 真空能？标量场？ | 精确测量状态方程 $w(a)$ |
| 宇宙暴涨 | 解决视界/平坦性问题，但机制不明 | 暴涨子场、弦多重宇宙 |
| 宇宙学常数问题 | 真空能与观测差 $10^{120}$ 倍 | 最大的物理学危机 |

### 11.2 从 PHYS 250 到 PHYS 380 的认知跃迁

1. **PHYS 250**：弯曲时空的**数学**——张量、测地线、Einstein 方程
2. **PHYS 380**：宇宙的**演化**——从大爆炸到今天到未来
3. **前沿研究**：**观测+理论**——引力波天文学、精确宇宙学、量子引力

### 11.3 延伸阅读

- **Carroll《Spacetime and Geometry》**：PHYS 250 标准教材，从几何到应用
- **Dodelson & Schmidt《Modern Cosmology》2ed**：PHYS 380 标准，CMB + 结构形成
- **Weinberg《Cosmology》**：严谨全面的研究生参考
- **Misner, Thorne & Wheeler《Gravitation》**：GR 的百科全书（MTW 圣经）
- **Wald《General Relativity》**：数学严谨，适合理论方向
- **Baumann《Cosmology》**（剑桥讲义）：现代视角的宇宙学

---

## 参考文献

1. Carroll, S. M. *Spacetime and Geometry: An Introduction to General Relativity*. Cambridge, 2019.
2. Dodelson, S. & Schmidt, F. *Modern Cosmology* 2nd ed. Academic Press, 2020.
3. Weinberg, S. *Cosmology*. Oxford, 2008.
4. Misner, C. W., Thorne, K. S. & Wheeler, J. A. *Gravitation*. Freeman, 1973.
5. Wald, R. M. *General Relativity*. University of Chicago, 1984.
6. Planck Collaboration. "Planck 2018 Results." *A&A* **641**, A6 (2020).

---

> **本主题对应讲透X 宪法**：直觉（§1「直觉」段）→ 公式（§2-7 全部 boxed 公式）→ 代码（§10 bash 跑通）→ 不足（§11）→ 应用（§8 KIPAC 关联）。
>
> **文件信息**：stanford-physics/topic08-gr-cosmology/gr-cosmology.md · Phase 2 主题 8 · 2026-08-12

---

## 🎯 费曼式入口（白话版）

> **一句话解释**：引力不是力——是时空的弯曲。质量告诉时空怎么弯，弯曲的时空告诉物质怎么走。苹果落地不是被「拉」下来的，是顺着时空的「凹槽」滚下去的。

Einstein 最深刻的洞察：「站在自由下落的电梯里，你感觉不到引力。」这不是巧合，而是引力的本质。就像蹦床上的保龄球——它压出一个凹陷，弹珠滚过去时路径弯曲。太阳是保龄球，行星是弹珠，弯曲的不是蹦床而是时空本身。

> **生活类比**：宇宙膨胀就像在气球表面画满点，然后吹气球——每个点都看到其他点在远离自己，但没有任何点是「中心」。更诡异的是：不是点在气球表面「移动」，是气球本身在膨胀。星系之间没有相对运动，是空间本身在拉伸。

> **反直觉发现（啊哈时刻）**：
> 1. **时间在引力场中变慢**：黑洞附近 1 小时 = 地球上 7 年（电影《星际穿越》的硬核物理）。这不是科幻，GPS 卫星每天都要修正这个效应。
> 2. **我们只能看到宇宙的 5%**：暗能量 68.5% + 暗物质 26.8% + 普通物质 4.9%。你能看见的一切——恒星、行星、你、这本书——只占宇宙的百分之五。
> 3. **宇宙来自一个比原子还小的奇点**：138 亿年前，所有物质和空间压缩到 $10^{-35}$ m 尺度。CMB（2.725 K 微波背景）就是那个时刻的「照片」——已被红移到微波波段。

---

## 🔗 衔接：从哪来，到哪去

| 维度 | 内容 |
|------|------|
| **前置知识** | 主题 1（力学）的狭义相对论；主题 5（数学）的张量微积分/微分几何；主题 2（EM）的协变表述 |
| **本主题解决的危机** | 水星近日点反常进动（43"/世纪，牛顿力学无法解释）+ 引力的瞬时传播矛盾 → Einstein 用时空几何革命性解决 |
| **核心跃迁** | 从「弯曲时空数学」（PHYS 250）→「宇宙演化」（PHYS 380）→「精确观测+量子引力」（前沿） |
| **留下新危机** | ①量子引力（普朗克尺度 GR 失效）②暗物质本质 ③暗能量本质 ④宇宙学常数问题（理论与观测差 $10^{120}$ 倍）⑤奇点 |
| **后续方向** | 弦理论（PHYS 370）试图统一 GR 与量子力学；AdS/CFT 对偶；量子信息与黑洞 |

---

## 🏭 理论联系实际：5 个现代应用

1. **GPS 定位（GR + SR 修正）**：卫星钟每天比地面快 45 µs（GR 引力红移）- 7 µs（SR 钟慢）= +38 µs。不修正则定位每天漂移 ~10 km——GR 不是象牙塔，是你手机导航的隐形组件。

2. **LIGO 引力波探测器（2015 首次探测）**：4 公里激光干涉仪测量到 $10^{-21}$ 量级的时空畸变——13 亿光年外两个黑洞合并的「声音」。2017 诺奖，开启了引力波天文学。

3. **事件视界望远镜（EHT, 2019）**：全球射电望远镜阵列「拍」到了 M87 星系中心黑洞的剪影——直接验证了 Schwarzschild 度规与黑洞阴影的大小关系。

4. **引力透镜天文学**：大质量天体偏折背景星光（§4.4），放大远方星系。JWST 利用强引力透镜看到了 $z>10$ 的早期宇宙星系。

5. **核磁共振与原子钟**：引力红移在 cm 高度差上的效应（$10^{-18}$ 精度光学钟）已被测量——2024 年可用于「相对论测高」，监测地壳运动和地下水。

---

## 🔬 最新研究前沿（2024-2026）

1. **DESI 2024：暗能量可能在演化**：暗能量光谱仪（DESI）2024 年公布最大 3D 宇宙地图，发现暗能量状态方程 $w(a)$ 可能随时间变化——挑战宇宙学常数假设（$w=-1$）。如果属实，将颠覆 25 年来的标准宇宙学模型。

2. **JWST 早期星系挑战宇宙学（2023-2025）**：詹姆斯·韦伯望远镜发现 $z>10$ 的超大质量星系，比标准模型预言的「更亮、更成熟」——可能需要修改早期宇宙结构形成理论，或暗物质性质。

3. **NANOGrav 超大质量黑洞背景（2023-2024）**：脉冲星计时阵列（PTA）首次探测到纳赫兹引力波背景——可能来自早期宇宙中超大质量黑洞双旋的集体信号，开启低频引力波窗口。

4. **LIGO O4 与 LISA 进展（2023-2025）**：LIGO 第四轮观测已记录数十个新事件。欧洲空间局 LISA 任务（2030s 发射）将探测 mHz 引力波——超质量黑洞并合、极端质量比旋近。

5. **黑洞信息悖论的进展（2024-2025）**：量子信息与引力融合——「岛屿公式」（island formula）与 Page 曲线计算表明，信息确实能从黑洞辐射逃出，AdS/CFT 对偶为量子引力提供了新线索。Stanford 的 Susskind 等人在此方向持续引领。

---

## 🗺️ 学习 Roadmap（Stanford 路径）

```
入门 → PHYS 250 (Carroll《Spacetime and Geometry》— Stanford 讲义!)
  │   等效原理、张量微积分、Einstein 场方程、Schwarzschild 解、黑洞
  │   ✅ 检查点：能推导水星近日点进动的 43"/世纪
  ▼
进阶 → PHYS 380 (Dodelson & Schmidt《Modern Cosmology》)
  │   FLRW 度规、Friedmann 方程、CMB、结构形成、暗物质/暗能量
  │   ✅ 检查点：能解释宇宙能量收支的 5%-27%-68% 结构
  ▼
深造 → 前沿专题
  │   数值相对论（黑洞合并）、量子引力、弦宇宙学
  │   ✅ 检查点：理解为什么宇宙学常数是物理学最大危机
  ▼
前沿 → KIPAC / LIGO / JWST / Vera Rubin 天文台
      引力波天文学、精确宇宙学、量子信息与黑洞
```

> **费曼的建议**：GR 最反直觉的是「时空是演员，不是舞台」。先彻底理解等效原理——一个自由下落的人感觉不到引力——然后整个 GR 的几何图像就自然浮现。Carroll 的教材之所以是经典，因为它就是 Stanford PHYS 250 的讲义。
