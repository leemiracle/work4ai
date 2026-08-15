# 🎓 UC Berkeley EECS 2026 - 全课程项目实战（完整版）

> **完成度**：✅ 全部 12 个主题 + 补充课程微项目
> **覆盖课程**：~60+ 门（核心 + 补充）
> **可运行代码**：12 个完整主题项目 + 30 个微项目

---

## 📊 主题完成情况

| # | 主题 | 项目文件 | 覆盖课程 | 状态 |
|---|------|---------|---------|------|
| 1 | SICP / 编程抽象 | `topic1-sicp/sicp.py` | CS 61A | ✅ |
| 2 | 数据结构 | `topic2-dsa/data_structures.py` | CS 61B | ✅ |
| 3 | 体系结构 | `topic3-arch/arch.py` | CS 61C | ✅ |
| 4 | 离散数学 | `topic4-discrete/discrete.py` | CS 70 | ✅ |
| 5 | 人工智能 | `topic5-ai/ai_pacman.py` | CS 188 | ✅ |
| 6 | 机器学习 | `topic6-ml/ml_classic.py` | CS 189 | ✅ |
| 7 | 深度强化学习 | `topic7-rl/deep_rl.py` | CS 285 | ✅ |
| 8 | 自然语言处理 | `topic8-nlp/nlp.py` | CS 288 | ✅ |
| 9 | 计算机视觉 | `topic9-vision/vision.py` | CS 280 | ✅ |
| 10 | 操作系统 | `topic10-os/os.py` | CS 162 | ✅ |
| 11 | 数据科学 | `topic11-data/data_science.py` | Data 8 / 100 | ✅ |
| 12 | 最优化 | `topic12-opt/optimization.py` | EECS 127 | ✅ |
| 13 | 计算机安全 | `topic13-sec/cs161_security.py` | CS 161 | ✅ |
| 📚 | 补充本科 | `supplementary/undergrad_projects.py` | CS 61A进阶/70进阶/EE16A/CS170/161/164/169/174/C100/EE120 | ✅ |
| 📚 | 补充研究生 | `supplementary/grad_projects.py` | CS 288/294/267/287/294-141/294-165/280/EE227BT/281A/C267 | ✅ |
| 📚 | 杂项微项目 | `supplementary/micro_projects.py` | CS 198/9K/Data6/188进阶/M11/Stat154/EE127/CS191/198-126/198-127 | ✅ |

---

## 🚀 快速开始

```bash
cd berkeley-cs-projects
bash run_all.sh

# 或单独运行补充课程
python3 supplementary/undergrad_projects.py
python3 supplementary/grad_projects.py
python3 supplementary/micro_projects.py
```

---

## 📦 共享基础设施（`core/`）

所有主题共享的模块：

| 文件 | 内容 |
|------|------|
| `core/llm.py` | LLM 客户端（litellm + Mock 兜底）|
| `core/rag.py` | RAG pipeline（embedding + 向量库）|
| `core/tools.py` | 工具集（calculator + search + file_reader）|
| `core/react.py` | ReAct 主循环 |
| `core/hybrid_search.py` | BM25 + Dense 混合检索 |
| `core/eval.py` | 4-tuple evaluation framework + pass@k |

---

## 🎯 各主题核心学习点

### 主题 1：CS 61A SICP (Python) — DeNero
**数学/算法骨架**：
- 树递归复杂度：$T(n) = O(\phi^n)$，$\phi = \frac{1+\sqrt{5}}{2} \approx 1.618$
- Memo 化：$O(2^n) \to O(n)$
- Scheme 求值器：`eval(expr, env) → apply(proc, args)`

**反直觉发现**：`fib(30)` 树递归调用 ~270 万次，memo 版仅 30 次（90,000× 差距）。

---

### 主题 2：CS 61B 数据结构 — Hug
**核心算法**：
- 红黑树插入修复：3 种 case + 镜像，保证高度 $\leq 2\log(n+1)$
- 哈希表：chaining vs linear probing，load factor 触发 resize
- 图：DFS/BFS/拓扑排序（Kahn 算法）

**反直觉发现**：RB-tree 升序插入 31 个元素，black-height=5（普通 BST 退化为高度 31 的链表）。

---

### 主题 3：CS 61C 机器结构
**核心模型**：
- RISC-V 5 段流水线：IF → ID → EX → MEM → WB
- Data hazard + forwarding：$CPI_{forward} < CPI_{no\_forward}$
- IEEE 754：$(-1)^s \times 1.\text{mantissa} \times 2^{e-127}$
- Cache 3C 模型：Compulsory / Capacity / Conflict miss

**反直觉发现**：Direct-mapped cache 即使未满也 thrash（冲突 miss），forwarding 让 CPI 从 ~2.0 → ~1.3。

---

