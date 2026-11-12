<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/nsight-aftermath-samples · page 2 Vulkan Sample (VkHelloNsightAftermath) · fetched 2026-10-26 -->

# Vulkan Sample (VkHelloNsightAftermath)

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [VkHelloNsightAftermath/README.md](VkHelloNsightAftermath/README.md)
- [VkHelloNsightAftermath/VkHelloNsightAftermath.cpp](VkHelloNsightAftermath/VkHelloNsightAftermath.cpp)

</details>



## Purpose and Scope

This document covers the primary Vulkan-based demonstration sample in the NVIDIA Nsight Aftermath repository. The `VkHelloNsightAftermath` application serves as a comprehensive reference implementation showing how to integrate NVIDIA Nsight Aftermath GPU crash debugging capabilities into a Vulkan graphics application. The sample intentionally triggers GPU crashes to demonstrate the complete crash dump collection and analysis workflow.

For information about the Direct3D 12 equivalent sample, see [Direct3D 12 Sample](#3). For general development setup instructions, see [Development Setup](#4).

## Application Architecture Overview

The `VkHelloNsightAftermath` sample is built around a monolithic `Demo` class that encapsulates all Vulkan operations, platform-specific windowing, and Nsight Aftermath integration. The application follows a traditional Vulkan rendering architecture with added instrumentation for crash dump generation.

**Core Application Structure**

```mermaid
graph TD
    subgraph "VkHelloNsightAftermath Application"
        DemoClass["Demo Class<br/>(Main Controller)"]
        VulkanCore["Vulkan Core Systems<br/>(Instance, Device, Queues)"]
        RenderSys["Rendering Systems<br/>(Pipeline, Buffers, Textures)"]
        WindowSys["Window Management<br/>(Platform-Specific)"]
    end
    
    subgraph "Nsight Aftermath Integration"
        CrashTracker["gpuCrashTracker<br/>(GpuCrashTracker)"]
        MarkerMap["markerMap<br/>(MarkerMap)"]
        FrameTracking["frameNumber<br/>(uint64_t)"]
    end
    
    subgraph "Platform Abstraction"
        Win32["Win32 (Windows)"]
        XCB["XCB (Linux)"]
        Wayland["Wayland (Linux)"]
    end
    
    DemoClass --> VulkanCore
    DemoClass --> RenderSys
    DemoClass --> WindowSys
    DemoClass --> CrashTracker
    DemoClass --> MarkerMap
    
    WindowSys --> Win32
    WindowSys --> XCB
    WindowSys --> Wayland
    
    CrashTracker --> MarkerMap
    CrashTracker --> FrameTracking
```

Sources: [VkHelloNsightAftermath/VkHelloNsightAftermath.cpp:237-429]()

**Demo Class Core Components**

The `Demo` class contains all essential Vulkan objects and Nsight Aftermath integration components:

| Component Category | Key Members | Purpose |
|-------------------|-------------|---------|
| Vulkan Core | `inst`, `gpu`, `device`, `graphics_queue` | Core Vulkan objects |
| Rendering | `swapchain`, `render_pass`, `pipeline` | Graphics pipeline |
| Resources | `uniform_data`, `textures[]`, `depth` | Rendering resources |
| Synchronization | `fences[]`, `*_semaphores[]` | Frame synchronization |
| Aftermath Integration | `gpuCrashTracker`, `markerMap`, `frameNumber` | Crash debugging |

Sources: [VkHelloNsightAftermath/VkHelloNsightAftermath.cpp:325-428]()

## Nsight Aftermath Integration Points

The application demonstrates several key integration points where Nsight Aftermath functionality is woven into the standard Vulkan workflow.

**Device Creation with Aftermath Features**

```mermaid
graph LR
    DeviceSetup["Device Setup"] --> AftermathConfig["vk::DeviceDiagnosticsConfigCreateInfoNV"]
    AftermathConfig --> EnableFlags["Aftermath Flags<br/>• Resource Tracking<br/>• Auto Checkpoints<br/>• Shader Debug Info<br/>• Error Reporting"]
    EnableFlags --> DeviceCreation["gpu.createDevice()"]
    DeviceCreation --> CrashTrackerInit["gpuCrashTracker.Initialize()"]
```

Sources: [VkHelloNsightAftermath/VkHelloNsightAftermath.cpp:747-800]()

The application enables comprehensive Aftermath features during device creation:
- **Resource Tracking**: Captures resource information for GPU page fault analysis
- **Automatic Checkpoints**: Automatically captures call stacks for draw/dispatch operations  
- **Shader Debug Info**: Generates debug information for all shaders
- **Error Reporting**: Enables enhanced error reporting capabilities

**Checkpoint Marker System**

```mermaid
graph TD
    RenderLoop["Render Loop"] --> FrameMarkerSetup["Frame Marker Setup<br/>markerMapIndex = frameNumber % 4"]
    FrameMarkerSetup --> MarkerCreation["Marker Creation<br/>markerID = markerMapIndex * 10000 + count + 1"]
    MarkerCreation --> MarkerStorage["Store in MarkerMap<br/>markerMap[markerMapIndex][markerID] = markerData"]
    MarkerStorage --> CheckpointCall["commandBuffer.setCheckpointNV(markerID)"]
    CheckpointCall --> GPUExecution["GPU Command Execution"]
```

Sources: [VkHelloNsightAftermath/VkHelloNsightAftermath.cpp:972-1007]()

The marker system provides a rolling buffer of debug information across the last 4 frames, enabling precise crash location identification.

## Rendering Pipeline and Crash Demonstration

The application implements a standard Vulkan rendering pipeline that renders a textured cube with intentional crash triggering for demonstration purposes.

**Core Rendering Flow**

```mermaid
graph TD
    AppInit["Application Initialize<br/>Demo::init()"] --> VulkanInit["Vulkan Setup<br/>init_vk(), init_vk_swapchain()"]
    VulkanInit --> ResourcePrep["Resource Preparation<br/>prepare()"]
    ResourcePrep --> RenderLoop["Main Render Loop<br/>draw()"]
    
    subgraph "Render Loop Components"
        AcquireImage["Acquire Swapchain Image<br/>acquireNextImageKHR()"]
        UpdateBuffers["Update Uniform Buffers<br/>update_data_buffer()"]
        RecordCommands["Record Command Buffer<br/>draw_build_cmd()"]
        SubmitWork["Submit to Graphics Queue<br/>graphics_queue.submit()"]
        Present["Present Frame<br/>present_queue.presentKHR()"]
    end
    
    RenderLoop --> AcquireImage
    AcquireImage --> UpdateBuffers
    UpdateBuffers --> RecordCommands
    RecordCommands --> SubmitWork
    SubmitWork --> Present
    Present --> RenderLoop
```

Sources: [VkHelloNsightAftermath/VkHelloNsightAftermath.cpp:809-943](), [VkHelloNsightAftermath/VkHelloNsightAftermath.cpp:945-1040]()

**GPU Crash Handling Mechanism**

The application includes sophisticated error handling for intentionally triggered GPU crashes:

```mermaid
sequenceDiagram
    participant App as "Demo::draw()"
    participant Vulkan as "Vulkan Driver"
    participant Aftermath as "Nsight Aftermath"
    participant FileSystem as "File System"
    
    App->>Vulkan: waitForFences()
    Vulkan-->>App: VK_ERROR_DEVICE_LOST
    App->>Aftermath: GFSDK_Aftermath_GetCrashDumpStatus()
    
    loop "Wait for Crash Dump Processing"
        App->>App: sleep_for(50ms)
        App->>Aftermath: GFSDK_Aftermath_GetCrashDumpStatus()
        Aftermath-->>App: Status Update
    end
    
    Aftermath->>FileSystem: Write .nv-gpudmp file
    Aftermath->>FileSystem: Write .json decoded file
    App->>App: exit(1)
```

Sources: [VkHelloNsightAftermath/VkHelloNsightAftermath.cpp:814-848]()

## Resource Management and Shader Handling

The application demonstrates proper resource lifecycle management and shader binary handling for Aftermath integration.

**Shader Loading System**

```mermaid
graph LR
    LoadShader["LoadSpirvBinary()"] --> FileRead["Read SPIR-V File<br/>(cube.vert.spirv, cube.frag.spirv)"]
    FileRead --> ShaderModule["prepare_shader_module()"]
    ShaderModule --> PipelineStage["Pipeline Stage Creation<br/>VkPipelineShaderStageCreateInfo"]
    
    subgraph "Shader Variants"
        FullShader["cube.*.full.spirv<br/>(Debug Info)"]
        StrippedShader["cube.*.spirv<br/>(Optimized)"]
    end
    
    FileRead --> FullShader
    FileRead --> StrippedShader
```

Sources: [VkHelloNsightAftermath/VkHelloNsightAftermath.cpp:544-554](), [VkHelloNsightAftermath/VkHelloNsightAftermath.cpp:2101-2107]()

The application supports both full debug shaders and stripped optimized shaders, controlled by the `use_stripped_shaders` flag.

**Memory and Resource Management**

| Resource Type | Management Strategy | Cleanup Location |
|---------------|-------------------|------------------|
| Swapchain Images | Per-frame resources in `SwapchainImageResources` | `Demo::cleanup()` |
| Uniform Buffers | Per-swapchain-image allocation | `Demo::prepare_cube_data_buffers()` |
| Textures | Static allocation with staging buffers | `Demo::destroy_texture()` |
| Command Pools | Graphics and present queue pools | `Demo::cleanup()` |

Sources: [VkHelloNsightAftermath/VkHelloNsightAftermath.cpp:663-737](), [VkHelloNsightAftermath/VkHelloNsightAftermath.cpp:1904-1961]()

## Platform Integration and Window Management

The application provides comprehensive cross-platform support through conditional compilation and platform-specific windowing code.

**Platform Support Matrix**

```mermaid
graph TD
    VkApp["VkHelloNsightAftermath"] --> PlatformLayer["Platform Abstraction Layer"]
    
    subgraph "Windows Support"
        Win32API["Win32 API<br/>VK_USE_PLATFORM_WIN32_KHR"]
        WinSurface["vk::Win32SurfaceCreateInfoKHR"]
    end
    
    subgraph "Linux Support"  
        XCBSupport["XCB<br/>VK_USE_PLATFORM_XCB_KHR"]
        WaylandSupport["Wayland<br/>VK_USE_PLATFORM_WAYLAND_KHR"]
        XlibSupport["Xlib<br/>VK_USE_PLATFORM_XLIB_KHR"]
    end
    
    subgraph "macOS Support"
        MVKSupport["MoltenVK<br/>VK_USE_PLATFORM_MACOS_MVK"]
    end
    
    PlatformLayer --> Win32API
    PlatformLayer --> XCBSupport  
    PlatformLayer --> WaylandSupport
    PlatformLayer --> XlibSupport
    PlatformLayer --> MVKSupport
```

Sources: [VkHelloNsightAftermath/VkHelloNsightAftermath.cpp:276-295](), [VkHelloNsightAftermath/VkHelloNsightAftermath.cpp:1500-1550]()

The application uses preprocessor directives to conditionally compile platform-specific windowing code, ensuring broad compatibility while maintaining clean separation of platform concerns.

---

