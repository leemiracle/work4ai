<!-- source: knowledge-graph tour step 9 | files: src/main/java/pascal/taie/analysis/pta/plugin/Plugin.java, src/main/java/pascal/taie/analysis/pta/plugin/CompositePlugin.java -->
# 09 · 插件体系：Plugin 接口、CompositePlugin 分发与声明式建模范式

### 角色定位

图谱 L9 层"指针分析插件与工具箱"。两个主讲文件合计不到 300 行，但第 8 篇的 `DefaultSolver` 只做语言无关的 worklist 传播，reflection/lambda/invokedynamic/taint/Spring/Android 等"难点分析"全部住在 plugin 目录（Plugin.java:38-44）。装配集中在 `PointerAnalysis.setPlugin`（PointerAnalysis.java:125-173）：AnalysisTimer 首挂、ResultProcessor 收尾（129-136），余按选项插入（140-165）。实质是 **Solver 当服务柜台、Plugin 当订阅者**。

### 内部结构

**Plugin 十钩子**（全 default 空实现，Plugin.java:45-131，另设 `DUMMY`:47）。生命周期：`setSolver`:52、`onStart`:58、`onPhaseFinish`:68（排空后触发，可注入条目"重启"分析）、`onFinish`:76（禁改结果）。事件：`onNewPointsToSet`:85（**增量 diff** 非全量）、`onNewCallEdge`:93、`onNewMethod`:101（context 无关）、`onNewStmt`:110、`onNewCSMethod`:118（context 敏感）、`onUnresolvedCall`:130（callee 解析失败时接管，仅 reflection 与 LambdaAnalysis）。

**CompositePlugin 双通道分发**：低频生命周期钩子遍历 `allPlugins`（CompositePlugin.java:48）；六个高频事件各持独立列表，注册时反射探测真覆写（`getDeclaringClass() != Plugin.class`，82-86）才登记，而 `onNewPointsToSet` 每 diff 必发（121-123）——热路径优化。Composite 可嵌套（`NativeModeller` 把子模型创建推迟到 setSolver，NativeModeller.java:28-34；`TaintAnalysis` 亦然，TaintAnalysis.java:87）。**SolverHolder** 把 `hierarchy`/`csManager`/`heapModel` 等七件套解包为字段（util/SolverHolder.java:40-62）。

**声明式建模范式 = ModelPlugin 家族**：`ModelPlugin extends SolverHolder implements Plugin`（ModelPlugin.java:35），构造时反射扫可重复注解 `@InvokeHandler` 注册（InvokeHandler.java:46），`SignatureMatcher` 在 ClassHierarchy 匹配目标 API（AnalysisModelPlugin.java:67-69）。两分支：**AnalysisModelPlugin（事件式）** handler 形如 `void h(Context, Invoke, PointsToSet...)`，onNewStmt 把相关调用点登记进 `relevantVars`（102-114），onNewPointsToSet 只对登记变量触发（117-126），持 **delta 语义**——变化参数拿增量、其余取当前全量（154-168）；**IRModelPlugin（IR 生成式）** handler 返回 `Collection<Stmt>`，onStart 先 `addIgnoredMethod` 防双重建模（96-98），onNewCSMethod 逐 context 实例 `addStmts` 注入合成语句（128-133），onFinish 清理人造 Invoke 登记（137-148）。活样本 ArrayModel.java 对照两范式（66-67,104-105）；索引 BASE=-1/RESULT=-2（InvokeUtils.java:38）。

### 外部连接

**被 DefaultSolver 回调的九个锚点**：onStart（DefaultSolver.java:269）、onNewPointsToSet（324）、onPhaseFinish（330）、onFinish（338）、onUnresolvedCall（496）、onNewCallEdge（550）、onNewMethod/onNewStmt（564-565）、onNewCSMethod（880）。**反向通道**是 Solver 的 side-effect API（Solver.java:90-228）：注入 `addPointsTo`/`addVarPointsTo`（95-122，落点即 workList.addEntry）、`addPFGEdge`（135-179）、`addEntryPoint`/`addCallEdge`/`addCSMethod`/`addStmts`（185-207）、`addIgnoredMethod`（210-220）。**插件间协作走 solver 间接完成**——`addCSMethod` 级联触发其他插件的 onNewCSMethod/onNewStmt（ClassInitializer 引爆 `<clinit>` 即此理）。接线顺序：先填满 solver 字段再 setPlugin（PointerAnalysis.java:117-121），随后 `plugin.setSolver(solver); solver.setPlugin(plugin)` 互指（171-172）；用户插件经 `plugins` 选项反射注入、须 public 无参构造（tai-e-analyses.yml:34；PointerAnalysis.java:179-194）。

