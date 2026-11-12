<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/onnxruntime · page 5 Language Bindings · fetched 2026-10-21 -->

# Language Bindings

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [include/onnxruntime/core/session/onnxruntime_c_api.h](include/onnxruntime/core/session/onnxruntime_c_api.h)
- [include/onnxruntime/core/session/onnxruntime_cxx_api.h](include/onnxruntime/core/session/onnxruntime_cxx_api.h)
- [include/onnxruntime/core/session/onnxruntime_cxx_inline.h](include/onnxruntime/core/session/onnxruntime_cxx_inline.h)
- [include/onnxruntime/core/session/onnxruntime_lite_custom_op.h](include/onnxruntime/core/session/onnxruntime_lite_custom_op.h)
- [onnxruntime/core/framework/session_options.h](onnxruntime/core/framework/session_options.h)
- [onnxruntime/core/session/abi_session_options.cc](onnxruntime/core/session/abi_session_options.cc)
- [onnxruntime/core/session/custom_ops.cc](onnxruntime/core/session/custom_ops.cc)
- [onnxruntime/core/session/inference_session.cc](onnxruntime/core/session/inference_session.cc)
- [onnxruntime/core/session/inference_session.h](onnxruntime/core/session/inference_session.h)
- [onnxruntime/core/session/onnxruntime_c_api.cc](onnxruntime/core/session/onnxruntime_c_api.cc)
- [onnxruntime/core/session/ort_apis.h](onnxruntime/core/session/ort_apis.h)
- [onnxruntime/core/session/standalone_op_invoker.cc](onnxruntime/core/session/standalone_op_invoker.cc)
- [onnxruntime/test/framework/inference_session_test.cc](onnxruntime/test/framework/inference_session_test.cc)
- [onnxruntime/test/shared_lib/custom_op_utils.cc](onnxruntime/test/shared_lib/custom_op_utils.cc)
- [onnxruntime/test/shared_lib/custom_op_utils.h](onnxruntime/test/shared_lib/custom_op_utils.h)
- [onnxruntime/test/shared_lib/test_inference.cc](onnxruntime/test/shared_lib/test_inference.cc)
- [onnxruntime/test/testdata/custom_op_library/cpu/cpu_ops.cc](onnxruntime/test/testdata/custom_op_library/cpu/cpu_ops.cc)
- [onnxruntime/test/testdata/custom_op_library/custom_op_library.cc](onnxruntime/test/testdata/custom_op_library/custom_op_library.cc)
- [onnxruntime/test/testdata/fuse_select_filter.onnx](onnxruntime/test/testdata/fuse_select_filter.onnx)
- [onnxruntime/test/testdata/fuse_select_filter_opset_8.onnx](onnxruntime/test/testdata/fuse_select_filter_opset_8.onnx)
- [onnxruntime/test/testdata/merge.onnx](onnxruntime/test/testdata/merge.onnx)
- [onnxruntime/test/testdata/optional_2.onnx](onnxruntime/test/testdata/optional_2.onnx)
- [onnxruntime/test/testdata/optional_3.onnx](onnxruntime/test/testdata/optional_3.onnx)

</details>



## Purpose and Scope

This document describes ONNX Runtime's language bindings, which provide programmatic interfaces for loading models and running inference from different programming languages. The primary APIs are the C API (the foundational interface), the C++ API (a header-only wrapper), and Python bindings (via pybind11). For information about the training-specific APIs, see [Training System](#8).

The language bindings handle:
- Model loading and session lifecycle management
- Input/output tensor creation and memory management
- Inference execution across different execution providers
- Configuration of session options and runtime parameters
- Advanced features like IOBinding for zero-copy operations

---

## API Architecture Overview

ONNX Runtime uses a layered architecture where the C API forms the stable ABI (Application Binary Interface) foundation, with higher-level language bindings built on top.

