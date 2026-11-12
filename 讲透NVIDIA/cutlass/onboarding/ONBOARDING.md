# CUTLASS 4.8 ONBOARDING（新人上手指南）

> 知识图谱基线：9311 节点 / 20737 边 / 16 层 / 16 步导览 / validator 0 issues / fingerprints 1911 文件 @ commit `0b55a2f6`。
> 本指南所有行号锚均从源码逐条核实（2026-11-06 快照）。

---

## 1. 项目定位：CUDA 上的 GEMM/卷积模板抽象库

CUTLASS（CUDA Templates for Attention, Linear Algebra, Sparse/Symmetric Matrices and Semaphores... 官方全称见 README）是 NVIDIA 开源的 **CUDA C++ 模板库**，把 cuBLAS 级别的 GEMM / 卷积 / epilogue 融合内核以可组合模板的形式交到用户手里。它既是"能直接跑的算子库"，更是"写你自己内核的框架"——vLLM、SGLang、TensorRT-LLM、Triton 的部分底层内核都构建在 CUTLASS 抽象之上。

**三代演进脉络**（理解本仓目录结构的钥匙）：

- **CUTLASS 2.x 世代**：`thread → warp → threadblock → kernel → device` 五级传统抽象，`DefaultGemmConfiguration`（include/cutlass/gemm/device/default_gemm_configuration.h，955 行 35 偏特化）+ `DefaultGemm`（include/cutlass/gemm/kernel/default_gemm.h，1189 行）组成配置工厂链，"无参即用"但组合自由度受限。
- **CUTLASS 3.x 世代（CuTe）**：引入 `include/cute/` 坐标代数学（layout/swizzle/tensor）与 collective 抽象，kernel 变成 `CollectiveMainloop + CollectiveEpilogue + TileScheduler` 三件套，靠 `CollectiveBuilder` 工厂按 dispatch policy 标签组装；SM90 warp specialization、TMA、persistent kernel 都在这一世代表达。
- **CUTLASS 4.x 世代（Python 双轨 + 编译器）**：`python/CuTeDSL`（@jit 装饰的 Python 原生 DSL，AST 捕获→MLIR→cubin）、`cutlass_compiler/`（cute MLIR 方言编译器栈）、`operators/`（新一代黑盒 Operator API）三块加入，与 C++ 模板库并行构成"同一套 CuTe 代数，四套语言面"的格局。

**版本真相（三条线索拼出双轨发布线）**：

1. C++ 侧权威版本：include/cutlass/version.h:41-43 定义 `CUTLASS_MAJOR 4 / MINOR 8 / PATCH 0`，version.h:52 合成 `CUTLASS_VERSION`。
2. 构建期注入：version.h:44-49 在 `CUTLASS_VERSIONS_GENERATED` 宏下条件包含 `cutlass/version_extended.h`——**该文件仓内不存在**，由 CMakeLists.txt:758-761 `configure_file` 从 cmake/version_extended.h.in:33-34（注入 `CUTLASS_BUILD` 与 `CUTLASS_REVISION` git 串）生成到构建目录。直接源码 include 而不跑 CMake 时回落 BUILD=0/REVISION 空。
3. Python 轮子独立版本：pyproject.toml:7 写死 `version = "4.2.0.0"`，落后 C++ 侧 4.8.0——Python 轮子由发布管线单独维护，**不要用 pyproject 判断 C++ 能力**。

当前 4.8.0 的主题是 Rubin（sm107）初始支持（README.md:50）：dense/blockscaled GEMM 的 sm107 kernel 预览、Rubin CuTe 扩展与 profiler 支持。README.md:309-313 钉版了一个高频踩坑：**数据中心 Blackwell SM100 与消费级 RTX 50（SM120）互不兼容**——用 `sm100a` 条件特性编译的 kernel 无法跑在 RTX 50 上，反之亦然，选目标架构时先分清"数据中心卡还是游戏卡"。

---

## 2. 架构总览：四大物理块与 16 层地图

仓根四大物理块（括号为图谱扫描文件数，合计约 1885 个 analyzed 文件）：

