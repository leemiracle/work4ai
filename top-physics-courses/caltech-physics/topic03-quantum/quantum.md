# Topic 03 · 量子力学 — Caltech Ph 2a / Ph 12b / Ph 125

> **课程链**：Ph 2abc（Feynman Lectures Vol 3）→ Ph 12bc Honors（Townsend）→ Ph 125abc Quantum Mechanics（Sakurai / Cohen-Tannoudji）
>
> **教材三角**：Feynman Lectures Vol 3（从双缝实验和自旋出发，最物理化的入门） · Townsend *A Modern Approach to Quantum Mechanics*（从 Stern-Gerlach 和自旋开始，Caltech Ph 12b 选用） · Sakurai *Modern Quantum Mechanics* 3ed（Caltech Ph 125 研究生标准）

---

## Caltech 特色：Feynman Lectures Vol 3 + 路径积分

Feynman 在 Caltech 讲量子力学的方式独步全球：

1. **不自薛定谔方程开始**——他从**双缝实验**和**概率幅叠加**开始。先让你理解"为什么需要概率幅"。
2. **自旋在前，位置在后**——第 1–5 章全是 Stern-Gerlach 和自旋 1/2。有限维希尔伯特空间（2 维）让你先理解叠加、测量、不确定性，再进入无穷维的波动力学。
3. **路径积分的种子**——Feynman 在第 2 章就暗示了"粒子走所有路径"的思想，这后来成为他的路径积分表述，是量子场论的基础。

---

## §1 薛定谔方程

### 1.1 波函数与概率解释

波函数 $\Psi(x, t)$ 包含系统的全部信息。

**玻恩规则**：$|\Psi(x,t)|^2\,dx$ = 在 $x$ 处 $dx$ 范围内找到粒子的概率。

归一化：$\int_{-\infty}^{\infty}|\Psi|^2\,dx = 1$

### 1.2 含时薛定谔方程（TDSE）

$$i\hbar\frac{\partial\Psi}{\partial t} = \hat{H}\Psi = \left(-\frac{\hbar^2}{2m}\nabla^2 + V(\mathbf{r},t)\right)\Psi$$

### 1.3 定态薛定谔方程（TISE）

若 $V$ 不含时间，分离变量 $\Psi(x,t) = \psi(x)e^{-iEt/\hbar}$：

$$\hat{H}\psi = E\psi \qquad \Longrightarrow \qquad -\frac{\hbar^2}{2m}\frac{d^2\psi}{dx^2} + V(x)\psi = E\psi$$

> **Feynman 的强调**（Vol 3 Ch 7–10）：Schrödinger 方程不是"推导"出来的——它是量子力学的**公理**。但 Feynman 会让你先理解为什么经典力学（哈密顿-雅可比方程）是它的极限（$\hbar \to 0$），以及为什么路径积分自然导出它。

---

## §2 三大标准问题

### 2.1 无限深势阱

$V(x) = 0$（$0 < x < a$），$V = \infty$（其他）。

$$\psi_n(x) = \sqrt{\frac{2}{a}}\sin\frac{n\pi x}{a}, \qquad E_n = \frac{n^2\pi^2\hbar^2}{2ma^2} \quad (n = 1, 2, 3, \ldots)$$

**关键特征**：
- 能级离散（量子化的起源）
- $n=1$ 的基态能量 $E_1 > 0$（零点能——不确定性原理的直接后果）
- $\Delta x \sim a \Rightarrow \Delta p \gtrsim \hbar/a \Rightarrow E \sim (\Delta p)^2/2m \sim \hbar^2/(2ma^2)$

### 2.2 量子谐振子

$V(x) = \frac{1}{2}m\omega^2 x^2$

**升降算符方法**（Caltech 的核心教法）：

$$a = \sqrt{\frac{m\omega}{2\hbar}}\left(x + \frac{ip}{m\omega}\right), \qquad a^\dagger = \sqrt{\frac{m\omega}{2\hbar}}\left(x - \frac{ip}{m\omega}\right)$$

