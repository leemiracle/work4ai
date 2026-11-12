# XGrammar 新人上手指南（ONBOARDING）

> 基于知识图谱（1305 节点/1788 边/12 层/15 步导览，commit c30554f7）+ 源码精读生成，2026-09-05。

## 1. 项目总览

LLM 采样无法保证输出结构合法，而结构化输出（JSON Schema / tool calling / 正则约束）需要**硬约束**。"生成后校验+重试"浪费算力，正确做法是**采样前屏蔽不合法 token 的 logit**——约束解码。

XGrammar（MLC 团队，NeurIPS 2024）是工业级答案：输入 EBNF / JSON Schema / 正则 / Lark / Structural Tag 之一，输出每步一个 `(batch, vocab_size)` 的 token bitmask。

核心矛盾：语法是 CFG 级别，判断合法性理论上很贵；推理却要每 token 微秒级。解法是全库最重要的架构决策——**编译期/运行期两阶段分离**：解析、规则展开、递归消除、NFA→DFA、mask 预计算全放 `GrammarCompiler`（一次编译多次复用）；推理期 `GrammarMatcher` 只做逐 token 轻量推进+查表。三条主线：Python 四件套（接口）→ C++ 编译管线（重活）→ kernels（最后一公里），另有 Web WASM 端口。

## 2. 架构分层（12 层）

```
用户代码 → python-api(四件套+tvm-ffi轻壳)
  ↓ FFI 反射
cpp-public-api  include/xgrammar 8 头（PIMPL 对象协议）
  ↓
cpp-frontend  多格式→CSR 语法树
  (grammar_parser/json_schema/lark/regex/structural_tag → grammar_builder)
  ↓
cpp-compiler  22 functor pass + FSM(NFA→DFA→Minimize)
  + adaptive token mask 预计算(线程池+双级 LRU)
  ↓
cpp-runtime  earley_parser(Complete/Predict/Scan)
  + grammar_matcher(推进/回滚/草稿树) + tokenizer_info(词表)
  ↓
kernels  CPU/torch/torch.compile/CUDA/Triton/MLX 就地套掩码
─ cpp-support(bitset/线程池/LRU/并查集/反射JSON)=全层地基
─ web-wasm(Emscripten→TS)；测试47；文档53；CI 33
```

12 层：cpp-public-api（8 头 PIMPL）/ cpp-frontend（19 五格式转 CSR）/ cpp-compiler（9 优化+FSM+mask 预计算）/ cpp-runtime（7 Earley+Matcher+词表）/ cpp-support（21 基础件）/ python-api（21）/ kernels（8）/ web-wasm（19）/ test-python（35）/ test-cpp（12）/ documentation（53）/ build-ci（33）。

## 3. 核心模块

**Python 四件套**：`Grammar`（grammar.py）——五工厂+union/concat；`TokenizerInfo`——HF 词表构造，探测解码器类型（RAW/BYTE_FALLBACK/BYTE_LEVEL），维护排序词表与 trie 范围；`GrammarCompiler`——五路 compile_* 返回 CompiledGrammar；`GrammarMatcher`——fill_next_token_bitmask 产掩码、accept_token 推进、rollback、traverse_draft_tree 投机解码，配 BatchGrammarMatcher 批量。

**C++ 三段管线**：前端段——grammar_parser.cc（EBNF 递归下降）、json_schema_converter.cc（全仓最大）、json_schema_converter_ext.cc（XML tool calling）、lark_converter.cc、regex_converter.cc、structural_tag.cc，产物统一交 grammar_builder.cc。编译优化段——grammar_compiler.cc 编排 22 个 pass（grammar_functor.cc）+ FSM（fsm.cc / fsm_builder.cc 正则→FSM / suffix_automata.cc 子串约束）。运行时段——earley_parser.cc、grammar_matcher.cc、tokenizer_info.cc。行号分布见第 7 节热点表。

**kernels**：apply_token_bitmask_inplace 五后端——CPU/torch/torch.compile/CUDA（NVRTC JIT）/Triton/MLX。

**Web WASM**：Emscripten 编 C++ 核心 → JS 绑定 → TS 门面；WASM 下禁 ThreadPool/mutex。

## 4. 关键概念（11 把钥匙）

1. **CSR 语法表示**：语法树平铺进 int32 数组+起始下标表，无指针链，序列化/去重友好；表达式共 14 种 GrammarExprType（kByteString/kCharacterClass(Star)/kRuleRef/kSequence/kChoices/kTagDispatch/kRepeat/kToken/kRegex/kSubstring 等）。
2. **per-rule FSM**：每规则一个 DFA，字符匹配 O(1)；TagDispatch/递归结构回退 Earley 展开。
3. **Earley 选型**：LL/LR 只覆盖 CFG 真子集；Earley 容纳左递归/二义并支持部分匹配。
4. **三模式 mask**：kAccepted/kRejected/kAcceptedBitset（阈值 1000）。token 分 accepted/rejected/uncertain 三类，uncertain（依赖父上下文）存下标列表，lookahead assertion 编译期消解。
5. **22 个 functor pass**：visitor（只读）/mutator（重建）两族，新变换只需派生一个 functor。
6. **structural tag 触发式切换**：begin 跳进 schema 子规则、end 跳出（kTagDispatch/kTokenTagDispatch）；trie 多模式匹配+二次切片 bitset。
7. **token bitmask**：(batch, vocab) int32 掩码，kernels 就地 logits[mask==0]=-inf。
8. **speculative rollback**：rollback/fork/traverse_draft_tree（DFS 草稿树+超时剪枝）。
9. **双级缓存**：语法级 LRU（内存 2/3）+ 规则级（1/3，键=FSM 哈希+状态 id）。
10. **PIMPL**：公共类只持 shared_ptr<Impl>，object.h 定对象协议，ABI 稳定。
11. **tvm-ffi 反射绑定**：XGRObject 轻壳持 handle，refl::ObjectDef 声明式注册，零手写胶水。

