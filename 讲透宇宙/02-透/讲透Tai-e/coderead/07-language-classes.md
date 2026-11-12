<!-- coderead unit 07 | files: 22 个 | 全量深读 2026-10-13 -->

# 07 · language/classes：类模型 JClass 族

## 1. 包职责与架构位置

`pascal.taie.language.classes` 是 L2 的类模型层：定义被分析程序的静态骨架——JClass/JMethod/JField、类加载器视图 JClassLoader、类层次与成员解析 ClassHierarchy。JMethod 是全仓引用度数第一的类（235）；pta 全分析族都回流到这里：DefaultSolver 初始化即取 `World.get().getClassHierarchy()`（DefaultSolver.java:177），虚拟分派（DefaultSolver.java:650）与子类查询皆在此。本包刻意**前端无关**：解析逻辑为零，只留三个 SPI（JClassLoader/JClassBuilder/ClassSource）给 frontend——soot 前端给 SootClassLoader/SootClassBuilder，java 前端给 DefaultClassLoader/BytecodeClassBuilder/PhantomClassBuilder；World 装配点在 SootWorldBuilder.java:163 与 JavaWorldBuilder.java:100（`new ClassHierarchyImpl()`）。另有常量族（ClassNames/MethodNames/Signatures 等）与签名模式匹配（SignatureMatcher+Pattern），后者是 taint 配置与 IR 模型插件解析 YAML pattern 的统一入口。

## 2. 逐类深读

#### ClassMember ClassMember.java:34
JMethod/JField 公共抽象基类（Annotated+Serializable）。字段 declaringClass/name/modifiers/annotationHolder 全 final（ClassMember.java:36-42），唯独 signature 是 protected 非 final（ClassMember.java:44）——由子类构造器回填，签名是派生数据。`toString()` 返回 signature（ClassMember.java:116）；`isApplication()` 委托声明类。

#### JClass JClass.java:61
全包核心，**声明与继承分离**：构造器只装壳（loader/name/simpleName/moduleName/classSource，JClass.java:123-130），结构信息延迟到 `build(JClassBuilder)` 二次填充（JClass.java:144）——前端先按名建壳、解析后再回填继承，解决类间循环引用。三个要点：

- **build 失败降级 phantom**：try/catch 内 warn 后 superClass 强制为 Object（JClass.java:172）、成员表清空（JClass.java:169-177），脏 class 文件不炸 World 构建。
- **成员表结构不对称**：declaredFields 是 MultiMap\<String,JField\>（JClass.java:87，同名不同类型字段 JVM 合法），declaredMethods 是 Map\<Subsignature,JMethod\>（JClass.java:89，方法按子签名唯一）；build 后均套不可变包装（JClass.java:155-168），JClass 一旦 build 即只读。方法 subsignature 冲突静默取先出现者（JClass.java:167），容忍混淆字节码。
- **phantom 成员按需制造**：getPhantomField（JClass.java:377）/getPhantomMethod（JClass.java:390）用 computeIfAbsent 原子懒创建；后者靠 parseSubsignature（JClass.java:406）把子签名字符串拆回三元组，依赖 `World.get().getTypeSystem()` 已就绪。

getDeclaredField 单参版遇重名抛 AmbiguousMemberException（JClass.java:271-278）；setIndex 一次性赋值（JClass.java:427），index 供 HybridBitSet 用；releaseClassSource 幂等释放字节码读取器（JClass.java:456）。

