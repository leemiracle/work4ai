# 06-syntax 精读手册

> 模块定位：`crates/syntax` 是 vide 中介于 slang-sys（C++ slang 解析器的 Rust 绑定）与上层（hir-def / ide / preproc / preproc-expand）之间的 **语法门面 crate**：把 slang_sys 原样 re-export 成稳定入口，并在其上补一层 rust-analyzer 风格的 IDE 工具集——TextRange 显示坐标（`HasTextRange`）、offset 定位（`token_at_offset` 家族）、跨解析树身份（`SyntaxNodePtr` 等）、名字提取（`HasName`）、模式宏（`match_ast!` / `Token!` / `Trivia!`）。它是全仓被 import 最多的 crate 入口（lib.rs 入边 141 条，全仓第一），但不含任何 salsa query——纯语法层，改动波及的是解析坐标系约定而非增量计算。

## `crates/syntax/Cargo.toml`（15 行）
**作用**：定义 syntax crate 元数据与依赖。
**关键字段**：`name = "syntax"`，`description = "Syntax facade and utilities over slang-sys"`（L4）；依赖仅 4 个：`either`（node/token 的 Either 返回值）、`serde`、`smol_str`（trivia caption）、`slang_sys = { package = "slang-sys", path = "../slang-sys" }`（L14，path 依赖本地绑定 crate）、`utils`（line_index 的 TextRange/TextSize）。
**改动的连带影响**：新增依赖会传染给全部 141 个 lib.rs 消费者的编译图；删 `either`/`smol_str` 需先改 node.rs L35 与 trivia.rs L66 的直接使用。

## `crates/syntax/src/lib.rs`（67 行）
**角色**：crate 根门面——模块声明 + slang_sys 全量 re-export + 自研 ext trait 的双路径导出。
**关键结构与不变量**：
- `pub mod has_name / has_text_range / ptr`（L5/L6/L8），`mod macros / mod slang_ext`（L7/L9，私有，宏经 `#[macro_export]` 提升、ext 经 L26-29 重导出）。不变量：**外部永不直接 touch slang_sys 的语法类型**，全部经由本 crate——这是坐标/身份语义的唯一改写点。
- `pub mod token`（L11）：`TokenKind/TriviaKind` + ext trait 的命名空间版导出（`SyntaxTokenExt, SyntaxTokenWithParentExt, TokenKindExt, pair_token`，L14-15）。
- `pub mod trivia`（L19）：`TriviaKind` + `TriviaExt, TriviaKindExt`。
- `pub type Trivia<'a> = SyntaxTrivia<'a>`（L25）。
- L26-29 根级重导出 `AstNodeExt, SyntaxCursorExt, SyntaxNodeExt, ...`（与 token/trivia 子模块双路径并存，消费者两种写法都合法——如 ide 用 `syntax::token::TokenKindExt`，hir-def 用 `syntax::SyntaxNodeExt`）。
- L30-38 re-export slang_sys::syntax 的 18 个类型（`SyntaxNode/Token/Tree/Cursor/Element/Kind/ast/WalkEvent...`）；L40-66 再开 `compilation/facts/source/value/diagnostics/preproc` 六个命名空间（preproc 额外并入 source_buffer 的 `SourceBufferId/Origin/Range/SyntaxTreeBufferIds`，L60-67）。
**公开 API**：上述模块 + 根级 ext traits。
**依赖/被依赖**：出边 13 条——本地 5 模块 + slang_sys 的 syntax/token/compilation/facts/source_buffer/value/diagnostic/preproc；入边 **141 条 imports**（全仓第一）：hir-def 约 40 文件、ide 约 70 文件、preproc/preproc-expand/base-db/hir-ty/hir-semantics/src(global_state、lsp_ext) 皆有。
**改动影响面**：re-export 清单增删 = 全仓 import 级联编译错误；`Token!` 宏路径（`$crate::TokenKind`）依赖 L37 的根级 `TokenKind` 导出，动它等于废掉 macros.rs。
**集成点**：二次开发者统一从 `use syntax::{...}` 进入；新 ext trait 应同时在根级与子模块导出（跟随现有双路径惯例）。

