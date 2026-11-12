# 03-utils 精读手册

> 模块定位：`crates/utils` 是 vide 的**叶子基础库**——不依赖任何其他 vide crate，为 VFS/Salsa 数据库层提供 TextRange/TextSize、LineIndex（offset↔行列换算）、TextEdit（代码编辑代数）、路径类型（ra_ap_paths + camino 再导出）与路径身份（alias+inode 双证据）；为 LSP 层提供取消令牌（CancellationToken）、互斥任务（ExclTask）、带 QoS 分级的线程池（Pool/ThreadIntent）、可取消子进程（process.rs）与 JSON 配置容错解析。大量代码系从 rust-analyzer 移植（`line_index.rs` L1、`thread.rs` L1 均有致谢注释），是全仓被依赖最广的 crate（lib.rs 被 22 文件直接 use，line_index 61 个、text_edit 56 个下游）。

## `crates/utils/Cargo.toml`（34 行）

**作用**：workspace 成员 `utils`（version 0.0.0，description "Utils"，edition 跟 workspace）的依赖清单与 feature 门。

**关键字段**：
- `ra_ap_paths = "0.0.347"`（L11）——rust-analyzer paths crate 的**已发布版**，`paths.rs` 的类型来源（非 vendored）。
- 线程/并发三件套：`crossbeam-channel`（Pool 双通道）、`jod-thread = "0.1.2"`（L15，join-on-drop 线程句柄）、`libc = "0.2.150"`（L17，unix `kill(-pgid)`）。
- 文本三件套：`text-size`（TextSize/TextRange 唯一来源）、`memchr`、`itertools`（TextEdit 的 merge_by/coalesce）。
- 哈希：`rustc-hash`（FxHash）、`nohash-hasher`（IntMap，key 为 u32 免哈希）。
- 其他：`la-arena`（get.rs 的 Arena impl）、`triomphe`（lines.rs 的 Arc）、`dunce`（path_identity 的 Windows canonicalize）、`camino`、`serde`/`serde_json`、`tempfile`、`tracing`、`anyhow`。
- Windows 专属（L28-30）：`winapi-util` + `winapi`（features `jobapi2`/`handleapi`/`winnt`）——process.rs 的 Job Object 与 path_identity.rs 的 file index。
- Features（L32-34）：`camino_serde1 = ["camino/serde1"]`（project-model 开启，见 crates/project-model/Cargo.toml L23）；`test-support = []`（打开 `test_support` 模块，root dev-deps Cargo.toml L164 与 project-model L28 开启）。

**改动的连带影响**：升 `ra_ap_paths` 版本会改变全仓路径类型（vfs/project-model/preproc-expand 共 34 个文件经 paths.rs 消费）；新增依赖会传染到全部 22+ 个 use utils 的编译单元；改 feature 名会破坏 project-model 与根 crate 的构建。

## `crates/utils/src/cancellation.rs`（132 行）

**角色**：手写的父子树状取消令牌（自研，非 tokio-util），是 LSP 请求取消与后台任务中止的唯一原语。

**关键结构与不变量**：
- `CancellationToken`（L11）：`Arc<CancellationState>` 共享态；Clone 即同令牌。
- `CancellationState`（L16）：`cancelled: AtomicBool` + `children: Mutex<Vec<Weak<CancellationState>>>`。不变量：children 持 **Weak**——子令牌可自由 drop，父不阻塞子生命周期；槽位在 `child_token`/`cancel` 时惰性清理（L45 `retain(strong_count>0)`，L61 同）。
- `child_token`（L37）：父已取消 → 子直接取消短路（L39-42）；否则注册 Weak 后**再次检查**（L48-50）关闭"注册与 cancel 并发"的竞态窗口。
- `cancel`（L54）：`swap(true, AcqRel)`，首个取消者负责级联（L55-57 提前返回防重入）；children 先 upgrade 再在锁外递归 cancel（L59-67）。
- `check`（L74）→ `Result<(), CancellationError>`；`CancellationError`（L88）零字段 unit struct，Display "operation cancelled"，impl `Error`。
- Mutex 中毒恢复：`unwrap_or_else(|poison| poison.into_inner())`（L79）——取消路径绝不能因锁中毒卡死。

**公开 API**：`CancellationToken::{new, child_token, cancel, is_cancelled, check}`、`CancellationError`。

**依赖/被依赖**：依赖无（纯 std）。被依赖：`crates/ide/src/analysis.rs`、`ide/src/formatting.rs`、`utils/src/process.rs`、`vide-lsp-runtime/src/client.rs`（L13-14：`lifecycle_cancel` + `request_cancellations: Mutex<HashMap<RequestId, CancellationToken>>` 按 LSP 请求 ID 建令牌）、`vide-lsp-runtime/src/router.rs`（L50 snapshot 签名携带）、`src/global_state.rs`（L156 `cancellation` 字段）。

**改动影响面**：语义改动直接波及 LSP `$/cancelRequest`（client.rs）、格式化器中止（formatting.rs）与 workspace 加载取消；`process.rs` 的轮询取消也依赖它。内置测试（L100-132）`parent_cancellation_reaches_child_tokens`、`child_created_after_parent_cancellation_is_cancelled`、`child_creation_removes_dropped_child_slots` 会先红。

**集成点**：长循环里周期 `check()?`；新后台任务用 `child_token()` 派生作用域令牌，父令牌取消时整棵子树联动。

## `crates/utils/src/excl_task.rs`（46 行）

**角色**："同一时刻至多一个在飞"的长任务互斥器（workspace 加载/重载专用，非通用并发原语）。

**关键结构与不变量**：
- `ExclTask<Output, Cause = String>`（L4）：`requested: Option<Cause>`（单槽 pending，新请求覆盖旧请求）+ `in_process: bool` + `last_result: Option<Output>`。
- 不变量：`in_process == true` 期间 `should_start` 恒返回 None（L22-24）——飞行中到达的 request 留存到本轮 `complete` 之后；`complete`（L29）`assert!(self.in_process)`（L30）——必须与 should_start 严格配对，否则 panic。

