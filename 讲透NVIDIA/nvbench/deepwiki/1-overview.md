<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/nvbench · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [docs/benchmarks.md](docs/benchmarks.md)
- [examples/CMakeLists.txt](examples/CMakeLists.txt)
- [examples/cpu_only.cu](examples/cpu_only.cu)
- [examples/summaries.cu](examples/summaries.cu)
- [nvbench/detail/measure_cpu_only.cuh](nvbench/detail/measure_cpu_only.cuh)
- [nvbench/detail/measure_cpu_only.cxx](nvbench/detail/measure_cpu_only.cxx)
- [nvbench/main.cuh](nvbench/main.cuh)
- [nvbench/nvbench.cuh](nvbench/nvbench.cuh)

</details>



This document provides a high-level overview of NVBench, a C++17 CUDA benchmarking framework designed to simplify GPU kernel performance measurement and analysis. It covers the system's architecture, core components, and primary workflows. For detailed information about creating benchmarks, see [Getting Started](#2). For specific measurement strategies and execution details, see [Measurement Systems](#3.2).

NVBench enables developers to create comprehensive benchmarks with parameter sweeps, multiple measurement strategies, and rich output formatting. The framework handles the complexities of GPU timing, statistical analysis, and result presentation while providing a simple API for benchmark definition.

## System Architecture

The NVBench framework consists of several interconnected subsystems that work together to provide comprehensive CUDA benchmarking capabilities:

**NVBench Core Architecture**
```mermaid
graph TB
    subgraph "User API Layer"
        MACROS["NVBENCH_BENCH macros<br/>benchmark registration"]
        STATE["nvbench::state<br/>configuration access"]
        LAUNCH["nvbench::launch<br/>kernel execution context"]
    end
    
    subgraph "Benchmark Management"
        BENCH_BASE["benchmark_base<br/>benchmark definition"]
        BENCH_MGR["benchmark_manager<br/>global registry"]
        STATE_GEN["state_generator<br/>parameter combinations"]
    end
    
    subgraph "Execution Engine"
        RUNNER["runner<br/>execution orchestration"]
        MEASURE_COLD["measure_cold<br/>individual kernel runs"]
        MEASURE_HOT["measure_hot<br/>batched execution"]
        MEASURE_CPU["measure_cpu_only<br/>CPU-only timing"]
        MEASURE_CUPTI["measure_cupti<br/>CUPTI profiling"]
    end
    
    subgraph "Configuration System"
        OPTION_PARSER["option_parser<br/>CLI processing"]
        AXES_META["axes_metadata<br/>parameter definitions"]
        CRITERION_MGR["criterion_manager<br/>stopping conditions"]
    end
    
    subgraph "CUDA Infrastructure"
        CUDA_STREAM["cuda_stream<br/>stream management"]
        DEVICE_INFO["device_info<br/>GPU properties"]
        CUDA_TIMER["cuda_timer<br/>GPU timing"]
        CPU_TIMER["cpu_timer<br/>CPU timing"]
    end
    
    subgraph "Output System"
        SUMMARY["summary<br/>performance metrics"]
        PRINTER_BASE["printer_base<br/>output formatting"]
        MARKDOWN["markdown_printer"]
        CSV["csv_printer"]
        JSON["json_printer"]
    end
    
    MACROS --> BENCH_BASE
    STATE --> LAUNCH
    BENCH_BASE --> BENCH_MGR
    BENCH_MGR --> STATE_GEN
    STATE_GEN --> RUNNER
    RUNNER --> MEASURE_COLD
    RUNNER --> MEASURE_HOT
    RUNNER --> MEASURE_CPU
    RUNNER --> MEASURE_CUPTI
    OPTION_PARSER --> AXES_META
    OPTION_PARSER --> CRITERION_MGR
    MEASURE_COLD --> CUDA_STREAM
    MEASURE_COLD --> CUDA_TIMER
    MEASURE_CPU --> CPU_TIMER
    RUNNER --> SUMMARY
    SUMMARY --> PRINTER_BASE
    PRINTER_BASE --> MARKDOWN
    PRINTER_BASE --> CSV
    PRINTER_BASE --> JSON
```

