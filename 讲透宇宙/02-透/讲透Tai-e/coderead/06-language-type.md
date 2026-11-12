<!-- coderead unit 06 | files: 22 个 | 全量深读 2026-10-13 -->

# 06 · language/type 类型系统（逐类深读）

## 1. 包职责与架构位置

`pascal.taie.language.type` 是 Tai-e 的 **L2 类型系统层**：类型一等模型（`Type` 接口族）、全局享元注册表与子类型判断（`TypeSystem`/`AbstractTypeSystem`/`FastTypeSystem`）、字节码描述符双向转换（`BytecodeDescriptors`）。22 文件仅 1273 行，却是典型**度数枢纽**：IR（`Var.java:133` 的 `getType()`）、Soot/ASM 两个前端、pta、backend 全消费——实证：`instanceof ClassType` 58 处、`instanceof PrimitiveType` 26 处、`getTypeSystem()` 35 处、`getClassType(` 60 处、`getArrayType(` 25 处。

类层次：

```
Type (Serializable)               ← Type.java:27，唯一方法 getName()
├── ValueType                     ← 值类型标记接口
│   └── PrimitiveType             ← asInt() 计算类型语义
│       └── Int/Boolean/Byte/Char/Short/Long/Float/Double  ← 8 个单元素枚举
├── ReferenceType                 ← 引用类型标记接口
│   ├── ClassType                 ← 唯一普通 class：loader + name
│   ├── ArrayType                 ← record (baseType, dimensions, elementType)
│   └── NullType                  ← 单元素枚举
├── VoidType                      ← 单元素枚举（不属于 ValueType）
└── BottomType                    ← 单元素枚举（"无类型"哨兵）
```

两个**勘误**：①任务描述里的 `TypeParser`/`TypeMapper` 仓内**不存在**（grep 零命中）——字符串→Type 解析入口是 `AbstractTypeSystem.getType(String)`（AbstractTypeSystem.java:158），Soot 类型桥是 `frontend/soot/Converter.java:138` 的 `convertType`；②"八原始单例"实为 **8 个 PrimitiveType 枚举 + 独立 VoidType**（void 不实现 PrimitiveType，VoidType.java:25）。

装配路径最终都汇聚 `World.setTypeSystem`（World.java:123）：Soot 前端 `new FastTypeSystem(hierarchy)`（SootWorldBuilder.java:170）；ASM Java 前端先建 `FrontendTypeSystem`（JavaWorldBuilder.java:84，走延迟初始化构造器）建类期转换描述符，hierarchy 建好后再 `setHierarchy`（JavaWorldBuilder.java:97）。

## 2. 逐类深读

#### Type Type.java:27
全类型族根接口，`extends Serializable`（World/IR 序列化通道前提），唯一方法 `getName()`（Type.java:29）。约定 `getName()` 返回类型名字符串——原始类型 `int`、ClassType 全限定名、ArrayType `int[][]` 形态——可经 `TypeSystem.getType(String)` 反解析（往返闭环）。

#### ValueType ValueType.java:25
纯标记接口（marker），"直接持值"类型（8 个 primitive）。是 `TypeSystem.isAssignable`（TypeSystem.java:108-112）分派"子类型路径 vs 计算类型等价路径"的依据。注意 VoidType 既非 ValueType 也非 ReferenceType。

#### ReferenceType ReferenceType.java:25
纯标记接口，引用语义。实现：ClassType/ArrayType/NullType。它是 null 可赋值性判断的关键（NullType 分支只要求 supertype 是 ReferenceType，FastTypeSystem.java:53-54），也是 pta 把 Var 类型当堆对象类型的前提。

#### PrimitiveType PrimitiveType.java:25
8 个原始类型公共接口。`getName()` default 转调 `toString()`（PrimitiveType.java:28-30），实现枚举只需覆写 toString。核心方法 `asInt()`（PrimitiveType.java:40）：依 JVM Spec 2.11.1 计算类型规则，boolean/byte/char/short 运算都以 int 进行，返回"该类型的值计算中是否表现为 int"。消费方：`Exps.isIntLike`（Exps.java:51）、`NegExp` 把 `-byteVar` 归一为 int（NegExp.java:52）、`canHoldInt`（TypeSystem.java:124-126）。

