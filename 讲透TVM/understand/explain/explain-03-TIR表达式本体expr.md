# explain-03 · TIR 表达式本体：python/tvm/tirx/expr.py（fork 把 tir 改名 tirx）

## 角色定位

`python/tvm/tirx/expr.py`（1313 行）是 TIR（Tensor IR）**表达式侧 AST 节点的 Python 面目**。本 fork 做了一次结构性手术：把上游的 `tvm.tir` 拆成 `tirx`（IR 本体）与 `s_tir`（调度层），本文件就是 tirx 命名空间的表达式字典——常量、二元/比较/逻辑算子、Select/Ramp/Broadcast/Shuffle 向量节点、Let 绑定、IterVar 以及从 te 借来的 Reduce/CommReducer。文件头 docstring（L18-29）一句话给出使用范式：`x = tvm.tirx.Var("n", "int32"); y = x + 2; assert y.a == x`——表达式节点子字段可直接从 Python 访问。

最值得先看的 fork 痕迹：**Python 类住在 tirx，C++ type_key 却是 `ir.prim.*`**。L765 的 `@tvm_ffi.register_object("ir.prim.Add")`、L1194 的 `"ir.prim.Ramp"`、L1289 的 `"ir.prim.Let"` 表明 C++ 侧表达式节点已迁入 `tvm::ir::prim` 命名空间（对应 `include/tvm/ir/prim/expr.h`），成为 TIR/TE/Relax 共用的 prim 表达式基座；tirx 只是 Python 门面。

## 内部结构

文件三段式（行号锚定本文件）：

**第一段：运算符重载层（L47-313）。** `ExprOp`（L95）是所有可运算表达式的 mixin：`__add__` 等（L107-135）先经 `_is_scalar_operand`（L85-92）把关，非法操作数返回 `NotImplemented` 交给 Python 协议；注意 L88-91 特意**拒绝 BufferRegion**——"construct a BufferLoad explicitly"，防止把区域当标量。除法是重头戏：`div_ambiguity_error()`（L57-62）在 `__div__`/`__truediv__`（L137-163）检测到 int/int 时抛错，逼你显式选择 `div/indexdiv/floordiv/truncdiv`——整数除法语义（C 向取整 vs Python floor 取整）歧义被编译期拦截；`//` 与 `%` 无条件映射 FloorDiv/FloorMod（L165-175）。`~` 对 float 报错（L211-214）；`and/or/not` 直接 raise 并提示改用 `tvm.tirx.all/any`（L234-241）。L280-313 是一个跨模块 monkey-patch：把 `ExprOp` 的全部运算符**赋给 `tvm.ir._overload_prim_expr` 模块**，让住在 ir.prim 命名空间的表达式也获得同样的运算符——fork 拆包后保持旧 API 兼容的缝合术。

**第二段：延迟比较与常量（L316-424）。** `EqualOp`（L316）/`NotEqualOp`（L360）解决"一个 `==` 两种含义"：`a == b` 返回 `EqualOp` 对象，`if` 里求值时走 `same_as`（指针级同一，L342-346），需要构造 IR 节点时调 `asobject()`（L348-350）真正生成 `_OpEQ`。`IntImmEnum`（L404）用惰性求值延迟构造 IntImm，"constructor is not available in runtime"时也能当枚举用。

