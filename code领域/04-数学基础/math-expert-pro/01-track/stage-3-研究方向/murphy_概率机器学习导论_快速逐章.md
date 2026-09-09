# Kevin P. Murphy《概率机器学习：导论》(PML 2022) · 快速逐章精读

> 基于原书 `Probabilistic Machine Learning: An Introduction` (Kevin P. Murphy, MIT Press, 2022, ~850pp)
> · **stage-3 §3B ML 理论方向**, PML 三卷本之 Vol 1（导论），是 2012 年 MLAPP 的现代化换代版。
> 读于：2026-07-03
> 定位：**以「概率论 + 贝叶斯」统一从线性模型到 Diffusion 的 ML 全景**，概率派 ML 的现代百科全书。
> 本文为**快速逐章精读**，全书 ~28 章按 5 大部分整合为 **14 主题**（忠于原书 TOC，精选核心章），
> 每主题 1 个飞腾锚点 + 1 个关键定理 + 1 道自测题。
> 已读本仓库：Bishop PRML、Bishop DL 2024、Murphy MLAPP 2012、Hastie ESL、Mohri、Vapnik、Goodfellow DL、MacKay、Cover-Thomas。

---

## §0 引言：PML 2022 是什么，为什么读它（约 360 字）

Kevin P. Murphy（UBC 教授，Google/DeepMind 研究科学家）在 2022 年把 2012 年的经典 *Machine Learning: A Probabilistic Perspective*（MLAPP）**彻底重写**为三卷本 *Probabilistic Machine Learning*（PML）系列：Vol 1「导论」（本书）、Vol 2「进阶」（Advanced Topics）。本书（~850pp）不再是 MLAPP 的简单修订，而是**用 2020 年代的视角重新组织全部 ML**——从概率公理到 Diffusion 去噪，统一语言始终是「概率论 + 贝叶斯推断」。与 MLAPP 相比最大升级是**全面纳入深度学习**（CNN/Transformer/Diffusion，2012 版几乎空白），并把代码全部迁移到 Python/JAX 生态（提供可运行 notebook）。

定位区分：**Bishop PRML（已读，2006）**是贝叶斯 ML 优雅经典但止于浅层模型；**Bishop DL 2024（已读）**是 PRML 的深度学习续作、更聚焦 DL 架构；**Murphy MLAPP 2012（已读）**覆盖最广但深度学习陈旧。本书站在三者交汇——**比 PRML 更全面现代（含 DL/Diffusion）、比 Bishop DL 更偏概率统计根基（频率派 + 贝叶斯并重）、比 MLAPP 更新更深**。对「应用数学研究型工程师」，PML 是建立「从概率公理到 Stable Diffusion 的完整数学链条」的最佳单书。读法建议：Ch2–3（概率统计地基）+ Ch5（优化）+ Ch9–11（贝叶斯/高斯/核）+ Ch14（深度学习）+ Ch22/24（VAE/Diffusion）精读。

| 书 | 风格 | 严格性 | 适合谁 |
|:--|:--|:--|:--|
| **Murphy PML 导论 2022（本书）** | 概率 + 贝叶斯统一视角，频率/贝叶斯并重，Python/JAX 代码密集 | ★★★★ 全面严谨 | 系统建立「概率→深度学习→生成模型」全谱数学骨架 |
| **Bishop PRML 2006（已读）** | 几何 + 概率，贝叶斯贯穿，推导完整优雅 | ★★★★ 严格系统 | 精读贝叶斯 ML 经典；DL 覆盖浅（早于 AlexNet） |
| **Bishop DL 2024（已读）** | 概率统一视角，bite-sized 章，聚焦深度学习架构 | ★★★☆ 概率严格 | 从 PRML 过渡到 Transformer/Diffusion |
| **Murphy MLAPP 2012（已读）** | 概率百科，伪代码密集，工程感强 | ★★★ 全面但 DL 陈旧 | 学概率派 ML 全谱；2012 年时代局限 |

---

## §1 全书 14 主题骨架一览（飞腾锚点分布表）

本书按「**基础（概率/统计/线代/优化）→ 线性模型 → 贝叶斯与高斯 → 深度网络 → 生成与无监督**」五段递进。全书灵魂：**用概率论这把万能钥匙，把从线性回归到 Diffusion 去噪的全部 ML 模型统一在「建模 → 推断 → 预测」同一框架内**。飞腾锚点池共 8 个，14 主题从中分散复用（隔章不重复，标不同角度）。

- **第一段 基础（主题 1–5）**：概率公理 → 统计估计 → 线性代数 → 优化。**UDOT⭐熵 / Schmidt⭐分解**。
- **第二段 线性模型（主题 6–8）**：回归 → 分类 → GLM 统一。**matmul 正规方程 / 分支预测决策**。
- **第三段 贝叶斯与高斯（主题 9–11）**：后验分布 → GP/SVM 核方法。**GEMM⭐核矩阵**。
- **第四段 深度网络（主题 12–13）**：反向传播 → CNN/Transformer。**GEMM⭐大模型训练**。
- **第五段 生成与无监督（主题 14）**：EM/VAE/GAN/Diffusion/RL。**FP16⭐混合精度**。

