# Topic 02 — 电动力学：从静电到电磁波

> **Oxford MPhys · Year 2 Electromagnetism**
> 教材：David J. Griffiths *Introduction to Electrodynamics* 4ed (2013) — 10/10 校共用
> 覆盖：静电学、静磁学、麦克斯韦方程组、电磁波

---

## 目录

1. [课程定位](#1-课程定位)
2. [向量分析工具箱](#2-向量分析工具箱)
3. [静电学](#3-静电学)
4. [静磁学](#4-静磁学)
5. [麦克斯韦方程组与时变场](#5-麦克斯韦方程组与时变场)
6. [电磁波](#6-电磁波)
7. [反直觉实验 (Python)](#7-反直觉实验-python)
8. [Tutorial 习题](#8-tutorial-习题)
9. [局限与延伸阅读](#9-局限与延伸阅读)

---

## 1. 课程定位

| 学期 | 主题 | Griffiths 章节 |
|------|------|---------------|
| HT (Hilary) 前半 | 静电学 | Ch.1-3 |
| HT 后半 | 静磁学 | Ch.5 |
| TT (Trinity) | 时变场 + 麦克斯韦 + 电磁波 | Ch.7-9 |

Oxford Y1 已用 Griffiths Ch.1-7 打底；Y2 完成全书并引入推迟势、辐射。Jackson 留到 Y3/Y4。

---

## 2. 向量分析工具箱

### 2.1 三定理 (Griffiths §1.6)

$$
\boxed{\text{梯度定理}:\quad V(\mathbf{b})-V(\mathbf{a})=\int_{\mathbf{a}}^{\mathbf{b}}\nabla V\cdot d\mathbf{l}}
$$

$$
\boxed{\text{散度定理}:\quad \oint_S \mathbf{F}\cdot d\mathbf{a}=\int_V(\nabla\cdot\mathbf{F})\,d\tau}
$$

$$
\boxed{\text{斯托克斯定理}:\quad \oint_C \mathbf{F}\cdot d\mathbf{l}=\int_S(\nabla\times\mathbf{F})\cdot d\mathbf{a}}
$$

### 2.2 两个恒等式（反复用到）

$$
\nabla\times(\nabla V)=\mathbf{0},\qquad \nabla\cdot(\nabla\times\mathbf{F})=0
$$

> **直觉**：梯度场无旋，旋度场无散——这两条是静电势 $V$ 和磁矢势 $\mathbf{A}$ 存在性的根据。

---

## 3. 静电学

### 3.1 库仑定律与电场 (Griffiths §2.1)

点电荷 $q$ 在原点：
$$
\mathbf{E}(\mathbf{r})=\frac{1}{4\pi\epsilon_0}\frac{q}{r^2}\hat{\mathbf{r}}
$$

连续分布推广为积分 $\mathbf{E}=\frac{1}{4\pi\epsilon_0}\int\rho(\mathbf{r}')\frac{\hat{\boldsymbol{\mathcal{R}}}}{\mathcal{R}^2}d\tau'$，$\boldsymbol{\mathcal R=\mathbf{r}-\mathbf{r}'}$。

### 3.2 高斯定律 (Griffiths §2.2)

积分形式：$\oint\mathbf{E}\cdot d\mathbf{a}=Q_{\text{enc}}/\epsilon_0$；微分形式：
$$
\boxed{\;\nabla\cdot\mathbf{E}=\frac{\rho}{\epsilon_0}\;}
$$

**用途**：仅在**高度对称**（球/柱/面对称）时能直接算 $\mathbf{E}$。Oxford tutorial 常考的反例：均匀带电立方体不能用高斯定律解析求解。

### 3.3 电势与泊松方程 (Griffiths §2.3-3.1)

$\nabla\times\mathbf{E}=0\Rightarrow\mathbf{E}=-\nabla V$，代入高斯定律：
$$
\boxed{\;\nabla^2 V=-\frac{\rho}{\epsilon_0}\quad\text{(泊松方程)},\qquad \rho=0\Rightarrow\nabla^2V=0\ \text{(拉普拉斯方程)}\;}
$$

### 3.4 唯一性定理 (Griffiths §3.1.6) — Oxford 反复强调

> 在体积 $V$ 内，若 $\rho$ 给定，且边界 $S$ 上 $V$ 或 $\partial V/\partial n$ 给定，则 $V$ 内的 $V$ **唯一**。

这是镜像法、分离变量法**有效性的根据**——只要找到一个满足边界条件的解，它就是解。

### 3.5 多极展开 (Griffiths §3.4)

远处任意分布的势展开：
$$
V(\mathbf{r})=\frac{1}{4\pi\epsilon_0}\left[\frac{Q}{r}+\frac{\mathbf{p}\cdot\hat{\mathbf{r}}}{r^2}+\frac{1}{2}\sum_{ij}Q_{ij}\frac{\hat r_i\hat r_j}{r^3}+\cdots\right]
$$

- 单极 $Q=\int\rho\,d\tau$
- 偶极 $\mathbf{p}=\int\mathbf{r}'\rho\,d\tau'$
- 四极 $Q_{ij}=\int(3x_i'x_j'-r'^2\delta_{ij})\rho\,d\tau'$

> **反直觉**：电偶极场 $\propto 1/r^3$，但偶极-偶极相互作用 $\propto 1/r^3$，而偶极辐射功率 $\propto 1/r^2$（因坡印廷矢量积分）。维度分析须区分**近场静态**与**辐射场**。

---

## 4. 静磁学

### 4.1 洛伦兹力与毕奥-萨伐尔 (Griffiths §5.1-5.2)

$$
\mathbf{F}=q(\mathbf{E}+\mathbf{v}\times\mathbf{B}),\qquad 
\mathbf{B}(\mathbf{r})=\frac{\mu_0}{4\pi}\int\frac{I\,d\mathbf{l}'\times\hat{\boldsymbol{\mathcal R}}}{\mathcal{R}^2}
$$

### 4.2 安培定律 (Griffiths §5.3)

$$
\boxed{\;\oint\mathbf{B}\cdot d\mathbf{l}=\mu_0 I_{\text{enc}},\qquad \nabla\times\mathbf{B}=\mu_0\mathbf{J}\;}
$$

**标准 tutorial**（Griffiths Ex.5.8）：长直螺线管内部 $\mathbf{B}=\mu_0 n I\hat{\mathbf{z}}$，外部为零。这要求把安培定律用于跨过管壁的矩形环路。

### 4.3 磁矢势 (Griffiths §5.4)

$\nabla\cdot\mathbf{B}=0\Rightarrow\mathbf{B}=\nabla\times\mathbf{A}$，库仑规范 $\nabla\cdot\mathbf{A}=0$ 下：
$$
\nabla^2\mathbf{A}=-\mu_0\mathbf{J}
$$

### 4.4 磁偶极子

电流圈磁矩 $\mathbf{m}=I\mathbf{a}$（$\mathbf{a}$ 为有向面积），远场：
$$
\mathbf{B}_{\text{dip}}=\frac{\mu_0}{4\pi r^3}\left[2\cos\theta\,\hat{\mathbf r}+\sin\theta\,\hat{\boldsymbol\theta}\right]m
$$

形式上与电偶极场**完全平行**——这是 Griffiths §5.4.3 着重指出的「双层结构」对称美。

---

## 5. 麦克斯韦方程组与时变场

### 5.1 法拉第定律 (Griffiths §7.1-7.2)

$$
\boxed{\;\nabla\times\mathbf{E}=-\frac{\partial\mathbf{B}}{\partial t},\qquad \mathcal{E}=-\frac{d\Phi_B}{dt}\;}
$$

发电机、变压器、涡流制动都源于此。Lenz 定律给负号以直觉解释：感应电流**反抗**磁通变化。

### 5.2 位移电流 (Griffiths §7.3) — Maxwell 的关键修补

安培定律 $\nabla\times\mathbf{B}=\mu_0\mathbf{J}$ 在充电电容情形矛盾：两极板间 $\mathbf{J}=0$ 但 $\mathbf{B}\neq0$。Maxwell 加位移电流：
$$
\boxed{\;\nabla\times\mathbf{B}=\mu_0\mathbf{J}+\mu_0\epsilon_0\frac{\partial\mathbf{E}}{\partial t}\;}
$$

这一项是电磁波存在的**充要条件**——没有它，§6 的波速将是无穷大，而非 $c$。

### 5.3 麦克斯韦方程组完整形式 (真空)

$$
\boxed{
\begin{aligned}
\nabla\cdot\mathbf{E}&=\frac{\rho}{\epsilon_0} &\quad\text{(I)}\\
\nabla\cdot\mathbf{B}&=0 &\quad\text{(II)}\\
\nabla\times\mathbf{E}&=-\frac{\partial\mathbf{B}}{\partial t} &\quad\text{(III)}\\
\nabla\times\mathbf{B}&=\mu_0\mathbf{J}+\mu_0\epsilon_0\frac{\partial\mathbf{E}}{\partial t} &\quad\text{(IV)}
\end{aligned}}
$$

**连续性方程** $\nabla\cdot\mathbf{J}+\partial\rho/\partial t=0$ 是 (I) 和 (IV) 的推论——电荷守恒被**编码**进方程组。

### 5.4 坡印廷矢量 (Griffiths §8.1.2)

能流密度：
$$
\mathbf{S}=\frac{1}{\mu_0}\mathbf{E}\times\mathbf{B}
$$

**反直觉**：直流电路中能量**不沿导线**流动，而是沿导线**周围的场**从电源直奔负载（Heaviside 最早指出）。

---

## 6. 电磁波

### 6.1 真空中的波方程

$\rho=\mathbf{J}=0$ 下取 (III) 的旋度，用 (IV) 消去 $\mathbf{B}$：
$$
\boxed{\;\nabla^2\mathbf{E}=\mu_0\epsilon_0\frac{\partial^2\mathbf{E}}{\partial t^2},\qquad c=\frac{1}{\sqrt{\mu_0\epsilon_0}}\;}
$$

代入常数 $\mu_0=4\pi\times10^{-7},\ \epsilon_0=8.854\times10^{-12}$ 算出 $c\approx2.998\times10^8\,\text{m/s}$——Maxwell 据此断言光是电磁波（1865）。

### 6.2 平面波的横波性 (Griffiths §9.2)

$$
\mathbf{E}(\mathbf{r},t)=\mathbf{E}_0 e^{i(\mathbf{k}\cdot\mathbf{r}-\omega t)},\qquad \mathbf{B}=\frac{1}{c}\hat{\mathbf{k}}\times\mathbf{E}
$$

由 (I)(II)：$\mathbf{k}\cdot\mathbf{E}=\mathbf{k}\cdot\mathbf{B}=0$——**横波**。$\mathbf{E},\mathbf{B},\mathbf{k}$ 构成右手正交三重矢量。

### 6.3 偏振

线偏振：$\mathbf{E}_0$ 固定方向。圆偏振：$\mathbf{E}_0=E_0(\hat{\mathbf{x}}\pm i\hat{\mathbf{y}})/\sqrt2$，正负号区分左/右旋。

### 6.4 反射与折射 (Griffiths §9.3.2)

边界条件（$\mathbf{E}_\parallel,\mathbf{B}_\parallel$ 连续，$\mathbf{D}_\perp,\mathbf{B}_\perp$ 连续）给出：
- Snell 定律：$n_1\sin\theta_i=n_2\sin\theta_t$
- Fresnel 公式（s 偏振）：
$$
\frac{E_r}{E_i}=\frac{n_1\cos\theta_i-n_2\cos\theta_t}{n_1\cos\theta_i+n_2\cos\theta_t}
$$

**Brewster 角** $\tan\theta_B=n_2/n_1$ 时反射光完全 s 偏振——偏振片的物理基础。

---

## 7. 反直觉实验 (Python)

> **镜像法 vs 直接积分对比**：点电荷 $+q$ 置于接地导体球（半径 $R$）外，距离 $d$。Griffiths §3.2.1 的镜像法给出球面感应电荷总量 $Q_{\text{ind}}=-qR/d$。本实验用数值积分验证。

```python
#!/usr/bin/env python3
"""
接地导体球的感应电荷：镜像法 vs 数值积分
Griffiths Introduction to Electrodynamics §3.2.1
纯标准库。运行: python3 induced_charge.py
注意: 电荷置于 z 轴 (极轴), 保证 phi 对称性, 否则违反 Gauss 定律。
"""
import math

def image_charge(q, d, R):
    """镜像法: 像电荷 q' = -qR/d 位于球内 z = R^2/d 处"""
    return -q*R/d, R*R/d

def field_of(qc, zc, x, z):
    """电荷 qc 位于 (0,0,zc), 求在 (x,0,z) 处的电场 (单位 1/4pi eps0 = 1)"""
    dx, dz = x, z - zc
    r2 = dx*dx + dz*dz
    r3 = r2 * math.sqrt(r2)
    return [qc*dx/r3, qc*dz/r3]      # [Ex, Ez]

def induced_charge_numerical(q_real, d, R, n_theta=2000):
    """数值积分 ∮ E·n dA, 再除 4π 得 Q_ind (单位 1/4πε0=1 -> ε0=1/4π)"""
    q_img, b = image_charge(q_real, d, R)
    dtheta = math.pi / n_theta
    total = 0.0
    for i in range(n_theta):
        theta = (i + 0.5) * dtheta                # 中点法
        st, ct = math.sin(theta), math.cos(theta)
        x, z = R*st, R*ct                         # 球面点 (phi=0 代表)
        Ex_r, Ez_r = field_of(q_real, d, x, z)
        Ex_i, Ez_i = field_of(q_img, b, x, z)
        En = (Ex_r + Ex_i)*st + (Ez_r + Ez_i)*ct  # E·n, n=(sinθ,0,cosθ)
        total += En * st * dtheta * 2*math.pi*R*R # dA = R²sinθ dθ × 2π
    return total / (4*math.pi)                     # Q_ind = ε₀ ∮E·n dA

print("="*60)
print("接地导体球感应电荷: 镜像法 vs 数值积分")
print("解析公式: Q_ind / q = -R/d  (Griffiths 3.16)")
print("="*60)
print(f"{'d/R':>8} {'解析 Q_ind/q':>16} {'数值 Q_ind/q':>16} {'相对误差':>12}")

R = 1.0
q = 1.0
for d in [1.5, 2.0, 3.0, 5.0, 10.0]:
    exact = -R/d
    numer = induced_charge_numerical(q, d, R)
    err = abs(numer - exact)/abs(exact)
    print(f"{d:>8.2f} {exact:>16.4f} {numer:>16.4f} {err*100:>11.2f}%")

print()
# Gauss 定律自洽检验: 单电荷 球内 -> 4πq, 球外 -> 0
def gauss_check(qc, zc, R, n_theta=2000):
    dtheta = math.pi/n_theta; total = 0.0
    for i in range(n_theta):
        theta=(i+0.5)*dtheta; st,ct=math.sin(theta),math.cos(theta)
        x,z=R*st,R*ct
        Ex,Ez=field_of(qc,zc,x,z)
        total+=(Ex*st+Ez*ct)*st*dtheta*2*math.pi*R*R
    return total
print(f"  球外单电荷 zc=2 (期望 0):       ∮ = {gauss_check(1.0,2.0,R):.6f}")
print(f"  球内单电荷 zc=0.5 (期望 4π={4*math.pi:.4f}): ∮ = {gauss_check(1.0,0.5,R):.4f}")

print()
print("反直觉发现:")
print("  1. 感应电荷总量 |Q_ind| = qR/d < q, 不是 -q (远端球面有反向感应电荷)")
print("  2. 当 d -> R (电荷逼近球面), Q_ind -> -q, 球完全屏蔽")
print("  3. 当 d -> inf, Q_ind -> 0, 但镜像电荷位置 b=R^2/d -> 0")
print("     镜像法把无穷多个边界条件浓缩成一个虚构电荷, 体现唯一性定理的威力")
print("  4. 电荷必须在极轴(z轴)上才满足 phi 对称——若放 x 轴却用 z 极参数化,")
print("     会破坏 Gauss 定律自洽性 (常见 tutorial 陷阱)")
```

**预期输出**：数值与解析 $-R/d$ 误差 < 1%（粗网格），随 $n_\theta,n_\phi$ 增加收敛。

---

## 8. Tutorial 习题

### T1. 同轴电缆的电容与电感 (Griffiths Prob.7.58 经典)

同轴电缆内半径 $a$ 外半径 $b$，长 $L$，介质 $\epsilon,\mu$。

(a) 证明单位长度电容 $C/L=2\pi\epsilon/\ln(b/a)$，单位长度电感 $L'/L=\mu\ln(b/a)/(2\pi)$。

(b) 证明乘积 $L'C'=\mu\epsilon$，且电缆中的波速 $v=1/\sqrt{\mu\epsilon}=1/\sqrt{L'C'}$。

> **导师追问**：为何 $L'C'$ 与几何无关？这与传输线「特征阻抗」$Z_0=\sqrt{L'/C'}$ 的几何依赖性形成什么对比？

### T2. 偶极辐射角分布 (Griffiths §11.1.2)

振荡电偶极 $\mathbf{p}(t)=p_0\cos(\omega t)\hat{\mathbf{z}}$。

(a) 推出远场辐射功率角分布：
$$
\frac{dP}{d\Omega}=\frac{\mu_0 p_0^2\omega^4}{32\pi^2 c}\sin^2\theta
$$

(b) 求总辐射功率 $P=\mu_0 p_0^2\omega^4/(12\pi c)$。

> **导师追问**：为何 $P\propto\omega^4$？这如何解释瑞利散射（天空蓝）的频率依赖？

### T3. 法拉第圆盘 (Griffiths Prob.7.15)

半径 $R$ 的导体圆盘在均匀磁场 $B$ 中以角速度 $\omega$ 绕轴旋转。

(a) 求中心与边缘的电动势 $\mathcal{E}=\tfrac12 B\omega R^2$。

(b) 解释非相对论极限下此电动势的微观起源（磁力 vs 电力）。

> **导师追问**：把盘和磁铁一起转 vs 只转盘，电动势相同吗？这是「单极感应」争议的核心——爱因斯坦 1905 论文的动机之一。

### T4. Maxwell 位移电流的测量

平行板电容器半径 $R$ 充电电流 $I(t)$。

(a) 求极板间磁场（轴对称）：$B(r,t)=\mu_0 I r/(2\pi R^2)$。

(b) 这个 $B$ 由位移电流 $\epsilon_0\partial E/\partial t$ 而非传导电流产生。讨论能否用霍姆赫兹线圈实验分离两者。

> **导师追问**：位移电流在真空中存在吗？它与传导电流在哪些方面等价、哪些方面不等价？

---

## 9. 局限与延伸阅读

### 局限

1. **Griffiths 全用「即时作用」图像**——推迟势到 §10 才引入，但严格说静电学根本不存在（电荷一旦运动就有推迟效应）。
2. **介质用宏观 $\epsilon,\mu$**：隐藏了极化/磁化的微观机制，更严谨处理需 Jackson §4-6。
3. **不涉及规范场论的几何图像**：$A_\mu$ 作为联络要到 Y4 规范理论才讲清。
4. **辐射章节（Ch.11） Oxford Y2 不一定讲完**——留到 Y3 Atomic/Quantum Optics。

### 延伸阅读

- **J. D. Jackson** *Classical Electrodynamics* 3ed — Oxford Y3/研究生用，多极展开、辐射、相对论表述更严谨。
- **Purcell & Morin** *Electricity and Magnetism* 3ed — Berkeley 物理教程卷二，**用相对论推出磁场**，观点独特。
- **L. D. Landau & E. M. Lifshitz Vol.2** *The Classical Theory of Fields* — 从作用量和洛伦兹不变性出发，最优雅。

---

**版本**：v1.0 (2026-08-12) · Oxford MPhys Phase 1 Topic 02
**依据**：SURVEY.md Oxford Y2 课程表 + Griffiths (2013) 4ed
