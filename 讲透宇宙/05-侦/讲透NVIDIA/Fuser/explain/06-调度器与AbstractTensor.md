# 06 · 调度器体系与 AbstractTensor：注册、启发式与调度 DSL

## 角色定位

`csrc/scheduler/` 是图谱 L06 层（110 个节点）的主体：一个注册骨架 + 十三个具体调度器 + 共享工具与工具箱。入口抽象是 registry.h:25 的 SchedulerEntry：schedule（registry.h:32）/computeHeuristics（registry.h:36）/canScheduleCompileTime（registry.h:42）/canScheduleRunTime（registry.h:46）四接口，makeSchedulerInstance（registry.h:57）按 SchedulerType 枚举（scheduler_types.h:50，14 值）分发 13 实例（registry.cpp:136）。选择顺序固化在 all_heuristics_in_priority_order（scheduler_types.h:66）：Cutlass>ExprEval>Communication>NoOp>Matmul>Reduction>Resize>Transpose>PointWise>三个 Persistent>Greedy。

## 内部结构

公共门禁 checkCanSchedule（registry.cpp:29）先做算子级排除——Scatter/SdpaFwd/TopK 等只准 ExprEval/Greedy 接、MatmulOp/LinearOp/MmaOp 只准 Matmul 调度器接，再查连通性、self-mapping、resize 与 cyclic reshape；运行期形状由 SchedulerRuntimeInfo（runtime_info.cpp:153）供给；共享分析缓存在 HeuristicDataCache（compile_time_info.h，20 类）。共享底座 utils.cpp 3796 行 84 个自由函数（调度目录最大），持久 buffer/断点/并行化/调度反转全在此（图谱甄别：与文件名的朴素印象反差极大）。normalization 家族 18 个文件归 6 变体：inner 非 TMA（normalization_inner_non_tma.cpp，1200 行）、inner TMA（normalization_inner_tma.cpp）、inner-outer 多波（normalization_inner_outer_multi_wave.cpp）、inner-outer TMA-WS（normalization_inner_outer_tma_ws.cpp）、outer（normalization_outer.cpp）与共享层（normalization_utils.cpp，2028 行，checkIfWithinRegisterSpace@195、PersistentBufferResolution@1729）；TMA 与 warp-specialized 路径选择在 normalization_inner_outer.cpp:27 preferWarpSpecialized。调度 DSL 在 tools/abstract_tensor.h（953 行）：AbstractId（abstract_tensor.h:30）是 DynamicType，可装 IterDomain\*、ValGroupAndItsGraph 或嵌套向量；AbstractTensorWithInfo（abstract_tensor.h:424）提供与 TensorView 同名同语义的链式 split/merge/reorder/swizzle/parallelize，DispatchSplit 等谓词分派器（abstract_tensor.h:46/:80/:147/:236）按元素类型路由到 IterDomain::split 或图版 merge/split/swizzle（schedule.h:41 起）；别名 using AbstractTensor = AbstractTensorWithInfo\<EmptyInfo\>（abstract_tensor.h:860），TaggedAbstractTensor（abstract_tensor.h:903）给每轴挂随变换传播的 tag 集——mma_utils.h:77 的 AbstractMatmulTensor 即用 MatmulDimRole 标 M/N/K。

## 外部连接

上游消费 Fusion IR 与 IdModel 等价类图（AbstractTensor 的 ValGroup 分支）；每个调度器的 schedule() 输出变换后的 TensorView（computeAt/parallelize 落到 02 篇的域体系），交给 L08 的 GpuLower。下游工具箱 tools/：inlining.cpp 的 MaxPosCalculator、domain_map.cpp 的 DomainMap、vectorize_helper.cpp 的连续内维映射、loop_domain_scheduler.cpp 的循环域重放。

## 数据流

一次调度：scheduleWith（registry.cpp:181）→ checkCanSchedule + canScheduleCompileTime/RunTime 双检 → computeHeuristics 产参数 → schedule(fusion, params) 施加变换。启发式内部先用 AbstractTensor 在域/图上小规模推演（记录-回放：同一份 DSL 代码既能改真实 IterDomain 也能改 ValGroup 等价类），确定分块/向量宽/持久 buffer 后一次性回放到全部相关 TensorView。

## 设计决策

调度器是无状态轻量对象（registry.h:52 注释），参数与实例分离便于缓存与比较（sameAs）。canSchedule 拆编译期/运行期两段，是"编译一次、多形状复用"的前提。AbstractTensor 借自研 dynamic_type 库实现一码两用，避免调度逻辑在"真实域"与"等价类图"写两遍——这是本仓调度代码可读性的关键抽象（图谱甄别）。甄别钉版：transpose_tma.cpp:17-20 getTransposeHeuristics 直接 return nullptr、:23-24 scheduleTranspose 抛 "not yet implemented"——TMA 转置是全仓罕见的显式占位 stub，真实现看 transpose_non_tma.cpp，别把 stub 当特性。

## 新人提示

加新算子先查 registry.cpp:29 的门禁表，算子没被任何调度器认领会落到 Greedy 兜底。读某类融合的调度从 scheduler_types.h:66 的优先序定位家族，再进对应 \*_heuristic.h 看参数结构。调试打印用 scheduler/debug_utils.h 与 canScheduleRejectReason 日志。写新调度逻辑优先用 AbstractTensor DSL 而非裸操作 TensorView，图/域双跑测试会免费覆盖你。
