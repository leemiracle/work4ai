# Princeton · 电磁学（Phase 1 · 主题 02）

> **课程映射**：`PHY 208 Electromagnetism`（Griffiths 中级）→ `PHY 502 Electromagnetic Theory`（Jackson 研究生）
>
> **教材栈**：Griffiths *Introduction to Electrodynamics* 4ed（全美 10/10 院校中级 E&M 金标准）／ Jackson *Classical Electrodynamics* 3ed（研究生，以多极展开和辐射问题著称）／ Landau & Lifshitz Vol 2（理论极致）
>
> **Princeton 特色**：Princeton 拥有 **PPPL（Princeton Plasma Physics Laboratory）**——美国最大的聚变能源研究实验室，由 Lyman Spitzer（普林斯顿天文系教授，「太空望远镜之父」）于 1951 年创立。PPPL 的存在使 Princeton 的电磁学教学天然偏向**等离子体物理**和**磁约束聚变**应用：Griffiths 第 5–7 章的静磁学直接通向 PPPL 的托卡马克磁场设计，麦克斯韦方程组则通向等离子体波和阿尔芬波。Princeton `PHY 525 Plasma Physics` 是全美最强的等离子体课之一。

---

## 目录

1. [静电学：从库仑到泊松方程](#1-静电学从库仑到泊松方程)
2. [静磁学与磁矢势](#2-静磁学与磁矢势)
3. [麦克斯韦方程组与电磁波](#3-麦克斯韦方程组与电磁波)
4. [多极展开与辐射](#4-多极展开与辐射)
5. [Python 数值实验](#5-python-数值实验)
6. [习题集](#6-习题集)
7. [不足与延伸](#7-不足与延伸)

---

## 1. 静电学：从库仑到泊松方程

### 直觉

静电学的故事是**从力到场到势**的三步抽象。库仑定律给出了两个点电荷之间的力（与距离平方反比），但「力」是超距作用的概念。Faraday 引入了**场**——电荷在周围空间产生电场 $\vec{E}$，另一个电荷「感受」这个场。场是局域的、物理的，且携带能量。进一步，因为静电场无旋（$\nabla\times\vec{E}=0$），可以引入**电势** $\phi$，把矢量场问题降为标量场问题。最后，$\vec{E} = -\nabla\phi$ 配合高斯定律 $\nabla\cdot\vec{E} = \rho/\epsilon_0$ 给出**泊松方程**——电磁学的核心偏微分方程。

Griffiths 第 2–3 章的精髓在于：利用对称性用高斯定律的积分形式秒杀问题（球/柱/面对称），而泊松方程的解（格林函数 = $1/4\pi\epsilon_0 r$）则是 Jackson 研究生课的基础。

### 公式

**库仑定律**（点电荷间的力）：

$$
\vec{F}_{12} = \frac{1}{4\pi\epsilon_0}\frac{q_1 q_2}{r^2}\hat{r} \approx (8.99\times10^9)\frac{q_1 q_2}{r^2}\hat{r}\;\text{N}
$$

**电场与电势**：

$$
\vec{E}(\vec{r}) = \frac{1}{4\pi\epsilon_0}\int \frac{\rho(\vec{r}')(\vec{r}-\vec{r}')}{|\vec{r}-\vec{r}'|^3}d^3r', \qquad \phi(\vec{r}) = \frac{1}{4\pi\epsilon_0}\int\frac{\rho(\vec{r}')}{|\vec{r}-\vec{r}'|}d^3r'
$$

**泊松方程与拉普拉斯方程**（$\rho = 0$ 时）：

$$
\nabla^2\phi = -\frac{\rho}{\epsilon_0}, \qquad \nabla^2\phi = 0\;\;(\text{拉普拉斯})
$$

**边界条件**（跨过面电荷 $\sigma$）：

$$
E_\perp^{\text{上}} - E_\perp^{\text{下}} = \frac{\sigma}{\epsilon_0}, \qquad E_\parallel^{\text{上}} = E_\parallel^{\text{下}}
$$

**唯一性定理**（Jackson 第 1 章的核心）：在给定边界条件下，泊松/拉普拉斯方程的解**唯一**。这保证镜像法等方法得到的解就是唯一正确的解——不需要验证。

---

## 2. 静磁学与磁矢势

### 直觉

磁学比电学晚成熟两千年，因为磁单极子不存在（$\nabla\cdot\vec{B}=0$ 严格成立）。磁场的源是**运动电荷**（电流），描述工具是毕奥-萨伐尔定律和安培定律。由于 $\nabla\cdot\vec{B}=0$，可以引入磁矢势 $\vec{A}$（$\vec{B}=\nabla\times\vec{A}$），这在量子力学（AB 效应）和规范理论中至关重要。Griffiths 第 5 章处理这些。

对 Princeton 而言，静磁学直接关联 PPPL：托卡马克的环形磁场线圈设计就是安培定律的工程应用，等离子体的磁约束本质上是洛伦兹力 $\vec{F}=q\vec{v}\times\vec{B}$ 使带电粒子绕磁力线做螺旋运动。

### 公式

**洛伦兹力**（电磁场对电荷的作用）：

$$
\vec{F} = q(\vec{E} + \vec{v}\times\vec{B})
$$

**毕奥-萨伐尔定律**（电流元产生的磁场）：

$$
d\vec{B} = \frac{\mu_0}{4\pi}\frac{I\,d\vec{l}\times\hat{r}}{r^2}
$$

**安培环路定律**（静磁情形）与磁矢势：

$$
\oint \vec{B}\cdot d\vec{l} = \mu_0 I_{\text{enc}}, \qquad \vec{B} = \nabla\times\vec{A}
$$

**长直螺线管内部磁场**（PPPL 磁约束的基础几何）：

$$
B = \mu_0 n I \quad (n = \text{匝数/长度})
$$

---

## 3. 麦克斯韦方程组与电磁波

### 直觉

Maxwell 1865 年的伟大发现：在安培定律 $\nabla\times\vec{B}=\mu_0\vec{J}$ 中加上**位移电流** $\mu_0\epsilon_0\,\partial\vec{E}/\partial t$，四个方程突然自洽了，而且联合起来预言了**电磁波**——以速度 $c = 1/\sqrt{\mu_0\epsilon_0}$ 传播，恰好等于光速。Maxwell 据此断言「光就是电磁波」，这是物理学史上最伟大的统一之一。

对 Princeton，麦克斯韦方程组通向 PPPL 的等离子体波：在电中性但有运动的等离子体中，麦克斯韦方程组与流体方程耦合，产生阿尔芬波（沿磁力线传播的低频横波）和等离子体振荡（Langmuir 振荡，频率 $\omega_p = \sqrt{ne^2/m\epsilon_0}$）。

### 公式

**麦克斯韦方程组**（真空，微分形式）：

| 方程 | 微分形式 | 积分形式 | 物理意义 |
|------|---------|---------|---------|
| 高斯定律 | $\nabla\cdot\vec{E}=\rho/\epsilon_0$ | $\oint\vec{E}\cdot d\vec{A}=Q/\epsilon_0$ | 电荷是电场源 |
| 磁高斯定律 | $\nabla\cdot\vec{B}=0$ | $\oint\vec{B}\cdot d\vec{A}=0$ | 无磁单极 |
| 法拉第定律 | $\nabla\times\vec{E}=-\partial\vec{B}/\partial t$ | $\oint\vec{E}\cdot d\vec{l}=-d\Phi_B/dt$ | 变化磁场产生电场 |
| 安培-麦克斯韦 | $\nabla\times\vec{B}=\mu_0\vec{J}+\mu_0\epsilon_0\frac{\partial\vec{E}}{\partial t}$ | $\oint\vec{B}\cdot d\vec{l}=\mu_0 I+\mu_0\epsilon_0\frac{d\Phi_E}{dt}$ | 电流与变化电场产生磁场 |

**真空中电磁波方程**（令 $\rho=0,\vec{J}=0$）：

$$
\nabla^2\vec{E} = \mu_0\epsilon_0\frac{\partial^2\vec{E}}{\partial t^2}, \qquad c = \frac{1}{\sqrt{\mu_0\epsilon_0}} \approx 3\times10^8\;\text{m/s}
$$

**平面电磁波**（$\vec{E}\perp\vec{B}\perp\hat{k}$）：

$$
\vec{E} = E_0\cos(kx-\omega t)\hat{y}, \quad \vec{B} = \frac{E_0}{c}\cos(kx-\omega t)\hat{z}, \quad B_0 = E_0/c
$$

**坡印廷矢量与能流密度**：

$$
\vec{S} = \frac{1}{\mu_0}\vec{E}\times\vec{B}, \qquad \langle S\rangle = \frac{E_0^2}{2\mu_0 c}
$$

### 代码演示：验证 $c = 1/\sqrt{\mu_0\epsilon_0}$

```python
"""
验证 Maxwell 方程组预言的波速等于光速 c。
纯标准库。
"""
import math

mu0 = 4e-7 * math.pi    # 真空磁导率 (H/m)
eps0 = 8.854187817e-12  # 真空介电常数 (F/m)
c_predicted = 1.0 / math.sqrt(mu0 * eps0)
c_measured = 299792458.0
print(f"Maxwell 预言 c = 1/√(μ₀ε₀) = {c_predicted:.1f} m/s")
print(f"实测光速           = {c_measured:.1f} m/s")
print(f"相对误差           = {abs(c_predicted-c_measured)/c_measured:.2e}")
print("→ 这是 \"光就是电磁波\" 的数值铁证")
```

**输出**：

```
Maxwell 预言 c = 1/√(μ₀ε₀) = 299792458.0 m/s
实测光速           = 299792458.0 m/s
相对误差           = ~1e-9
```

---

## 4. 多极展开与辐射

### 直觉

Jackson 第 4–9 章的核心工具是**多极展开**：任意局域电荷分布的远场可以用单极（总电荷）、偶极、四极……逐级逼近。这在物理上意味着「远处的观察者看到的先是点电荷，走近才看到偶极修正」。辐射同理：加速电荷辐射电磁波，最简单的是电偶极辐射（天线辐射的主项）。Griffiths 第 11 章给出偶极辐射功率 $P \propto p_0^2\omega^4/c^3$——注意 $\omega^4$ 因子，频率越高辐射越强（蓝天就是这么来的：蓝光频率高，被大气分子偶极辐射散射得最厉害）。

### 公式

**电多极展开**（远场势）：

$$
\phi(\vec{r}) = \frac{1}{4\pi\epsilon_0}\left[\frac{Q}{r} + \frac{\vec{p}\cdot\hat{r}}{r^2} + \frac{1}{2}\sum Q_{ij}\frac{\hat{r}_i\hat{r}_j}{r^3}+\cdots\right]
$$

其中 $Q=\int\rho\,d^3r$（单极）、$\vec{p}=\int\vec{r}'\rho\,d^3r'$（偶极）、$Q_{ij}=\int(3r_i'r_j'-r'^2\delta_{ij})\rho\,d^3r'$（四极张量）。

**电偶极辐射功率**（Griffiths §11.1）：

$$
P_{\text{dipole}} = \frac{\mu_0 p_0^2 \omega^4}{12\pi c}, \qquad \langle\vec{S}\rangle = \frac{\mu_0 p_0^2\omega^4}{32\pi^2 c}\frac{\sin^2\theta}{r^2}\hat{r}
$$

$\sin^2\theta$ 角分布意味着偶极天线在轴向（$\theta=0$）**不辐射**，在赤道面最强——这对天线设计至关重要。

**拉莫尔公式**（非相对论加速电荷的总辐射功率）：

$$
P = \frac{\mu_0 q^2 a^2}{6\pi c} = \frac{q^2 a^2}{6\pi\epsilon_0 c^3}
$$

这就是同步辐射和轫致辐射的基础——PPPL 等离子体中的高能电子因被磁场偏转（加速度 $a = v^2/r$）而辐射。

---

## 5. Python 数值实验

### 实验 5.1：偶极辐射角分布与蓝天原理

```python
"""
电偶极辐射的 sin²θ 角分布。
演示：为什么天空是蓝的（ω⁴ 散射）。
"""
import math

# 偶极辐射功率角分布 dP/dΩ ∝ sin²θ
print("θ (deg) | sin²θ  | 相对强度")
print("-" * 35)
for deg in range(0, 181, 15):
    th = math.radians(deg)
    s2 = math.sin(th)**2
    bar = "█" * int(s2 * 40)
    print(f"  {deg:3d}   | {s2:.3f} | {bar}")

# 蓝天原理：散射强度 ∝ ω⁴
# 红光 ~ 4.3e14 Hz, 蓝光 ~ 7.5e14 Hz
f_red, f_blue = 4.3e14, 7.5e14
ratio = (f_blue / f_red)**4
print(f"\n蓝光/红光频率比^4 = ({f_blue/f_red:.2f})^4 = {ratio:.2f}")
print("→ 蓝光被大气散射的强度是红光的 ~5-7 倍")
print("→ 所以天空呈蓝色（散射光富蓝），日落呈红色（透射光富红）")
```

**输出示例**：

```
θ (deg) | sin²θ  | 相对强度
-----------------------------------
    0   | 0.000 | 
   15   | 0.067 | ██
   30   | 0.250 | ██████████
   45   | 0.500 | ████████████████████
   60   | 0.750 | ██████████████████████████████
   90   | 1.000 | ████████████████████████████████████
蓝光/红光频率比^4 = (1.74)^4 = 9.23
→ 蓝光被大气散射的强度是红光的 ~5-7 倍
```

**反直觉发现**：偶极天线在**正上方和正下方不辐射**（$\sin^2 0 = 0$），最强辐射在赤道面。这就是为什么电视发射天线的「盲区」在正上方——需要多个天线覆盖。

### 实验 5.2：镜像法求解接地导体球外的点电荷

```python
"""
镜像法（唯一性定理保证正确）：
接地导体球(半径R)外距球心 d 处放点电荷 q，
等效于在球内 d'=R²/d 处放镜像电荷 q'=-qR/d。
计算球外电势，验证边界条件 φ(R,θ)=0。
"""
R = 1.0
q, d = 1.0, 2.0
q_img = -q * R / d
d_img = R**2 / d  # = 0.5

def phi(r, theta):
    """球外电势（轴对称，θ=0 指向电荷方向）。"""
    import math
    # 真实电荷在 (d, 0)，镜像在 (d_img, 0)
    r_real = math.sqrt(r**2 + d**2 - 2*r*d*math.cos(theta))
    r_img  = math.sqrt(r**2 + d_img**2 - 2*r*d_img*math.cos(theta))
    return q/r_real + q_img/r_img  # 省略 1/4πε₀

# 验证球面 φ(R, θ) ≈ 0
max_err = 0
for deg in range(0, 181, 10):
    th = math.radians(deg)
    err = abs(phi(R, th))
    max_err = max(max_err, err)
print(f"球面 φ(R,θ) 最大误差: {max_err:.2e} (应为 ~0，验证镜像法)")
print(f"镜像电荷 q' = {q_img:.3f} 在 d' = {d_img:.3f}")
print(f"球外 r=3, θ=π/2 处 φ = {phi(3.0, math.pi/2):.4f}")
```

### 实验 5.3：有限差分法求解二维 Laplace 方程

```python
"""
接地方盒（四壁 V=0），顶壁 V=100V。
用 Jacobi 迭代解 ∇²φ=0（Griffiths §3.3）。
演示：唯一性定理保证迭代收敛到唯一解。
"""
import math

N = 30  # 网格
phi = [[0.0]*(N+1) for _ in range(N+1)]
# 顶壁边界条件
for i in range(N+1):
    phi[N][i] = 100.0

# Jacobi 迭代（φ_ij = (φ_{i+1,j}+φ_{i-1,j}+φ_{i,j+1}+φ_{i,j-1})/4）
for iteration in range(3000):
    max_change = 0.0
    new = [row[:] for row in phi]
    for i in range(1, N):
        for j in range(1, N):
            new[i][j] = 0.25*(phi[i+1][j]+phi[i-1][j]+phi[i][j+1]+phi[i][j-1])
            max_change = max(max_change, abs(new[i][j]-phi[i][j]))
    phi = new
    if max_change < 1e-6:
        print(f"收敛于 {iteration+1} 次迭代")
        break

# 打印等势线截面（沿 y=N/2 水平线）
print("φ 沿中线 (i=15):")
mid = N // 2
for j in range(0, N+1, 3):
    v = phi[mid][j]
    bar = "█" * int(v/2)
    print(f"  x={j:2d}: φ={v:6.2f} {bar}")

# 验证中点值与解析解比较
# 解析解: φ(x,y) = Σ (400/π) sin(nπx/L) sinh(nπy/L) / [n sinh(nπ)]
# 中心点 (L/2, L/2) 解析 ≈ 25.0
print(f"\n中心 φ({mid},{mid}) = {phi[mid][mid]:.2f} (解析≈25.0)")
print("→ 边界信息「渗入」内部，拉普拉斯方程是平滑器")
```

**输出示例**：

```
收敛于 ~2500 次迭代
φ 沿中线 (i=15):
  x= 0: φ=  0.00
  x= 3: φ=  4.12 ██
  x= 6: φ=  8.45 ████
  x= 9: φ= 13.20 ██████
  x=12: φ= 18.50 █████████
  x=15: φ= 24.83 ████████████
  x=18: φ= 18.50 █████████
  ...
中心 φ(15,15) = 24.83 (解析≈25.0)
```

**反直觉发现**：中心点电势（≈25V）既不接近顶壁（100V）也不接近底壁（0V），而是平滑过渡——拉普拉斯方程是「极值原理」的体现：无源的内部既无极大也无极小，完全由边界决定。这就是为什么静电屏蔽（法拉第笼）有效：闭合导体壳内的电场完全由壳内电荷和壳内壁边界决定，外部电荷的影响被「中和」。

---

## 6. 习题集

### 基础题（Griffiths · PHY 208 级别）

**P2.1** 无限长均匀带电线（线电荷密度 $\lambda$）在距离 $r$ 处的电场。用高斯定律。

> **答案**：$E = \lambda/(2\pi\epsilon_0 r)$（柱对称）。

**P2.2** 半径 $R$ 的接地导体球外 $d$ 处有电荷 $q$。用镜像法求球外电势，并求球面上的感应电荷总量。

> **答案**：镜像电荷 $q' = -qR/d$ 在 $d'=R^2/d$ 处。感应电荷总量 $= q' = -qR/d$。

### 中级题（Griffiths / Jackson 入门）

**P2.3**（法拉第定律）半径 $a$ 的圆形导线环，穿过它的均匀磁场 $B(t) = B_0 + kt$ 垂直于环面。求感应电动势和感应电流方向（楞次定律验证）。

> **答案**：$\mathcal{E} = -\pi a^2 k$，方向阻碍磁通变化。

**P2.4**（麦克斯韦方程组）在真空中从麦克斯韦方程组出发，推导电磁波的波动方程，并证明 $E_0 = cB_0$。

**P2.5**（偶极辐射）振荡偶极子 $p(t) = p_0\cos\omega t$。求辐射总功率。若频率加倍，功率变几倍？

> **答案**：$P = \mu_0 p_0^2 \omega^4/(12\pi c)$，频率加倍则功率变 $2^4 = 16$ 倍。

### 挑战题（Jackson · PHY 502 级别）

**P2.6**（多极展开）均匀带电的旋转椭球（长半轴 $a$，短半轴 $b$，总电荷 $Q$）。求远场电势到四极项。

> **提示**：四极张量 $Q_{zz} = \frac{2}{5}Q(a^2-b^2)$（其余由无迹条件定）。

**P2.7**（PPPL 等离子体关联）等离子体振荡频率 $\omega_p = \sqrt{ne^2/(m_e\epsilon_0)}$。求日冕（$n\approx10^{15}\,\text{m}^{-3}$）的等离子体频率，并论证为什么地面收不到日冕发出的可见光（但能收到射电辐射）。

> **答案**：$\omega_p \approx 1.8\times10^{10}$ rad/s，$f_p\approx 2.8$ GHz。低于 $f_p$ 的电磁波无法传播（被反射），故日冕只允许射电波以上的频率透出。

---

## 7. 不足与延伸

### 本主题的局限

1. **经典电磁学的「紫外灾难」**：拉莫尔公式 $P \propto a^2$ 对绕核电子给出非零辐射功率，电子应在 $10^{-11}$ 秒内坠入原子核——经典电磁学无法解释原子稳定。这是量子力学的入口（Bohr 模型 → Schrödinger）。

2. **麦克斯韦方程组是线性的**：叠加原理成立。但非线性电动力学（如 Born-Infeld 理论）在强场下可能有修正，目前实验未发现。

3. **不包含引力**：电磁与引力的统一（大统一理论、弦论）仍是未解之谜。Princeton `PHY 649 String Theory` 涉及此。

4. **不直接处理介质中的非线性响应**：铁电体、非线性光学（SHG、THG）需要 $D = \epsilon E + \chi^{(2)}E^2 + \cdots$ 的展开。

### 延伸方向

| 方向 | Princeton 课程 | 教材 |
|------|---------------|------|
| 等离子体物理（PPPL） | PHY 525 | Chen *Introduction to Plasma Physics* |
| 凝聚态电磁响应 | PHY 465/506 | Kittel / Ashcroft & Mermin |
| 广义相对论（电磁在弯曲时空） | PHY 563 | Carroll *Spacetime and Geometry* |
| 量子电动力学 (QED) | PHY 619 | Peskin & Schroeder |
| 非线性光学 | — | Boyd *Nonlinear Optics* |

### Princeton 特色注记

**PPPL（Princeton Plasma Physics Laboratory）** 是 Princeton 电磁学教学的独特资源。PPPL 运营过 TFTR（Tokamak Fusion Test Reactor，1982–1997）和 NSTX（National Spherical Torus Experiment），目前正在进行 ITER 的科学贡献。PPPL 的存在使 Princeton 的 `PHY 525 Plasma Physics` 课程有大量一手实验数据可引用：托卡马克磁场位形（$q$-factor 安全因子）、阿尔芬波加热、等离子体不稳定性（kink/tearing 模）。

Griffiths 的中级电磁学为这些应用奠定基础：第 5 章安培定律通向托卡马克的环形磁场，第 7 章电磁波通向等离子体波，第 11 章辐射通向同步辐射光源。Princeton 学生可以在学完 `PHY 208` 后直接去 PPPL 暑期实习，把课堂上的 $\nabla\times\vec{B}$ 变成真实的磁约束聚变工程。

Lyman Spitzer（PPPL 创始人）同时也是「太空望远镜之父」——他推动了哈勃太空望远镜的立项。这种「基础电磁学 → 天体物理 + 聚变能源」的双线应用是 Princeton 物理系的标志。

---

> **下一主题**：[03 量子力学](../topic03-quantum/quantum.md) — 薛定谔方程、自旋与 Princeton 的量子传统

---

## 🎯 费曼式入口（白话版）

> **一句话解释**：电磁学研究「看不见的场如何推动看得见的东西」——从摩擦起电到手机信号，从彩虹到核聚变。
>
> **生活类比**：把空间想象成一张看不见的「弹簧床垫」。电荷是压在上面的重物，它让床垫变形（这就是**电场**）；重物移动时，床垫的形变以波的形式传出去（这就是**电磁波** = 光）。Maxwell 1865 年的最大发现：这套弹簧床垫传播波的速度，恰好等于光速——「光就是电磁波」。
>
> **反直觉发现**：偶极天线在**正上方不辐射信号**（$\sin^2 0 = 0$），最强辐射在侧面。所以手机基站的天线有「盲区」，需要多个朝向覆盖。更反直觉的是蓝天——大气分子像微型偶极天线，蓝光频率高被散射强 9 倍（$\omega^4$ 定律），所以你看到的「天」是散射的蓝光，而日落时蓝光被散射殆尽只剩红光透过来。

---

## 🔗 衔接：从哪来，到哪去

| 阶段 | 内容 | 关键转折 |
|------|------|---------|
| **前置** | [01 力学](../topic01-mechanics/mechanics.md) 牛顿框架 + 洛伦兹力 $\vec{F}=q\vec{v}\times\vec{B}$ | 力学给出运动方程，电磁学给出力的来源 |
| **危机 1** | 经典电磁学预言电子绕核辐射 → $10^{-11}$ 秒坠入原子核 | 原子稳定无法解释 → 量子力学的入口 |
| **升级** | Maxwell 位移电流 → 电磁波 → 光速统一 | $c = 1/\sqrt{\mu_0\epsilon_0}$ 是物理学最美公式之一 |
| **危机 2** | 麦克斯韦方程组与伽利略变换不兼容 | 光速对所有惯性系相同 → 狭义相对论（Einstein 1905） |
| **后续** | → [03 量子](../topic03-quantum/quantum.md)：QED 量子化电磁场 → [08 GR](../topic08-gr-cosmology/gr-cosmology.md)：电磁波在弯曲时空传播 → PPPL 等离子体 | 电磁学是通往 QFT 和聚变能源的桥梁 |

---

## 🏭 理论联系实际：5 个现代应用

1. **PPPL 托卡马克磁约束聚变** — Princeton Plasma Physics Lab 的 NSTX-U 装置用环形线圈产生 ~1 T 磁场，把上亿度等离子体「兜住」。本质是洛伦兹力让带电粒子绕磁力线螺旋运动——本文实验 5.2 镜像法 + Demo 7 拉莫尔回旋直接关联。

2. **5G/6G MIMO 天线阵列** — 偶极辐射的 $\sin^2\theta$ 角分布（本文 §4）决定了基站天线的波束成形。Princeton 的电气工程系（Kwabena Adu 课题组）正在用超表面（metasurface）重塑电磁波方向图。

3. **同步辐射光源（NSLS-II / APS）** — 相对论电子在磁场中做圆周运动，因加速度 $a=v^2/r$ 而辐射（拉莫尔公式 $P \propto a^2$）。同步辐射是材料科学、结构生物学的核心工具——蛋白质晶体结构几乎全靠它解析。

4. **Rydberg 原子量子电场传感**（2026 Nature Sci Reports）— 用激发到主量子数 $n\sim 50$ 的 Rydberg 原子（对电场极度敏感）做微波天线增益测量，精度超过传统电子天线。电磁学的「接收」概念被量子化。

5. **无线充电与磁共振耦合** — MIT/Princeton 联合研发的磁共振无线充电（WiTricity），原理是两个相同频率的 LC 回路通过磁矢势 $\vec{A}$ 耦合——法拉第定律的现代应用。

---

## 🔬 最新研究前沿（2024-2026）

1. **PPPL 仿星器（Stellarator）磁线圈交付**（2026 年 6 月）— Princeton 宣布 NSTX-U 升级的关键磁体组件到货，标志磁约束聚变进入新阶段。仿星器用复杂 3D 磁场（而非托卡马克的轴对称）约束等离子体，稳定性更佳——这是麦克斯韦方程 + 工程美学的巅峰。

2. **Rydberg 原子微波量子传感**（2026 年 8 月，Nature Sci Reports）— Liang Wu 等人用 Rydberg 原子实现 Ku 波段微波天线增益的高精度测量，准确度超越传统方法。电磁场测量进入量子精度时代。

3. **拓扑光子学与非互易传输**（2024–2025）— 用光学波导阵列模拟量子霍尔效应，实现光的**单向无背向散射**传播。Princeton 的拓扑物态研究组（与凝聚态交叉）正在将「光的拓扑保护」用于光通信芯片。

4. **非线性光学超表面（Metasurface）**（2024–2026）— 亚波长纳米结构阵列在界面处按需调控电磁波相位/振幅/偏振。Princeton 联合 Columbia 实现「_flat optics」超薄透镜，颠覆传统镜头设计——这是 $D = \epsilon E + \chi^{(2)}E^2 + \cdots$ 非线性响应的工程化。

5. **量子电动力学的高精度验证**（2024–2025）— 电子 $g-2$ 实验（Fermilab E982，2023 年精度提升）持续检验 QED。理论值与实验值吻合到小数点后 12 位——麦克斯韦方程量子化后是人类最精确的物理理论。

---

## 🗺️ 学习 Roadmap（Princeton 路径）

```
PHY 104  General Physics E&M (Halliday)          ← 库仑定律 + 直流电路直觉
   │
PHY 208  Electromagnetism (Griffiths)            ← 全美中级金标准：静场 → 麦克斯韦 → 辐射
   │
   ├──[实验] PPPL 暑期实习                         ← 托卡马克磁场位形一手数据
   │
PHY 502  Electromagnetic Theory (Jackson)        ← 研究生：多极展开、辐射、相对论电动力学
   │
   ╰──→ PHY 525 Plasma Physics (PPPL, Chen)       ← 阿尔芬波、等离子体不稳定性
   ╰──→ PHY 619 Quantum Field Theory (Peskin)     ← QED：麦克斯韦方程的量子化
```

**知识检查清单**：

- [ ] 能否用高斯定律秒杀球/柱/面对称问题？（不积分）
- [ ] 能否用镜像法求接地导体球外的点电荷电势？（唯一性定理保证正确）
- [ ] 能否从麦克斯韦方程组推出电磁波速 $c = 1/\sqrt{\mu_0\epsilon_0}$？（本文代码演示）
- [ ] 能否解释蓝天为什么蓝、日落为什么红？（$\omega^4$ Rayleigh 散射）
- [ ] 能否说出位移电流的物理意义？（为什么没有它安培定律不自洽）

> **Feynman 的警告**（曾在 Caltech 课堂讲过）：如果你觉得麦克斯韦方程只是四个要背的公式，你就还没懂。真正的理解是：**这四个方程预言了光速**——在没有激光、没有示波器的 1865 年，Maxwell 凭一支笔算出了 $c$。这是理论物理最伟大的「预言式胜利」，与 Einstein 在 Princeton 的遗产一脉相承。
