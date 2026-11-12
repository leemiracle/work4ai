# openhands 深读卡 —— 开源自主软件工程 Agent 平台标杆：CodeAct 统一动作空间 + 沙盒内 Action Server 执行 + 事件驱动会话，正完成 V0 单体 → V1「SDK 化 + 云原生」大迁移

> **定位**：OpenHands（原 OpenDevin）是 All-Hands-AI 开源的自主软件工程 Agent 平台，以 CodeAct 范式（bash/Python/浏览器/文件操作统一为一个代码动作空间）+ 隔离沙盒执行 + React Web UI 起家，产品线覆盖 SDK、CLI、Local GUI、Cloud、Enterprise 五形态。架构上正从 V0（FastAPI+Socket.IO 单体、AgentController+EventStream、文件存储，2026-04-01 已移除）迁移到 V1（`app_server` 服务化 + 外部 `openhands-sdk` + 沙盒内 agent-server 镜像 + PostgreSQL）。
> **本地**：`repos/openhands`（All-Hands-AI/OpenHands）｜**深读**：deepwiki 88 子页归档 `deepwiki/openhands/full.md`（2026-08-21）

## 一、组件栈（DeepWiki 蒸馏）

| 层 | 职责 | 关键实体 |
|---|---|---|
| Presentation | 用户入口：Web GUI / CLI / i18n | React 19 + Vite 7 + Zustand + TanStack Query + Socket.IO（`frontend/`）、`openhands-cli`、`@openhands/ui` |
| Application Server | 会话生命周期、鉴权、设置、WebSocket/REST | V1：`openhands/app_server/`（`AppConversationService`、`LiveStatusAppConversationService`、`SQLAppConversationInfoService`）；V0：`openhands/server/`（已废弃） |
| Agent Execution | 推理循环、动作决策、状态机 | V1：`openhands-sdk` + `openhands-agent-server`（跑在沙盒内）；V0：`AgentController` + `CodeActAgent`（仅存于文档） |
| Runtime Execution | 隔离沙盒与动作落地 | `SandboxService` → Docker/Remote/Process 三实现；沙盒内 `ActionExecutionServer`（FastAPI :60000）+ `ActionExecutor` → `BashSession`(tmux)/`OHEditor`(openhands-aci)/`JupyterKernel`/`BrowserEnv`(Playwright)/`MCPProxyManager` |
| Infrastructure | 存储、LLM、外部集成 | `FileStore`(V0)/PostgreSQL(V1)、litellm 多 Provider、Git Providers（GitHub/GitLab/Azure）、MCP、Skills 体系 |

## 二、核心机制

1. **事件驱动 Agent 回路 + 双熔断状态机**（来源：6.1 Agent Controller / 6.2 Event-Driven Architecture / 6.4 CodeActAgent）。一切皆事件：`Action`（`CmdRunAction`/`FileEditAction`/`IPythonRunCellAction`/`BrowseURLAction`）与 `Observation` 成对流经 `EventStream` 中央总线（pub/sub + 自动 secret 脱敏 + 持久化，`EventSource` ∈ {USER, AGENT, ENVIRONMENT}）。`AgentController._step()` 十步循环：状态检查 → pending action → 控制限额 → delegate 转发 → `StuckDetector` 重复检测 → `agent.step(state)` 生成动作 → 安全分析 → 确认拦截（可转 `AWAITING_USER_CONFIRMATION`）→ 入流执行 → 等 Observation。`iteration_flag`（超限抛 `AgentStuckInLoopError`）与 `budget_flag`（超支抛 `RuntimeError`）构成双重熔断；状态机 `LOADING→RUNNING→AWAITING_USER_CONFIRMATION→FINISHED/ERROR/STOPPED`，每次迁移发 `AgentStateChangedObservation` 并落盘。
2. **沙盒即服务（Sandbox-as-a-Service）**（来源：4.1 Runtime Abstractions / 4.2 Action Execution Server / 3.2 Sandbox Specification Service）。`SandboxService` ABC 统一三种后端：`DockerSandboxService`（docker-py、动态端口映射）、`RemoteSandboxService`（httpx + `X-API-Key`，SHA-256 哈希后入库的 `StoredRemoteSandbox`）、`ProcessSandboxService`（subprocess.Popen + psutil，仅目录级隔离）。沙盒状态机 `STARTING/RUNNING/PAUSED/MISSING/ERROR`；宿主注入 `OH_SESSION_API_KEYS_0`（鉴权）、`OH_WEBHOOKS_0_BASE_URL`（事件回调）、`OH_ALLOW_CORS_ORIGINS_0`，靠轮询沙盒内 `/alive` 判就绪；固定暴露 `AGENT_SERVER`:60000 / `VSCODE`:60001 / `WORKER`:12000-12001；动作经 `POST /execute_action` 下发，结果经 `/webhooks/on_conversation_update` 回推触发 `EventCallbackProcessor`（自动起标题、Slack/GitHub 摘要、终态埋点）。
3. **V0 → V1 架构大迁移**（来源：1.2 V0/V1 Migration Path / 7.4 V1 Conversation Architecture）。V0=单体（Socket.IO + `AgentController` + `EventStream` + `FileStore`），V1=服务化（`app_server` 编排 + 外部 `openhands-sdk` 承载 Agent 核心 + 沙盒内 `ghcr.io/openhands/agent-server:1.28.0-python` 镜像 + `conversation_metadata` SQL 表）；术语硬切换：`AgentController`→`Agent`(SDK)、`Microagents`→`Skills`、`FileStore`→SQL DB；数据库 `conversation_version` 字段双轨共存，`LLM_`/`LMNR_` 前缀环境变量自动转发进沙盒。
4. **Condenser 记忆压缩 + 多源 Skill 合并 + 父子会话委派**（来源：6.5 Memory and Context Condensation / 6.3 Agent Delegation）。长会话用三策略压缩：`LLMSummarizingCondenser`（副 LLM 摘要遗忘事件）、`AmortizedForgettingCondenser`（渐进丢弃）、`RecentEventsCondenser`（滑窗保留）；Skill 从 public→user→org→project 四源加载，后者同名覆盖前者，经沙盒内 `/api/skills` 聚合注入 `AgentContext`；委派=父会话（DEFAULT）spawn 子会话（如 PLAN），Planning Agent 备料、Code Agent 执行，共享同一沙盒工作区（`get_project_dir` 处理克隆仓库路径）。

