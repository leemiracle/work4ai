<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/Windows-Machine-Learning · page 5 Advanced Integration · fetched 2026-10-26 -->

# Advanced Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Samples/WinMLSamplesGallery/WinMLSamplesGallery/Samples/OpenCVInterop/README.md](Samples/WinMLSamplesGallery/WinMLSamplesGallery/Samples/OpenCVInterop/README.md)
- [Samples/WinMLSamplesGallery/WinMLSamplesGalleryNative/D3D12Quad.cpp](Samples/WinMLSamplesGallery/WinMLSamplesGalleryNative/D3D12Quad.cpp)
- [Samples/WinMLSamplesGallery/WinMLSamplesGalleryNative/D3D12Quad.h](Samples/WinMLSamplesGallery/WinMLSamplesGalleryNative/D3D12Quad.h)
- [Samples/WinMLSamplesGallery/WinMLSamplesGalleryNative/DXResourceBinding.cpp](Samples/WinMLSamplesGallery/WinMLSamplesGalleryNative/DXResourceBinding.cpp)
- [Samples/WinMLSamplesGallery/WinMLSamplesGalleryNative/ORTHelpers.cpp](Samples/WinMLSamplesGallery/WinMLSamplesGalleryNative/ORTHelpers.cpp)
- [Samples/WinMLSamplesGallery/WinMLSamplesGalleryNative/ORTHelpers.h](Samples/WinMLSamplesGallery/WinMLSamplesGalleryNative/ORTHelpers.h)
- [Samples/WinMLSamplesGallery/WinMLSamplesGalleryNative/OpenCVImage.cpp](Samples/WinMLSamplesGallery/WinMLSamplesGalleryNative/OpenCVImage.cpp)
- [Samples/WinMLSamplesGallery/WinMLSamplesGalleryNative/OpenCVImage.h](Samples/WinMLSamplesGallery/WinMLSamplesGalleryNative/OpenCVImage.h)
- [Samples/WinMLSamplesGallery/WinMLSamplesGalleryNative/RandomAccessStream.h](Samples/WinMLSamplesGallery/WinMLSamplesGalleryNative/RandomAccessStream.h)
- [Samples/WinMLSamplesGallery/WinMLSamplesGalleryNative/WeakBuffer.h](Samples/WinMLSamplesGallery/WinMLSamplesGalleryNative/WeakBuffer.h)
- [Samples/WinMLSamplesGallery/WinMLSamplesGalleryNative/Win32Application.cpp](Samples/WinMLSamplesGallery/WinMLSamplesGalleryNative/Win32Application.cpp)
- [Samples/WinMLSamplesGallery/WinMLSamplesGalleryNative/Win32Application.h](Samples/WinMLSamplesGallery/WinMLSamplesGalleryNative/Win32Application.h)
- [Samples/WinMLSamplesGallery/WinMLSamplesGalleryNative/stdafx.h](Samples/WinMLSamplesGallery/WinMLSamplesGalleryNative/stdafx.h)
- [azure-pipelines-samples.yml](azure-pipelines-samples.yml)
- [external/tools/BuildOpenCV.ps1](external/tools/BuildOpenCV.ps1)
- [external/tools/CMakeConfigureOpenCV.ps1](external/tools/CMakeConfigureOpenCV.ps1)
- [package.config](package.config)

</details>



This document provides an overview of advanced integration scenarios available in the Windows Machine Learning repository, covering DirectX resource binding, OpenCV interoperability, and real-time video processing capabilities. These integrations demonstrate sophisticated use cases that go beyond basic machine learning inference to enable high-performance, specialized workflows.

