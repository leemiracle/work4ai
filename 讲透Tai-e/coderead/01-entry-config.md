<!-- coderead unit 01 | files: 24 个 | 全量深读 2026-10-13 -->

# coderead 01：入口·World·分析管理（逐类参考手册）

与 explain 01 互补：那边讲数据流故事，本篇是逐类参考手册，行号对 2026-10-13 master 实测。

## 1. 包职责与架构位置

横跨 14 层图谱两层：`Main.java` 属 L14「应用入口与工程设施」；`World`/`WorldBuilder` 族、`analysis` 顶层接口族与 `config` 包属 L6「分析基座与全局配置」。承诺三事：装配 Plan、持有全局 World（单例）、反射执行分析与结果管理。消费方：60+ 分析全继承三基类，经 `World.get()` 读程序。分层破例一处：`AnalysisPlanner.java:25` 反向 import `CallGraphBuilder.ID`（config→analysis），为 REACHABLE scope 强制调用图先行。

## 2. 逐类深读

#### Main Main.java:47

CLI 入口。`main`（Main.java:51）全流程包 Monitor.runAndCount。`processConfigs`（:83）三岔：`-a` 走 expandPlan 并写盘计划供 `-p` 复现（:99-107）；`-p` 走 makePlan（:116）；皆空 emptyPlan。Android 先 android yml 覆盖、命令行在后故优先级最高（:90-94）。公开 `buildWorld(String...)`（:125）是测试建 world 主通道；私有版（:132）反射实例化 builderClass，`-wc` 外包 CachedWorldBuilder（:139）。`executePlan`（:158）委托 AnalysisManager。

#### World World.java:49

`final`，extends AbstractResultHolder（结果仓库）。静态 theWorld（:55）+resetCallbacks（:61）。七槽：options（:67，transient）/typeSystem/classHierarchy（:69/:71）/irBuilder（:80，transient）/nativeModel/mainMethod/implicitEntries（:82-86）。set/get/reset（:91/:98/:106；reset 先跑回调）。存取器全经 `checkAndSet`（:171）：反射按名取字段，已非 null 抛异常——**每槽至多写一次**。writeObject/readObject（:185/:191）序列化时换 CachedIRBuilder。不变量：setter 只归 WorldBuilder 调一次（:46-47）；get() build 前为 null。

#### WorldBuilder WorldBuilder.java:30

函数式接口，单方法 `build(Options)`（:38）：构建新 World 经 `World.set()` 挂全局，完成后 `World.get()` 必可用。

#### AbstractWorldBuilder AbstractWorldBuilder.java:48

builder 族共用工具基类。`JREs`（:52）/`ANDROID_PLATFORMs`（:54）为相对工作目录硬编码路径，换目录撞 :82-88 submodule 提示。implicitEntries（:56-70）硬编码 13 个 JVM 隐式入口签名。getClassPath（:72）：useCurrentJRE 直拼两 class path，否则 Files.walk 收 `jre1.{version}` 下 .jar 拼最前（:89-96）。getAndroidJDKPath（:108）同款只返 JRE jar；getNativeModel（:147）按开关选 Default/Empty；getInputClasses（:157）合并 `--input-classes`（.txt 逐行读 :163-168）与 -acp 的 ClassNameExtractor（:176）。

#### Analysis Analysis.java:35

分析抽象基类。字段 `config`（:40，final），构造时即调 `validateId`（:61）：反射取子类 `public static` 字段 `ID`，与配置 id 不符抛 ConfigException（:67）、缺失抛 AnalysisException（:72）。不变量：**每分析类必须有 `public static final String ID` 且与 yml id 一致**，构造期校验。

#### AnalysisManager AnalysisManager.java:51

