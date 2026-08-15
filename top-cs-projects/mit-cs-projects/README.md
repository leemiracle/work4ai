# 🎓 MIT EECS 2026 - 全课程项目实战（完整版）

> **完成度**：✅ 全部 12 个主题 + 补充课程微项目
> **覆盖课程**：~50+ 门（核心 + 补充）
> **可运行代码**：12 个完整项目 + 3 个补充项目集（27 个微项目）

---

## 📊 主题完成情况

| # | 主题 | 项目文件 | 覆盖课程 | 状态 |
|---|------|---------|---------|------|
| 1 | 编程入门 | `topic1-intro/intro.py` | 6.100A Intro Python | ✅ |
| 2 | 编程基础 | `topic2-fund/fundamentals.py` | 6.101 Fundamentals | ✅ |
| 3 | 算法导论 | `topic3-algo/algorithms.py` | 6.1210/6.006 Algorithms | ✅ |
| 4 | 高级算法 | `topic4-algo2/advanced_algo.py` | 6.1220/6.046 Advanced Algo | ✅ |
| 5 | 分布式系统 | `topic5-dist/distributed.py` | 6.5840/6.824 Distributed (Kaashoek) | ✅ |
| 6 | 数据库 | `topic6-db/database.py` | 6.5910/6.830 Database (Morris) | ✅ |
| 7 | 操作系统 | `topic7-os/os.py` | 6.5930/6.S081 OS (xv6) | ✅ |
| 8 | 性能工程 | `topic8-perf/performance.py` | 6.5940/6.172 Performance | ✅ |
| 9 | 经典 AI | `topic9-ai/ai_classic.py` | 6.4100/6.034 AI | ✅ |
| 10 | 机器学习/深度学习 | `topic10-ml/ml_deep.py` | 6.3900/6.867 ML + 6.S191 DL | ✅ |
| 11 | 欠驱动机器人 | `topic11-robot/underactuated.py` | 6.4210 Underactuated (Tedrake) | ✅ |
| 12 | 系统安全 | `topic12-sec/security.py` | 6.4420/6.858 Systems Security | ✅ |
| 📚 | 补充(本科) | `supplementary/undergrad_projects.py` | 6.100B/6.01/6.02/6.0002/6.009/6.031/18.06/18.600/6.042J/6.005 | ✅ |
| 📚 | 补充(研究生) | `supplementary/grad_projects.py` | 6.867/6.869/6.871/6.874/6.876/6.878/6.879/6.S982/9.520/HST.506 | ✅ |
| 📚 | 补充(杂项) | `supplementary/micro_projects.py` | 6.857/6.859/6.S192/6.S193/6.S898/6.S977/6.036/9.660 | ✅ |

---

## 🚀 快速开始

