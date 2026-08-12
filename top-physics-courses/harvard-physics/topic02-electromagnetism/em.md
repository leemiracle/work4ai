# Harvard 电磁学 — Phys 15b / 153

> **课程**：Phys 15b (Electromagnetism) · Phys 153 (Electrodynamics)
> **教材**：Purcell & Morin *Electricity and Magnetism* 3ed (2013) · Griffiths *Introduction to Electrodynamics* 4ed (2013)
> **一手来源**：[Harvard Physics Catalog](https://www.physics.harvard.edu/academics/courses)（2026-08 核实）

---

## 🎓 Harvard 特色：Georgi 直观教学法 + Purcell 的相对论视角

### Howard Georgi 的"波的物理学"

Howard Georgi（Harvard 物理系，执教 Phys 15c 数十年）著有 *The Physics of Waves*（免费在线），以 **色散关系** 为核心线索统一处理所有波现象——从弦上波到电磁波到量子德布罗意波。他的教学信条：

> *"Don't memorize equations. Understand the dispersion relation $\omega(k)$, and everything else follows."*

Georgi 强调**图象化思维**：每个波现象先用时空图画出，再写方程。这种方法使得 Maxwell 方程组的电磁波解变得"理所当然"。

### Purcell 的相对论视角（Berkeley Physics Course Vol. 2）

Purcell & Morin 教材的最大特色是用 **狭义相对论** 推导磁力的存在：

> 磁力不是独立的力——它是电场力在不同惯性系中的相对论修正。

这一视角让学生理解：**电和磁本质上是统一的**，Maxwell 方程组的优美性正是相对性原理的体现。

---

## 第一部分：静电学（Phys 15b, Purcell Ch.1-3, Griffiths Ch.2）

### 1.1 库仑定律

两个点电荷之间的力：
$$\vec{F}_{12} = \frac{1}{4\pi\epsilon_0}\frac{q_1 q_2}{r^2}\hat{r}_{12}$$

库仑常数 $k = 1/(4\pi\epsilon_0) \approx 8.99 \times 10^9\,\text{N·m}^2/\text{C}^2$。

### 1.2 电场

点电荷产生的电场：
$$\vec{E} = \frac{1}{4\pi\epsilon_0}\frac{q}{r^2}\hat{r}$$

连续电荷分布：
$$\vec{E}(\vec{r}) = \frac{1}{4\pi\epsilon_0}\int \frac{\rho(\vec{r}')(\vec{r}-\vec{r}')}{|\vec{r}-\vec{r}'|^3}d^3r'$$

### 1.3 高斯定律

$$\oint_S \vec{E}\cdot d\vec{A} = \frac{Q_{\text{enc}}}{\epsilon_0}$$

微分形式：$\nabla\cdot\vec{E} = \rho/\epsilon_0$

**高斯定律的威力**：当电荷分布有足够对称性（球、柱、面）时，可以直接求 $\vec{E}$ 而无需积分。

**例（无限长均匀带电直线，线电荷密度 $\lambda$）**：

取同轴圆柱高斯面，半径 $r$，长度 $L$：
$$E \cdot 2\pi r L = \frac{\lambda L}{\epsilon_0} \implies E = \frac{\lambda}{2\pi\epsilon_0 r}$$

### 1.4 电势

电场是电势的负梯度：$\vec{E} = -\nabla V$

点电荷电势：$V = \frac{1}{4\pi\epsilon_0}\frac{q}{r}$

电势满足泊松方程：$\nabla^2 V = -\rho/\epsilon_0$

### 1.5 电偶极子

电偶极矩 $\vec{p} = q\vec{d}$（$\vec{d}$ 从 $-q$ 指向 $+q$）。

远场（偶极近似）：
$$V_{\text{dip}} = \frac{1}{4\pi\epsilon_0}\frac{\vec{p}\cdot\hat{r}}{r^2}$$

$$\vec{E}_{\text{dip}} = \frac{1}{4\pi\epsilon_0}\frac{1}{r^3}\left[3(\vec{p}\cdot\hat{r})\hat{r} - \vec{p}\right]$$

> **反直觉**：偶极电场随 $1/r^3$ 衰减，比点电荷的 $1/r^2$ 快得多——正负电荷的场在大距离处几乎完全抵消。

### 1.6 导体与电容

导体内 $\vec{E} = 0$（静电平衡），电荷分布在表面。

平行板电容器：$C = \epsilon_0 A / d$

储存能量：$U = \frac{1}{2}CV^2 = \frac{Q^2}{2C} = \frac{1}{2}\epsilon_0 E^2 \cdot (\text{体积})$

> 💡 **关键洞察**：能量储存在**场**中而非电荷上。能量密度 $u = \frac{1}{2}\epsilon_0 E^2$。这一观点是 Purcell 教材反复强调的核心物理图像。

---

## 第二部分：静磁学（Phys 15b, Purcell Ch.5-6, Griffiths Ch.5）

### 2.1 Purcell 的相对论推导

Purcell 教材的招牌：从库仑定律+相对论推出磁力。

考虑一根载流导线旁有一个运动的测试电荷。在实验室系中，导线呈电中性但载流，电荷受磁力。换到电荷静止系——导线中的正离子和电子因长度收缩不同而不再抵消，出现净电荷，电荷受**电力**。

定量结果：磁力 $F_B = qvB$ 恰好等于相对论修正后的电力。

### 2.2 毕奥-萨伐尔定律

电流元产生的磁场：
$$d\vec{B} = \frac{\mu_0}{4\pi}\frac{I\,d\vec{l}\times\hat{r}}{r^2}$$

**例（无限长直导线，电流 $I$）**：
$$B = \frac{\mu_0 I}{2\pi r}$$

### 2.3 安培定律

$$\oint_C \vec{B}\cdot d\vec{l} = \mu_0 I_{\text{enc}}$$

微分形式：$\nabla\times\vec{B} = \mu_0\vec{J}$

**例（长螺线管内部）**：$B = \mu_0 n I$（$n$ = 单位长度匝数），内部均匀，外部近似为零。

### 2.4 磁矢势

$\vec{B} = \nabla\times\vec{A}$（自动满足 $\nabla\cdot\vec{B} = 0$，即无磁单极）

库仑规范 $\nabla\cdot\vec{A} = 0$ 下：
$$\vec{A}(\vec{r}) = \frac{\mu_0}{4\pi}\int \frac{\vec{J}(\vec{r}')}{|\vec{r}-\vec{r}'|}d^3r'$$

### 2.5 洛伦兹力

$$\vec{F} = q(\vec{E} + \vec{v}\times\vec{B})$$

磁场对运动电荷不做功（$\vec{v}\cdot(\vec{v}\times\vec{B})=0$），只改变方向。

---

## 第三部分：麦克斯韦方程组（Phys 153, Griffiths Ch.7）

### 3.1 四个方程

| 方程 | 积分形式 | 微分形式 | 物理意义 |
|------|---------|---------|---------|
| 高斯定律(电) | $\oint\vec{E}\cdot d\vec{A} = Q/\epsilon_0$ | $\nabla\cdot\vec{E} = \rho/\epsilon_0$ | 电荷是电场源 |
| 高斯定律(磁) | $\oint\vec{B}\cdot d\vec{A} = 0$ | $\nabla\cdot\vec{B} = 0$ | 无磁单极 |
| 法拉第定律 | $\oint\vec{E}\cdot d\vec{l} = -d\Phi_B/dt$ | $\nabla\times\vec{E} = -\partial\vec{B}/\partial t$ | 变化的B产生E |
| 安培-麦克斯韦 | $\oint\vec{B}\cdot d\vec{l} = \mu_0(I + \epsilon_0 d\Phi_E/dt)$ | $\nabla\times\vec{B} = \mu_0\vec{J}+\mu_0\epsilon_0\frac{\partial\vec{E}}{\partial t}$ | 电流+变化E产生B |

### 3.2 位移电流——Maxwell 的天才修正

安培定律的原始形式 $\nabla\times\vec{B} = \mu_0\vec{J}$ 在**电容器充电**时矛盾：极板间无电流 $J=0$，但磁场不为零。

Maxwell 加入**位移电流** $\epsilon_0\partial\vec{E}/\partial t$，修正为：

$$\nabla\times\vec{B} = \mu_0\vec{J} + \mu_0\epsilon_0\frac{\partial\vec{E}}{\partial t}$$

这一项使得方程组自洽，并预言了电磁波。

### 3.3 电磁波的预言（Griffiths 9.2）

在真空中（$\rho=0$, $\vec{J}=0$），对法拉第定律取旋度，利用矢量恒等式 $\nabla\times(\nabla\times\vec{E})=\nabla(\nabla\cdot\vec{E})-\nabla^2\vec{E}$：

$$\nabla^2\vec{E} = \mu_0\epsilon_0\frac{\partial^2\vec{E}}{\partial t^2}$$

这是波动方程！波速：
$$c = \frac{1}{\sqrt{\mu_0\epsilon_0}} \approx 3\times 10^8\,\text{m/s}$$

> 🏆 **物理史最伟大的时刻之一**：Maxwell 从纯电磁理论计算出 $c = 1/\sqrt{\mu_0\epsilon_0}$，发现这个速度等于光速，由此断言"光是一种电磁扰动"。

---

## 第四部分：电磁波与辐射（Phys 153, Griffiths Ch.9-11）

### 4.1 平面波解

$$\vec{E}(z,t) = \vec{E}_0\cos(kz - \omega t), \quad \vec{B}(z,t) = \vec{B}_0\cos(kz - \omega t)$$

关键关系：
- $\vec{E} \perp \vec{B} \perp \hat{k}$（横波）
- $|\vec{E}| = c|\vec{B}|$
- 色散关系：$\omega = ck$

### 4.2 偏振

线偏振：$\vec{E}$ 始终沿固定方向振荡。

圆偏振：$\vec{E}$ 端点做圆周运动 $\vec{E} = E_0(\hat{x}\pm i\hat{y})e^{i(kz-\omega t)}$

> 🔗 **Georgi 的色散关系视角**：真空中 $\omega = ck$（线性色散），所有频率等速传播。在介质中 $\omega(k)$ 变弯曲→色散→棱镜分光。

### 4.3 坡印廷矢量与辐射压

能流密度：$\vec{S} = \frac{1}{\mu_0}\vec{E}\times\vec{B}$

时间平均强度：$\langle S \rangle = \frac{1}{2}c\epsilon_0 E_0^2$

辐射压（全吸收）：$P = \langle S \rangle / c$

### 4.4 偶极辐射（Griffiths 11.1）

振荡电偶极子 $\vec{p}(t) = p_0\cos(\omega t)\hat{z}$ 的远场辐射：

$$\langle S \rangle = \frac{\mu_0 p_0^2\omega^4}{32\pi^2 c}\frac{\sin^2\theta}{r^2}$$

总辐射功率（拉莫尔公式）：
$$P = \frac{\mu_0 p_0^2\omega^4}{12\pi c}$$

> **反直觉**：辐射功率 $\propto \omega^4$！频率翻倍，辐射增强 16 倍。这就是为什么天线需要高频、为什么蓝光散射比红光强（瑞利散射 $\propto 1/\lambda^4$，天空是蓝色的）。

---

## 第五部分：介质中的电磁学（Phys 153, Griffiths Ch.4, 6）

### 5.1 电介质

极化强度 $\vec{P}$，电位移 $\vec{D} = \epsilon_0\vec{E} + \vec{P} = \epsilon\vec{E}$

线性介质：$\vec{P} = \epsilon_0\chi_e\vec{E}$，相对介电常数 $\epsilon_r = 1+\chi_e$

### 5.2 磁介质

磁化强度 $\vec{M}$，磁场强度 $\vec{H} = \vec{B}/\mu_0 - \vec{M} = \vec{B}/\mu$

线性介质：$\vec{M} = \chi_m\vec{H}$，相对磁导率 $\mu_r = 1+\chi_m$

| 类型 | $\chi_m$ | 例子 |
|------|---------|------|
| 抗磁 | $< 0$（极小） | 铜、水、金 |
| 顺磁 | $> 0$（极小） | 铝、铂 |
| 铁磁 | $\gg 0$（非线性） | 铁、钴、镍 |

### 5.3 边界条件

在两种介质交界面上：
- $D_\perp$ 和 $B_\perp$ 连续（无自由面电荷/磁单极时）
- $E_\parallel$ 和 $H_\parallel$ 连续（无自由面电流时）

---

## 📝 习题精选

### 习题 1（Phys 15b 级，高斯定律）

一个半径为 $R$ 的均匀带电球体（体电荷密度 $\rho$），求球内和球外的电场。

> **答案**：球外 $E = \rho R^3/(3\epsilon_0 r^2)$；球内 $E = \rho r/(3\epsilon_0)$。球心处 $E=0$，表面处最大。

### 习题 2（Phys 15b 级，Purcell 相对论）

一导线载流 $I$，正离子静止（线密度 $\lambda_+$），电子以速度 $v$ 漂移（线密度 $\lambda_-$）。实验室系中 $\lambda_+ = |\lambda_-|$，导线中性。一个电荷 $q$ 以速度 $v$（与电子同向同速）平行于导线运动。证明：在 $q$ 的静止系中，导线带净电荷，$q$ 受电力。

> **提示**：在 $q$ 的静止系中，运动的正离子发生洛伦兹收缩，$\lambda'_+ \neq \lambda'_-$。

### 习题 3（Phys 153 级，法拉第定律）

一个半径 $r$ 的圆形线圈电阻 $R$，置于随时间线性增长的均匀磁场 $B = \alpha t$ 中（线圈面垂直于B）。求感应电流和线圈受到的力矩。

> **答案**：$\varepsilon = -\pi r^2 \alpha$，$I = \pi r^2\alpha/R$。力矩=0（线圈无磁矩，因为这里线圈只是回路）。

### 习题 4（Phys 153 级，电磁波）

真空中一束激光强度 $I = 1\,\text{kW/m}^2$。求电场振幅和辐射压。

> **答案**：$E_0 = \sqrt{2I/(c\epsilon_0)} \approx 868\,\text{V/m}$；辐射压（全吸收）$P = I/c \approx 3.3\times10^{-6}\,\text{Pa}$。

### 习题 5（Phys 153 级，位移电流）

圆形平行板电容器半径 $R$，充电电流 $I$。求极板间的位移电流密度和距中心轴 $r$ 处的感生磁场。

> **答案**：$J_d = I/(\pi R^2)$；$r < R$ 时 $B = \mu_0 Ir/(2\pi R^2)$。

---

## 💻 Python 代码

### 代码 1：电场矢量场可视化（偶极子）

```python
"""
电偶极子电场线与等势线计算
纯数值计算，用文本/数值输出
"""
import math

k = 8.99e9  # 库仑常数
q = 1.6e-19
d = 1e-10   # 偶极间距

def E_field(x, y):
    """计算 (x,y) 处的电偶极子电场分量"""
    # 正电荷在 (d/2, 0), 负电荷在 (-d/2, 0)
    dx_p = x - d/2
    dx_n = x + d/2

    r_p = math.sqrt(dx_p**2 + y**2)
    r_n = math.sqrt(dx_n**2 + y**2)

    Ex = k*q * (dx_p/r_p**3 - dx_n/r_n**3)
    Ey = k*q * (y/r_p**3 - y/r_n**3)
    return Ex, Ey

# 在赤道面(y=0)和轴线上(x轴)采样
print("=== 赤道面电场 (应指向 -x 方向) ===")
for x in [2*d, 5*d, 10*d, 20*d]:
    Ex, Ey = E_field(x, 0.001*d)  # 微小y避免除零
    print(f"  x={x/d:.0f}d: Ex={Ex:.3e} V/m")

print("\n=== 偶极场 1/r³ 衰减验证 ===")
p = q * d  # 偶极矩
for r in [2*d, 4*d, 8*d, 16*d]:
    # 轴线上理论值: E ≈ 2kp/r³
    E_theory = 2*k*p / r**3
    Ex, _ = E_field(r, 0.001*d)
    ratio = Ex / E_theory
    print(f"  r={r/d:.0f}d: E_num={Ex:.3e} E_theory={E_theory:.3e} ratio={ratio:.4f}")
print("(ratio → 1 验证 1/r³ 衰减)")
```

### 代码 2：电磁波传播（一维 FDTD）

```python
"""
一维时域有限差分(FDTD)模拟电磁波传播
展示 Maxwell 方程的数值解
"""
import math

# 参数
N = 200        # 空间网格数
steps = 500    # 时间步数
c = 1.0        # 归一化光速
dx = 1.0
dt = 0.5 * dx / c  # CFL条件: dt < dx/c

E = [0.0] * N   # 电场
B = [0.0] * N   # 磁场(半步交错)

# 初始条件: 高斯脉冲在中心
center = N // 2
for i in range(N):
    E[i] = math.exp(-0.01 * (i - center)**2)

print("=== 电磁波传播模拟 ===")
print(f"网格: {N}, 步数: {steps}, dt={dt}, CFL数={c*dt/dx:.2f}")

for step in range(steps):
    # 更新 B (法拉第定律): dB/dt = -dE/dx
    for i in range(N-1):
        B[i] -= (dt/dx) * (E[i+1] - E[i])
    B[N-1] = B[N-2]  # 边界

    # 更新 E (安培定律): dE/dt = -c² dB/dx
    for i in range(1, N):
        E[i] -= (c**2 * dt/dx) * (B[i] - B[i-1])
    E[0] = E[1]  # 边界

    # 输出波包位置
    if step % 100 == 0:
        peak = max(range(N), key=lambda i: abs(E[i]))
        print(f"  step={step:4d}: 峰值位置={peak}, 峰值={E[peak]:.4f}")

print("\n结论: 脉冲以速度 c 向两侧传播 (Maxwell方程的数值验证)")
```

### 代码 3：Maxwell 方程组验证——光速计算

```python
"""
从 Maxwell 方程组计算光速: c = 1/√(μ₀ε₀)
验证 Maxwell 的伟大预言
"""
import math

# 真空常数（SI）
epsilon_0 = 8.854187817e-12  # F/m
mu_0 = 4 * math.pi * 1e-7    # N/A² (精确值)

c_maxwell = 1.0 / math.sqrt(mu_0 * epsilon_0)
c_measured = 299792458.0     # 精确值（SI 定义）

print("=== Maxwell 的光速预言 ===")
print(f"ε₀ = {epsilon_0:.10e} F/m")
print(f"μ₀ = {mu_0:.10e} N/A² (精确)")
print(f"c = 1/√(μ₀ε₀) = {c_maxwell:.4f} m/s")
print(f"c (定义值)    = {c_measured:.4f} m/s")
print(f"相对误差     = {abs(c_maxwell-c_measured)/c_measured:.2e}")
print()
print("💡 Maxwell 从电磁理论推导出光速, 断言光是电磁波!")
print(f"   1/(μ₀ε₀) = {1/(mu_0*epsilon_0):.6e}")

# 能量密度比较
E0 = 1000.0  # V/m 的电场
u_E = 0.5 * epsilon_0 * E0**2
B0 = E0 / c_measured
u_B = B0**2 / (2 * mu_0)
print(f"\n=== 电磁波能量密度 ===")
print(f"E₀ = {E0} V/m → u_E = ε₀E₀²/2 = {u_E:.4e} J/m³")
print(f"B₀ = E₀/c = {B0:.4e} T → u_B = B₀²/(2μ₀) = {u_B:.4e} J/m³")
print(f"u_E = u_B? 比值 = {u_E/u_B:.6f} (电磁波中电场能=磁场能)")
```

---

## 📚 两本教材对比

| 教材 | 视角 | 优势 | 适合 |
|------|------|------|------|
| **Purcell & Morin** | 相对论出发，先磁力的物理本质 | 物理直觉深，电磁统一 | Phys 15b（入门+深度） |
| **Griffiths** | 传统矢量分析，工程化 | 系统全面，习题丰富 | Phys 153（中级+标准） |

**Purcell 的独特价值**：用相对论解释磁力后，学生理解了 $\vec{E}$ 和 $\vec{B}$ 不是独立实体——它们是同一个电磁场张量 $F^{\mu\nu}$ 在不同参考系中的分量。

---

## 🔗 衔接

- **← Phys 15a（力学）**：牛顿运动定律、能量/动量守恒是基础
- **→ Phys 15c（波与光学）**：电磁波 → 几何光学、物理光学、干涉衍射
- **→ Phys 143a（量子力学）**：原子中的电磁相互作用是量子力学的核心舞台
- **→ Phys 210（广义相对论）**：Maxwell 方程组的洛伦兹协变性 → 广义协变性

---

*完成日期：2026-08-12 | 基于 Harvard Physics Catalog + Purcell/Morin + Griffiths 教材*
