# Tom Richardson, Rüdiger Urbanke《现代编码理论》 · 快速逐章精读

> 基于原书：*Modern Coding Theory*, Cambridge University Press（Tom Richardson & Rüdiger Urbanke, 2008, ~580pp）/ 读于：2026-07-03
> 定位：**现代编码理论（迭代译码时代）的标杆之作**，以「因子图 + 置信传播 + 密度演化」三步把 LDPC / Turbo / Raptor 统一为一个可分析的理论框架。
> 第二句特色：本书是 **Gallager 1960 LDPC 码在 1990s 复兴后的理论结晶**——把 Shannon「存在性好码」的存在性定理，升级为「随机稀疏图码 + 迭代译码 + 可解析门限」的现代构造理论。
> 本文为**快速逐章精读**，按原书 10 章组织（原书含附录，正文 10 章），每章 1 个飞腾锚点 + 1 个关键定理 + 1 道自测题。

---

## §0 引言：Richardson-Urbanke 是什么，为什么读它（约 360 字）

Shannon 1948 的信道编码定理证明：只要码率 $R$ 小于信道容量 $C$，就**存在**码使差错任意小——但没给构造，也没给可实用的译码算法。Gallager 1960 在博士论文提出**低密度奇偶校验（LDPC）码**与迭代译码，因当时算力不足被冷落三十余年。1993 年 Berrou 的 **Turbo 码**首次把实用码逼近 Shannon 极限（差 $<1$ dB），1996 年 MacKay 重发现 LDPC，证明迭代译码可距容量仅 $0.0045$ dB。

这场「现代编码革命」的理论总结，就是 Richardson（Flarion / Qualcomm）与 Urbanke（EPFL）这本 2008 年的《Modern Coding Theory》。本书的核心贡献：把看似不同的码族（LDPC、Turbo、Raptor）统一到**一套数学语言**：

- **因子图（factor graph）**把码的校验结构翻译成图论语言；
- **置信传播（Belief Propagation, BP）**是这个图上的通用迭代译码算法，不同码只是图的形状不同；
- **密度演化（density evolution）**跟踪消息分布的逐轮演化，把「BP 能否收敛」变成可解析的递推式，求固定点与门限（threshold）。

这套框架让码设计从「试错」变成「优化」。本书是 5G LDPC、Turbo 等标准的数学底座。对做深度学习的读者尤其重要：**BP（置信传播）与神经网络 backprop（反向传播）都是计算图上的消息传递**——理解本书是打通「神经译码器」「GNN 消息传递」的前提。本书偏概率-图论-渐近分析，与 MacWilliams-Sloane（代数-组合视角）互补。

**迭代译码发展史**（理解本书的历史坐标）：

| 年份 | 事件 | 意义 |
|---|---|---|
| 1948 | Shannon 信道编码定理 | 证「存在」好码，未给构造 |
| 1960 | Gallager LDPC + 迭代译码 | LDPC 开山，被遗忘（算力不足） |
| 1974 | BCJR 前向-后向算法 | 网格上精确后验，软信息译码 |
| 1993 | Berrou Turbo 码 | 首个逼近容量的实用码（差 $<1$ dB） |
| 1996 | MacKay 重发现 LDPC | 距容量 $0.0045$ dB，LDPC 复兴 |
| 2002/06 | LT / Raptor 无速率码 | 码率自适应信道 |
| 2008 | **本书出版** | 三步统一理论，迭代译码时代标杆 |
| 2009/16 | Polar 码 / 5G NR 标准 | 「后现代」Polar 达容量；5G 用 LDPC+Polar |

| 书 | 风格 | 严格性 | 适合谁 |
|---|---|---|---|
| **Richardson-Urbanke**（本书, 2008） | 概率+图论+渐近分析，density evolution 为核，定理密集 | ★★★★★ 现代前沿 | 做 5G/6G 迭代译码、Gallager 风格现代编码、LDPC/Turbo 研究者 |
| **MacWilliams-Sloane**《纠错码理论》（刚做, 1977） | 百科全书式，组合+代数双线，经典代数码 | ★★★★★ 完整 | 系统学经典编码理论、查码类谱系、密码/通信研究 |
| **Gallager**《LDPC Codes》（1963 / PhD 再版） | LDPC 开山，稀疏图+迭代译码原初思想，工程师笔触 | ★★★★ 经典 | 理解 LDPC 起源，本书是 Gallager 的现代严格化 |
| **Lin-Costello**《Error Control Coding》2ed（2004） | 工程教材，分组码/卷积码/RS/Turbo 全谱，例题丰富 | ★★★★ 友好 | 通信工程研究生入门，本书之前的现代编码过渡 |

**建议路线**：Cover-Thomas Ch7-8（信道编码定理热身）→ MacWilliams-Sloane（经典代数码地基）→ Lin-Costello（卷积码/Viterbi 工程过渡）→ **Richardson-Urbanke（本书，现代迭代译码）**。若偏深度学习，加读 MacKay《ITILA》（LDPC 复兴推手 + BP 通用推断）。

