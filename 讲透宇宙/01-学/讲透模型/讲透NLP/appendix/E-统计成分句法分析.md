# 附录 E — 统计成分句法分析（Statistical Constituency Parsing）

> 对应 SLP3 Appendix E。一句话可以有多种合法的句法树——概率上下文无关文法（PCFG）给每棵树打分，选概率最高的。但朴素的 PCFG 有两个致命缺陷：**不管词**和**不管上下文**。1990s 末，Collins 和 Charniak 用词法化（lexicalization）解决了这个问题，将 WSJ parsing F1 从 ~73% 推到 ~88%。本章讲透这整个演进。
>
> 配套实验：`experiments/E_cfg_rerank.py`

---

## 1. 直觉：歧义为什么需要概率？

经典歧义：*"I saw the man with a telescope."*

```
解读 A（PP 挂 VP）:           解读 B（PP 挂 NP）:
  S                            S
 ├─NP                          ├─NP
 │ └─I                         │ └─I
 └─VP                          └─VP
    ├─V saw                       ├─V saw
    ├─NP                          └─NP
    │ ├─Det the                     ├─Det the
    │ ├─N man                       ├─N man
    │ └─NP  ← 没有 PP               └─PP with a telescope
    └─PP with a telescope                ↑ "拿着望远镜的人"
       ↑ "用望远镜看"
```

两种解读**都语法合法**。人类靠常识判断："用望远镜看"比"拿着望远镜的人"更自然。但 CKY 算法只负责**找出**所有合法树，不负责**选**哪棵。

PCFG 的想法：**给每条文法规则一个概率，整棵树的概率 = 所有规则概率之积**，选概率最大的树。

> 🎯 **核心思想**：句法消歧 = 概率比较。不是"哪种解读语法对"（都对），而是"哪种解读更可能"。

---

## 2. 数学层

### 2.1 PCFG 定义

概率上下文无关文法（PCFG）= CFG + 每条规则的生成概率：

$$G = (N, \Sigma, R, S, q)$$

其中 $q(A \to \beta)$ 是规则 $A \to \beta$ 的概率，满足约束：

$$\sum_{\beta: A \to \beta \in R} q(A \to \beta) = 1 \quad \forall A \in N$$

即"从同一个非终结符出发的所有规则，概率之和 = 1"。

一棵解析树 $T$ 的概率：

$$\boxed{P(T) = \prod_{i=1}^{n} q(\text{rule}_i)}$$

一棵树用了 $n$ 条规则，每条规则的概率相乘——这就是"树的似然"。

### 2.2 概率 CKY 算法

概率 CKY 是普通 CKY 的概率版本。定义 **inside 概率**：

$$\pi(i, j, A) = P(A \overset{*}{\Rightarrow} w_i \cdots w_j)$$

即非终结符 $A$ 推导出子串 $w_i \cdots w_j$ 的**最高概率**。

**递推**（对每条 $A \to B\,C$ 规则，对每个分割点 $k$）：

$$\pi(i, j, A) = \max_{A \to BC,\; i \le k < j} q(A \to BC) \cdot \pi(i, k, B) \cdot \pi(k+1, j, C)$$

最终答案 $\pi(1, n, S)$ 就是最佳解析树的概率，通过回溯指针恢复树结构。

> **复杂度**：$O(|R| \cdot n^3)$，$|R|$ 是文法规则数，$n$ 是句子长度。

### 2.3 PCFG 的两个致命缺陷

#### 缺陷 1：缺乏结构偏好（structural independence）

考虑并列歧义：*"A or B and C"* 可以解读为 $[A \text{ or } [B \text{ and } C]]$ 或 $[[A \text{ or } B] \text{ and } C]$。

PCFG 中，规则 $S \to \text{NP conj NP}$ 和 $\text{NP} \to \text{NP conj NP}$ 的概率是**固定的**，不受左右并列项的影响。这导致 PCFG 有错误的**右结合偏好**（在英语中并列结构的左结合才更自然）。

#### 缺陷 2：缺乏词汇化（PP 附着问题）

回到 *"saw the man with a telescope"*。两种解读用到的规则是：

| 解读 A（PP 挂 VP） | 解读 B（PP 挂 NP） |
|---|---|
| VP → V NP PP | NP → NP PP |
| VP → V NP | NP → NP |

PCFG 给 VP→V NP PP 和 NP→NP PP 各一个**固定概率**，不管动词是 `saw`（看→用工具）还是 `eat`（吃→用叉子）。

这就是问题所在：**PP 到底挂 VP 还是 NP，取决于具体动词和名词**。

