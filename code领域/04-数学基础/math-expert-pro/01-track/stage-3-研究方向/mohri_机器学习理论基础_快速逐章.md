# Mehryar Mohri, Afshin Rostamizadeh, Ameet Talwalkar《机器学习理论基础》 · 快速逐章精读

> 基于原书：*Foundations of Machine Learning*（Mehryar Mohri / Afshin Rostamizadeh / Ameet Talwalkar, MIT Press, **2nd Edition, 2018**）/ 读于：2026-07-03
> 定位：**学习理论「算法导向 + 严格证明」的研究生教材**，以 **PAC + Rademacher 双轴**统一监督学习全景。
> 特色：第二句——本书把**数据相关的 Rademacher 复杂度**抬到全书主轴（而非只用粗糙的 VC 维），并用它贯穿 SVM / Boosting / 多类 / 排序 / 回归 / 最大熵 / 稳定性，是 Shalev-Shwartz《理解 ML》之后的**算法深化读物**。
> 声明：本文为**快速逐章精读**（核心逻辑串联 + 飞腾锚点 + 关键定理 LaTeX + 自测），非逐行证明复读。
> 关联：[Shalev-Shwartz 理解 ML](shalev_shwartz_理解机器学习_快速逐章.md) · [Hastie ESL](hastie_统计学习基础ESL_快速逐章.md) · [Bishop PRML](bishop_PRML_模式识别与机器学习_快速逐章.md) · [Murphy MLPP](murphy_机器学习概率视角_快速逐章.md) · [Cover-Thomas 信息论](cover_thomas_信息论_快速逐章.md)

---

## §0 引言：Mohri 的「PAC + Rademacher」双轴现代学习理论

Mehryar Mohri（NYU Courant 教授 + Google Research 顾问）这本 *Foundations of Machine Learning* 是学习理论领域**算法导向的严格教科书**。
它与已读的 Shalev-Shwartz《理解 ML》同样以 PAC 为骨架，但 Mohri 的独特之处在于**把 Rademacher 复杂度抬到全书主轴**——
不再只依赖 VC 维这一个粗糙、数据无关的尺度，而用**数据相关**的 Rademacher 复杂度给出更紧、更现代的泛化界，
并用它统一贯穿全部监督学习专题。Mohri 本人是**加权有限状态转换器（WFST）与序列核**的创立者，
故第 6 章 Kernel Methods（含序列核）与第 16 章 Learning Automata 带有别书没有的深度——这是语音识别、NLP 的工程理论根基。

对比视角：**Shalev-Shwartz** 是「PAC 严格化入门」，定义→定理→证明最清爽，31 章铺得最宽；
**Hastie ESL** 是「频率派统计学习」，偏差-方差为诊断、算法谱最全但证明偏几何直觉；
**Bishop PRML** 是「贝叶斯机器学习」，先验后验边缘化；
**Vapnik** 是「SLT 原始创立者」，SRM + 大间隔的直觉源头。
Mohri 恰好卡在「**严格性近 Shalev-Shwartz、算法谱近 ESL、现代工具（Rademacher / 在线学习 / 最大熵 / Fenchel 对偶）最全**」的位置。

对当前路径的意义：**已读 Shalev-Shwartz 建立了 PAC 直觉（VC 维、一致收敛、NFL），本书负责把它锻造成可下到算法的、带紧界的研究级框架**——
学完本书，应能「给定任意一个新算法，自己用 Rademacher/PAC 配出泛化保证」。
飞腾锚点把抽象泛化界钉到工程肉身：**Iron Law <2%**（误差控制）对应泛化 slack 的带宽半径；
**UDOT 16.9×**（求和/期望）对应经验风险与 Rademacher 平均的计算核心；
**matmul 15× / GEMM 9.45G**（矩阵乘法）对应线性分类器、核矩阵、值迭代的高维热点；
**FP16 3.81×** 对应 softmax / 平方损失的数值稳定性。本书定理多为 🟢（事实锚点），因为 PAC/Rademacher 界可严格验证。

### 四本 ML 理论教材对比

| 书 | 风格 | 严格性 | 适合谁 |
|:---|:---|:---|:---|
| **Mohri《Foundations of ML》2ed 2018（本书）** | 算法导向 + Rademacher 主轴 + 简洁证明 | ★★★★（证明完整、偏算法） | 研究生 / 想从 PAC 进到算法与紧界的人 |
| Shalev-Shwartz《理解 ML》2014 | PAC 严格化入门，定义→定理→证明最清爽 | ★★★★（最易懂的严格） | 本科高年级 / PAC 零基础入门 |
| Hastie《ESL》2009 | 频率派统计，几何直觉 + 偏差-方差诊断 | ★★★（证明偏直觉） | 统计直觉强、要全谱算法的人 |
| Bishop《PRML》2006 | 贝叶斯，先验后验 + 概率推断 | ★★★（推导完整、偏概率） | 贝叶斯 ML 全图 |

