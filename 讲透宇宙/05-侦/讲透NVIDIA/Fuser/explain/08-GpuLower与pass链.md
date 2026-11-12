# 08 · GpuLower 与 lower pass 链：从 Fusion IR 到 Kernel IR

## 1. 角色定位

`csrc/device_lower/lower2device.cpp`（608 行）是 nvFuser 编译器中端的总控台。每一段 SegmentedGroup 在这里完成「Fusion IR → Kernel IR（kir）」的下沉：先把并行化、同步、谓词、索引等所有**分析**算清楚存进 `FusionInfo`，再按一张固定顺序表跑**变换 pass**，产出 `kir::Kernel`——一个已经被 IndexLowering 展平、可直接吐 CUDA 文本的循环嵌套。GpuLower 对象贯穿全程：thread_local 的 `active_gpu_lower`（`lower2device.cpp:48`）让任何 pass 都能摸到全局分析结果。

## 2. 内部结构

**pass 执行表**是本文件的灵魂：构造函数初始化列表 `passes_`（`lower2device.cpp:208-235`）以「(名字, 函数)」对按序注册 23 个 pass，注释钉版「Passes will be executed in the order they are added here」（`lower2device.cpp:209`）。顺序为：removeTensorProducerAliases → LoopNestGenerator → loadStoreOpInserter → insertGridSerializationSyncs → insertAllocations → setInplaceAlias → reuseMemoryAllocations → CircularBufferPass → insertRawThreadSynchronization → insertWarThreadSynchronization → insertWarAsyncWait → **UnrollPass** → IndexLowering → fuseWarpReduce → generateConditionalFromPredicate → vectorizeWelford → addRNG → allocateCommonScalars → insertMagicZero → KIRCleaner → instrumentKernel → lowerToInlinePtx。文件头部 include 区（`lower2device.cpp:13-33`）与这张表一一对应——**include 列表即 pass 执行顺序**，改 pass 顺序必须同时动两处。

**两阶段结构**：构造函数先调 `analysis()`（`lower2device.cpp:310-497`，在 `lower2device.cpp:244` 触发），把 kir::Kernel 克隆出来（`lower2device.cpp:325`）后依次构建 validateIr（346）、MinimumDeviceVersion（350）、replaceSymbolicSizes（361）、IdModel（370）、ComputeAtMap（383）、resolveComputeWith（386）、ThreadPredicateMap（421）、FusedReductionInfo（427）、SyncMap（466）、TensorIndexer（486）、PredicateElimination（493）等分析产物；`run()`（`lower2device.cpp:259-289`）随后 reorderExprsForComputeAt（266）、初始化 commonScalarMap（269）、assignRNGOffset（276），然后跑 pass 循环（278-281），最终 `kernel_->finalize`（286）。`segmenterHintCleanup`（`lower2device.cpp:147-156`）在此把 SegmenterSet 还原为 Set。KIRCleaner（`lower2device.cpp:51-143`）收尾清 nop：空循环删除、恒真分支折叠，甚至 then 空而 else 非空时反转条件（`lower2device.cpp:126-134`）。

**谓词插入钉版在 unroll.h**：`csrc/device_lower/pass/unroll.h:26-28` 原文「A bit deceptively: UnrollPass adds all predicates, so it needs to be run even if we don't unroll any loops」——UnrollPass 的真实职责是插入全部保护谓词，unroll 只是顺带。头文件注释（`unroll.h:29-53`）给出经典变换：整瓦片判断提到内层循环外（`if (i*4+3 < I && j*128+127 < J)` 包住无谓词快路径），边角料留给内层逐元素谓词慢路径，即"两套循环集"。`canOmitElseClause`（`unroll.h:69`）与 ElectSync 谓词替换状态（`unroll.h:102-109`）处理 warp 选举与 1D TMA 到达谓词特例。

## 3. 外部连接

上游是分段器产出的每段克隆 Fusion 与 `LaunchParams`；下游 `kir::Kernel` 直接交给 codegen（`codegen.cpp`）与 `KernelExecutor`。pass 目录 21 对文件中，index.cpp 的 `IndexLowering` 用 78 个 handle 方法覆盖全部算子并做 grid 通信 work buffer 推导；circular_buffer.cpp 同文件并存通用与 TMA 专用克隆器，HopperPingPongMbarriers 硬编码 warp 组=2；inline_ptx.cpp 按 Turing/Ampere/Hopper/Blackwell 分代 handle。分析产物通过 `info()` 与 GpuLower 全局可查——ThreadPredicateMap 是 unroll.h include 的 `thread_predicate.h` 产物（`unroll.h:12`）。

## 4. 数据流

Fusion（分段后）→ GpuLower 构造（分析链填 FusionInfo）→ run()：表达式按 computeAt 重排 → 23 pass 依序改写（循环嵌套生成 → 分配/别名 → 同步插入 → 谓词/展开 → 索引下沉 → warp 归约融合 → RNG/magic-zero → 清理 → inline PTX）→ `kir::Kernel` 定型。每步之后 `dumpExprsIfEnabled`（`lower2device.cpp:185-205`）可按 pass 名过滤打印。

## 5. 设计决策

分析与变换严格分离：analysis() 只读不写（symbolic sizes 替换等少数例外），pass 链只消费分析、不改分析——这让 SyncMap/PredicateElimination 等重分析可以基于稳定的全局视图。pass 表用数据而非代码控制顺序，新增 pass 只改初始化列表一行。嵌套 lowering 被显式禁止（`lower2device.cpp:313-314` NVF_ERROR），避免 active_gpu_lower 串台。索引类型默认 int64（`lower2device.cpp:319-322`），TMA 场景由 executor 侧强制改 int32。

## 6. 新人提示

- `NVFUSER_DUMP=lower_verbose`（可带 pass 名参数过滤，`lower2device.cpp:189-197`）是观察 pass 逐层改写的首选工具。
- 找"谓词是谁加的"答案固定是 UnrollPass（`unroll.h:26-28`），不是 predicate.cpp——命名极具误导性。
- `insertRawThreadSynchronization` 在 `insertWarThreadSynchronization` 之前（L221-222），RAW 先于 WAR 不是笔误；同步分析源头在 SyncMap。
- KIRCleaner 会反转/折叠分支，调试谓词时若发现条件"变反了"（`lower2device.cpp:128` logicalNotExpr），不是 bug 而是清理器在规范化。
