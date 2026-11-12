<!-- source: knowledge-graph tour step 8 | files: src/main/java/pascal/taie/analysis/pta/core/solver/DefaultSolver.java, src/main/java/pascal/taie/analysis/pta/core/solver/PointerFlowEdge.java -->
# 08 · 指针分析主求解器：DefaultSolver 与 PFG 传播引擎

### 角色定位

`DefaultSolver` 是 Tai-e 的心脏：`pta` 分析把 `HeapModel`、`ContextSelector`、`CSManager`、options 注入给它（PointerAnalysis.java:115-116），`getResult()` 交出结果（DefaultSolver.java:919-926）。taint/reflection/lambda/spring 等上层能力以 `Plugin` 挂进 `CompositePlugin`（PointerAnalysis.java:129-166）——这正是 ISSTA 2023 论文的架构主张：**核心求解器只做与语言特性、上下文策略无关的 worklist 传播，其余全部外置**。DefaultSolver.java:99 一身二职：传播引擎 + 插件服务台（实现 Solver.java:90-228 全套 side-effect API）。

### 内部结构

求解状态在 `initialize()`（DefaultSolver.java:256-270）重建（150-166），不可重入；语句规则集中在 `StmtProcessor`（569-584）。

**主循环 `analyze()`（309-339）双层 while**：内层 drain worklist。`PointerEntry` 走 `propagate()`（317），diff 非空且指针是 `CSVar` 时按固定顺序触发五条规则——instance/array 的 store/load 四规则加 `processCall`——最后回调 `plugin.onNewPointsToSet`（318-325）；`CallEdgeEntry` 走 `processCallEdge`（326-328）。内层排空后调 `onPhaseFinish()`（330）——插件可再注入条目重启分析（Plugin.java:62-67）。超时由后台线程置标志（272-304），截断结果 warn unsound（332-335）。

**`propagate()`（345-363）是传播原子**：先应用指针自身 filters（347-353），`addAllDiff` 求增量（354），非空才沿出边逐 `Transfer` 送 target（356-360）。PFG 存储不在 `PointerFlowGraph` 里而在每个 `Pointer` 上（AbstractPointer.java:40-46），后者只是视图（PointerFlowGraph.java:57-59）。

**语句处理**：`addCSMethod`（871-882）去重后触发 `processNewMethod`（878）与 `StmtProcessor.Visitor`（885-887）。Visitor 只处理不依赖对象的语句：`New`、字面量、`Copy`/`Phi`、`Cast`、static 字段与调用（609-772，含 multiarray/finalize 特例 624-678）。**实例字段/数组访问被刻意跳过**（visit(StoreField) 只处理 `isStatic()`，751-752），由 base 变量 pts 变化驱动（第 4 节）。

**WorkList 排序关乎正确性**：`pollEntry` 强制 call edge 优先于 pointer entry（WorkList.java:65-69，注释 "for correctness"）——被调方法体扫描与参数/返回 PFG 边须先于对象传播落地。

### 外部连接

**九个 plugin 钩子**：`onStart`/`onPhaseFinish`/`onFinish`（269/330/338）、`onNewPointsToSet`（324，仅 CSVar 增量）、`onNewCallEdge`（550）、`onNewMethod`/`onNewStmt`（564-565）、`onNewCSMethod`（880）、`onUnresolvedCall`（496，解析不出 callee 时交插件接管）。`CompositePlugin` 用反射只把覆写了钩子的插件登记进对应分发列表（CompositePlugin.java:79-91），避免热路径空回调。

**消费 heap model**：抽象对象必须经 `HeapModel` 获取（HeapModel.java:35），缺省模型每条 `New` 一个 `NewObj`、常量与 mock 各自 intern（AbstractHeapModel.java:82,237-240）；`Obj.isFunctional()`（Obj.java:63-69）决定对象能否承载字段/数组边。

**消费 cs 元素**：`MapBasedCSManager` 的 `getCSVar`/`getInstanceField`/`getArrayIndex` 等全家桶把 (context, 元素) intern 成唯一指针（MapBasedCSManager.java:61-150）。**调用图内嵌驱动**——不委托外部 CallGraphBuilder：`processCall` 解析 callee、选上下文、把边排进 worklist（473-500,866-868），`processCallEdge` 去重落地、扫描被调方法、建参数/返回边（502-552）。

### 数据流

`o.f = p; q = o.f;`（同一可达方法，context-insensitive）的事件序列：