| 物理块 | 文件数 | 内容 |
|---|---|---|
| `include/` | 838 | C++ 模板库本体：cute 代数（52）+ cute 硬件原子（65）+ cutlass 基础库（64）+ arch 指令/流水线（32）+ GEMM 调度/collective（150+173）+ epilogue/EVT（133）+ conv（98）+ 支撑域（71） |
| `cutlass_compiler/` | 463 | cute MLIR 方言编译器栈 + cutegen 数值代数库 + 347 个 LIT/集成测试文件 |
| `python/` | 403+ | CuTeDSL 运行时（222）+ cutlass_library 生成器（21）+ cutlass_cppgen（70）+ pycute 玩具实现 + 旧文档快照 |
| `operators/` | 183 | 新一代黑盒 Python API：base/metadata/op/arguments + fusion EVT 镜像 + providers 双后端 |

**16 层知识图谱地图**（自底向上，层号即依赖深度）：

- **L01-L02 CuTe 层**（117 文件）：纯代数半区（layout/tuple/swizzle/tensor）+ 硬件半区（arch PTX 封装 + atom traits）。这是全仓被引用最密的底座：include/cutlass/cutlass.h fanIn=544，include/cute/config.hpp fanIn=78，include/cute/tensor.hpp fanIn=71。
- **L03-L04 CUTLASS 基础层**（96 文件）：数值类型/布局映射/宿主辅助（include/cutlass/cutlass.h 根头、numeric_types.h fanIn=254）+ arch 指令封装与流水线同步（sm50→sm100 MMA 全谱、sm90/sm100 pipeline）。
- **L05-L08 GEMM/Epilogue/Conv 主体**（554 文件）：kernel 调度层与 device API（150）、collective 主循环与传统 threadblock/warp 层（173）、epilogue 体系与 EVT 树（133）、卷积隐式 GEMM（98）。
- **L09 支撑域**（71 文件）：transform/reduction/detail/experimental 横向兜底，保证 include/ 零遗漏。
- **L10-L12 Python 世代**（506 文件）：CuTeDSL 运行时（222）、Python 工具生态（101）、operators 黑盒 API（183）。
- **L13-L15 编译器线**（463 文件）：PyIR/cute_ir 方言→base 降级→工具链（69）+ cutegen 数值代数（47）+ 测试验证面（347）。
- **L16 文档与构建链**（104 文件）：Sphinx 旧快照、cmake 资产、仓根文件。

依赖方向口诀：**cute 代数 ← cute 硬件 ← cutlass 基础 ← GEMM/conv/epilogue collective ← kernel ← device ← builder/工具链**；Python 侧（L10-L12）与编译器侧（L13-L15）各自镜像同一套 CuTe 概念，形成"C++ 头文件 / Python DSL / MLIR 方言 / 黑盒 API"四张面孔。

---

## 3. GEMM 模板主线：device → kernel → collective → builder

### 3.1 用户入口：device 层

3.x 的标准入口是 `GemmUniversalAdapter`（include/cutlass/gemm/device/gemm_universal_adapter.h:82 前向声明、:123 主特化，全库最重要设备层，819 行）：它把 CuTe collective kernel 适配到统一设备接口——cluster launch（含 cudaHostAdapter 路径，:145 `kEnableCudaHostAdapter`）、preferred cluster、CUDA graph 兼容初始化、TileSchedulerParams 装配。2.x 老入口 `GemmUniversal`（include/cutlass/gemm/device/gemm_universal.h）走 `DefaultGemmUniversal` 配置工厂（include/cutlass/gemm/kernel/default_gemm_universal.h，396 行），两套 API 并存但**新代码一律走 3.x 适配器**。

### 3.2 kernel 层：调度词汇表 + persistent

- **dispatch_policy.hpp 是 3.x 的中枢词汇表**（include/cutlass/gemm/dispatch_policy.hpp，1701 行 155 个空 tag 类）：`MainloopSm90TmaGmmaWarpSpecialized`（:266）等 Mainloop* 标签携带 Stages/ClusterShape/KernelSchedule 模板参数；`KernelTmaWarpSpecialized`（:119）与 `KernelTmaWarpSpecializedCooperative`（:123）等 Kernel* 标签是 schedule 分派主键。epilogue 侧对称地有 include/cutlass/epilogue/dispatch_policy.hpp（53 个空 tag）。**空 tag 零逻辑、纯类型分派**——这是全库 builder→collective→kernel 三层解耦的类型协议单一出处。
- **kernel 本体**：SM90 warp-specialized 基础版 include/cutlass/gemm/kernel/sm90_gemm_tma_warpspecialized.hpp:65（单 warp 组，523 行）；主流高吞吐走 cooperative 变体（893 行，双 math warp 组共享 epilogue）；SM100 参照实现 include/cutlass/gemm/kernel/sm100_gemm_tma_warpspecialized.hpp:67（964 行，load/mma/epilogue 三阶段 warp 分工，累加器放 TMEM）。
- **tile scheduler**：include/cutlass/gemm/kernel/tile_scheduler.hpp:86 `TileSchedulerSelector`（544 行 30 特化）按（SchedulerTag×ArchTag）选 Persistent/StreamK/Group/Dynamic；SM100 引入 CLC 硬件动态调度（include/cutlass/gemm/kernel/sm100_tile_scheduler.hpp:59 `PersistentTileSchedulerSm100`，:74 `CLCResponse` 16B opaque 响应，经 `PipelineCLCFetchAsync` 异步取号）。调度器数学本体在 tile_scheduler_params.h（2582 行，Sm90/Sm100 × 默认/StreamK/Group 六个 Params 类）。

