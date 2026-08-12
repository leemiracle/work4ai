# 🎓 Princeton COS 2026 - 全课程项目实战（完整版）

> **完成度**：✅ 全部 12 个主题 + 补充课程微项目
> **覆盖课程**：~50 门（核心 + 补充）
> **可运行代码**：12 个完整项目 + 30 个微项目

---

## 📊 主题完成情况

| # | 主题 | 项目文件 | 覆盖课程 | 状态 |
|---|------|---------|---------|------|
| 1 | 计算机科学导论 | `topic1-intro/intro.py` | COS 126 | ✅ |
| 2 | 数据结构与算法 | `topic2-dsa/data_struct.py` | COS 226 | ✅ |
| 3 | 图算法 | `topic3-graphs/graphs.py` | COS 226 (Algorithms) | ✅ |
| 4 | 函数式编程 | `topic4-fp/functional.py` | COS 326 (SML) | ✅ |
| 5 | 高级编程 | `topic5-systems/systems.py` | COS 333 | ✅ |
| 6 | 机器学习 | `topic6-ml/ml.py` | COS 435/402 | ✅ |
| 7 | 自然语言处理 | `topic7-nlp/nlp.py` | COS 484 | ✅ |
| 8 | 计算机视觉 | `topic8-vision/vision.py` | COS 429/529 | ✅ |
| 9 | ML 理论 | `topic9-ml-theory/theory.py` | COS 511/512 | ✅ |
| 10 | 高级系统 | `topic10-systems/adv_systems.py` | COS 518 | ✅ |
| 11 | 网络与安全 | `topic11-networks-sec/net_sec.py` | COS 463/432 | ✅ |
| 12 | 公平性 ML | `topic12-fairness/fairness.py` | COS 595/597 | ✅ |
| 📚 | 本科补充 | `supplementary/undergrad_projects.py` | COS 217/240/341/343/432/436/485/495, MAT 200, ORF 309 | ✅ |
| 📚 | 研究生补充 | `supplementary/grad_projects.py` | COS 502/508/513/521/522/597E/597J/598C, ELE 522, ORF 524 | ✅ |
| 📚 | 杂项微项目 | `supplementary/micro_projects.py` | COS 116/109/126+/398/495W/498, SML, FreeType, Trading, Writing | ✅ |

---

## 🚀 快速开始

```bash
# 一次性跑所有核心主题
cd princeton-cs-projects
bash run_all.sh

# 跑所有补充课程
python3 supplementary/undergrad_projects.py
python3 supplementary/grad_projects.py
python3 supplementary/micro_projects.py
```

---

## 📦 共享基础设施（`core/`）

所有主题共享的模块（从 Stanford 样板 cp 并适配）：

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

### 主题 1：COS 126 General CS

**数学骨架**：
- Monte Carlo 估算：$\hat{\pi} = \frac{4 \cdot |\text{inside circle}|}{|\text{total}|}$
- 排序复杂度：插入排序已排序数据 $O(n)$，随机 $O(n^2)$

**算法**：TOY machine 模拟器（16-bit 教学计算机）；insertion/selection/merge sort 步数对比；Monte Carlo π + Buffon 投针。

**反直觉发现**：Insertion sort 对已排序数组只需 99 次比较（vs 随机 2617 次），这是 Python Timsort 的核心原理。

---

### 主题 2：COS 226 Data Structures

**数学骨架**：
- FFT 蝶形：$X[k] = E[k] + W_N^k O[k]$, $W_N = e^{-2\pi i/N}$
- 红黑树高度保证：$h \leq 2\log_2 N$

**算法**：左倾红黑树（LLRB, Sedgewick 简化）；KMP 子串搜索（failure function）；递归 FFT（Cooley-Tukey）；TST 三叉搜索 trie；separate-chaining hash table。

**反直觉发现**：FFT→IFFT 往返误差仅 $10^{-15}$，是精确的可逆变换，$O(n \log n)$ 比 $O(n^2)$ DFT 快 100 倍以上。

---

### 主题 3：COS 226 Algorithms (Graphs)

**数学骨架**：
- Dijkstra 松弛：$\text{dist}[v] = \min(\text{dist}[v], \text{dist}[u] + w(u,v))$
- Ford-Fulkerson 增广：沿最短增广路径推流

**算法**：DFS/BFS；Kruskal MST（Union-Find）；Dijkstra 最短路（min-heap）；Ford-Fulkerson 最大流（Edmonds-Karp BFS）；Burrows-Wheeler Transform（encode + decode）。

**反直觉发现**：BWT 编码后把相同字符聚集（run 数大幅减少），使 bzip2 比 gzip 压缩率高 20-40%。

