# ix 深读卡 —— 把 Agent 工作流存成数据库图、再编译成 LangChain 执行的可视化多 Agent 平台

> **定位**：ix 是 2023 年初开源的自主 Agent 设计/部署平台：用 React 图编辑器拖拽节点编排工作流（Chain），后端 Django/FastAPI + Celery 把图编译成 LangChain LCEL Runnable 执行。差异化在于"图存 PostgreSQL、加载时三阶段编译 + ChatModerator 多 Agent 委派"这条完整链路；无论文背书，属"可视化编排 LangChain"一代（LangFlow/Flowise 同期）的早期开源探索标本。
> **本地**：`repos/ix`（kreneskyp/ix）｜**深读**：deepwiki 20 子页归档 `deepwiki/ix/full.md`（2026-08-21）

## 一、组件栈（DeepWiki 蒸馏）

| 层 | 职责 | 关键实体 |
|---|---|---|
| 前端 React | 可视化编排 + 聊天 | `ChainGraphEditor`、`ChatView`、`useChatGraph` |
| API 层 | REST + GraphQL | FastAPI routers（chains/chats/agents/editor/secrets…）、`ix.schema` 订阅 |
| 图数据模型 | 工作流持久化 | `Chain`/`ChainNode`/`ChainEdge`/`NodeType`（Django + PostgreSQL） |
| 编译加载层 | 图 → LCEL | `load_chain_flow`、`FlowPlaceholder`、`IxNode`、`IxContext` |
| Agent 运行时 | 异步执行 | `AgentProcess`、`start_agent_loop`（Celery Singleton）、`IxHandler` |
| 多 Agent 协调 | 路由与委派 | `ChatModerator`、Task 父子层级（`delegate_to_agent`） |
| 组件生态 | LangChain 复用 | NodeType fixtures 注册表 + JSON Schema 动态表单、memory/tools/llm 专用 loader |
| 基础设施 | 存储/消息/密钥 | PostgreSQL、Redis、Celery、HashiCorp Vault |

## 二、核心机制

1. **图 → LCEL 三阶段编译**（Chain System）：Chain/ChainNode/ChainEdge 存数据库；`load_chain_flow()` 先遍历图建 **FlowPlaceholder**（Sequence/Map/Branch/ImplicitJoin/Agg 五种模式），再 `init_flow_node()` 编译成 `RunnableSequence/Parallel/Branch`，每个组件包 `IxNode` 注入上下文与日志——"可视化图即 LangChain 代码"的编译器内核，是同类编辑器的通用套路源头。
2. **双边型边（LINK/PROP）**（Chain System）：ChainEdge 区分 `LINK`（数据流/执行序）与 `PROP`（把一个节点作为另一节点的属性注入，含 secret 自动从 Vault 解析）——用一种边模型同时表达控制流与组件组合，图编排里少见的简洁设计。
3. **ChatModerator 多 Agent 路由 + 任务树**（Agent Execution System）：一个聊天里多个 Agent，LLM 选择目标 Agent → `delegate_to_agent()` 创建父子层级 Task（`root_id`/`parent_id`）→ Celery `start_agent_loop`（Singleton 防重）异步执行——moderator/supervisor 模式 + 层级委派的早期完整实现。
4. **全链路可观测**（Agent Execution System）：`IxHandler` 实现 LangChain callback 接口，六类 `TaskLogMessage`（THINK/ASSISTANT/THOUGHT/FEEDBACK/EXECUTE_ERROR/ARTIFACT）全落库，token 级流式经 GraphQL/WebSocket 订阅直达前端——执行历史即数据库记录。

## 三、与讲透系列的对位

| ix 概念 | 讲透Agent / 讲透多Agent协作 对应概念 |
|---|---|
| Chain 图 + FlowPlaceholder 编译 | 编排模式：DAG/图执行与拓扑编译 |
| IxNode 包裹 Runnable 执行 | ReAct 循环 / 工具调用执行单元 |
| ChatModerator 路由 + Task 委派 | 多 Agent 协作的 moderator/supervisor 模式 |
| TaskLogMessage 六类消息持久化 | 记忆机制 / 上下文工程（执行历史） |
| NodeType fixture + JSON Schema 动态表单 | 上下文工程：组件配置层 |
| Vault secret 字段注入 | 安全沙盒：密钥管理 |

## 四、关键入口

```
repos/ix/
├── ix/chains/models.py                  # Chain/ChainNode/ChainEdge/NodeType 四模型，图即数据库
├── ix/chains/loaders/core.py            # 三阶段编译：load_chain_flow→Placeholder→init_flow_node 产出 LCEL
├── ix/agents/process.py                 # AgentProcess：load_chain + chat_with_ai + ainvoke 主循环
├── ix/chains/callbacks.py               # IxHandler：LangChain callback→消息落库+token 流式
├── ix/chains/moderator.py               # ChatModerator：LLM 选 agent 并 delegate
├── ix/task_log/models.py                # Task 父子层级 + 六类 TaskLogMessage + delegate_to_agent
├── ix/task_log/tasks/agent_runner.py    # Celery Singleton 任务 start_agent_loop 入口
└── frontend/chains/ChainGraphEditor.js  # 可视化拖拽图编辑器（React）
```

## 五、深读子页地图（20 页精选 6）

1. **Chain System（3.1）**——图→LCEL 编译全流程，全仓库最核心的一页
2. **Agent Execution System（3.2）**——执行生命周期、moderator 委派、流式回调
3. **Chain Graph Editor（5.1，20KB 最大页）**——节点/边/拖拽/自动连线的编辑器实现
4. **GraphQL API（4.3）**——Task 查询与实时 subscription 的通信底座
5. **LLM Configuration（6.1）**——多 provider 配置 + Vault secret 流程
6. **Deployment（7.2）**——Docker Compose 多服务 + CI/CD + Vault 的平台工程全套

## 六、与"我们"的关系（一句话）

想真正看懂 LangFlow/Flowise 这一代可视化 Agent 编排器的"编译器内核"（图怎么变成可执行 LangChain 代码）加上 2023 年最早的多 Agent moderator 委派实现，ix 是代码量适中、链路最完整的早期标本。

---
生成：2026-08-21 · deepwiki 20 页全归档
