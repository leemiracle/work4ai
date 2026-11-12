<!-- source: knowledge-graph tour step 5 | files: src/main/java/pascal/taie/frontend/soot/SootClassBuilder.java, src/main/java/pascal/taie/frontend/soot/Converter.java -->

# 05 · Soot 前端与程序装载

### 角色定位

frontend/soot 九个文件，除 SootWorldBuilder 与异常类外全部 package-private。它是**翻译层**：Tai-e 不在 Soot 模型上做分析，而是把 Scene 一次性翻译成 JClass/JMethod/IR，翻译完 Soot 对象退场。入口 SootWorldBuilder（SootWorldBuilder.java:57）两重身份：Java 的 legacy 前端（默认已是 JavaWorldBuilder，Options.java:85-89）与 **Android 唯一前端**（androidMode 强切，Options.java:444）。Tai-e 借 Soot 三样：字节码/dex 解析生态、Jimple 化的半成品 IR、wjtp 钩子——World 构建注册成 `wjtp.tai-e` Transform（SootWorldBuilder.java:123-132），借 Soot 主流程到类层次就绪时接管。

### 内部结构

**SootClassBuilder：拉式填充器。** 实现 JClassBuilder，build() 只有一行 `jclass.build(this)`（SootClassBuilder.java:58-61）——控制权反转给 JClass.build 回调拉取材料。getSuperClass 对 java.lang.Object 特判返回 null（SootClassBuilder.java:74-80）；getGSignature 从 SignatureTag 取泛型签名串（SootClassBuilder.java:122-129），但解析者是 ASM SignatureReader（GSignatures.java:40-42）——Soot 在泛型上只是搬运工；isApplication 在 Android 模式下把 android. 等前缀类排除出应用类（SootClassBuilder.java:110-114）。

**Converter：翻译器 + 四张缓存表。** field/method/fieldRef/methodRef 四张 ConcurrentMap（Converter.java:119-131）保证同一 Soot 对象只翻译一次且并发构建期线程安全。convertType 把 8 种 PrimType 映射到 Tai-e 类型单例（Converter.java:138-172）。最关键的 convertClass **不转对象，转名字**：`loader.loadClass(sootClass.getName())`（Converter.java:174-176）——Soot 引用从不进 JClass 模型，一切按名经 ClassHierarchy 装载，"翻译完可丢弃"由此成立。convertMethod（Converter.java:189-208）末个构造实参是裸 sootMethod，存入 JMethod 的 transient methodSource（JMethod.java:66-73）供 IR 构建。

**Modifiers**：int 修饰位经 15 个 soot.Modifier 谓词探测转成 EnumSet，按 int 缓存（Modifiers.java:42-92）。

**basic-classes.yml：Scene 预注册清单。** 跑 Soot 前先 `scene.addBasicClass(name, HIERARCHY)`（SootWorldBuilder.java:116-120、148）。四类：Java 8/11 防运行时异常类（basic-classes.yml:5-12）、native 间接引用不自动装载的 FileSystem（basic-classes.yml:17-19）、动态加载的 URL handler（basic-classes.yml:22-25）、被注释留 TODO 的 https.Handler（basic-classes.yml:27-29）。

### 外部连接

**Soot 类型泄漏面可数完**：JMethod.methodSource（实为 SootMethod，建完 IR 置 null，JMethod.java:190）与 SootClassLoader 持有的 Scene（SootClassLoader.java:37）。ir/language/analysis 三包 grep `^import soot` 仅一处——Android 插件用的 FlowDroid 类 ARSCFileParser（LayoutResourceResolver.java:32）。

依赖的特殊设计：编译用魔改 jar `lib/sootclasses-modified.jar`、运行用 Maven soot:4.4.1（build.gradle.kts:23-30）；Android 叠加 FlowDroid（build.gradle.kts:43-48）。

**被 World 消费**：build(options, scene)（SootWorldBuilder.java:154-204）把 ClassHierarchy/TypeSystem/mainMethod/implicitEntries（14 个 JRE 隐式入口，AbstractWorldBuilder.java:47-61）/NativeModel/IRBuilder 装进 World。对账工具 JClassExaminer（src/test/java/pascal/taie/frontend/soot/JClassExaminer.java:42-64）逐类比对父子/字段/方法签名，钉了两个差异：Soot 签名带引号须剥离、phantom 类在 Tai-e 有 java.lang.Object 父类而 Soot 为 null（JClassExaminer.java:59-73）。

