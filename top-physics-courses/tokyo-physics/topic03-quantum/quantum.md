# 東京大学物理系 Phase 1 · 量子力学 A/B 深度講義

> **课程映射**（SURVEY §9 東大）：量子力学 A（本科）+ 量子力学 B（本科高年级/研究生衔接）
> **教材**：David J. Griffiths *Introduction to Quantum Mechanics* 3ed（A 指定，日文译本）+ J. J. Sakurai & Jim Napolitano *Modern Quantum Mechanics* 3ed（B 指定，日文译本）+ Cohen-Tannoudji（参考）
> **定位**：从波函数到算符到矩阵力学，完成非相对论量子力学的核心闭环。東大量子力学 B 的招牌是用 Sakurai 的**Dirac 符号**贯穿始终——让学生先建立抽象的 Hilbert 空间直觉，再用具体表象（位置/动量/能量）落地。这是朝永（QED 重整化）和湯川（介子理论）的理论训练根基。

---

## 0. 導引：量子力学的「两种语言」

量子力学有两种等价的表述：

| 语言 | 创立者 | 核心对象 | 求解方式 |
|------|--------|----------|----------|
| **波动力学** | Schrödinger (1926) | 波函数 $\psi(x,t)$ | 解 PDE（偏微分方程）|
| **矩阵力学** | Heisenberg (1925) | 算符 $\hat{A}$、矩阵元 | 代数（对易关系）|

Griffiths 走 Schrödinger 路线（先 $\psi$，后算符），Sakurai 走 Dirac 路线（先 ket $|\psi\rangle$ 与对易子，后表象）。東大 A/B 分别对应这两条路，互为镜像。最后由 **Born 概率诠释**（$|\psi|^2$ = 概率密度）和 **von Neumann 公理体系**统一。

---

## 1. 波函数と Schrödinger 方程

### 1.1 公设（Postulates of QM）

1. **态用波函数描述**：$|\psi\rangle \in \mathcal{H}$（Hilbert 空间），位置表象 $\psi(x,t) = \langle x|\psi\rangle$。
2. **可观测量是厄米算符**：$\hat{A}^\dagger = \hat{A}$，本征值是实数 $\Rightarrow$ 可测量。
3. **测量塌缩**：测 $\hat{A}$ 得本征值 $a_n$ 的概率 $P(a_n) = |\langle a_n|\psi\rangle|^2$（Born 规则），测后态塌缩到 $|a_n\rangle$。
4. **时间演化**：$\hat{H}|\psi\rangle = i\hbar\partial_t|\psi\rangle$（Schrödinger 方程）。

### 1.2 含时与定态 Schrödinger 方程

**含时 Schrödinger 方程**（TDSE）：

$$i\hbar\frac{\partial\Psi}{\partial t} = \hat{H}\Psi = \left[-\frac{\hbar^2}{2m}\nabla^2 + V(\vec{r},t)\right]\Psi$$

若 $V$ 不显含时间，分离变量 $\Psi(\vec{r},t) = \psi(\vec{r})\,e^{-iEt/\hbar}$，得**定态 Schrödinger 方程**（TISE）：

$$\hat{H}\psi = E\psi \quad\Longleftrightarrow\quad -\frac{\hbar^2}{2m}\nabla^2\psi + V\psi = E\psi$$

$\psi_n$ 是能量本征态，$E_n$ 是离散能级。一般态 $\Psi = \sum_n c_n\psi_n e^{-iE_n t/\hbar}$。

### 1.3 归一化与概率流

归一化 $\int|\psi|^2 d^3r = 1$。**连续性方程**（概率守恒）：

$$\frac{\partial|\psi|^2}{\partial t} + \nabla\cdot\vec{j} = 0, \qquad \vec{j} = \frac{\hbar}{2mi}(\psi^*\nabla\psi - \psi\nabla\psi^*)$$

### 1.4 不确定性原理

