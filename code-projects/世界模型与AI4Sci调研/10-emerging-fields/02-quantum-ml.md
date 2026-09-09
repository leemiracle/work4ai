# 量子机器学习：现状、突破与 hype 之间的真相

> 专题 #2 · Emerging Fields 卷 · Quantum Machine Learning
> 撰写日期：2026-07-20 · 所有 arXiv / Nature 文献一手核实

---

## 引言：在两极之间寻找真相

「量子计算 + 机器学习」可能是当今科技舆论里被炒作得最严重的组合之一。一方面，量子计算公司、AI 巨头和媒体把每一次量子芯片发布都说成「颠覆在即」；另一方面，很多经典 ML 从业者嗤之以鼻，认为「量子 ML 永远不会有用」。本文的目标，是把这两种声音都按住，回到**物理、算法、工程**三层事实，看清楚量子机器学习（Quantum Machine Learning, QML）到底走在了哪里、卡在了哪里、值得不值得一个普通人投入。

一句话先给出结论：**量子计算是一门真实且在 2024–2025 年取得突破性进展的科学，但量子机器学习作为它的一个应用分支，目前仍处于「理论上诱人、工程上困难、商业上过早」的阶段。** 真正的量子优势，未来十年最可能先出现在**化学模拟、材料科学、密码学**这些「量子原生」任务上，而不是在大家更熟悉的文本生成、图像识别这类经典 ML 任务上。这个判断的依据，会在下面 13 节里逐层展开。

---

## 1. 历史：从 Feynman 的一个直觉到 NISQ 时代

量子机器学习不是凭空冒出来的，它站在四十多年量子计算史的最顶端。理解这条时间线，才能理解今天 QML 为什么是这副模样。

**1981–1982：Feynman 的关键直觉。** 物理学家 Richard Feynman 在 1981 年的 MIT 第一届「Physics of Computation」会议上提出一个深刻的问题：用经典计算机模拟量子系统是指数昂贵的，因为量子态空间的维度随粒子数指数增长——n 个粒子就有 2ⁿ 个复振幅。他在 1982 年正式撰文论述：**「自然界不是经典的，所以如果你想模拟自然，你最好造一台按量子力学规律工作的计算机。」** 这就是「量子模拟器」构想的源头。这一思想不是天马行空，它直接对应了一个今天仍统治整个领域的设计哲学——**用原生的量子硬件去处理量子的数据**，而不是用经典比特硬模拟量子振幅。这个哲学，正是后面要讲的 CC/CQ/QC/QQ 四象限里最右那一列（量子数据）的思想源头。

**1994：Shor 算法。** Bell 实验室的 Peter Shor 在 1994 年 FOCS 会议上证明，量子计算机可以在多项式时间内分解大整数、求离散对数。这篇论文后来正式发表，arXiv 编号 `quant-ph/9508027`：