### 3.3 collective 层：mainloop 与 builder 工厂

collective mainloop 是 3.x 的计算主体，例如 include/cutlass/gemm/collective/sm90_mma_tma_gmma_ss_warpspecialized.hpp:72 `struct CollectiveMma`（584 行）：producer warp 发 TMA、consumer warp 打 wgmma，per-stage mbarrier 同步；数组批处理变体 sm90_mma_array_tma_gmma_ss_warpspecialized.hpp:628/:716（`tensormaps_init`/`tensormaps_perform_update`，逐问题 tensormap 更新=动态形状 GEMM 基线）。

**CollectiveBuilder 是 3.x 的"用户 API"**（include/cutlass/gemm/collective/collective_builder_decl.hpp:93 主模板声明）：用户传 MMA atom/数据类型/TileShape/StageCount，builder 偏特化拼出完整 mainloop 类型。关键族谱：

- include/cutlass/gemm/collective/collective_builder.hpp:40 引入 sm90_gmma_builder.inl、:43 引入 sm100_umma_builder.inl（`__CUDACC_RTC__` 宏门控非编译期路径）——按架构枚举的单一入口。
- Stage 数三态：`StageCount<N>` 显式 / `StageCountAutoCarveout`（collective_builder_decl.hpp:50，从 SMEM 预算自动扣除 epilogue carveout）/ `StageCountAutoCarveoutEpi`（:67）。
- Blackwell 公共底座 sm1xx_common.inl:437-454：`blockscaled_type` 主模板+7 偏特化家族，把 mx_float4/6/8、tuple<T,SF> 等块缩放格式映射到 builder；SM100/103/107/120 各代 builder 共享。
- **源码级笔误（读码勿疑自己）**：sm107_common.inl:47/:73/:91 模板参数名写作 `ElementAMmaccumulator`（应为 ElementAccumulator，全文 7 处）——只是参数名拼写，不影响语义，但 grep ElementAccumulator 在该文件会漏。
- epilogue 侧同名工厂模式镜像：include/cutlass/epilogue/collective/collective_builder.hpp:70 `struct CollectiveBuilder` + CallbacksBuilder 特化家族（见 §6）。

### 3.4 传统三级（2.x 遗产）

`threadblock/warp/thread` 三级 83 文件与 collective 并存：mma_base.h（SMEM 分配与 gemm_k_iterations）、default_mma_core_sm80.h（2952 行最大特化矩阵）、mma_tensor_op_tile_iterator.h（4803 行 fragment 迭代器主库）。老代际（SM70/75/80 SIMT/tensorop）与部分 conv 路径仍靠它们服务，**改 2.x 路径先读 default_gemm.h 的 1189 行装配链**。

---

## 4. SM90/SM100 特化层：atom 动物园与 warp specialization

### 4.1 arch 与 atom 两层分工

- `include/cute/arch/`（35 文件）：**纯 PTX inline asm 封装**，纯结构体+静态 fma/copy 方法。旗舰是 include/cute/arch/mma_sm90_gmma.hpp（20974 行，320 个 `MMA_64xNxK` wgmma atom，首个 `wgmma.mma_async` PTX 串在 :158，代表性 struct `MMA_64x64x16_F32BF16BF16_SS` 在 :2538）；选择器工厂在 include/cute/arch/mma_sm90.hpp（9331 行，:366 `ss_op_selector`、:4852 `rs_op_selector`，2000+ 行 constexpr if-else 逐级试探链，Tree_N 对 256 取模选 atom）。SM100 的 tcgen05 UMMA 自 include/cute/arch/mma_sm100_umma.hpp:71 封装（44 个 atom，SS/TS/块缩放/稀疏/2x1SM 全系）。
- `include/cute/atom/`（30 文件）：**traits 动物园**——同名 `MMA_Traits` 模板特化家族在 mma_traits_sm90_gmma.hpp 精确 320 个（8987 行，grep -c 实证）、sm90_gmma_ext 736 个、sm80 65 个、sm100 48 个；批分析阶段确认 SM90 atom 动物园合计 **2201 个子节点**，是图谱最大单族。机制层：include/cute/atom/mma_atom.hpp:42-49 `MMA_Atom`（包装单条指令）→ :211 `TiledMMA`（线程分块到 tile）→ :203 `ThrMMA`（单线程视角）三层抽象；copy 侧对称（include/cute/atom/copy_atom.hpp:45-52 `Copy_Atom` + make_tiled_copy 工厂 :410）。

