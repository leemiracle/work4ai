# Christopher M. Bishop & Hugh Bishop《深度学习：基础与概念》 · 快速逐章精读

> 基于原书 `Deep Learning: Foundations and Concepts` (Christopher M. Bishop with Hugh Bishop,
> Springer, 2024, ~649pp, ISBN 978-3-031-45468-4; 伴侣站 bishopbook.com)
> · **stage-3 §3B ML 深化方向**, PRML（2006）的现代升级版——加入深度网络、Transformer、Graph NN、Diffusion。
> 读于:2026-07-03
> 定位:**PRML 的深度学习续作,以「概率统一视角」重写从线性模型到 Diffusion 的全谱**,父子合著、20 章 bite-sized 线性递进。
> 本文为**快速逐章精读**,全书真实 **20 章**（与用户预设 14 章差异较大,以下忠于原书真实 TOC）,
> 每章 1 个飞腾锚点 + 1 个关键定理 + 1 道自测题。已读本仓库:Bishop PRML、Goodfellow DL、Hastie ESL、Mohri ML 理论。

---

## §0 引言：本书是什么，为什么读它（约 380 字）

Christopher M. Bishop（Microsoft Research Cambridge 首席科学家、皇家学会会员）与其子 Hugh Bishop 合著的《Deep Learning: Foundations and Concepts》（Springer, 2024, 649pp）是 **Bishop PRML（2006）的现代升级版**——它把 PRML「一切 ML = 概率推断」的贝叶斯统一视角延伸到深度学习全面框架。全书 **20 章 bite-sized 结构**线性递进：概率地基 → 单层网络 → 深度网络 → 训练优化 → CNN/Transformer/GNN → 采样推断 → 生成模型（VAE/GAN/Flow/Diffusion）。

与同类书的定位区分：**PRML（已读）**止于浅层模型与图模型（2006 早于 AlexNet），本书补上 ReLU/残差/Adam/BatchNorm/Transformer/Diffusion 全部「深度」内容;**Goodfellow DL（已读,2016）**是工程直觉派的 DL 圣经，但不含 Transformer（2017）与 Diffusion（2020），本书更新且更概率化;**Murphy PML（2022）**两卷~1700 页覆盖最全但更偏经典 ML，本书更聚焦深度学习核心架构。**Sutton-Barto RL（已读）**是强化学习权威，本书无 RL 独立章节，二者互补。本书核心优势是**用概率语言（贝叶斯/KL/ELBO）统一解释从交叉熵损失到 Diffusion 去噪的全部 DL 概念**——对「应用数学研究型工程师」而言，这是 PyTorch 工程的数学骨架。读法建议：Ch2–3（分布地基）+ Ch6/8（深度/反向传播）+ Ch12（Transformer）+ Ch19/20（VAE/Diffusion）精读，其余按研究方向选读。

| 书 | 风格 | 严格性 | 适合谁 |
|:--|:--|:--|:--|
| **Bishop & Bishop DL 2024（本书）** | 概率统一视角,bite-sized 章,公式+图+伪代码三路并进 | ★★★☆ 概率严格,工程实用 | 从 PRML 过渡到深度学习;需要 Transformer/Diffusion 数学根基者 |
| **Goodfellow《Deep Learning》2016（已读）** | 工程直觉+概率信息论,三段式 Part I–III | ★★★ 应用驱动,推导适中 | 系统学 DL 全谱;2016 前沿,无 Transformer/Diffusion |
| **Bishop《PRML》2006（已读）** | 几何+概率,贝叶斯贯穿,推导完整 | ★★★★ 严格系统 | 学经典 ML 与贝叶斯框架;DL 覆盖浅（早于 AlexNet） |
| **Murphy《Probabilistic ML》2022** | 概率+矩阵,最全最现代,贝叶斯+频率并蓄 | ★★★★ 全面严谨 | 现代概率 ML 全面参考;~1700 页更偏经典 ML |

---

## §1 全书 20 章骨架一览（飞腾锚点分布表）

本书按「概率地基 → 网络 → 训练 → 架构 → 采样 → 生成」六段递进。全书灵魂：**概率统一视角——从线性回归到 Diffusion 去噪,底层都是贝叶斯推断 + 梯度优化**。飞腾锚点池共 8 个,20 章从中分散复用（隔章不重复,标不同角度）。

| 章 | 标题 | 核心概念 | 飞腾锚点 |
|:-:|------|---------|---------|
| 1 | The Deep Learning Revolution | DL 三要素、贝叶斯框架引入 | TLB 4.81× 🟡 |
| 2 | Probabilities | 贝叶斯定理、熵、KL 散度 | UDOT 16.9× 🟢 |
| 3 | Standard Distributions | 指数族、共轭先验、多元高斯 | matmul 15× 🟢 |
| 4 | Single-layer Networks: Regression | 线性回归、基函数、MLE | Schmidt 正交化 🟢 |
| 5 | Single-layer Networks: Classification | softmax、交叉熵、logistic | 分支预测 🟡 |
| 6 | Deep Neural Networks | 深层网络、残差、万有逼近 | GEMM 9.45G 🟢⭐ |
| 7 | Gradient Descent | SGD、动量、学习率调度 | Iron Law<2% 🟢 |
| 8 | Backpropagation | 链式法则、计算图、激活函数 | 分支预测 🟢⭐ |
| 9 | Regularization | Dropout、BatchNorm、L1/L2、早停 | Schmidt 正交化 🟢 |
| 10 | Convolutional Networks | 卷积、池化、平移不变性 | UDOT 16.9× 🟢 |
| 11 | Structured Distributions | 贝叶斯网、RNN、马尔可夫模型 | TLB 4.81× 🟡 |
| 12 | Transformers | 自注意力、多头、位置编码 | GEMM 9.45G 🟢⭐ |
| 13 | Graph Neural Networks | 消息传递、谱图卷积 | matmul 15× 🟡 |
| 14 | Sampling | 蒙特卡洛、MCMC、拒绝采样 | UDOT 16.9× 🟡 |
| 15 | Discrete Latent Variables | EM、K-means、混合模型 | Iron Law<2% 🟡 |
| 16 | Continuous Latent Variables | PCA、PPCA、变分推断 | matmul 15× 🟡 |
| 17 | Generative Adversarial Networks | GAN 极小极大博弈 | GEMM 9.45G 🟢 |
| 18 | Normalizing Flows | 可逆变换、Jacobian | Schmidt 正交化 🟡 |
| 19 | Autoencoders | VAE、ELBO、重参数化 | FP16 3.81× 🟢 |
| 20 | Diffusion Models | 前向加噪、反向去噪 | GEMM 9.45G 🟢⭐ |

