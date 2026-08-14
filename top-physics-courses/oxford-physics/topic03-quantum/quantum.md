# Topic 03 — 量子力学：从薛定谔到微扰

> **Oxford MPhys · Year 2 / Year 3 Quantum Mechanics**
> 教材：R. Shankar *Principles of Quantum Mechanics* 2ed (1994) — Oxford 全英标准
> 覆盖：薛定谔方程、势阱/谐振子/氢原子、角动量/自旋、微扰理论

---

## 目录

1. [课程定位与 Oxford 量子序列](#1-课程定位与-oxford-量子序列)
2. [公理与数学结构](#2-公理与数学结构)
3. [一维问题：势阱与谐振子](#3-一维问题势阱与谐振子)
4. [角动量与自旋](#4-角动量与自旋)
5. [氢原子](#5-氢原子)
6. [微扰理论](#6-微扰理论)
7. [反直觉实验 (Python)](#7-反直觉实验-python)
8. [Tutorial 习题](#8-tutorial-习题)
9. [局限与延伸阅读](#9-局限与延伸阅读)

---

## 1. 课程定位与 Oxford 量子序列

| 年级 | 课程 | 教材 | 重点 |
|------|------|------|------|
| Y1 | Quantum (intro) | Rae | 历史动机 + 黑体辐射 + 德布罗意 |
| **Y2** | **Quantum Mechanics** | **Shankar Ch.1-15** | **公理体系、一维问题、谐振子、氢原子、自旋** |
| Y3 | Quantum | Sakurai / Cohen-Tannoudji | 角动量加法、散射、Dirac 方程 |
| Y4 | Advanced QM | Sakurai | 路径积分、量子信息、QFT 入门 |

**为何 Oxford 选 Shankar？** Shankar 从**线性代数公理**出发（Hilbert 空间、算子），不像 Griffiths 那样从历史实验先讲。这与 Oxford 强调数学严谨的传统契合——学生在 Y1 数学方法已掌握线性代数与微分方程，Y2 直接进入 Dirac 记号。

---

## 2. 公理与数学结构

### 2.1 四公理 (Shankar §1-4)

**公理一**：系统状态由 Hilbert 空间 $\mathcal{H}$ 中的**右矢** $|\psi\rangle$ 描述（模长归一）。

**公理二**：可观测量对应**厄米算子** $\Omega=\Omega^\dagger$，本征方程 $\Omega|\omega\rangle=\omega|\omega\rangle$ 给出可能测量值。

**公理三**（Born 规则）：测量 $\Omega$ 得本征值 $\omega$ 的概率 $P(\omega)=|\langle\omega|\psi\rangle|^2$。

**公理四**（测量塌缩）：测量后状态投影到对应本征矢。

**公理五**（时间演化）：态满足薛定谔方程
$$
\boxed{\;i\hbar\frac{d}{dt}|\psi(t)\rangle=H|\psi(t)\rangle\;}
$$

### 2.2 不确定性关系 (Shankar §9)

对任意两厄米算子 $\Omega,\Lambda$：
$$
\boxed{\;\Delta\Omega\cdot\Delta\Lambda\ge\frac12|\langle[\Omega,\Lambda]\rangle|\;}
$$

对位置-动量 $[\hat x,\hat p]=i\hbar$：$\Delta x\,\Delta p\ge\hbar/2$。这不是测量精度问题，而是**态本身的内禀性质**。

### 2.3 薛定谔 vs 海森堡绘景

- **薛定谔绘景**：态变 $|\psi(t)\rangle=e^{-iHt/\hbar}|\psi(0)\rangle$，算子不变。
- **海森堡绘景**：态不变，$\Omega_H(t)=e^{iHt/\hbar}\Omega_S e^{-iHt/\hbar}$，满足 $\frac{d\Omega_H}{dt}=\frac{i}{\hbar}[H,\Omega_H]$。

两者等价，但海森堡绘景与经典力学 Poisson 括号 $\{\cdot,\cdot\}\to\frac{1}{i\hbar}[\cdot,\cdot]$ 直接对应——这是量子化的**正则形式**（Dirac 公式）。

---

## 3. 一维问题：势阱与谐振子

### 3.1 无限深势阱 (Shankar §5.2)

$V(x)=0$ for $0<x<L$，边界 $\psi(0)=\psi(L)=0$。解：
$$
\psi_n(x)=\sqrt{\frac{2}{L}}\sin\frac{n\pi x}{L},\quad E_n=\frac{n^2\pi^2\hbar^2}{2mL^2},\quad n=1,2,\dots
$$

**反直觉**：最低能态 $E_1\neq0$——零点能是测不准原理的直接后果。

### 3.2 简谐振子 (Shankar §7) — 最重要的一维问题

哈密顿 $H=\frac{p^2}{2m}+\frac12 m\omega^2 x^2$。Shankar 用**算子代数**（Dirac 法）：

定义升降算子：
$$
a=\sqrt{\frac{m\omega}{2\hbar}}\left(x+\frac{ip}{m\omega}\right),\quad a^\dagger=\sqrt{\frac{m\omega}{2\hbar}}\left(x-\frac{ip}{m\omega}\right)
$$

对易子 $[a,a^\dagger]=1$，$H=\hbar\omega(a^\dagger a+\tfrac12)$。基态 $a|0\rangle=0$，激发态 $|n\rangle=(a^\dagger)^n|0\rangle/\sqrt{n!}$：

$$
\boxed{\;E_n=\hbar\omega\left(n+\tfrac12\right),\quad n=0,1,2,\dots\;}
$$

零点能 $E_0=\hbar\omega/2$。

**为何这一节如此重要？** 升降算子的代数结构在后续到处复用：
- 角动量 $L_\pm$（§4）
- 电磁场量子化（每个波模是一个谐振子，Y4 QFT）
- 玻色子产生/湮灭（Y2 统计力学，§Bose-Einstein）
- 相干态（激光、量子光学 Y3）

### 3.3 自由粒子与波包 (Shankar §5.3-5.4)

自由粒子本征态 $e^{ikx}$ 不可归一化，物理态是波包：
$$
\psi(x,0)=\int \phi(k) e^{ikx}\,dk
$$

高斯波包演化：宽度 $\sigma(t)=\sqrt{\sigma_0^2+(\hbar t/2m\sigma_0)^2}$——**扩散**，且扩散速率由 $\hbar/m$ 决定。电子比原子扩散快 $10^5$ 倍（质量比）。

---

## 4. 角动量与自旋

### 4.1 轨道角动量算子

$$
L_x=yp_z-zp_y,\ \ldots,\quad [L_x,L_y]=i\hbar L_z\ \text{(及循环)}
$$

球坐标下 $L^2$ 与 $L_z$ 共同本征函数为球谐函数 $Y_l^m(\theta,\phi)$：
$$
L^2 Y_l^m=\hbar^2 l(l+1)Y_l^m,\quad L_z Y_l^m=\hbar m\,Y_l^m,\quad l=0,1,\dots,\ m=-l,\dots,l
$$

### 4.2 一般角动量与自旋 (Shankar §12)

定义 $J_\pm=J_x\pm iJ_y$，由 $[J_z,J_\pm]=\pm\hbar J_\pm$ 和 $[J_+,J_-]=2\hbar J_z$ 推出：
$$
\boxed{\;J^2|j,m\rangle=\hbar^2 j(j+1)|j,m\rangle,\quad J_z|j,m\rangle=\hbar m|j,m\rangle\;}
$$

允许 $j=0,\tfrac12,1,\tfrac32,\dots$，$m=-j,\dots,j$。**半整数 $j$ 不出现在轨道角动量**——只有自旋。

**自旋 $\tfrac12$**：Pauli 矩阵
$$
\sigma_x=\begin{pmatrix}0&1\\1&0\end{pmatrix},\ \sigma_y=\begin{pmatrix}0&-i\\i&0\end{pmatrix},\ \sigma_z=\begin{pmatrix}1&0\\0&-1\end{pmatrix},\quad \sigma_i\sigma_j=\delta_{ij}I+i\epsilon_{ijk}\sigma_k
$$

### 4.3 角动量加法 (Shankar §15)

$\mathbf{J}=\mathbf{J}_1+\mathbf{J}_2$，总角动量量子数 $j\in\{|j_1-j_2|,|j_1-j_2|+1,\dots,j_1+j_2\}$。

CG 系数 $\langle j_1 m_1 j_2 m_2|jm\rangle$ 实现基变换。**典型例**：两自旋 $\tfrac12$ 耦合，单态（$j=0$）与三重态（$j=1$）——氢原子精细/超精细结构的根据。

### 4.4 自旋轨道耦合 (Shankar §15.4)

电子在原子核场中，相对论效应给出：
$$
H_{\text{SO}}=\frac{1}{2m^2c^2}\frac{1}{r}\frac{dV}{dr}\mathbf{L}\cdot\mathbf{S}
$$

这耦合使 $\mathbf{L},\mathbf{S}$ 不再各自守恒，但 $\mathbf{J}=\mathbf{L}+\mathbf{S}$ 守恒。这就是为何 Y3 用 $|j,m_j\rangle$ 而非 $|m_l,m_s\rangle$ 标记氢原子态。

---

## 5. 氢原子 (Shankar §13)

### 5.1 径向方程

中心势 $V(r)=-e^2/(4\pi\epsilon_0 r)$ 下分离变量：$\psi_{nlm}=R_{nl}(r)Y_l^m$。径向方程引入 $u=rR$：

$$
-\frac{\hbar^2}{2m}\frac{d^2u}{dr^2}+\left[V(r)+\frac{\hbar^2 l(l+1)}{2mr^2}\right]u=Eu
$$

有效势含**离心势** $\propto 1/r^2$。

### 5.2 能级 (Shankar §13.1)

边界条件 + 级数收敛给出：
$$
\boxed{\;E_n=-\frac{me^4}{2(4\pi\epsilon_0)^2\hbar^2}\cdot\frac{1}{n^2}=-\frac{13.6\,\text{eV}}{n^2},\quad n=1,2,\dots\;}
$$

注意：能级只依赖 $n$（**偶然简并**，源于 Runge-Lenz 隐对称，Y3 才讲清）。

### 5.3 波函数

基态 $R_{10}=2a_0^{-3/2}e^{-r/a_0}$，玻尔半径 $a_0=4\pi\epsilon_0\hbar^2/(me^2)\approx0.529$ Å。

> **Oxford 反直觉题**：在经典力学中电子不会出现在核内（离心势太高），但量子波函数 $|\psi_{1s}(0)|^2=1/(\pi a_0^3)\neq0$——这是 p 轨道不可能、s 轨道可能的，**也是放射性 β 衰变（核内 p→n+e）需要 s 电子参与**的根据。

---

## 6. 微扰理论

### 6.1 非简并微扰 (Shankar §16.1)

$H=H_0+\lambda V$，$H_0|n^0\rangle=E_n^0|n^0\rangle$。能量修正：
$$
\boxed{\;E_n=E_n^0+\lambda V_{nn}+\lambda^2\sum_{k\neq n}\frac{|V_{kn}|^2}{E_n^0-E_k^0}+\mathcal{O}(\lambda^3)\;}
$$

态修正：$|n\rangle=|n^0\rangle+\lambda\sum_{k\neq n}\frac{V_{kn}}{E_n^0-E_k^0}|k^0\rangle+\cdots$。

**适用条件**：$|V_{kn}/(E_n^0-E_k^0)|\ll1$ 对所有 $k\neq n$。**简并必须先用简并微扰**对角化（§6.2）。

### 6.2 简并微扰 (Shankar §16.2)

在简并子空间内对角化 $V$ 矩阵，本征值即一级能量修正。

**Stark 效应**（氢 $n=2$，4 重简并）：在一阶电场微扰下分裂为三条（一个 $m=0$ 不动，两个 $m=\pm1$ 简并）。线性 Stark 效应**仅**氢原子（因偶然简并），其他原子是二级（平方）效应。

### 6.3 氢原子精细结构 (Shankar §17)

三项修正：
1. 相对论动能 $-\frac{p^4}{8m^3c^2}$
2. 自旋-轨道 $H_{\text{SO}}$
3. Darwin 项（s 轨道穿透核）

合并给出精细结构能量：
$$
E_{n,j}=E_n^0\left[1+\frac{\alpha^2}{n^2}\left(\frac{n}{j+1/2}-\frac34\right)\right]
$$

精细结构常数 $\alpha=e^2/(4\pi\epsilon_0\hbar c)\approx1/137$。

---

## 7. 反直觉实验 (Python)

> **谐振子升降算子的数值实现**：本实验从 $H=\hbar\omega(a^\dagger a+\tfrac12)$ 出发，用矩阵表示验证 $E_n=\hbar\omega(n+\tfrac12)$，并展示基态波函数与算子作用。

```python
#!/usr/bin/env python3
"""
一维谐振子: 升降算子代数的数值实现
Shankar Principles of QM §7
纯标准库, 零依赖。运行: python3 harmonic_oscillator.py
"""
import math

N = 30  # 截断维数

# 单位: hbar = m = omega = 1
# a_{ij} = sqrt(i) delta_{i, j+1}  (i 从 1 编号; 我们用 0 起索引)
def make_a(N):
    a = [[0.0]*N for _ in range(N)]
    for i in range(1, N):
        a[i-1][i] = math.sqrt(i)   # <i-1| a |i> = sqrt(i)
    return a

def dag(a, N):
    return [[a[j][i] for j in range(N)] for i in range(N)]

def matmul(A, B, N):
    return [[sum(A[i][k]*B[k][j] for k in range(N)) for j in range(N)] for i in range(N)]

def matadd(A, B, N, c=1.0, d=1.0):
    return [[c*A[i][j]+d*B[i][j] for j in range(N)] for i in range(N)]

def diag(A, N):
    return [A[i][i] for i in range(N)]

a = make_a(N)
ad = dag(a, N)
# H = a^dag a + 1/2
ada = matmul(ad, a, N)
for i in range(N):
    ada[i][i] += 0.5

print("="*56)
print("一维谐振子: 数值 Hamiltonian 谱")
print("H = a†a + 1/2  (单位 hbar = omega = 1)")
print("="*56)
print(f"截断维数 N = {N}, 取前 10 个本征值:")
print()

for i in range(10):
    exact = i + 0.5
    numer = ada[i][i]
    print(f"  n={i}:  数值 E_n = {numer:8.4f},   精确 = {exact:8.4f},   差 = {numer-exact:.2e}")

print()
print("验证对易子 [a, a†] = I (前 5x5 块):")
comm = matadd(matmul(a, ad, N), matmul(ad, a, N), N, c=1.0, d=-1.0)
for i in range(5):
    row = [f"{comm[i][j]:5.2f}" for j in range(5)]
    print("  " + " ".join(row))

print()
print("基态 |0> = 高斯波函数 psi_0(x) = (1/pi)^{1/4} exp(-x^2/2)")
print("验证 a|0> = 0:")
# a 作用在 |0> (列向量 (1,0,0,...)) 给出第 0 列
col0 = [a[i][0] for i in range(N)]
norm = math.sqrt(sum(x*x for x in col0))
print(f"  || a|0> || = {norm:.2e}  (应为 0)")

print()
print("反直觉发现:")
print("  1. H 本征值精确等于 n+1/2, 完全无离散化误差(代数法超越有限差分)")
print("  2. a|0> = 0 解出基态为高斯, 这是量子涨落的'零点振动'")
print("  3. 量子谐振子的'零点能' E0 = hbar*omega/2 不是数学技巧,")
print("     是 Casimir 效应、Hawking 辐射、真空结构的物理实在")
print()
print("工程意义: 该算子代数直接映射到")
print("  - 量子电动力学: 每个电磁波模是一个谐振子")
print("  - 凝聚态: 声子(晶格振动量子)用相同代数")
print("  - 量子计算: 相干态 |alpha> = e^{-|alpha|^2/2} sum (alpha^n/sqrt(n!)) |n>")
```

**预期输出**：$E_n=n+0.5$ 精确（数值差 $<10^{-15}$），$[a,a^\dagger]=I$，$a|0\rangle$ 范数 $\approx0$。

---

## 8. Tutorial 习题

### T1. 测不准原理的最小波包 (Shankar Ex.9.2)

高斯波包 $\psi(x)=(2\pi\sigma^2)^{-1/4}e^{-x^2/(4\sigma^2)}$。

(a) 验证 $\Delta x=\sigma$。

(b) 在动量空间 $\phi(p)$ 也是高斯，证明 $\Delta p=\hbar/(2\sigma)$，从而 $\Delta x\Delta p=\hbar/2$——**饱和**测不准下界。

> **导师追问**：相干态 $|\alpha\rangle$（谐振子基态平移）也饱和下界。为何压缩态 $|\xi\rangle$ 可以让 $\Delta x<\hbar/(2\Delta p)$ 但代价是 $\Delta p$ 变大？引力波探测器 LIGO 如何用压缩光降低量子噪声？

### T2. 氢原子基态期望值 (Shankar Prob.13.2)

基态 $\psi_{100}$。

(a) 计算 $\langle r\rangle=\tfrac32 a_0$，$\langle r^2\rangle=3a_0^2$，$\langle 1/r\rangle=1/a_0$。

(b) 由 Virial 定理 $\langle T\rangle=-E_1$，$\langle V\rangle=2E_1$ 验证（注意 $E_1<0$）。

> **导师追问**：氢原子在 1s 态有非零的 $\langle p^4\rangle$，导致精细结构的第一项修正。用 Feynman-Hellmann 定理 $\frac{dE_n}{d\lambda}=\langle\frac{\partial H}{\partial\lambda}\rangle$ 估算此项。

### T3. 自旋 1/2 在磁场中的进动 (Shankar §14.5)

电子在均匀磁场 $\mathbf{B}=B_0\hat{\mathbf{z}}$ 中，$H=-\gamma\mathbf{S}\cdot\mathbf{B}$，$\gamma=g e/(2m)$。

(a) 初态 $|\psi(0)\rangle=|\uparrow_x\rangle=\tfrac1{\sqrt2}(|+\rangle+|-\rangle)$，求 $|\psi(t)\rangle$。

(b) 证明 $\langle S_x(t)\rangle=\tfrac{\hbar}{2}\cos\omega_L t$，$\omega_L=g e B_0/(2m)$ 为拉莫尔频率。

> **导师追问**：若 $\mathbf{B}$ 旋转而非静止（与自旋同方向旋转），会发生什么？这是核磁共振 (NMR) 的物理基础——你能写出共振条件吗？

### T4. 氦原子基态变分法 (Shankar §16.4 标志例)

氦原子核电荷 $Z=2$，两电子。

(a) 用无屏蔽的类氢乘积态 $\psi=\phi_{100}^{(Z)}(1)\phi_{100}^{(Z)}(2)$ 作试探，变分给出能量上界 $E=-74.8$ eV（实验 $-79.0$ eV）。

(b) 引入有效核电荷 $Z^*$ 作变分参数，证明最优 $Z^*=Z-5/16=27/16$，能量 $-77.5$ eV——大幅改善。

> **导师追问**：为何 $Z^*<Z$？这如何用「电子屏蔽」直觉解释？为何变分法永远给**上界**？这与微扰法给「近似」而无误差保证形成对比。

---

## 9. 局限与延伸阅读

### 局限

1. **Shankar Y2 不讲路径积分**——Feynman 形式留到 Y4 Theoretical Physics。
2. **多体问题不在 Y2 范围**：氦原子变分只是入门，真正的多体（Hartree-Fock、密度泛函）要到 Y4 Condensed Matter。
3. **不涉及相对论量子力学**：Dirac 方程、反粒子、自旋的相对论起源是 Y3/Y4 内容。
4. **测量公理仍有哲学争议**：塌缩是物理过程还是信息更新？Oxford 的 Vlatko Vedral、Jonathan Oppenheim 等在量子信息方向给出新视角。

### 延伸阅读

- **Griffiths & Schroeter** *Introduction to Quantum Mechanics* 3ed — 比 Shankar 更直观，作为对照阅读。
- **Sakurai & Napolitano** *Modern Quantum Mechanics* 3ed — Oxford Y3 主教材，从对称性出发。
- **Cohen-Tannoudji, Diu & Laloë** *Quantum Mechanics* — 法国经典，章节短小适合 tutorial 查阅。
- **Dirac** *The Principles of Quantum Mechanics* — Oxford 出品，bra-ket 记号的发源地。
- **Feynman & Hibbs** *Quantum Mechanics and Path Integrals* — Y4 路径积分的预备。

---

**版本**：v1.1 (2026-08-12) · Oxford MPhys Phase 1 Topic 03
**依据**：SURVEY.md Oxford Y2 课程表 + Shankar (1994) 2ed

---

## 🎯 费曼式入口（白话版）

> **一句话解释**：量子力学是研究「极小尺度下，确定性消失、概率成为基本」的物理——电子不再是小球，而是弥散的「概率波」，测量前它没有确定位置。
>
> **生活类比**：把电子想象成「一团雾」——不是在哪，而是「这里 30%、那里 70%」。你用手电一照（测量），雾瞬间凝结成一个点——但凝结到哪是掷骰子决定的，连上帝都猜不到。谐振子的升降算子就像楼梯：粒子只能站在某一阶（$E_n=\hbar\omega(n+\tfrac12)$），不能悬空，最底层（$n=0$）也有一份「零点能」——这是真空永不寂静的根源。
>
> **反直觉发现**：
> - **零点能不是数学技巧**：$E_0=\hbar\omega/2$ 是物理实在——它产生 Casimir 力（两块不带电的平行板会被真空涨落推到一起）、Hawking 辐射（黑洞会蒸发）。
> - **1s 电子在原子核里**：经典力学里电子进不了核（离心势太高），但 $|\psi_{1s}(0)|^2\ne0$——这是 β 衰变需要 s 电子参与的根据。
> - **自旋是相对论效应**：Dirac 方程把自旋「自然涌现」——它是时空对称性（旋转群表示论）的必然结果，而不是把电子想象成「自转小球」。

---

## 🔗 衔接：从哪来，到哪去

### 前置
- **Y1 Quantum intro**（Rae）：黑体辐射、光电效应、德布罗意波——历史动机
- **Y1/Y2 Mathematical Methods**（RHB）：线性代数（本征值/本征矢、厄米矩阵）、ODE 级数解（Frobenius）、复变
- **Y2 Classical Mechanics**（Topic 01）：哈密顿力学——Poisson 括号 $\{\cdot,\cdot\}\to\frac{1}{i\hbar}[\cdot,\cdot]$ 是量子化的正则形式

### 本课的危机
- **测不准不是测量精度问题**：$\Delta x\Delta p\ge\hbar/2$ 是态本身的内禀性质，与仪器无关。压缩态可以让 $\Delta x$ 更小，但 $\Delta p$ 必然变大。
- **谐振子的算子代数超越有限差分**：用 $a,a^\dagger$ 代数得到 $E_n$ 完全无离散化误差——这是「对称性比方程更强大」的第一课。
- **测量塌缩的哲学争议**：塌缩是物理过程还是信息更新？Oxford 的 Vedral、Oppenheim 等在量子信息方向给出新视角。

### 新危机
- **多体问题在 Y2 范围外**：氦原子变分只是入门，真正的多体（Hartree-Fock、DFT）要到 Y4 凝聚态（Topic 06）。
- **Shankar 不讲路径积分**：Feynman 形式留到 Y4 Theoretical Physics——它把量子振幅与经典作用量直接联系。
- **不涉及相对论量子力学**：Dirac 方程、反粒子、自旋的相对论起源是 Y3/Y4 内容。

### 后续
- **Y3 Quantum**（Sakurai / Cohen-Tannoudji）：角动量加法、散射、Dirac 方程
- **Y4 Advanced QM**：路径积分、量子信息、QFT 入门
- **Y4 Quantum Information**（Oxford 强项）：Vedral/Oppenheim 的量子计算与量子热力学
- **Y4 Atomic & Laser Physics**：相干态、压缩光、腔 QED

---

## 🏭 理论联系实际：5 个应用

1. **半导体与晶体管**：能带理论（Y3 凝聚态）的量子基础——硅的导带/价带间隙源自薛定谔方程在周期势中的解，整个数字电子学建立于此。
2. **激光**：受激辐射的概念源自 Einstein 1917——相干态 $|\alpha\rangle$（谐振子基态平移）饱和测不准下界，是激光「相位确定」的量子描述。
3. **核磁共振（MRI）**：自旋 1/2 在磁场中的拉莫尔进动（Shankar §14.5）+ 射频脉冲的 Rabi 振荡——医疗 MRI 的全部物理。
4. **量子计算**：量子比特 = 两能级系统（自旋 1/2、离子阱、超导约瑟夫森结）。Oxford Lucas group 用 $^{43}\text{Ca}^+$ 离子做逻辑门——Shankar 的角动量代数就是 gate 操作的数学。
5. **原子钟与 GPS**：铯原子基态超精细跃迁（$9.2\times10^9$ Hz）定义「秒」——精度 $10^{-15}$，是 GPS 定位（需纳秒级时间同步）的物理基础。

---

## 🔬 最新研究前沿（2024-2026）

> 注：firecrawl 搜索返回空数据，以下基于 Oxford Quantum、Google Quantum AI、Nature/Science 公开报道整理。

1. **Google Willow 量子纠错芯片（2024-12）**：105 个物理量子比特实现表面码纠错——增加码距时错误率反而**下降**（越过「纠错阈值」），首次实验演示 logical qubit 比 physical qubit 更可靠。这是容错量子计算的里程碑。
2. **Oxford 离子阱量子计算（2024-2025）**：Lucas group 用 $^{43}\text{Ca}^+$ 与 $^{88}\text{Sr}^+$ 离子链演示高保真度双比特门（$>99.9\%$），并探索可扩展的模块化架构（光子互连连接不同离子阱）。
3. **中性原子量子计算（2024-2025）**：用光镊阵列捕获单个原子（Rb/Cs/Sr），通过 Rydberg 阻塞实现纠缠——Atom Computing、QuEra、Pasqal 等公司竞逐千比特规模，Oxford 亦有相关组。
4. **量子热力学与量子信息（2024-2025）**：Oxford Oppenheim 提出「重力-量子信息」一致性问题，Vedral 探索宏观量子纠缠（纳米机械振子、生物系统）。这是量子力学边界问题的新前沿。
5. **拓扑量子比特的回归（2024-2025）**：Microsoft 的 Majorana 费米子路线在 2023 受挫后，2024-2025 通过更严格的拓扑间隙测量重新推进——若成功，将天然免疫局域噪声。

---

## 🗺️ 学习 Roadmap（Oxford MPhys 路径）

```
Year 1                       Year 2                       Year 3-4
─────                       ─────                       ─────────
Quantum (intro)             Quantum Mechanics           Advanced QM
· 历史 + 黑体辐射           · Shankar 公理体系           · Sakurai: 对称性、散射
· 德布罗意波                · 一维问题、谐振子           · Dirac 方程、反粒子
· 波函数初识                · 氢原子、自旋               · 量子信息 (Y4)
                            · 微扰理论                   · 路径积分 (Y4)
教材: Rae                   教材: Shankar               教材: Sakurai, Feynman & Hibbs
```

**知识检查清单**：
- [ ] 能默写量子力学五公理（Hilbert 空间、厄米算子、Born 规则、塌缩、薛定谔方程）
- [ ] 能用升降算子推出谐振子能级（不写微分方程）
- [ ] 能解释零点能的物理实在性（Casimir、Hawking）
- [ ] 能算氢原子 1s 态的 $\langle r\rangle,\langle 1/r\rangle$
- [ ] 能用变分法估算氦原子基态（含有效核电荷 $Z^*$）
- [ ] 能解释为何量子谐振子代数直接映射到电磁场量子化

**Oxford 特色资源**：
- **Dirac 的遗产**：bra-ket 记号就是 Oxford 出品（Dirac 1930《The Principles of QM》）
- **量子信息重镇**：Vedral（量子纠缠与热力学）、Oppenheim（量子信息与引力）
- **Ion Trap 实验室**：Lucas group 在 Clarendon Lab，本科生 MPhys 项目可参与