**公开 API**：`request(Cause)`（L17）、`should_start() -> Option<Cause>`（L21，原子地取走请求并置 in_process）、`complete(Option<Output>)`（L29）、`last_op_result()`（L35）、`in_process()`（L39）、`has_op_requested()`（L43）。

**依赖/被依赖**：依赖无。被依赖：`src/global_state.rs` L107-108 `fetch_workspaces_task: ExclTask<(Arc<Vec<Workspace>>, Vec<anyhow::Error>), WorkspaceFetchCause>`——由 `reload.rs`（L114 request / L124 should_start / L130 last_op_result）、`event_loop.rs`（L308/317/330 complete）与 `main_loop.rs`（L673 等 5 处）共同驱动。

**改动影响面**：这是 workspace fetch 合并（debounce）语义的核心：若允许并发 in_process，`main_loop.rs` 中的时序测试（L742-803 的 first/second should_start 断言）与 `handlers/notification/workspace.rs` L154 的 `has_op_requested` 断言全部失效。

**集成点**：任何"用户可反复触发、但结果只需最新一份"的 IO 型任务（项目重载、索引重建）直接套用此三段式协议（request → should_start → complete）。

## `crates/utils/src/get.rs`（21 行）

**角色**：索引式泛型抽象 `Get`/`GetRef`——把 "用 Id 查容器" 从具体 Arena/Map 类型上解耦，让 hir-def 的 id→实体查询可泛型化、可测试替身。

**关键结构与不变量**：
- `Get<A>`（L3）：`type Output` + `fn get(&self, a: A) -> Self::Output`（**按值**返回，`Option<T>` 场景专用——查不到就是 None 而非 panic）。
- `GetRef<A>`（L9）：同形但返回 `&Self::Output`（**必须存在**，越界 panic 语义）。
- 本文件唯一 impl：`impl<T> GetRef<Idx<T>> for Arena<T>`（L15）——la-arena 到 trait 的桥。

**公开 API**：两个 trait + 上述 Arena impl。

**依赖/被依赖**：依赖 la-arena。被依赖（10 文件）：真正的 impl 群在 hir-def——`crates/hir-def/src/lib.rs` L60/L75 的宏为容器批量生成 `GetRef`/`Get` impl；`module/port.rs` L148-249 手写 Ports/PortSrcs 六个 impl；`source_map.rs` L108-131 以 `T::SourceMap: Get<Id, Output = Option<SourceAstId>>` 约束写泛型 source 查询；`def_id.rs` L186、`hir-ty/src/infer.rs` L20、`ide/src/folding_ranges.rs` L464-467（M: Get + GetRef 多重约束）。

**改动影响面**：动 trait 签名（如加方法、改关联类型名）会同时打破 hir-def 的宏、port.rs 的手写 impl 与全部泛型约束点——hir-def 编译即红。

**集成点**：新 ID 类型想进入泛型查询体系时，给持有容器 `impl Get<NewId, Output = ...>` 即可（宏或手写均可），无需改消费方。

## `crates/utils/src/json.rs`（33 行）

**角色**：LSP 配置反序列化的两个容错助手（ra 风格）：整体失败给上下文的 `from_json`，逐字段失败降级默认值的 `get_field`。

**关键结构与不变量**：
- `from_json<T: DeserializeOwned>`（L3）：克隆 Value 反序列化，失败时 `anyhow::format_err!("Failed to deserialize {name}: {e}; {json}")`（L8）——错误里**带原始 JSON**，方便日志定位。
- `get_field<T>`（L11）：字段名→层级 JSON pointer 的约定映射：`field.replace('_', "/")` 再前插 `/`（L19-20），即 `a_b` 查 `/a/b` 嵌套路径（注释 L17-18 说明动机：VS Code 会预填默认值而非发空对象，先查"别名"路径）。
  不变量：单字段反序列化失败**不中断**——`tracing::warn!` + 压入 `error_sink: &mut Vec<(String, serde_json::Error)>`（L25-27）+ 回落 `default()` 闭包（L32）；`pointer_mut` + `it.take()`（L21-23）把值从 Value 树里**拿走**，防止重复消费。

**公开 API**：`from_json<T>`、`get_field<T>`。

**依赖/被依赖**：依赖 serde/serde_json/anyhow/tracing。被依赖：`src/browser.rs`（L101 用 `from_json::<InitializeParams>` 解析初始化参数）、`src/config.rs`、`src/config/user_config.rs`、`src/global_state/qihe.rs`。

**改动影响面**：`get_field` 的下划线→层级指针约定是**所有用户配置字段名的隐式契约**，改动等于改配置 schema；`from_json` 的错误格式被 LSP 日志测试快照引用。

**集成点**：新增客户端配置项时，在 user_config.rs 用 `get_field(json, sink, "section_field", || default)` 接入，天然获得"部分坏配置不拖垮启动"的性质。

## `crates/utils/src/lib.rs`（17 行）

**角色**：crate 门面——16 个 pub mod + 1 个条件编译模块，无任何自有代码。

**关键结构与不变量**：模块表即全部内容；唯一逻辑在 L11-12：`#[cfg(any(test, feature = "test-support"))] pub mod test_support;`——`test_support` 只在测试或显式 feature 下编译进公共 API。

**公开 API**：`utils::cancellation / excl_task / get / json / line_index / lines / panic_context / path_identity / paths / process / test_support(条件) / text_edit / thread / uimpl / uniq_vec / utry`。

**依赖/被依赖**：依赖 = 16 个子模块（图谱出边）。被依赖 = 22 个文件直接 use `utils::{...}`（hir-def 5、hir-semantics 1、ide 1、src/global_state 13、src/lsp_ext 2），另有大量文件经 `utils::line_index` 等子路径单独引用。

