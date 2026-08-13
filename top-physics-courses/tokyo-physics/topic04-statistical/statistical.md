# 東京大学物理系 Phase 1 · 統計力学と熱力学 深度講義

> **课程映射**（SURVEY §9 東大）：統計力学 + 熱力学
> **教材**：Pathria & Beale *Statistical Mechanics* 4ed（統計力学指定）+ Kittel & Kroemer *Thermal Physics* 2ed（日文译本，熱力学/統計入门）+ Zemansky & Dittman *Heat and Thermodynamics*（熱力学指定）+ Reif（参考）
> **定位**：从宏观热力学到微观统计力学再到相变与量子统计，完成「多体」视角的物理闭环。统计力学是连接微观量子力学与宏观热力学的桥梁—— Boltzmann 的 $S = k\ln W$ 把熵还原为微观态计数。東大此课的特色收束是 **Koshiba（2002）/ Kajita（2015）诺奖的粒子物理/宇宙学关联**——中微子、宇宙微波背景、黑洞都是统计力学的高能应用。

---

## 0. 導引：统计力学为何是「物理学的中央车站」

热力学（19 世纪，Carnot/Clausius/Kelvin）是**唯象**的——四条定律 + 一组状态函数，不问微观。统计力学（Boltzmann/Gibbs/Maxwell，19 世纪末）从**微观粒子 + 概率**重建热力学，揭示了温度、熵、热的本质。两条路在 20 世纪汇合：

$$\underbrace{\text{微观：Hamilton 量 + 相空间}}_{\text{力学/量子}} \xrightarrow{\text{系综平均}} \underbrace{\text{配分函数 } Z}_{\text{统计力学}} \xrightarrow{\text{求导}} \underbrace{\text{热力学势}}_{\text{F, G, E, S}}$$

Kittel & Kroemer 走「先热力学后统计」路线（東大熱力学课），Pathria 走「先系综后应用」路线（東大統計力学课）。Phase 1 把两者合并讲透。

---

## 1. 熱力学（Thermodynamics）

### 1.1 四条定律

| 定律 | 内容 | 数学 |
|------|------|------|
| **第零定律** | 热平衡的传递性 $\Rightarrow$ 温度 $T$ 存在 | $A\sim B, B\sim C \Rightarrow A\sim C$ |
| **第一定律** | 能量守恒 | $dU = \delta Q - \delta W = TdS - pdV$ |
| **第二定律** | 熵增（孤立系）| $\Delta S \geq 0$，$dS \geq \delta Q/T$ |
| **第三定律** | $T\to0$ 时 $S\to0$（完美晶体）| $\lim_{T\to0}S = 0$ |

### 1.2 状态函数与热力学势

从内能 $U(S,V)$ 经 Legendre 变换得到各势：

| 势 | 定义 | 自然变量 | 适用 |
|----|------|----------|------|
| 内能 $U$ | — | $S, V$ | 孤立系 |
| 焓 $H$ | $U + pV$ | $S, p$ | 等压过程 |
| **Helmholtz 自由能** $F$ | $U - TS$ | $T, V$ | 等温等容（统计力学标准）|
| **Gibbs 自由能** $G$ | $U - TS + pV = \mu N$ | $T, p$ | 等温等压（化学/相变）|

平衡判据：等温等容 $\Rightarrow F$ 极小；等温等压 $\Rightarrow G$ 极小。

### 1.3 Maxwell 关系

从 $dU = TdS - pdV$ 的全微分性质（混合偏导相等）推出 4 个 Maxwell 关系，例：

$$\left(\frac{\partial T}{\partial V}\right)_S = -\left(\frac{\partial p}{\partial S}\right)_V$$

这是把「难测量的量」用「易测量的量」表达的桥梁——東大熱力学入试的经典考点。

### 1.4 Carnot 循环与效率

理想可逆热机（两个等温 + 两个绝热），效率**只依赖两个温度**：

$$\eta_{\text{Carnot}} = 1 - \frac{T_C}{T_H}$$

这是第二定律的定量表述——任何热机效率不超过 Carnot。Clausius 据此定义熵 $dS = \delta Q_{\text{rev}}/T$。

