<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/optix-toolkit · extra page CUDA Kernels and Rendering · fetched 2026-10-26 -->

# CUDA Kernels and Rendering

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [DemandLoading/DemandLoading/tests/DeferredImageLoadingKernels.cu](DemandLoading/DemandLoading/tests/DeferredImageLoadingKernels.cu)
- [Memory/tests/TestDeviceMemoryPools.cu](Memory/tests/TestDeviceMemoryPools.cu)
- [ShaderUtil/tests/TestDebugLocation.cu](ShaderUtil/tests/TestDebugLocation.cu)
- [examples/DemandLoading/DemandGeometryViewer/Sphere.cu](examples/DemandLoading/DemandGeometryViewer/Sphere.cu)
- [examples/DemandLoading/DemandPbrtScene/DemandPbrtScene.cu](examples/DemandLoading/DemandPbrtScene/DemandPbrtScene.cu)
- [examples/DemandLoading/DemandPbrtScene/PhongMaterial.cu](examples/DemandLoading/DemandPbrtScene/PhongMaterial.cu)
- [examples/DemandLoading/DemandPbrtScene/include/DemandPbrtScene/DeviceTriangles.h](examples/DemandLoading/DemandPbrtScene/include/DemandPbrtScene/DeviceTriangles.h)
- [examples/DemandLoading/TexturePainting/CMakeLists.txt](examples/DemandLoading/TexturePainting/CMakeLists.txt)
- [examples/DemandLoading/TexturePainting/TexturePainting.cu](examples/DemandLoading/TexturePainting/TexturePainting.cu)
- [examples/DemandLoading/TexturePainting/TexturePaintingParams.h](examples/DemandLoading/TexturePainting/TexturePaintingParams.h)

</details>



This document covers the CUDA kernel implementation and rendering pipeline of the PbrtScene viewer, focusing on the OptiX ray tracing programs that handle camera ray generation, material shading, and intersection processing. The kernels implement multiple rendering modes including primary ray visualization, path tracing, and ambient occlusion.

