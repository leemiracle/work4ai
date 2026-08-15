# CS329Z HW3: 4-tuple Evaluation Suite — Agent 评估方法论

> **课程**: CS329Z Engineering AI Agents (Autumn 2025)
> **作业**: HW3 — 占总评 10%
> **对应模块**: W7 Evaluation Fundamentals · W7 LLM-as-Judge
> **代码位置**: `topic2-agent-v2/hw3_self_improve_coding.py` (PART 1)
> **完成度**: ★★★★★ (4-tuple + 多种 scorer + pass@k vs pass^k)
> **最后更新**: 2026-08-11

---

## 📚 作业定位

HW3 是 CS329Z **方法论最核心**的作业。学生拿到一个预构建 agent，需要设计**完整的 evaluation suite**。CS329Z 的核心贡献是 **4-tuple 评估框架**：

> **(request, environment, stopping_criteria, scorer)**

这不是调库跑指标，而是系统性地思考"什么算成功"、"怎么测量"、"在什么环境里测"。同时覆盖 **pass@k vs pass^k** 这个衡量 agent 可靠性的非确定性指标。

> 注：本文件还包含 CS329A STaR self-improve 和 CS329M coding agent 实现，HW3 文档聚焦 PART 1 的 4-tuple Eval。

---

## 📅 核心模块

### 1. EvalTuple — 4-tuple 数据结构
```python
@dataclass
class EvalTuple:
    name: str
    request: str                          # 测试请求
    environment: dict                     # tools / knowledge / constraints
    stopping_criteria: Callable           # 何时算"结束"
    scorer: Callable[[str], tuple[float, str]]  # 打分 + rationale
```
**关键设计**：scorer 返回 `(score, rationale)` 而非纯分数——便于 debug 和 LLM-as-judge。

### 2. EvalHarness — 评估套件引擎
- `add(case)`：链式添加测试用例
- `run(agent_fn, n_runs)`：跑 n_runs 次，计算 pass@k vs pass^k
- 判定逻辑：`passed = (score >= 0.7) and terminated`
- 完整异常容错：agent 崩溃记为 `[ERROR]`

### 3. 五种标准 Scorer
| Scorer | 适用场景 | 实现 |
|--------|---------|------|
| `exact_match_scorer(expected)` | 精确事实 | 子串匹配 |
| `numeric_scorer(expected, tol)` | 数值计算 | 正则提取数字 + 容差 |
| `keyword_scorer(keywords, min_hits)` | 知识检索 | 关键词命中计数 |
| `llm_judge_scorer(rubric)` | 开放式问答 | rubric 词命中 + 长度 + 推理信号 |
| 自定义 lambda | 长度/格式约束 | 闭包打分 |

### 4. pass@k vs pass^k — 可靠性度量（核心创新）
- **pass@k**（at least 1 pass）：k 次运行中至少 1 次通过 → 衡量**能力上限**
- **pass^k**（all k pass）：k 次运行全部通过 → 衡量**可靠性下限**
- **reliability_gap = pass@k − pass^k**：差距越大，agent 越不稳定
- `pass^k > 0.8` → ✅ Reliable；否则 ⚠️ Unreliable

这是 CS329Z 区别于传统 ML eval 的关键——**agent 是非确定性的，单次跑通不等于可靠**。

---

## 💻 项目代码

**文件**: `topic2-agent-v2/hw3_self_improve_coding.py` (函数 `hw3_demo`)

**运行**：
```bash
cd topic2-agent-v2
python3 hw3_self_improve_coding.py
# 选择 hw3_demo() 部分
```

**5 个测试用例**：
1. `math_addition` — "What is 23+17?" → `numeric_scorer(40.0)`
2. `knowledge_rag` — "What is RAG?" → `keyword_scorer(["retrieval","generation","knowledge"])`
3. `open_ended_explanation` — "Explain attention" → `llm_judge_scorer(rubric)`
4. `tool_use_required` — "sqrt(144)" → `numeric_scorer(12.0)`
5. `length_constrained` — "Summarize in 2 sentences" → 自定义长度 scorer

**输出示例**：
```
📊 Results (5 runs):
   pass@5 (at least 1 pass): 100.0%
   pass^5 (all runs pass):   100.0%
   Reliability gap: 0.0%
   → ✅ Reliable
```

---

## 📊 关键论文

1. 🔴 **Anthropic 2026** "Demystifying Evals for AI Agents" — 8-step eval roadmap
2. 🔴 **Ryan et al. 2026** "AutoMetrics" — 讲师 Michael Ryan 一作
3. 🔴 **Zheng et al. 2023** "MT-Bench / Chatbot Arena" — LLM-as-judge 范式
4. 🟡 **Press 2024** "How to Build Good LM Benchmarks"
5. 🟡 **Polo et al. 2024** "tinyBenchmarks" — 小而精的 benchmark

---

## 🎯 学习路径建议

1. **理解 4-tuple**：每个测试用例必须显式定义 request / environment / stopping / scorer——缺一不可
2. **重点跑 pass@k vs pass^k**：把 mock_agent 改成随机性更强的版本，观察 reliability_gap 变化
3. **生产化**：接入真实 agent + 真实 LLM-as-judge（替代 mock scorer）→ 设计针对你自己 agent 的 eval suite

---

## 💡 核心反思

- **4-tuple 是可推广的方法论**：不只适用于 agent eval，任何 AI 系统评估都可用
- **pass@k vs pass^k 是 agent eval 的灵魂**：传统 ML eval 只测能力，agent eval 必须测可靠性
- **LLM-as-judge 有 bias**：position bias / verbosity bias / self-preference——需要 pairwise + 多 judge 校准
- **好的 eval 比好的 agent 更难**——这是 CS329Z 反复强调的核心论点