## `crates/syntax/src/has_name.rs`（136 行）
**角色**：为 15 类 AST 节点提供统一的"名字 token"提取 trait，抹平各节点取名字的形状差异。
**关键结构与不变量**：
- `pub trait HasName<'a>: AstNode<'a> { fn name(&self) -> Option<SyntaxToken<'a>> }`（L11-13）。不变量：返回**名字 token 本身**（非文本、非 node），None 表示该形状无名字。
- `ModuleDeclaration`（L15）走 `header().name()`——module 名在 header 子节点而非 decl 直接子级。
- `GenerateBlock`（L45-51）：`label().name()` 优先、`begin_name().name()` 兜底。
- `NonAnsiPort`（L53-64）：三分支 match——Explicit 取 name、Implicit 仅 `PortExpression::PortReference` 有名（Concatenation→None）、Empty→None。
- `ParamAssignment`（L90-97）：`OrderedParamAssignment` 恒 None（按位传参无名）。
- `FunctionDeclaration`（L119-136）：内嵌 `rightmost_name_token` 递归（L121-132）剥 `ScopedName` 链取**最右**标识符——`pkg::func` 的名字是 `func`；支持 IdentifierName/IdentifierSelectName 两形态。
**公开 API**：`HasName` + 15 个 impl（Module/Config/Udp/Library/BlockStatement/GenerateBlock/NonAnsiPort/PortReference/Declarator/IdentifierName/SpecparamDeclarator/ParamAssignment/PortConnection/HierarchicalInstance/Statement/FunctionDeclaration）。
**依赖/被依赖**：依赖 slang-sys syntax.rs 与 ast.rs；被 hir-def/{aggregate,owner,item_tree}.rs、ide/definitions.rs、lib.rs import。
**改动影响面**：改签名（如返回 SmolStr）直接打断 hir-def 三个核心文件与 ide 定义跳转；给新节点加 impl 不影响旧调用者。
**集成点**：新 DSL 形态节点要参与定义/引用索引时，先在此补 impl，再在 ide/definitions.rs 的泛型边界消费。

## `crates/syntax/src/has_text_range.rs`（89 行）
**角色**：把 slang 的 `SourceRange`（buffer 相对、可能跨 buffer）翻译成 `utils::line_index::TextRange` 显示坐标——全 IDE 层定位的坐标系基石。
**关键结构与不变量**：
- `pub(crate) trait SourceRangeExt::to_text_range_in_root(self, root)`（L7-9，impl L11-23）：**不变量**——`start_buffer_id` 与 `end_buffer_id` 都必须等于 root 的 buffer id（L15-17）否则 None（跨 buffer 无显示坐标）；u32 收窄失败→None；`start <= end` 才构造（L21）。
- `fn root_node`（L25-30）：沿 parent 爬到根。
- `pub trait HasTextRange::text_range(&self) -> Option<TextRange>`（L32-47）：doc 注释钉死两条语义（L33-46）——①显示坐标：宏展开 token 的 range = **宏调用点整体**（parser 消费 token 流，展开文本无物理 offset），故 `token_at_offset` 在宏展开内部不可靠，应改用 `preprocessor_trace_emitted_token().emitted_token_index`；②跨多 buffer（如 `expand_includes: false` 的树）返回 None。
- impl for `SyntaxNode`（L58-64）：`range_with_context(root)` 优先、裸 `range()` 兜底，再经 `to_text_range_in_root` 收敛——**带上下文优先**保证宏 token 映射回调用点。
- `pub trait HasTextRangeIn<'a>`（L54-56）+ impl for `SyntaxToken`（L66-71）：给裸 token 显式指定上下文 node，包成 `SyntaxTokenWithParent` 再取 range——用于"生成式 AST getter 仍返回裸 token"的边界。
- impl for `SyntaxTokenWithParent`（L73-79）与 `SyntaxElement`（L81-89，双分支转发）。
**公开 API**：`HasTextRange`、`HasTextRangeIn`。
**依赖/被依赖**：依赖 slang-sys source_buffer.rs/syntax.rs、utils/line_index.rs；**入边 55 条**——ide 的 hover/inlay_hint/folding/formatting/code_lens/signature_help/references/semantic_tokens/selection_ranges/约 25 个 code_action handler + hir-def 的 lower/item_tree/region_tree/pathres/checker/ast_id_map + 本 crate ptr.rs/node.rs。
**改动影响面**：这是改动波及面最广的文件之一；改 None 语义（如跨 buffer 回退裸 range）会让 `expand_includes:false` 场景的 IDE 定位行为整体变化；`SyntaxElement` impl L81 若漏分支会编译期报 exhaustive match 错（安全）。
**集成点**：任何新 LSP feature 取 token 范围一律走 `HasTextRange`；持有裸 `SyntaxToken` 的旧 API 边界用 `HasTextRangeIn::text_range_in(context)`。

