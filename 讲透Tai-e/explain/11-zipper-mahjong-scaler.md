<!-- source: knowledge-graph tour step 11 | files: src/main/java/pascal/taie/analysis/pta/toolkit/zipper/Zipper.java, src/main/java/pascal/taie/analysis/pta/toolkit/mahjong/Mahjong.java -->
# 11 · 上下文敏感度工具箱：Zipper / Mahjong / Scaler

### 角色定位

`pta.toolkit` 下这三个包是 pascal-lab 三篇论文在自家框架的落地，都在回答上下文敏感分析的按需分配问题：Zipper 决定**哪些方法**值得上下文敏感（产出 `Set<JMethod>`），Scaler 决定每个方法**用哪种变体**（产出 `Map<JMethod, String>`），Mahjong 不碰上下文，从堆端合并等价对象（产出 `HeapModel`）。

论文出处以 package-info 实证：Zipper = OOPSLA 2018 加 TOPLAS 2020 扩展（zipper/package-info.java:27-34）、Mahjong = PLDI 2017（mahjong/package-info.java:27-30）、Scaler = ESEC/FSE 2018（scaler/package-info.java:27-30）——流传的 "OOPSLA'22/'23/'21" 年份全对不上，勿引。另一勘误：原论文工具仓的 `ZipperAnalysis`/`AchievabilityAnalysis`/`ContextSelectorBenchLiveFiles` 在 Tai-e 中不存在，落地形态是三个由 `PointerAnalysis.analyze()` 内联编排的普通类。

### 内部结构

**编排入口** PointerAnalysis.java:79-109：`advanced` 四分支——`collection` 用 `CollectionMethods` 免预分析；其余三分支先跑一遍**CI 预分析**（87-88）再分派：`scaler*`→`makeGuidedSelector`（89-92）、`zipper*`→`makeSelectiveSelector`（93-96）、`mahjong`→整体替换默认堆模型（97-99 对 77）。

**Zipper** 三步走。构造器建 ObjectAllocationGraph（OAG）与 PotentialContextElement（PCE）（Zipper.java:113-117）：OAG 记"对象→其上被调方法内分配的对象"（ObjectAllocationGraph.java:54-63）并累计传递 allocatees；PCE 对每类型并行算"该类型对象（含 allocatees）上被调方法集"（PotentialContextElement.java:58-69）。主流程对全部类型并行建精度流图（151）：`PFGBuilder` 以"类型对象上被调方法的参数"为 IN（PFGBuilder.java:125-133）、"返回变量"为 OUT（135-156），从 IN 做 DFS——store 到本类型对象域时加 wrapped 边绕到 this（223-234），其余边要求目标方法在 PCE 集内放行（211-222，滤 CI 伪流）；最后从 OUT 反向收集可达节点（203-219），映射回方法再经 PCE 过滤（184）——即"逃出又流回 OUT 的方法"。

**Mahjong** 四阶段（Mahjong.java:56-68）：`FieldPointsToGraph` 并行抽取 对象-Field-对象 映射（FieldPointsToGraph.java:50-69）；`DFAFactory` 对每对象把 FPG 视为 NFA 做 subset construction，相同状态集全局共享 DFAState（DFAFactory.java:92-99）；按类型分组并行两两等价判定（75-97），判定用 Hopcroft-Karp 风格算法：并查集合并起始态、弹栈遍历出边并集、根不同则 union（DFAEquivChecker.java:52-67）；预过滤：DFA 任一状态输出多类型的对象直接出局（113-129），保证 type-consistent。结果由 `MahjongHeapModel` 转成 New 分配点到 `MergedObj` 的映射（MahjongHeapModel.java:50-67）。

**Scaler**（Scaler.java:91-123）构造从精到粗的上下文计算机 `2-obj`/`2-type`/`1-type`（98-101，以 OAG 入度估计上下文数）。核心是二分：找最大 ST 使全程序累计权重不超 TST（131-154）；方法权重 = 变体上下文数 × CI 指向集大小（212-215），从最精变体起找第一个可承受的，全超则落回 CI 底线（181-196）。

### 外部连接

三者共同上游是 CI 预分析的 `PointerAnalysisResult`：Zipper 取 `getObjectFlowGraph()`（Zipper.java:117）；Scaler 复用 `toolkit/util/OAGs` 通用 OAG（Scaler.java:96），与 Zipper 专用版是两套实现；Mahjong 只读字段指向结果。下游注入点就是 DefaultSolver 的 heapModel 与 selector 两参（PointerAnalysis.java:115-116），**solver 对三工具零感知**。

两个 selector 语义不同：Zipper 的 `makeSelectiveSelector(cs, pcms)` 把 `cs` 选项的单一变体只应用于方法集内（ContextSelectorFactory.java:90-103），`SelectiveSelector` 全有或全无——不命中给 emptyContext（SelectiveSelector.java:68-79）；Scaler 的 `GuidedSelector` 逐方法分派 ci/1-type/2-type/2-obj 四档（GuidedSelector.java:85-95）。

