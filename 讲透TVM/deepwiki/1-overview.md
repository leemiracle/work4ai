> 来源: [https://deepwiki.com/apache/tvm/1-overview](https://deepwiki.com/apache/tvm/1-overview)
> DeepWiki apache/tvm | Last indexed: 31 August 2026 (b16cde

# Overview

  Relevant source files 
 - [.asf.yaml](https://github.com/apache/tvm/blob/b16cdecb/.asf.yaml)
 - [3rdparty/compiler-rt/builtin_fp16.h](https://github.com/apache/tvm/blob/b16cdecb/3rdparty/compiler-rt/builtin_fp16.h)
 - [CONTRIBUTORS.md](https://github.com/apache/tvm/blob/b16cdecb/CONTRIBUTORS.md?plain=1)
 - [NOTICE](https://github.com/apache/tvm/blob/b16cdecb/NOTICE)
 - [README.md](https://github.com/apache/tvm/blob/b16cdecb/README.md?plain=1)
 - [docs/README.md](https://github.com/apache/tvm/blob/b16cdecb/docs/README.md?plain=1)
 - [docs/_static/img/e2e_fashionmnist_mlp_model.png](https://github.com/apache/tvm/blob/b16cdecb/docs/_static/img/e2e_fashionmnist_mlp_model.png)
 - [docs/arch/codegen.rst](https://github.com/apache/tvm/blob/b16cdecb/docs/arch/codegen.rst)
 - [docs/arch/external_library_dispatch.rst](https://github.com/apache/tvm/blob/b16cdecb/docs/arch/external_library_dispatch.rst)
 - [docs/arch/fusion.rst](https://github.com/apache/tvm/blob/b16cdecb/docs/arch/fusion.rst)
 - [docs/arch/index.rst](https://github.com/apache/tvm/blob/b16cdecb/docs/arch/index.rst)
 - [docs/arch/pass_infra.rst](https://github.com/apache/tvm/blob/b16cdecb/docs/arch/pass_infra.rst)
 - [docs/arch/relax_vm.rst](https://github.com/apache/tvm/blob/b16cdecb/docs/arch/relax_vm.rst)
 - [docs/arch/runtime.rst](https://github.com/apache/tvm/blob/b16cdecb/docs/arch/runtime.rst)
 - [docs/arch/runtimes/vulkan.rst](https://github.com/apache/tvm/blob/b16cdecb/docs/arch/runtimes/vulkan.rst)
 - [docs/contribute/error_handling.rst](https://github.com/apache/tvm/blob/b16cdecb/docs/contribute/error_handling.rst)
 - [docs/deep_dive/relax/learning.rst](https://github.com/apache/tvm/blob/b16cdecb/docs/deep_dive/relax/learning.rst)
 - [docs/deep_dive/tensor_ir/index.rst](https://github.com/apache/tvm/blob/b16cdecb/docs/deep_dive/tensor_ir/index.rst)
 - [docs/deep_dive/tensor_ir/tutorials/dlight_gpu_scheduling.py](https://github.com/apache/tvm/blob/b16cdecb/docs/deep_dive/tensor_ir/tutorials/dlight_gpu_scheduling.py)
 - [docs/deep_dive/tensor_ir/tutorials/meta_schedule.py](https://github.com/apache/tvm/blob/b16cdecb/docs/deep_dive/tensor_ir/tutorials/meta_schedule.py)
 - [docs/get_started/overview.rst](https://github.com/apache/tvm/blob/b16cdecb/docs/get_started/overview.rst)
 - [include/tvm/runtime/timer.h](https://github.com/apache/tvm/blob/b16cdecb/include/tvm/runtime/timer.h)
 - [jvm/native/linux-x86_64/pom.xml](https://github.com/apache/tvm/blob/b16cdecb/jvm/native/linux-x86_64/pom.xml)
 - [jvm/native/osx-x86_64/pom.xml](https://github.com/apache/tvm/blob/b16cdecb/jvm/native/osx-x86_64/pom.xml)
 - [jvm/pom.xml](https://github.com/apache/tvm/blob/b16cdecb/jvm/pom.xml)
 
  
## Purpose and Scope

 Apache TVM is an open-source machine learning compilation framework designed to optimize and deploy neural network models across diverse hardware backends, from cloud GPUs and CPUs to mobile and embedded accelerators. TVM follows a **Python-first development** philosophy to enable quick customization of compiler pipelines while ensuring **universal deployment** to minimum modules [README.md18-30](https://github.com/apache/tvm/blob/b16cdecb/README.md?plain=1#L18-L30) [docs/get_started/overview.rst21-33](https://github.com/apache/tvm/blob/b16cdecb/docs/get_started/overview.rst#L21-L33)

 The framework provides a cross-level design that jointly optimizes computational graphs (via Relax), tensor programs (via TensorIR), and hardware-specific libraries [README.md60-65](https://github.com/apache/tvm/blob/b16cdecb/README.md?plain=1#L60-L65) [docs/arch/index.rst102-106](https://github.com/apache/tvm/blob/b16cdecb/docs/arch/index.rst#L102-L106)

 For detailed information about specific subsystems, refer to:

 
 - [Architecture Overview](https://deepwiki.com/apache/tvm/1.1-architecture-overview): Layered architecture from frontends through IR layers to backends and runtime.
 - [Core IRs and Languages](https://deepwiki.com/apache/tvm/2-core-irs-and-languages): Details on Relax, TIR, and TVMScript.
 - [Operator Libraries](https://deepwiki.com/apache/tvm/3-operator-libraries): TOPI and operator collections.
 - [Frontend Systems](https://deepwiki.com/apache/tvm/4-frontend-systems): Model importers for PyTorch, ONNX, and more.
 - [Compiler Transformations](https://deepwiki.com/apache/tvm/5-compiler-transformations): Optimization passes and auto-tuning.
 - [Code Generation](https://deepwiki.com/apache/tvm/6-code-generation): Target systems and backend codegen.
 - [Runtime Systems](https://deepwiki.com/apache/tvm/7-runtime-systems): Virtual Machine, RPC, and distributed execution.
 
 **Sources**: [README.md18-65](https://github.com/apache/tvm/blob/b16cdecb/README.md?plain=1#L18-L65) [.asf.yaml18-35](https://github.com/apache/tvm/blob/b16cdecb/.asf.yaml#L18-L35) [docs/get_started/overview.rst21-41](https://github.com/apache/tvm/blob/b16cdecb/docs/get_started/overview.rst#L21-L41)

 
## System Architecture

 TVM transforms ML models through progressively lower levels of abstraction, bridging the gap between high-level frameworks and low-level hardware primitives. The compilation flow generally involves **Model Creation**, **Transformation**, **Target Translation**, and **Runtime Execution** [docs/arch/index.rst37-47](https://github.com/apache/tvm/blob/b16cdecb/docs/arch/index.rst#L37-L47)

 
### Logical Architecture Layers

 
```

```

 **Sources**: [docs/arch/index.rst34-110](https://github.com/apache/tvm/blob/b16cdecb/docs/arch/index.rst#L34-L110) [README.md60-65](https://github.com/apache/tvm/blob/b16cdecb/README.md?plain=1#L60-L65) [docs/deep_dive/tensor_ir/index.rst22-34](https://github.com/apache/tvm/blob/b16cdecb/docs/deep_dive/tensor_ir/index.rst#L22-L34)

 
## Core Components

 
### 1. Intermediate Representations (IRs)

 TVM utilizes a unified `IRModule` [docs/arch/index.rst61-62](https://github.com/apache/tvm/blob/b16cdecb/docs/arch/index.rst#L61-L62) to hold different levels of IR:

 
 - **Relax (`relax::Function`)**: A high-level functional IR representing computational graphs with support for control-flow and symbolic shapes [docs/arch/index.rst64-66](https://github.com/apache/tvm/blob/b16cdecb/docs/arch/index.rst#L64-L66) [docs/deep_dive/relax/learning.rst183-185](https://github.com/apache/tvm/blob/b16cdecb/docs/deep_dive/relax/learning.rst#L183-L185)
 - **TensorIR (`tirx::PrimFunc`)**: A low-level IR for tensor-level programs, focusing on loop-nests, threading, and vector instructions [docs/arch/index.rst67-69](https://github.com/apache/tvm/blob/b16cdecb/docs/arch/index.rst#L67-L69) [docs/deep_dive/tensor_ir/index.rst22-28](https://github.com/apache/tvm/blob/b16cdecb/docs/deep_dive/tensor_ir/index.rst#L22-L28)
 - **TIRx**: A next-generation kernel DSL for hardware-native ML kernels [docs/deep_dive/tensor_ir/index.rst27-28](https://github.com/apache/tvm/blob/b16cdecb/docs/deep_dive/tensor_ir/index.rst#L27-L28)
 
 
### 2. Frontend Importers

 TVM supports importing models from various frameworks:

 
 - **PyTorch**: Support via Dynamo and ExportedProgram translation.
 - **ONNX**: Importers for both Relay and Relax paths.
 - **nn.Module**: A Relax-native frontend allowing model definition in Python with a PyTorch-like API [docs/arch/index.rst40](https://github.com/apache/tvm/blob/b16cdecb/docs/arch/index.rst#L40-L40)
 
 
### 3. Backend and Target System

 The `Target` system manages hardware-specific translation [docs/arch/index.rst44-46](https://github.com/apache/tvm/blob/b16cdecb/docs/arch/index.rst#L44-L46)

 
 - **LLVM**: Generates code for CPU (x86, ARM) and GPU targets [docs/arch/index.rst97-98](https://github.com/apache/tvm/blob/b16cdecb/docs/arch/index.rst#L97-L98)
 - **Native Codegen**: Direct generation for CUDA, Metal, OpenCL, and Vulkan [docs/arch/index.rst98-100](https://github.com/apache/tvm/blob/b16cdecb/docs/arch/index.rst#L98-L100)
 - **BYOC (Bring Your Own Codegen)**: Integration with external libraries like TensorRT or CUTLASS [CONTRIBUTORS.md32-94](https://github.com/apache/tvm/blob/b16cdecb/CONTRIBUTORS.md?plain=1#L32-L94)
 
 
### 4. Runtime and Deployment

 The runtime environment executes compiled modules:

 
 - **Virtual Machine (VM)**: Bytecode executor for Relax functions [docs/arch/relax_vm.rst](https://github.com/apache/tvm/blob/b16cdecb/docs/arch/relax_vm.rst)
 - **Disco**: Distributed runtime for multi-GPU collective communication.
 - **RPC**: Cross-compilation and remote device execution infrastructure [CONTRIBUTORS.md92](https://github.com/apache/tvm/blob/b16cdecb/CONTRIBUTORS.md?plain=1#L92-L92)
 - **Language Bindings**: Support for Python, C++, Java (TVM4J) [jvm/pom.xml23-28](https://github.com/apache/tvm/blob/b16cdecb/jvm/pom.xml#L23-L28) and Rust [CONTRIBUTORS.md48](https://github.com/apache/tvm/blob/b16cdecb/CONTRIBUTORS.md?plain=1#L48-L48)
 
 **Sources**: [docs/arch/index.rst61-110](https://github.com/apache/tvm/blob/b16cdecb/docs/arch/index.rst#L61-L110) [README.md47-65](https://github.com/apache/tvm/blob/b16cdecb/README.md?plain=1#L47-L65) [jvm/pom.xml19-32](https://github.com/apache/tvm/blob/b16cdecb/jvm/pom.xml#L19-L32) [docs/deep_dive/relax/learning.rst179-185](https://github.com/apache/tvm/blob/b16cdecb/docs/deep_dive/relax/learning.rst#L179-L185)

 
## Code Entity Map: From Framework to Runtime

 The following diagram bridges the natural language concepts to specific code entities and identifiers used within the codebase.

 
```

```

 **Sources**: [docs/arch/index.rst37-110](https://github.com/apache/tvm/blob/b16cdecb/docs/arch/index.rst#L37-L110) [docs/arch/pass_infra.rst126-144](https://github.com/apache/tvm/blob/b16cdecb/docs/arch/pass_infra.rst#L126-L144) [jvm/native/osx-x86_64/pom.xml70-74](https://github.com/apache/tvm/blob/b16cdecb/jvm/native/osx-x86_64/pom.xml#L70-L74)

 
## Project Governance and History

 TVM started as a research project and is now an **Apache Software Foundation** project [README.md47-50](https://github.com/apache/tvm/blob/b16cdecb/README.md?plain=1#L47-L50) It is governed by meritocracy, inviting contributors to influence the project's direction [CONTRIBUTORS.md20-23](https://github.com/apache/tvm/blob/b16cdecb/CONTRIBUTORS.md?plain=1#L20-L23)

 The project incorporates technologies and design inspirations from:

 
 - **Halide**: Part of TIR and arithmetic simplification [README.md51-52](https://github.com/apache/tvm/blob/b16cdecb/README.md?plain=1#L51-L52)
 - **Loopy**: Integer set analysis and loop transformation primitives [README.md53](https://github.com/apache/tvm/blob/b16cdecb/README.md?plain=1#L53-L53)
 - **Theano**: Symbolic scan operator design [README.md54](https://github.com/apache/tvm/blob/b16cdecb/README.md?plain=1#L54-L54)
 
 **Sources**: [README.md1-65](https://github.com/apache/tvm/blob/b16cdecb/README.md?plain=1#L1-L65) [CONTRIBUTORS.md18-30](https://github.com/apache/tvm/blob/b16cdecb/CONTRIBUTORS.md?plain=1#L18-L30) [NOTICE1-5](https://github.com/apache/tvm/blob/b16cdecb/NOTICE#L1-L5)