## `crates/syntax/src/macros.rs`（97 行）
**角色**：三个 `#[macro_export]` 声明宏——AST 模式分派与 token/trivia 字面量速记。
**关键结构与不变量**：
- `match_ast!`（L2-21）：三臂——`_ => body` 终止臂；`$path:ty[$it:pat] $(if $cond:expr)? => body`（cast 成功**且**可选 guard 才进，L5-12，注意 `[$it:pat]` 是绑定模式不是数组）；`$path:ty $(| $paths:ty)* => body`（多类型任一 cast 成功即进，不绑定值，L14-20）。递归展开为 if-else 链，`$crate::ast::AstNode::cast` 保证宏在任意 crate 可用。
- `match_ast_kind!`（L24-43）：同构，但吃 `SyntaxKind` 用 `can_cast`（L28/L37）——用于只有 kind 没有节点的场合（如 hir-def/symbol.rs L300、ide/inlay_hint.rs L88）。
- `Token!`（L46-88）：约 40 条 token 字面量→`$crate::TokenKind::*` 映射（`[.]`→DOT、`[::]`→DOUBLE_COLON、`["`\""]`→MACRO_QUOTE L62、`[**]`→DOUBLE_STAR L57、`[$unit]`/`[$root]`→UNIT/ROOT_SYSTEM_NAME L60-61、关键字 `[always]/[posedge]/[pulsestyle_ondetect]` L84 等）。
- `Trivia!`（L91-97）：`[ws]/[eol]/[lc]/[bc]/["`"]` 五种 trivia 速记。
**公开 API**：仅三个宏（macro_export 到 `syntax::` 根）。
**依赖/被依赖**：出边 0（纯宏，无 use）；实际消费者：`match_ast!`/`match_ast_kind!` 在 ide/definitions.rs L85、ide/inlay_hint.rs L88/L93、ide/signature_help.rs L79、hir-def/{symbol,item_tree,region_tree,body}.rs；`Token!`/`Trivia!` 遍布 ide/completion（context.rs L320、engine/member.rs L55/81/98、context/lex.rs L18-20 等）与 semantic_tokens。
**改动影响面**：改宏内部展开形（如 `$crate::ast` 路径）需保证 lib.rs 根级 `ast` 导出在（L35）；删某条 Token! 映射 = 对应消费者编译错；新增映射零风险。
**集成点**：写新 code_action/completion 时用 `syntax::Token![.]` 代替裸 `TokenKind::DOT` 提升可读性；多类型分派用 `match_ast!` 的 `$(| $paths)*` 臂。

## `crates/syntax/src/ptr.rs`（199 行）
**角色**：定义与解析树实例解耦的语法元素身份（"指针"），供 salsa 侧把语法位置冻结进 intern ID。
**关键结构与不变量**：
- `SyntaxNodePtr`（L13-16）：`(kind: SyntaxKind, range: TextRange)` 二元组身份，`Copy + Eq + Hash + Ord`（Ord：kind → start → end，L24-31）。不变量：`from_node`（L35）对 `text_range().unwrap()` 直接 unwrap——**构造前提是该 node 有显示坐标**（跨 buffer node 会 panic）。
- `to_node`（L40-56）：先 `root.elem_at_exact_range(range)` 精确命中，再循环**只沿同 range 的 wrapper 下钻**（L46-55，注释 L43-44：SyntaxList 包装层可与语义子节点同 range；绝不整树扫描）。不变量：下钻层数受同 range 链长度约束，宏区域因所有 token 同 range 需注意。
- `SyntaxTokenPtr`（L80-83）：`(TokenKind, TextRange)`。doc（L69-78）钉死边界：普通源 token 可靠；**宏展开 token 全部上报调用点 range**，同 `(kind, range)` 可撞车，`to_token`（L109-113，`token_at_offset(range.start())` 后按 kind+range 过滤）可能解析错 token——宏内身份必须用 `preprocessor_trace_emitted_token().emitted_token_index`。
- `SyntaxElementPtr`（L125-128）：`Node(SyntaxNodePtr) | Token { parent: SyntaxNodePtr, tok: SyntaxTokenPtr }`；`from_element`（L131）/`to_elem`（L143，Token 臂忽略 parent ptr 直接按 tok 定位）/`kind()`（L150）。
- 内联 `#[cfg(test)] mod tests`（L158-198）：`no_include_expansion_parse_does_not_expand_cwd_includes`——用 `SyntaxTreeOptions::without_include_expansion()` 解析带 `` `include `` 的文本，断言不产生 TypedefDeclaration 成员（即不读 CWD 文件）、module 的 `text_range().is_some()`（L186-192）。
**公开 API**：三个 ptr 类型 + from/to 双向转换 + `kind()/range()` 访问器。
**依赖/被依赖**：依赖 slang-sys syntax.rs/token.rs、utils/line_index.rs、crate has_text_range（`SyntaxNodeExt` 经 slang_ext re-export）；被 hir-def/{ast_id_map,source_projection}.rs、ide/{range,semantic_index,semantic_index/build,references/search}.rs、本 crate ast_node.rs/node.rs/lib.rs import。
**改动影响面**：`SyntaxNodePtr` 是 `AstIdMap`/`SourceAstId` 的身份底座——改 Ord 语义会破坏 BTreeMap 排序相关逻辑；改 `(kind,range)` 结构会牵动 hir-def 的 item 定位与 ide 的 range 映射。
**集成点**：新 query 要跨 revision 记住"某个语法位置"时，存 ptr 而非借用 node；恢复时 `to_node(tree)`。