| 动词 | PP 挂 VP 比例 | 典型 |
|------|-------------|------|
| `saw`（看） | 90%+ | 用望远镜/用刀/用心 |
| `eat`（吃） | ~80% | 用叉子/用手 |
| `visit`（访问） | ~30% | with 的 PP 更多挂 NP |

PCFG 看不到这些差异。**"with a fork" 挂在 "eat"（VP）上 vs 挂在 "pizza"（NP）上，PCFG 给出完全相同的概率**——因为文法规则不包含词信息。

> 🧩 **反直觉发现**：朴素的 Treebank PCFG 在 WSJ 上只有 ~73% F1。问题不在算法（CKY 是精确的），而在模型——**句法消歧的本质是语义/词法问题，PCFG 把它当成了纯结构问题**。

### 2.4 改进路线一：拆分非终结符

**Klein & Manning (2003)**：手工给非终结符加"父节点"注释。把 NP 拆成 NP^S、NP^VP、NP^NP（分别表示 NP 出现在 S 下、VP 下、NP 下）。这编码了**结构上下文**。

**Petrov et al. (2006)——Berkeley Parser**：用**自动 split-merge** 让机器自己学怎么拆：
- **Split**：把每个非终结符一分为二（NP → NP_1, NP_2），赋予不同概率。
- **Merge**：用 EM 判断哪些拆分没用（两个子符号行为相似），合并回去。
- 迭代多轮，自动发现 NP 主语 vs NP 宾语、VP 从句 vs VP 非从句等隐含区分。

Berkeley Parser 把 WSJ F1 从 ~73% 推到 **~90%**，全程不需要语言学家的手工标注。

### 2.5 改进路线二：词法化 PCFG（Collins / Charniak）

**核心思想**：每个非终结符都标注它的**词汇中心词**（head word）和**中心词词性**（head tag）。

```
VP → VBD NP PP       原始规则（无词法信息）
VP(dumped,VBD) →     词法化后：
  VBD(dumped,VBD)      中心词是 dumped（动词过去式）
  NP(sacks,NNS)        中心词是 sacks（名词复数）
  PP(into,P)           中心词是 into（介词）
```

但全词法化的规则太稀疏（"VP 以 dumped 为中心，带 sacks 的 NP 和 into 的 PP"几乎见不到第二次），直接估计 $P(\text{RHS}|\text{LHS})$ 会全部是 0。

**Collins Model 1 的生成故事**（巧妙地分解稀疏性）：

给定左部 $P(h)$，规则 $P(h) \to L_n \cdots L_1 \, H \, R_1 \cdots R_m$ 的概率被分解为三个独立步骤：

$$P(\text{rule}) = \underbrace{P_H(H \mid P, h)}_{\text{生成中心子节点}} \times \prod_{i=1}^{n} \underbrace{P_L(L_i \mid P, h, H)}_{\text{左修饰子节点}} \times \prod_{j=1}^{m} \underbrace{P_R(R_j \mid P, h, H)}_{\text{右修饰子节点}}$$

1. **先生成中心子节点** $H$（概率 $P_H$）。
2. **从中心向左逐个生成修饰语**，直到生成 STOP（概率 $P_L$）。
3. **从中心向右逐个生成修饰语**，直到生成 STOP（概率 $P_R$）。

每个条件概率只依赖 $(P, h, H)$——父节点类别 + 中心词 + 中心子节点类别——而不是所有右部符号的联合。这个独立性假设大大减少了参数数量。

**Charniak (1997)** 用类似但不同的分解方式。两者都在 WSJ 上达到 **~88%** precision/recall，比朴素 PCFG 提升约 **15 个百分点**。

### 2.6 改进路线三：判别式重排序（discriminative re-ranking）

生成式模型（PCFG、Collins parser）直接建模 $P(\text{tree}, \text{sentence})$，然后取 $\arg\max$。但**排序只需要 $P(\text{tree} \mid \text{sentence})$ 的相对大小，不需要正确的概率分布**。

**思路**（Collins 2000; Charniak & Johnson 2005）：
1. 用 PCFG parser 生成 **top-k** 候选树（k=50 左右）。
2. 用**判别式模型**（最大熵/感知器/后来的神经网络）对 k 棵树重新排序。

判别式模型可以使用生成式模型**无法自然融入**的特征：任意跨词特征、句子级特征、外部知识。这个 two-stage 思路把 F1 进一步推到 **~90%+**。

> **时代意义**：reranking 是 NLP 中最早成功应用结构化预测和感知器/最大熵的范例之一。到 2010s，这个"先生成 top-k 再判别排序"的范式被 CRF 和后来的 neural parser 继承。

### 2.7 成分分析 vs 依存分析：一张全景图

