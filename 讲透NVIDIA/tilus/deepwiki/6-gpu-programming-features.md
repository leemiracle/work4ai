<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/tilus · page 6 GPU Programming Features · fetched 2026-10-26 -->

# GPU Programming Features

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [python/tilus/extensions/hidet/ir/primitives/cuda/tcgen05.py](python/tilus/extensions/hidet/ir/primitives/cuda/tcgen05.py)
- [python/tilus/ir/instructions/cuda/tmem.py](python/tilus/ir/instructions/cuda/tmem.py)
- [python/tilus/ir/layout/inference/inference_rules/__init__.py](python/tilus/ir/layout/inference/inference_rules/__init__.py)
- [python/tilus/ir/layout/inference/inference_rules/mma_dot.py](python/tilus/ir/layout/inference/inference_rules/mma_dot.py)
- [python/tilus/ir/layout/inference/inference_rules/tmem_ldst.py](python/tilus/ir/layout/inference/inference_rules/tmem_ldst.py)
- [python/tilus/ir/layout/inference/order.py](python/tilus/ir/layout/inference/order.py)
- [python/tilus/ir/layout/inference/validation_rules/always_ok.py](python/tilus/ir/layout/inference/validation_rules/always_ok.py)
- [tests/ir/layout/register_layout/test_layout_divide.py](tests/ir/layout/register_layout/test_layout_divide.py)

</details>



