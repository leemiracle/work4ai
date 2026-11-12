<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/VisRTX · page 2 VisRTX RTX Device · fetched 2026-10-26 -->

# VisRTX RTX Device

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [devices/rtx/device/CMakeLists.txt](devices/rtx/device/CMakeLists.txt)
- [devices/rtx/device/VisRTXDevice.cpp](devices/rtx/device/VisRTXDevice.cpp)
- [devices/rtx/device/gpu/gpu_objects.h](devices/rtx/device/gpu/gpu_objects.h)
- [devices/rtx/device/optix_visrtx.h](devices/rtx/device/optix_visrtx.h)
- [devices/rtx/device/renderer/Quality.cpp](devices/rtx/device/renderer/Quality.cpp)
- [devices/rtx/device/renderer/Quality.h](devices/rtx/device/renderer/Quality.h)
- [devices/rtx/device/renderer/Renderer.cpp](devices/rtx/device/renderer/Renderer.cpp)
- [devices/rtx/device/renderer/Renderer.h](devices/rtx/device/renderer/Renderer.h)
- [devices/rtx/device/visrtx_device.json](devices/rtx/device/visrtx_device.json)
- [devices/rtx/device/visrtx_renderer_debug.json](devices/rtx/device/visrtx_renderer_debug.json)
- [devices/rtx/device/visrtx_renderer_default.json](devices/rtx/device/visrtx_renderer_default.json)
- [devices/rtx/device/visrtx_renderer_fast.json](devices/rtx/device/visrtx_renderer_fast.json)
- [devices/rtx/device/visrtx_renderer_interactive.json](devices/rtx/device/visrtx_renderer_interactive.json)
- [devices/rtx/device/visrtx_renderer_quality.json](devices/rtx/device/visrtx_renderer_quality.json)

</details>



The VisRTX RTX Device is an ANARI device implementation built on NVIDIA OptiX, designed for high-performance, GPU-accelerated rendering. It leverages the power of NVIDIA RTX GPUs to provide advanced rendering capabilities, including physically based materials, complex geometries, and volume rendering. This page provides a high-level overview of its architecture and features, with links to more detailed child pages.

The device adheres to the ANARI API specification, providing a standardized interface for scene description and rendering. It supports a wide range of ANARI extensions, enabling advanced features such as compressed textures, various camera models, diverse light types, and specialized spatial fields [devices/rtx/device/visrtx_device.json:5-61]().

## Device Initialization & ANARI API Layer

The core of the VisRTX device is managed by the `VisRTXDevice` class [devices/rtx/device/VisRTXDevice.cpp:43-886](). This class is responsible for setting up the CUDA and OptiX contexts, managing device-global state, and providing factory methods for creating ANARI objects like cameras, geometries, materials, and renderers [devices/rtx/device/VisRTXDevice.cpp:130-300](). It also handles the construction of the OptiX Shader Binding Table (SBT) and the embedding of PTX (Parallel Thread Execution) code via `EmbedPTX.cmake`. The device's capabilities and supported extensions are defined in `visrtx_device.json`, which is used to generate ANARI query information. For details, see [Device Initialization & ANARI API Layer](#2.1).

Sources:
- [devices/rtx/device/VisRTXDevice.cpp:43-886]()
- [devices/rtx/device/VisRTXDevice.cpp:130-300]()
- [devices/rtx/device/visrtx_device.json:5-61]()

## GPU Rendering Pipeline & Renderers

