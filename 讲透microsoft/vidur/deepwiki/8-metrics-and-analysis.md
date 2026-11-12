<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/vidur · page 8 Metrics and Analysis · fetched 2026-10-26 -->

# Metrics and Analysis

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [assets/batch_size.png](assets/batch_size.png)
- [assets/decode_time_execution_plus_preemption_normalized.png](assets/decode_time_execution_plus_preemption_normalized.png)
- [assets/prefill_e2e_time.png](assets/prefill_e2e_time.png)
- [assets/request_e2e_time.png](assets/request_e2e_time.png)
- [vidur/metrics/metrics_store.py](vidur/metrics/metrics_store.py)

</details>



This document covers Vidur's comprehensive metrics collection, storage, and analysis system. The metrics system provides detailed performance measurements across all simulation components, from individual request latencies to system-wide throughput and hardware utilization statistics. For specific performance indicators tracked by the simulator, see [Performance Metrics](#8.1). For visualization tools and monitoring integrations, see [Visualization and Monitoring](#8.2). For advanced statistical analysis capabilities, see [Advanced Analytics](#8.3).

## Metrics System Architecture

The metrics system in Vidur is built around a centralized `MetricsStore` that collects performance data from all simulation components and provides multiple output formats for analysis.

```mermaid
graph TD
    subgraph "Simulation Components"
        A["Simulator"] --> E["MetricsStore"]
        B["BaseGlobalScheduler"] --> E
        C["ReplicaScheduler"] --> E
        D["Batch Execution"] --> E
    end
    
    subgraph "MetricsStore Core"
        E --> F["DataSeries"]
        E --> G["CDFSketch"] 
        E --> H["SeriesAverageMeter"]
        E --> I["MFUCalculator"]
    end
    
    subgraph "Metric Categories"
        J["RequestMetricsTimeDistributions"] --> F
        K["TokenMetricsTimeDistribution"] --> G
        L["BatchMetricsTimeDistribution"] --> G
        M["OperationMetrics"] --> G
        N["CpuOperationMetrics"] --> G
    end
    
    subgraph "Output Systems"
        F --> O["CSV Files"]
        G --> P["CDF Plots"]
        H --> Q["Time Series Plots"]
        E --> R["WandB Integration"]
        E --> S["Chrome Traces"]
    end
```

**Sources:** [vidur/metrics/metrics_store.py:1-822]()

## MetricsStore Component

The `MetricsStore` class serves as the central hub for all metrics collection in Vidur. It initializes multiple data structures to track different types of performance metrics and provides event-driven interfaces for the simulation engine to record data points.

```mermaid
graph LR
    subgraph "MetricsStore Initialization"
        A["__init__"] --> B["_request_metrics_time_distributions"]
        A --> C["_token_metrics_time_distribution"]
        A --> D["_batch_metrics_count_distribution"] 
        A --> E["_operation_metrics"]
        A --> F["_replica_memory_usage"]
        A --> G["_replica_busy_time"]
        A --> H["_replica_mfu"]
    end
    
    subgraph "Event Handlers"
        I["on_request_arrival"] --> B
        J["on_batch_end"] --> C
        J --> D
        K["on_replica_schedule"] --> F
        L["on_replica_stage_schedule"] --> G
        L --> H
        L --> E
    end
    
    subgraph "Output Methods"
        M["plot"] --> N["_store_request_metrics"]
        M --> O["_store_batch_metrics"]
        M --> P["_store_operation_metrics"]
        M --> Q["_store_utilization_metrics"]
    end
```

**Sources:** [vidur/metrics/metrics_store.py:50-237]()

## Metric Collection Events

The metrics system uses an event-driven architecture where simulation components call specific methods on the `MetricsStore` when significant events occur.

### Request Lifecycle Events

```mermaid
sequenceDiagram
    participant S as Simulator
    participant MS as MetricsStore
    participant DS as DataSeries
    participant CS as CDFSketch
    
    S->>MS: on_request_arrival(time, request)
    MS->>DS: put(request_id, num_tokens)
    
    Note over S,CS: Request processing occurs
    
    S->>MS: on_batch_end(time, batch, replica_id, memory_usage)
    MS->>MS: _on_request_end(time, request)
    MS->>DS: put(request_id, e2e_time)
    MS->>CS: put(decode_token_time)
    MS->>MS: _update_per_token_execution_times(time, request, batch)
```

**Sources:** [vidur/metrics/metrics_store.py:488-821]()

## Metric Categories

The system categorizes metrics into several distinct types, each using appropriate data structures for efficient storage and analysis.