## `crates/syntax/src/slang_ext.rs`（17 行）
**角色**：ext 子模块的组织者：声明 7 个子模块（L1-7，其中 `pub mod support/token/trivia`，`mod ast_node/cursor/node/token_at_offset`）+ `pub use *_` 扁平重导出（L9-14）+ 测试挂载（L16-17）。
**关键结构与不变量**：扁平 re-export 使 crate 外只见 trait 名不见子模块路径（配合 lib.rs L26-29）。
**公开 API**：经 `pub use` 暴露全部子模块公开项。
**依赖/被依赖**：出边 6（六个子模块）；入边 4：lib.rs、token.rs、ptr.rs、tests.rs。
**改动影响面**：新增 ext 文件需在此登记 `mod` + `pub use`，漏了即对外不可见。
**集成点**：扩展语法工具的注册点。

## `crates/syntax/src/slang_ext/ast_node.rs`（17 行）
**角色**：给所有 `AstNode` 提供 `to_ptr()` 桥接。
**关键结构与不变量**：`pub trait AstNodeExt { fn to_ptr(&self) -> SyntaxNodePtr }`（L5-7）；blanket impl `impl<'a, T: AstNode<'a>> AstNodeExt for T`（L9-16）——任何 AST 节点零成本获得 ptr 化（内部 `SyntaxNodePtr::from_node(self.syntax())`，L15）。
**公开 API**：`AstNodeExt::to_ptr`。
**依赖/被依赖**：依赖 ptr.rs 与 slang-sys/syntax.rs；被 slang_ext.rs（→lib.rs 根级导出）。
**改动影响面**：语义上等价 ptr.rs 的 `from_node`；删除会打断所有 `.to_ptr()` 调用点（hir-def lower/ide 索引构建大量使用）。
**集成点**：lower 阶段把 AST 节点登记进 `AstIdMap` 的标准入口。

