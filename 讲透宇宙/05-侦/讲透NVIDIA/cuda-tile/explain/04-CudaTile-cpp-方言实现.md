# 04 · CudaTile.cpp —— 6400 行方言实现巨文件

> 文件：`lib/Dialect/CudaTile/IR/CudaTile.cpp`（6400 行，全仓单文件之最）
> 配套头：`Ops.h`/`Attributes.h`/`Types.h`（tblgen 生成声明的手工实现侧）、`SharedVerifiers.h`（跨 op 复用验证器）、`SharedFuncParserAndPrinter.h`

## 一、角色定位

Ops.td（第 1 篇）用声明式语法定义了 105 个操作"是什么"，CudaTile.cpp 则回答"怎么落地"：所有无法声明表达的部分——文本格式的 parse/print、语义校验 verify、常量折叠 fold、规范化 canonicalize——全部手工实现在这一个文件里。它同时是方言门面：`CudaTileDialect::initialize()`（CudaTile.cpp:6392-6400）注册全部属性、类型、操作（经 `Ops.cpp.inc` 生成物）和两个接口（inliner、OpAsm）。粗略统计文件内分布着约 50 个 `::verify()`、10 余个 `fold`、一个 8-pattern 的 canonicalize 家族和 20 余对手写 parse/print——这使它成为"读 IR 文本报错时第一个要打开的文件"。

文件大体按字母序组织（与 Ops.td 同步），但开头是公共层：匿名 namespace 里的函数签名解析工具（CudaTile.cpp:84-330）、稠密属性编解码（331-1105）、region 参数解析（1106）、调试信息验证器（1205-1330），之后才是逐 op 的三件套区块。

## 二、内部结构

### 2.1 稠密常量的完整生命：parseDenseTypedElementsAttr（L381-655）

这是全文件最精致的解析器，支撑 `constant <i32: [0,1,2]>` 语法。流程：`<` 开局 → 解析前缀元素类型（错误信息穷举 15 种合法元素类型，L388-405）→ `isValidDenseElementType` 白名单校验 → 冒号后进入递归数组解析。三个巧思：

- **整型先收 int64 再 `validateIntegerBounds`（L335 起）**：不信任词法层的字面量宽度，统一进 int64 后按目标位宽复核，超界报错带精确位置；
- **浮点直接用目标语义解析**：`parser.parseFloat(targetSemantics, ...)`（L448-452）把 f16/bf16/f64 的舍入在解析期就做对，而不是先收 double 再转（那会引入双重舍入误差）；
- **形状随解析推断**：`parseNestedArrayWithShape`（L466 起）递归下降时同步维护 `inferredShape`，解析完成即得到形状与溅射标志，随后 L621-655 按"标量溅射/一维/多维/空数组"四种形态分派构造 `DenseTypedElementsAttr`。

打印侧 `printDenseTypedElementsAttr`（L657-685）与之严格互逆；`*NoResult` 两个包装（L687-695）服务无结果类型上下文（如 global 初始化器）。

### 2.2 公共验证器层：SharedVerifiers.h 的模板复用

大量 op 共享同一类语义检查，抽成了头文件内联模板：`verifyFtz`（SharedVerifiers.h:127，flush-to-zero 只对 f32/f64 合法）、`verifyAlloca`（H:210）、`verifyIEEERoundingModes`、`verifyMmaShapes` 等。典型如 `AddFOp::verify()`（CudaTile.cpp:1540-1545）只有两行——rounding 模式合法性 + ftz 检查，其余交给 trait。这种"trait 管结构、模板管语义、op::verify 只做编排"的三层分工是全文件的主旋律，也是它能把 6400 行维持住可读性的根本原因。同文件还有 op 专属的通用版：`verifyMemoryModelLoad`（L3956 起）集中裁决 load 族的内存序组合——WEAK/RELAXED/ACQUIRE 合法、WEAK 禁带 scope、RELAXED/ACQUIRE 必带 scope（L3960-3986），三个 load 变体（L4572/4594 等）全部委托给它。

### 2.3 MmaFOp::verify：类型矩阵的运行时执法（L2458-2518）

