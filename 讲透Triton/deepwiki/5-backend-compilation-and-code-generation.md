> 来源: [https://deepwiki.com/triton-lang/triton/5-backend-compilation-and-code-generation](https://deepwiki.com/triton-lang/triton/5-backend-compilation-and-code-generation)
> DeepWiki triton-lang/triton | Last indexed: 20 August 2026 (f89384

# Backend Compilation and Code Generation

  Relevant source files 
 - [include/triton/Conversion/TritonGPUToLLVM/PatternTritonGPUOpToLLVM.h](https://github.com/triton-lang/triton/blob/f893845b/include/triton/Conversion/TritonGPUToLLVM/PatternTritonGPUOpToLLVM.h)
 - [include/triton/Conversion/TritonGPUToLLVM/Utility.h](https://github.com/triton-lang/triton/blob/f893845b/include/triton/Conversion/TritonGPUToLLVM/Utility.h)
 - [lib/Conversion/TritonGPUToLLVM/CMakeLists.txt](https://github.com/triton-lang/triton/blob/f893845b/lib/Conversion/TritonGPUToLLVM/CMakeLists.txt)
 - [lib/Conversion/TritonGPUToLLVM/CanonicalizeLLVMIR.cpp](https://github.com/triton-lang/triton/blob/f893845b/lib/Conversion/TritonGPUToLLVM/CanonicalizeLLVMIR.cpp)
 - [lib/Conversion/TritonGPUToLLVM/ConvertLayoutOpToLLVM.cpp](https://github.com/triton-lang/triton/blob/f893845b/lib/Conversion/TritonGPUToLLVM/ConvertLayoutOpToLLVM.cpp)
 - [lib/Conversion/TritonGPUToLLVM/DotOpToLLVM/FMA.cpp](https://github.com/triton-lang/triton/blob/f893845b/lib/Conversion/TritonGPUToLLVM/DotOpToLLVM/FMA.cpp)
 - [lib/Conversion/TritonGPUToLLVM/MemoryOpToLLVM.cpp](https://github.com/triton-lang/triton/blob/f893845b/lib/Conversion/TritonGPUToLLVM/MemoryOpToLLVM.cpp)
 - [lib/Conversion/TritonGPUToLLVM/Utility.cpp](https://github.com/triton-lang/triton/blob/f893845b/lib/Conversion/TritonGPUToLLVM/Utility.cpp)
 - [test/Conversion/tritongpu_to_llvm.mlir](https://github.com/triton-lang/triton/blob/f893845b/test/Conversion/tritongpu_to_llvm.mlir)
 - [third_party/nvidia/lib/TritonNVIDIAGPUToLLVM/ConvertLayoutOpToLLVM.cpp](https://github.com/triton-lang/triton/blob/f893845b/third_party/nvidia/lib/TritonNVIDIAGPUToLLVM/ConvertLayoutOpToLLVM.cpp)
 - [third_party/nvidia/lib/TritonNVIDIAGPUToLLVM/LoadStoreOpToLLVM.cpp](https://github.com/triton-lang/triton/blob/f893845b/third_party/nvidia/lib/TritonNVIDIAGPUToLLVM/LoadStoreOpToLLVM.cpp)
 - [third_party/nvidia/lib/TritonNVIDIAGPUToLLVM/PatternTritonGPUOpToLLVM.h](https://github.com/triton-lang/triton/blob/f893845b/third_party/nvidia/lib/TritonNVIDIAGPUToLLVM/PatternTritonGPUOpToLLVM.h)
 - [third_party/nvidia/lib/TritonNVIDIAGPUToLLVM/TritonGPUToLLVM.cpp](https://github.com/triton-lang/triton/blob/f893845b/third_party/nvidia/lib/TritonNVIDIAGPUToLLVM/TritonGPUToLLVM.cpp)
 
  
## Purpose and Scope

 This page describes the backend compilation stage where optimized TritonGPU IR (TTGIR) is lowered to LLVM IR and subsequently to target-specific machine code (PTX for NVIDIA, AMDGCN for AMD). This corresponds to Stage 4 (TTGIR → LLVM) and Stage 5 (Code Generation) in the project pipeline.

 The backend compilation process transforms high-level tensor operations with GPU-specific layout information into efficient LLVM IR that can be compiled to native GPU instructions. This stage is responsible for:

 
 - Converting TTGIR operations to LLVM dialect operations.
 - Generating inline PTX/AMDGCN assembly for specialized instructions.
 - Mapping distributed tensor layouts to register-level code using `LinearLayout` abstractions.
 - Handling memory operations (loads, stores, shared memory access).
 - Lowering matrix multiplication operations to hardware MMA instructions.
 
 For details on specific operation lowering patterns, see:

 
 - [TritonGPU to LLVM Lowering Framework](https://deepwiki.com/triton-lang/triton/5.1-tritongpu-to-llvm-lowering-framework)
 - [Memory Operations Lowering](https://deepwiki.com/triton-lang/triton/5.2-memory-operations-lowering)
 - [Layout Conversion Lowering](https://deepwiki.com/triton-lang/triton/5.3-layout-conversion-lowering)
 - [Reduction and Scan Operations Lowering](https://deepwiki.com/triton-lang/triton/5.4-reduction-and-scan-operations-lowering)
 - [MMA and Dot Operation Lowering](https://deepwiki.com/triton-lang/triton/5.5-mma-and-dot-operation-lowering)
 - [NVIDIA CUDA Backend](https://deepwiki.com/triton-lang/triton/5.6-nvidia-cuda-backend)
 - [AMD HIP Backend](https://deepwiki.com/triton-lang/triton/5.7-amd-hip-backend)
 
 
## Backend Compilation Architecture

 The backend compilation system is built on MLIR's conversion infrastructure with hardware-specific customization points. The project utilizes `ConversionPatternRewriter` and `LLVMTypeConverter` to transition from Triton dialects to LLVM.

 
### System Flow to Code Entity Map

 The following diagram maps high-level compilation steps to the specific C++ classes and files that implement them.

 
```

```

 Sources: [lib/Conversion/TritonGPUToLLVM/MemoryOpToLLVM.cpp168-170](https://github.com/triton-lang/triton/blob/f893845b/lib/Conversion/TritonGPUToLLVM/MemoryOpToLLVM.cpp#L168-L170) [lib/Conversion/TritonGPUToLLVM/ConvertLayoutOpToLLVM.cpp26-34](https://github.com/triton-lang/triton/blob/f893845b/lib/Conversion/TritonGPUToLLVM/ConvertLayoutOpToLLVM.cpp#L26-L34) [include/triton/Conversion/TritonGPUToLLVM/Utility.h52-54](https://github.com/triton-lang/triton/blob/f893845b/include/triton/Conversion/TritonGPUToLLVM/Utility.h#L52-L54) [lib/Conversion/TritonGPUToLLVM/Utility.cpp43-49](https://github.com/triton-lang/triton/blob/f893845b/lib/Conversion/TritonGPUToLLVM/Utility.cpp#L43-L49)

 
## Type Conversion System

 The `TritonGPUToLLVMTypeConverter` transforms TritonGPU types into LLVM-compatible types. Tensor types are converted into structures containing individual register values.

 
```

```

 Tensors with distributed layouts are unpacked into individual scalar values, one per register held by the thread. For a tensor where each thread holds multiple elements, the converted type is an `LLVM::LLVMStructType` containing those elements. Memory descriptors for shared memory are converted to `SharedMemoryObject` structures containing a base pointer and dimension offsets [lib/Conversion/TritonGPUToLLVM/MemoryOpToLLVM.cpp131-132](https://github.com/triton-lang/triton/blob/f893845b/lib/Conversion/TritonGPUToLLVM/MemoryOpToLLVM.cpp#L131-L132)

 Sources: [lib/Conversion/TritonGPUToLLVM/Utility.cpp83-86](https://github.com/triton-lang/triton/blob/f893845b/lib/Conversion/TritonGPUToLLVM/Utility.cpp#L83-L86) [lib/Conversion/TritonGPUToLLVM/MemoryOpToLLVM.cpp146-147](https://github.com/triton-lang/triton/blob/f893845b/lib/Conversion/TritonGPUToLLVM/MemoryOpToLLVM.cpp#L146-L147) [lib/Conversion/TritonGPUToLLVM/ConvertLayoutOpToLLVM.cpp105-114](https://github.com/triton-lang/triton/blob/f893845b/lib/Conversion/TritonGPUToLLVM/ConvertLayoutOpToLLVM.cpp#L105-L114)

 
## Target Abstraction: TargetInfoBase

 The `TargetInfoBase` interface provides hardware-specific operations, allowing lowering patterns to remain largely target-independent. Backends implement this interface (e.g., `NVIDIA::TargetInfo`) to provide architecture-specific logic.

 
| Feature | TargetInfoBase Method | Purpose |
|---|---|---|
| Shared Memory | loadDShared() / storeDShared() | Generates shared memory access (e.g., ld.shared) lib/Conversion/TritonGPUToLLVM/MemoryOpToLLVM.cpp40-44 |
| Barrier | barrier() | Emits threadblock-level synchronization lib/Conversion/TritonGPUToLLVM/ConvertLayoutOpToLLVM.cpp163-164 |
| Matrix Core | supportLdMatrix() / supportStMatrix() | Queries hardware support for specialized matrix instructions lib/Conversion/TritonGPUToLLVM/Utility.cpp56-65 |
| Warp Sync | warpSync() | Emits warp-level synchronization lib/Conversion/TritonGPUToLLVM/ConvertLayoutOpToLLVM.cpp161-162 |

 Sources: [include/triton/Conversion/TritonGPUToLLVM/TargetInfoBase.h1-20](https://github.com/triton-lang/triton/blob/f893845b/include/triton/Conversion/TritonGPUToLLVM/TargetInfoBase.h#L1-L20) [lib/Conversion/TritonGPUToLLVM/Utility.cpp43-80](https://github.com/triton-lang/triton/blob/f893845b/lib/Conversion/TritonGPUToLLVM/Utility.cpp#L43-L80)

 
## Key Utility Functions and Data Structures

 
### TritonLLVMOpBuilder

 A helper struct providing shortcuts for creating common LLVM operations like `add`, `sub`, `shl`, and `bitcast` while maintaining project-specific location and builder context [include/triton/Conversion/TritonGPUToLLVM/Utility.h52-157](https://github.com/triton-lang/triton/blob/f893845b/include/triton/Conversion/TritonGPUToLLVM/Utility.h#L52-L157)

 
### Index Computation with LinearLayout

 The backend uses `LinearLayout` to map logical tensor coordinates to physical register and thread locations. The utility `matrixVectorProd` performs the underlying linear transformation required for layout mapping [lib/Conversion/TritonGPUToLLVM/Utility.cpp111-213](https://github.com/triton-lang/triton/blob/f893845b/lib/Conversion/TritonGPUToLLVM/Utility.cpp#L111-L213)

 
### SharedMemoryObject

 `SharedMemoryObject` encapsulates shared memory accesses. It tracks the base pointer (address space 3) and dimension offsets. It is often created during `LocalAllocOp` lowering [lib/Conversion/TritonGPUToLLVM/MemoryOpToLLVM.cpp131-132](https://github.com/triton-lang/triton/blob/f893845b/lib/Conversion/TritonGPUToLLVM/MemoryOpToLLVM.cpp#L131-L132)

 
## Operation Lowering Overview

 
### Memory Operations

 
 - **Global Memory**: `triton::LoadOp` and `triton::StoreOp` are lowered to global load/store instructions. The `LoadOpConversion` handles vectorization sizes, masking, and cache policies [third_party/nvidia/lib/TritonNVIDIAGPUToLLVM/LoadStoreOpToLLVM.cpp132-190](https://github.com/triton-lang/triton/blob/f893845b/third_party/nvidia/lib/TritonNVIDIAGPUToLLVM/LoadStoreOpToLLVM.cpp#L132-L190)
 - **Shared Memory**: `triton::gpu::LocalAllocOp` allocates shared memory, while `LocalLoadOp` and `LocalStoreOp` handle data movement [lib/Conversion/TritonGPUToLLVM/MemoryOpToLLVM.cpp109-170](https://github.com/triton-lang/triton/blob/f893845b/lib/Conversion/TritonGPUToLLVM/MemoryOpToLLVM.cpp#L109-L170)
 - **Cache Policies**: NVIDIA-specific lowering supports `createpolicy.fractional.L2` for fine-grained cache control [third_party/nvidia/lib/TritonNVIDIAGPUToLLVM/LoadStoreOpToLLVM.cpp46-79](https://github.com/triton-lang/triton/blob/f893845b/third_party/nvidia/lib/TritonNVIDIAGPUToLLVM/LoadStoreOpToLLVM.cpp#L46-L79)
 
 
### Layout Conversions

 
 - **`triton::gpu::ConvertLayoutOp`**: Transforms data between different distributed layouts. The lowering framework chooses between: 
 - `transferWithinThread`: Simple register reordering [lib/Conversion/TritonGPUToLLVM/ConvertLayoutOpToLLVM.cpp93-116](https://github.com/triton-lang/triton/blob/f893845b/lib/Conversion/TritonGPUToLLVM/ConvertLayoutOpToLLVM.cpp#L93-L116)
 - `transferWithinWarp`: Using warp shuffles [lib/Conversion/TritonGPUToLLVM/ConvertLayoutOpToLLVM.cpp69-74](https://github.com/triton-lang/triton/blob/f893845b/lib/Conversion/TritonGPUToLLVM/ConvertLayoutOpToLLVM.cpp#L69-L74)
 - `transferSwizzlingLocalMem`: Using shared memory for complex exchanges [lib/Conversion/TritonGPUToLLVM/ConvertLayoutOpToLLVM.cpp63-68](https://github.com/triton-lang/triton/blob/f893845b/lib/Conversion/TritonGPUToLLVM/ConvertLayoutOpToLLVM.cpp#L63-L68)
 
 
### Compute Operations

 
 - **Matrix Multiply**: `triton::DotOp` is lowered via `convertFMADot` for basic FMA-based multiplication [lib/Conversion/TritonGPUToLLVM/DotOpToLLVM/FMA.cpp50-57](https://github.com/triton-lang/triton/blob/f893845b/lib/Conversion/TritonGPUToLLVM/DotOpToLLVM/FMA.cpp#L50-L57) or specialized MMA patterns for Tensor Cores.
 - **Reductions**: `triton::ReduceOp` uses multi-stage tree-based algorithms across threads and warps [include/triton/Conversion/TritonGPUToLLVM/PatternTritonGPUOpToLLVM.h67-70](https://github.com/triton-lang/triton/blob/f893845b/include/triton/Conversion/TritonGPUToLLVM/PatternTritonGPUOpToLLVM.h#L67-L70)
 
 Sources: [lib/Conversion/TritonGPUToLLVM/MemoryOpToLLVM.cpp20-49](https://github.com/triton-lang/triton/blob/f893845b/lib/Conversion/TritonGPUToLLVM/MemoryOpToLLVM.cpp#L20-L49) [lib/Conversion/TritonGPUToLLVM/ConvertLayoutOpToLLVM.cpp36-90](https://github.com/triton-lang/triton/blob/f893845b/lib/Conversion/TritonGPUToLLVM/ConvertLayoutOpToLLVM.cpp#L36-L90) [test/Conversion/tritongpu_to_llvm.mlir138-145](https://github.com/triton-lang/triton/blob/f893845b/test/Conversion/tritongpu_to_llvm.mlir#L138-L145)