### 1.5 熵的微观意义（Boltzmann）

**Boltzmann 公式**（刻在他维也纳墓碑上）：

$$\boxed{S = k_B \ln W}$$

$W$ 是给定宏观态对应的微观态数。这把「不可逆性」（宏观熵增）追溯到「微观态计数」——孤立系趋向微观态最多的宏观态，纯属概率。

---

## 2. 系综理論（Ensemble Theory）

### 2.1 微正则系综（Microcanonical）

孤立系（$E, V, N$ 固定），等概率原理：每个可达微观态等概率。

$$S(E,V,N) = k_B\ln\Omega(E,V,N), \quad \frac{1}{T} = \left(\frac{\partial S}{\partial E}\right)_{V,N}, \quad \frac{p}{T} = \left(\frac{\partial S}{\partial V}\right)_{E,N}$$

$\Omega$ 是相空间中能量 $E \pm \delta E$ 壳层内的微观态数。

### 2.2 正则系综（Canonical）

与热库接触（$T, V, N$ 固定），能量可涨落。**Boltzmann 分布**：

$$P_i = \frac{e^{-\beta E_i}}{Z}, \quad \beta = \frac{1}{k_BT}, \quad Z = \sum_i e^{-\beta E_i} \text{（配分函数）}$$

一切热力学量从 $Z$ 求导：

$$F = -k_BT\ln Z, \quad U = -\frac{\partial\ln Z}{\partial\beta}, \quad S = k_B(\ln Z + \beta U)$$

> **关键洞察**：配分函数 $Z$ 是统计力学的「生成函数」——知道 $Z$ 就知道一切。这是 Kittel & Kroemer 全书的核心方法论。

经典连续极限：$Z = \frac{1}{N!h^{3N}}\int e^{-\beta H(\vec{p},\vec{q})}d^{3N}p\,d^{3N}q$（$1/N!$ 修正 Gibbs 悖论，$h^{3N}$ 量子相格体积）。

### 2.3 巨正则系综（Grand Canonical）

与热库+粒子库接触（$T, V, \mu$ 固定），能量与粒子数均可涨落。**巨配分函数**：

$$\mathcal{Z} = \sum_{N=0}^{\infty}\sum_i e^{-\beta(E_{i,N} - \mu N)} = \sum_N z^N Z_N, \quad z = e^{\beta\mu}$$

$$\langle N\rangle = z\frac{\partial\ln\mathcal{Z}}{\partial z}, \quad \Phi = -k_BT\ln\mathcal{Z} = -pV$$

巨正则系综是量子统计（Bose/Fermi）的自然舞台——粒子数不守恒的光子气、半导体载流子都用它。

### 2.4 等概率原理的动力学根基

为什么微观态等概率？**遍历假说**（ergodic hypothesis）：系统在长时间内遍历等能面上所有微观态。Liouville 定理（力学篇 §3.3）保证相空间密度不散——这是等概率的动力学辩护。严格遍历性是数学难题，但物理上「足够混沌」的系统都满足。

---

## 3. 量子統計（Quantum Statistics）

### 3.1 全同粒子与交换对称性

量子力学中，全同粒子交换后波函数只差符号：

| 类型 | 自旋 | 波函数对称性 | 占据数 |
|------|------|------------|--------|
| **玻色子** Bose | 整数（0,1,2,…）| 对称 | 任意多个同态 |
| **费米子** Fermi | 半整数（1/2,3/2,…）| 反对称 | 每态至多 1（Pauli）|

### 3.2 Bose–Einstein 与 Fermi–Dirac 分布

巨正则系综下，能级 $\epsilon_i$（简并 $g_i$）的平均占据数：

$$\boxed{\bar{n}_i = \frac{g_i}{e^{\beta(\epsilon_i - \mu)} \mp 1}} \quad \begin{cases}- \text{（Bose–Einstein）}\\ + \text{（Fermi–Diri）}\end{cases}$$

- **Bose–Einstein (BE)**：分母 $-$ 号，化学势 $\mu \leq \epsilon_0$（基态）。$\mu\to\epsilon_0$ 时基态宏观占据 $\Rightarrow$ **Bose–Einstein 凝聚（BEC）**。
- **Fermi–Dirac (FD)**：分母 $+$ 号，$T=0$ 时 $\epsilon < \mu_F$ 全填满（Fermi 海），$\epsilon > \mu_F$ 全空。