| Metric Category | Data Structure | Examples |
|-----------------|----------------|----------|
| Request Time Distributions | `DataSeries` | `REQUEST_E2E_TIME`, `REQUEST_EXECUTION_TIME` |
| Token Time Distributions | `CDFSketch` | `DECODE_TOKEN_EXECUTION_PLUS_PREMPTION_TIME` |
| Batch Count Distributions | `CDFSketch` | `BATCH_NUM_TOKENS`, `BATCH_SIZE` |
| Operation Metrics | `CDFSketch` | `MLP_UP_PROJ`, `ATTN_PREFILL`, `ATTN_DECODE` |
| CPU Operation Metrics | `CDFSketch` | `SCHEDULE`, `SAMPLER_E2E`, `MODEL_EXECUTION_E2E` |
| Utilization Metrics | `SeriesAverageMeter` | Memory usage, busy time, MFU per replica |

**Sources:** [vidur/metrics/constants.py]() (imported in [vidur/metrics/metrics_store.py:13-23]())

## Data Structures for Metrics Storage

Vidur uses specialized data structures optimized for different types of performance analysis:

```mermaid
graph TD
    subgraph "DataSeries"
        A["Time series data"] --> B["CDF plots"]
        A --> C["Step plots"] 
        A --> D["Histogram plots"]
        A --> E["CSV export"]
    end
    
    subgraph "CDFSketch"
        F["Distribution sketches"] --> G["CDF analysis"]
        F --> H["Percentile queries"]
        F --> I["Memory efficient"]
    end
    
    subgraph "SeriesAverageMeter" 
        J["Running statistics"] --> K["Time-weighted averages"]
        J --> L["Utilization tracking"]
        J --> M["Resource monitoring"]
    end
```

The `DataSeries` class handles time-indexed data with configurable subsampling, while `CDFSketch` provides memory-efficient distribution tracking. `SeriesAverageMeter` calculates running averages for utilization metrics.

**Sources:** [vidur/metrics/data_series.py](), [vidur/metrics/cdf_sketch.py](), [vidur/metrics/series_average_meter.py]() (imported in [vidur/metrics/metrics_store.py:24-25]())

## Hardware Performance Metrics

The system tracks detailed hardware operation timings through the `on_replica_stage_schedule` method, recording execution times for individual GPU operations:

```mermaid
graph TD
    subgraph "Model Layer Operations"
        A["MLP_UP_PROJ"] --> G["OperationMetrics"]
        B["MLP_ACTIVATION"] --> G
        C["MLP_DOWN_PROJ"] --> G
        D["MLP_DOWN_PROJ_ALL_REDUCE"] --> G
    end
    
    subgraph "Attention Operations"
        E["ATTN_PRE_PROJ"] --> G
        F["ATTN_POST_PROJ"] --> G
        H["ATTN_PREFILL"] --> G
        I["ATTN_DECODE"] --> G
        J["ATTN_KV_CACHE_SAVE"] --> G
    end
    
    subgraph "CPU Operations"
        K["SCHEDULE"] --> L["CpuOperationMetrics"]
        M["SAMPLER_E2E"] --> L
        N["MODEL_EXECUTION_E2E"] --> L
        O["RAY_COMM_TIME"] --> L
    end
    
    G --> P["CDFSketch per operation"]
    L --> Q["CDFSketch per CPU operation"]
```

The `MFUCalculator` computes Model FLOPS Utilization (MFU) metrics to measure how efficiently the hardware is being used during model execution.

**Sources:** [vidur/metrics/metrics_store.py:690-813](), [vidur/utils/mfu_calculator.py]() (imported at [vidur/metrics/metrics_store.py:26]())

## Configuration and Output Control

The metrics system behavior is controlled through the `MetricsConfig` which determines what metrics to collect and how to output them:

```mermaid
graph TD
    A["MetricsConfig"] --> B["write_metrics"]
    A --> C["store_request_metrics"] 
    A --> D["store_batch_metrics"]
    A --> E["store_operation_metrics"]
    A --> F["store_utilization_metrics"]
    
    G["Output Configuration"] --> H["wandb_project"]
    G --> I["wandb_group"]
    G --> J["output_dir"]
    G --> K["store_plots"]
    G --> L["save_table_to_wandb"]
    
    B --> M["@if_write_metrics decorator"]
    M --> N["Conditional metric collection"]
```

The `@if_write_metrics` decorator ensures that metric collection only occurs when enabled, preventing performance overhead during runs where metrics are not needed.

**Sources:** [vidur/metrics/metrics_store.py:31-36](), [vidur/metrics/metrics_store.py:52-54]()

---

