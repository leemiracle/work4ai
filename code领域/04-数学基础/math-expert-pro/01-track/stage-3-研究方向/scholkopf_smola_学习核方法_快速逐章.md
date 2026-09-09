# Bernhard Schölkopf, Alexander J. Smola《学习核方法》 · 快速逐章精读

> 基于原书 `Learning with Kernels: Support Vector Machines, Regularization, Optimization, and Beyond`
> (Bernhard Schölkopf, Alexander J. Smola, Adaptive Computation and Machine Learning series, MIT Press, 2002, ~626pp)
> · **stage-3 方向 A(ML 理论) 核方法开山之作**。
> 三柱 = RKHS(再生核 Hilbert 空间) × Large Margin(大间隔) × Regularization(正则化)
> 关联:[Hastie ESL] · [Bishop PRML] · [Murphy MLPP] · [Vapnik SLT] · [Cover-Thomas 信息论] · [Shalev-Shwartz 理解ML]
> 创建:2026-07-02 / 读于:2026-07-03 / 套路:每章=核心+飞腾锚点+关键定理/公式+自测
> 已读本仓库:Hastie ESL、Bishop PRML、Murphy MLPP、Wainwright 高维统计、Cover-Thomas 信息论、Shalev-Shwartz 理解ML。
> 定位:**核方法的开山专著,把 SVM/SVR/KPCA/RVM/不变性统一翻译成 RKHS 语言**,是「核方法的数学自洽性专著」。第二句:Schölkopf(SMPI Tübingen 所长)、Smola(AWS) 皆为 Vapnik 学派核心,本书是从 VC 理论到核算法的桥梁。
> 本文为**快速逐章精读**,每章 1 个飞腾锚点 + 1 个关键定理 + 1 道自测题。

---

## §0 引言:核方法是什么,为什么读这本书（约 350 字）

Bernhard Schölkopf 与 Alexander J. Smola 是 Vapnik 的弟子与核方法黄金时代(1995–2005)的**核心建构者**。本书 2002 年由 MIT Press「自适应计算与机器学习」丛书出版,是核方法从分散论文凝聚为**自洽数学体系**的里程碑。全书以**三大支柱**展开:① **再生核 Hilbert 空间(RKHS)**——Mercer 定理保证正定核 $K$ 唯一对应一个 Hilbert 空间与特征映射,使「在无穷维特征空间线性可分」可计算;② **大间隔(Large Margin)**——Vapnik 的最大间隔原理,把「好分类器」翻译成「几何上离两类都远」,且间隔 $\rho=1/\|w\|$ 直接控制 VC 维与泛化误差;③ **正则化理论**——Tikhonov 正则化 $\lambda\|f\|_\mathcal H^2$ 与表示定理联手,保证 RKHS 中正则化经验风险最小的解必为 $f(x)=\sum_i\alpha_i K(x_i,x)$(有限维,可算)。三柱合一,使 SVM 分类、SVR 回归、KPCA 无监督、RVM 贝叶斯、tangent kernel 不变性**共用同一套 RKHS 语言**——这是本书相对 Hastie ESL(工程算法)和 Bishop PRML(贝叶斯)的独特价值:它是核方法的**数学母语读本**。

本仓库已读 Hastie ESL(频率派统计,Ch12 SVM 路径)、Bishop PRML(贝叶斯,Ch6 GP/Ch7 RVM)、Murphy MLPP(概率视角)。本书是其**核数学根**:ESL 讲「SVM 怎么调路径」,本书讲「为什么 RKHS 让 SVM 自洽」;Bishop 的 RVM 直接源自本书 Ch11;Mercer 谱分解与 Cover-Thomas 信息论的 PCA/熵谱同源。读法:Ch3(RKHS)+ Ch4(正则化)+ Ch6(SVM)+ Ch12(KPCA)+ Ch11(RVM)精读。

| 书 | 风格 | 严格性 | 适合谁 |
|:--|:--|:--|:--|
| **Schölkopf-Smola 本书 2002** | 核方法数学专著,RKHS 统一框架,推导严密 | ★★★★(数学严密) | 做 ML 理论/核方法研究,要 RKHS 严格基础者 |
| Vapnik《SLT》1998 | VC 维/SRM 原典,哲学式,泛化理论本源 | ★★★★★(极严密) | 研究泛化理论本源的学者 |
| Hastie ESL 2009 | 频率派统计学习,算法+直觉+工程 | ★★★(工程平衡) | 应用统计学习全谱,想跑算法的人 |
| Bishop PRML 2006 | 贝叶斯 ML,图模型/变分/概率推断 | ★★★★(概率严密) | 贝叶斯 ML、概率推断研究者 |

---

## §1 全书 17 章骨架一览（飞腾锚点分布表）

三部分:**Part I 概念与工具(Ch1–2)** → **Part II 学习理论(Ch3–5)** → **Part III 学习算法(Ch6–17)**。全书灵魂:**以 RKHS 为通用语言,把大间隔、正则化、贝叶斯、不变性统一成「在 Hilbert 空间中定义目标函数」的单一框架。** 锚点池 8 个(分支预测 / Iron Law / UDOT / Schmidt / TLB / matmul / GEMM / FP16),17 章从中分散选用,每章 1 个。

- **Part I 基础(Ch1–2)**:教程引言 → 统计学习理论综述。**分支预测⭐分类判别**。
- **Part II 理论(Ch3–5)**:核与 RKHS → 正则化 → 单类问题。**UDOT/Schmidt⭐点积正交**。
- **Part III 算法(Ch6–14)**:SVM 分类 → SVR → QP 实现 → 不变性 → 理论回顾 → 贝叶斯 → KPCA → 核扩展 → 实践。**matmul/GEMM⭐Gram 矩阵**。
- **结尾(Ch15–17)**:总结 → 开放问题 → 附录。

