# 04 · Dynamo eval_frame.py — TorchDynamo 编译前端入口

> 源码: `torch/_dynamo/eval_frame.py` (2979 行) | 图层: `layer:dynamo-frontend` | 复杂度: complex
> 一句话:它是 torch.compile 的"总开关室"——把一个 Python 回调挂到 CPython 的帧求值钩子上,
> 并管理此后的一切运行时状态:缓存、守卫、stance、disable、嵌套与恢复。

---

## 1. 架构位置:为什么需要这个文件

PT2 编译器栈分层:`torch.compile`(用户 API)→ **Dynamo(字节码捕获前端)** → AOTAutograd → Inductor 后端。
`eval_frame.py` 是 Dynamo 前端层的运行时入口(knowledge graph: `layer:dynamo-frontend`,tour order 8),
它的核心哲学写在文件头 L4-17:

- 本文件的所有函数**在运行时、每个 Python 帧上都会执行**,是 hot path,性能敏感;
- 编译期才跑的逻辑放到 `convert_frame.py`。这条分界线是理解两文件分工的钥匙。

它不做字节码符号执行(那是 `symbolic_convert.py` 的 `InstructionTranslator`),也不构图(`output_graph.py`),
它只负责**三件事**:
1. 安装/卸载 eval-frame 回调(进入/退出编译区域的门禁);
2. 提供用户 API:`optimize`(L1786)、`explain`(L1932)、`export`(L2318)、`optimize_assert`(L2799);
3. 管理编译缓存与运行时开关(`_debug_get_cache_entry_list` L424、`remove_from_cache` L693、`skip_code` L2976)。

## 2. PEP 523 机制:回调如何挂上去

CPython 的 PEP 523 允许替换解释器的帧求值函数。Dynamo 的 C 层
(`torch/csrc/dynamo/eval_frame.c`)在初始化时调用
`_PyInterpreterState_SetEvalFrameFunc(...)`(eval_frame.c L250)换成自己的 `dynamo__custom_eval_frame`
(`eval_frame_cpp.cpp` L342)。从此**每个 Python 函数调用**都会先进这段 C 代码。

C 层用一个 thread-local 变量 `eval_frame_callback_key`(eval_frame.c L28)决定行为,三态:
- `None` — 回调未激活,Dynamo 隐身(普通 eager 执行);
- `Py_False` — run-only 模式:只查缓存、重放已编译代码,绝不触发新编译;
- callable — 完整 Dynamo:缓存 miss 时调用 Python 回调去编译。

Python 侧的开关就是 `set_eval_frame(callback)`:eval_frame.c L623-646 的实现是
"swap-and-return":先 `eval_frame_callback_get()` 取旧值返给调用者保存,再 `eval_frame_callback_set(新值)`。
所以你在本文件到处看到 `prior = set_eval_frame(None)` ... `_maybe_set_eval_frame(prior)` 的配对模式——
这是整个 Dynamo 的进出栈协议。`_maybe_set_eval_frame`(L176-185)额外套了 Justknob 杀伤开关
(`pytorch/compiler:enable_compiler_set_eval_frame`),Meta 线上可一键全局关闭 Dynamo。

**典型时序**(cache miss 首编译):
```
用户调 compiled_fn(args)
 → compile_wrapper (eval_frame.py L1147)
   → set_eval_frame(None)                    # 先摘掉回调,避免 Dynamo 追 Dynamo 自己
   → _maybe_set_eval_frame(CatchErrorsWrapper 实例)
   → fn(*args)                               # 真正执行用户函数
     → CPython 帧求值 → dynamo__custom_eval_frame (eval_frame_cpp.cpp L342)
       → get_extra_state(F_CODE(frame)) (L494)      # code object 的缓存挂在 _PyCode_SetExtra
       → 遍历 CacheEntry 跑 C++ 守卫树 → 全 miss
       → 调 Python 回调 CatchErrorsWrapper.__call__ (convert_frame.py L2579)
         → ConvertFrame.__call__ → ConvertFrameAssert → _compile() (L1688) → trace_frame() (L892)
           → InstructionTranslator 符号执行 → OutputGraph 捕获 FX 图
           → compile_subgraph (output_graph.py L2010) 调 backend → 生成新字节码
       → C 层 create_cache_entry (eval_frame_cpp.cpp L678) 把 GuardedCode+backend 挂回 code object
       → dynamo_eval_custom_code_impl (eval_frame.c L285) 在 shadow frame 里执行编译产物
```