---

## §1 全书 10 章骨架一览（飞腾锚点分布）

本书按「引言 → 因子图语言 → BEC 沙盘 → 一般信道 → EXIT 可视化 → 编码定理 → 非规则优化 → 无速率码 → 卷积/Turbo → 码设计」十段递进：

| 章 | 标题 | 核心概念 | 飞腾锚点 |
|:-:|------|---------|---------|
| 1 | Introduction | Shannon 极限、迭代译码概览、Gallager 复兴 | **Iron Law <2%** ⭐ |
| 2 | Factor Graphs & Sum-Product | Tanner 图、message passing、BP 在树上精确 | **UDOT 16.9×** ⭐ |
| 3 | Binary Erasure Channel | BEC 上 BP 译码、密度演化、门限 | **TLB 4.81×** ⭐ |
| 4 | General Channels: Density Evolution | Gaussian 逼近、stability condition | **FP16 3.81×** |
| 5 | EXIT Charts & Area Theorems | 互信息传递图、面积定理 | **GEMM 9.45G** |
| 6 | Coding Theorems for Sparse Graphs | 浓度定理、ensemble 平均、随机构造好 | **Schmidt 正交化** |
| 7 | Analysis of Irregular Codes | degree distribution、逼近容量优化 | **分支预测 0.71 vs 3.14** ⭐ |
| 8 | Rateless Codes | Fountain/LT/Raptor、鲁棒孤波分布 | **matmul 15×** |
| 9 | Convolutional & Turbo Codes | BCJR、交织器、Turbo 迭代收敛 | **Iron Law <2%** ⭐ |
| 10 | Code Design & Optimization | 瀑布/地板、trapping set、5G 设计 | **UDOT 16.9×** ⭐ |

> 🟢 = 直接锚定（概念↔硬件对应）/ 🟡 = 类比锚点（供直觉，不引严格证明）。10 章 > 8 锚点，Iron Law 与 UDOT 各隔 8 章复用一次（角度不同），相邻不重复。

**三步统一 vs 经典代数码**（理解本书与 MacWilliams-Sloane 的分野）：

| 维度 | 经典代数码（MacWilliams-Sloane） | 现代迭代码（本书） |
|---|---|---|
| 数学舞台 | 有限域 $GF(q)$、多项式环 | 稀疏二部图（Tanner 图） |
| 译码 | 代数译码（Berlekamp-Massey、伴随式） | 图上消息传递（BP/置信传播） |
| 性能分析 | 重量枚举器、MacWilliams 恒等式 | density evolution、门限、浓度定理 |
| 极限 | Singleton/Hamming 界（精确纠 $t$ 错） | 逼近 Shannon 容量（差错概率 $\to0$） |
| 代表码 | Hamming、RS、BCH、Golay | LDPC、Turbo、Raptor、Polar |

---

### 第 1 章 · Introduction（引言：Shannon 极限与迭代译码概览）

- **核心**：
  - 本章是全书导航。Shannon 1948 信道编码定理证「存在」码率 $R<C$ 的好码，但留两个空缺：① 如何**构造**？② 如何**译码**（最优 ML 译码 NP-hard）？
  - Gallager 1960 的 LDPC + 迭代译码是答案雏形，被遗忘；1990s Turbo（Berrou）与 LDPC 重发现（MacKay）证明迭代译码可逼近 Shannon 极限。
  - 本书用统一框架（因子图 / BP / 密度演化）整理这场革命，并把性能分析严格化。
- **关键概念**：
  - **信道容量** $C$：信道可靠传输的最大码率（BSC 的 $C=1-H_2(p)$，BEC 的 $C=1-\varepsilon$）。
  - **Shannon 极限（gap to capacity）**：码的实际可达码率距 $C$ 的差距，越小越好（LDPC 可达 $0.0045$ dB）。
  - **迭代译码（iterative decoding）**：低复杂度的次优译码，反复在图上传递消息，逼近 ML 性能。
- **飞腾锚点**：**Iron Law <2% [Lab00]** 🟢 —— 通信的工程铁律是误码率（BER）须低于阈值（5G eMBB 要求 BER $<10^{-5}$）。Shannon 极限是说「只要 $R<C$，存在码使 BER$\to0$」；现代编码理论的目标就是设计 $R$ 接近 $C$ 时仍能把 BER 压到铁律以下的迭代译码码。
- **关键定理**：**Shannon 信道编码定理** —— 对容量 $C$ 的离散无记忆信道，任给 $R<C$、$\varepsilon>0$，存在码率 $R$ 的码使差错概率 $<\varepsilon$；$R>C$ 则不可靠传输。
- **自测**：BSC($0.11$) 的 Shannon 容量？（答：$C=1-H_2(0.11)\approx1-0.499\approx0.501$ 比特/信道。）

