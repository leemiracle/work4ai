# Kevin P. Murphy《概率机器学习：高级专题》(PML Advanced 2023) · 快速逐章精读

> 基于原书 `Probabilistic Machine Learning: Advanced Topics` (Kevin P. Murphy, MIT Press, 2023, ~1360pp)
> · **stage-3 §3B ML 理论方向**, PML 三卷本之 Vol 2（进阶），与刚做的 Vol 1「导论」合成 **PML 双子书**。
> 读于：2026-07-03
> 定位：**把深度学习放回概率统计的更大语境**，统一「深度生成建模 / 贝叶斯推断 / 图模型 / 强化学习 / 因果」五大前沿。
> 本文为**快速逐章精读**，全书真实 **6 大部分 36 章**按部分整合为 **14 主题**（忠于原书 TOC，标注对应原章号），
> 每主题 1 个飞腾锚点 + 1 个关键定理 + 1 道自测题。
> 已读本仓库：Murphy PML 导论（Vol 1）、Murphy MLAPP 2012、Bishop PRML、Bishop DL 2024、Hastie ESL、Mohri、Vapnik、Goodfellow DL、Sutton-Barto RL、Cover-Thomas、Boucheron 集中不等式。

---

## §0 引言：PML Advanced 是什么，为什么读它（约 370 字）

Kevin P. Murphy 在 2023 年推出 PML 三卷本的 **Vol 2「高级专题」**（~1360pp，比 Vol 1 还厚）。本书的**核心主张**写在扉页：**把深度学习放回更大的统计语境**——不是把 DL 当孤立工程奇迹，而是用概率建模与贝叶斯推断的统一语言，把 VAE/GAN/Diffusion、高斯过程、变分推断、强化学习、因果推断**全部串成一条线**。真实结构是 **6 大部分 36 章**：① Fundamentals（概率/统计/图模型/信息论/优化）→ ② Inference（高斯滤波、消息传递、变分推断、MCMC/SMC）→ ③ Prediction（贝叶斯神经网络、高斯过程）→ ④ Generation（VAE/自回归/流/能量模型/Diffusion/GAN 七章）→ ⑤ Discovery（潜因子/状态空间/图学习/非参贝叶斯）→ ⑥ Action（决策/POMDP、强化学习、因果）。

与**刚做的 Vol 1（导论）**的关系：Vol 1 建立从概率公理到 Diffusion 的**入门全谱**（线性模型、贝叶斯、DL、生成入门），Vol 2 则**纵向深挖推断算法与前沿专题**——GP 的稀疏计算与深度化、变分推断的随机/自然梯度版、MCMC 的 HMC/NUTS、强化学习的策略搜索、因果的 do 演算。两卷**互补**：Vol 1 给广度全景，Vol 2 给深度武器库。读法建议：先 Vol 1 Ch9–10（贝叶斯/高斯地基），再本书 Part II–IV（推断算法 + GP + 生成深度）精读，Part VI（因果）可独立阅读。

| 书 | 风格 | 严格性 | 适合谁 |
|:--|:--|:--|:--|
| **Murphy PML 进阶 2023（本书）** | 概率统一视角，DL↔贝叶斯双向桥接，36 章巨细，Python/JAX 代码 | ★★★★★ 全面深入 | 已读 Vol 1，想深挖推断算法/GP/Diffusion/RL/因果的研究者 |
| **Murphy PML 导论 2022（已读 Vol 1）** | 概率 + 贝叶斯统一，频率/贝叶斯并重，入门全谱 | ★★★★ 全面 | 建立「概率→DL→生成」全谱数学骨架 |
| **Bishop PRML 2006（已读）** | 几何 + 概率，贝叶斯优雅经典，推导完整 | ★★★★ 严格系统 | 贝叶斯 ML 精读；推断章节（EP/变分）本书的先驱 |
| **Bishop DL 2024（已读）** | 概率视角，bite-sized 章，聚焦深度学习架构 | ★★★☆ 概念严格 | 从 PRML 过渡到 Transformer/Diffusion；本书 Part IV 互补 |
| **Sutton-Barto RL 2018（已读）** | RL 经典，MDP→TD→策略梯度，工程直觉 | ★★★★ 系统权威 | 本书 Part VI RL 章的纵深原典 |

---

## §1 全书 14 主题骨架一览（飞腾锚点分布表）

本书按真实 **6 部分 36 章**整合为 14 主题。全书灵魂：**一切 ML = 概率建模 + 推断算法；Vol 1 给「建模」，Vol 2 给「推断」与「前沿专题」的深度武器库**。飞腾锚点池共 8 个，14 主题从中分散复用（隔章不重复，标不同角度）。

- **Part I 基础（主题 1–4）**：概率统计回顾 / 图模型 / 信息论 / 优化。**UDOT⭐熵 / TLB 局部依赖**。
- **Part II 推断（主题 5–8）**：高斯滤波 / 消息传递 / 变分推断 / MCMC·SMC。**Schmidt 投影 / UDOT 期望 / Iron Law 收敛**。
- **Part III 预测（主题 9–10）**：贝叶斯神经网络 / 高斯过程。**GEMM⭐核矩阵**。
- **Part IV 生成（主题 11–12）**：VAE/流/能量模型 / 自回归·Diffusion·GAN。**FP16⭐混合精度 / GEMM⭐U-Net**。
- **Part V 发现（主题 13）**：潜因子/状态空间/非参贝叶斯。**matmul 协方差**。
- **Part VI 行动（主题 14）**：决策/RL/因果。**分支预测探索-利用**。

