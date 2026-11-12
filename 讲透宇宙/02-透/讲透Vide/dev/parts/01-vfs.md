# 01-vfs 精读手册

> 模块定位：`crates/vfs` 是 vide 从 rust-analyzer fork 的自有 VFS crate（Cargo.toml L4 自述 "Owned fork of rust-analyzer VFS"），位于三层架构的最底层：Salsa RootDb 之下、一切分析之上。职责有二：① 把任意路径（真实/虚拟）intern 成紧凑 `FileId(u32)` 并维护内容变更日志（`Vfs`，LSP 层的唯一文件事实来源）；② 提供 `loader::Handle` 异步加载/监听抽象与两个后端（notify=OS 真监听、dummy=wasm/无监听）。vide 对原版的三处关键改造：`SOURCE_FILE_EXTENSIONS` 换成 SystemVerilog 扩展（loader.rs L7）、`FileSetConfig` 扩展出 include/source/exclude 三段式 `FileSetFilter`+`PathMatcher`/`PathGlobMatcher`（服务 project-model 的 workspace 配置）、`FileState` 增加 `Excluded` 第三态（lib.rs L92）。ide/preproc-expand/hir-def/base-db/workspace-model 及 src/global_state*（LSP 主循环）共 100+ 文件依赖本 crate；`FileId` 直接 unsafe 实现 `salsa::SalsaValue`（lib.rs L54）进入 Salsa query key 体系。

---

## `crates/vfs/Cargo.toml`（27 行）

**作用**：crate 清单。`vfs` 0.0.0（workspace 内版本由根统一），edition 走 workspace。
**关键字段**：`features` 三态——`default = ["notify-backend"]`，`notify-backend` 门控 `dep:notify`/`dep:rayon`/`dep:walkdir` 三个可选依赖（notify.rs L15-16 的 `#[cfg(feature = "notify-backend")]` 对应）。依赖面：salsa（SalsaValue）、fst 0.4.7（file_set 的有序 map 自动机）、globset（path_glob）、indexmap（changes 变更表 + interner）、nohash-hasher（FileId 作 IntMap key）、rustc-hash、triomphe（Arc<str>）、tracing、utils（paths/thread）。dev-dependencies 仅 tempfile（notify.rs L431 测试用临时目录）。
**改动的连带影响**：根 Cargo.toml L167-169 中 LSP 二进制的 `server-file-watcher` feature 传递启用 `vfs/notify-backend`；关掉 default feature 则 notify.rs 整个模块不编译，`spawn_vfs_loader`（src/global_state.rs L113-126）在无 watcher 构建下降级到 DummyHandle。升级 fst/globset 大版本会波及 file_set/path_glob 的路径匹配语义。

---

## `crates/vfs/src/lib.rs`（363 行）

**角色**：crate 门面——定义 `FileId`/`Vfs`/`ChangedFile`/`Change`/`FileState` 核心状态机，re-export 全部子模块公开类型，是整个 vide 文件世界的根类型文件。

**关键结构与不变量**：
- `FileId(u32)`（L51）——intern 后的文件身份。不变量：值 = `PathInterner` 的 IndexSet 下标，**只增不回收**（path_interner.rs L1-3 头注释明言不做清理）；上限 `MAX = 0x7fff_ffff`（L57），`from_raw` 会 assert。`unsafe impl salsa::SalsaValue`（L54）要求其 Copy+'static，SAFETY 注释即此；`nohash_hasher::IsEnabled`（L72）允许它直接作 nohash IntMap 的 key（位模式即哈希值）。
- `FileState`（L85）三态：`Exists(u64)`（内容 FxHasher 哈希）/`Deleted`/`Excluded`。**不变量**：`Excluded` 文件保留 id 与路径但不存内容——lib.rs L350-352 注释解释了为什么不能直接忽略（客户端对被排除文件请求语义信息时会报错，所以打特殊标记）。这是 vide 对 rust-analyzer 原版两态的扩展。
- `Vfs`（L78）= `interner: PathInterner` + `data: Vec<FileState>`（下标即 FileId）+ `changes: IndexMap<FileId, ChangedFile>`。不变量：`data.len()` ≥ interner 长度（`alloc_file_id` L333-339 resize 补齐，默认填 `Deleted`）；changes 是"自上次 take_changes 以来的增量"。
- `set_file_contents`（L250-314）核心写路径：状态机匹配 (state, contents) 生成 `Change`——Deleted+None 直接 false（无变化）；Exists+同哈希 false（内容未变短路，L261-266）；Excluded 一律 false（L268）。**同周期合并律**（L279-311）：同一文件多次变更合并进一个 `ChangedFile`——新 Delete 必胜（L286）；Create/Create 或 Create/Modify 取新内容但仍标 Create（L288-291）；Delete+Create 折叠为 Modify（L298-299，"等价于 Modify"）；两条"shouldn't occur"分支（L302-306）做防御性折叠。
- `ChangedFile`（L97）：`file_id` + `Change`。`text()`（L135）把无效 UTF-8 替换成空串返回 `triomphe::Arc<str>`——**约定：非 UTF-8 文件在 VFS 层不报错，静默为空**。
- `hash_once<Hasher: Hasher + Default>`（L43）：单次哈希工具，Content hash 一律 FxHasher。