高温/低密度极限（$\bar{n} \ll 1$）两者都退化为 **Maxwell–Boltzmann 分布** $\bar{n} \propto e^{-\beta\epsilon}$（经典统计）。

### 3.3 黑体辐射（Planck 定律）

光子是玻色子（自旋 1），数不守恒 $\Rightarrow$ $\mu = 0$。模式密度 $g(\nu)d\nu = 8\pi\nu^2/c^3\,d\nu$，平均能量 $\bar{E} = h\nu/(e^{h\nu/k_BT}-1)$。

**Planck 黑体辐射谱**（1900，量子力学诞生）：

$$u(\nu, T) = \frac{8\pi h\nu^3}{c^3}\frac{1}{e^{h\nu/k_BT}-1}$$

高温低频 $\Rightarrow$ Rayleigh–Jeans $u \propto \nu^2 T$（经典，紫外灾难的根源）；高频 $\Rightarrow$ Wien $u \propto \nu^3 e^{-h\nu/k_BT}$。Planck 公式统合两者。

> **東大关联**：**宇宙微波背景辐射（CMB）**温度 2.725 K，是完美的 Planck 黑体谱——宇宙本身就是个黑体腔！这是大爆炸理论的关键证据，也是東大宇宙論课（SURVEY §9 研究生）的核心数据。

### 3.4 Debye 模型（声子 = 玻色子）

固体晶格振动量子化为**声子**（自旋 0 玻色子）。低温热容 $T^3$ 律（Debye 1912）：

$$C_V \approx \frac{12\pi^4}{5}Nk_B\left(\frac{T}{\Theta_D}\right)^3, \quad T \ll \Theta_D$$

高温趋向 Dulong–Petit 经典值 $3Nk_B$。这统一了量子与经典固体的热性质。

### 3.5 Fermi 气体（电子气）

金属中的传导电子是费米气体。Fermi 能 $\epsilon_F = \frac{\hbar^2}{2m}(3\pi^2 n)^{2/3}$（$n$ 为电子密度）。$T=0$ 时所有 $\epsilon < \epsilon_F$ 填满。

电子气热容：只有 Fermi 面附近 $O(k_BT)$ 的电子可激发 $\Rightarrow$

$$C_V^{\text{el}} \approx \frac{\pi^2}{2}Nk_B\frac{T}{T_F} \ll Nk_B \quad \text{（远小于经典预期）}$$

这是为什么金属电子对热容贡献远小于 Dulong–Petit 值——纯量子效应。

---

## 4. 相転移（Phase Transitions）

### 4.1 相变分类（Ehrenfest）

- **一级**：一阶导（$S, V$）不连续，有潜热（冰熔化、水沸腾）。
- **连续（二级）**：一阶导连续，二阶导（$C_V, \kappa_T$）发散/不连续（超流、铁磁、超导）。

### 4.2 Ising 模型——相变的万能模型

最近邻自旋 $s_i = \pm 1$，Hamilton 量：

$$H = -J\sum_{\langle i,j\rangle} s_i s_j - h\sum_i s_i$$

- **1D**：无相变（任意 $T > 0$ 无长程序）。
- **2D**（Onsager 1944 精确解）：临界温度 $k_BT_c/J \approx 2.269$，自发磁化 $M \sim (T_c - T)^{1/8}$（临界指数 $\beta = 1/8$）。这是统计力学最著名的精确结果之一。
- **平均场**：$T_c^{\text{MF}} = zJ/k_B$（$z$ 配位数），临界指数 $\beta = 1/2$（与精确 2D 值不同——涨落被忽略）。

### 4.3 Landau 理论（序参量 + 对称性）

Landau（1937）把连续相变统一为**序参量** $\eta$（对称性破缺标志）的自由能展开：

$$F(\eta) = F_0 + a(T-T_c)\eta^2 + b\eta^4 + \cdots$$