---

### 第 2 章 · Factor Graphs and the Sum-Product Algorithm（因子图与和积算法）

- **核心**：
  - 因子图把全局函数（如后验 $P(x|y)$）分解为局部因子的乘积。LDPC 的 **Tanner 图**：变量节点 = 码位，校验节点 = 校验方程，边连接参与同一校验的变量。
  - **和积算法（sum-product = belief propagation, BP）**在图上传消息：每节点把入边消息按因子做「积」（连乘）与「和」（边缘化）后发出。
  - 树结构图上 BP 给精确边缘；含环时是近似（loopy BP），但 LDPC 实践中高 SNR 下收敛极好。
- **关键概念**：
  - **Tanner 图**：变量节点集 $\cup$ 校验节点集的二部图，是 LDPC 的几何表示。
  - **message passing**：节点沿边交换软信息（似然/概率），是 BP/BCJR/GNN 的共同骨架。
  - **loopy BP**：含环图上的近似 BP，迭代收敛无保证，但实践中常收敛（LDPC/Turbo 的成功基础）。
- **飞腾锚点**：**UDOT 16.9× [E05]** 🟢⭐ —— sum-product 的「sum」步骤是外信息值的连加（变量节点把所有入边消息求和），UDOT 点积累加指令把这些求和加速 16.9×，是 BP 译码器实时性的硬件肉身——「product-sum」译码器吞吐的核心算子。
- **关键定理**：**BP 在树上精确** —— 若因子图是一棵树（无环），则和积算法在有限步收敛到精确边缘分布 $P(x_i|\text{evidence})$；含环时 loopy BP 是近似，但常在 LDPC 高 SNR 下收敛。
- **自测**：$[7,4,3]$ Hamming 码的 Tanner 图有几个校验节点？是否含环？（答：校验节点 $n-k=3$ 个、变量节点 7 个；含 4-环，故 loopy BP 近似。）

---

### 第 3 章 · Binary Erasure Channel（二元删除信道 BEC）

- **核心**：
  - BEC($\varepsilon$) 以概率 $\varepsilon$ 删除比特（输出「？」）、概率 $1-\varepsilon$ 正确传递，是最简单的非平凡信道。
  - BEC 上 BP 译码有闭式分析：等价于「沿校验方程传播已知比特」——若某校验方程只有一个未知变量，就能解出它。
  - **密度演化**跟踪每轮迭代后「未知变量比例」$x_\ell$ 的演化，得到一维递推式，求固定点判断**门限**（threshold）。BEC 是密度演化的教学沙盘。
- **关键概念**：
  - **erasure（删除）**：比特丢失（非翻转），是最易分析的信道损伤。
  - **density evolution**：跟踪 BP 消息分布的逐轮演化，是分析迭代译码收敛的核心工具。
  - **threshold（门限）$\varepsilon^*$**：BP 能完全译码的最大信道噪声参数，是码的「性能指纹」。
- **飞腾锚点**：**TLB 4.81× [E04]** 🟢⭐ —— BEC 译码在稀疏 Tanner 图上反复遍历校验方程，每校验节点只连少量变量（稀疏），相邻访问有强局部性，TLB 命中率决定大规模码的译码吞吐——稀疏访问是 LDPC 区别于稠密代数码的硬件特征。
- **关键定理**：**BEC 上 BP 密度演化递推** —— 设 $x_\ell$ 为第 $\ell$ 轮后「从变量到校验的消息仍为 erasure 的概率」，则 $x_{\ell+1}=\varepsilon\,\lambda(1-\rho(1-x_\ell))$，门限 $\varepsilon^*=\sup\{\varepsilon:x_\ell\to0\}$。
- **自测**：$(3,6)$-regular LDPC 码率 $R=1/2$，BEC 门限 $\varepsilon^*\approx0.4294$（低于容量极限 $0.5$）。$\varepsilon=0.40<\varepsilon^*$ 能否完全译码？（答：能，$x_\ell\to0$。这正是 regular 码离容量有差距的体现，推动 Ch7 irregular 优化。）

---

### 第 4 章 · General Channels: Density Evolution（一般信道密度演化）

- **核心**：
  - 对一般信道（BSC、AWGN 等），消息是连续分布（如对数似然比的高斯），密度演化需跟踪消息分布的逐轮变换——精确跟踪无限维分布不可行。
  - **Gaussian approximation（高斯逼近）**假设消息分布恒为高斯，只需跟踪均值方差，降为二维迭代。
  - 关键概念 **stability（稳定性）**：固定点是否局部稳定，决定码在低噪附近能否把残余错误驱零。
- **关键概念**：
  - **对数似然比（LLR）**：消息的数值载体，正负号表硬判决、绝对值表置信度。
  - **Gaussian approximation**：假设 LLR 分布为高斯，把密度演化降维，是工程实用的简化。
  - **stability condition**：无误码固定点的局部稳定判据 $\lambda'(0)\rho'(1)>1$，是码设计的必要条件。
