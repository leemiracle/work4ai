<!-- source: knowledge-graph tour step 2 | files: src/main/java/pascal/taie/World.java, src/main/java/pascal/taie/language/classes/JClass.java, src/main/java/pascal/taie/AbstractWorldBuilder.java -->

# 02 World 与类层次：单例门面 + 构建流水线 + JClass 类模型

主线：Main.buildWorld 反射实例化 WorldBuilder（接口仅 `void build(Options)`，WorldBuilder.java:38），默认 JavaWorldBuilder（Options.java:86）把字节码装进 World 单例，JClass/JMethod/JField 是被装内容。

### 角色定位：程序抽象的中枢

Tai-e 把被分析程序的全部静态事实收敛进一个 196 行的 final 类 World（World.java:49）：前端（字节码→对象模型）与分析世界唯一的交接界面。知识图谱中它横跨 L5「前端翻译与程序装载」与 L2「语言与类型系统」两层。彩蛋：单例字段的源码注释是 `ZA WARUDO, i.e., the current world`（World.java:53）——全程序只此一个 World。三角分工：**World**＝全局状态容器兼结果挂载点，**WorldBuilder**＝生产者，**JClass 类模型**＝被生产的数据。

### 内部结构：门面、流水线、类模型

**World 门面。** 实例字段仅七个：options/typeSystem/classHierarchy/irBuilder/nativeModel/mainMethod/implicitEntries（World.java:67-86）。其一，**一次性写语义**：setter 全走 checkAndSet（World.java:171-182），字段已非 null 即抛 IllegalStateException；类头注释明言 setter 只由 world builder 各调一次（World.java:44-48）。其二，**reset 非置空**：先跑 resetCallbacks 再置 null（World.java:106-109）。World 还继承 AbstractResultHolder，getResult 走 computeIfAbsent 惰性缓存，兼作分析结果第一级挂载点。

**WorldBuilder 流水线。** Main.buildWorld（Main.java:132-156）是唯一正规入口：反射实例化 builder，开 `--world-cache` 则外包 CachedWorldBuilder，再 build(options)。AbstractWorldBuilder（AbstractWorldBuilder.java:48）收敛两前端公共策略：12 条 JRE 隐式入口（AbstractWorldBuilder.java:56-70）、classpath 与 JRE 子模块报错（AbstractWorldBuilder.java:82-87）、native model 二选一。Soot 前端为 legacy。

**JClass 类模型。** declaredFields 是 `MultiMap<String, JField>`（JClass.java:87），因为 Java 允许同名不同类型字段共存；declaredMethods 是 `Map<Subsignature, JMethod>`（JClass.java:89），按子签名索引，也是 dispatch 缓存的键。构建两阶段：构造器只登记 loader/name/source，成员由 build(JClassBuilder) 二次填充（JClass.java:144）；关键容错在 JClass.java:169-177——构建失败降级为 phantom（superClass 置 Object、成员清空），缺 class 不炸。JMethod.getIR()（JMethod.java:179-195）是 synchronized 懒构建四分支：abstract 抛 AnalysisException、native 交 NativeModel、phantom 返回空 IR、正常走 FastIRBuilder（FastIRBuilder.java:90）且构建完置 methodSource = null 释放字节码源（JMethod.java:191）。IR 默认按需，`--pre-build-ir` 才全量预构建（JavaWorldBuilder.java:141-143）。

### 外部连接：谁消费 World，World 依赖谁

消费者几乎是全体分析：各分析经 World.get() 取 hierarchy/mainMethod——DefaultSolver、PTABasedExplicitThrowAnalysis、CHABuilder（对子类 dispatch）皆然。一个反向依赖值得警惕：JClass.parseSubsignature 直接调 World.get().getTypeSystem()（JClass.java:407）——类模型无法脱离已 set 的 World 独立造 phantom 方法，单例路线的代价样本。输入四路：Options（最先 set）、前端三件套（Project/ClosedWorldBuilder/DefaultClassLoader）、TypeSystem、NativeModel 与 IRBuilder。

### 数据流：一个 jar 进来到 World 构建完成

以 runWorldBuilder（JavaWorldBuilder.java:68-144）为例的直线流程：