Sources: [nvbench/nvbench.cuh:1-40](), [nvbench/main.cuh:1-254](), [README.md:1-186]()

## Core Benchmarking Workflow

The benchmarking process follows a well-defined sequence from benchmark definition through result output:

**Benchmark Execution Flow**
```mermaid
flowchart TD
    DEFINE["User defines benchmark<br/>NVBENCH_BENCH(func)"] --> REGISTER["benchmark_base registration<br/>benchmark_manager::add()"]
    REGISTER --> MAIN_INIT["main_initialize()<br/>CUDA setup + manager init"]
    MAIN_INIT --> PARSE["option_parser::parse()<br/>CLI argument processing"]
    PARSE --> GEN_STATES["state_generator::generate()<br/>cartesian product of axes"]
    
    GEN_STATES --> STATE_LOOP["For each nvbench::state"]
    STATE_LOOP --> MEASURE_SELECT{"Measurement selection<br/>based on exec_tag"}
    
    MEASURE_SELECT -->|"CPU-only"| CPU_MEASURE["measure_cpu_only::operator()<br/>CPU timing only"]
    MEASURE_SELECT -->|"Cold measurement"| COLD_MEASURE["measure_cold::operator()<br/>individual GPU runs"]
    MEASURE_SELECT -->|"Hot measurement"| HOT_MEASURE["measure_hot::operator()<br/>batched GPU execution"]
    MEASURE_SELECT -->|"CUPTI profiling"| CUPTI_MEASURE["measure_cupti::operator()<br/>hardware counters"]
    
    CPU_MEASURE --> COLLECT_RESULTS["summary object creation<br/>performance metrics"]
    COLD_MEASURE --> COLLECT_RESULTS
    HOT_MEASURE --> COLLECT_RESULTS
    CUPTI_MEASURE --> COLLECT_RESULTS
    
    COLLECT_RESULTS --> MORE_STATES{"More states?"}
    MORE_STATES -->|"Yes"| STATE_LOOP
    MORE_STATES -->|"No"| OUTPUT["printer_base::print_benchmark_results()<br/>formatted output"]
    
    OUTPUT --> CLEANUP["main_finalize()<br/>cudaDeviceReset()"]
```

Sources: [nvbench/main.cuh:112-156](), [nvbench/detail/measure_cpu_only.cuh:88-142](), [docs/benchmarks.md:1-516]()

## Key Components

### Benchmark Definition and Registration

The `benchmark_base` class serves as the foundation for all benchmarks, storing configuration data and parameter axes. The `benchmark_manager` maintains a global registry of all benchmarks defined using the `NVBENCH_BENCH` macro system.

| Component | Role | Key Methods |
|-----------|------|-------------|
| `benchmark_base` | Benchmark definition storage | `run()`, `get_config_count()`, `set_name()` |
| `benchmark_manager` | Global benchmark registry | `initialize()`, `get()` (singleton) |
| `NVBENCH_BENCH` | Benchmark registration macro | Creates and registers benchmark instances |

### State Management and Configuration

The `nvbench::state` object provides runtime access to benchmark parameters and execution context. The `state_generator` creates all possible parameter combinations from defined axes.

| Component | Role | Key Methods |
|-----------|------|-------------|
| `nvbench::state` | Runtime parameter access | `get_int64()`, `get_float64()`, `get_string()`, `exec()` |
| `state_generator` | Parameter combination generation | Generates cartesian product of all axes |
| `axes_metadata` | Parameter axis definitions | Stores axis names, values, and types |

### Measurement Backends

NVBench provides multiple measurement strategies optimized for different use cases:

| Backend | Purpose | Implementation |
|---------|---------|----------------|
| `measure_cold` | Individual GPU kernel runs | Clean L2 cache between runs |
| `measure_hot` | Batched GPU execution | Multiple back-to-back runs |
| `measure_cpu_only` | CPU-only workloads | Host-side timing only |
| `measure_cupti` | Hardware profiling | CUPTI-based metrics collection |

Sources: [nvbench/detail/measure_cpu_only.cuh:40-142](), [README.md:21-31](), [docs/benchmarks.md:417-451]()

## Measurement Strategy Selection

NVBench automatically selects the appropriate measurement backend based on execution tags and benchmark configuration:

**Measurement Backend Selection**
```mermaid
graph TB
    EXEC_CALL["state.exec() called"] --> TAG_CHECK{"exec_tag analysis"}
    
    TAG_CHECK -->|"no_gpu tag"| CPU_ONLY_CHECK{"is_cpu_only() == true?"}
    TAG_CHECK -->|"sync tag"| SYNC_MEASURE["Synchronized measurement<br/>with device sync"]
    TAG_CHECK -->|"timer tag"| TIMER_MEASURE["Manual timer mode<br/>explicit start/stop"]
    TAG_CHECK -->|"default"| DEFAULT_MEASURE["Standard GPU measurement"]
    
    CPU_ONLY_CHECK -->|"Yes"| CPU_BACKEND["measure_cpu_only backend<br/>CPU timing only"]
    CPU_ONLY_CHECK -->|"No"| ERROR["Runtime error<br/>invalid configuration"]
    
    DEFAULT_MEASURE --> GPU_BACKEND_SELECT{"GPU backend selection"}
    GPU_BACKEND_SELECT -->|"Cold measurement"| COLD_BACKEND["measure_cold backend<br/>individual kernel runs"]
    GPU_BACKEND_SELECT -->|"Hot measurement"| HOT_BACKEND["measure_hot backend<br/>batched execution"]
    
    SYNC_MEASURE --> SYNC_BACKEND["measure_with_sync backend<br/>handles internal sync"]
    TIMER_MEASURE --> TIMER_BACKEND["Timer-enabled backend<br/>manual timing control"]
    
    COLD_BACKEND --> CUPTI_CHECK{"CUPTI enabled?"}
    HOT_BACKEND --> CUPTI_CHECK
    CUPTI_CHECK -->|"Yes"| CUPTI_BACKEND["measure_cupti backend<br/>hardware profiling"]
    CUPTI_CHECK -->|"No"| STANDARD_GPU["Standard GPU timing"]
```

Sources: [docs/benchmarks.md:308-341](), [docs/benchmarks.md:361-401](), [examples/cpu_only.cu:1-84]()

## Usage Patterns

### Basic Benchmark Definition

```cpp
void my_benchmark(nvbench::state& state) {
  state.exec([](nvbench::launch& launch) {
    my_kernel<<<blocks, threads, 0, launch.get_stream()>>>();
  });
}
NVBENCH_BENCH(my_benchmark);
```

### Parameter Sweeps

```cpp
NVBENCH_BENCH(benchmark)
  .add_int64_axis("NumInputs", {16, 64, 256, 1024})
  .add_float64_axis("Quality", {0.5, 0.75, 1.0});
```

### Advanced Execution Control

```cpp
state.exec(nvbench::exec_tag::sync | nvbench::exec_tag::timer,
           [](nvbench::launch& launch, auto& timer) {
             timer.start();
             /* timed region */
             timer.stop();
           });
```

Sources: [docs/benchmarks.md:1-56](), [docs/benchmarks.md:88-125](), [docs/benchmarks.md:332-338](), [examples/summaries.cu:26-74]()

This architecture enables NVBench to provide comprehensive CUDA benchmarking capabilities while maintaining a simple user interface and handling the complexities of GPU performance measurement automatically.

---

