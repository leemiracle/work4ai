# 02 · BytecodeWriter.cpp —— .tilebc 序列化核心

> 文件：`lib/Bytecode/Writer/BytecodeWriter.cpp`（1832 行）
> 头文件：`include/cuda_tile/Bytecode/Writer/BytecodeWriter.h`（公共 API 仅 `writeBytecode` 一个入口）

## 一、角色定位

如果说 Ops.td（第 1 篇）是方言的"语法"，BytecodeWriter.cpp 就是方言的"落盘器"。它把内存中的 `cuda_tile::ModuleOp` 序列化为自定义二进制格式 `.tilebc`——不是 MLIR 通用 bytecode，而是一套为 Tile IR 量身定制的线格式：12 字节定长头 + 七类 Section + LEB128 varint 编码。整个文件可以看作三层：最底层 `EncodingWriter`（原子编码原语，BytecodeWriter.cpp:64-168）、中间层五个 Manager/String/Type/Constant/DebugInfo/FunctionTable，各自攒一个 Section）、顶层 `writeBytecode`（BytecodeWriter.cpp:1770-1831）做编排。它与第 3 篇的 BytecodeReader 是严格镜像：Writer 写出的每一个字节，Reader 都有对应的解析路径。

设计上最值得先记住的一点：**Writer 是"先收集、后写出"的两段式**。函数表遍历会把类型、字符串、常量顺手登记进各自的 Manager 池，等所有函数扫描完，再按 Global→Func→Constant→Debug→Type→Producer→String 的顺序统一落盘（BytecodeWriter.cpp:1808-1826）。这个顺序与 Section 枚举值（BytecodeEnums.h:30-41）完全无关——枚举只是节身份标签，写出顺序由依赖关系决定。

## 二、内部结构

### 2.1 EncodingWriter：varint/zigzag/小端三原语（L64-168）

`writeVarInt`（BytecodeWriter.cpp:77-91）实现经典 LEB128：每字节低 7 位承载数据、最高位是续位标志，缓冲上限 10 字节（64 位极限）。枚举类型有模板重载直接转发（L93-96），所以调用点写 `writeVarInt(SomeEnum::Foo)` 与写整数同样自然。

`writeSignedVarInt`（L102-104）在 varint 之上叠 zigzag：`(value << 1) ^ (value >> 63)`。这一步是负数编码的效率关键——不 zigzag 时 `-1` 会编码成 10 个 0xFF 字节，zigzag 后仅需 1 字节。**读端必须做同样的 zigzag 逆变换**，这对 Reader 是强契约。

`writeLE<T>`（L107-115）按小端逐字节写定宽整数，主要用于头部的版本字段与各节 offset 表。`alignTo`（L150-162）负责对齐：当目标对齐 >1 时，计算当前位置模对齐的差值，用 `kAlignmentByte` 填充，并把这次对齐要求并入 `requiredAlignment`——后者最终写进 Section 头，让 Reader 知道需要按几字节对齐来读。`tell()` 配合 offset 表的"先占位、后回填"模式贯穿全部 Manager。

### 2.2 12 字节头：writeHeader（L181-201）

头部结构是全格式最"硬"的部分：8 字节魔数 `{0x7F, 'T', 'i', 'l', 'e', 'I', 'R', 0x00}`（L195）+ 1 字节 major + 1 字节 minor + 2 字节 tag，全部小端定宽，合计**正好 12 字节**。版本字段类型来自 `BytecodeVersion`（Version.h:35-41：`uint8_t` major / `uint8_t` minor / `uint16_t` tag），`writeLE` 三连（L197-199）依次写出。tag 字段当前恒 0，是为 250.x 之类实验版本预留的第三维。

写头之前有一道版本闸门（L184-194）：请求的目标版本若低于 `kMinSupportedVersion` 直接报错并打印合法区间——Writer 从源头保证不产出自己都不认识的版本号。

### 2.3 Section 头与 0xCB 对齐（L208-221）

每个 Section 由 `writeSectionHeader` 开头：1 字节 `idAndIsAligned`——**低 7 位是 Section ID，最高位是"有无对齐"标志**；随后 varint 长度；若对齐 >1，再补 varint 对齐值并对齐填充（L211-219）。填充字节统一为 `kAlignmentByte = 0xCB`（BytecodeEnums.h:26）。读端扫描时靠高位标志决定是否多读一个 varint，格式因此保持紧凑：无对齐需求的节（如 Producer，L1760 显式传 `alignment=1`）一个字节的头就能装下。

**勘误（以源码为准）**：文件顶部的格式总览注释有两处与实现不符——①BytecodeWriter.cpp:49-50 说头是 `magic[8] + version[varint]`，实现实为 12 字节定长（varint 根本没用于版本字段）；②BytecodeWriter.cpp:56 注释说 padding 字节是 **0xCF**，而代码实际填充 `kAlignmentByte = 0xCB`（BytecodeEnums.h:26，Reader 侧校验也按 0xCB）。0xCF 是注释笔误，读代码时以枚举常量为准。

