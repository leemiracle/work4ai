<!-- coderead unit 02 | files: 22 个 | 全量深读 2026-10-13 -->

# 02 · util 根工具族：22 个类的逐类参考手册

## 1. 包职责与架构位置

`pascal.taie.util` 根目录是 Tai-e 的 **L1 通用基础设施层**——不依赖 IR、World、analysis 等上层概念（唯一邻接依赖是 `util.collection.Maps` 工厂）。四类原语：

1. **稠密索引抽象**：`Indexable` + `Indexer` + `SimpleIndexer`。Var/Stmt/JClass/Pointer/Node/CSObj 全实现 Indexable，映射为非负 int 后存入 `util.collection` 的 `IndexableSet`/`IndexerBitSet`，把 equals/hashCode 换成数组下标访问——性能设计基石。
2. **结果传递总线**：`ResultHolder` + `AbstractResultHolder`——World/JClass/DefaultIR/PointerAnalysisResultImpl 靠它实现"分析 A 的结果供分析 B 取用"。
3. **性能监控**：`Monitor`（现役）与 `Timer`（deprecated 待删）；4. **散装工具**：字符串/哈希/路径/可变整数/三元函数式接口。

引用度实测（main 源码，2026-10）：`Indexer` 26 文件 import（6 实现类）；`AnalysisException` 26 文件；`Hashes` 15 文件；`Monitor` 11 文件（Main.java:52）；`Indexable` 11 个实现/消费文件；`Timer` **0 import**（仅剩 Monitor javadoc `@see`，实质退役）。批量集合/图算法在 `util.collection`/`util.graph`。

## 2. 逐类深读（主体）

#### Indexable Indexable.java:35
实现者提供**非负** int 索引以便存入 bit set 等高效结构，唯一方法 `getIndex()`（Indexable.java:40）。javadoc 钉死两条：索引非负；**不保证全局唯一**（如 Var 索引仅在同方法内唯一），跨作用域混用是调用方责任。

#### Indexer Indexer.java:41
对象↔索引双向映射接口，`extends Serializable`，两方法 `getIndex(E)`（Indexer.java:46）/`getObject(int)`（L51）。核心不变量（L37）：`e.equals(i.getObject(i.getIndex(e)))`；索引只在**同一 indexer 内**唯一。与 Indexable 互补：前者"对象自带索引"，后者"外部按需登记"。

#### SimpleIndexer SimpleIndexer.java:47
`Map<E,Integer>` + `List<E>` 双向表实现，索引即列表下标。三构造器（L58/L66/L75）。`getIndex`（SimpleIndexer.java:81）**自动登记**：miss 则 put+add 返回 `counter++`，开头 `Objects.requireNonNull` 拒绝 null；`getObject`（L94）把越界转译为更友好的 `IllegalArgumentException`。易错点：check-then-act **非线程安全**；`toString`（L104）全量打印，大表调日志会爆。

#### AbstractResultHolder AbstractResultHolder.java:34
Map-based 骨架实现。唯一字段 `transient Map<String,Object> results = Maps.newHybridMap()`（AbstractResultHolder.java:39）——transient：宿主序列化时缓存不落盘，靠 supplier 重算。`getResult(String)`（L52）是 unchecked 强转，类型安全靠调用方；`getResult(String, Supplier)`（AbstractResultHolder.java:63）用 `computeIfAbsent` 实现"没有就算、算了就存"的惰性缓存。

#### ResultHolder ResultHolder.java:32
结果容器 8 方法接口。`getResult(String, Supplier<R>)`（ResultHolder.java:60）在接口层定义惰性语义：miss 时计算并**存入后返回**；三个 getResult 重载（L47/L53/L60）靠参数类型区分，传 `null` 默认值有重载歧义。非抽象实现仅 AbstractResultHolder，四个子类恰是 World.java:49 / PointerAnalysisResultImpl.java:65 / DefaultIR.java:42 / JClass.java:61——"全局/单分析/单方法/单类"四级缓存位点。

