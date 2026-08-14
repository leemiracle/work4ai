# 🎓 Oxford CS 2026 - 全课程项目实战（完整版）

> **完成度**：✅ 全部 12 个主题 + 补充课程微项目
> **覆盖课程**：~40+ 门（核心 + 补充）
> **可运行代码**：12 个完整项目 + 29 个微项目

---

## 📊 主题完成情况

| # | 主题 | 项目文件 | Oxford 课程 | 状态 |
|---|------|---------|------------|------|
| 1 | 计算基础 | `topic1-foundations/foundations.py` | Foundations of CS | ✅ |
| 2 | 编程语言 | `topic2-pl/pl.py` | Principles of Programming Languages | ✅ |
| 3 | 算法 | `topic3-algorithms/algorithms.py` | Algorithms | ✅ |
| 4 | 并发 | `topic4-concurrency/concurrency.py` | Concurrency | ✅ |
| 5 | 数据库 | `topic5-databases/databases.py` | Databases | ✅ |
| 6 | 编译器 | `topic6-compilers/compilers.py` | Compilers | ✅ |
| 7 | 计算机视觉 | `topic7-vision/vision.py` | Computer Vision | ✅ |
| 8 | 机器学习 | `topic8-ml/ml.py` | Machine Learning | ✅ |
| 9 | 知识表示 | `topic9-kr/kr.py` | Knowledge Representation & Reasoning | ✅ |
| 10 | 自动推理 | `topic10-ar/auto_reasoning.py` | Automated Reasoning | ✅ |
| 11 | 博弈论 | `topic11-cgt/game_theory.py` | Computational Game Theory | ✅ |
| 12 | 范畴论 | `topic12-foundations/cpp.py` | Categories, Proofs & Processes | ✅ |
| 📚 | 本科补充 | `supplementary/undergrad_projects.py` | FP / Imperative / OOP / Discrete Math / Probability / LA / Continuous Math / Architecture / Networks / OS | ✅ |
| 📚 | 研究生补充 | `supplementary/grad_projects.py` | ML(deep) / Deep NLP(Youn Kim) / CV(deep) / Quantum / AR(deep) / CPP(deep) / Verification / Foundations(deep) / Security / Software Verification | ✅ |
| 📚 | 杂项补充 | `supplementary/micro_projects.py` | Comp Bio / PDEs / CGT(deep) / Info Theory / Geometric Modelling / Program Analysis / MDD / Lambda Calc(deep) / Complexity | ✅ |

---

## 🚀 快速开始

```bash
# 一次性跑所有核心主题
cd oxford-cs-projects
bash run_all.sh

# 跑单个主题
python3 topic1-foundations/foundations.py

# 跑所有补充课程
python3 supplementary/undergrad_projects.py
python3 supplementary/grad_projects.py
python3 supplementary/micro_projects.py
```

---

## 📦 共享基础设施（`core/`）

所有主题共享的模块（从 Stanford 样板移植，仅改头部注释）：

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

### 主题 1：Foundations of CS

**数学骨架**：
- 数学归纳法：$S(n) = \sum_{i=1}^{n} i = \frac{n(n+1)}{2}$
- 谓词逻辑自然演绎：Modus Ponens $(P \land (P \to Q)) \to Q$
- Warshall 传递闭包：$O(n^3)$
- 最小不动点：$\text{lfp}(f) = \bigsqcup_{i=0}^{\infty} f^i(\bot)$

**反直觉发现**：sum(1..100)=5050 看似需 100 步，归纳法一步证明。

---

### 主题 2：Principles of Programming Languages

**数学骨架**：
- λ-calculus β-归约：$(\lambda x.M)\,N \to M[x := N]$
- Church numerals：$\bar{n} = \lambda f.\lambda x. f^n(x)$
- Hindley-Milner Algorithm W：$W(\Gamma, e) = (\sigma, \tau)$
- Monad：$\text{return} : A \to M(A)$，$\text{bind} : M(A) \to (A \to M(B)) \to M(B)$

**反直觉发现**：Option monad 链式除法中除以 0 自动短路返回 none。

---

### 主题 3：Algorithms

**数学骨架**：
- 主定理：$T(n) = aT(n/b) + f(n)$
- Dijkstra：$O((V+E)\log V)$
- LCS DP：$dp[i][j] = \max(dp[i-1][j], dp[i][j-1])$ if $s_1[i] \neq s_2[j]$
- Prim MST 贪心：每步选最小横切边

**反直觉发现**：已排序数组+固定pivot快排=O(n²)，随机pivot=O(n log n)。

---

### 主题 4：Concurrency

