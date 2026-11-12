<!-- source: knowledge-graph tour step 4 | files: src/main/java/pascal/taie/frontend/java/ir/BytecodeIRBuilder.java, src/main/java/pascal/taie/frontend/java/ir/IRBuilderContext.java, src/main/java/pascal/taie/frontend/java/ir/VarManager.java, src/main/java/pascal/taie/frontend/java/ir/BytecodeCFGBuilder.java, src/main/java/pascal/taie/frontend/java/ir/AsmInsnUtils.java -->

# 04 · 字节码→IR 翻译：java/ir 前端的九步流水线

> 先纠正旧称：`MethodIRBuilder` 不在 `frontend/java/ir/` 下——该目录主入口已演化为 `BytecodeIRBuilder.java:36`；现存的 MethodIRBuilder 在 `frontend/soot/MethodIRBuilder.java`，属旧 Soot 前端。

### 一、角色定位：ASM Tree API 的消费方

翻译**不**走 `visitMethodInsn` 式回调。类装载时 `FastIRBuilder.java:169-180` 让 `ClassReader.accept` 把每个方法的事件流灌进一个 `JSRInlinerAdapter`，JSR/RET 在此内联，指令收进 InsnList 包成 `AsmMethodSource.java:30` 缓存；L180 传 `SKIP_FRAMES`——Tai-e 自做栈模拟，不信任 StackMapTable；真正翻译是对 InsnList 的主动遍历分派（第四节）。包内分两层：门面 `FastIRBuilder.java:54`（实现 IRBuilder 接口）与引擎 BytecodeIRBuilder（每方法一个，跑完即弃）。

### 二、内部结构：一个上下文袋 + 四大管理器 + 九步流水线

**IRBuilderContext 是纯状态袋**（`IRBuilderContext.java:34`）：不可变输入（method/source/typeSystem，加 L96 从 `World.get().getOptions().isSSA()` 读的 SSA 开关）、四大管理器（L98-101）、图数据 cfg/dom（L85-90），各阶段直接读写字段。

**九步流水线在 `BytecodeIRBuilder.java:50-89` 一屏读尽**：①建 CFG（L55-57，CFGBuilder 携带 recordDUInfo/getExceptionType 两个回调，扫描顺带记 DU）；②建支配树（L61）；③初始化 SlotManager（L64）；④逐块翻译（L67，BytecodeProcessor）；⑤生成 phi（L70-71）；⑥收集语句（L74-79）；⑦删无用槽位变量（L82）；⑧类型推断（L85）；⑨组装（L88，IRAssembler）。

**四大管理器**：VarManager（`VarManager.java:53`）是变量工厂——槽位变量 `$N`（L304-312）、临时变量 `%vN`（L176-180）、常量缓存（[-8,7] 小整数与 `$null`，L83-85/213-218），并从 LocalVariableTable 还原真名（L370-396）。SlotManager（`SlotManager.java:37`）：load 按 reaching def 解析 Var、store 决定直接传播/落新槽位/丢弃（L124-173）。StmtManager 维护指令→语句双层映射（溢出的进 additionalStmts，`StmtManager.java:45-51`）。

**BytecodeCFGBuilder**（`BytecodeCFGBuilder.java:63`）四步建图：扫描定界（跳转/switch/return/throw 建块，L191-265；try 区内的 store 另触发拆块以保异常安全，L236-243）→ 排序 + fall-through 边 + 空块合并（L267-319）→ 补 jump/switch 边（L321-334）→ 补异常边（L351-363，try 区间每块连 handler）。

### 三、外部连接：上游 WorldBuilder，下游 ir/language

**触发链**：`JavaWorldBuilder.java:139-140` 注册 FastIRBuilder 进 World；分析首次调 `JMethod.getIR()`（`JMethod.java:179`，惰性求值）→ L190 `buildIR(this)`。`FastIRBuilder.buildIR`（L90-106）装载方法源后 `method2Source.remove(method)` **一次性消费**（二次构建即抛异常，L93-97）；批量 buildAll 用 parallelStream（L112-122），故每方法独立 context。依赖：向上 ASM Tree API + FrontendTypeSystem（`FrontendTypeSystem.java:123/202/230`）；向下 Var/DefinitionStmt 子类（`IRUtils.java:60-93`）、MethodRef、ExceptionEntry → DefaultIR。

### 四、数据流：一条 invokevirtual 的完整变换链