| 主题 | 原书章 | 核心概念 | 飞腾锚点 |
|:-:|:------|:------|:------|
| 1 | Ch1 引言 | ML 范式、偏差-方差、泛化 | Iron Law<2% 🟡 |
| 2 | Ch2 概率 | 贝叶斯定理、分布、KL 散度 | UDOT 16.9× 🟢⭐ |
| 3 | Ch3 统计 | MLE/MAP、Cramér-Rao、Bootstrap | matmul 15× 🟢 |
| 4 | Ch4 线性代数 | SVD、特征分解、低秩近似 | Schmidt 正交化 🟢⭐ |
| 5 | Ch5 优化 | 梯度下降、SGD、凸优化、Jensen | Iron Law<2% 🟢 |
| 6 | Ch6 线性回归 | 最小二乘、Ridge/Lasso、正规方程 | matmul 15× 🟢 |
| 7 | Ch7 逻辑回归 | softmax、交叉熵、最大熵 | 分支预测 🟡 |
| 8 | Ch8 广义线性模型 | 指数族、链接函数、GLM | UDOT 16.9× 🟢 |
| 9 | Ch9 贝叶斯线性回归 | 先验/后验/证据、模型选择 | Schmidt 正交化 🟡 |
| 10 | Ch10 高斯模型 | 多元高斯、GP、PPCA | matmul 15× 🟢 |
| 11 | Ch11 SVM 与核方法 | 最大间隔、核技巧、RKHS | GEMM 9.45G 🟢⭐ |
| 12 | Ch13 神经网络 | 反向传播、万有逼近、激活 | 分支预测 🟢 |
| 13 | Ch14 深度学习 | CNN/RNN/Transformer、Adam | GEMM 9.45G 🟢⭐ |
| 14 | Ch20/22/23/24/25 生成与无监督 | EM/VAE/GAN/Diffusion/RL | FP16 3.81× 🟢⭐ |

> 🟢 = 直接锚定（概念↔硬件对应）/ 🟡 = 类比锚点（供直觉）/ ⭐ = 该段主锚点。14 主题 > 8 锚点，允许隔章复用标不同角度。

---

# Part I · 基础（主题 1–5）—— 概率统计 + 线代 + 优化，四块地基

**本段锚点：UDOT⭐熵 / Schmidt⭐分解 / Iron Law 收敛** —— 概率似然求和 = 点积加速；线性代数的正交分解；优化收敛的误差铁律。

---

## 主题 1 · Ch1 Introduction（导论）

- **核心**：Murphy 用「多项式曲线拟合」一例贯穿全书引子，定义 ML 三大范式，预告频率派与贝叶斯派之争。

  ① 监督学 $p(y|\mathbf{x})$，无监督学 $p(\mathbf{x})$，强化学序贯决策最大化累积奖励。
  
  ② **偏差-方差权衡**（Bias-Variance Tradeoff）：复杂模型偏差小但方差大（过拟合），简单模型反之。
  
  ③ **泛化能力** = 未见数据上的表现，是 ML 终极目标；过拟合 = 训练好但测试差。
  
  ④ Murphy 强调「不确定性无处不在」，概率论是处理它的唯一数学语言。

- **飞腾锚点**：Iron Law<2%[Lab00] 🟡。偏差-方差分解刻画泛化误差结构——总误差 = 偏置² + 方差 + 噪声，与 Iron Law「性能 = 指令数 × CPI × 时钟」分解思想同构：各分量独立可控，总误差逼近最优须协同下降。
- **关键定理**：**偏差-方差分解** $E[(y-\hat{f}(x))^2]=\underbrace{(E[\hat{f}]-f)^2}_{\text{Bias}^2}+\underbrace{E[(\hat{f}-E[\hat{f}])^2]}_{\text{Var}}+\underbrace{\sigma^2}_{\text{噪声}}$。
- **自测**：模型复杂度从低到高增加时，偏差和方差各如何变化？（偏差↓、方差↑；总误差先降后升，U 形曲线。）

---

## 主题 2 · Ch2 Probability（概率）⭐⭐ 全书地基

- **核心**：概率论是全书「操作系统」，本章建立后续所有概率推导的锚点。

  ① **概率公理**（Kolmogorov：非负/规范/可列可加）→ 加法/乘法法则 → **贝叶斯定理**。
  
  ② **频率派**（概率 = 长期频率）vs **贝叶斯派**（概率 = 不确定性度量）诠释之辨——Murphy 两者并重，这是本书与纯贝叶斯 Bishop PRML 的关键区别。
  
  ③ 常见分布（Bernoulli/Binomial/Multinomial/Gamma/Beta/高斯/均匀）。
  
  ④ **信息论**工具：熵 $H$、**KL 散度**、互信息——成为后续损失函数与模型比较的统一度量。
  
  ⑤ 协方差、相关与条件独立。

- **飞腾锚点**：**UDOT 16.9×[E05]** 🟢⭐（本段主锚点）。对数似然 $\log p(\mathcal{D}|\boldsymbol\theta)=\sum_n\log p(x_n|\boldsymbol\theta)$ 是逐样本加权求和 = 点积；KL 散度 $D_{KL}=\sum p\log(p/q)$ 也是点积累加——UDOT 加速批量似然与散度评估（接续 Cover-Thomas Ch2）。
- **关键定理**：**贝叶斯定理** $p(\boldsymbol\theta|\mathcal{D})=\dfrac{p(\mathcal{D}|\boldsymbol\theta)\,p(\boldsymbol\theta)}{p(\mathcal{D})}$；**KL 散度** $D_{KL}(p\|q)=\sum_x p(x)\ln\dfrac{p(x)}{q(x)}\ge 0$（Gibbs 不等式）；**链式法则** $p(x_{1:n})=\prod_i p(x_i|x_{1:i-1})$。
- **自测**：为什么贝叶斯定理是「从数据更新信念的唯一相容规则」？（Cox 定理：任何合理信念更新系统必等价于概率的贝叶斯更新。）