第 1 篇讲过 mmaf 的合法输入输出组合写在 Ops.td 的 `descriptionTables`（文档表格），但文档不执法——执法在这里：`AllowedMMAType` 数组逐一列出 f4E2M1FN/f8E4M3FN/f8E5M2→{f16,f32}、bf16/tf32→f32、f32→f32、f64→f64 八行组合（L2469-2494），先 `verifyMmaShapes` 查 2D/3D 矩阵形状契约，再查 acc 元素类型落在允许集合。报错信息把"期望集合 vs 实际类型"完整打出。注意注释"Types must be created with context, so array can't be static"（L2467-2468）——MLIR 的 uniquing 类型不能用静态常量数组缓存，这是 MLIR 上下文模型的直接后果。**改类型支持时 Ops.td 表格与此处数组必须同步**，两处真源。

### 2.4 控制流三巨头的手写解析与折叠

**ForOp**：`verifyRegions`（L2808 起）委托 `verifyLoopIterValues`（L2717）检查迭代值类型/数量一致；print/parse（L2830/2846）实现 `(lb to ub, step)` 区间语法与 `iter_values` 绑定。**LoopOp**（通用 while 型）同构（L4609/4638）。**IfOp** 是折叠重镇：`getCanonicalizationPatterns`（L3906-3910）注册整整 8 个 pattern——`RemoveUnusedResults`（L3465）、`ReplaceYieldWithValue`（L3536）、`RemoveStaticCondition`（L346 附近，常量条件直通内联分支）、`ConvertToSelect`（L3371，两端单值 if 转_select 指令级选择）、`RemoveEmptyElseBranch`（L3746）、`CombineIfs`（L3596，串联 if 合并）、`CombineNestedIfs`（L3770）、`MoveTerminatorToParent`（L3885）。公共工具 `replaceOpWithRegion`（L3290-3305）负责"把单块 region 内联到 op 位置并重接 yield"，是前四个 pattern 的共享骨架。`IfOp::fold`（L3318）再补一手直接常量折叠。这套 if 简化器是下游编译器（pattern 匹配做 fusion/locality）的地基。

**AddFOp::canonicalize 的代表性小招**（L1566-1572）：交换律规范化——若 RHS 是乘法而 LHS 不是，则交换两操作数，把乘法固定到 LHS。注释直言目的："enables FMA fusion patterns to work more reliably"——一条看似无害的规范化，实为 FMA 融合的匹配前提。

### 2.5 EntryOp：函数外壳的定制解析（L3042-3165）

EntryOp 的签名不走 MLIR 标准 `function_interface_impl`，而是自家 `parseFunctionSignatureWithArguments`（L239 起）——为的是在 `cuda_tile.module` 默认方言上下文里同时支持短形 `tile<ptr<f32>>` 与长形 `!cuda_tile.tile<ptr<f32>>`（L3051-3056 注释）。优化提示属性解析（L3093-3110）体现规范化思想：**显式空形式（`optimization_hints = {}`）与无属性语义等价，解析期直接归一化掉**，保证内存 IR 只有单一规范形态、字节码往返稳定。`EntryOp::verify`（L3139）还挂了调试信息双验证（见 2.6）。

### 2.6 DebugInfoVerifier：调试信息的六条铁律（L1205-1330）

一个纯静态类，`verifyFunc`/`verifyFuncBody`/`verifyModule` 三入口被 EntryOp（L3150/3156）与 ModuleOp（L5255 附近）调用。规则编号直写在注释里：函数位置不得是 CallSiteLoc（Rule 6，L1210-1214）、函数 scope 必须是 di_subprogram（Rule 1）、函数名必须与 subprogram linkage name 一致（Rule 2）等。这是**序列化前的语义级质检**——BytecodeWriter 的位置流（第 2 篇）要求调试信息结构规范，这里在 IR 层提前把不合格形态拦下，而不是等到字节码层报晦涩错误。

### 2.7 视图族的共享解析骨架（L4020-4600）

`_tko` 视图操作（load/store/atomic_red）共享 `ViewTkoParseState`（L4121）与 `finalizeViewTkoParse`（L4152）——inbounds 属性省略时合成全 false 向量（第 1 篇讲的契约在 L4347 附近注释明确"cannot be smuggled"，防属性字典走私绕过校验）。`MakeTensorViewOp`/`MakePartitionViewOp`/`MakeStridedViewOp`/`MakeGatherScatterViewOp` 四个 13.1/13.3 视图构造器各有定制 print/parse（L4683/5064/5120/5176）。

## 三、外部连接