**公开 API**：`Vfs::file_id(&VfsPath) -> Option<(FileId, FileExcluded)>`（L210）、`file_path(FileId) -> &VfsPath`（L225，id 不存在则 panic）、`iter()` 跳过 Deleted（L232）、`set_file_contents(VfsPath, Option<Vec<u8>>) -> bool`（L250）、`take_changes() -> IndexMap<FileId, ChangedFile>`（L317，mem::take 清空）、`exists(FileId) -> bool`（L322）、`insert_excluded_file(VfsPath)`（L353）。`ChangedFile::exists/is_created_or_deleted/is_created/is_modified/kind/text/contents/create/modify/delete`（L104-165）。`Change::from_bytes(Option<Vec<u8>>)`（L169，None→Delete，Some→Create）。re-export：`AnchoredPath(Buf)`/`FileSet` 系/`PathGlobMatcher`/`VfsPath`/`AbsPath(Buf)`（L30, L33-41）。

**依赖/被依赖**：依赖（模块内）anchored_path/dummy/file_set/loader/notify(cfg)/path_glob/path_interner/vfs_path + `utils::paths`。被依赖（图谱入边，100+）：base-db（source_db.rs 的 salsa trait `resolve_path`/`file_text`/`files` 以 FileId 为 key）、preproc-expand（file.rs/macro_file.rs/db.rs 等 10 文件）、hir-def（owner/pathres/scope/item_tree/diagnostics）、ide（40+ 文件）、workspace-model（source_db/source_root）、hir-semantics、src/global_state* 全家（snapshot.rs L76 把 `Vfs` 与 LineEnding 表一起装进 `Arc<RwLock<(Vfs, IntMap<FileId, LineEnding>)>>`，process_changes.rs L32 每轮 `take_changes` 分发）。

**改动影响面**：`FileId` 的位模式/上限改动会破坏 nohash IntMap 与所有 salsa query 缓存 key；`FileState` 增删变体必须同步 `file_id`（L210-218）与 `set_file_contents` 的 match（L254-269，两处穷尽匹配会编译报错，属安全网）；`take_changes` 语义变化直接影响 process_changes.rs 的变更分发节流逻辑；`text()` 的 UTF-8 容错行为变化会改变二进制文件在诊断里的表现。同周期合并律（L279-311）是 LSP 端 didOpen/didChange 风暴下 change 计数稳定的前提，动了会引发 main_loop.rs L353 的 `assert!(!take_changes().is_empty())` 类测试连锁失败。

**集成点**：二次开发最常用入口是 `Vfs::set_file_contents` + `take_changes`（自建加载通道）；`insert_excluded_file` 是构建系统"排除但不驱逐"语义的挂点（project-model 消费 `FileExcluded` 决定是否走完整分析）；`FileId::from_raw/index`（L60/L66）供跨 crate 持久化 id（base-db L94 的 registry.files() 反向重建就用了 from_raw）。

---

## `crates/vfs/src/anchored_path.rs`（49 行）

**角色**：分析层路径表示——"相对某文件的路径"，解决 `#[path]`/`` `include`` 类相对引用的锚定语义。

**关键结构与不变量**：`AnchoredPathBuf`（L33）= `anchor: FileId` + `path: String`（owned）；`AnchoredPath<'a>`（L44）= 同构借用版（Copy）。**设计动机（L1-26 头注释）**：为什么不用 PathBuf——宿主 OS 相关，无法在 Unix 处理 `C:\bar.rs`；为什么不用 String——绝对路径也只在某个文件系统"宇宙"内绝对（分布式/虚拟 VFS 场景）；所以每条相对路径携带来源文件锚，从锚可取回 fs/宇宙信息。不变量：`path` 相对 anchor 的**所在目录**（非 anchor 文件本身，FileSet::resolve_path L34 的 `base.pop()` 体现了这一点）。

**公开 API**：两个 pub struct 均为纯数据（字段 pub），无方法——语义由消费者（FileSet::resolve_path）实现。

**依赖/被依赖**：依赖 `crate::FileId`。被依赖（入边）：lib.rs（re-export）、base-db source_db.rs（salsa trait `resolve_path(AnchoredPath)` 的参数类型）、ide/db/root_db.rs、hir-def pathres（L580 测试桩实现）、preproc-expand 测试。

**改动影响面**：`AnchoredPath` 是 salsa query `resolve_path` 的输入之一（base-db L16），给它加字段等于改 query 签名，会波及 hir-def 模块解析与 ide module_resolution 全链路测试。