### 数据流

1. **Soot 跑主流程**：buildForJava 后 `soot.Main.v().run(args)`（SootWorldBuilder.java:225）；Android 绕开它手动 loadNecessaryClasses+wjtp.apply()，因 soot.Main 会 retrieveAllBodies 拖慢装载（SootWorldBuilder.java:270-276）。
2. **钩子触发**：Soot 跑到 wjtp pack 回调 build(options, Scene.v())（SootWorldBuilder.java:126-128）。
3. **类装载**：buildClasses 逐个 loadClass（SootWorldBuilder.java:206-210，TODO: parallelize?）。SootClassLoader.loadClass（SootClassLoader.java:54-72）查缓存 → getSootClassUnsafe → new JClass → **先 put 进 map 再 build**（SootClassLoader.java:62-65，防继承链递归死循环）→ hierarchy.addClass，成员再由 JClass.build 回调、Converter 按需翻译。
4. **IR 惰性构建**：JMethod.getIR（JMethod.java:179-193）：abstract 抛 AnalysisException、native 走 NativeModel、phantom 给空 IR；正常路径由 MethodIRBuilder 把 methodSource 强转 SootMethod 后 retrieveActiveBody（MethodIRBuilder.java:214-216），Android 应用类再转 Shimple SSA，用完 releaseActiveBody、建好即 methodSource=null（JMethod.java:190），Soot 抛错则降级空 IR。
5. **可选预热**：--pre-build-ir 时 buildAll 按 CPU 数分组并行 getIR（IRBuilder.java:69-100），且须联动调整 Soot 选项（见提示 2）。

JastAdd 异常则意味着喂了含 Java 8+ 语法的 .java 源码（SootWorldBuilder.java:237-248）。

### 设计决策

保留 Soot 三个硬理由：①Android/dex 生态（SootWorldBuilder.java:251-268），ASM 直翻路线没有；②Jimple 化的 Body 已是半成品 IR，只做逐语句搬运；③wjtp 钩子复用装载时序。代价：G/Scene 单例须 G.reset() 清场（SootWorldBuilder.java:81）、装载串行、双份内存边建边丢、魔改 jar 版本漂移。

**frontend/java 对照**：JavaWorldBuilder（JavaWorldBuilder.java:55）由 ClosedWorldBuilder 做引用闭包（ClosedWorldBuilder.java:53）：从 mainClass+inputClasses+4 个 BASIC_CLASSES 出发，8 线程 worklist 跑传递依赖（ClosedWorldBuilder.java:118-158），找不到的降级 phantom；类构建 parallelStream、IR 用 FastIRBuilder。它砍掉 Soot、天然并行，但只吃 .class 无 dex 能力。"legacy" 名不副实：**Java 路线上它是被替代的旧方案，Android 路线上是不可替代的现行方案**；两前端靠 AbstractWorldBuilder 骨架保持产出同构。

### 新人提示

1. **加 JRE 类先查 basic-classes.yml**：装载期 SootClassNotFoundException/AssertionError 多半缺预注册类，把类名加进 yml 即可；https.Handler 的注释 TODO（basic-classes.yml:27-29）说明加类可能引出下一个缺失。
2. **preBuildIR 与 drop_bodies_after_load 联动**（SootWorldBuilder.java:102-108）：开 --pre-build-ir 却漏设 false，Soot 在 IR 阶段抛 "No method source set"。
3. **Soot 版本升级三查**：双 jar 分裂（build.gradle.kts:23-30）、魔改 jar 与 4.4.1 的 diff、ASM 9.8（build.gradle.kts:33-37）与 Soot 内嵌 ASM 兼容。
4. **双前端选择**：普通 Java 程序默认 JavaWorldBuilder 已够；apk 必走 Soot 前端（Options.java:444 强切）。调试转换用 JClassExaminer 对账，注意 phantom 父子语义两体系不同。
5. **改 Converter 注意并发**：四张表与 Modifiers.modMap 都是 ConcurrentMap——buildAll 并行 getIR（IRBuilder.java:88-91）会并发触发 ref 转换，换普通 HashMap 会在预热路径上炸。
