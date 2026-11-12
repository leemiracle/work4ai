# 讲透 goose

> aaif-goose/goose（Block 出品，AAIF 聚合）—— Rust 开源 AI agent 全家桶：crates 架构（agent core/provider/MCP 扩展）+ 桌面端（Electron UI）+ CLI + ACP server + Recipes 调度。
> 本地仓：/usr-data/data2/repos/aaif-projects/repos/goose（HEAD 390dfb8c，迁移自 ~/ai/explore/ai-trending/goose，原路径软链回读）

## 状态（2026-10-23 全链完成 ✅）

| 步骤 | 状态 | 产物 |
|---|---|---|
| DeepWiki 全量 | ✅ | [deepwiki/](deepwiki)（**51 页 100%**，全文 652K 字符，mcp.deepwiki.com 直连，2026-10-21） |
| understand 中文图谱 | ✅ | 仓内 `.understand-anything/knowledge-graph.json`（**4437 节点/9220 边/16 层/16 步 tour**，validator 0 issues 0 warnings，fingerprints 1350 文件@390dfb8c，2026-10-23；91 批 4 并发，backup-batches/ 全量备份） |
| onboarding | ✅ | [onboarding/ONBOARDING.md](onboarding/ONBOARDING.md)（4012 汉字/26,942 非空白字符，8 节 97 锚，主会话独立抽验 14 锚全命中） |
| explain 系列 | ✅ | [explain/](explain) 12 篇（合计 32,677 汉字/230,600 非空白字符，每篇 51-156 锚全源码核验，2026-10-23） |

字数口径（SB3 轮钉版双轨）：汉字数=正则 `[\x{4e00}-\x{9fff}]` 计数；非空白字符=`tr -d '[:space:]'`（含 markdown 语法与行号锚，故显著大于 worker 自报"正文非空白"）。

## explain 12 篇索引

| # | 篇 | 主角 | 汉字 |
|---|---|---|---|
| 01 | [agent.rs：reply 主循环](explain/01-agent-reply-engine.md) | reply/reply_internal/dispatch_tool_call 六出口漏斗 | 2534 |
| 02 | [Provider trait 契约](explain/02-provider-trait-contract.md) | base.rs 三必选方法+ApiClient 五路认证 | 2523 |
| 03 | [MCP 扩展机制](explain/03-mcp-extension-manager.md) | 三级路由/进程内 vs 子进程/MCP Apps 防伪造 | 3268 |
| 04 | [ACP 协议层](explain/04-acp-protocol-layer.md) | GooseAcpAgent 双角色/过程宏 schema 生成链 | 2504 |
| 05 | [session 持久化](explain/05-session-persistence.md) | SQLite 三表+六索引/13 版迁移链/BEGIN IMMEDIATE | 2588 |
| 06 | [CLI 装配线](explain/06-cli-session-builder.md) | build_session 18 步总装/REPL tokio::select! | 2824 |
| 07 | [goosed SSE 后端](explain/07-goosed-sse-backend.md) | 19 模块路由/两代 reply 端点/512 重放缓冲 | 2263 |
| 08 | [桌面主进程](explain/08-desktop-main-process.md) | 每窗口一 goosed/证书钉扎带外信道 | 3198 |
| 09 | [渲染层对话流](explain/09-renderer-chat-stream.md) | useReducer 12 action/SSE 双层消费/断线兜底 | 2696 |
| 10 | [上下文压缩](explain/10-context-compaction.md) | 0.8 阈值/middle-out 五档/工具对摘要 cutoff | 2611 |
| 11 | [recipe 与 scheduler](explain/11-recipe-scheduler.md) | 13 字段格式/minijinja 三层防御/cron 5→6 位 | 3183 |
| 12 | [permission 安全审批](explain/12-permission-security.md) | 五检查员管线/permission.yaml/LLM 判官 | 2485 |

## 源码级实证勘误（explain 系列产出，12 条钉版）

1. **subagent 委派不在 agent.rs**——subagent_handler.rs:141 新建独立 Agent+白名单扩展后复用同一 reply()；"禁止嵌套"实为架构性隔离（引擎无 parent 字段），无 nest/depth 守卫（01）
2. **developer 已不在 goose-mcp 内置清单**——它是进程内平台扩展；现役内置四件套=autovisualiser/computercontroller/memory/tutorial（goose-mcp lib.rs:59-62）（03）
3. `stream` 定义在 base.rs:469（460 是 trait 声明行）；base.rs 无 stream_inner；canonical 5063 模型目录在 goose-providers crate（02）
4. Message 实际定义在 goose-providers；goose 仓无 src/conversation/ 目录（05）
5. **goosed 入站头只有 X-Secret-Key 与 Last-Event-ID**；agent-session-id/agent-working-dir 是注入 MCP CallToolRequest._meta 的字段+task-local，不是 HTTP 头（07）
6. **TLS 自签证书已改磁盘缓存复用**（tls.rs load_cached_tls 快路径）；每次启动随机的只是认证 secret；两路径都向 stdout 打 GOOSED_CERT_FINGERPRINT=（08）
7. 渲染层无 zustand/redux——useReducer 12 action+模块级 resultsCache+window.dispatchEvent 自定义事件总线；React 应用平铺在 ui/desktop/src/（无 renderer/ 子目录）（09）
8. scheduler 无 notify 机制（仅 tracing+posthog）；**调度路径 retry_config: None 硬编码（scheduler.rs:923）——recipe.retry 对 scheduled job 无效**；Temporal 调度器已移除（11）
9. **permission_store.rs 的 ToolPermissionStore 是死代码**（全仓零消费者）；活权限表=config/permission.rs 的 PermissionManager（permission.yaml）；LLM 判官工具名 platform__tool_by_tool_permission，非 read_only_check（12）
10. 五检查员管线 Security→Egress→Adversary→Permission→Repetition 以 permission 决定为基线、其余只收紧不放松（tool_inspection.rs:243）；注入扫描默认关闭且只覆盖 shell 工具（12）
11. 两代 reply 端点并存是渐进迁移活标本：一代事件绑死 POST 不可重连；二代总线+512 重放缓冲+单调 seq 断线补发，渲染层 too-far-behind 走全量 reloadConversation（07/09）
12. ACP 自定义方法 59 个=58 个 _goose/unstable/* + 1 个标准 session/delete（custom_requests.rs:145）（04）

## DeepWiki 章节速览（11 章）

1 Goose Overview · 2 Architecture & Core Crates · 3 MCP Extension System · 4 Recipes & Scheduling · 5 ACP Server & Protocol Layer · 6 Desktop Application (Electron UI) · 7 CLI (`goose-cli`) · 8 Build, CI/CD & Release · 9 Testing & Evaluation · 10 Supporting Services & Infrastructure · 11 Glossary

深水区提示：2 章三个三级页（agent 状态机 / 上下文管理与压缩 / provider 线格式翻译）+ 2.2.4 Canonical Model Registry 是理解 goose 内核的关键，均已在 deepwiki/x2、x4、x5、x3 落盘。

入口：[deepwiki/INDEX.md](deepwiki/INDEX.md) · 覆盖率：[deepwiki/_coverage-check.md](deepwiki/_coverage-check.md)（含 2026-10-22 三级页口径甄别结论）
