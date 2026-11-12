# 06 · 预处理模型与增量宏展开（crates/preproc-expand/src/db.rs + macro_file.rs）

## 角色定位

SystemVerilog 的宏系统（`define/`include/条件编译）是 IDE 世界的头号难题：一段 `FOO(1)` 展开后是完整的 module 声明，导航、补全、重命名都得能「走进展开里去」。`preproc-expand` 是 vide 对这道题的答案，也是图谱度数第二（db.rs 129 + macro_file.rs 92）的枢纽层。核心思路不是重写预处理器，而是**让 slang 在权威解析时顺手录下完整的预处理 trace**（事件流 + 发射 token 流），再建模成可查询的 Salsa 增量数据：`db.rs` 管解析与诊断查询，`macro_file.rs` 把「一次宏调用」升格为 `MacroFileId`——与普通文件平起平坐的虚拟 HIR 文件（`HirFileId::Macro`），让宏展开体复用整套 parse→lower 管线。L416-421 trait 文档给出定位：「派生的预处理、编译与宏展开查询；这是第一个语义数据库层」。

## 内部结构

**db.rs**（1511 行）的组织：L41-51 两个 interned key（`PreprocFileQueryKey{file_id}`、`PreprocProfileQueryKey{profile_id}`）——L37-40 注释解释 Salsa 0.28 tracked 函数要求 salsa-struct 参数，纯整数必须 intern 后才能当 key；L53-78 定义核心值类型 `ParsedCompilationUnit{syntax_tree, preprocessor_trace}`、`ParsedProfile{units}`（每单元带 `SyntaxTreeBufferIds`）；L80-111 是 buffer→FileId 映射辅助（`path_file_ids` 建 PathIdentityIndex、`insert_buffer_file_ids` 把 slang buffer id 翻回 VFS 文件）；L113-170 按文件/profile/光标三种粒度组装 `SyntaxTreeOptions`（L124 过滤文件自身，避免自 include）；L420-421 `pub trait PreprocDb: SourceRootDb {}` 加 L423-542 的查询面（20 个方法，从 compilation_plan 到 macro_reference_index）。

**macro_file.rs**（756 行）：L28-49 定义 trace 坐标系——`SourceEmittedTokenId(usize)`（发射 token 流下标）与 `SourceEmittedTokenRange{start, len}`（L41-44 注释：slang 把一次展开（含嵌套）的 token 连续发射，「首 token + 长度」完整刻画一次展开）；L52-55 `MacroCallLoc{model_file, trace_call}` 定位一次调用；L57-79 把 `MacroCallId` 与 `MacroFileId` 都做成 interned struct；L93-118 `ExpansionInfo{text, parse, source_map}` 与 `ExpandResult{value, err}`（错误不中断，产出部分结果）；L135-144 `ExpandErrorKind` 八种失败模式。L552-598 的 `TraceIndex` 是性能心脏：`expansion_by_call` 与 `emitted_range_by_expansion` 两表一次遍历建好，之后查询 O(1)。

## 外部连接

上游：`base_db`（CompilationContext、DiagnosticsConfig、profile）、`syntax`（SyntaxTree/Compilation/Trace）。平行依赖 `::preproc` crate（L3，SourcePreprocModel——纯 Rust 复算的预处理模型，管宏调用点索引与 source map）。下游：`hir-def` 经 `HirFileId::Macro` 无缝消费宏文件；`ide` 用 `macro_files_at_offset`（L170）做「展开预览/宏内跳转」，用 `file_macro_coverage` 灰显未激活分支。诊断流上，`parse_diagnostics`（L373-414）按 root buffer 过滤（L395-398，include 文件的诊断归它自己的文件），`compilation_diagnostics_from_compilation`（L633-731）把 slang 语义诊断经 `buffer_file_ids` 映射回 FileId 并按 config 过滤。

## 数据流

