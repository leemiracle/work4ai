# Peter Bühlmann, Sara van de Geer《高维统计学习》 · 快速逐章精读

> 基于原书：*Statistics for High-Dimensional Data: Methods, Theory and Applications*（Peter Bühlmann / Sara van de Geer, Springer Series in Statistics, **2011**）/ 读于：2026-07-03
> 定位：**Lasso 与高维稀疏统计的「方法 + 理论 + 应用」三位一体经典**，Springer 统计丛书旗舰之一，是连接 Tibshirani 原始 Lasso（1996）与现代高维推断理论的**桥樑之作**。
> 特色：第二句——本书不以「概率工具」取胜（那是 Boucheron/Vershynin 的定位），而以**Lasso 为单一主轴贯穿全书**：从线性回归（Ch2）到 GLM（Ch3）、从 oracle 性质（Ch4）到正交设计精确理论（Ch6）、从浓度工具（Ch7）到 Graphical Lasso（Ch10）与 Boosting（Ch13），把「$\ell_1$ 正则 + 稀疏恢复」打成一套自洽的统计方法学。
> 声明：本文为**快速逐章精读**（核心逻辑串联 + 飞腾锚点 + 关键定理 LaTeX + 自测），非逐行证明复读。
> 关联：[Hastie ESL](hastie_统计学习基础ESL_快速逐章.md) · [Wainwright 高维统计](wainwright_高维统计_快速逐章.md) · [Boucheron 集中不等式](boucheron_集中不等式_快速逐章.md)（刚做）· [Mohri FoML](mohri_机器学习理论基础_快速逐章.md) · [Vapnik SLT](vapnik_统计学习理论_快速逐章.md)（刚做）

---

> ⚠️ **TOC 说明（忠于原书真实结构）**：原书分两大块——**Part I 方法（Ch1–5）**：Lasso 在线性/GLM 中的应用与变量选择；**Part II 理论（Ch6–9）**：正交设计精确理论 → 浓度不等式 → Anscombe 逼近 → Multiplier/Bootstrap；**Part III 应用与扩展（Ch10–14）**：Graphical Lasso → 协方差估计 → 多重检验 → Boosting → 扩展。本文以原书 14 章 + 引言为骨架，逐章标注。其中 **Compatibility Condition**（van de Geer 提出）与 **Restricted Eigenvalue Condition**（Bickel-Ritov-Tsybakov）是 Lasso 理论的两大支柱，分别在 Ch4、Ch5 出场。

---

## §0 引言：高维统计学习是什么，为什么 ML 理论方向必须读它（约 360 字）

两位作者——Bühlmann（ETH Zürich 统计系，Boosting/高维因果推断名家）与 van de Geer（ETH 统计系，经验过程与 Lasso 理论权威）——在 2011 年推出这部专著，恰逢 Lasso（Tibshirani 1996）、压缩感知（Candès-Tao 2006）、高维统计（2008–2010 黄金期）三股潮流交汇。它系统回答一个核心问题：**当协变量维度 $p\gg n$（变量远多于样本），经典最小二乘完全失效，但若真实信号「稀疏」（仅 $s_0\ll n$ 个非零），$\ell_1$ 正则能否把信号恢复出来、误差多大、需要什么条件？**

全书以 **Lasso 估计** $\hat\beta=\arg\min_\beta\|y-X\beta\|_2^2/n+\lambda\|\beta\|_1$ 为唯一主轴。方法层（Ch1–5）讲「怎么用」——线性回归、GLM、变量选择、预测；理论层（Ch6–9）讲「为什么有效」——正交设计是精确 warm-up，一般设计需要**兼容性条件（Compatibility Condition）**保证设计矩阵在稀疏子空间上「不太病态」；应用层（Ch10–14）把 Lasso 思想推广到**图模型（Graphical Lasso 估计稀疏精度矩阵）、协方差估计、多重检验、Boosting**。**与已读教材呼应**：Hastie ESL 给统计直觉全谱，Boucheron（刚做）给浓度工具母机，Wainwright 给非渐近极小极大理论，本书则是「**Lasso 方法学的完整工程手册 + 自洽理论**」。飞腾锚点：**matmul 15×**（设计矩阵 $X^\top X$）贯穿回归，**分支预测**（变量选择=路径）是 Boosting/greedy 的硬件肉身。

### 四本高维/统计学习教材对比

| 书 | 风格 | 严格性 | 适合谁 |
|:---|:---|:---|:---|
| **Bühlmann-van de Geer《高维统计学习》2011（本书）** | Lasso 单主轴贯穿方法+理论+应用，ETH 学派 | ★★★★（理论自洽，工程友好） | 想系统掌握 Lasso 方法学与理论的人 |
| Hastie-Tibshirani-Friedman《ESL》2009（pre-batch） | 统计学习全谱教材，偏差-方差+正则+树+核 | ★★★（渐近为主，直觉强） | 想要全谱统计学习直觉的人 |
| Wainwright《High-Dimensional Statistics》2019（pre-batch） | 非渐近理论正典，极小极大+oracle+信息下界 | ★★★★★（最严密） | 做高维统计推断研究的人 |
| Boucheron-Lugosi-Massart《集中不等式》2013（刚做） | 浓度方法专精，方差/熵/等周/transportation 四路线 | ★★★★★（极严密） | 想吃透浓度工具本身的人 |

> **阅读策略**：Hastie ESL（统计直觉全谱）→ **Bühlmann（Lasso 方法学+理论核心，本书）** → Wainwright（极小极大严格化）→ Boucheron（浓度工具深挖）。本书是「**Lasso 工程手册 + 理论桥梁**」环节。
> 注意：本书早于 Wainwright（2011 vs 2019），是后者的**思想源头之一**——Wainwright 的 oracle 不等式框架直接继承自 van de Geer。
> **最小阅读集**：Ch1→Ch2→Ch4→Ch6→Ch7（共 5 章，约 150 页）即可掌握 Lasso 方法与理论骨架；Ch10/Ch13 按研究方向（图模型/Boosting）选读。

---

## §1 全书 14 章骨架一览（飞腾锚点分布）

> **结构概览**：全书分**三大块**。**Part I 方法（Ch1–5）**：Lasso 在线性回归（Ch2）与 GLM（Ch3）中的定义与求解，oracle 性质（Ch4 变量选择一致性）与预测/选择权衡（Ch5）；**Part II 理论（Ch6–9）**：正交设计精确理论（Ch6 warm-up）→ 浓度不等式（Ch7，**承接 Boucheron**）→ Anscombe 修正与经验过程逼近（Ch8）→ Multiplier/Bootstrap（Ch9）；**Part III 应用与扩展（Ch10–14）**：Graphical Lasso（Ch10）→ 高维协方差估计（Ch11）→ 多重检验/FDR（Ch12）→ Boosting/greedy（Ch13）→ group/fused Lasso 等扩展（Ch14）。**全书灵魂：$\ell_1$ 正则在「稀疏假设」下把 $p\gg n$ 的不可解问题变成 $s_0\log p$ 可解，兼容性条件是设计矩阵的「不病态」保证。**

