# 02 · VFS：编辑器文本进入分析世界（crates/vfs/src/lib.rs）

## 角色定位

`crates/vfs` 是 vide 与文件系统之间的隔音层。L1-6 的 crate 文档直言它「基于 rust-analyzer 的 vfs crate」：把「磁盘上路径各异的文件」抽象成「内存里编号为 `FileId` 的文本单元」，并维护一份待消费的变更日志。整个编译管线（parse、preproc、HIR）只认 FileId，不认 Path——这带来两个决定性好处：一是 `didOpen` 的未保存文档、虚拟路径（宏展开产物、`/__vide/preproc/...`）与真实磁盘文件在同一坐标系下处理；二是路径字符串只在此处 intern 一次，全仓后续比较都是 u32 等值比较。L6-9 点名 IO 与监听不在本文件，而在 `loader` 后端（`notify`/`dummy`），lib.rs 只负责纯数据结构与变更合并语义。

## 内部结构

核心类型三件套：

- **`FileId(u32)`**（L50-51）：Copy 型文件身份。L54 有一行 `unsafe impl salsa::SalsaValue for FileId {}`——它同时是 Salsa 查询体系认可的值类型，这是 VFS 与增量数据库之间的粘合点。L57 定义 `MAX = 0x7fff_ffff`，`from_raw`（L60）与 `index`（L66）在裸整数与 newtype 间换算；L72 `impl nohash_hasher::IsEnabled` 允许它直接作 IntMap 的 key（恒等 hash）。
- **`FileState`**（L84-93）：三态——`Exists(u64)`（存活，附内容 hash）、`Deleted`、`Excluded`（被用户排除但保留身份，打开时仍可查询，见 L350-352 注释）。
- **`Vfs`**（L77-82）：`interner: PathInterner`（路径↔FileId 双向表）+ `data: Vec<FileState>`（以 FileId 为下标的状态槽）+ `changes: IndexMap<FileId, ChangedFile>`（变更日志，按插入序）。

`ChangedFile`（L96-166）是对外暴露的变更记录：`file_id` + `Change`（L182-189 的 `Create(Vec<u8>, u64)` / `Modify(Vec<u8>, u64)` / `Delete`，元组第二项是 FxHasher 内容 hash）。便捷判断有 `exists`（L106）、`is_created_or_deleted`（L112）、`is_modified`（L120）；`text()`（L135-142）把字节安全转成 `Arc<str>`，非法 UTF-8 退化为空串——VFS 层不因坏编码崩溃。构造器 `create/modify/delete`（L151-165）在录入时同步计算 hash。

配套模块在 L11-19 声明：`anchored_path`（相对某锚点文件的路径，供 `include` 解析）、`file_set`（FileSet/FileSetConfig，source root 的路径划分）、`path_glob`、`path_interner`、`vfs_path`（VfsPath：真实路径与虚拟路径的统一封装）。L33-41 把这些统一 re-export。

## 外部连接

上游消费者是 `src/global_state.rs`：`WorkspaceState.vfs` 字段（global_state.rs L104）以 `Arc<RwLock<(Vfs, IntMap<FileId, LineEnding>)>>` 持有，写者只有主循环的 `process_vfs_files`，读者是快照与 `process_changes`。`loader` 模块（loader.rs）定义接口契约：`Entry::Files/Directories`（L11-16）、`Directories { extensions, include, exclude }`（L29-33，注释写明最长匹配优先、exclude 覆盖 include）、`Config { version, load, watch }`（L37-48，version 用于把进度消息对齐到正确配置代）。后端通过 `Message`（L58-76）回报：`Progress { n_total, n_done, dir, config_version }`、`Loaded`（首次装载）、`Changed`（监听触发）。`trait Handle`（L82-97）只要求 `spawn/set_config/invalidate/load_sync` 四个方法，`SOURCE_FILE_EXTENSIONS`（L7）把 v/sv/vh/svh/svi/map 定为递归加载的扩展名集合。下游 `base_db::change::Change::apply` 消费 `take_changes` 的产物写入 Salsa 输入。

## 数据流

一次典型的「编辑器保存文件」旅程：

