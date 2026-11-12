# low_level_ir.py 深度解析：pre-lowering 低层 IR 契约校验器

> 源码：`tirx_kernels/kern/low_level_ir.py`（274 行）｜图谱节点 `file:tirx_kernels/kern/low_level_ir.py`（complexity=moderate，tested）

## 角色定位：在 14 层架构中的位置

low_level_ir.py 属于 **Kern DSL 内核语言层（kern-dsl）**——图谱标注该层 fan-in 105 为全库最高，是所有 GPU kernel 的编写基座：`@K.kernel` 入口追踪、共享内存与 TensorMap 地址构造、warp 角色分区、软件流水线协议、tile 调度器都在这层。它是导览 Tour#5 定名的"DSL 的质量闸"。存在的理由：TIRx 是 **PTX 级**的低层 DSL，一旦 lowering 之后，TVM 面向高层张量程序的常规保障（tiling、自动内存管理）既不适用也来不及介入；所以"低层 kernel 的合法书写约定"必须在 **lowering 之前**以静态检查落实。这个文件把四条隐式约定升格为机器可判定的显式契约：(1) 不得使用 tile 原语——低层 kernel 已经手工完成调度，再用 tile 是语义错位；(2) 不得直接访问 `global`/`shared` scope 的 buffer——这些地址必须经 DSL 的地址构造原语进入；(3) `setmaxnreg`（PTX 寄存器再分配）必须搭配 `launch_bounds_min_blocks_per_sm` 属性，否则占用契约无法对账；(4) `func_call` 只能调白名单内函数。

## 内部结构：5 个子节点的紧凑设计

图谱 contains 边只列 5 个，源码同构：

- **`LowLevelIRFinding` / `LowLevelIRReport`**（50-100 行）：两个 frozen dataclass。前者是一条发现（函数路径、kind、节点类型、scope/callee、span 定位）；后者聚合 `checked_functions` / `violations` / `func_calls` / `address_only_loads` 四元组，`ok` property 仅看 violations 是否为空，`summary()` 产出人类可读文本。
- **`LowLevelIRContractError(ValueError)`**（103-108 行）：携带完整 report 的异常——抛错时不丢上下文。
- **`_LowLevelIRVisitor`**（111-184 行）：继承 TVM `StmtExprVisitor` 的访问者，四条契约的检测逻辑全在这里（覆写 `visit_op_call_` / `visit_attr_` / `visit_buffer_load_` / `visit_buffer_store_` / `visit_call_`）。
- **`_span_text` / `_iter_prim_funcs`**（31-47 / 191-219 行）：定位格式化与 PrimFunc 递归解包。前者把节点 span 渲染成 `文件:起始行列-结束行列`——违规报告能直接跳回 DSL 源码的精确区间，不必反推 AST；配合 `_node_name` 去掉类型名的 `Node` 后缀（如 `BufferLoadNode` 显示为 `BufferLoad`），报告可读性是第一公民。
- **`inspect_low_level_ir` / `check_low_level_ir`**（222-265 行）：双入口——前者返回报告不抛错（诊断），后者违规即抛 `LowLevelIRContractError`（断言）。

## 外部连接：图谱边视图

- **imports →** `tvm`、`tvm.tirx`、`tvm.tirx.stmt_functor.StmtExprVisitor`——本文件对 TVM 的唯一依赖是访问者基类，校验全程不触碰 codegen。
- **tested_by ←** `tests/test_low_level_ir.py`。
- 没有对库内其它文件的 import——它是纯叶子模块。反方向，kern 层的 `get_kernel` 返回值（PrimFunc/IRModule/嵌套容器）正是它的输入；上层入口追踪（`@K.kernel`）产出什么、它就检查什么，这种"生产者-契约校验者"的配对让 DSL 每个公开入口都有质量闸。`__all__` 只导出两个入口与三个类型，`_LowLevelIRVisitor` 有意保持私有。

## 数据流：inspect_low_level_ir 走读（222-255 行）

输入是任意 `get_kernel` 返回值。三步：