**改动影响面**：改 cfg 门（如把 test-support 改成默认开）会改变所有下游的编译面；删/改名模块直接编译错误。

**集成点**：新 util 模块的唯一注册点；注意 `#[macro_export]` 宏（uimpl/utry）在 crate root 命名空间，用 `$crate::` 引用。

## `crates/utils/src/line_index.rs`（521 行）

**角色**：全仓 offset↔(line, col) 换算的唯一实现（移植自 rust-analyzer，源头是 rustc_span），并**再导出 `TextRange`/`TextSize`**（L6）——这两个类型是整个 vide 的位置坐标系统一来源。

**关键结构与不变量**：
- `LineCol`（L16）：零基 line + 零基 **UTF-8 字节** col；`WideEncoding`（L25，`#[non_exhaustive]`，Utf16/Utf32，`measure` L31）；`WideLineCol`（L41，刻意与 LineCol 分型防混用）；私有 `WideChar`（L49）：行内非 ASCII 区间 [start,end)，`wide_len`（L63）：UTF-8 4 字节字符在 UTF-16 占 2 单元、其余 1；UTF-32 恒 1。
- `LineIndex`（L78）：`newlines: Box<[TextSize]>` 存**每行行首 offset**（首行恒 0 不存，即换行符位置+1）；`line_wide_chars: IntMap<u32, Box<[WideChar]>>` 只记含非 ASCII 的行；`len`。不变量：newlines 严格递增；SIMD/标量两条构造路径产物必须等价。
- `try_line_col`（L103）：`partition_point(|&it| it <= offset)`（L107）定位行；offset 落在多字节字符内部时返回 None（L111-116：col 不得落在任何 WideChar 区间内部）。
- `offset`（L120）：LineCol→TextSize（不校验 col 合法性）；`to_wide`/`to_utf8`（L133/L151）：基于该行 WideChar 列表做 col 的编码换算，`checked_sub/add` 防下溢，遇首个位于目标之后的 WideChar 即 break（L141-143）。
- `range_for_line`（L168）、`line_for_offset`（L176）、`lines(range)`（L187，按换行切区间并滤空）、`text_len`（L201）、`lines_len`（L207，= newlines.len()+1）、`line_ranges`（L212）。
- `analyze_source_file`（L229，注释注明改编自 rustc_span）：`assert!(src.len() < !0u32)`（L230）——TextSize 32 位上限；按架构 dispatch：x86/x86_64 检测 SSE2（L246）、aarch64 检测 NEON（L262）、其余走 generic（L462）。
- SIMD 路径（`analyze_source_file_sse2` L278 / `analyze_source_file_neon` L384）：16 字节 chunk，先用 `cmplt_epi8(0)`/`vcltzq_s8` 探测多字节（L308/L411）；纯 ASCII chunk 走向量化换行扫描（mask 逐位提取，SSE2 记录 offset 用 `chunk_index*CHUNK+1` 基准 L323，NEON 用 4-bit nibble mask 除以 4 取 index L428-431）；混合 chunk 回退 generic 只扫该 chunk，`intra_chunk_offset`（L298）携带跨 chunk 多字节字符的溢出量。
- `analyze_source_file_generic`（L475）：字节循环；遇 `\n` 记 `i+1`（L497）；≥127 的字节走 char 解码，len>1 才记 WideChar（L510-514），行内坐标 = 绝对 offset − `lines.last()`（L507-508）；**返回值 `i - scan_len`**（L520）= 已读超界字节数，供 SIMD 路径接续。

**公开 API**：`LineIndex::{new, try_line_col, offset, to_wide, to_utf8, range_for_line, line_for_offset, lines, text_len, lines_len, line_ranges}`、`LineCol/WideLineCol/WideEncoding`、`covering_range`（L8）、re-export `TextRange/TextSize`。

**依赖/被依赖**：依赖 nohash-hasher、text-size。被依赖（61 文件，全仓最广）：ide 全部 feature（经 `ide/db/line_index_db.rs` 做成 salsa query）、syntax（ptr.rs/has_text_range.rs 的 AstPtr 区间）、preproc-expand 宏展开 source map、completion context、`src/lsp_ext/from_proto.rs` L31-32（按 PositionEncoding 分支调 to_wide/to_utf8 做协议坐标转换）。

**改动影响面**：改换行语义/col 编码会破坏**每一个** LSP range 类功能（诊断、跳转、补全、重命名）与 snapshot 测试；`TextSize` 的 re-export 地位意味着改 `pub use` 行会波及 60+ 文件的 use 路径。内置测试 `line_len_test`（L219-226）只覆盖行数，深度行为靠下游 ide 测试兜底。

**集成点**：`LineIndex::new(text)` 后任意 offset/LineCol/WideLineCol 三域互转；`lines(range)` 是折叠范围/逐行处理的现成迭代器；做新协议编码（如 UTF-32）只需扩 `WideEncoding`（已 `#[non_exhaustive]` 预留）。

## `crates/utils/src/lines.rs`（32 行）

**角色**：文档级行信息三件套 `PositionEncoding`/`LineEnding`/`LineInfo`——把 LineIndex、换行风格、客户端坐标编码捆成一个可传递对象。

**关键结构与不变量**：
- `PositionEncoding`（L6，Copy）：`Utf8` 或 `Wide(WideEncoding)`——LSP `positionEncoding` 协商结果（`src/config/caps.rs` L229-231 决定：客户端不认 utf-8 时回落 Utf32/Utf16）。
- `LineEnding`（L11）：`Unix`/`Dos` 二值；`normalize(src: String) -> (String, LineEnding)`（L19）：`contains("\r\n")` 则全量替换为 `\n` 并标 Dos，否则原样 Unix。不变量：**只处理 \r\n，孤立 \r 不动**；返回值是"归一后文本 + 原风格"，消费方负责在输出时还原。
- `LineInfo`（L28）：`index: Arc<LineIndex>`（**triomphe::Arc**，L1，非 std——cheap clone 且无原子弱计数）、`ending`、`encoding`——Analysis API 的每文档参数（`ide/src/analysis.rs` L251/L264 以 `&LineInfo` 收参）。

