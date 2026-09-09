# smallpond 新人指南（简版）

> 依据：仓库 knowledge-graph.json（356 节点/898 边/9 层/12 步导览）+ README.md。生成日期：2026-09-05。

## 一、项目是什么与定位

smallpond 是 DeepSeek 开源的**轻量级数据处理框架**，计算引擎用 DuckDB，存储底座用 3FS（DeepSeek 自研分布式文件系统）。三个卖点：DuckDB 驱动的高性能、PB 级扩展能力、**免常驻服务**（no long-running services）——作业即起即走，没有 master/worker 常驻进程的运维负担。与 Spark 这类重型系统相比，它不维护元数据库、不部署调度服务器，一个 Python 进程拉起整个作业、跑完即退，运维成本趋近于零；单节点靠 DuckDB 向量化执行拿到极高效率，多节点靠 3FS 的聚合带宽横向扩展，两者结合才有了 PB 级的底气。招牌战绩是 GraySort 基准：50 计算节点 + 25 存储节点的 3FS 集群上，**30 分 14 秒排完 110.5TiB 数据，平均吞吐 3.66TiB/min**。MIT 许可，支持 Python 3.8–3.12，`pip install smallpond` 即装即用。定位一句话：面向 AI 基础设施的数据预处理/排序/转换利器，与 3FS 是天作之合；API 风格接近 pandas/PySpark 的 DataFrame 范式，上手迁移成本低。

## 二、架构分层（按图谱 layers，自顶向下）

1. **项目配置与文档层**：README、pyproject、docs，入口面极小，主张"极小入口承载 PB 级野心"。
2. **用户 API 层（会话与 DataFrame）**：`smallpond.init()` 返回 Session，DataFrame 惰性链式变换——用户 95% 时间只打交道这一层，几乎不感知底下复杂度。
3. **逻辑计划层（节点/数据集/UDF）**：Node 算子 DAG、DataSet 统一数据抽象、UDF 注册协议，是"用户想做什么"的形式化表达。
4. **IO 与公共基础层**：parquet 多线程读写、hf3fs 挂载检测、原子 pickle 状态传递，为 3FS 而生的 IO 路径。
5. **执行引擎层（任务与工作队列）**：Task 家族把逻辑节点落地为可执行任务，含失败上报与断点恢复语义。
6. **调度与集群运行时层**：Scheduler/Executor/Driver，支持 standalone（本地 fork）、Ray 集群（NUMA 绑定）、平台适配（MPI）三种拉起形态。
7. **扩展贡献库**：社区贡献算子与工具，随主仓演进但不在核心路径上。
8. **基准与示例层**：GraySort、file_io、hash_partition、urls_sort 基准与 fstest 文件系统压测，是框架性能主张的证据链。
9. **测试体系**：TestFabric 真跑分布式的不 mock 测试哲学，覆盖容错与投机执行路径。

## 三、核心模块

- **`smallpond/__init__.py` + `dataframe.py`**：唯一入口 `init()`；Session 提供 `read_csv/parquet/json`、`from_pandas/from_arrow`、`partial_sql`（部分聚合）；DataFrame 提供 `repartition/random_shuffle/partial_sort/filter/map` 惰性变换，`compute` 时才真正执行。
- **`logical/node.py`**：DAG 积木盒，三族算子——计算族（PythonScriptNode 用户自定义、ArrowStreamNode 流式、SqlEngineNode SQL）、分区族（Hash/Range/Evenly/Shuffle）、收尾族（DataSink/Root/Projection/Limit）；LogicalPlanVisitor 统一遍历协议。
- **`logical/dataset.py`**：一切数据的统一表达；ParquetDataSet 是性能核心（行级/文件级分区、大小估算）。
- **`logical/planner.py` + `optimizer.py`**：Visitor 式计划编译，为节点生成 Task 织出 ExecutionPlan；Optimizer 做列裁剪下推减少 IO。
- **`execution/task.py`**：Task 基类（依赖就绪/输入解析/失败上报）；ExecSqlQueryMixin 统一 DuckDB 连接与 UDF 注册；ArrowStreamTask 支持分批与断点恢复；HashPartitionTask 三兄弟体现"同一算子多实现"演进。
- **`execution/scheduler.py` + `executor.py` + `workqueue.py`**：WorkItem/WorkQueue（内存+文件系统两种实现）是 scheduler→executor 任务通道；Scheduler 驱动调度主循环、失败重试与投机执行；RemoteExecutor 状态机管健康与资源水位。
- **`io/arrow.py` + `io/filesystem.py`**：`dump_to_parquet_files` 按 row group/文件大小切分多线程写盘；`load_from_parquet_files` 按行范围加载；原子 pickle dump/load 撑起跨进程状态传递。
- **`logical/udf.py`**：把 Python 函数、外部模块、DuckDB 扩展三种能力统一注册进 SQL，一条 `@udf` 装饰器即可让自定义逻辑进 DAG。
- **`session.py` + `execution/task.py:RuntimeContext`**：SessionBase 管理自身 spawn、prometheus/grafana 监控、graph/timeline 周期 dump；Config 合并命令行参数与环境变量；RuntimeContext 探测 CPU/NUMA/GPU/内存并定义作业目录布局，是全框架共享的运行环境描述。
- **`execution/driver.py` + `manager.py` + `worker.py`**：部署形态三件套。Driver 是理解部署差异的最佳入口——standalone 模式下它直接在本地 fork 出 scheduler 与 executors；Ray 模式下 JobManager 按节点拉起进程组，worker.py 以 NUMA 绑定方式启动 Ray worker；platform/base.py 则抽象出 MPI 等平台适配接口。同一套执行引擎，三种拉起方式，代码路径在 Driver 处分岔。

