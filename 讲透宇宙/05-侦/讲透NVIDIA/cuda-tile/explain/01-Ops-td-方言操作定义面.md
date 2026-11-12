# 01 · Ops.td —— CUDA Tile 方言的 107 项操作定义面

> 文件：`include/cuda_tile/Dialect/CudaTile/IR/Ops.td`（5710 行）
> 配套：`Dialect.td`（基类与参数包装）、`BytecodeOpcodes.td`（操作码冻结表）

## 一、角色定位

Ops.td 是整个 CUDA Tile IR 的"宪法"。每一门 IR 方言都要回答三个问题：有哪些操作（op）、每个操作接受什么类型、语义约束是什么——在本仓库里，这三个问题的答案全部以 TableGen 记录的形式写在 Ops.td 中，再由 `tools/cuda-tile-tblgen`（见第 6 篇）翻译成 C++ 的 `Op` 类、Python 绑定、规格文档乃至字节码序列化代码。可以说 Ops.td 是单一事实源（single source of truth）：改一个操作定义，会同时改变 C++ IR、文本语法、文档和 .tilebc 线格式四个面。

文件组织非常朴素：按操作 mnemonic 的字母序从 `absf` 排到 `while`，每个 op 一段 `//===--- XxxOp ---===//` 横幅。文件头（Ops.td:13-27）先 include 上游 MLIR 的基础设施（`BuiltinAttributes.td`、`OpBase.td`、`ControlFlowInterfaces.td` 等），再 include 本方言的 `Dialect.td`/`Interfaces.td`/`Types.td`/`AttrDefs.td`。Ops.td:29-31 有一个条件开关：`#ifdef TILE_IR_INCLUDE_TESTS` 时追加引入 `TestingOps.td`——这是字节码版本演化测试的专用通道（250.x 假版本号），仅测试构建存在，不污染公共定义面。

## 二、内部结构

### 2.1 十个分组基类：分组不靠位置，靠继承

Ops.td 里没有"分组区块"，分组信息编码在基类名里。基类全部定义在 Dialect.td:183-220：`CudaTileBitwiseOpDef`、`CudaTileIntegerOpDef`、`CudaTileFloatingPointOpDef`、`CudaTileAtomicsOpDef`、`CudaTileConversionOpDef`、`CudaTileCoreOpDef`、`CudaTileControlFlowOpDef`、`CudaTileMemOpDef`、`CudaTileViewOpDef`、`CudaTileMiscOpDef`，每一个都只是给公共基类 `CudaTileOpDef`（Dialect.td:102）填了不同的 `group` 字符串。统计下来十组分布为：

| 分组 | 操作数 | 代表 op |
|---|---|---|
| Floating Point | 30 | `absf`/`addf`/`mmaf`/`exp2`/`atan2` |
| Core | 20 | `constant`/`entry`/`module`/`global`/`pack`/`insert` |
| Integer | 14 | `addi`/`cmpi`/`absi`/`mmai` |
| Conversions | 9 | `bitcast`/`ftof`/`ftoi`/`itof`/`inttoptr` |
| Views | 8 | `load_view_tko`/`store_view_tko`/`make_tensor_view` |
| Control Flow | 8 | `for`/`loop`/`if`/`break`/`continue`/`return` |
| Memory | 6 | `alloca`/`load_ptr_tko`/`store_ptr_tko` |
| Miscellaneous | 4 | `assume`/`get_tile_block_id` 等 |
| Bitwise | 3 | `andi`/`ori`/`xori` |
| Atomics | 3 | `atomic_cas_tko`/`atomic_rmw_tko`/`atomic_red_view_tko` |

合计 105 个具体操作；文件里 `^def CudaTile_` 共 107 项，多出的 2 项是 `FmaTile`、`PowIExponentTileType` 这类服务于单个 op 的辅助类型 def（挂在宿主 op 定义旁），不是独立操作。Memory 组还有一层内部复用：Ops.td:2978 的 `class CudaTile_LoadOpBase` 与 Ops.td:4746 的 `class CudaTile_StoreOpBase` 把 load/store 族的公共骨架抽出，`load_ptr_tko`（Ops.td:2999）和 `store_ptr_tko`（Ops.td:4763）经由它们定义——这是全文件仅有的两个"中间基类"。

