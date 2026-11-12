# 02 · Rust 正典 harness 解剖

> card_id: claw-code-02
> universe: Agent框架案例
> burke: 场景=净室重写的 Rust 正典；主体=runtime crate 47 模块；能动=ConversationRuntime 驱动循环；行动=逐组件 file:line 取证；目的=六组件模型的可引用实现；张力=_flat 大文件 by design vs 可维护性；弧线=48K→116K 行的 5 个月演化
> status: 已完成（2026-08-20，HEAD `08106b0`）
> refs: rust/crates/ 实测；AGENTS.md CODE MAP 交叉验证
> updated: 2026-08-20

## 0. 工作区地图（2026-08 实测）

11 crates / 101 .rs / **115,957 行**（PARITY 检查点 2026-04-03 仅 9 crates/48,599 行——新增 claw-analog、claw-rag-service 与 lane_events/policy_engine/worker_boot 等舰队模块）：

| crate | 职责 | 关键文件 |
|---|---|---|
| `runtime` | 会话/配置/权限/MCP/提示/auth（47 个平铺模块） | conversation.rs 1878 · config.rs 3894 · mcp_stdio.rs 2969 · lane_events.rs 2561 · prompt.rs 1436 · hooks.rs 1151 · compact.rs 846 |
| `api` | Provider 客户端/SSE/请求预检 | prompt_cache.rs 735（缓存遥测！）· sse.rs 330 · client.rs 265 |
| `tools` | 55 工具 spec + 执行 | lib.rs **10,892 行单文件** |
| `commands` | 120+ slash 命令注册表 | lib.rs ~7.2K |
| `rusty-claude-cli` | `claw` 二进制：REPL/一次性/子命令 | main.rs **19,831 行**（手写 parser，CliAction 枚举 ~L1162，dispatch L995-1158——AGENTS.md 口径） |
| `plugins` | 插件元数据/安装/启停 | manifest=`.claude-plugin/plugin.json` |
| `claw-analog` | 精简 CI agent（见 04 篇） | lib.rs（NDJSON 合同） |
| `claw-rag-service` | 独立 RAG 进程（见 04 篇） | axum + SQLite/Qdrant |
| `mock-anthropic-service` | 确定性 /v1/messages mock | `SCENARIO_PREFIX` 剧本协议 |
| `compat-harness` / `telemetry` | parity 工具 / 会话追踪类型 | |

**风格契约**（AGENTS.md:53-60，全部实测可验）：workspace 级 `unsafe_code = "forbid"`；巨型平铺文件 **by design**（组织是"位置性"的：类型→spec 表→dispatch→handlers→EOF 测试）；双输出路径 `render_x` + `render_x_json`，**JSON 错误走 stdout、文本错误走 stderr**；集成测试以 `CARGO_BIN_EXE_claw` 子进程打 mock 服务。

## 1. ConversationRuntime：主循环（conversation.rs）

结构体定义 `conversation.rs:130-143`，**12 字段**（泄露版 7 字段的 8 月演化）：

```rust
pub struct ConversationRuntime<C, T> {   // C: ApiClient, T: ToolExecutor
    session: Session,                     // 有状态对话记忆
    api_client: C,                        // 模型连接（trait 注入，可 mock）
    tool_executor: T,                     // 真实世界连接
    permission_policy: PermissionPolicy,  // 安全网关
    system_prompt: Vec<String>,           // 行为规范注入
    max_iterations: usize,                // 失控保护（默认 usize::MAX！:185）
    usage_tracker: UsageTracker,          // 成本追踪
    hook_runner: HookRunner,              // 生命周期钩子
    auto_compaction_input_tokens_threshold: u32,  // 默认 100_000（:18）
    hook_abort_signal / hook_progress_reporter / session_tracer,
}
```

`run_turn()`（:325）主循环骨架（:354-510 实读）：

```
健康金丝雀 → push 用户消息 → loop {
    迭代上限检查(:356)                     # usize::MAX 说明靠压缩而非硬上限兜底
    stream(ApiRequest{system_prompt, messages})   :368
    build_assistant_message(events) + 记录 usage/prompt_cache 事件
    提取 pending_tool_uses                   :387-396
    push assistant 消息
    maybe_auto_compact()  ← #3106：无工具的最后一轮也压，防会话无界增长 :408-412
    无工具 → break                          :414
    for each tool_use {
        pre_hook：可取消/拒绝/**改写输入**(:420 updated_input)/覆盖权限(:423-426)
        permission_policy.authorize_with_context(...)  :449-463
        Allow → execute → merge_hook_feedback → post_hook(成功/失败两个变体:475-488)
        Deny{reason} → 也生成 tool_result，is_error=true 回注对话  :505-510
    }
}
```

