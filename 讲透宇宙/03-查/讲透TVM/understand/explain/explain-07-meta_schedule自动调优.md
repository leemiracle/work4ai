# explain-07 · meta_schedule 自动调优：TuneContext 与 TaskScheduler 双子星

## 角色定位

meta_schedule 是 TVM 的**搜索式自动调优框架**（与 explain-06 的 dlight 规则式构成两条路线），在 fork 中整体搬到 `python/tvm/s_tir/meta_schedule/`。两个文件撑起骨架：`tune_context.py`（295 行）是**单任务调优的全资源容器**——docstring L65 "contain all resources for a tuning task"，把 workload（mod）、目标（target）、设计空间生成器（space_generator）、搜索策略（search_strategy）、随机状态、线程数打包成一个 C++ 对象；`task_scheduler/task_scheduler.py`（285 行）是**多任务编排器**——一个模型会抽出几十个子任务（conv2d/dense/gemm…），谁来先跑、跑多少次、何时终止，由它裁决。`tune.py` 的 `tune_tir/tune_relax` 一条龙入口最终都汇聚到这两者。

## 内部结构

**TuneContext**（行号锚定 tune_context.py）：七个字段（L89-96）——mod/target/space_generator/search_strategy/task_name/logger/rand_state/num_threads。构造器（L98-160）是一段防御性编程示范：PrimFunc 经 `_normalize_mod`（L47-60，@register_global_func 注册的全局函数：补 `global_symbol="main"`、`tirx.noalias=True`、单函数模块统一改名 main）包成 IRModule（L117-118）；target 字符串就地转 Target（L119-121）；space_generator/search_strategy 支持字符串直传并工厂化（L122-127）；L130-136 用 `type() is` 精确类型检查拦下"直接实例化抽象 SearchStrategy"的误用（L128-129 注释解释为何不用 isinstance——子类合法）；num_threads 支持 "physical"/"logical" 关键字经 `cpu_count` 解析（L139-148）。L149-160 走 FFI 构造后**立即调 `TuneContextInitialize`**（L160）——C++ 侧完成 rand_state 播种等初始化。

方法层全是"校验+委托"：`generate_design_space`（L162-178）委托 space_generator；`pre_tuning`（L180-235）为 EvolutionarySearch 自动补 `MemoryDatabase()` 与 `RandomModel()` 默认件（L223-228）；`generate_measure_candidates`（L248-262）返回一批待测候选或 None（搜索结束）；`notify_runner_results`（L264-284）把测量结果回灌策略；`clone`（L286-294）经 FFI 深拷贝。四个方法合起来正是搜索主循环的四个拍点：**出空间→预处理→出候选→收结果**。

**TaskScheduler**（锚定 task_scheduler/task_scheduler.py）：`TaskRecord`（L45-58）记录单任务运行态——task_weight/flop/is_terminated/build_error_count/run_error_count/三轮结果列表。抽象接口 `TaskScheduler`（L60）的核心方法群：`next_task_id`（L72-80）、`join_running_task`（L82-95）、`terminate_task`/`touch_task`（L150-168）、`print_tuning_statistics`（L170-172）；总入口 `tune`（L97-148）一次性收齐 tasks/task_weights/max_trials_global/max_trials_per_task/num_trials_per_iter/builder/runner/measure_callbacks/database/cost_model 十一件套转发 FFI——真实调度循环在 C++ 侧（`src/s_tir/meta_schedule/task_scheduler.cc`），Python 只是壳。工厂 `create`（L174-190）支持 "gradient"（默认，GradientBased）/"round-robin" 两种（实现极薄：round_robin.py L29 起仅 37 行、gradient_based.py L29 起 56 行，策略真身全在 C++）。扩展协议是 `_PyTaskScheduler`（L196-219）+ 用户面 `PyTaskScheduler`（L222-284）：`_tvm_metadata`（L230-234）声明可被子类覆盖的三个方法，`self._outer()`（L253、L284）取 C++ 外壳指针——**Python 子类方法被 C++ 回调的官方通道**。

## 外部连接

- **上游组件**：`space_generator/`（PostOrderApply 生成设计空间——本质是调用 explain-05 的调度原语做随机变换并记 trace）；`search_strategy/`（EvolutionarySearch 进化搜索 + ReplayTrace/ReplayFunc 回放）；`builder/`（LocalBuilder/PoolBuilder 产 kernel 二进制）；`runner/`（LocalRunner/RPCRunner 真机测量）；`database/`（调优记录持久化，支持 JSON/断点续跑）；`cost_model/`（XGBModel 用 148 特征预测耗时）。
- **relax 集成**：`relax_integration.py` 的 meta_schedule_relax pass 从 relax 图抽任务表（ExtractedTask）；`tir_integration.py` 对应 tirx 线。
- **与 explain-05 的闭环**：搜索策略产出的每个候选都是一串调度指令 trace，经 TracedSchedule 回放成具体 Schedule——ConcreteSchedule 的 decision 出参机制（explain-05 L244）正是为此设计。
- **与 dlight 的分工**：dlight 毫秒级出默认调度，meta_schedule 分钟~小时级搜索峰值；`profiler.py` 提供两者对比的计时工具。

## 数据流

一次 `tune_tir(mod, target)`：抽取任务（每个子图一个 TuneContext，weight=flop 占比）→ TaskScheduler.tune 主循环：`next_task_id` 按梯度策略选任务（优先"单位时间吞吐提升最大"者）→ TuneContext.generate_measure_candidates 出一批候选 → Builder 并行编译 → Runner 真机测速（RPC 可跨设备）→ notify_runner_results 回灌：好结果进 database、XGB cost model 增量训练 → 循环直到 max_trials_global 耗尽或全部 is_terminated → 从 database 取每任务最优 → 回填 IRModule。

## 设计决策

1. **Context 即对象图**：TuneContext 把调优所需全部资源句柄化，C++ 侧持同一对象——Python 配置、C++ 执行，无中间转换损耗；clone 支持多随机种子并行（对应 explain-05 的 ForkSeed）。
2. **策略/调度器分离**：单任务内怎么搜（Evolutionary）与多任务间怎么分配预算（GradientBased）正交，可独立替换——PyTaskScheduler 让后者纯 Python 可扩展。
3. **默认值按需注入**（pre_tuning L223-228）：默认件只在"没给且策略确实需要"时创建，避免空配置对象满天飞。
4. **错误计数进 TaskRecord**（L53-54）：build/run 连续失败的任务可被调度器降权或熔断，防止一个坏 kernel 吞掉全部调优预算。
5. **抽象类误用防御**（tune_context.py L130-136）：`type() is` 精确匹配 + 明确报错文案，把新手最常见的"new 了个基类"在构造期拦截。

## 新人提示

- 跑调优先确认三件事：rand_state 固定（复现）、database 路径设置（断点续跑）、num_threads 选 physical（L107 默认，避免超线程伪加速）。
- 任务日志看 TaskScheduler.print_tuningStatistics 的输出；单任务细节在 TuneContext.logger（可注入自定义 logger，L108）。
- 想自定义调度顺序：继承 PyTaskScheduler 覆盖 next_task_id，注意 L253 的 `self._outer()` 用法是协议要求不是可选。
- `tirx.noalias=True`（L53）是 normalize 的硬行为——依赖别名语义的 PrimFunc 会被调优器误解，先在 IR 层面显式化。
