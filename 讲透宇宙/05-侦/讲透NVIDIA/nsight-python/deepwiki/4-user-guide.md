<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/nsight-python · page 4 User Guide · fetched 2026-10-26 -->

# User Guide

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [examples/01_compare_throughput.py](examples/01_compare_throughput.py)
- [examples/02_parameter_sweep.py](examples/02_parameter_sweep.py)
- [examples/README.md](examples/README.md)
- [examples/test_examples.py](examples/test_examples.py)
- [nsight/analyze.py](nsight/analyze.py)

</details>



This guide provides comprehensive documentation for using `nsight-python` to profile GPU kernels. It covers the two primary APIs (`nsight.analyze` and `nsight.annotate`), configuration options, metric collection, and visualization capabilities. As of version 1.0.0, `nsight-python` uses an injection-based approach where the profiler attaches to the running process, supporting environments like Jupyter and Google Colab without script relaunching.

For installation instructions, see [Installation](#2). For a quick introduction to basic concepts, see [Getting Started](#3). For detailed architectural information, see [Architecture Deep Dive](#5).

---

## Profiling Workflow Overview

The `nsight-python` profiling workflow consists of three main steps: code instrumentation, configuration, and execution. 

### End-to-End Profiling Flow

```mermaid
graph TB
    subgraph "Step 1: Code Instrumentation"
        UserCode["User Function<br/>(GPU kernel launcher)"]
        KernelDec["@nsight.analyze.kernel<br/>decorator"]
        AnnotateCtx["nsight.annotate<br/>context manager"]
        
        UserCode -->|"decorate with"| KernelDec
        UserCode -->|"contains"| AnnotateCtx
    end
    
    subgraph "Step 2: Configuration"
        Configs["configs parameter<br/>Iterable[Any]"]
        Runs["runs parameter<br/>int"]
        MetricParam["metrics parameter<br/>Sequence[str]"]
        DeriveMetric["derive_metric parameter<br/>Callable"]
        NormalizeParam["normalize_against parameter<br/>str (annotation name)"]
        
        Configs -->|"passed to"| KernelDec
        Runs -->|"passed to"| KernelDec
        MetricParam -->|"passed to"| KernelDec
        DeriveMetric -->|"passed to"| KernelDec
        NormalizeParam -->|"passed to"| KernelDec
    end
    
    subgraph "Step 3: Execution (v1.0.0 Injection)"
        FuncCall["wrapped_function(...)"]
        NCUAttach["ncu --mode attach<br/>(via try_init_injection)"]
        Results["ProfileResults object"]
        DataFrame["pandas DataFrame<br/>with 'Unit' column"]
        
        FuncCall -->|"triggers"| NCUAttach
        NCUAttach -->|"returns"| Results
        Results -->|"converts to"| DataFrame
    end
    
    KernelDec -->|"creates"| FuncCall
    AnnotateCtx -->|"marks NVTX ranges<br/>domain='nsight-python'"| NCUAttach
    
    style KernelDec fill:#f0f0f0
    style AnnotateCtx fill:#f0f0f0
    style Results fill:#f0f0f0
```

**Sources**: [nsight/analyze.py:61-116](), [nsight/analyze.py:118-191]()

---

## Core API Components

The `nsight-python` package exposes two primary modules in its public API: `nsight.analyze` and `nsight.annotate`.

### API Surface and Code Entities

```mermaid
graph TB
    subgraph "nsight package exports"
        AnalyzeModule["nsight.analyze module"]
        AnnotateClass["nsight.annotate class"]
    end
    
    subgraph "nsight.analyze decorators"
        KernelDec["@analyze.kernel<br/>Main profiling decorator"]
        PlotDec["@analyze.plot<br/>Visualization decorator"]
        IgnoreContext["analyze.ignore_failures()<br/>Context manager"]
    end
    
    subgraph "nsight.annotate usage"
        AsDecorator["@annotate('name')<br/>Function decorator"]
        AsContext["with annotate('name'):<br/>Context manager"]
    end
    
    subgraph "Internal Orchestration"
        NsightProfiler["collection.core.NsightProfiler<br/>Orchestrates runs"]
        NCUCollector["collection.ncu.NCUCollector<br/>Manages ncu attach"]
        ProfileResults["collection.core.ProfileResults<br/>Results container"]
        Extraction["extract_df_from_report<br/>Parses .ncu-rep"]
    end
    
    AnalyzeModule --> KernelDec
    AnalyzeModule --> PlotDec
    AnalyzeModule --> IgnoreContext
    
    AnnotateClass --> AsDecorator
    AnnotateClass --> AsContext
    
    KernelDec -->|"instantiates"| NsightProfiler
    NsightProfiler -->|"uses"| NCUCollector
    NCUCollector -->|"produces"| Extraction
    Extraction -->|"populates"| ProfileResults
    
    PlotDec -->|"consumes"| ProfileResults
    
    style KernelDec fill:#f0f0f0
    style AnnotateClass fill:#f0f0f0
    style ProfileResults fill:#f0f0f0
```

**Sources**: [nsight/analyze.py:61-90](), [examples/01_compare_throughput.py:23-27](), [examples/01_compare_throughput.py:50-51]()

---

## Using the @nsight.analyze.kernel Decorator

The `@nsight.analyze.kernel` decorator is the primary interface for profiling. It executes your function multiple times across different configurations. In v1.0.0, it supports improved keyword-only parameter handling and default value padding for configurations.

### Decorator Syntax Options

| Pattern | Syntax | Use Case |
|---------|--------|----------|
| **No parentheses** | `@nsight.analyze.kernel` | Quick profiling with defaults |
| **With parameters** | `@nsight.analyze.kernel(configs=..., runs=10)` | Custom configuration |

### Key Parameters (v1.0.0)

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `configs` | `Iterable[Any]` | `None` | Arguments for the decorated function. Supports scalars or sequences. |
| `runs` | `int` | `1` | Number of repetitions per configuration. |
| `metrics` | `Sequence[str]` | `["gpu__time_duration.sum"]` | NCU metrics to collect. |
| `derive_metric` | `Callable` | `None` | Function to transform metrics. Must return `(value, unit)` in v1.0.0. |
| `verbosity` | `VerbosityLevel` | `VerbosityLevel.INFO` | Replaces the old `output` parameter. |
| `thermal_device`| `int` | `None` | Pin thermal monitoring to a specific GPU device. |
| `output_csv` | `bool` | `False` | Enable CSV output of results. |

For details, see [Using nsight.analyze.kernel](#4.1).

**Sources**: [nsight/analyze.py:61-86](), [nsight/analyze.py:118-154]()

---

## Using nsight.annotate for Code Regions

The `nsight.annotate` class marks specific code regions for profiling by creating NVTX ranges. It is thread-local; kernels launched from other threads will not be associated with the annotation.

### Usage Example
```python
@nsight.annotate("torch.einsum")
def my_func(a, b):
    return torch.einsum("ij,jk->ik", a, b)

with nsight.annotate("matmul-region"):
    _ = a @ b
```

**Important**: Nested annotations are not supported. For details, see [Using nsight.annotate](#4.2).

**Sources**: [examples/01_compare_throughput.py:23-26](), [examples/01_compare_throughput.py:50-51]()

---

## Profiling Configurations

Configurations define the parameter space. Version 1.0.0 supports:
- **Scalar Configs**: `configs=[1, 2, 3]` for single-argument functions.
- **Multi-dimensional Configs**: Using `itertools.product` for parameter sweeps.
- **Default Value Padding**: If a config provides fewer values than parameters, missing values are filled from function defaults.

For details, see [Profiling Configurations](#4.3).

**Sources**: [nsight/analyze.py:118-132](), [examples/02_parameter_sweep.py:21-21]()

---

## Working with Metrics

Nsight-python v1.0.0 introduces a dedicated `Unit` column in results.
- **Default Metric**: `gpu__time_duration.sum`.
- **Custom Metrics**: Defined via `derive_metric`. To populate the `Unit` column, the function should return a tuple: `(value, "UnitName")`.
- **Multiple Metrics**: You can pass a list of metrics to the `metrics` parameter.

For details, see [Working with Metrics](#4.4).

**Sources**: [nsight/analyze.py:134-152](), [examples/03_custom_metrics.py:73-77]()

---

## Visualization and Plotting

The `@nsight.analyze.plot` decorator generates publication-quality visualizations from `ProfileResults`.

### Visualization Features
- **Plot Types**: Supports `line` and `bar` charts.
- **Subplots**: Use `row_panels` and `col_panels` to organize multi-dimensional sweeps.
- **DataFrames**: The `.to_dataframe()` method exports the full result set including statistical confidence intervals (CI95) and the `Unit` column.

For details, see [Visualization and Plotting](#4.5).

**Sources**: [nsight/analyze.py:244-255](), [examples/05_subplots.py:34-36]()

---

## Related Pages

- [Using nsight.analyze.kernel](#4.1) — Detailed documentation of the decorator and v1.0.0 parameters.
- [Using nsight.annotate](#4.2) — NVTX marking and thread-locality behavior.
- [Profiling Configurations](#4.3) — Parameter sweeps and default value support.
- [Working with Metrics](#4.4) — Collection, derivation, and the Unit column.
- [Visualization and Plotting](#4.5) — Customizing plots and DataFrames.

---