**权威解析**（L172-241 `parsed_compilation_unit`，tracked lru=128）：先查 profile 与 `CompilationPlan`；若文件是 plan 的 root（L177-194），直接从 `parsed_profile` 复用整批解析的树（注释：root 必须在权威 parse 里，找不到就 panic）；否则单文件走 `SyntaxTree::from_file_in_memory_with_options_and_trace`（L221-226）。**profile 级解析**（L243-308 `parsed_profile`，tracked lru=128）才是真权威：L258 `Compilation::new_with_top_modules(&context.top_modules)` 建 slang 会话，L259 `register_source_buffers` 把 plan 全部源注册进内存（未保存的 include 也来自内存而非磁盘），逐 root 解析并带走 trace 与 buffer_ids。**光标级解析**（L328-363 `parser_expected_syntax`，tracked lru=64）：注释钉版「期望语法是补全专属元数据，不进权威树」——按 offset 单独请求 slang 期望集合，fallback 拿到与权威 parse 相同的 profile buffers。**HirFileId 分派**（L544-559 `parse`）：`File(id)` 走 `parse_src_for_compilation`，`Macro(macro_file)` 走 `macro_expansion(macro_file).value.parse`——两类文件汇入同一条查询接口。

**宏展开**（L425-483）：`macro_expansion_query`（tracked lru=128）包 `macro_expansion`：查 model 拿调用 → 查 `trace_index` 拿 `emitted_range`（L461-469，无则报 ExpansionUnavailable）→ 空展开走 `expansion_text_for_empty_call`（L470-471），否则 `expansion_text_for_range` 拼展开文本 → `ExpansionSourceMap::from_trace_range`（L475-481）建双向映射 → `expansion_info`（L501-508）把文本再 parse 成 `SyntaxTree::from_file_in_memory(&text, "macro-expansion", "")`。入口 `macro_files_at_offset(db, file_id, offset)`（L170-238）经 `relevant_model_files`（L318-338：文件自身 + 相关 model 文件）逐 model 查 `macro_call_ids_at`，校验 trace_call 与 emitted_range 后 intern 出 MacroFileId。`TraceIndex::new`（L565-598）用 `expansion_parents` 传播祖先链（L582-590：token 属于自身展开及全部祖先展开）。

## 设计决策

**为什么「一次宏调用 = 一个虚拟文件」？** rust-analyzer 用每个宏调用一个 MacroFile 证明了这条路可以让展开体免费获得 parse/lower/index。vide 照搬：MacroFileId intern（L75-79）后，hir-def 的全部 per-owner 查询（body、item_tree）对 `HirFileId::Macro` 自动生效——语义索引甚至把宏生成的 module 纳入模块索引（macro_file.rs L241-246 文档：不发明第二条名字解析路径）。

**为什么展开文本来自 emitted_tokens 而非重新跑宏引擎？** slang 展开时已把每个发射 token 的 origin 记进 trace。`expansion_text_for_range` 按区间拼接 token 文本，保证与权威解析吃到的 token 完全一致（同一份事实的两次投影），且免去在 Rust 侧重实现 `` `define 语义。代价是必须信任 trace 完整——L222-230 对每个入口校验 emitted_range，失败降级为空列表并 warn。

**为什么补全期望要单独 parse？** L321-327 注释：期望集合挂在「权威树」上会让每个 recovery 窗口都污染树结构；cursor-scoped parse 把元数据限制在一次查询内。db.rs 测试 `parser_expectations_are_cursor_scoped_outside_authoritative_tree`（L989-999）锁定：权威树 `expected_syntax_at(28)` 为空而查询接口非空。

**为什么 buffer→FileId 映射按路径找？** slang 只认 buffer id；诊断要回到编辑器文件只能靠 path 对账（L99-111）。Predefine/内存 include 等「无 VFS 实体」的 buffer 映射成 `/__vide/preproc/...` 虚拟路径（测试 L1504-1510 钉版保留命名空间）。

## 新人提示

1. 改宏 bug 先分清三层事实：trace（slang 录制）、SourcePreprocModel（`::preproc` 复算）、ExpansionInfo（拼接产物）。三者的 call id 是不同体系（TraceMacroCallId vs MacroCallId），桥在 `MacroCallLoc`。
2. `parsed_compilation_unit` 对 plan root 的复用（L177-194）是硬约束：root 不在权威 parse 里会 panic 而非静默重 parse——「单一权威树」的守门员。
3. 新增依赖 trace 的查询务必经 `trace_index`，别直接扫 `trace.events`/`emitted_tokens`——注释（L554-557）明确是为把 O(n) 扫描变 O(1)。
4. 诊断「报错文件不对」九成是 buffer_file_ids 映射漏了：检查文件是否在 `path_file_ids`（被 ignored 的文件被 L90-92 跳过）以及 include 是否走内存 buffer。
5. db.rs 测试模块（L782-1511）是现成规格书：predefine 验证、重复 define、manifest 区间校验等边界都有断言可抄。
