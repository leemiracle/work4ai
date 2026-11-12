# 01 · core.py 编译管线：从 Python 函数到每设备独立 jit

## 角色定位

`src/jaxpp/core.py`（4071 行）是全库心脏，也是 JAX 非标准用法的深水区：它把一个含流水线注解的普通 JAX 函数，编译成 mpmd 维上每台设备各持一段的独立 jit 程序。两个公开入口 `mpmd_jit_with_loop`（`src/jaxpp/core.py:4013`）与 `mpmd_jit_by_yield`（`src/jaxpp/core.py:4047`）只是给私有工厂 `_mpmd_jit`（`src/jaxpp/core.py:3984`）配不同 Strategy 策略对象（ABC 在 `src/jaxpp/core.py:3252`）：FunctionWithLoop（`src/jaxpp/core.py:3267`）吃"函数体内含 scan 循环"的写法，FunctionWithYield（`src/jaxpp/core.py:3285`）吃"mark_stage_end 注解"的写法。配套的 `jax_primitives.py`（1412 行）注册自定义原语，`licm.py`/`sharding_inference.py` 是两个优化 pass。

## 内部结构

编译主干挂在 TraceableFunction（`src/jaxpp/core.py:3316`）上，三段式：compile（`src/jaxpp/core.py:3328`）= trace_and_place（`src/jaxpp/core.py:3342`）→ infer_intermediate_shardings（`src/jaxpp/core.py:3751`）→ mpmdify（`src/jaxpp/core.py:3912`）。追踪期 AllReduceRewriteTracer/AllReduceRewriteTrace 两级追踪体系（`src/jaxpp/core.py:167/:178`）经 propagate_and_rewrite_adds（`src/jaxpp/core.py:327`）重写跨设备加法为显式 all_reduce 原语（`src/jaxpp/jax_primitives.py:214`）。任务化分两路：yield 路线按 pipeline_yield 方程聚类（cluster_by_yield_eqns `src/jaxpp/core.py:976`、clusters_to_tasks `src/jaxpp/core.py:1072`、cluster_jaxpr `src/jaxpp/core.py:1128`）；loop 路线在循环体内外包任务（wrap_into_tasks_inside_loop `src/jaxpp/core.py:1188`、wrap_into_tasks_after_loop `src/jaxpp/core.py:1434`、统一入口 `src/jaxpp/core.py:1601`）。每个任务由 make_task_eqn（`src/jaxpp/core.py:791`）包成 TaskEqn 方程（类定义在 `src/jaxpp/jax_primitives.py:1373`），并挂 CommunicationEffect 自定义 effect（`src/jaxpp/jax_primitives.py:727`）阻止 XLA 重排跨任务通信。

## 外部连接

上游消费 pipeline_yield_p 原语（`src/jaxpp/jax_primitives.py:896`）与 TaskType（`src/jaxpp/types.py:84`）；调度器经 reorder_nodes_with_schedule+infer_times（`src/jaxpp/core.py:1876/:2465`）注入时间表；输出端接 MpmdArray 与 dime2 传输层。jaxpr_utils.py 四件套：partition_remat/partition_eqns 按谓词切方程（`src/jaxpp/jaxpr_utils.py:58/:103`）、defs_and_uses 活性分析（`:207`）、substitute 替换（`:244`）。CommToken（`src/jaxpp/jax_primitives.py:71`）建模通信完成信号，PjitKwargs（`:1055`）处理 jit 参数透传，compiled_task/callable_task（`:1125/:1095`）承担任务级编译缓存。

## 数据流

一条 jaxpr 的完整旅程：①预处理 preprocess_jaxpr（`src/jaxpp/core.py:3227`）；②活性分析 compute_needed（`src/jaxpp/core.py:526`）决定任务真实输入；③去重融合 deduplicate_task_jaxprs/fuse_groups（`src/jaxpp/core.py:2339/:2384`）；④调度重排；⑤插传输 compute_transfers/add_transfers（`:2035/:2079`）与 bufferize_recvs（`:2688`）；⑥check_global_jaxpr 终检（`:2853`，含 transfer FIFO 校验）；⑦to_local_jaxprs（`:2917`）切出每设备局部 jaxpr 交给 jit。注意 `_get_fused_jaxpr_cached` 是 @overload 三连（`src/jaxpp/core.py:2218/:2231` 签名桩 + `:2244` 真实现），别被三段同名函数迷惑。

## 设计决策

三个值得咀嚼的取舍：其一，JAX 私有 API 全部经 `jax_compat/__init__.py` 垫片隔离，升级 JAX 只改一处。其二，LICM+部分求值+CSE 三合一 pass（licm.py 的 partial_eval_jaxpr `src/jaxpp/licm.py:323`、partial_eval_loop `:576`、hoist_and_cse_pscan_invariant_equations `:680`）默认关闭（`src/jaxpp/env_vars.py:5` 的 JAXPP_ENABLE_LICM 默认 False）——激进优化不默认吃用户。其三，sharding 推断做了两代：infer_shardings（`src/jaxpp/sharding_inference.py:548`）与 fast 版 infer_shardings2（`src/jaxpp/sharding_inference.py:486`），reconcile_shardings（`src/jaxpp/sharding_inference.py:241`）负责调和显式标注与推断结果；`docs/compilation.md` 讲清了 Auto 轴（借 XLA SPMD 传播，需一次"只为拿 sharding"的完整编译）与 Explicit 轴（类型携带、免编译）的分野。

## 新人提示

按 ①→⑦ 顺序读 core.py 最不易迷路；先读 `docs/compilation.md`（135 行）再进源码。调试期打开 `scripts/jax-env.sh` 的 IR dump 三路开关（jaxpr/stablehlo/hlo）看中间产物，print_jaxpr/dump_jaxpr（`src/jaxpp/core.py:3678/:3705`）现成可用；common_passes（`src/jaxpp/core.py:3720`）是常规 pass 调用顺序的"地图索引"。改完用 tests/test_task_compile.py 快速回归。