### 2.4 五个 Section Manager

**StringManager（L255-307）**：`llvm::MapVector` 按 StringRef 去重并发号。节格式为 `numStrings[varint] + 4 字节对齐 + offsets[uint32×N] + 字符串数据`（L245-251 注释）。offset 表先全部写 0 占位（L266-268），字符串数据流式写完后用 `std::copy_n` 直接覆写回预留槽（L293-295）——避免了两遍扫描。对齐取 `alignof(uint32_t)`。

**TypeManager（L344-409）**：类型以 `getAsOpaquePointer()` 为 key 去重（L357），首次见到某类型时先递归 `registerDependentTypes`（L365）——保证嵌套类型（如 `tile<ptr<f32>>` 里的 `ptr<f32>`）在宿主之前拿到更小的索引号。节布局与字符串节同构，只是 offset 换 uint32。它还缓存 `cachedContext`（L352-355），给"序列化嵌在类型载荷里的属性"这种没有 op 句柄可用的报错路径兜底。

**ConstantManager（L548-692）**：常量池的核心决策在 `serializeAttribute`（L575 起）。最讲究的是 **i1 稠密属性的规范化**（L579-606）：上游 MLIR 对 `getRawData()` 在 i1 上曾在"位打包"与"每元素一字节"之间摇摆，两种历史形态都存在于旧字节码里；本仓选择**位打包作为 v13.4+ 起的永久规范线格式**（`kCanonicalI1Version`），并在版本低于该阈值且是 splat 时退回单字节形式兼容旧读端。非 i1 走 `getRawData()` 原始缓冲；标量 IntegerAttr 直接 `writeLE<uint64_t>`；FloatAttr 经 `bitcastToAPInt` 复用 `writeAPInt`。`writeAPInt`（L224-239）按位宽三档：≤8 位写单字节、≤64 位走 zigzag varint、更宽先写活跃字数再逐字 zigzag。节内 offset 表用 uint64、对齐取 `alignof(uint64_t)`（L658-661）——比字符串/类型节更宽，因为常量数据可能含双精度浮点。空常量数据是硬错误（L673-677）。

**DebugInfoWriter（L836 附近）**：调试信息（DICompileUnit/DIFile/DILoc 等，见 BytecodeEnums.h:43-50 的 DebugTag）挂靠字符串节复用去重。`FunctionTableWriter::writeOperation` 里每个 op 都会 `addDebugInfo` 登记位置（L1117-1120），写节前还有 `validateDebugInfo` 预校验。

**FunctionTableWriter（L1084-1631）**：唯一有控制流的 Manager。`writeOperation`（L1089-1133）是逐 op 序列化的骨架：先查 `Bytecode::getOpcodeMap()` 拿操作码——查不到即报"missing from BytecodeOpcodes.td"（L1090-1092），这正是第 1 篇"新增 op 必须登记操作码"纪律的执行点；再过 `isOpcodeAvailableInVersion` 版本闸门（L1096-1101），保证不会把 13.4 的 op 写进 13.1 文件。一个精妙细节在 L1124-1131：**只有真正被序列化的结果才进 `valueIndexMap`**——版本兼容裁剪掉的 result 不占索引号，否则 Reader 侧 SSA 编号会错位。函数元数据写入时（L1500-1537），`entryFlag` 一字节打包三个标志位：bit0 VisibilityPrivate、bit1 KindKernel、bit2 HasOptimizationHints（定义在 BytecodeEnums.h:61-68）；优化提示属性仅在 kernel 入口存在时跟随写出（L1530-1535）。函数体先写进局部 buffer 量出长度再入流（L1539-1543），region/block 递归结构为 `numBlocks[varint] + block*`（L1547 起）。

**Producer 节（L1733-1768）**：版本条件节——13.3 之前根本不写（L1735-1739）；模块没有 producer 属性也跳过。内容仅一个字符串索引（L1752），不参与对齐。

### 2.5 顶层编排 writeBytecode（L1770-1831）

入口先做两道校验：标准 `verify(module)`（会顺带执行 -Wunsupported-hints 之类方言诊断，L1773-1776）和 `verifySelfContainedModuleAndOperationInvariants`（L1780-1783）——**自包含性检查**是序列化的前置硬约束：模块若还有外部依赖（如外部函数引用）就无法落盘。然后建头、实例化五个 Manager、按固定顺序写七节，最后写 1 字节 `EndOfBytecode`（0x00，L1830）收尾。空常量池时 ConstantManager 直接跳过整节（L640-643），所以最小合法文件只有：头 + 若干节 + 结束符。

## 三、外部连接