按 Plan 创建执行分析、管理结果生命周期。字段 plan/keepAllResults/dependenceGraph/scope 懒缓存（:55/:61/:68/:76-78）。`execute()`（:88）逐 config 包 Monitor 执行（:103），非 keepAll 时每个完成后 clearUnusedResults（:107）。`runAnalysis`（:112）反射创建实例（:116-118，异常翻译 :119-132）再 instanceof 三分派（:134-139）：ProgramAnalysis 存 World（:147）、ClassAnalysis **parallelStream** 逐类存 JClass（:154）、MethodAnalysis 逐 IR 存 IR（:190）。getClassScope（:164）：APP/ALL→对应类集、REACHABLE→调用图按 declaringClass 去重（:177-181）；getMethodScope（:202）APP/ALL 展开非 abstract 方法（:210）。clearUnusedResults（:226）清"出度 0 且不在 keepResult"者（:234-252）。易错：analyze 须线程安全（并行）；scope 缓存后同 run 不变。

#### ClassAnalysis ClassAnalysis.java:33

类内分析基类。抽象 `analyze(JClass)`（:47）：结果存该 JClass，无人消费应返回 null。

#### MethodAnalysis MethodAnalysis.java:33

过程内分析基类。抽象 `analyze(IR)`（:49）：结果存该 IR，同样建议无人消费返回 null。

#### ProgramAnalysis ProgramAnalysis.java:32

全程序分析基类。抽象 `analyze()`（:46）：结果存 World；pta/cg 等重器属此类。

#### StmtResult StmtResult.java:32

逐语句结果查询接口：`isRelevant(Stmt)`（:37）+`getResult(Stmt)`（:42）。实现它即可被 ResultProcessor 逐 stmt dump/compare（ResultProcessor.java:255）。

#### IRDumper IRDumper.java:55

`ClassAnalysis<Void>`，ID="ir-dumper"（:57）。输出 `tir/`（:61）下每类一个 `.tir`；analyze（:82）恒 null。内部类 Dumper（:87）：dumpClassDeclaration（:118，interface 压 INTERFACE/ABSTRACT :126-127）；dumpMethod（:168，有 IR 才打 body+异常表 :184-188，参数名优先显式名 :208-213）；dumpVariables（:223，按类型分组排除 this/参数）。

#### ResultProcessor ResultProcessor.java:66

`ProgramAnalysis<Set<String>>`，ID="process-result"（:68），注释（:64）钉死测试用、**须排计划最后**。`analyze`（:89）：dump→setOutput（:121，缺省 stdout）；compare→readInputs（:134，extractKey :156 解析分节头）；`analyses` 选项按 `World.get()::hasResult` 二分（:102）出 Program 与 Class/Method 组（:201-203），程序组走 cg reachableMethods（:179/:184）。processResults（:221）分派 dump/compare 并查期望键全被处理（:236-241）。均三形态：Collection（排序 :272/差集 :313-324）、StmtResult 逐 stmt（:258/:329-350）、单值（:352-356）；Stmt 走 IRPrinter（:286）。

#### AnalysisConfig AnalysisConfig.java:41

yml 单条目模型。字段：description（:50，纯注释）、analysisClass（:63，**String 而非 Class** 防启动强加载 :53-60）、id（:73，全局唯一）、requires（:94，条件语法 `A(x=y)`/`A(x=y&a=b)`/`A(x=a|b|c)`）、options（:100）。静态工厂 `of(id, Object...)`（:125）：`[k1,v1,k2,v2]` 转 options。getRequires（:160）**包私有**且返回原始串——真实依赖走 ConfigManager.getRequiredConfigs（:155-158 注释）。`parseConfigs`（:186）YAML 反序列化，失败抛 ConfigException（:193）。

#### AnalysisOptions AnalysisOptions.java:42

选项 Map 包装（:50）。核心是包私有 `update`（AnalysisOptions.java:74）：**白名单校验**——传入 key 必须已存在否则 IllegalArgumentException（:76-81）再 putAll——"命令行 `-a` 的键必须先在 yml 声明"的机制根源。访问器 has/get（:89/:97，缺 key 抛 ConfigException）、getString/getBoolean/getInt/getFloat（:105-117，直接强转）。

