# CSdiy AI/ML/DL 课程完全解析

> 本文档覆盖 csdiy 课程地图中 AI/ML/DL 相关的全部大类（人工智能、机器学习、机器学习系统、深度学习、深度生成模型、机器学习进阶），约 30 门课程。
> 作为 AI 全栈导师的核心文档，每门课做到**主题级实质内容**（概念+公式+算法+应用）。
> 数据来源：csdiy.wiki 课程详情 + 课程官网 + 学科知识。

---

# 第一大类 · 人工智能入门（3 门）

> **定位**：经典 AI（搜索/规划/推理/经典 RL），非深度学习。基于 AIMA 教材。

---

## 课程 #1 · UCB CS188：Introduction to Artificial Intelligence ⭐

### 课程元数据
| 字段 | 内容 |
|------|------|
| 开课 | UC Berkeley |
| 先修 | CS70 |
| 语言 | Python |
| 难度 | 🌟🌟🌟 |
| 学时 | 50 小时 |
| 课程网站(SP24) | https://inst.eecs.berkeley.edu/~cs188/sp24/ |
| 教材 | *Artificial Intelligence: A Modern Approach*（AIMA，AI 圣经）|
| Gradescope | SP24 开放旁听，可在线测评 |

**csdiy 评价**：notes 深入浅出，基本不需看视频。**6 个 Project 质量爆炸**——复现 Pacman 吃豆人，用 AI 算法让吃豆人穿梭迷宫、躲避鬼怪、收集豆子。

### 📑 完整教学大纲（按 AIMA 顺序，逐主题实质内容）

#### 🔵 搜索（Search）⭐ 经典 AI 核心

| 主题 | 核心内容 | 关键算法/概念 |
|------|---------|--------------|
| **搜索问题建模** | state / action / transition / goal / cost 五元组 | 形式化问题的能力 |
| **无信息搜索** | BFS（广度）/ DFS（深度）/ UCS（一致代价）| FIFO / LIFO / 优先队列；完备性/最优性 |
| **A\* 搜索** ⭐⭐ | $f(n)=g(n)+h(n)$（实际代价+启发式）；**可采纳性**（admissible，不高估）| 曼哈顿距离/欧式距离作为 h |
| **对抗搜索（Minimax）** ⭐ | 零和博弈；MAX/MIN 交替；递归求值 | Alpha-Beta 剪枝（减少搜索）|
| **期望最小最大（Expectimax）** | 含随机节点；概率加权 | 处理不确定性对手 |

**Pacman Project 1-2** ⭐：用搜索算法让 Pacman 找豆子、逃跑。

#### 🟢 约束满足问题（CSP）

| 主题 | 核心内容 |
|------|---------|
| **CSP 建模** | 变量/域/约束三元组；地图着色/数独 |
| **回溯搜索** | MRV（最少剩余值）/ LCV（最少约束值）启发式 |
| **弧一致性（AC-3）** | 前向检查；约束传播 |

#### 🟡 马尔可夫决策过程（MDP）⭐⭐ 强化学习根基

| 主题 | 核心内容 | 公式 |
|------|---------|------|
| **MDP 建模** | (S, A, T, R, γ) 五元组 | 状态/动作/转移/奖励/折扣 |
| **Bellman 方程** ⭐⭐ | 最优价值函数的自洽方程 | $V^*(s)=\max_a \sum_{s'} T(s,a,s')[R(s,a,s')+\gamma V^*(s')]$ |
| **价值迭代** ⭐ | 迭代求解 Bellman | $V_{k+1}(s) \leftarrow \max_a \sum_{s'} T(\cdot)[R+\gamma V_k(s')]$ |
| **策略迭代** | 策略评估 + 策略改进 | 交替直到收敛 |

**Pacman Project 3** ⭐：用 MDP 让 Pacman 在不确定环境中决策。

#### 🟣 强化学习（RL）⭐