**代际差速记**：SM90 wgmma 操作数=SS（双 smem descriptor）或 RS（A 在寄存器）；SM100 tcgen05=SS 或 TS（A 在 tensor memory），累加器从寄存器搬到 TMEM（tcgen05.alloc 分配列），这是 Hopper→Blackwell 最大的编程模型断层——SM100 kernel 必须配 tmem 分配器（include/cute/arch/tmem_allocator_sm100.hpp 的 Allocator1Sm/Allocator2Sm）+ TMEM carveout（sm100_pipeline_carveout.inl 的 Sm100DenseGemmTmaUmmaCarveout）。

### 4.2 流水线与同步

- include/cutlass/pipeline/sm90_pipeline.hpp:289 `PipelineTmaAsync`（TMA 生产者）、PipelineTmaStore/PipelineTransactionAsync/PipelineAsync/OrderedSequenceBarrier（1406 行）；SM100 对称 include/cutlass/pipeline/sm100_pipeline.hpp:119 `PipelineUmmaAsync`、:537 `PipelineTmaUmmaAsync`。
- 更底层同步原语：include/cutlass/arch/barrier.h（NamedBarrier 位图 + ClusterBarrier/ClusterTransactionBarrier mbarrier 家族，1010 行）、include/cute/arch/cluster_sm90.hpp（elect_one_sync/leader_sync 选举，fanIn=85 全库硬件层最高）、include/cutlass/arch/reg_reconfig.h（setmaxnreg warp 组间寄存器再分配）。
- **调试利器**：include/cutlass/arch/synclog.hpp:55 `CUTLASS_ENABLE_SYNCLOG` 开启后每条 barrier/TMA/wgmma 发射前记录进环形缓冲，死锁与乱序排查第一手段；宿主侧对应 include/cutlass/trace.h 的 `CUTLASS_TRACE_HOST`（编译期零开销）。

### 4.3 TMA 与动态形状

include/cute/arch/copy_sm90_desc.hpp:333 起的 `tensormap.replace.tile.*` PTX 系列支持**设备端改写 gmem 中 TMA descriptor 的字段**（地址/维度/stride，:350/:371 变体）——CUTLASS 动态形状 TMA（grouped GEMM 逐问题换 tensor map）的基石，配合 §3.3 的 tensormaps_init/perform_update 闭环。SM100 TMA 在 copy_sm100_tma.hpp（2SM 双 SM 协作 + gather4/scatter4 行索引 gather-scatter 变体）。

---

## 5. CuTeDSL/PyIR：Python 原生世代

### 5.1 CuTeDSL 是什么

`python/CuTeDSL/cutlass/` 让 **@jit 装饰的 Python 函数经 AST 预处理捕获为 IR，再 JIT 编译成 CUDA cubin**，无需写 C++。三层结构：