```mermaid
graph TB
    subgraph "Application Code"
        PythonApp["Python Application"]
        CppApp["C++ Application"]
        CApp["C Application"]
        CSharpApp["C# Application"]
        JavaApp["Java Application"]
        ObjectiveCApp["Objective-C/Swift Application"]
        RustApp["Rust Application"]
        GoApp["Go Application"]
    end
    
    subgraph "Language Bindings Layer"
        PythonBinding["Python Bindings<br/>onnxruntime_pybind_state.cc<br/>InferenceSession class"]
        CppAPI["C++ API<br/>onnxruntime_cxx_api.h<br/>Ort::Session, Ort::Value"]
        CSharpBinding["C# Bindings<br/>P/Invoke layer"]
        JavaBinding["Java Bindings<br/>JNI layer"]
        ObjectiveCBinding["Objective-C/Swift Pod"]
        RustBinding["Rust Bindings"]
        GoBinding["Go Bindings"]
    end
    
    subgraph "C API Layer"
        OrtApi["OrtApi struct<br/>onnxruntime_c_api.h<br/>Function pointers"]
        OrtApiImpl["C API Implementation<br/>onnxruntime_c_api.cc"]
    end
    
    subgraph "Core Runtime"
        InferenceSession["InferenceSession<br/>C++ class"]
        OrtValue["OrtValue<br/>Tensor representation"]
        SessionState["SessionState<br/>Execution context"]
    end
    
    PythonApp --> PythonBinding
    CppApp --> CppAPI
    CApp --> OrtApi
    CSharpApp --> CSharpBinding
    JavaApp --> JavaBinding
    ObjectiveCApp --> ObjectiveCBinding
    RustApp --> RustBinding
    GoApp --> GoBinding
    
    PythonBinding --> OrtApi
    CppAPI --> OrtApi
    CSharpBinding --> OrtApi
    JavaBinding --> OrtApi
    ObjectiveCBinding --> OrtApi
    RustBinding --> OrtApi
    GoBinding --> OrtApi
    
    OrtApi --> OrtApiImpl
    OrtApiImpl --> InferenceSession
    OrtApiImpl --> OrtValue
    InferenceSession --> SessionState
    
    style OrtApi fill:#f9f,stroke:#333,stroke-width:2px
    style PythonBinding fill:#bbf,stroke:#333,stroke-width:2px
    style CppAPI fill:#bbf,stroke:#333,stroke-width:2px
```

**Sources:** [include/onnxruntime/core/session/onnxruntime_c_api.h:1-913](), [onnxruntime/python/onnxruntime_pybind_state.cc:1-100](), [include/onnxruntime/core/session/onnxruntime_cxx_api.h:1-250]()

---

## C API: Foundation Layer

### API Structure and Versioning

The C API is defined through the `OrtApi` struct, which contains function pointers for all runtime operations. This design ensures ABI stability across versions.

```mermaid
graph LR
    subgraph "API Entry Point"
        OrtGetApiBase["OrtGetApiBase()<br/>Global function"]
        OrtApiBase["OrtApiBase struct<br/>GetApi() method"]
    end
    
    subgraph "Versioned API"
        OrtApi["OrtApi struct<br/>Function pointers<br/>ORT_API_VERSION 31"]
    end
    
    subgraph "Core API Functions"
        CreateEnv["CreateEnv()"]
        CreateSession["CreateSession()"]
        Run["Run()"]
        CreateTensor["CreateTensorWithDataAsOrtValue()"]
        ReleaseSession["ReleaseSession()"]
    end
    
    subgraph "Opaque Types"
        OrtEnv["OrtEnv*<br/>Environment"]
        OrtSession["OrtSession*<br/>Inference session"]
        OrtValue["OrtValue*<br/>Tensor/value"]
        OrtStatus["OrtStatus*<br/>Error status"]
    end
    
    OrtGetApiBase --> OrtApiBase
    OrtApiBase --> OrtApi
    
    OrtApi --> CreateEnv
    OrtApi --> CreateSession
    OrtApi --> Run
    OrtApi --> CreateTensor
    OrtApi --> ReleaseSession
    
    CreateEnv --> OrtEnv
    CreateSession --> OrtSession
    CreateTensor --> OrtValue
    CreateEnv --> OrtStatus
```

**API Version Constant:** The current API version is defined as `ORT_API_VERSION 31` at [include/onnxruntime/core/session/onnxruntime_c_api.h:43]().

**Entry Point:** Applications access the API through `OrtGetApiBase()` at [onnxruntime/core/session/ort_apis.h:6](), which returns an `OrtApiBase` pointer containing a versioned `GetApi()` function.

**Sources:** [include/onnxruntime/core/session/onnxruntime_c_api.h:37-913](), [onnxruntime/core/session/ort_apis.h:1-250]()

### Core C API Types

