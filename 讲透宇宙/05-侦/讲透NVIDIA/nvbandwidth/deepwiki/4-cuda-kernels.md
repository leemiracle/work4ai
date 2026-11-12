<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/nvbandwidth · page 4 CUDA Kernels · fetched 2026-10-26 -->

# CUDA Kernels

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [kernels.cu](kernels.cu)
- [kernels.cuh](kernels.cuh)

</details>



## Purpose and Scope

This document describes the CUDA kernels implemented in the NVIDIA nvbandwidth tool. These kernels are the core computational components that execute on the GPU to measure memory bandwidth between different hardware components. They implement various memory transfer patterns and optimizations to achieve accurate bandwidth measurements for different scenarios.

For information about how these kernels are utilized in specific test cases, see [Test Cases](#5) and its child pages. For details on the memory copy framework that orchestrates these kernels, see [Memory Copy Framework](#3).

Sources: [kernels.cuh:17-39]()

## Kernel Architecture Overview

The nvbandwidth tool implements several specialized CUDA kernels that perform different types of memory operations:

```mermaid
flowchart TD
    subgraph "CUDA Kernels"
        direction TB
        MemCopy["Memory Copy Kernels"]
        Sync["Synchronization Kernels"]
        Latency["Latency Measurement Kernels"]
        MemOps["Memory Ops Kernels"]
    end

    MemCopy --> Simple["simpleCopyKernel"]
    MemCopy --> Striding["stridingMemcpyKernel"]
    MemCopy --> SplitWarp["splitWarpCopyKernel"]
    MemCopy --> Multicast["multicastCopyKernel"]
    
    Sync --> Spin["spinKernelDevice"]
    Sync --> MultiSpin["spinKernelDeviceMultistage"]
    
    Latency --> PtrChase["ptrChasingKernel"]
    
    MemOps --> Memset["memsetKernelDevice"]
    MemOps --> MemClear["memclearKernelByWarpParityDevice"]
    MemOps --> Memcmp["memcmpKernelDevice"]
    MemOps --> MCMemcmp["multicastMemcmpKernelDevice"]
```

Sources: [kernels.cu:20-399](), [kernels.cuh:27-39]()

## Memory Copy Kernels

Memory copy kernels are the primary components for bandwidth measurement. They implement different memory access patterns to measure bandwidth under various scenarios.

### Simple Copy Kernel

The `simpleCopyKernel` is a basic memory copy kernel used for smaller buffer sizes (less than the small buffer threshold). It uses cache global (CG) memory operations for data transfer.

```mermaid
sequenceDiagram
    participant Thread as "CUDA Thread"
    participant Source as "Source Memory"
    participant Dest as "Destination Memory"
    
    Note over Thread: "Thread assigned idx based on blockIdx and threadIdx"
    Thread->>Source: "__ldcg(src_uint4)" 
    Note over Source: "Cache-global load operation"
    Source-->>Thread: "Return data"
    Thread->>Dest: "__stcg(dst_uint4, data)"
    Note over Dest: "Cache-global store operation"
```

Sources: [kernels.cu:20-28](), [kernels.cu:183-222]()

### Striding Memcpy Kernel

The `stridingMemcpyKernel` is an optimized kernel for larger buffer sizes that uses a striding memory access pattern to maximize memory bandwidth. It employs techniques like memory pipelining and thread striding to achieve high throughput.

```mermaid
flowchart TD
    Thread["Thread with index 'from'"]
    Thread --> AdjustPointers["Adjust pointers\ndst += from\nsrc += from"]
    AdjustPointers --> LoopCount["Loop for loopCount iterations"]
    LoopCount --> BigChunk["Process big chunks in groups of 12"]
    BigChunk --> PipeLoad["Load 12 values in pipeline"]
    PipeLoad --> PipeStore["Store 12 values to destination"]
    PipeStore --> BigChunk
    BigChunk --> SmallChunk["Process remaining elements"]
    SmallChunk --> LoopCount
```

Sources: [kernels.cu:30-74](), [kernels.cu:183-222]()

### Split Warp Copy Kernel

The `splitWarpCopyKernel` performs a split warp copy by alternating copy directions across warps. This pattern is useful for maximizing bidirectional bandwidth between GPU components.

```mermaid
flowchart TD
    Thread["Thread with index 'idx'"]
    Thread --> CalcWarpID["Calculate globalWarpId = idx / warpSize"]
    CalcWarpID --> CheckParity{"Is globalWarpId odd?"}
    CheckParity -->|"Yes (odd warp)"| OddWarp["Copy from src to dst"]
    CheckParity -->|"No (even warp)"| EvenWarp["Copy from dst to src (reverse direction)"]
    OddWarp --> PerformCopy["Perform cache-global load and store"]
    EvenWarp --> PerformCopy
```

Sources: [kernels.cu:77-98](), [kernels.cu:224-242]()

### Multicast Copy Kernel

The `multicastCopyKernel` is specialized for architectures that support multicast memory operations (Hopper and later). It writes from regular memory to multicast memory regions.

```mermaid
flowchart TD
    Thread["Thread with offset based on block and thread ID"]
    Thread --> InitPointers["Initialize pointers to chunks"]
    InitPointers --> Loop["Loop for loopCount iterations"]
    Loop --> ResetPointers["Reset pointers to src and dst chunks"]
    ResetPointers --> InnerLoop["Process elements in chunks"]
    InnerLoop --> MulticastStore["mc_st_u32: Write using multimem.st.u32"]
    MulticastStore --> InnerLoop
    InnerLoop --> Loop
```

Sources: [kernels.cu:128-146](), [kernels.cu:244-259]()

## Latency Measurement Kernels

### Pointer Chasing Kernel

The `ptrChasingKernel` and its host-side wrapper `latencyPtrChaseKernel` implement a pointer chasing technique to measure memory latency. This approach forces serial memory accesses that cannot be parallelized, allowing accurate latency measurement.

```mermaid
sequenceDiagram
    participant Host as "Host Code"
    participant SM as "Streaming Multiprocessor"
    participant Memory as "GPU Memory"
    
    Host->>SM: "Launch ptrChasingKernel"
    Note over Host: "Record start time"
    SM->>Memory: "p = data"
    loop For i = 0 to accesses
        SM->>Memory: "Load p->next"
        Memory-->>SM: "Return next pointer"
        Note over SM: "p = p->next (serialize memory accesses)"
    end
    Host->>SM: "Synchronize"
    Note over Host: "Record end time\nCalculate latency"
```

Sources: [kernels.cu:100-111](), [kernels.cu:148-181]()

## Synchronization Kernels

### Spin Kernels

The nvbandwidth tool includes spin kernels for synchronization purposes:

1. `spinKernelDevice`: Simple spin kernel that waits until a latch variable is set or timeout occurs
2. `spinKernelDeviceMultistage`: Two-stage spin kernel for complex multi-node synchronization

```mermaid
flowchart TD
    subgraph "Single-stage Spin"
        S1["Start spinKernelDevice"]
        S2["Calculate endTime = clock64() + timeoutClocks"]
        S3{"*latch == 0?"}
        S4{"Timeout?"}
        S5["Exit kernel"]
        
        S1 --> S2 --> S3
        S3 -->|"Yes"| S4
        S4 -->|"No"| S3
        S4 -->|"Yes"| S5
        S3 -->|"No"| S5
    end
    
    subgraph "Two-stage Spin"
        M1["Start spinKernelDeviceMultistage"]
        M2{"latch1 provided?"}
        M3["Wait for latch1"]
        M4["Set latch2 = 1"]
        M5["Wait for latch2"]
        M6["Exit kernel"]
        
        M1 --> M2
        M2 -->|"Yes"| M3 --> M4 --> M5 --> M6
        M2 -->|"No"| M5
    end
```

Sources: [kernels.cu:261-331]()

## Memory Initialization and Verification Kernels

The nvbandwidth tool includes several kernels for memory pattern initialization and verification:

### Memory Pattern Operations

1. `memsetKernelDevice`: Sets memory to a specified pattern
2. `memcmpKernelDevice`: Compares memory with a specified pattern
3. `multicastMemcmpKernelDevice`: Compares multicast memory with a pattern
4. `memclearKernelByWarpParityDevice`: Clears memory locations based on warp parity

```mermaid
flowchart TD
    subgraph "Memory Pattern Operations"
        Memset["memsetKernelDevice:\nSet memory to pattern"]
        Memcmp["memcmpKernelDevice:\nVerify memory pattern"]
        McMemcmp["multicastMemcmpKernelDevice:\nVerify multicast memory pattern"]
        WarpClear["memclearKernelByWarpParityDevice:\nClear memory based on warp parity"]
    end
    
    OddWarp["Clear odd warp indexed locations"]
    EvenWarp["Clear even warp indexed locations"]
    
    WarpClear --> OddWarp
    WarpClear --> EvenWarp
```

Sources: [kernels.cu:333-447]()

## Kernel Preloading Mechanism

The nvbandwidth tool preloads all kernels on all devices at initialization to reduce kernel launch latency during measurements. This is implemented in the `preloadKernels` function.

```mermaid
sequenceDiagram
    participant Main as "Main Program"
    participant DevLoop as "Device Loop"
    participant CUDA as "CUDA Runtime"
    
    Main->>DevLoop: "preloadKernels(deviceCount)"
    loop For each device
        DevLoop->>CUDA: "cudaSetDevice(iDev)"
        Note over DevLoop: "Call cudaFuncGetAttributes for each kernel"
        DevLoop->>CUDA: "cudaFuncGetAttributes(&unused, &stridingMemcpyKernel)"
        DevLoop->>CUDA: "cudaFuncGetAttributes(&unused, &spinKernelDevice)"
        DevLoop->>CUDA: "cudaFuncGetAttributes(&unused, &...other kernels...)"
    end
```

Sources: [kernels.cu:449-465]()

## Kernel Selection Logic

The nvbandwidth tool selects the appropriate kernel based on buffer size and test requirements. The selection logic is primarily implemented in the `copyKernel` function.

```mermaid
flowchart TD
    Start["copyKernel() called"] --> SizeCheck{"copySize < smallBufferThreshold?"}
    SizeCheck -->|"Yes (small buffer)"| UseSimple["Use simpleCopyKernel"]
    SizeCheck -->|"No (large buffer)"| UseStriding["Use stridingMemcpyKernel"]
    
    UseSimple --> LaunchSimple["Launch with calculated\ngrid and block dimensions"]
    UseStriding --> CalcElements["Calculate elements and dimensions"]
    CalcElements --> LaunchStriding["Launch with adjusted parameters"]
    
    LaunchSimple --> Return["Return copied size"]
    LaunchStriding --> Return
```

The kernel selection table below summarizes when each kernel is used:

| Kernel Type | Function | Used When | Key Optimizations |
|-------------|----------|-----------|-------------------|
| Simple Copy | `simpleCopyKernel` | Buffer size < threshold | Basic cache-global ops |
| Striding Copy | `stridingMemcpyKernel` | Buffer size ≥ threshold | Memory pipelining, striding |
| Split Warp | `splitWarpCopyKernel` | Bidirectional tests | Alternating warp directions |
| Multicast | `multicastCopyKernel` | Multicast memory tests | Hopper+ multimem ops |

Sources: [kernels.cu:183-222](), [kernels.cu:224-242](), [kernels.cu:244-259]()

## Technical Implementation Details

### Key Parameters and Constants

| Constant | Value | Purpose |
|----------|-------|---------|
| `numThreadPerBlock` | Varies | Threads per block for memory copy |
| `smallBufferThreshold` | Defined in MiB | Threshold for kernel selection |
| `DEFAULT_SPIN_KERNEL_TIMEOUT_MS` | 10000 (10s) | Default timeout for spin kernels |

### Memory Access Instructions

The kernels use specific memory access instructions for optimal performance:

- `__ldcg()`: Cache-global load instruction that caches data globally
- `__stcg()`: Cache-global store instruction that caches data globally
- `multimem.st.u32`: Hopper architecture's multicast store instruction
- `multimem.ld_reduce.and.b32`: Hopper architecture's multicast load instruction

Sources: [kernels.cu:20-28](), [kernels.cu:113-125]()

## Integration with Memory Copy Framework

The CUDA kernels are integrated with the Memory Copy Framework through kernel wrapper functions like `copyKernel`, `copyKernelSplitWarp`, and `multicastCopy`. These functions take a `MemcpyDescriptor` structure or similar parameters and handle the details of launching the appropriate kernel with the right parameters.

```mermaid
classDiagram
    class MemcpyDescriptor {
        CUdeviceptr src
        CUdeviceptr dst
        size_t copySize
        unsigned long long loopCount
        CUstream stream
    }
    
    class MemcpyInitiator {
        <<interface>>
        +memcpyFunc(MemcpyDescriptor&)
    }
    
    class MemcpyInitiatorSM {
        +memcpyFunc(MemcpyDescriptor&)
    }
    
    class MemcpyInitiatorCE {
        +memcpyFunc(MemcpyDescriptor&)
    }
    
    MemcpyInitiator <|.. MemcpyInitiatorSM
    MemcpyInitiator <|.. MemcpyInitiatorCE
    MemcpyInitiator --> MemcpyDescriptor: uses
    MemcpyInitiatorSM ..> copyKernel: calls
    MemcpyInitiatorCE ..> copyKernel: calls
```

Sources: [kernels.cu:183-222](), [kernels.cuh:27-39]()

---