**集成点**：新的路径解析特性（如 `` `include` `` 搜索路径、包相对路径）应复用该类型走 `SourceDatabase::resolve_path`，而非自己拼字符串。

---

## `crates/vfs/src/dummy.rs`（53 行）

**角色**：`loader::Handle` 的无 OS 监听实现（wasm/无 watcher 构建用），即"协议正确但永远没有文件事件"的后端。

**关键结构与不变量**：`DummyHandle`（L10）只持 `Sender<loader::Message>`。不变量（`set_config` L19-37）：对每个 config 立即发 Progress(Started) → 逐 entry 发一条空 `Loaded { files: Vec::new() }`（L29）→ Progress(Finished)——**协议形状与 NotifyHandle 完全一致**（消费方 global_state 的 VfsProgress 就绪逻辑不能区分后端），只是永远不交付任何文件内容。`invalidate`（L39-42）仍做真实同步读盘并回发 `Changed`——即 dummy 并非完全无 IO，它保留了"客户端主动要求重读"这条同步通道。`load_sync`（L44）直接 `std::fs::read`。

**公开 API**：`impl loader::Handle for DummyHandle`（L14）：`spawn(Sender)`/`set_config(Config)`/`invalidate(AbsPathBuf)`/`load_sync(&AbsPath) -> Option<Vec<u8>>`。

**依赖/被依赖**：依赖 loader.rs（Handle/LoadingProgress/Message）、utils::paths。被依赖：lib.rs（`pub mod dummy`，L12）；消费方是 src/global_state.rs L122 的 `spawn_vfs_loader`——在 `#[cfg(not(feature = "server-file-watcher"))]` 分支装箱为 `Box<dyn Handle>`。

**改动影响面**：Message 序列的顺序/数量若不再镜像 NotifyHandle，global_state 的加载进度展示与 `WorkspaceVfsReadiness` 就绪判定会挂；notify.rs L438 的 `watcher_setup_finishes_loading` 测试范式对 dummy 同样适用（每 config 必须 Finished）。

**集成点**：写新后端（如远程文件系统、快照回放）时的最小参照——只需实现 4 个方法并保持 Progress/Loaded/Progress 消息形状即可被 `spawn_vfs_loader` 无缝替换（Box<dyn Handle> 动态分发，loader.rs L239-241 `handle_is_dyn_compatible` 静态保证）。

---

## `crates/vfs/src/file_set.rs`（395 行）

**角色**：source root 分区器——把 Vfs 全量文件按配置切成有序 `FileSet`（每 root 一个双向索引），并叠加 vide 特有的 include/source/exclude 过滤与语义源文件子集。

**关键结构与不变量**：
- `FileSet`（L10）= `files: FxHashMap<VfsPath, FileId>` + `paths: IntMap<FileId, VfsPath>`，双向一致由 `insert`（L39-42，两表同写）维护。`resolve_path`（L32-37）：anchor 路径 pop 出父目录 → `VfsPath::join` 相对段 → 查 files。**依赖 VirtualPath::join 的 `../` 解析（vfs_path.rs L392-403）**，越过根返回 None。
- `FileSetConfig`（L51）= `len`（roots 数+1，末位是"不匹配任何 root"的兜底分区）+ `map: fst::Map`（路径编码→root 索引）+ `filters: Vec<FileSetFilter>`。不变量：`classify`（L250-263）用 `PrefixOf` 自动机在 fst 上做**最长前缀匹配**，从 `len-1`（兜底位）起步，遍历所有前缀 root、取最后一个 filter 通过者为归属——**等价规则：前缀更长的 root 声明优先，但同分区内 earlier roots win（struct 注释 L49）由 fst 迭代序+later-overwrite 实现**。`scratch_space` 复用编码缓冲避免每文件分配。
- `PathMatcher`（L67）= `scan_roots: Vec<AbsPathBuf>` + `kind: AllUnderRoots | Glob(PathGlobMatcher)`。`contains_file`（L97）= 落在任一 scan_root 下 &&（Glob 时模式命中）；`contains_dir`（L105）只查 scan_root；`prefers_recursive_directory_load`（L115）——模式全含 `**` 或纯根 → 可走递归目录加载（project-model L700 据此选择加载策略）；`collect_matching_files`（L125）真实遍盘收集（`collect_files_under` L145 递归 read_dir）后按扩展名+contains_file 过滤，sort+dedup 保确定性。
- `FileSetFilter`（L170）= `include: Vec<PathMatcher>` + `source: Option<Vec<PathMatcher>>` + `exclude_paths` + `exclude_globs: Option<PathGlobMatcher>`。`matches`（L178-185）：任一 include 命中 && 不在任何 exclude 前缀下 && 不命中 exclude glob；**virtual path（非真实盘路径）特判**（L180-181）：include 与 exclude_paths 均空才收——虚拟路径没有 AbsPath 可言。`is_source`（L187）同构但只看 source 段。
- `PartitionedFileSet`（L60）= `file_set` + `source_files: Option<FxHashSet<FileId>>`——同一 root 内再切"语义上属于源码"子集（`partition_with_source` L215-238 在插入时按 `is_source` 双写）。
- `FileSetConfigBuilder`（L268）：`add_file_set(roots)`（L286）把 roots 转 `PathMatcher::all_under_roots` 的默认 include；`build`（L301-322）把每个 root 的 `VfsPath::encode` 字节串与 root 序号做 fst::Map，**sort 保证长前缀靠后**（L318 注释）、dedup 同键。
- `PrefixOf<'a>`（L326）实现 `fst::Automaton`（L337）：state 是已匹配前缀长度，`!0` 为死态——标准前缀自动机。

