# Cline 深读卡 —— VSCode 原生 AI 编码 Agent（Plan/Act 双模式 + Focus Chain）

> **定位**：VSCode 扩展形态的自主编码 Agent（前身为 Claude Dev），核心是 Task 循环（LLM 流式输出→工具执行→消息回灌）+ **Plan/Act 双模式分离** + **Focus Chain 结构化进度追踪**；现已长出 CLI / SDK / ACP / Hub / Cron 全家桶。
> **本地**：`repos/cline`（cline/cline，TypeScript）｜**深读**：deepwiki **85 子页**全文归档 `deepwiki/cline/full.md`（2026-08-21，940KB——本批最大 wiki）

## 一、组件栈（DeepWiki 蒸馏）

| 层 | 职责 | 关键实体 |
|---|---|---|
| 扩展宿主 | VSCode 集成/生命周期 | `HostProvider` 抽象（VSCode/CLI/SDK 多宿主）、gRPC 服务层 |
| 任务执行 | Agent 核心循环 | `Task`、`ToolExecutor` + 20+ ToolHandler、消息状态管理 |
| 模式 | Plan/Act 分离 | 两套 system prompt（规划模式只读思考/行动模式写代码）|
| 子代理 | 任务分解 | `AgentRuntime`（SDK）派生嵌套 Agent，独立 prompt+工具集 |
| 上下文 | 窗口管理 | Context Management（compaction 压缩）+ Focus Chain 持久进度 |
| 模型层 | 多 Provider | OpenAI/Anthropic/Gemini/OpenRouter/Ollama…+ streaming 架构 |
| 安全 | 访问控制 | `.clineignore`、AutoApprovalSettings、HITL 审批、Checkpoints 快照 |
| 生态 | MCP×Skills×Hooks | MCP 5 页（含 Marketplace）、Skills 系统、Workflows、Hooks |

## 二、核心架构机制（本框架的知识增量）

1. **Plan/Act 双模式**（Plan and Act Modes 页）：同一 Task 循环、两套 system prompt 与工具权限——Plan 模式受限只读（收集上下文/制定方案），Act 模式全量工具；规避"边想边做"的破坏性行动，是 Cline 区别于单模式编码 Agent 的招牌。
2. **Focus Chain**（Subagents 页）：跨轮次/跨 compaction 的结构化任务追踪链，保证上下文压缩后不丢总目标与已完成进度——直接回答"长任务压缩后 Agent 迷失"痛点。
3. **访问控制数据流**（Access Control 页，mermaid 全景）：`.clineignore`(文件级) + `CLINE_COMMAND_PERMISSIONS`(环境变量) + AutoApprovalSettings(审批粒度) 三源配置 → `ClineIgnoreController.validateAccess()` + `isToolAutoApproved()` 双闸门 → 工具执行。
4. **MCP 三件套**（49-53 页）：McpServer 管理（remote/HTTP/stdio）+ Tools/Resources 双通道 + **MCP Marketplace**（社区服务器目录直接安装）。
5. **Cron 自动化**（Automation and Cron 页）：`.cron.md` 规格文件 → `CronService`/`CronReconciler` → SQLite 队列 → HubTransport 执行——把 Agent 从"被动应答"推向"定时自主运行"（与 opencode 的 jobs、Claude Cron 同一思潮）。
6. **Checkpoints 快照**：每步文件系统影子快照，回滚任意历史状态（对应讲透Agent 的"可逆性"设计原则）。

## 三、与讲透系列的对位

| Cline 概念 | 讲透系列对应 |
|---|---|
| Plan/Act 双模式 | 讲透Agent/03 §规划与搜索（先搜后动的工程化） |
| Focus Chain | 讲透Agent/04 §记忆机制（工作记忆持久化） |
| Context compaction | 讲透Agent/02 §上下文工程（窗口压缩） |
| Subagents/AgentRuntime | 讲透多Agent协作/01 §层级编排 |
| Checkpoints + HITL | 讲透Agent/00 §安全护栏三件套 |
| `.clineignore` 访问控制 | 讲透Agent/00 §权限模型 |

## 四、关键入口

```
src/core/task/          # Task 循环本体（消息流→工具→observation）
src/core/               # Controller 编排 / webview grpc
src/services/mcp/       # MCP 服务器管理
src/api/                # Provider 层（streaming）
sdk/packages/agents/src/agent-runtime.ts   # SDK AgentRuntime（子代理引擎）
cline CLI / ACP         # 终端形态 + Agent Client Protocol 跨编辑器标准
```

## 五、深读子页地图（85 页精选 9）

总览：1-2 Overview/Architecture｜核心循环：12-14 Task Execution/Lifecycle/ToolExecutor｜模式：16 Plan and Act｜上下文：17-18 Context Management/Subagents&Focus Chain｜安全：54-56 Safety/Checkpoints/HITL｜生态：49-53 MCP 五连页｜前沿：74 ACP / 79 Hub&Zen / 80 Cron。

## 六、与"我们"的关系（一句话）

Cline 是"IDE Agent 三大件（Plan-Act 分离、Focus Chain、Checkpoints）"教材级实现，与 opencode（CLI）、ClaudeCode（闭源标杆）构成讲透Agent/Agent架构模式参考 的三极对照——85 页 wiki 已全归档，任何章节可按行号直查。

---
生成：2026-08-21 · deepwiki 全文归档（85 页 940KB）· 唯一外部依赖：DeepWiki MCP
