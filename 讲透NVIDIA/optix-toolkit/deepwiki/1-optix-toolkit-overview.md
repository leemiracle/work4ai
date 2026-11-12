<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/optix-toolkit · page 1 OptiX Toolkit Overview · fetched 2026-10-26 -->

# OptiX Toolkit Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CHANGELOG.md](CHANGELOG.md)
- [CMakeLists.txt](CMakeLists.txt)
- [DemandLoading/CMakeLists.txt](DemandLoading/CMakeLists.txt)
- [DemandLoading/README.md](DemandLoading/README.md)
- [Memory/CHANGELOG.md](Memory/CHANGELOG.md)
- [Memory/LICENSE.txt](Memory/LICENSE.txt)
- [Memory/README.md](Memory/README.md)
- [Memory/include/OptiXToolkit/Memory/BitCast.h](Memory/include/OptiXToolkit/Memory/BitCast.h)
- [README.md](README.md)

</details>



## Purpose and Scope

The OptiX Toolkit (OTK) is a collection of C++/CUDA utilities designed to simplify the development of applications using the NVIDIA OptiX ray tracing API. This document provides a high-level overview of the toolkit's architecture, core libraries, and how they work together to enable advanced ray tracing features like demand-loaded textures, opacity micromaps, and efficient memory management.

