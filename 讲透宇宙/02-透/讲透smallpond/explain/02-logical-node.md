# smallpond/logical/node.py 精讲——逻辑算子全集

> 原文件：`smallpond/smallpond/logical/node.py`（2024 行）

## 一、角色定位

node.py 是 smallpond 逻辑计划层的全部家当：用户在 DataFrame API 上做的每一个动作——读文件、过滤、map、重分区、union、写盘——在这里都有一个对应的 Node 类。它是**用户语义与物理执行之间的中间表示（IR）**：DataFrame 持有 Node 构成的 DAG，Optimizer 在其上做剪裁，Planner 遍历它调用 `create_task` 生成 execution/task.py 里的 Task。可以说 node.py 定义了"计算是什么"，task.py 决定"计算怎么跑"。

## 二、内部结构

文件分四层：

1. **Context**：逻辑计划上下文，负责分配自增 `NodeId`，更重要的是维护三类 UDF 注册——`create_python_udf`（Python 函数）、`create_external_module`（外部 .so 模块）、`create_duckdb_extension`（.duckdb_extension 动态库），全部收进 `self.udfs` 字典，后续随任务 bind 到 DuckDB 连接。
2. **Node 基类**：构造参数 `ctx/input_deps/output_name/output_path/cpu_limit/gpu_limit/memory_limit`；`task_factory` 静态装饰器（包装 create_task，自动回填 `task.node_id`、`task.location`，登记 `generated_tasks`）；`slim_copy()` 产出剥离依赖的浅拷贝（给 pickle 瘦身）；`add_perf_metrics/get_perf_stats`（p50-p99 分位统计）。
3. **算子族**（约 28 个类）：源汇（DataSourceNode；DataSinkNode 两阶段写出——先写运行时输出再收集为最终目录）；计算（PythonScriptNode、ArrowComputeNode、ArrowStreamNode、ArrowBatchNode、PandasComputeNode、PandasBatchNode、SqlEngineNode）；组合（UnionNode、ConsolidateNode、RootNode）；分区家族（PartitionNode 基类 → RepeatPartitionNode / UserDefinedPartitionNode / EvenlyDistributedPartitionNode / LoadPartitionedDataSetNode / HashPartitionNode → ShuffleNode、RangePartitionNode）；投影与限量（ProjectionNode；LimitNode 直接继承 SqlEngineNode）。
4. **LogicalPlanVisitor / LogicalPlan**：泛型访问器与计划封装，是 optimizer.py 和 planner.py 的遍历基类。

## 三、外部连接

上游是 dataframe.py：每个 API 方法就是一次 Node 构造——`filter('a>1')` 造 SqlEngineNode、`repartition(10, hash_by='id')` 造 HashPartitionNode、`repartition(10, by='bucket')` 造 ShuffleNode、`write_parquet_lazy` 造 DataSinkNode。Context 的 UDF 注册对接 logical/udf.py 的 PythonUDFContext/ExternalModuleContext/DuckDbExtensionContext 三态绑定。向下，每个 Node 的 `create_task(runtime_ctx, input_deps, partition_infos)` 产出对应 Task 类实例。横向上 LogicalPlanVisitor 被 logical/optimizer.py（子类 Optimizer）与 logical/planner.py（子类 Planner）继承，是"计划处理管道"的骨架。

## 四、数据流

链式调用期：DataFrame 每次变换 new 一个 Node，`input_deps=(self.plan,)` 指向父节点，DAG 向后生长，**期间零计算**。compute 期：Optimizer 先 `visit`（exclude 已算节点实现子图复用），Planner 再递归 `visit`——子节点先编译，把自己的 Task 列表传给父节点的 create_task 作为 input_deps，配合 PartitionInfo（分区维度+索引）决定并行度。输出落点由 docstring 精确定义：`{job_root}/output/{output_name}/{task_runtime_id}/{output_name}-{task_runtime_id}-{seqnum}.parquet`，其中 runtime_id = `job_id.task_id.sched_epoch.retry_count`，重试不覆盖旧结果。

## 五、设计决策

- **声明式资源，不强制执行**：cpu/gpu/memory limit 只指导调度，docstring 三次强调 "smallpond does NOT enforce this limit"；但 `cpu_limit = max(cpu_limit, gpu_limit * 8)` 的兜底写法暗示了实际负载比例经验。
- **算子边界 = 落盘边界 = 容错边界**：每个 Node 的输出都是一组 parquet 文件，天然形成断点——Session 的 `_node_to_tasks` 以节点为单位缓存，派生第二个 DataFrame 时上游不重算。这是"文件即数据血缘"的设计哲学。
- **HashPartitionNode 一节点三模式**：正常 `hash_columns` 哈希、`random_shuffle=True` 时 hash_columns 被替换为 `["random()"]`（借 SQL 随机函数）、`shuffle_only=True` 时按 `data_partition_column` 列值直接定区；`engine_type` 可选 duckdb/arrow 双后端，`hive_partitioning` 仅 duckdb 引擎可用——约束关系全用 assert 表达。
- **构造位置溯源**：`__init__` 用 `traceback.extract_stack` 反向找第一个不在 node.py/dataframe.py 里的栈帧，存进 `self.location`。任务报错时能直接指到用户源码行，这个细节极大降低排障成本。
- **LimitNode 继承 SqlEngineNode**：limit 不是专门算子，就是一条 `select ... limit` SQL——体现"能用 SQL 就不写代码"的取向。

## 六、新人提示

先读 `Node.__init__` 完整 docstring（输出路径格式、资源语义都在里面）；再对着 dataframe.py 每个方法看它构造哪个 Node，建立 API↔算子映射表。加新算子的三步：写 Node 子类 + create_task 分支 + 对应 Task 类。排障时善用 `self.location`（repr 里能看到）与 `generated_tasks` 列表核对编译结果。改分区类节点要特别注意 `nested` 维度与 PartitionInfo 的去重断言（重复 dimension 直接 assert 失败）。

值得单独认识的是 **SqlEngineNode**（全库被构造最频繁的节点）：`sql_query` 支持字符串或列表——多条顺序执行、只有最后一条的结果落盘；查询里除 `{0}{1}` 输入占位符外还有 `{batch_index}/{query_index}/{rand_seed}/{__data_partition__}` 四个运行时占位符；`udfs` 非空时资源自动降级到 `min(cpu_limit, 3)` 与 `min(memory_limit, 50*GB)`（docstring 直言 DuckDB 的 UDF 执行并行度不高）；`relax_memory_if_oom` 提供"OOM 就翻倍内存重试"的自愈开关；`per_thread_output=True` 默认开启——每线程一个文件换写并行（DuckDB 官方 tips 背书）。
