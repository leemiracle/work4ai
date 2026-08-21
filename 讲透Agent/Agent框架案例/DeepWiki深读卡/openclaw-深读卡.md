# openclaw 深读卡 —— 自托管多渠道个人 AI 助理网关：消息 App 直连常驻 Agent 的完整工程化

> **定位**：OpenClaw（原 Clawdbot→Moltbot，2025 年末爆红后定名的开源明星项目）是自托管个人 AI 助手网关——常驻 Gateway 把 Telegram/WhatsApp/Slack/Discord 等消息渠道接往 Claude/OpenAI/本地模型（Ollama/llama.cpp/LM Studio）驱动的 Agent，配 MCP 工具、技能系统与定时任务。差异化在"个人助理信任模型"下的全栈工程化：一个 monorepo 同时交付服务端、Web/CLI/TUI 与 iOS/Android/macOS/Linux 原生客户端（CalVer 版本 2026.8.1）。
> **本地**：`repos/openclaw`（openclaw/openclaw）｜**深读**：deepwiki 68 子页归档 `deepwiki/openclaw/full.md`（2026-08-21）

## 一、组件栈（DeepWiki 蒸馏）

| 层 | 职责 | 关键实体 |
|---|---|---|
| 消息渠道 `extensions/*` | Telegram(grammY)/WhatsApp(baileys)/Slack(Bolt)/Discord/Buzz 接入：durable ingress、去重、进度草稿 | `defineChannelPluginEntry`、ProviderMonitor |
| Gateway 控制面 `src/gateway`+`packages/gateway-protocol` | 常驻 Node 守护进程：WebSocket RPC、会话/transcript（SQLite database-first）、热重载、设备配对与 operator scope | GatewayServer、gateway-protocol（TypeBox） |
| Agent 运行时 `src/agents` | 多引擎：Pi 内嵌循环 / Codex app-server / Claude CLI harness；failover、上下文压缩、steering | `runEmbeddedPiAgent`、CodexAppServer、agent-bundle-mcp-runtime |
| 模型提供方 `extensions/{anthropic,openai,google,ollama…}` | 提供方归一化发现、auth profile 隔离、本地服务按需 sidecar | provider normalization、auth-profiles.json |
| 工具与沙盒 `src/agents/tools` | exec/browser/web-search/cron 等工具 + policy 分层过滤 + Docker/Crabbox 隔离 | `createOpenClawCodingTools`、scheduled-tool-policy |
| 技能与插件 `src/skills`+`src/plugins`+`skills/` | SKILL.md 六级加载、Workshop 提案、manifest 驱动插件 + SDK 边界审计、ClawHub 注册表 | SkillWorkshop、PluginRegistry |
| 记忆 `extensions/memory-core` | QMD 可查询记忆文档、hybrid 检索、"Dreaming" 后台整理 | memory/hybrid.ts、dreaming-events.ts |
| 原生客户端 `apps/` | iOS/macOS(Swift)/Android(Compose)/Linux(Tauri)，兼作 Device Node 反哺摄像头/定位/短信 | NodeRuntime、`node.invoke` |

## 二、核心机制

1. **单 Gateway 控制面 + 协议代码生成**（来源：Platform Architecture / WebSocket Protocol & RPC）：hub-and-spoke 的中心是一个常驻守护进程，TypeBox schema 作为单一事实源生成 TS/Swift/Kotlin 三端协议代码（Connect/Request/Response/Event 四帧 + steering queue 主动推送）——把"个人 AI 助手"做成可从手机、手表、网页、TUI 同时接入的自托管服务，而非又一个 chatbot SDK。
2. **渠道即插件，传输与产品解耦**（来源：Channel Architecture / Platform Integrations）：渠道插件 transport-only（禁止产品命令树），统一 ingress monitor 做 durable admission 与断线恢复；Session Key 由 channel+chat 推导路由，多渠道共享同一 agent 记忆——AGENTS.md 明文"never infer commands from raw strings"。
3. **Cron/Heartbeat：从被动应答到主动 Agent**（来源：Automation & Cron）：五种调度（at/every/cron/on-exit/stream，stream 监督长命令输出批量触发）× 四档 sessionTarget（main/isolated/current/session:id，isolated 临时会话不污染主对话）；agent 可用 `cron` 工具自建任务但 `capCronJobToolsAllowOnCreate` 防自我提权；`heartbeat_respond` 显式收束主动回合。
4. **技能自进化与安全边界同体**（来源：Skills System / Security Model & Trust Boundaries）：Skill Workshop 从会话历史回顾提议新技能（proposal 状态机 pending/applied/rejected/quarantined），ClawHub 注册表做 sha256 完整性校验；SKILL.md 六级优先级 + requires 门控（bins/env/config/os）；个人助理信任模型下用 Docker/Crabbox 沙盒、SecretRef（secret 绑定 egress host）、`doctor` 审计自修兜底。

