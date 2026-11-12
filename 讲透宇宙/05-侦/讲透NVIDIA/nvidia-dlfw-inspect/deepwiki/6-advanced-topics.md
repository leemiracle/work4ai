<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/nvidia-dlfw-inspect · page 6 Advanced Topics · fetched 2026-10-26 -->

# Advanced Topics

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/getting_started.md](docs/getting_started.md)
- [docs/logging.md](docs/logging.md)
- [nvdlfw_inspect/utils.py](nvdlfw_inspect/utils.py)

</details>



This section covers advanced usage scenarios for `nvdlfw_inspect` that are essential for production deployments and complex training pipelines. The advanced features are organized into four main areas:

- **Logging and Statistics** (Section 6.1): Output directories, custom loggers, TensorBoard integration, and statistics aggregation
- **Distributed Training Support** (Section 6.2): Multi-GPU tensor reduction, per-rank logging, and pipeline parallelism handling
- **Caching and Performance** (Section 6.3): API caching mechanisms, performance optimization, and best practices for minimal overhead
- **Framework Integration** (Section 6.4): Integration with Transformer Engine, Megatron-LM, NeMo, and other frameworks

This overview demonstrates how these advanced components interact with the core architecture and provides context for the detailed subsections.

For basic usage, see [Getting Started](#2). For API details, see [API Reference](#3). For configuration basics, see [Configuration System](#4).

## Advanced System Integration Overview

The advanced features of `nvdlfw_inspect` work together to provide comprehensive debugging capabilities in production training environments. The following diagram shows how the four main subsystems interact during a typical training workflow.

### Advanced Features Integration Architecture

```mermaid
graph TB
    subgraph UserCode["User Training Code"]
        Init["debug_api.initialize()"]
        LogStats["debug_api.log_tensor_stats()"]
        Step["debug_api.step()"]
    end
    
    subgraph CoreSystem["Core System"]
        DebugMgr["DebugManager"]
        BaseNS["BaseNamespaceAPI"]
        ConfigMgr["ConfigManager"]
    end
    
    subgraph Logging["Logging System (6.1)"]
        FileLog["nvdlfw_inspect_logs/"]
        StatsLog["debug_statistic_logs/"]
        TBWriter["TensorBoard Writer"]
        BaseLogger["BaseLogger"]
    end
    
    subgraph Distributed["Distributed Support (6.2)"]
        GatherFirst["gather_along_first_dim()"]
        GatherLast["gather_tensor_on_last_rank()"]
        ReductionGroup["set_tensor_reduction_group()"]
        SkipReduce["skip_reduction parameter"]
    end
    
    subgraph Caching["Caching System (6.3)"]
        APICacheId["APICacheIdentifier"]
        SingleMsg["SingleMessageLogger"]
        CacheStore["API cache dictionary"]
    end
    
    subgraph Frameworks["Framework Integration (6.4)"]
        TENamespace["transformer_engine namespace"]
        SampleNS["sample_namespace"]
        ImportExec["import_and_exec_module()"]
    end
    
    Init --> DebugMgr
    Init --> ImportExec
    LogStats --> APICacheId
    LogStats --> BaseNS
    Step --> DebugMgr
    
    DebugMgr --> ConfigMgr
    BaseNS --> Logging
    BaseNS --> Distributed
    
    APICacheId --> CacheStore
    SingleMsg --> FileLog
    
    GatherFirst --> LogStats
    GatherLast --> LogStats
    ReductionGroup --> DebugMgr
    SkipReduce --> LogStats
    
    BaseNS --> TENamespace
    BaseNS --> SampleNS
    ImportExec --> Frameworks
    
    Distributed --> StatsLog
    Logging --> TBWriter
    Logging --> BaseLogger
```

Sources: [nvdlfw_inspect/api.py:1-500](), [nvdlfw_inspect/debug_manager.py:1-300](), [nvdlfw_inspect/utils.py:1-192]()

### Key Components and Their Interactions

The advanced subsystems are built on several key utility classes and functions that provide cross-cutting functionality:

| Component | Location | Primary Function | Related Subsection |
|-----------|----------|------------------|-------------------|
| `APICacheIdentifier` | [nvdlfw_inspect/utils.py:125-150]() | Cache API calls by source location | 6.3 Caching |
| `SingleMessageLogger` | [nvdlfw_inspect/utils.py:152-179]() | Deduplicate log messages | 6.1 Logging |
| `gather_along_first_dim()` | [nvdlfw_inspect/utils.py:41-68]() | All-gather tensors across ranks | 6.2 Distributed |
| `gather_tensor_on_last_rank()` | [nvdlfw_inspect/utils.py:71-98]() | Gather tensors to last rank only | 6.2 Distributed |
| `get_distributed_world_size()` | [nvdlfw_inspect/utils.py:28-32]() | Query distributed configuration | 6.2 Distributed |
| `get_distributed_rank()` | [nvdlfw_inspect/utils.py:35-38]() | Query current rank | 6.2 Distributed |
| `import_and_exec_module()` | [nvdlfw_inspect/utils.py:100-123]() | Dynamic feature loading | 6.4 Framework Integration |

Sources: [nvdlfw_inspect/utils.py:1-192]()

## Call Flow for Advanced Features

Understanding how API calls flow through the advanced subsystems is essential for effective usage. The following diagram traces a typical `log_tensor_stats()` call through caching, distributed reduction, and logging.

### API Call Flow Through Advanced Subsystems

```mermaid
sequenceDiagram
    participant User as "Training Code"
    participant API as "debug_api.log_tensor_stats()"
    participant Cache as "APICacheIdentifier"
    participant BaseNS as "BaseNamespaceAPI.route_api()"
    participant Feature as "LogTensorStats"
    participant Dist as "Distributed Utils"
    participant Logger as "Logging System"
    
    User->>API: log_tensor_stats(layer, tensor, ...)
    API->>Cache: save_call_details()
    Cache->>Cache: Store caller frame info
    API->>Cache: get_unique_identifier()
    Cache-->>API: Cache ID
    
    alt Cache Hit
        API-->>User: Return cached result
    else Cache Miss
        API->>BaseNS: route_api()
        BaseNS->>Feature: Execute LogTensorStats
        
        alt skip_reduction=False
            Feature->>Dist: Check reduction_group
            alt reduction_group set
                Dist->>Dist: gather_along_first_dim()
            else Default behavior
                Dist->>Dist: gather_tensor_on_last_rank()
            end
            Dist-->>Feature: Gathered tensor
        end
        
        Feature->>Feature: Calculate statistics
        Feature->>Logger: Log statistics
        
        alt TensorBoard enabled
            Logger->>Logger: Write to TensorBoard
        end
        
        alt File logging enabled
            Logger->>Logger: Write to debug_statistic_logs/
        end
        
        Feature-->>BaseNS: Result
        BaseNS-->>API: Result
        API-->>User: Return result
    end
```

Sources: [nvdlfw_inspect/api.py:1-500](), [nvdlfw_inspect/utils.py:125-150](), [nvdlfw_inspect/utils.py:41-98](), [docs/getting_started.md:39-66]()

### Initialization Parameters for Advanced Features

The `debug_api.initialize()` function accepts several parameters that control advanced behavior. These parameters determine how the subsystems operate throughout the training session.

| Parameter | Type | Default | Controls | Subsection |
|-----------|------|---------|----------|------------|
| `log_dir` | str | "." | Output directory for logs and statistics | 6.1 |
| `statistics_logger` | BaseLogger | None | Custom statistics logger implementation | 6.1 |
| `tb_writer` | TensorBoard Writer | None | TensorBoard integration | 6.1 |
| `default_logging_enabled` | bool | True | Enable default file logging | 6.1 |
| `init_training_step` | int | 0 | Initial step counter value | 6.1 |
| `feature_dirs` | List[str] | [] | Custom feature directories to load | 6.4 |

Sources: [docs/getting_started.md:128-149](), [docs/logging.md:1-99]()

## Tensor Reduction in Distributed Training

The distributed training support provides three primary reduction strategies, each optimized for different use cases. The choice of strategy significantly impacts both performance and the semantics of the logged statistics.

### Reduction Strategy Decision Tree

```mermaid
graph TB
    Start["log_tensor_stats() called"]
    
    CheckSkip{"skip_reduction<br/>parameter?"}
    CheckGroup{"reduction_group<br/>provided?"}
    CheckInit{"torch.distributed<br/>initialized?"}
    
    NoReduce["No reduction<br/>Per-rank statistics"]
    AllGather["gather_along_first_dim()<br/>All ranks have same stats"]
    LastRank["gather_tensor_on_last_rank()<br/>Only last rank logs"]
    NoOp["Single GPU<br/>No reduction needed"]
    
    LogPerRank["Write to rank-specific log"]
    LogUnified["Write to all rank logs"]
    LogLast["Write to last rank log only"]
    
    Start --> CheckSkip
    CheckSkip -->|True| NoReduce
    CheckSkip -->|False| CheckGroup
    
    CheckGroup -->|Yes| CheckInit
    CheckGroup -->|No| CheckInit
    
    CheckInit -->|No| NoOp
    CheckInit -->|Yes, with group| AllGather
    CheckInit -->|Yes, no group| LastRank
    
    NoReduce --> LogPerRank
    AllGather --> LogUnified
    LastRank --> LogLast
    NoOp --> LogPerRank
```

Sources: [docs/getting_started.md:248-257](), [nvdlfw_inspect/utils.py:41-98](), [docs/logging.md:48-89]()

### Distributed Training Configuration Examples

The following table shows common distributed training scenarios and their recommended configurations:

| Scenario | Configuration | Behavior | Performance |
|----------|---------------|----------|-------------|
| **Data Parallel Only** | `skip_reduction=False` (default) | Last rank gathers and logs | Low overhead |
| **Tensor Parallel** | `set_tensor_reduction_group(tp_group)` | All ranks compute same stats | Medium overhead |
| **Pipeline Parallel** | `skip_reduction=True` | Each pipeline stage logs separately | Minimal overhead |
| **3D Parallelism** | `set_tensor_reduction_group(tp_dp_group)` + last PP rank | Reduce across TP/DP, log on last PP | Optimized |
| **Debug Per-Rank** | `skip_reduction=True` | Individual rank statistics | Minimal overhead |

Sources: [docs/logging.md:48-89](), [docs/getting_started.md:248-257]()

## Performance Considerations

### Memory Efficiency

The tool implements several optimizations to minimize memory overhead:

- **Lazy tensor copying**: Tensors are only copied when reduction is required
- **Asynchronous operations**: Distributed operations support `async_op=True` parameter
- **Selective statistics**: Only enabled features compute statistics

### Computational Overhead

Key performance optimizations include:

| Optimization | Implementation | Impact |
|--------------|----------------|---------|
| API Caching | `APICacheIdentifier` | Prevents redundant feature execution |
| Message Deduplication | `SingleMessageLogger` | Reduces logging overhead |
| Conditional Reduction | `skip_reduction` parameter | Avoids unnecessary communication |

### Configuration Best Practices

For production environments, consider these configuration patterns:

```yaml
# Performance-optimized configuration
LogTensorStats:
  layer_name_regex_pattern: ".*attention.*"  # Target specific layers
  extensions:
    log_frequency: 100  # Log every 100 steps
    
transformer_engine:
  LogFp8TensorStats:
    layer_name_regex_pattern: ".*linear.*"
    extensions:
      skip_reduction: true  # For per-rank analysis
```

Sources: [nvdlfw_inspect/utils.py:125-176](), performance considerations from architectural analysis

---

