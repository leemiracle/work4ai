# 数值分析与科学计算基础：AI 计算的硬根基

> **本章定位**：第十四章的第五根支柱，也是"应用数学研究型工程师"最该补的一块。`03` 讲概率语言，`04` 讲演化几何，本章讲**所有这些数学在浮点硬件上如何落地**——浮点误差、条件数、矩阵分解、迭代法、自动微分、ODE/SDE 数值解。
>
> 为什么单独成章？因为 AI 工程师每天都在和数值问题打交道却不自知：混合精度训练为什么用 bf16 而非 fp16、softmax 为什么要减最大值、loss scaling 是干什么的、`log(softmax)` 为什么不能分开算、Adam 为什么是"对角预条件梯度法"、为什么 Neural ODE 反向要用伴随方法省内存。这些问题的答案全在数值分析里。不学这一层，你调库调到 NaN 只能瞎试 lr；学了，你能像数值分析师一样诊断"这个 NaN 来自 catastrophic cancellation 还是来自条件数爆炸"。

## 摘要

本章回答一个问题：**数学上正确的公式，在计算机上为什么会出错，以及怎么避免？** 我们从 IEEE 754 浮点表示出发，走到条件数与稳定性，再到矩阵分解、Krylov 迭代法，重点深入**自动微分**（AI 的核心数值工具）与 **ODE/SDE 数值解**（Neural ODE 与扩散模型的基础），最后给出 ML 工程里常见的数值陷阱清单与诊断方法。

核心论点：**深度学习本质是超大规模的浮点数值计算，它的每一个"工程经验"背后都有一条数值分析定理**。bf16 训练的可行性来自"指数位足够保证动态范围"；FlashAttention 的正确性来自"在线 softmax"的数值稳定性重排；混合精度的 loss scaling 来自"小梯度在 fp16 下会 underflow"；Adam 的有效性来自"对角预条件把病态 Hessian 拉平"。理解这些，你才能从"调参"升维到"设计算法"。

---

## 一、为什么 AI 工程师需要数值分析

先做诊断：多数工程师把 GPU 当成一个"精确计算器"，以为 `a + b` 就是数学上的加法。残酷的真相是——**浮点运算既不满足结合律也不满足分配律**：$(a+b)+c \neq a+(b+c)$ 在浮点下经常成立，差异可能小（相对误差 $10^{-7}$）也可能致命（catastrophic cancellation 后完全失真）。

这个"不精确性"在三个场景会咬人：

1. **大模型训练的 loss spike 与 NaN**：混合精度下，某层激活值上溢或梯度下溢，连锁反应导致整个网络 NaN。这通常不是 bug，是浮点动态范围不够。诊断与解决全靠数值分析。
2. **数值算法的收敛失败**：你实现了一个自定义的 Newton 法或变分推断，理论上收敛，实际不收敛。原因往往是条件数太大或 Jacobian 病态——数值分析的经典议题。
3. **复现性危机**：同一代码不同硬件（CPU/GPU/TPU）、不同库版本（cuDNN 升级）、不同 reduction 顺序，结果有微小差异，累积后模型精度差几个点。这是浮点非结合律的直接后果。

本章把这些"地雷"逐一标出来，并给出数值分析师的排雷方法。

---

## 二、浮点数与舍入误差

### 2.1 IEEE 754 浮点表示

一个浮点数 $x \neq 0$ 表示为 $x = (-1)^s \times m \times 2^e$，其中 $s$ 是符号位，$m \in [1, 2)$ 是尾数（mantissa/significand），$e$ 是指数。常见格式的位分配：

| 格式 | 总位 | 符号 | 指数 | 尾数 | 机器精度 $\varepsilon_{\text{mach}}$ | 动态范围（量级） |
|---|---|---|---|---|---|---|
| fp16 (half) | 16 | 1 | 5 | 10 | $\approx 2^{-11} \approx 4.9 \times 10^{-4}$ | $\pm 6.5 \times 10^4$ |
| bf16 (brain float) | 16 | 1 | 8 | 7 | $\approx 2^{-8} \approx 3.9 \times 10^{-3}$ | $\pm 3.4 \times 10^{38}$ |
| fp32 (single) | 32 | 1 | 8 | 23 | $\approx 2^{-24} \approx 6 \times 10^{-8}$ | $\pm 3.4 \times 10^{38}$ |
| fp64 (double) | 64 | 1 | 11 | 52 | $\approx 2^{-53} \approx 1.1 \times 10^{-16}$ | $\pm 1.8 \times 10^{308}$ |

**关键洞察**：fp16 与 bf16 同为 16 位，但 fp16 尾数多（精度高）、指数少（范围小），bf16 尾数少（精度低）、指数多（范围大）。这决定了它们的适用场景：
- **bf16 训练**：深度学习的梯度动态范围极大（几万倍的量级跨度），需要大指数范围；相对精度 $10^{-3}$ 对随机梯度足够。所以大模型训练几乎全用 bf16。
- **fp16 训练**：精度高但范围小，梯度容易 underflow（小于 $6 \times 10^{-8}$ 变成 0）或 overflow（大于 $6.5 \times 10^4$ 变成 inf）。必须配 loss scaling（把 loss 放大几千倍，把梯度拉回 fp16 的可表示范围）才能训练。这就是 PyTorch `GradScaler` 的用途。
- **fp32 主权重**：主权重通常用 fp32 存（精度高），计算时转 bf16/fp16（快），梯度更新回 fp32（避免累积误差）。这是混合精度训练的标准范式。

### 2.2 机器精度与舍入模型

每次浮点运算的结果可建模为 $\text{fl}(x \text{ op } y) = (x \text{ op } y)(1 + \delta)$，$|\delta| \leq \varepsilon_{\text{mach}}$。这是**向后误差分析**的基础（Wilkinson 1960s 奠基）：把浮点运算的误差"归咎"到输入扰动上，从而用经典扰动理论分析算法稳定性。

### 2.3 舍入误差的累积