---

## 主题 3 · Ch3 Statistics（统计）

- **核心**：从概率（已知模型算数据）翻转到统计（已知数据估模型），本章是频率派统计完整工具箱。

  ① **最大似然估计（MLE）** $\hat\theta_{ML}=\arg\max_\theta\sum_n\log p(x_n|\theta)$——频率派点估计基石，渐近正态。
  
  ② **最大后验（MAP）**= MLE + 先验正则（贝叶斯与频率的桥梁）。
  
  ③ **充分统计量**（Fisher-Neyman）与 **Fisher 信息矩阵** $I(\theta)=-E[\partial^2\log p/\partial\theta^2]$。
  
  ④ **Cramér-Rao 下界**：任何无偏估计方差有下限 $1/(nI)$。
  
  ⑤ 假设检验（p 值）、**Bootstrap** 重采样、模型选择（CV/AIC/BIC）。

- **飞腾锚点**：matmul 15×[V03] 🟢。协方差矩阵估计 $\hat\Sigma=\frac1n\sum(\mathbf{x}_i-\bar{\mathbf{x}})(\mathbf{x}_i-\bar{\mathbf{x}})^\top$ 是矩阵外积累加；Fisher 信息 = Hessian 期望——全部矩阵乘法，matmul 加速。
- **关键定理**：**MLE 渐近正态** $\sqrt{n}(\hat\theta_{ML}-\theta)\xrightarrow{d}\mathcal{N}(0,\,I(\theta)^{-1})$；**Cramér-Rao 下界** $\text{Var}(\hat\theta)\ge\dfrac{1}{n\,I(\theta)}$。
- **自测**：MLE 与 MAP 的区别？先验均匀时关系？（MAP = MLE + $\log p(\theta)$；先验均匀 → MAP = MLE。L2 = 高斯先验 MAP，L1 = Laplace 先验 MAP。）

---

## 主题 4 · Ch4 Linear Algebra（线性代数）⭐ 工具箱

- **核心**：ML 的「线性变换语言」，后续所有模型（回归/分类/PCA/GP/NN）的矩阵工具。

  ① **特征分解** $A=V\Lambda V^{-1}$（方阵）、**SVD** $A=U\Sigma V^\top$（任意矩阵，最通用最稳定）。
  
  ② **Cholesky** $A=LL^\top$（对称正定，GP/高斯推断必备，比求逆快 2 倍）。
  
  ③ QR 分解（最小二乘数值稳定解，Gram-Schmidt 本质）。
  
  ④ **Woodbury 矩阵求逆引理** $(A+UCV)^{-1}=A^{-1}-A^{-1}U(C^{-1}+VA^{-1}U)^{-1}VA^{-1}$——在线学习/卡尔曼滤波核心。
  
  ⑤ 低秩近似与数值稳定性（条件数 $\kappa=\sigma_{\max}/\sigma_{\min}$）。

- **飞腾锚点**：**Schmidt 正交化** 🟢⭐（本段主锚点）。SVD 列正交性 $U^\top U=I$、QR 分解的 Gram-Schmidt 本质、PCA 正交基——全部追溯到正交化。Murphy 把「投影到最佳子空间」作为几何直觉。
- **关键定理**：**SVD** $A=U\Sigma V^\top$；**Eckart-Young**：截断 SVD 给出最优低秩近似 $\min_{\text{rank}(B)=k}\|A-B\|_F=\sqrt{\sum_{i>k}\sigma_i^2}$；**Woodbury 引理**见上。
- **自测**：为什么 SVD 给出最优低秩近似而非特征分解？（SVD 适用于任意矩阵，是 Frobenius 范数全局最优；特征分解只对方阵有效。）

---

## 主题 5 · Ch5 Optimization（优化）

