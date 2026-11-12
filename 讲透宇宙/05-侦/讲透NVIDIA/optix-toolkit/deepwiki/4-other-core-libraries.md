<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/optix-toolkit · page 4 Other Core Libraries · fetched 2026-10-26 -->

# Other Core Libraries

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CHANGELOG.md](CHANGELOG.md)
- [CMake/SetCxxStandard.cmake](CMake/SetCxxStandard.cmake)
- [DemandLoading/DemandGeometry/CMakeLists.txt](DemandLoading/DemandGeometry/CMakeLists.txt)
- [DemandLoading/DemandLoading/CMakeLists.txt](DemandLoading/DemandLoading/CMakeLists.txt)
- [DemandLoading/ImageSource/CMakeLists.txt](DemandLoading/ImageSource/CMakeLists.txt)
- [DemandLoading/ImageSource/include/OptiXToolkit/ImageSource/EXRReader.h](DemandLoading/ImageSource/include/OptiXToolkit/ImageSource/EXRReader.h)
- [DemandLoading/README.md](DemandLoading/README.md)
- [Memory/CHANGELOG.md](Memory/CHANGELOG.md)
- [Memory/CMakeLists.txt](Memory/CMakeLists.txt)
- [Memory/LICENSE.txt](Memory/LICENSE.txt)
- [Memory/README.md](Memory/README.md)
- [Memory/include/OptiXToolkit/Memory/BitCast.h](Memory/include/OptiXToolkit/Memory/BitCast.h)
- [OmmBaking/CMakeLists.txt](OmmBaking/CMakeLists.txt)
- [README.md](README.md)
- [ShaderUtil/CMakeLists.txt](ShaderUtil/CMakeLists.txt)
- [examples/CMakeLists.txt](examples/CMakeLists.txt)
- [examples/CuOmmBaking/Simple/CMakeLists.txt](examples/CuOmmBaking/Simple/CMakeLists.txt)
- [examples/CuOmmBaking/Viewer/CMakeLists.txt](examples/CuOmmBaking/Viewer/CMakeLists.txt)

</details>



