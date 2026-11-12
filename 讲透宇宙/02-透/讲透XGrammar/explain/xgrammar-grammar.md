# xgrammar-grammar — 语法对象与 CSR 表示（grammar.cc / grammar.h / grammar_impl.h）

## 角色定位

`Grammar` 是全库的"通用货币"：五种输入格式（EBNF / JSON Schema / 正则 / Lark / Structural Tag）最终都汇成一个 Grammar 对象，后续编译、匹配、序列化全都消费它。对应 **cpp-frontend 层出口**——`include/xgrammar/grammar.h`（221 行）是对外 PIMPL 契约，数据模型在 `cpp/grammar_impl.h`（480 行），工厂胶水在 `cpp/grammar.cc`（197 行）。它只描述纯语法、不绑词表——词表到 `GrammarCompiler(TokenizerInfo)` 阶段才注入，同一份 Grammar 可搭配不同模型复用。

## 内部结构

数据模型是"规则 × 表达式"两级。**Rule**：`name` + `body_expr_id` + 运行期元数据（`lookahead_assertion_id` 前瞻断言、`max_tokens`/`max_chars` 预算、`capture_name` 捕获组、`is_lazy` 最短匹配、`temperature` 采样温度），另有稀疏 `SuffixStopInfo` 侧表。**GrammarExpr**：14 种类型（`GrammarExprType` 枚举）——叶子类 kByteString / kCharacterClass(Star) / kEmptyStr / kRuleRef / kToken / kExcludeToken / kRegex / kSubstring，组合类 kSequence / kChoices / kRepeat，分发类 kTagDispatch / kTokenTagDispatch，每个是 `(type, data[])` 二元组，data 布局在枚举注释逐一定义。

**CSR 存储**是最重要的设计：所有表达式平铺进 `std::vector<int32_t> grammar_expr_data_`，`grammar_expr_indptr_` 记录每个表达式的起始下标。`GetGrammarExpr(i)` 读 indptr 定位 `[type, len]` 头、切出 data 切片，零拷贝返回视图。`Impl` 的 public 区还挂编译期回填的辅助数据：`per_rule_fsms`（每规则 FSM）、`per_rule_fsm_hashes`（跨语法缓存键）、`allow_empty_rule_ids`、`optimized`。

五个静态工厂：`FromEBNF`（ParseEBNF 后过 GrammarNormalizer）、`FromJSONSchema`（9 个参数对齐 `json.dumps` 语义）、`FromRegex`（先 RegexToEBNF 再走 FromEBNF）、`FromLark`（支持命名子语法 `@name`）、`FromStructuralTag`（返回 `variant<Grammar, StructuralTagError>`）；组合子 `Union`/`Concat` 委托同名 functor；`BuiltinJSONGrammar` 内嵌手写优化 EBNF（含 lookahead 断言）静态单例。

## 外部连接

`grammar.h` 是全仓被 include 最多的公共头；`grammar.cc` 上游是五个前端转换器，下游把成品交给 functor pass 链与 `grammar_compiler.cc`。`SerializeJSON`/`DeserializeJSON` 走 `XGRAMMAR_MEMBER_TABLE` 反射宏——成员表注册成元数据后由通用 JSON 序列化器自动 dump/load，CSR 数组整块落盘。

## 数据流

以 `FromJSONSchema(schema)` 为例：① `JSONSchemaToGrammar` 生成未规整语法树；② `GrammarNormalizer` 展开嵌套、合并相邻字符串、规范化结构；③ 得到 `rules_ + data + indptr` 三件套。运行期消费者按 `GetRootRuleId() → GetRule(id).body_expr_id → GetGrammarExpr(id)` 链条遍历，遇 kRuleRef 跳到对应规则——一次"树遍历"实际是两次数组下标运算。

## 设计决策

- **CSR 而非对象树**：序列化零成本（反射宏直接 dump 两数组）；FSM 化时顺序扫描只碰两块连续内存；builder 去重容易（同构子树共享下标）；跨 FFI 传共享指针时 CSR 天然只读。
- **五工厂统一入口**：所有格式创建时即 normalize 到同一形状，后续 pass 无需关心来源——多格式复杂度被挡在前端转换器里。
- **kCharacterClassStar 单列**：`[a-z]*` 若展开成递归规则拖慢匹配，单列类型让 FSM 用 O(1) 自环处理。
- **kRegex/kSubstring 作不透明叶子穿透 pass 链**：原样携带到 GrammarFSMBuilder 才编译成自动机，避免中间表示过载。
- **内置 JSON 手写而非生成**：带 lookahead 断言的手工优化能显著消解 uncertain token，机器生成达不到。

## 新人提示

先读 `grammar_impl.h` 顶部 70 行注释（官方数据格式文档）；用 `ToString()` 随时把 CSR 树打回 EBNF 人读形式调试。`GetGrammarExpr` 返回视图，`SetData` 可原地改下标但别破坏 indptr 不变式。`FromStructuralTag` 返回 variant——不检查错误分支直接用是常见新手 bug。配套测试 `test_grammar_parser.py`、`test_serialization.py`。
