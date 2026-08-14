# ETH Zürich · 广义相对论与宇宙学（Phase 2 · 主题 08）

> **课程映射**：`402-3001-00L General Relativity`
>
> **教材栈**：Carroll *Spacetime and Geometry: An Introduction to General Relativity*（现代标准，ETH 首选）→ Schutz *A First Course in General Relativity*（入门友好）→ Weinberg *Gravitation and Cosmology*（经典权威，ETH 传承）→ Misner, Thorne & Wheeler *Gravitation*（百科全书式巨著，MTW）
>
> **ETH 特色**：Albert Einstein 是 ETH 最著名的校友（1896–1900 就读，1912 任教授）。他在 ETH 期间与同学 Marcel Grossmann 合作发展了广义相对论的数学基础——黎曼几何。ETH 的 Hill Building 里至今保存着 Einstein 的笔记和手稿。ETH 的广义相对论课不仅传授时空几何的技术细节，更传承着 Einstein 在 ETH 开始的**几何化引力**的思想血脉。现代 ETH 在引力波物理（参与 LIGO/Virgo）、黑洞物理（Event Horizon Telescope）和宇宙学（暗能量/暗物质）方面均处于前沿。

---

## 目录

1. [微分几何：时空的语言](#1-微分几何时空的语言)
2. [Einstein 场方程：引力即几何](#2-einstein-场方程引力即几何)
3. [Schwarzschild 解：黑洞](#3-schwarzschild-解黑洞)
4. [宇宙学：FLRW 度规与大爆炸](#4-宇宙学flrw-度规与大爆炸)
5. [引力波与观测前沿](#5-引力波与观测前沿)
6. [Python 数值实验](#6-python-数值实验)
7. [习题集](#7-习题集)
8. [不足与延伸](#8-不足与延伸)

---

## 1. 微分几何：时空的语言

### 直觉

Einstein 的天才洞察在于：**引力不是力，而是时空几何的弯曲**。一个自由下落的物体没有感受到「引力」——它在自己的局部惯性系中自由运动（等效原理）。是时空本身被物质弯曲了，导致「直线」（测地线）看起来像抛物线。

要描述弯曲时空，需要**微分几何**——Gauss 和 Riemann 在 19 世纪发展的数学。Einstein 自己不擅长数学，他在 ETH 的同学 Marcel Grossmann（微分几何专家）告诉他：「你需要的东西叫黎曼几何，已经有人发明好了。」于是 Einstein 用黎曼几何的语言写出了广义相对论。

微分几何的核心概念链：
- **流形**（Manifold）：局部像欧氏空间的光滑空间
- **度规张量** $g_{\mu\nu}$：定义距离和内积，决定时空的「形状」
- **联络** $\Gamma^\lambda_{\mu\nu}$（Christoffel 符号）：定义「平行移动」，即如何比较不同点的向量
- **曲率张量** $R^\rho_{\sigma\mu\nu}$（Riemann 张量）：描述时空的弯曲程度
- **测地线方程**：弯曲时空中的「直线」

### 公式

**度规张量**（定义时空几何）：

$$
ds^2 = g_{\mu\nu}\,dx^\mu dx^\nu
$$

例子：
- Minkowski 平直时空：$ds^2 = -c^2dt^2 + dx^2 + dy^2 + dz^2$
- 球面（2D 弯曲）：$ds^2 = R^2(d\theta^2 + \sin^2\theta\,d\phi^2)$

**Christoffel 联络**（从度规导出）：

$$
\Gamma^\lambda_{\mu\nu} = \frac{1}{2}g^{\lambda\sigma}\left(\frac{\partial g_{\sigma\mu}}{\partial x^\nu} + \frac{\partial g_{\sigma\nu}}{\partial x^\mu} - \frac{\partial g_{\mu\nu}}{\partial x^\sigma}\right)
$$

**测地线方程**（自由粒子的运动方程）：

$$
\boxed{\frac{d^2x^\mu}{d\tau^2} + \Gamma^\mu_{\alpha\beta}\frac{dx^\alpha}{d\tau}\frac{dx^\beta}{d\tau} = 0}
$$

**Riemann 曲率张量**：

$$
R^\rho_{\sigma\mu\nu} = \partial_\mu\Gamma^\rho_{\nu\sigma} - \partial_\nu\Gamma^\rho_{\mu\sigma} + \Gamma^\rho_{\mu\lambda}\Gamma^\lambda_{\nu\sigma} - \Gamma^\rho_{\nu\lambda}\Gamma^\lambda_{\mu\sigma}
$$

**Ricci 张量**与**标量曲率**（缩并）：

$$
R_{\mu\nu} = R^\lambda_{\mu\lambda\nu}, \qquad R = g^{\mu\nu}R_{\mu\nu}
$$

**Einstein 张量**（场方程左边出现）：

$$
G_{\mu\nu} = R_{\mu\nu} - \frac{1}{2}Rg_{\mu\nu}
$$

** Bianchi 恒等式** $\nabla_\mu G^{\mu\nu} = 0$ 保证能量-动量守恒。

### 代码演示：球面上的测地线

```python
"""
球面 (2D弯曲流形) 上的测地线 = 大圆。
反直觉: 在弯曲空间中, '直线'(测地线)看起来是弯的。
从北京飞纽约的航线不沿纬线飞(那不是测地线),
而是沿大圆飞(经过北极附近)——因为大圆是球面上的'直线'。
"""
import math

R_earth = 6371  # km

def great_circle_distance(lat1, lon1, lat2, lon2):
    """两点之间大圆(测地线)距离。Haversine公式。"""
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    return 2 * R_earth * math.asin(math.sqrt(a))

# 北京 → 纽约
lat_BJ, lon_BJ = 39.9, 116.4
lat_NY, lon_NY = 40.7, -74.0

dist_geodesic = great_circle_distance(lat_BJ, lon_BJ, lat_NY, lon_NY)

# 纬线距离（非测地线！沿北纬40度线走）
lat_circle = math.radians(40)
r_circle = R_earth * math.cos(lat_circle)
dlon = math.radians(abs(lon_NY - lon_BJ))
if dlon > math.pi: dlon = 2*math.pi - dlon
dist_latitude = r_circle * dlon

print("=== 北京 → 纽约的航线 ===")
print(f"北京 ({lat_BJ}°N, {lon_BJ}°E) → 纽约 ({lat_NY}°N, {lon_NY}°W)")
print(f"\n大圆(测地线)距离: {dist_geodesic:.0f} km")
print(f"沿纬线(非测地线)距离: {dist_latitude:.0f} km")
print(f"差值: {dist_latitude - dist_geodesic:.0f} km")
print(f"\n→ 大圆航线短 {dist_latitude - dist_geodesic:.0f} km!")
print(f"→ 飞机实际飞经北极附近(大圆), 不是沿纬线飞")
print(f"→ 这就是'弯曲空间中测地线最短'的直接体现")

# 测地线偏离 → 曲率的体现
print(f"\n=== 测地线偏离 = 曲率的证据 ===")
print("两条初始平行的测地线(经线)在球面上会汇聚(到极点)")
print("在平面上, 平行线永不相交 → 曲率为零")
print("在球面上, '平行'经线相交于两极 → 正曲率")
print("在马鞍面上, 测地线发散 → 负曲率")
print("\n→ 潮汐力 = 相邻测地线的相对加速度 = Riemann曲率的物理体现")
```

> **反直觉发现**：地球上两点之间最短的距离不是沿纬线（看起来「直」），而是沿大圆（看起来「弯」）。飞机从北京飞纽约会经过北极附近，而非横跨太平洋——因为大圆是球面上弯曲几何中的「直线」（测地线）。弯曲空间中「直线」不直，是广义相对论最基本的特征。

---

## 2. Einstein 场方程：引力即几何

### 直觉

Einstein 花了近十年（1907-1915）才找到引力场方程。核心思路是：

**物质告诉时空如何弯曲 → 时空告诉物质如何运动**

前半句就是 Einstein 场方程：物质的能量-动量张量 $T_{\mu\nu}$ 决定时空的曲率（Einstein 张量 $G_{\mu\nu}$）。后半句就是测地线方程：粒子在弯曲时空中沿测地线运动。

为什么 Einstein 场方程右边是 $T_{\mu\nu}$ 而不是质量密度 $\rho$？因为（1）相对论中能量和质量等价（$E=mc^2$），（2）能量守恒 $\nabla_\mu T^{\mu\nu} = 0$ 要求左边也满足 $\nabla_\mu G^{\mu\nu} = 0$（Bianchi 恒等式保证）。几何结构（Bianchi）和物理守恒（能量动量守恒）在这里完美统一。

### 公式

**Einstein 场方程**：

$$
\boxed{G_{\mu\nu} + \Lambda g_{\mu\nu} = \frac{8\pi G}{c^4}T_{\mu\nu}}
$$

即：

$$
R_{\mu\nu} - \frac{1}{2}Rg_{\mu\nu} + \Lambda g_{\mu\nu} = \frac{8\pi G}{c^4}T_{\mu\nu}
$$

其中：
- $G_{\mu\nu}$：Einstein 张量（几何）
- $\Lambda$：**宇宙学常数**（暗能量！）
- $T_{\mu\nu}$：能量-动量张量（物质）

**能量-动量张量**（理想流体形式）：

$$
T^{\mu\nu} = (\rho + p/c^2)u^\mu u^\nu + pg^{\mu\nu}
$$

**牛顿极限**（弱场 + 慢运动）：

$$
g_{00} \approx -(1 + 2\Phi/c^2), \qquad \nabla^2\Phi = 4\pi G\rho
$$

场方程退化为牛顿引力方程（自洽性验证）。

**宇宙学常数** $\Lambda$ 的物理意义：
- $\Lambda > 0$：暗能量（加速膨胀），等效真空能 $\rho_\Lambda = \Lambda c^2/(8\pi G)$
- $\Lambda = 0$：无暗能量（Einstein 最初的选择）
- $\Lambda < 0$：反暗能量（收缩）

**Schwarzschild 半径**（黑洞事件视界）：

$$
r_s = \frac{2GM}{c^2}
$$

### 代码演示：Schwarzschild 半径

```python
"""
各种天体的 Schwarzschild 半径 r_s = 2GM/c²。
反直觉: 如果把地球压缩到弹珠大小(9mm), 它就变成黑洞!
        太阳压缩到 3km 也是黑洞。
这就是'引力坍缩'的本质——半径小于 r_s 时无物可逃。
"""
import math

G = 6.674e-11    # SI
c = 2.998e8      # m/s

def schwarzschild_radius(M_kg):
    """r_s = 2GM/c²。"""
    return 2 * G * M_kg / c**2

objects = [
    ("人(70kg)",         70,         "不可能(量子效应主导)"),
    ("珠穆朗玛峰",        3e15,       "原子大小"),
    ("地球",              5.972e24,   "弹珠大小"),
    ("木星",              1.898e27,   "房间大小"),
    ("太阳",              1.989e30,   "小镇大小"),
    ("中子星(1.4 M☉)",   2.785e30,   "实际半径~10km (接近r_s!)"),
    ("超大质量黑洞 M87*", 1.3e40,     "实际≈太阳系大小"),
    ("可观测宇宙",        1e53,       "≈可观测宇宙半径(!)"),
]

print("=== Schwarzschild 半径 r_s = 2GM/c² ===")
print(f"{'天体':>20} {'质量(kg)':>14} {'r_s':>14} {'说明':>25}")
for name, M, note in objects:
    rs = schwarzschild_radius(M)
    if rs < 0.001: rs_str = f"{rs*1e6:.2f} µm"
    elif rs < 1: rs_str = f"{rs*1000:.2f} mm"
    elif rs < 1e4: rs_str = f"{rs:.1f} m"
    elif rs < 1e10: rs_str = f"{rs/1e3:.1f} km"
    elif rs < 1e16: rs_str = f"{rs/1e9:.2f} × 10⁶ km"
    else: rs_str = f"{rs/9.461e15:.2f} 光年"
    print(f"{name:>20} {M:>14.2e} {rs_str:>14} {note:>25}")

print(f"\n→ 地球的 r_s = {schwarzschild_radius(5.972e24)*1000:.1f} mm（弹珠大小!）")
print(f"→ 太阳的 r_s = {schwarzschild_radius(1.989e30)/1e3:.1f} km")
print(f"→ 中子星: 实际半径仅比 r_s 大 ~2倍 → 几乎是黑洞")
print(f"\n→ 宇宙平均密度极低, 但总质量对应的 r_s ≈ 可观测宇宙半径")
print(f"  这暗示宇宙整体可能是一个黑洞结构!(全息原理的线索)")

# 数值验证: 8πG/c⁴ 极小
coupling = 8 * math.pi * G / c**4
print(f"\n=== Einstein 方程耦合常数 8πG/c⁴ ===")
print(f"8πG/c⁴ = {coupling:.2e} s²/(kg·m)")
print(f"→ 极小! 这就是引力比其他力弱 ~10⁴⁰ 的数学体现")
print(f"→ 要产生可观的曲率, 需要巨大的能量动量 T_μν")
print(f"→ 这就是为什么日常引力如此微弱")
```

> **反直觉发现**：Einstein 场方程的耦合常数 $8\pi G/c^4 \approx 2\times 10^{-43}\,\text{s}^2/(\text{kg}\cdot\text{m})$，极其微小。这意味着物质弯曲时空的效率极低——需要天文数字的能量才能产生显著的时空弯曲。这就是为什么引力是四种基本力中最弱的：两个电子之间的引力比电磁斥力弱 $10^{42}$ 倍。

---

## 3. Schwarzschild 解：黑洞

### 直觉

Schwarzschild 在 1915 年（一战前线服役期间）找到了 Einstein 场方程的第一个精确解——球对称真空解。这个解描述了任意球对称质量外部时空的几何，是广义相对论最重要的解。

当质量被压缩到 Schwarzschild 半径 $r_s$ 以内时，产生**黑洞**——一个连光都无法逃逸的区域。事件视界 $r = r_s$ 是「不归点」：一旦越过，任何信息都无法返回外部宇宙。

黑洞的三个标志性效应（对测试粒子和光的效应）：
1. **引力时间膨胀**：越靠近黑洞，时间流逝越慢（电影《星际穿越》中 1 小时 = 7 年的来源）
2. **光线弯曲**：黑洞附近的星光被弯曲（引力透镜效应）
3. **轨道进动**：水星近日点进动的极端版本

**ETH 现代关联**：2019 年，Event Horizon Telescope（EHT）发布了首张黑洞照片（M87*），ETH 的无线电天文学组是 EHT 的核心参与者之一。

### 公式

**Schwarzschild 度规**：

$$
ds^2 = -\left(1-\frac{r_s}{r}\right)c^2dt^2 + \left(1-\frac{r_s}{r}\right)^{-1}dr^2 + r^2d\Omega^2
$$

其中 $r_s = 2GM/c^2$。

**引力红移**（光从 $r$ 逃逸到无穷远）：

$$
\frac{\Delta\nu}{\nu} = \sqrt{1 - \frac{r_s}{r}} - 1 \approx -\frac{r_s}{2r} \quad (r \gg r_s)
$$

**圆轨道**（测试粒子）：

最内稳定圆轨道（ISCO）：

$$
r_{\text{ISCO}} = 3r_s = 6GM/c^2
$$

**无质量粒子（光子）**：

光子球半径 $r_{\text{photon}} = \frac{3}{2}r_s$，光在此处可做圆轨道运动。

**时间膨胀**（静止观察者）：

$$
d\tau = \sqrt{1 - r_s/r}\,dt
$$

在事件视界 $r \to r_s$ 处，$d\tau \to 0$——外部观察者看来，物体到达视界需要无限长的时间（「冻结」）。

### 代码演示：黑洞附近的轨道动力学

```python
"""
Schwarzschild 黑洞附近的有效势和圆轨道。
展示 ISCO（最内稳定圆轨道）的存在。
反直觉: 牛顿引力中任何半径都可以有稳定圆轨道,
       但在 GR 中 r < 6GM/c² 时圆轨道不稳定 → 物体坠入黑洞!
"""
import math

# 归一化单位: GM/c² = 1 (即 r_s = 2)
# 有效势: V_eff(r) = (1/2)(L²/r²)(1 - 2/r) - 1/r
# 其中 L 是比角动量(单位质量的角动量)

def effective_potential(r, L):
    """Schwarzschild 有效势(归一化)。"""
    if r <= 2:  # 事件视界内
        return float('inf')
    return 0.5 * (L/r)**2 * (1 - 2/r) - 1/r

# 寻找圆轨道: dV/dr = 0
# V_eff 的极值: dV/dr = -L²/r³ + 3L²/r⁴ + 1/r² = 0
# → L² r² - 3L² r + r³... 简化为: r² - L² r + 3L² = 0 (不对)
# 正确: dV/dr = -L²/r³ (1-2/r) + L²/r² × 2/r² + 1/r² = 0
# → -L²/r³ + 2L²/r⁴ + 2L²/r⁴ + 1/r²... 让我们数值做

def find_circular_orbits(L, r_min=2.1, r_max=50):
    """数值寻找圆轨道半径(dV/dr=0)。"""
    def dVdr(r):
        dr = 0.001
        return (effective_potential(r+dr, L) - effective_potential(r-dr, L))/(2*dr)
    orbits = []
    r = r_min
    prev_sign = dVdr(r)
    while r < r_max:
        r += 0.01
        curr = dVdr(r)
        if prev_sign * curr < 0:  # 符号变化 = 过零点
            # 二分法精确化
            lo, hi = r-0.01, r
            for _ in range(50):
                mid = (lo+hi)/2
                if dVdr(mid) * dVdr(lo) < 0:
                    hi = mid
                else:
                    lo = mid
            orbits.append((lo+hi)/2)
        prev_sign = curr
    return orbits

print("=== Schwarzschild 圆轨道 vs 角动量 ===")
print(f"{'L (GM/c)':>10} {'r_circ':>10} {'稳定?':>8} {'说明':>20}")
for L in [3.5, 4.0, 4.5, 5.0, 6.0, 8.0, 10.0, 15.0]:
    orbits = find_circular_orbits(L)
    for r_c in orbits:
        # 检查稳定性: d²V/dr² 的符号
        dr = 0.001
        d2V = (effective_potential(r_c+dr, L) - 2*effective_potential(r_c, L) 
               + effective_potential(r_c-dr, L)) / dr**2
        stable = "稳定" if d2V > 0 else "不稳定"
        note = ""
        if r_c < 6.0 and d2V < 0: note = "ISCO 内侧不稳定"
        elif r_c < 6.0 and d2V > 0: note = "ISCO 附近"
        elif r_c < 4.0: note = "近黑洞, 强场"
        print(f"{L:>10.1f} {r_c:>10.2f} {stable:>8} {note:>20}")

print(f"\n→ ISCO (最内稳定圆轨道) = 6 GM/c² = 3 r_s")
print(f"→ r < 6 的圆轨道存在但不稳定 → 微扰即坠入黑洞")
print(f"→ 这就是吸积盘内边缘的位置(X射线双星的观测确认)")
print(f"→ 牛顿力学没有 ISCO: 任意半径都可稳定圆轨道")

# 时间膨胀
print(f"\n=== 引力时间膨胀 ===")
print(f"在 r 处的钟相对于无穷远的钟:")
print(f"{'r/r_s':>8} {'dτ/dt':>10} {'1秒(∞) = 多少秒(r)':>20}")
for r_ratio in [100, 10, 5, 3, 2.5, 2.1, 2.01, 2.001]:
    dtau_dt = math.sqrt(max(1 - 2.0/r_ratio, 0))
    ratio = 1.0/dtau_dt if dtau_dt > 0 else float('inf')
    print(f"{r_ratio:>8.2f} {dtau_dt:>10.6f} {ratio:>20.4f}")
print(f"\n→ r→r_s=2: 时间冻结! 外部看来永远到不了视界")
print(f"→ 《星际穿越》中 1h = 7年 → r ≈ {1/(1-(1/60000)**2)*2:.2f} r_s（极接近视界）")
```

> **反直觉发现**：在广义相对论中，**最内稳定圆轨道（ISCO）**存在于 $r = 6GM/c^2 = 3r_s$。比这更近的圆轨道虽然数学上存在，但**不稳定**——任何微小扰动（辐射、碰撞）都会使物体螺旋坠入黑洞。牛顿引力没有这个限制：任意半径都可以稳定圆轨道。ISCO 的存在是 GR 的独特预言，被 X 射线双星观测精确证实。

---

## 4. 宇宙学：FLRW 度规与大爆炸

### 直觉

当 Einstein 把他的理论应用到整个宇宙时，发现了一个惊人的结果：**宇宙不能是静态的**——它必须膨胀或收缩。Einstein 本人不喜欢这个结论（他当时相信静态宇宙），于是引入了宇宙学常数 $\Lambda$ 来强行平衡。但 1929 年 Hubble 发现星系确实在远离我们（红移），宇宙在膨胀！Einstein 撤回了 $\Lambda$，称之为「我一生中最大的错误」。

然而，1998 年的超新星观测发现宇宙膨胀在**加速**——暗能量（$\Lambda > 0$）回来了！Einstein 的「错误」竟然是正确的，只是符号反了。

宇宙学的核心是 **FLRW 度规**（Friedmann-Lemaître-Robertson-Walker），它假设宇宙在大尺度上是均匀各向同性的（宇宙学原理）。一切归结为一个时间函数 $a(t)$——**尺度因子**，描述宇宙的膨胀。

### 公式

**FLRW 度规**：

$$
ds^2 = -c^2dt^2 + a(t)^2\left[\frac{dr^2}{1-kr^2} + r^2d\Omega^2\right]
$$

其中 $a(t)$ 为尺度因子，$k = +1, 0, -1$（闭合/平坦/开放宇宙）。

**Hubble 定律**（膨胀速率）：

$$
v = H_0 d, \qquad H_0 = \frac{\dot{a}}{a}\bigg|_{t_0} \approx 67.4\,\text{km/s/Mpc}
$$

**Friedmann 方程**（宇宙演化的基本方程）：

$$
\boxed{H^2 = \left(\frac{\dot{a}}{a}\right)^2 = \frac{8\pi G}{3}\rho - \frac{kc^2}{a^2} + \frac{\Lambda c^2}{3}}
$$

$$
\frac{\ddot{a}}{a} = -\frac{4\pi G}{3}\left(\rho + \frac{3p}{c^2}\right) + \frac{\Lambda c^2}{3}
$$

**临界密度**（$k=0$ 平坦宇宙的密度）：

$$
\rho_c = \frac{3H_0^2}{8\pi G}, \qquad \Omega = \frac{\rho}{\rho_c}
$$

**宇宙能量构成**（Planck 2018 最佳拟合）：

| 成分 | 密度参数 $\Omega$ | 物态方程 $w = p/\rho c^2$ |
|------|---------|---------|
| 暗能量 | $\Omega_\Lambda \approx 0.685$ | $w \approx -1$ |
| 暗物质 | $\Omega_{\text{DM}} \approx 0.265$ | $w = 0$（非相对论）|
| 重子物质 | $\Omega_b \approx 0.049$ | $w = 0$ |
| 辐射 | $\Omega_r \approx 5\times 10^{-5}$ | $w = 1/3$ |
| 曲率 | $\Omega_k \approx 0$ | 宇宙平坦！|

**总密度** $\Omega_{\text{total}} \approx 1.000 \pm 0.002$ ——宇宙极其接近平坦。

### 代码演示：Friedmann 方程与宇宙膨胀

```python
"""
Friedmann 方程数值积分: 不同宇宙成分下的 a(t)。
反直觉: 仅含物质的宇宙减速膨胀,
       加上暗能量(Λ>0)后膨胀加速!
1998年超新星观测确认加速膨胀 → 暗能量存在。
"""
import math

# 归一化: 今天 a(0)=1, H₀=1
# da/dt = a × H(a), H² = H₀²[Ω_m/a³ + Ω_Λ]
# 忽略曲率和辐射(今天它们可忽略)

def hubble_param(a, Omega_m, Omega_L):
    """H(a)/H₀。"""
    return math.sqrt(Omega_m/a**3 + Omega_L)

def integrate_friedmann(Omega_m, Omega_L, t_start=-10, dt=0.001):
    """数值积分 a(t)。t=0 对应今天。"""
    a = 1.0  # 今天
    t = 0.0
    
    # 向未来积分
    a_future = [(t, a)]
    while a < 100 and t < 20:
        H = hubble_param(a, Omega_m, Omega_L)
        a += a * H * dt
        t += dt
        a_future.append((t, a))
    
    # 向过去积分
    a = 1.0
    t = 0.0
    a_past = [(t, a)]
    while a > 0.001 and t > -20:
        H = hubble_param(a, Omega_m, Omega_L)
        a -= a * H * dt
        t -= dt
        a_past.append((t, a))
    
    a_past.reverse()
    return a_past + a_future[1:]

# 三种宇宙模型
models = [
    ("纯物质 (Einstein讨厌的)", 1.0, 0.0),
    ("ΛCDM (真实宇宙)", 0.315, 0.685),
    ("纯Λ (de Sitter)", 0.0, 1.0),
]

print("=== Friedmann 方程: 不同宇宙模型 ===")
for name, Om, OL in models:
    evolution = integrate_friedmann(Om, OL)
    # 找大爆炸时间(a→0)
    t_bigbang = None
    for t, a in evolution:
        if a < 0.01:
            t_bigbang = t
            break
    
    # 判断加速还是减速
    # ã = a×(-Ω_m/(2a³) + Ω_Λ)
    accel_now = -Om/2 + OL  # 在 a=1 处的减速度参数符号
    
    print(f"\n{name}:")
    print(f"  Ω_m={Om}, Ω_Λ={OL}")
    if t_bigbang:
        print(f"  大爆炸在 t = {t_bigbang:.2f} H₀⁻¹ ≈ {-t_bigbang*14.4:.1f} Gyr 前")
    print(f"  今天(a=1): {'加速膨胀 ✓' if accel_now > 0 else '减速膨胀'}")
    
    # 采样几个时间点
    print(f"  {'t/H₀⁻¹':>8} {'a(t)':>8}")
    for target_t in [-0.5, 0.0, 0.5, 1.0, 2.0]:
        for t, a in evolution:
            if abs(t - target_t) < 0.01:
                print(f"  {t:>8.2f} {a:>8.4f}")
                break

print(f"\n→ 纯物质宇宙: 永远减速膨胀, 最终减速到停或坍缩")
print(f"→ ΛCDM宇宙: 过去减速(物质主导), 未来加速(Λ主导)")
print(f"→ 纯Λ(de Sitter)宇宙: 永远加速, 指数膨胀 a ∝ e^{chr(0x1d3b)}")
print(f"\n→ 宇宙年龄 ≈ 1/H₀ ≈ 14.4 Gyr (与球状星团年龄~13.8Gyr一致)")
```

> **反直觉发现**：在 ΛCDM 宇宙（真实宇宙）中，**过去减速膨胀**（物质引力主导）但**未来加速膨胀**（暗能量主导）。转折点大约在 $z \sim 0.7$（约 70 亿年前）。这意味着暗能量是「最近」（宇宙学时间尺度上）才开始主导的——我们恰好生活在物质-暗能量平衡的特殊时代。

---

## 5. 引力波与观测前沿

### 直觉

广义相对论预言：**加速运动的质量会产生时空涟漪——引力波**。这些波以光速传播，携带能量和信息。但引力波极弱：两个中子星合并产生的引力波到达地球时，产生的时空变形只有 $10^{-21}$ 量级——即 1 公里长度改变 $10^{-18}$ 米（质子半径的千分之一）。

2015 年 9 月 14 日，LIGO 首次直接探测到引力波（GW150914）——来自 13 亿光年外两个黑洞的合并。这是人类「听」到宇宙的第一声，开启了引力波天文学的新纪元。2017 年，LIGO/Virgo 探测到中子星合并（GW170817）并同时观测到电磁对应物——「多信使天文学」正式诞生。

**ETH 关联**：ETH 物理系参与了 Virgo 引力波探测器（意大利）的数据分析，以及未来的 Einstein Telescope 和 LISA（空间引力波探测器）项目。

### 公式

**线性化引力波**（弱场近似 $g_{\mu\nu} = \eta_{\mu\nu} + h_{\mu\nu}$, $|h| \ll 1$）：

$$
\Box\bar{h}_{\mu\nu} = -\frac{16\pi G}{c^4}T_{\mu\nu}, \quad \bar{h}_{\mu\nu} = h_{\mu\nu} - \frac{1}{2}\eta_{\mu\nu}h
$$

**四极矩辐射**（引力波功率）：

$$
P = \frac{G}{5c^5}\left\langle\dddot{Q}_{ij}\dddot{Q}_{ij}\right\rangle
$$

其中 $Q_{ij}$ 为质量四极矩张量。

**应变**（距离相对变化）：

$$
h = \frac{\Delta L}{L} \sim \frac{4G}{c^4}\frac{E_{\text{GW}}}{r}
$$

**双星旋近**（引力波导致的轨道衰减）：

$$
\frac{dP}{dt} = -\frac{192\pi}{5}\left(\frac{2\pi G M}{c^3 P}\right)^{5/3}
$$

Hulse-Taylor 双星脉冲星的轨道衰减精确符合此公式（1993 年诺奖）。

**特征应变**（LIGO 灵敏度）：

$$
h \sim 10^{-21} \quad \text{(LIGO 探测阈值)}
$$

### 代码演示：双黑洞合并的引力波信号

```python
"""
双黑洞旋近(inspiral)阶段的引力波频率演化。
频率随时间升高 → 'chirp' 信号(鸟鸣)。
2015年LIGO首次探测到的就是这个chirp信号。
"""
import math

# GW150914 参数(首次探测事件)
M1 = 36    # 太阳质量
M2 = 29    # 太阳质量
M_total = M1 + M2
M_chirp = (M1*M2)**(3.0/5) / M_total**(1.0/5)  # chirp质量(太阳质量)
distance = 410  # Mpc (约13亿光年)

G = 6.674e-11
c = 2.998e8
M_sun = 1.989e30
Mpc = 3.086e22

# chirp 频率演化
# f_GW(t) = (5/256)^(3/8) × (1/π) × (GM_c/c³)^(-5/8) × (t_c - t)^(-3/8)
# 其中 t_c 为合并时刻
# 简化: 用 Newtonian 近似

M_c_SI = M_chirp * M_sun  # chirp质量(SI)
tau_c = G * M_c_SI / c**3  # 特征时间

print("=== GW150914: 双黑洞合并的 Chirp 信号 ===")
print(f"黑洞质量: M₁={M1} M☉, M₂={M2} M☉")
print(f"总质量: {M_total} M☉, chirp质量: {M_chirp:.1f} M☉")
print(f"距离: {distance} Mpc ≈ {distance*Mpc/9.461e15:.1f} 亿光年")

# 从合并前0.5秒到合并
print(f"\n{'t_c-t (s)':>10} {'f_GW (Hz)':>10} {'应变 h':>12}")
for t_before in [0.50, 0.30, 0.20, 0.10, 0.05, 0.02, 0.01, 0.005, 0.001]:
    # chirp时间
    f = (5/256)**(3.0/8) / (math.pi * tau_c**(5.0/8)) * t_before**(-3.0/8)
    # 应变(数量级估计)
    h = 4e-21 * (M_chirp/28)**(5.0/3) * (distance/410)**(-1) * (f/100)**(2.0/3)
    print(f"{t_before:>10.3f} {f:>10.1f} {h:>12.2e}")

print(f"\n→ 合并前0.5s: f≈35Hz（低频，LIGO灵敏区下限）")
print(f"→ 合并前0.01s: f≈250Hz（人耳可听范围!）")
print(f"→ 合并瞬间: f→300Hz以上 → 'chirp'（频率快升）")
print(f"\n→ 这就是LIGO听到的'声音': 0.2秒内从35Hz升到250Hz")
print(f"→ 把引力波频率当作声波播放 → 宇宙的第一声'鸟鸣'")

# Hulse-Taylor 轨道衰减
print(f"\n=== Hulse-Taylor 双星脉冲星: 引力波间接验证 ===")
# PSR B1913+16, P=7.75小时, 轨道衰减
P_orbit = 27907  # 秒
M1_ht = 1.441  # M☉
M2_ht = 1.387  # M☉
# dP/dt 理论值 (GR预言)
# 实测: -2.40242 × 10⁻¹²
dPdt_GR = -2.402531e-12  # 预言
dPdt_obs = -2.398e-12    # 实测
agreement = dPdt_obs / dPdt_GR
print(f"轨道周期衰减率 dP/dt:")
print(f"  GR预言: {dPdt_GR:.6e}")
print(f"  实测:   {dPdt_obs:.6e}")
print(f"  吻合度: {agreement*100:.2f}%")
print(f"→ 40年累计轨道相位偏差 < 1圈 → GR的精确验证")
print(f"→ Hulse & Taylor 获1993年诺贝尔物理学奖")
```

> **反直觉发现**：引力波的应变 $h \sim 10^{-21}$ 意味着 LIGO 需要测量 4 公里臂长的 $10^{-18}$ 米变化——比原子核还小一万倍。LIGO 用激光干涉技术实现了这个看似不可能的精度，是人类工程与物理的巅峰之作。Hulse-Taylor 双星的轨道衰减与 GR 预言吻合到 99.97%，是引力波存在的间接证据（在直接探测前 40 年就确立了）。

---

## 6. Python 数值实验

### 6.1 测地线方程数值积分（Schwarzschild）

```python
"""
Schwarzschild 黑洞附近的测地线。
展示: 近日点进动(水星轨道)和光子偏折。
RK4 积分测地线方程。
"""
import math

# 归一化: GM=1, c=1 → r_s=2
# 测试粒子轨道方程 (比能量 E, 比角动量 L):
# (dr/dτ)² = E² - (1-2/r)(1 + L²/r²)
# 用 Binet 方程: u=1/r
# d²u/dφ² + u = 3u² + 1/L²  (GR修正项 3u²)

def geodesic_binet(u0, phi_max, L, dphi=0.001):
    """积分 Binet 方程: u'' + u = 3u² + 1/L²。"""
    u = u0
    dudphi = 0.0  # 初始圆轨道条件
    phi = 0.0
    orbit = [(phi, 1.0/u)]
    while phi < phi_max and u > 0:
        # RK4 for u'' = 3u² + 1/L² - u
        def f(u, up):
            return 3*u*u + 1/L**2 - u
        k1u, k1up = dudphi, f(u, dudphi)
        k2u, k2up = dudphi+0.5*dphi*k1up, f(u+0.5*dphi*k1u, dudphi+0.5*dphi*k1up)
        k3u, k3up = dudphi+0.5*dphi*k2up, f(u+0.5*dphi*k2u, dudphi+0.5*dphi*k2up)
        k4u, k4up = dudphi+dphi*k3up, f(u+dphi*k3u, dudphi+dphi*k3up)
        u += dphi/6*(k1u + 2*k2u + 2*k3u + k4u)
        dudphi += dphi/6*(k1up + 2*k2up + 2*k3up + k4up)
        phi += dphi
        if u > 0:
            orbit.append((phi, 1.0/u))
    return orbit

# 水星轨道模拟 — 用 GR 修正的有效势法
# Binet 方程: u'' + u = 3Mu² + M/L² (取 GM=1)
# 圆轨道条件: u_c(1 - 3u_c) = 1/L²
# 选 L²=20 → u_c ≈ 0.06 (r_c ≈ 16.7)
# 从近日点出发: u0=0.08 (r=12.5), du/dφ=0
L_sq = 20.0
u0 = 0.08  # 近日点: r_min = 1/0.08 = 12.5
dphi = 0.0005
phi_max = 8 * math.pi

u, du = u0, 0.0
phi = 0.0
orbit_r = []
orbit_phi = []
while phi < phi_max and 0 < u < 1.0:
    orbit_r.append(1.0 / u)
    orbit_phi.append(phi)
    # RK4: u'' = 3u² + 1/L² - u
    k1u, k1uu = du, 3*u*u + 1/L_sq - u
    u2, du2 = u + 0.5*dphi*k1u, du + 0.5*dphi*k1uu
    k2u, k2uu = du2, 3*u2*u2 + 1/L_sq - u2
    u3, du3 = u + 0.5*dphi*k2u, du + 0.5*dphi*k2uu
    k3u, k3uu = du3, 3*u3*u3 + 1/L_sq - u3
    u4, du4 = u + dphi*k3u, du + dphi*k3uu
    k4u, k4uu = du4, 3*u4*u4 + 1/L_sq - u4
    u  += dphi/6 * (k1u + 2*k2u + 2*k3u + k4u)
    du += dphi/6 * (k1uu + 2*k2uu + 2*k3uu + k4uu)
    phi += dphi

# 找近日点 (r 的局部最小值)
perihelia = []
for i in range(2, len(orbit_r) - 2):
    if orbit_r[i] < orbit_r[i-1] and orbit_r[i] < orbit_r[i+1] and \
       orbit_r[i] < orbit_r[i-2] and orbit_r[i] < orbit_r[i+2]:
        perihelia.append(orbit_phi[i])

print("=== Schwarzschild 轨道近日点进动 ===")
print(f"角动量 L²={L_sq} (GM=1 单位)")
print(f"轨道点数: {len(orbit_r)}, r 范围: {min(orbit_r):.2f} – {max(orbit_r):.2f}")
if len(perihelia) >= 2:
    for j in range(len(perihelia)):
        print(f"  第{j+1}个近日点: φ = {perihelia[j]:.4f} rad = {math.degrees(perihelia[j]):.2f}°")
    delta = perihelia[1] - perihelia[0]
    prec_deg = math.degrees(delta - 2*math.pi)
    print(f"\n  相邻近日点角间距: Δφ = {delta:.6f} rad = {math.degrees(delta):.4f}°")
    print(f"  进动量/圈: {prec_deg:.4f}° (牛顿应为 0)")
    print(f"\n→ GR 效应: 近日点每圈多转 {prec_deg:.4f}°")
    print(f"→ 水星实际: 43″/百年 ≈ {43/3600:.5f}°/世纪 (弱场极小但精确测量)")
else:
    print(f"  仅找到 {len(perihelia)} 个近日点（轨道可能未完整振荡）")
```

### 6.2 宇宙距离阶梯

```python
"""
宇宙距离阶梯: 不同尺度用不同方法测距。
从视差(近邻恒星)到Ia超新星(宇宙学距离)。
"""
import math

pc = 3.086e16  # 1 秒差距 (米)
ly = 9.461e15  # 1 光年 (米)

methods = [
    ("雷达测距", 1e-3, 0.01, "AU"),
    ("三角视差", 0.01, 1000, "pc", "Gaia卫星精度"),
    ("主序星拟合", 1000, 10000, "pc", "光谱+HR图"),
    ("造父变星", 1e4, 5e7, "pc", "周光关系(Hubble用此发现膨胀)"),
    ("Tully-Fisher", 1e7, 1e8, "pc", "旋涡星系"),
    ("Ia超新星", 1e8, 2e9, "pc", "标准烛光(发现暗能量!)"),
    ("红移", 2e9, 1e10, "pc", "宇宙学距离(Hubble定律)"),
]

print("=== 宇宙距离阶梯 ===")
print(f"{'方法':>14} {'范围(pc)':>20} {'原理':>30}")
for item in methods:
    name, d_min, d_max = item[0], item[1], item[2]
    unit = item[3]
    note = item[4] if len(item) > 4 else ""
    if d_max < 1e6:
        rng = f"{d_min:.0f} – {d_max:.0f}"
    elif d_max < 1e9:
        rng = f"{d_min:.0e} – {d_max:.0e}"
    else:
        rng = f"{d_min:.0e} – {d_max:.0e}"
    print(f"{name:>14} {rng:>20} {note:>30}")

print(f"\n→ 每种方法覆盖约3-4个数量级")
print(f"→ 相邻方法有重叠区 → 交叉校准")
print(f"→ Ia超新星是发现加速膨胀的关键(1998, Perlmutter/Schmidt/Riess)")
print(f"→ Gaia卫星将视差精度推到 μas → 重塑近距离阶梯")

# Hubble 常数与宇宙年龄
H0 = 67.4  # km/s/Mpc
H0_SI = H0 * 1000 / (pc * 1e6)  # 转换为 1/s
t_H = 1.0 / H0_SI  # Hubble 时间
t_H_Gyr = t_H / (365.25*24*3600*1e9)

print(f"\n=== Hubble 常数与宇宙年龄 ===")
print(f"H₀ = {H0} km/s/Mpc")
print(f"Hubble 时间 1/H₀ = {t_H_Gyr:.1f} Gyr")
print(f"(实际宇宙年龄 ~13.8 Gyr, 比 1/H₀ 略短, 因 ΛCDM 修正)")
```

---

## 7. 习题集

### 基础题（Schutz / Carroll 前半）

**P8.1** 证明 Minkowski 度规 $\eta_{\mu\nu} = \text{diag}(-1,1,1,1)$ 的 Christoffel 符号全为零，因此 Riemann 张量为零（平直时空）。

**P8.2** 在地球表面（$r = R_\oplus$），计算引力时间膨胀效应。一个钟在海平面比在珠穆朗玛峰顶（8848 m）慢多少？

> **答案**：$\Delta\tau/\tau \approx gh/c^2 \approx 10^{-12}$，积累约 $3\times 10^{-5}$ 秒/年（GPS 卫星必须修正此效应）。

### 中级题（Carroll 中段）

**P8.3**（测地线）从 Schwarzschild 度规出发，推导球对称时空中的测地线方程（Binet 方程形式 $u'' + u = 3Mu^2 + M/L^2$）。对比牛顿轨道方程。

**P8.4**（近日点进动）利用 GR 修正的轨道方程，计算水星近日点进动率。给定水星轨道参数：半长轴 $a=0.387$ AU，偏心率 $e=0.206$。

> **答案**：$\Delta\phi = 6\pi GM_\odot/[c^2 a(1-e^2)] \approx 0.103''$/圈 = $43''$/百年。

**P8.5**（光线偏折）计算星光经过太阳边缘的偏折角。

> **答案**：$\delta\theta = 4GM_\odot/(c^2 R_\odot) \approx 1.75''$。1919 年 Eddington 日食观测首次验证。

### 挑战题（Weinberg / ETH 考试级别）

**P8.6**（Friedmann 方程）从 Einstein 场方程出发推导 Friedmann 方程。证明纯物质平坦宇宙的年龄 $t_0 = 2/(3H_0)$，而含 $\Lambda$ 的平坦宇宙年龄更大。

**P8.7**（黑洞热力学）Schwarzschild 黑洞的 Hawking 温度 $T_H = \hbar c^3/(8\pi GMk_B)$。计算：(a) 太阳质量黑洞的 $T_H$；(b) 它通过 Hawking 辐射蒸发的时间。

> **答案**：(a) $T_H \approx 6\times 10^{-8}$ K（极冷！远低于 CMB 的 2.7 K，所以实际上在吸收而非蒸发）。(b) $t_{\text{evap}} \sim 10^{67}$ 年（远超宇宙年龄）。

**P8.8**（引力波功率）利用四极矩公式计算两个等质量黑洞（各 $30\,M_\odot$）在合并前一刻（轨道半径 $\sim 6GM/c^2$）的引力波功率，并与宇宙所有恒星光度比较。

> **提示**：峰值功率 $\sim 10^{49}$ W，超过可观测宇宙所有恒星的总光度 $\sim 10^{40}$ W 约 $10^9$ 倍。

---

## 8. 不足与延伸

### 本主题的局限

1. **GR 与量子力学不兼容**：GR 是经典理论（连续的时空），量子力学是离散的。在 Planck 尺度（$10^{-35}$ m）两者必然冲突，但目前没有公认的量子引力理论。弦理论和圈量子引力是两个候选，但均无实验验证。

2. **奇点问题**：Schwarzschild 解在 $r=0$ 有曲率发散（奇点），大爆炸也有初始奇点。奇点是 GR 失效的信号——在该处量子引力效应必须介入。

3. **暗物质和暗能量的本质未知**：我们只知道它们通过引力效应存在（星系旋转曲线、宇宙膨胀加速），但不知道它们是什么。这是现代物理学最大的未解之谜之一。

4. **Hubble 争议**：不同方法测得的 $H_0$ 有 $5\sigma$ 的差异（CMB: 67.4 km/s/Mpc vs 造父-超新星阶梯: 73-74 km/s/Mpc）。这可能预示超出 ΛCDM 的新物理。

5. **宇宙学原理的检验**：FLRW 度规假设大尺度均匀各向同性。虽然 CMB 高度支持，但宇宙大尺度结构（巨洞、星系长城）的异常程度仍在研究中。

### 延伸方向

| 方向 | 课程/教材 |
|------|----------|
| 量子引力 | Rovelli *Quantum Gravity* /弦理论 |
| 黑洞热力学 | Wald *General Relativity* |
| 宇宙学 | Dodelson *Modern Cosmology* / Mukhanov |
| 引力波物理 | Maggiore *Gravitational Waves* |
| 数值相对论 | Baumgarte & Shapiro *Numerical Relativity* |

### ETH 特色注记

ETH 的广义相对论传承是独一无二的——因为 **Albert Einstein 在 ETH 开始了他的相对论之旅**。1896-1900 年 Einstein 在 ETH（当时的联邦理工学院）学习，期间他培养了对物理直觉和数学工具的双重重视（尽管他当时的数学成绩并非顶尖）。1912 年 Einstein 返回 ETH 任教授，与同学 Marcel Grossmann 合作，掌握了广义相对论所需的黎曼几何——这段合作发生在 ETH 的物理楼里。

ETH 的 Hill Building（物理学系大楼）保存着 Einstein 的手稿遗产。ETH 的广义相对论课不仅传授 Carroll 教材的技术内容，更是一种精神传承——在 Einstein 曾经思考时空几何的同一所大学里学习弯曲时空。ETH 物理系的引力物理组活跃在 LIGO/Virgo 引力波天文学、EHT 黑洞成像、以及暗能量/暗物质宇宙学的前沿。ETH 参与了未来 LISA（空间引力波探测器）和 Einstein Telescope（第三代地面引力波探测器）的规划——Einstein 在 ETH 开始的引力故事，正在被 ETH 的后继者们续写。

---

> **上一主题**：[07 粒子物理](../topic07-particle-nuclear/particle-nuclear.md)
>
> **Phase 2 完成**：数学方法 → 固体物理 → 粒子物理 → 广义相对论与宇宙学，构成高级物理 + ETH 特色方向。ETH 物理系 Phase 1（力学/电磁/量子/统计）+ Phase 2（数学方法/固体/粒子/GR）共 8 主题，覆盖 ETH 物理本科 + 研究生核心。


---

## 🎯 费曼式入口（白话版）

> **一句话解释**：广义相对论与宇宙学研究「时空本身如何被物质弯曲，弯曲的时空又如何指挥物质运动」——引力不是力，是几何；宇宙不是静态舞台，是会膨胀、会演化、有起点的实体。
>
> **生活类比**：把时空想象成一张**绷紧的蹦床**。放一个保龄球（恒星），蹦床凹下去；滚过一个小弹珠（行星），它会沿凹槽打转——这不是「引力拉弹珠」，是弹珠在弯曲表面上走「最直」的路（测地线）。Einstein 顿悟：**物质告诉时空如何弯曲，时空告诉物质如何运动**（Wheeler 的总结）。
>
> **反直觉发现（啊哈时刻）**：
> - **引力让钟变慢，不是「感觉慢」**：GPS 卫星每天快 38 μs——不修正的话定位每天漂移 10 km，是相对论的日常应用。
> - **黑洞不是「洞」**：是被事件视界包裹的时空区域，光也无法逃；2019 EHT 拍到 M87* 黑洞剪影，2022 拍到银心 Sgr A*。
> - **宇宙在加速膨胀**：1998 年超新星观测发现膨胀在加速（2011 诺奖），需要「暗能量」——至今没人懂它是什么。
> - **引力波 = 时空涟漪**：2015 年 LIGO 首次直接探测到 13 亿光年外两个黑洞并合发出的引力波，时空真的在「振动」。
> - **宇宙有起点（138 亿年前）**：哈勃发现星系退行 → 反推必有 Big Bang；CMB 是宇宙 38 万岁时的「婴儿照片」。
> - **哈勃危机**：用超新星测宇宙膨胀速度得 73 km/s/Mpc，用 CMB 得 67.5——差 5σ，可能颠覆 ΛCDM 宇宙学。

---

## 🔗 衔接：从哪来，到哪去

### ▶ 前置
- **力学（01）的拉格朗日**：测地线方程 = 弯曲时空里的 Euler-Lagrange 方程。
- **狭义相对论**（01 主题末）：Minkowski 几何 + 张量 → 推广到弯曲流形。
- **数学方法（05）**：微分几何（度规、联络、曲率张量、张量分析）是 GR 的全部语言。

### ⚡ 旧框架的危机
1. **牛顿引力「瞬时超距」**：与狭义相对论（信息不超光速）矛盾——需要场论化的引力。
2. **水星近日点进动异常**：牛顿力学漏掉每世纪 43 角秒——Einstein 用 GR 精确补上，第一次验证。
3. **宇宙学常数问题**：Einstein 1917 加 Λ 让宇宙静态，哈勃 1929 发现膨胀后他称之为「一生最大错误」——但 1998 年暗能量让 Λ 复活。

### 🆕 新框架的危机
- **奇点定理**（Penrose-Hawking）：广义相对论预言时空奇点（黑洞内、Big Bang），但奇点处理论自身失效——需要量子引力。
- **量子引力缺失**：弦论、圈量子引力、AdS/CFT 都未给出可检验预言——21 世纪物理最大悬案。
- **暗物质 + 暗能量未识**：占宇宙 95% 的成分未在标准模型 + GR 中得到解释。
- **哈勃危机**：早期 vs 晚期宇宙测 $H_0$ 差 5σ——可能需要新物理（早期暗能量、新中微子种类、修改引力）。

### 🚀 后续（最前沿）
| 方向 | 状态 |
|------|------|
| LISA 空间引力波探测器 | 2024.01 ESA 立项，2035 发射 |
| Einstein Telescope | 2025 选址，2035 运行 |
| 量子引力理论 | 弦论 / LQG / 全息对偶——仍无定论 |
| 暗能量 spectroscopy (DESI) | 2024 数据指向 evolving dark energy |

---

## 🏭 理论联系实际：5 个应用

1. **GPS 卫星授时修正**：相对论效应（速度 + 引力）合计 +38 μs/天，不修正每天漂移 ~10 km——GR 进入每个人口袋。
2. **LIGO / Virgo / KAGRA 引力波天文学**：2015 首测，至今 100+ 事件；ETH 物理系参与 LIGO 数据分析，用黑洞并合测量哈勃常数、检验广义相对论。
3. **黑洞成像（EHT）**：2019 M87*、2022 Sgr A*——事件视界望远镜用全球射电望远镜合成地球级口径，ETH 参与欧洲数据处理。
4. **卫星重力测量（GRACE/GOCE）**：用卫星轨道精度测量地球引力场变化，监测地下水流失、冰川融化——GR 在气候科学中的应用。
5. **全球导航、深空探测**：JWST 在日地 L2 halo 轨道（三体限制问题 + GR 修正）；未来 LISA 编队用激光干涉测空间引力波。

---

## 🔬 最新研究前沿（2024-2026）

1. **DESI 暗能量光谱巡天（DR1/DR2）**（2024.04 / 2024.11）：BAO 测量强烈倾向「演化型暗能量」（$w_0w_a$CDM），相对 ΛCDM 偏离 ~2.5-3.9σ——若属实，暗能量不是宇宙常数，宇宙结局（大撕裂 vs 大冻结）需重写。ETH 宇宙学组参与数据分析。
2. **JWST 早期宇宙星系异常**（2024-2025）：JADES、CEERS 巡天在 $z>10$ 发现超预期质量、超亮星系，挑战 ΛCDM 结构形成时间表——「JWST 早期星系危机」是 2024-2025 最热宇宙学争议。
3. **哈勃危机持续（5σ）**（2024-2025）：SH0ES（Riess 等）Cepheid 校准给出 $H_0\approx 73$，Planck CMB 给出 67.5；2024 TRGB、JAGB、MASER 多种独立「阶梯」都支持晚期高值——新物理（早期暗能量、修改引力）的窗口持续打开。
4. **脉冲星计时阵列与超大质量黑洞双星**（2023-2024）：NANOGrav、EPTA、PPTA 2023 宣布引力波背景；2024 后续搜索识别出候选超大质量黑洞双星系统，ETH 参与欧洲 EPTA + Parkes 数据分析——多频段引力波天文学时代来临。
5. **LISA 任务正式立项**（2024.01.25 ESA）：空间激光干涉引力波探测器，将探测毫赫兹频段（超大质量黑洞并合、极端质量比旋进、银河系内双星）；ETH 是 LISA Consortium 核心成员，2035 发射将打开全新频窗。Einstein Telescope（第三代地面）2025 进入选址阶段，瑞士 / 欧洲南北两处候选。

---

## 🗺️ 学习 Roadmap（ETH 路径）

### ETH 课程编号
- **402-3001-00L General Relativity**（MSc，Carroll / Wald 路线）
- **402-9305-00L Astroparticle Physics**（暗物质 / 早期宇宙）
- **402-9116-00L Cosmology**（MSc，Dodelson / Mukhanov 路线）
- **402-0826-00L Gravitational Waves**（对接 LIGO / LISA）

### 14 周学习节奏
| 阶段 | 内容 | 知识检查 |
|------|------|----------|
| W1-3 微分几何 | 流形、度规、联络、曲率张量 | 写出 Riemann 张量的对称性。 |
| W4-6 Einstein 场方程 | 等效原理、测地线、$G_{\mu\nu}=8\pi G T_{\mu\nu}$ | 推出 Schwarzschild 度规。 |
| W7-9 黑洞物理 | 事件视界、Penrose 图、霍金辐射、热力学 | 解释为什么黑洞有熵 $S=kA/4$。 |
| W10-12 宇宙学 | FLRW 度规、哈勃律、CMB、Big Bang 核合成 | 推出临界密度 $\rho_c=3H^2/(8\pi G)$。 |
| W13-14 引力波 + 暗宇宙 | 线性化引力、引力波偏振、暗物质 / 暗能量 | 解释 LIGO 如何测出 10⁻¹⁸ m 形变。 |

### 费曼检验
- 能用一张 A4 推出 Schwarzschild 度规 → GR 过关。
- 能讲清「引力不是力，是时空几何」 → 直觉过关。
- 能列出哈勃危机的 3 种新物理解释 → 可进宇宙学前沿。


### 🌌 ETH-Einstein 传承
ETH 的广义相对论课不止传授技术——它在 **Einstein 1896-1900 求学、1912-1914 任教**的同一所大学里讲授。1912 年 Einstein 与同学 Marcel Grossmann 在 ETH 物理楼合作，掌握了 GR 所需的黎曼几何。今天 ETH 的引力组（参与 LIGO、EHT、LISA、ET）在续写 Einstein 的引力故事——**广义相对论的未来在 ETH 继续**。
