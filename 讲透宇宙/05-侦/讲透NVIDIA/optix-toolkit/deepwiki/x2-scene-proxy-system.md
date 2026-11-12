<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/optix-toolkit · extra page Scene Proxy System · fetched 2026-10-26 -->

# Scene Proxy System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [examples/DemandLoading/DemandPbrtScene/GeometryResolver.cpp](examples/DemandLoading/DemandPbrtScene/GeometryResolver.cpp)
- [examples/DemandLoading/DemandPbrtScene/MaterialResolver.cpp](examples/DemandLoading/DemandPbrtScene/MaterialResolver.cpp)
- [examples/DemandLoading/DemandPbrtScene/ProgramGroups.cpp](examples/DemandLoading/DemandPbrtScene/ProgramGroups.cpp)
- [examples/DemandLoading/DemandPbrtScene/SceneProxy.cpp](examples/DemandLoading/DemandPbrtScene/SceneProxy.cpp)
- [examples/DemandLoading/DemandPbrtScene/include/DemandPbrtScene/Params.h](examples/DemandLoading/DemandPbrtScene/include/DemandPbrtScene/Params.h)
- [examples/DemandLoading/DemandPbrtScene/include/DemandPbrtScene/SceneGeometry.h](examples/DemandLoading/DemandPbrtScene/include/DemandPbrtScene/SceneGeometry.h)
- [examples/DemandLoading/DemandPbrtScene/include/DemandPbrtScene/SceneProxy.h](examples/DemandLoading/DemandPbrtScene/include/DemandPbrtScene/SceneProxy.h)
- [examples/DemandLoading/DemandPbrtScene/include/DemandPbrtScene/SceneSyncState.h](examples/DemandLoading/DemandPbrtScene/include/DemandPbrtScene/SceneSyncState.h)
- [examples/DemandLoading/DemandPbrtScene/tests/GeometryInstancePrinter.h](examples/DemandLoading/DemandPbrtScene/tests/GeometryInstancePrinter.h)
- [examples/DemandLoading/DemandPbrtScene/tests/MockRenderer.h](examples/DemandLoading/DemandPbrtScene/tests/MockRenderer.h)
- [examples/DemandLoading/DemandPbrtScene/tests/ParamsPrinters.h](examples/DemandLoading/DemandPbrtScene/tests/ParamsPrinters.h)
- [examples/DemandLoading/DemandPbrtScene/tests/TestGeometryResolver.cpp](examples/DemandLoading/DemandPbrtScene/tests/TestGeometryResolver.cpp)
- [examples/DemandLoading/DemandPbrtScene/tests/TestMaterialResolver.cpp](examples/DemandLoading/DemandPbrtScene/tests/TestMaterialResolver.cpp)
- [examples/DemandLoading/DemandPbrtScene/tests/TestProgramGroups.cpp](examples/DemandLoading/DemandPbrtScene/tests/TestProgramGroups.cpp)
- [examples/DemandLoading/DemandPbrtScene/tests/TestSceneProxy.cpp](examples/DemandLoading/DemandPbrtScene/tests/TestSceneProxy.cpp)

</details>



## Purpose and Scope

The Scene Proxy System is a hierarchical demand-loading mechanism used in the DemandPbrtScene example to efficiently render large scenes by decomposing them into manageable chunks. This system enables on-demand streaming of geometry and materials, allowing only visible portions of the scene to be realized in GPU memory during ray tracing.

