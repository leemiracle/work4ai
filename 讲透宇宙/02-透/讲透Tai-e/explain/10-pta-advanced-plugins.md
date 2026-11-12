<!-- source: knowledge-graph tour step 10 | files: src/main/java/pascal/taie/analysis/pta/plugin/invokedynamic/InvokeDynamicAnalysis.java, src/main/java/pascal/taie/analysis/pta/plugin/reflection/ReflectionAnalysis.java -->

# 10 · invokedynamic 与反射：两大语言特性攻坚插件

## 一、角色定位

指针分析的不确定性里，invokedynamic 与 reflection 最硬：前者 callee 藏在 bootstrap method（BSM）的运行期返回值里，后者藏在字符串与 Class 元对象里。Tai-e 把它们做成两个插件家族，是与 DefaultSolver 交互最深的 L9 特性建模插件。启用条件不同（`PointerAnalysis.java:145-157`）：LambdaAnalysis 在 Java 8+ 默认开启；InvokeDynamicAnalysis 需 `handle-invokedynamic: true`（默认 false）且 JRE 可解析 MethodHandle 类；ReflectionAnalysis 仅当 `reflection-inference`（string-constant|solar）或 `reflection-log` 任一非空时加入。勘误：`LambdaAnalysisPlugin` 不存在于当前代码库，`LambdaAnalysis` 直接 `implements Plugin`（`LambdaAnalysis.java:61`）。

## 二、内部结构

### invokedynamic：三插件按 BSM 分工

`getInvokeDynamic` 把 lambda 与字符串拼接两类 indy 排除给专门插件（`InvokeDynamicAnalysis.java:206-217`）：BSM 为 `LambdaMetafactory` 归 LambdaAnalysis、`StringConcatFactory` 归 Java9StringConcatHandler，其余归 InvokeDynamicAnalysis。

**LambdaAnalysis = 一个 mock 对象 + 一个回调**。每条 lambda indy 记为 `LambdaObj` mock；方法上下文到达时以**创建方法的完整调用上下文为堆上下文**灌给结果变量，捕获值的上下文敏感性免费获得（`LambdaAnalysis.java:135-148`）。目标直接取 `bootstrapArgs.get(1)` 的 MethodHandle（`LambdaAnalysis.java:223-225`）——JVM 规范固定参数，绕开 LambdaMetafactory 方法体分析。

**InvokeDynamicAnalysis 真去"执行"BSM**：为每个 indy 建空上下文 BSMCallEdge 并按 JVM 约定传参（Lookup/方法名/MethodType/静态实参），再从 BSM 方法体扫出 `new *CallSite(target)`/`setTarget` 首参变量登记为 MethodHandle 候选（`InvokeDynamicAnalysis.java:229-250`，注释自认 unsound：理想应关联 `CallSite.target` 字段，但回调只支持变量级）；候选收到 MethodHandle 后按 Kind 建边，invokeVirtual 走 dispatch、invokeStatic 直接 resolve、其余抛异常。

**MethodHandle 是 `ReferenceLiteral` 实现类**（`MethodHandle.java:44`）——编译期常量池对象，可作堆对象流动；Kind 9 种映射 `MethodHandleInfo.REF_*`，invoke 类 5 种（含构造器实例化）与 field 类 4 种，目前只消费前者。

### 反射：组合插件 + 五个 model

`ReflectionAnalysis extends CompositePlugin`，组装 LogBasedModel + 推断模型三选一（string-constant→StringBasedModel、solar→SolarModel、null→匿名 dummy）+ ReflectiveActionModel + OthersModel + AnnotationModel（`ReflectionAnalysis.java:68-99`）。

**InferenceModel 是抽象基类**，提供名称与 Class 对象双已知时的 forName/getConstructor/getMethod 模板方法（`InferenceModel.java:66-126`）。子类差别在未知信息策略：StringBasedModel 纯常量驱动——`@InvokeHandler` 把字符串常量与 Class 常量对象笛卡尔积交给基类，任一未知即跳过，宁漏报不误报；SolarModel（TOSEM 2019）为"未知"发明专门元对象（按 class/name 已知与否分四象限）再收敛：调用点类型过滤候选（collective inference）、cast 类型的非抽象子类回灌 Class 对象（lazy heap modeling，`SolarModel.java:277-300`），收不回的进 unsoundInvokes 汇报。

LogBasedModel 是"日志优先"锚点：按 caller 类/方法名+API+行号在 IR 匹配调用点（`LogBasedModel.java:172-208`），其 `invokesWithLog` 集合注入其他模型——有日志的调用点推断模型直接 return、ActionModel 只接受日志专属元对象（`ReflectiveActionModel.java:340-342`）。ActionModel 消费上层元对象建边（Field.get/set 不建调用边而直接挂 LOAD/STORE PFG 边，`ReflectiveActionModel.java:188-250`）。