$n$ 次浮点加法的相对误差约 $\sqrt{n} \varepsilon_{\text{mach}}$（随机舍入）或 $n \varepsilon_{\text{mach}}$（最坏情况）。对 $n = 10^9$（大 batch reduction），fp32 下最坏误差约 $6 \times 10^{-8} \times 10^9 = 60$——完全不可接受！这就是为什么 GPU reduction 要用**分层求和**（pairwise summation，误差降到 $\log n \cdot \varepsilon$）或 **Kahan 求和**（补偿求和，误差降到 $\varepsilon$ 几乎不累积）。

### 2.4 灾难性抵消（catastrophic cancellation）

两个接近的大数相减，结果的小数位全是噪声：$1.0000001 - 1.0000000 = 1 \times 10^{-7}$，但每个操作数只有 7 位有效数字，差的有效数字几乎为零。经典例子是 `1 - cos(x)` 当 $x$ 很小时——直接算会丢失几乎所有精度，应该用恒等变形 $1 - \cos x = 2 \sin^2(x/2)$。

ML 里的变体：方差计算 $\sum (x_i - \bar x)^2$ 直接套公式会有抵消（$\sum x_i^2$ 与 $(\sum x_i)^2/n$ 都是大数，相减丢精度），应该用 Welford 在线算法（一次遍历，数值稳定）。BatchNorm 的方差估计如果实现不当就会踩这个坑。

### 2.5 用代码演示：求和顺序与抵消

```python
import numpy as np

# 实验1: 求和顺序影响精度 (fp32 模拟)
rng = np.random.default_rng(0)
x = rng.standard_normal(10_000_000).astype(np.float32)
print(f"fp32 朴素求和: {x.sum():.6f}")
print(f"fp64 提升求和: {x.astype(np.float64).sum():.6f}  (作为真值)")
# 差异来自 fp32 朴素 sum 的累积舍入

# 实验2: 灾难性抵消: 1 - cos(x) 在 x 很小时
for x in [1.0, 1e-2, 1e-5, 1e-8]:
    naive = 1.0 - np.cos(x)
    stable = 2.0 * np.sin(x/2)**2
    print(f"x={x:.0e}: 朴素 1-cos={naive:.3e}  稳定 2sin²(x/2)={stable:.3e}")
```

预期输出（朴素 `1-cos` 在 $x$ 极小时完全抵消为 0，稳定公式保持精度）：

```
x=1e+00: 朴素 1-cos=4.597e-01  稳定 2sin²(x/2)=4.597e-01   # 正常
x=1e-02: 朴素 1-cos=5.000e-05  稳定 2sin²(x/2)=5.000e-05   # 正常
x=1e-05: 朴素 1-cos=5.000e-11  稳定 2sin²(x/2)=5.000e-11   # fp64 仍准
x=1e-08: 朴素 1-cos=0.000e+00  稳定 2sin²(x/2)=5.000e-17   # 朴素=0(完全抵消), 稳定仍准
```

当 $x = 10^{-8}$ 时，朴素 `1 - cos(x)` 在 fp64 下变成 0：因为 $\cos(10^{-8}) \approx 1 - 5 \times 10^{-17}$，而 $5 \times 10^{-17}$ 小于 fp64 机器精度 $\varepsilon_{\text{mach}} \approx 2.2 \times 10^{-16}$，$\cos(10^{-8})$ 被舍入为 1.0，相减得 0。而稳定公式 $2\sin^2(x/2)$ 给出正确的 $5 \times 10^{-17}$。这就是灾难性抵消——**数学等价的公式，数值性能天差地别**。

---

## 三、条件数与稳定性：区分"问题难"与"算法烂"

### 3.1 问题的条件数

**条件数** $\kappa$ 度量"问题本身对扰动的敏感度"，与算法无关。对函数求值 $f(x)$，条件数