#### IntType IntType.java:25
单元素枚举 `INT`，toString `"int"`（IntType.java:30），`asInt()` true（:35）。枚举保证全局唯一，**可直接 `==` 比较**（范式如 OperandStack.java:473 `returnType == DOUBLE || returnType == LONG`）。IR 中最常见类型。

#### BooleanType BooleanType.java:25
单元素枚举 `BOOLEAN`，toString `"boolean"`（:31），`asInt()` true（:35）——JVM 层 boolean 以 int 表示，是 Soot `Integer1Type` 折叠为 INT 的根源（Converter.java:147-149）。

#### ByteType ByteType.java:25
单元素枚举 `BYTE`，`asInt()` true（:35）。描述符 `B`（BytecodeDescriptors.java:61）。

#### CharType CharType.java:25
单元素枚举 `CHAR`，`asInt()` true（:35）。描述符 `C`。char 在 isAssignable 值类型等价下与 int 互换——建模的是 JVM 计算类型而非 Java 语言赋值规则。

#### ShortType ShortType.java:25
单元素枚举 `SHORT`，`asInt()` true（:35）。描述符 `S`。

#### LongType LongType.java:25
单元素枚举 `LONG`，`asInt()` **false**（:36）——long 是 category 2 计算类型，与 int 在 isAssignable 意义下不可互换。描述符 `J`。

#### FloatType FloatType.java:25
单元素枚举 `FLOAT`，`asInt()` false（:36）。描述符 `F`。

#### DoubleType DoubleType.java:25
单元素枚举 `DOUBLE`，`asInt()` false（:36）。与 LONG 同为 category 2；OperandStack.java:473 的 category-2 判断即 `== DOUBLE || == LONG`。

#### VoidType VoidType.java:25
单元素枚举 `VOID`，**直接实现 Type**，`getName()` 返回 `"void"`（:31）。仅见于方法返回类型与个别注解；`getArrayType` 以 assert 拒绝 void 作数组基类型（AbstractTypeSystem.java:206）。描述符 `V`——但 `toTaieTypeDesc` 的 switch 无 V 分支，ASM 前端对 `@Ann(type = void.class)` 的 `class V` 描述符特判绕开（BytecodeClassBuilder.java:569）。

#### NullType NullType.java:25
单元素枚举 `NULL`，**implements ReferenceType**，`getName()` 返回 `"null-type"`（:31）。代表 `null` 字面量类型（NullLiteral）。不变量：`isSubtype(任意 ReferenceType, NULL)` 恒 true（FastTypeSystem.java:53-54）；`getArrayType` 禁止 NullType 作基类型（AbstractTypeSystem.java:206-207）。

#### BottomType BottomType.java:30
单元素枚举 `BOTTOM`，`getName()` 返回 `"bottom-type"`（:36）。Javadoc 钉版语义（:26-29）：表示表达式**未定型**，按理不应进 IR，但 Soot 前端对个别变量推不出类型时保留它。消费面极窄：仅 `Converter.java:169` 做 soot BottomType→BOTTOM 映射。**不要**当类型格的 ⊥ 用于子类型推理——只是前端缺类型哨兵。

#### ClassType ClassType.java:29
包内唯一普通 class。字段：`JClassLoader loader`（:31）、`String name`（:33）、`transient JClass jclass` 缓存（:38）。`getJClass()` 懒加载 `loader.loadClass(name)` 并缓存（:50-55）。**equals 语义是最大易错点**（:58-73）：等价 = `loader.equals + name.equals`，**不含 jclass**；hashCode 用 `Hashes.hash(loader, name)`。因 `classTypes` 按名享元（AbstractTypeSystem.java:49），同一 TypeSystem 内同名 ClassType 即同一对象，`==` 与 `equals` 皆成立；**跨 TypeSystem 实例只有 equals 可靠**。陷阱：不存在类名仍返回 ClassType（FIXME，AbstractTypeSystem.java:193-194），`getJClass()` 为 null 时传给 `ClassHierarchyImpl.isSubclass`（ClassHierarchyImpl.java:406）在 `superclass.equals(...)` 处 NPE。

