<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/renderformer · page 5 Scene Definition · fetched 2026-10-26 -->

# Scene Definition

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [examples/cbox.json](examples/cbox.json)

</details>



This document covers RenderFormer's scene definition system, which uses a JSON-based format to describe 3D scenes including geometry, materials, lighting, and camera configurations. The scene definition serves as the primary input to the RenderFormer neural rendering pipeline and is converted to HDF5 format for processing.

For information about the scene processing pipeline that converts these definitions, see [Scene Processing](#2.2). For details on the underlying data formats used during rendering, see [Data Formats](#2.3).

## Scene Definition Overview

RenderFormer uses a hierarchical JSON-based scene description format that defines all aspects of a 3D scene. The system follows a structured approach where scenes are composed of objects, materials, cameras, and transformations that are processed into a format suitable for neural rendering.

```mermaid
graph TD
    subgraph "Scene Definition Components"
        A["JSON Scene File"]
        B["Scene Metadata"]
        C["Objects Dictionary"]
        D["Material Properties"]
        E["Transform Data"]
        F["Camera Array"]
    end
    
    subgraph "Processing Pipeline"
        G["convert_scene.py"]
        H["HDF5 Scene File"]
        I["Triangle Data"]
        J["Texture Patches"]
        K["Camera Matrices"]
    end
    
    A --> B
    A --> C
    A --> F
    C --> D
    C --> E
    
    A --> G
    G --> H
    H --> I
    H --> J
    H --> K
    
    style A fill:#e1f5fe
    style H fill:#f3e5f5
```

**Scene Definition to Processing Flow**

Sources: [README.md:230-288](), [examples/cbox.json:1-320]()

## JSON Scene Structure

The scene definition follows a standardized JSON schema with four primary components organized in a hierarchical structure.

| Component | Purpose | Required |
|-----------|---------|----------|
| `scene_name` | Descriptive identifier for the scene | Yes |
| `version` | Scene format version (currently "1.0") | Yes |
| `objects` | Dictionary of scene objects and lighting | Yes |
| `cameras` | Array of camera configurations | Yes |

```mermaid
graph LR
    subgraph "JSON Scene Schema"
        A["scene_name"]
        B["version"]
        C["objects"]
        D["cameras"]
    end
    
    subgraph "Objects Structure"
        E["Object ID"]
        F["mesh_path"]
        G["material"]
        H["transform"]
        I["remesh"]
    end
    
    subgraph "Camera Structure"
        J["position"]
        K["look_at"]
        L["up"]
        M["fov"]
    end
    
    C --> E
    E --> F
    E --> G
    E --> H
    E --> I
    
    D --> J
    D --> K
    D --> L
    D --> M
```

**JSON Scene Schema Structure**

Sources: [README.md:234-240](), [examples/cbox.json:1-10]()

## Object and Material System

Each object in the scene requires specific configuration for geometry, materials, and spatial positioning. The material system supports physically-based rendering properties with constraints on energy conservation.

### Object Configuration

```mermaid
graph TD
    subgraph "Object Definition"
        A["Object ID Key"]
        B["mesh_path"]
        C["material"]
        D["transform"]
        E["remesh"]
    end
    
    subgraph "Material Properties"
        F["diffuse RGB"]
        G["specular RGB"]
        H["roughness"]
        I["emissive RGB"]
        J["smooth_shading"]
        K["rand_tri_diffuse_seed"]
        L["random_diffuse_max"]
        M["random_diffuse_type"]
    end
    
    subgraph "Transform Properties"
        N["translation XYZ"]
        O["rotation XYZ"]
        P["scale XYZ"]
        Q["normalize"]
    end
    
    A --> B
    A --> C
    A --> D
    A --> E
    
    C --> F
    C --> G
    C --> H
    C --> I
    C --> J
    C --> K
    C --> L
    C --> M
    
    D --> N
    D --> O
    D --> P
    D --> Q
```

**Object and Material Configuration Structure**

### Material Property Constraints

The material system enforces specific constraints for physical plausibility:

| Property | Range | Constraint |
|----------|-------|------------|
| `diffuse` | [0.0, 1.0] per channel | diffuse + specular ≤ 1.0 |
| `specular` | [0.0, 1.0] per channel | Currently white only |
| `roughness` | [0.01, 1.0] | Surface microsurface roughness |
| `emissive` | [0.0, ∞] per channel | Light source only, white only |
| `smooth_shading` | boolean | Vertex normal interpolation |

Sources: [README.md:241-262](), [examples/cbox.json:25-46]()

## Camera Configuration System

Camera configuration defines the viewpoint and projection parameters for rendering. The system uses a standard camera model with position, orientation, and field of view parameters.

```mermaid
graph LR
    subgraph "Camera Parameters"
        A["position"]
        B["look_at"]
        C["up"]
        D["fov"]
    end
    
    subgraph "Coordinate System"
        E["-Z = view direction"]
        F["+Y = up"]
        G["+X = right"]
        H["Blender Compatible"]
    end
    
    subgraph "Matrix Generation"
        I["c2w Matrix"]
        J["4x4 Transform"]
        K["Camera-to-World"]
    end
    
    A --> I
    B --> I
    C --> I
    D --> J
    
    E --> H
    F --> H
    G --> H
    H --> I
    
    I --> J
    J --> K
```

**Camera Configuration and Coordinate System**

### Camera Parameter Specification

| Parameter | Type | Description |
|-----------|------|-------------|
| `position` | [x, y, z] | Camera world position |
| `look_at` | [x, y, z] | Target point for camera orientation |
| `up` | [x, y, z] | Up vector for camera orientation |
| `fov` | float | Field of view in degrees |

The system uses Blender's coordinate convention where -Z is the view direction, +Y is up, and +X is right.

Sources: [README.md:264-271](), [README.md:286-287](), [examples/cbox.json:300-319]()

## Transform and Coordinate System

The transform system handles object positioning, orientation, and scaling within the scene coordinate space. Objects can be transformed through translation, rotation, scaling, and normalization operations.

```mermaid
graph TD
    subgraph "Transform Operations"
        A["translation"]
        B["rotation"]
        C["scale"]
        D["normalize"]
    end
    
    subgraph "Coordinate Constraints"
        E["Scene Bounding Box"]
        F["[-0.5, 0.5] XYZ"]
        G["Unit Sphere Normalization"]
    end
    
    subgraph "Object Processing"
        H["OBJ Mesh Loading"]
        I["Vertex Transformation"]
        J["Triangle Generation"]
        K["Normal Computation"]
    end
    
    A --> I
    B --> I
    C --> I
    D --> G
    
    E --> F
    G --> E
    
    H --> I
    I --> J
    J --> K
```

**Transform System and Coordinate Processing**

### Transform Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `translation` | [x, y, z] | Object position offset |
| `rotation` | [x, y, z] | Rotation in degrees per axis |
| `scale` | [x, y, z] | Scale factors per axis |
| `normalize` | boolean | Normalize to unit sphere |

Sources: [README.md:255-261](), [examples/cbox.json:175-192]()

## Scene Processing Pipeline

The scene definition undergoes conversion from JSON format to HDF5 format through the `convert_scene.py` processor. This conversion handles mesh loading, material processing, and data preparation for neural rendering.

```mermaid
graph LR
    subgraph "Input Processing"
        A["JSON Scene File"]
        B["OBJ Mesh Files"]
        C["Material Properties"]
    end
    
    subgraph "convert_scene.py"
        D["Scene Parser"]
        E["Mesh Loader"]
        F["Triangle Processor"]
        G["Texture Generator"]
        H["Camera Matrix Builder"]
    end
    
    subgraph "HDF5 Output"
        I["triangles N×3×3"]
        J["texture N×13×32×32"]
        K["vn N×3×3"]
        L["c2w N×4×4"]
        M["fov N"]
    end
    
    A --> D
    B --> E
    C --> G
    
    D --> E
    E --> F
    F --> I
    G --> J
    E --> K
    D --> H
    H --> L
    H --> M
```

**Scene Processing Pipeline Flow**

### HDF5 Data Structure

The conversion process generates HDF5 files with specific data arrays:

| Field | Shape | Description |
|-------|-------|-------------|
| `triangles` | [N, 3, 3] | Triangle vertex coordinates |
| `texture` | [N, 13, 32, 32] | Material texture patches |
| `vn` | [N, 3, 3] | Vertex normal vectors |
| `c2w` | [N, 4, 4] | Camera-to-world matrices |
| `fov` | [N] | Field of view values |

Sources: [README.md:276-285](), [README.md:109-115]()

## Scene Configuration Constraints

RenderFormer has specific constraints based on its training data distribution. These constraints ensure optimal performance within the model's learned domain.

### Training Data Constraints

| Component | Constraint | Range |
|-----------|------------|-------|
| Camera Distance | Scene center distance | [1.5, 2.0] units |
| Field of View | Camera FOV | [30, 60] degrees |
| Scene Bounds | Bounding box | [-0.5, 0.5] XYZ |
| Light Sources | Triangle count | Up to 8 triangles |
| Light Scale | Light source scale | [2.0, 2.5] units |
| Light Distance | Distance to center | [2.1, 2.7] units |
| Light Emission | Summed emission | [2500, 5000] units |
| Total Triangles | Scene triangle count | Up to 4096 (8192 during inference) |

### Mesh Quality Requirements

- Water-tight meshes preferred
- Uniform triangle sizes recommended
- QSlim simplification suggested
- Remeshing tools available via [scene_processor/remesh.py]()

Sources: [README.md:304-313](), [README.md:290-298]()

## Integration with Rendering Pipeline

The scene definition system integrates with the broader RenderFormer architecture through the HDF5 conversion process and dataset loading mechanisms.

```mermaid
graph TB
    subgraph "Scene Definition Layer"
        A["JSON Scene Files"]
        B["convert_scene.py"]
        C["HDF5 Scene Files"]
    end
    
    subgraph "Data Loading Layer"
        D["TriangleRenderH5Dataset"]
        E["DataLoader"]
        F["Batch Processing"]
    end
    
    subgraph "Neural Rendering Layer"
        G["RenderFormerRenderingPipeline"]
        H["View-Independent Stage"]
        I["View-Dependent Stage"]
    end
    
    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
    F --> G
    G --> H
    H --> I
```

**Scene Definition Integration Architecture**

The scene definition system serves as the foundational input layer that feeds into the neural rendering pipeline through standardized data formats and processing workflows.

Sources: [README.md:149-189](), [README.md:192-227]()

---

