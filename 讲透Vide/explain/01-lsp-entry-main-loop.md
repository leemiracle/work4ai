# 01 · LSP 二进制入口与主循环（src/main.rs + src/global_state.rs）

## 角色定位

vide 的可执行文件本体是一台「LSP 协议状态机」：`src/main.rs` 是进程入口，`src/lib.rs` 里的 `run_server` 完成 LSP initialize 握手，`src/global_state.rs` 及其同名目录下的 `event_loop.rs` 则承担真正的服务循环。三者加起来构成 rust-analyzer 范式中经典的 `main_loop` 层——它不解析 Verilog、不算类型，只负责把三类异步事件流（客户端 LSP 消息、后台任务、VFS 加载）汇成一条串行队列，按序驱动 `GlobalState` 这个庞大的可变状态机。理解这一层，就理解了 vide「编辑器进程」的全部骨架；后面的 Salsa 查询、slang 解析都只是它在事件循环里顺手调用的库。

## 内部结构

`src/main.rs` 极薄：`fn main()` 在 L117，先在 L118-122 兜底设置 `RUST_BACKTRACE=short`，L124 用 clap 解析 `Opt`，L125 `setup_logging(&opt)` 装配 tracing（fmt layer + 可选 `profile-trace` feature 的 Chrome trace，L90-114；L14-27 的默认 filter 把 vide/base_db/hir_def 等全打到 trace 级），L126 一行 `run_server(opt)?` 交棒。

`run_server` 在 `src/lib.rs` L56-154：L59 `Connection::stdio()` 建立 stdio 双通道；L60-68 `connection.initialize_start()` 拿到 initialize 请求；L72-80 解构 `InitializeParams`（root_uri、capabilities、workspace_folders、initialization_options、locale）；L82-106 把 root_uri/workspace_folders 折算成绝对路径（`patch_path_prefix` 处理盘符与符号链接）；L108 `I18n::new(Locale::from_lsp(locale.as_deref()))` 决定服务器文案语言；L110-127 解析 initialization_options 里的用户配置与 snippets，配置有错经 `ShowMessage` 通知而不中断启动；L132-138 组装 `InitializeResult`（capabilities 来自 `config.server_caps()`）；L149 进入 `main_loop::main_loop(config, connection, trace)`。

真正的状态体 `GlobalState` 定义在 `src/global_state.rs` L61-72，由七个字段分组构成（L78-110 的四个子 struct）：

- `ConfigState`（L78-83）：`Arc<Config>`、配置错误、`SourceRootConfig` 与 `SharedProjectConfig`；
- `AnalysisState`（L85-89）：`AnalysisHost`（RootDb 的宿主）、`MemDocs`（打开文档的内存文本）、semantic tokens 缓存；
- `DiagnosticsState`（L91-100）：已发布诊断表与两级修订号、每文件 `DiagnosticFileRevision`；
- `WorkspaceState`（L102-110）：VFS loader 句柄、`Arc<RwLock<(Vfs, IntMap<FileId, LineEnding>)>>`、workspace 列表与 `ExclTask` 型 fetch 任务；
- 另加 `qihe`、`semantic_compiler` 两个外部工具通道与 `TaskState`（线程池）。

`GlobalState::new`（L182-243）在 L187-191 起 vfs loader（L112-125 的 `spawn_vfs_loader` 按编译期 feature 在 `notify` 真实监听与 `dummy` 空实现间切换），L193-197 建 `TaskPool::new_with_threads_num`，L199-201 创建 `AnalysisHost` 并写入诊断配置。

## 外部连接

入口层向内依赖 `vide_lsp_runtime`（LspClient 与 LspRouter，见 L59 `pub(crate) type LspClient = vide_lsp_runtime::Client<GlobalState>`）、`ide::analysis_host::AnalysisHost`（L25）、`project_model::Workspace`（L29）与 `vfs`。向外它只讲 LSP：请求经 `protocol::router()`（`src/global_state/protocol.rs`）分派到 handlers 子目录；诊断以 `Task::Diagnostics` 回流；进度经 `respond::Progress` 上报 `window/workDoneProgress`。`src/global_state/` 下还有 reload.rs（workspace 重载）、process_changes.rs（变更入 db）、snapshot.rs（只读快照）等 14 个子模块在 L1-16 声明，构成「一个 struct + 一屋子 mixin」的组织方式。

## 数据流

