# David Tong · Quantum Mechanics（量子力学）导读笔记

> Tong 系列第 06 本 | 难度 ★★（本科核心）| 配合：L08 量子力学 + L09 量子力学进阶

## §0 基本信息
- **作者**：David Tong（Cambridge，本科 Part IB）
- **难度**：★★（需要线性代数 + 微分方程 + 经典力学）
- **篇幅**：约 155 页
- **链接**：davidtong.org/teaching/quantum-mechanics/
- **配合项目**：L08 量子力学 + L09 量子力学进阶

## §1 一句话定位
**从波函数到自旋**——量子力学的标准本科课程，Tong 的版本特别注重直觉和物理图像。

## §2 前置知识
- 必须会：线性代数（本征值/本征向量/厄米矩阵）、常微分方程、04_classical_dynamics（哈密顿力学概念）、复数
- 建议会：特殊函数（Bessel、Legendre、Hermite）、偏微分方程（分离变量法）

## §3 讲义全景（章节地图）

从 Schrödinger 方程出发，逐步建立量子力学的全套工具。

| 章 | 主题 | 核心问题 |
|----|------|---------|
| 1 | 波函数与 Schrödinger 方程 | 粒子怎么用波描述？|
| 2 | 一维问题 | 势阱/势垒/谐振子 |
| 3 | 角动量与氢原子 | 三维薛定谔方程怎么解？|
| 4 | 自旋与角动量 | 自旋是什么？SU(2) 怎么来？|
| 5 | 多粒子与全同性 | 为什么费米子和玻色子不同？|
| 6 | 微扰理论 | 近似方法 |
| 7 | 散射简介 | 粒子碰撞的量子描述 |

## §4 核心章节拆解（深化版）

### §4.1 波函数与 Schrödinger 方程

**核心概念**：粒子状态由波函数 $\psi(x,t)$ 完全描述，演化服从 Schrödinger 方程。

- **关键公式**：
$$i\hbar \frac{\partial \psi}{\partial t} = \hat{H}\psi = \left(-\frac{\hbar^2}{2m}\nabla^2 + V\right)\psi$$
- **概率诠释**：$|\psi(x,t)|^2$ 是在 $x$ 处找到粒子的概率密度
- **归一化**：$\int |\psi|^2\, d^3x = 1$
- **叠加原理**：$\psi = c_1\psi_1 + c_2\psi_2$ 也是合法态——这导致量子干涉

**不确定性原理的推导**（从 $[\hat{x}, \hat{p}] = i\hbar$ 用 Cauchy-Schwarz）：
- 对任意两个厄米算符 $A, B$，定义 $\Delta A = A - \langle A\rangle$
- Cauchy-Schwarz：$\langle(\Delta A)^2\rangle\langle(\Delta B)^2\rangle \geq |\langle\Delta A\,\Delta B\rangle|^2$
- 分解 $\langle\Delta A\,\Delta B\rangle = \frac{1}{2}\langle\{\Delta A,\Delta B\}\rangle + \frac{1}{2}\langle[\Delta A,\Delta B]\rangle$
- 对 $A=x, B=p$，$[\Delta x, \Delta p] = i\hbar$（纯虚），反交换子部分为实
- 取模：$\Delta x\,\Delta p \geq \frac{1}{2}|\langle[x,p]\rangle| = \frac{\hbar}{2}$

**Ehrenfest 定理**：
$$\frac{d\langle x\rangle}{dt} = \frac{\langle p\rangle}{m}, \quad \frac{d\langle p\rangle}{dt} = -\langle\nabla V\rangle$$
形式上像牛顿方程，但注意 $\langle\nabla V\rangle \neq \nabla V(\langle x\rangle)$（一般情况）——只有谐振子势（$V\propto x^2$ 线性 $\nabla V$）两者相等。

**概率流**：
$$\mathbf{j} = \frac{\hbar}{2mi}(\psi^*\nabla\psi - \psi\nabla\psi^*)$$
满足连续性方程 $\frac{\partial|\psi|^2}{\partial t} + \nabla\cdot\mathbf{j} = 0$（概率定域守恒）。

**直觉图像**：经典粒子是一个点，量子粒子是一团"概率云"——云的形状随时间演化，按 Schrödinger 方程"流动"。