| Type | Purpose | Lifecycle Management |
|------|---------|---------------------|
| `OrtEnv` | Global environment and logging manager | `CreateEnv()` / `ReleaseEnv()` |
| `OrtSession` | Loaded model and execution context | `CreateSession()` / `ReleaseSession()` |
| `OrtSessionOptions` | Configuration for session creation | `CreateSessionOptions()` / `ReleaseSessionOptions()` |
| `OrtValue` | Input/output tensors and values | `CreateTensorAsOrtValue()` / `ReleaseValue()` |
| `OrtMemoryInfo` | Memory allocation location descriptor | `CreateCpuMemoryInfo()` / `ReleaseMemoryInfo()` |
| `OrtRunOptions` | Per-inference runtime configuration | `CreateRunOptions()` / `ReleaseRunOptions()` |
| `OrtIoBinding` | Pre-bound input/output buffers | `CreateIoBinding()` / `ReleaseIoBinding()` |
| `OrtStatus` | Error status and message | Return value from most API calls / `ReleaseStatus()` |

**Type Definitions:** All opaque types are defined using the `ORT_RUNTIME_CLASS` macro at [include/onnxruntime/core/session/onnxruntime_c_api.h:294-332]().

**Memory Management Pattern:** All `Create*()` functions allocate resources that must be freed with corresponding `Release*()` functions. The `OrtStatus*` return value indicates success (nullptr) or error (non-null pointer that must be released).

**Sources:** [include/onnxruntime/core/session/onnxruntime_c_api.h:294-332](), [onnxruntime/core/session/onnxruntime_c_api.cc:1-100]()

### Session Lifecycle in C API

```mermaid
sequenceDiagram
    participant App as "C Application"
    participant API as "OrtApi"
    participant Impl as "C API Implementation"
    participant Session as "InferenceSession"
    
    App->>API: CreateEnv(log_level, log_id, &env)
    API->>Impl: OrtApis::CreateEnv
    Impl->>Impl: OrtEnv::GetInstance()
    Impl-->>App: OrtStatus* (nullptr = success)
    
    App->>API: CreateSessionOptions(&options)
    API->>Impl: OrtApis::CreateSessionOptions
    Impl-->>App: OrtSessionOptions*
    
    App->>API: SetSessionGraphOptimizationLevel(options, level)
    App->>API: SetIntraOpNumThreads(options, threads)
    
    App->>API: CreateSession(env, model_path, options, &session)
    API->>Impl: OrtApis::CreateSession
    Impl->>Session: new InferenceSession()
    Impl->>Session: Load(model_path)
    Impl->>Session: Initialize()
    Impl-->>App: OrtSession*
    
    App->>API: CreateTensorWithDataAsOrtValue(info, data, shape, type, &input_tensor)
    API->>Impl: CreateTensorImpl
    Impl-->>App: OrtValue*
    
    App->>API: Run(session, run_options, input_names, inputs, output_names, &outputs)
    API->>Impl: OrtApis::Run
    Impl->>Session: InferenceSession::Run()
    Session-->>Impl: std::vector<OrtValue>
    Impl-->>App: OrtValue** (output array)
    
    App->>API: ReleaseValue(input_tensor)
    App->>API: ReleaseValue(outputs[0])
    App->>API: ReleaseSession(session)
    App->>API: ReleaseSessionOptions(options)
    App->>API: ReleaseEnv(env)
```

**Implementation:** Session creation is implemented in [onnxruntime/core/session/onnxruntime_c_api.cc:47-51]() with the `CreateSession` function wrapping the C++ `InferenceSession` class from [onnxruntime/core/session/inference_session.h:171](). The `CreateTensorImpl` function is used for tensor creation [onnxruntime/core/session/onnxruntime_c_api.cc:136-142]().

**Sources:** [onnxruntime/core/session/onnxruntime_c_api.cc:1-300](), [onnxruntime/core/session/ort_apis.h:47-51]()

---

## C++ API: Header-Only Wrapper

The C++ API provides RAII (Resource Acquisition Is Initialization) wrappers around the C API, converting error codes to exceptions and automating memory management.

### Key C++ Wrapper Classes