三个值得讲的决策：
1. **拒绝是信息，不是异常**：权限拒绝/钩子取消都以 `tool_result(is_error=true)` 回注，模型感知后自行调整计划——与泄露分析一致，这里有了实现锚点。
2. **压缩是循环内一等公民**：默认 100K input tokens 触发（env `CLAUDE_CODE_AUTO_COMPACT_INPUT_TOKENS` 可覆盖 :19；还能在收到 400 后按服务器返回的上下文窗口动态调阈值 :207-212）。
3. **压缩后健康探测**（:306-322，ROADMAP #38）：用 `glob_search "*.health-check-probe-"` 这种"必然空匹配"的探针验证工具执行器还活着——**用无害工具调用当心跳**。

## 2. SystemPromptBuilder：静态/动态分界（prompt.rs）

- `SYSTEM_PROMPT_DYNAMIC_BOUNDARY = "__SYSTEM_PROMPT_DYNAMIC_BOUNDARY__"`（:40），在 `build()`（:211-233）中插在静态段（intro/output style/system/doing tasks/actions）与动态段（environment/project context/指令文件/config/append）之间——**分界线之前可被 provider 缓存**，这就是 Raschka 说的"激进缓存复用"的实现面。
- 指令文件祖先链：优先级 `CLAUDE.md` → `CLAW.md` → `AGENTS.md`，发现范围限定 git root（rust/README.md:157）。团队级/子项目级/个人级三级叠加的"约定优于配置"在净室版被简化为三种文件名+git root 边界。
- `status --output-format json` 会汇报 `workspace.memory_files[]`（path/source/origin/scope_path/outside_project/chars/contributes）——**系统提示的每一块都能被审计**。

## 3. 权限双模块：Policy 与 Enforcer 分层

**permissions.rs（策略层）**：`PermissionMode` 五档（:9-15）：`ReadOnly < WorkspaceWrite < DangerFullAccess` + `Prompt` + `Allow`——比泄露版的"三级"多了两档运行时语义。`PermissionPolicy`（:99-109）= active_mode + 每工具 required_mode（BTreeMap）+ **allow/deny/ask 三列规则表** + `denied_tools`（#159：小写归一化的无条件拒绝，先于规则表求值）。hook 可注入 `PermissionContext{override: Allow/Deny/Ask}`（:31-43）——**钩子优先于静态规则**。

**permission_enforcer.rs（执行层，738 行）**：`PermissionEnforcer`（:27）是 pre-dispatch 闸门：`check_file_write()` 做 workspace 边界/只读拒绝；`check_bash()` 只读模式下拒绝变更命令、prompt 模式无确认则阻塞。工具表里每个 spec 自带 `required_permission`（tools/lib.rs:109）：`bash=DangerFullAccess`(:505)、`read_file=ReadOnly`(:520)、`write_file/edit_file=WorkspaceWrite`(:534/:550)。

> 与泄露版对照：Daniel Zhang 记录的"ReadOnly 无法运行时升级到 WorkspaceWrite（须重启，防诱导）"在净室版表现为 `--accept-danger-non-interactive` 显式旗标 + claw-analog 非交互模式硬阻断（claw-analog/src/lib.rs:50）。

## 4. Compaction：上下文生命周期（compact.rs,846 行）

- `estimate_session_tokens`（:35）逐消息粗估求和 → `should_compact`（:41）：压缩预算 + `preserve_recent_messages` 尾部保 immobilization。
- `compact_session`（:96）：保留近 N 条，旧消息让位给摘要；已压缩过的会话取 `existing_summary` 续压（:101-104）；`preserve_recent_messages == 0` 时有专门的越界守卫（注释直接解释了 saturating_sub 陷阱）。
- 摘要后处理（:55-94）：剥 `<analysis>` 块、抽 `<summary>` 标签转人话、`get_compact_continuation_message` 生成合成续接消息（可抑制追问/标注近消息已保留）——**压缩产物本身是 prompt 工程**。
- 掘金报道泄露版另有 `microcompact`（优先清旧 tool results）与 AutoDream（梦游整理记忆）——净室版未实现，属于"重写边界"的诚实缺口。