| 章 | 标题 | 核心概念 | 飞腾锚点 |
|:--|:--|:--|:--|
| Ch1 | A Tutorial Introduction 教程引言 | 超平面、大间隔、核技巧直觉 | 分支预测 🟡 |
| Ch2 | Statistical Learning Theory 综述 | VC 维、SRM、大间隔泛化 | Iron Law<2% 🟡 |
| Ch3 | Kernels and RKHS 核与 RKHS | Mercer 定理、正定核、再生性质 | UDOT 16.9× 🟢⭐ |
| Ch4 | Regularization Theory 正则化 | Tikhonov、Green 函数、表示定理 | Schmidt 正交化 🟡 |
| Ch5 | Single-Class 单类/密度估计 | Parzen 窗、$\nu$-SVM、novelty | TLB 4.81× 🟡 |
| Ch6 | SVM 分类 | 软间隔、对偶、KKT、支持向量 | matmul 15× 🟢⭐ |
| Ch7 | SVM 回归 | $\varepsilon$-insensitive loss、tube | 分支预测 🟢 |
| Ch8 | Implementation of SVM | SMO、分解方法、QP | GEMM 9.45G 🟢⭐ |
| Ch9 | Incorporating Invariances 不变性 | 虚拟样本、tangent kernel | Schmidt 正交化 🟡 |
| Ch10 | Learning Theory Revisited 理论回顾 | margin 界、leave-one-out | FP16 3.81× 🟡 |
| Ch11 | Bayesian Extensions 贝叶斯 | 证据框架、ARD、RVM | Iron Law<2% 🟡 |
| Ch12 | Kernel Feature Extraction 核特征提取 | KPCA、KFA | UDOT 16.9× 🟢 |
| Ch13 | Kernels Beyond 核扩展 | Fisher 核、字符串核、树核 | matmul 15× 🟢 |
| Ch14 | Kernels in Practice 核实践 | 超参选择、模型选择、网格搜索 | TLB 4.81× 🟡 |
| Ch15 | Concluding Remarks 总结 | RKHS 统一四大领域 | 分支预测 🟡 |
| Ch16 | Open Problems 开放问题 | 核学习、多核、半监督 | Schmidt 正交化 🟡 |
| Ch17 | Appendix 杂项 | 数学补充、概率不等式 | GEMM 9.45G 🟢 |

> 🟢 = 直接锚定(概念硬件对应) / 🟡 = 类比锚点(供直觉,不引严格证明)

---

# Part I · 概念与工具（Ch1–2）—— 从直觉到学习理论,分支预测⭐

**本段锚点:分支预测** —— 分类本质是「按超平面符号分支」,与 CPU 0.71 vs 3.14 cycle 的条件分支预测同构。

---

## 第 1 章 · A Tutorial Introduction（教程式引言）

- **核心**:用一个**线性分类器**的几何故事串起全书。① 最简单分类器是符号函数 $f(x)=\mathrm{sign}(w^\top x+b)$,把空间切成两半——这就是「超平面」。② 若两类线性可分,存在无穷多分离超平面;**最大间隔**原理选离两类最近点都最远的那一个,间隔 $\rho=2/\|w\|$,对应优化 $\min_w\frac12\|w\|^2$ s.t. $y_i(w^\top x_i+b)\geq 1$。③ 现实不可分→软间隔引入松弛变量 $\xi_i$。④ 关键飞跃:**核技巧**——把 $w^\top x$ 换成 $\langle\phi(x_i),\phi(x)\rangle=K(x_i,x)$,无需显式映射 $\phi$ 即可在无穷维特征空间线性分类。本章是全书「为什么」的导览。

- **飞腾锚点**:**分支预测** 🟡。分类器输出 $\mathrm{sign}(\cdot)$ 是一个二值条件跳转,与 CPU 分支预测器(命中 0.71 cycle、误预测惩罚 3.14 cycle)同构:margin 越大→分类「分支」越稳→「误预测」(误分)越少。本书借此把泛化与「分支可预测性」挂钩。

- **关键定理/公式**:**最大间隔超平面**
$$\min_{w,b}\ \tfrac12\|w\|^2 \quad\text{s.t.}\quad y_i(w^\top\Phi(x_i)+b)\geq 1,\ \forall i;\qquad \rho=\frac{2}{\|w\|}.$$
间隔 $\rho$ 由 $\|w\|$ 决定,最大化间隔=最小化 $\|w\|$。

- **自测**:给定二维两类点 $x_i$ 线性可分,写出最大间隔问题的标准形式;若 $w=(3,4),b=-5$,间隔是多少?(答:$\rho=2/\sqrt{3^2+4^2}=2/5=0.4$。)

---

## 第 2 章 · An Overview of Statistical Learning Theory（统计学习理论综述:VC、SRM、Large Margin）

- **核心**:本章为核方法提供**泛化理论基础**。① 学习目标是最小化**真实风险** $R(f)=E[L(f(X),Y)]$,但只能观测**经验风险** $\hat R(f)=\frac1n\sum L$。② Vapnik-Chervonenkis(VC)理论给出二者差距界:与函数类的 **VC 维** $h$ 有关,$h$ 越大假设空间越复杂、差距越大。③ **结构风险最小化(SRM)**:把函数类按复杂度嵌套分层 $\mathcal F_1\subset\mathcal F_2\subset\cdots$,在每层最小化经验风险,再按 SRM 界择优——经验风险与复杂度罚的权衡。④ **大间隔**是 SRM 的几何特例:间隔 $\rho$ 大→有效 VC 维小($h\leq R^2/\rho^2$)→泛化好。margin 把 SRM 从抽象分层变成可计算量。

- **飞腾锚点**:**Iron Law<2%** 🟡。SRM 泛化界要求「经验风险 + 复杂度罚」随样本增长而收敛,本质是「误差必须可控到 $<2\%$」的统计版——与大间隔把可分误差压到 0 一致。

- **关键定理/公式**:**VC 泛化界** 与 **SRM 界**:以概率 $1-\eta$,
$$R(f)\leq \hat R(f)+\sqrt{\frac{h\big(\ln(2n/h)+1\big)-\ln(\eta/4)}{n}};$$
**margin VC 上界** $h\leq \min\!\big(R^2/\rho^2,\ n\big)+1$(半径 $R$ 的球内、间隔 $\rho$ 的超平面族)。

- **自测**:对线性可分数据,减小 $C$(软间隔惩罚)会增大还是减小有效间隔 $\rho$?对 VC 维上界有何影响?(答:$C$ 小→允许更多松弛→$\|w\|$ 可更小→$\rho$ 增大→VC 上界减小→泛化界更紧。)

---

# Part II · 学习理论（Ch3–5）—— RKHS + 正则化,UDOT/Schmidt⭐

**本段锚点:UDOT 点积 + Schmidt 正交** —— 核求值是点积累加,正则化是 RKHS 正交投影。

---

## 第 3 章 · Kernels and Reproducing Kernel Hilbert Spaces（核函数与再生核 Hilbert 空间）⭐⭐ 全书地基