- **核心**：训练模型的母算法，本章覆盖一阶/二阶方法与凸优化基础。

  ① **梯度下降** $\theta_{t+1}=\theta_t-\eta\nabla f(\theta_t)$；批量/小批量/**SGD** 权衡（偏差 vs 方差 vs 效率）。
  
  ② **动量** $\mathbf{v}_t=\beta\mathbf{v}_{t-1}+\nabla f$ 加速收敛；**Adam**= 动量 + 自适应学习率（DL 标配）。
  
  ③ 二阶：**牛顿法** $\theta\leftarrow\theta-H^{-1}\nabla f$（Hessian 求逆贵）、拟牛顿（L-BFGS）。
  
  ④ **凸优化**：凸集/凸函数/**对偶**（Lagrange/KKT）——SVM 的数学根基。
  
  ⑤ 非凸挑战：局部极小、鞍点（高维下远多于局部极小）。

- **飞腾锚点**：Iron Law<2%[Lab00] 🟢。凸函数 GD 收敛率 $f(\theta_t)-f^*\le O(1/t)$ 是「铁律」：学习率太大发散、太小慢；Adam 动量帮逃离鞍点——呼应 Iron Law 可控收敛。
- **关键定理**：**Jensen 不等式** $f(E[X])\le E[f(X)]$（$f$ 凸）——ELBO 推导、EM 单调性、变分推断全部依赖；**凸 GD 收敛率** $f(\theta_t)-f^*\le\dfrac{L\|\theta_0-\theta^*\|^2}{2t}$；**KKT** $\nabla f+\sum\lambda_i\nabla g_i=0$。
- **自测**：学习率太大时损失曲线怎样？（震荡甚至发散——梯度爆炸。最优学习率需匹配 loss 曲面曲率。）

---

# Part II · 线性模型（主题 6–8）—— 回归/分类/GLM

**本段锚点：matmul 正规方程 / 分支预测决策边界 / UDOT 指数族** —— 最小二乘矩阵运算、分类路径选择、指数族似然点积。线性模型是理解复杂模型的起点。

---

## 主题 6 · Ch6 Linear Regression（线性回归）

- **核心**：ML 的「Hello World」，从最小二乘到正则化的完整链条。

  ① 线性基函数 $y=\mathbf{w}^\top\phi(\mathbf{x})$；**最小二乘 = 高斯噪声 MLE**，正规方程 $\mathbf{w}=(\Phi^\top\Phi)^{-1}\Phi^\top\mathbf{t}$。
  
  ② 正则化：**Ridge**（L2）闭式解 $\mathbf{w}=(\Phi^\top\Phi+\lambda I)^{-1}\Phi^\top\mathbf{t}$；**Lasso**（L1）无闭式但给稀疏解。
  
  ③ Ridge = 高斯先验 MAP，Lasso = Laplace 先验 MAP——频率与贝叶斯统一。
  
  ④ 几何直觉：最小二乘 = 目标到列空间的正交投影。

- **飞腾锚点**：matmul 15×[V03] 🟢。正规方程 $\Phi^\top\Phi$（$N\times D$ 乘 $D\times N$）、求逆全是矩阵乘；Ridge 只加 $\lambda I$ 再求逆——matmul 是最小二乘硬件肉身。
- **关键定理**：**正规方程** $\mathbf{w}_{ML}=(\Phi^\top\Phi)^{-1}\Phi^\top\mathbf{t}$；**Ridge 解** $\mathbf{w}_{Ridge}=(\Phi^\top\Phi+\lambda I)^{-1}\Phi^\top\mathbf{t}$。
- **自测**：Ridge 与 Lasso 的稀疏性本质区别？（Lasso L1 约束菱形→交点在角→系数精确为零；Ridge L2 约束球→系数缩小但不为零。）

---

## 主题 7 · Ch7 Logistic Regression（逻辑回归）

- **核心**：从回归到分类，核心是「生成 vs 判别」之辨。

  ① **logistic sigmoid** $\sigma(a)=1/(1+e^{-a})$，建模 $p(y=1|\mathbf{x})=\sigma(\mathbf{w}^\top\mathbf{x})$。
  
  ② **交叉熵损失** = 负对数似然，梯度 $\nabla=\Phi^\top(\sigma-\mathbf{y})$（与线性回归同构）。
  
  ③ 多分类 **softmax**；**最大熵原理**：logistic = 约束特征期望下的最大熵分类（接续 Cover-Thomas）。
  
  ④ **IRLS** 求 MLE；生成（建模 $p(\mathbf{x},y)$）vs 判别（直接学 $p(y|\mathbf{x})$）：判别数据效率高。

- **飞腾锚点**：分支预测[Lab02] 🟡。logistic 决策边界 $\sigma(\mathbf{w}^\top\mathbf{x})=0.5$ 把空间二分，推理判 $\mathbf{w}^\top\mathbf{x}$ 符号 = 二路分支预测；softmax argmax 是多路分支选择。
- **关键定理**：**softmax** $p(C_k|\mathbf{x})=\dfrac{\exp(a_k)}{\sum_j\exp(a_j)}$；**交叉熵** $\mathcal{L}=-\sum_n\sum_k t_{nk}\ln y_{nk}$；**最大熵等价**：logistic 回归 = 二类最大熵。
- **自测**：为什么交叉熵比 MSE 更适合分类？（交叉熵梯度 $\propto(\mathbf{y}-\mathbf{t})$ 不含 sigmoid 导数不饱和；MSE 梯度含 $\sigma'$，$|\sigma'|\le0.25$→梯度消失。）

---

## 主题 8 · Ch8 Generalized Linear Models（广义线性模型）

- **核心**：用**指数族**统一所有经典回归，GLM 是「一个框架装下所有分布」的优雅抽象。

  ① **指数族** $p(y|\boldsymbol\eta)=h(y)g(\boldsymbol\eta)\exp(\boldsymbol\eta^\top T(y))$，统一高斯/Bernoulli/Poisson/Gamma。
  
  ② **GLM** 三要素：线性预测 $\eta=\mathbf{w}^\top\mathbf{x}$、链接函数 $g$、指数族分布。
  
  ③ logistic = Bernoulli + logit；**Poisson 回归** = Poisson + log（计数数据）；Probit = 正态 CDF。
  
  ④ MLE 用 IRLS（指数族对数似然凹）；Murphy 强调指数族是「可解析推断」通用语言。

- **飞腾锚点**：UDOT 16.9×[E05] 🟢。指数族对数似然 $\log p=\boldsymbol\eta^\top T(y)-A(\boldsymbol\eta)+\log h(y)$，充分统计量 $T(y)$ 与 $\boldsymbol\eta$ 内积是点积——GLM 批量似然评估全靠点积累加（与主题 2 同构，聚焦 GLM 统一框架）。
- **关键定理**：**指数族** $p(y|\boldsymbol\eta)=h(y)g(\boldsymbol\eta)\exp(\boldsymbol\eta^\top T(y))$；$A'(\eta)=E[T(y)]$（均值），$A''(\eta)=\text{Var}[T(y)]$（方差）；**GLM** $g(\mu)=\mathbf{w}^\top\mathbf{x}$。
- **自测**：Poisson 回归适用于什么场景？链接函数？（计数数据（事件数/点击量）；链接 = log，因 $\lambda>0$ 需 log 变换到 $\mathbb{R}$。）

---

# Part III · 贝叶斯与高斯（主题 9–11）—— 不确定性量化 + 核方法

**本段锚点：Schmidt 贝叶斯投影 / matmul 协方差求逆 / GEMM⭐核矩阵** —— 贝叶斯后验正交结构、高斯协方差运算、核 Gram 矩阵。这是本书区别于纯 DL 教材的核心段。

---

## 主题 9 · Ch9 Bayesian Linear Regression（贝叶斯线性回归）

- **核心**：把线性回归从点估计升级为**完整后验分布**，量化参数不确定性——贝叶斯方法核心优势。

  ① 高斯先验 → 高斯后验 $p(\mathbf{w}|\mathcal{D})=\mathcal{N}(\mathbf{m}_N,\mathbf{S}_N)$（**共轭**！后验仍是高斯）。
  
  ② **预测分布**边际化掉参数，自动给均值 + 方差。
  
  ③ **边际似然（证据）**自动选模型复杂度（**Occam 剃刀**：简单模型先验概率高，复杂模型拟合好，证据自动权衡）。
  
  ④ **经验贝叶斯**（数据估超参）vs 全贝叶斯（超参加先验）；贝叶斯模型平均。

- **飞腾锚点**：Schmidt 正交化 🟡。后验均值 $\mathbf{m}_N=\beta\mathbf{S}_N\Phi^\top\mathbf{t}$ 可视为目标在先验正则化子空间上的**正交投影**——先验定义「偏好方向」，后验是数据力与先验力的投影平衡。
- **关键定理**：后验 $p(\mathbf{w}|\mathcal{D})=\mathcal{N}(\mathbf{m}_N,\mathbf{S}_N)$，$\mathbf{m}_N=\beta\mathbf{S}_N\Phi^\top\mathbf{t}$，$\mathbf{S}_N^{-1}=\alpha I+\beta\Phi^\top\Phi$；**预测方差** $\sigma_N^2(\mathbf{x})=\dfrac1\beta+\phi(\mathbf{x})^\top\mathbf{S}_N\phi(\mathbf{x})$。
- **自测**：贝叶斯回归预测方差在训练点附近大还是远离时大？（训练点附近小——已观测处不确定性低；远离大——外推谨慎。）

---

## 主题 10 · Ch10 Gaussian Models（高斯模型）

- **核心**：高斯分布是 ML「万能近似器」（中心极限 + 共轭封闭性），本章覆盖高斯全谱应用。

  ① **多元高斯**：条件/边缘仍高斯（Schur 补），协方差椭球几何（主轴 = 特征向量）。
  
  ② **高斯判别分析（GDA）**：生成式分类，每类一个高斯——朴素贝叶斯的连续推广。
  
  ③ **PCA/PPCA**：降维 = 协方差特征分解（频率）/ 概率模型（贝叶斯，可自动定维数）。
  
  ④ **高斯过程（GP）**：直接对函数定义高斯过程——贝叶斯核方法旗舰，预测给均值 + 方差。
  
  ⑤ GP 分类需近似（Laplace/EP），因非高斯似然破坏共轭。

- **飞腾锚点**：matmul 15×[V03] 🟢。GP 预测需核矩阵求逆 $\mathbf{K}^{-1}$（Cholesky），$O(N^3)$ 是大 $N$ 瓶颈（引出稀疏 GP）；GDA 协方差估计、PCA 特征分解全是矩阵乘。
- **关键定理**：**GP 预测** $\mu_*=k_*^\top(\mathbf{K}+\sigma^2 I)^{-1}\mathbf{t}$，$\sigma_*^2=k_{**}-k_*^\top(\mathbf{K}+\sigma^2 I)^{-1}k_*$；**边际似然** $\log p(\mathbf{t})=-\frac12\mathbf{t}^\top\mathbf{C}^{-1}\mathbf{t}-\frac12\log|\mathbf{C}|-\frac N2\log2\pi$。
- **自测**：GP 与贝叶斯线性回归（主题 9）关系？（取核 $k=\phi^\top\phi$，GP = 积分掉权重的贝叶斯线性回归 = 无限维特征空间贝叶斯回归。NTK = 无限宽 GP。）

---

## 主题 11 · Ch11 SVM & Kernel Methods（SVM 与核方法）⭐⭐

- **核心**：稀疏性 + 核技巧 = 小数据强基线。Murphy 把 SVM 放在贝叶斯/高斯之后，形成频率派（SVM 间隔）与贝叶斯（GP 后验）的对照。

  ① **SVM**：最大间隔 $\max 2/\|\mathbf{w}\|$，软间隔松弛 $\xi$；对偶后只有**支持向量**系数非零 → 稀疏解。
  
  ② **核技巧**：不显式算 $\phi$，直接定义 $k(\mathbf{x},\mathbf{x}')=\phi^\top\phi$，隐式映射到高维（甚至无限维 RBF）。
  
  ③ **Mercer 定理**：核合法 ⇔ 半正定（Gram 矩阵 PSD）。
  
  ④ **RKHS**（再生核 Hilbert 空间，接续 Schölkopf-Smola）；SVM 输出非概率（合页损失）。

- **飞腾锚点**：**GEMM 9.45G[Lab05]** 🟢⭐（本段主锚点）。核 SVM 的 Gram 矩阵 $\mathbf{K}\in\mathbb{R}^{N\times N}$，$K_{ij}=k(\mathbf{x}_i,\mathbf{x}_j)$，大规模计算 $\mathbf{K}$ 和 SMO 优化全靠 GEMM——SVM 在大数据上的算力瓶颈。
- **关键定理**：**SVM 对偶** $\max_\alpha\sum_n\alpha_n-\frac12\sum_{n,m}\alpha_n\alpha_m y_ny_m k(\mathbf{x}_n,\mathbf{x}_m)$，$0\le\alpha_n\le C$；**间隔泛化界**（接续 Vapnik SLT）：间隔越大 → VC 维越低 → 泛化越好；**Mercer**：$k$ 半正定 ⇔ 存在 $\phi$ 使 $k=\phi^\top\phi$。
- **自测**：核技巧如何避免显式计算高维映射？（直接在原空间算核值等价于特征空间内积，无需构造 $\phi$（可能无限维）。RBF 核 = 无限维。）

---

# Part IV · 深度网络（主题 12–13）—— 反向传播 + Transformer，GEMM⭐ 是肉身

**本段锚点：分支预测⭐ReLU / GEMM⭐Transformer** —— ReLU 稀疏激活 = 分支跳过；注意力大规模 GEMM。本书相对 PRML/MLAPP 的最大升级：全面纳入 2012 年后的深度学习革命。

---

## 主题 12 · Ch13 Neural Networks（神经网络）

- **核心**：通用函数逼近器 + 反向传播让高维参数可学，本章是深度学习前置基础。

  ① 前馈网络 $f(\mathbf{x})=\mathbf{W}^{(L)}\sigma(\cdots\sigma(\mathbf{W}^{(1)}\mathbf{x}))$；权重空间对称性。
  
  ② **反向传播** = 链式法则在计算图上的高效实现：前向记录中间值，反向逆拓扑序回传梯度。
  
  ③ 激活演进：sigmoid → **ReLU** $\max(0,x)$（解决梯度消失）→ GELU/Swish。
  
  ④ **万有逼近定理**（Cybenko/Hornik）：单隐层足够宽即逼近任意连续函数。
  
  ⑤ **深度 > 宽度**：深层用指数级少参数表示某些函数。

- **飞腾锚点**：分支预测[Lab02] 🟢。ReLU $f(x)=\max(0,x)$ 是逐元素「分支」：$x>0$ 通行、$x\le0$ 归零（~50% 神经元静默）。稀疏性带来计算跳过，是 ReLU 比 sigmoid 训练更快的工程原因之一。
- **关键定理**：**反向传播** $\dfrac{\partial\mathcal{L}}{\partial\mathbf{W}^{(\ell)}}=\boldsymbol\delta^{(\ell)}(\mathbf{a}^{(\ell-1)})^\top$，$\boldsymbol\delta^{(\ell)}=(\mathbf{W}^{(\ell+1)})^\top\boldsymbol\delta^{(\ell+1)}\odot\sigma'(\mathbf{a}^{(\ell)})$；**万有逼近**：单隐层逼近任意连续函数；ReLU $\sigma'(x)=\mathbb{1}[x>0]$。
- **自测**：为什么深层网络用 sigmoid 会梯度消失而 ReLU 不会？（$|\sigma'|\le0.25$ 连乘衰减；ReLU 导数 0 或 1，正区间梯度直通。）

---

## 主题 13 · Ch14 Deep Learning（深度学习）⭐⭐

- **核心**：现代深度学习工程化全景，Murphy 在此把 PRML/MLAPP 缺失的现代 DL 全部补齐。

  ① **CNN**：局部连接 + 参数共享 → 平移不变性（im2col 化为 GEMM）。
  
  ② **RNN/LSTM**：序列建模，门控控制长程依赖；$\mathbf{h}_t=f(\mathbf{h}_{t-1},\mathbf{x}_t)$。
  
  ③ **Transformer**：自注意力取代循环，完全并行——2017 年以来 NLP/CV 统一架构。
  
  ④ 正则化：**Dropout**（≈变分推断近似集成）、**BatchNorm/LayerNorm**（稳定训练）。
  
  ⑤ 优化器 **Adam**（动量 + 自适应学习率）；**迁移学习与预训练**（BERT/GPT 范式）。

- **飞腾锚点**：**GEMM 9.45G[Lab05]** 🟢⭐（本段主锚点）。CNN im2col + GEMM、Transformer $QK^\top$（$n\times d$ 乘 $d\times n$）、全连接层——DL 训练/推理核心算力全是 GEMM。GPU/TPU 即巨型 GEMM 引擎；**Flash Attention** 分块 softmax 减少 HBM 读写。
- **关键定理**：**缩放点积自注意力** $\text{Attention}(Q,K,V)=\text{softmax}\!\left(\dfrac{QK^\top}{\sqrt{d_k}}\right)V$；多头 $\text{MultiHead}=\text{Concat}(\text{head}_1,\ldots,\text{head}_h)W^O$；**BatchNorm** $\hat{x}=\dfrac{x-\mu_B}{\sqrt{\sigma_B^2+\epsilon}}$，$y=\gamma\hat{x}+\beta$。
- **自测**：自注意力中除以 $\sqrt{d_k}$ 的作用？（$d_k$ 大时点积方差 $\sim d_k$→softmax 饱和→梯度消失；缩放使方差稳定为 1。）

---

# Part V · 生成与无监督（主题 14）—— EM/VAE/GAN/Diffusion/RL

**本段锚点：FP16 3.81×⭐混合精度生成** —— VAE/GAN/Diffusion 训练涉及双网络或大规模去噪网络，混合精度省内存加速 GEMM。全书高潮：用概率论统一全部生成范式。

---

## 主题 14 · Ch20/22/23/24/25 生成模型与无监督学习（EM / VAE / GAN / Diffusion / RL）⭐⭐⭐

- **核心**：本书的高潮——用概率论统一全部生成范式。本章整合原书 5 章核心：

  **① Ch20 隐变量模型与 EM**：高斯混合（GMM）$p(\mathbf{x})=\sum_k\pi_k\mathcal{N}(\mathbf{x}|\boldsymbol\mu_k,\Sigma_k)$，隐变量 $\mathbf{z}$ one-hot 指派。**EM 算法**：E 步算后验期望、M 步最大化更新参数；EM **单调增**对数似然（等价最小化 KL 到后验）。**K-means** = EM 硬指派特例。

  **② Ch22 变分自编码器（VAE）**：编码器输出 $q(\mathbf{z}|\mathbf{x})=\mathcal{N}(\boldsymbol\mu,\boldsymbol\sigma^2)$，**重参数化** $\mathbf{z}=\boldsymbol\mu+\boldsymbol\sigma\odot\boldsymbol\epsilon$ 使梯度可传播；目标 = 最大化 **ELBO**（Jensen 不等式）= 重构项 − KL 正则项。

  **③ Ch23 生成对抗网络（GAN）**：生成器 $G$ 骗判别器 $D$ 的极小极大博弈；Nash 均衡时 $p_g=p_{data}$；**模式崩溃**问题；**WGAN** 用 Wasserstein 距离改善稳定性。

  **④ Ch24 扩散模型（Diffusion）**：前向逐步加噪 $q(\mathbf{x}_t|\mathbf{x}_0)=\mathcal{N}(\sqrt{\bar\alpha_t}\mathbf{x}_0,(1-\bar\alpha_t)I)$（闭式可跳步）；反向学习去噪网络；训练目标 = 预测噪声（去噪得分匹配）；**DDPM**/Stable Diffusion 潜空间扩散。

  **⑤ Ch25 强化学习（RL）**：MDP / 策略梯度 REINFORCE / Q-learning DQN（接续 Sutton-Barto）；与生成模型联系（**RLHF** 对齐大语言模型）。