- $T > T_c$：$a>0$，极小在 $\eta = 0$（对称相）。
- $T < T_c$：$a<0$，极小在 $\eta \neq 0$（破缺相，$\eta \sim (T_c - T)^{1/2}$）。

临界指数在 Landau/平均场理论下普适（$\beta = 1/2, \gamma = 1, \delta = 3$）。**重整化群**（Wilson 1982 诺奖）解释了为什么临界指数按维度/对称性**普适类**分组，与微观细节无关——这是统计力学最深的成就之一。

### 4.4 临界现象与关联长度

临界点处**关联长度** $\xi \to \infty$，系统出现尺度不变的涨落。这就是为什么临界乳光（临界点液体变浑浊）、各种临界指数有**标度关系**。

---

## 5. Python 数值验证

### 5.1 理想气体配分函数与热力学量

```python
# ideal_gas_Z.py —— 单原子理想气体的配分函数与内能/熵
import numpy as np
k_B, hbar, m = 1.381e-23, 1.055e-34, 4.65e-26  # N2 分子
V, N = 1e-3, 6.022e23   # 1L, 1mol
def thermo(T):
    lam = hbar*np.sqrt(2*np.pi/(m*k_B*T))  # 热波长
    Z1 = V/lam**3                          # 单粒子配分函数
    Z = Z1**N / np.math.factorial(0)       # 略 1/N!（对数用 Stirling）
    from math import lgamma
    lnZ = N*np.log(Z1) - N*lgamma(N+1) + N   # Stirling: ln N! ≈ NlnN-N
    U = k_B*T**2 * N/2 * (3/T)               # U=3/2 NkT（能均分）
    F = -k_B*T*lnZ
    S = (U - F)/T
    return U, F, S
for T in [100, 300, 500, 1000]:
    U,F,S = thermo(T)
    print(f"T={T:4d}K: U={U:.1f}J  F={F:.1f}J  S={S:.1f}J/K (3/2NkT={1.5*N*k_B*T:.1f})")
```

### 5.2 Planck 黑体辐射谱（CMB 验证）

```python
# planck_cmb.py —— Planck 谱 + Wien 位移定律验证 CMB
import numpy as np
h, c, k_B = 6.626e-34, 3e8, 1.381e-23
def planck_nu(nu, T):  # 频率空间谱密度
    return 8*np.pi*h*nu**3/c**3 / (np.exp(h*nu/(k_B*T)) - 1)
# Wien 位移定律（波长空间，标准形式）：λ_max·T = b = 2.898e-3 m·K
b = 2.898e-3
for T, label in [(2.725,"CMB"), (300,"室温"), (5800,"太阳表面")]:
    lam_max = b / T                        # 波长空间峰值
    nu_range = np.logspace(8, 15, 2000)
    u = planck_nu(nu_range, T)
    nu_pk = nu_range[np.argmax(u)]         # 频率空间峰值
    print(f"T={T:7.1f}K ({label}): λ_max={lam_max*1e6:7.1f}μm  "
          f"ν_peak={nu_pk:.2e}Hz")
print(f"\nCMB λ_max={b/2.725*1e3:.1f}mm（微波！）→ 宇宙是 2.725K 黑体")
print(f"太阳 λ_max={b/5800*1e9:.0f}nm（可见绿光）← 为什么太阳是黄的")
# 注：频率空间峰与波长空间峰不同（Jacobian dν=-c/λ²dλ 偏移），这是 Planck 谱的已知细节
```

### 5.3 Ising 模型（Monte Carlo，Metropolis 算法）

