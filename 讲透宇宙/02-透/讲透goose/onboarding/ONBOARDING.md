# goose 新人 Onboarding（Block 开源、现归 AAIF 基金会的 AI agent 全家桶）

> 图谱基线：commit `390dfb8c`，16 层 / 4437 节点 / 9220 边，分析于 2026-10-23。文中行号锚均经源码或图谱节点 summary 核实；图谱概数（如「3400 行」）与实测行数可能有百分之一量级漂移，见⑦节。

## ① 这个项目是什么 / 为什么存在

goose 是 Block 开源、现已迁入 AAIF 基金会治理的开源 AI agent（README.md 顶部有迁移公告），用**同一套 Rust 核心引擎长出三种产品形态**：Electron 桌面应用、终端 CLI、HTTP API。它不是又一个聊天客户端，而是一个「会话引擎 + 模型接入 + 工具扩展」的三层平台：支持 15 家以上 providers（含 Claude/ChatGPT/Gemini 订阅复用、Ollama 等本地推理、claude/codex 等 CLI coding agent），通过 70 个以上 MCP extensions 接工具，还内置 recipe（可复用提示配方）、skills 技能、cron 定时调度、权限审批、本地 Whisper 听写、遥测等完整工程能力。社区侧有 Discord 助教 bot、recipe 安全扫描容器、五平台 npm 二进制分发等周边。对企业用户，CUSTOM_DISTROS.md（全仓最大文档）给出从预置模型到桌面品牌化的完整自定义发行版手册。

