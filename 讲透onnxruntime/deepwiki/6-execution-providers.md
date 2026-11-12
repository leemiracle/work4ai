<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/onnxruntime · page 6 Execution Providers · fetched 2026-10-21 -->

# Execution Providers

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [include/onnxruntime/core/framework/execution_provider.h](include/onnxruntime/core/framework/execution_provider.h)
- [include/onnxruntime/core/framework/kernel_def_builder.h](include/onnxruntime/core/framework/kernel_def_builder.h)
- [include/onnxruntime/core/framework/kernel_registry.h](include/onnxruntime/core/framework/kernel_registry.h)
- [onnxruntime/core/framework/execution_provider.cc](onnxruntime/core/framework/execution_provider.cc)
- [onnxruntime/core/framework/kernel_def_builder.cc](onnxruntime/core/framework/kernel_def_builder.cc)
- [onnxruntime/core/framework/kernel_registry.cc](onnxruntime/core/framework/kernel_registry.cc)
- [onnxruntime/core/framework/kernel_registry_manager.cc](onnxruntime/core/framework/kernel_registry_manager.cc)
- [onnxruntime/core/framework/kernel_registry_manager.h](onnxruntime/core/framework/kernel_registry_manager.h)
- [onnxruntime/test/framework/kernel_registry_test.cc](onnxruntime/test/framework/kernel_registry_test.cc)

</details>



## Purpose and Scope

This document describes the Execution Provider (EP) system in ONNX Runtime, which enables hardware-accelerated inference and training across diverse compute platforms including CPUs, GPUs, and specialized accelerators. An execution provider is responsible for implementing ONNX operators on a specific hardware backend, managing device memory, and optimizing computational graphs for its target hardware.