依赖侧：`BytecodeEnums.h`（Section/标志/对齐常量+生成物 include）、`Common/VersionUtils.h`（版本闸门）、`BytecodeVerification.h`（自包含校验）、方言的 Ops.h/Types.h/Attributes.h。被用侧：公共 API `writeBytecode`（BytecodeWriter.h）被 `cuda-tile-opt`/工具链和 Python 绑定（`python/Dialect/DialectCudaTile.cpp` 的 `_cuda_tile` 模块）调用；生成的 `AttrBytecode.inc`/`TypeBytecode.inc`（第 6 篇 tblgen 产物）通过 `GEN_*` 宏被本文件 include，`dispatchOpWriter` 与 `serializeType` 的 switch 骨架就在那些生成物里。Reader（第 3 篇）是它的逆过程，两端共享 BytecodeEnums.h 的全部常量。

## 四、数据流

一次 `writeBytecode(os, module, version)` 的完整旅程：

1. **校验**：verify → 自包含检查，任一失败立即返回；
2. **建头**：12 字节（magic 8 + 版本 4）先落流；
3. **收集期**：`FunctionTableWriter.buildFunctionMap` 遍历模块（L1799-1801），每个函数的名字进 StringManager、签名进 TypeManager、常量进 ConstantManager、每个 op 的类型/属性同样入池，同时 SSA 值按序列化顺序编入 `valueIndexMap`；
4. **Global 节**先写（模块级符号）；
5. **Func 节**写出函数表：每函数（名字 idx、签名 idx、entryFlag、调试 loc、优化提示、定长函数体）；
6. **Constant→Debug→Type→Producer→String** 依次落盘，节头携带长度与对齐；
7. **0x00 结束符**。

反序列化端只需先读 String 节即可解析其余一切（所有引用都是池索引），但注意 Writer 故意把 String 节写在**最后**（L1822-1824）——Reader 是流式跳到对应节随机解析的，写出顺序对它无关紧要，对 Writer 却是"收集完成度"的自然序。

## 五、设计决策

**为什么自造格式而不用 MLIR 通用 bytecode？** Tile IR 需要跨工具链稳定（driver/JIT/python 端各自链接不同 MLIR 版本都可能读它），通用 bytecode 格式随 LLVM 版本演化。自造 12B 头 + 冻结操作码的格式把稳定性抓在自己手里。i1 位打包规范化（L579-596 注释直言"both forms appear in legacy bytecode"）就是这种独立性的直接收益：宁可自己定义线格式，也不继承上游的摇摆。

**为什么 offset 表先占位后回填？** 避免"先量尺寸再写"的两遍序列化。代价是 Manager 必须在内存 buffer 里攒完整节再一次性入流（全部节都走 `SmallVector<char>` 中转），换来实现简单与 offset 计算零重复。

**为什么 ZigZag 只用于有符号语义字段？** 操作数索引、池索引天然非负用 varint 即可；APInt 字、有符号常量才走 zigzag。编码选择与值域语义一一对应，不为统一而统一。

**为什么 entryFlag 只留三位且配公共掩码？** `kPublicFunctionFlagsMask`（BytecodeEnums.h:71-75）注释写明用途：读端用它**拒收设置了未知位的文件**——这是"不同厂商编译器产出的字节码不得静默流入"的跨厂商兼容闸门（第 3 篇展开）。Writer 侧的配合纪律就是：新增标志位必须同时扩掩码。

## 六、新人提示

1. **改格式先过兼容关**：任何 Section 布局、编码原语、12B 头的改动都会立即破坏新旧互读。安全的演化路径只有：新 op 追加操作码、新节类型追加枚举（NumSections 之前）、新版本号走 BytecodeVersion 三元组。
2. **两处注释笔误要心里有数**（见 2.3 勘误）：格式总览里 `version[varint]` 与 `0xCF` 都与实现不符。以 writeHeader 的 writeLE 三连和 `kAlignmentByte=0xCB` 为准，不要照注释写解析器。
3. 加新常量类型时改 `ConstantManager::serializeAttribute` 的 dyn_cast 链即可，但想清楚：它必须能被 Reader 的对应分支精确逆变换，且 i1 那样的规范化版本分界（kCanonicalI1Version）要不要参与。
4. `valueIndexMap` 的"只索引已序列化结果"规则（L1124-1131）是版本裁剪正确性的命门：给 op 加可裁剪 result 时，务必确认 dispatchOpWriter 返回的"实际序列化数"仍然准确。
5. Section 写出顺序改了通常无害（Reader 按节 ID 找），但 Global 必须在 Func 之前、所有池节（String/Type/Constant）必须在函数体引用它们之前**收集**完成——两段式结构别拆。
6. 调试本文件时，十六进制 dump 头 12 字节即可快速定版本：`xxd -l 12 file.tilebc`，第 9-10 字节就是 major.minor（小端）。
