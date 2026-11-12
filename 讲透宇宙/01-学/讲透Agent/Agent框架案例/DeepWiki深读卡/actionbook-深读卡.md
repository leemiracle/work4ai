# actionbook 深读卡 —— 给 AI Agent 用的"网站操作手册"离线工厂：爬一次，用千次

> **定位**：Actionbook 是一个为 AI agent 预构建、验证并分发网站"动作手册"（action manual）的平台——把昂贵的 DOM 探索（AI 驱动的浏览器自动化 + 多轮 LLM 循环）离线做一次，沉淀为带置信度的多路 selector，之后所有 agent 查询即得（号称 10x 执行提速、100x token 节省）。核心差异化在于**发现与执行分离** + PostgreSQL 双存储（DB 供混合检索、YAML 供人读/版本控制）+ Blue-Green 版本发布，且查询侧完全框架无关（CLI/MCP/SDK 三入口，OpenAI/Anthropic/Bedrock 通吃）。
> **本地**：`repos/actionbook`（actionbook/actionbook）｜**深读**：deepwiki 40 子页归档 `deepwiki/actionbook/full.md`（2026-08-21，817K 字符；注意：本地 HEAD 仅含 `packages/`，wiki 快照中的 `services/`、`apps/` 本地未检出）

## 一、组件栈（DeepWiki 蒸馏）

| 层 | 职责 | 关键实体 |
|---|---|---|
| L1 用户接口 | Agent/开发者查询动作手册 | `@actionbookdev/cli`、`@actionbookdev/mcp`（`search_actions`/`get_action_by_id`）、`@actionbookdev/sdk` |
| L2 API 层 | REST 检索 + 混合搜索 | `/actions/search`、`/actions/:id`；全文 GIN + pgvector HNSW + RRF 融合 |
| L3 核心服务 | 离线构建管线 | `ActionBuilder`（录制）、`PlaybookBuilder`（文档）、`KnowledgeBuilder`（爬取+embedding） |
| L4 任务编排 | 并发调度与容错 | `Coordinator` → `BuildTaskRunner` → `RecordingTaskQueueWorker`（DB 状态机） |
| L5 浏览器自动化 | 统一浏览器抽象 | `BrowserAdapter` 接口；`StagehandBrowser`（本地 Playwright）/`AgentCoreBrowser`（AWS 云）；`BrowserProfileManager`（登录态复用） |
| L6 数据层 | 持久化 + 向量检索 + 人读输出 | `sources/pages/elements/chunks/build_tasks/recording_tasks` 表；`output/sites/` YAML |

领域模型：`Source → SourceVersion(Blue-Green) → Page → Element → Selectors`；ActionId 格式 `site/{domain}/page/{pageType}/element/{semanticId}`。

## 二、核心机制

1. **发现/执行分离（"crawl once, use many times"）**：构建管线用 AI 浏览器自动化一次性发现并验证 selector，存入 DB+YAML；运行时 agent 只查询不解析，手册可独立于 agent 代码更新，从根上治 selector 脆弱性与 LLM 幻觉。〔Overview〕
2. **ActionRecorder 多轮 LLM 循环**：max 30 轮 tool-calling 循环（`navigate/observe_page/register_element/interact/set_page_context/scroll/wait/go_back`），`observe_page` 借 Stagehand AI 视觉发现元素，`register_element` 自动抽取 7 级优先级 selector（id 0.95 → placeholder 0.65）并检测动态日期模板化为 `{{date}}`；6 重终止条件（超时/token/元素阈值 80/观察效率<3/页面数 5/轮数 30）+ 部分结果兜底保存。〔Action Recording〕
3. **三层生产者-消费者编排，数据库即状态机**：`Coordinator` 认领 build_task（默认并发 5）→ `BuildTaskRunner` 幂等 UPSERT 生成 50-100+ recording_task → 全局 `QueueWorker` 以 `FOR UPDATE SKIP LOCKED` 原子认领（浏览器并发 3）；5s 心跳 + 15min 陈旧检测 + max 3 重试 + 永久失败不阻塞完成，实现无状态崩溃恢复。〔Task Execution Pipeline〕
4. **SelectorOptimizer LLM 稳定性分析**：录制结束后单次 LLM 批量分析全部 selector，剔除动态计数器/哈希/UUID/时间戳/会话 ID，按稳定度重排并调整置信度后再落盘。〔Action Recording〕

