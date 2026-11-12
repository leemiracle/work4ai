# 03 · BytecodeReader.cpp —— .tilebc 反序列化与四重校验

> 文件：`lib/Bytecode/Reader/BytecodeReader.cpp`（3044 行，全仓最大单文件）
> 头文件：`include/cuda_tile/Bytecode/Reader/BytecodeReader.h`（`isTileIRBytecode`/`getBytecodeSize`/`readBytecode` 三 API）

## 一、角色定位

BytecodeReader 是 BytecodeWriter（第 2 篇）的严格镜像：Writer 写的每个字节它都要能读回来，外加 Writer 没有的职责——**对不可信输入的防御**。.tilebc 文件可能来自任何版本的 CUDA 工具链、甚至另一家厂商的编译器，Reader 是整个流水线里唯一同时见到"格式冻结纪律"（操作码冻结表）与"外部世界"的地方，所以它的代码形态是"解析一半、校验一半"。公共 API 有三个：`isTileIRBytecode` 魔数探测（BytecodeReader.cpp:44-64）、`getBytecodeSize` 不解析内容的尺寸测量（L2810 附近）、`readBytecode` 完整反序列化（L2851-3043）。驱动/JIT 场景先探测再量尺寸再装载，三步渐进。

文件内部结构四层：`EncodingReader` 原子解码器 → 各 Section 解析函数（parseStringSection/parseTypeSection/…）→ `InstructionParser`（op 级反序列化，含生成物 dispatch）→ `readBytecode` 编排。另有 `LazyTypeTable` 提供类型的按需解析。

## 二、内部结构

### 2.1 魔数探测：两个重载的讲究（L41-64）

`kTileIRBytecodeMagic` 是 8 字节 `{0x7F,'T','i','l','e','I','R',0x00}`（L41-43），以 `\0` 结尾是刻意的。`MemoryBufferRef` 重载直接 memcmp；C 字符串重载（L53-64）则用 `strnlen(buffer, 7)+1` 构造一个恰好盖住魔数的 StringRef 再复用前者——因为魔数尾字节是 0x00，C 字符串语义下 strlen 会停在第 7 字节，strnlen 上限 7 正好不越界。这个细节让调用方可以直接传 `const char*` 而不必先知道长度。

### 2.2 EncodingReader：带护栏的 varint（L69 起）

`readVarInt`（L86-125）是 LEB128 逆变换，比 Writer 版多两道护栏：shift 超 63 位即失败（防恶意超长 varint 打符号溢出主意）、可选 `max` 参数在解码后直接上限校验并报错（L118-123）——调用方用它来约束"数量"类字段（块数、操作数个数），从源头掐死巨型分配。`readSignedVarInt` 做 zigzag 逆变换，与 Writer 的 `(v<<1)^(v>>63)` 严格互逆。每个读取函数都在 `offset >= data.size()` 时失败，任何越界读都不可能发生。

### 2.3 parseHeader：逐字节校验 + 版本拒收（L318-354）

魔数不是一次性 memcmp 而是逐字节循环比较（L321-332），好处是错误信息能精确到"第几字节不匹配、实际值是什么"——对格式考古非常有用。随后 `readLE` 三连读出 1+1+2 字节版本（L336-341），与 Writer 的 12 字节头严格对齐。版本拒收逻辑在 L342-353：`BytecodeVersion::fromVersion` 查**生成物白名单**（StaticOpcodes.inc 的 GEN_VERSION_VALIDATION，源头是 BytecodeOpcodes.td 里四个 `SupportedVersion` 记录），未知版本直接判空；再叠加 `kMinSupportedVersion`（=13.1，Version.cpp:68-72）下界检查。报错信息会同时打出文件版本与读端支持区间 `[13.1 - 13.4]`。注意**没有上界拒收**——13.4 是 kCurrentVersion（Version.cpp:46-50），更新的版本（如 13.5）压根过不了 fromVersion 白名单，白名单本身就是上界。

### 2.4 getBytecodeSize：只扫节头（L2820-2847）

这个辅助 API 的姿势值得学：挂一个吞掉所有诊断的 `ScopedDiagnosticHandler`（L2821-2824），循环只做"解析节头 → skip(length)"，不碰任何节内容，直到 EndOfBytecode 返回当前偏移即文件总长。三重防错：节头解析失败、跳越失败、同一节出现两次（`std::exchange(seenSections[...], true)` 技巧，L2842）都返回 nullopt。它的存在是为了让调用方（如 JIT 加载器）能在解析前完成缓冲区规划。