上游：mlir/IR 的 OpAsmParser/OpAsmPrinter/PatternRewriter/Verifier。方言内：`Ops.cpp.inc`/`Ops.h.inc`（tblgen 生成，声明本文件实现的类）、`SharedVerifiers.h`/`SharedFuncParserAndPrinter.h`（共享内联工具）、Attributes.h 的 OptimizationHintsAttr/DenseTypedElementsAttr 等自定义属性（其 parse 在 L1023-1045 经 DivByAttr/SameElementsAttr/BoundedAttr 复用链组装）。被用侧：BytecodeWriter/Reader 不直接调它（字节码不经过文本层），但 `CudaTileDialect::initialize` 注册的一切是两者能工作的前提；Python 绑定与 cuda-tile-opt 的文本 round-trip 全靠这里的 parse/print；canonicalize/fold 被 greedy pattern rewrite 在 pass 管线中驱动。

## 四、数据流

以一条 `# entry @k(%p: tile<ptr<f32>>) { ... }` 文本的旅程为例：EntryOp::parse 拿到符号名 → parseFunctionSignatureWithArguments 逐参数解析短形类型（转而调用类型解析器，Types.h 侧）→ 组装 FunctionType/argAttrs → 可选 optimization_hints 归一化 → region 体里每个 op 经各自 parse 重建。verify 管线（全模块 verify 时）逐 op 触发：trait 先行、SharedVerifiers 次之、op::verify 收尾、EntryOp/ModuleOp 额外跑 DebugInfoVerifier。优化管线中 getCanonicalizationPatterns 的 8 个 if pattern + 各 op fold/canonicalize 在 greedy driver 里迭代到不动点。打印方向则逆向走 print 家族，产出可 round-trip 的文本。

## 五、设计决策

**为什么 verify 大量模板化共享？** 105 个 op 里"ftz 只许 f32/f64""内存序组合表""inbounds 逐维 bool"这类约束是横切的，写成 op 内联会导致 50 份拷贝漂移。模板放在头文件（SharedVerifiers.h）让编译器按 op 类型实例化，共享逻辑单点维护。

**为什么文本格式 parse/print 全手写而不用 declarative format 全覆盖？** 签名双形（长/短类型名）、inbounds 可省略合成、优化提示空形式归一化、稠密属性的形状推断——全是"带语义的语法"，declarative format 表达不了。手写的代价是这个文件巨大，收益是文本层完全可控。

**为什么 canonicalize 要管操作数顺序（AddFOp 交换）？** 下游 fusion 匹配的是固定模式（mul 在左的 add）。与其让每个消费者写双向匹配，不如在规范化层统一姿态——这是"规范化即契约"的经典应用。

**为什么调试信息规则放在方言层而非 pass？** 调试信息合法性是 IR 不变量（影响序列化正确性），不是可选优化。verify 钩子保证任何来源（文本解析、字节码装载、变换产出）的模块都被同一套规则约束。

## 六、新人提示

1. **改 op 语义先找三处**：Ops.td（声明）、本文件该 op 区块（verify/print/parse）、SharedVerifiers.h（若约束可共享）。只改一处会出现"文本能解析、verify 拒收"或反向的裂缝。
2. mmaf/mmai 的类型组合表是**双真源**（Ops.td descriptionTables 与本文件 L2469-2494），扩类型支持必须两处同步改，PR 审查时这是头号检查点。
3. 手写 parse 的失败路径必须 `return failure()` 且尽量 emitError 带位置；本文件惯例是用 parser.emitError(loc)，别学某些生成物静默失败——文本 IR 用户依赖这些报错。
4. 新增 canonicalize pattern 记得挂进对应 op 的 getCanonicalizationPatterns（若 op 无此入口，Ops.td 加 `let hasCanonicalizer = 1`）；pattern 乱序添加可能到不了不动点，参考 IfOp 八件套的依赖排列。
5. 6400 行按字母序区块检索时，直接搜 `^//===` 横幅或 `XxxOp::verify` 比滚动快；op 区块与 Ops.td 定义行号无对应关系，别拿 .td 行号来这找。
6. DenseTypedElementsAttr 解析的 15 元素类型白名单（L388-405 错误文案与 isValidDenseElementType）在加新元素类型（如更新的 FP8 变体）时要三处同步：文案、校验函数、Ops.td 常量约束。
