# Topic 04 · 统计物理与热力学（MIT 8.044 / 8.08）

> **教材**：Schroeder《Introduction to Thermal Physics》+ Reif《Fundamentals of Statistical and Thermal Physics》
>
> **覆盖课程**：
> - **8.044** Statistical Physics I（Schroeder：热力学四定律 + 微正则/正则系综）
> - **8.08** Statistical Physics II（Reif：巨正则、量子统计、相变）
>
> **宪法**：直觉 → 公式 → 代码(bash 跑通) → 不足 → 应用

---

## 目录

1. [热力学四定律](#1-热力学四定律)
2. [熵与信息](#2-熵与信息)
3. [系综理论](#3-系综理论)
4. [配分函数与可观察量](#4-配分函数与可观察量)
5. [量子统计：玻色子与费米子](#5-量子统计)
6. [相变](#6-相变)
7. [Python 代码演示](#7-python-代码演示)
8. [习题与解答](#8-习题与解答)
9. [反直觉发现](#9-反直觉发现)
10. [不足与延伸](#10-不足与延伸)

---

## 1. 热力学四定律

### 1.1 第零定律（热平衡的传递性）

若 $A$ 与 $B$ 热平衡，$B$ 与 $C$ 热平衡，则 $A$ 与 $C$ 热平衡。

→ 存在**温度** $T$ 这个态函数。这是温度计能工作的逻辑基础。

### 1.2 第一定律（能量守恒）

$$
\boxed{\Delta U = Q - W}
$$

内能变化 = 系统吸热 − 系统对外做功。

微分形式：$dU = \delta Q - \delta W$。对可逆过程，$\delta W = P\,dV$，$\delta Q = T\,dS$：

$$
dU = T\,dS - P\,dV
$$

### 1.3 第二定律（熵增）

孤立系统的熵不减：

$$
\Delta S_{\text{isolated}} \ge 0
$$

等号仅当可逆过程。这给出**时间箭头**——宏观不可逆的来源。

**Clausius 不等式**：$\oint \frac{\delta Q}{T} \le 0$。

### 1.4 第三定律（绝对零度不可达）

$$
\lim_{T\to 0} S = S_0 \text{（常数，对理想晶体 } S_0 = 0\text{）}
$$

绝对零度不可在有限步操作达到。这是 Nernst 热定理。

### 1.5 热力学势

| 势 | 定义 | 微分 | 自然变量 |
|----|------|------|---------|
| 内能 $U$ | — | $dU = TdS - PdV$ | $S, V$ |
| 焓 $H$ | $H = U + PV$ | $dH = TdS + VdP$ | $S, P$ |
| 自由能 $F$ | $F = U - TS$ | $dF = -SdT - PdV$ | $T, V$ |
| Gibbs $G$ | $G = U + PV - TS$ | $dG = -SdT + VdP$ | $T, P$ |

- **$F$** 最小化给出等温等容下的平衡（封闭系统常用）。
- **$G$** 最小化给出等温等压下的平衡（化学反应常用）。
- 化学势 $\mu = \left(\frac{\partial G}{\partial N}\right)_{T,P}$。

---

## 2. 熵与信息

### 2.1 玻尔兹曼熵

$$
\boxed{S = k_B \ln \Omega}
$$

$\Omega$ 是与宏观态相容的微观态数。这刻在维也纳中央公墓玻尔兹纳墓碑上——统计力学的核心方程。

### 2.2 吉布斯熵（一般化）

对处于概率分布 $\{p_i\}$ 的系统：

$$
S = -k_B \sum_i p_i \ln p_i
$$

玻尔兹曼熵是 $p_i = 1/\Omega$（微正则系综均匀分布）的特例。

### 2.3 熵与信息

Shannon 信息熵 $H = -\sum p_i \log_2 p_i$ 与吉布斯熵结构完全相同（差一个 $k_B\ln 2$ 系数）。

**物理意义**：熵 = 我们对系统微观态的"无知程度"。信息获取（测量）必然减少熵——Landauer 原理：擦除 1 bit 信息至少耗散 $k_B T\ln 2$ 热量。

### 2.4 微观状态数计算

理想气体 $N$ 个粒子、体积 $V$、能量 $E$，微观状态数：

$$
\Omega(E, V, N) = \frac{1}{N!h^{3N}}\cdot\frac{(2\pi m E)^{3N/2}}{(3N/2)!}\cdot V^N
$$

用 Stirling 公式 $\ln N! \approx N\ln N - N$ 得 Sakur-Tetrode 熵公式：

$$
S = Nk_B\left[\ln\left(\frac{V}{N}\left(\frac{4\pi m E}{3Nh^2}\right)^{3/2}\right) + \frac{5}{2}\right]
$$

由此推导理想气体状态方程 $PV = Nk_B T$。

---

## 3. 系综理论

### 3.1 微正则系综（NVE）

**孤立系统**：$N, V, E$ 固定，所有 $\Omega$ 个可达微观态**等概率** $p_i = 1/\Omega$。

温度：$\frac{1}{T} = \left(\frac{\partial S}{\partial E}\right)_{V,N} = k_B\frac{\partial\ln\Omega}{\partial E}$。

### 3.2 正则系综（NVT）

**与热浴接触**：$N, V, T$ 固定，能量可变。系统在微观态 $i$（能量 $E_i$）的概率：

$$
p_i = \frac{e^{-\beta E_i}}{Z}, \qquad \beta = \frac{1}{k_B T}
$$

**配分函数**：

$$
\boxed{Z = \sum_i e^{-\beta E_i} \quad \text{(离散)} \qquad Z = \int dE\, \rho(E) e^{-\beta E} \quad \text{(连续)}}
$$

### 3.3 巨正则系综（$\mu$VT）

**与粒子源 + 热浴接触**：$\mu, V, T$ 固定，$N$、$E$ 都可变。

$$
p_{N,i} = \frac{e^{-\beta(E_i - \mu N)}}{\mathcal{Z}}
$$

**巨配分函数**：

$$
\mathcal{Z} = \sum_N \sum_i e^{-\beta(E_i - \mu N)} = \sum_N z^N Z_N, \qquad z = e^{\beta\mu}\text{（逸度）}
$$

平均粒子数 $\langle N\rangle = \frac{1}{\beta}\frac{\partial\ln\mathcal{Z}}{\partial\mu}$。

### 3.4 三种系综的等价性

在**热力学极限**（$N\to\infty, V\to\infty$, $N/V$ 固定）下，三种系综给出相同的热力学量。差异只在涨落：

| 系综 | 固定 | 能量涨落 | 粒子数涨落 |
|------|------|---------|-----------|
| 微正则 | $E$ | 0 | 0 |
| 正则 | $T$ | $\Delta E^2 = k_BT^2 C_V$ | 0 |
| 巨正则 | $\mu, T$ | 大 | $\Delta N^2 = k_BT(\partial\langle N\rangle/\partial\mu)_T$ |

在**相变临界点**附近，涨落发散，三种系综可能给出不同结果——需谨慎选择。

---

## 4. 配分函数与可观察量

正则配分函数 $Z$ 是**生成函数**，所有热力学量从中导出：

| 量 | 公式 |
|----|------|
| 自由能 | $F = -k_BT\ln Z$ |
| 熵 | $S = -\left(\frac{\partial F}{\partial T}\right)_V = k_B(\ln Z + \beta\langle E\rangle)$ |
| 内能 | $U = \langle E\rangle = -\frac{\partial\ln Z}{\partial\beta}$ |
| 热容 | $C_V = \left(\frac{\partial U}{\partial T}\right)_V = \frac{(\Delta E)^2}{k_BT^2}$ |
| 压强 | $P = -\left(\frac{\partial F}{\partial V}\right)_T = k_BT\left(\frac{\partial\ln Z}{\partial V}\right)_T$ |
| 化学势 | $\mu = -k_BT\left(\frac{\partial\ln Z}{\partial N}\right)_{T,V}$ |

**涨落-响应关系**：$C_V = (\Delta E)^2/(k_BT^2)$——能量涨落正比于热容。同理磁化率正比于磁化涨落、压缩率正比于密度涨落。这是统计力学的"中心法则"。

### 例：经典理想气体

$$
Z_1 = \frac{1}{h^3}\int d^3r\, d^3p\, e^{-\beta p^2/2m} = \frac{V}{h^3}(2\pi m k_BT)^{3/2}
$$

$N$ 个**可分辨**粒子 $Z_N = Z_1^N$，**全同**粒子 $Z_N = Z_1^N/N!$（吉布斯因子）。

由此 $F = -Nk_BT[\ln(V/N\lambda^3) + 1]$（$\lambda = h/\sqrt{2\pi m k_BT}$ 是热德布罗意波长），推出 $PV = Nk_BT$、$U = \frac{3}{2}Nk_BT$、$C_V = \frac{3}{2}Nk_B$。

---

## 5. 量子统计

### 5.1 平均占据数

对单粒子能级 $\epsilon$，求平均占据数 $n$。统计权重 $w_n$：

| 类型 | 占据数 $n$ | 权重 $w_n$ | 平均 $\bar{n}$ |
|------|-----------|-----------|--------------|
| 玻色子 | $0, 1, 2, \dots$ | $\sum_{n=0}^\infty e^{-\beta n(\epsilon-\mu)} = \frac{1}{1-e^{-\beta(\epsilon-\mu)}}$ | $\frac{1}{e^{\beta(\epsilon-\mu)}-1}$ |
| 费米子 | $0, 1$ | $1 + e^{-\beta(\epsilon-\mu)}$ | $\frac{1}{e^{\beta(\epsilon-\mu)}+1}$ |
| 经典（玻尔兹曼） | (近似稀薄) | $e^{-\beta(\epsilon-\mu)}$ | $e^{-\beta(\epsilon-\mu)}$ |

### 5.2 三大分布

**玻色-爱因斯坦分布**（整数自旋，玻色子）：

$$
\boxed{\bar{n}_{BE}(\epsilon) = \frac{1}{e^{\beta(\epsilon-\mu)} - 1}}
$$

**费米-狄拉克分布**（半整数自旋，费米子）：

$$
\boxed{\bar{n}_{FD}(\epsilon) = \frac{1}{e^{\beta(\epsilon-\mu)} + 1}}
$$

**麦克斯韦-玻尔兹曼分布**（经典极限 $\bar{n} \ll 1$）：

$$
\bar{n}_{MB}(\epsilon) = e^{-\beta(\epsilon-\mu)}
$$

**经典极限条件**：相邻能级间距 $\gg k_BT$，即 $\bar{n}\ll 1$——温度高、密度低、粒子质量大。

### 5.3 化学势的物理意义

- **$\mu < 0$**（玻色子）：保证 $\bar{n}$ 分母不为零。
- **$T\to 0$ 玻色子**：$\mu \to 0^-$（基态能量），大量粒子凝聚到基态——玻色-爱因斯坦凝聚（BEC）。
- **$T\to 0$ 费米子**：$\mu \to E_F$（费米能），所有 $\epsilon < E_F$ 态占满，$\epsilon > E_F$ 态空——费米海。

### 5.4 黑体辐射（光子气体）

光子是玻色子，化学势 $\mu = 0$（光子数不守恒）。能量密度（Planck 分布）：

$$
u(\nu) = \frac{8\pi h\nu^3}{c^3}\cdot\frac{1}{e^{h\nu/k_BT} - 1}
$$

积分总能量 $U = aT^4$（Stefan-Boltzmann），$a = \pi^2 k_B^4/(15\hbar^3 c^3)$。

低频极限 $h\nu\ll k_BT$ 退化为 **Rayleigh-Jeans** $u \propto \nu^2 T$（紫外灾难！）。
高频极限 $h\nu\gg k_BT$ 退化为 **Wien** $u\propto \nu^3 e^{-h\nu/k_BT}$。

Planck 公式是量子力学诞生的起点。

---

## 6. 相变

### 6.1 相变的分类（Ehrenfest）

- **一级相变**：自由能一阶导（熵 $S$、体积 $V$）不连续。如冰→水（潜热）。
- **二级相变**：一阶导连续，二阶导（热容、压缩率、磁化率）发散或不连续。如铁磁 Curie 点、超导转变、液氦 $\lambda$ 点。

### 6.2 序参量

**序参量** $m$：低温有序相 $m\neq 0$，高温无序相 $m = 0$。

- 铁磁：磁化强度 $M$
- 气液临界点：$\rho_l - \rho_g$
- 超流：复序参量 $\psi = |\psi|e^{i\phi}$

### 6.3 临界指数

在临界温度 $T_c$ 附近，物理量按幂律发散：

$$
|m| \sim |T - T_c|^\beta, \quad \chi \sim |T-T_c|^{-\gamma}, \quad C \sim |T-T_c|^{-\alpha}, \quad \xi \sim |T-T_c|^{-\nu}
$$

其中 $\xi$ 是**关联长度**——临界点附近涨落的相关尺度发散。

### 6.4 平均场理论（van der Waals / Weiss）

最简单的近似：忽略涨落，每个粒子只感受到"平均场"。

- van der Waals 气体：$(P + a/V_m^2)(V_m - b) = RT$，临界点 $(P_c, V_c, T_c)$ 满足 $\partial P/\partial V|_T = \partial^2 P/\partial V^2|_T = 0$。
- Weiss 铁磁：$m = \tanh(\beta J z m)$（$z$ 配位数）。

**临界指数（平均场）**：$\beta = 1/2, \gamma = 1, \alpha = 0, \nu = 1/2$——与实际三维值（如 Ising $\beta\approx 0.326$）不符，因为忽略了涨落。

### 6.5 Ising 模型

最简单且非平凡的相变模型。自旋 $s_i = \pm 1$ 在格点上，哈密顿：

$$
\hat{H} = -J\sum_{\langle ij\rangle} s_i s_j - h\sum_i s_i
$$

- 一维 Ising：**无相变**（任意 $T>0$ 都是顺磁）。
- 二维 Ising（Onsager 1944）：$T_c = 2J/(k_B\ln(1+\sqrt{2}))$，自发磁化 $m\sim (T_c-T)^{1/8}$（精确临界指数 $\beta=1/8$）。
- 三维 Ising：无精确解，数值给出 $\beta\approx 0.326$。

**普适性**：相距很远的物理系统（液气、Ising、合金有序化）在临界点附近有**相同的临界指数**——只依赖维度和序参量分量数。这是 Wilson 重整化群（RG）的伟大成就。

---

## 7. Python 代码演示

### 7.1 麦克斯韦-玻尔兹曼速度分布

```python
"""
麦克斯韦-玻尔兹曼速度分布（不同温度）
"""
import numpy as np
import matplotlib.pyplot as plt

# 归一化 m/kB = 1，速度单位为 (kT/m)^{1/2}
v = np.linspace(0, 6, 500)
def mb(v, T):
    return 4*np.pi*v**2 * (1/(2*np.pi*T))**1.5 * np.exp(-v**2/(2*T))

fig, ax = plt.subplots(figsize=(9, 6))
for T in [0.5, 1.0, 2.0, 4.0]:
    ax.plot(v, mb(v, T), label=f'T={T}')
ax.set_xlabel('速度 v'); ax.set_ylabel('P(v)')
ax.set_title('麦克斯韦-玻尔兹曼速度分布：升温→峰值右移+变宽')
ax.legend(); ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig('maxwell_boltzmann.png', dpi=110, bbox_inches='tight')
print("已保存 maxwell_boltzmann.png")
print("最概然速率 v_p = sqrt(2kT/m), 平均 <v> = sqrt(8kT/πm), 方均根 = sqrt(3kT/m)")
print("关系: v_p : <v> : v_rms = 1 : 1.128 : 1.225")
```

### 7.2 费米-狄拉克 vs 玻色-爱因斯坦分布对比

```python
"""
三大分布对比: BE, FD, MB
"""
import numpy as np
import matplotlib.pyplot as plt

eps = np.linspace(-3, 8, 500)
mu = 0.0

fig, ax = plt.subplots(figsize=(10, 6))
for T_label, beta in [('T=0.2 (低温)', 5.0), ('T=1.0', 1.0), ('T=3.0 (高温)', 0.333)]:
    n_BE = 1.0 / (np.exp(beta*(eps - mu)) - 1)
    n_FD = 1.0 / (np.exp(beta*(eps - mu)) + 1)
    n_MB = np.exp(-beta*(eps - mu))
    n_BE[n_BE < 0] = np.nan  # 排除 ε < μ 玻色子无定义区
    ax.plot(eps, n_FD, label=f'FD {T_label}', linewidth=1.5)
    ax.plot(eps, n_BE, '--', label=f'BE {T_label}', linewidth=1.5)
ax.set_ylim(-0.2, 5)
ax.set_xlabel('能量 ε − μ'); ax.set_ylabel('平均占据数 n̄(ε)')
ax.set_title('玻色子 vs 费米子分布：低温下 BE 趋向∞（凝聚），FD 趋向阶跃（费米海）')
ax.legend(loc='upper right', fontsize=8); ax.grid(alpha=0.3)
ax.axhline(1, color='gray', linewidth=0.5, linestyle=':')
plt.tight_layout()
plt.savefig('bose_fermi.png', dpi=110, bbox_inches='tight')
print("已保存 bose_fermi.png")
print("低温极限: BE 在 ε→μ⁻ 发散(凝聚), FD 成阶跃(0/1)")
print("高温极限: n̄ ≪ 1, 三种分布趋于一致 (经典极限)")
```

### 7.3 二维 Ising 模型蒙特卡洛（Metropolis 算法）

```python
"""
2D Ising 模型 Metropolis Monte Carlo
观察自发磁化随温度的变化
"""
import numpy as np
import matplotlib.pyplot as plt

def ising_mc(L, T, n_sweeps=5000, n_thermalize=2000):
    """Metropolis 算法模拟 LxL Ising 模型"""
    J = 1.0
    spins = np.random.choice([-1, 1], size=(L, L))
    magnetizations = []

    for sweep in range(n_sweeps):
        for _ in range(L*L):
            i, j = np.random.randint(0, L, 2)
            # 周期边界条件下的邻居和
            nb = (spins[(i+1)%L, j] + spins[(i-1)%L, j] +
                  spins[i, (j+1)%L] + spins[i, (j-1)%L])
            dE = 2*J*spins[i, j]*nb
            if dE < 0 or np.random.random() < np.exp(-dE/T):
                spins[i, j] *= -1
        if sweep >= n_thermalize:
            magnetizations.append(np.abs(np.mean(spins)))

    return np.mean(magnetizations), np.std(magnetizations)

L = 16
T_array = np.linspace(1.0, 4.0, 25)
Tc_exact = 2.0/np.log(1 + np.sqrt(2))  # Onsager 解 ≈ 2.269

mags, errs = [], []
for T in T_array:
    m, e = ising_mc(L, T, n_sweeps=4000, n_thermalize=1500)
    mags.append(m); errs.append(e)
    print(f"T={T:.2f}  m={m:.3f}±{e:.3f}")

fig, ax = plt.subplots(figsize=(9, 6))
ax.errorbar(T_array, mags, yerr=errs, fmt='o-', capsize=3)
ax.axvline(Tc_exact, color='r', linestyle='--', label=f'T_c(Onsager)={Tc_exact:.3f}')
ax.set_xlabel('温度 T (J/k_B)'); ax.set_ylabel('|磁化| ⟨|m|⟩')
ax.set_title(f'2D Ising 模型 (L={L})：自发磁化在 T_c 附近消失')
ax.legend(); ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig('ising.png', dpi=110, bbox_inches='tight')
print(f"\n已保存 ising.png")
print(f"Onsager 精确临界温度 T_c = 2J/(k_B ln(1+√2)) ≈ {Tc_exact:.4f}")
```

---

## 8. 习题与解答

### 习题 1（熵计算）— 气体混合

两个相同容器各装 1 mol 理想气体（同种）温度 $T$，压力 $P$。打开阀门连通，求熵变。

**解**：两份气体相互扩散到 2 倍体积。对每份气体，自由膨胀 $\Delta S = nR\ln(V_f/V_i) = R\ln 2$。

总 $\Delta S = 2R\ln 2 \approx 11.5$ J/K。

**Gibbs 佯谬**：若是同种气体，"扩散"什么都没发生，$\Delta S$ 应该为零——但上述计算给出 $2R\ln 2$。佯谬的解决：粒子全同性导致量子力学修正，相同气体混合熵变确实为零（同位素混合才有 $\Delta S > 0$）。

### 习题 2（热机效率）— 卡诺循环

卡诺热机工作在 $T_H = 600$ K 和 $T_C = 300$ K 之间。求最大效率与 1 kJ 热输入对应的功。

**解**：

$$
\eta_{\max} = 1 - \frac{T_C}{T_H} = 1 - \frac{1}{2} = 50\%
$$

功 $W = \eta Q_H = 500$ J。

这是热力学第二定律给出的上限——任何实际热机效率更低。蒸汽机 $\sim 10\%$，汽车发动机 $\sim 25\%$，联合循环电厂 $\sim 60\%$。

### 习题 3（正则系综）— 二能级系统

二能级系统：基态 $E_0 = 0$，激发态 $E_1 = \epsilon$。求配分函数、内能、熵。

**解**：

$$
Z = 1 + e^{-\beta\epsilon}
$$

$$
U = -\partial_\beta\ln Z = \frac{\epsilon e^{-\beta\epsilon}}{1 + e^{-\beta\epsilon}} = \frac{\epsilon}{e^{\beta\epsilon}+1}
$$

$$
F = -k_BT\ln(1 + e^{-\beta\epsilon})
$$

$$
S = -\left(\frac{\partial F}{\partial T}\right)_V = k_B\left[\ln(1+e^{-\beta\epsilon}) + \frac{\beta\epsilon}{1+e^{\beta\epsilon}}\right]
$$

**极限**：
- $T\to 0$：$U\to 0, S\to 0$（被困在基态）。
- $T\to\infty$：$U\to\epsilon/2$（两态等概率），$S\to k_B\ln 2$（最大信息熵）。
- 熵峰在 $k_BT\sim\epsilon$ 处。

### 习题 4（理想气体）— 配分函数

经典理想气体单粒子配分函数 $Z_1 = V/\lambda^3$（$\lambda = h/\sqrt{2\pi mk_BT}$）。求 $N$ 粒子的内能、压强、化学势。

**解**：全同粒子 $Z_N = Z_1^N/N!$。

$$
F = -k_BT\ln Z_N = -Nk_BT\ln(V/(N\lambda^3)) - Nk_BT
$$

$$
P = -\left(\frac{\partial F}{\partial V}\right)_T = \frac{Nk_BT}{V}
$$

$PV = Nk_BT$ ✓（理想气体状态方程从配分函数自然出现）。

$$
U = -\partial_\beta\ln Z_N = \frac{3N}{2\beta} = \frac{3}{2}Nk_BT
$$

（自由度均分：3 个平动自由度 × $k_BT/2$）。

$$
\mu = \left(\frac{\partial F}{\partial N}\right)_{T,V} = -k_BT\ln\frac{V}{N\lambda^3}
$$

### 习题 5（费米气体）— $T=0$ 电子气

费米能 $E_F$ 的电子气体，求 $T=0$ 时总能量。

**解**：$T=0$ 时所有 $\epsilon < E_F$ 态占满，$\epsilon > E_F$ 态空。态密度 $g(\epsilon) = \frac{V}{2\pi^2}\left(\frac{2m}{\hbar^2}\right)^{3/2}\sqrt{\epsilon}$。

$$
N = \int_0^{E_F}g(\epsilon)d\epsilon = \frac{V}{3\pi^2}\left(\frac{2mE_F}{\hbar^2}\right)^{3/2}
$$

$$
E_{\text{tot}} = \int_0^{E_F}\epsilon g(\epsilon)d\epsilon = \frac{2}{5}NE_F\cdot\frac{1}{1}\cdot 5/3 \cdot \frac{3}{5}\cdot ...
$$

直接积分：$E_{\text{tot}} = \frac{V}{2\pi^2}(2m/\hbar^2)^{3/2}\cdot\frac{2}{5}E_F^{5/2} = \frac{3}{5}NE_F$。

**$T=0$ 时仍有零点能量** $\frac{3}{5}NE_F \neq 0$——泡利原理禁止全部电子退到最低能态。金属中 $E_F\sim 5$ eV，对应"费米温度" $T_F = E_F/k_B \sim 60{,}000$ K。

### 习题 6（德拜模型）— 声子热容

德拜模型声子热容低温行为：

**解**：三维声子态密度 $g(\omega)\propto\omega^2$（直到德拜频率 $\omega_D$）。高温 $C_V\to 3Nk_B$（Dulong-Petit）。低温 $T\ll\Theta_D$：

$$
C_V = \frac{12\pi^4}{5}Nk_B\left(\frac{T}{\Theta_D}\right)^3
$$

**$T^3$ 律**——是绝缘体低温热容的标志。金属低温还有电子贡献 $\gamma T$（来自费米面附近电子），所以 $C_V = \gamma T + AT^3$。

### 习题 7（玻色凝聚）— 临界温度

理想玻色气体凝聚温度 $T_c$。

**解**：$T < T_c$ 时基态宏观占据。临界点条件：激发态粒子数饱和。用 BE 分布 $\bar{n} = (e^{\beta\epsilon}-1)^{-1}$ 在三维盒子中（$\epsilon = \hbar^2 k^2/2m$，$k$ 量子化）：

$$
N_{\text{ex}} = \int_0^\infty \frac{g(\epsilon)d\epsilon}{e^{\beta\epsilon}-1}\Big|_{T=T_c} = N
$$

求出：

$$
\boxed{T_c = \frac{2\pi\hbar^2}{mk_B}\left(\frac{n}{\zeta(3/2)}\right)^{2/3}, \qquad \zeta(3/2) \approx 2.612}
$$

$T < T_c$ 时 $N_0/N = 1 - (T/T_c)^{3/2}$——基态宏观占据。这是 1995 年 Cornell-Wieman-Ketterle 实验实现的 BEC（2001 诺奖）。

### 习题 8（黑体辐射）— 维恩位移

由 Planck 公式 $u(\nu)$，求峰值频率 $\nu_{\max}$ 与 $T$ 的关系。

**解**：$du/d\nu = 0$ → $x = h\nu/k_BT$ 满足 $3(1-e^{-x}) = x$，数值解 $x\approx 2.82$。

$$
h\nu_{\max}/k_BT \approx 2.82, \qquad \lambda_{\max}T \approx 2.9\times 10^{-3}\text{ m·K}
$$

**维恩位移定律**——测恒星光谱峰值波长就能推温度（太阳 $\lambda_{\max}\approx 500$ nm → $T\approx 5800$ K）。

### 习题 9（涨落）— 能量涨落

正则系综中能量方差。

**解**：

$$
\langle E^2\rangle - \langle E\rangle^2 = \frac{\partial^2 Z}{\partial(-\beta)^2}/Z - (\cdots)^2 = \frac{\partial^2\ln Z}{\partial(-\beta)^2} = k_BT^2 C_V
$$

$$
\frac{\Delta E}{\langle E\rangle} = \frac{\sqrt{k_BT^2 C_V}}{U} \sim \frac{1}{\sqrt{N}}
$$

宏观系统 $N\sim 10^{23}$，相对涨落 $10^{-12}$——**统计力学为什么能预言宏观确定性**。

---

## 9. 反直觉发现

### 9.1 时间箭头：热力学第二定律

牛顿 / 薛定谔方程时间反演不变——基础物理定律中没有"过去未来"的区别。但熵增原理给出明确的时间方向：打破的杯子不会自动复原。

**关键**：基础定律可逆 + 大数定律 → 宏观不可逆。熵增是**概率现象**：$N\sim 10^{23}$ 个粒子的所有粒子恰好都退回杯子状态的概率是 $e^{-10^{23}}$，"事实上不可能"。

### 9.2 麦克斯韦妖与信息热力学

设想一个"小妖"在分隔冷热气体的隔板上控制门，让快分子过一边、慢分子过另一边——形成温差，违反第二定律。

解决：小妖必须**测量**分子速度，存储信息。Landauer 原理：擦除 1 bit 信息至少耗散 $k_BT\ln 2$ 热量。妖整理完信息后擦除存储，释放的热量正好抵消温差收益——第二定律完整闭环。这是**信息是物理**的明证。

### 9.3 负温度

构造能级有上限的系统（如核自旋在磁场中），可出现 $\beta < 0$，即 $T < 0$！

**意义**：负温度比任何正温度都"更热"——热量从负温流到正温。这是因为温度定义 $1/T = \partial S/\partial E$，能量超过某阈值后熵随能量**减小**，$T$ 变负。

### 9.4 量子统计导致反常宏观行为

- **玻色凝聚**：粒子凝聚到基态 → 超流（液氦-4）、超导（Cooper 对近似玻色子）、激光（光子凝聚到同模式）。
- **泡利排斥**：费米子挤满能级 → 白矮星、中子星对抗引力坍缩（费米简并压）；金属的硬度、导电性来自费米海。

**同样的多体数学，符号差（+1 vs -1）的差别给出截然不同的宏观物态**——这是统计力学最美的统一。

### 9.5 临界点的普适性

水、CO₂、铁磁体、合金、超流，看似无关，但相变临界点附近有相同临界指数——序参量维度 $n$ 和空间维度 $d$ 相同的系统属于同一"普适类"。

**深层原因**：临界点关联长度发散，微观细节（分子形状、力程）被平均掉，只剩对称性。重整化群用数学严格化这个直觉——Wilson 1982 诺奖。

---

## 10. 不足与延伸

| 本主题局限 | 延伸方向 | 课程 |
|-----------|---------|------|
| 平衡态 | 非平衡：涨落定理、Jarzynski 等式、生命系统 | 8.08 续 / 8.592 |
| 经典 + 简单量子 | 强相互作用多体、量子相变 | 8.511 凝聚态 |
| 静态 | 动力学、输运（玻尔兹曼方程） | 8.09 / 流体 |
| 不含引力 | 黑洞热力学、Bekenstein-Hawking 熵 | 8.962 GR |
| 不含信息论 | 量子信息、纠缠熵 | 6.443 JQC |
| 平均场 | RG 重整化群、临界现象严格 | 8.512 |

**学习路径**：8.044（Schroeder）→ 8.08（Reif + 量子统计）→ 8.511（Pathria 多体）→ 8.512（RG）。

---

**参考**：
- Schroeder《Introduction to Thermal Physics》Ch 1-3 (热力学), Ch 4-6 (统计), Ch 7 (量子统计)
- Reif《Fundamentals of Statistical and Thermal Physics》Ch 6-7 (系综), Ch 9 (量子统计), Ch 10 (相变)
- Pathria & Beale《Statistical Mechanics》4ed — 研究生版
- Kardar《Statistical Physics of Particles/Fields》— MIT 进阶教材
- MIT OCW 8.044 (Cohen) / 8.08 (Kardar)

---

## 🎯 费曼式入口（白话版）

> **一句话解释**：统计物理研究"一堆粒子在一起会怎样"。一个空气分子撞你，你感觉不到；但 $10^{23}$ 个空气分子每秒撞你 $10^{23}$ 次，你感觉到的就是"气压"和"温度"。统计物理就是把微观粒子的混乱运动翻译成宏观的"热"、"温度"、"压强"——它是连接微观和宏观的翻译官。
>
> **生活类比**：
> - 温度 ≈ 分子平均动能的"体温计"——温度高 = 分子跑得快
> - 熵 ≈ 房间的凌乱程度——整洁（低熵）很容易破坏，凌乱（高熵）总是自然发生
> - 第二定律 ≈ 打碎的杯子不会自己拼回来——不是不可能，而是概率小到宇宙热寂都等不到
> - 配分函数 ≈ 一本"菜单"——列出系统所有可能的微观状态及其"价格"（能量），从菜单可以算出所有宏观性质
> - 玻尔兹曼分布 ≈ "越高能量越没人去"——住在山上的人比住在谷底的人少（$e^{-E/kT}$）
> - 相变 ≈ 人群中突然有人开始跑，然后所有人跟着跑——微观上没有变化，但宏观行为突变了
>
> **反直觉发现**：你以为是热力学第二定律让时间有方向（熵增 = 时间箭头）？更深层的是：**微观物理定律本身是时间可逆的**（牛顿方程、薛定谔方程都对称于时间）！时间的箭头纯粹来自概率——$10^{23}$ 个粒子有 $10^{10^{23}}$ 种方式排列成"乱"，只有 1 种方式排列成"整齐"。这就是为什么鸡蛋碎了不会自动复原——不是物理定律禁止，而是概率禁止。麦克斯韦妖的故事告诉我们：信息就是物理。

---

## 🔗 衔接：这个主题从哪来，到哪去

### 前置知识
- **Topic 01 经典力学**：哈密顿量 $H = T + V$（配分函数的核心）、能量守恒
- **Topic 03 量子力学**：量子态、能量本征值——量子统计（玻色子/费米子）需要量子力学基础
- **概率论与组合数学**：排列组合（微观状态计数）、概率分布

### 本主题解决了什么危机
- **热质说的终结（19 世纪）**：19 世纪初人们认为"热"是一种流动的流体（热质）。焦耳（1840s）通过实验证明热是能量的一种形式 → 热力学第一定律 $\Delta U = Q - W$。
- **时间箭头之谜**：牛顿方程是时间可逆的，但现实世界中打破的杯子不会复原、人不能返老还童。**为什么微观可逆但宏观不可逆？** 玻尔兹曼（1872）给出了答案：$S = k_B \ln \Omega$——熵只是微观状态数的对数。不可逆性不是物理定律的属性，而是概率的属性。
- **麦克斯韦妖的信息悖论**：1867 年麦克斯韦提出一个思想实验——一个"小妖"可以筛选快慢分子，违反第二定律。这个悖论困扰了物理学家近一个世纪，直到兰道尔原理（1961）给出答案：**擦除 1 bit 信息至少耗散 $k_B T \ln 2$ 的热量**——信息是物理的。

### 本主题留下的新危机
- **非平衡态统计物理**：以上所有理论只处理平衡态（系统"安顿下来"后的状态）。但生命系统、湍流、气候系统都是**远离平衡**的。非平衡统计物理至今是开放的活跃前沿——没有统一的非平衡"配分函数"。
- **黑洞信息悖论**：贝肯斯坦-霍金熵 $S_{BH} = k_B A/(4\ell_P^2)$ 表明黑洞的熵正比于面积而非体积——这暗示了全息原理，但具体的信息如何编码至今未解。
- **生命与热力学**：薛定谔 1944 年问"生命是什么"——生命如何在不违反第二定律的情况下维持低熵（高度有序）？答案似乎是：生命通过消耗环境能量来"排出"熵（耗散结构）。

### 后续主题
- **Topic 06 凝聚态物理**：量子统计（费米-狄拉克分布 → 电子能带、玻色-爱因斯坦凝聚 → 超导、超流）
- **Topic 08 广义相对论**：黑洞热力学、霍金辐射温度 $T_H = \hbar\kappa/(2\pi k_B c)$
- **信息论与机器学习**：熵的概念被推广到信息熵（香农熵 $S = -\sum p\ln p$），成为机器学习（交叉熵损失）的核心

---

## 🏭 理论联系实际：5 个工业/生活应用

1. **热机与制冷循环**：卡诺循环效率 $\eta = 1 - T_C/T_H$ 是所有热机的理论上限。汽车发动机、火力发电站、空调、冰箱都遵循这条定律。
   - 实例：发电厂蒸汽轮机（朗肯循环）；特斯拉热泵空调的 COP 可达 4.0

2. **半导体器件设计**：费米-狄拉克分布决定了电子在导带和价带的占据数。通过掺杂（n 型/p 型）移动费米能级，控制导电性——这就是 transistor 的物理基础。
   - 实例：Intel 18A 工艺（1.8nm 节点）；温度升高导致漏电流增大 = 统计物理的直接后果

3. **化学电池与燃料电池**：电化学反应的速率和方向由自由能 $\Delta G = \Delta H - T\Delta S$ 决定（吉布斯自由能 = 热力学势）。锂离子电池的电压、容量、温度特性都遵循统计物理规律。
   - 实例：宁德时代麒麟电池（能量密度 255 Wh/kg）；氢燃料电池效率可达 60%

4. **蛋白质折叠与药物设计**：蛋白质折叠成 3D 结构的过程本质上是在自由能景观上寻找极小值——这是统计物理（配分函数 + 能量景观）在生物学中的直接应用。
   - 实例：AlphaFold（DeepMind）预测蛋白质结构——本质是学习自由能景观

5. **退火算法与量子退火**：模拟退火（Simulated Annealing）灵感来自晶体退火——先高温（大步探索）、再慢慢降温（精细优化）。D-Wave 量子退火机利用量子隧穿来优化组合问题。
   - 实例：D-Wave Advantage（5000+ 量子比特量子退火机，用于物流优化、金融建模）

---

## 🔬 最新研究前沿（2024-2026）

> 基于 Nature 系列期刊搜索的真实结果

### 活性物质：耦合微电机阵列中的相干与波传播
- **发现**：用 3D 打印的旋转微电机实验证明了：旋转运动可以导致时空有序以及无序诱导的波传播。耦合的自驱动组件（无论生物还是人工）可以展现协调动力学——这是"活性物质"物理的重要进展。
- **来源**：Braun, R. et al. *Nature Physics* (2026)
- **日期**：2026 年 8 月
- **为什么重要**：活性物质是非平衡统计物理的核心——细菌群落、鸟群、细胞组织都遵循类似规律

### 社会模仿的随机热力学
- **发现**：将随机热力学从能量系统扩展到社会模仿动力学——建立了一个"第二定律"联系社会属性变化、信息和不可逆性，并有涨落定理和不确定性关系支撑。
- **来源**：Irisarri, L. et al. *Nature Communications* (2026)
- **日期**：2026 年 8 月
- **为什么重要**：统计物理框架扩展到社会动力学——信息、熵、不可逆性在社会系统中也有意义

### 耗散动力学的可辨识学习
- **发现**：开发了从轨迹数据中恢复唯一能量景观并量化熵产生率的框架——揭示了聚合物拉伸中的标度律和学习算法中的采样偏差。
- **来源**：Zhu, A. et al. *Nature Communications* (2026)
- **日期**：2026 年 8 月
- **为什么重要**：将统计物理（熵产生 = 不可逆性度量）与机器学习结合——可以从未知动力学中提取热力学信息

### 细胞组织中的相变——黏附与堵塞的解耦
- **发现**：通过独立调节细胞密度和黏附（体外 + 体内），发现黏附决定了组织的物质态——黏附驱动的固态化在未堵塞的多能组织中驱动上皮组织化。相变主导发育程序！
- **来源**：*Nature Physics* **22**, 830 (2026)
- **日期**：2026 年 6 月
- **为什么重要**：生物学中的相变——统计物理概念（堵塞转变、玻璃化）直接解释胚胎发育

---

## 🗺️ 学习 Roadmap（MIT 路径）

### 🎓 入门（2-3 周）
- 📖 读：Schroeder《Introduction to Thermal Physics》Ch 1-3（热力学四定律 + 熵 + 温度）
- 🎥 看：MIT OCW **8.044**（Statistical Physics I）
  - 重点：理解熵 $S = k_B \ln\Omega$ 的物理含义、卡诺循环
- ✍️ 做：
  - 计算理想气体的等温/绝热过程
  - 运行 `physics_demos.py` 的 `statistical()` demo 观察麦克斯韦-玻尔兹曼分布

### 🏗️ 进阶（4-6 周）
- 📖 读：Schroeder Ch 4-7（统计力学 + 量子统计）、Reif Ch 6-10（系综 + 相变）
- 💻 做：
  - 用 Monte Carlo 方法模拟二维伊辛模型，观察自发磁化相变
  - 用 `physics_demos.py` 模拟玻尔兹曼分布
- 🧪 实验：MIT Junior Lab（测量热导率、比热容）

### 🔬 深造（持续）
- 📄 读：
  - Pathria & Beale《Statistical Mechanics》4ed——研究生标准教材
  - Kardar《Statistical Physics of Particles/Fields》——MIT 教材，难度大但视野最高
  - Sethna《Statistical Mechanics: Entropy, Order Parameters, and Complexity》——信息论视角
- 🛠️ 项目：用 Metropolis 算法模拟渗流模型（percolation），找临界点 $p_c$

### ✅ 知识检查
- [ ] 能解释为什么 $S = k_B \ln\Omega$ 中的对数来自组合数学
- [ ] 能推导理想气体的麦克斯韦速度分布
- [ ] 理解正则系综与微正则系综的区别（什么时候用哪个）
- [ ] 能解释为什么玻色子在低温下凝聚（BEC）而费米子不会（泡利不相容）
- [ ] 能解释涨落定理（为什么短时间内第二定律可以"违反"）