1. notify 后端侦测磁盘变化，发 `Message::Changed { files }`；
2. `event_loop.rs::process_vfs_files` 逐条调 `Vfs::set_file_contents(path, contents)`（本文件 L250-314）；
3. `set_file_contents` 先 `alloc_file_id`（L333-339，新路径分配 id，`data.resize` 填 `Deleted` 占位但不记变更）；然后 L254-269 按 `(旧状态, 新内容)` 二维决策：`Deleted+None` 直接 false；`Exists(hash)+Some(v)` 时 L261-266 先比 hash，相同返回 false——**内容未变的保存被原地吞掉**，下游不会产生任何失效；不同则构造 `Modify(v, new_hash)`；
4. L271-311 把变更并入 `changes` 表。`Entry::Occupied` 分支（L281-309）处理「同一文件一轮内多次变更」的合并代数：新 `Delete` 覆盖一切（L286）；`Create` 可吸收后续 `Create/Modify`（L288-291）；两个 `Modify` 塌缩为后者（L293-296）；`Delete` 后的 `Create` 语义等价 `Modify`（L298-300）。`set_data` 闭包（L271-276）同步刷新 `data` 槽；
5. 主循环随后 `take_changes()`（L317-319，`mem::take` 清空日志）拿到 `IndexMap<FileId, ChangedFile>`，经 `base_db::Change` 翻译成 `set_file_text_with_durability` 等输入写入。

查询侧：`file_id(&VfsPath) -> Option<(FileId, FileExcluded)>`（L210-218）按三态返回（Deleted 视为不存在，Excluded 返回 `FileExcluded::Yes`）；`file_path`（L225）反查；`iter`（L232-240）只迭代存活文件；`exists`（L322）panic-free 校验。`insert_excluded_file`（L353-356）为被排除文件保留身份。

## 设计决策

**为什么存 hash 而不存全文？** `FileState::Exists(u64)` 只保存 FxHasher 摘要（L84-87），全文在变更日志的 `Change` 里随消费即走。状态槽 8 字节/文件，百万文件也只是几 MB；而 set_file_contents 的去重（L261-266）需要 O(1) 判断「内容是否真的变了」，hash 是唯一便宜答案。代价是理论碰撞——工程上 FxHasher 64 位对编辑器场景足够。

**为什么 changes 是 IndexMap 且合并语义这么讲究？** 变更日志的消费周期是「一轮事件处理」（event_loop 每轮 `process_changes` 清空一次）。同一轮内 loader 可能既报 Modify 又报 Delete；不合并的话下游会看到中间态甚至倒退态。L279-311 的合并表保证日志语义等价于「按序应用到最终状态」，且 `Create→Delete` 在一轮内对外的净效果正确呈现为删除。

**为什么 Excluded 不直接删除？** L350-352 注释给出答案：客户端仍可能对被排除文件请求语义信息，彻底抹掉身份会让这些请求报「未知文件」；保留 id、标记 Excluded 让上层能优雅降级。

**为什么与 salsa 解耦？** Vfs 自己没有任何 Salsa 依赖（除了 FileId 实现 SalsaValue），读写都不进查询体系。输入提交走 `Change::apply` 这道显式边界（base-db/change.rs L35），保证「VFS 是纯数据结构 + 日志」这一最小契约，方便单测与复用。

## 新人提示

1. 排查「编辑没生效」类 bug 时，先看 `set_file_contents` 是否在 L263 的 hash 比较处提前返回 false——同内容保存静默跳过是特性不是 bug。
2. `take_changes` 是破坏性读取，每轮必须由唯一消费者调用；忘了调用会导致下一轮把旧变更重复应用（`data` 槽已更新但日志还在）。
3. VfsPath 分真实/虚拟两形态，`as_abs_path`（source_db.rs L188-192 消费它）返回 Option；在诊断归属、goto 定义跳转处务必处理虚拟路径（宏展开的 `/__vide/preproc/...` 就是虚拟路径）。
4. loader 的 `Config.version` 与 event_loop 的 `config_version` 断言（event_loop.rs L373 `always!`）联动：改 loader 协议时两边的版本语义要同步演进，否则旧进度消息会 panic。