- **飞腾锚点**：**FP16 3.81×[L01]** 🟢⭐（本段主锚点）。VAE 编码器+解码器双网络、GAN 交替训练双网络、Diffusion U-Net 需 20–1000 步推理——混合精度（FP16/BF16）省内存加速 GEMM，loss scale 防梯度下溢。重参数化逐元素乘加用 FP16 精度足够，是现代生成模型训练工程标配。

- **关键定理**（三条顶峰）：
  - **VAE 的 ELBO**：$\mathcal{L}_{VAE}=\underbrace{E_{q(\mathbf{z}|\mathbf{x})}[\ln p(\mathbf{x}|\mathbf{z})]}_{\text{重构}}-\underbrace{D_{KL}(q(\mathbf{z}|\mathbf{x})\|p(\mathbf{z}))}_{\text{正则}}$；推导 $\ln p(\mathbf{x})=\mathcal{L}+D_{KL}(q\|p)\ge\mathcal{L}$（**Jensen 不等式**）。
  - **GAN 极小极大**：$\min_G\max_D\;E_{\mathbf{x}\sim p_{data}}[\ln D(\mathbf{x})]+E_{\mathbf{z}\sim p_z}[\ln(1-D(G(\mathbf{z})))]$；最优 $D^*(\mathbf{x})=\dfrac{p_{data}(\mathbf{x})}{p_{data}(\mathbf{x})+p_g(\mathbf{x})}$。
  - **Diffusion 前向**：$q(\mathbf{x}_t|\mathbf{x}_0)=\mathcal{N}\!\left(\sqrt{\bar\alpha_t}\,\mathbf{x}_0,\,(1-\bar\alpha_t)\mathbf{I}\right)$，$\bar\alpha_t=\prod_{s=1}^t\alpha_s$；训练目标 $\mathcal{L}_{simple}=E_{t,\mathbf{x}_0,\boldsymbol\epsilon}\!\left[\|\boldsymbol\epsilon-\boldsymbol\epsilon_\theta(\mathbf{x}_t,t)\|^2\right]$。