#### JMethod JMethod.java:47
构造时派生三件套：toSubsignature 算子签名、getSignatureOf 算全签名、Subsignature.get 驻留化（JMethod.java:90-92），signature 出生即定型。isConstructor/isStaticInitializer 用 MethodNames 常量比较（JMethod.java:107-113）；参数注解与参数名是可空平行结构（JMethod.java:131-156）。`getIR()` 是 synchronized 惰性四路分发（JMethod.java:179-195）：abstract 抛 AnalysisException；native 走 NativeModel.buildNativeIR（JMethod.java:186）；声明类 phantom 走 IRBuildHelper.buildEmpty；正常路径 IRBuilder.buildIR 且**立即置 methodSource=null 释放**（JMethod.java:191）。ir/methodSource 均 transient（后者因 CachedIRBuilder 单独序列化 IR，见 JMethod.java:73-77）。getRef() 返回指向自身的 MethodRef（JMethod.java:200）。

#### JField JField.java:39
特有逻辑是 constantValue（JField.java:64）：static final 字段的 ConstantValue 属性（JVM Spec 4.7.2）——此时 `<clinit>` 里没有初始化语句，必须把 Literal 存在 JField 上否则常量丢失（JField.java:44-63 Javadoc）。signature 构造时定型（JField.java:76）；getRef() 返回 FieldRef（JField.java:94）。

#### Subsignature Subsignature.java:38
"方法名+描述符"驻留值对象（`void main(java.lang.String[])` 式），@InternalCanonicalized 的 String 包装：私有静态 ConcurrentMap 全局驻留（Subsignature.java:47），get() 走 computeIfAbsent（Subsignature.java:61）。两个必记点：(1) `World.registerResetCallback(map::clear)`（Subsignature.java:50-52）——跨 World 重建清空，是 Tai-e 全局驻留缓存的标准防泄漏模式，自建缓存必须照抄；(2) 常量 CLINIT/NO_ARG_INIT/MAIN + 工厂 getClinit/getNoArgInit/getMain（Subsignature.java:41-45,68-81）。

#### StringReps StringReps.java:50
签名字符串语法中枢。语法（StringReps.java:38-48）：方法 `<CLASS: RET name(PARAMS)>`、字段 `<CLASS: TYPE name>`。正向 getMethodSignature/toSubsignature（参数 `,` 连接无空格，StringReps.java:135-149）；反向 getClassNameOf（StringReps.java:56）/getSubsignatureOf（StringReps.java:112）/getFieldNameOf/getFieldTypeOf（StringReps.java:90/96，靠首尾空格切分）。**易错点**：validateSignature（StringReps.java:151-163）条件是 `charAt(0)!='<' && charAt(len-1)!='>'`——&& 意味着单边畸形（如 `abc>`）漏检，只有双缺才报错，别拿它当完整校验。getSubsignatureOf(MethodRef)/getDescriptorOf 是 UnsupportedOperationException 占位（StringReps.java:108-124）；isArrayType/isJavaClassName 词法工具在 StringReps.java:168-222。

#### Modifier Modifier.java:27
18 值枚举：语言级 12 个（PUBLIC..STRICTFP）+ 字节码级 6 个（BRIDGE/VARARGS/SYNTHETIC/ANNOTATION/ENUM/MANDATED，Modifier.java:42-47）。谓词族 hasPublic..hasEnum（Modifier.java:54-112）以 Set.contains 实现——**没有 hasVarargs/hasBridge**，取这两个修饰位须直接 contains。

#### ClassSource ClassSource.java:28
"类来源"标记接口，仅 className()/isApp()。JClass 构造时可选携带（transient），是 IR 构建期回查字节码的钥匙，构建完可 release。

#### JClassLoader JClassLoader.java:28
SPI：loadClass 两重载 + getLoadedClasses。allowPhantom 默认语义由实现定——DefaultClassLoader 单参版即 `loadClass(name, true)`（DefaultClassLoader.java:57-58，允许造 phantom），故 `getClass(String)` 在 java 前端下可能返回 phantom 类；拒绝 phantom 须显式 `getClass(name,false)` 或 getJREClass。