**公开 API**：`FileSet::{len,is_empty,get_file,get_path,resolve_path,insert,iter}`；`FileSetConfig::{builder,partition,partition_with_source}`；`FileSetConfigBuilder::{len,is_empty,add_file_set,add_filtered_file_set,build}`；`PathMatcher::{all_under_roots,glob,is_empty,contains_file,contains_dir,scan_roots,prefers_recursive_directory_load,collect_matching_files}`；`FileSetFilter`（字段全 pub）；`PartitionedFileSet`（字段 pub）。

**依赖/被依赖**：依赖 fst、nohash IntMap、`utils::paths`（含 `abs_path_buf_from_path_buf`）、crate 内 Vfs/VfsPath/AnchoredPath/FileId/PathGlobMatcher。被依赖（入边）：lib.rs（re-export）、project-model lib.rs（L20 `use vfs::{FileSetConfig, FileSetFilter, PathGlobMatcher, PathMatcher, VfsPath}`——workspace 配置到 FileSetConfig 的唯一翻译点）、ide code_action/tests、preproc-expand tests、file_set/tests.rs。

**改动影响面**：`classify` 的前缀匹配或兜底位语义变化直接改写 source root 归属 → workspace-model/source_root.rs 的 SourceRoot 划分 → hir-def 模块解析的可见域，全套模块解析测试会动；`FileSetFilter::matches` 的 virtual-path 分支是测试 fixture（new_virtual_path）能落盘的关键，删掉会炸所有用虚拟路径的分区测试；fst map 的编码格式与 `VfsPath::encode` 强耦合（同一 encode 函数），单边改动会静默错配。

**集成点**：project-model 的 workspace include/exclude glob 配置全部经 `FileSetConfigBuilder::add_filtered_file_set` 注入；`source_files` 子集是"哪些文件算语义源码"（区别于头文件/生成文件）的扩展点；`PathMatcher::collect_matching_files` 可独立用于任何"按根+扩展名收文件"的场景（project-model L705 正是这么用的）。

---

## `crates/vfs/src/file_set/tests.rs`（65 行）

**角色**：FileSetConfig 前缀归属语义的单测（`mod tests` 内嵌于 file_set.rs，L357 起 `#[cfg(test)] mod tests` 已有 2 个 SV 化测试，本文件是 file_set.rs 尾部 `#[cfg]` 外的独立覆盖——实际由 file_set.rs L1 处声明路径拼接；见下方"跑法"）。

**覆盖什么行为**：①`path_prefix`（L4）——`/foo` 与 `/foo/bar/baz` 两 root 前缀嵌套时，`/foo/src/lib.rs` 与 `/foo/bar/baz/lib.rs` 归短前缀 root、深层文件归长前缀 root、`/quux` 落兜底分区，断言分区大小 `[2,1,1]`（L23）；②`name_prefix`（L27）——`/foo` vs `/foo-things`：同为 `/foo` 字符串前缀但不同 root，断言 `[1,1,0]`（L41），证明前缀匹配是按路径编码不是朴素 starts_with 字符串；③`name_prefix_partially_matches`（L47）——`/foo/bar_baz.rs` 不能因 `/foo/bar` 是字符串前缀而归入 `/foo/bar` root（注释 L44-45 点名该回归动机），断言 `[2,1,0]`。这三条共同钉死 fst 编码+PrefixOf 自动机的边界正确性。

**跑法**：`cargo test -p vfs`（与 crate 内其余测试同跑；file_set.rs L362/L378 的内嵌测试 `partition_places_file_under_matching_root`/`partition_prefers_earlier_root_when_prefixes_overlap` 补充 SV 语境用例）。

---

## `crates/vfs/src/loader.rs`（241 行）

**角色**：文件加载/监听的接口层——`Handle` trait + `Config`/`Entry`/`Message` 协议类型，是 dummy/notify 两后端与 LSP event_loop 之间的契约。

