> 来源: [https://deepwiki.com/triton-lang/triton/3-mlir-dialects-and-ir-system](https://deepwiki.com/triton-lang/triton/3-mlir-dialects-and-ir-system)
> DeepWiki triton-lang/triton | Last indexed: 20 August 2026 (f89384

# MLIR Dialects and IR System

  Relevant source files 
 - [include/triton/Dialect/TritonGPU/IR/Dialect.h](https://github.com/triton-lang/triton/blob/f893845b/include/triton/Dialect/TritonGPU/IR/Dialect.h)
 - [include/triton/Dialect/TritonGPU/IR/LinearLayoutConversions.h](https://github.com/triton-lang/triton/blob/f893845b/include/triton/Dialect/TritonGPU/IR/LinearLayoutConversions.h)
 - [include/triton/Dialect/TritonGPU/IR/TritonGPUAttrDefs.td](https://github.com/triton-lang/triton/blob/f893845b/include/triton/Dialect/TritonGPU/IR/TritonGPUAttrDefs.td)
 - [include/triton/Dialect/TritonGPU/IR/TritonGPUOps.td](https://github.com/triton-lang/triton/blob/f893845b/include/triton/Dialect/TritonGPU/IR/TritonGPUOps.td)
 - [lib/Conversion/TritonGPUToLLVM/ViewOpToLLVM.cpp](https://github.com/triton-lang/triton/blob/f893845b/lib/Conversion/TritonGPUToLLVM/ViewOpToLLVM.cpp)
 - [lib/Dialect/TritonGPU/IR/Dialect.cpp](https://github.com/triton-lang/triton/blob/f893845b/lib/Dialect/TritonGPU/IR/Dialect.cpp)
 - [lib/Dialect/TritonGPU/IR/LinearLayoutConversions.cpp](https://github.com/triton-lang/triton/blob/f893845b/lib/Dialect/TritonGPU/IR/LinearLayoutConversions.cpp)
 - [lib/Dialect/TritonGPU/IR/Ops.cpp](https://github.com/triton-lang/triton/blob/f893845b/lib/Dialect/TritonGPU/IR/Ops.cpp)
 - [lib/Dialect/TritonGPU/IR/Types.cpp](https://github.com/triton-lang/triton/blob/f893845b/lib/Dialect/TritonGPU/IR/Types.cpp)
 - [test/TritonGPU/invalid.mlir](https://github.com/triton-lang/triton/blob/f893845b/test/TritonGPU/invalid.mlir)
 - [test/TritonGPU/ops.mlir](https://github.com/triton-lang/triton/blob/f893845b/test/TritonGPU/ops.mlir)
 - [unittest/Dialect/TritonGPU/DialectTest.cpp](https://github.com/triton-lang/triton/blob/f893845b/unittest/Dialect/TritonGPU/DialectTest.cpp)
 - [unittest/Dialect/TritonGPU/LinearLayoutConversionsTest.cpp](https://github.com/triton-lang/triton/blob/f893845b/unittest/Dialect/TritonGPU/LinearLayoutConversionsTest.cpp)
 
  This document provides an overview of the MLIR-based intermediate representation (IR) system used in Triton. It introduces the dialect hierarchy, core concepts like operations and layout encodings, and explains how the IR progressively lowers from high-level tensor operations to GPU-specific representations.

 For details on specific operations in the Triton dialect, see [Triton Dialect (TTIR)](https://deepwiki.com/triton-lang/triton/3.1-triton-dialect-(ttir)). For GPU-specific transformations and layout propagation, see [TritonGPU Dialect and Layout System](https://deepwiki.com/triton-lang/triton/3.2-tritongpu-dialect-and-layout-system). For in-depth coverage of layout encodings, see [Layout Encoding Attributes](https://deepwiki.com/triton-lang/triton/3.3-layout-encoding-attributes) and [LinearLayout System](https://deepwiki.com/triton-lang/triton/3.4-linearlayout-system).

 
---

 
## MLIR Dialect Hierarchy

 Triton uses a layered dialect architecture where each dialect represents a progressively lower level of abstraction. The compilation flow moves through three primary IR stages:

 
```

```

 **Figure 1: MLIR Dialect Hierarchy in Triton**

 Sources: [lib/Dialect/TritonGPU/IR/Dialect.cpp1-20](https://github.com/triton-lang/triton/blob/f893845b/lib/Dialect/TritonGPU/IR/Dialect.cpp#L1-L20) [include/triton/Dialect/TritonGPU/IR/Dialect.h10-15](https://github.com/triton-lang/triton/blob/f893845b/include/triton/Dialect/TritonGPU/IR/Dialect.h#L10-L15)

 
### Triton Dialect (tt.*)

 The Triton dialect (`tt.*`) provides hardware-agnostic operations for tensor programming. At this level, tensors are abstract mathematical objects with shape and element type.

 
 - **Memory operations**: `tt.load`, `tt.store` [lib/Dialect/TritonGPU/IR/Ops.cpp74-83](https://github.com/triton-lang/triton/blob/f893845b/lib/Dialect/TritonGPU/IR/Ops.cpp#L74-L83)
 - **Compute operations**: `tt.dot`, `tt.reduce`, `tt.scan` [lib/Dialect/TritonGPU/IR/Dialect.cpp12-13](https://github.com/triton-lang/triton/blob/f893845b/lib/Dialect/TritonGPU/IR/Dialect.cpp#L12-L13)
 - **Shape manipulation**: `tt.trans`, `tt.reshape`, `tt.join`, `tt.split` [lib/Dialect/TritonGPU/IR/Ops.cpp113-173](https://github.com/triton-lang/triton/blob/f893845b/lib/Dialect/TritonGPU/IR/Ops.cpp#L113-L173)
 
 Sources: [lib/Dialect/TritonGPU/IR/Ops.cpp4-15](https://github.com/triton-lang/triton/blob/f893845b/lib/Dialect/TritonGPU/IR/Ops.cpp#L4-L15) [lib/Dialect/TritonGPU/IR/Dialect.cpp1-15](https://github.com/triton-lang/triton/blob/f893845b/lib/Dialect/TritonGPU/IR/Dialect.cpp#L1-L15)

 
### TritonGPU Dialect (ttg.*)

 The TritonGPU dialect (`ttg.*`) extends Triton operations with **layout encodings** that describe how tensor elements are distributed across GPU threads, warps, and CTAs.

 
 - `ttg.convert_layout`: The primary operation for changing tensor layout [include/triton/Dialect/TritonGPU/IR/TritonGPUOps.td32-46](https://github.com/triton-lang/triton/blob/f893845b/include/triton/Dialect/TritonGPU/IR/TritonGPUOps.td#L32-L46)
 - `ttg.local_alloc` / `ttg.local_dealloc`: Shared memory management [include/triton/Dialect/TritonGPU/IR/TritonGPUOps.td153-176](https://github.com/triton-lang/triton/blob/f893845b/include/triton/Dialect/TritonGPU/IR/TritonGPUOps.td#L153-L176)
 - `ttg.async_copy_global_to_local`: Asynchronous memory copy from global to shared memory [include/triton/Dialect/TritonGPU/IR/TritonGPUOps.td91-150](https://github.com/triton-lang/triton/blob/f893845b/include/triton/Dialect/TritonGPU/IR/TritonGPUOps.td#L91-L150)
 
 The dialect introduces **encoding attributes** attached to tensor types that specify data distribution [lib/Dialect/TritonGPU/IR/Dialect.cpp46-72](https://github.com/triton-lang/triton/blob/f893845b/lib/Dialect/TritonGPU/IR/Dialect.cpp#L46-L72)

 Sources: [include/triton/Dialect/TritonGPU/IR/TritonGPUOps.td27-180](https://github.com/triton-lang/triton/blob/f893845b/include/triton/Dialect/TritonGPU/IR/TritonGPUOps.td#L27-L180) [lib/Dialect/TritonGPU/IR/Dialect.cpp46-60](https://github.com/triton-lang/triton/blob/f893845b/lib/Dialect/TritonGPU/IR/Dialect.cpp#L46-L60)

 
### Vendor-Specific Dialects

 **TritonNvidiaGPU (ttng.*)**: NVIDIA-specific extensions for architectures like Hopper and Blackwell. It handles hardware-specific features like `TMEM` and `TMA` [lib/Dialect/TritonGPU/IR/LinearLayoutConversions.cpp18-20](https://github.com/triton-lang/triton/blob/f893845b/lib/Dialect/TritonGPU/IR/LinearLayoutConversions.cpp#L18-L20) [lib/Dialect/TritonGPU/IR/Ops.cpp88-111](https://github.com/triton-lang/triton/blob/f893845b/lib/Dialect/TritonGPU/IR/Ops.cpp#L88-L111)

 **TritonAMDGPU**: AMD-specific extensions for CDNA and RDNA architectures, including `AMDMfmaEncodingAttr` and `AMDWmmaEncodingAttr` support [include/triton/Dialect/TritonGPU/IR/TritonGPUAttrDefs.td123-134](https://github.com/triton-lang/triton/blob/f893845b/include/triton/Dialect/TritonGPU/IR/TritonGPUAttrDefs.td#L123-L134)

 Sources: [lib/Dialect/TritonGPU/IR/Ops.cpp88-111](https://github.com/triton-lang/triton/blob/f893845b/lib/Dialect/TritonGPU/IR/Ops.cpp#L88-L111) [include/triton/Dialect/TritonGPU/IR/TritonGPUAttrDefs.td120-140](https://github.com/triton-lang/triton/blob/f893845b/include/triton/Dialect/TritonGPU/IR/TritonGPUAttrDefs.td#L120-L140)

 
---

 
## Core IR Concepts

 
### Operations

 Operations are defined using TableGen. Each Triton operation can have:

 
```

```

 **Figure 2: Operation Structure and Code Entities**

 Example: `TTG_ConvertLayoutOp` uses `SameOperandsAndResultShape` and `Pure` traits [include/triton/Dialect/TritonGPU/IR/TritonGPUOps.td32-35](https://github.com/triton-lang/triton/blob/f893845b/include/triton/Dialect/TritonGPU/IR/TritonGPUOps.td#L32-L35)

 Sources: [include/triton/Dialect/TritonGPU/IR/TritonGPUOps.td32-46](https://github.com/triton-lang/triton/blob/f893845b/include/triton/Dialect/TritonGPU/IR/TritonGPUOps.td#L32-L46) [lib/Dialect/TritonGPU/IR/Ops.cpp45-70](https://github.com/triton-lang/triton/blob/f893845b/lib/Dialect/TritonGPU/IR/Ops.cpp#L45-L70)

 
### Types and Layouts

 Triton uses standard MLIR `RankedTensorType` but enriches it with encoding attributes [lib/Dialect/TritonGPU/IR/Dialect.cpp68-72](https://github.com/triton-lang/triton/blob/f893845b/lib/Dialect/TritonGPU/IR/Dialect.cpp#L68-L72) It also introduces `MemDescType` for shared memory buffers [include/triton/Dialect/TritonGPU/IR/LinearLayoutConversions.h18-19](https://github.com/triton-lang/triton/blob/f893845b/include/triton/Dialect/TritonGPU/IR/LinearLayoutConversions.h#L18-L19)

 
| Attribute Class | Description | Code Symbol |
|---|---|---|
| Blocked | Distributed layout for general elementwise ops | BlockedEncodingAttr |
| MMA | Hardware-specific matrix-multiply layouts | NvidiaMmaEncodingAttr |
| Shared | Shared memory layout with swizzling | SwizzledSharedEncodingAttr |
| Linear | Canonical representation for all layouts | LinearEncodingAttr |

 Sources: [include/triton/Dialect/TritonGPU/IR/TritonGPUAttrDefs.td10-14](https://github.com/triton-lang/triton/blob/f893845b/include/triton/Dialect/TritonGPU/IR/TritonGPUAttrDefs.td#L10-L14) [lib/Dialect/TritonGPU/IR/Dialect.cpp46-58](https://github.com/triton-lang/triton/blob/f893845b/lib/Dialect/TritonGPU/IR/Dialect.cpp#L46-L58) [include/triton/Dialect/TritonGPU/IR/LinearLayoutConversions.h50-52](https://github.com/triton-lang/triton/blob/f893845b/include/triton/Dialect/TritonGPU/IR/LinearLayoutConversions.h#L50-L52)

 
---

 
## Layout System Overview

 The **layout system** determines how data maps to hardware. A layout encoding specifies how indices are mapped to threads and registers.

 
### Distributed Layout Example

 
```

```

 **Figure 3: Logical to Hardware Mapping**

 Sources: [include/triton/Dialect/TritonGPU/IR/Dialect.h181-193](https://github.com/triton-lang/triton/blob/f893845b/include/triton/Dialect/TritonGPU/IR/Dialect.h#L181-L193) [unittest/Dialect/TritonGPU/LinearLayoutConversionsTest.cpp31-38](https://github.com/triton-lang/triton/blob/f893845b/unittest/Dialect/TritonGPU/LinearLayoutConversionsTest.cpp#L31-L38)

 
### Layout Inference

 The compiler provides interfaces to infer result layouts for operations like `reshape` or `fp4_to_fp` [lib/Dialect/TritonGPU/IR/Dialect.cpp167-188](https://github.com/triton-lang/triton/blob/f893845b/lib/Dialect/TritonGPU/IR/Dialect.cpp#L167-L188) This ensures that transformations maintain correct data distribution semantics across the IR.

 Sources: [lib/Dialect/TritonGPU/IR/Dialect.cpp167-188](https://github.com/triton-lang/triton/blob/f893845b/lib/Dialect/TritonGPU/IR/Dialect.cpp#L167-L188) [unittest/Dialect/TritonGPU/DialectTest.cpp122-150](https://github.com/triton-lang/triton/blob/f893845b/unittest/Dialect/TritonGPU/DialectTest.cpp#L122-L150)

 
---

 
## LinearLayout System

 The `LinearLayout` is the canonical representation used for complex conversions and analysis. It treats layouts as a linear mapping between input dimensions (register, lane, warp, block) and output dimensions (tensor axes) [include/triton/Dialect/TritonGPU/IR/LinearLayoutConversions.h23-45](https://github.com/triton-lang/triton/blob/f893845b/include/triton/Dialect/TritonGPU/IR/LinearLayoutConversions.h#L23-L45)

 Key utilities:

 
 - `toLinearLayout`: Converts any encoding to its linear form [include/triton/Dialect/TritonGPU/IR/LinearLayoutConversions.h50-56](https://github.com/triton-lang/triton/blob/f893845b/include/triton/Dialect/TritonGPU/IR/LinearLayoutConversions.h#L50-L56)
 - `isPermutationMatrixLayout`: Checks if a layout is a simple permutation of data [lib/Dialect/TritonGPU/IR/Dialect.cpp83-89](https://github.com/triton-lang/triton/blob/f893845b/lib/Dialect/TritonGPU/IR/Dialect.cpp#L83-L89)
 - `hasPowerOfTwoBases`: Verifies layout regularity for efficient lowering [lib/Dialect/TritonGPU/IR/Dialect.cpp74-81](https://github.com/triton-lang/triton/blob/f893845b/lib/Dialect/TritonGPU/IR/Dialect.cpp#L74-L81)
 
 Sources: [lib/Dialect/TritonGPU/IR/Dialect.cpp46-112](https://github.com/triton-lang/triton/blob/f893845b/lib/Dialect/TritonGPU/IR/Dialect.cpp#L46-L112) [include/triton/Dialect/TritonGPU/IR/LinearLayoutConversions.h1-103](https://github.com/triton-lang/triton/blob/f893845b/include/triton/Dialect/TritonGPU/IR/LinearLayoutConversions.h#L1-L103)

 
---

 
## Memory Descriptors

 `MemDescType` is used to describe shared memory allocations. Unlike standard tensors, memory descriptors explicitly handle:

 
 - **Memory Space**: Typically `SharedMemory` [include/triton/Dialect/TritonGPU/IR/Dialect.h100-103](https://github.com/triton-lang/triton/blob/f893845b/include/triton/Dialect/TritonGPU/IR/Dialect.h#L100-L103)
 - **Mutability**: Whether the buffer can be written to [include/triton/Dialect/TritonGPU/IR/TritonGPUOps.td163-164](https://github.com/triton-lang/triton/blob/f893845b/include/triton/Dialect/TritonGPU/IR/TritonGPUOps.td#L163-L164)
 - **Allocation Shape**: The physical shape in memory, which may differ from the logical view [test/TritonGPU/ops.mlir78-81](https://github.com/triton-lang/triton/blob/f893845b/test/TritonGPU/ops.mlir#L78-L81)
 
 Sources: [include/triton/Dialect/TritonGPU/IR/TritonGPUOps.td153-176](https://github.com/triton-lang/triton/blob/f893845b/include/triton/Dialect/TritonGPU/IR/TritonGPUOps.td#L153-L176) [test/TritonGPU/ops.mlir71-82](https://github.com/triton-lang/triton/blob/f893845b/test/TritonGPU/ops.mlir#L71-L82)

 
---

 
## Summary of Dialect Capabilities

 
| Dialect | Key Responsibility | Primary Operations |
|---|---|---|
| Triton (tt) | Functional semantics | load, store, dot, reduce |
| TritonGPU (ttg) | Data distribution | convert_layout, local_alloc, async_copy |
| TritonNvidiaGPU | NVIDIA hardware features | TMEMStoreOp, TMA utilities |

 For more detail, refer to the child pages:

 
 - [Triton Dialect (TTIR)](https://deepwiki.com/triton-lang/triton/3.1-triton-dialect-(ttir))
 - [TritonGPU Dialect and Layout System](https://deepwiki.com/triton-lang/triton/3.2-tritongpu-dialect-and-layout-system)
 - [Layout Encoding Attributes](https://deepwiki.com/triton-lang/triton/3.3-layout-encoding-attributes)
 - [LinearLayout System](https://deepwiki.com/triton-lang/triton/3.4-linearlayout-system)
 - [Memory Descriptors and Shared Memory Layouts](https://deepwiki.com/triton-lang/triton/3.5-memory-descriptors-and-shared-memory-layouts)
 
 Sources: [include/triton/Dialect/TritonGPU/IR/TritonGPUOps.td1-180](https://github.com/triton-lang/triton/blob/f893845b/include/triton/Dialect/TritonGPU/IR/TritonGPUOps.td#L1-L180) [lib/Dialect/TritonGPU/IR/Dialect.cpp1-100](https://github.com/triton-lang/triton/blob/f893845b/lib/Dialect/TritonGPU/IR/Dialect.cpp#L1-L100)