**第三段：AST 节点字典（L426-1313）。** 分组：基类 `ConstExpr/BinaryOpExpr/CmpExpr/LogicalExpr`（L426-443）；`IterVar`（L447-448，type_key `tirx.IterVar`）带九种迭代类型常量 `DataPar=0…Tensorized=8`（L476-484），构造时校验 Var 类型必须匹配 domain extent 类型；`CommReducer`（L527）与 `Reduce`（L572）type_key 是 `te.*`，经 `_get_te_constructor`（L47-50，`functools.cache` 缓存的 `get_global_func(f"te.{name}")`）惰性拿构造器——TE 的 reduce 节点被 tirx 复用但归属不动；常量三件套 `FloatImm`（L630）/`IntImm`（L662，`__hash__` 直接返回 value L690、支持 `__bool__` L701-702）/`StringImm`（L709）；算子全家桶 `Cast`（L741）、`Add/Sub/Mul/Div/Mod`（L765-863）、`FloorDiv/FloorMod/Min/Max`（L865-944）、`EQ/NE/LT/LE/GT/GE`（L945-1063）、`And/Or/Not`（L1065-1126）；`Select`（L1127，docstring 警告两个分支都可能被计算，要短路语义用 `if_then_else`）；`BufferLoad` 工厂函数（L1175，返回 `tvm.ir.TensorLoad`——fork 新引入的节点名）；向量三节点 `Ramp`（L1194）/`Broadcast`（L1227）/`Shuffle`（L1250）；`CallEffectKind`（L1278-1286，`ExprAnnotation=0/Pure=1/ReadState=2/UpdateState=3/Opaque=UpdateState`）标记 Call 副作用等级；`Let`（L1289）收尾。

## 外部连接

- **上游**：C++ 实现在 `include/tvm/ir/prim/expr.h` + `src/tirx/op/op.cc`（运算符真身）；构造经 `from . import _ffi_api`（L43）与 `tvm.ir.prim._ffi_api`（L37）双通道。
- **te 层**：`te/__init__.py` 反向 re-export tirx 运算符；`CommReducer/Reduce` 是 te compute/reduce DSL 的支柱，`create_prim_func` 把 te 图降级成 PrimFunc 后这些节点原样进入 tirx 世界。
- **TVMScript**：`Scriptable` 基类（L448、L528 的继承列表）让节点可打印回 Python 语法；parser 侧反向构造这些类。
- **arith 分析引擎**：本文件全部节点都是 `src/arith/analyzer.cc` 化简的对象——表达式树越"正则"（div 语义显式），int solver 越能证明循环变换安全。

## 数据流

以 `T.add()` 为例：`__add__`（L107）→ `_ffi_api._OpAdd(self, other, None)`（第三个参数是 span）→ C++ 构造 `ir.prim.Add` 节点做类型检查（dtype 提升在 C++ 侧）→ 返回的 ObjectRef 被 tvm_ffi 包装成 `Add` 类实例回 Python。节点不可变，"修改"即重建整棵子树——这是所有 tirx transform pass 用 Rewriter（自底向上重建）而非原地改写的原因。`x == 2` 则停留为 EqualOp，直到 `asobject()` 或被塞进需要 Expr 的位置才物化。

## 设计决策

1. **div 歧义编译期拦截**（L57-62）：不同后端整数除法语义不一（trunc vs floor），上游历史上踩过坑，这里把选择权强制交还用户——API 设计课范本。
2. **延迟等号**（EqualOp）：同一符号在"Python 布尔上下文=指针同一"与"IR 构造上下文=EQ 节点"间自动切换，兼顾 `assert x.same_as(y)` 与 `T.where(x == y, ...)` 两种惯用法。
3. **type_key 与 Python 包解耦**（tirx 类挂 `ir.prim.*` key）：C++ 层先把 prim 表达式下沉为多 IR 共享底座，Python 层再按域分包——跨语言命名空间不必一一对应，注册键只认 C++ 事实。
4. **monkey-patch 桥**（L280-313）：不给 ir.prim 写第二份运算符，而是把 ExprOp 方法注入对方模块——一处定义两处生效，代价是读 `_overload_prim_expr.py` 时会看到"凭空出现"的方法。

## 新人提示

- 写 kernel 遇到 "multiple types of integer divisions" 就是 L57 命中：循环下标用 `//`（FloorDiv），bit 折算用 `tirx.truncdiv`。
- `if expr:` 报 ValueError 时看 L234 的提示：IR 里没有短路布尔，用 `tirx.all/tirx.any`。
- `Select` 两个分支都算（可能越界读），边界保护场景换 `if_then_else`（L1100 附近的 docstring 专门警告）。
- 找某个节点的 C++ 字段定义：type_key 前缀才是地址——`ir.prim.*` 去 `include/tvm/ir/prim/expr.h`，`te.*` 去 `include/tvm/te/`，`tirx.*`（仅 IterVar 等少数）去 `include/tvm/tirx/`。