**关键结构与不变量**：
- `SOURCE_FILE_EXTENSIONS`（L7）= `["v","sv","vh","svh","svi","map"]`——**vide 对 rust-analyzer 的核心 diff：SystemVerilog 扩展名表**（原版是 rs）。project-model L571/L705/L827 与 global_state/reload.rs L250 都引用它做过滤。
- `Entry`（L11）二态：`Files(Vec<AbsPathBuf>)`（显式文件集）| `Directories(Directories)`（按目录规则）。三个遗留构造器 `rs_files_recursively`/`local_cargo_package`/`cargo_package_dependency`（L108-134）仍是 RA 原版 rs 语义，vide 实际主路径走的是 project-model 的 PathMatcher 体系，这三个是兼容残留。
- `Directories`（L29）：extensions/include/exclude 三段。**`includes_path`（L185-202）的裁决规则**：include 取所有匹配前缀中**最长**者（L189-192 的 `prev.starts_with(incl)` 保留 prev）；exclude 只有当它是"包含在胜出 include 之内的前缀"才生效（L201 的 `excl.starts_with(include)`），且**等长时 exclude 赢**（doc 注释 L27）。
- `Config`（L37）：`version`（进度消息对账用）/`load: Vec<Entry>`/`watch: Vec<usize>`（**watch 是 load 的下标集**，L46 注释——被 watch 的 entry 变更时 Handle 有义务通知）。
- `LoadingProgress`（L51）：Started/Progress(usize)/Finished 渐进枚举。
- `Message`（L58）三态：`Progress{n_total,n_done,dir,config_version}` / `Loaded{files}`（**首次**载入）/ `Changed{files}`（后续变更）——Loaded vs Changed 的区分是 VFS 侧区分初装与增量的依据。
- `Handle`（L82）：`spawn(Sender) -> Self where Self: Sized` + `set_config`/`invalidate`/`load_sync`；`fmt::Debug` supertrait。文件尾 `handle_is_dyn_compatible`（L239-241）用 `&dyn Handle` 签名静态断言 dyn 兼容（spawn 的 Sized 约束不影响已有实例的动态分发）。

**公开 API**：上述全部 pub；`Sender = crossbeam_channel::Sender<Message>`（L79）；`Entry::contains_file/contains_dir`（L139/L150，Files 分支的 contains_dir 恒 false）；`Directories::contains_file`（L160，先扩展名后 includes_path）/`contains_dir`（L175）。

**依赖/被依赖**：依赖 `utils::paths`。被依赖（入边）：lib.rs、dummy.rs、notify.rs（两后端）、src/global_state/event_loop.rs（LSP 侧收 Message 驱动 reload）。

**改动影响面**：`Message` 枚举增删变体会同时强制改 dummy.rs/notify.rs/event_loop.rs 三处；`watch` 下标语义若改为独立路径集，notify.rs L159 的 `config.watch.contains(&i)` 与后端注册逻辑都要重写；`SOURCE_FILE_EXTENSIONS` 增删扩展名直接决定哪些 SV 文件会被扫描进工作区（漏 `.svh` 会让头文件 include 解析静默失败）。

**集成点**：新后端接入点 = `impl loader::Handle`；新文件类型过滤 = 改 `SOURCE_FILE_EXTENSIONS` 或在 project-model 侧走 PathMatcher；`invalidate(path)` 是外部（如测试、外部进程）强制重读单文件的同步钩子。

---

## `crates/vfs/src/notify.rs`（488 行）

**角色**：`loader::Handle` 的生产后端——walkdir 并行初载 + OS 文件监听（notify crate），单线程 actor 模型。

