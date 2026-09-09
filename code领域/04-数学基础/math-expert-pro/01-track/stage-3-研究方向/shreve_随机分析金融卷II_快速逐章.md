# Steven E. Shreve《随机分析金融 II：连续时间模型》 · 快速逐章精读

> **原书名**：Stochastic Calculus for Finance II: Continuous-Time Models　**丛书**：Springer Finance　**著者**：Steven E. Shreve　**年份**：2004
> **读于**：2026-07-03
> **定位**：金融数学连续时间模型的标杆教材，从一般概率论与 Brown 运动出发，严格建立 Itô 随机积分，最终推出 Black-Scholes 定价与利率期限结构模型。
> **特色**：以「Itô 积分 → 鞅 → 风险中性测度」三步统一连续时间金融，证明严格却配有大量金融直觉与计算实例，是工程导向研究者进入随机分析的最佳单卷入门。
> **声明**：本文为「快速逐章精读」，每章给核心逻辑串联 + 飞腾锚点 + 关键定理（LaTeX）+ 自测题，非逐页翻译。

---

## §0 引言：Shreve 卷 II 是什么，为什么读它

Steven Shreve（Carnegie Mellon 计算金融创始人）的《随机分析金融》两卷本是华尔街量化金融与学术随机分析的**标准桥梁**。卷 I 用二叉树模型（离散）建立无套利定价的直觉，卷 II 则跨入连续时间：从测度论概率（Ch 1-2）经 Brown 运动（Ch 3）建立 Itô 随机微积分（Ch 4），再用 Girsanov 换测度与等价鞅测度推出风险中性定价（Ch 5），最后打通 PDE（Ch 6）、奇异与美式期权（Ch 7-8）、利率模型（Ch 9-10）与跳过程（Ch 11）。

全书精神可浓缩为一句：**「Brown 运动是无处可导的混沌，Itô 积分给混沌装上微积分，等价鞅测度把定价化为求期望。」**

与 Karatzas-Shreve GTM113（纯数学研究级，以半鞅为终点）不同，Shreve 卷 II 始终锚定金融应用——每个定理都指向一个定价问题。与卷 I（二项模型）的直接接续关系是：卷 I 证明的「离散无套利 $\iff$ 风险中性概率」在卷 II 连续化为「资产定价基本定理」。

对做深度学习的读者，本书的 Itô 公式直接支撑 score-based 扩散模型（反向 SDE），鞅测度关联变分推断与强化学习的 Bellman 方程，Girsanov 换测度对应重要性采样（importance sampling）的连续时间版——这是概率随机过程方向的核心教材，也是「1944 年 Itô 的纯数学」在「2021 年深度学习」中复活的典型范例。

**读书策略**：Ch 1-2 若已读 Williams《概率与鞅》可快速过，重点核对 filtration 与条件期望的记号约定；Ch 3-4（Brown 运动 + Itô 积分）是必须逐节手推的技术核心，建议用 Python 跑蒙特卡洛验证 Itô 公式的 $\frac{1}{2}f_{xx}\,dt$ 项；Ch 5（Girsanov + 资产定价基本定理）是金融灵魂，要能手推 Black-Scholes 公式；Ch 6-11 按应用需求选读，Ch 6 的 Feynman-Kac 与 Ch 10 的利率模型对量化工程最有用。

| 书 | 风格 | 严格性 | 适合谁 |
|---|---|---|---|
| **Shreve《随机分析金融 II》** | 金融驱动、直觉与证明并重、单卷自洽 | 高（完整测度论 + Itô 积分严格构造） | 想用最短路径从概率抵达 Black-Scholes 与利率模型的工程研究者 |
| **Karatzas-Shreve GTM113** | 纯数学研究级、半鞅框架、样本轨道优先 | 极高（研究级严格，无金融应用） | 做随机分析理论研究的数学研究生 |
| **Williams《概率与鞅》** | 鞅中心化、文学化、离散鞅为主 | 高（测度论完整，但不碰 Itô 积分） | 想先吃透离散鞅论再升级连续时间者 |
| **Shreve 卷 I（二项模型）** | 离散、无测度论、完全靠二叉树直觉 | 中（无严格证明，靠复制论证） | 零基础入门无套利定价，作为卷 II 前置 |

---

## §1 全书 11 章骨架一览（飞腾锚点分布）