The VisRTX device implements a sophisticated GPU rendering pipeline, supporting four distinct renderer modes: "Quality", "Interactive", "Fast", and "Debug" [devices/rtx/device/renderer/Renderer.cpp:114-129](). Each renderer offers a different balance of visual fidelity and performance. For instance, the "Quality" renderer [devices/rtx/device/renderer/Quality.h:38-51]() employs a path-tracing loop implemented in `Quality_ptx.cu` for high-fidelity results, while "Interactive" and "Fast" prioritize responsiveness. The rendering process involves various OptiX program types, including `__raygen__`, `__closesthit__`, `__anyhit__`, and `__miss__` programs, which define how rays are generated, intersect with geometry, and behave when no intersection occurs [devices/rtx/device/renderer/Renderer.h:49-52](). The pipeline also incorporates features like shadow transmittance, ambient occlusion, and utilizes Halton/PCG random number generators for stochastic sampling. For details, see [GPU Rendering Pipeline & Renderers](#2.2).

### Renderer Modes

The VisRTX device provides several renderer types, each optimized for different use cases:

| Renderer Type | Description | Key Parameters |
| :------------ | :---------- | :------------- |
| `quality`     | High-fidelity path tracing with advanced lighting and material interactions. | `maxRayDepth`, `maxTransparencyDepth`, `pixelSamples`, `denoise`, `fireflyFilter` [devices/rtx/device/visrtx_renderer_quality.json]() |
| `interactive` | Optimized for interactive performance, often using simplified lighting models and fewer samples. | `ambientSamples`, `ambientOcclusionDistance`, `lightFalloff`, `volumeSamplingRate` [devices/rtx/device/visrtx_renderer_interactive.json]() |
| `fast`        | Fastest rendering mode, typically for quick previews or simple scenes. | `fixedAmbientLighting`, `ambientSamples`, `aoBlend` [devices/rtx/device/visrtx_renderer_fast.json]() |
| `debug`       | Provides various visualization modes for debugging scene properties like normals, depth, or IDs. | `method` (e.g., "normals", "depth", "primID") [devices/rtx/device/visrtx_renderer_debug.json]() |
| `default`     | An alias for the `interactive` renderer. [devices/rtx/device/visrtx_renderer_default.json]() | Same as `interactive` |

Sources:
- [devices/rtx/device/renderer/Renderer.cpp:114-129]()
- [devices/rtx/device/renderer/Quality.h:38-51]()
- [devices/rtx/device/renderer/Renderer.h:49-52]()
- [devices/rtx/device/visrtx_renderer_quality.json]()
- [devices/rtx/device/visrtx_renderer_interactive.json]()
- [devices/rtx/device/visrtx_renderer_fast.json]()
- [devices/rtx/device/visrtx_renderer_debug.json]()
- [devices/rtx/device/visrtx_renderer_default.json]()

## Material System

The material system in VisRTX supports three primary material models: "Matte", "PhysicallyBased" (PBR), and "MDL" (Material Definition Language) [devices/rtx/device/material/Material.cpp:40-50](). These models are defined by `ShadingState` structs and interact with a direct-callable material interface for evaluating properties like tint, opacity, emission, and surface shading. The MDL backend, when enabled, utilizes `libmdl::Core` and `ArgumentBlockDescriptor` for advanced material definitions. The `evalMaterialParameters` helper function is crucial for parameter evaluation. For details, see [Material System](#2.3).

Sources:
- [devices/rtx/device/material/Material.cpp:40-50]()

## Geometry, Spatial Fields & Volume Rendering

VisRTX supports a diverse set of geometry types, including "triangle", "sphere", "cylinder", "cone", "curve", "quad", "SDF" (Signed Distance Fields), and "neural" geometries [devices/rtx/device/gpu/gpu_objects.h:124-135](). The `populateHit` pipeline is responsible for processing ray-geometry intersections. The device also handles various spatial field types, such as "StructuredRegular", "StructuredRectilinear", "NvdbRegular", "NvdbRectilinear", and "CustomField" [devices/rtx/device/spatial_field/SpatialField.cpp:40-50](). Volume rendering is achieved through techniques like delta tracking and ratio tracking, often utilizing space-skipping `UniformGrid` structures and `TransferFunction1D` for mapping data values to visual properties. For details, see [Geometry, Spatial Fields & Volume Rendering](#2.4).

Sources:
- [devices/rtx/device/gpu/gpu_objects.h:124-135]()
- [devices/rtx/device/spatial_field/SpatialField.cpp:40-50]()

## Frame, Denoiser & Samplers

The `Frame` object is central to managing rendering output, handling accumulation, channel mapping, and supporting CUDA buffer extensions (`NV_FRAME_BUFFERS_CUDA`). VisRTX integrates the OptiX AI denoiser to improve image quality by removing noise from rendered frames. The device also provides various image sampler types, including `Image1D`, `Image2D`, `Image3D`, `CompressedImage2D`, `Primitive`, and `Transform` samplers, for accessing texture data. GPU memory management for these samplers and other data is often handled by the `UploadableArray` pattern. For details, see [Frame, Denoiser & Samplers](#2.5).

Sources:
- [devices/rtx/device/gpu/gpu_objects.h:286-290]()
- [devices/rtx/device/array/UploadableArray.h]()
- [devices/rtx/device/frame/Frame.cu]()
- [devices/rtx/device/frame/Denoiser.cu]()

---