```python
# ising_mc.py —— 2D Ising 模型 Monte Carlo，验证 T_c≈2.269J/k_B
import numpy as np
def mc_ising(L, T, J=1.0, kB=1.0, steps=50000):
    s = np.random.choice([-1,1], (L,L))
    E0 = -J*np.sum(s*np.roll(s,1,0) + s*np.roll(s,1,1))
    M_list, E_list = [], []
    for _ in range(steps):
        i, j = np.random.randint(L), np.random.randint(L)
        nb = s[(i-1)%L,j]+s[(i+1)%L,j]+s[i,(j-1)%L]+s[i,(j+1)%L]
        dE = 2*J*s[i,j]*nb
        if dE < 0 or np.random.rand() < np.exp(-dE/(kB*T)):
            s[i,j] *= -1
        if _ % 100 == 0:
            M_list.append(abs(np.mean(s)))
            E_list.append(-J*np.mean(s*np.roll(s,1,0)+s*np.roll(s,1,1)))
    return np.mean(M_list[-100:]), np.std(M_list[-100:])**2*T  # χ=kBT<ΔM²>
print("2D Ising (L=16):")
for T in [1.5, 2.0, 2.269, 2.5, 3.0, 4.0]:
    M, chi = mc_ising(16, T)
    print(f"  T={T:.2f}: |M|={M:.3f}  χ={chi:.3f}  "
          f"({'有序' if M>0.3 else '无序'})")
print("\n理论 T_c = 2.269J/k_B (Onsager 精确解)")
```

### 5.4 Fermi–Dirac 分布（电子气热容验证）

```python
# fermi_gas.py —— Fermi-Dirac 分布与电子热容 T 线性律
import numpy as np
m, n = 9.11e-31, 1e29   # 电子质量, 密度
hbar = 1.055e-34
kF = (3*np.pi**2*n)**(1/3)
epsF = hbar**2*kF**2/(2*m)
TF = epsF/1.381e-23
print(f"Fermi 能 εF={epsF:.2e} J = {epsF/1.602e-19:.2f} eV")
print(f"Fermi 温度 TF={TF:.0f} K (>>室温, 量子简并)")
def fd(eps, mu, T):
    return 1/(np.exp((eps-mu)/(1.381e-23*T))+1)
# 室温下分布几乎与 T=0 相同（TF 巨大）
eps = np.linspace(0, 2*epsF, 1000)
for T in [0, 300, TF//10]:
    f = fd(eps, epsF, T) if T>0 else (eps < epsF).astype(float)
    n_occ = np.trapz(f*np.sqrt(eps), eps)/np.trapz(np.sqrt(eps),eps)
    print(f"T={T:7d}K: 占据比例={n_occ:.3f} (T=0时全部填满ε<εF)")
print(f"\n电子热容 C∝T/T_F: 室温 T/TF={300/TF:.1e} → 电子贡献被晶格{T^3}掩盖")
```

---

## 6. 東大特色：Koshiba・Kajita 與粒子物理/宇宙学

统计力学在東京大学有一条贯穿粒子物理与宇宙学的主线：

### 6.1 中微子与统计权重

中微子是**费米子**（自旋 1/2），遵循 Fermi–Dirac 分布。大爆炸核合成（BBN）和 CMB 分析中，中微子的有效自由度 $N_{\text{eff}}$ 直接影响宇宙的能量密度——这是统计力学在宇宙学的精确应用。

- **小柴昌俊（Koshiba, 2002 诺贝尔奖）**：Super-Kamiokande 探测太阳/大气中微子，确认中微子流量与 Bahcall 标准太阳模型（用统计力学算太阳核心 $T \approx 1.5\times10^7$ K 的核反应率）对比。
- **梶田隆章（Kajita, 2015 诺贝尔奖）**：发现大气中微子振荡 $\nu_\mu \to \nu_\tau$，证明中微子有质量——这改变了标准模型的费米子质量谱。中微子振荡的概率公式 $P \sim \sin^2(2\theta)\sin^2(\Delta m^2 L/4E)$ 背后是量子相干叠加，而宇宙中微子背景（CνB, $T \approx 1.95$ K）的统计性质是未来探测目标。

### 6.2 黑洞热力学（Hawking/Bekenstein）

黑洞有温度 $T_H = \hbar c^3/(8\pi G M k_B)$ 和熵 $S_{BH} = k_B c^3 A/(4G\hbar)$（$A$ 视界面积）。这是统计力学 + 广义相对论 + 量子力学的交叉——**Hawking 辐射**是黑洞的黑体辐射！東大 Kavli IPMU（宇宙物理数学研究所）是这类研究的前沿。

> 这条线说明：统计力学不是「古老的热学」，而是连接量子场论、宇宙学、引力论的活语言。

---

## 7. 習題集

