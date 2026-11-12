<!-- source: knowledge-graph 14 layers + 16 tour | generated 2026-10-12 -->

# Tai-e 新人上手指南（ONBOARDING）

> 与 DeepWiki 版（work4ai/讲透Tai-e/deepwiki/）互补：那边讲概念，本文讲代码落地。行号基于 master 实测；文件名全仓唯一，首次后文用短名。

## 一、一图看懂：Tai-e 是什么

Tai-e（太阿）是南京大学 pascal-lab 的 Java 17 静态分析框架，论文《Tai-e: A Developer-Friendly Static Analysis Framework for Java by Harnessing the Good Designs of Classics》见 ISSTA 2023（CITATION.bib）。设计上继承三大经典：Soot 的类模型与三地址中间表示传统（SootWorldBuilder 桥接前端加载 APK）；WALA 的指针流图与上下文敏感元素体系；Doop 的声明式配置——分析与污点规则全是 YAML，改规则不动内核。

数据主线：输入→前端→IR→{程序图→数据流/缺陷检查；指针分析→插件→污点}，IR 还可经后端回写字节码或直接解释执行。插件机制把 Java/Spring/Android 的动态语义静态化。

## 二、分层架构总览：14 层依赖树

图谱把全仓切成 14 层（自底向上，括号为图谱文件数）：

```text
L14 入口与工程 (33)    Main + Gradle/CI/文档
L13 测试套件 (150)     Tests 驱动 + DroidBench/ICC 基准
L12 Android 支撑 (61)  ApkInfo + lifecycle/icc/misc 插件
L11 缺陷检查 (30)      nullpointer/deadcode/异常
L10 污点与规则 (127)   TaintAnalysis + YAML 规则库
L9  pta 插件 (116)     reflection/lambda/spring/工具箱
L8  指针分析核心 (69)  DefaultSolver/PFG/堆模型/上下文
L7  程序图数据流 (67)  CFG/ICFG/调用图 + worklist 求解器
L6  分析基座 (20)      AnalysisManager + 分析注册表
L5  前端翻译 (93)      JavaWorldBuilder/SootWorldBuilder
L4  IR 后端 (21)       BytecodeEmitter + VM 解释器
L3  中间表示 (93)      stmt/exp + IRBuilder/IRPrinter
L2  语言类型 (80)      JClass/JMethod/ClassHierarchy/TypeSystem
L1  通用基础 (84)      util 集合/图算法/Monitor
```

度数枢纽（图谱实测，优先精读）：JMethod(235)、Var(178)、World(110)、Solver(77)。L1 的 util/graph/Graph 是 CFG、调用图、PFG 的共同父接口。

## 三、核心数据流：从 java -jar 到污点结果

fatJar（build.gradle.kts:118）设 Main-Class，第一站 src/main/java/pascal/taie/Main.java:51，四步：

1. 解析参数：Options.parse 处理 30+ 选项；--world-builder（Options.java:253）选前端。
2. 生成计划：processConfigs（Main.java:83）读 src/main/resources/tai-e-analyses.yml（22 个内置分析的注册表）；AnalysisPlanner 按 requires 条件建依赖图、拓扑排序出 Plan。
3. 构建世界：buildWorld（Main.java:132）反射实例化 WorldBuilder（自研或 Soot 桥接），装配 ClassHierarchy/TypeSystem 后调 World.set（World.java:91）。World 是全框架单例（度数 110），方法体 IR 由 JMethod.getIR 惰性翻译。
4. 执行计划：executePlan（Main.java:158）→ AnalysisManager.execute（AnalysisManager.java:88）反射创建（:116）后三分派（:134）：ProgramAnalysis 存结果进 World，Class/MethodAnalysis 并行流执行，再按依赖图清理无用结果。

污点链：给了 taint-config 时 setPlugin（PointerAnalysis.java:125）挂上 TaintAnalysis，onFinish 输出污点流，结果可经 process-result（tai-e-analyses.yml:140）dump/compare。