For basic Windows ML API usage, see [Core API and Architecture](#2). For specific implementation details of each integration type, see [DirectX Resource Binding](#5.1), [OpenCV Integration](#5.2), and [Real-time Video Processing](#5.3).

## Integration Architecture Overview

The Windows ML repository supports three primary advanced integration scenarios that extend beyond standard inference workflows:

```mermaid
graph TB
    subgraph "Windows ML Core"
        WinMLAPI["Windows.AI.MachineLearning API"]
        ONNXRuntime["ONNX Runtime"]
        DirectML["DirectML"]
    end
    
    subgraph "DirectX Integration"
        D3D12Quad["D3D12Quad"]
        DXResourceBinding["DXResourceBinding"]
        ORTHelpers["ORTHelpers"]
        Win32Application["Win32Application"]
    end
    
    subgraph "OpenCV Integration"
        OpenCVImage["OpenCVImage"]
        WeakBuffer["WeakBuffer"]
        RandomAccessStream["RandomAccessStream"]
    end
    
    subgraph "Real-time Processing"
        MediaFoundation["Media Foundation Transforms"]
        StreamEffects["Stream Effects Pipeline"]
        D3D12Resources["D3D12 Resource Sharing"]
    end
    
    WinMLAPI --> ONNXRuntime
    ONNXRuntime --> DirectML
    
    DirectML --> D3D12Quad
    D3D12Quad --> DXResourceBinding
    DXResourceBinding --> ORTHelpers
    
    WinMLAPI --> OpenCVImage
    OpenCVImage --> WeakBuffer
    
    D3D12Resources --> StreamEffects
    StreamEffects --> MediaFoundation
    
    ORTHelpers --> DirectML
```

**Advanced Integration Capabilities Overview**

Sources: [Samples/WinMLSamplesGallery/WinMLSamplesGalleryNative/DXResourceBinding.cpp:1-57](), [Samples/WinMLSamplesGallery/WinMLSamplesGalleryNative/OpenCVImage.cpp:1-117](), [azure-pipelines-samples.yml:64-93]()

## DirectX Resource Binding Integration

The DirectX integration enables direct GPU memory sharing between Direct3D 12 resources and ONNX Runtime, eliminating CPU-GPU memory transfers for high-performance scenarios.

```mermaid
graph LR
    subgraph "DirectX Pipeline"
        D3D12Device["ID3D12Device"]
        D3D12Resource["ID3D12Resource"]
        SwapChain["IDXGISwapChain3"]
        CommandQueue["ID3D12CommandQueue"]
    end
    
    subgraph "ONNX Runtime Integration"
        OrtSession["Ort::Session"]
        OrtDmlApi["OrtDmlApi"]
        OrtValue["Ort::Value"]
        DMLProvider["DirectML Provider"]
    end
    
    subgraph "WinML Native Bridge"
        DXResourceBinding["DXResourceBinding::EvalORT()"]
        CreateTensorValueFromD3DResource["CreateTensorValueFromD3DResource()"]
        Preprocess["Preprocess()"]
        Eval["Eval()"]
    end
    
    D3D12Resource --> CreateTensorValueFromD3DResource
    CreateTensorValueFromD3DResource --> OrtValue
    OrtValue --> Preprocess
    Preprocess --> Eval
    
    OrtDmlApi --> DMLProvider
    DMLProvider --> OrtSession
    OrtSession --> Eval
    
    DXResourceBinding --> D3D12Resource
    DXResourceBinding --> OrtSession
```

**Key Components and Data Flow**

| Component | Class/Function | Purpose |
|-----------|----------------|---------|
| DirectX Window Management | `D3D12Quad` | Manages D3D12 rendering pipeline and texture resources |
| Resource Binding | `DXResourceBinding::EvalORT()` | Coordinates GPU memory sharing between D3D12 and ORT |
| Tensor Creation | `CreateTensorValueFromD3DResource()` | Creates ORT tensors directly from D3D12 resources |
| Session Management | `CreateSession()` | Initializes ORT sessions with DirectML provider |

Sources: [Samples/WinMLSamplesGallery/WinMLSamplesGalleryNative/DXResourceBinding.cpp:17-56](), [Samples/WinMLSamplesGallery/WinMLSamplesGalleryNative/D3D12Quad.cpp:19-27](), [Samples/WinMLSamplesGallery/WinMLSamplesGalleryNative/ORTHelpers.cpp:121-158]()

## OpenCV Interoperability Integration

The OpenCV integration provides seamless interoperability between OpenCV's computer vision operations and Windows ML inference, enabling preprocessing and postprocessing workflows.

```mermaid
graph TB
    subgraph "OpenCV Operations"
        cvMat["cv::Mat"]
        ImageIO["cv::imread()"]
        NoiseOps["cv::medianBlur()"]
        ColorConvert["cv::cvtColor()"]
    end
    
    subgraph "WinML Bridge Components"
        OpenCVImage["OpenCVImage"]
        WeakBuffer["WeakBuffer<uint8_t>"]
        AsWeakBuffer["AsWeakBuffer()"]
        AsTensor["AsTensor()"]
        AsSoftwareBitmap["AsSoftwareBitmap()"]
    end
    
    subgraph "Windows ML Types"
        ITensor["ITensor"]
        TensorUInt8Bit["TensorUInt8Bit"]
        SoftwareBitmap["SoftwareBitmap"]
        IBuffer["IBuffer"]
    end
    
    cvMat --> OpenCVImage
    ImageIO --> cvMat
    NoiseOps --> cvMat
    ColorConvert --> cvMat
    
    OpenCVImage --> AsWeakBuffer
    OpenCVImage --> AsTensor
    OpenCVImage --> AsSoftwareBitmap
    
    AsWeakBuffer --> WeakBuffer
    WeakBuffer --> IBuffer
    AsTensor --> TensorUInt8Bit
    TensorUInt8Bit --> ITensor
    AsSoftwareBitmap --> SoftwareBitmap
```

**OpenCV-WinML Type Conversions**

| OpenCV Type | Bridge Method | Windows ML Type | Purpose |
|-------------|---------------|-----------------|---------|
| `cv::Mat` | `AsWeakBuffer()` | `IBuffer` | Memory-efficient buffer sharing |
| `cv::Mat` | `AsTensor()` | `TensorUInt8Bit` | Direct tensor creation for inference |
| `cv::Mat` | `AsSoftwareBitmap()` | `SoftwareBitmap` | UI display integration |

Sources: [Samples/WinMLSamplesGallery/WinMLSamplesGalleryNative/OpenCVImage.cpp:33-74](), [Samples/WinMLSamplesGallery/WinMLSamplesGalleryNative/WeakBuffer.h:15-71](), [Samples/WinMLSamplesGallery/WinMLSamplesGallery/Samples/OpenCVInterop/README.md:1-49]()

## Real-time Video Processing Integration

Real-time video processing combines DirectX resource management with Media Foundation transforms to enable low-latency inference on video streams.

```mermaid
graph LR
    subgraph "Media Pipeline"
        MediaFoundation["Media Foundation"]
        VideoFrame["VideoFrame"]
        Transform["MF Transform"]
    end
    
    subgraph "DirectX Resources"
        TextureBuffer["textureBuffer"]
        CurrentBuffer["currentBuffer"]
        RenderTargets["m_renderTargets"]
        CommandList["m_commandList"]
    end
    
    subgraph "Processing Flow"
        LoadImageTexture["LoadImageTexture()"]
        CopyTextureIntoCurrentBuffer["CopyTextureIntoCurrentBuffer()"]
        GetCurrentBuffer["GetCurrentBuffer()"]
        ShowNextImage["ShowNextImage()"]
    end
    
    MediaFoundation --> VideoFrame
    VideoFrame --> TextureBuffer
    TextureBuffer --> LoadImageTexture
    LoadImageTexture --> RenderTargets
    RenderTargets --> CopyTextureIntoCurrentBuffer
    CopyTextureIntoCurrentBuffer --> CurrentBuffer
    CurrentBuffer --> GetCurrentBuffer
    GetCurrentBuffer --> Transform
    Transform --> ShowNextImage
```

**Real-time Processing Components**

Sources: [Samples/WinMLSamplesGallery/WinMLSamplesGalleryNative/D3D12Quad.cpp:285-343](), [Samples/WinMLSamplesGallery/WinMLSamplesGalleryNative/D3D12Quad.cpp:347-393](), [Samples/WinMLSamplesGallery/WinMLSamplesGalleryNative/D3D12Quad.h:25-107]()

## Build System Integration

The advanced integrations require specialized build configurations that handle external dependencies and platform-specific compilation requirements.

**Build Pipeline Integration**

| Integration | Build Requirement | Configuration |
|-------------|-------------------|---------------|
| DirectX | Windows SDK 10.0.19041.0 | Native C++ with D3D12 |
| OpenCV | External submodule build | CMake configuration with `BuildOpenCV.ps1` |
| Media Foundation | Platform-specific MF SDK | UWP/Desktop targeting |

**OpenCV Build Process**

The OpenCV integration requires a multi-stage build process:

1. **Submodule Synchronization**: `git submodule update --init --recursive`
2. **CMake Configuration**: `CMakeConfigureOpenCV.ps1 -Architecture x64`
3. **MSBuild Compilation**: Platform-specific OpenCV library generation
4. **Integration**: Link with `WinMLSamplesGalleryNative` project

Sources: [azure-pipelines-samples.yml:47-92](), [external/tools/CMakeConfigureOpenCV.ps1:24-62](), [external/tools/BuildOpenCV.ps1:22-47]()

## Performance Considerations

Advanced integrations optimize performance through several mechanisms:

- **Zero-copy memory sharing** between DirectX and ONNX Runtime via `CreateTensorValueFromD3DResource()`
- **GPU-resident processing** eliminating CPU-GPU transfers in DirectX scenarios  
- **Weak buffer references** in OpenCV integration avoiding unnecessary memory copies
- **Asynchronous processing pipelines** for real-time video scenarios

Sources: [Samples/WinMLSamplesGallery/WinMLSamplesGalleryNative/ORTHelpers.cpp:121-158](), [Samples/WinMLSamplesGallery/WinMLSamplesGalleryNative/WeakBuffer.h:28-70](), [Samples/WinMLSamplesGallery/WinMLSamplesGalleryNative/RandomAccessStream.h:207-234]()

---