This page covers the core EP abstraction (`IExecutionProvider`), graph partitioning mechanisms, kernel registration, and memory management patterns. For information about specific operator implementations, see [Operators and Kernels](#7). For training-specific EP usage, see [Training System](#8). For API-level EP configuration, see [Session Configuration](#3.4).

## Architecture Overview

The execution provider system provides a pluggable architecture where hardware-specific implementations can be added without modifying the core runtime. The runtime uses a capability-based partitioning scheme to assign graph nodes to EPs.

```mermaid
graph TB
    subgraph "Session Initialization"
        SessionOptions["SessionOptions<br/>(EP registration)"]
        Session["InferenceSession"]
        GraphViewer["GraphViewer"]
        SessionOptions --> Session
        Session --> GraphViewer
    end
    
    subgraph "EP Interface Layer"
        IExecutionProvider["IExecutionProvider<br/>(abstract interface)"]
        GetCapability["GetCapability()<br/>(capability reporting)"]
        GetKernelRegistry["GetKernelRegistry()<br/>(kernel lookup)"]
        CreatePreferredAllocators["CreatePreferredAllocators()<br/>(memory management)"]
        
        IExecutionProvider --> GetCapability
        IExecutionProvider --> GetKernelRegistry
        IExecutionProvider --> CreatePreferredAllocators
    end
    
    subgraph "Graph Partitioning"
        GraphPartitioner["Graph Partitioner"]
        ComputeCapability["ComputeCapability<br/>(IndexedSubGraph)"]
        IKernelLookup["IKernelLookup<br/>(kernel matching)"]
        
        GraphViewer --> GraphPartitioner
        GetCapability --> ComputeCapability
        IKernelLookup --> GetCapability
        GraphPartitioner --> ComputeCapability
    end
    
    subgraph "Concrete Providers"
        CPUExecutionProvider["CPUExecutionProvider<br/>(kCpuExecutionProvider)"]
        CUDAExecutionProvider["CUDAExecutionProvider<br/>(kCudaExecutionProvider)"]
        TensorRTExecutionProvider["TensorrtExecutionProvider"]
        QNNExecutionProvider["QNNExecutionProvider"]
        
        IExecutionProvider -.implements.- CPUExecutionProvider
        IExecutionProvider -.implements.- CUDAExecutionProvider
        IExecutionProvider -.implements.- TensorRTExecutionProvider
        IExecutionProvider -.implements.- QNNExecutionProvider
    end
    
    subgraph "Kernel Execution"
        KernelRegistry["KernelRegistry<br/>(per-EP kernels)"]
        OpKernel["OpKernel<br/>(compute implementation)"]
        
        GetKernelRegistry --> KernelRegistry
        KernelRegistry --> OpKernel
    end
    
    subgraph "Memory Management"
        AllocatorPtr["AllocatorPtr<br/>(device allocator)"]
        OrtDevice["OrtDevice<br/>(device descriptor)"]
        
        CreatePreferredAllocators --> AllocatorPtr
        AllocatorPtr --> OrtDevice
    end
```

**Sources:** [include/onnxruntime/core/framework/execution_provider.h:74-282](), [onnxruntime/core/framework/execution_provider.cc:14-30]()

## IExecutionProvider Interface

The `IExecutionProvider` abstract class defines the contract that all execution providers must implement. Each EP is identified by a unique type string (e.g., `kCpuExecutionProvider`, `kCudaExecutionProvider`) and is associated with an `OrtDevice` descriptor. For details, see [Execution Provider Interface](#6.1).

### Core Members

```mermaid
classDiagram
    class IExecutionProvider {
        -OrtDevice default_device_
        -string type_
        -Logger* logger_
        +GetCapability() vector~ComputeCapability~
        +GetKernelRegistry() shared_ptr~KernelRegistry~
        +GetDataTransfer() unique_ptr~IDataTransfer~
        +CreatePreferredAllocators() vector~AllocatorPtr~
        +GetDeviceId() int
        +Type() string
        +Sync() Status
        +OnRunStart() Status
        +OnRunEnd() Status
    }
    
    class OrtDevice {
        +DeviceType type
        +MemType mem_type
        +DeviceId id
    }
    
    class IKernelLookup {
        <<interface>>
        +LookUpKernel() KernelCreateInfo*
    }
    
    IExecutionProvider --> OrtDevice
    IExecutionProvider ..> IKernelLookup
```

| Method | Purpose |
|--------|---------|
| `GetCapability()` | Reports which graph nodes the EP can execute, returns `ComputeCapability` objects |
| `GetKernelRegistry()` | Provides EP-specific kernel implementations |
| `GetDataTransfer()` | Returns data transfer interface for moving data to/from device |
| `CreatePreferredAllocators()` | Creates memory allocators for the EP's device |
| `Sync()` | Blocks until all device work completes |
| `OnRunStart()` / `OnRunEnd()` | Lifecycle hooks for per-inference setup/teardown |

**Sources:** [include/onnxruntime/core/framework/execution_provider.h:74-282](), [onnxruntime/core/providers/cpu/cpu_execution_provider.cc:58-67]()

## Graph Partitioning and Capability Reporting

The runtime uses a capability-based system to partition the computational graph across multiple execution providers. Each EP examines the graph and reports which nodes it can execute. For details, see [Execution Provider Interface](#6.1).

### Capability Reporting Flow

```mermaid
sequenceDiagram
    participant GV as GraphViewer
    participant GP as GraphPartitioner
    participant EP as IExecutionProvider
    participant KL as IKernelLookup
    participant KR as KernelRegistry
    
    GP->>EP: GetCapability(graph_viewer, kernel_lookup, ...)
    
    loop For each node in graph
        EP->>GV: Iterate nodes
        EP->>KL: LookUpKernel(node)
        KL->>KR: Find matching kernel
        KR-->>KL: KernelCreateInfo*
        KL-->>EP: kernel_create_info
        
        alt Kernel found
            EP->>EP: Create IndexedSubGraph
            EP->>EP: Add node index
        end
    end
    
    EP-->>GP: vector<ComputeCapability>
    GP->>GP: Assign nodes to EPs
```

The default `GetCapability()` implementation in `IExecutionProvider` checks each node against the EP's kernel registry:

```cpp
// onnxruntime/core/framework/execution_provider.cc:19-29
std::vector<std::unique_ptr<ComputeCapability>>
IExecutionProvider::GetCapability(const onnxruntime::GraphViewer& graph,
                                  const IKernelLookup& kernel_lookup,
                                  const GraphOptimizerRegistry&,
                                  IResourceAccountant*) const {
  std::vector<std::unique_ptr<ComputeCapability>> result;
  for (const auto& node : graph.Nodes()) {
    if (const KernelCreateInfo* kernel_create_info = kernel_lookup.LookUpKernel(node);
        kernel_create_info != nullptr) {
      std::unique_ptr<IndexedSubGraph> sub_graph = std::make_unique<IndexedSubGraph>();
      sub_graph->nodes.push_back(node.Index());
      result.push_back(std::make_unique<ComputeCapability>(std::move(sub_graph)));
    }
  }

  return result;
}
```

Execution providers can override this to implement custom partitioning logic, such as fusing multiple nodes into a single subgraph.

**Sources:** [onnxruntime/core/framework/execution_provider.cc:14-30](), [include/onnxruntime/core/framework/execution_provider.h:158-162]()

### ComputeCapability Structure

```mermaid
graph LR
    ComputeCapability["ComputeCapability"]
    IndexedSubGraph["IndexedSubGraph<br/>(nodes to execute)"]
    MetaDef["MetaDef<br/>(fused node metadata)"]
    
    ComputeCapability --> IndexedSubGraph
    ComputeCapability -.optional.- MetaDef
    
    IndexedSubGraph --> NodeIndices["vector&lt;NodeIndex&gt;<br/>(node IDs)"]
```

A `ComputeCapability` contains an `IndexedSubGraph` specifying which nodes the EP will execute. For fused subgraphs, it may also include a `MetaDef` describing the fused operation.

**Sources:** [include/onnxruntime/core/framework/execution_provider.h:158-162]()

## Kernel Registration

Each execution provider maintains its own `KernelRegistry` containing operator implementations specific to its hardware. Kernels are registered using opset versioning and type constraints. For details, see [Execution Provider Interface](#6.1).

### Registration Pattern

EPs typically register kernels using macros that specify:
- Operator name (e.g., "Add", "Conv")
- Domain (typically `kOnnxDomain`)
- Opset version range
- Type constraints (supported data types)
- Implementation class

Example from CPU EP:

```cpp
// onnxruntime/core/providers/cpu/cpu_execution_provider.cc:157-178
ONNX_OPERATOR_VERSIONED_TYPED_KERNEL(
    Add,           // operator name
    7, 12,         // opset version range
    float,         // data type
    Add<float>     // implementation class
)
```

**Sources:** [onnxruntime/core/providers/cpu/cpu_execution_provider.cc:157-178]()

### Kernel Lookup Mechanism

```mermaid
graph TB
    Node["Graph Node<br/>(OpType, Domain, OpSetVersion)"]
    KernelRegistryManager["KernelRegistryManager"]
    EPRegistry["EP KernelRegistry"]
    
    Node --> KernelRegistryManager
    KernelRegistryManager --> EPRegistry
    
    EPRegistry --> Matcher["Kernel Matcher"]
    Matcher --> TypeCheck["Type Constraint Check"]
    Matcher --> VersionCheck["Opset Version Check"]
    
    TypeCheck --> KernelCreateInfo["KernelCreateInfo<br/>(kernel factory)"]
    VersionCheck --> KernelCreateInfo
```

The `IKernelLookup` interface abstracts kernel matching, allowing the runtime to find appropriate kernel implementations without exposing registry internals. The `KernelRegistryManager` orchestrates the search across multiple registries, including custom ones, as shown in `SearchKernelRegistry` [onnxruntime/core/framework/kernel_registry_manager.cc:60-105](). The `KernelRegistry::VerifyKernelDef` function [onnxruntime/core/framework/kernel_registry.cc:146-175]() performs the actual type and version matching.

**Sources:** [include/onnxruntime/core/framework/execution_provider.h:122-132](), [onnxruntime/core/framework/kernel_registry_manager.cc:60-105](), [onnxruntime/core/framework/kernel_registry.cc:146-175]()

## Memory Management

Execution providers manage device memory through the allocator abstraction. Each EP creates allocators for its specific memory types (device memory, pinned memory, etc.).

### Allocator Creation

```mermaid
graph TB
    EP["IExecutionProvider"]
    CreatePreferredAllocators["CreatePreferredAllocators()"]
    
    EP --> CreatePreferredAllocators
    
    subgraph "CPU EP Allocators"
        CPUAlloc["CPUAllocator<br/>(DEFAULT_CPU_ALLOCATOR_DEVICE_ID)"]
        ArenaConfig["Arena Configuration<br/>(optional)"]
        CPUAlloc --> ArenaConfig
    end
    
    subgraph "CUDA EP Allocators"
        CUDAAlloc["CUDAAllocator / CudaMempoolArena<br/>(device memory)"]
        PinnedAlloc["CUDAPinnedAllocator<br/>(host pinned memory)"]
        ExternalAlloc["CUDAExternalAllocator<br/>(user-provided)"]
        
        CUDAMemChoice{GPU mem pool<br/>supported?}
        CUDAMemChoice -->|Yes| CudaMempoolArena["CudaMempoolArena"]
        CUDAMemChoice -->|No| BFCArena["BFCArena<br/>(Best-Fit with Coalescing)"]
    end
    
    CreatePreferredAllocators -.CPU.- CPUAlloc
    CreatePreferredAllocators -.CUDA.- CUDAAlloc
    CreatePreferredAllocators -.CUDA.- PinnedAlloc
```

| Allocator Type | Purpose | Memory Location |
|----------------|---------|-----------------|
| `CPUAllocator` | Default CPU memory | Host RAM |
| `CUDAAllocator` | GPU device memory | Device VRAM |
| `CUDAPinnedAllocator` | Pinned host memory | Host RAM (page-locked) |
| `CudaMempoolArena` | CUDA memory pool allocator | Device VRAM (pooled) |

**Sources:** [onnxruntime/core/providers/cpu/cpu_execution_provider.cc:61-67](), [onnxruntime/core/providers/cuda/cuda_execution_provider.cc:140-206]()

### Device Synchronization

EPs implement the `Sync()` method to ensure all device work completes before returning control. This is critical for `IOBinding` and ensuring data consistency.

For CUDA EP:
```cpp
// onnxruntime/core/providers/cuda/cuda_execution_provider.cc:505-508
Status CUDAExecutionProvider::Sync() const {
  CUDA_RETURN_IF_ERROR(cudaDeviceSynchronize());
  return Status::OK();
}
```

**Sources:** [onnxruntime/core/providers/cuda/cuda_execution_provider.cc:505-508]()

## Concrete Execution Provider Implementations

### CPU Execution Provider

The `CPUExecutionProvider` is the default fallback provider supporting all standard ONNX operators. It uses MLAS (Microsoft Linear Algebra Subprograms) for optimized BLAS operations. For details, see [CPU Execution Provider](#6.2).

```mermaid
graph TB
    CPUExecutionProvider["CPUExecutionProvider<br/>(kCpuExecutionProvider)"]
    
    subgraph "CPU EP Components"
        CPUKernels["CPU Kernels<br/>(element-wise, GEMM, Conv, etc.)"]
        MLASLib["MLAS Library<br/>(platform-optimized BLAS)"]
        ContribOps["Contrib Operators<br/>(com.microsoft domain)"]
    end
    
    subgraph "Memory"
        CPUArena["CPU Arena Allocator<br/>(optional)"]
    end
    
    CPUExecutionProvider --> CPUKernels
    CPUKernels --> MLASLib
    CPUExecutionProvider --> ContribOps
    CPUExecutionProvider --> CPUArena
```

The CPU EP registers standard operations in [onnxruntime/core/providers/cpu/cpu_execution_provider.cc:70-1500]() and contrib operations conditionally based on build configuration.

**Sources:** [onnxruntime/core/providers/cpu/cpu_execution_provider.cc:1-1500]()

### CUDA Execution Provider

The `CUDAExecutionProvider` enables GPU acceleration using NVIDIA CUDA, cuDNN, and cuBLAS libraries. It supports advanced features like CUDA graphs for reduced kernel launch overhead. For details, see [CUDA Execution Provider](#6.3).

```mermaid
graph TB
    CUDAExecutionProvider["CUDAExecutionProvider<br/>(kCudaExecutionProvider)"]
    
    subgraph "CUDA EP State"
        DeviceId["device_id<br/>(GPU device)"]
        Stream["cudaStream_t<br/>(compute stream)"]
        DeviceProp["cudaDeviceProp<br/>(device properties)"]
    end
    
    subgraph "Per-Thread Context"
        PerThreadContext["PerThreadContext"]
        CublasHandle["cublasHandle_t"]
        CudnnHandle["cudnnHandle_t"]
        CUDAGraph["CUDAGraph<br/>(graph capture/replay)"]
        
        PerThreadContext --> CublasHandle
        PerThreadContext --> CudnnHandle
        PerThreadContext --> CUDAGraph
    end
    
    subgraph "Memory Management"
        CUDAAllocOptions{Allocator<br/>Type}
        CUDAAllocOptions -->|Mempool| CudaMempoolArena
        CUDAAllocOptions -->|Arena| BFCArena
        CUDAAllocOptions -->|External| ExternalAllocator
    end
    
    CUDAExecutionProvider --> DeviceId
    CUDAExecutionProvider --> Stream
    CUDAExecutionProvider --> DeviceProp
    CUDAExecutionProvider --> PerThreadContext
    CUDAExecutionProvider --> CUDAAllocOptions
```

**Key CUDA EP Features:**

| Feature | Configuration | Purpose |
|---------|---------------|---------|
| CUDA Graphs | `enable_cuda_graph` | Capture and replay execution graphs to reduce overhead |
| Tunable Operations | `tunable_op_enable` | Auto-tune kernels for optimal performance |
| TF32 Mode | `use_tf32` | Use Tensor Float 32 for faster GEMM/Conv |
| NHWC Layout | `prefer_nhwc` | Prefer NHWC data layout for conv operations |
| External Stream | `user_compute_stream` | Use user-provided CUDA stream |

**Sources:** [onnxruntime/core/providers/cuda/cuda_execution_provider.h:29-282](), [onnxruntime/core/providers/cuda/cuda_execution_provider.cc:326-372]()

### Per-Thread Context Management

CUDA EP maintains thread-local contexts containing library handles and CUDA graphs. This allows thread-safe execution with multiple concurrent inference sessions.

```mermaid
graph LR
    ThreadA["Thread A"]
    ThreadB["Thread B"]
    
    ThreadA --> ContextCacheA["PerThreadContextCache<br/>(thread_local)"]
    ThreadB --> ContextCacheB["PerThreadContextCache<br/>(thread_local)"]
    
    ContextCacheA --> ContextA["PerThreadContext A<br/>(cublas, cudnn, graphs)"]
    ContextCacheB --> ContextB["PerThreadContext B<br/>(cublas, cudnn, graphs)"]
    
    CUDAExecutionProvider["CUDAExecutionProvider"]
    
    ContextA -.weak_ptr.- CUDAExecutionProvider
    ContextB -.weak_ptr.- CUDAExecutionProvider
```

The EP maintains weak pointers to thread-local contexts and a pool of retired contexts for reuse. Context acquisition happens in `GetPerThreadContext()` [onnxruntime/core/providers/cuda/cuda_execution_provider.cc:446-482]().

**Sources:** [onnxruntime/core/providers/cuda/cuda_execution_provider.h:148-240](), [onnxruntime/core/providers/cuda/cuda_execution_provider.cc:446-503]()

### Other Execution Providers

The system supports numerous other EPs for different hardware. For details, see [Other Execution Providers](#6.5).

| EP Type | Provider String | Hardware |
|---------|----------------|----------|
| TensorRT | `kTensorrtExecutionProvider` | NVIDIA GPUs (optimizing compiler) |
| QNN | `kQnnExecutionProvider` | Qualcomm NPUs |
| CoreML | `kCoreMLExecutionProvider` | Apple Neural Engine |
| OpenVINO | `kOpenVINOExecutionProvider` | Intel accelerators |
| NNAPI | `kNnapiExecutionProvider` | Android Neural Networks API |
| DirectML | `kDmlExecutionProvider` | DirectX 12 GPUs |
| SNPE | `kSnpeExecutionProvider` | Qualcomm Snapdragon NPE |

Each follows the same `IExecutionProvider` interface but implements hardware-specific optimizations and memory management.

**Sources:** [onnxruntime/test/onnx/main.cc:58-60](), [onnxruntime/test/python/onnx_backend_test_series.py:132-165]()

## Configuration and Lifecycle

### EP Registration

Execution providers are registered with an `InferenceSession` through `SessionOptions`. The order of registration determines EP priority during graph partitioning (first registered = highest priority).

```mermaid
sequenceDiagram
    participant App as Application
    participant SO as SessionOptions
    participant EPF as ExecutionProviderFactory
    participant Sess as InferenceSession
    participant GP as GraphPartitioner
    
    App->>SO: Create SessionOptions
    App->>SO: AppendExecutionProvider_CUDA(options)
    SO->>EPF: Create CUDAProviderFactory
    
    App->>Sess: Create InferenceSession(options)
    Sess->>EPF: CreateProvider()
    EPF-->>Sess: CUDAExecutionProvider instance
    
    Sess->>Sess: Initialize()
    Sess->>GP: PartitionGraph(execution_providers)
    
    loop For each EP (priority order)
        GP->>CUDAExecutionProvider: GetCapability(graph)
        CUDAExecutionProvider-->>GP: ComputeCapability
    end
    
    GP->>GP: Assign nodes to EPs
```

Common registration patterns:

**C API:**
```c
OrtCUDAProviderOptionsV2 cuda_options;
// Configure cuda_options...
OrtSessionOptionsAppendExecutionProvider_CUDA_V2(session_options, &cuda_options);
```

**C++ API:**
```cpp
Ort::SessionOptions options;
OrtCUDAProviderOptionsV2 cuda_options{};
cuda_options.device_id = 0;
options.AppendExecutionProvider_CUDA_V2(cuda_options);
```

**Sources:** [onnxruntime/test/onnx/main.cc:484-522](), [onnxruntime/core/providers/cuda/cuda_provider_factory.cc:206-224]()

### EP Information Structures

Each EP defines an info structure for configuration parameters. For CUDA EP, this is `CUDAExecutionProviderInfo`:

| Field | Type | Default | Purpose |
|-------|------|---------|---------|
| `device_id` | `int` | 0 | GPU device index |
| `gpu_mem_limit` | `size_t` | max | Maximum GPU memory for arena |
| `arena_extend_strategy` | enum | kNextPowerOfTwo | How arena grows |
| `cudnn_conv_algo_search` | enum | EXHAUSTIVE | Conv algorithm selection |
| `enable_cuda_graph` | `bool` | false | Enable CUDA graph capture |
| `tunable_op.enable` | `bool` | false | Enable tunable ops |
| `prefer_nhwc` | `bool` | false | Prefer NHWC layout |

Configuration is typically parsed from `ProviderOptions` (string key-value pairs) into the info structure via `FromProviderOptions()`.

**Sources:** [onnxruntime/core/providers/cuda/cuda_execution_provider_info.h:48-105](), [onnxruntime/core/providers/cuda/cuda_execution_provider_info.cc:54-166]()

### Lifecycle Hooks

EPs can participate in session lifecycle through hooks:

```mermaid
stateDiagram-v2
    [*] --> Created: EP Constructor
    Created --> Initialized: Session.Initialize()
    Initialized --> RunStart: OnRunStart()
    RunStart --> Executing: Execute nodes
    Executing --> RunEnd: OnRunEnd(sync_stream)
    RunEnd --> Initialized: Next inference
    Initialized --> [*]: Session destroyed
    
    note right of RunStart
        CUDA: Begin graph capture
        if enabled and allowed
    end note
    
    note right of RunEnd
        CUDA: End graph capture
        or replay captured graph
        Sync stream if requested
    end note
```

The CUDA EP uses these hooks for CUDA graph management:
- `OnRunStart()`: Begins graph capture if conditions are met
- `OnRunEnd()`: Completes capture or replays existing graph

**Sources:** [onnxruntime/core/providers/cuda/cuda_execution_provider.cc:510-552](), [include/onnxruntime/core/framework/execution_provider.h:231-241]()

### Provider Priority and Fallback

When multiple EPs are registered, the graph partitioner processes them in registration order. Nodes claimed by higher-priority EPs are removed from consideration for lower-priority EPs. Nodes not claimed by any EP default to the CPU EP.

```mermaid
graph TB
    Graph["Computational Graph<br/>(all nodes)"]
    
    EP1["EP1: TensorRT<br/>(highest priority)"]
    EP2["EP2: CUDA"]
    EP3["EP3: CPU<br/>(fallback)"]
    
    Graph --> EP1
    Graph --> EP2
    Graph --> EP3
    
    EP1 --> Claimed1["Nodes claimed by TensorRT<br/>(optimizable subgraphs)"]
    
    Remaining1["Remaining nodes"] --> EP2
    EP2 --> Claimed2["Nodes claimed by CUDA<br/>(GPU kernels available)"]
    
    Remaining2["Remaining nodes"] --> EP3
    EP3 --> Claimed3["All remaining nodes<br/>(CPU fallback)"]
```

This ensures maximum hardware utilization while maintaining complete operator coverage through CPU fallback.

**Sources:** [onnxruntime/test/onnx/main.cc:484-522](), [onnxruntime/test/python/onnx_backend_test_series.py:177-178]()

---

