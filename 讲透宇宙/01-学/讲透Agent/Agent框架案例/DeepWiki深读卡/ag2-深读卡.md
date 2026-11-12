# AG2 深读卡 —— AutoGen 社区分叉的持续演进版（ConversableAgent + GroupChat 经典线 + Swarm/Realtime/A2A 新线）

> **定位**：ag2ai/ag2 是 AutoGen 0.2 时代核心团队（Chi Wang 等）的社区分叉，**延续并演进了 AutoGen 原经典架构**——`ConversableAgent` 双向对话 + `GroupChat` 群聊编排，同时叠加 2025-2026 新能力：SwarmAgent 动态编排、Realtime 语音 Agent、A2A/AG-UI 协议、依赖注入工具、OTel tracing。当 microsoft/autogen 转向 0.4 重构（core/agentchat/ext 分层）并进入维护模式时，AG2 是"经典 AutoGen 血统"的活跃继承者。
> **本地**：`repos/ag2`（ag2ai/ag2）｜**深读**：deepwiki **59 子页**归档 `deepwiki/ag2/full.md`（2026-08-21，~1MB）

## 一、组件栈（DeepWiki 蒸馏）

| 层 | 职责 | 关键实体 |
|---|---|---|
| 核心对话 | 双向可对话 Agent | `ConversableAgent`（24KB 专页：generate_reply 链 + register_reply）、`AssistantAgent`/`UserProxyAgent` |
| 群聊编排 | GroupChat 系 | `GroupChat` + `GroupChatManager`（auto/manual/speaker selection）、nested chat、`GroupChat目标` |
| 动态编排 | Swarm 模式 | `SwarmAgent`（handoff 即注册的工具）+ `ContextVariables` 共享状态（21KB 专页）|
| 实时会话 | 语音 | `RealtimeAgent`（WebRTC）|
| LLM 层 | 多供应商 | `OpenAIWrapper`（client 缓存池）、ModelClient V2 `UnifiedResponse` 统一返回 |
| 工具 | 注册+DI | `register_function` + **依赖注入**（按类型注解注入 agent/db 等上下文，23 页）|
| 代码执行 | 多后端 | local/docker/jupyter executor |
| 互操作 | 协议 | MCP（26 页）+ **A2A Client/Server**（33-34 页）+ AG-UI Adapter（35 页，前端事件流）|
| 可观测 | 日志/追踪 | Runtime Logging（30 页：session 记录）、OpenTelemetry（32 页）、Hooks 生命周期（31 页 20KB）|

## 二、核心机制

1. **register_reply 责任链**（ConversableAgent 页）：`ConversableAgent.generate_reply` 按 LLM→工具→自定义 reply 的注册顺序组合应答——一切交互模式（群聊/swarm/nested）都是往这条链上挂 hook 的变体，是经典 AutoGen 的心脏。
2. **Swarm + ContextVariables**（18/29 页）：`SwarmAgent` 把 handoff 实现为普通工具调用（返回下一个 agent 名）；共享状态走 `ContextVariables`（update_context 装饰器）——对照 OpenAI swarm 实验版的"生产化转正"。
3. **工具依赖注入**（23 页）：`register_function` 支持按参数类型注解自动注入 `ConversableAgent`/db 连接等运行时对象——工具签名即依赖声明，超越 plain function calling。
4. **AG-UI Adapter**（35 页）：把 agent 会话事件转成 AG-UI 前端协议（消息/状态/工具事件流）——与 A2A（agent 间）组成"对外双协议"矩阵。

## 三、与讲透系列的对位

| AG2 概念 | 讲透系列对应 |
|---|---|
| `ConversableAgent` register_reply 链 | 讲透Agent/01 §经典范式（AutoGen 线）|
| `GroupChat` speaker selection | 讲透多Agent协作/02 §发言权分配 |
| `SwarmAgent` handoff-as-tool | 讲透Agent/01 §Handoff |
| `ContextVariables` | 讲透多Agent协作/03 §共享状态 |
| A2A + AG-UI | 讲透Agent/02 §Agent 协议栈（MCP/A2A/AG-UI 三件套）|
| Runtime Logging + OTel | 讲透Agent/00 §可观测性 |

## 四、关键入口

```
autogen/agentchat/conversable_agent.py    # ConversableAgent（wiki 5 号页 24KB）
autogen/agentchat/groupchat/              # GroupChat 家族
autogen/agentchat/swarm_agent.py          # SwarmAgent
autogen/oai/client.py                     # OpenAIWrapper
autogen/tools/                            # 工具注册 + 依赖注入
autogen/interop/                          # A2A / AG-UI 适配
python/packages/ag2-ui/                   # UI 层
```

## 五、深读子页地图（59 页精选 8）

**5 ConversableAgent（24KB 最厚）**｜6 Message Handling｜8 GroupChat（19KB）｜18 SwarmAgent｜22-23 Function Calling + 依赖注入｜29 ContextVariables（21KB）｜31 Hooks（20KB）｜33-35 A2A/AG-UI 三连页。

## 六、与"我们"的关系（一句话）

AG2 保留了讲透Agent 教学最友好的"经典 AutoGen"主线（ConversableAgent+GroupChat），又补齐 2026 协议层（MCP/A2A/AG-UI）——是连接 AWESOME-AGENTS-ANALYSIS 里 AutoGen 旧分析与当下生态的桥梁仓库。

---
生成：2026-08-21 · deepwiki 59 页全归档 · 与 microsoft/autogen（维护模式）形成分叉对照