## `crates/syntax/src/slang_ext/cursor.rs`（66 行）
**角色**：`SyntaxCursor`（slang-sys 的树游标）的 offset 导航扩展——三个"定位到 offset 附近 token"原语，是 node.rs 全部定位算法的引擎。
**关键结构与不变量**：
- `pub trait SyntaxCursorExt`（L4-10）：`goto_first_tok_after / goto_first_tok_after_or_last / goto_last_tok_before`，均 `&mut self` 就地移动、返回 bool 成功位。
- `goto_first_tok_after`（L13-30）：先看当前 elem range（L15 `to_elem().range()` 为 None 即失败）；`end <= offset` 返回 false（L18-20）；然后循环 `goto_first_child_after_pos(offset)` 下钻直到 `to_node().is_none()`（L22-27），收尾 `debug_assert!(to_token().is_some())`（L28）。
- `goto_first_tok_after_or_last`（L32-46）：失败补救分支——仅当当前 elem 的 `end == offset` 时改用 `goto_last_child()` 一路钻到底（L34-40），即"offset 恰在树末尾"时给出最后一个 token 而非 None。
- `goto_last_tok_before`（L48-65）：对称的左侧版本——`start >= offset` 失败（L53-55），循环 `goto_last_child_before_pos(offset)`。
**公开 API**：`SyntaxCursorExt` 三方法。
**依赖/被依赖**：依赖 slang-sys/syntax.rs（SyntaxCursor）与 utils/line_index.rs（TextSize）；被 node.rs 消费（L13-17 引入）。
**改动影响面**：改这三个原语 = 动 node.rs 的 `token_at_offset/token_or_node_at_offset/trivia_kind_at_offset` 的底层搜索行为，直接影响 LSP 光标定位精度（hover/completion/goto 的 offset 语义）。
**集成点**：自定义树遍历要按 offset 跳 token 时复用它们，别手写 goto 循环。