This document covers the GPU-specific programming features and optimizations available in Tilus. It focuses on the low-level primitives, memory management, instruction system, and layout inference that enable efficient GPU kernel development. For high-level kernel programming patterns, see [Programming Guide](#5). For memory layout specifics, see [Memory Layout System](#6.1). For instruction implementation details, see [Instruction System](#6.2).

## Memory Hierarchy and Tensor Types

Tilus provides explicit support for the GPU memory hierarchy through distinct tensor types that correspond to different memory spaces. Each tensor type has specific characteristics and usage patterns optimized for its memory domain.

### Tensor Type System

```mermaid
graph TB
    subgraph "Memory Domains"
        A[GlobalTensor] --> A1["Global Memory<br/>Large capacity<br/>High latency<br/>Cross-device access"]
        B[SharedTensor] --> B1["Shared Memory<br/>Fast access<br/>Block-scoped<br/>Bank conflicts possible"]
        C[RegisterTensor] --> C1["Register Memory<br/>Fastest access<br/>Thread-local<br/>Limited capacity"]
        D[TMemoryTensor] --> D1["Tensor Memory<br/>SM90+ hardware<br/>128 lanes<br/>TCGEN05 operations"]
    end
    
    subgraph "Layout Systems"
        E[GlobalLayout] --> E1["Strided access patterns"]
        F[SharedLayout] --> F1["Bank conflict avoidance<br/>Swizzling patterns"]
        G[RegisterLayout] --> G1["Spatial/Local modes<br/>Thread distribution"]
        H[TMemoryLayout] --> H1["Hardware-defined<br/>128-lane structure"]
    end
    
    A --> E
    B --> F
    C --> G
    D --> H
```

**Memory Hierarchy Architecture**

Sources: [python/tilus/ir/tensor.py](), [python/tilus/ir/layout/](), [python/tilus/ir/instructions/cuda/tmem.py:24-25]()

### Memory Operations and Data Movement

The system provides optimized operations for moving data between memory hierarchies:

```mermaid
graph LR
    subgraph "Async Copy Operations"
        A[CopyAsyncGenericInst] --> A1["Generic async copy"]
        B[CopyAsyncInst] --> B1["Standard async copy"]
        C[CopyAsyncBulkGlobalToSharedInst] --> C1["Bulk global→shared"]
        D[CopyAsyncBulkSharedToGlobalInst] --> D1["Bulk shared→global"]
        E[CopyAsyncTensorGlobalToSharedInst] --> E1["Tensor global→shared"]
        F[CopyAsyncTensorSharedToGlobalInst] --> F1["Tensor shared→global"]
    end
    
    subgraph "Load/Store Operations"
        G[LoadGlobalInst] --> G1["Global memory load"]
        H[StoreGlobalInst] --> H1["Global memory store"]
        I[LoadSharedInst] --> I1["Shared memory load"]
        J[StoreSharedInst] --> J1["Shared memory store"]
        K[TMemoryLoadInst] --> K1["Tensor memory load"]
        L[TMemoryStoreInst] --> L1["Tensor memory store"]
    end
```

**Memory Operation Instruction Types**

Sources: [python/tilus/ir/layout/inference/validation_rules/always_ok.py:15-43](), [python/tilus/ir/instructions/cuda/tmem.py:89-114]()

## Layout Inference System

Tilus employs a sophisticated layout inference system that automatically determines optimal memory layouts for tensors based on their usage patterns and hardware constraints.

### Layout Inference Rules Architecture

```mermaid
graph TB
    subgraph "Rule Categories"
        A[MmaDotRule] --> A1["Tensor core operations<br/>MMA layout constraints"]
        B[TMemoryLoadRule] --> B1["TCGEN05 operations<br/>128-lane patterns"]
        C[LoadGlobalRule] --> C1["Global memory access<br/>Coalescing optimization"]
        D[BinaryRule] --> D1["Element-wise operations<br/>Broadcasting patterns"]
        E[ReduceRule] --> E1["Reduction operations<br/>Warp-level primitives"]
        F[TransposeRule] --> F1["Matrix transpose<br/>Layout transformation"]
    end
    
    subgraph "Inference Order"
        G["Priority 0: MMA Operations"] --> H["Priority 1: TMemory Operations"]
        H --> I["Priority 2: Binary/Unary Operations"]
        I --> J["Priority 3: Global Memory"]
        J --> K["Priority 4: Shared Memory"]
        K --> L["Priority 5: Transform Operations"]
    end
    
    A --> G
    B --> H
    C --> J
    D --> I
```

**Layout Inference Priority System**

The inference system processes rules in a specific order to ensure hardware constraints are satisfied first, followed by optimization opportunities.

Sources: [python/tilus/ir/layout/inference/order.py:42-61](), [python/tilus/ir/layout/inference/inference_rules/]()

### Validation Rules System

```mermaid
graph LR
    subgraph "Validation Framework"
        A[LayoutValidationRule] --> B[register_rule]
        B --> C[AlwaysOkayRule]
        C --> D["validate() method"]
    end
    
    subgraph "Instruction Coverage"
        E[TMemoryLoadInst] --> F[AlwaysOkayRule]
        G[CopyAsyncInst] --> F
        H[LoadGlobalInst] --> F
        I[StoreSharedInst] --> F
        J[MMA operations] --> K["Dedicated rules"]
    end
```

**Layout Validation Architecture**

Sources: [python/tilus/ir/layout/inference/validation_rules/always_ok.py:47-82]()

## CUDA-Specific Hardware Primitives

Tilus provides direct access to CUDA hardware primitives for maximum performance, particularly on modern GPU architectures.

### Tensor Core (MMA) Operations

```mermaid
graph TB
    subgraph "MMA Configuration System"
        A[DotInst] --> B[AtomicMmaConfig]
        B --> C["operand_type<br/>acc_type<br/>num_warps"]
        C --> D["la: A operand layout<br/>lb: B operand layout<br/>lc: accumulator layout"]
    end
    
    subgraph "Layout Inference"
        E["MmaDotRule.generate_default_layouts()"] --> F["cuda.resolve_dot_config()"]
        F --> G["Hardware-optimal layouts"]
        G --> H["Warp-level distribution"]
    end
    
    subgraph "Validation Process"
        I["get_atom_config_from_layout_d()"] --> J["divide(layout, config.layout)"]
        J --> K["Layout compatibility check"]
    end
    
    A --> E
    B --> I
```

**MMA Operation Configuration**

Sources: [python/tilus/ir/layout/inference/inference_rules/mma_dot.py:23-98](), [python/tilus/ir/instructions/cuda/mma_dot.py]()

### TCGEN05 Tensor Memory Operations

TCGEN05 provides advanced tensor memory capabilities on SM90+ hardware:

```mermaid
graph TB
    subgraph "TCGEN05 Operations"
        A[tcgen05_alloc] --> A1["Memory allocation<br/>CTA group: 1 or 2"]
        B[tcgen05_dealloc] --> B1["Memory deallocation<br/>Address + columns"]
        C[tcgen05_load] --> C1["Tensor load<br/>Multiple shapes/formats"]
        D[tcgen05_store] --> D1["Tensor store<br/>Register to TMemory"]
        E[tcgen05_copy] --> E1["Direct copy<br/>Multicast support"]
        F[tcgen05_commit] --> F1["Barrier commit<br/>Cluster synchronization"]
    end
    
    subgraph "Shape Configurations"
        G[R16x64B] --> G1["16 rows × 64 bits"]
        H[R16x128B] --> H1["16 rows × 128 bits"]
        I[R16x256B] --> I1["16 rows × 256 bits"]
        J[R32x32B] --> J1["32 rows × 32 bits"]
    end
    
    subgraph "Advanced Features"
        K[Multicast] --> K1["WARP_X2_02_13<br/>WARP_X2_01_23<br/>WARP_X4"]
        L[Pack] --> L1["PACK_16B<br/>Register optimization"]
        M[CTA_Group] --> M1["Single CTA: .cta_group::1<br/>Dual CTA: .cta_group::2"]
    end
    
    C --> G
    C --> H
    C --> I
    C --> J
    
    E --> K
    C --> L
    A --> M
```

**TCGEN05 Hardware Primitive System**

Sources: [python/tilus/extensions/hidet/ir/primitives/cuda/tcgen05.py:27-498]()

### TMemory Layout Inference

```mermaid
graph LR
    subgraph "TMemory Layout Process"
        A[TMemoryTensor] --> B[TMemoryLdstRule]
        B --> C["get_register_layout()"]
        C --> D["Shape analysis<br/>R16x64B, R16x128B, etc."]
        D --> E["Thread distribution<br/>intra_warp/inter_warp"]
        E --> F["get_ldst_layout()"]
        F --> G["Final RegisterLayout"]
    end
    
    subgraph "Layout Components"
        H["local(1, columns_repeat)"] --> I["spatial(inter_warp_rows, 1)"]
        I --> J["local(intra_warp_rows, 1)"]
        J --> K["atom layout * vectorization"]
    end
    
    C --> H
```

**TMemory Layout Inference Process**

Sources: [python/tilus/ir/layout/inference/inference_rules/tmem_ldst.py:29-109]()

## Instruction System Architecture

The instruction system provides a hierarchical organization of GPU operations, from generic memory operations to hardware-specific primitives.

### Instruction Hierarchy

| Instruction Category | Examples | Purpose |
|---------------------|----------|---------|
| Memory Allocation | `AllocateSharedInst`, `TMemoryAllocInst` | Resource management |
| Data Movement | `LoadGlobalInst`, `StoreSharedInst`, `CopyAsyncInst` | Memory hierarchy operations |
| Compute Operations | `DotInst`, MMA instructions | Mathematical computations |
| Hardware Primitives | TCGEN05 instructions, barriers | Low-level hardware access |
| Control Flow | Synchronization, barriers | Thread coordination |

### CUDA-Specific Instruction Extensions

```mermaid
graph TB
    subgraph "Base Instructions"
        A[Instruction] --> B[LoadGlobalInst]
        A --> C[StoreSharedInst]
        A --> D[DotInst]
    end
    
    subgraph "CUDA Extensions"
        E[CopyAsyncBulkGlobalToSharedInst] --> F["Bulk async copy<br/>Hardware-accelerated"]
        G[TMemoryLoadInst] --> H["TCGEN05 load<br/>128-lane access"]
        I[Tcgen05CopyInst] --> J["Direct tensor copy<br/>Multicast capable"]
    end
    
    subgraph "Hardware Features"
        K["Async Operations"] --> L["Non-blocking transfers<br/>Pipeline overlap"]
        M["Tensor Cores"] --> N["MMA operations<br/>Mixed precision"]
        O["TMA (Tensor Memory)"] --> P["SM90+ hardware<br/>Cluster operations"]
    end
    
    E --> K
    G --> O
    D --> M
```

**CUDA Instruction Extension Architecture**

Sources: [python/tilus/ir/instructions/](), [python/tilus/ir/instructions/cuda/]()

## Layout Operation Framework

Tilus provides a comprehensive set of layout operations for manipulating tensor memory patterns.

### Core Layout Operations

```mermaid
graph LR
    subgraph "Layout Operations"
        A[divide] --> A1["Layout division<br/>Pattern extraction"]
        B[spatial] --> B1["Spatial dimensions<br/>Thread distribution"]
        C[local] --> C1["Local dimensions<br/>Per-thread data"]
        D[reduce_to] --> D1["Dimension reduction<br/>Layout simplification"]
    end
    
    subgraph "Layout Types"
        E[RegisterLayout] --> E1["Thread-local patterns<br/>Spatial + Local modes"]
        F[SharedLayout] --> F1["Block-shared patterns<br/>Swizzling support"]
        G[GlobalLayout] --> G1["Strided access<br/>Memory coalescing"]
    end
    
    subgraph "Operations"
        H["lhs / rhs → divide(lhs, rhs)"] --> I["spatial(2,4) / spatial(1,2) → spatial(2,2)"]
        J["local(1, k) * config.la"] --> K["Layout composition"]
    end
```

**Layout Operation System**

Sources: [tests/ir/layout/register_layout/test_layout_divide.py:19-36](), [python/tilus/ir/layout/ops.py]()

## Performance Optimization Features

### Hardware-Aware Optimizations

1. **Memory Coalescing**: Automatic layout inference ensures optimal global memory access patterns
2. **Bank Conflict Avoidance**: Shared memory layouts use swizzling to minimize bank conflicts  
3. **Tensor Core Utilization**: MMA operations automatically select optimal tensor core configurations
4. **Async Pipeline**: Non-blocking memory transfers enable computation/communication overlap
5. **Register Optimization**: Layout system minimizes register pressure through efficient data distribution

### Target-Specific Features

| GPU Architecture | Supported Features |
|-----------------|-------------------|
| SM80 | Tensor cores, async copy, shared memory optimization |
| SM90 | All SM80 features + TCGEN05, tensor memory, cluster operations |
| Future architectures | Extensible through target system |

The GPU programming features in Tilus provide a comprehensive foundation for implementing high-performance GPU kernels while maintaining code clarity and optimization opportunities through automatic layout inference and hardware-specific primitive access.

Sources: [python/tilus/ir/layout/](), [python/tilus/ir/instructions/](), [python/tilus/extensions/hidet/ir/primitives/cuda/]()

---