### 2.5 readBytecode 主流程：先编目、后按依赖序解析（L2851-3043）

与直觉不同，Reader **第一遍不解析任何节内容**：循环读节头、做对齐校验、把每节 payload 存进 `sectionPayloads` 数组（L2900-2947），直到 EndOfBytecode 且其后必须零剩余字节（L2884-2890）。对齐校验 `validateSectionAlignment`（L2903-2919）按节类型执行：String/Type 节的对齐必须是 `alignof(uint32_t)` 的倍数，Constant/Debug/Func 节必须是 `alignof(uint64_t)` 的倍数，Global 节对齐可变跳过校验。这组约束是 Writer 侧 Manager 对齐选择的镜像契约。节长度还要过"不超过剩余数据"检查（L2937-2942）。

第二遍才按**依赖顺序**解析：String（强制，缺席即错，L2954-2962）→ Producer（可选）→ Type → Constant → Debug → Global → Func（强制）。这就是为什么 Writer 把 String 写在文件最后也无妨：Reader 手里有全节 payload，解析顺序完全由"谁引用谁"决定——字符串表是类型解析的前置（`types.setStringTable`，L2964-2966，参数化类型要查字符串），类型表又是常量/函数的前置。

### 2.6 函数表解析与 kPublicFunctionFlagsMask 闸门（L2346-2440）

每个函数条目依次读：nameIndex、signatureIndex、**entryFlag（定长 1 字节）**、functionLocIndex、可选优化提示属性、函数体长度（L2366-2405）。最重量级的是 entryFlag 的未知位拒收（L2382-2393）：

```cpp
uint8_t allowedMask = Bytecode::kPublicFunctionFlagsMask;   // 0x07
if (bytecodeVersion < BytecodeVersion::kFunctionFlagsExtendedVersion)
  allowedMask = 0xFF;
if (uint8_t unknown = funcInfo.entryFlag & ~allowedMask) { /* 硬错误 */ }
```

这段就是**跨厂商兼容闸门**的实现。语义分两档：文件版本 < kFunctionFlagsExtendedVersion（=13.4，Version.cpp:61-65）时，位 3-4 是保留位、掩码放宽到 0xFF（老文件里可能堆了实验位，不能误杀）；版本 ≥13.4 后每一位都必须是本构建认识的（公共位仅 VisibilityPrivate/KindKernel/HasOptimizationHints 三位，BytecodeEnums.h:61-75），**任何未知位都是硬错误而非忽略**。为什么这么凶？因为这个文件可能出自另一家编译器厂商——静默忽略未知标志意味着"别人家的语义被当成我家的默认值"执行，是最危险的跨实现事故；fail fast 是唯一安全姿势。Version.h:95-103 的注释把这条契约写得非常直白。

随后按 KindKernel 位重建 entry/device 之分、按 HasOptimizationHints 位决定是否解析提示属性（L2395-2408），`applyFunctionVisibility`（L2333-2337）把 VisibilityPrivate 位映射回符号可见性。

### 2.7 InstructionParser::parseOperation：opcode 三连检（L2111-2137）

函数体内逐 op 解析的骨架：读 varint opcode → `isOpcodeAvailableInVersion` 版本闸门 → 从调试信息迭代器取 LocationAttr → 进生成物 switch（`GEN_OP_READER_DISPATCH` include BytecodeReader.inc，L2130-1332）。版本闸门的实现值得一看（Version.cpp:85-93）：它查的是**版本→最大操作码**映射——由于操作码按版本单调递增分配（第 1 篇冻结表"只追加"纪律的直接红利），"版本 v 可用" 等价于 "opcode ≤ max(v)"，一次查表搞定，无需逐 op 版本表。枚举属性侧还有对应检查 `isEnumAttrAvailableInVersion`（L1873-1878），防止 13.3 文件里出现 13.4 枚举值。操作数/结果索引在 createFunction 阶段经 `valueIndexList` 重放 SSA 编号，与 Writer 侧"只索引已序列化结果"规则对齐。

### 2.8 收尾双 verify（L3032-3043）

模块重建完成后并不直接返回：先跑标准 `verify(module)`，再跑 `verifySelfContainedModuleAndOperationInvariants`——与 Writer 入口是**同一个**函数（BytecodeVerification.h）。这构成"序列化→反序列化"的往返闭环校验：Writer 入口保证出去的模块自包含，Reader 出口保证回来的模块同样自包含，任何一侧的破坏都会在此暴露。

## 三、外部连接

