# xgrammar-python-api — XGRObject 与 FFI 四件套（base.py / grammar.py / compiler.py / matcher.py）

## 角色定位

`python/xgrammar/` 是全库门面层（python-api 层），多数用户只跟它打交道。设计哲学写在 base.py 的 docstring 里——**Python 对象只是 C++ 对象的轻壳（lightweight handle）**，重活全部下沉 C++。四个核心类 Grammar / TokenizerInfo / GrammarCompiler / GrammarMatcher 经 tvm-ffi 反射绑定直连 C++，加模块级 bitmask 工具与 kernels 子包构成全部用户表面。代码量小（四主文件约 2100 行），fan-in 最高。

## 内部结构

**base.py（95 行）**：XGRObject 基类持私有 `__handle`，提供 `_create_from_handle`（绕过 `__init__`）、`_init_handle`、`_handle` 属性、按 handle 比较的 `__eq__`。导入时把 tvm_ffi_binding 的 `_ffi_api` 挂成 `_core` 并聚合 testing/kernels/config 子命名空间。

**grammar.py（500 行）**：Grammar(XGRObject) 五工厂 from_ebnf / from_json_schema / from_regex / from_lark / from_structural_tag + builtin_json_grammar + concat/union + serialize/deserialize。

**compiler.py（358 行）**：GrammarCompiler(XGRObject) 构造 `(tokenizer_info, *, max_threads=8, cache_enabled=True, max_memory_bytes=-1)`；五路 compile_* 返回 CompiledGrammar。

**matcher.py（717 行）**：模块级四函数——get_bitmask_shape / allocate_token_bitmask（torch int32 全 1 张量）/ reset_token_bitmask / apply_token_bitmask_inplace（分派 kernels）。GrammarMatcher 构造 `(compiled_grammar, *, max_rollback_tokens=-1, terminate_without_trailing_space=False, debug_print=False)`；核心 fill_next_token_bitmask(bitmask, index=0)、accept_token/string、rollback / fork、traverse_draft_tree、get_captures、is_terminated。BatchGrammarMatcher：batch_fill/accept/rollback。

配套：load_binding.py 定位原生库；contrib/hf.py 的 transformers LogitsProcessor；contrib/mlxlm.py 覆盖 MLX。

## 外部连接

向下：`cpp/tvm_ffi/tvm_ffi.cc` 用 `refl::ObjectDef<GrammarObj>().def(refl::init<…>())` 声明式注册全部类与方法（约 780 行注册表）；`_handle` 里就是 PIMPL 的 shared_ptr<Impl>。向上：被 vLLM / SGLang / MLC-LLM / transformers 适配层调用；kernels 子包被 apply_token_bitmask_inplace 分派。

## 数据流

一次完整调用：`Grammar.from_json_schema(schema)` → `TokenizerInfo.from_huggingface(tok)` → `GrammarCompiler(...)` → `compile_json_schema(schema)` 得 CompiledGrammar（缓存命中直接复用）→ `GrammarMatcher(...)` → 循环里 `fill_next_token_bitmask(mask, 0)` 写允许集 → 引擎 `apply_token_bitmask_inplace(logits, mask)` → 采样 → `accept_token(tid)`。跨 FFI 只有 handle 与方法调用；掩码经 DLTensor 直写 torch 内存。

## 设计决策

- **轻壳而非包装**：Python 层不缓存/派生任何状态，C++ 侧双级 LRU 与并发控制是唯一事实源；`__eq__` 比 handle 而非内容；FFI handle 用 `_create_from_handle` 无构造副作用地包装。
- **tvm-ffi 反射绑定而非手写 pybind11/nanobind**：注册表式声明，接口维护接近纯声明；同一思路服务 Python 与 WASM。
- **bitmask 用 int32 张量而非 bool**：GPU 友好布局，kernels 按 `token_id >> 5` 寻址。
- **Batch 匹配器独立成类**：批式并行 fill/accept/rollback 值得独立 API。

## 新人提示

读序：base.py（95 行全读）→ matcher.py 类 docstring → tvm_ffi.cc 任一 ObjectDef 注册块。调试 FFI 第一工具是 `_handle`——"对象不相等/缓存不命中"先查 handle。C++ 经 DLTensor 直写 torch 张量，无需同步。fill_next_token_bitmask 的 index 是批内行号，单请求传 0。加新 API：先 tvm_ffi.cc 注册再加 .py 薄方法。测试参考 test_grammar_matcher_basic.py。