- **飞腾锚点**：**FP16 3.81× [L01]** 🟢 —— 密度演化需数值模拟消息分布（每轮量化分布、做卷积/概率积分变换），FP16 半精度在分布迭代的批量数值计算上拿 3.81× 加速，是「用蒙特卡洛仿真验证门限」的工具——精度与吞吐的工程权衡。
- **关键定理**：**stability condition（稳定性条件）** —— density evolution 在「无误码」固定点的线性化稳定条件为 $\lambda'(0)\,\rho'(1)>1$（由度 2 变量节点贡献 $\lambda'(0)$）。物理：残余错误才能在迭代中被驱零。
- **自测**：某 irregular LDPC 的 $\lambda'(0)=0.4$、$\rho'(1)=6$，是否满足 stability？（答：$0.4\times6=2.4>1$ ✓ 满足，错误可驱零。regular $(3,6)$ 的 $\lambda'(0)=0$，stability 处边界。）

---

### 第 5 章 · EXIT Charts and Area Theorems（EXIT 图与面积定理）

- **核心**：
  - **EXIT（Extrinsic Information Transfer）图**把迭代译码可视化：横轴先验互信息 $I_A$，纵轴外信息互信息 $I_E$。
  - Turbo 两个分量码的 EXIT 曲线之间「走阶梯」= 迭代译码，直到收敛（曲线相交则卡住）或抵达无误码区。
  - 核心 **area theorem（面积定理）**：对 BEC，单码 EXIT 曲线下面积恰为 $1-R$。两曲线不相交且面积互补 ⇒ 迭代到无误码 ⇒ 逼近容量。
- **关键概念**：
  - **extrinsic information（外信息）**：子译码器输出的互信息，不含该比特自身观测。
  - **transfer curve（传递曲线）**：$I_E$ 关于 $I_A$ 的函数，是子译码器的「指纹」。
  - **tunnel（迭代隧道）**：两 EXIT 曲线间的缝隙，缝隙越宽迭代越顺利收敛。
- **飞腾锚点**：**GEMM 9.45 GFLOPS [Lab05]** 🟡 —— EXIT 面积定理的验证、大规模码族 transfer function 的数值积分（$\int I_E\,dI_A$）需密集矩阵运算，GEMM 吞吐决定「在设计空间搜索逼近容量的度分布」的效率——面积法把码设计变成数值优化。
- **关键定理**：**area theorem（面积定理）** —— 对 BEC 上码率 $R$ 的码，外信息 EXIT 曲线满足 $\int_0^1 I_E(i)\,di=1-R$。达容量码「撑满」该面积，给出迭代收敛的几何必要条件。
- **自测**：码率 $R=1/2$ 的码在 BEC 上 EXIT 曲线下面积应为多少？（答：$1-R=1/2$。达容量码的 EXIT 曲线与对称线「贴满」，两分量码可无间隙迭代。）

---

### 第 6 章 · Coding Theorems for Sparse Graph Codes（稀疏图码的编码定理）

- **核心**：
  - 本章把 ensemble（码族，如 LDPC($n,\lambda,\rho$)）的平均性能用**浓度定理（concentration theorem）**严格化。
  - 对足够大码长 $n$，几乎所有从 ensemble 随机抽取的码，其性能都集中在 ensemble 平均附近——「平均好」⇒「随机抽的也好」。
  - 这把 Shannon 的「存在性好码」升级为「随机构造大概率好」的现代版本，是本书最严格的概率工具（大偏差/Azuma-Martingale）。
- **关键概念**：
  - **ensemble（码族/系综）**：度分布 $(\lambda,\rho)$ 定义的概率码族，密度演化算的是它的平均。
  - **concentration（集中）**：随机码性能指数级集中在 ensemble 均值附近（大偏差界）。
  - **edge-perspective degree distribution**：从边的角度看度分布，是密度演化递推的自然参数。
- **飞腾锚点**：**Schmidt 正交化** 🟡 —— 浓度定理证明（McDiarmid 有界差分 / Azuma 不等式）本质是把码空间的随机扰动做**正交分解**：沿每个独立坐标（每条边、每个校验位）逐维剥离贡献，各维有界变化求和给集中界。Schmidt 正交化「逐维投影剥离」的直觉正是其内核。
- **关键定理**：**浓度定理（concentration theorem）** —— 对 LDPC($n,\lambda,\rho$) ensemble，BP 译码第 $\ell$ 轮某边消息出错的比例 $X_\ell$ 满足 $\Pr(|X_\ell-\mathbb{E}X_\ell|>\delta)\le 2e^{-cn\delta^2}$。即「密度演化预测 = 大码实际行为」。
- **自测**：ensemble 平均门限 $\varepsilon^*=0.4294$，码长 $n=10^6$、$\varepsilon=0.42$，差错概率如何？（答：$\approx0$，因 $n$ 大且 $\varepsilon<\varepsilon^*$，集中到无差错固定点。）