**反直觉点**：波函数 $\psi$ 是**复数**，不可直接观测——只有 $|\psi|^2$ 有物理意义。但正是**相位差**导致量子干涉（双缝实验）。波函数不是物理波动（像水波），而是**概率幅**。

---

### §4.2 一维问题

**核心概念**：一维 Schrödinger 方程是二阶 ODE，不同势能给出不同物理。

**升降算符（谐振子的核心魔术）**：定义
$$a = \sqrt{\frac{m\omega}{2\hbar}}\left(x + \frac{ip}{m\omega}\right), \quad a^\dagger = \sqrt{\frac{m\omega}{2\hbar}}\left(x - \frac{ip}{m\omega}\right)$$
- 对易关系 $[a, a^\dagger] = 1$
- Hamilton 量改写：$H = \hbar\omega(a^\dagger a + \frac{1}{2})$
- 升降：$H(a^\dagger|n\rangle) = \hbar\omega(n+\frac{3}{2})(a^\dagger|n\rangle)$，即 $a^\dagger|n\rangle \propto |n+1\rangle$
- 能级 $E_n = \hbar\omega(n + \frac{1}{2})$，$n = 0,1,2,\ldots$

**零点能 $E_0 = \frac{1}{2}\hbar\omega$ 的根源**：来自 $[x,p]=i\hbar$。如果 $E_0=0$，则基态 $x=p=0$，即 $\Delta x = \Delta p = 0$，违反 $\Delta x\,\Delta p \geq \hbar/2$。所以**零点能是对易关系的必然**，不可消除。

**量子隧穿**：能量 $E < V_0$ 的粒子穿过势垒，透射系数
$$T \approx \exp\left(-\frac{2}{\hbar}\int\sqrt{2m(V(x)-E)}\, dx\right)$$
WKB 近似结果。势垒越宽越高，透射越小（指数衰减）。

**反直觉点**：隧穿允许粒子穿过**经典禁戒区**（$E < V$ 的区域）。这驱动了 α 衰变、扫描隧道显微镜（STM）、隧道二极管。能量严格守恒——隧穿不是"借能量"，是量子态的概率分布延伸到经典禁戒区的直接后果。

---

### §4.3 角动量与氢原子

**核心概念**：三维 Schrödinger 方程在球坐标中分离变量，角动量量子化自然出现。

**分离变量**：$\psi(r,\theta,\phi) = R(r)\, Y_l^m(\theta,\phi)$
- **角向**方程 → 球谐函数 $Y_l^m$，$\hat{L}^2 Y_l^m = \hbar^2 l(l+1)Y_l^m$，$\hat{L}_z Y_l^m = \hbar m\, Y_l^m$
- **径向**方程 → 关联 Laguerre 多项式 $R_{nl}(r)$

**氢原子能级**：
$$E_n = -\frac{me^4}{2\hbar^2 n^2} = -\frac{13.6\text{ eV}}{n^2}$$
量子数：$n=1,2,3,\ldots$（主）；$l=0,\ldots,n-1$（角）；$m=-l,\ldots,l$（磁）。

**偶然简并**（$E_n$ 与 $l$ 无关）的根源：Coulomb $1/r$ 势有**隐藏的 SO(4) 对称性**（Runge-Lenz 矢量 $\mathbf{A} = \frac{1}{2m}(\mathbf{p}\times\mathbf{L} - \mathbf{L}\times\mathbf{p}) - \frac{e^2}{r}\mathbf{r}$ 守恒）。一般有心力（如 $V\propto r^k$）没有这个对称性，能级依赖 $l$。

**反直觉点**：氢原子基态最概然半径是玻尔半径 $a_0$，但 $\langle r\rangle = \frac{3}{2}a_0$——**最概然值 ≠ 期望值**。径向概率分布 $|R_{10}|^2 r^2$ 在 $a_0$ 处取峰，但右尾拉长了平均值。

---

### §4.4 自旋

**核心概念**：自旋是**内禀**角动量，与轨道运动无关——粒子"天生就有"。

**自旋代数**：
$$[\hat{S}_i, \hat{S}_j] = i\hbar\,\epsilon_{ijk}\hat{S}_k, \quad \hat{S}^2|s,m_s\rangle = \hbar^2 s(s+1)|s,m_s\rangle$$

