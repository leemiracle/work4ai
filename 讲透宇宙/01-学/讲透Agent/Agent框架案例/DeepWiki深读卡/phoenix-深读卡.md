# phoenix 深读卡 —— LLM/Agent 可观测性+评估的开源参考实现（OTLP tracing × evals × React UI 三位一体）

> **定位**：Phoenix 是 Arize 开源的 AI observability 平台：FastAPI 服务器接收 OpenTelemetry (OTLP) traces（gRPC 4317 / HTTP 6006），落库 SQLite/PostgreSQL，经 GraphQL/REST API 驱动 React UI 做 trace 可视化、LLM-as-judge 评估与实验对比。它同时把"评估"做成一等公民（Dataset/Experiment/Annotation 实体），甚至内嵌了一个 pydantic-ai 构建的 Agent 助手 PxI——**用 Phoenix 追踪 Phoenix 自己**，是 Agent 可观测性的活教材。
> **本地**：`repos/phoenix`（Arize-ai/phoenix）｜**深读**：deepwiki 39 子页归档 `deepwiki/phoenix/full.md`（2026-08-21）

## 一、组件栈（DeepWiki 蒸馏）

| 层 | 职责 | 关键实体 |
|---|---|---|
| 埋点/导出层 | 应用侧单调用注册 tracer + 自动 instrument | `phoenix.otel.register()`、`HTTPSpanExporter`/`GRPCSpanExporter`（`packages/phoenix-otel`、`js/packages/phoenix-otel`）、`openinference-instrumentation-*` |
| 摄入层 | OTLP protobuf 解码 → 队列 → 批量落库 | `Servicer.Export()`（`server/grpc_server.py`）、`decode_otlp_span()`（`trace/otel.py`）、`BulkInserter` + `_spans deque`（`db/bulk_inserter.py`） |
| API 层 | GraphQL + REST v1 + Agent + MCP | Strawberry `api/schema.py`、`api/routers/v1/`、`/v1/agents/assistant/chat`、`/mcp` 端点 |
| 数据层 | ORM + 迁移 + 双引擎 | `db/models.py`（Trace/Span/Dataset/Experiment/Prompt…）、Alembic `db/migrations/`、`db/engines.py`（SQLite/PostgreSQL） |
| 前端 | SPA 展示 trace 树/表格/Playground | `app/`（React + Vite + Relay + Zustand），`TraceTree`/`SpansTable` |
| Agent 层（PxI） | 内置 AI 助手编排 | `agents/agent_factory.py`（pydantic-ai）、`model_factory.py`、`capabilities/`（Bash/CallSubAgent/Skills/MCP） |
| 客户端 SDK | 脱离服务器的 API/评估调用 | `arize-phoenix-client`、`arize-phoenix-evals`、`@arizeai/phoenix-mcp`（monorepo 独立版本，release-please 管理） |

## 二、核心机制

1. **解耦摄入管道（削峰 + 背压）**：OTLP 请求 → `decode_otlp_span()` 在 threadpool 解码（防阻塞 asyncio loop）→ `_enqueue_span()` 入 deque → `BulkInserter` 后台任务按 `max_ops_per_transaction` 批量写库；队列满时 `is_full` 触发拒绝，Prometheus 指标（`phoenix_span_queue_size`、`span_insertion_time_seconds`）全程监控。〔源：OTLP Ingestion & gRPC Server〕
2. **三层实体宇宙**：Tracing 侧 `Project → Trace → Span(parent_id 树)` + `ProjectSession` 聚合多轮对话；实验侧 `Dataset/Version/Example/Revision + Experiment/ExperimentRun`；评估侧 `SpanAnnotation`（label/score/explanation，annotator 分 LLM/HUMAN/CODE）+ `Evaluator`（LLM/Code 两亚型，引用 PromptVersion）。〔源：Core Concepts & Terminology〕
3. **OpenInference 语义约定是数据契约**：SpanKind 十类（`LLM/CHAIN/TOOL/AGENT/RETRIEVER/RERANKER/EMBEDDING/EVALUATOR/GUARDRAIL/…`）+ 标准属性键（`input.value`、`llm.token_count.prompt`、`retrieval.documents`），让任意框架的 trace 可互通分析；查询侧 `SpanFilter` 把 **Python 子集表达式经 AST 编译成 SQLAlchemy 子句**（支持 `evals['quality'].label == 'high'` 这类注解过滤）。〔源：Tracing & Observability〕
4. **事件驱动 + Agent 自举**：落库后发 `DmlEvent` 入事件队列，异步 daemon（如 `SpanCostCalculator`）做成本计算；PxI 用 `build_agent()` 组合 capabilities（含 subagent、沙箱 Bash、MCP docs、skills 包），每个能力包 `OpenInferenceCapabilityWrapper` 做埋线——Agent 调用本身成为可评估的 trace。〔源：Tracing & Observability、AI Agent Backend (PxI)〕

