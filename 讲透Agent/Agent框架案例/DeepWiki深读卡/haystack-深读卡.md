# haystack 深读卡 —— 把 LLM 应用编排成类型化组件 DAG 的生产级框架

> **定位**：Haystack（PyPI 包 `haystack-ai`，Apache 2.0，Python ≥3.10）是 deepset 出品的开源 AI orchestration 框架，用 `@component` 装饰器把 Generators/Retrievers/Converters 等组件接成有向图 Pipeline，主打 RAG 与 Agentic 工作流的"explicit control over data flow"（context engineering）。v3.0 完成三项收敛：集成拆包到 `haystack-core-integrations`、只留 ChatGenerator、`ToolInvoker` 取消——工具执行循环原生归 `Agent` 组件持有。
> **本地**：`repos/haystack`（deepset-ai/haystack）｜**深读**：deepwiki 27 子页归档 `deepwiki/haystack/full.md`（2026-08-21）

## 一、组件栈（DeepWiki 蒸馏）

| 层 | 职责 | 关键实体 |
|---|---|---|
| Core 框架 `haystack.core` | 组件契约 + DAG 编排 + 序列化 | `@component`/`ComponentMeta`、`InputSocket`/`OutputSocket`、`PipelineBase`→`Pipeline`/`AsyncPipeline`、`FIFOPriorityQueue`、`ComponentPriority`、`SuperComponent`、`PipelineSnapshot`/`Breakpoint` |
| 工具抽象 `haystack.tools` | LLM 工具调用统一封装 | `Tool`、`ComponentTool`、`PipelineTool`、`AgentTool`、`Toolset`/`SearchableToolset`、`MCPToolset` |
| Agent 层 `haystack.components.agents` | 自主循环 + 共享状态 + HITL | `Agent`、`State`（schema 校验）、hooks（`before_llm`/`before_tool`/…）、`ConfirmationHook` |
| 数据模型 `haystack.dataclasses` | 跨组件互操作标准 | `Document`、`ChatMessage`、`Answer` |
| 组件库 `haystack.components` | 开箱即用 LLM/检索/构建 | `OpenAIChatGenerator`、`InMemoryBM25Retriever`、`ChatPromptBuilder` |
| 文档处理 `document_stores`/converters/embedders | RAG 数据面 | `InMemoryDocumentStore`、各类 Converter、Embedder/Ranker |
| 工程基建 | 环境与发布流水线 | Hatch（envs+scripts）、Ruff、reno release notes、`pyproject.toml` 单一事实源 |

## 二、核心机制

1. **组件契约（Component System 页）**：`@component` 装饰器经 `ComponentMeta` 元类完成三件事——校验 `run()` 存在、按方法签名自动生成 `__haystack_input__`/`__haystack_output__` socket、注册进 `component.registry` 供反序列化。生命周期铁律：`__init__` 极轻量（参数必须 JSON 可序列化、存入 `init_parameters`）→ `warm_up()` 承载重资源 → `run()`/`run_async()`（二者签名与输出类型必须严格一致，置 `__haystack_supports_async__`）。
2. **调度内核（Pipeline System 页）**：图存于 `networkx.MultiDiGraph`，调度靠 `FIFOPriorityQueue` + `ComponentPriority` 四级优先级（`HIGHEST`=greedy variadic 独占 / `READY`=输入齐 / `DEFER`=等 Variadic 汇聚 / `BLOCKED`=缺必需输入）；`Variadic[T]` 与 `GreedyVariadic[T]` 区分"等齐再跑"与"来一个跑一个"两种汇聚语义；每组件 visit 计数对撞 `_max_runs_per_component` 防死循环。v3.0 起 `AsyncPipeline` 并入标准 `Pipeline`（Overview 页）。
3. **可恢复执行（Pipeline System 页）**：组件异常统一包装为 `PipelineRuntimeError` 并附带 `PipelineSnapshot`（含完整内部输入态 `dict[component][socket]=list` 与 `AgentSnapshot`）；`Breakpoint`（组件名+visit 数）与 `AgentBreakpoint`（包 `ToolBreakpoint`）支持断点暂停，`run(pipeline_snapshot=...)` 校验图一致性后原地恢复——把"长时 Agent 运行"变成可持久化、可审计的对象。
4. **Agent 内循环（Agent System + Tool Invocation 页）**：v3.0 `Agent` 自持工具执行（`_run_tool`/`_run_tool_async`），循环到 `exit_conditions`（默认 `["text"]`）或 `max_agent_steps`（默认 100）双保险；`State` 是 schema 校验容器（自动含 `messages: list[ChatMessage]`，list 字段默认 `merge_lists`、其余 `replace_values`），并自动写入保留元数据 `step_count`/`token_usage`/`tool_call_counts`/`exit_reason`；六个 hook 切点中 `before_tool` 挂 `ConfirmationHook`（`BlockingConfirmationStrategy` + Always/NeverAskPolicy）实现 HITL；工具侧 `inputs_from_state`/`outputs_to_state` 完成 State 注入/抽取，`SearchableToolset` 按查询动态取工具防 prompt 溢出，工具报错默认回传 LLM 自我恢复。

