# 分册 C · 编码 Agent / 研究 Agent / 基础设施（11 仓深读）

> 深读材料：README（前 300 行）+ 关键源文件（≤350 行）+ 代码树指标。行号证据限于已读片段。

### google-gemini/gemini-cli
- **架构模式**：TypeScript monorepo（packages/，2996 文件，.ts=1737）分层的终端 Agent，核心 `@google/gemini-cli-core` 可被多种宿主（CLI、GitHub Action、A2A server）复用。
- **核心抽象**：`AgentCard`（A2A 自描述卡片，packages__a2a-server__src__http__app.ts:45-90）；`CoderAgentExecutor`（执行器，app.ts:23/265）；`CommandRegistry` 命令注册表（app.ts:146/314-347）。
- **关键机制**：A2A 协议服务化——`DefaultRequestHandler + TaskStore`，任务持久化可选 GCS 或内存（app.ts:249-273）；流式命令执行走 `DefaultExecutionEventBus` + SSE（app.ts:160-178）；会话 checkpointing 用 `GitService`（app.ts:242-246）；启动即做路径信任检查 `checkPathTrust` 防注入（app.ts:204-209）。
- **工程亮点**：同一 core 同时输出 CLI / JSON / stream-json 三种模式，且通过 a2a-server 把 CLI 变成可被其他 Agent 调用的网络服务。
- **教学映射**：讲透多Agent协作（A2A）、讲透上下文缓存（GEMINI.md + token caching）、透视Agent系统工程。
- **一句话本质**：把 Gemini 以"免费、终端原生、可脚本化"的方式交到开发者手里，并顺手定义了 Agent 服务化边界。

### aaif-goose/goose
- **架构模式**：Rust workspace（crates/，2368 文件，.rs=514）的"本地通用 Agent 内核"，一套内核同时暴露 CLI、桌面、MCP server 三种形态。
- **核心抽象**：`SessionManager`/`SessionType`（crates__goose-cli__src__cli.rs:36-37）；`Recipe`（可分享的 YAML Agent 配方，cli.rs:10/237-276）；`Extension` 体系（stdio/streamable-http/builtin 三类，cli.rs:174-208）。
- **关键机制**：防失控护栏——`max-tool-repetitions`（连续相同调用熔断）与 `max-turns`（cli.rs:115-129）；扩展可跑在指定 Docker `--container` 内实现隔离（cli.rs:131-137）；`serve` 子命令生成随机 ACP secret 供桌面端复用（cli.rs:40-49）；子配方 `--sub-recipe` 组合复用（cli.rs:268-276）；内置 `MemoryServer`/`TutorialServer` 等 MCP 扩展（cli.rs:13）。
- **工程亮点**：GoosePlatform 抽象让 CLI 与桌面共享同一 Agent 会话协议（cli.rs:51-65）；15+ 提供商 + 70+ MCP 扩展全走同一扩展接口。
- **教学映射**：讲透多Agent协作、讲透记忆（MemoryServer）、透视Agent系统工程。
- **一句话本质**：用 Rust 做一个跑在你机器上、可编程可插拽数据的"干活的鹅"，而不是聊天框。

### SWE-agent/SWE-agent
- **架构模式**：学术派"可复现实验装置"——单 YAML 配置治理全部行为，一切围绕 trajectory（轨迹）文件组织（409 文件，.py=100）。
- **核心抽象**：`run`/`run-batch` 批量执行入口（sweagent__run__run.py:89-96）；trajectory 数据结构 `{thought, action, response, observation}`（sweagent__inspector__server.py:26-35）；延迟导入的子命令分派（run.py:88-140）。
- **关键机制**：轨迹一等公民——inspect/inspector/traj-to-demo/run-replay 全是围绕轨迹的查看、转换、回放工具链（run.py:21-27）；每条轨迹记录 cost/tokens/api_calls 统计（server.py:84-99）；README 明示核心论点"Agent-Computer Interfaces Enable Automated Software Engineering"（README:27-34）。
- **工程亮点**：为可微调的实验对比而生的 `compare-runs`/`quick-stats`；官方承认被 100 行的 mini-swe-agent 取代（README:19-24）——本身就是关于"接口设计>代码量"的教材。
- **教学映射**：讲透代码生成、透视Agent系统工程（可复现 Agent 实验方法学）。
- **一句话本质**：证明"给 LM 设计好的计算机接口（ACI）"比堆 Agent 框架更能解决真实 GitHub issue。

