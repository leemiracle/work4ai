<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/cuBQL · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [cuBQL/bvh.h](cuBQL/bvh.h)

</details>



## Purpose and Scope

This page provides a high-level introduction to cuBQL, a CUDA/C++ library for GPU-accelerated construction and traversal of Bounding Volume Hierarchies (BVHs). The overview covers the library's purpose, architecture, core data structures, and basic usage patterns. For detailed installation and build instructions, see [Getting Started](#2). For in-depth architectural details, see [Architecture](#3).

**Sources:** [README.md:1-12]()

## What is cuBQL?

cuBQL (pronounced "cubicle") is a header-only CUDA/C++ library designed to enable efficient GPU-accelerated spatial queries over geometric primitives. The library provides tools for both constructing BVH data structures on the GPU and performing various spatial queries against them.

The library is inspired by the Standard Template Library (STL) and CUB, using templates and lambda functions to support different primitive types, coordinate types (float, double, int), dimensionalities (2D, 3D, 4D, N-D), and query patterns. This design enables a single codebase to handle diverse use cases: from `float3` ray tracing to `int2` spatial indexing.

**Key Design Goals:**
- **Robustness**: All builders work for all input types and handle numerically challenging data
- **Generality**: Template-based design supports arbitrary scalar types and dimensionalities
- **Ease of Use**: Simple API with sensible defaults and flexible customization
- **Performance**: GPU-accelerated construction (~13ms for 10M points) and traversal

**Sources:** [README.md:8-26]()

## Core Architecture: Four-Layer System

cuBQL organizes functionality into four distinct layers, each building on the layer below:

```mermaid
graph TB
    subgraph Layer4["Layer 4: Geometric Queries"]
        L4A["Closest Point Queries"]
        L4B["k-NN Queries"]
        L4C["Ray-Triangle Intersection"]
        L4D["User-Defined Queries"]
    end
    
    subgraph Layer3["Layer 3: BVH Traversal Templates"]
        L3A["fixedRadiusQuery"]
        L3B["shrinkingRadiusQuery"]
        L3C["fixedRayQuery"]
        L3D["shrinkingRayQuery"]
        L3E["Two-Level TLAS/BLAS"]
    end
    
    subgraph Layer2["Layer 2: BVH Builders"]
        L2A["cuBQL::gpuBuilder"]
        L2B["radixBuilder"]
        L2C["sahBuilder"]
        L2D["elhBuilder"]
        L2E["wideGpuBuilder"]
    end
    
    subgraph Layer1["Layer 1: Core Data Structures"]
        L1A["BinaryBVH<T,D>"]
        L1B["WideBVH<T,D,N>"]
        L1C["BuildConfig"]
    end
    
    subgraph Layer0["Layer 0: Mathematical Foundation"]
        L0A["vec_t<T,D>"]
        L0B["box_t<T,D>"]
        L0C["ray_t<T>"]
        L0D["triangle_t<T>"]
    end
    
    L4A --> L3B
    L4B --> L3B
    L4C --> L3D
    L4D --> L3A
    L4D --> L3B
    
    L3A --> L1A
    L3B --> L1A
    L3C --> L1A
    L3D --> L1A
    L3E --> L1A
    L3E --> L1B
    
    L2A --> L1A
    L2B --> L1A
    L2C --> L1A
    L2D --> L1A
    L2E --> L1B
    
    L1A --> L0B
    L1B --> L0B
    
    L3A --> L0A
    L3A --> L0B
    L3C --> L0C
```