## 3. torch.compile 的公共 API 路径

`torch.compile` 本体在 `torch/__init__.py` L3023(L3289 处的收尾):

```python
return torch._dynamo.optimize(backend=backend, nopython=fullgraph, dynamic=..., ...)(model)
```

注意 backend 已被包成 `_TorchCompileInductorWrapper`(mode/options 解析在 torch/__init__.py 完成),
`nopython=fullgraph` 是术语转换点。随后进入本文件的调用链:

`torch._dynamo.optimize` → `eval_frame.optimize`(L1786)→ `_optimize`(L1802):
- L1857-1858 `check_if_dynamo_supported()`(L1744:Python < 3.15、free-threading ≥ 3.13.3)+ 互斥 config 检查;
- L1864 构造 `Hooks(guard_export_fn, guard_fail_fn, guard_filter_fn)`(hooks.py 的数据类,贯穿回调装配);
- L1870-1875 三路逃逸:`disable=True` / 环境变量 `TORCHDYNAMO_DISABLE=1` / Justknob → 返回 `_NullDecorator`(L1648);
- L1877 `nopython=True` → 分流到 `optimize_assert`(L2799 → `_optimize_assert` L2812,fullgraph 语义,graph break 直接抛错);
- L1889 `get_compiler_fn(backend)`(L1625):字符串走 `backends.registry.lookup_backend`,再裹一层
  `wrap_backend_debug`(repro 调试钩子),并触发 backend 的 `_dynamo_backend_init` 预热(L1615);
- L1905-1927 终点:`_optimize_catch_errors(convert_frame.convert_frame(backend, hooks), hooks, ...)`。

`_optimize_catch_errors`(L1582)是装配流水线的最后一步:把 `ConvertFrame` 对象再包一层
`catch_errors_wrapper`(L1599),得到最终回调,连同所有选项塞进 `OptimizeContext`。

## 4. 回调洋葱:四层包装

最终装到 C 层的回调是一个洋葱,从外到内:

| 层 | 位置 | 职责 |
|---|---|---|
| CatchErrorsWrapper | convert_frame.py L2560 | 异常分类(Unsupported→graph break;UserError→抛给用户)、skipfile 检查、skip 原因记录、DDP optimizer 劫持(L2664)、`compile_lock` 串行化(L2690) |
| ConvertFrame | convert_frame.py L2338 | 对外门面,持有 `ConvertFrameAssert(one_graph=False)`;L19-20 注释说明 `_torchdynamo_orig_backend` 链用于找回裸 backend |
| ConvertFrameAssert | convert_frame.py L605 | 重编译计数/recompile_limit 检查、cache_size 检查、调 `_compile`(L1688)驱动真正的符号执行 |
| 用户 backend | 如 inductor | 接收 FX GraphModule + example_inputs,返回优化后的可调用对象 |

`_create_wrapped_callback`(L353)是这个洋葱的最小复刻,供 stance 切换 backend 时即时重建回调(L283)。
`innermost_backend`(L756)沿 `_torchdynamo_orig_backend` 链穿透所有包装找到裸 backend——
C 层还会在它上面挂 backend 身份守卫(L1894-1896 注释),防止换 backend 后误用旧缓存。

## 5. _TorchDynamoContext:三种进入方式,一个基类

`_TorchDynamoContext`(L864)是所有上下文的基类,派生树(graph `inherits` 边):
`OptimizeContext`(L1393)、`RunOnlyContext`(L1472)、`DisableContext`(L1484)。

三种使用方式殊途同归:

**(a) 装饰器路径**(最常见):`_TorchDynamoContext.__call__`(L978)返回 `compile_wrapper`(L1147)。
每次调用时它完成精确的"保存-安装-执行-恢复" ballet:
- L1154 `prior = set_eval_frame(None)`(摘回调→用户顶层代码里新出现的帧不会被追踪,除非重新装上);
- L1246 `_maybe_set_eval_frame(_callback_from_stance(callback))`(真正开启);
- L1261 `result = fn(*args, **kwargs)` 执行用户代码(编译就发生在这期间的 C 层 miss 里);
- 嵌套保护三连:L1164 `_is_eager_on_nested_compile()`(编译器内部 tracing 中嵌套 compile 直通 eager)、
  L1195 `torch.compiler.is_exporting()`(export 区域内嵌套 compile 跳过)、
  L1205 FX symbolic tracing 中嵌套则 inline(L1216 jit tracing 直接报错);
- L1257 `torch._C._dynamo_save_local_dispatch_key_set()`:dispatch key 快照进 C++ 线程栈,
  L1318 恢复——刻意做成 C 侧保存避免每次编译调用都构造 pybind 对象(注释 L1248-1256 记录了这层优化);
- L1282-1297 fullgraph 计数检查:如果 fullgraph=True 却一个帧都没编译,抛
  "found no compiled frames" 并附上收集到的 skip 原因(`dynamo_tls.skip_reasons`,L807-816);
- L1327-1338 给 wrapper 打元数据:`_torchdynamo_inline`、`_torchdynamo_orig_callable`、
  `_torchdynamo_wrapper_id`(供 `innermost_fn` L727 解嵌套,`_wrapper_id` 校验防止 functools.wraps 拷贝误穿)。

**(b) 上下文管理器路径**:`__enter__`(L947)/`__exit__`(L961),注意 L948
`config.raise_on_ctx_manager_usage`——社区版默认允许,但官方教程推荐装饰器用法。

**(c) nn.Module 路径**:`torch.compile(model)` 在 L1047-1074 被接住,返回 `OptimizedModule`。
L1048 显式拒绝 `RecursiveScriptModule`(提示编译 eager 原始模块)。

## 6. OptimizedModule:编译的模块外壳(L469-690)

`OptimizedModule(torch.nn.Module)` 把原始模块存为 `_orig_mod` 子模块(L514-520),关键设计:
- **属性透传**:`__getattr__`(L649)/`__setattr__`(L654)/`__delattr__`(L663)把一切非自有属性
  (白名单 `_opt_mod_attributes` L478)代理到 `_orig_mod`,用户感觉不到包装存在;
- **forward 三策略**(`_initialize` L533):DisableContext 直接包 `__call__`(L537);
  `config.wrap_top_frame` 或 skip-rule 命中(如 `nn.Linear` 这类 trace_rules 可识别的类)时走
  `wrap_inline` 加一层可捕获帧(L542);否则包 `__call__` 让 hook 在 Dynamo 外跑、捕获更内层的 forward(L545);
- **training 属性镜像**(L636-647):property 双向同步到 `_orig_mod.training`;
- **lazy module 支持**:`_call_lazy_check`(L672)先跑 `_infer_parameters` 再进编译 forward;
- **AOT 实验**:`_aot_compile`(L565)/`_save_aot_compiled_module`(L590)/`_load_aot_compiled_module`(L607)
  + `__reduce__`(L621)/`__getstate__`(L626,剔除不可 pickle 的 forward)支持序列化;
- L551-561 `__call__` 警告:全局 module hook 会对 OptimizedModule 多触发一次,建议改用 `module.compile()`。

## 7. 缓存与守卫:eval_frame.py 视角

编译缓存**不在这个文件里**,它挂在每个 code object 的 C 侧 `ExtraState`(`_PyCode_SetExtra`,
extra_state.cpp),内含 LRU 链表 `cache_entry_list` 与 `frame_state`。每个 `CacheEntry`
(cache_entry.cpp)存三样:`RootGuardManager*`(裸 C++ 指针,守卫树根)、编译后的 code object、backend。