The system operates at multiple levels of granularity, from whole-scene proxies down to individual primitive groups, and coordinates with the OptiX ray tracing pipeline to trigger decomposition and realization based on actual ray hits. For information about the underlying demand loading infrastructure, see [DemandLoading System](#3). For details about rendering and CUDA kernels, see [CUDA Kernels and Rendering](#5.1.2).

## System Architecture Overview

The Scene Proxy System implements a tree-like decomposition strategy where complex scene elements are initially represented as coarse bounding box proxies. When rays intersect these proxies during OptiX traversal, the system progressively decomposes them into finer-grained proxies or realizes them as actual geometry and materials.

```mermaid
graph TD
    Scene["SceneDescriptionPtr"] --> ProxyFactory["ProxyFactoryImpl"]
    ProxyFactory --> WholeScene["WholeSceneProxy"]
    
    WholeScene --> |"decompose()"| InstanceProxies["InstanceProxy[]"]
    WholeScene --> |"decompose()"| ShapeProxies["ShapeProxy[]"]
    
    InstanceProxies --> |"decompose()"| InstanceShapeProxies["InstanceShapeProxy[]"]
    InstanceProxies --> |"decompose()"| InstancePrimitiveProxies["InstancePrimitiveProxy[]"]
    
    InstanceShapeProxies --> |"createGeometry()"| GeometryInstance["GeometryInstance"]
    ShapeProxies --> |"createGeometry()"| GeometryInstance
    InstancePrimitiveProxies --> |"createGeometry()"| GeometryInstance
    
    GeometryInstance --> MaterialResolver["MaterialResolver"]
    MaterialResolver --> RealizedMaterials["Realized Materials"]
```

**Sources:** [examples/DemandLoading/DemandPbrtScene/SceneProxy.cpp:416-427](), [examples/DemandLoading/DemandPbrtScene/SceneProxy.cpp:490-509]()

## Core Abstractions

### SceneProxy Interface

The `SceneProxy` abstract base class defines the contract for all proxy objects in the system:

| Method | Purpose |
|--------|---------|
| `getPageId()` | Returns the demand geometry page ID for OptiX integration |
| `getBounds()` | Provides world-space bounding box for culling |
| `isDecomposable()` | Indicates if proxy can be further decomposed |
| `createGeometry()` | Creates actual OptiX geometry for non-decomposable proxies |
| `decompose()` | Breaks proxy into sub-proxies for hierarchical loading |

```mermaid
classDiagram
    class SceneProxy {
        <<abstract>>
        +getPageId() uint_t
        +getBounds() OptixAabb
        +isDecomposable() bool
        +createGeometry(OptixDeviceContext, CUstream) GeometryInstance
        +decompose(ProxyFactoryPtr) vector~SceneProxyPtr~
    }
    
    class WholeSceneProxy {
        -m_pageId: uint_t
        -m_scene: SceneDescriptionPtr
        +isDecomposable() true
    }
    
    class InstanceProxy {
        -m_instanceIndex: uint_t
        -m_name: string
        +isDecomposable() depends on shapes
    }
    
    class ShapeProxy {
        -m_shapeIndex: uint_t
        +isDecomposable() false
    }
    
    class InstanceShapeProxy {
        -m_instanceIndex: uint_t
        -m_shapeIndex: uint_t
        +isDecomposable() false
    }
    
    SceneProxy <|-- WholeSceneProxy
    SceneProxy <|-- InstanceProxy
    SceneProxy <|-- ShapeProxy
    SceneProxy <|-- InstanceShapeProxy
```

**Sources:** [examples/DemandLoading/DemandPbrtScene/include/DemandPbrtScene/SceneProxy.h:44-63](), [examples/DemandLoading/DemandPbrtScene/SceneProxy.cpp:87-108]()

### ProxyFactory

The `ProxyFactory` creates appropriate proxy types based on scene structure and granularity settings:

```mermaid
graph LR
    ProxyFactory["ProxyFactoryImpl"] --> |"scene()"| WholeSceneProxy
    ProxyFactory --> |"sceneShape()"| ShapeProxy
    ProxyFactory --> |"sceneInstance()"| InstanceProxy
    ProxyFactory --> |"sceneInstanceShape()"| InstanceShapeProxy
    ProxyFactory --> |"sceneInstancePrimitive()"| InstancePrimitiveProxy
    
    Options["Options.proxyGranularity"] --> ProxyFactory
    GeometryLoader --> ProxyFactory
    GeometryCache --> ProxyFactory
```

**Sources:** [examples/DemandLoading/DemandPbrtScene/SceneProxy.cpp:464-488](), [examples/DemandLoading/DemandPbrtScene/SceneProxy.cpp:589-592]()

## Proxy Decomposition Hierarchy

The system supports multiple decomposition strategies based on the `ProxyGranularity` setting:

### Fine Granularity
In fine mode, decomposition proceeds to individual shapes:
- `WholeSceneProxy` → `InstanceProxy[]` + `ShapeProxy[]`  
- `InstanceProxy` → `InstanceShapeProxy[]`

### Coarse Granularity  
In coarse mode, shapes with similar properties are grouped:
- `InstanceProxy` → `InstancePrimitiveProxy[]` (grouped by `GeometryPrimitive` and `MaterialFlags`)

```mermaid
flowchart TD
    WS["WholeSceneProxy"] --> |"Options.proxyGranularity"| Choice{{"Granularity?"}}
    
    Choice --> |"FINE"| FineDecomp["Fine Decomposition"]
    Choice --> |"COARSE"| CoarseDecomp["Coarse Decomposition"]
    
    FineDecomp --> IP1["InstanceProxy"] 
    FineDecomp --> SP1["ShapeProxy"]
    
    IP1 --> |"per shape"| ISP["InstanceShapeProxy[]"]
    
    CoarseDecomp --> IP2["InstanceProxy"]
    IP2 --> |"per primitive+material type"| IPP["InstancePrimitiveProxy[]"]
    
    ISP --> |"createGeometry()"| GI1["GeometryInstance"]
    SP1 --> |"createGeometry()"| GI2["GeometryInstance"] 
    IPP --> |"createGeometry()"| GI3["GeometryInstance"]
```

**Sources:** [examples/DemandLoading/DemandPbrtScene/SceneProxy.cpp:309-330](), [examples/DemandLoading/DemandPbrtScene/SceneProxy.cpp:382-409]()

## Geometry and Material Resolution

### GeometryInstance Structure

When a proxy is realized, it produces a `GeometryInstance` containing all data needed for OptiX:

```mermaid
graph LR
    GI["GeometryInstance"] --> AB["accelBuffer: CUdeviceptr"]
    GI --> Prim["primitive: GeometryPrimitive"]
    GI --> OI["instance: OptixInstance"]
    GI --> MG["groups: MaterialGroup[]"]
    GI --> DN["devNormals: TriangleNormals*"]
    GI --> DU["devUVs: TriangleUVs*"]
    
    MG --> PM["material: PhongMaterial"]
    MG --> DF["diffuseMapFileName: string"]
    MG --> AF["alphaMapFileName: string"]
    MG --> PIE["primitiveIndexEnd: uint_t"]
```

**Sources:** [examples/DemandLoading/DemandPbrtScene/include/DemandPbrtScene/SceneProxy.h:34-42](), [examples/DemandLoading/DemandPbrtScene/include/DemandPbrtScene/SceneProxy.h:26-32]()

### Material Resolution Pipeline

Materials follow a two-phase resolution process coordinated by the `MaterialResolver`:

```mermaid
sequenceDiagram
    participant GR as GeometryResolver
    participant MR as MaterialResolver
    participant DTC as DemandTextureCache
    participant ML as MaterialLoader
    
    GR->>MR: resolveMaterialForGeometry()
    
    alt New Material
        MR->>ML: add() → proxyMaterialId
        MR->>GR: return false (no immediate update)
    else Existing Material  
        MR->>GR: return true (requires update)
    end
    
    Note over ML: Ray hits proxy material
    ML->>MR: requestedMaterialIds()
    
    alt Alpha Map Required
        MR->>DTC: createAlphaTextureFromFile()
        MR->>GR: return PARTIAL resolution
    end
    
    alt Full Material
        MR->>DTC: createDiffuseTextureFromFile() 
        MR->>ML: remove(proxyMaterialId)
        MR->>GR: return FULL resolution
    end
```

**Sources:** [examples/DemandLoading/DemandPbrtScene/MaterialResolver.cpp:380-423](), [examples/DemandLoading/DemandPbrtScene/MaterialResolver.cpp:239-285]()

## Integration with Demand Loading

The Scene Proxy System integrates tightly with the OptiX demand loading infrastructure:

### Page ID Management
- Each proxy receives a unique page ID from `GeometryLoader::add()`
- Page IDs map proxy bounding boxes to demand loading requests
- When rays hit proxies, the page ID triggers decomposition

### Synchronization Flow
The `SceneSyncState` coordinates updates between CPU proxy management and GPU rendering:

```mermaid
graph TD
    PR["Proxy Resolution"] --> SS["SceneSyncState"]
    SS --> TLI["topLevelInstances: SyncVector"]
    SS --> RM["realizedMaterials: SyncVector"] 
    SS --> RN["realizedNormals: SyncVector"]
    SS --> RU["realizedUVs: SyncVector"]
    SS --> MI["materialIndices: SyncVector"]
    SS --> PM["primitiveMaterials: SyncVector"]
    
    TLI --> |"copyToDeviceAsync()"| GPU["GPU Memory"]
    RM --> |"copyToDeviceAsync()"| GPU
    RN --> |"copyToDeviceAsync()"| GPU
    RU --> |"copyToDeviceAsync()"| GPU
    MI --> |"copyToDeviceAsync()"| GPU
    PM --> |"copyToDeviceAsync()"| GPU
```

**Sources:** [examples/DemandLoading/DemandPbrtScene/include/DemandPbrtScene/SceneSyncState.h:17-33](), [examples/DemandLoading/DemandPbrtScene/GeometryResolver.cpp:220-234]()

## SBT Offset Management

The system manages Shader Binding Table (SBT) offsets to ensure correct hit group selection:

| Proxy Type | SBT Offset | Purpose |
|------------|------------|---------|
| Geometry Proxy | `HitGroupIndex::PROXY_GEOMETRY` | Triggers decomposition |
| Material Proxy Triangle | `HitGroupIndex::PROXY_MATERIAL_TRIANGLE` | Triggers material resolution |
| Material Proxy Triangle Alpha | `HitGroupIndex::PROXY_MATERIAL_TRIANGLE_ALPHA` | Alpha cutout support |
| Realized Material | Dynamic offset from `ProgramGroups` | Actual shading |

**Sources:** [examples/DemandLoading/DemandPbrtScene/include/DemandPbrtScene/Params.h:49-63](), [examples/DemandLoading/DemandPbrtScene/SceneProxy.cpp:73-85]()

---