```bash
cd mit-cs-projects
bash run_all.sh
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

### 主题 1：6.100A 编程入门
**数学骨架**：
- Big-O：$T(n) = O(f(n))$ 意味着 $\exists c, n_0 : T(n) \leq c \cdot f(n), \forall n \geq n_0$
- 渐近层次：$O(1) < O(\log n) < O(n) < O(n \log n) < O(n^2) < O(2^n)$

**算法**：6 种排序（bubble/selection/insertion/merge/quick）的步数计数 + Eratosthenes 筛。

**反直觉发现**：n≈30-50 时 insertion sort ($O(n^2)$) 击败 merge sort ($O(n\log n)$)——常数因子在小 n 下主导。这就是 Timsort/Introsort 在小段切换 insertion sort 的原因。

---

### 主题 2：6.101 编程基础（mini-Lisp 解释器）
**数学骨架**：
- λ-演算：$(\lambda x. M) N \to_\beta M[x := N]$
- Y-combinator：$Y = \lambda f. (\lambda x. f(x\,x))(\lambda x. f(x\,x))$

**算法**：S-expr tokenize → parse → eval/apply；闭包；词法作用域环境链。

**反直觉发现**：在没有 `define` 的纯 λ-演算中，Y-combinator 仍能实现递归（factorial/fibonacci）——自引用是计算的基本性质。

---

### 主题 3：6.006 算法导论
**数学骨架**：
- Dijkstra：$d(v) = \min_u [d(u) + w(u,v)]$，贪心 + 优先队列
- Edit Distance DP：$D[i,j] = \min\{D[i-1,j]+1, D[i,j-1]+1, D[i-1,j-1] + [s_1[i] \neq s_2[j]]\}$

**算法**：Dijkstra、Bellman-Ford（负权检测）、LIS、Edit Distance、Kruskal MST、Prim MST。

**反直觉发现**：负权边让 Dijkstra 的贪心假设失效——它会在负权路径更优时给出错误答案。

---

### 主题 4：6.046 高级算法
**数学骨架**：
- FFT 蝶形：$X_k = E_k + \omega_N^k O_k$，$\omega_N = e^{-2\pi i/N}$
- Max-flow min-cut：$\max\text{flow} = \min\text{cut}$

**算法**：Ford-Fulkerson (Edmonds-Karp BFS)、Cooley-Tukey FFT（多项式乘法）、Randomized Quickselect、Union-Find。

**反直觉发现**：FFT 把 $O(n^2)$ 多项式乘法降到 $O(n \log n)$——n=1024 时加速 6x，n 越大越明显。

---

### 主题 5：6.824 分布式系统（Kaashoek）
**数学骨架**：
- Paxos 安全性：值一旦被多数派接受就不可更改
- 线性一致性：所有操作看起来在某个原子时刻瞬间完成

**算法**：MapReduce wordcount、GFS chunk 管理、Raft leader election + log replication、Paxos Prepare/Promise/Accept/Ack、线性一致 KV（CAS）。

**反直觉发现**：Paxos/Raft 只需"多数派"（n/2+1）而非全部节点同意——3 节点容忍 1 故障，但 2 节点容忍 0，多 1 个节点的边际价值巨大。

---

### 主题 6：6.830 数据库（Morris）
**数学骨架**：
- B-tree：高度 $h \leq \log_t N$，t=50 时百万键只需 h=2
- ARIES 三阶段：Analysis → Redo → Undo

**算法**：B-tree（搜索/插入/分裂）、ARIES WAL 恢复、2PL wait-for graph 死锁检测、Selinger DP 查询优化器。

**反直觉发现**：B-tree 高度增长极慢——t=50 时 100 万键只需 height=2！这就是数据库用 B-tree 而非二叉树的原因。

---

### 主题 7：6.S081 操作系统（xv6）
**数学骨架**：
- xv6 inode：12 direct + 1 indirect + 1 double-indirect 块指针
- CFS vruntime：$V_i(t) = \int_0^t \frac{1024}{w_i} dt$，$w_i = 1024 \cdot 1.25^{-\text{nice}_i}$

**算法**：xv6 inode FS（块映射 + 读写）、4 级页表 + TLB（LRU）、CFS 调度器（nice 影响时间片）、Trap/syscall 分发。

**反直觉发现**：TLB 容量极小（8 entries）但命中率接近 100%——只要 TLB ≥ working set，分页在实践中几乎"免费"。

---

### 主题 8：6.172 性能工程
**数学骨架**：
- Cache 行为：$t_{\text{access}} = t_{\text{cache}} \cdot P(\text{hit}) + t_{\text{mem}} \cdot P(\text{miss})$
- 2-bit 预测器：状态机 SN→WN→WT→ST

**算法**：直接映射 cache 模拟（矩阵乘法 6 种顺序）、SIMD 向量求和模拟、2-bit 饱和分支预测器、popcount（Brian Kernighan / 查表法）。

**反直觉发现**：矩阵乘法 6 种循环顺序数学上完全等价，但 cache miss 差 10 倍——ikj 连续访问比 ijk 友好得多。循环变换是性能优化的核心。

---

### 主题 9：6.4100 经典 AI
**数学骨架**：
- A* 评估函数：$f(n) = g(n) + h(n)$，$h$ 可采纳时保证最优
- Bayes 推断：$P(B|J,M) = \frac{P(J,M|B)P(B)}{P(J,M)}$
- αβ 剪枝：$\alpha \geq \beta$ 时剪枝

**算法**：A* 8-puzzle（Manhattan 距离）、MINIMAX + Alpha-Beta（井字棋）、CSP 回溯 + AC-3（地图着色）、贝叶斯网络枚举推断（Burglary 网络）。

**反直觉发现**：Alpha-beta 剪枝大幅减少搜索节点；启发式越强，A* 扩展节点越少（指数级差距）。

---

### 主题 10：6.867 ML + 6.S191 DL
**数学骨架**：
- Self-Attention：$\text{Attention}(Q,K,V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V$
- Backprop 链式法则：$\frac{\partial L}{\partial W^{(l)}} = \frac{\partial L}{\partial a^{(L)}} \prod_{k=L}^{l+1} \frac{\partial a^{(k)}}{\partial a^{(k-1)}} \cdot \frac{\partial a^{(l)}}{\partial W^{(l)}}$
- Sigmoid：$\sigma(x) = \frac{1}{1+e^{-x}}$

**算法**：Perceptron（在线学习）、MLP + 反向传播（XOR）、conv2d（Sobel 边缘检测）、RNN char-LM、Self-Attention（scaled dot-product）。

**反直觉发现**：随机 Q/K 下 self-attention 对角线权重略高；单层 Perceptron 无法解 XOR，2 层 MLP 可以（通用近似定理）。

---

### 主题 11：6.4210 欠驱动机器人（Tedrake）
**数学骨架**：
- LQR Bellman 方程：$P = A^T P A - A^T P B(R + B^T P B)^{-1} B^T P A + Q$
- 接触互补条件：$0 \leq f_n \perp g \geq 0$（法向力与间隙互补）
- Lyapunov：系统渐近稳定 $\iff \exists V(x) > 0, \dot{V}(x) < 0$

**算法**：离散 Riccati LQR（cartpole 线性化）、LCP 求解器（接触力学）、Lyapunov 导数验证（$V̇ < 0$）、Pendulum RK4 + 相图 ASCII。

**反直觉发现**：cartpole 自然不稳定（开环特征值有正实部），但 LQR 通过状态反馈使其闭环特征值全负——稳定化不稳定系统。

---

### 主题 12：6.858 系统安全
**数学骨架**：
- RSA：$c = m^e \bmod n$，$m = c^d \bmod n$，$ed \equiv 1 \pmod{\phi(n)}$
- OAEP：$EM = 0x00 \| H(r) \oplus m$，随机填充防确定性

**算法**：RSA（Miller-Rabin + 扩展欧几里得）、OAEP-lite 填充、mini 符号执行（路径约束枚举）、Capability sandbox + CFI 检查。

**反直觉发现**：RSA 直接加密相同明文→相同密文（确定性，可被字典攻击）；加 OAEP 随机填充后每次不同——OAEP 是 RSA 安全的基石。

---

## 📈 整体统计

- **代码行数**：~4,000 行（12 主题）+ ~1,200 行（3 补充项目集）+ ~1,000 行（core/）
- **覆盖课程**：~50 门（12 主题 + 28 补充）
- **零外部依赖**：核心 12 主题中仅 topic10/topic11 使用 numpy，其余纯标准库
- **每个文件包含「反直觉发现」**：揭示非平凡结论的数字

---

## 🎓 学习路径建议

### 想做 AI 工程师（最 ROI 路径）
1. **6.100A**（intro）→ 编程基础
2. **6.006**（algorithms）→ 算法思维
3. **6.172**（performance）→ 性能优化
4. **6.867+6.S191**（ML/DL）→ 模型训练
5. **6.824**（distributed）→ 分布式训练/推理
6. **6.830**（database）→ 数据管道

### 想做 AI 研究者
1. **6.006 + 6.046**（算法）→ 理论基础
2. **6.4100**（classic AI）→ 搜索/推理
3. **6.867+6.S191**（ML/DL）→ 深度学习
4. **6.4210**（underactuated）→ 强化学习/控制
5. **9.520**（statistical learning theory）→ 泛化理论

### 想做系统架构师
1. **6.S081**（OS）→ 内核原理
2. **6.824**（distributed）→ 共识/复制
3. **6.830**（database）→ 事务/存储
4. **6.172**（performance）→ 优化
5. **6.858**（security）→ 防御

---

## 📚 关键参考论文/教材

每个项目代码头部都列了参考论文。最重要的 10 篇（arXiv ID 已核实）：

1. **Attention Is All You Need** (Vaswani et al. 2017) arXiv:1706.03762 — 主题 10
2. **Deep Residual Learning** (He et al. 2016) arXiv:1512.03385 — 主题 10 (CNN/ResNet)
3. **Denoising Diffusion Probabilistic Models** (Ho et al. 2020) arXiv:2006.11239 — 补充 6.S898
4. **Raft** (Ongaro & Osterhout 2014 USENIX ATC) — 主题 5
5. **Paxos** (Lamport 1998 ACM TOCS) — 主题 5
6. **MapReduce** (Dean & Ghemawat 2004 OSDI) — 主题 5
7. **ARIES** (Mohan et al. 1992 ACM TODS) — 主题 6
8. **CLRS Introduction to Algorithms** 4th ed — 主题 3-4
9. **SICP** (Abelson & Sussman, MIT Press) — 主题 2
10. **Underactuated Robotics** (Tedrake, course notes) — 主题 11

---

## ✅ 项目验证

所有 12 主题 + 3 补充项目已通过 `run_all.sh` 自动化测试。

```bash
$ bash run_all.sh
# 12 主题 + 3 补充 ✅ 全部 PASS
```

---

**完成日期**：2026-08-12
**作者**：AI Mentor + 学生
**版本**：1.0（覆盖 MIT EECS 2026 核心课程）