| 章 | 标题 | 核心概念 | 飞腾锚点 |
|:--:|------|----------|----------|
| 1 | General Probability Theory | $\sigma$-代数、filtration、条件期望、鞅基础 | TLB 4.81× |
| 2 | Information and Conditioning | 信息流、Markov 性、独立性 | Schmidt 正交化 |
| 3 | Brownian Motion | 定义、连续路径、鞅性、二次变分、Lévy 刻画 | FP16 3.81× |
| 4 | Stochastic Calculus | Itô 积分、Itô 公式、二次变分 | UDOT 16.9× |
| 5 | Risk-Neutral Pricing | Girsanov 定理、等价鞅测度、资产定价基本定理 | matmul 15× |
| 6 | Connections with PDEs | Feynman-Kac、Black-Scholes PDE | TLB 4.81× |
| 7 | Exotic Options | barrier、Asian、lookback、反射原理 | 分支预测 0.71/3.14 |
| 8 | American Derivative Securities | 最优停时、Snell 包络 | Iron Law <2% |
| 9 | Change of Numéraire | 远期测度、计价单位变换 | GEMM 9.45 GFLOPS |
| 10 | Term Structure Models | Vasicek、CIR、HJM 框架 | FP16 3.81× |
| 11 | Introduction to Jump Processes | Poisson 过程、跳-扩散、Itô-Lévy 公式 | UDOT 16.9× |

> **飞腾锚点复用说明**：11 章 > 8 个锚点，故合理复用（同一锚点隔数章再出现，标注不同角度），保证相邻章绝不重复。TLB 在 Ch 1（$\sigma$-代数分层）/ Ch 6（Feynman-Kac PDE 网格离散）双用，前者是「可测集层级生成」、后者是「时空网格的局部性」；FP16 在 Ch 3（Brown 路径模拟精度）/ Ch 10（利率 SDE 模拟精度）呼应，前者关注二次变分数值、后者关注均值回归稳态；UDOT 在 Ch 4（Itô 积分点积累加）/ Ch 11（Poisson 跳计数累加）呼应，前者连续、后者离散跳跃，均为「和式积累」的硬件加速。

---

### 第 1 章 · General Probability Theory（一般概率论）

**核心**：从样本空间出发建立概率的测度论基础。$\sigma$-代数把「可观测事件」形式化，随机变量是可测函数，filtration $\{\mathcal{F}_t\}$ 把时间引入——信息只增不减。

期望是 Lebesgue 积分，条件期望 $E[X|\mathcal{G}]$ 是部分信息下的最优预测（$L^2$ 中为正交投影）。本章还引入鞅：$E[M_t|\mathcal{F}_s]=M_s$，即「公平游戏」。Shreve 卷 I 的二项模型是本章的离散原型——卷 I 的「风险中性概率」在这里被严格化为「使贴现价格为鞅的测度」。

**飞腾锚点**：🟢 **TLB 4.81× [E04]** —— $\sigma$-代数 $\mathcal{F}_t=\sigma(W_s:s\leq t)$ 是逐步「解锁」的事件层级，正如 CPU 虚拟地址经页表分层翻译（TLB 缓存近期翻译）。filtration 的「信息只增」对应「页表项一旦填入就驻留」，TLB 命中率 4.81× 提升正是分层局部性的回报。

**关键定理**：**条件期望存在性**（Radon-Nikodym 保证）。给定 $X\in L^1$ 与子 $\sigma$-代数 $\mathcal{G}$，存在唯一 $E[X|\mathcal{G}]\in L^1$ 使

$$\int_A E[X|\mathcal{G}]\,dP=\int_A X\,dP,\qquad \forall A\in\mathcal{G}.$$

重要性：条件期望是全书的中心操作，鞅、Markov 性、Girsanov 全部建立在它之上。没有 Radon-Nikodym 定理，条件期望的存在性无法保证。

**自测**：$X\sim N(0,1)$，$\mathcal{G}=\sigma(\mathrm{sgn}(X))$。算 $E[X|\mathcal{G}]$。

> 提示：$\mathrm{sgn}(X)=+1$ 时 $X>0$，$E[X|X>0]=E[|X|]=\sqrt{2/\pi}$；同理 $\mathrm{sgn}(X)=-1$ 时 $E[X|X<0]=-E[|X|]$。故 $E[X|\mathcal{G}]=\mathrm{sgn}(X)\sqrt{2/\pi}$。

---

### 第 2 章 · Information and Conditioning（信息与条件）

**核心**：filtration 是「信息流」的数学化——$\mathcal{F}_t$ 包含到时刻 $t$ 为止观测到的所有事件。条件期望 $E[X|\mathcal{F}_t]$ 是用截至 $t$ 的信息对 $X$ 的最优预测。

独立性意味着条件不改变预测：$X\perp\!\!\!\perp\mathcal{G}\Rightarrow E[X|\mathcal{G}]=E[X]$。**Markov 性**是「未来只依赖现在」：$E[f(X_{t+s})|\mathcal{F}_t]=E[f(X_{t+s})|X_t]$——历史信息一旦压缩进当前状态 $X_t$ 便不再提供额外预测力。本章把 Ch 1 的测度工具「时间化」，为 Brown 运动和鞅搭建舞台。

**飞腾锚点**：🟡 **Schmidt 正交化** —— 条件期望 $E[X|\mathcal{F}_s]$ 在 $L^2$ 是 $X$ 向 $\mathcal{F}_s$-可测子空间的正交投影，误差 $X-E[X|\mathcal{F}_s]$ 与子空间正交。这与 Schmidt 正交化「逐维投影取残差」同构——每多一层信息（更大 $\sigma$-代数），残差方差减小，正如逐步正交化降低分量间冗余。

