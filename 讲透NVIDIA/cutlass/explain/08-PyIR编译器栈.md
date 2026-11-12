# 08 · PyIR 编译器栈：Python AST 到 MLIR 的六层运行时与 _mlir_helpers

## 角色定位

PyIR 线是 CuTeDSL 的"Python 语义保持"编译路线：把用户 Python 函数的执行语义（赋值、控制流、循环携带、类事实）翻译成 MLIR，而非仅做表达式跟踪。它由两组文件构成：`base_dsl/pyir_*.py` 十文件（合计约 2.9 万行，图谱归入 base_dsl 域）与 `python/CuTeDSL/_mlir_helpers/` 十二文件（图谱域 58 节点，任务书口径 69 含装饰器）。C++ 侧的 cute MLIR 方言（第 10 篇）是它的编译目标之一。

## 内部结构

**六层运行时链**是 PyIR 的骨架，由 `pyir_runtime.py`（全文仅 30 行的 facade）注释钉版：pyir_state → pyir_core → pyir_corewalk → pyir_loop_carry → pyir_entrypoints → pyir_call_boundary，**每层 import 全部低层**（pyir_runtime.py:21-27 逐行 `from .pyir_xx import *`）；另有 pyir_class_facts 与 pyir_spec 两个"叶子"（明确标注 not part of the layer chain，pyir_runtime.py:28-29）。`pyir_runtime.<name>` 因此保持可用，`__all__` 由 scripts/gen_pyir_all.py 生成（pyir_runtime.py:17-19）。各层体量：pyir_core.py 9913 行、pyir_preprocessor.py 6327、pyir_entrypoints.py 5374、pyir_call_boundary.py 2417、pyir_state.py 1190、pyir_loop_carry.py 1135、pyir_class_facts.py 1026、pyir_corewalk.py 334。

**pyir_core.py 是语义核心**，围绕"memref scratch 准入"展开：load 值打 version/depth/epoch 标签（_tag_load pyir_core.py:114），函数/模块边界判定（_is_func_boundary_op L141），ref 可创建性（_can_create_ref L181），memref 判定（_is_memref_like L261），域内分配重绑定拒绝（_pyir_raise_memref_inregion_alloc_rebind L278），陈旧值拒发（_pyir_refuse_stale_memref_serve L372），op 先序判定（_pyir_op_strictly_before L414），以及准入/校验对 `_pyir_admit_scratch_rebind`（L470）/`_pyir_verify_scratch_admissions`（L548）——这套机制决定哪些跨 region 的寄存器化 memref 值可合法重绑定。

**_mlir_helpers 是 MLIR Python bindings 的加固层**：arith.py（1110 行）以模块级 `__getattr__`（arith.py:1105）延迟导入打破 arith↔vector 循环依赖；math.py（2289 行）`RoundingMode` 枚举（math.py:89）统一舍入语义，`_validate_fastmath_exclusive`（math.py:286）在 fastmath 与 NVVM approx/ftz 属性互斥时报错（sin/cos/exp2 调用处 L652/L754）；lru_cache_ir.py 提供 IR 值敏感缓存（`lru_cache_ir` L49）；op.py 管调试设施（`set_verify_trace` op.py:108、`loc_transform` L144）；dialect_proxy.py 的 `DialectAutoConvertProxy`（L17）自动做方言类型转换代理；dominance.py 给 SSA 叶遍历与支配性检查（`ssa_leaves` L36）；nanobind_compat.py 抹平 nanobind 版本差异。

**AST 装饰器双轨**：`cutlass_dsl/cutlass_ast_decorators_pyir.py:117` 的 `PyIRScfGenerator(ScfGenerator)` 是 PyIR 路线的 SCF 生成器，覆盖旧线 cutlass_ast_decorators.py 同名基类——两文件并存标示代际切换。

## 外部连接

最著名的消费者是 operators 库的 tile scheduler：`operators/cutlass/operators/providers/cutedsl/gemm/implementations/scheduler.py:31` 写着 `from cutlass._mlir import ir`——**该目标模块在仓内不存在**（python/CuTeDSL/cutlass/ 下无 _mlir*），由 MLIR 后端在运行时动态注入（批阶段甄别钉版）。`WorkTileInfo.__extract_mlir_values__`（scheduler.py:56）与 `__new_from_mlir_values__`（scheduler.py:61）用 helpers 的 extract/new_from_mlir_values（scheduler.py:37/39）把调度状态在 Python 对象与 SSA 值间往返。向 C++ 侧，PyIR 产出的 cute 方言 IR 由第 10 篇管线接管；向 Python 侧，base_dsl 的 AST 预处理（ast_preprocessor.py）喂给它。

## 数据流

用户 `@cute.jit` 函数 → AST 预处理（pyir_preprocessor.py 6327 行改写语法糖）→ PyIR 状态机逐语句执行（pyir_state 的 MutableValue/pyir_assign 语义经 facade 导出）→ 控制流降为 SCF（PyIRScfGenerator，cutlass_ast_decorators_pyir.py:117）→ 循环携带分析（pyir_loop_carry.py）与入口点处理（pyir_entrypoints.py）→ 调用边界（pyir_call_boundary.py）封口 → MLIR module 交编译后端。math/arith/vector helpers 在每个表达式节点处被调用并即时校验（如 fastmath 互斥）。

## 设计决策

1. **分层 import 全低层而非树状依赖**（pyir_runtime.py:21-27）：层序即初始化序，避免循环 import 用了一道 module `__getattr__`（arith.py:1105）之外的第二重保险。
2. **scratch 准入显式化**（pyir_core.py:470/548）：把"哪些 memref 可以寄存器化重绑定"做成显式 admit+verify 流程而非隐式启发式，错误可在编译期报告。
3. **helpers 与 bindings 分离**：_mlir_helpers 全部包装在 MLIR Python bindings 之上，bindings 版本抖动被 nanobind_compat.py 与 dialect_proxy.py 吸收。
4. **scheduler.py 的运行时注入**（scheduler.py:31）：operators 库不硬依赖 CuTeDSL 包内路径布局，_mlir 由后端供给——代价是静态分析（含本图谱 scanner）看不到该边。

## 新人提示

- 先读 pyir_runtime.py 全部 30 行——注释即架构图；再按层序读 pyir_state（1190 行，最小可懂层）。
- pyir_core.py 9900+ 行不要线性读：从 `_pyir_verify_scratch_admissions`（L548）的断言反推准入规则。
- 排查"奇怪的类型错误"先看 math.py 互斥校验（L286）与 dialect_proxy 自动转换——多数惊喜来自这两处。
- `import cutlass._mlir` 失败不一定是环境坏了：确认走的是 CuTeDSL 安装包（后端注入存在）而非裸源码树。
