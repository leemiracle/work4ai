# smallpond/execution/task.py 精讲——执行引擎的心脏

> 原文件：`smallpond/smallpond/execution/task.py`（3197 行，全仓最大文件）

## 一、角色定位

task.py 是 smallpond 从"逻辑计划"落到"物理执行"的翻译终点。用户在 DataFrame 上写下的每一条链式变换，经过 planner.py 编译后都会变成这里的一个个 Task：**每个 Task 接收一组输入 DataSet，产出一个输出 DataSet，Task 之间靠依赖边连成 DAG**。它是调度器派发的最小单元、执行器运行的最小单元，也是容错重试的最小单元——docstring 明确要求"Tasks should be idempotent. They can be retried if they fail"，整份文件的目录布局、随机种子、原子提交设计都为这一句服务。

## 二、内部结构

文件自顶向下分四块：

1. **基础设施**：`JobId`/`TaskId`/`TaskRuntimeId`（task_id + sched_epoch + retry_count 三元组，重试会生成新 runtime id）、`PerfStats`（cnt/min/max/p50-p99 九元组）、`RuntimeContext`（job 级状态：job_root 下的 output/staging/temp/log/queue 目录布局、NUMA/CPU/GPU/内存探测、probe 超时参数、`started_task_dir`/`completed_task_dir` 两个 ray 断点目录）。
2. **Task 基类**（`__slots__` 20 个字段）：构造时声明 `cpu_limit/gpu_limit/memory_limit` 与 `PartitionInfo` 列表；`input_deps` 只在 planning 期维护 DAG，执行前清空引用以便独立 pickle 到 worker（源码注释大写警告 DO NOT use at execution time）。
3. **任务家族**（约 20 个具体类）：数据源汇（DataSourceTask/DataSinkTask/MergeDataSetsTask/SplitDataSetTask）；分区家族（PartitionProducerTask/PartitionConsumerTask，下派 RangePartitionTask 和 HashPartitionTask，后者经 `create(engine_type)` 工厂分出 HashPartitionDuckDbTask 与 HashPartitionArrowTask 双引擎）；计算家族（PythonScriptTask、ArrowComputeTask/ArrowStreamTask/ArrowBatchTask、PandasComputeTask/PandasBatchTask、SqlEngineTask），除 PythonScript 外多数混入 `ExecSqlQueryMixin`；最后是 RootTask 与 ExecutionPlan 汇总。
4. **ExecSqlQueryMixin**：所有走 DuckDB 的任务共享的连接准备、输入视图创建、查询执行与指标抽取逻辑。

## 三、外部连接

向上：logical/planner.py 遍历 Node 时调用各 Task 构造器，`task.node_id` 回填逻辑节点 id。向下：Task 继承自 workqueue.py 的 `WorkItem`（状态机 INCOMPLETE→SUCCEED/FAILED/CRASHED，`exec()` 驱动 initialize/run/finalize/cleanup 生命周期），由 scheduler.py 派发进 workqueue，executor.py 消费。横向：重度依赖 duckdb（查询引擎）、pyarrow（列存）、ray（`run_on_ray()` 返回 `_dataset_ref`，跨进程传递输出 DataSet）；输入输出统一走 logical/dataset.py 的 DataSet 抽象。

## 四、数据流

一个 Task 的完整旅程：planning 期在 scheduler 节点实例化 → pickle 发往 worker → `initialize()`：建 runtime/temp 目录、按需 cProfile、`set_memory_limit()` 设 RLIMIT_DATA、`arrow.set_cpu_count(cpu_limit)`、播种确定性随机数 → `run()` 干活 → `finalize()`：把 `runtime_output_abspath`（staging 下）`os.rename` 到 `final_output_abspath`，收集 perf_metrics → pickle 回 scheduler。

以最核心的 `SqlEngineTask.run()` 为例：若启用 `batched_processing` 则先按 `max_batch_size = memory_limit // 2` 把输入 parquet 分批；每批 `duckdb.connect(":memory:")` 建临时连接 → `prepare_connection`（`SET threads/memory_limit/temp_directory/preserve_insertion_order=false` 等 + `setseed`）→ `create_input_views` 为每个输入 DataSet 建 `CREATE VIEW` → 查询模板 format 填入视图名 → 最后一条查询包成 `COPY (...) TO '...' (FORMAT PARQUET, KV_METADATA ..., PER_THREAD_OUTPUT ..., FILENAME_PATTERN ...)` 落盘。DuckDB 的 `EXPLAIN ANALYZE` JSON 被 `exec_query` 解析，从中抽取 TABLE_SCAN/COPY_TO_FILE 的基数与耗时进 perf_metrics。

## 五、设计决策

- **staging + 原子 rename 提交协议**：运行时输出先写 staging，成功才 rename 到最终目录。失败任务不污染输出，重试与投机执行（`allow_speculative_exec`）因此天然安全——这是"免常驻服务"架构下用文件系统模拟事务的典型手法。
- **内存即并行度的资源模型**：memory_limit 未指定时按 `usable_memory_size * cpu_limit / usable_cpu_count` 推导，即"按 CPU 配内存"；enforce 模式下软限 1.2 倍、硬限 1.5 倍 RLIMIT_DATA。
- **每任务临时 DuckDB 连接**：不用常驻服务，连接级 `SET preserve_insertion_order=false` 牺牲顺序换并行，是 DuckDB 官方推荐的大数据姿势。
- **确定性随机**：task id + job seed 派生 numpy/python 随机流，并 `setseed` 注入 DuckDB——同一任务重试结果逐字节一致，这是幂等的前提。
- **可测性内建**：`inject_fault()` 按 `uniform_failure_prob` 概率抛 InjectedFault，配合调度器做崩溃恢复演练。
- **HashPartition 双引擎**：duckdb 引擎（SQL 表达分区）与 arrow 引擎（ParquetWriter 直写）二选一，`write_buffer_size` 等参数按 npartitions 自适应。

## 六、新人提示

入门路线：先精读 `SqlEngineTask.run + process_batch`、`Task.initialize/finalize`，再横扫任务类清单（`grep ^class`）建立全景。注意 `__slots__` 意味着不能随意挂属性（pickle 体积控制）；`input_deps` 在执行期为 None 是特性不是 bug；调 row group 参数看 `adjust_row_group_size`（行数/字节/行组数三上限）。查 OOM 先看 `OutOfMemory`（duckdb.OutOfMemoryException 的转译）与 memory_overcommit_ratio 的关系。