eval_frame.py 提供的是**观察与操控窗口**:
- `_debug_get_cache_entry_list`(L424)直通 C API——TORCH_LOGS=recompiles 的诊断基础;
- `_get_cache_entries_for_region`(L436):`isolate_recompiles` 分桶查询(LRU 序,隔离桶只读回落默认桶);
- `remove_from_cache`(L693)/`skip_code`(L2976,给 code 打 `FrameAction.SKIP` 永久跳过)。

**守卫命中路径全在 C++**:`dynamo__custom_eval_frame` 拿 `ExtraState`(eval_frame_cpp.cpp L494)→
`FrameLocalsMapping` O(1) 构造局部变量视图(L544,不物化 dict)→ 对每个 CacheEntry 调
`run_root_guard_manager()` → 命中则 `dynamo_eval_custom_code_impl`(eval_frame.c L285)把
`localsplus` 拷进 shadow frame 执行编译产物;全 miss 才回调 Python(L633)。
守卫失败钩子:`guard_collectives_hook`(L840)在分布式场景 all_gather 各 rank 的守卫结果,
一 rank miss 全体回退(通过 `set_guard_error_hook` 等 C API L67-68 注册)。

Python 侧唯一参与守卫的路径是 `Hooks.guard_fail_fn`(L1866)——每次 recompile 的回调出口,
`explain`/日志靠它收集。

## 8. Stance:运行时姿态控制(2024+ 新机制)

`DynamoStance`(L201)是一个进程级全局 `_stance`(L208),六种取值(L191-198):
`default` / `eager_then_compile` / `aot_eager_then_compile` / `force_eager` / `eager_on_recompile` / `fail_on_recompile`。
`torch.compiler.set_stance`(decorators.py L150)调 `_set_stance`(L227,禁止在编译区域内切换,L234)。

`_callback_from_stance`(L279)在**每次安装回调时**按 stance 改写回调:
- `force_eager` → 返回 `None`(L294-296,等价于 disable);
- `eager_on_recompile` → 返回 `False`(L297-299,C 层解释为 run-only,只重放缓存);
- `fail_on_recompile` → 返回包装函数 `fail_callback`(L304):凡是该编译而不该 miss 的帧,直接抛
  RuntimeError 并附守卫失败明细(L318-343,调 `_debug_get_cache_entry_list` + `get_and_maybe_log_recompilation_reasons`)
  ——CI 里抓 recompile 回归的利器;
- `eager_then_compile`/`aot_eager_then_compile` → `_create_delayed_compile_callback`(L376):
  前两次调用攒 example inputs(克隆成 meta,L371),首次 eager 直通,之后用
  `track_dynamism_across_examples`(L394)对比两份输入推断 dynamic dims,再正式编译——
  "先跑两次热身、第三次编译"的 inference 服务器模式。

## 9. disable/restart 动力学

**disable 家族**:`DisableContext`(L1484,`callback=None`)装饰函数时返回 `_fn`(L1523):
热路径极简——`set_eval_frame(None)` 直通执行(L1525-1548),并打上
`_torchdynamo_disable = True` + `_torchdynamo_disable_msg` + `_torchdynamo_disable_recursive`(L1566-1574)
标记。symbolic_convert 看到 `trace_rules.lookup` 命中这些标记就在 inline 前放弃,整棵子树回 eager。
`decorators.disable` 的 `reason` 参数最终就存在 `_torchdynamo_disable_msg` 里,graph break 报告会引用它。
`RunOnlyContext`(L1472)则是 `callback=False`:还在 Dynamo 体系内但只读缓存,
on_enter 递增 `GenerationTracker.generation`(L1476,cudagraph trees 依赖它)。

**嵌套语义**:compile/disable/optimize 可任意嵌套,靠三层机制解开:
`set_eval_frame` 的 prior 保存恢复(栈式)、`innermost_fn`(L727)穿透 `_torchdynamo_orig_callable` 链
(校验 `_torchdynamo_wrapper_id` 防止 bound method / functools.wraps 拷贝误穿透,L738-745)、
`always_optimize_code_objects`(L156,L1388 写入)让被 `@optimize` 直接装饰的 code 无视 skip 规则。