```mermaid
graph TB
    subgraph "Ort Namespace"
        Env["Ort::Env<br/>RAII wrapper for OrtEnv*<br/>Manages global state"]
        Session["Ort::Session<br/>RAII wrapper for OrtSession*<br/>Loads and runs models"]
        Value["Ort::Value<br/>RAII wrapper for OrtValue*<br/>Tensor operations"]
        SessionOptions["Ort::SessionOptions<br/>RAII wrapper for OrtSessionOptions*"]
        RunOptions["Ort::RunOptions<br/>RAII wrapper for OrtRunOptions*"]
        MemoryInfo["Ort::MemoryInfo<br/>RAII wrapper for OrtMemoryInfo*"]
        IoBinding["Ort::IoBinding<br/>RAII wrapper for OrtIoBinding*"]
        Allocator["Ort::Allocator<br/>Memory allocation interface"]
    end
    
    subgraph "Base Template"
        Base["detail::Base<T><br/>Common RAII pattern<br/>Stores T* p_<br/>Destructor calls Release"]
    end
    
    Env --> Base
    Session --> Base
    Value --> Base
    SessionOptions --> Base
    RunOptions --> Base
    MemoryInfo --> Base
    IoBinding --> Base
```

**Template Base:** All wrapper classes inherit from `detail::Base<T>` which stores the underlying C pointer and calls the appropriate `Release*()` function in the destructor. Defined at [include/onnxruntime/core/session/onnxruntime_cxx_api.h:1-100]().

**Exception Handling:** The `ThrowOnError()` helper function converts `OrtStatus*` into `Ort::Exception`, defined at [include/onnxruntime/core/session/onnxruntime_cxx_inline.h:44-55]().

**Sources:** [include/onnxruntime/core/session/onnxruntime_cxx_api.h:1-500](), [include/onnxruntime/core/session/onnxruntime_cxx_inline.h:1-100]()

### C++ API Usage Pattern

The C++ API eliminates manual memory management:

**Env Creation:** `Ort::Env env(ORT_LOGGING_LEVEL_WARNING, "test");` automatically releases the `OrtEnv*` when `env` goes out of scope. Constructor at [include/onnxruntime/core/session/onnxruntime_cxx_api.h:800-900]().

**Session Creation:** `Ort::Session session(env, model_path, session_options);` throws `Ort::Exception` on error instead of returning status. Constructor at [include/onnxruntime/core/session/onnxruntime_cxx_api.h:1200-1300]().

**Running Inference:**
```cpp
// Input tensor from raw data
Ort::Value input_tensor = Ort::Value::CreateTensor<float>(
    memory_info, input_data, input_size, shape, shape_len);

// Run inference
std::vector<Ort::Value> outputs = session.Run(
    run_options, input_names, &input_tensor, 1, output_names, 1);
```

**Type Safety:** The C++ API includes `TypeToTensorType<T>` template to map C++ types to `ONNXTensorElementDataType` at [include/onnxruntime/core/session/onnxruntime_cxx_inline.h:86-156]().

**Sources:** [include/onnxruntime/core/session/onnxruntime_cxx_api.h:1-2000](), [onnxruntime/test/shared_lib/test_inference.cc:260-335]()

---

## Python Bindings Architecture

### pybind11 Module Structure

Python bindings are implemented using pybind11 to expose C++ functionality. The main module is defined in `onnxruntime_pybind_state.cc`.

```mermaid
graph TB
    subgraph "Python Module: onnxruntime.capi._pybind_state"
        Module["PYBIND11_MODULE(onnxruntime_pybind11_state)<br/>Entry point"]
    end
    
    subgraph "Exposed Classes"
        PySession["PyInferenceSession<br/>Wraps InferenceSession*"]
        PySessionOptions["PySessionOptions<br/>Wraps SessionOptions"]
        PyRunOptions["PyRunOptions<br/>Wraps RunOptions"]
        PyOrtValue["PyOrtValue<br/>OrtValue with numpy integration"]
        PyIoBinding["PyIoBinding<br/>Wraps IOBinding"]
        PyEnv["PyEnv<br/>Wraps OrtEnv"]
    end
    
    subgraph "Helper Functions"
        GetDevice["GetDevice()<br/>Convert device string to OrtDevice"]
        AddTensor["AddTensorAsPyObj()<br/>OrtValue to numpy array"]
        GetPyObj["GetPyObjFromTensor()<br/>Tensor to Python object"]
        CreateOrtValue["CreateOrtValueFromNumpy()<br/>numpy to OrtValue"]
    end
    
    subgraph "C++ Core"
        InferenceSession["InferenceSession C++ class"]
        OrtValue["OrtValue C++ class"]
    end
    
    Module --> PySession
    Module --> PySessionOptions
    Module --> PyRunOptions
    Module --> PyOrtValue
    Module --> PyIoBinding
    Module --> PyEnv
    
    PySession --> InferenceSession
    PyOrtValue --> OrtValue
    
    PySession --> AddTensor
    PySession --> GetPyObj
    PyOrtValue --> CreateOrtValue
    
    GetDevice --> GetPyObj
```