**关键定理**：**塔性质（Tower Property）**。若 $\mathcal{G}\subseteq\mathcal{H}$（$\mathcal{G}$ 是更粗的信息），则

$$E\bigl[E[X|\mathcal{H}]\bigm|\mathcal{G}\bigr]=E[X|\mathcal{G}].$$

重要性：信息越粗预测越「平滑」——先用细信息预测再用粗信息平均，等于直接用粗信息预测。这是鞅定义与 Markov 性的逻辑基石。

**自测**：$W_t$ 为 Brown 运动，$s<t$。算 $E[W_t^2|\mathcal{F}_s]$。

> 解：$W_t=W_s+(W_t-W_s)$，增量独立于 $\mathcal{F}_s$。故 $E[W_t^2|\mathcal{F}_s]=W_s^2+E[(W_t-W_s)^2|\mathcal{F}_s]+2W_s\cdot 0=W_s^2+(t-s)$。

---

### 第 3 章 · Brownian Motion（Brown 运动）

**核心**：Brown 运动 $W_t$ 是连续时间随机过程的基石。定义：(1) $W_0=0$；(2) 增量独立且 $W_t-W_s\sim N(0,t-s)$；(3) 路径连续。

关键性质：$W_t$ 是鞅、处处连续但几乎处处不可导、二次变分 $\langle W\rangle_t=t$（路径「抖动」总量正比于时间）。直觉上，Brown 路径在任意小区间内的「总位移绝对值」无穷大，但「净位移」平方的期望恰等于区间长度。

**Lévy 刻画定理**：连续鞅且 $\langle M\rangle_t=t$ 则 $M$ 是 Brown 运动——从「鞅性 + 二次变分」反推 Brown 运动的判据，无需逐一验证增量分布。这是 Ch 4 Itô 积分合理性的根基。

**飞腾锚点**：🟢 **FP16 3.81× [L01]** —— Brown 路径处处不可导但连续，数值模拟必须离散化为 $\Delta W_t\sim N(0,\Delta t)$。路径积分精度取决于 $\Delta t$ 细度与浮点表示，FP16 的 3.81× 吞吐使大规模路径模拟（蒙特卡洛）成为可能，但半精度尾数有限会引入二次变分累积误差——$\langle W\rangle_t=\sum(\Delta W)^2\approx t$ 的数值验证需关注精度。

**关键定理**：**Lévy 刻画定理**。若 $M_t$ 是连续局部鞅，$M_0=0$，且二次变分 $\langle M\rangle_t=t$，则 $M_t$ 是 Brown 运动：

$$\text{连续鞅}+\langle M\rangle_t=t\quad\Longrightarrow\quad M_t\sim\text{Brown 运动}.$$

重要性：给定一个 SDE 的解，只需验证「鞅性 + 二次变分」即可判定它就是 Brown 运动。

**自测**：用 $W_t\sim N(0,t)$，算矩母函数 $E[e^{\sigma W_t}]$。

> 解：$E[e^{\sigma W_t}]=\int e^{\sigma x}\frac{1}{\sqrt{2\pi t}}e^{-x^2/(2t)}\,dx=e^{\sigma^2 t/2}$（配方法）。这解释了为何 $S_t=S_0e^{\sigma W_t-\sigma^2 t/2}$ 是鞅——指数中的 $-\sigma^2 t/2$ 恰好抵消矩母函数的增长。

---

### 第 4 章 · Stochastic Calculus（随机微积分）

**核心**：**全书技术核心**。Itô 积分 $\int_0^t\Delta_s\,dW_s$ 对「不可导」的 Brown 运动积分，关键是被积函数 $\Delta_s$ 必须适应（可料，左连续）——即只能用截至 $s$ 的信息决定 $\Delta_s$，不能用未来。

Itô 积分本身是鞅（期望为零），这与普通 Lebesgue 积分截然不同。然后是 **Itô 公式**：对 $f(t,W_t)$，

$$df=f_t\,dt+f_x\,dW+\tfrac{1}{2}f_{xx}\,dt,$$

比经典链式法则多出 $\frac{1}{2}f_{xx}\,dt$ 这一项，源于 Brown 的二次变分 $(dW)^2=dt$（在均方意义下）。这一项是整个金融数学的引擎——它使几何 Brown 运动 $S_t=S_0e^{\sigma W_t+(\mu-\frac{\sigma^2}{2})t}$ 的 SDE 化为 $dS=\mu S\,dt+\sigma S\,dW$。