> **阅读策略**：Shalev-Shwartz（PAC 入门） → **Mohri（算法深化 + 紧界）** → Anthony-Bartlett（神经网理论纵深） → Vapnik（原始视角溯源）。本书是这条链的「**严格算法**」环节。

---

## §1 全书 17 章骨架一览

> **⚠️ TOC 勘误（以原书 2ed 真实为准）**：(1) 全书实为 **17 章**而非 14 章——第 1 版(2012)是 14 章，
> **2ed 新增 3 章**：Model Selection(Ch4)、Maximum Entropy Models(Ch12)、Conditional Maxent(Ch13)；
> 另 2ed 的 **Part II 高级部分**含 Ch15 Dimensionality Reduction / Ch16 Learning Automata and Languages / Ch17 Reinforcement Learning。
> (2) Ch2 原题为「The PAC Learning **Framework**」（任务清单误作 "Model"）。
> (3) Ch12 原题「Maximum Entropy **Models**」（非 "Exponential Family"，后者在章内讨论）；Ch13「Conditional Maximum Entropy Models」（logistic regression 是其核心实例，非章题）。
> (4) 附录 A–E：线性代数 / 凸优化 / 概率 / **集中不等式(2ed 扩充)** / **信息论(2ed 全新 Ch E)**。

**两大部分结构**：全书分 **Part I 基础（Ch1–14）** 与 **Part II 高级专题（Ch15–17）**。
Part I 的前 4 章（PAC → Rademacher/VC → 模型选择）奠定理论地基，Ch5–14 是「把地基下放到各监督学习算法」；
Part II 把 PAC 框架拓展到降维、序列、强化三大非标准场景。**全书的灵魂是：每章都用 Rademacher 或其变体给出泛化保证。**

| 章 | 标题 | 核心概念 | 飞腾锚点 |
|:--|:--|:--|:--|
| 1 | Introduction | 学习任务/阶段/泛化问题 | Iron Law<2% 🟡 |
| 2 | The PAC Learning Framework | PAC 可学、样本复杂度 | UDOT 16.9× 🟢 |
| 3 | Rademacher Complexity & VC-Dimension | 数据相关复杂度、VC 界 | Iron Law<2% 🟢 |
| 4 | Model Selection | ERM/SRM、估计-近似误差 | TLB 4.81× 🟡 |
| 5 | Support Vector Machines | 间隔最大化、QP、软间隔 | matmul 15× 🟢 |
| 6 | Kernel Methods | PSD 核、表示定理、序列核 | GEMM 9.45G 🟢 |
| 7 | Boosting | AdaBoost、弱→强、坐标下降 | 分支预测 🟢 |
| 8 | On-Line Learning | regret、加权多数、Hedge | UDOT 16.9× 🟡 |
| 9 | Multi-Class Classification | 一对多、ECOC、多类 SVM | 分支预测 🟡 |
| 10 | Ranking | 成对排序、RankBoost、泛化界 | matmul 15× 🟡 |
| 11 | Regression | 实值 Rademacher、最小二乘 | FP16 3.81× 🟡 |
| 12 | Maximum Entropy Models | 最大熵原理、指数族、对偶 | Schmidt 正交化 🟡 |
| 13 | Conditional Maximum Entropy Models | 逻辑回归、条件最大熵、MLE | FP16 3.81× 🟡 |
| 14 | Algorithmic Stability | 稳定性⇒泛化、强凸 | Iron Law<2% 🟢 |
| 15 | Dimensionality Reduction | PCA、KPCA、JL 引理 | Schmidt 正交化 🟢 |
| 16 | Learning Automata & Languages | DFA 推断、序列学习 | 分支预测 🟡 |
| 17 | Reinforcement Learning | MDP、Bellman、PAC-MDP | GEMM 9.45G 🟡 |

> **精读优先级**：⭐Ch2–3（理论地基，必精读）→ ⭐Ch5–7（SVM/核/Boosting 三大算法，必精读）→ Ch8/14（在线/稳定性，重点）→ Ch11–13（回归/最大熵/logistic）→ Ch9–10/15–17（按需）。8 锚点分配到 17 章，相邻章均不重复，🟢=事实可验证锚点（定理级），🟡=工程直觉锚点（类比级）。

---

## 第 1 章 Introduction

**核心**：定义「什么是机器学习」、标准任务（分类/回归/排序/聚类）、学习阶段（训练/验证/测试）、学习场景（监督/无监督/在线/强化）。
本章不证定理，只立框架：所有后续泛化分析都指向一个核心问题——**经验风险 $\widehat R_S(h)$ 与真实风险 $R(h)$ 何时接近**。
这把「学习」从模糊的「让机器变聪明」精确化为「从样本推出一个风险可控的假设」。

