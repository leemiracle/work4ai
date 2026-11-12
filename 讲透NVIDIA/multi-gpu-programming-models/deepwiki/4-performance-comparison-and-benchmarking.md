<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/multi-gpu-programming-models · page 4 Performance Comparison and Benchmarking · fetched 2026-10-26 -->

# Performance Comparison and Benchmarking

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [bench.sh](bench.sh)
- [nccl/Makefile](nccl/Makefile)
- [nccl/jacobi_kernels.cu](nccl/jacobi_kernels.cu)
- [nccl_overlap/Makefile](nccl_overlap/Makefile)

</details>



This document explains how to benchmark the different Jacobi solver implementations in the multi-GPU programming models repository and how to analyze their performance characteristics. It covers the benchmarking framework, methodology, and techniques for comparing the efficiency of different programming models.

For information about the Jacobi method theory, see [Jacobi Method Theory](#2). For details on building and running specific implementations, see [Building and Running](#5).

## 1. Benchmarking Framework Overview

The repository includes a benchmarking framework based on the `bench.sh` script, which automates the process of executing each implementation with consistent parameters and collecting performance results for comparison.

```mermaid
flowchart TD
    A["bench.sh"]
    A --> B["find_best()"]
    B --> C["Multiple Runs (NREP=5)"]
    C --> D["Sort Results"]
    D --> E["Select Best Runtime"]
    A --> F["Single GPU Tests"]
    A --> G["Multi-GPU Tests"]
    G --> H["Host-Based Communication"]
    G --> I["Direct P2P"]
    G --> J["MPI-Based"]
    G --> K["NCCL-Based"]
    G --> L["NVSHMEM-Based"]
    F --> M["CSV Output"]
    H --> M
    I --> M
    J --> M
    K --> M
    L --> M
```

The benchmarking framework:
- Executes each implementation multiple times to obtain reliable performance measurements
- Controls GPU and CPU affinities for consistent testing
- Configures problem sizes and iteration counts
- Collects and formats results in CSV format for easy analysis

Sources: [bench.sh:1-69](). [README.md:63-64]()

## 2. Key Metrics and Measurements

The Jacobi solver implementations report several performance metrics:

| Metric | Description |
|--------|-------------|
| Runtime | Total execution time of the solver |
| Runtime serial | Estimated serial execution time (for parallel efficiency calculation) |
| Convergence | Whether the solver converged to the solution |
| Iteration count | Number of iterations performed |

The primary performance metric is the runtime, which measures how long it takes to complete a fixed number of iterations or to converge to a solution within a specified tolerance.

```mermaid
flowchart LR
    A["Jacobi Implementation"]
    A -->|"Measures"| B["Runtime"]
    A -->|"Measures"| C["Convergence"]
    A -->|"Reports"| D["Parallel Efficiency"]
    B --> E["CSV Output"]
    C --> E
    D --> E
    E --> F["Performance Analysis"]
```

Sources: [bench.sh:84-85]()

## 3. Running Benchmarks

### 3.1 Basic Usage

To run the benchmarks, execute the `bench.sh` script:

```bash
./bench.sh
```

By default, this will run all enabled benchmarks with the parameters configured in the script.

The script has configuration sections for different hardware platforms:
- DGX-1V
- DGX-2
- DGX-A100
- DGX-H100

You should uncomment the appropriate section for your hardware.

Sources: [bench.sh:30-58]()

### 3.2 Benchmark Parameters

You can modify these parameters at the top of `bench.sh`:

| Parameter | Description |
|-----------|-------------|
| NREP | Number of repetitions for each test (default: 5) |
| NXNY | Problem size (default: 20480) |
| CPUID | CPU ID range for thread binding |
| FIRST_CORE | Starting CPU core ID for thread binding |
| MAX_NUM_GPUS | Maximum number of GPUs to test |
| CUDA_VISIBLE_DEVICES_SETTING | GPU visibility settings for different runs |

Sources: [bench.sh:28-58]()

### 3.3 Individual Implementation Options

Each implementation accepts command-line arguments that can be modified in the script:

```mermaid
flowchart LR
    A["Command Line Options"]
    A --> B["-niter: Iteration count"]
    A --> C["-nccheck: Convergence check frequency"]
    A --> D["-nx: X domain size"]
    A --> E["-ny: Y domain size"]
    A --> F["-csv: Output CSV format"]
    A --> G["-use_hp_streams: High priority streams"]
    
    subgraph "Implementation-Specific Options"
    H["NVSHMEM Options"]
    I["NCCL Options"]
    J["Multi-node Options"]
    end
    
    H --> H1["-use_block_comm"]
    H --> H2["-norm_overlap"]
    H --> H3["-neighborhood_sync"]
    
    I --> I1["-user_buffer_reg"]
    
    J --> J1["-use_mc_red"]
```

Sources: [README.md:44-62]()

## 4. Benchmarking Methodology

The benchmarking system uses several techniques to ensure accurate and consistent results:

### 4.1 Finding Best Performance

The `find_best()` function executes each implementation multiple times and selects the best result:

```mermaid
flowchart TD
    A["find_best()"]
    A --> B["Run implementation NREP times"]
    B --> C["Store results in array"]
    C --> D["Sort results by runtime"]
    D --> E["Select fastest run"]
    E --> F["Return as benchmark result"]
```

This approach helps minimize the impact of system noise and variability.

Sources: [bench.sh:60-67]()

### 4.2 CPU and GPU Pinning

The benchmarking framework uses CPU pinning and GPU visibility settings to ensure consistent hardware utilization:

```mermaid
flowchart LR
    A["Execution Control"]
    A --> B["taskset"]
    B -->|"CPU pinning"| B1["Fixed CPU-to-thread mapping"]
    A --> C["CUDA_VISIBLE_DEVICES"]
    C -->|"GPU selection"| C1["Controlled GPU visibility"]
    A --> D["OpenMP Settings"]
    D --> D1["OMP_PROC_BIND"]
    D --> D2["OMP_PLACES"]
    A --> E["MPI Settings"]
    E --> E1["mpirun"]
    E --> E2["CPU binding options"]
```

Each implementation is tested with progressive GPU counts to evaluate scaling characteristics.

Sources: [bench.sh:89-189](), [bench.sh:193-257]()

## 5. Performance Analysis and Comparison

### 5.1 CSV Output Format

The benchmark results are output in CSV format with the following fields:

```
type, nx, ny, iter_max, nccheck, num_devices, p2p, runtime, runtime_serial
```

Where:
- `type`: Implementation type
- `nx`, `ny`: Problem dimensions
- `iter_max`: Maximum iterations
- `nccheck`: Convergence check frequency
- `num_devices`: Number of GPUs used
- `p2p`: Whether P2P communication was enabled
- `runtime`: Execution time in seconds
- `runtime_serial`: Serial execution time (for speedup calculation)

Sources: [bench.sh:84-85]()

### 5.2 Comparing Communication Models

The benchmarking framework allows systematic comparison of different communication models:

```mermaid
flowchart TB
    subgraph "Communication Models"
        A["Host-Based"]
        B["Direct P2P"]
        C["MPI-Based"]
        D["NCCL-Based"]
        E["NVSHMEM-Based"]
    end
    
    A --> A1["single_threaded_copy"]
    A --> A2["multi_threaded_copy"]
    A --> A3["multi_threaded_copy_overlap"]
    
    B --> B1["multi_threaded_p2p"]
    B --> B2["multi_threaded_p2p_opt"]
    B --> B3["multi_threaded_um"]
    B --> B4["multi_node_p2p"]
    
    C --> C1["mpi"]
    C --> C2["mpi_overlap"]
    
    D --> D1["nccl"]
    D --> D2["nccl_overlap"]
    D --> D3["nccl_graphs"]
    
    E --> E1["nvshmem"]
    
    A1 --> P["Performance Comparison"]
    A2 --> P
    A3 --> P
    B1 --> P
    B2 --> P
    B3 --> P
    B4 --> P
    C1 --> P
    C2 --> P
    D1 --> P
    D2 --> P
    D3 --> P
    E1 --> P
```

Typical performance patterns to analyze include:
- Strong scaling (fixed problem size, increasing GPU count)
- Communication overhead (comparing overlap vs. non-overlap versions)
- Programming model efficiency (comparing different models with the same GPU count)

Sources: [README.md:2-15]()

## 6. Advanced Benchmarking Techniques

### 6.1 Profiling

The Makefiles in various implementations include profiling targets using Nsight Systems:

```bash
make profile NP=<number_of_processes>
```

This generates detailed timeline traces showing kernel execution, memory transfers, and communication patterns.

Sources: [nccl/Makefile:42-43](), [nccl_overlap/Makefile:42-43]()

### 6.2 Compute Sanitizer

For debugging and validation, you can run implementations through NVIDIA Compute Sanitizer:

```bash
make sanitize NP=<number_of_processes>
```

This helps detect memory errors, race conditions, and other runtime issues.

Sources: [nccl/Makefile:36-37](), [nccl_overlap/Makefile:36-37]()

### 6.3 Hardware-Specific Optimizations

Different hardware platforms may require specific benchmarking strategies:

```mermaid
flowchart LR
    A["Hardware Platform"]
    A --> B["DGX-1V"]
    A --> C["DGX-2"]
    A --> D["DGX-A100"]
    A --> E["DGX-H100"]
    
    B --> F["System-Specific Settings"]
    C --> F
    D --> F
    E --> F
    
    F --> G["CPU Binding"]
    F --> H["GPU Topology"]
    F --> I["Memory Configuration"]
    
    G --> J["Performance Results"]
    H --> J
    I --> J
```

For optimal results, modify the hardware-specific settings in `bench.sh` to match your platform's topology.

Sources: [bench.sh:30-58]()

## 7. Interpreting Benchmark Results

When analyzing the results, consider these key factors:

1. **Scaling Efficiency**: How runtime changes as GPU count increases
2. **Communication Overhead**: Difference between overlapped and non-overlapped versions
3. **Programming Model Overhead**: Additional costs of higher-level abstractions
4. **Problem Size Sensitivity**: How performance varies with different problem sizes

The CSV output can be processed with data analysis tools to create visual comparisons and scaling charts.

For multi-GPU scenarios, pay particular attention to:
- Communication patterns (halo exchange efficiency)
- Load balancing across GPUs
- Synchronization overhead
- Memory transfer bandwidth

Sources: [bench.sh:193-257]()

---