## 四、指针分析怎么转：DefaultSolver 主循环（全书心脏）

编排器是 PointerAnalysis.analyze（PointerAnalysis.java:75）：advanced 选项可先跑 CI 预分析交给 Scaler/Zipper/Mahjong 精化（:87-104），再 runAnalysis（:112）建求解器装配插件。

DefaultSolver（src/main/java/pascal/taie/analysis/pta/core/solver/DefaultSolver.java:99）的 solve()（:248）= initialize() + analyze()：initialize（:256）建调用图、PFG、WorkList，末尾 plugin.onStart()（:269）——入口方法由 EntryPointHandler 在此注册。analyze 主循环（:309-339）全书最关键：

1. 双层 while 取两种条目：PointerEntry（指针+新指向集）与 CallEdgeEntry（新调用边）；内层清空后触发 onPhaseFinish（:330），插件可借此再投喂 workList 重启分析（污点交互模式）。
2. propagate（:345）：应用对象过滤器后 addAllDiff 求差量，仅新增对象沿 PFG 出边经 Transfer 变换传给后继——差量传播是可扩展性来源。
3. 五个 process*：字段/数组 store/load（:371/:397/:423/:450，数组因协变需类型守卫）对每个新对象建边；processCall（:473）做 on-the-fly 调用图——对 receiver 指向的每个对象 resolveCallee 分派、选上下文、addCallEdge、对象传 this；解析不出交 onUnresolvedCall（:496，反射/lambda 接管点）。
4. processCallEdge（:502）：addCSMethod（新可达方法触发扫 IR）→ 参数传递（:518-525）→ 返回值传递（:540-547）→ onNewCallEdge。

StmtProcessor（:569）按语句建图：New（:609）取堆对象、选堆上下文后 addVarPointsTo；Copy（:695）LOCAL_ASSIGN；Cast（:719）带类型守卫的 CAST；静态字段读写与静态调用（:735/:751/:767）。插件钩子时序（Plugin.java:45，全为 default 方法）：

```text
setSolver → onStart → addCSMethod → onNewMethod → onNewStmt(逐条) → onNewCSMethod
  → [循环] onNewPointsToSet(diff) / onNewCallEdge / onUnresolvedCall
  → 内层清空 → onPhaseFinish → (可再循环) → onFinish
```

插件经 Solver 接口反向操作求解器（addPointsTo/addPFGEdge/addCallEdge 等，DefaultSolver.java:778-916）；removeEdgesIf 只许在 onPhaseFinish 调用。

## 五、扩展点地图：三类二次开发的触碰面

（1）新分析 pass：继承 ProgramAnalysis/ClassAnalysis/MethodAnalysis 之一，声明 public static final String ID，在 tai-e-analyses.yml 追加一条（第 39 行 cg 条目的 requires: [ pta(algorithm=pta) ] 展示条件依赖）；AnalysisManager.java:116 反射找 (AnalysisConfig) 构造器。之后 `java -jar tai-e.jar -a your-id` 即可。

（2）新 pta 插件（给 API 建模）：继承 AnalysisModelPlugin（AnalysisModelPlugin.java:52），方法标 @InvokeHandler(signature=..., argIndexes=...)（InvokeHandler.java:39），基类按签名自动分发事件；需合成 IR 用 IRModelPlugin。装配两通道：pta 的 plugins 选项（tai-e-analyses.yml:34，PointerAnalysis.java:169 反射实例化），或在 setPlugin 里按选项内置激活（PointerAnalysis.java:159-165）。

（3）新污点规则：一个 YAML——sources/sinks/transfers/sanitizers 四键，签名 `<Class: ret name(params)>`，污点位置 index: result/0/0[*]/0.f（范本 src/main/resources/commonly-used-taint-config/ 下 java-io.yml:1 与 command.yml:1），签名匹配由 SignatureMatcher 支持通配。启用：taint-config 选项指向文件或目录（tai-e-analyses.yml:29）；程序化规则实现 TaintConfigProvider（夹具 MockTaintConfigProvider.java）。