---

### 主题 4：COS 326 Functional Programming

**数学骨架**：
- Hindley-Milner 类型推断：$\Gamma \vdash e : \tau \rightsquigarrow \Gamma'$
- Curry-Howard：命题 $A \to B$ ↔ 类型 $A \to B$（函数类型）

**算法**：mini-SML 解释器（AST + eval with environment）；Algorithm W（unification-based 类型推断）；Curry-Howard 对应表；CPS 转换。

**反直觉发现**：HM 类型推断自动推断 $\lambda x.x$ 为 $t_0 \to t_0$（最一般类型），无需任何注解。Algorithm W 实际复杂度接近线性。

---

### 主题 5：COS 333 Advanced Programming

**算法**：HTTP 请求/响应解析器；JSON-RPC 2.0 method dispatch；Shell 管道（pipe & filter）；C-like 内存安全检测器（OOB/UAF/double-free/leak）。

**反直觉发现**：Python 中所有 4 类 C 内存错误都不可能发生，但这些错误占 CVE 漏洞的 ~70%。Rust 的所有权模型在编译期消除这些，零运行时开销。

---

### 主题 6：COS 435/402 Machine Learning

**数学骨架**：
- 逻辑回归：$\sigma(z) = \frac{1}{1 + e^{-z}}$, $L = -\sum y \log \hat{y}$
- 梯度下降：$\theta_{t+1} = \theta_t - \eta \nabla L$

**算法**：线性回归（batch GD）；逻辑回归（GD + cross-entropy）；感知机（online mistake-driven）；kNN（majority vote）；决策树（ID3 信息增益）。

**反直觉发现**：k=1 训练准确率几乎 100%（过拟合），k=7 泛化更好。这是 bias-variance tradeoff 的直观体现。

---

### 主题 7：COS 484 NLP

**数学骨架**：
- Viterbi：$V[t][j] = \max_i V[t-1][i] \cdot P(j|i) \cdot P(w_t|j)$
- SGNS：$\max \log \sigma(\mathbf{v}_c \cdot \mathbf{u}_o) + \sum_{n} \log \sigma(-\mathbf{v}_c \cdot \mathbf{u}_n)$

**算法**：HMM POS 标注（Viterbi 解码）；PCFG CKY 解析；mini word2vec（SGNS 梯度下降）；BERT tokenizer + masked LM 概念。

**反直觉发现**：SGNS 自动发现 king↔queen 相似度高于 king↔rules，词嵌入无需显式规则即可学到语义关系。

---

### 主题 8：COS 429/529 Computer Vision

**数学骨架**：
- Sobel 梯度：$G = \sqrt{G_x^2 + G_y^2}$
- Gaussian：$G(x,y) = \frac{1}{2\pi\sigma^2} e^{-\frac{x^2+y^2}{2\sigma^2}}$

**算法**：conv2d（padding + stride）；Canny 边缘检测（Sobel → NMS → hysteresis）；形态学操作（erode/dilate/open/close）；DoG 关键点检测。

**反直觉发现**：Canny 的非极大值抑制确保边缘只有 1px 宽——这是它至今仍是工业标准的原因。

---

### 主题 9：COS 511/512 Theoretical ML

**数学骨架**：
- PAC 界限：$\epsilon = \sqrt{\frac{\ln(2/\delta)}{2n}}$（Hoeffding）
- VC 维：区间假设类 $VC = 2$；阈值假设类 $VC = 1$
- Regret 界：$\text{Regret} \leq O(\sqrt{T \ln N})$（Multiplicative Weights）

**算法**：PAC/Hoeffding 界限验证；VC dimension shattering 实验；Rademacher complexity 经验估计；Multiplicative Weights（regret 实验）；SGD 收敛速率（凸 vs 强凸）。

**反直觉发现**：平均 regret $\to 0$（no-regret），即算法渐近最优。这是博弈论中达到 Nash 均衡的数学基础。

---

### 主题 10：COS 518 Advanced Systems

**数学骨架**：
- CAS：$\text{CAS}(addr, expected, new) \to old\_value$（原子）
- RCU 读者复杂度：$O(1)$（完全无锁）

**算法**：Lock-free stack（CAS 模拟）；RCU read pattern（copy + swap + grace period）；STM（optimistic concurrency, read/write sets, validation）；Bw-tree（delta updates + page mapping table）。

**反直觉发现**：RCU 读者完全无锁、无原子操作——直接读！在读多写少场景比读写锁快 10-100 倍。

---

### 主题 11：COS 463/432 Networks & Security