**Module Definition:** The pybind11 module is defined at [onnxruntime/python/onnxruntime_pybind_state.cc:1-100]() using the `PYBIND11_MODULE` macro.

**Sources:** [onnxruntime/python/onnxruntime_pybind_state.cc:1-200](), [onnxruntime/python/onnxruntime_pybind_state_common.h:1-150]()

### InferenceSession Python Class

The high-level Python API is provided by the `InferenceSession` class in `onnxruntime_inference_collection.py`, which wraps the pybind11-exposed `PyInferenceSession`.

**Class Structure:**

| Method | Purpose | Implementation |
|--------|---------|----------------|
| `__init__(model_path, sess_options, providers)` | Load model and create session | [onnxruntime/python/onnxruntime_inference_collection.py:1-100]() |
| `run(output_names, input_feed, run_options)` | Execute inference | Calls `PyInferenceSession.run()` |
| `get_inputs()` | Retrieve input metadata | Returns `NodeArg` information |
| `get_outputs()` | Retrieve output metadata | Returns `NodeArg` information |
| `get_providers()` | List active execution providers | Query session state |
| `set_providers(providers, provider_options)` | Configure execution providers | Must be called before session creation |

**Initialization Flow:**
1. Parse `providers` argument to determine execution provider order
2. Create `SessionOptions` with configuration (graph optimization level, threading, etc.)
3. Append execution providers in specified order
4. Call underlying C++ `InferenceSession` constructor via pybind11
5. Load and initialize model

**Run Method:** The `run()` method at [onnxruntime/python/onnxruntime_inference_collection.py:200-300]() converts Python inputs (numpy arrays, lists) to `OrtValue` objects, executes inference, and converts outputs back to numpy arrays.

**Sources:** [onnxruntime/python/onnxruntime_inference_collection.py:1-500](), [onnxruntime/test/python/onnxruntime_test_python.py:51-150]()

### OrtValue and NumPy Integration

`OrtValue` is the internal representation of tensors and other data types. The Python bindings provide seamless conversion between `OrtValue` and NumPy arrays.

```mermaid
graph LR
    subgraph "Python Space"
        NumpyArray["numpy.ndarray<br/>Python array object"]
        PythonList["Python list/dict<br/>Input data"]
    end
    
    subgraph "Conversion Layer"
        CreateFromNumpy["CreateOrtValueFromNumpy()<br/>Zero-copy if possible"]
        TensorToNumpy["PrimitiveTensorToNumpyOverOrtValue()<br/>Returns view with capsule"]
        StringTensor["StringTensorToNumpyArray()<br/>Copy string data"]
        GetPyObj["GetPyObjFromTensor()<br/>Dispatch by type"]
    end
    
    subgraph "ORT Internal"
        OrtValue["OrtValue<br/>Contains Tensor*"]
        Tensor["Tensor<br/>Data + shape + type"]
        TensorData["Tensor data buffer<br/>CPU or device memory"]
    end
    
    NumpyArray --> CreateFromNumpy
    PythonList --> CreateFromNumpy
    CreateFromNumpy --> OrtValue
    
    OrtValue --> GetPyObj
    GetPyObj --> TensorToNumpy
    GetPyObj --> StringTensor
    TensorToNumpy --> NumpyArray
    StringTensor --> NumpyArray
    
    OrtValue --> Tensor
    Tensor --> TensorData
```

**Zero-Copy Optimization:** For CPU tensors with numeric types, `PrimitiveTensorToNumpyOverOrtValue()` at [onnxruntime/python/onnxruntime_pybind_state.cc:225-244]() creates a NumPy array that references the original `OrtValue` data without copying. A Python capsule with a custom destructor ensures the `OrtValue` remains alive.

**Device Memory Handling:** For GPU tensors, `PrimitiveTensorToNumpyFromDevice()` at [onnxruntime/python/onnxruntime_pybind_state.cc:246-261]() allocates CPU memory and copies data from device using the `DataTransferManager`.

**String Tensors:** String tensors always require copying since they must be converted to Python string objects, handled by `StringTensorToNumpyArray()` at [onnxruntime/python/onnxruntime_pybind_state.cc:214-223]().

**Sources:** [onnxruntime/python/onnxruntime_pybind_state.cc:214-460](), [onnxruntime/python/onnxruntime_pybind_mlvalue.cc:1-200]()

---

## C# Bindings