#### JClassBuilder JClassBuilder.java:37
SPI，"一个 builder 构建一个 JClass"（JClassBuilder.java:35 TODO 自认关系待显式化）。接口方法=JClass.build 消费的全部字段（getClassType/getModifiers/getSuperClass/getInterfaces/getDeclaredFields/getDeclaredMethods/isApplication/isPhantom/getGSignature…），`build(JClass)` 是回调入口。实现族：SootClassBuilder、BytecodeClassBuilder、PhantomClassBuilder。

#### ClassHierarchy ClassHierarchy.java:37
对外稳定契约，extends Indexer\<JClass\>（稠密索引语义）。五组能力：loader 管理（ClassHierarchy.java:39-47）；类查询——**addClass 契约：每次 JClassLoader 加载新类都必须调用**（ClassHierarchy.java:50-54）；签名查询 getMethod/getField/getJREClass/getJREMethod/getJREField（非法签名抛 AnalysisException，ClassHierarchy.java:76）；解析与分派 resolveMethod/resolveField/dispatch（ClassHierarchy.java:123-147）；子类关系 getDirectSubinterfacesOf/getDirectImplementorsOf/getDirectSubclassesOf/getAllSubclassesOf/isSubclass/getDirectInnerClassesOf（ClassHierarchy.java:152-181）。

#### ClassHierarchyImpl ClassHierarchyImpl.java:46
唯一实现，**缓存策略是二次开发第一敏感点**。数据结构四层：

- **逆邻接表**：四个 MultiMap（directSubinterfaces/directImplementors/directSubclasses/directInnerClasses，ClassHierarchyImpl.java:66-81），由 addClass 维护，二分逻辑：接口只挂 subinterface 边、非接口挂 implementors+subclasses 边（ClassHierarchyImpl.java:133-149），接口不进 directSubclasses。
- **dispatch 缓存**：TwoKeyMap\<JClass,Subsignature,JMethod\>（ClassHierarchyImpl.java:86），永不失效——假设 World 构建后层次冻结。
- **getAllSubclassesOf 缓存**：并发 Map（ClassHierarchyImpl.java:91），值 HybridBitSet\<\>(this,true)（ClassHierarchyImpl.java:477）用 JClass index 做 bitset（setIndex 存在的理由）。**失效是全量清空**：addClass 每次都 `allSubclasses.clear()`（ClassHierarchyImpl.java:160，带 TODO）；构建期穿插查询会反复重算，增量加载是 O(n²) 陷阱。
- **无正向索引**：getClass 直接委托 loader.loadClass（ClassHierarchyImpl.java:184-186）。

解析镜像 JVM Spec 11 Ed.：resolveField 按 5.4.3.2——声明类精确匹配→递归 superinterface→递归 superclass，phantom 类直接造 phantom 字段（ClassHierarchyImpl.java:282-312）；resolveMethod 走 lookupMethod(allowAbstract=true)，失败且为 polymorphic signature（MethodHandle 族）时回退声明类同名方法（ClassHierarchyImpl.java:262-274）；lookupMethod（ClassHierarchyImpl.java:349-383）按 5.4.3.3 先沿 superclass 链（**遇 phantom 类立即返回 getPhantomMethod**，不管是否真声明过，ClassHierarchyImpl.java:359-361）再沿各层接口递归（ClassHierarchyImpl.java:385-403）。

dispatch 分工：Type 版把 ArrayType 归一到 `getJREClass(ClassNames.OBJECT)`（ClassHierarchyImpl.java:319-320）、非 ClassType 警告返 null；JClass 版先做**反向包含检查** isSubclass(methodRef 声明类, receiverClass) 防意外命中（ClassHierarchyImpl.java:332），再查 dispatchTable、miss 时 lookupMethod(allowAbstract=false)——dispatch 只收具体方法、resolve 容 abstract，这是两族查询的本质区别。isSubclass 三级短路：同对象/Object 特判/getAllSubclassesOf().contains（ClassHierarchyImpl.java:406-414）；getObjectClass 懒加载（TypeSystem 初始化顺序，ClassHierarchyImpl.java:424-431）。**isSubclass0/isSubinterface（ClassHierarchyImpl.java:437/453）是不在生效路径上的遗留遍历实现（死代码），改子类查询别改错地方**。