| 主题 | 原书章 | 核心概念 | 飞腾锚点 |
|:-:|:------|:------|:------|
| 1 | Ch2–3 | Bayes 后验、指数族、KL 散度、充分统计量 | UDOT 16.9× 🟢⭐ |
| 2 | Ch4 | 有向/无向图、条件独立、d-分离、Markov blanket | TLB 4.81× 🟡 |
| 3 | Ch5 | 熵、互信息、信道容量、率失真 | Iron Law<2% 🟡 |
| 4 | Ch6 | 自然梯度、二阶方法、凸优化深入 | matmul 15× 🟢 |
| 5 | Ch7–8 | 精确推断、Kalman 滤波/平滑、LDS | Schmidt 正交化 🟡⭐ |
| 6 | Ch9 | 和积算法、置信传播、Junction Tree、EP | TLB 4.81× 🟡 |
| 7 | Ch10 | ELBO、平均场、重参数化、随机 VI、自然梯度 VI | UDOT 16.9× 🟢⭐ |
| 8 | Ch11–13 | 重要采样、Metropolis、HMC/NUTS、粒子滤波 | Iron Law<2% 🟢 |
| 9 | Ch16–17 | 贝叶斯神经网络、MC Dropout、深度集成 | GEMM 9.45G 🟢⭐ |
| 10 | Ch18–19 | GP 回归后验、稀疏 GP、深度 GP、分布漂移 | Schmidt 正交化 🟡 |
| 11 | Ch20–21,23–24 | VAE/重参数化、Normalizing Flows、能量模型、得分匹配 | FP16 3.81× 🟢⭐ |
| 12 | Ch22,25–26 | 自回归模型、Diffusion 前向/反向、GAN 极小极大 | GEMM 9.45G 🟢⭐ |
| 13 | Ch27–31 | 潜因子(PCA/GMM)、状态空间(HMM)、非参贝叶斯(DP/CRP) | matmul 15× 🟢 |
| 14 | Ch32–36 | 表示学习、决策/POMDP、策略梯度、因果 do 演算 | 分支预测 🟡 |

> 🟢 = 直接锚定（概念↔硬件对应）/ 🟡 = 类比锚点（供直觉）/ ⭐ = 该段主锚点。14 主题 > 8 锚点，允许隔章复用标不同角度。

---

# Part I · 基础（主题 1–4）—— 概率统计 + 图模型 + 信息论 + 优化的高级地基

**本段锚点：UDOT⭐熵 / TLB 局部依赖 / matmul 自然梯度** —— 这 5 章是 Vol 1 同名章的「进阶版」，为后续推断算法铺地基。

---

## 主题 1 · Ch2–3 Probability & Statistics（概率统计回顾）

- **核心**：Vol 1 已详讲，此处是「进阶视角」回顾，聚焦后续推断算法要用的工具。

  ① **贝叶斯后验** $p(\theta|\mathcal{D})\propto p(\mathcal{D}|\theta)p(\theta)$ 是全书「推断」的根——Vol 2 大量篇幅就是「后验算不出来怎么办」（VI/MCMC）。
  
  ② **指数族** $p(x|\eta)=h(x)\exp(\eta^\top T(x)-A(\eta))$：共轭先验使后验有闭式（高斯/Beta/Dirichlet），是精确推断的基础。
  
  ③ **充分统计量**（Fisher-Neyman）与 **Fisher 信息** $I(\theta)=-E[\nabla^2\log p]$：自然梯度与 Laplace 近似的根基。
  
  ④ **KL 散度** $D_{KL}(p\|q)$：变分推断的最小化目标、EM 单调性、生成模型比较的统一度量。

