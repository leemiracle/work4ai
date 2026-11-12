# explain-05 · 调度核心：src/s_tir/schedule/concrete_schedule.cc（ConcreteSchedule 状态机）

## 角色定位

`concrete_schedule.cc`（1102 行）是 s_tir 调度层的**心脏**：`ConcreteScheduleNode` 是 Python 侧 `tvm.s_tir.Schedule` 对象背后的 C++ 状态机，用户敲下的每条调度原语（split/fuse/compute_at/cache_read/tensorize…共 40+ 条）都路由到本文件的同名方法。它自己几乎不做 IR 变换——每方法都是固定三拍：**校验入参 → 委托 `s_tir::` 命名空间的自由函数（真正的变换实现，住在 primitive 子目录）→ `state_->DebugVerify()` 复核**。它的独特价值是三样状态管理：StmtSRef 树（IR 节点→可变引用的映射）、符号表（随机变量 RV 的物化）、以及确定性采样引擎。同目录还有 `traced_schedule.cc`（继承它、额外记录指令 trace 供 meta_schedule 回放），`Schedule::Concrete` 工厂（L31-46）是两者的共同地基——构造时建 `ScheduleState`、初始化 analyzer、`FindEntryFunc` 选定默认工作函数（L39-44）。

## 内部结构

五个状态成员（`concrete_schedule.h` L44-55）：`state_`（ScheduleState：mod + stmt2ref + block_info）、`func_working_on_`、`error_render_level_`、`symbol_table_`（RV→StmtSRef/IntImm）、`analyzer_`（arith::Analyzer，"persistent stateless"）、`rand_state_`。文件按功能分区（行号锚定本文件）：

- **ScheduleCopier（L51-189）**：深拷贝 sref 树的专职类。L75-91 两遍构建：先按 `stmt2ref` 建全部新 SRef（parent 置空），再回填 parent 指针——**指针分两遍接的目的是避免顺序依赖**。L97-103 处理"过期 sref"（指向已被变换删除的语句）：拷成 `StmtSRef(nullptr, nullptr, -1)` 哨兵而非报错。`Copy()`（L200-208）里 L205 特意新建 analyzer（注释："new analyzer needed because it is stateful"——缓存过的化简结论对新 IR 不安全）、L206 `ForkSeed()` 分叉随机流。
- **错误渲染协议（L211-228）**：`TVM_TIR_SCHEDULE_BEGIN/END` 宏对是所有原语的统一 try/catch 外壳，按 `error_render_level_` 三档渲染 ScheduleError：kDetail 走 `RenderReport`（带 IR 定位的高亮报告）、kFast 只给一句话、kNone 连消息都不渲染——搜索式调优每秒失败上千次时的性能阀门。
- **采样族（L230-278）**：`Seed/ForkSeed`（L232-238）用线性同余引擎；`SampleCategorical/PerfectTile/PartitionedTile/ComputeLocation` 四个采样器全部带 `decision` 出参——**采样与决策分离**是可回放的关键：同一个 seed + decisions 序列 = 同一条调度路径。
- **名字寻址（L282-338）**：`GetSBlock` 按名找块，内嵌 `NotSingleResult` 错误类（L284-319，实现了 ScheduleError 的三个渲染接口，`LocationsOfInterest` 让 detail 模式能高亮全部候选块）；函数解析优先级 L320-330：显式参数 > `work_on` 设定 > 报错。
- **Split 主线（L407-521）**：本文件最有教学价值的一段。三个错误类先声明——`NotSingleInferFactorError`（L407，-1 推断层只能有一个）、`WrongFactorError`（L425，因子积必须 ≥ 循环长度）、`NonPositiveFactorError`（L453，常量因子必须为正）。`Split` 本体（L477-521）：收集因子时 dtype 过宽则向循环变量 dtype 收窄 cast（L498-501）；推断因子用 `analyzer_->Simplify(floordiv(extent + tot - 1, tot))` 即**ceildiv 补齐**（L517-519）；显式因子则 `CanProve(tot_length >= extent)` 符号证明（L520-521）——证明不了就拒绝，绝不生成静默越界的循环。
- **原语面（L385-931）**：循环变换 Merge/Fuse/Reorder/LoopPartition（L385/396/596/521）；注记族 Parallel/Vectorize/Bind/Unroll（L631-656，本质是给 For 挂 kind/attr）；缓存族 CacheRead/CacheWrite/Reindex*/CacheInplace/CacheIndex/ReIndex（L665-763）；局部性族 ReadAt/WriteAt/ComputeAt/ReverseComputeAt/ComputeInline/ReverseComputeInline（L764-839）；存储族 StorageAlign/SetScope/UnsafeSetDType（L851-876）；归约族 DecomposeReduction/RFactor（L877/886）；Blockize 两个重载（L896/L905）与 Tensorize 两个重载（L915/L924，经 `tirx::TensorIntrin::Get(intrin)` 取张量内联描述）。
- **Annotate 值净化（L935-990）**：`CheckAndGetAnnotationValue` 递归处理 String/IntImm/FloatImm/PrimExpr/Array/Map，并**优先把表达式坍缩为字面量**（L942-948、L954-960）——注记不该携带未物化的 RV。
- **布局与收尾（L1024-1099）**：`TransformLayout`（L1025）先用 symbol_table 把 index_map 里的 RV 变量 Substitute 成具体表达式（L1031-1038）再下发；`DecomposePadding/PadEinsum`（L1055/1064）、`RollingBuffer`（L1073）、`UnsafeHideBufferAccess`（L1082，名字自带警告：隐藏 buffer 访问会破坏依赖分析，仅限明确知道自己在干什么的人）。

