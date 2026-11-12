<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/renderformer · page 7 Data & Resources · fetched 2026-10-26 -->

# Data & Resources

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [download_video_data.sh](download_video_data.sh)

</details>



This document covers the external datasets, pre-trained models, example assets, and other resources available for use with RenderFormer. It includes information about downloading and organizing video datasets, accessing pre-trained models from Hugging Face, and utilizing example scenes and 3D assets.

For information about scene definition formats and creating your own scenes, see [Scene Definition](#5). For details about the internal HDF5 data format, see [Data Formats](#2.3).

## Dataset Overview

RenderFormer provides access to multiple types of data resources through different channels. The system relies on external datasets for video rendering examples, pre-trained transformer models for inference, and a collection of example scenes with 3D assets.

```mermaid
graph TB
    subgraph "External Data Sources"
        A["Hugging Face Hub"]
        B["GitHub Repository"]
        C["Third-party Assets"]
    end
    
    subgraph "Data Categories"
        D["Pre-trained Models<br/>microsoft/renderformer-*"]
        E["Video Dataset<br/>renderformer/renderformer-video-data"]
        F["Example Scenes<br/>examples/*.json"]
        G["3D Model Assets<br/>examples/templates/objects/*"]
    end
    
    subgraph "Local Organization"
        H["video-data/<br/>animations/<br/>teaser-scenes/<br/>simulations/"]
        I["examples/<br/>Scene JSON files"]
        J["Model Cache<br/>~/.cache/huggingface/"]
    end
    
    subgraph "Usage Entry Points"
        K["batch_infer.py<br/>--h5_folder"]
        L["infer.py<br/>--model_id"]
        M["convert_scene.py<br/>examples/*.json"]
    end
    
    A --> D
    A --> E
    B --> F
    B --> G
    
    D --> J
    E --> H
    F --> I
    G --> I
    
    J --> L
    H --> K
    I --> M
    
    style A fill:#f9f,stroke:#333,stroke-width:2px
    style E fill:#bbf,stroke:#333,stroke-width:2px
    style D fill:#bbf,stroke:#333,stroke-width:2px
```

Sources: [README.md:93-98](), [README.md:194-196](), [README.md:322-342]()

## Video Dataset

The RenderFormer video dataset is hosted on Hugging Face and contains pre-rendered scene sequences for video generation examples. The dataset includes various scene types organized into categories.

### Dataset Structure

```mermaid
graph TD
    A["renderformer/renderformer-video-data<br/>Hugging Face Dataset"]
    
    subgraph "Dataset Categories"
        B["animations/<br/>Dynamic object animations"]
        C["teaser-scenes/<br/>Promotional examples"] 
        D["simulations/<br/>Physics simulations"]
    end
    
    subgraph "File Organization"
        E["*.zip files<br/>Compressed scene data"]
        F["Extracted directories<br/>Individual scenes"]
        G["*.h5 files<br/>HDF5 scene format"]
    end
    
    subgraph "Processing Pipeline"
        H["download_video_data.sh<br/>Download script"]
        I["huggingface-cli download<br/>CLI tool"]
        J["Automatic unzipping<br/>Directory creation"]
    end
    
    A --> B
    A --> C  
    A --> D
    
    B --> E
    C --> E
    D --> E
    
    E --> F
    F --> G
    
    I --> H
    H --> J
    J --> F
    
    style A fill:#bbf,stroke:#333,stroke-width:2px
    style H fill:#bfb,stroke:#333,stroke-width:2px
```

Sources: [README.md:194-196](), [download_video_data.sh:1-44]()

### Download Process

The video dataset can be downloaded using the provided shell script, which handles both downloading and extraction:

| Component | Purpose | Location |
|-----------|---------|----------|
| `huggingface-cli` | Command-line tool for downloading | System dependency |
| `download_video_data.sh` | Automated download script | [download_video_data.sh:1-44]() |
| Local storage | Extracted video data | `video-data/` directory |

The download script performs these operations:
1. Downloads dataset using `huggingface-cli download --repo-type dataset renderformer/renderformer-video-data`
2. Creates organized directory structure
3. Extracts ZIP files into named subdirectories
4. Processes animations, teaser-scenes, and simulations categories

```mermaid
sequenceDiagram
    participant User
    participant Script as "download_video_data.sh"
    participant HF as "Hugging Face CLI"
    participant FS as "File System"
    
    User->>Script: Execute download script
    Script->>HF: huggingface-cli download
    HF->>FS: Download to video-data/
    Script->>FS: Check directory exists
    
    loop For each category
        Script->>FS: Process *.zip files
        FS->>Script: Return zip file list
        
        loop For each zip file
            Script->>FS: mkdir dirname
            Script->>FS: unzip file to dirname
        end
    end
    
    Script->>User: Completion message
```

Sources: [download_video_data.sh:2-3](), [download_video_data.sh:10-36]()

### Usage with Batch Inference

The downloaded video data is designed for use with the batch inference pipeline:

```bash
python3 batch_infer.py --h5_folder renderformer-video-data/submission-videos/cbox-roughness/ --output_dir output/videos/cbox-roughness
```

The `TriangleRenderH5Dataset` class in the batch inference system reads the HDF5 files from these directories and processes them for video rendering.

Sources: [README.md:199-201]()

## Pre-trained Models

RenderFormer provides pre-trained transformer models through Hugging Face Hub, offering different parameter sizes for various computational requirements.

### Available Models

| Model Name | Parameters | Hugging Face ID | Purpose |
|------------|------------|-----------------|---------|
| RenderFormer-V1-Base | 205M | `microsoft/renderformer-v1-base` | Lightweight inference |
| RenderFormer-V1.1-Large | 483M | `microsoft/renderformer-v1.1-swin-large` | High-quality rendering |

### Model Architecture Mapping

```mermaid
graph LR
    subgraph "Hugging Face Models"
        A["microsoft/renderformer-v1-base<br/>205M parameters"]
        B["microsoft/renderformer-v1.1-swin-large<br/>483M parameters"]
    end
    
    subgraph "Pipeline Integration"
        C["RenderFormerRenderingPipeline.from_pretrained()"]
    end
    
    subgraph "Model Components"
        D["View-Independent Stage<br/>Triangle-to-triangle transport"]
        E["View-Dependent Stage<br/>Ray-to-pixel transformation"]
    end
    
    subgraph "Inference Usage"
        F["infer.py<br/>--model_id"]
        G["batch_infer.py<br/>--model_id"]
    end
    
    A --> C
    B --> C
    C --> D
    C --> E
    C --> F
    C --> G
    
    style C fill:#bbf,stroke:#333,stroke-width:2px
    style A fill:#f9f,stroke:#333,stroke-width:2px
    style B fill:#f9f,stroke:#333,stroke-width:2px
```

Sources: [README.md:94-98](), [README.md:138](), [README.md:210]()

### Model Loading Process

The models are automatically downloaded and cached when first accessed through the `RenderFormerRenderingPipeline.from_pretrained()` method. The system handles model loading, device placement, and precision configuration.

Sources: [README.md:159]()

## Example Scenes and Assets

The repository includes a comprehensive collection of example scenes and 3D model assets for testing and demonstration purposes.

### Scene Organization

```mermaid
graph TB
    subgraph "Scene Categories"
        A["examples/<br/>Scene JSON files"]
    end
    
    subgraph "Asset Types"
        B["Cornell Box Scenes<br/>cbox*.json"]
        C["Complex Scenes<br/>Multi-object compositions"]
        D["Template Assets<br/>Reusable components"]
    end
    
    subgraph "3D Models"
        E["Object Meshes<br/>*.obj files"]
        F["Lighting Templates<br/>Light source geometry"]
        G["Standard Test Objects<br/>Bunny, teapot, etc."]
    end
    
    subgraph "Processing Pipeline"
        H["convert_scene.py<br/>JSON to HDF5"]
        I["remesh.py<br/>Face optimization"]
        J["Texture Processing<br/>Material extraction"]
    end
    
    A --> B
    A --> C
    A --> D
    
    B --> E
    C --> E
    D --> F
    
    E --> H
    F --> H
    G --> H
    
    H --> I
    H --> J
    
    style A fill:#bfb,stroke:#333,stroke-width:2px
    style H fill:#bbf,stroke:#333,stroke-width:2px
```

Sources: [README.md:111-115](), [README.md:274](), [README.md:292-298]()

### Asset Attribution

The repository includes 3D models from various sources with proper attribution:

| Source | Assets | Usage |
|--------|--------|-------|
| Stanford Repository | Bunny, Lucy | Standard test geometry |
| Cornell University | Cornell Box | Classic rendering test |
| Mitsuba Gallery | Shader Ball | Material testing |
| Objaverse | Various objects | Scene composition |
| Microsoft | Custom models | Demonstration scenes |

The complete attribution list includes licensing information and source URLs for all included 3D assets.

Sources: [README.md:322-342]()

## External Dependencies and Resources

RenderFormer integrates with several external resources and tools that provide additional functionality.

### Resource Integration Map

```mermaid
graph TD
    subgraph "External Tools"
        A["Blender Extension<br/>Scene creation aid"]
        B["huggingface-cli<br/>Dataset download"]
        C["imageio.freeimage<br/>HDR image support"]
    end
    
    subgraph "Data Repositories"
        D["Hugging Face Hub<br/>Models + datasets"]
        E["GitHub Repositories<br/>Code dependencies"]
        F["Academic Sources<br/>3D model collections"]
    end
    
    subgraph "Integration Points"
        G["renderformer-blender-extension<br/>UI integration"]
        H["requirements.txt<br/>Python dependencies"]
        I["Attribution system<br/>License compliance"]
    end
    
    A --> G
    B --> D
    C --> H
    
    D --> H
    E --> H
    F --> I
    
    G --> A
    H --> B
    H --> C
    I --> F
    
    style D fill:#f9f,stroke:#333,stroke-width:2px
    style H fill:#bbf,stroke:#333,stroke-width:2px
```

Sources: [README.md:300-302](), [README.md:87-90](), [README.md:314-342]()

### Setup Requirements

The external resources require specific setup steps:

1. **HDR Image Support**: `python3 -c "import imageio; imageio.plugins.freeimage.download()"`
2. **Hugging Face CLI**: Required for dataset downloads
3. **Blender Extension**: Optional UI tool for scene creation

These dependencies are managed through the installation process and provide extended functionality for data handling and user interaction.

Sources: [README.md:89](), [download_video_data.sh:2]()

---