**关键结构与不变量**：
- `BackendWatcher`（L23-26）平台分派：**macOS 强制 PollWatcher**（L19-22 注释：FSEvents 的 CFRunLoop 启停可能阻塞，不能拿 workspace 就绪性冒险；PollWatcher 启停有界且保留递归监听），其余平台 RecommendedWatcher。`WATCHER_BACKEND` 常量（L28-31）配套打日志。
- `NotifyHandle`（L34）= `sender: Sender<Message>`（内部指令通道）+ `_thread: utils::thread::JoinHandle`——**字段顺序即 drop 顺序**（L36 注释）：先关 sender 让 actor 的 `recv` 收到 Err 退出，再 join 线程。
- 内部 `Message`（L41）= Config | Invalidate；`NotifyActor`（L72）= 下行 loader::Sender + `watched_file_entries: FxHashSet`（显式文件集）+ `watched_dir_entries: Vec<Directories>`（目录规则）+ `seen_paths: FxHashSet`（Access 事件去重）+ `watcher: Option<(BackendWatcher, Receiver)>`（watcher 与其事件通道同生共死，L78 注释 drop 顺序）。
- `next_event`（L98-107）：无 watcher 时只收指令；有 watcher 时 `select!` 双通道——**L105 的 `it.unwrap()`**：watcher 通道 Err 即 panic，但因回调持有 sender、watcher 由 actor 独占，正常生命周期不会触发。
- `run` 主循环（L109-304）Config 分支：先作废旧 watcher（L116），重建 watcher（poll interval 1s，L119）；发 Progress(Started)；`config.load.into_par_iter()`（L158，rayon）并行载入——**进度计数用 AtomicUsize**（L156，Relaxed 读 L171 / AcqRel fetch_add L182）；载完 drain watch_rx 逐路径注册监听（L190-192）再 drain entry_rx 记账 watched_*（L195-204）；收尾 Progress(Finished)。**watch_tx/entry_tx 的 drop 顺序（L189/L194）是 drain 能终止的前提**。
- NotifyEvent 分支（L219-301）：只处理 Create/Modify/Remove/Access(Open)（L227-230）；路径转 `Utf8PathBuf`→`AbsPathBuf`（非 UTF-8/非绝对被 filter_map 丢弃，L235-240）；`seen_paths` 去重 + **FUSE 特判**（L252-258 注释：FUSE 可能不给 Create 只有 Access，故 Access 只对没见过的文件放行，同时避免"处理 Access 又触发 Access"的自激环）；L265-270 双重身份过滤（在 watched_file_entries 或任一 watched_dir 的 contains_file 内，否则忽略）；Remove 事件直接上报 `(path, None)` 不查 metadata（L276-278，文件已不在）；目录事件→递归补注册（L281-288）；最终 Changed 上报。
- `load_entry`（L306-383）：Files 分支逐文件读；Directories 分支 WalkDir `follow_links(true)`（L329）+ `filter_entry`：`path_might_be_cyclic`（L335）拦截父目录符号链接环，**跳过本身是其它 root 的子目录**（L342-349，它们会被单独访问）；depth<2 的目录发进度（L360-362）；is_dir 且 do_watch 则注册监听（L363-364）；文件再过 `dirs.contains_file` 扩展名关（L369）。
- `path_might_be_cyclic`（L414-424）：read_link 是相对父链（全 `.`/`..` 组件）或目标包含路径自身 → 判环。**自认是启发式**（L411-413 注释：双符号链接环抓不到）。
- `read`（L404）= `std::fs::read(...).ok()`——**读失败一律当文件不存在**（Some 路径丢失内容、Delete 语义靠事件 kind 而非读取结果）。

**公开 API**：`impl loader::Handle for NotifyHandle`（L46-68）：spawn（起 "VfsLoader" 具名 Worker 线程，L50-53，`expect("failed to spawn thread")`）/set_config/invalidate（转内部消息）/load_sync（直接同步 read）。其余（NotifyActor/Event/load_entry/watch/path_might_be_cyclic）均私有。

**依赖/被依赖**：依赖 loader.rs、`utils::paths`、`utils::thread`（Builder/ThreadIntent/JoinHandle——非 std thread）、notify/rayon/walkdir（feature 门控）。被依赖：lib.rs（L15-16 `#[cfg(feature = "notify-backend")] pub mod notify`）；消费方 src/global_state.rs L117（`server-file-watcher` feature 时的 spawn_vfs_loader 分支）。

**改动影响面**：Message::Config 的处理顺序（作废 watcher→重置 seen_paths→并行载→drain→Finished）被打乱会让 LSP 端进度/就绪状态机错乱；`EventKind` 过滤集变化影响重命名（rename 依赖成对的 Remove+Create）等语义；rayon 并行度变化影响大库初载时间；macOS PollWatcher 决策（L23）回退 FSEvents 会重现"drop handle 卡死"（L484-486 测试注释记录的旧 bug）。

**集成点**：`watch()` 失败只记 error 不中断（L389-394）——外部挂载点不可监听时系统继续跑；`path_might_be_cyclic` 是独立可复用的符号链接环启发器；测试 `watcher_setup_finishes_loading`（L438-487，tempfile + 5s deadline + journal panic 消息）是新后端行为验收的模板。

---

## `crates/vfs/src/path_glob.rs`（70 行）

**角色**：根相对 glob 匹配器——globset 的薄包装，把"workspace 根 + 相对 pattern 集"变成可哈希、可比较的匹配对象（供 FileSetFilter/project-model 配置用）。