对两个算符 $\hat{A}, \hat{B}$，对易子 $[\hat{A},\hat{B}] = \hat{A}\hat{B} - \hat{B}\hat{A}$。**Robertson 不等式**：

$$\sigma_A^2 \sigma_B^2 \geq \left(\frac{1}{2i}\langle[\hat{A},\hat{B}]\rangle\right)^2$$

对位置-动量 $[\hat{x},\hat{p}] = i\hbar \Rightarrow \sigma_x\sigma_p \geq \hbar/2$。

---

## 2. 一维問題：井戸・調和振動子（势阱、谐振子）

### 2.1 无限深方势阱（Particle in a Box）

$V(x) = 0$（$0<x<a$），$V = \infty$（外部）。边界条件 $\psi(0)=\psi(a)=0$。解：

$$\psi_n(x) = \sqrt{\frac{2}{a}}\sin\frac{n\pi x}{a}, \quad E_n = \frac{n^2\pi^2\hbar^2}{2ma^2}, \quad n=1,2,3,\ldots$$

> **反直觉**：最低能 $E_1 > 0$（零点能）——粒子不能静止！这是不确定性原理的直接后果：$\Delta x \sim a \Rightarrow \Delta p \gtrsim \hbar/(2a) \Rightarrow E \gtrsim \hbar^2/(8ma^2)$。

### 2.2 量子谐振子（QHO）—— 量子场论的种子

$V(x) = \frac{1}{2}m\omega^2 x^2$。这是物理学的「万能模型」——任何势的极小值附近都近似谐振（Taylor 展开）。

**代数解法（Dirac 阶梯算符）**——这是 Sakurai 的招牌方法：

定义升/降算符：
$$\hat{a} = \sqrt{\frac{m\omega}{2\hbar}}\left(\hat{x} + \frac{i\hat{p}}{m\omega}\right), \quad \hat{a}^\dagger = \sqrt{\frac{m\omega}{2\hbar}}\left(\hat{x} - \frac{i\hat{p}}{m\omega}\right)$$

对易关系 $[\hat{a}, \hat{a}^\dagger] = 1$。Hamilton 量化为：

$$\hat{H} = \hbar\omega\left(\hat{a}^\dagger\hat{a} + \tfrac{1}{2}\right) = \hbar\omega\left(\hat{N} + \tfrac{1}{2}\right)$$

$\hat{N} = \hat{a}^\dagger\hat{a}$ 是**粒子数算符**，本征值 $n = 0, 1, 2, \ldots$。能级：

$$\boxed{E_n = \hbar\omega\left(n + \tfrac{1}{2}\right)}$$

基态 $|0\rangle$ 被 $\hat{a}|0\rangle = 0$（湮灭真空）确定，激发态 $|n\rangle = \frac{(\hat{a}^\dagger)^n}{\sqrt{n!}}|0\rangle$。

> **关键**：这套 $\hat{a}, \hat{a}^\dagger$ 代数直接推广到量子场论——把每个简谐模式量子化为粒子（声子、光子、胶子……）。東大量子场论课（SURVEY §9 研究生）从这里起手。

### 2.3 势垒隧穿（Tunneling）

方势垒 $V_0$（宽 $a$），能量 $E < V_0$。经典力学粒子被全反射；量子力学**透射系数**：

$$T \approx e^{-2\kappa a}, \quad \kappa = \sqrt{2m(V_0-E)}/\hbar$$

指数小但非零！这是 $\alpha$ 衰变（Gamow 1928）、扫描隧道显微镜（STM, Binning & Rohrer 1986 诺奖）的物理。

---

## 3. 三維・水素原子（Hydrogen Atom）

### 3.1 三维定态与分离变量

中心势 $V(r)$ 下，$\psi(r,\theta,\phi) = R_{nl}(r)Y_l^m(\theta,\phi)$ 分离为径向 + 球谐函数。

