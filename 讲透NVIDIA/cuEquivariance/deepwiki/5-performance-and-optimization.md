<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/cuEquivariance · page 5 Performance and Optimization · fetched 2026-10-26 -->

# Performance and Optimization

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [cuequivariance_jax/cuequivariance_jax/benchmarking.py](cuequivariance_jax/cuequivariance_jax/benchmarking.py)
- [cuequivariance_jax/tests/benchmarking_test.py](cuequivariance_jax/tests/benchmarking_test.py)
- [cuequivariance_jax/tests/sigmoid_gated_dual_gemm_test.py](cuequivariance_jax/tests/sigmoid_gated_dual_gemm_test.py)
- [cuequivariance_torch/cuequivariance_torch/benchmarking.py](cuequivariance_torch/cuequivariance_torch/benchmarking.py)
- [cuequivariance_torch/tests/benchmarking_test.py](cuequivariance_torch/tests/benchmarking_test.py)

</details>



This document covers performance measurement, benchmarking utilities, CUDA kernel optimization, and tuning strategies in the cuEquivariance library. It focuses on the technical implementation of performance-critical components and optimization techniques used across both JAX and PyTorch backends.

For general architecture and backend selection, see [Overview](#1). For specific CUDA kernel implementations, see [CUDA Kernels and Tuning](#5.2). For benchmarking methodology and tools, see [Benchmarking](#5.1).

## Performance Measurement Architecture

The cuEquivariance library implements sophisticated performance measurement infrastructure that handles GPU clock rate calibration, adaptive iteration counting, and proper synchronization across both JAX and PyTorch backends.

```mermaid
graph TD
    subgraph "Performance Measurement Workflow"
        START["measure_clock_ticks()"]
        WARMUP["Warmup Phase<br/>• JIT compilation<br/>• GPU clock stabilization<br/>• Library loading"]
        CALIBRATE["Clock Rate Calibration<br/>• sleep() operations<br/>• Tick rate measurement<br/>• Rate validation"]
        MEASURE["Main Measurement<br/>• Timed execution<br/>• Event recording<br/>• Iteration control"]
        VALIDATE["Result Validation<br/>• Clock rate consistency<br/>• Measurement duration<br/>• Synchronization timing"]
        ADAPTIVE["Adaptive Tuning<br/>• Iteration adjustment<br/>• Fill time optimization<br/>• Rejection handling"]
    end
    
    subgraph "Backend-Specific Implementation"
        JAX_IMPL["JAX Implementation<br/>• _event_record<br/>• _event_elapsed<br/>• noop operations"]
        TORCH_IMPL["PyTorch Implementation<br/>• torch.cuda.Event<br/>• elapsed_time()<br/>• synchronize()"]
    end
    
    subgraph "CUDA Operations"
        SLEEP["sleep(time, state)"]
        SYNC["synchronize(state)"]
        NOOP["noop(data)"]
        EVENTS["GPU Events<br/>• Start/end timing<br/>• Elapsed calculation"]
    end
    
    START --> WARMUP
    WARMUP --> CALIBRATE
    CALIBRATE --> MEASURE
    MEASURE --> VALIDATE
    VALIDATE --> ADAPTIVE
    ADAPTIVE --> VALIDATE
    
    JAX_IMPL --> SLEEP
    JAX_IMPL --> EVENTS
    TORCH_IMPL --> EVENTS
    TORCH_IMPL --> SYNC
    
    SLEEP --> CALIBRATE
    EVENTS --> MEASURE
    SYNC --> VALIDATE
    NOOP --> JAX_IMPL
```

Sources: [cuequivariance_jax/cuequivariance_jax/benchmarking.py:25-182](), [cuequivariance_torch/cuequivariance_torch/benchmarking.py:24-158]()

## CUDA Optimization Pipeline

The library employs a multi-layered CUDA optimization strategy with Triton kernel tuning, precision control, and intelligent fallback mechanisms.

```mermaid
graph TD
    subgraph "Optimization Request Flow"
        USER_CALL["User Function Call"]
        BACKEND_CHECK["Backend Detection<br/>• CUDA availability<br/>• Device placement<br/>• Fallback flags"]
        TUNING_MODE["Tuning Mode Selection<br/>• CUEQ_TRITON_TUNING<br/>• AOT vs ONDEMAND<br/>• Cache policies"]
        PRECISION_SELECT["Precision Selection<br/>• Precision.DEFAULT<br/>• Precision.TF32<br/>• Precision.IEEE"]
    end
    
    subgraph "Triton Kernel Optimization"
        AOT_TUNING["AOT Tuning<br/>• Pre-compilation<br/>• Optimal config search<br/>• Cache generation"]
        ONDEMAND_TUNING["On-Demand Tuning<br/>• Runtime optimization<br/>• Dynamic adaptation<br/>• JIT compilation"]
        CACHE_MGMT["Cache Management<br/>• CUEQ_TRITON_IGNORE_EXISTING_CACHE<br/>• Config persistence<br/>• Invalidation policies"]
    end
    
    subgraph "Execution Paths"
        TRITON_KERNELS["Triton CUDA Kernels<br/>• sigmoid_gated_dual_gemm<br/>• triangle_attention<br/>• tensor_product_uniform"]
        CUSTOM_KERNELS["Custom CUDA Kernels<br/>• indexed_linear<br/>• attention_pair_bias<br/>• triangle_multiplicative_update"]
        FALLBACK_PATH["Fallback Implementation<br/>• Pure JAX/PyTorch<br/>• CPU compatibility<br/>• Reference implementation"]
    end
    
    USER_CALL --> BACKEND_CHECK
    BACKEND_CHECK --> TUNING_MODE
    TUNING_MODE --> PRECISION_SELECT
    
    PRECISION_SELECT --> AOT_TUNING
    PRECISION_SELECT --> ONDEMAND_TUNING
    
    AOT_TUNING --> CACHE_MGMT
    ONDEMAND_TUNING --> CACHE_MGMT
    
    CACHE_MGMT --> TRITON_KERNELS
    CACHE_MGMT --> CUSTOM_KERNELS
    BACKEND_CHECK --> FALLBACK_PATH
```

Sources: [cuequivariance_jax/tests/sigmoid_gated_dual_gemm_test.py:430-477](), [cuequivariance_jax/tests/sigmoid_gated_dual_gemm_test.py:32-35]()

## Benchmarking Implementation Details

### JAX Benchmarking Architecture

The JAX benchmarking implementation uses sophisticated GPU event timing with clock rate calibration and adaptive measurement strategies.

| Component | Function | Purpose |
|-----------|----------|---------|
| `measure_clock_ticks` | Main benchmark function | Measures execution time in clock ticks |
| `run_bench` | JIT-compiled measurement | Core timing loop with warmup and iteration |
| `sleep` | CUDA sleep operation | Clock rate calibration and stream filling |
| `noop` | No-operation function | Prevents compiler optimizations |
| `_event_record` | GPU event recording | Precise timing measurement |
| `synchronize` | CPU-GPU synchronization | Lag detection and validation |

The measurement process implements multiple validation checks:

- **Clock Rate Consistency**: Validates that before/after clock rates match within 2% tolerance
- **Measurement Duration**: Ensures minimum 20μs total measurement time for accuracy
- **CPU-GPU Synchronization**: Detects and compensates for CPU lag behind GPU
- **Adaptive Iteration**: Automatically adjusts iteration count and warmup based on performance

```mermaid
graph LR
    subgraph "JAX Benchmarking Flow"
        INIT["measure_clock_ticks(f, *args, **kwargs)"]
        ADAPTIVE["Adaptive Loop<br/>• 20 attempts max<br/>• n_warm adjustment<br/>• n_iter scaling"]
        RUN_BENCH["run_bench(n_warm, n_iter, fill_time, state)"]
        VALIDATION["Validation Checks<br/>• Clock rate variation<br/>• Sync time threshold<br/>• Measurement duration"]
        RESULT["Return (avg_rate, avg_time)"]
    end
    
    subgraph "CUDA Operations"
        SLEEP_FILL["sleep(fill_time)"]
        WARMUP_LOOP["Warmup Iterations"]
        SLEEP_BEFORE["sleep(tick_time)"]
        MAIN_LOOP["Main Measurement Loop"]
        SLEEP_AFTER["sleep(tick_time)"]
        SYNC_CHECK["synchronize()"]
    end
    
    INIT --> ADAPTIVE
    ADAPTIVE --> RUN_BENCH
    RUN_BENCH --> SLEEP_FILL
    SLEEP_FILL --> WARMUP_LOOP
    WARMUP_LOOP --> SLEEP_BEFORE
    SLEEP_BEFORE --> MAIN_LOOP
    MAIN_LOOP --> SLEEP_AFTER
    SLEEP_AFTER --> SYNC_CHECK
    SYNC_CHECK --> VALIDATION
    VALIDATION --> ADAPTIVE
    VALIDATION --> RESULT
```

Sources: [cuequivariance_jax/cuequivariance_jax/benchmarking.py:62-98](), [cuequivariance_jax/cuequivariance_jax/benchmarking.py:108-182]()

### PyTorch Benchmarking Architecture

The PyTorch implementation provides similar functionality with framework-specific optimizations and event handling.

| Component | Implementation | Key Differences from JAX |
|-----------|----------------|-------------------------|
| Event Timing | `torch.cuda.Event(enable_timing=True)` | Direct PyTorch CUDA events |
| Synchronization | `torch.cuda.synchronize()` | Explicit CUDA synchronization |
| Clock Measurement | `sleep(tick_time, x)` | Tensor-based state passing |
| Time Calculation | `start_event.elapsed_time(end_event)` | Native PyTorch timing API |
| Device Handling | `torch.tensor(0, device="cuda")` | Explicit device placement |

The PyTorch benchmarking includes additional safeguards:

- **First Iteration Skip**: Always skips first iteration to allow JIT compilation
- **Increased Fill Time**: Uses longer base fill time (200μs vs 50μs) for stability
- **Stream Filling**: More aggressive stream filling to ensure proper GPU utilization

Sources: [cuequivariance_torch/cuequivariance_torch/benchmarking.py:45-146]()

## Performance Testing and Validation

### Triton Tuning Modes

The library supports multiple Triton tuning strategies controlled by the `CUEQ_TRITON_TUNING` environment variable:

| Mode | Description | Use Case |
|------|-------------|----------|
| `AOT` | Ahead-of-Time tuning | Production deployment with pre-optimized kernels |
| `ONDEMAND` | On-demand tuning | Development and dynamic workloads |
| `None` | Default behavior | Standard operation without explicit tuning |

Cache management is controlled by `CUEQ_TRITON_IGNORE_EXISTING_CACHE` for development and testing scenarios.

```mermaid
graph TD
    subgraph "Tuning Mode Selection"
        ENV_CHECK["Environment Variable Check<br/>CUEQ_TRITON_TUNING"]
        AOT_MODE["AOT Mode<br/>• Pre-compile all configs<br/>• Exhaustive search<br/>• Cache persistence"]
        ONDEMAND_MODE["On-Demand Mode<br/>• JIT optimization<br/>• Runtime adaptation<br/>• Dynamic caching"]
        DEFAULT_MODE["Default Mode<br/>• Standard behavior<br/>• Minimal overhead<br/>• Basic optimization"]
    end
    
    subgraph "Cache Management"
        CACHE_CHECK["Cache Policy Check<br/>CUEQ_TRITON_IGNORE_EXISTING_CACHE"]
        CACHE_HIT["Cache Hit<br/>• Load existing config<br/>• Skip optimization<br/>• Fast execution"]
        CACHE_MISS["Cache Miss<br/>• Run optimization<br/>• Store result<br/>• Update cache"]
        CACHE_IGNORE["Ignore Cache<br/>• Force re-optimization<br/>• Testing mode<br/>• Development"]
    end
    
    ENV_CHECK --> AOT_MODE
    ENV_CHECK --> ONDEMAND_MODE
    ENV_CHECK --> DEFAULT_MODE
    
    AOT_MODE --> CACHE_CHECK
    ONDEMAND_MODE --> CACHE_CHECK
    
    CACHE_CHECK --> CACHE_HIT
    CACHE_CHECK --> CACHE_MISS
    CACHE_CHECK --> CACHE_IGNORE
```

Sources: [cuequivariance_jax/tests/sigmoid_gated_dual_gemm_test.py:430-440](), [cuequivariance_jax/tests/sigmoid_gated_dual_gemm_test.py:33-35]()

### Precision Control

Performance is balanced with numerical accuracy through precision mode selection:

| Precision Mode | Matrix Operations | Use Case |
|----------------|------------------|----------|
| `Precision.DEFAULT` | Hardware default (typically TF32) | Balanced performance/accuracy |
| `Precision.TF32` | TensorFloat-32 format | High performance training |
| `Precision.IEEE` | IEEE 754 compliance | Maximum numerical precision |

The precision modes affect GEMM operations in CUDA kernels and can significantly impact performance characteristics.

Sources: [cuequivariance_jax/tests/sigmoid_gated_dual_gemm_test.py:398-427](), [cuequivariance_jax/tests/sigmoid_gated_dual_gemm_test.py:231-280]()

### Fallback and Compatibility

The library implements comprehensive fallback mechanisms for performance and compatibility:

- **CPU Execution**: Automatic fallback to CPU-based reference implementations
- **Dimension Compatibility**: Shape validation and automatic method selection
- **Device Placement**: Proper handling of CPU vs GPU tensor placement
- **Framework Compatibility**: Consistent behavior across JAX and PyTorch

Sources: [cuequivariance_jax/tests/sigmoid_gated_dual_gemm_test.py:536-590](), [cuequivariance_jax/tests/sigmoid_gated_dual_gemm_test.py:608-643]()

---