## 三、与讲透系列的对位

| Haystack 实体 | 讲透系列对位 | 对位点 |
|---|---|---|
| `InMemoryBM25Retriever` + Embedder + `DocumentStore` | 讲透NLP（检索/嵌入章节） | BM25/向量检索从讲义玩具到工业组件的直接映射 |
| `ChatPromptBuilder` + `ChatMessage` 四角色 | 讲透NLP（对话/提示词部分） | system/user/assistant/tool 消息模型的工程化落地 |
| `Pipeline` 类型化 socket + DAG | Agent 框架选型主题（vs LangGraph） | "静态类型图编排"路线的最佳对照样本（LangGraph 是动态图路线） |
| `Agent` loop + `Tool`/`Toolset`/MCP | 工具调用/MCP 主题（agent-development） | 工具 schema 自动生成、并行执行、错误回传 LLM 的完整实现 |
| `State` + hooks + HITL | 多智能体协作主题 | 状态合并策略与生命周期切点的教科书案例 |
| `SuperComponent`/`PipelineTool` | （待补全候选） | "Pipeline 即组件/工具"的递归组合思想 |

## 四、关键入口

```python
# 最小 RAG 骨架（三大件：DocumentStore → Retriever → ChatGenerator）
from haystack import Pipeline
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack.components.retrievers import InMemoryBM25Retriever
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.components.builders import ChatPromptBuilder

pipe = Pipeline()
pipe.add_component("store", InMemoryDocumentStore())      # add_component：名唯一/禁 "."/"_debug" 保留
pipe.add_component("retriever", InMemoryBM25Retriever(store=pipe["store"]))
pipe.connect("retriever", "prompt_builder")               # 按类型自动匹配 socket
result = pipe.run({"retriever": {"query": "..."}})

# 源码导航（本地 repos/haystack）
# haystack/core/component/component.py      @component / ComponentMeta / registry
# haystack/core/pipeline/base.py            PipelineBase / ComponentPriority / 图与序列化
# haystack/core/pipeline/pipeline.py        同步执行循环 + snapshot 恢复
# haystack/core/pipeline/async_pipeline.py  Semaphore 并发 + run_in_executor 卸载同步组件
# haystack/core/super_component/super_component.py  Pipeline 包成组件
# haystack/components/agents/agent.py       Agent 主循环 / _run_tool / exit_conditions
# haystack/components/agents/state/state.py State schema + 合并策略
# haystack/tools/tool.py / component_tool.py / searchable_toolset.py
# haystack/dataclasses/{document,chat_message,breakpoints}.py
```

## 五、深读子页地图（27 页精选 6）

| 子页 | full.md 行号 | 为什么值得读 |
|---|---|---|
| Haystack Overview | L6 | 三层架构总览 + v3.0 四大变更（拆包/ChatGenerator 收敛/Agent 持工具/AsyncPipeline 合并）一页看懂 |
| Component System | L1810 | `@component` 元类魔法全解：socket 自动生成、warm_up 契约、pre-init hooks |
| Pipeline System | L2072 | 调度内核最硬核一页：优先级队列、Variadic 语义、Snapshot 断点恢复 |
| Agent System | L5691 | Agent 循环时序图 + State schema + 六切点 hooks + HITL 策略 |
| Tool Invocation | L5895 | Tool 家族（ComponentTool 自动 schema/PipelineTool/AgentTool）+ 状态注入抽取 |
| Migration Guide v2.x→v3.0 | L6475 | 框架演进决策记录，理解"为什么砍 ToolInvoker" |

## 六、与"我们"的关系（一句话）

Haystack 是讲透系列"Pipeline 组件系统 + RAG 主线"最值得对照拆解的工业级样本——它的类型化 socket、Snapshot 可恢复执行和"Pipeline 即 Tool"递归组合，正是讲透Agent 框架选型（vs LangChain/LangGraph）一章的现成案例素材。

---
生成：2026-08-21 · deepwiki 27 页全归档