1. **解包**：`_iter_prim_funcs` 递归下钻——`PrimFunc` 直接收；`IRModule` 按全局变量逐函数取出（非 PrimFunc 立即 TypeError）；list/tuple 按下标、dict 按键继续下钻，路径记成 `root.main`、`root['head'][0]` 这样的可读串；走到尽头还不是 PrimFunc 就报"期望什么、实际是什么"。空集合同样报错（247 行）。
2. **逐函数访问**：每个 PrimFunc 配一个**全新的** visitor 实例，`visitor(prim_func.body)` 遍历语句树——不复用实例是为了让 `has_min_blocks_per_sm` 旗标与 setmaxnreg 收集表的配对判定严格按函数作用域隔离，多函数 kernel 里 A 函数的属性不能"帮" B 函数过关。路径串一路随身，报告能指认到 `root.module.wrapper` 级别。四类钩子：
   - `visit_op_call_`（136-138）：任何 op_call 一律记 `tile_primitive` 违规——tile 原语在低层语境里没有合法形态。
   - `visit_buffer_load_` / `visit_buffer_store_`（145-158）：`str(op.source.scope())` 前缀匹配 `global` / `global.*` / `shared` / `shared.*`（`_is_forbidden_scope`，23-24 行）即记违规。注意两者都**手动递归 indices/value 表达式**——因为地址表达式里还可能嵌着真正的内存读。
   - `visit_call_`（160-184）：按 op 名三分支——`tirx.ptx.setmaxnreg` 先记入 `setmaxnreg_calls`（是否违规延后到整函数遍历完判定，因为配套属性可能出现在调用之前或之后的任意位置）；`tirx.cuda.func_call` 记入 `func_calls`，callee 不在 `allowed_func_calls` 白名单即同时记违规；`tirx.address_of` 单参数且操作数为 TensorLoad 时走**指针语法豁免**（下详）。
   - `visit_attr_`（140-143）：见到 `tirx.launch_bounds_min_blocks_per_sm` 属性就点亮 `has_min_blocks_per_sm` 旗标。
3. **后验与汇总**（241-245）：`setmaxnreg_calls` 非空且旗标未亮，才把整批 setmaxnreg 升格为违规；四类发现跨函数汇总进 frozen report。`check_low_level_ir` 在此之上加一句"not ok 即抛"。

## 设计决策：值得学习的模式

- **契约即类型（contract as types）**：把"低层 kernel 该怎么写"从文档约定变成可执行断言，错误在 CI 阶段而非 codegen 深处爆炸。配合抛错携带完整 report（而非只有消息），调用方既能 print 也能程序化处理。
- **地址取值的指针语义豁免**（170-183 行）：`tirx.address_of(TensorLoad)` 里的 TensorLoad 是"取地址"语法，不是内存读——若按普通 load 判就会误报 global/shared 违规；但它只豁免"取地址"本身，TensorLoad 的 **indices 仍被手动递归**（178-183 行注释言明：索引表达式里的真读取照常检查）。这是"语义区分到 AST 子节点级别"的精细处理，是本文件最值得细读的一段。
- **setmaxnreg 的两遍判定**：配对约束（调用 ↔ 属性）无法在单节点判定，先收集后后验——比"看见调用立即判"多容忍"属性在调用之后声明"的合法写法，避免顺序敏感的误报。
- **inspect/check 双入口**：诊断场景要全量报告（哪怕几十条违规一起列），断言场景要 fail-fast——一个动词的两种语用，比布尔参数 `raise_on_error` 更自描述。
- **frozen dataclass 报告**：结果不可变、可哈希、可比较，测试可以直接 `assert report.violations == (...)`，不用解析字符串。
- **白名单参数化**：`allowed_func_calls` 是函数参数而非模块常量，调用方按 kernel 的合法外部调用集合注入——校验器不替业务做决定。

## 新人提示

- 阅读切入点：先读 `tests/test_low_level_ir.py`——每条契约都有对应的违规样例与通过样例，测试即文档；再回来读 `_LowLevelIRVisitor` 的五个 visit 方法。
- 易混淆点一：**违规（violations）与记录（func_calls / address_only_loads）是两类东西**——后两者是合法行为的登记（供上层审计"这个 kernel 调了哪些外部函数、做了哪些纯取址"），只有前者影响 `ok`。看 summary 输出时别把"recorded N func_call(s)"当成错误。
- 易混淆点二：`visit_buffer_load_` 里手动 `self.visit_expr(index)` 后**没有**调 `super()`——默认遍历会被绕开，这是刻意的（TensorLoad 本身已被处理，只需检查索引）；漏看这一点会以为有 bug。
- 易混淆点三：`_iter_prim_funcs` 对 IRModule 里混入非 PrimFunc 函数直接 TypeError 而非跳过——契约校验宁可失败也不静默缩小检查范围，这与 bench_suite 的 fail-closed 哲学一脉相承。
- 本文件刻意不做 lowering（docscript 强调 "without lowering it"）——它是 pre-lowering 闸门；lowering 之后的问题归 codegen 诊断体系管，别在这里找。
