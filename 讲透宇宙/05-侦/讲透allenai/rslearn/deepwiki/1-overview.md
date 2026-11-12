<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/rslearn · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [extra_requirements.txt](extra_requirements.txt)
- [pyproject.toml](pyproject.toml)
- [requirements.txt](requirements.txt)
- [rslearn/py.typed](rslearn/py.typed)

</details>



## Purpose and Scope

This document provides a high-level technical overview of the rslearn framework, a comprehensive library and command-line tool for developing remote sensing datasets and machine learning models. rslearn facilitates the entire pipeline from raw satellite data ingestion to model training and inference for remote sensing applications.

The framework addresses five core capabilities: defining spatiotemporal windows for training data, importing raster and vector data from diverse sources, annotating vector data through integrated labeling applications, fine-tuning remote sensing foundation models, and applying trained models to new geographic locations and time periods.

For specific implementation details of individual subsystems, see [Data Sources](#4), [Dataset Management](#5), [Machine Learning Framework](#7), and [Development and Deployment](#8).

## System Architecture

The rslearn framework consists of four primary subsystems that work together to provide an end-to-end remote sensing machine learning platform:

#### High-Level System Architecture

```mermaid
graph TB
    subgraph "External Data Ecosystem"
        AWS["AWS S3 Buckets<br/>usgs-landsat, sentinel-s2, naip-source"]
        GCP["GCP Public Datasets<br/>gcp-public-data-sentinel-2"]
        ESA["ESA Copernicus<br/>Climate Data Store, OData API"]
        LOCAL["Local File Systems<br/>GeoTIFF, Shapefiles"]
    end
    
    subgraph "rslearn CLI Framework"
        MAIN["rslearn.main:main"]
        DATASET_CLI["dataset commands<br/>add_windows, prepare, ingest, materialize"]
        MODEL_CLI["model commands<br/>fit, validate, test, predict"]
    end
    
    subgraph "Data Management Layer"
        DATASOURCE["DataSource implementations<br/>LandsatOliTirs, Sentinel2, LocalFiles"]
        TILESTORE["TileStore system<br/>DefaultTileStore, TileStoreWithLayer"]
        DATASET["Dataset class<br/>Window management, metadata"]
    end
    
    subgraph "Machine Learning Pipeline"
        DATAMODULE["RslearnDataModule<br/>PyTorch Lightning data loading"]
        LIGHTNING["RslearnLightningModule<br/>Training orchestration"]
        MODELS["Model architectures<br/>SatlasPretrain, UNet, SegmentationHead"]
        WRITER["RslearnWriter<br/>Prediction output handling"]
    end
    
    AWS --> DATASOURCE
    GCP --> DATASOURCE
    ESA --> DATASOURCE
    LOCAL --> DATASOURCE
    
    MAIN --> DATASET_CLI
    MAIN --> MODEL_CLI
    
    DATASET_CLI --> DATASOURCE
    DATASET_CLI --> TILESTORE
    DATASET_CLI --> DATASET
    
    MODEL_CLI --> DATAMODULE
    DATAMODULE --> DATASET
    DATAMODULE --> LIGHTNING
    LIGHTNING --> MODELS
    LIGHTNING --> WRITER
    
    TILESTORE --> DATAMODULE
```

Sources: [pyproject.toml:22-23](), [README.md:1-16](), [extra_requirements.txt:1-22](), [requirements.txt:1-15]()

## Core Workflow and CLI Commands

The rslearn framework operates through a command-line interface that orchestrates data ingestion and model training workflows. The following diagram illustrates the primary CLI commands and their corresponding code execution paths:

#### CLI Command Flow and Code Mapping

```mermaid
graph TD
    ENTRY["rslearn CLI Entry<br/>rslearn.main:main"] --> PARSE["Command parsing and routing"]
    
    PARSE --> DATASET_BRANCH{"Dataset operations"}
    PARSE --> MODEL_BRANCH{"Model operations"}
    
    DATASET_BRANCH --> ADD_WIN["add_windows<br/>Create spatiotemporal windows"]
    DATASET_BRANCH --> PREPARE["prepare<br/>Item discovery from data sources"]
    DATASET_BRANCH --> INGEST["ingest<br/>Data download to TileStore"]
    DATASET_BRANCH --> MATERIALIZE["materialize<br/>Window-aligned data processing"]
    
    MODEL_BRANCH --> FIT["fit<br/>Model training"]
    MODEL_BRANCH --> VALIDATE["validate<br/>Model validation"]
    MODEL_BRANCH --> TEST["test<br/>Model testing"]
    MODEL_BRANCH --> PREDICT["predict<br/>Model inference"]
    
    subgraph "Dataset Processing Pipeline"
        ADD_WIN --> WINDOWS["Window objects<br/>STGeometry, Projection"]
        PREPARE --> ITEMS["WindowLayerData<br/>Item metadata collection"]
        INGEST --> TILES["TileStore population<br/>Raw data storage"]
        MATERIALIZE --> LAYERS["Materialized layers<br/>Window-aligned GeoTIFFs"]
    end
    
    subgraph "ML Training Pipeline"
        FIT --> TRAINER["Lightning Trainer<br/>PyTorch Lightning orchestration"]
        VALIDATE --> TRAINER
        TEST --> TRAINER
        PREDICT --> TRAINER
        TRAINER --> OUTPUTS["Model checkpoints<br/>Prediction outputs"]
    end
    
    LAYERS --> FIT
    LAYERS --> PREDICT
```

Sources: [pyproject.toml:22-23](), [README.md:102-120](), [README.md:320-324]()

## Primary Framework Components

### Data Source Abstraction Layer

rslearn implements a plugin-based data source system that provides uniform access to diverse remote sensing data repositories. The framework supports AWS S3 buckets for Landsat and Sentinel-2 data, Google Cloud Platform public datasets, European Space Agency services, and local file systems.

| Data Source Type | Implementation Class | Primary Use Case |
|------------------|---------------------|------------------|
| AWS Landsat | `LandsatOliTirs` | Landsat 8/9 OLI-TIRS imagery |
| AWS Sentinel-2 | `Sentinel2` | Sentinel-2 L1C/L2A from AWS |
| GCP Sentinel-2 | `Sentinel2` | Sentinel-2 from Google Cloud |
| Climate Data | `ERA5LandMonthlyMeans` | ERA5 climate variables |
| ESA Services | Copernicus implementations | European satellite missions |
| Local Files | `LocalFiles` | Local GeoTIFF and vector files |
| Web Tiles | `XyzTiles` | Mapbox and other tile services |

Sources: [README.md:38-57](), [extra_requirements.txt:3-4](), [extra_requirements.txt:6-8]()

### Dataset Management System

The dataset management subsystem handles spatiotemporal window definitions, metadata storage, and data materialization workflows. Windows represent training examples with specific geographic bounds, temporal ranges, and projection parameters.

#### Dataset Processing Workflow

```mermaid
graph LR
    WINDOWS["Window Definition<br/>STGeometry + temporal bounds"] --> PREPARE_STAGE["prepare<br/>Item discovery"]
    PREPARE_STAGE --> INGEST_STAGE["ingest<br/>Data retrieval"]
    INGEST_STAGE --> MATERIALIZE_STAGE["materialize<br/>Data alignment"]
    
    subgraph "Data Storage"
        TILESTORE_RAW["TileStore<br/>Raw downloaded data"]
        WINDOW_LAYERS["Window layers<br/>Processed GeoTIFFs"]
    end
    
    INGEST_STAGE --> TILESTORE_RAW
    MATERIALIZE_STAGE --> WINDOW_LAYERS
    
    subgraph "Configuration System"
        CONFIG["config.json<br/>Layer definitions and data sources"]
        METADATA["metadata.json<br/>Window options and parameters"]
    end
    
    CONFIG --> PREPARE_STAGE
    METADATA --> WINDOWS
```

Sources: [README.md:98-120](), [README.md:67-89]()

### Machine Learning Framework Integration

rslearn integrates with PyTorch Lightning to provide a standardized training and inference pipeline for remote sensing models. The framework supports various model architectures including foundation models, time series processors, and task-specific heads.

#### ML Pipeline Architecture

```mermaid
graph TB
    subgraph "Data Loading"
        DATASET_OBJ["Dataset object<br/>Window and layer management"]
        DATAMODULE["RslearnDataModule<br/>PyTorch Lightning data interface"]
        MODELDATASET["ModelDataset<br/>Window loading and transforms"]
    end
    
    subgraph "Model Components"
        ENCODER["Encoders<br/>SatlasPretrain, Swin, SAM2"]
        TIMESERIES["SimpleTimeSeries<br/>Temporal aggregation"]
        DECODER["Decoders<br/>UNet, classification heads"]
        TASK["Task implementations<br/>SegmentationTask, etc."]
    end
    
    subgraph "Training Infrastructure"
        LIGHTNING_MOD["RslearnLightningModule<br/>Training orchestration"]
        TRAINER["Lightning Trainer<br/>Training loop management"]
        CALLBACKS["Training callbacks<br/>FreezeUnfreeze, checkpointing"]
    end
    
    subgraph "Output Systems"
        CHECKPOINTS["Model checkpoints<br/>saved model states"]
        PREDICTIONS["RslearnWriter<br/>Prediction output handling"]
        WANDB["Experiment tracking<br/>Weights & Biases integration"]
    end
    
    DATASET_OBJ --> DATAMODULE
    DATAMODULE --> MODELDATASET
    MODELDATASET --> LIGHTNING_MOD
    
    LIGHTNING_MOD --> ENCODER
    ENCODER --> TIMESERIES
    TIMESERIES --> DECODER
    DECODER --> TASK
    
    LIGHTNING_MOD --> TRAINER
    TRAINER --> CALLBACKS
    TRAINER --> CHECKPOINTS
    TRAINER --> PREDICTIONS
    TRAINER --> WANDB
```

Sources: [README.md:214-324](), [extra_requirements.txt:18](), [extra_requirements.txt:21](), [requirements.txt:5]()

## Data Flow and Processing Pipeline

The rslearn framework implements a three-stage data processing pipeline that transforms raw remote sensing data into training-ready formats:

1. **Preparation Stage**: Discovers available data items from configured data sources that intersect with defined spatiotemporal windows
2. **Ingestion Stage**: Downloads raw data to the local TileStore, maintaining original formats and projections
3. **Materialization Stage**: Processes raw data into window-aligned GeoTIFF files with consistent projections and spatial bounds

This pipeline ensures that heterogeneous remote sensing data from multiple sources can be consistently accessed during model training and inference operations.

Sources: [README.md:112-120](), [README.md:200-205]()

## Framework Dependencies and Requirements

rslearn requires Python 3.10 or higher and integrates with several key dependencies for remote sensing and machine learning functionality:

- **Core ML**: PyTorch Lightning for training orchestration, torchvision for computer vision operations
- **Geospatial**: rasterio and fiona for raster/vector data handling, pyproj for coordinate system transformations
- **Cloud Storage**: boto3 for AWS S3 access, gcsfs for Google Cloud Storage
- **Remote Sensing**: earthengine-api for Google Earth Engine, satlaspretrain_models for foundation models
- **Optional**: wandb for experiment tracking, transformers for additional model architectures

Sources: [requirements.txt:1-15](), [extra_requirements.txt:1-22](), [pyproject.toml:14]()

---