**习题 1（★）**　一理想气体等温（$T$）从 $V_1$ 膨胀到 $V_2$。求 $\Delta S, \Delta U, Q, W$。
> *答案*：$\Delta S = nR\ln(V_2/V_1)$，$\Delta U = 0$（理想气体 $U$ 只依赖 $T$），$Q = W = nRT\ln(V_2/V_1)$。

**习题 2（★★）**　用配分函数 $Z = V/\lambda^3$（$\lambda = h/\sqrt{2\pi mk_BT}$ 热波长）推导理想气体状态方程 $pV = Nk_BT$。
> *提示*：$p = k_BT(\partial\ln Z/\partial V)_T$，对 $N$ 个无相互作用粒子 $Z_N = Z_1^N/N!$。

**习题 3（★）**　太阳（$T \approx 5800$ K）的总辐射功率约 $3.8\times10^{26}$ W。用 Stefan–Boltzmann 定律 $j = \sigma T^4$（$\sigma = 5.67\times10^{-8}$）估算太阳半径，与实测 $R_\odot \approx 7\times10^8$ m 比较。
> *答案*：$R = \sqrt{L/(4\pi\sigma T^4)} \approx 6.9\times10^8$ m ✓。

**习题 4（★★）**　推导 Bose–Einstein 凝聚的临界温度：$N$ 个无自旋玻色子（质量 $m$）在体积 $V$ 中，$T < T_c$ 时基态宏观占据。求 $T_c$。
> *答案*：$T_c = \frac{2\pi\hbar^2}{mk_B}\left(\frac{n}{\zeta(3/2)}\right)^{2/3}$，$\zeta(3/2)\approx 2.612$。$T<T_c$ 时凝聚分数 $N_0/N = 1-(T/T_c)^{3/2}$。

**习题 5（★）**　铜的电子密度 $n \approx 8.5\times10^{28}$ m$^{-3}$。求 Fermi 能（eV）与 Fermi 温度。
> *答案*：$\epsilon_F = \frac{\hbar^2}{2m_e}(3\pi^2 n)^{2/3} \approx 7.0$ eV，$T_F \approx 8\times10^4$ K $\gg$ 室温。

**习题 6（★★）**　用 Landau 平均场理论推导铁磁相变（序参量 $M$）的临界指数 $\beta, \gamma, \delta$，并说明它们为何与精确 2D Ising 值不同。
> *答案*：Landau $F = a(T-T_c)M^2 + bM^4$，得 $\beta = 1/2, \gamma = 1, \delta = 3$。2D Ising 精确 $\beta = 1/8$——差异来自临界区涨落（平均场忽略）。

---

## 8. 参考文献

1. Pathria, Beale. *Statistical Mechanics* 4ed. Butterworth-Heinemann, 2021.（東大統計力学指定）
2. Kittel, Kroemer. *Thermal Physics* 2ed. Freeman, 1980.（熱力学/統計入门，日文译本）
3. Zemansky, Dittman. *Heat and Thermodynamics* 7ed. McGraw-Hill.（熱力学经典）
4. Reif, F. *Fundamentals of Statistical and Thermal Physics*. Waveland, 2009.（最详尽，参考）
5. Huang, Kerson. *Statistical Mechanics* 2ed. Wiley.（研究生级别）
6. Landau, Lifshitz. *Statistical Physics* Vol 5.（俄系经典，简洁）
7. 戸田盛和. 『統計力学』（岩波書店）——東大经典本土教材，从系综到相变紧凑。
8. 中村允. 『熱学・統計力学』（裳華房）——東大推荐，习题丰富。

---

**完成日期**：2026-08-12　|　**对应 SURVEY §9 東大**：統計力学 + 熱力学　|　**特色收束**：Koshiba/Kajita 中微子 + CMB + 黑洞热力学

---

## 🎯 费曼式入口（白话版）