**公开 API**：三个类型 + `LineEnding::normalize`。

**依赖/被依赖**：依赖 line_index（triomphe）。被依赖（8 文件）：`global_state/handlers/notification/text_changes.rs` L17/L42（didOpen/didChange 入口先 normalize）、`process_changes.rs` L257（VFS 写回）、`ide/formatting.rs` L85（格式化输出 normalize 后再按原 ending 还原）、`config/caps.rs`、`ide/analysis.rs`、`src/global_state.rs`。

**改动影响面**：`LineEnding` 若扩三值（如 OldMac 孤立 \r），formatting.rs 的"normalize→格式化→还原"往返与 text_changes 的增量 diff 都要跟着改；PositionEncoding 加变体需同步 `lsp_ext/from_proto.rs`。

**集成点**：任何新入口拿到编辑器文本，第一行代码应是 `LineEnding::normalize`，产出 LineInfo 后传给 Analysis——这是文档进入 vide 的标准入队姿势。

## `crates/utils/src/panic_context.rs`（45 行）

**角色**：RAII 式 panic 上下文栈——panic 时在默认 hook 前打印"当前执行到哪一层"，用于长流水线的崩溃定位。

**关键结构与不变量**：
- `enter(context: String) -> PanicContext`（L3）：`Once` 保证 hook 只装一次（L4-5），随后向 thread-local `Vec<String>` 压栈。
- Hook（L17-31，`PanicContext::init`）：`take_hook()` 取默认 hook → 包一层：栈非空则 `eprintln!("Panic context:")` 逐帧打印 `> {frame}` → 再调默认 hook。不变量：**push/pop 严格配对**——`Drop`（L34-38）`assert!(ctx.pop().is_some())`，中途 panic 展开也不会留下脏栈帧。
- `with_ctx`（L40）：`thread_local!` + `RefCell<Vec<String>>`（const init），上下文按线程隔离。

**公开 API**：`enter(String)`、`PanicContext`（`#[must_use]` L11，丢弃即丢上下文）。

**依赖/被依赖**：依赖无。被依赖：**当前仓内仅 lib.rs 再导出，无外部消费者**（全仓 grep 实证）——功能就绪但休眠的基础设施。

**改动影响面**：零外部破坏面（无消费者）；但 hook 是全局单例，未来若多模块竞争安装 panic hook 需注意顺序。

**集成点**：二次开发时给 index/lower/expand 等易崩阶段包一层 `let _ctx = utils::panic_context::enter(format!("lowering {file:?}"))`，即可在崩溃日志中自动获得定位帧——这是本文件对集成者的全部价值。

## `crates/utils/src/path_identity.rs`（284 行）

**角色**：路径身份系统——"拼写别名"（raw + canonical）与"文件对象身份"（dev/ino 或 volume/index）双证据模型，解决 Verilog include 解析里 symlink/大小写/Windows 前缀导致的同文件异名问题。