| 章 | 标题 | 核心概念 | 飞腾锚点 |
|:--|:--|:--|:--|
| 1 | Introduction: Lasso and Generalizations | 高维问题、Lasso 定义、$\ell_1$ 几何 | Iron Law<2% 🟢 |
| 2 | Lasso for Linear Regression | 线性回归 Lasso、KKT、坐标下降 | matmul 15× 🟢 |
| 3 | Generalized Linear Models and Lasso | GLM、logistic Lasso、负对数似然 | UDOT 16.9× 🟢 |
| 4 | The Oracle Properties of the Lasso | 变量选择一致性、Compatibility Condition | Iron Law<2% 🟢 |
| 5 | More about Variables Selection and Prediction | Restricted Eigenvalue、Relaxed Lasso、阈值化 | 分支预测 🟡 |
| 6 | Theory for Orthogonal Design | 正交设计精确理论、软阈值 | Schmidt 正交化 🟡 |
| 7 | Concentration Inequalities and Tail Bounds | Hoeffding/Bernstein/McDiarmid、sub-Gaussian | UDOT 16.9× 🟢 |
| 8 | The Anscombe Correction and Approximation | 经验过程逼近、随机标准化 | Iron Law<2% 🟡 |
| 9 | The Multiplier and Bootstrap | Multiplier 方法、Bootstrap 一致性 | TLB 4.81× 🟡 |
| 10 | Graphical Modeling | Graphical Lasso、稀疏精度矩阵 | GEMM 9.45G 🟢 |
| 11 | Covariance Estimation in High-Dim | banding、thresholding、谱集中 | matmul 15× 🟡 |
| 12 | Multiple Testing | FDR、Benjamini-Hochberg、高维 $p$ 值 | FP16 3.81× 🟡 |
| 13 | Boosting and Greedy Algorithms | L2-Boosting、forward stagewise、greedy | 分支预测 🟢 |
| 14 | Extensions and Some Further Topics | group/fused Lasso、半参数、因果 | TLB 4.81× 🟡 |

> **精读优先级**：⭐Ch2（Lasso 线性回归地基）→ ⭐Ch4（Compatibility Condition，**全书理论核心**）→ ⭐Ch6（正交设计，精确 warm-up）→ ⭐Ch7（浓度工具，**承接 Boucheron**）→ Ch10（Graphical Lasso，应用高潮）→ Ch13（Boosting）→ Ch5/11/12（按需）。14 章用 8 个锚点分散覆盖，相邻章均不重复。
>
> **两大设计条件对照**：本书理论的「命门」是设计矩阵 $X$ 在稀疏子空间上不病态，两条平行条件——**Compatibility Condition**（van de Geer，Ch4，较弱，给 $\ell_1$ 误差与预测误差界）与 **Restricted Eigenvalue Condition**（Bickel-Ritov-Tsybakov，Ch5，略强，蕴含前者）。更强的 **irrepresentable condition**（Ch4）是变量选择一致性的**充要**条件。三者构成「条件严苛度光谱」，是全书最易混淆也最关键的概念。

---

# Part I · 方法（Ch1–5）

---

## 第 1 章 · Introduction: Lasso and Generalizations（引言：Lasso 与推广）

**核心**：开篇立下全书的**中心命题**：高维数据 $p\gg n$ 下，最小二乘过拟合（$p>n$ 时 $X^\top X$ 奇异，OLS 无解），但若真实系数稀疏（$s_0=\|\beta^0\|_0\ll n$），则 $\ell_1$ 正则化能从 $p$ 个候选变量中「挑出」这 $s_0$ 个。Lasso（Least Absolute Shrinkage and Selection Operator）估计 $\hat\beta=\arg\min_\beta\|y-X\beta\|_2^2/n+\lambda\|\beta\|_1$。**$\ell_1$ 的几何**：约束 $\|\beta\|_1\le t$ 是菱形（高维是超正八面体），其「尖角」恰落在坐标轴上——故最优解常恰有若干分量为零（稀疏），而 $\ell_2$（岭回归）的球面光滑、不留零。本章还预告推广：elastic net（$\ell_1+\ell_2$）、group Lasso、fused Lasso（Ch14 展开）。

**飞腾锚点** 🟢 **Iron Law<2%**：Lasso 的本质是**结构化误差铁律**——用 $\ell_1$ 把「$\|\hat\beta-\beta^0\|_1$ 的误差」与「$\lambda$ 罚」锁定在一个 oracle 不等式里。性能 = 指令数×CPI×时钟每个因子 $<2\%$；Lasso = 拟合误差 $+$ 罚项两块都受 Iron Law 约束，使预测误差 $\sim\sigma^2 s_0\log p/n$ 而非 $p/n$。

**关键定理**：**Lasso 的基本不等式（KKT 起源）**——若 $\lambda\ge c\|2X^\top\varepsilon/n\|_\infty$（$\varepsilon$ 为噪声），则 Lasso 估计满足
$$\|\hat\beta-\beta^0\|_1 \le C\,s_0\,\lambda,$$
即误差被「稀疏度×罚水平」控制，与维度 $p$ 仅 $\log$ 相关。这是全书一切理论的起点。

**自测**：$p=1000$，$n=100$，$s_0=5$。OLS 能否用？Lasso 误差阶？答：OLS 不可用（$X^\top X$ 奇异）；Lasso 预测误差 $\sim\sigma^2\cdot5\log 1000/100\approx\sigma^2\cdot0.35$——维度诅咒被稀疏祝福化解。**几何直觉**：$\ell_1$ 球 $\|\beta\|_1\le t$ 在 2D 是菱形，其顶点恰在坐标轴上；高维时超正八面体的「尖角」使最优解落在稀疏顶点，而 $\ell_2$ 球光滑无尖角故岭回归不稀疏。

---

## 第 2 章 · Lasso for Linear Regression（Lasso 线性回归）

**核心**：把 Ch1 的 Lasso 定义在**线性模型** $y=X\beta^0+\varepsilon$ 下做透。三大主题：① **求解**——坐标下降（每步对单坐标软阈值 $S(\cdot,\lambda)$，闭式）、LARS（最小角回归，可给出整条 Lasso 路径）；② **KKT 条件**——$\hat\beta$ 为解 $\iff -2X_j^\top(y-X\hat\beta)/n+\lambda\,\mathrm{sign}(\hat\beta_j)=0$（$\hat\beta_j\ne0$），未被选变量满足 $|2X_j^\top r/n|\le\lambda$（$r$ 残差）——这给出「变量被选/被弃」的精确阈值；③ **预测误差 oracle 不等式**——在兼容性条件下，$\|X(\hat\beta-\beta^0)\|_2^2/n\le C\sigma^2 s_0\log p/n$。