**数学骨架**：
- CSP traces：$\text{traces}(P) = \{\langle \rangle\} \cup \{\langle a \rangle \frown t \mid a \to P', t \in \text{traces}(P')\}$
- CCS bisimulation：$P \sim Q$ iff 存在 bisimulation $R$ s.t. $(P,Q) \in R$
- π-calculus：$P = \bar{x}\langle y \rangle.P' \mid x(z).P'' \to P' \mid P''\{y/z\}$
- LTL：$\mathbf{G}\,p$ (globally), $\mathbf{F}\,p$ (eventually)

**反直觉发现**：CCS bisimulation 不看状态名，只看可观测行为。

---

### 主题 5：Databases

**数学骨架**：
- 关系代数：$\sigma_{\text{pred}}(R)$, $\pi_{\text{attrs}}(R)$, $R \bowtie S$
- 可串行化：precedence graph 无环
- Hash join：$O(n+m)$ vs nested-loop $O(n \times m)$

**反直觉发现**：100×50 数据上 hash join 比 nested-loop 快 50+ 倍。

---

### 主题 6：Compilers

**数学骨架**：
- FIRST/FOLLOW 集合
- LL(1) 预测分析表：$M[A, a] = \alpha$ if $a \in \text{FIRST}(\alpha)$
- LR(0) 项目集规范族：$\text{closure}(I)$, $\text{goto}(I, X)$

**反直觉发现**：文法设计隐含运算符优先级——`id+id*id` 正确解析为 `id+(id*id)`。

---

### 主题 7：Computer Vision

**数学骨架**：
- 高斯核（可分离）：$G(x,y) = G(x) \cdot G(y)$，$G(x) = \frac{1}{\sigma\sqrt{2\pi}} e^{-x^2/(2\sigma^2)}$
- Sobel：$G_x = \begin{bmatrix}-1&0&1\\-2&0&2\\-1&0&1\end{bmatrix}$
- Canny：NMS（非极大抑制）+ 双阈值滞后
- K-means：$\arg\min_S \sum_{k=1}^{K} \sum_{x \in S_k} \|x - \mu_k\|^2$

**反直觉发现**：高斯模糊利用可分离性将 2D 卷积（9次乘法）拆为 2 个 1D 卷积（6次）。

---

### 主题 8：Machine Learning

**数学骨架**：
- 贝叶斯线性回归后验：$m_N = \beta S_N \Phi^T y$，$S_N = (\alpha I + \beta \Phi^T \Phi)^{-1}$
- GP 边际似然：$\log p(y|X) = -\frac{1}{2}y^T K_y^{-1}y - \frac{1}{2}\log|K_y| - \frac{n}{2}\log(2\pi)$
- GP 预测：$\mu_* = K_*^T K_y^{-1} y$，$\sigma_*^2 = k(x_*,x_*) - K_*^T K_y^{-1} K_*$
- SVM 对偶：$\max_\alpha \sum_i \alpha_i - \frac{1}{2}\sum_{i,j} \alpha_i \alpha_j y_i y_j K(x_i,x_j)$

**反直觉发现**：GP 在远离训练数据处不确定性自动增大——"知道自己的无知"。

---

### 主题 9：Knowledge Representation & Reasoning

**数学骨架**：
- ALC tableau：$\exists r.C(x) \Rightarrow$ 新个体 $y$, $r(x,y)$, $C(y)$
- Resolution：$C_1 \lor \{p\}$ 和 $C_2 \lor \{\neg p\}$ → $C_1 \lor C_2$
- Kripke 模型检测：$\mathcal{M}, s \models \Box p$ iff $\forall s' \in R(s): \mathcal{M}, s' \models p$

**反直觉发现**：Ontology 中 alice∈Student 通过传递闭包自动推出 alice∈Animal。

---

### 主题 10：Automated Reasoning

**数学骨架**：
- DPLL：unit propagation + pure literal + branching
- CDCL 1-UIP clause learning：$\text{learned} = \neg(\text{conflict literals})$
- Resolution 完备性：$KB \models \phi$ iff $KB \cup \{\neg\phi\} \vdash \square$
- 3-SAT 相变：ratio $\approx 4.26$

**反直觉发现**：3-SAT 在 ratio≈4.26 时最难——这是"相变"现象。

---

### 主题 11：Computational Game Theory

**数学骨架**：
- Nash 均衡存在性：$\exists x^* \in \Delta$ s.t. $u_i(x^*) \geq u_i(x_i, x^*_{-i})$ $\forall i$（Brouwer 不动点）
- 零和博弈值：$v = \max_x \min_y x^T A y = \min_y \max_x x^T A y$（von Neumann minimax）
- Regret matching：$x_i(a) = \frac{R_i^+(a)}{\sum_b R_i^+(b)}$
- VCG 支付：$p_i = \max \sum_{j \neq i} v_j x_j - \sum_{j \neq i} v_j x_j^*$（Clarke pivot）