> 🟢 = 直接锚定（概念↔硬件对应）/ 🟡 = 类比锚点（供直觉）/ ⭐ = 该段主锚点。20 章 > 8 锚点,允许隔章复用标不同角度。

---

# Part I · 概率与基础（Ch1–3）—— 贝叶斯操作系统

**本段锚点:UDOT⭐熵 / matmul 协方差** —— 概率分布的对数似然、贝叶斯证据全是点积求和,UDOT 加速;协方差运算全靠 matmul。

---

## 第 1 章 · The Deep Learning Revolution（深度学习革命）

- **核心**:用多项式曲线拟合一例引出全书——频率派最小二乘 → 贝叶斯（先验/边际化），展示 DL 三要素（数据+算力+算法）。区分监督/无监督/强化三大范式，预告全书以概率为统一语言。与 PRML Ch1 高度对应但加入「深度学习革命」的历史叙事（ImageNet 2012 → Transformer 2017 → Diffusion 2020），强调 Bishop 父子选择「聚焦经得起时间考验的思想」而非瞬息万变的工程细节。
- **飞腾锚点**:TLB 4.81×[E04] 🟡。DL 模型以高维权重矩阵存储知识,部署时参数访问的局部性决定推理延迟,TLB 命中率是工程隐性约束——大模型推理的 KV cache 本质是利用时序局部性。
- **关键定理**:**贝叶斯定理** $p(\mathbf{w}|\mathcal{D})=\dfrac{p(\mathcal{D}|\mathbf{w})p(\mathbf{w})}{p(\mathcal{D})}$;预测 $p(t|\mathbf{x},\mathcal{D})=\int p(t|\mathbf{x},\mathbf{w})p(\mathbf{w}|\mathcal{D})\,d\mathbf{w}$。
- **自测**:多项式阶数 $M$ 过高时,频率派 MLE 会怎样?贝叶斯先验如何缓解?（过拟合;先验约束权重大小。）

---

## 第 2 章 · Probabilities（概率）

- **核心**:概率论 = 处理不确定性的数学,本章是全书后续所有概率推导的锚点。

  ① 加法/乘法法则 → **贝叶斯定理**;频率派（概率=长期频率）vs 贝叶斯派（概率=不确定性度量）诠释之辨。
  ② 信息论：熵 $H$、KL 散度、互信息 $I$——成为后续损失函数与模型比较的统一语言。
  ③ 多元分布、变量变换（Jacobian）、Bayesian machine learning 入门。
- **飞腾锚点**:UDOT 16.9×[E05] 🟢。熵 $H=E[-\log p]$、KL 散度 $D=\sum p\log(p/q)$ 都是加权点积;UDOT 点积指令加速批量似然评估（接续 Cover-Thomas Ch2 同构）。
- **关键定理**:**KL 散度** $D_{KL}(p\|q)=\sum_x p(x)\log\dfrac{p(x)}{q(x)}\ge 0$（Gibbs 不等式,等号当且仅当 $p=q$）;**互信息** $I(X;Y)=H(X)-H(X|Y)$;**微分熵** $H(\mathbf{x})=-\int p(\mathbf{x})\ln p(\mathbf{x})\,d\mathbf{x}$。
- **自测**:为什么「最小化交叉熵损失」等价于「最小化 KL 散度」?（$H(p)$ 与参数无关,梯度相同。）

---

## 第 3 章 · Standard Distributions（标准分布）

- **核心**:为贝叶斯推断准备可解析处理的分布族。

  ① Bernoulli/Binomial/Multinomial（离散）;多元高斯（条件/边缘仍高斯、协方差椭球几何）;周期变量（von Mises）。
  ② **指数族**统一所有,充分统计量 + 共轭先验让后验可解析。
  ③ 非参数方法（核密度估计/KNN）。与 PRML Ch2 几乎一一对应。
- **飞腾锚点**:matmul 15×[V03] 🟢。多元高斯协方差矩阵的运算、指数族自然参数的点积 $\boldsymbol\eta^\top\mathbf{u}(\mathbf{x})$ 都是矩阵乘;matmul 加速批量密度评估与协方差估计。
- **关键定理**:**指数族** $p(\mathbf{x}|\boldsymbol\eta)=h(\mathbf{x})g(\boldsymbol\eta)\exp(\boldsymbol\eta^\top\mathbf{u}(\mathbf{x}))$;**共轭**:Beta-Bernoulli 后验 $\text{Beta}(a',b')$,参数加计数即可;多元高斯条件分布仍高斯（Schur 补）。
- **自测**:为什么高斯分布的边缘分布和条件分布仍是高斯?（联合正态的封闭性。）

---