`CudaTileOpDef` 基类本体（Dialect.td:102-115）在 MLIR `Op` 之上挂了四样方言私货：`operationVersion`（该 op 最早出现的 CUDA 版本，如 "13.1"）、`mlirExamples`（会进规格文档的可执行示例）、`descriptionTables`（文档表格）和 `CudaTileOpMetadata`（版本+分组+子组的打包元数据，Dialect.td:95）。这个 `operationVersion` 字段是后面字节码版本分析的原始输入——版本号不是写在 C++ 里，而是写在 op 定义上，让 tblgen 全链路自动传播。

### 2.2 版本分布：一个 13.2、七个 13.3、五个 13.4

对全部 105 个操作按 `operationVersion` 统计：90 个生于 13.1（基线），之后的增量是——

- **13.2 仅 1 个**：`atan2`（Ops.td:369，浮点二元数学函数补齐）；
- **13.3 共 7 个**：`alloca`（Ops.td:265）、`atomic_red_view_tko`（Ops.td:655）、`mmaf_scaled`（Ops.td:1593）、`pack`（Ops.td:3915）、`unpack`（Ops.td:5155）、`make_strided_view`（Ops.td:5259）、`make_gather_scatter_view`——主题非常集中：**NVFP4/MXFP8 缩放 MMA + gather/scatter/strided 视图 + 子字节 pack/unpack**，正是 Blackwell 代硬件能力在 IR 层的投影；
- **13.4 共 5 个**：`insert`（Ops.td:1789）、`memory_fence_alias_tko`（Ops.td:3840）、`fpowi`（Ops.td:4041）、`gdc_launch_dependents_tko`（Ops.td:5613）、`gdc_wait_tko`——主题是 **PDL（programmatic dependent launch）依赖启动与内存序别名**，即 CUDA 12.8 引入的 grid dependency control 在 IR 层的对应物。

这张增量表直接决定了 BytecodeOpcodes.td 尾部的追加段（见 2.4）和 MinVersionAnalyzer 的判定输入（第 5 篇）。

### 2.3 代表性 op 精讲

**ConstantOp（Ops.td:1188）——最常用的 op。** trait 上挂了 `ConstantLike`、`Pure` 和 `AllTypesMatch<["value","result"]>`（值与结果同型）。它有双形态：标量溅射 `<i32: 0>` 与稠密列表 `<i32: [0,1,2,3]>`，由 `Builtin_DenseTypedElementsAttr` 属性承载。注意 `assemblyFormat` 用的是 `custom<DenseTypedElementsAttr>` 定制指令而非默认属性打印——因为 Tile 方言的常量打印语法（`<D: c>`）是自造的，还带 `# ` 前缀注释对齐的示例（Ops.td:1208-1218）。`hasFolder = 1` 说明它在 CudaTile.cpp 里有常量折叠 canonicalization。

**ForOp（Ops.td:1986）——结构化循环。** trait 密度全文件罕见：`AutomaticAllocationScope`、两组 `AllTypesMatch`、`RecursiveMemoryEffects`、`SingleBlockImplicitTerminator<"ContinueOp">`。语义是半开区间 `[lb, ub)` 步进循环，归纳变量按**有符号**比较终止，可用 `unsigned` 单元属性切成无符号（Ops.td:2035 附近文档）。循环携带变量经 `iter_values` 传入、`continue` yield 回传；文档明确警告携带变量不能是 view 类型、`for` 不允许提前 break 出口（Ops.td:2043-2045 的 warning 块）——这是 Tile IR "结构化控制流"哲学的直接体现：牺牲一点表达力，换取可静态分析的循环体。

**MmaFOp（Ops.td:1497）——数值核心。** 三操作数 MMA：`lhs × rhs + acc`，2D 普通或 3D 批量。三个自定义 trait（`AllElementTypeMatch`、`AllRanksMatch`）约束操作数族；输入输出合法组合不用文字描述而用 `descriptionTables` 里的真表格（f8E4M3FN→f16/f32、bf16→f32、tf32→f32…，Ops.td:1516-1530）——这份表格会直接进规格文档。有趣的是 13.3 才加入的 `fast_acc` 单元属性（Ops.td:1585）：**同一 op 在 13.1 定义，13.3 给它追加了一个可选属性**——op 级版本和参数级版本是独立的两个维度，这正是版本分析器要逐参数处理的原因。其姊妹 `MmaFScaledOp`（Ops.td:1593，13.3）用三个专门的 `CudaTile_TileOf` 辅助约束（OperandTileType/ScaleTileType/ResultTileType，Ops.td:1553-1567）把 FP8E4M3FN/E5M2/FP4E2M1FN 输入、E8M0/E5M3FNU 缩放、f32 输出钉死——MXFP4 缩放乘法的类型面完全由 TableGen 声明式表达。