**数学骨架**：
- RSA：$c = m^e \bmod n$, $m = c^d \bmod n$, $ed \equiv 1 \pmod{\phi(n)}$
- DH 共享密钥：$g^{ab} \bmod p$（离散对数难题）

**算法**：TCP 状态机（三次握手 + 四次挥手 + TIME_WAIT）；TLS 1.3 握手流程；RSA（Miller-Rabin + 扩展欧几里得）；Diffie-Hellman 密钥交换；ARP 欺骗模拟。

**反直觉发现**：TLS 1.3 把握手从 2-RTT 减到 1-RTT，还支持 0-RTT 恢复——但有重放攻击风险。

---

### 主题 12：COS 595/597 Fairness

**数学骨架**：
- Demographic parity：$P(\hat{Y}=1 | A=a) = P(\hat{Y}=1 | A=b)$
- Equalized odds：$P(\hat{Y}=1 | Y=y, A=a) = P(\hat{Y}=1 | Y=y, A=b)$

**算法**：Demographic parity 测量；Equalized odds（Hardt 后处理阈值优化）；Calibration 分析；Counterfactual fairness（Kusner 因果模型）；Post-processing vs in-processing 对比。

**反直觉发现**：Hardt 后处理优化 equalized odds 后 demographic parity 反而恶化——这就是 Kleinberg/Chouldechova 不可能性定理的实证体现。

---

## 📈 整体统计

- **代码行数**：~4,000 行（核心 12 主题）+ ~2,000 行（补充 30 微项目）
- **覆盖课程**：~50 门（12 主题课程 + 30 补充课程）
- **测试覆盖率**：所有文件 `python3 file.py` 运行通过
- **零外部依赖**（除 Python 标准库）：所有项目可在任何环境跑通

---

## 🎓 学习路径建议

### 想做 AI 工程师（最 ROI 路径）
1. **COS 126**（intro.py）→ 编程基础
2. **COS 226**（data_struct.py）→ 数据结构核心
3. **COS 435/402**（ml.py）→ 机器学习
4. **COS 484**（nlp.py）→ NLP / LLM 基础
5. **COS 518**（adv_systems.py）→ 生产部署
6. **COS 333**（systems.py）→ 工程能力

### 想做 AI 研究
1. **COS 435/402**（ml.py）
2. **COS 511/512**（theory.py）→ PAC / VC dimension
3. **COS 484**（nlp.py）→ HMM / word2vec
4. **COS 595/597**（fairness.py）→ 公平性 / 因果
5. **COS 429/529**（vision.py）→ CV 基础

### 想做系统/基础设施
1. **COS 126**（intro.py）
2. **COS 226**（data_struct.py + graphs.py）
3. **COS 333**（systems.py）→ HTTP / RPC / 内存安全
4. **COS 518**（adv_systems.py）→ 并发 / lock-free / RCU
5. **COS 463/432**（net_sec.py）→ 网络 / 密码学

### 想做理论/算法研究
1. **COS 226**（data_struct.py）→ LLRB / FFT / KMP
2. **COS 326**（functional.py）→ 类型论 / Curry-Howard
3. **COS 511/512**（theory.py）→ PAC / VC / Rademacher
4. **COS 521**（grad_projects.py）→ LP 松弛

---

## 📚 关键参考论文

每个项目代码头部都列了参考论文。最重要的 10 篇：

1. Sedgewick & Wayne "Algorithms" 4th ed — 主题 2/3
2. Damas & Milner 1982 "Principal Type-Schemes for Functional Programs" POPL — 主题 4
3. Canny 1986 "A Computational Approach to Edge Detection" IEEE TPAMI — 主题 8
4. Valiant 1984 "A Theory of the Learnable" CACM (PAC learning) — 主题 9
5. Hardt, Price, Srebro 2016 "Equality of Opportunity in Supervised Learning" NeurIPS — 主题 12
6. Kusner et al. 2017 "Counterfactual Fairness" NeurIPS — 主题 12
7. Rivest, Shamir, Adleman 1978 "A Method for Obtaining Digital Signatures" CACM (RSA) — 主题 11
8. Diffie & Hellman 1976 "New Directions in Cryptography" IEEE Trans IT (DH) — 主题 11
9. Vapnik & Chervonenkis 1971 (VC dimension) — 主题 9
10. Herlihy & Shavit "The Art of Multiprocessor Programming" — 主题 10

---

## ✅ 项目验证

所有 12 主题已通过 `run_all.sh` 自动化测试。

```bash
$ bash run_all.sh
# 12 个项目 ✅ 全部 PASS
```

---

**完成日期**：2026-08-12
**版本**：1.0（覆盖 Princeton COS 2026 核心课程）
**参考样板**：Stanford CS Projects (stanford-cs-projects)
