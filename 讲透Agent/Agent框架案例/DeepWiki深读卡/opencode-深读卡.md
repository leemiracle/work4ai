# opencode 深读卡 —— 开源终端 AI 编码 Agent 的"客户端-服务器"参考实现：一个 Hono 后端同时喂 TUI/Desktop/VS Code/Web 四种前端

> **定位**：opencode（sst/opencode，MIT）是对标 Claude Code 的 provider 无关终端 AI 编码 Agent，支持 75+ LLM provider（Anthropic/OpenAI/Bedrock/本地 Ollama，外加自营 Zen/Go 网关）。架构核心是 client-server 分离：TUI（SolidJS）、Electron Desktop、VS Code 扩展、Web 全部通过 HTTP+SSE 连到同一个 Effect/Hono 后端，agent loop、工具执行、会话状态全在服务端。工程上是一座 Bun + Turbo monorepo，深度使用 Effect 生态做依赖注入与 Schema 校验（Zod/Effect 混合），正处于 V1→V2（`lildax` 新 CLI + core 领域层）演进期。
> **本地**：`repos/opencode`（sst/opencode）｜**深读**：deepwiki 71 子页归档 `deepwiki/opencode/full.md`（2026-08-21）

## 一、组件栈（DeepWiki 蒸馏）

| 层 | 职责 | 关键实体 |
|---|---|---|
| Client Layer | 四端 UI，全部经 SDK 走 HTTP/SSE | TUI（`@opentui/solid`）、`packages/desktop`（Electron）、VS Code ext、`@opencode-ai/sdk` |
| API Layer | HTTP 路由 + 实时事件推送 | `Server.App`（`#hono` 适配器）、PublicApi、SSE/Global Event Bus、WebSocketTracker |
| Session 层（业务核心） | prompt 编排、agent loop、上下文压缩 | `SessionPrompt.Service/loop()`、`SessionProcessor.Service`、`SessionCompaction.Service`、`MessageV2` |
| Provider Layer | 75+ 模型接入与归一化 | `Provider.Service/getModel()`、`BUNDLED_PROVIDERS`、`ProviderTransform`、`LLM.Service/stream()` |
| Tool/Integration Layer | 工具注册、权限门禁、外部协议 | `ToolRegistry.Service`、`Tool.define()`、`MCP.Service`、`LSP.Service`、Plugin hooks |
| Storage Layer | 会话持久化 | SQLite + Drizzle ORM（`#db` 别名）、SessionTable/MessageTable/PartTable、`auth.json` |
| 扩展面 | 用户自定义 | `.opencode/agent/`、`.opencode/tool/*.ts`、`@opencode-ai/plugin`、Skills |
| 周边系统 | 商业化与集成 | Console（Zen/团队管理，Stripe）、Slack bot、GitHub Action、ACP |

## 二、核心机制

1. **`SessionPrompt.loop()` 状态机式 agent loop**（来源：2.3 Prompt Processing Pipeline、1.2 Architecture Overview）：每轮先处理 pending task（`SubtaskPart` 递归子代理 → `CompactionPart` 维护任务）→ `isOverflow` 检查 → `ToolRegistry.tools()` 按当前 agent 权限过滤工具集 → `SystemPrompt` 组装 → `SessionProcessor.process()` 消费 `LLM.stream` 流式输出（Text/Reasoning/Tool 三种 Part 增量落库）→ 按 continue/compact/stop 三态决定循环去向。终止条件是 terminal finish reason；`DOOM_LOOP_THRESHOLD=3` 防止模型原地打转空转工具调用。
2. **三级上下文防御：buffer → prune → compaction → replay**（来源：2.4 Context Management and Compaction）：`COMPACTION_BUFFER` 20k tokens 提前触发；prune 反向扫描旧 ToolPart 输出（保护最近 2 个 user turn、`PRUNE_PROTECT` 40k / `PRUNE_MINIMUM` 20k 门槛、`skill` 工具永不剪）；compaction 用专用 agent loop 按 `SUMMARY_TEMPLATE`（Goal/Constraints/Progress/Key Decisions/Next Steps/Critical Context）生成摘要替换历史；replay 克隆最后一条 user message（媒体转文本占位符防再溢出）。压缩本身再溢出 = `ContextOverflowError` 不可恢复态。
3. **Effect 化工具系统 + 三态权限门禁**（来源：5.1 Tool Architecture、5.2 Permission System）：工具 = `{id, description, parameters(Effect Schema), execute}` 四元组，registry 统一包装 telemetry span、schema 解码、`truncate.output` 自动截断；来源三路合并（builtin + `.opencode/tool/*.ts` 自定义 + plugin/MCP）。每次执行前 `ctx.ask()` 走 allow/deny/ask 三态规则（通配符模式匹配），ask 时用 `Effect.Deferred` 挂起等 UI 审批；文件类工具强制 `assertExternalDirectoryEffect` 路径边界断言。
4. **Provider 归一化与容错**（来源：1.2、2.3）：`ProviderTransform` 处理各家怪癖（surrogate 清洗、tool result 里的媒体降级为后续 user message、输出 token 上限），`SessionRetry` 指数退避 + jitter 且尊重 `retry-after` 头（上限 5 次）；结构化输出通过注入 `StructuredOutput` 工具 + 专用 system prompt 强制 JSON Schema 合规。