$$[a, a^\dagger] = 1$$

$$H = \hbar\omega\left(a^\dagger a + \frac{1}{2}\right)$$

能级：$E_n = \hbar\omega\left(n + \frac{1}{2}\right), \quad n = 0, 1, 2, \ldots$

$$a^\dagger|n\rangle = \sqrt{n+1}\,|n+1\rangle, \qquad a|n\rangle = \sqrt{n}\,|n-1\rangle$$

> **反直觉**：基态 $n=0$ 仍有能量 $\frac{1}{2}\hbar\omega$（零点能）。经典力学中最低能量态是粒子静止在底部 ($E=0$)，量子力学禁止这个态——因为 $\Delta x = 0$ 和 $\Delta p = 0$ 同时成立违反不确定性原理。

### 2.3 氢原子

库仑势 $V(r) = -e^2/(4\pi\epsilon_0 r)$

能级（玻尔公式）：

$$E_n = -\frac{13.6\;\text{eV}}{n^2}, \quad n = 1, 2, 3, \ldots$$

轨道角动量量子数 $l = 0, 1, \ldots, n-1$；磁量子数 $m_l = -l, \ldots, +l$。

**意外简并**：能量只依赖主量子数 $n$，不依赖 $l$。这是库仑势 $1/r$ 的特殊对称性（Runge-Lenz 向量守恒）的结果——经典力学中对应椭圆轨道闭合。

---

## §3 角动量与自旋

### 3.1 轨道角动量

$$\hat{L}^2 Y_l^m = \hbar^2 l(l+1) Y_l^m, \qquad \hat{L}_z Y_l^m = m\hbar\, Y_l^m$$

球谐函数 $Y_l^m(\theta,\phi)$ 是 $\hat{L}^2$ 和 $\hat{L}_z$ 的共同本征态。

### 3.2 自旋 1/2：Townsend/Sakurai 的起点

> **Caltech 的教法**（Townsend Ch 1, Sakurai Ch 1, Feynman Vol 3 Ch 1-5）：不从 Schrödinger 方程开始，而从 **Stern-Gerlach 实验**开始。银原子束经过非均匀磁场后分裂成两束——这是自旋 $1/2$ 的直接实验证据。

自旋算符用 Pauli 矩阵表示：

$$\hat{S}_x = \frac{\hbar}{2}\begin{pmatrix}0 & 1 \\ 1 & 0\end{pmatrix}, \quad \hat{S}_y = \frac{\hbar}{2}\begin{pmatrix}0 & -i \\ i & 0\end{pmatrix}, \quad \hat{S}_z = \frac{\hbar}{2}\begin{pmatrix}1 & 0 \\ 0 & -1\end{pmatrix}$$

$\hat{S}_z$ 的本征态：$|+\rangle = \binom{1}{0}$（自旋向上），$|-\rangle = \binom{0}{1}$（自旋向下）。

### 3.3 叠加与测量

一般态：$|\psi\rangle = \alpha|+\rangle + \beta|-\rangle$，$|\alpha|^2 + |\beta|^2 = 1$

测量 $\hat{S}_z$：得到 $+\hbar/2$ 的概率 $= |\alpha|^2$，$-\hbar/2$ 的概率 $= |\beta|^2$。

> **Feynman 的核心思想**（Vol 3 Ch 1）：概率幅叠加 $\alpha|+\rangle + \beta|-\rangle$ 不是"不知道哪个态"——**粒子真的同时处于两个态**。双缝实验中的干涉条纹就是证据：遮住一条缝反而让屏幕某些位置更亮（干涉消失）。

### 3.4 顺序测量的不可交换性

连续测量 $S_x$ 再测量 $S_z$ 与反过来结果不同：

$$[\hat{S}_x, \hat{S}_z] = i\hbar \hat{S}_y \neq 0$$

这就是**不确定性原理**的数学根源：