主循环本体在 `event_loop.rs`。`pub fn main_loop` 位于 L72-90：L100-102 视配置注册 didSave 动态能力，L104-105 发起首轮 workspace 重载，随后进入 L107-115 的核心 `while let Some(event) = self.next_event(&client_receiver)`；收到 `exit` 通知即 `client.cancel_all()` 返回。

事件枚举 `Event` 在 L22-26：`Lsp(Message)` / `Task(Task)` / `Vfs(vfs_loader::Message)`。调度核心 `next_event`（L146-162）体现了一个精心设计的优先级：L150-155 先 `try_recv` VFS 与任务通道——注释（L147-149）点明「后台状态迁移不能排在无界客户端请求流后面」，VFS ready 消息必须先于 pull-diagnostic 重试提交快照；L157-161 才用 crossbeam `select!` 公平等待三通道。`handle_event`（L164-251）是统一入口：L193-209 分派三类事件（Request 先 `client.register_incoming` 记账）；L213 `process_changes()` 把本轮累积的变更刷进 RootDb；L214-216 兑现延迟的诊断失效；L218-228 在 workspace ready 或状态变化时请求 codeLens/inlayHint 客户端刷新；L233-241 对超过 100ms 的轮次打 warn——主循环的「心跳监测」。

后台任务在 `process_task`（L264-359）消费：`Task::Protocol(ProtocolTask::Response)` 携带 `accepted_effects`（L275-281，响应被客户端接受后才提交副作用，例如 semantic tokens 缓存）；`Task::FetchWorkspace` 的 L287-354 是一段教科书式的过期治理——`finish_workspace_fetch` 返回 `WorkspaceFetchCompletion::Stale`/`CurrentFailure`/`CurrentSuccess` 三态，Stale 直接丢弃结果（L307-314），成功才 `switch_workspaces`。VFS 消息处理 `process_vfs_msg`（L370-430）用 `always!`（L373）断言 config_version 单调，L384-397 的 `accept_vfs_progress` 拒绝过期进度；`process_vfs_files`（L432-474）跳过 mem_docs 管辖的文件（L449，打开的文档以内存文本为准），并在 manifest 变化时触发自动重载（L465-473）。

## 设计决策

**为什么单线程事件循环 + 线程池，而不是每请求一线程？** IDE 语义的全部状态（RootDb、VFS、诊断修订号）都在 `GlobalState` 里，若并发访问需要把每个字段都上锁。vide 沿用 rust-analyzer 的方案：主循环独占可变状态，重活（诊断计算、workspace 发现）扔进 `TaskPool`，算完以 `Task` 消息回队串行合入。`make_snapshot`（global_state.rs L148-179）每次事件后克隆出只读 `GlobalStateSnapshot` 交给后台线程，写读隔离靠 Arc + RwLock 而非修改锁。

**为什么要 `accepted_response_effects`？** 服务器主动请求（如 semantic tokens 缓存提交）的响应可能在到达前请求已被客户端取消；直接提交会污染缓存。event_loop.rs L275-281 把副作用延迟到 `client.respond` 确认成功后执行，main_loop.rs 的测试 `accepted_response_effects_commit_only_after_response_acceptance`（L525-583）锁定了该语义。

**为什么 Event 优先级是 VFS > Task > LSP？** 见 next_event 注释：加载完成这类「就绪门槛」事件若被键入事件饿死，客户端的 pull 诊断会永远拿不到 ready 状态。同理 handle_task/handle_vfs_msg 里的 `try_recv` 循环（L257-259、L365-367）把同批任务合并处理，摊薄每轮固定开销。

## 新人提示

1. 想跟踪「一个 keystroke 到诊断刷新」的路径，按此顺序读：event_loop.rs L107 → L213 `process_changes` → process_changes.rs 的 `analysis_host.apply_change(change)` → 诊断任务重派。
2. `main_loop.rs` 文件名有误导性——它只有 `register_did_save_cap`（L7-42）和大量测试，真正的 `main_loop` 在 event_loop.rs L4 被 re-export。
3. 改 GlobalState 字段时记得同步 `make_snapshot`（global_state.rs L148）与 `DiagnosticsState` 的修订号联动；诊断发布的新鲜度校验（L127-145 `diagnostic_publish_freshness`）对 snapshot_id 一致性有硬 assert。
4. 测试基建可复用：`Connection::memory()`（main_loop.rs L105）让主循环无需编辑器即可单测。
