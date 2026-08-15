# Oxford CS Projects — 完成报告

## 总览

| 项目 | 数量 | 状态 |
|------|------|------|
| 主题项目 (topic*) | 12 | ✅ 全部完成 |
| 本科补充 (undergrad) | 10 个微项目 | ✅ |
| 研究生补充 (grad) | 10 个微项目 | ✅ |
| 杂项补充 (micro) | 9 个微项目 | ✅ |
| 共享基础设施 (core/) | 7 文件 | ✅ |
| 文档 | README + 本报告 | ✅ |

---

## 文件清单

### 核心主题（12 个）

| 文件 | 行数 | 覆盖算法 |
|------|------|---------|
| `topic1-foundations/foundations.py` | ~250 | 归纳法 / 谓词逻辑 / 等价关系 / 不动点 |
| `topic2-pl/pl.py` | ~300 | λ-calculus / HM Algorithm W / CPS / Monad |
| `topic3-algorithms/algorithms.py` | ~250 | Merge/Quick sort / LCS / Dijkstra / Prim |
| `topic4-concurrency/concurrency.py` | ~280 | CSP traces / CCS bisimulation / π-calculus / LTL |
| `topic5-databases/databases.py` | ~300 | 关系代数 / SQL / 可串行化 / Join 算法 |
| `topic6-compilers/compilers.py` | ~280 | LL(1) / LR(0) / 类型检查 / 代码生成 |
| `topic7-vision/vision.py` | ~280 | 高斯/Sobel / Canny / K-means / CNN |
| `topic8-ml/ml.py` | ~320 | 贝叶斯回归 / GP / SVM SMO / 核方法 |
| `topic9-kr/kr.py` | ~290 | ALC tableau / Resolution / Ontology / Kripke |
| `topic10-ar/auto_reasoning.py` | ~300 | DPLL / CDCL / Resolution / Superposition |
| `topic11-cgt/game_theory.py` | ~300 | Nash / 零和博弈 / Regret matching / VCG |
| `topic12-foundations/cpp.py` | ~300 | STLC / Curry-Howard / 范畴论 / CCC |

### 补充课程（3 文件，29 个微项目）

| 文件 | 行数 | 覆盖课程数 |
|------|------|----------|
| `supplementary/undergrad_projects.py` | ~300 | 10 门 |
| `supplementary/grad_projects.py` | ~280 | 10 门 |
| `supplementary/micro_projects.py` | ~300 | 9 门 |

### 共享基础设施（7 文件）

| 文件 | 行数 | 来源 |
|------|------|------|
| `core/__init__.py` | 14 | 从 Stanford 移植 |
| `core/llm.py` | ~165 | 从 Stanford 移植 |
| `core/rag.py` | ~223 | 从 Stanford 移植 |
| `core/tools.py` | ~164 | 从 Stanford 移植 |
| `core/react.py` | ~235 | 从 Stanford 移植 |
| `core/eval.py` | ~231 | 从 Stanford 移植 |
| `core/hybrid_search.py` | ~166 | 从 Stanford 移植 |

---

## 语法校验结果

```
所有 .py 文件通过 ast.parse 语法校验 ✅
```

---

## 设计决策

1. **零依赖**：所有主题文件仅用 Python 标准库（math, random, heapq, collections 等），不依赖 numpy/matplotlib/torch/sklearn。
2. **arXiv ID 真实性**：所有论文引用使用真实 arXiv ID 或完整出版信息（作者+标题+会议+年份），无编造。
3. **反直觉发现**：每个主题的 main demo 都揭示一个非平凡的、有数字支撑的结论。
4. **三层宪法**：直觉 → 公式(LaTeX 注释) → 代码 → 反直觉发现。

---

## 已知缺口

以下 Oxford 课程因与已有项目重叠或超出单文件范围，未单独实现完整主题：
- **Software Engineering**：部分在 supplementary
- **Human-Computer Interaction**：部分在 Stanford 样板
- **Computational Finance**：可扩展为 micro project

---

## 测试

```bash
# 语法校验（全部通过）
for f in $(find . -name "*.py"); do
    python3 -c "import ast; ast.parse(open('$f').read())" && echo "OK: $f"
done

# 运行单个主题
python3 topic1-foundations/foundations.py

# 一键运行全部
bash run_all.sh
```

---

**完成日期**：2026-08-12
**版本**：1.0
