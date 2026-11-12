# python/triton/language/core.py — tl DSL 语义心脏

## 1. 角色定位

13 层架构中属 **language-dsl（语言 DSL 语义层）**（图谱 tour 3）。3814 行定义 `tl.*` 的一切：类型系统、值对象、运算符协议与 builtin 函数。kernel 里每个 `tl.load`/`tl.dot` 都落到这里，再经 `_semantic`（semantic.py）调 `ir.builder`（L16 `from .._C.libtriton import ir`，pybind11 的 MLIR 构造器）产出 TTIR。本仓 e08ec19 已含 tensor descriptor。

## 2. 内部结构

- **builtin 协议**：`builtin`（L34）打 `TRITON_BUILTIN` 标记，wrapper 强制 `_semantic` kwarg，缺失即抛 "Did you forget to add @triton.jit?"（L40）；`_tensor_member_fn`（L50）把自由函数挂成 tensor 成员方法。
- **constexpr**：`constexpr`（L220）实现全套运算符使常量折叠透明传播；`_unwrap_if_constexpr`（L369）是最高频解包口。
- **类型与值**：`base_type`（L170）约定 to_ir/mangle 序列化协议，下辖 `dtype`（L400）、`pointer_type`（L677）、`block_type`（L719，禁 0d）；值侧 `tensor`（L870）持 IR handle，L913 起约 40 个 `@builtin` 运算符重载一行转发 `_semantic`，另有 `tuple`（L1308）、tensor_descriptor 族（L1392-1567，TMA）与 `_aggregate`（L1654）。
- **builtin 函数族**：`arange` L1848（端点须 2 的幂）、`dot` L2219、`load`/`store` L2347/L2408、`make_tensor_descriptor` L2471、`atomic_*` L2570-2689、`reduce` L2919、`range` L3565（携带 num_stages/warp_specialize 等 pipelining 属性），full/reshape 等同构。

## 3. 外部连接

图谱**入边**：`language/__init__.py`（tl 命名空间）、`math.py`/`standard.py`（扩充函数族）、`compiler/code_generator.py`（AST 执行器）与 gluon 层。**出边**：`_utils.py`、`runtime/jit.py`（L13 取 JITCallable）、`math.py`（core↔math 循环 import）。`_C.libtriton.ir` 是通往 C++/MLIR 唯一的桥。

## 4. 数据流

**一次 `tl.dot(a, b)` 的语义构造**：CodeGenerator（code_generator.py L294）AST 遍历中，`visit_Call`（L1532）识别 builtin 后注入 `_semantic`/`_generator` 再调用（L1496-1503）——builder 模式的真相：**tl 函数体在 AST 解释执行时被真正运行，即时产出 MLIR**。`dot`（L2219）先做：input_precision 默认推导（L2253-2256）、形状断言（L2264-2273）、rank≥4 时 reshape 降 3d（L2276-2283），随后 `_semantic.dot`（semantic.py L1446）做类型与硬件检查，`builder.create_dot(...)`（semantic.py L1544）创建 `tt.dot`。`reduce` 构造更深：`make_combine_region`（L2935）在 reduce op 的 region 里建 block，`_generator.call_JitFunction`（L2943）把用户 combine 函数编进 region，`_insertion_guard`（L2910）保护插入点。

## 5. 设计决策

**为何运算符重载+builder 而非 AST 全解析**：混合策略。表达式层借 Python 原生求值——`tensor.__add__`（L914）被直接调用即刻产 IR；控制流（短路、循环依赖）无法重载表达，留给 AST 访问器。铁证：`tensor.T` 直接 `assert False, "Transposition must be created by the AST Visitor"`（L1138）；`__not__` 不是 Python 魔法方法，注释直言 "our ASTVisitor handles it"（L1113）。**`_semantic` 隐式注入**免去全局 builder 且区分 host/device 语境。**constexpr 透明协议**：常量算术在 Python 层折叠不产 IR。**descriptor 取代 block pointer**：`make_block_ptr`（L2448）已改 raise NotImplementedError。

## 6. 新人提示

切入点：`python/tutorials/01-vector-add.py` → `03-matrix-multiplication.py` → `02-fused-softmax.py`（reduce/broadcast）。易错点：① tl 函数离开 `@triton.jit` 语境必抛 ValueError（L40）；② `arange` 端点须 2 的幂；③ 新增 builtin 要 `@builtin`+`_tensor_member_fn` 双装饰且后者在最外层；④ core↔math/semantic 循环 import，新 import 须放函数体内；⑤ `where` 不短路，访存遮蔽必须用 `load` 的 `mask`。
