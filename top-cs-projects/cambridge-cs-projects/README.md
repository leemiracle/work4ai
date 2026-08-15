# 🎓 Cambridge CST (Tripos) 2026 - 全课程项目实战（完整版）

> **完成度**：✅ 全部 12 个主题 + 补充课程微项目
> **覆盖课程**：~40+ 门（核心 + 补充，Computer Science Tripos Part IA → Part III）
> **可运行代码**：12 个完整主题项目 + 30 个微项目

---

## 📊 主题完成情况

| # | 主题 | 项目文件 | 覆盖课程 | 状态 |
|---|------|---------|---------|------|
| 1 | 计算基础 | `topic1-foundations/foundations.py` | Part IA Foundations of CS | ✅ |
| 2 | 自动机理论 | `topic2-automata/automata.py` | Part IA Regular Languages & FA | ✅ |
| 3 | 算法 | `topic3-algorithms/algorithms.py` | Part IA/IB Algorithms | ✅ |
| 4 | 编译器 | `topic4-compiler/compiler.py` | Part IB Compiler Construction | ✅ |
| 5 | 操作系统 | `topic5-os/os.py` | Part IB Operating Systems | ✅ |
| 6 | 并发系统 | `topic6-concurrent/concurrent.py` | Part IB Concurrent & Distributed Systems | ✅ |
| 7 | 计算机网络 | `topic7-networks/networks.py` | Part IB Computer Networking | ✅ |
| 8 | 计算机视觉 | `topic8-vision/vision.py` | Part IB Computer Vision | ✅ |
| 9 | 机器学习与贝叶斯推断 | `topic9-ml/mbi.py` | Part IB ML & Bayesian Inference | ✅ |
| 10 | 深度学习 | `topic10-deep/deep.py` | Part II Deep Learning | ✅ |
| 11 | 自然语言处理 | `topic11-nlp/nlp.py` | Part II NLP | ✅ |
| 12 | 信息论与编码 | `topic12-info/info_theory.py` | Part II Information Theory & Coding | ✅ |
| 📚 | 补充 | `supplementary/*.py` | Part IA/IB/III 30 门 | ✅ |

---

## 🚀 快速开始

```bash
cd cambridge-cs-projects
bash run_all.sh

# 或单独运行补充课程
python3 supplementary/undergrad_projects.py
python3 supplementary/grad_projects.py
python3 supplementary/micro_projects.py
```

---

## 📦 共享基础设施（`core/`）

所有主题共享的模块（从 Stanford 样板适配）：

| 文件 | 内容 |
|------|------|
| `core/llm.py` | LLM 客户端（litellm + Mock 兜底，离线可用）|
| `core/rag.py` | RAG pipeline（chunking + embedding + retrieval）|
| `core/tools.py` | 工具集（calculator + search + file_reader）|
| `core/react.py` | ReAct 主循环（thought-action-observation）|
| `core/hybrid_search.py` | BM25 + Dense 混合检索 |
| `core/eval.py` | 4-tuple evaluation framework + pass@k |

---

## 🎯 各主题核心学习点

### 主题 1：Foundations of CS（Part IA）

**数学骨架**：
- Cantor 对角线：$D_i = 1 - L_{i,i}$，对角线翻转构造不在列表中的实数
- 停机问题归约：$\text{halts}(D, D) \Rightarrow \text{contradiction}$
- Schröder–Bernstein：$|A| \le |B| \wedge |B| \le |A| \Rightarrow |A| = |B|$

**算法**：Relation 传递闭包（Warshall/Floyd）、偏序格验证、函数类型分类。

**反直觉发现**：自然数和偶数「一样多」（无限集合的等势）。

---

### 主题 2：Regular Languages & Finite Automata（Part IA）

**数学骨架**：
- 子集构造：$\delta_{DFA}(S, a) = \bigcup_{s \in S} \epsilon\text{-closure}(\delta_{NFA}(s, a))$
- Pumping lemma：$\forall L \in \text{REG}, \exists p, \forall s \in L, |s| \ge p, \exists x,y,z: s=xyz, |xy| \le p, |y| \ge 1, \forall i \ge 0: xy^iz \in L$

**算法**：NFA→DFA 子集构造、Thompson regex→NFA、Hopcroft DFA 最小化。

**反直觉发现**：最坏情况 NFA $n$ 状态 → DFA $2^n$ 状态（指数爆炸）。

---

