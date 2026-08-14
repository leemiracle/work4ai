# Topic 04 — 热力学与统计力学

> **Oxford MPhys · Year 2 Thermodynamics + Statistical Mechanics**
> 教材：Zemansky & Dittman *Heat and Thermodynamics* 7ed (1997) + Guenther *Statistical Mechanics* / Pathria & Beale *Statistical Mechanics* 4ed
> 覆盖：热力学定律、系综理论、量子统计、相变

---

## 目录

1. [课程定位](#1-课程定位)
2. [热力学四定律](#2-热力学四定律)
3. [热力学势与麦克斯韦关系](#3-热力学势与麦克斯韦关系)
4. [系综理论](#4-系综理论)
5. [量子统计](#5-量子统计)
6. [相变与临界现象](#6-相变与临界现象)
7. [反直觉实验 (Python)](#7-反直觉实验-python)
8. [Tutorial 习题](#8-tutorial-习题)
9. [局限与延伸阅读](#9-局限与延伸阅读)

---

## 1. 课程定位

Oxford Y2 的「热力学 + 统计力学」是两门互补课：

| 学期 | 课程 | 教材 | 视角 |
|------|------|------|------|
| HT | Thermodynamics | Zemansky | **唯象**：从实验定律出发，不问微观 |
| TT | Statistical Mechanics | Guenther / Pathria Ch.1-7 | **微观**：从分子配分函数导出热力学 |

**Oxford 风格**：先严格建立热力学（不像美式教材一开始就混杂），再用统计力学「自上而下」验证。这种顺序让物理图像更清晰——热力学的普适性（即便对非平衡、复杂系统）凸显出来。

---

## 2. 热力学四定律

### 2.1 第零定律 (Zemansky §1.5)

若 $A$ 与 $B$ 各自与 $C$ 处于热平衡，则 $A$ 与 $B$ 热平衡。**推论**：存在**温度** $T$ 这一态函数。

> **直觉**：第零律不是废话——它建立了「温度」的可操作定义（温度计）。Boltzmann 之前的物理学家靠这条公理绕开了「温度是什么」的难题。

### 2.2 第一定律 (Zemansky §3)

$$
\boxed{\;\Delta U=Q-W\quad\text{或}\quad dU=\delta Q-\delta W\;}
$$

- $U$：内能，**态函数**（与路径无关）
- $Q$：热量，**过程量**（依赖路径，故用 $\delta$ 而非 $d$）
- $W$：系统对外做功，$W=\int p\,dV$（可逆）

**关键**：能量守恒；$U$ 是态函数意味着 $dU$ 是恰当微分。

### 2.3 第二定律 (Zemansky §6-7)

**Clausius 表述**：热量不能自发从低温流向高温。

**Kelvin 表述**：不可能从单一热源吸热完全变成功而不产生其他效应。

**熵表述**（最普适）：孤立系统熵不减
$$
\boxed{\;dS\ge\frac{\delta Q}{T}\quad(\text{等号对可逆过程})\;}
$$

态函数 $S$ 的存在性证明来自 Carnot 定理：所有工作在 $T_H,T_C$ 间的热机效率 $\eta\le1-T_C/T_H$。

### 2.4 第三定律 (Zemansky §10)

$$
\boxed{\;T\to0\ \text{时}\ S\to S_0\ \text{(常数, 通常取 0)}\;}
$$

**推论**：绝对零度不可达（有限步数冷却）。Nernst 定理。

---

## 3. 热力学势与麦克斯韦关系

### 3.1 四个势 (Zemansky §9)

| 势 | 定义 | 自然变量 | 物理意义 |
|----|------|---------|---------|
| 内能 $U$ | — | $S,V,N$ | 绝热功 |
| 焓 $H$ | $U+pV$ | $S,p,N$ | 等压热 |
| 自由能 $F$ (Helmholtz) | $U-TS$ | $T,V,N$ | 等温功 |
| 吉布斯 $G$ | $U+pV-TS$ | $T,p,N$ | 等温等压功（化学势 $\mu=G/N$） |

### 3.2 麦克斯韦关系

由「势的二阶偏导与顺序无关」推出。例如由 $dU=TdS-pdV$：
$$
\boxed{\;\left(\frac{\partial T}{\partial V}\right)_S=-\left(\frac{\partial p}{\partial S}\right)_V\;}
$$

四个势共给出 4 个麦克斯韦关系——Oxford tutorial 的经典记忆法（热力学方阵 / Born square）。

### 3.3 化学势与开放系统

引入粒子数 $N$：$dU=TdS-pdV+\mu dN$，$\mu=(\partial U/\partial N)_{S,V}$。

**相平衡**条件：两相化学势相等 $\mu_1=\mu_2$。Clapeyron 方程给出相界斜率：
$$
\boxed{\;\frac{dp}{dT}=\frac{\Delta s}{\Delta v}=\frac{L}{T\Delta v}\;}
$$

（$\Delta s,\Delta v$ 是摩尔熵变/体积变，$L$ 是潜热）

---

## 4. 系综理论

### 4.1 微正则系综 (Pathria §1)

孤立系统 $E,V,N$ 固定。**等先验概率假设**：每个可达微观态等概率。

熵（Boltzmann 公式）：
$$
\boxed{\;S=k_B\ln\Omega\;}
$$

$\Omega(E,V,N)$ 是能量在 $[E,E+\delta E]$ 内的微观态数。$S$ 极大给出平衡态。

**温度的定义**：$1/T=(\partial S/\partial E)_{V,N}$——温度是熵对能量的响应。

### 4.2 正则系综 (Pathria §3)

与大热源接触，$T,V,N$ 固定。概率分布：
$$
\boxed{\;P_i=\frac{1}{Z}e^{-\beta E_i},\quad Z=\sum_i e^{-\beta E_i},\quad \beta=\frac{1}{k_BT}\;}
$$

配分函数 $Z$ 编码**全部**热力学。关键关系：
$$
F=-k_BT\ln Z,\quad U=-\frac{\partial\ln Z}{\partial\beta},\quad S=k_B(\ln Z+\beta U)
$$

> **Oxford 强调的桥梁**：从微观配分函数（统计力学）直接得到自由能 $F$（热力学势）。$Z$ 是两套语言的「翻译机」。

### 4.3 巨正则系综 (Pathria §4)

开放系统，$T,V,\mu$ 固定：
$$
\boxed{\;\mathcal{P}_{i,N}=\frac{1}{\Xi}e^{-\beta(E_i-\mu N)},\quad \Xi=\sum_{N=0}^\infty\sum_i e^{-\beta(E_i-\mu N)}\;}
$$

巨配分函数 $\Xi$。$\langle N\rangle=(1/\beta)\partial\ln\Xi/\partial\mu$。

**等价性**：在热力学极限 ($N\to\infty$) 三个系综给出相同结果——能量涨落 $\Delta E/\langle E\rangle\sim1/\sqrt{N}$ 可忽略。

### 4.4 经典理想气体 (Pathria §5)

单原子理想气体配分函数：
$$
Z=\frac{1}{N!}\left(\frac{V}{\lambda_T^3}\right)^N,\quad \lambda_T=\frac{h}{\sqrt{2\pi m k_BT}}\ \text{(热德布罗意波长)}
$$

$1/N!$ 是 Gibbs 修正（修正粒子不可分辨），消除了 Gibbs 悖论（混合熵）。

推出：$pV=Nk_BT$（理想气体方程）、$U=\tfrac32 Nk_BT$、$C_V=\tfrac32 Nk_B$。

---

## 5. 量子统计

### 5.1 全同粒子与对称性 (Pathria §6)

波函数在对换下：
- **玻色子**：对称 $\psi(1,2)=+\psi(2,1)$，整数自旋
- **费米子**：反对称 $\psi(1,2)=-\psi(2,1)$，半整数自旋

**Pauli 不相容**：费米子不能占据同一态（$\psi(1,1)=-\psi(1,1)=0$）。

### 5.2 占据数分布

巨正则系综推出：
$$
\boxed{\;\bar n_\epsilon=\frac{1}{e^{\beta(\epsilon-\mu)}\pm1}\quad(+\text{ 费米子, }-\text{ 玻色子})\;}
$$

- Fermi-Dirac: $\bar n=\frac{1}{e^{(\epsilon-\mu)/k_BT}+1}$
- Bose-Einstein: $\bar n=\frac{1}{e^{(\epsilon-\mu)/k_BT}-1}$

### 5.3 简并费米气体 (Pathria §8)

$T=0$ 时态填满至 Fermi 能 $\epsilon_F$：
$$
\epsilon_F=\frac{\hbar^2}{2m}\left(3\pi^2 n\right)^{2/3},\quad E_{\text{tot}}=\frac35 N\epsilon_F
$$

Fermi 压强 $p_0=\tfrac25 n\epsilon_F$ 抵抗引力塌缩——**白矮星、中子星稳定**的根据。

有限温度修正（Sommerfeld 展开）：
$$
\frac{C_V}{Nk_B}=\frac{\pi^2}{2}\frac{T}{T_F}\quad(T\ll T_F)
$$

线性 $T$ 依赖，与经典 $C_V=\tfrac32 k_B$（常数）形成鲜明对比——这是金属低温比热的特征。

### 5.4 玻色-爱因斯坦凝聚 (Pathria §7.1)

对 $T<T_c$，宏观数量玻色子凝聚到基态：
$$
\boxed{\;T_c=\frac{2\pi\hbar^2}{mk_B}\left(\frac{n}{\zeta(3/2)}\right)^{2/3}\approx3.31\frac{\hbar^2 n^{2/3}}{mk_B}\;}
$$

凝聚分数 $N_0/N=1-(T/T_c)^{3/2}$。1995 年 Cornell-Wieman-Ketterle 首次在稀薄碱金属气体中实现 BEC（2001 诺奖）。

---

## 6. 相变与临界现象

### 6.1 Ehrenfest 分类

- **一级**：自由能一阶导（熵、体积）不连续。潜热存在。例：冰融化。
- **二级（连续）**：一阶导连续，二阶导（比热、压缩率）发散。例：铁磁 Curie 点、超导转变。

### 6.2 Ising 模型 (Pathria §12)

最近邻自旋 $\sigma_i=\pm1$，哈密顿 $H=-J\sum_{\langle ij\rangle}\sigma_i\sigma_j-h\sum_i\sigma_i$。

**一维**：无有限温相变（Peierls 论证）。
**二维**：Onsager 1944 严格解，$T_c=2J/(k_B\ln(1+\sqrt2))\approx2.269\,J/k_B$。

Onsager 比热的对数发散：
$$
C\sim|T-T_c|^{-\alpha},\quad \alpha=0\ (\text{对数发散})
$$

### 6.3 临界指数与标度 (Pathria §12)

邻近 $T_c$ 各量幂律发散：
- 磁化 $M\sim(T_c-T)^\beta$（$\beta=1/8$ 二维 Ising）
- 磁化率 $\chi\sim|T-T_c|^{-\gamma}$（$\gamma=7/4$）
- 关联长度 $\xi\sim|T-T_c|^{-\nu}$（$\nu=1$）

**标度律**（Y4 重整化群）：四个指数受两个独立标度假说约束 $\alpha+2\beta+\gamma=2$（Rushbrooke）、$\gamma=\beta\delta$（Widom）。

### 6.4 普适性

不同物理系统（液气临界点、二元合金、磁体）**共享**同一组临界指数——只依赖**维数 + 对称性 + 序参量分量数**。这是 Wilson 重整化群（Y4）的核心物理。

---

## 7. 反直觉实验 (Python)

> **Maxwell-Boltzmann → Fermi-Dirac → Bose-Einstein 分布的对比**：本实验数值实现三种统计，画出分布，并展示 Fermi「台阶」与 Bose「堆积」的反直觉差异。

```python
#!/usr/bin/env python3
"""
三种量子统计分布对比: Maxwell-Boltzmann / Fermi-Dirac / Bose-Einstein
Pathria Statistical Mechanics §6
纯标准库, 零依赖。运行: python3 quantum_statistics.py
"""
import math

def fermi_dirac(eps, mu, kT):
    """FD 占据数"""
    x = (eps - mu) / kT
    if x > 500: return 0.0
    if x < -500: return 1.0
    return 1.0 / (math.exp(x) + 1.0)

def bose_einstein(eps, mu, kT):
    """BE 占据数 (要求 eps > mu)"""
    x = (eps - mu) / kT
    if x <= 0: return float('inf')   # 凝聚
    if x > 500: return 0.0
    return 1.0 / (math.exp(x) - 1.0)

def maxwell_boltzmann(eps, mu, kT):
    """MB 占据数"""
    x = (eps - mu) / kT
    if x > 500: return 0.0
    return math.exp(-x)

# 态密度 (三维自由粒子, 单位制 hbar=m=1)
def dos(eps):
    """g(eps) ∝ sqrt(eps), eps >= 0"""
    if eps < 0: return 0.0
    return math.sqrt(eps) / (2 * math.pi**2)

def total_number(integrand, mu, kT, eps_max=20.0, n=2000):
    """数值积分 N/V = ∫ g(eps) * f(eps) deps"""
    d = eps_max / n
    total = 0.0
    for i in range(n):
        eps = (i + 0.5) * d
        total += dos(eps) * integrand(eps, mu, kT) * d
    return total

def find_mu(target_n, integrand, kT, mu_lo=-5.0, mu_hi=10.0, tol=1e-4):
    """二分法求化学势使 N = target_n"""
    for _ in range(60):
        mu_mid = 0.5 * (mu_lo + mu_hi)
        n = total_number(integrand, mu_mid, kT)
        if n < target_n: mu_lo = mu_mid
        else: mu_hi = mu_mid
        if abs(mu_hi - mu_lo) < tol: break
    return 0.5 * (mu_lo + mu_hi)

print("="*64)
print("三种量子统计分布对比 (三维自由粒子, 态密度 g(eps) ∝ sqrt(eps))")
print("="*64)

target_n = 1.0   # 目标粒子数密度 (任意单位)
print(f"目标粒子数密度 N/V = {target_n}")
print()

for kT in [2.0, 0.5, 0.1]:
    mu_FD = find_mu(target_n, fermi_dirac, kT)
    mu_MB = find_mu(target_n, maxwell_boltzmann, kT)
    # 对 BE, mu 必须 < 0 (基态能量 = 0); 若求出的 mu > 0 说明发生 BEC
    mu_BE_candidate = find_mu(target_n, bose_einstein, kT, mu_lo=-10, mu_hi=-0.01)
    print(f"kT = {kT:4.2f}:")
    print(f"  Fermi-Dirac:    mu = {mu_FD:+.4f}")
    print(f"  Bose-Einstein:  mu = {mu_BE_candidate:+.4f} (必须 < 0)")
    print(f"  Maxwell-Boltz:  mu = {mu_MB:+.4f}")
    
    # 在 eps = mu 附近(或 eps = 0)的占据数
    eps_sample = 0.0
    nFD0 = fermi_dirac(eps_sample, mu_FD, kT)
    nBE0 = bose_einstein(eps_sample, mu_BE_candidate, kT)
    nMB0 = maxwell_boltzmann(eps_sample, mu_MB, kT)
    print(f"  基态(eps=0)占据数: FD={nFD0:.3f}, BE={nBE0:.1f}, MB={nMB0:.3f}")
    print()

print("反直觉发现:")
print("  1. 低温下 Fermi-Dirac 形如'台阶': mu 以下全满, mu 以上全空")
print("     这就是金属中电子'简并压'的来源, 即使 T=0 也有巨大动能")
print("  2. Bose-Einstein 在低温 mu -> 0-, 基态占据数发散 -> BEC")
print("     激光冷却碱金属气体的物理基础 (2001 诺奖)")
print("  3. Maxwell-Boltzmann 在 eps < mu 时超过 1, 违反 Pauli 不相容")
print("     说明高温低密度下三种统计趋同, 低温高密度必须用量子统计")
print()
print("物质量级估算 (T=0 简并费米气体):")
# 金属电子: n ~ 10^29 /m^3, m = m_e
# eps_F = hbar^2/(2m) (3 pi^2 n)^(2/3)
hbar = 1.0546e-34
me = 9.109e-31
n_metal = 1e29
eps_F = hbar**2 / (2*me) * (3*math.pi**2*n_metal)**(2/3)
eV = 1.602e-19
print(f"  金属电子气 n=10^29 /m^3:")
print(f"  Fermi 能 = {eps_F/eV:.2f} eV (对应 T_F ~ {eps_F/1.381e-23:.0f} K)")
print(f"  室温 300 K 远低于 T_F, 金属电子高度简并")
print(f"  这解释为何金属电子对比热的贡献仅 ~T (而非经典 3/2 k_B)")
```

**预期输出**：低温下 FD 分布呈台阶（$\mu_{FD}>0$），BE 分布基态占据数激增（$\mu_{BE}\to0^-$），MB 在 $\epsilon<\mu$ 时可超过 1（违反 Pauli）。金属 Fermi 能 $\sim10$ eV，$T_F\sim10^5$ K。

---

## 8. Tutorial 习题

### T1. Gibbs 悖论 (Zemansky §7.4 / Pathria §1.5)

两种惰性气体 A、B 各 $N$ 个分子，初始由隔板分开，体积均为 $V$。

(a) 抽去隔板（等温），求混合熵变 $\Delta S_{\text{mix}}=2Nk_B\ln2$。

(b) 若 A、B 是**同种**气体（如皆氦），实验测得 $\Delta S=0$。但 (a) 的推导仍形式成立——这是 Gibbs 悖论。

(c) 用全同性论证 $\Omega$ 需除以 $N!$ 修正，证明同种气体混合熵变为零。

> **导师追问**：若 A、B 是同位素（$^3$He vs $^4$He）——前者费米子后者玻色子，量子效应如何改变混合熵？低温 $^3$He-$^4$He 混合制冷 (稀释制冷机) 如何利用此差？

### T2. 黑体辐射的热力学 (Pathria §5)

光子气体（化学势 $\mu=0$，因光子数不守恒）。

(a) 由态密度 $g(\omega)=V\omega^2/(\pi^2 c^3)$ 与 Bose-Einstein 分布推出能量密度：
$$
u(\omega,T)=\frac{\hbar\omega^3}{\pi^2 c^3}\frac{1}{e^{\hbar\omega/k_BT}-1}
$$

(b) 积分得 Stefan-Boltzmann $U/V=\sigma T^4$，$\sigma=\pi^2 k_B^4/(15\hbar^3 c^3)$。

(c) Wien 位移律 $\omega_{\max}/T\approx2.82\,\hbar/k_B$（常数来自方程 $3(1-e^{-x})=x$）。

> **导师追问**：宇宙微波背景 $T=2.725$ K，峰值波长 $\lambda\approx1.06$ mm。如何由 $T$ 推出重子数与光子数比 $\eta\sim10^{-9}$——这是 Big Bang 核合成理论的关键约束？

### T3. 一维 Ising 模型的传递矩阵法 (Pathria §12.1)

$N$ 个自旋周期性连接，配分函数：
$$
Z_N=\mathrm{tr}(T^N),\quad T=\begin{pmatrix}e^{K+h}&e^{-K}\\e^{-K}&e^{K-h}\end{pmatrix}
$$

$K=J/(k_BT),\ h=\beta\mu B$。

(a) 求自由能 $f=-k_BT\ln\lambda_{\max}$，$\lambda_\pm=e^K\cosh h\pm\sqrt{e^{2K}\sinh^2 h+e^{-2K}}$。

(b) 证明对一切 $T>0$ 磁化 $M=0$（无相变）。

> **导师追问**：把相互作用推到二维 ($N\times N$ 网格)，Onsager 严格解显示 $T_c=2.269\,J/k_B$。为何维度如此关键？（提示：Peierls 圈论证）

### T4. 黑体辐射压与恒星稳定 (Pathria Prob.5.6)

光子气体状态方程 $p=u/3$（$u$ 能量密度）。

(a) 由热力学推出绝热过程 $p\propto V^{-4/3}$。

(b) 假设恒星由辐射压主导（如早期恒星），用流体静力平衡 $\frac{dP}{dr}=-G M(r)\rho/r^2$ 估算辐射压与温度梯度，讨论 Eddington 光度极限 $L_{\text{Edd}}=4\pi c G M/\kappa_T$。

> **导师追问**：超过 Eddington 极限的恒星会怎样？这与 Wolf-Rayet 星、γ 暴的驱动机制有何关联？

---

## 9. 局限与延伸阅读

### 局限

1. **平衡态统计力学的核心假设**——等先验概率与各态历经（ergodic）——在非平衡系统未必成立。Oxford Y4 有专门 Non-equilibrium Statistical Mechanics 选修。
2. **相变的 Landau 平均场理论**未在 Y2 深入——它给出错误的临界指数（如 Ising $\beta_{\text{MF}}=1/2$ 而非 $1/8$），需 Y4 Wilson 重整化群修正。
3. **量子统计仅处理理想气体**——相互作用费米液体（Landau 理论）、超流 He-4、超导 BCS 都到 Y3/Y4。
4. **热力学第三定律的细节**：玻璃、自旋玻璃在 $T\to0$ 残余熵 $S_0\neq0$——这不是公理违反，而是简并基态。

### 延伸阅读

- **Kittel & Kroemer** *Thermal Physics* 2ed — Oxford 亦可选用，更直观，与 Guenther 互补。
- **Reif** *Fundamentals of Statistical and Thermal Physics* — 美式经典，详尽到啰嗦，自学友好。
- **Schroeder** *Introduction to Thermal Physics* — 6/10 校共用，文笔最友好。
- **Landau & Lifshitz Vol.5** *Statistical Physics* — Landau 平均场理论发源地，Oxford Y3 推荐。
- **Kardar** *Statistical Physics of Particles/Fields* — MIT 用，Oxford Y4 现代化路径，重整化群最清晰。

---

**版本**：v1.1 (2026-08-12) · Oxford MPhys Phase 1 Topic 04
**依据**：SURVEY.md Oxford Y2 课程表 + Zemansky & Dittman (1997) 7ed + Pathria & Beale (2011) 4ed

---

## 🎯 费曼式入口（白话版）

> **一句话解释**：统计力学是「从 $10^{23}$ 个分子的混乱中，提炼出温度、压强、熵这些宏观规律」的学问——热力学是它的「表象」，分子运动是它的「底牌」。
>
> **生活类比**：想象一个体育馆十万个观众。你预测不了某个具体观众何时鼓掌，但你能预测「平均音量」「何时雷鸣般掌声」——这就是统计力学。Boltzmann 公式 $S=k_B\ln\Omega$ 把「混乱程度」（微观态数 $\Omega$）翻译成「熵」（宏观量），是物理最美的桥梁之一。Fermi-Dirac 与 Bose-Einstein 的差别就像「单人间旅馆」（费米子，一人一间）vs「大通铺」（玻色子，挤一起）——后者冷到极点会突然「全员挤进同一间」，这就是 BEC。
>
> **反直觉发现**：
> - **金属电子在绝对零度仍有巨大动能**：Fermi 能 $\epsilon_F\sim10$ eV，对应 $T_F\sim10^5$ K。室温 300 K 对电子气是「冰点」——这就是金属电子简并压的来源。
> - **熵不是「混乱」而是「可能性」**：$S=k_B\ln\Omega$。气体自由膨胀熵增，不是因为分子「更乱」，而是因为可达到的微观态变多。
> - **玻璃在 $T\to0$ 残余熵不为零**：$S_0\ne0$ 不是公理违反，而是有无穷多简并基态——这挑战了第三定律的简单表述。

---

## 🔗 衔接：从哪来，到哪去

### 前置
- **Y1 Mechanics + 数学方法**：能量守恒、概率论基础、积分
- **Y2 量子力学**（Topic 03）：全同粒子、Fermi-Dirac/Bose-Einstein 的量子起源
- **A-level 热学**：理想气体方程、卡诺循环的现象学

### 本课的危机
- **热力学先于统计力学的 Oxford 顺序**：先严格建立唯象热力学，再用微观验证——学生容易把两者混淆。
- **配分函数 $Z$ 是「翻译机」**：$F=-k_BT\ln Z$ 把微观（能级）翻译到宏观（自由能）。学生常忘记 $Z$ 编码**全部**热力学。
- **三个系综在热力学极限下等价**——但小系统（纳米、生物分子）差异显著，涨落不再是 $\sim1/\sqrt{N}$。

### 新危机
- **等先验概率与各态历经假设未必成立**——非平衡系统（生命、湍流、玻璃）的核心难题。Oxford Y4 有专门 Non-equilibrium Statistical Mechanics 选修。
- **Landau 平均场给出错误临界指数**（如 Ising $\beta_{\text{MF}}=1/2$ 而非 $1/8$）——需 Y4 Wilson 重整化群修正。
- **量子统计仅处理理想气体**——相互作用费米液体（Landau 理论）、超流 He-4、超导 BCS 都到 Y3/Y4。

### 后续
- **Y3 Statistical Mechanics 进阶**：Landau 平均场、相变理论
- **Y3 Condensed Matter**（Topic 06）：Debye 比热、Sommerfeld 电子比热——直接用本课的量子统计
- **Y4 Non-equilibrium Stat Mech / Soft Matter**：Oxford Rudnick、Marenduzzo 等组
- **Y4 重整化群 / Quantum Field Theory**：临界指数的现代化解释

---

## 🏭 理论联系实际：5 个应用

1. **超低温技术（稀释制冷机）**：$^3$He-$^4$He 混合熵差（$^3$He 是费米子、$^4$He 是玻色子）驱动降温——量子统计的直接工程应用，量子计算机的 mK 环境。
2. **白矮星与中子星稳定**：电子/中子的 Fermi 简并压抵抗引力塌缩——Chandrasekhar 极限（$1.44 M_\odot$）完全由 Fermi 气体物理算出。
3. **黑体辐射与宇宙微波背景**：CMB 是 $T=2.725$ K 的近完美黑体——大爆炸遗骸，宇宙学（Topic 08）的「化石记录」。COBE/Planck 卫星精密测量其涨落。
4. **化学与生物分子的自由能计算**：药物设计用 $F=-k_BT\ln Z$ 算蛋白质折叠自由能面——分子动力学模拟的核心统计力学。
5. **Ising 模型与机器学习**：Hopfield 神经网络（2024 诺奖物理！Hinton）的能量函数就是 Ising 哈密顿量——「联想记忆」= 自旋玻璃基态。统计力学是深度学习的数学基础。

---

## 🔬 最新研究前沿（2024-2026）

> 注：firecrawl 搜索返回空数据，以下基于 2024 Nobel Prize、Oxford Soft Matter Group、Nature 公开报道整理。

1. **2024 诺贝尔物理学奖：Hopfield 与 Hinton**——机器学习的基础是统计力学！Hopfield 网络（Ising 自旋玻璃）、Boltzmann 机（配分函数采样）把「学习」翻译成「寻找能量极小」。Oxford 数据科学/统计物理交叉方向因此大热。
2. **活性物质与细胞物理（2024-2025）**：生物分子（肌动蛋白、微管）的自驱动聚合形成「活性液态晶体」——非平衡统计力学的实验平台。Oxford Marenduzzo、Fletcher 组在拓扑缺陷与细胞运动方向活跃。
3. **拓扑相变与非平衡量子系统（2024-2025）**：用量子气体模拟「时间晶体」「费米子拓扑相」——超越传统 Ising 模型的新相变类别。Oxford 与剑桥合作。
4. **超冷原子的量子模拟（2024-2025）**：用光晶格中的超冷原子实现 Hubbard 模型——直接观测 Mott 绝缘体-超流相变。这是「量子气体显微镜」时代，统计力学的实验黄金期。
5. **热力学信息与 Maxwell 妖的最终定论（2024）**：Landauer 原理（擦除 1 比特耗散 $k_BT\ln2$）在纳米尺度实验精确验证——信息真的是物理的。

---

## 🗺️ 学习 Roadmap（Oxford MPhys 路径）

```
Year 2 (HT)                 Year 2 (TT)                 Year 3-4
───────────                ───────────                ─────────
Thermodynamics             Statistical Mechanics      Advanced Stat Mech
· 四定律（零~三）          · 系综理论（微正则/正则/巨）  · 相变与重整化群
· 热力学势 + 麦克斯韦关系  · 量子统计 (FD/BE)          · 非平衡统计力学
· 相变/Clapeyron           · 理想气体/简并费米/BEC     · 软物质/活性物质 (Y4)
· 化学势                    · Ising / 临界指数          · 量子多体 (Y4)
教材: Zemansky             教材: Pathria / Guenther    教材: Kardar, Chaikin-Lubensky
```

**知识检查清单**：
- [ ] 能说出热力学四定律各自的「不可能性」表述
- [ ] 能从 $dU=TdS-pdV+\mu dN$ 推出 4 个麦克斯韦关系（用 Born 方阵）
- [ ] 能算理想气体的配分函数并推出 $pV=Nk_BT$
- [ ] 能解释 Fermi 简并压为何稳定白矮星
- [ ] 能推出 Debye $T^3$ 比热律（与 Topic 06 串联）
- [ ] 能说出 2024 诺奖物理如何把统计力学与机器学习联系起来

**Oxford 特色资源**：
- Soft Matter & Biological Physics Group：Rudnick（DNA 物理）、Marenduzzo（活性物质）
- Y4 选修 *Non-equilibrium Statistical Mechanics* 直通现代前沿
- 与 Oxford Maths Institute 的概率论组交叉（随机过程、大偏差）
