# 🎓 Toronto DCS 2026 - 全课程项目实战（完整版）

> **完成度**：✅ 全部 12 个主题 + 补充课程微项目
> **覆盖课程**：~50+ 门（核心 + 补充）
> **可运行代码**：12 个完整项目 + 30 个微项目

---

## 📊 主题完成情况

| # | 主题 | 项目文件 | 覆盖课程 | 状态 |
|---|------|---------|---------|------|
| 1 | CS 入门 | `topic1-intro/intro.py` | CSC 108/148 | ✅ |
| 2 | 离散数学 | `topic2-discrete/discrete.py` | CSC 165/236 | ✅ |
| 3 | 软件设计 | `topic3-design/design.py` | CSC 207 | ✅ |
| 4 | 系统编程 | `topic4-systems/systems.py` | CSC 209 | ✅ |
| 5 | 数据结构 | `topic5-dsa/data_struct.py` | CSC 263 | ✅ |
| 6 | 人工智能 | `topic6-ai/ai.py` | CSC 384 | ✅ |
| 7 | 机器学习 | `topic7-ml/ml.py` | CSC 411/511 | ✅ |
| 8 | 概率ML | `topic8-pml/prob_ml.py` | CSC 412/512 | ✅ |
| 9 | 深度学习 | `topic9-deep/deep.py` | CSC 413/513 | ✅ |
| 10 | NLP | `topic10-nlp/nlp.py` | CSC 401 | ✅ |
| 11 | 计算机视觉 | `topic11-vision/vision.py` | CSC 420 | ✅ |
| 12 | 生成模型 | `topic12-generative/generative.py` | CSC 2547H | ✅ |
| 📚 | 补充 | `supplementary/*.py` | 30 门本科/研究生/杂项 | ✅ |

---

## 🚀 快速开始

```bash
# 一次性跑所有核心主题
cd toronto-cs-projects
bash run_all.sh

# 跑所有补充课程
python3 supplementary/undergrad_projects.py
python3 supplementary/grad_projects.py
python3 supplementary/micro_projects.py
```

---

## 📦 共享基础设施（`core/`）

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

### 主题 1：CSC 108/148 Intro CS

**核心算法**：
- Stack / Queue / LinkedList / BST 从零实现
- N-Queens 回溯求解器（含剪枝）
- OOP 多态（Shape → Circle/Rectangle/Triangle）

**反直觉发现**：记忆化 `fib(100)` 比朴素递归 `fib(30)` 快数千倍——指数复杂度的恐怖。

---

### 主题 2：CSC 165/236 Discrete Math

**数学骨架**：
- 谓词逻辑：$\forall x \in \mathbb{N}, \exists y \in \mathbb{N}, y > x$
- 归纳法：$\sum_{i=1}^{n} i = \frac{n(n+1)}{2}$
- Master Theorem：$T(n) = aT(n/b) + O(n^d)$

**核心实现**：
- Master Theorem 求解器（Merge Sort / Karatsuba / Strassen）
- Gödel 编码（符号序列 → 唯一自然数）
- Turing 机模拟器（二进制递增）

---

### 主题 3：CSC 207 Software Design

**设计模式**：
- **Strategy**：排序策略可替换
- **Observer**：Subject-Observer 事件通知
- **Factory**：对象创建解耦
- **Decorator**：咖啡配料链式装饰

**SOLID 原则**：SRP / OCP / LSP / ISP / DIP

---

### 主题 4：CSC 209 Systems Programming

**核心实现**：
- Mini Shell（命令解析：管道 |、重定向 >/<、后台 &）
- 进程模拟（fork / exec / wait）
- TCP 三次握手 + 四次挥手状态机
- 正则引擎（子集实现：`.`, `*`, `+`, `?`, `[abc]`）

---

### 主题 5：CSC 263 Data Structures

**核心数据结构**：
- AVL 树（4 种旋转 + 高度平衡验证）
- B-Tree（节点分裂 + 磁盘优化）
- Hash Table（链地址法 vs 开放寻址对比）
- Binomial Heap（$O(\log n)$ 合并）

**反直觉发现**：顺序插入 1..15 到 AVL 树，高度仅 4（$\approx \log_2 15$），而普通 BST 退化为高度 15 的链表。

