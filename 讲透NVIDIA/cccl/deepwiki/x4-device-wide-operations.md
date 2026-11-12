<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/cccl · extra page Device-Wide Operations · fetched 2026-10-26 -->

# Device-Wide Operations

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [c/parallel/include/cccl/c/transform.h](c/parallel/include/cccl/c/transform.h)
- [c/parallel/src/for.cu](c/parallel/src/for.cu)
- [c/parallel/src/merge_sort.cu](c/parallel/src/merge_sort.cu)
- [c/parallel/src/radix_sort.cu](c/parallel/src/radix_sort.cu)
- [c/parallel/src/reduce.cu](c/parallel/src/reduce.cu)
- [c/parallel/src/scan.cu](c/parallel/src/scan.cu)
- [c/parallel/src/segmented_reduce.cu](c/parallel/src/segmented_reduce.cu)
- [c/parallel/src/segmented_sort.cu](c/parallel/src/segmented_sort.cu)
- [c/parallel/src/three_way_partition.cu](c/parallel/src/three_way_partition.cu)
- [c/parallel/src/transform.cu](c/parallel/src/transform.cu)
- [c/parallel/src/unique_by_key.cu](c/parallel/src/unique_by_key.cu)
- [cub/benchmarks/bench/radix_sort/keys.cu](cub/benchmarks/bench/radix_sort/keys.cu)
- [cub/benchmarks/bench/radix_sort/pairs.cu](cub/benchmarks/bench/radix_sort/pairs.cu)
- [cub/benchmarks/bench/radix_sort/policy_selector.h](cub/benchmarks/bench/radix_sort/policy_selector.h)
- [cub/benchmarks/bench/reduce/base.cuh](cub/benchmarks/bench/reduce/base.cuh)
- [cub/benchmarks/bench/reduce/deterministic.cu](cub/benchmarks/bench/reduce/deterministic.cu)
- [cub/benchmarks/bench/reduce/nondeterministic.cu](cub/benchmarks/bench/reduce/nondeterministic.cu)
- [cub/benchmarks/bench/transform/babelstream.cu](cub/benchmarks/bench/transform/babelstream.cu)
- [cub/benchmarks/bench/transform/common.h](cub/benchmarks/bench/transform/common.h)
- [cub/benchmarks/bench/transform/complex_cmp.cu](cub/benchmarks/bench/transform/complex_cmp.cu)
- [cub/benchmarks/bench/transform/fib.cu](cub/benchmarks/bench/transform/fib.cu)
- [cub/benchmarks/bench/transform/fill.cu](cub/benchmarks/bench/transform/fill.cu)
- [cub/benchmarks/bench/transform/grayscale.cu](cub/benchmarks/bench/transform/grayscale.cu)
- [cub/benchmarks/bench/transform/heavy.cu](cub/benchmarks/bench/transform/heavy.cu)
- [cub/benchmarks/bench/transform_reduce/sum.cu](cub/benchmarks/bench/transform_reduce/sum.cu)
- [cub/cub/agent/agent_radix_sort_downsweep.cuh](cub/cub/agent/agent_radix_sort_downsweep.cuh)
- [cub/cub/agent/agent_radix_sort_histogram.cuh](cub/cub/agent/agent_radix_sort_histogram.cuh)
- [cub/cub/agent/agent_radix_sort_onesweep.cuh](cub/cub/agent/agent_radix_sort_onesweep.cuh)
- [cub/cub/agent/agent_radix_sort_upsweep.cuh](cub/cub/agent/agent_radix_sort_upsweep.cuh)
- [cub/cub/agent/agent_reduce.cuh](cub/cub/agent/agent_reduce.cuh)
- [cub/cub/agent/agent_reduce_by_key.cuh](cub/cub/agent/agent_reduce_by_key.cuh)
- [cub/cub/agent/agent_rle.cuh](cub/cub/agent/agent_rle.cuh)
- [cub/cub/agent/agent_scan.cuh](cub/cub/agent/agent_scan.cuh)
- [cub/cub/agent/agent_scan_by_key.cuh](cub/cub/agent/agent_scan_by_key.cuh)
- [cub/cub/agent/agent_segmented_radix_sort.cuh](cub/cub/agent/agent_segmented_radix_sort.cuh)
- [cub/cub/agent/agent_select_if.cuh](cub/cub/agent/agent_select_if.cuh)
- [cub/cub/agent/agent_three_way_partition.cuh](cub/cub/agent/agent_three_way_partition.cuh)
- [cub/cub/agent/agent_unique_by_key.cuh](cub/cub/agent/agent_unique_by_key.cuh)
- [cub/cub/agent/single_pass_scan_operators.cuh](cub/cub/agent/single_pass_scan_operators.cuh)
- [cub/cub/detail/arch_dispatch.cuh](cub/cub/detail/arch_dispatch.cuh)
- [cub/cub/detail/launcher/cuda_driver.cuh](cub/cub/detail/launcher/cuda_driver.cuh)
- [cub/cub/detail/launcher/cuda_runtime.cuh](cub/cub/detail/launcher/cuda_runtime.cuh)
- [cub/cub/detail/rfa.cuh](cub/cub/detail/rfa.cuh)
- [cub/cub/device/device_adjacent_difference.cuh](cub/cub/device/device_adjacent_difference.cuh)
- [cub/cub/device/device_histogram.cuh](cub/cub/device/device_histogram.cuh)
- [cub/cub/device/device_partition.cuh](cub/cub/device/device_partition.cuh)
- [cub/cub/device/device_radix_sort.cuh](cub/cub/device/device_radix_sort.cuh)
- [cub/cub/device/device_reduce.cuh](cub/cub/device/device_reduce.cuh)
- [cub/cub/device/device_segmented_radix_sort.cuh](cub/cub/device/device_segmented_radix_sort.cuh)
- [cub/cub/device/device_segmented_reduce.cuh](cub/cub/device/device_segmented_reduce.cuh)
- [cub/cub/device/device_segmented_sort.cuh](cub/cub/device/device_segmented_sort.cuh)
- [cub/cub/device/device_select.cuh](cub/cub/device/device_select.cuh)
- [cub/cub/device/dispatch/dispatch_adjacent_difference.cuh](cub/cub/device/dispatch/dispatch_adjacent_difference.cuh)
- [cub/cub/device/dispatch/dispatch_common.cuh](cub/cub/device/dispatch/dispatch_common.cuh)
- [cub/cub/device/dispatch/dispatch_fixed_size_segmented_reduce.cuh](cub/cub/device/dispatch/dispatch_fixed_size_segmented_reduce.cuh)
- [cub/cub/device/dispatch/dispatch_histogram.cuh](cub/cub/device/dispatch/dispatch_histogram.cuh)
- [cub/cub/device/dispatch/dispatch_merge_sort.cuh](cub/cub/device/dispatch/dispatch_merge_sort.cuh)
- [cub/cub/device/dispatch/dispatch_radix_sort.cuh](cub/cub/device/dispatch/dispatch_radix_sort.cuh)
- [cub/cub/device/dispatch/dispatch_reduce.cuh](cub/cub/device/dispatch/dispatch_reduce.cuh)
- [cub/cub/device/dispatch/dispatch_reduce_by_key.cuh](cub/cub/device/dispatch/dispatch_reduce_by_key.cuh)
- [cub/cub/device/dispatch/dispatch_reduce_deterministic.cuh](cub/cub/device/dispatch/dispatch_reduce_deterministic.cuh)
- [cub/cub/device/dispatch/dispatch_reduce_nondeterministic.cuh](cub/cub/device/dispatch/dispatch_reduce_nondeterministic.cuh)
- [cub/cub/device/dispatch/dispatch_rle.cuh](cub/cub/device/dispatch/dispatch_rle.cuh)
- [cub/cub/device/dispatch/dispatch_scan.cuh](cub/cub/device/dispatch/dispatch_scan.cuh)
- [cub/cub/device/dispatch/dispatch_scan_by_key.cuh](cub/cub/device/dispatch/dispatch_scan_by_key.cuh)
- [cub/cub/device/dispatch/dispatch_segmented_radix_sort.cuh](cub/cub/device/dispatch/dispatch_segmented_radix_sort.cuh)
- [cub/cub/device/dispatch/dispatch_segmented_reduce.cuh](cub/cub/device/dispatch/dispatch_segmented_reduce.cuh)
- [cub/cub/device/dispatch/dispatch_segmented_sort.cuh](cub/cub/device/dispatch/dispatch_segmented_sort.cuh)
- [cub/cub/device/dispatch/dispatch_select_if.cuh](cub/cub/device/dispatch/dispatch_select_if.cuh)
- [cub/cub/device/dispatch/dispatch_streaming_reduce.cuh](cub/cub/device/dispatch/dispatch_streaming_reduce.cuh)
- [cub/cub/device/dispatch/dispatch_three_way_partition.cuh](cub/cub/device/dispatch/dispatch_three_way_partition.cuh)
- [cub/cub/device/dispatch/dispatch_transform.cuh](cub/cub/device/dispatch/dispatch_transform.cuh)
- [cub/cub/device/dispatch/dispatch_unique_by_key.cuh](cub/cub/device/dispatch/dispatch_unique_by_key.cuh)
- [cub/cub/device/dispatch/kernels/kernel_radix_sort.cuh](cub/cub/device/dispatch/kernels/kernel_radix_sort.cuh)
- [cub/cub/device/dispatch/kernels/kernel_reduce.cuh](cub/cub/device/dispatch/kernels/kernel_reduce.cuh)
- [cub/cub/device/dispatch/kernels/kernel_scan.cuh](cub/cub/device/dispatch/kernels/kernel_scan.cuh)
- [cub/cub/device/dispatch/kernels/kernel_segmented_radix_sort.cuh](cub/cub/device/dispatch/kernels/kernel_segmented_radix_sort.cuh)
- [cub/cub/device/dispatch/kernels/kernel_segmented_reduce.cuh](cub/cub/device/dispatch/kernels/kernel_segmented_reduce.cuh)
- [cub/cub/device/dispatch/kernels/kernel_transform.cuh](cub/cub/device/dispatch/kernels/kernel_transform.cuh)
- [cub/cub/device/dispatch/tuning/common.cuh](cub/cub/device/dispatch/tuning/common.cuh)
- [cub/cub/device/dispatch/tuning/tuning_adjacent_difference.cuh](cub/cub/device/dispatch/tuning/tuning_adjacent_difference.cuh)
- [cub/cub/device/dispatch/tuning/tuning_batch_memcpy.cuh](cub/cub/device/dispatch/tuning/tuning_batch_memcpy.cuh)
- [cub/cub/device/dispatch/tuning/tuning_for.cuh](cub/cub/device/dispatch/tuning/tuning_for.cuh)
- [cub/cub/device/dispatch/tuning/tuning_merge_sort.cuh](cub/cub/device/dispatch/tuning/tuning_merge_sort.cuh)
- [cub/cub/device/dispatch/tuning/tuning_radix_sort.cuh](cub/cub/device/dispatch/tuning/tuning_radix_sort.cuh)
- [cub/cub/device/dispatch/tuning/tuning_reduce.cuh](cub/cub/device/dispatch/tuning/tuning_reduce.cuh)
- [cub/cub/device/dispatch/tuning/tuning_run_length_encode.cuh](cub/cub/device/dispatch/tuning/tuning_run_length_encode.cuh)
- [cub/cub/device/dispatch/tuning/tuning_scan.cuh](cub/cub/device/dispatch/tuning/tuning_scan.cuh)
- [cub/cub/device/dispatch/tuning/tuning_scan_by_key.cuh](cub/cub/device/dispatch/tuning/tuning_scan_by_key.cuh)
- [cub/cub/device/dispatch/tuning/tuning_segmented_sort.cuh](cub/cub/device/dispatch/tuning/tuning_segmented_sort.cuh)
- [cub/cub/device/dispatch/tuning/tuning_select_if.cuh](cub/cub/device/dispatch/tuning/tuning_select_if.cuh)
- [cub/cub/device/dispatch/tuning/tuning_three_way_partition.cuh](cub/cub/device/dispatch/tuning/tuning_three_way_partition.cuh)
- [cub/cub/device/dispatch/tuning/tuning_transform.cuh](cub/cub/device/dispatch/tuning/tuning_transform.cuh)
- [cub/cub/device/dispatch/tuning/tuning_unique_by_key.cuh](cub/cub/device/dispatch/tuning/tuning_unique_by_key.cuh)
- [cub/cub/grid/grid_even_share.cuh](cub/cub/grid/grid_even_share.cuh)
- [cub/cub/util_device.cuh](cub/cub/util_device.cuh)
- [cub/test/catch2_test_arch_dispatch.cu](cub/test/catch2_test_arch_dispatch.cu)
- [cub/test/catch2_test_device_radix_sort_custom_policy_hub.cu](cub/test/catch2_test_device_radix_sort_custom_policy_hub.cu)
- [cub/test/catch2_test_device_reduce_deterministic.cu](cub/test/catch2_test_device_reduce_deterministic.cu)
- [cub/test/catch2_test_device_reduce_env.cu](cub/test/catch2_test_device_reduce_env.cu)
- [cub/test/catch2_test_device_reduce_env_api.cu](cub/test/catch2_test_device_reduce_env_api.cu)
- [cub/test/catch2_test_device_reduce_nondeterministic.cu](cub/test/catch2_test_device_reduce_nondeterministic.cu)
- [cub/test/catch2_test_device_segmented_reduce_large_offsets.cu](cub/test/catch2_test_device_segmented_reduce_large_offsets.cu)
- [cub/test/catch2_test_device_transform.cu](cub/test/catch2_test_device_transform.cu)
- [cub/test/catch2_test_grid_even_share.cu](cub/test/catch2_test_grid_even_share.cu)
- [cub/test/catch2_test_launch_helper.h](cub/test/catch2_test_launch_helper.h)
- [cub/test/test_device_reduce_env_fail.cu](cub/test/test_device_reduce_env_fail.cu)
- [cub/test/test_device_reduce_unsupported_env_fail.cu](cub/test/test_device_reduce_unsupported_env_fail.cu)
- [thrust/testing/cuda/unique.cu](thrust/testing/cuda/unique.cu)
- [thrust/thrust/type_traits/unwrap_contiguous_iterator.h](thrust/thrust/type_traits/unwrap_contiguous_iterator.h)

