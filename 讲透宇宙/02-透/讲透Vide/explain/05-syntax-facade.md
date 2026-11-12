# 05 · syntax 门面：统一语法树 API（crates/syntax/src/lib.rs）

## 角色定位

`crates/syntax` 是图谱度数全仓第一（154）的文件——因为几乎所有语义代码都从这里 import 语法类型。它的定位在 L1-2 两行文档写尽：「re-export slang-sys 的 API，并在其上提供一些工具」。这不是简单的转发层：slang 的语法树天然带 C++ 血统（区间跨 buffer、token 无稳定身份、宏展开 token 无物理位置），而 IDE/HIR 需要的是「单文件坐标系、可做 Map key、可定位光标」的树。本 crate 的工作就是把前者的棱角磨成后者：`has_text_range` 统一坐标系、`ptr` 提供跨快照身份、`slang_ext` 补齐遍历与定位工具、`has_name` 抽象命名节点。它让下游 18 个 crate 不必各自感知 slang 的怪癖。

## 内部结构

lib.rs 的 67 行是一次精心的「货架摆放」：

- **工具模块**（L4-9）：`has_name`、`has_text_range`、`ptr`、`slang_ext`（+内部 macros）；
- **token/trivia 分域 re-export**（L11-23）：`pub mod token` 把 `slang_sys::token::{TokenKind, TriviaKind}` 与本地扩展 trait（SyntaxTokenExt/TokenKindExt/pair_token）分层组织——同名扩展从 `slang_ext` 的不同子模块进入两个域，避免命名冲突；
- **核心类型批发**（L25-38）：L26-29 re-export slang_ext 的 11 个扩展 trait 与 `TokenAtOffset`；L30-38 一次性转售 slang_sys::syntax 的全部 27 个类型（SyntaxNode/SyntaxToken/SyntaxTree/SyntaxElement/WalkEvent/ast 等）与 token 枚举；
- **领域子门面**（L40-67）：`compilation`、`facts`（SemanticFacts/SyntaxFacts）、`source`（SourceLocation/SourceRange）、`value`（SVInt/Bit/TimeUnit）、`diagnostics`、`preproc` 六个命名空间，把 slang-sys 里平铺的模块按语义重新归架。

三个支撑文件的分工：

**has_text_range.rs** 定义坐标系契约。核心 trait `HasTextRange`（L32-47）的文档注释是全 crate 最重要的知识：`text_range()` 返回「编辑器显示坐标」——对宏展开 token，区间是**调用点**而非展开文本中的位置（解析器消费的是 token 流，展开 token 没有物理偏移），因此在宏展开内部做光标定位不可靠，应该匹配 `preprocessor_trace_emitted_token().emitted_token_index`；跨 buffer 的元素返回 None。实现侧 L7-23 的 `SourceRangeExt::to_text_range_in_root` 检查起止 buffer 都等于根 buffer 才换算成 `utils` 的 TextRange；L58-88 给 SyntaxNode / LocatedSyntaxToken（即 SyntaxTokenWithParent）/ SyntaxElement 各自实现，均先爬到根（L25-30 `root_node`）再校验。

**ptr.rs** 提供「树外身份」。`SyntaxNodePtr { kind, range }`（L12-16）是 Copy + Hash + Ord 的轻量指针；`to_node`（L40-56）在目标树中按精确区间定位（L42 `elem_at_exact_range`），再沿「同区间 wrapper」下钻直到 kind 匹配（L46-55 的 loop，注释警告 SyntaxList 包装可能与语义子节点同区间，只下钻不整树扫描）。`SyntaxTokenPtr`（L80-83）文档同样钉版：宏展开 token 共享调用点显示区间，`(kind, range)` 不再是唯一身份。L124-128 `SyntaxElementPtr` 把两者 union。

