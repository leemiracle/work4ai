> 来源: [https://deepwiki.com/apache/tvm/7-runtime-systems](https://deepwiki.com/apache/tvm/7-runtime-systems)
> DeepWiki apache/tvm | Last indexed: 31 August 2026 (b16cde

# Runtime Systems

  Relevant source files 
 - [include/tvm/runtime/vm/executable.h](https://github.com/apache/tvm/blob/b16cdecb/include/tvm/runtime/vm/executable.h)
 - [include/tvm/runtime/vm/vm.h](https://github.com/apache/tvm/blob/b16cdecb/include/tvm/runtime/vm/vm.h)
 - [python/tvm/base.py](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/base.py)
 - [python/tvm/exec/query_rpc_tracker.py](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/exec/query_rpc_tracker.py)
 - [python/tvm/exec/rpc_tracker.py](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/exec/rpc_tracker.py)
 - [python/tvm/rpc/base.py](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/rpc/base.py)
 - [python/tvm/rpc/minrpc.py](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/rpc/minrpc.py)
 - [python/tvm/rpc/proxy.py](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/rpc/proxy.py)
 - [python/tvm/rpc/server.py](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/rpc/server.py)
 - [python/tvm/rpc/testing.py](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/rpc/testing.py)
 - [python/tvm/rpc/tracker.py](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/rpc/tracker.py)
 - [python/tvm/runtime/module.py](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/runtime/module.py)
 - [python/tvm/runtime/vm.py](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/runtime/vm.py)
 - [python/tvm/support/emcc.py](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/support/emcc.py)
 - [src/runtime/vm/executable.cc](https://github.com/apache/tvm/blob/b16cdecb/src/runtime/vm/executable.cc)
 - [src/runtime/vm/vm.cc](https://github.com/apache/tvm/blob/b16cdecb/src/runtime/vm/vm.cc)
 - [src/target/codegen.cc](https://github.com/apache/tvm/blob/b16cdecb/src/target/codegen.cc)
 
  
## Purpose and Scope

 This overview page introduces TVM's runtime execution environments that run compiled models on target devices. TVM provides several specialized runtime systems optimized for different deployment scenarios:

 
 - **[Virtual Machine](https://deepwiki.com/apache/tvm/7.1-virtual-machine)**: Native bytecode interpreter for Relax-based execution on CPU/GPU.
 - **[WebAssembly Runtime](https://deepwiki.com/apache/tvm/7.2-webassembly-runtime)**: Browser and Node.js execution with WebGPU acceleration.
 - **[Runtime APIs and Device Management](https://deepwiki.com/apache/tvm/7.3-runtime-apis-and-device-management)**: Device abstraction, memory management, and cross-platform APIs.
 - **[RPC and Remote Execution](https://deepwiki.com/apache/tvm/7.4-rpc-and-remote-execution)**: Infrastructure for cross-compilation and remote device execution.
 - **[Disco Distributed Runtime](https://deepwiki.com/apache/tvm/7.5-disco-distributed-runtime)**: Multi-GPU and multi-node distributed execution framework.
 - **[Java Runtime (TVM4J)](https://deepwiki.com/apache/tvm/7.6-java-runtime-(tvm4j))**: Java frontend and JNI bindings for TVM execution.
 
 For details on code generation that produces runtime artifacts, see [Code Generation](https://deepwiki.com/apache/tvm/6-code-generation). For compiler transformations that lower models to runtime formats, see [Compiler Transformations](https://deepwiki.com/apache/tvm/5-compiler-transformations).

 
## Overview

 The TVM runtime system executes compiled models after the compilation pipeline (Relax/Relay → TIR → Code Generation) produces executable artifacts. The runtime provides:

 
 - **Bytecode execution** via the Virtual Machine interpreter for dynamic models.
 - **Distributed execution** via Disco for large-scale model inference (e.g., LLMs).
 - **Device abstraction** for heterogeneous hardware (CPU, CUDA, ROCm, Metal, OpenCL, Vulkan, WebGPU).
 - **Memory management** with device-specific allocators and unified `DeviceAPI`.
 - **Language bindings** for Python, C++, JavaScript, and Java.
 - **RPC support** for remote execution, cross-compilation, and benchmarking.
 
 
## Runtime System Architecture

 The following diagram bridges the high-level runtime components to their specific code entities and identifies how they interact across the system.

 
### Diagram: Runtime Component Mapping

 
```

```

 **Sources:** [src/runtime/vm/vm.cc190-200](https://github.com/apache/tvm/blob/b16cdecb/src/runtime/vm/vm.cc#L190-L200) [include/tvm/runtime/vm/vm.h40-46](https://github.com/apache/tvm/blob/b16cdecb/include/tvm/runtime/vm/vm.h#L40-L46) [python/tvm/runtime/vm.py41-89](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/runtime/vm.py#L41-L89)

 
## Runtime System Components

 
### 1. Virtual Machine (Native Execution)

 The Virtual Machine is TVM's primary runtime for executing `VMExecutable` bytecode generated from Relax IR. It supports dynamic shapes, control flow, and closure execution through `VMClosure` [src/runtime/vm/vm.cc44-49](https://github.com/apache/tvm/blob/b16cdecb/src/runtime/vm/vm.cc#L44-L49)

 **Key capabilities:**

 
 - Register-based bytecode execution using `VMFrame` to manage stack state [src/runtime/vm/vm.cc163-188](https://github.com/apache/tvm/blob/b16cdecb/src/runtime/vm/vm.cc#L163-L188)
 - Closure support for functional programming patterns [include/tvm/runtime/vm/vm.h59-77](https://github.com/apache/tvm/blob/b16cdecb/include/tvm/runtime/vm/vm.h#L59-L77)
 - Multi-device coordination via `Device` and `Allocator` types [include/tvm/runtime/vm/vm.h133-134](https://github.com/apache/tvm/blob/b16cdecb/include/tvm/runtime/vm/vm.h#L133-L134)
 - Serialized bytecode format `kTVMVMBytecodeMagicV2` for model deployment [src/runtime/vm/executable.cc43-44](https://github.com/apache/tvm/blob/b16cdecb/src/runtime/vm/executable.cc#L43-L44)
 
 For details, see **[Virtual Machine](https://deepwiki.com/apache/tvm/7.1-virtual-machine)**.

 
### 2. WebAssembly Runtime (Browser Execution)

 The WebAssembly runtime enables TVM execution in browsers and Node.js. It leverages WebGPU for GPU compute and provides a TypeScript/JavaScript interface for model interaction.

 For details, see **[WebAssembly Runtime](https://deepwiki.com/apache/tvm/7.2-webassembly-runtime)**.

 
### 3. Runtime APIs and Device Management

 This layer provides the unified interface for all hardware interactions. The runtime handles memory allocation via `Allocator::Empty` and data movement via `ConvertTensorToDevice` [src/runtime/vm/vm.cc90-99](https://github.com/apache/tvm/blob/b16cdecb/src/runtime/vm/vm.cc#L90-L99)

 **Key Code Entities:**

 
 - `Device`: Identifies device type and ID [python/tvm/runtime/vm.py30](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/runtime/vm.py#L30-L30)
 - `Module`: The basic unit of runtime execution, supporting `export_library` for deployment [python/tvm/runtime/module.py108-157](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/runtime/module.py#L108-L157)
 - `BenchmarkResult`: Utility for measuring execution performance [python/tvm/runtime/module.py48-89](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/runtime/module.py#L48-L89)
 
 For details, see **[Runtime APIs and Device Management](https://deepwiki.com/apache/tvm/7.3-runtime-apis-and-device-management)**.

 
### 4. RPC and Remote Execution

 The RPC infrastructure allows a client to execute code on a remote server. The `RPCServer` manages the server-side environment and module loading [python/tvm/rpc/server.py65-84](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/rpc/server.py#L65-L84)

 **Key Infrastructure:**

 
 - `RPCTracker`: Tracks and distributes available RPC resources [python/tvm/rpc/tracker.py17-41](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/rpc/tracker.py#L17-L41)
 - `RPCProxy`: Forwards messages when the server lacks a static IP [python/tvm/rpc/proxy.py18-24](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/rpc/proxy.py#L18-L24)
 - `TrackerCode`: Defines control plane protocols like `PING`, `PUT`, and `REQUEST` [python/tvm/rpc/base.py42-54](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/rpc/base.py#L42-L54)
 
 For details, see **[RPC and Remote Execution](https://deepwiki.com/apache/tvm/7.4-rpc-and-remote-execution)**.

 
### 5. Disco Distributed Runtime

 Disco is TVM's framework for multi-GPU and multi-node execution, providing collective communication primitives and session management.

 For details, see **[Disco Distributed Runtime](https://deepwiki.com/apache/tvm/7.5-disco-distributed-runtime)**.

 
### 6. Java Runtime (TVM4J)

 TVM4J provides Java bindings for the TVM runtime, allowing Java-based applications to load and execute TVM modules via JNI.

 For details, see **[Java Runtime (TVM4J)](https://deepwiki.com/apache/tvm/7.6-java-runtime-(tvm4j))**.

 
## Core Runtime Data Structures

 The runtime relies on several core structures to manage execution state and data.

 
### Diagram: Object and Function Interaction

 This diagram shows how high-level Python objects interact with the underlying C++ FFI (Foreign Function Interface) and runtime logic.

 
```

```

 **Key Code Symbols:**

 
 - `VMExecutable`: The serialized format containing the `func_table` and `constants` pool [include/tvm/runtime/vm/executable.h89-162](https://github.com/apache/tvm/blob/b16cdecb/include/tvm/runtime/vm/executable.h#L89-L162)
 - `VMFuncInfo`: Metadata for each function, including its start/end instruction index and register file size [include/tvm/runtime/vm/executable.h53-81](https://github.com/apache/tvm/blob/b16cdecb/include/tvm/runtime/vm/executable.h#L53-L81)
 - `Instruction`: The atomic unit of execution within the VM, covering `Call`, `Ret`, `Goto`, and `If` [src/runtime/vm/executable.cc131-160](https://github.com/apache/tvm/blob/b16cdecb/src/runtime/vm/executable.cc#L131-L160)
 
 **Sources:** [src/runtime/vm/vm.cc151-188](https://github.com/apache/tvm/blob/b16cdecb/src/runtime/vm/vm.cc#L151-L188) [include/tvm/runtime/vm/executable.h47-81](https://github.com/apache/tvm/blob/b16cdecb/include/tvm/runtime/vm/executable.h#L47-L81) [python/tvm/runtime/module.py108-142](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/runtime/module.py#L108-L142) [python/tvm/runtime/vm.py41-89](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/runtime/vm.py#L41-L89)

 
## Compiled Artifact Formats

 Runtime systems consume different executable formats depending on the compilation target:

 
| Format | Description | Target Runtime |
|---|---|---|
| VMExecutable | Bytecode instructions + Constant Pool | Virtual Machine |
| Shared Library | Compiled .so or .dll via export_library | Native Runtime |
| Binary Bytes | Serialized module state via SaveToBytes | Remote/RPC Runtime |

 **Sources:** [src/runtime/vm/executable.cc183-203](https://github.com/apache/tvm/blob/b16cdecb/src/runtime/vm/executable.cc#L183-L203) [python/tvm/runtime/module.py148-180](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/runtime/module.py#L148-L180) [src/target/codegen.cc65-93](https://github.com/apache/tvm/blob/b16cdecb/src/target/codegen.cc#L65-L93)