**Layer 0 (Mathematical Foundation)**: Template-based geometric primitives that work on both CPU and GPU. All types are parameterized by scalar type `T` and dimensionality `D`. See [Mathematical Foundation](#4) for details.

**Layer 1 (Core Data Structures)**: BVH storage formats defined in [cuBQL/bvh.h](). `BinaryBVH<T,D>` is the primary structure; `WideBVH<T,D,N>` provides N-ary trees for traversal optimization. See [Core Data Structures](#5).

**Layer 2 (BVH Builders)**: GPU-accelerated construction algorithms with different speed/quality tradeoffs. The `cuBQL::gpuBuilder` function dispatches to specialized builders based on `BuildConfig` settings. See [BVH Construction](#6).

**Layer 3 (Traversal Templates)**: Generic query patterns customizable via lambda callbacks. Users can implement custom queries without modifying core BVH code. See [BVH Traversal](#7).

**Layer 4 (Geometric Queries)**: Example implementations that demonstrate how to use the traversal templates. These serve as both usable queries and reference implementations. See [Geometric Queries](#8).

**Sources:** [README.md:30-60](), [cuBQL/bvh.h:1-161]()

## Core Data Structures

### BinaryBVH Structure

The primary BVH type is `BinaryBVH<T,D>`, a binary tree where each node contains a bounding box and administrative data:

```mermaid
graph LR
    subgraph BinaryBVH["BinaryBVH&lt;T,D&gt; Structure"]
        direction TB
        Nodes["nodes array<br/>Node structures"]
        PrimIDs["primIDs array<br/>uint32_t indices"]
        
        subgraph NodeStruct["Node Structure"]
            Bounds["bounds: box_t&lt;T,D&gt;"]
            Admin["admin.offset: uint64<br/>admin.count: uint64"]
        end
    end
    
    subgraph Interpretation["Node Type Interpretation"]
        Inner["Inner Node:<br/>count == 0<br/>offset → nodes array<br/>children at offset+0, offset+1"]
        Leaf["Leaf Node:<br/>count > 0<br/>offset → primIDs array<br/>primitives at offset..offset+count-1"]
    end
    
    Nodes --> NodeStruct
    NodeStruct --> Inner
    NodeStruct --> Leaf
    Inner --> Nodes
    Leaf --> PrimIDs
```

**Key characteristics:**
- Node 0 is always the root
- Node 1 is unused (ensures child pairs start at even indices)
- Inner nodes: `count=0`, `offset` indexes into `nodes[]` array
- Leaf nodes: `count>0`, `offset` indexes into `primIDs[]` array
- Maximum leaf size: `(1<<16)-1` = 65535 primitives

The structure definition from [cuBQL/bvh.h:58-100]():

| Field | Type | Purpose |
|-------|------|---------|
| `nodes` | `Node*` | Array of BVH nodes (device or host memory) |
| `numNodes` | `uint32_t` | Total number of nodes in the tree |
| `primIDs` | `uint32_t*` | Array of primitive indices |
| `numPrims` | `uint32_t` | Total number of primitives indexed |

**Sources:** [cuBQL/bvh.h:53-100](), [README.md:64-91]()

### WideBVH Structure

`WideBVH<T,D,N>` provides N-ary trees with fixed branching factor. Each "node" is actually N child slots merged together:

```mermaid
graph TB
    subgraph WideBVH["WideBVH&lt;T,D,N&gt; Multi-Node"]
        direction LR
        Child0["Child[0]<br/>bounds: box_t&lt;T,D&gt;<br/>valid: 1 bit<br/>offset: 45 bits<br/>count: 16 bits"]
        Child1["Child[1]<br/>..."]
        Child2["Child[2]<br/>..."]
        ChildN["Child[N-1]<br/>..."]
        
        Child0 --> Child1
        Child1 --> Child2
        Child2 --> ChildN
    end
    
    Valid["valid bit:<br/>0 = unused child<br/>1 = valid child"]
    Offset["offset field:<br/>→ nodes array (inner)<br/>→ primIDs array (leaf)"]
    Count["count field:<br/>0 = inner child<br/>&gt;0 = leaf child"]
    
    Child0 --> Valid
    Child0 --> Offset
    Child0 --> Count
```

Wide BVHs are typically created by collapsing binary BVHs, improving traversal efficiency through better cache utilization and SIMD opportunities.

**Sources:** [cuBQL/bvh.h:102-134]()

## Template Type System

cuBQL uses three primary template parameters to achieve flexibility:

```mermaid
graph TB
    subgraph Templates["Template Parameters"]
        T["T: Scalar Type<br/>float, double, int32_t, int64_t, ..."]
        D["D: Dimensionality<br/>2, 3, 4, N"]
        N["N: BVH Width<br/>4, 8, 16 (for WideBVH only)"]
    end
    
    subgraph GenericTypes["Generic Type Templates"]
        VecT["vec_t&lt;T,D&gt;"]
        BoxT["box_t&lt;T,D&gt;"]
        RayT["ray_t&lt;T&gt;"]
        BinaryT["BinaryBVH&lt;T,D&gt;"]
        WideT["WideBVH&lt;T,D,N&gt;"]
    end
    
    subgraph Aliases["Common Type Aliases"]
        Vec3f["vec3f = vec_t&lt;float,3&gt;"]
        Box3f["box3f = box_t&lt;float,3&gt;"]
        Bvh3f["bvh3f = BinaryBVH&lt;float,3&gt;"]
        Vec3d["vec3d = vec_t&lt;double,3&gt;"]
        Bvh3d["bvh3d = BinaryBVH&lt;double,3&gt;"]
    end
    
    T --> VecT
    D --> VecT
    T --> BoxT
    D --> BoxT
    T --> RayT
    T --> BinaryT
    D --> BinaryT
    T --> WideT
    D --> WideT
    N --> WideT
    
    VecT --> Vec3f
    VecT --> Vec3d
    BoxT --> Box3f
    BinaryT --> Bvh3f
    BinaryT --> Bvh3d
    
    VecT --> BoxT
    BoxT --> BinaryT
    BoxT --> WideT
```

**Type Aliases:** The library provides common aliases to reduce verbosity. For example, `bvh3f` is shorthand for `BinaryBVH<float,3>`, and `vec3f` is shorthand for `vec_t<float,3>`.

**CUDA Integration:** When `CUBQL_SUPPORT_CUDA_VECTOR_TYPES=1`, automatic conversions enable interoperation with CUDA built-in types like `float3`, `int4`, and `dim3`.

**Sources:** [cuBQL/bvh.h:58-149](), [README.md:99-104]()

## Build and Query Workflow

The typical cuBQL usage follows a two-phase pattern: construction followed by queries.

### Construction Phase

```mermaid
flowchart LR
    Input["Input: Primitive<br/>Bounding Boxes<br/>box_t&lt;T,D&gt;[]"]
    Config["BuildConfig:<br/>buildMethod<br/>makeLeafThreshold<br/>maxAllowedLeafSize"]
    
    Builder["cuBQL::gpuBuilder()<br/>function call"]
    
    Dispatch{{"Algorithm<br/>Dispatch"}}
    
    Radix["radixBuilder:<br/>morton codes<br/>spatial median"]
    SAH["sahBuilder:<br/>binning<br/>SAH cost metric"]
    ELH["elhBuilder:<br/>edge-length<br/>heuristic"]
    
    Output["Output:<br/>BinaryBVH&lt;T,D&gt;<br/>nodes + primIDs"]
    
    Input --> Builder
    Config --> Builder
    Builder --> Dispatch
    
    Dispatch -->|"SPATIAL_MEDIAN"| Radix
    Dispatch -->|"SAH"| SAH
    Dispatch -->|"ELH"| ELH
    
    Radix --> Output
    SAH --> Output
    ELH --> Output
```

Example build invocation from [README.md:135-145]():

```cpp
box3f *d_boxes  = 0;
int    numBoxes = 0;
// User code generates boxes on GPU
userCodeForGeneratingPrims(&d_boxes, &numBoxes);

cuBQL::BinaryBVH<float,3> bvh;
cuBQL::BuildConfig buildParams;
cuBQL::gpuBuilder(bvh, d_boxes, numBoxes, buildParams);
```

The builder:
- Accepts bounding boxes in device or managed memory
- Does not modify input boxes
- Handles invalid boxes (where `lower.x > upper.x`) by excluding them
- Handles zero-volume boxes (where `lower == upper`) as valid
- Populates `bvh.nodes[]` and `bvh.primIDs[]` arrays

**Sources:** [README.md:106-169](), [cuBQL/bvh.h:18-51]()

### Query Phase

```mermaid
flowchart TB
    BVH["BVH Structure<br/>from construction"]
    Query["Query Parameters:<br/>point, radius, ray, etc."]
    Lambda["User Lambda:<br/>custom per-primitive<br/>processing logic"]
    
    Template["Traversal Template:<br/>fixedRadiusQuery<br/>shrinkingRadiusQuery<br/>fixedRayQuery<br/>shrinkingRayQuery"]
    
    Traverse["Stack-based<br/>BVH Descent"]
    
    Test{{"Intersection<br/>Test"}}
    
    Inner["Inner Node:<br/>push children<br/>to stack"]
    Leaf["Leaf Node:<br/>invoke lambda<br/>on primitives"]
    
    Decision{{"Lambda<br/>Return Value"}}
    
    Continue["Continue:<br/>new search radius<br/>or tMax"]
    Terminate["Terminate:<br/>early exit"]
    
    Results["Results in<br/>Lambda State"]
    
    BVH --> Template
    Query --> Template
    Lambda --> Template
    
    Template --> Traverse
    Traverse --> Test
    
    Test -->|"Inner"| Inner
    Test -->|"Leaf"| Leaf
    
    Inner --> Traverse
    Leaf --> Decision
    
    Decision --> Continue
    Decision --> Terminate
    
    Continue --> Traverse
    Terminate --> Results
```

Example query from [README.md:254-266]():

```cpp
void findClosestPoint(...) {
   float closestDist = INFINITY;
   int   closestID   = -1;
   auto myQueryLambda = [&closestDist,&closestID,...](int primID) -> float {
      float dist = distance(queryPoint, myPrims[primID]);
      if (dist < closestDist) {
         closestDist = dist;
         closestID = primID;
      }
      return closestDist;  // New search radius
   };
   cuBQL::shrinkingRadiusQuery::forEachPrim(myQueryLambda, queryPoint, myBVH, ...);
}
```

The lambda-based design enables:
- **Custom per-primitive processing**: Lambda implements query-specific logic
- **Dynamic search space reduction**: Lambda returns new radius/tMax for shrinking queries
- **Early termination**: Lambda can signal traversal to stop
- **Flexible result accumulation**: Results stored in lambda-captured variables

**Sources:** [README.md:193-269]()

## Key File Organization

```mermaid
graph TB
    subgraph Include["cuBQL/ (Include Directory)"]
        BVH["bvh.h:<br/>BinaryBVH, WideBVH,<br/>BuildConfig definitions"]
        
        subgraph Math["math/"]
            Vec["vec.h: vec_t&lt;T,D&gt;"]
            Box["box.h: box_t&lt;T,D&gt;"]
            Ray["ray.h: ray_t&lt;T&gt;"]
            Common["common.h: macros,<br/>__cubql_both"]
        end
        
        subgraph Builder["builder/"]
            CudaBuilder["cuda.h:<br/>GPU builders"]
            CpuBuilder["cpu.h:<br/>Host builders"]
            BuilderImpl["cuda/gpu_builder.h:<br/>Implementation"]
        end
        
        subgraph Traversal["traversal/"]
            RadiusQ["radiusQueries.h:<br/>fixedRadiusQuery,<br/>shrinkingRadiusQuery"]
            RayQ["rayQueries.h:<br/>fixedRayQuery,<br/>shrinkingRayQuery"]
        end
        
        subgraph Queries["queries/ (Optional)"]
            Closest["closestPoint.h"]
            KNN["kNN.h"]
            RayTri["rayTriangle.h"]
        end
    end
    
    BVH --> Math
    BVH --> Builder
    Builder --> BuilderImpl
    Traversal --> BVH
    Queries --> Traversal
```

**Core Library (`cuBQL/`)**: Everything needed for BVH construction and traversal

**Math Foundation (`cuBQL/math/`)**: Template-based geometric primitives with CPU/GPU support

**Builders (`cuBQL/builder/`)**: Construction algorithms; can be used header-only or as pre-built targets

**Traversal (`cuBQL/traversal/`)**: Generic query patterns via lambda callbacks

**Queries (`cuBQL/queries/`)**: Example implementations demonstrating traversal template usage

**Sources:** [README.md:282-296]()

## Build Configuration Options

The `BuildConfig` structure controls builder behavior:

| Field | Type | Default | Purpose |
|-------|------|---------|---------|
| `buildMethod` | `BuildMethod` enum | `SPATIAL_MEDIAN` | Algorithm selection: `SPATIAL_MEDIAN`, `SAH`, or `ELH` |
| `makeLeafThreshold` | `int` | `0` | Threshold below which to create leaves (0 = let builder decide) |
| `maxAllowedLeafSize` | `int` | `1<<15` (32768) | Maximum primitives per leaf |

**Build Methods:**
- **SPATIAL_MEDIAN** (default): Fast construction using morton codes and spatial median splits
- **SAH**: Higher quality using Surface Area Heuristic, slower build but better query performance
- **ELH**: Edge-Length Heuristic, experimental balanced approach

Methods can be enabled via:
```cpp
BuildConfig config;
config.enableSAH();  // Use SAH builder
config.enableELH();  // Use ELH builder
```

**Sources:** [cuBQL/bvh.h:18-51]()

## Memory Management

cuBQL supports flexible memory allocation strategies:

**Default**: Device memory allocated via `cudaMalloc`/`cudaFree`

**Managed Memory**: Use `cuBQL::ManagedMemoryResource` for automatic CPU/GPU migration

**Async Device Memory**: Use `cuBQL::AsyncDeviceMemoryResource` for stream-ordered allocations

**Custom Resources**: Implement `cuBQL::GpuMemoryResource` interface for custom allocators

Memory resources can be passed to builders:
```cpp
cuBQL::ManagedMemoryResource mr;
cuBQL::gpuBuilder(bvh, d_boxes, numBoxes, buildParams, 0, mr);
```

See [Memory Management](#9.1) for detailed documentation.

**Sources:** [README.md:176-179]()

## Header-Only vs. Pre-Built Libraries

cuBQL supports two usage modes:

### Header-Only Mode

Define `CUBQL_GPU_BUILDER_IMPLEMENTATION=1` in exactly one translation unit to include implementation:

```cpp
#define CUBQL_GPU_BUILDER_IMPLEMENTATION 1
#include <cuBQL/bvh.h>
```

This allows compilation with custom flags and architectures.

### Pre-Built Library Mode

Link against type-specific targets in CMake:

```cmake
target_link_libraries(userExec cuBQL_cuda_float3)
```

Available targets include `cuBQL_cuda_float3`, `cuBQL_cuda_double3`, `cuBQL_host_int4`, etc.

See [Getting Started](#2) for build system integration details and [Template Instantiation](#9.3) for advanced customization.

**Sources:** [README.md:181-191](), [README.md:308-368]()

## Next Steps

- **Installation and Build**: See [Getting Started](#2) for CMake integration and build instructions
- **Architecture Details**: See [Architecture](#3) for in-depth layer descriptions
- **Mathematical Types**: See [Mathematical Foundation](#4) for `vec_t`, `box_t`, and related types
- **BVH Construction**: See [BVH Construction](#6) for builder algorithms and implementation details
- **BVH Traversal**: See [BVH Traversal](#7) for traversal templates and query patterns
- **Example Queries**: See [Geometric Queries](#8) for reference implementations

**Sources:** [README.md:1-369]()

---