- **核心**:本章是全书**数学心脏**。① **核函数**:映射 $K:\mathcal X\times\mathcal X\to\mathbb R$;若对称且**半正定**(对所有 $\{c_i\},\{x_i\}$ 有 $\sum_{ij}c_ic_jK(x_i,x_j)\geq 0$),则称正定核。② **Mercer 定理**:正定核可谱分解 $K(x,y)=\sum_k\lambda_k\psi_k(x)\psi_k(y)$,等价于存在特征映射 $\Phi(x)$ 使 $K(x,y)=\langle\Phi(x),\Phi(y)\rangle$——**核即隐式高维内积**。③ **RKHS**:由核再生的 Hilbert 空间,满足**再生性质** $f(x)=\langle f,K(\cdot,x)\rangle_\mathcal H$,即求值是连续线性泛函。④ **构造核**:多项式核 $K=(x^\top y+c)^d$、高斯 RBF 核 $K=\exp(-\gamma\|x-y\|^2)$;核上的运算(和、积、与概率密度卷积)保持正定性。RKHS 让「无穷维特征空间」变得可计算。

- **飞腾锚点**:**UDOT 16.9×** 🟢⭐。核求值 $K(x_i,x)=\sum_k\Phi_k(x_i)\Phi_k(x)$ 是**点积累加**,与 CPU `UDOT`(无符号点积)16.9× 加速的 SIMD 点积指令同构:Gram 矩阵 $K_{ij}$ 的每一行就是一次点积,Gram 行是核方法的计算肉身。

- **关键定理/公式**:**Mercer 定理** $K(x,y)=\sum_{k=1}^\infty\lambda_k\psi_k(x)\psi_k(y)$($\lambda_k\geq 0$);**再生性质** $f(x)=\langle f,K_x\rangle_\mathcal H$;正定判据 $\sum_{ij}c_ic_jK(x_i,x_j)\geq 0$。RBF 核对应**无穷维**特征空间(核展开含所有阶多项式)。

- **自测**:验证高斯 RBF 核 $K(x,y)=\exp(-\gamma\|x-y\|^2)$ 是正定核。(提示:展开 $\exp(-\gamma\|x-y\|^2)=\exp(-\gamma\|x\|^2)\exp(2\gamma x^\top y)\exp(-\gamma\|y\|^2)$,中项是无穷级数正项和。)$\gamma\to\infty$ 时 RKHS 越来越复杂还是越简单?(复杂→过拟合。)

---

## 第 4 章 · Regularization Theory（正则化理论）

- **核心**:正则化是核方法的**第二支柱**,回答「RKHS 里无穷多函数,选哪个」。① **Tikhonov 正则化**:在 RKHS $\mathcal H$ 中最小化「数据拟合 + 罚」
$$\min_{f\in\mathcal H}\ \frac1n\sum_{i=1}^n c(f(x_i),y_i)+\frac{\lambda}{2}\|f\|_\mathcal H^2,$$
罚项 $\|f\|_\mathcal H^2$ 控制复杂度,$\lambda$ 越大越平滑。② **Green 函数**:该变分问题的解由算子的 Green 函数表示,而核 $K$ 正是对应算子的 Green 函数。③ **表示定理(Representer Theorem)**:正则化经验风险最小的解**必**落在样本核函数的张成空间 $f^*(x)=\sum_i\alpha_iK(x_i,x)$——把无穷维优化降为有限维 $\alpha\in\mathbb R^n$,这是 SVM/SVR/RVR 可计算的根源。④ 不同损失 $c$ 给不同方法:合页损失→SVM、$\varepsilon$-insensitive→SVR、平方→正则化网络/RVM。

- **飞腾锚点**:**Schmidt 正交化** 🟡。表示定理的本质是「最优解落在数据张成的子空间」,即**正交投影**:解 $f^*$ 是真实目标函数在 $\mathrm{span}\{K_{x_i}\}$ 上的 RKHS 投影(残差正交于该子空间),与 Schmidt 正交分解「向量=投影+正交残差」同构。

- **关键定理/公式**:**Representer Theorem**
$$f^*(x)=\sum_{i=1}^n\alpha_i\,K(x_i,x),\qquad f^*\in\mathrm{span}\{K(\cdot,x_1),\dots,K(\cdot,x_n)\}.$$
即 Tikhonov 正则化经验风险最小化在 RKHS 中的解为样本核函数的有限线性组合。

- **自测**:为什么表示定理说解在「样本张成子空间」而不是整个 RKHS?(答:罚项 $\|f\|_\mathcal H^2$ 使解偏向最小范数;由再生性质,任意 $f$ 在 $\mathrm{span}\{K_{x_i}\}$ 外的分量只增加范数不降低经验风险,故最优解投影到子空间内。)

---

## 第 5 章 · Single-Class Problems: Density Estimation and Novelty Detection（单类问题:密度估计与新颖性检测）

- **核心**:只有一类(正常)样本时,如何描述分布、检测异常。① **密度估计**:Parzen 窗核密度估计 $\hat p(x)=\frac1n\sum_i K_h(x-x_i)$,RBF 核的带宽 $h$ 控制平滑。② **新颖性/异常检测**:不求密度,而求一个把大部分样本「包住」、把离群点排外的**最小体积区域**——这是单类 SVM($\nu$-SVM)的思想。③ **$\nu$-SVM**:在特征空间用超平面把原点与样本分开,优化 $\min\frac12\|w\|^2+\frac1{\nu n}\sum\xi_i-\rho$,分数维 $\nu\in(0,1]$ 同时控制支持向量比例与误差率上限。④ 单类是二类的退化:把「原点」当第二类,间隔区域即「正常分布的紧凑描述」。本章把密度、分位数、异常检测统一到 RKHS 的几何框架。

- **飞腾锚点**:**TLB 4.81×** 🟡。单类/异常检测在线推理时,新样本 $x$ 是否落在支持区域需与缓存的支持向量核行比较;核行缓存命中 TLB(4.81× 局部性收益)决定实时异常检测的吞吐。

- **关键定理/公式**:**$\nu$-SVM**
$$\min_{w,\xi,\rho}\ \tfrac12\|w\|^2+\frac1{\nu n}\sum_{i=1}^n\xi_i-\rho \quad\text{s.t.}\quad \langle w,\Phi(x_i)\rangle\geq \rho-\xi_i,\ \xi_i\geq0,$$
$\nu$ 既是支持向量比例的上界,也是训练误差比例的上界。

- **自测**:对 100 个正常样本,设 $\nu=0.1$,最多有多少比例被当作异常排除在外?支持向量至少占多少?(答:误差上界 $=0.1$,故至多 10 个被排外;支持向量比例 $\geq\nu=0.1$,故 $\geq 10$ 个 SV。)

---