**关键结构与不变量**：
- `PathKey(String)`（L9）：归一化拼写键（newtype 不透明，只经 `new`/`from_abs_path` 构造）。`normalize_path_key`（L198）三步：`\`→`/`（L199）→ 剥 `//?/UNC/`→`//` 与 `//?/` 前缀（L201-205，注意是在已归一化的斜杠串上匹配）→ 盘符大写（L207-210）。不变量：Key 只做**拼写**归一，不做 IO、不做大小写折叠（unix 下 `A.sv`≠`a.sv`）。
- `path_alias_paths`（L40）：恒以 raw 拼写打头（L41，"唯一无需 IO 就能保住的身份"，doc L26-39），canonical（dunce）仅在 OS 能证明且不同时追加（L43-47）；**文件不存在时不发明拼写**（测试 L243-250 钉死）。
- `FileIdentityKey`（L61，Copy）：平台 repr `Unix{dev,ino}`（L66）/`Windows{volume,index}`（L68），经 `std::fs::metadata` / `winapi_util::file::information` 计算（L176-191）；doc L58-59 明确"不像 same_file::Handle 那样持有打开句柄"。
- `PathIdentityIndex<T: Copy>`（L87）：`aliases: FxHashMap<PathKey,T>` + `identities: FxHashMap<FileIdentityKey,T>`。`insert_path`（L105）：所有 alias 后插覆盖先插（doc L99-104——碰撞按插入序可见，不猜哪个更"对"）+ identity；`get`（L112）字符串入口 → `get_path`（L117）三级查找：raw alias → canonical alias → **文件身份**（hard link / symlink 解析的最后防线，测试 L263-274 用 hardlink 钉死）。
- `PathIdentitySet`（L145）：同证据模型的去重集合；`insert_path`（L153）返回 `is_new` = 所有 alias 未见 **且** identity 未见（L156-157，`is_none_or` 兼容无 identity 场景）。
- `canonical_path`（L168）：`dunce::canonicalize`（Windows `\\?\` 长路径平滑）→ `abs_path_buf_from_path_buf`。

**公开 API**：`PathKey::{new, from_abs_path, as_str}`、`path_alias_paths`、`path_alias_keys`、`FileIdentityKey::from_path`、`PathIdentityIndex<T>::{insert_path, get, get_path}`、`PathIdentitySet::insert_path`。

**依赖/被依赖**：依赖 paths（AbsPath/AbsPathBuf）、rustc-hash、dunce、winapi-util(Windows)。被依赖：`preproc-expand/src/db.rs` L87（`path_file_ids: PathIdentityIndex<FileId>` —— **include 查找的 FileId 解析表**）、`preproc-expand/src/compilation_plan.rs` L157（seen_files 去重）、`preproc-expand/src/source_db.rs`、`project-model/src/lib.rs`。

**改动影响面**：normalize 规则一变（如加大小写不敏感），全仓 include/macro 文件解析的 FileId 归并全变——preproc 的 snapshot 测试会大面积红；FileIdentityKey repr 改动使跨进程缓存身份失效。

**集成点**：`PathIdentityIndex<FileId>` 是把"任意路径字符串"映射到 VFS FileId 的标准入口（db.rs 已示范）；PathIdentitySet 适合文件遍历去重（project-model 可用）。

## `crates/utils/src/paths.rs`（76 行）

**角色**：路径类型的**再导出层** + 4 个 Vide 特有助手——上游换成 `ra_ap_paths` 0.0.347 后的适配壳（头注释 L1-17 记载迁移理由：旧 vendored 版 `RelPath(Path)` 布局使 `new_unchecked` 成为 transmute UB，上游已修复并补了 `AbsPath::as_str`）。

**关键结构与不变量**：
- L21-22：`pub use camino::{self, *}`（Utf8Path/Utf8PathBuf/Utf8Component 等）+ `pub use ra_ap_paths::{AbsPath, AbsPathBuf, RelPath, RelPathBuf}`。不变量：**AbsPath/AbsPathBuf 构造即校验绝对性**（内部 try_from Utf8），全仓路径安全性的根。
- `abs_path_buf_from_path_buf`（L27）：`PathBuf → Utf8PathBuf → AbsPathBuf` 双重 fallible，None 表示非绝对或非 UTF-8；doc L24-26。孤儿规则挡住 `TryFrom<PathBuf>`（注释 L34-35），故为自由函数。
- `try_abs_path_buf_from_path_buf`（L36）：`Result<AbsPathBuf, PathBuf>` 变体，Err 时**原样奉还 PathBuf**（L38-40，损失最小化）。
- `patch_path_prefix`（L48）：Windows 盘符大写（Disk L56 / VerbatimDisk L57 两种前缀），动机注释 L44-47——VS Code 上报 `c:\` 而规范化路径是 `C:\`，直接比较会 miss；非 Windows 原样返回（L67-69）。
- `sort_and_remove_subfolders`（L73）：先 `sort()` 再 `dedup_by(|a, b| a.starts_with(b))`——排序后子目录紧邻其父之后，被前缀匹配删除，**保留最外层目录**；project-model 用它合并 include 目录列表。

**公开 API**：上述 4 函数 + camino/ra_ap_paths 全量再导出。

**依赖/被依赖**：依赖 camino、ra_ap_paths、std。被依赖（34 文件，全仓第二广）：vfs 全家（`vfs/lib.rs` L30 直接 `pub use utils::paths::{AbsPath, AbsPathBuf}` 对外转卖；vfs_path.rs/file_set.rs/loader.rs/notify.rs/path_glob.rs）、project-model（含 `Utf8Component`/`sort_and_remove_subfolders`，lib.rs L18/L82/L94）、preproc-expand、workspace-model、base-db、hir-def、src 根（`src/lib.rs` L12/84/101 用 patch_path_prefix 规整客户端路径）。

**改动影响面**：本文件是**路径类型的单点替换层**——动 L21-22 的 use 等于改写全仓路径 API；4 个助手的语义变化影响 VFS 装载、workspace 发现与 preproc 编译计划。

**集成点**：拿到 OS `PathBuf` 想进 vide 体系的唯一正门是 `try_abs_path_buf_from_path_buf`；与客户端/规范化路径比对前先过 `patch_path_prefix`。

## `crates/utils/src/process.rs`（406 行）

**角色**：可取消子进程工具——跨平台"杀整棵进程树"（Windows Job Object / unix 进程组）+ 免管道死锁的 stdio 泵，服务于外部格式化器等长命子进程。

**关键结构与不变量**：
- `configure_process_tree`（L12）：unix 在 **spawn 前**调 `command.process_group(0)`（L144）让子进程自立 pgid——`kill(-pgid)` 的前提；Windows no-op（L57，job 在 attach 时建）。
- `wait_with_cancellation`（L16）：10ms 轮询循环（L29 `thread::sleep(Duration::from_millis(10))`）；取消时先 `process_tree.kill`（杀树）再 `child.wait()`（收尸防僵尸）后返 `Err(CancellationError)`（L19-23）；正常路径 `try_wait` 非阻塞取状态（L25）。
- Windows `imp`（L34-134）：`JobHandle::for_child`（L84）三步建 Job：`CreateJobObjectW` → `SetInformationJobObject` 置 `JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE`（L92）→ `AssignProcessToJobObject`（L110）；任一步失败 `tracing::debug!` 并降级为仅 `child.kill()`（L73-80）；`terminate` 走 `TerminateJobObject`（L123）；`Drop` CloseHandle（L127-133）。
- unix `imp`（L136-162）：`kill` = `libc::kill(-(child.id() as pid_t), SIGKILL)`（L155-157，负 pid 即整组）+ `child.kill()` 兜底。第三平台（L164-181）纯降级。
- `wait_with_stdio_and_cancellation`（L198，私有核心；公共入口 `wait_with_output_and_cancellation` L183 / `wait_with_input_and_output_and_cancellation` L190）：**先把 stdin writer（L203-209）与 stdout/stderr reader（L210-211）各拆线程**（`read_to_end` L231 / `write_all` L242）再等待——否则管道写满即死锁；关键不变量（L224-226）：**stdin 写错误仅在子进程 exit success 时上报**——崩溃子进程的 EPIPE 不是调用者的错。
- 测试（L270-406）：`cancellation_kills_child_process`（预取消）、`cancellation_kills_grandchild_process`（孙进程写 marker 文件的编舞：1s/1.5s/2.2s sleep 链，断言 marker 未出现 = 树杀成功，L288-328）、`cancellation_kills_process_while_input_writer_is_active`（1MiB stdin 阻塞中取消，L330-348）；平台分叉的 powershell/sh 脚本工厂（L350-405）。

**公开 API**：`configure_process_tree(&mut Command)`、`wait_with_cancellation(&mut Child, &CancellationToken) -> Result<ExitStatus>`、`wait_with_output_and_cancellation`、`wait_with_input_and_output_and_cancellation`。

**依赖/被依赖**：依赖 cancellation、libc(unix)、winapi(win)、anyhow、tempfile(test)。被依赖：**`ide/formatting.rs` L22（唯一生产消费者**——外部格式化子进程的启动与取消）。

**改动影响面**：删 `process_group(0)` 会让 unix 下孙进程逃逸取消（grandchild 测试即红）；改 10ms 轮询影响取消延迟；formatting 是唯一下游，破坏面集中。

**集成点**：新增任何外部工具调用（linter、linter、编译器调用）套此三段式：`configure_process_tree` → `spawn` → `wait_with_*_cancellation`，自带整树取消与管道安全。

## `crates/utils/src/test_support.rs`（103 行）

**角色**：测试目录设施 `TestDir`——tempfile 目录的 AbsPathBuf 包装，测试夹具的文件系统脚手架（cfg 门控：`any(test, feature="test-support")`，lib.rs L11-12）。

**关键结构与不变量**：
- `TestDir`（L6）：`_temp_dir: tempfile::TempDir`（所有权字段，Drop 自动递归删除）+ `path: AbsPathBuf`。不变量：只要 TestDir 被 drop，目录连同内容消失（测试 L90-102 钉死）；`into_path`（L43）是唯一"故意泄漏"出口——`self._temp_dir.keep()`（L45）解除删除语义。
- `new(name)`（L12）/ `new_in(parent, name)`（L23）：前缀 `vide-{name}-` 的 tempdir，失败 panic（测试代码不做错误传播）；`from_temp_dir`（L34）/ `into_temp_dir`（L39）双向桥接 tempfile 生态。
- `close(self)`（L49）：显式删除，失败 panic（带路径，L51-53）。
- `join`（L60）= `absolutize`（paths 层）；`create_dir_all`（L64）；`write`（L72）：**自动建父目录**（L74-78）+ 写文件 + 返回 AbsPathBuf——一行铺一个 fixture 文件树。

**公开 API**：`TestDir::{new, new_in, from_temp_dir, into_temp_dir, into_path, close, path, join, create_dir_all, write}`。

**依赖/被依赖**：依赖 tempfile、paths。被依赖（8 文件，均测试场景）：`ide/diagnostics.rs`、`ide/macro_hover_tests.rs`、`ide/verilog_2005.rs`、`src/browser.rs`、`src/tests.rs`、`global_state/handlers/notification/{text_document,workspace}.rs`。

**改动影响面**：属测试基建，影响集中在下游测试的可写性；改 `write` 语义（如不再建父目录）会破坏所有多级 fixture。

**集成点**：新 crate 要用就在其 Cargo.toml 加 `utils = { workspace = true, features = ["test-support"] }`（dev-dependencies），随即获得磁盘级测试能力（对 preproc/vfs 这类真文件系统逻辑必不可少）。

## `crates/utils/src/text_edit.rs`（228 行）

**角色**：文本编辑代数——`TextEdit`/`TextEditItem` 是 rename、code action、格式化、quickfix 等一切"改文档"功能的统一载体（ra 移植 + coalesce 扩展）。

**关键结构与不变量**：
- `TextEditItem`（L10）：`ins: String` + `del: TextRange`，del 引用**原文** offset（L12）；insert/delete/replace 三个构造器（L17-27）统一归约到 replace；注释 L8：item 间不得重叠。
- `TextEdit`（L37）：核心不变量**"disjoint and sorted by `delete`"**（L38-39）——由构造路径强制：
  - `TextEditBuilder::finish`（L187）/ `FromIterator`（L156）：`sort_and_check_disjoint`（L203，sort_by_key (start,end) 后 `check_all_disjoint` L208：相邻 `l.del.end() <= r.del.start() || l == r`——**完全相同的重复项被容忍**，这是 union 去重的窗口）→ `coalsece_changes`（L215，函数名 typo 原样保留）：`a.del.end() == b.del.start()` 的相邻项合并（ins 拼接、del 拓宽，L218-225）。
- `apply`（L77）：0/1 项快路径（L78-87）；多项先算 `change_len`（净长度变化）与 `max_change_len` 用于**一次性 reserve**（L89-100），再**倒序** apply（L102-104，倒序保证未处理区间的 offset 不失效）；收尾 `assert_eq!(TextSize::of(&*text), change_len)`（L106）——长度守恒自检。
- `union`（L109）：itertools `merge_by` 按 `del.start` 归并两编辑；任一重叠返回 `Err(other)` 原物奉还（L112-114）；去重规则（L116-117 注释+代码）：**只去重删除/替换（非空 del），insert 全保留**（同 offset 两个 insert 语义上都有效）。
- `apply_to_offset`（L122）：把原文 offset 映射到编辑后文本的 offset；落入删除区间内返回 None（L128-130）；遇 `del.start() >= offset` 即 break（L125-127，后续编辑不影响更早 offset）。
- `TextEditBuilder::invalidates_offset`（L194）：`contains_inclusive` 判断 offset 是否会被改动吞掉。

**公开 API**：`TextEditItem::{insert, delete, replace, apply_on}`、`TextEdit::{builder, insert, delete, replace, len, is_empty, iter, apply, union, apply_to_offset}` + IntoIterator（值/引用两版 L138-154）+ `FromIterator<TextEditItem>`、`TextEditBuilder::{replace, delete, insert, finish, is_empty, invalidates_offset}`、re-export `TextRange/TextSize`（L5，源自 line_index）。

**依赖/被依赖**：依赖 line_index（TextRange/TextSize）、itertools。被依赖（**56 文件，全仓第三广**）：ide code_action 全家（engine/collector/edits + 12 个 handler）、rename、formatting、semantic_tokens、inlay_hint、completion engine、signature_help、source_change.rs（SourceChange 的原子单位）、以及 hir-def 的 diagnostics/lower/source_map（构造诊断 fix）。

**改动影响面**：disjoint 不变量与倒序 apply 是正确性根基——放松校验会让所有 code action 产出错乱文本；`ide/code_action/tests.rs` 与 completion engine 的 snapshot 测试是第一道防线；TextRange re-export 地位同 line_index。

**集成点**：写新 code action 直接 `TextEdit::builder()` 撞 replace/insert 后 finish（自动排序+合并+校验）；需要"两个来源的编辑合流"时用 `union` 并处理 Err 重叠；`apply_to_offset` 用于把用户光标/选区同步到编辑后坐标。

## `crates/utils/src/thread.rs`（578 行）

**角色**：线程基础设施（ra 移植+扩展）：`Pool`（双通道、QoS 感知、防饿死的任务池）、`Builder`/`JoinHandle`（jod-thread 封装，可选 detach）、`ThreadIntent`（线程用途分级）。是 LSP 主循环任务调度与 QoS 管理的核心。

**关键结构与不变量**：
- `Pool`（L7）：字段顺序即 Drop 顺序的**不变量**（注释 L9-13）：`job_senders` 必须先于 `_handles` drop——通道先关，worker 的 recv 循环才能退出，随后 join 才不卡死。
- `Pool::new(threads)`（L35）：每 worker **8 MiB 栈**（L36 const STACK_SIZE）、名 "Worker"；spawn 失败仅 `tracing::error!` 后 continue（L68-71）——池容错降级不 panic；worker 主循环（L56-65）：recv → job 的 intent 与当前不符则热切换 QoS（L59-62）→ 执行。
- 调度核心 `JobReceivers::recv`（L126）+ `LATENCY_BURST = 3`（L175）四步：① `latency_budget > 0` 且 latency 队列有货 → 取之并扣减（L127-132）；② worker 队列有货 → 取之并**重置 budget**（L134-137）；③ latency 有货 → 取之，budget 置 burst-1（L139-142）；④ 双空则 `select!` 阻塞（L144-171）。**防饿死不变量：latency 敏感任务连跑至多 3 个后，pending 的 worker 任务必得让路**（测试 L544-577 `worker_jobs_make_progress_under_latency_sensitive_load` 钉死）。`Clone for JobReceivers`（L115）给每个 worker 线程发**全新 budget**（L120）。
- `Pool::spawn(intent, f)`（L80）：emscripten 内联执行（L84-88）；debug 构建包一层 `intent.assert_is_used_on_current_thread()`（L91-95）防 QoS 被中途篡改；池已关则**内联执行并 debug 日志**（L98-102）——任务永不丢失。
- `JobSenders::send`（L107）：按 intent 路由到 worker/latency_sensitive 两条 unbounded channel（L39-40）。
- 自由函数 `spawn`（L178）：`Builder::new(intent).spawn(f).expect(...)`——独立建线程版（clippy expect_used 特赦）。
- `Builder`（L187）：包 `jod_thread::Builder`（join-on-drop 语义），`name`/`stack_size`/`allow_leak`（L198-208）；`spawn`（L210）在**线程体内**先 `intent.apply_to_current_thread()` 再跑 f（L216-218）。
- `JoinHandle<T>`（L225）：`join`（L232）；`Drop`（L237）当 `allow_leak == true` 时 `detach()`（L243-245）——通知线程等"必须活得比持有者久"的场景（vfs/notify.rs 即此用法）。
- `ThreadIntent`（L257）：`Worker < LatencySensitive`（L256 注释要求 Ord 顺序恒为优先级升序）；`apply_to_current_thread`/`assert_is_used_on_current_thread` 刻意 `pub(super)`（L263-265 注释：**只允许在建线程时或经 Pool 设置 QoS**，不开放给消费者）。
- QoS 平台层：Apple XNU（L297-474）`pthread_set_qos_class_self_np`，映射 Worker→`Utility`、LatencySensitive→`UserInitiated`（L468-473）；EPERM（线程已退出 QoS 体系）直接 panic（L399-407，"只用 QoS API"不变量）；`QOS_CLASS_DEFAULT → None`（从未设置）。非 Apple（L477-497）`IS_QOS_AVAILABLE = false` 全 no-op（L476 TODO：Windows QoS）。
- 测试（L499-578）：`latency_sensitive_jobs_are_not_blocked_by_worker_fifo`（单 worker 塞满 worker 任务后，latency 任务仍**第一个**完成）。

**公开 API**：`Pool::{new, spawn}`、`spawn`（自由函数）、`Builder::{new, name, stack_size, allow_leak, spawn}`、`JoinHandle::join`、`ThreadIntent`。

**依赖/被依赖**：依赖 crossbeam-channel、jod-thread、libc(Apple)、tracing。被依赖：`src/global_state/task.rs` L4/L80（**TaskPool = Pool::new(main_loop_threads_num)**，主循环任务引擎）、`src/global_state/protocol.rs` L163、`ide/analysis_host.rs` L107/L119（reader/updater 线程经自由函数 spawn）、`crates/vfs/src/notify.rs` L37/L50（notify 线程：Builder + Worker intent + allow_leak JoinHandle）、`vide-lsp-runtime/src/router.rs` L11/23-28（handler 声明 ThreadIntent：LatencySensitive 用于 prime 请求路由、Worker 用于次要）。

**改动影响面**：LATENCY_BURST/调度顺序一动，LSP 请求延迟特性全变（router 的 intent 声明全部重排语义）；Pool Drop 顺序不变量被破坏会挂死退出流程；两个内置调度测试是守护网。

**集成点**：新 LSP handler 在 router 上声明 `ThreadIntent::LatencySensitive`（用户阻塞型）或 `Worker`（后台型）即自动获得 QoS 与防饿死调度；长命后台线程用 `Builder::new(intent).allow_leak(true)`（notify.rs 范式）。

## `crates/utils/src/uimpl.rs`（43 行）

**角色**：两个过程宏替代品（声明宏）——为 enum 批量生成 `From` impl，消除 hir-def AST 包装层的样板。

**关键结构与不变量**：
- `impl_from!`（L2）：递归展开两种臂——`Enum => Variant`（variant 名即类型名，L2-11）与 `Enum => Variant(Ty)`（显式类型，L13-21）；空臂终止（L23）。不变量：**variant 与类型同名或显式标注二选一**，展开是纯机械的 `From<Ty> for Enum`。
- `define_enum_deriving_from!`（L27）：一体两面——直接**定义 enum**（每个 variant 是单字段 tuple，L28-34 / 36-42 两种体）并连锁调 `impl_from!`。attr 参数原样透传（`#[$attr:meta]`），支持 derive/文档属性。