This page documents the supporting libraries that complement the DemandLoading system in the OptiX Toolkit. These libraries provide essential functionality for shader utilities, image processing, memory management, and opacity micromap baking. For information about the main DemandLoading system, see [DemandLoading System](#3). For build configuration and dependencies, see [Build System](#2.2).

## Library Overview

The OptiX Toolkit includes several specialized libraries that work together to provide a complete ray tracing development environment:

```mermaid
graph TB
    subgraph "Header-Only Utilities"
        ShaderUtil["ShaderUtil<br/>OptiXToolkit::ShaderUtil"]
        Error["Error<br/>OptiXToolkit::Error"]
        Memory["Memory<br/>OptiXToolkit::Memory"]
        OptiXMemory["OptiXMemory<br/>OptiXToolkit::OptiXMemory"]
    end
    
    subgraph "Compiled Libraries"
        ImageSource["ImageSource<br/>OptiXToolkit::ImageSource"]
        CuOmmBaking["CuOmmBaking<br/>OptiXToolkit::CuOmmBaking"]
    end
    
    subgraph "Main System"
        DemandLoading["DemandLoading<br/>OptiXToolkit::DemandLoading"]
    end
    
    subgraph "External Dependencies"
        CUDA["CUDA Toolkit"]
        OptiX["OptiX SDK"]
        OpenEXR["OpenEXR/Imath"]
        OIIO["OpenImageIO"]
    end
    
    %% Header-only dependencies
    ShaderUtil --> CUDA
    Error --> CUDA
    Memory --> Error
    Memory --> CUDA
    OptiXMemory --> OptiX
    OptiXMemory --> Memory
    
    %% Compiled library dependencies
    ImageSource --> Memory
    ImageSource --> Error
    ImageSource --> OpenEXR
    ImageSource --> OIIO
    CuOmmBaking --> CUDA
    CuOmmBaking --> OptiX
    
    %% Main system dependencies
    DemandLoading --> ImageSource
    DemandLoading --> ShaderUtil
    DemandLoading --> Memory
    DemandLoading --> OptiX
```

**Library Dependency Relationships**

Sources: [README.md:20-26](), [ShaderUtil/CMakeLists.txt:27-28](), [Memory/CMakeLists.txt:45-108](), [DemandLoading/ImageSource/CMakeLists.txt:24-25](), [OmmBaking/CMakeLists.txt:61-62]()

## ShaderUtil Library

`ShaderUtil` is a header-only library providing mathematical utilities and helper functions for OptiX device code. It implements common operations needed in ray tracing kernels without requiring separate compilation.

### Core Components

```mermaid
graph TD
    ShaderUtilLib["ShaderUtil Library<br/>INTERFACE target"]
    
    subgraph "Mathematical Utilities"
        vec_math["vec_math.h<br/>Vector operations"]
        Transform4["Transform4.h<br/>4x4 transformations"]
        color["color.h<br/>Color space operations"]
    end
    
    subgraph "Ray Tracing Utilities"
        SIA["SelfIntersectionAvoidance.h<br/>Ray offset calculations"]
        OptixSIA["OptixSelfIntersectionAvoidance.h<br/>OptiX-specific helpers"]
        CudaSIA["CudaSelfIntersectionAvoidance.h<br/>CUDA-specific helpers"]
        ray_cone["ray_cone.h<br/>Ray cone calculations"]
    end
    
    subgraph "Sampling Utilities"
        AliasTable["AliasTable.h<br/>Alias method sampling"]
        CdfInversion["CdfInversionTable.h<br/>CDF inversion sampling"]
        PdfTable["PdfTable.h<br/>PDF table utilities"]
        SummedArea["ISummedAreaTable.h<br/>Summed area tables"]
    end
    
    subgraph "Development Utilities"
        DebugLocation["DebugLocation.h<br/>Debug annotations"]
        Preprocessor["Preprocessor.h<br/>Macro utilities"]
        vec_printers["vec_printers.h<br/>Vector printing"]
    end
    
    ShaderUtilLib --> vec_math
    ShaderUtilLib --> Transform4
    ShaderUtilLib --> color
    ShaderUtilLib --> SIA
    ShaderUtilLib --> OptixSIA
    ShaderUtilLib --> CudaSIA
    ShaderUtilLib --> ray_cone
    ShaderUtilLib --> AliasTable
    ShaderUtilLib --> CdfInversion
    ShaderUtilLib --> PdfTable
    ShaderUtilLib --> SummedArea
    ShaderUtilLib --> DebugLocation
    ShaderUtilLib --> Preprocessor
    ShaderUtilLib --> vec_printers
```

**ShaderUtil Component Architecture**

The library is configured as an `INTERFACE` CMake target, meaning all headers are included directly in consuming projects without separate compilation:

Sources: [ShaderUtil/CMakeLists.txt:27-51](), [ShaderUtil/CMakeLists.txt:53-57]()

### Self-Intersection Avoidance System

One of the most important components is the self-intersection avoidance system, which prevents ray-surface intersection artifacts:

```mermaid
graph LR
    subgraph "SIA Headers"
        SIATypes["SelfIntersectionAvoidanceTypes.h<br/>Common data structures"]
        SIACore["SelfIntersectionAvoidance.h<br/>Core algorithms"]
        OptixSIA["OptixSelfIntersectionAvoidance.h<br/>optixOffsetRay wrapper"]
        CudaSIA["CudaSelfIntersectionAvoidance.h<br/>CUDA ray offset"]
    end
    
    SIATypes --> SIACore
    SIACore --> OptixSIA
    SIACore --> CudaSIA
```

**Self-Intersection Avoidance Structure**

Sources: [ShaderUtil/CMakeLists.txt:38-45]()

## OmmBaking Library

`CuOmmBaking` provides functionality for baking Opacity Micromap Arrays (OMMs), which enable hardware-accelerated alpha testing in OptiX 7.6+. This library processes textured geometry to generate efficient opacity representations.

### Implementation Architecture

```mermaid
graph TB
    subgraph "Public API"
        CuOmmBaking_h["CuOmmBaking.h<br/>Main baking interface"]
        CuBuffer_h["CuBuffer.h<br/>CUDA buffer utilities"]
    end
    
    subgraph "Implementation"
        CuOmmBakingImpl_cpp["CuOmmBakingImpl.cpp<br/>Host-side implementation"]
        CuOmmBakingImpl_cu["CuOmmBakingImpl.cu<br/>Device-side kernels"]
        CuOmmBakingImpl_h["CuOmmBakingImpl.h<br/>Internal interface"]
    end
    
    subgraph "Core Processing"
        Texture_cu["Texture.cu<br/>Texture sampling"]
        Texture_h["Texture.h<br/>Texture definitions"]
        Evaluate_h["Evaluate.h<br/>Opacity evaluation"]
        Triangle_h["Triangle.h<br/>Triangle utilities"]
        SummedAreaTable_h["SummedAreaTable.h<br/>Optimization structure"]
    end
    
    subgraph "Utilities"
        BufferLayout["BufferLayout.h<br/>Memory layout"]
        VecMath["VecMath.h<br/>Vector mathematics"]
        Rasterize["Rasterize.h<br/>Rasterization utilities"]
        XXH["XXH.h<br/>Hash functions"]
        Exception["Exception.h<br/>Error handling"]
    end
    
    CuOmmBaking_h --> CuOmmBakingImpl_h
    CuBuffer_h --> CuOmmBakingImpl_h
    CuOmmBakingImpl_cpp --> CuOmmBakingImpl_cu
    CuOmmBakingImpl_h --> Texture_h
    CuOmmBakingImpl_h --> Evaluate_h
    Texture_cu --> Triangle_h
    Texture_cu --> SummedAreaTable_h
    CuOmmBakingImpl_cpp --> BufferLayout
    CuOmmBakingImpl_cpp --> VecMath
    CuOmmBakingImpl_cpp --> Rasterize
    CuOmmBakingImpl_cpp --> XXH
    CuOmmBakingImpl_cpp --> Exception
```

**OmmBaking Internal Architecture**

The library requires OptiX 7.6+ and uses CUDA for GPU-accelerated processing:

Sources: [OmmBaking/CMakeLists.txt:24-27](), [OmmBaking/CMakeLists.txt:32-46](), [OmmBaking/CMakeLists.txt:82-86]()

## ImageSource Library

`ImageSource` provides a unified interface for reading various image file formats, abstracting away format-specific details while supporting both CPU and GPU memory operations.

### Reader Architecture

```mermaid
graph TB
    subgraph "Core Interface"
        ImageSource_h["ImageSource.h<br/>ImageSourceBase class"]
        TextureInfo_h["TextureInfo.h<br/>Image metadata"]
        ImageHelpers_h["ImageHelpers.h<br/>Utility functions"]
    end
    
    subgraph "Format Readers"
        EXRReader_h["EXRReader.h<br/>OpenEXR support"]
        CoreEXRReader_h["CoreEXRReader.h<br/>OpenEXR Core API"]
        DDSImageReader_h["DDSImageReader.h<br/>DirectDraw Surface"]
        OIIOReader_h["OIIOReader.h<br/>OpenImageIO formats"]
    end
    
    subgraph "Processing Components"
        MipMapImageSource_h["MipMapImageSource.h<br/>Mipmap generation"]
        TiledImageSource_h["TiledImageSource.h<br/>Tile-based access"]
        CascadeImage_h["CascadeImage.h<br/>Multi-resolution"]
        CheckerBoardImage_h["CheckerBoardImage.h<br/>Procedural patterns"]
    end
    
    subgraph "Caching & Management"
        ImageSourceCache_h["ImageSourceCache.h<br/>Reader caching"]
        RateLimitedImageSource_h["RateLimitedImageSource.h<br/>Bandwidth control"]
        WrappedImageSource_h["WrappedImageSource.h<br/>Reader wrapper"]
    end
    
    ImageSource_h --> TextureInfo_h
    ImageSource_h --> ImageHelpers_h
    EXRReader_h --> ImageSource_h
    CoreEXRReader_h --> ImageSource_h
    DDSImageReader_h --> ImageSource_h
    OIIOReader_h --> ImageSource_h
    MipMapImageSource_h --> ImageSource_h
    TiledImageSource_h --> ImageSource_h
    CascadeImage_h --> ImageSource_h
    CheckerBoardImage_h --> ImageSource_h
    ImageSourceCache_h --> ImageSource_h
    RateLimitedImageSource_h --> ImageSource_h
    WrappedImageSource_h --> ImageSource_h
```

**ImageSource Reader Hierarchy**

### Configuration Options

The library supports conditional compilation based on available dependencies:

```mermaid
graph LR
    subgraph "Configuration"
        Config_h["Config.h<br/>Generated configuration"]
        Config_in["Config.h.in<br/>Template file"]
    end
    
    subgraph "OpenEXR Support"
        OTK_USE_OPENEXR["OTK_USE_OPENEXR<br/>CMake option"]
        FetchOpenEXR["FetchOpenEXR<br/>CMake module"]
        OpenEXR_Target["OpenEXR::OpenEXR<br/>Library target"]
    end
    
    subgraph "OpenImageIO Support"
        OTK_USE_OIIO["OTK_USE_OIIO<br/>CMake option"]
        OIIO_Package["find_package(OpenImageIO)<br/>Package discovery"]
        OIIO_Target["OpenImageIO::OpenImageIO<br/>Library target"]
    end
    
    Config_in --> Config_h
    OTK_USE_OPENEXR --> Config_h
    OTK_USE_OIIO --> Config_h
    FetchOpenEXR --> OpenEXR_Target
    OIIO_Package --> OIIO_Target
```

**ImageSource Configuration System**

Sources: [DemandLoading/ImageSource/CMakeLists.txt:7-22](), [DemandLoading/ImageSource/CMakeLists.txt:64-97](), [DemandLoading/ImageSource/CMakeLists.txt:99-114](), [DemandLoading/ImageSource/CMakeLists.txt:116-121]()

## Memory Management Libraries

The OptiX Toolkit provides three interconnected libraries for memory management and error handling:

### Error Handling System

```mermaid
graph TB
    subgraph "Error Library (Header-Only)"
        ErrorCheck_h["ErrorCheck.h<br/>Generic error mapping"]
        cuErrorCheck_h["cuErrorCheck.h<br/>CUDA Driver API errors"]
        cudaErrorCheck_h["cudaErrorCheck.h<br/>CUDA Runtime API errors"]
        optixErrorCheck_h["optixErrorCheck.h<br/>OptiX API errors"]
    end
    
    ErrorCheck_h --> cuErrorCheck_h
    ErrorCheck_h --> cudaErrorCheck_h
    ErrorCheck_h --> optixErrorCheck_h
```

**Error Handling Component Structure**

### Memory Allocation System

```mermaid
graph TB
    subgraph "Memory Library (Header-Only)"
        Allocators_h["Allocators.h<br/>Memory allocator interfaces"]
        MemoryPool_h["MemoryPool.h<br/>Thread-safe pooling"]
        DeviceBuffer_h["DeviceBuffer.h<br/>CUDA buffer wrapper"]
    end
    
    subgraph "Specialized Allocators"
        BinnedSuballocator_h["BinnedSuballocator.h<br/>Size-based allocation"]
        FixedSuballocator_h["FixedSuballocator.h<br/>Fixed-size blocks"]
        HeapSuballocator_h["HeapSuballocator.h<br/>Heap-based allocation"]
        RingSuballocator_h["RingSuballocator.h<br/>Circular buffer allocation"]
    end
    
    subgraph "Device-Specific Components"
        DeviceFixedPool_h["DeviceFixedPool.h<br/>GPU fixed-size pool"]
        DeviceRingBuffer_h["DeviceRingBuffer.h<br/>GPU ring buffer"]
    end
    
    subgraph "Utilities"
        MemoryBlockDesc_h["MemoryBlockDesc.h<br/>Block descriptors"]
        SyncVector_h["SyncVector.h<br/>Thread-safe vector"]
        BitCast_h["BitCast.h<br/>Type-safe casting"]
    end
    
    Allocators_h --> MemoryPool_h
    MemoryPool_h --> BinnedSuballocator_h
    MemoryPool_h --> FixedSuballocator_h
    MemoryPool_h --> HeapSuballocator_h
    MemoryPool_h --> RingSuballocator_h
    DeviceBuffer_h --> DeviceFixedPool_h
    DeviceBuffer_h --> DeviceRingBuffer_h
    MemoryPool_h --> MemoryBlockDesc_h
    MemoryPool_h --> SyncVector_h
    Allocators_h --> BitCast_h
```

**Memory Management Architecture**

### OptiX-Specific Memory Utilities

```mermaid
graph TB
    subgraph "OptiXMemory Library (Header-Only)"
        Builders_h["Builders.h<br/>OptiX object builders"]
        CompileOptions_h["CompileOptions.h<br/>Compilation helpers"]
        Record_h["Record.h<br/>SBT record wrapper"]
        SyncRecord_h["SyncRecord.h<br/>Thread-safe SBT records"]
    end
    
    subgraph "Builder Components"
        ProgramGroupDescBuilder["ProgramGroupDescBuilder<br/>Program group creation"]
        BuildInputBuilder["BuildInputBuilder<br/>Acceleration structure input"]
    end
    
    Builders_h --> ProgramGroupDescBuilder
    Builders_h --> BuildInputBuilder
    CompileOptions_h --> Builders_h
    Record_h --> SyncRecord_h
```

**OptiXMemory Specialized Components**

Sources: [Memory/CMakeLists.txt:45-75](), [Memory/CMakeLists.txt:78-108](), [Memory/CMakeLists.txt:125-144](), [Memory/README.md:7-15]()

### CUDA Memory Pool Integration

The Memory library supports CUDA memory pools when available:

Sources: [Memory/CMakeLists.txt:25-29](), [Memory/CMakeLists.txt:105-107]()

## Library Integration Patterns

These core libraries integrate with the main OptiX Toolkit through well-defined interfaces:

```mermaid
graph TB
    subgraph "Application Layer"
        Examples["Example Applications"]
        UserCode["User Applications"]
    end
    
    subgraph "Integration Targets"
        DemandLoading_Target["OptiXToolkit::DemandLoading"]
        CuOmmBaking_Target["OptiXToolkit::CuOmmBaking"]
        ImageSource_Target["OptiXToolkit::ImageSource"]
        ShaderUtil_Target["OptiXToolkit::ShaderUtil"]
        Memory_Target["OptiXToolkit::Memory"]
        Error_Target["OptiXToolkit::Error"]
        OptiXMemory_Target["OptiXToolkit::OptiXMemory"]
    end
    
    subgraph "CMake Export Targets"
        DemandLoadingTargets["DemandLoadingTargets.cmake"]
        CuOmmBakingTargets["CuOmmBakingTargets.cmake"]
        ImageSourceTargets["ImageSourceTargets.cmake"]
        ShaderUtilTargets["ShaderUtilTargets.cmake"]
        MemoryTargets["MemoryTargets.cmake"]
        ErrorTargets["ErrorTargets.cmake"]
        OptiXMemoryTargets["OptiXMemoryTargets.cmake"]
    end
    
    Examples --> DemandLoading_Target
    Examples --> CuOmmBaking_Target
    UserCode --> ShaderUtil_Target
    UserCode --> Memory_Target
    
    DemandLoading_Target --> DemandLoadingTargets
    CuOmmBaking_Target --> CuOmmBakingTargets
    ImageSource_Target --> ImageSourceTargets
    ShaderUtil_Target --> ShaderUtilTargets
    Memory_Target --> MemoryTargets
    Error_Target --> ErrorTargets
    OptiXMemory_Target --> OptiXMemoryTargets
```

**CMake Target Export System**

Each library provides CMake export targets for integration into downstream projects, with consistent naming conventions using the `OptiXToolkit::` namespace.

Sources: [ShaderUtil/CMakeLists.txt:69-73](), [OmmBaking/CMakeLists.txt:104-108](), [DemandLoading/ImageSource/CMakeLists.txt:133-137](), [Memory/CMakeLists.txt:71-75](), [Memory/CMakeLists.txt:118-122](), [Memory/CMakeLists.txt:155-159]()

---

