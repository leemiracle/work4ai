<!-- source: knowledge-graph tour step 6 | files: src/main/java/pascal/taie/analysis/graph/cfg/CFG.java, src/main/java/pascal/taie/analysis/graph/icfg/DefaultICFG.java, src/main/java/pascal/taie/analysis/graph/callgraph/PTABasedBuilder.java -->

# 06 · 程序图三件套：CFG、ICFG 与 CallGraph

### 角色定位

Tai-e 把程序结构拆成三张图。**CFG** 是刻意做小的接口（CFG.java:36），扩展 IndexedGraph 服务数据流位集合运算——StmtCFG 把 entry 映射为 0、stmt 右移 1、exit 垫底（StmtCFG.java:51-59）。**CallGraph** 是"谁调谁"的投影，边为 (callSite, callee, CallKind)，同时 extends Graph 与 StmtResult 故可按 stmt 查询。**ICFG** 缝合两者：可达方法集为节点域、各方法 CFG 为骨架，call site 处外接 call/return 边。依赖链写进配置：icfg 分析 `requires: [ cfg,cg ]`（tai-e-analyses.yml:91）。

### 内部结构

**CFG 边四族**（CFGEdge.java:39-94）：顺序流 ENTRY/FALL_THROUGH/GOTO、分支流 IF_TRUE/IF_FALSE/SWITCH_*、异常流 CAUGHT/UNCAUGHT_EXCEPTION、返回流 RETURN。携带数据的两族由子类承载：SwitchCaseEdge 存 caseValue、ExceptionalEdge 存异常集合；基类 getCaseValue 直接抛 AnalysisException——先判型再取数据，**责任在调用方**。

**DefaultICFG.build**（DefaultICFG.java:62-120）三层循环：遍历可达方法（getCFGOf 从 IR 结果仓库取 CFG，ICFGBuilder.java:103-105；取不到 warn 跳过并提示 `-scope REACHABLE`，DefaultICFG.java:65-68）；逐 stmt 登记 stmtToCFG，CFG 出边包装成 ICFG 边——call site 的包 CallToReturnEdge、其余包 NormalEdge（DefaultICFG.java:73-75）；Invoke stmt 则每 callee 加 CallEdge、每 return site 加 ReturnEdge（DefaultICFG.java:110-115）。两个细节：return site 不是"下一条语句"——getReturnSitesOf 返回 CFG 全部后继含 catch handler（DefaultICFG.java:143-146），被调方法异常才能传到 caller handler；exit 是 Nop 假节点，返回值/异常须从 exit 入边回扫收集进 ReturnEdge。

**PTABasedBuilder 是全包最薄的类**（PTABasedBuilder.java:37-44）：build() 两行——World 取 PointerAnalysis 结果再 getCallGraph。on-the-fly 特性全在求解器内部（见数据流节），它只把现成结果包装成 CGBuilder 形状，供 CallGraphBuilder 按 algorithm 分派（CallGraphBuilder.java:59-62）。

### 外部连接

**CFG → 过程内数据流全家桶**：AnalysisDriver 统一入口，拿 CFG、造分析、交 Solver（AnalysisDriver.java:44-49），LiveVariable 等全走此路。**ICFG → 过程间数据流**：InterSolver 核心循环是 meetInto(transferEdge(...))，transferEdge 按边类型分派到 transferNormalEdge/transferCallToReturnEdge/transferCallEdge/transferReturnEdge 四个抽象转移函数（AbstractInterDataflowAnalysis.java:98-108）——**ICFG 边类型系统直接定义了过程间分析的转移函数签名**，CallToReturnEdge 让 fact 可"跳过被调方法体"。**CallGraph → pta 侧**：taint 分析用 solver.getCallGraph() 拿上下文敏感版本（TaintAnalysis.java:172）。

**两条构建路线**：CHA 对虚调用枚举所有非抽象子类的 dispatch 结果（CHABuilder.java:169-174），便宜但 spurious 边多；PTA 按 receiver 指向集逐对象 dispatch，精确但需先跑完整 pta。CHA 显式 worklist 从 main BFS（CHABuilder.java:127-144），PTA 求解器事件驱动。CHA 遇 invokedynamic 只 warn + 空集（CHABuilder.java:183-186），PTA 靠 LambdaAnalysis 等插件建模。默认 cha 模式忽略 java.lang.Object 方法防假边（CHABuilder.java:155-157），另有 cha-full/cha-LIMIT（丢弃超限调用点）。

### 数据流