**自旋 1/2**：$\hat{\mathbf{S}} = \frac{\hbar}{2}\boldsymbol{\sigma}$，Pauli 矩阵
$$\sigma_x = \begin{pmatrix} 0 & 1 \\ 1 & 0 \end{pmatrix},\quad \sigma_y = \begin{pmatrix} 0 & -i \\ i & 0 \end{pmatrix},\quad \sigma_z = \begin{pmatrix} 1 & 0 \\ 0 & -1 \end{pmatrix}$$
- **反对易**：$\{\sigma_i, \sigma_j\} = 2\delta_{ij}$
- **对易**：$[\sigma_i, \sigma_j] = 2i\epsilon_{ijk}\sigma_k$

**SU(2) 双覆盖 SO(3)**：自旋态 $|\psi\rangle$ 在旋转 $\hat{R}(\boldsymbol{\theta}) = e^{-i\boldsymbol{\theta}\cdot\boldsymbol{\sigma}/2}$ 下变换。关键：
- 转 $2\pi$：$\hat{R}(2\pi) = -1 \neq \mathbf{1}$（**负的自己！**）
- 转 $4\pi$：$\hat{R}(4\pi) = +1$（才回到本身）

这是 SU(2) 双覆盖 SO(3) 的体现——自旋 1/2 表示"需要转两圈才回来"。

**Stern-Gerlach 实验**：银原子束通过非均匀磁场，分裂成**两束**（自旋上/下）——直接观测到自旋量子化。这是自旋存在的最直接证据。

**自旋-轨道耦合与精细结构**：电子自旋磁矩与轨道磁场耦合 $\hat{H}_{SO} \propto \hat{\mathbf{L}}\cdot\hat{\mathbf{S}}$，导致能级对 $l$ 的精细分裂（$\alpha^2 mc^2$ 量级，约 $10^{-4}$ eV）。

**反直觉点**：自旋**没有经典对应**。如果电子是半径 $r_e$ 的小球在旋转，要产生观测到的磁矩，表面速度需 $v > c$——相对论禁止。自旋是相对论量子力学（Dirac 方程）的**内禀性质**，不能理解为"小球旋转"。

---

### §4.5 全同粒子与 Pauli 不相容原理

**核心概念**：同种粒子**不可区分**——交换两个粒子不产生新状态。

**对称化公设**：
- **费米子**（半整数自旋）：交换**反对称** $\psi(1,2) = -\psi(2,1)$
- **玻色子**（整数自旋）：交换**对称** $\psi(1,2) = +\psi(2,1)$

**Pauli 不相容原理的推导**：对两个费米子在同一态 $\phi$，
$$\psi(1,1) = -\psi(1,1) \implies \psi(1,1) = 0$$
即**两个全同费米子不能占据同一量子态**。这是反对称性的直接数学后果，不需要额外假设。

**周期表的起源**：电子是自旋 1/2 费米子。填充原子轨道时，每个空间态（$n,l,m$）最多容纳 2 个电子（自旋上/下）。Pauli 不相容 → 轨道逐层填满 → 元素化学性质周期性变化。

**反直觉点**：Pauli 不相容**不是力**——它纯粹是交换对称性的数学后果（不是电磁力、不是引力）。但它是**整个化学和固体物理的基础**：没有 Pauli 排斥，所有电子会坍缩到 1s 轨道，没有元素多样性、没有导电性、没有生命。

---

### §4.6 微扰理论

**核心概念**：当精确解不可能时，把哈密顿量分成 $H = H_0 + \lambda H'$，用 $H_0$ 的解做微扰展开。