1. **方法可达**：入口方法经 `addEntryPoint`（DefaultSolver.java:828,833）可达，Visitor 扫描方法体但这两条语句此刻什么都不产生——IR 的 `Var` 已带语句索引（Var.java:200,188）。
2. **o 获得对象**：`o = new O()` 被扫描（609-614）→ `addVarPointsTo(o, o_i)` 入 worklist。
3. **双规则同事件触发**：`propagate(o,{o_i})` 返回 diff 后，`processInstanceStore`（319）对每个新 base 对象建边 `p → o_i.f`（383），`processInstanceLoad`（320）同时建边 `o_i.f→q`（409）。中间节点由 `getInstanceField(o_i, f)` 造出（382）——**每对象一个独立指针**，字段敏感由此落地。
4. **对象流经 store 边**：`p_j` 进入 p 后沿出边经 Identity transfer 送出（356-360）；边晚于对象建立时，`addPFGEdge` 补偿（816-825）重放 source 当前集合给 target。
5. **对象流经 load 边**：poll 到 `o_i.f`，沿 load 边把 `p_j` 送进 q——别名传播完成，全程未经过调用。注意 318 行的 `instanceof CSVar` 分支：字段指针的 diff 既不触发五条规则也不回调 `onNewPointsToSet`。

### 设计决策

**PFG 只存出边**：`getInEdgesOf`/`getPredsOf` 直接抛 `UnsupportedOperationException`（PointerFlowGraph.java:62-64,76-78）——算法只需前向遍历，入边零消费者。配套：**边身份只由 (source,target) 决定**（PointerFlowEdge.java:80-94），同一对指针只一条边；例外是插件 `OTHER` 边允许平行（AbstractPointer.java:99-107）。

**solver 与 plugin 的控制反转**：插件经 `setSolver` 拿引用（Plugin.java:52），用 `addPointsTo`/`addPFGEdge`/`addCallEdge` 等反向驱动求解（ClassInitializer.java:53 补 `<clinit>` 即例）。边界在 `removeEdgesIf`——严格限制在 `onPhaseFinish` 内（Pointer.java:100-107），删边破坏传播单调性，只能在 phase 边界做。

**on-the-fly 而非预建 call graph**：callee 按 receiver 的每个新对象解析（479-480），不可达方法永不进 `reachableMethods`；代价是反射/lambda 等解析不了的调用须走 `onUnresolvedCall`（496）。易漏细节：`this` 传递**不走 PFG**——`THIS_PASSING` 虽在枚举里（FlowKind.java:38），求解器直接 `addVarPointsTo` 注入 this（491-494），该 kind 只用于事后构建的 ObjectFlowGraph（ObjectFlowGraph.java:74）。

**上下文敏感两层**：配置层在 PointerAnalysis.java:79-109（`advanced=scaler/zipper/mahjong` 要先跑 CI 预分析再造 selector）；求解层每指针自带 Context，求解器只在两处问 selector——调用上下文 `selectContext(csCallSite, recv, callee)`（484-485）与堆上下文 `selectHeapContext(csMethod, obj)`（613）。另注意**双层过滤**：节点级 filter 在 propagate 入口统一应用且不可追溯（Solver.java:125-129）；边级 `TypeFilter`（cast 724-727、数组协变 434-437）在传播时应用。

### 新人提示

**阅读顺序**：`solve`（248）→ `initialize`（256）→ `analyze`（309）→ `propagate`（345）→ `processCall`（473）→ `processCallEdge`（502）→ `StmtProcessor.Visitor`（597）→ API 区（779-916）。

**断点位置**：`propagate` 入口（345，346 有现成 trace 日志）；`addPFGEdge`（816）看边建立与补偿重放；`WorkList.pollEntry`（WorkList.java:65）验证 call-edge 优先序。

**常见误区**：① **边方向**——`addPFGEdge(from, to)` 语义是"from 的对象流向 to"：store 边 `p→o.f`、load 边 `o.f→q`。② 以为实例字段读写随方法扫描处理——实际由 base 变量 pts 变化驱动（318-322）。③ **diff vs 全量**——`propagate` 返回增量（362），五条规则与 `onNewPointsToSet` 拿到的都是 diff。④ PFG 边动态生长，同一 (source,target) 只有一条。⑤ `Var` ≠ `CSVar`：同一 `Var` 在不同 Context 下是互不相通的指针。
