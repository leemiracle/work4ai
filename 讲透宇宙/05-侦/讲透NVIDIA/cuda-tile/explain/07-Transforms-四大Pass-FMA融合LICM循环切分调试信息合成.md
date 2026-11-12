# 07 · lib/Dialect/CudaTile/Transforms/ —— 四大 Pass：FMA 融合、LICM、循环切分、调试信息合成

## ① 角色定位

Transforms 目录是 CUDA Tile IR 的"优化器弹药库"：四个独立 Pass（FuseFMA、CudaTileLICM、LoopSplit、SynthesizeDebugInfoScopes）加一个共享工具函数文件（TransformsUtils.cpp），全部通过 `include/cuda_tile/Dialect/CudaTile/Transforms/Passes.td` 的 TableGen 定义生成 Pass 基类（Passes.td:19/39/65/108 四个 `def`），再由 Optimizer 管线（见第 8 篇）按 optLevel 组装调用。它们操作的都是 cuda_tile 方言自己的 IR 结构——tile 循环（ForOp/LoopOp）、非标准控制流（IfOp 内嵌 ContinueOp/BreakOp）——因此没有一个 Pass 能直接复用 MLIR 上游的通用实现，这是本目录存在的根本理由。四个 Pass 分两类：前三个是性能变换（数值行为各有取舍），SynthesizeDebugInfoScopes 则是给前端"兜底"生成行号级调试元数据的便利 Pass。

## ② 内部结构

**FuseFMA.cpp**（112 行）是两个 `OpRewritePattern` 的贪心重写：`MulAddPattern`（FuseFMA.cpp:22）匹配 `(a*b)+c`，要求乘积 `hasOneUse()`（FuseFMA.cpp:30-31），且 addf 与 mulf 的 `rounding mode` 和 `flush_to_zero` 修饰完全一致（FuseFMA.cpp:44），才替换为单条 `FmaOp`（FuseFMA.cpp:48）；`MulSubPattern`（FuseFMA.cpp:57）处理 `(a*b)-c`，用 `createOrFold<NegFOp>` 生成 `-c`（FuseFMA.cpp:80）再拼成 FMA。Pass 驱动先注入 AddFOp 的 canonicalization patterns 重排交换律操作数，再跑融合模式（FuseFMA.cpp:104-106）。

**LICM.cpp**（147 行）文件头 40 行注释就是设计文档（LICM.cpp:9-51）：为什么不用 MLIR 标准的 `moveLoopInvariantCode`——因为 cuda_tile 循环因 IfOp 区域内的 ContinueOp/BreakOp 早退而无法实现 `LoopLikeOpInterface`（LICM.cpp:36-40）。自研实现分两层：`isHoistableOp`（LICM.cpp:72-99）检查四个条件——非 terminator（:74）、`isMemoryEffectFree` 且 `isSpeculatable`（:78，后者防止把动态除数的 divi 提出去在零次循环里引入除零）、所有操作数要么定义在循环外要么本身将被提升（:82-96）；`hoistFromLoop`（LICM.cpp:106-128）用一次 **PreOrder walk** 配 `willHoist` 集合在单遍内传递闭包，遇到嵌套 ForOp/LoopOp 返回 `WalkResult::skip`（:112）留给外层驱动。外层驱动是函数级 **PostOrder walk**（LICM.cpp:138），内循环先处理，不变量逐层外溢。

**LoopSplit.cpp**（395 行）是四件里最重的：把 `for { if (iv CMP k) {...} else {...} }` 形态按谓词翻转点拆成两个循环，消除分支。判定链是 `isSplittableCondition`（LoopSplit.cpp:108-181）：条件必须是 CmpIOp、符号性匹配 ForOp 的 `unsignedCmp` 属性（:40/:43）、归一化成 `iv <op> 不变量`（`normalizeForOpCmp`，:36-73，操作数交换时翻转谓词），再看盈利性 `isSplitProfitable`（:77-104）——then/else 块操作数达阈值或含 heavy op（Load/Store/Mma/Reduce/嵌套 If/For，:87-88）。执行在 `performLoopSplit`（:266-328）：GT/LTE 谓词分裂点 +1（:284-292）；步长非 1 时用 ceil 除法把分裂点对齐到 `lb + k*step`（:293-302）；再用 min/max 把分裂点夹在 `[lb,ub]` 内（:304-307）。`copyLoop`（:184-248）克隆循环体时，CmpOp 被替换为常量 `tile<i1>` true/false（:204-209），IfOp 只克隆选中的一侧区域，遇到 ContinueOp 即停止（:226-231）；克隆 else 侧时 then-only IfOp 直接跳过（:220-222，条件恒假时无副作用）。阈值可被三层 IR 级 hint 覆盖：if > for > entry > pass 默认值（`getSplitThreshold`，:335-345），hint 载体是 discardable attribute（`kLoopSplitThresholdAttrName`，:347-354）。