### continuedev/continue
- **架构模式**：单一 headless `core` 进程 + 多 IDE 前端的"内核/外壳"架构（3058 文件，extensions[848]/core[726]/gui[443]，.ts=1429）。
- **核心抽象**：`Core`（core/core，由 binary__src__index.ts:37 启动）；`IMessenger<ToCoreProtocol, FromCoreProtocol>` 双向消息协议（index.ts:5-21）；`IpcIde` 把 IDE 能力抽象为接口（index.ts:34）。
- **关键机制**：进程通信双模——生产走 IPC、开发走 TCP 便于调试（index.ts:22-33）；`LLMLogFormatter` 把每次 prompt 落盘成可审计日志（index.ts:38）；协议即类型，core 与扩展层靠 protocol 包解耦。
- **工程亮点**：一份 core 同时服务 VS Code/JetBrains/CLI 三种宿主，是"IDE 插件如何共享 Agent 内核"的干净范本；已归档发布 final 2.0.0（README:19-29），生命周期管理本身值得讲。
- **教学映射**：讲透代码生成、透视Agent系统工程。
- **一句话本质**：把 coding agent 做成 IDE 无关的本地服务，证明内核与 UI 分离是插件形态 Agent 的正确形态。

### TabbyML/tabby
- **架构模式**：自托管 Copilot 替代——Rust 推理服务端（crates/）+ TypeScript LSP agent（clients/tabby-agent）+ 企业版（ee/，2099 文件，.tsx=299/.rs=272）。
- **核心抽象**：`CompletionProvider`（clients__tabby-agent__src__codeCompletion__index.ts:54）；`CompletionCache` + 上下文哈希/前向上下文（index.ts:41,57）；ContextProvider 家族——workspace/git/declarationSnippets/recentlyChangedCodeSearch（index.ts:83-88）。
- **关键机制**：LSP `inlineCompletion` 能力协商与动态注册/注销（index.ts:166-254）；`CompletionDebouncer` 防抖节省推理（index.ts:42,203）；`LatencyTracker` 自动诊断超时/慢响应并生成用户帮助文案（index.ts:50,108-118）；接受率遥测每 24h 回传（index.ts:219-222）；README:63 记录 repo 级 RAG 补全自 v0.3 起是核心卖点。
- **工程亮点**：把"补全质量"工程化为 cache→debounce→多源上下文→后处理→统计闭环，全部在客户端 agent 内完成。
- **教学映射**：讲透代码生成、讲透RAG（代码补全场景的 repo 上下文检索）。
- **一句话本质**：让企业能在自己 GPU 上跑一个不联网、可审计的 Copilot，难点全在补全延迟与上下文工程。

### assafelovic/gpt-researcher
- **架构模式**：planner 生成研究问题 → 并行 execution agent 检索汇总 → publisher 聚合成报告的流水线（763 文件，.py=274）。
- **核心抽象**：`GPTResearcher`（唯一入口类，backend__report_type__deep_research__main.py:16-19）；`conduct_research()/write_report()` 两阶段（main.py:23-27）；`ChatAgentWithMemory`（backend__server__app.py:35）。
- **关键机制**：deep research 用 depth×breadth 树状递归展开子课题，`on_progress` 回调实时上报进度（main.py:8-13）；FastAPI + `WebSocketManager.run_agent` 推送 Agent 过程到前端（app.py:24-32）；报告产物持久化到 ReportStore/outputs 静态目录（app.py:71-91）；retriever 可组合 `tavily,mcp` 做混合检索（README:158-191）。
- **工程亮点**：用"先规划问题再并行搜集"对冲单次长报告的 token 限制与幻觉（README:27、56-67）。
- **教学映射**：讲透RAG、讲透多Agent协作（planner/executor/publisher 分工）。
- **一句话本质**：把"深度研究报告"拆成可并行、可引用、可追踪的小检索任务，让 LLM 做研究而不是编故事。

