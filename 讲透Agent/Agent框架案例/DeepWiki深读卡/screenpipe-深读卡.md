# screenpipe 深读卡 —— 把整台电脑变成 Agent 的 24/7 记忆：Rust 事件驱动捕获 + SQLite 全文索引 + pipe.md 声明式 Agent 插件

> **定位**：screenpipe 是开源的 local-first "AI 记忆"系统——持续捕获屏幕（截图 + OCR + accessibility tree）与音频（VAD + STT），全部存入本地 SQLite/FTS5，通过 `localhost:3030` REST API 与 MCP server 暴露给 Claude/Cursor 等助手。核心是一句承诺：**捕获、处理、存储 100% 在本机**（CPU 5-10%，RAM 0.5-3GB，~20GB/月），隐私靠本地 PII redaction 与可选加密。对 Agent 框架视角最有价值的是它的 **Pipes 插件系统**：一个 `pipe.md`（YAML frontmatter + Markdown prompt）就是一个定时/事件触发的 LLM Agent，由 Pi coding agent 子进程带权限沙箱执行。
> **本地**：`repos/screenpipe`（screenpipe/screenpipe）｜**深读**：deepwiki 48 子页归档 `deepwiki/screenpipe/full.md`（2026-08-21）

## 一、组件栈（DeepWiki 蒸馏）

| 层 | Crate/模块 | 职责 | 关键实体 |
|---|---|---|---|
| 捕获层 | `screenpipe-screen` / `screenpipe-audio` / `screenpipe-a11y` | 截帧+OCR（Apple Vision/Windows OCR/Tesseract）、音频 WAV chunk、平台 accessibility tree | `paired_capture()`、`AudioRecorder`、`TreeWalkerPlatform`、`AccessibilityTreeNode` |
| 引擎层 | `screenpipe-engine` | 事件驱动捕获调度、per-monitor 录制任务、Axum HTTP API(3030)、DRM/睡眠检测 | `VisionManager`、`EventDrivenCapture`、`CaptureTrigger`、`ServerCore`、`DRMDetector` |
| 存储层 | `screenpipe-db` / `screenpipe-vault` | SQLite + FTS5 全文索引、压缩帧、加密 `store.bin`（magic header `SPSTORE1`） | `DatabaseManager`、frames 表、5 层设置恢复（`bin.last-good`） |
| AI/插件层 | `screenpipe-core` | pipe.md 解析调度、Agent 子进程执行、权限规则、AI preset 熔断降级 | `PipeManager`、`PiExecutor`、`AgentExecutor`、`PipePermissions`、`PresetFallbackRegistry` |
| 桌面壳 | `apps/screenpipe-app-tauri` | Tauri + Next.js UI、时间线 Rewind、托盘/快捷键/onboarding、Pi 会话管理 | `main.rs`、`CaptureSession`、`PiManager`、`SettingsStore` |
| 访问层 | `screenpipe-mcp` | 把屏幕历史作为 MCP 工具暴露给 Claude/Cursor | `npx -y screenpipe-mcp` |
| 商业层 | `ee/` | 企业版：license 校验、admin policy、MDM/Intune 管控 | `AdminPolicy`、`EnterpriseSettingsGuard` |

## 二、核心机制

1. **事件驱动捕获（非固定轮询）**：`CaptureTrigger` 枚举定义全部触发原因——`AppSwitch`/`Click`/`TypingPause`/`ScrollStop`/`Clipboard`/`VisualChange`/`Idle` 等，经 `TriggerSender` broadcast channel 分发给 per-monitor 任务；`FocusAwareController`（聚焦屏优先）、`HighFpsController`、`PowerProfile`（AC/电池动态调频）做性能调优；`DRMDetector` 识别 Netflix 等 DRM 内容即停采释放句柄。（来源：Data Capture Pipeline）
2. **ServerCore vs CaptureSession 两相架构**：长寿的 API/DB/Pipe 层（`ServerCore`）与可随时停开的资源密集捕获层（`CaptureSession`）分离，暂停录制不丢服务；`BootPhase` 原子量（`migrating_database`→`building_audio`）保证 HTTP server 在 DB 就绪后才 bind，消除启动竞态。（来源：System Overview）
3. **pipe.md = 声明式 Agent 插件**：YAML frontmatter（`schedule: every 30m`/cron/事件触发、`model`、`permissions`、`connections`、`timeout`、`artifacts`）+ Markdown 正文即 prompt。执行时 `PipeManager` 注入 context header（ISO8601 时间窗、时区、`http://localhost:3030`、输出目录），`PiExecutor` spawn pi-coding-agent 子进程，LLM 自己 `curl /search` 拿数据再行动——"Agent 即插件，插件即提示词"。（来源：Pipes System）
4. **三层权限沙箱 "Deny→Allow→Default→Reject"**：类型化规则 `Api(METHOD /path)` / `App(name)` / `Window(glob)` / `Content(ocr|audio|input|accessibility)`，经 `SCREENPIPE_PIPE_PERMISSIONS` 环境变量传给子进程，服务端 `OptionalPipePerms` extractor 从 bearer token 还原权限并**在 SQL 查询层过滤结果**——最小权限贯彻到数据行，而非只在网关拦 URL。（来源：Pipes System）

