<!-- source: knowledge-graph tour step 1 | files: Main.java, AnalysisManager.java, AnalysisPlanner.java (pascal.taie / analysis / config 包) -->

# Tai-e 精讲 01：入口与配置驱动——从 Main 到分析执行

### 1. 角色定位

本篇三主角横跨图谱两层：Main.java 属 L14「应用入口与工程设施」，AnalysisManager.java 与 AnalysisPlanner.java 属 L6「分析基座与全局配置」。它们是 Tai-e 的"装配线"：不做任何具体分析，只把命令行参数、YAML 声明、分析类装配成可执行 `Plan` 并跑完——60+ 个分析全部声明在 tai-e-analyses.yml，入口零硬编码，`Main.main()` 实质只有 6 行调用（Main.java:51-68）。

### 2. 内部结构

**Main** 的核心是 `processConfigs()`（Main.java:83），内部分三岔：`-a` 指定分析、`-p/--plan-file` 指定计划文件、皆空则 `Plan.emptyPlan()`；executePlan（Main.java:158）仅一行 `new AnalysisManager(plan).execute()`。

**AnalysisConfig**（AnalysisConfig.java:41）是单分析配置模型（description/analysisClass/id/requires/options）。analysisClass 刻意用 String 而非 Class（AnalysisConfig.java:56）：启动要加载全部配置，用 Class 会强制加载所有分析类，拖慢启动。

**ConfigManager**（ConfigManager.java:40）是 id→config 注册表；`overwriteOptions()`（ConfigManager.java:82）把命令行/计划文件选项合并进全局配置；`getRequiredConfigs()`（ConfigManager.java:95）解析条件依赖并 memoize。

**AnalysisPlanner**（AnalysisPlanner.java:45）双入口：`makePlan()`（AnalysisPlanner.java:67）供计划文件，严格校验顺序；`expandPlan()`（AnalysisPlanner.java:151）供命令行，自动补依赖并拓扑排序。`buildDependenceGraph()`（AnalysisPlanner.java:221）用 worklist 沿 requires 收集依赖闭包，再用 Tarjan SCC 检环（AnalysisPlanner.java:257），相互依赖判非法。产物 **Plan**（Plan.java:39）是 record：analyses 有序列表 + dependenceGraph（供结果清理）+ keepResult 保留集（哨兵 `KEEP_ALL`）。

**AnalysisManager**（AnalysisManager.java:51）逐项执行：`runAnalysis()` 反射创建实例（AnalysisManager.java:116-118），按 `instanceof` 分派三路径（AnalysisManager.java:134-143）——ProgramAnalysis 全程序、ClassAnalysis 逐类并行、MethodAnalysis 逐方法 IR 并行。

### 3. 外部连接

上游：Gradle `application` 插件设 `mainClass = pascal.taie.Main`（build.gradle.kts:60）。测试是第二入口：`Main.buildWorld(String...)` 为公开 API（Main.java:125），IRTest.java:40 直接用它建 world。横向：Main 依赖 config 包全部 9 个类、CachedWorldBuilder 与 Monitor（Main.java:28-41）。下游：分析结果经 storeResult 存进 World（继承 AbstractResultHolder，World.java:49）。

### 4. 数据流：`java -jar tai-e-all.jar -cp app.jar -m Main -a pta` 全链

