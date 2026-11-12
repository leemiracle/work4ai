<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/optimum-benchmark · page 2 Architecture · fetched 2026-10-26 -->

# Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/test_cli_cpu_ipex.yaml](.github/workflows/test_cli_cpu_ipex.yaml)
- [.github/workflows/test_cli_cpu_llama_cpp.yaml](.github/workflows/test_cli_cpu_llama_cpp.yaml)
- [.gitignore](.gitignore)
- [README.md](README.md)
- [optimum_benchmark/__init__.py](optimum_benchmark/__init__.py)
- [optimum_benchmark/backends/__init__.py](optimum_benchmark/backends/__init__.py)
- [optimum_benchmark/backends/base.py](optimum_benchmark/backends/base.py)
- [optimum_benchmark/backends/config.py](optimum_benchmark/backends/config.py)
- [optimum_benchmark/backends/transformers_utils.py](optimum_benchmark/backends/transformers_utils.py)
- [optimum_benchmark/cli.py](optimum_benchmark/cli.py)
- [optimum_benchmark/import_utils.py](optimum_benchmark/import_utils.py)
- [optimum_benchmark/task_utils.py](optimum_benchmark/task_utils.py)
- [setup.py](setup.py)

</details>



This document outlines the high-level architecture of the Optimum-Benchmark framework, detailing its core components, their relationships, and how they work together to provide a comprehensive benchmarking system for machine learning models. For a general introduction to the system, see [Overview](#1). For detailed information about specific components, refer to their respective wiki pages linked throughout this document.

## High-Level Architecture

Optimum-Benchmark is designed with a modular architecture that separates concerns between different aspects of the benchmarking process. The framework consists of four main components that work together to provide comprehensive benchmarking capabilities:

```mermaid
flowchart TB
    subgraph "Benchmarking Framework"
        A["Benchmark API"] --> B["BenchmarkConfig"]
        A --> C["CLI Interface"]
        B --> D["Launcher"]
        B --> E["Backend"]
        B --> F["Scenario"]
        
        D --> |"executes"| G["Benchmark Workload"]
        E --> |"provides"| G
        F --> |"defines"| G
        G --> H["Benchmark Report"]
        H --> I["Results Output"]
    end

    subgraph "Components"
        J["Trackers"] --> G
    end
```

**Key Components:**

1. **Benchmark API**: The central entry point for running benchmarks programmatically.
2. **Benchmark Configuration**: Defines what and how to benchmark.
3. **Launcher**: Controls how benchmark workloads are executed.
4. **Backend**: Represents machine learning frameworks and optimizations.
5. **Scenario**: Defines benchmarking workflows (inference, training).
6. **Trackers**: Monitor and record performance metrics.

Sources: [optimum_benchmark/benchmark/base.py](), [optimum_benchmark/benchmark/config.py](), [optimum_benchmark/cli.py:1-82]()

## Core Component Relationships

The following diagram shows the detailed relationships between the core components of the system, highlighting how they interact:

```mermaid
classDiagram
    class Benchmark {
        +config: BenchmarkConfig
        +report: BenchmarkReport
        +launch(config) BenchmarkReport
        +from_hub(repo_id) Benchmark
        +save_json(file_path)
        +push_to_hub(repo_id)
    }
    
    class BenchmarkConfig {
        +name: str
        +backend: BackendConfig
        +launcher: LauncherConfig
        +scenario: ScenarioConfig
        +to_dict() dict
        +save_json(file_path)
        +push_to_hub(repo_id)
    }
    
    class BenchmarkReport {
        +results: dict
        +metadata: dict
        +save_json(file_path)
        +save_csv(file_path)
        +save_markdown(file_path)
        +push_to_hub(repo_id)
    }
    
    class BackendConfig {
        <<abstract>>
        +name: str
        +model: str
        +task: str
        +device: str
        +device_ids: str
    }
    
    class LauncherConfig {
        <<abstract>>
        +name: str
        +device_isolation: bool
    }
    
    class ScenarioConfig {
        <<abstract>>
        +name: str
        +latency: bool
        +memory: bool
        +energy: bool
    }
    
    Benchmark *-- BenchmarkConfig
    Benchmark *-- BenchmarkReport
    BenchmarkConfig *-- BackendConfig
    BenchmarkConfig *-- LauncherConfig
    BenchmarkConfig *-- ScenarioConfig
    
    BackendConfig <|-- PyTorchConfig
    BackendConfig <|-- ORTConfig
    BackendConfig <|-- OVConfig
    BackendConfig <|-- IPEXConfig
    BackendConfig <|-- TRTLLMConfig
    BackendConfig <|-- VLLMConfig
    BackendConfig <|-- LlamaCppConfig
    BackendConfig <|-- PyTXIConfig
    
    LauncherConfig <|-- ProcessConfig
    LauncherConfig <|-- TorchrunConfig
    LauncherConfig <|-- InlineConfig
    
    ScenarioConfig <|-- InferenceConfig
    ScenarioConfig <|-- TrainingConfig
    ScenarioConfig <|-- EnergyStarConfig
```

Sources: [optimum_benchmark/__init__.py:1-41](), [optimum_benchmark/benchmark/base.py](), [optimum_benchmark/backends/config.py:1-129]()

## Backend Subsystem

The backend subsystem is responsible for interfacing with different machine learning frameworks and optimization libraries. It provides a unified API for loading models, preparing inputs, and executing workloads.

```mermaid
classDiagram
    class Backend {
        <<abstract>>
        +config: BackendConfigT
        +model_shapes: Dict[str, int]
        +load()
        +prepare_inputs(inputs)
        +forward(inputs, kwargs)
        +generate(inputs, kwargs)
        +call(inputs, kwargs)
        +train(kwargs)
    }
    
    class BackendConfig {
        <<abstract>>
        +name: str
        +model: str
        +processor: str
        +task: str
        +library: str
        +model_type: str
        +device: str
        +device_ids: str
        +seed: int
        +inter_op_num_threads: int
        +intra_op_num_threads: int
        +model_kwargs: Dict
        +processor_kwargs: Dict
    }
    
    Backend *-- BackendConfig
    
    Backend <|-- PyTorchBackend
    Backend <|-- ORTBackend
    Backend <|-- OVBackend
    Backend <|-- IPEXBackend
    Backend <|-- TRTLLMBackend
    Backend <|-- VLLMBackend
    Backend <|-- LlamaCppBackend
    Backend <|-- PyTXIBackend
    
    BackendConfig <|-- PyTorchConfig
    BackendConfig <|-- ORTConfig
    BackendConfig <|-- OVConfig
    BackendConfig <|-- IPEXConfig
    BackendConfig <|-- TRTLLMConfig
    BackendConfig <|-- VLLMConfig
    BackendConfig <|-- LlamaCppConfig
    BackendConfig <|-- PyTXIConfig
```

The backend system is designed for flexibility and extensibility, allowing easy integration of new machine learning frameworks and optimization libraries. Each backend implements the same interface but handles framework-specific details internally.

Key features of the backend system:

1. **Universal Interface**: All backends implement the same methods (`load`, `forward`, `generate`, etc.)
2. **Library Support**: Works with Transformers, Diffusers, TIMM, and LlamaCpp models
3. **Device Flexibility**: Supports CPU, NVIDIA GPUs (CUDA), AMD GPUs (ROCm), and specialized hardware
4. **Optimization Options**: Each backend can apply framework-specific optimizations

Sources: [optimum_benchmark/backends/base.py:1-147](), [optimum_benchmark/backends/config.py:1-129](), [optimum_benchmark/backends/__init__.py:1-24]()

## Task and Model Type Handling

Optimum-Benchmark has a sophisticated system for inferring tasks and model types from model names or directories, allowing it to automatically configure the appropriate benchmarking environment.

```mermaid
flowchart TD
    A["Model Name/Path"] --> B{"Is HF Hub Repo?"}
    B -- Yes --> C["Get repo files"]
    B -- No --> D{"Is Local Directory?"}
    D -- Yes --> C
    D -- No --> E["Error: Invalid Model Path"]
    
    C --> F{"Contains model_index.json?"}
    F -- Yes --> G["Infer Diffusers Library"]
    
    C --> H{"Contains config_sentence_transformers.json?"}
    H -- Yes --> I["Infer Sentence-Transformers Library"]
    
    C --> J{"Contains config.json?"}
    J -- Yes --> K{"Contains pretrained_cfg?"}
    K -- Yes --> L["Infer TIMM Library"]
    K -- No --> M["Infer Transformers Library"]
    
    C --> N{"Contains .gguf files?"}
    N -- Yes --> O["Infer LlamaCpp Library"]
    
    G --> P["Get Pipeline Class Name"]
    M --> Q["Get Model Architecture"]
    L --> R["Get Model Architecture"]
    O --> S["Default to text-generation task"]
    
    P --> T["Map to Benchmark Task"]
    Q --> T
    R --> T["Map to Benchmark Task"]
    S --> T
    
    T --> U["Configure Backend"]
```

Sources: [optimum_benchmark/task_utils.py:1-340](), [optimum_benchmark/backends/config.py:1-129]()

## Launcher Subsystem

The launcher subsystem is responsible for executing benchmark workloads. It provides different strategies for running benchmarks, from simple in-process execution to distributed training across multiple devices.

```mermaid
classDiagram
    class LauncherConfig {
        <<abstract>>
        +name: str
        +device_isolation: bool
    }
    
    class InlineConfig {
        +name: "inline"
    }
    
    class ProcessConfig {
        +name: "process"
        +numactl: bool
        +numactl_args: str
    }
    
    class TorchrunConfig {
        +name: "torchrun"
        +nproc_per_node: int
        +master_addr: str
        +master_port: int
        +numactl: bool
        +numactl_args: str
    }
    
    LauncherConfig <|-- InlineConfig
    LauncherConfig <|-- ProcessConfig
    LauncherConfig <|-- TorchrunConfig
    
    class Launcher {
        <<interface>>
        +launch(config)
    }
    
    class InlineLauncher {
        +launch(config)
    }
    
    class ProcessLauncher {
        +launch(config)
        -_prepare_cmd()
    }
    
    class TorchrunLauncher {
        +launch(config)
        -_prepare_cmd()
    }
    
    Launcher <|.. InlineLauncher
    Launcher <|.. ProcessLauncher
    Launcher <|.. TorchrunLauncher
    
    InlineLauncher -- InlineConfig
    ProcessLauncher -- ProcessConfig
    TorchrunLauncher -- TorchrunConfig
```

Each launcher provides a different execution strategy:

1. **InlineLauncher**: Executes the benchmark in the same process (mainly for debugging)
2. **ProcessLauncher**: Runs the benchmark in a separate process for isolation
3. **TorchrunLauncher**: Uses PyTorch's distributed execution tools for multi-GPU benchmarking

Sources: [optimum_benchmark/launchers/__init__.py](), [optimum_benchmark/__init__.py:16-16](), [optimum_benchmark/cli.py:51-54]()

## Scenario Subsystem

The scenario subsystem defines different benchmarking workflows, configuring what aspects of model performance to measure and how.

```mermaid
classDiagram
    class ScenarioConfig {
        <<abstract>>
        +name: str
        +latency: bool
        +memory: bool
        +energy: bool
    }
    
    class InferenceConfig {
        +name: "inference"
        +warmup_runs: int
        +repeat: int
        +input_shapes: Dict
        +forward_kwargs: Dict
        +generate_kwargs: Dict
        +call_kwargs: Dict
    }
    
    class TrainingConfig {
        +name: "training"
        +warmup_steps: int
        +steps: int
        +dataset_shapes: Dict
        +training_args: Dict
    }
    
    class EnergyStarConfig {
        +name: "energy-star"
        +idle_time: int
        +warmup_time: int
        +measurement_time: int
    }
    
    ScenarioConfig <|-- InferenceConfig
    ScenarioConfig <|-- TrainingConfig
    ScenarioConfig <|-- EnergyStarConfig
    
    class Scenario {
        <<interface>>
        +run(backend)
    }
    
    class InferenceScenario {
        +run(backend)
        -_prepare_inputs()
        -_track_metrics()
    }
    
    class TrainingScenario {
        +run(backend)
        -_prepare_dataset()
        -_track_metrics()
    }
    
    class EnergyStarScenario {
        +run(backend)
        -_measure_energy()
    }
    
    Scenario <|.. InferenceScenario
    Scenario <|.. TrainingScenario
    Scenario <|.. EnergyStarScenario
    
    InferenceScenario -- InferenceConfig
    TrainingScenario -- TrainingConfig
    EnergyStarScenario -- EnergyStarConfig
```

Each scenario type focuses on different aspects of model performance:

1. **InferenceScenario**: Measures the performance of model inference (forward pass, generation)
2. **TrainingScenario**: Evaluates model training performance
3. **EnergyStarScenario**: Focuses on energy efficiency metrics

Sources: [optimum_benchmark/__init__.py:17-17](), [optimum_benchmark/cli.py:47-50]()

## Performance Tracking System

The performance tracking system is responsible for measuring and recording various performance metrics during benchmark execution.

```mermaid
flowchart TB
    subgraph "Tracking System"
        A["Scenario"] -- "Initializes" --> B{"Tracking Type"}
        
        B -- "Measures time" --> C["LatencyTracker"]
        B -- "Measures memory" --> D["MemoryTracker"]
        B -- "Measures energy" --> E["EnergyTracker"]
        
        C --> C1["Basic Latency"]
        C --> C2["Per-token Latency"]
        C --> C3["Per-step Latency"]
        
        D --> D1["System Memory Monitor"]
        D --> D2["Device Memory Monitor"]
        
        E --> E1["CodeCarbon Tracker"]
        
        C1 --> F["Benchmark Report"]
        C2 --> F
        C3 --> F
        D1 --> F
        D2 --> F
        E1 --> F
    end
```

Key features of the tracking system:

1. **Latency Tracking**: Measures execution time with specialized trackers for token generation and training steps
2. **Memory Tracking**: Monitors RAM and device (GPU/TPU) memory usage
3. **Energy Tracking**: Records energy consumption using CodeCarbon

Sources: [README.md:245-247](), [README.md:252-255]()

## Benchmark Execution Flow

The following sequence diagram illustrates the flow of execution when running a benchmark:

```mermaid
sequenceDiagram
    participant User
    participant CLI as "Command Line Interface"
    participant Benchmark
    participant BenchmarkConfig
    participant Launcher
    participant Backend
    participant Scenario
    participant Trackers
    participant Report as "BenchmarkReport"
    
    User->>CLI: Run command with config file
    CLI->>BenchmarkConfig: Parse configuration
    CLI->>Benchmark: launch(config)
    
    Benchmark->>BenchmarkConfig: Validate configuration
    
    Benchmark->>Launcher: Initialize based on config
    Benchmark->>Backend: Initialize based on config
    Benchmark->>Scenario: Initialize based on config
    
    Benchmark->>Launcher: Launch benchmark
    
    Launcher->>Backend: load()
    
    alt Inference Scenario
        Launcher->>Scenario: run(backend)
        Scenario->>Trackers: Start tracking
        Scenario->>Backend: forward/generate/call
        Scenario->>Trackers: Stop tracking
    else Training Scenario
        Launcher->>Scenario: run(backend)
        Scenario->>Trackers: Start tracking
        Scenario->>Backend: train
        Scenario->>Trackers: Stop tracking
    end
    
    Launcher->>Benchmark: Return results
    Benchmark->>Report: Create benchmark report
    Benchmark->>CLI: Return report
    CLI->>User: Display results and save artifacts
```

Sources: [optimum_benchmark/cli.py:56-82](), [README.md:120-163]()

## CLI and Configuration System

Optimum-Benchmark provides a command-line interface built on Hydra, allowing for flexible configuration and execution of benchmarks.

```mermaid
flowchart TB
    A["User"] --> B["optimum-benchmark CLI"]
    B --> C["Hydra Configuration System"]
    
    C --> D["Configuration Store"]
    D --> E1["Backend Configs"]
    D --> E2["Launcher Configs"]
    D --> E3["Scenario Configs"]
    
    C --> F["Load Configuration"]
    F --> G["Create BenchmarkConfig"]
    G --> H["Launch Benchmark"]
    H --> I["Generate Report"]
    I --> J["Save Artifacts"]
```

The CLI enables users to:

1. Run benchmarks with predefined configurations
2. Override configuration parameters from the command line
3. Perform parameter sweeps for comparative benchmarking
4. Save and share benchmark results

Sources: [optimum_benchmark/cli.py:1-82](), [README.md:164-209]()

## System Requirements and Dependencies

Optimum-Benchmark has a modular dependency system, only loading necessary libraries based on the backends and features being used.

```mermaid
flowchart TB
    A["optimum-benchmark"] --> B["Core Dependencies"]
    B --> B1["transformers"]
    B --> B2["accelerate"]
    B --> B3["datasets"]
    B --> B4["hydra-core"]
    B --> B5["psutil"]
    
    A --> C["Backend Dependencies"]
    C --> C1["optimum (+ backend extensions)"]
    C --> C2["torch"]
    C --> C3["onnxruntime"]
    C --> C4["vllm"]
    C --> C5["py-txi"]
    C --> C6["llama-cpp-python"]
    
    A --> D["Optional Features"]
    D --> D1["codecarbon (energy tracking)"]
    D --> D2["bitsandbytes (quantization)"]
    D --> D3["peft (parameter-efficient tuning)"]
    D --> D4["diffusers (image generation)"]
    D --> D5["timm (computer vision)"]
```

The setup system automatically detects available hardware and suggests appropriate dependencies to install:

1. Detects NVIDIA GPUs and installs NVIDIA utilities
2. Detects AMD GPUs and installs AMD utilities
3. Provides extras for specific backends (e.g., `pip install optimum-benchmark[vllm]`)

Sources: [setup.py:1-123](), [import_utils.py:1-277]()

## Summary

The architecture of Optimum-Benchmark is designed to be:

1. **Modular**: Components can be swapped or extended independently
2. **Extensible**: New backends, scenarios, and trackers can be added easily
3. **Flexible**: Supports various hardware, frameworks, and benchmarking scenarios
4. **Comprehensive**: Measures multiple aspects of performance (speed, memory, energy)

This design allows Optimum-Benchmark to support a wide range of machine learning models, frameworks, and hardware, making it a versatile tool for performance evaluation and optimization.

---

