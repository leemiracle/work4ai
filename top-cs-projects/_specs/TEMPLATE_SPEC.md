# 顶级名校 CS 全课程实战项目 — 共享模板规格

> 这是 **共享模板规格**。每个大学（CMU/MIT/Berkeley/Princeton/Cambridge/Oxford/ETH/Toronto）的项目都遵循本规格，差异仅在「课程主题清单」。Stanford 是参考样板。

---

## STEP 0 — 先读 Stanford 样板（强制）

在动手写任何文件前，必须读：

| 文件 | 用途 |
|------|------|
| `~/ai/work4ai/stanford-cs-projects/README.md` | 整体文档风格、章节结构、学习路径、论文清单 |
| `~/ai/work4ai/stanford-cs-projects/topic1-choice/choice_theory.py` | 单文件代码风格（280 行，含 docstring/数学/可视化/main demo） |
| `~/ai/work4ai/stanford-cs-projects/topic4-mlsys/kv_cache_sim.py` | 第二个代码样板（系统类，ASCII 可视化） |
| `~/ai/work4ai/stanford-cs-projects/topic2-agent-v2/dspy_framework.py` | 第三样板（含 mock LLM 调用风格） |
| `~/ai/work4ai/stanford-cs-projects/supplementary/all_micro_projects.py` | 微项目样板（一文件覆盖多门课） |
| `~/ai/work4ai/stanford-cs-projects/core/llm.py` + `core/rag.py` + `core/eval.py` | 共享基础设施样板 |

可以直接 `cp -r` 一些 core 文件再编辑头部注释，节省时间。

---

## STEP 1 — 目录结构（每个大学都一样）

```
<uni>-cs-projects/
├── core/                          # 共享基础设施
│   ├── __init__.py
│   ├── llm.py                     # litellm wrapper + Mock 兜底（离线可用）
│   ├── rag.py                     # chunking + embedding(mock) + retrieval
│   ├── tools.py                   # calculator/search/file_reader 工具
│   ├── react.py                   # ReAct 主循环
│   ├── eval.py                    # pass@k + 4-tuple eval framework
│   └── hybrid_search.py           # BM25 + Dense 混合检索（可选）
├── topic1-<name>/                 # 12 个主题目录
│   └── <name>.py
├── topic2-<name>/
│   └── <name>.py
├── ... (topic3 到 topic12)
├── supplementary/                 # 补充课程微项目
│   ├── undergrad_projects.py      # 本科其余课程（覆盖 5-10 门）
│   ├── grad_projects.py           # 研究生其余课程（覆盖 5-10 门）
│   └── micro_projects.py          # 杂项微项目（覆盖 5-10 门）
├── docs/                          # 可选补充文档
├── README.md                      # 主文档
├── COMPLETION_REPORT.md           # 完成报告
├── run_all.sh                     # bash 一键运行
└── requirements.txt               # 空文件或仅 numpy
```

---

## STEP 2 — 主题 Python 文件规格（每个大学 12 个）

每个 `topicN-<name>/<name>.py` 必须满足：

### 2.1 文件规模
- **200-400 行**（不低于 200，不超过 450）
- 零依赖或近零依赖（**仅** Python 标准库 + 可选 `numpy`）
- 禁用：`torch`/`tensorflow`/`matplotlib`/`pandas`/`sklearn`/`scipy`/任何外部 API

### 2.2 文件头部 docstring（强制）
```python
"""
<课程编号> <课程全名>（<大学>）
================================================
覆盖主题：
- <主题 1，对应 lecture X>
- <主题 2>
- <主题 3>

核心论文/教材（arXiv ID 已核实）：
- <作者 年> "<标题>" arXiv:<真实 ID，不许编造>
- <教材章节>

本文件实现：
- <算法 1>
- <算法 2>
- <算法 3>

运行：
    python <name>.py
"""
```

