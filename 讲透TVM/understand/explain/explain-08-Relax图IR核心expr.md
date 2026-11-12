# explain-08 · Relax 新一代图 IR：src/relax/ir/expr.cc

## 角色定位

`src/relax/ir/expr.cc`（493 行）是 **Relax** —— TVM 为 LLM/动态模型时代设计的下一代图 IR——的节点构造器总册。与 tirx（explain-03/04，"一个 kernel 内部怎么算"）不同，relax 表达"**整个模型怎么组合**"：Function/Var/Constant/Call 构成函数层图，BindingBlock/DataflowBlock 组织副作用边界，SeqExpr 提供序列语义，ShapeExpr/MatchCast 支持符号化 shape（动态 batch/序列长度的一等公民）。文件头 L30-45 的反射注册表一次性列出 14 个节点；本文件与前几篇同款 `TVM_FFI_STATIC_INIT_BLOCK + GlobalDef().def("relax.XXX")` 节奏（fork 的 tvm::ffi 新反射体系，见 explain-04）。

本文件的独特分量在于它承载了 relax 的三大语义设计：一等符号 shape（ShapeExpr + Function 构造器里的 TIR 变量域检查）、数据流块与普通绑定块的二分（DataflowBlock/BindingBlock）、以及构造期类型规范化（每个节点构造时 ty 字段必须就位）。

## 内部结构

按行号走：

- **字面量与基础节点（L47-158）**：`If`（L47，cond/true_branch/false_branch 三件套）；`ShapeExpr`（L63-77）——**shape 值强制 int64**：字面量自动 cast（L66-69），非 int64 直接 ICHECK 拒绝（L70-71），并同步构造 ShapeType（L75）；`DataflowVar`（L86，数据流变量——只在 DataflowBlock 内合法的中间值）；`Constant`（L104-123）直接持有 `runtime::Tensor`（真数据！），无类型注解时从 data 的 shape/dtype 现场推导 TensorType（L110-120）；`StringImm`/`DataTypeImm`（L132/L146）类型都是 AnyType。
- **绑定三件套（L160-218）**：`MatchCast`（L160，运行时 shape 匹配断言——动态 shape 的关键节点，var 必须已定义 L162）；`VarBinding`（L177）；以及本文件最精致的一段——`VarBindingNode::SEqual/SHash`（L192-218）：**比较顺序依 value 是否为函数定义而变**——是函数时必须先比 var（L194-199 注释：递归函数体内引用被绑定变量，先定义 var 才能在使用点解析），其余情况 value 先比以获得更好的错误信息。SHash（L207-218）保持与 SEqual 完全一致的顺序——**相等与哈希的遍历序必须配对**，否则哈希表会出现"相等却不同桶"的灵异 bug。
- **块与序列（L220-288）**：`BindingBlock`（L220）；其 `CopyOnWrite`（L227-244）手写而非用宏——L228-232 注释说明原因：BindingBlock 是 DataflowBlock 的基类，宏版 COW 会把 DataflowBlock 错误降级成 BindingBlock，所以 L236-240 手工按动态类型克隆。`DataflowBlock`（L253）与 `SeqExpr`（L267-281，单参构造器 L267-273 做归一化：body 已是 SeqExpr 就原样接受）。
- **Function（L290-396）**：构造器即类型推导器。L297-300 逐参数断言类型已知（L293-294 注释自陈"conservative approach...known at construction time"）；L308-311 要求 ret_ty 与 body_ty 至少有一个；L315-316 决定用哪个返回类型（`IsBaseOf` 判 body 类型是否更细粒度）；L319-335 处理**符号变量提升**：body 内 MatchCast 引入的 TIR 符号变量（如动态 seq_len）在函数返回类型里只能引用**参数定义过的**变量——L325 `DefinableTIRVarsInType` 收集参数可用集，L334 `EraseToWellDefined` 清洗越域引用。`CreateEmpty`（L360-388）造带 `_dummy_function` 假 body 的空函数（L371-376），保证"空函数仍 well-formed"的不变量。
- **ExternFunc 与外部类型推导（L398-448）**：`infer_by_ty_args`（L402-411）按调用的类型参数推导返回类型（0 个→AnyType、1 个→直取、多个→TupleType），经 `GetExternFuncType`（L416-421）包成 OpaqueFunc 挂给每个 ExternFunc 默认构造（L423-424）——外部函数（库调用）无需注册也能有类型；显式传 Type 时校验必须 FuncType（L426-429）。
- **GetShapeOf 与 attr 工具（L450-489）**：`GetShapeOf`（L450-463）体现 relax 的 shape 哲学——静态 shape 直接取 TensorType 的（L456），未知才发 `relax.shape_of` 调用（L458-462）并同步写回类型；末尾 FuncWithAttr(s)/FuncWithoutAttr 三个 FFI 工具函数（L469-488）。