**公开 API**：两个 `#[macro_export]` 宏（crate root 命名空间，可用 `$crate::` 引用）。

**依赖/被依赖**：依赖无（macro_rules）。被依赖（图谱+grep）：`hir-def/src/block.rs` L4、`declaration.rs` L15、`expr/declarator.rs` L25、`module/specify.rs` L16（define_enum_deriving_from 定义 SyntaxNode 包装 enum）+ `symbol.rs` L66（裸 impl_from）。

**改动影响面**：宏规则变化直接改写 hir-def 多个类型的生成代码；hir-def 编译即红，属最紧的下游反馈。

**集成点**：新 crate 定义"每 variant 包一种类型"的聚合 enum（HIR 层常见形态）时直接 `define_enum_deriving_from!`，免手写 From；已有 enum 补转换用裸 `impl_from!`。

## `crates/utils/src/uniq_vec.rs`（91 行）

**角色**：多键去重收集器 `UniqVec<T, K>`——"按一组键去重地积累元素"，preproc 宏定义收集与诊断去重的专用结构。

**关键结构与不变量**：
- `UniqVec<T, K>`（L6）：`items: Vec<T>` + `seen: FxHashSet<K>`——**T 与 K 解耦**（值与判重键分离是本类型存在的理由）。手动 PartialEq/Eq（L11-17，items 与 seen 双比较）与 Default（L19）。
- `push(keys: impl IntoIterator<Item=K>, value: T) -> bool`（L26）：**任一键已见即整体拒绝**（L28-31，且拒绝时不污染 seen——先检查后 extend）；接受时把全部键登记再压值（L32-34）。注意 L27 先 `collect::<Vec<_>>`：避免部分迭代后才拒绝的半提交。
- `push_keyed(value, F: FnOnce(&T) -> K)`（L37）：单键便捷版。
- `contains/get/len/is_empty/as_slice/into_vec`（L45-67）：只读视图 + 消费。
- `UniqVec<T, T>` 特化（L70）：`push_unique`——值即键（clone 一份入 seen）。
- `UniqVec<T, ()>` 特化（L76）：`push_unique_by(same: Fn(&T,&T) -> bool)`（L77，**O(n) 线性扫描**，K=() 无哈希集可用）与 `push_unique_eq`（L88）。