| 主题 | 核心内容 | 与 MDP 区别 |
|------|---------|------------|
| **模型无关 RL** | 不知道转移函数 T | 需要探索 |
| **Q-learning** ⭐⭐ | 学习 Q(s,a) 表 | $Q(s,a)\leftarrow Q(s,a)+\alpha[r+\gamma\max_{a'}Q(s',a')-Q(s,a)]$ |
| **ε-贪心探索** | 平衡探索 vs 利用 | 以 ε 概率随机 |
| **近似 Q 学习** | 特征+权重 | 处理大状态空间 |

**Pacman Project 4-6** ⭐：Q-learning 让 Pacman 学会逃跑/追鬼。

#### 🔴 概率推理

| 主题 | 核心内容 |
|------|---------|
| **贝叶斯网络** ⭐ | 有向无环图；条件独立；联合 = 各条件概率之积 |
| **隐马尔可夫模型（HMM）** ⭐ | 状态隐藏；Viterbi 解码；前向/后向算法 |
| **粒子滤波** | 蒙特卡洛近似 |

#### ⚫ 机器学习基础（简介）
朴素贝叶斯分类；感知机；简介神经网络。

### 🎯 在 AI 学习中的定位
- **经典 AI 的全景图**：搜索/博弈/MDP/RL/概率推理
- **深度强化学习（CS285）的前置**：MDP/Q-learning 是 DQN 的根基
- **AIMA 教材**：AI 领域的圣经

---

## 课程 #2 · Harvard CS50's Introduction to AI with Python

### 课程元数据
| 字段 | 内容 |
|------|------|
| 开课 | Harvard |
| 先修 | 概率论 + Python |
| 难度 | 🌟🌟🌟 |
| 学时 | 30 小时 |
| 网站(2024) | https://cs50.harvard.edu/ai/2024/ |
| 资源 | https://github.com/PKUFlyingPig/cs50_ai |

**csdiy 评价**：非常基础的 AI 入门。**12 个精巧编程作业**——用 AI 知识实现游戏 AI（如 RL 训练 Nim 游戏 AI，alpha-beta 剪枝扫雷）。

### 📑 核心教学主题（6 大模块，每模块 2 作业）
1. **搜索**：BFS/DFS/A* → 迷宫求解
2. **知识推理**：命题逻辑 → 扫雷
3. **不确定性**：贝叶斯网络 → 信念更新
4. **优化**：局部搜索/约束满足
5. **学习**：监督/无监督
6. **神经网络**：基础 NN → 手写识别

---

## 课程 #3 · Neural Networks: Zero to Hero（Karpathy）⭐⭐⭐ 强推

### 课程元数据
| 字段 | 内容 |
|------|------|
| 讲师 | **Andrej Karpathy**（Tesla AI 总监、OpenAI 创始成员、李飞飞博士、CS231n 创始人）|
| 先修 | Python + 深度学习基础概念 |
| 语言 | Python（PyTorch）|
| 难度 | 🌟🌟🌟🌟 |
| 时长 | ~19 小时 |
| YouTube | https://www.youtube.com/watch?v=VMj-3S1tku0&list=PLAqhIrjkxbuWI23v9cThsA9GvCAUhRvKZ |

**csdiy 评价**：深度学习入门的**最佳实践课程**——不调包，从零实现。

### 📑 完整教学大纲（6 集，每集从零实现一个系统）⭐⭐⭐

#### Lecture 1：The spelled-out intro to neural networks and backpropagation
- **micrograd**：用 ~100 行 Python 从零实现自动微分引擎
- **反向传播的精髓** ⭐⭐：每个节点的局部梯度 × 上游梯度
- 链式法则的代码化（联系 18.01 链式法则 + 18.06 矩阵）
- 理解 PyTorch 的底层原理

#### Lecture 2-4：makemore（字符级语言模型，逐步升级）⭐⭐
- **L2**：Bigram 模型（最简单的语言模型）；计数法 vs 神经网络法
- **L3** ⭐⭐：**MLP（多层感知机）**实现字符级语言模型（参考 Bengio 2003 论文）
- **L4** ⭐：**激活函数选择**（为什么 tanh 会饱和）；**BatchNorm**（内部协变量偏移）；初始化策略

#### Lecture 5：WaveNet ⭐
- **多层 MLP → 树状结构**（逐层聚合）
- 理解**感受野**（receptive field）的扩大
- 参考 WaveNet 论文

#### Lecture 6：Let's build GPT from scratch ⭐⭐⭐
- **从零实现 GPT**（Transformer decoder）
- **Self-Attention** ⭐⭐⭐：$Attention(Q,K,V)=softmax(QK^T/\sqrt{d_k})V$
- 多头注意力；位置编码；LayerNorm
- 用 GPT 生成莎士比亚风格文本

### 🎯 在 AI 学习中的定位（极高价值）
- **理解深度学习的"第一性原理"**：不调包，理解每个细节
- **Karpathy 的独特视角**：工业界顶级实战 + 学术深度
- **CS231n 创始人亲自教**：计算机视觉深度学习课程的起源

**⚠️ 学习建议**：适合已学过一门深度学习理论课（如吴恩达 DL）后，想**真正理解**底层原理的人。

---

# 第二大类 · 机器学习（3 门）

> **定位**：从经典 ML（线性模型/SVM）到现代 ML（树模型/集成）。

---

## 课程 #4 · Coursera: Machine Learning（吴恩达）⭐ 最友好入门

### 课程元数据
| 字段 | 内容 |
|------|------|
| 开课 | Stanford（Coursera）|
| 主讲 | **Andrew Ng（吴恩达）**（Coursera 创始人、Stanford 网红教授）|
| 先修 | AI 入门 + Python |
| 语言 | Python |
| 难度 | 🌟🌟🌟 |
| 学时 | 100 小时 |
| 课程网站 | https://www.coursera.org/specializations/machine-learning-introduction |

**csdiy 评价**：吴恩达的成名作之一。把机器学习讲成"1+1=2"一样直白。保姆级代码框架，作业背景取自生活。难度刻意放低（数学推导一带而过）。

### 📑 完整教学大纲（三大课程系列）

#### 课程 1：Supervised Learning（监督学习）

| 主题 | 核心内容 | 公式/算法 |
|------|---------|----------|
| **线性回归** ⭐ | 单变量/多变量 | $h_\theta(x)=\theta^Tx$；梯度下降 $\theta \leftarrow \theta - \alpha\nabla J$ |
| **代价函数** | MSE | $J(\theta)=\frac{1}{2m}\sum(h_\theta(x^{(i)})-y^{(i)})^2$ |
| **梯度下降** ⭐ | 批量/小批量/随机 | 学习率 α 的选择；收敛诊断 |
| **特征工程** | 归一化/多项式特征 | mean normalization |
| **逻辑回归** ⭐ | 二分类 | Sigmoid $g(z)=1/(1+e^{-z})$；交叉熵损失 |
| **正则化** ⭐ | 防止过拟合 | L1/L2（联系 Data100 + EE364A）|
| **神经网络基础** | 前向传播；简单识别 | 手写数字识别 |

#### 课程 2：Advanced Learning Algorithms

| 主题 | 核心内容 |
|------|---------|
| **神经网络深入** ⭐ | 多层；激活函数（ReLU）；反向传播 |
| **激活函数** | Sigmoid/tanh/ReLU/Softmax |
| **多分类** | Softmax 回归 |
| **优化算法** | Adam；学习率衰减 |
| **CNN 简介** | 卷积层；池化 |

#### 课程 3：Unsupervised Learning（无监督学习）

| 主题 | 核心内容 |
|------|---------|
| **K-Means 聚类** ⭐ | 簇分配 + 中心更新 |
| **异常检测** | 高斯模型；密度估计 |
| **推荐系统** ⭐ | 协同过滤；矩阵分解 |
| **强化学习简介** | Q-learning |

### 🎯 在 AI 学习中的定位
- **ML 最佳入门**——零数学负担建立直觉
- 理解后接 CS229（理论深入）或直接上深度学习

---

## 课程 #5 · Stanford CS229：Machine Learning ⭐ 理论圣经

### 课程元数据
| 字段 | 内容 |
|------|------|
| 开课 | Stanford |
| 主讲 | **Andrew Ng** |
| 先修 | 高数 + 概率论 + Python + **深厚数学功底** |
| 难度 | 🌟🌟🌟🌟 |
| 学时 | 100 小时 |
| 课程网站 | http://cs229.stanford.edu |
| B站视频 | https://www.bilibili.com/video/BV1JE411w7Ub |
| 资源汇总 | https://github.com/PKUFlyingPig/CS229 |

**csdiy 评价**：研究生课程，**偏重数学理论**。课程 notes 写得专业且理论，需数学功底。不满足于调包、想深入本质的人必学。

### 📑 完整教学大纲（理论深度版）⭐⭐

#### 🔵 监督学习（理论推导）

| 主题 | 核心内容 | 关键推导 |
|------|---------|---------|
| **线性回归** | 正规方程；概率解释 | $\hat\theta=(X^TX)^{-1}X^Ty$；最大似然 → MSE |
| **广义线性模型（GLM）** ⭐ | 指数族分布的统一框架 | 逻辑回归/Softmax/线性回归都是 GLM 特例 |
| **逻辑回归** ⭐ | 分类 | Sigmoid 从指数族导出；梯度上升 |
| **生成学习算法** ⭐⭐ | GDA（高斯判别分析）；朴素贝叶斯 | $p(x\|y)$ 建模 vs $p(y\|x)$ |
| **GDA vs 逻辑回归** | 生成 vs 判别 | GDA 更强假设 → 数据少时更好 |

#### 🟢 核方法与 SVM ⭐⭐

| 主题 | 核心内容 | 数学 |
|------|---------|------|
| **间隔最大化** | 几何直觉 | $\max \gamma$ s.t. $y^{(i)}(w^Tx+b)\ge\gamma$ |
| **对偶问题** ⭐ | 拉格朗日对偶（联系 EE364A KKT） | $\max_\alpha W(\alpha)$ s.t. $\sum\alpha_i y^{(i)}=0$ |
| **核技巧（Kernel Trick）** ⭐⭐ | 隐式高维映射 | $K(x,z)=\phi(x)^T\phi(z)$；多项式/RBF 核 |
| **软间隔** | 处理非线性可分 | 松弛变量 $\xi_i$；C 参数权衡 |

#### 🟡 学习理论 ⭐⭐

| 主题 | 核心内容 |
|------|---------|
| **偏差-方差权衡** | $E[\text{err}]=\text{Bias}^2+\text{Var}+\text{noise}$ |
| **VC 维** | 假设空间复杂度 |
| **ERM（经验风险最小化）** | 一致性；PAC 学习 |

#### 🟣 其他

| 主题 | 核心内容 |
|------|---------|
| **决策树** | 信息增益；ID3 |
| **神经网络** | 反向传播推导 |
| **无监督** | K-Means/EM 算法 ⭐/PCA |
| **强化学习** | MDP/Q-learning |

### 🎯 在 AI 学习中的定位
- **ML 理论的圣经**——所有算法的数学本质
- 与 EE364A 凸优化 + CS70/CS126 概率论交叉验证

---

## 课程 #6 · UCB CS189：Introduction to Machine Learning

### 课程元数据
| 字段 | 内容 |
|------|------|
| 开课 | UC Berkeley |
| 先修 | CS188, CS70 |
| 语言 | Python |
| 难度 | 🌟🌟🌟🌟 |
| 学时 | 100 小时 |
| 课程网站 | https://www.eecs189.org/ |
| YouTube | https://www.youtube.com/playlist?list=PLOOm2AoWIPEyZazQVnIcaK2KnezpGZV-X |

**定位**：CS229 的 UCB 版本，理论深入。**比 CS229 好**的是开源了所有 homework 代码 + gradescope autograder。

### 📑 核心主题（与 CS229 类似但侧重不同）
- 线性/逻辑回归
- **随机梯度下降**深入
- **交叉验证/正则化**实践
- 决策树/随机森林/GBDT
- 神经网络
- **无监督**（PCA/K-Means）

---

# 📊 AI 入门 + ML 选课套餐

### 套餐 A：零基础入门 ML
```
CS50 AI(#2) 或 CS188(#1) → Coursera ML(#4) ⭐ 最友好
```

### 套餐 B：理论深入（csdiy 强推）
```
CS188(#1) + CS70(数学) → CS229(#5) ⭐⭐ 理论圣经
```

### 套餐 C：从零实现（理解底层）
```
Coursera ML(#4) → Karpathy Zero to Hero(#3) ⭐⭐⭐ 从零实现 GPT
```

### 套餐 D：完整 AI 路径（csdiy 隐含）
```
数学基础(18.06/CS70/EE364A) → CS188(#1) → CS229(#5) → Karpathy(#3) → 深度学习(下一文档)
```

## ⚠️ 关键提醒

1. **Karpathy Zero to Hero 是隐藏的王者** ⭐⭐⭐——从零实现 micrograd/MLP/WaveNet/GPT，理解深度学习第一性原理
2. **CS188 的 Pacman Project 极高质量**——用经典 AI 算法让吃豆人智能行动
3. **吴恩达两门课定位不同**：Coursera ML（友好入门）vs CS229（理论圣经）
4. **数学映射**：SVM↔EE364A KKT 对偶，逻辑回归↔CS126 指数族，PCA↔18.06 SVD

---

# 第三大类 · 深度学习（10 门）⭐⭐ csdiy 后半核心

> **定位**：从 CNN/RNN 到 Transformer/Attention，覆盖 CV/NLP/图/RL 全领域。

---

## 课程 #7 · Stanford CS231n：CNN for Visual Recognition ⭐ CV 入门

### 课程元数据
| 字段 | 内容 |
|------|------|
| 开课 | Stanford |
| 主讲 | **李飞飞院士**（ImageNet 创始人，CV 划时代人物）|
| 先修 | 机器学习基础 |
| 语言 | Python |
| 难度 | 🌟🌟🌟🌟 |
| 学时 | 80 小时 |
| 课程网站 | http://cs231n.stanford.edu/ |
| B站(2017) | https://www.bilibili.com/video/BV1nJ411z7fe |
| YouTube(2025最新) | https://www.youtube.com/playlist?list=PLoROMvodv4rOmsNzYBMe0gJY2XS8AQg16 |
| 作业 | 3 个编程作业 |

**csdiy 评价**：CV 入门课，内容基础友好。学过 CS230 可直接上手 Project。

### 📑 完整教学大纲（CV 从零到现代）

#### 🔵 基础（分类器的演进）

| 主题 | 核心内容 | 关键概念 |
|------|---------|---------|
| **KNN 分类器** | 最简单；距离度量 | L1/L2 距离；缺点：维度灾难 |
| **线性分类器** ⭐ | $f(x)=Wx+b$ | 参数化；解释 W 的每一行 = 模板 |
| **损失函数** ⭐ | SVM（hinge loss）；**Softmax（交叉熵）** ⭐⭐ | $L_i=-\log\frac{e^{f_{y_i}}}{\sum_j e^{f_j}}$（联系 6.050J 熵）|
| **优化** ⭐ | 梯度下降；数值/解析梯度 | 反向传播 = 链式法则（联系 18.01 S11）|
| **反向传播** ⭐⭐ | 计算图；局部梯度 | 理解深度学习的核心机制 |

#### 🟢 神经网络

| 主题 | 核心内容 |
|------|---------|
| **激活函数** | Sigmoid/tanh/**ReLU** ⭐/Leaky ReLU |
| **数据预处理** | 归一化；PCA/白化（联系 Data100/18.06）|
| **权重初始化** | Xavier/He 初始化；为什么不能全零 |
| **BatchNorm** ⭐ | 内部协变量偏移；加速训练 |
| **正则化** | Dropout；L2 |

#### 🟡 CNN（卷积神经网络）⭐⭐ CV 核心

| 主题 | 核心内容 | 数学 |
|------|---------|------|
| **卷积层** ⭐⭐ | 局部连接；权值共享；平移不变性 | 输出尺寸 $(W-F+2P)/S+1$ |
| **池化层** | 最大/平均池化；降维 | |
| **经典架构** ⭐⭐ | AlexNet→VGG→GoogLeNet→**ResNet** ⭐⭐⭐ | ResNet 残差连接解决深度退化 |
| **视觉任务** | 分类/检测/分割 | |

### 📑 3 个 Assignment
1. **kNN / SVM / Softmax / 两层 NN**（从零实现，不用框架）
2. **全连接神经网络**（实现反向传播）
3. **CNN** ⭐（实现卷积层；在 CIFAR-10 训练）

### 🎯 在 AI 学习中的定位
- **CV 的标准入门**——李飞飞团队 + ImageNet 的发源地
- Karpathy 是这门课的创始人（后来做了 Zero to Hero）

---

## 课程 #8 · UMich EECS 498-007：Deep Learning for CV ⭐ CS231n 升级版

### 课程元数据
| 字段 | 内容 |
|------|------|
| 开课 | UMich |
| 主讲 | **Justin Johnson**（CS231n 元老）|
| 先修 | Python + 矩阵论（求导）+ 微积分 |
| 语言 | Python |
| 难度 | 🌟🌟🌟🌟 |
| 学时 | 60-80 小时 |

**csdiy 评价**：**比 CS231n 更新更全**。从零教 PyTorch，递进式 Assignment 覆盖 CV 全阶段。

### 📑 5 个 Assignment（递进式，覆盖 CV 全流程）⭐

| A# | 主题 | 核心内容 |
|----|------|---------|
| **A1** | **PyTorch + Colab 入门** | 从零学框架；可当工具书 |
| **A2** ⭐ | **线性分类器 + 两层 NN + MNIST** | 从零实现；亲手训练识别手写数字 |
| **A3** ⭐⭐ | **CNN** | 感受卷积魅力；CIFAR-10 |
| **A4** ⭐⭐ | **目标检测** | 实现 One-Stage + Two-Stage Detector（两篇论文）|
| **A5** ⭐⭐⭐ | **RNN/LSTM + Transformer** | 从 CNN 到注意力；搭建 Transformer |

### 🎯 定位
- **CS231n 的现代版**——Justin Johnson 把 CS231n 内容更新到 Transformer 时代
- **Assignment 5 直达 Transformer**——一门课从 KNN 走到 Transformer

---

## 课程 #9 · Stanford CS224n：Natural Language Processing ⭐ NLP 入门

### 课程元数据
| 字段 | 内容 |
|------|------|
| 开课 | Stanford |
| 主讲 | **Chris Manning**（NLP 巨佬）|
| 先修 | 深度学习基础 + Python |
| 语言 | Python |
| 难度 | 🌟🌟🌟🌟 |
| 学时 | 80 小时 |
| 课程网站 | http://web.stanford.edu/class/cs224n/index.html |
| 资源 | https://github.com/PKUFlyingPig/CS224n |

### 📑 完整教学大纲（NLP 从词向量到 Transformer）

#### 🔵 词表示

| 主题 | 核心内容 | 关键概念 |
|------|---------|---------|
| **词向量（Word Embedding）** ⭐⭐ | 词的分布式表示 | word2vec（Skip-gram/CBOW）；GloVe |
| **Word2vec 数学** ⭐ | 中心词预测上下文 | 概率模型；负采样；梯度推导 |

#### 🟢 句法与语义

| 主题 | 核心内容 |
|------|---------|
| **词向量应用** | 相似度；类比（king-man+woman=queen）|
| **依存句法分析** ⭐ | 句子结构；转移/图算法 |

#### 🟡 序列模型 ⭐⭐ NLP 核心

| 主题 | 核心内容 | 数学 |
|------|---------|------|
| **RNN** ⭐ | 处理序列；隐状态 | $h_t=\tanh(W_{hh}h_{t-1}+W_{xh}x_t)$ |
| **LSTM/GRU** ⭐⭐ | 解决梯度消失；门控机制 | 遗忘门/输入门/输出门 |
| **Seq2Seq** ⭐ | 编码器-解码器；机器翻译 | |
| **注意力机制（Attention）** ⭐⭐⭐ | 解决长序列瓶颈 | $Attention(Q,K,V)=softmax(QK^T/\sqrt{d_k})V$ |

#### 🟣 Transformer 与现代 NLP ⭐⭐⭐

| 主题 | 核心内容 |
|------|---------|
| **Transformer** ⭐⭐⭐ | 完全基于注意力；并行化 |
| **预训练模型** | BERT/GPT 简介 |
| **机器翻译** | 完整 MT 流程 |

### 📑 5 个 Assignment + Final Project
1. 词向量探索
2. **Word2vec 实现** ⭐
3. 依存句法分析
4. **机器翻译（Seq2Seq + Attention）** ⭐⭐
5. **Transformer fine-tune** ⭐⭐

**Final Project** ⭐⭐：在 **SQuAD 数据集**训练 QA 模型。有学生大作业直接发了顶会论文！

---

## 课程 #10 · UCB CS285：Deep Reinforcement Learning ⭐ RL 入门

### 课程元数据
| 字段 | 内容 |
|------|------|
| 开课 | UC Berkeley |
| 主讲 | **Sergey Levine**（RL 领域领军，人很 nice）|
| 先修 | CS188, CS189 |
| 语言 | Python |
| 难度 | 🌟🌟🌟🌟 |
| 学时 | 80 小时 |
| 课程网站 | http://rail.eecs.berkeley.edu/deeprlcourse/ |
| YouTube | https://www.youtube.com/playlist?list=PL_iWQOsE6TfX7MaC6C3HcdOf1g337dlC9 |

### 📑 完整教学大纲（DRL 全谱系）⭐⭐

#### 🔵 模仿学习与策略梯度基础

| 主题 | 核心内容 |
|------|---------|
| **模仿学习** | 行为克隆（Behavior Cloning）；DAgger |
| **策略梯度（PG）** ⭐⭐ | REINFORCE；$\nabla J=\mathbb{E}[\nabla_\theta\log\pi_\theta(a\|s)R]$ |
| **方差降低** | 基线（baseline）；因果性 |

#### 🟢 Actor-Critic 与现代 PG

| 主题 | 核心内容 |
|------|---------|
| **Actor-Critic** ⭐⭐ | 策略（Actor）+ 价值（Critic）；偏差-方差权衡 |
| **TRPO/PPO** ⭐⭐ | 信赖域；PPO 是工业界主流（OpenAI Five/ChatGPT RLHF）|

#### 🟡 Value-based RL

| 主题 | 核心内容 |
|------|---------|
| **DQN** ⭐⭐ | 深度 Q 网络；经验回放；目标网络 |
| **Double DQN / Rainbow** | 减少过估计 |

#### 🟣 Model-based RL + 高级

| 主题 | 核心内容 |
|------|---------|
| **Model-based RL** ⭐ | 学习环境模型；规划 |
| **离线 RL（Offline RL）** | 从固定数据学习 |
| **RLHF 简介** | ChatGPT 的对齐技术（最新加入）|

### 📑 5 个编程作业（复现经典模型）
每次复现经典模型 + 对比，递交报告。作业有框架 + hint 填空。

### 🎯 在 AI 学习中的定位
- **DRL 的标准入门**——Sergey Levine 是该领域奠基人之一
- **PPO 是 ChatGPT RLHF 的核心算法** ⭐⭐⭐

---

## 课程 #11 · 国立台湾大学 李宏毅机器学习 ⭐⭐⭐ 最全中文 DL

### 课程元数据
| 字段 | 内容 |
|------|------|
| 开课 | 國立台灣大學 |
| 主讲 | **李宏毅**（风趣幽默，PPT 喜欢宝可梦等动漫元素）|
| 先修 | Python |
| 语言 | Python（中文授课）|
| 难度 | 🌟🌟🌟🌟 |
| 学时 | 80 小时 |
| 课程网站(2023) | https://speech.ee.ntu.edu.tw/~hylee/ml/2023-spring.php |
| 课程网站(2025) | https://speech.ee.ntu.edu.tw/~hylee/ml/2025-spring.php |

**csdiy 评价**：挂着 ML 牌子但**内容之广令人咋舌**。15 个 Lab 几乎覆盖 DL 所有领域。**最佳中文 DL 课程**。2025 版改革侧重 RAG/Agent/LLM。

### 📑 完整教学大纲（15 Lab，DL 全景）⭐⭐⭐

| Lab# | 主题 | 核心内容 |
|------|------|---------|
| 1 | **Regression** | 线性回归；梯度下降；过拟合 |
| 2 | **Classification** | 逻辑回归；交叉熵 |
| 3 | **CNN** ⭐ | 卷积；经典架构 |
| 4 | **Self-Attention** ⭐⭐ | 注意力机制（Transformer 前奏）|
| 5 | **Transformer** ⭐⭐⭐ | 完整 Transformer 实现 |
| 6 | **GAN** ⭐ | 生成对抗网络；对抗训练 |
| 7 | **BERT** ⭐⭐ | 预训练模型；fine-tune |
| 8 | **Anomaly Detection** | 异常检测 |
| 9 | **Explainable AI** | 可解释性 |
| 10 | **Attack** | 对抗攻击 |
| 11 | **Adaptation** | 域适应 |
| 12 | **RL** | 强化学习 |
| 13 | **Compression** | 模型压缩 |
| 14 | **Life-Long Learning** | 持续学习 |
| 15 | **Meta Learning** | 元学习（学会学习）|

**2025 版改革** ⭐：侧重 RAG/AI Agent/LLM 等最新方向。

### 🎯 在 AI 学习中的定位
- **中文 DL 学习者的首选**——一个课程看尽 DL 全景
- 适合建立**广度**后选择方向深入

---

## 课程 #12 · CMU 11-785：Introduction to Deep Learning ⭐ 硬核

### 课程元数据
| 字段 | 内容 |
|------|------|
| 开课 | CMU |
| 先修 | 线代 + 概率 + Python + ML 基础 |
| 语言 | Python |
| 难度 | 🌟🌟🌟🌟🌟 |
| 学时 | 120 小时 |
| 课程网站(S26) | https://deeplearning.cs.cmu.edu/S26/index.html |

**csdiy 评价**：**非常硬核**的 DL 核心课。风格扎实、节奏快、几乎没有水内容。研究生强度训练。

### 📑 核心教学主题
- 神经网络基础（反向传播推导）
- CNN / RNN
- **Attention / Transformer** ⭐
- **优化与泛化** ⭐⭐（理论深入，少见的深度）

**定位**：希望建立**长期可迁移**深度学习能力（而非只会调 API）的人。

---

## 课程 #13-16 · CS230 / MIT 6.7960 / NYU DLSP21 / CS224w
- **CS230**（Coursera DL，吴恩达）：DL 友好入门，5 门子课程
- **MIT 6.7960**（MIT DL）：MIT 版 DL，理论 + 实践
- **NYU DLSP21**（Yann LeCun）：NYU 深度学习，LeCun（CNN 之父）主讲
- **CS224w**（Stanford 图神经网络）⭐：GNN 专题——图卷积/GraphSAGE/GAT

---

# 第四大类 · 深度生成模型 + 大语言模型（4 门）⭐ 前沿

> **csdiy 导航**：含学习路线图 + MIT 6.S184（扩散模型）+ 3 门 LLM 课。

---

## 课程 #17 · MIT 6.S184：Generative AI with SDEs（扩散模型）⭐

**核心**：用随机微分方程（SDE）统一理解扩散模型。Score-based generative models；DDPM；条件生成。

## 课程 #18 · CMU 11-868：Large Language Model System（LLM 系统）⭐
**核心**：LLM 的系统层面——训练/推理/部署/服务化。

## 课程 #19 · CMU 11-667：LLM Methods and Applications ⭐
**核心**：LLM 方法与应用——prompt/fine-tune/RAG/Agent。

## 课程 #20 · CMU 11-711：Advanced NLP ⭐
**核心**：CMU 高级 NLP，研究导向。

---

# 第五大类 · 机器学习系统（5 门）⭐ 工程 + 系统交叉

> **定位**：ML 系统工程——如何高效训练/部署/服务 ML 模型。

---

## 课程 #21 · CMU 10-414/714：Deep Learning Systems ⭐⭐ 强推

**核心**：从零实现**深度学习框架**（类似 mini-PyTorch）。理解 Automatic Differentiation、GPU 编程、算子实现。

## 课程 #22 · MIT 6.5940：TinyML and Efficient DL Computing ⭐
**核心**：**高效深度学习**——量化/剪枝/蒸馏；边缘部署。联系 ai-deployment skill。

## 课程 #23 · Machine Learning Compilation（MLC）
**核心**：ML 编译——TVM/Relay；跨硬件部署。

## 课程 #24 · 智能计算系统（AICS）
**中文**：中科院计算所，从算法到芯片的全栈智能计算。

## 课程 #25 · UCSD CSE234：Data Systems for ML
**核心**：ML 数据系统——特征存储/向量数据库/数据流水线。

---

# 第六大类 · 机器学习进阶（5 门）⭐ 研究

---

## 课程 #26 · CMU 10-708：Probabilistic Graphical Models ⭐
**核心**：**概率图模型**——贝叶斯网络/马尔可夫随机场/变分推断。

## 课程 #27 · Columbia STAT 8201：Deep Generative Models
**核心**：深度生成模型——VAE/Flow/GAN/扩散。

## 课程 #28 · U Toronto STA 4273：Minimizing Expectations
**核心**：变分推断/重参数化/ELBO。

## 课程 #29 · Stanford STATS214/CS229M：ML Theory ⭐
**核心**：**ML 理论**——PAC 学习/泛化界/优化理论。

---

# 📊 AI/ML/DL 完整学习路径（csdiy 隐含路线 + AI 导师建议）

## 🤖 套餐 A：AI/ML 完整路径（csdiy 隐含）
```
数学基础(18.06/CS70/EE364A)
  → CS188(#1) 经典 AI（搜索/MDP/概率推理）
  → CS229(#5) ⭐ ML 理论圣经
  → Karpathy Zero to Hero(#3) ⭐⭐⭐ 从零实现 GPT
  → 深度学习方向课（见下）
```

## 🖼️ 套餐 B：计算机视觉（CV）方向
```
CS231n(#7) 或 EECS498(#8) ⭐ 更新 → 论文阅读 → 研究
```

## 💬 套餐 C：自然语言处理（NLP）/LLM 方向
```
CS224n(#9) → 李宏毅 BERT/Transformer → LLM 课(#18-20)
```

## 🎮 套餐 D：强化学习（RL）方向
```
CS188 MDP/RL → CS285(#10) ⭐ DRL → 论文阅读
```

## 🎨 套餐 E：生成模型方向
```
李宏毅 GAN → MIT 6.S184(#17) 扩散 → Columbia STAT8201(#27)
```

## ⚙️ 套餐 F：ML 系统工程方向 ⭐ 就业热门
```
CMU 10-414(#21) ⭐ 从零造框架 → MIT 6.5940(#22) 高效DL → MLC(#23) 编译
```

## 📚 套餐 G：中文学习路径
```
吴恩达 Coursera ML(#4) → 李宏毅(#11) ⭐⭐⭐ 全景 → 选方向深入
```

---

## ⚠️ 关键提醒（AI 导师视角）

1. **Karpathy Zero to Hero 是隐藏王者** ⭐⭐⭐——理解 DL 第一性原理，从零实现 GPT
2. **数学是根基**：SVM↔EE364A KKT；逻辑回归↔CS126 指数族；PCA↔18.06 SVD；交叉熵↔6.050J 熵；反向传播↔18.01 链式法则
3. **PPO 是 ChatGPT 的核心**——CS285 教的就是 ChatGPT RLHF 用的算法
4. **EECS498 比 CS231n 更现代**——Justin Johnson（CS231n 元老）的升级版，直达 Transformer
5. **李宏毅是中文 DL 之最**——15 Lab 覆盖 DL 全景，适合建立广度
6. **ML 系统方向就业极好**——CMU 10-414（造框架）+ MIT 6.5940（高效 DL）是大厂核心竞争力

---

## 📚 按课程编号索引（30 门）

| # | 课程 | 子类 | 难度 | 核心亮点 |
|---|------|------|------|---------|
| 1 | CS188 | AI | 🌟🌟🌟 | Pacman + 经典 AI |
| 2 | CS50 AI | AI | 🌟🌟🌟 | 12 精巧作业 |
| 3 | Karpathy Zero to Hero | AI | 🌟🌟🌟🌟 | ⭐⭐⭐ 从零实现 GPT |
| 4 | Coursera ML | ML | 🌟🌟🌟 | 吴恩达最友好入门 |
| 5 | CS229 | ML | 🌟🌟🌟🌟 | ⭐ ML 理论圣经 |
| 6 | CS189 | ML | 🌟🌟🌟🌟 | UCB 理论版 |
| 7 | CS231n | DL/CV | 🌟🌟🌟🌟 | 李飞飞，CV 入门 |
| 8 | EECS498 | DL/CV | 🌟🌟🌟🌟 | ⭐ CS231n 升级版 |
| 9 | CS224n | DL/NLP | 🌟🌟🌟🌟 | Manning，NLP 入门 |
| 10 | CS285 | DL/RL | 🌟🌟🌟🌟 | Levine，PPO 根基 |
| 11 | 李宏毅 | DL | 🌟🌟🌟🌟 | ⭐⭐⭐ 中文最全 DL |
| 12 | CMU 11-785 | DL | 🌟🌟🌟🌟🌟 | 硬核研究生强度 |
| 13-16 | CS230/MIT6.7960/NYU/CS224w | DL | 🌟🌟🌟🌟 | 各校 DL 课 |
| 17 | MIT 6.S184 | 生成 | 🌟🌟🌟🌟 | 扩散模型/SDE |
| 18 | CMU 11-868 | LLM | 🌟🌟🌟🌟 | LLM 系统 |
| 19 | CMU 11-667 | LLM | 🌟🌟🌟🌟 | LLM 方法应用 |
| 20 | CMU 11-711 | NLP | 🌟🌟🌟🌟🌟 | 高级 NLP |
| 21 | CMU 10-414 | ML系统 | 🌟🌟🌟🌟 | ⭐⭐ 从零造框架 |
| 22 | MIT 6.5940 | ML系统 | 🌟🌟🌟🌟 | ⭐ 高效 DL（量化/剪枝）|
| 23 | MLC | ML系统 | 🌟🌟🌟🌟 | ML 编译 |
| 24 | AICS | ML系统 | 🌟🌟🌟 | 中科院全栈 |
| 25 | CSE234 | ML系统 | 🌟🌟🌟 | ML 数据系统 |
| 26 | CMU 10-708 | ML进阶 | 🌟🌟🌟🌟🌟 | 概率图模型 |
| 27 | STAT 8201 | ML进阶 | 🌟🌟🌟🌟🌟 | 深度生成模型 |
| 28 | STA 4273 | ML进阶 | 🌟🌟🌟🌟 | 变分推断 |
| 29 | CS229M | ML进阶 | 🌟🌟🌟🌟🌟 | ML 理论 |

---

**文档版本**：v1.0（AI/ML/DL 30 门完整版）
**最后更新**：2026-07-07