## 5. Session：会话持久化（session.rs）

`Session`（:117 附近）：version/session_id/时间戳/messages/`compaction: Option<SessionCompaction>`/`fork: Option<SessionFork>`/`prompt_history`/`model`/`last_health_check_ms`（#38 心跳）/**`workspace_root`**。

最有意思的文档注释（:107-115 原文意译）：*workspace_root 把会话绑死在创建它的 worktree。全局会话仓库被所有 serve 实例共享，若不绑定 workspace root，并行 lane 会竞态——在错误 CWD 落盘却报告成功（"Phantom completions"，ROADMAP #41）。*——**这是从 opencode 共享会话仓库的实弹教训里抄来的防御**（注释直接点名 `~/.local/share/opencode`），多 agent 并行时代 session 隔离的跨项目知识转移样本。

配套：`SessionHeartbeat{transport_alive, liveness}`（:100-105）——会话活性是显式状态机，不是"进程还在就算活着"。

## 6. 工具面：55 个 spec（tools/lib.rs:484-1348）

实测 55 个（grep `name: "` 计数，与 AGENTS.md 口径一致），按能力族分：

| 族 | 工具 | 备注 |
|---|---|---|
| 核心执行 6 | bash / read_file / write_file / edit_file / glob_search / grep_search | bash schema 带 sandbox 微调（run_in_background/isolateNetwork/filesystemMode/allowedMounts）——4 月 9-lane 后持续加码 |
| 产品面 17 | WebFetch/WebSearch/TodoWrite/Skill/Agent/ToolSearch/NotebookEdit/Sleep/SendUserMessage/Config/Enter(Exit)PlanMode/StructuredOutput/REPL/PowerShell/AskUserQuestion | AskUserQuestion 已从 stub 换真实现（PARITY:9） |
| Task* 7 | TaskCreate/RunTaskPacket/TaskGet/TaskList/TaskStop/TaskUpdate/TaskOutput | TaskPacket 带 scope_path/worktree（progress.txt US-005） |
| **Worker\* 9** | WorkerCreate/Get/Observe/**ResolveTrust**/**AwaitReady**/SendPrompt/Restart/Terminate/ObserveCompletion | **多 agent 舰队面**：信任解析与就绪等待是一等工具——4-16 Ralph 迭代产物 |
| Team/Cron 5 | TeamCreate/Delete · CronCreate/Delete/List | 内存 registry，尚无真调度器（PARITY:113） |
| MCP 5 | ListMcpResources/ReadMcpResource/McpAuth/MCP(+RemoteTrigger stub) | 生命周期桥 mcp_tool_bridge.rs 921 行 |
| LSP 1 | LSP（symbols/references/diagnostics/definition/hover） | lsp_client.rs 747 行 registry 级 |
| Git 5 | GitStatus/Diff/Log/Show/Blame | 只读 git 上下文（Raschka 杀手锏①的实现面） |

> 演化读法：4-03 是 40 个（PARITY:149），8 月 55 个——增量几乎全在 Worker/Task/Team/Cron/Git，**"单 agent 工具箱 → agent 舰队调度台"** 的方向一目了然。

## 7. 六组件对表（harness工程手册口径）

| 组件 | 实现锚点 | 备注 |
|---|---|---|
| E 循环引擎 | conversation.rs run_turn | 压缩内嵌循环 |
| T 工具面 | tools/lib.rs 55 spec + execute_tool dispatch | 位置性单文件 |
| C 上下文装配 | prompt.rs SystemPromptBuilder + DYNAMIC_BOUNDARY | 静态段可缓存 |
| S 会话状态 | session.rs Session/fork/heartbeat/workspace_root | 防 phantom completions |
| L 生命周期挂点 | hooks.rs 1151 行（pre/post tool use + failure 变体 + abort signal） | 钩子可改写输入/覆盖权限 |
| V 凭证与审批 | permissions.rs + permission_enforcer.rs + oauth.rs 603 行（PKCE） | hook 覆盖 > 静态规则 |

📌 下一步：03 篇看这套代码是怎么被 agent 自己治理的（PARITY/质量门/.omx 回执）。