## `crates/syntax/src/slang_ext/node.rs`（414 行）★ 本单元核心
**角色**：`SyntaxNode` 的 IDE 定位扩展 trait——offset→token/node 的全套查询，IDE 层每一次"光标在哪个 token/哪个 AST 节点"都经此。
**关键结构与不变量**：
- `pub trait SyntaxNodeExt<'a>`（L23-42）12 个方法，impl for `SyntaxNode`（L44-414）。
- `elem_at_exact_range`（L45-64）：游标下钻，elem range 必须包含目标 range（L52），相等即返回（L56-58），`goto_first_child_after_pos` 失败→None。被 ptr.rs `to_node` 与 ide/render.rs 使用。
- `covering_element`（L66-87）：找**最小覆盖** range 的 elem；不包含时回退 `goto_parent()` 后返回（L73-76）；token 即终点（L79），node 继续钻（L81）。
- `token_at_offset`（L89-164）：**双路径**。单 buffer 快路径（L90-124）：范围空/不含 offset→None；`goto_last_tok_before` 找左 token（L100），左 range 含 offset→`Single`（L102-106）；否则重置游标找右 token（L109-113），按 `(left_end==offset, right_contains)` 四象限产出 `Single/Between/None`（L115-123）。多 buffer 慢路径（L126-164）：注释 L126-129 钉死原因——**slang 原生 offset 只在单个 source buffer 内可比较**，include/macro 展开的树交错多 buffer，改用显示坐标线性扫 `self.tokens()`（L132-151：`contains` 且 `start != offset` 即 Single；end==offset 记 left；start==offset 记 right）。
- `token_at_offset_including_eof`（L166-182）：先走普通版，None 且 offset==range.end 时回退 `token_before_offset` 的尾 token——覆盖"光标在 EOF 处"。
- `token_after_or_at_offset`（L184-204）/`token_before_offset`（L206-224）：同样单 buffer 游标快路径 + 多 buffer 线性扫描两分。
- `trivia_kind_at_offset`（L226-287）：内层 helper（L227-263）逐条扫 token 的 `trivias_with_range`；**DIRECTIVE 特例**（L238-259）——directive trivia 有自己的语法子树，先试其整体 range（L241-246），再递归进其 first token 的嵌套 trivia（L249-258）。外层按"token 之前/之后双向试 + 最后 token 兜底"（L265-286，注释说明 trivia 可能挂在任一侧，trivia-only 文件靠最后 token）。
- `find_node_at_offset<N: AstNode<'a>>`（L289-332）：种子集合 = covering_element 的 node/parent（L311-312）+ 前后 token 的 parent（L313-317），对每个种子沿 `SyntaxAncestors` 找**最短**能 cast 成 N 的祖先（`best_match_in_ancestors` L290-308，按 range 长度最小者胜，无 range 记 u32::MAX 视为最差）。
- `token_or_node_at_offset`（L334-385）：`Either<TokenAtOffset, SyntaxNode>`；四象限全失败时（L372-383）沿 `goto_parent` 上爬找第一个 range 含 offset 的 node——覆盖"光标落在纯 trivia/结构洞里"。
- `find_root`（L388）、`to_ptr`（L393）、`trivias`/`trivias_with_range`（L398-413，node 无 first_token 时空迭代器，`Either` 统一返回类型）。
**公开 API**：上述 12 方法（trait 对 `SyntaxNode<'a>` 实现）。
**依赖/被依赖**：依赖 slang-sys syntax.rs/ast.rs/token.rs、utils/line_index.rs、crate cursor.rs/token.rs/token_at_offset.rs/has_text_range.rs/ptr.rs；被 slang_ext.rs→lib.rs 导出；全仓消费者：`find_node_at_offset` 31 文件、`token_at_offset` 11 文件、`covering_element` 5 文件。
**改动影响面**：改 `token_at_offset` 的 Between 判定 = 改全 IDE 光标语义（completion 的 caret.rs、hover、definitions 的 `pick_best_token` 全部连锁）；多 buffer 慢路径（L132 线性扫）是性能敏感点，include 重型文件上 O(n_tokens)。
**集成点**：新 LSP feature 取上下文的第一入口；`find_node_at_offset::<N>` 的泛型形式可直接要"最内层某类节点"。

## `crates/syntax/src/slang_ext/support.rs`（13 行）
**角色**：无状态小工具箱（当前仅一个函数）。
**关键结构与不变量**：`pub fn child_token(parent: SyntaxNode, kind: TokenKind) -> Option<SyntaxToken>`（L7-13）——在直接 children 里找**第一个**指定 kind 的 token，返回裸 `SyntaxToken`（剥掉 WithParent包装，L12 `.map(|tok| tok.tok)`）。不变量：只查直接子级、不递归、同名 kind 取首个。
**公开 API**：`child_token`。
**依赖/被依赖**：依赖 slang-sys syntax.rs/token.rs；仅被 token.rs（`pair_token` 的 P! 宏）消费。
**改动影响面**：极小；改返回类型会牵 pair_token。
**集成点**：pair-token 配对查找的共享原语。

