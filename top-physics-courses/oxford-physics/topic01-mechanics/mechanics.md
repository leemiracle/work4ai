# Topic 01 — 牛顿力学、分析力学与狭义相对论

> **Oxford MPhys · Year 1 Mechanics + Year 2 Classical Mechanics**
> 教材：John R. Taylor *Classical Mechanics* (2005) + Kibble & Berkshire *Classical Mechanics* (5ed, 2004)
> 特色：导师制 (tutorial) 深度习题 + 从牛顿到哈密顿的完整分析力学链条

---

## 目录

1. [课程定位与 Oxford 特色](#1-课程定位与-oxford-特色)
2. [牛顿力学复习](#2-牛顿力学复习)
3. [拉格朗日力学](#3-拉格朗日力学)
4. [哈密顿力学](#4-哈密顿力学)
5. [刚体动力学](#5-刚体动力学)
6. [狭义相对论](#6-狭义相对论)
7. [反直觉实验 (Python)](#7-反直觉实验-python)
8. [Tutorial 习题 (导师制精选)](#8-tutorial-习题-导师制精选)
9. [局限与延伸阅读](#9-局限与延伸阅读)

---

## 1. 课程定位与 Oxford 特色

Oxford 物理系 MPhys 四年制中，力学跨两年：

| 年级 | 课程 | 核心教材 | 重点 |
|------|------|---------|------|
| Y1 | Mechanics | Taylor Ch.1-7 + K&B Ch.1-7 | 牛顿力学、振荡、有心力、狭义相对论入门 |
| Y2 | Classical Mechanics | Taylor Ch.6-13 + K&B Ch.7-12 | 拉格朗日、刚体、哈密顿、非线性 |

**Oxford 导师制 (tutorial) 特色**：每周 1 对 1（或 1 对 2-3）与导师讨论，每堂课前须提交 2-4 道书面解答。本文件的 §8 精选 Taylor/K&B 的标志性 tutorial 题，每题附「导师追问」(tutor's follow-up)——这正是 Oxford 区别于美式大课的灵魂。

---

## 2. 牛顿力学复习

### 2.1 三定律 (Taylor §1.2)

$$
\boxed{\;\text{第一律（惯性律）}\;:\quad \mathbf{F}=\mathbf{0}\ \Rightarrow\ \frac{d\mathbf{p}}{dt}=\mathbf{0}\;}
$$

$$
\boxed{\;\text{第二律}\;:\quad \mathbf{F}=\frac{d\mathbf{p}}{dt}=\dot m\,\mathbf{v}+m\,\mathbf{a}\ \xrightarrow{\,m=\text{const}\,}\ m\mathbf{a}\;}
$$

$$
\boxed{\;\text{第三律（弱形式）}\;:\quad \mathbf{F}_{12}=-\mathbf{F}_{21}\;}
$$

> **直觉**：第二律不是定义而是**经验定律**——它断言「力」这个概念可以被定义为动量的时间导数，且这个量满足线性叠加。Taylor (§1.3) 特意强调：把 $F=ma$ 当定义会陷入同义反复，关键在于力是**可独立测量**的外部作用。

### 2.2 有心力与开普勒问题 (Taylor §8, K&B §4.7)

二体问题约化为等效单体：
$$
\mu\ddot{\mathbf{r}}=-\nabla V(r),\qquad \mu=\frac{m_1 m_2}{m_1+m_2}
$$

角动量守恒 $\mathbf{L}=\mu\mathbf{r}\times\dot{\mathbf{r}}$ 给出运动在平面内。Binet 方程把轨道形状直接联系到力律：

$$
\boxed{\;F\!\left(\frac{1}{u}\right)=-\mu h^2 u^2\left(\frac{d^2u}{d\theta^2}+u\right),\quad u=\frac{1}{r},\ h=r^2\dot\theta\;}
$$

对平方反比引力 $F=-k/r^2$ 解出圆锥曲线：
$$
r(\theta)=\frac{\ell}{1+e\cos\theta},\quad \ell=\frac{L^2}{\mu k}\ \text{(半通径)},\ e=\sqrt{1+\frac{2EL^2}{\mu k^2}}\ \text{(偏心率)}
$$

开普勒三定律的**推导**（而非经验归纳）由此完成。

---

## 3. 拉格朗日力学

### 3.1 最小作用量原理 (Taylor §6.1-6.2)

定义**作用量**：
$$
S[\mathbf{q}(t)]=\int_{t_1}^{t_2} L(\mathbf{q},\dot{\mathbf{q}},t)\,dt,\qquad L=T-V
$$

**哈密顿原理**：物理轨道使 $S$ 取驻值（变分为零）。

### 3.2 欧拉-拉格朗日方程推导

固定端点 $\delta q(t_1)=\delta q(t_2)=0$，对任意变分 $\delta q$：

$$
\delta S=\int_{t_1}^{t_2}\!\left(\frac{\partial L}{\partial q}\delta q+\frac{\partial L}{\partial\dot q}\delta\dot q\right)dt
$$

第二项分部积分，边界项消失，$\delta q$ 任意故被积函数须为零：

$$
\boxed{\;\frac{d}{dt}\!\left(\frac{\partial L}{\partial\dot q_i}\right)-\frac{\partial L}{\partial q_i}=0,\quad i=1,\dots,n\;}
$$

这是**坐标无关**的——广义坐标 $q_i$ 可以是角度、长度、甚至电磁势，方程形式不变。

### 3.3 约束与拉氏乘子 (Taylor §7.1)

完整约束 $f(\mathbf{q},t)=0$ 用乘子 $\lambda$ 处理：
$$
\frac{d}{dt}\frac{\partial L}{\partial\dot q_i}-\frac{\partial L}{\partial q_i}=\lambda\frac{\partial f}{\partial q_i}
$$

**例（Taylor §7.5 珠子在旋转圆环上）**：圆环以 $\omega$ 绕竖直直径转，珠子受重力。广义坐标 $\theta$（偏离最低点的角）：

$$
L=\tfrac12 mR^2\dot\theta^2+\tfrac12 mR^2\omega^2\sin^2\theta+mgR\cos\theta
$$

EL 方程给出：$\ddot\theta=(\omega^2\cos\theta-g/R)\sin\theta$。平衡位置 $\theta^*$ 满足 $\cos\theta^*=g/(R\omega^2)$——**当 $\omega>\sqrt{g/R}$ 出现新的稳定平衡点**，这是自发对称性破缺的力学原型（§7 实验验证）。

### 3.4 守恒律与 Noether 定理

连续对称性 ↔ 守恒量：

| 对称性 | 变换 | 守恒量 |
|--------|------|--------|
| 时间平移 | $t\to t+\epsilon$ | 能量 $H=\sum\dot q_i p_i-L$ |
| 空间平移 | $\mathbf{r}\to\mathbf{r}+\boldsymbol\epsilon$ | 动量 $\mathbf{p}$ |
| 空间旋转 | $\mathbf{r}\to\mathbf{r}+\boldsymbol\theta\times\mathbf{r}$ | 角动量 $\mathbf{L}$ |

---

## 4. 哈密顿力学

### 4.1 勒让德变换 (Taylor §13.1)

从 $(q,\dot q)$ 切换到 $(q,p)$，$p_i=\partial L/\partial\dot q_i$：

$$
\boxed{\;H(\mathbf{q},\mathbf{p},t)=\sum_i p_i\dot q_i-L(\mathbf{q},\dot{\mathbf{q}},t)\;}
$$

### 4.2 正则方程

$$
\dot q_i=\frac{\partial H}{\partial p_i},\qquad \dot p_i=-\frac{\partial H}{\partial q_i},\qquad \frac{\partial H}{\partial t}=-\frac{\partial L}{\partial t}
$$

**反直觉**：一阶方程组代替二阶，相空间 $(q,p)$ 是偶数维流形——这是通向统计力学（Liouville 定理）和量子力学（$\hat q,\hat p$ 不可对易）的桥梁。

### 4.3 谐振子的三套等价表述

| 形式 | 运动方程 | 守恒量 |
|------|---------|--------|
| 牛顿 | $m\ddot x=-kx$ | $E=\tfrac12 m\dot x^2+\tfrac12 kx^2$ |
| 拉格朗日 | $L=\tfrac12 m\dot x^2-\tfrac12 kx^2$ | $H=\tfrac{p^2}{2m}+\tfrac12 kx^2$ |
| 哈密顿 | $\dot x=p/m,\ \dot p=-kx$ | 同上，但相空间轨迹是椭圆 |

---

## 5. 刚体动力学

### 5.1 转动惯量张量 (Taylor §10.2, K&B §9.3)

$$
I_{ij}=\int \rho(\mathbf{r})\left(r^2\delta_{ij}-x_i x_j\right)d^3r
$$

对角化得**主转动惯量** $I_1,I_2,I_3$。主轴上的角动量 $\mathbf{L}=(I_1\omega_1,I_2\omega_2,I_3\omega_3)$。

### 5.2 欧拉方程 (Taylor §10.6)

在体坐标系（非惯性系）：
$$
\boxed{\;I_1\dot\omega_1-(I_2-I_3)\omega_2\omega_3=N_1\ \text{(及循环置换)}\;}
$$

**自由刚体 ($N=0$)** 的稳定性分类：
- 绕 $I_{\max}$ 或 $I_{\min}$ 主轴转：**稳定**
- 绕中间主轴转：**不稳定**（网球拍定理 / 借力翻滚）

### 5.3 陀螺进动 (Taylor §10.9, K&B §9.7)

对称陀螺 ($I_1=I_2\neq I_3$)，定点在尖端，重力矩 $\boldsymbol\tau=M g\ell\,\sin\theta\,\hat\phi$。快速自转近似下进动角速度：

$$
\Omega_p=\frac{M g\ell}{I_3\omega_3}
$$

---

## 6. 狭义相对论 (Taylor Ch.15, K&B Ch.7)

### 6.1 洛伦兹变换

两惯性系沿 $x$ 相对速度 $v$：
$$
\boxed{\;\begin{pmatrix}ct'\\x'\end{pmatrix}=\begin{pmatrix}\gamma&-\gamma\beta\\-\gamma\beta&\gamma\end{pmatrix}\begin{pmatrix}ct\\x\end{pmatrix},\quad \beta=\frac vc,\ \gamma=\frac{1}{\sqrt{1-\beta^2}}\;}
$$

### 6.2 四维矢量

$$
x^\mu=(ct,\mathbf{x}),\qquad p^\mu=(E/c,\mathbf{p}),\qquad u^\mu=\gamma(c,\mathbf{v})
$$

不变量：$p_\mu p^\mu=(E/c)^2-\mathbf{p}^2=(mc)^2$，即
$$
\boxed{\;E^2=p^2c^2+m^2c^4\ \Longrightarrow\ E_{\text{静}}=mc^2\;}
$$

### 6.3 相对论动量-能量守恒

碰撞问题用四动量守恒 $p_1^\mu+p_2^\mu=p_3^\mu+p_4^\mu$，自动兼容能量守恒。**K&B §7.7** 的标准 tutorial：证明 $v_{\text{rel}}$ 不会超过 $c$，即便两物体相向 $0.9c$。

---

## 7. 反直觉实验 (Python)

> **铁律**：纯标准库零依赖，几秒跑完。本实验复现 §3.3 的「旋转圆环上珠子」对称性破缺——Oxford 经典 demo。

```python
#!/usr/bin/env python3
"""
旋转圆环上珠子：自发对称性破缺的力学原型
Taylor Classical Mechanics §7.5 / Kibble & Berkshire §10.4
纯标准库，零依赖。运行: python3 symmetry_breaking.py
"""
import math

def accel(theta, omega):
    """角加速度: ddot_theta = (omega^2 cos theta - g/R) sin theta"""
    g_over_R = 1.0          # 自然单位 g = R = 1
    return (omega*omega*math.cos(theta) - g_over_R) * math.sin(theta)

def integrate(theta0, omega, dt=0.001, T=40.0):
    """Velocity-Verlet 积分，返回 (时间列表, theta列表)"""
    th, ts = theta0, 0.0
    out_t, out_th = [], []
    n = int(T/dt)
    a = accel(th, omega)
    for i in range(n):
        th += ts*dt + 0.5*a*dt*dt
        a_new = accel(th, omega)
        ts += 0.5*(a + a_new)*dt
        a = a_new
        if i % 50 == 0:                     # 降采样
            out_t.append(i*dt)
            out_th.append(th)
    return out_t, out_th

def mean_theta(theta0, omega, settle=20.0):
    """丢弃前 settle 秒瞬态，取后半段均值判断终态位置"""
    ts, ths = integrate(theta0, omega, T=60.0)
    steady = [t for t, _ in zip(ts, ths) if t > settle]
    steady_th = [th for t, th in zip(ts, ths) if t > settle]
    # 折叠到 [0, pi] 判断落在上还是下半环
    folded = [abs(math.cos(th)) for th in steady_th]
    return sum(folded)/len(folded), max(ths), min(ths)

print("="*64)
print("旋转圆环上珠子：自发对称性破缺")
print("平衡解 cos(theta*) = g/(R*omega^2) = 1/omega^2 (自然单位)")
print("="*64)
print(f"{'omega':>8} {'理论 cos(theta*)':>18} {'稳态|cos(theta)|':>20} {'theta 振幅':>14}")

for omega in [0.5, 0.8, 1.0, 1.2, 1.5, 2.0, 3.0]:
    theory = 1.0/(omega*omega) if omega > 1.0 else float('nan')
    if omega > 1.0:
        th0 = math.acos(theory) + 0.01     # 从理论平衡点附近扰动
    else:
        th0 = 0.01                           # 从底部扰动
    steady_cos, hi, lo = mean_theta(th0, omega)
    swing = hi - lo
    if omega > 1.0:
        print(f"{omega:>8.2f} {theory:>18.4f} {steady_cos:>20.4f} {swing:>14.4f}")
    else:
        print(f"{omega:>8.2f} {'(无解, theta*=0)':>18} {steady_cos:>20.4f} {swing:>14.4f}")

print()
print("反直觉发现:")
print("  1. omega < sqrt(g/R)=1 时，珠子稳态停在底部 (theta=0)，对称未破缺")
print("  2. omega > sqrt(g/R) 后，珠子被甩到 theta*=arccos(1/omega^2)")
print("     ——底部变不稳定平衡！这是自发对称性破缺的最简力学实例")
print("  3. theta* 的两个解 (+/-) 对应圆环两侧，破缺方向取决于初始扰动")
print()
print("物理意义: 此模型与 Higgs 机制的真空对称性破缺同构。")
print("          '慢'相=底部稳定; '快'相=底部失稳,新平衡涌现。")
```

**预期输出**（核心数字）：
- $\omega=0.5$：稳态 $|\cos\theta|\approx 1.0$（停在底部 $\theta\approx0$）
- $\omega=2.0$：稳态 $|\cos\theta|\approx 0.25$（被甩到 $\theta^*=\arccos(0.25)\approx75.5°$）

---

## 8. Tutorial 习题 (导师制精选)

> Oxford 每周 tutorial 通常 4 题，下方选自 Taylor / K&B 标志性题目，每题附「导师追问」。

### T1. 双摆的小振动 (Taylor §11.5, 经典 Oxford 题)

双摆：第一摆质量 $m_1$ 长 $\ell_1$，第二摆 $m_2$ 长 $\ell_2$ 挂在 $m_1$ 下。小角近似下：

(a) 写出拉格朗日量并线性化。

(b) 证明简正模式频率满足：
$$
\omega^4-\left(1+\frac{m_2}{m_1}\right)\!\left(\frac{g}{\ell_1}+\frac{g}{\ell_2}\right)\omega^2+\frac{m_1+m_2}{m_1}\frac{g^2}{\ell_1\ell_2}=0
$$

(c) 取 $m_1=m_2=m,\ \ell_1=\ell_2=\ell$，求两简正频率并画出模式形状。

> **导师追问**：若把上摆固定点做水平振动 $A\cos\omega t$，共振时能量如何注入？这如何联系到秋千「打荡」？

### T2. 开普勒椭圆的 Runge-Lenz 矢量 (Taylor §8.9 补充)

平方反比引力额外有一个守恒矢量：
$$
\mathbf{A}=\mathbf{p}\times\mathbf{L}-\mu k\hat{\mathbf{r}}
$$

(a) 验证 $d\mathbf{A}/dt=0$。

(b) 证明 $\mathbf{A}\cdot\mathbf{r}=\mu k r - L^2$，从而推出 $r(\theta)=\ell/(1+e\cos\theta)$，其中 $e=A/(\mu k)$。

> **导师追问**：为何谐振子势 $V\propto r^2$ 也有额外守恒量（Fradkin 张量）？Bertrand 定理说只有这两种势封闭轨道——你能从对称性论证理解吗？

### T3. 网球拍定理的线性稳定性 (Taylor §10.10)

自由刚体绕主轴 $I_3$（中间惯量）自转。设扰动 $\omega_1,\omega_2\ll\omega_3$。

(a) 由欧拉方程推出 $\ddot\omega_1=\alpha\omega_1$，其中
$$
\alpha=\frac{(I_1-I_3)(I_3-I_2)}{I_1 I_2}\omega_3^2
$$

(b) 解释符号：为何 $I_1<I_3<I_2$ 时 $\alpha>0$ 意味着指数增长（不稳定）？

> **导师追问**：在太空站抛一个旋紧的扳手，为何会周期性「翻转」？给出翻转周期与三主惯量的关系。

### T4. 相对论多普勒与横向多普勒 (K&B §7.5)

光源以速度 $v$ 运动，观察者静止。

(a) 纵向多普勒：$\nu_{\text{obs}}=\nu_0\sqrt{(1-\beta)/(1+\beta)}$（退行）。

(b) **横向多普勒**（光源垂直于视线运动）：证明 $\nu_{\text{obs}}=\nu_0/\gamma<\nu_0$——纯时间膨胀效应，经典理论预测为零频移。

> **导师追问**：Ives-Stilwell (1938) 实验如何验证横向多普勒？为何这是相对论最早的确证之一？

---

## 9. 局限与延伸阅读

### 局限

1. **牛顿框架的隐含假设**：绝对时间、伽利略不变性——只在 $v\ll c$ 成立。
2. **拉格朗日的「最小作用量」措辞误导**：实际是**驻值**（stationary），不一定是极小；经典轨道可对应 $S$ 的鞍点。
3. **欧拉方程在体坐标系**：体坐标系是非惯性的，$\mathbf{N}$ 是**外力矩**，别误加惯性力矩。
4. **狭义相对论不处理引力**：等效原理需广义相对论（Y3 Schutz/Hobson 课）。

### 延伸阅读

- **Goldstein, Poole & Safko** *Classical Mechanics* 3ed — Oxford Y3/Theoretical Physics 的进阶，Noether 定理与正则变换更严谨。
- **Landau & Lifshitz Vol.1** *Mechanics* — 从最小作用量**公理出发**推导全部力学，极简极美，Oxford 理论生必读。
- **Morin** *Introduction to Classical Mechanics* (Harvard) — 习题极多，与 Oxford tutorial 风格互补。

---

**版本**：v1.1 (2026-08-12) · Oxford MPhys Phase 1 Topic 01
**依据**：SURVEY.md Oxford Y1/Y2 课程表 + Taylor (2005) + Kibble & Berkshire (2004)

---

## 🎯 费曼式入口（白话版）

> **一句话解释**：力学是研究「东西怎么动、为什么这么动」的学问——从苹果落地到行星绕日，都服从同一套极少数原理。
>
> **生活类比**：把牛顿三定律想象成一场台球游戏。第一律说球不碰就直走（惯性）；第二律说「你推多用力 × 推多久 = 球变快多少」（$F=ma$）；第三律说「你打球，球也打你」（反作用力）。拉格朗日和哈密顿则是把这套规则换成「自然走最省事的路」——像水总是找最低点流。
>
> **反直觉发现**：
> - **卫星一直在「掉」**：国际空间站的宇航员飘着不是没引力（引力还有 89%），而是他们在自由落体——掉得快，但地球弧度让他们永远掉不到地面。
> - **对称性会「破」**：旋转圆环上的珠子，转速一过临界值，底部就突然变成不稳定平衡——这是 Higgs 机制（赋予粒子质量）的力学原型。
> - **中间主轴最不稳**：抛一个绕中间惯量主轴自转的物体，它会周期性「翻跟头」（网球拍定理）——太空站里扳手真的会这样翻。

---

## 🔗 衔接：从哪来，到哪去

### 前置（入学前应掌握）
- **A-level / IB HL 物理**：牛顿三定律、能量守恒、动量、简谐运动
- **A-level 数学**：微积分（链式法则、分部积分）、向量叉乘、复数
- **Y1 数学方法 I**（RHB Ch.1-8）：线性代数、ODE 基础——拉格朗日要算偏导，哈密顿要算矩阵

### 本课的危机（学生最容易栽跟头的地方）
- **「最小作用量」措辞误导**：物理轨道取的是**驻值**（stationary），不一定是极小——经典轨道可对应作用量 $S$ 的鞍点。
- **欧拉方程在体坐标系**：体坐标系是非惯性的，$\mathbf{N}$ 是**外力矩**，别误加惯性力矩。
- **狭义相对论不处理引力**：等效原理需广义相对论（Y3 Schutz/Hobson 课，见 Topic 08）。

### 新危机（学完本课后会冒出来的新问题）
- 牛顿框架假设绝对时间——$v\to c$ 时崩塌，需要狭义相对论修补。
- 拉格朗日的「广义坐标」一旦推广到场（连续自由度），就跨入经典场论与 QFT。
- 哈密顿力学的相空间是偶数维流形——这是通向统计力学（Liouville 定理，Topic 04）和量子力学（$\hat q,\hat p$ 不可对易，Topic 03）的桥梁。

### 后续（Oxford 路径）
- **Y2 Classical Mechanics**：Goldstein 级深度，正则变换、Hamilton-Jacobi、非线性振动
- **Y3 General Relativity**（Topic 08）：等效原理把引力几何化
- **Y3 Theoretical Physics**：经典场论、Noether 定理严格化
- **Y4**：规范场论、弦论入门（哈密顿约束系统的量子化）

---

## 🏭 理论联系实际：5 个应用

1. **GPS 卫星轨道设计**：开普勒问题 + 摄动论。每颗 GPS 卫星的椭圆轨道参数（$a,e,i$）都用经典力学算出，地球扁率 $J_2$ 项引起进动需修正。
2. **陀螺仪与惯性导航**：飞机/导弹/手机的 IMU（惯性测量单元）核心是 MEMS 陀螺——基于欧拉方程与科里奥利效应。无人机姿态控制就是实时解刚体动力学。
3. **拉格朗日点 L1/L2 任务**：JWST 望远镜在日地 L2 点（2021 发射），Gaia 在 L2。「三体问题共线解」是限制性三体的经典结论。
4. **羽毛球/网球拍翻滚（Dzhanibekov 效应）**：网球拍定理在太空站实拍视频广为流传——T 形翼在轨翻转曾让工程师困惑，纯经典力学可解释。
5. **机器人腿式运动（Boston Dynamics）**：双足机器人的「动力学」就是拉格朗日方程 + 数值积分——广义坐标选关节角，惯量张量算步态。

---

## 🔬 最新研究前沿（2024-2026）

> 注：以下为基于公开研究项目与会议报道的方向性梳理（firecrawl 搜索返回空数据，依据领域常识与 Oxford Physics 公开项目页整理）。

1. **非厄米拓扑力学（2024-2025）**：把「非厄米物理」（含损耗/增益）与拓扑力学结合，设计「单向传力」的超材料——破缺时间反演对称性的力学系统可实现单向声波/振动隔离。Oxford 与 Imperial 共同推进的 metamaterials 项目活跃。
2. **Origami/Kirigami 力学超材料（2024）**：折纸结构作为「可编程刚度」材料——通过折痕几何（拉格朗日约束）控制大变形模式。应用于可展开太空天线（JWST 的遮阳屏就是折纸工程）。
3. **Active Matter 与 flocking 理论（2024-2025）**：鸟群/细胞群/机器人集群的「非平衡统计力学」——Toner-Tu 方程（连续化 Vicsek 模型）描述自推进粒子的集体运动，与经典流体力学（Navier-Stokes）形成对照。Oxford Rudnick 组、Pringle 组在研。
4. **三体问题的数值新时代（2024）**：随着高精度数值积分（IAS15、WHFast）与机器学习势能拟合（「Hamiltonian Neural Networks」），混沌三体轨道的长期统计性质被重新审视——「三体问题的混沌不是噪声，是结构」。
5. **引力波多信使时代（2023-2024 LIGO O4 运行）**：双中子星并合的动力学（潮汐形变、并合前的刚体自转）需精确的相对论刚体力学——牛顿框架是零阶近似，Kerr 度规下的相对论陀螺进动是高阶修正。

---

## 🗺️ 学习 Roadmap（Oxford MPhys 路径）

```
Year 1 (MT/HT)                Year 2 (HT/TT)                Year 3-4
─────────────                ─────────────                ─────────
Mechanics                    Classical Mechanics          General Relativity (Y3)
· 牛顿三定律                  · 拉格朗日（最小作用量）       · 等效原理、张量
· 有心力/开普勒               · 哈密顿、正则方程            · Schwarzschild 解
· 狭义相对论入门              · 刚体（欧拉方程）            · 黑洞、宇宙学 (Y4)
· 振荡/波                    · 非线性振动/混沌             · Theoretical Physics
                                                          · 经典场论、Noether
教材: Taylor + K&B           教材: Taylor + Goldstein     教材: Schutz/Hobson/Carroll
```

**知识检查清单**：
- [ ] 能从 $F=ma$ 推出开普勒三定律（不查书）
- [ ] 能用最小作用量推出欧拉-拉格朗日方程
- [ ] 能解释为何绕中间主轴自转不稳定（网球拍定理）
- [ ] 能算双摆的小振动简正模式
- [ ] 能用四动量守恒解相对论碰撞
- [ ] 能说出 Noether 定理：时间平移↔能量、空间平移↔动量、旋转↔角动量

**Oxford 特色资源**：
- Clarendon Laboratory 的非线性动力学实验组（dynamical systems）
- Oxford 的 Balliol/Merton 等学院 tutorial 题库传承百年
- Y4 选修 *Advanced Theoretical Physics* 直通场论与弦论