- **自测**：VAE 重参数化为什么使梯度可传播？GAN 为什么绕过配分函数？Diffusion 前向为什么有闭式解？（重参数化把随机性外移到 $\boldsymbol\epsilon$，$\boldsymbol\mu,\boldsymbol\sigma$ 路径可微；GAN 用判别器间接比较分布无需配分函数；高斯加噪累积仍高斯，$\bar\alpha_t$ 闭式。）

---

## §9 全书思想主线：概率论统一从线性到 Diffusion（约 230 字）

全书被**一条主线**贯穿（Murphy 核心贡献，从 MLAPP 延续到 PML 并升级）：

> **一切机器学习 = 概率建模 + 统计推断。从线性回归到 Diffusion 去噪，底层都是「指定概率模型 → 推断后验/参数 → 预测」同一框架，统一语言是贝叶斯定理与 KL 散度。**

本书沿五段递进铺满：① **基础**（Ch1–5）建立概率公理、统计估计、线性代数与优化的四块地基；② **线性模型**（Ch6–8）用 MLE + 指数族统一回归/分类/GLM——一切经典模型都是指数族最大似然；③ **贝叶斯与高斯**（Ch9–11）把点估计升级为后验分布，GP/SVM 给出不确定性量化和核方法；④ **深度网络**（Ch12–13）用反向传播 + GEMM 让高维参数可学，Transformer 实现并行序列建模；⑤ **生成模型**（Ch14）四路并进——EM 算隐变量、VAE 用变分（ELBO）、GAN 用博弈、Diffusion 用去噪得分匹配，全部归结为概率推断。