## 外部连接

- **上游**：`ScheduleState`（stmt2ref/block_info 的维护者，每条原语落盘后更新）；`s_tir::` 原语实现（`src/s_tir/schedule/primitive/` 下几十个 .cc）；`tirx::TensorIntrin` 注册表；`arith::Analyzer`。
- **Python 面**：`python/tvm/s_tir/schedule/_schedule.py` 的 `Schedule` 类按 FFI 调到这里；`_typing.py` 定义 LoopRV/SBlockRV 的 Python 侧类型。
- **下游**：`traced_schedule.cc` 把每次调用记成 Instruction 进 Trace——meta_schedule 的搜索策略（explain-07）在 trace 上做变异与回放；dlight（explain-06）的规则最终也编译成一串对这些原语的调用。
- **RV 机制**：`CreateRV`（concrete_schedule.h L212-234）把 StmtSRef/整数包成随机变量登记进 symbol_table，`GetSRef` 反向物化——随机变量让"先采样后使用"的搜索代码不必立即确定数值。

## 数据流

以 meta_schedule 采样一次 tiling 为例：策略层先 `SamplePerfectTile(loop, n=3, ...)`（L249-259）→ rand_state 抽出因子，返回的 `Array<ExprRV>` 是**符号**（可能是 None 表示待推断）→ 策略决定调用 `Split(loop, factors)` → L487-521 把 RV 逐个 `Get()` 物化，-1 因子 ceildiv 推断，全部过 arith 证明 → `s_tir::Split` 真正改写 IR（重建 For 嵌套）→ `DebugVerify()` 全树复核 → 新循环包成 LoopRV 返回。traced_schedule 同时把 `(inst, decision)` 追加进 trace——日后重放时 decision 直接注入，跳过随机性。

## 设计决策

1. **校验/实现/复核三拍分离**：ConcreteSchedule 管契约（参数合法性、可证明性），primitive 管 IR 手术，DebugVerify 管事后审计——失败原语的中间状态不外泄。
2. **可回放性是一等公民**：LCE 种子 + decision 出参 + ForkSeed 分叉（L236-238），让多任务并行调优各自持有独立随机流，且任何调度序列可精确重现——对"调优结果不可复现"这一业界顽疾的正面回答。
3. **错误也是 API**：ScheduleError 体系三接口（FastErrorString/DetailRenderTemplate/LocationsOfInterest）把"给搜索算法的短消息"与"给人的带高亮报告"统一在一个对象里，渲染档位按性能需要切换。
4. **analyzer 不可跨拷贝共享**（L205）：arith 缓存是状态污染源，Copy 时宁可重建——细小但关键的不可变性纪律。
5. **过期 sref 哨兵化**（L102）：调度变换会使旧引用失效，拷贝语义选择"携带墓碑继续"而非异常终止，配合 symbol_table 让上层可以做防御式编程。

## 新人提示

- 读调度代码的姿势：先在本文件看方法签名的校验逻辑，再去 `primitive/` 目录找同名实现——例如 Split 的真身在 `primitive/loop_splitting.cc` 类文件中。
- `GetSBlock` 报 "Found N blocks" 时用 L326-330 的提示显式传函数名或先 `work_on`。
- 调试随机调优不确定：确认 `ForkSeed`/decision 记录完整；dlight 这种确定性规则线则完全不走采样。
- `Unsafe*` 前缀（L867/L1082）是明确的契约逃逸口，用前读 primitive 侧注释，依赖分析失效的后果自负。
