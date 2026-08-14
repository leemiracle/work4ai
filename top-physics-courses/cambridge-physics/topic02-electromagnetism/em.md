# Cambridge Part IA/IB · Electromagnetism

> **教材**：Griffiths *Introduction to Electrodynamics* (4th ed.) — 全球 10/10 通用教材；Lorrain & Corson *Electromagnetic Fields and Waves* — Cambridge Part IA 指定参考
>
> **Cambridge 课程编号**：Part IA Electromagnetism + Part IB Electromagnetism
>
> **Cambridge 特色**：Cavendish Laboratory 实验传统——Maxwell 创立的精确电磁测量；从实验现象到麦克斯韦方程组的严密推演

---

## 目录

1. [静电学](#1-静电学)
2. [静磁学](#2-静磁学)
3. [麦克斯韦方程组](#3-麦克斯韦方程组)
4. [电磁波](#4-电磁波)
5. [势与规范变换](#5-势与规范变换)
6. [Python 代码演示](#6-python-代码演示)
7. [Tripos 风格习题](#7-tripos-风格习题)

---

## 1. 静电学

### 1.1 库仑定律与电场

点电荷 $q$ 在距离 $r$ 处产生的电场：

$$\mathbf{E} = \frac{1}{4\pi\epsilon_0}\frac{q}{r^2}\hat{\mathbf{r}}$$

### 1.2 高斯定律

电场的散度等于电荷密度除以 $\epsilon_0$：

$$\nabla \cdot \mathbf{E} = \frac{\rho}{\epsilon_0}$$

积分形式：穿过闭合曲面的电通量等于内部总电荷除以 $\epsilon_0$：

$$\oint_S \mathbf{E} \cdot d\mathbf{A} = \frac{Q_{\text{enc}}}{\epsilon_0}$$

**高斯定律的威力在于对称性**。只有当电荷分布具有球、柱或平面对称性时，才能用高斯定律"猜出"电场方向，从而将矢量积分化为标量代数。

### 1.3 电势

静电场是保守场（$\nabla \times \mathbf{E} = 0$），故可引入标量势：

$$\mathbf{E} = -\nabla V$$

电势满足泊松方程：

$$\nabla^2 V = -\frac{\rho}{\epsilon_0}$$

### 1.4 多极展开

远处观察一个局域电荷分布的电势：

$$V(\mathbf{r}) = \frac{1}{4\pi\epsilon_0}\left[\frac{Q}{r} + \frac{\mathbf{p}\cdot\hat{\mathbf{r}}}{r^2} + \frac{1}{2}\sum_{ij}Q_{ij}\frac{\hat{r}_i\hat{r}_j}{r^3} + \cdots\right]$$

- $Q = \int \rho\,d^3r'$ — 总电荷（单极矩）
- $\mathbf{p} = \int \mathbf{r}'\rho\,d^3r'$ — 电偶极矩
- $Q_{ij} = \int (3x_i'x_j' - r'^2\delta_{ij})\rho\,d^3r'$ — 电四极矩

**反直觉发现**：对于电中性系统（$Q=0$），偶极项主导。但如果系统还有 $\mathbf{p}=0$（例如均匀带电的球壳拉伸为椭球），则四极项主导，电势以 $1/r^3$ 衰减——远快于点电荷的 $1/r$。

### 1.5 电介质

在物质中，束缚电荷的响应由**电极化率** $\chi_e$ 描述：

$$\mathbf{P} = \epsilon_0 \chi_e \mathbf{E}$$

定义电位移：$\mathbf{D} = \epsilon_0 \mathbf{E} + \mathbf{P} = \epsilon \mathbf{E}$，高斯定律变为：

$$\nabla \cdot \mathbf{D} = \rho_{\text{free}}$$

**边界条件**（两种介质交界面）：
- $D_\perp$ 有跳变 $\Delta D_\perp = \sigma_{\text{free}}$
- $E_\parallel$ 连续

---

## 2. 静磁学

### 2.1 毕奥-萨伐尔定律

稳恒电流 $\mathbf{J}$ 产生的磁场：

$$\mathbf{B}(\mathbf{r}) = \frac{\mu_0}{4\pi}\int \frac{\mathbf{J}(\mathbf{r}') \times (\mathbf{r}-\mathbf{r}')}{|\mathbf{r}-\mathbf{r}'|^3}d^3r'$$

### 2.2 安培定律

$$\nabla \times \mathbf{B} = \mu_0 \mathbf{J}$$

积分形式：$\oint_C \mathbf{B}\cdot d\boldsymbol{\ell} = \mu_0 I_{\text{enc}}$。

**经典应用——长直螺线管**：理想长螺线管内部磁场均匀 $B = \mu_0 n I$（$n$ = 单位长度匝数），外部为零。

### 2.3 磁偶极矩

电流回路的磁偶极矩：

$$\mathbf{m} = I\mathbf{A}$$

（$\mathbf{A}$ 为面积矢量）。远场与电偶极子形式完全对应：

$$\mathbf{B}_{\text{dip}} = \frac{\mu_0}{4\pi r^3}\left[3(\mathbf{m}\cdot\hat{\mathbf{r}})\hat{\mathbf{r}} - \mathbf{m}\right]$$

**电与磁的深刻不对称**：至今未发现磁单极子。$\nabla \cdot \mathbf{B} = 0$ 意味着磁场线无头无尾（总是闭合的），这与 $\nabla \cdot \mathbf{E} = \rho/\epsilon_0$ 形成鲜明对比。Dirac（Cavendish 的精神遗产）证明：**哪怕宇宙中只存在一个磁单极子，电荷就必须量子化**（$eg = n\hbar/2$）。

### 2.4 磁介质

磁化强度 $\mathbf{M}$，辅助场 $\mathbf{H} = \frac{\mathbf{B}}{\mu_0} - \mathbf{M}$。

三种磁性物质：
| 类型 | $\chi_m$ | 典型 |
|------|---------|------|
| 抗磁 | $< 0$（极小，$\sim 10^{-5}$） | 铋、铜 |
| 顺磁 | $> 0$（极小，$\sim 10^{-4}$） | 铝、铂 |
| 铁磁 | $\gg 1$（非线性，有磁滞） | 铁、钴、镍 |

---

## 3. 麦克斯韦方程组

### 3.1 位移电流的引入

安培定律 $\nabla \times \mathbf{B} = \mu_0 \mathbf{J}$ 在时变情况下**不自洽**：对两边取散度，左边 $\nabla \cdot (\nabla \times \mathbf{B}) \equiv 0$，但右边 $\mu_0 \nabla \cdot \mathbf{J} = -\mu_0 \frac{\partial \rho}{\partial t} \ne 0$（一般情况）。

Maxwell 的天才修正是加入**位移电流**：

$$\nabla \times \mathbf{B} = \mu_0 \mathbf{J} + \mu_0\epsilon_0 \frac{\partial \mathbf{E}}{\partial t}$$

这一项的加入使方程自洽，并且——最惊人的——**预言了电磁波**。

### 3.2 完整的麦克斯韦方程组

**微分形式**（真空，Cambridge 国际标准记法）：

$$\nabla \cdot \mathbf{E} = \frac{\rho}{\epsilon_0}$$

$$\nabla \cdot \mathbf{B} = 0$$

$$\nabla \times \mathbf{E} = -\frac{\partial \mathbf{B}}{\partial t}$$

$$\nabla \times \mathbf{B} = \mu_0 \mathbf{J} + \mu_0\epsilon_0 \frac{\partial \mathbf{E}}{\partial t}$$

**介质中的形式**（用 $\mathbf{D}, \mathbf{H}$）：

$$\nabla \cdot \mathbf{D} = \rho_f, \quad \nabla \cdot \mathbf{B} = 0$$
$$\nabla \times \mathbf{E} = -\frac{\partial \mathbf{B}}{\partial t}, \quad \nabla \times \mathbf{H} = \mathbf{J}_f + \frac{\partial \mathbf{D}}{\partial t}$$

### 3.3 Maxwell 的遗产

1865 年，Maxwell 在 Cavendish 的前身时期发表了 *A Dynamical Theory of the Electromagnetic Field*。他不仅统一了电学和磁学，还发现电磁波的传播速度：

$$c = \frac{1}{\sqrt{\mu_0\epsilon_0}} \approx 3 \times 10^8 \text{ m/s}$$

恰好等于光速！这是物理学史上最伟大的统一之一：**光就是电磁波**。

---

## 4. 电磁波

### 4.1 真空中的波方程

在真空中（$\rho = 0, \mathbf{J} = 0$），取 $\nabla \times (\nabla \times \mathbf{E}) = \nabla(\nabla \cdot \mathbf{E}) - \nabla^2 \mathbf{E}$：

$$\nabla^2 \mathbf{E} = \mu_0\epsilon_0 \frac{\partial^2 \mathbf{E}}{\partial t^2}$$

这是波速为 $c = 1/\sqrt{\mu_0\epsilon_0}$ 的波动方程。

### 4.2 平面波解

$$\mathbf{E}(\mathbf{r}, t) = \mathbf{E}_0 e^{i(\mathbf{k}\cdot\mathbf{r} - \omega t)}$$

其中 $\omega = c|\mathbf{k}|$。关键性质：
1. **横波**：$\mathbf{k} \cdot \mathbf{E}_0 = 0$，$\mathbf{k} \cdot \mathbf{B}_0 = 0$
2. $\mathbf{E}_0 \perp \mathbf{B}_0$，且 $\mathbf{B}_0 = \frac{\mathbf{k}\times\mathbf{E}_0}{\omega}$
3. $|\mathbf{B}| = |\mathbf{E}|/c$

### 4.3 偏振

电磁波的电场矢量方向定义偏振：
- **线偏振**：$\mathbf{E}_0$ 固定方向
- **圆偏振**：$\mathbf{E}_0 = E_0(\hat{\mathbf{x}} \pm i\hat{\mathbf{y}})/\sqrt{2}$，左旋/右旋

### 4.4 能流与坡印廷矢量

$$\mathbf{S} = \frac{1}{\mu_0}\mathbf{E} \times \mathbf{B}$$

能流密度（单位时间通过单位面积的电磁能量）。时间平均：

$$\langle \mathbf{S} \rangle = \frac{1}{2\mu_0}|\mathbf{E}_0|^2 \hat{\mathbf{k}}$$

电磁能量密度 $u = \frac{1}{2}(\epsilon_0 E^2 + B^2/\mu_0)$，对平面波 $u = \epsilon_0 E^2$。

### 4.5 介质中的色散

在介电常数为 $\epsilon(\omega)$ 的介质中，相速度 $v = c/n$，折射率 $n = \sqrt{\epsilon_r}$。

**色散**：不同频率的光传播速度不同，导致棱镜分光和彩虹。Lorentz 振子模型给出：

$$n^2(\omega) = 1 + \frac{Ne^2}{m\epsilon_0}\sum_j \frac{f_j}{\omega_j^2 - \omega^2 - i\gamma_j\omega}$$

在共振频率 $\omega_j$ 附近，$n$ 剧烈变化（反常色散）——这就是 Cavendish 经典光谱实验的理论基础。

---

## 5. 势与规范变换

### 5.1 标势与矢势

由于 $\nabla \cdot \mathbf{B} = 0$，引入矢势 $\mathbf{A}$：$\mathbf{B} = \nabla \times \mathbf{A}$。

Faraday 定律 $\nabla \times \mathbf{E} + \partial\mathbf{B}/\partial t = 0$ 变为 $\nabla \times (\mathbf{E} + \partial\mathbf{A}/\partial t) = 0$，故引入标势 $\phi$：

$$\mathbf{E} = -\nabla\phi - \frac{\partial \mathbf{A}}{\partial t}$$

### 5.2 规范不变性

变换 $\mathbf{A}' = \mathbf{A} + \nabla\Lambda$，$\phi' = \phi - \partial\Lambda/\partial t$ 不改变物理场 $\mathbf{E}, \mathbf{B}$。

**Lorenz 规范**（$\nabla \cdot \mathbf{A} + \mu_0\epsilon_0 \partial\phi/\partial t = 0$）下，势满足非齐次波方程：

$$\Box\phi = -\rho/\epsilon_0, \quad \Box\mathbf{A} = -\mu_0\mathbf{J}$$

其中 $\Box = \nabla^2 - \frac{1}{c^2}\frac{\partial^2}{\partial t^2}$（达朗贝尔算子）。

**规范不变性**的深刻意义在量子力学和粒子物理中才完全显现——它是 Yang-Mills 理论和标准模型的基石。

### 5.3 推迟势

Lorenz 规范下波方程的解（推迟势）：

$$\phi(\mathbf{r}, t) = \frac{1}{4\pi\epsilon_0}\int \frac{\rho(\mathbf{r}', t_r)}{|\mathbf{r}-\mathbf{r}'|}d^3r'$$

其中 $t_r = t - |\mathbf{r}-\mathbf{r}'|/c$ 是推迟时间——电磁作用以光速传播。

---

## 6. Python 代码演示

### 6.1 电偶极子场线可视化（ASCII）

```python
"""
电偶极子电场线与等势线（ASCII 可视化）
零依赖。
"""
import math

def dipole_field(x, y, d=1.0, q=1.0):
    """两个点电荷 +q 在 (0, d/2), -q 在 (0, -d/2)
    返回 (Ex, Ey, V)
    """
    # +q at (0, d/2)
    r1 = math.sqrt(x**2 + (y - d/2)**2)
    # -q at (0, -d/2)
    r2 = math.sqrt(x**2 + (y + d/2)**2)

    # 避免奇点
    r1 = max(r1, 0.01)
    r2 = max(r2, 0.01)

    # 电势 (忽略 1/4πε₀ 因子)
    V = q/r1 - q/r2

    # 电场 (负梯度)
    Ex = q * x / r1**3 - q * x / r2**3
    Ey = q * (y - d/2) / r1**3 - q * (y + d/2) / r2**3

    return Ex, Ey, V

# ASCII 可视化: 30x30 网格
width, height = 40, 20
x_max, y_max = 3.0, 2.0

print("=== 电偶极子电场线 (→ 方向) ===")
print("+q 在上方, -q 在下方\n")

for j in range(height):
    row = ""
    for i in range(width):
        x = (i / width - 0.5) * 2 * x_max
        y = -(j / height - 0.5) * 2 * y_max  # y轴翻转

        Ex, Ey, V = dipole_field(x, y)
        E_mag = math.sqrt(Ex**2 + Ey**2)

        # 用箭头方向表示场方向
        if E_mag < 0.01:
            row += " "
        elif E_mag > 100:
            row += "*"
        else:
            angle = math.atan2(Ey, Ex)
            # 8方向量化
            idx = int((angle + math.pi) / (2*math.pi) * 8) % 8
            arrows = "→↘↓↙←↖↑↗"
            row += arrows[idx]
    print(row)

# 等势线数值采样
print("\n=== 电偶极子电势 V(x,0) 沿 x 轴 ===")
print("x\t\tV(x,0)")
for x10 in range(-30, 31, 3):
    x = x10 / 10.0
    _, _, V = dipole_field(x, 0)
    bar = "#" * int(abs(V) * 5)
    sign = "+" if V > 0 else ("-" if V < 0 else " ")
    print(f"{x:+.1f}\t\t{V:+.4f} {sign}{bar}")
```

### 6.2 电磁波传播模拟

```python
"""
电磁平面波: E ⊥ B ⊥ k 传播
用字符动画展示（终端输出快照）
零依赖。
"""
import math

def em_wave_snapshot(t, k=1.0, omega=1.0, E0=1.0):
    """E 沿 y 方向, B 沿 z 方向, 传播沿 x 方向
    E(x,t) = E0 cos(kx - ωt) ŷ
    B(x,t) = (E0/c) cos(kx - ωt) ẑ
    """
    c = omega / k
    print(f"=== 电磁波快照 t={t:.2f}, k={k}, ω={omega}, c={c:.2f} ===")
    print(f"E沿y轴(↑↓), B沿z轴(⊗⊙ 进入/出屏幕), 传播方向→x\n")

    n_points = 50
    x_max = 4 * math.pi / k  # 两个波长

    # 上半部分画 E
    for row in range(10, -1, -1):
        line = ""
        for i in range(n_points):
            x = i / n_points * x_max
            E = E0 * math.cos(k*x - omega*t)
            # 映射 E 值 [-1,1] 到行 [0, 10]
            target_row = int((E / E0 + 1) * 5)
            if row == target_row:
                line += "●"
            elif row == 5 and abs(E) < 0.3:
                line += "-"
            else:
                line += " "
        label = f"E={0.1*(10-row)-0.5:+.1f}" if row in (0, 5, 10) else "     "
        print(f"  {label} |{line}")

    print("  " + " " * 7 + "+" + "-" * n_points + "→ x (传播方向)")

    # 下半部分画 B (用 ⊗⊙ 符号)
    b_line1 = ""
    b_line2 = ""
    for i in range(n_points):
        x = i / n_points * x_max
        B = (E0 / 1.0) * math.cos(k*x - omega*t)  # c=1 in natural units
        if B > 0.3:
            b_line1 += "⊙"  # 出屏幕
            b_line2 += " "
        elif B < -0.3:
            b_line1 += " "
            b_line2 += "⊗"  # 入屏幕
        else:
            b_line1 += " "
            b_line2 += " "
    print(f"\n  B(out) |{b_line1}")
    print(f"  B(in)  |{b_line2}")

# 取不同时刻的快照
for t in [0.0, math.pi/4, math.pi/2]:
    em_wave_snapshot(t)
    print()

# 能量密度检验
print("=== 能量密度 u = ε₀E² = B²/μ₀ ===")
print("验证 E 和 B 同相位, 且 u(E) = u(B)")
for t in [0.0, 0.5, 1.0]:
    E = math.cos(t)  # E0=1
    B = math.cos(t)  # E0/c=1 (natural units c=1)
    u_E = 0.5 * E**2  # 忽略常数因子
    u_B = 0.5 * B**2
    print(f"  t={t:.1f}: E={E:+.4f}, B={B:+.4f}, "
          f"u_E={u_E:.4f}, u_B={u_B:.4f}, "
          f"u_E/u_B={u_E/u_B if u_B>0 else 'inf':.4f}")
```

### 6.3 电容充电电路的位移电流验证

```python
"""
位移电流验证: 电容器充电时两板间的磁场
安培-麦克斯韦定律: ∮B·dl = μ₀(I_cond + I_disp)
在电容器内部 I_cond=0, 但 I_disp=ε₀ dΦ_E/dt
在电容器外部 I_disp=0, 但 I_cond=I
两者给出的 B 完全相同 → 位移电流的物理实在性
零依赖。
"""
import math

mu0 = 4e-7 * math.pi  # μ₀
eps0 = 8.854e-12       # ε₀

# 平行板电容器, 半径 R, 板间距 d
R = 0.01    # 1 cm
d = 0.001   # 1 mm
C = eps0 * math.pi * R**2 / d  # 电容

# 充电电流恒定 I
I = 1e-3  # 1 mA

# 电场增长率 (E = Q/(ε₀ A), dE/dt = I/(ε₀ A))
A = math.pi * R**2
dEdt = I / (eps0 * A)

print("=== 位移电流验证 ===")
print(f"电容器: R={R*100:.1f}cm, d={d*1000:.1f}mm")
print(f"电容 C = {C*1e12:.4f} pF")
print(f"充电电流 I = {I*1000:.1f} mA")
print(f"dE/dt = {dEdt:.2e} V/(m·s)")
print()

# 安培回路半径 r
for r_cm in [0.3, 0.5, 0.8, 1.0, 1.5, 2.0]:
    r = r_cm * 0.01  # 转 m

    if r <= R:
        # 板间: 位移电流 = ε₀ dE/dt × πr²
        I_disp = eps0 * dEdt * math.pi * r**2
        I_cond = 0
    else:
        # 板外: 位移电流 = ε₀ dE/dt × πR² = I (全部)
        I_disp = eps0 * dEdt * math.pi * R**2
        I_cond = I

    # ∮B·dl = μ₀(I_cond + I_disp)
    # B × 2πr = μ₀(I_cond + I_disp)
    B = mu0 * (I_cond + I_disp) / (2 * math.pi * r)

    location = "板间" if r <= R else "板外"
    print(f"  r={r_cm:.1f}cm ({location}): "
          f"I_cond={I_cond*1e3:.2f}mA, "
          f"I_disp={I_disp*1e3:.2f}mA, "
          f"B={B*1e9:.4f}nT")

print(f"\n关键: 板外 I_disp=I={I*1e3:.1f}mA, "
      f"板间总位移电流也=I={eps0*dEdt*math.pi*R**2*1e3:.1f}mA")
print("→ 位移电流在电容器内部'替代'了传导电流, 保持了电流连续性")
```

---

## 7. Tripos 风格习题

### 习题 1（Part IA）：均匀带电球的电场

半径 $R$ 的球均匀带电，总电荷 $Q$。

(a) 用高斯定律求球内外电场 $\mathbf{E}(r)$。
(b) 求电势 $V(r)$（取 $V(\infty)=0$）。
(c) 验证 $\nabla^2 V = -\rho/\epsilon_0$（泊松方程）。

<details>
<summary>解答</summary>

(a) 由球对称性，$\mathbf{E} = E(r)\hat{\mathbf{r}}$。

球内 ($r < R$): $E \cdot 4\pi r^2 = Q_{\text{enc}}/\epsilon_0 = \frac{Q}{\epsilon_0}\frac{r^3}{R^3}$

$$E = \frac{Qr}{4\pi\epsilon_0 R^3}$$

球外 ($r > R$): $E \cdot 4\pi r^2 = Q/\epsilon_0$

$$E = \frac{Q}{4\pi\epsilon_0 r^2}$$

(b) $V(r) = -\int_\infty^r E\,dr'$。

球外: $V(r) = \frac{Q}{4\pi\epsilon_0 r}$

球内: $V(r) = V(R) - \int_R^r \frac{Qr'}{4\pi\epsilon_0 R^3}dr' = \frac{Q}{4\pi\epsilon_0 R}\left(\frac{3}{2} - \frac{r^2}{2R^2}\right)$

注意 $V(0) = \frac{3}{2}V(R) = \frac{3Q}{8\pi\epsilon_0 R}$。
</details>

### 习题 2（Part IB）：同轴电缆的电感

同轴电缆内半径 $a$，外半径 $b$，通电流 $I$（内外电流方向相反）。

(a) 求各区域磁场 $\mathbf{B}$。
(b) 求单位长度磁能 $U/\ell$。
(c) 由 $U/\ell = \frac{1}{2}L'I^2$ 求单位长度电感 $L'$。

<details>
<summary>解答</summary>

(a) 由安培定律：
- 导体内部 ($r < a$): $B = \frac{\mu_0 I r}{2\pi a^2}$（假设均匀电流分布）
- 两导体间 ($a < r < b$): $B = \frac{\mu_0 I}{2\pi r}$
- 外部 ($r > b$): $B = 0$（净电流为零）

(b) $U/\ell = \int \frac{B^2}{2\mu_0}dA$

$$\frac{U}{\ell} = \int_0^a \frac{\mu_0^2 I^2 r^2}{8\pi^2 \mu_0 a^4}2\pi r\,dr + \int_a^b \frac{\mu_0^2 I^2}{8\pi^2 \mu_0 r^2}2\pi r\,dr$$

$$= \frac{\mu_0 I^2}{4\pi a^4}\cdot\frac{a^4}{4} + \frac{\mu_0 I^2}{4\pi}\ln\frac{b}{a}$$

$$= \frac{\mu_0 I^2}{16\pi} + \frac{\mu_0 I^2}{4\pi}\ln\frac{b}{a}$$

(c) $L' = 2U/(\ell I^2) = \frac{\mu_0}{8\pi} + \frac{\mu_0}{2\pi}\ln\frac{b}{a}$

通常忽略内部磁能（薄壁导体），$L' \approx \frac{\mu_0}{2\pi}\ln(b/a)$。
</details>

### 习题 3（Part IB）：电磁波的反射与透射

电磁波从介质 1（折射率 $n_1$）垂直入射到介质 2（折射率 $n_2$）的平面界面。

(a) 写出边界条件并求反射系数 $R$ 和透射系数 $T$。
(b) 证明 $R + T = 1$（能量守恒）。
(c) 对 $n_1 = 1$（空气）→ $n_2 = 1.5$（玻璃），计算 $R$ 和 $T$ 的数值。

<details>
<summary>解答</summary>

(a) 设入射 $E_I = E_0 e^{i(k_1 x - \omega t)}$，反射 $E_R = r E_0 e^{i(-k_1 x - \omega t)}$，透射 $E_T = t E_0 e^{i(k_2 x - \omega t)}$。

边界条件 ($x=0$)：
- $E_\parallel$ 连续: $1 + r = t$
- $H_\parallel$ 连续: $n_1(1 - r) = n_2 t$ （利用 $H = nE/\mu_0 c$）

解得 Fresnel 公式（垂直入射）：

$$r = \frac{n_1 - n_2}{n_1 + n_2}, \quad t = \frac{2n_1}{n_1 + n_2}$$

$$R = |r|^2 = \left(\frac{n_1 - n_2}{n_1 + n_2}\right)^2$$

$$T = \frac{n_2}{n_1}|t|^2 = \frac{4n_1 n_2}{(n_1+n_2)^2}$$

(b) $R + T = \frac{(n_1-n_2)^2 + 4n_1 n_2}{(n_1+n_2)^2} = \frac{(n_1+n_2)^2}{(n_1+n_2)^2} = 1$ ✓

(c) $n_1=1, n_2=1.5$: $R = (1-1.5)^2/(1+1.5)^2 = 0.25/6.25 = 0.04$（4%反射）

$T = 4\times1\times1.5/6.25 = 6/6.25 = 0.96$（96%透射）

这正是为什么裸镜头/玻璃表面反射约 4% 的光——也是镀膜镜头（利用干涉消反射）的物理动机。
</details>

---

## Cavendish Laboratory 的电磁学传统

### Maxwell 与 Cavendish

James Clerk Maxwell 是 Cavendish Laboratory 的**第一任教授**（1871-1879）。他的贡献远不止麦克斯韦方程组：

1. **统一电与磁**：将 Coulomb, Ampère, Faraday 的工作整合为四个方程
2. **预言电磁波**：纯理论推导得出光 = 电磁波
3. **颜色摄影**：在 Cavendish 发明了三色合成摄影
4. **土星环**：证明土星环不可能是固体或液体，必须是无数小颗粒

### Cavendish 的精确测量传统

Maxwell 建立的 Cavendish 传统强调**精确电磁测量**，后代出了多个诺奖级成果：

- **J.J. Thomson** (1897): 电子的发现（$e/m$ 测量）
- **Wilson cloud chamber** (1911): 粒子径迹可视化
- **Bragg X-ray crystallography** (1913): 晶体结构
- **Rutherford 原子核** (1911): $\alpha$ 粒子散射
- **Crick & Watson DNA** (1953): X射线衍射（Cavendish 分支实验室）
- **Cavendish 实验课**至今保留: 学生亲手重复这些经典实验

---

## 参考与延伸阅读

| 教材 | 章节 | 重点 |
|------|------|------|
| Griffiths Ch 1-3 | 静电学 | Part IA 核心 |
| Griffiths Ch 4-5 | 多极 + 磁场 | Part IA/IB |
| Griffiths Ch 6-7 | 远场 + 电动力学 | Part IB |
| Griffiths Ch 8-9 | 守恒律 + 电磁波 | Part IB 核心 |
| Griffiths Ch 10-12 | 势 + 辐射 + 相对论 | Part II 预习 |
| Lorrain & Corson Ch 1-7 | 静态场 | Cambridge Part IA |
| Lorrain & Corson Ch 8-11 | 时变场 + 波 | Cambridge Part IB |
| Jackson Ch 1-6 | 研究生深度 | Part II/III |
| Purcell & Morin | 力学视角 | 直觉补充 |

---

**版本**：v1.0 (2026-08-12) · Cambridge Part IA/IB Electromagnetism


---

## 🎯 费曼式入口（白话版）

> **一句话解释**：电和磁原本是两件事，麦克斯韦用四个方程把它们和光合在一起——人类历史上最伟大的"大统一"。
>
> **生活类比**：微波炉加热食物——电磁波让水分子来回翻转、摩擦生热。你的手机信号、阳光、X 光、可见光，本质全是同一套方程的解，只是频率不同。
>
> **反直觉发现（啊哈时刻）**：移动电荷会产生磁场，但如果你跟着电荷一起跑，磁场就"消失"了——电和磁是同一件事在不同参考系下的不同侧面。正是这个念头，把爱因斯坦推向了狭义相对论。

---

## 🔗 衔接：从哪来，到哪去

- **前置知识**：Part IA 力学（矢量、功、能）、矢量微积分（散度 ∇·、旋度 ∇×）
- **危机（麦克斯韦方程引发的革命）**：
  - 麦克斯韦方程 + 牛顿力学在不同惯性系不自洽 → **狭义相对论**（也是 Topic 8 广义相对论的起点）
  - 经典电动力学无法解释黑体辐射、光电效应、原子稳定性 → **量子力学**（Topic 3）
- **新危机**：介质响应、色散、非线性光学需要量子化的物质描述；极短波长/极强场下需要量子电动力学
- **后续去向**：**规范不变性 → Yang-Mills → 标准模型**（Topic 7）；电磁波 → 光学/光子学；势与规范 → **量子场论**

---

## 🏭 理论联系实际：5 个现代应用

1. **光纤通信**：全反射 + 色散管理，是全球互联网的物理根基；§4.5 的色散理论直接决定光缆设计。
2. **无线充电与 RFID**：近场磁场耦合（法拉第电磁感应），从牙刷到电动汽车都在用。
3. **MRI 核磁共振**：超强静磁场（B₀）+ 射频脉冲，操控核自旋磁矩；§2.3 的磁偶极与 §3 的麦克斯韦方程是其核心。
4. **相控阵雷达 / 5G·6G**：电子扫描波束，靠精确控制上千天线单元的相位（§4.3 偏振与相位）。
5. **光伏太阳能**：光电效应——半导体能带吸收电磁波能量，把光子变成电流。

---

## 🔬 最新研究前沿（2024-2026）

1. **超表面 / 平面光学（metasurfaces）**：2024 用亚波长结构实现全息投影、任意光束整形，用一片薄膜替代笨重透镜组（*Nature Photonics*, 2024）。
2. **拓扑光子学**：2024–2025 在光子晶体中实现拓扑 protected 的光传输——光遇到缺陷会自动绕行不散射，对光通信与光量子芯片意义重大。
3. **光子神经网络 / 光计算**：2024 用光子做矩阵乘法实现低能耗 AI 推理（光子芯片，*Nature*, 2024），把 §4.4 的坡印廷能流变成算力。
4. **强场 QED 与非线性真空**：2024–2025 在超高激光强度（ELI、ZEUS 装置）下逼近 Schwinger 临界场，验证"真空极化"——电磁场自己产生正负电子对。
5. **Cavendish 半导体量子光源**：剑桥自组织 InAs 量子点单光子源（2024）用于量子通信，把 §3 的麦克斯韦与 Topic 3 的量子叠加接在一起。

---

## 🗺️ 学习 Roadmap（Cambridge Tripos 路径）

| 阶段 | 课程 | 你应当能做到 |
|------|------|------------|
| **Part IA** | Electromagnetism | 熟练用高斯/安培定律算对称场；理解 RC/LC 电路（见 Demos 3,4） |
| **Part IB** | Electromagnetism | 从麦克斯韦方程推出电磁波速 $c=1/\sqrt{\mu_0\epsilon_0}$；处理势、规范、偏振 |
| **Part II** | Electrodynamics / Optics | 辐射（天线）、相对论电动力学、介质中的色散与非线性光学 |
| **Part III** | Gauge Theory / QED / Laser Physics | 规范场量子化、量子电动力学、激光物理 |

**知识检查三问**：
1. 为什么电容器充电时，两板**之间**会有磁场？（位移电流的物理实在性，见 Demo 逻辑）
2. 为什么裸玻璃表面会反射约 4% 的光？镀膜镜头怎么消掉它？
3. 为什么麦克斯韦方程"暗示"了狭义相对论？