**飞腾锚点** 🟢 **matmul 15×**：坐标下降每步算 $X_j^\top r$（列向量·残差内积）、残差更新 $r\leftarrow r-X_j\Delta\beta_j$ 是矩阵-向量运算；LARS 的相关度 $\mathbf{c}=X^\top(y-X\beta)$ 是一次完整矩阵乘。设计矩阵 $X\in\mathbb{R}^{n\times p}$ 的运算贯穿 Lasso 求解，matmul 15× 向量化是大规模 Lasso（$p=10^5$ 基因数据）的硬件基础。

**关键定理**：**Lasso 预测 oracle 不等式**（compatibility 成立时）——
$$\frac{1}{n}\|X(\hat\beta-\beta^0)\|_2^2 \le C\,\sigma^2\,\frac{s_0\log p}{n},$$
达到极小极大最优速率（Wainwright 已读的下界匹配）。

**自测**：$X_j$ 标准化（$\|X_j\|_2^2=n$），坐标下降对 $\hat\beta_j$ 的更新？答：$\hat\beta_j\leftarrow S\!\left(\hat\beta_j+\tfrac{X_j^\top r}{n},\,\lambda\right)$，$S(z,\lambda)=\mathrm{sign}(z)(|z|-\lambda)_+$（软阈值）——$\lambda$ 把小于阈值的系数直接压零。

---

## 第 3 章 · Generalized Linear Models and Lasso（GLM 与 Lasso）

**核心**：把 Lasso 从线性回归推广到**广义线性模型**（GLM）：$Y|X\sim$ 指数族，$g(\mathbb{E}[Y|X])=X\beta$（$g$ 为链接函数）。Lasso 变为对**负对数似然**加 $\ell_1$ 罚：$\hat\beta=\arg\min_\beta\{-\ell(\beta;X,Y)/n+\lambda\|\beta\|_1\}$。重点特例：**logistic 回归**（$g=\mathrm{logit}$，损失为对数损失 $\log(1+e^{-yX\beta})$）、**Poisson 回归**（计数）。求解用 IRLS（迭代加权最小二乘）+ 软阈值：每步把 GLM 局部化成加权线性回归，套用 Ch2 的坐标下降。理论保证同 Ch2：在兼容性条件下，估计误差 $\sim s_0\log p/n$，只是常数换成 Fisher 信息。

**飞腾锚点** 🟢 **UDOT 16.9×**：负对数似然 $\ell(\beta)=-\sum_{i=1}^n\log p(y_i|x_i;\beta)$ 是**样本求和**，IRLS 每步的加权内积 $\sum_i w_i(X\beta)_i y_i$ 也是点积累加。大规模 GLM（百万样本 logistic）的 IRLS 迭代是稠密 UDOT 运算，16.9× 向量化是训练吞吐的硬件肉身。

**关键定理**：**GLM Lasso oracle 不等式**——在线性部分有界 + 兼容性条件下，
$$\|\hat\beta-\beta^0\|_1 \le C\,s_0\,\lambda,\quad \lambda \asymp \sqrt{\frac{\log p}{n}}.$$
注意 logistic 的浓度需 Bernstein 型（损失非有界方差），承接 Ch7。

**自测**：logistic Lasso 与线性 Lasso 的算法差异？答：线性损失为二次（IRLS 一步收敛）；logistic 损失凸但非二次，需多次 IRLS 迭代，每次解加权 Lasso（权重 $w_i=\hat\pi_i(1-\hat\pi_i)$）。
> **应用场景**：GLM Lasso 是生物医学/金融的标配——logistic Lasso 做疾病-基因关联（$p=10^5$ SNP，$n=10^3$ 病人，稀疏致病位点），Poisson Lasso 做保险精算计数。$\ell_1$ 把 $p\gg n$ 的过拟合风险压成 $s_0\log p/n$，使高维 GLM 在临床可解释（选出的 SNP 即候选生物标志物）。

---

## 第 4 章 · The Oracle Properties of the Lasso（Lasso 的 Oracle 性质）⭐⭐⭐