### 主题 3：Algorithms（Part IA/IB）

**数学骨架**：
- Master theorem：$T(n) = aT(n/b) + O(n^c)$，比较 $c$ 与 $\log_b a$
- LIS：$O(n \log n)$ patience sorting

**算法**：Mergesort（带逆序对计数）、Quickselect（期望 $O(n)$）、LIS、Coin Change DP、SAT→3SAT→Clique 归约链。

**反直觉发现**：Quickselect 找中位数只需 $O(n)$，比先排序 $O(n \log n)$ 更快。

---

### 主题 4：Compiler Construction（Part IB）

**算法**：Lexer（正则词法分析）、Recursive-descent parser（6 层优先级）、AST 构建、Type checker（int/bool 推断）、栈机 CodeGen + VM 执行。

**反直觉发现**：栈机只有 PUSH/LOAD/STORE/OP/JMP 几类指令，却能编译任意程序；递归下降天然映射运算符优先级。

---

### 主题 5：Operating Systems（Part IB）

**算法**：Round-Robin / SJF 调度、FIFO/LRU/Optimal 页面置换、inode-like FS（位图块分配）。

**反直觉发现**：**Belady 异常**——FIFO 增加帧数可能增加缺页率！LRU 不会（栈式算法）。

---

### 主题 6：Concurrent & Distributed Systems（Part IB）

**数学骨架**：
- CSP trace 等价：$P \equiv Q \iff \text{traces}(P) = \text{traces}(Q)$
- LTL：$\Box p$（always）、$\Diamond p$（eventually）、$p \to \Diamond q$（leads-to）

**算法**：Peterson 互斥验证、资源分配图死锁检测（wait-for 图找环）、CSP trace 操作、mini SPIN 模型检测。

**反直觉发现**：Peterson 仅用 2 flag + 1 turn 实现互斥（无需硬件原子指令）。

---

### 主题 7：Computer Networking（Part IB）

**算法**：TCP 状态机（三次握手/四次挥手/TIME_WAIT）、Reno 拥塞控制（慢启动→拥塞避免→快恢复）、Go-Back-N、CSMA/CD 时隙仿真。

**反直觉发现**：TCP 慢启动是**指数增长**（每 RTT 翻倍），不是「慢」；以太网在高负载下退化为 ALOHA（冲突风暴）。

---

### 主题 8：Computer Vision（Part IB）

**数学骨架**：
- Harris 角点：$R = \det(M) - k \cdot \text{trace}(M)^2$，$M = \sum \begin{bmatrix} I_x^2 & I_x I_y \\ I_x I_y & I_y^2 \end{bmatrix}$
- Lucas-Kanade：$I_x v_x + I_y v_y = -I_t$（亮度恒常假设）

**算法**：Sobel 边缘检测、HOG 描述子、Harris 角点、RANSAC 直线拟合、Lucas-Kanade 光流。

**反直觉发现**：RANSAC 用最少样本（2 点）反而最鲁棒（50% 离群率也能拟合）。

---

### 主题 9：ML & Bayesian Inference（Part IB）