依赖：`BytecodeEnums.h`（Section/标志/DebugTag 常量）、`Common/Version.h`+`Version.cpp`（六个版本常量与版本→操作码映射）、`VersionUtils.h`、`BytecodeVerification.h`、方言 Types.h/Attributes.h。生成物三件：`BytecodeReader.inc`（op dispatch，由 tools/cuda-tile-tblgen 的 BytecodeReaderGen.cpp 产出，第 6 篇）、`StaticOpcodes.inc`（版本白名单/常量，BytecodeGen.cpp 产出）、Type/Attr 反序列化生成物。被用侧：`readBytecode` 被 cuda-tile 工具与 Python 绑定调用；`isTileIRBytecode`/`getBytecodeSize` 服务于流式装载与格式探测（JIT 协议里也用它识别 TileIR 输入）。

## 四、数据流

输入 `MemoryBufferRef` → EncodingReader 包一层 → parseHeader 消费 12 字节 → 节编目循环填 `sectionPayloads` → 依赖序解析：字符串先入表 → 类型表懒初始化（LazyTypeTable 记录 offset，真正用到某类型才解码，参数化类型经字符串表解析）→ 常量池逐条解码（i1 走位解包，见第 2 篇的规范化决策）→ 调试节建位置流 → Global 重建模块级符号 → Func 节逐函数：元数据四元组+entryFlag 闸门 → 函数体内 parseOperation 循环（opcode→switch→重建 op→SSA 编号重放）→ 收尾双 verify → 返回 `OwningOpRef<ModuleOp>`。全程任何一步失败都带上下文报错并整体失败，绝不产出半成品模块。

## 五、设计决策

**为什么先编目再解析？** 文件物理顺序由 Writer 的"收集完成度"决定（String 在最后），而解析依赖要求 String 最先。两遍式把物理布局与逻辑依赖彻底解耦，也让"同一节出现两次""EndOfBytecode 后还有数据"这类结构错误在解析前就能拦下。

**为什么未知标志位是硬错误而不是警告？** 字节码的跨厂商流通是这个格式的现实场景（mask 的注释直言"produced by a different compiler"）。未知语义位如果被忽略，后续解析全部建立在错误前提上，错得越晚越难查。而老版本位放宽（allowedMask=0xFF）则体现了"演进期间宽容、定型后严格"的阶段性策略——13.4 就是定型线。

**为什么版本→操作码用 max 映射而非逐 op 表？** 冻结表"只追加、不改号"的纪律（第 1 篇）保证了操作码与版本的双单调性，max 映射是这种纪律的 O(1) 兑现。代价是纪律必须守住：一旦有人改号或复用跳洞，这个查询就从正确变成静默错误。

**为什么收尾再跑一遍自包含校验？** 反序列化路径理论上不可能产生外部依赖，但这条不变量若被未来改动破坏（比如有人加了延迟解析的占位 op），只有出口校验能兜住。防御性编程在这里便宜且值得。

## 六、新人提示

1. **加新的函数标志位**：同步三处——BytecodeEnums.h 的 FunctionFlags、kPublicFunctionFlagsMask、以及决定"何时开始严格执行"的 kFunctionFlagsExtendedVersion。忘了第三处，新位在过渡期会被 0xFF 掩码放过、定型期又被当未知位拒收，两头都错。
2. **调试"unsupported opcode"类报错**时记住判定公式是 `opcode ≤ maxVersion(文件版本)`；先查 StaticOpcodes.inc 里该版本的 max 值，再对照冻结表，能立刻分清"文件版本太老"还是"操作码未登记"。
3. Reader 文件头部也有一份与 Writer 相同的格式总览注释，同样带着 `version[varint]` 与 `0xCF` 两处笔误（BytecodeReader.cpp:77、L84-85）——以 parseHeader 的 readLE 三连与 `kAlignmentByte=0xCB` 为准，别照注释实现外部解析器。
4. 改对齐规则（Writer 侧 Manager 的 alignTo）时必须同步 Reader 的 validateSectionAlignment 分组，否则自产的文件自己拒收。
5. `getBytecodeSize` 故意吞诊断——别在它里面加会 emitError 的新逻辑，它的契约是"静默探测"。反过来，需要给用户真实错误时用 readBytecode。
6. 阅读生成物 dispatch 时记住 `parse<CudaTile_XxxOp>` 函数名与 Ops.td 的 op 名一一对应；遇到解析分支与 Ops.td 定义不符，以 Ops.td 与本文件的手写骨架为准并核对 tblgen 生成器（第 6 篇）。