## 三、与讲透系列的对位

| OpenHands 机制 | 讲透系列主题（work4ai/agent-development 等） | 差异洞察 |
|---|---|---|
| `EventStream` Action/Observation 对 + `_step()` 循环 | ReAct / 工具调用 / Agent loop | CodeAct 比 tool-call 更激进：一切动作=可执行代码，工具即语言 |
| Condenser 三策略 | 记忆机制 / 上下文管理 | 工业级实现把"记忆压缩"做成可插拔策略类，而非单一 trick |
| Delegation 父子会话 | 多智能体协作（swarm/crew） | 不是消息传递型 multi-agent，而是"同沙盒内子会话"——省去环境同步 |
| `SandboxService` 三实现 + ActionExecutionServer | MCP / 工具执行环境 | 沙盒=独立进程/容器内跑 FastAPI 执行器，安全边界靠隔离而非提示词 |
| `mcp/` + MCPProxyManager | MCP 协议 | MCP 服务跑在沙盒内经 proxy 暴露，与外部 MCP client 模式互补 |
| litellm 层 + verified models + LLM proxy | LLM API / 讲透LLM 系列 | 多 Provider 归一 + "验证过的模型"白名单 + 可选自建代理，SaaS 化三件套 |

## 四、关键入口

```
repos/openhands/
├── openhands/app_server/              # V1 应用服务器（本地唯一主体，V0 目录已删）
│   ├── app.py                         # FastAPI 组装入口
│   ├── app_conversation/              # 会话生命周期
│   │   ├── app_conversation_service.py + live_status_app_conversation_service.py
│   │   └── skill_loader.py            # 四源 Skill 聚合 → AgentContext 注入
│   ├── sandbox/                       # 沙盒抽象核心
│   │   ├── sandbox_service.py         # ABC：start/pause/delete/wait_for_sandbox_running(/alive)
│   │   ├── docker_sandbox_service.py / remote_sandbox_service.py / process_sandbox_service.py
│   │   └── sandbox_spec_service.py    # SandboxSpec：镜像/启动命令/env 注入
│   ├── event/ + event_callback/       # 事件存储(FS/GCS) + webhook 回调处理器
│   └── mcp/ git/ secrets/ settings/   # MCP、Git provider、密钥、设置
├── frontend/                          # React 19 + Vite 7 + Zustand SPA
├── enterprise/                        # Keycloak、LiteLLM 预算、计费、Slack/Jira/Linear
├── openhands-ui/                      # @openhands/ui 组件库
├── Makefile + containers/ + kind/     # make build && make run
# 注意：Agent 推理核心不在本仓运行——在外部包 openhands-sdk +
#       沙盒镜像 ghcr.io/openhands/agent-server:1.28.0-python；
#       V0（controller/runtime/events）仅存于 DeepWiki 归档，可作文档级考古
```

## 五、深读子页地图（88 页精选 6）

| 页 | 行号 | 为什么值得读 |
|---|---|---|
| 1 OpenHands Overview | L6 | 产品矩阵 + 五层架构总图 + V0/V1 全景，10 分钟建骨架 |
| 1.2 V0 Legacy Architecture and V1 Migration Path | L729 | 双架构逐项对照表 + 术语映射，理解大平台如何换引擎 |
| 4.1 Runtime Abstractions and Implementations | L3656 | SandboxService 三实现类图 + `/execute_action` 时序，沙盒设计教科书 |
| 4.2 Action Execution Server | L3840 | 沙盒内执行器解剖：Bash/Jupyter/Browser/Editor 分发 + env 注入表 |
| 6.1 Agent Controller and State Management（V0） | L6247 | 完整状态机图 + `_step()` 十步 + 双熔断，Agent 循环的工业标准写法 |
| 6.2 Event-Driven Architecture | L6555 | EventStream 总线 + 事件全链路图（前端→服务端→沙盒→回调） |

（备选：6.5 Memory and Context Condensation L7013、7.4 V1 Conversation Architecture L7953、3.2 Sandbox Specification Service L2847）

## 六、与"我们"的关系（一句话）

学 Agent 框架（agent-development / 讲透 Agent 主题）的最佳工业级对照样本——CodeAct 循环、事件总线、记忆压缩、沙盒抽象每个讲透主题都能在这里找到生产级实现，而其 V0→V1 迁移本身就是大型 Agent 平台架构演进的一手教材。

---
生成：2026-08-21 · deepwiki 88 页全归档