## 三、外部连接

挂接 Solver 的三种姿势：① **InvokeHandler 注解**（反射家族）——`AnalysisModelPlugin` 构造时反射扫描注解登记 handler（`AnalysisModelPlugin.java:72-108`）；② **onUnresolvedCall 回调**（LambdaAnalysis 专用）——函数式接口方法 dispatch 失败时 `DefaultSolver.processCall` 回调插件（`DefaultSolver.java:496`）；③ **OTHER 类调用边**（共用）——三家的边均继承 OtherEdge，且 `DefaultSolver.processCallEdge` 对 OTHER 边**跳过默认参数传递**（`DefaultSolver.java:508-510`），传参交还插件 onNewCallEdge 手写缝合（ReflectiveCallEdge 携带 args 数组解包）。

合成边经 `addCallEdge` 回流触发新 CSMethod 可达、再触发全插件 onNewCSMethod——反射元对象正是在这条循环里灌入。

## 四、数据流

### `list.forEach(x -> use(x))`

javac 编译为 indy（bootstrap 参数含指向合成方法 `lambda$main$0` 的 `MethodHandle(REF_invokeStatic)`）；`onNewStmt` 匹配 BSM 签名建 LambdaObj 并在方法上下文到达时灌给结果变量；LambdaObj 流入 `ArrayList.forEach` 内部的 `consumer.accept(e)`，dispatch 失败触发 onUnresolvedCall；方法名过滤剔除混入的无关 LambdaObj（`LambdaAnalysis.java:158-163`）后建 LambdaCallEdge，实参 `e` 经带类型 filter 的 PFG 边流向形参 `x`。若是 `this::use`，首 capture 即 receiver，逐对象 dispatch 并登记 InstanceInvoInfo 供后续补边。

### `Class.forName(name).getMethod("run").invoke(obj, args)`

forName：handler 收到 name 变量的 points-to set，字符串常量 → `initializeClass` + ClassLiteral 常量对象灌给 result（`InferenceModel.java:72-85`）；非常量则 StringBasedModel 漏报、SolarModel 出 unknown class 续传。getMethod：双已知时展开全部同名方法灌 mock。invoke：static 直接建边，实例目标对 receiver 逐对象 dispatch 并用 typeMatcher 过滤，args 数组元素灌给被调参数。日志覆盖的调用点则拒绝推断元对象。

## 五、设计决策

**反射拆多 model 而非一锤子**：可知性分层——日志 > 字符串常量 > 部分信息（四象限）> 完全未知，每层可插拔、避让协议协调、可混用。对比 Doop：反射需在规则变体间整体切换；Tai-e 的推断发生在求解循环内——unknown 元对象流入 cast 后回灌 Class 对象，把反射解析做成指针分析**不动点迭代的参与者**，规则式方案模拟该反馈需多轮求值。

**lambda 走 mock+回调、通用 indy 走 BSM 执行**是精确度与通用性的换算：lambda 的 BSM 行为被 JVM 规范固定，mock 方案零开销拿精确 callee；通用 BSM 是任意用户代码只能真建边去跑，且仅追踪 CallSite 构造/setTarget 首参窗口，field 类 Kind 与 varargs 均为 TODO。

**OTHER 边下放参数传递**换来对非对齐参数表（lambda 双段参数、反射 Object[] 解包）的控制权，代价是三插件各维护一套 shift 逻辑——全家族最易出 off-by-one 之处。

## 六、新人提示

**开启选项**：lambda 零配置；自定义 indy 需 `handle-invokedynamic: true`；反射三档 `reflection-log: <path>`（精确）/ `string-constant`（保守）/ `solar`（激进），可同开且日志优先。

**常见漏报**按频率：① 目标名运行期拼接——只有 cast 或调用点类型能救（Solar 的 unsound 日志兜底）；② `handle-invokedynamic` 忘开或 JRE 缺 MethodHandle 类；③ 自定义 BSM 用 field 类 Kind 或 MethodHandle 经字段转手（追踪断链）；④ Android 模式 target 超 5 不建边且只看应用代码调用点（刻意控误报非 bug）；⑤ 上下文不敏感时 LambdaObj 跨调用点共享。

**验证合成边**：跑 pta 后 dump call graph，三种合成边按 `OTHER.类简单名` 格式区分；`reportImpreciseCalls` 把 target 数 ≥50 的调用点降序列出（`ReflectionAnalysis.java:124-146`），Method.invoke 挂几百个 target 即失守信号；points-to set 搜 `ReflectiveObj` Descriptor 可确认灌入。