与已读教材呼应：**PRML** 是更优雅精炼的贝叶斯经典（本书比它全面现代）；**Bishop DL 2024** 更聚焦 DL 架构（本书更偏概率统计根基）；**Mohri/Vapnik** 补充 PAC/VC/SRM 的频率派泛化理论。一句话：**Murphy 把概率论这把万能钥匙，把从 $y=\mathbf{w}^\top\mathbf{x}$ 到 Stable Diffusion 的全部 ML 模型，统一在「建模 → 推断 → 预测」的同一数学框架内。**

---

## §10 与本仓库其他笔记的交叉引用

| 本书概念 | 关联书 / 领域 | 接口说明 |
|:------|:------|:------|
| 贝叶斯/指数族/KL（Ch2,8） | **[Bishop PRML](bishop_PRML_模式识别与机器学习_快速逐章.md) Ch1–2** | 本书直接继承 PRML 概率地基；[Cover-Thomas](cover_thomas_信息论_快速逐章.md) KL 严格基础 |
| MLE/统计估计（Ch3） | **[Hastie ESL](hastie_统计学习基础ESL_快速逐章.md) Ch2,7** | 频率派统计对照；Cramér-Rao / Bootstrap |
| SVM 间隔/核方法（Ch11） | **[Vapnik SLT](vapnik_统计学习理论_快速逐章.md)** / **[Mohri](mohri_机器学习理论基础_快速逐章.md) Ch6** | 间隔泛化界 = 低 VC 维；[Schölkopf-Smola RKHS](scholkopf_smola_学习核方法_快速逐章.md) |
| 深度学习/Transformer（Ch13–14） | **[Bishop DL 2024](bishop_深度学习_快速逐章.md) Ch6,8,12** | 本书更新全面；Bishop DL 更聚焦架构 |
| 生成模型 VAE/GAN/Diffusion（Ch22–24） | **[Bishop DL 2024](bishop_深度学习_快速逐章.md) Ch17–20** / **[Goodfellow DL](goodfellow_深度学习_快速逐章.md)** | ELBO = Jensen；VAE/GAN/Diffusion 同源概率推断 |
| 前作 MLAPP 2012 | **[Murphy MLAPP](murphy_机器学习概率视角_快速逐章.md)** | 本书 = MLAPP 现代化换代（补 DL/Diffusion，Python/JAX） |

