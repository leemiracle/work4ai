<!-- source: DeepWiki mcp.deepwiki.com · repo deepspeedai/DeepSpeed · page 12 Profiling, Monitoring, and Autotuning · fetched 2026-10-21 -->

# Profiling, Monitoring, and Autotuning

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.clang-format](.clang-format)
- [csrc/includes/Timer.h](csrc/includes/Timer.h)
- [deepspeed/autotuning/autotuner.py](deepspeed/autotuning/autotuner.py)
- [deepspeed/autotuning/config.py](deepspeed/autotuning/config.py)
- [deepspeed/autotuning/constants.py](deepspeed/autotuning/constants.py)
- [deepspeed/autotuning/scheduler.py](deepspeed/autotuning/scheduler.py)
- [deepspeed/autotuning/tuner/base_tuner.py](deepspeed/autotuning/tuner/base_tuner.py)
- [deepspeed/autotuning/utils.py](deepspeed/autotuning/utils.py)
- [deepspeed/comm/config.py](deepspeed/comm/config.py)
- [deepspeed/monitor/comet.py](deepspeed/monitor/comet.py)
- [deepspeed/monitor/config.py](deepspeed/monitor/config.py)
- [deepspeed/monitor/monitor.py](deepspeed/monitor/monitor.py)
- [deepspeed/monitor/utils.py](deepspeed/monitor/utils.py)
- [deepspeed/profiling/config.py](deepspeed/profiling/config.py)
- [deepspeed/profiling/constants.py](deepspeed/profiling/constants.py)
- [deepspeed/profiling/flops_profiler/README.md](deepspeed/profiling/flops_profiler/README.md)
- [deepspeed/profiling/flops_profiler/profiler.py](deepspeed/profiling/flops_profiler/profiler.py)
- [deepspeed/runtime/activation_checkpointing/config.py](deepspeed/runtime/activation_checkpointing/config.py)
- [deepspeed/runtime/lr_schedules.py](deepspeed/runtime/lr_schedules.py)
- [docs/_tutorials/MoQ-tutorial.md](docs/_tutorials/MoQ-tutorial.md)
- [docs/_tutorials/flops-profiler.md](docs/_tutorials/flops-profiler.md)
- [docs/_tutorials/monitor.md](docs/_tutorials/monitor.md)
- [docs/assets/images/comet_monitor.png](docs/assets/images/comet_monitor.png)
- [docs/code-docs/source/monitor.rst](docs/code-docs/source/monitor.rst)
- [tests/unit/monitor/test_monitor.py](tests/unit/monitor/test_monitor.py)
- [tests/unit/runtime/pipe/test_topology.py](tests/unit/runtime/pipe/test_topology.py)
- [tests/unit/runtime/test_ds_config_model.py](tests/unit/runtime/test_ds_config_model.py)
- [tests/unit/runtime/test_lr_schedulers.py](tests/unit/runtime/test_lr_schedulers.py)

</details>



DeepSpeed provides a comprehensive suite of tools designed to measure hardware efficiency, track training dynamics, and automatically optimize system configurations. These tools bridge the gap between high-level model definitions and low-level hardware performance, enabling developers to identify bottlenecks and maximize throughput without manual trial-and-error.

The system is divided into three primary functional areas:
1.  **Profiling**: Detailed measurement of FLOPs, latency, and parameter counts at the module level.
2.  **Monitoring**: Real-time logging of training metrics to popular backends like TensorBoard and WandB.
3.  **Autotuning**: An automated system that searches for the optimal DeepSpeed configuration for a given model and hardware setup.

### System Architecture Overview

The following diagram illustrates how these components interact with the `DeepSpeedEngine` and the user's training environment.

**Performance and Tuning Orchestration**
```mermaid
graph TD
    subgraph "UserSpace"
        "UserScript"["User Training Script"]
        "DSConfig"["deepspeed_config.json"]
    end

    subgraph "DeepSpeedCore"
        "DSEngine"["DeepSpeedEngine"]
        "MonitorMaster"["MonitorMaster (monitor/monitor.py)"]
        "FlopsProfiler"["FlopsProfiler (profiling/flops_profiler/profiler.py)"]
    end

    subgraph "ExternalSinks"
        "WandB"["Weights & Biases"]
        "TB"["TensorBoard"]
        "CSV"["CSV Files"]
        "Comet"["Comet.ml"]
    end

    subgraph "AutoTuningSystem"
        "Autotuner"["Autotuner (autotuning/autotuner.py)"]
        "RM"["ResourceManager (autotuning/scheduler.py)"]
        "Tuners"["Grid/Random/Model Tuners"]
    end

    "UserScript" --> "DSEngine"
    "DSConfig" --> "DSEngine"
    "DSEngine" --> "MonitorMaster"
    "DSEngine" --> "FlopsProfiler"
    
    "MonitorMaster" --> "WandB"
    "MonitorMaster" --> "TB"
    "MonitorMaster" --> "CSV"
    "MonitorMaster" --> "Comet"

    "Autotuner" --> "RM"
    "RM" --> "UserScript"
    "Tuners" --> "Autotuner"
```
**Sources:** [deepspeed/monitor/monitor.py:1-20](), [deepspeed/profiling/flops_profiler/profiler.py:30-65](), [deepspeed/autotuning/autotuner.py:42-45]()

