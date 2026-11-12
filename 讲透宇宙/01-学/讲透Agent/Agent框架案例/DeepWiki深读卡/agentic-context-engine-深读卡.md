# agentic-context-engine 深读卡 —— 给 Agent 挂上"经验→策略"持久学习环的开源框架

> **定位**：ACE（Agentic Context Engine）是 kayba-ai 出品的 Agent 自学习框架——不做 fine-tuning、不手写 prompt，而是给 Agent 加一条 **Execute → Evaluate → Reflect → Update** 的闭环，把执行 trace 反思成策略，沉淀进可检索的 **Skillbook**。核心创新是 **Recursive Reflector（RR）**：让 LLM 在沙箱 REPL 里写 Python 代码去程序化分析 trace，而非单遍总结。生产指标：Tau2 基准 pass 率翻倍、浏览器自动化 token 省 49%、14k 行代码翻译零构建错误。
> **本地**：`repos/agentic-context-engine`（kayba-ai/agentic-context-engine）｜**深读**：deepwiki 93 子页归档 `deepwiki/agentic-context-engine/full.md`（2026-08-21）

## 一、组件栈（DeepWiki 蒸馏）

| 层 | 职责 | 关键实体 |
|---|---|---|
| Core Library `ace/` | 三角色学习环 + 各框架 Runner | `Agent` / `Reflector` / `SkillManager`；Runner：`ACE`（在线）、`TraceAnalyser`（离线学日志）、`ACELiteLLM` / `ACEBrowserUse` / `ACELangChain` / `ACEClaudeCode` |
| Pipeline Engine `pipeline/` | 通用不可变编排引擎，学习环的底座 | `Pipeline` / `StepProtocol` / `Branch` / `async_boundary` |
| Recursive Reflector | 沙箱代码化 trace 深析（可插拔替换标准 Reflector） | `RRStep` / `RecursiveAgent` / `TraceSandbox` / `recurse` 子代理 |
| Shared Foundation | 知识存储 + 模型接入 | `Skillbook` / `Skill` / `UpdateBatch`（ADD/UPDATE/TAG/REMOVE）；PydanticAI + LiteLLM（100+ providers），BM25 检索 |
| Tracing SDK `sdk/` | 采集 Agent 执行 trace 供反思 | `kayba-tracing`（Python/TypeScript）+ Logfire 可观测 |

## 二、核心机制

1. **四阶段学习环（§2.1）**：`AgentStep → EvaluateStep → ReflectStep → UpdateStep` 各自是可组合的 Pipeline Step；Agent 从 Skillbook 取策略注入 system prompt，并在推理中引用策略编号（如 `[section-001]`）以追踪哪些 skill 真正生效；SkillManager 产出 `UpdateBatch`（ADD/UPDATE/TAG/REMOVE）原子化更新 Skillbook。
2. **Learning Tail + 异步边界（§2.1/§3.2.5）**：慢速的 Reflect→Update 两步通过 `async_boundary` 甩到后台线程，Agent 答案在 Evaluate 后立即返回——高吞吐执行与后台持续学习解耦。
3. **Recursive Reflector（§3.3，全 wiki 灵魂）**：`RRStep` 继承 `RecursiveAgent`，在 `TraceSandbox`（受限 builtins、超时强杀、变量跨调用持久）里迭代"写代码→看输出→再 refine"；六阶段策略 Discover→Adapt→Survey→Categorize→Deep-dive→Synthesize；带 evidence guard——没探索数据就提前产出 `ReflectorOutput` 会被 `ModelRetry` 打回。
4. **递归子代理与上下文管理（§3.3.4）**：`recurse` 工具把子问题派发给隔离子会话（继承父沙箱变量副本，`max_depth=2`，同轮多调用并行，共享根预算）；两级 compaction（Micro 清工具输出保沙箱态 / Full 全对话摘要）撑住长 trace。

## 三、与讲透系列的对位

| ACE 概念 | 讲透系列/已有项目对位 |
|---|---|
| Learning Loop（经验→策略库） | agent-development 的"记忆机制/自我改进 Agent"章节的一手工程实现 |
| Skillbook + BM25 检索 | 讲透NLP 的反向索引/词法检索——策略库本质是"带引用追踪的 mini RAG" |
| RecursiveAgent REPL 工具环 | agent-development 的 ReAct/工具调用；但 ACE 反向为之——用 Agent 驱动数据分析 |
| Pipeline/StepProtocol 不可变编排 | LangChain/LangGraph 框架选型对照：自研轻量 DAG vs 重框架 |
| TraceSandbox 安全执行 | ai-os-dd/Lean4 的"可验证执行环境"思路在 Python 侧的对应物 |
| Trace→Insight 离线学习（TraceAnalyser） | neo-os 可解释性：对执行痕迹做程序化归因 |

## 四、关键入口

```python
# repos/agentic-context-engine
from ace import Agent, Reflector, SkillManager        # 三角色
from ace import ACE, TraceAnalyser                    # 在线 runner / 离线学日志
from ace import Pipeline, AgentStep, EvaluateStep, learning_tail  # 手动编排学习环

runner = ACE.from_roles(agent, reflector, skill_manager, environment)
results = runner.run(samples, epochs=3)               # 每轮带着更成熟的 Skillbook 重访任务
```
文件入口：`ace/__init__.py`（总导出）· `ace/steps/__init__.py`（`learning_tail`）· `ace/runners/{ace,litellm,claude_code,browser_use,langchain,trace_analyser}.py` · `pipeline/pipeline.py` · `ace/core/{recursive_agent,sandbox}.py`（RR 内核）· `ace/integrations/mcp/server.py`（MCP 暴露 ask/learn/skillbook）· `examples/ace/ace_demo.py`

## 五、深读子页地图（93 页精选 8）

| 子页 | full.md 行号 | 价值 |
|---|---|---|
| §2.1 The ACE Learning Loop | L775 | 主线索：四阶段闭环全图 + 异步学习尾，必读首页 |
| §2.2 Skillbook System | L1051 | 策略库 schema、分区存储与 BM25 检索 |
| §3.2 Pipeline Engine | L2820 | 不可变 Step/Context 引擎，ACE 与框架解耦的底座 |
| §3.3 Recursive Reflector System | L4160 | 核心创新总览：REPL 环、双协议、六阶段、compaction |
| §3.3.2 Sandbox Environment | L4605 | `SAFE_BUILTINS`/dunder 屏蔽/超时实现细节 |
| §7.5 Claude Code Integration | L10388 | 自改进编码回路实战（最贴近日常使用） |
| §7.7 MCP Server Integration | L10914 | 把 ask/learn/skillbook 做成 MCP 工具 |
| §9.8 Safety and Security | L14733 | 沙箱逃逸防护与学习环安全边界 |

## 六、与"我们"的关系（一句话）

ACE 把"反思"本身变成可执行代码验证（RR 写 Python 分析 trace），与讲透系列三层宪法"直觉→公式→代码跑通"同构，是 agent-development 记忆机制/自改进章节最完整的一手案例库。

---
生成：2026-08-21 · deepwiki 93 页全归档
