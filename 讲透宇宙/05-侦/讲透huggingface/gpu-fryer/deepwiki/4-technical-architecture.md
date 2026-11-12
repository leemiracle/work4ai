<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/gpu-fryer · page 4 Technical Architecture · fetched 2026-10-26 -->

# Technical Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Cargo.toml](Cargo.toml)
- [src/main.rs](src/main.rs)

</details>



This document provides a detailed explanation of GPU-Fryer's internal architecture and design. It describes the core components, their interactions, and implementation details that enable effective GPU stress testing and performance monitoring.

For information about how to use the tool, please refer to the [Usage Guide](#3). For information about building or contributing to the project, see the [Development Guide](#5).

## System Overview

GPU-Fryer is designed to stress test NVIDIA GPUs by performing intensive matrix multiplication operations while monitoring key performance metrics. The system uses cuBLAS for computation and NVML (NVIDIA Management Library) for monitoring GPU temperatures and throttling conditions.

```mermaid
graph TD
    subgraph "Core Application"
        CLI["Command Line Interface"]
        Core["Core Engine"]
        GPUOps["GPU Operations"]
        Monitor["Monitoring System"]
        Analysis["Results Analysis"]
    end
    
    subgraph "External Libraries"
        CUDA["CUDA/cuBLAS API"]
        NVML["NVIDIA Management Library"]
        Tokio["Async Runtime (Tokio)"]
    end
    
    CLI --> Core
    Core --> GPUOps
    Core --> Monitor
    GPUOps --> CUDA
    Monitor --> NVML
    Monitor --> Analysis
    Core --> Tokio
```

Sources: [src/main.rs:1-9](), [Cargo.toml:6-13]()

## Component Architecture

The application is structured around several key components that work together to provide comprehensive GPU stress testing.

```mermaid
flowchart TD
    main["main()"] --> run["run()"]
    run --> detect_gpus["detect_gpus()"]
    run --> run_with_precision["run_with_precision<T>()"]
    
    run_with_precision --> burn_gpu["burn_gpu<T>()"]
    run_with_precision --> report_progress["report_progress()"]
    
    burn_gpu --> compute["compute<T>()"]
    burn_gpu -- "Operations Count" --> report_progress
    
    report_progress --> poll_temperatures["poll_temperatures()"]
    report_progress --> poll_throttling["poll_throttling()"]
    report_progress --> are_gpus_healthy["are_gpus_healthy()"]
```

Sources: [src/main.rs:143-169](), [src/main.rs:184-221](), [src/main.rs:223-297]()

### Key Components and Functions

| Component | Primary Function | Purpose |
|-----------|------------------|---------|
| Command Line Interface | `Args` struct | Parses user configuration options |
| GPU Detection | `detect_gpus()` | Identifies available NVIDIA GPUs |
| Precision Management | `VariablePrecisionFloat` trait | Supports both FP32 and BF16 operations |
| Matrix Multiplication | `compute<T>()` | Performs GEMM operations via cuBLAS |
| GPU Monitoring | `poll_temperatures()`, `poll_throttling()` | Collects GPU health metrics |
| Results Analysis | `are_gpus_healthy()` | Determines if GPUs are functioning properly |

Sources: [src/main.rs:31-50](), [src/main.rs:125-141](), [src/main.rs:299-315](), [src/main.rs:450-481]()

## Data Flow

The following sequence diagram illustrates how data flows through the system during operation:

```mermaid
sequenceDiagram
    participant User
    participant Main as "main()"
    participant GPU as "burn_gpu()"
    participant Monitor as "report_progress()"
    participant NVML as "NVML Functions"
    
    User->>Main: Start with parameters
    Main->>Main: Detect GPUs
    Main->>Main: Generate test matrices
    
    par For each GPU
        Main->>GPU: Start stress test
        loop Until completion
            GPU->>GPU: Perform matrix multiplication
            GPU->>Monitor: Send operations count
        end
    and Monitoring
        Main->>Monitor: Start monitoring
        loop Until completion
            Monitor->>NVML: Get temperatures
            Monitor->>NVML: Check throttling
            Monitor->>User: Display progress
        end
    end
    
    Monitor->>Monitor: Analyze results
    Monitor->>User: Report GPU health status
```

Sources: [src/main.rs:223-297](), [src/main.rs:327-448](), [src/main.rs:483-517]()

## Core Subsystems

### 1. GPU Detection and Initialization

The system begins by identifying available GPUs and their capabilities:

```mermaid
flowchart TD
    detect_gpus["detect_gpus()"] --> count["CudaDevice::count()"]
    count --> loop["Loop through GPU indices"]
    loop --> create["CudaDevice::new(i)"]
    create --> return["Return GPU devices"]
    
    run["run()"] --> detect_gpus
    run --> check_bf16["Check BF16 support"]
    check_bf16 -- "All GPUs support BF16" --> use_bf16["Use BF16 precision"]
    check_bf16 -- "Some GPUs lack BF16" --> use_fp32["Use FP32 precision"]
```

Sources: [src/main.rs:184-221](), [src/main.rs:572-580]()

### 2. Memory Management

GPU-Fryer allocates memory efficiently to maximize GPU utilization:

- Targets 90% of available GPU memory (`MEM_TO_USE_PCT` = 0.9)
- Uses fixed matrix size of 8192×8192 (defined by `SIZE` constant)
- Creates multiple output matrices as a ring buffer

```mermaid
flowchart TD
    burn_gpu["burn_gpu()"] --> get_mem["get_gpu_memory()"]
    get_mem -- "Free memory" --> calculate["Calculate memory to use (90%)"]
    calculate --> determine["Determine number of output matrices"]
    determine --> alloc_buffers["alloc_buffers()"]
    
    alloc_buffers --> copy_a["Copy matrix A to GPU"]
    alloc_buffers --> copy_b["Copy matrix B to GPU"]
    alloc_buffers --> alloc_out["Allocate output matrices"]
```

Sources: [src/main.rs:20-22](), [src/main.rs:483-517](), [src/main.rs:523-543]()

### 3. Matrix Multiplication Engine

The core stress testing mechanism uses matrix multiplication:

```mermaid
flowchart TD
    compute["compute<T>()"] --> cfg["Configure GEMM operation"]
    cfg --> gemm["cuBLAS::gemm()"]
    gemm --> result["Return Result"]
    
    burn_gpu["burn_gpu()"] --> loop["Loop until stop signal"]
    loop --> out_loop["Iterate through output matrices"]
    out_loop --> compute
    out_loop --> send["Send operation count"]
```

Sources: [src/main.rs:483-517](), [src/main.rs:545-570]()

Key characteristics:
- Uses cuBLAS for optimized matrix multiplication
- Supports both FP32 and BF16 precision through generic implementation
- Continuously performs operations, cycling through output buffers

### 4. Monitoring System

While the stress test runs, the monitoring component:

```mermaid
flowchart TD
    report_progress["report_progress()"] --> setup["Setup monitoring interval"]
    setup --> loop["Loop at 1-second intervals"]
    
    loop --> collect["Collect operations counts"]
    loop --> calc["Calculate FLOPS"]
    loop --> temps["poll_temperatures()"]
    loop --> throttle["poll_throttling()"]
    
    loop --> update["Update BurnResult records"]
    loop --> display["Display progress"]
    
    end_test["End of test"] --> analyze["Analyze results"]
    analyze --> report["Report GPU health"]
```

Sources: [src/main.rs:327-448](), [src/main.rs:299-315]()

The `BurnResult` structure [src/main.rs:52-113]() tracks per-GPU metrics including:
- FLOPS (min, max, average)
- Temperature (min, max, average)
- Throttling events (hardware, thermal software, thermal hardware)

### 5. Results Analysis

After testing completes, GPU-Fryer analyzes results to determine GPU health:

```mermaid
flowchart TD
    are_gpus_healthy["are_gpus_healthy()"] --> acceptable["Calculate acceptable FLOPS threshold"]
    acceptable --> check_loop["Check each GPU"]
    
    check_loop --> check_flops["Check if FLOPS below threshold"]
    check_loop --> check_throttle["Check for throttling events"]
    
    check_flops -- "Performance too low" --> add_reason["Add to reason list"]
    check_throttle -- "Throttling detected" --> add_reason
    
    add_reason --> return["Return health status and reasons"]
```

Sources: [src/main.rs:450-481]()

Health determination is based on:
- Performance consistency (within configurable tolerance of the best GPU)
- Presence of throttling events (with option to tolerate software throttling)

## Implementation Details

### Precision Management

GPU-Fryer supports both FP32 and BF16 precision modes through a trait-based approach:

```rust
trait VariablePrecisionFloat:
    Copy + Debug + Send + Sync + Unpin + DeviceRepr + ValidAsZeroBits + 'static
{
    fn from_f32(f: f32) -> Self;
}
```

Sources: [src/main.rs:125-141]()

This trait allows the core computation functions to be generic over the floating-point type, with specializations for both `f32` and `half::bf16`.

### Asynchronous Execution Model

The application leverages Rust's async/await with Tokio:

```mermaid
graph TD
    subgraph "Main Task"
        main["main()"]
        run["run()"]
    end
    
    subgraph "GPU Tasks"
        gpu1["burn_gpu() for GPU 0"]
        gpu2["burn_gpu() for GPU 1"]
        gpuN["burn_gpu() for GPU N"]
    end
    
    subgraph "Support Tasks"
        monitor["report_progress()"]
        signal["shutdown_signal()"]
        timer["Duration timer"]
    end
    
    main --> run
    run --> gpu1
    run --> gpu2
    run --> gpuN
    run --> monitor
    run --> signal
    run --> timer
    
    gpu1 -- "Channel" --> monitor
    gpu2 -- "Channel" --> monitor
    gpuN -- "Channel" --> monitor
    
    signal -- "AtomicBool" --> gpu1
    signal -- "AtomicBool" --> gpu2
    signal -- "AtomicBool" --> gpuN
    signal -- "AtomicBool" --> monitor
    timer -- "AtomicBool" --> signal
```

Sources: [src/main.rs:242-288](), [src/main.rs:582-602]()

This design enables:
- Parallel operation across multiple GPUs
- Responsive monitoring and user feedback
- Graceful shutdown on timeout or user interruption

### Cross-Thread Communication

Components communicate using:
- Tokio's unbounded channels (`UnboundedSender`/`UnboundedReceiver`) for operation counts
- Shared atomic boolean (`Arc<AtomicBool>`) for coordinating shutdown
- Tokio's task spawning mechanism for parallel execution

Sources: [src/main.rs:16-18](), [src/main.rs:242-253]()

## Dependencies

GPU-Fryer relies on several key dependencies:

| Dependency | Version | Purpose |
|------------|---------|---------|
| cudarc | 0.13.0 | CUDA runtime and cuBLAS operations |
| nvml-wrapper | 0.10.0 | GPU monitoring via NVIDIA Management Library |
| tokio | 1.42 | Async runtime and concurrency |
| clap | 4.5.26 | Command-line argument parsing |
| rand | 0.8.5 | Random number generation for test matrices |
| half | 2.4.1 | BF16 floating-point support |
| anyhow | 1.0.95 | Error handling |

Sources: [Cargo.toml:6-13]()

## Conclusion

GPU-Fryer's architecture is designed for effective GPU stress testing through heavy matrix multiplication workloads while monitoring performance and health metrics. The system's modular design, asynchronous execution model, and comprehensive monitoring capabilities enable accurate detection of GPU performance issues, thermal throttling, and other potential problems.

For more detailed information about specific components, refer to the following pages:
- [GPU Stress Testing Mechanism](#4.2)
- [Performance Monitoring](#4.3)
- [CUDA Integration](#4.4)

---