| 方法 | 代表 | WSJ F1 | 核心创新 | 时代 |
|------|------|--------|---------|------|
| Treebank PCFG | — | ~73% | 直接从树库抽规则 | 1990s |
| Parent annotation | Klein & Manning 2003 | ~86% | 手工拆分非终结符 | 2000s |
| Lexicalized PCFG | Collins 1999, Charniak 1997 | ~88% | 中心词分解 | 1990s 末 |
| Berkeley Parser | Petrov et al. 2006 | ~90% | 自动 split-merge | 2000s |
| Discriminative reranking | Charniak & Johnson 2005 | ~92% | 判别重排 top-k | 2000s |
| Neural (constituency) | Kitaev & Klein 2018 | ~95% | 自注意力编码 | 2010s |

---

## 3. 代码层：玩具级词法化重排序

```bash
cd 讲透NLP && python3 experiments/E_cfg_rerank.py
```

实验用极简 PCFG + CKY 对 PP 歧义句生成 top-k 候选树，然后用一个简单的**词法化特征**（"动词 + with → VP 附着"的偏好概率）重排序。

> 🧩 **反直觉发现**：PCFG 对 *"eat pizza with a fork"* 和 *"eat pizza with anchovies"* 给出**完全相同**的树概率（因为规则概率不含词）。加上一个仅依赖中心词的简单特征，立刻区分了"用叉子吃"（VP 附着）和"带凤尾鱼的披萨"（NP 附着）。**词法化的提升，本质上是在做语义消歧**。

---

## 4. 批判性视角

- **PCFG 独立性假设太强**：PCFG 假设"同一棵树里不同位置使用同一规则的事件相互独立"。但语言不是这样——一个句子用了 $S \to \text{NP VP}$ 之后，再次用它的概率取决于上下文。这让 PCFG 系统性地偏好"少规则、规则复用多"的树，即使这不符合语言学事实。

- **词法化的代价**：Collins Model 1 虽然效果出色，但参数量剧增（每个中心词都有一组条件概率），训练数据需求大。而**真正的瓶颈是 PP 附着**这种局部歧义——全局树概率的小差异被远处的规则概率淹没。这就是为什么 reranking 有效：它把判别集中在最难的局部决策上。

- **成分分析 vs 依存分析**：成分分析（constituency）强调层次嵌套（NP、VP），依存分析（dependency）强调词与词的直接关系。Collins Model 1 本质上就是一个**伪装成成分分析的依存模型**（"生成中心词的修饰语"就是依存关系）。这解释了为什么 2010s 后依存分析（如 Stanford Parser、spaCy）逐渐主导实践——依存表示更直接、更易用于下游任务。

- **神经时代的遗产**：Kitaev & Klein (2018) 用 Transformer encoder + 成分 CKY 达到 ~95% F1，几乎不需要人工设计。但**CKY 的 O(n³) 复杂度**仍然是瓶颈（长句慢），这也是为什么实践中 spaCy 的**移进归约**（transition-based）依存解析器更快——O(n) 线性时间，虽然准确率略低。

- **"成分"概念本身在争论中**：构式语法（Construction Grammar）、依存语法等理论质疑"成分"是否是真实的语言单元。统计成分分析器在工程上有效，但这是**工程成功**而非**语言学验证**。

---

## 📌 下一步

统计成分分析展示了概率思想如何应用于句法结构。理解 PCFG 的基础是 **CFG 本身**——一个形式语言理论概念。

→ [F-上下文无关文法.md](F-上下文无关文法.md)：CFG 在 Chomsky 层级中的位置、CNF 转换的算法细节、以及 Pumping Lemma 如何证明某些语言"超越了 CFG 的能力"。

---

## ✍️ 练习

1. ⭐ PCFG 的两个致命缺陷分别是什么？用 PP 附着问题解释"缺乏词汇化"为什么有害。

2. Collins Model 1 把规则 $P(h) \to L_n \cdots H \cdots R_m$ 的概率分解为 $P_H \times \prod P_L \times \prod P_R$。为什么这个分解比直接估计 $P(\text{RHS}|\text{LHS})$ 更可行？涉及什么统计学概念？（提示：稀疏性。）

3. 跑 `E_cfg_rerank.py`，找到 PCFG 排第一但词法化重排后排第二的树。解释 reranker 用了什么信号来翻转排名。

4. ★ Berkeley Parser 的 split-merge 与 Klein & Manning 的手工 parent annotation 解决的是同一个问题（非终结符太粗）。比较两者：自动方法有什么优势？有什么风险？

5. 思考：如果把 CKY 的复杂度 $O(|R| \cdot n^3)$ 中的 $|R|$ 替换为 Collins Model 1 的规则数（远大于普通 PCFG），解析还能在合理时间内完成吗？（提示：考虑 Collins 如何用**剪枝**将候选规则数从指数级降到可控。）