#### Monitor Monitor.java:78
现役综合监控器：计时+CPU+内存。`INTERVAL=1` 秒采样（Monitor.java:85）；单线程 daemon scheduler（L117）。`start()`（Monitor.java:131）幂等，把起始样本**折入峰值**（L139）再启动周期采样；`stop()`（L153）对称折入**结束样本**（L161）后 shutdown（2 秒等待→shutdownNow，中断恢复位）。`inSecond()`（L178）/`clear()`（L187）/`toString()`（L202，输出 elapsed + CPU/内存 start/peak/end）。峰值更新带参版 `synchronized`（Monitor.java:216）；CPU 负值钳位 0（L225）；内存=heap+non-heap used（L233）。静态族：`runAndCount(Supplier, name, Level)`（Monitor.java:251）为核心；`runWithTimeout`（L303）独立线程，超时 `cancel(true)` 中断并抛 RuntimeException。**易错点**：实例一次性——stop 后 scheduler 已关，再 start 抛 RejectedExecutionException；`clear()` 不关 scheduler，运行中 clear 留孤儿采样任务。（git 8f22e419 刚修"峰值忽略首尾样本"，L139/L161 即修复位。）

#### Timer Timer.java:49
`@Deprecated(forRemoval = true)`（Timer.java:48）旧计时器，全仓已无 import。start（L65）/stop（L72）幂等累加、runAndCount（L100）。与 Monitor 两处行为差异：① 无 scheduler，**可反复复用**；② 旧 `runWithTimeout`（Timer.java:132）超时直接 `System.exit(1)`（L140）杀进程，新版改为中断+抛异常（进程级熔断→任务级取消）。新代码一律用 Monitor。

#### AnalysisException AnalysisException.java:25
框架统一运行时异常（26 文件），"分析失败"与"程序 bug"的边界类型。四构造器（L30/L36/L43/L50）全转发 RuntimeException。

#### Canonicalizer Canonicalizer.java:35
等价元素去重器，返回**规范实例**（intern 语义）。核心 `get(T item)`（Canonicalizer.java:39）：先 get，miss 则 `putIfAbsent(item, item)`，竞态下返回已驻留旧值；底层 `newConcurrentMap()`（L37）线程安全。这是**外部规范化**（与 InternalCanonicalized 相对），消费者 Zipper 与 OtherFlowEdge 借它把值相等身份不同的临时对象折叠成可 `==` 比较的单例。

#### InternalCanonicalized InternalCanonicalized.java:45
标记注解："本类实例由类内部自行规范化"。javadoc（L35-42）钉死配套**四步模式**：①默认 equals/hashCode（`==` 即 equals）；②私有嵌套 Key 类覆写 equals/hashCode；③Key→instance 映射；④构造器私有 + 静态工厂查表。全仓唯一使用者 Subsignature.java 严格符合（静态工厂 get + 私有构造器 Subsignature.java:83）。

#### Copyable Copyable.java:35
自描述拷贝接口 `T copy()`，语义约定**独立可变副本**，深浅由实现者文档化。消费者：数据流 fact（MapFact/SetFact）、PTA PointsToSet、SetEx/IBitSet。

#### Experimental Experimental.java:45
实验性标记注解，RUNTIME retention（可反射）+ Target 覆盖包/类型/构造器/字段/方法（Experimental.java:37-44）+ Documented。现用于整个 generics 包与 JClass/JMethod 泛型签名方法——"泛型签名支持"是最大实验面，勿在其上做长期承诺。

#### Hashes Hashes.java:31
手写 hash 组合器，避免 `Objects.hash()` 的 varargs **数组分配**（javadoc L29 明言）。三对方法：`hash(o1,o2)`（Hashes.java:40）/`safeHash`（L47 null 安全）；三元（L55/L65）；四元（L76/L87）。系数 31 与 `String.hashCode` 同族。契约：`hash` 遇 null 抛 NPE，`safeHash` 把 null 映射 0。15 文件用于 Key 类手写 hashCode。

#### Strings Strings.java:28
String 静态工具（final+私有构造标准形态）。`capitalize`（Strings.java:40）：null/空原样返回；首字符已大写则**返回原引用零拷贝**（L46-48）。`escape`（Strings.java:63）只转义 `\\ \" \b \t \n \f \r` 八字符（L71-78），不处理 Unicode 控制字符与单引号——面向 Jimple/Dot 输出，严格 JSON 需另找工具。null 宽容与 Hashes.hash 相反，读 javadoc 为准。