## `crates/syntax/src/slang_ext/token_at_offset.rs`（63 行）
**角色**：offset 定位的结果类型——rust-analyzer `TokenAtOffset` 的移植。
**关键结构与不变量**：
- `pub enum TokenAtOffset<'a>`（L4-8）：`None | Single(SyntaxTokenWithParent) | Between(left, right)`（Between = offset 恰落在两 token 边界上，两个都算命中）。
- `pick_best_token(f: impl Fn(TokenKind) -> usize)`（L12-27）：按权重函数在 Between 二选一（`f(a.kind()) > f(b.kind())` 取 a 否则 b，L20-25，平手偏右）。
- `left_biased`（L30-37）：偏向左侧 token 的快捷解包。
- `impl Iterator`（L39-63）：消费式迭代（`std::mem::replace(self, None)` L43），Between 先吐 left 剩 Single(right)；`size_hint` 精确 0/1/2。
**公开 API**：enum + 两方法 + Iterator。
**依赖/被依赖**：依赖 slang-sys syntax.rs/token.rs；被 node.rs、lib.rs、ide/completion/context/caret.rs 消费；`pick_best_token` 另被 ide/{definitions,selection_ranges,semantic_target}.rs 使用。
**改动影响面**：增变体是 breaking（match 穷尽性）；Iterator 语义使 `TokenAtOffset` 被 move，调用处不能复用。
**集成点**：completion 上下文判定的标准返回类型；配 `pick_best_token` + 自定义 kind 权重表决定光标归属。

## `crates/syntax/src/slang_ext/token.rs`（191 行）
**角色**：token 层扩展：TokenKind 分类判定、word-like 识别、配对关键字跳转（`pair_token`）、trivia 显示坐标化。
**关键结构与不变量**：
- `pub trait TokenKindExt`（L13-17，impl L19-58）：`is_pair_token`（L20-39，BEGIN/END、MODULE/END_MODULE、CASE/END_CASE、FUNCTION/END_FUNCTION、GENERATE/END_GENERATE、INTERFACE/END_INTERFACE、TASK/END_TASK 七对）；`name_like`（L42-44，IDENTIFIER|SYSTEM_IDENTIFIER）；`is_literal`（L47-57，六种字面量）。
- `pub trait SyntaxTokenWithParentExt<'a>`（L60-65，impl L67-80）：`is_word_like`（L69-74——kind 是标识符类直接 true，否则按 **SystemVerilog 标识符词法**手工扫描 value_text：`$` 开头允许（系统名）、后续 `[a-zA-Z0-9_$]`，L83-105）；`trivias_with_range`（L77-80，委托 `trivias_with_range_in_root(parent.find_root())`）。
- `pub fn pair_token(SyntaxTokenWithParent) -> Option<Either<beg, end>>`（L109-161）：注释 L107-108 钉死约定——`Left`=beg token、`Right`=end token。局部宏 `P!`（L114-131）对六对同父关键字做双向配对（`support::child_token` 找兄弟）；**module 特例**（L133-147）：`module` 关键字在 header 里，配对的 `endmodule` 要先 `ModuleDeclaration::cast(parent.parent()?)` 上跳再取（L136-137）；反向 `endmodule`→header 的 `module_keyword`（L139-147）。
- `pub trait SyntaxTokenExt<'a>`（L163-168，impl L170-191）：`trivias_with_range_in_root(root)`——`trivias_with_loc()` 逐条按 `loc.buffer_id == root_buffer_id` 过滤（L181-183，跨 buffer trivia 无显示坐标）后转 TextRange。
**公开 API**：三个 trait + `pair_token`（lib.rs token 子模块与根级双导出）。
**依赖/被依赖**：依赖 slang-sys syntax.rs/token.rs、utils/line_index.rs、crate slang_ext（node ext）与 support.rs；被 node.rs 与 lib.rs；外部消费者：ide/token.rs（`syntax::pair_token` L43、`is_pair_token` L17）、ide/{semantic_index,definitions,hover,rename,completion/lex}.rs 用分类谓词。
**改动影响面**：`pair_token` 的 Either 方向约定若翻转，ide/token.rs 的跳转方向反转；`is_word_like` 词法定义改动影响 completion 触发条件与 rename 资格判定。
**集成点**：新配对关键字（如 class/endclass）在 P! 表 L149-156 加一行即接入跳转；语义谓词供索引层复用。