1. **重置占位**：World.reset() → new World() → World.set → setOptions（JavaWorldBuilder.java:69-75）。
2. **封闭世界**：OptionsProjectBuilder 产出 Project，ClosedWorldBuilder 再收齐全部 ClassSource（JavaWorldBuilder.java:79）——一次性定死可见类集合（closed-world assumption），与 JVM 按需加载相反。
3. **类壳先行**：DefaultClassLoader 构造时全量 new JClass 入 map（DefaultClassLoader.java:48-53），只有名字没有成员。
4. **并行填充**：closedWorld.parallelStream() 逐源分派 BytecodeClassBuilder（ASM）/PhantomClassBuilder，调 jclass.build(builder)（JavaWorldBuilder.java:87-98）。
5. **建层次**：ClassHierarchyImpl 逐个 addClass（ClassHierarchyImpl.java:96-100），在四张 MultiMap 邻接表上架起继承图。
6. **入口锚定**：main 找不到只 warn 不失败；implicitEntries 滤 null——某些 JDK 版本缺这些方法（JavaWorldBuilder.java:130-135）。
7. **IR 就位**：装 NativeModel 与 FastIRBuilder，此后 getIR() 按需触发。

### 设计决策：单例、阶段化、与 Soot Scene 对比

**单例 vs 显式传参。** Tai-e 选了 Soot `Scene.v()` 同款全局单例：收益是全程序信息免传参，代价是隐藏依赖、测试隔离难。缓解三件套＝checkAndSet 防状态漂移 + resetCallbacks 显式化缓存清理 + World.reset() 供测试重建；但 JClass.java:407 这类深层反向调用说明代价只能围堵。

**builder 阶段化。** 接口刻意最小，复杂度压进实现；两个前端 build 方法几乎逐行同构——"换前端不动 World"的架构保证。

**数据与算法分离。** JClass 只查 declared 成员（同名多字段抛 AmbiguousMemberException，JClass.java:271-278）；沿继承链的 resolveMethod/dispatch 全在 ClassHierarchyImpl（ClassHierarchy.java:123），lookupMethod 注释引用 JVM Spec 5.4.3.3（ClassHierarchyImpl.java:351）；dispatch 缓存（ClassHierarchyImpl.java:86）也归 hierarchy，单一归属。

**对比 Soot Scene。** Soot Scene 混装全局状态/解析器/体管理，前端还须借 wjtp Transform 回调才能拿到加载完的 Scene（SootWorldBuilder.java:154）；Tai-e World 只有七个纯数据字段加结果表，前端是直线代码。序列化是 Tai-e 独有增量：`--world-cache` 时 CachedWorldBuilder（CachedWorldBuilder.java:53）先 loadCache，命中即 World.set 返回，未命中则构建后 saveCache；writeObject 把 irBuilder 换成 CachedIRBuilder（World.java:184-188）；缓存键 getWorldCacheHash 改 classpath 即失效。

### 新人提示

1. **World.get() 是肌肉记忆**：测试用 Main.buildWorld(String... args) 便捷入口（Main.java:125-130），它自己 reset+重建。
2. **构建失败三连**：报"Failed to locate Java library"→ `git submodule update --init --recursive` 拉 java-benchmarks（AbstractWorldBuilder.java:82-87）；warn "main class not found"→ 不是失败，只是 getMainMethod() 为 null，查 `--main-class` 拼写；某 JRE 方法拿不到 → 该 JDK 缺这条隐式入口，被静默滤掉（JavaWorldBuilder.java:130-135）。
3. **缓存语义四层**：dispatchTable/allSubclasses 进程内缓存随 World 丢弃；JMethod.ir 懒 + synchronized，getIR 幂等；JClass.releaseClassSource()（JClass.java:456）IR 构建后释放 ClassReader；world-cache 跨进程，仅程序输入不变时命中。
4. **写自己的分析**：永远别碰 World setter（checkAndSet 当场抛异常）；结果存取走 storeResult/getResult；遍历程序用 allClasses()（ClassHierarchy.java:56）或 applicationClasses()（ClassHierarchyImpl.java:179-180）。
5. **phantom 是特性不是异常**：缺 class 时 JClass.build 降级，phantom 字段/方法按需原子生成（JClass.java:377-399）；分析里先判 isPhantom() 再定语义。