# Part III · 学习算法（Ch6–17）—— SVM/SVR/QP/KPCA/RVM/扩展,matmul/GEMM⭐

**本段锚点:matmul + GEMM** —— SVM 对偶是 Gram 矩阵运算,大规模 QP 靠 GEMM 吞吐。

---

## 第 6 章 · Support Vector Classification（SVM 分类）⭐⭐ SVM 核心

- **核心**:本章把第 1 章的直觉变成**完整算法**。① **软间隔 SVM**:允许松弛 $\xi_i$ 处理不可分,
$$\min_{w,b,\xi}\ \tfrac12\|w\|^2+C\sum\xi_i \quad\text{s.t.}\quad y_i(w^\top\Phi(x_i)+b)\geq1-\xi_i,\ \xi_i\geq0.$$
② **拉格朗日对偶**:化为主问题的对偶
$$\max_\alpha\ \sum_i\alpha_i-\tfrac12\sum_{ij}\alpha_i\alpha_j y_iy_jK(x_i,x_j),\quad 0\leq\alpha_i\leq C,\ \sum_i\alpha_i y_i=0,$$
解 $w=\sum_i\alpha_iy_i\Phi(x_i)$,只依赖**支持向量**($\alpha_i>0$)。③ **KKT 条件**互补松弛 $\alpha_i[y_i(w^\top\Phi(x_i)+b)-1+\xi_i]=0$ 决定 SV 集合。④ 决策函数 $f(x)=\mathrm{sign}(\sum_i\alpha_iy_iK(x_i,x)+b)$。对偶把问题从特征维数 $d$ 移到样本数 $n$,这正是核技巧可行的关键。

- **飞腾锚点**:**matmul 15×** 🟢⭐。对偶目标含 Gram 矩阵 $Q_{ij}=y_iy_jK(x_i,x_j)\in\mathbb R^{n\times n}$,每次梯度/SMO 更新都要算 $Q\alpha$——纯矩阵乘,与 `matmul` 15× 加速的 GEMV 同构。$Q$ 是 SVM 的计算瓶颈。

- **关键定理/公式**:**SVM 对偶**
$$\boxed{\ \max_\alpha\ \sum_{i=1}^n\alpha_i-\tfrac12\sum_{i,j}\alpha_i\alpha_j y_i y_j\,K(x_i,x_j),\qquad 0\leq\alpha_i\leq C,\ \sum_i\alpha_iy_i=0\ }$$
决策函数 $f(x)=\mathrm{sign}\!\big(\sum_i\alpha_iy_iK(x_i,x)+b\big)$,$b$ 由任一 $0<\alpha_i<C$ 的 SV 求得。

- **自测**:Iris 数据 setosa vs versicolor 两类(各 50 样本),用 RBF 核 $K=\exp(-0.5\|x-y\|^2)$、$C=1$。若训练后 $\alpha$ 中只有 8 个非零,其余 92 个 $\alpha_i=0$ 说明什么?这 8 个是什么?(答:它们是支持向量,决定了分类超平面;其余样本不在间隔边界、被正确分类且余量足,对 $w$ 无贡献。)

---

## 第 7 章 · Support Vector Regression（SVM 回归)

- **核心**:把 SVM 的「间隔」从分类推广到回归。① **$\varepsilon$-insensitive loss**:仅当预测偏差 $|f(x_i)-y_i|>\varepsilon$ 才有损失,
$$|t|_\varepsilon=\max(0,|t|-\varepsilon),$$
宽度 $\varepsilon$ 的「tube」内样本零损失——造就**稀疏支持向量**(tube 外才是 SV)。② **$\varepsilon$-SVR**:
$$\min\ \tfrac12\|w\|^2+C\sum|f(x_i)-y_i|_\varepsilon,$$
对偶后 $f(x)=\sum_i(\alpha_i-\alpha_i^*)K(x_i,x)+b$,只有落在 tube 外的点 $\alpha\neq0$。③ **$\nu$-SVR**:用 $\nu$ 自动确定 $\varepsilon$ 与支持向量比例,$\nu$ 越小 tube 越宽、SV 越少。④ 稀疏性来源:与分类 SVM 的「间隔外才罚」不同,SVR 是「tube 内不罚」,两者稀疏机制同源(不活跃样本系数归零)。本章把「大间隔几何」翻译成「tube 几何」。

- **飞腾锚点**:**分支预测** 🟢。$\varepsilon$-tube 判定 $|f(x_i)-y_i|>\varepsilon$ 是**条件分支**:在 tube 内(零梯度、跳过)还是外(产生损失与梯度)。KKT 选择 SV 也是逐点条件判断——分支预测器命中率决定 QP 内循环吞吐。

- **关键定理/公式**:**$\varepsilon$-SVR 对偶**
$$\min_{\alpha,\alpha^*}\ \tfrac12\sum_{ij}(\alpha_i-\alpha_i^*)(\alpha_j-\alpha_j^*)K_{ij}+\varepsilon\sum_i(\alpha_i+\alpha_i^*)-\sum_iy_i(\alpha_i-\alpha_i^*),$$
约束 $\sum(\alpha_i-\alpha_i^*)=0,\ 0\leq\alpha_i,\alpha_i^*\leq C$;$f(x)=\sum_i(\alpha_i-\alpha_i^*)K(x_i,x)+b$。

- **自测**:Boston 房价(506 样本)用 SVR,$\varepsilon=0.1,C=10$,RBF 核。若 $\varepsilon$ 从 0.1 增到 1.0,支持向量数目会怎样?过拟合风险?(答:tube 变宽→更多样本落在 tube 内→SV 减少→模型更平滑→欠拟合风险上升。)

---

## 第 8 章 · Implementation of SVM（QP 实现:SMO、分解方法）⭐⭐ 工程核心

- **核心**:SVM 对偶是带线性等式与 box 约束的**凸二次规划(QQP)**,$n$ 大时 $Q\in\mathbb R^{n\times n}$ 无法全存。① **分解方法(Decomposition / chunking)**:每次只优化 $\alpha$ 的一个子集(working set),其余固定,迭代收敛——Vapnik 的 chunking 是其鼻祖。② **SMO(序列最小优化,Platt 1998)**:每次只选 2 个变量更新(等式约束要求成对),解析求解二元 QP,无需通用 QP 求解器,极大降低内存。③ **核缓存(caching kernel rows)**:反复使用的 $K(x_i,\cdot)$ 行缓存,避免重算。④ ** shrinking(收缩)**:迭代中识别并冻结大概率非 SV 的 $\alpha_i=0$ 变量,缩小有效规模。libSVM = SMO + 缓存 + shrinking 的工业实现。本章是「理论 SVM」到「可跑 SVM」的关键一跃。