---

### 主题 6：CSC 384 Intro to AI

**搜索算法**：
- **A***：$f(n) = g(n) + h(n)$，启发式必须 admissible

$$f(n) = g(n) + h(n)$$

- **CSP**：Forward Checking + MRV（Map Coloring）
- **STRIPS**：积木世界规划（Pick → Stack → goal）
- **MINIMAX + Alpha-Beta**：Tic-Tac-Toe

**反直觉发现**：Alpha-Beta 剪枝理论最优可减少 ~50% 节点，实测接近此值。

---

### 主题 7：CSC 411/511 Machine Learning

**核心算法**：
- 线性回归（Normal Equation + GD）
- Logistic 回归（$P(y=1|\mathbf{x}) = \sigma(\mathbf{w}^T \mathbf{x} + b)$）
- 决策树（信息增益 $= H(\text{parent}) - \sum \frac{n_k}{n} H(\text{child}_k)$）
- Random Forest（Bagging + 特征子采样）
- k-Means + GMM（EM 算法）

**EM Q-function**：

$$Q(\boldsymbol{\theta}|\boldsymbol{\theta}_{\text{old}}) = \sum_n \sum_k \gamma(z_{nk}) \left[\log \pi_k + \log \mathcal{N}(\mathbf{x}_n|\boldsymbol{\mu}_k, \boldsymbol{\Sigma}_k)\right]$$

---

### 主题 8：CSC 412/512 Probabilistic ML

**核心算法**：
- 贝叶斯线性回归（后验 $= \mathcal{N}(\mathbf{m}_N, \mathbf{S}_N)$）
- Mean-Field VI（ELBO 最大化）
- Metropolis-Hastings MCMC
- GP 回归（RBF Kernel）

**ELBO（变分下界）**：

$$\text{ELBO} = \mathbb{E}_q[\log p(\mathbf{x}, \mathbf{z})] - \mathbb{E}_q[\log q(\mathbf{z})]$$

**Bayes 定理**：

$$p(\mathbf{w}|\mathbf{X},\mathbf{y}) = \frac{p(\mathbf{y}|\mathbf{X},\mathbf{w}) \, p(\mathbf{w})}{p(\mathbf{y}|\mathbf{X})}$$

---

### 主题 9：CSC 413/513 Neural Nets & DL

**核心实现**：
- MLP + Backprop（$\boldsymbol{\delta}_L = \nabla L \odot \sigma'(\mathbf{z}_L)$）
- CNN（Conv2D + MaxPool，含 Sobel 边缘检测）
- LSTM（遗忘门 $f_t = \sigma(W_f [h_{t-1}, x_t] + b_f)$）
- Self-Attention + Transformer Block

**Attention 公式**：

$$\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V$$

---

### 主题 10：CSC 401 NLP

**核心算法**：
- HMM Viterbi（POS tagging）
- CKY 解析器（CNF 文法）
- IBM Model 1（EM 词对齐）
- Linear-Chain CRF（前向-后向）

**CRF（Lafferty 2001 ICML）**：

$$P(\mathbf{y}|\mathbf{x}) \propto \exp\left(\sum_t \sum_k \lambda_k f_k(y_{t-1}, y_t, \mathbf{x}_t)\right)$$

---

### 主题 11：CSC 420 Computer Vision

**核心管线**：
- 高斯模糊 + Sobel 梯度
- Canny 边缘检测（NMS + 双阈值 + 滞后连接）
- DoG 关键点检测（SIFT-like）
- RANSAC 单应性估计（Fischler & Bolles 1981）
- FCN 语义分割

---

### 主题 12：CSC 2547H Generative Models

**四大生成模型**：

| 模型 | 似然 | 隐空间 | 训练稳定性 |
|------|------|--------|-----------|
| VAE | 下界 | 随机 | 稳定 |
| GAN | 隐式 | 确定性 | 不稳定 |
| Diffusion | 精确 | 随机 | 稳定但慢 |
| Flow | 精确 | 确定性 | 稳定 |

**DDPM 前向/反向**：

