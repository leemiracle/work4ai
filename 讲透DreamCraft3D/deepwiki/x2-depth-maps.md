<!-- source: DeepWiki mcp.deepwiki.com · repo deepseek-ai/DreamCraft3D · extra page Depth Maps · fetched 2026-10-30 -->

# Depth Maps

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [load/images/a DSLR photo of a puffin standing on a rock_depth.png](load/images/a DSLR photo of a puffin standing on a rock_depth.png)
- [load/images/a figurine of a frog holding a birthday cake_depth.png](load/images/a figurine of a frog holding a birthday cake_depth.png)
- [load/images/a kingfisher sitting on top of a piece of wood_depth.png](load/images/a kingfisher sitting on top of a piece of wood_depth.png)

</details>



This document details the role of depth maps in the DreamCraft3D pipeline. Depth maps provide essential distance information that helps the system generate accurate 3D geometry from a single 2D reference image. For information about normal maps, which work alongside depth maps to provide surface orientation data, see [Normal Maps](#3.2.2).

## Overview

Depth maps are grayscale images where pixel intensity represents the distance from the camera viewpoint to the object. In DreamCraft3D, these maps are a critical preprocessing step that enables initial coarse geometry generation. Darker pixels indicate objects closer to the camera, while lighter pixels represent objects farther away.

```mermaid
flowchart LR
    A["Input Reference Image"] --> B["Preprocessing Pipeline"]
    B --> C["Depth Map Generation"]
    C --> D["Depth Map (.png)"]
    D --> E["Stage 1: Coarse Geometry"]
    
    subgraph "Depth Information"
        D --- F["Dark Pixels: Close to Camera"]
        D --- G["Light Pixels: Far from Camera"]
        D --- H["_depth.png Suffix"]
    end
```

Sources: load/images/a DSLR photo of a puffin standing on a rock_depth.png

## Generation Process

DreamCraft3D uses the Omnidata model for depth estimation from a single reference image. The preprocessing stage generates depth maps automatically before the main reconstruction pipeline begins.

```mermaid
flowchart TB
    A["Input 2D Image"] --> B["preprocess_image.py"]
    B --> C["Omnidata Depth Estimation"]
    C --> D["Raw Depth Prediction"]
    D --> E["Post-processing"]
    E --> F["Final Depth Map"]
    F --> G["Save as imageFilename_depth.png"]
    
    style A fill:none
    style B fill:none
    style C fill:none
    style D fill:none
    style E fill:none
    style F fill:none
    style G fill:none
```

The depth maps are stored with a consistent naming convention that appends `_depth` to the original image filename, as seen in the example file "a DSLR photo of a puffin standing on a rock_depth.png".

Sources: Repository overview diagrams

## Integration in Pipeline

Depth maps play several key roles in the DreamCraft3D pipeline:

1. **Stage 1 Initialization**: They provide initial depth constraints for the NeRF and NeuS training
2. **Multi-view Guidance**: They help generate consistent multi-view images from the single reference image
3. **Geometry Constraints**: They ensure that generated geometry respects the perceived depth in the original image

```mermaid
graph TB
    A["Input 2D Image"] --> B["Image Preprocessing"]
    B --> C["Depth Map"]
    B --> D["Normal Map"]
    B --> E["RGBA Image"]
    
    subgraph "Stage 1: Coarse Geometry Generation"
        F["img_to_mv.py"]
        G["NeRF Training"]
        H["NeuS Training"]
    end
    
    C --> F
    F --> G
    G --> H
    H --> I["Initial 3D Mesh"]
    
    I --> J["Stage 2: Geometry Refinement"]
    
    style A fill:none
    style B fill:none
    style C fill:none
    style D fill:none
    style E fill:none
    style F fill:none
    style G fill:none
    style H fill:none
    style I fill:none
    style J fill:none
```

In the first stage of the pipeline, depth maps are used alongside normal maps to generate multi-view images that guide the NeRF and NeuS training processes.

Sources: Repository overview diagrams

## Data Format and Processing

Depth maps in DreamCraft3D are stored as grayscale PNG images. The value of each pixel represents the relative distance from the camera viewpoint:

| Pixel Value | Meaning |
|-------------|---------|
| Dark (near 0) | Closest to camera |
| Light (near 255) | Farthest from camera |
| Middle values | Intermediate distances |

```mermaid
graph TD
    A["Depth Map Structure"] --> B["Grayscale PNG Image"]
    B --> C["Pixel Values Represent Distance"]
    
    C --> D["Dark (0): Closest"]
    C --> E["Gray: Intermediate"]
    C --> F["White (255): Farthest"]
    
    G["File Naming"] --> H["Original Filename + _depth.png"]
    
    I["Storage Location"] --> J["load/images/ Directory"]
    
    style A fill:none
    style B fill:none
    style C fill:none
    style D fill:none
    style E fill:none
    style F fill:none
    style G fill:none
    style H fill:none
    style I fill:none
    style J fill:none
```

Sources: load/images/a DSLR photo of a puffin standing on a rock_depth.png

## Common Issues and Troubleshooting

When working with depth maps in DreamCraft3D, you may encounter these common issues:

1. **Inaccurate depth estimation**: Happens when the reference image contains complex scenes or unusual objects
2. **Inconsistent depth boundaries**: Can cause artifacts in the generated 3D model, especially at object edges
3. **Flat depth regions**: Some areas may lack depth detail, resulting in flat geometry in those regions

To address these issues:

- Use reference images with clear subjects against simple backgrounds
- Manually check generated depth maps before proceeding to Stage 1
- If depth estimation fails, consider using alternative reference images

Sources: Repository overview diagrams

## Relationship to Other Components

Depth maps work in conjunction with normal maps and RGBA images in the preprocessing stage to provide comprehensive 3D information:

```mermaid
graph LR
    A["Image Preprocessing"] --> B["Depth Maps"]
    A --> C["Normal Maps"]
    A --> D["RGBA Images"]
    
    B --> E["Distance Information"]
    C --> F["Surface Orientation"]
    D --> G["Subject Isolation"]
    
    E & F & G --> H["Stage 1: Coarse Geometry"]
    H --> I["NeRF Training"]
    I --> J["NeuS Training"]
    J --> K["Initial 3D Mesh"]
    
    style A fill:none
    style B fill:none
    style C fill:none
    style D fill:none
    style E fill:none
    style F fill:none
    style G fill:none
    style H fill:none
    style I fill:none
    style J fill:none
    style K fill:none
```

While depth maps provide the distance information, normal maps encode surface orientation, and RGBA images isolate the subject with transparency information. Together, these three preprocessing components enable the system to generate accurate initial 3D geometry from a single 2D image.

Sources: Repository overview diagrams

---

