# 06 · tools/cuda-tile-tblgen —— 代码生成器：一份数据，六路后端

> 目录：`tools/cuda-tile-tblgen/`（29 个文件，共 10551 行）
> 代表文件：cuda-tile-tblgen.cpp（入口）、BytecodeGen.cpp（1443 行）、BytecodeReaderGen.cpp（874 行）、BytecodeTypeCodeGen.cpp（1213 行）、BytecodeAttrCodeGen.cpp（1327 行）、SpecGen.cpp（规格文档）

## 一、角色定位

这个目录是"生成器的生成器"：它自己是一个可执行工具 `cuda-tile-tblgen`，读入 Ops.td/BytecodeOpcodes.td/BytecodeTypeOpcodes.td/BytecodeAttrOpcodes.td 等 TableGen 记录，产出 C++ 源码片段（.inc），再被 BytecodeWriter/BytecodeReader/MinVersionAnalyzer（第 2/3/5 篇）include。第 5 篇说过"版本判定代码零手写"——零手写的另一面就是这里：**全部手写集中在生成器，且生成器本身由分析层与发射层分工**。除了字节码主线，目录里还住着规格文档生成线（SpecGen/Emitter，产出方言 Markdown/RST 文档）与属性常量线（AttrCodeGen，产出枚举清单/GPU 架构常量）。整个目录的逻辑身份：Ops.td 是唯一真源，本目录负责把真源编译成一切下游形态。

工具入口 cuda-tile-tblgen.cpp 极薄：`MlirTblgenMain`（cuda-tile-tblgen.cpp:43）撑起标准 tblgen 命令行，本地只注册一个 `-gen-op-spec` 后端（L29-41，带 `-examples-directory` 选项把示例写到磁盘）；其余全部后端经 `GenRegistration` 静态对象在各 .cpp 里自注册——这是 mlir-tblgen 插件式架构的标准姿势。

## 二、内部结构

### 2.1 字节码四后端 + 读端两后端：六个 GenRegistration

BytecodeGen.cpp 尾部注册了四个后端（L1417-1441）：`-gen-cuda-tile-bytecode`（→Bytecode.inc）、`-gen-cuda-tile-opcodes`（→StaticOpcodes.inc）、`-gen-cuda-tile-type-bytecode`（→TypeBytecode.inc）、`-gen-cuda-tile-attr-bytecode`（→AttrBytecode.inc）。CMake 接线在 lib/Bytecode/Writer/CMakeLists.txt:33-36，源 .td 与选项一一对应。读端另有两个：BytecodeReaderGen.cpp:862/869 的 `-gen-cuda-tile-bytecode-reader`（→BytecodeReader.inc，被 Reader 的 GEN_OP_READER_DISPATCH include，第 3 篇 2.7）与 `-gen-cuda-tile-type-bytecode-reader`（→TypeBytecodeReader.inc），接线在 lib/Bytecode/Reader/CMakeLists.txt:31-39。**写端与读端是两个独立后端**——不是一份代码生成两份，而是各自从同一份 .td 记录独立推导。这保证了对称性靠"同源"而非"共享代码"，任何一侧改坏都过不了 round-trip 测试。

**opcode 冻结纪律的编译期执法**在 BytecodeGen.cpp:62-100：`validateAllOpcodeAssignments` 在任何发射之前先扫全部 PublicOpcode 记录，四查——码值在所属区间内、**码值不得重复**（重复即 `PrintFatalError "duplicate opcode value 0x..."`，L81-89）、**同一操作不得双重分配**（L90-98）、码类与操作类型匹配。第 1 篇"新增 op 忘登记操作码会被拦"说的就是这里——以及它反向也拦"两个 op 抢一个码"。这是把冻结表从文档纪律升级为构建期硬约束的关键一招。

**主发射入口 `generateBytecode`**（L1143-1172）按四个 `#ifdef` 段输出：`GEN_OP_WRITERS`（逐 op 序列化函数，Writer 的 dispatchOpWriter 消费）、`GEN_OP_WRITER_DISPATCH`（opcode→函数 switch）、`GEN_OP_VERSION_CHECKERS` 与 `GEN_OP_VERSION_CHECK_DISPATCH`（第 5 篇分析器的引擎）。同文件还有 `generateOpcodes`/`generateTypeBytecode`/`generateAttrBytecode` 分别驱动另三个 .inc。

### 2.2 版本抽取共享层：BytecodeGenUtilities