为什么存在：把 agent 的核心难题——reply 循环、上下文压缩、会话持久化、工具分发、安全审批——全部沉淀在 `crates/goose` 一个 crate，再让 CLI（goose-cli）、桌面后端（goose-server/goosed）、ACP 协议层都做它的薄壳。仓库本体是一个 cargo workspace（Cargo.toml members 覆盖 crates/* 八个 crate：goose 核心、goose-cli、goose-server、goose-mcp、goose-acp-macros、goose-providers、goose-sdk、goose-test/goose-test-support），加一个 pnpm ui 工作区（desktop/text/sdk/acp 四包）与 evals 评测区。换模型、换前端、换接入协议互不牵连——这是它区别于单体聊天工具的根本设计。`.goosehints` 与 AGENTS.md 把这条架构规约钉死：**非平凡功能一律进 goose crate，各端只做调用**；桌面端新功能要先在 goose-server 加路由、跑 `just generate-openapi` 生成契约、再由 TS 调用。四个入口点（AGENTS.md「Entry Points」节）：CLI 是 `crates/goose-cli/src/main.rs`，Server 是 `crates/goose-server/src/main.rs`，UI 是 `ui/desktop/src/main.ts`，Agent 是 `crates/goose/src/agents/agent.rs`。仓库根的 CLAUDE.md 只有一行——`@AGENTS.md`，把协作规范原样透传给 Claude Code 会话；治理上 GOVERNANCE.md 定义贡献者/维护者/核心维护者三级角色与 RFC 流程，安全漏洞走 SECURITY.md 的私密上报通道。

## ② 全景架构：16 层地图

- **L0 Agent 会话引擎（goose 核心，68 文件）**：全仓心脏，跨层入度 347——Provider 层 126 边、CLI 49 边、server/SDK 36 边、ACP 26 边都指向它。`agents/` 44 文件管 reply 循环、planner/extend 生命周期与 subagent 调度；`session/` 11 文件管 SQLite 会话持久化与导入导出；根模块还有 model.rs（1008 行，模型名到上下文/温度限额解析）、token_counter.rs（tiktoken 分词 + LRU 缓存）、prompt_template.rs（MiniJinja 模板）、session_context.rs（task-local 会话上下文）。
- **L1 LLM Provider 适配层（130 文件）**：`crates/goose/src/providers` 106 文件（mod.rs 声明 59 个子模块）+ goose-providers crate。三分支组织：declarative（29 个 YAML 声明式 provider）、formats（OpenAI/Anthropic wire 格式双向转换）、local_inference（GGUF/llama.cpp 本地推理）。配套 goose-providers 提供 Conversation 消息容器、统一错误枚举与 canonical 模型目录。
- **L2 工具与 MCP 扩展子系统（59 文件）**：goose-mcp crate 四个内置 MCP 扩展 + 核心 crate 的 skills（SKILL.md 发现）、plugins（gemini/open-plugins 双格式）、goose_apps（MCP App 缓存与资源）、tool_inspection（工具检查框架）、tool_monitor（重复调用拦截）、download_manager（断点续传下载本地模型）。
- **L3 ACP 协议层（33 文件）**：`crates/goose/src/acp` 29 文件实现 Agent Client Protocol 服务端，配 goose-acp-macros 过程宏与 acp-schema.json（144 个 $defs）/acp-meta.json（59 个 `_goose/unstable/*` 方法注册表）。桌面端 Electron 经 ACP client 与 goosed 通信。
- **L4 配置·安全·网关与提示词资产（99 文件）**：config（多源合并/keyring 密钥回退）、security（提示注入双检）、permission（LLM 判官审批）、gateway（Telegram 等外部网关 trait）、recipe（10 文件模型与校验）、prompts（10 文件系统提示模板）、scheduler（cron 定时按 recipe 起会话）、slash_commands、dictation（Candle 加载 GGUF 的本地 Whisper，whisper.rs 1200 行）、posthog 遥测（604 行）。入度 304，仅次于核心层。
- **L5 goose-cli 命令行界面（65 文件）**：clap 命令树（run/session/schedule/recipe/review/term/serve/mcp/gateway 等）+ 交互式 REPL + configure 向导 + review 代码评审。纯消费者，跨层入度 0。
- **L6 goose-server 与 Rust SDK（60 文件）**：goosed HTTP API（46 文件：会话管理/调度器/健康检查/token 鉴权）+ goose-sdk/goose-sdk-types（wire 类型单点真相源，uniffi 生成 Kotlin 绑定 aaif.goose）。
- **L7 桌面端主进程与构建打包（48 文件）**：main.ts（2818 行 Electron 主进程：窗口树/goose:// 深链/托盘/更新）、preload.ts（contextBridge 白名单 IPC）、goosed.ts 与 mesh.ts（后端/本地推理进程编排）、startupDiagnostics.ts 启动诊断、forge/vite 构建配置、prepare-platform-binaries.js 平台二进制准备。
- **L8 桌面端渲染进程应用层（116 文件）**：React 骨架——入口 renderer.tsx/App.tsx、hooks 13 个（useChatStream 是聊天核心）、contexts、api 目录（OpenAPI 生成客户端）、i18n 四语言、recipe/会话封装。前端最大被依赖底座（入度 524）。
- **L9 桌面端组件库（305 文件）**：settings 90、icons 78、ui 25（shadcn 基件）、recipes 22、alerts/onboarding/schedule/sessions/McpApps 功能组件。纯消费叶子（入度仅 31，出度 504）。
- **L10 TUI 与 TypeScript SDK 发布件（57 文件）**：ui/text（React Ink 终端聊天 TUI，tui.tsx 1424 行）、ui/sdk（@aaif/goose-sdk：ACP 客户端 + Streamable HTTP 传输）、goose-binary 五平台 npm 二进制。与 Rust 侧零 import，纯协议解耦。
- **L11 边缘服务（50 文件）**：services/ask-ai-bot（Bun 的 Discord AI 助教）、oidc-proxy（Cloudflare Worker：OIDC 凭据转 Anthropic API）、recipe-scanner（社区 recipe 安全扫描容器）、provider-error-proxy（供应商故障注入，专测重试韧性）。与主代码零 import 耦合，经 API/容器边界交互。
- **L12 测试、示例与评估（124 文件）**：crates/goose tests 47 + goose-test/goose-test-support 14 + 桌面 e2e/integration + evals（open-model-gym 套件与 harbor 基准）+ 仓根 goose-self-test.yaml 自测配方与基准脚本。
- **L13 CI/CD 流水线（61 文件）**：47 个 GitHub workflow（release/desktop/cli/docs/benchmark/nightly 全覆盖）+ composite actions 3 个 + dependabot 三路周更 + issue 模板。
- **L14 基础设施与工具链（65 文件）**：根 Dockerfile 多阶段镜像、.devcontainer（devcontainer 开发镜像补 keyring/DBus/protobuf 依赖）、bin/ Hermit 工具链钉扎（38 个 wrapper + 隐藏 .pkg 版本锁）、Justfile（450 行 34 目标）、flake.nix、deny.toml、clippy.toml。
- **L15 文档与项目资产（18 文件）**：README/CONTRIBUTING/RELEASE 三部曲、GOVERNANCE/MAINTAINERS/SECURITY 治理、BUILDING_DOCKER/LINUX/CUSTOM_DISTROS 构建指南、I18N.md，以及 AI 协作提示（AGENTS.md/CLAUDE.md/.goosehints）。

## ③ 核心抽象

**1. Agent 会话引擎（reply 主循环）**。`crates/goose/src/agents/agent.rs`（3395 行）是核心 Agent：`agent.rs:1406` 的 `pub async fn reply` 是对外入口，`agent.rs:1616` 的 `reply_internal`（约 800 行）跑真正的循环——每轮把会话交给 provider 流式消费，收到工具请求后由 `agent.rs:916` 的 `dispatch_tool_call` 分发到扩展工具（`agent.rs:715` 的调用点在 subagent 路径复用同一分发）。循环内还有两条支线：失败重试由 agents/types.rs 的 RetryConfig 与 SuccessCheck 控制（可按校验函数判定成功与否决定重试）；planner 模式与 subagent 委派（delegate 工具支持同步/异步，嵌套被禁止）让一个会话能派生子会话干活。循环的分文件实现在 reply_parts.rs（960 行）：`reply_parts.rs:141` 的 `prepare_tools_and_prompt` 每轮准备工具与系统提示词，`reply_parts.rs:578` 起按 MCP Apps 规范（2026-01-26 版）过滤对模型不可见的工具。Agent 构造时在 `agent.rs:344` 创建扩展管理器；会话到 Agent 的生命周期、每会话取消令牌由 `execution/manager.rs` 的 AgentManager（770 行）管理。系统提示词来自 prompt_template.rs：`prompt_template.rs:7` 用 `include_dir!` 编译期内嵌 prompts 目录，`prompt_template.rs:9` 起的 TEMPLATE_REGISTRY 注册 system/compaction/plan/subagent_system/permission_judge 等十个模板，用户可自定义覆盖。

**2. Provider trait 与 canonical 目录**。`providers/base.rs:460` 定义 `pub trait Provider`（图谱函数节点给出 L460-L802 区间），核心是 `base.rs:469` 的 `async fn stream` 流式对话，外加模型推荐、元数据、凭据声明。三类实现路线：托管 API（anthropic.rs/openai.rs/databricks 等，openai_compatible.rs 通道构造器被大量第三方 provider 复用，openai.rs 的 API key 走 secret→环境变量→keyring 三级解析）；CLI coding agent（claude_code.rs/codex.rs 以子进程驱动外部 CLI，codex 每轮 spawn `codex exec` 读 JSONL 事件）；本地推理（local_inference 显存感知上下文预算 + 逐 token 生成）。配套 goose-providers crate 是消息底座：conversation.rs 的 `fix_conversation` 修复管线（合并连续同角色消息、补空 tool result、修复配对）；errors.rs 的 ProviderError 统一错误枚举（认证/上下文超长/限流含 retry_delay/额度耗尽含 top_up_url），重试策略由 providers/retry.rs 的 retry_operation 按「仅瞬态错误」执行；`canonical/registry.rs:9` 用 Lazy 内联 canonical_models.json——**5063 个模型的规范目录**，免网络解析限额（对应数据由 `goose/src/bin/build_canonical_models.rs` 从 models.dev API 抓取构建）；另可用 `config/declarative_providers.rs`（1273 行）以 YAML 声明自定义 provider，支持 `${VAR}` 展开与工厂注册。

**3. MCP 扩展机制**。扩展配置模型在 `agents/extension.rs`：ExtensionConfig 枚举七种形态（stdio/http/inline python 等）加 Envs 白名单校验。`agents/extension_manager.rs:743` 起的 ExtensionManager（2932 行）管 MCP 客户端全生命周期——stdio/http/unix socket/oauth 多传输连接、工具名前缀与资源/提示词聚合。内置扩展在 goose-mcp crate：`goose-mcp/src/lib.rs:57` 的 BUILTIN_EXTENSIONS 表注册四个扩展（autovisualiser/computercontroller/memory/tutorial），`lib.rs:31` 的 spawn_and_serve 以进程内 DuplexStream 伺服——**内置扩展不需要真的起子进程**。每个内置扩展各有绝活：autovisualiser 暴露八种可视化工具，模板与样式经 `autovisualiser/mod.rs:749` 的 include_str! 编译期内联（get_template_html 从 mod.rs:744 起）；computercontroller 聚合 web_scrape/GUI 自动化/office 文档（docx/xlsx）工具；memory 提供 global/local 两级文件记忆；tutorial 内嵌教程引导 agent 主动推介（`tutorial/mod.rs:14`）。工具交互层：`agents/mcp_client.rs:69` 的 McpClientTrait 抽象 stdio/sse 连接，`mcp_client.rs:286` 的 create_message 实现采样反向请求与 elicitation。质量护栏：tool_inspection.rs 的检查器框架把检查结果混入权限判定；tool_monitor.rs 用调用指纹（工具名+参数摘要）拦截重复调用防死循环。外围生态：skills/mod.rs 发现全局（~/.agents/skills）与项目级 SKILL.md 并合并内置技能（`skills/builtin.rs:3` 内嵌打包）；plugins/mod.rs 实现 gemini/open-plugins 双格式安装与 24 小时自动更新。

**4. ACP 协议层**。ACP 是桌面端/IDE 接入的主协议。`acp/server.rs:203` 的 GooseAcpAgent 管会话生命周期与通知路由，`server.rs:2365` 的 `on_prompt` 处理对话请求；`acp/server/new_session.rs:13` 的 handle_new_session 校验 cwd、恢复/创建会话并装配扩展。最具特色的是自定义方法分发：`acp/server/custom_dispatch.rs:4` 标注 `#[custom_methods]`，由 goose-acp-macros 过程宏（`goose-acp-macros/src/lib.rs:42`）在编译期把约 60 个 `_goose/unstable/*` 方法（扩展增删/工具直调/偏好读写/听写密钥）生成为 JSON-RPC 分发器，wire 契约落在 acp-schema.json（144 个 $defs）与 acp-meta.json（59 个方法三元组）。传输双通道：transport/http.rs 提供 POST JSON-RPC（`http.rs:102` 记录入站）、GET SSE 流、DELETE 关闭（`http.rs:280`）；transport/websocket.rs 做全双工消息泵。反向能力：`acp/provider.rs:332` 把外部 ACP agent 进程适配为 goose 的 Provider——goose 既当 ACP 服务端也能消费别人的 ACP agent。

四个抽象的衔接：**Agent 引擎只面向 Provider trait 编程**（模型后端可无痛切换）；**所有工具经 ExtensionManager 聚合**注入 reply 循环，权限与监控在分发链上生效；**ACP、goosed HTTP、CLI REPL 都是引擎外壳**，共享同一套会话持久化与配置层。

## ④ 一次会话的生命周期

**CLI 路径**：`goose` 命令 → `goose-cli/src/main.rs`（初始化日志，Windows 启用 VT 转义序列否则 spinner 不刷新）→ cli.rs（2286 行 clap 命令树）→ `session/builder.rs:483` 的 build_session 装配 provider/model/扩展/session id（恢复旧会话或新建）→ CliSession（session/mod.rs，2449 行）跑 REPL 主循环。用户输入后调用 `agent.rs:1406` reply → `reply_internal`（1616）→ `reply_parts.rs:141` 准备工具与提示词 → `base.rs:469` provider.stream 流式返回。若模型发起工具调用：`agent.rs:916` dispatch_tool_call → ExtensionManager 按工具名前缀路由（内置扩展走进程内 spawn_and_serve，外部扩展经 `mcp_client.rs:69` 起 stdio/sse 子进程）→ 结果作为 tool response 追加进会话 → 下一轮继续，直到模型给出纯文本收尾。每条消息经 session_manager.rs 落 SQLite：全局单例在 `session_manager.rs:52`，存储实现在 `session_manager.rs:540` 的 SessionStorage（657 行起 impl，`session_manager.rs:730/746/779` 三张建表语句 schema_version/sessions/messages；迁移逻辑 `session_manager.rs:987` 的 apply_migration）。上下文逼近限额时 context_mgmt/mod.rs（815 行）触发自动压缩与工具响应裁剪，token_counter.rs 全程计数。权限敏感工具走 permission 层的 LLM 判官确认链（permission_judge 模板构造 read_only_check 工具判定只读可否放行），等待用户或智能审批。会话全程有 task-local 上下文（session_context.rs 把 SESSION_ID 存进 tokio task_local，并定义 agent-session-id/agent-working-dir 两个 HTTP 头常量），外部 MCP server 可据此识别会话归属。跨工具迁移者有福：session/import_formats/mod.rs 能嗅探并转换 claude_code/codex/pi 等四种外来会话格式为 goose 原生 JSON，CLI 的 `goose session import` 甚至支持 Nostr 加密链接分享。

**桌面路径**：`ui/desktop/src/main.ts`（2818 行）启动时 `main.ts:27` 加载 .env（VITE_START_EMBEDDED_SERVER=yes 时拉起内嵌后端）→ goosed.ts 探测端口、定位二进制、健康检查、按运行模式构造环境变量并 spawn goosed → goosed 的 `commands/agent.rs:152` axum::serve 挂全部路由（routes/mod.rs 的 configure() 总装）。此后前端有两条数据通道：**HTTP 面**——渲染进程经生成的 API 客户端（sdk.gen.ts，60 余个类型安全函数）调 REST，对话走 `routes/reply.rs:210` 的 reply handler 以 SSE 流推送（session_event_bus.rs 用单调序列号 + Last-Event-ID 重放缓冲支撑断线续连与请求级取消）；**ACP 面**——`ui/desktop/src/acp/acpConnection.ts:44` 建 WebSocket 流、`acpConnection.ts:66` 的 getAcpClient 维护 GooseClient 单例，JSON-RPC 到 `server.rs:2365` on_prompt → 复用同一条 Agent reply 循环。goose:// 深链由 main.ts 处理，可直达 recipe 运行或扩展安装（deeplink.ts 有命令白名单与 npx -c 注入防护）。本地推理场景下 mesh.ts 另管 mesh-llm 进程（仅 macOS Apple Silicon，端口 9337 探活）。两条通道各有所长：HTTP 面管配置、会话管理与对话 SSE，ACP 面管扩展协商、权限确认与自定义通知，前端 useChatStream 用 useReducer 状态机把两边事件归一成同一条消息流。

## ⑤ 目录导航

| 需求 | 去处 |
|---|---|
| 新增/改 provider | `crates/goose/src/providers/`（实现 `providers/base.rs:460` 的 Provider trait，mod.rs 注册子模块）；YAML 声明式走 `config/declarative_providers.rs`；canonical 目录在 goose-providers crate |
| 加内置 MCP 扩展 | `crates/goose-mcp/src/`（`lib.rs:57` 注册表 + 对应子目录）；接外部 MCP server 只需 ExtensionConfig 配 stdio/http |
| 桌面端 UI | 组件 `ui/desktop/src/components/`（305 个）；应用层 hooks/api 在 `src/`；主进程/IPC 在 `src/main.ts` 与 `src/preload.ts` |
| 桌面端新后端功能 | 先 `crates/goose-server/src/routes/` 加路由，再 `just generate-openapi` 重生成契约与 `src/api/`（AGENTS.md 铁律） |
| recipe | 数据模型 `crates/goose/src/recipe/mod.rs`（877 行）；校验 validate_recipe.rs；CLI 命令 `goose-cli/src/commands/recipe.rs`；前端表单 `components/recipes/`；自测配方仓根 goose-self-test.yaml |
| 配置/密钥 | `crates/goose/src/config/`（base.rs 2401 行多源合并；paths.rs 标准目录布局） |
| 会话存储 | `crates/goose/src/session/session_manager.rs`；迁移工具 `scripts/goose-db-helper.sh:220`（从 `session_manager.rs:987` 的 apply_migration 自动抽取 SQL 生成迁移文件） |
| ACP 协议 | 服务端 `crates/goose/src/acp/`（server/ 与 transport/）；TS 侧 `ui/sdk/src/`（http-stream.ts 实现 Streamable HTTP） |
| TUI | `ui/text/src/`（tui.tsx 1424 行主入口；无 --server 时自动拉起 goose acp 子进程） |
| 定时任务 | `crates/goose/src/scheduler.rs`（cron 按 recipe 起会话）；命令 `goose-cli/src/commands/schedule.rs` |
| 测试 | `crates/goose/tests/`（AGENTS.md：优先 tests/ 目录）；UI 测试 `ui/desktop` pnpm test；评测 `evals/` |
| CI/发布 | `.github/workflows/`（release.yml 正式链、ci.yml 主 CI）；本地命令 Justfile（450 行 34 目标） |
| 安全/遥测 | 提示注入扫描 `crates/goose/src/security/`；权限 `config/permission.rs` 与 permission/ 判官；网关 `gateway/mod.rs`；遥测 posthog.rs |
| 听写/本地模型 | 本地 Whisper `crates/goose/src/dictation/whisper.rs`；本地模型注册表 `providers/local_inference/local_model_registry.rs` 与下载器 download_manager.rs |

## ⑥ 构建·测试·质量体系

- **环境**：`source bin/activate-hermit`（必须 source 而非执行）注入钉扎工具链——bin/ 下 38 个 wrapper 由 Hermit 管理（bin/hermit 是自举 stub，勿手改），rust-toolchain.toml 锁 channel 1.92，Cargo.toml workspace 统一 version 1.37.0 与 rust-version 1.91.1，llama-cpp-2 等敏感依赖精确钉扎。
- **构建/测试/lint**（AGENTS.md 钉版）：`cargo build` / `cargo test`（单 crate `cargo test -p goose`）/ `cargo fmt` / `cargo clippy --all-targets -- -D warnings`。clippy.toml 设 too-many-lines-threshold=200，超过 200 行的函数才告警。
- **schema 生成链**：server 改路由必须 `just generate-openapi`（`Justfile:168`；生成器 `goose-server/src/bin/generate_schema.rs:10-15` 写出 ui/desktop/openapi.json，105 路径/115 操作，openapi-ts.config.ts 再生成前端 src/api 客户端）；ACP 侧 `just generate-acp-schema`（`Justfile:189`，cargo run --bin generate-acp-schema 从 Rust 类型生成 acp-schema.json）与 `just generate-acp-types`（`Justfile:195`）；漂移守卫 `just check-openapi-schema`（`Justfile:164`），CI 在 `ci.yml:190` 强制执行、`ci.yml:192` 另查 ACP Schema 是否最新。
- **goose 自测**：`goose run --recipe goose-self-test.yaml`（AGENTS.md:79 钉版流程）。goose-self-test.yaml（447 行）让 goose 用自己的工具测自己——文件 CRUD、shell 执行、代码分析、扩展发现、delegate 委派（同步+异步+嵌套禁止）、错误边界全链路，参数化 test_phases 可裁剪阶段。
- **测试资产纵深**：ACP 回归库 `crates/goose/tests/acp_common_tests/mod.rs` 的 36 个共享步骤函数被 provider/server 两种连接视角复用；`tests/providers.rs` 是 19 家 provider 参数化矩阵（图像/上下文超限/模型切换/权限）；`tests/agent.rs` 17 个 tokio 测试覆盖调度/重试/权限；`tests/mcp_integration_test.rs:296-298` 挂四个真实 MCP server 的录制/回放夹具（goose-test-support 的 McpFixture 逐请求校验 agent-session-id 头）。评测线 open-model-gym 的 runner.ts（1504 行）组模型×场景矩阵、三级 sha256 缓存、出 HTML 报告；桌面端另有 playwright e2e 与 18 家供应商冒烟矩阵。
- **CI 与供应链**：主 CI ci.yml 用 dorny/paths-filter 做路径门控分流 rust-format/build-and-test/msrv/lint/schema-check，Windows 编译独立验证；cargo-deny.yml 按 deny.toml 审计依赖（yanked 直接拒绝，RUSTSEC-2023-0071 因无安全升级路径显式忽略）；code-review.yml 是手动触发的 LLM 代码评审（容器内跑模型评审再回帖 PR）；dependabot 三路周更 npm/cargo/actions。发布走 RELEASE.md 的 minor/patch 双轨：周二 cron 自动开版本 PR，人工打 tag 触发 release.yml 并行复用 build-cli 与五个桌面打包工作流，附带 SLSA provenance。
- **日常开发命令**：`just run-ui`（`Justfile:96`，release 构建 + 拉起桌面）、`just check-everything`（`Justfile:8`，fmt+clippy+UI lint+schema 校验一站式）、`just release-binary`（`Justfile:22`）。Docker 构建见根 Dockerfile：`Dockerfile:6` builder 阶段 rust:1.82 极限尺寸优化（LTO/opt-level=z/strip），`Dockerfile:37` 运行阶段摘要钉扎的 debian:bookworm-slim 非 root 用户，`Dockerfile:69` ENTRYPOINT goose。devcontainer 开发镜像在 `.devcontainer/Dockerfile` L5-11 补 keyring/DBus/protobuf 原生依赖。

## ⑦ 深水区预警（图谱勘误与坑）

1. **生成物绝对勿手改**：AGENTS.md「Never」节明令禁止手编 `ui/desktop/openapi.json`；`ui/desktop/src/api/types.gen.ts`（4877 行）与 sdk.gen.ts 是 openapi-ts 产物；`ui/sdk/src/generated/` 三件（zod.gen.ts 1472 行、client.gen.ts——其 L3-8 的 ExtMethodProvider 接口在 import 语句之前，属非典型序文件）从 acp-schema.json 生成；acp-schema.json 又是 generate-acp-schema bin 从 Rust 类型生成的。改了 Rust 忘跑 just generate-openapi，CI `ci.yml:190` schema-check 直接红。
2. **迁移遗留副本**：`crates/goose-server/ui/desktop/openapi.json` 是 60KB 旧副本（真身是仓根 ui/desktop/openapi.json 235KB，全仓零消费者）——别改错文件。
3. **图谱行数口径有百分之一量级漂移**：图谱标 agent.rs「3400 行」实测 3395、extension_manager.rs 标 2900 实测 2932、acp/server.rs 标 3800 实测 3785。本文锚以实测为准，引用其他图谱概数前先 wc -l 校准。
4. **知识图谱的 scanner 盲区**（消费图谱时须知道）：Rust 跨 crate use 几乎全靠源码重扫补齐（179 条）；GitHub workflow 的 steps 数组提取恒为空（90 个 job 级 step 节点全部 PyYAML 补扫，行号独立抽验 7/7 命中，如 bundle-windows sign L203、canary release L125、release.yml:102、build-cli.yml:175 与 L244-246 的 CUDA 变体）；`tests/agent.rs` 因深层嵌套 mod tests 提取到 0 个函数；React.memo const 组件（InputBar/Viewport/SplashScreen 等）extractor 全漏手工补建；`#[path = "X"] mod name;` 属性重定向是朴素 mod 解析盲区（6 文件实证）。
5. **Dockerfile 阶段 endLine 系统性多计 1**（0-index 转换伪差，rust 12→11/debian 103→102/production 36→35，已手工修正）——图谱里 Dockerfile 阶段行范围使用前先对源文件核一遍。recipe-scanner 的 scan-recipe.sh 内嵌 Python heredoc 的函数结束行也被花括号干扰过（heuristic 报 587 实际 608）。
6. **仓内拼写笔误两处**：autovisualiser sankey 模板占位符 `{{D3_SANKY}}` 实为 d3.sankey.min.js（`autovisualiser/mod.rs:762`，资产实名不含拼写错误）；components.json 指向不存在的 tailwind.config.ts（Tailwind v4 CSS-first 迁移残留）。
7. **vendor 资产不在图谱扫描集**：chart.min.js/d3*/leaflet*/mermaid.min.js 被 .understandignore 排除未建边——可视化模板的血缘要看 `autovisualiser/mod.rs:749` 的 include_str! 链（get_template_html 从 mod.rs:744 起编译期内联）。
8. **i18n 陷阱**：非英文目录无完备性闸门（tr 键 1610 多于 en 1586）；en.json 运行时不加载（文案内联 defaultMessage），`i18n/index.ts:18` 的 SUPPORTED_LOCALES 才是四语言真名单。
9. **巨石文件导航**：acp/server.rs 3785 行、extension_manager.rs 2932 行、session_manager.rs 2891 行、cli.rs 2286 行、ChatInput.tsx 1811 行、main.ts 2818 行——动手前先 grep 符号定位，别通读。
10. **发布流水线的锚**：bundle-desktop.yml:139 把 goosed 拷进 Electron 目录、L176 跑 bundle:default；publish-npm.yml:182 以 pnpm publish --provenance 发布；这些 workflow 锚经图谱终验 9/9 命中，可放心引用。