**非简并微扰**（一级）：
$$E_n^{(1)} = \langle n^{(0)} | H' | n^{(0)} \rangle$$
$$|n^{(1)}\rangle = \sum_{m \neq n} \frac{\langle m^{(0)} | H' | n^{(0)} \rangle}{E_n^{(0)} - E_m^{(0)}} |m^{(0)}\rangle$$

**简并微扰**（关键！）：当 $E_n^{(0)} = E_m^{(0)}$，分母为零 → 发散。必须**在简并子空间内对角化 $H'$**：
$$\det\left(H'_{ij} - E^{(1)}\delta_{ij}\right) = 0 \quad (i,j \in \text{简并子空间})$$
本征值就是一级能量修正，本征向量是"正确基底"。

**线性 Stark 效应**（简并微扰的典型应用）：氢原子 $n=2$ 能级四重简并（2s + 三个 2p）。外电场下 $H' = eEz$ 在简并子空间内对角化 → 能级**线性**分裂（$\propto E$）。非简并微扰只能给二次效应（$\propto E^2$），简并微扰给出更大的一阶效应。

**含时微扰与 Fermi 黄金定则**：周期性微扰 $H'(t) = V e^{-i\omega t}$ 导致能级间跃迁，跃迁率
$$\Gamma_{i\to f} = \frac{2\pi}{\hbar}|\langle f|V|i\rangle|^2 \rho(E_f)$$
（$\rho(E_f)$ 是末态密度）。这是激光、吸收光谱、放射性衰变的理论基础。

**反直觉点**：简并微扰论可以给出**大效应**（线性 Stark），而非简并微扰只能给小效应。简并是"放大器"——因为零阶态不唯一，微扰可以显著改变态的结构。

## §5 必做习题（深化版）

| 题 | 内容 | 为什么必做 |
|----|------|----------|
| 1 | **无限深势阱**：求能级 $E_n = \frac{n^2\pi^2\hbar^2}{2mL^2}$，验证正交归一 | 量子化与边界条件的第一练 |
| 2 | **谐振子**：用升降算符 $a, a^\dagger$ 推全部能级和基态波函数 | 升降算符方法是 QFT 的语言基础 |
| 3 | **氢原子 $n=2$**：写出 4 个波函数（2s + 三个 2p），画角度分布 | 理解化学键形状的量子起源 |
| 4 | **自旋进动**：自旋 1/2 在磁场 $\mathbf{B}$ 中的进动，求 Larmor 频率 | 自旋动力学 + SU(2) 实操 |
| 5 | **Pauli 排斥**：从反对称性 $\psi(1,2)=-\psi(2,1)$ 严格推出不相容 | 理解化学的基础是对称性而非力 |
| 6 | **非简并微扰**：谐振子加 $H'=\lambda x^4$，求一级能量修正 $\Delta E = \frac{3\lambda\hbar^2}{4m^2\omega^2}(2n^2+2n+1)$ | 微扰展开的标准练习 |
| 7 | **简并微扰**：氢原子 $n=2$ 的线性 Stark 效应，对角化 $4\times4$ 矩阵 | 理解简并为何是效应的放大器 |

**Tong 的习题表**在讲义末尾。建议**至少做完上表 7 题**才算入门。

## §6 读完后你应该能
- [ ] 解一维 Schrödinger 方程（势阱、势垒、谐振子）
- [ ] 用升降算符方法处理谐振子和角动量
- [ ] 写出氢原子波函数（至少 $n=1,2$）并理解量子数 $n, l, m$ 的含义
- [ ] 理解自旋是内禀的，不是"小球旋转"
- [ ] 理解 SU(2) 双覆盖 SO(3)（$2\pi$ 转出 $-1$）
- [ ] 用微扰理论（含简并）计算一级能量修正
- [ ] 解释为什么 Pauli 不相容原理是元素周期表的基础

## §7 与项目的映射
- **前置**：04_classical_dynamics.md（哈密顿力学概念）、03_vector_calculus.md（球坐标/Laplacian）
- **后续**：12_topics_qm.md（原子物理、散射、量子基础）
- **进阶**：14_qft.md（把单粒子 QM 推广到多粒子场论）
- **AI for Physics**：PINN 解 Schrödinger 方程、NeuralPotentials（神经网络学波函数）
- **对应**：L08 量子力学 + L09 量子力学进阶

## §8 延伸阅读
- 读完 → 12 Topics in QM（原子物理 + 散射 + 量子基础）
- 教材 → Griffiths *Introduction to Quantum Mechanics*（最经典本科教材，和 Tong 互为补充）
- 教材 → Sakurai *Modern Quantum Mechanics*（研究生标准，更形式化，以自旋开头）
- 直觉 → Feynman 讲义卷 3（用最直觉的方式引入 QM）
- 历史 → 《上帝掷骰子吗》（曹天元，中文最好的 QM 科普）
- 深入 → Shankar *Principles of Quantum Mechanics*（全面严谨，Dirac 符号从头讲）
- 数学 → Cohen-Tannoudji *Quantum Mechanics*（最详尽的本科教材，两卷）

## §9 学习建议
- **节奏**：6-8 周（155 页，但需要大量习题）
- **怎么读**：每章至少做 5-8 道习题——量子力学是"做"出来的，不是"看"出来的。特别是谐振子升降算符方法，必须自己推一遍
- **陷阱**：
  - 不要把波函数当成"实体波"——它是概率幅（复数），不是物理波动
  - 测量坍缩不是决定论的——这是量子力学与经典物理的根本区别
  - 自旋没有经典对应——不要试图用"小球旋转"来理解
  - 全同粒子的交换对称性不是"近似"——它是精确的原理，但只有在粒子真正不可区分时才有效
  - 微扰论中分母为零（简并）时直接用公式会发散——需要简并微扰论
- **关键洞察**：量子力学的核心是**叠加原理 + 概率诠释 + 不可对易的观测量**。经典力学中 $x$ 和 $p$ 可以同时确定，量子力学中 $[\hat{x}, \hat{p}] = i\hbar \neq 0$ 导致不确定性原理。理解了这一点，你就理解了量子力学与经典力学的本质区别。

## §10 常见误区（深化新增）

### 🕳️ 误区 1：波函数是物理波动
- ❌ "波函数像水波一样是实在的物理波动"
- ✅ 波函数是**概率幅**（复数），$|\psi|^2$ 才是概率密度。$\psi$ 本身**不可直接观测**——不同整体相位给出相同物理。但相对相位（相位差）可观测，导致干涉。

### 🕳️ 误区 2：量子隧穿违反能量守恒
- ❌ "粒子隧穿时'借用'了能量穿过势垒"
- ✅ 隧穿中能量**严格守恒**。"借能量"是海森堡不确定性 $\Delta E\Delta t$ 的错误经典类比。量子力学中能量是守恒的好量子数（若 $H$ 不显含时间）。隧穿是波函数延伸到经典禁戒区的自然结果。

### 🕳️ 误区 3：自旋是小球在旋转
- ❌ "电子自旋就是电子这个小球在自转"
- ✅ 自旋**无经典对应**。如果电子是半径为经典电子半径的小球，要产生观测到的磁矩，表面速度需 $v > c$（违反相对论）。自旋是相对论量子力学（Dirac 方程）的**内禀性质**，是 SU(2) 表示论的体现，不是机械旋转。

### 🕳️ 误区 4：测量坍缩是物理过程
- ❌ "坍缩是一个可以用方程描述的物理过程"
- ✅ 坍缩的机制**至今未解**（量子力学的诠释问题）。哥本哈根诠释说"测量时坍缩"，多世界诠释说"没有坍缩而是分支"，退相干理论说"与环境纠缠"。目前无定论——这是量子基础研究的核心问题。

### 🕳️ 误区 5：不确定性原理是测量精度的限制
- ❌ "粒子其实有确定的 $x$ 和 $p$，只是我们测不准"
- ✅ 不确定性是粒子的**内禀性质**。即使不测量，粒子也不具有同时确定的 $x$ 和 $p$——因为 $[\hat{x},\hat{p}]=i\hbar\neq0$，两者**没有共同本征态**。这不是技术限制，是自然规律。

## §11 与其他量子力学教材的对比（深化新增）

| 教材 | 风格 | 适合谁 | vs Tong |
|------|------|--------|---------|
| **Griffiths** *Intro to QM* | 清晰友好，习题经典 | 本科主教材 | 与 Tong 互补，Griffiths 更详细（散射/微扰）|
| **Sakurai** *Modern QM* | 形式化，以自旋开头 | 研究生标准 | 比 Tong 更深更抽象，强调对称性 |
| **Shankar** *Principles of QM* | 全面严谨，Dirac 符号从头讲 | 想扎实学一遍 | 比 Tong 更全，数学基础铺垫充分 |
| **Cohen-Tannoudji** *QM*（两卷）| 最详尽，大量补充材料 | 想当参考书 | 比 Tong 厚得多，适合查阅 |
| **Feynman Lectures** vol 3 | 最直觉，物理洞察多 | 想要"啊哈"时刻 | 比 Tong 更散文化，思想实验精彩 |
| **Landau & Lifshitz** *QM* | 理论物理教程风格 | 想看最深 | 凝练极深，从对称性原理出发 |

**建议组合**：**Tong（主读）+ Griffiths（做题）+ Shankar（补数学）** = 量子力学自学三件套。

---

**完成日期**：2026-08-13（深化版 v2，从 144 行扩到 ~310 行）
**配套**：[tong/README.md](README.md) + [TEMPLATE.md](../TEMPLATE.md) + [ai_for_physics/](../../ai_for_physics/)
