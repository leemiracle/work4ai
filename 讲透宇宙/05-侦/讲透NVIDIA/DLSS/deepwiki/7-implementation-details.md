<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/DLSS · page 7 Implementation Details · fetched 2026-10-26 -->

# Implementation Details

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [include/nvsdk_ngx.h](include/nvsdk_ngx.h)
- [include/nvsdk_ngx_defs.h](include/nvsdk_ngx_defs.h)
- [lib/Windows_x86_64/dev/nvngx_dlss.dll](lib/Windows_x86_64/dev/nvngx_dlss.dll)
- [lib/Windows_x86_64/rel/nvngx_dlss.dll](lib/Windows_x86_64/rel/nvngx_dlss.dll)

</details>



This page provides in-depth technical information on the internal workings of NVIDIA DLSS (Deep Learning Super Sampling) for engineers and technical leads implementing or optimizing DLSS in their applications. For general integration guidance, see [NGX SDK Integration](#4), and for debugging tools, see [Debugging Tools](#7.1).

## DLSS Implementation Architecture

DLSS follows a layered architecture that separates the application interface from the core deep learning implementation. This architecture enables consistent performance across different graphics APIs while maintaining a clean integration path.

```mermaid
flowchart TD
    subgraph "Application Layer"
        App["Application"]
        RenderEngine["Rendering Engine"]
    end
    
    subgraph "NGX SDK Layer"
        NGX["NGX Framework"]
        Parameters["Parameter Interface"]
    end
    
    subgraph "DLSS Core Layer"
        DLSS["DLSS Core (nvngx_dlss.dll)"]
        Models["Neural Network Models"]
        Memory["Memory Management"]
    end
    
    subgraph "Hardware Layer"
        GPU["GPU Cores"]
        TensorCores["Tensor Cores"]
    end
    
    App --> RenderEngine
    RenderEngine --> NGX
    NGX <--> Parameters
    NGX --> DLSS
    DLSS --> Models
    DLSS --> Memory
    DLSS --> GPU
    DLSS --> TensorCores
    TensorCores --> RenderEngine
```

Sources: [include/nvsdk_ngx.h:14-67](), [lib/Windows_x86_64/dev/nvngx_dlss.dll]()

## Core Components

### Dynamic Libraries

DLSS functionality is primarily implemented in platform-specific binaries:

| Platform | Core Library | Description |
|----------|-------------|-------------|
| Windows | nvngx_dlss.dll | Core DLSS implementation for DirectX and CUDA |
| Linux | libnvidia-ngx-dlss.so | Core DLSS implementation for Vulkan |

These libraries contain the neural network models, inference code, and platform-specific optimizations needed to perform DLSS upscaling.

Sources: [lib/Windows_x86_64/dev/nvngx_dlss.dll](), [lib/Windows_x86_64/rel/nvngx_dlss.dll]()

### NGX Framework Interface

The NGX framework provides a consistent API across all NVIDIA AI features. For DLSS, the key interfaces are:

```mermaid
classDiagram
    class NVSDK_NGX_Parameter {
        +Set(ParameterId, Value)
        +Get(ParameterId, Value)
        +Reset()
    }
    
    class NGX_Handle {
        +unsigned long long Id
    }
    
    class NVSDK_NGX_API {
        +Init()
        +GetCapabilityParameters()
        +GetScratchBufferSize()
        +CreateFeature()
        +EvaluateFeature()
        +ReleaseFeature()
        +Shutdown()
    }
    
    NVSDK_NGX_API --> NVSDK_NGX_Parameter : creates
    NVSDK_NGX_API --> NGX_Handle : manages
```

Sources: [include/nvsdk_ngx.h:72-146](), [include/nvsdk_ngx_params.h]()

## Memory Model

DLSS requires several types of memory resources to function efficiently:

### Memory Buffer Types

1. **Input Buffers**: Low-resolution color buffer, motion vectors, depth buffer, and optional exposure textures
2. **Output Buffer**: High-resolution result texture
3. **Scratch Buffer**: Temporary workspace for computations
4. **State Buffer**: Internal persistent state maintaining temporal information between frames

```mermaid
flowchart LR
    subgraph "Application-Managed"
        InputBuffers["Input Buffers"]
        OutputBuffer["Output Buffer"]
        ScratchBuffer["Scratch Buffer"]
    end
    
    subgraph "DLSS-Managed"
        StateBuffer["State Buffer"]
        NetworkWeights["Neural Network Weights"]
    end
    
    InputBuffers --> DLSSProcessing["DLSS Processing"]
    ScratchBuffer --> DLSSProcessing
    StateBuffer <--> DLSSProcessing
    NetworkWeights --> DLSSProcessing
    DLSSProcessing --> OutputBuffer
```

Sources: [include/nvsdk_ngx.h:42-49]()

### Memory Requirements

DLSS memory requirements scale with resolution. The scratch buffer size needed can be queried via `NVSDK_NGX_[API]_GetScratchBufferSize()`. The internal state buffers are managed by the DLSS library itself.

## Execution Flow

### Initialization Sequence

```mermaid
sequenceDiagram
    participant App as Application
    participant NGX as NGX Framework
    participant DLSS as DLSS Library
    
    App->>NGX: NVSDK_NGX_[API]_Init(appId, dataPath, device)
    NGX->>NGX: Validate parameters
    NGX->>DLSS: Load DLSS library
    DLSS->>DLSS: Initialize internal state
    DLSS-->>NGX: Return initialization status
    NGX-->>App: Return result
```

Sources: [include/nvsdk_ngx.h:119-146]()

### Feature Creation

```mermaid
sequenceDiagram
    participant App as Application
    participant NGX as NGX Framework
    participant DLSS as DLSS Library
    
    App->>NGX: GetParameters()
    NGX-->>App: Return Parameter Interface
    App->>NGX: Set(Width, Height, etc)
    App->>NGX: GetScratchBufferSize()
    NGX->>DLSS: Calculate memory requirements
    DLSS-->>NGX: Return buffer size
    App->>App: Allocate scratch buffer
    App->>NGX: CreateFeature(DLSS)
    NGX->>DLSS: Initialize feature with parameters
    DLSS->>DLSS: Load AI models
    DLSS->>DLSS: Allocate state buffer
    DLSS-->>NGX: Return feature handle
    NGX-->>App: Return handle to application
```

Sources: [include/nvsdk_ngx.h:51-55]()

### Per-Frame Evaluation

```mermaid
sequenceDiagram
    participant App as Application
    participant NGX as NGX Framework
    participant DLSS as DLSS Library
    
    App->>App: Render low-resolution frame
    App->>App: Generate motion vectors and depth
    App->>NGX: Set input/output resources
    App->>NGX: EvaluateFeature(handle)
    NGX->>DLSS: Process frame with parameters
    DLSS->>DLSS: Apply temporal accumulation
    DLSS->>DLSS: Execute neural network
    DLSS->>DLSS: Update internal state
    DLSS-->>NGX: Write to output resource
    NGX-->>App: Return evaluation status
    App->>App: Present upscaled frame
```

Sources: [include/nvsdk_ngx.h:57-60]()

## Technical Details

### Quality Presets

DLSS provides several quality presets that determine the internal scaling ratio:

| Quality Preset | Approximate Scaling Ratio | Use Case |
|----------------|---------------------------|----------|
| Ultra Quality | ~1.3x | Maximum image quality with modest performance gain |
| Quality | ~1.5x | High image quality with good performance gain |
| Balanced | ~1.7x | Balance between quality and performance |
| Performance | ~2.0x | Prioritize performance |
| Ultra Performance | ~3.0x | Maximum performance gain |

Sources: Repository overview diagrams

### Render Presets

DLSS also supports render presets that affect the internal processing pipeline:

```mermaid
classDiagram
    class NVSDK_NGX_DLSS_Hint_Render_Preset {
        +Default
        +Preset_A
        +Preset_B
        +Preset_C
        +Preset_D
        +Preset_E
        +Preset_F
        +Preset_J
        +Preset_K
    }
```

Sources: [include/nvsdk_ngx_defs.h:60-77]()

### Supported Features

The `NVSDK_NGX_Feature` enumeration defines the feature ID for DLSS as `NVSDK_NGX_Feature_SuperSampling` (value 1) in the NGX framework.

Sources: [include/nvsdk_ngx_defs.h:148-184]()

## Platform-Specific Implementation

### Windows Implementation

On Windows, DLSS supports DirectX 11, DirectX 12, and CUDA through respective API functions:

```mermaid
flowchart TD
    subgraph "DirectX 11 Path"
        D3D11App["D3D11 Application"]
        D3D11Funcs["NVSDK_NGX_D3D11_* Functions"]
    end
    
    subgraph "DirectX 12 Path"
        D3D12App["D3D12 Application"]
        D3D12Funcs["NVSDK_NGX_D3D12_* Functions"]
    end
    
    subgraph "CUDA Path"
        CUDAApp["CUDA Application"]
        CUDAFuncs["NVSDK_NGX_CUDA_* Functions"]
    end
    
    D3D11App --> D3D11Funcs
    D3D12App --> D3D12Funcs
    CUDAApp --> CUDAFuncs
    
    D3D11Funcs --> DLSSDLL["nvngx_dlss.dll"]
    D3D12Funcs --> DLSSDLL
    CUDAFuncs --> DLSSDLL
    
    DLSSDLL --> GPUExecution["GPU Execution"]
```

The Windows implementation makes extensive use of DirectX resource sharing mechanisms for efficient memory handling between the application and DLSS.

Sources: [lib/Windows_x86_64/dev/nvngx_dlss.dll]()

### Linux Implementation

On Linux, DLSS primarily supports Vulkan through the `NVSDK_NGX_VULKAN_*` functions, with similar functionality to the Windows implementation but adapted for Vulkan resource handling.

## Thread Safety and Synchronization

DLSS functions are not thread-safe. Applications must ensure:

1. No concurrent calls to NGX functions
2. Input resources are not modified during DLSS evaluation
3. Output resources are not read until DLSS evaluation completes

```mermaid
sequenceDiagram
    participant RT as Render Thread
    participant DLSS as DLSS Processing
    
    Note over RT,DLSS: Not Thread Safe
    RT->>DLSS: EvaluateFeature()
    activate DLSS
    RT->>RT: Wait for completion
    DLSS-->>RT: Complete
    deactivate DLSS
    RT->>RT: Access output resource
```

Sources: [include/nvsdk_ngx.h:18-20]()

## Error Handling

DLSS uses a comprehensive error code system defined in the `NVSDK_NGX_Result` enumeration:

| Result Category | Description | Example |
|-----------------|-------------|---------|
| Success | Operation completed successfully | `NVSDK_NGX_Result_Success` |
| Hardware Error | Hardware doesn't support DLSS | `NVSDK_NGX_Result_FAIL_FeatureNotSupported` |
| Memory Error | Insufficient memory available | `NVSDK_NGX_Result_FAIL_OutOfGPUMemory` |
| Parameter Error | Invalid or unsupported parameters | `NVSDK_NGX_Result_FAIL_InvalidParameter` |
| Initialization Error | SDK not properly initialized | `NVSDK_NGX_Result_FAIL_NotInitialized` |

Helper macros `NVSDK_NGX_SUCCEED()` and `NVSDK_NGX_FAILED()` are provided to simplify error checking.

Sources: [include/nvsdk_ngx_defs.h:84-143](), [include/nvsdk_ngx_defs.h:145-146]()

## Internal Processing Pipeline

DLSS uses a sophisticated processing pipeline that combines temporal accumulation with deep learning inference:

```mermaid
flowchart TD
    Input["Low-Resolution Input"] --> Preprocess["Preprocessing"]
    MotionVectors["Motion Vectors"] --> TemporalAccum["Temporal Accumulation"]
    Depth["Depth Buffer"] --> TemporalAccum
    Preprocess --> TemporalAccum
    PrevState["Previous Frame State"] --> TemporalAccum
    TemporalAccum --> NeuralNetwork["Neural Network Processing"]
    NeuralNetwork --> PostProcess["Post-Processing"]
    PostProcess --> Output["High-Resolution Output"]
    PostProcess --> UpdateState["Update Frame State"]
    UpdateState --> PrevState
```

The internal pipeline includes specialized handling for anti-aliasing, detail reconstruction, and stability across frames.

Sources: [lib/Windows_x86_64/dev/nvngx_dlss.dll](), [lib/Windows_x86_64/rel/nvngx_dlss.dll]()

## Advanced Configuration

### Key Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `NVSDK_NGX_Parameter_Width` | Output width | Required |
| `NVSDK_NGX_Parameter_Height` | Output height | Required |
| `NVSDK_NGX_Parameter_OutWidth` | Input width | Required |
| `NVSDK_NGX_Parameter_OutHeight` | Input height | Required |
| `NVSDK_NGX_Parameter_Sharpness` | Sharpness control (0.0-1.0) | 0.0 |
| `NVSDK_NGX_Parameter_DLSS_Hint_Render_Preset` | Rendering preset | Default |
| `NVSDK_NGX_Parameter_Hint_HDR` | HDR content flag | 0 (SDR) |

Sources: [include/nvsdk_ngx_params.h]()

### Memory Optimization

For optimal performance, applications should:

1. Reuse scratch buffers across frames when possible
2. Create DLSS features at initialization rather than per-frame
3. Use appropriate quality settings for target hardware

## Compatibility Considerations

### Hardware Requirements

DLSS requires NVIDIA RTX GPUs with Tensor Cores. The library includes internal detection and fallback mechanisms for unsupported hardware, returning appropriate error codes.

### Driver Requirements

DLSS has specific driver version requirements. The NGX framework will return `NVSDK_NGX_Result_FAIL_OutOfDate` if driver updates are needed.

Sources: [include/nvsdk_ngx_defs.h:123-124]()

## Conclusion

NVIDIA DLSS employs a sophisticated multi-layer architecture that combines traditional rendering techniques with deep learning. The implementation balances performance, memory usage, and image quality through carefully designed processing pipelines and neural network models. Understanding these implementation details is crucial for optimal integration and performance tuning in applications.

For specific integration guidelines, see [NGX SDK Integration](#4), and for quality settings information, see [Quality Settings and Performance](#4.2).

---