For information about the scene proxy system and geometry management, see [Scene Proxy System](#5.1.1). For details about PBRT file parsing and scene loading, see [PBRT Scene Loading](#5.3).

## OptiX Program Architecture

The PbrtScene viewer implements a complete OptiX ray tracing pipeline with specialized programs for different ray types and geometry intersections. The kernel architecture follows OptiX's shader binding table (SBT) model with distinct program types for ray generation, material handling, and intersection processing.

```mermaid
graph TB
    subgraph "Ray Generation Programs"
        RAYGEN["__raygen__perspectiveCamera()"]
    end
    
    subgraph "Miss Programs"
        MISS["__miss__backgroundColor()"]
    end
    
    subgraph "Hit Group Programs - Triangular Meshes"
        CH_MESH["__closesthit__mesh()"]
        CH_TEXTURED["__closesthit__texturedMesh()"]
        AH_ALPHA["__anyhit__alphaCutOutMesh()"]
        AH_PARTIAL["__anyhit__alphaCutOutPartialMesh()"]
    end
    
    subgraph "Hit Group Programs - Spheres"
        CH_SPHERE["__closesthit__sphere()"]
        AH_SPHERE["__anyhit__sphere()"]
    end
    
    subgraph "Shared Utilities"
        TRIANGLES["DeviceTriangles.h"]
        PARAMS["Params structure"]
        PAYLOAD["RayPayload structure"]
    end
    
    RAYGEN --> |"optixTrace()"| CH_MESH
    RAYGEN --> |"optixTrace()"| CH_TEXTURED
    RAYGEN --> |"optixTrace()"| CH_SPHERE
    RAYGEN --> |"optixTrace()"| MISS
    
    CH_MESH --> TRIANGLES
    CH_TEXTURED --> TRIANGLES
    CH_SPHERE --> PARAMS
    
    AH_ALPHA --> |"optixIgnoreIntersection()"| CH_TEXTURED
    AH_PARTIAL --> |"optixIgnoreIntersection()"| CH_TEXTURED
    
    TRIANGLES --> PARAMS
    CH_MESH --> PAYLOAD
    CH_TEXTURED --> PAYLOAD
    CH_SPHERE --> PAYLOAD
```

**Sources:** [examples/DemandLoading/DemandPbrtScene/DemandPbrtScene.cu:138-808](), [examples/DemandLoading/DemandPbrtScene/PhongMaterial.cu:19-142]()

## Ray Generation and Camera Models

The `__raygen__perspectiveCamera` kernel serves as the entry point for all rays, supporting both PBRT-compatible camera transformations and simplified pinhole camera models. The kernel handles anti-aliasing through jittered sampling and implements different rendering modes.

### Camera Ray Computation

The ray generation kernel supports two camera models controlled by the `usePinholeCamera` parameter:

| Camera Model | Description | Implementation |
|--------------|-------------|----------------|
| **PBRT Camera** | Full camera transformation pipeline using `cameraToWorld` and `cameraToScreen` matrices | [DemandPbrtScene.cu:150-159]() |
| **Pinhole Camera** | Simplified model using `LookAtParams` with eye, lookAt, and up vectors | [DemandPbrtScene.cu:162-168]() |

```mermaid
graph LR
    subgraph "Ray Generation Flow"
        LAUNCH["optixGetLaunchIndex()"] 
        PIXEL["Pixel coordinates"]
        JITTER["Anti-aliasing jitter"]
        CAMERA_CALC["Camera ray calculation"]
        TRACE["optixTrace()"]
        ACCUMULATE["accumulateValue()"]
    end
    
    subgraph "Camera Models"
        PBRT["PBRT Transform Chain"]
        PINHOLE["Pinhole uvwFrame()"]
    end
    
    subgraph "Rendering Modes"
        PRIMARY["PRIMARY_RAY"]
        PATH["PATH_TRACING"] 
        AO["Ambient Occlusion"]
    end
    
    LAUNCH --> PIXEL
    PIXEL --> JITTER
    JITTER --> CAMERA_CALC
    CAMERA_CALC --> PBRT
    CAMERA_CALC --> PINHOLE
    PBRT --> TRACE
    PINHOLE --> TRACE
    TRACE --> PRIMARY
    TRACE --> PATH
    TRACE --> AO
    PRIMARY --> ACCUMULATE
    PATH --> ACCUMULATE
    AO --> ACCUMULATE
```

**Sources:** [examples/DemandLoading/DemandPbrtScene/DemandPbrtScene.cu:138-369](), [examples/DemandLoading/DemandPbrtScene/DemandPbrtScene.cu:49-60]()

## Hit Group Programs and Material Processing

The viewer implements specialized hit group programs for different geometry types and material configurations. Each hit group extracts intersection data, processes materials, and updates the ray payload for subsequent rendering stages.

### Triangle Mesh Hit Groups

The triangle mesh hit groups handle both simple materials and textured surfaces with alpha cutout support:

```mermaid
graph TB
    subgraph "Triangle Hit Processing"
        GET_TRI["getTriangleData()"]
        GET_MAT["getMaterialId()"]
        GET_UV["getTriangleUVs()"]
        SET_PAYLOAD["Set RayPayload"]
    end
    
    subgraph "Material Resolution"
        MAT_INDEX["MaterialIndex lookup"]
        PRIM_RANGE["PrimitiveMaterialRange"]
        REALIZED["realizedMaterials array"]
        PARTIAL["partialMaterials array"]
    end
    
    subgraph "Texture Handling"
        DIFFUSE_TEX["diffuseTextureId"]
        ALPHA_TEX["alphaTextureId"]
        UV_CALC["UV coordinate calculation"]
        TEX_SIZE["worldSpaceTextureSize"]
    end
    
    GET_TRI --> GET_MAT
    GET_MAT --> MAT_INDEX
    MAT_INDEX --> PRIM_RANGE
    PRIM_RANGE --> REALIZED
    PRIM_RANGE --> PARTIAL
    
    GET_UV --> UV_CALC
    UV_CALC --> DIFFUSE_TEX
    UV_CALC --> ALPHA_TEX
    
    REALIZED --> SET_PAYLOAD
    UV_CALC --> TEX_SIZE
    TEX_SIZE --> SET_PAYLOAD
```

**Sources:** [examples/DemandLoading/DemandPbrtScene/DemandPbrtScene.cu:816-859](), [examples/DemandLoading/DemandPbrtScene/PhongMaterial.cu:19-59](), [examples/DemandLoading/DemandPbrtScene/include/DemandPbrtScene/DeviceTriangles.h:35-64]()

### Alpha Cutout Processing

The any-hit programs implement alpha cutout functionality for transparent materials using demand-loaded alpha textures:

```mermaid
graph LR
    subgraph "Alpha Cutout Pipeline"
        AH_ENTRY["__anyhit__ entry"]
        GET_ALPHA_ID["getPartialAlphaTextureId()"]
        SAMPLE_ALPHA["demandLoading::tex2D<float>()"]
        CHECK_RESIDENT["isResident check"]
        ALPHA_TEST["texel == 0.0f test"]
        IGNORE["optixIgnoreIntersection()"]
        DISCARD["discardRay = true"]
    end
    
    AH_ENTRY --> GET_ALPHA_ID
    GET_ALPHA_ID --> SAMPLE_ALPHA
    SAMPLE_ALPHA --> CHECK_RESIDENT
    CHECK_RESIDENT --> |"not resident"| DISCARD
    CHECK_RESIDENT --> |"resident"| ALPHA_TEST
    ALPHA_TEST --> |"transparent"| IGNORE
```

**Sources:** [examples/DemandLoading/DemandPbrtScene/DemandPbrtScene.cu:739-808](), [examples/DemandLoading/DemandPbrtScene/DemandPbrtScene.cu:687-714]()

## Rendering Modes and Shading

The kernel supports multiple rendering modes that determine how surface intersections are processed and shaded. Each mode implements different lighting models and ray tracing techniques.

### Primary Ray Mode

Primary ray mode implements Phong shading with demand-loaded diffuse textures and proper texture filtering:

| Component | Implementation | Location |
|-----------|---------------|----------|
| **Material Setup** | `PhongMaterial` structure with `Kd`, `Ka`, `Ks` components | [DemandPbrtScene.cu:277-292]() |
| **Texture Sampling** | `demandLoading::tex2DGrad<float4>()` with ray cone derivatives | [DemandPbrtScene.cu:284-285]() |
| **Shading** | `phongShade()` function with directional lighting | [DemandPbrtScene.cu:294]() |

### Path Tracing Mode

Path tracing mode implements global illumination using Monte Carlo sampling with cosine-weighted hemisphere sampling:

```mermaid
graph TB
    subgraph "Path Tracing Loop"
        INIT["Initialize sampleColor"]
        SAMPLE_TEX["Sample diffuse texture"]
        RAY_DEPTH["for rayDepth < maxRayDepth"]
        SCATTER["sampleDiffuse() direction"]
        TRACE_SCATTER["optixTrace() secondary ray"]
        ACCUMULATE_LIGHT["Accumulate lighting"]
    end
    
    subgraph "Sampling Functions"
        CONCENTRIC["concentricMapping()"]
        ORTHO_BASIS["makeOrthoBasis()"]
        COSINE_SAMPLE["Cosine-weighted hemisphere"]
    end
    
    INIT --> SAMPLE_TEX
    SAMPLE_TEX --> RAY_DEPTH
    RAY_DEPTH --> SCATTER
    SCATTER --> CONCENTRIC
    SCATTER --> ORTHO_BASIS
    CONCENTRIC --> COSINE_SAMPLE
    COSINE_SAMPLE --> TRACE_SCATTER
    TRACE_SCATTER --> ACCUMULATE_LIGHT
    ACCUMULATE_LIGHT --> RAY_DEPTH
```

**Sources:** [examples/DemandLoading/DemandPbrtScene/DemandPbrtScene.cu:299-369](), [examples/DemandLoading/DemandPbrtScene/DemandPbrtScene.cu:77-115]()

## Demand Loading Integration

The kernels integrate tightly with the demand loading system to handle texture streaming and memory management. Texture access uses specialized functions that track residency and trigger loading requests.

### Texture Access Patterns

| Access Type | Function | Usage | Residency Handling |
|-------------|----------|-------|-------------------|
| **Basic Sampling** | `demandLoading::tex2D<float4>()` | Simple texture lookups without filtering | [DemandPbrtScene.cu:304]() |
| **Gradient Sampling** | `demandLoading::tex2DGrad<float4>()` | Filtered sampling with explicit derivatives | [DemandPbrtScene.cu:284-285]() |
| **Alpha Testing** | `demandLoading::tex2D<float>()` | Single-channel alpha cutout textures | [DemandPbrtScene.cu:745]() |

### Ray Cone Integration

The kernels implement ray cone tracking for proper texture level-of-detail calculation:

```mermaid
graph LR
    subgraph "Ray Cone Pipeline"
        INIT_CONE["initRayConePinholeCamera()"]
        PROPAGATE["propagate() at intersection"]
        CALC_DD["Calculate ddx, ddy derivatives"] 
        TEX_GRAD["tex2DGrad() with derivatives"]
        WORLD_SIZE["worldSpaceTextureSize calculation"]
    end
    
    INIT_CONE --> PROPAGATE
    PROPAGATE --> CALC_DD
    CALC_DD --> TEX_GRAD
    PROPAGATE --> WORLD_SIZE
    WORLD_SIZE --> TEX_GRAD
```

**Sources:** [examples/DemandLoading/DemandPbrtScene/DemandPbrtScene.cu:247-251](), [examples/DemandLoading/DemandPbrtScene/DemandPbrtScene.cu:280-282](), [examples/DemandLoading/DemandPbrtScene/DemandPbrtScene.cu:854-858]()

## Background and Miss Shading

The `__miss__backgroundColor` program handles rays that don't intersect geometry, implementing environment lighting and skybox rendering through infinite light sources.

### Infinite Light Processing

The miss shader supports multiple infinite light sources with optional skybox textures:

```mermaid
graph TB
    subgraph "Miss Shader Flow"
        MISS_ENTRY["__miss__backgroundColor()"]
        CHECK_LIGHTS["numInfiniteLights > 0"]
        SPHERE_COORD["sphericalCoordFromRayDirection()"]
        SAMPLE_SKYBOX["tex2D() skybox texture"]
        COMBINE_LIGHTS["Combine light contributions"]
        SET_BACKGROUND["Set background color"]
    end
    
    MISS_ENTRY --> CHECK_LIGHTS
    CHECK_LIGHTS --> |"has lights"| SPHERE_COORD
    CHECK_LIGHTS --> |"no lights"| SET_BACKGROUND
    SPHERE_COORD --> SAMPLE_SKYBOX
    SAMPLE_SKYBOX --> COMBINE_LIGHTS
    COMBINE_LIGHTS --> SET_BACKGROUND
```

**Sources:** [examples/DemandLoading/DemandPbrtScene/DemandPbrtScene.cu:406-445](), [examples/DemandLoading/DemandPbrtScene/DemandPbrtScene.cu:371-391]()

## Debug and Visualization Infrastructure

The kernels include extensive debug support through the `DebugLocation` system, enabling pixel-specific debugging and visualization of intermediate rendering states.

### Debug Information System

| Debug Type | Structure | Purpose | Location |
|------------|-----------|---------|----------|
| **Triangle Debug** | `TriMeshMaterialDebugInfo` | Material and geometry inspection | [DeviceTriangles.h:66-176]() |
| **Sphere Debug** | `SphereMaterialDebugInfo` | Sphere intersection debugging | [PhongMaterial.cu:61-86]() |
| **Proxy Debug** | `ProxyClosestHitDebugInfo` | Demand geometry visualization | [DemandPbrtScene.cu:510-535]() |
| **Alpha Debug** | `AlphaCutOutDebugInfo` | Alpha cutout texture inspection | [DemandPbrtScene.cu:633-665]() |

The debug system uses a callback pattern where debug structures implement `dump()` and `setColor()` methods, allowing for comprehensive inspection of rendering state at specific pixels.

**Sources:** [examples/DemandLoading/DemandPbrtScene/include/DemandPbrtScene/DeviceTriangles.h:66-182](), [examples/DemandLoading/DemandPbrtScene/DemandPbrtScene.cu:510-673]()

---