- **飞腾锚点**:**GEMM 9.45G** 🟢⭐。大规模 SVM(百万样本)的瓶颈是 Gram 子块 $Q_{WW}\alpha_W$ 的矩阵乘;GPU/向量化的 GEMM(9.45 GFLOPS)把 SMO 内层的批量核求值压到实时——ThunderSVM/cuML 即以此为引擎。

- **关键定理/公式**:**SMO 两变量更新**:选 $\alpha_1,\alpha_2$ 后,沿等式约束 $\alpha_1y_1+\alpha_2y_2=\text{const}$ 一维搜索,解析解
$$\alpha_2^{\text{new}}=\alpha_2^{\text{old}}+\frac{y_2(E_1-E_2)}{\eta},\quad \eta=K_{11}+K_{22}-2K_{12},$$
再 box-clip 到 $[L,H]$;$E_i=f(x_i)-y_i$ 为预测误差。收敛由 KKT 违背量驱动。

- **自测**:为什么 SMO 每次必须同时更新 2 个 $\alpha$ 而非 1 个?(答:等式约束 $\sum\alpha_iy_i=0$ 耦合变量,单变量更新会破坏约束;选 2 个可沿约束方向移动保持可行性。)

---

## 第 9 章 · Incorporating Invariances（不变性引入:虚拟样本、tangent kernel）

- **核心**:先验知识「分类对某些变换不变」(图像平移/旋转不变)如何注入 SVM。① **虚拟样本(virtual examples)**:对每个样本施加已知不变变换生成增广样本,加入训练——朴素但有效。② **tangent kernel(切核)**:更优雅的方式。若变换的不变性可用切向量 $\tau(x)=\partial_t T_t(x)|_{t=0}$ 局部刻画,则构造
$$K_{\text{tangent}}(x,y)=K(x,y)+\langleabla_x K(x,y),\tau(x)\rangle+\langleabla_yK(x,y),\tau(y)\rangle+\langle\tau(x),\tau(y)\rangle,$$
保持正定性且编码一阶不变性。③ 等价性:虚拟样本(线性核下)≈ tangent kernel 的一阶近似。④ 不变性是「正则化先验」的核语言:惩罚沿不变方向的快速变化。本章把领域知识(平移/旋转/尺度)翻译成可计算的核修正。

- **飞腾锚点**:**Schmidt 正交化** 🟡。tangent kernel 本质是「在特征空间中,把沿不变切方向的分量投影掉/弱化」,保留与不变方向**正交**的有判别力分量——与 Schmidt 正交分解「信号=目标分量+正交补」同构。

- **关键定理/公式**:**Jittered/tangent kernel**(一阶)在 RBF 核下退化为方向加权 RBF;不变性等价于在 RKHS 中对不变算子 $L$ 施罚 $\|Lf\|_\mathcal H^2$,对应修正核 $K\to(I+L)^{-1}K$。

- **自测**:MNIST 手写数字,希望分类对 $5^\circ$ 内旋转不变。描述两种注入方式:① 数据增广怎么做?② tangent kernel 需要什么?(答:① 对每图生成 $-5^\circ\ldots5^\circ$ 旋转副本加入训练;② 估计每样本的旋转切向量 $\tau(x)$(图像旋转的数值微分),代入 tangent kernel 公式构造 $K_{\text{tangent}}$。)

---

## 第 10 章 · Learning Theory Revisited（学习理论回顾:margin 界、leave-one-out）

- **核心**:用前几章的工具**重新审视泛化**。① **基于间隔的界**:不依赖 VC 维,而依赖样本在特征空间的半径 $R$ 与间隔 $\rho$,$h\leq R^2/\rho^2$;当 $\rho$ 大时即便特征维数极高,有效复杂度仍低——解释「无穷维 RBF 特征空间仍泛化」。② **leave-one-out(LOO)**:对 SVM 有特殊的 LOO 估计——LOO 误差上界由支持向量数控制,「训练后若第 $i$ 个样本不是 SV,则删去它不影响预测」,故 $\text{LOO err}\leq \#\text{SV}/n$。③ **$\nu$ 与误差率**的对应:Ch5 的 $\nu$ 既是 SV 比例上界也是误差上界,可直接读出泛化。④ 本章把 Ch2 的抽象 SRM 收紧为「margin + 半径 + SV 数」的**可计算泛化诊断**,是模型选择的理论依据。

- **飞腾锚点**:**FP16 3.81×** 🟡。margin 界、半径 $R$、$\#\text{SV}$ 都涉及 Gram 矩阵的数值估计;大规模下用 FP16(3.81× 加速、3.4e3 最大值)计算 $\|w\|^2=\alpha^\top Q\alpha$ 等,须监控数值稳定($\eta=K_{11}+K_{22}-2K_{12}$ 可能下溢)。

- **关键定理/公式**:**margin 泛化界** $R(f)\leq \tilde O\!\big(\sqrt{(R^2\|w\|^2)/n}\big)$;**SVM 的 LOO 上界** $\mathrm{Err}_{\text{LOO}}\leq \frac{1}{n}\#\{i:\alpha_i>0\}$。

- **自测**:某 SVM 训练后 $\#\text{SV}=30$,总样本 $n=200$。给出 LOO 误差上界。若把 $C$ 调大,SV 数通常如何变?LOO 界?(答:LOO err $\leq 30/200=0.15$;$C$ 大→间隔窄→更多样本触界→$\#$SV 增→LOO 界变松。)

---

## 第 11 章 · Bayesian Extensions（贝叶斯扩展:证据框架、ARD、RVM）

- **核心**:给核方法披上**贝叶斯外衣**,并催生了稀疏的 RVM。① **贝叶斯线性模型** $y=\Phi w+\varepsilon$,高斯先验 $w\sim\mathcal N(0,\alpha^{-1}I)$→后验 $w|\cdot\sim\mathcal N$;MAP 解 = Ridge 回归(等价 Tikhonov 正则化),$\alpha$ 即 $1/\lambda$。② **证据框架(MacKay)**:二级推断超参 $\alpha,\beta$——最大化**边缘似然**(evidence)自动定正则强度,免交叉验证。③ **ARD(自动相关性确定)**:每维/每核分量独立先验精度 $\alpha_i$,证据最大化把无关维的 $\alpha_i\to\infty$→对应权重归零→**自动特征/核选择**。④ **RVM(相关向量机,Tipping 2001)**:用 ARD 先验配核基函数 $\{K(\cdot,x_i)\}$,证据最大化后绝大多数 $\alpha_i\to\infty$,留下极少数「相关向量」——比 SVM 更稀疏、概率输出。本章是本书通向 Bishop PRML 的桥梁。

