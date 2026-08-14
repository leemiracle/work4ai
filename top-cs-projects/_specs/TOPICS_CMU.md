# CMU 课程主题清单（12 主题）

> 大学：Carnegie Mellon University (School of Computer Science)
> 项目根：`~/ai/work4ai/cmu-cs-projects/`
> 参考规格：`~/ai/work4ai/top-cs-projects/_specs/TEMPLATE_SPEC.md`

---

## 12 个主题（topicN-dir/file.py）

### 1. `topic1-intro/fundamentals.py` — 15-112 Fundamentals of Programming
覆盖：minimax + alpha-beta 剪枝；动态规划（BlackJack 最优策略）；位置评估（Othello）。
要求：
- Tic-Tac-Toe AI（minimax + alpha-beta，永不输）
- BlackJack 状态价值迭代（DP）
- Othello 落子评估函数（角+边权重）
反直觉发现：minimax 在 4x4 Tic-Tac-Toe 上的搜索树大小 vs alpha-beta 剪枝后的节点数（>10x 缩减）。

### 2. `topic2-systems/csapp.py` — 15-213 Introduction to Computer Systems（CSAPP 教材）
覆盖：缓存层次；虚拟内存；malloc 实现。
要求：
- L1/L2 set-associative cache 模拟器（输入访存序列，输出命中率）
- 隐式空闲链表 malloc/free
- 虚拟地址→物理地址翻译（含 TLB）
反直觉发现：循环遍历 2D 数组 row-major vs col-major 的 cache miss 比（>50x）。

### 3. `topic3-database/dbms.py` — 15-445 Database Systems（Andy Pavlo）
覆盖：B+ tree；查询执行（join 算法）；MVCC。
要求：
- B+ tree 插入/查找（带分裂）
- 三种 join 对比：nested-loop / hash / sort-merge（计时）
- MVCC snapshot isolation 模拟（多事务并发，看读写冲突）
反直觉发现：sort-merge join 在已排序数据上比 hash join 还快（无 hash 计算）。

### 4. `topic4-distributed/dist_sys.py` — 15-440 + 15-721 Distributed Systems
覆盖：Paxos；2PC；vector clocks；leader election。
要求：
- 单 decree Paxos（多 Proposer，故障注入）
- 两阶段提交（Coordinator + 多 Participant）
- Vector clock 因果一致性检查
反直觉发现：Paxos 在 3 节点容忍 1 节点宕机；在 5 节点容忍 2 节点宕机——但 FLP 证明异步下不可能确定性终止。

### 5. `topic5-ml/ml.py` — 10-701 Introduction to Machine Learning
覆盖：logistic regression；GDA；GMM/EM；决策树。
要求：
- Logistic regression（梯度下降，纯 numpy 或纯 Python）
- Gaussian Discriminant Analysis（多类）
- EM 拟合 GMM
- ID3 决策树（信息增益）
反直觉发现：GDA 在数据少时优于 logistic（高斯假设强先验），数据多时被 logistic 反超（GDA 的生成式假设变弱）。

### 6. `topic6-pgm/pgm.py` — 10-708 Probabilistic Graphical Models
覆盖：variable elimination；junction tree；HMM；粒子滤波。
要求：
- Variable elimination（小图）
- Belief propagation（树结构）
- HMM forward-backward + Viterbi（POS tagging 玩具数据）
- Bootstrap particle filter
- Gibbs sampling on Ising model（2D 网格 8x8）
反直觉发现：Ising Gibbs 在 T<Tc（临界温度）下相关长度爆发，混合时间指数级。

### 7. `topic7-nlp/intro_nlp.py` — 11-411/611 Natural Language Processing
覆盖：HMM POS；PCFG parsing；word alignment。
要求：
- HMM POS tagger（Viterbi，2-tag 玩具语料）
- CKY parser for CNF PCFG
- IBM Model 1 词对齐（EM）
反直觉发现：IBM Model 1 在小语料上对低频词的 alignment 几乎随机（t(f|e) ≈ uniform）。

### 8. `topic8-deep/intro_dl.py` — 10-315/11-667 Introduction to Deep Learning
覆盖：MLP；CNN；RNN；self-attention。
要求：
- MLP + backprop（numpy；XOR + MNIST-3-类 玩具）
- CNN forward（conv2d + maxpool）
- Simple RNN（字符级 LM）
- Mini self-attention（4-token 序列）
反直觉发现：mini self-attention 的注意力矩阵在长序列上稀疏化（softmax 把概率压到 1-2 个 token）。

