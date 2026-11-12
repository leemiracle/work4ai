# 07 · PreSegmenter 与融合分段器：Fusion IR 的两道门户

## 1. 角色定位

nvFuser 的编译流水线在「Fusion 定义」与「设备代码生成」之间有两道顺序门户：**PreSegmenter** 先把用户送来的 Fusion IR 规范化成调度器喜欢的形状；**SegmentCandidateFinder**（fusion_segmenter.cpp，5042 行）再决定这个融合能不能整体调度，不能则切成若干段（SegmentedGroup），每段独立选一个调度器。两者共同回答一个问题：「这一坨表达式，按什么粒度交给调度器最划算」。分段器是 nvFuser 与"单 kernel 融合"哲学的折中点——能融则融，不能融就分而治之，段间靠中间张量交接。

## 2. 内部结构

**PreSegmenter**（`csrc/preseg_passes/pre_segmenter.cpp`，103 行）是极简的总驱动：`PreSegmenter::runPass`（`pre_segmenter.cpp:36`）按固定顺序调用 20 个 OptimizationPass（`pre_segmenter.cpp:46-99`），pass 头文件清单写在 `pre_segmenter.cpp:13-32`。顺序即语义：`TranslateRepeatToExpand` 必须先于 `ConsecutiveCastPass`（`pre_segmenter.cpp:48-49` 注释明言前者会暴露更多连续 cast）；`MovePadPass` 受 `DisableOption::ResizeScheduler` 开关控制（`pre_segmenter.cpp:71-73`），只在 resize 调度器关闭时后移 pad；`FinalizeMultideviceDomainsPass` 固定垫底（`pre_segmenter.cpp:95-99`），把带 DeviceMesh 的 allocation domain 继承 DID 切分。图谱里 preseg_passes 目录恰为 42 个 file 节点（21 对 .h/.cpp），即"42 节点 pass 族"。

**分段器**三层数据结构：`SegmentedGroup::makeClonedFusion`（`fusion_segmenter.cpp:58`）让每段持有自己的克隆 Fusion；`SegmentedFusion::fromCompleteFusion`（`fusion_segmenter.cpp:303`）走"整体可调度"快路径；`makeFusion`（`fusion_segmenter.cpp:1516`）把段还原成可 lower 的子 Fusion。入口是三个 `segment()` 重载（`fusion_segmenter.cpp:1612/1621/1634`）——先 `hasSegmentHints`（`fusion_segmenter.cpp:1660`）检测用户显式埋的 `LoadStoreOpType::SegmenterSet` 标记（`fusion_segmenter.cpp:1665`），无标记则先尝试不分段直接 `proposeHeuristics`。核心合并试探 `tryMerge` 两个重载（`fusion_segmenter.cpp:2137/2160`）用 RAII 式 `FusionSegmentGuard`（`fusion_segmenter.cpp:1953`）临时把候选组拼成完整 Fusion 交给调度器判可行性，失败即回滚。`CombineReductions`（`fusion_segmenter.cpp:2701`）在主合并前识别可合并成 normalization kernel 的同型 reduction（`makeReductionSignature`，`fusion_segmenter.cpp:3121`；`shouldRun`，`fusion_segmenter.cpp:3181`）。收尾 `SegmentCandidateFinder::finalize`（`fusion_segmenter.cpp:4837`）去孤组、重定 ID、`resolveScalarsInGroup` 补标量、`deriveSchedulerType` 定型。`toposort`（`fusion_segmenter.cpp:1674`）与 `GroupDependencyAnalysis::mergeGroups`（`fusion_segmenter.cpp:1226/1264`）维护段间 DAG；`castInputOutputToLowerPrecision`（`fusion_segmenter.cpp:844`）允许把段间边降精度换带宽。

## 3. 外部连接

上游是 `FusionExecutorCache` 与 dynamic transform 完成后的 Fusion；`PropagateShardingsPass/DecomposeReshardingsPass/ReorderShardedAxisPass` 三连（`pre_segmenter.cpp:88-90`）直接消费 multidevice 层的 DeviceMesh/DID 表达。下游每个 SegmentedGroup 带着 scheduler_type 交给 `GpuLower` 与 `KernelExecutor`；`Schedule::proposeHeuristics` 是 tryMerge 的唯一裁判，分段器与调度器注册表构成双向耦合。`lower2device.cpp:147` 的 `segmenterHintCleanup` 会在 lower 前把 `SegmenterSet` 还原成普通 `Set`——分段提示跨阶段贯穿。

## 4. 数据流

Fusion 定义 → PreSegmenter 20 连 pass 规范化 → `buildInitialSegments`（`fusion_segmenter.cpp:3770`）+ `forwardInputs`（`fusion_segmenter.cpp:3790`）建初始组 → `findSegments`（`fusion_segmenter.cpp:3912`，调用点 3758）主循环按 `getMergeCandidates` 试合并 → `resolveForwardedInputs`（`fusion_segmenter.cpp:3874`）/`cleanupForwardedInputs`（`fusion_segmenter.cpp:4009`）补共享输入 → finalize 输出 SegmentedFusion（groups+edges+每段 scheduler_type 与 heuristic 参数缓存）。

## 5. 设计决策

分段本质是"调度可行性约束下的图划分"：把 canSchedule 当 oracle，用 FusionSegmentGuard 做"试拼-验-回滚"，避免为每个子集真编译。守恒由 `validateDisjoint`（`fusion_segmenter.cpp:4912`）断言表达式不跨组重复——但它包在 `#ifndef NDEBUG` 里（`validateIfDebug`，`fusion_segmenter.cpp:2684-2692`），且最终校验显式放宽 `require_disjoint=false`（`fusion_segmenter.cpp:4006`）：转发输入会让 unary expr 合法地跨组共享。`tryMerge` 里那句 "change of world view" 断言（`fusion_segmenter.cpp:2147-2151`）明示：空融合参与合并意味着世界观变了，宁死不静默。

## 6. 新人提示

- 调试分段看 `NVFUSER_DUMP=fusion_segments`；`tryMerge` 的每次试探都有 canScheduleMessage 输出。
- SegmenterSet 是"用户指定切段"的硬提示：检测在 `fusion_segmenter.cpp:1660`，清理在 `lower2device.cpp:147-155`，漏看后者会误以为该算子真存在。
- `segment()` 三重载同名折叠为图谱单节点，读图时注意 1612/1621/1634 三处语义不同（拷贝融合/接管融合/带 runtime_info 的运行时入口）。
- preseg pass 顺序调整前先读注释：MovePad 与 MarkAliasPrepare、MoveSplitCat 的相对顺序（`pre_segmenter.cpp:56-73`）是被注释钉死的约束。