**公开 API**：上述全部。

**依赖/被依赖**：依赖 rustc-hash。被依赖：`preproc-expand/src/preproc/conditionals.rs` L7（`UniqVec<InactiveBranch, InactiveBranchKey>`）、`diagnostics.rs` L8（`UniqVec<DiagnosticTarget, ()>`——用 O(n) by 版）、`predefines.rs` L4/L21/L37/L39（宏定义/编译 profile 收集）、`source_db.rs`、`preproc/types.rs`、`ide/hover.rs`、`ide/rename.rs`。

**改动影响面**：push 的"任一键拒绝且不污染"语义是 preproc 幂等收集的前提，改动会改变宏展开结果与诊断去重行为（preproc tests 有 snapshot）。

**集成点**：任何"多身份判重"的收集场景（如同名宏被多个 define 定义）直接选 `UniqVec<T, KeyType>`；纯等值去重且量小用 `push_unique_eq`。

## `crates/utils/src/utry.rs`（8 行）

**角色**：单宏文件——`check_or_throw!` 在 `Option` 管道中做断言式提前退出。

**关键结构与不变量**：`check_or_throw!($expr)`（L2）：表达式为 false 则执行 `None?`（L5）——**要求宏所在函数返回 Option**（`?` 对 None 提前返回），即"条件不满足 = 本轮无结果"的语义，而非错误。