四后端共用一簇版本工具（BytecodeGenUtilities.h:32-95）：`parseVersion` 把 "13.3" 拆 major/minor；`extractVersionFromOperation/Attribute/Operand/Result` 分别从 Operator 记录、命名属性装饰器（`CudaTileArgMetadata`，Dialect.td:246）、操作数/结果索引上把 `sinceVersion` 挖出来。第 1 篇强调"版本写在 .td 定义上"、第 5 篇讲"五档 bump 规则"——中间的桥就是这一簇函数。所有后端拿到的版本元数据都经它归一，不存在第二套解析。

### 2.3 类型/属性双后端：分析层 + 发射层的镜像结构

TypeBytecode.inc 与 AttrBytecode.inc 各由一对文件产出，且两对结构互为镜像：

**分析层**先把 TableGen 记录归拢成中间模型。BytecodeAttrAnalysis.h:51-62 的 `BytecodeAttrParameter::Kind` 把属性参数分类（EnumValue/NestedAttr/PolymorphicNestedAttr/StringAttr/StringRef 等），`analyzeBytecodeAttrs`（.cpp）汇总出 `BytecodeAttrStructure`——内含 `CudaTileSerializableAttr`（可序列化属性清单）、`BytecodeAttr`、`CudaTileEnumAttr`+`EnumCase`（枚举及其带版本的 case）。BytecodeTypeAnalysis 同构，产出 `BytecodeTypeStructure`（CudaTileType/BuiltinType）。

**发射层**再按模型逐函数生成。类型侧七个函数（BytecodeTypeCodeGen.h:31-55）：`generateTypeTagEnum`（类型 tag 枚举——Reader 侧 switch 的 case 来源）、`generateTypeSerializers`/`generateTypeDeserializers`（写读两套参数编解码）、`generateSerializerDispatch`/`generateDeserializerDispatch`（双 dispatch）、`generateDependentTypeRegistration`（第 2 篇 TypeManager"先注册依赖类型"的生成物来源）、`generateTypeVersionMap`（第 5 篇 GEN_TYPE_VERSION_MAP 的真身）。属性侧十七个函数（BytecodeAttrCodeGen.h:31-108）：多出的 `generateEnumTypeTrait`/`generateEnumAttrVersionCheck`/`generateEnumValueVersionCheck`/`generateEnumValueVersionMap`/`generateAttrParamVersionMap` 系列正对应第 5 篇 include 的三个属性版本宏；头文件注释明说 Serializers/Deserializers/DependentRegistration"Mirrors ... in BytecodeTypeCodeGen"（L71-77、L107-108）——**镜像关系是注释钉死的契约**，一侧加函数另一侧要跟。

### 2.4 读端后端 BytecodeReaderGen.cpp

874 行生成 Reader 侧四类代码：flags/operand/attribute/result 的反序列化、**SameOperandRank 修正**、操作读取 dispatch 与类型读取。与写端生成器比，它多处理"读旧版本文件"的分支——可选参数在 13.3 前后有两种编码（Version.h:89-93 的 kUnifiedBitfieldVersion：13.3 起可选参数统一进位域，之前 OptionalEnum 用内联标志），生成物里逐参数按文件版本二选一。这是"格式演化史"被编码进读端的直接证据。

### 2.5 规格文档线与 covertSyntaxToSignature 笔误

SpecGen/Emitter/CudaTileOp/CudaTileAttr/CudaTileType 五文件组成文档后端：`CudaTileOp`（580 行 .cpp）把 TableGen Operator 包装成带签名/约束描述/示例的文档模型，`SpecGen::generateSpec` 按分组（第 1 篇十分组在此消费）发射 Markdown，`Emitter` 提供 Badge/表格/锚点原语并把 `mlirExamples` 写到磁盘。**勘误一处**：SpecGen.cpp:220 的 `covertSyntaxToSignature` 函数名是 `convert` 的笔误（covert=隐蔽的，本意"把语法转换成签名"）；实现（L220-240）是把 assemblyFormat 按空格切分、剥掉反引号、遇 `` `:` `` 或 `attr-dict` 停止，收集操作数段做签名渲染。该函数当前只在 L471 的注释里被引用（实际调用已改为别的路径），因此笔误无运行时影响——但 grep 时按 convert 找不到、按 covert 才找得到，新人别被名字骗了。此外 AttrCodeGen.cpp（569 行）是独立小后端：`-gen-enum-attr-list`/`-gen-gpu-arch-def`/`-gen-gpu-arch-constants`/`-gen-hint-key-accessors` 四个注册（L532-563），服务 sm_ 架构族常量与优化提示键，与字节码无关。