#### PathUtils PathUtils.java:27
路径/类名工具。常量 JAVA/CLASS/JAR/ZIP（PathUtils.java:29-35）被 ClassNameExtractor 复用。`toStringWithoutExt`（L43）只剥最后一个点后扩展名；`toClassName`（PathUtils.java:54）= 去扩展名 + `\`→`/`（Windows 防御）+ `/`→`.`，即 `java/lang/Object.class → java.lang.Object`，嵌套类 `$` 原样保留。`isJavaFile/isClassFile/isJarFile`（L63-73）纯后缀判断；`isZipFile`（PathUtils.java:79）**jar 也算 zip**，类路径加载统一处理两种压缩格式。

#### ClassNameExtractor ClassNameExtractor.java:44
从 JAR/目录抽取全部类名，兼 CLI（`main` L46：args[0]=输出文件）。`extract(String)`（L69）→ 私有 `extract(Path)`（L76）按 isDirectory 分派：`extractDir`（L80）`Files.walk` 遍历 .java/.class 后 toClassName；`extractJar`（L96）先校验 isJarFile，`jar.stream()` 过滤 META-INF 与 .class 后缀，手工 `/`→`.` 去尾。消费者 AbstractWorldBuilder 与 OptionsProjectBuilder。易错点：异常统一包 RuntimeException；`module-info.class` 不在排除名单会被列出。

#### RuntimeInfoLogger RuntimeInfoLogger.java:38
启动期环境/版本日志器，Main.java:58 调 `logRuntimeInfo()`（RuntimeInfoLogger.java:65：env→system→taie 三段）。`ENV_KEYS`（L42）固定 8 个系统属性；`logSystemInfo`（L84）报 CPU 核数与总内存；`logTaieInfo`（L97）读 build 注入的 `META-INF/tai-e-build.properties`（version/commit）。`getBuildProperties()`（RuntimeInfoLogger.java:114）双通道：jar 运行走 JarURLConnection（L118），开发环境走 classloader（L130）。排查"用户跑哪个 commit"的第一信息源。

#### MutableInt MutableInt.java:31
可变 int 包装器，`extends Number`，单线程场景（javadoc L28-29 让并发用 AtomicInteger）。`set`（L45）、`add(int)`（MutableInt.java:52）+ 四个 Number 转换。消费者 Dominators/Zipper/Profiler。易错点：**未覆写 equals/hashCode**，当 HashMap key 按引用相等，几乎必是 bug。

#### TriConsumer TriConsumer.java:37
三元 Consumer（`accept(T,U,V)`，TriConsumer.java:46），JDK 缺失的三元扩展，javadoc 强调**靠副作用工作**，无默认方法。消费者：TwoKeyMap 族的双键遍历回调与 PTA AbstractModel。

#### TriFunction TriFunction.java:37
三元 Function（`apply(T,U,V)→R`，TriFunction.java:47），无 andThen/compose。消费者：TwoKeyMap 的 `compute(K1,K2,TriFunction)` remapping 与 MapMapTwoKeyMap。

#### Predicates Predicates.java:27
Predicate 工厂，`alwaysTrue()`（Predicates.java:67）/`alwaysFalse()`（L74）。**枚举单例**（L32）+ `withNarrowedType()`（L58）做一次标注 `// safe contravariant cast` 的协变窄化——`Predicate<Object>` 转 `Predicate<T>` 安全（test 忽略入参），免每次 new 且 `toString()` 恒为 `Predicates.alwaysTrue()` 便于日志（L41）。使用点 AbstractHeapModel；等价 Guava 但零依赖。

#### SerializableSupplier SerializableSupplier.java:38
`Supplier<T> extends Serializable` 交叉接口（SerializableSupplier.java:38）。javadoc（L31-33）警告实现**应无状态**否则序列化失败。存在理由：Maps 工厂族把 factory 存进集合字段要求集合可序列化，普通 lambda 不满足，方法引用以此类型声明即可。消费者全在 util.collection。