- **飞腾锚点**：**UDOT 16.9×[E05]** 🟢⭐。对数似然 $\sum_n\log p(x_n|\theta)$ 与 KL 散度 $\sum_x p\log(p/q)$ 全是逐项加权求和 = 点积累加——后续 ELBO 的 Monte Carlo 估计、MCMC 的接受比计算都靠点积（接续 Vol 1 主题 2）。
- **关键定理**：**贝叶斯后验** $p(\theta|\mathcal{D})=\dfrac{p(\mathcal{D}|\theta)p(\theta)}{\int p(\mathcal{D}|\theta')p(\theta')d\theta'}$；**KL 散度** $D_{KL}(p\|q)=\sum_x p(x)\ln\dfrac{p(x)}{q(x)}\ge 0$（Gibbs 不等式，等号当 $p=q$）；**Fisher 信息** $I(\theta)=-E_{x\sim p}\!\left[\dfrac{\partial^2\log p(x|\theta)}{\partial\theta^2}\right]$。
- **自测**：为什么高斯似然 + 高斯先验的后验仍是高斯？（指数族 + 共轭先验：$A(\eta)$ 的凸性保证后验仍在同族内。）

---

## 主题 2 · Ch4 Graphical Models（图模型）

- **核心**：用图编码「变量间的条件独立结构」，是高效推断的几何基础。

  ① **有向图（贝叶斯网络 BN）**：$p(x_{1:n})=\prod_i p(x_i|\text{pa}_i)$，因子分解沿有向边。
  
  ② **无向图（马尔可夫随机场 MRF）**：$p(x)=\frac1Z\prod_c\psi_c(x_c)$，配分函数 $Z$ 难算（引出后续推断）。
  
  ③ **d-分离**：图上判别条件独立的算法——给定集 $Z$ 阻断所有路径 ⇔ $X\perp Y|Z$。
  
  ④ **Markov blanket**：一个节点的「信息屏蔽集」= 父节点 + 子节点 + 共父节点；给定 blanket，该节点与其余条件独立——这是消息传递「只需邻居」的根源。

- **飞腾锚点**：**TLB 4.81×[E04]** 🟡。Markov blanket 保证「推断只需局部邻居信息」= 算法的**局部性**，与 TLB「数据局部性好则缓存命中高」同构：稀疏图 → 消息局部传播 → 缓存友好 → 推断快；稠密全连接图 → 退化成全局耦合 → 缓存失效。
- **关键定理**：**因子分解 ⇔ 局部马尔可夫性**（Hammersley-Clifford，正分布下）：$p(x)\propto\prod_c\psi_c(x_c)$ 当且仅当 $X_i\perp \text{其余}|\text{Markov blanket}(X_i)$。
- **自测**：d-分离中「v-结构（head-to-head）$X\to Z\leftarrow Y$」为何默认 $X\perp Y$，但给定 $Z$ 反而变相关？（.collider：观测到共同效果暴露了原因间的依赖——解释 Away 效应。）

---

## 主题 3 · Ch5 Information Theory（信息论）

- **核心**：信息论度量贯穿后续生成模型与推断——熵定义「不确定性」，互信息定义「依赖」，率失真定义「压缩-质量权衡」。

  ① **熵** $H(X)=-\sum p\log p$：均匀分布熵最大（最不确定）。
  
  ② **互信息** $I(X;Y)=H(X)-H(X|Y)=D_{KL}(p(x,y)\|p(x)p(y))$：变量间的依赖量；**Infomax 原则**（最大化输入输出互信息）是表示学习的目标。
  
  ③ **信道容量** $C=\max_{p(x)}I(X;Y)$（接续 Cover-Thomas）；**率失真** $R(D)=\min I(X;\hat X)$ s.t. $E[d]\le D$：压缩率与失真的最优权衡曲线。
  
  ④ **信息瓶颈**（Tishby）：表示 $Z$ 在「压缩 $I(X;Z)$」与「保留 $I(Z;Y)$」间取舍——深度学习泛化的信息论视角。

- **飞腾锚点**：Iron Law<2%[Lab00] 🟡。率失真函数 $R(D)$ 是「编码率 vs 失真」的**最优权衡曲线**，与 Iron Law「性能 = 指令数 × CPI × 时钟」的可分解约束同构：编码率（比特数）与失真（误差）不可同时任意小，存在理论下界——正如性能各分量有物理下限。
- **关键定理**：**互信息** $I(X;Y)=D_{KL}(p(x,y)\|p(x)p(y))\ge 0$；**数据处理不等式** $I(X;Z)\le I(X;Y)$（马尔可夫链 $X\to Y\to Z$ 中后处理不增信息）；**率失真** $R(D)=\min_{p(\hat x|x):E[d]\le D}I(X;\hat X)$。
- **自测**：数据处理不等式为什么说「后处理不能增加信息」？（马尔可夫链 $X\to Y\to Z$，$Z$ 只依赖 $Y$，对 $X$ 的任何信息必经 $Y$，故 $I(X;Z)\le I(X;Y)$。）

---

## 主题 4 · Ch6 Optimization（优化进阶）

- **核心**：Vol 1 讲了 GD/Adam，本章补**自然梯度、二阶方法、凸优化深入**——VI 和 GP 训练的核心工具。

  ① **自然梯度** $\theta\leftarrow\theta-\eta F^{-1}\nabla\mathcal{L}$：用 Fisher 信息 $F$ 修正参数空间的「曲率」，使更新在**概率分布空间**而非参数空间等距——KL 散度下的最速下降。
  
  ② **二阶方法**：牛顿法用 Hessian、Gauss-Newton 用外积近似；trust-region 控制步长。
  
  ③ **凸优化**：强凸/强光滑的收敛率 $O(1/t)$ vs $O(1/t^2)$（Nesterov 加速）；对偶理论（Lagrange/KKT）。
  
  ④ **非凸**：鞍点（高维下远多于局部极小）、Plateau、escape dynamics。

- **飞腾锚点**：matmul 15×[V03] 🟢。自然梯度需 Fisher 矩阵逆 $F^{-1}$（$D\times D$ 矩阵求逆），二阶方法需 Hessian——全部矩阵运算。K-FAC 近似用 Kronecker 分解降低求逆代价，仍是分块 matmul。
- **关键定理**：**自然梯度** $\Delta\theta=-\eta F(\theta)^{-1}\nabla_\theta\mathcal{L}$，$F=E[\nabla\log p\,\nabla\log p^\top]$；**凸 GD 收敛** $f(\theta_t)-f^*\le\dfrac{L\|\theta_0-\theta^*\|^2}{2t}$；**Nesterov 加速**达 $O(1/t^2)$。
- **自测**：自然梯度比普通梯度好在哪？（普通 GD 在曲率各向异性时震荡；自然梯度用 Fisher 预条件，在分布空间均匀步进，VI 中显著加速收敛。）

---

# Part II · 推断（主题 5–8）—— 后验算不出来怎么办：精确/变分/MC 四大武器

**本段是本书相对 Vol 1 的最大增量**：Vol 1 的贝叶斯章假设后验可解析（共轭），Vol 2 正面解决「后验不可解析」这一核心难题。**本段锚点：Schmidt 投影 / UDOT 期望 / Iron Law 收敛**。

---

## 主题 5 · Ch7–8 Inference Overview & Gaussian Filtering/Smoothing（推断总览与高斯滤波）

- **核心**：推断分「精确」（只对特殊图结构可行）与「近似」（VI/MC/确定性）。高斯滤波是**精确推断在序列模型上的最优闭式解**。

  ① **精确推断**：变量消除（VE）、和积算法——对树结构精确，对含环结构需近似。
  
  ② **线性动力系统（LDS）**：状态 $z_t=Az_{t-1}+w$，观测 $x_t=Cz_t+v$，全高斯 → 后验有闭式。
  
  ③ **Kalman 滤波**：递归两步——预测 $\hat z_{t|t-1}=A\hat z_{t-1}$，更新用新观测修正。**Kalman 增益** $K_t$ 自动权衡预测与观测的不确定性。
  
  ④ **RTS 平滑**：用未来信息反推过去（backward pass），得比滤波更准的估计——「后见之明」。

- **飞腾锚点**：**Schmidt 正交化** 🟡⭐。Kalman 更新本质是**正交投影**：新估计 = 旧估计 + 沿「新息（innovation）正交方向」的修正。新息 $e_t=x_t-C\hat z_{t|t-1}$ 与历史正交，投影到它上更新——与 Gram-Schmidt 逐正交分量修正同构。
- **关键定理**：**Kalman 滤波** 预测 $\hat z_{t|t-1}=A\hat z_{t-1|t-1}$，$P_{t|t-1}=AP_{t-1}A^\top+Q$；更新 $K_t=P_{t|t-1}C^\top(CP_{t|t-1}C^\top+R)^{-1}$，$\hat z_{t|t}=\hat z_{t|t-1}+K_t(x_t-C\hat z_{t|t-1})$。
- **自测**：Kalman 增益在观测噪声 $R$ 很大时趋于多少？（趋于 0——观测不可信，只信预测；反之 $R\to0$ 则 $K\to C^{-1}$，完全信观测。）

---

## 主题 6 · Ch9 Message Passing（消息传递算法）

- **核心**：把推断转化为图上的「消息流动」，是精确推断（树）与近似推断（环）的统一框架。

  ① **和积算法（Sum-Product）**= 置信传播（BP）：节点向邻居传「我对外面世界的信念」$m_{i\to j}(x_j)=\sum_{x_i}\psi_{ij}\psi_i\prod_{k\in N(i)\setminus j}m_{k\to i}$。对**树**精确收敛，对**含环图**迭代近似（Loopy BP）。
  
  ② **最大积算法（Max-Product）**：把求和换成取 max → MAP 推断（最可能配置），Viterbi 是其在 HMM 链上的特例。
  
  ③ **Junction Tree**：把任意图三角化成簇树，簇间消息传递——精确但簇大小 = treewidth，可能指数爆炸。
  
  ④ **期望传播（EP）**：用矩匹配局部近似，比 Loopy BP 常更准（接续 Bishop PRML Ch10）。

- **飞腾锚点**：**TLB 4.81×[E04]** 🟡。消息传递的效率取决于图的**稀疏性**：稀疏图邻居少 → 消息局部 → 缓存命中高 → TLB 友好；消息只需邻居不需全局，是「局部性」的算法体现。
- **关键定理**：**和积消息** $m_{i\to j}(x_j)=\sum_{x_i}\psi_{ij}(x_i,x_j)\psi_i(x_i)\prod_{k\in N(i)\setminus j}m_{k\to i}(x_i)$；树结构下边际 $b(x_i)\propto\psi_i\prod_{k\in N(i)}m_{k\to i}$ **精确**。
- **自测**：Loopy BP 为什么在含环图上不一定收敛？（环上消息无限循环传播，无终止条件；但实践中常收敛到好的近似，特别在弱耦合图上。）

---

## 主题 7 · Ch10 Variational Inference（变分推断）⭐⭐ 本书核心章

- **核心**：把「算后验」转化为「优化一个简单分布 $q$ 去逼近后验 $p$」，是处理不可解析后验的**优化范式**（区别于 MCMC 的采样范式）。

  ① **ELBO（证据下界）**：由 Jensen 不等式 $\log p(x)=\mathcal{L}+D_{KL}(q\|p(z|x))\ge\mathcal{L}$；最大化 ELBO ⇔ 最小化 $q$ 与真后验的 KL。
  
  ② **平均场（Mean-Field）**：假设 $q(z)=\prod_i q_i(z_i)$（完全分解），闭式坐标上升——经典 VI（接续 Bishop PRML Ch10）。
  
  ③ **重参数化技巧** $\mathbf{z}=\boldsymbol\mu+\boldsymbol\sigma\odot\boldsymbol\epsilon$，$\epsilon\sim\mathcal{N}(0,I)$：把随机性外移，使梯度可反向传播到 $\mu,\sigma$——VAE 与随机 VI 的基石。
  
  ④ **随机 VI（SVI）**：小批量 + 自然梯度，scale 到大数据；**Amortized Inference**：用神经网络编码器一次性出所有数据点的 $q$（VAE 思想推广）。

- **飞腾锚点**：**UDOT 16.9×[E05]** 🟢⭐。ELBO 的 Monte Carlo 估计 $\mathcal{L}\approx\frac1S\sum_s\log p(x|z_s)+D_{KL}$ 是批量样本点积累加；SVI 每个小批量的梯度也是点积——VI 训练循环全是点积运算。
- **关键定理**：**ELBO** $\mathcal{L}(\phi)=E_{q_\phi(z|x)}[\log p(x,z)]-E_{q_\phi(z|x)}[\log q_\phi(z|x)]=\underbrace{E_q[\log p(x|z)]}_{\text{重构}}-\underbrace{D_{KL}(q_\phi(z|x)\|p(z))}_{\text{正则}}$；**重参数化梯度** $\nabla_\phi E_{q_\phi}[f(z)]=E_\epsilon[\nabla_z f(z)\nabla_\phi z]$。
- **自测**：为什么 ELBO 最大化等价于最小化 $D_{KL}(q\|p(z|x))$？（$\log p(x)=\mathcal{L}+D_{KL}(q\|p)$，左边 $\log p(x)$ 与 $q$ 无关是常数，故 max $\mathcal{L}$ ⇔ min KL。）

---

## 主题 8 · Ch11–13 Monte Carlo / MCMC / SMC（蒙特卡洛采样族）

- **核心**：用**随机采样**逼近后验——MCMC 是贝叶斯统计的金标准，SMC 处理序列/在线推断。

  ① **Monte Carlo** 基础：$E_{p}[f]\approx\frac1S\sum_s f(z_s)$，方差 $O(1/\sqrt S)$（接续 Vol 1）。
  
  ② **MCMC**：构造马尔可夫链使其平稳分布 = 目标 $p(z)$。**Metropolis-Hastings**：按接受率 $\alpha=\min(1,\dfrac{p(z')q(z|z')}{p(z)q(z'|z)})$ 接受/拒绝；满足**细致平衡**。
  
  ③ **Hamiltonian Monte Carlo（HMC/NUTS）**：引入动量，沿势能曲面「滑行」，远距离高效探索——Stan/PyMC 默认引擎。
  
  ④ **序贯蒙特卡洛（SMC）/ 粒子滤波**：用加权粒子集 $\{w_s,z_s\}$ 表示分布，重采样防止退化——非高斯/非线性状态空间（主题 5 的推广）的利器。

- **飞腾锚点**：Iron Law<2%[Lab00] 🟢。MCMC 的核心是**收敛诊断**：burn-in、混合时间、有效样本量——全部是「误差是否控制在阈值内」的铁律问题。步长太大（HMC）→ 接受率低 → 混合差；太小 → 随机游走慢——与 GD 学习率同构的可控收敛。
- **关键定理**：**细致平衡** $p(z)T(z\to z')=p(z')T(z'\to z)$ 保证平稳分布为 $p$；**MH 接受率** $\alpha=\min\!\left(1,\dfrac{p(z')q(z|z')}{p(z)q(z'|z)}\right)$；**粒子滤波**权重 $w_t^{(s)}\propto w_{t-1}^{(s)}p(x_t|z_t^{(s)})$。
- **自测**：HMC 为什么比随机游走 MH 高效？（HMC 用梯度信息沿等势能线滑行，可大步移动仍高接受率；随机游走 MH 步长受维度诅咒限制，高维几乎不移动。）

---

# Part III · 预测（主题 9–10）—— 贝叶斯神经网络 + 高斯过程，不确定性量化的两条路

**本段锚点：GEMM⭐核矩阵 / Schmidt 核空间正交** —— BNN 用网络参数化的先验，GP 直接对函数建模；两者都是「给预测加不确定性」。

---

## 主题 9 · Ch16–17 Deep & Bayesian Neural Networks（深度与贝叶斯神经网络）

- **核心**：给神经网络加不确定性量化——BNN 对权重加先验，深度集成用模型多样性。

  ① **BNN**：权重加先验 $p(w)$，预测 = 边际化后验 $p(y|x,\mathcal{D})=\int p(y|x,w)p(w|\mathcal{D})dw$——后验难算，用 VI（主题 7）或 MC 近似。
  
  ② **MC Dropout**（Gal-Ghahramani）：训练用 Dropout，测试时**保留 Dropout 多次前向**取均值/方差 ≈ 变分推断近似——工程上极简的 BNN。
  
  ③ **深度集成**（Deep Ensemble）：训练 $M$ 个不同初始化的网络，预测取平均——实证上最好的不确定性估计之一（接续主题 9 Vol 1）。
  
  ④ **Last-layer Laplace**：只对最后一层做 Laplace 近似（Hessian 近似后验为高斯）——BNN 的廉价近似。
  
  ⑤ **Scaling Laws / Foundation Models**（Ch16 延伸）：缩放律 $L\propto N^{-\alpha}$（Chinchilla）、涌现能力——大模型的概率视角。

- **飞腾锚点**：**GEMM 9.45G[Lab05]** 🟢⭐。BNN 每次采样权重需一次前向 = 一次 GEMM；MC Dropout 多次前向 = 多次 GEMM；深度集成 $M$ 个网络 = $M$ 倍 GEMM——不确定性量化的算力代价直接是 GEMM 倍数。
- **关键定理**：**BNN 预测** $p(y|x,\mathcal{D})=\int p(y|x,w)p(w|\mathcal{D})dw\approx\frac1S\sum_s p(y|x,w_s)$，$w_s\sim p(w|\mathcal{D})$；**MC Dropout** $\hat y=\frac1T\sum_t f_{\text{drop}}(x;\theta_t)$，方差 = 认知不确定性。
- **自测**：MC Dropout 为什么能近似 BNN？（Dropout 可视为权重的 Bernoulli 变分分布，测试时多次采样 ≈ 从变分后验采样，数学上等价于特定 VI 近似。）

---

## 主题 10 · Ch18–19 Gaussian Processes & Beyond iid（高斯过程与分布漂移）

- **核心**：GP 是「函数空间贝叶斯」——直接对函数定义高斯先验，无需参数化。Vol 1 给入门，本章深入计算与深度化。

  ① **GP 回归**：先验 $f\sim\mathcal{GP}(m,k)$，核 $k$ 编码平滑性。后验**闭式**（高斯似然 + 高斯先验）。
  
  ② **稀疏 GP**：核矩阵求逆 $O(N^3)$ 是瓶颈；引入 $M$ 个**诱导点**（inducing），用 Nyström 近似降到 $O(NM^2)$——大数据 GP 的关键。
  
  ③ **深度 GP**：把 GP 堆叠成层，每层输出喂下一层输入——非参数的深度模型，避免参数计数但难推断。
  
  ④ **GP 分类**：非高斯似然（softmax）破坏共轭，需 EP/VI 近似（主题 6/7）。
  
  ⑤ **Beyond iid（Ch19）**：协变量偏移、概念漂移、领域适应——训练测试分布不同的鲁棒推断；不变预测（因果稳定性的先声，主题 14）。

- **飞腾锚点**：**Schmidt 正交化** 🟡。GP 后验均值 $\mu_*=K_{*X}(K_{XX}+\sigma^2I)^{-1}y$ 是 $y$ 在**核空间正交基**上的投影；Cholesky 分解 $K=LL^\top$ 把核矩阵正交三角化——稀疏 GP 用诱导点选「代表性正交方向」近似全空间。
- **关键定理**：**GP 后验** $\mu_*=K_{*X}(K_{XX}+\sigma^2I)^{-1}\mathbf{y}$，$\Sigma_*=K_{**}-K_{*X}(K_{XX}+\sigma^2I)^{-1}K_{X*}$；**边际似然** $\log p(\mathbf{y})=-\frac12\mathbf{y}^\top K_y^{-1}\mathbf{y}-\frac12\log|K_y|-\frac N2\log2\pi$（自动 Occam 剃刀）。
- **自测**：稀疏 GP 的诱导点为什么能降复杂度？（只对 $M$ 个诱导点算 $M\times M$ 核矩阵求逆 $O(M^3)$，$M\ll N$；测试点通过核与诱导点关联，避开 $N\times N$ 全核矩阵。）

---

# Part IV · 生成（主题 11–12）—— VAE/流/能量模型/Diffusion/GAN 的深度武器库

**全书高潮（7 章）**：用概率统一全部生成范式。Vol 1 给入门，本章深入变分推断与得分匹配的数学。**本段锚点：FP16⭐混合精度 / GEMM⭐U-Net**。

---

## 主题 11 · Ch20–21,23–24 VAE / Normalizing Flows / Energy-Based Models（生成模型 I）

- **核心**：三种「显式密度」生成模型——VAE 近似、流精确可逆、能量模型无归一化。

  ① **VAE**：编码器 $q_\phi(z|x)$ + 解码器 $p_\theta(x|z)$，最大化 ELBO（主题 7 的应用）。**重参数化**使端到端可微；后验坍缩问题。
  
  ② **Normalizing Flows**：可逆变换 $z=f_\theta^{-1}(x)$，密度由变量替换 $\log p(x)=\log p(z)+\log|\det J_f|$——精确似然，但需可逆 + 易算 Jacobian（RealNVP/MAF）。
  
  ③ **能量模型（EBM）** $p(x)=\frac1Z e^{-E_\theta(x)}$：配分函数 $Z$ 难算，用对比散度/Scorescore matching（不归一化也能学）。
  
  ④ **得分匹配**：学 $\nabla_x\log p(x)$（得分函数），绕过 $Z$——Diffusion 的理论基础（主题 12）。

- **飞腾锚点**：**FP16 3.81×[L01]** 🟢⭐。VAE 编码器+解码器双网络、流的串联可逆层、EBM 的 Langevin 采样迭代——全部涉及大规模 GEMM + 多次前向/反向。混合精度（FP16/BF16）省显存加速训练，loss scaling 防梯度下溢，是现代生成模型工程标配。
- **关键定理**：**VAE ELBO** $\mathcal{L}=E_{q_\phi(z|x)}[\log p_\theta(x|z)]-D_{KL}(q_\phi(z|x)\|p(z))$，**重参数化** $z=\mu_\phi+\sigma_\phi\odot\epsilon$；**流密度** $\log p(x)=\log p(f_\theta^{-1}(x))+\log|\det J_{f_\theta^{-1}}|$；**得分匹配** $\min_\theta E[\|\nabla_x\log p_\theta(x)-\nabla_x\log p_{data}(x)\|^2]$。
- **自测**：Normalizing Flows 为什么能算精确似然而 VAE 只能算下界？（流的可逆变换给出闭式密度变换公式，精确；VAE 的 $q$ 是后验近似，$E_q[\log p(x|z)]$ 只是 ELBO 下界。）

---

## 主题 12 · Ch22,25–26 Autoregressive / Diffusion / GAN（生成模型 II）

- **核心**：三种「强大生成器」——自回归逐步生成、Diffusion 反向去噪、GAN 对抗博弈。

  ① **自回归模型** $p(x)=\prod_i p(x_i|x_{1:i-1})$：PixelRNN/PixelCNN（图像）、GPT（文本）——精确似然但慢（逐 token）。
  
  ② **Diffusion 模型**：前向逐步加噪 $q(x_t|x_0)=\mathcal{N}(\sqrt{\bar\alpha_t}x_0,(1-\bar\alpha_t)I)$（闭式可跳步）；反向学去噪网络 $\epsilon_\theta(x_t,t)$ 预测噪声；**DDPM** 训练 = 去噪得分匹配。Stable Diffusion = 潜空间扩散。
  
  ③ **GAN**：生成器 $G$ vs 判别器 $D$ 极小极大博弈；最优 $D^*=\frac{p_{data}}{p_{data}+p_g}$；Nash 均衡时 $p_g=p_{data}$；模式崩溃与 WGAN 改进。
  
  ④ **三者统一**：Diffusion ≈ 退火 Langevin 采样（得分匹配视角）；GAN 与 EBM 的联系（判别器 = 能量分类器）。

- **飞腾锚点**：**GEMM 9.45G[Lab05]** 🟢⭐。Diffusion 的 U-Net 去噪网络需 20–1000 步推理，每步一次 GEMM 密集的前向——Stable Diffusion 生成一张图 = 数十次 U-Net 前向，GEMM 是绝对瓶颈。自回归模型逐 token 生成也是循环 GEMM。
- **关键定理**：**Diffusion 前向** $q(x_t|x_0)=\mathcal{N}(\sqrt{\bar\alpha_t}x_0,(1-\bar\alpha_t)I)$，$\bar\alpha_t=\prod_{s\le t}\alpha_s$；**DDPM 损失** $\mathcal{L}=E_{t,x_0,\epsilon}[\|\epsilon-\epsilon_\theta(\sqrt{\bar\alpha_t}x_0+\sqrt{1-\bar\alpha_t}\epsilon,t)\|^2]$；**GAN 极小极大** $\min_G\max_D E[\log D(x)]+E[\log(1-D(G(z)))]$。
- **自测**：Diffusion 前向为什么有闭式解可跳步？（每步加独立高斯噪声，高斯叠加仍高斯，方差可累加，故 $x_t$ 直接由 $x_0$ + 累积噪声表出，无需逐步。）

---

# Part V · 发现（主题 13）—— 潜变量发现：从聚类到非参数贝叶斯

**本段锚点：matmul 协方差** —— 无监督发现数据隐藏结构：连续潜因子（PCA/因子分析）、离散状态（HMM）、无限混合（Dirichlet 过程）。

---

## 主题 13 · Ch27–31 Discovery: Latent Factors / State-Space / Nonparametric Bayes

- **核心**：「发现」= 从数据中学习隐藏结构，不依赖标签。三系并存——连续潜因子、离散序列状态、无限容量非参。

  ① **潜因子模型**（Ch28）：PCA/PPCA/因子分析 $x=Wz+\epsilon$——线性降维；**混合模型** GMM $p(x)=\sum_k\pi_k\mathcal{N}(\mu_k,\Sigma_k)$ 用 EM（接续 Vol 1 主题 14）。
  
  ② **状态空间模型**（Ch29）：HMM（离散状态）与 LDS（连续状态）的统一——隐状态序列建模时序依赖；前向-后向算法 = 和积算法（主题 6）在链上的特例。
  
  ③ **非参数贝叶斯**（Ch31）：**Dirichlet 过程（DP）** $G\sim\text{DP}(\alpha,H)$ 自动定聚类数；**中国餐馆过程（CRP）** 直观生成；Indian Buffet Process 用于无限特征。从「固定 $K$」到「数据决定复杂度」。
  
  ④ **图学习 / 表示学习**（Ch30,32）：从数据学图结构、学表示——Infomax（主题 3）与对比学习。

- **飞腾锚点**：**matmul 15×[V03]** 🟢。GMM 的协方差估计、PCA 的特征分解、HMM 的转移矩阵运算全是矩阵乘；EM 的 M 步更新 $\Sigma=\frac1N\sum xx^\top$ 是外积累加——matmul 是无监督发现的算力肉身。
- **关键定理**：**DP/CRP** $p(z_n=k|\mathbf{z}_{1:n-1})\propto\begin{cases}n_k & k\le K_{\text{已有}}\\ \alpha & \text{新类}\end{cases}$（富者愈富）；**HMM 前向** $\alpha_t(k)=p(x_{1:t},z_t=k)=[\sum_j\alpha_{t-1}(j)A_{jk}]B_k(x_t)$。
- **自测**：Dirichlet 过程如何自动确定聚类数？（CRP 的「开新桌」概率 $\propto\alpha$，数据越多越可能开新桌，但桌数 $K$ 随 $N$ 对数增长（$E[K]\approx\alpha\log N$），自动平衡复杂度与拟合。）

---

# Part VI · 行动（主题 14）—— 决策 / 强化学习 / 因果：从预测到干预

**全书收尾**：把「预测」升级为「决策与行动」。POMDP 建模部分可观测，RL 序贯优化，因果区分「观察」与「干预」。**本段锚点：分支预测 探索-利用**。

---

## 主题 14 · Ch32–36 Representation / Decision / RL / Causality（行动与因果）

- **核心**：本书把「行动」单列一部分——ML 不只预测，还要在不确定下做最优决策，并理解「因果」而非「相关」。

  ① **决策/POMDP**（Ch34）：部分可观测马尔可夫决策过程——状态不可见只有观测，需**信念状态**（belief state）滤波；最优策略 = 信念上的 MDP 解。
  
  ② **强化学习**（Ch35，接续 Sutton-Barto）：**策略梯度** $\nabla J(\theta)=E_{\tau\sim\pi_\theta}[\nabla_\theta\log\pi_\theta(a|s)\,R(\tau)]$（REINFORCE）；actor-critic 降低方差；PPO/TRPO 用信任域稳定更新；探索-利用权衡（$\epsilon$-greedy / UCB / Thompson 采样）。
  
  ③ **因果**（Ch36）：**结构因果模型（SCM）** 与 **do 演算** $P(Y|do(X=x))\neq P(Y|X=x)$（干预≠观察）；反事实 $Y_{x}$（「假如当时做了 $x$」）；工具变量（IV）、不变预测（IRM）——分布漂移下仍有效的稳定预测（接续主题 10 Ch19）。

- **飞腾锚点**：**分支预测[Lab02]** 🟡。RL 的核心是**探索-利用**：每步在「利用已知最优（预测分支）」与「探索未知（冒险分支）」间抉择 = 条件分支路径选择；POMDP 的信念状态维护是「预测+修正」的序贯决策；因果的 do 干预 = 主动切换分支做反事实实验。
- **关键定理**：**策略梯度** $\nabla_\theta J(\theta)=E_{\tau\sim\pi_\theta}\!\left[\sum_t\nabla_\theta\log\pi_\theta(a_t|s_t)\,G_t\right]$（$G_t$ 回报）；**do 演算** $P(Y|do(X))=\sum_z P(Y|X,z)P(z)$（后门调整）；**反事实** $Y_x=\sum_z f(x,z,U)$。
- **自测**：为什么 $P(Y|do(X=x))\neq P(Y|X=x)$？（观察 $X=x$ 可能因共同原因 $Z$ 导致 $Y$，是相关；干预 $do(X=x)$ 切断进入 $X$ 的边，只保留 $X\to Y$ 的因果效应，排除混杂。）

---

## §9 全书思想主线：把深度学习放回概率统计的更大语境（约 230 字）

全书被**一条主线**贯穿（Murphy 在扉页明示）：

> **深度学习不是孤立工程奇迹，而是概率建模 + 推断算法的特例。本书用「建模 → 推断 → 决策」的统一框架，把 VAE/GAN/Diffusion、高斯过程、贝叶斯网络、强化学习、因果全部串成一条线。**

本书沿六段递进铺满：① **基础**（Ch2–6）回顾概率/图模型/信息论/优化，为推断铺地基；② **推断**（Ch7–13）正面解决「后验算不出来」——Kalman 滤波（精确）、消息传递（树结构）、变分推断（优化近似）、MCMC/SMC（采样近似）四大武器；③ **预测**（Ch14–19）给预测加不确定性——BNN 用网络参数化先验、GP 直接建模函数；④ **生成**（Ch20–26）七章并进——VAE 用变分、流用可逆变换、Diffusion 用去噪得分匹配、GAN 用博弈，全部归结为概率推断；⑤ **发现**（Ch27–33）无监督学隐藏结构——潜因子/状态空间/非参贝叶斯；⑥ **行动**（Ch34–36）从预测升级到决策——POMDP/RL/因果。

与**刚做的 Vol 1**呼应：Vol 1 给「建模全谱」（线性→DL→生成入门），Vol 2 给「推断武器库 + 前沿专题」——两卷合成完整的「概率机器学习」双子书。一句话：**Murphy 用概率论证明，从 Kalman 滤波到 Stable Diffusion、从 AlphaGo 到因果推断，底层都是「指定概率模型 → 推断后验 → 做决策」的同一数学框架。**

---

## §10 与本仓库其他笔记的交叉引用

| 本书概念 | 关联书 / 领域 | 接口说明 |
|:------|:------|:------|
| 变分推断/ELBO（Ch10） | **[PML 导论 Vol 1](murphy_概率机器学习导论_快速逐章.md) 主题 14** / **[Bishop PRML](bishop_PRML_模式识别与机器学习_快速逐章.md) Ch10** | Vol 1 给 ELBO 入门，本书深入平均场/SVI/自然梯度；PRML EP 是先驱 |
| 高斯过程（Ch18） | **[PML 导论 Vol 1](murphy_概率机器学习导论_快速逐章.md) 主题 10** / **[Schölkopf-Smola RKHS](scholkopf_smola_学习核方法_快速逐章.md)** | Vol 1 GP 入门，本书深入稀疏 GP/深度 GP；RKHS 是 GP 的核理论根基 |
| 强化学习（Ch35） | **[Sutton-Barto RL](sutton_barto_强化学习_快速逐章.md)** | 本书 RL 章是 Sutton-Barto 的概率视角浓缩；策略梯度原典在 Sutton-Barto Ch13 |
| 泛化/缩放律（Ch16–17,19） | **[Vapnik SLT](vapnik_统计学习理论_快速逐章.md)** / **[Boucheron 集中不等式](boucheron_集中不等式_快速逐章.md)** | Vapnik VC 维 vs 大模型缩放律；集中不等式给泛化的频率派严格界 |
| 生成模型 Diffusion/GAN（Ch25–26） | **[Bishop DL 2024](bishop_深度学习_快速逐章.md) Ch17–20** / **[PML 导论 Vol 1](murphy_概率机器学习导论_快速逐章.md) 主题 14** | Vol 1 给 Diffusion 入门公式，本书深入去噪得分匹配数学；Bishop DL 架构互补 |

**AI / 工程锚点速查**（本书 → 现代 AI/ML 生态的直接映射）：

- 🟢 **Stable Diffusion = Ch25 工程化**：潜空间扩散（VAE 编码 + U-Net 去噪，主题 11–12 合体）；20–1000 步推理大规模 GEMM；FP16 混合精度训练；去噪得分匹配是数学根基。
- 🟢 **AlphaFold = Ch9–10 工程化**：结构预测的置信度 = BNN/GP 不确定性（主题 9–10）；MSA + Evoformer = 概率图模型（主题 2）的深度版。
- 🟢 **AlphaGo = Ch34–35 工程化**：MCTS + 策略梯度（主题 14）；POMDP 信念状态；探索-利用（分支预测锚点）是围棋搜索的核心。
- 🟢 **GPT-4 / 基础模型 = Ch16,22 工程化**：自回归生成（主题 12）$p(x)=\prod p(x_i|x_{<i})$；缩放律（主题 9）；RLHF 对齐 = 强化学习 + 偏好模型（主题 14 + Vol 1 主题 14）。
- 🟢 **Hugging Face = Ch10,25 工程化**：变分推断库（Pyro）；Diffusion 模型库（diffusers）；KV cache 推理加速依赖 TLB 局部性（主题 6 图模型稀疏性）。
- 🟡 **因果 AI = Ch36 延伸**：do 演算用于 A/B 测试推断、反事实用于推荐系统重排、不变预测用于分布漂移鲁棒性（主题 10 Ch19 + 主题 14）。

> **双子书关系**：本书（Vol 2）与 [PML 导论 Vol 1](murphy_概率机器学习导论_快速逐章.md) 是 Murphy 的「概率机器学习」双子书。Vol 1 = **广度全景**（入门全谱，含 DL/生成入门），Vol 2 = **深度武器库**（推断算法 + 前沿专题）。建议读法：Vol 1 先过一遍建立全谱，再用 Vol 2 按需深挖（推断→Part II、生成→Part IV、RL/因果→Part VI）。两卷合读可得 2020s 概率派 ML 的完整数学图景。
