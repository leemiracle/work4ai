# mateclaw 深读卡 —— Java/Spring AI 版个人 AI 操作系统：图编排 Agent + 做梦记忆 + 多 Provider 容灾

> **定位**：自托管个人 AI 助理平台（Spring Boot 3.5 + Vue 3），把 Claude Code 式 Agent 能力（ReAct/Plan-Execute 图运行时、ToolGuard 审批、SKILL.md、MEMORY.md/SOUL.md 工作区文件）完整搬进 Java 企业技术栈。核心差异化：多 Provider 健康探测自动故障转移（14+ 国产/海外模型）+ "做梦"式记忆固化 + LLM Wiki 知识库 + IM 多渠道分发。中国 matecloud 社区出品，纯工程驱动、无论文背书。
> **本地**：`repos/mateclaw`（matevip/mateclaw）｜**深读**：deepwiki 47 子页归档 `deepwiki/mateclaw/full.md`（2026-08-21）

## 一、组件栈（DeepWiki 蒸馏）

| 层 | 职责 | 关键实体 |
|---|---|---|
| Agent 运行时 | StateGraph 图编排，ReAct/Plan-Execute 双模式 | `AgentGraphBuilder`、`StateGraphReActAgent`、`ReasoningNode/ActionNode/ObservationNode`、`MateClawStateKeys` |
| LLM Provider | 14+ 提供商接入、健康追踪、故障转移 | `ModelProviderService`、`ProviderHealthTracker`、`AgentClaudeCodeChatModelBuilder`、`DeepSeekV4ThinkingDecorator` |
| 记忆 | 回忆打分、做梦固化、事实抽取 | `MemoryLifecycleMediator`、`MemoryRecallService`、`MemoryEmergenceService`、`ContradictionDetector` |
| 知识库 | Wiki 摄取管线、混合检索、引用溯源 | `WikiProcessingService`、`HybridRetriever`、`WikiModelRoutingService` |
| 工具/技能 | 内置工具、SKILL.md 打包、MCP 接入 | `ToolRegistry`、`ToolExecutionExecutor`、`SkillRuntimeService`、`McpToolCallbackProvider` |
| 安全 | ToolGuard 评估、HiL 审批、RBAC、路径沙盒 | `DefaultToolGuard`、`ApprovalService`、`WorkspacePathGuard`、`ShellCommandGuardian` |
| 渠道分发 | Web 控制台/WebChat 部件/IM 适配器 | `ChannelManager`、`WeixinChannelAdapter`、`FeishuChannelAdapter`、`TalkModeWebSocketHandler` |
| 前端 | Vue3 SPA、SSE 流式渲染、晨报卡 | `useChat`、`ChatConsole.vue`、`MorningCard.vue`、`useMemoryStore` |

## 二、核心机制

1. **StateGraph 双模式 Agent**（来源：StateGraph & Agent Patterns）：基于 `spring-ai-alibaba-graph-core` 把 ReAct 编译为有向图——Reasoning→ReasoningDispatcher→Action→Observation 循环，边（Dispatcher）承载全部路由逻辑；Plan-Execute 先分诊（直答/单步/2–6 步序列），每步内嵌 ReAct 且限 5 次工具调用防失控。创新点本质：LangGraph 式图抽象的 Java 强类型实现（typed State Accessor + 集中 StateKeys）。
2. **做梦式记忆固化（Dreaming）**（来源：Memory Lifecycle & Dreaming）：记忆写入不等于持久——先落 daily notes，每轮记录"回忆事件"（频率/查询多样性/时间衰减三维打分，精确到 `##` 小节级），夜间 cron（默认凌晨 3 点）由 `MemoryEmergenceService` 驱动 LLM 把通过门槛的高频候选固化为 `MEMORY.md`/`SOUL.md`，`ContradictionDetector` 检测新旧冲突，带 `<!-- user-edited -->` 标记的用户手改区永不覆盖只追加。创新点本质：记忆晋升靠使用统计"涌现"，而非全量入库，且内置 HIL 保护。
3. **多 Provider 健康追踪与故障转移**（来源：Provider Management & Failover；Overview）：`ProviderHealthTracker` 持续分类探测 401/超时/配额耗尽并冷却劣化节点，请求沿用户优先级链路由到下一健康 Provider；甚至能以 Claude Code OAuth 身份伪装（`ClaudeCodeIdentityChatModelDecorator`）接入官方 Claude 订阅，Ollama 本地模型自动发现。创新点本质：把"模型不可用"当一等公民设计，国产与海外模型统一为可切换资源池。
4. **观察预算三层防线**（来源：StateGraph & Agent Patterns；Configuration Reference）：工具结果 8K 硬截断 → 16K 溢写磁盘（Spill Store，RFC-008）→ 单轮 32K 聚合预算，超限路由至 `SummarizingNode` 结构化压缩；外加 `RepetitionDetector` 检测同参重复调用、100 次迭代硬顶。创新点本质：上下文工程做成分层可配置预算，而非一刀切截断。