### 9. `topic9-vision/cv.py` — 16-385 Computer Vision
覆盖：HOG；Harris；RANSAC；光流。
要求：
- HOG descriptor（8x8 cell, 9 bin）
- Harris corner detector（梯度矩阵 M）
- RANSAC 直线拟合（含 outlier）
- Lucas-Kanade 光流（亮度恒定假设）
反直觉发现：RANSAC 在 80% outlier 下仍能找到正确直线（迭代次数 vs inlier 比例的指数衰减）。

### 10. `topic10-robot/robotics.py` — 16-735 + 16-687
覆盖：LQR；RRT*；graph-SLAM。
要求：
- LQR（线性系统 + 二次 cost，DARE 求解）
- RRT* 路径规划（2D 障碍）
- Graph SLAM（pose-graph，Gauss-Newton）
- iLQR（单步）
反直觉发现：LQR 反馈增益 K 在无限 horizon 下是常数（DARE 的不动点），但有限 horizon 下 K 时变（DP backward）。

### 11. `topic11-hci-med/hci_med.py` — 05-410 HCI + 17-556 ML in Healthcare
覆盖：Fitts；KLM/GOMS；clinical decision support。
要求：
- Fitts' Law 预测点击时间（ID = log2(D/W + 1)）
- KLM-GOMS 估算任务时间（K/P/B/H/M/T 操作符）
- 临床决策树（mortality risk from age + vitals）
- 假阳性/假阴性 tradeoff（不同阈值的 ROC）
反直觉发现：Fitts Law 在小目标（W<10px）上时间爆炸（log 函数）。

### 12. `topic12-theory/pl_fp.py` — 15-150 FP + 15-312 PL + 15-251 GITCS
覆盖：lambda calc；HM type inference；mini-Prolog；DFA minimization。
要求：
- Lambda calculus interpreter（CBV，alpha conversion + beta reduction）
- Hindley-Milner algorithm W（let + lambda + 应用）
- Mini-Prolog（unification + backtracking search）
- DFA minimization（Hopcroft）
反直觉发现：HM 类型推断能推出 `let id = fun x -> x in (id 1, id "a")` 是多态的，但 `(fun id -> (id 1, id "a"))` 不能（let-polymorphism 限制）。

---

## supplementary/ 补充课程

### `undergrad_projects.py`（覆盖本科其余 8-10 门）
- 15-122 Imperative Computation：循环不变量、合约（Hoare triple）
- 15-251 Great Ideas in TCS：停机问题归约、Gödel 不完备、P vs NP
- 15-462 Computer Graphics：光线追踪基础
- 15-213 buffer overflow：栈布局演示
- 15-110 CS 编程基础（Java/Python 入门）：basic sort
- 15-128 Freshman Immigration：数据结构 sweep
- 15-214 Software Architecture：依赖图、循环依赖检测
- 21-127 Concepts of Math：等势、Cantor 对角线
- 21-241 Matrices and Linear Algebra：QR 分解
- 21-259 Calculus in 3D：梯度/散度/旋度

### `grad_projects.py`（覆盖研究生其余 8-10 门）
- 10-708 PGM advanced：贝叶斯网络 learning
- 11-711 Advanced NLP：mini BERT
- 11-737 Multilingual NLP：cross-lingual embedding
- 15-721 Advanced DB：columnar storage + SIMD
- 15-749 Distributed Systems：Raft log replication
- 15-780 Advanced Optimization：内点法
- 15-826 Multimedia Data Mining：LSH
- 16-720 Computer Vision（grad）：bundle adjustment
- 16-824 Visual Learning：metric learning
- 17-804 ML for Healthcare：federated learning

### `micro_projects.py`（杂项 8-10 个）
- 11-411Hidden Markov：Baum-Welch 训练
- 14-733 Computational Photography：seam carving
- 15-388 Practical Data Science：pandas mini from scratch
- 15-463 Computational Photography：image blending
- 16-385 Image Processing：bilateral filter
- 17-556 Bias in clinical data：subgroup disparity
- 05-839 Privacy in ML：differential privacy noise
- 11-667 NLP for Healthcare：de-identification
- 08-725 Empirical Research Methods：power analysis

---

## 关键参考论文（README 用）
1. CSAPP textbook — Bryant & O'Hallaron
2. Database System Concepts — Silberschatz, Pavlo lectures
3. Lamport 1998 Part-Time Parliament (Paxos)
4. Pearl 1988 Probabilistic Reasoning (Bayes net)
5. Rabiner 1989 HMM tutorial
6. Brown 1993 IBM Model mathematics of statistical MT
7. Dalal & Triggs 2005 HOG (CVPR)
8. Harris & Stephens 1988 corners
9. Kalman 1960 LQR/Filtering
10. Wright 2015 ML in Healthcare textbook