#### AnalysisPlanner AnalysisPlanner.java:45

计划生成器，双入口。`makePlan`（:67，plan file 路径，**顺序即权威**）：covertConfigs（:79）→validateAnalyses（:92，依赖须在前 :98-111；reachable 须含 cg 且 cg 前只放其依赖 :113-135）→建图→验图→Plan。`expandPlan`（:151，CLI 路径）：reachable 缺 cg 自动补（:160）→TopologicalSorter 拓扑排序（:165）→shiftCG（:176）把 cg 前移到其依赖之后（:190-208）。buildDependenceGraph（:221）worklist 收 requires 传递闭包；validateDependenceGraph（:244）自包含检查+SCC 查环（:257-261，相互依赖非法）。

#### ConfigException ConfigException.java:28

config 统一异常（RuntimeException 子类），两构造器（:30/:34）；Analysis ID 校验失败复用（Analysis.java:67）。

#### ConfigManager ConfigManager.java:40

AnalysisConfig 注册表+依赖解析器。configs（:45，id→config 的 LinkedHashMap）、requires（:50，memoize）。addConfig（:56）id 重复抛异常；getConfig（:70，包私有）查无抛（:73-74）。`overwriteOptions`（:82）把 PlanConfig 选项 update 进全局配置——命令行/plan file 覆盖 yml 默认值的落点。`getRequiredConfigs`（:95）computeIfAbsent memo：条件过滤（:100-101）+extractId 查表（:103）；**必须在 overwriteOptions 后调用**（:91-93，否则条件解析错且 memo 固化）。

#### Configs Configs.java:32

静态工具类（私有构造器 :34）。CONFIG（:41）=`tai-e-analyses.yml`（classpath，:39 硬编码）、ANDROID_CONFIG（:46）；getAnalysisConfig 及 android/URL 版（:51/:60/:69）。require 解析：extractId（:78）、extractConditions（:87）、`satisfyConditions`（:101）支持 `a=b`/`a=b&c=d`（:104）/`a=b|c|d`（:108-116），取值 `Objects.toString(options.get(key))`（:112）。

#### LoggerConfigs LoggerConfigs.java:42

log4j2 运行时配置（CHECKSTYLE:OFF :26）。`setOutput`（:78）：new FileAppender 复用 STDOUT layout（:82-88）挂 root logger（:92-93），日志双写控制台+文件。`reconfigure()`（:64）重载 log4j2.yml 撤销动态修改，Main 收尾与 buildWorld 各调一次（Main.java:66/:129）。

#### Options Options.java:77

picocli `@Command`（:73）+Jackson `@JsonProperty` 双注解——同字段吃命令行与 options.yml。关键项：`-cp`（:118，:688 按系统分隔符拆）、`-java`（:162）、useCurrentJRE（:185，**boxed Boolean 三态** :178-183）、`--world-builder`（:253，默认 JavaWorldBuilder :85）、`--output-dir`（:265，支持 `$AUTO-GEN` 时间戳 :612）、`-kr`（:355，默认 $KEEP-ALL）。`parse`（Options.java:392）注册 AnalysisOptionsConverter（:732/:754，k:v 串转 YAML）后 `postProcess`（:405）七步：① optionsFile 存在则**整体改读文件**（:408-412）；② resolveJREOptions（:478）四分支：`-pp` 强制当前 JRE（:481-494）、useCurrentJRE 显式（:495-503）、`-java`（:504-508）、默认当前 JRE（:509-520）；③ `-wc` 联动 preBuildIR（:428-430）；④ `-a`/`-p` 互斥（:431-436）；⑤ Android 强制 SootWorldBuilder、APK 推 javaVersion（:444/:448），Java 模式至少一项输入（:450-457）；⑥ reflection-log 补输入类（:460-463→:776）；⑦ mkdir+writeOptions 落盘 output/options.yml（:471→:593）。

#### Plan Plan.java:39

