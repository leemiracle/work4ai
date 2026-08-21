# claw-code 深读卡 —— Claude Code 风格的开源 Rust 终端编码 Agent（双轨实现 + 机器可读恢复控制面）

> **定位**：claw-code 是一个高性能、local-first 的编码 Agent harness，最初受 Claude Code 架构模式启发，为 AI Agent 提供工具套件、slash 命令与成熟的会话运行时。仓库走**双轨架构**：生产级 Rust 多 crate 实现（`rust/`，产出 `claw` 二进制）+ Python clean-room 移植工作区（`src/`，作 parity 审计参照）。路线图主打确定性状态机（Worker Boot）、机器可读事件流（Lane Events）与自主恢复（Recovery Recipes）。

**本地**：`repos/claw-code`（ultraworkers/claw-code）｜**深读**：deepwiki 35 子页归档 `deepwiki/claw-code/full.md`（2026-08-21）

## 一、组件栈（DeepWiki 蒸馏）

| 层 | 职责 | 关键实体 |
|---|---|---|
| CLI/REPL | 交互入口、参数解析、行编辑与补全 | `claw` 二进制、`rusty-claude-cli::main`、`SlashCommand`/`SlashCommandSpec`、`LineEditor` |
| 会话运行时 | 对话循环、持久化、压缩、系统提示词 | `ConversationRuntime`、`Session`/`ContentBlock`、`SessionStore`、`SystemPromptBuilder` |
| 工具执行 | 工具注册、分发、权限门控、子 Agent | `GlobalToolRegistry`、`mvp_tool_specs`、`execute_tool`、Skill System |
| API/Provider | 多供应商抽象、SSE 流归一化、缓存 | `ProviderClient`、`Provider` trait、`anthropic`/`openai_compat`、`SseParser`、`prompt_cache` |
| MCP/Plugin | 外部工具发现、hook 扩展 | `McpServerManager`、`mcp_stdio`、Plugin Manifest、Hook Events |
| 编排控制面 | Worker 生命周期、任务包、策略与审批 | `WorkerStatus`、`LaneEventName`、`TaskPacket`/`TaskRegistry`、`PolicyEngine`、`ApprovalToken`、`GreenContract` |
| 周边服务 | 轻量 harness、工作区 RAG、对拍工具 | `claw-analog`、`claw-rag-service`（sqlite-vec/Qdrant）、`compat-harness`、`mock-anthropic-service` |
| Python 移植层 | 领域映射、parity 审计、安全作用域 | `PortRuntime`、`QueryEnginePort`、`PathScope`、`PARITY.md` 九车道检查点 |

## 二、核心机制

1. **Dual-Track 双轨架构**：Rust 生产轨（`rust/` 多 crate：cli/runtime/api/tools/commands/plugins）负责速度与内存安全；Python 轨（`src/`）先做 clean-room 表面积映射，再以 `PARITY.md` + Mock Parity Harness（mock-anthropic-service + 场景 JSON 对拍）持续校验行为等价。（来源：Overview、Repository Structure、Parity Audit）
2. **Session 持久化与三级 Compaction**：`Session` 以 JSONL 原子落盘（>256KB 轮转），按 workspace fingerprint 隔离防跨项目泄漏；超 token 预算（默认 10K/保留近 4 条）触发 `compact_session`，进阶走 **Trident 流水线**——Supersede（剔除被覆盖的文件操作）→ Collapse（折叠长工具链）→ Cluster（聚类相似消息），并有 Boundary Protection "walk-back" 保证 `ToolUse`/`ToolResult` 不被边界切断（防 provider 400）。（来源：Session Management and Compaction）
3. **Worker Boot 状态机 + Recovery Recipes + Lane Events**：Worker 生命周期显式建模为 `Spawning→TrustRequired/ToolPermissionRequired→ReadyForPrompt→Running→Finished/Failed`，配 `TrustResolver`（信任门提示自动识别）、Prompt-Misdelivery 检测（`WorkerPromptTarget` 判定 prompt 误入裸 shell）、`StartupEvidenceBundle` 取证；Lane 层发机器可读事件（`lane.started/green/red/finished`、`branch.stale_against_main`），失败按 `LaneFailureClass` 分类（PromptDelivery/TrustGate/BranchDivergence/McpHandshake），六大典型失败各有 Recipe，策略=自动恢复一次后升级。（来源：Worker Boot and Lane System、Recovery Recipes）
4. **Provider 抽象与模型兼容路由**：`ProviderClient` enum 统一 Anthropic 原生与 OpenAI-compatible 端点，含模型别名解析、reasoning 模型参数剥离、GPT-5 token 特判、Kimi/DashScope 路由，支持 Ollama/vLLM 本地接入；OAuth2 PKCE + 多 `AuthSource`。（来源：API Client、Model Compatibility、Permission Modes and OAuth）