**reset**:`_TorchDynamoContext.__init__` L913-914 把 backend 登记进 `cached_backends`(L165),
`torch._dynamo.reset()` 遍历调 `backend.reset()`(L409-414)并清空缓存——restart 的核心。

## 10. 与图邻居的协作(convert_frame / output_graph / hooks / guards)

graph 的 imports 边显示 eval_frame.py 依赖 15 个文件,核心四个:
- **convert_frame.py**(编译期):本文的"另一半"。运行时门禁在此,编译流水线(`ConvertFrameAssert.__call__`
  查缓存计数 → `_compile` L1688 驱动 `InstructionTranslator`)在彼。两文件通过 `ConvertFrameReturn`
  (types.py,含 `guarded_code`/`frame_exec_strategy`/`skip_reason`)通信;
- **output_graph.py**:`OutputGraph`(L690)持图 + ShapeEnv + SideEffects;`compile_subgraph`(L2010)
  在图断裂/结束时收尾:finalizes 图 → 调 backend → 经 `PyCodegen` 生成出口字节码(resume 由
  resume_execution.py 续接);
- **hooks.py**:`Hooks` 三槽(guard_export/guard_fail/guard_filter)从 `_optimize` L1864 一路传到
  convert_frame 的守卫构建现场;
- **guards.py**(反向依赖本文):CheckFunctionManager 把 Python Guard 树翻译成 C++ GuardManager 树,
  `get_and_maybe_log_recompilation_reasons` 是 recompile 诊断的统一入口。

其余:`trace_rules.py`(哪些 code 可追/该跳)、`mutation_guard.py`(`install_generation_tagging_init`,
OptimizeContext.on_enter L1411-1412 挂 nn.Module `__init__` 代数标签,识别运行时动态创建的模块)、
`distributed.py`(guard PG)、`code_context.py`(per-code 弱引用上下文,export 的 orig_graphmodule L1042)。

## 11. 杂项但值得知道的

- `TorchPatcher.patch`(L2868,`@functools.cache` 只跑一次):disable 掉 jit.trace/FX Tracer.trace/
  fused optimizer step(防 Dynamo 误入),关掉 distribution 参数校验(L2892,纯性能);
- `explain`(L1932):`@patch("torch._dynamo.symbolic_convert.explain", True)` 开诊断模式,自造一个
  收集图/guard 的 backend 跑一遍,返回 `ExplainOutput`(graph 数、break 理由、op 计数、守卫、编译耗时);
- `export`(L2318,约 480 行,本文件最长函数):旧式 AOT 捕获入口,做参数展平
  (`argument_names` L1658 / `rewrite_signature` L2224 / `FlattenInputOutputSignature` L2006 把
  flatten 图签名还原嵌套结构)+ dynamic_shapes 规整——新代码请走 `torch.export`(其内部仍复用本层);
- `DynamoTLS`(L793):traced_frame_infos(退出时 L828 atexit 打印)+ skip_reasons 收集;
- L3.13+ 差异:L2590(convert_frame)对 `f_lasti` 判断"帧已开始执行"的阈值在 3.13 变了——
  PEP 523 语义随 CPython 版本演进的活例子。

## 12. 阅读地图(按调用频率)

```
每次编译调用(hot):  compile_wrapper L1147 → set_eval_frame/dynamo__custom_eval_frame
每次守卫评估( hotter): 纯 C++,eval_frame_cpp.cpp L342,Python 不参与 ← 90% 时间在这
首次配置(冷):       optimize L1786 → _optimize L1802 → _optimize_catch_errors L1582
诊断:               _debug_get_cache_entry_list L424 / explain L1932 / dynamo_tls L804
```

理解本文后再读 convert_frame.py(编译流水线)→ symbolic_convert.py(字节码模拟)→
output_graph.py(图收尾),即 Dynamo 主干的完整四部曲。