> **一句话解释**：统计力学是「从 $10^{23}$ 个分子的舞蹈中，看出温度、压强、熵」的学问。它的核心信念是 Boltzmann 的 $S = k_B \ln W$——熵就是「有多少种微观排布方式对应同一个宏观状态」。
>
> **生活类比**：一个乱糟糟的房间（高熵）有无数种「乱」的方式；一个整洁的房间（低熵）只有少数几种摆法。所以房间自然变乱——这就是热力学第二定律。但统计力学告诉你：不是「宇宙讨厌整洁」，而是「乱的微观状态数量压倒性地多」。熵增不是命令，是概率。
>
> **反直觉发现**：
> - **麦克斯韦妖悖论**：一个分子大小的小妖隔开冷热气体，看似违反第二定律。Landauer（1961）解药：妖「擦除」信息时必须耗散 $k_BT\ln 2$ 的热量——信息是物理的。这就是现代「信息热力学」的起源。
> - **负温度比正无穷还热**：自旋系统（能量有上限）可以出现 $T < 0$ 状态，热量会从「负温度」流向「正温度」。1951 年 Purcell Pound 实验。
> - **玻色-爱因斯坦凝聚（BEC）**：温度低到一定程度，宏观数量的玻色子集体跳进同一个量子态——一种「宏观量子现象」。常温看不见，但 1995 年（Cornell/Wieman/Ketterle 2001 诺奖）碱金属气体做到了。
> - **黑洞也有熵**：$S_{BH} = k_B c^3 A / (4G\hbar)$，与视界面积成正比，不是体积！这暗示时空本身是「量子信息」的全息编码——AdS/CFT 对应的起源。

---

## 🔗 衔接：从哪来，到哪去

### 前置
- **力学**：Hamilton 量、相空间、Liouville 定理（统计力学的动力学基础）。
- **量子力学**：Bose-Einstein / Fermi-Dirac 分布来自全同粒子对称性；密度矩阵。
- **数学**：组合数学（微观态计数）、复变（配分函数的解析性质）、概率论。

### 本课解决了什么危机
- **热力学的「唯象」之困**：19 世纪的热力学（Carnot/Clausius/Kelvin）只有宏观定律，不知「熵」是什么。**Boltzmann 1877**：$S = k_B \ln W$——熵是微观态计数，热力学第二定律还原为概率。
- **Maxwell-Boltzmann 分布的导出**：从 Newton + 概率假设推出气体分子速度分布，与实验（Stern-Gerlach 类）完全符合。

### 本课留下的新危机（通往下一站）
- **非平衡态统计力学**：本课主要讲平衡态。但生命、气候、发动机都是**远离平衡**的开放系统。**Prigogine**（1977 诺奖）的耗散结构、**Jarzynski/Crooks**涨落定理（1997）正在重写非平衡统计力学。
- **量子多体问题**：$10^{23}$ 个相互作用粒子，精确解不可能。**密度矩阵重整化群（DMRG, White 1992）+ 张量网络（PEPS/MERA）+ 量子蒙特卡洛**是当代凝聚态的核心工具。
- **信息与物理的统一**：Maxwell 妖、Landauer 原理、黑洞信息悖论 → **It from Qubit**：物理学可能本质是信息处理。

### 后续（東大路径）
| 方向 | 课程 | 用到本课什么 |
|------|------|-------------|
| 凝聚态多体 | 物性物理 | 量子统计 → 电子气、声子、超流 |
| 宇宙学 | 一般相対論/宇宙論 | CMB 黑体谱、原初核合成、暗物质 |
| 化学物理 | 物化 | 配分函数 → 化学势、相图 |
| 生物物理 | 选修 | 蛋白质折叠、分子马达、熵弹性 |
| 机器学习 | 选修 | Boltzmann 机、自由能、采样 |

---

## 🏭 理论联系实际：5 个应用