**公开 API**：`#[macro_export] macro_rules! check_or_throw`。

**依赖/被依赖**：依赖无。被依赖：`ide/src/inlay_hint.rs` L27/L450/L455/L483——inlay hint 收集器里连续的"范围不相交/表达式不同名才继续"早退链，把深层嵌套 if 拉平成线性守卫。

**改动影响面**：宏体一动只影响 inlay_hint 的早退行为；语义改成 throw Err 会破坏调用点的 Option 返回型。

**集成点**：写"多重过滤条件、任一不过即放弃"的 Option 型收集逻辑时（hover/inlay/ assist 类），`check_or_throw!(cond)` 是仓内惯用法。

---

### 附：本单元架构速记

- **文本域**（line_index → lines → text_edit）：LineIndex 是坐标原语（含 SIMD 构造），LineInfo 打包每文档三要素，TextEdit 建立在两者之上——这条链被 ide 层 60+ 文件消费，是 utils 的主体价值。
- **路径域**（paths → path_identity）：paths 定类型（ra_ap_paths 壳），path_identity 定身份（拼写+inode 双证据），二者共同支撑 VFS FileId 与 preproc include 解析。
- **运行时域**（cancellation → process；excl_task、thread 独立）：cancellation 是取消原语，process 消费它管子进程；thread 的 Pool/ThreadIntent 管 LSP 任务调度与 QoS。
- **微型工具**（get/json/uimpl/uniq_vec/utry/panic_context/test_support）：各解决一个横切小问题；其中 panic_context 目前无消费者（休眠资产）。