$$\Delta S_x \cdot \Delta S_z \geq \frac{\hbar}{2}|\langle S_y \rangle|$$

---

## §4 微扰理论

### 4.1 非简并微扰

哈密顿量 $\hat{H} = \hat{H}_0 + \lambda \hat{H}'$，已知 $\hat{H}_0$ 的解。

能量一级修正：

$$E_n^{(1)} = \langle n^{(0)}|\hat{H}'|n^{(0)}\rangle$$

波函数一级修正：

$$|n^{(1)}\rangle = \sum_{m \neq n}\frac{\langle m^{(0)}|\hat{H}'|n^{(0)}\rangle}{E_n^{(0)} - E_m^{(0)}}|m^{(0)}\rangle$$

**例**（谐振子 + 微扰 $H' = \lambda x$）：$\langle 0|x|0\rangle = 0$（宇称）。一级修正为零。二级修正 $E_0^{(2)} = -\lambda^2/(2m\omega^2)$——恰好等于经典力学中常数力 $F = -\lambda$ 使平衡位置移动 $x_0 = \lambda/(m\omega^2)$ 后的势能变化。

### 4.2 简并微扰

当 $E_n^{(0)}$ 有简并时，需在简并子空间内对角化微扰矩阵。

**例**：氢原子 $n=2$ 四重简并（$2s, 2p_{+1}, 2p_0, 2p_{-1}$）。Stark 效应（外加电场）使 $2s$ 和 $2p_0$ 简并分裂。

### 4.3 含时微扰与 Fermi 黄金定则

在弱周期微扰 $\hat{H}'(t) = \hat{V}e^{-i\omega t}$ 下，从 $|i\rangle$ 跃迁到 $|f\rangle$ 的速率：

$$\boxed{\Gamma_{i\to f} = \frac{2\pi}{\hbar}|\langle f|\hat{V}|i\rangle|^2 \rho(E_f)}$$

其中 $\rho(E_f)$ 是末态密度。这是**激光物理**、**放射性衰变**、**光电效应**的统一基础。

---

## Python 演示：无限深势阱本征态 + 谐振子升降算符

```python
"""
Caltech Ph 2a / Ph 12b Demo: 量子力学的两个标准问题
1. 无限深势阱的本征态和概率密度
2. 谐振子的升降算符与零点能验证
纯标准库零依赖，bash 可直接跑通。
"""
import math

hbar = 1.0  # 归一化单位 ℏ = m = a = ω = 1

# ── 1. 无限深势阱 (0 < x < a, a=1) ──
a = 1.0
m_well = 1.0

def psi_n(n, x):
    """无限深势阱第 n 个本征态"""
    if x <= 0 or x >= a:
        return 0.0
    return math.sqrt(2/a) * math.sin(n * math.pi * x / a)

def energy_n(n):
    """能级 E_n = n²π²ℏ²/(2ma²)"""
    return n**2 * math.pi**2 * hbar**2 / (2 * m_well * a**2)

print("=== 无限深势阱能级 ===")
for n in range(1, 6):
    print(f"  E_{n} = {energy_n(n):.4f} (E_1 = {energy_n(1):.4f}, 比值 = {n**2})")

# 归一化验证（数值积分）
N_pts = 10000
dx = a / N_pts
for n in [1, 2, 3]:
    norm_sq = sum(psi_n(n, x)**2 * dx for x in [i*dx for i in range(N_pts)])
    print(f"  ∫|ψ_{n}|²dx = {norm_sq:.6f} (应=1.0)")

# 零点能
print(f"\n零点能 E_1 = {energy_n(1):.4f} ℏ²π²/(2ma²) > 0")
print(f"经典粒子最低能量 = 0 → 量子禁止 Δx=Δp=0 同时成立\n")

# ── 2. 谐振子升降算符 ──
m_osc = 1.0
omega = 1.0

# H = ℏω(a†a + 1/2)
# 基态波函数 ψ₀(x) = (mω/πℏ)^(1/4) exp(-mωx²/2ℏ)
def psi_0(x):
    return (m_osc * omega / (math.pi * hbar))**0.25 * \
           math.exp(-m_osc * omega * x**2 / (2 * hbar))

def psi_1(x):
    """第一激发态 ψ₁ = √2 (mω/ℏ)^(1/2) x · ψ₀"""
    alpha = math.sqrt(m_osc * omega / hbar)
    return math.sqrt(2) * alpha * x * psi_0(x)

# 正交性验证: ∫ψ₀·ψ₁ dx = 0
N_pts = 10000
x_max = 10.0
dx_osc = 2 * x_max / N_pts
overlap = sum(psi_0(x) * psi_1(x) * dx_osc
              for x in [-x_max + i*dx_osc for i in range(N_pts)])
print("=== 谐振子 ===")
print(f"⟨0|1⟩ = {overlap:.8f} (应=0, 正交性 ✓)")

# 升降算符验证: a|0⟩ = 0, a†|0⟩ = |1⟩
# a = √(mω/2ℏ)(x + ip/mω), 在位置表象: aψ = √(mω/2ℏ)(x + ℏ/(mω) d/dx)ψ
# a†ψ = √(mω/2ℏ)(x - ℏ/(mω) d/dx)ψ
def apply_a(psi_func, x, dx=0.001):
    """降算符 a 作用在 ψ 上"""
    dpsi = (psi_func(x+dx) - psi_func(x-dx)) / (2*dx)
    coeff = math.sqrt(m_osc * omega / (2*hbar))
    return coeff * (x * psi_func(x) + hbar/(m_osc*omega) * dpsi)

def apply_a_dag(psi_func, x, dx=0.001):
    """升算符 a† 作用在 ψ 上"""
    dpsi = (psi_func(x+dx) - psi_func(x-dx)) / (2*dx)
    coeff = math.sqrt(m_osc * omega / (2*hbar))
    return coeff * (x * psi_func(x) - hbar/(m_osc*omega) * dpsi)

# a|0⟩ 应该 = 0
a_psi0 = sum(abs(apply_a(psi_0, x))**2 * dx_osc
             for x in [-x_max + i*dx_osc for i in range(N_pts)])
print(f"⟨0|a†a|0⟩ = {a_psi0:.8f} (应=0, 基态被湮灭 ✓)")

# a†|0⟩ = |1⟩ → ⟨0|a†a|0⟩... 不对，验证 a†|0⟩ = |1⟩
# 检查 a†|0⟩ 正比于 ψ₁
ratio_list = []
for x in [0.3, 0.5, 0.7, 1.0, 1.5]:
    val_a_dag = apply_a_dag(psi_0, x)
    val_psi1 = psi_1(x)
    if abs(val_psi1) > 1e-10:
        ratio_list.append(val_a_dag / val_psi1)
print(f"a†|0⟩ / |1⟩ 在各点的比值: {[f'{r:.4f}' for r in ratio_list]}")
print(f"  → 应全部相同（=1），验证 a†|0⟩ = |1⟩ ✓")

print(f"\n能级: E_n = ℏω(n + 1/2)")
for n in range(5):
    print(f"  E_{n} = {n + 0.5:.1f} ℏω")

# 零点能反直觉
print(f"\n反直觉: E_0 = 0.5 ℏω > 0（零点能）")
print(f"  经典振子最低能量 = 0（粒子停在原点）")
print(f"  量子禁止 Δx=0 且 Δp=0 → 残留 '量子涨落'")
```

---

## 习题

### 基础题（Townsend / Griffiths 级别）

**P1.** 用不确定性原理 $\Delta x \cdot \Delta p \geq \hbar/2$ 估算氢原子基态能量（不解 Schrödinger 方程）。提示：$E = p^2/2m - e^2/(4\pi\epsilon_0 r)$，令 $\Delta x \sim r$，$\Delta p \sim p$，对 $r$ 最小化。

**P2.** Stern-Gerlach 实验：银原子束经过 $z$ 方向非均匀磁场后分裂成两束。若再加一个 $x$ 方向的 SG 装置，描述结果。这就是 Feynman Vol 3 第 1-5 章的核心实验序列。

**P3.** 证明谐振子的基态满足最小不确定性：$\Delta x \cdot \Delta p = \hbar/2$。

### 进阶题（Sakurai 级别）

**P4.** 用升降算符推导谐振子的波函数 $\psi_n(x)$。从基态 $\psi_0(x) = (m\omega/\pi\hbar)^{1/4}e^{-m\omega x^2/2\hbar}$ 出发，用 $a^\dagger$ 递推到 $|n\rangle$。

**P5.** 角动量叠加：两个自旋 $1/2$ 粒子耦合成总自旋 $S=1$（三重态）和 $S=0$（单态）。写出 CG 系数表。证明单态是纠缠态（不可分解为直积）。

**P6.**（微扰）谐振子加微扰 $H' = \frac{1}{2}\epsilon x^4$。求基态能量的一级和二级修正。

### 挑战题

**P7.** **路径积分**（Feynman 的方法）：自由粒子的传播子 $K(x_f, t_f; x_i, t_i)$ 可通过对所有路径求和得到：

$$K = \int_{x_i}^{x_f} \mathcal{D}[x(t)]\,e^{iS[x(t)]/\hbar}$$

证明自由粒子的传播子为：

$$K = \sqrt{\frac{m}{2\pi i\hbar T}}\,\exp\frac{im(x_f-x_i)^2}{2\hbar T}$$

这是 Feynman 在 Caltech 的工作的核心——也是 QFT 的语言基础。

**P8.** **隧穿效应**：用 WKB 近似计算矩形势垒（高 $V_0$，宽 $a$）的透射系数 $T$。验证 $T \propto e^{-2\kappa a}$，$\kappa = \sqrt{2m(V_0-E)}/\hbar$。这是扫描隧道显微镜（STM）的物理基础。

---

## 知识地图与跨课程联系

```
Schrödinger 方程 (Ph 2a)
    │
    ├──→ 标准问题 (势阱/谐振子/氢原子)
    │         │
    │    Feynman Lectures Vol 3 (Caltech 精神)
    │         │
    ├──→ 自旋与角动量 (Ph 12b, Townsend)
    │         │
    │    自旋统计定理 → Bose-Einstein / Fermi-Dirac (Ph 127)
    │
    ├──→ 微扰理论 (Ph 125, Sakurai)
    │         │
    │    Fermi 黄金定则 → 激光物理 / 光谱学
    │
    └──→ 路径积分 → 量子场论 (Ph 237, Peskin & Schroeder)
```

**关键连接**：
- 自旋 $1/2$ → 量子信息（Caltech Ph 115, Nielsen & Chuang）
- 谐振子升降算符 → QFT 中的粒子产生/湮灭
- 氢原子波函数 → 原子光谱 → 化学（化学键 = 分子轨道 = QM）
- 路径积分 → Feynman 的 Caltech 遗产 → QFT 的标准语言

---

## 参考与延伸阅读

| 教材 | 章节 | 重点 |
|------|------|------|
| Feynman Lectures Vol 3 | Ch 1-5（自旋/SG）、Ch 7-8（Schr 方程）、Ch 10-11（角动量）、Ch 16（自旋耦合）| Caltech 一年级必读 |
| Townsend *A Modern Approach to QM* 2ed | Ch 1-2（自旋）、Ch 5-6（谐振子/三维）、Ch 10-11（微扰）| Ph 12b 主教材 |
| Sakurai & Napolitano *Modern QM* 3ed | Ch 1（ket 形式/自旋）、Ch 2（量子动力学）、Ch 5（微扰）| Ph 125 研究生标准 |
| Cohen-Tannoudji *Quantum Mechanics* | Ch 5-7（谐振子/角动量/氢原子）| 参考书，最详尽 |

> **Feynman 的话**（Caltech 1964）：*"I think I can safely say that nobody understands quantum mechanics."* 但 Feynman 的理解比任何人都深——他的路径积分表述是理解量子力学最物理化的方式。

---

*本文件属于 top-physics-courses/caltech-physics Phase 1。对应课程 Ph 2a → Ph 12b → Ph 125。*

---

## 🎯 费曼式入口（白话版）

> **一句话解释**：量子力学告诉你，世界的底层不是"确定"而是"概率"——粒子不是一颗小弹珠，而是一团会分身、会干涉的概率云。
>
> **生活类比**：经典世界像台球——你精确知道每颗球在哪、去哪。量子世界像一团雾——你只能说"它大概率在这"，而且**你越想知道它的位置，就越不知道它的速度**。更诡异的是，这团雾能"同时穿过两条缝"和自己干涉。
>
> **反直觉发现（啊哈时刻）**：
> - **粒子同时走多条路**：双缝实验里，哪怕一次只发一个电子，累积久了照样出现干涉条纹——电子**自己和自己干涉**。Feynman 说这是量子力学"唯一的奥秘"。
> - **零点能：粒子永远在抖**：谐振子最低能量不是 0，而是 $\frac{1}{2}\hbar\omega$。绝对静止被不确定性原理禁止——这就是为什么液氦在常压下永远不凝固。
> - **测量改变现实**：测 $S_z$ 得到 $+\hbar/2$ 后，再测 $S_x$，原来的 $S_z$ 信息"消失"了——测量不是"看"系统，而是"创造"系统的状态。Feynman 说："没有人真正理解量子力学。"

---

## 🔗 衔接：从哪来，到哪去

### 前置（你需要先会什么）
- **Ph 1a/1b 经典力学 + 电磁学**：哈密顿量 $H=T+V$ 是量子力学的出发点
- **Ph 106 线性代数**：本征值、本征矢、厄米矩阵、酉变换——量子力学的数学语言
- **Ph 106 复变 + 特殊函数**：概率幅是复数，氢原子需要球谐函数

### 量子力学的"危机"（为什么需要它）
- **经典物理的崩塌**：
  - 黑体辐射紫外灾变（Rayleigh-J Jeans 发散）
  - 原子不坍缩（按拉莫尔公式，电子 $10^{-11}$ s 内坠入核）
  - 光电效应（光强不影响电子能量，只有频率）
- **解决 → 量子化**：Planck $E=h\nu$ + Einstein 光子 + Bohr 轨道 + de Broglie 波 → Schrödinger 方程
- **新危机**：Schrödinger 方程是非相对论的，且无法描述粒子产生湮灭
- **解决 → 量子场论**（Ph 237）：把波函数升级为场算符，狄拉克方程 + QED

### 后续（量子通向哪里）
- 路径积分（Feynman）→ **量子场论的标准语言**（Ph 237, Peskin & Schroeder）
- 自旋 1/2 + 纠缠 → **量子信息与计算**（Caltech Ph 115, IQIM, Preskill）
- 谐振子升降算符 → **QFT 的粒子产生湮灭**
- 氢原子波函数 → **化学键 / 原子光谱 / 固体能带**（Ph 126）

---

## 🏭 理论联系实际：5 个应用

1. **半导体与晶体管**（量子能带的直接产物）：硅的能带结构决定了导带/价带，掺杂形成 PN 结——所有芯片、电脑、手机的物理基础。没有量子力学就没有现代文明。
2. **激光**（受激辐射 + 谐振腔）：Einstein 1917 预言受激辐射，Fermi 黄金定则算跃迁速率——激光是量子力学最直接的工程产物。
3. **MRI 核磁共振**（自旋 + 塞曼分裂）：质子自旋在磁场中分裂能级，射频脉冲共振翻转——量子力学让医生看见人体内部。
4. **量子计算**（叠加 + 纠缠）：Caltech IQIM 的 Preskill 提出 NISQ 时代概念；2024 Google Willow 芯片实现纠错突破；2026-03 Caltech+Oratomic 证明 10000 个可重构原子比特即可运行 Shor 算法。
5. **扫描隧道显微镜 STM**（量子隧穿）：$T\propto e^{-2\kappa a}$——电子隧穿过真空缝隙，能"看见"单个原子。IBM 用 STM 拼出原子 logo。

---

## 🔬 最新研究前沿（2024-2026）

1. **Caltech IQIM：10000 原子比特实现 Shor 算法**（2026-03-31）：Caltech 与初创公司 Oratomic 合作的理论-实验联合工作证明，**仅需 ~10000 个可重构原子量子比特**即可运行 Shor 大数分解算法——远低于此前估计。这是通向实用量子计算的重要里程碑。[IQIM Caltech 2026-03-31]
2. **量子学习优势的光子验证**（2025-09-26）：Caltech 参与的国际团队在可扩展光子平台上展示了**量子学习优势**——用量子方法表征物理系统只需数小时，而最优经典方法需 **2000 万年**。[IQIM Caltech 2025-09-26]
3. **Google Willow 量子纠错突破**（2024-12）：Google 宣布 Willow 芯片实现"表面码低于阈值"——增加量子比特数反而**降低**逻辑错误率，这是 30 年来量子纠错的关键转折。Caltech Preskill 是该领域的理论奠基者之一。
4. **魔角三层石墨烯的超导机理**（2026-02-04）：Caltech Nadj-Perge 实验室用 STM 首次分辨出魔角扭曲三层石墨烯的超导能隙与关联能隙——为非常规超导（可能是拓扑超导）机理提供关键实验证据。[IQIM Caltech 2026-02-04]
5. **IQIM 25 周年 + 量子科学工程 Minor**（2025-11-07）：Caltech 的 IQIM（2000 年创立，Preskill/Kitaev 领衔）庆祝 25 年，并设立本科量子科学工程辅修——量子信息从前沿研究走向系统化教学。[IQIM Caltech 2025-11-07]

---

## 🗺️ 学习 Roadmap（Caltech 路径）

```
Ph 1c/2a 引言 (Feynman Vol 1 Ch 38 量子行为)  ← Caltech 大一
    │   • 掌握：双缝实验的概率幅直觉
    │   • ✅ 知识检查：解释为什么遮住一条缝反而让屏幕某些点更亮
    │
    ▼
Ph 2a  量子力学入门 (Feynman Vol 3, Griffiths)  ← 大二
    │   • 掌握：Schrödinger 方程、势阱、谐振子、氢原子
    │   • ✅ 知识检查：用升算符推出谐振子前 3 个波函数
    │
    ▼
Ph 12b  自旋与角动量 (Townsend)  ← 大二 Honors
    │   • 掌握：Stern-Gerlach、Pauli 矩阵、CG 系数、微扰
    │   • ✅ 知识检查：解释连续测 Sx→Sz 为什么顺序不可交换
    │
    ▼
Ph 125abc  高等量子力学 (Sakurai)  ← 研究生
    │   • 掌握：ket 形式、路径积分、散射理论、密度矩阵
    │   • ✅ 知识检查：写出自由粒子 Feynman 传播子
    │
    ▼
→ Ph 237 量子场论 (路径积分 → QED → 规范理论)
→ Ph 115 量子信息与计算 (IQIM, Preskill《Quantum Computation》讲义)
→ Ph 229 量子多体理论 (凝聚态 + 超冷原子)
```

**关键里程碑**：能否用 Feynman 路径积分的"驻相近似"解释为什么宏观世界看起来服从经典力学（$\hbar\to 0$ 时只有经典路径幸存），是检验你是否理解量子-经典桥梁的试金石。Caltech 的 Feynman 正是用这个洞察统一了两个世界。
