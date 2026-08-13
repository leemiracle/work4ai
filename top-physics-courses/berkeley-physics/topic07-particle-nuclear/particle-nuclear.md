# Topic 07: 粒子物理与核物理 — 标准模型与夸克

> **UC Berkeley 课程映射**：129 (Particles and Nuclei, Griffiths "Introduction to Elementary Particles") → 研究生 237A/B (Quantum Field Theory, Peskin & Schroeder)
>
> **教材体系**：
> - **本科核心**：David J. Griffiths "Introduction to Elementary Particles" 2ed（Berkeley 129 主教材）
> - **核物理补充**：Krane "Introductory Nuclear Physics"（Berkeley 核物理部分）
> - **研究生 QFT**：Peskin & Schroeder "An Introduction to Quantum Field Theory"（Berkeley 237）
> - **进阶粒子物理**：Halzen & Martin "Quarks and Leptons" / Weinberg "The Quantum Theory of Fields"
> - **Berkeley 特色**：与 **LBNL（劳伦斯伯克利国家实验室）** 深度关联——回旋加速器发源地、88-inch Cyclotron、探测器研发

---

## 目录

1. [§1 粒子动物园与历史](#1-粒子动物园与历史)
2. [§2 标准模型](#2-标准模型)
3. [§3 量子电动力学与费曼图](#3-量子电动力学与费曼图)
4. [§4 强相互作用与夸克禁闭](#4-强相互作用与夸克禁闭)
5. [§5 弱相互作用与电弱统一](#5-弱相互作用与电弱统一)
6. [§6 Berkeley 特色：LBNL 与加速器传统](#6-berkeley-特色lbnl-与加速器传统)
7. [习题集](#习题集)
8. [Python 演示](#python-演示)

---

## §1 粒子动物园与历史

### 1.1 从原子到夸克的尺度阶梯

| 尺度 | 物体 | 大小 | 探测工具 |
|------|------|------|---------|
| $10^{-10}$ m | 原子 | 1 Å | X 射线 |
| $10^{-14}$ m | 原子核 | 几 fm | 电子散射 |
| $10^{-15}$ m | 质子/中子 | ~1 fm | 高能电子 |
| $<10^{-18}$ m | 夸克/电子 | 点粒子（无结构）| LHC |

**Rutherford 散射**（1911）：$\alpha$ 粒子被金箔散射，发现原子核——开启了"用散射看内部结构"的范式，至今粒子物理实验的核心方法。

### 1.2 粒子发现时间线

| 年代 | 发现 | 意义 |
|------|------|------|
| 1897 | 电子 (Thomson) | 第一个基本粒子 |
| 1932 | 中子 (Chadwick) | 核结构 |
| 1932 | 正电子 (Anderson) | 反物质 |
| 1936 | μ子 (Anderson) | "谁点了这个？"（I. Rabi）|
| 1947 | π介子 (Powell) | 汤川介子理论验证 |
| 1950s-60s | 强子"动物园" | 几百种强子被发现 |
| 1964 | 夸克模型 (Gell-Mann, Zweig) | 强子的内在结构 |
| 1968 | 质子内部结构 (SLAC) | 夸克实验证据 |
| 1973 | 弱中性流 (CERN) | 电弱统一验证 |
| 1974 | J/ψ 粒子 | 粲夸克 |
| 1979 | 胶子 (PETRA) | 强力载体 |
| 1983 | W/Z 玻色子 (CERN) | 弱力载体 |
| 1995 | 顶夸克 (Tevatron) | 最重夸克 |
| 2000 | τ中微子 | 标准模型最后轻子 |
| 2012 | 希格斯玻色子 (LHC) | 质量起源 |

### 1.3 强子动物园的危机与夸克模型的救赎

1950-60 年代，加速器发现了上百种强子（强相互作用粒子），物理学家被"粒子动物园"淹没——这些粒子之间有什么规律？

**Gell-Mann 与 Zweig（1964）的洞察**：所有强子由更基本的"夸克"组成。

- **重子**（费米子，半整数自旋）= 3 个夸克，如质子 $p = uud$，中子 $n = udd$。
- **介子**（玻色子，整数自旋）= 夸克 + 反夸克，如 $\pi^+ = u\bar{d}$。

**Eightfold Way（八重法）**：Gell-Mann 用 SU(3) 对称性把强子排列成漂亮的图案（如自旋 1/2 重子八重态、自旋 3/2 重子十重态）。十重态的图案预测了 $\Omega^-$ 粒子的存在和质量（1964 实验发现）——这是夸克模型的第一个胜利。

---

## §2 标准模型

### 2.1 基本粒子表

**标准模型 = 3 代费米子 + 4 种规范玻色子 + 希格斯玻色子**

| 类型 | 第一代 | 第二代 | 第三代 |
|------|--------|--------|--------|
| **夸克** | $u$ (上) $d$ (下) | $c$ (粲) $s$ (奇) | $t$ (顶) $b$ (底) |
| **轻子** | $e$ (电子) $\nu_e$ | $\mu$ (μ子) $\nu_\mu$ | $\tau$ (τ子) $\nu_\tau$ |

| 规范玻色子 | 自旋 | 相互作用 | 质量 |
|-----------|------|---------|------|
| 光子 $\gamma$ | 1 | 电磁 | 0 |
| 胶子 $g$ (8种) | 1 | 强 | 0 |
| $W^\pm$ | 1 | 弱 | 80.4 GeV |
| $Z^0$ | 1 | 弱 | 91.2 GeV |
| 希格斯 $H$ | 0 | 质量起源 | 125 GeV |

**反直觉发现**：
1. **三代重复**：为什么有三代完全相同结构但质量递增的粒子？没人知道。这是标准模型最大的未解之谜之一。
2. **质量跨度惊人**：顶夸克 $m_t \approx 173$ GeV，是上夸克 $m_u \approx 2$ MeV 的 **86000 倍**！
3. **中微子质量问题**：标准模型原本设中微子质量为零，但 1998 年中微子振荡实验证明中微子有微小质量——这是标准模型的第一个"裂痕"。

### 2.2 四种基本力

| 力 | 相对强度 | 力程 | 载体 |
|----|---------|------|------|
| 强核力 | 1 | $\sim 1$ fm | 胶子 |
| 电磁力 | $1/137$ | $\infty$ | 光子 |
| 弱核力 | $10^{-6}$ | $\sim 0.001$ fm | W/Z |
| 引力 | $10^{-39}$ | $\infty$ | 引力子（未发现）|

**反直觉**：尽管强力最强，它的力程最短（夸克禁闭，§4）；引力最弱，却力程无限（主导宇宙学尺度，Topic 08）。

### 2.3 规范对称性——标准模型的数学骨架

标准模型的拉格朗日量由规范对称群决定：

$$\boxed{SU(3)_C \times SU(2)_L \times U(1)_Y}$$

- $SU(3)_C$：色荷（color），强相互作用（QCD）
- $SU(2)_L$：弱同位旋（左手费米子）
- $U(1)_Y$：超荷

**规范原理**（Yang & Mills 1954）：要求拉格朗日量在局域规范变换下不变，**唯一地**确定了相互作用的形式和规范玻色子的存在。这是物理学最美的思想之一——对称性决定动力学。

$$\text{对称性} \xrightarrow{\text{规范原理}} \text{相互作用}$$

电弱统一（§5）把 $SU(2)_L \times U(1)_Y$ 自发破缺为 $U(1)_{em}$，这就是希格斯机制。

---

## §3 量子电动力学与费曼图

### 3.1 费曼图——粒子相互作用的"卡通"

**直觉**：费曼图是 QFT 振幅的图形化编码。每条线代表一个粒子传播子，每个顶点代表一次相互作用。

QED 中电子-电子散射（Møller 散射）的最低阶费曼图：两个电子交换一个虚光子。

**费曼规则**（Griffiths Ch 2/6）：

| 图形元素 | 物理量 | 数学因子 |
|---------|--------|---------|
| 外线（费米子） | 入射/出射粒子 | 旋量 $u, \bar{u}$ |
| 内线（费米子传播子） | 虚费米子 | $\frac{i(\slashed{p}+m)}{p^2-m^2}$ |
| 内线（光子传播子） | 虚光子 | $\frac{-ig_{\mu\nu}}{q^2}$ |
| 顶点 | 电磁相互作用 | $-ie\gamma^\mu$ |

振幅 = 所有费曼图的贡献之和。截面（可测量）$\propto |\mathcal{M}|^2$。

### 3.2 QED：最精确的物理理论

**电子反常磁矩**：Dirac 理论预言 $g=2$（精确）。QED 辐射修正给出：

$$a_e = \frac{g-2}{2} = \frac{\alpha}{2\pi} - 0.328478965\left(\frac{\alpha}{\pi}\right)^2 + \cdots = 0.00115965218028$$

实验值：$0.00115965218073$。理论与实验符合到 **12 位有效数字**——这是物理学最精确的预言，QED 是人类最成功的理论。

### 3.3 跑动耦合常数与重整化

**反直觉发现**：耦合常数不是常数！电磁精细结构常数 $\alpha \approx 1/137$ 只是在低能（原子尺度）的值。能量越高，$\alpha$ 越大（屏蔽减弱）：

$$\alpha(Q^2) = \frac{\alpha}{1 - \frac{\alpha}{3\pi}\ln(Q^2/m_e^2 c^4)}$$

在 LHC 能量（$\sim$ TeV），$\alpha \approx 1/128$。这是"真空极化"——虚电子-正电子对屏蔽电荷，高能探针穿透屏蔽看到"裸"电荷更大。

**重整化**：QFT 计算出现无穷大（紫外发散）。重整化理论（'t Hooft-Veltman 证明可重整化，1971）把这些无穷大吸收进有限个物理参数（质量、电荷），给出有限可测预言。

---

## §4 强相互作用与夸克禁闭

### 4.1 量子色动力学（QCD）

夸克携带"色荷"——三种色（红、绿、蓝）+ 三种反色。胶子传递色力。

**QCD 拉格朗日量**（与 QED 类比）：

| | QED | QCD |
|---|-----|-----|
| 荷 | 电荷 (1种) | 色荷 (3种色) |
| 载体 | 光子 (1种, 不带电) | 胶子 (8种, 带色荷) |
| 规范群 | $U(1)$ | $SU(3)$ |
| 自相互作用 | 无（光子不带电）| **有**（胶子带色荷！）|

**关键差异**：胶子本身带色荷，所以胶子会发射胶子——强力的自相互作用。这是 QCD 远比 QED 复杂的根本原因。

### 4.2 渐近自由

**1973 年 Gross, Politzer, Wilczek 的伟大发现**（2004 诺贝尔奖）：QCD 的耦合常数在高能（短距离）**趋于零**！

$$\boxed{\alpha_s(Q^2) \xrightarrow{Q^2\to\infty} 0 \quad \text{(渐近自由)}}$$

**物理图像**：夸克靠得越近，相互作用越弱——在高能碰撞中，夸克 behaves 几乎像自由粒子。这解释了为什么 SLAC 深度非弹性散射（1968）看到质子内部"自由"的部分子（夸克）。

**反直觉**：这与 QED 相反！QED 高能 $\alpha$ 变大（反屏蔽），QCD 高能 $\alpha_s$ 变小（屏蔽）。差异源于胶子的自相互作用。

### 4.3 夸克禁闭

**渐近自由的另一面**：低能（长距离）时 $\alpha_s$ 增长，最终趋于无穷——**单个夸克永远无法被分离出来**！

**色禁闭**：只有"色单态"（无色组合）才能作为自由粒子存在：
- 3 个不同色的夸克（红+绿+蓝 = 无色）→ 重子
- 夸克 + 反色的反夸克 → 介子

**弦模型**：拉开两个夸克，色力线形成"弦"。拉得越远，能量越大。当能量超过 $2m_q c^2$，弦断裂，从真空中产生新的夸克-反夸克对——你得到的永远是强子（介子/重子），永远不是自由夸克。

$$E(r) \approx \sigma r \quad (\sigma \approx 1 \text{ GeV/fm}, \text{ 弦张力})$$

拉开 1 fm 就需要 ~1 GeV——立刻产生新强子。这就是为什么没人见过孤立夸克。

### 4.4 核力 = 残余强力

质子和中子之间的核力（将它们束缚在原子核中）本质上是夸克之间强力的**残余**——类似范德华力是电磁力的残余。

核力特征：
- 力程 ~1-2 fm（核子大小尺度）
- 短程排斥（硬芯）+ 中程吸引
- $\pi$ 介子交换（汤川理论）是低能有效描述

---

## §5 弱相互作用与电弱统一

### 5.1 β 衰变与弱力的奇异性质

$$n \to p + e^- + \bar{\nu}_e \quad \text{(中子β衰变)}$$

**弱力的独特性**：
1. **唯一能改变夸克味的力**（如 $d \to u$）。
2. **宇称不守恒**（李政道、杨振宁 1956，吴健雄实验验证）——弱力区分左和右！
3. **CP 破坏**（1964 Cronin-Fitch 实验）——物质-反物质微小不对称，可能是宇宙物质主导的根源。

### 5.2 V-A 理论与左手性

弱相互作用只耦合**左手螺旋**的费米子（和右手螺旋的反费米子）。

$$\mathcal{L}_{int} = -\frac{G_F}{\sqrt{2}}[\bar{\psi}_e\gamma^\mu(1-\gamma^5)\psi_\nu][\bar{\psi}_\nu\gamma_\mu(1-\gamma^5)\psi_e]$$

$(1-\gamma^5)/2$ 是手征投影算符，挑出左手分量。

**反直觉**：右手中微子根本不参与弱相互作用（如果存在的话）——这就是为什么中微子是左手的（标准模型中没有右手中微子）。

### 5.3 电弱统一（Glashow-Salam-Weinberg）

**伟大的统一**（1979 诺贝尔奖）：电磁力和弱力在高能下是**同一种力**——电弱力。它们在低能显得不同，是因为希格斯场自发破缺了电弱对称性。

**希格斯机制**：
1. 宇宙充满一个标量场——希格斯场 $\phi$（真空期望值 $v \approx 246$ GeV）。
2. 希格斯场与 $W, Z$ 玻色子耦合，给它们质量（$m_W = gv/2$），但光子保持无质量（不耦合）。
3. 希格斯场也通过汤川耦合给费米子质量（$m_f = y_f v/\sqrt{2}$，$y_f$ 是汤川耦合常数）。

**破缺模式**：

$$SU(2)_L \times U(1)_Y \xrightarrow{\text{希格斯}} U(1)_{em}$$

破缺前：4 个规范玻色子（$W^1, W^2, W^3, B$）全无质量。
破缺后：3 个获得质量（$W^\pm, Z^0$），1 个保持无质量（光子 $\gamma$）。

### 5.4 希格斯玻色子的发现

标准模型预言希格斯场的量子激发——希格斯玻色子 $H$。2012 年 LHC（CERN）在 125 GeV 处发现它，**标准模型的最后一块拼图归位**。

希格斯质量决定了一切：太轻，宇宙不稳定；太重，对称性不破缺。125 GeV 恰好使宇宙处于"亚稳态"边缘——我们恰好存在。

### 5.5 CKM 矩阵与中微子振荡

夸克质量本征态与弱作用本征态不同，由 **CKM 矩阵**（Cabibbo-Kobayashi-Maskawa，2008 诺贝尔奖，小林诚与益川敏英）联系：

$$\begin{pmatrix} d' \\ s' \\ b' \end{pmatrix} = V_{CKM}\begin{pmatrix} d \\ s \\ b \end{pmatrix}$$

CKM 矩阵的复相位是 CP 破坏的来源。

**中微子振荡**（1998 Super-Kamiokande，2015 诺贝尔奖）：类似地，中微子味本征态与质量本征态不同（PMNS 矩阵），导致中微子在传播中改变味——电子中微子会变成 μ 中微子再变回来。这证明中微子有非零质量，是超出标准模型的第一个明确信号。

---

## §6 Berkeley 特色：LBNL 与加速器传统

### Ernest Lawrence 与回旋加速器

UC Berkeley 粒子物理的辉煌始于 **Ernest O. Lawrence**（1901-1958），Berkeley 教授（1928 起）。

**1929 年**：Lawrence 发明**回旋加速器**（cyclotron）——用磁场让带电粒子做圆周运动，用交变电场反复加速。这是粒子加速器的革命，开启了"高能物理"时代。

**1939 年诺贝尔物理学奖**授予 Lawrence。

### 88-Inch Cyclotron

LBNL 至今运行着 **88-inch Cyclotron**（1962 建成），用于：
- 核物理实验（核结构、核反应）
- 半导体抗辐射测试（空间电子学）
- 同位素生产
- Berkeley 核物理课程（Physics 129 核物理部分）的实验基地

### Berkeley/LBNL 的粒子物理贡献

| Berkeley/LBNL 贡献 | 意义 |
|-------------------|------|
| **回旋加速器** (Lawrence 1929) | 加速器时代开端 |
| **反质子发现** (Segrè, Chamberlain 1955) | 1959 诺贝尔奖 |
| **超铀元素** (Seaborg 等) | 多种人造元素，104号 Sg/106号 Sg 命名权 |
| **Gerson Goldhaber** | J/ψ 共振态发现贡献 |
| **SNO 中微子实验** (Berkeley 参与) | 2002-2006，中微子质量 |
| **LBNL 探测器研发** | ATLAS/CMS 探测器部件 |
| **SuperNova Legacy Survey** | 暗能量研究 |

### Berkeley 粒子理论研究

Berkeley 理论粒子物理组历史悠久：
- **Geoffrey Chew**：S 矩阵理论（1960s，夸克模型前的尝试）
- **Stanley Mandelstam**：双重共振模型
- **Mary K. Gaillard**：标准模型唯象学，粲夸克预言
- 当前：粒子宇宙学、超出标准模型物理、弦理论

### Berkeley 129 → 237 路线

| Berkeley 129 内容 | 连接到的研究/研究生课 |
|-------------------|---------------------|
| 标准模型 | 超出标准模型物理（Berkeley 237/239）|
| 费曼图/QED | 量子场论（Berkeley 237A/B, Peskin）|
| QCD | 格点 QCD、强子物理 |
| 电弱统一 | 希格斯物理、电弱精确测量 |
| 中微子 | 中微子物理、轻子味破坏 |
| 宇宙学连接 | 暗物质、暗能量（Berkeley 139/161）|

---

## 习题集

### 基础题（标准模型与守恒律）

**习题 7.1**：写出质子、中子、π⁺、π⁰、K⁺ 的夸克组成。
> **解**：$p=uud$, $n=udd$, $\pi^+=u\bar{d}$, $\pi^0=(u\bar{u}-d\bar{d})/\sqrt{2}$, $K^+=u\bar{s}$。

**习题 7.2**：在反应 $\pi^- + p \to K^0 + \Lambda^0$ 中，验证奇异数守恒。
> **解**：初态 $S=0+0=0$（$\pi^-,p$ 无奇夸克）。末态 $K^0=d\bar{s}$（$S=+1$），$\Lambda^0=uds$（$S=-1$）。总 $S=+1-1=0$。守恒。

**习题 7.3**：为什么自由中子能 β 衰变而自由质子不能？（$m_n > m_p + m_e$？）
> **解**：$m_n c^2=939.6$ MeV，$m_p c^2+m_e c^2=938.3+0.5=938.8$ MeV。$m_n > m_p+m_e$，能量允许。反向 $p\to n+e^+$ 需 $m_p > m_n+m_e$，不满足。

### 中级题（QCD 与弱相互作用）

**习题 7.4**（强子质量）：三个夸克（$uud$，每个质量 $\sim$ 几 MeV）如何组成 938 MeV 的质子？
> **解**：质子质量的 ~99% 来自夸克间的结合能（胶子场能量 + 夸克动能），而非夸克静质量。这是 QCD 禁闭能标的体现——$E\sim\Lambda_{QCD}\sim 200$ MeV/夸克。

**习题 7.5**（弱衰变寿命）：比较 $\mu \to e\nu\bar\nu$（寿命 $2.2\mu$s）和 $\pi \to \mu\nu$（寿命 $26$ ns）。为什么 π 介子衰变更快但弱力相同？
> **提示**：衰变率 $\Gamma \propto G_F^2 |M|^2$，矩阵元 $M$ 不同（轻子衰变 vs 强子-轻子衰变，后者涉及强子矩阵元）。

**习题 7.6**（CKM 矩阵）：写出 CKM 矩阵的 Wolfenstein 参数化，指出哪个参数对应 CP 破坏。
> **解**：$V_{CKM}\approx\begin{pmatrix}1-\lambda^2/2&\lambda&A\lambda^3(\rho-i\eta)\\-\lambda&1-\lambda^2/2&A\lambda^3\\A\lambda^3(1-\rho-i\eta)&-A\lambda^2&1\end{pmatrix}$。虚部 $\eta$ 是 CP 破坏。

### 挑战题

**习题 7.7**（渐近自由）：定性解释为什么 QCD 渐近自由而 QED 没有。
> **提示**：胶子带色荷自相互作用（反屏蔽），光子不带电不自相互作用。QCD 中胶子贡献"反屏蔽"超过费米子的"屏蔽"。

**习题 7.8**（希格斯机制）：解释为什么光子无质量而 W/Z 有质量，尽管它们都来自同一个 $SU(2)_L\times U(1)_Y$ 规范群。
> **提示**：希格斯场真空期望值在 $SU(2)$ 方向，破缺到 $U(1)_{em}$。沿 $U(1)_{em}$ 方向的组合（光子）不耦合希格斯，保持无质量。

**习题 7.9**（中微子振荡）：推导两味中微子振荡公式 $P(\nu_e\to\nu_\mu)=\sin^2(2\theta)\sin^2(\Delta m^2 L/4E)$。
> **提示**：味态 $|\nu_e\rangle=\cos\theta|\nu_1\rangle+\sin\theta|\nu_2\rangle$，质量本征态相位演化为 $e^{-iE_i t}$。

---

## Python 演示

### 演示 1：标准模型粒子质量谱与相互作用

```python
"""
标准模型粒子质量谱 — Berkeley 129
展示三代费米子质量跨越 10⁶ 倍。
纯 NumPy。
"""
import numpy as np
import matplotlib.pyplot as plt

# 粒子质量 (GeV)
particles = {
    '夸克': [('u', 0.0022), ('d', 0.0047), ('c', 1.275), ('s', 0.095),
             ('t', 173.0), ('b', 4.18)],
    '轻子': [('e', 0.000511), ('μ', 0.10566), ('τ', 1.7768),
             ('νe', 1e-9), ('νμ', 1e-9), ('ντ', 1e-9)],
    '玻色子': [('γ', 0), ('g', 0), ('W±', 80.379), ('Z⁰', 91.1876), ('H', 125.18)]
}

fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# 左：质量谱（对数）
ax = axes[0]
colors = {'夸克': 'red', '轻子': 'blue', '玻色子': 'green'}
y = 0
labels = []
for cat, plist in particles.items():
    for name, mass in plist:
        m_display = max(mass, 1e-10)  # 避免 log(0)
        ax.barh(y, np.log10(m_display*1000), color=colors[cat], alpha=0.7, edgecolor='k')
        ax.text(np.log10(m_display*1000)+0.1, y, f'{name} ({mass*1000:.2f} MeV)' if mass>0.0001 else f'{name}', 
                va='center', fontsize=9)
        y += 1
    y += 0.5
ax.set_yticks([])
ax.set_xlabel(r'$\log_{10}(\mathrm{mass / MeV})$')
ax.set_title('Standard Model Mass Spectrum\n(spreads over 10⁵ in mass!)')
ax.axvline(np.log10(1), color='gray', ls='--', alpha=0.3)

# 右：三代结构
ax = axes[1]
gen_data = [('Gen I', ['u','d','e','νe'], [2.2,4.7,0.511,0.001]),
            ('Gen II', ['c','s','μ','νμ'], [1275,95,105.7,0.001]),
            ('Gen III', ['t','b','τ','ντ'], [173000,4180,1777,0.001])]
x = np.arange(4)
width = 0.25
for i, (gen, names, masses) in enumerate(gen_data):
    ax.bar(x + i*width, np.log10([max(m,0.001) for m in masses]), width, label=gen)
ax.set_xticks(x + width)
ax.set_xticklabels(['quark up-type','quark down-type','charged lepton','neutrino'])
ax.set_ylabel(r'$\log_{10}(\mathrm{mass/MeV})$')
ax.set_title('Three Generations\n(why 3 copies? No one knows!)')
ax.legend()
plt.setp(ax.get_xticklabels(), rotation=15, ha='right')

plt.tight_layout()
plt.savefig('standard_model_masses.png', dpi=150)
plt.show()
print("反直觉: 顶夸克(173GeV)比上夸克(2.2MeV)重 80000 倍 — 却是'同一种'粒子!")
print("标准模型最大谜团: 为什么有三代? (与宇宙物质-反物质不对称可能相关)")
```

**反直觉发现**：
1. **三代质量跨越 5 个数量级**——同族粒子的唯一差别是质量，原因不明。
2. **玻色子质量分离**：光子/胶子无质量，W/Z/H 有质量——全因希格斯机制的选择性耦合。

### 演示 2：QCD 耦合常数跑动 vs QED

```python
"""
跑动耦合常数 — Berkeley 129
QCD 渐近自由 vs QED 反屏蔽。
"""
import numpy as np
import matplotlib.pyplot as plt

# 能量尺度 (GeV), 对数
logQ = np.linspace(-1, 5, 300)  # 0.1 GeV 到 100 TeV
Q = 10**logQ

# QED: α(Q) = α₀/(1 - α₀/(3π) ln(Q²/m_e²))
alpha0 = 1/137.036
me = 0.000511  # GeV
alpha_QED = alpha0 / (1 - alpha0/(3*np.pi) * np.log((Q**2)/(me**2)))
alpha_QED = np.maximum(alpha_QED, 0)  # 避免 Landau pole 发散区

# QCD: α_s(Q) = 12π/(33-2n_f) / ln(Q²/Λ²), Λ≈200 MeV, n_f=6
Lambda_QCD = 0.2  # GeV
n_f = 6
alpha_s = 12*np.pi / (33 - 2*n_f) / np.log(np.maximum(Q**2/Lambda_QCD**2, 1.01))

fig, axes = plt.subplots(1, 2, figsize=(13, 5))

ax = axes[0]
ax.semilogx(Q, alpha_QED*137, 'b-', linewidth=2.5, label=r'QED: $\alpha \times 137$')
ax.semilogx(Q, alpha_s, 'r-', linewidth=2.5, label=r'QCD: $\alpha_s$')
ax.axhline(1, color='gray', ls='--', alpha=0.3)
ax.set_xlabel('Energy scale Q (GeV)')
ax.set_ylabel('Coupling constant')
ax.set_title('Running Coupling Constants\n(QCD: asymptotic freedom; QED: anti-screening)')
ax.legend()
ax.grid(alpha=0.3)
ax.annotate('QCD → 0\n(asymptotic freedom)', xy=(100, 0.12), fontsize=10, color='red')
ax.annotate('QED grows\n(anti-screening)', xy=(0.5, 1.3), fontsize=10, color='blue')

# 右：夸克禁闭弦模型
ax = axes[1]
r = np.linspace(0.01, 2, 200)  # fm
# 短程库仑-like + 长程弦
E_short = -0.5 / r  # 短程 (渐近自由, 弱)
E_string = 1.0 * r  # 长程弦张力
E_total = E_short + E_string
# 产生强子的阈值
E_pair = 0.7  # GeV (典型轻夸克强子对质量)

ax.plot(r, E_total, 'k-', linewidth=2.5, label='Total V(r)')
ax.plot(r, E_string, 'r--', linewidth=1.5, label='String: σr')
ax.plot(r, E_short, 'b--', linewidth=1.5, label='Coulomb-like: -α_s/r')
ax.axhline(E_pair, color='green', ls=':', linewidth=2, label='Hadron pair threshold')
r_break = r[np.argmin(np.abs(E_total - E_pair))]
ax.axvline(r_break, color='orange', ls='-.', alpha=0.7)
ax.annotate(f'String breaks here\n(r≈{r_break:.2f} fm)\n→ new hadrons', 
            xy=(r_break, E_pair), xytext=(r_break+0.3, 0.3),
            arrowprops=dict(arrowstyle='->', color='orange'),
            fontsize=9, color='orange')
ax.set_xlabel('Quark separation r (fm)')
ax.set_ylabel('Potential energy V(r) (GeV)')
ax.set_title('Quark Confinement: QCD String\n(cannot pull quarks apart!)')
ax.legend(loc='upper left')
ax.set_ylim(-2, 3)
ax.grid(alpha=0.3)

plt.tight_layout()
plt.savefig('qcd_running_confinement.png', dpi=150)
plt.show()
print("反直觉: 把夸克拉开的下场不是'看到自由夸克', 而是弦断裂产生新强子!")
```

**反直觉发现**：
1. **QCD 高能变弱，QED 高能变强**——方向相反，源于胶子自相互作用。
2. **夸克禁闭的必然性**：拉开夸克，能量线性增长，到阈值就产生新强子对——永远得不到自由夸克。

### 演示 3：中微子振荡

```python
"""
中微子振荡 — Berkeley 129 (超出标准模型)
"""
import numpy as np
import matplotlib.pyplot as plt

# 两味中微子振荡: P(νe → νμ) = sin²(2θ) sin²(Δm²L/4E)
# 大气中微子参数: Δm² ≈ 2.5e-3 eV², θ ≈ 45°

theta = np.pi/4  # 最大混合
dm2 = 2.5e-3  # eV²

# L/E 扫描 (km/GeV)
LE = np.linspace(0, 3000, 500)  # km/GeV
# 转换: 1.27 * Δm²(eV²) * L(km) / E(GeV) 给出相位 (rad)
phase = 1.27 * dm2 * LE
P_mumu = 1 - np.sin(2*theta)**2 * np.sin(phase)**2  # 保持在 νμ 的概率
P_nue = 1 - P_mumu  # 变成 νe (两味近似)

fig, axes = plt.subplots(1, 2, figsize=(13, 5))

ax = axes[0]
ax.plot(LE, P_mumu, 'b-', linewidth=2, label=r'$P(\nu_\mu \to \nu_\mu)$ survival')
ax.plot(LE, P_nue, 'r-', linewidth=2, label=r'$P(\nu_\mu \to \nu_e)$ oscillation')
ax.set_xlabel('L/E (km/GeV)')
ax.set_ylabel('Probability')
ax.set_title(f'Neutrino Oscillation (2-flavor)\n$\\theta=45°$, $\\Delta m^2={dm2*1000}$ meV²')
ax.legend()
ax.grid(alpha=0.3)
# 标注振荡长度
L_osc = np.pi / (1.27 * dm2)
ax.axvline(L_osc, color='gray', ls=':', alpha=0.5)
ax.annotate(f'oscillation length\nL/E ≈ {L_osc:.0f} km/GeV', 
            xy=(L_osc, 0.5), xytext=(L_osc+400, 0.7),
            arrowprops=dict(arrowstyle='->', color='gray'))

# 右：混合角的影响
ax = axes[1]
angles = [np.pi/8, np.pi/6, np.pi/4]
for ang in angles:
    P = np.sin(2*ang)**2 * np.sin(phase)**2
    ax.plot(LE, P, linewidth=2, label=f'θ = {np.degrees(ang):.0f}°')
ax.set_xlabel('L/E (km/GeV)')
ax.set_ylabel(r'$P(\nu_\mu \to \nu_e)$')
ax.set_title('Effect of Mixing Angle θ\n(larger θ → larger amplitude)')
ax.legend()
ax.grid(alpha=0.3)

plt.tight_layout()
plt.savefig('neutrino_oscillation.png', dpi=150)
plt.show()
print("中微子振荡证明中微子有质量 — 标准模型的第一个裂痕!")
print(f"大气中微子振荡长度: L_osc ≈ {L_osc:.0f} km/GeV (地球尺度!)")
```

---

## 学习路径建议

```
129 (Griffiths Ch 1-4)  →  粒子动物园 + 守恒律 + 对称性
      ↓
129 (Griffiths Ch 5-7)  →  夸克模型 + QED + 费曼图
      ↓
129 (Griffiths Ch 8-9)  →  弱相互作用 + 电弱统一
      ↓
237A (Peskin Ch 1-5)    →  QFT 形式化 + 路径积分
      ↓
237B (Peskin Ch 15-19)  →  非阿贝尔规范理论 + 标准模型
      ↓
研究前沿                 →  超出标准模型 / 弦论 / 宇宙学
```

**Griffiths 教材学习节奏**（Berkeley 129 一学期 15 周）：
- 周 1-2：Ch 1-2（粒子历史 + 守恒律）
- 周 3-4：Ch 3（夸克模型，Eightfold Way）
- 周 5-6：Ch 4（对称性与群论）
- 周 7-9：Ch 5-6（QED + 费曼规则 + 截面）
- 周 10-11：Ch 7（QCD + 渐近自由）
- 周 12-13：Ch 8-9（弱相互作用 + 电弱统一）
- 周 14-15：Ch 10（希格斯机制）+ 核物理补充（Krane）

---

> **文件信息**：Berkeley Physics · Topic 07 Particle & Nuclear Physics · 2026-08-12
>
> **教材交叉引用**：Griffiths Particles (129) / Krane (核物理补充) / Peskin & Schroeder (237 研究生 QFT) / Halzen & Martin (进阶) · LBNL 88-inch Cyclotron 关联

---

## 🎯 费曼式入口（白话版）

> **一句话解释**：粒子物理研究"世界最小的积木是什么"——所有物质（你、我、星星）最终由什么构成？答案出人意料地简洁：三代夸克 + 三代轻子 + 四种力粒子，总共 17 种基本粒子，构成了整个宇宙。
>
> **生活类比**：想象乐高积木。你用少数几种基本积木块，可以搭出城堡、飞船、恐龙——任何东西。宇宙也是如此：夸克组成质子和中子，质子和中子组成原子核，原子核加电子组成原子，原子组成分子，分子组成……一切。更神奇的是，积木块之间"交流"用的"信使"（力粒子）也是同一种乐高——光子传递电磁力，胶子传递强力，W/Z 玻色子传递弱力。标准模型就是这套"宇宙乐高说明书"。
>
> **反直觉发现**：
> - **物质几乎全是"空的"**：原子核的直径是原子的十万分之一。如果把原子核放大到乒乓球大小，最近的电子在 3 公里外！你坐的椅子、踩的地板、你的身体——99.9999% 是真空。
> - **质量大部分不是"真正的质量"**：质子的质量（938 MeV）远大于组成它的三个夸克的质量之和（~10 MeV）。其余 99% 的质量来自夸克和胶子的结合能——$E = mc^2$！你身体的大部分重量是"能量的重量"。
> - **中微子可以穿墙——穿地球**：每秒钟有 650 亿个中微子穿过你的指甲盖。它们几乎不与物质相互作用——需要一光年厚的铅才能挡住一半的中微子。但它们有质量（违反标准模型！），还能在中微子振荡中改变身份。
> - **反物质存在但几乎消失**：每种粒子都有对应的反粒子（电子↔正电子）。大爆炸应该产生等量的物质和反物质，但宇宙中几乎只有物质——这种"物质-反物质不对称"是物理学最大的未解之谜之一。

---

## 🔗 衔接：从哪来，到哪去

### 前置知识
- **Topic 01 经典力学**：守恒律与对称性（Noether 定理）；相对论能量-动量关系 $E^2 = p^2c^2 + m^2c^4$
- **Topic 02 电磁学**：QED 的经典基础；电磁场→光子
- **Topic 03 量子力学**：量子态→粒子态；全同粒子→交换对称性；自旋→统计
- **Topic 05 数学方法**：群论（SU(3)×SU(2)×U(1) 规范群）；张量分析

### 本主题解决了什么危机
- **粒子动物园的混乱**（1960s）：加速器发现了上百种"基本粒子"——$\pi$、$K$、$\Lambda$、$\Sigma$、$\Xi$……物理学陷入混乱。Murray Gell-Mann 和 George Zweig 的夸克模型（1964）用上、下、奇三种夸克统一了所有强子——上百种粒子变成了 3 种夸克的组合。Gell-Mann 因此获 1969 年诺贝尔奖。
- **四种力的统一**：电磁力和弱力看似毫无关系（强度差 $10^5$ 倍，力程不同），但 Glashow-Weinberg-Salam 的电弱统一理论（1967）证明在高能下它们是同一种力。这是爱因斯坦"统一场论"梦想的部分实现。
- **质量的起源**（希格斯机制 1964）：为什么 W/Z 玻色子有质量而光子没有？希格斯场像一层"粘稠的蜂蜜"，粒子穿过时获得质量。2012 年 LHC 发现希格斯玻色子——标准模型的最后一块拼图。

### 本主题留下的新危机
- **暗物质看不见但存在**：星系旋转速度、引力透镜、宇宙微波背景都表明宇宙中有 5 倍于可见物质的"暗物质"。但它不发光、不吸收光——完全不在标准模型中。它是什么？
- **暗能量更诡异**：宇宙膨胀在加速！驱动加速的"暗能量"占宇宙能量密度的 68%。它可能是一种真空能（宇宙学常数 $\Lambda$），但理论预言值比观测大 $10^{120}$ 倍——物理学史上最大的差值。
- **引力无法量子化**：标准模型描述了三种力（电磁、弱、强），但引力（广义相对论）无法用量子场论描述。弦论和圈量子引力是候选方案，但都没有实验验证。
- **中微子质量的来源**：标准模型预言中微子质量为零，但中微子振荡实验证明它们有质量（虽然极小）。这需要超出标准模型的新物理——是马约拉纳质量？还是额外维度？

### 后续主题
- → Berkeley **237A/B**：量子场论（Peskin & Schroeder）→ 标准模型的严格推导
- → Berkeley **139**：广义相对论 → 宇宙学 → 暗物质/暗能量的理论
- → 研究前沿：**弦论** · **圈量子引力** · **超越标准模型(BSM)** · **中微子物理**
- → LBNL 实验：**88-inch 回旋加速器** · **暗物质直接探测(LUX-ZEPLIN)** · **中微子实验**

---

## 🏭 理论联系实际：5 个应用

1. **正电子发射断层扫描(PET)**：癌症诊断的利器。注射放射性同位素（如 F-18 标记的葡萄糖），同位素衰变释放正电子，正电子与电子湮灭产生两个反向 511 keV 光子——探测器记录这些光子重建肿瘤三维图像。Berkeley 的核医学研究开发新型 PET 示踪剂。

2. **放射性同位素生产**：LBNL 的 88-inch 回旋加速器生产医用同位素（如 Ga-68 用于 PET 显像、Ac-225 用于靶向 Alpha 治疗癌症）。粒子加速器从基础研究工具变成了拯救生命的医疗设备。

3. **核能（裂变与聚变）**：核电站（全球 400+ 座）提供约 10% 的电力。核聚变（ITER 项目，2025 年开始 D-T 实验）有望提供几乎无限的清洁能源——它的物理基础就是 E=mc² 和核力。LBNL 参与聚变靶材设计和诊断。

4. **同步辐射与散裂中子源**：高能粒子加速器产生的同步辐射光和中子束是材料科学的"超级显微镜"。LBNL 的 ALS（Advanced Light Source）每年服务 2000+ 研究者，从蛋白质结构到电池材料到量子材料。加速器物理直接服务于整个科学界。

5. **辐射探测与核安全**：安检设备（机场 X 光机、集装箱辐射检测）、核电站监控、核废料管理、核不扩散验证——都需要粒子物理的探测器技术和辐射物理知识。Berkeley 的核工程系培养此领域专业人才。暗物质探测器(LUX-ZEPLIN, LBNL 主导)是最灵敏的辐射探测系统。

---

## 🔬 最新研究前沿（2024-2026）

1. **地球深部中微子提供地幔新图像**（2026-08-07, Quanta Magazine）：全球中微子探测器网络正在创建前所未有的地幔放射性元素分布图——这些元素驱动地球的构造热引擎。Berkeley LBNL 的 KamLAND 实验参与此国际合作，开创"地球中微学"(geoneutrino) 新学科。

2. **缪子 g-2 谜题：25 年之谜的解答与新矛盾**（2026-07-29, Quanta Magazine）：新计算方法似乎解决了缪子磁矩的长期矛盾——但同时也与某些实验结果产生冲突。这暗示电磁相互作用中可能存在超出标准模型的新物理。Berkeley LBNL 的理论物理学家参与此计算。

3. **暗维度：暗物质与暗能量的隐藏联系**（2026-06-22, Quanta Magazine）：近期观测暗示暗能量随时间变化。理论家推测暗物质也在变化——也许暗物质和暗能量是同一个"暗维度"的两种表现。Berkeley 的理论物理组研究额外维度模型与暗物质候选者（如轴子、WIMP）。

4. **到底有多少基本粒子？**（2026-06-15, Quanta Magazine）：标准模型给出 17 种基本粒子，但考虑理论扩展（超对称、大统一、弦论），合理答案从 17 到 995.5 不等。LHC 和未来对撞机正在搜索超对称伙伴粒子。

5. **LUX-ZEPLIN 暗物质探测器运行**（2024-2025）：LBNL 主导的 LUX-ZEPLIN 实验——10 吨液氙暗物质探测器——开始科学运行。它是世界上最灵敏的 WIMP 暗物质探测器，灵敏度比上一代提高 50 倍。Berkeley 的物理学家领导数据分析。如果探测到暗物质信号，将是 21 世纪物理学最大发现之一。

6. **中微子质量顺序接近确定**（2024-2025）：DUNE（美国）和 Hyper-Kamiokande（日本）下一代中微子实验正在建设中，目标之一是确定中微子质量顺序（正常 vs 反转）。Berkeley LBNL 参与这两个实验的设计和模拟。结果将约束大统一模型和宇宙物质-反物质不对称的机制。

---

## 🗺️ 学习 Roadmap（Berkeley 路径）

```
 7A/7B — 基础物理（原子结构、核物理入门）
      ↓
 129 — Particle Physics (Griffiths Particles)
      │  粒子动物园历史 · 守恒律与对称性 · 夸克模型(Eightfold Way) · QED 基础
      │  · 费曼规则 · 强相互作用(QCD) · 弱相互作用 · 电弱统一 · 希格斯机制
      │  ✅ 知识检查：能否画出电子-缪子散射的费曼图？能否解释为什么渐近自由让夸克禁闭？
      │  📖 核物理补充：Krane "Introductory Nuclear Physics"（LBNL 88-inch 加速器关联）
      ↓
 237A — Quantum Field Theory I (Peskin & Schroeder)
      │  经典场论 → 正则量子化 → 路径积分 → 微扰论(QED) → 重整化
      │  ✅ 知识检查：能否用费曼规则计算电子-电子散射截面？能否解释重整化的物理意义？
      ↓
 237B — Quantum Field Theory II
      │  非阿贝尔规范理论(Yang-Mills) · QCD(渐近自由) · 电弱理论 · 标准模型
      │  ✅ 知识检查：能否推导胶子自相互作用顶点？能否解释 Higgs 机制如何赋予质量？
      ↓
 研究前沿 → 弦论 · 暗物质 · 中微子物理 · 量子引力 · 超越标准模型
      │
      │  🔬 LBNL 关联：88-inch Cyclotron ·(dark matter) · SuperCDMS · KamLAND · DUNE
```

**核心教材节奏**：
| 阶段 | 教材 | 周数 | 核心概念 |
|------|------|------|----------|
| 129 | Griffiths Particles | 15 周 | 标准模型定性理解 |
| 237A | Peskin Ch 1-10 | 15 周 | QFT 形式化 + QED |
| 237B | Peskin Ch 15-21 | 15 周 | QCD + 电弱 + 标准模型 |

**费曼学习法检查点**：
- [ ] 能否用白话解释"为什么质子的质量 99% 来自能量而不是夸克质量"？（$E=mc^2$ + 强相互作用结合能）
- [ ] 能否画出标准模型 17 种基本粒子的分类表，并说明每种粒子的作用？
- [ ] 能否解释中微子振荡为什么证明标准模型不完整？（中微子应有零质量，但有振荡=有质量）
- [ ] 能否解释为什么暗物质不可能是标准模型中的任何已知粒子？（不发光 + 不参与强/电磁相互作用 + 有引力效应）