## 外部连接

- **头文件**：`include/tvm/relax/expr.h`（577 行，字段与继承树）；`expr_functor.h`（访问器/重写器）。
- **构造 API**：`src/relax/ir/block_builder.cc`——前端 translator（torch fx 等）全部经 BlockBuilder 发射节点，保证作用域与去重；直接调这些构造器的主要是测试。
- **类型系统**：`src/relax/type.cc`（ShapeType/FuncType/ObjectType 层级）+ `relax/analysis.h` 的 `IsBaseOf/UpdateType/EraseToWellDefined`（本文件 L316/L334/L461 都在用）。
- **下游**：`src/relax/transform/` 61 个 pass（explain-02 的 ModulePass）做图优化；`src/relax/backend/vm/codegen_vm.cc` 编译成 VM 字节码（explain-11）；`dataflow_pattern/` 做库级模式替换。
- **与 tirx 的接驳**：relax 的 Call 到 `relax.call_tir` 算子时携带 PrimFunc——tirx 的 SBlock 世界嵌在 relax 节点属性里，两层 IR 的分界线就在 Call 的 op 类型上。

## 数据流

torch 模型导入为例：fx 图逐节点 → BlockBuilder.emit_binding 产出 VarBinding（值在 DataflowBlock 内）→ 算子调用 emit Call，类型经 op 注册的类型关系函数推导，未知 shape 处 MatchCast+ShapeExpr → pass 管线里 to_non_dataflow 把 DataflowBlock 展平（fusion 需要的边界在 fuse_ops 前重新标注）→ codegen_vm 逐函数走字节码。每个环节构造节点都过本文件构造器，类型不变量全程保持——所以 relax 的 pass 永远不需要"先跑类型检查"的前置步骤。

## 设计决策

1. **类型构造期锁定**（L292-294）：类型不合法的图无法被构造，pass 链条上任何时刻图都是 typed 的——换来 pass 实现的自由（无需处理 Missing type）与调试的确定性。
2. **SEqual/SHash 顺序配对**（L192-218）：为递归函数专门调整比较序——图哈希正确性依赖相等与哈希的严格对偶，这是所有 IR 库最隐蔽的坑之一，这里给出了教科书级处理。
3. **COW 宏不可用的教训**（L227-244）：继承层级中基类 COW 必须保动态类型——L228-232 的"为什么不用宏"注释比宏本身更有教育价值。
4. **符号 shape 有作用域**（L319-335）：动态维度变量不是全局逃生门，必须由参数或 MatchCast 定义——让动态 shape 可推理而非退化成 Any。
5. **ExternFunc 默认带推导器**（L423-424）：外部符号"零注册可用"，类型从调用点 ty_args 反推——生态友好性优先于严格性，再可用显式 Type 覆盖。

## 新人提示

- 打印 relax 图时看到 `lv0/lv1` 前缀变量即 DataflowVar（DataflowBlock 内）；`x/GV` 前缀是普通 Var（可跨块/跨函数逃逸）——读懂 dump 的第一课。
- "Function must be constructed with either..."（L308-311）报错时：要么用 BlockBuilder emit 让 body 类型规范化，要么显式传 ret_ty。
- 动态 shape 调试从 MatchCast 与 `relax.shape_of` call 入手（L458 的 Op::Get 名字）；静态 shape 直接在 TensorType 里。
- 本文件所有 "relax.*" GlobalDef 名字即 Python 侧 `tvm.relax.*` 构造入口——查 API 签名直接读对应 lambda 参数列表最快。
