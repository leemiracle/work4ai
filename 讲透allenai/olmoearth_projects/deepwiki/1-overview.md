<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/olmoearth_projects · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Dockerfile](Dockerfile)
- [LICENSE](LICENSE)
- [README.md](README.md)
- [pyproject.toml](pyproject.toml)
- [uv.lock](uv.lock)

</details>



## Purpose and Scope

The `olmoearth_projects` repository contains configuration files, trained model checkpoints, and supporting code for fine-tuned remote sensing models built on the OlmoEarth foundation model. This repository serves as the deployment and application layer for OlmoEarth-based models, providing everything needed to apply pre-trained models to new geographic regions or to reproduce the fine-tuning process for existing models.

This wiki documents the technical infrastructure for applying and fine-tuning OlmoEarth models. For information about the OlmoEarth foundation model architecture and pre-training process, see the [olmoearth_pretrain repository](https://github.com/allenai/olmoearth_pretrain/). For details on the underlying data processing and training framework, see the [rslearn repository](https://github.com/allenai/rslearn/).

**Sources:** [README.md:1-35](), [pyproject.toml:1-11]()

## System Architecture

The `olmoearth_projects` system is built on three primary components that work together to enable model deployment and fine-tuning:

```mermaid
graph TB
    subgraph "Foundation Layer"
        PRETRAIN["olmoearth_pretrain<br/>Pre-trained OlmoEarth Model<br/>OLMOEARTH_V1_BASE"]
    end
    
    subgraph "Framework Layer"
        RSLEARN["rslearn<br/>RslearnLightningModule<br/>RslearnDataModule<br/>Data Acquisition & Training"]
        RUNNER["olmoearth-runner<br/>olmoearth_run Pipeline<br/>Partitioning & Post-processing"]
    end
    
    subgraph "Application Layer - olmoearth_projects"
        CONFIG["Configuration Files<br/>dataset.json<br/>model.yaml<br/>olmoearth_run.yaml"]
        CHECKPOINTS["Model Checkpoints<br/>*.ckpt Files<br/>HuggingFace Hub"]
        DOCS["Documentation<br/>docs/*.md<br/>Usage & Examples"]
        UTILS["Utility Scripts<br/>create_windows_for_lulc.py<br/>Label Quality Tools"]
    end
    
    subgraph "External Dependencies"
        PC["Planetary Computer<br/>Sentinel-1 & Sentinel-2<br/>STAC API"]
        WANDB["Weights & Biases<br/>Training Metrics<br/>Model Logging"]
        GEO["Geospatial Libraries<br/>geopandas<br/>rasterio"]
    end
    
    PRETRAIN --> RSLEARN
    RSLEARN --> CONFIG
    RUNNER --> CONFIG
    
    CONFIG --> CHECKPOINTS
    CONFIG --> DOCS
    CONFIG --> UTILS
    
    RSLEARN --> PC
    RSLEARN --> WANDB
    RSLEARN --> GEO
    RUNNER --> GEO
```

**Sources:** [README.md:25-34](), [pyproject.toml:12-21]()

## Available Fine-tuned Models

This repository provides seven fine-tuned OlmoEarth models for different remote sensing applications:

| Model | Task | Classes/Output | Accuracy | Configuration Path |
|-------|------|----------------|----------|-------------------|
| LFMC | Regression | Live Fuel Moisture Content (%) | Per-pixel MSE | `olmoearth_run_data/lfmc/` |
| Forest Loss Driver | Classification | 10 deforestation causes | 76.1% | `olmoearth_run_data/forest_loss_driver/` |
| Mangrove Extent | Segmentation | 3 classes (mangrove/water/other) | 97.6% | `olmoearth_run_data/mangrove/` |
| Ecosystem Type Mapping | Segmentation | 60 ecosystem types | 64.8% | `olmoearth_run_data/ecosystem_type_mapping/` |
| Nandi Crop Classification | Segmentation | 10 crop/land types | 87.3% | `olmoearth_run_data/nandi/` |
| AWF Land Cover | Segmentation | 9 land cover types | 89.5% | `olmoearth_run_data/awf/` |
| Mozambique LULC | Segmentation | 7 LULC + 7 crop types | Varies by region | `olmoearth_run_data/mozambique_lulc/` |

Each model directory contains three essential configuration files:
- `dataset.json`: Specifies satellite data sources and acquisition parameters
- `model.yaml`: Defines model architecture and training hyperparameters  
- `olmoearth_run.yaml`: Controls inference partitioning and post-processing

**Sources:** [README.md:8-15](), Diagram 3 from high-level architecture

## Component Relationships

The following diagram shows how code entities from different components interact during the model lifecycle:

```mermaid
graph LR
    subgraph "Training Workflow"
        DS_JSON["dataset.json<br/>DataSourceConfig<br/>Sentinel2L2ADataSource"]
        MOD_YAML["model.yaml<br/>OlmoEarthEncoderConfig<br/>SegmentationHead"]
        
        DS_JSON --> RSLEARN_DM["RslearnDataModule<br/>rslearn.data_sources<br/>rslearn.train.lightning_datamodule"]
        MOD_YAML --> RSLEARN_LM["RslearnLightningModule<br/>rslearn.train.lightning_module<br/>FreezeUnfreeze callback"]
        
        RSLEARN_DM --> CKPT["model.ckpt<br/>PyTorch Lightning<br/>Checkpoint"]
        RSLEARN_LM --> CKPT
    end
    
    subgraph "Inference Workflow"
        PRED_GEOJSON["prediction_request_geometry.geojson<br/>FeatureCollection<br/>oe_start_time/oe_end_time"]
        RUN_YAML["olmoearth_run.yaml<br/>PartitioningConfig<br/>PostProcessingConfig"]
        
        PRED_GEOJSON --> OE_RUN["olmoearth_run.main<br/>partition_request_geometry<br/>prepare_window_geometries"]
        RUN_YAML --> OE_RUN
        CKPT --> OE_RUN
        
        OE_RUN --> GEOTIFF["results_raster/*.tif<br/>GeoTIFF Output<br/>Classification/Regression"]
    end
    
    WANDB_VAR["WANDB_PROJECT<br/>WANDB_ENTITY<br/>Environment Variables"] --> RSLEARN_LM
    PC_API["Microsoft Planetary Computer<br/>pystac_client<br/>STAC API"] --> RSLEARN_DM
```

**Sources:** [README.md:62-104](), [README.md:156-185](), [pyproject.toml:12-21]()

## Repository Structure

```mermaid
graph TB
    ROOT["olmoearth_projects/"]
    
    ROOT --> OLMOEARTH_PROJECTS["olmoearth_projects/<br/>Python Package"]
    ROOT --> OLMOEARTH_RUN_DATA["olmoearth_run_data/<br/>Model Configurations"]
    ROOT --> DOCS["docs/<br/>Model Documentation"]
    ROOT --> TESTS["tests/<br/>Unit & Integration Tests"]
    ROOT --> CONFIG_FILES["Configuration<br/>pyproject.toml<br/>uv.lock<br/>Dockerfile"]
    
    OLMOEARTH_PROJECTS --> MAIN["main.py<br/>CLI Entry Point"]
    OLMOEARTH_PROJECTS --> MOZAMBIQUE["mozambique_lulc/<br/>create_windows_for_lulc.py<br/>create_label_raster.py<br/>update_train_test_split.py"]
    OLMOEARTH_PROJECTS --> LABEL_QUALITY["label_quality/<br/>spatial_clustering.py<br/>spatial_extent.py<br/>label_imbalance.py"]
    
    OLMOEARTH_RUN_DATA --> LFMC_CONFIG["lfmc/<br/>dataset.json<br/>model.yaml<br/>olmoearth_run.yaml"]
    OLMOEARTH_RUN_DATA --> FLD_CONFIG["forest_loss_driver/"]
    OLMOEARTH_RUN_DATA --> OTHER_CONFIGS["mangrove/<br/>ecosystem_type_mapping/<br/>nandi/<br/>awf/<br/>mozambique_lulc/"]
    
    DOCS --> MODEL_DOCS["lfmc.md<br/>forest_loss_driver.md<br/>mangrove.md<br/>ecosystem_type_mapping.md<br/>awf.md"]
    DOCS --> TUTORIALS["tutorials/<br/>FinetuneOlmoEarthSegmentation.md"]
```

**Sources:** [README.md:1-190](), [pyproject.toml:45-46]()

## Key Technologies and Dependencies

The system relies on the following core dependencies, as defined in [pyproject.toml:12-21]():

| Dependency | Version | Purpose |
|------------|---------|---------|
| `rslearn[extra]` | ≥0.0.18 | Framework for satellite data acquisition, model training, and fine-tuning |
| `olmoearth-runner` | ≥0.1.10 | High-level inference pipeline with partitioning and post-processing |
| `olmoearth_pretrain` | Latest | OlmoEarth foundation model architecture and pre-trained weights |
| `geopandas` | ≥1.1.1 | Geospatial data manipulation and coordinate transformations |
| `wandb` | ≥0.21 | Experiment tracking and metric logging |
| `PyYAML` | ≥6 | Configuration file parsing |
| `python-dotenv` | ≥1.0 | Environment variable management |

Python 3.11+ is required as specified in [pyproject.toml:10](). The system uses `uv` for fast, deterministic dependency resolution with locked versions in [uv.lock:1-3]().

**Sources:** [pyproject.toml:10-21](), [README.md:36-47]()

## Development and Deployment Infrastructure

The repository supports both local development and containerized deployment:

```mermaid
graph TB
    subgraph "Local Development"
        UV["uv Package Manager<br/>uv sync<br/>uv.lock"]
        VENV[".venv/<br/>Virtual Environment<br/>Python 3.11+"]
        UV --> VENV
    end
    
    subgraph "Container Deployment"
        DOCKERFILE["Dockerfile<br/>pytorch/pytorch:2.7.0<br/>cuda12.8-cudnn9"]
        UV_COPY["Copy uv binary<br/>ghcr.io/astral-sh/uv"]
        DOCKERFILE --> UV_COPY
        UV_COPY --> CONTAINER_VENV["Container .venv<br/>uv sync --all-extras"]
    end
    
    subgraph "CI/CD"
        GITHUB_ACTIONS["GitHub Actions<br/>.github/workflows"]
        GITHUB_ACTIONS --> DOCKERFILE
    end
    
    subgraph "Testing Infrastructure"
        PYTEST["pytest<br/>pytest.ini_options<br/>--import-mode=importlib"]
        TESTS_DIR["tests/<br/>Unit Tests<br/>Integration Tests"]
        PYTEST --> TESTS_DIR
    end
    
    VENV --> TESTS_DIR
    CONTAINER_VENV --> TESTS_DIR
```

The [Dockerfile:1-19]() uses PyTorch 2.7.0 with CUDA 12.8 support and installs dependencies via `uv` for reproducible builds. Testing is configured in [pyproject.toml:60-66]() to use the `importlib` import mode.

**Sources:** [Dockerfile:1-19](), [pyproject.toml:60-66](), [README.md:36-47]()

## Usage Workflows

The repository supports two primary workflows:

### Inference Workflow

```mermaid
sequenceDiagram
    participant User
    participant Config as "Configuration Files"
    participant OE_Run as "olmoearth_run"
    participant PC as "Planetary Computer"
    participant Model as "Model Checkpoint"
    
    User->>Config: Create prediction_request_geometry.geojson
    User->>OE_Run: python -m olmoearth_projects.main olmoearth_run
    OE_Run->>Config: Load dataset.json, model.yaml, olmoearth_run.yaml
    OE_Run->>PC: Query Sentinel-1/2 imagery
    PC-->>OE_Run: Return satellite data
    OE_Run->>Model: Load checkpoint (*.ckpt)
    OE_Run->>OE_Run: partition_request_geometry()
    OE_Run->>OE_Run: prepare_window_geometries()
    OE_Run->>OE_Run: Run inference
    OE_Run->>OE_Run: process_window(), process_partition(), process_dataset()
    OE_Run->>User: Generate GeoTIFF outputs
```

**Sources:** [README.md:49-140]()

### Training Workflow

```mermaid
sequenceDiagram
    participant User
    participant Dataset as "Training Dataset"
    participant Config as "model.yaml"
    participant RSLearn as "rslearn"
    participant WandB as "Weights & Biases"
    
    User->>Dataset: Download & extract dataset.tar
    User->>Config: Set DATASET_PATH, NUM_WORKERS, WANDB_*
    User->>RSLearn: rslearn model fit --config model.yaml
    RSLearn->>Config: Parse OlmoEarthEncoderConfig, SegmentationHead
    RSLearn->>Dataset: Load training windows
    RSLearn->>RSLearn: RslearnDataModule initialization
    RSLearn->>RSLearn: RslearnLightningModule with FreezeUnfreeze
    loop Training Epochs
        RSLearn->>WandB: Log metrics and losses
        RSLearn->>RSLearn: Save checkpoints (last.ckpt, best)
    end
    RSLearn->>User: Training complete
```

**Sources:** [README.md:142-186]()

## License

The repository is licensed under the [OlmoEarth Artifact License](LICENSE), which permits use, reproduction, modification, and distribution with specific restrictions on military/defense applications and extractive activities. See [LICENSE:1-128]() for complete terms.

**Sources:** [LICENSE:1-128](), [README.md:187-189]()

---

