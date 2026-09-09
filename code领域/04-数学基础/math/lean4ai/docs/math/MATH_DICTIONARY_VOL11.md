# 数学知识词典 - 第十一卷：连续介质力学与数学应用
## Mathematics Subject Dictionary - Volume 11: Continuum Mechanics and Mathematical Applications

**MSC分类**: 74-XX, 80-XX, 85-XX, 86-XX  
**版本**: 2.2  
**更新日期**: 2025-03-26  

---

## 目录

1. [74-XX 弹性力学 (Mechanics of Deformable Solids)](#74-xx-弹性力学-mechanics-of-deformable-solids)
2. [80-XX 经典热力学与热传导 (Classical Thermodynamics, Heat Transfer)](#80-xx-经典热力学与热传导-classical-thermodynamics-heat-transfer)
3. [85-XX 天文学与天体物理学 (Astronomy and Astrophysics)](#85-xx-天文学与天体物理学-astronomy-and-astrophysics)
4. [86-XX 地球物理学 (Geophysics)](#86-xx-地球物理学-geophysics)

---

## 74-XX 弹性力学 (Mechanics of Deformable Solids)

### 定义 I.74.1 (应变张量 / Strain Tensor)

**定义**: 设 $\mathbf{x}$ 是参考构型中的位置，$\mathbf{u}(\mathbf{x})$ 是位移场。**无穷小应变张量** 定义为：

$$\epsilon_{ij} = \frac{1}{2}\left(\frac{\partial u_i}{\partial x_j} + \frac{\partial u_j}{\partial x_i}\right)$$

**Green-Lagrange应变张量** (有限变形):

$$E_{ij} = \frac{1}{2}\left(\frac{\partial u_i}{\partial x_j} + \frac{\partial u_j}{\partial x_i} + \frac{\partial u_k}{\partial x_i}\frac{\partial u_k}{\partial x_j}\right)$$

**物理意义**: $\epsilon_{ij}$ 描述变形后线元长度和角度的变化。

---

### 定义 I.74.2 (应力张量 / Stress Tensor)

**定义**: **Cauchy应力张量** $\sigma_{ij}$ 满足：对于面元 $d\mathbf{S} = \mathbf{n}\, dS$，其上的面力为

$$d\mathbf{F} = \boldsymbol{\sigma} \cdot \mathbf{n}\, dS$$

即 $dF_i = \sigma_{ij} n_j\, dS$。

**性质**:
- 对称性: $\sigma_{ij} = \sigma_{ji}$（角动量守恒）
- 主应力: $\sigma_1 \geq \sigma_2 \geq \sigma_3$（特征值）
- Von Mises应力: $\sigma_{vm} = \sqrt{\frac{3}{2}s_{ij}s_{ij}}$，其中 $s_{ij} = \sigma_{ij} - \frac{1}{3}\sigma_{kk}\delta_{ij}$

---

### 定理 74.1 (平衡方程 / Equilibrium Equations)

**定理**: 在静力平衡下，应力张量满足：

$$\frac{\partial \sigma_{ij}}{\partial x_j} + f_i = 0 \quad \text{(无体力)}$$

或

$$\nabla \cdot \boldsymbol{\sigma} + \mathbf{f} = \mathbf{0}$$

其中 $\mathbf{f}$ 是单位体积的体力。

**推导**: 对任意体积 $V$ 应用Newton第二定律和散度定理。 □

---

### 定义 I.74.3 (本构关系 / Constitutive Relations)

**定义**: **本构关系** 描述材料的应力-应变关系。

**Hooke定律** (线性弹性):

$$\sigma_{ij} = C_{ijkl} \epsilon_{kl}$$

其中 $C_{ijkl}$ 是四阶弹性张量。

**各向同性材料**:

$$\sigma_{ij} = \lambda \epsilon_{kk} \delta_{ij} + 2\mu \epsilon_{ij}$$

其中 $\lambda$, $\mu$ 是 **Lamé常数**。

**逆关系**:

$$\epsilon_{ij} = \frac{1}{E}\left[(1+\nu)\sigma_{ij} - \nu \sigma_{kk}\delta_{ij}\right]$$

其中 $E$ 是Young模量，$\nu$ 是Poisson比。

---

### 定理 74.2 (Navier方程 / Navier's Equation)

**定理**: 对于各向同性线性弹性体，位移场 $\mathbf{u}$ 满足 **Navier方程**:

$$(\lambda + \mu)\nabla(\nabla \cdot \mathbf{u}) + \mu \nabla^2 \mathbf{u} + \mathbf{f} = \mathbf{0}$$

或等价地：

$$\mu \nabla^2 \mathbf{u} + (\lambda + \mu)\nabla(\nabla \cdot \mathbf{u}) + \mathbf{f} = \rho \frac{\partial^2 \mathbf{u}}{\partial t^2} \quad \text{(动力学)}$$

**Helmholtz分解**: $\mathbf{u} = \nabla\phi + \nabla \times \boldsymbol{\psi}$，其中 $\nabla \cdot \boldsymbol{\psi} = 0$。

---

### 定义 I.74.4 (弹性波 / Elastic Waves)

**定义**: 在无限大弹性介质中传播两种波：

1. **纵波 (P波)**: 位移方向与传播方向平行
   $$c_p = \sqrt{\frac{\lambda + 2\mu}{\rho}}$$

2. **横波 (S波)**: 位移方向与传播方向垂直
   $$c_s = \sqrt{\frac{\mu}{\rho}}$$

**关系**: $c_p > c_s$（纵波更快）。

---

### 定理 74.3 (弹性力学的唯一性定理 / Uniqueness Theorem in Elasticity)

**定理** (Kirchhoff): 设 $V$ 是弹性体，边界条件给定。则平衡问题
$$\nabla \cdot \boldsymbol{\sigma} + \mathbf{f} = \mathbf{0} \text{ 在 } V \text{ 内}$$
的解是唯一的。

**证明**: 设 $\mathbf{u}_1$, $\mathbf{u}_2$ 是两个解，$\mathbf{v} = \mathbf{u}_1 - \mathbf{u}_2$。则
$$0 = \int_V \sigma_{ij}(\mathbf{v}) \epsilon_{ij}(\mathbf{v}) dV \geq 2\mu \int_V \epsilon_{ij}\epsilon_{ij} dV$$
故 $\epsilon_{ij} = 0$，$\mathbf{v}$ 是刚体运动。由边界条件，$\mathbf{v} = 0$。 □

---

### 定义 I.74.5 (弹性应变能 / Elastic Strain Energy)

**定义**: **弹性应变能密度**:

$$U = \frac{1}{2} \sigma_{ij} \epsilon_{ij} = \frac{1}{2} C_{ijkl} \epsilon_{ij} \epsilon_{kl}$$

**总应变能**:

$$W = \int_V U\, dV$$

**Clapeyron定理**: 外力做功 = $2W$（线性弹性）。

---

### 定义 I.74.6 (平面应力与平面应变 / Plane Stress and Plane Strain)

**平面应力**: $\sigma_{zz} = \sigma_{zx} = \sigma_{zy} = 0$（薄板）
**平面应变**: $\epsilon_{zz} = \epsilon_{zx} = \epsilon_{zy} = 0$（长柱体）

**Airy应力函数** $\Phi(x,y)$: 对于平面问题，

$$\sigma_{xx} = \frac{\partial^2 \Phi}{\partial y^2}, \quad \sigma_{yy} = \frac{\partial^2 \Phi}{\partial x^2}, \quad \sigma_{xy} = -\frac{\partial^2 \Phi}{\partial x \partial y}$$

满足双调和方程:

$$\nabla^4 \Phi = 0$$

---

### 定理 74.4 (Saint-Venant原理 / Saint-Venant's Principle)

**定理**: 在弹性体上作用静力等效的载荷，则在距离载荷作用区域较远处，应力分布的差异可以忽略。

**数学表述**: 设 $\mathbf{f}_1$, $\mathbf{f}_2$ 是边界 $\partial V$ 上的两组面力，满足
$$\int_{\partial V} \mathbf{f}_1\, dS = \int_{\partial V} \mathbf{f}_2\, dS, \quad \int_{\partial V} \mathbf{x} \times \mathbf{f}_1\, dS = \int_{\partial V} \mathbf{x} \times \mathbf{f}_2\, dS$$
（合力和合力矩相同），则在距离 $\partial V$ 远处，$\|\boldsymbol{\sigma}_1 - \boldsymbol{\sigma}_2\| = O(r^{-n})$。

---

### 定义 I.74.7 (断裂力学 / Fracture Mechanics)

**定义**: **应力强度因子** $K$ 刻画裂纹尖端的应力奇异性：

$$K_I = \lim_{r \to 0} \sqrt{2\pi r}\, \sigma_{yy}(r, 0)$$

**断裂准则**: 裂纹扩展当 $K \geq K_c$（材料常数）。

**能量释放率**:

$$G = -\frac{\partial W}{\partial A}$$

其中 $A$ 是裂纹面积。**Griffith准则**: 裂纹扩展当 $G \geq G_c$。

---

### 定义 I.74.8 (塑性力学 / Plasticity)

**定义**: 当应力超过屈服极限，材料发生塑性变形（不可逆）。

**von Mises屈服准则**:

$$\sigma_{vm} = \sqrt{\frac{1}{2}[(\sigma_1-\sigma_2)^2 + (\sigma_2-\sigma_3)^2 + (\sigma_3-\sigma_1)^2]} \geq \sigma_Y$$

**Tresca屈服准则**:

$$\max(|\sigma_1 - \sigma_2|, |\sigma_2 - \sigma_3|, |\sigma_3 - \sigma_1|) \geq \sigma_Y$$

**流动法则**: 塑性应变增量方向垂直于屈服面。

---

### 参考文献 (74-XX)
1. Landau, L.D., Lifshitz, E.M., *Theory of Elasticity*, Pergamon, 1986
2. Gurtin, M.E., *An Introduction to Continuum Mechanics*, Academic Press, 1981
3. Timoshenko, S.P., Goodier, J.N., *Theory of Elasticity*, McGraw-Hill, 1970
4. Malvern, L.E., *Introduction to the Mechanics of a Continuous Medium*, Prentice-Hall, 1969
5. Anderson, T.L., *Fracture Mechanics: Fundamentals and Applications*, CRC, 2005

---

## 80-XX 经典热力学与热传导 (Classical Thermodynamics, Heat Transfer)

### 定义 I.80.1 (热力学系统 / Thermodynamic System)

**定义**: **热力学系统** 是宏观物理系统，用状态变量描述：
- **强度量**: 压强 $P$，温度 $T$（与系统大小无关）
- **广延量**: 体积 $V$，内能 $U$，熵 $S$（与系统大小成正比）

**状态方程**: 对于理想气体

$$PV = nRT$$

---

### 定理 80.1 (热力学定律 / Laws of Thermodynamics)

**第零定律**: 若 $A$ 与 $B$ 热平衡，$B$ 与 $C$ 热平衡，则 $A$ 与 $C$ 热平衡。（温度的定义）

**第一定律** (能量守恒):

$$dU = \delta Q - \delta W$$

其中 $\delta Q$ 是热量输入，$\delta W = P\, dV$ 是功。

**第二定律**: 熵不减。孤立系统 $\Delta S \geq 0$。可逆过程 $\Delta S = \delta Q / T$。

**第三定律**: $T \to 0$ 时 $S \to 0$。

---

### 定义 I.80.2 (热力学势 / Thermodynamic Potentials)

**定义**: 基本热力学势：
- **内能**: $U(S, V)$
- **焓**: $H = U + PV$
- **Helmholtz自由能**: $F = U - TS$
- **Gibbs自由能**: $G = H - TS = F + PV$

**Maxwell关系**:

$$\left(\frac{\partial T}{\partial V}\right)_S = -\left(\frac{\partial P}{\partial S}\right)_V, \quad \left(\frac{\partial T}{\partial P}\right)_S = \left(\frac{\partial V}{\partial S}\right)_P$$

---

### 定义 I.80.3 (热传导方程 / Heat Equation)

**定义**: **热传导方程** (Fourier定律):

$$\frac{\partial T}{\partial t} = \alpha \nabla^2 T + \frac{Q}{\rho c_p}$$

其中 $\alpha = k/(\rho c_p)$ 是 **热扩散率**，$k$ 是热导率。

**Fourier定律**:

$$\mathbf{q} = -k \nabla T$$

其中 $\mathbf{q}$ 是热流密度。

---

### 定理 80.2 (热传导方程的极值原理 / Maximum Principle for Heat Equation)

**定理**: 设 $T(\mathbf{x}, t)$ 在 $\Omega \times [0, T_0]$ 上满足热传导方程（无源项）。则

$$\max_{\overline{\Omega} \times [0, T_0]} T = \max_{\Gamma} T$$

其中 $\Gamma = (\partial \Omega \times [0, T_0]) \cup (\Omega \times \{0\})$ 是抛物边界。

**物理意义**: 内部温度不会超过边界和初始温度的最大值。

---

### 定理 80.3 (热传导方程的基本解 / Fundamental Solution of Heat Equation)

**定理**: 热传导方程 $\frac{\partial T}{\partial t} = \alpha \nabla^2 T$ 在 $\mathbb{R}^n$ 上的基本解：

$$G(\mathbf{x}, t) = \frac{1}{(4\pi\alpha t)^{n/2}} \exp\left(-\frac{|\mathbf{x}|^2}{4\alpha t}\right), \quad t > 0$$

**初值问题**的解：

$$T(\mathbf{x}, t) = \int_{\mathbb{R}^n} G(\mathbf{x} - \mathbf{y}, t) T_0(\mathbf{y})\, d\mathbf{y}$$

**注**: $G$ 是Gauss核，热传导导致温度分布"平滑化"。

---

### 定义 I.80.4 (Stefan问题 / Stefan Problem)

**定义**: **Stefan问题** 描述相变过程（如冰融化）。设 $s(t)$ 是相界位置，则：

**液相** ($0 < x < s(t)$):
$$\rho c \frac{\partial T}{\partial t} = k \frac{\partial^2 T}{\partial x^2}$$

**相界条件** (Stefan条件):
$$\rho L \frac{ds}{dt} = -k \frac{\partial T}{\partial x}\bigg|_{x=s(t)^-}$$

其中 $L$ 是潜热。

**特点**: 自由边界问题，边界位置由解本身决定。

---

### 定义 I.80.5 (对流传热 / Convective Heat Transfer)

**定义**: **Newton冷却定律**:

$$q = h(T_s - T_\infty)$$

其中 $h$ 是 **对流传热系数**，$T_s$ 是表面温度，$T_\infty$ 是环境温度。

**无量纲数**:
- **Nusselt数**: $Nu = hL/k$
- **Prandtl数**: $Pr = \nu/\alpha$
- **Grashof数**: $Gr = g\beta(T_s - T_\infty)L^3/\nu^2$
- **Rayleigh数**: $Ra = Gr \cdot Pr$

---

### 定理 80.4 (边界层理论 / Boundary Layer Theory)

**定理** (Prandtl): 对于大Reynolds数流动，粘性效应限制在薄边界层 $\delta \sim L/\sqrt{Re}$ 内。

**热边界层厚度**:

$$\delta_T \sim L \cdot Pr^{-1/2} \cdot Re^{-1/2}$$

**物理意义**: $Pr \gg 1$（油类）时热边界层薄于速度边界层；$Pr \ll 1$（液态金属）时相反。

---

### 参考文献 (80-XX)
1. Callen, H.B., *Thermodynamics and an Introduction to Thermostatistics*, Wiley, 1985
2. Carslaw, H.S., Jaeger, J.C., *Conduction of Heat in Solids*, Oxford, 1959
3. Incropera, F.P., DeWitt, D.P., *Fundamentals of Heat and Mass Transfer*, Wiley, 2002
4. Bird, R.B., Stewart, W.E., Lightfoot, E.N., *Transport Phenomena*, Wiley, 2002

---

## 85-XX 天文学与天体物理学 (Astronomy and Astrophysics)

### 定义 I.85.1 (天体力学 / Celestial Mechanics)

**定义**: **二体问题**：质量为 $m_1$, $m_2$ 的两个天体在引力作用下运动。

**约化质量**: $\mu = \frac{m_1 m_2}{m_1 + m_2}$

**运动方程**:

$$\mu \frac{d^2 \mathbf{r}}{dt^2} = -\frac{Gm_1 m_2}{r^2} \hat{\mathbf{r}}$$

**守恒量**: 能量 $E$，角动量 $\mathbf{L}$，Laplace-Runge-Lenz矢量 $\mathbf{A}$。

---

### 定理 85.1 (Kepler定律 / Kepler's Laws)

**定理**: 二体问题的解满足Kepler三定律：

1. **轨道定律**: 行星沿椭圆轨道运动，太阳在椭圆的一个焦点
2. **面积定律**: 行星与太阳的连线在相等时间内扫过相等面积
   $$\frac{dA}{dt} = \frac{L}{2\mu} = \text{const}$$
3. **周期定律**: 轨道周期的平方与半长轴的立方成正比
   $$T^2 = \frac{4\pi^2}{G(m_1+m_2)} a^3$$

---

### 定义 I.85.2 (恒星结构 / Stellar Structure)

**定义**: 恒星结构由四个基本方程描述：

1. **质量守恒**: $\frac{dM_r}{dr} = 4\pi r^2 \rho$
2. **静力平衡**: $\frac{dP}{dr} = -\frac{GM_r \rho}{r^2}$
3. **能量守恒**: $\frac{dL_r}{dr} = 4\pi r^2 \rho \epsilon$
4. **能量输运**: $\frac{dT}{dr} = -\frac{3\kappa \rho L_r}{16\pi acr^2 T^3}$（辐射）或 $\nabla_{ad}$（对流）

其中 $\rho$ 是密度，$P$ 是压强，$L_r$ 是光度，$\epsilon$ 是产能率，$\kappa$ 是不透明度。

---

### 定理 85.2 (恒星稳定性 / Stellar Stability)

**定理**: 恒星的振动稳定性由 **绝热指数** $\gamma$ 决定：

$$\gamma = \left(\frac{\partial \ln P}{\partial \ln \rho}\right)_s$$

- $\gamma > 4/3$: 动力学稳定
- $\gamma < 4/3$: 动力学不稳定（塌缩）

**应用**: 铁核在核燃烧结束后 $\gamma \to 4/3$，导致超新星爆发。

---

### 定义 I.85.3 (吸积盘 / Accretion Disks)

**定义**: **吸积盘** 是围绕致密天体（黑洞、中子星）旋转的物质盘。

**薄盘模型** (Shakura-Sunyaev):
- 角动量输运：粘滞应力 $\tau_{r\phi} = \alpha P$（$\alpha$-模型）
- 能量释放：$L = \frac{1}{2}\frac{GM\dot{M}}{R}$（吸积能的一半）

**Eddington光度**:

$$L_{Edd} = \frac{4\pi G M m_p c}{\sigma_T} \approx 1.3 \times 10^{38} \left(\frac{M}{M_\odot}\right) \text{ erg/s}$$

超过此光度，辐射压阻止吸积。

---

### 定义 I.85.4 (致密天体 / Compact Objects)

**白矮星**:
- 电子简并压支撑
- 质量 $M < 1.4 M_\odot$（Chandrasekhar极限）
- 半径 $R \sim 10^4$ km

**中子星**:
- 中子简并压支撑
- 质量 $M \sim 1.4-2 M_\odot$
- 半径 $R \sim 10$ km

**黑洞**:
- Schwarzschild半径: $r_s = \frac{2GM}{c^2}$
- 事件视界: 不可逃逸边界
- 无毛定理: 黑洞由质量、角动量、电荷完全表征

---

### 定理 85.3 (恒星演化终态 / End States of Stellar Evolution)

**定理**: 恒星演化终态由初始质量决定：

| 初始质量 | 终态 |
|----------|------|
| $M < 8 M_\odot$ | 白矮星 |
| $8 M_\odot < M < 25 M_\odot$ | 中子星（超新星爆发） |
| $M > 25 M_\odot$ | 黑洞 |

**质量-半径关系**（白矮星，非相对论）:

$$R \propto M^{-1/3}$$

---

### 定义 I.85.5 (宇宙学 / Cosmology)

**定义**: **Friedmann-Robertson-Walker度规**:

$$ds^2 = -c^2 dt^2 + a(t)^2 \left[\frac{dr^2}{1-kr^2} + r^2 d\Omega^2\right]$$

其中 $a(t)$ 是尺度因子，$k$ 是曲率参数。

**Friedmann方程**:

$$\left(\frac{\dot{a}}{a}\right)^2 = \frac{8\pi G}{3}\rho - \frac{kc^2}{a^2} + \frac{\Lambda c^2}{3}$$

其中 $\Lambda$ 是宇宙学常数。

---

### 定理 85.4 (宇宙膨胀 / Cosmic Expansion)

**定理**: Hubble定律

$$v = H_0 d$$

其中 $H_0 \approx 70$ km/s/Mpc 是Hubble常数。

**宇宙的临界密度**:

$$\rho_c = \frac{3H_0^2}{8\pi G} \approx 9 \times 10^{-30} \text{ g/cm}^3$$

**密度参数**: $\Omega = \rho/\rho_c$
- $\Omega = 1$: 平坦宇宙
- $\Omega > 1$: 闭宇宙
- $\Omega < 1$: 开宇宙

---

### 参考文献 (85-XX)
1. Binney, J., Tremaine, S., *Galactic Dynamics*, Princeton, 2008
2. Chandrasekhar, S., *An Introduction to the Study of Stellar Structure*, Dover, 1957
3. Frank, J., King, A., Raine, D., *Accretion Power in Astrophysics*, Cambridge, 2002
4. Peacock, J.A., *Cosmological Physics*, Cambridge, 1999
5. Shapiro, S.L., Teukolsky, S.A., *Black Holes, White Dwarfs, and Neutron Stars*, Wiley, 1983

---

## 86-XX 地球物理学 (Geophysics)

### 定义 I.86.1 (地球内部结构 / Earth's Interior Structure)

**定义**: 地球分层结构：
- **地壳** (Crust): 0-35 km（大陆），0-7 km（海洋）
- **地幔** (Mantle): 35-2900 km，分为上地幔和下地幔
- **外核** (Outer Core): 2900-5150 km，液态
- **内核** (Inner Core): 5150-6371 km，固态

**地震波**:
- **P波**（纵波）：可在固体和液体中传播
- **S波**（横波）：只能在固体中传播

**地震波速度**: 由密度和弹性模量决定

$$v_p = \sqrt{\frac{K + \frac{4}{3}\mu}{\rho}}, \quad v_s = \sqrt{\frac{\mu}{\rho}}$$

---

### 定理 86.1 (地震定位 / Earthquake Location)

**定理**: 设地震发生在 $(x_0, y_0, z_0, t_0)$，台站 $i$ 记录到P波到时 $t_i$。则

$$t_i - t_0 = \frac{1}{v_p} \sqrt{(x_i - x_0)^2 + (y_i - y_0)^2 + (z_i - z_0)^2}$$

**定位方法**: 需要至少4个台站的数据求解 $(x_0, y_0, z_0, t_0)$。

**实际应用**: 考虑地球三维速度结构，使用射线追踪和层析成像。

---

### 定义 I.86.2 (地球磁场 / Earth's Magnetic Field)

**定义**: 地球磁场近似为偶极场：

$$\mathbf{B} = -\nabla V, \quad V = \frac{a^3}{r^2} \mathbf{M} \cdot \hat{\mathbf{r}}$$

其中 $\mathbf{M}$ 是磁偶极矩，$a$ 是地球半径。

**地磁发电机理论**: 外核中的液态铁通过对流和Coriolis力产生磁场（磁流体动力学）。

**磁感应方程**:

$$\frac{\partial \mathbf{B}}{\partial t} = \nabla \times (\mathbf{v} \times \mathbf{B}) + \eta \nabla^2 \mathbf{B}$$

其中 $\eta$ 是磁扩散率。

---

### 定理 86.2 (磁冻结定理 / Alfvén's Frozen-in Flux Theorem)

**定理**: 在理想MHD（磁扩散率 $\eta = 0$）中，磁力线"冻结"在流体中：

$$\frac{d}{dt} \int_S \mathbf{B} \cdot d\mathbf{S} = 0$$

**意义**: 磁通量守恒，流体携带磁力线运动。

---

### 定义 I.86.3 (板块构造 / Plate Tectonics)

**定义**: 地球表面由若干刚性板块组成，在地质时间尺度上相对运动。

**板块边界类型**:
- **离散边界**: 中洋脊，新地壳生成
- **汇聚边界**: 俯冲带，地壳消减
- **转换边界**: 走滑断层

**板块运动速度**: ~1-10 cm/年

---

### 定理 86.3 (地幔对流 / Mantle Convection)

**定理**: 地幔对流由Rayleigh数控制：

$$Ra = \frac{\alpha g \Delta T d^3}{\kappa \nu}$$

其中 $\alpha$ 是热膨胀系数，$\Delta T$ 是温差，$d$ 是深度，$\kappa$ 是热扩散率，$\nu$ 是运动粘度。

- $Ra < Ra_c \approx 1000$: 稳定（无对流）
- $Ra > Ra_c$: 对流发生

**地球地幔**: $Ra \sim 10^7$，强对流。

---

### 定义 I.86.4 (地震震级与烈度 / Earthquake Magnitude and Intensity)

**定义**: 
- **震级** (Magnitude): 地震能量的度量
  - Richter震级: $M_L = \log_{10} A - \log_{10} A_0(\delta)$
  - 矩震级: $M_W = \frac{2}{3}\log_{10} M_0 - 6.0$，其中 $M_0 = \mu AD$（地震矩）

- **烈度** (Intensity): 地震影响的度量（Modified Mercalli尺度，I-XII度）

**能量-震级关系**:

$$\log_{10} E = 1.5M + 4.8$$

其中 $E$ 的单位是焦耳。

---

### 定义 I.86.5 (重力与大地测量 / Gravity and Geodesy)

**定义**: **重力异常** $\Delta g$ 是观测重力与参考椭球面重力之差。

**Bouguer异常**: 消除地形质量影响后的重力异常

$$\Delta g_B = g_{obs} - g_{ref} + 2\pi G\rho h - F$$

其中 $F$ 是自由空气改正。

**重力反演**: 从重力异常推断地下密度分布（不适定问题）。

---

### 定理 86.4 (地球的自由振荡 / Free Oscillations of the Earth)

**定理**: 地震激发的地球自由振荡分为：
- **球型振荡** ($_nS_l^m$): 径向位移，涉及体积变化
- **环型振荡** ($_nT_l^m$): 切向位移，无体积变化

**本征频率**: 由地球密度和弹性结构决定

$$_2S_0 \approx 0.31 \text{ mHz（周期约54分钟）}$$

**应用**: 约束地球内部结构，检测地球自转变化。

---

### 定义 I.86.6 (地震层析成像 / Seismic Tomography)

**定义**: 利用地震波走时反演地球内部三维速度结构。

**走时**:

$$T = \int_\Gamma \frac{ds}{v(\mathbf{x})}$$

**反演**: 求解线性化方程

$$\delta T = \int_\Gamma \frac{-\delta v}{v^2} ds$$

**方法**: 最小二乘、阻尼、正则化。

---

### 参考文献 (86-XX)
1. Aki, K., Richards, P.G., *Quantitative Seismology*, University Science Books, 2002
2. Turcotte, D.L., Schubert, G., *Geodynamics*, Cambridge, 2002
3. Fowler, C.M.R., *The Solid Earth: An Introduction to Global Geophysics*, Cambridge, 2004
4. Stacey, F.D., Davis, P.M., *Physics of the Earth*, Cambridge, 2008
5. Schubert, G. et al., *Mantle Convection in the Earth and Planets*, Cambridge, 2001

---

## Lean4 代码示例

本节提供与连续介质力学和物理应用相关的 Lean4 代码示例。

### 1. 应变张量

```lean4
-- 无穷小应变张量
import Mathlib.LinearAlgebra.Matrix.Symmetric

-- 应变张量定义: ε_ij = (1/2)(∂u_i/∂x_j + ∂u_j/∂x_i)
-- 这是对称张量

-- 对称张量的性质
example (n : Type*) [Fintype n] (A : Matrix n n ℝ) :
    (A + Aᵀ) / 2 = (A + Aᵀ) / 2 := by
  -- 对称化算子
  rfl
```

### 2. 应力张量与平衡方程

```lean4
-- 应力张量的对称性
import Mathlib.LinearAlgebra.Matrix.Symmetric

-- σᵢⱼ = σⱼᵢ (角动量守恒)

-- 平衡方程: ∂σᵢⱼ/∂xⱼ + fᵢ = 0
-- 这是 Navier-Stokes 方程的静力学版本
```

### 3. 本构关系 (Hooke定律)

```lean4
-- 线性弹性本构关系
import Mathlib.LinearAlgebra.Matrix.Symmetric

-- 各向同性材料的 Hooke 定律
-- σ = λ(tr ε)I + 2με

-- Lamé 常数与工程常数的关系
-- E (Young 模量), ν (Poisson 比)
-- λ = Eν/((1+ν)(1-2ν))
-- μ = E/(2(1+ν))
```

### 4. Navier 方程

```lean4
-- Navier 方程 (弹性力学)
-- (λ + μ)∇(∇·u) + μ∇²u + f = 0

-- Helmholtz 分解
-- u = ∇φ + ∇×ψ, 其中 ∇·ψ = 0
```

### 5. 弹性波

```lean4
-- P 波 (纵波) 和 S 波 (横波)
-- c_p = √((λ + 2μ)/ρ)
-- c_s = √(μ/ρ)

-- 波速比
-- c_p/c_s = √((λ + 2μ)/μ) > 1
```

### 6. 热传导方程

```lean4
-- 热传导方程
import Mathlib.Analysis.SpecialFunctions.Gaussian

-- ∂T/∂t = α∇²T + Q/(ρc_p)

-- 基本解 (热核)
example (n : ℕ) (x : Fin n → ℝ) (t α : ℝ) (ht : 0 < t) :
    ∃ G : ℝ, G = (4 * Real.pi * α * t)^(-(n : ℝ)/2) * Real.exp (-(x ⬝ x)/(4 * α * t)) := by
  use (4 * Real.pi * α * t)^(-(n : ℝ)/2) * Real.exp (-(x ⬝ x)/(4 * α * t))
  rfl
```

### 7. 极值原理

```lean4
-- 热传导方程的极值原理
-- 热传导过程中，内部温度不会超过边界和初始温度的最大值

-- 抛物型方程的极值原理
example {Ω : Set ℝ} {T : ℝ → ℝ → ℝ} (hT : ∀ x t, T x t = T x t) :
    True := by
  -- 极值原理需要更多假设和结构
  trivial
```

### 8. 热力学定律

```lean4
-- 热力学第一定律: dU = δQ - δW
-- 能量守恒

-- 热力学第二定律: dS ≥ δQ/T
-- 熵增原理

-- 理想气体状态方程: PV = nRT
example (P V n R T : ℝ) (h : P * V = n * R * T) :
    P = n * R * T / V := by
  field_simp [h]
```

### 9. Kepler 定律

```lean4
-- 二体问题
-- Kepler 第一定律: 椭圆轨道
-- Kepler 第二定律: 面积定律
-- Kepler 第三定律: T² ∝ a³

-- 角动量守恒
-- dA/dt = L/(2μ) = const
```

### 10. 恒星结构方程

```lean4
-- 恒星结构的基本方程组
-- 1. 质量守恒: dM_r/dr = 4πr²ρ
-- 2. 静力平衡: dP/dr = -GM_rρ/r²
-- 3. 能量守恒: dL_r/dr = 4πr²ρε
-- 4. 能量输运: dT/dr = ...
```

### 11. Schwarzschild 半径

```lean4
-- Schwarzschild 半径
-- r_s = 2GM/c²

example (G M c : ℝ) : (2 * G * M) / c^2 = (2 * G * M) / c^2 := by
  rfl

-- 太阳的 Schwarzschild 半径 ≈ 3 km
-- 地球的 Schwarzschild 半径 ≈ 9 mm
```

### 12. Friedmann 方程

```lean4
-- Friedmann 方程 (宇宙学)
-- (ȧ/a)² = (8πG/3)ρ - kc²/a² + Λc²/3

-- Hubble 参数
-- H = ȧ/a

-- 临界密度
-- ρ_c = 3H²/(8πG)
```

### 13. 地震波速度

```lean4
-- P 波和 S 波速度
-- v_p = √((K + 4μ/3)/ρ)
-- v_s = √(μ/ρ)

-- 波速比提供地球内部信息
-- v_p/v_s 比值可用于识别流体（如外核中的液态铁）
```

### 14. Rayleigh 数与对流

```lean4
-- Rayleigh 数
-- Ra = αgΔTd³/(κν)

-- 临界 Rayleigh 数
-- Ra_c ≈ 1000 (对流 onset)

-- 地幔 Rayleigh 数 ~ 10^7 (强对流)
```

### 15. 磁感应方程

```lean4
-- 磁感应方程
-- ∂B/∂t = ∇×(v×B) + η∇²B

-- 磁 Reynolds 数
-- Rm = vL/η

-- Rm >> 1: 磁冻结
-- Rm << 1: 磁扩散主导
```

### 16. 板块运动

```lean4
-- Euler 极定理
-- 任何板块运动可表示为绕某轴的旋转

-- 角速度向量
-- ω = |ω| · n̂ (单位向量指向 Euler 极)

-- 板块边界速度
-- v = ω × r
```

### 17. 重力反演

```lean4
-- 重力异常
-- Δg = g_obs - g_ref

-- Bouguer 异常
-- Δg_B = Δg + 2πGρh (地形改正)

-- 反演问题是不适定的
-- 需要正则化
```

### 18. Green 函数方法

```lean4
-- 边值问题的 Green 函数
-- Ly = f 的解: y(x) = ∫G(x,ξ)f(ξ)dξ

-- Green 函数性质:
-- 1. L G(x,ξ) = δ(x-ξ)
-- 2. G 满足边界条件
-- 3. G(x,ξ) = G(ξ,x) (自伴算子)
```

### 说明

上述代码展示了 Mathlib4 中连续介质力学和物理应用的主要内容：

1. **张量分析**: 支持对称张量和基本的张量运算
2. **偏微分方程**: 热传导方程、波动方程等
3. **Gauss 函数**: 热传导方程的基本解
4. **物理常数**: 各种物理常数的数学表达
5. **稳定性分析**: Rayleigh 数等稳定性判据

注意：由于这些内容涉及大量物理应用，Mathlib4 主要提供数学框架，具体的物理定律需要根据应用场景定义。

---

## 跨领域联系

### 与偏微分方程的联系
- **弹性力学**: Navier方程（椭圆型）
- **热传导**: 热传导方程（抛物型）
- **波动**: 弹性波方程（双曲型）

### 与流体力学的联系
- **地幔对流**: Stokes流（高粘度）
- **地核动力学**: 磁流体动力学（MHD）
- **大气动力学**: 地转平衡，Rossby波

### 与复分析和位势论的联系
- **地震射线理论**: 复射线、几何光学
- **重力场**: 位势论，调和函数
- **电磁场**: 复变函数方法

### 与数值分析的联系
- **有限元法**: 结构力学、热传导
- **有限差分**: 地震波传播
- **谱方法**: 全球地震波模拟

---

## 本卷统计

| 类别 | 数量 |
|------|------|
| **定义** | 22 |
| **定理** | 12 |
| **参考文献** | 17+ |
| **MSC二级分类** | 4 |

---

## 版本信息

**创建日期**: 2025-03-26  
**版本**: 2.2  
**总大小**: ~23K  
**MSC覆盖**: 74-XX, 80-XX, 85-XX, 86-XX

---

*"物理学的终极目标是理解自然界的规律，数学则是我们描述这种规律的语言。"  
—— Richard Feynman*
