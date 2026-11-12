# explain-02 · Pass 体系与 PassContext：python/tvm/ir/transform.py

## 角色定位

`python/tvm/ir/transform.py`（367 行）是 TVM **所有 IR 变体的公共 pass 基础设施**——文件 docstring 一句话钉版："Common pass infrastructure across IR variants"（L18）。tirx 的 60+ 个 lowering pass、relax 的 61 个图 pass、s_tir 的调度 pass，全部构建在它定义的四个概念上：`PassInfo`（pass 元数据）、`PassContext`（执行环境/线程局部状态）、`Pass`（可调用变换基类）、`Sequential`（依赖解析的 pass 链）。Python 侧只是薄包装——每个方法都是一行 FFI 转发到 `_ffi_transform_api`，真正的依赖解析、opt_level 过滤、instrument 回调调度都在 C++ 的 `src/ir/transform.cc`（其 L61 用 `static thread_local PassContextThreadLocalEntry` 存当前上下文，这解释了为什么 Python 侧 `PassContext.current()` 无参可得）。

## 内部结构

四个 `@tvm_ffi.register_object` 类（行号锚定本文件）：

- **PassInfo**（L30-52）：`opt_level/name/required/traceable` 四元组。`required` 是 pass 间依赖声明的载体——`Sequential` 在 C++ 侧据此自动补齐缺失的前置 pass。
- **PassContext**（L55-140）：构造参数 `opt_level=2, required_pass, disabled_pass, instruments, config`（L78-85）；L86-96 对三类列表做规范化并手写类型检查（此处 `isinstance(x, list | tuple)` 是 PEP 604 写法）。核心是上下文管理器协议：`__enter__`/`__exit__`（L108-113）分别 FFI 调 `EnterPassContext/ExitPassContext`——所以惯用法是 `with tvm.transform.PassContext(opt_level=3, config={...}): tvm.build(...)`。静态方法 `current()`（L127-129）取线程局部当前上下文；`list_configs()`（L131-140）列出全部已注册的 PassContext 配置项（每个 pass 用 `TVM_REGISTER_PASS_CONFIG` 注册自己的开关）。
- **Pass**（L143-171）：基类。`info` 属性（L152-155）查元数据；`__call__(mod)`（L157-171）执行 pass，docstring 强调"for sequential pass, the dependency among different passes will be resolved in the backend"。注意 `__slots__ = ("__dict__",)`（L150）——这是允许子类继续挂任意属性的小技巧。
- **Sequential**（L185-223）：pass 序列容器，默认 `opt_level=0`、`name="sequential"`；L201-203 docstring 明确警告：Sequential 内部 opt_level 高于上下文的 pass 依然不会执行。

装饰器工厂 **module_pass**（L256-352）是用户扩展点：既可装饰函数（L340-348 直接 `MakeModulePass(pass_arg, info)`），也可装饰带 `transform_module(mod, ctx)` 方法的类——后者经 `_wrap_class_module_pass`（L226-253）包装成 `PyModulePass`：L237-238 的闭包 `_pass_func` 特意**不捕获 self**（注释 L235-236："important not to capture self to avoid a cyclic dependency"——Pass 对象持有 Python 实例引用 `_inst`，若闭包再捕获 wrapper self 会成环导致 refcount 泄漏），L245-247 用 `__getattr__` 把属性访问回退到被包装实例。L293-330 的两段 docstring 示例就是定制 pipeline 的官方姿势。末尾 **PrintIR**（L355-367）是个特殊"trace pass"，插在链里打印中间 IR，调试利器。

## 外部连接

- **上游供给**：`from . import _ffi_transform_api`（L27）绑定 C++ `TVM_REGISTER_GLOBAL("transform.*")`；类经 `tvm_ffi.register_object("transform.PassContext")` 等 type_key 接入对象系统（再次体现 fork 的 tvm_ffi 外包化）。
- **instrument.py**：同目录的 `tvm.ir.instrument` 定义 `PassInstrument`（enter_pass_ctx/exit_pass_ctx/run_before_pass/run_after_pass 四回调），经 PassContext 的 `instruments` 参数注入，实现 pass 级 profiling 与 trace 收集；`override_instruments`（L115-124）支持运行中热切换。
- **下游消费者**：`tvm.tirx.transform`、`tvm.relax.transform`（图谱 L07/L09 大层）所有 pass 类都继承这里的 Pass/ModulePass；`tvm.driver.build` 内部把 PassContext 状态传给编译管线；meta_schedule/dlight 调优也靠 `PassContext.current()` 读 config。
- **Python pass 落地**：因为 `MakeModulePass` 接受任意 Python callable，纯 Python 写的 pass（如 relax 的部分 dpl 规则）与 C++ pass 在 Sequential 里无差别混排。

## 数据流

一次典型执行：用户构造 `Sequential([pass_a, pass_b])` → `seq(mod)` 触发 `Pass.__call__` → C++ PassManager 先读**线程局部** PassContext（决定 opt_level 门槛、disabled 名单、config 项），再拓扑解析 `required` 依赖 → 逐个 pass：instrument 的 `run_before_pass` → 变换（ModulePass 走用户回调，返回新 IRModule）→ `run_after_pass` → 失败时经 DiagnosticError 上抛（被 explain-01 讲的 excepthook 拦截提示 TVM_BACKTRACE）。IR 不可变（immutable IRModule），每个 pass 返回新对象，链式传递。

## 设计决策

1. **元数据与逻辑分离**（PassInfo 独立成类）：让依赖解析可以在不实例化 pass 的情况下静态完成——Sequential 的 required 补齐全靠它。
2. **上下文用 with + thread_local 而非全局单例**：既支持嵌套（内层覆盖外层），又保证多线程调优（meta_schedule 并行测量）互不污染。
3. **类装饰路径防循环引用**（L235-243）：FFI 对象持有 Python 闭包、闭包持有业务实例、实例再持有 pass——只要闭包不捕获 wrapper self，环就断开。这是读这段代码最值得吸收的工程细节。
4. **Python 只做糖衣**：整个文件没有一行变换逻辑，全部转发 C++——保证 Python pass 与 C++ pass 走完全相同的 PassManager 路径（instrument/trace/依赖解析行为一致）。

## 新人提示

- `PassContext.list_configs()` 是发现隐藏调优开关的最快方法（如 `"tirx.use_cuda_sync"` 类配置）；带 `"relax."` 前缀的 config 大多是 relax pass 开关。
- pass 没生效先查三处：opt_level 门槛、`disabled_pass` 名单、依赖未满足——三者都在 PassContext 层面裁决，与 pass 本体无关。
- 调试用 `PrintIR("after xxx")` 插桩，比在 C++ 里加 printf 便宜得多；更系统的观察用 `tvm.ir.instrument` 的 timing instrument。
- 本文件与上游 TVM 的 `tvm/ir/transform.py` 几乎同名同构，但注意 fork 的 `traceable` 参数（L49、L212、L281）是较新的扩展，配合 meta_schedule 的 trace 回放使用。