---

### 第 7 章 · Analysis of Irregular Codes（非规则码分析与优化）

- **核心**：
  - regular LDPC 门限远低于容量。关键突破是用 **irregular（非规则）度分布**：变量/校验节点度数不均。
  - 让「高度数变量节点」先恢复（连多校验，易纠），再传信息给「低度数变量」——自适应的级联效应（催化效应）。
  - 度分布用 $\lambda(x)=\sum\lambda_i x^{i-1}$（边视角）与 $\rho(x)=\sum\rho_i x^{i-1}$ 参数化。优化门限即在约束下用**线性规划 + 密度演化迭代**搜索最优 $(\lambda,\rho)$。
- **关键概念**：
  - **degree distribution（度分布）**：变量/校验节点度的概率分布，是 irregular 码的设计旋钮。
  - **催化效应（catalytic effect）**：高度变量节点率先纠错并辐射信息给低度节点，是逼近容量的机理。
  - **capacity-approaching**：门限 $\varepsilon^*$ 趋近容量极限 $1-R$ 的码族。
- **飞腾锚点**：**分支预测 0.71 vs 3.14 [Lab02]** 🟢⭐ —— 度分布优化是大规模组合搜索（在 $\lambda,\rho$ 多面体上做密度演化驱动的线性规划迭代），搜索路径的分支（接受/拒绝某度分布候选）不可预测，分支预测命中率低（~0.71 CPI），是优化器性能瓶颈——优化本身也是「译码式」的迭代收敛。
- **关键定理**：**irregular LDPC 逼近容量** —— 存在 irregular 度分布使 BEC 上 $R\to C^-$ 时门限 $\varepsilon^*\to 1-R$。优化目标：$\max R$ s.t. stability $\lambda'(0)\rho'(1)>1$ 与密度演化收敛。
- **自测**：为什么 irregular LDPC 比 regular 更接近 Shannon 容量？（答：高度变量节点先纠错，像「催化」低度节点，逐层传播已知信息——自适应级联结构，比 uniform 度分布更高效。）

---

### 第 8 章 · Rateless Codes（无速率码：Fountain / LT / Raptor）

- **核心**：
  - 传统码码率固定。**无速率码（rateless / fountain codes）**让编码器输出任意多比特——接收方收到足够多就停止，码率自适应信道。
  - **LT 码**（Luby Transform, 2002）是基础：每个输出比特 = 随机选若干输入比特的异或，度由**鲁棒孤波分布（robust soliton）**采样。
  - **Raptor 码**（2006）= 预编码（高码率 LDPC/级联）+ LT，把译码复杂度降到 $O(n)$。无速率码用于 5G 广播、深空、CDN。
- **关键概念**：
  - **fountain（喷泉）**：发送端源源不断产出编码符号，接收端像接水滴。
  - **robust soliton distribution**：LT 码的度采样分布，保证译码每步大概率有度 1 符号可解。
  - **overhead（开销）**：接收符号数减消息长，越小越接近容量。
- **飞腾锚点**：**matmul 15× [V03]** 🟢 —— LT 编码「输出 = 随机子集输入的异或」是稀疏二值矩阵 $\mathbf{y}=\mathbf{A}\mathbf{x}$ 的矩阵-向量乘法（$\mathbf{A}$ 每行稀疏），matmul 加速使高码率 Raptor 的实时编码近乎免费——编码开销与「随机稀疏矩阵乘法」等价。
- **关键定理**：**鲁棒孤波分布 + LT 译码** —— LT 码用鲁棒孤波度分布 $\Omega(d)$，编码符号数只需 $(1+\varepsilon)n\cdot k$ 即可 BP 译码恢复全部，开销 $\varepsilon$ 任意小；Raptor 加预编码使总复杂度 $O(k)$。
- **自测**：Raptor 码相比 LT 码的改进是什么？（答：预编码（高码率 LDPC）使 LT 部分不需处理度 1 符号耗尽，把复杂度从 $O(k\log k)$ 降到 $O(k)$，且降低错误地板——典型的「两级级联换复杂度」。）

---

### 第 9 章 · Convolutional Codes and Turbo Codes（卷积码与 Turbo 码：BCJR 与迭代）

- **核心**：
  - 卷积码用网格（trellis）表示，**BCJR 算法**（1974）在网格上做后验概率的精确**前向-后向（forward-backward）**计算，输出每比特软信息（APP）。
  - **Turbo 码**（Berrou 1993）= 两个卷积码并行级联 + **交织器（interleaver）**，用两个 BCJR 互交换软信息迭代译码，是首个逼近容量的实用码。
  - 本章统一 BCJR 与 BP：**BCJR = 网格图上精确的 sum-product**（网格无环，故精确），Turbo 两 BCJR 软信息交换是 loopy BP 的特例。