**飞腾锚点 🟡 Iron Law <2%**：泛化问题的「铁律」即经验误差与真实误差之差必须落入可控带宽——
这正是 Iron Law「误差 <2%」的数学化身，泛化界给出这个带宽的半径。本章是把这个工程直觉上升为数学命题的起点。

**关键定理**：泛化框架定义——真实风险 $R(h)=\mathbb E_{(x,y)\sim\mathcal D}[\ell(h(x),y)]$，经验风险 $\widehat R_S(h)=\frac1m\sum_{i=1}^m\ell(h(x_i),y_i)$；
目标是 $\Pr_{S\sim\mathcal D^m}[\,R(h_S)-\widehat R_S(h_S)\le\epsilon\,]\ge1-\delta$。

**自测**：设 $\widehat R_S(h)=0.05$ 但测试得 $R(h)=0.20$，差 0.15 是否「违反泛化」？答：不能直接判，需看是否超出 PAC 置信带宽（取决于 $m,\mathcal H,\delta$）。

## 第 2 章 The PAC Learning Framework

**核心**：PAC（Probably Approximately Correct）是全书地基——「大概率近似正确」。两条主线：①**一致情形**（存在零误差假设）样本复杂度仅 $\log|\mathcal H|$ 级；
②**不一致情形**用 Hoeffding 不等式给出经验-真实偏差的置信带。PAC 把「可学（learnable）」从哲学概念变成可计算的函数 $m(\epsilon,\delta)$——
这是 Shalev-Shwartz 前 8 章的同款地基，本书复习并加紧界。

**飞腾锚点 🟢 UDOT 16.9×**：样本复杂度本质是「对 $m$ 个样本求和以估计期望」——
经验风险即求和，UDOT 向量化求和 16.9× 加速直接决定大样本下 ERM 的工程可行性，是 PAC 界「能否在合理时间内跑出来」的硬件下界。

**关键定理**：一致情形，$m\ge\frac1\epsilon(\ln|\mathcal H|+\ln\frac1\delta)$ 即可 PAC；不一致情形，以概率 $\ge1-\delta$：

$$R(h)\le\widehat R_S(h)+\sqrt{\frac{\ln(2|\mathcal H|/\delta)}{2m}}\qquad(\text{有限假设类 }\mathcal H)$$

**自测**：有限类 $|\mathcal H|=1000$，$m=1000$，$\delta=0.05$，一致情形最小 $\epsilon$？解：$\epsilon_{\min}=\frac{\ln1000+\ln20}{1000}=\frac{6.9+3.0}{1000}\approx0.01$。

## 第 3 章 Rademacher Complexity and VC-Dimension

**核心**：本章是全书的「复杂度中枢」。VC 维是**数据无关**的粗糙尺度；
Rademacher 复杂度 $\mathfrak R_m(\mathcal H)$ 衡量「假设类拟合随机噪声 $\sigma_i$ 的能力」，**数据相关**、界更紧。
逻辑链：growth function $\Pi_{\mathcal H}(m)$ → Sauer-Shelah 引理 → VC 维 $d$ → Rademacher 平均，四者层层递进，给出从最松到最紧的泛化保证。
理解这章就拿到了本书所有后续章节的「万能钥匙」。

**飞腾锚点 🟢 Iron Law <2%**：Rademacher 界直接给出「经验-真实误差带宽」的紧版本，
是泛化 Iron Law 的研究级精确化——把「误差控制在 2%」从口号变成可计算的 slack。

**关键定理**：以概率 $\ge1-\delta$：

$$R(h)\le\widehat R_S(h)+2\widehat{\mathfrak R}_S(\mathcal H)+3\sqrt{\frac{\ln(2/\delta)}{2m}};\quad\text{Sauer-Shelah: }\Pi_{\mathcal H}(m)\le\Big(\frac{em}{d}\Big)^d,\;d=\mathrm{VCdim}$$

**自测**：实测 $\widehat{\mathfrak R}_S(\mathcal H)=0.05$，$m=1000$，$\delta=0.05$，求 Rademacher 泛化 slack。解：$2\times0.05+3\sqrt{\ln(40)/(2000)}=0.10+3\times0.043\approx0.23$。

## 第 4 章 Model Selection

**核心**：不同假设类 $\mathcal H$ 对应不同的「估计误差（estimation error）vs 近似误差（approximation error）」权衡——
类越大近似误差越小但估计误差越大。**ERM**（固定类内最小化经验风险）可能欠拟合；
**SRM**（结构风险最小化）用嵌套类族 $\mathcal H_1\subset\mathcal H_2\subset\cdots$ 加复杂度罚项，自动选「恰好够用」的类。
交叉验证（CV）是工程上最常用的模型选择实现。本章是 2ed 新增，补上了原版缺失的关键一环。

**飞腾锚点 🟡 TLB 4.81×**：SRM 的嵌套结构与 CV 的多次扫描（$k$ 折、留一），强依赖内存局部性——
TLB 命中率（4.81× 差）决定多模型训练的实际吞吐，这是 CV「理论上好但工程贵」的硬件根源。