### 数据流

监控 `Arrays.copyOf` 调用点的最小插件，五拍：①**注册**——`plugins: [com.example.CopyOfMonitor]` 反射实例化并登记（CompositePlugin.java:68-72）。②**接线**——互指后 onStart 随 initialize 触发（DefaultSolver.java:269），EntryPointHandler.onStart 塞入 main 与 implicit entries（EntryPointHandler.java:44-58）。③**事件流**——main 入队 → addCSMethod（871）→ onNewMethod（564）/逐语句 onNewStmt（565）记录调用点；CSVar 非空 diff 过五条规则后回调 onNewPointsToSet（317-324），插件拿 receiver 增量，注入走 `addVarPointsTo`，条目重新入队。④**phase 循环**——排空后 onPhaseFinish（310-331），注入过条目则再开一轮；AnalysisTimer 即最简样本（AnalysisTimer.java:39-49）。⑤onFinish（338）后 ResultProcessor 做 dump。改用 AnalysisModelPlugin，③塌缩成一行注解——登记与 delta 分发全由基类代劳（AnalysisModelPlugin.java:102-126）。

### 设计决策

**钩子粒度**：onNewMethod/onNewCSMethod 分设——登记类工作只需一次、注入类工作须逐 context 实例；给 diff 是增量传播的自然延伸。

**难点为何全走插件**：其一内核极稳而语义建模随 JDK 漂移（javaVersion 分支即活证据，PointerAnalysis.java:140-150）；其二每能力一个开关；其三学术可实验性，taint/Spring 不必污染核心。对比同类：WALA 将语义分散于 ContextSelector/SSAContextInterpreter/ReflectionProvider 等抽象类接缝，Tai-e 收敛为单一事件接口；Doop 只能往 Datalog 追加规则、无过程性钩子——TaintAnalysis 在 onPhaseFinish 交互改配置重启（TaintAnalysis.java:195-218）在纯 Datalog 框架没有落点。

**两范式选择**：能用 IR 表达的选 IRModelPlugin——合成语句免费获得 cast 过滤、数组 load/store 规则；无法成句的（copyOf 按 functional 分叉）选 AnalysisModelPlugin。addIgnoredMethod 的精度动机（Solver.java:210-216）：接管建模就不该再跑方法体，否则别的调用点汇入虚假流。

### 新人提示

**三步写新插件**：①选基类——纯观察直接 `implements Plugin` 在 setSolver 存引用；API 建模选 AnalysisModelPlugin/IRModelPlugin；聚合多个模型 extends CompositePlugin 在 setSolver 装配（照抄 NativeModeller.java:30-34）。②声明 handler——签名用 Tai-e 语法 `<java.util.Arrays: java.lang.Object[] copyOf(...)>`，argIndexes 的 -1=receiver、-2=result；一个 API 至多一个 handler（AnalysisModelPlugin.java:70-75）。③注册——临时走 `plugins: [全类名]`，须有 public 无参构造（PointerAnalysis.java:186-189）；内置化则进 setPlugin 清单。

**调试**：Root 日志默认 info（log4j2.yml:11），改 trace 可见逐条 Propagate 事件（DefaultSolver.java:346）；ResultProcessor 支持 dump 与 expected-file 比对。

**常见误用**：①直接改 onNewPointsToSet 传入的 pts——那是增量集，污染 solver 内部；发新关系走 `addVarPointsTo`。②把 pts 当全量——取当前全量须 `solver.getPointsToSetOf`（AnalysisModelPlugin.java:163-165）。③onFinish 改结果（Plugin.java:72-74 明令禁止）。④自定义 AnalysisModelPlugin 忘了 onStart 调 addIgnoredMethod——基类不代劳（范本 ArrayModel.java:60-63），否则双重建模引入虚假流。⑤经 options 注入的插件在构造函数里用 solver——只能在 setSolver 后用。