### firecrawl/firecrawl
- **架构模式**：面向 LLM 的 Web 数据 API——TS 单体 apps/api（1717 文件，.ts=798），搜索/抓取/交互/Agent 全部计费化、策略化。
- **核心抽象**：`agentController`（apps__api__src__controllers__v2__agent.ts:23）；threat protection 管线（agent.ts:61-126）；credit 计费（`billTeam`/`calculateThreatScanCredits`，agent.ts:19-20/84-98）。
- **关键机制**：Agent 请求先做 URL 威胁策略校验，被拦截也要为已发生的扫描扣费并出 SIEM 审计事件（agent.ts:73-126）；校验通过后透传给独立 Agent 服务 `EXTRACT_V3_BETA_URL`（agent.ts:160-184）；`uuidv7` 作为分布式任务 ID（agent.ts:27）；输出统一为 clean markdown/结构化 JSON（README:42,56）。
- **工程亮点**：把"网页→LLM 可用上下文"做成带安全、计量、ZDR（零数据保留）开关的商业级 API。
- **教学映射**：讲透RAG（数据获取层）、透视Agent系统工程。
- **一句话本质**：替 Agent 干掉 Web 上最脏的活——代理、JS 渲染、反爬、格式清洗——并按量卖干净上下文。

### infiniflow/ragflow
- **架构模式**：Go+Python 双栈重写中的 RAG 引擎（5508 文件，.go=1911/.py=1121/.tsx=830），DeepDoc 解析 + 模板化分块 + Agent 画布三层。
- **核心抽象**：`AgentComponent`（基于 cloudwego/eino ReAct 的多轮 Agent，internal__agent__component__agent.go:72-75）；`SubAgentTool`（子 Agent 包装为父 Agent 的工具，agent.go:111-116）；`AgentParam.Cite`（引用接地二次调用，agent.go:99-105）。
- **关键机制**：`scanAllStreamForToolCall` 消费完整流后才判定是否进工具节点，避免漏掉尾部 tool_call（agent.go:257-273）；流式 agent 输出与工具判定并行——先启动 `emitAgentModelStreams` 再 `agent.Stream`（agent.go:193-212）；`MessageHistoryWindowSize` 截断历史窗口（agent.go:314-319）；子 Agent 递归深度上限 `maxSubAgentDepth=8`（agent.go:40）；Go 实现逐行镜像 Python 行为并注释源码位置（agent.go:61-67）；沙箱执行器是独立 FastAPI + slowapi 限流（agent__sandbox__executor_manager__main.py:22-25），代码执行需 gVisor（README:157）。
- **工程亮点**：文档引擎可在 Elasticsearch/Infinity 间切换（README:279-297）；分块可视化允许人工干预——"quality in, quality out"。
- **教学映射**：讲透RAG（最完整）、讲透多Agent协作（子Agent/工具/画布）。
- **一句话本质**：解决"烂文档进、幻觉出"的问题——用深度解析和可控分块保证进入 LLM 的上下文质量。

### daytonaio/daytona
- **架构模式**：三平面（interface/control/compute）的沙箱基础设施运行时（README:63-70）；注意：本地快照仅含 README+assets（3 文件），且 2026-06 起核心转闭源（README:1-7），以下基于 README 证据。
- **核心抽象**：Sandbox（完整可组合计算机：独立内核/文件系统/网络栈/vCPU/RAM，README:36）；Snapshot（有状态环境快照，README:40）；五类工具矩阵 platform/sandbox/agent tools/human tools/system tools（README:52-61）。
- **关键机制**：沙箱冷启动 <90ms，OCI/Docker 兼容（README:38）；Agent 经 SDK/API/CLI 操作进程执行、文件系统、LSP、git、PTY、computer use（README:40,54-61）；人机入口 web terminal/SSH/VNC/VPN（README:58-61）。
- **工程亮点**：把"执行 AI 生成的代码"从安全问题提升为一等平台能力——网络限额、审计日志、webhook 全部内置。
- **教学映射**：透视Agent系统工程、软件即熵治理（Agent 执行环境治理）。
- **一句话本质**：给不可信的 Agent 代码一个秒级创建、完全隔离、可快照续命的"一次性电脑"。