**飞腾锚点**：🟢 **UDOT 16.9× [E05]** —— Itô 积分 $\int_0^t\Delta_s\,dW_s$ 的数值实现是黎曼和 $\sum_k\Delta_{t_k}(W_{t_{k+1}}-W_{t_k})$，本质是点积累加（dot product accumulate）。UDOT 指令的 16.9× 加速直接服务于这类「被积函数 × 增量」的逐项累加，是蒙特卡洛定价路径模拟的底层算子。

**关键定理**：**Itô 公式**（一维）。若 $X_t=X_0+\int\mu_s\,ds+\int\sigma_s\,dW_s$，$f=f(t,X_t)$ 光滑，则

$$df=\left(f_t+\mu f_x+\tfrac{1}{2}\sigma^2 f_{xx}\right)dt+\sigma f_x\,dW.$$

重要性：没有它，无法从 $dW$ 推出任何 SDE 的解。它是随机微积分的「链式法则」。

**自测**：$S_t=S_0e^{\sigma W_t+(\mu-\sigma^2/2)t}$，令 $f(t,x)=S_0e^{\sigma x+(\mu-\sigma^2/2)t}$。用 Itô 公式验证 $dS_t=\mu S_t\,dt+\sigma S_t\,dW_t$。

> 验证：$f_x=\sigma S$，$f_{xx}=\sigma^2 S$，$f_t=(\mu-\sigma^2/2)S$。代入 Itô 公式：$dS=(\mu-\sigma^2/2)S\,dt+\sigma S\,dW+\frac{1}{2}\sigma^2 S\,dt=\mu S\,dt+\sigma S\,dW$。✓

---

### 第 5 章 · Risk-Neutral Pricing（风险中性定价）

**核心**：**金融数学的灵魂章**。**Girsanov 定理**允许在等价测度间切换漂移：$\tilde{W}_t=W_t+\theta t$ 在新测度 $\tilde{P}$ 下是 Brown 运动——漂移被「吸收」进测度变换。

**资产定价基本定理**：市场无套利 $\iff$ 存在等价鞅测度（风险中性测度）$\tilde{P}$ 使贴现资产价格 $e^{-rt}S_t$ 是鞅。在此测度下，期权价格

$$V_0=\tilde{E}[e^{-rT}\cdot\mathrm{payoff}].$$

这把定价化为「在风险中性测度下算贴现期望」。对 $dS=\mu S\,dt+\sigma S\,dW$，Girsanov 把 $\mu$ 换成 $r$，$W$ 换成 $\tilde{W}$——真实漂移 $\mu$ 在定价中消失了，只剩波动率 $\sigma$ 起作用。

**飞腾锚点**：🟡 **matmul 15× [V03]** —— Girsanov 测度变换在多资产情形涉及协方差矩阵 $\Sigma$ 的 Cholesky 分解（生成相关 Brown 运动），远期测度下的多因子定价需批量矩阵运算。matmul 15× 加速服务于「$N$ 条相关路径 × $T$ 步」的蒙特卡洛矩阵化，正如深度学习中批量前向传播。

**关键定理**：**Girsanov 定理 + 资产定价基本定理**。Girsanov：若 $\theta_t$ 适应，令

$$Z_T=\exp\!\left(-\int_0^T\theta_s\,dW_s-\tfrac{1}{2}\int_0^T\theta_s^2\,ds\right),\qquad d\tilde{P}=Z_T\,dP,$$

则 $\tilde{W}_t=W_t+\int_0^t\theta_s\,ds$ 在 $\tilde{P}$ 下是 Brown 运动。基本定理：无套利 $\iff$ $\exists\,\tilde{P}\sim P$ 使贴现价格过程为鞅。

**自测**：$dS=\mu S\,dt+\sigma S\,dW$，$r$ 为无风险利率。

> (a) 风险中性 SDE：取 $\theta=(\mu-r)/\sigma$，则 $\tilde{W}=W+\theta t$，$dS=rS\,dt+\sigma S\,d\tilde{W}$。
>
> (b) 欧式看涨期权：$C=S_0N(d_1)-Ke^{-rT}N(d_2)$，其中 $d_1=\frac{\ln(S_0/K)+rT+\sigma^2 T/2}{\sigma\sqrt{T}}$，$d_2=d_1-\sigma\sqrt{T}$。注意 $S_0N(d_1)$ 来自 $\tilde{E}[S_T\mathbb{1}_{S_T>K}]$（计价单位变换的预演）。

---

### 第 6 章 · Connections with PDEs（与 PDE 的联系）

**核心**：风险中性定价有两条路——蒙特卡洛（算期望）和 PDE（解方程）。**Feynman-Kac 定理**把二者统一：$V(t,x)=E[g(W_T)\mid W_t=x]$ 满足倒向 PDE。

对 Black-Scholes 模型，期权价格 $V(t,S)$ 满足 **Black-Scholes PDE**：

$$V_t+rSV_S+\tfrac{1}{2}\sigma^2 S^2V_{SS}-rV=0,\qquad V(T,S)=(S-K)^+.$$

