> 来源: [https://deepwiki.com/triton-lang/triton/8-glossary](https://deepwiki.com/triton-lang/triton/8-glossary)
> DeepWiki triton-lang/triton | Last indexed: 20 August 2026 (f89384

# Glossary

  Relevant source files 
 - [bin/RegisterTritonDialects.h](https://github.com/triton-lang/triton/blob/f893845b/bin/RegisterTritonDialects.h)
 - [docs/python-api/triton-semantics.rst](https://github.com/triton-lang/triton/blob/f893845b/docs/python-api/triton-semantics.rst)
 - [include/triton/Dialect/TritonGPU/IR/Dialect.h](https://github.com/triton-lang/triton/blob/f893845b/include/triton/Dialect/TritonGPU/IR/Dialect.h)
 - [include/triton/Dialect/TritonGPU/IR/LinearLayoutConversions.h](https://github.com/triton-lang/triton/blob/f893845b/include/triton/Dialect/TritonGPU/IR/LinearLayoutConversions.h)
 - [include/triton/Dialect/TritonGPU/IR/TritonGPUAttrDefs.td](https://github.com/triton-lang/triton/blob/f893845b/include/triton/Dialect/TritonGPU/IR/TritonGPUAttrDefs.td)
 - [include/triton/Dialect/TritonGPU/Transforms/Passes.h](https://github.com/triton-lang/triton/blob/f893845b/include/triton/Dialect/TritonGPU/Transforms/Passes.h)
 - [include/triton/Dialect/TritonGPU/Transforms/Passes.td](https://github.com/triton-lang/triton/blob/f893845b/include/triton/Dialect/TritonGPU/Transforms/Passes.td)
 - [lib/Conversion/TritonGPUToLLVM/ViewOpToLLVM.cpp](https://github.com/triton-lang/triton/blob/f893845b/lib/Conversion/TritonGPUToLLVM/ViewOpToLLVM.cpp)
 - [lib/Conversion/TritonToTritonGPU/TritonToTritonGPUPass.cpp](https://github.com/triton-lang/triton/blob/f893845b/lib/Conversion/TritonToTritonGPU/TritonToTritonGPUPass.cpp)
 - [lib/Dialect/TritonGPU/IR/Dialect.cpp](https://github.com/triton-lang/triton/blob/f893845b/lib/Dialect/TritonGPU/IR/Dialect.cpp)
 - [lib/Dialect/TritonGPU/IR/LinearLayoutConversions.cpp](https://github.com/triton-lang/triton/blob/f893845b/lib/Dialect/TritonGPU/IR/LinearLayoutConversions.cpp)
 - [lib/Dialect/TritonGPU/Transforms/CMakeLists.txt](https://github.com/triton-lang/triton/blob/f893845b/lib/Dialect/TritonGPU/Transforms/CMakeLists.txt)
 - [python/src/gluon_ir.cc](https://github.com/triton-lang/triton/blob/f893845b/python/src/gluon_ir.cc)
 - [python/src/ir.cc](https://github.com/triton-lang/triton/blob/f893845b/python/src/ir.cc)
 - [python/src/llvm.cc](https://github.com/triton-lang/triton/blob/f893845b/python/src/llvm.cc)
 - [python/src/passes.cc](https://github.com/triton-lang/triton/blob/f893845b/python/src/passes.cc)
 - [python/test/backend/test_mir_stage.py](https://github.com/triton-lang/triton/blob/f893845b/python/test/backend/test_mir_stage.py)
 - [python/test/gluon/test_core.py](https://github.com/triton-lang/triton/blob/f893845b/python/test/gluon/test_core.py)
 - [python/test/gluon/test_frontend.py](https://github.com/triton-lang/triton/blob/f893845b/python/test/gluon/test_frontend.py)
 - [python/test/gluon/test_lowerings.py](https://github.com/triton-lang/triton/blob/f893845b/python/test/gluon/test_lowerings.py)
 - [python/test/unit/language/test_core.py](https://github.com/triton-lang/triton/blob/f893845b/python/test/unit/language/test_core.py)
 - [python/test/unit/language/test_frontend.py](https://github.com/triton-lang/triton/blob/f893845b/python/test/unit/language/test_frontend.py)
 - [python/test/unit/runtime/test_cache.py](https://github.com/triton-lang/triton/blob/f893845b/python/test/unit/runtime/test_cache.py)
 - [python/triton/compiler/code_generator.py](https://github.com/triton-lang/triton/blob/f893845b/python/triton/compiler/code_generator.py)
 - [python/triton/compiler/compiler.py](https://github.com/triton-lang/triton/blob/f893845b/python/triton/compiler/compiler.py)
 - [python/triton/experimental/gluon/language/__init__.py](https://github.com/triton-lang/triton/blob/f893845b/python/triton/experimental/gluon/language/__init__.py)
 - [python/triton/experimental/gluon/language/_core.py](https://github.com/triton-lang/triton/blob/f893845b/python/triton/experimental/gluon/language/_core.py)
 - [python/triton/experimental/gluon/language/_layouts.py](https://github.com/triton-lang/triton/blob/f893845b/python/triton/experimental/gluon/language/_layouts.py)
 - [python/triton/experimental/gluon/language/_semantic.py](https://github.com/triton-lang/triton/blob/f893845b/python/triton/experimental/gluon/language/_semantic.py)
 - [python/triton/experimental/gluon/language/nvidia/blackwell/__init__.py](https://github.com/triton-lang/triton/blob/f893845b/python/triton/experimental/gluon/language/nvidia/blackwell/__init__.py)
 - [python/triton/experimental/gluon/language/nvidia/hopper/__init__.py](https://github.com/triton-lang/triton/blob/f893845b/python/triton/experimental/gluon/language/nvidia/hopper/__init__.py)
 - [python/triton/language/__init__.py](https://github.com/triton-lang/triton/blob/f893845b/python/triton/language/__init__.py)
 - [python/triton/language/core.py](https://github.com/triton-lang/triton/blob/f893845b/python/triton/language/core.py)
 - [python/triton/language/semantic.py](https://github.com/triton-lang/triton/blob/f893845b/python/triton/language/semantic.py)
 - [python/triton/runtime/interpreter.py](https://github.com/triton-lang/triton/blob/f893845b/python/triton/runtime/interpreter.py)
 - [python/triton/runtime/jit.py](https://github.com/triton-lang/triton/blob/f893845b/python/triton/runtime/jit.py)
 - [third_party/amd/backend/compiler.py](https://github.com/triton-lang/triton/blob/f893845b/third_party/amd/backend/compiler.py)
 - [third_party/amd/include/TritonAMDGPUToLLVM/Passes.h](https://github.com/triton-lang/triton/blob/f893845b/third_party/amd/include/TritonAMDGPUToLLVM/Passes.h)
 - [third_party/amd/include/TritonAMDGPUToLLVM/Passes.td](https://github.com/triton-lang/triton/blob/f893845b/third_party/amd/include/TritonAMDGPUToLLVM/Passes.td)
 - [third_party/amd/include/TritonAMDGPUTransforms/Passes.h](https://github.com/triton-lang/triton/blob/f893845b/third_party/amd/include/TritonAMDGPUTransforms/Passes.h)
 - [third_party/amd/include/TritonAMDGPUTransforms/Passes.td](https://github.com/triton-lang/triton/blob/f893845b/third_party/amd/include/TritonAMDGPUTransforms/Passes.td)
 - [third_party/amd/lib/TritonAMDGPUToLLVM/CMakeLists.txt](https://github.com/triton-lang/triton/blob/f893845b/third_party/amd/lib/TritonAMDGPUToLLVM/CMakeLists.txt)
 - [third_party/amd/lib/TritonAMDGPUToLLVM/PatternTritonGPUOpToLLVM.h](https://github.com/triton-lang/triton/blob/f893845b/third_party/amd/lib/TritonAMDGPUToLLVM/PatternTritonGPUOpToLLVM.h)
 - [third_party/amd/lib/TritonAMDGPUToLLVM/TritonGPUToLLVM.cpp](https://github.com/triton-lang/triton/blob/f893845b/third_party/amd/lib/TritonAMDGPUToLLVM/TritonGPUToLLVM.cpp)
 - [third_party/amd/lib/TritonAMDGPUTransforms/CMakeLists.txt](https://github.com/triton-lang/triton/blob/f893845b/third_party/amd/lib/TritonAMDGPUTransforms/CMakeLists.txt)
 - [third_party/amd/python/triton_amd.cc](https://github.com/triton-lang/triton/blob/f893845b/third_party/amd/python/triton_amd.cc)
 - [third_party/nvidia/backend/compiler.py](https://github.com/triton-lang/triton/blob/f893845b/third_party/nvidia/backend/compiler.py)
 - [unittest/Dialect/TritonGPU/DialectTest.cpp](https://github.com/triton-lang/triton/blob/f893845b/unittest/Dialect/TritonGPU/DialectTest.cpp)
 - [unittest/Dialect/TritonGPU/LinearLayoutConversionsTest.cpp](https://github.com/triton-lang/triton/blob/f893845b/unittest/Dialect/TritonGPU/LinearLayoutConversionsTest.cpp)
 
  This page provides definitions for codebase-specific terms, hardware-specific jargon, and architectural concepts used within the Triton compiler.

 
## IR Stages and Dialects

 Triton uses a multi-stage compilation pipeline based on MLIR. Each stage lowers the abstraction level closer to the hardware.

 
| Stage | Name | Description |
|---|---|---|
| TTIR | Triton Dialect | The highest-level IR, directly generated from Python AST. Represents operations on infinite-precision tensors without hardware-specific layouts. python/triton/compiler/code_generator.py79-81 |
| TTGIR | TritonGPU Dialect | Extends TTIR with Layout Encoding Attributes. This stage is where most optimizations (pipelining, coalescing, layout propagation) occur. lib/Dialect/TritonGPU/IR/Dialect.cpp14-18 |
| LLIR | LLVM IR | The final software IR stage before being handed off to backend-specific assemblers (PTX for NVIDIA, GCN for AMD). third_party/amd/backend/compiler.py2-3 |

 
### Compilation Data Flow

 
```

```

 *Sources: [python/triton/compiler/code_generator.py79-81](https://github.com/triton-lang/triton/blob/f893845b/python/triton/compiler/code_generator.py#L79-L81) [lib/Dialect/TritonGPU/IR/Dialect.cpp46-59](https://github.com/triton-lang/triton/blob/f893845b/lib/Dialect/TritonGPU/IR/Dialect.cpp#L46-L59) [third_party/amd/backend/compiler.py140-150](https://github.com/triton-lang/triton/blob/f893845b/third_party/amd/backend/compiler.py#L140-L150)*

 
---

 
## Layout Concepts

 Layouts define how tensor elements are distributed across threads, warps, and memory.

 
 - **LinearLayout**: A canonical representation for layout conversions using a matrix-based mapping of input dimensions to output dimensions. It is the core abstraction for the `ttg.convert_layout` operation. [lib/Dialect/TritonGPU/IR/Dialect.cpp46-59](https://github.com/triton-lang/triton/blob/f893845b/lib/Dialect/TritonGPU/IR/Dialect.cpp#L46-L59) [lib/Dialect/TritonGPU/IR/LinearLayoutConversions.cpp10-12](https://github.com/triton-lang/triton/blob/f893845b/lib/Dialect/TritonGPU/IR/LinearLayoutConversions.cpp#L10-L12)
 - **BlockedEncoding**: Distributes a tensor across a grid of threads. Defined by `sizePerThread`, `threadsPerWarp`, and `warpsPerCTA`. [python/test/gluon/test_frontend.py71-73](https://github.com/triton-lang/triton/blob/f893845b/python/test/gluon/test_frontend.py#L71-L73)
 - **SwizzledShared**: A shared memory layout that applies a XOR-based swizzle pattern to avoid bank conflicts during matrix operand loading. [lib/Dialect/TritonGPU/IR/Dialect.cpp91-104](https://github.com/triton-lang/triton/blob/f893845b/lib/Dialect/TritonGPU/IR/Dialect.cpp#L91-L104) [lib/Dialect/TritonGPU/IR/LinearLayoutConversions.cpp50-51](https://github.com/triton-lang/triton/blob/f893845b/lib/Dialect/TritonGPU/IR/LinearLayoutConversions.cpp#L50-L51)
 - **DotOperand**: A specialized encoding for tensors that are used as inputs to a `tt.dot` operation, often matching the specific hardware requirements of MMA or MFMA instructions. [lib/Dialect/TritonGPU/IR/Dialect.cpp96-97](https://github.com/triton-lang/triton/blob/f893845b/lib/Dialect/TritonGPU/IR/Dialect.cpp#L96-L97)
 
 
---

 
## Hardware Terms

 
### General & NVIDIA

 
 - **CTA (Cooperative Thread Array)**: Equivalent to a CUDA Thread Block. Triton kernels can launch multiple CTAs per grid. [python/triton/compiler/compiler.py126-128](https://github.com/triton-lang/triton/blob/f893845b/python/triton/compiler/compiler.py#L126-L128)
 - **SM (Streaming Multiprocessor)**: The hardware unit that executes CTAs.
 - **TMA (Tensor Memory Accelerator)**: Hardware in NVIDIA Hopper (sm_90+) for asynchronous multidimensional memory copies between global and shared memory. [python/test/gluon/test_frontend.py11-15](https://github.com/triton-lang/triton/blob/f893845b/python/test/gluon/test_frontend.py#L11-L15)
 - **TMEM (Tensor Memory)**: A specialized high-bandwidth memory buffer in NVIDIA Blackwell (sm_100+) used by the TCGen5 engine. [python/test/gluon/test_frontend.py10-15](https://github.com/triton-lang/triton/blob/f893845b/python/test/gluon/test_frontend.py#L10-L15)
 - **mbarrier**: Hardware synchronization primitive used to track the completion of asynchronous TMA operations. [python/test/gluon/test_frontend.py13-15](https://github.com/triton-lang/triton/blob/f893845b/python/test/gluon/test_frontend.py#L13-L15)
 - **WGMMA (Warp Group MMA)**: Large-scale matrix-multiply-accumulate instructions that operate at the warp-group level (128 threads) on Hopper GPUs.
 
 
### AMD Specific

 
 - **MFMA / WMMA**: Matrix-fused-multiply-add instructions. MFMA is used on CDNA (gfx9) architectures, while WMMA is used on RDNA (gfx11/12). [python/test/unit/language/test_core.py78-84](https://github.com/triton-lang/triton/blob/f893845b/python/test/unit/language/test_core.py#L78-L84)
 - **LDS (Local Data Share)**: The AMD term for on-chip shared memory.
 - **HSACO**: The binary executable format for AMD GPU kernels. [third_party/amd/backend/compiler.py149](https://github.com/triton-lang/triton/blob/f893845b/third_party/amd/backend/compiler.py#L149-L149)
 - **VGPR / SGPR**: Vector and Scalar General Purpose Registers.
 - **TDM (Tensor Data Movement)**: AMD-specific hardware features for efficient data movement, particularly on `gfx1250`. [third_party/amd/backend/compiler.py36-39](https://github.com/triton-lang/triton/blob/f893845b/third_party/amd/backend/compiler.py#L36-L39)
 - **Block Pingpong**: A scheduling strategy on AMD GPUs to overlap memory loads and computation by alternating between two sets of buffers. [third_party/amd/backend/compiler.py22-24](https://github.com/triton-lang/triton/blob/f893845b/third_party/amd/backend/compiler.py#L22-L24)
 - **GFX1250**: The architecture identifier for AMD CDNA5 GPUs. [third_party/amd/backend/compiler.py46-49](https://github.com/triton-lang/triton/blob/f893845b/third_party/amd/backend/compiler.py#L46-L49)
 
 
---

 
## Compiler Concepts

 
 - **constexpr**: A value known at compile-time. In Triton, `tl.constexpr` allows for meta-programming, such as specialization and compile-time branching. [python/triton/language/core.py192-195](https://github.com/triton-lang/triton/blob/f893845b/python/triton/language/core.py#L192-L195) [python/triton/compiler/code_generator.py16-17](https://github.com/triton-lang/triton/blob/f893845b/python/triton/compiler/code_generator.py#L16-L17)
 - **Specialization**: The process of generating a specific version of a kernel based on the values of `constexpr` arguments or the alignment/type of pointer arguments. [python/triton/runtime/jit.py22-23](https://github.com/triton-lang/triton/blob/f893845b/python/triton/runtime/jit.py#L22-L23)
 - **Mangling**: The generation of unique strings for function names based on their argument types and `constexpr` values to prevent collisions in the kernel cache. [python/triton/compiler/code_generator.py32-41](https://github.com/triton-lang/triton/blob/f893845b/python/triton/compiler/code_generator.py#L32-L41)
 - **CGA (Cooperative Grid Array)**: A mechanism for CTAs to communicate and synchronize across the entire grid. [lib/Dialect/TritonGPU/IR/LinearLayoutConversions.cpp30](https://github.com/triton-lang/triton/blob/f893845b/lib/Dialect/TritonGPU/IR/LinearLayoutConversions.cpp#L30-L30)
 
 
### Code Entity Mapping: Semantic Analysis

 
```

```

 *Sources: [python/triton/runtime/jit.py136-140](https://github.com/triton-lang/triton/blob/f893845b/python/triton/runtime/jit.py#L136-L140) [python/triton/compiler/code_generator.py129-140](https://github.com/triton-lang/triton/blob/f893845b/python/triton/compiler/code_generator.py#L129-L140) [python/triton/language/semantic.py26-34](https://github.com/triton-lang/triton/blob/f893845b/python/triton/language/semantic.py#L26-L34)*

 
---

 
## Tools and Sanitizers

 
 - **Proton**: A lightweight profiling tool for Triton kernels.
 - **GSan (Global Sanitizer)**: A tool for detecting out-of-bounds accesses in global memory. [third_party/nvidia/backend/compiler.py144-149](https://github.com/triton-lang/triton/blob/f893845b/third_party/nvidia/backend/compiler.py#L144-L149)
 - **ConSan (Control Flow Sanitizer)**: Detects divergent control flow issues that might lead to deadlocks or incorrect results in synchronized blocks. [third_party/amd/backend/compiler.py52-53](https://github.com/triton-lang/triton/blob/f893845b/third_party/amd/backend/compiler.py#L52-L53)
 - **FpSan (Floating Point Sanitizer)**: Detects numerical issues like NaNs or Infs during kernel execution. [third_party/amd/backend/compiler.py48-49](https://github.com/triton-lang/triton/blob/f893845b/third_party/amd/backend/compiler.py#L48-L49)
 - **triton_kernels**: A reference library of high-performance kernels (matmul, reduce, etc.) implemented in Triton.
 - **triton-to-gluon translator**: A tool for converting standard Triton kernels to the hardware-aware Gluon IR.
 
 
### Code Entity Mapping: Runtime and Backend

 
```

```

 *Sources: [python/triton/runtime/jit.py15-23](https://github.com/triton-lang/triton/blob/f893845b/python/triton/runtime/jit.py#L15-L23) [third_party/nvidia/backend/compiler.py166-172](https://github.com/triton-lang/triton/blob/f893845b/third_party/nvidia/backend/compiler.py#L166-L172) [third_party/amd/backend/compiler.py131-139](https://github.com/triton-lang/triton/blob/f893845b/third_party/amd/backend/compiler.py#L131-L139)*
