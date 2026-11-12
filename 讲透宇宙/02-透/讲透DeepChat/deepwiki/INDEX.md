# DeepChat DeepWiki 全量文档索引

> 仓库：[ThinkInAIXYZ/DeepChat](https://github.com/thinkinaixyz/deepchat)（本地 `/usr-data/data1/browser/deepchat`，v1.1.3-beta.6）
> 来源：DeepWiki（deepwiki.com/ThinkInAIXYZ/DeepChat）Wayback 快照，2026-10-08 抓取
> 世代：主体 50 页为 2025-10 ~ 2026-04 快照（以 2026-03-06 导航世代为锚）；6 页（标 ★）从 2026-04-11 快照的 RSC payload 提取
> 文件名规则：`thinkinaixyz_deepchat_{slug}.md`

## 目录（9 章 56 页）

### 1. DeepChat 概览
- [1 DeepChat Overview](thinkinaixyz_deepchat_1-deepchat-overview.md) — 项目定位/技术栈/入口
- [1.1 Installation and Setup](thinkinaixyz_deepchat_1.1-installation-and-setup.md) — 安装与配置
- [1.2 Application Architecture Overview](thinkinaixyz_deepchat_1.2-application-architecture-overview.md) — 应用架构总览

### 2. 核心架构
- [2 Core Architecture](thinkinaixyz_deepchat_2-core-architecture.md) — 章总览
- [2.1 Presenter Pattern and IPC](thinkinaixyz_deepchat_2.1-presenter-pattern-and-ipc-communication.md) — Presenter 模式与 IPC 通信（主↔渲染进程核心解耦层）
- [2.2 Event System Architecture](thinkinaixyz_deepchat_2.2-event-system-architecture.md) — EventBus 事件驱动架构
- [2.3 Window and Tab Management](thinkinaixyz_deepchat_2.3-window-and-tab-management.md) — 窗口与 Tab 管理（WindowPresenter/TabPresenter）
- [2.4 State Management with Pinia](thinkinaixyz_deepchat_2.4-state-management-with-pinia.md) — Pinia 状态管理

### 3. 配置与设置系统
- [3 Configuration and Settings System](thinkinaixyz_deepchat_3-configuration-and-settings-system.md)
- [3.1 ConfigPresenter and Helper Architecture](thinkinaixyz_deepchat_3.1-configpresenter-and-helper-architecture.md) — ConfigPresenter 架构
- [3.2 Provider and Model Database](thinkinaixyz_deepchat_3.2-provider-and-model-database.md) — Provider/模型数据库（SQLite）
- [3.3 Model Configuration and Capabilities](thinkinaixyz_deepchat_3.3-model-configuration-and-capabilities.md) — 模型配置与能力位
- [3.4 Settings User Interface](thinkinaixyz_deepchat_3.4-settings-user-interface.md) — 设置界面
- [3.5 Internationalization System](thinkinaixyz_deepchat_3.5-internationalization-system.md) — 国际化
- [3.6 Data Migration and Versioning](thinkinaixyz_deepchat_3.6-data-migration-and-versioning.md) — 配置迁移与版本管理

### 4. MCP 系统
- [4 Model Context Protocol (MCP) System](thinkinaixyz_deepchat_4-model-context-protocol-(mcp)-system.md)
- [4.1 MCP System Architecture](thinkinaixyz_deepchat_4.1-mcp-system-architecture.md) — MCP 总体架构
- [4.2 MCP Client and Transport Layer](thinkinaixyz_deepchat_4.2-mcp-client-and-transport-layer.md) — 客户端与传输层（stdio/SSE/HTTP）
- [4.3 Server Lifecycle and Tool Management](thinkinaixyz_deepchat_4.3-server-lifecycle-and-tool-management.md) — 服务器生命周期与工具发现
- [4.4 Tool Execution and Permission System](thinkinaixyz_deepchat_4.4-tool-execution-and-permission-system.md) — 工具执行与权限系统
- [4.5 MCP Sampling System](thinkinaixyz_deepchat_4.5-mcp-sampling-system.md) ★ — Sampling 请求与 LLM 委托（原 6.6 节，2026-02 快照）
- [4.6 Built-in MCP Servers](thinkinaixyz_deepchat_4.6-built-in-mcp-servers.md) ★ — 内置 MCP 服务（原 6.7 节，2026-02 快照）
- [4.7 MCP Configuration Management](thinkinaixyz_deepchat_4.7-mcp-configuration-management.md) — MCP 配置管理
- [4.8 MCP Configuration UI](thinkinaixyz_deepchat_4.8-mcp-configuration-ui.md) — MCP 配置界面

### 5. LLM Provider 集成
- [5 LLM Provider Integration](thinkinaixyz_deepchat_5-llm-provider-integration.md)
- [5.1 Provider Architecture and Base Classes](thinkinaixyz_deepchat_5.1-provider-architecture-and-base-classes.md) — Provider 抽象与类层级
- [5.2 Provider Implementations](thinkinaixyz_deepchat_5.2-provider-implementations.md) — 各厂商 Provider 实现
- [5.3 Streaming and Agent Loop](thinkinaixyz_deepchat_5.3-streaming-and-agent-loop.md) — 流处理与 Agent 循环
- [5.4 Message Format Translation](thinkinaixyz_deepchat_5.4-message-format-translation.md) — 消息格式转换（内部块↔各家 API）
- [5.5 Rate Limiting and Model Fetching](thinkinaixyz_deepchat_5.5-rate-limiting-and-model-fetching.md) — 限流与模型拉取
- [5.6 Function Call Tag Parsing](thinkinaixyz_deepchat_5.6-function-call-tag-parsing.md) — 函数调用标签解析

### 6. 聊天与会话系统
- [6 Chat and Conversation System](thinkinaixyz_deepchat_6-chat-and-conversation-system.md)
- [6.1 Thread and Message Management](thinkinaixyz_deepchat_6.1-thread-and-message-management.md) — 线程与消息管理
- [6.2 Message Generation and Streaming Flow](thinkinaixyz_deepchat_6.2-message-generation-and-streaming-flow.md) — 消息生成与流式管线
- [6.3 Message Variant System](thinkinaixyz_deepchat_6.3-message-variant-system.md) — 消息变体（编辑/重新生成分叉）
- [6.4 Chat UI Components](thinkinaixyz_deepchat_6.4-chat-ui-components.md) — 聊天 UI 组件
- [6.5 Message Caching and Virtual Scrolling](thinkinaixyz_deepchat_6.5-message-caching-and-virtual-scrolling.md) — 消息缓存与虚拟滚动
- [6.6 Thread Creation and Model Selection](thinkinaixyz_deepchat_6.6-thread-creation-and-model-selection.md) — 线程创建与模型选择
- [6.7 Child Conversations and Forking](thinkinaixyz_deepchat_6.7-child-conversations-and-forking.md) — 子会话与分叉

### 7. 文件处理系统
- [7 File Processing System](thinkinaixyz_deepchat_7-file-processing-system.md)
- [7.1 File Processing Architecture](thinkinaixyz_deepchat_7.1-file-processing-architecture.md) — 文件处理架构（BaseFileAdapter）
- [7.2 File Adapters and Content Extraction](thinkinaixyz_deepchat_7.2-file-adapters-and-content-extraction.md) — 文件适配器与内容提取
- [7.3 Mention System and Prompt Parameters](thinkinaixyz_deepchat_7.3-mention-system-and-prompt-parameters.md) — @提及系统与提示参数注入

### 8. 知识库与 RAG 系统
- [8 Knowledge Base and RAG System](thinkinaixyz_deepchat_8-knowledge-base-and-rag-system.md)
- [8.1 Knowledge Base Architecture](thinkinaixyz_deepchat_8.1-knowledge-base-architecture.md) — 知识库架构
- [8.2 File Processing Pipeline](thinkinaixyz_deepchat_8.2-file-processing-pipeline.md) ★ — 入库文件处理管线（RSC 提取）
- [8.3 Vector Database and DuckDB](thinkinaixyz_deepchat_8.3-vector-database-and-duckdb.md) ★ — DuckDB 向量库（RSC 提取）
- [8.4 Task Queue and Concurrency](thinkinaixyz_deepchat_8.4-task-queue-and-concurrency.md) ★ — 任务调度与并发（RSC 提取）
- [8.5 Similarity Search and Querying](thinkinaixyz_deepchat_8.5-similarity-search-and-querying.md) ★ — 相似度检索（RSC 提取）

### 9. 高级特性
- [9 Advanced Features](thinkinaixyz_deepchat_9-advanced-features.md)
- [9.1 Deeplink Protocol](thinkinaixyz_deepchat_9.1-deeplink-protocol.md) ★ — Deep Link 与外部集成（RSC 提取）
- [9.2 Multi-Window Tab Operations](thinkinaixyz_deepchat_9.2-multi-window-tab-operations.md) — 多窗口 Tab 拖拽
- [9.3 Data Management and Backup](thinkinaixyz_deepchat_9.3-data-management-and-backup.md) — 数据管理与备份
- [9.4 Proxy Configuration System](thinkinaixyz_deepchat_9.4-proxy-configuration-system.md) — 代理配置系统
- [9.5 Agent Client Protocol (ACP) Integration](thinkinaixyz_deepchat_9.5-agent-client-protocol-(acp)-integration.md) — ACP 集成（原 8.5 节，2026-03 快照）
- [9.6 Artifact Rendering System](thinkinaixyz_deepchat_9.6-artifact-rendering-system.md) ★ — Artifact/Markdown 渲染（RSC 提取，含 artifactStore/Mermaid）

## 抓取说明

| 项 | 值 |
|---|---|
| 抓取日期 | 2026-10-08 |
| 通道 | Wayback Machine 快照（deepwiki.com 被 Vercel Security Checkpoint 拦截，直连/代理/jina 全断） |
| 工具 | `pipeline-bin/deepwiki/dw_fetch_wayback.py`（curl 子进程模式） |
| 世代锚定 | 2026-03-06 导航（56 页集合），避免多代目录混抓 |
| 快照时间跨度 | 2025-10-08 ~ 2026-04-11（对应 DeepChat v1.0.x ~ v1.1.x 早期） |
| 已知局限 | ①本地仓已到 v1.1.3-beta.6，快照内容略滞后；②overview 主页仅有 2025-09 老世代快照，未收录，由 1-deepchat-overview 代替；③★ 页从同代 RSC payload 提取，格式为 DeepWiki 原始 markdown，个别 `<details>` HTML 标签保留原样 |