## `crates/syntax/src/slang_ext/trivia.rs`（95 行）
**角色**：trivia（空白/注释/directive）分类谓词 + VS Code 风格 `//region` 折叠区识别。
**关键结构与不变量**：
- `pub trait TriviaKindExt`（L6-12，impl L14-34）：`is_whitespace/is_eol/is_comment/is_lc/is_bc` 五谓词。
- `pub trait TriviaExt`（L36-40，impl L45-95）：作用于 `SyntaxTrivia<'_>`。
- `is_region_begin`（L47-67）：**三态返回** `Option<Option<SmolStr>>`——外层 None=不是 region 注释；`Some(None)`=无标题裸 `//region`（L62-64）；`Some(Some(caption))`=带标题。解析链（L56-60）：仅 LINE_COMMENT → strip `//` → trim → strip 前缀 `region`（常量 L42）→ **下一字符不得是字母数字/下划线**（L57-59，防 `//regional` 误报）→ strip `:` 取标题。`unsafe str::from_utf8_unchecked` 前有 `debug_assert` UTF-8 校验（L53）。
- `is_region_end`（L70-80）：`//` 后 trim_start 以 `endregion`（L43）开头即真。
- `as_comment`（L83-94）：LINE 剥 `//`、BLOCK 剥 `/*`+`*/`，trim 后返回内部文本；其他 kind→None。
**公开 API**：两 trait（lib.rs trivia 子模块与根级导出）。
**依赖/被依赖**：依赖 slang-sys syntax.rs/token.rs（SyntaxTrivia/TriviaKind）+ smol_str；消费者：hir-def/region_tree.rs（`is_region_begin/is_region_end/as_comment/trivias_with_range/find_root`——折叠区树构建）、ide/folding_ranges.rs、ide/render.rs（`as_comment`）、ide/{selection_ranges,formatting}（`trivias_with_range`）。
**改动影响面**：region 语法解析变化直接改折叠区行为（region_tree 是 HIR 侧持久结构）；`as_comment` 改 trim 行为影响 hover 文档注释渲染。
**集成点**：自定义注释指令（如 `//vide-ignore`）应仿 `is_region_begin` 的三态模式在此扩展。

## `crates/syntax/src/slang_ext/tests.rs`（34 行）
**角色**：slang_ext 的回归测试模块（`#[cfg(test)] mod tests` 挂载于 slang_ext.rs L16-17）。
**覆盖行为**：单测 `token_at_offset_inside_macro_invocation_does_not_descend_forever`（L9）——带 `predefines: vec!["CA_WIDTH=8"]`（L17）解析宏参数用法，断言 `token_at_offset` 落在 `` `CA_WIDTH `` 内部时返回 `TokenAtOffset::Single` 且 kind 为 `INTEGER_LITERAL`（L30-33）：守护"多 buffer/宏展开坐标下定位不无限下钻、且映射回宏实参 token"这条 token_at_offset 核心语义。
**跑法**：`cargo test -p syntax`（连同 ptr.rs 内联测试 `no_include_expansion_parse_does_not_expand_cwd_includes` 一起跑）。

---
*行号锚自检：`HasName` L11 / `to_text_range_in_root` L13 / `match_ast` L2 / `Token!` L46 / `SyntaxNodePtr` L13 / `to_node` L40 / `AstNodeExt` L5 / `goto_first_tok_after` L13 / `token_at_offset` L89（多 buffer 注释 L126）/ `pick_best_token` L12 / `pair_token` L109 / `is_region_begin` L47——抽 3 个（ptr.rs L40、node.rs L126、token.rs L109）已对源码复核无误。*