## 三、与讲透系列的对位

| openclaw 概念 | 讲透系列对应概念 |
|---|---|
| Gateway 常驻宿主 + steering queue 插话 | 讲透Agent：ReAct 循环之上的生命周期宿主与执行中转向 |
| Multi-Agent Routing + ACP 子代理（sessions_spawn） | 讲透多Agent协作：编排模式——主 agent 派生隔离子代理再回收 |
| Cron/Heartbeat/commitments 主动回合 | 讲透学习型Agent：自主性——定时巡检环境而非被动等待 |
| Skill Workshop 经验→技能 + Memory Dreaming 短期晋升 | 讲透学习型Agent：自进化与记忆机制（会话经验沉淀为可复用资产） |
| Tool Policy 分层 + Docker/Crabbox 沙盒 + SecretRef | 安全沙盒：能力分级放行而非一刀切禁用 |

## 四、关键入口

```
repos/openclaw/
├── packages/gateway-protocol/src/index.ts        # WebSocket RPC 协议 TypeBox schema（TS/Swift/Kotlin 多端代码生成源头）
├── src/agents/embedded-agent-runner/runs.ts      # Pi Agent Core 主执行循环（failover/overflow compaction/steering）
├── extensions/telegram/src/bot.ts                # 渠道插件范本（grammY；WhatsApp=baileys、Slack=Bolt 同构）
├── src/cron/isolated-agent/run.ts                # isolated cron 执行器（临时会话 + MCP runtime retire 防泄漏）
├── src/agents/tools/cron-tool.ts                 # agent 自管定时任务工具（capCronJobToolsAllowOnCreate 防自提权）
├── src/skills/workshop/service.ts                # Skill Workshop：技能提案创建/应用状态机
├── extensions/memory-core/src/memory/hybrid.ts   # QMD 记忆 + hybrid 检索（向量×关键词）
└── src/agents/system-prompt.ts                   # 系统提示词组装（CONTEXT_FILE_ORDER 分节 + 技能/身份注入）
```

## 五、深读子页地图（68 页精选 6）

1. **Platform Architecture**（p4）——hub-and-spoke 全景：Gateway 控制面 / 原生 Device Node / Agent 运行时三子系统一张图
2. **WebSocket Protocol & RPC**（p6）——四帧协议、steering queue、TypeBox→Swift/Kotlin 代码生成流水线
3. **Automation & Cron**（p35）——五种调度 × 四档 sessionTarget + heartbeat，"主动式 agent"完整设计
4. **Skills System**（p45）——SKILL.md（AgentSkills.io 规范）六级优先级、Workshop 提案、ClawHub 信任链
5. **Memory & Search**（p27）——QMD 记忆格式、hybrid search、"Dreaming" 后台整理与短期晋升
6. **Security Model & Trust Boundaries**（p54）——个人助理信任模型：沙盒、SecretRef、`doctor` 审计自修

## 六、与"我们"的关系（一句话）

学 Agent 不止学循环——这里是"把 LLM 变成常驻个人助理"的最完整生产级参考：渠道接入、主动调度、技能自进化、记忆、沙盒五大件在一个 monorepo 里全齐，其 AGENTS.md 工程契约本身就是上下文工程范本。

---
生成：2026-08-21 · deepwiki 68 页全归档