**链路一：try-catch 如何长出 exceptional 边。** CFGBuilder.analyze 先建 entry/exit mock Nop 节点与普通边，再按 exception 选项（explicit 默认/all/null，tai-e-analyses.yml:85）补异常边。两批起点不同：**隐式异常**（NPE、除零等自身失败）从 throwable stmt 的**前驱**出发（CFGBuilder.java:156-164）——javadoc 解释（CFGBuilder.java:126-149）：o.foo() 因 o 为 null 抛 NPE 时调用根本没发生，异常流源点必须是上一条语句；**显式异常**（Throw/Invoke 声明异常）从 stmt 本身出发（CFGBuilder.java:177-188）。catch 匹配由 CatchAnalysis 逐 handler 判 subtype，内层吃掉的不外流（CatchAnalysis.java:70-88）。落图时同 kind/source/target 的 ExceptionalEdge 合并只并入异常集（AbstractCFG.java:105-116），这就是 ExceptionalEdge 持可变 HybridSet 的原因（ExceptionalEdge.java:39-46）。

**链路二：虚调用如何在 pta 中长出 call edge。** ①receiver 指向集新增对象触发 processCall（DefaultSolver.java:473）；②对每个相关 Invoke，resolveCallee(对象类型, callSite) 分派，virtual/interface 走 ClassHierarchy.dispatch(type, methodRef)（CallGraphs.java:80-93）；③成功则选 callee context 构造 Edge（DefaultSolver.java:488），失败走 onUnresolvedCall 回调。addCallEdge 只把边压进 workList，出队后 callGraph.addEdge（CSCallGraph.java:77-82）、addReachableMethod 为 true 才处理新方法语句（DefaultSolver.java:872-881）。结束后 getCallGraph() **惰性**投影出上下文不敏感调用图（CIEdge 保留 CallKind，PointerAnalysisResultImpl.java:337-341）。

### 设计决策

**显式建图 vs 隐式合成。** DefaultICFG 完全物化：所有边灌进两张 MultiMap 加一张 stmtToCFG（DefaultICFG.java:51-55），代价是 NormalEdge 包装与内存放大，收益是可整体枚举、可 dump 的一等图。配套：AbstractICFG 把 callee/caller 查询直接委托给内部 callGraph（AbstractICFG.java:44-51）；CallToReturnEdge 只留 source/target、丢弃底层 CFGEdge 的 kind（CallToReturnEdge.java:34-36）——ICFG 层不区分 fall-through 还是异常旁路。

**Edge 不可变值类。** CFGEdge 用 (kind, source, target) 实现 equals/hashCode（CFGEdge.java:150-166），子类按携带数据扩展；call graph 的 Edge 同构且构造时预算 hashCode——海量边对象下的实际优化。唯一例外是 ExceptionalEdge：建图期可变、addEdge 合并后事实冻结。

**reachable 方法集管理。** AbstractCallGraph 的 reachableMethods 声明为非 final，注释明说允许子类自选结构（AbstractCallGraph.java:54-58）。两种答案：DefaultCallGraph.addReachableMethod 入集后**立即扫 IR** 登记 callSitesIn（abstract 方法跳过，DefaultCallGraph.java:49-62）；CSCallGraph 只做一次 add，语句登记交给 solver 的 stmtProcessor（CSCallGraph.java:66-68）。CHA 的"拉"与 PTA 的"推"在此分野。

### 新人提示

**可视化**：cfg 分析 dump 选项经 CFGDumper 每方法一个 .dot（exceptional 红边、switch 带 case 值，CFGDumper.java:47-74）；cg 分析产 call-graph.dot / reachable-methods.txt / call-edges.txt（CallGraphBuilder.java:43-47）；icfg 的 dump 给 call/return/call-to-return 边上蓝/红/灰虚线（ICFGBuilder.java:83-93）；pta 侧另有 FlowGraphDumper。**判空陷阱**：getCFGOf 可能返回 null（方法不在 scope），DefaultICFG 在 caller 与 callee 两处判空（DefaultICFG.java:65）；resolveCallee 标注 @Nullable 须调用方处理。**call graph 缺方法排查**：①默认 cha 静默丢弃 java.lang.Object 方法；② CHA 遇 invokedynamic 只 warn 不建边；③ scope 未开 REACHABLE 致可达方法缺 IR/CFG，warn 是信号；④ PTA 路线下反射/native 依赖插件；⑤ abstract 方法入集但不登记 call sites（DefaultCallGraph.java:51），空集属正常。