#### SignatureMatcher SignatureMatcher.java:40
pattern→JClass/JMethod/JField 集合的查询门面，持有 ClassHierarchy。getClasses（SignatureMatcher.java:51-76）双路：无通配符精确 getClass、有通配符遍历 allClasses（源码自认 MAY cause performance issues，SignatureMatcher.java:64-65）；`^` 后缀并入 getAllSubclassesOf。getMethods/getFields（SignatureMatcher.java:81-128）isExactMatch 走精确查询、否则三谓词流式过滤。谓词族：NameMatcher 把 NameUnit 序列编译为正则（字面量 quote、`*`→`.*`，SignatureMatcher.java:130-153）；TypeMatcher 处理 `^` 时**只考虑 ClassType**（SignatureMatcher.java:158-191）；ParamsMatcher 是 Repeat 区间回溯匹配（SignatureMatcher.java:214-246）。消费者：TaintConfigProvider/YamlTaintConfigProvider、IRModelPlugin/AnalysisModelPlugin。

#### Pattern Pattern.java:40
包私有模式语法解析器（SignatureMatcher 专用）。`^`=含子类/子类型（Pattern.java:42）、`*`=通配（Pattern.java:44）；MethodPattern `<ClassPattern: TypePattern NamePattern(ParamUnit...)>` 用 `[:\s(,)]` split（Pattern.java:137-158），`<init>` 尖括号因 parseNamePattern 白名单放行（JavaIdentifierPart+`.`+`[]`+`<>`，Pattern.java:83-91）；Repeat 支持 `{N}`/`{N+}`/`{N-M}`（三个预编译正则 Pattern.java:236-242），上限 MAX=256（Pattern.java:233）。各 record 带 isExactMatch 供上层选精确路径。

#### Reflections Reflections.java:35
反射 API 行为静态建模（reflection 分析用）：getDeclaredConstructors/getConstructors（public 过滤，Reflections.java:40-48）、getDeclaredMethods（排除 `<init>`/`<clinit>`，Reflections.java:56-60）。getMethods 模拟 Class.getMethods() 的**简化版：只沿 superclass 链**收集 public 并按 subsignature 去重（Reflections.java:62-95）——不收接口默认方法，与 JLS 有差距，精确建模要自知。

#### ClassNames ClassNames.java:29
@StringProvider 常量族：OBJECT/八个包装类/反射四类（Class/Array/Constructor/Method/Field）/invokedynamic 五件套 CALL_SITE/METHOD_HANDLE/LOOKUP/VAR_HANDLE/METHOD_TYPE（ClassNames.java:84-92）/Throwable 族。全 final class+私有构造器。

#### MethodNames MethodNames.java:29
仅 INIT=`<init>`、CLINIT=`<clinit>`（MethodNames.java:31-33），全仓判断构造器/静态初始化器的唯一词法来源。

#### ExceptionNames ExceptionNames.java:28
11 个运行时异常全名常量（NPE/OOM 等，ExceptionNames.java:30-50）。**与 ClassNames/MethodNames 不一致**：无 @StringProvider、非 final class（ExceptionNames.java:28）——历史遗留，新常量族别学它。

#### Signatures Signatures.java:29
完整签名字符串常量族：FINALIZE/FINALIZER_REGISTER/REFERENCE_INIT、LAMBDA_METAFACTORY/LAMBDA_ALTMETAFACTORY（Signatures.java:38-40）、STRING_CONCAT_FACTORY_MAKE、MethodHandles$Lookup 的 findVirtual/findStatic/findSpecial/findConstructor（Signatures.java:44-50）、唯一字段签名 REFERENCE_PENDING（Signatures.java:53）。是 invokedynamic/字符串拼接插件的硬编码锚点。