1. **参数解析**：main()（Main.java:51）整体包 `Monitor.runAndCount` 采样耗时与内存。`Options.parse()`（Options.java:392）picocli 解析 30+ 选项；`postProcess()`（Options.java:405）做 JRE 解析、`-a`/`-p` 互斥检查（Options.java:431）、写盘 options.yml 到 output 目录（Options.java:471）。
2. **配置装载与选项合并**：processConfigs（Main.java:83）从 classpath 读 tai-e-analyses.yml（Configs.java:51），Jackson YAML 反序列化（AnalysisConfig.java:186）后装入 ConfigManager；`-a pta=cs:2-call` 的 `k:v;k:v` 值转 YAML 后解析（Options.java:754），经 overwriteOptions 合并。
3. **计划生成**：`expandPlan()`（AnalysisPlanner.java:151）映射 PlanConfig→AnalysisConfig，REACHABLE 缺 cg 自动补（AnalysisPlanner.java:160）；建依赖图→SCC 验证→拓扑排序→REACHABLE 时 shiftCG 前移 cg（AnalysisPlanner.java:165）；Plan 写盘 output/tai-e-plan.yml（Main.java:107）。
4. **世界构建**：buildWorld（Main.java:132）反射创建 `options.getWorldBuilderClass()`（默认 JavaWorldBuilder，Options.java:85；Android 模式强制 Soot 前端，Options.java:444）；builder 内部调 `World.set()`（World.java:91）挂全局单例。
5. **执行**：`AnalysisManager.execute()`（AnalysisManager.java:88）遍历计划，每个分析单独包 Monitor。pta 即 `PointerAnalysis`，是 ProgramAnalysis（PointerAnalysis.java:66），结果 storeResult 进 World（AnalysisManager.java:150）。
6. **结果消费闭环**：若计划还有 cg（requires `pta(algorithm=pta)`，tai-e-analyses.yml:42），它排在 pta 后，PTABasedBuilder 经 `World.get().getResult(PointerAnalysis.ID)` 取回结果建调用图（PTABasedBuilder.java:41）——依赖图保证时序。

### 5. 设计决策

**一、配置即数据，反射即解耦。** 60+ 分析全在 YAML 声明，新增分析=写 Analysis 类+yml 加条目，入口零改动。代价是反射实例化的 4 类异常（AnalysisManager.java:119-132）；约束：分析类必须声明 `public static ID` 且与配置 id 一致（Analysis.java:58）。

**二、两条计划路径语义不同。** CLI 走 expandPlan：自动补依赖+拓扑排序；计划文件走 makePlan（Main.java:116）：顺序即权威，validateAnalyses 用 indexOf 检查被依赖者在前（AnalysisPlanner.java:104）。CLI 每次把展开后的计划写盘（Main.java:107），结果可用 plan file 复现。

**三、条件依赖。** requires 支持 `pta(algorithm=pta)`：依赖成立与否取决于选项值。extractConditions/satisfyConditions（Configs.java:87/101）支持 `a=b&c=d|e` 组合；getRequiredConfigs 必须在 overwriteOptions 之后调用（ConfigManager.java:88-93 的 NOTE 钉死）并 memoize，防二次解析不一致。

**四、结果生命周期。** 默认 `-kr $KEEP-ALL`（Options.java:359）；指定保留集后 clearUnusedResults（AnalysisManager.java:226）跑完后摘除其依赖边、清"出度为 0 且不在保留集"的结果（AnalysisManager.java:234-238）——指针分析结果动辄数 GB，这是内存纪律。

**五、REACHABLE 前置保证。** scope=REACHABLE 时作用域来自调用图（AnalysisManager.java:177），故 cg 必须最早跑：plan file 路径只校验不修改（AnalysisPlanner.java:113-135），CLI 路径主动 shiftCG 重排（AnalysisPlanner.java:176）。动因：config 包反向 import 了 CallGraphBuilder（AnalysisPlanner.java:25 取 `"cg"` 常量，CallGraphBuilder.java:39），是 config→analysis 方向罕见的分层破例，图谱中二者的连边即由此产生。

**六、可复现性内建。** 每次运行落盘 options.yml 与 tai-e-plan.yml，即实际生效配置的真相源；`--output-dir` 支持 `$AUTO-GEN` 时间戳占位符（Options.java:612）。

### 6. 新人提示

**上手顺序**：Options → tai-e-analyses.yml → AnalysisConfig/ConfigManager → AnalysisPlanner → AnalysisManager → Main。

**易错点**：① `-a` 与 `-p` 互斥（Options.java:431）。② `-a` 选项键必须在 yml 已存在（AnalysisOptions.java:83 白名单校验）。③ 自写分析：构造器必须 public 且唯一参数为 AnalysisConfig（AnalysisManager.java:117），`ID` 缺失或不匹配在构造时炸（Analysis.java:64）。④ REACHABLE 忘带 cg：CLI 自动补、plan file 报错。⑤ World 是全局单例，reset 前不能建第二个（World.java:98）。

**调试入口**：优先用 `Main.buildWorld(...)`（Main.java:125）建最小 world 再手动跑分析；每个分析前后的 Monitor 日志（AnalysisManager.java:103）自带耗时与内存，是定位慢分析的第一现场；对比 output/tai-e-plan.yml 可确认依赖补全与重排。