1. **量子简并气体（BEC + 费米气体）**：1995 BEC 实现，2000s 费米气体简并（2005 Jin/Thomas/Regal）。这些系统是「干净的多体量子模拟器」，可调相互作用、维度、温度，验证 Hubbard 模型、BCS-BEC crossover。
2. **量子退火机 D-Wave**：本质是「Ising 自旋玻璃」的统计力学基态搜索。Google、NASA、大众汽车用它做物流优化。東京大学 2024–2025 接入 D-Wave Advantage 做量子退火研究。
3. **超流 He-4 + He-3**：BEC 思想的液态实现。He-4 在 2.17 K 以下无粘流动（Kapitza 1937），He-3 在 mK 级别有超流（1972 Osheroff/Richardson/Lee 1996 诺奖）——是 p 波配对的「非常规超流」，与高温超导机制有深刻联系。
4. **蒙特卡洛与统计物理计算**：Ising 模型 MC（Metropolis 1953）、Lattice QCD（计算质子质量）、蛋白质折叠（Folding@home / AlphaFold）——统计力学算法是现代计算物理的基石。東大物性研的「物质设计」大量依赖。
5. **中微子宇宙学（小柴/梶田遗产）**：宇宙微波背景（CMB）是 2.725 K 黑体辐射（完美 Planck 谱）；宇宙中微子背景 $T \approx 1.95$ K 仍未直接探测。统计力学 + 粒子物理 + 宇宙学的交叉——東大 Kavli IPMU 的核心方向。

---

## 🔬 最新研究前沿（2024-2026）

- **非平衡涨落定理 + 量子热机**：在量子层面实现 Otto/Carnot 循环（量子热机），2024–2025 多组实验验证量子 Jarzynski 等式。量子热机的效率能否超过经典？这是「量子热力学」前沿。
- **机器学习重写统计力学**：2024 年多篇 Nature 论文用扩散模型（Diffusion Models）生成平衡态构型，速度比传统 MC 快 $10^6$ 倍；反向地，统计力学的自由能方法用于训练大模型。
- **Hyper-Kamiokande 建设进展（2027 启动计划）**：26 万吨水切伦科夫探测器，将测量 CP 破坏、质子衰变。**2026 年 8 月，Super-Kamiokande 公布首次发现「弥散超新星中微子背景（DSNB）」的迹象**——2.6σ（99.5% CL），DSNB 通量 $\sim 3.6\ \text{cm}^{-2}\text{s}^{-1}$，来自宇宙史上所有核坍缩超新星的总和。这正是统计力学在宇宙学中的高能应用。
- **时空全息与量子纠错（2024–2026）**：AdS/CFT 对应把黑洞热力学与量子纠错码联系起来——时空本身可能是量子纠错的 emergent 现象。東大 Kavli IPMU 在「It from Qubit」方向活跃。
- **活性物质 + 非平衡相变**：鸟群、细菌、自驱动胶体——每个个体持续耗能，远离平衡。2024–2025 发现活性物质的「flocking」相变属于新型 universality class，挑战传统 Landau 理论。

---

## 🗺️ 学习 Roadmap（Tokyo 路径）

```
熱学（2 年级， Zemansky / Kittel-Kroemer）
  ↓ 热力学四大定律、Carnot 循环、熵
統計力学（3–4 年级， Pathria / Reif）
  ↓ 核心关卡 ↓
  ├─ 微正则 / 正则 / 巨正则系综
  ├─ 配分函数 → 全部热力学量
  ├─ 量子统计：Bose-Einstein + Fermi-Dirac
  ├─ 相变（Ising / Landau / 临界指数）
  └─ 涨落 + 响应（涨落-耗散定理）
研究生进阶
  ├─ 重整化群（Wilson，Phase 2 进阶）
  ├─ 非平衡统计力学（涨落定理、Jarzynski）
  ├─ 量子多体（Fetter-Walecka，凝聚态方向）
  └─ Lattice QCD / 宇宙学早期宇宙统计
```

**知识检查**：
- [ ] 能从配分函数 $Z = \sum e^{-\beta E_i}$ 推出 $F, U, S, p$（对应公式）。
- [ ] 能解释为什么铜的电子热容 $C_e \propto T$ 而声子 $C_{ph} \propto T^3$，并说明室温下哪个占主导。
- [ ] 能算 Bose-Einstein 凝聚临界温度 $T_c$，并解释 $T < T_c$ 时基态宏观占据。
- [ ] 能说出 Ising 模型精确解（Onsager 1944）的临界指数与 Landau 平均场为什么不同（涨落！）。
- [ ] 能用 Boltzmann 分布解释化学反应平衡常数 $K \propto e^{-\Delta G/k_BT}$。
- [ ] 理解黑洞熵公式 $S = k_B c^3 A/(4G\hbar)$ 为什么暗示时空是「全息」的。
