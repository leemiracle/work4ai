# Topic 08 — 广义相对论与宇宙学：时空与宇宙

> **Oxford MPhys · Year 3 General Relativity + Year 4 Cosmology**
> 教材：B. F. Schutz *A First Course in General Relativity* 2ed / M. P. Hobson, G. Efstathiou, A. N. Lasenby *General Relativity: An Introduction for Physicists* + S. Dodelson *Modern Cosmology*
> 覆盖：等效原理、张量与曲率、Einstein 场方程、Schwarzschild 与黑洞、FLRW 宇宙学、Friedmann 方程、热大爆炸

---

## 目录

1. [课程定位](#1-课程定位)
2. [等效原理与时空几何](#2-等效原理与时空几何)
3. [张量微积分与曲率](#3-张量微积分与曲率)
4. [Einstein 场方程](#4-einstein-场方程)
5. [Schwarzschild 解与黑洞](#5-schwarzschild-解与黑洞)
6. [宇宙学：FLRW 与 Friedmann 方程](#6-宇宙学flrw-与-friedmann-方程)
7. [反直觉实验 (Python)](#7-反直觉实验-python)
8. [Tutorial 习题](#8-tutorial-习题)
9. [局限与延伸阅读](#9-局限与延伸阅读)

---

## 1. 课程定位

Oxford 把 GR 分两段：Y3 学**广义相对论**（Schutz/Hobson，建立场方程与 Schwarzschild 解），Y4 选修**宇宙学**（Dodelson，FLRW 与现代观测宇宙学）。

| 年级 | 课程 | 教材 | 核心 |
|------|------|------|------|
| **Y3** | **General Relativity** | **Schutz Ch.1-10 / Hobson Ch.1-9** | **等效原理、张量、场方程、Schwarzschild** |
| Y4 | Cosmology | Dodelson Ch.1-4 / Hobson Ch.14 | FLRW、Friedmann、CMB、结构形成 |

> **Oxford 风格**：Hobson（Oxford 自家教授所著）专为物理系写——比数学系的 Wald 直观，比 Schutz 系统 Schutz 从几何（流形、度规）严格起步，Oxford 兼取两者：先建直觉（等效原理），再补张量（必要最小），落到场方程与经典解。

---

## 2. 等效原理与时空几何

### 2.1 等效原理 (Schutz Ch.2)

**弱等效原理**（Eötvös 实验 $\eta<10^{-15}$）：惯性质量 = 引力质量，**引力与加速度局域不可区分**。

**Einstein 等效原理**：在足够小的自由下落参考系内，物理定律退化为狭义相对论（无引力）。推论：引力 = **时空弯曲**。

> **直觉**：电梯自由下落时你「失重」——不是因为引力消失，而是你沿测地线运动（自由粒子轨迹）。引力不是「力」，而是时空几何。

### 2.2 度规与原时

时空间隔由**度规张量** $g_{\mu\nu}$ 描写：
$$
ds^2=g_{\mu\nu}\,dx^\mu dx^\nu
$$

**原时**（固有时，粒子自带的钟读数）：
$$
\boxed{\;d\tau^2=-\frac{ds^2}{c^2}\quad(\text{类时世界线 } ds^2<0)\;}
$$

自由粒子走**测地线**（原时极值路径）——弯曲时空中「直线」的推广。

**闵可夫斯基度规**（平直）：$\eta_{\mu\nu}=\mathrm{diag}(-1,+1,+1,+1)$。引力使 $g_{\mu\nu}$ 偏离 $\eta_{\mu\nu}$。

---

## 3. 张量微积分与曲率

### 3.1 协变导数 (Schutz Ch.3-4)

普通偏导在弯曲时空非张量。引入**协变导数**（含 Christoffel 记号 $\Gamma^\lambda_{\mu\nu}$）：
$$
\nabla_\nu V^\lambda=\partial_\nu V^\lambda+\Gamma^\lambda_{\nu\mu}V^\mu
$$
$$
\Gamma^\lambda_{\mu\nu}=\frac12 g^{\lambda\sigma}(\partial_\mu g_{\nu\sigma}+\partial_\nu g_{\mu\sigma}-\partial_\sigma g_{\mu\nu})
$$

测地线方程：$\frac{d^2x^\lambda}{d\tau^2}+\Gamma^\lambda_{\mu\nu}\frac{dx^\mu}{d\tau}\frac{dx^\nu}{d\tau}=0$。

### 3.2 Riemann 曲率张量

沿闭合回路平移矢量若改变，说明时空弯曲。Riemann 张量：
$$
R^\lambda_{\;\;\mu\nu\rho}V^\mu=(\nabla_\nu\nabla_\rho-\nabla_\rho\nabla_\nu)V^\lambda
$$

**关键判据**：$R^\lambda_{\;\;\mu\nu\rho}=0$ 当且仅当时空平直。曲率是引力的「真正」度量。

缩并得 **Ricci 张量** $R_{\mu\nu}=R^\lambda_{\;\;\mu\lambda\nu}$ 与**标曲率** $R=g^{\mu\nu}R_{\mu\nu}$。

---

## 4. Einstein 场方程

### 4.1 场方程 (Schutz Ch.5)

Einstein（1915）：
$$
\boxed{\;G_{\mu\nu}\equiv R_{\mu\nu}-\tfrac12 g_{\mu\nu}R=\frac{8\pi G}{c^4}T_{\mu\nu}\;}
$$

- 左边 $G_{\mu\nu}$：时空几何（曲率）。
- 右边 $T_{\mu\nu}$：物质-能量动量张量。

**口诀**：「物质告诉时空如何弯曲，时空告诉物质如何运动」（Wheeler）。

加入**宇宙学常数** $\Lambda$（暗能量）：
$$
R_{\mu\nu}-\tfrac12 g_{\mu\nu}R+\Lambda g_{\mu\nu}=\frac{8\pi G}{c^4}T_{\mu\nu}
$$

### 4.2 Schwarzschild 解的推导思路

对球对称真空（$T_{\mu\nu}=0$），解场方程得（见 §5）。这是检验 GR 的基石——水星近日点进动、光线偏折、引力时间延迟都来自它。

---

## 5. Schwarzschild 解与黑洞

### 5.1 Schwarzschild 度规 (Schutz Ch.9)

球对称质量 $M$ 外的真空解：
$$
\boxed{\;ds^2=-\left(1-\frac{r_s}{r}\right)c^2dt^2+\left(1-\frac{r_s}{r}\right)^{-1}dr^2+r^2d\Omega^2\;,\quad r_s=\frac{2GM}{c^2}\;}
$$

$r_s$ 是 **Schwarzschild 半径**（事件视界）。太阳 $r_s\approx3$ km，地球 $\approx9$ mm。

### 5.2 引力红移与时间膨胀

静止观察者的原时 $d\tau=\sqrt{1-r_s/r}\,dt$。从 $r$ 处发出的光子在无穷远观察者处的频率：
$$
\frac{\nu_{\text{obs}}}{\nu_{\text{emit}}}=\sqrt{1-\frac{r_s}{r_{\text{emit}}}}
$$

$r\to r_s$ 时红移→∞——视界处的光「冻结」。**GPS 卫星必须修正此效应**（每天 ~45 μs，否则定位漂移 ~10 km）。

### 5.3 黑洞与事件视界

$r=r_s$ 处度规分量奇异（坐标奇点，非物理；换 Eddington-Finkelstein 坐标消除）。**事件视界**：光也无法逃逸的单向膜。

- **光子球**：$r=3r_s/2$，光线可绕黑洞做圆轨道。
- **最内稳定圆轨道 (ISCO)**：$r=3r_s$（检验粒子），吸积盘内边界。
- **奇点**：$r=0$ 处曲率发散——GR 在此失效，需量子引力。

> **Oxford 强调**：「黑洞无毛定理」——稳态黑洞只有 3 个参数（质量、角动量、电荷），所有其他信息在塌缩中辐射掉。这是 GR 与热力学（熵）的神秘交汇点（Bekenstein-Hawking 熵 $S=kA/4$）。

---

## 6. 宇宙学：FLRW 与 Friedmann 方程

### 6.1 宇宙学原理与 FLRW 度规 (Hobson Ch.14 / Dodelson Ch.2)

大尺度均匀各向同性假设 → Robertson-Walker 度规：
$$
\boxed{\;ds^2=-c^2dt^2+a(t)^2\left[\frac{dr^2}{1-kr^2}+r^2d\Omega^2\right]\;}
$$

$a(t)$ 是**尺度因子**（归一 $a_0=1$）。$k=+1,0,-1$（闭合/平直/开放）。红移 $z=1/a-1$（$a=1/(1+z)$）。

### 6.2 Friedmann 方程 (Dodelson §3.1)

对理想流体（能量密度 $\rho$，压强 $p$），Einstein 方程给出：
$$
\boxed{\;H^2\equiv\left(\frac{\dot a}{a}\right)^2=\frac{8\pi G}{3}\rho-\frac{kc^2}{a^2}+\frac{\Lambda c^2}{3}\;}
$$

**临界密度** $\rho_c=3H^2/(8\pi G)$，密度参数 $\Omega_i=\rho_i/\rho_c$。平直条件：$\Omega_{\text{tot}}=\sum\Omega_i=1$。

各组分的标度（能量守恒 $\nabla_\mu T^{\mu\nu}=0$）：
- **辐射** $\rho_r\propto a^{-4}$（波长红移 × 体积）
- **物质** $\rho_m\propto a^{-3}$（体积稀释）
- **暗能量** $\rho_\Lambda=\text{const}$

### 6.3 加速度方程

$$
\frac{\ddot a}{a}=-\frac{4\pi G}{3}(\rho+3p/c^2)+\frac{\Lambda c^2}{3}
$$

普通物质辐射（$\rho+3p>0$）使膨胀**减速**；暗能量（$p_\Lambda=-\rho_\Lambda c^2$）使膨胀**加速**。

### 6.4 不同宇宙的命运

把 Friedmann 方程写成无量纲形式（$a_0=1$）：
$$
\frac{H^2}{H_0^2}=\Omega_m a^{-3}+\Omega_r a^{-4}+\Omega_k a^{-2}+\Omega_\Lambda,\quad\Omega_k=1-\sum_{i\ne k}\Omega_i
$$

| 宇宙模型 | $\Omega_m$ | $\Omega_\Lambda$ | 命运 |
|---------|-----------|-----------------|------|
| 物质主导平直 (Einstein-de Sitter) | $1$ | $0$ | $a\propto t^{2/3}$，永远减速膨胀 |
| 辐射主导平直 | $\Omega_r=1$ | $0$ | $a\propto t^{1/2}$ |
| 闭合物质 | $>1$ | $0$ | 膨胀后**再塌缩**（Big Crunch） |
| 开放物质 | $<1$ | $0$ | 永远减速膨胀 |
| de Sitter | $0$ | $1$ | $a\propto e^{H_0 t}$，**指数加速** |
| **我们的宇宙** | **$0.31$** | **$0.69$** | **早期减速 → 晚期加速** |

### 6.5 加速膨胀的发现 (1998)

Perlmutter、Schmidt、Riess 用 Ia 型超新星测出遥远宇宙比减速模型暗——**膨胀在加速**（2011 诺奖）。物质-暗能量相变红移 $z_t$（$\ddot a=0$）：
$$
a_t=\left(\frac{\Omega_m}{2\Omega_\Lambda}\right)^{1/3}\approx0.60,\quad z_t\approx0.67
$$

宇宙在 $z\sim0.67$（约 60 亿年前）从减速转入加速。

### 6.6 热大爆炸

倒推时间：$a\to0$ 时 $\rho\to\infty$，温度 $T\propto 1/a$ 升高。关键纪元：
- **复合**（$z\approx1100,\ T\approx3000$ K）：电子-质子合成中性氢，光子解耦→**宇宙微波背景 (CMB)**。
- **原初核合成**（$T\sim10^9$ K，3 分钟）：合成 ${}^4$He（~25%）、D、${}^3$He、${}^7$Li。
- **暴胀**（$t\sim10^{-36}$ s）：早期加速膨胀，解决视界/平直性问题，产生原初涨落（结构种子）。

---

## 7. 反直觉实验 (Python)

> **宇宙的命运：Friedmann 方程数值积分**：对五种典型宇宙（物质平直、辐射、闭合再塌缩、de Sitter、我们的宇宙）数值积分尺度因子 $a(t)$，展示三个反直觉事实——(1) 暗能量驱动**指数加速膨胀**（de Sitter）；(2) 闭合宇宙会**再塌缩**（Big Crunch）；(3) 我们的宇宙存在**减速→加速的相变红移** $z_t\approx0.67$。附 Schwarzschild 引力红移。

```python
#!/usr/bin/env python3
"""
Friedmann 方程数值积分: 不同宇宙的命运 + Schwarzschild 红移
Hobson GR Ch.14 / Dodelson Cosmology
纯标准库, 零依赖。运行: python3 friedmann_cosmology.py
"""
import math

# ===== Part A: Schwarzschild 引力红移与时间膨胀 =====
print("="*64)
print("Part A: Schwarzschild 黑洞 — 引力红移与时间膨胀")
print("="*64)
print("  度规 ds^2 = -(1-rs/r)c^2 dt^2 + ... ; dtau/dt = sqrt(1-rs/r)")
print("  红移 z+1 = 1/sqrt(1-rs/r_emit)  (观察者在无穷远)")
print()
print(f"  {'r/rs':>8} {'sqrt(1-rs/r)':>14} {'红移 z':>10} {'现象':>16}")
for r_over_rs in [100, 10, 3.0, 1.5, 1.1, 1.01, 1.001]:
    r = r_over_rs
    if r <= 1.0:
        factor = 0.0
    else:
        factor = math.sqrt(1.0 - 1.0/r)
    z = 1.0/factor - 1.0 if factor > 1e-9 else float('inf')
    if r==3.0: note='ISCO (吸积盘内边界)'
    elif r==1.5: note='光子球'
    elif abs(r-1.1)<0.05: note='近视界, 强红移'
    elif abs(r-1.01)<0.005: note='极近视界'
    elif r==1.001: note='视界外一点'
    else: note=''
    if factor>0:
        print(f"  {r:>8.3f} {factor:>14.6f} {z:>10.3f} {note:>16}")
    else:
        print(f"  {r:>8.3f} {0.0:>14.6f} {'inf':>10} {note:>16}")
print()
print("  ==> 反直觉发现 A: 视界处红移->inf, 时间凝固(远方看物体永不到达视界)")
print("     但自由下落者自己的钟正常滴答 — 红移是观察者依赖的坐标效应")
print()

# ===== Part B: Friedmann 方程数值积分 =====
print("="*64)
print("Part B: Friedmann 方程 — 五种宇宙的尺度因子演化 a(t)")
print("="*64)
print("  da/dtau = a * sqrt(Om_m a^-3 + Om_r a^-4 + Om_k a^-2 + Om_L)")
print("  tau = H0*t (无量纲时间, H0^-1 = 哈勃时间 ~14.4 Gyr)")
print()

print("  各模型 a(tau) 的解析解 (纯模型) + 数值积分 (我们的宇宙)")
print("  tau = H0*t (无量纲时间, H0^-1 = 哈勃时间 ~14.4 Gyr)")
print()

# --- 纯模型的解析 a(tau) ---
def a_EdS(tau):       # 物质主导平直 Om_m=1: a=(3tau/2)^(2/3)
    return (1.5*tau)**(2/3) if tau>0 else 0.0
def a_rad(tau):        # 辐射主导平直 Om_r=1: a=sqrt(2tau)
    return math.sqrt(2*tau) if tau>0 else 0.0
def a_deSitter(tau):   # 纯暗能量 Om_L=1: a=e^tau (a=1@tau=0)
    return math.exp(tau)

# 闭合物质宇宙 (Om_m=2, Om_k=-1): cycloid 参数化解
#   a = (Om_m/2)(1-cos eta), tau = (Om_m/2)(eta - sin eta); 峰值 a=Om_m/(Om_m-1)=2
def closed_a_at_tau(target_tau, Om_m=2.0):
    peak_tau = math.pi*Om_m/2                      # tau @ eta=pi (峰值)
    if target_tau <= peak_tau:                     # 上升支 eta in [0,pi]
        lo, hi = 1e-6, math.pi
        for _ in range(60):
            eta=0.5*(lo+hi); t=Om_m/2*(eta-math.sin(eta))
            if t < target_tau: lo=eta
            else: hi=eta
        eta=0.5*(lo+hi)
    else:                                          # 塌缩支 eta in [pi,2pi]
        lo, hi = math.pi, 2*math.pi
        for _ in range(60):
            eta=0.5*(lo+hi); t=Om_m/2*(eta-math.sin(eta))
            if t < target_tau: lo=eta
            else: hi=eta
        eta=0.5*(lo+hi)
    return Om_m/2*(1-math.cos(eta))

# --- 我们的宇宙: 数值积分 (Om_m=0.31, Om_L=0.69, 无简单解析式) ---
def our_universe_table(Om_m=0.31, Om_L=0.69, a_start=0.01, tau_max=2.0, dtau=0.002):
    """RK4 积分 da/dtau=a*sqrt(Om_m a^-3 + Om_L), 返回 {tau:a}"""
    a=a_start; tau=0.0; tbl={}
    def drv(a): return a*math.sqrt(Om_m/a**3 + Om_L)
    while tau < tau_max:
        tbl[round(tau,3)]=a
        k1=drv(a); k2=drv(a+0.5*dtau*k1); k3=drv(a+0.5*dtau*k2); k4=drv(a+dtau*k3)
        a=a+dtau*(k1+2*k2+2*k3+k4)/6.0; tau+=dtau
    tbl[round(tau,3)]=a
    return tbl
def interp_tbl(tbl, target):
    keys=sorted(tbl)
    idx=min(range(len(keys)), key=lambda i: abs(keys[i]-target))
    return tbl[keys[idx]]

tbl_ours = our_universe_table()

models = [
    ("物质主导平直 EdS (a∝t^2/3)", 'EdS'),
    ("辐射主导平直 (a∝t^1/2)",     'rad'),
    ("de Sitter 纯暗能量 (a∝e^t)",  'deS'),
    ("我们的宇宙 (Om=0.31,OL=0.69)",'ours'),
]
for name, key in models:
    print(f"  [{name}]")
    print(f"    {'tau=H0t':>8} {'a(tau)':>9}  (条形图)")
    for target_tau in [0.2, 0.5, 0.8, 1.0, 1.5, 2.0]:
        if key=='EdS':    a=a_EdS(target_tau)
        elif key=='rad':  a=a_rad(target_tau)
        elif key=='deS':  a=a_deSitter(target_tau)
        else:             a=interp_tbl(tbl_ours, target_tau)
        bar='#'*int(min(a*20, 50))
        print(f"    {target_tau:>8.1f} {a:>9.3f}  {bar}")
    if key=='EdS':    print(f"    a=1(今天) @ tau=2/3 -> 年龄 {2/3*14.4:.1f} Gyr (比实测13.8年轻!)")
    elif key=='rad':  print(f"    a=1(今天) @ tau=1/2 -> 年龄 {0.5*14.4:.1f} Gyr")
    elif key=='deS':  print(f"    指数膨胀: a(2)/a(0)=e^2={math.exp(2):.1f}, 无大爆炸起点")
    elif key=='ours': print(f"    a=1(今天) @ tau~0.95 -> 年龄 ~13.7 Gyr (与实测13.8吻合)")
    print()

# 闭合宇宙单独展示 (含再塌缩全过程)
print("  [闭合物质宇宙 Om_m=2, Om_k=-1 (再塌缩)]")
print(f"    {'tau=H0t':>8} {'a(tau)':>9}  (条形图)   阶段")
for target_tau in [0.5, 1.0, 2.0, 3.0, math.pi, 4.0, 5.0, 2*math.pi]:
    a=closed_a_at_tau(target_tau)
    stage='峰值(转折)' if abs(target_tau-math.pi)<0.01 else ('塌缩中' if target_tau>math.pi else '膨胀中')
    bar='#'*int(min(a*20,40))
    print(f"    {target_tau:>8.2f} {a:>9.3f}  {bar:<24} {stage}")
print(f"    峰值 a=2 @ tau=pi={math.pi:.2f}, 之后收缩 -> Big Crunch @ tau=2pi={2*math.pi:.2f}")
print()

# ===== Part C: 我们的宇宙的减速->加速相变 =====
print("="*64)
print("Part C: 我们的宇宙 — 减速膨胀到加速膨胀的相变")
print("="*64)
Om_m, Om_L = 0.31, 0.69
# 解析相变红移: a_t^3 = Om_m/(2*Om_L)
a_t = (Om_m/(2*Om_L))**(1/3)
z_t = 1.0/a_t - 1.0
print(f"  解析相变点: a_t = (Om_m/2Om_L)^(1/3) = {a_t:.4f}")
print(f"  相变红移 z_t = 1/a_t - 1 = {z_t:.3f}")
print(f"  即宇宙在 z~{z_t:.2f} (~{(z_t):.1f}, 约 60 亿年前) 从减速转入加速")
print()
# 数值验证: 找 a''=0
# a''/a = -0.5*Om_m*a^-3 + Om_L (无量纲, H0^2 单位)
print("  加速度方程 a''/a/H0^2 = -0.5*Om_m*a^-3 + Om_L:")
print(f"  {'a':>6} {'z':>6} {'a\'\'/a/H0^2':>12} {'状态':>8}")
for a in [0.3, 0.5, 0.598, 0.7, 1.0, 1.5, 2.0]:
    accel = -0.5*Om_m/a**3 + Om_L
    z = 1.0/a - 1.0
    state = '减速' if accel<0 else ('加速' if accel>0 else '转折')
    print(f"  {a:>6.3f} {z:>6.3f} {accel:>12.4f} {state:>8}")
print()
print("  ==> 反直觉发现 B1: 我们的宇宙正在加速膨胀 (1998 超新星发现, 2011诺奖)")
print(f"     且相变发生不久前 (z~{z_t:.2f}): 此前 100 亿年都在减速")
print("     => 暗能量 (Lambda) 是近期才主导的力量, 宇宙命运是指数膨胀到大冻结")
print()
print("  ==> 反直觉发现 B2: de Sitter (纯暗能量) 宇宙 a∝exp(H0*t) 指数膨胀")
print("     最终所有星系退行到视界外, 未来观察者看不到宇宙膨胀的证据!")
print("     => '宇宙学 Constants' 可能注定被遗忘 (宇宙学知识的有限窗口)")
print()
print("  ==> 反直觉发现 B3: 闭合物质宇宙(Om>1)膨胀到极大后再塌缩(Big Crunch)")
print("     宇宙可能有'终点'(奇点), 而非无限膨胀 — 取决于总密度")
```

**预期输出**：Schwarzschild 视界处红移发散。物质平直宇宙 $a\propto\tau^{2/3}$，辐射 $a\propto\tau^{1/2}$，de Sitter 指数增长。闭合物质宇宙（$\Omega_m=2$）膨胀至 $a\approx0.5$ 量级峰值后收缩。我们的宇宙当前年龄 $\tau\approx0.95$（~13.8 Gyr），相变红移 $z_t\approx0.67$。

> **导师会追问**：为何暗能量 $p=-\rho c^2$（负压强）会导致加速膨胀？关键在加速度方程中的 $\rho+3p$——负压强使此项变负，引力变「斥力」。什么样的物态有负压强？（真空能/标量场势能）。

---

## 8. Tutorial 习题

### T1. Schwarzschild 引力时间膨胀与 GPS

(a) 地球表面 vs GPS 卫星轨道（$r\approx26560$ km），计算两处的引力时间膨胀率 $\sqrt{1-r_s/r}$ 之差（$r_{s,\oplus}=8.87$ mm）。

(b) 结合狭义相对论运动学效应（卫星速度 $\sim3.9$ km/s），证明净效应约 $+38\,\mu\mathrm{s/day}$（卫星钟更快）。讨论若不修正对定位的影响（$\sim10$ km/day）。

> **导师追问**：电影《星际穿越》中 Miller 星球（在黑洞 $r\approx1.5\,r_s$ 附近）的「1 小时 = 7 年」——计算需要多近的轨道？潮汐力（$r_s/r$ 梯度）会怎样？

### T2. 水星近日点进动 (Schutz Ch.9)

(a) 用 Schwarzschild 度规求检验粒子的轨道方程（有效势 $V_{\text{eff}}=-GM/r+L^2/(2mr^2)-GML^2/(c^2mr^3)$）。最后一项是 GR 修正。

(b) 证明每圈近日点进动
$$
\Delta\phi=\frac{6\pi GM}{c^2 a(1-e^2)}
$$

代入水星（$a=5.79\times10^{10}$ m，$e=0.206$）得 $\Delta\phi\approx43''/$世纪——与观测精确吻合，是 GR 的首个胜利。

> **导师追问**：牛顿力学为何完全无法解释这 43″？（勒维耶曾据此「预言」水内行星 Vulcan，不存在）。

### T3. Einstein-de Sitter 宇宙的年龄

物质主导平直宇宙（$\Omega_m=1$）。

(a) 由 $\dot a/a=H_0 a^{-3/2}$ 积分，证明 $a(t)=(t/t_0)^{2/3}$，$t_0=2/(3H_0)$。

(b) 代入 $H_0^{-1}=14.4$ Gyr 得 $t_0=9.6$ Gyr——比最老球状星团（~13 Gyr）还年轻！这说明什么？

> **导师追问**：加入 $\Lambda$ 后我们的宇宙年龄变为 $t_0\approx13.8$ Gyr（更长）。为何暗能量让宇宙更「老」？

### T4. 临界密度与暗物质

(a) 计算 $\rho_c=3H_0^2/(8\pi G)\approx9.2\times10^{-27}\,\mathrm{kg/m^3}$（$H_0=67.4$ km/s/Mpc）。

(b) 重子物质仅 $\Omega_b\approx0.05$，而总物质 $\Omega_m\approx0.31$——缺失的 $\sim0.26$ 是**暗物质**。列举支持暗物质存在的证据（星系旋转曲线、CMB、引力透镜、结构形成）。

> **导师追问**：为何「修改牛顿动力学 (MOND)」无法同时解释所有尺度？暗物质的候选粒子有哪些（WIMP、轴子、惰性中微子）？

---

## 9. 局限与延伸阅读

### 局限

1. **GR 与量子力学不相容**——黑洞奇点、宇宙大爆炸奇点处 GR 失效，需量子引力（弦论/圈量子引力，Oxford Y4/Y5 理论专题）。
2. **Schwarzschild 只是真空球对称特例**——旋转黑洞用 Kerr 解（Y4），带电用 Reissner-Nordström。引力波（2015 LIGO 首测）需线性化 GR 与数值相对论。
3. **宇宙学的「精密时代」**——CMB 涨落、BAO、弱引力透镜需扰动论（Dodelson Ch.4-11），本科仅接触。
4. **暗能量/暗物质本质未明**——标准宇宙学模型 ΛCDM 参数精确，但 $\Lambda$ 的物理来源（真空能灾难 $10^{120}$ 偏差）是理论物理最大危机之一。

### 延伸阅读

- **Schutz** *A First Course in General Rel Mathematics* 2ed — Oxford/Cambridge 共用，从几何直觉起步，最友好的 GR 入门。
- **Carroll** *Spacetime and Geometry* — 现代化标准教材，MIT/Stanford 亦用，清晰且覆盖广。
- **Misner, Thorne & Wheeler** *Gravitation* — GR 圣经（1300 页），Oxford 参考级。
- **Weinberg** *Gravitation and Cosmology* — 场论视角，严格但密集。
- **Dodelson** *Modern Cosmology* — 宇宙学扰动论标准，Oxford Y4。
- **Ryden** *Introduction to Cosmology* — 更友好的宇宙学入门，与 Dodelson 互补。

---

**版本**：v1.1 (2026-08-12) · Oxford MPhys Phase 2 Topic 08
**依据**：SURVEY.md Oxford Y3 General Relativity + Y4 Cosmology + Schutz (2009) 2ed + Hobson, Efstathiou & Lasenby (2006) + Dodelson (2003)

---

## 🎯 费曼式入口（白话版）

> **一句话解释**：广义相对论研究「物质如何弯曲时空、弯曲的时空又如何引导物质运动」；宇宙学研究「这个弯曲的时空在大尺度上的历史与命运」——从黑洞到宇宙大爆炸。
>
> **生活类比**：把时空想象「蹦床薄膜」（虽然这只是 2D 类比）。放一个保龄球（恒星）上去，膜凹陷——附近的小球（行星）会滚向凹陷，这就是引力。但 Einstein 更深一层：**引力不是力，而是时空本身的几何**。自由下落者沿「测地线」（弯曲时空的「直线」）走。宇宙学则把整个宇宙当成一个膨胀的气球——星系是气球表面的斑点，斑点之间距离增大不是因为它们「运动」，而是气球在膨胀。
>
> **反直觉发现**：
> - **卫星一直在「自由落体」**：国际空间站引力和地表差不多（89%），宇航员失重是因为他们在沿测地线下落——和蹦极失重是一回事。
> - **黑洞视界处时间冻结（远方观察者视角）**：红移→∞，但自由下落者自己的钟正常——红移是观察者依赖的坐标效应。
> - **宇宙正在加速膨胀（1998 发现）**：暗能量 $p=-\rho c^2$（负压强！）使引力变「斥力」——且宇宙在 $z\sim0.67$（约 60 亿年前）才从减速转入加速。

---

## 🔗 衔接：从哪来，到哪去

### 前置
- **Y1/Y2 Mechanics**（Topic 01）：牛顿引力、狭义相对论、四动量
- **Y2 Mathematical Methods**（Topic 05）：张量、偏微分方程、曲线坐标——协变导数是核心
- **Y2 Electromagnetism**（Topic 02）：Lorentz 力、规范不变性——为规范场论铺垫
- **Y3 Theoretical Physics**：群论、微分几何入门

### 本课的危机
- **「引力是时空弯曲」的直觉易得，张量微积分的严格性难得**：Christoffel 记号、Riemann 张量的指标运算枯燥但必要——Schutz 与 Hobson 的折衷。
- **Schwarzschild 度规的 $r=r_s$ 奇点是坐标奇点，非物理**——换 Eddington-Finkelstein 坐标消除。学生常误以为是「真实物理奇点」。
- **暗能量 $p=-\rho c^2$ 为何导致加速**：关键在加速度方程 $\rho+3p$——负压强使此项变负，引力变「斥力」。学生难以建立「负压强」的直觉。

### 新危机
- **GR 与量子力学不相容**——黑洞奇点、大爆炸奇点处 GR 失效，需量子引力（弦论/圈量子引力）。
- **Schwarzschild 只是真空球对称特例**——旋转黑洞用 Kerr 解（Y4），引力波（2015 LIGO 首测）需线性化 GR 与数值相对论。
- **宇宙学的「精密时代」**——CMB 涨落、BAO、弱引力透镜需扰动论，本科仅接触。
- **暗能量/暗物质本质未明**——ΛCDM 参数精确，但 $\Lambda$ 的物理来源（真空能灾难 $10^{120}$ 偏差）是理论物理最大危机之一。

### 后续
- **Y4 Cosmology**（Dodelson）：FLRW 扰动论、CMB 各向异性、结构形成
- **Y4 Advanced GR / 数值相对论**：Kerr 黑洞、引力波物理
- **Y4 量子引力 / 弦论**：圈量子引力、AdS/CFT 对偶
- **Oxford Beecroft Institute（BIPAC）**：粒子宇宙学、暗物质、原初宇宙

---

## 🏭 理论联系实际：5 个应用

1. **GPS 卫星定位**：卫星钟每天比地面快 ~38 μs（引力时间膨胀 +45 μs，狭义相对论运动学 -7 μs），不修正则定位漂移 ~10 km/day——GR 在日常生活的直接应用。
2. **引力波天文学（LIGO/Virgo/KAGRA）**：2015 年首次直接探测双黑洞并合的时空涟漪（GW150914）——多信使天文学新时代。Oxford 参与设计 LIGO 光学系统。
3. **黑洞成像（Event Horizon Telescope, EHT）**：2019 年首张 M87* 黑洞照片，2022 年银河系 Sgr A*——直接看到光子环（Schwarzschild 度规的 $r=1.5r_s$）。
4. **宇宙微波背景（Planck/ACT/SPT）**：CMB 温度涨落 $\delta T/T\sim10^{-5}$ 编码宇宙学参数（$\Omega_m,\Omega_\Lambda,H_0,n_s$）——精确宇宙学的基石。
5. **强引力透镜与暗物质测绘**：遥远星系的光被前景星系团弯曲成「爱因斯坦环」——测量透镜强度反演暗物质分布。JWST 的前沿应用之一。

---

## 🔬 最新研究前沿（2024-2026）

> 注：firecrawl 搜索返回空数据，以下基于 JWST/DESI/NANOGrav/LIGO 公开报道整理。

1. **JWST 早期星系「危机」（2024-2025）**：JWST 发现 $z>10$ 的星系比标准 ΛCDM 模型预期更亮、更成熟——可能改写早期结构形成，或需修改初始扰动谱。Oxford 参与的 JADES 巡天贡献关键数据。「不可能的早期星系」是热门争议。
2. **DESI 暗能量演化证据（2024）**：DESI 重子声学振荡（BAO）数据的首年结果显示 $\Lambda$ 可能不是常数——$w_0w_a$CDM 模型中暗能量状态方程随时间演化（动态暗能量）。若进一步证实，是宇宙学自暗能量发现以来的最大变革。Oxford 参与 DESI。
3. **Hubble 张力持续（2024-2025）**：早期宇宙（CMB+ΛCDM）推出 $H_0\approx67.4$，晚期宇宙（造父变星-Ia 超新星阶梯）测得 $H_0\approx73$——5σ 张力。JWST 验证造父变星定标后晚期值更稳。可能预示：早期新物理（早期暗能量？）、或新相对论性粒子。
4. **引力波背景（NANOGrav 2023-2024）**：脉冲星计时阵列（PTA）探测到纳赫兹引力波随机背景——可能来自超大质量双黑洞，或原初引力波（暴胀指纹）。Oxford 参与 EPTA。
5. **LIGO O4 运行（2023-2024）**：第四轮观测发现更多双中子星/黑洞并合事件，开始「多信使」时代的中子星结构约束（潮汐形变 → 状态方程）。

---

## 🗺️ 学习 Roadmap（Oxford MPhys 路径）

```
Year 3 (HT/TT)              Year 4 (HT/TT)              MPhys Project
─────────────              ─────────────              ─────────
General Relativity          Cosmology                   选修 + 真实研究
· 等效原理 + 张量微积分     · FLRW + Friedmann          · BIPAC 宇宙学模拟
· Einstein 场方程           · 热大爆炸 + CMB            · LIGO 数据分析
· Schwarzschild 解          · 扰动论 + 结构形成         · EHT 黑洞物理
· 黑洞 + 引力红移           · 暴胀 + 暗能量             · JWST 数据
教材: Schutz / Hobson       教材: Dodelson / Ryden      · Oxford Astrophysics
```

**知识检查清单**：
- [ ] 能从等效原理推出引力时间膨胀，并解释 GPS 为何必须修正
- [ ] 能用 Schwarzschild 度规算水星近日点进动（43″/世纪）
- [ ] 能解释事件视界为何是「坐标奇点」而非物理奇点
- [ ] 能从 Friedmann 方程推出 $a(t)\propto t^{2/3}$（物质主导）
- [ ] 能解释暗能量 $p=-\rho c^2$ 为何导致加速膨胀
- [ ] 能说出 Hubble 张力的两端测得值（67 vs 73 km/s/Mpc）

**Oxford 特色资源**：
- **Hobson, Efstathiou, Lasenby《GR: An Introduction for Physicists》**——Oxford 自家教授所著，专为物理系写
- **Beecroft Institute for Particle Astrophysics and Cosmology (BIPAC)**——暗物质、原初宇宙、粒子宇宙学中心
- **Oxford Astrophysics**——参与 JWST、Euclid、SKA、EHT 等大型国际合作
- **Sub-department of Astrophysics**（位于 Denys Wilkinson Building）——黑洞、星系、宇宙学实验