# Part II · 线性与深度网络（Ch4–8）—— 从线性到深度,GEMM⭐ 是肉身

**本段锚点:GEMM 9.45G⭐网络高维 / 分支预测⭐ReLU** —— 深度网络每层前向反向都是 GEMM;ReLU 稀疏激活 = 分支跳过。

---

## 第 4 章 · Single-layer Networks: Regression（单层网络：回归）

- **核心**:线性基函数模型 $y(\mathbf{x},\mathbf{w})=\sum_j w_j\phi_j(\mathbf{x})$,从频率派到贝叶斯的完整跃迁。

  ① 最小二乘 = 高斯噪声 MLE $\mathbf{w}_{ML}=(\Phi^\top\Phi)^{-1}\Phi^\top\mathbf{t}$;序列学习（SGD）处理大数据。
  ② 正则化 Ridge/Lasso;偏置-方差分解刻画泛化权衡。
  ③ **贝叶斯线性回归**：高斯先验→高斯后验（共轭!），预测给均值+方差,自动量化不确定性;证据函数自动选超参。
- **飞腾锚点**:Schmidt 正交化 🟢。最小二乘的几何本质是把目标向量正交投影到基函数张成的列空间——正规方程 $\Phi^\top\Phi\mathbf{w}=\Phi^\top\mathbf{t}$ 即投影方程,与 Gram-Schmidt 同构。这给出了最小二乘「最近点」的直觉。
- **关键定理**:正规方程 $\mathbf{w}_{ML}=(\Phi^\top\Phi)^{-1}\Phi^\top\mathbf{t}$;贝叶斯后验 $p(\mathbf{w}|\mathbf{t})=\mathcal{N}(\mathbf{m}_N,\mathbf{S}_N)$, $\mathbf{m}_N=\beta\mathbf{S}_N\Phi^\top\mathbf{t}$;偏置-方差 $E[(y-t)^2]=\text{Bias}^2+\text{Var}+\sigma^2$。
- **自测**:贝叶斯回归预测方差在训练点附近大还是远?（小——已观测处不确定性低;远离则大,体现外推谨慎。）

---

## 第 5 章 · Single-layer Networks: Classification（单层网络：分类）

- **核心**:三条路通往分类。① 判别函数（Fisher LDA,最大化类间/类内方差比）。② 概率生成模型：对 $p(\mathbf{x}|C_k)$ 建模,贝叶斯得后验,自然引出 logistic sigmoid。③ 概率判别模型：**logistic 回归**直接建模 $p(C_1|\mathbf{x})=\sigma(\mathbf{w}^\top\mathbf{x})$,多类 **softmax**。交叉熵损失 = 负对数似然。生成 vs 判别之辨：生成需建模 $p(\mathbf{x})$（强假设）,判别直接学 $p(C|\mathbf{x})$（数据效率高）。
- **飞腾锚点**:分支预测[Lab02] 🟡。logistic 决策边界 $\sigma(\mathbf{w}^\top\mathbf{x})=0.5$ 二分空间,推理时判 $\mathbf{w}^\top\mathbf{x}$ 符号 = 二路分支预测。softmax 的 argmax 也是多路分支选择。
- **关键定理**:**softmax** $p(C_k|\mathbf{x})=\dfrac{\exp(a_k)}{\sum_j\exp(a_j)}$;**交叉熵损失** $E=-\sum_n\sum_k t_{nk}\ln y_{nk}$;logistic $\sigma(a)=\dfrac{1}{1+e^{-a}}$;Fisher $\mathbf{w}\propto\mathbf{S}_W^{-1}(\mathbf{m}_2-\mathbf{m}_1)$。
- **自测**:在 MNIST 上用 logistic 回归,为什么 softmax 交叉熵比均方误差好?（交叉熵梯度 $\propto(y-t)$ 不饱和;MSE 梯度含 $\sigma'$ 易消失。）

---

## 第 6 章 · Deep Neural Networks（深度神经网络）

- **核心**:从单层到深度——多层仿射变换与非线性激活的复合。

  ① $f(\mathbf{x})=\mathbf{W}^{(L)}\sigma(\cdots\sigma(\mathbf{W}^{(1)}\mathbf{x}))$;**万有逼近定理**：单隐层足够宽即逼近任意连续函数。
  ② 但**深度比宽度更高效**——深层用指数级少的参数表示某些函数（这是「深度」的本质优势）。
  ③ **残差连接** $y=F(x)+x$ 让梯度直通,解决深层梯度消失,使百层千层网络可训练。
- **飞腾锚点**:GEMM 9.45G[Lab05] 🟢⭐。每层前向 $\mathbf{a}^{(\ell)}=\mathbf{W}^{(\ell)}\phi(\mathbf{a}^{(\ell-1)})$ 是矩阵乘;深度网络训练的核心算力消耗全是 GEMM,GPU/TPU 即巨型 GEMM 引擎。残差连接的 identity shortcut 几乎不增加 GEMM 开销。
- **关键定理**:**万有逼近定理**（Cybenko/Hornik）：单隐层（足够多神经元）逼近任意连续函数;**残差** $\mathbf{y}=F(\mathbf{x})+\mathbf{x}$ 使梯度 $\frac{\partial\mathcal{L}}{\partial\mathbf{x}}=\frac{\partial\mathcal{L}}{\partial\mathbf{y}}(I+\frac{\partial F}{\partial\mathbf{x}})$ 含恒等项。
- **自测**:为什么 10 层残差网络比 10 层全连接网络更容易训练?（恒等映射是 $F=0$ 的特例,梯度沿 shortcut 直通。）

---

## 第 7 章 · Gradient Descent（梯度下降）