## 3. 修改热点（二次开发）

**加通用工具方法的惯例**：照抄四件套形态——`final class` + 私有构造器（Strings.java:30 / Hashes.java:33 / PathUtils.java:37 / Predicates.java:29 同款），全 static、无实例状态；null 语义必须在 javadoc 写死（Strings 宽容 vs Hashes.hash 抛 NPE，两种约定并存）；不得 import analysis/ir/language（否则下沉子包）；四元函数式接口照 TriConsumer.java:37 模板加。

**Monitor 性能采集怎么挂**：三层。① 一行式 `Monitor.runAndCount(() -> ..., "名", Level.INFO)`（Monitor.java:251），Main.java:52 与 AnalysisManager.java:103 就这么用；② 分段式——同一 Monitor 反复 start/stop 累计；③ 长生命周期式——PTA 的 AnalysisTimer 插件（AnalysisTimer.java:41-47）持有 Monitor 跨 onStart/onFinish 钩子。runWithTimeout 的中断是**协作式**（cancel(true) 只发中断）。加新指标：仿 CPU/内存三字段组（Monitor.java:98-103）+ 采样方法 + toString 增段，峰值仍走 synchronized updatePeakValues（L216）。

**AbstractResultHolder 扩展新结果类型**：不动 util——结果类直接 `storeResult(分析ID, result)` 存进 World，key 惯例用分析的 `getId()`；新建容器类则 `extends AbstractResultHolder` 一行得全部实现（模板 DefaultIR.java:42）。强类型包装优先 `getResult(key, supplier)`（AbstractResultHolder.java:63），把 unchecked 转换约束在 lambda 边界。

**Indexer/Indexable 扩展**：新 IR 元素要进 bitset 体系时实现 Indexable 并从宿主拿序号（参考 DefaultIR.java:124 的 VarIndexer）；临时建索引直接用 SimpleIndexer。

## 4. 集成触点

本单元几乎**零依赖可摘用**：除 Monitor/RuntimeInfoLogger 依赖 slf4j、AbstractResultHolder 依赖本仓 Maps 外，其余 18 文件仅依赖 JDK，可整文件拷进任何项目。外部价值排序：

- **Indexer 族 + Indexable**：对象映射稠密 int→bitset 集合运算。`SimpleIndexer`（SimpleIndexer.java:47）开箱即用（非线程安全）；连同 `util.collection.IndexerBitSet/IndexableSet` 一起取即得"索引化集合"子系统。
- **Monitor**：`runAndCount`（Monitor.java:251）与 `runWithTimeout`（L303）即拷即用，CPU/内存峰值采样是手写计时器没有的。
- **Hashes**：三元/四元组合 hash（Hashes.java:55/L76）免 varargs 分配。
- **Canonicalizer**（Canonicalizer.java:35）与 **InternalCanonicalized 四步模式**：值对象 intern 化、以 `==` 换 equals 的性能手法。
- **TriFunction/TriConsumer**：补 JDK 之缺，双键 Map 场景标配。**Pair** 不在本单元，在 `pascal.taie.util.collection.Pair`。小件（Strings.escape / PathUtils.toClassName / Predicates / MutableInt）均 50 行内按需取用。

**契约稳定性判断**：

| API | 稳定性 | 依据 |
|---|---|---|
| Indexer / Indexable / ResultHolder / Copyable | 高 | 公共接口，26+/11/4/5 个实现消费点，签名多年未动 |
| SimpleIndexer / AbstractResultHolder / Canonicalizer / Hashes / Strings / PathUtils / Tri\* / MutableInt / Predicates / SerializableSupplier | 高 | 实现类但语义收敛、javadoc 完整、无演进压力 |
| Monitor | 中高·活跃演进 | Timer 替代品（Monitor.java:73 自述），刚修峰值 bug（8f22e419） |
| Timer | 低·明示将删 | `@Deprecated(forRemoval = true)`（Timer.java:48），严禁新用 |
| Experimental 标记面（generics 包、泛型签名 API） | 低 | 注解语义即"随时可变" |

结论：util 根可当稳定底座；敬而远之的是 Timer 与一切 `@Experimental` 面。