## 三、与讲透系列的对位

| 该框架概念 | 讲透Agent / 讲透多Agent协作 对应概念 |
|---|---|
| ActionRecorder 30 轮 tool-calling 循环（observe→register→observe） | ReAct 循环（Thought→Action→Observation），含循环终止条件设计 |
| 录制器内存态 `siteCapability`/`discoveredElements`/`visitedUrls` | Agent 短期记忆/工作记忆（scratchpad + 去重集合） |
| Coordinator→BuildTaskRunner→QueueWorker 分层队列 | 多 Agent 编排模式：分层编排 + 生产者-消费者任务队列 |
| DB 状态机 + 心跳 + 陈旧恢复 + 重试上限 | 多 Agent 协作的容错：状态持久化、崩溃恢复、优雅降级 |
| Action 手册（YAML/DB 资产，Blue-Green 版本化） | 记忆机制外化：把昂贵探索固化为可复用的程序性记忆/技能库 |
| `navigate` 的外域/已访问拦截、headless 沙盒、BrowserProfile 隔离 | 安全沙盒与环境约束（动作域白名单） |
| MCP Server 暴露 `search_actions` 工具 | MCP 协议工具服务（与讲透Agent 工具调用章直接互证） |

## 四、关键入口

```text
repos/actionbook
├── packages/mcp/src/tools/search-actions.ts      # MCP 工具入口：search_actions（本地已核实）
├── packages/js-sdk/src/client.ts                 # SDK 客户端 + tool-defs（本地已核实）
├── packages/tools-ai-sdk/src/tools/              # Vercel AI SDK 工具集成（本地已核实）
├── services/action-builder/src/recorder/ActionRecorder.ts        # 核心：多轮 LLM 录制循环（仅 wiki 快照）
├── services/action-builder/src/recorder/RecorderToolExecutor.ts  # 工具分发到 BrowserAdapter（仅 wiki 快照）
├── services/action-builder/src/task-worker/coordinator.ts        # 顶层编排器 + SKIP LOCKED 认领（仅 wiki 快照）
├── services/action-builder/src/optimizer/SelectorOptimizer.ts    # LLM selector 稳定性优化（仅 wiki 快照）
└── apps/api-service/                             # Express REST + 混合搜索（仅 wiki 快照）
```

## 五、深读子页地图（40 页精选 6）

1. Overview（L6）—— 六层架构 + 领域模型全景，先读
2. ★ Action Recording / 3.2.2（L7574）—— **最值得读**：教科书级 ReAct 式浏览器 Agent 循环（工具集/重试/终止/部分结果/token 统计全齐）
3. ★ Task Execution Pipeline / 3.2.1（L6766）—— **最值得读**：DB 状态机 + SKIP LOCKED + 心跳恢复的多 Agent 编排范本
4. Recording Tools Reference / 3.2.3（L8234）—— 录制工具参数级文档，配 3.2.2 读
5. Search and Indexing / 5.3（L16164）—— 全文+向量+RRF 混合检索实现
6. AI and LLM Integration / 6（L16571）—— AIClient 多供应商抽象与 Selector Optimizer

## 六、与"我们"的关系（一句话）

对学 Agent 的人，这个仓库是"把 ReAct 浏览器 Agent 的探索成果工业化沉淀为可复用技能库"的最佳全栈样本——单 Agent 循环（Action Recording）与多 Agent 容错编排（Task Execution Pipeline）两页恰好覆盖讲透Agent→讲透多Agent协作的完整知识链。

---
生成：2026-08-21 · deepwiki 40 页全归档