**关键定理**：SRM 对嵌套类族，选 $\mathcal H_k$ 使 $\widehat R_S(h)+\text{penalty}(k)$ 最小，penalty 由 VC/Rademacher 复杂度给出；
CV 的留一/折数偏差有界（如 LOO 对稳定算法近无偏）。

**自测**：三类 $|\mathcal H_1|=10,|\mathcal H_2|=100,|\mathcal H_3|=1000$，$m=500,\delta=0.05$，经验风险 $0.10/0.06/0.04$，SRM 选哪个？
解：算各 slack $\sqrt{\ln(2|\mathcal H|/\delta)/(2m)}\approx0.12/0.14/0.15$，加罚后总风险 $\approx0.22/0.20/0.19$，选 $\mathcal H_3$（边际递减，工程常折中选 $\mathcal H_2$）。

## 第 5 章 Support Vector Machines

**核心**：SVM 把「最大间隔」变成凸二次规划（QP）。硬间隔 $\Rightarrow$ 严格可分；软间隔引入松弛 $\xi_i$ 处理不可分。
核心洞见：**泛化误差只依赖间隔 $\rho$ 与数据半径 $r$ 之比 $(r/\rho)^2$，而非输入维度**——
这就是「维数灾难被间隔化解」的数学根源，也是 SVM 在高维小样本上优于 logistic 回归的理论原因。对偶形式（KKT）引出第 6 章的核方法。

**飞腾锚点 🟢 matmul 15×**：SVM 训练即大规模 QP，内层是 $\mathbf w\cdot\mathbf x$ 的矩阵乘法（对偶形式则是核矩阵乘法），
matmul 向量化 15× 加速是工业 liblinear/libsvm 的性能支柱——离开向量化，百万级样本的 SVM 根本不可训。

**关键定理**：硬间隔 QP $\;\min_{w,b}\tfrac12\|w\|^2\;$ s.t. $y_i(w\cdot x_i+b)\ge1$；间隔 $\rho=1/\|w\|$。间隔泛化界：

$$R(h)\le\widetilde O\!\Big(\frac{r^2/\rho^2}{m}\Big)\quad(\text{仅依赖间隔比，与维度无关})$$

**自测**：$\mathbb R^{100}$ 中数据半径 $r=1$，SVM 学得 $\|w\|=2$，间隔 $\rho=0.5$，$m=500$，估 slack 量级。解：$(r/\rho)^2/m=4/500=0.008$，对数因子后约 $0.02$ 量级。

## 第 6 章 Kernel Methods

**核心**：核技巧 $K(x,x')=\Phi(x)\cdot\Phi(x')$ 把线性算法隐式提升到高维（甚至无穷维）特征空间而不显式计算 $\Phi$。
**Mercer 定理**保证正半定（PSD）核对应某再生核 Hilbert 空间（RKHS）；**表示定理**保证正则化经验风险的解可表为 $w=\sum_i\alpha_i\Phi(x_i)$，
使「无穷维优化」退化为「$m$ 维系数求解」。Mohri 独门的序列核（加权转换器构造）是本章特色，对接语音/NLP。

**飞腾锚点 🟢 GEMM 9.45G**：核方法的核心开销是 $m\times m$ 核矩阵 $K$ 的构建与缓存，高维 GEMM 是瓶颈——
这也是 Nyström 近似、随机傅里叶特征（§6.6）存在的工程理由：当 $K$ 装不进内存时必须近似。

**关键定理**：PSD 核 $\Leftrightarrow$ RKHS 内积；表示定理 $\;w=\sum_{i=1}^m\alpha_i\Phi(x_i)$；核 SVM 对偶：

$$\max_\alpha\sum\alpha_i-\tfrac12\sum\alpha_i\alpha_jy_iy_jK(x_i,x_j),\quad\text{s.t. }\sum\alpha_iy_i=0,\;0\le\alpha_i\le C$$

**自测**：RBF 核 $K(x,x')=\exp(-\gamma\|x-x'\|^2)$，$\gamma\to\infty$ 时 RKHS 维度如何变化？对应 VC 维？答：$\gamma$ 越大，$\Phi$ 映射到越高维、拟合越强、VC 维越高、过拟合风险升（极端时退化为查表）。

## 第 7 章 Boosting

**核心**：Boosting 回答「弱可学 ⇔ 强可学」等价性——若存在略好于随机（错误率 $<1/2-\gamma$）的弱分类器，就可组合成任意强的强分类器。
**AdaBoost** 通过重加权错分样本、迭代选弱分类器、线性加权组合，使训练误差指数下降。
本章揭示 AdaBoost = 对指数损失的**前向阶段加性建模（坐标下降）**，且自带间隔最大化效应（这解释了为何 AdaBoost 不易过拟合）。