**slang_ext/**（node.rs 等）补齐 IDE 眼中最常用的定位原语：`SyntaxNodeExt` 的 `token_at_offset`/`token_at_offset_including_eof`/`token_after_or_at_offset`/`token_before_offset`/`token_or_node_at_offset`（node.rs L26-32 声明，L89/L166/L184/L206/L334 实现）。

## 外部连接

上游是 `slang_sys`（全部类型的源头）；下游几乎无死角：`preproc-expand`（解析与宏）、`hir-def`（lowering 读 ast）、`hir-semantics`（source_to_def 在树上爬祖先）、`ide`（补全/高亮/重构定位）。`utils::line_index::TextRange/TextSize` 是坐标类型的统一来源（L5、L8 引用），保证语法层与 LSP 换算层共用同一坐标系。`facts` 子模块（L44-46）把 slang 的语法事实表（何种节点可声明何种成员）暴露给 ide 的 verilog_2005 兼容层与补全 keywords。

## 数据流

以「找光标处的标识符」为例（goto 定义、hover、补全都走这条路）：调用方拿到 `Semantics::parse_file(file_id)` 的 root SyntaxNode → `root.token_at_offset(offset)`（slang_ext/node.rs L89，返回 `TokenAtOffset`：Between 两个 token 或 At 一个）→ 对 token 调 `text_range()`（has_text_range.rs L73-79，需带 parent 定位根 buffer）得到 TextRange → 需要「这是哪个 AST 节点」时用 `SyntaxAncestors` 或 `find_node_at_offset::<N>`（hir-semantics/semantics.rs L72-88）。若要把结果存进索引或跨快照传递，则 `SyntaxNodePtr::from_node(node)`（ptr.rs L35-37）做成值，之后 `ptr.to_node(&tree)` 复原。宏文件里的 token 走例外通道：`SyntaxTokenPtr` 不可靠，改用 preproc trace 的 emitted_token_index（第 6 篇详述）。

## 设计决策

**为什么坐标系选「根 buffer 显示坐标」而非 slang 原生 SourceRange？** LSP 的位置必须落在用户正在看的文件里。slang 的 SourceRange 是 (buffer_id, start, end)，跨 include 的树里节点散布多个 buffer；`to_text_range_in_root` 的单 buffer 校验（L15-16）把「不可表达」显式化为 None，强迫每个消费方决定降级策略，而不是给出一个看似合法实则错位的区间。这是把宏/include 的复杂性挡在 IDE 门槛外的第一道闸。

**为什么 Ptr 是 (kind, range) 而不是树内指针？** Salsa 缓存的值不能借用语法树（树由 SharedPtr 拥有、可被 LRU 驱逐）。Ptr 是纯值，可进 HashMap/快照/快照测试。`to_node` 的「同区间 wrapper 下钻」（L46-55）用受控的局部搜索解决 SyntaxList 与子节点同区间的歧义，避免全树扫描的性能陷阱——注释原文「never scan the whole tree」。

**为什么扩展 trait 分 token/trivia 两域？** 同名扩展（如 SyntaxTokenExt 同时存在于 slang_ext::token 与顶层 re-export）按消费习惯分路径：写 token 逻辑时 `use syntax::token::SyntaxTokenExt`，写节点逻辑用顶层。lib.rs L14-16 与 L26-29 的双层组织让两批 import 都合法。

**为什么不直接让下游依赖 slang-sys？** 门面切断了「下游 ↔ slang-sys 内部结构」的耦合：slang 升级若改变 buffer 语义，修改集中在 has_text_range.rs 一处；lib.rs 的子门面（L40-67）也给了 `syntax::diagnostics::*` 这类稳定路径，ide 不必感知 slang_sys::diagnostic 的模块重排。

## 新人提示

1. **宏展开内的 range 不可当身份用**——has_text_range.rs L36-43 与 ptr.rs L70-78 两处文档反复钉版；凡是处理 `MACRO 展开 token 的查询，直接查 trace 的 emitted_token_index。
2. `text_range()` 返回 Option：跨 buffer（`expand_includes: false` 的树、include 展开节点）时为 None。IDE 代码里的每个 unwrap 都该自问「真的单 buffer 吗」。
3. 新加扩展 trait 时记得在 lib.rs 对应域 re-export（L11-23 或 L26-29），否则下游只能写全路径，图谱度数会误判耦合点。
4. 判断「两个 token 是不是同一个」：普通源码用 SyntaxTokenPtr 足够；写快照测试时 ptr.rs L18-31 的 Ord 实现（kind → start → end）保证了稳定排序，可以放心 assert 顺序。
5. 想看这套 API 的最小用法，slang-sys/src/syntax.rs L26-52 的测试（从 parse 到 root().kind() 断言 MODULE_DECLARATION）就是现成模板。
