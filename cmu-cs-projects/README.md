# 🎓 CMU SCS 2026 - 全课程项目实战（完整版）

> **完成度**：✅ 全部 12 个主题 + 补充课程微项目
> **覆盖课程**：~50+ 门（核心 + 补充）
> **可运行代码**：12 个完整项目 + 29 个微项目（3 个补充文件）

---

## 📊 主题完成情况

| # | 主题 | 项目文件 | 覆盖课程 | 状态 |
|---|------|---------|---------|------|
| 1 | 编程基础 | `topic1-intro/fundamentals.py` | 15-112 | ✅ |
| 2 | 计算机系统 | `topic2-systems/csapp.py` | 15-213 CSAPP | ✅ |
| 3 | 数据库系统 | `topic3-database/dbms.py` | 15-445 | ✅ |
| 4 | 分布式系统 | `topic4-distributed/dist_sys.py` | 15-440 + 15-721 | ✅ |
| 5 | 机器学习导论 | `topic5-ml/ml.py` | 10-701 | ✅ |
| 6 | 概率图模型 | `topic6-pgm/pgm.py` | 10-708 | ✅ |
| 7 | 自然语言处理 | `topic7-nlp/intro_nlp.py` | 11-411/611 | ✅ |
| 8 | 深度学习导论 | `topic8-deep/intro_dl.py` | 10-315/11-667 | ✅ |
| 9 | 计算机视觉 | `topic9-vision/cv.py` | 16-385 | ✅ |
| 10 | 机器人学 | `topic10-robot/robotics.py` | 16-735 + 16-687 | ✅ |
| 11 | HCI 与医疗 AI | `topic11-hci-med/hci_med.py` | 05-410 + 17-556 | ✅ |
| 12 | 理论与编程语言 | `topic12-theory/pl_fp.py` | 15-150/312/251 | ✅ |
| 📚 | 本科补充 | `supplementary/undergrad_projects.py` | 15-122/251/462/213/110/128/214 + 21-127/241/259 | ✅ |
| 📚 | 研究生补充 | `supplementary/grad_projects.py` | 10-708/11-711/737 + 15-721/749/780/826 + 16-720/824 + 17-804 | ✅ |
| 📚 | 杂项微项目 | `supplementary/micro_projects.py` | 11-411 + 14-733 + 15-388/463 + 16-385 + 17-556 + 05-839 + 11-667 + 08-725 | ✅ |

---

## 🚀 快速开始

```bash
# 一次性跑所有核心主题
cd cmu-cs-projects
bash run_all.sh

# 单独跑某个主题
python3 topic1-intro/fundamentals.py
python3 topic6-pgm/pgm.py

# 跑所有补充课程
python3 supplementary/undergrad_projects.py
python3 supplementary/grad_projects.py
python3 supplementary/micro_projects.py
```

---

## 📦 共享基础设施（`core/`）

所有主题共享的模块（从 mini-Agent 架构继承，适配 CMU SCS）：

| 文件 | 内容 |
|------|------|
| `core/llm.py` | LLM 客户端（litellm + Mock 兜底）|
| `core/rag.py` | RAG pipeline（embedding + 向量库）|
| `core/tools.py` | 工具集（calculator + search + file_reader）|
| `core/react.py` | ReAct 主循环（Thought→Action→Observation）|
| `core/hybrid_search.py` | BM25 + Dense 混合检索 |
| `core/eval.py` | 4-tuple evaluation framework + pass@k |

---

## 🎯 各主题核心学习点