三工具**互斥**：`advanced` 是单值选项。mahjong 分支不设 selector，最终走 `makePlainSelector(cs)`（PointerAnalysis.java:106-108）——只改堆不改上下文；堆与上下文维度理论上正交可组合，但当前分派不支持。

### 数据流

看"逃逸又回收"如何被 Zipper 识别。取 directFlow（src/test/resources/pta/misc/Zipper.java:9-13）：`Box b = new Box(); b.set(new Object()); o = b.get();`。对 type=Box：IN = `Box.set` 的参数 item，OUT = `get` 的返回变量。DFS 从 item：`this.item = item` 是 store 且 base 类型==Box，加 wrapped 边到 set 的 this；this 传到 get，`return item` 处 load 流回 OUT。反向可达集覆盖 set/get 全部节点，映射回 {set, get} 且都在 PCE(Box) 中 → precision-critical：参数值经字段逃逸又经返回回收，不敏感就会串流多个 Box 实例的数据。unwrappedFlow（29-39）则走捷径——返回值与 IN 指向集相交时直接加边连回（PFGBuilder.java:191-203）。

Mahjong 判定等价看测试 Mahjong.java:1-12：`x.f=new B(); y.f=new C(); z.f=new C(); a=z.f; (C)a`。CI 下 x.f 指向 {B,C}，cast may-fail。x 与 y：起始态输出同为 {A} 可合并，f 转移得 {B},{C}，validate 发现输出类型并集大于最小集（DFAEquivChecker.java:79-91）→ 不等价；y 与 z 结构输出全同（{A}-f→{C}）→ union。两个 `new A()` 分配点映射到同一 `MergedObj<A>`，第二轮分析 merged.f 只含 C，`a=z.f` 亦然，cast 不失败——MahjongTest 断言 may-fail-cast 为 0（MahjongTest.java:42-49）。

### 设计决策

**精度-规模三角**。Zipper 精度导向：识别"数据经字段回流的方法"，每类型独立小 PFG 并行分摊（Zipper.java:151）；Zipper-e 加量化截断——类型组的 precision-critical 方法累计指向集超 `pv ×` 全程序总量则**整组放弃**而非逐方法放弃（133-147,194-198），粗粒度防最坏情况。Scaler 规模导向：TST（默认 3000 万，Scaler.java:53）约束全程序"上下文数 × 指向集"总量，二分找最大可承受 ST，精度当预算花。Mahjong 堆端：合并等价自动机减少对象数，输出类型单值约束（Mahjong.java:113-129）保证不引入类型混淆。

**为什么后处理而非 solver 内建**：三工具的输入全是 pta 结果的只读查询，输出恰好填 DefaultSolver 的两个注入参数，结构固定为"CI 预分析 → 工具计算 → 主分析"——代价是预分析求解时间，收益是 solver 与 plugin 生态零改动。Zipper 论文原型的可达性分析被简化掉，直接用 PCE 过滤伪流（PFGBuilder.java:216-221 注释明言是近似优化）。

**与 k-CFA 的关系**：Zipper 不发明新变体，`cs` 仍走 k-obj/k-type，只决定变体适用范围；Scaler 自带四档变体（GuidedSelector.java:51-53），是"每方法自调档"。

### 新人提示

开启：`-a pta=cs:2-obj,advanced:zipper`（或 `zipper-e`、`zipper-e=0.1`、`scaler`、`scaler=10000000`、`mahjong`、`collection`，tai-e-analyses.yml:19-22）。`advanced` 与 `cs` 独立：zipper 分支里 `cs` 决定开敏感方法用什么变体，scaler 分支忽略之。

调参：zipper-e 的 pv 越小越快（默认 0.05，Zipper.java:60），1 退化为完整 Zipper；scaler 的 TST 越小越快越粗（默认 3e7）；mahjong 无参数，瓶颈在同类型 O(n²) 等价判定（Mahjong.java:84-96），靠分组+并行缓解。各阶段耗时看日志（全包在 `Monitor.runAndCount` 里）。

验证：跑 `pta=advanced:mahjong` 加 `may-fail-cast` 对比失败 cast 数（MahjongTest.java:42-49 套路）；ZipperTest 可转储 OAG/OFG 的 dot（ZipperTest.java:53-60,74-80），配 `pta` 的 dump 选项对比指向集。两个坑：给 GuidedSelector 塞四变体之外的值直接 AnalysisException（GuidedSelector.java:92-93）；Scaler 只处理实例方法（Scaler.java:106-108），且 `java.util.*` 被强制最精确变体（202-206）——改前先掂量集合类对精度的杠杆。