## 三、与讲透系列的对位

| screenpipe 机制 | 对位讲透主题 | 对位要点 |
|---|---|---|
| Pipes：cron/事件触发的 LLM 子进程 | Agent 框架（agent-development：多智能体/工具调用） | "提示词即插件"的极简 Agent 编排范本，对照 LangGraph 的显式图编排 |
| Pi agent 经 MCP/HTTP 自主 curl /search | MCP 协议（agent-development/MCP 章节） | 工具调用两形态对比：MCP server（暴露历史）vs REST API（Agent 主动拉取） |
| SQLite FTS5 全文检索屏幕历史 | RAG（llm-mastery：RAG 章节） | 非向量库路线：结构化时间窗查询 + BM25，本地优先的"记忆检索" |
| Context header 注入（时间窗/环境） | prompt-engineering：结构化输出/Agent 提示词 | 运行时上下文注入的工程实践 |
| CaptureTrigger broadcast channel | Agent 事件循环/ReAct（讲透 Agent 反射-行动循环） | 感知端的事件总线设计：信号→决策→动作 |
| PermissionRule + SQL 层过滤 | 安全/沙箱话题 | Agent 权限模型的"数据行级"粒度案例 |

## 四、关键入口

```text
repos/screenpipe/
├── crates/screenpipe-engine/src/server.rs               # ServerCore：Axum API + DB pool + Pipe 执行
├── crates/screenpipe-engine/src/event_driven_capture.rs # CaptureTrigger 枚举 + TriggerSender broadcast
├── crates/screenpipe-engine/src/vision_manager/manager.rs # VisionManager：per-monitor 任务 DashMap
├── crates/screenpipe-screen/src/core.rs                 # paired_capture()：截图 + a11y tree 成对采集
├── crates/screenpipe-db/src/db.rs                       # DatabaseManager：SQLite + FTS5
├── crates/screenpipe-core/src/pipes/mod.rs              # PipeManager：pipe.md 解析与调度
├── crates/screenpipe-core/src/pipes/permissions.rs      # PermissionRule + 服务端行级过滤
├── crates/screenpipe-core/src/agents/pi.rs              # PiExecutor：AgentExecutor 子进程实现
└── apps/screenpipe-app-tauri/src-tauri/src/main.rs      # Tauri 壳 + CaptureSession 生命周期

# 体验入口
npx -y screenpipe@latest record                          # CLI 守护进程，数据落 ~/.screenpipe/
claude mcp add screenpipe --transport stdio -- npx -y screenpipe-mcp  # 接入 Claude/Cursor
```

## 五、深读子页地图（48 页精选 6）

| 子页 | full.md 行号 | 为什么值得读 |
|---|---|---|
| 2.2 Data Capture Pipeline | L1385 | 全书精华：CaptureTrigger 全表、a11y tree 三平台实现（cidce/UIA/AT-SPI2）、DRM 检测、CorrelationId 帧链接 |
| 4.2 Pipes System | L4867 | 插件系统全景：pipe.md 格式、调度语法、执行时序图、三层权限模型 |
| 2.1 System Overview | L1192 | 组件拓扑 + ServerCore/CaptureSession 分相 + Pi Agent JSON-RPC 数据流 |
| 2.4 Storage & Database | L1879 | SQLite+FTS5 schema 与索引策略（存储层细节） |
| 4.3 MCP Server | L5118 | 屏幕历史如何变成 Agent 工具（与 Pipes 互补的另一种暴露方式） |
| 4.1 Pi Coding Agent | L4660 | 内置 coding agent 的会话管理与 provider 路由（native-ollama/openai/anthropic/cloud） |

## 六、与"我们"的关系（一句话）

screenpipe 是"Agent 上下文工程"的工业级活教材——它示范了 agent-development/llm-mastery 里 RAG、MCP、工具调用、多 Agent 编排如何落到一个 local-first 产品：捕获管道=感知、SQLite=记忆、pipe.md=行动，恰好是你学 Agent 框架时每个抽象的实物对照。

---
生成：2026-08-21 · deepwiki 48 页全归档