</details>



## Purpose and Scope

Device-Wide Operations are CUB's high-level algorithms that operate on entire sequences of data residing in device-accessible memory. These operations provide optimized implementations of common parallel primitives such as reductions, scans, selections, sorts, and transformations. This document covers the architecture, dispatch mechanisms, and implementation patterns shared across all device-wide operations.

For low-level building blocks to construct custom kernels, see [Block-Level Primitives](#2.2.2). For policy selection and tuning mechanisms, see [Dispatch and Policy System](#5.2).

**Sources:** [cub/cub/device/dispatch/dispatch_reduce.cuh:1-546](), [cub/cub/device/dispatch/dispatch_transform.cuh:1-569](), [cub/cub/device/dispatch/dispatch_scan.cuh:1-400]()

## Available Operations

CUB provides the following categories of device-wide operations:

| Operation Category | Primary API | Key Dispatch Classes | Description |
|-------------------|------------|---------------------|-------------|
| **Reduce** | `cub::DeviceReduce` | `DispatchReduce`, `detail::reduce::dispatch` | Compute aggregates (sum, min, max, custom operators) across sequences |
| **Transform** | `cub::DeviceTransform` | `detail::transform::dispatch` | Apply element-wise operations with vectorized/async memory access |
| **Scan** | `cub::DeviceScan` | `DispatchScan` | Compute prefix sums (inclusive/exclusive) with inter-block coordination |
| **Select** | `cub::DeviceSelect` | `DispatchSelectIf`, `DispatchUniqueByKey` | Filter elements based on predicates or uniqueness |
| **Histogram** | `cub::DeviceHistogram` | `DispatchHistogram`, `detail::histogram::dispatch_histogram` | Compute frequency distributions with privatized binning |
| **Sort** | `cub::DeviceRadixSort`, `cub::DeviceMergeSort` | `DispatchRadixSort`, `detail::merge_sort::dispatch_t` | Sort keys and key-value pairs using radix or merge algorithms |
| **Segmented Reduce** | `cub::DeviceSegmentedReduce` | `detail::segmented_reduce::dispatch`, `DispatchFixedSizeSegmentedReduce` | Reduce multiple independent segments in parallel |

**Sources:** [cub/cub/device/device_reduce.cuh:122-508](), [cub/cub/device/dispatch/dispatch_reduce.cuh:47-847](), [cub/cub/device/dispatch/dispatch_transform.cuh:58-594](), [cub/cub/device/dispatch/dispatch_scan.cuh:86-400](), [cub/cub/device/dispatch/dispatch_select_if.cuh:47-850](), [cub/cub/device/dispatch/dispatch_histogram.cuh:54-404](), [cub/cub/device/dispatch/dispatch_radix_sort.cuh:52-850](), [cub/cub/device/device_segmented_reduce.cuh:79-944]()

## Architectural Overview

### Dispatch Layer Pattern

All device-wide operations follow a common four-layer architectural pattern:

```mermaid
graph TB
    subgraph "Layer 1: User API"
        API["DeviceReduce::Sum()<br/>DeviceTransform::Transform()<br/>DeviceScan::ExclusiveSum()"]
    end
    
    subgraph "Layer 2: Dispatch Layer"
        DISPATCH["DispatchReduce<br/>dispatch_t (Transform)<br/>DispatchScan"]
        DISPATCH_METHODS["Dispatch()<br/>Invoke()<br/>InvokePasses()"]
    end
    
    subgraph "Layer 3: Policy Selection"
        POLICY_HUB["policy_hub<AccumT, OffsetT>"]
        CHAINED["ChainedPolicy<br/>PTX Version Matching"]
        TUNING["sm80_tuning<br/>sm90_tuning<br/>sm100_tuning"]
    end
    
    subgraph "Layer 4: Kernel Execution"
        KERNELS["DeviceReduceKernel<br/>transform_kernel_*<br/>DeviceScanKernel"]
        AGENTS["AgentReduce<br/>transform logic<br/>AgentScan"]
    end
    
    API --> DISPATCH
    DISPATCH --> DISPATCH_METHODS
    DISPATCH_METHODS --> POLICY_HUB
    POLICY_HUB --> CHAINED
    CHAINED --> TUNING
    TUNING --> KERNELS
    KERNELS --> AGENTS
    
    style API fill:#f9f9f9
    style DISPATCH fill:#e8e8e8
    style POLICY_HUB fill:#d8d8d8
    style KERNELS fill:#c8c8c8
```

**Dispatch Layer Pattern Overview**

The dispatch layer orchestrates the entire execution flow from user API to kernel launch.

**Sources:** [cub/cub/device/dispatch/dispatch_reduce.cuh:139-158](), [cub/cub/device/dispatch/dispatch_transform.cuh:158-191](), [cub/cub/util_device.cuh:726-795]()

### Common Dispatch Components

```mermaid
graph TB
    subgraph TempStorage["Temporary Storage Management"]
        TEMP_CALC["detail::alias_temporaries()<br/>Computes offsets and sizes"]
        VSMEM["vsmem_t helper<br/>Virtual memory allocation"]
    end
    
    subgraph DeviceQueries["Device Queries (util_device.cuh)"]
        PTX_VER["PtxVersion(int& ptx_version)<br/>Returns PTX arch * 10"]
        SM_VER["SmVersion(int& sm_version)<br/>Returns compute capability * 10"]
        SM_COUNT["MultiProcessorCount()<br/>Via launcher_factory"]
        PTX_ARCH_ID["detail::ptx_arch_id(cuda::arch_id&)<br/>Returns cuda::arch_id"]
    end
    
    subgraph KernelConfig["Kernel Configuration"]
        KERNEL_STRUCT["detail::KernelConfig struct<br/>block_threads, items_per_thread<br/>tile_size, sm_occupancy"]
        MAX_OCC["MaxSmOccupancy(kernel_ptr)<br/>cudaOccupancyMaxActiveBlocks"]
        GRID_CALC["ceil_div(num_items, tile_size)<br/>Grid dimension calculation"]
    end
    
    subgraph PolicySel["Policy Selection"]
        DISPATCH_ARCH["detail::dispatch_arch()<br/>Invokes policy_selector(arch_id)"]
        LEGACY_INVOKE["ChainedPolicy::Invoke()<br/>Legacy PTX version matching"]
    end
    
    TEMP_CALC --> VSMEM
    PTX_VER --> LEGACY_INVOKE
    PTX_ARCH_ID --> DISPATCH_ARCH
    SM_VER --> KERNEL_STRUCT
    SM_COUNT --> GRID_CALC
    MAX_OCC --> KERNEL_STRUCT
    DISPATCH_ARCH --> KERNEL_STRUCT
    LEGACY_INVOKE --> KERNEL_STRUCT
```

**Common Components Shared by All Dispatch Layers**

Every dispatch implementation uses these utilities for device queries, memory allocation, configuration, and policy selection.

**Sources:** [cub/cub/util_device.cuh:276-461](), [cub/cub/util_device.cuh:592-598](), [cub/cub/util_device.cuh:728-761](), [cub/cub/util_temporary_storage.cuh:1-200](), [cub/cub/device/dispatch/dispatch_common.cuh:1-100](), [cub/cub/device/dispatch/dispatch_reduce.cuh:334-353]()

## Device Reduce Architecture

### Reduce Dispatch Flow

The `DispatchReduce` class manages two execution strategies: single-tile for small problems and two-pass for large problems.

```mermaid
graph TB
    DISPATCH_ENTRY["DispatchReduce::Dispatch()"]
    PTX_CHECK["Query PTX Version<br/>PtxVersion()"]
    CREATE_DISPATCH["Create DispatchReduce<br/>Instance"]
    CHAINED_INVOKE["ChainedPolicy::Invoke()"]
    
    INVOKE_DECIDE{"num_items <= tile_size?"}
    SINGLE_TILE["InvokeSingleTile()<br/>DeviceReduceSingleTileKernel"]
    TWO_PASS["InvokePasses()"]
    
    PASS1["Pass 1: DeviceReduceKernel<br/>Block-level reductions<br/>Store to d_block_reductions"]
    PASS2["Pass 2: DeviceReduceSingleTileKernel<br/>Reduce block results<br/>Apply init value"]
    
    DISPATCH_ENTRY --> PTX_CHECK
    PTX_CHECK --> CREATE_DISPATCH
    CREATE_DISPATCH --> CHAINED_INVOKE
    CHAINED_INVOKE --> INVOKE_DECIDE
    INVOKE_DECIDE -->|Yes| SINGLE_TILE
    INVOKE_DECIDE -->|No| TWO_PASS
    TWO_PASS --> PASS1
    PASS1 --> PASS2
```

**DeviceReduce Execution Path**

The dispatch layer chooses between single-tile and two-pass strategies based on problem size.

**Sources:** [cub/cub/device/dispatch/dispatch_reduce.cuh:439-454](), [cub/cub/device/dispatch/dispatch_reduce.cuh:246-290](), [cub/cub/device/dispatch/dispatch_reduce.cuh:314-432]()

### Reduce Kernel Source Structure

```mermaid
graph TB
    KERNEL_SOURCE["detail::reduce::DeviceReduceKernelSource<br/>Template params: PolicySelector,<br/>InputIteratorT, OutputIteratorT,<br/>OffsetT, ReductionOpT, InitT, AccumT, TransformOpT"]
    
    SINGLE_TILE_K["CUB_DEFINE_KERNEL_GETTER(SingleTileKernel)<br/>DeviceReduceSingleTileKernel<PolicySelector, ...>"]
    REDUCTION_K["CUB_DEFINE_KERNEL_GETTER(ReductionKernel)<br/>DeviceReduceKernel<PolicySelector, ...>"]
    SECOND_K["CUB_DEFINE_KERNEL_GETTER(SingleTileSecondKernel)<br/>DeviceReduceSingleTileKernel<AccumT*, ...>"]
    
    ACCUM_SIZE["static constexpr size_t AccumSize()<br/>returns sizeof(AccumT)"]
    
    KERNEL_SOURCE --> SINGLE_TILE_K
    KERNEL_SOURCE --> REDUCTION_K
    KERNEL_SOURCE --> SECOND_K
    KERNEL_SOURCE --> ACCUM_SIZE
    
    SINGLE_TILE_K -.->|"Instantiates"| AGENT_REDUCE["AgentReduce<policy.Reduce(),<br/>InputIteratorT, AccumT*, OffsetT,<br/>ReductionOpT, AccumT>"]
    REDUCTION_K -.->|"Instantiates"| AGENT_REDUCE
```

**detail::reduce::DeviceReduceKernelSource Structure**

The kernel source abstraction uses `CUB_DEFINE_KERNEL_GETTER` macros to provide typed access to kernel function pointers. Each getter returns a `CUkernel` (for C API) or function pointer.

**Sources:** [cub/cub/device/dispatch/dispatch_reduce.cuh:57-90](), [cub/cub/device/dispatch/kernels/kernel_reduce.cuh:149-272](), [cub/cub/agent/agent_reduce.cuh:116-468](), [c/parallel/src/reduce.cu:141-169]()

### Two-Pass Reduction Strategy

The two-pass approach enables efficient reduction of arbitrarily large datasets:

| Component | Purpose | Storage Location |
|-----------|---------|------------------|
| **Pass 1 Kernel** | Each block reduces its tile to a single value | Temporary device memory array |
| **Block Reductions Array** | Holds one reduced value per block | `d_block_reductions` (size: `max_blocks * sizeof(AccumT)`) |
| **Pass 2 Kernel** | Single block reduces all block results | Final output `d_out` |
| **Initial Value** | Applied only in Pass 2 | Incorporated during final reduction |

**Sources:** [cub/cub/device/dispatch/dispatch_reduce.cuh:314-432](), [cub/cub/device/dispatch/kernels/reduce.cuh:111-272]()

## Device Transform Architecture

### Transform Algorithm Selection

The `detail::transform::dispatch()` implementation employs multiple specialized kernel variants selected at runtime:

```mermaid
graph TB
    DISPATCH_ENTRY["detail::transform::dispatch()<br/>Called with tuple of input iterators"]
    
    PTX_QUERY["launcher_factory.PtxArchId(arch_id)<br/>Query GPU architecture"]
    
    DISPATCH_ARCH["detail::dispatch_arch(policy_selector, arch_id)<br/>Invoke policy functor with arch_id"]
    
    POLICY_RESULT["policy_selector(arch_id)<br/>Returns transform_policy struct"]
    
    CHECK_ALG{"active_policy.algorithm?"}
    
    UBLKCP["Algorithm::ublkcp<br/>Selected on SM90+ (Hopper/Blackwell)<br/>Requires aligned base pointers"]
    MEMCPY_ASYNC["Algorithm::memcpy_async<br/>Selected on SM80+ (Ampere)<br/>Requires contiguous trivially relocatable types"]
    VECTORIZED["Algorithm::vectorized<br/>Selected when power-of-two sizes<br/>and alignment conditions met"]
    PREFETCH["Algorithm::prefetch<br/>Fallback for all other cases<br/>Software prefetch loops"]
    
    UBLKCP_INVOKE["invoke_async_algorithm()<br/>bulk_copy_alignment(arch_id)<br/>bulk_copy_dyn_smem_for_tile_size()"]
    ASYNC_INVOKE["invoke_async_algorithm()<br/>ldgsts_size_and_align = 16<br/>memcpy_async_dyn_smem_for_tile_size()"]
    VEC_INVOKE["invoke_prefetch_or_vectorized_algorithm()<br/>CanVectorize(vec_size, out, in...)<br/>Runtime alignment check"]
    PREF_INVOKE["invoke_prefetch_or_vectorized_algorithm()<br/>spread_out_items_per_thread()<br/>Optimize for occupancy"]
    
    TRANSFORM_KERNEL["transform_kernel<PolicySelector, Offset,<br/>Predicate, TransformOp,<br/>RandomAccessIteratorOut,<br/>RandomAccessIteratorsIn...>"]
    
    DISPATCH_ENTRY --> PTX_QUERY
    PTX_QUERY --> DISPATCH_ARCH
    DISPATCH_ARCH --> POLICY_RESULT
    POLICY_RESULT --> CHECK_ALG
    
    CHECK_ALG -->|"ublkcp"| UBLKCP
    CHECK_ALG -->|"memcpy_async"| MEMCPY_ASYNC
    CHECK_ALG -->|"vectorized"| VECTORIZED
    CHECK_ALG -->|"prefetch"| PREFETCH
    
    UBLKCP --> UBLKCP_INVOKE
    MEMCPY_ASYNC --> ASYNC_INVOKE
    VECTORIZED --> VEC_INVOKE
    PREFETCH --> PREF_INVOKE
    
    UBLKCP_INVOKE --> TRANSFORM_KERNEL
    ASYNC_INVOKE --> TRANSFORM_KERNEL
    VEC_INVOKE --> TRANSFORM_KERNEL
    PREF_INVOKE --> TRANSFORM_KERNEL
```

**detail::transform::dispatch() Algorithm Selection**

A single parameterized `transform_kernel` is used with different algorithm paths selected via runtime `if constexpr` branches based on the `active_policy.algorithm` enum.

**Sources:** [cub/cub/device/dispatch/dispatch_transform.cuh:547-593](), [cub/cub/device/dispatch/dispatch_transform.cuh:459-525](), [cub/cub/device/dispatch/tuning/tuning_transform.cuh:58-66](), [cub/cub/device/dispatch/tuning/tuning_transform.cuh:325-458](), [cub/cub/device/dispatch/kernels/kernel_transform.cuh:205-900]()

### Transform Algorithm Code Paths

The single `transform_kernel` template contains four algorithm code paths selected at runtime via `if constexpr`:

| Algorithm Path | Hardware Requirement | Memory Access Pattern | Key Implementation Details |
|---------------|---------------------|----------------------|---------------------------|
| **Algorithm::ublkcp** | SM90+ (Hopper/Blackwell) | `cp.async.bulk.global.shared::cta.bulk_group` | Alignment: 128B (Hopper) or 16B (Blackwell)<br/>Uses `cuda::device::barrier_arrive_tx()`<br/>Shared memory staging with padding |
| **Algorithm::memcpy_async** | SM80+ (Ampere) | `cp.async.cg.shared.global [addr]` | Alignment: 16B (`ldgsts_size_and_align`)<br/>Uses `cuda::pipeline` for async copies<br/>Shared memory with head/tail scalar copies |
| **Algorithm::vectorized** | Any architecture | Vectorized loads via `cub::ThreadLoad<LOAD_DEFAULT, VecT>` | Power-of-two type sizes required<br/>Runtime alignment check via `CanVectorize()`<br/>Direct register-to-register computation |
| **Algorithm::prefetch** | Any architecture | Scalar loads with manual prefetch | No alignment requirements<br/>Handles fancy iterators and arbitrary types<br/>Prefetch next tile while computing current |

**Sources:** [cub/cub/device/dispatch/kernels/kernel_transform.cuh:205-900](), [cub/cub/device/dispatch/tuning/tuning_transform.cuh:58-86](), [cub/cub/device/dispatch/dispatch_transform.cuh:290-322](), [cub/cub/device/dispatch/dispatch_transform.cuh:472-509]()

### Transform Configuration Flow

```mermaid
graph TB
    CONFIG_START["configure_async_kernel<NoInputs>()<br/>Template param: NoInputs = (sizeof...(Iterators) == 0)"]
    
    POLICY_GETTER["policy_getter() returns transform_policy<br/>Contains async_copy.min_items_per_thread,<br/>async_copy.max_items_per_thread,<br/>min_bytes_in_flight"]
    
    LOOP_START["Loop: items_per_thread from<br/>min_items_per_thread to max_items_per_thread"]
    
    TILE_SIZE["tile_size = block_threads * items_per_thread"]
    
    SMEM_CALC["dyn_smem_for_tile_size(tile_size, alignment)<br/>Returns required shared memory bytes"]
    
    OCCUPANCY["launcher_factory.MaxSmOccupancy()<br/>Returns max_occupancy for this tile_size"]
    
    CHECK_ZERO{"max_occupancy == 0?"}
    
    BIF_CALC["bytes_in_flight_SM =<br/>max_occupancy * tile_size * LoadedBytesPerIteration()"]
    
    CHECK_BIF{"bytes_in_flight_SM >= min_bytes_in_flight?"}
    
    CACHE["kernel_source.CacheAsyncConfiguration()<br/>Static cache on host, recompute on device"]
    
    SPREAD["spread_out_items_per_thread(num_items, policy,<br/>items_per_thread, sm_count, max_occupancy)<br/>Clamp to ensure full occupancy for small inputs"]
    
    GRID_DIM["grid_dim = ceil_div(num_items, final_tile_size)"]
    
    RETURN["Return tuple(launcher, kernel, items_per_thread)"]
    
    CONFIG_START --> POLICY_GETTER
    POLICY_GETTER --> LOOP_START
    LOOP_START --> TILE_SIZE
    TILE_SIZE --> SMEM_CALC
    SMEM_CALC --> OCCUPANCY
    OCCUPANCY --> CHECK_ZERO
    CHECK_ZERO -->|"Yes"| CACHE
    CHECK_ZERO -->|"No"| BIF_CALC
    BIF_CALC --> CHECK_BIF
    CHECK_BIF -->|"Yes"| CACHE
    CHECK_BIF -->|"No"| LOOP_START
    CACHE --> SPREAD
    SPREAD --> GRID_DIM
    GRID_DIM --> RETURN
```

**configure_async_kernel() Runtime Configuration**

The async copy algorithms (ublkcp and memcpy_async) iterate to find the optimal `items_per_thread` that saturates memory bandwidth while fitting in shared memory and registers.

**Sources:** [cub/cub/device/dispatch/dispatch_transform.cuh:192-278](), [cub/cub/device/dispatch/dispatch_transform.cuh:174-184](), [cub/cub/device/dispatch/tuning/tuning_transform.cuh:222-270]()

### Transform Memory Alignment Handling

The async copy kernels (`ublkcp` and `ldgsts`) require careful alignment management:

```mermaid
graph LR
    subgraph "Input Buffer"
        ORIG_PTR["Original Pointer"]
        ALIGNED_BASE["Aligned Base Pointer<br/>round_down_ptr()"]
        HEAD_PAD["Head Padding<br/>0-15 or 0-127 bytes"]
    end
    
    subgraph "Shared Memory"
        SMEM_BASE["Shared Memory Base<br/>16-byte aligned"]
        SMEM_HEAD["Head Padding Space"]
        SMEM_DATA["Actual Data"]
        SMEM_TAIL["Tail Padding Space"]
    end
    
    subgraph "Copy Operation"
        ALIGNED_COPY["Aligned Bulk Copy<br/>cp.async.bulk or cp.async.cg"]
        SCALAR_HEAD["Scalar Head Copy<br/>threadIdx.x < head_bytes"]
        SCALAR_TAIL["Scalar Tail Copy<br/>threadIdx.x < tail_bytes"]
    end
    
    ALIGNED_BASE --> HEAD_PAD
    HEAD_PAD --> ORIG_PTR
    
    SMEM_BASE --> SMEM_HEAD
    SMEM_HEAD --> SMEM_DATA
    SMEM_DATA --> SMEM_TAIL
    
    SCALAR_HEAD --> SMEM_HEAD
    ALIGNED_COPY --> SMEM_DATA
    SCALAR_TAIL --> SMEM_TAIL
```

**Transform Alignment Strategy**

Head and tail padding enable aligned bulk copies while preserving correctness.

**Sources:** [cub/cub/device/dispatch/kernels/transform.cuh:333-393](), [cub/cub/device/dispatch/kernels/transform.cuh:623-688](), [cub/cub/device/dispatch/kernels/transform.cuh:61-66]()

## Device Scan Architecture

### Scan Tile State Coordination

Scans require inter-block coordination through a tile state mechanism:

```mermaid
graph TB
    subgraph "Block 0"
        B0_LOAD["Load Tile 0"]
        B0_SCAN["BlockScan"]
        B0_WRITE["Write to TileState[0]<br/>INCLUSIVE flag"]
        B0_OUT["Output Tile 0"]
    end
    
    subgraph "Block 1"
        B1_LOAD["Load Tile 1"]
        B1_SCAN["BlockScan"]
        B1_WAIT["Wait for TileState[0]<br/>Spin on flag"]
        B1_COMBINE["Combine with prefix"]
        B1_WRITE["Write to TileState[1]"]
        B1_OUT["Output Tile 1"]
    end
    
    subgraph "Block 2"
        B2_LOAD["Load Tile 2"]
        B2_SCAN["BlockScan"]
        B2_WAIT["Wait for TileState[1]"]
        B2_COMBINE["Combine with prefix"]
        B2_OUT["Output Tile 2"]
    end
    
    subgraph "Device Memory"
        TILE_STATE["ScanTileState Array<br/>Tile descriptors + aggregates"]
    end
    
    B0_SCAN --> B0_WRITE
    B0_WRITE --> TILE_STATE
    B0_SCAN --> B0_OUT
    
    B1_SCAN --> B1_WAIT
    TILE_STATE --> B1_WAIT
    B1_WAIT --> B1_COMBINE
    B1_COMBINE --> B1_WRITE
    B1_WRITE --> TILE_STATE
    B1_COMBINE --> B1_OUT
    
    B2_SCAN --> B2_WAIT
    TILE_STATE --> B2_WAIT
    B2_WAIT --> B2_COMBINE
    B2_COMBINE --> B2_OUT
```

**Scan Lookback Pattern**

Blocks use the lookback pattern to incorporate prefix aggregates from earlier tiles.

**Sources:** [cub/cub/agent/agent_scan.cuh:200-450](), [cub/cub/agent/single_pass_scan_operators.cuh:1-300](), [cub/cub/device/dispatch/dispatch_scan.cuh:200-350]()

### Scan Kernel Invocation

```mermaid
graph TB
    DISPATCH_SCAN["DispatchScan::Dispatch()"]
    
    INIT_TILE_STATE["Initialize ScanTileState<br/>DeviceScanInitKernel"]
    
    CONFIG["Calculate grid dimensions<br/>tiles = ceil(num_items / tile_size)"]
    
    SCAN_KERNEL["Launch DeviceScanKernel<br/>grid_size blocks"]
    
    AGENT_WORK["Each block:<br/>AgentScan::ConsumeRange()"]
    
    LOOKBACK["LookbackPrefixCallbackOp<br/>Determine block prefix"]
    
    DISPATCH_SCAN --> INIT_TILE_STATE
    INIT_TILE_STATE --> CONFIG
    CONFIG --> SCAN_KERNEL
    SCAN_KERNEL --> AGENT_WORK
    AGENT_WORK --> LOOKBACK
```

**Scan Dispatch Flow**

The scan dispatch initializes tile state before launching the main scan kernel.

**Sources:** [cub/cub/device/dispatch/dispatch_scan.cuh:200-350](), [cub/cub/device/dispatch/kernels/scan.cuh:50-200](), [cub/cub/agent/agent_scan.cuh:200-600]()

## Device Select Architecture

### Select Dispatch Strategy

The `DispatchSelectIf` implementation handles conditional element selection with optional compaction:

```mermaid
graph TB
    SELECT_DISPATCH["DispatchSelectIf::Dispatch()"]
    
    INIT_KERNEL["SelectInitKernel<br/>Initialize selection state"]
    
    SELECT_KERNEL["SelectKernel<br/>Two-phase selection"]
    
    subgraph "Phase 1: Scan Flags"
        LOAD_ITEMS["Load input items"]
        EVAL_PRED["Evaluate SelectOpT predicate"]
        FLAG_SCAN["BlockScan on flags"]
        WRITE_STATE["Write to SelectionState"]
    end
    
    subgraph "Phase 2: Compact Output"
        WAIT_PREFIX["Wait for prefix from<br/>earlier blocks"]
        SCATTER["Scatter selected items<br/>to output"]
    end
    
    FINALIZE["Copy num_selected_out<br/>to user pointer"]
    
    SELECT_DISPATCH --> INIT_KERNEL
    INIT_KERNEL --> SELECT_KERNEL
    SELECT_KERNEL --> LOAD_ITEMS
    LOAD_ITEMS --> EVAL_PRED
    EVAL_PRED --> FLAG_SCAN
    FLAG_SCAN --> WRITE_STATE
    WRITE_STATE --> WAIT_PREFIX
    WAIT_PREFIX --> SCATTER
    SCATTER --> FINALIZE
```

**DeviceSelect Execution Path**

Select operations scan predicate flags and compact output in a two-phase process.

**Sources:** [cub/cub/device/dispatch/dispatch_select_if.cuh:300-600](), [cub/cub/agent/agent_select_if.cuh:100-500]()

### Select Agent Structure

The `AgentSelectIf` template coordinates block-level selection:

| Template Parameter | Purpose |
|-------------------|---------|
| `SelectIfPolicyT` | Tuning parameters (threads, items, load/store algorithms) |
| `InputIteratorT` | Source data iterator |
| `FlagsInputIteratorT` | Optional pre-computed flags |
| `SelectedOutputIteratorT` | Output for selected items |
| `SelectOpT` | Predicate functor |
| `OffsetT` | Index type |
| `KeepRejects` | Whether to also output rejected items |

**Sources:** [cub/cub/agent/agent_select_if.cuh:100-200](), [cub/cub/device/dispatch/dispatch_select_if.cuh:70-150]()

## Policy Selection and Tuning System

### New Tuning API (CCCL 3.0+)

Starting with CCCL 3.0, device-wide operations use a new policy selection architecture based on `policy_selector` functors:

```mermaid
graph TB
    POLICY_SEL["policy_selector_from_types<AccumT, OffsetT, OpT><br/>Stateless functor, passable to kernels"]
    
    OPERATOR["constexpr auto operator()(cuda::arch_id arch) const<br/>Returns policy struct for given architecture"]
    
    TYPE_CLASS["Type Classification:<br/>type_t (float32, float64, other)<br/>op_kind_t (plus, min, max, other)<br/>size_t (1, 2, 4, 8, 16 bytes)"]
    
    ARCH_SELECT["Architecture Selection:<br/>if (arch >= arch_id::sm_100)<br/>else if (arch >= arch_id::sm_90)<br/>else if (arch >= arch_id::sm_80)"]
    
    TUNING_PARAMS["Return policy struct:<br/>reduce_policy { .reduce, .single_tile, .reduce_nondeterministic }<br/>transform_policy { .algorithm, .prefetch, .vectorized, .async_copy }<br/>scan_policy { .block_threads, .items_per_thread, ... }"]
    
    DISPATCH_ARCH["detail::dispatch_arch(policy_selector, arch_id, functor)<br/>Calls functor with selected policy"]
    
    POLICY_SEL --> OPERATOR
    OPERATOR --> TYPE_CLASS
    TYPE_CLASS --> ARCH_SELECT
    ARCH_SELECT --> TUNING_PARAMS
    TUNING_PARAMS --> DISPATCH_ARCH
```

**policy_selector Functor Architecture**

The new API uses compile-time type classification and runtime architecture queries to select tuning parameters. Policy selectors are stateless and can be passed to device code.

**Sources:** [cub/cub/device/dispatch/tuning/tuning_reduce.cuh:125-505](), [cub/cub/device/dispatch/tuning/tuning_transform.cuh:325-459](), [cub/cub/device/dispatch/tuning/tuning_scan.cuh:117-850](), [cub/cub/detail/arch_dispatch.cuh:1-200]()

### Legacy ChainedPolicy Runtime Selection (Deprecated)

The legacy `ChainedPolicy` mechanism (pre-CCCL 3.0) enables runtime selection of compile-time policies:

```mermaid
graph TB
    DISPATCH["DispatchReduce::Dispatch() or similar"]
    
    PTX_QUERY["PtxVersion(ptx_version, device)<br/>Query PTX virtual architecture"]
    
    CHAINED_INVOKE["max_policy.Invoke(ptx_version, dispatch_functor)<br/>ChainedPolicy<PolicyPtxVersion, PolicyT, PrevPolicyT>"]
    
    ARCH_LIST["__CUDA_ARCH_LIST__ or NV_TARGET_SM_INTEGER_LIST<br/>Compile-time list: e.g., 800, 860, 890, 900"]
    
    RUNTIME_MATCH["runtime_arch_to_compiletime<ArchMult, CudaArches...>()<br/>Fold expression: device_ptx_version == CudaArches * ArchMult"]
    
    FIND_POLICY["find_and_invoke_policy<DevicePtxVersion>()<br/>Walks ChainedPolicy list recursively"]
    
    ACTIVE_SEL{"DevicePtxVersion < PolicyPtxVersion?"}
    
    PREV["Recurse to PrevPolicyT::find_and_invoke_policy()"]
    
    CURRENT["dispatch_functor.template Invoke<PolicyT>()<br/>Launch kernel with selected policy"]
    
    DISPATCH --> PTX_QUERY
    PTX_QUERY --> CHAINED_INVOKE
    CHAINED_INVOKE --> ARCH_LIST
    ARCH_LIST --> RUNTIME_MATCH
    RUNTIME_MATCH --> FIND_POLICY
    FIND_POLICY --> ACTIVE_SEL
    ACTIVE_SEL -->|"Yes"| PREV
    ACTIVE_SEL -->|"No"| CURRENT
```

**ChainedPolicy<PolicyPtxVersion, PolicyT, PrevPolicyT> Runtime Dispatch (Legacy)**

PTX version detected at runtime selects from compile-time instantiated policies. This mechanism is deprecated in favor of the new `policy_selector` API but still used internally by some dispatchers.

**Sources:** [cub/cub/util_device.cuh:774-850](), [cub/cub/device/dispatch/dispatch_reduce.cuh:490-534](), [cub/cub/device/dispatch/tuning/tuning_reduce.cuh:94-140]()

### Tuning Policy Parameters

Common tuning parameters across device-wide operations:

| Parameter | Purpose | Typical Range |
|-----------|---------|---------------|
| `BLOCK_THREADS` | Threads per block | 128-512 |
| `ITEMS_PER_THREAD` | Items processed per thread | 4-24 |
| `VECTOR_LOAD_LENGTH` | Vector load size | 1, 2, 4 |
| `BLOCK_ALGORITHM` | Block-level algorithm choice | `BLOCK_REDUCE_RAKING`, `BLOCK_REDUCE_WARP_REDUCTIONS` |
| `LOAD_MODIFIER` | Cache hint for loads | `LOAD_DEFAULT`, `LOAD_CS`, `LOAD_LDG` |
| `LOAD_ALGORITHM` | Block load strategy | `BLOCK_LOAD_DIRECT`, `BLOCK_LOAD_WARP_TRANSPOSE` |
| `STORE_ALGORITHM` | Block store strategy | `BLOCK_STORE_DIRECT`, `BLOCK_STORE_WARP_TRANSPOSE` |

**Sources:** [cub/cub/agent/agent_reduce.cuh:66-93](), [cub/cub/device/dispatch/tuning/tuning_scan.cuh:93-114](), [cub/cub/device/dispatch/tuning/tuning_transform.cuh:93-153]()

## Temporary Storage Management

### Storage Aliasing Pattern

Device-wide operations use a unified temporary storage pattern:

```mermaid
graph TB
    USER_QUERY["User calls with<br/>d_temp_storage = nullptr"]
    
    CALC_SIZE["Algorithm calculates<br/>required allocation sizes"]
    
    ALIAS_TEMPS["AliasTemporaries()<br/>Compute offsets"]
    
    WRITE_SIZE["Write total to<br/>temp_storage_bytes"]
    
    RETURN_SIZE["Return to user"]
    
    USER_ALLOC["User allocates memory"]
    
    REAL_CALL["User calls with<br/>d_temp_storage != nullptr"]
    
    ALIAS_REAL["AliasTemporaries()<br/>Set allocation pointers"]
    
    USE_ALLOCS["Algorithm uses<br/>allocated regions"]
    
    USER_QUERY --> CALC_SIZE
    CALC_SIZE --> ALIAS_TEMPS
    ALIAS_TEMPS --> WRITE_SIZE
    WRITE_SIZE --> RETURN_SIZE
    RETURN_SIZE --> USER_ALLOC
    USER_ALLOC --> REAL_CALL
    REAL_CALL --> ALIAS_REAL
    ALIAS_REAL --> USE_ALLOCS
```

**Two-Phase Temporary Storage Pattern**

All device-wide operations follow this pattern for memory management.

**Sources:** [cub/cub/device/dispatch/dispatch_reduce.cuh:346-358](), [cub/cub/device/dispatch/dispatch_scan.cuh:250-300](), [cub/cub/util_temporary_storage.cuh:1-200]()

### Example: Reduce Storage Allocation

For a two-pass reduction with `max_blocks = 1024` and `AccumT = int`:

```
allocations[0] = block_reductions    // 1024 * sizeof(int) = 4096 bytes
Total temp_storage_bytes = 4096
```

For a scan with 10,000 items and `tile_size = 2048`:

```
allocations[0] = tile_state          // 5 tiles * sizeof(ScanTileDescriptor<AccumT>)
Total temp_storage_bytes = 5 * sizeof(ScanTileDescriptor<int>)
```

**Sources:** [cub/cub/device/dispatch/dispatch_reduce.cuh:345-358](), [cub/cub/device/dispatch/dispatch_scan.cuh:250-300]()

## Kernel Launch Configuration

### Grid Dimension Calculation

Device-wide operations compute grid dimensions based on occupancy targets:

```mermaid
graph TB
    QUERY_SM["Query SM count<br/>MultiProcessorCount()"]
    
    QUERY_OCC["Query kernel occupancy<br/>MaxSmOccupancy()"]
    
    CALC_TILES["Calculate tiles needed:<br/>ceil(num_items / tile_size)"]
    
    CALC_DEVICE_OCC["device_occupancy =<br/>sm_count * sm_occupancy"]
    
    DETERMINE_BLOCKS{"Determine blocks"}
    
    OPTION_A["Limited by tiles:<br/>min(device_occupancy, tiles)"]
    
    OPTION_B["Subscription factor:<br/>device_occupancy * factor"]
    
    GRID_DIM["Set grid dimensions"]
    
    QUERY_SM --> QUERY_OCC
    QUERY_OCC --> CALC_TILES
    CALC_TILES --> CALC_DEVICE_OCC
    CALC_DEVICE_OCC --> DETERMINE_BLOCKS
    DETERMINE_BLOCKS --> OPTION_A
    DETERMINE_BLOCKS --> OPTION_B
    OPTION_A --> GRID_DIM
    OPTION_B --> GRID_DIM
```

**Grid Dimension Strategy**

Operations balance between available SMs and required tiles.

**Sources:** [cub/cub/device/dispatch/dispatch_reduce.cuh:322-343](), [cub/cub/device/dispatch/dispatch_histogram.cuh:150-192]()

### Kernel Configuration Structure

The `KernelConfig` structure encapsulates launch parameters:

| Field | Description | Initialized By |
|-------|-------------|----------------|
| `block_threads` | Threads per block | Policy `BlockThreads()` |
| `items_per_thread` | Items per thread | Policy `ItemsPerThread()` |
| `tile_size` | Items per tile | `block_threads * items_per_thread` |
| `sm_occupancy` | Blocks per SM | `MaxSmOccupancy()` query |

**Sources:** [cub/cub/util_device.cuh:694-713]()

## Agent-Based Execution Model

### Agent Abstraction

Agents provide block-level abstractions that encapsulate shared memory management and tile processing logic:

```mermaid
graph TB
    subgraph AgentReduce["AgentReduce<PolicyT, InputIteratorT, OutputIteratorT, OffsetT, ReductionOpT, AccumT>"]
        AR_STRUCT["struct TempStorage {<br/>BlockReduceT::TempStorage reduce;<br/>}"]
        AR_CONSUME["AccumT ConsumeRange(block_offset, block_end)<br/>Process multiple tiles per block"]
        AR_CONSUME_TILE["AccumT ConsumeTile(offset, valid_items)<br/>Single tile with BlockLoad + BlockReduce"]
    end
    
    subgraph AgentScan["AgentScan<PolicyT, InputIteratorT, OutputIteratorT, ScanOpT, InitValueT, OffsetT>"]
        AS_STRUCT["struct TempStorage {<br/>BlockLoadT::TempStorage load;<br/>BlockStoreT::TempStorage store;<br/>BlockScanT::TempStorage scan;<br/>}"]
        AS_CONSUME["void ConsumeRange(tile_idx, tile_state, scan_op)<br/>Process tiles with lookback prefix callback"]
        AS_CALLBACK["LookbackPrefixCallbackOp<br/>Queries TileState for block prefix"]
    end
    
    subgraph AgentSelectIf["AgentSelectIf<PolicyT, InputIteratorT, FlagsInputIteratorT, SelectedOutputIteratorT, SelectOpT, OffsetT, KeepRejects>"]
        ASI_STRUCT["struct TempStorage {<br/>BlockLoadT::TempStorage load_items;<br/>BlockLoadT::TempStorage load_flags;<br/>BlockScanT::TempStorage scan;<br/>BlockDiscontinuityT::TempStorage discontinuity;<br/>}"]
        ASI_CONSUME["void ConsumeRange(num_items, tile_state, select_op)<br/>Two-phase: scan flags then scatter"]
    end
    
    subgraph SharedMem["Shared Memory Allocation"]
        SMEM["__shared__ union {<br/>typename AgentT::TempStorage temp_storage;<br/>} smem;"]
    end
    
    AR_STRUCT -.->|"Allocates"| SMEM
    AS_STRUCT -.->|"Allocates"| SMEM
    ASI_STRUCT -.->|"Allocates"| SMEM
```

**Agent Template Structure**

Agents are templated on policy types and iterator types, providing a `TempStorage` nested struct for shared memory and methods for tile processing.

**Sources:** [cub/cub/agent/agent_reduce.cuh:116-468](), [cub/cub/agent/agent_scan.cuh:142-958](), [cub/cub/agent/agent_select_if.cuh:156-1134]()

### Agent-Kernel Relationship

Device-wide kernels instantiate and invoke agents per thread block:

```mermaid
graph TB
    KERNEL_ENTRY["__global__ void DeviceReduceKernel<PolicySelector, ...>()<br/>Grid-stride loop over tiles"]
    
    POLICY_QUERY["constexpr auto policy = policy_selector(arch_id)<br/>Query runtime policy (new API)"]
    
    SMEM_ALLOC["__shared__ union {<br/>typename AgentReduceT::TempStorage storage;<br/>} temp_storage;"]
    
    AGENT_TYPEDEF["using AgentReduceT = AgentReduce<br/>decltype(policy.reduce),<br/>InputIteratorT, AccumT*,<br/>OffsetT, ReductionOpT, AccumT>"]
    
    AGENT_CONSTRUCT["AgentReduceT agent(<br/>temp_storage.storage,<br/>d_in, reduction_op)"]
    
    BLOCK_OFFSET["OffsetT block_offset = blockIdx.x * tile_size"]
    
    CONSUME_RANGE["AccumT block_aggregate =<br/>agent.ConsumeRange(block_offset, block_end)"]
    
    WRITE_OUTPUT["if (threadIdx.x == 0)<br/>d_block_reductions[blockIdx.x] = block_aggregate"]
    
    KERNEL_ENTRY --> POLICY_QUERY
    POLICY_QUERY --> SMEM_ALLOC
    SMEM_ALLOC --> AGENT_TYPEDEF
    AGENT_TYPEDEF --> AGENT_CONSTRUCT
    AGENT_CONSTRUCT --> BLOCK_OFFSET
    BLOCK_OFFSET --> CONSUME_RANGE
    CONSUME_RANGE --> WRITE_OUTPUT
```

**Kernel-Agent Instantiation Pattern**

Kernels query the policy selector, instantiate the agent type with the selected policy, allocate shared memory, construct the agent instance, and invoke `ConsumeRange()`.

**Sources:** [cub/cub/device/dispatch/kernels/kernel_reduce.cuh:149-272](), [cub/cub/agent/agent_reduce.cuh:204-468](), [cub/cub/device/dispatch/dispatch_reduce.cuh:62-75]()

## Performance Optimization Strategies

### Memory Access Optimization

Device-wide operations optimize memory access through multiple techniques:

| Technique | Implementation | Benefit |
|-----------|---------------|---------|
| **Vectorized Loads** | `VECTOR_LOAD_LENGTH` in policy | Coalesced access, reduced instructions |
| **Warp-Transpose** | `BLOCK_LOAD_WARP_TRANSPOSE` | Improved coalescing for strided access |
| **Cache Hints** | `LOAD_LDG`, `LOAD_CS` modifiers | Better cache utilization |
| **Async Copy** | `cp.async.cg`, `cp.async.bulk` | Overlap compute and memory transfer |
| **Prefetch** | Software prefetch loops | Hide memory latency |

**Sources:** [cub/cub/device/dispatch/tuning/tuning_transform.cuh:219-330](), [cub/cub/device/dispatch/kernels/transform.cuh:69-95](), [cub/cub/block/block_load.cuh:1-500]()

### Occupancy and Tile Size Tuning

The relationship between tile size and occupancy affects performance:

```
tile_size = block_threads * items_per_thread
tiles_needed = ceil(num_items / tile_size)

Goal: Maximize (occupancy * tile_size) while fitting in resources
```

Larger tiles reduce kernel launch overhead but may decrease occupancy due to register or shared memory pressure.

**Sources:** [cub/cub/device/dispatch/tuning/tuning_reduce.cuh:1-300](), [cub/cub/device/dispatch/tuning/tuning_scan.cuh:1-600]()

### Algorithm-Specific Optimizations

**Reduce:** Two-pass strategy minimizes synchronization overhead for large inputs.

**Transform:** Multiple kernel variants maximize memory bandwidth for different data layouts.

**Scan:** Lookback pattern enables single-pass execution without global synchronization.

**Select:** Two-phase scan-then-scatter minimizes divergence and atomic operations.

**Sources:** [cub/cub/device/dispatch/dispatch_reduce.cuh:314-432](), [cub/cub/device/dispatch/dispatch_transform.cuh:497-526](), [cub/cub/agent/agent_scan.cuh:300-600](), [cub/cub/agent/agent_select_if.cuh:400-800]()

---