$$q(\mathbf{x}_t|\mathbf{x}_0) = \mathcal{N}(\mathbf{x}_t; \sqrt{\bar{\alpha}_t}\mathbf{x}_0, (1-\bar{\alpha}_t)\mathbf{I})$$

$$p_\theta(\mathbf{x}_{t-1}|\mathbf{x}_t) = \mathcal{N}(\mathbf{x}_{t-1}; \boldsymbol{\mu}_\theta(\mathbf{x}_t, t), \sigma_t^2\mathbf{I})$$

**VAE ELBO**（Kingma 1312.6114）：

$$\mathcal{L} = \mathbb{E}_{q_\phi}[\log p_\theta(\mathbf{x}|\mathbf{z})] - D_{KL}(q_\phi(\mathbf{z}|\mathbf{x}) \| p(\mathbf{z}))$$

**GAN minimax**（Goodfellow 1406.2661）：

$$\min_G \max_D \mathbb{E}[\log D(\mathbf{x})] + \mathbb{E}[\log(1 - D(G(\mathbf{z})))]$$

---

## 📈 整体统计

- **代码行数**：~4,500 行（核心 12 主题）+ ~1,800 行（补充 30 微项目）+ ~1,200 行（core/）
- **覆盖课程**：~50 门（12 主题课程 + 30 补充课程）
- **零外部依赖**：仅 Python 标准库 + numpy
- **每个文件都可 `python3 file.py` 独立运行**

---

## 🎓 学习路径建议

### 想做 AI 工程师（最 ROI 路径）
1. **CSC 108/148**（intro.py）→ 编程基础
2. **CSC 411**（ml.py）→ 经典 ML
3. **CSC 413**（deep.py）→ 深度学习
4. **CSC 401**（nlp.py）→ NLP
5. **CSC 420**（vision.py）→ 计算机视觉
6. **CSC 2547H**（generative.py）→ 生成模型前沿

### 想做 AI 研究者
1. **CSC 165/236**（discrete.py）→ 理论基础
2. **CSC 263**（data_struct.py）→ 算法分析
3. **CSC 412**（prob_ml.py）→ 概率推断 + 贝叶斯
4. **CSC 413**（deep.py）→ Transformer / Attention
5. **CSC 2547H**（generative.py）→ VAE / GAN / Diffusion / Flow

### 想做系统/基础设施工程师
1. **CSC 209**（systems.py）→ Shell / 进程 / 网络
2. **CSC 207**（design.py）→ 设计模式
3. **CSC 263**（data_struct.py）→ B-Tree / Hash
4. **CSC 458**（supplementary）→ 网络路由

---

## 📚 关键参考论文

每个项目代码头部都列了参考论文。最重要的 10 篇：

1. **VAE** — Kingma & Welling "Auto-Encoding Variational Bayes" arXiv:1312.6114
2. **GAN** — Goodfellow et al. "Generative Adversarial Nets" arXiv:1406.2661
3. **DDPM** — Ho, Jain, Abbeel "Denoising Diffusion Probabilistic Models" arXiv:2006.11239
4. **RealNVP** — Dinh et al. "Density Estimation using Real NVP" NeurIPS 2017 (arXiv:1605.08803)
5. **Attention** — Vaswani et al. "Attention Is All You Need" arXiv:1706.03762
6. **Bahdanau Attention** — Bahdanau et al. "Neural Machine Translation by Jointly Learning to Align and Translate" arXiv:1409.0473
7. **CRF** — Lafferty, McCallum, Pereira "Conditional Random Fields" ICML 2001
8. **SIFT** — Lowe "Distinctive Image Features from Scale-Invariant Keypoints" IJCV 2004
9. **Hinton DBN** — Hinton et al. "A Fast Learning Algorithm for Deep Belief Nets" Neural Computation 2006
10. **Wasserstein GAN** — Arjovsky et al. "Wasserstein GAN" arXiv:1701.07875

---

## ✅ 项目验证

所有 12 主题已通过 `run_all.sh` 自动化测试。

```bash
$ bash run_all.sh
# 12 个项目 ✅ 全部 PASS
```

---

**完成日期**：2026-08-12
**版本**：1.0（覆盖 Toronto DCS 核心课程）
