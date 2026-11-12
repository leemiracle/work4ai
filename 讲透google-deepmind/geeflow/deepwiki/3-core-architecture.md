<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/geeflow · page 3 Core Architecture · fetched 2026-10-26 -->

# Core Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [geeflow/pipelines.py](geeflow/pipelines.py)
- [geeflow/utils.py](geeflow/utils.py)

</details>



This document explains the overall system architecture of GeeFlow, covering the key modules, their interactions, and the architectural patterns that enable large-scale geospatial dataset generation using Google Earth Engine. For configuration details, see [Configuration System](#6). For pipeline implementation specifics, see [Main Pipelines](#4).

## System Overview

GeeFlow follows a configuration-driven, pipeline-based architecture built on Apache Beam for distributed processing. The system transforms geospatial label data into machine learning-ready datasets by orchestrating Earth Engine queries through a modular processing pipeline.

## Core Architectural Components

### Configuration-Driven Design

```mermaid
graph TB
    subgraph "Configuration Layer"
        CONFIG["ml_collections.ConfigDict"]
        LABELS_CONFIG["labels config<br/>- path: CSV/Parquet<br/>- img_width_m<br/>- max_cell_size_m<br/>- meta_keys"]
        SOURCES_CONFIG["sources config<br/>- module: EE data class<br/>- scale: resolution<br/>- select: bands<br/>- date_ranges"]
        EXPORT_CONFIG["export config<br/>- filters<br/>- transforms"]
    end
    
    subgraph "Main Entry Points"
        EXPORT_BEAM["export_beam_tfds.py<br/>Dataset Export Pipeline"]
        STATS_BEAM["compute_stats_beam.py<br/>Statistics Pipeline"]
    end
    
    subgraph "Core Processing"
        PIPELINES["pipelines.py<br/>get_requests_fn()<br/>pipeline_labels()<br/>pipeline_sources()"]
        EE_EXPORT["ee_export_utils.py<br/>GetInfo DoFn"]
    end
    
    CONFIG --> LABELS_CONFIG
    CONFIG --> SOURCES_CONFIG
    CONFIG --> EXPORT_CONFIG
    
    LABELS_CONFIG --> EXPORT_BEAM
    SOURCES_CONFIG --> EXPORT_BEAM
    EXPORT_CONFIG --> EXPORT_BEAM
    
    CONFIG --> STATS_BEAM
    
    EXPORT_BEAM --> PIPELINES
    EXPORT_BEAM --> EE_EXPORT
    STATS_BEAM --> PIPELINES
```

Sources: [README.md:56-142](), [geeflow/utils.py:216-227]()

### Request-Response Architecture

The system uses a request-response pattern where processing is broken down into discrete `Request` objects that encapsulate Earth Engine queries:

```mermaid
graph LR
    subgraph "Input Processing"
        LABELS_DF["pd.DataFrame<br/>from CSV/Parquet"]
        PIPELINE_LABELS["pipelines.pipeline_labels()"]
        PIPELINE_ROIS["pipelines.pipeline_item_to_rois()"]
    end
    
    subgraph "Request Generation"
        REQUEST_FN["pipelines.get_requests_fn()"]
        REQUEST_OBJ["Request<br/>- image: ee.Image<br/>- roi: ee.Geometry<br/>- scale: int<br/>- name: str<br/>- crs: str"]
    end
    
    subgraph "Earth Engine Processing"
        EE_SOURCES["pipelines.pipeline_sources()"]
        EE_ALGO["ee_algo functions<br/>- ic_sample_date_ranges<br/>- sample_roi<br/>- get_ccdc"]
        EE_EXPORT_UTILS["ee_export_utils.py<br/>GetInfo DoFn"]
    end
    
    subgraph "Output"
        TFDS_RECORDS["TFDS Records"]
    end
    
    LABELS_DF --> PIPELINE_LABELS
    PIPELINE_LABELS --> PIPELINE_ROIS
    PIPELINE_ROIS --> REQUEST_FN
    EE_SOURCES --> REQUEST_FN
    REQUEST_FN --> REQUEST_OBJ
    REQUEST_OBJ --> EE_EXPORT_UTILS
    EE_ALGO --> EE_EXPORT_UTILS
    EE_EXPORT_UTILS --> TFDS_RECORDS
```

Sources: [geeflow/pipelines.py:61-70](), [geeflow/pipelines.py:289-410]()

## Module Architecture

### Core Processing Modules

The system is organized into distinct processing layers:

```mermaid
graph TB
    subgraph "Entry Points"
        EXPORT["export_beam_tfds.py<br/>TFDSBuilder._generate_examples()"]
        STATS["compute_stats_beam.py<br/>beam.Pipeline"]
    end
    
    subgraph "Pipeline Orchestration"
        PIPELINES_PY["pipelines.py"]
        GET_REQUESTS["get_requests_fn()"]
        PIPELINE_LABELS_FN["pipeline_labels()"]
        PIPELINE_SOURCES_FN["pipeline_sources()"]
        PIPELINE_ROIS_FN["pipeline_item_to_rois()"]
    end
    
    subgraph "Earth Engine Layer"
        EE_DATA["ee_data.py<br/>EeData classes<br/>- Sentinel1, Sentinel2<br/>- Hansen, NasaDem<br/>- CustomImage, CustomIC"]
        EE_ALGO["ee_algo.py<br/>Processing algorithms<br/>- ic_sample_date_ranges<br/>- sample_roi<br/>- get_ccdc"]
        EE_EXPORT_UTILS["ee_export_utils.py<br/>GetInfo DoFn<br/>Beam processing"]
    end
    
    subgraph "Coordinate & Utilities"
        COORDS["coords.py<br/>UtmGridMapping<br/>get_lat_lon_roi()"]
        UTILS["utils.py<br/>initialize_ee()<br/>parse_arg()<br/>get_source_config()"]
        TIMES["times.py<br/>Date/time utilities"]
    end
    
    EXPORT --> PIPELINES_PY
    STATS --> PIPELINES_PY
    
    PIPELINES_PY --> GET_REQUESTS
    PIPELINES_PY --> PIPELINE_LABELS_FN
    PIPELINES_PY --> PIPELINE_SOURCES_FN
    PIPELINES_PY --> PIPELINE_ROIS_FN
    
    GET_REQUESTS --> EE_ALGO
    PIPELINE_SOURCES_FN --> EE_DATA
    PIPELINE_ROIS_FN --> COORDS
    
    EE_EXPORT_UTILS --> EE_ALGO
    
    UTILS --> COORDS
    COORDS --> TIMES
```

Sources: [geeflow/pipelines.py:1-36](), [README.md:150-177]()

### Data Flow Through Processing Layers

```mermaid
flowchart TD
    A["Label CSV/Parquet"] --> B["pipelines.get_labels_df()"]
    B --> C["pipelines.pipeline_labels()"]
    C --> D["List[Dict[str, Any]]<br/>label items"]
    
    D --> E["pipelines.pipeline_item_to_rois()"]
    E --> F["Dict[str, ee.Geometry]<br/>ROI geometries"]
    
    G["Config sources"] --> H["pipelines.pipeline_sources()"]
    H --> I["Dict[str, EeAssetType]<br/>EE assets"]
    
    F --> J["pipelines.get_requests_fn()"]
    I --> J
    J --> K["List[Request]<br/>EE query requests"]
    
    K --> L["ee_export_utils.GetInfo DoFn"]
    L --> M["Apache Beam PCollection"]
    M --> N["TFDS Records"]
    
    style D fill:#e8f5e8
    style F fill:#fff3e0
    style I fill:#e3f2fd
    style K fill:#f3e5f5
```

Sources: [geeflow/pipelines.py:106-128](), [geeflow/pipelines.py:179-208](), [geeflow/pipelines.py:289-410]()

## Algorithm Selection and Processing

The system uses a mapping strategy to select appropriate processing algorithms based on the data source type:

| Data Source Type | Algorithm Function | Purpose |
|------------------|-------------------|---------|
| `IC_SAMPLE_DATE_RANGES` | `ee_algo.ic_sample_date_ranges` | Time-series sampling with date ranges |
| `IC_SAMPLE` | `ee_algo.ic_sample` | Simple image collection sampling |
| `RGB_IC_SAMPLE` | `ee_algo.rgb_ic_sample` | RGB-specific collection sampling |
| `SAMPLE_ROI` | `ee_algo.sample_roi` | Region-of-interest sampling |
| `FC_GET` | `ee_algo.fc_get` | Feature collection property extraction |
| `CCDC` | `ee_algo.get_ccdc` | Continuous Change Detection Classification |

Sources: [geeflow/pipelines.py:42-59](), [geeflow/pipelines.py:262-272]()

## Coordinate System Management

GeeFlow implements a sophisticated coordinate system that handles both UTM projections and lat/lon coordinates:

```mermaid
graph TB
    subgraph "Coordinate Input"
        LAT_LON["lat, lon coordinates<br/>from label data"]
        UTM_COORDS["UTM coordinates<br/>(optional in labels)"]
    end
    
    subgraph "Coordinate Processing"
        UTM_GRID["coords.UtmGridMapping"]
        FROM_LATLON["from_latlon_center()"]
        TO_EE["to_ee(utm=True)"]
        GET_LAT_LON_ROI["coords.get_lat_lon_roi()"]
    end
    
    subgraph "Geometry Output"
        EE_GEOMETRY["ee.Geometry<br/>ROI for EE queries"]
        SCALE_ALIGNMENT["realign_geometry_scale()"]
    end
    
    LAT_LON --> FROM_LATLON
    UTM_COORDS --> UTM_GRID
    FROM_LATLON --> UTM_GRID
    UTM_GRID --> TO_EE
    LAT_LON --> GET_LAT_LON_ROI
    TO_EE --> EE_GEOMETRY
    GET_LAT_LON_ROI --> EE_GEOMETRY
    EE_GEOMETRY --> SCALE_ALIGNMENT
```

Sources: [geeflow/pipelines.py:131-159](), [geeflow/pipelines.py:250-259]()

## Configuration Processing Pipeline

The configuration system transforms user specifications into executable processing functions:

```mermaid
graph LR
    subgraph "Configuration Input"
        CONFIG_DICT["ml_collections.ConfigDict"]
        LABELS_CFG["config.labels"]
        SOURCES_CFG["config.sources"]
    end
    
    subgraph "Pipeline Construction"
        LABELS_PIPELINE["pipeline_labels()"]
        SOURCES_PIPELINE["pipeline_sources()"]
        REQUESTS_PIPELINE["get_requests_fn()"]
    end
    
    subgraph "Processing Functions"
        LABEL_ITEMS["List[Dict]<br/>processed labels"]
        EE_ASSETS["Dict[str, EeAssetType]<br/>initialized assets"]
        REQUEST_FUNCTION["Callable<br/>item → requests"]
    end
    
    LABELS_CFG --> LABELS_PIPELINE
    SOURCES_CFG --> SOURCES_PIPELINE
    CONFIG_DICT --> REQUESTS_PIPELINE
    
    LABELS_PIPELINE --> LABEL_ITEMS
    SOURCES_PIPELINE --> EE_ASSETS
    REQUESTS_PIPELINE --> REQUEST_FUNCTION
    
    EE_ASSETS --> REQUEST_FUNCTION
```

Sources: [geeflow/pipelines.py:115-128](), [geeflow/pipelines.py:179-208](), [geeflow/pipelines.py:289-291]()

## Error Handling and Validation

The system includes validation at multiple levels:

- **Band/Property Validation**: [geeflow/pipelines.py:223-247]() validates that selected bands exist in the source
- **Configuration Validation**: [geeflow/pipelines.py:266-272]() ensures valid algorithm mapping
- **Geometry Validation**: [geeflow/pipelines.py:315-321]() handles scale alignment for grid consistency

The architecture emphasizes modularity and extensibility, allowing new Earth Engine data sources and processing algorithms to be added through the configuration system without modifying core pipeline logic.

---