**飞腾锚点 🟢 分支预测 0.71 vs 3.14**：弱分类器（决策桩 stump = 单变量阈值）本质是条件分支，
分支预测命中（0.71 周期）vs 失败（3.14 周期）的 4.4× 差异直接决定 stump 集成在 CPU 上的吞吐——
这是 GBDT 在推理端比神经网络更「CPU 友好」的硬件根源。

**关键定理**：AdaBoost 训练误差

$$\widehat R_T\le 2^T\prod_{t=1}^T Z_t\le\prod_{t=1}^T\sqrt{1-4\gamma_t^2}\le\exp\!\Big(-2\sum_{t=1}^T\gamma_t^2\Big),\quad\gamma_t=\tfrac12-\epsilon_t$$

**自测**：每轮弱分类器训练错误率 $\epsilon_t=0.4$（即 $\gamma_t=0.1$），$T=100$ 轮，训练误差上界？解：$\le\exp(-2\times100\times0.01)=e^{-2}\approx0.135$。

## 第 8 章 On-Line Learning

**核心**：在线学习放弃「一次性拿到全部 i.i.d. 数据」假设，逐样本到达、逐样本决策，用 **regret**（与事后最优固定策略的累计损失差）代替 PAC 风险。
**加权多数算法 / Hedge（指数加权）**给出 $O(\sqrt{T\ln N})$ 的 regret 界。
这一章是 multi-armed bandit、在线凸优化、乃至深度学习 epoch 训练（SGD 本质是在线）的理论根基——regret 界保证「只要跑得够久，累计表现接近最优」。

**飞腾锚点 🟡 UDOT 16.9×**：regret 分析全是「逐 $t=1\dots T$ 求和」的累积损失——UDOT 向量化求和加速大规模在线算法的批量评估与回测。

**关键定理**：Hedge（指数加权）对 $N$ 个专家、$T$ 轮、损失 $\in[0,1]$：

$$\sum_{t=1}^T\ell_t \le \min_{i}\sum_{t=1}^T\ell_{t,i}+O\!\big(\sqrt{T\ln N}\big)\qquad(\text{regret } \le O(\sqrt{T\ln N}))$$

**自测**：$N=1000$ 专家，$T=10000$，Hedge 的 regret 上界量级？解：$\sqrt{10000\cdot\ln1000}\approx\sqrt{10000\times6.9}\approx263$，即平均每轮 regret $\approx0.026$。

## 第 9 章 Multi-Class Classification

**核心**：把二分类 PAC/Rademacher 界推广到 $K$ 类。三条算法路线：①**一对多 / 一对一**（$K$ 或 $K(K-1)/2$ 个二分类器）；
②**误差纠正输出码 ECOC**（用编码矩阵把多类编成多个二分类，靠码距纠错）；③**原生多类 SVM / 多类 Boosting / 决策树**。
本章给出多类 margin 界，复杂度因子随 $K$ 增长。

**飞腾锚点 🟡 分支预测**：多类决策（argmax 比较 / ECOC 解码）是数据依赖的分支序列，分支预测命中率影响推理延迟——这是多类大模型推理端优化的关注点。

**关键定理**：多类 Rademacher 界 $\;R\le\widehat R_S+2K\widehat{\mathfrak R}_S(\mathcal H)+O(\sqrt{\ln(1/\delta)/m})$；
ECOC 的纠错能力随码的最小汉明距增长（距 $\delta$ 可纠正 $\lfloor(\delta-1)/2\rfloor$ 个二分类错误）。

**自测**：$K=10$ 类，一对多训练 10 个二分类器，各测试准确率 0.95 且独立，理想多类准确率上界？解：$\approx0.95^{10}\approx0.60$（实际因相关性更低）。

## 第 10 章 Ranking