## 三、与讲透系列的对位

| phoenix 机制 | 讲透系列对位 | 可落地的 experiment |
|---|---|---|
| OTLP span 树（AGENT/TOOL span） | 讲透Agent 的工具调用/多智能体协作章节 | `register()` + instrument 给自己手写的 ReAct/swarm agent 装上"显微镜"，trace 树即执行日志 |
| LLM-as-judge（`phoenix-evals`，hallucination/QA/toxicity） | 讲透LLM / 讲透RAG 的评估收尾章节 | 对讲透RAG 的检索结果批量跑 relevance/hallucination evals，标注对比 |
| `SpanFilter` DSL（Python AST → SQLAlchemy） | 讲透Python 的 AST/元编程主题 | 手写 mini filter DSL 复现"表达式→SQL"编译直觉 |
| PxI 的 capability/skills/MCP 组合 | 讲透Agent 的 MCP 协议章节 | 读 `agent_factory.py` 学生产级 agent 装配模式（对比玩具实现） |
| Dataset/Experiment 版本化对照 | ml-experiment 的基线对比方法论 | 把不同 prompt/模型的输出入 dataset 跑 experiment，产出回归表 |

## 四、关键入口

```python
# 最小可用：起服务器 + 埋点（src/phoenix/__init__.py）
import phoenix as px
session = px.launch_app()                      # http://localhost:6006

from phoenix.otel import register
from openinference.instrumentation.openai import OpenAIInstrumentor
tracer_provider = register()                   # 默认导出到本机 Phoenix
OpenAIInstrumentor().instrument(tracer_provider=tracer_provider)
```

```text
读码路线（由外向内）：
src/phoenix/server/grpc_server.py      # OTLP Export 入口（4317）
src/phoenix/trace/otel.py              # decode_otlp_span: protobuf → 内部 Span
src/phoenix/db/bulk_inserter.py        # 队列 + 批量写 + 背压
src/phoenix/db/insertion/span.py       # insert_span: trace/session/token 累计
src/phoenix/db/models.py               # 全部实体 ORM（602-2087 行区间）
src/phoenix/trace/dsl/filter.py        # AST → SQLAlchemy 过滤 DSL
src/phoenix/server/agents/agent_factory.py  # PxI agent 装配（pydantic-ai）
```

## 五、深读子页地图（39 页精选 6）

| 页 | full.md 行号 | 为什么值得读 |
|---|---|---|
| 1.2 Core Concepts & Terminology | 541–961 | 实体 ER 图 + 每个概念的 ORM 行号索引，全库地图 |
| 2.4 OTLP Ingestion & gRPC Server | 2079–2307 | 摄入管道全链路：解码/队列/批量/背压/Prometheus |
| 2.5 Database Layer & Migrations | 2308–2698 | Alembic 迁移与双引擎（SQLite↔PostgreSQL）策略 |
| 5.1 Tracing & Observability | 6956–7341 | OpenInference 约定 + SpanFilter DSL + UI 组件对应 |
| 5.6 AI Agent Backend (PxI) | 9158–9494 | pydantic-ai 工厂/capability/context/tracing 自举 |
| 7 Glossary | 12419–末尾 | 术语表，写教程引用时的定名依据 |

## 六、与"我们"的关系（一句话）

讲透Agent/讲透RAG 教程缺的正是"生产级可观测性后端"——phoenix 提供从 OpenInference 数据契约到 PxI 自举 tracing 的完整范本，直接当 experiment 基建和架构参考抄。

---
生成：2026-08-21 · deepwiki 39 页全归档
