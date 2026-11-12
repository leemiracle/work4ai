# agentgpt 深读卡 —— 前端跑循环 + 后端无状态 LLM 编排的第一代自主任务分解 Agent Web 应用

> **定位**：AgentGPT（reworkd 出品，2023 爆款）让用户在浏览器输入一个目标，Agent 自主将其分解为任务列表，逐个 analyze→选工具→execute→根据结果再生成新任务，直到 conclude。它最反直觉的设计是：**自主循环跑在浏览器前端**（`AutonomousAgent` + workLog 队列），FastAPI 后端只是无状态的 6 个 LLM 编排端点（start/analyze/execute/create/summarize/chat）。
> **本地**：`repos/agentgpt`（reworkd/AgentGPT）｜**深读**：deepwiki 21 子页归档 `deepwiki/agentgpt/full.md`（2026-08-21）

## 一、组件栈（DeepWiki 蒸馏）

| 层 | 职责 | 关键实体 |
|---|---|---|
| 前端 UI（Next.js 13 + TS + TailwindCSS/HeadlessUI） | Landing 输入目标、ChatWindow 实时渲染消息/任务 | `pages/index.tsx`、`ChatWindow`、`ChatMessage`、`SummarizeButton` |
| 前端状态 | agent 生命周期、任务、消息的集中管理（Zustand） | `agentStore` / `taskStore` / `messageStore`（offline→running→pausing→paused→stopped） |
| Agent 执行引擎（**跑在前端**） | 自主循环：workLog 队列调度 + 重试 + 生命周期控制 | `AutonomousAgent`、`AgentWork` 子类（`StartGoalWork`/`AnalyzeTaskWork`/`SummarizeWork`/`ChatWork`，各含 run/conclude/next/onError） |
| 后端 API（FastAPI + Pydantic） | 6 个无状态端点做 LLM 编排与工具执行，流式返回 | `views.py`：`POST /agent/{start,analyze,execute,create,summarize,chat}` |
| Agent Service（协议 + 双实现） | 任务生成/分析/执行/总结的 LLM 调用逻辑，token 管理 | `AgentService` Protocol、`OpenAIAgentService`、`MockAgentService`（ff_mock_mode_enabled 切换）、`model_factory`（WrappedChatOpenAI/Azure + Helicone） |
| 工具系统 | 6 种任务执行工具，OpenAI function calling 选择 | `Search`(Serper)、`Image`(Replicate)、`Code`、`Reason`、`Wikipedia`、`Conclude`（Tool 基类 + `get_tool_from_name`） |
| 数据层 | 双 ORM：前端 Prisma、后端 SQLAlchemy，共用 MySQL | AgentExecution、User/Org（NextAuth）、OAuth 凭据 |
| 部署 | Docker Compose 三容器 + CLI 交互式生成 .env | next / platform / db 三服务，`setup.sh` |

## 二、核心机制

1. **前端驱动的 workLog 执行循环**（来源：Agent Lifecycle，full.md L4673）：`AutonomousAgent.run()` 从 `workLog[0]` 顺序取 `AgentWork` → `runWork()`（带指数退避重试）→ `shift()` 出队 → `work.conclude()` 收尾 → `work.next()` 把后继工作（如 AnalyzeTaskWork→下一条任务）push 回队列——这就是"自主"的全部秘密：一个跑在浏览器里的协作式调度队列，而非后端守护进程。
2. **6 端点映射 6 方法的 LLM 编排协议**（来源：Agent Service，full.md L3197）：`start_goal_agent` 用 `start_goal_prompt` 分解目标 → `TaskOutputParser` 解析任务列表；`analyze_task_agent` 把工具映射成 OpenAI function definitions 让 LLM 选工具（解析进 `Analysis` 对象，失败回落 `get_default_analysis`）；`execute_task_agent` 实例化 Tool 流式执行；`create_tasks_agent` 按"上次任务+结果"动态生成新任务并**过滤已完成任务防死循环**（返回 `["conclude"]` 信号收尾）。
3. **状态机 + 代理模式的状态管理**（来源：Agent Lifecycle）：`AgentLifecycle` 五态由 `DefaultAgentRunModel` 代理读写 `useAgentStore`（get/setLifecycle 直接调 store）；`chat()` 与 `summarize()` 是"特殊操作"——chat 会先 pauseAgent 再插队 `ChatWork`，summarize 仅在 stopped 且有已完成任务且未总结过时触发。
4. **Token 预算工程**（来源：Agent Service）：`TokenService.calculate_max_tokens` 按模型上限动态扣减 prompt 占用；summarize/chat 强切 `gpt-3.5-turbo-16k`、max_tokens=8000、输入截断到 7000 tokens——2023 年 4k 上下文时代的典型生存技巧。