**核心**：排序不是分类——目标是给样本对 $(x,x')$ 正确排序而非单独打标签。
本章定义成对排序损失、给出排序的 Rademacher 泛化界，并用 SVM 求解（**RankSVM**）。RankBoost（排序版 AdaBoost）也在此。
应用：搜索引擎文档排序、推荐系统。排序学习的难点在于样本对空间是 $O(m^2)$，需结构化或抽样技巧控制开销。

**飞腾锚点 🟡 matmul 15×**：成对排序需构造 $O(m^2)$ 样本对，核矩阵 / 内积矩阵规模爆炸（$m=10^4$ 即 $10^8$ 对），
matmul 向量化是唯一可行的工程路径，否则内存与算力双双崩盘。

**关键定理**：成对排序泛化界 $\;R_{\text{rank}}\le\widehat R_{S,\text{rank}}+O(\widehat{\mathfrak R}_S(\mathcal H_{\text{pair}})+\sqrt{1/m})$；
RankSVM 的间隔约束作用于样本对 $(x_i,x_j)$ 而非单样本。

**自测**：$m=1000$ 样本，成对排序的样本对数？如何避免 $O(m^2)$ 开销？解：$m(m-1)/2\approx5\times10^5$；用结构化 SVM、成对抽样或近似核（Nyström）降阶。

## 第 11 章 Regression

**核心**：把 PAC 框架从 $\{0,1\}$ 损失推广到实值损失（平方、绝对）。关键是**有界损失**下 Rademacher 复杂度仍适用；
线性回归的 Rademacher 复杂度 $\mathfrak R_m\le BR/\sqrt m$（$B$ 权重范数上界、$R$ 输入范数上界）。
正则化（Ridge 收缩范数 / Lasso 促稀疏）压缩 $B$ 即压缩 $\mathfrak R_m$ 即压缩泛化误差——这是「正则化 = 控复杂度 = 控泛化」三联式的数学表达。

**飞腾锚点 🟡 FP16 3.81×**：平方损失数值范围随标签与预测放大，FP16 的有限精度（最大约 65504）在高维回归中易溢出——
FP16 vs FP32 的 3.81× 算力差是 mixed-precision 训练中「损失缩放（loss scaling）」技巧存在的直接原因。

**关键定理**：实值线性类 $\mathcal H=\{x\mapsto w\cdot x:\|w\|\le B\}$，$\|x\|\le R$：

$$\mathfrak R_m(\mathcal H)\le\frac{BR}{\sqrt m};\qquad R(h)\le\widehat R_S(h)+2\frac{BR}{\sqrt m}+O(\sqrt{1/m})$$

**自测**：$B=1,R=3,m=900$，线性回归 Rademacher 复杂度上界？解：$3/\sqrt{900}=0.1$。

## 第 12 章 Maximum Entropy Models

**核心**：最大熵原理——在满足经验特征约束的所有分布中，选**熵最大**的那个（最少额外假设，E.T. Jaynes 的认识论原则）。
其对偶问题是**指数族** $p_w(x)=\frac1Z\exp(w\cdot F(x))$。本章用 **Fenchel 对偶**（附录 B）把「约束最大化熵」转成「无约束最大化对数似然」，
是生成式建模（语言模型、CRF 的生成侧）的理论核心。本章是 2ed 新增。

**飞腾锚点 🟡 Schmidt 正交化**：最大熵的对偶几何上是在「特征约束子空间」内找「最均匀（投影到可行域极点）」的分布——
Schmidt 正交化对应的投影/正交操作是其几何直觉。

**关键定理**：$\;\max_p H(p)\;$ s.t. $\mathbb E_p[F]=\widehat{\mathbb E}_S[F]$；对偶解为指数族 $p_w(x)=Z(w)^{-1}\exp(w\cdot F(x))$，$w$ 由对数似然（凸函数）优化求得；
最大熵 ⇔ 最小相对熵 $D(p\|u)$（$u$ 均匀）。

**自测**：给定特征 $F(x)=x$，经验均值 $\bar x=0$，仅约束均值时最大熵分布是？加方差约束后呢？答：仅均值约束 → 在无界域上无解（需支撑集限定）；加均值+方差约束 → 高斯分布。

## 第 13 章 Conditional Maximum Entropy Models

**核心**：把第 12 章的最大熵从「建模 $p(x)$」推广到「建模 $p(y|x)$」——条件最大熵。
其对偶解正是** logistic regression**（二类）与 **softmax**（多类）：$p_w(y|x)=\frac{\exp(w\cdot\Phi(x,y))}{\sum_{y'}\exp(w\cdot\Phi(x,y'))}$。
MLE = 条件最大熵，二者用 Rademacher 界给出泛化保证。本章是判别式概率分类器（含深度 softmax 输出层）的理论归宿，是 2ed 新增。

**飞腾锚点 🟡 FP16 3.81×**：softmax 分母的 $\sum_{y'}\exp(\cdot)$ 易数值溢出，需 **log-sum-exp 稳定化技巧**——
FP16 的有限精度使该技巧在混合精度训练中成为必需，否则上溢/下溢导致 NaN。

**关键定理**：条件最大熵 ⇔ logistic regression MLE：

$$p_w(y|x)=\frac{\exp(w\cdot\Phi(x,y))}{\sum_{y'}\exp(w\cdot\Phi(x,y'))};\quad \widehat w=\arg\max_w\sum_i\log p_w(y_i|x_i)$$

泛化界用特征映射 $\Phi$ 的 Rademacher 复杂度给出。

**自测**：2 类 logistic regression，$\Phi(x,y)=x\cdot\mathbf 1[y=1]$，写出 $p_w(y=1|x)$。答：sigmoid $\sigma(w\cdot x)=1/(1+e^{-w\cdot x})$。

## 第 14 章 Algorithmic Stability