- **核心**:训练的母算法。批量/小批量/随机梯度下降的权衡（偏差 vs 方差 vs 效率）。学习率调度（预热、余弦退火、one-cycle）。**动量**累积历史梯度加速收敛、冲过鞍点。非凸 landscape 中的挑战：局部极小、鞍点（高维下鞍点远多于局部极小）、平坦区。本章聚焦一阶方法的直觉与调参,为 Ch8 反向传播提供优化语境。
- **飞腾锚点**:Iron Law<2%[Lab00] 🟢。梯度下降收敛是「铁律」：学习率太大发散、太小慢;非凸 landscape 中梯度可能困鞍点。动量通过惯性冲过震荡区,呼应 Iron Law 追求误差可控收敛 $<2\%$。
- **关键定理**:**SGD** $\boldsymbol\theta_{t+1}=\boldsymbol\theta_t-\eta\nabla f(\boldsymbol\theta_t)$;**动量** $\mathbf{v}_t=\beta\mathbf{v}_{t-1}+\eta\nabla f$, $\boldsymbol\theta\leftarrow\boldsymbol\theta-\mathbf{v}_t$;凸函数收敛率 $f(\theta_t)-f^*\le O(1/t)$。
- **自测**:学习率太大时损失曲线会怎样?（震荡甚至发散;梯度爆炸。）

---

## 第 8 章 · Backpropagation（反向传播）

- **核心**:反向传播 = 链式法则在计算图上的高效实现,是 PyTorch/TF 的底层引擎（autograd 数学原理）。

  ① 前向传播记录中间值,反向传播沿计算图逆拓扑序逐层回传梯度 $\boldsymbol\delta^{(\ell)}$。
  ② 激活函数：**ReLU** $\max(0,x)$（解决梯度消失）、Leaky ReLU、**GELU**（GPT/BERT 用）、Swish。
  ③ 计算图自动微分让框架自动求导,工程师只需定义前向——「define-by-run」范式。
- **飞腾锚点**:分支预测[Lab02] 🟢⭐。ReLU $f(x)=\max(0,x)$ 是逐元素「分支」：$x>0$ 通行、$x\le 0$ 归零（稀疏激活）。这正对应 CPU 分支预测——稀疏性带来计算跳过,也是 ReLU 比 sigmoid 训练更快的工程原因。
- **关键定理**:**反向传播（链式法则）** $\dfrac{\partial\mathcal{L}}{\partial\mathbf{W}^{(\ell)}}=\boldsymbol\delta^{(\ell)}(\mathbf{a}^{(\ell-1)})^\top$, 其中 $\boldsymbol\delta^{(\ell)}=(\mathbf{W}^{(\ell+1)})^\top\boldsymbol\delta^{(\ell+1)}\odot\sigma'(\mathbf{a}^{(\ell)})$;ReLU 导数 $\sigma'(x)=\mathbb{1}[x>0]$。
- **自测**:为什么深层网络用 sigmoid 会梯度消失?（$|\sigma'(x)|\le 0.25$,连乘→指数衰减。）

---

# Part III · 训练与架构（Ch9–13）—— Dropout/BatchNorm/CNN/Transformer/GNN

**本段锚点:Schmidt⭐BatchNorm / UDOT⭐卷积 / GEMM⭐Transformer** —— 正则化去相关、卷积滑窗点积、注意力大规模 GEMM。

---

## 第 9 章 · Regularization（正则化）

- **核心**:防止过拟合的武器库,本章是训练深层网络的关键工程。

  ① **参数惩罚**:L2（权重衰减 $\|\theta\|_2^2$）、L1（稀疏 $\|\theta\|_1$）。
  ② **训练时随机化**:Dropout（随机置零神经元,近似集成）、数据增强。
  ③ **归一化**:BatchNorm（标准化每层激活,稳定训练+加速）、LayerNorm（Transformer 标配）。
  ④ **贝叶斯诠释**:L2 = 高斯先验,L1 = Laplace 先验——频率派与贝叶斯派的统一。
- **飞腾锚点**:Schmidt 正交化 🟢。BatchNorm 把每 mini-batch 激活标准化为均值 0、方差 1,类似 Gram-Schmidt 去相关——减少内部协变量偏移,使各层输入分布稳定。这是 ReLU 之后训练深层网络的第二大工程突破。
- **关键定理**:**BatchNorm** $\hat{x}=\dfrac{x-\mu_B}{\sqrt{\sigma_B^2+\epsilon}}$, $y=\gamma\hat{x}+\beta$;**L2 正则目标** $\tilde{J}(\theta)=J(\theta)+\dfrac{\lambda}{2}\|\boldsymbol\theta\|_2^2$;**Dropout** 训练时以概率 $p$ 置零,测试时缩放 $\times(1-p)$。
- **自测**:BatchNorm 和 LayerNorm 的关键区别?（BN 沿 batch 维,CNN 用;LN 沿特征维,RNN/Transformer 用,BN 对变长序列不适用。）

---

## 第 10 章 · Convolutional Networks（卷积网络）

- **核心**:CNN 是计算机视觉基石。三大思想：**局部连接**（只看邻域）、**参数共享**（同一核扫遍全图→平移不变性）、**等变表示**（平移输入→平移输出）。**池化**降采样+局部不变性。步长与填充控制输出尺寸。经典架构演进：LeNet → AlexNet（2012 ImageNet 革命）→ VGG → ResNet（残差,Ch6）。本章是 LeCun 卷积思想的系统化。
- **飞腾锚点**:UDOT 16.9×[E05] 🟢。卷积 $S(i,j)=\sum_m\sum_n I(i+m,j+n)K(m,n)$ 本质是「滑窗点积」;UDOT 加速逐窗口加权求和。im2col 把卷积重排为 GEMM 后更是加速器吞吐主力——CNN 的「平移不变」最终化为海量点积。
- **关键定理**:**二维卷积** $S(i,j)=(I*K)(i,j)=\sum_m\sum_n I(i+m,j+n)K(m,n)$;参数共享使参数量 $O(n^2)\to O(k^2)$（核大小 $k$）。
- **自测**:用 $3\times 3$ 卷积核处理 $28\times 28$ 图像, stride=1, padding=1, 输出尺寸是多少?（$28\times 28$;padding 补偿核缩减。）

