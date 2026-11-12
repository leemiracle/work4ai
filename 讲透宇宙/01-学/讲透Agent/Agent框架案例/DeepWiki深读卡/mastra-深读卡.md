# mastra 深读卡 —— TS 生态的全栈 Agent 平台：Agent 循环本身即一条可持久化的 workflow

> **定位**：TypeScript 生产级 Agent 应用框架（Agent+Workflow+Tool+Memory+RAG+Evals 一体），常被视为"LangChain 的 TS 对手/Next.js of AI Agents"。核心差异化是把 ReAct 循环实现为 workflow（天然获得 suspend/resume、快照、time travel），94 provider/3373+ 模型统一路由，CLI+Studio+Deployer 全链路开发体验。
> **本地**：`repos/mastra`（mastra-ai/mastra）｜**深读**：deepwiki 119 子页归档 `deepwiki/mastra/full.md`（2026-08-21）

## 一、组件栈（DeepWiki 蒸馏）

| 层 | 职责 | 关键实体 |
|---|---|---|
| 核心容器 | 注册/装配所有子系统（DI 容器） | `Mastra` class（`src/mastra/index.ts`），agents/workflows Map |
| Agent 层 | LLM+工具+记忆的执行单元 | `Agent`、`AgentController`（交互会话）、Agent Networks、`ClaudeSDKAgent` 等外 SDK 包装 |
| Agentic Loop | LLM→Tool→LLM 循环 | `loop()`、`llm-execution-step`、`tool-call-step`、`MessageList` |
| Workflow 层 | 多步编排/控制流/持久化 | `createWorkflow/.then/.parallel/.branch/.foreach`、三引擎（Default/Inngest/Evented）+Temporal |
| 工具层 | 工具定义/校验/审批 | `createTool`、`CoreToolBuilder`（Zod 多版本+provider 兼容）、MCP client/server |
| 记忆存储层 | 消息/线程/向量/语义召回 | `@mastra/memory`、Working/Observational Memory、`MastraCompositeStore`（PG/LibSQL…） |
| 平台层 | API/客户端/部署 | hono Server（多框架适配）、client-js/React SDK、Cloudflare/Vercel Deployer、Studio |
| 质量层 | 可观测+评测 | OTel tracing、scorers、datasets/experiments、`@mastra/rag` |

## 二、核心机制

1. **循环即 workflow（最大创新点）**：Agentic Loop 用 `dowhile` 工作流实现——`LLM_EXECUTION → TOOL_CALL(foreach) → LLM_MAPPING → IS_TASK_COMPLETE` 四步循环（来源：Agentic Execution Loop (The Loop)）。Agent 对话循环因此免费获得 workflow 的 suspend/resume、快照持久化、time travel、崩溃恢复——LangChain 系里 Agent 循环和 workflow 是两套东西，Mastra 把它们统一成一层。
2. **可替换执行引擎（hook 模式）**：`ExecutionEngine` 抽象基类 + `DefaultExecutionEngine`（内存）被 `InngestExecutionEngine` 继承并只覆写 sleep/retry/durable-operation 等 hook，即获得跨进程持久化；`EventedExecutionEngine` 走 PubSub 事件驱动分布式的执行；另有 Temporal 引擎（来源：Execution Engines）。换引擎不改编排代码。
3. **人机协同内建在工具层**：`requireToolApproval` 触发 `tool-call-approval` chunk + `suspend()`；工具内部可 `context.suspend()` 长挂起，恢复后由 `SaveQueueManager` 先落盘消息再续跑；审批时强制串行并发（来源：The Loop / Suspend and Resume）。
4. **产品化全栈闭环**：`mastra dev`（热重载+file-based routing）→ Studio 调试 → `mastra build/deploy`（Cloudflare/Vercel/Netlify）→ client-js/React SDK 消费；模型层用 provider registry 生成 3373+ 模型类型（`"openai/gpt-4o"` 统一 ID + fallback 链 + gateway），TS 类型自动补全直达模型名（来源：Overview / Model Provider System）。

## 三、与讲透系列的对位

| mastra 概念 | 讲透系列对应概念 |
|---|---|
| `loop()` LLM_EXECUTION/TOOL_CALL dowhile 工作流 | 讲透Agent：ReAct 循环（这里循环被"工作流化"） |
| Agent Networks（routing agent 路由分发）+ Signals/Channels + A2A | 讲透多Agent协作：路由编排模式、Agent 间通信 |
| tool approval + `suspend()`/resume + snapshot | 讲透多Agent协作：human-in-the-loop 安全栅栏 |
| Working/Observational Memory + MessageList 格式化 | 讲透Agent：记忆机制、上下文工程（压缩/改写） |
| scorers/datasets/experiments + Workspace 沙盒（E2B） | 讲透学习型Agent：自进化（评测驱动迭代）+ 安全沙盒 |

## 四、关键入口

```text
repos/mastra/packages/core/src/mastra/index.ts            # Mastra 容器：注册 agents/workflows/storage，DI 根
repos/mastra/packages/core/src/agent/agent.ts             # Agent 类：generate/stream、模型 fallback、网络委托
repos/mastra/packages/core/src/loop/loop.ts               # agentic loop 入口：LLM→Tool→LLM 循环编排
repos/mastra/packages/core/src/loop/workflows/agentic-execution/tool-call-step.ts  # 工具执行步：审批/suspend/并发控制
repos/mastra/packages/core/src/agent/durable/durable-agent.ts  # DurableAgent：循环状态逐步持久化、崩溃恢复
repos/mastra/packages/core/src/workflows/default.ts       # DefaultExecutionEngine：hook 模式模板方法
repos/mastra/packages/core/src/tools/tool.ts              # createTool/CoreToolBuilder：Zod→各 provider schema 转换
repos/mastra/packages/memory/src/index.ts                 # @mastra/memory：线程/召回/working memory
```

## 五、深读子页地图（119 页精选 5）

1. **Agentic Execution Loop (The Loop)**（P15）—— 全仓最核心：循环的 workflow 化实现、chunk 类型、signal 注入。
2. **Execution Engines**（P22）—— 三引擎对比矩阵与 hook 覆写表，理解"可插拔持久化"的最短路径。
3. **Workflow State Management and Persistence**（P23）—— snapshot 持久化时机、resume 与 time travel 的状态学。
4. **Observational Memory System**（P50）—— 区别于千篇一律 RAG 记忆的观察式记忆设计（含与 Working Memory 的分工，P51）。
5. **Glossary: Core Runtime Concepts**（P117）—— 119 页概念的术语总表，迷路时回这里。

## 六、与"我们"的关系（一句话）

对学 Agent 的人，这是**"工程完整度天花板"级的参照系**——想看 ReAct 循环如何被持久化工程、HITL 如何嵌进工具层、一个 Agent 框架如何长成全栈产品（CLI/Studio/部署/评测），读它比读 LangChain 更成体系。

---
生成：2026-08-21 · deepwiki 119 页全归档
