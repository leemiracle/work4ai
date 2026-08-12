# Harvard 广义相对论与宇宙学 — Phys 210 / 212 / 211r

> **课程**：Phys 210 (General Theory of Relativity) · Phys 212 (Physical Cosmology) · Phys 211r (Black Holes from A to Z)
> **教材**：Carroll *Spacetime and Geometry: An Introduction to General Relativity* (2004) · Dodelson *Modern Cosmology* 2ed (2020)
> **一手来源**：[Harvard 2025-26 SPS Guide](https://www.physics.harvard.edu/resource/sps-guide-physics-2025-2026) + [Dvorkin Teaching Page](https://dvorkin.physics.harvard.edu/teaching-and-outreach/)（2026-08 核实）

> ⚠️ **核实说明**：用户原文指定 "Phys 210/232"。经核实，**Phys 232 = Advanced Classical Electromagnetism**（Jackson 经典电动力学），并非宇宙学。宇宙学研究生课为 **Phys 212 (Physical Cosmology)**，由 Cora Dvorkin 教授自 2016 年起开设并持续教授至今（经其个人教学主页确认）。Phys 211r (Black Holes) 与 GR 密切相关。

---

## 🎓 Harvard 特色：从张量到暗物质的完整链路

Harvard 2025-26 SPS Guide 对 Phys 210 的描述（原文）：

> *"General relativity is the final course a student takes in classical theory. Curved spacetime, black holes, an expanding universe, the whole nine yards... Long, tedious calculations of quantities involving rank-4 tensors are a staple of the coursework."*

> *"All the effort is worth it in the end, as the course provides a great introduction to general relativity."*

**Harford 的 GR/Cosmology 三层梯队**：

| 课程 | 定位 | 教材 | 核心内容 |
|------|------|------|---------|
| **Phys 210** | 本科/研初 GR | Carroll | 微分几何 → Einstein 方程 → 黑洞 |
| **Phys 212** | 研究生宇宙学 | Dodelson | FRW 宇宙 → CMB → 暗物质/暗能量 |
| **Phys 211r** | 黑洞专题 | Wald/Wald-dict | 黑洞热力学、信息悖论、AdS/CFT |

**Harford 宇宙学/引力组**：
- **Cora Dvorkin**：暗物质粒子物理、CMB 精确分析
- **Avi Loeb**（前 Harvard）：第一代恒星/黑洞、系外行星
- **Andrew Strominger**：弦论黑洞、黑洞信息悖论

| 教材 | 定位 | 特色 |
|------|------|------|
| **Carroll** | Phys 210 主教材 | 几何直觉清晰、推导适中、章节连贯 |
| **Dodelson** | Phys 212 主教材 | 现代 CMB/LSS 分析框架、计算导向 |
| **Wald** | 211r 参考 | 严格数学物理、黑洞热力学权威 |

---

## 第一部分：微分几何基础（Carroll Ch.1-3）

### 1.1 流形与坐标

**流形** $M$：局部看起来像平坦空间 $\mathbb{R}^n$ 的空间。每点有局部坐标系 $x^\mu$。

**坐标变换**：$x^\mu \to x'^\mu(x)$

### 1.2 张量与度规

**度规张量** $g_{\mu\nu}$：定义时空间隔

$$ds^2 = g_{\mu\nu}\,dx^\mu\,dx^\nu$$

| 时空 | 度规 | $g_{\mu\nu}$ |
|------|------|-------------|
| Minkowski（平直） | $\eta_{\mu\nu} = \text{diag}(-1,1,1,1)$ | 符号差 (-,+,+,+) |
| Schwarzschild（黑洞外部） | $ds^2 = -(1-\frac{2M}{r})dt^2 + (1-\frac{2M}{r})^{-1}dr^2 + r^2d\Omega^2$ | 球对称 |
| FRW（宇宙） | $ds^2 = -dt^2 + a(t)^2[dr^2/(1-kr^2) + r^2d\Omega^2]$ | 均匀各向同性 |

**张量升降指标**：$V^\mu = g^{\mu\nu}V_\nu$, $g^{\mu\alpha}g_{\alpha\nu} = \delta^\mu_\nu$

### 1.3 协变导数与测地线

普通偏导数在弯曲空间中不是张量——需要加上**联络**修正：

$$\nabla_\mu V^\nu = \partial_\mu V^\nu + \Gamma^\nu_{\mu\lambda}V^\lambda$$

**Christoffel 联络**（Levi-Civita 联络，由度规唯一确定）：

$$\boxed{\Gamma^\lambda_{\mu\nu} = \frac{1}{2}g^{\lambda\sigma}(\partial_\mu g_{\nu\sigma} + \partial_\nu g_{\mu\sigma} - \partial_\sigma g_{\mu\nu})}$$

**测地线方程**（弯曲时空中的"直线"=自由落体轨迹）：

$$\frac{d^2x^\lambda}{d\tau^2} + \Gamma^\lambda_{\mu\nu}\frac{dx^\mu}{d\tau}\frac{dx^\nu}{d\tau} = 0$$

> 💡 **直觉**：自由落体（如宇航员漂浮在空间站里）就是"惯性运动"——它们沿测地线运动，感受不到力。引力不是"力"，而是时空弯曲的表现。苹果落地不是被"拉"下来的，而是跟着弯曲时空的测地线走。

### 1.4 曲率张量

**Riemann 曲率张量**（衡量时空弯曲程度）：

$$R^\rho_{\quad\sigma\mu\nu} = \partial_\mu\Gamma^\rho_{\nu\sigma} - \partial_\nu\Gamma^\rho_{\mu\sigma} + \Gamma^\rho_{\mu\lambda}\Gamma^\lambda_{\nu\sigma} - \Gamma^\rho_{\nu\lambda}\Gamma^\lambda_{\mu\sigma}$$

**缩约**：
- **Ricci 张量**：$R_{\mu\nu} = R^\lambda_{\quad\mu\lambda\nu}$
- **标量曲率**：$R = g^{\mu\nu}R_{\mu\nu}$

**关键判据**：Riemann 张量 $= 0$ ↔ 时空平直（可全局找到 Minkowski 坐标）。

---

## 第二部分：Einstein 场方程（Carroll Ch.4-5）

### 2.1 等效原理

**Einstein 等效原理**：在足够小的时空区域内，引力效应可以通过选择局部惯性系（自由下落系）完全消除。

→ 物理定律在局部惯性系中取狭义相对论形式。

**推论**：引力不是"力"，而是时空弯曲的几何效应。

### 2.2 Einstein 场方程

$$\boxed{G_{\mu\nu} \equiv R_{\mu\nu} - \frac{1}{2}Rg_{\mu\nu} + \Lambda g_{\mu\nu} = 8\pi G\,T_{\mu\nu}}$$

| 量 | 含义 |
|----|------|
| $G_{\mu\nu}$ | Einstein 张量（几何 = 曲率） |
| $\Lambda$ | 宇宙学常数（暗能量） |
| $T_{\mu\nu}$ | 能量-动量张量（物质 = 源） |

> **Wheeler 的经典总结**：*"Spacetime tells matter how to move; matter tells spacetime how to curve."*

### 2.3 能量-动量张量

完美流体的 $T_{\mu\nu}$：

$$T_{\mu\nu} = (\rho + p)u_\mu u_\nu + pg_{\mu\nu}$$

其中 $\rho$ 是能量密度，$p$ 是压强，$u^\mu$ 是四维速度。

**能量守恒**（Bianchi 恒等式 $\nabla^\mu G_{\mu\nu} = 0$ 的推论）：

$$\nabla_\mu T^{\mu\nu} = 0$$

### 2.4 作用量原理（Einstein-Hilbert 作用量）

$$S = \frac{1}{16\pi G}\int (R - 2\Lambda)\sqrt{-g}\,d^4x + S_{\text{matter}}$$

对度规 $g^{\mu\nu}$ 变分 → Einstein 方程。

> 🔗 **连接**（Phys 151 经典力学）：这里的变分法与拉格朗日力学完全平行。$\sqrt{-g}$ 是弯曲时空的"体积元"。

---

## 第三部分：Schwarzschild 解与黑洞（Carroll Ch.5-6, Phys 211r）

### 3.1 Schwarzschild 度规

球对称真空解（Birkhoff 定理保证唯一性）：

$$\boxed{ds^2 = -\left(1-\frac{2GM}{rc^2}\right)c^2dt^2 + \left(1-\frac{2GM}{rc^2}\right)^{-1}dr^2 + r^2d\Omega^2}$$

**Schwarzschild 半径**（事件视界）：

$$r_s = \frac{2GM}{c^2}$$

| 天体 | 质量 | $r_s$ |
|------|------|-------|
| 太阳 | $1 M_\odot$ | 3.0 km |
| 地球 | $1 M_\oplus$ | 9.0 mm |
| 银河系中心黑洞 (Sgr A*) | $4\times 10^6 M_\odot$ | $1.2\times 10^7$ km |

### 3.2 引力红移

光从引力势 $\Phi_1$ 处发射，在 $\Phi_2$ 处接收：

$$\frac{\Delta\nu}{\nu} = \frac{\Phi_1 - \Phi_2}{c^2} \approx -\frac{GM}{c^2}\left(\frac{1}{r_1}-\frac{1}{r_2}\right)$$

> 光从强引力场（恒星表面）爬出时损失能量 → 频率降低（红移）。这不是 Doppler 效应——光子"攀登"出引力势井消耗了能量。

### 3.3 事件视界与黑洞

在 $r = r_s$ 处：
- $g_{tt} = 0$, $g_{rr} = \infty$（坐标奇点，非物理）
- 任何信号无法从 $r < r_s$ 传出（因果视界）

**自由落体的固有时间有限**，但远处观察者看到落体者"冻结"在视界上——时间膨胀 $\to \infty$。

> 🔑 **反直觉**：掉入黑洞的宇航员不会在视界处感到任何异常（等效原理！），但一旦越过视界，$r$ 变成类时坐标——只能向中心运动，无法回头。

### 3.4 黑洞热力学（Bekenstein-Hawking）

**Hawking 温度**：

$$T_H = \frac{\hbar c^3}{8\pi GMk_B}$$

**Bekenstein-Hawking 熵**：

$$\boxed{S_{\text{BH}} = \frac{k_B c^3 A}{4G\hbar} = \frac{k_B A}{4\ell_P^2}}$$

其中 $A$ 是事件视界面积，$\ell_P = \sqrt{G\hbar/c^3} \approx 1.6\times 10^{-35}$ m 是 Planck 长度。

> 🔑 **深刻疑难**：黑洞熵正比于**面积**，而非体积——这与所有已知量子系统矛盾（通常熵 $\propto$ 体积）。这暗示量子引力的自由度"生活"在边界上（holographic principle），是弦论 AdS/CFT 对偶的物理动机。

---

## 第四部分：FRW 宇宙学（Carroll Ch.8, Dodelson Ch.1-2）

### 4.1 宇宙学原理

在足够大尺度上（>100 Mpc），宇宙是**均匀各向同性**的。

→ 时空度规唯一确定为 **FRW（Friedmann-Robertson-Walker）形式**：

$$ds^2 = -dt^2 + a(t)^2\left[\frac{dr^2}{1-kr^2} + r^2(d\theta^2 + \sin^2\theta\,d\phi^2)\right]$$

| 参数 | 含义 |
|------|------|
| $a(t)$ | 尺度因子（宇宙大小随时间变化） |
| $k$ | 空间曲率（+1 球面 / 0 平直 / -1 双曲） |

### 4.2 Friedmann 方程

将 FRW 度规代入 Einstein 方程，得到宇宙演化的核心方程：

$$\boxed{H^2 \equiv \left(\frac{\dot{a}}{a}\right)^2 = \frac{8\pi G}{3}\rho - \frac{k}{a^2} + \frac{\Lambda}{3}}$$

$$\frac{\ddot{a}}{a} = -\frac{4\pi G}{3}(\rho + 3p) + \frac{\Lambda}{3}$$

其中 Hubble 参数 $H = \dot{a}/a$，当前值 $H_0 \approx 67$–$73$ km/s/Mpc。

### 4.3 物态方程与宇宙组分

不同物质成分的物态方程 $p = w\rho$：

| 成分 | $w$ | $\rho(a)$ | 行为 |
|------|-----|-----------|------|
| 物质（暗物质+重子） | 0 | $\propto a^{-3}$ | 稀释（体积膨胀） |
| 辐射（光子+相对论中微子） | 1/3 | $\propto a^{-4}$ | 稀释更快（红移） |
| 暗能量（宇宙学常数） | $-1$ | $\propto a^0$（常数！） | 不稀释 → 主导未来 |
| 曲率 | $-1/3$ | $\propto a^{-2}$ | 空间曲率贡献 |

**当前宇宙能量构成**（Planck 2018 数据）：

| 成分 | 占比 |
|------|------|
| 暗能量 | 68% |
| 暗物质 | 27% |
| 普通物质（重子） | 5% |
| 辐射 | $\sim 0.01\%$ |

> 🔑 **反直觉发现**：我们熟悉的"物质"（原子）只占宇宙总能量的 5%！95% 是我们完全不了解的暗物质和暗能量。这是物理学21世纪最大的未解之谜。

### 4.4 宇宙热历史

| 红移/时间 | 温度 | 事件 |
|-----------|------|------|
| $t \sim 10^{-36}$ s | $T \sim 10^{28}$ K | 暴胀（推测） |
| $t \sim 10^{-6}$ s | $T \sim 10^{13}$ K | 夸克-强子相变 |
| $t \sim 1$ s | $T \sim 10^{10}$ K | 中微子退耦 |
| $t \sim 3$ min | $T \sim 10^9$ K | 原初核合成（BBN） |
| $t \sim 380000$ yr | $T \sim 3000$ K | 复合（CMB 释放） |
| $t \sim 10^9$ yr | — | 第一代恒星 |
| $t \sim 13.8$ Gyr | $T = 2.725$ K | 现在 |

---

## 第五部分：暗物质（Dodelson Ch.5, Dvorkin 研究）

### 5.1 暗物质的证据

**旋转曲线**（Zwicky 1933, Rubin 1970s）：星系外围恒星速度不随 $r$ 下降：

$$v(r) = \sqrt{\frac{GM(r)}{r}} \to \text{const} \implies M(r) \propto r$$

→ 必须有看不见的质量（暗物质晕）。

**Bullet Cluster**（Clowe 2006）：两个星系团碰撞。X 射线（普通物质）在碰撞中心滞留，而引力透镜显示的质量中心在前方——**暗物质与暗物质几乎不相互作用**，直接穿过。

### 5.2 暗物质候选者

| 候选 | 质量 | 探测方法 |
|------|------|---------|
| WIMP（弱相互作用大质量粒子） | GeV–TeV | 直接探测（液氙）、对撞机 |
| 轴子（Axion） | $\mu$eV–meV | 超导谐振腔（ADMX） |
| 惰性中微子 | keV | X 射线谱线 |
| 原初黑洞 | $10^{-16}$–$10^2 M_\odot$ | 微引力透镜 |

> **Harvard 特色**：Dvorkin 教授的研究专注于利用 CMB 小尺度结构和星系形成约束暗物质粒子的性质（如 WIMP 湮灭截面、暗物质-重子散射）。

---

## 第六部分：CMB 与暴胀（Dodelson Ch.7-10）

### 6.1 宇宙微波背景辐射

CMB 是宇宙 38 万岁时"最后散射面"发出的光，今天被红移到微波波段：

$$T_{\text{CMB}} = 2.7255 \pm 0.0006\,\text{K}$$

**均匀性**：各方向温度差 $\Delta T/T \sim 10^{-5}$——宇宙在最后散射时极度均匀。

> **视界疑难**：CMB 在天空中相隔 >1° 的区域**从未因果接触过**（光传播时间不够），为何温度如此均匀？→ **暴胀**的动机。

### 6.2 暴胀理论

**宇宙暴胀**（Guth 1980, Linde 1982）：极早期宇宙经历指数膨胀：

$$a(t) \propto e^{Ht}, \quad H \approx \text{const}$$

持续 $\Delta t \sim 60$ e-folds（$\ln(a_f/a_i) > 60$）。

**解决的疑难**：
1. **视界疑难**：暴胀前因果区域被指数拉伸 → CMB 均匀性
2. **平坦性疑难**：暴胀使 $\Omega = 1$ 精确成立 → $k \approx 0$
3. **磁单极疑难**：暴胀稀释了拓扑缺陷的密度

### 6.3 CMB 各向异性与功率谱

CMB 的微小温度涨落用功率谱 $C_l$ 描述：

$$\langle a_{lm}^* a_{l'm'}\rangle = C_l\,\delta_{ll'}\delta_{mm'}$$

**声学峰**（Doppler 峰）：功率谱在 $l \sim 200$ 出现第一个峰——对应最后散射面的声学视界角尺度。

**峰的位置 → 几何**：$l_{\text{peak}} \approx 200$ → $\Omega_{\text{total}} \approx 1$（空间平直）。

> 🔑 **反直觉**：从 CMB 的"温度地图"中可以读出宇宙的年龄（13.8 Gyr）、成分比例（暗能量 68%）、空间曲率（平直）等——信息密度极高！Planck 卫星（2018）测量的参数精度优于 1%。

---

## 📝 习题精选

### 习题 1（测地线）

证明 Minkowski 时空（$g_{\mu\nu} = \eta_{\mu\nu}$）中所有 Christoffel 符号为零，测地线退化为直线。

### 习题 2（Schwarzschild 光子轨道）

光子在 Schwarzschild 度规中做圆轨道运动的半径是多少？

> **答案**：$r_{\text{photon}} = 3M$（光子球）。比事件视界 $r_s = 2M$ 更外。

### 习题 3（Friedmann 方程推导）

从 FRW 度规和完美流体 $T_{\mu\nu}$ 出发，推导 Friedmann 方程。

> **提示**：计算非零 Christoffel 符号 → Riemann/Ricci 张量 → Einstein 张量 → 与 $T_{\mu\nu}$ 匹配。

### 习题 4（物质-辐射平等）

已知当前 $\Omega_m \approx 0.3$, $\Omega_r \approx 5\times 10^{-5}$。求物质-辐射平等时的红移 $z_{\text{eq}}$。

> **答案**：$\rho_m \propto (1+z)^3$, $\rho_r \propto (1+z)^4$。平等时 $(1+z_{\text{eq}}) = \Omega_m/\Omega_r \approx 3400$。

### 习题 5（Hawking 温度）

计算太阳质量黑洞的 Hawking 温度和蒸发寿命。

> **答案**：$T_H \approx 6\times 10^{-8}$ K（远低于 CMB 温度！→ 黑洞在吸收而非蒸发）。蒸发时间 $\sim 10^{67}$ 年。

---

## 💻 Python 代码

### 代码 1：Schwarzschild 测地线与光子偏折

```python
"""
Schwarzschild 度规中的光子轨迹: 引力透镜偏折角
验证广义相对论的经典预言
零依赖纯 Python
"""
import math

def deflection_angle_gr(b, M=1.0):
    """
    光线偏折角 (GR, 一阶近似): δ = 4GM/(bc²)
    取 G=c=1, M=1 → δ = 4/b
    b = 瞄准参数 (impact parameter)
    """
    return 4.0 * M / b

def deflection_angle_newton(b, M=1.0):
    """牛顿力学预测: δ = 2GM/(bc²) (Soldner 1801)"""
    return 2.0 * M / b

# 太阳引力偏折
M_sun_in_m = 1.477  # GM☉/c² (km), 即太阳的 Schwarzschild 半径/2 in km
# 实际 GM☉/c² = 1.477 km
R_sun_km = 696340   # 太阳半径 km
b_sun = R_sun_km / 1.477  # 以 GM/c² 为单位

print("=== 光线引力偏折: 太阳边缘 ===")
print(f"太阳引力半径 GM☉/c² = {1.477:.3f} km")
print(f"太阳半径 R☉ = {R_sun_km} km")
print(f"瞄准参数 b = R☉/(GM☉/c²) = {b_sun:.1f} (几何单位)\n")

delta_gr = deflection_angle_gr(b_sun)
delta_newton = deflection_angle_newton(b_sun)
delta_gr_arcsec = math.degrees(delta_gr) * 3600

print(f"GR 预测:    δ = 4M/b = {delta_gr:.6f} rad = {delta_gr_arcsec:.3f}″")
print(f"牛顿预测:   δ = 2M/b = {delta_gr_arcsec/2:.3f}″")
print(f"GR 是牛顿的 2 倍!")
print(f"实验值 (Eddington 1919): ~1.75″  ✓ 确认 GR\n")

# 测地线数值积分 (简化: 平面轨道, 用有效势)
def geodesic_dr(dt, r0, phi0, L, M=1.0, steps=10000):
    """
    光子 Schwarzschild 测地线数值积分
    有效势: (dr/dφ)² = r⁴/L² - r² + 2Mr³/L²
    L = 角动量参数 = b (瞄准参数) in 几何单位
    """
    r, phi = r0, phi0
    trajectory = [(r, phi)]
    dphi = 0.001
    for _ in range(steps):
        # dr/dφ from effective potential
        dr_dphi_sq = r**4 / L**2 - r**2 + 2*M*r**3 / L**2
        if dr_dphi_sq < 0:
            dr_dphi_sq = 0  # 转折点
        dr = -math.sqrt(dr_dphi_sq) * dphi  # 光子靠近黑洞
        r += dr
        phi += dphi
        trajectory.append((r, phi))
        if r < 2 * M:  # 越过视界
            break
        if phi > math.pi:  # 足够远
            break
    return trajectory

# 追踪一条掠过黑洞的光子
print("=== 光子轨迹 (瞄准参数 b=10M) ===")
traj = geodesic_dr(0.001, r0=100, phi0=0, L=10.0, M=1.0, steps=50000)
if traj:
    r_final, phi_final = traj[-1]
    # 总偏折 = φ_final - π (直线应该到 π)
    total_deflect = phi_final - math.pi
    print(f"初始 r=100M, 瞄准参数 b=10M")
    print(f"最终 φ = {math.degrees(phi_final):.1f}° (直线应为 180°)")
    print(f"偏折角 = {math.degrees(total_deflect):.2f}°")
    print(f"理论 4M/b = {math.degrees(4/10):.2f}° rad→{4/10:.4f} rad")
```

### 代码 2：Friedmann 方程数值积分

```python
"""
宇宙膨胀数值模拟: 不同物质组分的 a(t) 演化
零依赖纯 Python (RK4 积分)
"""
import math

# 宇宙学常数 (SI)
G = 6.674e-11
H0 = 2.27e-18  # Hubble 常数 (1/s), ~70 km/s/Mpc

def friedmann_rhs(a, params):
    """
    da/dt = a * H(a)
    H² = H₀² [Ω_r/a⁴ + Ω_m/a³ + Ω_k/a² + Ω_Λ]
    params = (Omega_r, Omega_m, Omega_k, Omega_Lambda)
    """
    Or, Om, Ok, OL = params
    H_sq = H0**2 * (Or/a**4 + Om/a**3 + Ok/a**2 + OL)
    return a * math.sqrt(max(H_sq, 0))

def rk4_integrate(a0, t0, t_end, params, dt=1e15):
    """RK4 积分 a(t)"""
    a, t = a0, t0
    result = [(t, a)]
    while t < t_end:
        k1 = friedmann_rhs(a, params)
        k2 = friedmann_rhs(a + 0.5*dt*k1, params)
        k3 = friedmann_rhs(a + 0.5*dt*k2, params)
        k4 = friedmann_rhs(a + dt*k3, params)
        a += dt * (k1 + 2*k2 + 2*k3 + k4) / 6
        t += dt
        result.append((t, a))
    return result

# 当前宇宙参数 (Planck 2018)
Omega_r = 9.2e-5   # 辐射
Omega_m = 0.315     # 物质 (暗+重子)
Omega_L = 0.685     # 暗能量
Omega_k = 1 - Omega_r - Omega_m - Omega_L  # 曲率 ≈ 0

params_now = (Omega_r, Omega_m, Omega_k, Omega_L)
# 纯物质宇宙 (无暗能量, Einstein 最初想法)
params_matter = (0, 1.0, 0, 0)
# 纯暗能量 (de Sitter)
params_deSitter = (0, 0, 0, 1.0)

t_end = 5e17  # ~16 Gyr
# 从 a=0.01 积分到未来

print("=== 宇宙膨胀模拟 a(t) ===")
print(f"H₀ = {H0:.2e} 1/s (≈ 70 km/s/Mpc)")
print(f"当前: Ω_m={Omega_m}, Ω_Λ={Omega_L}, Ω_r={Omega_r:.1e}\n")

# 标准模型: 从早期到现在
traj = rk4_integrate(0.001, 0, t_end, params_now, dt=5e14)
print(f"{'时间(Gyr)':>10} {'a(t)':>10} {'1+z':>10} {'主导成分':>12}")
print("-" * 48)
for i in range(0, len(traj), max(1, len(traj)//10)):
    t, a = traj[i]
    t_gyr = t / 3.156e16  # 秒 → Gyr
    z = 1/a - 1 if a > 0 else float('inf')
    # 判断主导
    rho_r = Omega_r / a**4
    rho_m = Omega_m / a**3
    rho_L = Omega_L
    dominant = "辐射" if rho_r > max(rho_m, rho_L) else ("物质" if rho_m > rho_L else "暗能量")
    print(f"{t_gyr:10.2f} {a:10.5f} {z:10.2f} {dominant:>12}")

# 比较: 三种宇宙的 a(t)
print("\n=== 三种宇宙模型比较 (t ≈ 现在) ===")
t_now = 4.35e17  # ~13.8 Gyr
for label, params in [("标准 ΛCDM", params_now), ("纯物质(Einstein)", params_matter), ("纯Λ(de Sitter)", params_deSitter)]:
    traj = rk4_integrate(0.001, 0, t_now, params, dt=5e14)
    a_now = traj[-1][1]
    print(f"  {label:>20}: a(t₀) = {a_now:.4f}")

print("\n结论:")
print("  1. 纯物质宇宙: a ∝ t^(2/3) (减速膨胀)")
print("  2. 纯暗能量: a ∝ e^(Ht) (指数加速膨胀)")
print("  3. ΛCDM: 辐射→物质→暗能量 三阶段演化")
```

### 代码 3：黑洞热力学

```python
"""
黑洞热力学: Hawking 温度, Bekenstein-Hawking 熵, 蒸发时间
零依赖纯 Python
"""
import math

# 物理常数
G = 6.674e-11
c = 2.998e8
hbar = 1.055e-34
k_B = 1.381e-23
M_sun = 1.989e30
ly = 9.461e15  # 光年 (m)

def hawking_temperature(M_kg):
    """T_H = ℏc³/(8πGMk_B)"""
    return hbar * c**3 / (8 * math.pi * G * M_kg * k_B)

def bh_entropy(M_kg):
    """S_BH = k_B c³ A / (4Gℏ), A = 4π r_s² = 16π G²M²/c⁴"""
    A = 16 * math.pi * G**2 * M_kg**2 / c**4
    l_P_sq = G * hbar / c**3  # Planck 长度²
    return k_B * A / (4 * l_P_sq)

def evaporation_time(M_kg):
    """t_evap ≈ 5120 π G²M³/(ℏc⁴)"""
    return 5120 * math.pi * G**2 * M_kg**3 / (hbar * c**4)

def schwarzschild_radius(M_kg):
    """r_s = 2GM/c²"""
    return 2 * G * M_kg / c**2

print("=== 黑洞热力学 ===\n")

# 不同质量的黑洞
cases = [
    ("人质量黑洞 (70kg)", 70),
    ("月球质量", 7.35e22),
    ("地球质量", 5.97e24),
    ("太阳质量", M_sun),
    ("Sgr A* (银心)", 4e6 * M_sun),
    ("M87* (EHT 拍摄)", 6.5e9 * M_sun),
]

print(f"{'类型':>24} {'M(kg)':>12} {'r_s':>14} {'T_H(K)':>14} {'S/k_B':>14} {'t_evap(yr)':>14}")
print("-" * 96)
for name, M in cases:
    rs = schwarzschild_radius(M)
    TH = hawking_temperature(M)
    S = bh_entropy(M) / k_B
    t_ev = evaporation_time(M) / (3.156e7)  # 秒→年
    # 格式化 r_s
    if rs < 0.01:
        rs_str = f"{rs*1e3:.2e}mm"
    elif rs < 1000:
        rs_str = f"{rs:.3f}m"
    else:
        rs_str = f"{rs/1000:.2e}km"
    # 格式化熵
    S_str = f"{S:.2e}" if S > 1e6 else f"{S:.1f}"
    # 格式化蒸发时间
    if t_ev > 1e20:
        t_str = f"{t_ev:.2e}"
    else:
        t_str = f"{t_ev:.2e}"
    print(f"{name:>24} {M:12.2e} {rs_str:>14} {TH:14.4e} {S_str:>14} {t_str:>14}")

print(f"\n=== 关键发现 ===")
print(f"1. T_H ∝ 1/M: 黑洞越重越冷 (太阳质量黑洞 T~10⁻⁸K)")
print(f"   → 比当前 CMB (2.725K) 冷得多, 正在吸收而非蒸发!")
print(f"2. S_BH ∝ M²: 熵极大 (太阳黑洞熵~10⁷⁷ k_B)")
print(f"   → 远超热力学系统, 暗示全息原理")
print(f"3. t_evap ∝ M³: 大黑洞蒸发极慢 (太阳黑洞~10⁶⁷年)")
print(f"   → 宇宙年龄才~10¹⁰年, 天体黑洞几乎不蒸发")

# Planck 质量
M_P = math.sqrt(hbar * c / G)
print(f"\nPlanck 质量: M_P = {M_P:.4e} kg = {M_P*c**2/1.602e-19/1e9:.4e} GeV")
print(f"Planck 长度: ℓ_P = {math.sqrt(G*hbar/c**3):.4e} m")
print(f"  → 量子引力在此尺度变得重要")
```

---

## 📚 Carroll vs Dodelson vs Wald

| 教材 | 定位 | 强项 | 弱项 |
|------|------|------|------|
| **Carroll** | Phys 210 主教材 | 几何直觉好、叙述流畅、难度适中 | 宇宙学部分较简略 |
| **Dodelson** | Phys 212 主教材 | CMB/LSS 分析框架现代、计算导向 | 需要先学 GR 基础 |
| **Wald** | 211r 参考 | 数学严谨、黑洞热力学权威 | 对入门太难、公式密集 |

**学习路径**：
1. **Carroll Ch.1-3**（微分几何）→ 建立几何语言
2. **Carroll Ch.4-6**（Einstein 方程 + Schwarzschild + 黑洞）→ 核心物理
3. **Carroll Ch.8**（宇宙学导论）→ FRW 基础
4. **Dodelson Ch.1-5**（宇宙学深化）→ 暗物质 + 结构形成
5. **Dodelson Ch.7-10**（CMB）→ 功率谱分析
6. **专题**（暴胀/黑洞信息）→ 最新文献

---

## 🔗 与其他课程的衔接

- **← Phys 15a/16（力学 + 狭义相对论）**：SR 是 GR 的前置
- **← Phys 151（分析力学）**：Lagrangian/变分法 → Einstein-Hilbert 作用量
- **← Phys 153（电磁学）**：张量分析、Maxwell 方程的协变形式
- **→ Phys 253a/b（量子场论）**：弯曲时空 QFT（Hawking 辐射）、AdS/CFT
- **→ Harvard 引力/宇宙学组**：Strominger（弦论黑洞）、Dvorkin（暗物质/CMB）

---

*完成日期：2026-08-12 | 课程编号经 Harvard 2025-26 SPS Guide + Dvorkin 教学主页一手核实（Phys 232 实为 Advanced Classical EM，宇宙学为 Phys 212 由 Dvorkin 教授自 2016 年起开设）*