- **飞腾锚点**:**Iron Law<2%** 🟡。证据框架靠边缘似然做模型选择,本质是「让泛化误差可控到极小」的贝叶斯版——与 SRM 的 $<2\%$ 收敛目标殊途同归;ARD 把无关维罚零,正是「误差铁律」驱动的稀疏化。

- **关键定理/公式**:**证据最大化** $\arg\max_{\alpha,\beta}p(\mathbf y|\alpha,\beta)=\int p(\mathbf y|w,\beta)p(w|\alpha)\,dw$;**RVM 后验** $w|\mathbf y\sim\mathcal N(\mu,\Sigma)$,$\mu=\Sigma\Phi^\top\mathbf y$,$\Sigma=(\alpha^{-1}\Phi^\top\Phi+\beta I)^{-1}$;ARD 解 $\hat\alpha_i\to\infty$⇒$w_i=0$。

- **自测**:RVM 与 SVM 在稀疏机制上有何本质区别?(答:SVM 稀疏来自合页损失的「间隔外才罚」(KKT);RVM 稀疏来自 ARD 先验把无关基的证据罚到零。RVM 通常更稀疏且给概率输出,但训练较慢。)

---

## 第 12 章 · Kernel Feature Extraction（核特征提取:KPCA、KFA）

- **核心**:把**无监督特征提取**搬到特征空间。① **KPCA(核主成分分析,Schölkopf 1998)**:先在特征空间中心化,再对 Gram 矩阵 $K_c$ 做特征分解;主成分是 $K_c$ 的大特征值方向,投影坐标为 $\sum_i\alpha_iK(x_i,x)$。② **中心化技巧**:特征空间均值未知,用 $K_c=K-\mathbf 1_nK-K\mathbf 1_n+\mathbf 1_nK\mathbf 1_n$ 在核层面中心化。③ **核 Fisher 判别(KFDA)**:把线性 Fisher 判别 $w^\top S_Bw/w^\topS_Ww$ 推广到 RKHS,找最大类间/类内方差比的方向,用于核化判别。④ 与线性 PCA 的关系:线性核 $K=XX^\top$ 时 KPCA 退化为样本协方差 PCA;RBF 核提取**非线性主成分**。KPCA 是「核化一切」的范例,也是 kernel k-means、谱聚类的基础。

- **飞腾锚点**:**UDOT 16.9×** 🟢。KPCA 的核心运算是 Gram 矩阵中心化(逐行/列减均值=点积级运算)与特征分解 $K_c\alpha=n\lambda\alpha$;Gram 行的累加是 UDOT 点积指令的密集负载。

- **关键定理/公式**:**KPCA 特征方程**
$$K_c\,\alpha = n\lambda\,\alpha,\qquad \sum_{i=1}^n\alpha_i=0\ (\text{中心化约束}),\quad \text{主成分投影 } \mathrm{PC}_k(x)=\sum_i\alpha_i^{(k)}K(x_i,x).$$
中心化 $K_c=HKH$,$H=I-\frac1n\mathbf 1\mathbf 1^\top$。

- **自测**:用线性核 $K(x,y)=x^\top y$ 跑 KPCA,与直接对数据 $X$ 跑 PCA 结果应如何?(答:完全一致——线性核 Gram $K=XX^\top$ 的特征向量经归一化即样本空间主成分方向;KPCA 是 PCA 的核化推广,线性核时退化。)

---

## 第 13 章 · Kernels Beyond（核方法扩展:Fisher 核、字符串核、树核）

- **核心**:把核的定义从 $\mathbb R^d$ 矢量推广到**非矢量结构化对象**,开启核方法在文本/生物/序列的应用。① **Fisher 核(Jaakkola-Haussler)**:对生成模型 $p(x|\theta)$ 定义 Fisher 得分 $g_x=abla_\theta\log p(x|\theta)$,核 $K(x,y)=g_x^\top\mathcal I^{-1}g_y$($\mathcal I$ Fisher 信息),把生成模型与判别核结合——HMM + SVM 用于语音/蛋白。② **字符串核(String subsequence kernel, Lodhi 2002)**:定义两字符串的子序列匹配核 $K_n(s,t)=\sum_{u\in\Sigma^n}\phi_u(s)\phi_u(t)$,$\phi_u(s)$ 计 $u$ 作为 $s$ 子序列(带衰减)的次数;用动态规划 $O(|s||t|n)$ 计算,使 SVM 直接处理文本。③ **树核/图核**:对解析树/分子图定义结构匹配核。本章把「核=相似性」推广到任意可定义相似性的对象,核方法因此覆盖 NLP/生物/化学。

- **飞腾锚点**:**matmul 15×** 🟢。字符串核的 DP 计算 $K_n(s,t)$ 本质是带权子序列匹配的**张量/矩阵式累加**,与 matmul 的矩阵乘同构;大规模文本分类中 Gram 矩阵每项即一次 DP(等价小矩阵乘)。

- **关键定理/公式**:**Fisher 核** $K_{\text{Fisher}}(x,y)=\big(abla_\theta\log p(x|\theta)\big)^\top\mathcal I(\theta)^{-1}\big(abla_\theta\log p(y|\theta)\big)$;**字符串子序列核** $K_n(s,t)=\sum_{u\in\Sigma^n}\lambda^{\ell(u,s)+\ell(u,t)}\mathbf 1[u\subseteq s]\mathbf 1[u\subseteq t]$($\ell$ 为匹配跨度,DP 可算)。

- **自测**:对长度 10 和 8 的两个字符串,3-gram 子序列核的时间复杂度量级?为什么它比枚举所有公共子序列快?(答:DP $O(|s||t|\cdot n)$ 约 $10\times 8\times 3=240$ 量级;枚举 $\binom{10}{3}\binom{8}{3}$ 指数级,DP 复用子问题。)

---

## 第 14 章 · Kernels in Practice（核在实践中:超参选择、模型选择）

- **核心**:理论到落地的**实战手册**。① **超参选择**:RBF 核的 $\gamma$、惩罚 $C$、tube 宽 $\varepsilon$/$\nu$ 均需调;标准做法是网格搜索(grid search)+ $k$ 折交叉验证选最小验证误差的组合。② **核选择**:先试 RBF(通用),线性核做基线;领域知识可定制(tangent/Fisher/string)。③ **数据预处理**:标准化(z-score)、归一化——RBF 核对尺度敏感,不预处理则 $\gamma$ 失效。④ **规模问题**:$n>10^5$ 时全 Gram 不可行,用 Nyström 近似、random features(Rahimi-Recht)、或线性近似核 + 多核 GPU。⑤ **不平衡/多类**:类加权 $C$、one-vs-rest/one-vs-one 多类扩展。本章是「会跑 SVM」的工程清单,libSVM/sklearn 的默认套路多源于此。

