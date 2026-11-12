<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/optix-toolkit · page 5 Example Applications · fetched 2026-10-26 -->

# Example Applications

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [examples/DemandLoading/DemandPbrtScene/CMakeLists.txt](examples/DemandLoading/DemandPbrtScene/CMakeLists.txt)
- [examples/DemandLoading/DemandPbrtScene/ImGuiUserInterface.cpp](examples/DemandLoading/DemandPbrtScene/ImGuiUserInterface.cpp)
- [examples/DemandLoading/DemandPbrtScene/PbrtScene.cpp](examples/DemandLoading/DemandPbrtScene/PbrtScene.cpp)
- [examples/DemandLoading/DemandPbrtScene/include/DemandPbrtScene/ImGuiUserInterface.h](examples/DemandLoading/DemandPbrtScene/include/DemandPbrtScene/ImGuiUserInterface.h)
- [examples/DemandLoading/DemandPbrtScene/include/DemandPbrtScene/JsonStatisticsPrinter.h](examples/DemandLoading/DemandPbrtScene/include/DemandPbrtScene/JsonStatisticsPrinter.h)
- [examples/DemandLoading/DemandPbrtScene/tests/CMakeLists.txt](examples/DemandLoading/DemandPbrtScene/tests/CMakeLists.txt)
- [examples/DemandLoading/DemandPbrtScene/tests/TestJsonStatisticsPrinter.cpp](examples/DemandLoading/DemandPbrtScene/tests/TestJsonStatisticsPrinter.cpp)
- [examples/DemandLoading/DemandPbrtScene/tests/TestPbrtScene.cpp](examples/DemandLoading/DemandPbrtScene/tests/TestPbrtScene.cpp)
- [examples/DemandLoading/DemandTextureViewer/CMakeLists.txt](examples/DemandLoading/DemandTextureViewer/CMakeLists.txt)
- [examples/DemandLoading/DemandTextureViewer/DemandTextureViewer.cpp](examples/DemandLoading/DemandTextureViewer/DemandTextureViewer.cpp)
- [examples/DemandLoading/DemandTextureViewer/DemandTextureViewer.cu](examples/DemandLoading/DemandTextureViewer/DemandTextureViewer.cu)
- [examples/DemandLoading/TexturePainting/TexturePainting.cpp](examples/DemandLoading/TexturePainting/TexturePainting.cpp)
- [examples/DemandLoading/UdimTextureViewer/UdimTextureViewer.cpp](examples/DemandLoading/UdimTextureViewer/UdimTextureViewer.cpp)
- [examples/OTKAppBase/CMakeLists.txt](examples/OTKAppBase/CMakeLists.txt)
- [examples/OTKAppBase/include/OptiXToolkit/OTKAppBase/OTKApp.h](examples/OTKAppBase/include/OptiXToolkit/OTKAppBase/OTKApp.h)
- [examples/OTKAppBase/include/OptiXToolkit/OTKAppBase/OTKAppDeviceUtil.h](examples/OTKAppBase/include/OptiXToolkit/OTKAppBase/OTKAppDeviceUtil.h)
- [examples/OTKAppBase/include/OptiXToolkit/OTKAppBase/OTKAppLaunchParams.h](examples/OTKAppBase/include/OptiXToolkit/OTKAppBase/OTKAppLaunchParams.h)
- [examples/OTKAppBase/include/OptiXToolkit/OTKAppBase/OTKAppOptixPrograms.h](examples/OTKAppBase/include/OptiXToolkit/OTKAppBase/OTKAppOptixPrograms.h)
- [examples/OTKAppBase/include/OptiXToolkit/OTKAppBase/OTKAppSimpleBsdf.h](examples/OTKAppBase/include/OptiXToolkit/OTKAppBase/OTKAppSimpleBsdf.h)
- [examples/OTKAppBase/src/OTKApp.cpp](examples/OTKAppBase/src/OTKApp.cpp)

</details>



This page covers the example applications that demonstrate OptiX Toolkit capabilities. These applications showcase demand loading, texture handling, and ray tracing features through practical, interactive implementations.

