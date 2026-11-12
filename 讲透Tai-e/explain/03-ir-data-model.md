<!-- source: knowledge-graph tour step 3 | files: src/main/java/pascal/taie/ir/stmt/AbstractStmt.java, src/main/java/pascal/taie/ir/stmt/StmtVisitor.java, src/main/java/pascal/taie/ir/exp/ExpVisitor.java -->

# 03 IR 数据模型：三地址码 Stmt/Exp/Var 与双 visitor 枢纽

### 1. 角色定位

Tai-e 链路是"前端 → IR → 分析"三段，`pascal.taie.ir` 是全部分析共享的唯一地基：每个非抽象方法一个 `IR` 实例，持有其全部变量与语句；接口组合 `IR extends Iterable<Stmt>, Indexer<Stmt>, ResultHolder, Serializable`（IR.java:43-44）。图谱 L3 分层中，ir 下依 language（type/classes）与 proginfo（MethodRef/FieldRef），上供 cfg/dataflow/pta/bugfinder 全线消费。IR 不含分析结论，语义由消费侧注入。

### 2. 内部结构

**Stmt：一接口、一骨架、三分族。** `Stmt`（Stmt.java:36）定义 index/lineNumber、getDef/getUses/canFallThrough 与 accept 分发（Stmt.java:71），其中 getDef 至多一个 LValue（Stmt.java:55-58）。包级私有 `AbstractStmt`（AbstractStmt.java:31）管 index（只许设一次，AbstractStmt.java:43-48）并默认无 def/空 uses/可穿透（AbstractStmt.java:65-78）。三族：

- **赋值族**：`DefinitionStmt<L,R>`（DefinitionStmt.java:36）→ `AssignStmt<L,R>`（AssignStmt.java:39，final 双字段）→ 按值类型特化：Copy/Binary（Binary.java:31）/New（New.java:37，一句顶三种 new）/FieldStmt（FieldStmt.java:33）派生 LoadField/StoreField（LoadField.java:36），及 Cast/InstanceOf/Phi 等。
- **调用族**：`Invoke extends DefinitionStmt<Var, InvokeExp>`（Invoke.java:48），全体系唯一可能无左值的定义语句（DefinitionStmt.java:44 的 @Nullable）。
- **跳转族**：`JumpStmt`（JumpStmt.java:27）抽象 getTargets()，辖 Goto、If（If.java:35）、两种 Switch。

散类中 Catch 是隐形 def 点（Catch.java:49-51）。`StmtVisitor` 为 22 种语句各备 default 重载（StmtVisitor.java:32-118）。

**Exp：标记接口 + 封闭子类集。** `Exp`（Exp.java:33）只要求 getType()/accept()；`LValue`/`RValue` 是零方法标记接口（LValue.java:28、RValue.java:28）。Var 双栖两边（Var.java:50），ArrayAccess 亦然（ArrayAccess.java:33）。五支：Var；Literal 九种；字段/数组访问；New 三态（NewInstance.java:30、NewArray.java:32；stmt 侧只有一个 New）；Invoke 五态（见第 5 节）；一元/二元——`AbstractBinaryExp`（AbstractBinaryExp.java:33）强制操作数是 Var，即"运算不嵌套"的落点，ArithmeticExp 内置 ADD/SUB/MUL/DIV/REM（ArithmeticExp.java:32-39），ConditionExp 只有六比较符（ConditionExp.java:32-40）。`ExpVisitor` 覆盖 31 种表达式（ExpVisitor.java:33-165；图谱摘要记 32 系含 visitDefault 的口径差）。

**享元缓存**：IntLiteral 预分配 [-128,127] 的 256 实例（IntLiteral.java:35-41），get() 命中即复用（IntLiteral.java:52-58）。

### 3. 外部连接

**谁消费 IR：** ① CFGBuilder 逐语句建边：If 出真假双边，其余靠 canFallThrough()（CFGBuilder.java:96-122，用 instanceof 而非 visitor）。② 数据流分析用 ir.getVarIndexer() 把 fact 压成位向量（LiveVariable.java:65）。③ pta：DefaultSolver 用内部 StmtVisitor 逐语句处理（DefaultSolver.java:589-597）并吃 Var 反向索引（DefaultSolver.java:374/476）。④ bugfinder/异常按语句种类枚举风险（NPEVarVisitor.java:39、ImplicitThrowAnalysis.java:70-71）。另有 IR.invokes() 默认排除 indy（IR.java:124-129），由 lambda 插件接管。