---

## 第 11 章 · Structured Distributions（结构化分布）

- **核心**:用图编码随机变量间条件独立性;序列模型（RNN/LSTM）也在此章。

  ① **贝叶斯网络**（有向图）$p(\mathbf{x})=\prod_i p(x_i|\text{pa}_i)$;**马尔可夫随机场**（无向图,需配分函数）。
  ② **RNN** $\mathbf{h}_t=f(\mathbf{h}_{t-1},\mathbf{x}_t)$ 保留记忆但长序列梯度消失;**LSTM** 门控控制信息流。
  ③ d-分离判条件独立。本章连接 PRML Ch8/13 与 Ch12 Transformer。
- **飞腾锚点**:TLB 4.81×[E04] 🟡。RNN 隐藏状态是「跨时间步的内存」,访问模式类似 TLB 局部性——近期状态命中率高,远期依赖易「miss」（梯度消失）。LSTM 门控像预取机制延长局部窗口。
- **关键定理**:**有向分解** $p(\mathbf{x})=\prod_i p(x_i|\text{Pa}(x_i))$;**RNN** $\mathbf{h}_t=\tanh(\mathbf{W}_{hh}\mathbf{h}_{t-1}+\mathbf{W}_{xh}\mathbf{x}_t)$;**LSTM 遗忘门** $\mathbf{f}_t=\sigma(\mathbf{W}_f[\mathbf{h}_{t-1},\mathbf{x}_t])$,细胞 $\mathbf{c}_t=\mathbf{f}_t\odot\mathbf{c}_{t-1}+\mathbf{i}_t\odot\tilde{\mathbf{c}}_t$。
- **自测**:为什么普通 RNN 处理长序列梯度消失,而 LSTM 能缓解?（细胞状态加法更新,梯度沿常数路径流动不连乘。）

---

## 第 12 章 · Transformers（Transformer）

- **核心**:Transformer 以**自注意力**取代 RNN 的循环,实现完全并行的序列建模。

  ① **缩放点积注意力** $\text{softmax}(QK^\top/\sqrt{d_k})V$ 让每个位置直接关注所有位置,无需逐步循环。
  ② **多头注意力**在不同子空间并行关注,捕获多样化依赖;**位置编码**注入顺序信息。
  ③ 编码器-解码器架构;BERT（仅编码器）/GPT（仅解码器）/T5（编码器-解码器）。2017 年以来 NLP 与 CV 的统一架构。
- **飞腾锚点**:GEMM 9.45G[Lab05] 🟢⭐。注意力的 $QK^\top$ 是 $n\times d$ 乘 $d\times n$ 的大矩阵乘,softmax 后再乘 $V$——每层 3–4 个 GEMM,大模型训练吞吐瓶颈全在 GEMM。KV cache 的推理加速依赖参数局部加载（TLB 命中）。
- **关键定理**:**缩放点积自注意力** $\text{Attention}(Q,K,V)=\text{softmax}\!\left(\dfrac{QK^\top}{\sqrt{d_k}}\right)V$;多头拼接 $\text{MultiHead}=\text{Concat}(\text{head}_1,\ldots,\text{head}_h)W^O$。
- **自测**:自注意力中除以 $\sqrt{d_k}$ 的作用?（$d_k$ 大时点积方差大→softmax 饱和→梯度消失;缩放使方差稳定为 1。）

---

## 第 13 章 · Graph Neural Networks（图神经网络）

- **核心**:GNN 处理图结构数据（分子、社交网络、知识图谱、蛋白质）。核心是**消息传递**：每个节点聚合邻居信息更新自身表示。谱图卷积（ChebNet/GCN）从图傅里叶变换导出——图拉普拉斯 $L=D-A$ 的特征向量类比傅里叶基。GNN 是**排列等变**的,天然适合非欧结构数据。本章是 2020 年代图表示学习的前沿。
- **飞腾锚点**:matmul 15×[V03] 🟡。GNN 的邻居聚合涉及稀疏邻接矩阵乘节点特征矩阵 $\hat{A}\mathbf{X}$——稀疏 matmul 是 GNN 的核心运算,稀疏模式由图结构决定。
- **关键定理**:**GCN 传播规则** $\mathbf{H}^{(\ell+1)}=\sigma(\tilde{D}^{-1/2}\tilde{A}\tilde{D}^{-1/2}\mathbf{H}^{(\ell)}\mathbf{W}^{(\ell)})$,其中 $\tilde{A}=A+I$（加自环）,$\tilde{D}$ 为度矩阵;消息传递 $\mathbf{h}_v=\text{UPDATE}(\mathbf{h}_v,\text{AGG}(\{\mathbf{h}_u:u\in\mathcal{N}(v)\}))$。
- **自测**:GNN 为什么是排列等变的?（聚合函数 SUM/MEAN 对邻居顺序不敏感;对称函数。）

---

# Part IV · 采样与潜变量（Ch14–16）—— 推断引擎

**本段锚点:UDOT 蒙特卡洛 / Iron Law EM 收敛 / matmul PCA** —— 采样期望=加权点积,EM 迭代收敛,PCA 协方差特征分解。

