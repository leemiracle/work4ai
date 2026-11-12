# 10 · 补全引擎：completion 的 context→request→provider 流水线

## 角色定位

补全是 IDE 里「延迟预算最苛刻」的功能：用户每敲一个字符都在等它。vide 的 `crates/ide/src/completion/` 用三段流水线应对——**context 识别**（我在什么语法位置？）、**request 规划**（该由哪些 provider 供给？）、**provider 执行 + 候选过滤**。`engine.rs` 是总装（53 行），`context.rs` 与 `context/` 做第一阶段，`request.rs` 第二阶段，`engine/plan.rs` 与 `engine/` 下 16 个模块第三阶段。最大特点是**把 slang 解析器的「期望语法」当指挥棒**：context 判据大量来自 slang 对光标处的期望集合（`ParserExpectedSyntax`），而非自造「向前看 N 个 token」启发式。

## 内部结构

**engine.rs**（53 行）：入口 `completions(db, position, trigger)`（L31-41）先分流——manifest 文件走 `crate::manifest::completions`（L36-38）；其余经 `completion_context` 造上下文后进 `completions_with_context`（L43-53）：`CompletionRequest::from_context(ctx)` 规划不出 provider 就返回空（L48-50），否则 `plan::complete_request` 收尾。

**context.rs + context/**：`LexContext` 五态（L24-31：Code/LineComment/BlockComment/Literal/PreprocDirective）；`TriggerChar` 九种触发字符（L33-44：Dot/OpenParen/Comma/At/Hash/Dollar/Backtick/Apostrophe/Newline）；`ExpectedSyntax` 二十种期望（L46-69，DirectiveName/Keyword(ctx)/Expression/PortConnectionName/MemberName/EventControl…）。产物 `CompletionContext`（L76-84）：`replacement: TextRange`（被替换区间）、`prefix: String`（已敲前缀）、trigger、lex、expectations、`in_decl_name`。构造函数 `completion_context`（L91-122）并行收集五路信号——`Semantics::parse_file` 的树（L96-98）、`db.parser_expected_syntax(file_id, offset)`（L109，第 6 篇的 cursor-scoped parse）、directive/token/system 词（L110-112）——汇入 `detect_completion_context_impl`（L153-241）：CaretSnapshot 定位（L162-163），literal base 特判（L166-181），directive 特判（L183-196），非 Code 词法环境空手而归（L198-207），backtick 触发强制 DirectiveName（L223-234），最后 L236-240 三源合流：`parser::expectations` + `expected::detect_local` + decl_name 判定，交 `resolve::expectations` 融合。子目录里 `caret.rs` 快照光标邻域、`lex.rs` 判词法、`parser.rs`/`resolve.rs` 消解期望。

**request.rs**（455 行）：`CompletionRequest`（L43-46）是 `SmallVec<[ProviderPlan; 2]>`，每项 `ProviderPlan{provider, trigger}`（L48-52）；`CompletionProvider` 枚举（L62-78）列 15 类供给者。`from_context`（L93-128）：DirectiveName/IntegerLiteralBase 短路成单 provider（L94-108）；apostrophe 触发若无 literal-base 期望则拒绝（L110-113）；非 Code 拒绝（L115-117）；否则逐期望查 `request_for_expected_syntax`（L152-221）映射表合成 provider 集，再 `activated_by`（L130-133）按触发策略裁剪。**触发策略**（L54-59 三档 + L250-281 实现）是交互质量的关键：换行触发只放行 `ManualPrefixOrNewline`（端口列表类）；逗号/开括号在空边界一律压住（L274-277 注释：结构分隔符是用来组句法的，不是来要建议的，弹窗不能偷走下一个回车）。复合期望返回多 provider：BlockItem/Statement 语句位 = Keywords + SystemTasks + Expression（L159-166）。

**engine/plan.rs**（75 行）：`complete_request`（L14-24）`flat_map` 全部 provider 后交 `candidate::finalize_candidates(candidates, &ctx.prefix)` 统一去重排序。`complete_provider`（L26-75）是最终分派表：15 个 match 臂各调 `engine/` 下模块（preproc/keywords/system/expr/named/member/paren_list/port_list/sensitivity_list/literal）。`engine/expr.rs` 的 `complete_expression_impl`（L41 起）示范语义供给：沿 `ScopeParent::start_from` 收集容器名，再按 `expected_type_at_offset` 的期望类型过滤。

## 外部连接

上游：`RootDb`（parser_expected_syntax / file_text / hir 查询）、`hir_semantics::Semantics`（parse_file 与容器定位）、`hir_ty::Type`（typed_filter）、`syntax::diagnostics::{ParserExpectedSyntax, SyntaxKeywordContext}`。keywords.rs 的关键字表来自 slang 的 SyntaxFacts/KeywordContext；snippets.rs 读 `snippets.toml`（engine/ 目录）；`ide::manifest` 提供 vide.toml 补全。下游是 `src/` 的 completion handler。测试基建两套：context/fixtures（context.rs L473-480 的 insta glob 快照）与 engine/snapshots（端到端快照，近期 commit dd3d8432 更新过系统标识符补全快照）。

## 数据流

一次 `textDocument/completion`（用户敲了 `.`）的旅程：LSP handler 构造 FilePosition → `completions(db, position, Some(TriggerChar::Dot))` → `completion_context`：parse 树 + slang 期望查询并行展开 → `detect_completion_context_impl` 判定 lex=Code、期望集含 `MemberName` → `CompletionRequest::from_context` 命中 `CompletionProvider::MemberName`，trigger 策略 NonNewline 放行 → `plan::complete_request` → `member::complete_member_access`（plan.rs L46-47）：Semantics 定位 receiver → `db.infer_expr` 得 Type → `select_member` 列成员 → `finalize_candidates` 统一按 prefix 裁剪去重排序 → `Vec<CompletionItem>` → to_proto 发回客户端。链条里只有 slang cursor-scoped parse 与受影响的 hir 查询真正算数，其余全走 salsa 缓存——这是补全能压进延迟预算的原因。

## 设计决策

**为什么以 slang 期望为主判据？** 自写「向前看」启发式要与语法规则同步演化，slang 的 recovery 天然产出「此处期望什么」（`ParserExpectedSyntax` 带 keyword_context 与期望 token）。db.rs 侧把期望查询限制在光标单点（第 6 篇 L328-363），补全拿到的元数据既新鲜又不污染权威树。代价是必须信任 slang 的 recovery——所以 expected.rs 保留局部判据补充，resolve.rs 负责冲突收敛。

**为什么 provider 规划独立成 request.rs？** 「什么位置给什么」与「怎么给」分离后，交互策略集中在 L250-281 一张表里调优：想让逗号后也弹表达式，改一行 TriggerPolicy 而非翻 16 个 provider。`request_planning_matrix` 测试（L327-453）把 16 种上下文×策略组合钉成快照，回归成本极低。

**为什么 prefix 过滤放最后统一做？** provider 只管产出，`finalize_candidates`（plan.rs L23）统一裁剪去重排序——避免各 provider 实现不一致的匹配（如大小写敏感度），也给将来接入 fuzzy 匹配留单点。

## 新人提示

1. 加新补全天地的四步：ExpectedSyntax 加变体（context.rs L46-69）→ expected/resolve 给出判据 → request_for_expected_syntax 加映射（L152-221）→ engine/ 下写 provider 并挂进 complete_provider（plan.rs L32-74）。跑两套快照。
2. 快照测试协议：fixture 里 `/*caret*/` 标光标、`//- trigger: dot` 头声明触发（context.rs L367-440 解析），insta 自动对齐；`cargo insta accept` 前先人肉审快照。
3. 触发字符增删要同步两处：vscode 扩展的 triggerCharacters 与 context.rs L33-44——多一个没处理的触发字符会让 request 拒绝服务。
4. 「补全不弹」排查顺序：lex 是否 Code → expectations 是否为空（slang recovery 没接住）→ TriggerPolicy 是否压住 → prefix 是否匹配。前三步在 context/request，最后才怀疑 provider。
5. expr.rs 的 ScopeParent 遍历 + BTreeMap 去重是名字收集的标准姿势，新 provider 抄它而非直接扫 body arena。