以 `o.f(x)`（返回 int）的 `aload o; aload x; invokevirtual` 为例：①步骤 1 对 invokevirtual 无感——非控制流边、不访存槽位；②步骤 4 按 `dom.getReversePostOrder()` 逐块处理（`BytecodeProcessor.java:131`），两条 aload 经 loadVar 压槽位 Var（L207-210），invokevirtual 命中 L339-344 分支；③getInvokeExp（L442-466）：toJClass(owner) → fromAsmMethodDesc(desc) → MethodRef.get → 循环 popVar() 弹参数（非 Var 表达式此时提升为 auxStmt）→ Collections.reverse 修正弹栈逆序 → 弹 base → L461 `new InvokeVirtual(ref, base, args)`；④压栈时 `mayHaveSideEffect` 为真（`IRUtils.java:98-100`），先 ensureStackSafety 把栈上既有副作用表达式全部提升，保证求值序先于调用（`OperandStack.java:242-251`）；⑤返回 void 则立即 popToEffect 生成无结果 Invoke（L328-336）；本例 InvokeExp 暂存栈上，等消费点 `popVar→toVar`（L371-394）分配 `%vN`，经 `IRUtils.java:74-75` 生成 `%vN = invokevirtual o.f(x)` 挂回该指令索引——"指令序 = 语句序"由此维持；⑥步骤 9 编 index、解析跳转、换 Phi、建异常表（`IRAssembler.java:113-158`）。

### 五、设计决策：骨架先行、惰性提升、phi 三段式

**两遍翻译**。步骤 1-3 先算完 CFG/支配树/DU 链/SSA，步骤 4 才生成语句：loadVar 需要 reaching def（`SlotManager.java:127`）；storeVar 靠 `isDefUsed` 丢弃死 store（L147-152，仍保副作用）；栈模拟需要逆后序保证前驱 outStack 已算好（`BytecodeProcessor.java:129-134`）。

**栈→寄存器：惰性提升 + 安全阀**。栈上存 Exp 引用，`pushExp` 不急于建变量，`popVar` 才提升补 auxStmt——`a+b+c` 可整体挂进一条 Binary 语句。两个强制提升点：副作用表达式入栈前先清栈（`OperandStack.java:244-246`）；DUP/SWAP 复制栈项前先 lift（L421-428）——表达式无法复制，只有 Var 能同时占两个栈位；双字值用 TOP 哨兵占位（L60）。

**phi 插入三段式**。局部变量层：步骤 3 的 insertPhis 用 worklist + dominance frontier 放 phi（`SSATransform.java:228-248`），但此时 phi 只是 DUIndex 扩展空间的逻辑节点（L43）；buildReachDefs 沿支配树先序回填输入（L254-321），"沿 def 链回溯到支配该点"的 reaching def（L441-471）是正确性关键。SSA 模式在步骤 4 才发射块头 FrontendPhi（`SlotManager.java:191-205`）；**非 SSA 模式一个 phi 语句都不发**，改由 reSlot（`SSATransform.java:342-391`）把 phi-web 拆成新槽位，loadVar 改查 getNewSlot（L176-181），`VarManager.java:352-361` 建同名 Var——局部变量槽位复用被拆开，更接近 SSA 却无需 Phi 语句。操作数栈层：mergeStacks 在多前驱合并、同位表达式不同时建 StackPhi（`OperandStack.java:151-204`，loop header 全量造 phi 特判 L185-195）；步骤 5 的 StackPhiResolver 落成 SSA 块头 FrontendPhi（`StackPhiResolver.java:122-140`）或非 SSA 前驱块尾显式赋值（L159-189）。used 标记沿依赖链传播（L67-85），没用到的 phi 直接消失。

### 六、新人提示

**调试**：dump 成品 IR 用分析 `ir-dumper`（`IRDumper.java:52`，输出 `output/tir/*.tir`）；字节码 CFG 的 dot 调试无 CLI 开关（包私有 `BytecodeDumper.java:46-51`）；断点下在 `BytecodeIRBuilder.java:50`。

**常见坑**：①一条字节码指令可产出多条 IR 语句，溢出语句存 additionalStmts（`StmtManager.java:116-139`）；②方法源一次性消费（`FastIRBuilder.java:92`），重复 buildIR 会炸；③VarStore 查 LocalVariableTable 要用**下一条真指令**做程序点（start_pc 语义，`VarManager.java:438-445`）；④先确认 `--ssa` 开关（`Options.java:381-385`，默认关）——两套 phi 路径差异巨大。

**与 Soot Jimple 的差异**：旧前端里 Jimple 已是三地址码，Tai-e 只做结构映射 + temp$ 内联；本包从栈码裸做起，变量名靠 LocalVariableTable 事后还原；Soot 的 AssignStmt 是单一大类，Tai-e 拆成十几个子类供下游精确匹配。读 IR 输出记三个前缀：`$` 槽位变量、`%` 临时/常量变量、`this`/`$null` 特例（`VarManager.java:59-65`）。