## 三、与讲透系列的对位

| mateclaw 概念 | 讲透系列对应概念 |
|---|---|
| Reasoning→Action→Observation 图循环 | 讲透Agent：ReAct 循环（思考-行动-观察） |
| 三层观察预算 + SummarizingNode 压缩 | 讲透Agent：上下文工程（压缩/预算/溢写） |
| Dreaming 固化 + recall 三维打分 + 矛盾检测 | 讲透学习型Agent：记忆机制（巩固/遗忘/涌现） |
| DelegateAgentTool 父子会话 + 递归控制 | 讲透多Agent协作：委派模式（orchestrator-worker） |
| DefaultToolGuard + ApprovalService + WorkspacePathGuard | 讲透Agent：安全沙盒与 Human-in-the-Loop 审批 |

## 四、关键入口

```java
mateclaw-server/src/main/java/vip/mate/agent/AgentGraphBuilder.java                  // 图装配工厂：解析模型配置+工具绑定，编译 StateGraph
mateclaw-server/src/main/java/vip/mate/agent/graph/StateGraphReActAgent.java        // ReAct 图模式：Thought→Action→Observation 循环主体
mateclaw-server/src/main/java/vip/mate/agent/graph/executor/ToolExecutionExecutor.java // 工具两阶段执行：守卫评估+并发控制+观察预算截断
mateclaw-server/src/main/java/vip/mate/memory/service/MemoryEmergenceService.java   // 做梦固化：召回打分→LLM 合并→冲突检测→MEMORY.md
mateclaw-server/src/main/java/vip/mate/llm/failover/ProviderHealthTracker.java      // Provider 健康追踪：错误分类+冷却+优先级故障转移
mateclaw-server/src/main/java/vip/mate/wiki/service/HybridRetriever.java            // Wiki 混合检索（向量+关键词），Agent 引用溯源入口
```

## 五、深读子页地图（47 页精选 6）

1. **StateGraph & Agent Patterns**（#5）——图模式+状态键+安全限流全解，信息密度最高的一页
2. **Memory Lifecycle & Dreaming**（#21）——做梦固化完整工作流与回忆打分算法
3. **Provider Management & Failover**（#10）——健康探测/冷却/Ollama 自动发现的容灾设计
4. **Tool Guard & Audit**（#35）——守卫决策矩阵+Shell 命令模式匹配+审计流水
5. **Chat Console & Streaming Client**（#14）——前端 useChat/useStream 的 SSE 解析与本地/远端消息对账
6. **Conversation & History Management**（#8）——RFC-052 上下文压缩管线与 Agent 间委派

## 六、与"我们"的关系（一句话）

对学 Agent 的人，这个仓库的独特价值是：用 Java 企业技术栈（Spring AI Alibaba）从零完整实现了一套 Claude Code 式个人 Agent——图编排、工具守卫、SKILL.md、记忆做梦、多 Provider 容灾全都有工程级实现，是"Python 之外 Agent 如何工程化"与国产大模型适配的最佳对照样本。

---
生成：2026-08-21 · deepwiki 47 页全归档
