> 来源: [https://deepwiki.com/mlc-ai/mlc-llm/3-system-architecture](https://deepwiki.com/mlc-ai/mlc-llm/3-system-architecture)
> DeepWiki mlc-ai/mlc-llm | Last indexed: 30 March 2026 (fcce2c

# System Architecture

  Relevant source files 
 - [.gitmodules](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/.gitmodules)
 - [CMakeLists.txt](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/CMakeLists.txt)
 - [README.md](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/README.md?plain=1)
 - [android/README.md](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/android/README.md?plain=1)
 - [android/mlc4j/CMakeLists.txt](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/android/mlc4j/CMakeLists.txt)
 - [android/mlc4j/src/cpp/tvm_runtime.h](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/android/mlc4j/src/cpp/tvm_runtime.h)
 - [cpp/json_ffi/json_ffi_engine.cc](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/cpp/json_ffi/json_ffi_engine.cc)
 - [cpp/multi_gpu/builtin.cc](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/cpp/multi_gpu/builtin.cc)
 - [cpp/multi_gpu/multi_gpu_loader.cc](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/cpp/multi_gpu/multi_gpu_loader.cc)
 - [cpp/serve/config.cc](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/cpp/serve/config.cc)
 - [cpp/serve/config.h](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/cpp/serve/config.h)
 - [cpp/serve/data.cc](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/cpp/serve/data.cc)
 - [cpp/serve/data.h](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/cpp/serve/data.h)
 - [cpp/serve/engine.cc](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/cpp/serve/engine.cc)
 - [cpp/serve/engine.h](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/cpp/serve/engine.h)
 - [cpp/serve/event_trace_recorder.cc](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/cpp/serve/event_trace_recorder.cc)
 - [cpp/serve/function_table.cc](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/cpp/serve/function_table.cc)
 - [cpp/serve/function_table.h](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/cpp/serve/function_table.h)
 - [cpp/serve/model.cc](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/cpp/serve/model.cc)
 - [cpp/serve/model.h](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/cpp/serve/model.h)
 - [cpp/serve/radix_tree.cc](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/cpp/serve/radix_tree.cc)
 - [cpp/serve/request.cc](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/cpp/serve/request.cc)
 - [cpp/serve/request.h](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/cpp/serve/request.h)
 - [cpp/serve/request_state.cc](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/cpp/serve/request_state.cc)
 - [cpp/serve/request_state.h](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/cpp/serve/request_state.h)
 - [cpp/serve/threaded_engine.cc](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/cpp/serve/threaded_engine.cc)
 - [cpp/serve/threaded_engine.h](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/cpp/serve/threaded_engine.h)
 - [cpp/tokenizers/streamer.cc](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/cpp/tokenizers/streamer.cc)
 - [cpp/tokenizers/tokenizers.cc](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/cpp/tokenizers/tokenizers.cc)
 - [ios/MLCSwift/Package.swift](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/ios/MLCSwift/Package.swift)
 - [ios/MLCSwift/Sources/ObjC/LLMEngine.mm](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/ios/MLCSwift/Sources/ObjC/LLMEngine.mm)
 - [ios/README.md](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/ios/README.md?plain=1)
 - [site/index.md](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/site/index.md?plain=1)
 - [web/Makefile](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/web/Makefile)
 - [web/emcc/mlc_wasm_runtime.cc](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/web/emcc/mlc_wasm_runtime.cc)
 
  
## Purpose and Scope

 This document provides a comprehensive architectural overview of the MLC LLM system. It describes the interaction between the two major phases (compile-time and runtime), the role of TVM/Relax as the compiler backend, and how the C++ engine, Python serving layer, and mobile SDKs fit together to enable high-performance LLM deployment across diverse platforms.

 For detailed information about specific subsystems, see:

 
 - Compilation pipeline implementation: [Compilation System](https://deepwiki.com/mlc-ai/mlc-llm/4-compilation-system)
 - C++ runtime engine internals: [C++ Runtime Engine](https://deepwiki.com/mlc-ai/mlc-llm/5-c++-runtime-engine)
 - Python serving layer: [Python Serving Layer](https://deepwiki.com/mlc-ai/mlc-llm/6-python-serving-layer)
 - Platform-specific deployment: [Deployment Guide](https://deepwiki.com/mlc-ai/mlc-llm/7-deployment-guide)
 
 **Sources**: [README.md16-18](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/README.md?plain=1#L16-L18) [site/index.md9-13](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/site/index.md?plain=1#L9-L13)

 
---

 
## Core Design Principles

 MLC LLM is built on three fundamental architectural principles:

 
### 1. Compilation-Runtime Separation

 Models are compiled once into optimized executables and can be deployed repeatedly across different platforms without recompilation. The compilation system transforms high-level model definitions into hardware-specific kernels, while the runtime engine executes these compiled artifacts.

 
### 2. Universal Cross-Platform Portability

 A single codebase supports NVIDIA, AMD, Apple, and Intel GPUs, as well as mobile devices (iOS, Android) and web browsers. This is achieved through TVM's abstraction layer and platform-specific backends (CUDA, Metal, Vulkan, OpenCL, WebGPU).

 
### 3. ML Compilation for Performance

 Rather than relying on fixed operator libraries, MLC LLM uses machine learning compilation (MLC) to automatically generate optimized kernels for each target hardware, enabling peak performance without manual tuning.

 **Sources**: [README.md10-63](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/README.md?plain=1#L10-L63)

 
---

 
## Overall System Architecture

 The following diagram bridges the high-level system components with the specific code entities that implement them.

 
```

```

 The system consists of three major layers:

 
 - **Serving Layer**: Manages OpenAI-compatible API endpoints and asynchronous request handling in Python.
 - **Runtime Core**: A high-performance C++ engine (`ThreadedEngine`) that manages the request lifecycle, KV cache, and model execution.
 - **Compiler Backend**: TVM Unity (Relax/TensorIR) provides the optimized kernels and execution environment (VM).
 
 **Sources**: [cpp/serve/engine.cc6-37](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/cpp/serve/engine.cc#L6-L37) [cpp/json_ffi/json_ffi_engine.cc21-28](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/cpp/json_ffi/json_ffi_engine.cc#L21-L28) [cpp/serve/model.cc31-37](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/cpp/serve/model.cc#L31-L37)

 
---

 
## Compilation vs Runtime Separation

 MLC LLM strictly separates the compilation phase from the runtime phase, enabling a "compile once, deploy everywhere" workflow.

 
```

```

 
### Compilation Phase

 During compilation, the system:

 
 - Converts model weights to quantized format.
 - Generates `mlc-chat-config.json` using `gen_config`.
 - Compiles the model through TVM's optimization pipeline into a `Module`.
 
 
### Runtime Phase

 During runtime, the `Model::Create` function [cpp/serve/model.cc31-37](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/cpp/serve/model.cc#L31-L37) loads the compiled library and weights. The `ThreadedEngine` [cpp/serve/threaded_engine.cc](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/cpp/serve/threaded_engine.cc) then orchestrates inference by executing `EngineAction` steps such as prefill and decode.

 **Sources**: [cpp/serve/model.cc31-37](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/cpp/serve/model.cc#L31-L37) [cpp/serve/engine.cc176-182](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/cpp/serve/engine.cc#L176-L182)

 
---

 
## C++ Engine Architecture

 The C++ engine is the heart of MLC LLM, responsible for high-throughput, low-latency inference.

 
```

```

 
### Key Components:

 
 - **`EngineState`**: Maintains the `running_queue` and `waiting_queue` of requests [cpp/serve/engine_state.h](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/cpp/serve/engine_state.h)
 - **`RequestModelState`**: Stores the state of a request (tokens, slots, grammar) for a specific model [cpp/serve/request_state.h36-127](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/cpp/serve/request_state.h#L36-L127)
 - **`FunctionTable`**: A registry of TVM PackedFunctions (e.g., `prefill`, `decode`) that the engine calls to perform tensor computations [cpp/serve/function_table.h48-144](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/cpp/serve/function_table.h#L48-L144)
 - **`ModelImpl`**: Implements high-level operations like `TokenEmbed`, `BatchPrefill`, and `BatchDecode` by dispatching to the `FunctionTable` [cpp/serve/model.cc58-182](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/cpp/serve/model.cc#L58-L182)
 
 **Sources**: [cpp/serve/request_state.h36-127](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/cpp/serve/request_state.h#L36-L127) [cpp/serve/function_table.h48-144](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/cpp/serve/function_table.h#L48-L144) [cpp/serve/model.cc58-182](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/cpp/serve/model.cc#L58-L182)

 
---

 
## Multi-GPU and Distributed Execution

 MLC LLM uses **Disco** (TVM's distributed runtime) to support multi-GPU execution via tensor and pipeline parallelism.

 
```

```

 When `num_shards` or `num_stages` is greater than 1, the `FunctionTable` initializes a Disco session [cpp/serve/function_table.cc67-101](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/cpp/serve/function_table.cc#L67-L101) It uses `runtime.disco.load_vm_module` to load the model across all workers and wraps session functions as `PackedFunc` for the engine to call transparently [cpp/serve/function_table.cc53-65](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/cpp/serve/function_table.cc#L53-L65)

 **Sources**: [cpp/serve/function_table.cc53-101](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/cpp/serve/function_table.cc#L53-L101) [cpp/multi_gpu/multi_gpu_loader.cc1-20](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/cpp/multi_gpu/multi_gpu_loader.cc#L1-L20)

 
---

 
## Mobile and Web Integration

 The architecture is designed to be embedded into various environments via a unified FFI layer.

 
### JSONFFIEngine

 The `JSONFFIEngine` [cpp/json_ffi/json_ffi_engine.cc21-29](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/cpp/json_ffi/json_ffi_engine.cc#L21-L29) provides a string-based interface (JSON) that is easy to call from language-specific wrappers:

 
 - **iOS**: Wrapped by `LLMEngine.mm` (ObjC++) and `MLCEngine.swift` [ios/MLCSwift/Sources/ObjC/LLMEngine.mm](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/ios/MLCSwift/Sources/ObjC/LLMEngine.mm)
 - **Android**: Integrated via the `mlc4j` JNI layer [android/mlc4j/CMakeLists.txt](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/android/mlc4j/CMakeLists.txt)
 - **Web**: Compiled to WebAssembly and interacted with via `WebLLM` [web/Makefile](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/web/Makefile)
 
 **Sources**: [cpp/json_ffi/json_ffi_engine.cc21-29](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/cpp/json_ffi/json_ffi_engine.cc#L21-L29) [ios/MLCSwift/Sources/ObjC/LLMEngine.mm27-122](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/ios/MLCSwift/Sources/ObjC/LLMEngine.mm#L27-L122) [README.md47-58](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/README.md?plain=1#L47-L58)
