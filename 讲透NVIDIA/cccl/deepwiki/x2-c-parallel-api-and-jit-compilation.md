<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/cccl · extra page C Parallel API and JIT Compilation · fetched 2026-10-26 -->

# C Parallel API and JIT Compilation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

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
- [cub/cub/detail/arch_dispatch.cuh](cub/cub/detail/arch_dispatch.cuh)
- [cub/cub/detail/launcher/cuda_driver.cuh](cub/cub/detail/launcher/cuda_driver.cuh)
- [cub/cub/detail/launcher/cuda_runtime.cuh](cub/cub/detail/launcher/cuda_runtime.cuh)
- [cub/cub/device/device_radix_sort.cuh](cub/cub/device/device_radix_sort.cuh)
- [cub/cub/device/device_segmented_reduce.cuh](cub/cub/device/device_segmented_reduce.cuh)
- [cub/cub/device/dispatch/dispatch_common.cuh](cub/cub/device/dispatch/dispatch_common.cuh)
- [cub/cub/device/dispatch/dispatch_fixed_size_segmented_reduce.cuh](cub/cub/device/dispatch/dispatch_fixed_size_segmented_reduce.cuh)
- [cub/cub/device/dispatch/dispatch_merge_sort.cuh](cub/cub/device/dispatch/dispatch_merge_sort.cuh)
- [cub/cub/device/dispatch/dispatch_radix_sort.cuh](cub/cub/device/dispatch/dispatch_radix_sort.cuh)
- [cub/cub/device/dispatch/dispatch_reduce.cuh](cub/cub/device/dispatch/dispatch_reduce.cuh)
- [cub/cub/device/dispatch/dispatch_segmented_radix_sort.cuh](cub/cub/device/dispatch/dispatch_segmented_radix_sort.cuh)
- [cub/cub/device/dispatch/dispatch_segmented_reduce.cuh](cub/cub/device/dispatch/dispatch_segmented_reduce.cuh)
- [cub/cub/device/dispatch/dispatch_segmented_sort.cuh](cub/cub/device/dispatch/dispatch_segmented_sort.cuh)
- [cub/cub/device/dispatch/kernels/kernel_radix_sort.cuh](cub/cub/device/dispatch/kernels/kernel_radix_sort.cuh)
- [cub/cub/device/dispatch/kernels/kernel_segmented_radix_sort.cuh](cub/cub/device/dispatch/kernels/kernel_segmented_radix_sort.cuh)
- [cub/cub/device/dispatch/kernels/kernel_segmented_reduce.cuh](cub/cub/device/dispatch/kernels/kernel_segmented_reduce.cuh)
- [cub/cub/device/dispatch/tuning/common.cuh](cub/cub/device/dispatch/tuning/common.cuh)
- [cub/cub/device/dispatch/tuning/tuning_radix_sort.cuh](cub/cub/device/dispatch/tuning/tuning_radix_sort.cuh)
- [cub/cub/util_device.cuh](cub/cub/util_device.cuh)
- [cub/test/catch2_test_arch_dispatch.cu](cub/test/catch2_test_arch_dispatch.cu)
- [cub/test/catch2_test_device_radix_sort_custom_policy_hub.cu](cub/test/catch2_test_device_radix_sort_custom_policy_hub.cu)

</details>



## Purpose and Scope

This page documents the **C Parallel API** (also known as CCCL.C), a language-agnostic C interface to CUB's device-wide primitives that leverages **JIT (Just-In-Time) compilation** via NVRTC (NVIDIA Runtime Compiler) to generate specialized kernels at runtime. This system enables non-C++ languages (such as Python, Rust, or Julia) to access CUB's high-performance parallel algorithms without requiring compile-time template instantiation.