#### ArrayType ArrayType.java:25
record `(Type baseType, int dimensions, Type elementType)`。**不变量**：baseType 是最终非数组基类型；elementType 是"降一维"类型——`dim==1 时 elementType==baseType`，`dim>1 时 elementType==getArrayType(baseType, dim-1)`（由 AbstractTypeSystem.java:210-212 递归构造保证）。`getName()` 用 **elementType** 拼名（:29-31）：`elementType + "[]"`，与 `getType(String)` 的尾缀 `[]` 解析（AbstractTypeSystem.java:160-173）严格互逆。record 自动结构化 equals；TypeSystem 侧另有享元。易错点：`getArrayType` 只 assert 非 Void/Null 基类型，**未禁止传 ArrayType 作 baseType**——Soot 桥总传"非数组基类型+总维数"（Converter.java:164-166），自行调用传嵌套数组会维数重复计数。

#### TypeSystem TypeSystem.java:34
类型系统**稳定公共契约**（extends Serializable）。三段 API：①常用类型七连取 objectType/serializableType/cloneableType/stringType/arrayType/classType/throwableType（:40-70，`classType()` 指 `java.lang.Class`，:65 行尾注释注明避免与 `getClassType(String)` 混淆）；②任意检索 `getType`/`getClassType`/`getArrayType`/`getPrimitiveType`/`getBoxedType`/`getUnboxedType`（:73-87）；③类型检查 `isSubtype`（:100）、default `isAssignable`（:105-113）、`isPrimitiveType`（:115）、static `canHoldInt`（:124-126）。精读 `isAssignable`（:105-113）：`left==right` 快速通道；left 是 ReferenceType 走 `isSubtype`（null→引用、子类→父类、数组→Object）；否则退化为 `canHoldInt(left) && canHoldInt(right)` 的**计算类型等价**。推论：`int→long` false、`Integer→int`（拆箱）false——**装箱/拆箱不在 isAssignable 建模内**，需要处（如 TypeMatcher）自行用 getBoxedType/getUnboxedType 补（TypeMatcher.java:127）。

#### AbstractTypeSystem AbstractTypeSystem.java:37
模板基类，实现除 `isSubtype` 外全部 API，状态围绕**享元注册表**。字段：`defaultClassLoader`（:39）；`classTypes: Map<String, ClassType>`（:49，注释 :41-48 钉版"暂不支持多 classloader 同名类，若支持需扩成 Map<JClassLoader, Map<String, ClassType>>"）；`arrayTypes: ConcurrentMap<Integer, ConcurrentMap<Type, ArrayType>>`（:55，按维数+baseType 两级索引，:51-54 注明 IR 并行构建期被并发写）。构造器（:86-116）：七个常用 ClassType（:94-100，名字取自 ClassNames，ClassNames.java:31 起）、boxedMap 八对装箱映射（:101-109，`IntType.INT → java.lang.Integer`）、unboxedMap 反转（:110-112）、primitiveTypes 名字表（:113-115）；第二构造器（:118-120）给默认并发容器。关键方法：`getType(loader, typeName)`（:158-184）即**字符串类型解析器**——尾向前数 `[]` 对得维数（:160-170），递归解析基类型后 getArrayType 复原（:171-173）；primitive 名直查（:174-175）；`"void"` 特判（:176-177）；其余走 getClassType（:179）；异常包成 `AnalysisException("Invalid type name: ...")`（:181-183）。`getClassType` computeIfAbsent 享元、**不存在类名照常造对象**（:192-197）。`getArrayType`（:205-213）两级 computeIfAbsent 享元+递归构造 elementType，assert `dim>=1` 且基类型非 Void/Null。`getPrimitiveType`/`getUnboxedType` 非法输入抛 IllegalArgumentException（:216-222, :230-236）；`getBoxedType` 直查（:225-227）；`isPrimitiveType` 按名查表（:239-241）。

