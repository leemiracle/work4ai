# smallpond/dataframe.py 精讲——用户 API 门面

> 原文件：`smallpond/smallpond/dataframe.py`（668 行，两个类）

## 一、角色定位

dataframe.py 是用户与 smallpond 的全部界面：`smallpond.init()` 返回这里的 Session，`session.read_parquet(...)` 返回这里的 DataFrame。它刻意做薄——Session 负责"造计划"，DataFrame 负责"链变换 + 触发计算"，真正的优化、编译、执行全部下沉到 logical/execution 各层。读懂这一个文件，就掌握了 smallpond 的完整用户心智模型：**一切变换惰性、一切落盘显式、一切中间结果是文件**。

## 二、内部结构

**Session（继承 session.py 的 SessionBase）**：
- 数据入口六件套：`read_csv/read_parquet/read_json`（各自构造 CsvDataSet/ParquetDataSet/JsonDataSet + DataSourceNode）、`from_items/from_pandas/from_arrow`（内存数据源）。
- `partial_sql(query, *inputs)`：逐分区执行 SQL，`{0}{1}` 占位符引用输入 DataFrame，是 join/复杂计算的官方入口（docstring 给了先按 key 哈希分区再 join 的范例）。
- `wait(*dfs)`：等待多个输出 DataFrame，支撑"一份数据多路输出"的流水线。
- `graph()`：graphviz Digraph 导出当前会话全部节点。
- `shutdown()`：写 job 状态文件（success/failure@时间戳），成功才清理运行时目录。
- 关键字段 `_node_to_tasks: Dict[Node, List[Task]]`——已编译任务的缓存，跨 DataFrame 复用。

**DataFrame**：持有 `session + plan + optimized_plan（惰性）+ need_recompute`。`_get_or_create_tasks()` 是编译主路径：先 `Optimizer(exclude_nodes=已算节点).visit(plan)`，再查缓存，最后 `Planner(runtime_ctx).visit(optimized_plan)` 生成任务。变换层 repartition（三分支）/random_shuffle/partial_sort/filter/map/flat_map/map_batches/limit/write_parquet(_lazy)；动作层 count/take/take_all/to_pandas/to_arrow。

## 三、外部连接

向下 `from smallpond.logical.node import *` 与 `logical/dataset.py` 全量引入（算子与数据集工厂）；执行依赖 ray：`task.run_on_ray()` 提交任务拿 ObjectRef，`_compute()` 里 `ray.get` 阻塞收口，`wait()` 用 `ray.wait` 非阻塞轮询。SessionBase（session.py）提供 RuntimeContext 生命周期与 prometheus/grafana 监控启动。Optimizer/Planner 分别来自 logical/optimizer.py、logical/planner.py。清理路径用 io/filesystem.py 的 `remove_path`。

## 四、数据流

典型链路：`sp.read_parquet("in/*.parquet")` → DataSourceNode → `df.map('a+b as c')` 仅构造 SqlEngineNode → `df.write_parquet('out')` 追加 DataSinkNode 并 `compute()`。compute 内部：optimizer 裁掉已有结果的子图 → planner 递归编译 → `ray.get([task.run_on_ray() ...])` 全量等待 → 返回 `List[DataSet]`。多输出场景：`o1 = df.write_parquet_lazy('out1'); o2 = df.map(...).write_parquet_lazy('out2'); sp.wait(o1, o2)`——两次编译共享上游任务的 key（`_node_to_tasks` 命中），中间结果不重算。健壮性细节：`_compute` 对 ray 的 `RuntimeEnvSetupError` 做 3 次指数退避重试（源码注释指明是 Ray 已修但 Python 3.8 无法升级的 bug，`time.sleep(10 << retry_count)`）。

## 五、设计决策

- **SQL 优先的双模 API**：filter/map/flat_map/sort 都接受 SQL 表达式或 Python 函数，docstring 反复标注 "SQL expression is preferred as it's more efficient"——SQL 路径进 DuckDB 向量化引擎，函数路径退化为 ArrowBatchNode 逐行 Python 循环（`[func(row) for row in table.to_pylist()]`），性能差一个量级。
- **repartition 三分派**：`by` → ShuffleNode（按列值分区）、`hash_by` → HashPartitionNode（哈希分区）、默认 → EvenlyDistributedPartitionNode（均匀分摊，可 by_rows）——一个入口收编三种洗牌语义。
- **random_shuffle 的复合实现**：先 HashPartitionNode(random_shuffle=True) 借 `random()` 列做全局哈希打乱，再逐分区 `order by random()`——全局洗牌被拆成可并行的两段，这是分布式系统"全局乱序 = 分区乱 + 区内乱"的标准分解。
- **need_recompute 沿链传播**：`recompute()` 置 True 后所有下游 DataFrame 继承该标志，compute 时先删 completed_task_dir 下对应节点的标记目录再强制重算——缓存失效以子图为单位。
- **take 的 limit 下推**：已算或纯 DataSource 直接读，否则先 `self.limit(limit)._compute()`，避免全量物化。
- **诚实的 FIXME**：`count()` 里注释"don't use ThreadPoolExecutor because duckdb results will be mixed up"——保留了一个真实工程坑的现场。

## 六、新人提示

partial_sql 做 join 必须先对两边做同数哈希分区，否则结果错误（无 shuffle 引擎兜底）。`is_computed()` 只查任务是否完成，不代表磁盘仍在（shutdown 清理过就没了）。调试三板斧：`session.graph()` 看 DAG、开 DEBUG 日志看 Optimizer 前后的计划打印、`df.plan` 的 repr 直接看算子链。记住动作语义：只有 write/take/count/to_* 会触发执行，其余全是免费的计划构造。

partial_sql 的查询串会原样传给 SqlEngineNode，因此 SqlEngineNode docstring 里的全部占位符（`{0}/{1}` 输入、`{batch_index}`、`{rand_seed}`、`{__data_partition__}` 等）与参数（`udfs=`、`batched_processing=`、`per_thread_output=`）在 DataFrame 层同样可用——DataFrame 方法签名里的 `**kwargs` 就是透传通道；想精细控制某个节点的资源与压缩参数，直接在变换调用处传 kwargs 即可，不必下沉到 Node 层。