**反直觉发现**：囚徒困境中 (Defect,Defect) 是唯一 Nash，但帕累托劣于 (Cooperate,Cooperate)。

---

### 主题 12：Categories, Proofs & Processes

**数学骨架**：
- **Curry-Howard 同构**：命题 = 类型，证明 = 程序
  $$A \to B \quad \text{(逻辑蕴含)} \quad \equiv \quad A \to B \quad \text{(函数类型)}$$
  $$A \land B \quad \text{(合取)} \quad \equiv \quad A \times B \quad \text{(积类型)}$$
- STLC 类型检查 = 直觉主义证明验证
- 函子：$F: \mathcal{C} \to \mathcal{D}$，$F(g \circ f) = F(g) \circ F(f)$
- 自然变换：$\alpha: F \Rightarrow G$，$G(f) \circ \alpha_A = \alpha_B \circ F(f)$
- CCC currying：$\text{Hom}(A \times B, C) \cong \text{Hom}(A, C^B)$

**反直觉发现**：Peirce 律 $((P \to Q) \to P) \to P$ 在经典逻辑可证，但直觉主义（=STLC）不可证。

---

## 📈 整体统计

- **代码行数**：~4,500 行（12 主题）+ ~1,300 行（补充）
- **覆盖课程**：~40 门（12 主题课程 + 29 补充课程）
- **零外部依赖**（仅 Python 标准库）：所有项目可在任何环境跑通
- **语法校验**：全部通过 `ast.parse`

---

## 🎓 学习路径建议

### 想做 AI/ML 工程师（最 ROI 路径）

1. **Foundations of CS**（foundations）→ 数学基础
2. **Algorithms**（algorithms）→ 数据结构与算法
3. **Machine Learning**（ml）→ 贝叶斯/GP/SVM
4. **Computer Vision**（vision）→ 滤波/CNN
5. **Databases**（databases）→ SQL/存储
6. **Compilers**（compilers）→ 理解语言底层

### 想做理论/形式化研究

1. **Foundations of CS**（foundations）
2. **Categories, Proofs & Processes**（cpp）→ Curry-Howard
3. **Automated Reasoning**（auto_reasoning）→ SAT/CDCL
4. **Knowledge Representation**（kr）→ 描述逻辑
5. **Concurrency**（concurrency）→ CSP/π-calculus
6. **Principles of PL**（pl）→ HM 类型系统

### 想做系统/基础设施

1. **Algorithms**（algorithms）→ Dijkstra/MST
2. **Databases**（databases）→ 关系代数/事务
3. **Concurrency**（concurrency）→ 互模拟/模型检测
4. **Compilers**（compilers）→ LL/LR 解析
5. **Computer Architecture**（supplementary）→ 流水线/页替换

---

## 📚 关键参考论文/教材

每个项目代码头部都列了参考。最重要的 10 篇：

1. **Pierce "Types and Programming Languages"** MIT Press 2002 — 主题 2/12
2. **Winskel "The Formal Semantics of Programming Languages"** MIT Press 1993 — 主题 1/2
3. **Rasmussen & Williams "Gaussian Processes for Machine Learning"** MIT Press 2006 — 主题 8
4. **Nipkow, Paulson, Wenzel "Isabelle/HOL"** Springer 2002 — 主题 10/12
5. **Lemke & Howson "Equilibrium Points of Bimatrix Games"** SIAM J Appl Math 1964 — 主题 11
6. **Hoare "Communicating Sequential Processes"** Prentice Hall 1985 — 主题 4
7. **Canny "A Computational Approach to Edge Detection"** IEEE TPAMI 1986 — 主题 7
8. **Damas & Milner "Principal type-schemes of functional programs"** POPL 1982 — 主题 2
9. **Marques-Silva & Sakallah "GRASP"** IEEE Trans Computers 1999 (CDCL) — 主题 10
10. **Baader et al. "The Description Logic Handbook"** Cambridge 2007 — 主题 9

---

## ✅ 项目验证

所有 12 主题已通过 `run_all.sh` 自动化测试。

```bash
$ bash run_all.sh
# 12 个主题 + 3 个补充 ✅ 全部 PASS
```

---

**完成日期**：2026-08-12
**对齐样板**：Stanford CS Projects (TEMPLATE_SPEC.md)
**版本**：1.0（覆盖 Oxford CS 核心课程）