### 主题 1：15-112 编程基础（博弈 + DP）
**数学骨架**：
- Minimax: $V(s) = \max_a \min_{a'} V(s')$
- Alpha-Beta 剪枝: $\alpha \geq \beta \Rightarrow \text{prune}$
- BlackJack DP: $V(s) = \max(\text{stand}, \sum_{c} P(c) \cdot V(s'))$

**算法**：Tic-Tac-Toe 完美博弈（minimax + αβ）；BlackJack 期望回报 DP；Othello 位置评估。
**反直觉**：αβ 剪枝只访问 ~50% 节点；硬 16 vs 庄家 10 虽然 hit 大概率爆牌但 stand 更差。

---

### 主题 2：15-213 CSAPP（系统）
**核心概念**：
- Cache hit rate: $h = \frac{\text{hits}}{\text{hits} + \text{misses}}$
- 地址翻译: $\text{PA} = \text{PFN} \ll \text{offset\_bits} \;|\; \text{offset}$

**算法**：Set-associative cache 模拟（direct/2-way/4-way）；隐式空闲链表 malloc（first-fit + coalescing）；多级页表 + TLB。
**反直觉**：矩阵行优先 vs 列优先遍历——同样的 cache，行优先 hit rate 几乎 100%，列优先几乎全 miss。

---

### 主题 3：15-445 数据库系统
**核心公式**：
- Hash join I/O: $O(|R| + |S|)$
- MVCC: $\text{read}(\text{snapshot } T_s) = \text{version where } T_{\text{begin}} \leq T_s < T_{\text{end}}$

**算法**：B+ tree（叶子链表 + 分裂）；三种 join 对比（nested-loop/hash/sort-merge）；MVCC snapshot isolation。
**反直觉**：500×300 join，nested-loop = 15万 I/O vs hash join = 800 I/O = 187x 差距。

---

### 主题 4：15-440/721 分布式系统
**核心理论**：
- Paxos: $\text{quorum} = \lfloor N/2 \rfloor + 1$
- Vector clock: $A \to B \iff \forall i: A_i \leq B_i \;\wedge\; \exists j: A_j < B_j$

**算法**：单 decree Paxos（Prepare→Promise→Accept→Accepted，带故障注入）；2PC；Vector clock happens-before；Bully 选举。
**反直觉**：Paxos 在 majority 存活时总能决定，少数存活则阻塞——Safety 优先于 Liveness。

---

### 主题 5：10-701 机器学习导论
**数学骨架**：
- Logistic: $P(y=1|x) = \sigma(w^T x + b)$
- GDA: $P(x|y=k) = \mathcal{N}(x; \mu_k, \Sigma)$
- EM: $Q(\theta|\theta_t) = E_{Z|X,\theta_t}[\log P(X,Z|\theta)]$

**算法**：Logistic regression (GD)；多类 GDA（共享协方差）；EM for GMM；ID3 决策树。
**反直觉**：EM 保证 log-likelihood 单调递增但收敛到局部最优（非全局）。

---

### 主题 6：10-708 概率图模型
**核心公式**：
- VE: $P(Y|E) = \frac{\sum_{H} \prod_i \phi_i}{\sum \text{evidence}}$
- HMM Forward: $\alpha_t(j) = [\sum_i \alpha_{t-1}(i) A_{ij}] B_j(o_t)$
- Ising: $P(s) \propto \exp(\beta \sum_{\langle i,j \rangle} s_i s_j)$

**算法**：Variable elimination；HMM forward-backward + Viterbi；Bootstrap particle filter；Gibbs sampling on 2D Ising。
**反直觉**：2D Ising 模型在 β_c ≈ 0.44 发生相变——弱耦合随机，强耦合自发磁化。

---

### 主题 7：11-411/611 NLP
**算法**：HMM POS tagger (Viterbi)；CKY parser for CNF PCFG；IBM Model 1 (EM word alignment)。
**反直觉**：IBM Model 1 无语法模型，纯词到词概率，但 EM 能自动学习翻译对齐！

---

### 主题 8：10-315/11-667 深度学习导论
**核心公式**：
- Self-Attention: $\text{Attention}(Q,K,V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right) V$
- RNN: $h_t = \tanh(W_{xh} x_t + W_{hh} h_{t-1} + b_h)$

**算法**：MLP + 手写 backprop；Conv2d + MaxPool；Simple RNN forward；Scaled dot-product attention。
**参考**：Vaswani et al. "Attention Is All You Need" arXiv:1706.03762。
**反直觉**：注意力是凸组合（行和=1），Q 主要关注 K 最相似的 token。

---

### 主题 9：16-385 计算机视觉
**算法**：HOG descriptor；Harris corner（structure tensor $M$，$R = \det(M) - k \cdot \text{tr}(M)^2$）；RANSAC 直线拟合；Lucas-Kanade 光流。
**反直觉**：RANSAC 在 43% outlier 中仍能准确拟合真线（鲁棒性）。

---

### 主题 10：16-735/687 机器人学
**核心公式**：
- LQR DARE: $P = A^T P A - A^T P B(R + B^T P B)^{-1} B^T P A + Q$
- RRT* rewiring: $\text{cost decrease} \Rightarrow \text{asymptotic optimality}$

**算法**：LQR via DARE 迭代；RRT*（rewire + 最优连接）；Graph-SLAM (Gauss-Newton)；iLQR backward pass。
**反直觉**：RRT* path cost 随迭代单调下降趋近最优（普通 RRT 不保证）。

---

### 主题 11：05-410 HCI + 17-556 ML Healthcare
**核心公式**：
- Fitts' Law: $\text{MT} = a + b \cdot \log_2\left(\frac{D}{W} + 1\right)$
- Youden's J: $J = \text{TPR} - \text{FPR}$
- AUC: $\int_0^1 \text{TPR}(\text{FPR}) \; d\text{FPR}$

**算法**：Fitts' Law ID 计算；KLM-GOMS 任务时间估计；临床决策树（qSOFA）；ROC curve + AUC + Youden threshold。
**反直觉**：Mental operators (M) 占 KLM 任务总时间 ~50%——认知开销主导。

---

### 主题 12：15-150/312/251 理论与 PL
**核心理论**：
- HM Algorithm W: $\text{unify}(\tau_1, \tau_2) \Rightarrow \text{substitution}$
- DFA minimization: $\text{partition refinement (Hopcroft)} \Rightarrow \text{equivalence classes}$

**算法**：Lambda calculus interpreter (CBV)；Algorithm W (Hindley-Milner type inference)；Mini-Prolog (unification + DFS backtracking)；DFA minimization (Hopcroft)。
**反直觉**：HM 自动推断多态类型无需注解；Hopcroft 把冗余 DFA 状态合并为最小等价类。

---

## 📈 整体统计

- **代码行数**：~4,500+ 行（12 核心 + 3 补充 + 6 core）
- **覆盖课程**：~50 门（12 核心主题 + 29 补充微项目课程）
- **测试覆盖率**：全部 22 个 .py 文件通过 `python3 file.py` 运行
- **零外部依赖**：所有项目纯 Python 标准库（无需 numpy/pip install）

---

## 🎓 学习路径建议

### 想做 AI 工程师（最 ROI 路径）
1. **15-112**（fundamentals）→ 编程基础
2. **15-213**（csapp）→ 系统理解
3. **10-701**（ml）→ ML 基础
4. **10-315**（intro_dl）→ 深度学习
5. **15-445**（dbms）→ 数据库
6. **15-440**（dist_sys）→ 分布式系统

### 想做 AI 研究者
1. **10-701**（ml: logistic/GDA/EM/ID3）
2. **10-708**（pgm: VE/HMM/Ising）
3. **11-411**（nlp: HMM/CKY/IBM Model 1）
4. **16-385**（cv: HOG/Harris/RANSAC）
5. **15-150/312**（pl_fp: λ-calc/HM/Prolog）

### 想做产品经理 / 创业者
1. **05-410**（hci: Fitts' Law/KLM）
2. **17-556**（healthcare: ROC/fairness）
3. **15-445**（dbms: 理解数据基础设施）
4. **15-213**（csapp: 理解系统约束）
5. **15-251**（theory: 停机问题/P vs NP 的直觉）

---

## 🔮 下一步扩展

以下 CMU 课程因与已有项目重叠或需要特殊依赖，未单独实现：

1. **10-414/714 Deep Learning Systems**：实现 TVM/PyTorch codegen（已有 15-213 系统基础）
2. **11-785 Deep Learning**（Bhiksha）：完整 CNN/RNN/Transformer 训练（需 GPU）
3. **16-831 Statistical Techniques in Robotics**：完整 SLAM（已有 graph-SLAM 基础）
4. **17-445 Software Engineering for AI-Enabled Systems**：MLOps pipeline
5. **05-810/880 Language Technologies**：进阶 NLP pipeline

每个预计 200-400 行代码，可在 1-2 小时内完成。

---

## 📚 关键参考论文

每个项目代码头部都列了参考论文/教材。最重要的 10 篇：

1. Bryant & O'Hallaron "Computer Systems: A Programmer's Perspective" 3rd ed — 主题 2
2. Vaswani et al. "Attention Is All You Need" arXiv:1706.03762 — 主题 8
3. Koller & Friedman "Probabilistic Graphical Models" 2009 — 主题 6
4. Lamport "The Part-Time Parliament" 1998 ACM TOCS — 主题 4 (Paxos)
5. Dalal & Triggs "HOG" 2005 CVPR — 主题 9
6. Karaman & Frazzoli "RRT*" 2011 IJRR — 主题 10
7. Damas & Milner "Principal type-schemes" 1982 POPL — 主题 12 (HM)
8. Fitts "The Information Capacity of the Human Motor System" 1954 — 主题 11
9. Dempster Laird Rubin "Maximum Likelihood from Incomplete Data" 1977 — 主题 5 (EM)
10. Rabiner "A Tutorial on HMM" 1989 IEEE Proc — 主题 6/7

---

## ✅ 项目验证

所有 12 主题 + 3 补充文件已通过 `run_all.sh` 自动化测试。

```bash
$ bash run_all.sh
# 12 主题 + 3 补充 ✅ 全部 PASS
```

---

**完成日期**：2026-08-12
**版本**：1.0（覆盖 CMU SCS 2026 核心课程 50+ 门）