**数学骨架**：
- 贝叶斯：$P(\theta|D) = \frac{P(D|\theta)P(\theta)}{P(D)}$
- GP 后验：$\mu_* = K_*^T(K+\sigma_n^2 I)^{-1}y$
- Metropolis 接受率：$\alpha = \min(1, \frac{p(x')}{p(x)})$

**算法**：贝叶斯线性回归（后验分布）、EM for GMM、Metropolis MCMC、GP 回归（RBF kernel）。

**反直觉发现**：MCMC 接受率不是越高越好（~23% 最优，太高 = 步长太小）；GP 在训练点附近方差小，远离训练点方差大。

---

### 主题 10：Deep Learning（Part II）

**数学骨架**：
- Attention：$\text{Attention}(Q,K,V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V$（Vaswani 2017, arXiv:1706.03762）
- MAF log-likelihood：$\log p(x) = \log p(u) + \log|\det J|$（Papamakarios 2017, arXiv:1705.07057）

**算法**：1D CNN（卷积+池化）、RNN char-LM、Self/Multi-head Attention、MAF Normalizing Flow。

**反直觉发现**：Normalizing Flow 可以精确计算 log-likelihood（GAN 不能）；卷积核 [1,-1] 就是离散导数。

---

### 主题 11：NLP（Part II）

**算法**：BPE 子词分词器（arXiv:1508.07909）、mini seq2seq + Bahdanau attention（arXiv:1409.0473）、mini BERT MLM（arXiv:1810.04805）、Beam search 解码。

**反直觉发现**：BPE 自动发现子词共享（low/lower/newest）；Beam search width=2 已捕获大多数收益。

---

### 主题 12：Information Theory & Coding（Part II）

**数学骨架**：
- 熵：$H(X) = -\sum_x p(x) \log_2 p(x)$
- Kraft 不等式：$\sum_i 2^{-l_i} \le 1$（前缀码存在条件）
- BSC 容量：$C = 1 - H(p)$（$H$ 为二元熵函数）

**算法**：熵/KL 计算、Kraft 不等式验证、Huffman 编码、LZ77 压缩、BSC 信道容量、(7,4) 汉明码编解码+纠错。

**反直觉发现**：均匀分布熵最大；BSC $p=0.5$ 时容量 $C=0$（完全噪声无法传输信息）；Huffman 平均码长 $< H + 1$ bit。

---

## 📈 整体统计

- **代码行数**：~4,100 行（核心 12 主题）+ ~1,300 行（补充）+ ~1,000 行（core/）
- **覆盖课程**：~40 门（12 主题课程 + 30 补充课程）
- **零外部依赖**（除 Python 标准库）：所有项目可在任何环境跑通
- **LaTeX 公式**：README + 代码注释中均包含

---

## 🎓 学习路径建议

### 想做 AI / ML 工程师（最 ROI 路径）
1. **topic3** Algorithms → 基础
2. **topic9** ML & Bayesian → 贝叶斯思维
3. **topic10** Deep Learning → CNN/RNN/Transformer
4. **topic11** NLP → 实战 NLP
5. **topic12** Information Theory → 理论深度
6. **topic5** OS → 系统工程

### 想做 AI 研究者
1. **topic1** Foundations（逻辑/可计算性）
2. **topic9** Bayesian Inference（GP/MCMC/EM）
3. **topic10** Deep Learning（Flow/Attention）
4. **topic2** Automata（理论根基）
5. **topic6** Concurrent（分布式 ML）

### 想做系统工程师 / PM
1. **topic5** OS
2. **topic7** Networking
3. **topic6** Concurrent
4. **topic4** Compiler
5. **supplementary** undergrad_projects（DB/ECAD/OOP）

---

## 📚 关键参考论文与教材

每个项目代码头部都列了参考。最重要的 10 篇/本：

1. **Hopcroft, Motwani & Ullman** 2006 *Introduction to Automata Theory, Languages, and Computation* 3rd ed — 主题 2
2. **MacKay** 2003 *Information Theory, Inference, and Learning Algorithms* — 主题 9/12
3. **Cover & Thomas** 2006 *Elements of Information Theory* 2nd ed — 主题 12
4. **Rasmussen & Williams** 2006 *Gaussian Processes for Machine Learning* — 主题 9
5. **Hoare** 1985 *Communicating Sequential Processes* — 主题 6
6. **Vaswani et al.** 2017 "Attention Is All You Need" arXiv:1706.03762 — 主题 10/11
7. **Devlin et al.** 2019 "BERT" arXiv:1810.04805 — 主题 11
8. **Bishop** 2006 *Pattern Recognition and Machine Learning* — 主题 9
9. **Turing** 1936 "On Computable Numbers" — 主题 1
10. **Shannon** 1948 "A Mathematical Theory of Communication" — 主题 12

---

## 🔮 下一步扩展

Cambridge Tripos 还有部分课程未单独实现（与已有主题重叠或需特殊环境）：

- **Part IA Digital Electronics** — 与 topic5 OS 部分重叠
- **Part II Artificial Intelligence** — 与 topic9/10 高度重叠
- **Part II Computer Systems Modelling** — 排队论可扩展
- **Part III Natural Language Processing** — 进阶，与 topic11 互补
- **Part III Probabilistic Machine Learning** — 与 topic9 进阶版

每个预计 200-400 行，可在 1-2 小时内完成。

---

## ✅ 项目验证

所有 12 主题已通过 `run_all.sh` 自动化测试。

```bash
$ bash run_all.sh
# 12 个主题 + 3 个补充文件 ✅ 全部 PASS
```

---

**完成日期**：2026-08-12
**版本**：1.0（覆盖 Cambridge Computer Science Tripos Part IA → Part III 核心课程）