**铁律**：arXiv ID 必须真实。常用真实 ID 速查：
- Attention Is All You Need: 1706.03762
- BERT: 1810.04805
- GPT-3: 2005.14165
- ResNet: 1512.03385
- Adam: 1412.6980
- dropout: 1207.0580
- batch norm: 1502.03167
- VAE Kingma: 1312.6114
- GAN Goodfellow: 1406.2661
- DDPM Ho: 2006.11239
- DQN Mnih: 1312.5602
- PPO Schulman: 1707.06347
- A3C: 1602.01783
- SAC Haarnoja: 1801.01290
- WORD2VEC Mikolov: 1301.3781
- GLOVE Pennington: 1407.0111 (不进 arXiv，用 EMNLP 2014)
- NEURAL TPP Bengio 2003: 1301.3781 (用论文标题加 "Bengio 2003")
- seq2seq Sutskever: 1409.3215
- variational attention Bahdanau: 1409.0473
- Transformer Vaswani: 见上
- Paxos Lamport: 用 "Lamport 1998 ACM TOCS Part-Time Parliament"
- Raft Ongaro: 用 "Ongaro & Osterhout 2014 USENIX"
- MapReduce Dean: "Dean & Ghemawat 2004 OSDI"
- GFS Ghemawat: "Ghemawat et al 2003 SOSP"
- B-tree: "Bayer & McCreight 1972"
- B+ tree / ARIES: "Mohan 1992 ARIES SIGMOD"
- backpropagation: "Rumelhart Hinton Williams 1986 Nature"
- variational ELBO: 见 VAE
- KMeans MacQueen 1967
- SVM Cortes Vapnik 1995
- AdaBoost Freund Schapire 1997
- Random Forest Breiman 2001
- EM Dempster Laird Rubin 1977 J Royal Stat Soc B
- HMM Rabiner 1989 IEEE Proc
- Kalman filter: "Kalman 1960 J Basic Engineering"
- Baum-Welch: 同 Rabiner 1989
- PCFG: "Charniak 1997" 或 "Manning Schütze textbook chapter 11"
- IBM Model 1: "Brown et al 1993 Computational Linguistics"
- CYK: "Cocke-Kasami-Younger 见 Hopcroft Ullman 1979"
- Dijkstra 1959 Numerische Mathematik
- A* Hart Nilsson Raphael 1968 IEEE
- Bellman-Ford: "Bellman 1958 / Ford 1956"
- Floyd-Warshall: "Floyd 1962 CACM"
- max-flow Ford-Fulkerson 1956 Canadian J Math
- FFT Cooley-Tukey 1965 Math Comp
- DPLL: "Davis Putnam Logemann Loveland 1962 CACM"
- CDCL: "Marques-Silva Sakallah 1999"
- Hindley-Milner: "Damas Milner 1982 POPL"
- Curry-Howard: "Howard 1980 To H B Curry Festschrift"
- Paxos 见上
- LQR: 用 "Anderson Moore 2007 Optimal Control" 或 Kalman 1960
- iLQR / DDP: "Todorov Li 2005" / "Mayne 1966"
- RRT LaValle 1998
- RRT*: "Karaman Frazzoli 2011 IJRR"
- SLAM: "Durrant-Whyte Bailey 2006 IEEE RAM"
- HOG: "Dalal Triggs 2005 CVPR"
- SIFT: "Lowe 2004 IJCV" / Lowe 1999 ICCV
- Harris: "Harris Stephens 1988 Alvey Vision"
- RANSAC: "Fischler Bolles 1981 CACM"
- Lucas-Kanade: "Lucas Kanade 1981 IJCAI"
- VC dimension: "Vapnik Chervonenkis 1971"
- PAC: "Valiant 1984 CACM"
- Rademacher: "Bartlett Mendelson 2002 JMLD"
- Demographic parity / Equalized odds: "Hardt Price Srebro 2016 NIPS"
- Counterfactual fairness: "Kusner et al 2017 NIPS"
- do-calculus: "Pearl 1995" / Pearl Causality 2009 textbook
- PC algorithm: "Spirtes Glymour Scheines 2000 book"
- IV: "Wright 1928" / Angrist Imbens 1995
- Submodular: "Nemhauser Wolsey Fisher 1978"
- GP-UCB: "Srinivas Krause Kakade Seeger 2010 ICML"
- Paxos 见上
- FLP impossibility: "Fischer Lynch Paterson 1985"
- Byzantine generals: "Lamport Shostak Pease 1982 ACM TOPLAS"
- Nash equilibrium: "Nash 1950 Annals of Math"
- VCG: "Vickrey 1961 / Clarke 1971 / Groves 1973"
- regret minimization: "Littlestone Warmuth 1994" / multiplicative weights
- Bayes net: "Pearl 1988 book"
- junction tree: "Lauritzen Spiegelhalter 1988 J Royal Stat Soc B"
- particle filter: "Gordon Salmond Smith 1993 IEE Proc F"
- Kalman 见上

不许凭印象编 ID。**不确定就写论文标题+作者+会议+年份**，不写 arXiv 编号。

### 2.3 代码内容要求
- **真算法，不是 stub**。例如：实现 Dijkstra 必须真的找到最短路；实现 HMM 前向算法必须真的递归计算 α 值；实现 Paxos 必须真的能在 Prepare/Promise/Accept/Ack 之间状态迁移。
- **3-5 个逻辑分段**（class 或 函数群），对应 lecture 推进。
- 关键公式用 LaTeX 注释（行内 `# Attention: softmax(QK^T / sqrt(d_k)) V`）
- **ASCII 可视化优先**：表格、bar chart、流程图、状态机
- 严禁 matplotlib（除非题目本身是图像/图形学，可用 PIL 或纯 PPM/ASCII）

### 2.4 文件尾部强制 `if __name__ == "__main__":` 块
- 自测试 + demo
- 必须 print 一个 **「反直觉发现」**（参照 Stanford 的风格——揭示一个非平凡结论的数字）
- 例如：「PCA 第一主成分占 99.9% 方差」「投掉 1 个方向，拒绝率从 99.9%→25.5%」

---

## STEP 3 — 共享 core/ 基础设施（每个大学都建一份）