**AI / 工程锚点速查**（本书 → 现代 AI/ML 生态的直接映射）：

- 🟢 **PyTorch 全栈 = Ch4–5,13–14 工程化**：`nn.Linear`/`nn.Conv2d` = GEMM 层；`autograd` = 反向传播计算图（Ch13）；`optim.AdamW` = Ch5 优化器；`torch.distributions` = Ch2–3 概率统计。
- 🟢 **Hugging Face Transformers = Ch13 工程化**：`AutoModel`/`Attention` 实现；KV cache 推理加速依赖参数局部加载（TLB 4.81×）；Flash Attention 分块 softmax 减少 HBM 读写。
- 🟢 **Stable Diffusion = Ch24 工程化**：潜空间扩散（VAE 编码 + U-Net 去噪）；多步推理（20–1000 步）大规模 GEMM 消耗；FP16 混合精度训练。
- 🟢 **推荐系统 = Ch6–8 工程化**：logistic 回归 / GLM 是 CTR 预估强基线；矩阵分解（SVD，Ch4）是协同过滤核心；FM/DeepFM 是 GLM + 深度学习组合。
- 🟡 **贝叶斯深度学习 = Ch9–10 延伸**：GP 贝叶斯优化（超参调优）；MC Dropout ≈ 变分推断；不确定性估计用于主动学习 / 安全 AI。

> **注**：本书与 Bishop DL 2024 的关键差异——本书频率派 + 贝叶斯**并重**（Bishop DL 更偏纯贝叶斯），且覆盖更广（含 RL、GP、SVM/核方法、频率派统计）；Bishop DL 更聚焦深度学习架构（含 GNN、Normalizing Flows 独立章）。两书互补，合读可得 2020s ML/DL 全景。