- **`benchmarks/` 与 `tests/`**：gray_sort_benchmark 编排"生成→范围分区→局部排序→归并校验"全流程；urls_sort 的 v1（直接用 Driver）与 v2（DataFrame API）对照是理解 API 演进的最佳材料；TestFabric 基类 fork 真实 scheduler/executor 子进程搭建执行环境，几乎所有测试都继承它。

## 四、快速上手（摘自 README）

```bash
pip install smallpond
wget https://duckdb.org/data/prices.parquet
```

```python
import smallpond
sp = smallpond.init()
df = sp.read_parquet("prices.parquet")
df = df.repartition(3, hash_by="ticker")
df = sp.partial_sql("SELECT ticker, min(price), max(price) FROM {0} GROUP BY ticker", df)
df.write_parquet("output/")
print(df.to_pandas())
```

开发调试：`pip install .[dev]` 后 `pytest -v tests/test*.py` 跑单测；`pip install .[docs]` + `cd docs && make html` 构建文档。想看分布式形态，直接读 benchmarks 下脚本：GraySort 全流程编排展示了 repartition/partial_sort 等算子在真实 PB 级作业里的组合方式；examples/fstest.py 则可用来直接压测 3FS 文件系统带宽，验证存储侧是否达标。新手第一周建议只碰 API 层，不必碰集群配置。

## 五、学习路径（按 12 步导览串讲）

**入门段（步 1–2）**：读 README 与 pyproject 建立"免常驻、PB 级"直觉，体会极小入口面如何承载这一主张 → 精读 `dataframe.py` 的 Session/DataFrame 两个类，逐行对照 Quick Start 示例，体会惰性执行：所有链式调用只是在搭 DAG，`compute`/写出时才触发整图执行。
**计划段（步 3–6）**：看 SessionBase/Config/RuntimeContext 会话基建（监控、NUMA 探测、作业目录布局）→ DataSet 数据抽象（重点 ParquetDataSet 的行级/文件级分区与大小估算，RowRange 的行范围切分数学）→ 算子节点三族体系与 LogicalPlanVisitor 遍历协议 → Planner/Optimizer 如何把"用户想做什么"翻译成"机器怎么跑"，注意 broadcast 输入的专门处理与列裁剪下推。
**执行段（步 7–9）**：task.py 任务全景（Task 基类约 50 个方法，覆盖依赖就绪、输入解析、失败上报；ExecSqlQueryMixin 统一 DuckDB 连接；ArrowStreamTask 支持分批与断点恢复；HashPartitionTask 三兄弟看"同一算子多实现"的演进）→ Scheduler/WorkQueue/Executor 分布式骨架与投机执行、RemoteExecutor 状态机 → Driver 与三种部署形态（standalone/Ray JobManager/平台适配），worker.py 的 NUMA 绑定值得细看。
**IO 与验证段（步 10–12）**：arrow.py/filesystem.py 的 parquet+3FS IO 路径（按 row group/文件大小切分、多线程写盘、原子 pickle 跨进程传状态）→ 跑读 GraySort 基准编排（urls_sort 的 v1/v2 对照是理解 API 演进的最佳材料）→ 最后读 TestFabric 测试哲学：不 mock 分布式，fork 真实 scheduler/executor 子进程真跑，test_execution 覆盖 OOM/崩溃/内存限制等容错路径，test_scheduler 专测投机执行与失败容错。

新人建议：一周跑通 Quick Start，两周吃透计划段与执行段，第三周对照 GraySort 基准验证全链路理解。扩展阅读：官方文档 Getting Started 与 API Reference（docs/source/）；姊妹项目 3FS 仓库的 GraySort 章节可反过来看存储侧如何支撑这套吞吐；读代码时配合 SessionBase 的 graph/timeline dump，把 DAG 与执行时间线可视化出来对照，事半功倍。