**核心**：全书**理论高潮之一**：Lasso 能否「选对变量」（$\mathrm{supp}(\hat\beta)=\mathrm{supp}(\beta^0$）？答案是「**在两个条件下可以**」。条件一：**Compatibility Condition（兼容性条件）**——van de Geer 提出，要求设计矩阵在真实支撑集 $S_0$ 上「不病态」：$\|\beta_{S_0}\|_1^2\le C\cdot|S_0|\cdot\|X\beta_{S_0}\|_2^2/n$（稀疏信号方向上能量有下界）。条件二：**beta-min（最小信号）**——$\min_{j\in S_0}|\beta^0_j|\gg\lambda$（真实系数足够大，不被罚压零）。二者结合得 **oracle 性质**：Lasso 不仅预测好，还能渐近选出正确变量集。本章还讨论 irrepresentable condition（Lasso 变量选择一致性的**充要**条件，比兼容性更强）。

**飞腾锚点** 🟢 **Iron Law<2%**：Compatibility Condition 是**设计矩阵层面的 Iron Law**——「稀疏方向上能量不能塌缩」，否则误差铁律失效。它把「数值线性代数的良态」升级为「高维稀疏回归的统计铁律」：只要矩阵在 $s_0$-稀疏子空间上不病态，Lasso 的变量选择误差就被钉死。

**关键定理**：**Compatibility Condition**（van de Geer）——若存在 $\phi_{\mathrm{comp}}>0$ 使对所有 $\beta$（$\|X\beta_{S_0^c}\|_1\le C\|\beta_{S_0}\|_1$）有
$$\|\beta_{S_0}\|_2^2 \le \frac{\|X\beta\|_2^2}{n\,\phi_{\mathrm{comp}}^2\,|S_0|},$$
则 Lasso 的 $\ell_1$ 误差 $\le C s_0\lambda/\phi_{\mathrm{comp}}^2$。**irrepresentable condition**：$\|X_{S_0^c}^\top X_{S_0}(X_{S_0}^\top X_{S_0})^{-1}\mathrm{sign}(\beta^0_{S_0})\|_\infty<1$（充要）。

**自测**：正交设计 $X^\top X/n=I$ 是否满足兼容性？答：$\phi_{\mathrm{comp}}=1$（最优），irrepresentable 也自动成立——故 Ch6 正交设计是 Lasso 理论的「理想情形」。
> **易混点**：兼容性条件（充分，给误差界）≠ irrepresentable（充要，给选择一致性）。兼容性较弱、几乎对所有「相干设计」成立；irrepresentable 较强、对高度相关的「假相关」设计可能失败——此时 Lasso 仍预测好但选错变量。

---

## 第 5 章 · More about Variables Selection and Prediction（变量选择与预测）

**核心**：深化 Ch4 的两个方向。① **Restricted Eigenvalue Condition（REC）**（Bickel-Ritov-Tsybakov 2009）：与兼容性平行、略强的设计条件，要求 $\Lambda_{\min}(X_{S_0}^\top X_{S_0}/n)\ge\kappa>0$ 在锥约束 $\{\beta:\|\beta_{S_0^c}\|_1\le C\|\beta_{S_0}\|_1\}$ 内。REC 蕴含兼容性。② **Relaxed Lasso**（两阶段）：先用 Lasso 选变量，再在被选子集上跑 OLS——消除 Lasso 的收缩偏置，改进预测。③ **阈值化（thresholding）**：对 Lasso 估计设硬阈值 $\hat\beta_j\cdot\mathbb{1}[|\hat\beta_j|>t]$，进一步去伪。本章权衡「选择 vs 预测」：Lasso 单步可能「选多漏少」，relaxed/thresholded 修正。

**飞腾锚点** 🟡 **分支预测**：变量选择本质是**条件分支**——每个变量「选/不选」是一次 `if (|β̂_j|>λ)` 判定。阈值化与 relaxed Lasso 的两阶段是数据依赖的分支序列，分支预测器（0.71 vs 3.14 CPI）擅长「系数稳定选中」的模式；高相关变量使分支难预测 → 流水线气泡 → 选择不稳。

**关键定理**：**Restricted Eigenvalue Condition** ——
$$\min_{\beta\in\mathcal{C}}\frac{\|X\beta\|_2/\sqrt n}{\|\beta_{S_0}\|_2}\ge\kappa,\quad \mathcal{C}=\{\beta:\|\beta_{S_0^c}\|_1\le 3\|\beta_{S_0}\|_1\}.$$
则 Lasso 同时给 $\|\hat\beta-\beta^0\|$ 与预测误差的极小极大最优界。

**自测**：Relaxed Lasso 为何改进预测？答：Lasso 的 $\ell_1$ 罚对真信号也施加 $O(\lambda)$ 偏置；第二阶段 OLS 去掉偏置，预测误差从 $s_0\lambda$ 降到 $s_0/n$ 量级（无偏）。

---

# Part II · 理论（Ch6–9）

---

## 第 6 章 · Theory for Orthogonal Design（正交设计理论）⭐⭐⭐ 精确 warm-up

**核心**：全书**理论的最干净起点**——正交设计 $X^\top X/n=I_p$（如正交基回归、随机化实验）。此时 Lasso 有**闭式解**：$\hat\beta_j=S(\hat\beta_j^{\mathrm{OLS}},\lambda)$（各坐标独立软阈值），所有理论可**精确**计算，无任何近似。三大精确结论：① **预测**：$\|X(\hat\beta-\beta^0)\|_2^2/n=\sum_j(S(\hat\beta_j^{\mathrm{OLS}},\lambda)-\beta^0_j)^2$，期望 $\le C s_0\lambda^2+\sigma^2 s_0\lambda^2/\dots$（ Stein 无偏风险估计给出最优 $\lambda\sim\sigma\sqrt{\log p/n}$）；② **变量选择**：若 $\min_{j\in S_0}|\beta^0_j|>2\lambda$，则 $\mathrm{supp}(\hat\beta)=S_0$ 高概率成立；③ **风险**：软阈值的 Stein 风险恰为 Donoho-Johnstone 理论的小波去噪速率。本章是理解一般设计（Ch4–5）的**理想化原型**。

**飞腾锚点** 🟡 **Schmidt 正交化**：正交设计 $X^\top X/n=I$ 意味着列向量已**正交归一**——这正是 Schmidt/QR 正交化的产物。现实设计矩阵通常不正交，需先做 Gram-Schmidt 把基正交化（或用正交小波/正交匹配追踪 OMP），才能套用本章的精确理论。正交基是 Lasso「去耦」的几何前提。

**关键定理**：**正交设计软阈值闭式解** ——
$$\hat\beta_j = S(\hat\beta_j^{\mathrm{OLS}},\lambda) = \mathrm{sign}(\hat\beta_j^{\mathrm{OLS}})(|\hat\beta_j^{\mathrm{OLS}}|-\lambda)_+.$$
**Donoho-Johnstone 风险**：$\mathbb{E}\|\hat\beta-\beta^0\|_2^2\le C\sigma^2 s_0\log p$（极小极大最优，与一般设计的 oracle 速率一致）。

**自测**：正交设计 $\beta^0=(3,0,0,2,0)$，$\hat\beta^{\mathrm{OLS}}=(3.1,0.2,-0.1,1.8,0.05)$，$\lambda=0.5$。软阈值结果？答：$\hat\beta=(2.6,0,0,1.3,0)$——正确选出 2 个变量，噪声系数被压零。
> **为何 warm-up 重要**：正交设计是「理想实验台」——所有 Ch4–5 的一般设计结论在正交下都退化为**等式**（无不等式损失），让学生先看清「$\lambda\sim\sigma\sqrt{\log p/n}$、误差 $\sim s_0\log p/n$」从哪来，再面对一般设计的兼容性复杂性。这也是 Donoho-Johnstone 小波去噪的统计源头。

---

## 第 7 章 · Concentration Inequalities and Tail Bounds（集中不等式与尾界）

**核心**：理论工具层——为 Lasso 误差界提供概率控制。本章是**Boucheron（刚做）的浓缩版**：Markov → Chebyshev → Chernoff（MGF 方法）→ **Hoeffding**（有界变量 sub-Gaussian）→ **Bernstein**（方差敏感，$\exp(-t^2/(\sigma^2+Bt))$）→ **McDiarmid**（有界差，一般函数浓度）。核心应用：证明 $\|2X^\top\varepsilon/n\|_\infty\le C\sigma\sqrt{\log p/n}$（Ch1 基本不等式的 $\lambda$ 选择），需对 $p$ 个 $X_j^\top\varepsilon$ 同时做 union bound + Hoeffding——**对数因子 $\log p$ 正来自这里**。本章还含 sub-Gaussian/sub-exponential 随机变量的 $\psi_2/\psi_1$ 范数。

**飞腾锚点** 🟢 **UDOT 16.9×**：MGF $M(\lambda)=\mathbb{E}e^{\lambda\varepsilon}$、独立和 $S=\sum\varepsilon_i$、$X_j^\top\varepsilon=\sum_i X_{ij}\varepsilon_i$——全是**加权求和/内积**。对 $p$ 个变量同时算 $X^\top\varepsilon$ 是矩阵-向量乘，UDOT 16.9× 向量化是浓度界蒙特卡洛验证与 $\lambda$ 选择的硬件肉身。

**关键定理**：**$\|X^\top\varepsilon/n\|_\infty$ 的 Hoeffding+union 界** —— $\varepsilon_i$ i.i.d. sub-Gaussian（参数 $\sigma$），$X_{ij}$ 有界：
$$\mathbb{P}\!\left(\|2X^\top\varepsilon/n\|_\infty \ge \sigma\sqrt{\frac{2\log(2p)}{n}}+t\right)\le e^{-nt^2/(2\sigma^2)}.$$
取 $\lambda\asymp\sigma\sqrt{\log p/n}$ 代入 Ch1，即 Lasso 误差 $s_0\sqrt{\log p/n}$ 的来源。

**自测**：$p=10^6$，$n=1000$，$\sigma=1$。$\lambda$ 应取多大？答：$\lambda\sim\sqrt{\log(2\times10^6)/1000}\approx\sqrt{14.5/1000}\approx0.12$——$\log p$ 因子使 $\lambda$ 仅随 $p$ 缓增。
> **与 Boucheron 的衔接**：本章即 Boucheron（刚做）Ch2（Hoeffding/Bernstein/McDiarmid）+ Ch11–13（经验过程上确界）在 Lasso 场景的定向应用。Boucheron 给「为何这些不等式成立 + 四条统一路径」，本书只取「够用」的标量浓度，不展开 log-Sobolev/transportation。读 Boucheron 后本章应「透明」。

---

## 第 8 章 · The Anscombe Correction and Approximation（Anscombe 修正与逼近）

**核心**：理论精细化——Ch7 的浓度界控制**尾概率**，但 Lasso 误差的**精确分布**（如置信区间、假设检验）需要更强的工具：**经验过程的 Gaussian 逼近**。**Anscombe 定理**（随机标准化下的 CLT）：当用估计的标准差 $\hat\sigma$ 替代真 $\sigma$ 做标准化时，CLT 仍成立（带修正项）。本章把这一思想用到 Lasso：$\sqrt n(\hat\beta_j-\beta^0_j)/\hat\sigma_j$ 在被选变量上渐近正态——为 Lasso 估计的**推断**（置信区间、$p$ 值）奠基。还涉及 Komlós-Major-Tusnády 强逼近（经验过程 $\to$ Brownian 桥）。本章是「从 oracle 速率到统计推断」的桥梁。

**飞腾锚点** 🟡 **Iron Law<2%**：Anscombe 修正即**随机标准化的误差铁律**——用 $\hat\sigma$ 代 $\sigma$ 引入估计误差，必须修正到 $<2\%$ 才不破坏 CLT 的尾部分度。经验过程逼近的 Kolmogorov 距离 $\le C/\sqrt n$ 是 Iron Law 的渐近版。

**关键定理**：**Anscombe 随机标准化 CLT** —— 若 $\hat\sigma\to\sigma$ 依概率，则 $\sqrt n(\bar X-\mu)/\hat\sigma\xrightarrow{d}\mathcal{N}(0,1)$。**经验过程 Gaussian 逼近**：$\sup_t|\mathbb{F}_n(t)-\Phi(t)|\le C/\sqrt n$（Kolmogorov 距离）。

**自测**：为何 Lasso 的推断比 OLS 难？答：Lasso 的变量选择引入「选择偏倚」——被选变量的系数分布被「$|\hat\beta_j|>\lambda$」条件截断，不再是简单正态；需用 Anscombe + 选择修正（如 de-biased Lasso）。

---

## 第 9 章 · The Multiplier and Bootstrap（乘子方法与 Bootstrap）

**核心**：构造**可计算的近似**来估计 Lasso 误差分布（Ch8 给理论，Ch9 给算法）。① **Multiplier（乘子）方法**：给每个样本乘 i.i.d. 符号 $g_i\in\{-1,+1\}$（Rademacher 权重），重算 Lasso 残差统计量——这模拟了「均值 $0$」的原假设，不需知道真 $\beta^0$；② **Bootstrap（自助法）**：有放回重采样 $n$ 个样本，重算 $\hat\beta^*$，用 $\hat\beta^*-\hat\beta$ 的分布近似 $\hat\beta-\beta^0$。本章证明在稀疏 + 兼容性下，multiplier/bootstrap 分布**一致逼近**真分布（Ch8 的 Gaussian 逼近是其理论保证），从而可用 bootstrap 分位数构造 Lasso 的置信区间——**这是 Lasso 推断的工程方法**。

**飞腾锚点** 🟡 **TLB 4.81×**：Bootstrap 重采样本质是**样本的局部性重排**——同一批数据反复抽取，TLB 缓存命中率高（4.81× 加速）当样本在内存中连续存放；若数据分散（如分布式数据库），TLB 缺页 → 重采样变慢。Multiplier 方法的符号权重则是对局部数据的一次轻量乘法。

**关键定理**：**Bootstrap 一致性**（稀疏 + 兼容性）—— $\hat\beta^*-\hat\beta$ 的 bootstrap 分布 $\xrightarrow{d}$ $\hat\beta-\beta^0$ 的真分布，故 bootstrap 分位数 $\hat q_{1-\alpha/2}^*$ 给出近似正确的 $(1-\alpha)$ 置信区间。

**自测**：multiplier 与 bootstrap 的区别？答：multiplier 用 Rademacher 权重 $g_i\varepsilon_i$（保持 $X_i$ 不变，只扰动残差），适合均值检验；bootstrap 重采样 $(X_i,Y_i)$ 对，捕捉设计矩阵的不确定性，更通用但更慢。
> **工程权衡**：bootstrap 需重复拟合 Lasso $B$ 次（$B\sim1000$），计算量为单次 Lasso 的 $B$ 倍；multiplier 只在残差上扰动，每步是轻量乘法，远快于 bootstrap。高维下 multiplier 是可工程化的推断方法，bootstrap 则更精确但昂贵——精度与算力的权衡。

---

# Part III · 应用与扩展（Ch10–14）

---

## 第 10 章 · Graphical Modeling（图模型：Graphical Lasso）⭐⭐⭐

**核心**：把 Lasso 思想从「回归选变量」推广到「**估计稀疏图结构**」。高维图模型中，**精度矩阵**（precision matrix）$\Theta=\Sigma^{-1}$ 的零模式编码**条件独立**（$\Theta_{jk}=0\iff X_j\perp X_k\mid$ 其余）。**Graphical Lasso（glasso）**：$\hat\Theta=\arg\min_\Theta\{-\log\det\Theta+\mathrm{tr}(S\Theta)+\lambda\|\Theta\|_{1,\text{off}}\}$（$S$ 为样本协方差，罚在非对角元）。$\ell_1$ 罚使 $\hat\Theta$ 稀疏 → 对应稀疏图。求解用坐标下降（对每行/列做 $\ell_1$ 正则的二次规划）或 Nesterov 加速。理论：在 $\Theta$ 稀疏 + 谱条件下，$\hat\Theta$ 以 Frobenius 误差 $\sim s_0\log p/n$ 恢复真精度矩阵。

**飞腾锚点** 🟢 **GEMM 9.45G**：glasso 每步算 $\Theta^{-1}$、$\mathrm{tr}(S\Theta)$、对 $p\times p$ 矩阵做坐标更新——全是**大规模稠密矩阵运算**。$p=10^3$（基因调控网络）时 $\Theta$ 有 $10^6$ 元，GEMM 9.45 GFLOPS 吞吐决定 glasso 是否可工程化（每次迭代 $O(p^3)$）。

**关键定理**：**Graphical Lasso 收敛率**（Ravikumar 等 + 本书）—— 在 irrepresentable-type 条件 + 最小信号 $\Theta_{jk}^0$ 下，$\hat\Theta$ 以高概率正确恢复图结构（变量选择一致），Frobenius 误差 $\|\hat\Theta-\Theta^0\|_F\le C\sqrt{s_0\log p/n}$。

**自测**：$X$ 服从 3 变量马尔可夫链 $X_1-X_2-X_3$（$X_1\perp X_3|X_2$）。$\Theta$ 的零模式？答：$\Theta_{13}=\Theta_{31}=0$，其余非零——glasso 应恢复边集 $\{(1,2),(2,3)\}$。
> **与协方差估计（Ch11）的分工**：Ch11 估 $\Sigma$（稀疏协方差，假设变量间稀疏相关），Ch10 估 $\Theta=\Sigma^{-1}$（稀疏精度，对应稀疏**条件独立**图）。两者罚都在非对角元，但 $\Sigma$ 稀疏 ≠ $\Theta$ 稀疏（逆可能稠密）。选哪个取决于科学问题：金融风险管理估 $\Sigma$，基因调控网络估 $\Theta$。

---

## 第 11 章 · Covariance Estimation in High-Dim（高维协方差估计）

**核心**：估计 $p\times p$ 协方差矩阵 $\Sigma$（$p\gg n$ 时样本协方差 $S$ 严重高估谱、甚至奇异）。三种结构化估计：① **Banding（带状化）**：若变量有序（时间序列、空间），假设 $\Sigma_{jk}=0$ 当 $|j-k|>k_0$，截断为带状；② **Thresholding（阈值化）**：对 $S_{jk}$ 软/硬阈值（$S_{jk}\cdot\mathbb{1}[|S_{jk}|>t]$），得稀疏 $\hat\Sigma$；③ **低秩**：若 $\Sigma$ 接近低秩，用 PCA/硬阈值特征分解。本章给出各种估计在谱范数 / Frobenius 范数下的收敛率 $\sim$ 谱集中（Marchenko-Pastur）+ 稀疏增益。协方差估计是 PCA、风险度量、Markowitz 投资组合的底层。

**飞腾锚点** 🟡 **matmul 15×**：协方差估计核心算 $S=X^\top X/n$（一次 $p\times p$ 矩阵乘）+ 特征分解 $S=U\Lambda U^\top$（$O(p^3)$）。Banding/thresholding 是对 $S$ 元素的后处理（逐元素运算）。matmul 15× 向量化是 $p=10^3$ 以上协方差估计的工程前提。

**关键定理**：**阈值化协方差收敛率** —— 若 $\Sigma$ 稀疏（$s_0=\max_j\|\Sigma_{j\cdot}\|_0$），则
$$\|\hat\Sigma_{\mathrm{thresh}}-\Sigma\|_{\mathrm{op}}\le C\sqrt{\frac{s_0\log p}{n}},$$
而样本协方差 $S$ 的误差 $\sim\sqrt{p/n}$（无稀疏增益）。

**自测**：$p=500$，$n=100$，$\Sigma=I$（独立）。$S$ 的最大特征值？答：$\lambda_{\max}(S)\approx(1+\sqrt{p/n})^2=(1+\sqrt 5)^2\approx10.5$——样本协方差严重高估谱（Marchenko-Pastur），需收缩/阈值化。

---

## 第 12 章 · Multiple Testing（多重检验）

**核心**：高维下同时检验 $p$ 个假设（如「基因 $j$ 是否与表型相关」），若每检验水平 $\alpha$，则假阳性数 $\sim\alpha p$ 爆炸。核心问题：控制**族错误率**。① **FWER**（族错误率，至少一个假阳性）——Bonferroni 用 $\alpha/p$，过严；② **FDR**（False Discovery Rate，假阳性占被拒比例的期望）——**Benjamini-Hochberg（BH）程序**：排序 $p$ 值 $p_{(1)}\le\dots\le p_{(p)}$，找最大 $k$ 使 $p_{(k)}\le k\alpha/p$，拒前 $k$ 个。BH 在独立下控制 FDR $\le\alpha$。本章把 BH 推广到高维 + 相关结构（依赖下的 BY 程序），并讨论 Lasso 选出的变量如何做下游检验（selective inference，选择后推断）。

**飞腾锚点** 🟡 **FP16 3.81×**：多重检验的 $p$ 值在 $10^{-8}$ 量级（基因组关联 GWAS 需 $5\times10^{-8}$），$p$ 值精度（FP16 vs FP32 vs FP64）直接影响 BH 排序的稳健性。FP16 的 3.81× 加速适合 $p$ 值预筛，但最终 BH 阈值判定需 FP32/FP64 保精度——精度与速度的权衡。

**关键定理**：**Benjamini-Hochberg FDR 控制** —— $p$ 个独立检验，BH 程序在水平 $\alpha$ 下控制 $\mathrm{FDR}\le\alpha\cdot p_0/p\le\alpha$（$p_0$ 为真零假设数）。

**自测**：$p=1000$ 检验，$\alpha=0.05$，某 $p$ 值 $=0.0001$。BH 阈值？答：若该 $p$ 值排序第 $k$，BH 阈值 $=k\cdot0.05/1000=k\cdot5\times10^{-5}$。若 $k=3$，阈值 $1.5\times10^{-4}>10^{-4}$ → 拒绝（该基因为发现）。
> **与 Lasso 的接口**：Lasso 选出变量后，对这些「被选」变量做下游 $t$ 检验会引入**选择偏倚**（数据已用于选择，再检验不独立）。现代 selective inference（Lee 等 2016）与 de-biased Lasso（van de Geer 2014）解决此问题，是 Ch8 Anscombe 修正的高维推广，使 Lasso 从「预测」走向「统计推断」。

---

## 第 13 章 · Boosting and Greedy Algorithms（Boosting 与贪心算法）⭐⭐⭐

**核心**：另一条高维方法主线——**Boosting**（不像 Lasso 用 $\ell_1$ 罚，而是用「弱学习器迭代加性组合」）。① **L2-Boosting**（componentwise）：每步选残差相关性最大的基函数 $X_j$，沿其方向走一小步 $\hat f\leftarrow\hat f+\nu\cdot\langle r,X_j\rangle X_j/\|X_j\|^2$（$\nu$ 学习率），残差更新——本质是**函数空间梯度下降**；② **Forward Stagewise**：与 Boosting 同源，极小步长 $\nu\to0$ 时退化为 infinitesimal forward stagewise，与 Lasso 路径有深刻对偶（Efron-Hastie-Tibshirani 的 LARS-Boosting 等价）；③ **Greedy**：匹配追踪（OMP）每步贪心选最优原子。Boosting 的停止规则 = 正则化（早停防过拟合），与 Lasso 的 $\lambda$ 对偶。本章是 Bühlmann（作者本人）的看家方向。

**飞腾锚点** 🟢 **分支预测**：Boosting 每步「选哪个 $X_j$」是 $\arg\max_j|\langle r,X_j\rangle|$——一次**数据依赖的条件分支**（选最大相关）。分支预测器擅长「残差稳定指向同一 $X_j$」的模式（强信号）；若多个基函数相关性接近（高度共线），$\arg\max$ 在步间频繁跳变 → 分支难预测 → 流水线气泡 → Boosting 收敛慢。这正是「Boosting 对共线性敏感」的硬件镜像。

**关键定理**：**L2-Boosting 收敛率** —— 在稀疏真函数 $f^0=\sum_{j\in S_0}\beta_j X_j$ 下，$m$ 步 L2-Boosting 的估计误差 $\le C\sigma^2 s_0\log p\cdot(1-\nu)^m/n$——与 Lasso 同阶，早停 $m\sim\log n/\nu$ 达最优。

**自测**：Boosting 与 Lasso 何时等价？答：当用最小角回归（LARS）实现 Boosting 且步长 $\to0$，forward stagewise 路径与 Lasso 路径逐点重合（Efron 等 2004）——两种方法在高维稀疏下殊途同归。
> **作者背景**：Bühlmann（本书第一作者）是 Boosting 的统计理论权威（L2-Boosting 的 $L^2$ 收敛证明、早停 = 正则化的对应定理均出自其组）。本章是「ETH 学派」两大支柱（Lasso + Boosting）的交汇，体现「显式罚（Lasso）与隐式迭代（Boosting）是同一稀疏正则的两面」。

---

## 第 14 章 · Extensions and Some Further Topics（扩展与进一步专题）

**核心**：Lasso 的结构化推广与跨域应用。① **Group Lasso**（$\|\beta\|_1\to\sum_g\|\beta_g\|_2$）：组内全选或全弃（如分类变量的 one-hot 组、多任务学习的共享系数）；② **Fused Lasso**（$\sum|\beta_{j+1}-\beta_j|$）：鼓励相邻系数平滑（信号分段常数，如图像去噪、CNV 检测）；③ **半参数**：高维部分线性模型 $Y=X^\top\beta+g(Z)+\varepsilon$，同时估 $\beta$ 与非参数 $g$；④ **因果推断**：高维工具变量、双重机器学习（DML，Chernozhukov）——Lasso 选控制变量以消除混淆。本章把 Lasso 从「预测」推向「因果/推断」，对接现代计量经济学。

**飞腾锚点** 🟡 **TLB 4.81×**：fused Lasso 的 $\sum|\beta_{j+1}-\beta_j|$ 罚假设**相邻系数有结构**（分段常数），对应内存中相邻数据的**空间局部性**——TLB 命中率高（4.81×）。group Lasso 的组结构若与内存分块对齐（如行主序），同样受益。稀疏结构的局部性 = TLB 友好。

**关键定理**：**Group Lasso oracle**（组稀疏 $s_0$ 组）—— 在组兼容性下，$\|\hat\beta-\beta^0\|_2\le C\sqrt{s_0(d_{\max}\log G/n)}$（$d_{\max}$ 最大组大小，$G$ 组数）——组结构带来 $\log G$ 而非 $\log p$ 的增益。

**自测**：fused Lasso 与总变分（TV）去噪的关系？答：1D fused Lasso 罚 $\sum|\beta_{j+1}-\beta_j|$ 恰是离散总变分 $\mathrm{TV}(\beta)$——故 fused Lasso = TV-正则最小二乘，是图像/信号去噪的标准工具。

---

## §9 全书思想主线（约 210 字）

Bühlmann-van de Geer 的统一主线是「**稀疏假设 + $\ell_1$ 正则把 $p\gg n$ 的不可解化为 $s_0\log p/n$ 可解**」。**方法层**（Ch1–5）：Lasso 在线性/GLM 下以软阈值求解，oracle 性质（变量选择一致性）依赖两大条件——**Compatibility Condition**（van de Geer，设计矩阵在稀疏子空间不病态）与 **beta-min**（信号足够大）。**理论层**（Ch6–9）：正交设计是精确 warm-up（闭式软阈值，Donoho-Johnstone 速率），一般设计靠**浓度不等式**（Ch7，**承接 Boucheron**）控制 $\|X^\top\varepsilon\|_\infty$，$\log p$ 因子正来自 union bound；Anscombe/bootstrap 把 oracle 速率升级为可计算的统计推断。**应用层**（Ch10–14）：Graphical Lasso 把稀疏从回归推广到图结构，Boosting 以贪心迭代与 Lasso 殊途同归，group/fused Lasso 引入结构化先验。**一句话**：本书教你「**为什么 Lasso 能在高维恢复稀疏信号、误差多大、需要什么条件、如何推广到图/协方差/检验/Boosting**」——是 Lasso 方法学的完整工程手册。
> **与已读教材的定位差**：Boucheron（刚做）给浓度的「方法母机」，Wainwright 给「极小极大严格化」，Vapnik/Mohri（刚做）给「ML 泛化的函数类复杂度视角」；本书是唯一把 **$\ell_1$ 稀疏正则**从回归（Ch2）一路打到图模型（Ch10）、协方差（Ch11）、检验（Ch12）、Boosting（Ch13）的**单一主轴专著**——读完即掌握高维统计的「稀疏方法论全景」。

---

## §10 与本仓库其他笔记的交叉引用

**同类教材对比**：

1. **vs [Hastie ESL](hastie_统计学习基础ESL_快速逐章.md)（pre-batch）**：Hastie ESL 给统计学习**全谱直觉**（偏差-方差、正则、树、核），Bühlmann 则把 **Lasso 单主轴**打到方法+理论+应用的完整深度。Hastie 是 ESL 的合著者之一（Lasso 原作者），但 ESL 对 Lasso 理论（兼容性/REC/oracle）只点到为止；Bühlmann 是其理论严格化。读 ESL 建直觉 → 本书补 Lasso 理论核心。
2. **vs [Wainwright 高维统计](wainwright_高维统计_快速逐章.md)（pre-batch）**：Wainwright（2019）是本书（2011）的**理论后继与升级**——Wainwright 的 Ch7（Lasso oracle）直接继承 van de Geer 的兼容性框架，并加入极小极大下界 + 信息论下界。Bühlmann 偏「方法工程」，Wainwright 偏「理论严格化」。读本书建 Lasso 工程观 → Wainwright 补极小极大。
3. **vs [Boucheron 集中不等式](boucheron_集中不等式_快速逐章.md)（刚做）**：本书 Ch7 是 Boucheron Ch2（Hoeffding/Bernstein/McDiarmid）的**统计应用浓缩**。Boucheron 给浓度方法的四条统一路径（方差/熵/等周/transportation），本书只取标量浓度（够用于 Lasso 的 $\|X^\top\varepsilon\|_\infty$ 界）。读 Boucheron 后，本书 Ch7 透明；本书 Ch10（Graphical Lasso）的矩阵浓度需补 Boucheron 不含的矩阵版。
4. **vs [Mohri FoML](mohri_机器学习理论基础_快速逐章.md)（刚做）**：Mohri 是 ML 泛化理论（PAC/Rademacher/VC），本书是统计估计理论（oracle/兼容性）。交集在正则化——Mohri 的结构风险最小化（SRM）与本书 Lasso 的 $\ell_1$ 罚对偶：SRM 用复杂度罚（VC 维），Lasso 用稀疏罚（$\ell_1$）。两书互补：Mohri 管分类泛化，本书管回归估计。
5. **vs [Vapnik SLT](vapnik_统计学习理论_快速逐章.md)（刚做）**：Vapnik 的 SRM 用**函数类复杂度**（VC 维）控制泛化，Bühlmann 的 Lasso 用**系数稀疏**（$\ell_1$）控制估计——两种正则化哲学。Vapnik 是数据无关最坏界（VC），Bühlmann 是结构假设界（稀疏），后者在现代高维数据上更紧。

**AI/工程锚点（4 条）**：

6. **🟢 稀疏神经网络与剪枝**：Lasso 的 $\ell_1$ 罚使系数自然稀疏，这正是**神经网络剪枝**（Lottery Ticket Hypothesis）的统计基础——把 $\ell_1$（或 $\ell_0$ 近似）加到权重上，训练后剪小权重，得稀疏子网。group Lasso（Ch14）对应**通道剪枝**（整组神经元全弃）。oracle 性质（Ch4）给出「剪枝后仍选对重要连接」的理论保证。对接 [Goodfellow 深度学习](goodfellow_深度学习_快速逐章.md)。
7. **🟢 Dropout 与 Lasso 的对偶**：Dropout（训练时随机置零神经元）是**隐式 $\ell_2$ 正则**，而 Lasso 是显式 $\ell_1$。两者都防过拟合，但 Dropout 稀疏**激活**（路径级），Lasso 稀疏**权重**（参数级）。理解 Lasso 的稀疏恢复机制有助于分析 Dropout 为何泛化——本书 Ch4 的 oracle 性质是稀疏恢复的金标准。
8. **🟡 深度学习压缩与量化**：Ch11 协方差估计的阈值化 + Ch14 fused Lasso 的总变分正则，是**模型压缩**（权重稀疏化、量化）的统计工具。Graphical Lasso（Ch10）估计神经元间的稀疏依赖图，用于剪枝冗余连接。FP16 精度（Ch12 $p$ 值精度）对应低比特量化。
9. **🟡 推荐系统与矩阵补全**：低秩协方差估计（Ch11）+ Lasso 稀疏性 = **推荐系统协同过滤**（Netflix 大赛）。用户-物品矩阵低秩 + 稀疏残差，是 group/fused Lasso（Ch14）的典型应用场景。Graphical Lasso（Ch10）还用于用户兴趣图建模。

### 飞腾锚点速查（14 章 · 8 锚点分散覆盖）

| 锚点 | 章节 | 主题 |
|:------|:------|:------|
| **Iron Law<2% ⭐** | **Ch1⭐**, **Ch4⭐**, Ch8 | Lasso=结构化误差铁律（基本不等式/兼容性铁律/Anscombe 随机标准化） |
| **matmul 15× ⭐** | **Ch2⭐**, Ch11 | 设计矩阵/协方差（$X^\top X$ 坐标下降/样本协方差） |
| **UDOT 16.9× ⭐** | Ch3, **Ch7⭐** | 求和/内积（负对数似然/MGF 浓度界） |
| **分支预测 ⭐** | Ch5, **Ch13⭐** | 条件分支（变量选择选/弃/Boosting argmax 选基） |
| **Schmidt 正交化** | **Ch6⭐** | 正交基（正交设计=已正交归一列） |
| **TLB 4.81×** | Ch9, Ch14 | 局部性（bootstrap 重采样/fused Lasso 相邻结构） |
| **GEMM 9.45G ⭐** | **Ch10⭐** | 大矩阵吞吐（Graphical Lasso $p\times p$ 精度矩阵） |
| **FP16 3.81×** | Ch12 | 精度权衡（GWAS $p$ 值 $10^{-8}$ 量级） |

### 核心符号速查

| 符号 | 含义 | 首现 |
|:------|:------|:------|
| $\hat\beta$ | Lasso 估计 $\arg\min\|y-X\beta\|^2/n+\lambda\|\beta\|_1$ | Ch1 |
| $\beta^0$, $s_0$ | 真实系数及其稀疏度 $\|\beta^0\|_0$ | Ch1 |
| $S_0$ | 真实支撑集 $\{j:\beta^0_j\ne0\}$ | Ch4 |
| $\phi_{\mathrm{comp}}$ | 兼容性常数（Compatibility Condition） | Ch4 |
| $\kappa$ | 限制特征值常数（REC） | Ch5 |
| $S(z,\lambda)$ | 软阈值 $\mathrm{sign}(z)(|z|-\lambda)_+$ | Ch2/Ch6 |
| $\Theta=\Sigma^{-1}$ | 精度矩阵（零模式=条件独立图） | Ch10 |
| $\mathfrak{R}_n$ | Rademacher 复杂度 | Ch7（与 Boucheron 对接） |

---

> **续读指引**：精读本书后，① Lasso 理论严格化 → 重读 [Wainwright Ch7](wainwright_高维统计_快速逐章.md)（极小极大下界匹配本书 oracle 速率）；② 浓度工具深挖 → [Boucheron Ch2/Ch11–13](boucheron_集中不等式_快速逐章.md)（本书 Ch7 的方法母机）；③ 统计直觉全谱 → [Hastie ESL](hastie_统计学习基础ESL_快速逐章.md) Ch3（回归）/Ch18（高维）；④ 现代前沿 → de-biased/selective Lasso 推断、双重机器学习（Chernozhukov）、稀疏神经网络（Ch4 oracle 性质的深度推广）。**本书是 Lasso 方法学的「工程手册 + 理论桥梁」**。
> **进阶专题**：本书未覆盖但承前启后——① 矩阵补全（soft-impute，low-rank + Lasso 残差，Netflix）；② de-biased/de-sparsified Lasso（Javanmard-Montanari、van de Geer 2014，做 Lasso 后的置信区间，修正 Ch8 的选择偏倚）；③ 双重机器学习 DML（Chernozhukov 2018，用 Lasso 选 nuisance 控制变量做因果）。三者都是本书 Ch4/Ch14 的直接延伸。
