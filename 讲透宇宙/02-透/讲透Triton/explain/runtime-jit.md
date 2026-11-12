# python/triton/runtime/jit.py — JITFunction：@triton.jit 与编译启动全流程

## 1. 角色定位

13 层架构中属 **runtime-backends（运行时与后端抽象层）**（知识图谱 tour 第 4 步）。1187 行：`@triton.jit` 把普通 Python 函数变成 `JITFunction`，负责参数特化、cache key 与 kernel launch 的 host 侧全流程。它不生成 IR，但决定何时编译、编译什么变体、何时复用缓存。

## 2. 内部结构

- **参数元数据**：`KernelParam`（L304）缓存 `is_constexpr`（L335）等。
- **可调用协议**：`JITCallable`（L472）的 `cache_key`（L522）先放 `recursion:{name}` 占位防自引用死锁（L530），再由 `DependenciesFinder`（L39）遍历 AST 得源码 hash 与全局变量引用。`KernelInterface`（L360）提供 `fn[grid](...)` 语法（`__getitem__` L369）与 `warmup`（L363）。
- **JITFunction**（L635）：`__init__`（L793）逐参建 KernelParam（`**kwargs` 形参直接 TypeError，L808）、`device_caches = defaultdict(self.create_binder)`（L818）；`run`（L733）launch 主路径；`_pack_args`（L709）+ `_do_compile`（L887）编译路径；`jit` 装饰器在 L963。

## 3. 外部连接

图谱**入边 19 文件**：`triton/__init__.py`、`runtime/autotuner.py`（@triton.autotune）、`compiler/code_generator.py`、`language/core.py`、`interpreter.py`、gluon 运行时等；**出边**：`driver.py`、`cache.py`、`_async_compile.py`、`backends`。`from ..compiler import ...` 为延迟 import（L700）解开 jit↔compiler 循环；特化热路径下沉到 C++（`native_specialize_impl`，L22）。

## 4. 数据流

**`kernel[grid](...)` 从调用到执行**：

1. `__getitem__`（L369）捕获 grid → `run`（L733）；`driver.active` 查 device/stream（L739）；首次触达设备时 `create_binder`（L696）造 binder。
2. `binder(*args)`（L749）完成绑定与特化，返回 `(bound_args, specialization, options)`。specialization 为每参数 `(type_str, spec_val)`：constexpr 参数标 `"constexpr"`；指针由 native_specialize_impl 判 16 字节对齐得 `"D"`、可整除得 `"N"`；int 值为 1 折叠成常量。
3. `compute_cache_key`（L611）把 specialization + options 拼成 key 查 `kernel_cache`；miss 则 `_pack_args`（L709）产出 signature、constexprs（L724）与对齐 attrs（L727），`_do_compile`（L887）构造 `ASTSource` 交 `compile()`。
4. launch 前校验 `used_global_vals` 未被篡改（L769）；grid 为 callable 时求值（L778）；`kernel.run(grid_0..2, stream, kernel.function, packed_metadata, hooks, *args)`（L786）进 C++ launcher。

## 5. 设计决策

**为何特化（constexpr/alignment/value）**：对齐信息让编译器敢发向量化访存，`==1` 值特化消枝，constexpr 进常量池参与展开——特化值必须进 cache key，否则错拿二进制；代价是变体爆炸，故暴露 `do_not_specialize`/`do_not_specialize_on_alignment`（L795-796）逃生门。**为何 exec 生成 binder**：注释直言 inspect.bind+apply_defaults "constitute much of the kernel launch overhead"（L400-402）——专用绑定函数让热路径零反射。**为何 AST 依赖追踪而非只 hash 自身源码**：kernel 调 kernel 的传递依赖任何一方变动都须失效；全局变量则选 launch 时校验报错（L769）而非静默重编译。**interpret 分流**：`knobs.runtime.interpret` 时改返 `InterpretedFunction`（L993）纯 Python 解释，可断点调试。

## 6. 新人提示

切入点：tour 第 4 步后跑 `python/tutorials/04-low-memory-dropout.py`，配合 `TRITON_CACHE_DIR` 看编译缓存。易错点：① kernel 引用的模块级变量编译后被改，下次 launch 直接 RuntimeError（L772）；② 不支持 `**kwargs` 形参（L808）；③ `@triton.jit` 函数不能 host 直接 `fn()`（L918），入口只有 `fn[grid](...)` 与 `fn.warmup(...)`；④ autotune 场景给 stride 类参数标 do_not_specialize，否则每个奇偶值都触发重编译。