**球谐函数** $Y_l^m$ 是 $\hat{L}^2$ 和 $\hat{L}_z$ 的共同本征态：

$$\hat{L}^2 Y_l^m = \hbar^2 l(l+1)Y_l^m, \quad \hat{L}_z Y_l^m = \hbar m\,Y_l^m$$

$l = 0,1,2,\ldots$（轨道角动量量子数），$m = -l,\ldots,+l$（磁量子数）。

### 3.2 氢原子能级

Coulomb 势 $V(r) = -e^2/(4\pi\varepsilon_0 r)$。径向方程解出能级**只依赖主量子数 $n$**（而非 $l$）：

$$\boxed{E_n = -\frac{13.6\ \text{eV}}{n^2}, \quad n = 1,2,3,\ldots}$$

这是 Coulomb 势的「偶然简并」（与 $SO(4)$ 隐藏对称性 / Runge–Lenz 矢量有关）。波函数 $\psi_{nlm}$，玻尔半径 $a_0 = 0.529$ Å。

轨道记号：$1s, 2s, 2p, 3s, 3p, 3d, \ldots$（$l=0,1,2,3 \to s,p,d,f$）。这是化学元素周期表的量子力学根基。

### 3.3 自旋与 Pauli 原理

电子有**内禀自旋** $s = 1/2$（非经典「自转」！），自旋算符 $\hat{S}_i$ 满足 $[\hat{S}_i, \hat{S}_j] = i\hbar\varepsilon_{ijk}\hat{S}_k$，本征值 $m_s = \pm 1/2$。

用 **Pauli 矩阵**表示（$\sigma_i$）：

$$\sigma_x = \begin{pmatrix}0&1\\1&0\end{pmatrix}, \quad \sigma_y = \begin{pmatrix}0&-i\\i&0\end{pmatrix}, \quad \sigma_z = \begin{pmatrix}1&0\\0&-1\end{pmatrix}$$

$\hat{S}_i = \frac{\hbar}{2}\sigma_i$。自旋是两分量旋量（spinor），与轨道角动量耦合（$\vec{J} = \vec{L} + \vec{S}$）。

**Pauli 不相容原理**：费米子（半整数自旋）的全同多体波函数必须**反对称** $\Rightarrow$ 两个电子不能占据同一量子态（含自旋）。这是化学键和固体物理的全部基础。

---

## 4. 角動量合成と表現論（Angular Momentum Addition）

### 4.1 Clebsch–Gordan 系数

两个角动量 $\vec{J} = \vec{J}_1 + \vec{J}_2$，量子数 $j$ 取 $|j_1 - j_2|, |j_1-j_2|+1, \ldots, j_1+j_2$，每个 $j$ 有 $m = -j,\ldots,j$。耦合态与非耦合态的变换：

$$|j,m\rangle = \sum_{m_1,m_2} C^{jm}_{j_1 m_1, j_2 m_2}|j_1 m_1\rangle|j_2 m_2\rangle$$

$C$ 是 **Clebsch–Gordan 系数**。例：两个自旋-1/2 $\Rightarrow$ $j=1$（三重态，对称）和 $j=0$（单态，反对称）。

### 4.2 自旋-轨道耦合

氢原子精细结构：$\vec{L}\cdot\vec{S}$ 耦合分裂能级。$\vec{J} = \vec{L} + \vec{S}$ 是好量子数。这是原子光谱学的核心。

---

## 5. 微擾理論（Perturbation Theory）

### 5.1 非简并时间无关微扰

Hamilton 量 $\hat{H} = \hat{H}_0 + \lambda\hat{H}'$，$\hat{H}_0$ 已解（$E_n^{(0)}, |n^{(0)}\rangle$）。能量修正（设非简并）：