**核心**：换一个全新视角看泛化——不分析假设类的复杂度（VC/Rademacher），而分析**学习算法本身**的稳定性：
若替换训练集里一个样本，输出假设变化很小（$\beta$-一致稳定），则该算法自动泛化。
**强凸正则化 ERM**（Ridge / 正则 logistic）是 $\beta=O(1/(\lambda m))$ 稳定的。
本章解释了「为什么正则化既降方差又保证泛化」——因为正则化让算法变稳定。这是理解深度学习泛化（SGD 隐式正则、dropout）的另一把钥匙。

**飞腾锚点 🟢 Iron Law<2%**：稳定性是泛化 Iron Law 的**算法层**精确化——稳定算法的经验-真实误差带宽天然可控，无需先算 VC 维。

**关键定理**：若算法为 $\beta$-一致稳定、损失 $\le M$，以概率 $\ge1-\delta$：

$$R(h_S)\le\widehat R_S(h_S)+2\beta+(4\beta+M)\sqrt{\frac{\ln(2/\delta)}{2m}};\quad\text{强凸情形 }\beta=\frac{2L^2}{\lambda m}$$

**自测**：$\lambda$-强凸、Lipschitz $L=1$，$m=1000,\lambda=0.01$，稳定性 $\beta$？解：$\beta=2L^2/(\lambda m)=2/(0.01\times1000)=0.2$。

## 第 15 章 Dimensionality Reduction

**核心**：高维数据的「维数灾难」（距离趋同、样本稀疏）用降维缓解。
**PCA** 取协方差矩阵 $\Sigma$ 的 top-$k$ 特征向量（最优线性重构，最小重构误差）；**KPCA** 用核推广到非线性流形；
**Johnson-Lindenstrauss 引理**保证随机投影近似保持任意点对距离。本章是数据可视化、特征压缩、流形学习、随机化算法的理论入口。

**飞腾锚点 🟢 Schmidt 正交化**：PCA 即在主成分方向做正交投影（协方差对角化）——
Schmidt 正交化的投影/正交操作是其数值核心，特征向量求解等价于找一组正交基。

**关键定理**：PCA = 协方差 $\Sigma$ 的 top-$k$ 特征向量；JL 引理：对任意 $n$ 点，投影到 $k=O(\ln n/\epsilon^2)$ 维保持

$$(1-\epsilon)\|x_i-x_j\|\le\|\tilde x_i-\tilde x_j\|\le(1+\epsilon)\|x_i-x_j\|$$

**自测**：$n=10^6$ 个点，要保持距离失真 $\epsilon=0.1$，JL 最小目标维数？解：$k\gtrsim\ln(10^6)/\epsilon^2\approx47.7/0.01\approx4770$ 维（远小于原维）。

## 第 16 章 Learning Automata and Languages

**核心**：Mohri 的看家领域。本章研究**序列数据**上的学习——从正负样本推断确定性有限自动机（DFA）、序列分类与语法推断。
用 PAC 框架定义「语言可学」，给出自动机推断的样本复杂度与算法（如 RPNI 思路）。
这是 NLP、语音识别、生物序列（DNA/蛋白质）建模的工程理论根基，也是本书区别于一般 ML 教材的独门章节。

**飞腾锚点 🟡 分支预测**：DFA 的状态转移即一张条件分支表，推理时分支命中率决定序列分类器的吞吐——WFST 解码引擎的优化正围绕这一点。

**关键定理**：DFA 类的 VC 维与状态数相关；PAC 可推断需样本 $m\ge O\big(\tfrac1\epsilon(|Q|\ln|Q|+\ln\tfrac1\delta)\big)$（$|Q|$ 状态数）；
正则语言的精确推断受 Gold 定理限制（不可行），故用 PAC 近似。

**自测**：要 PAC 学一个 10 状态 DFA，$\epsilon=\delta=0.05$，样本复杂度量级？解：$\propto10\ln10/\epsilon\approx23/0.05\approx460$，量级约数千样本。

## 第 17 章 Reinforcement Learning

**核心**：强化学习放弃「样本独立同分布」假设，转入**序贯决策**——当前动作影响未来状态。
建模为 MDP（状态/动作/转移概率/奖励/折扣因子 $\gamma$），核心方程 **Bellman 最优性**。
本章给出 **PAC-MDP** 框架——在采样次数多项式界内学到 $\epsilon$-最优策略。与 Sutton-Barto 的算法直觉视角互补，Mohri 给出的是样本复杂度的严格保证。

**飞腾锚点 🟡 GEMM 9.45G**：值迭代 / 策略评估的核心是状态-转移矩阵乘法 $P\cdot V$，大状态空间下 GEMM 是算力瓶颈——
这也是值函数近似（DQN 把表格 $V$ 换成神经网络）存在的工程理由。

