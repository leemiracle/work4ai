> 来源: [https://deepwiki.com/ray-project/ray/3-ray-data](https://deepwiki.com/ray-project/ray/3-ray-data)
> DeepWiki ray-project/ray | Last indexed: 25 June 2026 (bf1295

# Ray Data

  Relevant source files 
 - [.claude/CLAUDE.md](https://github.com/ray-project/ray/blob/bf129559/.claude/CLAUDE.md?plain=1)
 - [.claude/rules/python-guidelines.md](https://github.com/ray-project/ray/blob/bf129559/.claude/rules/python-guidelines.md?plain=1)
 - [.claude/skills/lint/SKILL.md](https://github.com/ray-project/ray/blob/bf129559/.claude/skills/lint/SKILL.md?plain=1)
 - [.claude/skills/rebuild/SKILL.md](https://github.com/ray-project/ray/blob/bf129559/.claude/skills/rebuild/SKILL.md?plain=1)
 - [.vale/styles/config/vocabularies/Data/accept.txt](https://github.com/ray-project/ray/blob/bf129559/.vale/styles/config/vocabularies/Data/accept.txt)
 - [doc/BUILD.bazel](https://github.com/ray-project/ray/blob/bf129559/doc/BUILD.bazel)
 - [doc/source/_templates/autosummary/class_without_autosummary_noindex.rst](https://github.com/ray-project/ray/blob/bf129559/doc/source/_templates/autosummary/class_without_autosummary_noindex.rst)
 - [doc/source/data/aggregating-data.rst](https://github.com/ray-project/ray/blob/bf129559/doc/source/data/aggregating-data.rst)
 - [doc/source/data/api/dataset.rst](https://github.com/ray-project/ray/blob/bf129559/doc/source/data/api/dataset.rst)
 - [doc/source/data/api/expressions.rst](https://github.com/ray-project/ray/blob/bf129559/doc/source/data/api/expressions.rst)
 - [doc/source/data/api/from_other_data_libs.rst](https://github.com/ray-project/ray/blob/bf129559/doc/source/data/api/from_other_data_libs.rst)
 - [doc/source/data/comparisons.rst](https://github.com/ray-project/ray/blob/bf129559/doc/source/data/comparisons.rst)
 - [doc/source/data/concurrent-dataset-execution.md](https://github.com/ray-project/ray/blob/bf129559/doc/source/data/concurrent-dataset-execution.md?plain=1)
 - [doc/source/data/data-internals.rst](https://github.com/ray-project/ray/blob/bf129559/doc/source/data/data-internals.rst)
 - [doc/source/data/data-memory-model-1.svg](https://github.com/ray-project/ray/blob/bf129559/doc/source/data/data-memory-model-1.svg)
 - [doc/source/data/data-memory-model-2.svg](https://github.com/ray-project/ray/blob/bf129559/doc/source/data/data-memory-model-2.svg)
 - [doc/source/data/data-memory-model-3.svg](https://github.com/ray-project/ray/blob/bf129559/doc/source/data/data-memory-model-3.svg)
 - [doc/source/data/how-to-avoid-ooms.md](https://github.com/ray-project/ray/blob/bf129559/doc/source/data/how-to-avoid-ooms.md?plain=1)
 - [doc/source/data/joining-data.rst](https://github.com/ray-project/ray/blob/bf129559/doc/source/data/joining-data.rst)
 - [doc/source/data/key-concepts.rst](https://github.com/ray-project/ray/blob/bf129559/doc/source/data/key-concepts.rst)
 - [doc/source/data/node-count.png](https://github.com/ray-project/ray/blob/bf129559/doc/source/data/node-count.png)
 - [doc/source/data/performance-tips.rst](https://github.com/ray-project/ray/blob/bf129559/doc/source/data/performance-tips.rst)
 - [doc/source/data/ray-oom-kills-chart.png](https://github.com/ray-project/ray/blob/bf129559/doc/source/data/ray-oom-kills-chart.png)
 - [doc/source/data/shuffling-data.rst](https://github.com/ray-project/ray/blob/bf129559/doc/source/data/shuffling-data.rst)
 - [doc/source/data/transforming-data.rst](https://github.com/ray-project/ray/blob/bf129559/doc/source/data/transforming-data.rst)
 - [doc/source/data/unexpected-system-level-chart.png](https://github.com/ray-project/ray/blob/bf129559/doc/source/data/unexpected-system-level-chart.png)
 - [doc/source/data/user-guide.rst](https://github.com/ray-project/ray/blob/bf129559/doc/source/data/user-guide.rst)
 - [doc/source/train/doc_code/asynchronous_validation.py](https://github.com/ray-project/ray/blob/bf129559/doc/source/train/doc_code/asynchronous_validation.py)
 - [doc/source/train/images/checkpoint_metrics_lifecycle.png](https://github.com/ray-project/ray/blob/bf129559/doc/source/train/images/checkpoint_metrics_lifecycle.png)
 - [doc/source/train/user-guides/asynchronous-validation.rst](https://github.com/ray-project/ray/blob/bf129559/doc/source/train/user-guides/asynchronous-validation.rst)
 - [doc/source/train/user-guides/monitoring-logging.rst](https://github.com/ray-project/ray/blob/bf129559/doc/source/train/user-guides/monitoring-logging.rst)
 - [python/ray/dashboard/modules/metrics/dashboards/data_dashboard_panels.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/dashboard/modules/metrics/dashboards/data_dashboard_panels.py)
 - [python/ray/data/_internal/execution/dataset_state.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/data/_internal/execution/dataset_state.py)
 - [python/ray/data/_internal/execution/interfaces/execution_options.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/data/_internal/execution/interfaces/execution_options.py)
 - [python/ray/data/_internal/execution/interfaces/op_runtime_metrics.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/data/_internal/execution/interfaces/op_runtime_metrics.py)
 - [python/ray/data/_internal/execution/interfaces/physical_operator.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/data/_internal/execution/interfaces/physical_operator.py)
 - [python/ray/data/_internal/execution/operators/actor_pool_map_operator.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/data/_internal/execution/operators/actor_pool_map_operator.py)
 - [python/ray/data/_internal/execution/operators/aggregate_num_rows.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/data/_internal/execution/operators/aggregate_num_rows.py)
 - [python/ray/data/_internal/execution/operators/base_physical_operator.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/data/_internal/execution/operators/base_physical_operator.py)
 - [python/ray/data/_internal/execution/operators/input_data_buffer.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/data/_internal/execution/operators/input_data_buffer.py)
 - [python/ray/data/_internal/execution/operators/limit_operator.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/data/_internal/execution/operators/limit_operator.py)
 - [python/ray/data/_internal/execution/operators/map_operator.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/data/_internal/execution/operators/map_operator.py)
 - [python/ray/data/_internal/execution/operators/output_splitter.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/data/_internal/execution/operators/output_splitter.py)
 - [python/ray/data/_internal/execution/operators/task_pool_map_operator.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/data/_internal/execution/operators/task_pool_map_operator.py)
 - [python/ray/data/_internal/execution/operators/union_operator.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/data/_internal/execution/operators/union_operator.py)
 - [python/ray/data/_internal/execution/operators/zip_operator.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/data/_internal/execution/operators/zip_operator.py)
 - [python/ray/data/_internal/execution/resource_manager.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/data/_internal/execution/resource_manager.py)
 - [python/ray/data/_internal/execution/streaming_executor.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/data/_internal/execution/streaming_executor.py)
 - [python/ray/data/_internal/execution/streaming_executor_state.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/data/_internal/execution/streaming_executor_state.py)
 - [python/ray/data/_internal/logical/interfaces/logical_operator.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/data/_internal/logical/interfaces/logical_operator.py)
 - [python/ray/data/_internal/logical/operators/all_to_all_operator.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/data/_internal/logical/operators/all_to_all_operator.py)
 - [python/ray/data/_internal/logical/operators/count_operator.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/data/_internal/logical/operators/count_operator.py)
 - [python/ray/data/_internal/logical/operators/from_operators.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/data/_internal/logical/operators/from_operators.py)
 - [python/ray/data/_internal/logical/operators/input_data_operator.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/data/_internal/logical/operators/input_data_operator.py)
 - [python/ray/data/_internal/logical/operators/join_operator.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/data/_internal/logical/operators/join_operator.py)
 - [python/ray/data/_internal/logical/operators/map_operator.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/data/_internal/logical/operators/map_operator.py)
 - [python/ray/data/_internal/logical/operators/n_ary_operator.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/data/_internal/logical/operators/n_ary_operator.py)
 - [python/ray/data/_internal/logical/operators/one_to_one_operator.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/data/_internal/logical/operators/one_to_one_operator.py)
 - [python/ray/data/_internal/logical/operators/read_operator.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/data/_internal/logical/operators/read_operator.py)
 - [python/ray/data/_internal/logical/operators/streaming_split_operator.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/data/_internal/logical/operators/streaming_split_operator.py)
 - [python/ray/data/_internal/logical/operators/write_operator.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/data/_internal/logical/operators/write_operator.py)
 - [python/ray/data/_internal/logical/rules/limit_pushdown.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/data/_internal/logical/rules/limit_pushdown.py)
 - [python/ray/data/_internal/logical/rules/predicate_pushdown.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/data/_internal/logical/rules/predicate_pushdown.py)
 - [python/ray/data/_internal/metadata_exporter.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/data/_internal/metadata_exporter.py)
 - [python/ray/data/_internal/planner/plan_expression/expression_evaluator.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/data/_internal/planner/plan_expression/expression_evaluator.py)
 - [python/ray/data/_internal/planner/plan_expression/expression_visitors.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/data/_internal/planner/plan_expression/expression_visitors.py)
 - [python/ray/data/_internal/planner/plan_udf_map_op.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/data/_internal/planner/plan_udf_map_op.py)
 - [python/ray/data/_internal/stats.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/data/_internal/stats.py)
 - [python/ray/data/context.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/data/context.py)
 - [python/ray/data/dataset.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/data/dataset.py)
 - [python/ray/data/expressions.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/data/expressions.py)
 - [python/ray/data/grouped_data.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/data/grouped_data.py)
 - [python/ray/data/tests/test_actor_pool_map_operator.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/data/tests/test_actor_pool_map_operator.py)
 - [python/ray/data/tests/test_backpressure_e2e.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/data/tests/test_backpressure_e2e.py)
 - [python/ray/data/tests/test_execution_optimizer_limit_pushdown.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/data/tests/test_execution_optimizer_limit_pushdown.py)
 - [python/ray/data/tests/test_executor_resource_management.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/data/tests/test_executor_resource_management.py)
 - [python/ray/data/tests/test_map.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/data/tests/test_map.py)
 - [python/ray/data/tests/test_op_runtime_metrics.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/data/tests/test_op_runtime_metrics.py)
 - [python/ray/data/tests/test_operators.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/data/tests/test_operators.py)
 - [python/ray/data/tests/test_predicate_pushdown.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/data/tests/test_predicate_pushdown.py)
 - [python/ray/data/tests/test_reservation_based_resource_allocator.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/data/tests/test_reservation_based_resource_allocator.py)
 - [python/ray/data/tests/test_resource_manager.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/data/tests/test_resource_manager.py)
 - [python/ray/data/tests/test_state_export.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/data/tests/test_state_export.py)
 - [python/ray/data/tests/test_stats.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/data/tests/test_stats.py)
 - [python/ray/data/tests/test_streaming_executor.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/data/tests/test_streaming_executor.py)
 - [python/ray/data/tests/unit/test_expression_evaluator.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/data/tests/unit/test_expression_evaluator.py)
 - [python/ray/data/tests/unit/test_logical_plan.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/data/tests/unit/test_logical_plan.py)
 - [python/ray/data/util/expression_utils.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/data/util/expression_utils.py)
 - [src/ray/protobuf/export_dataset_metadata.proto](https://github.com/ray-project/ray/blob/bf129559/src/ray/protobuf/export_dataset_metadata.proto)
 
  
## Purpose and Scope

 Ray Data is Ray's distributed data processing library that provides scalable data loading, transformation, and output capabilities. The core abstraction is the `Dataset` class [python/ray/data/dataset.py201-203](https://github.com/ray-project/ray/blob/bf129559/python/ray/data/dataset.py#L201-L203) which represents a distributed data collection produced by a pipeline of blocks. Ray Data enables memory-efficient processing through streaming execution and backpressure control, allowing datasets larger than cluster memory to be processed.

 This page covers:

 
 - The `Dataset` API and its transformation operations
 - Logical and physical operator planning
 - The `StreamingExecutor` and its scheduling loop
 - Resource management and backpressure policies
 - Data formats and I/O integration
 
 For operator-level details, see [Dataset API and Transformations](https://deepwiki.com/ray-project/ray/3.1-dataset-api-and-transformations). For datasource implementations, see [Data Sources and Sinks](https://deepwiki.com/ray-project/ray/3.2-data-sources-and-sinks). For execution engine internals, see [Streaming Execution and Resource Management](https://deepwiki.com/ray-project/ray/3.3-streaming-execution-and-resource-management). For LLM-specific features, see [Ray Data for LLMs](https://deepwiki.com/ray-project/ray/3.4-ray-data-for-llms).

 Ray Data builds on Ray Core's distributed execution primitives ([Ray Core Infrastructure](https://deepwiki.com/ray-project/ray/2-ray-core-infrastructure)) and integrates with Ray Serve ([Ray Serve](https://deepwiki.com/ray-project/ray/4-ray-serve)), Ray Train, and Ray Tune.

 
## Architecture Overview

 Ray Data Architecture: Logical Planning to Streaming Execution

 
```

```

 The architecture follows a multi-stage pipeline:

 
 - **Logical Planning**: User API calls build a `LogicalPlan` [python/ray/data/_internal/logical/interfaces/logical_operator.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/data/_internal/logical/interfaces/logical_operator.py) consisting of high-level operators.
 - **Physical Planning**: The `LogicalPlan` is converted to physical operators via `build_streaming_topology()` [python/ray/data/_internal/execution/streaming_executor_state.py36](https://github.com/ray-project/ray/blob/bf129559/python/ray/data/_internal/execution/streaming_executor_state.py#L36-L36)
 - **Streaming Execution**: `StreamingExecutor.execute()` [python/ray/data/_internal/execution/streaming_executor.py164-169](https://github.com/ray-project/ray/blob/bf129559/python/ray/data/_internal/execution/streaming_executor.py#L164-L169) sets up the topology and starts a background thread [python/ray/data/_internal/execution/streaming_executor.py160](https://github.com/ray-project/ray/blob/bf129559/python/ray/data/_internal/execution/streaming_executor.py#L160-L160) to drive the event-based scheduling loop.
 
 Sources: [python/ray/data/dataset.py201-4000](https://github.com/ray-project/ray/blob/bf129559/python/ray/data/dataset.py#L201-L4000) [python/ray/data/_internal/execution/streaming_executor.py100-200](https://github.com/ray-project/ray/blob/bf129559/python/ray/data/_internal/execution/streaming_executor.py#L100-L200) [python/ray/data/_internal/execution/streaming_executor_state.py156-200](https://github.com/ray-project/ray/blob/bf129559/python/ray/data/_internal/execution/streaming_executor_state.py#L156-L200) [python/ray/data/_internal/logical/interfaces/logical_operator.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/data/_internal/logical/interfaces/logical_operator.py)

 
## Core Components

 
### Dataset Class

 The `Dataset` class [python/ray/data/dataset.py201-203](https://github.com/ray-project/ray/blob/bf129559/python/ray/data/dataset.py#L201-L203) is the primary user-facing API. It represents a distributed collection that produces `ObjectRef[Block]` outputs.

 **Key attributes:**

 
 - `_plan: ExecutionPlan` - The lazy execution plan [python/ray/data/_internal/execution/interfaces/physical_operator.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/data/_internal/execution/interfaces/physical_operator.py)
 - `_logical_plan: LogicalPlan` - The logical DAG [python/ray/data/_internal/logical/interfaces/logical_operator.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/data/_internal/logical/interfaces/logical_operator.py)
 
 **Transformation operations:**

 
| Method | Purpose | Implementation |
|---|---|---|
| map() | Apply function per row | python/ray/data/dataset.py338 |
| map_batches() | Apply function per batch | python/ray/data/dataset.py538 |
| filter() | Filter rows by predicate | python/ray/data/dataset.py1161 |
| groupby() | Group data for aggregation | python/ray/data/dataset.py2163 |
| sort() | Sort the dataset | python/ray/data/dataset.py2550 |

 **Execution methods:**

 
| Method | Purpose | Implementation |
|---|---|---|
| materialize() | Execute and cache all blocks | python/ray/data/dataset.py3461 |
| iter_batches() | Yield batches as iterator | python/ray/data/dataset.py1833 |
| take() | Execute and collect N results | python/ray/data/dataset.py3102 |
| write_parquet() | Write to Parquet files | python/ray/data/dataset.py3828 |

 Sources: [python/ray/data/dataset.py201-4000](https://github.com/ray-project/ray/blob/bf129559/python/ray/data/dataset.py#L201-L4000)

 
### Physical Operators

 Physical operators are the executable nodes in the execution DAG. They manage task dispatch and resource tracking.

 
| Operator | Role | Source |
|---|---|---|
| MapOperator | Base class for 1:1 transformations | python/ray/data/_internal/execution/operators/map_operator.py196 |
| TaskPoolMapOperator | Executes tasks on Ray's task pool | python/ray/data/_internal/execution/operators/task_pool_map_operator.py |
| ActorPoolMapOperator | Executes tasks on a pool of actors | python/ray/data/_internal/execution/operators/actor_pool_map_operator.py85 |
| InputDataBuffer | Buffers initial input data | python/ray/data/_internal/execution/operators/input_data_buffer.py |
| AllToAllOperator | Base for blocking/shuffling operations | python/ray/data/_internal/execution/operators/base_physical_operator.py |

 Sources: [python/ray/data/_internal/execution/interfaces/physical_operator.py1-100](https://github.com/ray-project/ray/blob/bf129559/python/ray/data/_internal/execution/interfaces/physical_operator.py#L1-L100) [python/ray/data/_internal/execution/operators/map_operator.py196-200](https://github.com/ray-project/ray/blob/bf129559/python/ray/data/_internal/execution/operators/map_operator.py#L196-L200) [python/ray/data/_internal/execution/operators/actor_pool_map_operator.py85-150](https://github.com/ray-project/ray/blob/bf129559/python/ray/data/_internal/execution/operators/actor_pool_map_operator.py#L85-L150)

 
### Streaming Executor

 The `StreamingExecutor` [python/ray/data/_internal/execution/streaming_executor.py100](https://github.com/ray-project/ray/blob/bf129559/python/ray/data/_internal/execution/streaming_executor.py#L100-L100) runs the DAG by routing blocks through operators to maximize throughput under resource constraints.

 **Key Executor State:**

 
| Component | Type | Purpose |
|---|---|---|
| _topology | Topology | Maps operators to OpState python/ray/data/_internal/execution/streaming_executor.py107 |
| _resource_manager | ResourceManager | Tracks resource usage python/ray/data/_internal/execution/streaming_executor.py116 |
| _backpressure_policies | List[BackpressurePolicy] | Enforces backpressure python/ray/data/_internal/execution/streaming_executor.py109 |

 **Scheduling Loop**: The executor runs a loop that calls `select_operator_to_run()` [python/ray/data/_internal/execution/streaming_executor_state.py39](https://github.com/ray-project/ray/blob/bf129559/python/ray/data/_internal/execution/streaming_executor_state.py#L39-L39) to decide which operator should process the next available input or start a new task.

 Sources: [python/ray/data/_internal/execution/streaming_executor.py100-200](https://github.com/ray-project/ray/blob/bf129559/python/ray/data/_internal/execution/streaming_executor.py#L100-L200) [python/ray/data/_internal/execution/streaming_executor_state.py156-200](https://github.com/ray-project/ray/blob/bf129559/python/ray/data/_internal/execution/streaming_executor_state.py#L156-L200)

 
## Data Structures

 
### RefBundle

 `RefBundle` [python/ray/data/_internal/execution/interfaces/ref_bundle.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/data/_internal/execution/interfaces/ref_bundle.py) is the unit of data transfer. It wraps a set of Ray `ObjectRef[Block]` and their metadata.

 
### Block

 A `Block` is the atomic unit of data. Ray Data uses `BlockAccessor` [python/ray/data/block.py120](https://github.com/ray-project/ray/blob/bf129559/python/ray/data/block.py#L120-L120) to provide a uniform interface over:

 
 - **Arrow Blocks**: Tabular data using PyArrow.
 - **Pandas Blocks**: Tabular data using Pandas.
 - **Tensor Blocks**: Multi-dimensional arrays using NumPy.
 
 Sources: [python/ray/data/block.py120-130](https://github.com/ray-project/ray/blob/bf129559/python/ray/data/block.py#L120-L130) [python/ray/data/_internal/execution/interfaces/ref_bundle.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/data/_internal/execution/interfaces/ref_bundle.py)

 
## Execution Context and Configuration

 `DataContext` [python/ray/data/context.py33](https://github.com/ray-project/ray/blob/bf129559/python/ray/data/context.py#L33-L33) provides global configuration.

 
| Setting | Default | Source |
|---|---|---|
| target_max_block_size | 128 MiB | python/ray/data/context.py48 |
| streaming_read_buffer_size | 32 MiB | python/ray/data/context.py66 |
| scheduling_strategy | "SPREAD" | python/ray/data/context.py112 |
| max_errored_blocks | 0 | python/ray/data/context.py212 |

 Sources: [python/ray/data/context.py33-250](https://github.com/ray-project/ray/blob/bf129559/python/ray/data/context.py#L33-L250)

 
## Statistics and Monitoring

 Ray Data collects detailed execution statistics via `DatasetStats` [python/ray/data/_internal/stats.py227](https://github.com/ray-project/ray/blob/bf129559/python/ray/data/_internal/stats.py#L227-L227)

 **Key Metrics:**

 
 - **Wall Time**: Total time spent in operators.
 - **Object Store Memory**: Peak and current usage [python/ray/data/_internal/execution/resource_manager.py157](https://github.com/ray-project/ray/blob/bf129559/python/ray/data/_internal/execution/resource_manager.py#L157-L157)
 - **Task Duration**: Distribution of task completion times [python/ray/data/_internal/execution/interfaces/op_runtime_metrics.py31](https://github.com/ray-project/ray/blob/bf129559/python/ray/data/_internal/execution/interfaces/op_runtime_metrics.py#L31-L31)
 
 Sources: [python/ray/data/_internal/stats.py1-250](https://github.com/ray-project/ray/blob/bf129559/python/ray/data/_internal/stats.py#L1-L250) [python/ray/data/tests/test_stats.py35-45](https://github.com/ray-project/ray/blob/bf129559/python/ray/data/tests/test_stats.py#L35-L45)