---

## 第 14 章 · Sampling（采样）

- **核心**:当分布难解析处理时,用**采样**估计期望。基本方法：逆 CDF、拒绝采样、**重要性采样**（用易采样分布 $q$ 估计 $E_p[f]$）。**MCMC**：Metropolis-Hastings（提议+接受率 $\min(1,\cdot)$）、**Gibbs**（逐维条件采样）。**细致平衡** $p(x)T(x\to x')=p(x')T(x'\to x)$ 保证平稳分布。蒙特卡洛误差 $O(1/\sqrt{N})$ 与维数无关——高维的救命性质。接续 PRML Ch11。
- **飞腾锚点**:UDOT 16.9×[E05] 🟡。蒙特卡洛估计 $E[f]\approx\frac{1}{N}\sum f(x_i)$ 是等权点积（权重 $1/N$）;UDOT 加速批量采样期望的求和,重要性采样的权重比 $p/q$ 也是逐元素点积。
- **关键定理**:**重要性采样** $E_p[f(\mathbf{x})]=E_q\!\left[f(\mathbf{x})\dfrac{p(\mathbf{x})}{q(\mathbf{x})}\right]$;**细致平衡** $p(x)T(x\to x')=p(x')T(x'\to x)\Rightarrow\pi=p$ 平稳;蒙特卡洛误差 $O(1/\sqrt{N})$。
- **自测**:重要性采样中 $q$ 在 $p$ 高概率区概率很低会怎样?（估计方差爆炸,甚至无界。）

---

## 第 15 章 · Discrete Latent Variables（离散隐变量）

- **核心**:用离散隐变量解释观测数据结构。**高斯混合（GMM）** $p(\mathbf{x})=\sum_k\pi_k\mathcal{N}(\mathbf{x}|\boldsymbol\mu_k,\Sigma_k)$,隐变量 one-hot 指派。**EM 算法**：E 步算隐变量后验期望,M 步最大化更新参数;EM **单调增**对数似然（等价最小化 KL 到后验）。**K-means** 是 EM 的硬指派特例（责任度退化为 0/1）。主题模型 LDA（Dirichlet 先验 + Multinomial 似然）。
- **飞腾锚点**:Iron Law<2%[Lab00] 🟡。EM 收敛到局部极大非全局;迭代似然单调增但可能停在次优,误差控制呼应 Iron Law「逼近但须可控」。多次初始化是工程实践。
- **关键定理**:**EM Q 函数** $Q(\boldsymbol\theta,\boldsymbol\theta^{old})=\sum_{\mathbf{z}}p(\mathbf{z}|\mathbf{X},\boldsymbol\theta^{old})\ln p(\mathbf{X},\mathbf{z}|\boldsymbol\theta)$;**EM 单调性** $\ln p(\mathbf{X}|\boldsymbol\theta)\ge\ln p(\mathbf{X}|\boldsymbol\theta^{old})$;GMM 责任度 $\gamma_{nk}=\frac{\pi_k\mathcal{N}_k}{\sum_j\pi_j\mathcal{N}_j}$。
- **自测**:K-means 与 EM 的关系?（K-means = EM 的硬指派特例：责任度退化为 0/1。）

---

## 第 16 章 · Continuous Latent Variables（连续隐变量）

- **核心**:用低维连续隐变量解释高维观测,本章含 PCA 与变分推断入门。

  ① **PCA**：最大方差/最小重构误差两种等价推导,解都是协方差特征向量。
  ② **概率 PCA**（PPCA）:$\mathbf{x}=W\mathbf{z}+\boldsymbol\mu+\boldsymbol\epsilon$,EM 拟合,贝叶斯可自动定维数。
  ③ **变分推断**入门：精确后验不可解时用 $q$ 近似,最大化 ELBO——为 Ch19 VAE 做数学准备。
- **飞腾锚点**:matmul 15×[V03] 🟡。PCA 解协方差 $S=\frac{1}{N}\sum(\mathbf{x}_n-\bar{\mathbf{x}})(\mathbf{x}_n-\bar{\mathbf{x}})^\top$ 的特征向量——矩阵求积+特征分解,协方差对角化即降维。变分推断的摊销用网络参数化 $q$,计算仍是矩阵运算。
- **关键定理**:**PCA** 协方差特征 $S\mathbf{u}_j=\lambda_j\mathbf{u}_j$;**PPCA** $\mathbf{x}=W\mathbf{z}+\boldsymbol\mu+\boldsymbol\epsilon$, $\mathbf{z}\sim\mathcal{N}(0,I)$;**ELBO** $\mathcal{L}=E_q[\ln p(\mathbf{x},\mathbf{z})]-E_q[\ln q(\mathbf{z})]\le\ln p(\mathbf{x})$。
- **自测**:PCA 与 PPCA 的区别?（PCA 确定性,PPCA 概率化——给似然/不确定性,可贝叶斯模型比较。）

---

# Part V · 生成模型（Ch17–20）—— VAE/GAN/Flow/Diffusion 四路生成

**本段锚点:GEMM⭐大规模生成训练** —— GAN/VAE/Diffusion 的训练是大规模概率计算,瓶颈全在 GEMM 吞吐。

---

## 第 17 章 · Generative Adversarial Networks（生成对抗网络）

- **核心**:GAN 用**博弈**替代显式似然,绕过配分函数。

  ① 生成器 $G$ 试图骗过判别器 $D$,判别器区分真实/生成样本,极小极大博弈达 Nash 均衡时 $p_g=p_{data}$。
  ② 训练挑战：模式崩溃（mode collapse,只产少数样本）、不稳定性。
  ③ WGAN 用 Wasserstein 距离改善稳定性;StyleGAN 用风格注入控制生成质量。
- **飞腾锚点**:GEMM 9.45G[Lab05] 🟢。GAN 训练是大规模 GEMM：生成器与判别器都是深层网络,交替训练需海量矩阵乘;StyleGAN 等大规模生成把 GEMM 吞吐推到极致。
- **关键定理**:**GAN 极小极大目标** $\min_G\max_D\;E_{\mathbf{x}\sim p_{data}}[\ln D(\mathbf{x})]+E_{\mathbf{z}\sim p_z}[\ln(1-D(G(\mathbf{z})))]$;最优 $D^*(\mathbf{x})=\dfrac{p_{data}(\mathbf{x})}{p_{data}(\mathbf{x})+p_g(\mathbf{x})}$。
- **自测**:GAN 的「模式崩溃」是什么?如何缓解?（生成器只产少数样本骗判别器;WGAN/minibatch discrimination 缓解。）

---

## 第 18 章 · Normalizing Flows（归一化流）

- **核心**:用一系列**可逆变换**构建复杂分布：简单基础分布 $p(\mathbf{z})$ → 可逆网络 $\mathbf{z}=f_\theta(\mathbf{x})$ → 精确似然 $\log p(\mathbf{x})=\log p(\mathbf{z})+\log|\det J_f|$。耦合层（RealNVP）分裂维度,一半不变另一半仿射变换,Jacobian 为三角易算行列式。自回归流（MAF/IAF）。Flows 给出**精确对数似然**（不像 GAN/VAE 有近似）,但可逆性约束限制了架构灵活性。
- **飞腾锚点**:Schmidt 正交化 🟡。可逆变换要求 Jacobian 行列式可算——三角 Jacobian 的行列式 = 对角元素积,类似 Schmidt 把变换分解为初等（三角）操作,使行列式易算。
- **关键定理**:**变量变换公式** $\log p(\mathbf{x})=\log p(\mathbf{z})+\log\left|\det\dfrac{\partial f_\theta}{\partial\mathbf{x}}\right|$, $\mathbf{z}=f_\theta(\mathbf{x})$;RealNVP 耦合层 Jacobian 为三角,行列式 $=\prod$ 对角元素。
- **自测**:为什么 Normalizing Flows 能给出精确对数似然而 VAE 不能?（可逆变换的变量变换公式精确;VAE 用 ELBO 近似,有 KL gap。）

---

## 第 19 章 · Autoencoders（自编码器）

- **核心**:自编码器学「恒等映射」的压缩表示;VAE 是其概率化升级。

  ① 基本自编码器：编码器 $f$ 压成潜码 $\mathbf{z}=f(\mathbf{x})$,解码器 $g$ 重建 $\hat{\mathbf{x}}=g(\mathbf{z})$,目标 $\|\mathbf{x}-\hat{\mathbf{x}}\|^2$。
  ② **变分自编码器（VAE）**：编码器输出分布参数 $q(\mathbf{z}|\mathbf{x})=\mathcal{N}(\boldsymbol\mu,\boldsymbol\sigma^2)$。
  ③ **重参数化技巧** $z=\mu+\sigma\odot\epsilon$（$\epsilon\sim\mathcal{N}(0,I)$）使梯度可传播;目标 = 负 ELBO。
- **飞腾锚点**:FP16 3.81×[L01] 🟢。VAE 训练涉及编码器+解码器双网络前向反向,混合精度（FP16/BF16）省内存加速 GEMM;重参数化的逐元素乘加用 FP16 精度足够,loss scale 防下溢。
- **关键定理**:**VAE 目标（=负 ELBO）** $\mathcal{L}_{VAE}=E_{q(\mathbf{z}|\mathbf{x})}[\ln p(\mathbf{x}|\mathbf{z})]-D_{KL}(q(\mathbf{z}|\mathbf{x})\|p(\mathbf{z}))$;**重参数化** $\mathbf{z}=\boldsymbol\mu+\boldsymbol\sigma\odot\boldsymbol\epsilon$, $\boldsymbol\epsilon\sim\mathcal{N}(0,I)$;**ELBO 推导** $\ln p(\mathbf{x})=\mathcal{L}+D_{KL}(q\|p)\ge\mathcal{L}$（Jensen 不等式）。
- **自测**:重参数化技巧为什么使梯度可传播?（$\mathbf{z}=\boldsymbol\mu+\boldsymbol\sigma\odot\boldsymbol\epsilon$ 把随机性外移到 $\epsilon$, $\mu,\sigma$ 的路径可微。）

---

## 第 20 章 · Diffusion Models（扩散模型）

- **核心**:Diffusion 用两阶段生成,是 2020–2024 生成模型的新范式,已超越 GAN。

  ① **前向**逐步加噪（固定马尔可夫链）把数据破坏为纯噪声;前向 $q(\mathbf{x}_t|\mathbf{x}_0)$ 有解析式（直接跳到任意步）。
  ② **反向**学习逐步去噪网络恢复数据;训练目标 = 预测每步添加的噪声（去噪得分匹配）。
  ③ **DDPM**（Ho 2020）使扩散实用化;**Stable Diffusion** 在潜空间扩散大幅降算力。
- **飞腾锚点**:GEMM 9.45G[Lab05] 🟢⭐。扩散模型的 U-Net 去噪网络是深层 CNN,每个去噪步需一次完整前向+反向;多步推理（20–1000 步）是大规模 GEMM 消耗。潜空间扩散（Stable Diffusion）用 VAE 先降维再扩散,大幅减少 GEMM 规模。
- **关键定理**:**前向过程** $q(\mathbf{x}_t|\mathbf{x}_0)=\mathcal{N}\!\left(\sqrt{\bar\alpha_t}\,\mathbf{x}_0,(1-\bar\alpha_t)\mathbf{I}\right)$,其中 $\bar\alpha_t=\prod_{s=1}^t\alpha_s$;**训练目标**（简化） $\mathcal{L}_{simple}=E_{t,\mathbf{x}_0,\boldsymbol\epsilon}\left[\|\boldsymbol\epsilon-\boldsymbol\epsilon_\theta(\mathbf{x}_t,t)\|^2\right]$;**反向过程** $p_\theta(\mathbf{x}_{t-1}|\mathbf{x}_t)=\mathcal{N}(\boldsymbol\mu_\theta(\mathbf{x}_t,t),\boldsymbol\Sigma_\theta)$。
- **自测**:为什么 Diffusion 前向 $q(\mathbf{x}_t|\mathbf{x}_0)$ 有解析式可直接采样?（高斯加噪累积效应是高斯, $\bar\alpha_t$ 闭式给出。）

---

## §9 全书思想主线：概率统一视角（约 230 字）

全书被**一条主线**贯穿（Bishop 一以贯之的核心贡献,从 PRML 延续到本书）：

> **机器学习 = 概率推断 + 梯度优化。一切 DL 模型——从线性回归到 Diffusion 去噪——底层都是贝叶斯框架,统一语言是 KL 散度与 ELBO。**

本书沿六段递进铺满：① **概率地基**（Ch1–3）建立贝叶斯操作系统与指数族;② **网络**（Ch4–8）从线性到深度,反向传播让高维参数可学,GEMM 是算力肉身;③ **训练架构**（Ch9–13）用正则化/CNN/Transformer/GNN 组装真实系统;④ **采样推断**（Ch14–16）用蒙特卡洛/EM/变分解不可解后验;⑤ **生成模型**（Ch17–20）四路并进——GAN 用博弈、Flow 用可逆变换、VAE 用变分、Diffusion 用去噪得分匹配。

与已读教材呼应：**PRML（pre）**是本书前半（Ch1–5,8,11,15）的直接来源,本书补上 PRML 缺失的深度/Transformer/Diffusion;**Goodfellow DL（已读）**是 2016 工程直觉版,本书更概率化且更新;**Hastie ESL（已读）**提供频率派对照;**Mohri（已读）**补充 PAC/Rademacher 理论保证。一句话：**Bishop 把概率推断这门语言从经典 ML 推广到深度学习全谱,KL/ELBO 是从交叉熵损失到 Diffusion 去噪的统一数学骨架。**

---

## §10 与本仓库其他笔记的交叉引用

| 本书概念 | 关联书 / 领域 | 接口说明 |
|:------|:------|:------|
| 贝叶斯/指数族/KL（Ch2–3） | **Bishop PRML（已读）Ch1–2** | 本书直接继承 PRML 概率地基;Cover-Thomas KL 严格基础 |
| 线性回归/分类（Ch4–5） | **Bishop PRML Ch3–4 / Hastie ESL（已读）Ch3–4** | 正规方程/logistic 同源;Hastie 频率派对照 |
| 深度网络/反向传播（Ch6,8） | **Goodfellow DL（已读）Ch6** | 万有逼近+链式法则;本书更新含残差/GELU |
| 优化/SGD/动量（Ch7） | **nocedal-wright 数值优化（已读）** | 一阶随机优化的深度学习工程化 |
| 正则化/Dropout/BatchNorm（Ch9） | **Goodfellow DL Ch7** | BatchNorm/Schmidt 正交化类比 |
| Transformer 自注意力（Ch12） | **Goodfellow DL（2016,无 Transformer）** | 本书新增;HF Transformers 工程落地 |
| EM/隐变量（Ch15） | **Bishop PRML Ch9 / Mohri（已读）** | EM 单调性 = 最小化 KL |
| VAE/ELBO（Ch19） | **Bishop PRML Ch10（变分推断源头）** | ELBO = Jensen 不等式;VAE = 变分 + 网络 |
| Diffusion（Ch20） | **Goodfellow DL（2016,无 Diffusion）** | 本书新增 2020 前沿;Stable Diffusion 工程 |

**AI / 工程锚点速查**（本书 → PyTorch 生态的直接映射）：

- 🟢 **torch.nn = 网络层**：Ch6 深度网络 → `nn.Linear`/`nn.Conv2d`;前向 = GEMM,反向 = autograd 计算图（Ch8 反向传播）。
- 🟢 **torch.optim = 优化器**：Ch7 梯度下降 → `optim.SGD`/`optim.AdamW`;学习率调度 → `lr_scheduler`。
- 🟢 **Hugging Face Transformers = Ch12 工程化**：`AutoModel`/`Attention` 实现;KV cache 推理加速依赖参数局部加载（TLB）。
- 🟢 **Stable Diffusion = Ch20 工程化**：潜空间扩散（VAE 编码 + U-Net 去噪）;大规模 GEMM 训练。
- 🟢 **Flash Attention = Ch12 优化**：分块计算注意力 softmax,减少 HBM 读写,把 GEMM/IO 比推向硬件极限。
- 🟡 **BatchNorm/LayerNorm = Schmidt 正交化**：激活分布标准化,去相关降内部协变量偏移（Ch9）。

> **注**:本书无强化学习（RL）独立章节;RL 方向直接读 **Sutton-Barto（已读）**。本书与 Goodfellow DL 的关键差异：含 Transformer（Ch12）、GNN（Ch13）、Normalizing Flows（Ch18）、Diffusion（Ch20）——均为 2017 年后新增的现代架构,Goodfellow 2016 版未覆盖。