$$E_n \approx E_n^{(0)} + \lambda\langle n^{(0)}|\hat{H}'|n^{(0)}\rangle + \lambda^2\sum_{k\neq n}\frac{|\langle k^{(0)}|\hat{H}'|n^{(0)}\rangle|^2}{E_n^{(0)}-E_k^{(0)}} + \cdots$$

一级、二级能量修正。态矢量的一级修正类似。

### 5.2 简并微扰（Stark 效应）

简并能级需先在简并子空间内对角化 $\hat{H}'$ 的矩阵元，得到修正后的「正确零级态」。氢原子 Stark 效应（外加电场分裂能级）是经典例子——线性 Stark 效应只在 $n=2$ 出现（简并）。

### 5.3 含时微扰与 Fermi 黄金规则

含时微扰 $\hat{H}'(t)$ 导致能级间跃迁。$t\to\infty$ 时**跃迁速率**：

$$\boxed{\Gamma_{i\to f} = \frac{2\pi}{\hbar}|\langle f|\hat{H}'|i\rangle|^2 \rho(E_f)}$$

$\rho(E_f)$ 是末态密度。这是激光、辐射、散射、半导体器件的理论根基。

---

## 6. Python 数值验证

### 6.1 无限势阱的零点能与概率分布

```python
# infinite_well.py —— 无限势阱能级与波函数（解析 + 数值对照）
import numpy as np
hbar, m, a = 1.0, 1.0, 1.0
print("无限深方势阱 E_n = n²π²ℏ²/(2ma²):")
for n in [1,2,3,4,5]:
    En = n**2*np.pi**2*hbar**2/(2*m*a**2)
    print(f"  n={n}: E={En:.4f}  (零点能 E1={np.pi**2/(2*m*a**2):.4f})")
print(f"\n经典粒子 E_min=0，量子 E_min={np.pi**2/(2*m*a**2):.3f} > 0 ← 零点能")
```

### 6.2 量子谐振子（数值解 TISE + 阶梯算符验证）

```python
# qho.py —— 用有限差分数值解谐振子，验证 E_n=ℏω(n+1/2)
import numpy as np
m, omega, hbar = 1.0, 1.0, 1.0
N = 1000
x = np.linspace(-6, 6, N)
dx = x[1]-x[0]
# 动能算符（二阶差分矩阵）
T = -(hbar**2/(2*m)) * (np.diag(-2*np.ones(N)) + np.diag(np.ones(N-1),1) + np.diag(np.ones(N-1),-1))/dx**2
V = np.diag(0.5*m*omega**2*x**2)
H = T + V
E, psi = np.linalg.eigh(H)
print("谐振子能级（数值 vs 理论 ℏω(n+1/2)）:")
for n in range(5):
    E_th = hbar*omega*(n+0.5)
    print(f"  n={n}: 数值 E={E[n]:.4f}  理论 {E_th:.4f}  误差 {abs(E[n]-E_th):.2e}")
```

### 6.3 势垒隧穿（WKB 指数衰减）

```python
# tunneling.py —— 验证隧穿透射率 T≈exp(-2κa)
import numpy as np
hbar = 1.055e-34
m, V0, E = 9.11e-31, 5e-19, 1e-19   # 电子, 垒高5eV, 能量1eV
for a_nm in [0.1, 0.3, 0.5, 1.0, 2.0]:
    a = a_nm*1e-9
    kappa = np.sqrt(2*m*(V0-E))/hbar
    T = np.exp(-2*kappa*a)
    print(f"垒宽 {a_nm:.1f}nm: κ={kappa:.2e}/m  T={T:.2e}")
print("\n→ 隧穿率随垒宽指数下降，这是 STM 的灵敏度来源")
```

### 6.4 氢原子波函数（径向概率分布可视化数据）

```python
# hydrogen_radial.py —— 氢原子径向概率密度 P(r)=r²|R_nl|²
import numpy as np
from math import factorial, exp
a0 = 1.0  # 玻尔半径（原子单位）
def R10(r):  # 1s
    return 2*np.exp(-r/a0)/a0**1.5
def R20(r):  # 2s
    return (1/(2*np.sqrt(2)))*(2 - r/a0)*np.exp(-r/(2*a0))/a0**1.5
def R21(r):  # 2p
    return (1/(2*np.sqrt(6)))*(r/a0)*np.exp(-r/(2*a0))/a0**1.5
r = np.linspace(0.01, 10, 500)
for label, R in [("1s",R10),("2s",R20),("2p",R21)]:
    P = r**2 * R(r)**2
    rmax = r[np.argmax(P)]
    print(f"{label}: 径向概率峰位 r_max/a0 = {rmax:.2f}  (1s理论=1.0, 2s≈5.24)")
```

### 6.5 自旋-1/2 与 Pauli 矩阵对易关系

```python
# spin_pauli.py —— 验证 Pauli 矩阵对易子与 [σi,σj]=2iεijk σk
import numpy as np
sx = np.array([[0,1],[1,0]])
sy = np.array([[0,-1j],[1j,0]])
sz = np.array([[1,0],[0,-1]])
print("[σx,σy] =", sx@sy - sy@sx, " 应=2iσz =", 2j*sz)
print("[σy,σz] =", sy@sz - sz@sy, " 应=2iσx =", 2j*sx)
print("[σz,σx] =", sz@sx - sx@sz, " 应=2iσy =", 2j*sy)
# 自旋向上/向下本征态
print("σz 本征态 ↑=", [1,0], " 本征值 +1")
print("σz 本征态 ↓=", [0,1], " 本征值 -1")
# 两自旋合成：单态 vs 三重态维度
print(f"\n两个 spin-1/2: 维度 2×2=4 = 三重态(3)+单态(1)")
```

---

## 7. 東大特色：Dirac 記号と朝永の遺産

東大量子力学 B（Sakurai）的特色是用 **Dirac bra-ket 记号**贯穿：
- 态 $|\psi\rangle$（ket）、对偶 $\langle\phi|$（bra）、内积 $\langle\phi|\psi\rangle$（复数）。
- 投影算符 $|n\rangle\langle n|$、单位分解 $\hat{1} = \sum_n|n\rangle\langle n|$。
- 表象变换 = 幺正算符；对称性 = 幺正/反幺正算符（Wigner 定理）。

这套抽象语言是**量子场论的门票**。朝永振一郎的 QED 重整化（1965 诺贝尔奖）、湯川秀树的介子理论（1949）、小林誠与益川敏英的 CP 破坏（CKM 矩阵，2008 诺贝尔奖）——全部建立在 Sakurai 式的算符代数之上。

> **東大物理血脉**：湯川（1949，介子）→ 朝永（1965，QED）→ 小林・益川（2008，弱相互作用 CP 破坏）→ 梶田（2015，中微子振荡）。这条线从量子力学 A/B 出发，经量子场论到粒子物理标准模型。本课是它的起点。

---

## 8. 習題集

**习题 1（★）**　电子被限制在 $a = 1$ Å 的无限势阱中。求（a）基态能量（eV）；（b）从 $n=2\to1$ 跃迁的光子波长。
> *答案*：(a) $E_1 = \pi^2\hbar^2/(2ma^2) \approx 37.6$ eV；(b) $\lambda = hc/(E_2-E_1) \approx 33$ nm（紫外）。

**习题 2（★★）**　用阶梯算符证明量子谐振子基态满足最小不确定性 $\sigma_x\sigma_p = \hbar/2$（相干态性质）。
> *提示*：基态 $|0\rangle$ 满足 $\hat{a}|0\rangle=0$，即 $(\hat{x} + i\hat{p}/m\omega)|0\rangle = 0$，推得 $\langle xp\rangle$ 关系。

**习题 3（★）**　氢原子从 $n=3$ 跃迁到 $n=2$（Balmer 系 Hα 线），求光子波长，与实验值 656.3 nm 比较。
> *答案*：$\Delta E = 13.6(1/4 - 1/9) = 1.89$ eV，$\lambda = 1240/1.89 \approx 656$ nm ✓。

**习题 4（★★）**　两个自旋-1/2 粒子，Hamilton 量 $\hat{H} = A\,\hat{\vec{S}}_1\cdot\hat{\vec{S}}_2$。求能量本征值，并说明三重态/单态的分裂。
> *答案*：$\vec{S}_1\cdot\vec{S}_2 = \frac{1}{2}(S^2 - S_1^2 - S_2^2)$。三重态（$S=1$）$E = A\hbar^2/4$；单态（$S=0$）$E = -3A\hbar^2/4$。这是氢原子超精细结构（21 cm 线）的模型。

**习题 5（★）**　一维无限势阱受微扰 $\hat{H}' = V_0\sin(\pi x/a)$。求基态能量的一级修正。
> *答案*：$\Delta E_1^{(1)} = V_0\langle 1|\sin(\pi x/a)|1\rangle = \frac{2V_0}{a}\int_0^a\sin^3(\pi x/a)dx = \frac{8V_0}{3\pi}$。

**习题 6（★★）**　用 Fermi 黄金规则推导：原子在频率 $\omega$ 的电磁波中从 $|i\rangle$ 跃迁到 $|f\rangle$（$E_f > E_i$）的吸收速率正比于 $|\langle f|\hat{x}|i\rangle|^2$（电偶极近似）。
> *提示*：$\hat{H}' = -eE_0\hat{x}\cos\omega t$，矩阵元 $\langle f|\hat{H}'|i\rangle = -eE_0\langle f|\hat{x}|i\rangle/2$，代入 $\Gamma = \frac{2\pi}{\hbar}|\cdot|^2\rho$。

---

## 9. 参考文献

1. Griffiths, Darrell F. & Schroeter. *Introduction to Quantum Mechanics* 3ed. Cambridge, 2018.（東大量子力学 A 指定，日文译本）
2. Sakurai, Napolitano. *Modern Quantum Mechanics* 3ed. Cambridge, 2020.（東大量子力学 B 指定，Dirac 符号贯穿）
3. Cohen-Tannoudji, Diu, Laloë. *Quantum Mechanics* Vol 1/2. Wiley.（最详尽，参考查表）
4. Shankar. *Principles of Quantum Mechanics* 2ed. Springer.（公理体系讲得清楚）
5. Landau, Lifshitz. *Quantum Mechanics: Non-Relativistic Theory* Vol 3.（俄系，简洁深刻）
6. 砂川重信. 『量子力学』（岩波書店）——東大推荐桥梁教材，从波函数到算符过渡平滑。
7. 小出昭一郎. 『量子力学』（裳華房）——東大经典本土教材，习题丰富。

---

**完成日期**：2026-08-12　|　**对应 SURVEY §9 東大**：量子力学 A/B

---

## 🎯 费曼式入口（白话版）

> **一句话解释**：量子力学告诉你，世界在最底层不是「小球轨道」，而是「概率云的演化」——粒子没有确定的位置，只有测量时才「掷骰子」塌缩到一个值。Einstein 不信这套，说「上帝不掷骰子」，Bohr 回敬「别告诉上帝怎么做」。
>
> **生活类比**：经典世界像台球——你看见球在哪、知道速度，就能精确预测下一秒。量子世界像「旋转的硬币」——你说不清它是正面还是反面，直到它「啪」地落在桌上（测量）。更怪：硬币在空中同时是正反两种状态的叠加（Schrödinger 猫），一观察就只剩一种。
>
> **反直觉发现**：
> - **零点能**：把电子关在盒子里（无限势阱），它最低能量 $E_1 > 0$，永远不能静止。原因：位置被束缚 $\Delta x$ 小 → 动量不确定性 $\Delta p \geq \hbar/(2\Delta x)$ 大 → 动能不能为零。**「不确定性」不是测量技术差，是自然界的根本属性**。
> - **隧穿**：电子遇到能量比它高的墙，经典会 100% 反弹；量子有非零概率「穿墙」。你的 USB 闪存（量子隧穿闪存）、STM 显微镜（看单个原子）、太阳核聚变（质子克服 Coulomb 势垒）都靠它。
> - **波函数「坍缩」是非局域的**：测量一个纠缠对的一个粒子，另一个（哪怕在月球上）瞬间「决定」自己的状态。Einstein 称之为「鬼魅般的超距作用」，但 Bell 不等式实验（2022 诺奖 Aspect/Ferry/Zeilinger）证明量子纠缠是真的。

---

## 🔗 衔接：从哪来，到哪去

### 前置
- **力学**：Hamilton 量、Poisson 括号、作用量、简谐振子（量子谐振子的经典前身）。
- **EM**：平面波、偏振、Coulomb 势（氢原子）。
- **数学**：线性代数（本征值/本征矢、Hermite/幺正矩阵）、复变、Fourier 变换、PDE（Schrödinger 方程）。

### 本课解决了什么危机
- **黑体辐射紫外灾难（1900）**：经典 Maxwell+统计推出「黑体辐射能量随频率发散」（每个模式 $k_BT$，无穷多模式）。**Planck 量子化**：能量 $E = nh\nu$ 一份一份。**Einstein 光量子（1905）**：光电效应解释。
- **原子稳定性危机**：经典电子绕核辐射电磁波 1 纳秒内坠入原子核。**Bohr 模型（1913）**：分立轨道，不辐射。**de Broglie 物质波（1924）→ Schrödinger 方程（1926）**：彻底解决。

### 本课留下的新危机（通往下一站）
- **Schrödinger 方程与相对论不兼容** $\to$ **Klein-Gordon / Dirac 方程** → 量子场论。Dirac 方程预言反物质（正电子 1932 被发现）。
- **测量问题**：波函数坍缩的机制是什么？**多世界诠释 vs 哥本哈根 vs 退相干**——至今哲学+物理争议。
- **量子与引力的统一**：黑洞 Hawking 辐射把两者硬碰硬，但量子化 Einstein 引力不可重整化 → **弦理论 / 圈量子引力**。

### 后续（東大路径）
| 方向 | 课程 | 用到本课什么 |
|------|------|-------------|
| 量子场论 | 素粒子 | 升降算符 → 粒子产生湮灭、Dirac 方程 |
| 凝聚态 | 物性 | Bloch 定理、能带、超导 BCS |
| 量子信息 | 选修/前沿 | 纠缠、Bell 不等式、量子算法 |
| 量子化学 | 化学/物性 | 氢原子轨道、Hartree-Fock、DFT |
| 原子分子光物理 | AMO | 激光冷却、光镊、BEC |

---

## 🏭 理论联系实际：5 个应用

1. **半导体与晶体管**：能带论（量子力学 + 周期势）→ 半导体物理 → MOSFET → CPU/GPU。你正在读这页文字就是量子力学的应用。東大半导体的传统（SONY 的江崎 Leo Esaki 1973 诺奖，隧道二极管）正是隧穿效应的应用。
2. **激光与 LED**：受激辐射（Einstein 1917 提出）+ 占据数反转 = 激光（1960 Maiman）。中村修二（2014 诺奖，蓝光 LED）的发明彻底改变照明——LED 的核心是量子阱能级工程。
3. **量子计算（2020s 大爆发）**：IBM（127+ qubits）、Google（Sycamore 量子优越性 2019）、IBM Heron r2（2024）、超导/离子阱/光量子多种路线。東京大学 2024 年成立「量子創薬センター」，IBM Quantum One 落地东大 IIS。
4. **磁共振（MRI/NMR）**：核自旋在外磁场中 Zeeman 分裂，射频脉冲翻转，弛豫释放信号。Bloch（1946）方程描述。东京大学医学部 + 物理所的 MRI 技术全球领先。
5. **GPS 中的原子钟**：铯原子基态超精细跃迁（9.2 GHz）定义「秒」。GPS 卫星上的原子钟精度 $10^{-13}$，没有它 GPS 误差每天 10 公里。量子力学的精细结构理论直接给出跃迁频率。

---

## 🔬 最新研究前沿（2024-2026）

- **量子纠错跨越「盈亏平衡」（2024–2025）**：Google Sycamore + 表面码 7→实现 logical qubit 寿命 > physical qubit（2024 Nature）；Quantinuum H2 离子阱用「魔术态蒸馏」做出首个容错逻辑比特（2024–2025）。这是通用量子计算的关键里程碑。
- **中性原子阵列量子计算崛起（2024–2026）**：Atom Computing（1180 原子）、QuEra、PASQAL 用光镊夹住原子阵列做量子模拟。東京大学 Takashi Takano 组、京都大亦有原子阵列平台。
- **超导量子比特记录刷新**：IBM Condor（1121 qubits, 2023），Heron r2（156 qubit, 2024）解决串扰；中国「九章 3 号」光量子（2024）模拟玻色采样速度超过经典超算 $10^{15}$ 倍。
- **量子机器学习与量子化学**：用变分量子本征解（VQE）计算分子基态能——2025 年首次在真实硬件上模拟 FeMoCo（固氮酶核心），可能彻底改变合成氨工业（节能 Haber-Bosch）。
- **拓扑量子计算**：Microsoft 的马约拉纳费米子路线（2023–2025 争议中进展）；東大 Kavli IPMU 的中村荣一/Kitano 等在拓扑物态/量子计算交叉持续产出。

---

## 🗺️ 学习 Roadmap（Tokyo 路径）

```
现代物理（2 年级， moderna physics 入门）
  ↓ 黑体辐射、光电效应、Bohr 模型、de Broglie 波
量子力学 A（3 年级， Griffiths）
  ↓ 核心关卡 ↓
  ├─ Schrödinger 方程 + 一维问题（阱、谐振子、势垒）
  ├─ 三维 + 氢原子 + 角动量 + 自旋
  ├─ 微扰论（定态 + 含时 + Fermi 黄金规则）
  └─ 全同粒子 + Pauli 原理（通往多体）
量子力学 B（4 年级/研究生， Sakurai）
  ↓ Dirac 符号 + 幺正变换 + 对称性
  ├─ 角动量合成 + CG 系数 + Wigner-Eckart
  ├─ 散射理论 + 分波分析
  └─ 路径积分（Feynman 诠释）
研究生进阶
  ├─ 量子场论（Peskin & Schroeder，朝永遗产）
  ├─ 多体物理（凝聚态，Fetter-Walecka）
  └─ 量子信息（Nielsen-Chuang，东大量子创新 initiative）
```

**知识检查**：
- [ ] 能解释「为什么无限势阱基态能量 $E_1 > 0$」（不确定性原理）。
- [ ] 能用升降算符推导谐振子能级 $E_n = \hbar\omega(n+1/2)$，并理解为什么这是 QFT 的种子。
- [ ] 能写出氢原子轨道（1s/2s/2p）波函数并说出对应量子数 $(n,l,m)$。
- [ ] 能解释 Pauli 不相容原理如何从「费米子波函数反对称」推出，并说明它如何决定元素周期表。
- [ ] 能用 Fermi 黄金规则推出光吸收速率 $\Gamma \propto |\langle f|\hat{x}|i\rangle|^2$（电偶极近似）。
- [ ] 理解 Bell 不等式为什么说明「隐变量」理论失败，量子纠缠是真实现象。
