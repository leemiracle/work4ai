<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/rslearn_projects · page 7 Additional Applications · fetched 2026-10-26 -->

# Additional Applications

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [data/maldives_ecosystem_mapping/config_sentinel2.yaml](data/maldives_ecosystem_mapping/config_sentinel2.yaml)
- [rslp/maldives_ecosystem_mapping/README.md](rslp/maldives_ecosystem_mapping/README.md)
- [rslp/maldives_ecosystem_mapping/data_pipeline.py](rslp/maldives_ecosystem_mapping/data_pipeline.py)

</details>



This document covers specialized machine learning applications for remote sensing tasks that extend beyond the core systems covered in other sections. These applications demonstrate the flexibility of the rslearn framework for domain-specific remote sensing problems.

The applications documented here include ecosystem mapping for the Maldives using semantic segmentation and crop type classification systems. For comprehensive vessel detection systems, see [Vessel Detection Systems](#4). For large-scale geospatial inference, see [Satlas System](#5). For foundation model applications, see [Helios Foundation Model](#6).

## System Overview

The additional applications leverage the core rslearn framework infrastructure while implementing specialized data processing pipelines and model architectures for specific remote sensing tasks.

```mermaid
graph TB
    subgraph "Additional Applications"
        maldives["Maldives Ecosystem Mapping"]
        crop_mapping["Crop Type Mapping"]
    end
    
    subgraph "Core Infrastructure"
        rslearn_framework["rslearn Framework"]
        lightning_cli["CustomLightningCLI"]
        multitask_model["MultiTaskModel"]
        satlaspretrain["SatlasPretrain"]
    end
    
    subgraph "Data Sources"
        kili_annotations["Kili Annotations"]
        maxar_imagery["Maxar Imagery"]
        sentinel2_imagery["Sentinel-2 Imagery"]
        csv_ground_truth["CSV Ground Truth"]
    end
    
    subgraph "Processing Pipelines"
        data_pipeline["data_pipeline()"]
        window_creation["Window Creation"]
        label_processing["Label Processing"]
    end
    
    kili_annotations --> maldives
    maxar_imagery --> maldives
    sentinel2_imagery --> maldives
    csv_ground_truth --> crop_mapping
    
    maldives --> data_pipeline
    crop_mapping --> window_creation
    
    data_pipeline --> rslearn_framework
    window_creation --> rslearn_framework
    
    rslearn_framework --> lightning_cli
    lightning_cli --> multitask_model
    multitask_model --> satlaspretrain
    
    maldives --> label_processing
    label_processing --> rslearn_framework
```

**Additional Applications Architecture**

Sources: [rslp/maldives_ecosystem_mapping/data_pipeline.py:1-690](), [data/maldives_ecosystem_mapping/config_sentinel2.yaml:1-161]()

## Maldives Ecosystem Mapping

The Maldives ecosystem mapping system performs semantic segmentation of marine ecosystems using annotations from Kili and multiple satellite data sources. The system processes both labeled crops for training and unlabeled full images for inference.

### Data Pipeline Architecture

The Maldives system implements a sophisticated data pipeline that handles multiple satellite data sources and creates rslearn-compatible datasets from Kili annotations.

```mermaid
graph TB
    subgraph "Input Data"
        kili_json["Kili JSON Exports"]
        maxar_geotiff["Maxar GeoTIFF Files"]
        islands_geojson["Islands GeoJSON"]
    end
    
    subgraph "Job Processing"
        load_label["load_label()"]
        maxar_job["MaxarJob"]
        bare_job["BareJob"]
        process_maxar["process_maxar()"]
        process_bare["process_bare()"]
    end
    
    subgraph "Window Creation"
        images_windows["images/ Windows"]
        crops_windows["crops/ Windows"]
        images_sentinel2["images_sentinel2/ Windows"]
        crops_sentinel2["crops_sentinel2/ Windows"]
    end
    
    subgraph "Label Processing"
        label_class["Label Class"]
        convert_geom["convert_geom()"]
        rasterize["rasterio.features.rasterize()"]
    end
    
    subgraph "rslearn Dataset"
        dataset_structure["Dataset Structure"]
        window_metadata["Window Metadata"]
        layer_data["Layer Data"]
    end
    
    kili_json --> load_label
    load_label --> label_class
    label_class --> convert_geom
    
    maxar_geotiff --> maxar_job
    islands_geojson --> bare_job
    
    maxar_job --> process_maxar
    bare_job --> process_bare
    
    process_maxar --> images_windows
    process_maxar --> crops_windows
    process_bare --> images_sentinel2
    process_bare --> crops_sentinel2
    
    convert_geom --> rasterize
    rasterize --> crops_windows
    rasterize --> crops_sentinel2
    
    images_windows --> dataset_structure
    crops_windows --> dataset_structure
    images_sentinel2 --> dataset_structure
    crops_sentinel2 --> dataset_structure
```

**Maldives Data Pipeline Flow**

Sources: [rslp/maldives_ecosystem_mapping/data_pipeline.py:572-690](), [rslp/maldives_ecosystem_mapping/data_pipeline.py:214-246]()

### Core Classes and Components

The data pipeline is built around several key classes that handle different aspects of data processing:

| Class | Purpose | Key Methods |
|-------|---------|-------------|
| `DataPipelineConfig` | Configuration management | Inherits from `BaseDataPipelineConfig` |
| `Label` | Segmentation label representation | `__init__()` with geometries and classes |
| `MaxarJob` | Maxar scene processing | Used with `process_maxar()` |
| `BareJob` | Non-Maxar window creation | Used with `process_bare()` |

The `Label` class encapsulates segmentation annotations with spatial and temporal information:

```mermaid
graph LR
    subgraph "Label Class Structure"
        label_init["Label.__init__()"]
        bounding_geom["bounding_geom: STGeometry"]
        geoms["geoms: list[STGeometry]"]
        classes["classes: list[int]"]
        ts["ts: datetime"]
    end
    
    subgraph "Geometry Processing"
        convert_geom_func["convert_geom()"]
        wgs84_proj["WGS84_PROJECTION"]
        target_proj["Target Projection"]
    end
    
    subgraph "Rasterization"
        rasterio_features["rasterio.features.rasterize()"]
        mask_output["Segmentation Mask"]
        vis_output["Visualization Image"]
    end
    
    label_init --> bounding_geom
    label_init --> geoms
    label_init --> classes
    label_init --> ts
    
    geoms --> convert_geom_func
    convert_geom_func --> wgs84_proj
    wgs84_proj --> target_proj
    
    target_proj --> rasterio_features
    rasterio_features --> mask_output
    rasterio_features --> vis_output
```

**Label Processing Architecture**

Sources: [rslp/maldives_ecosystem_mapping/data_pipeline.py:70-92](), [rslp/maldives_ecosystem_mapping/data_pipeline.py:181-211]()

### Multi-Source Data Integration

The system handles multiple satellite data sources through a unified approach using the `get_bare_jobs()` function:

```mermaid
graph TB
    subgraph "Island Processing"
        island_feature["Island Feature from GeoJSON"]
        island_props["Island Properties"]
        window_prefix["Window Prefix Generation"]
    end
    
    subgraph "Satellite Data Sources"
        sentinel2["Sentinel-2 (10m resolution)"]
        skysat["SkySat (0.5m resolution)"]
        planetscope["PlanetScope (2m resolution)"]
    end
    
    subgraph "Projection Handling"
        utm_projection["get_utm_ups_projection()"]
        dst_projection["Destination Projection"]
        geom_transform["Geometry Transformation"]
    end
    
    subgraph "Job Creation"
        bare_job_creation["BareJob Creation"]
        suffix_assignment["Suffix Assignment"]
        label_matching["Label Matching"]
    end
    
    island_feature --> island_props
    island_props --> window_prefix
    
    sentinel2 --> utm_projection
    skysat --> utm_projection
    planetscope --> utm_projection
    
    utm_projection --> dst_projection
    dst_projection --> geom_transform
    
    window_prefix --> bare_job_creation
    geom_transform --> bare_job_creation
    suffix_assignment --> bare_job_creation
    label_matching --> bare_job_creation
```

**Multi-Source Data Integration**

Sources: [rslp/maldives_ecosystem_mapping/data_pipeline.py:494-570](), [rslp/maldives_ecosystem_mapping/data_pipeline.py:547-567]()

### Model Configuration

The system uses a `MultiTaskModel` with `SatlasPretrain` encoder for semantic segmentation:

| Configuration Aspect | Implementation |
|---------------------|----------------|
| **Encoder** | `SatlasPretrain` with `Sentinel2_SwinB_MI_MS` |
| **Time Series** | `SimpleTimeSeries` with 6 temporal groups |
| **Decoder** | `UNetDecoder` with `SegmentationHead` |
| **Input Channels** | 9 Sentinel-2 bands |
| **Output Classes** | 17 ecosystem categories |
| **Loss Function** | Cross-entropy with class remapping |

Sources: [data/maldives_ecosystem_mapping/config_sentinel2.yaml:1-161]()

### Usage and Workflow

The complete workflow for Maldives ecosystem mapping follows these steps:

1. **Data Preprocessing**: Run `data_pipeline()` to create rslearn dataset
2. **Model Training**: Use `CustomLightningCLI` with configuration files
3. **Inference**: Apply trained model to full images for ecosystem mapping

The system creates multiple window groups for different purposes:
- `images/`: Full Maxar scenes (unlabeled)
- `crops/`: Labeled patches from Maxar scenes
- `images_sentinel2/`: Full island coverage (unlabeled)
- `crops_sentinel2/`: Labeled patches for training

Sources: [rslp/maldives_ecosystem_mapping/README.md:1-55](), [rslp/maldives_ecosystem_mapping/data_pipeline.py:572-690]()

## Crop Type Mapping

The crop type mapping system generates spatial-temporal windows from CSV ground truth data for crop classification tasks. This system creates training data by extracting satellite imagery windows based on ground truth locations and timestamps provided in CSV format.

The crop mapping application demonstrates how the rslearn framework can be extended for agricultural remote sensing applications where ground truth data is provided in tabular format rather than as spatial annotations.

Sources: Based on table of contents structure, specific implementation files not provided.

## Integration with Core Infrastructure

These additional applications integrate seamlessly with the core rslearn infrastructure:

- **Dataset Management**: Use rslearn `Dataset` and `Window` classes
- **Model Training**: Leverage `CustomLightningCLI` and `MultiTaskModel`
- **Data Processing**: Utilize rslearn transforms and data modules
- **Distributed Computing**: Support Beaker cluster execution

The applications demonstrate the extensibility of the rslearn framework for specialized remote sensing tasks while maintaining consistency with the overall system architecture.

Sources: [rslp/maldives_ecosystem_mapping/data_pipeline.py:20-31](), [data/maldives_ecosystem_mapping/config_sentinel2.yaml:30-140]()

---

