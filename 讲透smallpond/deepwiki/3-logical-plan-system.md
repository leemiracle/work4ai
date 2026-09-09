> 来源: [https://deepwiki.com/deepseek-ai/smallpond/3-logical-plan-system](https://deepwiki.com/deepseek-ai/smallpond/3-logical-plan-system)
> DeepWiki deepseek-ai/smallpond

# Logical Plan System

  Relevant source files 
 - [benchmarks/hash_partition_benchmark.py](https://github.com/deepseek-ai/smallpond/blob/52ecc5e4/benchmarks/hash_partition_benchmark.py)
 - [examples/shuffle_data.py](https://github.com/deepseek-ai/smallpond/blob/52ecc5e4/examples/shuffle_data.py)
 - [examples/sort_mock_urls.py](https://github.com/deepseek-ai/smallpond/blob/52ecc5e4/examples/sort_mock_urls.py)
 
  The Logical Plan System forms the core execution framework of the smallpond data processing platform. It provides a mechanism for constructing and executing directed acyclic graphs (DAGs) of data processing operations. This document explains the architecture, components, and usage of the Logical Plan System in smallpond.

 For information about the high-level Session API that builds on top of this system, see [Core API](https://deepwiki.com/deepseek-ai/smallpond/2-core-api) and [Session API](https://deepwiki.com/deepseek-ai/smallpond/2.1-session-api).

 
## System Purpose and Architecture

 The Logical Plan System enables the definition of complex data processing workflows through a composable node-based architecture. It serves as the foundation for all data operations in smallpond, providing a flexible and extensible framework for tasks such as data loading, transformation, partitioning, and output.

 
```

```

 The system consists of four primary components:

 
 - **LogicalPlan**: The top-level container that holds a directed acyclic graph of processing nodes with a single root node representing the final output.
 - **Context**: Maintains the registry of all nodes in a plan, enabling node lookup and management.
 - **Node**: The abstract base class for all operation types, with subclasses for specific operations like data loading, SQL execution, partitioning, etc.
 - **Driver**: Handles command-line argument parsing and plan execution, providing the entry point for running logical plans.
 
 Sources: [benchmarks/hash_partition_benchmark.py10-11](https://github.com/deepseek-ai/smallpond/blob/52ecc5e4/benchmarks/hash_partition_benchmark.py#L10-L11) [benchmarks/hash_partition_benchmark.py61-63](https://github.com/deepseek-ai/smallpond/blob/52ecc5e4/benchmarks/hash_partition_benchmark.py#L61-L63) [examples/shuffle_data.py8-10](https://github.com/deepseek-ai/smallpond/blob/52ecc5e4/examples/shuffle_data.py#L8-L10)

 
## Node Types and Hierarchy

 The Logical Plan System includes a variety of specialized node types, each providing specific data processing functionality. These nodes can be composed to create complex data processing pipelines.

 
```

```

 
### Key Node Types:

 
 - **DataSourceNode**: Loads data from sources like Parquet or CSV files into the processing pipeline
 - **DataSetPartitionNode**: Divides datasets into multiple partitions for parallel processing
 - **HashPartitionNode**: Partitions data based on hash values of specified columns
 - **SqlEngineNode**: Executes SQL queries on input data using DuckDB
 - **ArrowComputeNode**: Performs custom operations on Apache Arrow tables
 - **ConsolidateNode**: Combines multiple data partitions into a single dataset
 - **DataSinkNode**: Writes processed data to storage
 - **StreamCopy**: Copies data streams between nodes
 - **PythonScriptNode**: Executes custom Python code on data
 - **ProjectionNode**: Selects specific columns from datasets
 - **ShuffleNode**: Randomizes data ordering
 
 Sources: [examples/sort_mock_urls.py10-19](https://github.com/deepseek-ai/smallpond/blob/52ecc5e4/examples/sort_mock_urls.py#L10-L19) [examples/shuffle_data.py4-10](https://github.com/deepseek-ai/smallpond/blob/52ecc5e4/examples/shuffle_data.py#L4-L10) [benchmarks/hash_partition_benchmark.py5-12](https://github.com/deepseek-ai/smallpond/blob/52ecc5e4/benchmarks/hash_partition_benchmark.py#L5-L12)

 
## Building and Executing Logical Plans

 Creating and executing a logical plan involves three main steps:

 
 - Creating a Context
 - Building a node graph with a root node
 - Constructing a LogicalPlan and executing it via a Driver
 
 
```

```

 
### Example Plan Construction

 Here's how a typical logical plan is built:

 
```

```

 Sources: [benchmarks/hash_partition_benchmark.py27-64](https://github.com/deepseek-ai/smallpond/blob/52ecc5e4/benchmarks/hash_partition_benchmark.py#L27-L64) [examples/shuffle_data.py22-58](https://github.com/deepseek-ai/smallpond/blob/52ecc5e4/examples/shuffle_data.py#L22-L58) [examples/sort_mock_urls.py28-86](https://github.com/deepseek-ai/smallpond/blob/52ecc5e4/examples/sort_mock_urls.py#L28-L86)

 
## Driver and Execution

 The Driver component manages the execution of logical plans and provides utilities for handling command-line arguments. It serves as the entry point for running logical plans from command-line applications.

 
```

```

 
### Driver Features:

 
 - **Argument Management**:

 
 - Define command-line arguments with `add_argument()`
 - Parse arguments with `parse_arguments()`
 - Retrieve parsed arguments with `get_arguments()`
 - **Plan Execution**:

 
 - Execute the plan with `run(plan)`
 - Handle execution context and resource management
 - Process the node graph in the correct dependency order
 - **Resource Control**:

 
 - Specify CPU and memory limits for operations
 - Configure execution environment parameters
 
 Sources: [benchmarks/hash_partition_benchmark.py69-87](https://github.com/deepseek-ai/smallpond/blob/52ecc5e4/benchmarks/hash_partition_benchmark.py#L69-L87) [examples/shuffle_data.py61-70](https://github.com/deepseek-ai/smallpond/blob/52ecc5e4/examples/shuffle_data.py#L61-L70) [examples/sort_mock_urls.py89-96](https://github.com/deepseek-ai/smallpond/blob/52ecc5e4/examples/sort_mock_urls.py#L89-L96)

 
## Common Usage Patterns

 The Logical Plan System supports several common data processing patterns that appear frequently in smallpond applications.

 
### Data Partitioning and Distribution

 
```

```

 This pattern divides data into partitions for parallel processing, improving performance for large datasets.

 
### ETL Pipeline

 
```

```

 This pattern represents a standard Extract-Transform-Load pipeline for data processing.

 
### Sort and Aggregate

 
```

```

 This pattern enables efficient sorting and aggregation of large datasets.

 Sources: [examples/sort_mock_urls.py28-86](https://github.com/deepseek-ai/smallpond/blob/52ecc5e4/examples/sort_mock_urls.py#L28-L86) [benchmarks/hash_partition_benchmark.py15-65](https://github.com/deepseek-ai/smallpond/blob/52ecc5e4/benchmarks/hash_partition_benchmark.py#L15-L65) [examples/shuffle_data.py14-58](https://github.com/deepseek-ai/smallpond/blob/52ecc5e4/examples/shuffle_data.py#L14-L58)

 
## Resource Management

 Nodes in the Logical Plan System can be configured with resource constraints to control their execution:

 
| Parameter | Description | Example |
|---|---|---|
| cpu_limit | Maximum CPU cores to use | cpu_limit=16 |
| memory_limit | Maximum memory allocation | memory_limit=10 * GB |
| output_name | Name for tracking output | output_name="sorted_data" |
| output_path | Path for persisting output | output_path="/tmp/results" |

 These parameters can be specified when creating nodes, allowing fine-grained control over resource utilization throughout the plan.

 Sources: [benchmarks/hash_partition_benchmark.py42-43](https://github.com/deepseek-ai/smallpond/blob/52ecc5e4/benchmarks/hash_partition_benchmark.py#L42-L43) [examples/sort_mock_urls.py66](https://github.com/deepseek-ai/smallpond/blob/52ecc5e4/examples/sort_mock_urls.py#L66-L66) [benchmarks/hash_partition_benchmark.py54](https://github.com/deepseek-ai/smallpond/blob/52ecc5e4/benchmarks/hash_partition_benchmark.py#L54-L54)

 
## Integration with Execution Engines

 The Logical Plan System can use different execution engines for data processing:

 
```

```

 The system primarily supports two execution engines:

 
 - **DuckDB**: Used for SQL-based operations and general data processing
 - **Arrow**: Used for specialized compute operations or when custom processing logic is needed
 
 The engine can be specified through the `engine_type` parameter in nodes like `HashPartitionNode`, allowing selection between "duckdb" and "arrow" based on processing requirements.

 Sources: [examples/sort_mock_urls.py61-74](https://github.com/deepseek-ai/smallpond/blob/52ecc5e4/examples/sort_mock_urls.py#L61-L74) [benchmarks/hash_partition_benchmark.py19](https://github.com/deepseek-ai/smallpond/blob/52ecc5e4/benchmarks/hash_partition_benchmark.py#L19-L19) [examples/shuffle_data.py67](https://github.com/deepseek-ai/smallpond/blob/52ecc5e4/examples/shuffle_data.py#L67-L67)

 
## Extending the System

 The Logical Plan System can be extended by creating custom node types that inherit from existing node classes:

 
 - **Custom Processing Nodes**: Extend `ArrowComputeNode` or other node types
 - **Custom Data Sources/Sinks**: Extend `DataSourceNode` or `DataSinkNode`
 - **Specialized Operations**: Create dedicated node classes for domain-specific operations
 
 Example of a custom node extension:

 
```

```

 Sources: [examples/sort_mock_urls.py22-25](https://github.com/deepseek-ai/smallpond/blob/52ecc5e4/examples/sort_mock_urls.py#L22-L25)

 
## Summary

 The Logical Plan System provides a flexible, extensible framework for defining and executing complex data processing workflows in smallpond. By composing different node types into directed acyclic graphs, users can create sophisticated data processing pipelines that efficiently handle large-scale data operations.

 The system's integration with the Driver component enables easy execution from command-line applications, while its support for different execution engines allows selection of the most appropriate processing technology for each operation.