For information about the core demand loading system used by these examples, see [DemandLoading System](#3). For details about the underlying framework components, see [Core Libraries](#1.1).

## Application Architecture

The OptiX Toolkit provides a structured framework for building ray tracing applications through the `OTKAppBase` library. All example applications inherit from or utilize this common foundation.

### OTKApp Framework Architecture

```mermaid
graph TB
    subgraph "Application Layer"
        PBRT["DemandPbrtScene"]
        TEXVIEWER["DemandTextureViewer"] 
        UDIM["UdimTextureViewer"]
        PAINT["TexturePainting"]
    end
    
    subgraph "OTKAppBase Framework"
        OTKAPP["OTKApp"]
        PARAMS["OTKAppLaunchParams"]
        DEVICE["OTKAppDeviceUtil"]
        OPTIX["OTKAppOptixPrograms"]
        SHAPES["OTKAppShapeMaker"]
    end
    
    subgraph "Core OptiX Operations"
        CONTEXT["OptixDeviceContext"]
        PIPELINE["OptixPipeline"]
        SBT["Shader Binding Table"]
        ACCEL["Acceleration Structure"]
    end
    
    subgraph "Demand Loading Integration"
        DEMANDLOADER["DemandLoader"]
        TEXTURES["DemandTexture"]
        DEVCTX["DeviceContext"]
    end
    
    subgraph "UI and Display"
        GLFW["GLFW Window"]
        IMGUI["ImGui Interface"]
        CUDABUFFER["CUDAOutputBuffer"]
        GLDISPLAY["GLDisplay"]
    end

    %% Inheritance relationships
    PBRT --> OTKAPP
    TEXVIEWER --> OTKAPP
    UDIM --> OTKAPP
    PAINT --> OTKAPP
    
    %% Framework dependencies
    OTKAPP --> PARAMS
    OTKAPP --> DEVICE
    OTKAPP --> OPTIX
    OTKAPP --> SHAPES
    
    %% OptiX integration
    OTKAPP --> CONTEXT
    OTKAPP --> PIPELINE
    OTKAPP --> SBT
    OTKAPP --> ACCEL
    
    %% Demand loading integration
    OTKAPP --> DEMANDLOADER
    OTKAPP --> TEXTURES
    PARAMS --> DEVCTX
    
    %% UI integration
    OTKAPP --> GLFW
    PBRT --> IMGUI
    OTKAPP --> CUDABUFFER
    OTKAPP --> GLDISPLAY
```

Sources: [examples/OTKAppBase/include/OptiXToolkit/OTKAppBase/OTKApp.h:30-159](), [examples/OTKAppBase/src/OTKApp.cpp:54-88]()

### Core Application Components

| Component | Purpose | Key Classes |
|-----------|---------|-------------|
| **Application Base** | Common OptiX setup and rendering loop | `OTKApp`, `OTKAppPerDeviceOptixState` |
| **Launch Parameters** | GPU kernel parameter structure | `OTKAppLaunchParams`, `OTKAppRayPayload` |
| **Device Utilities** | GPU helper functions | Functions in `OTKAppDeviceUtil.h` |
| **OptiX Programs** | Standard ray tracing shaders | `__miss__OTKApp`, `__closesthit__OTKApp` |
| **Shape Generation** | Geometric primitive creation | `OTKAppShapeMaker` |

Sources: [examples/OTKAppBase/include/OptiXToolkit/OTKAppBase/OTKAppLaunchParams.h:40-71](), [examples/OTKAppBase/include/OptiXToolkit/OTKAppBase/OTKAppDeviceUtil.h:29-98]()

## DemandPbrtScene Viewer

The most sophisticated example application, `DemandPbrtScene` provides a full-featured PBRT scene viewer with advanced demand loading capabilities.

### DemandPbrtScene System Architecture

```mermaid
graph TB
    subgraph "Application Entry"
        MAIN["main.cpp"]
        APP["Application"]
    end
    
    subgraph "Scene Management"
        SCENE["PbrtScene"]
        SCENELOADER["PbrtSceneLoader"] 
        SCENEDESC["SceneDescription"]
        SCENESYNC["SceneSyncState"]
    end
    
    subgraph "Rendering Pipeline"
        RENDERER["OptixRenderer"]
        PROGRAMS["ProgramGroups"]
        KERNELS["DemandPbrtScene.cu"]
    end
    
    subgraph "Demand Resolution"
        GEOMRESOLVER["GeometryResolver"]
        MATRESOLVER["MaterialResolver"]
        GEOMCACHE["GeometryCache"]
        TEXTURECACHE["DemandTextureCache"]
    end
    
    subgraph "User Interface"
        UI["ImGuiUserInterface"]
        STATS["Statistics"]
        OPTIONS["Options"]
    end
    
    subgraph "OptiX Integration"
        CONTEXT["OptixDeviceContext"]
        TRAVERSABLE["OptixTraversableHandle"]
        PARAMS["Params"]
    end

    %% Flow relationships
    MAIN --> APP
    APP --> SCENE
    APP --> UI
    APP --> RENDERER
    
    SCENE --> SCENELOADER
    SCENE --> GEOMRESOLVER
    SCENE --> MATRESOLVER
    SCENE --> SCENESYNC
    
    SCENELOADER --> SCENEDESC
    
    GEOMRESOLVER --> GEOMCACHE
    MATRESOLVER --> TEXTURECACHE
    
    RENDERER --> PROGRAMS
    RENDERER --> CONTEXT
    PROGRAMS --> KERNELS
    
    SCENE --> TRAVERSABLE
    RENDERER --> PARAMS
    
    UI --> STATS
    UI --> OPTIONS
    
    %% Data flow
    SCENEDESC -.-> GEOMRESOLVER
    SCENEDESC -.-> MATRESOLVER
    GEOMCACHE -.-> SCENESYNC
    TEXTURECACHE -.-> SCENESYNC
    SCENESYNC -.-> PARAMS
```

Sources: [examples/DemandLoading/DemandPbrtScene/PbrtScene.cpp:44-94](), [examples/DemandLoading/DemandPbrtScene/ImGuiUserInterface.cpp:52-119]()

### Key Features

The `DemandPbrtScene` application demonstrates:

- **Scene Proxy System**: Decomposes complex scenes into demand-loadable components through `GeometryResolver` and `MaterialResolver`
- **Interactive Rendering**: Multiple rendering modes (primary ray, ambient occlusion, path tracing) via `RenderMode` enum
- **Statistics Collection**: Comprehensive performance monitoring through `UserInterfaceStatistics`
- **Debug Capabilities**: Pixel-level debugging and performance analysis

The main application logic resides in `PbrtScene::beforeLaunch()` and `PbrtScene::afterLaunch()`, which coordinate demand loading requests and scene updates.

Sources: [examples/DemandLoading/DemandPbrtScene/PbrtScene.cpp:321-346](), [examples/DemandLoading/DemandPbrtScene/ImGuiUserInterface.cpp:233-297]()

## Texture Viewer Applications

### DemandTextureViewer

A straightforward texture viewing application that demonstrates basic demand loading capabilities.

```mermaid
graph LR
    subgraph "DemandTextureViewer Flow"
        MAIN["main()"]
        APP["DemandTextureViewer"]
        IMGSRC["ImageSource"]
        TEXTURE["DemandTexture"]
        KERNEL["DemandTextureViewer.cu"]
    end
    
    MAIN --> APP
    APP --> IMGSRC
    IMGSRC --> TEXTURE
    APP --> KERNEL
    TEXTURE -.-> KERNEL
```

Key implementation details:
- Creates `ImageSource` objects with optional tiling and mipmapping via `createImageSource()`
- Uses `tex2DGrad()` for texture sampling in the CUDA kernel
- Supports both ray casting and direct texture coordinate calculation

Sources: [examples/DemandLoading/DemandTextureViewer/DemandTextureViewer.cpp:44-78](), [examples/DemandLoading/DemandTextureViewer/DemandTextureViewer.cu:22-66]()

### UdimTextureViewer

Demonstrates UDIM (UV Tile) texture support for complex texture atlases.

```mermaid
graph TB
    subgraph "UDIM Texture Creation"
        TEXNAME["Texture Name Pattern"]
        SUBIMAGES["Sub-image Sources"]
        DESCRIPTORS["Texture Descriptors"]
        UDIMTEX["UDIM Texture"]
    end
    
    subgraph "Rendering"
        KERNEL["UdimTextureViewer.cu"]
        SAMPLING["tex2DGradUdimBlend()"]
        OUTPUT["Rendered Output"]
    end
    
    TEXNAME --> SUBIMAGES
    SUBIMAGES --> DESCRIPTORS
    DESCRIPTORS --> UDIMTEX
    UDIMTEX --> KERNEL
    KERNEL --> SAMPLING
    SAMPLING --> OUTPUT
```

The application creates UDIM textures by:
1. Generating sub-images for each U,V tile coordinate
2. Creating texture descriptors with `CU_TR_ADDRESS_MODE_BORDER` for proper blending
3. Using `createUdimTexture()` to combine sub-images into a single addressable texture

Sources: [examples/DemandLoading/UdimTextureViewer/UdimTextureViewer.cpp:91-144]()

## TexturePainting Application

An interactive painting application showcasing real-time texture modification and tile reloading.

### TexturePainting Architecture

```mermaid
graph TB
    subgraph "Canvas Management"
        CANVASES["CanvasImage[4]"]
        BRUSH["CanvasBrush"]
        DIRTY["Dirty Tiles Set"]
    end
    
    subgraph "Interaction Handling"
        MOUSE["Mouse Events"]
        KEYBOARD["Key Events"]
        COORDS["Mouse to Image Coords"]
    end
    
    subgraph "Texture Updates"
        RELOAD["reloadDirtyTiles()"]
        DEMANDLOADER["DemandLoader"]
        TILELOAD["loadTextureTile()"]
    end
    
    subgraph "Rendering"
        TEXTURE["DemandTexture"]
        KERNEL["TexturePainting.cu"]
        DISPLAY["Visual Output"]
    end

    MOUSE --> COORDS
    COORDS --> BRUSH
    BRUSH --> CANVASES
    CANVASES --> DIRTY
    DIRTY --> RELOAD
    RELOAD --> DEMANDLOADER
    DEMANDLOADER --> TILELOAD
    
    KEYBOARD --> BRUSH
    
    CANVASES --> TEXTURE
    TEXTURE --> KERNEL
    KERNEL --> DISPLAY
```

Sources: [examples/DemandLoading/TexturePainting/TexturePainting.cpp:122-171](), [examples/DemandLoading/TexturePainting/TexturePainting.cpp:245-263]()

### Interactive Features

The `TexturePainting` application provides:

- **Real-time Editing**: Direct painting on textures through `CanvasImage` and `CanvasBrush`
- **Multi-canvas Support**: Switch between 4 different canvases using number keys or UI buttons
- **Selective Tile Reloading**: Only reloads modified texture tiles via `reloadDirtyTiles()`
- **Brush Customization**: Adjustable size and color through mouse and keyboard interaction

Key interaction methods:
- `mouseToImageCoords()`: Converts screen coordinates to texture space
- `drawStroke()`: Paints between two points for smooth drawing
- `loadTextureTile()`: Refreshes specific texture tiles after modification

Sources: [examples/DemandLoading/TexturePainting/TexturePainting.cpp:227-235](), [examples/DemandLoading/TexturePainting/TexturePainting.cpp:152-157]()

## Common Application Patterns

### Initialization Sequence

All example applications follow a consistent initialization pattern:

```mermaid
sequenceDiagram
    participant App as "Application"
    participant OTK as "OTKApp"
    participant DL as "DemandLoader"
    participant OptiX as "OptiX Pipeline"
    
    App->>OTK: Create application
    App->>DL: initDemandLoading()
    App->>App: createTexture()
    App->>App: createScene()
    App->>OptiX: initOptixPipelines()
    App->>App: startLaunchLoop()
```

### Launch Loop Pattern

The rendering loop in `OTKApp::performLaunches()` provides the core execution pattern:

1. **Demand Loading Preparation**: Call `demandLoader->launchPrepare()`
2. **OptiX Launch**: Execute `optixLaunch()` with current parameters
3. **Request Processing**: Handle demand loading requests with `processRequests()`
4. **Convergence Check**: Continue until all requests are satisfied

Sources: [examples/OTKAppBase/src/OTKApp.cpp:495-567]()

### Texture Descriptor Patterns

Applications consistently use `makeTextureDescriptor()` to configure textures:

- **Address Mode**: Typically `CU_TR_ADDRESS_MODE_CLAMP` for single textures, `CU_TR_ADDRESS_MODE_BORDER` for UDIM tiles
- **Filter Mode**: `FILTER_BILINEAR` for smooth interpolation
- **Mipmap Support**: Automatic mipmap generation through `createMipMapImageSource()`

Sources: [examples/OTKAppBase/src/OTKApp.cpp:426-436](), [examples/DemandLoading/UdimTextureViewer/UdimTextureViewer.cpp:126-131]()

---

