<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/mlperf-common · page 2 Core MLPerf Systems · fetched 2026-10-26 -->

# Core MLPerf Systems

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [mlperf_common/callbacks/__init__.py](mlperf_common/callbacks/__init__.py)
- [mlperf_common/callbacks/logging.py](mlperf_common/callbacks/logging.py)
- [mlperf_common/logging.py](mlperf_common/logging.py)

</details>



## Purpose and Scope

This document covers the most critical systems in the MLPerf Common repository that enable MLPerf benchmark compliance, distributed training coordination, and performance logging. These systems provide the foundational infrastructure for running MLPerf benchmarks across different machine learning frameworks with standardized logging and metric tracking.

The core systems include PyTorch Lightning integration callbacks, the MLPerf logging wrapper infrastructure, and distributed training statistics collection. For framework-specific implementations and handlers, see [Framework Integration](#2.3). For command-line utilities and operational tools, see [Client Utilities](#3).

## System Architecture Overview

The core MLPerf systems form a layered architecture where PyTorch Lightning callbacks coordinate with the MLPerf logging infrastructure to ensure benchmark compliance across distributed training environments.

```mermaid
graph TB
    subgraph "PyTorch Lightning Integration"
        LoggingCallback["LoggingCallback<br/>MLPerf Event Coordination"]
        MLPerfLogger["MLPerfLogger<br/>Target Metric Tracking"]
        StatsLogCallback["StatsLogCallback<br/>Distributed Statistics"]
    end
    
    subgraph "MLPerf Logging Infrastructure"
        MLLoggerWrapper["MLLoggerWrapper<br/>Distributed Logging Coordination"]
        PyTCommunicationHandler["PyTCommunicationHandler<br/>torch.distributed Backend"]
    end
    
    subgraph "MLPerf Event System"
        INIT_STOP["INIT_STOP"]
        RUN_START["RUN_START"] 
        BLOCK_START["BLOCK_START"]
        EVAL_START["EVAL_START"]
        EVAL_ACCURACY["EVAL_ACCURACY"]
        EVAL_STOP["EVAL_STOP"]
        BLOCK_STOP["BLOCK_STOP"]
        RUN_STOP["RUN_STOP"]
    end
    
    LoggingCallback --> MLLoggerWrapper
    MLPerfLogger --> MLLoggerWrapper
    StatsLogCallback --> PyTCommunicationHandler
    MLLoggerWrapper --> PyTCommunicationHandler
    
    LoggingCallback --> INIT_STOP
    LoggingCallback --> RUN_START
    LoggingCallback --> BLOCK_START
    LoggingCallback --> EVAL_START
    LoggingCallback --> EVAL_STOP  
    LoggingCallback --> BLOCK_STOP
    LoggingCallback --> RUN_STOP
    
    MLPerfLogger --> EVAL_ACCURACY
    
    MLLoggerWrapper --> INIT_STOP
    MLLoggerWrapper --> RUN_START
    MLLoggerWrapper --> RUN_STOP
```

Sources: [mlperf_common/callbacks/logging.py:41-42](), [mlperf_common/logging.py:21-43]()

## PyTorch Lightning Callback System

The callback system provides MLPerf-compliant event logging throughout the training lifecycle. The `LoggingCallback` class integrates with PyTorch Lightning's training loop to emit required MLPerf events at precise timing points.

### LoggingCallback Core Functionality

```mermaid
graph LR
    subgraph "Training Lifecycle Events"
        on_train_epoch_start["on_train_epoch_start()"]
        on_validation_start["on_validation_start()"]
        on_validation_end["on_validation_end()"]  
        on_train_end["on_train_end()"]
    end
    
    subgraph "MLPerf Event Emission"
        warmup["warmup()"]
        log_init_stop_run_start["mllogger.log_init_stop_run_start()"]
        _start_train_block["_start_train_block()"]
        _end_train_block["_end_train_block()"]
        _log_train_step_time["_log_train_step_time()"]
    end
    
    subgraph "Timer Management"
        DeltaTimer["DeltaTimer<br/>Performance Timing"]
        log_custom_timedelta["log_custom_timedelta()"]
    end
    
    on_train_epoch_start --> warmup
    on_train_epoch_start --> log_init_stop_run_start
    on_train_epoch_start --> _start_train_block
    
    on_validation_start --> _log_train_step_time
    on_validation_start --> _end_train_block
    
    on_validation_end --> _start_train_block
    on_train_end --> _end_train_block
    
    warmup --> log_custom_timedelta
    _log_train_step_time --> DeltaTimer
    log_custom_timedelta --> DeltaTimer
```

The `LoggingCallback` manages training blocks and validation cycles with precise timing measurements. Key responsibilities include:

- **Warmup Handling**: Executes one-time initialization logging via `warmup()` method
- **Block Management**: Coordinates `BLOCK_START` and `BLOCK_STOP` events around training intervals
- **Timing Measurement**: Uses `DeltaTimer` class for precise performance timing
- **Status Tracking**: Maintains `train_block_started` and `train_current_block` state

Sources: [mlperf_common/callbacks/logging.py:57-219]()

### MLPerfLogger Target Validation

The `MLPerfLogger` extends PyTorch Lightning's `Logger` interface to provide target metric tracking and early stopping functionality.

```mermaid
graph TB
    subgraph "MLPerfLogger Configuration"
        callback_cls["callback_cls: type[LoggingCallback]"]
        validation_metric["validation_metric: str"]
        target_validation_metric["target_validation_metric: float"]
        target_validation_metric_type["target_validation_metric_type: Literal['min', 'max']"]
    end
    
    subgraph "Validation Logic"
        log_metrics["log_metrics()"]
        compute_validation_metric["compute_validation_metric()"]
        target_reached_check["Target Reached Check"]
        trainer_should_stop["trainer.should_stop = True"]
    end
    
    subgraph "MLPerf Events"
        EVAL_ACCURACY["EVAL_ACCURACY Event"]
        log_hyperparams["log_hyperparams()"]
    end
    
    log_metrics --> compute_validation_metric
    compute_validation_metric --> target_reached_check
    target_reached_check --> trainer_should_stop
    log_metrics --> EVAL_ACCURACY
    
    validation_metric --> compute_validation_metric
    target_validation_metric --> target_reached_check
    target_validation_metric_type --> target_reached_check
```

The logger automatically stops training when validation metrics reach target thresholds, ensuring MLPerf compliance for convergence criteria.

Sources: [mlperf_common/callbacks/logging.py:221-327]()

## MLPerf Logging Infrastructure

The `MLLoggerWrapper` provides distributed logging coordination with communication handlers for different frameworks. It wraps the official MLPerf logger with additional synchronization and distributed coordination capabilities.

### MLLoggerWrapper Core Methods

| Method | Purpose | Synchronization |
|--------|---------|----------------|
| `start()` | Log time interval start | Configurable via `sync` parameter |
| `end()` | Log time interval end | Configurable via `sync` parameter |
| `event()` | Log point-in-time event | Configurable via `sync` parameter |
| `log_init_stop_run_start()` | Log INIT_STOP and RUN_START | Full barrier synchronization |
| `log_run_stop()` | Log RUN_STOP with status | Configurable synchronization |

The wrapper supports several key distributed coordination features:

- **Unique Logging**: Only `unique_log_rank` process logs when `unique=True`
- **Barrier Synchronization**: Calls `comm_handler.barrier()` before logging when `sync=True`
- **Stack Trace Offset**: Maintains proper call stack attribution with `default_stack_offset`

Sources: [mlperf_common/logging.py:44-90]()

### Communication Handler Integration

```mermaid
graph LR
    MLLoggerWrapper --> CommunicationHandler["comm_handler<br/>(CommunicationHandler)"]
    CommunicationHandler --> global_rank["global_rank()"]
    CommunicationHandler --> barrier["barrier(sync_group)"]
    
    subgraph "Framework Implementations"
        PyTCommunicationHandler["PyTCommunicationHandler<br/>torch.distributed"]
        MPICommunicationHandler["MPICommunicationHandler<br/>MPI/Horovod"]
    end
    
    CommunicationHandler --> PyTCommunicationHandler
    CommunicationHandler --> MPICommunicationHandler
```

The communication handler abstraction allows the same logging infrastructure to work across different distributed training frameworks.

Sources: [mlperf_common/logging.py:75-85]()

## Distributed Statistics Collection

The `StatsLogCallback` provides comprehensive statistics collection for distributed training environments, supporting tensor parallel, pipeline parallel, and data parallel configurations.

### Statistics Collection Architecture

```mermaid
graph TB
    subgraph "Hook Registration"
        register_hooks["register_hooks()"]
        _activation_hook["_activation_hook()"]
        _grad_hook["_grad_hook()"]
    end
    
    subgraph "Statistics Computation"
        _compute_tensor_stats["_compute_tensor_stats()"]
        _collect_group_stats["_collect_group_stats()"]
        _aggregate_local_stats["_aggregate_local_stats()"]
    end
    
    subgraph "Parallel Coordination"
        _collect_pp_dicts["_collect_pp_dicts()<br/>Pipeline Parallel"]
        _collect_tp_dicts["_collect_tp_dicts()<br/>Tensor Parallel"]
        _gather_group_stats["_gather_group_stats()<br/>Data Parallel"]
    end
    
    subgraph "Statistics Types"
        grad_stats["grad_stats: {}"]
        activation_stats["activation_stats: {}"]
        weights_stats["weights_stats: {}"]
        train_loss_batch["train_loss_batch: []"]
        val_loss_batch["val_loss_batch: []"]
    end
    
    register_hooks --> _activation_hook
    register_hooks --> _grad_hook
    
    _activation_hook --> _compute_tensor_stats
    _grad_hook --> _compute_tensor_stats
    
    _compute_tensor_stats --> _collect_group_stats
    _collect_group_stats --> _gather_group_stats
    _collect_group_stats --> _aggregate_local_stats
    
    _collect_group_stats --> _collect_pp_dicts
    _collect_group_stats --> _collect_tp_dicts
    
    _aggregate_local_stats --> grad_stats
    _aggregate_local_stats --> activation_stats
    _aggregate_local_stats --> weights_stats
```

### Key Statistics Features

The `StatsLogCallback` supports advanced distributed training configurations:

- **Virtual Pipeline Parallelism**: Handles multi-chunk models with `use_vp` and `set_layer_vp_chunk()`
- **Tensor Parallelism**: Configurable reduction via `REDUCE_TP` environment variable
- **Selective Logging**: Controlled via `LOG_EVERY_N_BATCHES` and `RUN_N_ITERS` environment variables
- **Hook Management**: Automatic registration/removal of forward and backward hooks

Statistics collected include tensor mean, variance, min, max, and L2 norm across all parallel dimensions.

Sources: [mlperf_common/callbacks/logging.py:329-741]()

## Code Entity Mapping

The following diagram maps the natural language system concepts to specific code entities that developers can search for in the codebase:

```mermaid
graph LR
    subgraph "Core Classes"
        LoggingCallback_class["LoggingCallback<br/>mlperf_common.callbacks.logging"]
        MLPerfLogger_class["MLPerfLogger<br/>mlperf_common.callbacks.logging"]
        StatsLogCallback_class["StatsLogCallback<br/>mlperf_common.callbacks.logging"]
        MLLoggerWrapper_class["MLLoggerWrapper<br/>mlperf_common.logging"]
    end
    
    subgraph "Key Methods"
        on_train_epoch_start["on_train_epoch_start()"]
        on_validation_start["on_validation_start()"]
        log_init_stop_run_start["log_init_stop_run_start()"]
        _start_train_block["_start_train_block()"]
        _end_train_block["_end_train_block()"]
        log_metrics["log_metrics()"]
        _compute_tensor_stats["_compute_tensor_stats()"]
        _collect_group_stats["_collect_group_stats()"]
    end
    
    subgraph "Global Instance"
        mllogger_instance["mllogger<br/>Global MLLoggerWrapper Instance"]
    end
    
    subgraph "Configuration"
        force_success["FORCE_SUCCESS_STATUS env var"]
        reduce_tp["REDUCE_TP env var"]
        log_every_n_batches["LOG_EVERY_N_BATCHES env var"]
        run_n_iters["RUN_N_ITERS env var"]
    end
    
    LoggingCallback_class --> on_train_epoch_start
    LoggingCallback_class --> on_validation_start
    LoggingCallback_class --> _start_train_block
    LoggingCallback_class --> _end_train_block
    
    MLPerfLogger_class --> log_metrics
    
    StatsLogCallback_class --> _compute_tensor_stats
    StatsLogCallback_class --> _collect_group_stats
    
    MLLoggerWrapper_class --> log_init_stop_run_start
    MLLoggerWrapper_class --> mllogger_instance
```

Sources: [mlperf_common/callbacks/__init__.py:16](), [mlperf_common/callbacks/logging.py:41](), [mlperf_common/callbacks/logging.py:348-351]()

---