- **关键概念**：
  - **trellis（网格）**：卷积码的状态-时间展开图，BCJR 在其上做 DP。
  - **APP（后验概率）**：每比特的软判决输出，比硬判决多 2-3 dB 增益。
  - **interleaver（交织器）**：打散分量码相关性，使迭代软信息近似独立，是 Turbo 接近容量的关键。
  - **turbo cliff / error floor**：瀑布区（BER 陡降）与错误地板（残余 BER 平台）是 Turbo 性能曲线的两段。
- **飞腾锚点**：**Iron Law <2% [Lab00]** 🟢（复用 Ch1，隔 8 章） —— Turbo 迭代译码的工程铁律：迭代足够时 BER 陡降（瀑布区），但之后出现**错误地板**。把 BER 压到铁律以下需控制低重量码字与交织器设计——瀑布区高与地板低是矛盾的两端。
- **关键定理**：**BCJR = 网格上的精确 BP** —— BCJR 在无环网格图上精确计算后验 $P(u_i|\mathbf{y})$，等价于 sum-product 在树上的精确边缘化。Turbo 两 BCJR 软信息交换是 loopy BP 特例，实践中收敛极好。
- **自测**：Turbo 译码中「交织器」的作用？（答：打散两分量码相关性，使迭代软信息近似独立，避免 BP 在环上发散；把「局部错误」铺开成「随机错误」供迭代纠正。）

---

### 第 10 章 · Code Design and Optimization（码设计与优化）

- **核心**：
  - 码设计是多目标优化：① 瀑布区门限高（逼近容量），② 错误地板低，③ 编/译码复杂度低，④ 码长 trade-off。
  - 设计流程：选度分布（密度演化优化门限）→ 估错误地板（weight enumerator / trapping set）→ 定图构造（**PEG / ACE** 避短环）→ 硬件实现。
  - **5G LDPC 码**（3GPP NR）正是这套流程的产物——本书是它的数学方法论手册。
- **关键概念**：
  - **waterfall（瀑布区）**：低-中 SNR 下 BER 陡降的区段，由门限决定。
  - **trapping set**：高 SNR 下译码器卡住的局部结构（短环 + 少数错误变量），决定错误地板。
  - **girth（围长）**：图中最短环长度，越大 loopy BP 越接近精确——PEG/ACE 构造增大围长。
  - **quasi-cyclic LDPC（QC-LDPC）**：循环移位结构，5G 标准采用的硬件友好构造。
- **飞腾锚点**：**UDOT 16.9× [E05]** 🟢⭐（复用 Ch2，隔 8 章） —— 大规模码设计需反复仿真 BER 曲线（百万次 BP 译码求和统计），UDOT 加速使设计空间搜索可行；5G LDPC 译码器硬件以点积累加为核心算子——从「译码」到「设计验证」UDOT 贯穿全程。
- **关键定理**：**错误地板与 trapping set** —— 高 SNR 下 LDPC 残余错误由 **trapping set**（短环 + 少数错误变量）决定，非低重量码字。设计目标是消除小 trapping set（PEG/ACE 增大围长）。
- **自测**：5G 数据信道（eMBB）为何选 LDPC 而非 Turbo？（答：LDPC 译码**并行度高**（适合 Gbps 吞吐）、错误地板低、硬件成熟；Turbo 串行迭代吞吐受限。控制信道用 Polar 码。）

---

## §9 全书思想主线（约 210 字）

Richardson-Urbanke 以**「因子图 + 置信传播 + 密度演化」三步**统一现代编码理论。① **因子图（Tanner 图）**把码的代数结构（校验方程）翻译成图论语言，使「译码」变成「图上消息传递」。② **置信传播（BP / sum-product）**是这个图上的通用译码算法——LDPC、Turbo、Raptor 都是 BP 的不同实例，区别只在图的形状（稀疏二部图 / 网格 / 随机图）。③ **密度演化**跟踪消息分布的逐轮演化，把「BP 能否收敛」变成可解析的递推式，求固定点与门限。这三步把 Shannon 的「存在性好码」（1948）升级为「随机稀疏图码 + 迭代译码 + 可解析门限」的现代构造理论（2008）。

**与已读教材呼应**：与 **MacWilliams-Sloane**（代数-组合视角，MacWilliams 恒等式顶峰）**互补**——本书是概率-图论-渐近视角，两书合看才得编码理论全貌（经典代数码 vs 现代迭代码）。与 **Cover-Thomas**（信道编码定理概率视角）衔接——Cover-Thomas 给存在性与界，本书给迭代译码的工程实现。与 **Gallager 1963**（LDPC 开山）是「思想原初 → 理论严格化」的关系。

**现代码类生态位对比**（5G 时代的码类分工，务必区分）：