record `(analyses, dependenceGraph, keepResult)`：analyses **有序**即执行序；dependenceGraph 供结果清理；keepResult 保留集。哨兵 `KEEP_ALL="$KEEP-ALL"`（:48）；EMPTY 单例/emptyPlan()（:50/:55）。

#### PlanConfig PlanConfig.java:47

"要跑什么"轻配置（对照 AnalysisConfig 的"它是什么"，:42-45）：仅 id（:57）+options（:63）。readConfigs(File)（:93）读 plan 文件；readConfigs(Options)（:107）把 `-a` Map 转列表；writeConfigs（:121）写 `output/tai-e-plan.yml`（:51）。

#### Scope Scope.java:25

三值枚举：APP（:30）、REACHABLE（:36，**要求 cg 先行**）、ALL（:41）。被 `-scope`（Options.java:302）写入、被 AnalysisManager 两 scope 方法消费。

#### package-info（package-info.java:26）

一句话包文档：config 包提供 options 与 configurations 处理能力。

## 3. 修改热点（二次开发）

**加新 CLI 选项**：Options.java 三处——字段加 `@JsonProperty`+`@Option`（照抄 :289-295 样例）、补 getter、toString（:803）加项；联动写 postProcess（:405）仿 :431-436。

**加新分析注册（最常见二开）**：① 分析类三基类选一+`public static final String ID`+public 单参 AnalysisConfig 构造器（AnalysisManager.java:117 反射查找；ID 不符构造期炸，Analysis.java:64）；② `src/main/resources/tai-e-analyses.yml` 加条目——**全部选项键及默认值必须先在 options 声明**，否则命令行传该键被白名单拒（AnalysisOptions.java:76-81）；③ 零 Java 改动（Configs.java:51 自动装载）；④ 依赖用 `requires: [A]` 或 `[A(x=y)]`（Configs.java:78-123）。

**Android 覆盖**：`android/tai-e-android-analyses.yml` 只放 id+options，由 Main.java:90-94 overwriteOptions；命令行其后合并故优先级最高。

**改 World 单例**：扩字段加存取对（自动获 checkAndSet 一次性语义，按字段名反射拼错运行时落 :180 异常）；静态缓存类 registerResetCallback（:102）防跨 run 泄漏。

**换前端**：零改码 `--world-builder your.Builder`（Options.java:253），实现 WorldBuilder.build（:38）；改默认动 Options.java:85。

## 4. 集成触点

**稳定契约**：`Main.buildWorld(String...)`（Main.java:125）建 world 官方通道；`Options.parse`（Options.java:392）；`World.get()` 七 getter（World.java:111-165）+getResult/storeResult 等；三基类+`AnalysisConfig.of`（AnalysisConfig.java:125）程序化构造；`new AnalysisManager(plan).execute()`（AnalysisManager.java:80/:88）；`PlanConfig.readConfigs(File)`（:93）回读计划。

**半稳定**：Configs 资源定位（Configs.java:51-73）；LoggerConfigs.setOutput/reconfigure（LoggerConfigs.java:78/:64）仅自管进程用；IRDumper/ResultProcessor 是"分析"非 API，经 yml 选项（id ir-dumper/process-result）使用。

**内部（勿依赖）**：ConfigManager.getConfig/getRequiredConfigs、AnalysisOptions.update、AnalysisConfig.getRequires 均**包私有**（ConfigManager.java:70/:95、AnalysisOptions.java:74、AnalysisConfig.java:160），跨包编译不过——有意的封装边界；World.theWorld 只能经 set/reset（World.java:91/:106）。

**集成三铁律**：① 二次 build 前必须 `World.reset()`（清 result 仓库）；② getRequiredConfigs 须在 overwriteOptions 后（ConfigManager.java:91-93），自拼 Plan 先合并选项再解析依赖；③ REACHABLE 计划须含 cg 且先行（AnalysisPlanner.java:113-135/:160），否则 scope 解析在 AnalysisManager.java:177 取不到调用图。
