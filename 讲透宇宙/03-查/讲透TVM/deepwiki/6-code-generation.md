> 来源: [https://deepwiki.com/apache/tvm/6-code-generation](https://deepwiki.com/apache/tvm/6-code-generation)
> DeepWiki apache/tvm | Last indexed: 31 August 2026 (b16cde

# Code Generation

  Relevant source files 
 - [include/tvm/target/tag.h](https://github.com/apache/tvm/blob/b16cdecb/include/tvm/target/tag.h)
 - [include/tvm/target/target.h](https://github.com/apache/tvm/blob/b16cdecb/include/tvm/target/target.h)
 - [include/tvm/target/target_kind.h](https://github.com/apache/tvm/blob/b16cdecb/include/tvm/target/target_kind.h)
 - [python/tvm/target/__init__.py](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/target/__init__.py)
 - [python/tvm/target/target.py](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/target/target.py)
 - [src/target/source/codegen_c.cc](https://github.com/apache/tvm/blob/b16cdecb/src/target/source/codegen_c.cc)
 - [src/target/source/codegen_c.h](https://github.com/apache/tvm/blob/b16cdecb/src/target/source/codegen_c.h)
 - [src/target/source/codegen_c_host.cc](https://github.com/apache/tvm/blob/b16cdecb/src/target/source/codegen_c_host.cc)
 - [src/target/source/codegen_c_host.h](https://github.com/apache/tvm/blob/b16cdecb/src/target/source/codegen_c_host.h)
 - [src/target/tag.cc](https://github.com/apache/tvm/blob/b16cdecb/src/target/tag.cc)
 - [src/target/target.cc](https://github.com/apache/tvm/blob/b16cdecb/src/target/target.cc)
 - [src/target/target_kind.cc](https://github.com/apache/tvm/blob/b16cdecb/src/target/target_kind.cc)
 - [tests/cpp/target_test.cc](https://github.com/apache/tvm/blob/b16cdecb/tests/cpp/target_test.cc)
 - [tests/cpp/tir_scalable_datatype.cc](https://github.com/apache/tvm/blob/b16cdecb/tests/cpp/tir_scalable_datatype.cc)
 
  This page documents TVM's code generation system, which translates optimized TIR (Tensor IR) programs into executable code for diverse hardware targets. Code generation is the final stage of the TVM compilation pipeline, producing machine code, bytecode, or source code that can run on CPUs, GPUs, DSPs, and other accelerators.

 For details about target specification and hardware characteristics, see [Target System](https://deepwiki.com/apache/tvm/6.1-target-system). For in-depth coverage of the LLVM backend implementation, see [LLVM Backend](https://deepwiki.com/apache/tvm/6.2-llvm-backend).

 
## Code Generation Architecture

 TVM supports multiple code generation backends to target different hardware platforms. The primary backend uses LLVM for CPU and GPU targets, while specialized backends generate source code for platforms like CUDA C, OpenCL, and Metal.

 
### Code Generation Backends

 
```

```

 **Sources:** [src/target/source/codegen_c.h59-61](https://github.com/apache/tvm/blob/b16cdecb/src/target/source/codegen_c.h#L59-L61) [src/target/source/codegen_c_host.h40](https://github.com/apache/tvm/blob/b16cdecb/src/target/source/codegen_c_host.h#L40-L40)

 
## Target Specification System

 Before code generation begins, TVM uses a `Target` object to configure the compiler. A `Target` describes the hardware and the desired codegen path (e.g., `llvm`, `cuda`).

 
### Target and TargetKind Relationship

 
```

```

 **Sources:** [python/tvm/target/target.py29-76](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/target/target.py#L29-L76) [src/target/target.cc140-164](https://github.com/apache/tvm/blob/b16cdecb/src/target/target.cc#L140-L164) [include/tvm/target/target.h45-56](https://github.com/apache/tvm/blob/b16cdecb/include/tvm/target/target.h#L45-L56)

 
### Key Target Components

 
| Component | Responsibility | Source |
|---|---|---|
| TargetKind | Defines the codegen backend (e.g., llvm, c, cuda) and its allowed attributes. | src/target/target_kind.cc116-175 |
| Target | A specific instance containing hardware attributes like mcpu, mattr, and arch. | include/tvm/target/target.h134-188 |
| TargetTag | A registry of common hardware configurations (e.g., nvidia/nvidia-a100). | src/target/tag.cc69-83 |
| TargetFeatures | Accesses hardware-specific capabilities (e.g., feature.is_test). | python/tvm/target/target.py43-49 |

 **Sources:** [python/tvm/target/target.py28-146](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/target/target.py#L28-L146) [src/target/target_kind.cc68-102](https://github.com/apache/tvm/blob/b16cdecb/src/target/target_kind.cc#L68-L102) [include/tvm/target/target_kind.h57-97](https://github.com/apache/tvm/blob/b16cdecb/include/tvm/target/target_kind.h#L57-L97)

 
## C-Style Source Code Generation

 The `CodeGenC` hierarchy provides a foundation for generating C-compatible source code. Unlike LLVM, which generates machine code directly, these generators produce text-based source code that is subsequently compiled by target-specific compilers (e.g., GCC, Clang, NVCC).

 
### CodeGenC Hierarchy

 
```

```

 **Sources:** [src/target/source/codegen_c.h59-61](https://github.com/apache/tvm/blob/b16cdecb/src/target/source/codegen_c.h#L59-L61) [src/target/source/codegen_c_host.h40](https://github.com/apache/tvm/blob/b16cdecb/src/target/source/codegen_c_host.h#L40-L40)

 
### Key C-Generation Components

 
| Component | Responsibility | Source |
|---|---|---|
| CodeGenC | Base class for C variants (CUDA, OpenCL). Handles SSA vs Normal form and keyword reservation. | src/target/source/codegen_c.cc41-212 |
| CodeGenCHost | Generates C code for host execution, including tvm_ffi_main entry points and library context management. | src/target/source/codegen_c_host.cc38-91 |
| PrintType | Maps TVM PrimType to C types (e.g., int32_t, float). | src/target/source/codegen_c_host.cc124-191 |
| PrintExpr | Recursively visits TIR expressions to emit C code strings. | src/target/source/codegen_c.cc204-222 |

 **Sources:** [src/target/source/codegen_c.h49-100](https://github.com/apache/tvm/blob/b16cdecb/src/target/source/codegen_c.h#L49-L100) [src/target/source/codegen_c_host.h40-78](https://github.com/apache/tvm/blob/b16cdecb/src/target/source/codegen_c_host.h#L40-L78)

 
## Code Generation Flow

 The code generation process transforms TIR functions into executable code through several stages:

 
### Initialization and Function Handling

 For C-based targets, the flow involves signature printing and body traversal:

 
 - **Initialization**: `CodeGenC::Init` sets the output mode (SSA or normal) [src/target/source/codegen_c.cc41](https://github.com/apache/tvm/blob/b16cdecb/src/target/source/codegen_c.cc#L41-L41)
 - **Signature Generation**: `PrintFunctionSignature` maps TIR parameters to C types and handles storage scopes [src/target/source/codegen_c.cc82-135](https://github.com/apache/tvm/blob/b16cdecb/src/target/source/codegen_c.cc#L82-L135)
 - **Forward Declarations**: `DeclareFunction` ensures functions are known before use in the generated source [src/target/source/codegen_c.cc137-163](https://github.com/apache/tvm/blob/b16cdecb/src/target/source/codegen_c.cc#L137-L163)
 - **Body Generation**: `AddFunction` opens a scope and visits the TIR statement tree to emit C code [src/target/source/codegen_c.cc173-190](https://github.com/apache/tvm/blob/b16cdecb/src/target/source/codegen_c.cc#L173-L190)
 
 **Sources:** [src/target/source/codegen_c.cc41-190](https://github.com/apache/tvm/blob/b16cdecb/src/target/source/codegen_c.cc#L41-L190)

 
### Expression and Statement Handling

 `CodeGenC` implements visitors for TIR nodes to emit C code:

 
 - **Expressions**: `PrintExpr` handles standard arithmetic and variable access, utilizing `name_supply_` for unique IDs [src/target/source/codegen_c.cc204-212](https://github.com/apache/tvm/blob/b16cdecb/src/target/source/codegen_c.cc#L204-L212)
 - **Host Integration**: `CodeGenCHost` specifically handles calls to the TVM backend environment via `TVMFFIEnvModLookupFromImports` [src/target/source/codegen_c_host.cc206-218](https://github.com/apache/tvm/blob/b16cdecb/src/target/source/codegen_c_host.cc#L206-L218)
 
 **Sources:** [src/target/source/codegen_c.cc204-212](https://github.com/apache/tvm/blob/b16cdecb/src/target/source/codegen_c.cc#L204-L212) [src/target/source/codegen_c_host.cc206-218](https://github.com/apache/tvm/blob/b16cdecb/src/target/source/codegen_c_host.cc#L206-L218)

 
## Target-Specific Code Generation

 Each specialized codegen class adds functionality for its target platform:

 
### LLVM Backends

 For details on LLVM-based generation (CPU, NVPTX, AMDGPU, Hexagon), see [LLVM Backend](https://deepwiki.com/apache/tvm/6.2-llvm-backend).

 
### C Host Code Generation (CodeGenCHost)

 Located in [src/target/source/codegen_c_host.cc](https://github.com/apache/tvm/blob/b16cdecb/src/target/source/codegen_c_host.cc) `CodeGenCHost` adds:

 
 - **Global Context**: Defines `tvm_ffi_library_ctx` for runtime interaction [src/target/source/codegen_c_host.cc59-63](https://github.com/apache/tvm/blob/b16cdecb/src/target/source/codegen_c_host.cc#L59-L63)
 - **Entry Function**: Automatically generates a `tvm_ffi_main` wrapper if an entry function is detected [src/target/source/codegen_c_host.cc77-91](https://github.com/apache/tvm/blob/b16cdecb/src/target/source/codegen_c_host.cc#L77-L91)
 - **Type Mapping**: Maps `DLDataType` to standard C types like `int32_t`, `float`, and `bool` [src/target/source/codegen_c_host.cc124-191](https://github.com/apache/tvm/blob/b16cdecb/src/target/source/codegen_c_host.cc#L124-L191)
 
 **Sources:** [src/target/source/codegen_c_host.cc1-218](https://github.com/apache/tvm/blob/b16cdecb/src/target/source/codegen_c_host.cc#L1-L218)

 
### External Library Integration

 TVM supports "Bring Your Own Codegen" (BYOC) and external library integration (e.g., TensorRT, CUTLASS). For details, see:

 
 - [CUTLASS Integration](https://deepwiki.com/apache/tvm/6.4-cutlass-integration)
 - [BYOC and External Library Backends](https://deepwiki.com/apache/tvm/6.6-byoc-and-external-library-backends)
 
 
## Runtime Module Generation

 After code generation, the result is wrapped in a `Module` for the TVM runtime:

 
 - **LLVMModuleNode**: For JIT/AOT execution of LLVM IR.
 - **CSourceModuleNode**: For C/C++ source code that can be exported and compiled by external tools.
 
 **Sources:** [include/tvm/target/target.h1-188](https://github.com/apache/tvm/blob/b16cdecb/include/tvm/target/target.h#L1-L188) [src/target/target.cc1-213](https://github.com/apache/tvm/blob/b16cdecb/src/target/target.cc#L1-L213)