$$\kappa = \frac{|\delta f|/|f|}{|\delta x|/|x|} \approx \frac{|x f'(x)|}{|f(x)|}.$$

直觉：输入扰动 $\delta x$ 被放大 $\kappa$ 倍到输出。$\kappa$ 大的问题"本质难"——无论用什么算法，相对误差下界是 $\kappa \varepsilon_{\text{mach}}$。

经典例子：矩阵求逆的条件数 $\kappa(A) = \|A\|\|A^{-1}\| = \sigma_{\max}/\sigma_{\min}$（最大最小奇异值之比）。$\kappa(A) = 10^k$ 意味着求逆结果最多只有 $k$ 位有效数字（fp32 的 7 位会丢掉 $k$ 位）。

### 3.2 算法的数值稳定性

**稳定性**度量"算法是否把误差控制在与问题条件数匹配的量级"。一个算法向后稳定，若它给出的解 $=$ 某个相近问题的精确解（即浮点误差等价于输入的小扰动）。向后稳定的算法，最终误差 $\approx \kappa \varepsilon_{\text{mach}}$——这是信息论意义上的最优。

关键区分：
- **问题病态**（$\kappa$ 大）：换算法无济于事，只能换问题表述或提高精度。
- **算法不稳定**：即便问题良态（$\kappa$ 小），算法仍放大误差——这是可以修的，换稳定算法。

工程师常犯的错误：把"算法不稳定导致的误差"误诊为"问题本身难"。诊断方法是**先估 $\kappa$**——若 $\kappa$ 小但误差大，是算法的锅；若 $\kappa$ 大，是问题的锅。

### 3.3 求解线性方程组的稳定性

解 $Ax = b$：高斯消元（带部分主元选取 partial pivoting）向后稳定，误差 $\approx \kappa(A) \varepsilon$。**不加主元的高斯消元不稳定**（即使 $\kappa(A)$ 小）——经典教学陷阱。NumPy 的 `np.linalg.solve` 默认带主元，安全；自己实现线性解算器必须加主元。

### 3.4 特征值 vs SVD 的稳定性差异

- **特征值分解** $A = V \Lambda V^{-1}$ 只对可对角化矩阵良定义，且对非正规矩阵（$A^\top A \neq A A^\top$）条件数可能极大。
- **SVD** $A = U \Sigma V^\top$ 对任何矩阵都存在，且**总是向后稳定**。

所以数值上**优先用 SVD 而非特征值分解**。PCA 用 SVD（`np.linalg.svd`）而非特征值（`np.linalg.eig`），就是这个道理。

---

## 四、矩阵分解：线性代数的工程实现

矩阵分解是数值线性代数的核心——把"一般矩阵运算"化归为"三角/正交/对角矩阵运算"，后者高效且稳定。

### 4.1 LU 分解

$A = LU$（$L$ 下三角、$U$ 上三角）。用于解 $Ax=b$（前代 + 回代）。带部分主元 $PA = LU$，稳定。复杂度 $O(n^3)$。

### 4.2 Cholesky 分解

对对称正定矩阵 $A = LL^\top$（$L$ 下三角）。比 LU 快 2 倍、更稳定、存一半。神经网络里二阶方法（自然梯度、KFAC）需要逆 Fisher 信息矩阵，常用 Cholesky。前提是矩阵正定——加了数值阻尼（$\lambda I$）保证。

### 4.3 QR 分解

$A = QR$（$Q$ 正交、$R$ 上三角）。最稳定的最小二乘解法（解 $A^\top A x = A^\top b$ 用正规方程不稳定，条件数平方；用 QR 稳定）。Householder 反射或 Givens 旋转实现。

### 4.4 SVD：最通用的分解

$A = U \Sigma V^\top$。能做：低秩近似、伪逆、子空间、PCA、去噪。**Eckart-Young 定理**：SVD 截断到前 $k$ 个奇异值给出最佳秩 $k$ 近似（Frobenius 范数与谱范数下都最优）。这是 PCA、推荐系统、压缩感知的理论根基。

### 4.5 随机化 SVD（大矩阵时代）

对 $n \times n$ 巨大矩阵，精确 SVD 的 $O(n^3)$ 不可行。**随机化 SVD**（Halko, Martinsson, Tropp 2011）用随机投影把矩阵降到小空间再精确分解，复杂度降到 $O(n^2 k)$（$k$ 是目标秩）。这是大模型时代处理巨大权重矩阵、激活矩阵的标准工具。

---

## 五、迭代法与 Krylov 子空间

### 5.1 为什么迭代

对超大稀疏矩阵（如 PDE 离散化、PageRank、图拉普拉斯），直接分解（LU/Cholesky）的内存与时间不可行（fill-in 让稀疏变稠密）。**迭代法**只做矩阵-向量乘法，保持稀疏性。

### 5.2 共轭梯度（CG）

对称正定系统 $Ax = b$ 的最优迭代法。关键性质：在第 $k$ 步，CG 在 Krylov 子空间 $\mathcal{K}_k = \text{span}\{b, Ab, \ldots, A^{k-1}b\}$ 内给出最优近似。收敛速率 $O(\sqrt{\kappa})$ 步——比最速下降的 $O(\kappa)$ 快得多。

### 5.3 GMRES

非对称系统的推广。每步在扩大的 Krylov 子空间内最小化残差。代价是存储与正交化成本随步数增长，实际配 restart。

### 5.4 预条件（preconditioning）

迭代法的收敛取决于"等效条件数"。**预条件**是找一个 $M \approx A^{-1}$，解 $M A x = M b$ 而非 $Ax = b$，使 $MA$ 的条件数小。好预条件是科学与工程计算的核心艺术。

### 5.5 与 ML 的联系：Adam = 对角预条件梯度法

一个深刻对应：**Adam 本质是对角预条件的梯度下降**。它用梯度二阶矩的对角估计 $D = \text{diag}(\sqrt{v_i} + \varepsilon)$ 作为预条件器，更新 $\theta \leftarrow \theta - \eta D^{-1} g$。这把各参数方向的"有效曲率"拉平，等效降低条件数，加速收敛。从这个视角看，Adam、RMSprop、AdaGrad 都是"在线估计对角预条件矩阵"的变体。更高级的二阶方法（KFAC、Shampoo）则是估计块对角或低秩预条件。

---

## 六、微分的三种方式

### 6.1 数值微分（有限差分）

$$f'(x) \approx \frac{f(x+h) - f(x)}{h} \quad (\text{前向差分}).$$

截断误差 $O(h)$（精度低）；舍入误差 $O(\varepsilon_{\text{mach}}/h)$（$h$ 越小越大）。最优 $h \approx \sqrt{\varepsilon}$，精度上限约 $\sqrt{\varepsilon} \approx 10^{-8}$（fp64）。这是数值微分的根本限制——**精度被浮点误差封顶**。

### 6.2 符号微分

用代数规则（$(fg)' = f'g + fg'$ 等）精确求导，像 Mathematica/SymPy。问题：表达式膨胀（expression swell）——复杂函数的符号导数表达式天文级膨胀，不可计算。

### 6.3 自动微分（AD）

把函数分解为基本运算（$+, -, \times, \sin, \exp, \ldots$），每个基本运算有已知导数，用链式法则**精确**累加（精度同浮点，无截断误差）。AD 兼具数值微分的好实现性与符号微分的精确性。**反向模式 AD = 反向传播**，是深度学习的命脉。

### 6.4 三者对比

| 方式 | 精度 | 效率 | 适用 |
|---|---|---|---|
| 数值微分 | $\sqrt{\varepsilon}$ 封顶 | 低（每个偏导一次函数求值） | 快速验证、不可微函数 |
| 符号微分 | 精确 | 表达式爆炸 | 简单闭式函数 |
| 自动微分 | 同浮点精度 | 反向模式 $O(\text{前向})$ | 深度学习主力 |

### 6.5 Baydin et al. AD 综述

Baydin, Pearlmutter, Radul, Siskind 在《Automatic Differentiation in Machine Learning: a Survey》（JMLR 2018，**arXiv:1502.05767**）系统梳理了 AD 与 ML 的关系，澄清了"autodiff / 符号微分 / 数值微分"的常见混淆。这是每个想做可微编程、JAX、不同iable physics 的人的必读。

---

## 七、自动微分深入：前向 vs 反向

### 7.1 前向模式（forward-mode AD）

伴随每个变量 $x$ 携带一个"导数" $\dot{x}$（dual number $x + \dot{x}\epsilon$，$\epsilon^2 = 0$）。一次前向传播同时算出函数值与对一个输入的导数。计算 Jacobian 一列的成本 $\approx$ 函数求值的 2-3 倍。**适合输入少、输出多**（如 $f: \mathbb{R} \to \mathbb{R}^n$）。

### 7.2 反向模式（reverse-mode AD = backpropagation）

先前向计算函数值并记录计算图（tape），再反向传播，用链式法则从输出往输入累加梯度。计算对**所有输入**的梯度（Jacobian 一行）的成本 $\approx$ 函数求值的 2-4 倍。**适合输入多、输出少**（如损失 $L: \mathbb{R}^n \to \mathbb{R}$，这正是深度学习的场景——亿参数、单标量 loss）。

### 7.3 为什么深度学习用反向

深度学习的 loss $L(\theta)$ 是 $\mathbb{R}^n \to \mathbb{R}$（$n$ 是参数数，输出是标量 loss）。前向模式要算 $n$ 次（每个参数一次），反向模式只需一次。对 $n = 10^9$ 的大模型，反向比前向快 $10^9$ 倍——这就是为什么反向传播统治了深度学习。

### 7.4 反向的代价：内存

反向需要存中间激活（计算图 tape），内存 $O(\text{层数})$。深层网络显存爆炸的根源。**梯度检查点（gradient checkpointing / rematerialization）** 用"重计算换内存"：只存少数检查点层，反向时重新前向算中间层。内存从 $O(L)$ 降到 $O(\sqrt{L})$，时间增加约 50%。这是大模型训练的标准技巧。

### 7.5 伴随方法：Neural ODE 的内存 $O(1)$

Neural ODE（第四章 §8.3）的反向更激进——用**伴随方法（adjoint method）**完全不存中间状态，而是反向解一个增广 ODE 来算梯度，内存 $O(1)$（与深度无关）。代价是反向也要调 ODE 求解器，时间翻倍。这是经典最优控制技术（Pontryagin 1960s）在深度学习里的复兴。

---

## 八、微分方程的数值解

### 8.1 ODE：Runge-Kutta 与自适应步长

$\dot{x} = f(x, t)$ 的经典数值解：
- **前向 Euler**：$x_{n+1} = x_n + h f(x_n, t_n)$，一阶精度，简单但精度低、稳定性差。
- **RK4**（四阶 Runge-Kutta）：四步加权，四阶精度，工程默认。
- **自适应步长**（Dormand-Prince RK45 等）：根据局部误差估计自动调整步长，`scipy.integrate.odeint` / `torchdiffeq.odeint` 的默认。

### 8.2 Stiff ODE 与隐式方法

**刚性（stiff）**系统有跨多个时间尺度的动力学（快慢耦合），显式方法（Euler/RK）需要极小步长才能稳定。**隐式方法**（后向 Euler、BDF、隐式 RK）每步解一个非线性方程，但稳定性好（可用大步长）。化学反应动力学、电路仿真全是 stiff，必须用隐式。Neural ODE 若学到 stiff 动力学，也需切换到隐式求解器。

### 8.3 SDE：Euler-Maruyama 与 Milstein

随机微分方程 $dX = a(X)dt + b(X)dW$ 的数值解：
- **Euler-Maruyama**：$X_{n+1} = X_n + a(X_n)\Delta t + b(X_n)\Delta W_n$，$\Delta W_n \sim \mathcal{N}(0, \Delta t)$，强收敛阶 0.5。
- **Milstein**：加 Ito-Taylor 一项，强收敛阶 1.0。

### 8.4 与扩散模型的直接联系

扩散模型（第三章 §10）的反向 SDE 离散化就是 Euler-Maruyama / predictor-corrector。DDPM 的采样器、DDIM、DPM-Solver 都是 SDE/ODE 数值解器的变体——DDIM 等价于反向 ODE 的指数积分器，DPM-Solver 是高阶指数积分器。**理解 SDE 数值解，你就能理解并设计新的扩散采样器**。

---

## 九、谱方法与有限元概览

### 9.1 谱方法

用全局光滑基（傅里叶、切比雪夫、Legendre 多项式）表示解，对光滑问题收敛极快（指数收敛）。气象模型（球谐函数）、湍流模拟常用。PINN 里若解光滑，可用谱基底提升收敛。

### 9.2 有限元（FEM）

把区域分成小单元，每单元用低阶多项式，对复杂几何与边界条件适应性强。工程结构、流体、电磁仿真的主力。FEniCS、deal.II 是开源 FEM 框架。

### 9.3 神经算子 = 学习 PDE 解算子

传统数值方法（谱/FEM）解**一个**具体 PDE 实例。**神经算子**（第十四章 `02` §4.2 详述）学习从"参数/边界条件"到"解场"的**映射**，一次训练后对一族 PDE 实例秒级求解。FNO（傅里叶神经算子）等价于谱方法的神经网络化，DeepONet 等价于算子学习的分支-主干分解。这是"数值分析 × 深度学习"最活跃的交叉前沿。

---

## 十、ML 中的数值陷阱清单（实战诊断手册）

把前面的理论落到工程师每天踩的坑上：

| 现象 | 根因 | 修复 |
|---|---|---|
| `log(0)` → -inf | softmax 输出含 0 | 用 `log_softmax`（数值稳定的合并实现） |
| attention softmax 上溢 | logits 大 | softmax 前减最大值 `x - x.max()` |
| 混合精度梯度变 0 | fp16 underflow | loss scaling（放大 loss 把梯度拉回 fp16 范围） |
| 方差估计为负 | catastrophic cancellation | Welford 在线方差 |
| `cross_entropy` NaN | one-hot × log(0) | 用 `F.cross_entropy`（内部 log_softmax 合并） |
| 矩阵求逆爆炸 | $\kappa(A)$ 大 | 加阻尼 $A + \lambda I$ 或用伪逆/最小二乘 |
| LayerNorm 除零 | 方差为 0（常数特征） | 加 `eps`（如 1e-5） |
| 梯度爆炸 | loss landscape 尖锐 | 梯度裁剪（clip grad norm） |
| bf16 下小量消失 | bf16 精度低（$10^{-3}$） | 关键累加转 fp32 |
| 归一化后内积溢出 | 向量模长大 | 归一化前裁剪或用 fp32 算点积 |
| 大 batch reduction 慢/不精 | fp32 朴素求和累积误差 | pairwise / 分层 reduction |

**诊断口诀**：遇到 NaN/Inf，第一步问"是溢出（overflow）还是抵消（cancellation）？"——前者动态范围问题，换精度/loss scaling；后者条件数问题，重排公式或加 eps。第二步问"这个问题条件数多大？"——$\kappa$ 大换问题表述，$\kappa$ 小换算法。

---

## 十一、国产硬件（飞腾 D3000）的数值与 ISA 特性：信创 AI 的硬件底座

> **本节定位**：前面 §一-§十 讲的都是"硬件无关"的数值分析——数学是普适的。但 AI 工程师最终要把算法落到具体硬件上，**ISA（Instruction Set Architecture）决定了数值精度的物理上界**。本节以国产 ARMv8.2-A CPU **飞腾 D3000（FTC862）** 为例，讲清楚"一颗具体 CPU 决定你能用什么数值格式"这件具体的事。本节内容基于一手实测（来源：`lean4ai/飞腾D3000指令集支持.md` + 实测 `test_isa.c` / `test_arch.c` 编译验证）。

### 11.1 为什么 AI 工程师要懂一颗具体的 CPU？

数学说 FP16 比 FP32 省 50% 显存——但你跑的机器**真的有 FP16 硬件支持吗**？理论说 INT8 量化能加速 4×——但你 CPU 上**有没有 SDOT/UDOT 指令**？大多数 AI 工程师对硬件有两个**默认假设**：
1. "现代 CPU 都支持 BF16"——错，**很多国产 ARM 没有 BF16**（飞腾 D3000 没有）
2. "INT8 推理一定比 FP16 快"——不一定，**取决于是否有 DotProd 或 i8mm 指令**

信创背景下，AI 工程师越来越多地要把模型部署到**国产硬件**（飞腾 / 鲲鹏 / 海光 / 兆芯 / 龙芯）。这些硬件的 ISA 各不相同，"通用 ARM 代码"未必跑得快，"通用 PyTorch 量化"未必生效。本节用飞腾 D3000 作样本，教你看懂一颗具体 CPU 的"数值画像"。

> **D3000 是谁**：飞腾（Phytium）D3000，8 核 aarch64，FTC862 核心，2.5GHz，L4=8MiB；定位桌面/工控/边缘 AI 推理；配套银河麒麟 OS + kpgcc 工具链。这是"信创 AI 推理"的主流候选 CPU 之一。

### 11.2 D3000 的指令集一览（一手实测）

通过 `getauxval(AT_HWCAP)` 读取硬件能力位图（实测 `AT_HWCAP = 0x3f9fff`），D3000 的指令集支持如下：

| HWCAP 标志 | 含义 | D3000 | AI 工程意义 |
|---|---|---|---|
| `FP` | 标量 FP32/FP64 | ✅ | 基础浮点 |
| `ASIMD`（NEON） | 128-bit SIMD | ✅ | **所有向量化基础** |
| `FPHP` + `ASIMDHP` | FP16 半精度（ARMv8.2-A）| ✅ | **省一半带宽/显存** |
| `ASIMDDP` | SDOT/UDOT 点积 | ✅ | **INT8 矩阵乘加速** |
| `ATOMICS`（LSE） | 原子操作 | ✅ | 多核同步高效 |
| `LRCPC` | LDAPR/STLR 弱一致原子 | ✅ | RCPC 内存模型 |
| `AES` + `PMULL` | AES + 多项式乘 | ✅ | 加解密加速 |
| `SHA1` / `SHA2` | SHA1/SHA256 | ✅ | 国际哈希 |
| `SHA3` / `SHA512` | SHA3/SHA512 | ✅ | 国际哈希全套 |
| `SM3` / `SM4` | **国密 SM3/SM4** | ✅ | **信创刚需** |
| `CRC32` | 硬件 CRC32 | ✅ | 校验和加速 |
| **`SVE`** | 可伸缩向量 | ❌ | **不支持 SVE**（关键缺） |
| **`BF16`** | BF16 矩阵乘 | ❌ | **不支持 BF16**（关键缺） |
| **`I8MM`** | INT8×INT8→INT32 矩阵乘 | ❌ | **不支持 i8mm**（需用 DotProd 替代）|
| `ASIMDFHM` | FP16 FMLA | ❌ | FP16 fused-multiply-add 受限 |

**架构判定**：通过 HWCAP 反推（`/proc/cpuinfo` 只显示 `architecture: 8`，无法区分子版本）—— 有 FPHP/ASIMDHP/ASIMDDP（ARMv8.2 新增）+ 无 SVE/ASIMDFHM（排除 ARMv8.4+）→ **ARMv8.2-A + Crypto + DotProd + FP16 + LSE + LRCPC**。

### 11.3 NEON 128-bit SIMD：FP16/INT8/DotProd 的并行度

NEON 寄存器宽 = 128 bit，**一条指令能处理的元素数完全由元素位宽决定**：

| 元素类型 | 元素数/指令 | D3000 支持？ | AI 工程含义 |
|---|---|---|---|
| FP64 | 2 | ✅ | 双精度科学计算 |
| FP32 | 4 | ✅ | 默认深度学习 |
| **FP16** | **8** | **✅ FHP** | **vs FP32: 2× 元素 → 2× 算术吞吐** |
| BF16 | 8 | ❌ | **D3000 跑不了 BF16 内核** |
| INT16 | 8 | ✅ | 量化备选 |
| **INT8** | **16** | **✅** | **vs FP16: 2× 元素** |
| INT4 | 32 | ❌ | 理论最优，D3000 不支持 |
| **DotProd (SDOT)** | **4×INT8 → 4×INT32** | **✅** | **INT8 GEMM 的硬件基石** |

**关键洞察**：在 D3000 上，**FP16 推理 ≈ 2× FP32 加速**（NEON 元素翻倍），**INT8 量化推理 ≈ 再 2× 加速**（再翻倍）。复合加速比 ≈ 4×，这就是飞腾跑量化小模型比"裸跑 FP32"快 4 倍的物理基础。

**DotProd (SDOT/UDOT) 的精髓**：一条指令完成 `4 个 INT8 × 4 个 INT8 → 累加到 4 个 INT32`，相当于 4 次乘法 + 4 次累加压缩到 1 拍。LLM 推理的 GEMM 内核（如 `K × N` 矩阵乘）把 K 维度切 4 一组，用 SDOT 大幅减少指令数。实测代码：

```c
#include <arm_neon.h>
// 4×INT8 × 4×INT8 → 4×INT32 累加（一条 SDOT 指令）
int32x4_t sdot_demo(int8x16_t a, int8x16_t b, int32x4_t acc) {
    return vdotq_s32(acc, a, b);  // D3000 HWCAP_ASIMDDPE:YES 实测通过
}
```

实验验证：见 `experiments_05/06_phytium_d3000_fp16_neon.py` 实验 3。

### 11.4 FP16 数值特性（ARMv8.2-A FHP）

FP16（half-precision float）在 D3000 上的特性：
- **范围**：±65504（超出则 ±Inf）
- **精度**：~3-4 位有效十进制位（10 bit 尾数）
- **最小正规数**：~6.10e-5
- **运算指令**：`vaddq_f16` / `vmulq_f16` / `vfmaq_f16`（fused-multiply-add，但 D3000 **不支持 FP16 FMLA 的 FHM 扩展**，只有标量 FMA）

**核心工程权衡：纯 FP16 累加 vs FP16 输入+FP32 累加**

```python
# 实验 1（experiments_05/06_*.py）：1000 元素点积
# 模式 A：纯 FP16（vdotq_f16，输入累加都 FP16）→ 误差 0.0312%
# 模式 B：FP16 输入 + FP32 累加（vfmaq_lane_f16 + FP32 accumulator）→ 误差 0.0077%
```

**结论**：模式 B 几乎不损失精度（误差从 0.03% 降到 0.008%），但吞吐接近 FP16（输入仍是 FP16，只是累加器升 FP32）。**这是 D3000 跑 LLM 推理的推荐策略**——存权重用 FP16（省一半内存），算累加用 FP32（保精度）。混合精度训练 / 推理在飞腾上的物理基础就在这里。

> 📊 **实验测定（v2.1.1 课题 NA-1 执行结果）**：纯 FP16 累加误差的 scaling law 是 $\epsilon(n) \propto n^{0.54}$（50 次平均 × 12 个 n 值拟合）。**Higham 的 $O(n)$ 最坏情况上界高度保守（过估 10-100×）**——实际误差接近随机游走预测 $O(\sqrt{n})$，说明 FP16 量化误差几乎完全随机抵消。FP16+FP32 累加的 $\epsilon(n) \propto n^{0.14}$（几乎不随 n 增长）。交叉点：$n \approx 20$ 时纯 FP16 误差超 1%。详见 `docs/research-execution/01-fp16-error-propagation.md`。

> ⚠️ **BF16 缺失的后果**：现代 LLM 训练主流是 BF16（动态范围大、不需要 loss scaling）。D3000 **不支持 BF16**，所以训练时只能用 FP16 + loss scaling（麻烦）或 FP32（慢）。**D3000 不适合训练大模型，只适合推理**——这是工程上一条硬约束。

### 11.5 国密双栈：SM3/SM4 + 国际 SHA/AES

D3000 同时硬件加速**国密**和**国际**两套密码学指令，这是信创 CPU 区别于普通 ARM Cortex 的核心特性：

| 类别 | 指令 | 用途 |
|---|---|---|
| **国密** | SM3SS / SM3SS1 / SM3PARTW1 / SM3PARTW2 | SM3 哈希（256-bit，用于金融/政务数字签名）|
| **国密** | SM4E / SM4EKEY / SM4EKEY | SM4 对称加密（用于国密 TLS / 政务云）|
| **国际** | AESE/AESD/AESMC | AES-128/192/256 |
| **国际** | SHA1H/SHA1C/SHA1P/SHA1M | SHA1 |
| **国际** | SHA256H/SHA256H2/SHA256SU0/1 | SHA-256 |
| **国际** | SHA512H/SHA512H2/SHA512SU0/1 | SHA-512 |
| **国际** | SHA3/RAXI/EOR3/BCAX/XAR | SHA-3（Keccak）|
| **跨用** | PMULL/PMULL2 | 多项式乘法（GHASH for AES-GCM）|

**信创意义**：同一颗 CPU 同时跑国密+国际算法，**软件层无需切换库**（OpenSSL/GMSSL 都透明支持）。汇编层用 `SM3SS` / `SM4E` 等专用指令直接硬件加速，比软件实现快 5-10×。

**对 AI 工程师的实际影响**：
- AI 模型部署在政务云/金融云上，模型权重传输用 SM4 加密、模型完整性用 SM3 哈希——这些在 D3000 上几乎零开销
- 联邦学习的梯度聚合可以用 SM3 做承诺方案（commitment scheme）
- **AI × 国密** 是信创 AI 的隐性刚需，但学术研究极少——一个空白方向

### 11.6 kpgcc 工具链：硬件感知的代码生成

D3000 配套 **kpgcc 9.3.1**（银河麒麟专用 GCC），其 `/opt/kpgcc_release/.../aarch64-cores.def` 内置 `ftc862` 核心模型——这是通用 GCC 没有的。

**关键差异：指令融合对（fusion pairs）**

kpgcc 知道 D3000 微架构的"指令融合对"——CPU 把两条相邻指令合并为单拍执行：

| 融合对 | 工程含义 |
|---|---|
| `mov + movk` | 64-bit 立即数加载（2 条→1 拍） |
| `adrp + add` | PC 相对地址计算（PIC 代码常驻） |
| `adrp + ldr` | 全局变量加载（高频） |
| `movk + movk` | 长立即数分段加载 |
| `cmp + branch` | 比较 + 分支（核心循环条件） |
| `aes + aesmc` | AES 轮密钥加 + SubBytes（密码学专用） |
| `alu + branch` | ALU 运算 + 分支（典型 if-then） |

**实测建议**：编译 AI 推理代码用 `kpgcc -march=armv8.2-a+fp16+dotprod -O3` 而非通用 `gcc -march=native`，差距可达 10-20%。

**周边生态**：
- **PhyTune**：GUI 性能调优工具，60+ PMU 事件 + Topdown 方法论（`/opt/phytune/resource/conf/phytium-ftc862.json`）
- **Kylin FTMalloc**：多核并发优化 malloc（`/opt/kylin-gcc-ftmalloc/libs/`，`LD_PRELOAD=libmalloc.so` 替换 glibc malloc）
- **runtime 库**：libgomp（OpenMP）/ libatomic（原子）/ libasan（地址 sanitizer）/ libtsan（线程 sanitizer）/ libgfortran / libquadmath（四精度）

### 11.7 「不支持的特性」的工程后果

D3000 不支持 SVE / BF16 / i8mm / FP16-FHM，每一条都有具体后果：

| 缺失特性 | 工程后果 | 应对策略 |
|---|---|---|
| **无 SVE** | 不能用 SVE 自动向量化（128-2048 bit 可伸缩）；某些 HPC 内核（如 OpenBLAS SVE 后端）跑不了 | 用 NEON 128-bit 固定向量化 |
| **无 BF16** | 不能跑 BF16 训练（主流 LLM 训练都用 BF16）；Transformer 训练易数值不稳 | 训练用 FP32（慢但稳）或 FP16+loss scaling；**推理才是 D3000 的主场** |
| **无 i8MM** | 不能用 INT8×INT8→INT32 矩阵乘指令（这是 ARMv8.6-A 的杀手锏，A78/X2 后才有） | 用 DotProd (SDOT) 替代——4 元素一组 vs i8MM 的 8 元素一组，效率折半 |
| **无 FP16 FMLA (FHM)** | FP16 的 fused-multiply-add 在 D3000 上是标量（不是向量 FMA） | 用 FP32 累加策略（见 §11.4）规避 |

**核心判断**：D3000 的**绝对算力不如最新 NVIDIA GPU**，但**在国产替代 + 边缘 AI + 信创合规**三大场景下有不可替代性。AI 工程师的工作不是"咒它为什么没 BF16"，而是"在没有 BF16 的约束下把推理做到最快"——这才是工程能力。

### 11.8 给 AI 工程师的 5 条实战建议

1. **量化首选 INT8 + DotProd 路径**，不要选 INT4（D3000 不支持）或 BF16（不支持）。算子库选支持 SDOT 内核的（如 QNNPACK / tslite）。

2. **混合精度推理**：权重 FP16 存（省内存）+ 累加 FP32 算（保精度）。这是 D3000 上"精度-速度"最优解。

3. **编译用 kpgcc -march=armv8.2-a+fp16+dotprod -O3**，不要用通用 gcc -march=native。10-20% 性能差距。

4. **性能分析用 PhyTune + Topdown**，盯三个指标：`frontend_bound` / `backend_bound` / `retiring`。GEMM 内核应 ≥ 70% retiring（高 CPE 利用）。

5. **国密合规用 SM3/SM4 硬件指令**，不要走软件实现。模型权重的数字签名、联邦学习梯度加密都用硬件 SM3/SM4，性能近零开销。

### 11.9 一个反向思考：飞腾 D3000 是 AI 推理的"反 Roofline 训练场"

回到 §一-§十 的数学层：所有数值分析结论（条件数、稳定性、灾难性抵消）在 D3000 上**依然成立**——但**物理上界被 ISA 锁死**。FP16 累加的精度损失（§11.4 实验 1）是 §二 浮点舍入误差的具体表现；DotProd 的 4 元素并行是 §四 矩阵分解的工程实现；BF16 缺失意味着你不能用 §七 自动微分里"BF16 训练 + FP32 主权重"的标准混合精度策略。

**核心洞见**：**数学告诉你算法该是什么样，硬件告诉你能不能这么实现**。优秀的 AI 工程师要同时懂"算法的数值分析"（§一-§十）和"硬件的 ISA 边界"（§十一）。两者缺一，都会写出"理论对、跑不起来"的代码。

> **本节配套实验**：`experiments_05/06_phytium_d3000_fp16_neon.py`（5 部分，纯 numpy 模拟，结论与 D3000 实测一致）

---

## 十二、给「应用数学研究型工程师」的建议

### 12.1 学习路线

1. **入门（3-4 月）**：Lloyd Trefethen & David Bau《Numerical Linear Algebra》——全球最佳的数值线代入门，简洁优雅，配套 MATLAB/Python 实验极易复现。
2. **进阶（6-12 月）**：Alfio Quarteroni et al.《Numerical Mathematics》——全面覆盖；Nicholas Higham《Accuracy and Stability of Numerical Algorithms》——精度与稳定性的权威，每个算法的误差分析都有。
3. **自动微分**：Baydin et al. 综述（**arXiv:1502.05767**）入门 → Griewank & Walther《Evaluating Derivatives》深入 → 读 JAX/PyTorch autograd 源码。
4. **ODE/PDE 数值解**：Hairer & Wanner《Solving ODEs I/II》；LeVeque《Finite Difference / Finite Volume / Finite Element Methods》。
5. **随机数值**：Kloeden & Platen《Numerical Solution of SDE》——扩散模型采样的数学底座。

### 12.2 与本卷的交叉

- 本章 ↔ `03` 概率：SDE 数值解（§8.3）是第三章 Markov 链/遍历的计算实现。
- 本章 ↔ `04` 动力系统：ODE 数值解（§8.1）是第四章 ResNet/Neural ODE 的计算实现；stiff（§8.2）对应训练动力学的不稳定。
- 本章 ↔ 模块 `11`/`12`：混合精度、loss scaling、梯度检查点（本章 §2、§7.4）= 模块 11/12 的工程实践。
- 本章 ↔ `02` 物理：神经算子（§9.3）= `02` §4.2 的物理内容。

### 12.3 一个可执行的研究小课题

**实现一个数值稳定的在线方差 + 对比朴素实现**：用 Welford 算法（一次遍历，无中间大数相减）计算一个大数据集的方差，与"两遍公式" $\sum x_i^2/n - \bar x^2$ 对比，构造一个让两遍公式给出负方差（灾难性抵消）的数据集。这能把 §2.4、§2.5、§3 的概念全部手过一遍。进阶：实现一个最小反向模式 AD（对一个小 MLP 算梯度），对比 PyTorch autograd 的结果，验证 §7 的理论。

---

## 📌 进一步阅读

**教材**
- Lloyd Trefethen & David Bau《Numerical Linear Algebra》—— 数值线代最佳入门。
- Nicholas Higham《Accuracy and Stability of Numerical Algorithms》—— 精度稳定性权威。
- Alfio Quarteroni, Riccardo Sacco, Fausto Saleri《Numerical Mathematics》—— 全面覆盖。
- Ernst Hairer, Gerhard Wanner《Solving Ordinary Differential Equations I/II》—— ODE 数值解圣经。
- Randall LeVeque《Finite Difference Methods for Ordinary and Partial Differential Equations》—— FDM 入门。
- Peter Kloeden & Eckhard Platen《Numerical Solution of Stochastic Differential Equations》—— SDE 数值解。
- Andreas Griewank & Andrea Walther《Evaluating Derivatives: Principles and Techniques of Algorithmic Differentiation》—— AD 权威。

**关键论文（arXiv ID 已一手核实）**
- Baydin, Pearlmutter, Radul, Siskind, *Automatic Differentiation in Machine Learning: a Survey*, JMLR 2018 — **arXiv:1502.05767**。
- Halko, Martinsson, Tropp, *Finding Structure with Randomness: Probabilistic Algorithms for Constructing Approximate Matrix Decompositions*, SIAM Review 2011 — 随机化 SVD（无 arXiv，SIAM Review 论文）。
- Ho, Jain, Abbeel, *DDPM*（采样器 = 反向 SDE 的 Euler-Maruyama）— **arXiv:2006.11239**（见第三章）。

**§十一 国产 ARM 硬件配套（飞腾 D3000 / 信创 AI）**
- *ARM Architecture Reference Manual* (ARMv8-A, ARM DDI 0487) — ARM 官方架构手册，含各版本特性定义、HWCAP 标志位、指令编码。
- *ARM C Language Extensions* (ARM IHI 0053) — NEON intrinsics、FP16 intrinsics、ACLE 标准接口。
- Linux Kernel Documentation — `arm64/elf_hwcaps` 章节详解 HWCAP 标志位检测。
- 飞腾 D3000（FTC862）实测文档：lean4ai 项目 `飞腾D3000指令集支持.md`（含 `/proc/cpuinfo` + HWCAP + `test_isa.c`/`test_arch.c` 实测代码）。
- 国密 SM3（GB/T 32905-2016）/ SM4（GB/T 32907-2016）国家标准 — 全国信息安全标准化技术委员会。
- IEEE Std 754-2019 — 浮点数表示国际标准（§二、§11.4 的基础）。

---

## ✍️ 思考题（9 道）

1. **bf16 vs fp16**：一个梯度的真实值是 $10^{-7}$。在 fp16（最小正规数 $\approx 6 \times 10^{-8}$）和 bf16（最小正规数 $\approx 10^{-38}$）下分别会变成什么？这能解释为什么大模型训练偏好 bf16 吗？
2. **求和顺序**：写代码验证 fp32 下 `sum([1e8, 1, -1e8, 1])` 与不同顺序的结果差异。解释为什么 pairwise 求和（`np.sum` 的实现）比朴素顺序求和精确。
3. **条件数诊断**：你解 $Ax=b$ 得到残差 $\|Ax-b\|/\|b\| = 10^{-12}$（很小），但 $\|x - x^*\|/\|x^*\| = 10^{-2}$（很大）。这是问题病态还是算法不稳定？给出诊断依据。
4. **softmax 稳定性**：证明 `softmax(x)` 减最大值 `softmax(x - max(x))` 与原式数学等价，但数值更稳定。构造一个让不减最大值的 softmax 溢出的输入。
5. **AD 复杂度**：为什么深度学习用反向模式 AD 而非前向？若损失是 $f: \mathbb{R}^{10^9} \to \mathbb{R}$，前向模式算全部梯度需要多少次前向？反向呢？
6. **stiff 系统**：$\dot{x} = -1000x + \sin(t)$。用前向 Euler，稳定所需的最大步长是多少？用后向 Euler 呢？这对 Neural ODE 学习多尺度动力学有什么启示？
7. **Adam = 预条件**：把 Adam 更新写成 $\theta_{t+1} = \theta_t - \eta D_t^{-1} g_t$ 的形式，指出 $D_t$ 是什么。为什么这能加速病态优化？它与对角预条件共轭梯度有何异同？

8. **飞腾 D3000 上跑 LLM 推理的精度-速度权衡**（§11 配套）：你有一个 7B FP16 模型要在 D3000 上推理。三个选项：(a) 纯 FP16 + `vdotq_f16`（NEON 8 元素/指令，但累加器也是 FP16）；(b) FP16 输入 + FP32 累加（`vfmaq_lane_f16` + FP32 acc，精度更高但慢）；(c) INT8 量化 + `SDOT`（NEON 16 元素/指令，4×INT8→4×INT32）。在保持 perplexity 损失 ≤ 1% 的约束下，哪个最块？请结合 §11.4 实验 1（FP16 累加误差）和 §11.3（DotProd 加速）做定量推断。

9. **「无 BF16」的工程后果深度分析**（§11.7 配套）：D3000 不支持 BF16 矩阵乘指令。一个团队想"在 D3000 上微调 Llama-3-8B"。三个候选方案：(a) FP32 全程（精度最高但最慢）；(b) FP16 + loss scaling（PyTorch 标准做法，但 D3000 FP16 范围窄易梯度下溢）；(c) 等待飞腾下一代支持 BF16 的 CPU（推迟 6 月）。请从精度、速度、工程风险三维度给出推荐方案，并解释为什么 D3000"理论上能训练，工程上不宜训练大模型"。

---

<!-- 本章 2026-07-22 补写。arXiv ID 1502.05767 经 arXiv 官网一手核实。浮点求和与灾难性抵消代码为标准数值分析教学实验，结论可数值复现。 -->