## 三、与讲透系列的对位

| opencode 机制 | 讲透系列对应主题 | 备注 |
|---|---|---|
| `SessionPrompt.loop()` 状态机 | 讲透 Agent loop / ReAct | 生产级 ReAct：不是朴素 while，而是 task 优先级 + overflow + 三态出口 |
| Compaction/Prune/Replay | 讲透 LLM 长上下文 / 上下文管理 | 三级防御 + 模板化摘要，比"截断历史"教法深一层 |
| `Tool.define` + ToolRegistry | 讲透工具调用（function calling） | Effect Schema→JSON Schema 的运行时校验链可当案例 |
| TaskTool 子代理（background/深度限制） | 讲透多智能体协作 | 子会话而非独立进程，对照 LangGraph supervisor |
| allow/deny/ask + `Effect.Deferred` | 讲透 human-in-the-loop | 挂起-审批-恢复的干净实现 |
| MCP.Service / Skills / Plugin | 讲透 MCP 协议 | 三种扩展面并列：协议、markdown 技能、代码插件 |
| Zen/Go 网关 + Console | （商业侧） | provider 聚合变现路径，agent-development 素材 |

## 四、关键入口

```text
repos/opencode/packages/opencode/src/
├── index.ts                  # 包入口
├── server/server.ts          # Hono HTTP + SSE 服务端（listen → HttpApiApp）
├── session/
│   ├── prompt.ts             # ★ SessionPrompt.loop() —— agent loop 状态机
│   ├── processor.ts          # 流消费、ToolPart 生命周期、DOOM_LOOP 检测
│   ├── llm.ts                # LLM.Service/stream、LLMRequestPrep、GitLab 特化
│   ├── compaction.ts         # isOverflow、prune、SUMMARY_TEMPLATE、replay
│   └── message-v2.ts         # MessageV2：Drizzle 水合 + provider 归一化
├── tool/
│   ├── tool.ts               # Tool.define 四元组 + ToolContext(ask/abort)
│   ├── registry.ts           # ToolRegistry：builtin+custom+plugin 合并
│   └── task.ts               # TaskTool 子代理（background、深度限制）
└── provider/provider.ts      # Provider.getModel + BUNDLED_PROVIDERS（75+）
```

## 五、深读子页地图（71 页精选 6）

| 子页 | 价值 |
|---|---|
| 1 Overview | 全景架构图（含代码实体映射）+ monorepo 依赖图 + agent pipeline 时序图 |
| 1.2 Architecture Overview | 六层分层 + Effect 服务清单，读代码前的地图 |
| 2.3 Prompt Processing Pipeline | agent loop 逐阶段拆解 + retry/doom-loop 细节 |
| 2.4 Context Management and Compaction | 三级上下文防御全算法（含具体 token 阈值） |
| 5.1 Tool Architecture | Tool.define/Registry/执行时序/TaskTool 子代理 |
| 5.2 Permission System | allow/deny/ask 规则引擎 + Deferred 挂起审批 |

（备选：3.2 Agent System、4.1 Provider Architecture、5.6 MCP、2.8 Event Bus）

## 六、与"我们"的关系（一句话）

它是"讲透 Agent loop / 工具调用 / 上下文管理 / MCP"四讲的最佳生产级活教材——每个教程概念在这里都有带测试的 TypeScript/Effect 工业实现可对照，且本 agent 自身就跑在 opencode 上，读它即读自己的运行时。

---
生成：2026-08-21 · deepwiki 71 页全归档
