# 01 · tilus Script 与 DSL 前端（"@tilus.script"之辨）

## 1. 角色定位

tilus 的用户编程面是 `python/tilus/lang/`：一个把 Python 类直译成 GPU kernel 的 DSL 前端。先纠一个流传甚广的误解（图谱摘要也中招）：**tilus 没有 `@tilus_script` 装饰器**——全仓 `python/`、`tests/`、`examples/` 零处出现 `tilus_script`；`lang/__init__.py` 只导出 `Class`、`Attributes`、`Script` 三件（`python/tilus/lang/__init__.py:15-16`）。写 kernel 是**类子类化**：`class MatmulV1(tilus.Script)`（`examples/matmul/matmul_v1.py:20`），官方文档同样如此定义（`docs/source/programming-guides/tilus-script.rst:8`）。唯一的装饰器是 `autotune`（`python/tilus/lang/script.py:106`），且它装饰的是 Script 类而非函数。

## 2. 内部结构

三层构成：**脚本模型**、**指令面**、**实例化引擎**。

脚本模型 `Script`（`python/tilus/lang/script.py:41`）只有两个真方法体：`__new__` 与 `__init__`。关键在 `__new__` 直接返回 `InstantiatedScript`（`python/tilus/lang/script.py:49-56`）——用户"实例化"Script 类时拿到的从来不是 Script 对象，而是经 `InstantiatedScriptCache` 缓存的实例化句柄；`__call__`/`compile` 在 Script 上永远 raise（:81-101），真身在 InstantiatedScript。类属性 `debug_block`（打印指定 block 的指令输出）与 `debug_schedule`（钉死单一 schedule 覆盖 autotune 空间，:44-47）是调试后门。

指令面 `RootInstructionGroup`（`python/tilus/lang/instructions/root.py:32`，2200 行 77 方法，全仓最大文件）就是 kernel 体里的 `self.*`：`load_global`（python/tilus/lang/instructions/root.py:476）、`store_global`（:528）、`store_shared`（:645）、`load_shared`（:619）、`free_shared`（:688）、`dot`（:856）、`cast`（:938）、`scan`（:1684）、`sync`（:1889）；硬件专属指令独立成 12 个组挂进 `self.cuda`/`self.tcgen05`/`self.tma`/`self.mbarrier` 等命名空间（`python/tilus/lang/instructions/__init__.py` 注册表 + `python/tilus/lang/modules/cuda.py:238`）。

实例化引擎在 `python/tilus/lang/instantiated_script.py`（1148 行，tilus 核心运行时）：`CallParameters`（:236）规范化参数；`extract_keys`（:340）把参数切成常量键/调参键——int 按 2 的幂与 16 整除性分桶（`_tuning_key_part`:334），保证形状邻近的调用命中同一特化；`span_space`（:54）+`generate_schedules`（:108）枚举 autotune 调度空间；`JitInstance`（:395）承载 transpile（`_transpile_programs`:629）→ 并行 build（`_build_programs`:760）→ autotune 选优（`_pick_best_program`:874）全流程。

## 3. 外部连接

向上，tilus 顶层 barrel 导出 `Script`/`autotune`/`InstantiatedScript`（`python/tilus/__init__.py:101-102`），dtype 全部来自 hidet 基座（`python/tilus/hidet/ir/dtypes/__init__.py`）——这就是 DSL 注解 `a_ptr: ~float16`（examples/matmul/matmul_v1.py:33）里 `~` 指针语法糖的来源：DataType 重载了 `__invert__`。向下，AST→IR 转译器 `Transpiler`（`python/tilus/lang/transpiler/transpiler.py:82`）继承 `ScopedProgramBuilder`（`python/tilus/lang/transpiler/builder.py:73`）+`PythonAstFunctor`，落成 Tilus Program；`for` 循环经 `RangeLoop`（`python/tilus/lang/constructs/loops.py:35`）适配为 ForStmt。侧向，转译依赖快照 `script_dependency_fingerprint`（`python/tilus/lang/script_dependencies.py:62`）保守捕获闭包/引用全局/方法，喂给 specialization 缓存键。

## 4. 数据流（一次调用的生命周期）

以 `examples/matmul/matmul_v1.py` 为例：① `MatmulV1()` 触发 `Script.__new__` → `InstantiatedScriptCache.get`（python/tilus/lang/script.py:50-54）按参数形状查缓存；② 未命中则 `InstantiatedScript.__call__`（python/tilus/lang/instantiated_script.py:1016）→ `_jit_instance_for`（:1088）构造 `JitInstance`；③ JitInstance 跑 `Transpiler` 把 `__call__` 源码 AST 翻成 Program（kernel 体里 `self.attrs.blocks/warps`（examples/matmul/matmul_v1.py:36-38）设置启动属性，`self.global_view`（:43）建立全局张量视图，`shared_tensor`/`register_tensor`（:46-51）声明存储）；④ 对 autotune 空间每个 schedule 生成 Program、走 drivers 六步编译、基准测速、选最优（`_pick_best_program`:874）；⑤ 之后每次调用直接派发到已编译 .so。缓存三层（scripts/programs/specializations，`CLAUDE.md:5-8`）让第二次运行零编译。

## 5. 设计决策

**为什么类而不是装饰器**：Script 的 `__init__` 天然承载编译期配置（block_m/block_n、num_warps），`__call__` 承载 kernel 体——类把"配置"与"体"分离成两个方法，装饰器函数做不到；autotune 空间声明也必须挂在类属性 `_autotune_space` 上（python/tilus/lang/script.py:121-123）。**为什么 `__new__` 返回外物**：把缓存查询做进实例化语法本身，用户写 `MatmulV1()` 就自动拿到缓存句柄，API 表面零额外概念。**为什么指令面 2200 行单文件**：`self.*` 是强命名空间的平铺 API，root.py 实为"标准库"，硬件组按需拆分（tcgen05 374 行 12 方法独立成 `python/tilus/lang/instructions/tcgen05.py`）。**为什么调参键按整除性分桶**：matmul 的 M/N/K 连续变化时避免每换一个数就重新特化，是 Triton 式 `tl.constexpr` 之外的另一种特化粒度设计。

## 6. 新人提示

- 读 `examples/matmul/matmul_v1.py` 一篇即可掌握 80% DSL 语法；末尾注释（:93-105）逐条解释 shared/load_shared/store_shared/free_shared/sync 的语义与"两次 sync"的原因。
- 写死调度调 bug：类属性 `debug_schedule=dict(...)` + `tilus.option.cache_dir(...)` 看生成的 source.cu（`CLAUDE.md:13`）。
- 想单测 kernel 的 IR：`InstantiatedScript._jit_instance_for(...)`（python/tilus/lang/instantiated_script.py:1088，CLAUDE.md:61 钦点）拿 `ji.transpiled_programs[0]`。
- `self.__call__` 里不能用任意 Python——转译器只认受控子集，报错类型是 `TilusProgramError`（`python/tilus/lang/transpiler/common.py:25`，带源码定位）。
- 闭包捕获的外部对象若不可哈希/不可追踪（opaque 对象、动态 import），specialization 持久化会保守回退为每次重转译（`python/tilus/lang/script_dependencies.py`，CLAUDE.md:16）。