**关键定理**：Bellman 最优性 $\;V^\star(s)=\max_a\big[r(s,a)+\gamma\sum_{s'}P(s'|s,a)V^\star(s')\big]$；PAC-MDP：以 $\tilde O\big(|S||A|/(\epsilon^2(1-\gamma))\big)$ 样本得 $\epsilon$-最优策略。

**自测**：$\gamma=0.9$，有效时域 $1/(1-\gamma)=10$，PAC-MDP 样本复杂度对 $\epsilon$ 的依赖？解：$\propto1/\epsilon^2$，$\epsilon$ 减半则所需样本 $\times4$。

---

## §9 全书思想主线

Mohri 的统一主线是「**样本复杂度 + Rademacher 复杂度**」双轴。
**第 2 章 PAC** 给出「学习何时可能」的 $m(\epsilon,\delta)$ 形式答案；
**第 3 章 Rademacher** 把粗糙、数据无关的 VC 维升级为数据相关、更紧的复杂度度量；
之后每一章都是把这对工具**下放到一个具体场景**：SVM 用间隔（§5）、核方法用 RKHS 范数（§6）、
Boosting 用指数损失坐标下降（§7）、在线用 regret（§8）、多类/排序/回归用各自的 Rademacher（§9–11）、
最大熵用 Fenchel 对偶（§12–13）、稳定性用算法本身（§14）；最后 §15–17 把框架拓展到降维、序列、强化学习。

**一句话**：Mohri 教你「**给定一个新算法，如何用 Rademacher/PAC 给它配一个泛化保证**」——
这正是 Shalev-Shwartz 建立 PAC 直觉、Hastie 给完统计直觉之后，仍缺的那块「**研究级紧界工具**」。
读完本书，应当能对深度学习的过参数化泛化、SVM 的间隔优势、AdaBoost 的抗过拟合，各给出一条可计算的理论解释链，而非停留在工程经验。

---

## §10 交叉引用

**同类教材对比**：

1. **vs [Shalev-Shwartz 理解 ML](shalev_shwartz_理解机器学习_快速逐章.md)**：SS-BD 是 PAC 严格化入门（31 章、最易懂的证明）；Mohri 是其算法深化——
   SS-BD 的 Ch26 Rademacher 在 Mohri §3 被抬为全书主轴，SS-BD 的 Ch21 在线学习在 Mohri §8 更深，SS-BD 无最大熵/条件最大熵（Mohri §12–13 是 2ed 新增）。
2. **vs [Hastie ESL](hastie_统计学习基础ESL_快速逐章.md)**：ESL 的 SVM(Ch12)/Boosting(Ch10) 算法谱全但证明偏几何直觉；Mohri 给出严格 PAC/Rademacher 界。
   ESL 的偏差-方差 ↔ Mohri 的估计-近似误差是同一权衡的两种语言；ESL 的 Lasso(Ch3/18) ↔ Mohri §14 稳定性（强凸正则）。
3. **vs [Bishop PRML](bishop_PRML_模式识别与机器学习_快速逐章.md)**：Bishop 是贝叶斯（先验后验边缘化），Mohri §12–13 的最大熵/logistic 是频率派对照——
   Bishop Ch4 logistic 回归 ↔ Mohri §13，但 Bishop 无 Rademacher 界，Bishop Ch6 核方法 ↔ Mohri §6。
4. **vs [Murphy MLPP](murphy_机器学习概率视角_快速逐章.md)**：Murphy 贝叶斯+频率并蓄、最全面；Mohri 严格性更深但概率建模视角更窄，二者互补。
5. **vs [Cover-Thomas 信息论](cover_thomas_信息论_快速逐章.md)**：Mohri §12 最大熵原理 = Cover-Thomas 的最小相对熵原理（$D(p\|u)$），
   Mohri 附录 E（2ed 新增信息论）直接对接 Cover-Thomas 第 2/12 章。

**AI/工程锚点**：

6. **深度学习泛化界**：Mohri §3 Rademacher 界是解释「为什么过参数化深度网仍泛化」的理论起点
   （虽紧度不足，需 PAC-Bayes / 隐式正则 / 双下降补充）——对接 [Goodfellow 深度学习](goodfellow_深度学习_快速逐章.md)。
7. **SVM 工业实现**：Mohri §5–6 的对偶 QP + 核矩阵 → liblinear/libsvm/Sklearn 的工程实现，matmul/GEMM 锚点对应其热点。
8. **GBDT/XGBoost/LightGBM**：Mohri §7 AdaBoost 的指数损失坐标下降是 Gradient Boosting（Hastie §10）的理论祖宗，XGBoost/LightGBM 即其工业化（二阶牛顿 + 列抽样）。
9. **混合精度训练**：Mohri §11/§13 的数值范围分析（平方损失溢出、log-sum-exp 稳定性）解释 FP16 mixed-precision 训练为何需要损失缩放——FP16 3.81× 锚点。
10. **DQN/值函数近似**：Mohri §17 PAC-MDP 的样本复杂度界是 DQN「为什么能学」的原始理论参照，GEMM 锚点对应值迭代的矩阵开销；连接 [Sutton-Barto 强化学习](sutton_barto_强化学习_快速逐章.md)。