For detailed information about specific components, see [Core Libraries](#1.1) for library-specific documentation, [Getting Started](#2) for build instructions, and [DemandLoading System](#3) for the toolkit's most important subsystem.

Sources: [README.md:1-3](), [CMakeLists.txt:6-7]()

## High-Level Architecture

The OptiX Toolkit follows a modular design with four main layers: external dependencies, build system infrastructure, core libraries, and example applications. The central component is the DemandLoading system, which enables sparse texture loading and forms the foundation for most advanced features.

### System Architecture Overview

```mermaid
graph TB
    subgraph "External Dependencies"
        OPTIX["OptiX SDK 7.3+"]
        CUDA["CUDA Toolkit 11.1+"]
        VCPKG["vcpkg Package Manager"]
        PYOPTIX["PyOptiX Submodule"]
    end
    
    subgraph "Core Libraries"
        MEMORY["Memory Library<br/>- MemoryPool<br/>- DeviceMemoryManager<br/>- Various Allocators"]
        SHADER["ShaderUtil<br/>- Header-only utilities<br/>- Vector math<br/>- Self Intersection Avoidance"]
        DEMAND["DemandLoading<br/>- DemandLoaderImpl<br/>- DeviceContext<br/>- PageLoader"]
        OMM["OmmBaking<br/>- Opacity Micromap Arrays<br/>- Textured geometry baking"]
        IMGSRC["ImageSource<br/>- File format readers<br/>- EXR, PNG, JPEG support"]
        GEOM["DemandGeometry<br/>- On-demand geometry loading"]
    end
    
    subgraph "Build System"
        CMAKE["CMakeLists.txt<br/>- Project configuration<br/>- Dependency management"]
        PRESETS["CMakePresets.json<br/>- otk-default<br/>- otk-fetch-content<br/>- otk-libraries"]
    end
    
    subgraph "Example Applications"
        PBRT["DemandPbrtScene Viewer"]
        TEXTURE["Texture Viewers"]
        SIMPLE["Simple Examples"]
    end

    %% Dependencies
    DEMAND --> MEMORY
    DEMAND --> SHADER
    DEMAND --> IMGSRC
    GEOM --> DEMAND
    OMM --> MEMORY
    
    %% External Dependencies
    MEMORY --> CUDA
    DEMAND --> OPTIX
    DEMAND --> CUDA
    
    %% Build Dependencies
    CMAKE --> VCPKG
    PRESETS --> CMAKE
    
    %% Example Dependencies
    PBRT --> DEMAND
    PBRT --> GEOM
    TEXTURE --> DEMAND
    SIMPLE --> OMM
```

Sources: [CMakeLists.txt:76-97](), [README.md:20-25](), [DemandLoading/CMakeLists.txt:35-38]()

## Core Libraries

The OptiX Toolkit provides four primary libraries that can be built independently or together. Each library serves a specific purpose and follows clear dependency relationships.

### Library Dependency Structure

```mermaid
graph TD
    subgraph "Foundation Layer"
        MEMORY["Memory<br/>- MemoryPool<br/>- DeviceMemoryManager<br/>- CudaMemoryResource"]
        ERROR["Error Handling<br/>- ErrorCheck.h<br/>- Exception mapping"]
    end
    
    subgraph "Image Processing"
        IMGSRC["ImageSource<br/>- ImageReader interface<br/>- EXRReader, PngReader<br/>- File format abstraction"]
    end
    
    subgraph "Core OptiX Utilities"
        SHADER["ShaderUtil<br/>- Header-only library<br/>- Vector math utilities<br/>- SelfIntersectionAvoidance"]
        DEMAND["DemandLoading<br/>- DemandLoaderImpl<br/>- DemandPageLoaderImpl<br/>- RequestProcessor"]
        GEOM["DemandGeometry<br/>- Geometry streaming<br/>- ProxyGeometry system"]
        OMM["OmmBaking<br/>- Opacity micromap generation<br/>- Texture analysis"]
    end

    %% Dependencies
    ERROR --> CUDA_RT["CUDA Runtime"]
    MEMORY --> ERROR
    MEMORY --> CUDA_RT
    IMGSRC --> MEMORY
    IMGSRC --> OPENEXR["OpenEXR Libraries"]
    SHADER --> CUDA_RT
    DEMAND --> MEMORY
    DEMAND --> IMGSRC
    DEMAND --> SHADER
    DEMAND --> OPTIX_SDK["OptiX SDK"]
    GEOM --> DEMAND
    OMM --> MEMORY
    OMM --> OPTIX_SDK
```

### Library Configuration

The toolkit uses a flexible library selection system controlled by the `OTK_LIBRARIES` CMake variable. The default configuration includes all four core libraries with their dependencies automatically resolved.

| Library | Dependencies | Purpose |
|---------|-------------|---------|
| `Memory` | None | Foundation memory management |
| `ShaderUtil` | `Memory` | OptiX kernel utilities |
| `DemandLoading` | `Memory`, `ShaderUtil` | Sparse texture streaming |
| `OmmBaking` | `Memory` | Opacity micromap generation |

Sources: [CMakeLists.txt:76-88](), [README.md:145-148](), [Memory/README.md:7-16]()

## Build System Architecture

The OptiX Toolkit employs a sophisticated CMake-based build system with multiple dependency acquisition strategies and extensive configuration options.

### Build Configuration Flow

```mermaid
graph LR
    subgraph "Configuration Sources"
        PRESETS["CMakePresets.json<br/>- otk-default<br/>- otk-fetch-content<br/>- otk-libraries"]
        VCPKG_MANIFEST["vcpkg.json<br/>Package dependencies"]
        USER_PRESETS["CMakeUserPresets.json<br/>User customizations"]
    end
    
    subgraph "CMake Processing"
        TOP_CMAKE["CMakeLists.txt<br/>- OTK_PROJECT_NAME<br/>- OTK_LIBRARIES<br/>- OTK_USE_VCPKG"]
        BUILD_CONFIG["BuildConfig.cmake<br/>- ProjectOptions.cmake<br/>- Dependency resolution"]
    end
    
    subgraph "Dependency Methods"
        VCPKG_METHOD["vcpkg<br/>- Integrated toolchain<br/>- vcpkg-overlays"]
        FETCHCONTENT["FetchContent<br/>- Direct downloads<br/>- Git repositories"]
    end
    
    subgraph "Library Targets"
        CORE_LIBS["Core Libraries<br/>- OptiXToolkit::DemandLoading<br/>- OptiXToolkit::Memory<br/>- OptiXToolkit::OmmBaking<br/>- OptiXToolkit::ShaderUtil"]
        EXAMPLES["Example Executables<br/>- DemandPbrtScene<br/>- DemandTextureViewer"]
        TESTS["Test Executables<br/>- Unit tests<br/>- Integration tests"]
    end

    %% Configuration Flow
    PRESETS --> TOP_CMAKE
    USER_PRESETS --> TOP_CMAKE
    VCPKG_MANIFEST --> BUILD_CONFIG
    TOP_CMAKE --> BUILD_CONFIG
    
    %% Dependency Resolution
    BUILD_CONFIG --> |"OTK_USE_VCPKG=ON"| VCPKG_METHOD
    BUILD_CONFIG --> |"OTK_USE_VCPKG=OFF"| FETCHCONTENT
    
    %% Output Generation
    BUILD_CONFIG --> CORE_LIBS
    BUILD_CONFIG --> EXAMPLES
    BUILD_CONFIG --> TESTS
```

### CMake Configuration Options

The build system provides extensive customization through CMake variables:

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `OTK_USE_VCPKG` | `BOOL` | `ON` | Use vcpkg for dependencies |
| `OTK_LIBRARIES` | `STRING` | `ALL` | Libraries to build |
| `OTK_BUILD_EXAMPLES` | `BOOL` | `ON` | Build example applications |
| `OTK_BUILD_TESTS` | `BOOL` | `ON` | Build test suite |
| `OTK_PROJECT_NAME` | `STRING` | `OptiXToolkit` | CMake project name |

Sources: [CMakeLists.txt:25](), [README.md:126-142](), [CMakeLists.txt:55-60]()

## System Dependencies

The OptiX Toolkit requires several external dependencies that are managed through either vcpkg or CMake FetchContent.

### External Dependency Requirements

| Component | Requirements | Purpose |
|-----------|-------------|---------|
| **Runtime** | OptiX SDK 7.3+, CUDA Toolkit 11.1+ | Core ray tracing and compute |
| **Image Processing** | OpenEXR 3.1.5+, Imath 3.1.5+, OpenImageIO (optional) | Texture file format support |
| **GUI (Examples)** | GLFW 3.3+, ImGui, glad, stb | Interactive applications |
| **Testing** | Google Test, Google Mock | Unit and integration testing |
| **Build Tools** | CMake 3.27+, git with LFS | Build system and version control |

The toolkit automatically detects and configures these dependencies using the specified acquisition method (vcpkg or FetchContent).

Sources: [README.md:27-35](), [README.md:155-164](), [CMakeLists.txt:55-60]()

## Integration Points

The OptiX Toolkit is designed to integrate seamlessly with existing OptiX applications. The primary integration points are:

1. **CMake Integration**: Include as a subdirectory using `add_subdirectory(OptiXToolkit)`
2. **Library Linking**: Link against specific libraries like `OptiXToolkit::DemandLoading`
3. **Header Inclusion**: Use toolkit headers with the `<OptiXToolkit/Library>` prefix
4. **Device Code**: Include toolkit device functions in OptiX kernels

For comprehensive integration guidance, see [Getting Started](#2) and library-specific documentation in [Core Libraries](#1.1).

Sources: [DemandLoading/README.md:84-95](), [Memory/README.md:9-15]()

---