**LoadViewTkoOp（Ops.td:2780）——视图消费端。** 从视图取一个 tile，索引操作数按无符号解释。最有分量的是 `inbounds` 属性（描述见 Ops.td:43-51 的 `inbounds_desc` defvar）：每索引维一个 bool，`true` = 用户向编译器立保证"该维坐标必在界内"（违反即 UB），`false` = 保守按可能越界处理；文本格式可省略，parser 自动合成全 false 向量。这是一个把越界检查从运行时搬到编译期契约的典型设计。文档还钉死了对齐要求：底层数据指针必须按元素字节大小对齐（子字节类型向上取整到整字节，Ops.td:2820-2825 的 note）。

**结构三件套：ModuleOp/EntryOp/GlobalOp。** `module`（Ops.td:3594）是序列化的根单元（字节码一模块一文件）；`entry`（Ops.td:2300）是函数入口（带 `# entry @name(...) { # }` 的特殊文本语法）；`global`（Ops.td:2477）挂 `Symbol`/`SymbolName` trait 做模块级符号。三者合起来构成 Tile IR 的"程序外壳"。

### 2.4 操作码冻结表：BytecodeOpcodes.td 的 0x19-0x24 跳洞

操作码不靠 tblgen 自动分配，而是显式冻结在 `BytecodeOpcodes.td`（Ops.td 的姊妹文件）。其结构：`BytecodeOpcode<op, int>` 基类（BytecodeOpcodes.td:27-30）+ `PublicOpcode`（32）标记公共构建可见 + `OpcodeRange` 划定合法区间——公共操作限 `0x0-0xFFF`（BytecodeOpcodes.td:44），测试操作限 `0x3000-0xFFFFFFFF`（46，且仅 TILE_IR_INCLUDE_TESTS 构建）。支持的字节码版本四挡：13.1/13.2/13.3/13.4（BytecodeOpcodes.td:55-58）。

分配表按 mnemonic 字母序连续编号，从 `absf`=0x0 到 `memory_fence_alias_tko`=0x7A（BytecodeOpcodes.td:72-176）。头部的注释把纪律写得斩钉截铁："**FROZEN for backward compatibility** … must never be renumbered"（BytecodeOpcodes.td:67-71）。表中有两处显式跳洞：

- **0x19-0x24**：`exp2` 是 0x18（BytecodeOpcodes.td:96），下一个 `exti` 直接跳到 0x25（97），中间 12 个码位空洞；
- **0x34-0x39**：`inttoptr`=0x33（111）之后 `iota` 直接从 0x3A 起（112），6 个码位空洞。

文件对两处空洞**没有留下任何注释**。按字母序推断，0x19-0x24 段本应落在 exp2 与 exti 之间的操作（可能曾存在后被删除的实验性 op），但无论历史如何，冻结表的语义是明确的：**空洞码位与已分配码位同等冻结，永不复用**——因为任何旧版本 .tilebc 文件里若曾出现这些码位，新读端把它们解释成别的 op 就是静默数据损坏。这比"未用可回收"的直觉强得多，是二进制格式向后兼容的经典处置。另一个值得注意的规律：13.3/13.4 新增的 12 个 op 全部追加在表尾 0x6F-0x7A 段（BytecodeOpcodes.td:165-176），印证了"只追加、不改写"的演化纪律；测试 op 则整体放逐到 0x3000+（BytecodeOpcodes.td:180-182），与公共空间物理隔离。

## 三、外部连接

上游依赖（Ops.td:13-22）：MLIR 的 `OpBase.td`（Op/ trait 体系）、`BuiltinAttributes.td`（Dense 元素属性）、`ControlFlowInterfaces.td`（RegionBranchOpInterface）、`SideEffectInterfaces.td`（Pure/MemoryEffects）、`FunctionInterfaces.td` 等。方言内部（Ops.td:24-27）：`Dialect.td` 提供基类与 `CudaTileArg`；`Types.td` 提供 tile/tensor_view/pointer 类型约束；`AttrDefs.td` 提供枚举与结构属性；`Interfaces.td` 提供方言接口。

下游消费方向有五条：① `lib/Dialect/CudaTile/IR/CudaTile.cpp`（第 4 篇）由 `-gen-op-decls/-gen-op-defs` 生成的声明实现 verify/canonicalize/print；② `tools/cuda-tile-tblgen` 的 BytecodeGen.cpp 读它生成序列化/反序列化 C++；③ `python/cuda_tile/dialects/CudaTileOps.td` 是一层"壳"，只 include 本文件再交给 mlir-tblgen 的 Python 绑定后端；④ SpecGen 读 `mlirExamples`/`descriptionTables` 生成方言规格 Markdown；⑤ TestingOps.td 在测试构建下扩展它做版本演化演练。

