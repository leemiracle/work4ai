# aideml 深读卡 —— 用"解树搜索"替代单次生成的自主 Kaggle 竞赛 Agent

> **定位**：AIDE ML（AI-Driven Exploration in the space of code）是 WecoAI 维护的开源 ML 竞赛自动化 Agent——用户给 `data_dir + goal + eval` 三件套，它自主生成 Python 方案、沙盒执行、按 metric 迭代改进，产出一棵带性能标注的 solution tree。论文 arXiv:2502.13138，OpenAI MLE-Bench 上其 tree search 比 best linear agent 多拿 4× 奖牌，被 AI-Scientist-v2、ML-Master 等用作基件。
> **本地**：`repos/aideml`（WecoAI/aideml）｜**深读**：deepwiki 30 子页归档 `deepwiki/aideml/full.md`（2026-08-21）

## 一、组件栈（DeepWiki 蒸馏）

| 层 | 职责 | 关键实体 |
|---|---|---|
| L1 用户接口 | 三入口汇聚同一核心 | CLI `aide`（Hydra）、Python API `Experiment`、Streamlit Web UI、Docker |
| L2 编排 | 配置/任务/生命周期管理 | `Experiment`（aide/\_\_init\_\_.py）、OmegaConf `config.yaml`、`load_task_desc()` |
| L3 核心执行 | 生成-执行-评估闭环 | `Agent`（三模式代码生成+搜索策略）、`Interpreter`（subprocess 沙盒）、`Journal`+`Node`（solution tree） |
| L4 LLM 抽象 | 按模型名自动路由 | `backend.query()` → OpenAI / Anthropic / Gemini / OpenRouter 适配器 |
| 产物 | 每步落盘、可容错 | `best_solution.py`、`tree_plot.html`、`journal.json`、`experiment.cfg`、`report.md` |

## 二、核心机制

1. **Agentic Tree Search 主循环**（来源：Overview、Experiment Execution Flow）：`while global_step < steps`（默认 20）内执行 `agent.step()` → 沙盒执行 → LLM 评审 → `journal.append(node)` → `save_run()` 每步落盘（fault tolerance）。每 node = 一个完整 Python 方案，边 = 代码修改，`stage_name` 由 parent 状态推导出 Draft / Debug / Improve 三型。
2. **search_policy 三岔决策**（来源：Agent & Search System）：① `draft_nodes < num_drafts` → `_draft()` 白手起家（含 `journal.generate_summary()` 记忆）；② `random() < debug_prob` → 从"buggy + leaf + `debug_depth ≤ max_debug_depth`"集合随机选节点 `_debug()`（喂 code + term_out）；③ 否则 `get_best_node()` → `_improve()`，prompt 明确要求"single atomic improvement"。探索/利用/修复全靠 `num_drafts / debug_prob / max_debug_depth` 三旋钮。
3. **双 LLM 角色分工 + 结构化评审**（来源：Agent & Search System）：`cfg.agent.code`（生成）与 `cfg.agent.feedback`（评审）可配不同模型；评审走 `review_func_spec` function calling，强制输出 `is_bug / summary / metric / lower_is_better` 四字段，落成 `MetricValue`——其比较运算符内嵌优化方向，`get_best_node()` 直接 `max(nodes, key=metric)`。
4. **沙盒执行与隔离**（来源：Experiment Execution Flow、skeleton #22）：`Interpreter.run()` 在隔离子进程执行代码，`RedirectQueue` 捕获 stdout/stderr，超时默认 300s，返回 `ExecutionResult`（term_out + return code）——buggy 判定与 debug prompt 的原料。

## 三、与讲透系列的对位

| aideml 机制 | 讲透系列/主题对位 |
|---|---|
| Agentic Tree Search（solution tree + best-first 选择） | Agent 开发（agent-development）：无框架裸 Python 单 Agent 的反例参照——不靠 LangGraph，靠数据结构 |
| `debug_prob` 随机修复 vs 贪心改进 | RL（rl-learning）：exploration/exploitation 的工程化 ε-greedy 变体 |
| `review_func_spec` 四字段 schema | Prompt 工程（prompt-engineering）：结构化输出/function calling 的最小干净案例 |
| goal+eval 自然语言任务规约 → 自动实验 | ML 实验（ml-experiment）："自动调参/特征工程"的 Agent 化终点 |
| Interpreter 多进程隔离 + timeout | OS/工程直觉：沙盒即资源隔离，与 ai-os-dd 的进程语义互通 |
| `MetricValue.lower_is_better` 比较语义 | 代码细节课：把"优化方向"编码进类型的教科书做法 |

## 四、关键入口

```bash
# CLI（Hydra 覆盖任意 config 键）
aide data_dir="example_tasks/house_prices" \
     goal="Predict the sales price for each house" \
     eval="RMSE between log-prices" \
     agent.search.num_drafts=10 exec.timeout=300
```
```python
# Python API（aide/__init__.py）
from aide import Experiment
exp = Experiment(data_dir="example_tasks/bitcoin_price",
                 goal="Build a time series forecasting model", eval="RMSLE")
sol = exp.run(steps=20)   # Solution(code, valid_metric)
```
```
源码导航：aide/agent.py:61 search_policy / :175 _draft / :207 _improve / :243 _debug / :276 step
         aide/journal.py:21 Node / :165 get_best_node　aide/interpreter.py Interpreter.run
         aide/backend/__init__.py query() 路由　aide/run.py CLI 主循环
```

## 五、深读子页地图（30 页精选 5）

| 页 | 行号 | 为什么值得读 |
|---|---|---|
| #6 Experiment Execution Flow | L1518 | 全链路时序图最全（7 mermaid），主循环唯一权威页 |
| #21 Agent & Search System | L6425 | 三模式 prompt 构造 + 三超参语义，Agent 心脏 |
| #22 Code Interpreter | L6693 | 多进程沙盒/队列/timeout 实现细节，隔离范式样本 |
| #14 Backend Architecture & Router | L3882 | 模型名→provider 路由 + FunctionSpec 跨厂商抽象 |
| #3 Key Concepts | L761 | 概念术语表前置页，与 #30 Glossary 配套速查 |

## 六、与"我们"的关系（一句话）

AIDE 是讲透Agent/RL 系列最干净的实拍教材——把"exploration vs exploitation"压缩成三个 yaml 旋钮、把"LLM 评审"压成一个 function calling schema，读它等于同时复习搜索算法与 Agent 工程两课。

---
生成：2026-08-21 · deepwiki 30 页全归档