解此 PDE 得到 Black-Scholes 公式。本章是概率（鞅）与分析（PDE）的交汇点——同一个期权价格，既可以用蒙特卡洛算期望，也可以用有限差分解 PDE，两者等价。

**飞腾锚点**：🟡 **TLB 4.81× [E04]** —— Feynman-Kac 的数值实现是在时空网格 $(t_i,S_j)$ 上离散化 PDE（有限差分法），每个网格点访问邻居需要良好的局部性。TLB 4.81× 的提升来自「相邻网格点共享页表项」，正如 filtration 中「相邻时刻共享信息」——PDE 求解器的缓存友好性与 $\sigma$-代数的层级结构同构。

**关键定理**：**Feynman-Kac 公式**。若

$$V_t+\mu(x)V_x+\tfrac{1}{2}\sigma^2(x)V_{xx}-rV=0,\qquad V(T,x)=g(x),$$

则

$$V(t,x)=E\!\left[e^{-r(T-t)}g(X_T)\mid X_t=x\right],\qquad dX=\mu\,dt+\sigma\,dW.$$

重要性：它证明了「期权价格 = PDE 解 = 风险中性期望」三位一体。

**自测**：对 Black-Scholes PDE $V_t+\frac{1}{2}\sigma^2 S^2 V_{SS}+rSV_S-rV=0$，终值 $V(T,S)=(S-K)^+$。写出 Feynman-Kac 对应的 SDE。

> 答：$dS=rS\,dt+\sigma S\,d\tilde{W}$（风险中性测度下），$V(t,S)=\tilde{E}[e^{-r(T-t)}(S_T-K)^+\mid S_t=S]$。这正是 Ch 5 的 Black-Scholes 公式来源。

---

### 第 7 章 · Exotic Options（奇异期权）

**核心**：标准欧式期权是「到期日 payoff」的函数。奇异期权改 payoff 结构：

- **Barrier 期权**：在标的触碰障碍 $H$ 时生效（knock-in）或失效（knock-out）。
- **Asian 期权**：用路径平均 $\bar{S}=\frac{1}{T}\int_0^T S_t\,dt$ 替代到期价格。
- **Lookback 期权**：用路径极值 $\max_{[0,T]}S_t$ 或 $\min_{[0,T]}S_t$。

**反射原理**利用 $W_t$ 关于零点的对称性算 barrier 触碰概率。Asian 期权因 $\int S_t\,dt$ 的分布非对数正态而无封闭解，需数值方法（PDE 或蒙特卡洛控制变量）。

**飞腾锚点**：🟡 **分支预测 0.71 vs 3.14 [Lab02]** —— barrier 期权定价需在每个时间步判定「是否触碰障碍」$\mathbb{1}[S_t\geq H]$，这是高度可预测的模式化条件分支（路径一旦穿越就 knock-out）。分支预测器在「大多数路径不触碰」的先验下命中率接近预测值，但真实触碰是稀有事件——0.71（命中）vs 3.14（未命中）的代价差异刻画了「触碰判定」的计算开销。

**关键定理**：**反射原理**。对 $a>0$，

$$\Pr\!\left(\max_{0\leq s\leq t}W_s\geq a\right)=2\Pr(W_t\geq a)=2\!\left(1-\Phi\!\left(\frac{a}{\sqrt{t}}\right)\right).$$

重要性：直接给出 up-and-out / down-and-out barrier 期权的封闭定价公式。

**自测**：down-and-out call，障碍 $H<S_0$，strike $K>H$，payoff $=\mathbb{1}[\min_{[0,T]}S_t>H]\cdot(S_T-K)^+$。

> 定性讨论：其价格 $\leq$ 普通欧式看涨（因为多了一个「可能归零」的条件）。当 $H\to 0$ 时退化为普通看涨；当 $H\to K$ 时价格显著下降。用反射原理可写出显式公式。

---

### 第 8 章 · American Derivative Securities（美式衍生品）

**核心**：美式期权可在到期前任意时刻行权，核心是**最优停时问题**：找停时 $\tau^*$ 最大化

$$E[e^{-r\tau}g(S_\tau)].$$

**Snell 包络**是最优值过程：

$$V_t=\sup_{\tau\geq t}E\!\left[e^{-r(\tau-t)}g(S_\tau)\mid\mathcal{F}_t\right].$$

最优停时 $\tau^*$ 是首次 $g(S_t)$ 触及 $V_t$ 的时刻（继续持有与立即行权无差异的边界）。美式看跌有**提前行权溢价**（时间价值 vs 内在价值的权衡）——在深度价内时立即行权拿现金可能优于等待。本章把「优化」嵌入「概率」框架，是随机最优控制的离散化预演。

**飞腾锚点**：🟡 **Iron Law <2% [Lab00]** —— 美式期权定价（二叉树 / Longstaff-Schwartz 蒙特卡洛）需在每个节点比较「立即行权」与「继续持有」的期望值，定价误差来自蒙特卡洛方差与网格离散。Iron Law「性能=指令数×CPI×时钟」的 <2% 误差控制铁律对应「定价误差须收敛到真值」——Longstaff-Schwartz 回归基函数的选取直接影响误差上界。