## ⑧ 上手路线：3 天计划

**Day 1（tour step 1-5）：读懂引擎**。上午 step 1 门面三件（README/AGENTS.md/.goosehints）+ step 2 核心会话引擎：精读 `agent.rs:1406` 到 `agent.rs:1616` 的 reply 循环、reply_parts.rs 的准备与消费、`session_manager.rs:540` 的存储层；下午 step 3 Provider trait（`base.rs:460`，对照 anthropic.rs 与 openai_compatible.rs 两种风格）+ step 4 MCP 扩展（`lib.rs:57` 注册表与四个内置扩展）+ step 5 ACP（`server.rs:203` 的 GooseAcpAgent 与 custom_dispatch 的宏分发）。目标：`source bin/activate-hermit && cargo build`，跑一次 `goose` CLI 会话，观察一次工具调用的完整往返。

**Day 2（tour step 6-11）：贯通两端**。上午 step 6 配置安全权限（base.rs 多源合并 + permission 判官 + scheduler）+ step 7 CLI REPL（CliSession 与 configure 向导）+ step 8 goosed（`routes/reply.rs:210` 的 SSE 通道与 session_event_bus）；下午 step 9 Electron 主进程（main.ts 窗口树 + goosed.ts 编排）+ step 10 渲染层（useChatStream 状态机 1169 行 + 生成的 API 客户端）+ step 11 组件库速览（ChatInput/BaseChat/ToolCallWithResponse 三大件）。目标：`just run-ui` 跑通桌面端，对照④节数据流用开发者工具看一次 reply 的 SSE 流。

**Day 3（tour step 12-16）：贡献闭环**。上午 step 12 TUI 与 TS SDK（http-stream.ts 的 Streamable HTTP 双 GET SSE）+ step 13 边缘服务（ask-ai-bot/oidc-proxy/recipe-scanner）+ step 14 测试评估（acp_common_tests 36 步骤库与 provider 矩阵）；下午 step 15 CI/发布链（ci.yml 路径门控 + release.yml 复用工作流）+ step 16 治理文档与工程守护（goose-db-helper.sh、check-openapi-schema.sh）。目标：挑一个小改动（如给 goose-server 加一个只读路由）走完全流程——加路由 → `just generate-openapi` → cargo fmt/clippy/test → 更新 goose-self-test.yaml → `goose run --recipe goose-self-test.yaml` 验证 → git commit -s（DCO 签署）。走完这条链，你就完成了第一个合格的 goose 贡献。

延伸资料：仓库根 PROGRESS.md 是本知识图谱流水线自己的台账（含全部图谱勘误的钉版记录，⑦节多数结论的出处）；`../../../../讲透宇宙/02-透/讲透goose//` 目录另有 deepwiki 全量文档 51 页与本图谱的完整导览（tour 16 步、每层代表节点摘要），读完本篇后可按需下钻。