### mudler/LocalAI
- **架构模式**：Go 小核心 + 按需拉取的 OCI 后端镜像（3561 文件，.go=1636，core[1599]/backend[1022]），"装了你才存在"的组合式 AI 引擎。
- **核心抽象**：Backend Gallery（60+ 后端运行时装卸，README:215）；Model Gallery（`local-ai run model:tag`，README:149-159）；模型族谱 `family/childBuild`（.github__ci__apexentries__main.go:67-80）。
- **关键机制**：后端自动探测 GPU 并下载匹配镜像（README:171）；分布式模式 PostgreSQL+NATS、prefix-cache-aware 路由（README:181-184）；量化阶梯 `rungRank`（Quality→Nano）自动排序生成 gallery 条目（main.go:49-52）；从 HuggingFace 实际文件名发现构建而非信任 repo 命名（main.go:14-17）；自研一批纯 C++/GGML 零 Python 推理引擎（vllm.cpp、parakeet.cpp 等，README:225-248）。
- **工程亮点**：API 层 OpenAI/Anthropic/ElevenLabs 三兼容 + 多用户配额，让"本地模型"可以直接顶替线上 API。
- **教学映射**：透视Agent系统工程、软件即熵治理（依赖最小化）、讲透上下文缓存（prompt cache）。
- **一句话本质**：让任何硬件跑任何模态模型且只装你需要的部分——用组合式架构对抗 AI 工具链的膨胀。

### hpcaitech/ColossalAI
- **架构模式**：PyTorch 之上的并行训练加速框架（2207 文件，.py=1708），配置文件声明并行策略、Booster 注入改写。
- **核心抽象**：`Config`（colossalai.context，launcher__run.py:9）；`HostInfo/HostInfoList`（多节点主机模型，run.py:11）；`MultiNodeRunner`（SSH 远程执行器，run.py:12/276）。
- **关键机制**：hostfile 解析 + include/exclude 主机过滤（run.py:18-105）；按 torch 版本（<1.9 / 1.9 / >1.9）动态生成 `torch.distributed.launch`/`torchrun` 命令（run.py:157-209）；逐节点 send/recv 收集成败状态并统一退出码（run.py:294-337）；并行策略覆盖 DP/PP/1D-3D TP/SP/ZeRO/Auto（README:160-166）。
- **工程亮点**："像写单机模型一样写分布式模型"——一行配置换并行策略；B200 上 7B 训练吞吐较 H200 提升 50%（README:67-74）。
- **教学映射**：讲透世界模型（训练基础设施侧）、透视Agent系统工程（分布式编排）。
- **一句话本质**：解决"大模型训不起"——把多机多卡并行策略压缩成一份配置文件。

---

## 组内横向对比

**编码 Agent 三种形态**：CLI 双子星（gemini-cli/goose）的共同点是"会话即资产"——checkpointing、session resume、recipe/GEMINI.md 把交互经验沉淀为可复现制品，且都在向 A2A/ACP 协议化演进（gemini-cli 的 AgentCard vs goose 的 serve secret），区别在 TS 生态位 vs Rust 单二进制。学术派 SWE-agent 反其道行之：不建框架，用单 YAML + trajectory 文件把"Agent-计算机接口"变成可度量、可回放、可对比的实验对象，其被 mini-swe-agent（100 行）取代恰恰证明 ACI 设计才是变量。IDE 插件派（continue/tabby）本质是"headless 内核 + 宿主适配"：continue 用 IMessenger 协议让 VS Code/JetBrains/CLI 共享一个 core，tabby 则把工程重心放在补全的延迟/缓存/多源上下文闭环上——前者赢在架构分层，后者赢在垂直体验。

**RAG 三层分工**：firecrawl 是"取"层（Web→干净 markdown，含安全与计量）；ragflow 是"存与炼"层（DeepDoc 解析、模板分块、多路召回融合重排，再往上是 eino ReAct Agent 画布）；gpt-researcher 是"用"层（planner 把问题拆给并行 execution agent，消费前两层的输出并聚合为带引用的报告）。三者正好构成《讲透RAG》单元的完整纵深：数据获取→索引与检索→agentic 消费。