- **飞腾锚点**:**TLB 4.81×** 🟡。网格搜索需对每组 $(C,\gamma)$ 重训,反复访问同一批核行;若核矩阵按行缓存命中 TLB(4.81× 局部性收益),网格搜索的总耗时大幅下降——内存局部性是大规模 SVM 调参的隐形瓶颈。

- **关键定理/公式**:**交叉验证误差** $\mathrm{CV}_k(\theta)=\frac1k\sum_{j=1}^k\frac1{|V_j|}\sum_{i\in V_j}L(f_{\theta}^{(-j)}(x_i),y_i)$,选 $\theta^\*=\arg\min_\theta\mathrm{CV}_k(\theta)$;**Nyström 近似** $\tilde K=K_{nm}K_{mm}^{-1}K_{mn}$($m\ll n$ 采样子集)。

- **自测**:对某数据集,RBF 核 $\gamma$ 从 $10^{-3}$ 扫到 $10^{3}$(对数网格)、$C$ 同样 7 点,共 $7\times7=49$ 组,5 折 CV。总训练次数?若每组平均 2 秒,总耗时?(答:$49\times5=245$ 次训练;约 $245\times2=490$ 秒。这解释了为何要缓存核行与用 GPU。)

---

# Part III 续 · 总结与展望（Ch15–17）

---

## 第 15 章 · Concluding Remarks（总结:RKHS 统一四大领域）

- **核心**:收束全书主线——**RKHS 是核方法的通用语言**。SVM 分类、SVR 回归、KPCA 无监督、RVM 贝叶斯、tangent 不变性,在 RKHS 中都化为同一形式「$\min$ 损失 + $\lambda\|f\|_\mathcal H^2$」+ 表示定理的有限维解。核方法的胜利在于:把「设计特征」(人工特征工程)换成「设计核」(相似性函数),让非线性方法既理论自洽又工程可算。本书的遗产是这一统一视角,它直接孕育了后来的核贝叶斯、高斯过程、核因果推断(MMD/KCM)。

- **飞腾锚点**:**分支预测** 🟡。统一框架的实质是「所有方法走同一条 RKHS 计算路径(核求值→Gram→对偶/特征分解)」,与 CPU 一旦预测中核方法主循环即可高速执行同构——框架统一带来「执行路径统一」。

- **关键定理/公式**:**统一目标** $\min_{f\in\mathcal H}\frac1n\sum c(f(x_i),y_i)+\frac{\lambda}{2}\|f\|_\mathcal H^2$,解 $f^*=\sum_i\alpha_iK(x_i,\cdot)$;换损失 $c$ 即换方法(合页→SVM、$\varepsilon$-insensitive→SVR、平方→RVM/正则化网络)。

- **自测**:用「损失 $c$ + 表示定理」一句话解释为何 SVM、SVR、RVM 共享同一个 $f^*=\sum\alpha_iK_i$ 解结构?(答:三者都是 RKHS 中 Tikhonov 正则化经验风险最小,由表示定理,解必为样本核函数的有限线性组合;只损失不同→$\alpha$ 不同,结构相同。)

---

## 第 16 章 · Open Problems（开放问题:核学习、多核、半监督）

- **核心**:指明 2002 年后核方法的研究前沿。① **核学习(multiple kernel learning, MKL)**:多个候选核 $K_1,\dots,K_m$ 如何最优凸组合 $K=\sum\beta_jK_j$($\beta_j\geq0,\sum\beta_j=1$)——把核选择本身变成优化问题。② **半监督/直推 SVM(TSVM)**:利用无标签样本推最大间隔。③ **大规模核方法**:突破 $O(n^3)$ 的 Nyström/random features/CG 求解。④ **核与因果**:用 RKHS 上的 MMD(Maximum Mean Discrepancy)比较分布、做独立性检验(HSIC),通向核因果发现。这些方向在随后 20 年(2002–2022)大多成为独立领域,MMD/HSIC 尤其影响深远。

- **飞腾锚点**:**Schmidt 正交化** 🟡。多核学习的本质是在多个核子空间中找最优(正交)组合——与 Schmidt 把向量分解到正交基、选最优基组合同构;HSIC 用核正交化度量独立性。

- **关键定理/公式**:**MKL** $\min_{\beta,\alpha}\ \ldots$ s.t. $K=\sum_j\beta_jK_j,\ \beta\in\Delta^m$;**MMD** $\mathrm{MMD}^2[\mathcal F,p,q]=\|\mu_p-\mu_q\|_\mathcal H^2=\sup_{\|f\|_\mathcal H\leq1}(E_pf-E_qf)$($\mu$ 为核均值嵌入)。

- **自测**:MMD 为何能检验两样本是否同分布?它依赖什么核性质?(答:MMD 是两分布在 RKHS 中均值嵌入的距离;特征核(如 RBF)的均值嵌入是**特征的**(单射),同分布⇔MMD=0,故可用经验 MMD 做两样本检验。)

---

## 第 17 章 · Appendix: Miscellaneous（附录:数学补充)

- **核心**:收录支撑正文的数学工具——概率不等式(Hoeffding/McDiarmid,服务于泛化界)、凸优化对偶理论(拉格朗日对偶/KKT,服务于 SVM 推导)、线性代数(谱分解,服务于 Mercer/KPCA)、以及核矩阵的数值稳定性(条件数、Gram 矩阵正定修正)。附录是「快速查阅」性质,正文已基本带过,此处仅作公式手册。

- **飞腾锚点**:**GEMM 9.45G** 🟢。附录的谱分解与对偶求解都是高维矩阵运算;数值稳定性的核心(Gram 条件数、Cholesky 失败时加 jitter)在大规模场景靠 GEMM 级吞吐与 FP64/FP16 混合精度实现。

- **关键定理/公式**:**Hoeffding 不等式** $P(|\hat R-R|\geq\epsilon)\leq 2\exp(-2n\epsilon^2/(b-a)^2)$;**强对偶(Slater)** 凸问题满足约束资格时对偶间隙为零,KKT 充要。