**IR 依赖谁**：language/type（ClassLiteral 经 World 取类型，ClassLiteral.java:46）；language/classes（Var/Invoke/New 持 JMethod container）；proginfo 的 MethodRef/FieldRef。

### 4. 数据流：`x = y + z; obj.f(x)` 的对象结构

```
├─ stmts
│  ├─ [0] Binary             // x = y + z
│  │   ├─ lvalue ─► Var{x}
│  │   └─ rvalue ─► ArithmeticExp{ADD, op1─►Var{y}, op2─►Var{z}}
│  └─ [1] Invoke             // obj.f(x)
│      ├─ result = null
│      └─ invokeExp ─► InvokeVirtual{MethodRef{f}, base─►Var{obj}, args=[Var{x}]}
└─ obj.relevantStmts.invokes += [Invoke[1]]  // 构造副作用
```

要点：① 一条源语句一条 stmt、无临时变量——Binary 直接以 y/z 为操作数（AbstractBinaryExp.java:35-36）：前端把栈槽建模为变量，iadd 栈槽可解析回源变量。getUses() 含 y、z 与 rvalue 自身（AssignStmt.java:67-75）。② Invoke 构造带副作用：base.addInvoke(this)（Invoke.java:70-73）登记进 obj 的反向索引，LoadField 同理（LoadField.java:40-43），这是"Var 知道谁在用我"的唯一来源。③ def-use 链即引用同一性：Binary.lvalue 与 Invoke.args[0] 是同一对象，== 即关系，无需额外结构。④ relevantStmts 惰性升级：初始指向 EMPTY 单例（Var.java:88），首次登记才换真对象（Var.java:261-265），多数变量终生空。

### 5. 设计决策

**三地址码而非 AST。** (a) 每语句至多一个 def（Stmt.java:55-58），fact 才能按 Var index 做位向量；(b) 控制流与 JVM 跳转指令一一对应，源码 a&&b 早被拆成 If+Goto，表达式内部无控制流；(c) DIV/REM 单独成 op，ImplicitThrowAnalysis 才有除零异常边（ImplicitThrowAnalysis.java:70-71）。

**不可变 Stmt/Exp，可变性锁进前端。** 字段 final（AssignStmt.java:42-44），args 构造即 List.copyOf（InvokeExp.java:50）。可变通道收窄：Stmt.setIndex 一次性、Var 的 setName/setType/setIndex 包级私有（Var.java:121-123），前端绕行走 VarMutator 白名单（VarMutator.java:32-34）。例外：跳转 target 公开可变（If.java:66），因前端先造语句后补目标；AbstractBinaryExp 被注释掉的 validate()（AbstractBinaryExp.java:42-44）是类型后定的物证。

**双 visitor vs instanceof 链。** 演化隔离：新增 stmt 只加一个 default 重载，现存 visitor 不破坏，未覆写的落 visitDefault（StmtVisitor.java:120-122）；匿名 visitor 可内联进算法（InterConstantPropagation.java:217）。但不教条：CFGBuilder 坚持 instanceof 链（CFGBuilder.java:99-118）——CFG 关心"边种类"而非语句类型。按关注点选访问机制。

**invoke 四态 + indy。** 五子类镜像 JVM 指令：InvokeStatic 无 base（InvokeStatic.java:32），Special/Virtual/Interface 经 InvokeInstanceExp 获得 base（InvokeInstanceExp.java:35）。语义差异编码进 getUses：static 只含参数（InvokeExp.java:97-99），instance 含 receiver（InvokeInstanceExp.java:49-54）——pta 的 dispatch 决策只需五谓词（Invoke.java:111-129）。

### 6. 新人提示

① 调试第一步：IRPrinter.print(ir, System.out)（IRPrinter.java:38-58），语句位置 [index@Lline]（IRPrinter.java:97-102）。② Var 编号语义：index 是方法内顺序号（IRBuildHelper.java:153），前端清理死槽位变量后整体重排（VarManager.java:297），分析合成 Var 填 -1（TransferHandler.java:274）——index 只配当数组下标，跨 IR 身份只能是对象引用（Var 未覆写 equals）。③ 网格访问：IR 即 Indexer<Stmt>，getVarIndexer() 给 Var 发号（IR.java:99），对称查询契约见 Indexer.java:41-52。④ getUses() 每次新建集合别缓存，且含 rvalue 自身等非 Var 元素。⑤ 删除/替换语句必须调 Var.removeRelevantStmt（Var.java:243-255），否则 pta 处理幽灵语句。⑥ Var 可携带 constValue（Var.java:77），前端为 ldc 常量所造；%this/%param/%temp/%return 是命名约定（IRBuildHelper.java:44-50）。