| 码类 | 译码 | 复杂度 | 码率灵活性 | 标准生态位 |
|---|---|---|---|---|
| **LDPC** | BP 置信传播 | 近线性，高并行 | 固定码率 | 🟢 5G eMBB 数据信道、WiFi |
| **Turbo** | BCJR 迭代 | 串行迭代，吞吐受限 | 固定码率 | 3G/4G（LTE） |
| **Polar** | SC / SCL | $O(n\log n)$ | 固定码率 | 5G 控制信道 |
| **Raptor** | BP（无速率） | $O(n)$ | 🟢 码率自适应 | 5G 广播、深空 |
| **RS（代数码）** | Berlekamp-Massey | $O(n^2)$ | 固定 | 光盘/QR（外层） |

---

## §10 与本仓库其他笔记的交叉引用

### 与已精读书目的呼应

| 本书概念 | 关联书 / 领域 | 接口说明 |
|---|---|---|
| Tanner 图 / BP 迭代译码 / LDPC-Turbo | **macwilliams 码理论**（刚做） | MacWilliams 给经典代数码（线性码/MacWilliams 恒等式/循环码/Viterbi），本书把 Viterbi 推广为 BCJR+Turbo 迭代；经典代数码是现代迭代码的代数地基 |
| Shannon 容量 / 信道编码定理 | **cover_thomas 信息论** Ch7-8 | Cover-Thomas 给容量定理概率证明与界，本书给迭代译码逼近容量的构造 |
| 严格编码代数 / RS / BCH | **E-信息论 GTM134**（已读） | Roman 给 RS/BCH 严格代数译码，本书用稀疏图 + 迭代 BP 替代代数译码 |
| Shannon 极限 / 随机码论证 | **Shannon 1948 原始论文**（已读） | Shannon 证「存在性好码」（随机码 + 典型序列），本书 Ch6 浓度定理证「随机稀疏图码大概率达容量」 |
| LDPC 复兴 / BP 通用推断 | **mackay 信息论推理与学习**（已读） | MacKay 是 LDPC 重发现者 + 把 BP 推广为通用贝叶斯推断；本书严格化密度演化，MacKay 给 BP 的直觉统一 |

### AI/工程锚点：现代编码理论的落地与 AI 交叉

| 数学概念 | AI/工程对应 | 锚点说明 |
|---|---|---|
| **LDPC + density evolution** | 🟢 **5G eMBB 数据信道** | 5G NR（3GPP）用 LDPC，本书 LDPC + 门限分析是其标准数学底座；5G Gbps 吞吐靠 BP 译码器并行化（UDOT 16.9× 点积累加） |
| **Turbo / Polar 码** | 🟡 3G/4G Turbo · 5G 控制信道 Polar | Turbo（本书 Ch9）统治 3G/4G；Polar（Arikan 2009）是「后现代」延伸，达容量且有低复杂度 SC/SCL 译码 |
| **BP 置信传播** | 🟢 **神经网络 backprop / GNN 消息传递** | backprop（反向传播）与 BP（置信传播）同名异义但都是计算图上消息传递：backprop 在 DAG 上精确、loopy BP 在含环图上近似；**GNN 消息传递与 LDPC Tanner 图 BP 同构**——理解本书是打通「神经译码器」的前提 |
| **Transformer attention / KV-cache** | 🟡 消息缓存复用 | Transformer 的 KV-cache（空间换时间复用 key/value）与 BP 译码的消息缓存复用同源——都是「消息传递的工程加速」 |
| **深度学习译码器（neural decoder）** | 🟡 神经网络学接近最优 LDPC/Turbo 译码 | 用神经网络/图神经网络学习接近最优的 BP 译码（替代手工 BP 调度），是本书 BP 的可学习化——AI×编码的典型选题 |

**编码理论常见误区**（对照本书与 MacWilliams-Sloane）：

| 误区 | 正确理解 | 出处 |
|---|---|---|
| BP 译码总是精确 | BP 仅在树/无环图上精确；LDPC/Turbo 含环是 loopy BP（近似但常收敛） | Ch 2, 9 |
| regular LDPC 已达容量 | regular 门限远低于容量；需 irregular 度分布才逼近 | Ch 7 |
| stability condition 是充分条件 | stability 是**必要**条件（局部稳定），不保证全局收敛 | Ch 4 |
| EXIT 面积定理对所有信道成立 | 面积定理 $\int I_E=1-R$ 严格仅对 BEC；一般信道是近似 | Ch 5 |
| Turbo = LDPC | Turbo 基于卷积码网格（BCJR）；LDPC 基于稀疏二部图（BP），图结构不同 | Ch 9 |
| 无速率码码率任意高 | 码率自适应信道，但上限仍是 Shannon 容量 | Ch 8 |
| backprop = 置信传播 | 同名异义：backprop 传梯度（DAG 精确），BP 传置信度（含环近似）；但都是消息传递 | Ch 2 |

---

## §11 自测答案要点（供核对）