- **自测**:Gram 矩阵 $K$ 数值上出现微小负特征值($-10^{-8}$)时,如何修正以保证 Cholesky 成功?(答:加 jitter $K\gets K+\delta I$($\delta\sim10^{-6}\!\cdot\!\mathrm{tr}(K)/n$)或截断负特征值为 0,保证半正定。)

---

## §9 全书思想主线（约 200 字）

本书的统一主线是:**以 RKHS 为通用语言,把大间隔、正则化、贝叶斯、不变性四大领域合并为「在 Hilbert 空间中定义目标函数」的单一框架。** 具体地:① Mercer 定理保证正定核⇔RKHS+特征映射,使「无穷维特征空间线性可分」可计算(Ch3);② Tikhonov 正则化 + 表示定理把无穷维优化降为样本数维 $\alpha$(Ch4);③ 损失函数 $c$ 一换,同一框架产出 SVM(合页)、SVR($\varepsilon$-insensitive)、RVM(平方+ARD)、KPCA(方差)(Ch6/7/11/12);④ 大间隔与 margin 界把 SRM 从抽象分层变为可计算泛化诊断(Ch2/10)。与已读教材呼应:**Hastie ESL** 给 SVM 的工程路径算法与频率统计框架,**本书**给 SVM 的 RKHS 数学自洽性;**Bishop PRML** 的 RVM/GP 直接源自本书 Ch11;**Murphy MLPP** 的核章节是本书的现代重写;**Cover-Thomas** 的 PCA/熵谱与 Mercer 谱分解同源。本书是「理解一切核方法为何自洽」的母语读本。

---

## §10 与本仓库其他笔记的交叉引用

**与已读教材及其他书的交叉**:

| 本书概念 | 关联书/笔记 | 接口说明 |
|:------|:------|:------|
| RKHS / Mercer / 表示定理 | **Hastie ESL Ch5/12** / **Bishop Ch6(GP)** | 本书给 RKHS 严格基础;ESL 给 SVM 路径算法;Bishop GP 把 RKHS 贝叶斯化 |
| 大间隔 / VC / SRM | **Shalev-Shwartz 理解ML** / **Vapnik SLT** | 本书 Ch2 综述;Shalev-Shwartz 给现代 PAC/Rademacher;Vapnik 原典 |
| $\varepsilon$-SVR / 正则化 | **Hastie ESL Ch3/5** / **Murphy MLPP** | 频率正则化网络;Murphy 把正则化统一为贝叶斯 MAP |
| KPCA / 谱分解 | **Cover-Thomas 信息论** / **Hastie ESL Ch14** | PCA 的核化;Cover-Thomas 的 PCA=最大方差=熵压缩 |
| RVM / ARD / 证据 | **Bishop Ch3/7** | 本书 Ch11 是 Bishop RVM 的源头;证据框架 MacKay |
| MMD / 核均值嵌入(Ch16) | **Wainwright 高维统计** | RKHS 上的两样本/独立性检验;通向核因果发现 |

**AI / 工程锚点**(本书 RKHS → 现代 AI/ML):

- 🟢 **神经正切核 NTK**:无限宽网络在梯度下降下等价于核回归,核 $K_{\text{NTK}}(x,y)=\langleabla_\theta f(x;\theta),abla_\theta f(y;\theta)\rangle$——本书 RKHS/表示定理是 NTK 理论(Jacot 2018)的数学祖宗,「深度网络训练=在 NTK 的 RKHS 中正则化回归」。
- 🟢 **Transformer attention 的核视角**:attention $A=\mathrm{softmax}(QK^\top/\sqrt d)$ 是 **softmax 核**的 Gram 矩阵;Performer/线性 attention 用 random features(Nyström 思想,本书 Ch14)近似,把 $O(n^2)$ attention 降到 $O(n)$——本书的核近似理论是高效 attention 的根。
- 🟢 **GPU/大规模 SVM(ThunderSVM、RAPIDS cuML)**:本书 Ch8 的 SMO+分解方法 + Gram 缓存在 GPU 上以 GEMM 9.45 GFLOPS 并行,百万样本核 SVM 工业可用。
- 🟡 **核近似(Nyström / Random Features,Rahimi-Recht 2007)**:本书 Ch14 提示的 $O(n^3)$ 瓶颈,催生了 random Fourier features($\tilde K$ 无偏估计)与 Nyström 子采样——现代大模型高效核化的基础。
- 🟡 **核因果 / MMD / HSIC**:本书 Ch16 开放的 MMD 方向,发展成 Gretton 等的核两样本检验、HSIC 独立性、核因果发现——连接本书与 Pearl 因果推断。

**飞腾锚点速查**（17 章 · 8 锚点分散覆盖）:

| 锚点 | 章节 | 主题 |
|:------|:------|:------|
| **分支预测** | Ch1, Ch7, Ch15 | 符号分类(引言)+ $\varepsilon$-tube 判断(SVR)+ 统一路径(总结) |
| **Iron Law<2%** | Ch2, Ch11 | SRM 泛化界(理论)+ 证据框架模型选择(贝叶斯) |
| **UDOT 16.9×** | **Ch3⭐**, Ch12 | 核求值点积(RKHS)+ KPCA Gram 特征分解 |
| **Schmidt 正交化** | Ch4, Ch9, Ch16 | 正则化投影(理论)+ tangent 切空间(不变性)+ 多核/MMD(开放) |
| **TLB 4.81×** | Ch5, Ch14 | 单类核行缓存(密度)+ 网格搜索局部性(实践) |
| **matmul 15×** | **Ch6⭐**, Ch13 | SVM 对偶 Gram(SVM)+ 字符串核 DP(核扩展) |
| **GEMM 9.45G** | **Ch8⭐**, Ch17 | 大规模 QP/SMO(实现)+ 谱分解数值稳定(附录) |
| **FP16 3.81×** | Ch10 | margin 界/半径数值估计(理论回顾) |

---

> **下一步**(锁定 A 方向 + ML 理论交叉):精读 Ch3(RKHS/Mercer)+ Ch4(表示定理)+ Ch6(SVM 对偶)+ Ch11(RVM)+ Ch12(KPCA)+ Ch16(MMD)。
> 研究选题「**从 RKHS 到神经正切核:核方法的深度学习延续**」——把本书的表示定理/Tikhonov 正则化与 Jacot 的 NTK 对照,用本书 Ch16 的 MMD/HSIC 工具研究「过参数化网络的隐式正则化=NTK-RKHS 中的 Tikhonov」,正是核方法在 2020s 深度学习中的延续。同时本书 Ch13 的字符串核/注意力核视角,是高效 Transformer 的理论入口。