## 三、与讲透系列的对位

| claw-code 机制 | 讲透X 对应主题 |
|---|---|
| ConversationRuntime 主循环（LLM↔工具 ReAct 式驱动） | 讲透 Agent/LLM：Agent Loop 与工具调用（agent-development 教程主线） |
| Session + Trident Compaction（上下文预算管理） | 讲透 LLM 长上下文/上下文窗口（三层宪法"直觉→公式→代码"可复用其 Supersede/Collapse/Cluster 讲法） |
| claw-rag-service（chunk→embed→sqlite-vec/Qdrant 检索） | 讲透 NLP/反向索引：RAG 全链路 Rust 参考实现 |
| MCP stdio/JSON-RPC 集成 | MCP 协议章（工具调用生态） |
| Mock Parity Harness 场景对拍 | 工程铁律"bash 跑通验证"的进阶版：行为级对拍可作为教程实验设计范式 |

## 四、关键入口

```text
rust/crates/rusty-claude-cli/src/main.rs   # claw 主入口：ConversationRuntime + MCP 装配
rust/crates/runtime/src/lib.rs             # 运行时门面（session/compact/prompt/permissions）
rust/crates/runtime/src/worker_boot.rs     # Worker 状态机 + StartupEvidenceBundle
rust/crates/runtime/src/trident.rs         # 三级 Compaction 流水线
rust/crates/runtime/src/lane_events.rs     # 机器可读事件流与失败分类
rust/crates/tools/src/lib.rs               # GlobalToolRegistry + mvp_tool_specs
rust/crates/api/src/lib.rs                 # ProviderClient（anthropic/openai_compat）
src/main.py                                # Python 移植轨入口（parity 参照）
.claw.json / CLAUDE.md / CLAW.md           # 工作区配置与项目记忆文件
```

## 五、深读子页地图（35 页精选 6）

| # | 页面 | 行号 | 精读理由 |
|---|---|---|---|
| 8 | Session Management and Compaction | L1130 | 最大页；Trident 压缩 + 边界保护是上下文管理核心 |
| 15 | Worker Boot and Lane System | L2267 | 本仓最独创的设计：状态机启动 + 事件化控制面 |
| 19 | Policy Engine, Green Contract, Approval Tokens | L2899 | 权限策略引擎与审批令牌账本（自主化安全设计） |
| 11 | Model Compatibility and Provider Routing | L1625 | 多模型/本地 provider 路由的工程细节 |
| 23 | claw-rag-service | L3555 | 可独立复用的工作区 RAG 服务（含 Web UI） |
| 27 | Parity Audit and Reference Data | L4242 | 双轨对拍方法论：场景清单 + 九车道检查点 |

## 六、与"我们"的关系（一句话）

claw-code 是"Claude Code 开源复刻"的 Rust 工程级范本——其 Agent Loop/Compaction/MCP 三件套是讲透 Agent 系列的活教材，而 Mock Parity Harness 的"场景对拍验证"可直接移植进 work4ai 教程的实验设计铁律。

---
生成：2026-08-21 · deepwiki 35 页全归档