**关键定理**：**Snell 包络 + 最优停时**。

$$V_t=\mathrm{ess\,sup}_{\tau\geq t}\,E\!\left[e^{-r(\tau-t)}g(S_\tau)\mid\mathcal{F}_t\right],\qquad \tau^*=\inf\{t\geq 0:V_t=g(S_t)\}.$$

重要性：把「何时行权」这个看似优化的问题，严格化为「包络过程的首次触及时刻」。

**自测**：永续美式看跌，$g(S)=(K-S)^+$，$dS=rS\,dt+\sigma S\,dW$（风险中性）。设行权边界 $S^*$（$S<S^*$ 时行权）。

> 写出 $V(S)$ 满足的 ODE：$\frac{1}{2}\sigma^2 S^2 V''+rSV'-rV=0$（$S>S^*$），边界条件 $V(S^*)=K-S^*$，$V'(S^*)=-1$（光滑粘贴），$V(\infty)=0$。解形如 $V=AS^\gamma$，定 $\gamma$ 与 $S^*$。

---

### 第 9 章 · Change of Numéraire（计价单位变换）

**核心**：风险中性测度以银行账户 $e^{rt}$ 为计价单位（numéraire）。但换计价单位可简化定价：以零息债券 $B(t,T)$ 为 numéraire 得到 $T$-**远期测度** $\tilde{P}^T$，在此测度下远期价格 $F(t,T)=S_t/B(t,T)$ 是鞅。这对利率衍生品尤其方便。

**计价单位变换定理**：$\frac{V_t}{N_t^{(1)}}$ 在 $\tilde{P}^{(1)}$ 下是鞅 $\iff$ $\frac{V_t}{N_t^{(2)}}$ 在 $\tilde{P}^{(2)}$ 下是鞅，两测度由

$$\frac{d\tilde{P}^{(2)}}{d\tilde{P}^{(1)}}=\frac{N_T^{(2)}}{N_T^{(1)}}\cdot\frac{N_0^{(1)}}{N_0^{(2)}}$$

联系。本章是 Ch 5 Girsanov 的多资产推广，也是 Ch 10 利率模型的工具基础。

**飞腾锚点**：🟡 **GEMM 9.45 GFLOPS [Lab05]** —— 多 numéraire 切换涉及多个计价单位资产的协方差矩阵，批量定价（$N$ 个期权 × $M$ 个 numéraire）是高维 GEMM 运算。9.45 GFLOPS 的吞吐支撑「远期测度族」的并行计算，正如多资产期权定价需同时维护多个等价鞅测度。

**关键定理**：**计价单位变换定理**。若 $N^{(1)},N^{(2)}$ 为正的资产价格过程，$\tilde{P}^{(i)}$ 使 $V/N^{(i)}$ 为鞅，则

$$\frac{d\tilde{P}^{(2)}}{d\tilde{P}^{(1)}}\bigg|_{\mathcal{F}_T}=\frac{N_T^{(2)}/N_0^{(2)}}{N_T^{(1)}/N_0^{(1)}}.$$

重要性：统一了所有「以某资产为计价」的定价框架，远期测度是特例。

**自测**：零息债 $B(t,T)=e^{-r(T-t)}$（常数利率）。写出以 $B(\cdot,T)$ 为 numéraire 的远期测度 $d\tilde{P}^T/d\tilde{P}$。

> 解：$N_T^{(B)}/N_0^{(B)}=e^{-r(T-T)}/e^{-r(T-0)}=e^{rT}$，银行账户 $N_T^{(\text{bank})}/N_0=e^{rT}$，故 $d\tilde{P}^T/d\tilde{P}=e^{rT}/e^{rT}=1$（常数利率下远期测度=风险中性测度）。利率随机时两者不同——这正是 Ch 10 的动机。

---

### 第 10 章 · Term Structure Models（期限结构模型）

**核心**：利率不是常数而是随期限变化的收益率曲线。本章建利率动态模型：

- **Vasicek 模型**：$dr=a(b-r)\,dt+\sigma\,dW$（均值回归，但可负利率）。
- **CIR 模型**：$dr=a(b-r)\,dt+\sigma\sqrt{r}\,dW$（$\sqrt{r}$ 保证非负）。
- **HJM 框架**：直接对远期利率曲线 $f(t,T)$ 建模，给出无套利条件（波动率结构决定漂移）。

债券价格是利率 SDE 的仿射变换解。本章是 Ch 5 定价理论在利率市场的完整展开——短期利率 $r_t$ 本身是随机过程，贴现因子 $e^{-\int r_s\,ds}$ 也是随机的。