The C API wraps CUB primitives like reduce, scan, sort, and transform, compiling them dynamically based on user-specified iterator types, operations, and data types. This differs from the standard C++ template-based CUB API documented in [CUB](#2.2), which requires compile-time type information.

For information about CUB's internal dispatch mechanisms and policy systems, see [Dispatch and Policy System](#5.2). For details on NVRTC usage patterns, see [JIT Compilation and Code Generation](#5.5).

## Architecture Overview

The C Parallel API follows a two-phase architecture: a **build phase** that JIT-compiles specialized kernels, and an **execution phase** that launches those kernels using the CUDA Driver API.

```mermaid
graph TB
    User["User Application<br/>(C, Python, Rust, etc.)"]
    
    subgraph "Build Phase (JIT Compilation)"
        BuildAPI["cccl_device_*_build_ex()<br/>Functions"]
        CodeGen["Template Code<br/>Generation"]
        NVRTC["NVRTC Compiler"]
        LTO["LTO-IR Linking"]
        PolicySel["Policy Selector<br/>Runtime Tuning"]
    end
    
    subgraph "Build Result"
        BuildResult["cccl_device_*_build_result_t"]
        Kernels["CUkernel Handles"]
        Metadata["Metadata<br/>(accumulator size, policy, etc.)"]
    end
    
    subgraph "Execution Phase"
        ExecAPI["cccl_device_*()<br/>Functions"]
        Dispatch["CUB Dispatch Logic"]
        DriverAPI["CUDA Driver API<br/>cuLaunchKernel()"]
    end
    
    subgraph "CUB Internals"
        CUBKernels["CUB Device Kernels<br/>(DeviceReduceKernel, etc.)"]
        Agents["Agent Classes<br/>(AgentReduce, etc.)"]
    end
    
    User -->|"1. Build Request"| BuildAPI
    BuildAPI --> CodeGen
    CodeGen --> NVRTC
    NVRTC --> LTO
    LTO --> Kernels
    BuildAPI --> PolicySel
    PolicySel --> Metadata
    Kernels --> BuildResult
    Metadata --> BuildResult
    
    User -->|"2. Execute with Build Result"| ExecAPI
    BuildResult --> ExecAPI
    ExecAPI --> Dispatch
    Dispatch --> DriverAPI
    DriverAPI --> CUBKernels
    CUBKernels --> Agents
    
    style BuildAPI fill:#f9f,stroke:#333
    style ExecAPI fill:#9ff,stroke:#333
    style BuildResult fill:#ff9,stroke:#333
```

**Sources:** [c/parallel/src/reduce.cu:175-385](), [c/parallel/src/transform.cu:214-351]()

## Build Phase: JIT Compilation Pipeline

The build phase transforms user-specified types and operations into compiled CUDA kernels. This occurs in several stages:

### Code Generation

Each algorithm generates specialized C++ template code based on input parameters:

```mermaid
graph LR
    Input["User Inputs<br/>- Iterator types<br/>- Operation<br/>- Data types"]
    
    subgraph "Template Specialization"
        IterTraits["Iterator Traits<br/>input_iterator_traits<br/>output_iterator_traits"]
        OpTraits["Operation Traits<br/>binary_user_operation_traits"]
        TypeMapping["Type Mapping<br/>cccl_type_enum_to_name()"]
    end
    
    subgraph "Code Assembly"
        Header["JIT Template Headers"]
        IterSrc["Iterator Source<br/>get_specialization()"]
        OpSrc["Operation Source<br/>get_specialization()"]
        PolicyExpr["Policy Selector Expression"]
        FinalSrc["Final Source Code"]
    end
    
    Input --> IterTraits
    Input --> OpTraits
    Input --> TypeMapping
    
    IterTraits --> IterSrc
    OpTraits --> OpSrc
    TypeMapping --> PolicyExpr
    
    Header --> FinalSrc
    IterSrc --> FinalSrc
    OpSrc --> FinalSrc
    PolicyExpr --> FinalSrc
    
    FinalSrc -->|"Passed to NVRTC"| NVRTC["NVRTC Compilation"]
```

**Example from Device Reduce:**

The `cccl_device_reduce_build_ex` function generates code that includes:

| Component | Generated Code Element | Purpose |
|-----------|----------------------|---------|
| Storage Types | `struct __align__(n) storage_t { char data[size]; }` | Stores user-defined types |
| Iterators | Specializations of `input_iterator_traits`, `output_iterator_traits` | Type-erased iterator wrappers |
| Operations | Specializations of `binary_user_operation_traits` | Type-erased operation wrappers |
| Policy | `cub::detail::reduce::policy_selector_from_types<AccumT, OffsetT, OpT>` | Runtime tuning policy selection |

**Sources:** [c/parallel/src/reduce.cu:175-293](), [c/parallel/src/transform.cu:214-284]()

### NVRTC Compilation and LTO-IR Linking

The generated code is compiled using NVRTC with link-time optimization:

```mermaid
graph TB
    MainTU["Main Translation Unit<br/>(Generated Code)"]
    
    subgraph "Separate LTO-IRs"
        OpLTO["Operation LTO-IR<br/>(User Operation)"]
        IterLTO["Iterator LTO-IRs<br/>(Iterator Definitions)"]
    end
    
    subgraph "NVRTC Compilation"
        Compile["nvrtcCompileProgram()<br/>with -dlto, -rdc=true"]
        Extract["Extract Kernel Names<br/>nvrtcGetLoweredName()"]
    end
    
    subgraph "Linking Phase"
        LinkList["nvrtc_linkable_list"]
        Link["cuLinkAddData()<br/>LTO-IR Linking"]
        Finalize["cuLinkComplete()"]
    end
    
    subgraph "Result"
        Cubin["Compiled CUBIN"]
        Library["CUlibrary Handle"]
        KernelHandles["CUkernel Handles"]
    end
    
    MainTU --> Compile
    Compile --> Extract
    Extract --> LinkList
    
    OpLTO --> LinkList
    IterLTO --> LinkList
    
    LinkList --> Link
    Link --> Finalize
    Finalize --> Cubin
    
    Cubin --> Library
    Library --> KernelHandles
    
    style Compile fill:#f9f,stroke:#333
    style Link fill:#9ff,stroke:#333
    style Library fill:#ff9,stroke:#333
```

The linking architecture uses `nvrtc_linkable_list_appender` to collect all LTO-IR modules:

```mermaid
graph LR
    Appender["nvrtc_linkable_list_appender"]
    
    Appender -->|"append_operation()"| OpIR["Operation LTO-IR"]
    Appender -->|"add_iterator_definition()"| InputIter["Input Iterator LTO-IR"]
    Appender -->|"add_iterator_definition()"| OutputIter["Output Iterator LTO-IR"]
    
    OpIR --> LinkList["nvrtc_linkable_list"]
    InputIter --> LinkList
    OutputIter --> LinkList
    
    LinkList --> Linker["begin_linking_nvrtc_program()"]
```

**Sources:** [c/parallel/src/reduce.cu:330-375](), [c/parallel/src/radix_sort.cu:249-356]()

### Policy Selection and Runtime Tuning

Each algorithm selects optimal tuning parameters at build time based on data types and architecture:

```mermaid
graph TB
    Input["Input Types<br/>- Accumulator Type<br/>- Offset Type<br/>- Operation Kind"]
    
    subgraph "Type Classification"
        AccumClass["Accumulator Type<br/>float32, float64, other"]
        OpClass["Operation Kind<br/>plus, min, max, other"]
        OffsetSize["Offset Size<br/>4 or 8 bytes"]
    end
    
    subgraph "Policy Selector Construction"
        Selector["policy_selector<br/>{accum_type, op_kind, offset_size, accum_size}"]
    end
    
    subgraph "Architecture Query"
        ArchID["cuda::arch_id<br/>(from cc_major, cc_minor)"]
        Invoke["policy_selector(arch_id)"]
    end
    
    subgraph "Tuning Policy Result"
        Policy["Concrete Policy<br/>- block_threads<br/>- items_per_thread<br/>- algorithm variants"]
    end
    
    Input --> AccumClass
    Input --> OpClass
    Input --> OffsetSize
    
    AccumClass --> Selector
    OpClass --> Selector
    OffsetSize --> Selector
    
    Selector --> Invoke
    ArchID --> Invoke
    Invoke --> Policy
    
    Policy -->|"Embedded in Build Result"| BuildResult["build_result_t"]
```

For example, in Device Reduce, the policy selector considers:

| Input | Classification | Impact on Policy |
|-------|----------------|------------------|
| `CCCL_FLOAT32` | `type_t::float32` | Enables optimized float summation paths |
| `CCCL_FLOAT64` | `type_t::float64` | Adjusts register usage for double precision |
| `CCCL_PLUS` | `op_kind_t::plus` | May enable non-deterministic atomic optimizations |
| `CCCL_MINIMUM/MAXIMUM` | `op_kind_t::min/max` | Selects min/max-specific kernels |

**Sources:** [c/parallel/src/reduce.cu:223-254](), [c/parallel/src/segmented_reduce.cu:158-190]()

## Execution Phase: Kernel Dispatch

The execution phase uses the build result to launch specialized kernels via the CUDA Driver API:

```mermaid
graph TB
    BuildResult["cccl_device_*_build_result_t<br/>- CUkernel handles<br/>- Policy selector<br/>- Metadata"]
    
    subgraph "Execution Call"
        ExecFunc["cccl_device_*()<br/>(reduce, transform, etc.)"]
        Context["Context Management<br/>try_push_context()"]
    end
    
    subgraph "CUB Dispatch"
        DispatchFunc["cub::detail::*::dispatch()<br/>(templated dispatch logic)"]
        PolicySelect["Select Policy<br/>policy_selector(arch_id)"]
        ConfigCalc["Calculate Configuration<br/>- Grid size<br/>- Block size<br/>- Shared memory"]
    end
    
    subgraph "Kernel Launch"
        Factory["CudaDriverLauncherFactory"]
        Launcher["CudaDriverLauncher<br/>.doit()"]
        DriverAPI["cuLaunchKernel()"]
    end
    
    subgraph "Indirect Arguments"
        IndirectArg["indirect_arg_t<br/>Type-erased wrappers"]
        KernelArgs["Kernel Argument Array"]
    end
    
    BuildResult --> ExecFunc
    ExecFunc --> Context
    Context --> DispatchFunc
    
    BuildResult -->|"Provides policy"| PolicySelect
    PolicySelect --> ConfigCalc
    ConfigCalc --> Factory
    
    ExecFunc -->|"Wraps arguments"| IndirectArg
    IndirectArg --> KernelArgs
    
    Factory --> Launcher
    Launcher --> KernelArgs
    Launcher --> DriverAPI
    
    DriverAPI -->|"Executes"| CUDAKernel["CUDA Kernel<br/>(JIT-compiled)"]
    
    style ExecFunc fill:#9ff,stroke:#333
    style IndirectArg fill:#f9f,stroke:#333
    style DriverAPI fill:#ff9,stroke:#333
```

**Sources:** [c/parallel/src/reduce.cu:393-446](), [cub/cub/detail/launcher/cuda_driver.cuh:28-75]()

### Indirect Arguments and Type Erasure

The C API uses `indirect_arg_t` to pass type-erased arguments to kernels:

```mermaid
graph LR
    subgraph "C API Arguments"
        CIterator["cccl_iterator_t<br/>- type (pointer/custom)<br/>- state (void*)<br/>- value_type"]
        COperation["cccl_op_t<br/>- type (plus/custom)<br/>- name<br/>- ltoir"]
        CValue["cccl_value_t<br/>- type<br/>- state (void*)"]
    end
    
    subgraph "Wrapper Types"
        IndirectArg["indirect_arg_t<T><br/>- Holds void* or T*<br/>- Provides operator()"]
        IndirectIter["indirect_iterator_t<br/>- Holds cccl_iterator_t<br/>- Provides operator*"]
    end
    
    subgraph "Kernel Invocation"
        CUBDispatch["CUB Dispatch Function<br/>(expects iterator/op types)"]
        Kernel["JIT-Compiled Kernel<br/>(knows concrete types)"]
    end
    
    CIterator -->|"Wrapped in"| IndirectIter
    COperation -->|"Wrapped in"| IndirectArg
    CValue -->|"Wrapped in"| IndirectArg
    
    IndirectIter -->|"Passed to"| CUBDispatch
    IndirectArg -->|"Passed to"| CUBDispatch
    
    CUBDispatch -->|"Launches"| Kernel
    
    Kernel -->|"Dereferences at runtime"| IndirectIter
    Kernel -->|"Invokes at runtime"| IndirectArg
```

**Key mechanisms:**

| Wrapper Type | Purpose | Implementation |
|--------------|---------|----------------|
| `indirect_arg_t<T>` | Generic argument passing | Stores `void*` state, provides `operator()` to dereference as `T&` |
| `indirect_iterator_t` | Iterator abstraction | Wraps `cccl_iterator_t`, provides iterator interface via `operator*` |
| `op_wrapper` | Operation abstraction | JIT-compiled struct that implements binary/unary operation |

**Sources:** [c/parallel/src/reduce.cu:415-427](), [c/parallel/src/transform.cu:369-378]()

## Example: Device Reduce Build and Execution

### Build Phase Code Flow

```mermaid
sequenceDiagram
    participant User
    participant BuildFunc as cccl_device_reduce_build_ex
    participant CodeGen as Code Generator
    participant NVRTC as NVRTC Compiler
    participant Linker as LTO Linker
    
    User->>BuildFunc: input_it, output_it, op, init
    BuildFunc->>BuildFunc: get_accumulator_type(op, input_it, init)
    BuildFunc->>CodeGen: get_specialization<input_iterator_traits>()
    BuildFunc->>CodeGen: get_specialization<operation_traits>()
    BuildFunc->>BuildFunc: Construct policy_selector
    BuildFunc->>CodeGen: Generate final source code
    BuildFunc->>NVRTC: nvrtcCompileProgram(source, args)
    NVRTC-->>BuildFunc: LTO-IR for main TU
    BuildFunc->>Linker: Add operation LTO-IR
    BuildFunc->>Linker: Add iterator LTO-IRs
    Linker->>Linker: cuLinkAddData(all LTO-IRs)
    Linker->>Linker: cuLinkComplete()
    Linker-->>BuildFunc: Compiled CUBIN
    BuildFunc->>BuildFunc: cuLibraryLoadData()
    BuildFunc->>BuildFunc: cuLibraryGetKernel() x3
    BuildFunc-->>User: build_result_t with kernel handles
```

The generated kernel names follow this pattern:

| Kernel | Name Template | Purpose |
|--------|---------------|---------|
| Single Tile | `DeviceReduceSingleTileKernel<PolicySelector, InputIt, OutputIt, OffsetT, OpT, InitT, AccumT>` | Small problem sizes (one block) |
| Reduction | `DeviceReduceKernel<PolicySelector, InputIt, OffsetT, OpT, AccumT, TransformT>` | First pass of two-pass reduction |
| Second Tile | `DeviceReduceSingleTileKernel<PolicySelector, AccumT*, OutputIt, int, OpT, InitT, AccumT>` | Second pass reduction of block results |

**Sources:** [c/parallel/src/reduce.cu:52-139](), [c/parallel/src/reduce.cu:175-385]()

### Execution Phase Code Flow

```mermaid
sequenceDiagram
    participant User
    participant ExecFunc as cccl_device_reduce
    participant Dispatch as cub::detail::reduce::dispatch
    participant Factory as CudaDriverLauncherFactory
    participant Driver as CUDA Driver API
    
    User->>ExecFunc: build_result, d_in, d_out, num_items, op, init, stream
    ExecFunc->>ExecFunc: try_push_context()
    ExecFunc->>ExecFunc: Wrap arguments in indirect_arg_t
    ExecFunc->>Dispatch: dispatch(d_temp_storage, ..., indirect args)
    Dispatch->>Dispatch: policy_selector(arch_id) → active_policy
    Dispatch->>Dispatch: Check if small problem (single tile)
    alt Small Problem
        Dispatch->>Factory: Create launcher(1, block_threads, 0, stream)
        Factory->>Driver: cuLaunchKernel(single_tile_kernel, ...)
    else Large Problem
        Dispatch->>Dispatch: Calculate grid size, allocate temp storage
        Dispatch->>Factory: Create launcher(grid_size, block_threads, 0, stream)
        Factory->>Driver: cuLaunchKernel(reduction_kernel, ...)
        Dispatch->>Factory: Create launcher(1, block_threads, 0, stream)
        Factory->>Driver: cuLaunchKernel(single_tile_second_kernel, ...)
    end
    Driver-->>ExecFunc: cudaError_t
    ExecFunc->>ExecFunc: cuCtxPopCurrent()
    ExecFunc-->>User: CUresult
```

**Sources:** [c/parallel/src/reduce.cu:393-446](), [cub/cub/device/dispatch/dispatch_reduce.cuh:763-844]()

## Supported Algorithms

The C Parallel API provides JIT-compiled wrappers for the following CUB algorithms:

| Algorithm | Build Function | Execution Function | Key Features |
|-----------|----------------|-------------------|--------------|
| **Reduce** | `cccl_device_reduce_build_ex` | `cccl_device_reduce` | Deterministic and non-deterministic variants |
| **Transform** | `cccl_device_unary_transform_build_ex`<br/>`cccl_device_binary_transform_build_ex` | `cccl_device_unary_transform`<br/>`cccl_device_binary_transform` | Unary and binary operations, vectorization |
| **Scan** | `cccl_device_scan_build_ex` | `cccl_device_scan` | Inclusive/exclusive, with/without init |
| **Radix Sort** | `cccl_device_radix_sort_build_ex` | `cccl_device_radix_sort` | Keys-only and pairs, ascending/descending, custom decomposers |
| **Merge Sort** | `cccl_device_merge_sort_build_ex` | `cccl_device_merge_sort` | Keys-only and pairs, custom comparators |
| **Segmented Reduce** | `cccl_device_segmented_reduce_build_ex` | `cccl_device_segmented_reduce` | Fixed and variable segment sizes |
| **Segmented Sort** | `cccl_device_segmented_sort_build_ex` | `cccl_device_segmented_sort` | Keys-only and pairs, per-segment sorting |
| **Unique by Key** | `cccl_device_unique_by_key_build_ex` | `cccl_device_unique_by_key` | Key-value pair deduplication |
| **Three-Way Partition** | `cccl_device_three_way_partition_build_ex` | `cccl_device_three_way_partition` | Tri-state partitioning |
| **For** | `cccl_device_for_build_ex` | `cccl_device_for` | Parallel loop execution |

**Build Result Structures:**

All algorithms follow a similar build result pattern:

```mermaid
graph TB
    BuildResult["cccl_device_*_build_result_t"]
    
    BuildResult --> Library["CUlibrary library<br/>(CUBIN handle)"]
    BuildResult --> Kernels["CUkernel Handles<br/>(1-8 kernels depending on algorithm)"]
    BuildResult --> Metadata["Metadata"]
    
    Metadata --> Policy["void* runtime_policy<br/>(Policy selector instance)"]
    Metadata --> CUBIN["void* cubin<br/>(Raw CUBIN data)"]
    Metadata --> Size["size_t cubin_size"]
    Metadata --> CC["int cc<br/>(Compute capability)"]
    Metadata --> Algo["Algorithm-specific<br/>(e.g., accumulator_size)"]
```

**Sources:** [c/parallel/src/reduce.cu:1-557](), [c/parallel/src/transform.cu:1-530](), [c/parallel/src/radix_sort.cu:1-457]()

## Iterator and Operation Abstraction

The C API uses a trait-based system to generate code for user-defined iterators and operations:

### Iterator Traits

```mermaid
graph TB
    subgraph "Iterator Kinds"
        Pointer["CCCL_POINTER<br/>Raw pointer"]
        Custom["CCCL_ITERATOR<br/>Custom iterator"]
    end
    
    subgraph "Trait Specialization"
        InputTraits["input_iterator_traits<TagT>"]
        OutputTraits["output_iterator_traits<TagT>"]
    end
    
    subgraph "Generated Code"
        PointerCode["Type* pointer"]
        CustomCode["struct iterator_t {<br/>  storage_t state;<br/>  using value_type = storage_t;<br/>  value_type operator*() { ... }<br/>  iterator_t& operator++() { ... }<br/>}"]
    end
    
    Pointer --> InputTraits
    Custom --> InputTraits
    Pointer --> OutputTraits
    Custom --> OutputTraits
    
    InputTraits -->|"Pointer"| PointerCode
    InputTraits -->|"Custom"| CustomCode
    OutputTraits -->|"Pointer"| PointerCode
    OutputTraits -->|"Custom"| CustomCode
    
    PointerCode --> NVRTCSource["NVRTC Source Code"]
    CustomCode --> NVRTCSource
    CustomCode --> LTO["Custom Iterator LTO-IR<br/>(advance, dereference)"]
```

**Iterator State Management:**

| Iterator Component | Storage | Usage |
|-------------------|---------|-------|
| `cccl_iterator_t.type` | Enum (POINTER/ITERATOR) | Determines code generation path |
| `cccl_iterator_t.state` | `void*` | Points to actual iterator state |
| `cccl_iterator_t.value_type` | `cccl_type_info` | Describes element type and size |
| `cccl_iterator_t.advance_function` | LTO-IR | Implements `operator++` |
| `cccl_iterator_t.dereference_function` | LTO-IR | Implements `operator*` |

**Sources:** [c/parallel/src/reduce.cu:213-217](), [c/parallel/src/transform.cu:235-237]()

### Operation Traits

```mermaid
graph TB
    subgraph "Operation Kinds"
        Builtin["Built-in Operations<br/>CCCL_PLUS, CCCL_MINIMUM, etc."]
        Custom["CCCL_USER_*<br/>Custom operations"]
    end
    
    subgraph "Trait Specialization"
        UnaryTraits["unary_user_operation_traits<TagT>"]
        BinaryTraits["binary_user_operation_traits<TagT>"]
    end
    
    subgraph "Generated Code"
        BuiltinCode["Using cuda::std::plus<br/>Using cuda::minimum<br/>etc."]
        CustomCode["struct op_wrapper {<br/>  storage_t state;<br/>  auto operator()(...) { ... }<br/>}"]
    end
    
    Builtin --> BinaryTraits
    Custom --> UnaryTraits
    Custom --> BinaryTraits
    
    BinaryTraits -->|"Built-in"| BuiltinCode
    BinaryTraits -->|"Custom"| CustomCode
    UnaryTraits -->|"Custom"| CustomCode
    
    BuiltinCode --> NVRTCSource["NVRTC Source Code"]
    CustomCode --> NVRTCSource
    CustomCode --> LTO["Custom Operation LTO-IR<br/>(invoke function)"]
```

**Operation Specialization:**

For binary operations like reduce:

| Operation Type | Generated Name | Implementation |
|---------------|----------------|----------------|
| `CCCL_PLUS` | `::cuda::std::plus<>` | Standard library functor |
| `CCCL_MINIMUM` | `::cuda::minimum<>` | Standard library functor |
| `CCCL_MAXIMUM` | `::cuda::maximum<>` | Standard library functor |
| `CCCL_USER_BINARY_OP` | `op_wrapper` | Custom struct with `operator()(T, T)` linked from LTO-IR |

**Sources:** [c/parallel/src/reduce.cu:218-220](), [c/parallel/src/segmented_reduce.cu:151-152]()

## Policy Selection and Performance Tuning

The C API embeds the same tuning system used by CUB's C++ interface, enabling architecture-specific optimizations:

### Policy Selector Architecture

```mermaid
graph TB
    subgraph "Input Classification"
        DataType["Data Type<br/>float32/float64/other"]
        Operation["Operation Kind<br/>plus/min/max/other"]
        OffsetSize["Offset Size<br/>32-bit/64-bit"]
        DataSize["Data Element Size"]
    end
    
    subgraph "Policy Selector"
        Selector["policy_selector<br/>{type, op, offset_size, data_size}"]
        Invoke["operator()(arch_id)"]
    end
    
    subgraph "Architecture-Specific Policies"
        SM70["SM70 Policy<br/>- Optimized for Volta"]
        SM80["SM80 Policy<br/>- Optimized for Ampere"]
        SM90["SM90 Policy<br/>- Optimized for Hopper"]
    end
    
    subgraph "Tuning Parameters"
        BlockThreads["block_threads<br/>(128, 256, 512, etc.)"]
        ItemsPerThread["items_per_thread<br/>(7, 15, 23, etc.)"]
        Algorithm["Algorithm Variant<br/>(vectorized, async, prefetch)"]
        LoadModifier["Load Modifier<br/>(LDG, CA, etc.)"]
    end
    
    DataType --> Selector
    Operation --> Selector
    OffsetSize --> Selector
    DataSize --> Selector
    
    Selector --> Invoke
    
    Invoke -->|"SM 7.0"| SM70
    Invoke -->|"SM 8.0+"| SM80
    Invoke -->|"SM 9.0+"| SM90
    
    SM70 --> BlockThreads
    SM70 --> ItemsPerThread
    SM70 --> Algorithm
    SM70 --> LoadModifier
    
    SM80 --> BlockThreads
    SM80 --> ItemsPerThread
    SM80 --> Algorithm
    SM80 --> LoadModifier
    
    SM90 --> BlockThreads
    SM90 --> ItemsPerThread
    SM90 --> Algorithm
    SM90 --> LoadModifier
```

**Policy Selection Example (Reduce):**

The policy selector for reduce considers:

```mermaid
graph LR
    Input["Input Parameters"]
    
    Input --> Float32Plus["float32 + plus<br/>→ Optimized for FP32 sum"]
    Input --> Float64Plus["float64 + plus<br/>→ Adjusted for FP64"]
    Input --> IntMin["int32 + min<br/>→ Min-specific kernel"]
    Input --> OtherOp["other + other<br/>→ Generic kernel"]
    
    Float32Plus --> SM80F32["SM80: 256 threads<br/>15 items/thread<br/>vectorized load"]
    Float64Plus --> SM80F64["SM80: 256 threads<br/>7 items/thread<br/>normal load"]
    IntMin --> SM80Int["SM80: 512 threads<br/>23 items/thread<br/>LDG load"]
    OtherOp --> SM80Gen["SM80: 256 threads<br/>15 items/thread<br/>default"]
```

**Runtime Policy Storage:**

The build result stores the policy selector instance:

| Field | Type | Purpose |
|-------|------|---------|
| `build_result_t.runtime_policy` | `void*` | Pointer to `policy_selector` instance |
| Policy in dispatch | Type-safe cast | `*static_cast<policy_selector*>(build.runtime_policy)` |
| Policy evaluation | `operator()(arch_id)` | Returns concrete tuning parameters |

**Sources:** [c/parallel/src/reduce.cu:223-254](), [c/parallel/src/transform.cu:239-245](), [c/parallel/src/radix_sort.cu:229-235]()

## Build Configuration and Compiler Flags

The C API accepts optional build configuration to customize compilation:

```mermaid
graph TB
    Config["cccl_build_config"]
    
    Config --> Flags["flags: const char**"]
    Config --> NumFlags["num_flags: size_t"]
    
    Flags --> User1["Custom Compiler Flag 1"]
    Flags --> User2["Custom Compiler Flag 2"]
    Flags --> UserN["Custom Compiler Flag N"]
    
    subgraph "Default Flags (Always Added)"
        Arch["-arch=sm_XX"]
        Paths["-I paths for cub, thrust, libcudacxx, ctk"]
        RDC["-rdc=true"]
        DLTO["-dlto"]
        Std["-std=c++20"]
        CDP["-DCUB_DISABLE_CDP"]
    end
    
    User1 --> Merged["Merged Argument List"]
    User2 --> Merged
    UserN --> Merged
    Arch --> Merged
    Paths --> Merged
    RDC --> Merged
    DLTO --> Merged
    Std --> Merged
    CDP --> Merged
    
    Merged --> NVRTC["nvrtcCompileProgram()"]
```

**Standard Compilation Arguments:**

| Argument | Value | Purpose |
|----------|-------|---------|
| `-arch` | `sm_{cc_major}{cc_minor}` | Target GPU architecture |
| `-I` | CUB/Thrust/libcudacxx paths | Include directories |
| `-rdc=true` | Enabled | Relocatable device code for linking |
| `-dlto` | Enabled | Device link-time optimization |
| `-std=c++20` | C++20 | Required language standard |
| `-DCUB_DISABLE_CDP` | Defined | Disable CUDA Dynamic Parallelism |
| `-default-device` | Transform only | Default lambdas to `__device__` |

**Sources:** [c/parallel/src/reduce.cu:313-329](), [c/parallel/src/transform.cu:289-309]()

## Memory Management and Cleanup

### Build Result Lifecycle

```mermaid
stateDiagram-v2
    [*] --> Building: cccl_device_*_build_ex()
    Building --> Built: Success
    Built --> Executing: cccl_device_*() (multiple times)
    Executing --> Built: Kernel complete
    Built --> Cleanup: cccl_device_*_cleanup()
    Cleanup --> [*]: Resources freed
    
    note right of Building
        - Allocates CUBIN data
        - Creates CUlibrary
        - Gets CUkernel handles
        - Allocates policy selector
    end note
    
    note right of Cleanup
        - Frees CUBIN data
        - Unloads CUlibrary
        - Deletes policy selector
    end note
```

**Cleanup Operations:**

Each algorithm provides a cleanup function that frees allocated resources:

| Resource | Storage Location | Cleanup Method |
|----------|------------------|----------------|
| CUBIN data | `build_result.cubin` | `delete[]` or `unique_ptr` |
| CUlibrary | `build_result.library` | `cuLibraryUnload()` |
| Policy selector | `build_result.runtime_policy` | `delete` or `free()` |
| Algorithm cache | `build_result.cache` (transform) | `delete` |

**Sources:** [c/parallel/src/reduce.cu:503-525](), [c/parallel/src/transform.cu:477-490]()

---