**省时策略**：可以 `cp -r ~/ai/work4ai/stanford-cs-projects/core/ <uni>-cs-projects/core/`，然后批量替换头部注释和 docstring 里的"Stanford" → "<uni>"。

必须有的文件：
- `core/__init__.py`：版本号 + 大学名
- `core/llm.py`（~150 行）：litellm wrapper，配 Mock LLM 类（不联网），返回确定性回答用于测试
- `core/rag.py`（~200 行）：chunking（sliding window）+ embedding（用 hash mock）+ top-k retrieval
- `core/tools.py`（~150 行）：calculator / search / file_reader 三个标准工具
- `core/react.py`（~200 行）：ReAct 主循环（thought-action-observation）
- `core/eval.py`（~200 行）：4-tuple（query, context, response, reference）评估框架 + pass@k 计算
- `core/hybrid_search.py`（~150 行，可选）：BM25 + Dense 混合检索

---

## STEP 4 — supplementary/ 补充课程微项目（每个大学都建一份）

3 个文件，每个 ~400-600 行，覆盖那些没进 12 主题但有代表性的课程。

格式：一个文件里 8-12 个 `def micro_<coursenumber>_<topic>():` 函数，每个函数 30-80 行实现一个具体的小算法/小演示。

| 文件 | 覆盖范围 |
|------|---------|
| `undergrad_projects.py` | 本科基础/进阶课程 8-12 门 |
| `grad_projects.py` | 研究生专题课程 8-12 门 |
| `micro_projects.py` | 杂项（实验课、seminar、special topics）8-12 门 |

---

## STEP 5 — README.md 主文档（~300-500 行）

**严格**参照 `stanford-cs-projects/README.md` 的章节顺序：

1. **标题**：`# 🎓 <大学简称> CS 2026 - 全课程项目实战（完整版）`
2. **完成度徽章**：`✅ 全部 12 个主题 + 补充课程微项目`
3. **覆盖统计**：`~XX 门（核心 + 补充）`
4. **主题完成情况表**（13 行：12 主题 + 1 补充行）
5. **快速开始**：bash run_all.sh
6. **共享基础设施表**
7. **各主题核心学习点**：每个主题一节，含数学公式（LaTeX）、关键算法、反直觉发现
8. **整体统计**（代码行数、覆盖率等）
9. **学习路径建议**（3 persona：AI 工程师 / AI 研究者 / PM/创业者）
10. **关键参考论文**（10 篇，必须真实）

---

## STEP 6 — COMPLETION_REPORT.md（~80-120 行）

简明清单：
- 文件清单 + 行数统计
- 12 主题 + supplementary 完成状态
- 已知缺口（哪些课没覆盖、为什么）
- 测试情况

---

## STEP 7 — run_all.sh

```bash
#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
echo "=== <大学> CS 全课程项目一键运行 ==="
for d in topic*/; do
    echo "--- $d ---"
    (cd "$d" && python3 *.py)
done
echo "--- supplementary ---"
python3 supplementary/undergrad_projects.py
python3 supplementary/grad_projects.py
python3 supplementary/micro_projects.py
echo "=== ✅ 全部完成 ==="
```

---

## STEP 8 — requirements.txt

留空或仅写 `numpy>=1.20`（多数项目应该纯标准库）。

---

## QUALITY BAR — 强制质量门槛

1. ✅ **代码可运行**（Python 3.10+，每个 .py 都能 `python3 file.py` 跑完不报错）
2. ✅ **算法正确**（实现 Dijkstra 真的最短路；HMM forward-backward 真的能解码）
3. ✅ **arXiv ID 真实**（不许编造；不确定就写论文标题+会议+年份）
4. ✅ **每个文件有「反直觉发现」**（main demo 揭示一个非平凡结论）
5. ✅ **零外部 API**（mock LLM 兜底）
6. ✅ **LaTeX 数学公式**（README + 代码注释里都要有）

## 约束
- 不许用 matplotlib（图像/图形学题除外，可用 PIL）
- 不许用 torch/tensorflow/sklearn
- 不许 import OpenAI/Anthropic 客户端
- 所有代码必须能在 `python3 file.py` 单文件运行

---

## 完成后自检清单

```bash
# 1. 结构核对
find <uni>-cs-projects/ -type f | sort
# 应当至少有：
# - 12 个 topic*/*.py
# - 6 个 core/*.py
# - 3 个 supplementary/*.py
# - README.md, COMPLETION_REPORT.md, run_all.sh, requirements.txt

# 2. 行数统计
wc -l <uni>-cs-projects/topic*/*.py <uni>-cs-projects/supplementary/*.py <uni>-cs-projects/core/*.py

# 3. Python 语法快速校验（不运行，仅编译）
for f in $(find <uni>-cs-projects -name "*.py"); do python3 -c "import ast; ast.parse(open('$f').read())"; done
```

---

**现在开始**：先读 Stanford 3 个文件（README + 2 个 topic），然后建目录、写文件、最后写 README。