#### FastTypeSystem FastTypeSystem.java:32
`isSubtype` 唯一生产实现，"借助 ClassHierarchy 做快速子类判断"。字段 `protected ClassHierarchy hierarchy`（:34）；主构造器（:36-39）拿现成 hierarchy；**延迟构造器**（:45-47）专供子类 `FrontendTypeSystem`（FrontendTypeSystem.java:67）——先建类型系统后 `setHierarchy`，期间禁调 hierarchy 相关 API（JavaWorldBuilder.java:84-97）。`isSubtype(supertype, subtype)`（:50-88）分派链：`subtype.equals(supertype)` 直通 true（:51）；NullType → 要求 supertype 是 ReferenceType（:53-54）；ClassType/ClassType → `hierarchy.isSubclass(super.getJClass(), sub.getJClass())`（:55-60，**getJClass 可能为 null**，见 ClassType 节 NPE 陷阱）；ArrayType 对 ClassType → supertype 须为 Object/Cloneable/Serializable（:61-66，JLS 11 版第 10 章，**`==` 引用比较**，正确性依赖享元）；ArrayType 对 ArrayType（:67-85）：维数相等看 baseType 相等或基类子类关系（:71-79，数组协变），`superArray.dimensions() < subArray.dimensions()` 要求 superBase 是三接口之一（:80-83，如 `int[][] <: Object[]`）。其余一律 false（:87）——**无泛型/类型变量分支**（擦除模型），装箱类与原始类型间也无 isSubtype 关系。

#### BytecodeDescriptors BytecodeDescriptors.java:30
final 工具类（私有构造 :33），**字节码描述符 ↔ Tai-e 类型名**双向转换，三处消费：Soot 桥（Converter.java:281 等）、ASM 前端（BytecodeClassBuilder.java:572）、backend 回发（BytecodeEmitter.java:966）。`toTaieTypeDesc(desc)`（:46-76）：`lastIndexOf('[')` 数维数并剥 `[`（:47-51）；`L...;` 剥壳换 `/`→`.`（:53-56）；否则单字符 switch 出八个原始名（:58-69，default 抛 IllegalArgumentException）；最后 `baseType + "[]".repeat(dimensions)`（:71-75）。**不支持 `V`**——`void.class` 注解值需调用方特判（BytecodeClassBuilder.java:569，该注释引用的 `StringReps#toTaieTypeDesc` 是**已死类名**，方法实际在本类）。反向 `toBytecodeDescriptor(Type)`（:84-107）：ClassType → `Lfqcn;`（:85-86）、primitive 按名 switch（:87-99）、VoidType → `V`（:100-101）、ArrayType → `"[" + 递归(elementType)`（:102-103，递归 elementType 天然还原全部维数）。`toBytecodeDescriptor(JMethod)`（:115-123）拼方法描述符。

#### package-info package-info.java:29
包级 Javadoc："Provides model of Java type system"，`@see` 指向 Type 与 TypeSystem（:26-27）。无代码。

## 3. 修改热点（二次开发）

**加新类型（几乎不该做）**。`Type` 实现族是**封闭集合**，类型判断/转换/桥接全是 `instanceof` 链而非 Visitor，新增实现 = "编译器不报错、语义静默漏判"：①`FastTypeSystem.isSubtype`（FastTypeSystem.java:50-88）未列分支一律 false，新类型被静默当作与一切不相关；②`AbstractTypeSystem.getType` 字符串解析（:158-184）不认识新类型名；③`BytecodeDescriptors.toBytecodeDescriptor`（:84-107）对新类型抛异常；④`isAssignable`（TypeSystem.java:105-113）的引用/值二分覆盖不到；⑤前端桥（Converter.java:138、FrontendTypeSystem 的 ASM 转换）映射不到；⑥ClassNames 缺常量。唯一"合理"方向是引入泛型残影（TypeVariable/IntersectionType），那是横跨 language/ir/frontend/analysis 的大手术；常规需求（"表示某类"）应 `getClassType(fqcn)` 而非新类型类。相对便宜的真修改点：**多 classloader 同名类支持**——官方注释给出改法（AbstractTypeSystem.java:44-47，classTypes 键扩为 (loader, name)），同步项：ClassType.equals 语义核对（ClassType.java:58-68）与 FastTypeSystem 里依赖"同名即同对象"的 `==` 判断（FastTypeSystem.java:64-66、:81-83 改 equals 或按 loader 取规范实例）。