> 论文：Peter W. Shor, *Polynomial-Time Algorithms for Prime Factorization and Discrete Logarithms on a Quantum Computer* [SIAM J. Sci. Comput. 26:1484, 1997 / arXiv:quant-ph/9508027](https://arxiv.org/abs/quant-ph/9508027)

Shor 算法的震撼在于：RSA、ECC 等几乎所有现代公钥密码都建立在「大整数分解和离散对数对经典计算机是困难的」这一假设上。如果量子计算机真的造出来并足够大，整个互联网的密码基础设施会被一夜推翻。**这是把量子计算从理论物理推到国家战略层面的关键事件**——美国 NSA、NIST 从 2015 年前后就开始认真部署后量子密码。

**1996：Grover 算法。** Lov Grover 给出无结构数据库搜索的平方根加速：

> 论文：Lov K. Grover, *A Fast Quantum Mechanical Algorithm for Database Search* [STOC 1996:212-219 / arXiv:quant-ph/9605043](https://arxiv.org/abs/quant-ph/9605043)

Grover 算法把 N 项搜索从 O(N) 降到 O(√N)，看起来没有 Shor 那么戏剧化，但它的普适性极强：任何需要「在大量可能性里找少数正确解」的问题（密码学暴力破解、组合优化、NP 类问题的搜索子程序）都能套上 Grover 框架拿到平方根加速。这也是为什么 QML 里很多「加速」其实只是 Grover 加速的变形。

**2009：HHL 算法。** Harrow、Hassidim、Lloyd（HHL）证明量子计算机可以指数级快地求解（满足一定条件的）线性方程组 Ax=b：

> 论文：Aram W. Harrow, Avinatan Hassidim, Seth Lloyd, *Quantum Algorithm for Solving Linear Systems of Equations* [Phys. Rev. Lett. 103:150502, 2009 / arXiv:0811.3171](https://arxiv.org/abs/0811.3171)

HHL 是 QML 的「理论核武器」：很多 ML 算法（SVM、最小二乘回归、主成分分析、推荐系统）的数学核心都是解线性方程组或做矩阵运算，所以 HHL 一度被夸大为「量子计算能指数加速一切 ML」。但 HHL 有三个经常被媒体忽略的隐藏前提——稀疏矩阵、条件数小、量子态读出代价——这些前提在真实数据上几乎从不同时满足，所以 HHL 的「指数加速」在现实中很难兑现。这个落差是理解 QML hype 的关键，后面会专门展开。

**2013–2014：VQE 与 QAOA。** 在硬件受限的现实下，研究者转向「量子-经典混合」（hybrid variational）算法。Peruzzo 等人 2014 年提出变分量子特征值求解器（VQE），用一小段浅量子电路加经典优化器去逼近分子的基态能量：

> 论文：Alberto Peruzzo et al., *A Variational Eigenvalue Solver on a Quantum Processor* [Nature Communications 5:4213, 2014 / arXiv:1304.3061](https://arxiv.org/abs/1304.3061)

同年 Farhi 等人提出量子近似优化算法（QAOA），用类似的变分思想处理 MaxCut 等组合优化问题：

> 论文：Edward Farhi, Jeffrey Goldstone, Sam Gutmann, *A Quantum Approximate Optimization Algorithm* [arXiv:1411.4028, 2014](https://arxiv.org/abs/1411.4028)

**这两个算法彻底改变了量子算法的范式：从「等容错量子计算机造好」转向「在当前噪声设备上就能试」。** 这是 NISQ 时代的精神起点。

**2018：NISQ 时代正式命名。** John Preskill 在 2017 年底的一个演讲里提出 NISQ（Noisy Intermediate-Scale Quantum，噪声中等规模量子）一词，并整理成论文：

> 论文：John Preskill, *Quantum Computing in the NISQ Era and Beyond* [Quantum 2:79, 2018 / arXiv:1801.00862](https://arxiv.org/abs/1801.00862)

Preskill 在文章里写了一句被反复引用的话：「100-qubit quantum computer will not change the world right away」。他清醒地指出：噪声会限制电路深度，所以近期量子设备主要用来探索多体物理，离商业化还很远。这篇论文定义了一个时代的自我认知——**「我们已经进入了量子时代，但还远没有进入实用的量子时代。」**

**2018–：量子 AI 兴起。** 同年，两个标志性事件把量子计算和机器学习绑在一起：一是 McClean 等人发现「贫瘠高原」（barren plateaus）现象，揭示了变分量子算法的根本训练难题；二是 Havlíček 等人在 IBM 超导处理器上首次实验演示量子核方法。从这一年起，量子 ML 成为量子计算里最活跃的子方向之一。本专题的下半部分，就是从这一年开始的。

---

## 2. 量子计算基础：qubit、叠加、纠缠、干涉

要看懂 QML，必须先有一套量子计算的「硬件常识」。这里给最小够用的版本。

### 2.1 Qubit 与 Bloch 球

经典比特只有 0 或 1 两个状态。量子比特（qubit）的「0 态」记作 |0⟩，「1 态」记作 |1⟩（狄拉克记号），它的一般状态是这两个基态的**复线性组合**：

$$|\psi\rangle = \alpha|0\rangle + \beta|1\rangle, \quad \alpha,\beta \in \mathbb{C}, \quad |\alpha|^2 + |\beta|^2 = 1$$

|α|² 和 |β|² 分别是测量时得到 0 和 1 的概率，归一化条件保证概率之和为 1。这个「系数是复数」和「测量时塌缩」两件事是量子态区别于经典概率分布的核心——经典掷硬币也有 0.5/0.5 的概率，但它的状态空间只有 [0,1] 上一个点，而 qubit 的状态空间是复二维单位球面，是一个连续流形。

**Bloch 球**就是把单 qubit 的所有可能状态画在单位球面上：

$$|\psi\rangle = \cos\frac{\theta}{2}|0\rangle + e^{i\varphi}\sin\frac{\theta}{2}|1\rangle$$

|0⟩ 是北极，|1⟩ 是南极，赤道上是 |0⟩ 和 |1⟩ 的等权叠加（相位不同）。单 qubit 的任何操作都对应 Bloch 球面的一次旋转——这是几何直觉的来源。注意：**Bloch 球只对单 qubit 有效**，多 qubit 的态空间无法这样画，因为存在纠缠。

### 2.2 叠加、纠缠、干涉

量子计算的「魔力」全部来自三件事，缺一不可：

**叠加（superposition）。** 一个 qubit 可以同时「是 0 又是 1」。但这话被滥用得很厉害——更准确的说法是：qubit 处于 |0⟩ 和 |1⟩ 的线性组合，**直到被测量才塌缩成某一个**。叠加本身不神奇，神奇的是叠加组合上纠缠和干涉能产生经典算不出的概率分布。n 个 qubit 的状态可以写成：

$$|\psi\rangle = \sum_{x \in \{0,1\}^n} \alpha_x |x\rangle, \quad \sum_x |\alpha_x|^2 = 1$$

这里有 2ⁿ 个复振幅——**状态空间维度随 qubit 数指数增长**，这正是 Feynman 当年的核心观察，也是量子并行性的来源。

**纠缠（entanglement）。** 多 qubit 系统的状态里，存在一类无法写成各 qubit 状态乘积的态。最著名的是 Bell 态：

$$|\Phi^+\rangle = \frac{|00\rangle + |11\rangle}{\sqrt{2}}$$

这个态「不能」写成 (α|0⟩+β|1⟩)⊗(γ|0⟩+δ|1⟩) 的形式——它整体性更强，测量第一个 qubit 得到 0，第二个 qubit 必然也是 0；得到 1，第二个也是 1。爱因斯坦称这种现象为「鬼魅般的超距作用」（spukhafte Fernwirkung），并和 Podolsky、Rosen 在 1935 年提出 EPR 悖论，试图以此证明量子力学不完备。但 1964 年 Bell 提出不等式，2022 年诺贝尔物理学奖（Aspect、Clauser、Zeilinger）最终确认**纠缠是真实的、不可还原为经典隐变量的物理现象**。纠缠是量子通信、量子密钥分发、量子隐形传态的物理基础。

**干涉（interference）。** 这是量子算法真正取得加速的机制，也是外行最容易忽略的。叠加给了量子计算机同时处理 2ⁿ 个分量的能力，但如果你直接测量，你只是按 |α_x|² 的概率随机采到一个 x，没有任何加速。**真正的加速来自让「正确的答案」的概率振幅相长干涉（constructive interference）、让「错误的答案」相消干涉（destructive interference）**，从而在测量时高概率地塌缩到正确解。Shor 算法的量子傅里叶变换、Grover 算法的振幅放大、HHL 算法的相位估计，本质上都是精心设计的干涉图案。**叠加是原料，干涉是工艺，纠缠是纽带**——三者缺一，量子计算就退化成一个昂贵的随机数发生器。

### 2.3 量子门 vs 经典门

经典计算机用 NAND、AND、OR 等逻辑门操作比特。量子计算机用量子门操作 qubit，量子门是**酉变换**（unitary transformation），即满足 U†U = I 的复矩阵——它必须保持概率归一化，所以是可逆的（每个量子门都有逆门）。

最常用的几个：

- **Hadamard 门 H**：把 |0⟩ 变成 (|0⟩+|1⟩)/√2，把 |1⟩ 变成 (|0⟩−|1⟩)/√2。它是制造叠加的工具：

$$H = \frac{1}{\sqrt{2}}\begin{pmatrix}1 & 1 \\ 1 & -1\end{pmatrix}$$

- **Pauli 门 X / Y / Z**：对应 Bloch 球绕 x/y/z 轴转 180°。X 门就是量子版 NOT（|0⟩↔|1⟩）。
- **相位门 S、T**：引入相位，是构造干涉图案的零件。
- **CNOT 门**（两 qubit）：如果控制位是 |1⟩，就翻转目标位。CNOT 是制造纠缠的标准工具——把 H|0⟩=(|0⟩+|1⟩)/√2 作为控制位、|0⟩ 作为目标位输入 CNOT，输出就是 Bell 态 |Φ+⟩。
- **Toffoli 门**（三 qubit）：双控制 NOT，是经典可逆计算的通用门，证明量子计算至少不弱于经典计算。

一个深刻的事实是：**任意多 qubit 的酉变换都可以用 H、T、CNOT 这一组通用量子门任意精确逼近**（Solovay-Kitaev 定理）。这是量子计算的「通用性」，对应经典计算的 NAND 通用性。但代价是：把一个一般酉变换分解成基本门可能需要指数多的门——这就是「电路深度」问题，也是 NISQ 时代最大的工程约束。

### 2.4 Shor 算法：破解 RSA

Shor 算法的核心是把「分解大整数 N」转化为「求函数 f(x)=aˣ mod N 的周期 r」。一旦知道 r，用经典的最大公约数算法就能高概率地分解 N。经典求周期需要 O(N) 级别（或更精细的数筛法 sub-exponential），而量子部分可以在 O((log N)³) 内求出周期——**指数加速**。

量子求周期的关键步骤是**量子傅里叶变换（QFT）**，它把周期信号在频域集中到一个尖峰，干涉使得正确周期高概率被测量到。整个算法需要数百万到数十亿个高保真量子门，**目前没有任何量子硬件能跑完整的 Shor 算法分解 RSA-2048**——估计需要几千到几百万个**逻辑**量子比特（容错的），而今天的硬件还在一百多个**物理**量子比特的水平。所以你的银行账户暂时是安全的，但 NIST 已经把 2035 年设为后量子密码迁移的最后期限（见第 11 节）。

### 2.5 Grover 算法：搜索加速

Grover 解决的是：给定一个「黑盒」函数 f，在 N 个候选里找出满足 f(x)=1 的那个 x。经典算法平均要试 N/2 次；Grover 算法只需约 (π/4)√N 次。

它的物理图景极其优雅：把初始态做成所有 N 个候选的等权叠加（用 Hadamard 门），然后反复做两件事——

1. **Oracle 翻转**：把满足 f(x)=1 的那个候选的振幅翻转（乘 −1）。
2. **关于均值反转（diffusion）**：把每个振幅关于所有振幅的均值做反射。

每做一轮「Oracle + 反射」，正确答案的振幅就被放大一点、错误答案的振幅就被压低一点（这是干涉）。约 √N 轮后，正确答案的概率接近 1。这个「振幅放大」（amplitude amplification）框架非常普适，是大多数 QML「搜索型加速」的母算法。注意 Grover 是**平方根加速**，不是指数加速，所以它不会改写 NP 难问题的根本难度——只是把暴力破解的时间从天文数字缩短到「仍然天文但小一些的数字」。

---

## 3. 量子机器学习的四象限：CC / CQ / QC / QQ

Maria Schuld 在她的专著里把整个 QML 领域按「数据来源 × 模型类型」分成四个象限，这是理解 QML 最有用的思维框架：

| 象限 | 数据 | 模型 | 代表 | 是否有量子优势 |
|------|------|------|------|----------------|
| **CC** | 经典 | 经典 | 量子启发算法（如 tensor network 训练） | 无（本质是经典） |
| **CQ** | 经典 | 量子 | VQA、QNN、量子核 | **存疑**（核心争论区） |
| **QC** | 量子 | 经典 | 用经典 ML 分析量子实验数据 | 有（数据天然量子） |
| **QQ** | 量子 | 量子 | 模拟分子、材料、量子化学 | **最强优势区** |

**CC（经典-经典）**：严格说不算「真量子」，但用张量网络、玻尔兹曼机等量子物理工具训练经典模型，能解决某些大模型问题。这部分已经在主流深度学习里被吸收（如 TensorRing 分解）。

**CQ（经典-量子）**：这是**今天 90% 的 QML 研究都在做的事**，也是 hype 最集中的地方。把经典数据（图像、文本、表格）编码到量子态里，用参数化量子电路当模型，用经典优化器调参。核心问题是：经典数据进入量子态需要「数据加载」（data loading / encoding），这一步本身可能是指数昂贵的，会吃掉后面所有的加速。**这是 QML 整个领域最大的隐形炸弹。**

**QC（量子-经典）**：用经典 ML 处理量子实验或量子模拟产生的数据。例如用神经网络拟合变分波函数、用 ML 加速量子化学计算。这部分有真实价值，因为数据天然就是量子的，不需要加载。

**QQ（量子-量子）**：用量子计算机处理量子数据。这才是 Feynman 1982 年直觉里真正的圣杯——**用量子硬件原生地模拟量子系统**。分子基态能量、化学反应路径、超导材料、高温超导机制这些问题的数据天然是量子的，量子计算机在这里有最扎实的指数加速潜力。**Google、IBM、微软、Quantinuum 现在的「实用化路线图」几乎全部押在 QQ 上**，而不是押在 CQ（即大众意义上的「量子 ML」）上。这是一个经常被外行忽略的关键事实。

---

## 4. 核心算法：从 HHL 到量子神经网络

### 4.1 HHL 算法：被夸大的指数加速

HHL 解的是 Ax=b，输出不是 x 本身（量子态不能直接读出），而是 x 的某个期望 ⟨x|M|x⟩。算法分三步：相位估计把 A 的特征值提取到寄存器；旋转把 1/λ 写进振幅（这就是求逆）；逆相位估计还原。

理论复杂度是 O(poly(log N), κ)（κ 是 A 的条件数），对比经典共轭梯度的 O(N√κ)，看起来是指数加速。**但有三个隐藏前提被几乎所有科普文章忽略：**

1. **A 必须是稀疏或结构化的**，且量子模拟 A 的代价不能太大。
2. **κ（条件数）必须小**。κ 出现在多项式次数里，如果数据病态（κ ~ N），加速就蒸发了。
3. **数据加载与读出代价**。把经典向量 b 写进量子态需要 QRAM（量子随机访问存储器），这一步可能本身指数昂贵；读出 ⟨x|M|x⟩ 也是一次量子测量的采样，要重复很多次。

结果是：对绝大多数真实 ML 数据集，HHL 不仅没有加速，反而比经典算法慢。这是 2010 年代「量子 ML 会取代经典 ML」论调破灭的核心原因。

### 4.2 量子 PCA

Lloyd、Mohseni、Rebentrost 在 2013 年提出量子版主成分分析：

> 论文：Seth Lloyd, Masoud Mohseni, Patrick Rebentrost, *Quantum Algorithms for Supervised and Unsupervised Machine Learning* [arXiv:1307.0411, 2013](https://arxiv.org/abs/1307.0411)

量子 PCA 用密度矩阵 ρ = Σλᵢ|eᵢ⟩⟨eᵢ| 表示协方差矩阵，通过「密度矩阵幂」的量子模拟提取主成分。理论复杂度 O(log N)，但同样依赖 QRAM 数据加载和密度矩阵制备，所以「指数加速」在真实数据上同样难兑现。

### 4.3 变分量子算法（VQA）族

VQE 和 QAOA 都属于**变分量子算法**（Variational Quantum Algorithms）大家族，它们是 NISQ 时代的主流范式。共同结构是：

$$\mathcal{L}(\boldsymbol{\theta}) = \langle \psi(\boldsymbol{\theta}) | \hat{H} | \psi(\boldsymbol{\theta}) \rangle, \quad |\psi(\boldsymbol{\theta})\rangle = U(\boldsymbol{\theta})|0\rangle$$

U(θ) 是参数化量子电路（parameterized quantum circuit, PQC），θ 是可调参数，Ĥ 是问题相关的哈密顿量。**量子计算机负责算期望值 L(θ)，经典优化器负责调 θ**。这种「量子-经典交替」的好处是电路深度浅、对噪声相对鲁棒，所以能在今天的 NISQ 设备上跑。

- **VQE**：Ĥ 是分子的电子哈密顿量，目标是分子基态能量。已在 HeH⁺、LiH、BeH₂ 等小分子上验证，但目前精度还不如经典 CCSD(T)，且量子噪声限制了可处理分子的大小。
- **QAOA**：Ĥ 是把优化问题（如 MaxCut）编码成的「问题哈密顿量」，再加一个「混合哈密顿量」。层数 p 越大、解越好；p=1 时在 3-regular 图上 MaxCut 至少能达到最优解的 0.6924 倍。但实践中，Goemans-Williamson 经典近似算法通常胜过浅层 QAOA。

变分算法的根本优势是**「硬件友好」**，根本劣势是**「能否取得真正的量子优势仍然没有定论」**——目前没有严格证明 VQE 或 QAOA 在任何实际问题上能击败最好的经典算法。这是 NISQ 时代最大的开放问题。

### 4.4 量子神经网络（QNN）

Farhi 和 Neven 在 2018 年提出了「近期处理器上的量子神经网络」：

> 论文：Edward Farhi, Hartmut Neven, *Classification with Quantum Neural Networks on Near Term Processors* [arXiv:1802.06002, 2018](https://arxiv.org/abs/1802.06002)

QNN 的标准形式是：把经典数据 x 编码进量子态 |x⟩，过一个参数化电路 U(θ)，在某个 qubit 上测 Pauli 算符得到预测。训练用「参数移位法则」（parameter shift rule）计算精确梯度：

$$\frac{\partial \mathcal{L}}{\partial \theta_i} = \frac{1}{2}\left[\mathcal{L}(\theta_i + \pi/2) - \mathcal{L}(\theta_i - \pi/2)\right]$$

这避免了经典神经网络里的反向传播和数值差分，是一个干净的设计。但 QNN 面临一个致命困难——**贫瘠高原**（见第 8 节），导致它在超过几个 qubit 时几乎无法训练。

### 4.5 量子核方法：最有理论根基的 CQ 算法

Havlíček 等人在 2019 年发表的工作，可能是 CQ 象限里理论最扎实的一个：

> 论文：Vojtěch Havlíček et al., *Supervised Learning with Quantum Enhanced Feature Spaces* [Nature 567:209-212, 2019 / arXiv:1804.11326](https://arxiv.org/abs/1804.11326)

核心思想：把经典数据 x 通过量子特征映射 φ(x) 映射到指数大的量子希尔伯特空间，然后定义量子核：

$$K(x, x') = |\langle \phi(x) | \phi(x') \rangle|^2$$

用经典 SVM 配合这个量子核做分类。**核方法的好处是不需要训练量子电路参数，只需估计核矩阵**，避开了 QNN 的训练难题。Havlíček 等人在 IBM 的超导处理器上实验演示了这个方法。

**这个方向在 2021 年迎来了最重要的理论突破**——Liu、Arunachalam、Temme 给出了**第一个严格的、鲁棒的、仅需要经典数据访问的量子分类优势证明**：

> 论文：Yunchao Liu, Srinivasan Arunachalam, Kristan Temme, *A Rigorous and Robust Quantum Speed-up in Supervised Machine Learning* [Nature Physics, 2021 / arXiv:2010.02174](https://arxiv.org/abs/2010.02174)

他们构造了一族数据集，证明在「离散对数问题困难」的标准密码学假设下，任何经典分类器都不会比随机猜好太多，但量子核分类器能达到高精度。**这是 QML 历史上第一篇把「量子优势」从启发式口号变成可证明定理的工作**——但要强调，这是存在性构造，构造的数据集是人为设计的离散对数问题，并不是说你的图像分类任务也会受益。

---

## 5. 代表公司：硬件竞赛的全景图

量子硬件现在是「七国八制」：超导、离子阱、光子、拓扑、中性原子、量子退火、硅自旋等多种物理体系在赛跑。下面列出主要玩家及其技术路线（所有规格均来自官方发布或一手论文）。

### 5.1 Google Quantum AI：Willow 与 Sycamore

Google Quantum AI 由 Hartmut Neven 在 2012 年创立。2019 年 10 月，53-qubit 的 **Sycamore** 处理器在随机电路采样（RCS）任务上宣称「量子霸权」——完成 200 秒的采样任务，当时估计超级计算机需要 1 万年（后被 IBM 等改进经典算法缩减到几天，所以「霸权」反复被挑战）。

**2024 年 12 月 9 日，Google 发布了 Willow 芯片，这是过去十年量子纠错最重大的进展**：

> 论文：Google Quantum AI, *Quantum Error Correction Below the Surface Code Threshold* [Nature, 2024 / DOI 10.1038/s41586-024-08449-y](https://www.nature.com/articles/s41586-024-08449-y)
> 官方：[Meet Willow, our state-of-the-art quantum chip (Google Blog, 2024-12-09)](https://blog.google/technology/research/google-willow-quantum-chip/)

Willow 的三项关键指标：
- **105 个物理 qubit**，T1（量子比特相干时间）接近 100 µs，比上一代提升 5 倍。
- **首次实现「低于阈值」（below threshold）的量子纠错**：把 qubit 阵列从 3×3 扩到 5×5 再到 7×7，每扩大一次错误率就减半——**「qubit 越多、错误越少」**，这是量子纠错界追逐了近 30 年的目标，由 Peter Shor 在 1995 年首次提出纠错码概念以来一直未被实验实现。
- **RCS 基准**：Willow 5 分钟完成的采样任务，估算需要 Frontier 超级计算机 10²⁵（10 septillion，10⁻²⁵ 倍宇宙年龄）年。Neven 在博客里直接把这个数字关联到 Deutsch 的多世界解释（见第 12 节）。

Willow 的意义不在于它已经能跑实用算法（事实上 RCS 没有已知商业应用），而在于它**第一次用实验证明「可扩展的逻辑 qubit」在物理上是可行的**——这是通往百万 qubit 容错量子计算机的必要前提。

### 5.2 IBM Quantum：Heron R2 与量子路线图

IBM 是最早把量子计算商业化的公司，2016 年第一个把量子计算机放上云。2021 年发布 127-qubit Eagle（首个破百的处理器）。

2023 年发布 **Heron** 处理器（133 qubit，引入可调耦合器，大幅提高双 qubit 门保真度），2024 年 12 月发布 **Heron R2**（156 qubit，错误率比 Heron 第一代降低 5 倍）。IBM 的策略不是追求单芯片最大 qubit 数，而是**模块化**：通过量子通信链接多个处理器，构建「quantum-centric supercomputer」。其长期路线图包括 Kookaburra（1386 qubit 多芯片）、Flamingo（量子通信链接）、Starling（容错原型）等。IBM 的软件栈 Qiskit 也是事实上的行业标准。

### 5.3 Microsoft：Majorana 1 与拓扑路线

微软走了 17 年最孤独的路：**拓扑量子比特**。

> 论文：Chetan Nayak et al. (Microsoft), *Interferometric Single-Shot Parity Measurement in InAs-Al Hybrid Devices* [Nature, 2025 / DOI 10.1038/s41586-024-08445-2](https://www.nature.com/articles/s41586-024-08445-2)
> 官方：[Microsoft's Majorana 1 chip carves new path for quantum computing (2025-02-19)](https://news.microsoft.com/source/features/innovation/microsofts-majorana-1-chip-carves-new-path-for-quantum-computing/)

2025 年 2 月 19 日发布的 **Majorana 1** 是世界首个基于拓扑核（Topological Core）架构的量子芯片。其核心是用砷化铟-铝（InAs-Al）混合器件构建「拓扑超导体」（topoconductor），在其中产生并测量 **Majorana 粒子**——这种粒子是其自身反粒子的奇特准粒子，由 Ettore Majorana 在 1937 年预言。Majorana 把量子信息「拓扑保护」起来，理论上有更高的本征抗噪能力。每个 H 形纳米线含 4 个可控 Majorana，构成 1 个 qubit。当前芯片含 8 个拓扑 qubit，但设计目标是单芯片扩展到 100 万 qubit。

**需要清醒**：Majorana 拓扑 qubit 是高风险高回报路线，2021 年微软第一篇声称观测到 Majorana 的论文曾因数据问题被 Nature 撤稿，所以这次发布在学术圈里评价谨慎——拓扑 qubit 路线是否真的成功，仍需要更多独立验证。但 2025 年的 Nature 论文经过了同行评议，且 DARPA 的 US2QC 项目把微软列为最终阶段两个公司之一，说明这条路至少在工程上已经取得实质性进展。微软的策略是「硬件级纠错」——如果拓扑 qubit 真的成功，需要的纠错开销会远小于超导/离子阱路线。

### 5.4 Quantinuum：离子阱的旗手

Quantinuum 是 2021 年 Honeywell 量子部门与剑桥量子计算合并而成的公司，走**离子阱**（trapped ion）路线：用电磁场把镱（Yb⁺）离子束缚在真空中，用激光操作。离子阱的优势是 qubit 之间**全连接**（任意两个 qubit 都能直接纠缠）、单/双 qubit 门保真度行业最高（>99.9%）、相干时间极长（秒级）。劣势是门操作慢（微秒到毫秒级，比超导慢 100–1000 倍）、扩展到大规模困难。其 **H2** 系统（2023 年发布，56 qubit）创下了多次量子体积（Quantum Volume）世界纪录。2024 年，Quantinuum 联合微软演示了 12 个逻辑 qubit 的化学模拟，是目前最接近「可靠量子计算」的演示之一。

### 5.5 IonQ、Rigetti、PsiQuantum

- **IonQ**：另一家离子阱公司（锂/镱），是第一家上市的纯量子公司（NYSE: IONQ，2021 年 SPAC 借壳）。主打「门数量」指标，与 AWS Braket、Azure Quantum 深度集成。
- **Rigetti**：超导路线，纯自研芯片，也是上市公司。规模比 IBM/Google 小，但走全栈路线（芯片+软件+云）。
- **PsiQuantum**：光子路线（用光子做 qubit），野心极大——目标是直接造百万 qubit 容错量子计算机，跳过 NISQ 阶段。与 GlobalFoundries 合作制造光子芯片，预计 2020 年代后期才有原型。

### 5.6 中国：潘建伟团队与「九章」「祖冲之号」

中国在量子计算两条路线上都处于第一梯队：

- **中科大潘建伟团队**主导：
  - **「九章」**光量子计算原型机（2020，76 个光子模式）：在「玻色采样」任务上实现量子优势（与 Sycamore 不同的赛道）。2023 年「九章三号」把光子数推到 255 个。
  - **「祖冲之号」**超导处理器（2021，62/66 qubit）：在随机线路采样上比 Sycamore 路线更高的采样率。
  - **量子通信**：潘建伟团队还主导了「墨子号」量子科学实验卫星（2016）、京沪量子通信干线，在量子密钥分发（QKD）上是世界领先的应用。
- **本源量子（OriginQ）**：中国第一家量子计算初创公司，主打超导路线 + 国产量子操作系统本源司南、Q-Network 软件栈。已交付 24、72 qubit 超导芯片。
- **百度、阿里、腾讯**均有量子实验室（部分近年有所收缩）。整体看，中国在「量子通信 + 光量子计算」上世界领先，在「通用超导容错量子计算」上略落后于 IBM/Google，但差距在快速缩小。

---

## 6. 2024–2026 关键里程碑

把过去两年的进展串起来，可以看出量子计算正处于「纠错」这一关键拐点：

| 时间 | 事件 | 意义 |
|------|------|------|
| 2024-09 | Quantinuum + Microsoft 演示 12 个逻辑 qubit 的端到端化学模拟 | 当时最大逻辑 qubit 数 |
| 2024-11 | Microsoft + Atom Computing 演示 24 个纠缠逻辑 qubit | 「第一台可靠量子计算机」商业预告 |
| 2024-12 | **Google Willow**（105 qubit）实现 below-threshold QEC | 30 年纠错难题首次实验突破 |
| 2024-12 | **IBM Heron R2**（156 qubit），错误率降低 5 倍 | 超导门保真度持续提升 |
| 2025-02 | **Microsoft Majorana 1**（8 拓扑 qubit） | 首个拓扑核量子芯片 |
| 2025 | Quantinuum H2 持续刷新量子体积纪录 | 离子阱路线稳定推进 |
| 2026 | 各家继续向「百万物理 qubit + 数千逻辑 qubit」推进 | 容错量子计算的工程前夜 |

**把这些事件连起来读，趋势很清晰**：业界已经从「追求 qubit 数量」转向「追求可纠错的逻辑 qubit」。Willow 的「below threshold」之所以重要，是因为它证明「加更多物理 qubit 真的能换来更低的错误率」——这是把物理 qubit 堆叠成可靠逻辑 qubit 的前提，也是 Feynman 1982 年直觉变成工程的最后一公里。

---

## 7. 量子 AI 的现实评估：理论、工程、案例

### 7.1 理论基础：BQP 与可能的计算优势

量子计算的理论优势用复杂度类 **BQP**（Bounded-error Quantum Polynomial time）刻画——量子计算机在多项式时间内可解、错误概率有界的判定问题类。已知的关系是 P ⊆ BPP ⊆ BQP ⊆ PSPACE，且 BQP 包含一些**经典认为困难**的问题（如 Shor 的因式分解、量子模拟）。但**至今没有任何证明显示 BQP ⊋ BPP**——也就是说，「量子比经典快」这件事在严格数学意义上仍是猜想，只是大量证据（Shor、Grover、量子模拟、Willow 实验）让物理学家普遍相信它成立。

注意一个常被混淆的点：**BQP 不包含 NP**（普遍相信 NP ⊄ BQP），所以量子计算机**不能**高效解决所有 NP 难问题。它能解决一些特殊结构的问题（因式分解、量子模拟、特定搜索），但旅行商问题、SAT 求解等一般 NP 难问题，量子也搞不定。Grover 提供的只是平方根加速，不会把 NP 变成 QP。

### 7.2 工程现状：NISQ 的天花板

目前的工程现实是：

1. **qubit 数量在百级**（IBM Heron R2 156、Google Willow 105），但都是**物理 qubit**，噪声大、相干时间短。
2. **逻辑 qubit 还在个位数到十位数**。1 个可靠的逻辑 qubit 通常需要 1000+ 个物理 qubit 来纠错（surface code 开销）。
3. **电路深度有限**。NISQ 设备上能跑的电路深度通常只有几十到几百层，复杂算法跑不通。
4. **数据输入（QRAM）不存在**。把 GB 级经典数据高效加载进量子态的硬件，目前只是理论设想。

**结论**：今天的量子计算机是「非常有价值的物理实验装置」，但**离任何商业有用的 ML 任务都还很远**。Hartmut Neven 自己在 Willow 发布时也承认，下一步是「在今天的芯片上跑出第一个既有商业价值、又超越经典计算的算法」，而这件事还没有人做到。

### 7.3 量子优势的真实案例：少而有限

到目前为止，**严格意义上的「量子优势」案例非常有限**，且都集中在物理本源任务上：

- **随机电路采样（RCS）**：Google Sycamore/Willow、中科大「祖冲之号」。这是被设计出来「对经典最难」的基准，目前**没有已知商业应用**。
- **玻色采样**：中科大「九章」。同样是对经典难的采样任务，**没有已知商业应用**。
- **量子化学小分子模拟**：VQE 在 HeH⁺、LiH 等小分子上跑通，但精度和规模都**不如经典 CCSD(T)**。
- **离散对数型 ML 任务**：Liu-Arunachalam-Temme 2021 的严格量子优势（第 4.5 节），但是**人为构造的数据集**。

**一个让人不舒服的事实是：截至 2026 年，没有任何量子计算机在任何实际商业任务上证明过超越最好经典算法的优势。** 所有「量子优势」宣称要么是 RCS/玻色采样这种无应用基准，要么是后来被经典算法追平（如 2019 Sycamore 的 1 万年被 IBM 缩到几天）。

### 7.4 何时实用：10–20 年的估计

主流专家（Preskill、IBM、Google、Quantinuum）的估计大致是：

- **5–10 年内**：可能看到「量子-经典混合」在某些化学/材料模拟上的窄而真实的应用，但都是 QQ 象限，不是大众意义上的 ML。
- **10–15 年**：第一批容错量子计算机（数千逻辑 qubit）问世，开始有商业价值的药物发现、催化剂设计、材料科学应用。
- **15–20 年+**：可能威胁 RSA-2048，迫使全球完成 PQC 迁移；量子 ML 是否真的有用，到那时才能下结论。

**对所有「3 年内颠覆 AI」的说法，请直接打上 hype 标签。** 量子计算的发展节奏更像「摩尔定律的 10 倍慢版本」，而不是 LLM 那种 2 年一个数量级的快变量。

---

## 8. 量子神经网络的挑战：贫瘠高原

如果说有一条理由让 CQ 象限的 QNN 至今没有实用，那就是 **barren plateaus**（贫瘠高原）现象。2018 年 McClean 等人的发现：

> 论文：Jarrod R. McClean, Sergio Boixo, Vadim N. Smelyanskiy, Ryan Babbush, Hartmut Neven, *Barren Plateaus in Quantum Neural Network Training Landscapes* [Nature Communications 9:4812, 2018 / arXiv:1803.11173](https://arxiv.org/abs/1803.11173)

**核心结论**：对于一个「足够随机」的参数化量子电路，损失函数对参数的梯度方差随 qubit 数 n **指数衰减**：

$$\mathrm{Var}\left(\frac{\partial \mathcal{L}}{\partial \theta_i}\right) \sim \mathcal{O}\left(\frac{1}{2^n}\right)$$

也就是说，qubit 数一多，梯度几乎处处接近 0——**训练曲面变成一片平坦的高原**，经典优化器无论从哪开始都看不到方向。这就是量子版的「梯度消失」，比经典深度网络的梯度消失更致命，因为它是指数级的。

物理直觉是：随机量子电路的行为趋近于 Haar 随机酉变换（2-design），而 Haar 随机变换的期望值对任何局部扰动都不敏感——所以梯度被平均掉了。这和「真正有结构的电路才有可学习的梯度」是一致的。

后续研究（Holmes、Cerezo、Pesah 等）发现：贫瘠高原不仅来自随机初始化，**糟糕的损失函数（全局可观）、噪声、过深的电路**都会触发它。这意味着 QNN 要训练，必须精心设计电路结构（如层次化 ansatz）、用局部可观、控制噪声——这又大幅限制了 QNN 的表达能力。

**这是 QML 最深刻的悖论**：电路要表达能力强（接近随机酉），就训练不动（贫瘠高原）；电路要训练得动（高度结构化），表达能力可能就不足以拟合复杂数据。**经典深度网络用残差连接、归一化、注意力机制解决了类似的梯度问题，QML 还在寻找对应的工具。** 在这些工具出现之前，超过 20–30 qubit 的 QNN 基本无法有效训练。

---

## 9. 量子 ML vs 经典 ML：谁会赢？

把上面的分析落到「什么任务可能量子有优势、什么永远没有」上：

**量子可能占优的任务**（共同特征是「数据天然量子」或「问题结构有量子友好的对称性」）：
- **量子化学模拟**（分子基态、反应路径、激发态）：数据天然量子，HHL/VQE/QPE 类算法有指数加速潜力。这是**所有 QML 应用里最有希望的方向**。
- **组合优化**（特定结构的）：QAOA 在某些特定问题上有机会，但目前还未击败经典启发式。
- **线性代数问题**（稀疏、低秩、结构良好）：HHL 类算法，但 QRAM 假设很强。
- **量子核分类**（Liu-Arunachalam-Temme 型）：在密码学难问题上严格占优，但需要构造对应数据。

**量子基本不会有优势的任务**（共同特征是「数据是经典符号序列、且经典 ML 已经极强」）：
- **文本生成、对话、翻译**（LLM 任务）。语言的本质是离散符号，量子叠加对它没有天然亲和力。把 token 序列编码进量子态本身代价就巨大。**没有任何严肃研究者认为量子计算会取代 Transformer。**
- **图像识别、语音识别**。经典 CNN/Transformer 已经极强，量子硬件的数据加载瓶颈使得「编码一张图片」本身就比「经典识别这张图片」慢得多。
- **大规模表格数据的梯度提升树、线性模型**。
- **强化学习（环境是经典模拟的）**。

**一个有用的判断准则**：**如果数据是经典的、且经典 ML 在该任务上已经接近最优，量子几乎不会有优势**；**如果数据天然是量子的（分子、材料、量子场），量子计算就有真实的潜力**。这条准则可以让你过滤掉 90% 的 QML hype。

Google 自己也持类似观点：Neven 在 Willow 博客里提到的应用方向是「药物发现、电池设计、聚变能源」——全部是 QQ 象限，没有一个是「用量子训练 LLM」。

---

## 10. 量子纠错码（QEC）：通往容错的最后一公里

量子计算的噪声问题是根本性的——qubit 极其脆弱，一次测量、一次门操作甚至周围环境的轻微扰动都会破坏量子态。如果不纠错，量子计算机连最简单的算法都跑不完。这就是 QEC 的核心地位。

### 10.1 Surface Code（表面码）

最主流的 QEC 方案是 **surface code**（表面码），由 Kitaev 在 1997 年提出。它把一个**逻辑 qubit** 编码在一个 2D 物理量子比特阵列上，通过测量「稳定子」（stabilizer）来检测错误但不破坏编码信息。表面码的优点是：

- **只需要最近邻耦合**（超导硬件天然适用）。
- **阈值较高**：理论上当物理错误率低于约 1% 时，编码后逻辑错误率可以任意降低。

Peter Shor 在 1995 年提出第一个量子纠错码（9 个物理 qubit 编 1 个逻辑 qubit，能纠正任意单 qubit 错误），这是整个 QEC 领域的起点。

### 10.2 阈值定理（Threshold Theorem）

**阈值定理**是量子容错计算的理论基石：**只要物理门的错误率低于某个阈值（surface code 约 1%），就可以用足够的冗余把逻辑错误率压到任意低**。这个定理类比于经典通信里的香农定理——它说「理论上噪声不是不可逾越的障碍」。

但代价是巨大的开销：用 surface code 编码 1 个高保真逻辑 qubit，**通常需要 1000+ 个物理 qubit**（具体取决于物理错误率和目标逻辑错误率）。所以一台能跑 Shor 算法破解 RSA-2048 的容错量子计算机，**需要数百万到数千万个物理 qubit**——而今天我们只有 100 多个。这就是为什么 Feynman 1982 年的构想要到 2024 年（Willow 的 below-threshold）才算走完了「理论上证明可行」这一步，距离「工程上造出来」还有漫长的路。

### 10.3 Willow 的历史意义

Willow 的 below-threshold 是 surface code 路线第一次实验证明：**随着物理 qubit 阵列扩大，逻辑错误率真的下降了**。3×3 → 5×5 → 7×7 每次扩大错误率减半，符合 surface code 的理论预测。这意味着 surface code 不仅是数学构造，是物理上可行的——**量子容错计算从「理论」正式进入「工程实现」阶段**。这是过去 30 年量子计算最重要的实验进展，没有之一。

---

## 11. 后量子密码学：Shor 算法的倒计时

Shor 算法对 RSA/ECC 的威胁催生了**后量子密码学**（Post-Quantum Cryptography, PQC）。NIST 从 2016 年开始举办 PQC 标准化竞赛，2024 年 8 月正式发布第一批三个标准：

- **FIPS 203 — ML-KEM**（Module-Lattice-Based Key Encapsulation，前称 **CRYSTALS-Kyber**）：用于密钥封装，替代 RSA/ECDH 密钥交换。
- **FIPS 204 — ML-DSA**（Module-Lattice-Based Digital Signature，前称 **CRYSTALS-Dilithium**）：数字签名，替代 RSA/ECDSA 签名。
- **FIPS 205 — SLH-DSA**（Stateless Hash-Based Digital Signature，前称 **SPHINCS+**）：基于哈希的数字签名，作为 lattice 路线的备份（哪怕 lattice 被攻破也安全）。

> 来源：[NIST Post-Quantum Cryptography 项目页（2024 年 8 月发布标准）](https://csrc.nist.gov/projects/post-quantum-cryptography)

**关键信息**：
- NIST 计划在 **2035 年**前完成向后量子密码的全面迁移（高风险系统更早）。
- 这些标准基于**格问题**（lattice problems，如 LWE、Module-LWE），被认为对量子计算机也困难。
- 中国在 2024 年发布了国家标准 **GM/T 0062–2024**（基于 LWE 的密钥封装）等，路线接近 NIST 但有自主实现；腾讯、阿里、华为等已在 PQC 库和产品上跟进。
- Google Chrome、Apple iMessage、Signal 已部署混合 PQC（PQC + 经典算法），以对冲 PQC 算法未充分验证的风险。

**「先收集，后解密」威胁**（harvest-now-decrypt-later）：即便量子计算机还需 15 年才能破解 RSA，攻击者今天就在大量截获并存储加密流量，等量子计算机出来再解密。所以 PQC 迁移**不能等量子计算机造好再开始**，今天就要启动——这是为什么 NIST 把 2035 设为硬截止。

---

## 12. 哲学问题：量子力学深处的迷雾

量子计算不只是工程，它触及了物理学最深的哲学争论。

### 12.1 哥本哈根解释 vs 多世界解释

量子力学的「测量问题」至今没有共识。**哥本哈根解释**（Bohr、Heisenberg）：测量时波函数「塌缩」到一个本征态，塌缩是基本且不可逆的过程。**多世界解释**（Everett 1957，DeWitt 推广）：没有塌缩，宇宙在每次量子测量时「分裂」成多个平行分支，每个可能的结果都在某个分支里实现了，只是观察者只能进入其中一个分支。

David Deutsch 是多世界解释最著名的当代捍卫者，他在 1997 年的著作 *The Fabric of Reality* 里把多世界解释作为「量子计算能工作的根本原因」——他认为 Shor 算法的指数加速之所以可能，是因为计算「真的」在大量平行宇宙里同时进行，然后干涉把结果带回来。Hartmut Neven 在 Willow 发布时直接呼应了 Deutsch：「10²⁵ 年这个数字支持了量子计算在许多平行宇宙中进行的观念，符合我们生活在一个 multiverse 里的观点，这一预测最早由 David Deutsch 提出。」

**这是一个无法用实验判定的问题**（至少目前如此），但它是量子计算哲学的底色。值得提醒：**多数物理学家持工具主义态度**（「shut up and calculate」），认为解释之争不影响计算，但 Deutsch 等人坚持认为解释决定了我们对算法的理解。

### 12.2 量子意识假说：Penrose-Hameroff Orch OR

更激进、也更受争议的是 **Penrose-Hameroff 的 Orch OR（Orchestrated Objective Reduction，编排客观还原）假说**。Roger Penrose（2020 年诺贝尔物理学奖得主，因黑洞奇点工作）在 1989 年的 *The Emperor's New Mind* 中论证：人类意识、特别是数学直觉中的「不可计算性」，不可能来自经典计算（图灵机）；他援引 Gödel 不完备定理，主张意识必须基于某种**非计算性的物理过程**，并提出这来自量子引力引起的波函数客观塌缩（他认为塌缩不是哥本哈根式的，而是引力决定的）。

Stuart Hameroff（麻醉学家）补充了生物载体：大脑神经元里的**微管**（microtubules）可能是量子相干的场所，意识是微管中量子态的 Orch OR 事件。

**主流神经科学和物理学界的立场**：Orch OR **几乎没有被实验支持，且面临严重的退相干难题**——大脑是温暖潮湿的环境，任何量子相干都会在飞秒级时间内被环境破坏，不可能维持到影响神经元计算。Max Tegmark 2000 年估算微管退相干时间在 10⁻¹³ 秒量级，远短于神经反应时间。所以**绝大多数神经生物学家和物理学家不把 Orch OR 当作严肃的意识理论**，它更像是一个有趣的哲学猜想。

但要注意：Penrose 不是民科，他的其他物理学贡献是第一流的；Orch OR 的存在说明即使在顶级物理学家之间，「意识是否量子」也是开放问题。量子机器学习工程师们应该知道：**目前没有任何可信证据表明「量子计算机会有意识」或「意识需要量子」**。这类说法应归入科幻而不是工程。

### 12.3 给工程师的实用结论

哲学争论不影响你今天能不能跑 VQE，但它影响你怎么讲故事。**对外宣传量子 ML 时，请把「多世界」「量子意识」「大脑是量子计算机」这些说法从工程叙事里彻底剥离**——它们属于科普和哲学讨论，不属于严肃的算法评估。

---

## 13. 给用户的建议：量子 ML 是否值得投入？

回到最现实的问题：作为一个 AI 应用工程师、一个零基础起步的学习者、一个想分配有限时间的人，**量子机器学习是否值得投入？** 给出明确而残酷的判断：

### 13.1 三种人的不同答案

**如果你是 ML 工程师 / AI 应用从业者（绝大多数人）**：**不要把主要精力放在量子 ML 上**。理由：
- 你的工作 99.9% 是经典 ML/LLM，量子 ML 在 5–10 年内不会进入你的生产技术栈。
- 量子 ML 的入门门槛极高（需要线性代数、量子力学、量子信息、复分析），而回报周期极长。
- 经典 ML（尤其 LLM、Agent、RAG）在 2020 年代的机会密度远高于量子 ML。
- 如果非要学，把「量子计算原理」当作**通识教育**投入 20–40 小时，理解 Bloch 球、叠加/纠缠/干涉、Shor/Grover 思想就够了，不要去学 Qiskit 写 VQE。

**如果你是有物理/化学背景、想做 AI4Science 的研究者**：**值得投入**，但要押在 QQ 象限：
- 你的天然赛道是**量子化学模拟、材料科学**，不是「量子神经网络」。
- 学习 VQE、QPE、量子模拟算法，关注 IBM Qiskit Nature、Google Cirq、PennyLane 这些工具。
- 跟进 Willow、Heron、Majorana 的进展，关注「逻辑 qubit 数」这个核心指标。
- 准备 5–10 年的耐心——这个领域不会快速变现。

**如果你是密码学 / 安全工程师**：**必须立刻投入 PQC**：
- 量子计算对你是真实的倒计时威胁，2035 年 NIST 截止日期不是开玩笑。
- 学习 ML-KEM、ML-DSA、混合 PQC 部署，评估你系统的「先收集后解密」暴露面。
- 这不是「值得不值得」，而是「不做就是失职」。

### 13.2 一个 20 小时的最小可行学习路径

如果你只想花 20 小时建立判断力（不被 hype 误导、能听懂量子计算新闻），推荐：

1. **物理基础（6 小时）**：读 Nielsen & Chuang《Quantum Computation and Quantum Information》第 1–2 章，或听 Leonard Susskind 的 Theoretical Minimum 量子力学 10 讲。
2. **算法基础（6 小时）**：手动推 Shor 在 N=15 上的过程；手动跑 Grover 在 N=4 上；理解 HHL 的三步结构。
3. **QML 全景（4 小时）**：读 Biamonte 2017 的 Nature review（arXiv:1611.09347），建立 CC/CQ/QC/QQ 四象限直觉。
4. **动手（4 小时）**：跑 Qiskit 或 PennyLane 教程，把一个 2-qubit Bell 态准备 + 测量跑通；用 IBM Quantum 免费体验真实硬件上的噪声。
5. **批判性阅读（持续）**：每看到「量子 ML 颠覆 AI」的新闻，问三个问题——数据是经典还是量子？优势是严格证明还是启发式？硬件时间表是否现实？

### 13.3 最后的判断

**量子计算是人类科技树上一条真实、深刻、且正在取得突破的分支，但它不是 AI 的下一站。** 大语言模型、Agent、扩散模型这些经典 ML 浪潮在 2020 年代会持续主导 AI；量子计算的真正影响，会在 2030 年代先从化学、材料、密码学渗透进来，而「量子 ML 取代经典 ML」大概率永远不会发生——它们会像 GPU 和 CPU 一样并存，各管一摊。

如果你必须记住本专题的一句话，那就是：**量子计算擅长处理量子数据，经典计算擅长处理经典数据；让量子回去做分子，让经典继续做语言。**

---

## 📌 进一步阅读

**入门教材**
- Nielsen, M. A., & Chuang, I. L. *Quantum Computation and Quantum Information* (Cambridge University Press, 10th Anniversary Edition, 2010). 量子计算的圣经，第 1–4 章足够建立完整基础。
- Susskind, L., & Friedman, A. *Quantum Mechanics: The Theoretical Minimum* (Basic Books, 2014). 物理直觉优先的最小路径。
- Schuld, M., & Petruccione, F. *Machine Learning with Quantum Computers* (Springer, 2nd ed., 2021). QML 最系统的入门专著。

**综述论文（一手已核实）**
- Biamonte, J. et al. *Quantum Machine Learning* [Nature 549:195-202, 2017 / arXiv:1611.09347](https://arxiv.org/abs/1611.09347)
- Schuld, M., Sinayskiy, I., Petruccione, F. *An Introduction to Quantum Machine Learning* [Contemporary Physics 56:172-185, 2015 / arXiv:1409.3097](https://arxiv.org/abs/1409.3097)
- Preskill, J. *Quantum Computing in the NISQ Era and Beyond* [Quantum 2:79, 2018 / arXiv:1801.00862](https://arxiv.org/abs/1801.00862)

**奠基算法论文**
- Shor, P. *Polynomial-Time Algorithms for Prime Factorization and Discrete Logarithms* [arXiv:quant-ph/9508027](https://arxiv.org/abs/quant-ph/9508027)
- Grover, L. *A Fast Quantum Mechanical Algorithm for Database Search* [arXiv:quant-ph/9605043](https://arxiv.org/abs/quant-ph/9605043)
- Harrow, A., Hassidim, A., Lloyd, S. *Quantum Algorithm for Solving Linear Systems of Equations* [arXiv:0811.3171](https://arxiv.org/abs/0811.3171)
- Lloyd, S., Mohseni, M., Rebentrost, P. *Quantum Algorithms for Supervised and Unsupervised Machine Learning* [arXiv:1307.0411](https://arxiv.org/abs/1307.0411)
- Peruzzo, A. et al. *A Variational Eigenvalue Solver on a Quantum Processor* [arXiv:1304.3061](https://arxiv.org/abs/1304.3061)
- Farhi, E., Goldstone, J., Gutmann, S. *A Quantum Approximate Optimization Algorithm* [arXiv:1411.4028](https://arxiv.org/abs/1411.4028)

**QML 关键论文**
- Havlíček, V. et al. *Supervised Learning with Quantum Enhanced Feature Spaces* [Nature 567:209-212, 2019 / arXiv:1804.11326](https://arxiv.org/abs/1804.11326)
- Farhi, E., Neven, H. *Classification with Quantum Neural Networks on Near Term Processors* [arXiv:1802.06002](https://arxiv.org/abs/1802.06002)
- McClean, J. et al. *Barren Plateaus in Quantum Neural Network Training Landscapes* [Nature Communications 9:4812, 2018 / arXiv:1803.11173](https://arxiv.org/abs/1803.11173)
- Liu, Y., Arunachalam, S., Temme, K. *A Rigorous and Robust Quantum Speed-up in Supervised Machine Learning* [Nature Physics, 2021 / arXiv:2010.02174](https://arxiv.org/abs/2010.02174)

**硬件里程碑**
- Google Quantum AI. *Quantum Error Correction Below the Surface Code Threshold* [Nature, 2024 / DOI 10.1038/s41586-024-08449-y](https://www.nature.com/articles/s41586-024-08449-y) — Willow 芯片
- Nayak, C. et al. (Microsoft). *Interferometric Single-Shot Parity Measurement in InAs-Al Hybrid Devices* [Nature, 2025 / DOI 10.1038/s41586-024-08445-2](https://www.nature.com/articles/s41586-024-08445-2) — Majorana 1 芯片

**密码学**
- [NIST Post-Quantum Cryptography（FIPS 203/204/205，2024 年 8 月）](https://csrc.nist.gov/projects/post-quantum-cryptography)

**哲学与科普**
- Deutsch, D. *The Fabric of Reality* (Penguin, 1997). 多世界解释与量子计算哲学的代表作。
- Penrose, R. *The Emperor's New Mind* (Oxford University Press, 1989). Orch OR 假说的起点（注意：意识理论部分争议极大）。

---

## ✍️ 思考题（5 道）

**题 1（数据编码悖论）**：HHL 算法在数学上对稀疏矩阵 Ax=b 有指数加速，但为什么在真实 ML 数据集上几乎不可能兑现？请列出至少三个隐藏前提，并解释为什么每一个都可能在真实数据上失效。这对「量子 ML 能取代经典 ML」的论调意味着什么？

**题 2（贫瘠高原的两难）**：McClean 2018 证明随机量子电路的梯度方差随 qubit 数指数衰减。请用「2-design」的语言解释为什么会发生这件事，并讨论：如果电路要可训练（梯度不为 0），它必须高度结构化；但结构化电路的表达能力又可能不足以拟合复杂函数。QML 该如何破解这个两难？经典深度网络是用什么机制破解了类似的梯度消失问题的？

**题 3（Willow 的历史定位）**：为什么 Google Willow 实现的「below-threshold」被称作「量子纠错界追逐了 30 年的目标」？请解释 surface code 的阈值定理，并估算：要把 1 个物理错误率 0.1% 的 qubit 编码成一个逻辑错误率 10⁻¹⁵ 的逻辑 qubit，大约需要多少物理 qubit？为什么这个开销使得 Shor 算法破解 RSA-2048 还遥遥无期？

**题 4（四象限判断练习）**：用 Schuld 的 CC/CQ/QC/QQ 四象限，判断以下任务分别落在哪个象限，并预测量子优势的可能性：(a) 用 QNN 分类 MNIST 手写数字；(b) 用 VQE 求咖啡因分子的基态能量；(c) 用神经网络拟合变分波函数；(d) 用 Grover 加速暴力破解 AES-256 密钥；(e) 用量子核方法做信用卡欺诈检测。哪些 hype 严重？哪些有真实价值？

**题 5（PQC 倒计时）**：假设你是某互联网公司的 CISO，公司有 10 亿用户的加密流量。NIST 要求 2035 年前完成 PQC 迁移，「先收集后解密」威胁真实存在。请设计一个迁移路线：哪些系统优先迁？为什么不能等到 2034 年才开始？混合 PQC（PQC + 经典算法）相比纯 PQC 的优劣是什么？中国和美国在 PQC 标准上的差异对你的选型有什么影响？

---

> **本专题核心判断**：量子计算是真实的、正在突破的科学，但量子机器学习（CQ 象限）目前是「理论诱人、工程困难、商业过早」的状态。真正的量子优势会在化学模拟、材料科学、密码学（QQ 象限）里先出现，而不会在文本生成、图像识别这类经典 ML 任务上出现。让量子回去做分子，让经典继续做语言。

<!-- delegate 直接写入，2026-07-20 -->