**飞腾锚点**：🟢 **FP16 3.81× [L01]** —— Vasicek/CIR 模拟需对 $dr=a(b-r)\,dt+\sigma\sqrt{r}\,dW$ 做路径积分，CIR 的 $\sqrt{r}$ 在 $r\to 0$ 时数值敏感，FP16 的有限精度可能产生负值导致 $\sqrt{r}$ 失效——这恰好凸显「连续数学模型 + 离散浮点实现」的张力，是数值随机分析的核心议题。

**关键定理**：**Vasicek 债券定价公式**（仿射期限结构）。$dr=a(b-r)\,dt+\sigma\,dW$，则零息债价格

$$B(t,T)=A(t,T)\,e^{-C(t,T)\,r_t},\qquad C(t,T)=\frac{1-e^{-a(T-t)}}{a},$$

其中 $A(t,T)$ 是 $a,b,\sigma,T-t$ 的显式函数。重要性：把无限维的「收益率曲线」压缩为有限参数（$a,b,\sigma$）的封闭解。

**自测**：Vasicek 模型 $dr=a(b-r)\,dt+\sigma\,dW$。用 Itô 公式对 $e^{at}r_t$ 展开算 $E[r_t]$。

> 解：$d(e^{at}r_t)=ae^{at}r_t\,dt+e^{at}\,dr_t=e^{at}[ar_t+a(b-r)]\,dt+e^{at}\sigma\,dW=abe^{at}\,dt+e^{at}\sigma\,dW$。取期望积分：$E[e^{at}r_t]=r_0+ab\int_0^t e^{as}\,ds=r_0+\frac{ab}{a}(e^{at}-1)$。故 $E[r_t]=b+(r_0-b)e^{-at}$（均值回归到 $b$）。

---

### 第 11 章 · Introduction to Jump Processes（跳过程引论）

**核心**：连续模型无法刻画突发跳变（如崩盘、公告冲击）。本章引入 **Poisson 过程** $N_t$（强度 $\lambda$，计数跳跃到达），**补偿 Poisson 过程** $M_t=N_t-\lambda t$ 是鞅。

**跳-扩散模型**：$dS=\mu S\,dt+\sigma S\,dW+S\,dJ$（$dJ$ 为跳项）。Itô 公式推广为 **Itô-Lévy 公式**，多出跳跃求和项——在跳时刻 $s$，$X$ 有不连续跳 $\Delta X_s=X_s-X_{s^-}$，$f$ 的变化不能用微分近似，需用有限差修正。这打开了 Lévy 过程的大门，更贴近真实市场的「肥尾」与跳跃现象。

**飞腾锚点**：🟢 **UDOT 16.9× [E05]** —— Poisson 过程 $N_t=\sum_{k}\mathbb{1}[\tau_k\leq t]$ 是跳时刻的计数累加，跳-扩散路径模拟需在连续扩散（Ch 4 的 Itô 积分累加）之上叠加离散跳求和——两者都是「点积累加」算子。UDOT 16.9× 同时加速扩散项与跳项的累加，是混合过程模拟的统一底层。

**关键定理**：**补偿 Poisson 鞅 + Itô-Lévy 公式**。$M_t=N_t-\lambda t$ 是鞅。对 $X_t=X_0+\int\mu\,ds+\int\sigma\,dW+\int\gamma\,dN$，$f(X_t)$ 的展开为

$$f(X_t)-f(X_0)=\int_0^t f'\,dX^c+\tfrac{1}{2}\int_0^t f''\,d\langle X^c\rangle+\sum_{0<s\leq t}\bigl[f(X_s)-f(X_{s^-})\bigr],$$

其中 $X^c$ 是 $X$ 的连续部分。重要性：它是 Ch 4 Itô 公式的「不连续版」，使带跳模型的定价与对冲成为可能。

**自测**：模型 $dS=\mu S\,dt+\sigma S\,dW-S\,dN$（每次 Poisson 跳使 $S$ 跌至零）。

> 讨论：这描述「破产/违约」场景——一旦跳发生，资产归零。$S_t$ 不可能为负（跳后恒为零），但连续部分可正。$S_t=S_0e^{(\mu-\sigma^2/2)t+\sigma W_t}\cdot\mathbb{1}[N_t=0]$（首次跳前保持几何 Brown 运动，跳后归零）。这是信用违约模型的原型。

---

## §9 全书思想主线

Shreve 卷 II 用一条主线贯穿 11 章：**「概率基础 → Itô 积分 → 风险中性测度」三步统一连续时间金融**。

前两章（Ch 1-2）铺设测度论与条件期望基础——$\sigma$-代数、filtration、条件期望——这是「语言」，Shreve 推进紧凑但配有卷 I 的离散原型。Ch 3-4 是技术飞跃：Brown 运动引入「不可导的连续噪声」，Itô 积分给噪声装上微积分，Itô 公式多出的 $\frac{1}{2}f_{xx}\,dt$ 项是全书引擎。Ch 5 是金融灵魂：Girsanov 定理换测度，资产定价基本定理把「无套利」化为「等价鞅测度存在」，定价坍缩为「求贴现期望」——真实漂移 $\mu$ 消失，只剩波动率 $\sigma$。Ch 6-11 是这条主线的应用展开——PDE 联系、奇异/美式期权、计价单位变换、利率模型、跳过程。