## 六、测试体系：Tests 驱动 + 参数化 + 移动基准

驱动是 Tests.java：testMain/testInput 组装命令行后直接调 Main.main（:140），自动挂 process-result 比对——GENERATE_EXPECTED_RESULTS（:61）开关两模式：true 生成期望文件，false 断言无 mismatch（:135-146）。参数化用自研 @MultiStringsSource：一组注解一组用例（首串主类名、其余选项），ContextSensitivityTest.java:41-46 覆盖全部上下文变体；testPTA（Tests.java:160）默认挂 AssertionChecker 断言插件。

Android 统一驱动 AndroidBenchTest.run（AndroidBenchTest.java:55）：DroidBenchTest（DroidBenchTest.java:31）按 13 类分测试类；ICCBenchTest 24 个 ICC 场景；UBCBenchTest 28 个微基准；RealWorldTest 跑 TaintBench 45 个真实恶意样本。聚合入口 TaieTestSuite.java（gradle test 默认排除，见 build.gradle.kts:165-180）。

## 七、工程设施：Gradle 约定插件 + 三条 CI 流水线

单主模块 + docs 子项目，Gradle Kotlin DSL。根 build.gradle.kts:1-6 只做三件事：apply buildSrc 三个 convention plugins（java/checkstyle/maven-publish）；声明依赖（picocli/log4j2/jackson-yaml/ASM）；引入 lib/ 两个本地修改版 jar（:23 soot、:41 flowdroid）。buildSrc 统一 Java 17 toolchain 与 JaCoCo；GitCommitValueSource.kt 直读 .git 取 commit hash。常用任务：fatJar（build.gradle.kts:118，产出 tai-e-all.jar）；test（:150-163）2G 堆、CPU/2 并行。CI 三条：test.yml 三 OS 矩阵（test.yml:8）跑 test jacocoTestReport 上传 Codecov；checkstyle.yml 每 PR 跑 checkstyle 并用 reviewdog 注到 PR；release.yml 手动触发签名发布 Maven Central。

## 八、上手路线：16 步 tour 的两周阅读路径

按"每周 8 步、每天 1-2 步、先跑再读"推进：

第一周（骨架）：
- D1-2｜tour1 入口与计划 + tour2 World：跑 `-a cfg`，往 yml 加假选项看报错。
- D3｜tour3 前端翻译 + tour4 类型与类层次：`-a ir-dumper` 导出方法 IR 对照源码。
- D4｜tour5 IR 模型 + tour6 后端：吃透 Var 的 def-use 与 Invoke 五类调用。
- D5｜tour7 图与数据流：对照教材读 ConstantPropagation 与 WorkListSolver.java:92 主循环。
- D6-7｜tour8 指针分析核心：精读 DefaultSolver 主循环与五个 process*，手画一次 PFG 传播。

第二周（血肉）：
- D8-9｜tour9 插件体系 + tour10 高级插件：照 AnalysisModelPlugin 写个最小 API 建模插件。
- D10｜tour11 精度工具箱："预分析指导上下文选择"。
- D11｜tour12 污点：读 TaintAnalysis.java:87 类注释工作流图，配小 YAML 跑通 source 到 sink。
- D12｜tour13 缺陷检查器：IsNullAnalysis 九格空值域是数据流应用范本。
- D13｜tour14 Android：ApkInfo→AndroidContext→三大子分析装配链。
- D14｜tour15 测试 + tour16 工程收尾；回 tour2 重读 World。

结业验收：ContextSensitivityTest 全绿；ir-dumper 读懂一个方法 IR；@InvokeHandler 插件挂进 pta；补一条 sink 规则命中污点流。