**isSubtype 修改点**。唯一实现在 FastTypeSystem.java:50-88，改子类型规则只动这一方法（35 处消费方零感知）。三个易错处：a) `==` 引用比较依赖享元注册表——绕过 `getClassType` 自己 `new ClassType(...)` 会让 `supertype == objectType` 假阴性，**永远从 TypeSystem 取类型**；b) `getJClass()` 可能 null（FIXME，AbstractTypeSystem.java:193），`hierarchy.isSubclass`（ClassHierarchyImpl.java:406）首行对 null NPE，防御写法应在 ClassType 分支前判 null；c) 数组维数比较只覆盖"相等"与"super 更小"，"super 维数更大"正确落兜底 false，勿手滑合并条件。改 null 语义或数组协变（:53-54 / :71-79）须回归 catch 匹配消费方：CatchAnalysis.java:69、ExceptionAnalysis.java:234。

**TypeMapper 与 Soot 桥接**。仓内无独立 TypeMapper，桥接实体是 `Converter.convertType(soot.Type)`（frontend/soot/Converter.java:138-171）：PrimType 逐个展开（:139-154，含 Soot 独有 `Integer1Type/Integer127Type/Integer32767Type` **折叠为 INT**——asInt() 计算类型模型落地处）；RefType → `typeSystem.getClassType(loader, sootType.toString())`（:156-158）；ArrayType → `getArrayType(convertType(baseType), numDimensions)`（:159-162）；VoidType/BottomType → 枚举单例（:163-167）；兜底抛 SootFrontendException（:171）。Converter 构造即持 TypeSystem（Converter.java:133-136），World 装配序"hierarchy → new FastTypeSystem → setTypeSystem → new Converter"（SootWorldBuilder.java:169-173）。ASM 前端不走 Converter，走 FrontendTypeSystem（FastTypeSystem 唯一子类 + 方法描述符缓存，FrontendTypeSystem.java:67）——**给 FastTypeSystem 加抽象方法时必须检查 FrontendTypeSystem**（延迟构造器 FastTypeSystem.java:45-47 存在的唯一理由）。

## 4. 集成触点

- **稳定契约是 TypeSystem 不是具体类**：外部集成一律 `World.get().getTypeSystem()`（World.java:119，35 处仓内调用为证），用 getClassType/getArrayType/getType(String) 取类型，勿 `new ClassType` 或手写解析。
- **单例 `==` 比较的边界**：8 个 primitive 枚举与 Void/Null/Bottom 枚举天然全局唯一，任意上下文 `==` 成立（范式 OperandStack.java:473）；ClassType/ArrayType 是**同一 TypeSystem 实例内**享元（AbstractTypeSystem.java:195、:209-212），实例内 `==` 等价 equals，**跨实例/跨 World 只能 equals**（ClassType.equals 按 loader+name，ClassType.java:58-68；ArrayType 为 record 结构等价）。FastTypeSystem 内部大量 `==`（:64-66）即依赖此约定。
- **类型名字符串协议**：`getType(String)` 接受 `"int[]"`/`"java.lang.Object"`/`"void"`（AbstractTypeSystem.java:158-184），与 `getName()` 严格互逆；`"null-type"`/`"bottom-type"`（NullType.java:31、BottomType.java:36）是特殊枚举名，勿当类名解析。
- **字节码描述符互转**：解析 annotation/反射元数据用 `BytecodeDescriptors.toTaieTypeDesc`（无 `V` 支持）；输出字节码用 `toBytecodeDescriptor`（现成范例 BytecodeEmitter.java:966）。
- **isAssignable 不是 Java 语言赋值规则**：是"计算类型等价 + 引用子类型"的 JVM 语义（TypeSystem.java:105-113），不含装箱/拆箱与 int→long 加宽；语言级赋值判断自行组合 getBoxedType/getUnboxedType（范本 TypeMatcher）。
- **序列化**：Type/TypeSystem 均 Serializable（Type.java:27、TypeSystem.java:34）；ClassType 的 jclass 是 transient（ClassType.java:38），反序列化后首次 `getJClass()` 经 `loader.loadClass(name)` 重解析（ClassType.java:50-55），要求环境里 loader 可用；FrontendTypeSystem 重写 readObject 重建方法描述符缓存。
- **已知缺陷挂账**：不存在类名经 `getClassType` 仍得非 null ClassType（AbstractTypeSystem.java:193-194 FIXME），下游表现为 getJClass()==null 与 isSubtype 链路 NPE 风险——集成方对用户输入类名应先做存在性校验再取类型。