与已读经典的呼应：本书是 **Williams《概率与鞅》** 离散鞅论的连续化升级——Williams 的可选停时在 Ch 8 变为最优停时，Williams 的 Radon-Nikodym 在 Ch 5 变为 Girsanov 换测度；与 **Karatzas-Shreve GTM113** 同源（Shreve 是共同作者），但卷 II 面向金融应用而非纯数学研究，GTM113 的半鞅理论是卷 II Ch 11 的深化版；与 **Shiryaev GTM95** 的测度公理骨架形成「经典概率 → 金融随机分析」的阶梯；与 **Feller 卷一** 的组合直觉形成互补——Feller 给离散手感，Shreve 给连续严格框架。

---

## §10 与本仓库其他笔记的交叉引用

**与仓库已读经典的对话**：

- **↔ Williams《概率与鞅》**：Williams 的离散鞅在 Shreve 卷 II 连续化——Williams Ch 12 的可选停时定理对应 Shreve Ch 8 的最优停时与 Snell 包络；Williams Ch 15 的 Radon-Nikodym 定理对应 Shreve Ch 5 的 Girsanov 测度变换（RN 导数 $Z_T=\exp(\cdots)$ 正是似然比的连续版）。读 Williams Ch 11-15 后再读 Shreve，能看清「离散鞅 → 连续鞅 → Itô 积分」的抽象阶梯。
- **↔ Karatzas-Shreve《随机计算》GTM113**：同源（Shreve 共同作者），GTM113 是纯数学研究级，以半鞅框架为终点；卷 II 面向金融应用，以 Black-Scholes 与利率模型为终点。GTM113 Ch 3 的 Itô 积分构造对应卷 II Ch 4，但卷 II 省略了 GTM113 的大量技术引理。读卷 II 建立「金融为什么需要 Itô 积分」的直觉后，可回 GTM113 补严格性。
- **↔ Shiryaev《概率》GTM95**：Shiryaev 的测度公理与收敛定理是 Shreve Ch 1-2 的理论母体；Shiryaev 的条件期望对应 Shreve Ch 2 的信息流建模。Shreve 是 Shiryaev「经典概率」向「金融随机分析」的应用延伸。
- **↔ Feller《概率论》卷一**：Feller 的组合直觉（随机游走、Arcsine 律）是 Brown 运动（Ch 3）的离散原型；Feller 第 III 章的随机游走在连续极限下变为 Brown 运动，Shreve Ch 3 的反射原理对应 Feller 的对称游走论证。Feller 给手感，Shreve 给框架。

**AI / 工程锚点**：

- 🟢 **Ch 4 Itô 公式 → score-based 扩散模型（Song & Ermon 2019）**：扩散模型的前向 SDE $dx=\sqrt{\beta_t}\,dW$ 与反向 SDE $dx=[-f(x,t)-\beta_t\nabla\log p_t(x)]\,dt+\sqrt{\beta_t}\,dW$ 直接建立在 Itô 积分之上。Shreve Ch 4 的 Itô 公式是理解扩散模型数学合法性的根基。
- 🟢 **Ch 5 风险中性测度 → 量化交易 Black-Scholes 数值实现**：期权做市商每日用 Black-Scholes 公式 $C=S_0N(d_1)-Ke^{-rT}N(d_2)$ 对数千个合约定价，Python/NumPy 向量化实现需对 $d_1,d_2$ 批量计算——这是 matmul 15× 的金融场景。隐含波动率反推（Newton 迭代）是 Ch 5 的工程出口。
- 🟢 **Ch 8 最优停时 → 强化学习连续时间控制**：Snell 包络 $V_t=\sup_\tau E[\cdots]$ 与 RL 的 Bellman 最优性方程 $V(s)=\max_a E[r+\gamma V(s')]$ 同构——美式期权的「最优行权」就是连续时间的「最优策略」。Shreve Ch 8 是 Sutton-Barto 强化学习（仓库已读）的连续时间理论母体。
- 🟢 **Ch 10 利率模型 → 随机优化与 Kalman 滤波**：Vasicek/CIR 的均值回归 SDE $dr=a(b-r)\,dt+\sigma\,dW$ 与 Kalman 滤波的状态空间模型同构，参数估计（$a,b,\sigma$）是随机优化的典型问题——连接了 Shreve 与 Nesterov/Bertsekas（仓库已读）的优化理论。
- 🟡 **Ch 11 跳过程 → 金融时序的肥尾建模**：跳-扩散模型比纯 Brown 运动更贴近真实市场的「黑天鹅」事件，Poisson 跳项对应深度学习中稀有梯度爆炸/消失的现象分析。