The C# bindings for ONNX Runtime are provided through a .NET API, typically consumed via NuGet packages. They leverage Platform Invoke (P/Invoke) to call the underlying C API functions.

**High-Level Overview:**
- **NuGet Packages:** Distributed as `Microsoft.ML.OnnxRuntime` and `Microsoft.ML.OnnxRuntime.Gpu` (and other provider-specific packages).
- **P/Invoke Layer:** C# methods are declared with `[DllImport]` attributes to map to the C API functions.
- **`InferenceSession`:** The primary class for loading models and running inference, mirroring the C++ `InferenceSession`.
- **`OrtValue`:** Represents tensors and other ONNX data types, with methods for creating from and converting to .NET types.

For details, see [C# Bindings](#5.3).

---

## IOBinding and Advanced Memory Management

### IOBinding Concept

`IOBinding` allows pre-allocating output buffers and binding inputs/outputs to specific memory locations, enabling zero-copy operations and better control over memory placement.

```mermaid
graph TB
    subgraph "User Code"
        AllocOutput["Allocate output buffer<br/>on target device"]
        CreateValue["Wrap buffer in OrtValue"]
    end
    
    subgraph "IOBinding API"
        CreateBinding["CreateIoBinding(session)<br/>C: OrtIoBinding*<br/>Python: IOBinding"]
        BindInput["BindInput(name, value)<br/>Associate input with tensor"]
        BindOutput["BindOutput(name, value)<br/>Pre-allocate output"]
        BindOutputDevice["BindOutputToDevice(name, mem_info)<br/>Runtime allocation"]
        GetOutputs["GetOutputValues()<br/>Retrieve results"]
    end
    
    subgraph "Session Execution"
        RunWithBinding["Run(run_options, io_binding)<br/>Execute with bound I/O"]
        SessionState["Access pre-bound tensors"]
        WriteOutput["Write to bound output buffer"]
    end
    
    AllocOutput --> CreateValue
    CreateValue --> BindOutput
    
    BindInput --> CreateBinding
    BindOutput --> CreateBinding
    BindOutputDevice --> CreateBinding
    
    CreateBinding --> RunWithBinding
    RunWithBinding --> SessionState
    SessionState --> WriteOutput
    WriteOutput --> GetOutputs
    
    style CreateBinding fill:#f9f,stroke:#333,stroke-width:2px
    style RunWithBinding fill:#f9f,stroke:#333,stroke-width:2px
```

**C API Functions:**
- `OrtApi::CreateIoBinding()` - Create binding object at [onnxruntime/core/session/onnxruntime_c_api.cc:1-100]()
- `OrtApi::BindInput()` - Bind input tensor at [onnxruntime/core/session/onnxruntime_c_api.cc:100-200]()
- `OrtApi::BindOutput()` - Bind pre-allocated output at [onnxruntime/core/session/onnxruntime_c_api.cc:200-300]()
- `OrtApi::BindOutputToDevice()` - Bind to device with runtime allocation at [onnxruntime/core/session/onnxruntime_c_api.cc:300-400]()

**Sources:** [onnxruntime/core/session/onnxruntime_c_api.cc:1-500](), [onnxruntime/core/session/IOBinding.h:1-100](), [onnxruntime/python/onnxruntime_inference_collection.py:500-700]()

### Device Memory Management

ONNX Runtime supports multiple device types for tensor allocation. The `OrtMemoryInfo` struct describes memory location.

**Device Types:**

| Device Type | Constant | Description |
|-------------|----------|-------------|
| CPU | `OrtDevice::CPU` | Host memory |
| CUDA | `OrtDevice::GPU` | NVIDIA GPU memory |
| DML | `OrtDevice::DML` | DirectML (Windows GPU) |
| NPU | `OrtDevice::NPU` | Neural Processing Unit |
| CANN | `OrtDevice::CANN` | Huawei Ascend NPU |

**OrtDevice Structure:** Defined at [include/onnxruntime/core/session/onnxruntime_c_api.h:478-496]() with fields for device type, vendor ID, device ID, and memory type.

**Allocator Selection:** Each execution provider registers allocators for its device type. The `AllocatorManager` selects the appropriate allocator based on `OrtMemoryInfo`. See [onnxruntime/core/framework/allocator.h:1-100]().

**Python Device Specification:** The `get_ort_device_type()` function at [onnxruntime/python/onnxruntime_inference_collection.py:24-40]() converts device strings ("cuda", "cpu", "dml") to `OrtDevice` constants.

**Sources:** [include/onnxruntime/core/session/onnxruntime_c_api.h:463-496](), [onnxruntime/python/onnxruntime_inference_collection.py:24-40]()

### Zero-Copy Operations with IOBinding

IOBinding enables efficient inference pipelines by eliminating unnecessary memory copies.

**Python IOBinding Usage Example Pattern:**

```python
# Create session
session = onnxruntime.InferenceSession("model.onnx", providers=["CUDAExecutionProvider"])

# Create IOBinding
io_binding = session.io_binding()

# Bind input (already on GPU)
input_ortvalue = onnxruntime.OrtValue.ortvalue_from_numpy(input_array, "cuda", 0)
io_binding.bind_input("input_name", input_ortvalue)

# Bind output to device (runtime allocation)
io_binding.bind_output("output_name", "cuda")

# Run inference - no host/device copies
session.run_with_iobinding(io_binding)

# Get outputs (still on GPU)
outputs = io_binding.get_outputs()
```

**Implementation:** The `PyIoBinding` class at [onnxruntime/python/onnxruntime_pybind_state.cc:1-100]() wraps the C++ `IOBinding` class from [onnxruntime/core/session/IOBinding.h:1-100]().

**Memory Copy Elimination:**
1. Input tensors already on device (GPU) can be bound directly without CPU→GPU copy
2. Output buffers allocated on device avoid GPU→CPU copy for subsequent operations
3. Multiple inferences can reuse the same IOBinding, avoiding repeated setup

For details, see [IOBinding and Memory Management](#5.4).

**Sources:** [onnxruntime/python/onnxruntime_inference_collection.py:400-600](), [onnxruntime/test/python/onnxruntime_test_python_iobinding.py:1-100](), [onnxruntime/core/session/IOBinding.h:1-118]()

---

## Java and Android Bindings

ONNX Runtime provides Java bindings, which are particularly useful for Android applications. These bindings use JNI (Java Native Interface) to interact with the underlying C API.

**High-Level Overview:**
- **Java API:** Classes like `OrtEnvironment` and `OrtSession` provide the Java-friendly interface.
- **JNI Layer:** Native methods in Java classes are implemented in C++ code that calls the ONNX Runtime C API.
- **Gradle Build:** Android AAR (Android Archive) packages are built using Gradle, integrating the native libraries.

For details, see [Java and Android Bindings](#5.5).

---

## Mobile and Other Language Bindings

ONNX Runtime extends its reach to mobile platforms and other programming languages to support a wide range of deployment scenarios.

**Objective-C/Swift:**
- **Pod:** An Objective-C/Swift pod is available for iOS and macOS development, providing an API similar to the C++ and C# bindings.
- **React Native:** A React Native module allows JavaScript applications to leverage ONNX Runtime on mobile devices.

**Rust and Go:**
- **Rust Bindings:** Provide a safe, idiomatic Rust interface to the ONNX Runtime C API.
- **Go Bindings:** Offer a Go language interface for integrating ONNX Runtime into Go applications.

These bindings are typically found in their respective language directories within the ONNX Runtime repository, often with samples demonstrating their usage.

For details, see [Mobile and Other Language Bindings](#5.6).

---

## Cross-Language Type Mapping

### Tensor Element Types

The type system must be consistent across C, C++, and Python interfaces.

| ONNX Type | C API Enum | C++ Type | NumPy Type | Code |
|-----------|------------|----------|------------|------|
| `float` | `ONNX_TENSOR_ELEMENT_DATA_TYPE_FLOAT` | `float` | `np.float32` | 1 |
| `double` | `ONNX_TENSOR_ELEMENT_DATA_TYPE_DOUBLE` | `double` | `np.float64` | 11 |
| `int8` | `ONNX_TENSOR_ELEMENT_DATA_TYPE_INT8` | `int8_t` | `np.int8` | 3 |
| `int16` | `ONNX_TENSOR_ELEMENT_DATA_TYPE_INT16` | `int16_t` | `np.int16` | 5 |
| `int32` | `ONNX_TENSOR_ELEMENT_DATA_TYPE_INT32` | `int32_t` | `np.int32` | 6 |
| `int64` | `ONNX_TENSOR_ELEMENT_DATA_TYPE_INT64` | `int64_t` | `np.int64` | 7 |
| `uint8` | `ONNX_TENSOR_ELEMENT_DATA_TYPE_UINT8` | `uint8_t` | `np.uint8` | 2 |
| `float16` | `ONNX_TENSOR_ELEMENT_DATA_TYPE_FLOAT16` | `Ort::Float16_t` | `np.float16` | 10 |
| `bfloat16` | `ONNX_TENSOR_ELEMENT_DATA_TYPE_BFLOAT16` | `Ort::BFloat16_t` | Custom | 16 |
| `string` | `ONNX_TENSOR_ELEMENT_DATA_TYPE_STRING` | `std::string` | `object` | 8 |
| `bool` | `ONNX_TENSOR_ELEMENT_DATA_TYPE_BOOL` | `bool` | `np.bool_` | 9 |

**Type Enum Definition:** `ONNXTensorElementDataType` enum at [include/onnxruntime/core/session/onnxruntime_c_api.h:193-212]().

**C++ Type Traits:** The `TypeToTensorType<T>` template at [include/onnxruntime/core/session/onnxruntime_cxx_inline.h:86-156]() maps C++ types to ONNX type enums.

**NumPy Conversion:** `OnnxRuntimeTensorToNumpyType()` function converts ONNX types to NumPy type codes, used in [onnxruntime/python/onnxruntime_pybind_state.cc:234]().

**Sources:** [include/onnxruntime/core/session/onnxruntime_c_api.h:193-212](), [include/onnxruntime/core/session/onnxruntime_cxx_inline.h:86-156](), [onnxruntime/python/numpy_helper.h:1-19]()

### Non-Tensor Types

ONNX Runtime also supports non-tensor types like sequences and maps (primarily for traditional ML models).

**ONNX Type Enum:** `ONNXType` enum at [include/onnxruntime/core/session/onnxruntime_c_api.h:215-223]() includes:
- `ONNX_TYPE_TENSOR` - Standard tensor
- `ONNX_TYPE_SEQUENCE` - Sequence of tensors (`TensorSeq`)
- `ONNX_TYPE_MAP` - Map types (key-value pairs)
- `ONNX_TYPE_OPTIONAL` - Optional value
- `ONNX_TYPE_SPARSETENSOR` - Sparse tensor format

**Python Handling:** Non-tensor outputs are converted by `AddNonTensorAsPyObj()` at [onnxruntime/python/onnxruntime_pybind_state.cc:415-454](), which dispatches to type-specific converters for maps and sequences.

**Sources:** [include/onnxruntime/core/session/onnxruntime_c_api.h:215-223](), [onnxruntime/python/onnxruntime_pybind_state.cc:415-454]()

---

## Provider Configuration Through APIs

### Provider Options

Each execution provider can be configured through provider-specific options passed at session creation.

**C API Provider Configuration:**
- `OrtApi::SessionOptionsAppendExecutionProvider_CUDA()` - Append CUDA EP with `OrtCUDAProviderOptions` struct
- `OrtApi::SessionOptionsAppendExecutionProvider()` - Generic append with string key-value pairs
- Provider option structs: `OrtCUDAProviderOptions` at [include/onnxruntime/core/session/onnxruntime_c_api.h:601-682](), `OrtTensorRTProviderOptions` at [include/onnxruntime/core/session/onnxruntime_c_api.h:777-799]()

**Python Provider Configuration:**

```python
providers = [
    ("CUDAExecutionProvider", {
        "device_id": 0,
        "gpu_mem_limit": 2 * 1024 * 1024 * 1024,  # 2GB
        "arena_extend_strategy": "kSameAsRequested",
        "cudnn_conv_algo_search": "EXHAUSTIVE",
        "do_copy_in_default_stream": True,
    }),
    "CPUExecutionProvider"  # Fallback
]
session = onnxruntime.InferenceSession("model.onnx", providers=providers)
```

**Provider Options Normalization:** The `check_and_normalize_provider_args()` function at [onnxruntime/python/onnxruntime_inference_collection.py:89-150]() validates and normalizes the `providers` and `provider_options` arguments.

**C++ Provider Configuration:**
```cpp
Ort::SessionOptions session_options;
OrtCUDAProviderOptions cuda_options;
cuda_options.device_id = 0;
cuda_options.gpu_mem_limit = SIZE_MAX;
session_options.AppendExecutionProvider_CUDA(cuda_options);
```

**Sources:** [include/onnxruntime/core/session/onnxruntime_c_api.h:601-833](), [onnxruntime/python/onnxruntime_inference_collection.py:89-200](), [onnxruntime/python/onnxruntime_pybind_state.cc:479-542]()

---