### 主题 4：CS 70 离散数学与概率
**数学公式**：
- RSA：$c = m^e \bmod n$，$m = c^d \bmod n$，$ed \equiv 1 \pmod{\phi(n)}$
- Erdős–Rényi 连通阈值：$p^* = \frac{\ln n}{n}$
- Markov 平稳分布：$\pi = \pi P$，power iteration 收敛
- Stirling：$n! \approx \sqrt{2\pi n}(n/e)^n$

**反直觉发现**：$G(n,p)$ 连通性在 $p^* = \ln n / n$ 附近尖锐相变（离散数学中的"冰点"）。

---

### 主题 5：CS 188 AI — Pacman (Klein)
**核心算法**：
- A* 搜索：$f(n) = g(n) + h(n)$，$h$ admissible
- Minimax + $\alpha\beta$ 剪枝：最优情况 $O(b^{d/2})$ vs 全搜索 $O(b^d)$
- Value Iteration：$V^*(s) = \max_a \sum_{s'} P(s'|s,a)[R + \gamma V^*(s')]$
- Q-Learning：$Q(s,a) \leftarrow Q(s,a) + \alpha[r + \gamma \max_{a'} Q(s',a') - Q(s,a)]$
- Bayes net 枚举：$P(X|e) \propto \sum_h P(X, e, h)$

**反直觉发现**：$\alpha\beta$ 在分支因子 $b$、深度 $d$ 上最优只需 $O(b^{d/2})$ → 可搜索深度翻倍。

> 🆕 **按 SP26 P0-P5 迭代组织的完整整合**：[`topic5-ai/cs188-sp26-pacman-projects.md`](./topic5-ai/cs188-sp26-pacman-projects.md)（6 个迭代专章 + autograder 拆解 + 学生卡点 + 项目内连接）+ 配套代码 [`cs188_sp26_iterations.py`](./topic5-ai/cs188_sp26_iterations.py)（5 个迭代核心算法跑通：DFS/BFS/A* + Minimax/Expectimax + Value Iteration/Q-Learning + HMM Forward + Perceptron）。

---

### 主题 6：CS 189 机器学习 — Sahai/Hasson
**核心公式**：
- 线性回归正规方程：$\mathbf{w} = (X^TX)^{-1}X^T\mathbf{y}$
- 逻辑回归：$P(y=1|\mathbf{x}) = \sigma(\mathbf{w}^T\mathbf{x} + b)$
- GDA：$P(\mathbf{x}|y=k) \sim \mathcal{N}(\mu_k, \Sigma)$
- 决策树 Gini：$Gini(S) = 1 - \sum_i p_i^2$

**反直觉发现**：XOR 数据上逻辑回归 ≈ 50%（线性不可分），决策树 95%。选模型 = 选归纳偏置。

---

### 主题 7：CS 285 深度强化学习 — Levine
**核心公式**：
- Policy Gradient：$\nabla J(\theta) = \mathbb{E}[\nabla \log \pi_\theta(a|s) \cdot G_t]$
- DQN target：$y = r + \gamma \max_{a'} Q_{target}(s', a')$
- SAC max-entropy：$\max \mathbb{E}[\sum_t r_t + \alpha \mathcal{H}(\pi(\cdot|s_t))]$
- TRPO：$\max_\theta \hat{E}[\frac{\pi_\theta}{\pi_{old}} \hat{A}]$ s.t. $\hat{E}[KL] \leq \delta$

**反直觉发现**：SAC 的 $\alpha$ 控制探索-利用平衡。高 $\alpha$ → 策略接近均匀（强探索），低 $\alpha$ → 贪心收敛。

---

### 主题 8：CS 288 自然语言处理
**核心算法**：
- HMM Forward：$\alpha_{t+1}(j) = [\sum_i \alpha_t(i) A_{ij}] B_j(o_{t+1})$
- Viterbi：$\delta_t(j) = \max_i [\delta_{t-1}(i) A_{ij}] \cdot B_j(o_t)$
- PCFG CKY：$O(n^3)$ parsing
- Attention：$\text{Att}(q, K) = \text{softmax}(qK^T)V$
- IBM Model 1：EM 隐式词对齐

**反直觉发现**：IBM Model 1 没有显式"对齐"变量，但 EM 通过期望自动发现对齐结构。$t(\text{狗}|\text{dog})$ 从 0.5 → ~0.9。

---

### 主题 9：CS 280 计算机视觉 — Malik/Efros
**核心算法**：
- Sobel：$G = \sqrt{G_x^2 + G_y^2}$
- Canny：Sobel → NMS → 双阈值
- HOG：cell 方向直方图 + block L2 归一化
- RANSAC：$P(\text{at least one clean sample}) = 1 - (1-p^n)^N$
- CNN：Conv → ReLU → Pool → FC

**反直觉发现**：RANSAC 在 47% 离群率下仍能精确找到直线。投票机制天然抗离群。

---

### 主题 10：CS 162 操作系统
**核心算法**：
- Lottery Scheduling：$P(\text{proc}_i \text{ runs}) = \frac{\text{tickets}_i}{\sum \text{tickets}}$
- CFS：vruntime $\propto \frac{\text{actual runtime}}{\text{weight(nice)}}$
- 多级页表 + TLB
- LFS：顺序追加写 + segment + compaction
- 死锁 4 条件（Coffman）：互斥/持有等待/非抢占/循环等待

**反直觉发现**：哲学家就餐中让 1 个哲学家"反着拿叉"即可打破循环等待，消除死锁。LFS 顺序写吞吐达带宽 80%（传统 FS 5-10%）。

---

### 主题 11：Data 8 / Data 100 — Adhikari
**核心方法**：
- Bootstrap CI：$\hat{\theta}^*_{(1)}, ..., \hat{\theta}^*_{(B)}$ → 取 $[\alpha/2, 1-\alpha/2]$ 分位数
- OLS：$\hat{\beta} = (X^TX)^{-1}X^Ty$，$R^2 = 1 - SS_{res}/SS_{tot}$
- SQL-like query：SELECT...WHERE...GROUP BY...HAVING...ORDER BY

**反直觉发现**：右偏分布中 Bootstrap 均值 CI 比中位数 CI 宽。$R^2$ 高 ≠ 模型正确。

---

### 主题 12：EECS 127 最优化
**核心公式**：
- LP Simplex：进基（max reduced cost）→ 出基（min ratio test）
- KKT 条件：stationarity / primal feasibility / dual feasibility / complementary slackness
- Newton：$\mathbf{x}_{k+1} = \mathbf{x}_k - H^{-1}\nabla f$
- Adam：$m_t = \beta_1 m_{t-1} + (1-\beta_1)g_t$，$v_t = \beta_2 v_{t-1} + (1-\beta_2)g_t^2$

**反直觉发现**：病态 Rosenbrock 函数上 GD 500 步几乎不动，Adam 好得多。Newton 在二次函数上一步到机器精度（二阶收敛 vs 一阶收敛）。

---

## 📈 整体统计

- **代码行数**：~4,500 行（12 主题）+ ~1,200 行（补充）+ ~1,500 行（core）
- **覆盖课程**：~60 门（12 主题课程 + 30 补充课程）
- **零外部依赖**（仅 Python 标准库 + 可选 numpy）：所有项目可在任何环境跑通
- **每个文件自包含**：`python3 file.py` 一键运行

---

## 🎓 学习路径建议

### 🛠️ AI Engineer 路径（最 ROI）
1. **CS 61A**（sicp.py）→ 编程抽象基础
2. **CS 61B**（data_structures.py）→ 数据结构 + 算法
3. **CS 189**（ml_classic.py）→ 机器学习经典算法
4. **CS 188**（ai_pacman.py）→ 搜索 + RL 基础
5. **CS 285**（deep_rl.py）→ 深度 RL
6. **CS 162**（os.py）→ 系统工程

### 🔬 AI Researcher 路径
1. **CS 70**（discrete.py）→ 数学基础
2. **CS 189**（ml_classic.py）→ ML 理论
3. **CS 288**（nlp.py）→ NLP 前沿
4. **CS 280**（vision.py）→ CV 前沿
5. **EECS 127**（optimization.py）→ 优化理论
6. **CS 285**（deep_rl.py）→ RL 研究

### 🚀 Founder / PM 路径
1. **CS 61A**（sicp.py）→ 抽象思维
2. **Data 8 / 100**（data_science.py）→ 数据驱动决策
3. **CS 188**（ai_pacman.py）→ AI 能力边界
4. **CS 162**（os.py）→ 系统设计
5. **CS 169**（supplementary）→ SaaS / REST API

---

## 📚 关键参考论文

每个项目代码头部都列了参考论文/教材。最重要的 10 篇：

1. **SICP** — Abelson & Sussman (MIT Press 1996) — 主题 1
2. **Red-Black Tree** — CLRS §13 (MIT 2009) — 主题 2
3. **Computer Organization RISC-V** — Patterson & Hennessy (MK 2020) — 主题 3
4. **RSA** — Rivest, Shamir, Adleman (CACM 1978) — 主题 4
5. **AIMA** — Russell & Norvig 4th ed (2021) — 主题 5
6. **ESL** — Hastie, Tibshirani, Friedman (Springer 2009) — 主题 6
7. **SAC** — Haarnoja et al. (ICML 2018, arXiv:1801.01290) — 主题 7
8. **HMM Tutorial** — Rabiner (Proc IEEE 1989) — 主题 8
9. **HOG** — Dalal & Triggs (CVPR 2005) — 主题 9
10. **Convex Optimization** — Boyd & Vandenberghe (Cambridge 2004) — 主题 12

---

## ✅ 项目验证

所有 12 主题已通过 `run_all.sh` 自动化测试。

```bash
$ bash run_all.sh
# 12 个项目 + 3 个补充文件 ✅ 全部 PASS
```

---

**完成日期**：2026-08-12
**作者**：AI Mentor + 学生
**版本**：1.0（覆盖 UC Berkeley EECS 2026 核心课程）