## 5. 推荐学习路径（15 步导览）

| 步 | 看什么 | 自检 |
|---|---|---|
| 1 | README + quick_start | 最贵的对象 |
| 2 | workflow_of_xgrammar + constrained_decoding | 预计算为何在编译期 |
| 3 | grammar/tokenizer_info/compiler.py | 为何排序词表 |
| 4 | matcher.py + base.py + tvm_ffi.cc | Python/C++ 关系 |
| 5 | include/xgrammar 8 个头 | 为何看不到成员 |
| 6 | grammar_parser + grammar_impl.h + grammar_builder | indptr/data 对应子树 |
| 7 | 四种 converter + structural_tag.cc | anyOf 映射哪种 expr |
| 8 | grammar_compiler.cc + grammar_functor.h/cc | RuleInliner 何时内联 |
| 9 | fsm.h/cc + fsm_builder.cc + suffix_automata.cc | 为何每规则一 FSM |
| 10 | earley_parser + grammar_matcher + compiled_grammar_impl.h | uncertain 何时消解 |
| 11 | kernels/ 全部 | CUDA 为何 NVRTC JIT |
| 12 | cpp/support/ | Compact2DArray 布局 |
| 13 | contrib/ + builtin_structural_tag.py | LogitsProcessor 写法 |
| 14 | web/ | WASM 禁了什么 |
| 15 | tests/ + CMakeLists + workflows | 压力测试覆盖啥 |

节奏：1-5 建地图；6-10 主干（配 explain/）；11-15 选读。

## 6. 文件地图（按层速查）

- **Python API**：grammar.py·tokenizer_info.py·compiler.py·matcher.py·base.py·load_binding.py·structural_tag.py·builtin_structural_tag.py（2462 行）·openai_tool_call_schema.py·contrib/hf.py·contrib/mlxlm.py
- **C++ 公共头**：xgrammar.h·grammar.h·compiler.h·matcher.h·tokenizer_info.h·object.h 等 8 头
- **C++ 前端**：grammar_parser.{h,cc}·grammar_builder.{h,cc}·grammar_impl.h·grammar_printer.{h,cc}·json_schema_converter{,_ext}.{h,cc}·lark_converter.{h,cc}·regex_converter.{h,cc}·structural_tag.{h,cc}
- **C++ 编译器**：grammar_compiler.cc·grammar_functor.{h,cc}·fsm.{h,cc}·fsm_builder.{h,cc}·suffix_automata.{h,cc}·compiled_grammar.cc+compiled_grammar_impl.h（AdaptiveTokenMask 定义处）
- **C++ 运行时**：earley_parser.{h,cc}·grammar_matcher.cc·tokenizer_info.cc+tokenizer_info_impl.h
- **C++ 支撑**：support/ 13 头（logging·encoding·dynamic_bitset·thread_pool·thread_safe_cache·union_find_set·reflection 等）；config.cc；tvm_ffi/{tvm_ffi.cc,python_methods.cc}
- **kernels**：apply_token_bitmask_inplace_{cpu,torch,torch_compile,cuda,triton}.py + _cuda.cu + _mlx.py
- **web**：src/{xgrammar.ts,structural_tag.ts,xgrammar_binding.cc,index.ts}·build.sh·example/
- **测试**：tests/python 33 模块（matcher 各格式×语义、json_schema 3537 行、speculative/pressure/recursion 等）；tests/cpp GoogleTest
- **构建**：CMakeLists（根+cpp）·cmake/config.cmake·pyproject.toml·8 条 workflows·scripts/

## 7. 复杂度热点

| 文件 | 行数 | 难点 |
|---|---|---|
| json_schema_converter.cc | 4312 | Schema 规范庞杂 |
| grammar_functor.cc | 3832 | 22 pass 顺序依赖；两套重写写法 |
| grammar_matcher.cc | 2774 | 预算/捕获/草稿树/jump-forward |
| lark_converter.cc | 2694 | 对齐 Lark 生态语义 |
| structural_tag.cc | 2509 | 21 种 Format 解析+TagDispatch 编译 |
| fsm.cc | 1996 | 化简/合并/ToDFA/Minimize 四算法咬合 |
| fsm_builder.cc | 1797 | 正则 IR+UTF-8 packed 边+trie FSM |
| grammar_compiler.cc | 1589 | 编排+双缓存+并发 |
| 测试侧 | — | json_schema 3537；structural_tag 3000+ |

心法：改 fsm/earley 先跑 test_fsm.cc；改 functor 链注意 pass 顺序；改 matcher 别在运行期引入昂贵操作。

## 8. 与生态的关系

**同类对比**：outlines——纯 Python 逐 token 索引编译，编译慢、运行期开销大；XGrammar 用 C++ 编译+预计算+三模式存储，快一个量级。guidance——程序+语法混合模板，表达力强但逐 token 解释执行。llguidance——guidance 的 Rust 后端，在 vLLM/SGLang 里是竞争后端。xgrammar 走"标准格式输入+极致编译优化"的编译器流派。

**引擎集成**：vLLM / SGLang 的 structured output 后端；MLC-LLM 的娘家，WebLLM 经 WASM 用同一核心；transformers 经 contrib/hf.py 三行接入。

---

*配套 explain/ 六篇：grammar / compiler-functors / fsm / earley-matcher / tokenizer-mask / python-api。*
