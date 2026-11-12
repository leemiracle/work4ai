<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/geeflow · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [geeflow/__init__.py](geeflow/__init__.py)

</details>



This document provides a high-level introduction to GeoFlow, explaining its purpose as a library for generating large-scale geospatial datasets using Google Earth Engine, and summarizing its key capabilities and architecture. For detailed information about running the pipelines, see [Getting Started](#2). For configuration details, see [Configuration System](#6). For specific pipeline documentation, see [Main Pipelines](#4).

## Purpose and Scope

GeoFlow is a Python library designed for generating large-scale geospatial datasets using [Google Earth Engine](https://earthengine.google.com) (GEE). The library focuses on supporting geospatial AI research by providing utilities, configurations, and pipeline launch scripts to extract and process satellite data into machine learning-ready formats.

**Core Capabilities:**
- Creating small- and large-scale datasets (supervised and unsupervised) ready for geospatial AI model training
- Generating inference maps up to global scale at arbitrary resolutions  
- Supporting any geospatial satellite and remote sensing data available in Google Earth Engine
- Providing arbitrary spatial and temporal resolution sampling of data sources
- Producing datasets in TensorFlow Datasets (TFDS) format with precomputed statistics

**Out of Scope:**
- Model training and inference (use frameworks like JAX/Flax with [Jeo](https://github.com/google-deepmind/jeo) or PyTorch with [TorchGeo](https://github.com/microsoft/torchgeo))
- Interactive Earth Engine data visualization (use tools like [geemap](https://geemap.org))
- Dataset hosting and distribution (use platforms like Hugging Face or TFDS Catalog)

Sources: [README.md:7-41]()

## System Architecture

### High-Level Component Overview

```mermaid
graph TB
    subgraph "Configuration Layer"
        CONFIG_DEMO["demo.py<br/>Demo Configuration"]
        CONFIG_GLOBAL["global_drivers_1km_2022_v1.py<br/>Production Configuration"]
        CONFIG_DICT["ConfigDict<br/>Labels + Sources + Export"]
    end
    
    subgraph "Core Pipelines"
        EXPORT_BEAM["export_beam_tfds.py<br/>Main Dataset Export Pipeline"]
        STATS_BEAM["compute_stats_beam.py<br/>Statistics Computation Pipeline"]
    end
    
    subgraph "Data Processing Engine"
        PIPELINES["pipelines.py<br/>get_roi_sample_fn()<br/>get_requests_fn()"]
        EE_ALGO["ee_algo.py<br/>Earth Engine Algorithms"]
        EE_DATA["ee_data.py<br/>Sentinel2, Sentinel1, Hansen<br/>CustomImage, CustomIC, CustomFC"]
    end
    
    subgraph "Coordinate & Utility Systems"
        COORDS["coords.py<br/>UTM Grid Mapping"]
        UTILS["utils.py<br/>get_source_config()"]
        EE_EXPORT["ee_export_utils.py<br/>GetInfo DoFn"]
    end
    
    subgraph "Statistics Infrastructure"
        STATS_UTILS["compute_stats_beam_utils.py<br/>Statistics Pipeline"]
        STATS_UTIL["stats_util.py<br/>Accumulator Classes"]
    end
    
    subgraph "External Dependencies"
        GEE["Google Earth Engine<br/>Satellite Data Platform"]
        APACHE_BEAM["Apache Beam<br/>Distributed Processing"]
        TFDS_OUTPUT["TensorFlow Datasets<br/>Output Format"]
    end
    
    CONFIG_DEMO --> CONFIG_DICT
    CONFIG_GLOBAL --> CONFIG_DICT
    CONFIG_DICT --> EXPORT_BEAM
    CONFIG_DICT --> STATS_BEAM
    
    EXPORT_BEAM --> PIPELINES
    EXPORT_BEAM --> EE_EXPORT
    STATS_BEAM --> STATS_UTILS
    
    PIPELINES --> EE_ALGO
    PIPELINES --> EE_DATA
    PIPELINES --> COORDS
    PIPELINES --> UTILS
    
    EE_ALGO --> GEE
    EE_DATA --> GEE
    EE_EXPORT --> GEE
    
    STATS_UTILS --> STATS_UTIL
    
    EXPORT_BEAM --> APACHE_BEAM
    STATS_BEAM --> APACHE_BEAM
    
    EXPORT_BEAM --> TFDS_OUTPUT
    STATS_BEAM --> TFDS_OUTPUT
```

**System Architecture Overview**

Sources: [README.md:150-177](), [geeflow/export_beam_tfds.py](), [geeflow/stats/compute_stats_beam.py](), [geeflow/pipelines.py](), [geeflow/ee_data.py](), [geeflow/ee_algo.py]()

### Data Processing Workflow

```mermaid
flowchart TD
    INPUT_LABELS["Labels CSV/Parquet<br/>lat, lon, metadata"]
    INPUT_CONFIG["ML Collections ConfigDict<br/>Labels + Sources Configuration"]
    
    EXPORT_PIPELINE["export_beam_tfds.py<br/>TFDSBuilder._generate_examples()"]
    
    GET_REQUESTS["pipelines.get_requests_fn()<br/>Request Generation"]
    GET_ROI_SAMPLE["pipelines.get_roi_sample_fn()<br/>ROI Processing"]
    
    EE_PROCESSING["Earth Engine Processing<br/>ee_algo sampling & reduction<br/>ee_data source definitions"]
    
    COORD_TRANSFORM["coords.py<br/>UTM Grid Mapping<br/>Spatial Transformations"]
    
    GETINFO_DOFN["ee_export_utils.GetInfo DoFn<br/>Distributed EE Queries"]
    
    TFDS_RECORDS["TFDS Records<br/>train/val/test splits"]
    
    STATS_PIPELINE["compute_stats_beam.py<br/>Statistics Computation"]
    STATS_OUTPUT["JSON Statistics Files<br/>Per-band metrics"]
    
    INPUT_LABELS --> EXPORT_PIPELINE
    INPUT_CONFIG --> EXPORT_PIPELINE
    
    EXPORT_PIPELINE --> GET_REQUESTS
    GET_REQUESTS --> GET_ROI_SAMPLE
    
    GET_ROI_SAMPLE --> EE_PROCESSING
    GET_ROI_SAMPLE --> COORD_TRANSFORM
    
    EE_PROCESSING --> GETINFO_DOFN
    COORD_TRANSFORM --> GETINFO_DOFN
    
    GETINFO_DOFN --> TFDS_RECORDS
    TFDS_RECORDS --> STATS_PIPELINE
    STATS_PIPELINE --> STATS_OUTPUT
```

**Data Processing Workflow**

Sources: [README.md:161-177](), [geeflow/export_beam_tfds.py](), [geeflow/pipelines.py](), [geeflow/ee_export_utils.py](), [geeflow/stats/compute_stats_beam.py]()

## Core Concepts

### Configuration-Driven Design

GeoFlow uses [ML Collections ConfigDict](https://github.com/google/ml_collections) for flexible dataset configuration. The configuration is split into three main sections:

| Configuration Section | Purpose | Key Components |
|----------------------|---------|----------------|
| **Labels Configuration** | Defines sample locations and metadata | `path`, `img_width_m`, `max_cell_size_m`, `meta_keys` |
| **Sources Configuration** | Specifies Earth Engine data sources | Source classes, `scale`, `select`, `date_ranges`, `sampling_kw` |
| **Export Configuration** | Controls processing and output | Filters, transforms, CCDC generation options |

Sources: [README.md:56-147]()

### Earth Engine Integration

GeoFlow provides abstractions for common Earth Engine data sources through the `ee_data.py` module:

- **Predefined Sources**: `Sentinel2`, `Sentinel1`, `Hansen`, `NasaDem`, `MODIS` classes
- **Custom Sources**: `CustomImage`, `CustomIC`, `CustomFC` for arbitrary Earth Engine assets
- **Processing Algorithms**: Temporal aggregation, cloud masking, and spatial sampling in `ee_algo.py`

Sources: [README.md:105-109](), [README.md:152-158](), [geeflow/ee_data.py](), [geeflow/ee_algo.py]()

### Coordinate System Conventions

GeoFlow follows consistent coordinate system conventions:

- **Default CRS**: WGS 84 (World Geodetic System) for latitude/longitude
- **Projected Coordinates**: Local UTM (Universal Transverse Mercator) coordinates
- **Grid Mapping**: UTM-based spatial gridding implemented in `coords.py`
- **Reference Variables**: `lat`/`lon` for geographic coordinates throughout the codebase

Sources: [README.md:178-187](), [geeflow/coords.py]()

## Main Processing Pipelines

### Dataset Export Pipeline

The primary pipeline is implemented in `export_beam_tfds.py` and orchestrates the complete dataset generation process:

1. **Input Processing**: Reads label CSV/Parquet files and processes configuration
2. **Request Generation**: Uses `pipelines.get_requests_fn()` to create processing requests
3. **Data Extraction**: Applies `pipelines.get_roi_sample_fn()` per location to extract Earth Engine data
4. **Coordinate Transformation**: Maps geographic coordinates to UTM grid system
5. **TFDS Generation**: Converts processed data to TensorFlow Datasets format with train/val/test splits

Sources: [README.md:161-174](), [geeflow/export_beam_tfds.py]()

### Statistics Computation Pipeline  

The statistics pipeline in `compute_stats_beam.py` generates comprehensive dataset statistics:

1. **Band-level Analysis**: Computes statistics for each band in each data source
2. **Statistical Metrics**: Mean, variance, quantiles, histograms, and robust statistics
3. **Parallel Processing**: Uses Apache Beam for distributed computation
4. **Output Format**: JSON files with detailed per-band statistics

Sources: [README.md:174-177](), [README.md:285-322](), [geeflow/stats/compute_stats_beam.py]()

## Versioning and Reproducibility

GeoFlow implements semantic versioning for datasets using the pattern `{LABELS_VERSION}.{SOURCES_VERSION}.{OTHERS}`:

- **MAJOR**: Incremented for new or modified label sets
- **MINOR**: Incremented for changes to Earth Engine data sources  
- **PATCH**: Used for processing changes, split modifications, or other updates

The system automatically saves launch commands and configuration arguments for full reproducibility.

Sources: [README.md:189-204]()

## Integration Ecosystem

GeoFlow integrates with several external systems and follows established patterns:

- **Apache Beam**: Distributed processing for scalable dataset generation
- **TensorFlow Datasets**: Standard output format for ML pipelines  
- **Google Earth Engine**: Primary data source for satellite and geospatial data
- **JAX/Flax Integration**: Compatible with [Jeo](https://github.com/google-deepmind/jeo) for model training
- **Cloud Platform**: Designed for Google Cloud Platform deployment

Sources: [README.md:13-14](), [README.md:29-33](), [README.md:162-163](), [README.md:265-268]()

---