## 三、外部连接

输入侧：include/cuda_tile/Dialect/CudaTile/IR/ 下的 Ops.td/BytecodeOpcodes.td/BytecodeTypeOpcodes.td/BytecodeAttrOpcodes.td/Types.td/AttrDefs.td（第 1 篇）。上游库：mlir/TableGen（GenRegistration、Operator/AttrOrTypeParameter 包装）、llvm/TableGen（RecordKeeper）。输出侧六路 .inc 的消费矩阵——Writer：Bytecode.inc+StaticOpcodes.inc+TypeBytecode.inc+AttrBytecode.inc；Reader：BytecodeReader.inc+TypeBytecodeReader.inc+StaticOpcodes.inc（版本白名单）+Type/Attr 反序列化段；MinVersionAnalyzer：三张 VERSION_MAP+版本检查器；方言本体 Ops.cpp.inc（经 mlir-tblgen 标准后端，非本工具）；文档构建：CudaTile.md/ops.rst（CMake CudaTileSpecGen/CudaTileDocGen 目标）。构建依赖链上 `add_dependencies(mlir-headers cuda-tile-tblgen)`（include/.../CMakeLists.txt:45）保证 .inc 先于消费者生成。

## 四、数据流

以新增一个带版本化属性的操作为例走全链：Ops.td 写定义（op 版本 13.4、`CudaTileArg` 第三参标属性版本）→ BytecodeOpcodes.td 表尾加码位 → CMake 触发 cuda-tile-tblgen 六后端 → BytecodeGen 先 validateAllOpcodeAssignments 验冻结表 → 生成物各就各位：写端序列化函数+dispatch（Writer 用）、读端 parse 函数+dispatch（Reader 用）、版本检查器（分析器用）、类型/属性编解码+版本表 → 下游 .cpp 重编译即获得完整读写分析能力 → 文档线同轮刷新签名与示例。**人类只写 .td 两行，机器生成约数百行**——且写读两端+分析器+文档四处保证一致。

## 五、设计决策

**为什么读端写端各自独立生成而不共享发射？** 序列化与反序列化的输出形态差异大（一个递归下降写、一个 switch 重建），强行共享会让两头都别扭；让两者从同一中间模型独立发射，对称性由 round-trip 测试兜底，是 tblgen 生态的成熟模式。

**为什么 opcode 校验用 PrintFatalError 而非返回错误？** 构建期配置错误（.td 写错）没有"运行时降级"的余地，fail fast 让构建直接红掉比生成一份坏 .inc 再让编译器报几百个谜语错误便宜得多。

**为什么属性/类型代码生成器做成分层的 Analysis+CodeGen？** 十七+七个生成函数共享同一份结构化中间模型，分类逻辑（参数 Kind、可序列化性）只算一次；若每个发射函数各自解读原始 Record，规则会漂移。

**为什么文档生成器与代码生成器同住一个工具？** 文档（签名、示例、类型矩阵）与代码同源于 .td——同工具保证"文档即代码"，第 1 篇 descriptionTables 与第 4 篇 verify 数组的那类双真源风险在文档侧天然消除。

## 六、新人提示

1. **改 .td 后看不到效果**时先查生成物：`build/` 下对应 .inc 是否刷新（依赖链偶有 stale，删 .inc 重编最稳）；再确认后端选项与 .td 的配对关系（Writer/CMakeLists.txt:33-36 那张表）。
2. 找 `covertSyntaxToSignature` 这类符号时记住它就是 convert 的笔误（SpecGen.cpp:220）；同样地，第 2/3 篇两处格式注释笔误（0xCF、version[varint]）说明本仓"注释漂移、代码为准"的坑不止一处，写外部解析器/文档引用时永远以代码与生成物为准。
3. 给属性/类型后端加生成函数，先查镜像契约（BytecodeAttrCodeGen.h 里各 "Mirrors" 注释）：类型侧有的 counterpart 是否也要加，否则写读不对称只在 round-trip 测试爆。
4. `validateAllOpcodeAssignments` 的报错是 PrintFatalError——本地复现直接跑 `cuda-tile-tblgen -gen-cuda-tile-opcodes .../BytecodeOpcodes.td`，比整仓构建快得多。
5. 调试生成物时记得 .inc 是 `#ifdef` 分段的全量文件（generateBytecode L1147-1171），同一段宏在不同 .cpp include 会拿到不同段；在生成器里加调试输出时保持这种分段纪律，别让段间产生依赖。
