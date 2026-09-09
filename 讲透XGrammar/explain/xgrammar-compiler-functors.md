# xgrammar-compiler-functors — 编译枢纽与 22 个 pass（grammar_compiler.cc / grammar_functor.cc）

## 角色定位

这对文件是**编译期的心脏**：`grammar_functor.cc`（3832 行，全仓第二大）实现全部语法树变换算子，`grammar_compiler.cc`（1589 行）编排、并行化、缓存。位于 **cpp-compiler 层**，输入前端产出的 Grammar，输出 `CompiledGrammar`——内含优化后语法、每规则 FSM、`adaptive_token_mask_cache`（每个可扫描 FSM 状态 → 预计算 token 掩码）。全库"编译期/运行期分离"在此落地。

## 内部结构

**functor 体系**（grammar_functor.h/.cc）：模板基类 `GrammarFunctor<T, ReturnType>` 派生两族——`GrammarVisitor<ReturnType>`（只读收集）与 `GrammarMutator`（重建语法，T=int32_t 即新表达式下标）。mutator 先给每条旧规则占位 AddEmptyRule 保持 id 对齐，再逐规则重写体。`.cc` 实数 **22 个变换/分析类**：构造类（SubGrammarAdder / GrammarUnion / GrammarConcat）；规整类（GrammarNormalizer / SingleElementExprEliminator / StructureNormalizer——保证每规则体是 choices-of-sequences 或 TagDispatch）；优化类（ByteStringFuser 相邻字节串融合、RuleInliner 内联前导规则引用、DeadCodeEliminator、LookaheadAssertionAnalyzer 合成前瞻断言消解 uncertain、AllowEmptyRuleAnalyzer、RepetitionRangeExpander / RepetitionNormalizer 处理 {m,n}、LazyBodyFlattener、RootRuleRenamer）；产物侧（GrammarFSMBuilderImpl 每规则编译成 FSM、GrammarFSMHasher 结构哈希作缓存键、GrammarOptimizerImpl 总编排、RuleLevelCache）；另有 InPlaceGrammarRewriter 中间基类。总编排固定顺序：ByteFuser→RuleInliner→DeadCode→Lookahead→AllowEmpty→RepetitionNormalizer→FSMBuilder。

**编译器侧**三层嵌套：`GrammarMatcherForTokenMaskCache`（继承 EarleyParser！）是"为算 mask 而生的匹配器"；`GrammarCompilerSub` 是无缓存编译器，核心 `MultiThreadCompileGrammar`：优化语法 → TagDispatchOptimization（预计算"第二字符起确定接受" bitset）→ FSM 哈希 → 枚举每规则 FSM 的 scanable 状态逐个建任务算 mask（多线程投线程池+mutex，单线程路径为 WASM 兼容）；外层 `GrammarCompiler::Impl` 是缓存壳，五种 key + ThreadSafeLRUCache。

## 外部连接

上游消费 `grammar_impl.h` 语法树与 `tokenizer_info_impl.h` 词表；下游被 `grammar_matcher.cc` 推理期消费。直接依赖 `fsm.h`/`earley_parser.h`/`thread_pool.h`/`thread_safe_cache.h`。Python 侧 GrammarCompiler 经 tvm-ffi 直连。

## 数据流

`CompileJSONSchema(schema)` 全流程：① schema → `Grammar::FromJSONSchema` → 规整语法；② `GrammarOptimizer::Apply` 七步 pass 链，逐规则填上 DFA；③ 使能缓存时算 FSM 哈希；④ 对每规则 FSM 每个 scanable 状态建任务：查 RuleLevelCache（哈希+状态 id 命中即复用）→ 未命中则用 first-char mask + sorted vocab 区间二分切成 accepted/rejected/uncertain → lookahead 断言消解 uncertain → 按规模选三模式存储写 mask cache；⑤ join 返回 CompiledGrammar。

## 设计决策

- **22 pass 而非一个大函数**：每个变换单一职责、可独立测试；visitor/mutator 二分让只读与改写类型安全分离。
- **规则 id 对齐**（先占位空规则再填体）：pass 前后 rule_id 稳定，缓存键不失效。
- **mask 预计算并行化**：每状态任务独立，天然并行；WASM 无 thread/mutex，单线程免锁直通。
- **内存预算 1/3-2/3 切分**：2/3 给语法级 LRU（命中省整次编译）、1/3 给规则级（跨语法共享子规则，哈希命中直接复用）。
- **预计算复用 EarleyParser**：编译期与运行期同一套状态机代码，杜绝语义漂移。

## 新人提示

读 pass 链从 `GrammarOptimizerImpl::Apply`（约 2802 行）入手记固定顺序——顺序错了会产出错误 FSM。改 functor 继承 GrammarMutator 要在 Apply 首行调 InitGrammar；原地重写优先继承 InPlaceGrammarRewriter。调试利器 `print_converted_ebnf=True`。缓存行为看 test_grammar_compiler.py。GrammarKey 用 `grammar.ToString()`——打印稳定性决定缓存命中率。