#### StringProvider StringProvider.java:33
包内 marker 注解（@Target(TYPE)），标注"以 final 字段提供特殊程序元素字符串表示"的常量类（StringProvider.java:28-31），无处理器消费。

#### AmbiguousMemberException AmbiguousMemberException.java:29
RuntimeException，格式化 "%s has multiple members with name %s"（AmbiguousMemberException.java:31-33），仅由 JClass 按名单参查询抛出。

#### package-info package-info.java:30
包级 Javadoc：一句话定位"类加载、类成员、类层次管理"，@see JClass 与 ClassHierarchy。

## 3. 修改热点（二次开发）

**加类层次查询**：改 ClassHierarchy 接口 + Impl，守缓存三律——dispatchTable 永不失效（冻结假设）、allSubclasses 随 addClass 全量失效（ClassHierarchyImpl.java:160）、正向查询委托 loader。新增缓存型查询先问：结果是否依赖类集合完整性（是则挂进 addClass 失效链）；能否用 JClass index 做 HybridBitSet（免费 O(1) contains，参照 ClassHierarchyImpl.java:477）。要支持增量类加载必须重做失效粒度并审视 dispatchTable 冻结假设。**别动 isSubclass0/isSubinterface**（不在生效路径）。

**注入自定义类/Builder 族**：实现 JClassBuilder（PhantomClassBuilder 最薄可抄）+ 自定义 JClassLoader 返回 build 好的 JClass，并**务必调 hierarchy.addClass**（契约 ClassHierarchy.java:50-54；漏调=逆邻接表缺边，getAllSubclassesOf/dispatch 静默失真）。合成类也可直接 new JClass 后手工 build。注意 JClass.build 降级分支（JClass.java:169-177）会吞 builder 异常变 phantom——调试时 logger 开 debug 才有完整栈（JClass.java:171）。

**JClassBuilder 钩子**：接口即全部钩子面。语言扩展优先改 builder 实现侧而非 JClass 字段——build 后成员表不可变（JClass.java:155-168），事后补成员的唯一官方通道是 phantom 成员（JClass.java:377/390）。

**常量族加条目**：照 ClassNames/Signatures 模板——final class+私有构造器+@StringProvider+全大写。签名字符串必须逐字符核对 StringReps 语法（参数分隔是**逗号无空格**），写错不报编译期错、只会在运行期 getMethod 静默返 null——Signatures.java:38 长签名最易抄错。ExceptionNames 是反面教材。

## 4. 集成触点

**ClassHierarchy 是外部稳定契约**：pta 插件、taint 配置、android/icc 模型只依赖接口不碰 Impl。集成方只 import 接口、从 `World.get().getClassHierarchy()` 取；空返回语义（resolve/dispatch/getMethod 未找到返 null）与异常语义（签名非法抛 AnalysisException）是契约一部分。getJREClass/getJREMethod 固定 bootstrap loader 且 allowPhantom=false，与 getClass 的 default-loader（java 前端下允许 phantom）形成两档严格度。

**JClass/JMethod/JField 只读视图语义**：build 后成员表不可变、签名构造即定型、index 一次性赋值。写通道仅三处且各有用途：phantom 成员按需制造（computeIfAbsent 并发安全）、getIR() 惰性构建（synchronized+构建后释放 methodSource）、releaseClassSource 内存回收（FastIRBuilder 构建后调用）。缓存 JMethod/JField 对象引用跨分析期安全（身份稳定），但**别缓存 getIR() 结果跨 World**（ir transient）；同理自建 String/Subsignature 驻留表必须挂 World.registerResetCallback 清空（范式 Subsignature.java:50-52）。SignatureMatcher 是外部配置（YAML taint 规则、模型方法声明）与类模型的官方桥梁，需要"按 pattern 找方法"时直接复用，别自写正则——Repeat 区间与 `^` 子类型语义的边界已处理。