---

## 12.1 Flops Profiler
The `FlopsProfiler` measures the latency, floating-point operations (FLOPs), and parameter counts of each module within a model [deepspeed/profiling/flops_profiler/profiler.py:30-33](). It is designed to help developers identify specific layers that act as performance bottlenecks.

*   **Integrated Usage**: When enabled via the DeepSpeed configuration file (`flops_profiler` key), it automatically hooks into the training loop [deepspeed/profiling/flops_profiler/profiler.py:34-35]().
*   **Standalone Usage**: It can be used independently of the DeepSpeed runtime by wrapping any `torch.nn.Module` [deepspeed/profiling/flops_profiler/profiler.py:43-44]().
*   **Metric Attribution**: It provides aggregated profiles at different model depths, attributing MACs and latency to parent modules [deepspeed/profiling/flops_profiler/README.md:43-72]().

For details, see [Flops Profiler](#12.1).

**Sources:** [deepspeed/profiling/flops_profiler/profiler.py:30-65](), [deepspeed/profiling/config.py:10-47]()

---

## 12.2 Training Monitor
The Monitoring system provides a centralized `MonitorMaster` class that orchestrates logging to multiple telemetry backends simultaneously [deepspeed/monitor/monitor.py:14-25](). It captures critical training metrics automatically, including:

| Metric Category | Examples | Condition |
| :--- | :--- | :--- |
| **Loss & Convergence** | `train_loss`, `lr` | Always enabled |
| **Hardware Performance** | `elapsed_time_ms_forward`, `elapsed_time_ms_step` | Requires `wall_clock_breakdown` |
| **ZeRO Internals** | `loss_scale` | Requires `fp16` |
| **Mathematical Health** | `ModelBlockParam_{i}` (Eigenvalues) | Requires `eigenvalue` enabled |

Supported backends include **TensorBoard**, **WandB**, **Comet**, and local **CSV** files [deepspeed/monitor/config.py:125-140]().

For details, see [Training Monitor](#12.2).

**Sources:** [deepspeed/monitor/config.py:12-14](), [docs/code-docs/source/monitor.rst:8-20]()

---

## 12.3 Autotuning System
The DeepSpeed `Autotuner` is an automated framework that discovers the optimal configuration (e.g., ZeRO stage, micro-batch size, offloading settings) for a specific model and hardware environment [deepspeed/autotuning/autotuner.py:42-45]().

**Autotuning Workflow and Code Entities**
```mermaid
graph LR
    subgraph "Core Logic"
        "AT"["Autotuner class (autotuner.py)"]
        "Config"["DeepSpeedAutotuningConfig (config.py)"]
    end

    subgraph "Scheduling"
        "RM"["ResourceManager (scheduler.py)"]
        "Node"["Node (scheduler.py)"]
    end

    subgraph "Search Strategies"
        "Grid"["GridSearchTuner (tuner.py)"]
        "Random"["RandomTuner (tuner.py)"]
        "Model"["ModelBasedTuner (tuner.py)"]
    end

    "AT" --> "Config"
    "AT" --> "RM"
    "RM" --> "Node"
    "AT" --> "Grid"
    "AT" --> "Random"
    "AT" --> "Model"
```

The system uses a `ResourceManager` to manage hardware slots across nodes and dispatch experiments in parallel threads [deepspeed/autotuning/scheduler.py:32-57](). It supports various search algorithms, including grid search and model-based tuning, to navigate the complex space of DeepSpeed hyperparameters [deepspeed/autotuning/autotuner.py:21-22]().

For details, see [Autotuning System](#12.3).

**Sources:** [deepspeed/autotuning/autotuner.py:42-107](), [deepspeed/autotuning/scheduler.py:32-57]()

---