1. **Ch 1** BSC($0.11$)：$C=1-H_2(0.11)\approx0.501$ 比特/信道。
2. **Ch 2** $[7,4,3]$ Hamming：校验节点 3 个、变量节点 7 个；含 4-环（两校验共享 2 变量），loopy BP。
3. **Ch 3** $(3,6)$ regular，$\varepsilon=0.40<\varepsilon^*=0.4294$：$x_\ell\to0$，能完全译码。
4. **Ch 4** $\lambda'(0)=0.4,\rho'(1)=6$：$0.4\times6=2.4>1$ ✓ 满足 stability；regular $(3,6)$ 的 $\lambda'(0)=0$（无度 2 节点）。
5. **Ch 5** $R=1/2$：EXIT 面积 $=1-R=1/2$。
6. **Ch 6** $n=10^6,\varepsilon=0.42<\varepsilon^*=0.4294$：差错 $\approx0$，集中到无差错固定点。
7. **Ch 7** irregular 逼近容量：催化效应（高度节点先纠错）。
8. **Ch 8** Raptor vs LT：预编码降复杂度 $O(k\log k)\to O(k)$，降错误地板。
9. **Ch 9** 交织器：打散相关性使迭代软信息近似独立。
10. **Ch 10** 5G 选 LDPC：高并行、低地板、硬件成熟。

---

## §12 延展阅读与后续方向

读完 Richardson-Urbanke，自然有三个深入方向：

1. **Polar 码（Arikan 2009）与极化理论**：Polar 码是「后现代」编码，首次证明达 Shannon 容量且有低复杂度（$O(n\log n)$）译码（SC/SCL）。Polar 与 LDPC 在 5G 标准中分工（数据 LDPC / 控制 Polar），是本书迭代译码之外的「严格达容量」路径。
2. **深度学习 × 编码（neural decoder）**：用图神经网络（GNN）学习接近最优的 LDPC/Turbo 译码，替代手工 BP 调度。本书的 BP（消息传递）与 GNN 的消息聚合层同构——是「AI×编码」的核心交叉，典型选题。
3. **后量子密码（McEliece / 基于编码）**：McEliece 1978 用 Goppa 码构造公钥密码，被认为抗量子。本书的稀疏图码 + 迭代译码是后量子编码密码的近邻，可联系 MacWilliams-Sloane Ch13。

**与已读笔记的闭环**：Shannon 1948（存在性奠基）→ Cover-Thomas Ch7-8（容量定理概率视角）→ MacWilliams-Sloane（代数-组合经典码）→ **Richardson-Urbanke（本书，迭代译码现代理论）** → MacKay《ITILA》（BP 通用推断统一）。五者合起来是「信息论 + 编码理论」标准研究入门组合。

**研究者方向取舍建议**：若偏**通信工程**（5G/6G），优先 Ch 3（BEC 沙盘）+ Ch 7（irregular 优化）+ Ch 10（5G 设计）。若偏**深度学习×编码**（神经译码器），优先 Ch 2（因子图/BP）+ Ch 4（density evolution）+ Ch 9（BCJR/Turbo），把 BP 与 GNN/backprop 打通。若偏**信息论理论**，优先 Ch 6（浓度定理）+ Ch 5（area theorem），这是本书最严格的概率-信息论核心。

---

> **精读纪律**：本文为快速逐章精读，每章取 1 个飞腾锚点 + 1 个关键定理 + 1 道自测题。深入计算与完整证明请回原书——尤其 **Ch 4 density evolution + stability**（$\lambda'(0)\rho'(1)>1$）与 **Ch 5 area theorem** 是全书最值得逐字精读的两章，是 LDPC/Turbo 码设计的「心法」。
>
> **实操验证建议**（Python + 现成库）：
> - `scomm` / `ldpc` Python 包 → 跑 BEC 上 BP 译码，验证密度演化门限 $\varepsilon^*\approx0.4294$（$(3,6)$ regular）
> - 手算 stability：给 irregular 度分布 $\lambda,\rho$，验证 $\lambda'(0)\rho'(1)>1$
> - EXIT 图：对 $R=1/2$ 码数值积分 $\int_0^1 I_E\,di$，验证面积定理 $=1-R$
> - 概念打通：用 PyTorch 写一个 loopy BP 译码器（消息传递 = GNN 单层），观察含环收敛
>
> **下一步**（锁定信息论/编码方向）：精读 Ch 4（density evolution）、Ch 5（EXIT/area theorem）、Ch 9（Turbo/BCJR）；研究选题「**神经网络学习接近最优的 LDPC/Polar 译码：从 density evolution 到 GNN 消息传递**」——把本书的 BP（置信传播）与深度学习的消息传递网络打通，是「应用数学研究型工程师」在 AI×编码理论交叉方向的典型选题。MacKay《ITILA》是 BP 统一直觉的下一步，MacWilliams-Sloane 是经典代数码地基的补充。