**关键结构与不变量**：`PathGlobMatcher`（L11）= `root: AbsPathBuf` + `patterns: Vec<String>` + `matcher: Arc<GlobSet>`。不变量：**匹配语义 = strip 掉 root 后按 `/` 分隔的相对路径匹配**（`is_match` L30-37，反斜杠归一为 `/`）；pattern 构建用 `GlobBuilder::literal_separator(true)`（L22）——`*` 不跨目录，`**` 才跨；`backslash_escape(true)` 允许 `\` 转义。**Eq/Hash 手写且只看 root+patterns 不看 GlobSet**（L57-70）——同配置的 matcher 视为相等，使 FileSetFilter 可作 HashMap key/可比较；Debug 同样不漏 Arc（L48-55）。strip 前缀失败（路径不在 root 下）直接 false（L31-33）。

**公开 API**：`new(root, patterns) -> Result<Self, globset::Error>`（L18，任一 pattern 非法即整体 Err）；`is_match(&AbsPath) -> bool`（L30）；`root() -> &AbsPathBuf`（L39）；`patterns() -> &[String]`（L43，file_set.rs L119 的 `prefers_recursive_directory_load` 靠它检查全 `**`）。

**依赖/被依赖**：依赖 globset、`utils::paths`。被依赖（入边）：lib.rs（re-export）、file_set.rs（`depends_on` 边——PathMatcherKind::Glob 与 FileSetFilter.exclude_globs）、project-model lib.rs（L20 import；L457 `PathGlobMatcher::new(workspace_root, patterns)` 由 workspace exclude 配置构建，L69/L319/L833 多处持有）。

**改动影响面**：`literal_separator`/`backslash_escape` 标志翻转会静默改变用户 exclude glob 的匹配行为（`*.gen.sv` 突然跨目录命中）；Eq/Hash 若把 GlobSet 纳入会破坏 FileSetFilter 的相等性语义（其 derive 的 Eq/Hash 依赖此手写实现）。

**集成点**：任何需要"配置驱动的路径过滤"的地方直接 new + is_match；`patterns()` 暴露原始串供策略判断（如 prefers_recursive_directory_load）。

---

## `crates/vfs/src/path_interner.rs`（43 行）

**角色**：VfsPath↔FileId 双向字典——IndexSet 单表兼任正反查询。

**关键结构与不变量**：`PathInterner`（L13）= `map: IndexSet<VfsPath, FxHasher>`。**核心不变量：id == IndexSet 下标，且只增不减**（L1-3 头注释：不做清理，假设看过的路径总量可控——这是内存换简单性的显式取舍）。`intern`（L29-33）的 `assert!(id < FileId::MAX as usize)` 是 2^31 文件防线（与 lib.rs L57/L61 呼应）。`lookup`（L40-42）对不存在 id `unwrap` panic——合法 id 只能来自 get/intern，故属内部契约而非公开错误路径。Vfs 的 `data: Vec<FileState>` 与此表按下标对齐（lib.rs L333-339 的 resize 保证）。

**公开 API**：全部 `pub(crate)`：`get(&VfsPath) -> Option<FileId>`（L21，get_index_of 查存在性）、`intern(VfsPath) -> FileId`（L29，insert_full 幂等）、`lookup(FileId) -> &VfsPath`（L40）。

**依赖/被依赖**：依赖 crate 内 FileId/VfsPath（lib.rs、vfs_path.rs 入边）。被依赖：仅 lib.rs（`Vfs.interner` 字段私有使用）。

**改动影响面**：换成可回收结构（如世代 id）会破坏 FileId 的 `'static` Copy 语义与 salsa 缓存（SalsaValue unsafe impl 的 SAFETY 前提）；FxHasher 换哈希器会改变 intern 顺序→FileId 分配顺序变化→依赖 id 序的下游（file_set IntMap 遍历序、测试快照）抖动。

**集成点**：无直接外部入口——想改 intern 策略只能通过 Vfs 间接；但"只增不删"这一取舍是评估超大 workspace 内存的行为锚点。

---

## `crates/vfs/src/vfs_path.rs`（440 行）

**角色**：VFS 路径抽象——`VfsPath` 双表示（真实 AbsPathBuf / 虚拟 `/` 分隔字符串）统一封装，含跨平台确定性编码（fst key 的来源）与虚拟路径代数。

**关键结构与不变量**：
- `VfsPath(VfsPathRepr)`（L13）newtype；`VfsPathRepr`（L289）私有 enum：`PathBuf(AbsPathBuf) | VirtualPath(VirtualPath)`。**跨表示运算恒 None/false**（`starts_with` L95、`strip_prefix` L103、`PartialEq<AbsPath>` L324-336）——真实与虚拟路径是两个不相交宇宙。
- `new_virtual_path`（L23）断言以 `/` 开头；`From<AbsPathBuf>`（L294）**进真实路径即 normalize**——VfsPath 持有的真实路径永远是规范化形态，这是 `==` 可靠的前提。
- `join(&str)`（L55）：真实路径走 `AbsPathBuf::join + normalize`；虚拟路径走 `VirtualPath::join`（L392-403）——**手工解析前导 `../`**（超出根返回 None）再剥 `./`，注释 L383-387 明确约定相对路径语义。`pop`（L83）双表示各自弹尾。
- `encode(&mut Vec<u8>)`（L131-179）`pub(crate)` 且带"**Don't make this pub**"（L123）的注释——这是 file_set fst map 的 key 编码：tag 0=真实/1=虚拟 + 表示体。**平台相关**（doc 注释 L130）：unix 走 OsStr 原始字节（L169-171）；windows 子模块（L182-285）按 UTF-16LE 编码组件并用 `Prefix::kind()` 归一（drive 大小写不敏感、正反斜杠等价——测试 `paths_encoding` L258-262 钉死 `C:/x.rs == c:/x.rs`、`C:/x/y.rs == C:\x\y.rs`；`test_sep_root_dir_encoding` L274-278 钉死精确字节序列）；其它平台 `to_string_lossy` 兜底。**同一性保证全靠该编码——改它等于换 fst 字典格式**。
- `VirtualPath(String)`（L342）私有：`starts_with` 是朴素字符串前缀（L346-348，**不含路径边界检查**——`/foo-bar` 以 `/foo` 为字符串前缀；路径边界正确性由 encode 的字节级前缀匹配在 fst 侧兜住）；`strip_prefix`（L350-355）借用 Utf8Path::strip_prefix 后 `RelPath::new_unchecked`；`pop`（L373-380）rfind('/') 截断；`name_and_extension`（L416-436）——尾 `/` 先剥（L417）、rsplitn(2,'.') 取扩展名、**首点文件特判**（`.file` 无扩展名、`.file.rs` 扩展名 rs，L430-434），`/foo/bar.baz.rs` → `("bar.baz", Some("rs"))`。