**SynthesizeDebugInfoScopes.cpp**（125 行）给没有调试信息的前端造出行表元数据：`extractFileLoc`（:27-43）递归剥 NameLoc/OpaqueLoc/FusedLoc/CallSiteLoc 取出 FileLineColLoc；无文件位置时用 `<unknown>` 兜底（:64）；每个函数造一个 `DISubprogramAttr`（:98），然后 walk 全函数把每个 op 的 Location 包成 `DILocAttr`（:100-105）；已有 DILocAttr 的函数跳过（:79）。**TransformsUtils.cpp** 只有一个函数 `updateSymbolName`（:17-73）：改符号名后，若 Location 挂着旧 subprogram，用 `AttrTypeReplacer` 把作用域内所有旧 `DISubprogramAttr` 换成带新 linkageName 的克隆（:58-70）。

## ③ 外部连接

依赖面：四个 Pass 都 include 方言的 `IR/Ops.h`；LoopSplit 额外依赖 `IR/Attributes.h`/`Types.h` 与 DenseIntElementsAttr 构造；SynthesizeDebugInfoScopes 依赖 MLIR 的 LLVMDialect 风格 DIAttr 体系。被依赖面：`Passes.h.inc` 生成的 `createFuseFMAPass/createCudaTileLICMPass/createLoopSplitPass/createSynthesizeDebugInfoScopesPass` 被 Optimizer 管线（CudaTileOptimizer.cpp:273-289）、CAPI 注册器（CudaTileDialect.cpp:722-740）、cuda-tile-opt 工具（cuda-tile-opt.cpp:54）三方消费；TransformsUtils 的 `updateSymbolName` 有配套 test pass 注册（cuda-tile-opt.cpp:56-58 的 `CUDA_TILE_ENABLE_TESTING` 分支）。测试对应 test/Transforms/ 六个文件（第 12 篇）。

## ④ 数据流

以默认 -O3 管线跑一个 kernel 为例：入口 MLIR/bytecode → canonicalize+CSE → **LICM**（PostOrder 找到最内层 ForOp，PreOrder 扫体把不变 constant/addi/muli `moveBefore` 到循环前，:123-125）→ **LoopSplit**（外层 walk ForOp、内层 walk IfOp，找到可拆条件即 `performLoopSplit` 后 `WalkResult::interrupt()` 中断本次内层扫描，LoopSplit.cpp:386）→ 再 canonicalize 扫尾。FuseFMA 默认关闭（优化级再高也不开，需显式 opt-in），因为它**非数值保持**——Passes.td:44-47 明言 "Changes rounding behavior from double-round to single-round FMA"。SynthesizeDebugInfoScopes 不在性能管线里，属按需调用的独立工序。

## ⑤ 设计决策

三个值得咀嚼的取舍：其一，LICM 用单遍 PreOrder+willHoist 替代标准实现的"迭代到不动点"（LICM.cpp:47-49），用遍历顺序换掉重复扫描，代价是注释里老实承认这依赖"定义先于使用"的 SSA 保证。其二，LoopSplit 的 splitThreshold 默认 1（任何分支都拆），但保留 hint 三级覆盖与 0=禁用的逃生门（:114 `if (!threshold) return false`），把盈利性判断权下放给前端——前端比编译器更知道热循环在哪。其三，FuseFMA 的 hasOneUse 约束（乘积被多处消费时不融合）保证了删除 mulf 的安全性（FuseFMA.cpp:52 显式 `eraseOp`），这是"融合到一半留下死乘法"这类 bug 的前置防线。

## ⑥ 新人提示

改这个目录先读 LICM.cpp 头注释（:9-51），它等于本方言"循环 IR 为何特殊"的入门课。看 LoopSplit 时抓两个不变量：两段循环的 iter_args 链式衔接（第二循环以第一循环结果为初值，:324-325），以及 CmpOp 换常量后**未选中侧整段蒸发**——测试 loop_split_if_no_else.mlir 专门钉住 then-only 的边界。诊断"为什么没融合/没提升"时，greedy rewriter 的 `notifyMatchFailure` 消息（FuseFMA.cpp:34/45）配 `-debug-only=rewriter` 是第一现场。切记 FuseFMA 会改数值结果（bit 级），任何数值回归先怀疑它是否被意外启用。源码勘误：无——本篇所有行号经 2026-11 快照核实。