## 三、与讲透系列的对位

| AgentGPT 实体 | 讲透系列对应主题 | 备注 |
|---|---|---|
| workLog 循环 + AgentWork(run/next) | Agent 循环/规划（CoT→ToT→ReAct 演进） | 无显式 ReAct prompt，是"任务队列版"自主循环 |
| analyze_task_agent function calling | 工具调用 / MCP | function calling 早期形态，对照 MCP 的标准化 |
| TaskOutputParser + prompts.py | Prompt 工程（结构化输出/JSON 解析） | 正则+Pydantic 双保险，解析失败兜底 |
| Zustand 三 store / 生命周期状态机 | Agent 记忆机制（短期记忆=store，无长期记忆） | 纯内存态，刷新即失——记忆缺失是它的时代局限 |
| MockAgentService / ff_mock_mode_enabled | ML/Agent 实验可复现性 | 测试替身 + feature flag 的工程范式 |
| 双 ORM + 流式 SSE | Agent 工程化部署 | 对照 vLLM/SSE 流式与讲透部署篇 |

## 四、关键入口

```text
# 前端自主循环（本仓库灵魂，Agent 跑在浏览器里）
next/src/services/agent/autonomous-agent.ts        # run() 主循环 / runWork() 重试 / chat() / summarize()
next/src/services/agent/agent-work/*.ts            # StartGoal / AnalyzeTask / Summarize / Chat 四种工作项
next/src/stores/agentStore.ts                      # lifecycle 状态机（offline/running/pausing/paused/stopped）

# 后端 LLM 编排（无状态，6 端点）
platform/reworkd_platform/web/api/agent/views.py               # POST /agent/{start,analyze,execute,create,summarize,chat}
platform/reworkd_platform/web/api/agent/agent_service/
    open_ai_agent_service.py         # 6 方法实现 + token 管理 + 16k 模型切换
    agent_service_provider.py        # 工厂：ff_mock_mode_enabled → Mock / OpenAI
platform/reworkd_platform/web/api/agent/tools/tools.py          # 工具注册表 + get_tool_from_name
platform/reworkd_platform/web/api/agent/prompts.py              # start_goal / analyze_task / create_tasks / summarize 模板
```

## 五、深读子页地图（21 页精选 6）

| 页 | full.md 行 | 为何值得读 |
|---|---|---|
| 1 Overview | L6 | 全栈分层图 + 执行时序图，5 分钟建立心智模型 |
| 11 Agent Service | L3197 | **信息量最大（20KB）**：6 方法逐个拆解含代码级细节、Model Factory、错误处理 |
| 15 Agent Lifecycle | L4673 | **最大页（23KB）**：workLog 循环 flowchart、状态机、chat/summarize 特殊路径 |
| 16 Task Execution | L5159 | 目标→任务→工具→结论的完整数据流（12 张图） |
| 17 Prompts and Output Parsing | L5483 | 4 类 prompt 模板 + TaskOutputParser 解析/兜底策略 |
| 12 Agent Tools | L3658 | Tool 基类接口与 6 工具执行流，看早期 tool-calling 设计 |

## 六、与"我们"的关系（一句话）

AgentGPT 是讲透 Agent 系列最理想的"第一代解剖标本"——用一个前端 workLog 队列 + 6 个无状态 LLM 端点就把"自主规划-执行-再规划"讲透了，正适合对照 agent-development 里 LangChain/LangGraph/MCP 的演进讲清"Agent 到底自治在哪一层"。

---
生成：2026-08-21 · deepwiki 21 页全归档