**公开 API**：`new_virtual_path(String)`、`new_real_path(String)`（L30，AbsPathBuf::assert）、`as_path/as_abs_path() -> Option<&AbsPath>`（L36/L43）、`into_abs_path() -> Option<AbsPathBuf>`（L47）、`join(&str) -> Option<VfsPath>`（L55）、`pop(&mut self) -> bool`（L83）、`starts_with(&VfsPath) -> bool`（L91）、`strip_prefix(&VfsPath) -> Option<&RelPath>`（L99）、`parent() -> Option<VfsPath>`（L110，clone+pop 实现）、`name_and_extension() -> Option<(&str, Option<&str>)>`（L116）；trait：`From<AbsPathBuf>`、`Display`、`Debug`、`PartialEq<AbsPath>`（双向）。

**依赖/被依赖**：依赖 `utils::paths`（AbsPath/AbsPathBuf/RelPath/normalize）。被依赖（入边）：lib.rs、path_interner.rs、project-model（workspace 构建全用 VfsPath）、ide code_action/tests、preproc-expand tests、vfs_path/tests.rs。

**改动影响面**：`encode` 与 file_set.rs 的 fst map 是同一契约的两端，单边改动让分区静默错位（最危险的一类改动，编译器不会报错）；`normalize` 时机变化（From impl）会让同一物理路径出现两种 VfsPath 表示→FileId 分裂；windows 编码改动只影响 Windows 分区测试；VirtualPath 的字符串前缀语义若改成带边界检查，file_set/tests.rs 的三条用例预期都要复核。

**集成点**：`new_virtual_path` 是测试/内存文档（mem_docs）造非盘文件的标准通道；`encode` 若需持久化 VfsPath（如索引落盘）应复用而非另造格式（pub(crate) 限制正是提示它属内部契约）。

---

## `crates/vfs/src/vfs_path/tests.rs`（30 行）

**角色**：`VirtualPath::name_and_extension` 的边界单测（`mod tests` 挂在 vfs_path.rs L439-440）。

**覆盖什么行为**：`virtual_path_extensions`（L4）逐行断言七种边界：`"/"` → None（L5）；无点路径 `"/directory"` → `(directory, None)`（L7-9）；**尾斜杠等价** `"/directory/"` 同样 `(directory, None)`（L11-13）；普通文件无扩展（L15-17）；**首点文件无扩展** `"/directory/.file"` → `(".file", None)`（L19-21）；首点文件带扩展 `".file.rs"` → `(".file", Some("rs"))`（L23-25）；常规扩展（L27-29）。钉死了 dotfile 语义与尾斜杠容错，防止扩展名误判导致 SOURCE_FILE_EXTENSIONS 过滤错杀。

**跑法**：`cargo test -p vfs`（Windows 专属的 `paths_encoding`/`test_sep_root_dir_encoding` 在非 Windows 下不编译）。

---

## 附：本单元在 vide 中的消费拓扑（图谱+grep 实证）

- `Vfs/FileId`（lib.rs）→ 100+ 下游文件；LSP 层 `src/global_state/snapshot.rs` L76 `Arc<RwLock<(Vfs, IntMap<FileId, LineEnding>)>>` 聚合，`process_changes.rs` L32 `take_changes` 每轮分发。
- `FileId` 的 `salsa::SalsaValue`（lib.rs L54）→ base-db source_db.rs 的 `resolve_path`/`file_text`/`file_kind`/`files` query 全用它当 key。
- `FileSetConfig/PathMatcher/FileSetFilter/PathGlobMatcher` → project-model lib.rs L20 独家翻译 workspace 配置；`prefers_recursive_directory_load`/`collect_matching_files`（file_set.rs L115/L125）→ project-model L700/L705 的加载策略分派。
- `loader::Handle` 选择：src/global_state.rs L113-126 `spawn_vfs_loader`，feature `server-file-watcher`（根 Cargo.toml L167-169）→ NotifyHandle，否则 DummyHandle。
- `AnchoredPath` → base-db `SourceDatabase::resolve_path`（source_db.rs L16）→ hir-def 模块解析 → ide module_resolution。