## 四、数据流

Ops.td 是 TableGen 源，不直接执行，但它定义的数据流骨架是全仓的模板：一个 `cuda_tile.module` 根下挂若干 `entry` 与 `global`；entry 内部 SSA 值全部是 tile 类型；数据经 `make_tensor_view`/`make_strided_view` 等把指针包成视图，`load_view_tko` 按索引从视图取出 tile；计算用元素级算术、`mmaf` 族做矩阵乘；`for`/`loop` 做循环携带；最后 `store_view_tko` 写回。`_tko` 后缀（tile kernel op）标记出现在 kernel 边界可见的操作（原子、栅栏、PDL）。

版本元数据流：每个 op 的 `operationVersion` + 每个参数上 `CudaTileArg` 的第三模板参（如 Ops.td:97 的 `"13.1"`、Ops.td:1585 的 `"13.3"`）→ tblgen 抽取进 `AttrBytecode.inc`/`TypeBytecode.inc` 相邻的 op 字节码生成物 → BytecodeWriter 写盘时逐 op 查表 → MinVersionAnalyzer 遍历 IR 时反向求"最早可序列化版本"。

## 五、设计决策

**为什么分组靠基类而非文件区块？** 因为同一分组的信息要被三个下游消费：规格文档按 group 分章、字节码生成按组无关处理、Python 绑定按 op 平铺。把 group 做成基类字段（而非注释或文件位置），让任何工具都能程序化取用，文档结构永不与代码漂移。

**为什么操作码手写冻结而不自动分配？** 自动分配对编译器友好但对二进制格式是灾难——tblgen 记录顺序一变全部重排，旧 .tilebc 全部作废。显式冻结表把"格式"从"编译器内部表示"中解耦：这就是为什么删除 op 只能留洞、新增只能追加到尾部。跳洞的存在本身就是这套纪律的化石证据。

**为什么版本号写在 op/参数定义上？** 让"这个功能什么时候引入"与"这个功能是什么"在同一行维护，避免 C++ 侧一张漂移的版本表。代价是 TableGen 语法要为此扩展 `CudaTileArg` 这类包装（Dialect.td:263），但收益是版本信息可被 tblgen、分析器、文档生成器统一消费。

**为什么常量/类型打印全走 custom 指令？** Tile 方言的文本格式（`# entry`、`<i32: 0>`、`tile<4x8xf16>`）有意与 MLIR 通用风格区隔，贴近 CUDA 用户的直觉；`custom<>` 指令让 parse/print 的实现留在 CudaTile.cpp 手工控制（SharedFuncParserAndPrinter.h 复用），而不是让 declarative assembly format 硬凑。

## 六、新人提示

1. **新增 op 的检查单**：在 Ops.td 按字母序插入定义（选对分组基类、写 `operationVersion`）；**必须**同步在 BytecodeOpcodes.td 表尾追加新码位（当前最高 0x7A，公共段上限 0xFFF）；新参数若晚于 op 本体引入，记得写参数级版本。漏掉操作码分配会让 BytecodeGen 的唯一性校验（见第 6 篇）直接报错，这是设计好的防线而非麻烦。
2. **绝不改已有操作码或回收跳洞**（0x19-0x24、0x34-0x39）。发现"这些码没人用"想复用时，先想旧文件兼容性。
3. `mlirExamples` 不是摆设——SpecGen 会把示例跑成真实测试输入，写错语法会在文档构建时炸掉；示例里的 `# ` 是行注释标记，模仿时保持对齐。
4. `descriptionTables` 的行列是文档表格的直接数据源（mmaf 的类型矩阵 Ops.td:1516-1530），改类型支持时记得同步这张表，否则规格文档说谎。
5. 注意 `CudaTileUnusedArg`（Dialect.td:269）：这个包装专用于"语法上存在但方言暂不处理"的参数（如某些 hint），它和 `CudaTileArg` 在生成代码里待遇不同，选错包装会让参数静默失去版本追踪。
6. 本篇与任务简报口径的一处出入：简报称"107 op"，源码 `^def CudaTile_` 确为 107 项，但其中 `FmaTile`/`PowIExponentTileType` 2 项是辅助类型 def，具体操作为 105 个（90 直接组定义 + load/store 两族经中间基类）；本文按源码口径注明，以源码为准。
