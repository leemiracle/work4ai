# agentdock 深读卡 —— 一切皆节点的"可配置确定性" TypeScript Agent 框架

> **定位**：AgentDock 是用 TypeScript 写的 AI Agent 构建框架，核心哲学是 **configurable determinism**（可配置确定性）——AgentNode 天生非确定（LLM 推理），但通过编排好的工具执行路径让整体行为可控。仓库双组件：`agentdock-core/`（后端框架）+ Next.js OSS Client（参考实现），所有能力（Agent、Tool、LLM Provider）统一抽象为 Node。
> **本地**：`repos/agentdock`（AgentDock/AgentDock）｜**深读**：deepwiki 35 子页归档 `deepwiki/agentdock/full.md`（2026-08-21）

## 一、组件栈（DeepWiki 蒸馏）

| 层 | 职责 | 关键实体 |
|---|---|---|
| OSS Client（Next.js） | 参考实现前端：聊天界面、设置页、布局系统 | `ChatContainer`、`/api/chat/[agentId]`、Zustand state、Tailwind+ShadCN/UI |
| Agent Adapter（桥接层） | API 路由 ↔ 核心框架的粘合 | `processAgentMessage()`、`_adapterContext`、`toDataStreamResponse` |
| Node System（核心抽象） | 一切皆节点：统一配置/执行/元数据接口 | `BaseNode`、`NodeCategory`（CORE/TOOL/LLM_PROVIDER/UTILITY）、`NodePort`/`NodeMetadata` |
| Agent 执行层 | 会话式 Agent 的中央执行引擎 | `AgentNode.handleMessage()`、主/备 LLM、system prompt 动态注入 |
| LLM Integration | 多 Provider 统一接口 + 编排式流式调用 | `CoreLLM`、`ProviderRegistry`、`LLMOrchestrationService.streamWithOrchestration()` |
| Tool 层 | 工具注册与按 Agent 过滤 | `DefaultToolRegistry`（单例）、`getToolsForAgent()`、Search/Deep Research/Weather 等 Tool |
| Orchestration | 按会话状态控制行为流与工具可见性 | `OrchestrationManager`、`AIOrchestrationState`、`getAllowedTools()` |
| Session/Storage | 会话隔离状态 + 可插拔存储 | `SessionManager`、Redis / Vercel KV provider |
| 配置层 | 声明式 Agent 定义 | `agents/*/template.json`（personality、nodes、nodeConfigurations、chatSettings） |
| 外部服务 | LLM/OpenAI/Anthropic/Gemini/Groq/DeepSeek、Serper、Firecrawl、PostHog | API Key 三级优先解析：Agent 级 → 全局设置 → 环境变量 |

## 二、核心机制

1. **Node-based 架构（"一切皆节点"）**：`AgentNode` 与 `Tool` 同继承 `BaseNode`（`execute(input)` + `getMetadata()`），靠 `NodeCategory` 分类；工具经 `ZodSchema parameters` 声明参数Schema，注册进全局单例 `ToolRegistry`，再按 template 的 `nodes` 列表裁剪出每个 Agent 的工具集。〔来源：Node System〕
2. **Configurable Determinism（招牌设计）**：LLM 环节非确定，但开发者通过配置"哪些环节走 LLM 推理、哪些走确定性工具工作流"来滑动控制确定性刻度——混合模式下 LLM 只做子工作流选择，200 步确定性流程交给 Tool 节点。〔来源：Overview〕
3. **消息主循环**：`/api/chat/[agentId]` → `processAgentMessage()` → `new AgentNode(config)` → `handleMessage()`：查 `OrchestrationManager.getState()` → `getToolsForAgent()` → `getAllowedTools()` 过滤 → 组装 system prompt（personality + 编排动态状态 + 当前日期/时间/时区注入）→ `streamWithOrchestration()` 流式输出，tool call 回路在 `LLMOrchestrationService` 内闭环，`onFinish` 回调异步记 token 用量不阻塞首包。〔来源：Overview + AgentNode〕
4. **Fallback LLM 韧性**：`AgentNodeConfig` 支持独立的 `fallbackProvider/fallbackModel/fallbackApiKey`，`handleMessage(useFallback: true)` 时切换备用实例；若 fallback 配置与主配置完全相同则跳过并告警。〔来源：AgentNode〕

## 三、与讲透系列的对位

| agentdock 概念 | 讲透系列对位 | 备注 |
|---|---|---|
| `BaseNode`/Node System | 讲透 Agent：Agent 抽象与组件化 | "一切皆节点" ≈ LangGraph 节点/组件化思想 |
| `ToolRegistry` + Zod 参数 | 讲透 Agent：工具调用（Function Calling）章节 | 对照 LangChain Tool/MCP 协议页 |
| `LLMOrchestrationService` + `CoreLLM` | 讲透 LLM/推理服务：Provider 抽象层 | Vercel AI SDK 之上的薄封装，适合讲 streaming |
| `OrchestrationManager`（状态机控工具可见性） | 讲透 Agent：多 Agent/编排（LangGraph 对位） | 会话级状态驱动的工具门控，是确定性来源 |
| OSS Client Chat/Settings/Layout | 前端参考：讲透 Agent 实战篇 UI 层 | Zustand + ShadCN/UI 的教科书样本 |

## 四、关键入口

```
agentdock-core/src/nodes/agent-node.ts     # AgentNode：handleMessage 消息主循环（L96-455 为核心）
agentdock-core/src/nodes/tool-registry.ts  # DefaultToolRegistry 单例 + getToolsForAgent（L26-83）
agents/<agentId>/template.json             # Agent 模板：personality/nodes/nodeConfigurations
src/app/api/chat/[agentId]/route.ts        # 消息入口 API 路由
src/lib/agent-adapter.ts                   # processAgentMessage：API↔Core 桥接（L90-208）
```

## 五、深读子页地图（35 页精选 5）

| 页 | full.md 行号 | 为什么值得读 |
|---|---|---|
| 2.1 Node System | L1525 | 全库最长页；BaseNode 接口 + 节点分类 + ER 关系一页讲透 |
| 3.1 AgentNode | L4261 | 执行引擎细节：初始化/消息流/工具过滤/时间注入/错误处理 |
| 3.2 Tool Registry | L4723 | 紧接 Node System 的工具注册全貌（含实现源码） |
| 2.3 Orchestration System | L2459 | 确定性刻度的实际控制面（OrchestrationManager 状态机） |
| 5.3 Deep Research Tool | L10150 | 最有含金量的内置工具：多阶段深度研究的参考实现 |

## 六、与"我们"的关系（一句话）

讲透 Agent 系列的现成"节点化 + 可配置确定性"参考实现——用最小概念集（BaseNode/ToolRegistry/Orchestration）演示了从 Function Calling 到编排分层的完整骨架，可直接当对照代码库拆解。

---
生成：2026-08-21 · deepwiki 35 页全归档