- **base_dsl**（62 文件）是引擎：dsl.py:288 `class BaseDSL`（88 方法 3260 行，jit 函数 trace/IR 上下文/编译执行的全部通用机制），:689 `def jit`（host 端装饰器）与 :704 `def kernel`（device 端装饰器）是两个入口动词；compile_backend.py:73 `class CompilerBackend`（ABC）+ :14 文档钉版的 `CUTE_DSL_COMPILER_BACKEND` 环境变量在多后端（legacy=MLIR ExecutionEngine 等）间选择；jit_executor.py:387 `ExecutionArgs`（运行时参数绑定）/ :1140 `JitExecutor`（持有执行引擎与 cubin）负责执行侧。
- **cute/**（59 文件）把 C++ CuTe API 镜像到 Python：core.py:1133 `class _Layout`、:3684 `make_layout`、:5379 `make_layout_tv`（6726 行核心原语集）；typing.py:101 `SymInt`（符号整数，AOT 动态维度）与 :640 `TypedTensor`（静态张量类型描述符，1025 行类型 ABC 层）。
- **cutlass_dsl/**（13 文件）对应 C++ cutlass 模板层：cutlass.py:481 `class CutlassBaseDSL`、:1855 `class CuTeDSL` 单例主类。

torch 互操作走 python/CuTeDSL/cutlass/torch.py（as_tensor/matrix/prepare_tensors_for_gemm），基准测试走 testing.py（benchmark/tune/autotune，CUDA graph 计时，1040 行）。

### 5.2 PyIR：Python 副作用语义升格为显式 IR 状态机

PyIR 七文件是 base_dsl 里最深的工程（图谱批 16-20 合计 2210 子节点）：Python 的赋值/读取/循环携带/跨函数调用副作用被插桩为显式 SSA 簿记。**六层运行时按依赖顺序装配**——pyir_runtime.py:19-27 的门面按 `pyir_state → pyir_core → pyir_corewalk → pyir_loop_carry → pyir_entrypoints → pyir_call_boundary` 顺序 star-import（class_facts 与 spec 是旁挂叶，不在层链上）：

| 层 | 职责 | 锚 |
|---|---|---|
| pyir_core.py | 核心簿记（9913 行 250+ 函数）：_WatchedM/_WatchedDict/_WatchedList 把 Python 原语包成受跟踪 place；MutableValue 持 pyir.ref 句柄 | :2396 / :6545 |
| pyir_entrypoints.py | AST 插桩代码的 choke 入口：每次赋值/读取前调 pyir_assign/pyir_read（5374 行 50+ 入口） | :1166 / :3428 |
| pyir_loop_carry | 循环/if 区域快照-配对-回放（循环携带变量物化） | — |
| pyir_call_boundary.py | 未插桩 callee 的受跟踪存储：快照→调用→diff→重放（2417 行） | — |
| pyir_preprocessor | PyIRDSLPreprocessor 122 方法：赋值重写、调用包装 f(x)→_pyir_call_boundary_(f)(x) | — |
| pyir_class_facts | 装饰期登记每个类的 self 写事实与传递闭包，绝不进 trace 期 | — |

读码建议：先读 pyir_runtime.py 的模块 docstring（六层分工自述），再从 pyir_entrypoints.py:1166 的 pyir_assign 下钻。

### 5.3 工具链小件

`_mlir_helpers/`（arith.py 等）用模块级 `__getattr__` 延迟导入打破 arith↔vector 循环依赖；安装唯一可靠路径是 python/CuTeDSL/setup.sh（wheel 模式按 --cu12/--cu13 选 requirements；--editable 模式强制要求 CUTLASS_IR_BUILD_DIR 指向 CMake 构建树）——**pyproject.toml 的 version 动态指向 VERSION.EDITABLE 文件，git 检出中不存在**（发布管线生成），源码树直接 pip install 会失败。

---

## 6. Epilogue 体系与 EVT fusion 树

### 6.1 三代 epilogue 并存

- **thread 级**（25 文件）：激活函数动物园——activation.h 48 个定义/19 种（ReLU/GELU_taylor/SiLu/HardSwish 及导数版），linear_combination.h 的经典 `D = alpha*acc + beta*C`（CUTLASS 2.x 默认 epilogue）。
- **threadblock 级**（54 文件）：2.x 直接存取路径，epilogue.h 的 acc2smem 中转 + PredicatedTileIterator（1414 行）谓词写出，default_epilogue_tensor_op.h（904 行）是配置装配中心。
- **collective 级**（25 文件）：3.x 主体——include/cutlass/epilogue/collective/sm90_epilogue_tma_warpspecialized.hpp:83 `class CollectiveEpilogue`（963 行，StagesC/StagesD 多阶段 SMEM 复用 ReuseSmemC + FusionCallbacks 树 + TMA 异步写出）；SM100 主力同构（TMEM→smem→TMA store，eVT 融合树在 smem 上执行）；nosmem 变体（default_epilogue.hpp）是逐线程直接写出的朴素回退。

### 6.2 EVT（Epilogue Visitor Tree）：fusion 的统一表达

3.x 把"输出前想顺手算点什么"统一为 visitor 树，四层结构：

1. **operations.hpp 语义标签层**：include/cutlass/epilogue/fusion/operations.hpp:128 `struct LinearCombination`、:143 `LinCombEltAct`、:548 `LinCombEltActBlockScaleFactor` 等 28 个描述性 struct，以注释公式（`D = activation(alpha*acc + beta*C + per-row bias)`）+模板参数声明用户侧语义，**与实现解耦**。
2. **callbacks.hpp 分发层**：include/cutlass/epilogue/fusion/callbacks.hpp:54-55 `struct FusionCallbacks` 主模板 static_assert 报错（"Could not find a callbacks specialization"）——找不到架构特化时的标志性报错就来自这里；各架构特化（sm90_callbacks_tma_warpspecialized.hpp 2886 行覆盖面最广 / sm100 1322 行）把标签组装成 visitor 树。
3. **visitor 三层正交节点**：
   - load 词典（sm90_visitor_load_tma_warpspecialized.hpp 1882 行）：:62 `Sm90AccFetch`（取累加器）、:91 `Sm90SrcFetch`（取 C）、:1010 `Sm90ScalarBroadcast`（标量/行/列广播，bias 来源）；
   - compute 词典（sm90_visitor_compute_tma_warpspecialized.hpp）：:91 `Sm90Compute`（functor 逐元素）、:233 `Sm90TreeVisitor`（组合子）；
   - store 词典（sm90_visitor_store_tma_warpspecialized.hpp 2135 行）：:70 `Sm90AuxStore`（辅助梯度 TMA 写出）、:1078 `Sm90RowReduction`、:1666 `Sm90ColReduction`（alpha/beta 梯度累加场景）。
   接口契约在 sm90_visitor_tma_warpspecialized.hpp:483 `Sm90VisitorImplBase` / :587 `Sm90VisitorImpl`（ProducerLoad/ConsumerStore 回调对）。
4. **非平凡子计算示范**：sm90_visitor_topk_softmax.hpp 的 TopK+Softmax 列归约（MoE 场景），证明树节点不只是逐元素。

### 6.3 Python 双侧镜像（易混淆点）

EVT 有**两套 Python 前端、同构同源**：① `python/cutlass_cppgen/backend/evt/`（frontend python_ast → ir/dag → passes → sm80/90/100 emitter，服务 cppgen 出 C++）；② `operators/cutlass/operators/fusion/`（同样 frontend→dag_ir→passes→emitter，服务 CuTeDSL JIT 后端）。核心数据结构一致：operators/cutlass/operators/fusion/ir/dag_ir.py:46 `class DAGIR`（有向无环图组织 Load/Compute/Store/Layout 节点）、ir/node.py:70 `ImplBase` / :174 `NodeBase`、passes/pass_manager.py:118 `class EVTPassManager(nx.DiGraph)`（拓扑序调度 pass）。**改 EVT 前端逻辑时两处都要看**，它们是复制品关系而非引用关系。

---

## 7. 工具链：代码生成器、cppgen 与 profiler

### 7.1 cutlass_library：13092 行的清单生成旗舰

python/cutlass_library/generator.py 是"把全库 kernel 实例化清单生成出来"的旗舰（**13092 行**）：

- **入口无 main() 函数**：generator.py:13035 `if __name__ == "__main__":` 直接构造 Manifest，:13049 起串行调用 `GenerateSM50(manifest, ...) → SM60 → SM61 → SM70 → SM75 → SM80 → SM89 → SM90 → Blackwell(sm100a/f…) → SM103/107`（`GenerateSM50` 函数定义本体在 :1357）——12 个代际工厂逐级展开 tile/数据类型/调度组合的全部 GEMM/Conv 实例源码。`heuristics_problems_file` 分支走启发式过滤（:13047）。
- manifest.py:494 `class Manifest` 收集 operation 列表并按 kernel filter 过滤，emit_manifest_cmake 产出 cmake 注册代码；library.py（1701 行）是元数据中心：30+ 枚举（DataType 47 型、KernelScheduleType/EpilogueScheduleType 全系后缀）+ TileDescription/TensorDescription 数据类。
- heuristics.py:125 `get_gemm_configs` 是运行时选型入口（SM90/SM100 从配置批量生成实例 + profiler 测试清单落 CSV）；sm90_shapes.py / sm100_shapes.py 是纯 dict 形状数据表（sm100 配 DynamicClusterShape 支持动态 cluster，level 越高越少发射的剪枝约定）。
- 构建集成：仓根 customConfigs.cmake 以 `PYTHONPATH=cutlass_library 包目录 + --architectures=${CUTLASS_NVCC_ARCHS}` 调 generator.py，把生成器织入 CMake（profiler 功能回归按 L0/L1/L2 测试级别生成 kernel filter）。

### 7.2 cutlass_cppgen：易用 Python GEMM（前身就叫 cutlass）

python/README.md 钉版：**cutlass_cppgen 前身即旧 `cutlass` 包**，为与 CuTe Python DSL 区分而更名——这解释了 python/docs/ 旧文档树（cutlass.emit/cutlass.op/cutlass.utils）与新包名的错位。核心链路：op/op.py:58 `class OperationBase`（cc 就近匹配/激活注册/epilogue 复位协议）→ op/gemm.py:140 `class Gemm(OperationBase)`（Python 一步构造/编译/运行 GEMM：tile/cluster/schedule 启发式选参、plan.run() 直达 device）；backend/gemm_operation.py（2145 行）发射 CUTLASS 2.x/3.x 实例源码并编码参数；utils/profiler.py:52 `class GpuTimer` / :97 `class CUDAEventProfiler` 是 Python 侧 kernel 计时器（bytes/flops 统计，可调外部 cutlass_profiler 比对）。

### 7.3 operators：新一代黑盒 API（4.x 主推）

operators/ 的用法三段式（README）：**Arguments 表达操作 → get_operators 发现 → JIT 编译执行**。骨架：base.py:49 `class Operator(ABC)`（参数解析/编译/运行/元数据声明契约）；providers/ 双后端——cutedsl 走 CuTeDSL JIT（关键魔法在 providers/cutedsl/gemm/implementations/scheduler.py:31 `from cutlass._mlir import ir`——**该目标模块仓内不存在，由 MLIR 后端运行时动态注入**，静态分析工具会在此报 unresolved import 属预期）、cutlass_library 走 cppgen 出 C++；heuristics/（nvmatmul）运行时选 kernel；rubin/ 6 文件是 sm107 早期实验线。官方教程在 operators/examples/000_gemm.ipynb → 001 融合 epilogue → 006 block-scaled GEMM → 007 heuristics。

### 7.4 profiler 与 cmake 细节

C++ 侧 cutlass_profiler（tools/，图谱裁剪范围外）配合 CUDA.cmake（387 行：nvcc/clang++ 二选一、unity batch 文件名用内容 SHA256 前 12 位保证确定性、MSVC/all-kernels 默认开 unity build）；cmake/googletest.cmake FetchContent 拉 gtest v1.14.0；CTest 双模板被仓根 CMakeLists.txt:974/:978 引用。

---

## 8. 新人上手：入口、阅读路线与版本陷阱

### 8.1 按身份选入口

- **C++ GEMM 用户**（只想跑个快 kernel）：读 examples/49_hopper_gemm_with_collective_builder/49_collective_builder.cu（Hopper CollectiveBuilder 标准用法）→ examples/70_blackwell_gemm（Blackwell 版）→ 按需看 examples/ 目录共 102 个例子（00_basic_gemm 到 70+ 代际纵深）。
- **Python 用户**：从 operators/examples/000_gemm.ipynb 入门黑盒 API；要精细控制再降级到 CuTeDSL（python/CuTeDSL examples + torch.py 互操作）；要生成 C++ 静态库走 cutlass_library generator.py。
- **内核开发者/研究者**：先吃透 §2 的 L01-L02（cute 代数：include/cute/layout.hpp:99 `struct Layout`、swizzle.hpp:55 `struct Swizzle`、tensor_impl.hpp:1037 `local_tile` / :1079 `local_partition`——GEMM 分块的两个基本动作），再沿 §3 主线下钻。

### 8.2 推荐阅读路线（图谱 16 步 tour 精简版）

1. README.md + version.h（版本与兼容性边界）→ 2. cute 代数三层（layout→swizzle→tensor，t01/t10）→ 3. atom 抽象（mma_atom.hpp:42 三层 + 一个 wgmma atom 的 arch/traits 两侧对照，t04）→ 4. collective mainloop（sm90_mma_tma_gmma_ss_warpspecialized.hpp:72，t05）→ 5. kernel 与 scheduler（sm90/cooperative + tile_scheduler.hpp:86，t02/t05）→ 6. epilogue/EVT（§6 四层，t06/t07）→ 7. builder 工厂（collective_builder_decl.hpp:93 → sm90_gmma_builder.inl → sm1xx_common.inl:437，t03）→ 8. conv（conv_kernel:60 ConvUniversal 直接继承 GEMM kernel 的零成本桥接 + collective/sm90_implicit_gemm:69，t08）→ 9. Python 线按需（CuTeDSL t09 / PyIR t11 / operators t15）→ 10. 工具链（t14）收官。

### 8.3 版本与构建陷阱清单（图谱甄别钉版）

1. **version_extended.h 不存在**：include/cutlass/version.h:44 条件包含的 `cutlass/version_extended.h` 由 CMakeLists.txt:758-761 从 cmake/version_extended.h.in:33-34 生成到**构建目录**——直接拿 include/ 源码头做静态分析/IDE 索引会报缺文件，属预期。
2. **pyproject 4.2.0.0 ≠ C++ 4.8.0**（pyproject.toml:7）：Python 轮子版本独立维护，判断 C++ 能力只认 version.h:41-43。
3. **CuTeDSL 源码树不能直接 pip install**：pyproject 的 version 动态读 VERSION.EDITABLE（git 检出中不存在），必须走 setup.sh（--editable 还要求 CUTLASS_IR_BUILD_DIR 指向 cutlass_compiler 的 CMake 构建树）。
4. **python/docs/ 是 v3.x 世代遗骸**：64 个 Sphinx 快照文档化的是已更名的旧 `cutlass` 包（今 cutlass_cppgen，模块一一对应），automodule 目标在当前主线均不存在；notebook 真身已迁 examples/python/deprecated/。查 Python API 文档**不要**以该目录为准。
5. **sm100a ≠ sm120**：README.md:309-313，数据中心 Blackwell 与 RTX 50 互不兼容，`-arch` 选错直接编译期/运行期失败。
6. **同名模板特化家族是常态**：本仓大量"一个主模板+N 个同名全特化"（MMA_Traits 320/736、Copy_Traits 175、激活函数 5 特化族），IDE 大纲会折叠成一条，grep 计数才是真相；sm107_common.inl:47 的 `ElementAMmaccumulator` 拼写笔误（7 处）勿当成自己的幻觉。
7. **断链死代码勿踩**：include/cutlass/arch/simd.h 主模板签名用了未声明的 T，本身编译不过，实际可用面依赖架构特化——引用 simd.h 前先确认走的是 sm60/sm61 特化路径。
8. **operators 的 `import cutlass._mlir`**（scheduler.py:31）是运行时注入的幽灵模块，静态导入分析工具在此必然报错，不是 bug。
9. **动态 import 的两个 `_mlir_helpers` 延迟导入**（arith↔vector 循环依赖）属设计而非绕过。

### 8.4 调试与验证手段速查

- 死锁/乱序：`CUTLASS_ENABLE_SYNCLOG`（synclog.hpp:55，异步指令发射环形日志）+ `CUTLASS_DEBUG_TRACE_LEVEL`（trace.h）。
- 正确性：test/unit 目录 + operators/test（integration 17+unit 17）；编译器线跑 `check-cute/-base/-integration/-pipelinelit` 六套 LIT 目标（cutlass_compiler/README.md）。
- 性能：cutlass_profiler（C++）或 CUDAEventProfiler（python/cutlass_cppgen/utils/profiler.py:97），前者可由后者外部比对。
- Python JIT：`CUTE_DSL_COMPILER_BACKEND` 切后端定位编译栈问题（compile_backend.py:14）。

### 8.5 收官数据流（把一切串起来）

一次 3.x GEMM 调用的完整链路：用户构造 `GemmUniversalAdapter::Arguments`（gemm_universal_adapter.h:123）→ `initialize` 解析 TileSchedulerParams 与 cluster → `run` 经 kernel_launch.h/cluster_launch.hpp 的 `cudaLaunchKernelEx`（或 CudaHostAdapter 外部执行器路径，:145）发射 persistent kernel → kernel 内 producer warp 经 `PipelineTmaAsync`（sm90_pipeline.hpp:289）搬 TMA、consumer warp 打 wgmma atom（arch/traits 两侧）→ epilogue 的 FusionCallbacks 树做融合 → TMA store 写回。整条链路的每一环都在 §3-§6 的地图里——**迷路时回到 dispatch_policy.hpp 的 tag 词典，那是全库唯一的事实坐标**。

---

## 附：图谱与产物索引

- 图谱：仓内 `.understand-anything/knowledge-graph.json`（9311 节点 / 20737 边 / 16 层 / 16 步 tour / 0 issues / fingerprints 1911 @ 0b55a2f6）
- 批甄别笔记：`.understand-anything/NOTES-DIGEST.md`（259 条）
- 本指南配套：`work4ai/讲透NVIDIA/cutlass/`（README 状态表 + explain 系列）
