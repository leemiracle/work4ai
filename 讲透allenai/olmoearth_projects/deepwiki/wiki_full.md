# Page: Overview

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

# Page: Getting Started

# Getting Started

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Dockerfile](Dockerfile)
- [LICENSE](LICENSE)
- [README.md](README.md)
- [pyproject.toml](pyproject.toml)
- [uv.lock](uv.lock)

</details>



This page guides you through installing the olmoearth_projects repository, setting up your development environment, and preparing your system for basic usage. This covers dependency management with `uv`, Docker containerization, and environment configuration needed to apply existing models or develop new ones.

For information about the overall system architecture, see [System Architecture](#3). For details on running inference with trained models, see [Inference and Deployment](#7). For model training procedures, see [Model Training](#5).

---

## Prerequisites

Before installing olmoearth_projects, ensure your system meets the following requirements:

| Requirement | Specification | Purpose |
|------------|---------------|----------|
| Python Version | ≥ 3.11 | Required by project dependencies |
| Operating System | Linux, macOS, or Windows | Cross-platform support |
| Disk Space | ≥ 10 GB | For dependencies and model checkpoints |
| GPU (Optional) | CUDA-compatible | For model training and inference |
| Git | Any recent version | For cloning the repository |

**Sources:** [pyproject.toml:10](), [Dockerfile:1]()

---

## Installation Methods

The repository supports two primary installation methods: local installation using `uv` (recommended for development) and Docker containerization (recommended for reproducible environments).

### Installation Flow

```mermaid
graph TB
    START["User"] --> CHOICE{"Installation Method?"}
    
    CHOICE -->|"Development/Local"| UV_PATH["UV Installation Path"]
    CHOICE -->|"Production/Reproducible"| DOCKER_PATH["Docker Installation Path"]
    
    UV_PATH --> INSTALL_UV["Install uv<br/>curl -LsSf https://astral.sh/uv/install.sh | sh"]
    INSTALL_UV --> CLONE_UV["git clone https://github.com/allenai/olmoearth_projects.git"]
    CLONE_UV --> CD_UV["cd olmoearth_projects"]
    CD_UV --> SYNC_UV["uv sync<br/>(reads pyproject.toml, uv.lock)"]
    SYNC_UV --> ACTIVATE["source .venv/bin/activate"]
    ACTIVATE --> VERIFY_UV["Verify Installation"]
    
    DOCKER_PATH --> BUILD_ARG["Set GITHUB_TOKEN<br/>build argument"]
    BUILD_ARG --> DOCKER_BUILD["docker build<br/>-t olmoearth_projects<br/>--build-arg GITHUB_TOKEN=..."]
    DOCKER_BUILD --> DOCKER_RUN["docker run<br/>-v /path/to/data:/data<br/>olmoearth_projects"]
    DOCKER_RUN --> VERIFY_DOCKER["Verify Installation"]
    
    VERIFY_UV --> COMPLETE["Installation Complete"]
    VERIFY_DOCKER --> COMPLETE
```

**Sources:** [README.md:36-47](), [Dockerfile:1-19]()

---

## Local Installation with uv

The `uv` package manager provides fast, reliable dependency resolution with lock file support.

### Step 1: Install uv

```bash
# Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Step 2: Clone and Set Up the Repository

```bash
git clone https://github.com/allenai/olmoearth_projects.git
cd olmoearth_projects
uv sync
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate  # Windows
```

The `uv sync` command reads [pyproject.toml:1-67]() and [uv.lock:1-21]() to install all dependencies into a virtual environment at `.venv/`.

### Dependency Structure

```mermaid
graph TB
    subgraph "Core Dependencies"
        PYPROJECT["pyproject.toml<br/>Project Definition"]
        UVLOCK["uv.lock<br/>Locked Versions"]
    end
    
    subgraph "Required Packages"
        GEOPANDAS["geopandas>=1.1.1<br/>Geospatial Data"]
        RSLEARN["rslearn[extra]>=0.0.18<br/>Training Framework"]
        OLMOEARTH_RUNNER["olmoearth-runner>=0.1.10<br/>Inference Pipeline"]
        OLMOEARTH_PRETRAIN["olmoearth_pretrain<br/>Base Model"]
        WANDB["wandb>=0.21<br/>Experiment Tracking"]
        PYYAML["PyYAML>=6<br/>Config Parsing"]
        DOTENV["python-dotenv>=1.0<br/>Environment Variables"]
        OPENPYXL["openpyxl>=3.1.5<br/>Excel Support"]
    end
    
    subgraph "Development Dependencies"
        PYTEST["pytest>=8.2"]
        RUFF["ruff>=0.7"]
        MYPY["mypy>=1.17.1"]
        PRECOMMIT["pre-commit>=4.3.0"]
        INTERROGATE["interrogate>=1.7.0"]
    end
    
    PYPROJECT --> GEOPANDAS
    PYPROJECT --> RSLEARN
    PYPROJECT --> OLMOEARTH_RUNNER
    PYPROJECT --> OLMOEARTH_PRETRAIN
    PYPROJECT --> WANDB
    PYPROJECT --> PYYAML
    PYPROJECT --> DOTENV
    PYPROJECT --> OPENPYXL
    
    PYPROJECT -.->|"optional-dependencies.dev"| PYTEST
    PYPROJECT -.->|"optional-dependencies.dev"| RUFF
    PYPROJECT -.->|"optional-dependencies.dev"| MYPY
    PYPROJECT -.->|"optional-dependencies.dev"| PRECOMMIT
    PYPROJECT -.->|"optional-dependencies.dev"| INTERROGATE
    
    UVLOCK --> PYPROJECT
```

**Sources:** [pyproject.toml:12-21](), [pyproject.toml:24-34](), [README.md:38-47]()

---

## Docker Installation

Docker provides a containerized environment with all dependencies pre-configured, including PyTorch with CUDA support.

### Step 1: Build the Docker Image

```bash
docker build -t olmoearth_projects \
  --build-arg GITHUB_TOKEN=your_token_here \
  .
```

The `GITHUB_TOKEN` build argument is required for accessing private Git repositories during the build process (see [Dockerfile:5-6]()).

### Step 2: Run the Container

```bash
docker run -it \
  -v $PWD/project_data:/project_data \
  -v $PWD/checkpoints:/checkpoints \
  olmoearth_projects \
  bash
```

### Docker Environment Structure

```mermaid
graph TB
    subgraph "Base Image"
        PYTORCH["pytorch/pytorch:2.7.0<br/>-cuda12.8-cudnn9-runtime"]
    end
    
    subgraph "System Setup"
        GIT["git<br/>(apt-get install)"]
        GITCONFIG["git config<br/>--global url"]
        UV_BINARY["/usr/local/bin/uv<br/>(copied from ghcr.io/astral-sh/uv)"]
    end
    
    subgraph "Application Setup"
        WORKDIR["/olmoearth_projects<br/>(WORKDIR)"]
        PYPROJECT_COPY["pyproject.toml<br/>(COPY)"]
        UVLOCK_COPY["uv.lock<br/>(COPY)"]
        UV_SYNC_1["uv sync --all-extras<br/>--no-install-project"]
        CODE_COPY["./<br/>(COPY all code)"]
        UV_SYNC_2["uv sync --all-extras<br/>--locked"]
    end
    
    subgraph "Runtime Environment"
        PATH_ENV["PATH=/olmoearth_projects/.venv/bin:$PATH"]
        VENV[".venv/<br/>(virtual environment)"]
    end
    
    PYTORCH --> GIT
    GIT --> GITCONFIG
    GITCONFIG --> UV_BINARY
    UV_BINARY --> WORKDIR
    WORKDIR --> PYPROJECT_COPY
    PYPROJECT_COPY --> UVLOCK_COPY
    UVLOCK_COPY --> UV_SYNC_1
    UV_SYNC_1 --> CODE_COPY
    CODE_COPY --> UV_SYNC_2
    UV_SYNC_2 --> PATH_ENV
    PATH_ENV --> VENV
```

**Sources:** [Dockerfile:1-19]()

---

## Environment Configuration

After installation, configure environment variables required by the system. These variables control training behavior, inference settings, and integration with external services.

### Required Environment Variables

Create a `.env` file in the repository root or export variables in your shell:

```bash
# Data and Output Paths
export DATASET_PATH=/path/to/your/dataset/
export TRAINER_DATA_PATH=./trainer_data
export PREDICTION_OUTPUT_LAYER=output

# Processing Configuration
export NUM_WORKERS=32

# Weights & Biases Integration
export WANDB_PROJECT=olmoearth_projects
export WANDB_NAME=my_experiment_name
export WANDB_ENTITY=your_wandb_username

# Optional: Microsoft Planetary Computer
export PC_SDK_SUBSCRIPTION_KEY=your_key_here
```

### Environment Variable Reference

| Variable | Purpose | Default/Example | Required By |
|----------|---------|-----------------|-------------|
| `DATASET_PATH` | Path to rslearn dataset directory | `/path/to/dataset/` | Training, Inference |
| `TRAINER_DATA_PATH` | Output directory for checkpoints | `./trainer_data` | Training |
| `NUM_WORKERS` | Number of data loading workers | `32` | Training, Inference |
| `WANDB_PROJECT` | W&B project name | `olmoearth_projects` | Training (if using W&B) |
| `WANDB_NAME` | W&B run name | `my_run` | Training (if using W&B) |
| `WANDB_ENTITY` | W&B username or team | - | Training (if using W&B) |
| `PREDICTION_OUTPUT_LAYER` | Output layer name for inference | `output` | Inference |
| `PC_SDK_SUBSCRIPTION_KEY` | Planetary Computer API key | - | Data Download (optional) |

**Sources:** [README.md:118-123](), [README.md:156-166]()

---

## Verifying Installation

After completing installation, verify that all components are correctly configured.

### Verification Commands

```bash
# Check Python version
python --version  # Should be >= 3.11

# Verify core packages
python -c "import rslearn; print(rslearn.__version__)"
python -c "import olmoearth_pretrain; print('OlmoEarth pretrain loaded')"
python -c "import olmoearth_run; print('olmoearth_run loaded')"
python -c "import geopandas; print('geopandas loaded')"

# Verify rslearn CLI
rslearn --help

# Verify olmoearth_projects module
python -c "import olmoearth_projects; print('Module loaded successfully')"
```

### Expected Output Structure

```mermaid
graph LR
    INSTALL["Completed Installation"] --> IMPORT_TEST["Import Tests"]
    IMPORT_TEST --> RSLEARN_OK["✓ rslearn imported"]
    IMPORT_TEST --> OLMOEARTH_OK["✓ olmoearth_pretrain imported"]
    IMPORT_TEST --> RUNNER_OK["✓ olmoearth_run imported"]
    IMPORT_TEST --> GEOPANDAS_OK["✓ geopandas imported"]
    
    RSLEARN_OK --> CLI_TEST["CLI Tests"]
    CLI_TEST --> RSLEARN_CLI["✓ rslearn --help works"]
    
    RUNNER_OK --> MODULE_TEST["Module Tests"]
    MODULE_TEST --> OLMOEARTH_PROJECTS["✓ olmoearth_projects imports"]
    
    OLMOEARTH_PROJECTS --> READY["System Ready"]
```

**Sources:** [pyproject.toml:12-21]()

---

## Directory Structure

After installation, your working directory should have the following structure:

```
olmoearth_projects/
├── .venv/                          # Virtual environment (uv installation)
├── olmoearth_projects/             # Python package source code
├── olmoearth_run_data/             # Model configurations
│   ├── lfmc/
│   │   ├── dataset.json
│   │   ├── model.yaml
│   │   └── olmoearth_run.yaml
│   ├── forest_loss_driver/
│   ├── mangrove/
│   └── ...
├── tests/                          # Test suite
├── pyproject.toml                  # Project definition
├── uv.lock                         # Locked dependencies
├── Dockerfile                      # Container definition
├── README.md                       # Main documentation
└── LICENSE                         # OlmoEarth Artifact License
```

### User-Created Directories

During usage, you will create additional directories:

```
olmoearth_projects/
├── checkpoints/                    # Downloaded model checkpoints
│   └── lfmc.ckpt
├── project_data/                   # Inference scratch space
│   └── lfmc/
│       ├── dataset/                # rslearn dataset
│       ├── windows/                # Partitioned windows
│       └── results/                # Output GeoTIFFs
└── trainer_data/                   # Training outputs
    ├── last.ckpt                   # Latest checkpoint
    └── epoch=X.ckpt                # Best checkpoint
```

**Sources:** [README.md:62-73](), [README.md:129](), [README.md:176-177]()

---

## Basic Usage Patterns

Once installed and configured, the repository supports three primary usage patterns:

### Pattern 1: Applying Existing Models (Inference)

```bash
# Download a model checkpoint
mkdir ./checkpoints
wget https://huggingface.co/allenai/OlmoEarth-v1-FT-LFMC-Base/resolve/main/model.ckpt \
  -O checkpoints/lfmc.ckpt

# Set environment variables
export NUM_WORKERS=32
export WANDB_PROJECT=lfmc_inference

# Run inference
mkdir ./project_data
python -m olmoearth_projects.main olmoearth_run olmoearth_run \
  --config_path $PWD/olmoearth_run_data/lfmc/ \
  --checkpoint_path $PWD/checkpoints/lfmc.ckpt \
  --scratch_path project_data/lfmc/
```

### Pattern 2: Fine-tuning Models

```bash
# Download training dataset
wget https://huggingface.co/datasets/allenai/olmoearth_projects_lfmc/blob/main/dataset.tar
tar xvf dataset.tar

# Set environment variables
export DATASET_PATH=/path/to/extracted/dataset/
export TRAINER_DATA_PATH=./trainer_data
export WANDB_PROJECT=olmoearth_projects
export WANDB_NAME=my_training_run

# Start training
rslearn model fit --config olmoearth_run_data/lfmc/model.yaml
```

### Pattern 3: Resuming Training

```bash
# Resume from last checkpoint
rslearn model fit \
  --config olmoearth_run_data/lfmc/model.yaml \
  --ckpt_path $TRAINER_DATA_PATH/last.ckpt
```

### Usage Flow

```mermaid
graph TB
    START["Installation Complete"] --> CHOICE{"Usage Pattern?"}
    
    CHOICE -->|"Apply Existing Model"| DOWNLOAD_CKPT["Download Checkpoint<br/>(wget from HuggingFace)"]
    CHOICE -->|"Train New Model"| DOWNLOAD_DATA["Download Training Data<br/>(wget dataset.tar)"]
    CHOICE -->|"Resume Training"| CHECK_CKPT["Locate last.ckpt<br/>in TRAINER_DATA_PATH"]
    
    DOWNLOAD_CKPT --> SET_ENV_INFER["Set Environment<br/>NUM_WORKERS, WANDB_*"]
    SET_ENV_INFER --> RUN_OLMOEARTH_RUN["python -m olmoearth_projects.main<br/>olmoearth_run olmoearth_run<br/>--config_path<br/>--checkpoint_path<br/>--scratch_path"]
    RUN_OLMOEARTH_RUN --> VISUALIZE["Visualize Results<br/>(qgis, GIS tools)"]
    
    DOWNLOAD_DATA --> EXTRACT["tar xvf dataset.tar"]
    EXTRACT --> SET_ENV_TRAIN["Set Environment<br/>DATASET_PATH<br/>TRAINER_DATA_PATH<br/>WANDB_*"]
    SET_ENV_TRAIN --> RUN_RSLEARN_FIT["rslearn model fit<br/>--config model.yaml"]
    RUN_RSLEARN_FIT --> MONITOR["Monitor W&B<br/>Checkpoints saved to<br/>TRAINER_DATA_PATH"]
    
    CHECK_CKPT --> SET_ENV_RESUME["Set Environment<br/>(same as training)"]
    SET_ENV_RESUME --> RUN_RSLEARN_RESUME["rslearn model fit<br/>--config model.yaml<br/>--ckpt_path last.ckpt"]
    RUN_RSLEARN_RESUME --> MONITOR
    
    VISUALIZE --> COMPLETE["Workflow Complete"]
    MONITOR --> COMPLETE
```

**Sources:** [README.md:49-140](), [README.md:143-185]()

---

## Next Steps

After completing installation and verification:

1. **Review Model Documentation:** Explore available models and their specific requirements in [Available Models](#6)
2. **Understand the Architecture:** Learn how components interact in [System Architecture](#3)
3. **Run Inference:** Follow detailed inference procedures in [Inference and Deployment](#7)
4. **Train Models:** Review training workflows in [Model Training](#5)
5. **Process Data:** Understand data preparation in [Data Processing Pipeline](#4)

**Sources:** [README.md:1-190]()

---

# Page: System Architecture

# System Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Dockerfile](Dockerfile)
- [olmoearth_run_data/mozambique_lulc/README.md](olmoearth_run_data/mozambique_lulc/README.md)
- [olmoearth_run_data/mozambique_lulc/config.json](olmoearth_run_data/mozambique_lulc/config.json)
- [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml](olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml)
- [olmoearth_run_data/mozambique_lulc/rslp_finetuning_croptype.yaml](olmoearth_run_data/mozambique_lulc/rslp_finetuning_croptype.yaml)
- [olmoearth_run_data/mozambique_lulc/rslp_finetuning_croptype_in_season_novmar.yaml](olmoearth_run_data/mozambique_lulc/rslp_finetuning_croptype_in_season_novmar.yaml)
- [olmoearth_run_data/mozambique_lulc/rslp_finetuning_in_season_novmar.yaml](olmoearth_run_data/mozambique_lulc/rslp_finetuning_in_season_novmar.yaml)
- [pyproject.toml](pyproject.toml)
- [uv.lock](uv.lock)

</details>



## Purpose and Scope

This document describes the high-level architecture of the olmoearth_projects system, explaining how the major components interact to enable fine-tuning OlmoEarth foundation models for remote sensing applications and deploying them for inference. The architecture encompasses data processing, model training, inference execution, and storage management.

For detailed information about specific subsystems, see:
- Data processing workflow: [Data Processing Pipeline](#4)
- Model training procedures: [Model Training](#5)
- Inference execution: [Inference and Deployment](#7)
- Development practices: [Development Guide](#9)

## System Overview

The olmoearth_projects system is organized into four primary architectural layers that work together to support the complete lifecycle of remote sensing model development and deployment:

```mermaid
graph TB
    subgraph Layer1["Data Processing Layer"]
        GPKGFiles["GPKG Files<br/>(Field Survey Data)"]
        CreateWindows["create_windows_for_lulc.py<br/>Window Generation"]
        CreateLabels["create_label_raster.py<br/>Point to Raster Conversion"]
        LabelQuality["check_label_quality.py<br/>Quality Assessment"]
        DataSplit["update_train_test_split.py<br/>SpatialDataSplitter"]
    end
    
    subgraph Layer2["Training Layer"]
        RslearnLightningModule["rslearn.train.lightning_module<br/>RslearnLightningModule"]
        RslearnDataModule["rslearn.train.data_module<br/>RslearnDataModule"]
        MultiTaskModel["rslearn.models.multitask<br/>MultiTaskModel"]
        OlmoEarth["rslearn.models.olmoearth_pretrain<br/>OlmoEarth Encoder"]
        FreezeUnfreeze["rslearn.train.callbacks<br/>FreezeUnfreeze"]
    end
    
    subgraph Layer3["Inference Layer"]
        OlmoEarthRunner["olmoearth-runner<br/>Pipeline Executor"]
        GridPartitioner["GridPartitioner<br/>Spatial Tiling"]
        CombineGeotiff["CombineGeotiff<br/>Result Aggregation"]
        PlanetaryComputer["Planetary Computer<br/>Data Acquisition"]
    end
    
    subgraph Layer4["Storage & Distribution"]
        WekaStorage["/weka/dfive-default/<br/>Datasets & Checkpoints"]
        HuggingFace["HuggingFace Hub<br/>allenai Organization"]
        OlmoEarthStudio["olmoearth.allenai.org<br/>Interactive Inference"]
    end
    
    GPKGFiles --> CreateWindows
    CreateWindows --> CreateLabels
    CreateLabels --> DataSplit
    DataSplit --> LabelQuality
    LabelQuality --> RslearnDataModule
    
    RslearnDataModule --> RslearnLightningModule
    MultiTaskModel --> RslearnLightningModule
    OlmoEarth --> MultiTaskModel
    FreezeUnfreeze --> RslearnLightningModule
    
    RslearnLightningModule --> WekaStorage
    WekaStorage --> OlmoEarthRunner
    GridPartitioner --> OlmoEarthRunner
    CombineGeotiff --> OlmoEarthRunner
    PlanetaryComputer --> OlmoEarthRunner
    
    WekaStorage --> HuggingFace
    WekaStorage --> OlmoEarthStudio
```

**Sources:** [pyproject.toml](), [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml](), Diagram 1 and 2 from high-level architecture

## Core Components

### Training System Architecture

The training system is built on the rslearn framework and uses PyTorch Lightning for distributed training. The architecture follows a modular design with clear separation between data loading, model definition, and training orchestration.

```mermaid
graph TB
    subgraph ConfigFiles["Configuration Files"]
        ModelYAML["model.yaml<br/>class_path: RslearnLightningModule<br/>encoder: OlmoEarth<br/>decoders: SegmentationHead"]
        DatasetJSON["dataset.json<br/>inputs: sentinel2_l2a, label<br/>task: SegmentationTask"]
        TrainerYAML["trainer section<br/>callbacks: ModelCheckpoint,<br/>FreezeUnfreeze"]
    end
    
    subgraph LightningModule["rslearn.train.lightning_module"]
        RLM["RslearnLightningModule<br/>init_args:<br/>- model: MultiTaskModel<br/>- lr: 0.0001<br/>- scheduler: PlateauScheduler"]
    end
    
    subgraph ModelArch["Model Architecture"]
        MTM["MultiTaskModel<br/>encoder: List[OlmoEarth]<br/>decoders: Dict[str, List]<br/>loss_weights: Optional"]
        OE["OlmoEarth<br/>checkpoint_path: /weka/.../step667200<br/>patch_size: 4<br/>autocast_dtype: bfloat16"]
        Decoder["Decoder Stack:<br/>1. Upsample (scale=4)<br/>2. Conv (768→8 channels)<br/>3. PickFeatures<br/>4. SegmentationHead"]
    end
    
    subgraph DataModule["rslearn.train.data_module"]
        RDM["RslearnDataModule<br/>path: /weka/.../datasets<br/>batch_size: 64<br/>num_workers: 32"]
        Transforms["Transforms:<br/>- Pad (size=31)<br/>- Crop (size=16)<br/>- Flip<br/>- OlmoEarthNormalize"]
    end
    
    subgraph TaskDef["Task Definition"]
        MT["MultiTask<br/>tasks: {segment: SegmentationTask}"]
        ST["SegmentationTask<br/>num_classes: 8<br/>zero_is_invalid: true<br/>metrics: precision, recall"]
    end
    
    subgraph Callbacks["Training Callbacks"]
        MC["ModelCheckpoint<br/>monitor: val_segment/accuracy<br/>save_top_k: 1"]
        FU["FreezeUnfreeze<br/>module_selector: [model,encoder,0]<br/>unfreeze_at_epoch: 20<br/>unfreeze_lr_factor: 10"]
        LRM["LearningRateMonitor<br/>logging_interval: epoch"]
    end
    
    ModelYAML --> RLM
    DatasetJSON --> RDM
    TrainerYAML --> Callbacks
    
    RLM --> MTM
    MTM --> OE
    MTM --> Decoder
    
    RDM --> Transforms
    RDM --> MT
    MT --> ST
    
    Callbacks --> RLM
```

**Sources:** [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:1-268](), Diagram 2 from high-level architecture

#### Model Configuration Structure

The training configuration follows a hierarchical YAML structure defined in files like `rslp_finetuning.yaml`. Key configuration sections:

| Section | Purpose | Key Parameters |
|---------|---------|----------------|
| `model.init_args.model.encoder` | Defines the OlmoEarth pre-trained encoder | `checkpoint_path`, `patch_size: 4`, `autocast_dtype: bfloat16` |
| `model.init_args.model.decoders` | Task-specific decoder heads | `Upsample`, `Conv`, `SegmentationHead` |
| `model.init_args.lr` | Learning rate configuration | Base: `0.0001`, Unfrozen: `0.001` (10x) |
| `model.init_args.scheduler` | Learning rate scheduling | `PlateauScheduler` with `factor: 0.2`, `patience: 2` |
| `data.init_args.inputs` | Input data specifications | `sentinel2_l2a` (12 bands), `label` (targets) |
| `data.init_args.task` | Task definition | `SegmentationTask` with `num_classes: 8` |
| `trainer.callbacks` | Training callbacks | `FreezeUnfreeze`, `ModelCheckpoint`, `LearningRateMonitor` |

**Sources:** [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:1-268]()

### Inference System Architecture

The inference system uses the `olmoearth-runner` package to execute predictions over large geographic areas. It implements a hierarchical partitioning strategy to process data efficiently.

```mermaid
graph TB
    subgraph RequestDef["Inference Request Definition"]
        ReqGeom["prediction_request_geometry.geojson<br/>type: Polygon<br/>properties:<br/>- oe_start_time<br/>- oe_end_time"]
        RunYAML["olmoearth_run.yaml<br/>partitioning:<br/>- coarse_partition_size<br/>- window_size<br/>post_processing: CombineGeotiff"]
    end
    
    subgraph Partitioning["Partitioning Stage"]
        P1["partition_request_geometry<br/>GridPartitioner<br/>Coarse grid: 0.1-1.0 degrees"]
        P2["prepare_window_geometries<br/>GridPartitioner<br/>Fine grid: 32-1024 pixels<br/>Projection: EPSG:3857 or UTM"]
    end
    
    subgraph DataAcq["Data Acquisition"]
        PC["PlanetaryComputer<br/>Collection: sentinel-2-l2a<br/>query_config:<br/>- period_duration: 30d<br/>- max_matches: 8<br/>- space_mode: PER_PERIOD_MOSAIC"]
        Mosaic["Temporal Mosaicking<br/>6-12 timesteps<br/>Harmonization enabled"]
    end
    
    subgraph ModelExec["Model Execution"]
        LoadCkpt["Load Checkpoint<br/>OlmoEarth + SegmentationHead<br/>From: /weka/.../checkpoints"]
        Transform["Data Transforms<br/>OlmoEarthNormalize<br/>Patch generation<br/>overlap_ratio: 0.25"]
        Predict["Inference Batch Processing<br/>Per-window predictions<br/>Overlap handling"]
    end
    
    subgraph PostProc["Post-processing"]
        WinProc["process_window<br/>Window-level processing<br/>NoopRaster or custom"]
        PartProc["process_partition<br/>CombineGeotiff<br/>Merge partition tiles"]
        DSProc["process_dataset<br/>CombineGeotiff<br/>Final output assembly"]
    end
    
    subgraph Output["Output Generation"]
        GeoTIFF["Results GeoTIFF<br/>Classification/Regression<br/>10m resolution<br/>CRS: EPSG:3857 or UTM"]
        Metadata["Inference Metadata<br/>classification_field<br/>class_name_mapping<br/>color_mapping"]
    end
    
    ReqGeom --> P1
    RunYAML --> P1
    P1 --> P2
    P2 --> PC
    
    PC --> Mosaic
    Mosaic --> LoadCkpt
    LoadCkpt --> Transform
    Transform --> Predict
    
    Predict --> WinProc
    WinProc --> PartProc
    PartProc --> DSProc
    
    DSProc --> GeoTIFF
    RunYAML --> Metadata
    Metadata --> GeoTIFF
```

**Sources:** [olmoearth_run_data/mozambique_lulc/config.json](), Diagram 4 from high-level architecture

### Data Processing Pipeline Components

The data processing system transforms raw field survey data (GPKG files) into training-ready datasets through a series of Python scripts.

```mermaid
graph LR
    subgraph Input["Input Data"]
        GPKG["GPKG Files<br/>Field survey points<br/>Provinces: gaza, manica, zambezia<br/>Attributes: class labels"]
    end
    
    subgraph WindowGen["olmoearth_projects/projects/<br/>mozambique_lulc/"]
        CW["create_windows_for_lulc.py<br/>--gpkg_dir<br/>--ds_path<br/>--window_size 32<br/>--crop_type (optional)"]
        CLR["create_label_raster.py<br/>--ds_path<br/>Convert point labels to rasters"]
        UTS["update_train_test_split.py<br/>SpatialDataSplitter<br/>val_ratio: 0.1<br/>Group by province"]
    end
    
    subgraph QualityCheck["olmoearth_projects/utils/"]
        CLQ["check_label_quality.py<br/>--ds_path<br/>--split train/val/test<br/>--crop_type (optional)"]
        SC["spatial_clustering.py<br/>Compute clustering F1 scores<br/>KMeans clustering"]
        SE["spatial_extent.py<br/>Calculate geographic spread<br/>Convex hull analysis"]
        LI["label_imbalance.py<br/>Class distribution metrics"]
    end
    
    subgraph DatasetPrep["rslearn Dataset Preparation"]
        Config["config.json<br/>layers: sentinel2, label<br/>data_source: PlanetaryComputer<br/>tile_store: file"]
        Prepare["rslearn dataset prepare<br/>--root $DATASET_PATH<br/>--workers 64"]
        Materialize["rslp launch_data_materialization_jobs<br/>Parallel data loading<br/>num_jobs: 5"]
    end
    
    subgraph Output["Dataset Output"]
        DSPath["/weka/dfive-default/rslearn-eai/<br/>datasets/crop/mozambique_lulc/<br/>- items.jsonl<br/>- tiles/<br/>- label_raster/"]
    end
    
    GPKG --> CW
    CW --> CLR
    CLR --> UTS
    UTS --> CLQ
    
    CLQ --> SC
    CLQ --> SE
    CLQ --> LI
    
    Config --> Prepare
    UTS --> Prepare
    Prepare --> Materialize
    Materialize --> DSPath
```

**Sources:** [olmoearth_run_data/mozambique_lulc/README.md:14-37](), [olmoearth_run_data/mozambique_lulc/config.json]()

## Configuration System

The system uses three primary configuration formats to define different aspects of the pipeline:

### YAML Configuration Hierarchy

Training configuration in `rslp_finetuning.yaml` follows this structure:

```yaml
model:
  class_path: rslearn.train.lightning_module.RslearnLightningModule
  init_args:
    model:
      class_path: rslearn.models.multitask.MultiTaskModel
      init_args:
        encoder: [OlmoEarth configuration]
        decoders: {segment: [Upsample, Conv, SegmentationHead]}
    lr: 0.0001
    scheduler: {PlateauScheduler configuration}

data:
  class_path: rslearn.train.data_module.RslearnDataModule
  init_args:
    path: /weka/dfive-default/rslearn-eai/datasets/...
    inputs: {sentinel2_l2a, label specifications}
    task: {MultiTask with SegmentationTask}
    batch_size: 64
    transforms: [Pad, Crop, Flip, OlmoEarthNormalize]

trainer:
  max_epochs: 100
  callbacks: [LearningRateMonitor, ModelCheckpoint, FreezeUnfreeze]
```

**Sources:** [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:1-268]()

### JSON Dataset Configuration

The `config.json` file defines data sources and layer specifications:

```json
{
  "layers": {
    "sentinel2": {
      "type": "raster",
      "data_source": {
        "name": "rslearn.data_sources.planetary_computer.Sentinel2",
        "query_config": {
          "max_matches": 8,
          "period_duration": "30d",
          "space_mode": "PER_PERIOD_MOSAIC"
        }
      }
    },
    "label_raster": {
      "type": "raster",
      "band_sets": [{"bands": ["label"], "dtype": "int32"}]
    }
  }
}
```

**Sources:** [olmoearth_run_data/mozambique_lulc/config.json:1-70]()

## Storage and Distribution Architecture

```mermaid
graph TB
    subgraph WEKAStorage["/weka/dfive-default/"]
        Datasets["/rslearn-eai/datasets/<br/>- mozambique_lulc/20251202<br/>- nandi/<br/>- mangrove/<br/>items.jsonl + tiles/"]
        Checkpoints["/helios/checkpoints/<br/>joer/phase2.0_base_lr0.0001_wd0.02/<br/>step667200/<br/>OlmoEarth foundation"]
        ProjectCkpts["/rslearn-eai/<br/>checkpoints/2025_09_18_*/<br/>Fine-tuned model weights"]
    end
    
    subgraph PublicDist["Public Distribution"]
        HF["HuggingFace Hub<br/>allenai organization<br/>Model checkpoints:<br/>- OlmoEarth-v1-FT-*-Base"]
        GCS["Google Cloud Storage<br/>Public data buckets<br/>Large dataset downloads"]
    end
    
    subgraph Deployment["Deployment Targets"]
        Studio["OlmoEarth Studio<br/>olmoearth.allenai.org<br/>Interactive inference UI<br/>Model selection dropdown"]
    end
    
    Checkpoints --> ProjectCkpts
    ProjectCkpts --> HF
    Datasets --> GCS
    HF --> Studio
```

**Sources:** [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:10](), Diagram 1 from high-level architecture

## Component Interaction Flows

### Training Execution Flow

```mermaid
sequenceDiagram
    participant User
    participant RSLP as rslp.main
    participant Beaker as Beaker Cluster
    participant RLM as RslearnLightningModule
    participant RDM as RslearnDataModule
    participant MTM as MultiTaskModel
    participant WEKA as WEKA Storage
    
    User->>RSLP: launch_finetune<br/>--config_paths rslp_finetuning.yaml<br/>--cluster ai2/saturn
    RSLP->>Beaker: Submit training job<br/>with GPU resources
    Beaker->>RLM: Initialize from YAML<br/>model, lr, scheduler
    Beaker->>RDM: Initialize from YAML<br/>path, inputs, task, transforms
    RDM->>WEKA: Load dataset<br/>items.jsonl + tiles/
    RLM->>MTM: Build model<br/>OlmoEarth + decoders
    
    loop Training Epochs
        RDM->>RLM: Batch data<br/>sentinel2_l2a + labels
        RLM->>MTM: Forward pass
        MTM->>RLM: Loss calculation
        Note over RLM: Epoch 20: FreezeUnfreeze<br/>unfreezes encoder<br/>lr *= 10
        RLM->>WEKA: Save checkpoint<br/>if val_segment/accuracy improves
    end
    
    WEKA->>User: Training complete<br/>checkpoint path
```

**Sources:** [olmoearth_run_data/mozambique_lulc/README.md:119-123](), [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:261-265]()

### Inference Execution Flow

```mermaid
sequenceDiagram
    participant User
    participant Runner as olmoearth-runner
    participant Grid as GridPartitioner
    participant PC as PlanetaryComputer
    participant Model as OlmoEarth + Decoder
    participant PP as Post-processor
    
    User->>Runner: Execute inference<br/>prediction_request_geometry.geojson<br/>olmoearth_run.yaml
    Runner->>Grid: partition_request_geometry<br/>Coarse grid (0.1-1.0°)
    
    loop For each coarse partition
        Grid->>Grid: prepare_window_geometries<br/>Fine grid (32-1024px)
        
        loop For each window
            Grid->>PC: Query Sentinel-2<br/>time range, bbox
            PC->>Grid: Return imagery<br/>8 timesteps, 12 bands
            Grid->>Model: Load checkpoint + predict<br/>OlmoEarthNormalize applied
            Model->>Grid: Per-pixel predictions<br/>class probabilities/values
            Grid->>PP: process_window<br/>NoopRaster or custom
        end
        
        PP->>PP: process_partition<br/>CombineGeotiff
    end
    
    PP->>PP: process_dataset<br/>CombineGeotiff final merge
    PP->>User: Results GeoTIFF<br/>+ metadata JSON
```

**Sources:** Diagram 4 from high-level architecture, [olmoearth_run_data/mozambique_lulc/config.json:54-59]()

## Dependency Management

The system uses `uv` for fast, reproducible dependency management as defined in [pyproject.toml]():

| Package | Version | Purpose |
|---------|---------|---------|
| `rslearn[extra]` | >=0.0.18 | Core training framework, data loading, transforms |
| `olmoearth-runner` | >=0.1.10 | Inference pipeline execution |
| `olmoearth_pretrain` | - | OlmoEarth encoder model definitions |
| `geopandas` | >=1.1.1 | Geospatial vector data processing |
| `wandb` | >=0.21 | Training metrics logging |
| `PyYAML` | >=6 | Configuration file parsing |

The Docker container [Dockerfile:1-19]() is built on `pytorch/pytorch:2.7.0-cuda12.8-cudnn9-runtime` and uses `uv sync` to install all dependencies in a virtual environment at `/olmoearth_projects/.venv`.

**Sources:** [pyproject.toml:12-21](), [Dockerfile:1-19](), [uv.lock:1-21]()

## Key Implementation Details

### OlmoEarth Encoder Initialization

The encoder is loaded from a checkpoint at `/weka/dfive-default/helios/checkpoints/joer/phase2.0_base_lr0.0001_wd0.02/step667200` with these parameters:

- **selector**: `["encoder"]` - extracts only encoder weights
- **patch_size**: `4` - spatial patch size for vision transformer
- **random_initialization**: `false` - uses pre-trained weights
- **autocast_dtype**: `bfloat16` - mixed precision training
- **embedding_size**: `null` - uses default 768 dimensions

**Sources:** [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:8-16]()

### Segmentation Decoder Architecture

The decoder transforms encoder outputs (768 channels) to class predictions through:

1. **Upsample** - `scale_factor: 4`, `mode: bilinear` - upsamples from patch resolution to pixel resolution
2. **Conv** - `in_channels: 768`, `out_channels: 8`, `kernel_size: 1` - 1x1 convolution for classification
3. **PickFeatures** - `indexes: [0]`, `collapse: true` - extracts first feature map
4. **SegmentationHead** - applies softmax and computes segmentation metrics

**Sources:** [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:17-38]()

### FreezeUnfreeze Training Strategy

The `FreezeUnfreeze` callback implements progressive unfreezing:

- **module_selector**: `["model", "encoder", 0]` - selects first encoder in model
- **unfreeze_at_epoch**: `20` - encoder frozen for first 20 epochs
- **unfreeze_lr_factor**: `10` - learning rate boosted 10x when unfrozen (0.0001 → 0.001)

This allows the decoder to train on frozen encoder features initially, then fine-tunes the entire model with a higher learning rate for the encoder.

**Sources:** [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:261-265]()

### Planetary Computer Data Query

Sentinel-2 data acquisition uses these query parameters in [config.json:54-59]():

- **max_matches**: `8` - retrieve 8 images per time period
- **min_matches**: `8` - ensure 8 images available
- **period_duration**: `"30d"` - 30-day temporal windows
- **space_mode**: `"PER_PERIOD_MOSAIC"` - mosaic all images within each period
- **harmonize**: `true` - apply harmonization for consistency across sensors

This creates temporal sequences of 6-12 timesteps (depending on date range) with consistent radiometry.

**Sources:** [olmoearth_run_data/mozambique_lulc/config.json:54-61]()

---

# Page: Data Processing Pipeline

# Data Processing Pipeline

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/build-test.yml](.github/workflows/build-test.yml)
- [olmoearth_projects/projects/mozambique_lulc/__init__.py](olmoearth_projects/projects/mozambique_lulc/__init__.py)
- [olmoearth_projects/projects/mozambique_lulc/create_label_raster.py](olmoearth_projects/projects/mozambique_lulc/create_label_raster.py)
- [olmoearth_projects/projects/mozambique_lulc/create_windows_for_lulc.py](olmoearth_projects/projects/mozambique_lulc/create_windows_for_lulc.py)
- [olmoearth_projects/projects/mozambique_lulc/update_train_test_split.py](olmoearth_projects/projects/mozambique_lulc/update_train_test_split.py)
- [olmoearth_projects/utils/label_quality/__init__.py](olmoearth_projects/utils/label_quality/__init__.py)
- [olmoearth_run_data/mozambique_lulc/prediction_request_geometry.geojson](olmoearth_run_data/mozambique_lulc/prediction_request_geometry.geojson)
- [tests/unit/utils/label_quality/test_wrapper.py](tests/unit/utils/label_quality/test_wrapper.py)

</details>



The Data Processing Pipeline transforms raw geospatial annotations into training-ready datasets for OlmoEarth model fine-tuning. This pipeline handles window generation, label conversion, spatial splitting, and quality validation. The output is an rslearn `Dataset` with properly formatted windows, projections, and metadata ready for training with the rslearn framework.

For information about model training with these datasets, see [Model Training](#5). For inference using trained models, see [Inference and Deployment](#7).

## Overview

The data processing workflow consists of four primary stages executed sequentially:

```mermaid
graph LR
    subgraph "Stage 1: Window Creation"
        GPKG["GPKG Files<br/>Point/Polygon Labels"]
        CREATE_WIN["create_windows_for_lulc.py<br/>calculate_bounds()<br/>create_window()"]
        WINDOWS["Window Objects<br/>window.json<br/>label/ layer"]
    end
    
    subgraph "Stage 2: Label Rasterization"
        RASTERIZE["create_label_raster.py<br/>create_label_raster()"]
        LABEL_RASTER["label_raster/<br/>GeoTIFF with<br/>class_id values"]
    end
    
    subgraph "Stage 3: Split Management"
        UPDATE_SPLIT["update_train_test_split.py<br/>SpatialDataSplitter<br/>RandomDataSplitter"]
        SPLITS["Updated Splits<br/>train/val/test<br/>in window.options"]
    end
    
    subgraph "Stage 4: Quality Assessment"
        QA["check_label_quality()<br/>spatial_clustering()<br/>label_imbalance()<br/>spatial_extent()"]
        REPORT["Quality Metrics<br/>F1 scores<br/>Class balance<br/>Coverage area"]
    end
    
    GPKG --> CREATE_WIN
    CREATE_WIN --> WINDOWS
    WINDOWS --> RASTERIZE
    RASTERIZE --> LABEL_RASTER
    LABEL_RASTER --> UPDATE_SPLIT
    UPDATE_SPLIT --> SPLITS
    SPLITS --> QA
    QA --> REPORT
```

**Sources:** [olmoearth_projects/projects/mozambique_lulc/create_windows_for_lulc.py](), [olmoearth_projects/projects/mozambique_lulc/create_label_raster.py](), [olmoearth_projects/projects/mozambique_lulc/update_train_test_split.py](), [olmoearth_projects/utils/label_quality/__init__.py]()

## Input Data Format

The pipeline accepts GeoPackage (`.gpkg`) files containing labeled geographic features. Input files must conform to specific column requirements:

| Model Type | Required Columns | Label Column Type | Example Values |
|------------|------------------|-------------------|----------------|
| LULC Classification | `class`, `geometry` | `int` | 0-6 (Water, Bare Ground, Rangeland, etc.) |
| Crop Type Classification | `crop1`, `geometry` | `str` | "corn", "cassava", "rice", "sesame", etc. |

The `geometry` column contains either Point or Polygon features in any valid CRS. The pipeline automatically converts all geometries to WGS84 (EPSG:4326) before processing. For Polygon features, centroids are computed and used as the window center points.

**Sources:** [olmoearth_projects/projects/mozambique_lulc/create_windows_for_lulc.py:110-145]()

## Window Generation Process

### Coordinate Transformation and Projection

The `create_windows_for_lulc.py` script generates training windows through a multi-step coordinate transformation:

```mermaid
graph TB
    subgraph "Transformation Pipeline"
        WGS84["WGS84 Point<br/>(longitude, latitude)<br/>EPSG:4326"]
        STGEOM["STGeometry<br/>WGS84_PROJECTION<br/>shapely.Point"]
        UTM["UTM/UPS Projection<br/>get_utm_ups_crs()<br/>10m resolution"]
        PROJECTED["Projected Point<br/>Integer coordinates<br/>dst_geometry"]
        BOUNDS["Window Bounds<br/>calculate_bounds()<br/>(min_x, min_y, max_x, max_y)"]
    end
    
    WGS84 --> STGEOM
    STGEOM --> UTM
    UTM --> PROJECTED
    PROJECTED --> BOUNDS
```

The transformation uses `get_utm_ups_crs()` from rslearn to determine the appropriate UTM zone based on the point's longitude and latitude. All windows are generated at 10-meter resolution as defined by `WINDOW_RESOLUTION = 10` [olmoearth_projects/projects/mozambique_lulc/create_windows_for_lulc.py:26]().

**Sources:** [olmoearth_projects/projects/mozambique_lulc/create_windows_for_lulc.py:77-107, 170-176]()

### Window Bounds Calculation

The `calculate_bounds()` function computes pixel bounds around a projected point. For a window of size `N` pixels:

- **Even size**: Center pixel at `(x, y)` creates bounds `[x - N/2, y - N/2, x + N/2, y + N/2]`
- **Odd size**: Center pixel at `(x, y)` creates bounds `[x - N/2, y - N/2 - 1, x + N/2 + 1, y + N/2]`

The asymmetry for odd-sized windows ensures the center pixel is consistently positioned [olmoearth_projects/projects/mozambique_lulc/create_windows_for_lulc.py:89-105]().

**Sources:** [olmoearth_projects/projects/mozambique_lulc/create_windows_for_lulc.py:77-107]()

### Window Creation and Storage

Each window is created as a `Window` object with comprehensive metadata:

```mermaid
graph TB
    subgraph "Window Structure"
        WIN["Window Object"]
        PATH["path: dataset/group/window_name/"]
        PROJ["projection: Projection(UTM, 10m)"]
        BOUNDS["bounds: (min_x, min_y, max_x, max_y)"]
        TIME["time_range: (start_time, end_time)"]
        OPTIONS["options:<br/>split: train/val/test<br/>category_id: int<br/>category: str<br/>fid: unique_id<br/>source: gpkg"]
    end
    
    subgraph "Layers"
        LABEL_LAYER["label/<br/>features.geojson<br/>Vector layer"]
        LABEL_RASTER_LAYER["label_raster/<br/>GeoTIFF<br/>Raster layer"]
    end
    
    WIN --> PATH
    WIN --> PROJ
    WIN --> BOUNDS
    WIN --> TIME
    WIN --> OPTIONS
    WIN --> LABEL_LAYER
    WIN --> LABEL_RASTER_LAYER
```

The `create_window()` function performs the following operations:

1. Creates `Window` object with projection, bounds, and time range
2. Saves window metadata to `window.json`
3. Creates a vector `Feature` with window geometry and label properties
4. Encodes feature to `label/` layer using `GeojsonVectorFormat`
5. Marks layer as completed

**Sources:** [olmoearth_projects/projects/mozambique_lulc/create_windows_for_lulc.py:147-216]()

### Group Organization and Temporal Coverage

Windows are organized by `group`, which corresponds to geographic regions or provinces. Each group has defined temporal coverage:

| Group | Start Time | End Time | Purpose |
|-------|-----------|----------|---------|
| `gaza` | 2024-10-23 | 2025-06-20 | Gaza province LULC |
| `manica` | 2024-10-23 | 2025-06-20 | Manica province LULC |
| `zambezia` | 2024-10-23 | 2025-06-20 | Zambezia province LULC |
| `crop_type` | 2024-10-23 | 2025-06-20 | All provinces combined |

The `GROUP_TIME` dictionary [olmoearth_projects/projects/mozambique_lulc/create_windows_for_lulc.py:54-74]() defines these temporal ranges, which are used to query satellite imagery during training and inference.

**Sources:** [olmoearth_projects/projects/mozambique_lulc/create_windows_for_lulc.py:54-74, 177-195]()

### Parallel Processing

The window creation process uses multiprocessing for efficiency:

```mermaid
graph LR
    RECORDS["Point Records<br/>iter_points()"]
    JOBS["Job Specifications<br/>dict per record"]
    POOL["multiprocessing.Pool<br/>star_imap_unordered"]
    WORKERS["Worker Processes<br/>create_window()"]
    PROGRESS["tqdm Progress<br/>Bar"]
    
    RECORDS --> JOBS
    JOBS --> POOL
    POOL --> WORKERS
    WORKERS --> PROGRESS
```

The `create_windows_from_gpkg()` function creates a job specification for each point, then dispatches jobs to a worker pool [olmoearth_projects/projects/mozambique_lulc/create_windows_for_lulc.py:237-265](). The default is 32 workers, configurable via `--max_workers`.

**Sources:** [olmoearth_projects/projects/mozambique_lulc/create_windows_for_lulc.py:218-266]()

## Label Raster Generation

After vector label layers are created, the `create_label_raster.py` script converts them to raster format for efficient training:

### Rasterization Process

```mermaid
graph TB
    VECTOR["label/<br/>GeojsonVectorFormat<br/>decode_vector()"]
    EXTRACT["Extract Properties<br/>category or category_id"]
    LOOKUP["Class Name → ID<br/>LULC_CLASS_NAMES<br/>CROPTYPE_CLASS_NAMES"]
    ARRAY["NumPy Array<br/>zeros(1, H, W)<br/>dtype=uint8"]
    CENTER["Set Center Pixel<br/>raster[:, H//2, W//2] = class_id"]
    ENCODE["GeotiffRasterFormat<br/>encode_raster()"]
    OUTPUT["label_raster/<br/>label.tif"]
    
    VECTOR --> EXTRACT
    EXTRACT --> LOOKUP
    LOOKUP --> ARRAY
    ARRAY --> CENTER
    CENTER --> ENCODE
    ENCODE --> OUTPUT
```

The `create_label_raster()` function performs the following:

1. Decodes vector features from `label/` directory
2. Extracts class name from feature properties
3. Maps class name to integer ID using `LULC_CLASS_NAMES` or `CROPTYPE_CLASS_NAMES`
4. Creates a zero-filled raster matching window dimensions
5. Sets the center pixel to the class ID value
6. Encodes raster as GeoTIFF in `label_raster/` directory

This creates a single-pixel label in the center of each window [olmoearth_projects/projects/mozambique_lulc/create_label_raster.py:54-76]().

**Sources:** [olmoearth_projects/projects/mozambique_lulc/create_label_raster.py:54-76]()

### Class Mapping

Two class mapping schemes are defined:

**LULC Classes** [olmoearth_projects/projects/mozambique_lulc/create_label_raster.py:30-39]():
```
0: invalid
1: Water
2: Bare Ground
3: Rangeland
4: Flooded Vegetation
5: Trees
6: Cropland
7: Buildings
```

**Crop Type Classes** [olmoearth_projects/projects/mozambique_lulc/create_label_raster.py:40-49]():
```
0: invalid
1: corn
2: cassava
3: rice
4: sesame
5: beans
6: millet
7: sorghum
```

The class ID of 0 is reserved for "invalid" to represent unlabeled pixels or regions outside the label area.

**Sources:** [olmoearth_projects/projects/mozambique_lulc/create_label_raster.py:30-49]()

## Data Splitting Strategies

The `update_train_test_split.py` script manages the assignment of windows to train, validation, and test splits using pluggable splitting strategies.

### Splitting Architecture

```mermaid
graph TB
    subgraph "Data Splitter Interface"
        INTERFACE["DataSplitterInterface<br/>choose_split_for_window()"]
    end
    
    subgraph "Implementations"
        SPATIAL["SpatialDataSplitter<br/>Grid-based partitioning<br/>grid_size=32"]
        RANDOM["RandomDataSplitter<br/>Random assignment<br/>train_prop=0.9"]
    end
    
    subgraph "Split Assignment"
        WINDOW["Window Objects<br/>Load from Dataset"]
        CHECK["Filter windows<br/>split in [train, val]"]
        ASSIGN["splitter.choose_split_for_window()"]
        UPDATE["window.options['split']<br/>window.save()"]
    end
    
    INTERFACE --> SPATIAL
    INTERFACE --> RANDOM
    SPATIAL --> ASSIGN
    RANDOM --> ASSIGN
    WINDOW --> CHECK
    CHECK --> ASSIGN
    ASSIGN --> UPDATE
```

**Sources:** [olmoearth_projects/projects/mozambique_lulc/update_train_test_split.py]()

### SpatialDataSplitter

The `SpatialDataSplitter` partitions windows based on spatial clustering to minimize spatial autocorrelation between splits. Configuration:

- `train_prop=0.9`: 90% of data for training
- `val_prop=0.1`: 10% of data for validation
- `test_prop=0.0`: 0% for test (test split comes from separate GPKG files)
- `grid_size=32`: Spatial grid resolution for clustering

This strategy ensures that nearby windows are assigned to the same split, preventing information leakage from spatially correlated features [olmoearth_projects/projects/mozambique_lulc/update_train_test_split.py:55-58]().

**Sources:** [olmoearth_projects/projects/mozambique_lulc/update_train_test_split.py:55-58]()

### RandomDataSplitter

The `RandomDataSplitter` assigns windows randomly according to specified proportions:

- `train_prop=0.9`: 90% training
- `val_prop=0.1`: 10% validation
- `test_prop=0.0`: 0% test

Random splitting is simpler but may result in spatially nearby windows appearing in different splits [olmoearth_projects/projects/mozambique_lulc/update_train_test_split.py:59-60]().

**Sources:** [olmoearth_projects/projects/mozambique_lulc/update_train_test_split.py:59-60]()

### Split Update Process

The `update_train_val_split()` function only modifies windows that are currently marked as `train` or `val`:

```python
if window.options["split"] in ["train", "val"]:
    split = splitter.choose_split_for_window(window)
    window.options["split"] = split
    window.save()
```

Windows marked as `test` (from test GPKG files) are never modified [olmoearth_projects/projects/mozambique_lulc/update_train_test_split.py:22-28]().

**Sources:** [olmoearth_projects/projects/mozambique_lulc/update_train_test_split.py:22-28]()

## Label Quality Assessment

The `label_quality` module provides utilities to validate dataset quality before training. The `check_label_quality()` function runs three distinct quality checks:

```mermaid
graph TB
    subgraph "Input"
        GDF["GeoDataFrame<br/>label column<br/>geometry column"]
    end
    
    subgraph "Quality Checks"
        CHECK1["spatial_clustering()<br/>Compute clustering F1<br/>per class"]
        CHECK2["label_imbalance()<br/>Compute class counts<br/>percentages"]
        CHECK3["spatial_extent()<br/>Compute bounding box<br/>coverage area"]
    end
    
    subgraph "Output"
        TABLE["Rich Table<br/>Check name | Metric | Value"]
        CONSOLE["Console Output<br/>Formatted display"]
    end
    
    GDF --> CHECK1
    GDF --> CHECK2
    GDF --> CHECK3
    CHECK1 --> TABLE
    CHECK2 --> TABLE
    CHECK3 --> TABLE
    TABLE --> CONSOLE
```

**Sources:** [olmoearth_projects/utils/label_quality/__init__.py:14-61]()

### Spatial Clustering Metric

The `spatial_clustering()` check computes an F1 score measuring whether spatially proximate labels belong to the same class. High F1 scores (close to 1.0) indicate strong spatial clustering, which is common in remote sensing data where similar land cover types occur in contiguous regions.

This metric helps identify:
- Annotation inconsistencies where nearby areas have conflicting labels
- Spatially scattered minority classes that may be difficult to learn
- Dataset suitability for spatial splitting strategies

**Sources:** [olmoearth_projects/utils/label_quality/__init__.py:9-10, 32-34]()

### Label Imbalance Metric

The `label_imbalance()` check computes class frequency statistics:

| Metric | Description |
|--------|-------------|
| Class counts | Number of instances per class |
| Class percentages | Proportion of total instances |
| Imbalance ratio | Ratio of most to least frequent class |

Severe imbalance (e.g., 100:1 ratio) may require:
- Class-weighted loss functions
- Oversampling minority classes
- Stratified data splitting

**Sources:** [olmoearth_projects/utils/label_quality/__init__.py:9, 32-34]()

### Spatial Extent Metric

The `spatial_extent()` check computes the geographic coverage:

- Bounding box coordinates (min/max longitude, min/max latitude)
- Total area in square degrees
- Geographic span

This helps verify:
- Dataset covers the intended region
- Labels are not concentrated in a small subregion
- No outlier points in incorrect locations

**Sources:** [olmoearth_projects/utils/label_quality/__init__.py:11, 32-34]()

### Running Quality Checks

The `check_label_quality()` function accepts a `checks_to_run` parameter to selectively execute checks:

```python
check_label_quality(gdf, checks_to_run=["label_imbalance"])
```

If `checks_to_run` is `None`, all three checks execute. Results are displayed in a formatted Rich table to the console [olmoearth_projects/utils/label_quality/__init__.py:46-60]().

**Sources:** [olmoearth_projects/utils/label_quality/__init__.py:14-61](), [tests/unit/utils/label_quality/test_wrapper.py:7-22]()

## Output Dataset Structure

The complete pipeline produces an rslearn `Dataset` with the following directory structure:

```
dataset_root/
├── config.json                          # Dataset configuration
├── {group}/                             # e.g., "gaza", "manica", "zambezia"
│   ├── {window_name}/                   # e.g., "123_-25.140374_33.664738"
│   │   ├── window.json                  # Window metadata
│   │   ├── label/                       # Vector label layer
│   │   │   └── features.geojson
│   │   ├── label_raster/                # Raster label layer
│   │   │   └── label.tif
│   │   └── .completed/                  # Layer completion markers
│   │       ├── label
│   │       └── label_raster
```

Each `window.json` contains:
- `projection`: UTM/UPS CRS with 10m resolution
- `bounds`: Integer pixel coordinates
- `time_range`: Start and end datetime in UTC
- `options`: Split assignment, category ID, category name, FID, source

The dataset is ready for use with `RslearnDataModule` for model training. See [Data Module and Transforms](#5.4) for details on loading and transforming this data during training.

**Sources:** [olmoearth_projects/projects/mozambique_lulc/create_windows_for_lulc.py:182-215](), [olmoearth_projects/projects/mozambique_lulc/create_label_raster.py:54-76]()

## Command-Line Usage

### Creating Windows

```bash
python -m olmoearth_projects.projects.mozambique_lulc.create_windows_for_lulc \
  --gpkg_dir /path/to/gpkg/files \
  --ds_path /path/to/output/dataset \
  --window_size 1 \
  --max_workers 32
```

For crop type datasets, add `--crop_type` flag [olmoearth_projects/projects/mozambique_lulc/create_windows_for_lulc.py:296]().

**Sources:** [olmoearth_projects/projects/mozambique_lulc/create_windows_for_lulc.py:268-337]()

### Creating Label Rasters

```bash
python -m olmoearth_projects.projects.mozambique_lulc.create_label_raster \
  --ds_path /path/to/dataset \
  --workers 64
```

For crop type datasets, add `--crop_type` flag [olmoearth_projects/projects/mozambique_lulc/create_label_raster.py:94]().

**Sources:** [olmoearth_projects/projects/mozambique_lulc/create_label_raster.py:79-109]()

### Updating Splits

```bash
python -m olmoearth_projects.projects.mozambique_lulc.update_train_test_split \
  --ds_path /path/to/dataset \
  --workers 32 \
  --splitter spatial
```

The `--splitter` argument accepts `spatial` or `random` [olmoearth_projects/projects/mozambique_lulc/update_train_test_split.py:47-65]().

**Sources:** [olmoearth_projects/projects/mozambique_lulc/update_train_test_split.py:31-85]()

## Integration with Training Pipeline

The datasets produced by this pipeline are consumed by the training system through the `dataset.json` configuration file, which specifies:

- Data sources (Sentinel-2, Sentinel-1)
- Label layer names (`label` or `label_raster`)
- Temporal parameters for satellite data queries
- Band configurations and data types

For complete training configuration details, see [Training Configuration Files](#5.1) and [Data Module and Transforms](#5.4).

**Sources:** [olmoearth_projects/projects/mozambique_lulc/create_label_raster.py:1-17]()

---

# Page: Creating Training Windows

# Creating Training Windows

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [olmoearth_projects/projects/mozambique_lulc/__init__.py](olmoearth_projects/projects/mozambique_lulc/__init__.py)
- [olmoearth_projects/projects/mozambique_lulc/create_label_raster.py](olmoearth_projects/projects/mozambique_lulc/create_label_raster.py)
- [olmoearth_projects/projects/mozambique_lulc/create_windows_for_lulc.py](olmoearth_projects/projects/mozambique_lulc/create_windows_for_lulc.py)
- [olmoearth_projects/projects/mozambique_lulc/update_train_test_split.py](olmoearth_projects/projects/mozambique_lulc/update_train_test_split.py)
- [olmoearth_run_data/mozambique_lulc/README.md](olmoearth_run_data/mozambique_lulc/README.md)
- [olmoearth_run_data/mozambique_lulc/config.json](olmoearth_run_data/mozambique_lulc/config.json)
- [olmoearth_run_data/mozambique_lulc/prediction_request_geometry.geojson](olmoearth_run_data/mozambique_lulc/prediction_request_geometry.geojson)

</details>



## Purpose and Scope

This page documents the process of creating training windows from raw geospatial annotation files (GPKG format). Training windows are the fundamental data units used in the rslearn framework for model training. Each window represents a spatially and temporally bounded region with associated labels.

This page covers the window creation workflow, coordinate transformations, label layer generation, and data organization strategies. For information about assessing the quality of generated windows, see [Label Quality Assessment](#4.2). For details on managing train/validation/test splits after window creation, see [Data Splitting and Organization](#4.3). For using these windows in model training, see [Model Training](#5).

## Overview

The window creation process transforms raw point or polygon annotations stored in GPKG files into structured training windows ready for model training. Each window is a georeferenced image patch with associated label data, organized into groups (typically provinces or regions) and splits (train/val/test).

The primary implementation is in [olmoearth_projects/projects/mozambique_lulc/create_windows_for_lulc.py:1-339]().

### Window Creation Workflow

```mermaid
graph TB
    GPKG["GPKG File(s)<br/>Point/Polygon Geometries<br/>Class Annotations"]
    
    ProcessGPKG["process_gpkg()<br/>Normalize to WGS84<br/>Validate columns"]
    
    IterPoints["iter_points()<br/>Extract centroids<br/>Yield (fid, lat, lon, category)"]
    
    CreateWindow["create_window()<br/>Per annotation"]
    
    CalcBounds["calculate_bounds()<br/>Compute pixel bounds"]
    
    Projection["UTM/UPS Projection<br/>get_utm_ups_crs()<br/>10m resolution"]
    
    WindowObj["Window object<br/>STGeometry<br/>Projection<br/>Bounds<br/>Time range<br/>Options"]
    
    SpatialSplit["SpatialDataSplitter<br/>choose_split_for_window()<br/>Train/Val split"]
    
    LabelVector["Label Layer (Vector)<br/>GeojsonVectorFormat<br/>Feature with properties"]
    
    WindowSave["Window.save()<br/>Persist metadata"]
    
    GPKG --> ProcessGPKG
    ProcessGPKG --> IterPoints
    IterPoints --> CreateWindow
    
    CreateWindow --> CalcBounds
    CreateWindow --> Projection
    CalcBounds --> WindowObj
    Projection --> WindowObj
    
    WindowObj --> SpatialSplit
    SpatialSplit --> WindowSave
    WindowObj --> LabelVector
    LabelVector --> WindowSave
    
    style ProcessGPKG fill:#f9f9f9
    style CreateWindow fill:#f9f9f9
    style WindowObj fill:#f0f0f0
```

**Diagram: Window Creation Pipeline**

This diagram shows the core functions and data transformations in the window creation process. The `process_gpkg()` function normalizes input data, `iter_points()` extracts point geometries, and `create_window()` orchestrates the creation of each training window with appropriate projections and splits.

Sources: [olmoearth_projects/projects/mozambique_lulc/create_windows_for_lulc.py:110-339]()

## Input Data Format

### GPKG File Structure

Training windows are created from GPKG (GeoPackage) files containing point or polygon annotations. The expected structure varies by task:

| Task Type | Required Column | Data Type | Description |
|-----------|----------------|-----------|-------------|
| LULC Classification | `class` | integer | Class ID (0-6) |
| Crop Type Classification | `crop1` | string | Crop name |
| Both | `geometry` | Point/Polygon | Spatial geometry |

The system supports multiple provinces/regions organized by filename:

```
gpkg_dir/
├── gaza_train.gpkg
├── gaza_test.gpkg
├── manica_train.gpkg
├── manica_test.gpkg
├── zambezia_train.gpkg
├── zambezia_test.gpkg
└── training_gaza_zambezia_manica.gpkg  # for crop type
```

Sources: [olmoearth_projects/projects/mozambique_lulc/create_windows_for_lulc.py:110-145](), [olmoearth_run_data/mozambique_lulc/README.md:7-14]()

### Class Mappings

Two classification schemes are supported with predefined class mappings:

**LULC Classes:**
```python
CLASS_MAP = {
    0: "Water",
    1: "Bare Ground",
    2: "Rangeland",
    3: "Flooded Vegetation",
    4: "Trees",
    5: "Cropland",
    6: "Buildings",
}
```

**Crop Type Classes:**
```python
CROP_TYPE_MAP = {
    "corn": 0,
    "cassava": 1,
    "rice": 2,
    "sesame": 3,
    "beans": 4,
    "millet": 5,
    "sorghum": 6,
}
```

Sources: [olmoearth_projects/projects/mozambique_lulc/create_windows_for_lulc.py:29-50]()

## Window Generation Process

### Coordinate Transformation

The window creation process involves transforming geographic coordinates (WGS84) to projected coordinates (UTM/UPS) to create pixel-aligned windows:

```mermaid
graph LR
    WGS84["Point in WGS84<br/>(longitude, latitude)"]
    
    STGeom["STGeometry<br/>WGS84_PROJECTION<br/>shapely.Point"]
    
    UTMCRS["get_utm_ups_crs()<br/>Determine UTM zone<br/>based on lon/lat"]
    
    DstProj["Projection<br/>UTM/UPS CRS<br/>10m, -10m resolution"]
    
    Transform["to_projection()<br/>Reproject to UTM"]
    
    ProjGeom["STGeometry (projected)<br/>Pixel coordinates<br/>(x, y) in meters"]
    
    WGS84 --> STGeom
    STGeom --> UTMCRS
    UTMCRS --> DstProj
    STGeom --> Transform
    DstProj --> Transform
    Transform --> ProjGeom
    
    style STGeom fill:#f9f9f9
    style Transform fill:#f9f9f9
```

**Diagram: Coordinate Transformation Workflow**

The transformation uses `get_utm_ups_crs()` from rslearn to automatically select the appropriate UTM or UPS zone based on the point's location, ensuring minimal distortion.

Sources: [olmoearth_projects/projects/mozambique_lulc/create_windows_for_lulc.py:170-176]()

### Window Size and Bounds Calculation

Windows are created with a configurable size (default 32 pixels) centered on the annotation point:

```python
def calculate_bounds(
    geometry: STGeometry, window_size: int
) -> tuple[int, int, int, int]:
    """Calculate the bounds of a window around a geometry.
    
    Returns (left, top, right, bottom) in projected coordinates.
    """
```

For even window sizes (e.g., 32):
- `left = x - window_size // 2`
- `top = y - window_size // 2`
- `right = x + window_size // 2`
- `bottom = y + window_size // 2`

For odd window sizes, an asymmetric adjustment is applied to the top bound.

At 10m resolution, a 32-pixel window covers 320m × 320m on the ground, providing sufficient spatial context around each annotation point.

Sources: [olmoearth_projects/projects/mozambique_lulc/create_windows_for_lulc.py:77-107]()

## Window Structure and Metadata

### Window Object Composition

Each `Window` object contains comprehensive metadata:

```mermaid
graph TB
    subgraph "Window Object"
        Path["path<br/>Dataset root + group + name"]
        Group["group<br/>Province or 'crop_type'"]
        Name["name<br/>'fid_lat_lon'"]
        Projection["projection<br/>UTM/UPS CRS + resolution"]
        Bounds["bounds<br/>(left, top, right, bottom)"]
        TimeRange["time_range<br/>(start_time, end_time)"]
        Options["options<br/>split, category_id,<br/>category, fid, source"]
    end
    
    subgraph "Layers"
        LabelLayer["'label' layer<br/>GeojsonVectorFormat<br/>Feature with properties"]
        LabelRaster["'label_raster' layer<br/>GeotiffRasterFormat<br/>Created post-processing"]
        Sentinel2["'sentinel2' layer<br/>Fetched during training"]
    end
    
    Path -.-> LabelLayer
    Path -.-> LabelRaster
    
    style Options fill:#f0f0f0
    style LabelLayer fill:#f9f9f9
```

**Diagram: Window Object Structure**

The `Window` object encapsulates all spatial, temporal, and metadata information needed for training. The `options` dictionary stores task-specific information including the train/val/test split assignment.

Sources: [olmoearth_projects/projects/mozambique_lulc/create_windows_for_lulc.py:182-201]()

### Temporal Coverage

Each group (province or region) has a defined temporal range for data collection:

| Group | Start Time (UTC) | End Time (UTC) | Duration |
|-------|-----------------|----------------|----------|
| gaza | 2024-10-23 | 2025-06-20 | ~8 months |
| manica | 2024-10-23 | 2025-06-20 | ~8 months |
| zambezia | 2024-10-23 | 2025-06-20 | ~8 months |
| crop_type | 2024-10-23 | 2025-06-20 | ~8 months |

These temporal ranges are used when querying satellite imagery during training data preparation. The ranges are aligned across provinces to ensure consistent seasonal coverage.

Sources: [olmoearth_projects/projects/mozambique_lulc/create_windows_for_lulc.py:53-74](), [olmoearth_run_data/mozambique_lulc/README.md:46-49]()

## Label Layer Creation

### Vector Label Format

Labels are stored as vector features using `GeojsonVectorFormat`:

```python
feature = Feature(
    window.get_geometry(),  # Geometry covering entire window
    {
        "category_id": category_id,      # Integer class ID
        "category": category_label,      # String class name
        "fid": fid,                       # Feature ID from GPKG
        "split": split,                  # train/val/test
    },
)
```

The vector label represents the entire window extent, with properties storing classification information. This format is suitable for point-based classification tasks.

Sources: [olmoearth_projects/projects/mozambique_lulc/create_windows_for_lulc.py:204-215]()

### Raster Label Conversion

For segmentation-based training (which is faster than classification), vector labels are converted to rasters using [olmoearth_projects/projects/mozambique_lulc/create_label_raster.py:1-110]():

```python
def create_label_raster(window: Window) -> None:
    """Create label raster for the given window."""
    # Read vector label
    features = GeojsonVectorFormat().decode_vector(label_dir, ...)
    class_id = get_class_id(features[0].properties["category"])
    
    # Create raster with class_id in center pixel
    raster = np.zeros((1, height, width), dtype=np.uint8)
    raster[:, height // 2, width // 2] = class_id
    
    # Write as GeoTIFF
    GeotiffRasterFormat().encode_raster(raster_dir, ...)
```

The raster is initialized to zeros except for the center pixel, which contains the class ID. This approach treats the task as segmentation while effectively performing classification on the center pixel.

Sources: [olmoearth_projects/projects/mozambique_lulc/create_label_raster.py:54-77](), [olmoearth_run_data/mozambique_lulc/README.md:33-37]()

## Data Splitting Strategies

### Spatial Data Splitter

The `SpatialDataSplitter` from `olmoearth_run` is used to create spatially-aware train/validation splits:

```python
splitter = SpatialDataSplitter(
    train_prop=0.9,   # 90% train
    val_prop=0.1,     # 10% validation
    test_prop=0.0,    # Test split from separate files
    grid_size=32      # Grid cell size for spatial grouping
)
```

The splitter uses a grid-based approach to ensure that nearby points are assigned to the same split, reducing spatial autocorrelation between training and validation sets:

1. Project window coordinates to a spatial grid
2. Hash grid cell coordinates to deterministically assign split
3. Ensures windows in the same grid cell have the same split

This is crucial for geospatial data where nearby observations are highly correlated.

Sources: [olmoearth_projects/projects/mozambique_lulc/create_windows_for_lulc.py:233-235](), [olmoearth_projects/projects/mozambique_lulc/update_train_test_split.py:55-65]()

### Split Assignment Workflow

```mermaid
graph TB
    InputSplit["Input split from filename<br/>'train' or 'test'"]
    
    CheckSplit{"split == 'train'?"}
    
    UseSplitter["splitter.choose_split_for_window()<br/>Apply spatial splitting"]
    
    KeepTest["Keep as 'test'"]
    
    UpdateOptions["window.options['split'] = split"]
    
    SaveWindow["window.save()"]
    
    InputSplit --> CheckSplit
    CheckSplit -->|Yes| UseSplitter
    CheckSplit -->|No| KeepTest
    UseSplitter --> UpdateOptions
    KeepTest --> UpdateOptions
    UpdateOptions --> SaveWindow
    
    style UseSplitter fill:#f9f9f9
```

**Diagram: Split Assignment Logic**

Windows from files marked as "train" are further split into train/val using `SpatialDataSplitter`, while windows from "test" files remain in the test split. This allows for a fixed test set with spatial validation splitting.

Sources: [olmoearth_projects/projects/mozambique_lulc/create_windows_for_lulc.py:198-201]()

### Updating Splits Post-Creation

Splits can be updated after initial window creation using [olmoearth_projects/projects/mozambique_lulc/update_train_test_split.py:1-86]():

```bash
python update_train_test_split.py \
    --ds_path /path/to/dataset \
    --splitter spatial \
    --workers 32
```

This script re-applies the splitting logic to existing windows, useful when changing validation ratios or switching between random and spatial splitting strategies.

Sources: [olmoearth_projects/projects/mozambique_lulc/update_train_test_split.py:22-86](), [olmoearth_run_data/mozambique_lulc/README.md:40-45]()

## Usage and Command Line Interface

### Basic Window Creation

The main script supports parallel processing for efficient window generation:

```bash
python create_windows_for_lulc.py \
    --gpkg_dir /path/to/gpkg/files \
    --ds_path /path/to/output/dataset \
    --window_size 32 \
    --max_workers 32
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--gpkg_dir` | str | required | Directory containing GPKG files |
| `--ds_path` | str | required | Output dataset root path |
| `--window_size` | int | 1 | Window size in pixels (typically 32) |
| `--max_workers` | int | 32 | Number of parallel worker processes |
| `--crop_type` | flag | False | Create crop type windows instead of LULC |

### Crop Type Mode

For crop type classification, use the `--crop_type` flag:

```bash
python create_windows_for_lulc.py \
    --gpkg_dir /path/to/gpkg/files \
    --ds_path /path/to/output/dataset \
    --window_size 32 \
    --crop_type
```

This expects different GPKG files with crop labels in the `crop1` column instead of numeric `class` values.

Sources: [olmoearth_projects/projects/mozambique_lulc/create_windows_for_lulc.py:268-337](), [olmoearth_run_data/mozambique_lulc/README.md:14-21]()

### Complete Dataset Preparation Pipeline

After creating windows, additional steps are needed to prepare the dataset for training:

1. **Create windows** (this page):
```bash
python create_windows_for_lulc.py --gpkg_dir ... --ds_path $DATASET_PATH
```

2. **Copy configuration**:
```bash
cp config.json $DATASET_PATH/
```

3. **Prepare dataset** (materialize satellite imagery):
```bash
rslearn dataset prepare --root $DATASET_PATH --workers 64
```

4. **Convert labels to rasters**:
```bash
python create_label_raster.py --ds_path $DATASET_PATH
```

5. **Assess label quality** (see [Label Quality Assessment](#4.2)):
```bash
python check_label_quality.py --ds_path $DATASET_PATH --split train
```

Sources: [olmoearth_run_data/mozambique_lulc/README.md:14-37]()

## Multiprocessing and Performance

The window creation process uses multiprocessing for parallel execution:

```python
multiprocessing.set_start_method("forkserver", force=True)

if max_workers <= 1:
    # Single-threaded for debugging
    for kw in tqdm.tqdm(jobs):
        create_window(**kw)
else:
    # Parallel processing
    p = multiprocessing.Pool(max_workers)
    outputs = star_imap_unordered(p, create_window, jobs)
    for _ in tqdm.tqdm(outputs, total=len(jobs)):
        pass
```

The `forkserver` start method is used to avoid issues with complex initialization in forked processes. The `star_imap_unordered` utility from rslearn provides efficient parallel mapping with progress tracking.

For typical datasets with thousands of annotations, using 32-64 workers can complete window creation in minutes rather than hours.

Sources: [olmoearth_projects/projects/mozambique_lulc/create_windows_for_lulc.py:257-265](), [olmoearth_projects/projects/mozambique_lulc/create_windows_for_lulc.py:269]()

## Window Organization Structure

Windows are organized on disk in a hierarchical structure:

```
dataset_root/
├── config.json
├── groups/
│   ├── gaza/
│   │   ├── windows/
│   │   │   ├── 123_-25.140374_33.664738/
│   │   │   │   ├── window.json           # Window metadata
│   │   │   │   ├── layers/
│   │   │   │   │   ├── label/            # Vector label
│   │   │   │   │   │   └── features.geojson
│   │   │   │   │   ├── label_raster/     # Raster label
│   │   │   │   │   │   └── label.tif
│   │   │   │   │   └── sentinel2/        # Satellite data
│   │   │   │   │       └── *.tif
│   ├── manica/
│   │   └── windows/...
│   ├── zambezia/
│   │   └── windows/...
│   └── crop_type/
│       └── windows/...
```

Each window is named using the format `{fid}_{latitude}_{longitude}` and stored under its group directory. The group typically corresponds to the province or region, allowing for group-based training and evaluation.

Sources: [olmoearth_projects/projects/mozambique_lulc/create_windows_for_lulc.py:180-196]()

## Integration with Dataset Configuration

The window creation process integrates with rslearn's dataset configuration system. A `config.json` file defines the data layers:

```json
{
  "layers": {
    "label": {
      "type": "vector"
    },
    "label_raster": {
      "type": "raster",
      "band_sets": [{
        "bands": ["label"],
        "dtype": "int32"
      }]
    },
    "sentinel2": {
      "type": "raster",
      "data_source": {
        "name": "rslearn.data_sources.planetary_computer.Sentinel2",
        "query_config": {
          "max_matches": 8,
          "min_matches": 8,
          "period_duration": "30d",
          "space_mode": "PER_PERIOD_MOSAIC"
        }
      }
    }
  }
}
```

This configuration is used during dataset preparation (see [Data Module and Transforms](#5.4)) to fetch satellite imagery for each window's spatial and temporal extent.

Sources: [olmoearth_run_data/mozambique_lulc/config.json:1-70](), [olmoearth_run_data/mozambique_lulc/README.md:22-32]()

---

# Page: Label Quality Assessment

# Label Quality Assessment

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [olmoearth_projects/projects/mozambique_lulc/check_label_quality.py](olmoearth_projects/projects/mozambique_lulc/check_label_quality.py)
- [olmoearth_projects/utils/label_quality/README.md](olmoearth_projects/utils/label_quality/README.md)
- [olmoearth_projects/utils/label_quality/spatial_clustering.py](olmoearth_projects/utils/label_quality/spatial_clustering.py)
- [olmoearth_projects/utils/label_quality/spatial_extent.py](olmoearth_projects/utils/label_quality/spatial_extent.py)
- [tests/unit/utils/__init__.py](tests/unit/utils/__init__.py)
- [tests/unit/utils/label_quality/__init__.py](tests/unit/utils/label_quality/__init__.py)
- [tests/unit/utils/label_quality/test_spatial_clustering.py](tests/unit/utils/label_quality/test_spatial_clustering.py)

</details>



## Purpose and Scope

This document describes the label quality assessment utilities used to evaluate training datasets before model fine-tuning. These utilities provide quantitative metrics to assess whether a set of labeled geospatial data is suitable for training high-quality models.

For information about creating training windows from raw data, see [Creating Training Windows](#4.1). For information about organizing and splitting the assessed data, see [Data Splitting and Organization](#4.3).

## Overview

Label quality assessment is a critical step in the data processing pipeline that occurs after training windows have been created and before model training begins. The quality of model predictions depends directly on the quality of training labels. While domain experts provide the best assessment, the utilities in this system provide quantitative indicators of dataset suitability.

The assessment system evaluates three key aspects of label quality:
- **Spatial Clustering**: How spatially distributed different classes are
- **Spatial Extent**: How much of the total labeled area each class covers
- **Label Imbalance**: The proportion of labels in each class

```mermaid
graph LR
    subgraph "Data Processing Pipeline"
        RAW["Raw GPKG Files<br/>Field Surveys"]
        WINDOWS["create_windows_for_lulc.py<br/>Window Generation"]
        QUALITY["check_label_quality function<br/>Quality Assessment"]
        SPLIT["update_train_test_split.py<br/>Data Splitting"]
        TRAINING["Model Training<br/>rslearn Framework"]
    end
    
    RAW --> WINDOWS
    WINDOWS --> QUALITY
    QUALITY --> SPLIT
    SPLIT --> TRAINING
    
    QUALITY --> METRICS["Quality Metrics<br/>- Spatial Clustering F1<br/>- Spatial Extent<br/>- Label Imbalance"]
```

**Sources**: [olmoearth_projects/utils/label_quality/README.md:1-86](), [olmoearth_projects/projects/mozambique_lulc/check_label_quality.py:1-51]()

## System Architecture

The label quality assessment system consists of a main entry point that coordinates three independent metric calculators, each operating on a GeoDataFrame with `label` and `geometry` columns.

```mermaid
graph TB
    subgraph "Entry Point"
        CHECK["check_label_quality.py<br/>Main Script"]
        LOAD["Dataset.load_windows()<br/>Load Windows"]
        GDF["GeoDataFrame Creation<br/>label, geometry columns"]
    end
    
    subgraph "Core Utilities"
        MAIN["check_label_quality()<br/>Coordinator Function"]
        SC["spatial_clustering()<br/>Spatial KNN Analysis"]
        SE["spatial_extent()<br/>Area Coverage"]
        LI["label_imbalance()<br/>Class Distribution"]
    end
    
    subgraph "Output"
        TABLE["Rich Table<br/>Formatted Metrics"]
    end
    
    CHECK --> LOAD
    LOAD --> GDF
    GDF --> MAIN
    MAIN --> SC
    MAIN --> SE
    MAIN --> LI
    SC --> TABLE
    SE --> TABLE
    LI --> TABLE
```

**Sources**: [olmoearth_projects/projects/mozambique_lulc/check_label_quality.py:1-51](), [olmoearth_projects/utils/label_quality/README.md:1-86]()

## Spatial Clustering Metric

### Concept

The spatial clustering metric assesses how geographically dispersed different classes are within the dataset. Ideally, different classes should be well-distributed across the study area rather than concentrated in isolated clusters. High spatial clustering indicates that a class's label can be predicted solely from its spatial location, which may lead to models that fail to generalize to new geographic areas.

The metric uses a spatial k-nearest neighbors (KNN) approach: for each instance, it predicts the class based on the k nearest spatial neighbors. High prediction accuracy indicates high spatial clustering, which is generally undesirable for robust model training.

```mermaid
graph TB
    subgraph "Input Processing"
        DF["GeoDataFrame<br/>label, geometry columns"]
        EXTRACT["Extract Centroids<br/>Convert to radians<br/>lat, lon features"]
        LABELS["Factorize Labels<br/>Classification: str→int<br/>Regression: float unchanged"]
    end
    
    subgraph "KNN Algorithm"
        LOOP["For each instance i"]
        DIST["relative_haversine()<br/>Calculate distances<br/>Great circle distance"]
        TOPK["torch.topk()<br/>Find k+1 nearest<br/>Skip self (index 0)"]
        PRED["Predict from neighbors<br/>Classification: mode()<br/>Regression: mean()"]
    end
    
    subgraph "Metric Calculation"
        CLASS["Classification:<br/>F1 per class<br/>TP/(TP+0.5*(FP+FN))"]
        REG["Regression:<br/>MSE<br/>mean((y-ŷ)²)"]
    end
    
    DF --> EXTRACT
    EXTRACT --> LABELS
    LABELS --> LOOP
    LOOP --> DIST
    DIST --> TOPK
    TOPK --> PRED
    PRED --> CLASS
    PRED --> REG
```

**Sources**: [olmoearth_projects/utils/label_quality/spatial_clustering.py:1-90](), [olmoearth_projects/utils/label_quality/README.md:10-29]()

### Implementation

The `spatial_clustering` function in [olmoearth_projects/utils/label_quality/spatial_clustering.py:30-89]() implements the spatial KNN algorithm:

| Component | Implementation Details |
|-----------|----------------------|
| **Distance Metric** | `relative_haversine()` function [10-27]() calculates great circle distance using Haversine formula on radians |
| **Feature Extraction** | Geometry centroids converted to latitude/longitude in radians [42-48]() |
| **Task Detection** | Automatically detects classification vs regression based on label type [51-54]() |
| **k Parameter** | Default k=5, finds k+1 nearest to exclude self [61-63]() |
| **Classification Output** | F1 score per class using precision and recall [77-88]() |
| **Regression Output** | Mean squared error (MSE) [73]() |

The Haversine formula calculates the great circle distance between two points on Earth:

```
a = sin²(Δlat/2) + cos(lat₁) × cos(lat₂) × sin²(Δlon/2)
distance = 2 × R × arcsin(√a)
```

Since we only need relative distances for KNN, the Earth radius R is omitted [olmoearth_projects/utils/label_quality/spatial_clustering.py:10-27]().

**Sources**: [olmoearth_projects/utils/label_quality/spatial_clustering.py:1-90]()

### Interpretation

For classification tasks, the output is an F1 score per class:

| F1 Score Range | Interpretation | Recommendation |
|---------------|----------------|----------------|
| 0.0 - 0.5 | Low spatial clustering | Good - classes are spatially distributed |
| 0.5 - 0.7 | Moderate clustering | Acceptable - some spatial patterns exist |
| 0.7 - 1.0 | High spatial clustering | Concerning - may limit generalization |

For regression tasks, lower MSE values indicate higher spatial clustering. The metric should be compared against the variance of the target variable to assess relative clustering.

**Sources**: [olmoearth_projects/utils/label_quality/README.md:10-29](), [tests/unit/utils/label_quality/test_spatial_clustering.py:7-30]()

## Spatial Extent Metric

### Concept

The spatial extent metric measures how much of the total labeled area each class occupies. Ideally, each class should be present across a large fraction of the study area rather than concentrated in a small region. This ensures that the model encounters each class across diverse spatial contexts.

The metric calculates the ratio of each class's bounding box area to the total dataset's bounding box area. Values close to 1.0 indicate that a class is distributed throughout the entire study area.

```mermaid
graph TB
    subgraph "Area Calculation"
        DF["GeoDataFrame<br/>label, geometry columns"]
        TOTAL["total_bounds<br/>Dataset bounding box<br/>min_lon, min_lat<br/>max_lon, max_lat"]
        CLASS_BOUNDS["Per-class bounds<br/>Filter by label<br/>total_bounds per class"]
    end
    
    subgraph "Relative Area Formula"
        FORMULA["relative_area()<br/>A = (sin(lat₂)-sin(lat₁)) × (lon₂-lon₁)<br/>Omit constants (R², π/180)"]
    end
    
    subgraph "Output"
        RATIO["class_area / total_area<br/>Per-class extent ratio"]
    end
    
    DF --> TOTAL
    DF --> CLASS_BOUNDS
    TOTAL --> FORMULA
    CLASS_BOUNDS --> FORMULA
    FORMULA --> RATIO
```

**Sources**: [olmoearth_projects/utils/label_quality/spatial_extent.py:1-32](), [olmoearth_projects/utils/label_quality/README.md:30-46]()

### Implementation

The `spatial_extent` function in [olmoearth_projects/utils/label_quality/spatial_extent.py:19-31]() calculates extent ratios using spherical geometry:

| Component | Implementation Details |
|-----------|----------------------|
| **Area Formula** | Spherical rectangle area: `A = R² × (sin(φ₂)-sin(φ₁)) × (λ₂-λ₁) / 180` [7-16]() |
| **Constant Omission** | R (Earth radius) and 180 factor omitted since using ratios [11]() |
| **Total Bounds** | `df.total_bounds` provides overall bounding box [24]() |
| **Class Bounds** | Filter by class label then compute `total_bounds` [28]() |
| **Output** | Dictionary mapping class label to extent ratio [26-29]() |

The spherical area calculation accounts for Earth's curvature by using the sine of latitude values, which properly handles the convergence of meridians at higher latitudes [olmoearth_projects/utils/label_quality/spatial_extent.py:7-16]().

**Sources**: [olmoearth_projects/utils/label_quality/spatial_extent.py:1-32]()

### Interpretation

| Extent Ratio | Interpretation | Recommendation |
|--------------|----------------|----------------|
| 0.8 - 1.0 | Excellent coverage | Class is distributed across study area |
| 0.5 - 0.8 | Good coverage | Class is reasonably distributed |
| 0.2 - 0.5 | Limited coverage | Class may be geographically constrained |
| 0.0 - 0.2 | Poor coverage | Class is highly localized |

Classes with low spatial extent ratios may indicate:
- Naturally rare phenomena (acceptable)
- Insufficient sampling in certain regions (concerning)
- Geographic specificity that may limit model generalization

**Sources**: [olmoearth_projects/utils/label_quality/README.md:30-46]()

## Label Imbalance Metric

### Concept

The label imbalance metric measures the proportion of labels belonging to each class. Severe class imbalance can lead to models that are biased toward majority classes and perform poorly on minority classes. The metric simply calculates: `count(class) / count(total)`.

While perfect balance (equal proportions) is not always necessary or desirable—some land cover types are naturally more prevalent—extreme imbalance (e.g., <1% or >90% for a class) often indicates data collection issues or suggests the need for class-weighted loss functions during training.

**Sources**: [olmoearth_projects/utils/label_quality/README.md:48-50]()

### Interpretation

| Class Proportion | Assessment | Considerations |
|-----------------|------------|----------------|
| > 50% | Dominant class | Risk of model bias toward this class |
| 20% - 50% | Well-represented | Generally good for training |
| 5% - 20% | Adequately represented | May need attention during training |
| < 5% | Minority class | Consider class weighting or oversampling |

The label imbalance values should be considered alongside the actual number of samples. A class with 5% representation is concerning if the dataset has 100 samples (5 instances) but acceptable with 10,000 samples (500 instances).

**Sources**: [olmoearth_projects/utils/label_quality/README.md:48-50]()

## Usage

### Command-Line Interface

The label quality assessment is typically run via the example script [olmoearth_projects/projects/mozambique_lulc/check_label_quality.py:1-51]():

```bash
python olmoearth_projects/projects/mozambique_lulc/check_label_quality.py \
    --ds_path /weka/dfive-default/rslearn-eai/datasets/crop/mozambique_lulc/20251202 \
    --split train \
    --crop_type  # Optional flag for crop type datasets
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--ds_path` | str | Required | Path to the rslearn dataset |
| `--split` | str | `"train"` | Dataset split to assess: `"train"`, `"val"`, `"test"`, or `"all"` |
| `--crop_type` | flag | False | Use `["crop_type"]` groups instead of province groups |

**Sources**: [olmoearth_projects/projects/mozambique_lulc/check_label_quality.py:12-28]()

### Integration Workflow

```mermaid
graph LR
    subgraph "Data Loading"
        DATASET["Dataset(UPath)<br/>rslearn.dataset.dataset"]
        WINDOWS["load_windows()<br/>show_progress=True<br/>groups parameter"]
        FILTER["Filter by split<br/>window.options['split']"]
    end
    
    subgraph "GeoDataFrame Creation"
        EXTRACT["Extract per window:<br/>- category → label<br/>- geometry → WGS84"]
        GDF["gpd.GeoDataFrame<br/>label, geometry columns"]
    end
    
    subgraph "Assessment"
        CHECK["check_label_quality(df)<br/>Run all metrics"]
        DISPLAY["Rich table output<br/>Formatted console display"]
    end
    
    DATASET --> WINDOWS
    WINDOWS --> FILTER
    FILTER --> EXTRACT
    EXTRACT --> GDF
    GDF --> CHECK
    CHECK --> DISPLAY
```

**Sources**: [olmoearth_projects/projects/mozambique_lulc/check_label_quality.py:35-50]()

### Example Code Pattern

The typical usage pattern from [olmoearth_projects/projects/mozambique_lulc/check_label_quality.py:35-50]():

1. **Load Dataset**: Initialize `Dataset` object with path
2. **Define Groups**: Specify groups to load (e.g., provinces or crop types)
3. **Filter Windows**: Select windows matching desired split(s)
4. **Extract Data**: Convert window options and geometries to GeoDataFrame format
5. **Transform Geometry**: Convert to `WGS84_PROJECTION` for spatial calculations
6. **Run Assessment**: Call `check_label_quality()` with the prepared GeoDataFrame

The geometry transformation is critical because spatial calculations assume WGS84 coordinates (latitude/longitude) [olmoearth_projects/projects/mozambique_lulc/check_label_quality.py:46]().

**Sources**: [olmoearth_projects/projects/mozambique_lulc/check_label_quality.py:35-50]()

## Output Format

The assessment produces a formatted table with three sections, one for each metric. Example output from the Mozambique LULC training split:

```
┏━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┓
┃         Check name ┃ Metric                ┃               Value ┃
┡━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━┩
│    label_imbalance │ Bare Ground           │ 0.12681827494365908 │
│    label_imbalance │ Trees                 │ 0.09813562794509322 │
│    label_imbalance │ Cropland              │ 0.27760704773611966 │
│    label_imbalance │ Flooded Vegetation    │  0.1024380249948781 │
│    label_imbalance │ Water                 │ 0.11391108379430445 │
│    label_imbalance │ Rangeland             │ 0.10530628969473468 │
│    label_imbalance │ Buildings             │  0.1757836508912108 │
│ spatial_clustering │ Bare Ground_f1        │  0.7763055339049103 │
│ spatial_clustering │ Trees_f1              │               0.918 │
│ spatial_clustering │ Cropland_f1           │  0.8201489890031926 │
│ spatial_clustering │ Flooded Vegetation_f1 │  0.6470588235294118 │
│ spatial_clustering │ Water_f1              │  0.5609756097560976 │
│ spatial_clustering │ Rangeland_f1          │  0.7097480832420592 │
│ spatial_clustering │ Buildings_f1          │  0.9638554216867469 │
│     spatial_extent │ Bare Ground           │   0.906388431021162 │
│     spatial_extent │ Trees                 │  0.8143211426450099 │
│     spatial_extent │ Cropland              │  0.8178565572914295 │
│     spatial_extent │ Flooded Vegetation    │  0.8195186876112993 │
│     spatial_extent │ Water                 │  0.8015534585021155 │
│     spatial_extent │ Rangeland             │  0.9892764881988351 │
│     spatial_extent │ Buildings             │  0.7256137393021044 │
└────────────────────┴───────────────────────┴─────────────────────┘
```

### Interpreting the Example

This Mozambique LULC dataset shows:

**Label Imbalance**: Relatively balanced with classes ranging from 9.8% (Trees) to 27.8% (Cropland). No severe imbalance issues.

**Spatial Clustering**: 
- High clustering concerns: Buildings (F1=0.964), Trees (F1=0.918) are highly spatially clustered
- Moderate clustering: Cropland (F1=0.820), Bare Ground (F1=0.776), Rangeland (F1=0.710)
- Good distribution: Water (F1=0.561), Flooded Vegetation (F1=0.647)

**Spatial Extent**: All classes show good coverage (>0.72), with Rangeland having excellent coverage (0.989). This indicates the dataset spans diverse geographic regions.

**Sources**: [olmoearth_projects/utils/label_quality/README.md:57-85]()

## Testing

Unit tests verify the correctness of each metric implementation:

### Spatial Clustering Tests

[tests/unit/utils/label_quality/test_spatial_clustering.py:7-30]() tests classification:
- **Perfect clustering**: South American cities labeled by hemisphere achieve F1=1.0 for both classes
- **No clustering**: Random labels achieve F1=0.0 for all classes

[tests/unit/utils/label_quality/test_spatial_clustering.py:32-51]() tests regression:
- **Perfect clustering**: Spatially consistent values achieve MSE=0.0
- **No clustering**: Spatially inconsistent values produce MSE=1.0

These tests validate that the spatial KNN algorithm correctly quantifies spatial clustering patterns.

**Sources**: [tests/unit/utils/label_quality/test_spatial_clustering.py:1-51]()

## Best Practices

### When to Run Assessment

Run label quality assessment:
1. **After initial window creation**: Identify data collection issues early
2. **After adding new labels**: Ensure new data maintains quality
3. **Before model training**: Verify dataset is suitable for training
4. **Per split**: Assess train, validation, and test splits separately to identify split-specific issues

### Addressing Quality Issues

| Issue | Potential Solutions |
|-------|-------------------|
| High spatial clustering | Collect more geographically diverse samples; use spatial cross-validation |
| Low spatial extent | Expand data collection to cover more of study area |
| Severe label imbalance | Use class-weighted loss functions; oversample minority classes; collect more minority samples |

### Multi-Split Assessment

Use `--split all` to assess all splits simultaneously [olmoearth_projects/projects/mozambique_lulc/check_label_quality.py:30-33](). This reveals whether spatial splitting strategies (see [Data Splitting and Organization](#4.3)) have created unintended biases between splits.

**Sources**: [olmoearth_projects/utils/label_quality/README.md:1-86](), [olmoearth_projects/projects/mozambique_lulc/check_label_quality.py:1-51]()

---

# Page: Data Splitting and Organization

# Data Splitting and Organization

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [olmoearth_projects/projects/mozambique_lulc/__init__.py](olmoearth_projects/projects/mozambique_lulc/__init__.py)
- [olmoearth_projects/projects/mozambique_lulc/create_label_raster.py](olmoearth_projects/projects/mozambique_lulc/create_label_raster.py)
- [olmoearth_projects/projects/mozambique_lulc/create_windows_for_lulc.py](olmoearth_projects/projects/mozambique_lulc/create_windows_for_lulc.py)
- [olmoearth_projects/projects/mozambique_lulc/update_train_test_split.py](olmoearth_projects/projects/mozambique_lulc/update_train_test_split.py)
- [olmoearth_run_data/awf/olmoearth_run.yaml](olmoearth_run_data/awf/olmoearth_run.yaml)
- [olmoearth_run_data/mozambique_lulc/prediction_request_geometry.geojson](olmoearth_run_data/mozambique_lulc/prediction_request_geometry.geojson)
- [olmoearth_run_data/nandi/olmoearth_run.yaml](olmoearth_run_data/nandi/olmoearth_run.yaml)

</details>



This document explains how training data is organized into groups and split into train, validation, and test sets within the olmoearth_projects repository. It covers the data splitter interfaces, spatial and random splitting strategies, and how splits are managed throughout the data processing pipeline.

For information about creating the windows themselves, see [Creating Training Windows](#4.1). For information about assessing the quality of splits and labels, see [Label Quality Assessment](#4.2).

## Overview of Data Organization

The system organizes training data using two primary concepts:

1. **Groups**: Logical divisions of the dataset, typically by geographic region or province (e.g., `gaza`, `manica`, `zambezia` for Mozambique LULC, or `spatial_split` for Nandi)
2. **Splits**: Division of data into `train`, `val`, and `test` subsets for model training and evaluation

Each window in a dataset has a `group` attribute and a `split` property stored in `window.options["split"]`. This dual organization enables both geographic partitioning and proper train/validation/test separation.

**Data Flow in Split Assignment**:

```mermaid
graph TB
    GPKG["GPKG Files<br/>(gaza_train.gpkg, manica_test.gpkg)"]
    INITIAL["Initial Split from Filename<br/>train or test"]
    SPATIAL["SpatialDataSplitter<br/>choose_split_for_window()"]
    WINDOW["Window Object<br/>window.options['split']"]
    TRAIN_SPLIT["Training Windows<br/>split='train'"]
    VAL_SPLIT["Validation Windows<br/>split='val'"]
    TEST_SPLIT["Test Windows<br/>split='test'"]
    
    GPKG --> INITIAL
    INITIAL -->|"if split=='train'"| SPATIAL
    INITIAL -->|"if split=='test'"| WINDOW
    SPATIAL --> WINDOW
    WINDOW --> TRAIN_SPLIT
    WINDOW --> VAL_SPLIT
    WINDOW --> TEST_SPLIT
    
    style SPATIAL fill:#f9f9f9
    style WINDOW fill:#f0f0f0
```

**Sources**: [olmoearth_projects/projects/mozambique_lulc/create_windows_for_lulc.py:1-339]()

## Data Splitter Interfaces

The system defines a common interface for data splitting strategies through the `DataSplitterInterface` class from `olmoearth_run`. Two primary implementations are available:

| Splitter | Strategy | Use Case | Parameters |
|----------|----------|----------|------------|
| `SpatialDataSplitter` | Grid-based spatial hashing | Ensures spatial separation between train/val/test | `train_prop`, `val_prop`, `test_prop`, `grid_size` |
| `RandomDataSplitter` | Random assignment | Simple random splitting without spatial consideration | `train_prop`, `val_prop`, `test_prop` |

Both implementations provide a `choose_split_for_window(window)` method that deterministically assigns a split based on the window's properties.

**Sources**: [olmoearth_projects/projects/mozambique_lulc/update_train_test_split.py:1-86](), [olmoearth_projects/projects/mozambique_lulc/create_windows_for_lulc.py:12-17]()

## Spatial Splitting Strategy

The `SpatialDataSplitter` implements a grid-based spatial hashing approach to ensure that geographically nearby samples are placed in the same split. This prevents data leakage where spatially correlated training and validation samples could lead to overly optimistic performance estimates.

**Spatial Splitting Algorithm**:

```mermaid
graph LR
    WINDOW["Window with<br/>Projection & Bounds"]
    CENTER["Calculate<br/>Window Center<br/>(x, y)"]
    GRID["Snap to Grid<br/>grid_x = x // grid_size<br/>grid_y = y // grid_size"]
    HASH["Hash Grid Coordinates<br/>hash((grid_x, grid_y))"]
    MODULO["Modulo Operation<br/>hash % 100"]
    SPLIT["Assign Split<br/>train: 0-89<br/>val: 90-99"]
    
    WINDOW --> CENTER
    CENTER --> GRID
    GRID --> HASH
    HASH --> MODULO
    MODULO --> SPLIT
    
    style GRID fill:#f9f9f9
    style HASH fill:#f9f9f9
```

**Configuration Parameters**:

- **`grid_size`**: Size of spatial grid cells in pixels (e.g., 32, 128). Larger values create larger contiguous regions with the same split
- **`train_prop`**: Proportion of data for training (e.g., 0.75 or 0.9)
- **`val_prop`**: Proportion of data for validation (e.g., 0.25 or 0.1)
- **`test_prop`**: Proportion of data for testing (typically 0.0 when test set is predefined)

**Example Configuration** from Mozambique LULC:

```python
splitter = SpatialDataSplitter(
    train_prop=0.9, 
    val_prop=0.1, 
    test_prop=0.0, 
    grid_size=32
)
```

The `grid_size=32` means that windows within a 32×32 pixel region will be assigned to the same split, creating spatial clusters.

**Sources**: [olmoearth_projects/projects/mozambique_lulc/create_windows_for_lulc.py:233-236](), [olmoearth_projects/projects/mozambique_lulc/update_train_test_split.py:55-58](), [olmoearth_run_data/nandi/olmoearth_run.yaml:11-17]()

## Split Assignment During Window Creation

The window creation process handles split assignment in two stages:

1. **Initial Split from Filename**: GPKG files are named with the intended split (e.g., `gaza_train.gpkg`, `gaza_test.gpkg`)
2. **Spatial Re-splitting of Training Data**: Windows initially marked as `train` are further divided into `train` and `val` using the spatial splitter

**Split Assignment Code Flow**:

```mermaid
graph TB
    subgraph "create_windows_for_lulc.py"
        GPKG_NAME["GPKG Filename<br/>e.g., gaza_train.gpkg"]
        EXPECTED["expected list<br/>(group, split, path)"]
        PARSE["Parse split<br/>from tuple"]
        CREATE["create_window()<br/>Line 147-216"]
        INITIAL_SPLIT["window.options['split'] = split"]
        CHECK["if split == 'train'"]
        CHOOSE["splitter.choose_split_for_window()"]
        UPDATE["window.options['split'] = new_split"]
        SAVE["window.save()"]
    end
    
    GPKG_NAME --> EXPECTED
    EXPECTED --> PARSE
    PARSE --> CREATE
    CREATE --> INITIAL_SPLIT
    INITIAL_SPLIT --> CHECK
    CHECK -->|"Yes"| CHOOSE
    CHECK -->|"No (test)"| SAVE
    CHOOSE --> UPDATE
    UPDATE --> SAVE
    
    style CHOOSE fill:#f9f9f9
    style CHECK fill:#f0f0f0
```

**Code Reference**: The split assignment logic is in [olmoearth_projects/projects/mozambique_lulc/create_windows_for_lulc.py:198-201]():

```python
if split == "train":
    split = splitter.choose_split_for_window(window)
    window.options["split"] = split
window.save()
```

This ensures that:
- Test data remains in the test split (no re-splitting)
- Training data is spatially divided into train and validation subsets

**Sources**: [olmoearth_projects/projects/mozambique_lulc/create_windows_for_lulc.py:147-216](), [olmoearth_projects/projects/mozambique_lulc/create_windows_for_lulc.py:218-266]()

## Group-Based Organization

Datasets are organized into **groups** that typically represent geographic regions or project-specific categories. Each group can have its own temporal coverage and processing parameters.

**Group Definition Structure**:

```mermaid
graph TB
    subgraph "GROUP_TIME Dictionary"
        GAZA["gaza:<br/>(2024-10-23, 2025-06-20)"]
        MANICA["manica:<br/>(2024-10-23, 2025-06-20)"]
        ZAMBEZIA["zambezia:<br/>(2024-10-23, 2025-06-20)"]
        CROP["crop_type:<br/>(2024-10-23, 2025-06-20)<br/>Union of all provinces"]
    end
    
    subgraph "Window Organization"
        W1["Windows with<br/>group='gaza'"]
        W2["Windows with<br/>group='manica'"]
        W3["Windows with<br/>group='zambezia'"]
        W4["Windows with<br/>group='crop_type'"]
    end
    
    GAZA --> W1
    MANICA --> W2
    ZAMBEZIA --> W3
    CROP --> W4
    
    style GAZA fill:#f9f9f9
    style CROP fill:#f0f0f0
```

**GROUP_TIME Configuration** from [olmoearth_projects/projects/mozambique_lulc/create_windows_for_lulc.py:54-74]():

The `GROUP_TIME` dictionary maps group names to temporal ranges:

```python
GROUP_TIME = {
    "gaza": (
        datetime(2024, 10, 23, tzinfo=UTC),
        datetime(2025, 6, 20, tzinfo=UTC),
    ),
    "manica": (
        datetime(2024, 10, 23, tzinfo=UTC),
        datetime(2025, 6, 20, tzinfo=UTC),
    ),
    "zambezia": (
        datetime(2024, 10, 23, tzinfo=UTC),
        datetime(2025, 6, 20, tzinfo=UTC),
    ),
    "crop_type": (
        datetime(2024, 10, 23, tzinfo=UTC),
        datetime(2025, 6, 20, tzinfo=UTC),
    ),
}
```

Groups enable:
- **Geographic partitioning**: Train separate models per region or a unified model
- **Temporal alignment**: Different regions can have different satellite imagery availability
- **Selective loading**: Filter windows by group during training or processing

**Sources**: [olmoearth_projects/projects/mozambique_lulc/create_windows_for_lulc.py:53-74](), [olmoearth_projects/projects/mozambique_lulc/create_windows_for_lulc.py:324-336]()

## Updating Splits After Creation

The `update_train_test_split.py` utility allows re-splitting existing datasets with different strategies or parameters. This is useful when:
- Changing from random to spatial splitting
- Adjusting train/validation proportions
- Modifying grid size for spatial splitting

**Update Split Workflow**:

```mermaid
graph LR
    DATASET["Dataset.load_windows()<br/>Filter by groups"]
    WINDOWS["List of Windows"]
    FILTER["Filter:<br/>split in ['train', 'val']"]
    CHOOSE["splitter.choose_split_for_window()"]
    UPDATE["window.options['split'] = new_split"]
    SAVE["window.save()"]
    
    DATASET --> WINDOWS
    WINDOWS --> FILTER
    FILTER --> CHOOSE
    CHOOSE --> UPDATE
    UPDATE --> SAVE
    
    style FILTER fill:#f9f9f9
    style CHOOSE fill:#f9f9f9
```

**Usage Example**:

```bash
# Update splits using spatial strategy
python update_train_test_split.py \
    --ds_path /path/to/dataset \
    --splitter spatial \
    --workers 32

# Update splits using random strategy
python update_train_test_split.py \
    --ds_path /path/to/dataset \
    --splitter random \
    --workers 32
```

**Key Implementation** from [olmoearth_projects/projects/mozambique_lulc/update_train_test_split.py:22-28]():

```python
def update_train_val_split(window: Window, splitter: DataSplitterInterface) -> None:
    """Create label raster for the given window."""
    if window.options["split"] in ["train", "val"]:
        split = splitter.choose_split_for_window(window)
        print(f"Window was {window.options['split']}, changing to {split}")
        window.options["split"] = split
        window.save()
```

Note that test splits are never modified to preserve the integrity of the test set.

**Sources**: [olmoearth_projects/projects/mozambique_lulc/update_train_test_split.py:1-86]()

## Configuration in YAML Files

Data splitter configuration is specified in `olmoearth_run.yaml` files for inference and window preparation workflows. These configurations define how data should be split during window preparation from raw labels.

**YAML Configuration Structure**:

```mermaid
graph TB
    subgraph "olmoearth_run.yaml"
        WP["window_prep:<br/>Window Preparation Config"]
        DS["data_splitter:<br/>class_path + init_args"]
        CLASS["class_path:<br/>SpatialDataSplitter"]
        ARGS["init_args:<br/>train_prop: 0.75<br/>val_prop: 0.25<br/>test_prop: 0.0<br/>grid_size: 128"]
        GN["group_name:<br/>spatial_split"]
        SP["split_property:<br/>split"]
    end
    
    WP --> DS
    DS --> CLASS
    DS --> ARGS
    WP --> GN
    WP --> SP
    
    style DS fill:#f9f9f9
    style ARGS fill:#f0f0f0
```

**Example Configuration** from [olmoearth_run_data/nandi/olmoearth_run.yaml:11-20]():

```yaml
window_prep:
  data_splitter:
    class_path: olmoearth_run.runner.tools.data_splitters.spatial_data_splitter.SpatialDataSplitter
    init_args:
      train_prop: 0.75
      val_prop: 0.25
      test_prop: 0.0
      grid_size: 128  # in pixels
  label_layer: "label"
  group_name: "spatial_split"
  split_property: "split"
```

**Configuration Parameters**:

| Parameter | Purpose | Example Values |
|-----------|---------|----------------|
| `class_path` | Fully qualified class name of splitter | `SpatialDataSplitter`, `RandomDataSplitter` |
| `train_prop` | Training set proportion | 0.75, 0.9 |
| `val_prop` | Validation set proportion | 0.25, 0.1 |
| `test_prop` | Test set proportion | 0.0 (typically predefined) |
| `grid_size` | Spatial grid cell size in pixels | 32, 128 |
| `group_name` | Name assigned to created windows | `"spatial_split"`, `"gaza"` |
| `split_property` | Window option key for split storage | `"split"` |

**Sources**: [olmoearth_run_data/nandi/olmoearth_run.yaml:11-20](), [olmoearth_run_data/awf/olmoearth_run.yaml:11-20]()

## Filtering Windows by Group and Split

During training and processing, windows can be filtered by group and split to create specific subsets:

**Dataset Loading with Filters**:

```python
# Load windows for specific groups
dataset = Dataset(UPath(args.ds_path))
windows = dataset.load_windows(
    workers=args.workers, 
    show_progress=True, 
    groups=["gaza", "manica", "zambezia"]  # Filter by group
)

# For crop type dataset
windows = dataset.load_windows(
    workers=args.workers,
    show_progress=True,
    groups=["crop_type"]
)
```

**Filtering by Split in Training**:

During training, the data module typically filters windows based on the split property:

```python
train_windows = [w for w in windows if w.options["split"] == "train"]
val_windows = [w for w in windows if w.options["split"] == "val"]
test_windows = [w for w in windows if w.options["split"] == "test"]
```

**Sources**: [olmoearth_projects/projects/mozambique_lulc/create_label_raster.py:67-104](), [olmoearth_projects/projects/mozambique_lulc/update_train_test_split.py:67-74]()

## Summary Table: Split Management Across Files

| File | Purpose | Split Handling | Group Usage |
|------|---------|----------------|-------------|
| `create_windows_for_lulc.py` | Create windows from GPKG files | Assigns initial split from filename; re-splits train data spatially | Creates windows with group names (gaza, manica, zambezia, crop_type) |
| `update_train_test_split.py` | Update existing window splits | Re-assigns splits for train/val windows using specified splitter | Filters windows by group list |
| `create_label_raster.py` | Create raster labels from vector labels | Reads split from `window.options["split"]` | Filters windows by group list |
| `olmoearth_run.yaml` | Configure inference and window prep | Defines splitter configuration for window preparation | Specifies `group_name` for created windows |

**Sources**: [olmoearth_projects/projects/mozambique_lulc/create_windows_for_lulc.py:1-339](), [olmoearth_projects/projects/mozambique_lulc/update_train_test_split.py:1-86](), [olmoearth_projects/projects/mozambique_lulc/create_label_raster.py:1-110](), [olmoearth_run_data/nandi/olmoearth_run.yaml:1-92]()

---

# Page: Model Training

# Model Training

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [olmoearth_run_data/mozambique_lulc/dataset.json](olmoearth_run_data/mozambique_lulc/dataset.json)
- [olmoearth_run_data/mozambique_lulc/model.yaml](olmoearth_run_data/mozambique_lulc/model.yaml)
- [olmoearth_run_data/mozambique_lulc/olmoearth_run.yaml](olmoearth_run_data/mozambique_lulc/olmoearth_run.yaml)
- [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml](olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml)
- [olmoearth_run_data/mozambique_lulc/rslp_finetuning_croptype.yaml](olmoearth_run_data/mozambique_lulc/rslp_finetuning_croptype.yaml)
- [olmoearth_run_data/mozambique_lulc/rslp_finetuning_croptype_in_season_novmar.yaml](olmoearth_run_data/mozambique_lulc/rslp_finetuning_croptype_in_season_novmar.yaml)
- [olmoearth_run_data/mozambique_lulc/rslp_finetuning_in_season_novmar.yaml](olmoearth_run_data/mozambique_lulc/rslp_finetuning_in_season_novmar.yaml)

</details>



This document describes the model training system in the olmoearth_projects repository, which uses the rslearn framework to fine-tune OlmoEarth foundation models for specific remote sensing tasks. Training is configured through YAML files that define model architecture, data loading, optimization, and callbacks.

For configuration file schemas, see [Training Configuration Files](#5.1). For details on the OlmoEarth encoder architecture, see [OlmoEarth Encoder Architecture](#5.2). For fine-tuning strategies, see [Fine-tuning Process](#5.3). For data loading details, see [Data Module and Transforms](#5.4). For evaluation metrics, see [Metrics and Evaluation](#5.5).

## Training System Overview

The training system uses PyTorch Lightning through the rslearn framework. All training is orchestrated by the `RslearnLightningModule` class with configurations specified in YAML files.

```mermaid
graph TB
    subgraph "Configuration Files"
        RSLP["rslp_finetuning.yaml<br/>Training Configuration"]
        MODEL["model.yaml<br/>Deployment Configuration"]
        DATASET["dataset.json<br/>Data Source Configuration"]
    end
    
    subgraph "rslearn Training Framework"
        LIGHTNING["rslearn.train.lightning_module<br/>RslearnLightningModule"]
        DATAMOD["rslearn.train.data_module<br/>RslearnDataModule"]
        MULTITASK["rslearn.models.multitask<br/>MultiTaskModel"]
    end
    
    subgraph "Model Components"
        OLMO["rslearn.models.olmoearth_pretrain.model<br/>OlmoEarth Encoder<br/>checkpoint_path: step667200"]
        UPSAMPLE["rslearn.models.upsample<br/>Upsample scale_factor=4"]
        CONV["rslearn.models.conv<br/>Conv 768->8 channels"]
        SEGHEAD["rslearn.train.tasks.segmentation<br/>SegmentationHead"]
    end
    
    subgraph "Training Components"
        TASK["rslearn.train.tasks.segmentation<br/>SegmentationTask<br/>num_classes: 8"]
        SCHEDULER["rslearn.train.scheduler<br/>PlateauScheduler<br/>factor=0.2 patience=2"]
        FREEZE["rslearn.train.callbacks.freeze_unfreeze<br/>FreezeUnfreeze<br/>unfreeze_at_epoch=20"]
    end
    
    subgraph "Callbacks"
        CKPT["lightning.pytorch.callbacks<br/>ModelCheckpoint<br/>monitor: val_segment/accuracy"]
        LRMON["lightning.pytorch.callbacks<br/>LearningRateMonitor"]
        WANDB["lightning.pytorch.loggers<br/>WandbLogger"]
    end
    
    RSLP --> LIGHTNING
    MODEL --> LIGHTNING
    DATASET --> DATAMOD
    
    LIGHTNING --> MULTITASK
    LIGHTNING --> DATAMOD
    LIGHTNING --> SCHEDULER
    
    MULTITASK --> OLMO
    MULTITASK --> UPSAMPLE
    UPSAMPLE --> CONV
    CONV --> SEGHEAD
    
    DATAMOD --> TASK
    
    LIGHTNING --> FREEZE
    LIGHTNING --> CKPT
    LIGHTNING --> LRMON
    LIGHTNING --> WANDB
    
    style LIGHTNING fill:#f9f9f9
    style MULTITASK fill:#f9f9f9
    style OLMO fill:#f9f9f9
```

**Sources:** [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:1-268](), [olmoearth_run_data/mozambique_lulc/model.yaml:1-278]()

## Configuration Structure

Training configurations are organized into three main sections: `model`, `data`, and `trainer`. Each section is specified using PyTorch Lightning's CLI configuration format with `class_path` and `init_args` patterns.

### Model Configuration Section

The model configuration defines the neural network architecture through a hierarchical structure:

| Component | Class Path | Key Parameters |
|-----------|-----------|----------------|
| Lightning Module | `rslearn.train.lightning_module.RslearnLightningModule` | `lr`, `scheduler` |
| Task Model | `rslearn.models.multitask.MultiTaskModel` | `encoder`, `decoders`, `loss_weights` |
| Encoder | `rslearn.models.olmoearth_pretrain.model.OlmoEarth` | `checkpoint_path`, `patch_size`, `autocast_dtype` |
| Decoder Upsample | `rslearn.models.upsample.Upsample` | `scale_factor: 4`, `mode: bilinear` |
| Decoder Conv | `rslearn.models.conv.Conv` | `in_channels: 768`, `out_channels: 8` |
| Task Head | `rslearn.train.tasks.segmentation.SegmentationHead` | - |

**Sources:** [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:1-41](), [olmoearth_run_data/mozambique_lulc/model.yaml:1-31]()

### Data Configuration Section

The data configuration specifies dataset location, input/output layers, and task definitions:

```mermaid
graph LR
    subgraph "Data Configuration"
        PATH["path:<br/>/weka/dfive-default/rslearn-eai/<br/>datasets/crop/mozambique_lulc/20251202"]
        
        subgraph "Inputs"
            S2["sentinel2_l2a:<br/>layers: [sentinel2]<br/>bands: [B02, B03, B04, B08, ...]<br/>dtype: FLOAT32<br/>passthrough: true"]
            LABEL["label:<br/>layers: [label_raster]<br/>bands: [label]<br/>dtype: INT32<br/>is_target: true"]
        end
        
        subgraph "Task Definition"
            MULTITASK_CFG["MultiTask"]
            SEGTASK["SegmentationTask<br/>num_classes: 8<br/>zero_is_invalid: true<br/>average: micro"]
            METRICS["Per-class Metrics:<br/>water_precision/recall<br/>bareground_precision/recall<br/>rangeland_precision/recall<br/>..."]
        end
    end
    
    PATH --> S2
    PATH --> LABEL
    S2 --> MULTITASK_CFG
    LABEL --> MULTITASK_CFG
    MULTITASK_CFG --> SEGTASK
    SEGTASK --> METRICS
```

**Sources:** [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:50-209](), [olmoearth_run_data/mozambique_lulc/model.yaml:32-191]()

### Trainer Configuration Section

The trainer configuration sets training duration, callbacks, and logging:

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `max_epochs` | 100 | Maximum training epochs |
| `callbacks[0]` | `LearningRateMonitor` | Log learning rate per epoch |
| `callbacks[1]` | `ModelCheckpoint` | Save best model on `val_segment/accuracy` |
| `callbacks[2]` | `FreezeUnfreeze` | Unfreeze encoder at epoch 20 |
| `logger` | `WandbLogger` | Log metrics to Weights & Biases |

**Sources:** [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:249-268](), [olmoearth_run_data/mozambique_lulc/model.yaml:246-278]()

## Model Architecture

The training system uses a encoder-decoder architecture where the OlmoEarth foundation model serves as the encoder and task-specific decoders are added for each task.

```mermaid
graph TB
    subgraph "Input"
        INPUT["Sentinel-2 L2A<br/>12 Bands x T Timesteps<br/>Shape: [B, T*12, H, W]"]
    end
    
    subgraph "Encoder: rslearn.models.olmoearth_pretrain.model.OlmoEarth"
        CKPT["checkpoint_path:<br/>/weka/.../step667200"]
        SELECTOR["selector: [encoder]"]
        PATCH["patch_size: 4<br/>Tokenize to patches"]
        EMBED["embedding_size: 768<br/>autocast_dtype: bfloat16"]
        FROZEN["Initial: Frozen<br/>Epoch 20+: Unfrozen"]
    end
    
    subgraph "Decoder Pipeline: segment"
        UP["rslearn.models.upsample.Upsample<br/>scale_factor: 4<br/>mode: bilinear<br/>Output: [B, 768, H, W]"]
        CONV_DECODE["rslearn.models.conv.Conv<br/>in_channels: 768<br/>out_channels: 8<br/>kernel_size: 1<br/>Output: [B, 8, H, W]"]
        PICK["rslearn.models.pick_features.PickFeatures<br/>indexes: [0]<br/>collapse: true"]
        HEAD["rslearn.train.tasks.segmentation<br/>SegmentationHead<br/>Output: logits"]
    end
    
    subgraph "Loss & Metrics"
        LOSS["Cross Entropy Loss<br/>zero_is_invalid: true"]
        ACC["Accuracy: micro average"]
        PER_CLASS["Per-class Precision/Recall<br/>8 classes total"]
    end
    
    INPUT --> PATCH
    CKPT --> PATCH
    SELECTOR --> PATCH
    PATCH --> EMBED
    EMBED --> FROZEN
    FROZEN --> UP
    UP --> CONV_DECODE
    CONV_DECODE --> PICK
    PICK --> HEAD
    HEAD --> LOSS
    HEAD --> ACC
    HEAD --> PER_CLASS
```

**Sources:** [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:7-38](), [olmoearth_run_data/mozambique_lulc/model.yaml:7-25]()

### OlmoEarth Encoder Initialization

The OlmoEarth encoder is initialized from a pre-trained checkpoint with specific configuration:

```yaml
class_path: rslearn.models.olmoearth_pretrain.model.OlmoEarth
init_args:
  checkpoint_path: /weka/dfive-default/helios/checkpoints/joer/phase2.0_base_lr0.0001_wd0.02/step667200
  selector: ["encoder"]
  patch_size: 4
  random_initialization: false
  embedding_size: null
  autocast_dtype: bfloat16
```

The `selector: ["encoder"]` parameter indicates that only the encoder portion of the checkpoint is loaded. The `patch_size: 4` divides input images into 4x4 pixel patches for processing. The `autocast_dtype: bfloat16` enables mixed-precision training for efficiency.

**Sources:** [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:8-16]()

### Decoder Architecture

The decoder pipeline consists of three sequential modules followed by a task head:

1. **Upsample Layer**: Upsamples features by 4x using bilinear interpolation to match input resolution
2. **Convolution Layer**: 1x1 convolution projecting 768 encoder features to 8 class channels
3. **PickFeatures**: Selects and collapses specific feature dimensions
4. **SegmentationHead**: Applies task-specific processing and loss computation

**Sources:** [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:18-38](), [olmoearth_run_data/mozambique_lulc/model.yaml:14-25]()

## Training Loop and Optimization

The training loop is managed by PyTorch Lightning's `Trainer` with custom schedulers and callbacks.

### Learning Rate and Scheduling

The system uses a plateau-based learning rate scheduler that reduces the learning rate when validation metrics plateau:

| Parameter | Value | Description |
|-----------|-------|-------------|
| Initial LR | 0.0001 | Starting learning rate |
| Scheduler | `PlateauScheduler` | Reduces LR on plateau |
| Factor | 0.2 | LR multiplier on reduction |
| Patience | 2 | Epochs to wait before reduction |
| Min LR | 0 | Minimum learning rate |
| Cooldown | 10 | Epochs to wait after reduction |

**Sources:** [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:42-49]()

### FreezeUnfreeze Training Strategy

The `FreezeUnfreeze` callback implements a two-stage training strategy:

```mermaid
graph LR
    subgraph "Stage 1: Epochs 0-19"
        FROZEN["Encoder: Frozen<br/>Decoder: Trainable<br/>LR: 0.0001"]
    end
    
    subgraph "Stage 2: Epochs 20-99"
        UNFROZEN["Encoder: Trainable<br/>Decoder: Trainable<br/>Encoder LR: 0.001<br/>Decoder LR: 0.0001"]
    end
    
    subgraph "FreezeUnfreeze Callback"
        SELECTOR["module_selector:<br/>[model, encoder, 0]"]
        EPOCH["unfreeze_at_epoch: 20"]
        FACTOR["unfreeze_lr_factor: 10"]
    end
    
    FROZEN --> EPOCH
    EPOCH --> UNFROZEN
    SELECTOR --> FROZEN
    SELECTOR --> UNFROZEN
    FACTOR --> UNFROZEN
```

This strategy first trains only the decoder while keeping the encoder frozen, then unfreezes the encoder with a 10x higher learning rate for fine-tuning. The `module_selector: ["model", "encoder", 0]` specifies the exact module path to freeze/unfreeze.

**Sources:** [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:261-265](), [olmoearth_run_data/mozambique_lulc/model.yaml:265-268]()

## Data Loading

The `RslearnDataModule` handles data loading, batching, and preprocessing for training, validation, and testing.

### Dataset Configuration

Datasets are loaded from rslearn archive format with specified input layers and target labels:

```mermaid
graph TB
    subgraph "Dataset Path"
        PATH["/weka/dfive-default/rslearn-eai/<br/>datasets/crop/mozambique_lulc/20251202"]
    end
    
    subgraph "Input Layers"
        S2_INPUT["sentinel2_l2a<br/>data_type: raster<br/>layers: [sentinel2]<br/>bands: [B02, B03, B04, B08,<br/>B05, B06, B07, B8A,<br/>B11, B12, B01, B09]<br/>dtype: FLOAT32<br/>load_all_item_groups: true<br/>load_all_layers: true"]
        
        LABEL_INPUT["label<br/>data_type: raster<br/>layers: [label_raster]<br/>bands: [label]<br/>dtype: INT32<br/>is_target: true"]
    end
    
    subgraph "Data Loading Configuration"
        BATCH["batch_size: 64"]
        WORKERS["num_workers: 32"]
        MAPPING["input_mapping:<br/>segment -> label: targets"]
    end
    
    PATH --> S2_INPUT
    PATH --> LABEL_INPUT
    S2_INPUT --> BATCH
    LABEL_INPUT --> BATCH
    BATCH --> WORKERS
    WORKERS --> MAPPING
```

**Sources:** [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:53-209]()

### Split Configurations

The data module uses separate configurations for training, validation, and testing:

| Split | Patch Size | Groups | Split Tag | Load Mode |
|-------|-----------|--------|-----------|-----------|
| train | Dynamic (crop to 16) | ["gaza", "manica", "zambezia"] | "train" | Random crops with transforms |
| val | 16 | ["gaza", "manica", "zambezia"] | "val" | Fixed patches |
| test | 16 | ["gaza", "manica", "zambezia"] | "test" | Fixed patches |

Training uses random cropping and augmentation while validation and testing use fixed patch sizes without augmentation.

**Sources:** [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:218-248]()

## Transforms Pipeline

The training pipeline applies different transforms for training versus validation/testing.

### Default Transforms

All data loading configurations include normalization:

```yaml
default_config:
  transforms:
    - class_path: rslearn.models.olmoearth_pretrain.norm.OlmoEarthNormalize
      init_args:
        band_names:
          sentinel2_l2a: ["B02", "B03", "B04", "B08", "B05", "B06", "B07", "B8A", "B11", "B12", "B01", "B09"]
```

The `OlmoEarthNormalize` transform applies band-specific normalization to match the pre-training distribution.

**Sources:** [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:212-217]()

### Training Transforms

Training data undergoes a sequence of augmentation transforms:

```mermaid
graph LR
    INPUT["Input<br/>Variable Size"] --> PAD["rslearn.train.transforms.pad.Pad<br/>size: 31<br/>mode: center<br/>selectors: [sentinel2_l2a,<br/>target/segment/classes,<br/>target/segment/valid]"]
    
    PAD --> CROP["rslearn.train.transforms.crop.Crop<br/>crop_size: 16<br/>Random spatial crop<br/>selectors: [sentinel2_l2a,<br/>target/segment/classes,<br/>target/segment/valid]"]
    
    CROP --> FLIP["rslearn.train.transforms.flip.Flip<br/>Random horizontal/vertical flip<br/>selectors: [sentinel2_l2a,<br/>target/segment/classes,<br/>target/segment/valid]"]
    
    FLIP --> NORM["rslearn.models.olmoearth_pretrain.norm<br/>OlmoEarthNormalize<br/>Band-specific normalization"]
    
    NORM --> OUTPUT["Output<br/>16x16 patches"]
```

The padding with size 31 pixels creates a 31-pixel border around the data to enable edge handling during cropping. The final crop to 16x16 provides the training patch size.

**Sources:** [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:218-235]()

### Validation/Test Transforms

Validation and test data use only normalization without augmentation:

- **Patch Size**: Fixed 16x16 pixels
- **Overlap**: None during validation/test
- **Transforms**: Only `OlmoEarthNormalize`

**Sources:** [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:239-248]()

### Prediction Configuration

For inference, the model uses overlapping patches to ensure smooth boundaries:

```yaml
predict_config:
  load_all_patches: true
  patch_size: 16
  overlap_ratio: 0.25  # 4 / 16
  skip_targets: true
  transforms:
    - class_path: rslearn.models.olmoearth_pretrain.norm.OlmoEarthNormalize
```

The `overlap_ratio: 0.25` means 4 pixels of overlap on each side of 16x16 patches, enabling smooth merging during inference.

**Sources:** [olmoearth_run_data/mozambique_lulc/model.yaml:236-245]()

## Task Definition and Metrics

The training system uses `SegmentationTask` with comprehensive per-class metrics.

### Segmentation Task Configuration

The segmentation task is configured with the following parameters:

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `num_classes` | 8 | Number of classification classes |
| `zero_is_invalid` | true | Class 0 treated as invalid/ignore |
| `metric_kwargs.average` | "micro" | Micro-averaged overall accuracy |

**Sources:** [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:73-79]()

### Per-Class Metrics

For each of the 7 valid classes (excluding class 0), the system tracks precision and recall:

```mermaid
graph TB
    subgraph "Class Definitions"
        C1["Class 1: Water"]
        C2["Class 2: Bare Ground"]
        C3["Class 3: Rangeland"]
        C4["Class 4: Flooded Vegetation"]
        C5["Class 5: Trees"]
        C6["Class 6: Cropland"]
        C7["Class 7: Buildings"]
    end
    
    subgraph "Metrics Per Class"
        PREC["Precision<br/>MulticlassPrecision<br/>num_classes: 8<br/>average: null"]
        RECALL["Recall<br/>MulticlassRecall<br/>num_classes: 8<br/>average: null"]
    end
    
    subgraph "Metric Implementation"
        SEGMETRIC["SegmentationMetric<br/>class_idx: 1-7<br/>Extracts per-class values"]
    end
    
    C1 --> SEGMETRIC
    C2 --> SEGMETRIC
    C3 --> SEGMETRIC
    C4 --> SEGMETRIC
    C5 --> SEGMETRIC
    C6 --> SEGMETRIC
    C7 --> SEGMETRIC
    
    SEGMETRIC --> PREC
    SEGMETRIC --> RECALL
```

Each metric is defined using the `SegmentationMetric` wrapper that extracts the specific class index from the multi-class metric output:

```yaml
water_precision:
  class_path: rslearn.train.tasks.segmentation.SegmentationMetric
  init_args:
    metric:
      class_path: torchmetrics.classification.MulticlassPrecision
      init_args:
        num_classes: 8
        average: null
    class_idx: 1
```

**Sources:** [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:80-206]()

## Checkpointing and Logging

The training system uses multiple callbacks for model checkpointing and metric logging.

### Model Checkpointing

The `ModelCheckpoint` callback saves model weights based on validation performance:

| Parameter | Value | Description |
|-----------|-------|-------------|
| `save_top_k` | 1 | Save only best checkpoint |
| `save_last` | true | Also save last checkpoint |
| `monitor` | `val_segment/accuracy` | Metric to monitor |
| `mode` | max | Save checkpoint with maximum metric |

This configuration saves two checkpoints: one with the highest validation accuracy and one from the final epoch.

**Sources:** [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:255-260]()

### Learning Rate Monitoring

The `LearningRateMonitor` callback logs the current learning rate:

```yaml
callbacks:
  - class_path: lightning.pytorch.callbacks.LearningRateMonitor
    init_args:
      logging_interval: "epoch"
```

This logs learning rates once per epoch, useful for tracking the `PlateauScheduler` behavior and `FreezeUnfreeze` learning rate adjustments.

**Sources:** [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:252-254]()

### Experiment Tracking

Training experiments are tracked using Weights & Biases:

```yaml
logger:
  class_path: lightning.pytorch.loggers.WandbLogger
  init_args:
    project: ${WANDB_PROJECT}
    name: ${WANDB_NAME}
    entity: ${WANDB_ENTITY}
```

The `rslp_project` and `rslp_experiment` fields at the end of the configuration file provide experiment metadata:

```yaml
rslp_project: 2025_09_18_mozambique_lulc
rslp_experiment: mozambique_lulc_helios_base_S2_ts_ws16_ps1_gaza
```

**Sources:** [olmoearth_run_data/mozambique_lulc/model.yaml:249-254](), [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:266-267]()

## Data Source Configuration

The `dataset.json` file defines how satellite imagery is queried and loaded during training.

### Sentinel-2 Configuration

Sentinel-2 data is configured with temporal mosaicking and harmonization:

```json
{
  "layers": {
    "sentinel2": {
      "band_sets": [{"bands": ["B01", "B02", "B03", "B04", "B05", "B06", "B07", "B08", "B8A", "B09", "B11", "B12"], "dtype": "uint16"}],
      "data_source": {
        "class_path": "rslearn.data_sources.planetary_computer.Sentinel2",
        "ingest": false,
        "init_args": {
          "cache_dir": "cache/planetary_computer",
          "harmonize": true,
          "sort_by": "eo:cloud_cover"
        },
        "query_config": {
          "max_matches": 8,
          "min_matches": 8,
          "period_duration": "30d",
          "space_mode": "PER_PERIOD_MOSAIC"
        }
      },
      "type": "raster"
    }
  }
}
```

Key parameters:

- **harmonize**: `true` - Applies radiometric harmonization across Sentinel-2A/2B satellites
- **max_matches** / **min_matches**: 8 - Loads exactly 8 temporal observations
- **period_duration**: "30d" - Each observation spans a 30-day period
- **space_mode**: "PER_PERIOD_MOSAIC" - Creates cloud-free mosaics within each period
- **sort_by**: "eo:cloud_cover" - Prioritizes images with less cloud coverage

**Sources:** [olmoearth_run_data/mozambique_lulc/dataset.json:25-62]()

### Layer Definitions

The dataset includes three layer types:

| Layer | Type | Bands | Data Type | Purpose |
|-------|------|-------|-----------|---------|
| `sentinel2` | raster | 12 optical bands | uint16 | Input imagery |
| `label` | raster | category | int32 | Ground truth labels |
| `output` | raster | output | float32 | Model predictions |

**Sources:** [olmoearth_run_data/mozambique_lulc/dataset.json:2-24]()

## Training Variants

The repository includes multiple training configuration variants for different tasks and temporal configurations.

### Standard Configuration

- **File**: `rslp_finetuning.yaml`
- **Purpose**: LULC classification using single-timestep Sentinel-2
- **Classes**: 8 (Water, Bare Ground, Rangeland, Flooded Vegetation, Trees, Cropland, Buildings, plus invalid)
- **Groups**: gaza, manica, zambezia provinces

**Sources:** [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:1-268]()

### Crop Type Configuration

- **File**: `rslp_finetuning_croptype.yaml`
- **Purpose**: Crop type classification
- **Classes**: 8 (Corn, Cassava, Rice, Sesame, Beans, Millet, Sorghum, plus invalid)
- **Groups**: crop_type

**Sources:** [olmoearth_run_data/mozambique_lulc/rslp_finetuning_croptype.yaml:1-268]()

### Multi-Timestep Configuration

- **File**: `rslp_finetuning_in_season_novmar.yaml`
- **Purpose**: In-season LULC classification using 5 temporal observations
- **Layers**: `["sentinel2", "sentinel2.1", "sentinel2.2", "sentinel2.3", "sentinel2.4"]`
- **Temporal Coverage**: November-March growing season

This configuration loads 5 separate temporal layers (60 total bands = 12 bands × 5 timesteps) to capture phenological changes during the growing season.

**Sources:** [olmoearth_run_data/mozambique_lulc/rslp_finetuning_in_season_novmar.yaml:54-61]()

---

# Page: Training Configuration Files

# Training Configuration Files

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [olmoearth_run_data/awf/dataset.json](olmoearth_run_data/awf/dataset.json)
- [olmoearth_run_data/awf/olmoearth_run.yaml](olmoearth_run_data/awf/olmoearth_run.yaml)
- [olmoearth_run_data/mozambique_lulc/dataset.json](olmoearth_run_data/mozambique_lulc/dataset.json)
- [olmoearth_run_data/mozambique_lulc/model.yaml](olmoearth_run_data/mozambique_lulc/model.yaml)
- [olmoearth_run_data/mozambique_lulc/olmoearth_run.yaml](olmoearth_run_data/mozambique_lulc/olmoearth_run.yaml)
- [olmoearth_run_data/nandi/dataset.json](olmoearth_run_data/nandi/dataset.json)
- [olmoearth_run_data/nandi/olmoearth_run.yaml](olmoearth_run_data/nandi/olmoearth_run.yaml)

</details>



## Purpose and Scope

This document describes the structure and parameters of the three primary configuration files used to train OlmoEarth models: `model.yaml`, `dataset.json`, and `olmoearth_run.yaml`. These YAML and JSON files define the model architecture, data loading pipelines, training parameters, and inference settings.

For information about the actual training process and callbacks, see [Fine-tuning Process](#5.3). For details about data transforms and the data module implementation, see [Data Module and Transforms](#5.4). For inference pipeline configuration details, see [olmoearth_run Pipeline](#7.1).

## Configuration File Overview

Training an OlmoEarth model requires three configuration files that work together to define the complete training and inference pipeline:

| Configuration File | Purpose | Primary Contents |
|-------------------|---------|------------------|
| `model.yaml` | Training configuration | Model architecture, Lightning module parameters, data module setup, trainer callbacks |
| `dataset.json` | Data source specification | Layer definitions, band configurations, Planetary Computer query parameters |
| `olmoearth_run.yaml` | Inference and data preparation | Window preparation, partitioning strategies, postprocessing, result metadata |

**Configuration File Relationships**

```mermaid
graph TB
    subgraph "Training Phase"
        MODEL_YAML["model.yaml<br/>RslearnLightningModule<br/>RslearnDataModule<br/>Trainer Config"]
        DATASET_JSON["dataset.json<br/>Layer Definitions<br/>Data Sources<br/>Query Config"]
        
        MODEL_YAML -->|"references via<br/>${DATASET_PATH}"| DATASET_JSON
    end
    
    subgraph "Inference Phase"
        RUN_YAML["olmoearth_run.yaml<br/>Partitioning<br/>Postprocessing<br/>Result Metadata"]
        
        MODEL_YAML -.->|"used by"| RUN_YAML
        DATASET_JSON -.->|"used by"| RUN_YAML
    end
    
    subgraph "rslearn Components"
        LIGHTNING["RslearnLightningModule<br/>Training Loop"]
        DATAMODULE["RslearnDataModule<br/>Data Loading"]
        CALLBACKS["Callbacks<br/>FreezeUnfreeze<br/>ModelCheckpoint"]
    end
    
    MODEL_YAML --> LIGHTNING
    MODEL_YAML --> DATAMODULE
    MODEL_YAML --> CALLBACKS
    
    DATASET_JSON --> DATAMODULE
```

**Sources:** [olmoearth_run_data/mozambique_lulc/model.yaml:1-278](), [olmoearth_run_data/mozambique_lulc/dataset.json:1-64](), [olmoearth_run_data/mozambique_lulc/olmoearth_run.yaml:1-81]()

## model.yaml Structure

The `model.yaml` file is the primary training configuration file containing three top-level sections: `model`, `data`, and `trainer`.

### model Section

Defines the Lightning module and model architecture using the `class_path` pattern for component instantiation.

**Model Architecture Hierarchy**

```mermaid
graph TB
    LIGHTNING["RslearnLightningModule"]
    MULTITASK["MultiTaskModel"]
    ENCODER["OlmoEarth<br/>Pre-trained Encoder"]
    DECODER_HEAD["Decoder Pipeline"]
    UPSAMPLE["Upsample<br/>scale_factor: 4"]
    CONV["Conv<br/>in: 768, out: num_classes"]
    SEG_HEAD["SegmentationHead<br/>Task-specific Head"]
    
    LIGHTNING --> MULTITASK
    MULTITASK --> ENCODER
    MULTITASK --> DECODER_HEAD
    DECODER_HEAD --> UPSAMPLE
    UPSAMPLE --> CONV
    CONV --> SEG_HEAD
```

**Sources:** [olmoearth_run_data/mozambique_lulc/model.yaml:1-31]()

**Key Parameters:**

| Parameter | Type | Description | Example Value |
|-----------|------|-------------|---------------|
| `class_path` | string | Fully qualified class name | `rslearn.train.lightning_module.RslearnLightningModule` |
| `encoder.checkpoint_path` | string | Path to pre-trained encoder | `${EXTRA_FILES_PATH}` |
| `encoder.selector` | list | Components to load from checkpoint | `["encoder"]` |
| `encoder.patch_size` | int | Patch size for vision transformer | `4` |
| `decoders` | dict | Task-specific decoder pipelines | See decoder configuration |
| `lr` | float | Learning rate | `0.0001` |
| `plateau` | bool | Enable plateau learning rate scheduler | `true` |
| `plateau_factor` | float | LR reduction factor on plateau | `0.2` |
| `plateau_patience` | int | Epochs to wait before reducing LR | `2` |

**Sources:** [olmoearth_run_data/mozambique_lulc/model.yaml:1-31]()

**Decoder Configuration:**

Decoders are defined per task (e.g., `segment`) as a list of sequential operations:

```yaml
decoders:
  segment:
    - class_path: rslearn.models.upsample.Upsample
      init_args:
        scale_factor: 4
    - class_path: rslearn.models.conv.Conv
      init_args:
        in_channels: 768
        out_channels: 8
        kernel_size: 1
    - class_path: rslearn.train.tasks.segmentation.SegmentationHead
```

**Sources:** [olmoearth_run_data/mozambique_lulc/model.yaml:13-25]()

### data Section

Defines the `RslearnDataModule` configuration including input layers, task definitions, batch processing, and data transforms.

**Data Module Configuration Structure**

```mermaid
graph TB
    DATAMODULE["RslearnDataModule"]
    INPUTS["inputs<br/>sentinel2_l2a<br/>label"]
    TASK["MultiTask<br/>SegmentationTask"]
    CONFIGS["Config Modes<br/>default_config<br/>train_config<br/>val_config<br/>test_config<br/>predict_config"]
    TRANSFORMS["Transforms<br/>Pad<br/>Crop<br/>Flip<br/>OlmoEarthNormalize"]
    
    DATAMODULE --> INPUTS
    DATAMODULE --> TASK
    DATAMODULE --> CONFIGS
    CONFIGS --> TRANSFORMS
```

**Sources:** [olmoearth_run_data/mozambique_lulc/model.yaml:32-245]()

**Input Layer Configuration:**

Each input layer specifies:

| Parameter | Description | Example |
|-----------|-------------|---------|
| `data_type` | Type of data layer | `"raster"` |
| `layers` | Layer names from dataset.json | `["sentinel2"]` |
| `bands` | Band names to load | `["B02", "B03", "B04", ...]` |
| `passthrough` | Pass data through without modification | `true` |
| `dtype` | Data type for loading | `FLOAT32`, `INT32` |
| `is_target` | Indicates target/label data | `true` (for labels) |
| `load_all_item_groups` | Load all temporal groups | `true` |
| `load_all_layers` | Load all layer instances | `true` |

**Sources:** [olmoearth_run_data/mozambique_lulc/model.yaml:36-50]()

**Task Configuration:**

```yaml
task:
  class_path: rslearn.train.tasks.multi_task.MultiTask
  init_args:
    tasks:
      segment:
        class_path: rslearn.train.tasks.segmentation.SegmentationTask
        init_args:
          num_classes: 8
          zero_is_invalid: true
          metric_kwargs:
            average: "micro"
          other_metrics:
            water_precision:
              class_path: rslearn.train.tasks.segmentation.SegmentationMetric
```

The task configuration includes per-class metrics for precision and recall tracking. See [Metrics and Evaluation](#5.5) for details on metric configuration.

**Sources:** [olmoearth_run_data/mozambique_lulc/model.yaml:51-188]()

**Configuration Modes:**

Five configuration modes control data loading behavior for different training phases:

| Config Mode | Purpose | Key Parameters |
|-------------|---------|----------------|
| `default_config` | Shared base configuration | `transforms` (Pad, OlmoEarthNormalize) |
| `train_config` | Training data loading | `transforms` (Pad, Crop, Flip), `groups`, `tags: {split: "train"}` |
| `val_config` | Validation data loading | `patch_size: 16`, `groups`, `tags: {split: "test"}` |
| `test_config` | Test data loading | Same as validation |
| `predict_config` | Inference data loading | `load_all_patches: true`, `overlap_ratio: 0.25`, `skip_targets: true` |

**Sources:** [olmoearth_run_data/mozambique_lulc/model.yaml:194-245]()

**Transform Pipeline:**

Training transforms include data augmentation:

```yaml
train_config:
  transforms:
    - class_path: rslearn.train.transforms.pad.Pad
      init_args:
        size: 31
        mode: "center"
    - class_path: rslearn.train.transforms.crop.Crop
      init_args:
        crop_size: 16
    - class_path: rslearn.train.transforms.flip.Flip
    - class_path: rslearn.models.olmoearth_pretrain.norm.OlmoEarthNormalize
      init_args:
        band_names:
          sentinel2_l2a: ["B02", "B03", "B04", ...]
```

**Sources:** [olmoearth_run_data/mozambique_lulc/model.yaml:206-222]()

### trainer Section

Defines PyTorch Lightning trainer configuration including callbacks, logging, and checkpointing.

**Trainer Component Hierarchy**

```mermaid
graph LR
    TRAINER["Trainer"]
    LOGGER["WandbLogger"]
    CALLBACKS["Callbacks"]
    
    LR_MON["LearningRateMonitor"]
    CKPT["ModelCheckpoint"]
    FREEZE["FreezeUnfreeze"]
    WRITER["RslearnWriter"]
    
    TRAINER --> LOGGER
    TRAINER --> CALLBACKS
    CALLBACKS --> LR_MON
    CALLBACKS --> CKPT
    CALLBACKS --> FREEZE
    CALLBACKS --> WRITER
```

**Sources:** [olmoearth_run_data/mozambique_lulc/model.yaml:246-278]()

**Key Trainer Parameters:**

| Parameter | Value | Description |
|-----------|-------|-------------|
| `max_epochs` | `100` | Maximum training epochs |
| `default_root_dir` | `${TRAINER_DATA_PATH}` | Directory for logs and checkpoints |

**Callback Configuration:**

```yaml
callbacks:
  - class_path: lightning.pytorch.callbacks.LearningRateMonitor
    init_args:
      logging_interval: "epoch"
  
  - class_path: lightning.pytorch.callbacks.ModelCheckpoint
    init_args:
      save_top_k: 1
      save_last: true
      monitor: val_loss
      mode: min
  
  - class_path: rslearn.train.callbacks.freeze_unfreeze.FreezeUnfreeze
    init_args:
      module_selector: ["model", "encoder", 0]
      unfreeze_at_epoch: 2
  
  - class_path: rslearn.train.prediction_writer.RslearnWriter
    init_args:
      path: placeholder
      output_layer: ${PREDICTION_OUTPUT_LAYER}
      selector: ["segment"]
      merger:
        class_path: rslearn.train.prediction_writer.RasterMerger
        init_args:
          padding: 2
```

The `FreezeUnfreeze` callback implements transfer learning by freezing the encoder initially and unfreezing at epoch 2. See [Fine-tuning Process](#5.3) for details.

**Sources:** [olmoearth_run_data/mozambique_lulc/model.yaml:255-278]()

## dataset.json Structure

The `dataset.json` file defines data layers, their band configurations, and data source specifications for querying satellite imagery.

**dataset.json Layer Structure**

```mermaid
graph TB
    DATASET["dataset.json"]
    LAYERS["layers"]
    
    LABEL["label<br/>type: raster<br/>dtype: int32"]
    OUTPUT["output<br/>type: raster<br/>dtype: float32"]
    SENTINEL2["sentinel2<br/>type: raster<br/>dtype: uint16"]
    
    DATA_SOURCE["data_source<br/>Sentinel2<br/>Planetary Computer"]
    QUERY_CFG["query_config<br/>max_matches: 8-12<br/>period_duration: 30d<br/>space_mode: PER_PERIOD_MOSAIC"]
    INIT_ARGS["init_args<br/>harmonize: true<br/>sort_by: eo:cloud_cover"]
    
    DATASET --> LAYERS
    LAYERS --> LABEL
    LAYERS --> OUTPUT
    LAYERS --> SENTINEL2
    
    SENTINEL2 --> DATA_SOURCE
    DATA_SOURCE --> QUERY_CFG
    DATA_SOURCE --> INIT_ARGS
```

**Sources:** [olmoearth_run_data/mozambique_lulc/dataset.json:1-64]()

### Layer Definitions

Each layer contains `band_sets` specifying bands and data types:

```json
{
  "layers": {
    "label": {
      "band_sets": [
        {
          "bands": ["category"],
          "dtype": "int32"
        }
      ],
      "type": "raster"
    },
    "sentinel2": {
      "band_sets": [
        {
          "bands": ["B01", "B02", "B03", "B04", "B05", "B06", 
                    "B07", "B08", "B8A", "B09", "B11", "B12"],
          "dtype": "uint16"
        }
      ],
      "type": "raster",
      "data_source": { ... }
    }
  }
}
```

**Sources:** [olmoearth_run_data/mozambique_lulc/dataset.json:2-62]()

### Data Source Configuration

For Sentinel-2 imagery, the data source configuration specifies:

| Parameter | Description | Example Values |
|-----------|-------------|----------------|
| `class_path` | Data source implementation | `rslearn.data_sources.planetary_computer.Sentinel2` |
| `ingest` | Whether to ingest data locally | `false` |
| `harmonize` | Apply cross-sensor harmonization | `true` |
| `sort_by` | Metadata field for sorting images | `"eo:cloud_cover"` |
| `cache_dir` | Local cache directory | `"cache/planetary_computer"` |

**Sources:** [olmoearth_run_data/mozambique_lulc/dataset.json:45-52]()

### Query Configuration

The `query_config` section controls temporal mosaicking and image selection:

| Parameter | Mozambique LULC | AWF/Nandi | Description |
|-----------|-----------------|-----------|-------------|
| `max_matches` | `8` | `12` | Maximum images per period |
| `min_matches` | `8` | `12` | Minimum images required |
| `period_duration` | `"30d"` | `"30d"` | Duration of each temporal period |
| `space_mode` | `"PER_PERIOD_MOSAIC"` | `"PER_PERIOD_MOSAIC"` | Spatial mosaicking strategy |

**Sources:** [olmoearth_run_data/mozambique_lulc/dataset.json:53-58](), [olmoearth_run_data/awf/dataset.json:53-58](), [olmoearth_run_data/nandi/dataset.json:53-58]()

## olmoearth_run.yaml Structure

The `olmoearth_run.yaml` file configures window preparation, partitioning strategies, postprocessing operations, and inference result metadata. This file is used both for creating training datasets and running inference.

### Window Preparation Configuration

**Window Preparation Pipeline**

```mermaid
graph LR
    INPUT["Point Labels<br/>GPKG File"]
    SAMPLER["NoopSampler"]
    PREPARER["PointToRasterWindowPreparer<br/>window_buffer: 31px<br/>resolution: 10m"]
    SPLITTER["SpatialDataSplitter<br/>train: 75%<br/>val: 25%<br/>grid_size: 128px"]
    OUTPUT["Training Windows<br/>with Split Labels"]
    
    INPUT --> SAMPLER
    SAMPLER --> PREPARER
    PREPARER --> SPLITTER
    SPLITTER --> OUTPUT
```

**Sources:** [olmoearth_run_data/mozambique_lulc/olmoearth_run.yaml:29-48]()

```yaml
window_prep:
  sampler:
    class_path: olmoearth_run.runner.tools.samplers.noop_sampler.NoopSampler
  labeled_window_preparer:
    class_path: olmoearth_run.runner.tools.labeled_window_preparers.point_to_raster_window_preparer.PointToRasterWindowPreparer
    init_args:
      window_buffer: 31  # in pixels
      window_resolution: 10.0
      dtype: INT32
      nodata_value: 255
  data_splitter:
    class_path: olmoearth_run.runner.tools.data_splitters.spatial_data_splitter.SpatialDataSplitter
    init_args:
      train_prop: 0.75
      val_prop: 0.25
      test_prop: 0.0
      grid_size: 128  # in pixels
```

**Sources:** [olmoearth_run_data/mozambique_lulc/olmoearth_run.yaml:29-48]()

### Partitioning Strategies

Two partitioning strategies define hierarchical spatial subdivision:

| Strategy | Grid Size | Purpose | Projection |
|----------|-----------|---------|------------|
| `partition_request_geometry` | `0.25` - `1.0` degrees | Coarse geographic partitioning | WGS84 (EPSG:4326) |
| `prepare_window_geometries` | `1024` pixels | Fine processing windows | EPSG:3857 or UTM (auto-selected) |

```yaml
partition_strategies:
  partition_request_geometry:
    class_path: olmoearth_run.runner.tools.partitioners.grid_partitioner.GridPartitioner
    init_args:
      grid_size: 0.25
  
  prepare_window_geometries:
    class_path: olmoearth_run.runner.tools.partitioners.grid_partitioner.GridPartitioner
    init_args:
      grid_size: 1024
      output_projection:
        class_path: rslearn.utils.geometry.Projection
        init_args:
          crs: EPSG:3857
          x_resolution: 10
          y_resolution: -10
      use_utm: true
```

**Sources:** [olmoearth_run_data/mozambique_lulc/olmoearth_run.yaml:50-67]()

### Postprocessing Strategies

Three-level postprocessing hierarchy for aggregating inference results:

**Postprocessing Hierarchy**

```mermaid
graph TB
    WINDOWS["Individual Windows<br/>Raw Predictions"]
    WINDOW_PP["process_window<br/>NoopRaster"]
    PARTITIONS["Partition Results"]
    PARTITION_PP["process_partition<br/>CombineGeotiff"]
    FINAL["Final Dataset Result"]
    DATASET_PP["process_dataset<br/>CombineGeotiff"]
    
    WINDOWS --> WINDOW_PP
    WINDOW_PP --> PARTITIONS
    PARTITIONS --> PARTITION_PP
    PARTITION_PP --> FINAL
    FINAL --> DATASET_PP
```

**Sources:** [olmoearth_run_data/mozambique_lulc/olmoearth_run.yaml:68-81]()

```yaml
postprocessing_strategies:
  process_window:
    class_path: olmoearth_run.runner.tools.postprocessors.noop_raster.NoopRaster
  
  process_partition:
    class_path: olmoearth_run.runner.tools.postprocessors.combine_geotiff.CombineGeotiff
    init_args:
      nodata_value: 255
  
  process_dataset:
    class_path: olmoearth_run.runner.tools.postprocessors.combine_geotiff.CombineGeotiff
    init_args:
      nodata_value: 255
```

**Sources:** [olmoearth_run_data/mozambique_lulc/olmoearth_run.yaml:68-81]()

### Inference Results Configuration

Defines output metadata including class labels, colors, and value mappings:

```yaml
inference_results_config:
  data_type: RASTER
  classification_fields:
    - property_name: crop_type_classification
      band_index: 1
      allowed_values:
        - value: 1
          label: Water
          color: [136, 33, 233]
        - value: 2
          label: Bare Ground
          color: [124, 67, 18]
        - value: 3
          label: Rangeland
          color: [51, 160, 44]
```

This configuration enables automatic visualization in GIS tools and the OlmoEarth Studio interface.

**Sources:** [olmoearth_run_data/mozambique_lulc/olmoearth_run.yaml:1-27]()

## Environment Variables and Placeholders

Configuration files use environment variable placeholders that are resolved at runtime:

| Placeholder | Description | Typical Value |
|-------------|-------------|---------------|
| `${DATASET_PATH}` | Path to rslearn dataset | `/path/to/dataset.tar` |
| `${EXTRA_FILES_PATH}` | Path to model checkpoint | `/path/to/checkpoint.ckpt` |
| `${TRAINER_DATA_PATH}` | Training output directory | `/path/to/training_output` |
| `${NUM_WORKERS}` | Data loader worker processes | `4` - `16` |
| `${WANDB_PROJECT}` | Weights & Biases project name | `"olmoearth-finetuning"` |
| `${WANDB_NAME}` | Experiment run name | `"mozambique-lulc-v1"` |
| `${WANDB_ENTITY}` | W&B entity/team name | `"allenai"` |
| `${PREDICTION_OUTPUT_LAYER}` | Output layer for predictions | `"output"` |

**Sources:** [olmoearth_run_data/mozambique_lulc/model.yaml:10-11](), [olmoearth_run_data/mozambique_lulc/model.yaml:35-36](), [olmoearth_run_data/mozambique_lulc/model.yaml:248-254](), [olmoearth_run_data/mozambique_lulc/model.yaml:272]()

## Configuration Usage Examples

**Relationship Between Configurations During Training**

```mermaid
graph TB
    ENV_VARS["Environment Variables<br/>DATASET_PATH<br/>EXTRA_FILES_PATH<br/>WANDB_*"]
    
    MODEL_YAML["model.yaml"]
    DATASET_JSON["dataset.json"]
    
    LIGHTNING["RslearnLightningModule<br/>Training Execution"]
    DATAMODULE["RslearnDataModule<br/>Data Loading"]
    ENCODER["OlmoEarth Encoder<br/>from checkpoint"]
    PC_QUERY["Planetary Computer<br/>Sentinel-2 Query"]
    
    ENV_VARS --> MODEL_YAML
    MODEL_YAML -->|"path: ${DATASET_PATH}"| DATASET_JSON
    MODEL_YAML -->|"checkpoint_path"| ENCODER
    
    MODEL_YAML --> LIGHTNING
    MODEL_YAML --> DATAMODULE
    DATASET_JSON --> DATAMODULE
    DATASET_JSON --> PC_QUERY
    
    ENCODER --> LIGHTNING
    PC_QUERY --> DATAMODULE
    DATAMODULE --> LIGHTNING
```

**Sources:** [olmoearth_run_data/mozambique_lulc/model.yaml:1-278](), [olmoearth_run_data/mozambique_lulc/dataset.json:1-64]()

### Common Configuration Patterns

**Multi-temporal Sentinel-2:**
- Mozambique LULC: 8 timesteps, 30-day periods
- AWF/Nandi: 12 timesteps, 30-day periods

**Spatial Resolution:**
- All models use 10m resolution (`x_resolution: 10`, `y_resolution: -10`)
- Window buffers typically 31 pixels (310m total window size)

**Data Splitting:**
- 75% training, 25% validation (standard across projects)
- Grid-based spatial splitting with 128-pixel grid cells

**Transform Pipelines:**
- Training: Pad → Crop → Flip → OlmoEarthNormalize
- Validation/Test: Pad → OlmoEarthNormalize
- Prediction: OlmoEarthNormalize only, with overlap handling

**Sources:** [olmoearth_run_data/mozambique_lulc/dataset.json:53-58](), [olmoearth_run_data/awf/dataset.json:53-58](), [olmoearth_run_data/mozambique_lulc/olmoearth_run.yaml:29-48](), [olmoearth_run_data/mozambique_lulc/model.yaml:194-245]()

---

# Page: OlmoEarth Encoder Architecture

# OlmoEarth Encoder Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [olmoearth_run_data/awf/model.yaml](olmoearth_run_data/awf/model.yaml)
- [olmoearth_run_data/mangrove/dataset.json](olmoearth_run_data/mangrove/dataset.json)
- [olmoearth_run_data/mangrove/model.yaml](olmoearth_run_data/mangrove/model.yaml)
- [olmoearth_run_data/mangrove/olmoearth_run.yaml](olmoearth_run_data/mangrove/olmoearth_run.yaml)
- [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml](olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml)
- [olmoearth_run_data/mozambique_lulc/rslp_finetuning_croptype.yaml](olmoearth_run_data/mozambique_lulc/rslp_finetuning_croptype.yaml)
- [olmoearth_run_data/mozambique_lulc/rslp_finetuning_croptype_in_season_novmar.yaml](olmoearth_run_data/mozambique_lulc/rslp_finetuning_croptype_in_season_novmar.yaml)
- [olmoearth_run_data/mozambique_lulc/rslp_finetuning_in_season_novmar.yaml](olmoearth_run_data/mozambique_lulc/rslp_finetuning_in_season_novmar.yaml)
- [olmoearth_run_data/nandi/model.yaml](olmoearth_run_data/nandi/model.yaml)

</details>



## Purpose and Scope

This document describes the OlmoEarth pre-trained encoder architecture, its initialization parameters, output characteristics, and usage patterns across different fine-tuned models in the repository. The OlmoEarth encoder serves as the foundation model that is fine-tuned for all downstream tasks.

For information about fine-tuning the encoder, see [Fine-tuning Process](#5.3). For configuration file structure, see [Training Configuration Files](#5.1). For the decoder architectures that process encoder outputs, refer to the individual model documentation in [Available Models](#6).

## Encoder Overview

The OlmoEarth encoder is implemented in the `rslearn.models.olmoearth_pretrain.model.OlmoEarth` class. It is a vision transformer-based model pre-trained on diverse satellite imagery to extract spatial features from multispectral remote sensing data.

**Key Characteristics**:
- **Output dimensionality**: 768-channel feature maps
- **Architecture**: Vision transformer with configurable patch sizes
- **Input**: Multi-band satellite imagery (typically 12 Sentinel-2 bands)
- **Pre-training**: Phase 2.0 base model trained on diverse earth observation datasets

The encoder is used consistently across all models in the repository as the feature extraction backbone, with task-specific decoder heads attached for different applications.

**Sources**: [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:7-16](), [olmoearth_run_data/mangrove/model.yaml:9-13](), [olmoearth_run_data/awf/model.yaml:7-11]()

## Architecture Structure

The following diagram illustrates the OlmoEarth encoder architecture and its position in the complete model pipeline:

```mermaid
graph TB
    subgraph "Input Data"
        S2["Sentinel-2 L2A<br/>12 bands<br/>(B02, B03, B04, B08,<br/>B05, B06, B07, B8A,<br/>B11, B12, B01, B09)"]
    end
    
    subgraph "Normalization"
        NORM["OlmoEarthNormalize<br/>rslearn.models.olmoearth_pretrain.norm"]
    end
    
    subgraph "OlmoEarth Encoder"
        PATCH["Patch Embedding<br/>patch_size: 1, 2, or 4"]
        TRANSFORMER["Vision Transformer<br/>Pre-trained Weights<br/>768-dimensional embeddings"]
        SELECTOR["Component Selector<br/>selector: ['encoder']"]
    end
    
    subgraph "Encoder Output"
        FEATURES["Feature Maps<br/>768 channels<br/>Spatial resolution /<br/>patch_size"]
    end
    
    subgraph "Task-Specific Decoders"
        UPSAMPLE["Upsample<br/>scale_factor: patch_size"]
        CONV["Conv 1x1<br/>768 → num_classes"]
        HEAD["SegmentationHead"]
    end
    
    S2 --> NORM
    NORM --> PATCH
    PATCH --> TRANSFORMER
    TRANSFORMER --> SELECTOR
    SELECTOR --> FEATURES
    
    FEATURES --> UPSAMPLE
    UPSAMPLE --> CONV
    CONV --> HEAD
```

**Sources**: [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:7-38](), [olmoearth_run_data/mangrove/model.yaml:9-25]()

## Initialization Methods

The OlmoEarth encoder supports two initialization methods:

### Method 1: Model ID (Recommended)

Uses a pre-defined model identifier to load the foundation model from a standard location:

```yaml
encoder:
  - class_path: rslearn.models.olmoearth_pretrain.model.OlmoEarth
    init_args:
      model_id: OLMOEARTH_V1_BASE
      patch_size: 4
```

This method automatically handles checkpoint loading and is used by most models in the repository.

### Method 2: Direct Checkpoint Path

Specifies an explicit path to a checkpoint file with additional control over component selection:

```yaml
encoder:
  - class_path: rslearn.models.olmoearth_pretrain.model.OlmoEarth
    init_args:
      checkpoint_path: /weka/dfive-default/helios/checkpoints/joer/phase2.0_base_lr0.0001_wd0.02/step667200
      selector:
        - encoder
      patch_size: 4
      random_initialization: false
      embedding_size: null
      autocast_dtype: bfloat16
```

This method provides fine-grained control and is used when working with specific checkpoint versions during development.

**Sources**: [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:7-16](), [olmoearth_run_data/mangrove/model.yaml:9-13](), [olmoearth_run_data/awf/model.yaml:8-11]()

## Configuration Parameters

The following table describes all initialization parameters for the OlmoEarth encoder:

| Parameter | Type | Required | Description | Common Values |
|-----------|------|----------|-------------|---------------|
| `model_id` | string | Yes (Method 1) | Pre-defined model identifier | `OLMOEARTH_V1_BASE` |
| `checkpoint_path` | string | Yes (Method 2) | Explicit path to checkpoint file | `/weka/dfive-default/helios/checkpoints/...` |
| `patch_size` | integer | Yes | Size of image patches for transformer | `1`, `2`, `4` |
| `selector` | list | No | Components to load from checkpoint | `["encoder"]` |
| `random_initialization` | boolean | No | Whether to use random weights instead of pre-trained | `false` |
| `embedding_size` | integer | No | Custom embedding dimension (null uses default) | `null` (768) |
| `autocast_dtype` | string | No | Data type for automatic mixed precision | `bfloat16` |

### Patch Size Selection

The `patch_size` parameter determines the spatial downsampling factor applied by the encoder:

- **patch_size=1**: No spatial downsampling, highest resolution output (used in Nandi model)
- **patch_size=2**: 2x downsampling, balanced efficiency (used in Mangrove model)
- **patch_size=4**: 4x downsampling, most efficient (used in Mozambique LULC, AWF models)

The decoder must compensate for this downsampling with an upsampling layer of corresponding `scale_factor`.

**Sources**: [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:8-16](), [olmoearth_run_data/nandi/model.yaml:8-11](), [olmoearth_run_data/mangrove/model.yaml:10-13]()

## Encoder Initialization Flow

```mermaid
graph TD
    START["Model Initialization"]
    METHOD{"Initialization<br/>Method?"}
    
    subgraph "Method 1: Model ID"
        MODEL_ID["model_id:<br/>OLMOEARTH_V1_BASE"]
        RESOLVE["Resolve to<br/>Standard Checkpoint<br/>Location"]
    end
    
    subgraph "Method 2: Checkpoint Path"
        CHECKPOINT["checkpoint_path:<br/>/weka/.../step667200"]
        SELECTOR["selector:<br/>['encoder']"]
        LOAD_COMP["Load Specific<br/>Components"]
    end
    
    subgraph "Common Initialization"
        PATCH_CFG["Configure<br/>patch_size"]
        DTYPE["Set autocast_dtype:<br/>bfloat16"]
        WEIGHTS["Load Pre-trained<br/>Weights"]
    end
    
    ENCODER["OlmoEarth Encoder<br/>Ready for Fine-tuning"]
    
    START --> METHOD
    METHOD -->|"model_id"| MODEL_ID
    METHOD -->|"checkpoint_path"| CHECKPOINT
    
    MODEL_ID --> RESOLVE
    RESOLVE --> PATCH_CFG
    
    CHECKPOINT --> SELECTOR
    SELECTOR --> LOAD_COMP
    LOAD_COMP --> PATCH_CFG
    
    PATCH_CFG --> DTYPE
    DTYPE --> WEIGHTS
    WEIGHTS --> ENCODER
```

**Sources**: [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:7-16](), [olmoearth_run_data/mangrove/model.yaml:9-13]()

## Output Characteristics

The OlmoEarth encoder produces feature maps with the following properties:

### Spatial Dimensions

For an input image of size `(B, C, H, W)`:
- Output size: `(B, 768, H/patch_size, W/patch_size)`
- Batch dimension preserved
- Channel dimension fixed at 768
- Spatial dimensions downsampled by `patch_size`

### Feature Representation

- **Channels**: 768 feature channels
- **Data type**: Typically `bfloat16` for memory efficiency
- **Semantic content**: Multi-scale spatial features learned from diverse satellite imagery
- **Usage**: Input to task-specific decoder heads

### Example Output Shapes

| Input Size | patch_size | Output Size |
|------------|------------|-------------|
| (32, 12, 64, 64) | 1 | (32, 768, 64, 64) |
| (32, 12, 64, 64) | 2 | (32, 768, 32, 32) |
| (32, 12, 64, 64) | 4 | (32, 768, 16, 16) |

The decoder architecture must account for this spatial downsampling and typically includes an upsampling layer.

**Sources**: [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:19-27](), [olmoearth_run_data/awf/model.yaml:14-24]()

## Integration with MultiTaskModel

The OlmoEarth encoder is used within the `rslearn.models.multitask.MultiTaskModel` wrapper, which provides the interface for connecting encoders to task-specific decoders:

```mermaid
graph LR
    subgraph "MultiTaskModel Structure"
        INPUT["Input:<br/>sentinel2_l2a"]
        
        subgraph "Encoder Component"
            OLMOEARTH["rslearn.models.olmoearth_pretrain.model.OlmoEarth<br/>Output: 768 channels"]
        end
        
        subgraph "Decoder Component"
            DECODER_UPSAMPLE["rslearn.models.upsample.Upsample<br/>scale_factor: patch_size"]
            DECODER_CONV["rslearn.models.conv.Conv<br/>768 → num_classes"]
            DECODER_PICK["rslearn.models.pick_features.PickFeatures"]
            DECODER_HEAD["rslearn.train.tasks.segmentation.SegmentationHead"]
        end
        
        OUTPUT["Output:<br/>Per-pixel predictions"]
    end
    
    INPUT --> OLMOEARTH
    OLMOEARTH --> DECODER_UPSAMPLE
    DECODER_UPSAMPLE --> DECODER_CONV
    DECODER_CONV --> DECODER_PICK
    DECODER_PICK --> DECODER_HEAD
    DECODER_HEAD --> OUTPUT
```

Configuration structure:

```yaml
model:
  class_path: rslearn.models.multitask.MultiTaskModel
  init_args:
    encoder:
      - class_path: rslearn.models.olmoearth_pretrain.model.OlmoEarth
        init_args:
          model_id: OLMOEARTH_V1_BASE
          patch_size: 4
    decoders:
      segment:
        - class_path: rslearn.models.upsample.Upsample
          init_args:
            scale_factor: 4
        - class_path: rslearn.models.conv.Conv
          init_args:
            in_channels: 768
            out_channels: 8
```

**Sources**: [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:4-38](), [olmoearth_run_data/mangrove/model.yaml:4-26]()

## Usage Patterns Across Models

Different models in the repository use varying encoder configurations based on their specific requirements:

### Patch Size Selection by Model

| Model | patch_size | Reasoning |
|-------|------------|-----------|
| Mozambique LULC | 4 | Efficient training with acceptable spatial detail |
| Mozambique Crop Type | 4 | Consistent with LULC model, same dataset |
| Mangrove Extent | 2 | Balance between detail and efficiency for coastline mapping |
| Nandi Crop Classification | 1 | Maximum spatial resolution for fine-grained crop boundaries |
| AWF Land Cover | 4 | Large-area mapping with computational efficiency |
| Ecosystem Type Mapping | Not specified in provided files | |
| LFMC | Not specified in provided files | |

### Decoder Architecture Patterns

**Pattern 1: Upsample + Conv (Most Common)**

Used by: Mozambique LULC, AWF, Nandi

```yaml
decoders:
  segment:
    - class_path: rslearn.models.upsample.Upsample
      init_args:
        scale_factor: 4
        mode: bilinear
    - class_path: rslearn.models.conv.Conv
      init_args:
        in_channels: 768
        out_channels: [num_classes]
        kernel_size: 1
```

**Pattern 2: Pooling Decoder**

Used by: Mangrove model

```yaml
decoders:
  mangrove_classification:
    - class_path: rslearn.models.pooling_decoder.SegmentationPoolingDecoder
      init_args:
        in_channels: 768
        out_channels: 4
        num_conv_layers: 0
        num_fc_layers: 0
```

**Sources**: [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:17-38](), [olmoearth_run_data/mangrove/model.yaml:14-26](), [olmoearth_run_data/nandi/model.yaml:8-24](), [olmoearth_run_data/awf/model.yaml:8-24]()

## Encoder Configuration Examples

### Example 1: Standard Fine-tuning Configuration

```yaml
model:
  class_path: rslearn.train.lightning_module.RslearnLightningModule
  init_args:
    model:
      class_path: rslearn.models.multitask.MultiTaskModel
      init_args:
        encoder:
          - class_path: rslearn.models.olmoearth_pretrain.model.OlmoEarth
            init_args:
              model_id: OLMOEARTH_V1_BASE
              patch_size: 4
        decoders:
          segment:
            - class_path: rslearn.models.upsample.Upsample
              init_args:
                scale_factor: 4
                mode: bilinear
            - class_path: rslearn.models.conv.Conv
              init_args:
                in_channels: 768
                out_channels: 10
                kernel_size: 1
            - class_path: rslearn.train.tasks.segmentation.SegmentationHead
```

**Sources**: [olmoearth_run_data/awf/model.yaml:1-24]()

### Example 2: Development Configuration with Explicit Checkpoint

```yaml
model:
  class_path: rslearn.train.lightning_module.RslearnLightningModule
  init_args:
    model:
      class_path: rslearn.models.multitask.MultiTaskModel
      init_args:
        encoder:
          - class_path: rslearn.models.olmoearth_pretrain.model.OlmoEarth
            init_args:
              checkpoint_path: /weka/dfive-default/helios/checkpoints/joer/phase2.0_base_lr0.0001_wd0.02/step667200
              selector:
                - encoder
              patch_size: 4
              random_initialization: false
              embedding_size: null
              autocast_dtype: bfloat16
```

**Sources**: [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:1-16]()

### Example 3: High-Resolution Configuration

```yaml
encoder:
  - class_path: rslearn.models.olmoearth_pretrain.model.OlmoEarth
    init_args:
      model_id: OLMOEARTH_V1_BASE
      patch_size: 1  # No downsampling
decoders:
  segment:
    - class_path: rslearn.models.upsample.Upsample
      init_args:
        scale_factor: 1  # No upsampling needed
```

**Sources**: [olmoearth_run_data/nandi/model.yaml:7-16]()

## Input Data Requirements

The OlmoEarth encoder expects normalized input data with specific band configurations:

### Expected Input Format

```yaml
inputs:
  sentinel2_l2a:
    data_type: "raster"
    layers: ["sentinel2"]
    bands: ["B02", "B03", "B04", "B08", "B05", "B06", "B07", "B8A", "B11", "B12", "B01", "B09"]
    passthrough: true
    dtype: FLOAT32
    load_all_item_groups: true
    load_all_layers: true
```

### Normalization Requirements

All models use `rslearn.models.olmoearth_pretrain.norm.OlmoEarthNormalize` to prepare input data:

```yaml
transforms:
  - class_path: rslearn.models.olmoearth_pretrain.norm.OlmoEarthNormalize
    init_args:
      band_names:
        sentinel2_l2a: ["B02", "B03", "B04", "B08", "B05", "B06", "B07", "B8A", "B11", "B12", "B01", "B09"]
      std_multiplier: 2.0  # Optional, default varies by model
```

This normalization is applied in both training and inference to ensure consistent preprocessing. See [Data Module and Transforms](#5.4) for detailed information about normalization.

**Sources**: [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:54-62](), [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:214-217](), [olmoearth_run_data/mangrove/model.yaml:59-83](), [olmoearth_run_data/mangrove/model.yaml:270-286]()

## Encoder Freezing and Unfreezing

During fine-tuning, the encoder is typically frozen initially and then unfrozen later in training using the `FreezeUnfreeze` callback. This is configured at the trainer level:

```yaml
trainer:
  callbacks:
    - class_path: rslearn.train.callbacks.freeze_unfreeze.FreezeUnfreeze
      init_args:
        module_selector: ["model", "encoder", 0]
        unfreeze_at_epoch: 20
        unfreeze_lr_factor: 10
```

The `module_selector` path `["model", "encoder", 0]` refers to:
- `"model"`: The MultiTaskModel instance
- `"encoder"`: The encoder list within MultiTaskModel
- `0`: The first (and typically only) encoder in the list

This strategy allows the task-specific decoder to train first, then fine-tunes the entire model including encoder weights. See [Fine-tuning Process](#5.3) for more details.

**Sources**: [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:261-265](), [olmoearth_run_data/mangrove/model.yaml:379-386](), [olmoearth_run_data/awf/model.yaml:303-307]()

## Model Component References

The following table maps configuration elements to their implementation classes in the rslearn framework:

| Configuration Class Path | Purpose | Location in Pipeline |
|-------------------------|---------|---------------------|
| `rslearn.models.olmoearth_pretrain.model.OlmoEarth` | Main encoder class | Feature extraction |
| `rslearn.models.olmoearth_pretrain.norm.OlmoEarthNormalize` | Input normalization | Preprocessing |
| `rslearn.models.multitask.MultiTaskModel` | Encoder-decoder wrapper | Model container |
| `rslearn.models.upsample.Upsample` | Spatial upsampling | Decoder |
| `rslearn.models.conv.Conv` | Convolutional layers | Decoder |
| `rslearn.models.pooling_decoder.SegmentationPoolingDecoder` | Alternative decoder | Decoder (Mangrove) |
| `rslearn.train.tasks.segmentation.SegmentationHead` | Final output layer | Task head |
| `rslearn.train.callbacks.freeze_unfreeze.FreezeUnfreeze` | Progressive unfreezing | Training strategy |

**Sources**: [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:1-267](), [olmoearth_run_data/mangrove/model.yaml:1-394]()

---

# Page: Fine-tuning Process

# Fine-tuning Process

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml](olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml)
- [olmoearth_run_data/mozambique_lulc/rslp_finetuning_croptype.yaml](olmoearth_run_data/mozambique_lulc/rslp_finetuning_croptype.yaml)
- [olmoearth_run_data/mozambique_lulc/rslp_finetuning_croptype_in_season_novapr.yaml](olmoearth_run_data/mozambique_lulc/rslp_finetuning_croptype_in_season_novapr.yaml)
- [olmoearth_run_data/mozambique_lulc/rslp_finetuning_croptype_in_season_novmar.yaml](olmoearth_run_data/mozambique_lulc/rslp_finetuning_croptype_in_season_novmar.yaml)
- [olmoearth_run_data/mozambique_lulc/rslp_finetuning_croptype_in_season_novmay.yaml](olmoearth_run_data/mozambique_lulc/rslp_finetuning_croptype_in_season_novmay.yaml)
- [olmoearth_run_data/mozambique_lulc/rslp_finetuning_in_season_novapr.yaml](olmoearth_run_data/mozambique_lulc/rslp_finetuning_in_season_novapr.yaml)
- [olmoearth_run_data/mozambique_lulc/rslp_finetuning_in_season_novmar.yaml](olmoearth_run_data/mozambique_lulc/rslp_finetuning_in_season_novmar.yaml)
- [olmoearth_run_data/mozambique_lulc/rslp_finetuning_in_season_novmay.yaml](olmoearth_run_data/mozambique_lulc/rslp_finetuning_in_season_novmay.yaml)

</details>



## Purpose and Scope

This document describes the fine-tuning workflow for OlmoEarth models in the olmoearth_projects repository. It covers the progressive training strategy using the `FreezeUnfreeze` callback, learning rate scheduling with `PlateauScheduler`, and checkpoint management during training. The fine-tuning process enables transfer learning from the pre-trained OlmoEarth encoder to domain-specific tasks.

For configuration file structure, see [Training Configuration Files](#5.1). For encoder architecture details, see [OlmoEarth Encoder Architecture](#5.2). For data loading specifics, see [Data Module and Transforms](#5.4). For evaluation metrics, see [Metrics and Evaluation](#5.5).

---

## Fine-tuning Workflow Overview

The fine-tuning process uses PyTorch Lightning's `RslearnLightningModule` to orchestrate training with a two-phase strategy: initial training with a frozen encoder followed by unfrozen full-model training.

```mermaid
graph TB
    subgraph "Initialization Phase"
        CONFIG["rslp_finetuning.yaml<br/>Configuration File"]
        CHECKPOINT["OlmoEarth Checkpoint<br/>/weka/.../step667200"]
        DATASET["rslearn Dataset<br/>/weka/.../mozambique_lulc/20251202"]
    end
    
    subgraph "Model Setup"
        LIGHTNING["RslearnLightningModule<br/>lr: 0.0001"]
        MULTITASK["MultiTaskModel"]
        ENCODER["OlmoEarth Encoder<br/>768 channels<br/>patch_size: 4"]
        DECODER["Segmentation Decoder<br/>Upsample + Conv<br/>out_channels: 8"]
    end
    
    subgraph "Training Callbacks"
        FREEZE["FreezeUnfreeze<br/>module_selector: ['model','encoder',0]<br/>unfreeze_at_epoch: 20<br/>unfreeze_lr_factor: 10"]
        SCHEDULER["PlateauScheduler<br/>factor: 0.2<br/>patience: 2<br/>cooldown: 10"]
        CHECKPOINT_CB["ModelCheckpoint<br/>monitor: val_segment/accuracy<br/>save_top_k: 1<br/>save_last: true"]
        LR_MONITOR["LearningRateMonitor<br/>logging_interval: epoch"]
    end
    
    subgraph "Training Phases"
        PHASE1["Phase 1: Epochs 0-19<br/>Encoder: FROZEN<br/>Decoder: TRAINABLE<br/>LR: 0.0001"]
        PHASE2["Phase 2: Epochs 20-99<br/>Encoder: TRAINABLE<br/>Decoder: TRAINABLE<br/>Encoder LR: 0.001<br/>Decoder LR: 0.0001"]
    end
    
    subgraph "Output"
        BEST["Best Checkpoint<br/>Highest val_segment/accuracy"]
        LAST["Last Checkpoint<br/>Final training state"]
    end
    
    CONFIG --> LIGHTNING
    CHECKPOINT --> ENCODER
    DATASET --> LIGHTNING
    
    LIGHTNING --> MULTITASK
    MULTITASK --> ENCODER
    MULTITASK --> DECODER
    
    FREEZE --> LIGHTNING
    SCHEDULER --> LIGHTNING
    CHECKPOINT_CB --> LIGHTNING
    LR_MONITOR --> LIGHTNING
    
    LIGHTNING --> PHASE1
    PHASE1 --> PHASE2
    
    PHASE2 --> BEST
    PHASE2 --> LAST
```

**Sources:** [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:1-268]()

---

## FreezeUnfreeze Callback

The `FreezeUnfreeze` callback implements progressive training by initially freezing the pre-trained encoder and unfreezing it after a specified number of epochs. This strategy allows the decoder to learn task-specific features before fine-tuning the encoder.

### Configuration Parameters

| Parameter | Value | Description |
|-----------|-------|-------------|
| `module_selector` | `["model", "encoder", 0]` | Selects the encoder module within the model hierarchy |
| `unfreeze_at_epoch` | `20` | Epoch at which the encoder is unfrozen |
| `unfreeze_lr_factor` | `10` | Learning rate multiplier applied to encoder when unfrozen |

### Behavior Over Training

```mermaid
graph LR
    subgraph "Epochs 0-19: Frozen Encoder Phase"
        E0["Epoch 0<br/>━━━━━━━━━━<br/>Encoder: FROZEN<br/>Decoder: lr=0.0001"]
        E10["Epoch 10<br/>━━━━━━━━━━<br/>Encoder: FROZEN<br/>Decoder: lr=0.0001"]
        E19["Epoch 19<br/>━━━━━━━━━━<br/>Encoder: FROZEN<br/>Decoder: lr=0.0001"]
    end
    
    subgraph "Epoch 20: Transition"
        UNFREEZE["FreezeUnfreeze.on_train_epoch_start<br/>━━━━━━━━━━<br/>Action: Unfreeze encoder<br/>Set encoder LR: 0.0001 × 10 = 0.001"]
    end
    
    subgraph "Epochs 20-99: Full Training Phase"
        E20["Epoch 20<br/>━━━━━━━━━━<br/>Encoder: lr=0.001<br/>Decoder: lr=0.0001"]
        E50["Epoch 50<br/>━━━━━━━━━━<br/>Encoder: lr=0.001 or lower<br/>Decoder: lr=0.0001 or lower"]
        E99["Epoch 99<br/>━━━━━━━━━━<br/>Encoder: lr varies<br/>Decoder: lr varies"]
    end
    
    E0 --> E10
    E10 --> E19
    E19 --> UNFREEZE
    UNFREEZE --> E20
    E20 --> E50
    E50 --> E99
```

### Module Selection Mechanism

The `module_selector` parameter `["model", "encoder", 0]` traverses the model hierarchy:

1. Start at `RslearnLightningModule.model`
2. Access `MultiTaskModel.encoder`
3. Select element `0` (the `OlmoEarth` encoder in the encoder list)

This targets the pre-trained encoder while leaving the decoder trainable throughout.

**Sources:** [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:261-265]()

---

## Learning Rate Scheduling

The `PlateauScheduler` dynamically adjusts learning rates based on validation performance, enabling adaptive learning throughout training.

### PlateauScheduler Configuration

```yaml
scheduler:
  class_path: rslearn.train.scheduler.PlateauScheduler
  init_args:
    factor: 0.2        # Multiply LR by 0.2 when reducing
    patience: 2        # Wait 2 epochs of no improvement
    min_lr: 0          # Minimum allowed learning rate
    cooldown: 10       # Wait 10 epochs after reduction
```

### Learning Rate Adjustment Logic

```mermaid
stateDiagram-v2
    [*] --> Monitoring
    
    Monitoring --> Evaluating: End of epoch
    Evaluating --> Monitoring: val_segment/accuracy improves
    Evaluating --> Waiting: val_segment/accuracy plateaus
    
    Waiting --> Waiting: patience counter < 2
    Waiting --> Reducing: patience counter = 2
    
    Reducing --> Cooldown: LR = LR × 0.2
    Cooldown --> Cooldown: cooldown counter < 10
    Cooldown --> Monitoring: cooldown counter = 10
    
    note right of Reducing
        New LR applied to
        all parameter groups
    end note
    
    note right of Cooldown
        No LR changes during
        cooldown period
    end note
```

### Learning Rate Evolution Example

| Epoch | Event | Encoder LR | Decoder LR | Notes |
|-------|-------|------------|------------|-------|
| 0-19 | Frozen encoder | N/A | 0.0001 | Decoder training only |
| 20 | Unfreeze trigger | 0.001 | 0.0001 | 10× boost for encoder |
| 20-40 | Steady training | 0.001 | 0.0001 | Both components training |
| 41 | Plateau detected | 0.0002 | 0.00002 | Reduced by factor 0.2 |
| 41-50 | Cooldown | 0.0002 | 0.00002 | No further reductions |
| 65 | Second plateau | 0.00004 | 0.000004 | Reduced again |
| 65-74 | Cooldown | 0.00004 | 0.000004 | Monitoring resumes after |

**Sources:** [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:43-49]()

---

## Training Phase Dynamics

### Phase 1: Decoder-Only Training (Epochs 0-19)

During the initial phase, the OlmoEarth encoder parameters remain frozen while the decoder learns task-specific patterns.

**Trainable Parameters:**
- `Upsample` layer: scale_factor=4, mode=bilinear
- `Conv` layer: 768 input channels → 8 output channels
- `SegmentationHead` task-specific components

**Frozen Parameters:**
- All OlmoEarth encoder weights (loaded from checkpoint)
- Encoder normalization layers
- Encoder attention mechanisms

**Rationale:** The frozen encoder provides stable, pre-trained features while the decoder adapts to the segmentation task. This prevents catastrophic forgetting of the pre-trained representations.

### Phase 2: Full-Model Fine-tuning (Epochs 20-99)

After epoch 20, the encoder is unfrozen with a higher learning rate, allowing end-to-end optimization.

**Learning Rate Configuration:**
```python
# At epoch 20, FreezeUnfreeze applies:
encoder_lr = base_lr * unfreeze_lr_factor  # 0.0001 × 10 = 0.001
decoder_lr = base_lr                        # 0.0001
```

**Parameter Group Structure:**
```mermaid
graph TB
    OPTIMIZER["Optimizer<br/>torch.optim.AdamW"]
    
    GROUP1["Parameter Group 0<br/>Encoder Parameters<br/>lr: 0.001"]
    GROUP2["Parameter Group 1<br/>Decoder Parameters<br/>lr: 0.0001"]
    
    OPTIMIZER --> GROUP1
    OPTIMIZER --> GROUP2
    
    GROUP1 --> ENCODER_PARAMS["encoder.transformer.layers[*]<br/>encoder.patch_embed<br/>encoder.pos_embed"]
    GROUP2 --> DECODER_PARAMS["decoders.segment.0 (Upsample)<br/>decoders.segment.1 (Conv)<br/>decoders.segment.3 (SegmentationHead)"]
```

**Rationale:** The higher encoder learning rate (10×) enables rapid adaptation to task-specific patterns while the lower decoder rate maintains stability in the already-trained decoder weights.

**Sources:** [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:7-41](), [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:261-265]()

---

## Checkpoint Management

### ModelCheckpoint Callback

The `ModelCheckpoint` callback saves model states during training based on validation performance.

```yaml
callbacks:
  - class_path: lightning.pytorch.callbacks.ModelCheckpoint
    init_args:
      save_top_k: 1                      # Keep only the best checkpoint
      save_last: true                    # Also save the last checkpoint
      monitor: val_segment/accuracy      # Metric to track
      mode: max                          # Higher is better
```

### Checkpoint Saving Strategy

```mermaid
flowchart TD
    START["Training Epoch Completes"]
    VALIDATE["Run Validation"]
    COMPUTE["Compute val_segment/accuracy"]
    
    CHECK_BEST{"accuracy ><br/>previous best?"}
    CHECK_LAST{"Is last<br/>epoch?"}
    
    SAVE_BEST["Save Best Checkpoint<br/>Filename: best.ckpt<br/>Delete previous best"]
    SAVE_LAST["Save Last Checkpoint<br/>Filename: last.ckpt<br/>Overwrite previous"]
    
    CONTINUE["Continue Training"]
    END["Training Complete"]
    
    START --> VALIDATE
    VALIDATE --> COMPUTE
    COMPUTE --> CHECK_BEST
    
    CHECK_BEST -->|Yes| SAVE_BEST
    CHECK_BEST -->|No| CHECK_LAST
    SAVE_BEST --> CHECK_LAST
    
    CHECK_LAST -->|Yes| SAVE_LAST
    CHECK_LAST -->|No| CONTINUE
    SAVE_LAST --> END
    
    CONTINUE --> START
```

### Checkpoint Contents

Saved checkpoints contain:
- Model state_dict: All trainable parameters
- Optimizer state_dict: Momentum and learning rate history
- Epoch number: Current training progress
- Global step: Total batches processed
- Callback states: FreezeUnfreeze freeze status, PlateauScheduler history
- Hyperparameters: From configuration file
- Metric values: Best validation accuracy

**Sources:** [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:255-260]()

---

## Training Configuration Summary

### Core Training Parameters

| Parameter | Value | Location | Purpose |
|-----------|-------|----------|---------|
| `max_epochs` | 100 | `trainer.max_epochs` | Maximum training duration |
| `batch_size` | 64 | `data.init_args.batch_size` | Samples per training batch |
| `num_workers` | 32 | `data.init_args.num_workers` | Data loading parallelism |
| `lr` | 0.0001 | `model.init_args.lr` | Base learning rate |
| `crop_size` | 16 | `train_config.transforms` | Training patch size |
| `patch_size` | 16 | `val_config.patch_size` | Validation patch size |

### Callback Hierarchy

```mermaid
graph TB
    TRAINER["PyTorch Lightning Trainer<br/>max_epochs: 100"]
    
    CB1["LearningRateMonitor<br/>━━━━━━━━━━<br/>Logs LR every epoch"]
    CB2["ModelCheckpoint<br/>━━━━━━━━━━<br/>Saves best & last"]
    CB3["FreezeUnfreeze<br/>━━━━━━━━━━<br/>Unfreezes at epoch 20"]
    
    HOOK1["on_train_epoch_start"]
    HOOK2["on_validation_end"]
    HOOK3["on_train_batch_start"]
    
    TRAINER --> CB1
    TRAINER --> CB2
    TRAINER --> CB3
    
    CB1 -.->|calls| HOOK1
    CB2 -.->|calls| HOOK2
    CB3 -.->|calls| HOOK1
    
    HOOK1 --> ACTION1["Log current LR"]
    HOOK1 --> ACTION2["Check epoch == 20<br/>Unfreeze encoder"]
    HOOK2 --> ACTION3["Compare val_segment/accuracy<br/>Save if improved"]
```

**Sources:** [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:249-268]()

---

## Seasonal and Multi-Temporal Variants

The repository includes fine-tuning configurations for different temporal resolutions and seasonal windows.

### Temporal Configuration Variants

| Variant | Layers Configuration | Use Case |
|---------|---------------------|----------|
| Single timestep | `["sentinel2"]` | Year-round LULC/crop type |
| 5 timesteps | `["sentinel2", "sentinel2.1", ..., "sentinel2.4"]` | In-season (Nov-Mar) |
| 6 timesteps | `["sentinel2", "sentinel2.1", ..., "sentinel2.5"]` | Extended season (Nov-Apr) |
| 7 timesteps | `["sentinel2", "sentinel2.1", ..., "sentinel2.6"]` | Full season (Nov-May) |

### Multi-Temporal Training Example

```yaml
# rslp_finetuning_in_season_novmar.yaml
inputs:
  sentinel2_l2a:
    layers: ["sentinel2", "sentinel2.1", "sentinel2.2", "sentinel2.3", "sentinel2.4"]
    bands: ["B02", "B03", "B04", "B08", "B05", "B06", "B07", "B8A", "B11", "B12", "B01", "B09"]
    load_all_layers: true
```

**Impact on Training:**
- Input channels multiply by number of timesteps (e.g., 12 bands × 5 timesteps = 60 channels)
- Encoder processes concatenated temporal stack
- Increased memory requirements during training
- Improved temporal feature extraction for phenology-dependent tasks

**Sources:** [olmoearth_run_data/mozambique_lulc/rslp_finetuning_in_season_novmar.yaml:54-61](), [olmoearth_run_data/mozambique_lulc/rslp_finetuning_in_season_novapr.yaml:54-61](), [olmoearth_run_data/mozambique_lulc/rslp_finetuning_in_season_novmay.yaml:54-61]()

---

## Training Execution Flow

### Complete Training Loop

```mermaid
sequenceDiagram
    participant Trainer as PyTorch Lightning Trainer
    participant Module as RslearnLightningModule
    participant DataModule as RslearnDataModule
    participant Model as MultiTaskModel
    participant Callbacks as Callbacks (FreezeUnfreeze, etc)
    
    Trainer->>DataModule: setup("fit")
    DataModule->>DataModule: Load dataset from WEKA
    DataModule->>DataModule: Create train/val dataloaders
    
    Trainer->>Module: Initialize with config
    Module->>Model: Create MultiTaskModel
    Model->>Model: Load OlmoEarth checkpoint
    Model->>Model: Initialize decoder
    
    Trainer->>Callbacks: on_fit_start()
    Callbacks->>Module: Freeze encoder (epoch < 20)
    
    loop For each epoch (0 to 99)
        Trainer->>Callbacks: on_train_epoch_start()
        Callbacks->>Module: Check if epoch == 20, unfreeze
        
        loop For each training batch
            Trainer->>DataModule: Get batch
            DataModule-->>Trainer: Return (sentinel2_l2a, label)
            Trainer->>Module: training_step(batch)
            Module->>Model: forward(sentinel2_l2a)
            Model-->>Module: predictions
            Module->>Module: Compute loss
            Module-->>Trainer: loss
            Trainer->>Trainer: Backward pass
            Trainer->>Trainer: Optimizer step
        end
        
        Trainer->>Callbacks: on_validation_epoch_start()
        
        loop For each validation batch
            Trainer->>Module: validation_step(batch)
            Module->>Model: forward(sentinel2_l2a)
            Module->>Module: Compute metrics
        end
        
        Trainer->>Callbacks: on_validation_epoch_end()
        Callbacks->>Callbacks: ModelCheckpoint checks val_segment/accuracy
        Callbacks->>Callbacks: PlateauScheduler checks for plateau
        Callbacks->>Module: Adjust learning rate if needed
    end
    
    Trainer->>Callbacks: on_fit_end()
```

**Sources:** [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:1-268]()

---

## Best Practices and Recommendations

### Hyperparameter Selection

**FreezeUnfreeze Timing:**
- `unfreeze_at_epoch: 20` is suitable for most tasks
- Increase if decoder requires more pre-training (complex tasks)
- Decrease if dataset is large and well-aligned with pre-training

**Learning Rate Factor:**
- `unfreeze_lr_factor: 10` provides strong encoder adaptation
- Reduce to 5 if encoder overfits quickly
- Increase to 20 if encoder needs aggressive fine-tuning

**PlateauScheduler Patience:**
- `patience: 2` for fast convergence detection
- Increase to 3-5 for noisy validation metrics
- Decrease to 1 for stable, monotonic improvements

### Training Monitoring

Key metrics to track:
1. `train_segment/loss` - Training loss trajectory
2. `val_segment/accuracy` - Overall validation performance
3. `val_segment/{class}_precision` - Per-class precision
4. `val_segment/{class}_recall` - Per-class recall
5. `lr-{optimizer_group}` - Learning rate evolution

### Convergence Indicators

Training has converged when:
- Validation accuracy plateaus for >10 epochs
- Learning rate reduced to near `min_lr` (approaching 0)
- Training and validation losses stabilize
- Per-class metrics show consistent performance

**Sources:** [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:43-49](), [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:261-265]()

---

# Page: Data Module and Transforms

# Data Module and Transforms

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [olmoearth_run_data/mangrove/dataset.json](olmoearth_run_data/mangrove/dataset.json)
- [olmoearth_run_data/mangrove/model.yaml](olmoearth_run_data/mangrove/model.yaml)
- [olmoearth_run_data/mangrove/olmoearth_run.yaml](olmoearth_run_data/mangrove/olmoearth_run.yaml)
- [olmoearth_run_data/mozambique_lulc/dataset.json](olmoearth_run_data/mozambique_lulc/dataset.json)
- [olmoearth_run_data/mozambique_lulc/model.yaml](olmoearth_run_data/mozambique_lulc/model.yaml)
- [olmoearth_run_data/mozambique_lulc/olmoearth_run.yaml](olmoearth_run_data/mozambique_lulc/olmoearth_run.yaml)

</details>



## Purpose and Scope

This document explains the data loading and transformation infrastructure used during model training and inference in the olmoearth_projects repository. It covers the `RslearnDataModule` configuration, data input specifications, batch processing parameters, and the transformation pipeline including normalization, padding, cropping, and augmentation operations.

For information about the overall training process, see [Model Training](#5). For details on training configuration files, see [Training Configuration Files](#5.1). For metrics and evaluation, see [Metrics and Evaluation](#5.5).

## RslearnDataModule Architecture

The `RslearnDataModule` is a PyTorch Lightning `DataModule` that orchestrates data loading for training and inference. It manages dataset paths, input specifications, transformation pipelines, and split configurations for train/validation/test/predict stages.

```mermaid
graph TB
    subgraph "RslearnDataModule Configuration"
        PATH["path: Dataset Path<br/>${DATASET_PATH}"]
        INPUTS["inputs: Dict of DataInput<br/>label, sentinel2_l2a, etc."]
        TASK["task: MultiTask<br/>Task definitions"]
        BATCH["Batch Parameters<br/>batch_size, num_workers"]
    end
    
    subgraph "Split Configurations"
        DEFAULT["default_config<br/>SplitConfig<br/>Base transforms"]
        TRAIN["train_config<br/>SplitConfig<br/>Augmentations + Base"]
        VAL["val_config<br/>SplitConfig<br/>Patch extraction"]
        TEST["test_config<br/>SplitConfig<br/>Patch extraction"]
        PREDICT["predict_config<br/>Inference settings<br/>overlap_ratio"]
    end
    
    subgraph "DataInput Specifications"
        LABEL_INPUT["label DataInput<br/>data_type: raster<br/>is_target: true<br/>dtype: INT32"]
        IMAGE_INPUT["sentinel2_l2a DataInput<br/>data_type: raster<br/>passthrough: true<br/>load_all_layers: true"]
    end
    
    PATH --> DEFAULT
    INPUTS --> LABEL_INPUT
    INPUTS --> IMAGE_INPUT
    TASK --> LABEL_INPUT
    
    DEFAULT --> TRAIN
    DEFAULT --> VAL
    DEFAULT --> TEST
    DEFAULT --> PREDICT
    
    BATCH --> TRAIN
    BATCH --> VAL
    BATCH --> TEST
    
    style PATH fill:#f9f9f9
    style INPUTS fill:#f9f9f9
    style DEFAULT fill:#e8f4f8
```

**Sources:** [olmoearth_run_data/mangrove/model.yaml:41-340](), [olmoearth_run_data/mozambique_lulc/model.yaml:32-246]()

## Data Input Configuration

Each input to the model is defined using the `rslearn.train.dataset.DataInput` class. The data module accepts a dictionary of named inputs under the `inputs` key, where each input specifies how a particular data layer should be loaded and processed.

### DataInput Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `data_type` | string | Type of data: `"raster"` or `"vector"` |
| `layers` | list[string] | Layer names to load from dataset (e.g., `["sentinel2"]`, `["label_raster"]`) |
| `bands` | list[string] | Specific bands to extract (e.g., `["B02", "B03", "B04"]` for Sentinel-2) |
| `required` | boolean | Whether this input must be present |
| `passthrough` | boolean | If true, data is passed through encoder without modification |
| `is_target` | boolean | Indicates this input contains ground truth labels |
| `dtype` | string | Data type: `FLOAT32`, `INT32`, `UINT16`, etc. |
| `load_all_layers` | boolean | Load all timesteps/layers for temporal data |
| `load_all_item_groups` | boolean | Load all item groups in the dataset |

**Sources:** [olmoearth_run_data/mangrove/model.yaml:44-83](), [olmoearth_run_data/mozambique_lulc/model.yaml:36-50]()

### Example: Label Input Configuration

```yaml
label:
  class_path: rslearn.train.dataset.DataInput
  init_args:
    data_type: raster
    layers:
      - label_raster
    bands:
      - label
    required: true
    passthrough: false
    is_target: true
    dtype: INT32
```

This configuration loads integer-valued labels from the `label_raster` layer. The `is_target: true` flag indicates this data will be used for loss computation rather than as model input.

**Sources:** [olmoearth_run_data/mangrove/model.yaml:45-58]()

### Example: Sentinel-2 Input Configuration

```yaml
sentinel2_l2a:
  class_path: rslearn.train.dataset.DataInput
  init_args:
    data_type: raster
    layers:
      - sentinel2
    bands:
      - B02  # Blue
      - B03  # Green
      - B04  # Red
      - B08  # NIR
      - B05  # Red Edge 1
      - B06  # Red Edge 2
      - B07  # Red Edge 3
      - B8A  # Red Edge 4
      - B11  # SWIR 1
      - B12  # SWIR 2
      - B01  # Coastal Aerosol
      - B09  # Water Vapor
    required: true
    passthrough: true
    is_target: false
    dtype: FLOAT32
    load_all_layers: true
    load_all_item_groups: true
```

This configuration loads all 12 Sentinel-2 bands. The `load_all_layers: true` and `load_all_item_groups: true` flags ensure temporal sequences are loaded when available (e.g., 12 timesteps for mangrove mapping, 8 timesteps for Mozambique LULC).

**Sources:** [olmoearth_run_data/mangrove/model.yaml:59-83](), [olmoearth_run_data/mozambique_lulc/model.yaml:37-44]()

## Split Configurations

The data module uses `rslearn.train.dataset.SplitConfig` objects to define how data is loaded for different stages. Each split can specify different transforms, data selection criteria, and processing parameters.

```mermaid
graph LR
    subgraph "SplitConfig Components"
        GROUPS["groups: List[str]<br/>Dataset groups to load"]
        TAGS["tags: Dict[str, str]<br/>Filter by metadata"]
        TRANSFORMS["transforms: List<br/>Transform pipeline"]
        SAMPLES["num_samples: int<br/>Limit sample count"]
        PATCHES["num_patches: int<br/>Patches per sample"]
    end
    
    subgraph "Stage-Specific Settings"
        TRAIN_SPEC["train_config<br/>Augmentations<br/>Random crops"]
        VAL_SPEC["val_config<br/>Patch extraction<br/>No augmentation"]
        PREDICT_SPEC["predict_config<br/>patch_size<br/>overlap_ratio<br/>skip_targets"]
    end
    
    GROUPS --> TRAIN_SPEC
    GROUPS --> VAL_SPEC
    TAGS --> TRAIN_SPEC
    TAGS --> VAL_SPEC
    TRANSFORMS --> TRAIN_SPEC
    TRANSFORMS --> VAL_SPEC
    TRANSFORMS --> PREDICT_SPEC
    
    PATCHES --> VAL_SPEC
    PATCHES --> PREDICT_SPEC
```

**Sources:** [olmoearth_run_data/mangrove/model.yaml:252-311](), [olmoearth_run_data/mozambique_lulc/model.yaml:194-245]()

### default_config

The `default_config` defines base transforms applied to all splits unless overridden. This typically includes padding to accommodate the encoder's patch size and normalization.

```yaml
default_config:
  class_path: rslearn.train.dataset.SplitConfig
  init_args:
    transforms:
      - class_path: rslearn.train.transforms.pad.Pad
        init_args:
          size: 4
          mode: "center"
          image_selectors: ["sentinel2_l2a"]
      - class_path: rslearn.models.olmoearth_pretrain.norm.OlmoEarthNormalize
        init_args:
          band_names:
            sentinel2_l2a: ["B02", "B03", "B04", "B08", "B05", "B06", "B07", "B8A", "B11", "B12", "B01", "B09"]
```

**Sources:** [olmoearth_run_data/mozambique_lulc/model.yaml:194-204]()

### train_config

The `train_config` adds data augmentation transforms for training. It specifies which groups to load and filters by split tag.

```yaml
train_config:
  class_path: rslearn.train.dataset.SplitConfig
  init_args:
    transforms:
      - class_path: rslearn.train.transforms.pad.Pad
        init_args:
          size: 31
          mode: "center"
          image_selectors: ["sentinel2_l2a", "target/segment/classes", "target/segment/valid"]
      - class_path: rslearn.train.transforms.crop.Crop
        init_args:
          crop_size: 16
          image_selectors: ["sentinel2_l2a", "target/segment/classes", "target/segment/valid"]
      - class_path: rslearn.train.transforms.flip.Flip
        init_args:
          image_selectors: ["sentinel2_l2a", "target/segment/classes", "target/segment/valid"]
      - class_path: rslearn.models.olmoearth_pretrain.norm.OlmoEarthNormalize
        init_args:
          band_names:
            sentinel2_l2a: ["B02", "B03", "B04", "B08", "B05", "B06", "B07", "B8A", "B11", "B12", "B01", "B09"]
    groups: ["gaza", "manica", "zambezia"]
    tags:
      split: "train"
```

The Mozambique LULC model uses a 31-pixel pad followed by a 16-pixel random crop for augmentation, ensuring diverse spatial contexts during training.

**Sources:** [olmoearth_run_data/mozambique_lulc/model.yaml:205-225]()

### val_config and test_config

Validation and test splits use patch-based extraction without augmentation. The `patch_size` parameter determines the size of extracted patches.

```yaml
val_config:
  patch_size: 16
  groups: ["gaza", "manica", "zambezia"]
  tags:
    split: "test"
```

**Sources:** [olmoearth_run_data/mozambique_lulc/model.yaml:226-230]()

### predict_config

The `predict_config` is used during inference. It specifies how to break large images into overlapping patches for efficient processing.

```yaml
predict_config:
  load_all_patches: true
  patch_size: 16
  overlap_ratio: 0.25  # 4-pixel overlap with 16-pixel patches
  skip_targets: true
  transforms:
    - class_path: rslearn.models.olmoearth_pretrain.norm.OlmoEarthNormalize
      init_args:
        band_names:
          sentinel2_l2a: ["B02", "B03", "B04", "B08", "B05", "B06", "B07", "B8A", "B11", "B12", "B01", "B09"]
```

The `overlap_ratio: 0.25` creates a 4-pixel overlap between adjacent 16-pixel patches, reducing boundary artifacts in the final prediction.

**Sources:** [olmoearth_run_data/mozambique_lulc/model.yaml:236-245]()

## Transform Pipeline

Transforms are applied sequentially to data samples. The pipeline typically includes geometric operations (pad, crop, flip) followed by normalization.

```mermaid
graph TB
    subgraph "Training Transform Pipeline"
        INPUT["Raw Data<br/>Variable size<br/>uint16 or int32"]
        PAD1["rslearn.train.transforms.pad.Pad<br/>size: 31 pixels<br/>mode: center"]
        CROP["rslearn.train.transforms.crop.Crop<br/>crop_size: 16<br/>Random spatial crop"]
        FLIP["rslearn.train.transforms.flip.Flip<br/>Random horizontal/vertical"]
        NORM["rslearn.models.olmoearth_pretrain.norm.OlmoEarthNormalize<br/>Band-wise normalization<br/>std_multiplier: 2.0"]
        OUTPUT["Normalized Tensor<br/>16x16 patches<br/>float32"]
    end
    
    subgraph "Inference Transform Pipeline"
        INPUT2["Raw Data<br/>Large image"]
        PAD2["rslearn.train.transforms.pad.Pad<br/>size: 2 or 4<br/>mode: center"]
        NORM2["OlmoEarthNormalize<br/>Band-wise normalization"]
        OUTPUT2["Normalized Tensor<br/>Fixed patch size"]
    end
    
    INPUT --> PAD1
    PAD1 --> CROP
    CROP --> FLIP
    FLIP --> NORM
    NORM --> OUTPUT
    
    INPUT2 --> PAD2
    PAD2 --> NORM2
    NORM2 --> OUTPUT2
```

**Sources:** [olmoearth_run_data/mozambique_lulc/model.yaml:206-222](), [olmoearth_run_data/mangrove/model.yaml:317-338]()

### Pad Transform

The `rslearn.train.transforms.pad.Pad` transform adds padding to images to accommodate the encoder's patch size requirements. The OlmoEarth encoder processes images in patches (typically 2x2 or 4x4 pixels per patch token), so input dimensions must be compatible.

**Key Parameters:**
- `size`: Number of pixels to pad on each side
- `mode`: Padding mode - `"center"` pads equally on all sides
- `image_selectors`: List of data keys to pad (e.g., `["sentinel2_l2a", "target/segment/classes"]`)

```yaml
class_path: rslearn.train.transforms.pad.Pad
init_args:
  size: 31
  mode: "center"
  image_selectors: ["sentinel2_l2a", "target/segment/classes", "target/segment/valid"]
```

For training with patch_size=4 and crop_size=16, a 31-pixel pad ensures room for random 16-pixel crops that remain evenly divisible by the patch size.

**Sources:** [olmoearth_run_data/mozambique_lulc/model.yaml:196-200](), [olmoearth_run_data/mangrove/model.yaml:261-268]()

### Crop Transform

The `rslearn.train.transforms.crop.Crop` transform extracts random spatial crops during training, providing data augmentation and enabling batch processing of large images.

```yaml
class_path: rslearn.train.transforms.crop.Crop
init_args:
  crop_size: 16
  image_selectors: ["sentinel2_l2a", "target/segment/classes", "target/segment/valid"]
```

**Sources:** [olmoearth_run_data/mozambique_lulc/model.yaml:212-215]()

### Flip Transform

The `rslearn.train.transforms.flip.Flip` transform randomly flips images horizontally and/or vertically, providing additional augmentation without changing class distributions.

```yaml
class_path: rslearn.train.transforms.flip.Flip
init_args:
  image_selectors: ["sentinel2_l2a", "target/segment/classes", "target/segment/valid"]
```

**Sources:** [olmoearth_run_data/mozambique_lulc/model.yaml:216-218]()

### OlmoEarthNormalize Transform

The `rslearn.models.olmoearth_pretrain.norm.OlmoEarthNormalize` transform normalizes satellite imagery to match the distribution expected by the pre-trained OlmoEarth encoder.

```mermaid
graph LR
    subgraph "OlmoEarthNormalize Process"
        INPUT_BANDS["Input Bands<br/>uint16 values<br/>0-10000 range"]
        BAND_MAPPING["band_names Dict<br/>sentinel2_l2a:<br/>B02, B03, B04, B08<br/>B05, B06, B07, B8A<br/>B11, B12, B01, B09"]
        STD_MULT["std_multiplier: 2.0<br/>Scaling factor for<br/>standard deviation"]
        NORMALIZE["Per-band Normalization<br/>mean=pretrain_mean<br/>std=pretrain_std*multiplier"]
        OUTPUT_NORM["Normalized Tensor<br/>float32<br/>~[-1, 1] range"]
    end
    
    INPUT_BANDS --> BAND_MAPPING
    BAND_MAPPING --> STD_MULT
    STD_MULT --> NORMALIZE
    NORMALIZE --> OUTPUT_NORM
```

**Key Parameters:**
- `band_names`: Dictionary mapping input keys to lists of band names
- `std_multiplier`: Scaling factor for standard deviation (default 2.0)

```yaml
class_path: rslearn.models.olmoearth_pretrain.norm.OlmoEarthNormalize
init_args:
  band_names:
    sentinel2_l2a:
      - B02
      - B03
      - B04
      - B08
      - B05
      - B06
      - B07
      - B8A
      - B11
      - B12
      - B01
      - B09
  std_multiplier: 2.0
```

The normalization uses pre-computed mean and standard deviation statistics from the OlmoEarth pre-training dataset. The `std_multiplier: 2.0` parameter allows finer control over the normalized value range.

**Sources:** [olmoearth_run_data/mangrove/model.yaml:270-286](), [olmoearth_run_data/mozambique_lulc/model.yaml:201-204](), [olmoearth_run_data/mozambique_lulc/model.yaml:242-245]()

## Batch Processing Configuration

The data module configures batch processing parameters that affect training performance and memory usage.

### Core Parameters

| Parameter | Description | Typical Values |
|-----------|-------------|----------------|
| `batch_size` | Number of samples per batch | 32-128 for training, higher for inference |
| `num_workers` | Number of data loading subprocesses | Set via `${NUM_WORKERS}` environment variable |
| `init_workers` | Workers to initialize at startup | Usually 0 |
| `retries` | Number of retry attempts for failed loads | Usually 0 |

```yaml
batch_size: 64
num_workers: ${NUM_WORKERS}
init_workers: 0
retries: 0
```

The mangrove model uses `batch_size: 128` while the Mozambique LULC model uses `batch_size: 64`, reflecting different memory requirements based on patch size and model complexity.

**Sources:** [olmoearth_run_data/mangrove/model.yaml:249-250](), [olmoearth_run_data/mozambique_lulc/model.yaml:192-193]()

### Inference Parameters

During inference, additional parameters control how large images are processed:

```yaml
predict_config:
  patch_size: 16
  overlap_ratio: 0.25
  load_all_patches: true
  skip_targets: true
```

- `patch_size`: Size of processing window in pixels
- `overlap_ratio`: Fraction of overlap between adjacent patches (0.25 = 25% overlap)
- `load_all_patches`: Process entire image in patches
- `skip_targets`: Don't load ground truth labels during inference

**Sources:** [olmoearth_run_data/mozambique_lulc/model.yaml:236-240]()

## Configuration Mapping: Code to Concepts

This diagram maps the YAML configuration structure to actual rslearn Python classes and their relationships:

```mermaid
graph TB
    subgraph "YAML Configuration"
        DATA_YAML["data:<br/>class_path: RslearnDataModule"]
        INPUTS_YAML["inputs:<br/>label, sentinel2_l2a"]
        TASK_YAML["task:<br/>class_path: MultiTask"]
        TRAIN_CFG_YAML["train_config:<br/>class_path: SplitConfig"]
        TRANSFORMS_YAML["transforms:<br/>- Pad<br/>- Crop<br/>- Flip<br/>- OlmoEarthNormalize"]
    end
    
    subgraph "Python Classes"
        DATAMODULE["rslearn.train.data_module<br/>RslearnDataModule"]
        DATAINPUT["rslearn.train.dataset<br/>DataInput"]
        SPLITCONFIG["rslearn.train.dataset<br/>SplitConfig"]
        PAD_CLASS["rslearn.train.transforms.pad<br/>Pad"]
        CROP_CLASS["rslearn.train.transforms.crop<br/>Crop"]
        FLIP_CLASS["rslearn.train.transforms.flip<br/>Flip"]
        NORM_CLASS["rslearn.models.olmoearth_pretrain.norm<br/>OlmoEarthNormalize"]
        MULTITASK["rslearn.train.tasks.multi_task<br/>MultiTask"]
    end
    
    DATA_YAML -.instantiates.-> DATAMODULE
    INPUTS_YAML -.instantiates.-> DATAINPUT
    TASK_YAML -.instantiates.-> MULTITASK
    TRAIN_CFG_YAML -.instantiates.-> SPLITCONFIG
    
    TRANSFORMS_YAML -.instantiates.-> PAD_CLASS
    TRANSFORMS_YAML -.instantiates.-> CROP_CLASS
    TRANSFORMS_YAML -.instantiates.-> FLIP_CLASS
    TRANSFORMS_YAML -.instantiates.-> NORM_CLASS
    
    DATAMODULE --> DATAINPUT
    DATAMODULE --> SPLITCONFIG
    DATAMODULE --> MULTITASK
    SPLITCONFIG --> PAD_CLASS
    SPLITCONFIG --> CROP_CLASS
    SPLITCONFIG --> FLIP_CLASS
    SPLITCONFIG --> NORM_CLASS
```

**Sources:** [olmoearth_run_data/mangrove/model.yaml:41-340](), [olmoearth_run_data/mozambique_lulc/model.yaml:32-246]()

## Complete Configuration Examples

### Example 1: Mangrove Classification

This configuration loads 12 timesteps of Sentinel-2 data over a year, with minimal padding for the patch_size=2 encoder:

```yaml
data:
  class_path: rslearn.train.data_module.RslearnDataModule
  init_args:
    path: ${DATASET_PATH}
    batch_size: 128
    num_workers: ${NUM_WORKERS}
    
    inputs:
      label:
        data_type: raster
        layers: [label_raster]
        bands: [label]
        is_target: true
        dtype: INT32
      
      sentinel2_l2a:
        data_type: raster
        layers: [sentinel2]
        bands: [B02, B03, B04, B08, B05, B06, B07, B8A, B11, B12, B01, B09]
        passthrough: true
        dtype: FLOAT32
        load_all_layers: true
        load_all_item_groups: true
    
    default_config:
      transforms:
        - class_path: rslearn.train.transforms.pad.Pad
          init_args:
            size: 2
            mode: center
            image_selectors: [sentinel2_l2a]
        - class_path: rslearn.models.olmoearth_pretrain.norm.OlmoEarthNormalize
          init_args:
            band_names:
              sentinel2_l2a: [B02, B03, B04, B08, B05, B06, B07, B8A, B11, B12, B01, B09]
            std_multiplier: 2.0
    
    train_config:
      groups: [sample_100K]
      tags: {split: train}
      num_samples: 10000
    
    predict_config:
      patch_size: 2
      load_all_patches: true
      skip_targets: true
```

**Sources:** [olmoearth_run_data/mangrove/model.yaml:41-340]()

### Example 2: Mozambique LULC

This configuration uses aggressive augmentation with large padding (31 pixels) followed by random crops:

```yaml
data:
  class_path: rslearn.train.data_module.RslearnDataModule
  init_args:
    path: ${DATASET_PATH}
    batch_size: 64
    num_workers: ${NUM_WORKERS}
    
    train_config:
      transforms:
        - class_path: rslearn.train.transforms.pad.Pad
          init_args:
            size: 31
            mode: center
            image_selectors: [sentinel2_l2a, target/segment/classes, target/segment/valid]
        - class_path: rslearn.train.transforms.crop.Crop
          init_args:
            crop_size: 16
            image_selectors: [sentinel2_l2a, target/segment/classes, target/segment/valid]
        - class_path: rslearn.train.transforms.flip.Flip
          init_args:
            image_selectors: [sentinel2_l2a, target/segment/classes, target/segment/valid]
        - class_path: rslearn.models.olmoearth_pretrain.norm.OlmoEarthNormalize
          init_args:
            band_names:
              sentinel2_l2a: [B02, B03, B04, B08, B05, B06, B07, B8A, B11, B12, B01, B09]
      groups: [gaza, manica, zambezia]
      tags: {split: train}
    
    val_config:
      patch_size: 16
      groups: [gaza, manica, zambezia]
      tags: {split: test}
    
    predict_config:
      patch_size: 16
      overlap_ratio: 0.25
      load_all_patches: true
      skip_targets: true
```

**Sources:** [olmoearth_run_data/mozambique_lulc/model.yaml:32-246]()

## Transform Selector Patterns

When specifying transforms, the `image_selectors` parameter determines which data tensors are affected. The selector patterns follow these conventions:

| Selector Pattern | Description |
|------------------|-------------|
| `sentinel2_l2a` | Input satellite imagery |
| `label` | Raw label data |
| `target/segment/classes` | Segmentation class predictions |
| `target/segment/valid` | Valid pixel mask |
| `target/mangrove_classification/classes` | Task-specific class outputs |

These selectors must match the data keys used in the `inputs` configuration and task definitions. All tensors that should undergo geometric transformations (pad, crop, flip) must be included in the selector list to maintain spatial alignment.

**Sources:** [olmoearth_run_data/mozambique_lulc/model.yaml:200](), [olmoearth_run_data/mozambique_lulc/model.yaml:211](), [olmoearth_run_data/mangrove/model.yaml:266-268]()

---

# Page: Metrics and Evaluation

# Metrics and Evaluation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [olmoearth_run_data/mangrove/dataset.json](olmoearth_run_data/mangrove/dataset.json)
- [olmoearth_run_data/mangrove/model.yaml](olmoearth_run_data/mangrove/model.yaml)
- [olmoearth_run_data/mangrove/olmoearth_run.yaml](olmoearth_run_data/mangrove/olmoearth_run.yaml)
- [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml](olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml)
- [olmoearth_run_data/mozambique_lulc/rslp_finetuning_croptype.yaml](olmoearth_run_data/mozambique_lulc/rslp_finetuning_croptype.yaml)
- [olmoearth_run_data/mozambique_lulc/rslp_finetuning_croptype_in_season_novmar.yaml](olmoearth_run_data/mozambique_lulc/rslp_finetuning_croptype_in_season_novmar.yaml)
- [olmoearth_run_data/mozambique_lulc/rslp_finetuning_in_season_novmar.yaml](olmoearth_run_data/mozambique_lulc/rslp_finetuning_in_season_novmar.yaml)

</details>



This document describes the metrics and evaluation system used during model training in the olmoearth_projects repository. It covers the configuration and usage of classification metrics for segmentation tasks, including overall accuracy, per-class precision and recall, and how these metrics integrate with the training loop and model checkpointing.

For information about the overall training configuration structure, see [Training Configuration Files](#5.1). For details about the training loop and callbacks, see [Fine-tuning Process](#5.3).

## Metric System Architecture

The metrics system integrates three frameworks: PyTorch Lightning for training orchestration, rslearn for geospatial task definitions, and torchmetrics for metric computations. All models in this repository use segmentation tasks, which output per-pixel classifications evaluated using multiclass classification metrics.

```mermaid
graph TB
    subgraph "PyTorch Lightning Training Loop"
        TRAIN["Lightning Trainer<br/>training_step()"]
        VAL["Lightning Trainer<br/>validation_step()"]
        LOG["Lightning Logger<br/>WandbLogger"]
    end
    
    subgraph "rslearn Task Layer"
        TASK["rslearn.train.tasks.segmentation.SegmentationTask"]
        HEAD["rslearn.train.tasks.segmentation.SegmentationHead"]
        WRAPPER["rslearn.train.tasks.segmentation.SegmentationMetric"]
    end
    
    subgraph "torchmetrics Computation"
        ACC["torchmetrics.Accuracy"]
        PREC["torchmetrics.classification.MulticlassPrecision"]
        REC["torchmetrics.classification.MulticlassRecall"]
        IOU["torchmetrics.JaccardIndex"]
    end
    
    subgraph "Model Outputs"
        LOGITS["Model Logits<br/>[B, C, H, W]"]
        TARGETS["Target Classes<br/>[B, H, W]"]
        VALID["Valid Mask<br/>[B, H, W]"]
    end
    
    TRAIN --> TASK
    VAL --> TASK
    TASK --> HEAD
    HEAD --> LOGITS
    TARGETS --> TASK
    VALID --> TASK
    
    TASK --> WRAPPER
    WRAPPER --> ACC
    WRAPPER --> PREC
    WRAPPER --> REC
    WRAPPER --> IOU
    
    ACC --> LOG
    PREC --> LOG
    REC --> LOG
    IOU --> LOG
    
    style TASK fill:#f9f9f9
    style WRAPPER fill:#f9f9f9
```

**Sources:** [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:69-98](), [olmoearth_run_data/mangrove/model.yaml:84-147]()

## Segmentation Task Configuration

The `SegmentationTask` class from rslearn defines the evaluation behavior for per-pixel classification problems. All configuration is specified in the training YAML files under the `task` section.

### Core Task Parameters

| Parameter | Type | Description | Common Values |
|-----------|------|-------------|---------------|
| `num_classes` | int | Total number of output classes including background | 4, 7, 8, 10, 60 |
| `zero_is_invalid` | bool | Whether class 0 represents invalid/background pixels | `true` |
| `metric_kwargs` | dict | Arguments passed to primary accuracy metric | `{"average": "micro"}` |
| `enable_accuracy_metric` | bool | Enable overall accuracy computation | `true` (default) |
| `enable_miou_metric` | bool | Enable mean Intersection over Union | `false` (default) |
| `enable_f1_metric` | bool | Enable F1 score computation | `false` (default) |

The `zero_is_invalid` parameter is critical - when set to `true`, pixels with label 0 are excluded from all metric calculations, and the actual class indices are 1 through `num_classes-1`.

**Sources:** [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:73-79](), [olmoearth_run_data/mangrove/model.yaml:88-145]()

## Overall Accuracy Metrics

The primary metric for all segmentation models is overall classification accuracy, computed using micro-averaging across all valid pixels. This metric is automatically enabled and logged as `val_segment/accuracy` (validation) and `train_segment/accuracy` (training).

### Averaging Strategies

The `metric_kwargs.average` parameter controls how metrics are aggregated across classes:

- **`"micro"`**: Compute metrics globally across all pixels, treating all classes equally. This is the most common setting for imbalanced datasets.
- **`"macro"`**: Compute metrics per-class then average, giving equal weight to each class regardless of frequency.
- **`"weighted"`**: Compute metrics per-class then average weighted by class support.
- **`null`**: Return per-class metrics without aggregation (used for individual class metrics).

```mermaid
graph LR
    PRED["Predicted Classes<br/>[B×H×W pixels]"]
    TARGET["Target Classes<br/>[B×H×W pixels]"]
    VALID_MASK["Valid Mask<br/>Excludes class 0"]
    
    PRED --> FILTER
    TARGET --> FILTER
    VALID_MASK --> FILTER
    
    FILTER["Apply Valid Mask<br/>Filter invalid pixels"]
    
    FILTER --> MICRO["Micro Average<br/>All valid pixels<br/>Σ(correct) / Σ(total)"]
    FILTER --> MACRO["Macro Average<br/>Per-class accuracy<br/>Σ(class_acc) / num_classes"]
    FILTER --> PERCLASS["Per-Class Metrics<br/>Individual class accuracy"]
    
    MICRO --> LOG1["val_segment/accuracy"]
    PERCLASS --> LOG2["val_segment/class1_precision<br/>val_segment/class1_recall"]
    
    style FILTER fill:#f9f9f9
```

**Sources:** [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:78-79](), [olmoearth_run_data/mangrove/model.yaml:144-145]()

## Per-Class Metrics

All models define per-class precision and recall metrics using the `other_metrics` configuration section. These metrics provide detailed performance analysis for individual classes, which is critical for imbalanced datasets common in earth observation tasks.

### Metric Configuration Pattern

Each per-class metric follows this configuration structure:

```yaml
other_metrics:
  classname_precision:
    class_path: rslearn.train.tasks.segmentation.SegmentationMetric
    init_args:
      metric:
        class_path: torchmetrics.classification.MulticlassPrecision
        init_args:
          num_classes: 8
          average: null  # Return per-class values
      class_idx: 1  # Extract metrics for this class index
  classname_recall:
    class_path: rslearn.train.tasks.segmentation.SegmentationMetric
    init_args:
      metric:
        class_path: torchmetrics.classification.MulticlassRecall
        init_args:
          num_classes: 8
          average: null
      class_idx: 1
```

The `SegmentationMetric` wrapper extracts the metric value for a specific `class_idx` from the tensor returned by torchmetrics.

### Example Configurations by Model

| Model | Classes | Example Per-Class Metrics |
|-------|---------|---------------------------|
| Mozambique LULC | 8 classes | water, bareground, rangeland, floodedvegetation, trees, cropland, buildings |
| Mozambique Crop Type | 8 classes | corn, cassava, rice, sesame, beans, millet, sorghum |
| Mangrove | 4 classes | mangrove, water, other |

```mermaid
graph TB
    CONFIG["YAML Configuration<br/>other_metrics section"]
    
    subgraph "Per-Class Metric Definition"
        WRAPPER["SegmentationMetric Wrapper"]
        METRIC["torchmetrics Metric<br/>MulticlassPrecision or<br/>MulticlassRecall"]
        CLASS_IDX["class_idx parameter<br/>Selects specific class"]
    end
    
    subgraph "Model Output Processing"
        PROBS["Class Probabilities<br/>[B, C, H, W]"]
        PREDS["Predicted Classes<br/>argmax(probs, dim=1)"]
        TARGETS["Target Classes<br/>[B, H, W]"]
    end
    
    subgraph "Metric Computation"
        COMPUTE["torchmetrics.update()<br/>Accumulate predictions"]
        TENSOR["Metric Tensor<br/>[num_classes] values"]
        EXTRACT["Extract class_idx value<br/>Single scalar"]
    end
    
    CONFIG --> WRAPPER
    WRAPPER --> METRIC
    WRAPPER --> CLASS_IDX
    
    PROBS --> PREDS
    PREDS --> COMPUTE
    TARGETS --> COMPUTE
    
    METRIC --> COMPUTE
    COMPUTE --> TENSOR
    TENSOR --> CLASS_IDX
    CLASS_IDX --> EXTRACT
    
    EXTRACT --> LOG["Logged Metric<br/>val_segment/water_precision<br/>val_segment/water_recall"]
    
    style WRAPPER fill:#f9f9f9
    style EXTRACT fill:#f9f9f9
```

**Sources:** [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:80-206](), [olmoearth_run_data/mozambique_lulc/rslp_finetuning_croptype.yaml:80-206](), [olmoearth_run_data/mangrove/model.yaml:148-238]()

## Metric Computation Details

### Multiclass Precision

Precision measures the proportion of predicted positive instances that are actually positive:

**Precision(class c) = TP(c) / (TP(c) + FP(c))**

Where:
- TP(c) = True Positives for class c (pixels correctly predicted as c)
- FP(c) = False Positives for class c (pixels incorrectly predicted as c)

Configuration parameters:
- `num_classes`: Total number of classes in the problem
- `average: null`: Returns per-class precision as a tensor
- `top_k: 1`: Use the top prediction (standard classification)
- `multidim_average: "global"`: Aggregate across spatial dimensions
- `ignore_index: null`: No classes are ignored (handled by valid mask)
- `zero_division: 0`: Return 0 when denominator is zero

### Multiclass Recall

Recall measures the proportion of actual positive instances that are correctly predicted:

**Recall(class c) = TP(c) / (TP(c) + FN(c))**

Where:
- TP(c) = True Positives for class c
- FN(c) = False Negatives for class c (pixels of class c predicted as other classes)

Configuration parameters match precision, using `torchmetrics.classification.MulticlassRecall` instead.

### Pass Probabilities Option

Some configurations use `pass_probabilities: true` in the `SegmentationMetric` wrapper. This passes the raw probability tensor to torchmetrics instead of predicted classes, though most torchmetrics classification metrics internally convert to classes anyway.

**Sources:** [olmoearth_run_data/mangrove/model.yaml:152-177](), [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:81-98]()

## Checkpoint Monitoring

The `ModelCheckpoint` callback uses metrics to determine which model checkpoint to save. The configuration specifies which metric to monitor and whether to maximize or minimize it.

### Checkpoint Configuration Structure

```yaml
callbacks:
  - class_path: lightning.pytorch.callbacks.ModelCheckpoint
    init_args:
      save_top_k: 1        # Keep best checkpoint
      save_last: true      # Also keep last checkpoint
      monitor: val_segment/accuracy  # Metric to track
      mode: max            # Maximize accuracy
```

Common monitoring strategies:

| Strategy | Monitor Metric | Mode | Use Case |
|----------|---------------|------|----------|
| Accuracy-based | `val_segment/accuracy` | `max` | Most segmentation tasks |
| Loss-based | `val_loss` | `min` | When accuracy is not representative |
| Class-specific | `val_segment/mangrove_recall` | `max` | When specific class is critical |

```mermaid
graph TB
    TRAIN["Training Epoch"]
    VAL["Validation Step"]
    
    subgraph "Metric Computation"
        TASK["SegmentationTask.validation_step()"]
        METRICS["Compute All Metrics<br/>accuracy, precision, recall"]
        LOG["Log to WandbLogger"]
    end
    
    subgraph "Model Checkpoint Callback"
        MONITOR["Monitor Metric<br/>val_segment/accuracy"]
        COMPARE["Compare to Best<br/>current > best_so_far"]
        SAVE["Save Checkpoint<br/>best.ckpt"]
        UPDATE["Update best_so_far"]
    end
    
    subgraph "Checkpoint Files"
        BEST["best.ckpt<br/>Best validation metric"]
        LAST["last.ckpt<br/>Most recent epoch"]
    end
    
    TRAIN --> VAL
    VAL --> TASK
    TASK --> METRICS
    METRICS --> LOG
    
    METRICS --> MONITOR
    MONITOR --> COMPARE
    COMPARE -->|Better| SAVE
    SAVE --> UPDATE
    SAVE --> BEST
    
    TRAIN -->|Every epoch| LAST
    
    style MONITOR fill:#f9f9f9
    style SAVE fill:#f9f9f9
```

**Sources:** [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:255-260](), [olmoearth_run_data/mangrove/model.yaml:362-377]()

## Metric Logging and Visualization

All metrics are automatically logged to WandbLogger during training. The logging format follows this naming convention:

| Metric Type | Format | Example |
|-------------|--------|---------|
| Overall accuracy | `{split}_segment/accuracy` | `val_segment/accuracy`, `train_segment/accuracy` |
| Per-class precision | `{split}_segment/{class}_precision` | `val_segment/water_precision` |
| Per-class recall | `{split}_segment/{class}_recall` | `val_segment/cropland_recall` |
| Task loss | `{split}_loss` | `val_loss`, `train_loss` |

The `LearningRateMonitor` callback additionally logs the learning rate at each epoch:

```yaml
callbacks:
  - class_path: lightning.pytorch.callbacks.LearningRateMonitor
    init_args:
      logging_interval: "epoch"
```

This enables tracking of learning rate changes during progressive unfreezing and plateau-based learning rate reduction.

**Sources:** [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:251-254](), [olmoearth_run_data/mangrove/model.yaml:349-354]()

## Common Metric Configurations

### Standard LULC Configuration (8 Classes)

Used by Mozambique LULC models with 7 land cover classes plus invalid (0):

- **Primary metric**: Micro-averaged accuracy
- **Per-class metrics**: Precision and recall for all 7 classes
- **Monitoring**: `val_segment/accuracy` (maximize)
- **Classes**: water, bareground, rangeland, floodedvegetation, trees, cropland, buildings

Configuration location: [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:73-206]()

### Crop Type Configuration (8 Classes)

Used by Mozambique crop type models:

- **Primary metric**: Micro-averaged accuracy
- **Per-class metrics**: Precision and recall for all 7 crop types
- **Monitoring**: `val_segment/accuracy` (maximize)
- **Classes**: corn, cassava, rice, sesame, beans, millet, sorghum

Configuration location: [olmoearth_run_data/mozambique_lulc/rslp_finetuning_croptype.yaml:73-206]()

### Mangrove Configuration (4 Classes)

Used by mangrove extent model:

- **Primary metric**: Micro-averaged accuracy
- **Per-class metrics**: Precision and recall for 3 classes
- **Monitoring**: `val_loss` (minimize)
- **Classes**: mangrove, water, other
- **Special setting**: `pass_probabilities: true`

Configuration location: [olmoearth_run_data/mangrove/model.yaml:88-238]()

## Validation vs Test Metrics

The training configuration defines separate splits for validation and testing:

```yaml
val_config:
  patch_size: 16
  groups: ["gaza", "manica", "zambezia"]
  tags:
    split: "val"

test_config:
  patch_size: 16
  groups: ["gaza", "manica", "zambezia"]
  tags:
    split: "test"
```

- **Validation metrics** are computed during training and used for checkpoint selection
- **Test metrics** are computed after training on held-out data for final model evaluation
- The same metric configurations apply to both splits, with prefixes `val_` and `test_`

**Sources:** [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:239-248](), [olmoearth_run_data/mangrove/model.yaml:296-311]()

---

# Page: Available Models

# Available Models

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [LICENSE](LICENSE)
- [README.md](README.md)
- [docs/awf.md](docs/awf.md)
- [docs/forest_loss_driver.md](docs/forest_loss_driver.md)
- [docs/lfmc.md](docs/lfmc.md)
- [docs/nandi.md](docs/nandi.md)
- [olmoearth_run_data/forest_loss_driver/model.yaml](olmoearth_run_data/forest_loss_driver/model.yaml)
- [olmoearth_run_data/nandi/prediction_request_geometry.geojson](olmoearth_run_data/nandi/prediction_request_geometry.geojson)

</details>



This page provides an overview of all fine-tuned OlmoEarth models available in this repository, including their applications, performance characteristics, and access information. Each model is built on the OlmoEarth-v1-Base foundation model and fine-tuned for specific remote sensing tasks. For detailed information about individual models including training data, inference procedures, and usage examples, see the corresponding child pages (sections 6.1-6.7).

For information about the training process used to create these models, see [Model Training](#5). For information about running inference with these models, see [Inference and Deployment](#7).

## Model Catalog

The repository contains seven distinct fine-tuned models, each targeting a specific application domain:

| Model Name | Task Type | Classes/Output | Accuracy/MSE | Geographic Focus | HuggingFace Link |
|------------|-----------|----------------|--------------|------------------|------------------|
| Mozambique LULC | Segmentation | 7 LULC classes + 7 crop types | TBD | Mozambique (3 provinces) | See [6.1](#6.1) |
| LFMC | Regression | Continuous moisture % | MSE: 580.6 | Continental US | [allenai/OlmoEarth-v1-FT-LFMC-Base](https://huggingface.co/allenai/OlmoEarth-v1-FT-LFMC-Base) |
| Forest Loss Driver | Classification | 10 driver classes | 76.1% | Tropical forests | [allenai/OlmoEarth-v1-FT-ForestLossDriver-Base](https://huggingface.co/allenai/OlmoEarth-v1-FT-ForestLossDriver-Base) |
| Mangrove Extent | Segmentation | 3 classes | 97.6% | Global mangroves | [allenai/OlmoEarth-v1-FT-Mangrove-Base](https://huggingface.co/allenai/OlmoEarth-v1-FT-Mangrove-Base) |
| Ecosystem Type | Segmentation | 60 ecosystem types | 64.8% | North Africa | [allenai/OlmoEarth-v1-FT-EcosystemTypeMapping-Base](https://huggingface.co/allenai/OlmoEarth-v1-FT-EcosystemTypeMapping-Base) |
| Nandi Crop | Segmentation | 10 crop/land types | 87.3% | Nandi County, Kenya | [allenai/OlmoEarth-v1-FT-Nandi-Base](https://huggingface.co/allenai/OlmoEarth-v1-FT-Nandi-Base) |
| AWF Land Cover | Segmentation | 9 land cover types | 89.5% | Southern Kenya | [allenai/OlmoEarth-v1-FT-AWF-Base](https://huggingface.co/allenai/OlmoEarth-v1-FT-AWF-Base) |

**Sources:** [README.md:8-17](), [docs/lfmc.md:1-24](), [docs/forest_loss_driver.md:1-39](), [docs/nandi.md:1-18](), [docs/awf.md:1-18]()

## Model Architecture Mapping

The following diagram shows how each model maps to its configuration files and the code entities that define its architecture:

```mermaid
graph TB
    subgraph "Base Foundation Model"
        BASE["OLMOEARTH_V1_BASE<br/>rslearn.models.olmoearth_pretrain.model.OlmoEarth"]
    end
    
    subgraph "Fine-tuned Models and Configurations"
        LFMC["LFMC Model<br/>olmoearth_run_data/lfmc/<br/>model.yaml"]
        FLD["Forest Loss Driver<br/>olmoearth_run_data/forest_loss_driver/<br/>model.yaml"]
        MANG["Mangrove Extent<br/>olmoearth_run_data/mangrove/<br/>model.yaml"]
        ECO["Ecosystem Type<br/>olmoearth_run_data/ecosystem_type_mapping/<br/>model.yaml"]
        NANDI["Nandi Crop<br/>olmoearth_run_data/nandi/<br/>model.yaml"]
        AWF["AWF Land Cover<br/>olmoearth_run_data/awf/<br/>model.yaml"]
        MOZ["Mozambique LULC<br/>olmoearth_run_data/mozambique_lulc/<br/>model.yaml"]
    end
    
    subgraph "Task Heads"
        REG["RegressionTask<br/>rslearn.train.tasks.regression"]
        CLS["ClassificationTask<br/>rslearn.train.tasks.classification"]
        SEG["SegmentationTask<br/>rslearn.train.tasks.segmentation"]
    end
    
    subgraph "Decoder Architectures"
        SEG_DEC["SegmentationHead<br/>rslearn.models.segmentation_head"]
        POOL_DEC["PoolingDecoder<br/>rslearn.models.pooling_decoder"]
    end
    
    BASE --> LFMC
    BASE --> FLD
    BASE --> MANG
    BASE --> ECO
    BASE --> NANDI
    BASE --> AWF
    BASE --> MOZ
    
    LFMC --> REG
    LFMC --> SEG_DEC
    
    FLD --> CLS
    FLD --> POOL_DEC
    
    MANG --> SEG
    MANG --> SEG_DEC
    
    ECO --> SEG
    ECO --> SEG_DEC
    
    NANDI --> SEG
    NANDI --> SEG_DEC
    
    AWF --> SEG
    AWF --> SEG_DEC
    
    MOZ --> SEG
    MOZ --> SEG_DEC
```

**Sources:** [olmoearth_run_data/forest_loss_driver/model.yaml:14-16](), [README.md:62-73]()

## Common Architecture Pattern

All models in this repository follow a consistent architecture pattern defined in their `model.yaml` configuration files:

### Encoder-Decoder Structure

Each model uses `rslearn.models.singletask.SingleTaskModel` with two main components:

1. **Encoder**: `rslearn.models.olmoearth_pretrain.model.OlmoEarth` initialized with `model_id: OLMOEARTH_V1_BASE`
2. **Decoder**: Task-specific head (either `SegmentationHead` or `PoolingDecoder`)

The encoder configuration specifies:
- `patch_size`: Typically 1, 2, or 4 depending on the model
- `image_channels`: Number of input channels (varies by temporal depth and bands)
- `image_key`: Input data key (e.g., `"sentinel2_l2a"`)

**Sources:** [olmoearth_run_data/forest_loss_driver/model.yaml:6-28]()

### Task Configurations

Models use three different task types from `rslearn.train.tasks`:

```mermaid
graph LR
    subgraph "Task Types"
        REG_TASK["RegressionTask<br/>Per-pixel continuous values"]
        CLS_TASK["ClassificationTask<br/>Single label per window"]
        SEG_TASK["SegmentationTask<br/>Per-pixel classification"]
    end
    
    subgraph "Models by Task"
        LFMC_M["LFMC<br/>Moisture content"]
        FLD_M["Forest Loss Driver<br/>10 classes"]
        OTHERS["Nandi, AWF, Mangrove<br/>Ecosystem, Mozambique<br/>Various class counts"]
    end
    
    REG_TASK --> LFMC_M
    CLS_TASK --> FLD_M
    SEG_TASK --> OTHERS
```

**Sources:** [olmoearth_run_data/forest_loss_driver/model.yaml:56-64]()

## Model Distribution Locations

Each model has associated artifacts distributed across multiple platforms:

```mermaid
graph TB
    subgraph "Model Artifacts"
        CKPT["Model Checkpoint<br/>model.ckpt<br/>PyTorch Lightning format"]
        CONFIG["Configuration Files<br/>model.yaml<br/>dataset.json<br/>olmoearth_run.yaml"]
        ANNOT["Annotation Data<br/>GeoJSON features<br/>Label geometries"]
        DATASET["Training Dataset<br/>dataset.tar<br/>rslearn format"]
    end
    
    subgraph "Distribution Platforms"
        HF_MODELS["HuggingFace Hub<br/>allenai organization<br/>Model repositories"]
        HF_DATA["HuggingFace Datasets<br/>allenai organization<br/>Dataset repositories"]
        GCS["Google Cloud Storage<br/>ai2-olmoearth-projects-public-data"]
        REPO["GitHub Repository<br/>olmoearth_projects<br/>olmoearth_run_data/"]
    end
    
    CKPT --> HF_MODELS
    CKPT --> GCS
    
    CONFIG --> REPO
    
    ANNOT --> HF_DATA
    ANNOT --> GCS
    
    DATASET --> HF_DATA
    DATASET --> GCS
```

**Sources:** [docs/lfmc.md:10-12](), [docs/nandi.md:8-10](), [docs/awf.md:8-10](), [docs/forest_loss_driver.md:27-28]()

## Input Data Requirements

All models consume satellite imagery with temporal sequences. The following table summarizes input requirements:

| Model | Primary Data | Secondary Data | Timesteps | Temporal Resolution |
|-------|-------------|----------------|-----------|-------------------|
| LFMC | Sentinel-2 L2A | Sentinel-1 RTC | 12 | 14-day periods |
| Forest Loss Driver | Sentinel-2 L2A | - | 8 (4 pre + 4 post) | Variable |
| Mangrove | Sentinel-2 L2A | - | 12 | 30-day periods |
| Ecosystem Type | Sentinel-2 L2A | - | 6 | 30-day periods |
| Nandi | Sentinel-2 L2A | Sentinel-1 RTC | 12 | 30-day periods |
| AWF | Sentinel-2 L2A | Sentinel-1 RTC | 12 | 30-day periods |
| Mozambique LULC | Sentinel-2 L2A | - | Seasonal | Variable |

All models retrieve data from Microsoft Planetary Computer as configured in their respective `dataset.json` files.

**Sources:** [docs/lfmc.md:16-20](), [docs/forest_loss_driver.md:32-36](), [docs/nandi.md:14](), [docs/awf.md:14]()

## Configuration File Structure

Each model's configuration is stored in `olmoearth_run_data/PROJECT_NAME/` with three files:

### dataset.json
Specifies data sources and query parameters:
- Data source URLs (Planetary Computer endpoints)
- Band selections for Sentinel-2 and Sentinel-1
- Harmonization settings
- Temporal query configurations

### model.yaml
Defines model architecture and training:
- Encoder: OlmoEarth initialization parameters
- Decoder: Task-specific head configuration
- Optimizer: AdamW with learning rate
- Scheduler: PlateauScheduler parameters
- Callbacks: FreezeUnfreeze, ModelCheckpoint, etc.

### olmoearth_run.yaml
Configures inference pipeline:
- Partitioning strategy (coarse and fine grids)
- Post-processing rules (CombineGeotiff)
- Output projection settings
- Metadata for visualization

**Sources:** [README.md:62-73](), [olmoearth_run_data/forest_loss_driver/model.yaml:1-128]()

## Model Checkpoint Access

Model checkpoints can be downloaded directly from HuggingFace using wget:

```bash
# LFMC model
wget https://huggingface.co/allenai/OlmoEarth-v1-FT-LFMC-Base/resolve/main/model.ckpt

# Forest Loss Driver model
wget https://huggingface.co/allenai/OlmoEarth-v1-FT-ForestLossDriver-Base/resolve/main/model.ckpt

# Nandi model
wget https://huggingface.co/allenai/OlmoEarth-v1-FT-Nandi-Base/blob/main/model.ckpt

# AWF model
wget https://huggingface.co/allenai/OlmoEarth-v1-FT-AWF-Base/blob/main/model.ckpt
```

Checkpoints are in PyTorch Lightning format (`.ckpt`) and can be loaded using the `--checkpoint_path` argument when running `olmoearth_run`.

**Sources:** [README.md:109-114](), [docs/lfmc.md:10](), [docs/forest_loss_driver.md:27]()

## Training Data Access

Training datasets are available in rslearn format as tar archives:

```bash
# LFMC dataset (from GCS)
wget https://storage.googleapis.com/ai2-olmoearth-projects-public-data/projects/lfmc/20251029/dataset.tar

# Forest Loss Driver dataset (from GCS)
wget https://storage.googleapis.com/ai2-olmoearth-projects-public-data/projects/forest_loss_driver/20251029/dataset.tar

# Nandi dataset (from HuggingFace)
wget https://huggingface.co/datasets/allenai/olmoearth_projects_nandi/blob/main/dataset.tar

# AWF dataset (from HuggingFace)
wget https://huggingface.co/datasets/allenai/olmoearth_projects_awf/blob/main/dataset.tar
```

Extract with `tar xvf dataset.tar` and set `DATASET_PATH` environment variable to the extracted directory when fine-tuning.

**Sources:** [README.md:148-154](), [docs/lfmc.md:12](), [docs/forest_loss_driver.md:28]()

## Model Performance Characteristics

### Segmentation Models

Most models perform per-pixel segmentation using `SegmentationHead` decoder:

- **Mangrove**: 97.6% accuracy on 3 classes (mangrove, water, other)
- **AWF**: 89.5% accuracy on 9 land cover classes
- **Nandi**: 87.3% accuracy on 10 crop/land types
- **Ecosystem Type**: 64.8% accuracy on 60 ecosystem types

Performance generally decreases as the number of classes increases, which is expected.

### Classification Model

**Forest Loss Driver** uses `PoolingDecoder` for whole-window classification:
- 76.1% accuracy on 10 driver classes
- Confusion matrix shows strong performance on agriculture, burned, and road classes
- Challenges with underrepresented classes (airstrip, landslide)

### Regression Model

**LFMC** predicts continuous moisture content values:
- MSE of 580.6 on test set
- Outputs per-pixel regression values
- Uses `RegressionTask` instead of classification

**Sources:** [docs/nandi.md:18](), [docs/awf.md:18](), [docs/forest_loss_driver.md:38-52](), [docs/lfmc.md:24]()

## Licensing

All models and code in this repository are released under the OlmoEarth Artifact License, which permits use, modification, and distribution with restrictions on military/defense and extractive industry applications.

Training data licenses vary by model:
- **LFMC**: CC0 (public domain)
- **Forest Loss Driver**: CC BY 4.0

Refer to individual model documentation for specific licensing terms.

**Sources:** [LICENSE:1-128](), [docs/lfmc.md:40](), [docs/forest_loss_driver.md:63]()

---

# Page: Mozambique LULC Models

# Mozambique LULC Models

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [olmoearth_run_data/mozambique_lulc/README.md](olmoearth_run_data/mozambique_lulc/README.md)
- [olmoearth_run_data/mozambique_lulc/config.json](olmoearth_run_data/mozambique_lulc/config.json)
- [olmoearth_run_data/mozambique_lulc/dataset.json](olmoearth_run_data/mozambique_lulc/dataset.json)
- [olmoearth_run_data/mozambique_lulc/model.yaml](olmoearth_run_data/mozambique_lulc/model.yaml)
- [olmoearth_run_data/mozambique_lulc/olmoearth_run.yaml](olmoearth_run_data/mozambique_lulc/olmoearth_run.yaml)
- [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml](olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml)
- [olmoearth_run_data/mozambique_lulc/rslp_finetuning_croptype.yaml](olmoearth_run_data/mozambique_lulc/rslp_finetuning_croptype.yaml)
- [olmoearth_run_data/mozambique_lulc/rslp_finetuning_croptype_in_season_novmar.yaml](olmoearth_run_data/mozambique_lulc/rslp_finetuning_croptype_in_season_novmar.yaml)
- [olmoearth_run_data/mozambique_lulc/rslp_finetuning_in_season_novmar.yaml](olmoearth_run_data/mozambique_lulc/rslp_finetuning_in_season_novmar.yaml)

</details>



This document covers the Mozambique Land Use Land Cover (LULC) classification models, which include two fine-tuned OlmoEarth variants: a 7-class LULC classifier and a 7-class crop type classifier. These models are trained on field survey data from three provinces in Mozambique (Gaza, Manica, and Zambezia) and perform pixel-level segmentation using Sentinel-2 imagery.

For general information about the model training process, see [Model Training](#5). For details on the inference pipeline, see [olmoearth_run Pipeline](#7.1). For information about other fine-tuned models in the repository, see [Available Models](#6).

## Overview

The Mozambique LULC project consists of two distinct classification tasks:

| Task | Classes | Training Samples | Purpose |
|------|---------|-----------------|---------|
| **LULC Classification** | 7 land cover types | 4,881 (train), 1,623 (val), 2,317 (test) | General land cover mapping including water, vegetation, buildings, cropland |
| **Crop Type Classification** | 7 crop types | 3,821 (train), 1,060 (val), 5,671 (test) | Agricultural crop identification within cropland areas |

Both models use the same OlmoEarth-v1-Base encoder with task-specific segmentation heads. Training data is organized by province groups to enable spatial generalization assessment.

**Sources**: [olmoearth_run_data/mozambique_lulc/README.md:1-49]()

## Model Variants

### LULC Classification Model

The LULC model classifies land cover into 7 categories plus an invalid class:

| Class Index | Label | Description |
|-------------|-------|-------------|
| 0 | Invalid | No data or unlabeled pixels (zero_is_invalid=true) |
| 1 | Water | Water bodies including rivers, lakes, ponds |
| 2 | Bare Ground | Exposed soil, sand, or rock |
| 3 | Rangeland | Grasslands and shrublands |
| 4 | Flooded Vegetation | Wetlands and seasonally flooded areas |
| 5 | Trees | Forest and tree cover |
| 6 | Cropland | Agricultural fields (all crop types) |
| 7 | Buildings | Built-up areas and structures |

The model is configured in [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:1-268]() and trains on all three province groups (gaza, manica, zambezia) as specified in [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:236-246]().

**Sources**: [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:76-188](), [olmoearth_run_data/mozambique_lulc/README.md:49](), [olmoearth_run_data/mozambique_lulc/olmoearth_run.yaml:6-27]()

### Crop Type Classification Model

The crop type model identifies specific crops within agricultural areas:

| Class Index | Label | Typical Growing Season |
|-------------|-------|----------------------|
| 0 | Invalid | No data or unlabeled pixels |
| 1 | Corn | November-March |
| 2 | Cassava | Year-round perennial |
| 3 | Rice | November-March |
| 4 | Sesame | November-March |
| 5 | Beans | November-March |
| 6 | Millet | November-March |
| 7 | Sorghum | November-March |

The crop type model configuration is in [olmoearth_run_data/mozambique_lulc/rslp_finetuning_croptype.yaml:1-268]() and trains on the `crop_type` group as specified in [olmoearth_run_data/mozambique_lulc/rslp_finetuning_croptype.yaml:236-247]().

**Sources**: [olmoearth_run_data/mozambique_lulc/rslp_finetuning_croptype.yaml:75-206](), [olmoearth_run_data/mozambique_lulc/README.md:45-48]()

### Seasonal Variants

Both models have seasonal variants optimized for the November-March growing season:
- `rslp_finetuning_in_season_novmar.yaml` for LULC
- `rslp_finetuning_croptype_in_season_novmar.yaml` for crop type

These variants load 5 Sentinel-2 layers ([olmoearth_run_data/mozambique_lulc/rslp_finetuning_in_season_novmar.yaml:57]()) corresponding to monthly observations during the growing season, compared to the standard 8-month configuration that uses all available temporal data.

**Sources**: [olmoearth_run_data/mozambique_lulc/rslp_finetuning_in_season_novmar.yaml:1-267](), [olmoearth_run_data/mozambique_lulc/rslp_finetuning_croptype_in_season_novmar.yaml:1-267]()

## Model Architecture

```mermaid
graph TB
    subgraph "Input Layer"
        S2["Sentinel-2 L2A<br/>12 bands x 8 timesteps<br/>10m resolution"]
        NORM["OlmoEarthNormalize<br/>Band normalization"]
    end
    
    subgraph "Encoder: OlmoEarth Pre-trained"
        CHECKPOINT["checkpoint_path:<br/>/weka/dfive-default/helios/checkpoints/<br/>joer/phase2.0_base_lr0.0001_wd0.02/step667200"]
        ENCODER["OlmoEarth encoder<br/>patch_size: 4<br/>embedding_size: 768<br/>autocast_dtype: bfloat16"]
        FREEZE["FreezeUnfreeze callback<br/>freeze until epoch 20<br/>unfreeze_lr_factor: 10"]
    end
    
    subgraph "Decoder: Segmentation Head"
        UPSAMPLE["Upsample<br/>scale_factor: 4<br/>mode: bilinear"]
        CONV["Conv<br/>in_channels: 768<br/>out_channels: 8<br/>kernel_size: 1"]
        PICK["PickFeatures<br/>indexes: [0]<br/>collapse: true"]
        SEGHEAD["SegmentationHead<br/>num_classes: 8<br/>zero_is_invalid: true"]
    end
    
    subgraph "Output"
        CLASSES["Class predictions<br/>8 channels<br/>per-pixel logits"]
    end
    
    S2 --> NORM
    NORM --> ENCODER
    CHECKPOINT --> ENCODER
    ENCODER --> FREEZE
    FREEZE --> UPSAMPLE
    UPSAMPLE --> CONV
    CONV --> PICK
    PICK --> SEGHEAD
    SEGHEAD --> CLASSES
```

**Architecture Configuration Mapping**

The model uses `rslearn.models.multitask.MultiTaskModel` as defined in [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:5-41](). Key architectural components:

1. **Encoder**: `rslearn.models.olmoearth_pretrain.model.OlmoEarth` ([olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:8-16]())
   - Loads pre-trained weights from checkpoint at step 667200
   - Uses selector `["encoder"]` to extract only encoder weights
   - Patch size of 4 means the encoder operates at 1/4 the input resolution

2. **Decoder Pipeline** ([olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:17-38]()):
   - `rslearn.models.upsample.Upsample`: Bilinear upsampling by 4x to restore original resolution
   - `rslearn.models.conv.Conv`: 1x1 convolution to project 768 encoder features to 8 class channels
   - `rslearn.models.pick_features.PickFeatures`: Selects first feature map
   - `rslearn.train.tasks.segmentation.SegmentationHead`: Applies softmax and loss computation

3. **Training Configuration** ([olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:42-49]()):
   - Base learning rate: 0.0001
   - `rslearn.train.scheduler.PlateauScheduler` with factor=0.2, patience=2
   - `rslearn.train.callbacks.freeze_unfreeze.FreezeUnfreeze` unfreezes encoder at epoch 20 with 10x LR boost

**Sources**: [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:1-49](), [olmoearth_run_data/mozambique_lulc/model.yaml:1-31]()

## Dataset Configuration

```mermaid
graph TB
    subgraph "Data Sources"
        GPKG["GPKG files<br/>/weka/dfive-default/yawenz/datasets/<br/>mozambique/train_test_samples"]
        PC["Planetary Computer<br/>Sentinel-2 L2A<br/>harmonize: true<br/>sort_by: eo:cloud_cover"]
    end
    
    subgraph "Dataset Structure"
        DS_PATH["/weka/dfive-default/rslearn-eai/<br/>datasets/crop/mozambique_lulc/20251202"]
        SENTINEL2["Layer: sentinel2<br/>12 bands: B02,B03,B04,B08,B05,<br/>B06,B07,B8A,B11,B12,B01,B09<br/>dtype: FLOAT32"]
        LABEL_RASTER["Layer: label_raster<br/>1 band: label<br/>dtype: INT32"]
        CONFIG["config.json<br/>defines data sources<br/>and layer schemas"]
        DATASET_JSON["dataset.json<br/>query configuration:<br/>8 timesteps x 30-day periods"]
    end
    
    subgraph "Groups and Splits"
        GAZA["Group: gaza<br/>Train: 1802<br/>Val: 460<br/>Test: 970"]
        MANICA["Group: manica<br/>Train: 1564<br/>Val: 353<br/>Test: 822"]
        ZAMBEZIA["Group: zambezia<br/>Train: 949<br/>Val: 276<br/>Test: 525"]
        CROP_TYPE["Group: crop_type<br/>Train: 3821<br/>Val: 1060<br/>Test: 5671"]
    end
    
    GPKG --> DS_PATH
    PC --> SENTINEL2
    DS_PATH --> CONFIG
    DS_PATH --> DATASET_JSON
    DS_PATH --> SENTINEL2
    DS_PATH --> LABEL_RASTER
    DS_PATH --> GAZA
    DS_PATH --> MANICA
    DS_PATH --> ZAMBEZIA
    DS_PATH --> CROP_TYPE
```

**Dataset Location and Structure**

The dataset is stored at `/weka/dfive-default/rslearn-eai/datasets/crop/mozambique_lulc/20251202` as specified in [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:53](). This version (20251202) is the latest iteration with aligned temporal configurations and updated train/val/test splits.

**Data Layers**

The `RslearnDataModule` configuration ([olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:50-68]()) defines two input layers:

1. **sentinel2_l2a** ([olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:55-62]())
   - 12 Sentinel-2 bands in canonical order
   - `load_all_item_groups: true` loads all 8 timesteps
   - `passthrough: true` allows direct access to raw values

2. **label** ([olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:63-68]())
   - Single integer band containing class labels
   - `is_target: true` marks as ground truth
   - Stored in rasterized format (see label_raster layer in [olmoearth_run_data/mozambique_lulc/config.json:6-16]())

**Temporal Configuration**

The `dataset.json` ([olmoearth_run_data/mozambique_lulc/dataset.json:45-58]()) specifies:
- `max_matches: 8` and `min_matches: 8` enforce exactly 8 temporal observations
- `period_duration: "30d"` creates monthly mosaics
- `space_mode: "PER_PERIOD_MOSAIC"` aggregates all images within each 30-day period

**Sources**: [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:50-68](), [olmoearth_run_data/mozambique_lulc/dataset.json:1-63](), [olmoearth_run_data/mozambique_lulc/config.json:1-69](), [olmoearth_run_data/mozambique_lulc/README.md:39-49]()

## Data Processing Pipeline

```mermaid
graph LR
    subgraph "Step 1: Window Creation"
        GPKG_INPUT["GPKG point<br/>annotations"]
        CREATE_WINDOWS["create_windows_for_lulc.py<br/>--gpkg_dir<br/>--ds_path<br/>--window_size 32"]
        WINDOWS["32x32 pixel<br/>windows created"]
    end
    
    subgraph "Step 2: Spatial Splitting"
        UPDATE_SPLIT["update_train_test_split.py<br/>SpatialDataSplitter<br/>grid_size: 128<br/>val_ratio: 0.1"]
        SPLIT_TAGS["Tags added:<br/>split: train/val/test"]
    end
    
    subgraph "Step 3: Data Preparation"
        RSLEARN_PREPARE["rslearn dataset prepare<br/>--root $DATASET_PATH<br/>--workers 64"]
        MATERIALIZE["rslp launch_data_<br/>materialization_jobs<br/>--num_jobs 5"]
    end
    
    subgraph "Step 4: Label Rasterization"
        CREATE_LABEL["create_label_raster.py<br/>--ds_path"]
        RASTER_LAYER["label_raster layer<br/>created from points"]
    end
    
    subgraph "Step 5: Quality Check"
        CHECK_QUALITY["check_label_quality.py<br/>--ds_path<br/>--split train"]
        METRICS["Spatial clustering F1<br/>Label imbalance<br/>Spatial extent"]
    end
    
    GPKG_INPUT --> CREATE_WINDOWS
    CREATE_WINDOWS --> WINDOWS
    WINDOWS --> UPDATE_SPLIT
    UPDATE_SPLIT --> SPLIT_TAGS
    SPLIT_TAGS --> RSLEARN_PREPARE
    RSLEARN_PREPARE --> MATERIALIZE
    MATERIALIZE --> CREATE_LABEL
    CREATE_LABEL --> RASTER_LAYER
    RASTER_LAYER --> CHECK_QUALITY
    CHECK_QUALITY --> METRICS
```

**Window Creation**

Windows are created using scripts in the project directory. The command structure is:

```bash
python olmoearth_projects/projects/mozambique_lulc/create_windows_for_lulc.py \
    --gpkg_dir /weka/dfive-default/yawenz/datasets/mozambique/train_test_samples \
    --ds_path $DATASET_PATH \
    --window_size 32
```

For crop type data, add the `--crop_type` flag ([olmoearth_run_data/mozambique_lulc/README.md:20]()).

The window creation process:
- Reads point annotations from GPKG files
- Creates 32x32 pixel windows centered on each point
- Sets 10m resolution as configured in [olmoearth_run_data/mozambique_lulc/olmoearth_run.yaml:36]()
- Applies 31-pixel buffer as specified in [olmoearth_run_data/mozambique_lulc/olmoearth_run.yaml:35]()

**Data Splitting**

The `SpatialDataSplitter` ([olmoearth_run_data/mozambique_lulc/olmoearth_run.yaml:40-48]()) creates spatially-coherent splits:
- Uses grid_size of 128 pixels to define spatial blocks
- Splits blocks with train_prop=0.75, val_prop=0.25, test_prop=0.0
- Assigns split tags to each window
- Prevents data leakage by ensuring spatial separation between splits

**Label Rasterization**

The script `create_label_raster.py` converts point labels to rasters:
```bash
python olmoearth_projects/projects/mozambique_lulc/create_label_raster.py \
    --ds_path $DATASET_PATH
```

This step is necessary because the model uses `rslearn.train.tasks.segmentation.SegmentationTask` ([olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:74]()) which expects raster inputs, not point geometries. The conversion creates a `label_raster` layer with dtype INT32 and nodata_value 255 ([olmoearth_run_data/mozambique_lulc/olmoearth_run.yaml:37-38]()).

**Sources**: [olmoearth_run_data/mozambique_lulc/README.md:14-37](), [olmoearth_run_data/mozambique_lulc/olmoearth_run.yaml:29-48]()

## Training Configuration

### Data Augmentation and Transforms

```mermaid
graph TB
    subgraph "Training Transforms"
        PAD1["Pad<br/>size: 31<br/>mode: center<br/>Pads to 31x31"]
        CROP1["Crop<br/>crop_size: 16<br/>Random 16x16 crop"]
        FLIP1["Flip<br/>Random horizontal/vertical"]
        NORM1["OlmoEarthNormalize<br/>Band-specific normalization"]
    end
    
    subgraph "Validation/Test Transforms"
        NORM2["OlmoEarthNormalize<br/>Band-specific normalization"]
        PATCH["patch_size: 16<br/>Non-overlapping patches"]
    end
    
    subgraph "Prediction Transforms"
        NORM3["OlmoEarthNormalize<br/>Band-specific normalization"]
        OVERLAP["overlap_ratio: 0.25<br/>4-pixel overlap<br/>load_all_patches: true"]
    end
    
    PAD1 --> CROP1
    CROP1 --> FLIP1
    FLIP1 --> NORM1
```

**Training Configuration**

The `train_config` ([olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:218-238]()) applies aggressive augmentation:

1. **Padding**: [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:220-224]()
   - Pads input from 16x16 to 31x31 pixels (center mode)
   - Applied to sentinel2_l2a, target/segment/classes, and target/segment/valid

2. **Random Cropping**: [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:225-228]()
   - Crops back to 16x16 at random location
   - Provides spatial jittering augmentation

3. **Random Flipping**: [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:229-231]()
   - Random horizontal and vertical flips
   - Improves rotation invariance

4. **Normalization**: [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:232-235]()
   - `rslearn.models.olmoearth_pretrain.norm.OlmoEarthNormalize`
   - Band-specific mean/std normalization for Sentinel-2

**Validation and Test Configuration**

The `val_config` and `test_config` ([olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:239-248]()) use:
- `patch_size: 16` for consistent 16x16 evaluation patches
- Only normalization transform, no augmentation
- Evaluates on respective groups and split tags

**Prediction Configuration**

The `predict_config` in [olmoearth_run_data/mozambique_lulc/model.yaml:236-245]() uses:
- `load_all_patches: true` for full coverage
- `overlap_ratio: 0.25` (4 pixels) to smooth boundaries
- `skip_targets: true` since no ground truth available during inference

**Sources**: [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:218-248](), [olmoearth_run_data/mozambique_lulc/model.yaml:236-245]()

### Training Hyperparameters

| Parameter | Value | Configuration Location |
|-----------|-------|----------------------|
| **Learning Rate** | 0.0001 | [rslp_finetuning.yaml:42]() |
| **Batch Size** | 64 | [rslp_finetuning.yaml:210]() |
| **Max Epochs** | 100 | [rslp_finetuning.yaml:250]() |
| **Num Workers** | 32 | [rslp_finetuning.yaml:211]() |
| **Scheduler** | PlateauScheduler | [rslp_finetuning.yaml:44]() |
| **Scheduler Factor** | 0.2 | [rslp_finetuning.yaml:46]() |
| **Scheduler Patience** | 2 epochs | [rslp_finetuning.yaml:47]() |
| **Scheduler Cooldown** | 10 epochs | [rslp_finetuning.yaml:49]() |
| **FreezeUnfreeze Epoch** | 20 | [rslp_finetuning.yaml:264]() |
| **Unfreeze LR Factor** | 10x | [rslp_finetuning.yaml:265]() |

**Callbacks**

The trainer uses several callbacks ([olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:251-265]()):

1. **LearningRateMonitor** ([olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:252-254]())
   - Logs learning rate per epoch

2. **ModelCheckpoint** ([olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:255-260]())
   - Monitors `val_segment/accuracy`
   - Saves best model (mode: max)
   - Also saves last checkpoint

3. **FreezeUnfreeze** ([olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:261-265]())
   - Freezes encoder until epoch 20
   - Module selector: `["model", "encoder", 0]`
   - Applies 10x learning rate boost on unfreeze
   - Enables progressive fine-tuning strategy

**Sources**: [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:42-265]()

## Metrics and Evaluation

### Task Configuration

The `SegmentationTask` ([olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:73-206]()) defines:
- `num_classes: 8` (including invalid class 0)
- `zero_is_invalid: true` treats class 0 as unlabeled/invalid
- `metric_kwargs: {average: "micro"}` computes overall accuracy across all classes

### Per-Class Metrics

Both LULC and crop type models compute precision and recall for each class using `SegmentationMetric` wrapper around `torchmetrics.classification.MulticlassPrecision` and `MulticlassRecall`.

**LULC Model Metrics** ([olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:80-206]()):

| Metric Name | Class | Class Index |
|-------------|-------|-------------|
| water_precision / water_recall | Water | 1 |
| bareground_precision / bareground_recall | Bare Ground | 2 |
| rangeland_precision / rangeland_recall | Rangeland | 3 |
| floodedvegetation_precision / floodedvegetation_recall | Flooded Vegetation | 4 |
| trees_precision / trees_recall | Trees | 5 |
| cropland_precision / cropland_recall | Cropland | 6 |
| buildings_precision / buildings_recall | Buildings | 7 |

**Crop Type Model Metrics** ([olmoearth_run_data/mozambique_lulc/rslp_finetuning_croptype.yaml:80-206]()):

| Metric Name | Class | Class Index |
|-------------|-------|-------------|
| corn_precision / corn_recall | Corn | 1 |
| cassava_precision / cassava_recall | Cassava | 2 |
| rice_precision / rice_recall | Rice | 3 |
| sesame_precision / sesame_recall | Sesame | 4 |
| beans_precision / beans_recall | Beans | 5 |
| millet_precision / millet_recall | Millet | 6 |
| sorghum_precision / sorghum_recall | Sorghum | 7 |

Each metric is configured with `average: null` to compute per-class metrics and uses `class_idx` to select the specific class for evaluation.

**Sources**: [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:69-206](), [olmoearth_run_data/mozambique_lulc/rslp_finetuning_croptype.yaml:69-206]()

## Label Quality Assessment

The script `check_label_quality.py` performs three quality checks on the training data:

```bash
python olmoearth_projects/projects/mozambique_lulc/check_label_quality.py \
    --ds_path /weka/dfive-default/rslearn-eai/datasets/crop/mozambique_lulc/20251202 \
    --split train
```

### LULC Label Quality Results

From [olmoearth_run_data/mozambique_lulc/README.md:56-83]():

| Check | Metric | Value | Interpretation |
|-------|--------|-------|----------------|
| **Label Imbalance** | Cropland | 0.278 | Most common class (28%) |
| | Buildings | 0.176 | Second most common (18%) |
| | Bare Ground | 0.127 | Balanced representation |
| | Other classes | 0.098-0.114 | Adequate representation |
| **Spatial Clustering F1** | Buildings | 0.964 | Strong spatial coherence |
| | Trees | 0.918 | Strong spatial coherence |
| | Cropland | 0.820 | Good spatial clustering |
| | Bare Ground | 0.776 | Moderate clustering |
| | Rangeland | 0.710 | Moderate clustering |
| | Flooded Vegetation | 0.647 | Some spatial scatter |
| | Water | 0.561 | Most spatially dispersed |
| **Spatial Extent** | Rangeland | 0.989 | Wide geographic coverage |
| | Bare Ground | 0.906 | Wide coverage |
| | Flooded Vegetation | 0.820 | Good coverage |
| | Cropland | 0.818 | Good coverage |
| | Trees | 0.814 | Good coverage |
| | Water | 0.802 | Good coverage |
| | Buildings | 0.726 | More concentrated |

### Crop Type Label Quality Results

From [olmoearth_run_data/mozambique_lulc/README.md:85-114]():

| Check | Metric | Value | Interpretation |
|-------|--------|-------|----------------|
| **Label Imbalance** | Beans | 0.261 | Most common crop (26%) |
| | Corn | 0.245 | Well represented |
| | Rice | 0.186 | Good representation |
| | Cassava | 0.185 | Good representation |
| | Sesame | 0.100 | Limited samples |
| | Millet | 0.009 | Very few samples |
| | Sorghum | 0.014 | Very few samples |
| **Spatial Clustering F1** | Sesame | 1.000 | Perfect clustering (small area) |
| | Millet | 1.000 | Perfect clustering (small area) |
| | Rice | 0.994 | Strong clustering |
| | Corn | 0.995 | Strong clustering |
| | Sorghum | 0.990 | Strong clustering |
| | Beans | 0.989 | Strong clustering |
| | Cassava | 0.973 | Strong clustering |
| **Spatial Extent** | Cassava | 0.938 | Widest distribution |
| | Corn | 0.836 | Good coverage |
| | Beans | 0.783 | Good coverage |
| | Rice | 0.765 | Good coverage |
| | Sesame | 0.0004 | Very localized |
| | Millet | 0.0002 | Very localized |
| | Sorghum | 0.0000003 | Extremely localized |

**Quality Check Interpretation**

1. **Label Imbalance**: Measures class distribution. Values closer to 1/num_classes indicate balanced representation. Millet and sorghum are underrepresented in the crop type dataset.

2. **Spatial Clustering F1**: Measures whether similar labels cluster together. High values (>0.9) indicate labels are spatially coherent, which is expected for land cover types. Low values may indicate noisy labels or naturally dispersed classes.

3. **Spatial Extent**: Measures geographic spread of each class across the study area. Low values indicate the class is concentrated in a small region, which may limit model generalization.

**Sources**: [olmoearth_run_data/mozambique_lulc/README.md:51-114]()

## Training and Testing Workflow

### Training via rslearn_projects

Training is executed through the `rslp` command-line interface from the rslearn_projects repository:

```bash
python -m rslp.main olmoearth_pretrain launch_finetune \
    --image_name yawenzzzz/rslp20251112h \
    --config_paths+=olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml \
    --cluster+=ai2/saturn \
    --rslp_project <MY_RSLP_PROJECT_NAME> \
    --experiment_id <MY_EXPERIMENT_ID>
```

This command submits a Beaker job with GPU resources on the Saturn cluster. The specified Docker image contains the full training environment with rslearn and dependencies.

For crop type training, replace the config path with `rslp_finetuning_croptype.yaml` ([olmoearth_run_data/mozambique_lulc/README.md:119-123]()).

### Testing Workflow

Testing is performed interactively on Beaker:

1. **Start Interactive Session** ([olmoearth_run_data/mozambique_lulc/README.md:128]()):
```bash
beaker session create --remote --bare \
    --budget ai2/es-platform \
    --cluster ai2/saturn \
    --mount src=weka,ref=dfive-default,dst=/weka/dfive-default \
    --image beaker://yawenzzzz/rslp20251112h \
    --gpus 1
```

2. **Set Environment** ([olmoearth_run_data/mozambique_lulc/README.md:130]()):
```bash
cd /weka/dfive-default/gabrielt/olmoearth_projects
export RSLP_PREFIX=/weka/dfive-default/rslearn-eai
```

3. **Run Testing** ([olmoearth_run_data/mozambique_lulc/README.md:131]()):
```bash
python -m rslp.rslearn_main model test \
    --config olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml \
    --rslp_experiment <MY_EXPERIMENT_ID> \
    --rslp_project <MY_RSLP_PROJECT_NAME> \
    --force_log=true \
    --load_best=true \
    --verbose true
```

The `--load_best=true` flag loads the checkpoint with highest validation accuracy as saved by the `ModelCheckpoint` callback ([olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:255-260]()).

**Sources**: [olmoearth_run_data/mozambique_lulc/README.md:117-131]()

## Inference Configuration

### Output Specification

The `olmoearth_run.yaml` ([olmoearth_run_data/mozambique_lulc/olmoearth_run.yaml:1-81]()) defines inference output format:

**Classification Fields** ([olmoearth_run_data/mozambique_lulc/olmoearth_run.yaml:2-27]()):

```yaml
inference_results_config:
  data_type: RASTER
  classification_fields:
    - property_name: crop_type_classification
      band_index: 1
      allowed_values:
        - value: 1
          label: Water
          color: [136, 33, 233]
        # ... additional classes
```

This configuration maps integer pixel values (1-7) to human-readable labels with associated colors for visualization. The output is a single-band GeoTIFF where each pixel value represents the predicted class.

### Partitioning Strategy

The inference pipeline uses hierarchical partitioning ([olmoearth_run_data/mozambique_lulc/olmoearth_run.yaml:50-66]()):

1. **Coarse Partitioning** ([olmoearth_run_data/mozambique_lulc/olmoearth_run.yaml:51-54]())
   - `GridPartitioner` with grid_size=0.25 degrees
   - Divides large geographic areas into manageable tiles

2. **Window Partitioning** ([olmoearth_run_data/mozambique_lulc/olmoearth_run.yaml:56-66]())
   - `GridPartitioner` with grid_size=1024 pixels
   - Output projection: EPSG:3857 or UTM (use_utm=true)
   - Resolution: 10m x 10m

### Post-processing

Three post-processing stages merge results ([olmoearth_run_data/mozambique_lulc/olmoearth_run.yaml:68-80]()):

1. **process_window**: `NoopRaster` (no per-window processing)
2. **process_partition**: `CombineGeotiff` merges windows within each partition
3. **process_dataset**: `CombineGeotiff` merges all partitions into final output

All use `nodata_value: 255` to mark invalid pixels.

**Deployment**

Inference is performed through OlmoEarth Studio ([olmoearth_run_data/mozambique_lulc/README.md:135]()), where users can draw polygons and execute predictions interactively. The system uses the configuration files in `olmoearth_run_data/mozambique_lulc/` to define model behavior and output formatting.

**Sources**: [olmoearth_run_data/mozambique_lulc/olmoearth_run.yaml:1-81](), [olmoearth_run_data/mozambique_lulc/README.md:133-135]()

## Dataset Versions and Evolution

The dataset has evolved through multiple versions stored under `/weka/dfive-default/rslearn-eai/datasets/crop/mozambique_lulc/`:

| Version | Date | Key Changes | Documentation |
|---------|------|-------------|---------------|
| **20251023** | Oct 2023 | Initial version with train/test split from GPKG files | [README.md:40]() |
| **20251113** | Nov 2023 | Added spatial validation split (val_ratio=0.2) | [README.md:41-45]() |
| **20251114** | Nov 2023 | Aligned temporal dates across all provinces | [README.md:46]() |
| **20251202** | Dec 2023 | **Current version**: 8-month data export, val_ratio=0.1, aligned configs | [README.md:47-49]() |

The current version (20251202) is specified in both training configurations:
- [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:53]()
- [olmoearth_run_data/mozambique_lulc/rslp_finetuning_croptype.yaml:53]()

This version provides the most comprehensive temporal coverage (8 months) and optimized validation split for both model variants.

**Sources**: [olmoearth_run_data/mozambique_lulc/README.md:39-49](), [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:53]()

## Key Configuration Files

| File | Purpose | Key Settings |
|------|---------|--------------|
| [rslp_finetuning.yaml]() | LULC training config | 7 land cover classes, gaza/manica/zambezia groups |
| [rslp_finetuning_croptype.yaml]() | Crop type training config | 7 crop classes, crop_type group |
| [rslp_finetuning_in_season_novmar.yaml]() | Seasonal LULC variant | 5 Sentinel-2 layers for Nov-Mar season |
| [rslp_finetuning_croptype_in_season_novmar.yaml]() | Seasonal crop type variant | 5 Sentinel-2 layers for Nov-Mar season |
| [model.yaml]() | Generic model template | Environment variable placeholders for deployment |
| [dataset.json]() | Data source specification | 8 timesteps, 30-day periods, harmonized Sentinel-2 |
| [config.json]() | rslearn dataset config | Layer definitions with zoom offsets |
| [olmoearth_run.yaml]() | Inference configuration | Partitioning, post-processing, output format |

**Sources**: [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:1-268](), [olmoearth_run_data/mozambique_lulc/rslp_finetuning_croptype.yaml:1-268](), [olmoearth_run_data/mozambique_lulc/model.yaml:1-278](), [olmoearth_run_data/mozambique_lulc/dataset.json:1-63](), [olmoearth_run_data/mozambique_lulc/config.json:1-69](), [olmoearth_run_data/mozambique_lulc/olmoearth_run.yaml:1-81]()

---

# Page: LFMC Model

# LFMC Model

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/forest_loss_driver.md](docs/forest_loss_driver.md)
- [docs/lfmc.md](docs/lfmc.md)
- [olmoearth_run_data/ecosystem_type_mapping/dataset.json](olmoearth_run_data/ecosystem_type_mapping/dataset.json)
- [olmoearth_run_data/forest_loss_driver/dataset.json](olmoearth_run_data/forest_loss_driver/dataset.json)
- [olmoearth_run_data/forest_loss_driver/model.yaml](olmoearth_run_data/forest_loss_driver/model.yaml)
- [olmoearth_run_data/lfmc/dataset.json](olmoearth_run_data/lfmc/dataset.json)

</details>



This document describes the Live Fuel Moisture Content (LFMC) prediction model, a fine-tuned variant of OlmoEarth-v1-Base that performs per-pixel regression of vegetation moisture content for wildfire risk assessment. The model processes multi-temporal satellite imagery from Sentinel-1 and Sentinel-2 to predict LFMC values at 10-meter resolution.

For information about the base OlmoEarth encoder architecture, see [OlmoEarth Encoder Architecture](#5.2). For general inference procedures, see [olmoearth_run Pipeline](#7.1). For training configuration details, see [Training Configuration Files](#5.1).

**Sources:** [docs/lfmc.md:1-52]()

## Model Purpose and Application

The LFMC model addresses wildfire risk assessment by predicting the live fuel moisture content of woody vegetation. Lower LFMC values indicate drier vegetation, which correlates with higher fire risk. The model outputs continuous LFMC percentage values for each pixel, enabling spatial analysis of fire susceptibility across landscapes.

The model achieves a mean squared error of 580.6 on the test set, trained exclusively on woody vegetation samples from the continental United States.

**Sources:** [docs/lfmc.md:3-24]()

## System Architecture

```mermaid
graph TB
    subgraph "Input Data Acquisition"
        REQ["prediction_request_geometry.geojson<br/>oe_start_time: target timestamp<br/>168-day lookback period"]
        S1_QUERY["Sentinel-1 RTC Query<br/>Planetary Computer<br/>VV/VH polarization<br/>IW instrument mode"]
        S2_QUERY["Sentinel-2 L2A Query<br/>Planetary Computer<br/>12 spectral bands<br/>harmonized data"]
        MOSAIC["Temporal Mosaicking<br/>12 timesteps total<br/>14-day period duration<br/>PER_PERIOD_MOSAIC"]
    end
    
    subgraph "Model Components"
        ENCODER["OlmoEarth Encoder<br/>OLMOEARTH_V1_BASE<br/>patch_size: 4<br/>Pre-trained foundation"]
        DECODER["Segmentation Decoder<br/>Per-pixel regression<br/>Output: LFMC value<br/>float32 predictions"]
        NORMALIZE["OlmoEarthNormalize<br/>Band-specific normalization<br/>S1: vv, vh<br/>S2: 12 bands"]
    end
    
    subgraph "Data Processing"
        WINDOW["Window Processing<br/>31-pixel buffer standard<br/>10m resolution<br/>EPSG:3857 or UTM"]
        BATCH["Batch Processing<br/>Multiple windows<br/>Overlap handling<br/>Result aggregation"]
    end
    
    subgraph "Output Generation"
        RASTER["LFMC GeoTIFF<br/>float32 values<br/>Moisture percentage<br/>Per-pixel predictions"]
        VIS["Visualization<br/>Value ranges<br/>Fire risk mapping<br/>Temporal analysis"]
    end
    
    REQ --> S1_QUERY
    REQ --> S2_QUERY
    S1_QUERY --> MOSAIC
    S2_QUERY --> MOSAIC
    MOSAIC --> NORMALIZE
    NORMALIZE --> ENCODER
    ENCODER --> DECODER
    DECODER --> WINDOW
    WINDOW --> BATCH
    BATCH --> RASTER
    RASTER --> VIS
```

**Sources:** [docs/lfmc.md:14-22](), [olmoearth_run_data/lfmc/dataset.json:1-103]()

## Input Data Configuration

The model requires a precisely configured temporal sequence of satellite observations. The input data configuration is defined in `dataset.json` and specifies two satellite data sources with synchronized temporal sampling.

### Sentinel-1 RTC Configuration

```mermaid
graph LR
    S1_SOURCE["rslearn.data_sources.planetary_computer.Sentinel1"]
    S1_PARAMS["Query Parameters<br/>sar:instrument_mode: IW<br/>sar:polarizations: VV, VH"]
    S1_TEMPORAL["Temporal Configuration<br/>duration: 168d<br/>time_offset: -168d<br/>period_duration: 14d"]
    S1_BANDS["Output Bands<br/>vv: float32<br/>vh: float32"]
    S1_CONFIG["query_config<br/>max_matches: 12<br/>min_matches: 12<br/>space_mode: PER_PERIOD_MOSAIC"]
    
    S1_SOURCE --> S1_PARAMS
    S1_SOURCE --> S1_TEMPORAL
    S1_PARAMS --> S1_CONFIG
    S1_TEMPORAL --> S1_CONFIG
    S1_CONFIG --> S1_BANDS
```

The Sentinel-1 configuration queries radar backscatter data in Interferometric Wide (IW) mode with dual polarization (VV and VH). The system retrieves 12 mosaics, one per 14-day period, covering 168 days (approximately 5.5 months) prior to the target timestamp.

**Sources:** [olmoearth_run_data/lfmc/dataset.json:25-61]()

### Sentinel-2 L2A Configuration

```mermaid
graph LR
    S2_SOURCE["rslearn.data_sources.planetary_computer.Sentinel2"]
    S2_PARAMS["Query Parameters<br/>harmonize: true<br/>sort_by: eo:cloud_cover<br/>cache_dir: cache/planetary_computer"]
    S2_TEMPORAL["Temporal Configuration<br/>duration: 168d<br/>time_offset: -168d<br/>period_duration: 14d"]
    S2_BANDS["Output Bands<br/>12 spectral bands<br/>B01-B12<br/>dtype: uint16"]
    S2_CONFIG["query_config<br/>max_matches: 12<br/>min_matches: 12<br/>space_mode: PER_PERIOD_MOSAIC"]
    
    S2_SOURCE --> S2_PARAMS
    S2_SOURCE --> S2_TEMPORAL
    S2_PARAMS --> S2_CONFIG
    S2_TEMPORAL --> S2_CONFIG
    S2_CONFIG --> S2_BANDS
```

The Sentinel-2 configuration uses harmonized Level 2A (surface reflectance) data with cloud cover sorting to select the clearest imagery. The 12 spectral bands include visible, near-infrared, shortwave infrared, and atmospheric bands.

| Band | Wavelength | Resolution | Purpose |
|------|------------|------------|---------|
| B01 | 443 nm (Coastal/Aerosol) | 60m | Atmospheric correction |
| B02 | 490 nm (Blue) | 10m | Visible spectrum |
| B03 | 560 nm (Green) | 10m | Visible spectrum |
| B04 | 665 nm (Red) | 10m | Visible spectrum |
| B05 | 705 nm (Red Edge 1) | 20m | Vegetation monitoring |
| B06 | 740 nm (Red Edge 2) | 20m | Vegetation monitoring |
| B07 | 783 nm (Red Edge 3) | 20m | Vegetation monitoring |
| B08 | 842 nm (NIR) | 10m | Vegetation health |
| B8A | 865 nm (Narrow NIR) | 20m | Vegetation health |
| B09 | 945 nm (Water Vapor) | 60m | Atmospheric correction |
| B11 | 1610 nm (SWIR 1) | 20m | Moisture content |
| B12 | 2190 nm (SWIR 2) | 20m | Moisture content |

**Sources:** [olmoearth_run_data/lfmc/dataset.json:63-101]()

### Temporal Alignment

Both data sources use identical temporal configuration parameters:

- **Duration**: 168 days (24 weeks)
- **Time Offset**: -168 days (lookback from target date)
- **Period Duration**: 14 days (bi-weekly sampling)
- **Matches**: Exactly 12 timesteps required
- **Space Mode**: `PER_PERIOD_MOSAIC` (create composite for each period)

This configuration ensures synchronized observations where each timestep contains both radar and optical data for the same 14-day period, providing complementary information about vegetation structure (Sentinel-1) and spectral properties (Sentinel-2).

**Sources:** [olmoearth_run_data/lfmc/dataset.json:37-59](), [olmoearth_run_data/lfmc/dataset.json:85-99]()

## Model Architecture

```mermaid
graph TB
    subgraph "Input Processing"
        S1_INPUT["Sentinel-1 RTC<br/>12 timesteps × 2 bands<br/>Total: 24 channels"]
        S2_INPUT["Sentinel-2 L2A<br/>12 timesteps × 12 bands<br/>Total: 144 channels"]
        CONCAT["Channel Concatenation<br/>Combined: 168 channels<br/>Multi-modal time series"]
    end
    
    subgraph "Encoder Stage"
        NORM["OlmoEarthNormalize<br/>Band-specific statistics<br/>Per-sensor normalization"]
        PATCH["Patch Embedding<br/>patch_size: 4<br/>Spatial tokenization"]
        OLMOEARTH["OlmoEarth Transformer<br/>OLMOEARTH_V1_BASE<br/>Pre-trained weights<br/>Contextual features"]
    end
    
    subgraph "Decoder Stage"
        SEG_HEAD["Segmentation Decoder<br/>Upsampling layers<br/>Per-pixel outputs"]
        REGRESSION["Regression Head<br/>Output: LFMC value<br/>dtype: float32"]
    end
    
    subgraph "Output Layer"
        PREDICTION["LFMC Predictions<br/>Moisture percentage<br/>Continuous values<br/>10m resolution"]
    end
    
    S1_INPUT --> CONCAT
    S2_INPUT --> CONCAT
    CONCAT --> NORM
    NORM --> PATCH
    PATCH --> OLMOEARTH
    OLMOEARTH --> SEG_HEAD
    SEG_HEAD --> REGRESSION
    REGRESSION --> PREDICTION
```

The LFMC model uses a standard encoder-decoder architecture with the pre-trained OlmoEarth foundation model as the encoder. The model processes multi-modal, multi-temporal satellite data through the following stages:

1. **Input Concatenation**: Sentinel-1 and Sentinel-2 data are concatenated along the channel dimension, creating a 168-channel input (24 + 144 channels)

2. **Normalization**: The `OlmoEarthNormalize` transform applies band-specific normalization using pre-computed statistics for each sensor type

3. **Encoder**: The OlmoEarth encoder with patch size 4 processes the normalized input, producing contextualized feature representations

4. **Decoder**: A segmentation decoder upsamples the encoded features back to the original spatial resolution

5. **Regression Head**: The final layer outputs a single-channel float32 raster representing LFMC values at each pixel

**Sources:** [docs/lfmc.md:14-22](), [olmoearth_run_data/lfmc/dataset.json:1-103]()

## Training Data and Configuration

The LFMC model is trained on the Globe-LFMC 2.0 dataset, a comprehensive collection of field-measured live fuel moisture content values.

### Training Dataset

```mermaid
graph TB
    subgraph "Globe-LFMC 2.0 Source"
        DATASET["Globe-LFMC 2.0<br/>Marta Yebra et al.<br/>CC0 License"]
        SUBSET["Continental US Subset<br/>Woody fuel type only<br/>Point measurements"]
    end
    
    subgraph "Sample Structure"
        SAMPLE["Sample Attributes<br/>longitude<br/>latitude<br/>timestamp<br/>fuel_type<br/>LFMC value"]
    end
    
    subgraph "Window Creation"
        CENTER["Window Centering<br/>Centered at sample location<br/>Standard buffer sizing"]
        TIMERANGE["Time Range<br/>168 days ending at timestamp<br/>12 bi-weekly periods"]
    end
    
    subgraph "Spatial Splitting"
        GRID["Grid-based Splitting<br/>128×128 pixel cells<br/>Hash-based assignment"]
        SPLITS["Split Ratios<br/>Train: 70%<br/>Val: 20%<br/>Test: 10%"]
    end
    
    DATASET --> SUBSET
    SUBSET --> SAMPLE
    SAMPLE --> CENTER
    SAMPLE --> TIMERANGE
    CENTER --> GRID
    TIMERANGE --> GRID
    GRID --> SPLITS
```

### Dataset Details

| Attribute | Value |
|-----------|-------|
| Source | Globe-LFMC 2.0 (Figshare) |
| Geographic Coverage | Continental United States |
| Fuel Type | Woody vegetation only |
| Measurement Type | Field-collected point samples |
| Temporal Range | 168 days per sample |
| License | CC0 (Public Domain) |

### Spatial Data Splitting

The dataset uses a spatial splitting strategy to prevent data leakage and ensure model generalization:

1. The study area is divided into 128×128 pixel grid cells
2. Each grid cell is assigned to train, validation, or test split via hash function
3. All samples within a grid cell belong to the same split
4. Split ratios: 70% training, 20% validation, 10% test

This approach ensures that geographically proximate samples remain in the same split, preventing the model from exploiting spatial autocorrelation during evaluation.

**Sources:** [docs/lfmc.md:26-40]()

### Training Configuration

The model training follows the standard fine-tuning workflow described in [Fine-tuning Process](#5.3). Key training parameters include:

- **Optimizer**: AdamW with initial learning rate
- **Scheduler**: PlateauScheduler with patience for validation loss
- **Loss Function**: Mean Squared Error (MSE) for regression
- **Callbacks**: FreezeUnfreeze for progressive training, ModelCheckpoint for best model saving
- **Data Augmentation**: Padding, flipping, and normalization transforms

The encoder starts frozen and unfreezes after a specified number of epochs, following the progressive fine-tuning strategy used across all OlmoEarth models.

**Sources:** [docs/lfmc.md:49-51]()

## Inference Usage

### Prediction Request Configuration

To run inference, create a `prediction_request_geometry.geojson` file specifying the target timestamp and geographic extent:

```json
{
  "type": "FeatureCollection",
  "features": [{
    "type": "Feature",
    "geometry": {
      "type": "Polygon",
      "coordinates": [[...]]
    },
    "properties": {
      "oe_start_time": "2024-01-15T00:00:00Z"
    }
  }]
}
```

**Important**: Set `oe_start_time` to the timestamp for which you want LFMC predictions (e.g., current date). The model automatically queries satellite data from the 168 days preceding this timestamp. The `oe_end_time` property is not used and can be omitted or set equal to `oe_start_time`.

**Sources:** [docs/lfmc.md:42-47]()

### Inference Pipeline

```mermaid
graph TB
    subgraph "Input Preparation"
        GEOJSON["prediction_request_geometry.geojson<br/>Target polygon and timestamp"]
        CHECKPOINT["Model Checkpoint<br/>allenai/OlmoEarth-v1-FT-LFMC-Base<br/>model.ckpt"]
    end
    
    subgraph "Data Acquisition"
        LOOKBACK["Temporal Lookback<br/>168 days from oe_start_time<br/>Automatic window calculation"]
        QUERY_S1["Query Sentinel-1<br/>12 bi-weekly mosaics<br/>VV/VH polarization"]
        QUERY_S2["Query Sentinel-2<br/>12 bi-weekly mosaics<br/>12 spectral bands"]
    end
    
    subgraph "Processing"
        PARTITION["Spatial Partitioning<br/>GridPartitioner<br/>Efficient tiling"]
        PREDICT["Model Inference<br/>Batch processing<br/>Per-pixel regression"]
    end
    
    subgraph "Output"
        COMBINE["Result Aggregation<br/>CombineGeotiff<br/>Merge partitions"]
        OUTPUT["LFMC Raster<br/>float32 GeoTIFF<br/>Moisture percentages"]
    end
    
    GEOJSON --> LOOKBACK
    CHECKPOINT --> PREDICT
    LOOKBACK --> QUERY_S1
    LOOKBACK --> QUERY_S2
    QUERY_S1 --> PARTITION
    QUERY_S2 --> PARTITION
    PARTITION --> PREDICT
    PREDICT --> COMBINE
    COMBINE --> OUTPUT
```

### Command Line Usage

Download the model checkpoint and run inference:

```bash
# Download model checkpoint
mkdir -p ./checkpoints
wget -O checkpoints/lfmc.ckpt \
  https://huggingface.co/allenai/OlmoEarth-v1-FT-LFMC-Base/resolve/main/model.ckpt

# Place prediction request geometry
mv prediction_request_geometry.geojson \
  olmoearth_run_data/lfmc/prediction_request_geometry.geojson

# Run inference
export NUM_WORKERS=32
export WANDB_PROJECT=lfmc_inference
export WANDB_NAME=lfmc_run
export WANDB_ENTITY=YOUR_ENTITY

python -m olmoearth_projects.main olmoearth_run olmoearth_run \
  --config_path $PWD/olmoearth_run_data/lfmc/ \
  --checkpoint_path $PWD/checkpoints/lfmc.ckpt \
  --scratch_path project_data/lfmc/
```

The output will be a GeoTIFF file with float32 values representing LFMC percentages at each pixel. Lower values indicate drier vegetation with higher fire risk.

**Sources:** [docs/lfmc.md:42-47]()

## Output Interpretation

The model outputs continuous LFMC values as floating-point percentages. Typical interpretation ranges:

| LFMC Range | Vegetation State | Fire Risk |
|------------|------------------|-----------|
| > 120% | Very high moisture | Very low |
| 80-120% | Adequate moisture | Low |
| 50-80% | Moderate moisture | Moderate |
| 30-50% | Low moisture | High |
| < 30% | Critical dryness | Extreme |

The output raster can be visualized in GIS software (QGIS, ArcGIS) or through OlmoEarth Studio for interactive mapping. Temporal analysis comparing LFMC values across multiple dates reveals vegetation stress patterns and seasonal dynamics.

**Sources:** [docs/lfmc.md:1-24]()

## Model Performance

The LFMC model achieves a **mean squared error (MSE) of 580.6** on the test set. This MSE represents the average squared difference between predicted and actual LFMC values for woody vegetation in the continental United States.

Given that LFMC values typically range from 30% to 200%, the root mean squared error (RMSE) of approximately 24% indicates the model's predictions are generally within this margin of the true values.

**Sources:** [docs/lfmc.md:24]()

## Model Distribution

The LFMC model and associated data are publicly available:

| Resource | Location |
|----------|----------|
| Model Checkpoint | [HuggingFace Hub](https://huggingface.co/allenai/OlmoEarth-v1-FT-LFMC-Base) |
| Annotation GeoJSONs | [Google Cloud Storage](https://storage.googleapis.com/ai2-olmoearth-projects-public-data/projects/lfmc/20251029/) |
| rslearn Dataset | [dataset.tar](https://storage.googleapis.com/ai2-olmoearth-projects-public-data/projects/lfmc/20251029/dataset.tar) |
| Training Data License | CC0 (Public Domain) |

**Sources:** [docs/lfmc.md:10-12](), [docs/lfmc.md:40]()

---

# Page: Forest Loss Driver Model

# Forest Loss Driver Model

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/forest_loss_driver.md](docs/forest_loss_driver.md)
- [docs/lfmc.md](docs/lfmc.md)
- [olmoearth_run_data/forest_loss_driver/model.yaml](olmoearth_run_data/forest_loss_driver/model.yaml)
- [olmoearth_run_data/forest_loss_driver/olmoearth_run.yaml](olmoearth_run_data/forest_loss_driver/olmoearth_run.yaml)

</details>



This document describes the Forest Loss Driver classification model, which predicts the cause of deforestation from satellite imagery. The model operates on GLAD-S2 forest loss alerts and classifies the driver into 10 categories including agriculture, mining, logging, and natural causes. For information about other classification models in the repository, see [Available Models](#6). For details on the general inference pipeline, see [olmoearth_run Pipeline](#7.1).

## Purpose and Scope

The Forest Loss Driver model (`OlmoEarth-v1-FT-ForestLossDriver-Base`) is a fine-tuned classification model that extends GLAD-S2 forest loss alerts with driver attribution. Rather than detecting forest loss from scratch, this model takes existing forest loss detections and predicts what caused the loss. The model analyzes pre-deforestation and post-deforestation Sentinel-2 imagery to classify the driver into one of 10 categories.

**Key Characteristics:**
- **Task Type:** Multi-class classification (10 classes)
- **Input:** Pre and post forest loss Sentinel-2 L2A imagery (4 timesteps each)
- **Output:** Driver classification per forest loss polygon
- **Validation Accuracy:** 76.1%
- **Data Source:** Amazon Conservation Association annotations
- **Integration:** Operates on GLAD-S2 forest loss alerts

**Sources:** [docs/forest_loss_driver.md:1-10]()

## Driver Categories

The model classifies forest loss into the following 10 categories:

| Category | Description | Use Case |
|----------|-------------|----------|
| `agriculture` | Forest cleared for agricultural expansion | Crop production, livestock grazing |
| `mining` | Forest removal for mineral extraction | Open-pit mining, quarrying |
| `airstrip` | Forest cleared for aviation infrastructure | Remote area access |
| `road` | Forest loss due to road construction | Transportation infrastructure |
| `logging` | Selective or clear-cut timber harvesting | Timber production |
| `burned` | Forest loss from fire events | Wildfire, controlled burns |
| `landslide` | Natural loss from geological events | Slope failure |
| `hurricane` | Storm damage to forest canopy | Tropical cyclone impacts |
| `river` | Forest loss from river course changes | Erosion, flooding |
| `none` | No clear driver or unclassifiable | Ambiguous cases |

**Sources:** [docs/forest_loss_driver.md:11-22](), [olmoearth_run_data/forest_loss_driver/model.yaml:59]()

## Model Architecture

### Architecture Overview

```mermaid
graph TB
    subgraph "Input Data Structure"
        PRE["Pre-Loss Imagery<br/>4 Sentinel-2 L2A timesteps<br/>12 bands each<br/>64×64 pixels"]
        POST["Post-Loss Imagery<br/>4 Sentinel-2 L2A timesteps<br/>12 bands each<br/>64×64 pixels"]
    end
    
    subgraph "Encoder: SimpleTimeSeries"
        CONCAT["Concatenate Groups<br/>groups: [[0], [1]]<br/>image_channels: 48"]
        OLMO["OlmoEarth Encoder<br/>model_id: OLMOEARTH_V1_BASE<br/>patch_size: 4"]
        FEAT["Feature Maps<br/>in_channels: 1536"]
    end
    
    subgraph "Decoder: PoolingDecoder"
        CONV["Convolutional Layers<br/>num_conv_layers: 1"]
        FC["Fully Connected Layers<br/>num_fc_layers: 2<br/>out_channels: 10"]
    end
    
    subgraph "Task: ClassificationHead"
        LOGITS["Class Logits<br/>10 classes"]
        PROBS["Probabilities<br/>property: probs"]
    end
    
    PRE --> CONCAT
    POST --> CONCAT
    CONCAT --> OLMO
    OLMO --> FEAT
    FEAT --> CONV
    CONV --> FC
    FC --> LOGITS
    LOGITS --> PROBS
    
    style OLMO fill:#f9f9f9
    style FC fill:#f0f0f0
```

**Diagram: Forest Loss Driver Model Architecture with Code Entities**

The model uses a two-stage encoder approach. The `SimpleTimeSeries` wrapper concatenates pre-forest-loss and post-forest-loss feature maps before feeding them to the decoder. Despite its name, `SimpleTimeSeries` is used here to combine spatial features from the two temporal groups rather than for true time series processing.

**Sources:** [olmoearth_run_data/forest_loss_driver/model.yaml:6-28]()

### Encoder Configuration

The encoder consists of the `OlmoEarth` foundation model wrapped in a `SimpleTimeSeries` module:

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `model_id` | `OLMOEARTH_V1_BASE` | Pre-trained OlmoEarth checkpoint identifier |
| `patch_size` | `4` | Patch size for vision transformer |
| `image_channels` | `48` | Total channels (12 bands × 4 timesteps) |
| `image_key` | `sentinel2_l2a` | Input data key |
| `groups` | `[[0], [1]]` | Group 0: pre-loss, Group 1: post-loss |

The encoder processes two groups separately:
- **Group 0:** Four pre-loss Sentinel-2 timesteps (layers: `pre_sentinel2`, `pre_sentinel2.1`, `pre_sentinel2.2`, `pre_sentinel2.3`)
- **Group 1:** Four post-loss Sentinel-2 timesteps (layers: `post_sentinel2`, `post_sentinel2.1`, `post_sentinel2.2`, `post_sentinel2.3`)

Each group contains 12 Sentinel-2 bands: `B02`, `B03`, `B04`, `B08`, `B05`, `B06`, `B07`, `B8A`, `B11`, `B12`, `B01`, `B09`

**Sources:** [olmoearth_run_data/forest_loss_driver/model.yaml:10-20](), [olmoearth_run_data/forest_loss_driver/model.yaml:44-50]()

### Decoder Configuration

The `PoolingDecoder` reduces spatial dimensions and classifies the forest loss driver:

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `in_channels` | `1536` | Input feature dimension from OlmoEarth |
| `out_channels` | `10` | Number of driver classes |
| `num_conv_layers` | `1` | Convolutional layers for spatial processing |
| `num_fc_layers` | `2` | Fully connected layers for classification |

The decoder is followed by a `ClassificationHead` that applies softmax and outputs probabilities to the `probs` property.

**Sources:** [olmoearth_run_data/forest_loss_driver/model.yaml:21-28]()

## Training Configuration

### Data Module

The `RslearnDataModule` configuration specifies:

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `batch_size` | `8` | Small batch size due to large input windows |
| `property_name` | `new_label` | Label property in vector data |
| `allow_invalid` | `true` | Allow samples with invalid labels |
| `skip_unknown_categories` | `true` | Skip samples with unknown driver categories |
| `metric_kwargs.average` | `micro` | Micro-averaged metrics across classes |

**Sources:** [olmoearth_run_data/forest_loss_driver/model.yaml:40-64]()

### Transforms Pipeline

```mermaid
graph LR
    INPUT["Input Window<br/>Variable size"]
    PAD["Pad<br/>mode: center<br/>size: 64×64"]
    NORM["OlmoEarthNormalize<br/>12 Sentinel-2 bands"]
    FLIP["Flip<br/>Random augmentation"]
    CONCAT["Concatenate<br/>RGB visualization<br/>bands: [2,1,0]"]
    OUTPUT["Normalized Tensor"]
    
    INPUT --> PAD
    PAD --> NORM
    NORM --> FLIP
    FLIP --> CONCAT
    CONCAT --> OUTPUT
```

**Diagram: Transform Pipeline for Forest Loss Driver Training**

The transform pipeline ensures consistent 64×64 pixel input windows centered on the forest loss polygon.

**Sources:** [olmoearth_run_data/forest_loss_driver/model.yaml:67-88]()

### Training Strategy

The model uses a freeze-unfreeze training strategy to leverage the pre-trained OlmoEarth encoder:

| Phase | Epochs | Learning Rate | Frozen Modules |
|-------|--------|---------------|----------------|
| Initial | 0-19 | 0.0001 | OlmoEarth encoder frozen |
| Fine-tuning | 20-99 | 0.001 (10× boost) | All modules unfrozen |

**Scheduler:** `PlateauScheduler` with factor=0.2, patience=2 epochs, cooldown=10 epochs

**Sources:** [olmoearth_run_data/forest_loss_driver/model.yaml:29-39](), [olmoearth_run_data/forest_loss_driver/model.yaml:112-116]()

## Training Data

### Data Source

The training data consists of forest loss driver annotations produced by **Amazon Conservation Association**. Each annotation contains:
- A polygon geometry derived from GLAD-S2 forest loss alerts
- A timestamp indicating when the forest loss occurred
- A driver category label (one of 10 classes)

The data is released under [CC BY 4.0 license](https://creativecommons.org/licenses/by/4.0/deed.en).

**Sources:** [docs/forest_loss_driver.md:54-63]()

### Image Acquisition

For each annotation, the system retrieves:
- **Pre-loss imagery:** 4 Sentinel-2 L2A images captured before the forest loss timestamp
- **Post-loss imagery:** 4 Sentinel-2 L2A images captured after the forest loss timestamp
- **Window size:** 64×64 pixels (at 10 m/pixel resolution) centered on the polygon

The specific timesteps and mosaicking strategy are handled by rslearn's data acquisition pipeline.

**Sources:** [docs/forest_loss_driver.md:32-36](), [docs/forest_loss_driver.md:57-59]()

### Data Splitting

The dataset uses a simple random split:
- **Training set:** 75% of samples
- **Validation set:** 25% of samples

No test set is defined; the validation set serves as the evaluation benchmark.

**Sources:** [docs/forest_loss_driver.md:61](), [olmoearth_run_data/forest_loss_driver/model.yaml:89-97]()

## Performance Metrics

### Overall Accuracy

The model achieves **76.1% accuracy** on the validation set. This represents the fraction of forest loss polygons for which the correct driver was predicted as the top class.

**Sources:** [docs/forest_loss_driver.md:38-39]()

### Confusion Matrix

The following confusion matrix shows per-class performance on the validation set:

| True \ Pred | Ag | Airstrip | Burned | Hurricane | Landslide | Logging | Mining | None | River | Road |
|-------------|----|---------:|-------:|----------:|----------:|--------:|-------:|-----:|------:|-----:|
| **Ag** | 37 | 0 | 2 | 0 | 0 | 0 | 0 | 2 | 0 | 3 |
| **Airstrip** | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| **Burned** | 2 | 0 | 21 | 3 | 0 | 0 | 0 | 4 | 0 | 0 |
| **Hurricane** | 0 | 0 | 0 | 6 | 0 | 0 | 0 | 0 | 0 | 0 |
| **Landslide** | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 |
| **Logging** | 0 | 0 | 0 | 2 | 0 | 2 | 0 | 0 | 0 | 0 |
| **Mining** | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 |
| **None** | 2 | 0 | 1 | 1 | 0 | 2 | 0 | 11 | 0 | 1 |
| **River** | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 |
| **Road** | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 4 |

**Key Observations:**
- Strong performance on agriculture (37/44 = 84.1%), burned (21/30 = 70.0%), and road (4/4 = 100%)
- Confusion between burned and hurricane classes
- Limited samples for rare classes (airstrip, landslide, river)
- "None" category captures ambiguous cases that confuse with other categories

**Sources:** [docs/forest_loss_driver.md:41-52]()

## Inference Process

### GLAD-S2 Alert Integration

```mermaid
graph TB
    subgraph "Alert Extraction: extract_alerts command"
        GCS["GLAD-S2 Alert Files<br/>GCS: earthenginepartners-hansen/S2alert/<br/>TIF format per tile"]
        EXTRACT["extract_alerts.py<br/>Parameters:<br/>- gcs_tiff_filenames<br/>- days: time range<br/>- out_fname"]
        POLYGONS["Connected Components<br/>Polygonized alerts"]
    end
    
    subgraph "Prediction Request: prediction_request_geometry.geojson"
        GEOJSON["GeoJSON Features<br/>One per forest loss polygon<br/>Properties:<br/>- oe_start_time<br/>- oe_end_time"]
    end
    
    subgraph "Inference Pipeline: olmoearth_run"
        NOOP["NoopPartitioner<br/>No coarse partitioning"]
        FIXED["FixedWindowPartitioner<br/>window_size: 128<br/>EPSG: 3857<br/>resolution: 9.55m"]
        QUERY["Planetary Computer Query<br/>Pre/Post Sentinel-2 L2A<br/>4 timesteps each"]
        MODEL["Model Inference<br/>forest_loss_driver.ckpt<br/>ClassificationHead output"]
    end
    
    subgraph "Output: CombineGeojson"
        RESULTS["results.geojson<br/>Properties:<br/>- new_label: class index<br/>- probs: probabilities"]
        VIZ["Visualization<br/>Color-coded by driver<br/>QGIS/OlmoEarth Studio"]
    end
    
    GCS --> EXTRACT
    EXTRACT --> POLYGONS
    POLYGONS --> GEOJSON
    GEOJSON --> NOOP
    NOOP --> FIXED
    FIXED --> QUERY
    QUERY --> MODEL
    MODEL --> RESULTS
    RESULTS --> VIZ
    
    style EXTRACT fill:#f9f9f9
    style MODEL fill:#f0f0f0
```

**Diagram: Forest Loss Driver Inference Workflow from GLAD-S2 Alerts**

**Sources:** [docs/forest_loss_driver.md:66-96](), [olmoearth_run_data/forest_loss_driver/olmoearth_run.yaml:38-64]()

### Extracting GLAD-S2 Alerts

The `extract_alerts` command processes GLAD-S2 alert rasters into prediction request geometries:

```bash
python -m olmoearth_projects.main projects.forest_loss_driver extract_alerts \
  --extract_alerts_args.gcs_tiff_filenames+=080W_20S_070W_10S.tif \
  --extract_alerts_args.out_fname='prediction_request_geometry.geojson' \
  --extract_alerts_args.days=90
```

**Parameters:**
- `gcs_tiff_filenames`: List of GLAD-S2 tiles to process (e.g., `080W_20S_070W_10S.tif`)
- `out_fname`: Output GeoJSON file path
- `days`: Time range in days from current timestamp into the past

The command reads alert rasters from [GCS](https://console.cloud.google.com/storage/browser/earthenginepartners-hansen/S2alert/), identifies connected components of alert pixels, and polygonizes them into individual features.

**Sources:** [docs/forest_loss_driver.md:71-85]()

### Partitioning Strategy

The `olmoearth_run.yaml` defines a two-stage partitioning approach:

| Stage | Partitioner | Configuration |
|-------|-------------|---------------|
| `partition_request_geometry` | `NoopPartitioner` | No coarse-level partitioning |
| `prepare_window_geometries` | `FixedWindowPartitioner` | 128×128 pixel windows in EPSG:3857 |

The `FixedWindowPartitioner` creates windows centered on each forest loss polygon with fixed size and projection:

```yaml
window_size: 128
output_projection:
  crs: EPSG:3857 (Web Mercator)
  x_resolution: 9.554628535647032
  y_resolution: -9.554628535647032
```

The resolution (9.55 m/pixel) matches the extraction process to ensure consistent spatial alignment.

**Sources:** [olmoearth_run_data/forest_loss_driver/olmoearth_run.yaml:38-54]()

### Running Inference

After extracting alerts and downloading the model checkpoint, run inference:

```bash
# Move prediction request geometry to project directory
mv prediction_request_geometry.geojson \
   olmoearth_run_data/forest_loss_driver/prediction_request_geometry.geojson

# Download model checkpoint
mkdir -p ./checkpoints
wget -O checkpoints/forest_loss_driver.ckpt \
  https://huggingface.co/allenai/OlmoEarth-v1-FT-ForestLossDriver-Base/resolve/main/model.ckpt

# Set environment variables
export NUM_WORKERS=32
export WANDB_PROJECT=forest_loss_driver
export WANDB_NAME=forest_loss_driver
export WANDB_ENTITY=YOUR_WANDB_ENTITY

# Run inference
python -m olmoearth_projects.main olmoearth_run olmoearth_run \
  --config_path $PWD/olmoearth_run_data/forest_loss_driver/ \
  --checkpoint_path $PWD/checkpoints/forest_loss_driver.ckpt \
  --scratch_path project_data/forest_loss_driver/
```

**Sources:** [docs/forest_loss_driver.md:86-96]()

## Output Format

### Classification Fields

The `inference_results_config` in `olmoearth_run.yaml` defines output metadata:

| Property | Type | Content |
|----------|------|---------|
| `data_type` | string | `vector` (GeoJSON output) |
| `property_name` | string | `new_label` |
| `band_index` | integer | `1` (classification band) |
| `allowed_values` | array | 10 driver classes with labels and colors |

Each output feature contains:
- **Geometry:** The forest loss polygon
- **`new_label`:** Integer class index (0-9)
- **`probs`:** Array of 10 probabilities (one per class)

**Sources:** [olmoearth_run_data/forest_loss_driver/olmoearth_run.yaml:1-36]()

### Visualization Colors

Each driver class has an assigned RGB color for visualization:

| Class | Label | RGB Color |
|-------|-------|-----------|
| 0 | agriculture | [137, 243, 54] (bright green) |
| 1 | mining | [255, 222, 33] (yellow) |
| 2 | airstrip | [255, 192, 203] (pink) |
| 3 | road | [255, 165, 0] (orange) |
| 4 | logging | [128, 0, 128] (purple) |
| 5 | burned | [255, 140, 0] (dark orange) |
| 6 | landslide | [255, 0, 0] (red) |
| 7 | hurricane | [245, 245, 220] (beige) |
| 8 | river | [0, 255, 255] (cyan) |
| 9 | none | [255, 255, 255] (white) |

These colors enable immediate visual interpretation when viewing results in QGIS or OlmoEarth Studio.

**Sources:** [olmoearth_run_data/forest_loss_driver/olmoearth_run.yaml:6-36]()

### Post-processing

The post-processing strategy uses `CombineGeojson` at all three levels:

```yaml
postprocessing_strategies:
  process_window: CombineGeojson
  process_partition: CombineGeojson
  process_dataset: CombineGeojson
```

This aggregates individual window predictions into partition-level GeoJSON files, then combines all partitions into a final `results.geojson` containing all classified forest loss polygons.

**Sources:** [olmoearth_run_data/forest_loss_driver/olmoearth_run.yaml:56-64]()

## Model Artifacts and Resources

### Public Distribution

| Resource | Location | Description |
|----------|----------|-------------|
| Model Checkpoint | [HuggingFace Hub](https://huggingface.co/allenai/OlmoEarth-v1-FT-ForestLossDriver-Base/resolve/main/model.ckpt) | Trained model weights |
| rslearn Dataset | [GCS Bucket](https://storage.googleapis.com/ai2-olmoearth-projects-public-data/projects/forest_loss_driver/20251029/dataset.tar) | Training dataset archive |
| Documentation | [GitHub docs/](https://github.com/allenai/olmoearth_projects/blob/main/docs/forest_loss_driver.md) | Usage guide and examples |

**Sources:** [docs/forest_loss_driver.md:24-28]()

### Configuration Files

The model requires three configuration files for both training and inference:

1. **`model.yaml`** - Model architecture, training loop, and data loading configuration
   - Location: [olmoearth_run_data/forest_loss_driver/model.yaml]()
   - Defines: Encoder, decoder, optimizer, scheduler, callbacks

2. **`dataset.json`** - Data source configuration (not shown in provided files)
   - Specifies Planetary Computer queries for Sentinel-2 L2A

3. **`olmoearth_run.yaml`** - Inference pipeline configuration
   - Location: [olmoearth_run_data/forest_loss_driver/olmoearth_run.yaml]()
   - Defines: Partitioning, post-processing, output format

**Sources:** [docs/forest_loss_driver.md:24-28](), [olmoearth_run_data/forest_loss_driver/model.yaml:1](), [olmoearth_run_data/forest_loss_driver/olmoearth_run.yaml:1]()

---

# Page: Mangrove Extent Model

# Mangrove Extent Model

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/mangrove.md](docs/mangrove.md)
- [olmoearth_run_data/mangrove/dataset.json](olmoearth_run_data/mangrove/dataset.json)
- [olmoearth_run_data/mangrove/model.yaml](olmoearth_run_data/mangrove/model.yaml)
- [olmoearth_run_data/mangrove/olmoearth_run.yaml](olmoearth_run_data/mangrove/olmoearth_run.yaml)

</details>



## Overview

The Mangrove Extent Model (`OlmoEarth-v1-FT-Mangrove-Base`) is a fine-tuned classification model that predicts mangrove extent from Sentinel-2 satellite imagery. The model classifies each 2×2 pixel patch into one of three classes: mangrove, water, or other land cover types. It achieves 97.6% overall accuracy on the validation set.

This page documents the model architecture, training configuration, data sources, and inference setup. For general information about model training workflows, see [Model Training](#5). For details on running inference with this model, see [olmoearth_run Pipeline](#7.1).

**Sources:** [docs/mangrove.md:1-37]()

## Model Architecture

The mangrove extent model follows the standard OlmoEarth fine-tuning architecture with an encoder-decoder structure:

```mermaid
graph TB
    subgraph "Input Processing"
        S2["Sentinel-2 L2A<br/>12 Timesteps<br/>12 Bands per Timestep"]
        NORM["OlmoEarthNormalize<br/>std_multiplier: 2.0"]
        PAD["Pad Transform<br/>size: 2<br/>mode: center"]
    end
    
    subgraph "Model Architecture"
        ENCODER["OlmoEarth Encoder<br/>model_id: OLMOEARTH_V1_BASE<br/>patch_size: 2<br/>in_channels: 768"]
        DECODER["SegmentationPoolingDecoder<br/>in_channels: 768<br/>out_channels: 4<br/>num_conv_layers: 0<br/>num_fc_layers: 0"]
        HEAD["SegmentationHead<br/>Task: mangrove_classification"]
    end
    
    subgraph "Output"
        OUTPUT["Classification Output<br/>Class 1: Mangrove<br/>Class 2: Water<br/>Class 3: Other<br/>Class 0: Invalid"]
    end
    
    S2 --> NORM
    NORM --> PAD
    PAD --> ENCODER
    ENCODER --> DECODER
    DECODER --> HEAD
    HEAD --> OUTPUT
```

**Diagram: Mangrove Model Architecture and Data Flow**

### Encoder Configuration

The encoder uses the pre-trained `OlmoEarth` model with `OLMOEARTH_V1_BASE` initialization. The patch size is set to 2, meaning the model processes 2×2 pixel patches and outputs classification predictions at this resolution.

**Sources:** [olmoearth_run_data/mangrove/model.yaml:9-13]()

### Decoder Configuration

The decoder is a `SegmentationPoolingDecoder` with the following configuration:

| Parameter | Value | Description |
|-----------|-------|-------------|
| `in_channels` | 768 | Input feature dimension from encoder |
| `out_channels` | 4 | Number of output classes |
| `num_conv_layers` | 0 | No additional convolutional layers |
| `num_fc_layers` | 0 | No additional fully connected layers |
| `image_key` | `sentinel2_l2a` | Input image identifier |

The output has 4 channels, where class 0 represents invalid pixels (handled by `zero_is_invalid: true` in the task configuration).

**Sources:** [olmoearth_run_data/mangrove/model.yaml:14-25]()

### Task Configuration

The model uses a `SegmentationTask` for the `mangrove_classification` task with these settings:

- **num_classes**: 4 (including invalid class)
- **zero_is_invalid**: true (class 0 filtered during evaluation)
- **enable_accuracy_metric**: true
- **metric averaging**: micro

**Sources:** [olmoearth_run_data/mangrove/model.yaml:84-145]()

## Input Data Configuration

### Temporal Configuration

The model processes 12 timesteps of Sentinel-2 imagery over a one-year period:

```mermaid
graph LR
    subgraph "Temporal Coverage"
        REF["Reference Time<br/>oe_end_time"]
        OFFSET["Time Offset<br/>-180d"]
        START["Start Time<br/>6 months before reference"]
        DURATION["Total Duration<br/>366d"]
        END["End Time<br/>6 months after reference"]
    end
    
    subgraph "Temporal Mosaicking"
        P1["Period 1<br/>30 days"]
        P2["Period 2<br/>30 days"]
        P3["Period 3<br/>30 days"]
        PDOTS["..."]
        P12["Period 12<br/>30 days"]
    end
    
    REF --> OFFSET
    OFFSET --> START
    START --> DURATION
    DURATION --> END
    
    START --> P1
    P1 --> P2
    P2 --> P3
    P3 --> PDOTS
    PDOTS --> P12
    P12 --> END
```

**Diagram: Temporal Configuration for Mangrove Model**

The `time_offset` of `-180d` means that the start time is 6 months before the reference date, and with a duration of `366d`, the imagery spans approximately 6 months before and after the reference date.

**Sources:** [olmoearth_run_data/mangrove/dataset.json:39-52]()

### Sentinel-2 Band Configuration

The model uses all 12 Sentinel-2 L2A bands in a specific order:

| Band | Wavelength Range | Spatial Resolution | Purpose |
|------|------------------|-------------------|---------|
| B02 | Blue (490 nm) | 10m | Visible |
| B03 | Green (560 nm) | 10m | Visible |
| B04 | Red (665 nm) | 10m | Visible |
| B08 | NIR (842 nm) | 10m | Near-infrared |
| B05 | Red Edge 1 (705 nm) | 20m | Vegetation |
| B06 | Red Edge 2 (740 nm) | 20m | Vegetation |
| B07 | Red Edge 3 (783 nm) | 20m | Vegetation |
| B8A | NIR Narrow (865 nm) | 20m | Vegetation |
| B11 | SWIR 1 (1610 nm) | 20m | Moisture |
| B12 | SWIR 2 (2190 nm) | 20m | Moisture |
| B01 | Coastal Aerosol (443 nm) | 60m | Atmospheric |
| B09 | Water Vapor (945 nm) | 60m | Atmospheric |

**Sources:** [olmoearth_run_data/mangrove/model.yaml:59-77](), [olmoearth_run_data/mangrove/dataset.json:20-33]()

### Data Source Configuration

Sentinel-2 data is acquired from Microsoft Planetary Computer with these parameters:

- **cache_dir**: `cache/planetary_computer`
- **harmonize**: true (ensures consistent radiometry across scenes)
- **sort_by**: `eo:cloud_cover` (prioritizes low-cloud imagery)
- **max_matches**: 12 (exactly 12 images required)
- **min_matches**: 12 (no tolerance for missing data)
- **period_duration**: `30d` (one mosaic per 30-day period)
- **space_mode**: `PER_PERIOD_MOSAIC` (temporal compositing within each period)

**Sources:** [olmoearth_run_data/mangrove/dataset.json:37-51]()

## Training Configuration

### Training Loop Parameters

```mermaid
graph TB
    subgraph "Lightning Module Configuration"
        MODULE["RslearnLightningModule"]
        LR["Learning Rate<br/>lr: 0.0001"]
        PLATEAU["ReduceLROnPlateau<br/>plateau: true<br/>factor: 0.2<br/>patience: 2<br/>cooldown: 10"]
        BATCH["Batch Size<br/>batch_size: 128"]
    end
    
    subgraph "Training Strategy"
        FREEZE["FreezeUnfreeze Callback<br/>module: encoder<br/>unfreeze_at_epoch: 20<br/>unfreeze_lr_factor: 10.0"]
        EPOCHS["Max Epochs: 100"]
        STRATEGY["DDPStrategy<br/>find_unused_parameters: true"]
    end
    
    subgraph "Data Configuration"
        TRAIN["Train Split<br/>group: sample_100K<br/>tag: train<br/>num_samples: 10000"]
        VAL["Val Split<br/>group: sample_100K<br/>tag: val"]
    end
    
    MODULE --> LR
    MODULE --> PLATEAU
    MODULE --> BATCH
    
    FREEZE --> MODULE
    EPOCHS --> MODULE
    STRATEGY --> MODULE
    
    TRAIN --> MODULE
    VAL --> MODULE
```

**Diagram: Training Configuration Components**

**Sources:** [olmoearth_run_data/mangrove/model.yaml:35-40](), [olmoearth_run_data/mangrove/model.yaml:249](), [olmoearth_run_data/mangrove/model.yaml:379-391]()

### FreezeUnfreeze Strategy

The training uses a two-phase approach:

**Phase 1 (Epochs 1-19)**: The encoder is frozen, only the decoder is trained with learning rate 0.0001.

**Phase 2 (Epochs 20-100)**: The encoder is unfrozen with a learning rate boost of 10x (0.001), while the decoder continues with its original learning rate.

This strategy enables transfer learning by initially adapting only the task-specific decoder, then fine-tuning the entire model.

**Sources:** [olmoearth_run_data/mangrove/model.yaml:379-386]()

### Data Transforms

The training pipeline applies these transforms:

1. **Pad**: Centers the input to ensure proper patch alignment
   - `size: 2` (matches patch size)
   - `mode: center`
   - Applied to `sentinel2_l2a`, classification targets, and valid mask

2. **OlmoEarthNormalize**: Normalizes Sentinel-2 bands using model-specific statistics
   - `std_multiplier: 2.0`
   - Applied to all 12 bands

**Sources:** [olmoearth_run_data/mangrove/model.yaml:260-286]()

## Evaluation Metrics

The model tracks multiple metrics during training and validation:

### Primary Metrics

- **Overall Accuracy**: Micro-averaged accuracy across all classes (97.6% on validation set)
- **Validation Loss**: Monitored for model checkpointing

**Sources:** [olmoearth_run_data/mangrove/model.yaml:139](), [docs/mangrove.md:20]()

### Per-Class Metrics

The model computes precision and recall for each class:

| Metric | Class | Configuration |
|--------|-------|---------------|
| `mangrove_precision` | Class 1 (Mangrove) | MulticlassPrecision, class_idx: 1 |
| `mangrove_recall` | Class 1 (Mangrove) | MulticlassRecall, class_idx: 1 |
| `water_precision` | Class 2 (Water) | MulticlassPrecision, class_idx: 2 |
| `water_recall` | Class 2 (Water) | MulticlassRecall, class_idx: 2 |
| `other_precision` | Class 3 (Other) | MulticlassPrecision, class_idx: 3 |
| `other_recall` | Class 3 (Other) | MulticlassRecall, class_idx: 3 |

All metrics use:
- `num_classes: 4`
- `top_k: 1`
- `average: null` (per-class outputs)
- `multidim_average: global`
- `zero_division: 0`

**Sources:** [olmoearth_run_data/mangrove/model.yaml:148-238]()

## Training Data

### Data Source

The model is trained on point annotations from [Global Mangrove Watch](https://www.mangrovealliance.org/global-mangrove-watch), available at https://zenodo.org/records/17394267 under the CC BY 4.0 license.

Each training sample specifies:
- Longitude and latitude coordinates
- Start and end time (1 year apart)
- Class label (mangrove, water, or other)

**Sources:** [docs/mangrove.md:23-28]()

### Data Splitting

The dataset uses a hash-based spatial splitting strategy:

- **Train Split**: 87.5% of samples (tag: `train`)
- **Validation Split**: 12.5% of samples (tag: `val`)

The splitting is performed at the 2×2 pixel grid cell level to ensure spatial independence between training and validation sets.

**Sources:** [docs/mangrove.md:30-31]()

### Dataset Groups

The configuration references a `sample_100K` group with 10,000 samples used during training. This suggests the full dataset contains 100,000+ samples with a subset used for training experiments.

**Sources:** [olmoearth_run_data/mangrove/model.yaml:290-303]()

## Inference Configuration

### Partitioning Strategy

The inference pipeline uses a two-level hierarchical partitioning:

```mermaid
graph TB
    subgraph "Request Geometry"
        INPUT["prediction_request_geometry.geojson<br/>Polygon coordinates<br/>oe_start_time<br/>oe_end_time"]
    end
    
    subgraph "Coarse Partitioning"
        PART1["GridPartitioner<br/>partition_request_geometry<br/>grid_size: 0.1 degrees"]
        PROJ1["Output Projection<br/>EPSG:3857<br/>x_resolution: 10m<br/>y_resolution: -10m<br/>use_utm: true"]
    end
    
    subgraph "Fine Partitioning"
        PART2["GridPartitioner<br/>prepare_window_geometries<br/>grid_size: 32 pixels"]
        PROJ2["Output Projection<br/>EPSG:3857<br/>x_resolution: 10m<br/>y_resolution: -10m<br/>use_utm: true"]
    end
    
    subgraph "Processing Windows"
        WIN1["Window 1<br/>32×32 pixels<br/>320m × 320m"]
        WIN2["Window 2<br/>32×32 pixels"]
        WINDOTS["..."]
        WINN["Window N"]
    end
    
    INPUT --> PART1
    PART1 --> PROJ1
    PROJ1 --> PART2
    PART2 --> PROJ2
    PROJ2 --> WIN1
    PROJ2 --> WIN2
    PROJ2 --> WINDOTS
    PROJ2 --> WINN
```

**Diagram: Hierarchical Partitioning for Inference**

**Level 1 - Coarse Grid**: Divides the request geometry into tiles of 0.1 degrees (~11 km at the equator).

**Level 2 - Fine Grid**: Each coarse tile is subdivided into 32×32 pixel windows (320m × 320m at 10m resolution).

Both levels use UTM projection when appropriate for accurate distance measurements.

**Sources:** [olmoearth_run_data/mangrove/olmoearth_run.yaml:1-24]()

### Post-processing Pipeline

The inference results are aggregated through three stages:

| Stage | Post-processor | Description |
|-------|----------------|-------------|
| `process_window` | `NoopRaster` | No processing at window level |
| `process_partition` | `CombineGeotiff` | Merge all windows in a partition |
| `process_dataset` | `CombineGeotiff` | Merge all partitions into final output |

**Sources:** [olmoearth_run_data/mangrove/olmoearth_run.yaml:26-34]()

### Output Classification

The final GeoTIFF output contains classification values with associated labels and colors:

| Value | Label | RGB Color | Description |
|-------|-------|-----------|-------------|
| 1 | mangrove | [148, 235, 99] | Mangrove vegetation |
| 2 | water | [99, 216, 235] | Water bodies |
| 3 | other | [235, 169, 99, 200] | Other land cover types |

The `inference_results_config` section defines these mappings for visualization in GIS tools and OlmoEarth Studio.

**Sources:** [olmoearth_run_data/mangrove/olmoearth_run.yaml:37-51]()

### Temporal Alignment

For inference, the `oe_start_time` in the prediction request geometry should be set to 12 months prior to the target classification date. This ensures the model receives the same temporal context as during training (12 timesteps spanning one year centered on the target date).

**Sources:** [docs/mangrove.md:35-36]()

## Model Access and Resources

The following resources are available for the mangrove extent model:

| Resource | Location | Description |
|----------|----------|-------------|
| Model Checkpoint | https://huggingface.co/allenai/OlmoEarth-v1-FT-Mangrove-Base/resolve/main/model.ckpt | Fine-tuned weights |
| Annotation GeoJSONs | https://huggingface.co/allenai/olmoearth_projects_mangrove/blob/main/annotation_features.geojson | Training point locations |
| rslearn Dataset | https://huggingface.co/allenai/olmoearth_projects_mangrove/resolve/main/mangrove.tar | Complete training dataset |
| Model Configuration | [olmoearth_run_data/mangrove/model.yaml]() | Training configuration |
| Dataset Configuration | [olmoearth_run_data/mangrove/dataset.json]() | Data source specification |
| Inference Configuration | [olmoearth_run_data/mangrove/olmoearth_run.yaml]() | Runtime parameters |

**Sources:** [docs/mangrove.md:8-10]()

## Code Entity Reference

Key classes and modules used in the mangrove model:

```mermaid
graph LR
    subgraph "rslearn.models"
        OLMOEARTH["OlmoEarth"]
        DECODER["SegmentationPoolingDecoder"]
        MULTITASK["MultiTaskModel"]
    end
    
    subgraph "rslearn.train"
        MODULE["RslearnLightningModule"]
        DATAMODULE["RslearnDataModule"]
        SEGTASK["SegmentationTask"]
        SEGHEAD["SegmentationHead"]
        FREEZE["FreezeUnfreeze"]
    end
    
    subgraph "rslearn.data_sources"
        S2SOURCE["Sentinel2"]
    end
    
    subgraph "rslearn.train.transforms"
        PAD_TRANSFORM["Pad"]
        NORM_TRANSFORM["OlmoEarthNormalize"]
    end
    
    subgraph "olmoearth_run"
        GRIDPART["GridPartitioner"]
        COMBINE["CombineGeotiff"]
        NOOP["NoopRaster"]
    end
    
    OLMOEARTH --> MULTITASK
    DECODER --> MULTITASK
    SEGHEAD --> MULTITASK
    MULTITASK --> MODULE
    SEGTASK --> DATAMODULE
    S2SOURCE --> DATAMODULE
    PAD_TRANSFORM --> DATAMODULE
    NORM_TRANSFORM --> DATAMODULE
    FREEZE --> MODULE
    GRIDPART --> OLMOEARTH
    COMBINE --> OLMOEARTH
    NOOP --> OLMOEARTH
```

**Diagram: Code Entity Relationships for Mangrove Model**

**Sources:** [olmoearth_run_data/mangrove/model.yaml:1-394](), [olmoearth_run_data/mangrove/dataset.json:1-57](), [olmoearth_run_data/mangrove/olmoearth_run.yaml:1-52]()

---

# Page: Ecosystem Type Mapping Model

# Ecosystem Type Mapping Model

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/ecosystem_type_mapping.md](docs/ecosystem_type_mapping.md)
- [olmoearth_run_data/ecosystem_type_mapping/model.yaml](olmoearth_run_data/ecosystem_type_mapping/model.yaml)
- [olmoearth_run_data/ecosystem_type_mapping/olmoearth_run.yaml](olmoearth_run_data/ecosystem_type_mapping/olmoearth_run.yaml)
- [olmoearth_run_data/ecosystem_type_mapping/prediction_request_geometry.geojson](olmoearth_run_data/ecosystem_type_mapping/prediction_request_geometry.geojson)
- [olmoearth_run_data/lfmc/model.yaml](olmoearth_run_data/lfmc/model.yaml)
- [olmoearth_run_data/lfmc/olmoearth_run.yaml](olmoearth_run_data/lfmc/olmoearth_run.yaml)
- [olmoearth_run_data/mozambique_lulc/dataset.json](olmoearth_run_data/mozambique_lulc/dataset.json)
- [olmoearth_run_data/mozambique_lulc/model.yaml](olmoearth_run_data/mozambique_lulc/model.yaml)
- [olmoearth_run_data/mozambique_lulc/olmoearth_run.yaml](olmoearth_run_data/mozambique_lulc/olmoearth_run.yaml)

</details>



This document describes the Ecosystem Type Mapping Model (OlmoEarth-v1-FT-EcosystemTypeMapping-Base), a fine-tuned model for classifying 60 different ecosystem types in the North Africa region. The model achieves 64.8% accuracy on its test set and uses the IUCN Global Ecosystem Typology classification scheme.

For information about other land cover models in this repository, see [Mozambique LULC Models](#6.1), [Nandi Crop Classification Model](#6.6), or [AWF Land Cover Model](#6.7). For the general training process, see [Fine-tuning Process](#5.3). For running inference, see [olmoearth_run Pipeline](#7.1).

**Sources:** [docs/ecosystem_type_mapping.md:1-37]()

---

## Model Overview

The Ecosystem Type Mapping Model is a segmentation model that classifies each 32x32 pixel crop of Sentinel-2 imagery into one of 60 ecosystem categories based on the [IUCN Global Ecosystem Typology](https://global-ecosystems.org/page/typology). The model processes six timesteps of Sentinel-2 L2A satellite imagery spanning 30-day mosaics over a 270-day period.

### Key Characteristics

| Property | Value |
|----------|-------|
| **Base Model** | OlmoEarth-v1-Base |
| **Task Type** | Multi-class segmentation |
| **Number of Classes** | 110 (60 active ecosystem types + unknown) |
| **Input Data** | Sentinel-2 L2A, 12 bands, 6 timesteps |
| **Temporal Range** | 270 days (6 × 30-day periods) |
| **Spatial Resolution** | 10m |
| **Processing Patch Size** | 32×32 pixels |
| **Test Accuracy** | 64.8% |
| **Geographic Region** | North Africa |
| **Model Checkpoint** | [HuggingFace](https://huggingface.co/allenai/OlmoEarth-v1-FT-EcosystemTypeMapping-Base/blob/main/model.ckpt) |

**Sources:** [docs/ecosystem_type_mapping.md:13-22](), [olmoearth_run_data/ecosystem_type_mapping/model.yaml:54-59]()

---

## Model Architecture

The architecture follows the standard fine-tuning pattern with an OlmoEarth encoder and a simple segmentation decoder.

```mermaid
graph TB
    subgraph Input["Input Data"]
        S2["Sentinel-2 L2A<br/>6 timesteps × 12 bands<br/>32×32 pixels"]
    end
    
    subgraph Preprocessing["Preprocessing"]
        NORM["OlmoEarthNormalize<br/>Band normalization"]
    end
    
    subgraph Encoder["OlmoEarth Encoder"]
        PRETRAIN["OlmoEarth<br/>model_id: OLMOEARTH_V1_BASE<br/>patch_size: 4<br/>output: 768 channels"]
    end
    
    subgraph Decoder["Segmentation Decoder"]
        UPSAMPLE["Upsample<br/>scale_factor: 4<br/>768 channels"]
        CONV["Conv<br/>768 → 110 channels<br/>kernel_size: 1"]
        SEG_HEAD["SegmentationHead<br/>110 classes"]
    end
    
    subgraph Output["Output"]
        PRED["Class Predictions<br/>110 classes<br/>nodata_value: 54<br/>32×32 pixels"]
    end
    
    S2 --> NORM
    NORM --> PRETRAIN
    PRETRAIN --> UPSAMPLE
    UPSAMPLE --> CONV
    CONV --> SEG_HEAD
    SEG_HEAD --> PRED
```

### Architecture Components

**Encoder Configuration** [olmoearth_run_data/ecosystem_type_mapping/model.yaml:7-11]()
- Class: `rslearn.models.olmoearth_pretrain.model.OlmoEarth`
- Model ID: `OLMOEARTH_V1_BASE` (pre-trained foundation model)
- Patch size: 4 (downsampling factor)
- Output: 768-dimensional feature representations

**Decoder Configuration** [olmoearth_run_data/ecosystem_type_mapping/model.yaml:12-23]()
- **Upsample Layer**: Upsamples by 4× to restore original resolution
- **Convolution Layer**: 1×1 convolution from 768 to 110 channels
- **Segmentation Head**: `rslearn.train.tasks.segmentation.SegmentationHead`

**Task Configuration** [olmoearth_run_data/ecosystem_type_mapping/model.yaml:53-59]()
- Class: `rslearn.train.tasks.segmentation.SegmentationTask`
- Number of classes: 110 (though only 60 are actively used)
- Nodata value: 54 (UNKNOWN class)
- Metric: Micro-averaged accuracy

**Sources:** [olmoearth_run_data/ecosystem_type_mapping/model.yaml:1-111]()

---

## Training Configuration

### Input Data Specification

The model ingests six timesteps of Sentinel-2 L2A imagery, each representing a 30-day mosaic. The temporal sequence spans 270 days (6 × 30-day periods), with an additional 90-day buffer for periods with insufficient coverage.

**Sentinel-2 Configuration** [olmoearth_run_data/ecosystem_type_mapping/model.yaml:40-46]()
```yaml
sentinel2_l2a:
  data_type: "raster"
  layers: ["sentinel2", "sentinel2.1", "sentinel2.2", 
           "sentinel2.3", "sentinel2.4", "sentinel2.5"]
  bands: ["B02", "B03", "B04", "B08", "B05", "B06", 
          "B07", "B8A", "B11", "B12", "B01", "B09"]
  dtype: FLOAT32
```

| Band | Wavelength | Resolution | Purpose |
|------|------------|------------|---------|
| B01 | 443 nm (Coastal aerosol) | 60m | Atmospheric correction |
| B02 | 490 nm (Blue) | 10m | Water bodies, vegetation |
| B03 | 560 nm (Green) | 10m | Vegetation health |
| B04 | 665 nm (Red) | 10m | Chlorophyll absorption |
| B05 | 705 nm (Red Edge 1) | 20m | Vegetation stress |
| B06 | 740 nm (Red Edge 2) | 20m | Vegetation stress |
| B07 | 783 nm (Red Edge 3) | 20m | Vegetation stress |
| B08 | 842 nm (NIR) | 10m | Biomass content |
| B8A | 865 nm (Narrow NIR) | 20m | Water vapor |
| B09 | 945 nm (Water vapor) | 60m | Atmospheric correction |
| B11 | 1610 nm (SWIR 1) | 20m | Moisture content |
| B12 | 2190 nm (SWIR 2) | 20m | Moisture content |

**Sources:** [olmoearth_run_data/ecosystem_type_mapping/model.yaml:40-46](), [docs/ecosystem_type_mapping.md:15-17]()

### Training Hyperparameters

```mermaid
graph LR
    subgraph Optimizer["Optimizer Configuration"]
        OPT["AdamW<br/>lr: 0.0001"]
    end
    
    subgraph Scheduler["Learning Rate Scheduler"]
        PLAT["PlateauScheduler<br/>factor: 0.2<br/>patience: 2<br/>min_lr: 0<br/>cooldown: 10"]
    end
    
    subgraph Training["Training Settings"]
        BATCH["Batch Size: 32<br/>Patch Size: 32<br/>Max Epochs: 100"]
    end
    
    subgraph Callbacks["Training Callbacks"]
        FREEZE["FreezeUnfreeze<br/>unfreeze_at_epoch: 10<br/>encoder freeze strategy"]
        CKPT["ModelCheckpoint<br/>monitor: val_accuracy<br/>mode: max<br/>save_top_k: 1"]
        LR_MON["LearningRateMonitor<br/>logging_interval: epoch"]
    end
    
    OPT --> PLAT
    PLAT --> Training
    Training --> Callbacks
```

**Optimizer Configuration** [olmoearth_run_data/ecosystem_type_mapping/model.yaml:31-34]()
- Class: `rslearn.train.optimizer.AdamW`
- Learning rate: 0.0001

**Scheduler Configuration** [olmoearth_run_data/ecosystem_type_mapping/model.yaml:24-30]()
- Class: `rslearn.train.scheduler.PlateauScheduler`
- Factor: 0.2 (reduces LR by 80% on plateau)
- Patience: 2 epochs
- Cooldown: 10 epochs

**Freeze/Unfreeze Strategy** [olmoearth_run_data/ecosystem_type_mapping/model.yaml:103-106]()
- Encoder frozen for first 10 epochs
- Unfreezes at epoch 10 to fine-tune all layers
- Module selector: `["model", "encoder", 0]`

**Data Configuration** [olmoearth_run_data/ecosystem_type_mapping/model.yaml:60-80]()
- Batch size: 32
- Patch size: 32×32 pixels
- Training group: `["north_africa"]`
- Train/val/test splits by `split` tag

**Sources:** [olmoearth_run_data/ecosystem_type_mapping/model.yaml:24-111]()

---

## Training Data

The model is trained on expert-annotated ecosystem type data from the [Global Ecosystem Atlas](https://globalecosystemsatlas.org/). The dataset uses the IUCN Global Ecosystem Typology classification scheme and covers the North Africa region.

### Data Preparation

**Window Preparation** [olmoearth_run_data/ecosystem_type_mapping/olmoearth_run.yaml:218-237]()
- Class: `olmoearth_run.runner.tools.labeled_window_preparers.point_to_raster_window_preparer.PointToRasterWindowPreparer`
- Window buffer: 31 pixels
- Window resolution: 10.0 meters
- Data type: FLOAT32
- Nodata value: 54 (UNKNOWN class)

**Data Splitting** [olmoearth_run_data/ecosystem_type_mapping/olmoearth_run.yaml:219-225]()
- Class: `olmoearth_run.runner.tools.data_splitters.spatial_data_splitter.SpatialDataSplitter`
- Grid size: 10.0 degrees
- Train proportion: 0.8 (80%)
- Validation proportion: 0.1 (10%)
- Test proportion: 0.1 (10%)

The dataset will be publicly released by Global Ecosystem Atlas in 2026.

**Sources:** [docs/ecosystem_type_mapping.md:24-27](), [olmoearth_run_data/ecosystem_type_mapping/olmoearth_run.yaml:218-237]()

---

## Ecosystem Classification Scheme

The model classifies 60 active ecosystem types following the IUCN Global Ecosystem Typology. The output has 110 classes total, with class 54 designated as UNKNOWN for missing or ambiguous data.

### Major Ecosystem Realms

```mermaid
graph TB
    subgraph Terrestrial["Terrestrial Ecosystems (T)"]
        T1["T.1: Tropical/Subtropical<br/>Forests (3 types)"]
        T2["T.2: Temperate/Boreal<br/>Forests (2 types)"]
        T3["T.3: Shrublands (3 types)"]
        T4["T.4: Savannas/Grasslands<br/>(4 types)"]
        T5["T.5: Deserts/Semi-deserts<br/>(3 types)"]
        T6["T.6: Polar/Alpine (2 types)"]
        T7["T.7: Intensive Land Use<br/>(5 types)"]
    end
    
    subgraph Freshwater["Freshwater Ecosystems (F, TF)"]
        TF["TF.1: Palustrine Wetlands<br/>(3 types)"]
        F1["F.1: Rivers/Streams<br/>(4 types)"]
        F2["F.2: Lakes (8 types)"]
        F3["F.3: Artificial Freshwater<br/>(4 types)"]
    end
    
    subgraph Marine["Marine/Coastal Ecosystems (M, MFT, MT, FM)"]
        MFT["MFT.1: Coastal Wetlands<br/>(2 types)"]
        MT1["MT.1: Rocky Shorelines<br/>(4 types)"]
        MT2["MT.2: Coastal Vegetation<br/>(2 types)"]
        MT3["MT.3: Artificial Shorelines<br/>(1 type)"]
        FM["FM.1: Estuaries/Lagoons<br/>(2 types)"]
        M1["M.1: Marine Benthic<br/>(4 types)"]
        M4["M.4: Artificial Marine<br/>(1 type)"]
        OCEAN["Open Ocean"]
    end
    
    subgraph Unknown["Special Classes"]
        UNK["UNKNOWN (class 54)<br/>nodata_value"]
    end
```

### Ecosystem Type Mapping Table

The following table shows selected ecosystem types from each realm. The complete mapping with all 60 types and their color schemes is defined in [olmoearth_run_data/ecosystem_type_mapping/olmoearth_run.yaml:1-187]().

| Class ID | Ecosystem Type | IUCN Code | Realm |
|----------|----------------|-----------|-------|
| 0 | Tropical/Subtropical Lowland Rainforests | T.1.1 | Terrestrial |
| 1 | Tropical/Subtropical Dry Forests and Thickets | T.1.2 | Terrestrial |
| 6 | Trophic Savannas | T.4.1 | Terrestrial |
| 7 | Pyric Tussock Savannas | T.4.2 | Terrestrial |
| 11 | Hyper-arid Deserts | T.5.5 | Terrestrial |
| 13 | Annual Croplands | T.7.1 | Terrestrial |
| 16 | Urban and Industrial Ecosystems | T.7.4 | Terrestrial |
| 18 | Permanent Marshes | TF.1.3 | Freshwater |
| 21 | Permanent Lowland Rivers | F.1.2 | Freshwater |
| 25 | Large Permanent Freshwater Lakes | F.2.1 | Freshwater |
| 36 | Intertidal Forests and Shrublands | MFT.1.2 | Marine/Coastal |
| 38 | Rocky Shorelines | MT.1.1 | Marine/Coastal |
| 51 | Seagrass Meadows | M.1.1 | Marine |
| 52 | Photic Coral Reefs | M.1.3 | Marine |
| 54 | **UNKNOWN** | — | Special (nodata) |

**Sources:** [olmoearth_run_data/ecosystem_type_mapping/olmoearth_run.yaml:1-187]()

---

## Inference Configuration

### Partitioning Strategy

The inference pipeline uses hierarchical partitioning to efficiently process large geographic areas.

```mermaid
graph TB
    subgraph Input["Input Geometry"]
        GEOJSON["prediction_request_geometry.geojson<br/>Polygon + Time Range"]
    end
    
    subgraph Coarse["Coarse Partitioning"]
        COARSE_PART["GridPartitioner<br/>grid_size: 0.1 degrees<br/>partition_request_geometry"]
    end
    
    subgraph Fine["Fine Partitioning"]
        FINE_PART["GridPartitioner<br/>grid_size: 64 pixels<br/>prepare_window_geometries"]
        PROJ["Projection:<br/>EPSG:3857<br/>x_resolution: 10m<br/>y_resolution: -10m<br/>use_utm: true"]
    end
    
    subgraph Processing["Window Processing"]
        QUERY["Query Sentinel-2 L2A<br/>6 timesteps × 30 days"]
        INFERENCE["Model Inference<br/>32×32 patch size"]
        NOOP["NoopRaster<br/>process_window<br/>No window-level PP"]
    end
    
    subgraph Aggregation["Result Aggregation"]
        PART_AGG["CombineGeotiff<br/>process_partition<br/>Merge partition tiles"]
        DATASET_AGG["CombineGeotiff<br/>process_dataset<br/>Final output assembly"]
    end
    
    GEOJSON --> COARSE_PART
    COARSE_PART --> FINE_PART
    FINE_PART --> PROJ
    PROJ --> QUERY
    QUERY --> INFERENCE
    INFERENCE --> NOOP
    NOOP --> PART_AGG
    PART_AGG --> DATASET_AGG
```

**Coarse Partitioning** [olmoearth_run_data/ecosystem_type_mapping/olmoearth_run.yaml:190-194]()
- Strategy: `partition_request_geometry`
- Class: `olmoearth_run.runner.tools.partitioners.grid_partitioner.GridPartitioner`
- Grid size: 0.1 degrees (~11 km at equator)
- Purpose: Divide large regions into manageable geographic tiles

**Fine Partitioning** [olmoearth_run_data/ecosystem_type_mapping/olmoearth_run.yaml:196-206]()
- Strategy: `prepare_window_geometries`
- Class: `olmoearth_run.runner.tools.partitioners.grid_partitioner.GridPartitioner`
- Grid size: 64 pixels (640m × 640m at 10m resolution)
- Output projection: EPSG:3857 (Web Mercator)
- Resolution: 10m × 10m
- UTM conversion: Enabled for more accurate local projections

**Sources:** [olmoearth_run_data/ecosystem_type_mapping/olmoearth_run.yaml:190-216]()

### Post-processing Pipeline

```mermaid
graph LR
    subgraph Window["Window Level"]
        W_IN["Individual Window<br/>Predictions"]
        W_PP["NoopRaster<br/>No processing"]
        W_OUT["Raw Predictions"]
    end
    
    subgraph Partition["Partition Level"]
        P_IN["All Windows in<br/>Partition"]
        P_PP["CombineGeotiff<br/>Merge windows<br/>into partition tile"]
        P_OUT["Partition GeoTIFF"]
    end
    
    subgraph Dataset["Dataset Level"]
        D_IN["All Partition<br/>Tiles"]
        D_PP["CombineGeotiff<br/>Merge partitions<br/>into final output"]
        D_OUT["Final GeoTIFF<br/>110 classes<br/>nodata: 54"]
    end
    
    W_IN --> W_PP
    W_PP --> W_OUT
    W_OUT --> P_IN
    P_IN --> P_PP
    P_PP --> P_OUT
    P_OUT --> D_IN
    D_IN --> D_PP
    D_PP --> D_OUT
```

**Window Processing** [olmoearth_run_data/ecosystem_type_mapping/olmoearth_run.yaml:215-216]()
- Class: `olmoearth_run.runner.tools.postprocessors.noop_raster.NoopRaster`
- No window-level post-processing applied

**Partition Processing** [olmoearth_run_data/ecosystem_type_mapping/olmoearth_run.yaml:212-213]()
- Class: `olmoearth_run.runner.tools.postprocessors.combine_geotiff.CombineGeotiff`
- Merges all windows within a partition into a single GeoTIFF

**Dataset Processing** [olmoearth_run_data/ecosystem_type_mapping/olmoearth_run.yaml:209-210]()
- Class: `olmoearth_run.runner.tools.postprocessors.combine_geotiff.CombineGeotiff`
- Merges all partition tiles into the final output raster

**Sources:** [olmoearth_run_data/ecosystem_type_mapping/olmoearth_run.yaml:208-216]()

---

## Temporal Configuration

The model requires six timesteps of Sentinel-2 imagery spanning approximately 270 days. The inference system automatically handles temporal mosaic generation.

### Temporal Mosaic Strategy

**Start Time Usage** [docs/ecosystem_type_mapping.md:31-36]()
- The `oe_start_time` in the prediction request geometry defines the beginning of the 180-day primary time range
- Six 30-day periods (180 days total) are created from this start time
- An additional 90-day buffer precedes the start time for periods with insufficient coverage
- Total temporal range: 270 days (90-day buffer + 180-day primary)

**End Time Handling**
- The `oe_end_time` field is not used by the model
- Can be set to any value, typically 180 days after `oe_start_time`

**Example Time Configuration** [olmoearth_run_data/ecosystem_type_mapping/prediction_request_geometry.geojson:32-33]()
```json
{
  "properties": {
    "oe_start_time": "2025-01-01 08:00:00+00:00",
    "oe_end_time": "2025-08-05 07:00:00+00:00"
  }
}
```

This configuration results in:
- Buffer period: 2024-10-03 to 2025-01-01 (90 days)
- Primary period: 2025-01-01 to 2025-06-30 (180 days)
- Six 30-day mosaics centered on: Jan 16, Feb 15, Mar 17, Apr 16, May 16, Jun 15

**Sources:** [docs/ecosystem_type_mapping.md:31-36](), [olmoearth_run_data/ecosystem_type_mapping/prediction_request_geometry.geojson:1-39]()

---

## Output Format

The model produces classification rasters with the following characteristics:

### Output Specification

```mermaid
graph LR
    subgraph Predictions["Model Predictions"]
        LOGITS["Logits<br/>110 channels"]
        ARGMAX["Argmax<br/>Class selection"]
        CLASS["Class IDs<br/>0-109"]
    end
    
    subgraph Metadata["Classification Metadata"]
        PROP["property_name: class<br/>band_index: 1"]
        VALUES["allowed_values<br/>60 ecosystem types<br/>+ UNKNOWN (54)"]
        COLORS["Color scheme<br/>IUCN typology colors"]
    end
    
    subgraph Output["GeoTIFF Output"]
        RASTER["Classification Raster<br/>data_type: RASTER<br/>10m resolution<br/>EPSG:3857 or UTM"]
    end
    
    LOGITS --> ARGMAX
    ARGMAX --> CLASS
    CLASS --> RASTER
    PROP --> RASTER
    VALUES --> RASTER
    COLORS --> RASTER
```

**Classification Field Configuration** [olmoearth_run_data/ecosystem_type_mapping/olmoearth_run.yaml:1-8]()
```yaml
inference_results_config:
  data_type: RASTER
  classification_fields:
    - property_name: class
      band_index: 1
      allowed_values: [60 ecosystem types with labels and colors]
```

| Property | Value |
|----------|-------|
| **Data Type** | RASTER |
| **Property Name** | `class` |
| **Band Index** | 1 (single-band classification) |
| **Value Range** | 0-59 (active classes) + 54 (UNKNOWN) |
| **Nodata Value** | 54 (UNKNOWN class) |
| **Spatial Resolution** | 10 meters |
| **Coordinate System** | EPSG:3857 or UTM (use_utm: true) |

**Sources:** [olmoearth_run_data/ecosystem_type_mapping/olmoearth_run.yaml:1-187]()

---

## Example Usage

### Prediction Request Geometry

To run inference, create a GeoJSON file with the area of interest and time range:

**Example** [olmoearth_run_data/ecosystem_type_mapping/prediction_request_geometry.geojson:1-39]()
```json
{
  "features": [
    {
      "geometry": {
        "coordinates": [[
          [15.030232213572674, 28.856258648812116],
          [15.030232213572674, 28.846640094401664],
          [15.041325166568527, 28.846640094401664],
          [15.041325166568527, 28.856258648812116],
          [15.030232213572674, 28.856258648812116]
        ]],
        "type": "Polygon"
      },
      "properties": {
        "oe_start_time": "2025-01-01 08:00:00+00:00",
        "oe_end_time": "2025-08-05 07:00:00+00:00"
      },
      "type": "Feature"
    }
  ],
  "type": "FeatureCollection"
}
```

This example covers a small region in Libya (~1.2 km × 1.2 km) with a 7-month time range starting January 2025.

**Sources:** [olmoearth_run_data/ecosystem_type_mapping/prediction_request_geometry.geojson:1-39]()

### Running Inference

For detailed instructions on running inference with this model, see the [olmoearth_run Pipeline](#7.1) documentation and the main README.

The general workflow:
1. Create `prediction_request_geometry.geojson` with your area and time range
2. Load model checkpoint: `OlmoEarth-v1-FT-EcosystemTypeMapping-Base`
3. Configure using `olmoearth_run_data/ecosystem_type_mapping/model.yaml`
4. Execute inference pipeline with partitioning strategy from `olmoearth_run.yaml`
5. Retrieve classified GeoTIFF with ecosystem type predictions

**Sources:** [docs/ecosystem_type_mapping.md:29-36]()

---

## Model Limitations

### Geographic Scope
- **Training Region:** Model is specifically trained for North Africa
- **Generalization:** Performance in other regions may vary significantly
- **Ecosystem Coverage:** The 60 ecosystem types may not cover all global ecosystems

### Temporal Constraints
- **Temporal Range:** Requires 270 days of observation (including 90-day buffer)
- **Cloud Coverage:** Performance degrades in regions with persistent cloud cover
- **Seasonal Variation:** Single time range may not capture full ecosystem dynamics

### Classification Challenges
- **Test Accuracy:** 64.8% indicates significant classification uncertainty
- **Class Imbalance:** Some ecosystem types may be underrepresented in training data
- **Transition Zones:** Ecosystem boundaries and ecotones may be misclassified
- **Mixed Pixels:** 10m resolution may contain multiple ecosystem types per pixel

### Data Dependencies
- **Sentinel-2 Availability:** Requires consistent Sentinel-2 coverage
- **Data Source:** Training data release pending (2026)
- **IUCN Schema:** Classification scheme may evolve with IUCN updates

**Sources:** [docs/ecosystem_type_mapping.md:22-27]()

---

# Page: Nandi Crop Classification Model

# Nandi Crop Classification Model

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/awf.md](docs/awf.md)
- [docs/nandi.md](docs/nandi.md)
- [olmoearth_run_data/awf/model.yaml](olmoearth_run_data/awf/model.yaml)
- [olmoearth_run_data/awf/olmoearth_run.yaml](olmoearth_run_data/awf/olmoearth_run.yaml)
- [olmoearth_run_data/nandi/model.yaml](olmoearth_run_data/nandi/model.yaml)
- [olmoearth_run_data/nandi/olmoearth_run.yaml](olmoearth_run_data/nandi/olmoearth_run.yaml)
- [olmoearth_run_data/nandi/prediction_request_geometry.geojson](olmoearth_run_data/nandi/prediction_request_geometry.geojson)

</details>



## Purpose and Scope

This page documents OlmoEarth-v1-FT-Nandi-Base, a fine-tuned model for predicting crop and land cover types in Nandi County, Kenya. The model classifies 10 categories including coffee, maize, sugarcane, tea, vegetables, legumes, grassland, trees, water, and built-up areas using Sentinel-2 L2A satellite imagery. The model achieves 87.3% overall accuracy on the validation set.

For information about the general training pipeline, see [Model Training](#5). For inference deployment details, see [Inference and Deployment](#7). For other regional crop classification models, see [Mozambique LULC Models](#6.1) and [AWF Land Cover Model](#6.7).

**Sources:** [docs/nandi.md:1-48]()

## Model Overview

OlmoEarth-v1-FT-Nandi-Base performs per-pixel segmentation to classify crop and land cover types. The model processes twelve timesteps of Sentinel-2 L2A imagery, with one mosaic per 30-day period covering a full year (2022-09 to 2023-09). The model operates on 16×16 pixel input patches and produces class predictions for every pixel within each patch.

**Key Characteristics:**

| Property | Value |
|----------|-------|
| Base Model | OlmoEarth-v1-Base |
| Geographic Region | Nandi County, Kenya |
| Input Data | Sentinel-2 L2A (12 bands) |
| Temporal Coverage | 12 timesteps (30-day periods) |
| Input Patch Size | 16×16 pixels |
| Model Patch Size | 1×1 (no spatial downsampling) |
| Number of Classes | 10 land cover categories |
| Overall Accuracy | 87.3% |
| Spatial Resolution | 10m per pixel |

**Sources:** [docs/nandi.md:1-28](), [olmoearth_run_data/nandi/model.yaml:1-11]()

## Model Architecture

The Nandi model uses a segmentation architecture with the OlmoEarth encoder and a simple decoder head. Unlike other models in this repository that use patch_size 4, this model uses patch_size 1 for finer spatial resolution.

```mermaid
graph TB
    subgraph Input["Input Data"]
        S2["Sentinel-2 L2A<br/>12 timesteps × 12 bands<br/>16×16 pixels"]
    end
    
    subgraph Encoder["OlmoEarth Encoder"]
        OLMO["rslearn.models.olmoearth_pretrain.model.OlmoEarth<br/>model_id: OLMOEARTH_V1_BASE<br/>patch_size: 1<br/>Output: 768 channels"]
    end
    
    subgraph Decoder["Segmentation Decoder"]
        UPSAMPLE["rslearn.models.upsample.Upsample<br/>scale_factor: 1<br/>(no upsampling)"]
        CONV["rslearn.models.conv.Conv<br/>in_channels: 768<br/>out_channels: 11<br/>kernel_size: 1"]
        SEGHEAD["rslearn.train.tasks.segmentation.SegmentationHead<br/>Applies softmax/argmax"]
    end
    
    subgraph Output["Output"]
        PRED["Per-pixel Classification<br/>16×16 pixels<br/>10 valid classes + nodata"]
    end
    
    S2 --> OLMO
    OLMO --> UPSAMPLE
    UPSAMPLE --> CONV
    CONV --> SEGHEAD
    SEGHEAD --> PRED
```

**Architecture Details:**

- **Encoder:** `OlmoEarth` with `patch_size: 1` preserves full spatial resolution throughout the encoder, producing 768-channel feature maps at the original spatial dimensions
- **Decoder:** A minimal decoder consisting of an identity upsampler (scale_factor 1), a 1×1 convolution to map 768 channels to 11 output channels (10 classes + 1 nodata), and a `SegmentationHead` that handles softmax/argmax operations
- **Output Channels:** 11 total channels where class indices 0-9 represent the 10 land cover categories and index 10 is the nodata value

**Sources:** [olmoearth_run_data/nandi/model.yaml:1-24]()

## Training Data

### Data Source and Coverage

The training data originates from ground-truth labels collected by CGIAR/IFPRI, consisting of 819 labeled polygons. To improve class coverage, additional samples were added from ESA WorldCover (for water and built-up classes) and manual annotations in OlmoEarth Studio (for tree samples to correct coffee/forest confusion).

**Class Distribution:**

| Class Index | Category | Description |
|-------------|----------|-------------|
| 0 | Coffee | Coffee plantations |
| 1 | Grassland | Grassland areas |
| 2 | Trees | Natural forest and tree cover |
| 3 | Maize | Maize crops |
| 4 | Sugarcane | Sugarcane plantations |
| 5 | Tea | Tea plantations |
| 6 | Vegetables | Vegetable crops |
| 7 | Legumes | Legume crops |
| 8 | Water | Water bodies |
| 9 | Built-up | Urban and built-up areas |
| 10 (nodata) | Invalid | No data or invalid pixels |

**Sources:** [docs/nandi.md:29-38](), [olmoearth_run_data/nandi/olmoearth_run.yaml:54-91]()

### Dataset Preparation

Training windows are generated by the window preparation pipeline, which converts point labels to raster format and applies spatial splitting:

```mermaid
graph LR
    subgraph Input["Input Labels"]
        POINTS["Point labels<br/>lon, lat, time_range, category<br/>819 polygons sampled"]
    end
    
    subgraph WindowPrep["Window Preparation"]
        P2R["PointToRasterWindowPreparer<br/>window_buffer: 31 pixels<br/>window_resolution: 10.0m<br/>nodata_value: 10"]
        GRID["SpatialDataSplitter<br/>grid_size: 128 pixels<br/>train_prop: 0.75<br/>val_prop: 0.25"]
    end
    
    subgraph Output["rslearn Dataset"]
        TRAIN["Train Split (75%)"]
        VAL["Val Split (25%)"]
    end
    
    POINTS --> P2R
    P2R --> GRID
    GRID --> TRAIN
    GRID --> VAL
```

**Window Preparation Configuration:**

- **Window Buffer:** 31 pixels added around each point location creates a 63×63 pixel window (with the point at center)
- **Resolution:** 10m per pixel matching Sentinel-2 L2A spatial resolution
- **Rasterization:** Point labels are converted to raster format with `INT32` dtype
- **Spatial Splitting:** A 128×128 pixel grid is hashed to assign windows to train (75%) or validation (25%) splits, ensuring spatial separation between splits

**Sources:** [docs/nandi.md:35-37](), [olmoearth_run_data/nandi/olmoearth_run.yaml:1-20]()

### Data Loading and Transforms

The `RslearnDataModule` handles data loading with the following configuration:

**Input Specification:**
- **sentinel2_l2a:** All 12 Sentinel-2 bands (B02, B03, B04, B08, B05, B06, B07, B8A, B11, B12, B01, B09) loaded as FLOAT32, with `load_all_item_groups: true` to load all timesteps
- **label:** Single-band category raster loaded as INT32 target

**Training Transforms (applied in sequence):**
1. `rslearn.train.transforms.pad.Pad` - Pads to size 31 pixels centered on the window
2. `rslearn.train.transforms.crop.Crop` - Crops to final 16×16 patch size
3. `rslearn.train.transforms.flip.Flip` - Random horizontal/vertical flips for augmentation
4. `rslearn.models.olmoearth_pretrain.norm.OlmoEarthNormalize` - Normalizes Sentinel-2 bands using OlmoEarth statistics

**Validation/Test Transforms:**
- Same as training but without the `Flip` augmentation

**Sources:** [olmoearth_run_data/nandi/model.yaml:31-287]()

## Training Configuration

### Optimization Settings

The model training uses the following optimization configuration defined in `RslearnLightningModule`:

| Parameter | Value | Description |
|-----------|-------|-------------|
| Learning Rate | 0.0001 | Initial learning rate |
| Plateau Scheduling | Enabled | Reduces LR on validation plateau |
| Plateau Factor | 0.2 | Multiply LR by 0.2 when plateau detected |
| Plateau Patience | 2 epochs | Wait 2 epochs before reducing LR |
| Plateau Min LR | 0 | No minimum LR threshold |
| Plateau Cooldown | 10 epochs | Wait 10 epochs after LR reduction |
| Batch Size | 4 | Training batch size |
| Max Epochs | 100 | Maximum training epochs |

**Sources:** [olmoearth_run_data/nandi/model.yaml:25-30, 246-303]()

### FreezeUnfreeze Strategy

The model uses a `FreezeUnfreeze` callback to implement progressive unfreezing of the OlmoEarth encoder:

```mermaid
graph LR
    subgraph Phase1["Phase 1: Epochs 0-19"]
        FROZEN["OlmoEarth Encoder<br/>FROZEN<br/>LR = 0.0001"]
        DEC1["Decoder<br/>TRAINABLE<br/>LR = 0.0001"]
    end
    
    subgraph Phase2["Phase 2: Epoch 20+"]
        UNFROZEN["OlmoEarth Encoder<br/>UNFROZEN<br/>LR = 0.001 (10x boost)"]
        DEC2["Decoder<br/>TRAINABLE<br/>LR = 0.0001 (unchanged)"]
    end
    
    Phase1 --> Phase2
```

**Configuration:**
- **Module Selector:** `["model", "encoder", 0]` - Targets the OlmoEarth encoder
- **Unfreeze Epoch:** 20 - Encoder unfrozen at epoch 20
- **LR Factor:** 10 - Encoder learning rate boosted 10x upon unfreezing

This strategy allows the decoder to adapt first while the encoder remains fixed, then fine-tunes the entire model with a higher encoder learning rate.

**Sources:** [olmoearth_run_data/nandi/model.yaml:321-325]()

### Task Configuration and Metrics

The model uses `SegmentationTask` with extensive per-class metrics:

**Task Configuration:**
- **Task Type:** `rslearn.train.tasks.segmentation.SegmentationTask`
- **Number of Classes:** 11 (10 valid classes + 1 nodata)
- **Zero Is Invalid:** `false` - Class 0 (coffee) is a valid class
- **Nodata Value:** 10 - Class index 10 represents invalid/nodata pixels
- **Overall Metric:** Micro-averaged accuracy across all valid pixels

**Per-Class Metrics:** For each of the 10 valid classes, the model tracks:
- **Precision:** `torchmetrics.classification.MulticlassPrecision` with `average: null` for per-class values
- **Recall:** `torchmetrics.classification.MulticlassRecall` with `average: null` for per-class values

These metrics are monitored during training via `WandbLogger` and used by `ModelCheckpoint` to save the best model based on `val_segment/accuracy`.

**Sources:** [olmoearth_run_data/nandi/model.yaml:50-242]()

## Model Performance

### Accuracy Results

The Nandi model achieves different performance levels depending on the patch size configuration:

| Window Size | Patch Size | Modalities | Accuracy (%) |
|-------------|------------|------------|--------------|
| 16×16 | 1 | Sentinel-2 | **87.3** |
| 16×16 | 1 | Sentinel-2 + Sentinel-1 | TBD |
| 16×16 | 2 | Sentinel-2 | 86.5 |
| 16×16 | 2 | Sentinel-2 + Sentinel-1 | 86.7 |
| 16×16 | 4 | Sentinel-2 | 81.9 |
| 16×16 | 4 | Sentinel-2 + Sentinel-1 | 82.2 |

**Key Findings:**
- **Patch Size 1 performs best:** The finest spatial resolution (patch_size 1) achieves the highest accuracy at 87.3%
- **Sentinel-2 only is sufficient:** Adding Sentinel-1 radar data provides minimal improvement
- **Spatial resolution matters:** Larger patch sizes (4×4) that downsample spatial features show significantly lower accuracy

The published model uses the best configuration: window size 16×16, patch size 1, Sentinel-2 only.

**Sources:** [docs/nandi.md:18-27]()

## Inference Configuration

### Partitioning Strategy

The inference pipeline uses a hierarchical two-level partitioning approach defined in `olmoearth_run.yaml`:

```mermaid
graph TB
    subgraph Input["Input Geometry"]
        GEOJSON["prediction_request_geometry.geojson<br/>Nandi County bounds<br/>2022-09-01 to 2023-09-01"]
    end
    
    subgraph CoarsePartition["Level 1: Coarse Partitioning"]
        GP1["GridPartitioner<br/>grid_size: 1.0 degrees<br/>Divides large areas"]
    end
    
    subgraph FinePartition["Level 2: Fine Partitioning"]
        GP2["GridPartitioner<br/>grid_size: 1024 pixels<br/>output_projection: EPSG:3857<br/>x_resolution: 10m<br/>y_resolution: -10m<br/>use_utm: true"]
    end
    
    subgraph Processing["Window Processing"]
        INFERENCE["Model Inference<br/>overlap_ratio: 0.25<br/>patch_size: 16"]
    end
    
    GEOJSON --> GP1
    GP1 --> GP2
    GP2 --> INFERENCE
```

**Partitioning Details:**

1. **Coarse Grid:** `partition_request_geometry` divides the input geometry into 1.0-degree tiles for parallel processing
2. **Fine Grid:** `prepare_window_geometries` subdivides each coarse tile into 1024×1024 pixel windows
3. **Projection:** Windows are projected to EPSG:3857 (Web Mercator) or UTM when `use_utm: true`, with 10m spatial resolution
4. **Overlap:** Inference uses 25% overlap between patches (4 pixels of a 16-pixel patch) to ensure smooth boundaries

**Sources:** [olmoearth_run_data/nandi/olmoearth_run.yaml:22-38](), [olmoearth_run_data/nandi/model.yaml:292-296]()

### Post-processing Configuration

After inference, results are aggregated at three levels:

```mermaid
graph TB
    subgraph WindowLevel["Window Level"]
        NOOP["NoopRaster<br/>No window-level processing"]
    end
    
    subgraph PartitionLevel["Partition Level"]
        COMBINE1["CombineGeotiff<br/>nodata_value: 10<br/>Merges all windows in partition"]
    end
    
    subgraph DatasetLevel["Dataset Level"]
        COMBINE2["CombineGeotiff<br/>nodata_value: 10<br/>Merges all partitions"]
    end
    
    subgraph Output["Output"]
        GEOTIFF["Final GeoTIFF<br/>Classification raster<br/>10m resolution"]
    end
    
    WindowLevel --> PartitionLevel
    PartitionLevel --> DatasetLevel
    DatasetLevel --> GEOTIFF
```

- **process_window:** `NoopRaster` - No processing applied at individual window level
- **process_partition:** `CombineGeotiff` with `nodata_value: 10` merges all windows within a 1.0-degree partition
- **process_dataset:** `CombineGeotiff` with `nodata_value: 10` merges all partitions into the final output

**Sources:** [olmoearth_run_data/nandi/olmoearth_run.yaml:40-53]()

## Classification Schema and Visualization

The inference results use the following classification schema with RGB color mappings for visualization:

| Value | Label | Color (RGB) | Hex Color |
|-------|-------|-------------|-----------|
| 0 | coffee | [124, 67, 18] | #7C4312 |
| 1 | grassland | [169, 214, 146] | #A9D692 |
| 2 | trees | [51, 160, 44] | #33A02C |
| 3 | maize | [240, 159, 28] | #F09F1C |
| 4 | sugarcane | [251, 154, 153] | #FB9A99 |
| 5 | tea | [31, 234, 146] | #1FEA92 |
| 6 | vegetables | [166, 206, 227] | #A6CEE3 |
| 7 | legumes | [227, 26, 28] | #E31A1C |
| 8 | water | [31, 120, 180] | #1F78B4 |
| 9 | builtup | [136, 33, 233] | #8821E9 |
| 10 | (nodata) | N/A | N/A |

The `inference_results_config` in `olmoearth_run.yaml` defines this schema with `data_type: RASTER` and a single classification field named "segment" on band index 1.

**Sources:** [olmoearth_run_data/nandi/olmoearth_run.yaml:54-91]()

## Model Access and Usage

### Model Artifacts

The Nandi model and associated datasets are publicly available on HuggingFace:

| Artifact | Location |
|----------|----------|
| Model Checkpoint | https://huggingface.co/allenai/OlmoEarth-v1-FT-Nandi-Base/blob/main/model.ckpt |
| Annotation GeoJSONs | https://huggingface.co/datasets/allenai/olmoearth_projects_nandi/tree/main |
| rslearn Dataset | https://huggingface.co/datasets/allenai/olmoearth_projects_nandi/blob/main/dataset.tar |

**Sources:** [docs/nandi.md:5-10]()

### Inference Requirements

For optimal results, inference should be configured with:

**Temporal Requirements:**
- **Time Range:** One full year of coverage (365 days)
- **Recommended Period:** 2022-09-01 to 2023-09-01 (matching training data)
- **Alternative Periods:** Other one-year periods can be used (e.g., 2018-09-01 to 2019-09-01)
- **Timesteps:** 12 Sentinel-2 L2A mosaics, one per 30-day period

**Spatial Requirements:**
- **Grid Size:** Inference runs on 1024×1024 pixel windows
- **Coverage:** All grid cells intersecting the input geometry are processed
- **Resolution:** 10m per pixel

**Example Output:**

A full inference for Nandi County is available at: https://olmoearth.allenai.org/viewer/6b1e4537-ea68-47f3-9a11-61ca2d468fd0#9.55/0.2218/35.1037

**Sources:** [docs/nandi.md:39-43](), [olmoearth_run_data/nandi/prediction_request_geometry.geojson:1-39]()

### Inference Geometry Format

The `prediction_request_geometry.geojson` file defines the spatial and temporal extent for inference. For the Nandi model:

```json
{
  "features": [
    {
      "geometry": {
        "coordinates": [...],  // Polygon covering Nandi County
        "type": "Polygon"
      },
      "properties": {
        "oe_start_time": "2022-09-01T00:00:00Z",
        "oe_end_time": "2023-09-01T00:00:00Z"
      },
      "type": "Feature"
    }
  ],
  "type": "FeatureCollection"
}
```

The geometry covers approximately:
- **Longitude:** 34.73°E to 35.48°E
- **Latitude:** -0.12°S to 0.57°N
- **Area:** Entire Nandi County administrative boundary

**Sources:** [olmoearth_run_data/nandi/prediction_request_geometry.geojson:1-39]()

## Training and Fine-tuning

For detailed information on training and fine-tuning procedures, refer to the main README. The training process follows the standard workflow documented in [Model Training](#5) with the configurations specified in this page.

**Key Training Files:**
- Model architecture: [olmoearth_run_data/nandi/model.yaml:1-336]()
- Inference configuration: [olmoearth_run_data/nandi/olmoearth_run.yaml:1-92]()
- Prediction geometry: [olmoearth_run_data/nandi/prediction_request_geometry.geojson:1-39]()

**Sources:** [docs/nandi.md:45-47]()

---

# Page: AWF Land Cover Model

# AWF Land Cover Model

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/awf.md](docs/awf.md)
- [docs/nandi.md](docs/nandi.md)
- [olmoearth_run_data/awf/dataset.json](olmoearth_run_data/awf/dataset.json)
- [olmoearth_run_data/awf/model.yaml](olmoearth_run_data/awf/model.yaml)
- [olmoearth_run_data/nandi/dataset.json](olmoearth_run_data/nandi/dataset.json)
- [olmoearth_run_data/nandi/model.yaml](olmoearth_run_data/nandi/model.yaml)
- [olmoearth_run_data/nandi/prediction_request_geometry.geojson](olmoearth_run_data/nandi/prediction_request_geometry.geojson)

</details>



## Purpose and Overview

This page documents the AWF (African Wildlife Foundation) Land Cover Model, a fine-tuned variant of OlmoEarth-v1-Base for land use and land cover classification in southern Kenya. The model classifies satellite imagery into 9 land cover categories including various forest types, grasslands, wetlands, and human-modified landscapes.

For general information about the model training pipeline, see [Model Training](#5). For details about running inference, see [Inference and Deployment](#7). For information about other fine-tuned models, see [Available Models](#6).

**Sources:** [docs/awf.md:1-6]()

## Model Architecture

The AWF model uses a hierarchical encoder-decoder architecture built on the OlmoEarth foundation model with task-specific components for land cover segmentation.

```mermaid
graph TB
    subgraph Input["Input Layer"]
        S2["Sentinel-2 L2A<br/>12 bands × 12 timesteps<br/>16×16 window<br/>31-pixel padded"]
    end
    
    subgraph Encoder["Encoder Pipeline"]
        OLMO["rslearn.models.olmoearth_pretrain.model.OlmoEarth<br/>model_id: OLMOEARTH_V1_BASE<br/>patch_size: 4<br/>Output: 768 channels"]
    end
    
    subgraph Decoder["Decoder Pipeline - segment task"]
        UP["rslearn.models.upsample.Upsample<br/>scale_factor: 4<br/>16×16 → 16×16"]
        CONV["rslearn.models.conv.Conv<br/>in_channels: 768<br/>out_channels: 10<br/>kernel_size: 1"]
        HEAD["rslearn.train.tasks.segmentation.SegmentationHead"]
    end
    
    subgraph Output["Output"]
        PRED["Classification Map<br/>10 classes<br/>16×16 pixels<br/>class 9 = nodata"]
    end
    
    S2 --> OLMO
    OLMO --> UP
    UP --> CONV
    CONV --> HEAD
    HEAD --> PRED
```

**Architecture Details:**

| Component | Class Path | Key Parameters |
|-----------|-----------|----------------|
| Model Wrapper | `rslearn.train.lightning_module.RslearnLightningModule` | lr: 0.0001, plateau scheduling |
| Encoder | `rslearn.models.olmoearth_pretrain.model.OlmoEarth` | model_id: OLMOEARTH_V1_BASE, patch_size: 4 |
| Upsampler | `rslearn.models.upsample.Upsample` | scale_factor: 4 |
| Classifier | `rslearn.models.conv.Conv` | 768 → 10 channels |
| Task Head | `rslearn.train.tasks.segmentation.SegmentationHead` | num_classes: 10 |

**Sources:** [olmoearth_run_data/awf/model.yaml:1-24]()

## Training Data and Data Collection

The model is trained on 1,469 labeled point samples collected by the African Wildlife Foundation across southern Kenya. The training data was annotated using Planet imagery as the primary reference.

```mermaid
graph LR
    subgraph Sources["Data Sources"]
        AWF["AWF Field Annotations<br/>1469 labeled points<br/>Planet imagery reference"]
    end
    
    subgraph Processing["Window Generation"]
        POINT["Point Sample<br/>lon, lat<br/>2023-01 to 2023-12"]
        WINDOW["rslearn Window<br/>Centered on point<br/>One year coverage"]
        QUERY["Planetary Computer Query<br/>12 Sentinel-2 mosaics<br/>30-day periods"]
    end
    
    subgraph Split["Spatial Split"]
        HASH["128×128 pixel grid<br/>Spatial hashing"]
        TRAIN["Training Set<br/>75% of tiles"]
        VAL["Validation Set<br/>25% of tiles"]
    end
    
    AWF --> POINT
    POINT --> WINDOW
    WINDOW --> QUERY
    QUERY --> HASH
    HASH --> TRAIN
    HASH --> VAL
```

The dataset uses spatial splitting to ensure that training and validation samples are geographically separated, preventing spatial autocorrelation bias. This is implemented by hashing a 128×128 pixel grid into train (75%) and validation (25%) splits.

**Sources:** [docs/awf.md:29-35](), [olmoearth_run_data/awf/model.yaml:263-273]()

## Land Cover Classes

The model classifies pixels into 9 distinct land cover types, with a 10th class (index 9) reserved as the nodata value:

| Class Index | Class Name | Description |
|-------------|-----------|-------------|
| 0 | Woodland Forest | Forest with >40% canopy cover |
| 1 | Open Water | Lakes, rivers, permanent water bodies |
| 2 | Shrubland/Savanna | Mixed shrubs and grassland ecosystems |
| 3 | Herbaceous Wetland | Wetland areas with herbaceous vegetation |
| 4 | Grassland/Barren | Grasslands and bare ground |
| 5 | Agriculture/Settlement | Agricultural fields and rural settlements |
| 6 | Montane Forest | High-elevation forest ecosystems |
| 7 | Lava Forest | Forest on volcanic substrates |
| 8 | Urban/Dense Development | Cities and dense built-up areas |
| 9 | Nodata | Invalid or missing data |

**Sources:** [docs/awf.md:31-33](), [olmoearth_run_data/awf/model.yaml:57-59]()

## Model Performance

The model achieves 89.5% overall accuracy on the validation set using window size 16×16 and patch size 4 with Sentinel-2-only input. Multiple configurations were tested:

| Window Size | Patch Size | Input Modalities | Accuracy |
|-------------|------------|------------------|----------|
| 16×16 | 1 | Sentinel-2 | 90.4% |
| 16×16 | 1 | Sentinel-2 + Sentinel-1 | 83.1% |
| **16×16** | **4** | **Sentinel-2** | **89.5%** |
| 16×16 | 4 | Sentinel-2 + Sentinel-1 | 83.1% |
| 32×32 | 4 | Sentinel-2 | 88.5% |
| 32×32 | 4 | Sentinel-2 + Sentinel-1 | 83.1% |

The model using Sentinel-2-only input consistently outperforms configurations that include Sentinel-1 radar data. The selected configuration (bold) balances accuracy with computational efficiency.

**Sources:** [docs/awf.md:18-27]()

## Per-Class Evaluation Metrics

The model configuration includes comprehensive per-class precision and recall tracking for all 9 land cover types:

```mermaid
graph LR
    subgraph Metrics["Per-Class Metrics Configuration"]
        TASK["rslearn.train.tasks.segmentation.SegmentationTask<br/>num_classes: 10<br/>average: micro"]
        
        WOODLAND_P["woodland_forest_precision<br/>MulticlassPrecision<br/>class_idx: 0"]
        WOODLAND_R["woodland_forest_recall<br/>MulticlassRecall<br/>class_idx: 0"]
        
        WATER_P["open_water_precision<br/>class_idx: 1"]
        WATER_R["open_water_recall<br/>class_idx: 1"]
        
        SHRUB_P["shrubland_savanna_precision<br/>class_idx: 2"]
        SHRUB_R["shrubland_savanna_recall<br/>class_idx: 2"]
        
        OTHER["Additional metrics<br/>for remaining 6 classes"]
    end
    
    TASK --> WOODLAND_P
    TASK --> WOODLAND_R
    TASK --> WATER_P
    TASK --> WATER_R
    TASK --> SHRUB_P
    TASK --> SHRUB_R
    TASK --> OTHER
```

Each class has dedicated precision and recall metrics using `torchmetrics.classification.MulticlassPrecision` and `torchmetrics.classification.MulticlassRecall` with `average: null` to compute per-class values.

**Sources:** [olmoearth_run_data/awf/model.yaml:62-224]()

## Input Data Configuration

The model uses Sentinel-2 Level 2A (surface reflectance) imagery queried from Microsoft Planetary Computer:

```mermaid
graph TB
    subgraph DataSource["dataset.json Configuration"]
        SENTINEL["sentinel2 layer<br/>rslearn.data_sources.planetary_computer.Sentinel2"]
        
        BANDS["Bands: B01, B02, B03, B04<br/>B05, B06, B07, B08<br/>B8A, B09, B11, B12<br/>dtype: uint16"]
        
        QUERY["Query Configuration<br/>max_matches: 12<br/>min_matches: 12<br/>period_duration: 30d<br/>space_mode: PER_PERIOD_MOSAIC"]
        
        OPTIONS["Data Source Options<br/>harmonize: true<br/>sort_by: eo:cloud_cover<br/>cache_dir: cache/planetary_computer"]
    end
    
    SENTINEL --> BANDS
    SENTINEL --> QUERY
    SENTINEL --> OPTIONS
```

**Key Configuration Parameters:**

| Parameter | Value | Description |
|-----------|-------|-------------|
| `max_matches` / `min_matches` | 12 | Exactly 12 timesteps required |
| `period_duration` | 30d | One mosaic per 30-day period |
| `space_mode` | PER_PERIOD_MOSAIC | Mosaic all images within each period |
| `harmonize` | true | Apply cross-sensor harmonization |
| `sort_by` | eo:cloud_cover | Prioritize low-cloud imagery |

**Sources:** [olmoearth_run_data/awf/dataset.json:25-61]()

## Training Configuration Details

### Data Transforms Pipeline

The training pipeline applies a sequence of transforms to prepare input data:

```mermaid
graph LR
    subgraph TrainTransforms["Training Transforms"]
        PAD["rslearn.train.transforms.pad.Pad<br/>size: 31<br/>mode: center"]
        CROP["rslearn.train.transforms.crop.Crop<br/>crop_size: 16"]
        FLIP["rslearn.train.transforms.flip.Flip<br/>Random horizontal/vertical"]
        NORM["rslearn.models.olmoearth_pretrain.norm.OlmoEarthNormalize<br/>All 12 Sentinel-2 bands"]
    end
    
    subgraph ValTransforms["Validation Transforms"]
        PAD2["Pad<br/>size: 31"]
        CROP2["Crop<br/>size: 16"]
        NORM2["OlmoEarthNormalize"]
    end
    
    PAD --> CROP
    CROP --> FLIP
    FLIP --> NORM
    
    PAD2 --> CROP2
    CROP2 --> NORM2
```

Training uses additional data augmentation (flip) compared to validation/test splits.

**Sources:** [olmoearth_run_data/awf/model.yaml:245-273]()

### Learning Rate and Optimization

The model uses a plateau-based learning rate scheduler with progressive unfreezing:

| Parameter | Value | Description |
|-----------|-------|-------------|
| Initial LR | 0.0001 | Base learning rate |
| Plateau Factor | 0.2 | Multiply LR by 0.2 on plateau |
| Plateau Patience | 2 | Epochs to wait before reducing |
| Plateau Cooldown | 10 | Epochs between reductions |
| Unfreeze Epoch | 20 | When to unfreeze encoder |
| Unfreeze LR Factor | 10 | Multiply encoder LR by 10 |

The `FreezeUnfreeze` callback initially freezes the OlmoEarth encoder (module selector: `["model", "encoder", 0]`), then unfreezes it at epoch 20 with a 10× learning rate boost for fine-tuning.

**Sources:** [olmoearth_run_data/awf/model.yaml:25-30](), [olmoearth_run_data/awf/model.yaml:303-307]()

## Training and Validation Split

The dataset uses spatial splitting based on a 128×128 pixel grid to ensure geographic separation:

```python
# Configuration in model.yaml
train_config:
  groups: ["spatial_split"]
  tags:
    split: "train"
    
val_config:
  groups: ["spatial_split"]
  tags:
    split: "val"
```

This ensures that training and validation samples are geographically separated, preventing the model from exploiting spatial autocorrelation in the evaluation metrics.

**Sources:** [olmoearth_run_data/awf/model.yaml:263-273]()

## Inference Configuration

### Prediction Window Processing

During inference, the model processes overlapping patches to ensure smooth predictions across tile boundaries:

```mermaid
graph TB
    subgraph PredictConfig["Inference Configuration"]
        LOAD["load_all_patches: true<br/>Load entire window"]
        PATCH["patch_size: 16<br/>Process 16×16 patches"]
        OVERLAP["overlap_ratio: 0.25<br/>4-pixel overlap"]
        SKIP["skip_targets: true<br/>No ground truth needed"]
    end
    
    subgraph Processing["Patch Processing"]
        GRID["Generate overlapping grid<br/>16×16 patches<br/>25% overlap"]
        INFER["Run model inference<br/>Per-patch predictions"]
        MERGE["RasterMerger<br/>padding: 2<br/>Blend overlapping regions"]
    end
    
    LOAD --> GRID
    PATCH --> GRID
    OVERLAP --> GRID
    GRID --> INFER
    INFER --> MERGE
    SKIP --> INFER
```

The 25% overlap (4 pixels out of 16) ensures smooth transitions between adjacent patches. The `RasterMerger` with `padding: 2` blends predictions in overlapping regions.

**Sources:** [olmoearth_run_data/awf/model.yaml:274-283](), [olmoearth_run_data/awf/model.yaml:308-316]()

### Time Range Requirements

For optimal results, inference should use a one-year time range matching the training data:

- **Recommended:** 2023-01-01 to 2023-12-31 (matches training period)
- **Alternative:** Other one-year periods can be used but may have reduced accuracy

The prediction request geometry should specify these dates in the `oe_start_time` and `oe_end_time` properties. See [Prediction Request Geometries](#7.2) for details on creating request files.

**Sources:** [docs/awf.md:37-39]()

## Model Resources and Distribution

### HuggingFace Hub Resources

The AWF model and associated data are distributed through HuggingFace:

| Resource Type | URL |
|--------------|-----|
| Model Checkpoint | https://huggingface.co/allenai/OlmoEarth-v1-FT-AWF-Base/blob/main/model.ckpt |
| Annotation GeoJSONs | https://huggingface.co/datasets/allenai/olmoearth_projects_awf/tree/main |
| rslearn Dataset (tar) | https://huggingface.co/datasets/allenai/olmoearth_projects_awf/blob/main/dataset.tar |

**Sources:** [docs/awf.md:8-10]()

### Example Inference Output

A complete inference run over the Amboseli National Park region is available for interactive visualization:

- **Viewer URL:** https://olmoearth.allenai.org/viewer/d591a8ce-c97d-4a23-a520-a1aa1363ce22#8.76/-2.9277/37.3573
- **Coverage:** Amboseli National Park and surrounding areas
- **Time Range:** 2023-01-01 to 2023-12-31

This demonstrates the model's ability to classify diverse landscapes including protected wildlife areas, agricultural zones, and different forest types in the region.

**Sources:** [docs/awf.md:41-42]()

## File Locations

The AWF model configuration files are located in the repository at:

```
olmoearth_run_data/awf/
├── model.yaml              # Model architecture and training config
├── dataset.json            # Data source and layer definitions
├── olmoearth_run.yaml      # Inference pipeline configuration (see page 7.1)
└── prediction_request_geometry.geojson  # Example request geometry
```

These files define the complete model specification and can be used for both fine-tuning (see [Fine-tuning Process](#5.3)) and inference (see [olmoearth_run Pipeline](#7.1)).

**Sources:** [olmoearth_run_data/awf/model.yaml:1](), [olmoearth_run_data/awf/dataset.json:1]()

---

# Page: Inference and Deployment

# Inference and Deployment

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [LICENSE](LICENSE)
- [README.md](README.md)
- [olmoearth_run_data/awf/olmoearth_run.yaml](olmoearth_run_data/awf/olmoearth_run.yaml)
- [olmoearth_run_data/mozambique_lulc/dataset.json](olmoearth_run_data/mozambique_lulc/dataset.json)
- [olmoearth_run_data/mozambique_lulc/model.yaml](olmoearth_run_data/mozambique_lulc/model.yaml)
- [olmoearth_run_data/mozambique_lulc/olmoearth_run.yaml](olmoearth_run_data/mozambique_lulc/olmoearth_run.yaml)
- [olmoearth_run_data/nandi/olmoearth_run.yaml](olmoearth_run_data/nandi/olmoearth_run.yaml)

</details>



## Purpose and Scope

This document provides an overview of how trained models in the `olmoearth_projects` repository are applied to new geographic areas and deployed for production use. It covers the configuration-based inference pipeline, model checkpoint management, and deployment strategies including command-line execution and web-based interfaces.

For detailed information about specific components:
- For the `olmoearth_run` pipeline internals, see [olmoearth_run Pipeline](#7.1)
- For creating prediction requests, see [Prediction Request Geometries](#7.2)
- For partitioning strategies, see [Partitioning and Grid Processing](#7.3)
- For output generation, see [Post-processing and Output](#7.4)
- For web deployment, see [OlmoEarth Studio Integration](#7.5)

For model training, see [Model Training](#5). For available models and their specifications, see [Available Models](#6).

**Sources:** [README.md:1-190]()

## Overview

Inference in this repository follows a configuration-driven approach where three types of files control the entire process:

| Configuration File | Purpose | Location |
|-------------------|---------|----------|
| `dataset.json` | Defines satellite data sources and acquisition parameters | `olmoearth_run_data/PROJECT_NAME/` |
| `model.yaml` | Specifies model architecture, loading, and data transforms | `olmoearth_run_data/PROJECT_NAME/` |
| `olmoearth_run.yaml` | Controls partitioning strategies and post-processing | `olmoearth_run_data/PROJECT_NAME/` |

The inference workflow proceeds through these stages:

1. **Request Definition**: User creates a `prediction_request_geometry.geojson` file specifying spatial (polygons) and temporal (start/end dates) extent
2. **Partitioning**: Large geographic areas are divided hierarchically into processable units
3. **Data Acquisition**: Satellite imagery is queried from data sources (typically Microsoft Planetary Computer)
4. **Model Prediction**: The trained model processes each partition with overlap handling
5. **Post-processing**: Results are combined at window, partition, and dataset levels
6. **Output Generation**: Final GeoTIFF rasters are created with metadata and visualization schemes

**Sources:** [README.md:49-140](), [olmoearth_run_data/nandi/olmoearth_run.yaml:1-92]()

## Inference Workflow

```mermaid
graph TB
    subgraph "User Input"
        USER["User"]
        GEOJSON["prediction_request_geometry.geojson<br/>Polygon + oe_start_time + oe_end_time"]
    end
    
    subgraph "Configuration Files"
        DATASET_JSON["dataset.json<br/>Data source definitions<br/>Query parameters"]
        MODEL_YAML["model.yaml<br/>Model architecture<br/>Transforms"]
        RUN_YAML["olmoearth_run.yaml<br/>Partitioning strategies<br/>Post-processing"]
    end
    
    subgraph "Execution"
        MAIN["python -m olmoearth_projects.main<br/>olmoearth_run"]
        CHECKPOINT["Model Checkpoint<br/>*.ckpt file"]
    end
    
    subgraph "Processing Pipeline"
        PARTITION["Hierarchical Partitioning<br/>GridPartitioner<br/>Coarse + Fine grids"]
        QUERY["Data Acquisition<br/>Planetary Computer<br/>Sentinel-2 imagery"]
        PREDICT["Model Inference<br/>RslearnLightningModule.predict<br/>Overlapping patches"]
        POSTPROC["Post-processing<br/>CombineGeotiff<br/>Multi-level aggregation"]
    end
    
    subgraph "Output"
        GEOTIFF["GeoTIFF Rasters<br/>results_raster/*.tif<br/>Classification or Regression"]
        METADATA["Inference Metadata<br/>Class labels<br/>Color schemes"]
        VIEWER["Visualization<br/>QGIS or OlmoEarth Studio"]
    end
    
    USER --> GEOJSON
    GEOJSON --> MAIN
    DATASET_JSON --> MAIN
    MODEL_YAML --> MAIN
    RUN_YAML --> MAIN
    CHECKPOINT --> MAIN
    
    MAIN --> PARTITION
    PARTITION --> QUERY
    QUERY --> PREDICT
    PREDICT --> POSTPROC
    POSTPROC --> GEOTIFF
    RUN_YAML --> METADATA
    METADATA --> GEOTIFF
    GEOTIFF --> VIEWER
```

**Sources:** [README.md:49-140](), Diagram 4 from high-level architecture

## Configuration Files

### dataset.json

The `dataset.json` file is an rslearn dataset configuration that defines the layers and data sources for inference. It specifies:

- **Layers**: Named data layers with band definitions and data types
- **Data Sources**: Query configurations for satellite imagery providers
- **Query Parameters**: Temporal mosaicking settings, cloud cover sorting, match requirements

Example structure from the Mozambique LULC project:

```json
{
  "layers": {
    "sentinel2": {
      "band_sets": [{
        "bands": ["B01", "B02", "B03", ..., "B12"],
        "dtype": "uint16"
      }],
      "data_source": {
        "class_path": "rslearn.data_sources.planetary_computer.Sentinel2",
        "query_config": {
          "max_matches": 8,
          "period_duration": "30d",
          "space_mode": "PER_PERIOD_MOSAIC"
        }
      }
    }
  }
}
```

**Sources:** [olmoearth_run_data/mozambique_lulc/dataset.json:1-64]()

### model.yaml

The `model.yaml` file defines the model architecture and inference configuration. Key sections include:

- **model**: Specifies encoder (OlmoEarth) and decoder (task-specific heads) architecture
- **data**: Configures `RslearnDataModule` with input mappings and transforms
- **predict_config**: Sets patch size, overlap ratio, and inference-specific transforms

The predict_config section is particularly important for inference:

```yaml
predict_config:
  load_all_patches: true
  patch_size: 16
  overlap_ratio: 0.25  # 4 / 16 pixel overlap
  skip_targets: true
  transforms:
    - class_path: rslearn.models.olmoearth_pretrain.norm.OlmoEarthNormalize
```

**Sources:** [olmoearth_run_data/mozambique_lulc/model.yaml:1-278]()

### olmoearth_run.yaml

The `olmoearth_run.yaml` file controls the inference execution strategy:

| Section | Purpose | Key Parameters |
|---------|---------|----------------|
| `partition_strategies` | Defines hierarchical grid partitioning | `grid_size`, `output_projection`, `use_utm` |
| `postprocessing_strategies` | Specifies result aggregation methods | `CombineGeotiff`, `NoopRaster` |
| `inference_results_config` | Defines output metadata | `classification_fields`, `allowed_values`, colors |

Example partition strategy:

```yaml
partition_strategies:
  partition_request_geometry:
    class_path: olmoearth_run.runner.tools.partitioners.grid_partitioner.GridPartitioner
    init_args:
      grid_size: 0.25  # degrees
  
  prepare_window_geometries:
    class_path: olmoearth_run.runner.tools.partitioners.grid_partitioner.GridPartitioner
    init_args:
      grid_size: 1024  # pixels
      use_utm: true
```

**Sources:** [olmoearth_run_data/mozambique_lulc/olmoearth_run.yaml:1-81](), [olmoearth_run_data/nandi/olmoearth_run.yaml:22-38]()

## Model Checkpoints

Model checkpoints are PyTorch Lightning checkpoint files (`.ckpt`) containing trained model weights and optimizer states. These are loaded during inference via the `--checkpoint_path` argument.

### Checkpoint Sources

Checkpoints are distributed through multiple channels:

- **HuggingFace Hub**: Public model checkpoints under the `allenai` organization (e.g., `allenai/OlmoEarth-v1-FT-LFMC-Base`)
- **Direct Download**: Released via HuggingFace URLs for downloading
- **Local Training**: Generated in `TRAINER_DATA_PATH` during fine-tuning

Example checkpoint download:

```bash
mkdir ./checkpoints
wget https://huggingface.co/allenai/OlmoEarth-v1-FT-LFMC-Base/resolve/main/model.ckpt \
  -O checkpoints/lfmc.ckpt
```

### Checkpoint Loading

During inference, the checkpoint is loaded by `RslearnLightningModule` and the model is reconstructed from the architecture defined in `model.yaml`. The encoder (OlmoEarth) is initialized with the checkpoint path specified in the model configuration at [olmoearth_run_data/mozambique_lulc/model.yaml:10]().

**Sources:** [README.md:109-114](), [olmoearth_run_data/mozambique_lulc/model.yaml:8-12]()

## Execution Methods

### Command-Line Execution

The primary execution method uses the `olmoearth_projects.main` module with the `olmoearth_run` command:

```bash
# Set environment variables
export NUM_WORKERS=32
export WANDB_PROJECT=project_name
export WANDB_NAME=inference_run
export WANDB_ENTITY=your_entity

# Execute inference
python -m olmoearth_projects.main olmoearth_run \
  --config_path $PWD/olmoearth_run_data/PROJECT_NAME/ \
  --checkpoint_path $PWD/checkpoints/model.ckpt \
  --scratch_path project_data/PROJECT_NAME/
```

**Environment Variables:**

| Variable | Purpose | Required |
|----------|---------|----------|
| `NUM_WORKERS` | Number of parallel data loading workers | Yes |
| `WANDB_PROJECT` | Weights & Biases project name for logging | Yes |
| `WANDB_NAME` | Run name for this inference execution | Yes |
| `WANDB_ENTITY` | W&B organization/user entity | Yes |

**Sources:** [README.md:116-130]()

### Output Structure

Inference outputs are organized in the scratch path directory:

```
project_data/PROJECT_NAME/
├── results/
│   └── results_raster/
│       └── *.tif           # Final GeoTIFF outputs
├── dataset/                 # rslearn dataset for inference
└── partitions/              # Intermediate partition results
```

The `results_raster` directory contains one or more GeoTIFF files representing the classification or regression predictions. These files include:

- Georeferencing information (CRS, affine transform)
- Classification labels or regression values
- NoData values for invalid regions
- Color tables for visualization (from `inference_results_config`)

**Sources:** [README.md:133-140]()

## Configuration-to-Component Mapping

```mermaid
graph TB
    subgraph "Configuration Files"
        DATASET_JSON["dataset.json"]
        MODEL_YAML["model.yaml"]
        RUN_YAML["olmoearth_run.yaml"]
        PRED_GEOM["prediction_request_geometry.geojson"]
    end
    
    subgraph "Data Acquisition Components"
        SENTINEL2["rslearn.data_sources.planetary_computer.Sentinel2"]
        QUERY_CFG["query_config<br/>max_matches, period_duration<br/>space_mode"]
        HARMONIZE["harmonize: true<br/>sort_by: eo:cloud_cover"]
    end
    
    subgraph "Model Components"
        OLMOEARTH["rslearn.models.olmoearth_pretrain.model.OlmoEarth"]
        DECODER["Decoders:<br/>Upsample + Conv + SegmentationHead"]
        LIGHTNING["rslearn.train.lightning_module.RslearnLightningModule"]
        DATAMODULE["rslearn.train.data_module.RslearnDataModule"]
    end
    
    subgraph "Transform Pipeline"
        PAD["rslearn.train.transforms.pad.Pad"]
        NORM["rslearn.models.olmoearth_pretrain.norm.OlmoEarthNormalize"]
        PATCH["patch_size: 16<br/>overlap_ratio: 0.25"]
    end
    
    subgraph "Partitioning Components"
        GRID_PART["olmoearth_run.runner.tools.partitioners.grid_partitioner.GridPartitioner"]
        COARSE["partition_request_geometry<br/>grid_size: 0.1-1.0 degrees"]
        FINE["prepare_window_geometries<br/>grid_size: 32-1024 pixels"]
        PROJ["output_projection<br/>Projection with CRS + resolution<br/>use_utm: true"]
    end
    
    subgraph "Post-processing Components"
        COMBINE["olmoearth_run.runner.tools.postprocessors.combine_geotiff.CombineGeotiff"]
        NOOP["olmoearth_run.runner.tools.postprocessors.noop_raster.NoopRaster"]
        WINDOW_PP["process_window"]
        PARTITION_PP["process_partition"]
        DATASET_PP["process_dataset"]
    end
    
    subgraph "Metadata Components"
        RESULTS_CFG["inference_results_config"]
        CLASS_FIELDS["classification_fields<br/>property_name, band_index"]
        ALLOWED_VALS["allowed_values<br/>value, label, color"]
    end
    
    DATASET_JSON --> SENTINEL2
    DATASET_JSON --> QUERY_CFG
    DATASET_JSON --> HARMONIZE
    
    MODEL_YAML --> OLMOEARTH
    MODEL_YAML --> DECODER
    MODEL_YAML --> LIGHTNING
    MODEL_YAML --> DATAMODULE
    MODEL_YAML --> PAD
    MODEL_YAML --> NORM
    MODEL_YAML --> PATCH
    
    RUN_YAML --> GRID_PART
    GRID_PART --> COARSE
    GRID_PART --> FINE
    RUN_YAML --> PROJ
    RUN_YAML --> COMBINE
    RUN_YAML --> NOOP
    COMBINE --> WINDOW_PP
    COMBINE --> PARTITION_PP
    COMBINE --> DATASET_PP
    
    RUN_YAML --> RESULTS_CFG
    RESULTS_CFG --> CLASS_FIELDS
    RESULTS_CFG --> ALLOWED_VALS
    
    PRED_GEOM -.->|"oe_start_time<br/>oe_end_time"| QUERY_CFG
```

**Sources:** [olmoearth_run_data/mozambique_lulc/dataset.json:1-64](), [olmoearth_run_data/mozambique_lulc/model.yaml:1-278](), [olmoearth_run_data/mozambique_lulc/olmoearth_run.yaml:1-81](), [olmoearth_run_data/nandi/olmoearth_run.yaml:1-92]()

## Inference Pipeline Code Flow

```mermaid
graph TB
    subgraph "Entry Point"
        MAIN["olmoearth_projects.main<br/>olmoearth_run command"]
    end
    
    subgraph "Configuration Loading"
        LOAD_CONFIG["Load configuration files<br/>dataset.json, model.yaml<br/>olmoearth_run.yaml"]
        LOAD_CKPT["Load checkpoint<br/>*.ckpt file"]
    end
    
    subgraph "Partitioning Phase"
        PART_REQ["partition_request_geometry<br/>GridPartitioner.partition"]
        PREP_WIN["prepare_window_geometries<br/>GridPartitioner.partition"]
        CREATE_DATASET["Create rslearn dataset<br/>for inference windows"]
    end
    
    subgraph "Data Acquisition Phase"
        QUERY_PC["Query Planetary Computer<br/>Sentinel2.query"]
        MOSAIC["Create temporal mosaics<br/>PER_PERIOD_MOSAIC"]
        CACHE["Cache downloaded data<br/>cache/planetary_computer/"]
    end
    
    subgraph "Model Loading Phase"
        INIT_MODULE["Initialize RslearnLightningModule<br/>from model.yaml"]
        LOAD_WEIGHTS["Load weights from checkpoint<br/>OlmoEarth encoder + decoder"]
        INIT_DATAMODULE["Initialize RslearnDataModule<br/>predict_config settings"]
    end
    
    subgraph "Prediction Phase"
        APPLY_TRANSFORMS["Apply transforms<br/>Pad, OlmoEarthNormalize"]
        GENERATE_PATCHES["Generate overlapping patches<br/>overlap_ratio: 0.25"]
        RUN_PREDICT["Run model.predict<br/>Batch processing"]
        MERGE_PATCHES["Merge overlapping predictions<br/>RasterMerger with padding"]
    end
    
    subgraph "Post-processing Phase"
        PROC_WIN["process_window<br/>NoopRaster or window-level ops"]
        PROC_PART["process_partition<br/>CombineGeotiff merge"]
        PROC_DATASET["process_dataset<br/>CombineGeotiff final merge"]
    end
    
    subgraph "Output Generation"
        WRITE_GEOTIFF["Write GeoTIFF<br/>results_raster/*.tif"]
        ATTACH_METADATA["Attach metadata<br/>classification_fields<br/>color schemes"]
    end
    
    MAIN --> LOAD_CONFIG
    MAIN --> LOAD_CKPT
    
    LOAD_CONFIG --> PART_REQ
    PART_REQ --> PREP_WIN
    PREP_WIN --> CREATE_DATASET
    
    CREATE_DATASET --> QUERY_PC
    QUERY_PC --> MOSAIC
    MOSAIC --> CACHE
    
    LOAD_CKPT --> INIT_MODULE
    LOAD_CONFIG --> INIT_MODULE
    INIT_MODULE --> LOAD_WEIGHTS
    INIT_MODULE --> INIT_DATAMODULE
    
    CACHE --> APPLY_TRANSFORMS
    INIT_DATAMODULE --> APPLY_TRANSFORMS
    APPLY_TRANSFORMS --> GENERATE_PATCHES
    GENERATE_PATCHES --> RUN_PREDICT
    LOAD_WEIGHTS --> RUN_PREDICT
    RUN_PREDICT --> MERGE_PATCHES
    
    MERGE_PATCHES --> PROC_WIN
    PROC_WIN --> PROC_PART
    PROC_PART --> PROC_DATASET
    
    PROC_DATASET --> WRITE_GEOTIFF
    LOAD_CONFIG --> ATTACH_METADATA
    ATTACH_METADATA --> WRITE_GEOTIFF
```

**Sources:** [README.md:49-140](), [olmoearth_run_data/mozambique_lulc/model.yaml:236-245](), [olmoearth_run_data/nandi/olmoearth_run.yaml:22-52]()

## Deployment to OlmoEarth Studio

While command-line execution is the primary documented method, models can be deployed to the OlmoEarth Studio web interface at `olmoearth.allenai.org` for interactive inference. This provides:

- **Interactive Map Interface**: Users can draw polygons and select time ranges visually
- **Real-time Prediction**: On-demand inference for user-defined regions
- **Visualization**: Integrated map viewer with classification overlays
- **Multi-model Support**: Access to all published fine-tuned models

The studio integration uses the same configuration files (`model.yaml`, `dataset.json`, `olmoearth_run.yaml`) and model checkpoints, ensuring consistency between command-line and web-based inference.

**Sources:** Diagram 1 and Diagram 3 from high-level architecture, [README.md:4-6]()

## Prediction Request Geometry Format

The `prediction_request_geometry.geojson` file defines the spatial and temporal extent for inference. It follows standard GeoJSON format with additional temporal properties:

```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Polygon",
        "coordinates": [...]
      },
      "properties": {
        "oe_start_time": "2024-01-01T00:00:00+00:00",
        "oe_end_time": "2024-02-01T00:00:00+00:00"
      }
    }
  ]
}
```

**Temporal Properties:**

| Property | Format | Purpose |
|----------|--------|---------|
| `oe_start_time` | ISO 8601 datetime with timezone | Start of temporal query window |
| `oe_end_time` | ISO 8601 datetime with timezone | End of temporal query window |

The time range determines which satellite images are queried based on the `period_duration` and mosaic settings in `dataset.json`. Different models have different temporal requirements (e.g., 6-12 timesteps over several months).

Users can create prediction geometries using [geojson.io](https://geojson.io/) for the spatial component, then manually add the temporal properties.

**Sources:** [README.md:75-104]()

## Output Visualization

The GeoTIFF outputs in `results_raster/` can be visualized using:

### QGIS

```bash
qgis project_data/PROJECT_NAME/results/results_raster/*.tif
```

QGIS automatically reads the embedded color tables and classification metadata from the `inference_results_config` section of `olmoearth_run.yaml`.

### OlmoEarth Studio

Upload results to the web interface for interactive exploration with basemap overlays and multi-temporal comparison.

### Custom Applications

The GeoTIFF format is compatible with standard geospatial libraries:

- **Python**: `rasterio`, `xarray`, `rioxarray`
- **R**: `terra`, `raster`, `sf`
- **JavaScript**: `geotiff.js`, `Leaflet`, `OpenLayers`

**Sources:** [README.md:133-140](), [olmoearth_run_data/mozambique_lulc/olmoearth_run.yaml:1-28]()

---

# Page: olmoearth_run Pipeline

# olmoearth_run Pipeline

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [olmoearth_run_data/awf/olmoearth_run.yaml](olmoearth_run_data/awf/olmoearth_run.yaml)
- [olmoearth_run_data/mangrove/dataset.json](olmoearth_run_data/mangrove/dataset.json)
- [olmoearth_run_data/mangrove/model.yaml](olmoearth_run_data/mangrove/model.yaml)
- [olmoearth_run_data/mangrove/olmoearth_run.yaml](olmoearth_run_data/mangrove/olmoearth_run.yaml)
- [olmoearth_run_data/mozambique_lulc/dataset.json](olmoearth_run_data/mozambique_lulc/dataset.json)
- [olmoearth_run_data/mozambique_lulc/model.yaml](olmoearth_run_data/mozambique_lulc/model.yaml)
- [olmoearth_run_data/mozambique_lulc/olmoearth_run.yaml](olmoearth_run_data/mozambique_lulc/olmoearth_run.yaml)
- [olmoearth_run_data/nandi/olmoearth_run.yaml](olmoearth_run_data/nandi/olmoearth_run.yaml)

</details>



## Purpose and Scope

The `olmoearth_run` pipeline is the inference execution system that processes geographic regions through trained OlmoEarth models to generate classification or regression outputs. This pipeline handles the complete workflow from receiving a spatial request to producing final GeoTIFF rasters with prediction results.

This document covers the inference pipeline configuration and execution process. For information about model training, see [Model Training](#5). For details on creating prediction request geometries, see [Prediction Request Geometries](#7.2). For post-processing strategies, see [Post-processing and Output](#7.4).

## Pipeline Architecture

The `olmoearth_run` pipeline processes inference requests through five sequential stages, each configured through `olmoearth_run.yaml` and `model.yaml` files.

```mermaid
graph TB
    subgraph "Stage 1: Request Partitioning"
        REQ["prediction_request_geometry.geojson<br/>User-defined polygon"]
        PART_REQ["partition_request_geometry<br/>GridPartitioner<br/>grid_size: 0.1-1.0 degrees"]
        COARSE["Coarse Geographic Tiles"]
    end
    
    subgraph "Stage 2: Window Preparation"
        PART_WIN["prepare_window_geometries<br/>GridPartitioner<br/>grid_size: 32-1024 pixels"]
        PROJ["output_projection<br/>Projection<br/>crs, x_resolution, y_resolution"]
        WINDOWS["Processing Windows<br/>UTM or EPSG:3857"]
    end
    
    subgraph "Stage 3: Data Acquisition"
        DATASRC["data_source<br/>Sentinel2<br/>Planetary Computer"]
        QUERY["query_config<br/>period_duration, max_matches<br/>space_mode: PER_PERIOD_MOSAIC"]
        IMAGERY["Satellite Imagery<br/>Multi-temporal Bands"]
    end
    
    subgraph "Stage 4: Model Inference"
        PREDCFG["predict_config<br/>patch_size, overlap_ratio<br/>transforms"]
        MODEL["RslearnLightningModule<br/>OlmoEarth encoder<br/>Task decoder"]
        PREDS["Raw Predictions<br/>Per-window Results"]
    end
    
    subgraph "Stage 5: Post-processing"
        PROC_WIN["process_window<br/>NoopRaster"]
        PROC_PART["process_partition<br/>CombineGeotiff"]
        PROC_DS["process_dataset<br/>CombineGeotiff"]
        OUTPUT["Final GeoTIFF<br/>inference_results_config"]
    end
    
    REQ --> PART_REQ
    PART_REQ --> COARSE
    COARSE --> PART_WIN
    PART_WIN --> PROJ
    PROJ --> WINDOWS
    
    WINDOWS --> DATASRC
    DATASRC --> QUERY
    QUERY --> IMAGERY
    
    IMAGERY --> PREDCFG
    PREDCFG --> MODEL
    MODEL --> PREDS
    
    PREDS --> PROC_WIN
    PROC_WIN --> PROC_PART
    PROC_PART --> PROC_DS
    PROC_DS --> OUTPUT
```

**Sources:** [olmoearth_run_data/nandi/olmoearth_run.yaml:1-92](), [olmoearth_run_data/mangrove/model.yaml:312-339](), [olmoearth_run_data/mozambique_lulc/dataset.json:45-59]()

## Configuration Files

The pipeline requires three configuration files that work together to define the complete inference process:

| Configuration File | Purpose | Key Components |
|-------------------|---------|----------------|
| `olmoearth_run.yaml` | Pipeline execution strategy | `partition_strategies`, `postprocessing_strategies`, `inference_results_config` |
| `model.yaml` | Model architecture and inference settings | `model`, `data.predict_config`, `trainer` |
| `dataset.json` | Data source specifications | `layers`, `data_source`, `query_config` |

### Configuration File Relationships

```mermaid
graph LR
    subgraph "olmoearth_run.yaml"
        PART_STRAT["partition_strategies"]
        POST_STRAT["postprocessing_strategies"]
        INFER_CFG["inference_results_config"]
    end
    
    subgraph "model.yaml"
        MODEL_DEF["model<br/>RslearnLightningModule"]
        PRED_CFG["data.predict_config<br/>patch_size, overlap_ratio"]
        TRANSFORMS["predict_config.transforms<br/>OlmoEarthNormalize, Pad"]
    end
    
    subgraph "dataset.json"
        LAYERS["layers<br/>sentinel2, label, output"]
        DATASRC["data_source<br/>Sentinel2"]
        QUERY["query_config<br/>period_duration, space_mode"]
    end
    
    PART_STRAT --> |"defines"| PRED_CFG
    MODEL_DEF --> |"loads checkpoint"| PRED_CFG
    TRANSFORMS --> |"normalizes"| DATASRC
    QUERY --> |"specifies acquisition"| PRED_CFG
    POST_STRAT --> |"merges results"| INFER_CFG
```

**Sources:** [olmoearth_run_data/nandi/olmoearth_run.yaml:1-92](), [olmoearth_run_data/mangrove/model.yaml:1-394](), [olmoearth_run_data/mozambique_lulc/dataset.json:1-63]()

## Partition Strategies

The pipeline uses hierarchical partitioning to process large geographic areas efficiently. Partitioning is configured in the `partition_strategies` section of `olmoearth_run.yaml`.

### partition_request_geometry

The first-level partitioning divides the input geometry into coarse geographic tiles.

```mermaid
graph TB
    INPUT["Input Geometry<br/>Large Region"]
    GRID_PART["GridPartitioner<br/>class_path: olmoearth_run.runner.tools.partitioners.grid_partitioner.GridPartitioner"]
    INIT_ARGS["init_args:<br/>grid_size<br/>output_projection<br/>use_utm"]
    TILES["Coarse Tiles<br/>0.1-1.0 degree cells"]
    
    INPUT --> GRID_PART
    GRID_PART --> INIT_ARGS
    INIT_ARGS --> TILES
```

**Configuration Parameters:**

| Parameter | Type | Example Values | Description |
|-----------|------|----------------|-------------|
| `grid_size` | float | 0.1, 0.25, 1.0 | Grid cell size in degrees (lat/lon) |
| `output_projection` | Projection | EPSG:3857 | Target coordinate system |
| `use_utm` | bool | true | Use UTM projection for local accuracy |

**Example Configuration:**

[olmoearth_run_data/nandi/olmoearth_run.yaml:23-26]()
```yaml
partition_request_geometry:
  class_path: olmoearth_run.runner.tools.partitioners.grid_partitioner.GridPartitioner
  init_args:
    grid_size: 1.0
```

**Sources:** [olmoearth_run_data/nandi/olmoearth_run.yaml:22-26](), [olmoearth_run_data/awf/olmoearth_run.yaml:22-26](), [olmoearth_run_data/mozambique_lulc/olmoearth_run.yaml:50-54](), [olmoearth_run_data/mangrove/olmoearth_run.yaml:1-12]()

### prepare_window_geometries

The second-level partitioning subdivides each coarse tile into processing windows aligned to pixel boundaries.

```mermaid
graph TB
    TILE["Coarse Tile<br/>Geographic Region"]
    GRID_PART["GridPartitioner<br/>class_path: olmoearth_run.runner.tools.partitioners.grid_partitioner.GridPartitioner"]
    PARAMS["init_args:<br/>grid_size: 32-1024 pixels<br/>output_projection<br/>use_utm: true"]
    PROJ["Projection<br/>crs: EPSG:3857 or UTM<br/>x_resolution: 10<br/>y_resolution: -10"]
    WINDOWS["Processing Windows<br/>Fixed pixel dimensions"]
    
    TILE --> GRID_PART
    GRID_PART --> PARAMS
    PARAMS --> PROJ
    PROJ --> WINDOWS
```

**Configuration Parameters:**

| Parameter | Type | Example Values | Description |
|-----------|------|----------------|-------------|
| `grid_size` | int | 32, 512, 1024 | Window size in pixels |
| `output_projection.crs` | str | EPSG:3857 | Coordinate reference system |
| `output_projection.x_resolution` | float | 10 | Pixel width in meters |
| `output_projection.y_resolution` | float | -10 | Pixel height in meters (negative for north-up) |
| `use_utm` | bool | true | Auto-select appropriate UTM zone |

**Example Configuration:**

[olmoearth_run_data/nandi/olmoearth_run.yaml:28-38]()
```yaml
prepare_window_geometries:
  class_path: olmoearth_run.runner.tools.partitioners.grid_partitioner.GridPartitioner
  init_args:
    grid_size: 1024
    output_projection:
      class_path: rslearn.utils.geometry.Projection
      init_args:
        crs: EPSG:3857
        x_resolution: 10
        y_resolution: -10
    use_utm: true
```

**Sources:** [olmoearth_run_data/nandi/olmoearth_run.yaml:28-38](), [olmoearth_run_data/awf/olmoearth_run.yaml:28-38](), [olmoearth_run_data/mozambique_lulc/olmoearth_run.yaml:56-66](), [olmoearth_run_data/mangrove/olmoearth_run.yaml:14-24]()

## Data Acquisition Configuration

Data acquisition is specified in `dataset.json` and defines how satellite imagery is queried and processed for each window.

### Sentinel-2 Data Source

The pipeline queries Sentinel-2 Level 2A surface reflectance data from Microsoft Planetary Computer.

```mermaid
graph TB
    LAYER["layers.sentinel2"]
    BANDS["band_sets<br/>B01-B12 spectral bands<br/>dtype: uint16"]
    DATASRC["data_source<br/>class_path: rslearn.data_sources.planetary_computer.Sentinel2"]
    INIT["init_args:<br/>cache_dir<br/>harmonize: true<br/>sort_by: eo:cloud_cover"]
    QUERY["query_config:<br/>max_matches: 8-12<br/>min_matches: 8-12<br/>period_duration: 30d<br/>space_mode: PER_PERIOD_MOSAIC"]
    TEMPORAL["Temporal Configuration:<br/>duration: 366d<br/>time_offset: -180d"]
    
    LAYER --> BANDS
    LAYER --> DATASRC
    DATASRC --> INIT
    DATASRC --> QUERY
    DATASRC --> TEMPORAL
```

**Query Configuration Parameters:**

| Parameter | Type | Example | Description |
|-----------|------|---------|-------------|
| `max_matches` | int | 8, 12 | Maximum images per time period |
| `min_matches` | int | 8, 12 | Minimum required images |
| `period_duration` | str | "30d" | Temporal window for mosaicking |
| `space_mode` | str | "PER_PERIOD_MOSAIC" | Mosaic images within each period |
| `duration` | str | "366d" | Total time range for image collection |
| `time_offset` | str | "-180d" | Temporal offset (start before request time) |

**Example Mangrove Configuration:**

[olmoearth_run_data/mangrove/dataset.json:37-52]()
```json
"data_source": {
  "class_path": "rslearn.data_sources.planetary_computer.Sentinel2",
  "duration": "366d",
  "ingest": false,
  "init_args": {
    "cache_dir": "cache/planetary_computer",
    "harmonize": true,
    "sort_by": "eo:cloud_cover"
  },
  "query_config": {
    "max_matches": 12,
    "min_matches": 12,
    "period_duration": "30d",
    "space_mode": "PER_PERIOD_MOSAIC"
  },
  "time_offset": "-180d"
}
```

**Sources:** [olmoearth_run_data/mangrove/dataset.json:17-56](), [olmoearth_run_data/mozambique_lulc/dataset.json:25-61]()

## Model Inference Configuration

Model inference is configured in the `predict_config` section of `model.yaml` under `data.predict_config`.

### Prediction Configuration Structure

```mermaid
graph TB
    PRED_CFG["data.predict_config"]
    PATCH["patch_size: 2-16<br/>Window subdivision size"]
    OVERLAP["overlap_ratio: 0.25<br/>Patch overlap fraction"]
    LOAD["load_all_patches: true<br/>Process all patches"]
    SKIP["skip_targets: true<br/>No ground truth labels"]
    TRANS["transforms:<br/>List of transforms"]
    
    NORM["OlmoEarthNormalize<br/>class_path: rslearn.models.olmoearth_pretrain.norm.OlmoEarthNormalize<br/>band_names, std_multiplier: 2.0"]
    PAD["Pad<br/>class_path: rslearn.train.transforms.pad.Pad<br/>size, mode: center"]
    
    PRED_CFG --> PATCH
    PRED_CFG --> OVERLAP
    PRED_CFG --> LOAD
    PRED_CFG --> SKIP
    PRED_CFG --> TRANS
    TRANS --> NORM
    TRANS --> PAD
```

**Prediction Configuration Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `patch_size` | int | 2, 16 | Subdivision size for processing windows |
| `overlap_ratio` | float | 0.25, null | Overlap between adjacent patches (0.25 = 25%) |
| `load_all_patches` | bool | true | Load and process all patches in window |
| `skip_targets` | bool | true | Skip loading target labels during inference |
| `transforms` | list | - | Data transformation pipeline |

### Transform Pipeline

The transform pipeline normalizes and prepares data for model input:

**OlmoEarthNormalize Configuration:**

[olmoearth_run_data/mangrove/model.yaml:318-333]()
```yaml
- class_path: rslearn.models.olmoearth_pretrain.norm.OlmoEarthNormalize
  init_args:
    band_names:
      sentinel2_l2a:
      - B02
      - B03
      - B04
      - B08
      - B05
      - B06
      - B07
      - B8A
      - B11
      - B12
      - B01
      - B09
```

**Pad Configuration:**

[olmoearth_run_data/mangrove/model.yaml:334-338]()
```yaml
- class_path: rslearn.train.transforms.pad.Pad
  init_args:
    size: 2
    mode: "center"
    image_selectors: ["sentinel2_l2a"]
```

**Complete Predict Config Example:**

[olmoearth_run_data/mozambique_lulc/model.yaml:236-245]()
```yaml
predict_config:
  load_all_patches: true
  patch_size: 16
  overlap_ratio: 0.25  # 4 / 16
  skip_targets: true
  transforms:
    - class_path: rslearn.models.olmoearth_pretrain.norm.OlmoEarthNormalize
      init_args:
        band_names:
          sentinel2_l2a: ["B02", "B03", "B04", "B08", "B05", "B06", "B07", "B8A", "B11", "B12", "B01", "B09"]
```

**Sources:** [olmoearth_run_data/mangrove/model.yaml:312-339](), [olmoearth_run_data/mozambique_lulc/model.yaml:236-245]()

## Post-processing Strategies

Post-processing aggregates predictions from individual windows into cohesive output rasters. The pipeline executes three post-processing levels configured in `postprocessing_strategies`.

### Post-processing Levels

```mermaid
graph TB
    WINDOWS["Multiple Windows<br/>Per-window Predictions"]
    PROC_WIN["process_window<br/>NoopRaster or<br/>Window-level Processing"]
    WINDOWS_PROC["Processed Windows"]
    
    WINDOWS_PROC --> PROC_PART
    PROC_PART["process_partition<br/>CombineGeotiff<br/>Merge within Partition"]
    PART_TILES["Partition Tiles"]
    
    PART_TILES --> PROC_DS
    PROC_DS["process_dataset<br/>CombineGeotiff<br/>Final Assembly"]
    FINAL["Final Output Raster<br/>Complete Coverage"]
    
    WINDOWS --> PROC_WIN
    PROC_WIN --> WINDOWS_PROC
```

### Process Window

Window-level processing operates on individual prediction windows before aggregation. Most configurations use `NoopRaster` which performs no modification.

**Configuration:**

[olmoearth_run_data/nandi/olmoearth_run.yaml:51-52]()
```yaml
process_window:
  class_path: olmoearth_run.runner.tools.postprocessors.noop_raster.NoopRaster
```

### Process Partition

Partition-level processing combines windows within a single coarse partition tile using `CombineGeotiff`.

**Configuration:**

[olmoearth_run_data/nandi/olmoearth_run.yaml:46-49]()
```yaml
process_partition:
  class_path: olmoearth_run.runner.tools.postprocessors.combine_geotiff.CombineGeotiff
  init_args:
    nodata_value: 10
```

### Process Dataset

Dataset-level processing merges all partition tiles into the final output raster.

**Configuration:**

[olmoearth_run_data/nandi/olmoearth_run.yaml:41-44]()
```yaml
process_dataset:
  class_path: olmoearth_run.runner.tools.postprocessors.combine_geotiff.CombineGeotiff
  init_args:
    nodata_value: 10
```

**NoData Value by Model:**

| Model | NoData Value | Purpose |
|-------|--------------|---------|
| Nandi | 10 | Class index reserved for no-data |
| AWF | 9 | Class index reserved for no-data |
| Mozambique LULC | 255 | Maximum uint8 value for no-data |
| Mangrove | Not specified | Uses default CombineGeotiff behavior |

**Sources:** [olmoearth_run_data/nandi/olmoearth_run.yaml:40-52](), [olmoearth_run_data/awf/olmoearth_run.yaml:40-52](), [olmoearth_run_data/mozambique_lulc/olmoearth_run.yaml:68-80](), [olmoearth_run_data/mangrove/olmoearth_run.yaml:26-34]()

## Inference Results Configuration

The `inference_results_config` section defines how prediction outputs are structured and visualized in the final GeoTIFF.

### Classification Fields

Classification fields map integer pixel values to semantic labels with visualization colors.

```mermaid
graph TB
    INFER_CFG["inference_results_config"]
    DATA_TYPE["data_type: RASTER"]
    CLASS_FIELDS["classification_fields<br/>List of classification bands"]
    
    FIELD["Classification Field"]
    PROP["property_name<br/>Task identifier"]
    BAND["band_index: 1<br/>Output band number"]
    VALUES["allowed_values<br/>Class definitions"]
    
    VALUE_DEF["Value Definition"]
    VAL["value: int<br/>Pixel value"]
    LABEL["label: str<br/>Class name"]
    COLOR["color: [R, G, B]<br/>Visualization RGB"]
    
    INFER_CFG --> DATA_TYPE
    INFER_CFG --> CLASS_FIELDS
    CLASS_FIELDS --> FIELD
    FIELD --> PROP
    FIELD --> BAND
    FIELD --> VALUES
    VALUES --> VALUE_DEF
    VALUE_DEF --> VAL
    VALUE_DEF --> LABEL
    VALUE_DEF --> COLOR
```

### Example: Mangrove Classification

[olmoearth_run_data/mangrove/olmoearth_run.yaml:37-51]()
```yaml
inference_results_config:
  data_type: RASTER
  classification_fields:
    - property_name: classification
      band_index: 1
      allowed_values:
        - value: 1
          label: mangrove
          color: [148,235,99]
        - value: 2
          label: water
          color: [99,216,235]
        - value: 3
          label: other
          color: [235,169,99,200]
```

### Example: Multi-class Land Cover

[olmoearth_run_data/nandi/olmoearth_run.yaml:54-89]()
```yaml
inference_results_config:
  data_type: RASTER
  classification_fields:
    - property_name: segment
      band_index: 1
      allowed_values:
        - value: 0
          label: coffee
          color: [124, 67, 18]
        - value: 1
          label: grassland
          color: [169, 214, 146]
        - value: 2
          label: trees
          color: [51, 160, 44]
        # ... additional classes
```

**Classification Field Schema:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `property_name` | str | Yes | Task identifier from model output |
| `band_index` | int | Yes | Band number in output raster (1-indexed) |
| `allowed_values` | list | Yes | List of class definitions |
| `allowed_values[].value` | int | Yes | Integer pixel value |
| `allowed_values[].label` | str | Yes | Human-readable class name |
| `allowed_values[].color` | list | Yes | RGB(A) color tuple for visualization |

**Sources:** [olmoearth_run_data/mangrove/olmoearth_run.yaml:37-51](), [olmoearth_run_data/nandi/olmoearth_run.yaml:54-89](), [olmoearth_run_data/awf/olmoearth_run.yaml:54-88](), [olmoearth_run_data/mozambique_lulc/olmoearth_run.yaml:1-27]()

## Pipeline Execution Flow

The complete inference pipeline executes through these integrated components:

```mermaid
graph TB
    subgraph "Input"
        GEOM["prediction_request_geometry.geojson<br/>oe_start_time, oe_end_time"]
        RUN_CFG["olmoearth_run.yaml<br/>partition_strategies<br/>postprocessing_strategies"]
        MODEL_CFG["model.yaml<br/>model architecture<br/>predict_config"]
        DATA_CFG["dataset.json<br/>data_source<br/>query_config"]
    end
    
    subgraph "Execution Engine"
        PART1["GridPartitioner.partition_request_geometry<br/>Create coarse tiles"]
        PART2["GridPartitioner.prepare_window_geometries<br/>Create processing windows"]
        QUERY["Sentinel2.query<br/>Planetary Computer API"]
        MOSAIC["PER_PERIOD_MOSAIC<br/>Temporal aggregation"]
        LOAD["RslearnLightningModule.load<br/>Load model checkpoint"]
        PREDICT["RslearnLightningModule.predict<br/>Batch inference"]
        PP_WIN["NoopRaster.process_window"]
        PP_PART["CombineGeotiff.process_partition"]
        PP_DS["CombineGeotiff.process_dataset"]
    end
    
    subgraph "Output"
        GEOTIFF["output.tif<br/>Classification raster"]
        METADATA["inference_results_config<br/>Class mappings, colors"]
    end
    
    GEOM --> PART1
    RUN_CFG --> PART1
    PART1 --> PART2
    RUN_CFG --> PART2
    
    PART2 --> QUERY
    DATA_CFG --> QUERY
    QUERY --> MOSAIC
    DATA_CFG --> MOSAIC
    
    MOSAIC --> LOAD
    MODEL_CFG --> LOAD
    LOAD --> PREDICT
    MODEL_CFG --> PREDICT
    
    PREDICT --> PP_WIN
    RUN_CFG --> PP_WIN
    PP_WIN --> PP_PART
    RUN_CFG --> PP_PART
    PP_PART --> PP_DS
    RUN_CFG --> PP_DS
    
    PP_DS --> GEOTIFF
    RUN_CFG --> METADATA
    METADATA --> GEOTIFF
```

**Key Processing Classes:**

| Class | Module | Purpose |
|-------|--------|---------|
| `GridPartitioner` | `olmoearth_run.runner.tools.partitioners.grid_partitioner` | Spatial partitioning of regions |
| `Sentinel2` | `rslearn.data_sources.planetary_computer` | Satellite data acquisition |
| `RslearnLightningModule` | `rslearn.train.lightning_module` | Model loading and inference |
| `OlmoEarthNormalize` | `rslearn.models.olmoearth_pretrain.norm` | Data normalization |
| `NoopRaster` | `olmoearth_run.runner.tools.postprocessors.noop_raster` | Pass-through window processing |
| `CombineGeotiff` | `olmoearth_run.runner.tools.postprocessors.combine_geotiff` | Raster merging and mosaicking |

**Sources:** [olmoearth_run_data/nandi/olmoearth_run.yaml:1-92](), [olmoearth_run_data/mangrove/model.yaml:1-394](), [olmoearth_run_data/mozambique_lulc/dataset.json:1-63]()

## Configuration Examples by Model

### Mangrove Model Configuration

**Partitioning Strategy:**
- Coarse partitioning: 0.1 degree grid
- Fine partitioning: 32 pixel windows
- Projection: EPSG:3857, 10m resolution, UTM

**Data Acquisition:**
- Duration: 366 days
- Time offset: -180 days (6 months before request)
- Period duration: 30 days
- Images per period: 12

**Model Inference:**
- Patch size: 2
- Overlap ratio: Not specified
- Transforms: OlmoEarthNormalize, Pad (size 2)

**Sources:** [olmoearth_run_data/mangrove/olmoearth_run.yaml:1-51](), [olmoearth_run_data/mangrove/model.yaml:312-339](), [olmoearth_run_data/mangrove/dataset.json:37-56]()

### Mozambique LULC Configuration

**Partitioning Strategy:**
- Coarse partitioning: 0.25 degree grid
- Fine partitioning: 1024 pixel windows
- Projection: EPSG:3857, 10m resolution, UTM

**Data Acquisition:**
- Period duration: 30 days
- Images per period: 8
- Space mode: PER_PERIOD_MOSAIC

**Model Inference:**
- Patch size: 16
- Overlap ratio: 0.25 (4 pixel overlap)
- Transforms: OlmoEarthNormalize

**Post-processing:**
- NoData value: 255
- All levels: CombineGeotiff

**Sources:** [olmoearth_run_data/mozambique_lulc/olmoearth_run.yaml:1-81](), [olmoearth_run_data/mozambique_lulc/model.yaml:236-245](), [olmoearth_run_data/mozambique_lulc/dataset.json:45-59]()

### Nandi Crop Classification Configuration

**Partitioning Strategy:**
- Coarse partitioning: 1.0 degree grid
- Fine partitioning: 1024 pixel windows
- Projection: EPSG:3857, 10m resolution, UTM

**Post-processing:**
- NoData value: 10
- All levels use CombineGeotiff
- Window level: NoopRaster

**Classification Output:**
- 10 classes: coffee, grassland, trees, maize, sugarcane, tea, vegetables, legumes, water, builtup
- RGB colors for each class
- Property name: "segment"

**Sources:** [olmoearth_run_data/nandi/olmoearth_run.yaml:1-92]()

---

# Page: Prediction Request Geometries

# Prediction Request Geometries

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/awf.md](docs/awf.md)
- [docs/nandi.md](docs/nandi.md)
- [olmoearth_projects/projects/mozambique_lulc/__init__.py](olmoearth_projects/projects/mozambique_lulc/__init__.py)
- [olmoearth_projects/projects/mozambique_lulc/create_label_raster.py](olmoearth_projects/projects/mozambique_lulc/create_label_raster.py)
- [olmoearth_projects/projects/mozambique_lulc/create_windows_for_lulc.py](olmoearth_projects/projects/mozambique_lulc/create_windows_for_lulc.py)
- [olmoearth_projects/projects/mozambique_lulc/update_train_test_split.py](olmoearth_projects/projects/mozambique_lulc/update_train_test_split.py)
- [olmoearth_run_data/mozambique_lulc/prediction_request_geometry.geojson](olmoearth_run_data/mozambique_lulc/prediction_request_geometry.geojson)
- [olmoearth_run_data/nandi/prediction_request_geometry.geojson](olmoearth_run_data/nandi/prediction_request_geometry.geojson)

</details>



## Purpose and Scope

This document explains the structure and usage of prediction request geometries, which are GeoJSON files that define the spatial and temporal extent for running inference with trained OlmoEarth models. These files serve as the primary input to the olmoearth_run inference pipeline and specify both where and when to generate predictions.

For information about the overall inference pipeline that consumes these geometries, see [olmoearth_run Pipeline](#7.1). For details on how these geometries are partitioned into processing units, see [Partitioning and Grid Processing](#7.3).

**Sources:** [olmoearth_run_data/mozambique_lulc/prediction_request_geometry.geojson:1-39](), [olmoearth_run_data/nandi/prediction_request_geometry.geojson:1-39]()

## GeoJSON File Structure

Prediction request geometries follow the GeoJSON specification with additional OlmoEarth-specific properties. Each file contains a `FeatureCollection` with one or more `Feature` objects that define spatial polygons and their associated temporal properties.

```mermaid
graph TB
    subgraph "GeoJSON Structure"
        ROOT["FeatureCollection<br/>(root object)"]
        FEATURES["features array"]
        FEATURE["Feature object"]
        GEOMETRY["geometry object<br/>type: Polygon"]
        COORDS["coordinates array<br/>(lon, lat pairs)"]
        PROPS["properties object"]
        START["oe_start_time<br/>(ISO 8601 string)"]
        END["oe_end_time<br/>(ISO 8601 string)"]
    end
    
    ROOT --> FEATURES
    FEATURES --> FEATURE
    FEATURE --> GEOMETRY
    FEATURE --> PROPS
    GEOMETRY --> COORDS
    PROPS --> START
    PROPS --> END
```

**Sources:** [olmoearth_run_data/mozambique_lulc/prediction_request_geometry.geojson:1-39](), [olmoearth_run_data/nandi/prediction_request_geometry.geojson:1-39]()

### Spatial Component

The spatial extent is defined by a GeoJSON `Polygon` geometry with coordinates in WGS84 (EPSG:4326) projection. Coordinates are specified as `[longitude, latitude]` pairs forming a closed polygon.

| Field | Type | Description |
|-------|------|-------------|
| `type` | string | Must be `"Polygon"` |
| `coordinates` | array | Array of linear rings, where first ring is exterior boundary |
| Coordinate format | `[number, number]` | `[longitude, latitude]` in decimal degrees |

**Example from Mozambique LULC:**
```json
"geometry": {
  "coordinates": [
    [
      [33.66473812697805, -25.14037394430332],
      [33.66473812697805, -25.145788014726122],
      [33.67009152455876, -25.145788014726122],
      [33.67009152455876, -25.14037394430332],
      [33.66473812697805, -25.14037394430332]
    ]
  ],
  "type": "Polygon"
}
```

**Sources:** [olmoearth_run_data/mozambique_lulc/prediction_request_geometry.geojson:4-29]()

### Temporal Component

The temporal extent is specified through two required properties that define the start and end times for data acquisition.

| Property | Format | Description |
|----------|--------|-------------|
| `oe_start_time` | ISO 8601 string | Start of temporal window (UTC) |
| `oe_end_time` | ISO 8601 string | End of temporal window (UTC) |

Both timestamps must be in ISO 8601 format with timezone specification (typically UTC). The time range determines which satellite imagery timesteps will be queried and mosaicked during inference.

**Example temporal properties:**
```json
"properties": {
  "oe_start_time": "2024-10-23T00:00:00+00:00",
  "oe_end_time": "2025-05-07T00:00:00+00:00"
}
```

**Sources:** [olmoearth_run_data/mozambique_lulc/prediction_request_geometry.geojson:31-34](), [olmoearth_run_data/nandi/prediction_request_geometry.geojson:31-34]()

## Temporal Ranges by Model

Different models are trained on specific temporal configurations and require appropriate time ranges for optimal inference results. The following table summarizes recommended temporal ranges for each model type:

| Model | Training Period | Recommended Range Duration | Example Period |
|-------|----------------|---------------------------|----------------|
| Mozambique LULC | 2024-10 to 2025-06 | ~7 months (seasonal) | 2024-10-23 to 2025-06-20 |
| Mozambique Crop Type | 2024-10 to 2025-06 | ~7 months (seasonal) | 2024-10-23 to 2025-06-20 |
| Nandi Crop | 2022-09 to 2023-09 | 12 months (annual) | Any 12-month period |
| AWF Land Cover | 2023-01 to 2023-12 | 12 months (annual) | 2023-01-01 to 2023-12-31 |

The temporal ranges defined during training are stored in project-specific constants. For example, the Mozambique LULC project defines per-province temporal coverage in the `GROUP_TIME` dictionary:

```python
GROUP_TIME = {
    "gaza": (
        datetime(2024, 10, 23, tzinfo=UTC),
        datetime(2025, 6, 20, tzinfo=UTC),
    ),
    "manica": (
        datetime(2024, 10, 23, tzinfo=UTC),
        datetime(2025, 6, 20, tzinfo=UTC),
    ),
    "zambezia": (
        datetime(2024, 10, 23, tzinfo=UTC),
        datetime(2025, 6, 20, tzinfo=UTC),
    ),
}
```

**Sources:** [olmoearth_projects/projects/mozambique_lulc/create_windows_for_lulc.py:53-74](), [docs/nandi.md:41](), [docs/awf.md:38]()

## Complete File Examples

### Mozambique LULC Example

The Mozambique LULC prediction request geometry defines a small area in Gaza province with seasonal temporal coverage:

```json
{
  "features": [
    {
      "geometry": {
        "coordinates": [
          [
            [33.66473812697805, -25.14037394430332],
            [33.66473812697805, -25.145788014726122],
            [33.67009152455876, -25.145788014726122],
            [33.67009152455876, -25.14037394430332],
            [33.66473812697805, -25.14037394430332]
          ]
        ],
        "type": "Polygon"
      },
      "properties": {
        "oe_end_time": "2025-05-07T00:00:00+00:00",
        "oe_start_time": "2024-10-23T00:00:00+00:00"
      },
      "type": "Feature"
    }
  ],
  "type": "FeatureCollection"
}
```

This geometry covers approximately 0.0054 degrees longitude by 0.0054 degrees latitude (~600m × 600m at this latitude).

**Sources:** [olmoearth_run_data/mozambique_lulc/prediction_request_geometry.geojson:1-39]()

### Nandi County Example

The Nandi prediction request geometry covers the entire county with annual temporal coverage:

```json
{
  "features": [
    {
      "geometry": {
        "coordinates": [
          [
            [34.725547461183425, 0.5677064073714604],
            [34.725547461183425, -0.1240714566526151],
            [35.481933382330055, -0.1240714566526151],
            [35.481933382330055, 0.5677064073714604],
            [34.725547461183425, 0.5677064073714604]
          ]
        ],
        "type": "Polygon"
      },
      "properties": {
        "oe_end_time": "2022-09-01T00:00:00Z",
        "oe_start_time": "2023-09-01T00:00:00Z"
      },
      "type": "Feature"
    }
  ],
  "type": "FeatureCollection"
}
```

This geometry covers approximately 0.76 degrees longitude by 0.69 degrees latitude (~84 km × 77 km), encompassing the full county area.

**Sources:** [olmoearth_run_data/nandi/prediction_request_geometry.geojson:1-39]()

## Integration with Inference Pipeline

Prediction request geometries serve as the entry point to the olmoearth_run inference pipeline. The pipeline processes these geometries through several stages:

```mermaid
graph LR
    GEOJSON["prediction_request_geometry.geojson<br/>Polygon + timestamps"]
    PARTITION["partition_request_geometry<br/>GridPartitioner<br/>Coarse grid: 0.1-1.0°"]
    WINDOWS["prepare_window_geometries<br/>GridPartitioner<br/>Fine grid: 32-1024 pixels"]
    QUERY["Data Source Query<br/>Microsoft Planetary Computer<br/>oe_start_time → oe_end_time"]
    MOSAIC["Temporal Mosaicking<br/>30-day periods<br/>12 timesteps"]
    INFERENCE["Model Inference<br/>Per-window predictions"]
    
    GEOJSON --> PARTITION
    PARTITION --> WINDOWS
    WINDOWS --> QUERY
    QUERY --> MOSAIC
    MOSAIC --> INFERENCE
```

**Sources:** [olmoearth_run_data/mozambique_lulc/prediction_request_geometry.geojson:1-39](), [olmoearth_run_data/nandi/prediction_request_geometry.geojson:1-39]()

### Partitioning Process

The inference pipeline reads the prediction request geometry and partitions it hierarchically:

1. **Coarse Partitioning**: The polygon is divided into coarse grid cells (0.1-1.0 degrees) using `partition_request_geometry`
2. **Fine Partitioning**: Each coarse partition is subdivided into processing windows (32-1024 pixels) using `prepare_window_geometries`
3. **Projection Selection**: Windows are projected to UTM or EPSG:3857 at 10m resolution for processing

The temporal properties (`oe_start_time` and `oe_end_time`) are preserved through all partitioning stages and used to query satellite data for each processing window.

**Sources:** [olmoearth_run_data/mozambique_lulc/prediction_request_geometry.geojson:31-34]()

### Data Acquisition

The temporal extent defined in the prediction request geometry determines which satellite imagery is retrieved:

1. **Query Period**: Data sources are queried for the period from `oe_start_time` to `oe_end_time`
2. **Temporal Mosaicking**: Imagery is aggregated into 30-day periods, creating 6-12 timesteps depending on the total duration
3. **Data Source**: Sentinel-2 L2A imagery is retrieved from Microsoft Planetary Computer

For example, a geometry with 12-month temporal range (`2022-09-01` to `2023-09-01`) results in 12 monthly mosaics, each representing one 30-day period.

**Sources:** [docs/nandi.md:14](), [docs/nandi.md:35](), [docs/awf.md:14](), [docs/awf.md:33]()

## Creating Prediction Request Geometries

### Manual Creation

Prediction request geometries can be created manually using any GeoJSON editor or programmatically. The minimal required structure is:

1. Define a polygon in WGS84 coordinates
2. Add `oe_start_time` property in ISO 8601 format with timezone
3. Add `oe_end_time` property in ISO 8601 format with timezone
4. Wrap in a FeatureCollection structure

### Coordinate System Requirements

```mermaid
graph TB
    WGS84["Input Geometry<br/>EPSG:4326 (WGS84)<br/>Decimal degrees"]
    PARTITION["Partitioning Stage<br/>Coarse grid generation"]
    UTM["Window Projection<br/>UTM or EPSG:3857<br/>10m resolution"]
    SENTINEL["Sentinel-2 Query<br/>Native CRS varies by tile"]
    
    WGS84 --> PARTITION
    PARTITION --> UTM
    UTM --> SENTINEL
    
    style WGS84 fill:#f9f9f9
    style UTM fill:#f9f9f9
```

All prediction request geometries must use WGS84 (EPSG:4326) projection with longitude/latitude coordinates. The inference pipeline handles projection transformations internally when creating processing windows.

**Sources:** [olmoearth_projects/projects/mozambique_lulc/create_windows_for_lulc.py:171-175]()

### Validation Checklist

Before using a prediction request geometry for inference, verify:

| Check | Requirement |
|-------|------------|
| Valid GeoJSON | Parseable as GeoJSON FeatureCollection |
| Geometry type | Polygon with closed ring |
| Coordinate order | `[longitude, latitude]` not `[latitude, longitude]` |
| Coordinate range | Longitude: -180 to 180, Latitude: -90 to 90 |
| Temporal format | ISO 8601 with timezone (e.g., `+00:00` or `Z`) |
| Temporal order | `oe_start_time` < `oe_end_time` |
| Property names | Exactly `oe_start_time` and `oe_end_time` (case-sensitive) |

**Sources:** [olmoearth_run_data/mozambique_lulc/prediction_request_geometry.geojson:1-39](), [olmoearth_run_data/nandi/prediction_request_geometry.geojson:1-39]()

## File Location and Naming Convention

Prediction request geometries are stored in the `olmoearth_run_data/` directory hierarchy, organized by project:

```
olmoearth_run_data/
├── mozambique_lulc/
│   └── prediction_request_geometry.geojson
├── nandi/
│   └── prediction_request_geometry.geojson
└── awf/
    └── prediction_request_geometry.geojson
```

The standard filename is `prediction_request_geometry.geojson`, placed in the project-specific subdirectory alongside other inference configuration files like `olmoearth_run.yaml`.

**Sources:** [olmoearth_run_data/mozambique_lulc/prediction_request_geometry.geojson:1](), [olmoearth_run_data/nandi/prediction_request_geometry.geojson:1]()

---

# Page: Partitioning and Grid Processing

# Partitioning and Grid Processing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [olmoearth_run_data/awf/olmoearth_run.yaml](olmoearth_run_data/awf/olmoearth_run.yaml)
- [olmoearth_run_data/mozambique_lulc/dataset.json](olmoearth_run_data/mozambique_lulc/dataset.json)
- [olmoearth_run_data/mozambique_lulc/model.yaml](olmoearth_run_data/mozambique_lulc/model.yaml)
- [olmoearth_run_data/mozambique_lulc/olmoearth_run.yaml](olmoearth_run_data/mozambique_lulc/olmoearth_run.yaml)
- [olmoearth_run_data/nandi/olmoearth_run.yaml](olmoearth_run_data/nandi/olmoearth_run.yaml)

</details>



This document explains the hierarchical partitioning strategies used by the olmoearth_run inference pipeline to divide large geographic areas into manageable processing units. The system uses a two-stage approach: coarse geographic partitioning followed by fine-grained window-level processing grids. This enables efficient parallel processing of predictions over large regions while managing memory constraints and data access patterns.

For information about the overall inference pipeline, see [olmoearth_run Pipeline](#7.1). For details about post-processing and result aggregation, see [Post-processing and Output](#7.4).

## Overview of Hierarchical Partitioning

The olmoearth_run pipeline uses a hierarchical partitioning strategy to decompose large prediction requests into smaller, processable units. This two-stage approach balances computational efficiency, memory usage, and data locality.

```mermaid
graph TB
    REQUEST["User Request Geometry<br/>prediction_request_geometry.geojson<br/>Entire AOI"]
    
    STAGE1["Stage 1: partition_request_geometry<br/>GridPartitioner<br/>grid_size: 0.25-1.0 degrees"]
    
    PARTITIONS["Coarse Partitions<br/>Geographic Tiles<br/>~28km to 111km per side"]
    
    STAGE2["Stage 2: prepare_window_geometries<br/>GridPartitioner<br/>grid_size: 32-1024 pixels"]
    
    WINDOWS["Processing Windows<br/>Fixed Pixel Grid<br/>10m resolution"]
    
    INFERENCE["Model Inference<br/>Per-Window Processing<br/>overlap_ratio: 0.25"]
    
    REQUEST --> STAGE1
    STAGE1 --> PARTITIONS
    PARTITIONS --> STAGE2
    STAGE2 --> WINDOWS
    WINDOWS --> INFERENCE
    
    style STAGE1 fill:#f0f0f0
    style STAGE2 fill:#f0f0f0
```

**Diagram: Two-Stage Hierarchical Partitioning Flow**

The first stage divides the request geometry into coarse geographic tiles (partitions) using latitude/longitude coordinates. The second stage subdivides each partition into pixel-aligned processing windows in a projected coordinate system. This hierarchy enables:

- **Parallel Processing**: Each partition can be processed independently
- **Memory Management**: Window sizes are bounded to fit in GPU/CPU memory
- **Data Locality**: Coarse partitions group spatially adjacent windows for efficient data access
- **Overlap Handling**: Window-level overlaps ensure seamless boundaries in final outputs

**Sources:** [olmoearth_run_data/nandi/olmoearth_run.yaml:22-38](), [olmoearth_run_data/mozambique_lulc/olmoearth_run.yaml:50-66]()

## Stage 1: Coarse Geographic Partitioning

The first partitioning stage uses `partition_request_geometry` to divide the user's area of interest into coarse geographic tiles using latitude/longitude coordinates.

### GridPartitioner Configuration

The coarse partitioning is controlled by the `partition_strategies.partition_request_geometry` section in `olmoearth_run.yaml`:

```yaml
partition_strategies:
  partition_request_geometry:
    class_path: olmoearth_run.runner.tools.partitioners.grid_partitioner.GridPartitioner
    init_args:
      grid_size: 0.25  # to 1.0 degrees
```

| Parameter | Description | Typical Values | Purpose |
|-----------|-------------|----------------|---------|
| `grid_size` | Size of partition tiles in degrees | 0.25, 0.5, 1.0 | Controls partition granularity |
| `class_path` | GridPartitioner implementation | `grid_partitioner.GridPartitioner` | Provides regular grid partitioning |

**Sources:** [olmoearth_run_data/mozambique_lulc/olmoearth_run.yaml:51-54](), [olmoearth_run_data/nandi/olmoearth_run.yaml:23-26](), [olmoearth_run_data/awf/olmoearth_run.yaml:23-26]()

### Grid Size Selection

The choice of `grid_size` depends on the geographic extent and processing requirements:

| grid_size | Approximate Width | Use Case |
|-----------|------------------|----------|
| 0.25° | ~28 km at equator | Small areas, high-resolution outputs |
| 0.5° | ~56 km at equator | Medium areas, balanced processing |
| 1.0° | ~111 km at equator | Large areas, continent-scale inference |

Smaller grid sizes create more partitions, enabling finer-grained parallelism but increasing coordination overhead. Larger grid sizes reduce the number of partitions but may increase memory requirements per partition.

**Sources:** [olmoearth_run_data/mozambique_lulc/olmoearth_run.yaml:54](), [olmoearth_run_data/nandi/olmoearth_run.yaml:26](), [olmoearth_run_data/awf/olmoearth_run.yaml:26]()

### Partition Geometry

```mermaid
graph LR
    AOI["Area of Interest<br/>Irregular Polygon<br/>User-defined bounds"]
    
    GRID["Regular Grid<br/>grid_size degrees<br/>Lat/Lon aligned"]
    
    P1["Partition 1<br/>[-10.0, -9.75]<br/>[30.0, 30.25]"]
    P2["Partition 2<br/>[-10.0, -9.75]<br/>[30.25, 30.5]"]
    P3["Partition 3<br/>[-9.75, -9.5]<br/>[30.0, 30.25]"]
    P4["Partition 4<br/>[-9.75, -9.5]<br/>[30.25, 30.5]"]
    
    AOI --> GRID
    GRID --> P1
    GRID --> P2
    GRID --> P3
    GRID --> P4
    
    style GRID fill:#f0f0f0
```

**Diagram: Geographic Grid Partitioning Example (grid_size=0.25)**

The `GridPartitioner` creates a regular grid aligned to latitude/longitude coordinates. Each partition is bounded by `[lat_min, lat_max]` and `[lon_min, lon_max]`. Partitions that intersect the user's area of interest are included in processing.

**Sources:** [olmoearth_run_data/nandi/olmoearth_run.yaml:23-26]()

## Stage 2: Window-Level Processing Grid

The second partitioning stage uses `prepare_window_geometries` to subdivide each coarse partition into pixel-aligned processing windows in a projected coordinate system.

### Window Grid Configuration

The window-level partitioning is controlled by the `partition_strategies.prepare_window_geometries` section:

```yaml
partition_strategies:
  prepare_window_geometries:
    class_path: olmoearth_run.runner.tools.partitioners.grid_partitioner.GridPartitioner
    init_args:
      grid_size: 1024  # pixels
      output_projection:
        class_path: rslearn.utils.geometry.Projection
        init_args:
          crs: EPSG:3857  # Web Mercator
          x_resolution: 10  # meters
          y_resolution: -10  # meters (negative = north-up)
      use_utm: true
```

| Parameter | Description | Values |
|-----------|-------------|--------|
| `grid_size` | Window size in pixels | 32, 64, 128, 256, 512, 1024 |
| `crs` | Coordinate reference system | EPSG:3857 (Web Mercator), or UTM |
| `x_resolution` | East-west pixel size in meters | 10 |
| `y_resolution` | North-south pixel size in meters | -10 (negative for north-up) |
| `use_utm` | Enable automatic UTM zone selection | true/false |

**Sources:** [olmoearth_run_data/nandi/olmoearth_run.yaml:28-38](), [olmoearth_run_data/mozambique_lulc/olmoearth_run.yaml:56-66](), [olmoearth_run_data/awf/olmoearth_run.yaml:28-38]()

### Window Size Selection

The `grid_size` parameter determines the processing window dimensions:

| grid_size (pixels) | Physical Size at 10m | Memory Footprint | Use Case |
|-------------------|---------------------|------------------|----------|
| 32 | 320m × 320m | ~6 MB per window | Testing, small models |
| 64 | 640m × 640m | ~24 MB per window | Memory-constrained environments |
| 128 | 1.28km × 1.28km | ~98 MB per window | Standard processing |
| 256 | 2.56km × 2.56km | ~393 MB per window | GPU-accelerated inference |
| 512 | 5.12km × 5.12km | ~1.6 GB per window | High-memory systems |
| 1024 | 10.24km × 10.24km | ~6.3 GB per window | Maximum efficiency |

Memory footprint assumes 12 Sentinel-2 bands × 8 timesteps × 2 bytes (uint16) per pixel. Actual memory usage includes model activations and temporary buffers.

**Sources:** [olmoearth_run_data/nandi/olmoearth_run.yaml:31](), [olmoearth_run_data/mozambique_lulc/olmoearth_run.yaml:59]()

### Window Grid Alignment

```mermaid
graph TB
    PARTITION["Coarse Partition<br/>Geographic Bounds<br/>Lat/Lon coordinates"]
    
    TRANSFORM["Project to CRS<br/>EPSG:3857 or UTM<br/>Metric coordinates"]
    
    SNAP["Snap to Grid<br/>grid_size × resolution<br/>Aligned boundaries"]
    
    W1["Window 1<br/>[0, 1024] pixels<br/>[0m, 10240m]"]
    W2["Window 2<br/>[1024, 2048] pixels<br/>[10240m, 20480m]"]
    W3["Window 3<br/>[0, 1024] pixels<br/>[10240m, 20480m]"]
    W4["Window 4<br/>[1024, 2048] pixels<br/>[10240m, 20480m]"]
    
    PARTITION --> TRANSFORM
    TRANSFORM --> SNAP
    SNAP --> W1
    SNAP --> W2
    SNAP --> W3
    SNAP --> W4
    
    style TRANSFORM fill:#f0f0f0
    style SNAP fill:#f0f0f0
```

**Diagram: Window Grid Creation from Partition**

Windows are created by:
1. Projecting the partition bounds to the output CRS
2. Snapping to a regular grid aligned to `grid_size × resolution`
3. Creating non-overlapping windows that tile the partition
4. Storing window geometries for data acquisition and inference

**Sources:** [olmoearth_run_data/nandi/olmoearth_run.yaml:28-38]()

## Output Projection and Resolution

### Projection Configuration

The `output_projection` defines the coordinate reference system and spatial resolution for processing windows:

```mermaid
graph LR
    PROJ_CONFIG["output_projection<br/>Projection class"]
    
    CRS["crs: EPSG:3857<br/>Web Mercator<br/>or UTM"]
    RES_X["x_resolution: 10<br/>East-West<br/>meters per pixel"]
    RES_Y["y_resolution: -10<br/>North-South<br/>meters per pixel"]
    
    PROJ_CONFIG --> CRS
    PROJ_CONFIG --> RES_X
    PROJ_CONFIG --> RES_Y
    
    CRS --> WINDOWS["Processing Windows<br/>Projected coordinates<br/>Pixel-aligned"]
    RES_X --> WINDOWS
    RES_Y --> WINDOWS
    
    style PROJ_CONFIG fill:#f0f0f0
```

**Diagram: Output Projection Configuration**

**Sources:** [olmoearth_run_data/nandi/olmoearth_run.yaml:32-37](), [olmoearth_run_data/mozambique_lulc/olmoearth_run.yaml:60-65]()

### Coordinate Reference Systems

Two projection strategies are supported:

#### EPSG:3857 (Web Mercator)

Used when `use_utm: false` or not specified:
- Global coverage without zone boundaries
- Compatible with web mapping libraries
- Distortion increases away from equator
- Suitable for near-equatorial regions

#### Automatic UTM Selection

Used when `use_utm: true`:
- Selects appropriate UTM zone based on partition centroid
- Minimal distortion within each zone
- Preserves distances and areas accurately
- Recommended for high-accuracy applications

**Sources:** [olmoearth_run_data/nandi/olmoearth_run.yaml:38](), [olmoearth_run_data/mozambique_lulc/olmoearth_run.yaml:66]()

### Resolution Parameters

The resolution defines the physical size of each pixel:

| Parameter | Value | Interpretation |
|-----------|-------|----------------|
| `x_resolution` | 10 | 10 meters east-west per pixel |
| `y_resolution` | -10 | 10 meters north-south per pixel (negative = north-up) |

The negative `y_resolution` ensures north-up orientation, matching standard GIS conventions. All models in this repository use 10-meter resolution to align with Sentinel-2 bands.

**Sources:** [olmoearth_run_data/nandi/olmoearth_run.yaml:35-37](), [olmoearth_run_data/mozambique_lulc/olmoearth_run.yaml:63-65]()

## UTM Zone Selection

When `use_utm: true`, the system automatically selects the appropriate UTM zone for each partition.

### UTM Zone Selection Process

```mermaid
graph TB
    PARTITION["Partition Bounds<br/>Lat/Lon coordinates"]
    
    CENTROID["Calculate Centroid<br/>Center point<br/>of partition"]
    
    ZONE_CALC["Determine UTM Zone<br/>zone = floor((lon + 180) / 6) + 1<br/>hemisphere from lat"]
    
    PROJECT["Create Projection<br/>EPSG:326xx (North)<br/>EPSG:327xx (South)"]
    
    WINDOWS["Window Geometries<br/>In selected UTM zone<br/>Consistent within partition"]
    
    PARTITION --> CENTROID
    CENTROID --> ZONE_CALC
    ZONE_CALC --> PROJECT
    PROJECT --> WINDOWS
    
    style ZONE_CALC fill:#f0f0f0
    style PROJECT fill:#f0f0f0
```

**Diagram: Automatic UTM Zone Selection**

### UTM Zone Properties

UTM zones provide:
- **Accurate Measurements**: Distances and areas are preserved within each zone
- **6-Degree Zones**: Each zone covers 6 degrees of longitude
- **North/South Variants**: Separate EPSG codes for northern (326xx) and southern (327xx) hemispheres
- **Consistent Within Partition**: All windows in a partition use the same UTM zone

### Zone Boundaries

```mermaid
graph LR
    LARGE_AOI["Large AOI<br/>Spans multiple UTM zones"]
    
    P1["Partition 1<br/>-12° to -11.75°<br/>UTM Zone 36S"]
    P2["Partition 2<br/>-11.75° to -11.5°<br/>UTM Zone 36S"]
    P3["Partition 3<br/>-11.5° to -11.25°<br/>UTM Zone 37S"]
    P4["Partition 4<br/>-11.25° to -11°<br/>UTM Zone 37S"]
    
    LARGE_AOI --> P1
    LARGE_AOI --> P2
    LARGE_AOI --> P3
    LARGE_AOI --> P4
    
    P1 --> ZONE36["UTM 36S<br/>Consistent projection<br/>for partitions 1-2"]
    P2 --> ZONE36
    P3 --> ZONE37["UTM 37S<br/>Consistent projection<br/>for partitions 3-4"]
    P4 --> ZONE37
    
    style ZONE36 fill:#f0f0f0
    style ZONE37 fill:#f0f0f0
```

**Diagram: UTM Zone Assignment Across Partitions**

When an area of interest spans multiple UTM zones, the coarse partitioning ensures each partition falls predominantly within a single zone. This avoids projection distortion at zone boundaries.

**Sources:** [olmoearth_run_data/nandi/olmoearth_run.yaml:38](), [olmoearth_run_data/mozambique_lulc/olmoearth_run.yaml:66]()

## Window Overlap for Inference

While window grids are created as non-overlapping tiles, the model inference stage processes windows with overlap to ensure smooth boundaries in predictions.

### Overlap Configuration

The overlap is configured in the model's `predict_config` section:

| Parameter | Value | Effect |
|-----------|-------|--------|
| `patch_size` | 16 | Each inference patch is 16×16 pixels |
| `overlap_ratio` | 0.25 | 25% overlap between patches (4 pixels) |

```mermaid
graph TB
    WINDOW["Processing Window<br/>1024 × 1024 pixels<br/>Non-overlapping tile"]
    
    PATCHES["Patch Grid<br/>patch_size: 16 pixels<br/>overlap_ratio: 0.25"]
    
    PATCH1["Patch [0:16, 0:16]<br/>16×16 pixels"]
    PATCH2["Patch [12:28, 0:16]<br/>16×16 pixels<br/>4-pixel overlap"]
    PATCH3["Patch [24:40, 0:16]<br/>16×16 pixels<br/>4-pixel overlap"]
    
    MERGE["Merge Predictions<br/>Average overlapping regions<br/>Smooth boundaries"]
    
    WINDOW --> PATCHES
    PATCHES --> PATCH1
    PATCHES --> PATCH2
    PATCHES --> PATCH3
    PATCH1 --> MERGE
    PATCH2 --> MERGE
    PATCH3 --> MERGE
    
    style PATCHES fill:#f0f0f0
    style MERGE fill:#f0f0f0
```

**Diagram: Patch-Level Overlap Within Windows**

The overlap ensures:
- **Smooth Boundaries**: Predictions are averaged at patch edges
- **Context Preservation**: Border pixels have full receptive field coverage
- **Quality Consistency**: No discontinuities at window boundaries

**Sources:** [olmoearth_run_data/mozambique_lulc/model.yaml:237-239]()

## Configuration Examples

### Example 1: Small Area, High Resolution

For detailed mapping of a small region (e.g., 10km × 10km):

```yaml
partition_strategies:
  partition_request_geometry:
    class_path: olmoearth_run.runner.tools.partitioners.grid_partitioner.GridPartitioner
    init_args:
      grid_size: 0.25  # Small partitions for fine control
      
  prepare_window_geometries:
    class_path: olmoearth_run.runner.tools.partitioners.grid_partitioner.GridPartitioner
    init_args:
      grid_size: 256  # Smaller windows for detailed processing
      output_projection:
        class_path: rslearn.utils.geometry.Projection
        init_args:
          crs: EPSG:3857
          x_resolution: 10
          y_resolution: -10
      use_utm: true
```

**Sources:** [olmoearth_run_data/mozambique_lulc/olmoearth_run.yaml:50-66]()

### Example 2: Large Area, Efficient Processing

For continental-scale inference (e.g., 500km × 500km):

```yaml
partition_strategies:
  partition_request_geometry:
    class_path: olmoearth_run.runner.tools.partitioners.grid_partitioner.GridPartitioner
    init_args:
      grid_size: 1.0  # Large partitions for fewer tiles
      
  prepare_window_geometries:
    class_path: olmoearth_run.runner.tools.partitioners.grid_partitioner.GridPartitioner
    init_args:
      grid_size: 1024  # Large windows for GPU efficiency
      output_projection:
        class_path: rslearn.utils.geometry.Projection
        init_args:
          crs: EPSG:3857
          x_resolution: 10
          y_resolution: -10
      use_utm: true
```

**Sources:** [olmoearth_run_data/nandi/olmoearth_run.yaml:22-38]()

## Integration with Pipeline Stages

The partitioning system integrates with other pipeline stages:

```mermaid
graph TB
    REQUEST["prediction_request_geometry.geojson<br/>User-defined AOI<br/>oe_start_time, oe_end_time"]
    
    STAGE1["partition_request_geometry<br/>GridPartitioner<br/>grid_size: 0.25-1.0°"]
    
    PARTITIONS["Coarse Partitions<br/>Geographic tiles<br/>Parallel processing"]
    
    STAGE2["prepare_window_geometries<br/>GridPartitioner<br/>grid_size: 32-1024 pixels"]
    
    WINDOWS["Processing Windows<br/>Pixel-aligned grids<br/>UTM or Web Mercator"]
    
    DATA_ACQ["Data Acquisition<br/>Query Planetary Computer<br/>Per-window Sentinel-2"]
    
    INFERENCE["Model Inference<br/>Per-window predictions<br/>overlap_ratio: 0.25"]
    
    POST_WINDOW["process_window<br/>Window-level postprocessing<br/>NoopRaster or custom"]
    
    POST_PARTITION["process_partition<br/>CombineGeotiff<br/>Merge windows in partition"]
    
    POST_DATASET["process_dataset<br/>CombineGeotiff<br/>Merge all partitions"]
    
    FINAL["Final GeoTIFF<br/>Complete predictions<br/>User AOI"]
    
    REQUEST --> STAGE1
    STAGE1 --> PARTITIONS
    PARTITIONS --> STAGE2
    STAGE2 --> WINDOWS
    WINDOWS --> DATA_ACQ
    DATA_ACQ --> INFERENCE
    INFERENCE --> POST_WINDOW
    POST_WINDOW --> POST_PARTITION
    POST_PARTITION --> POST_DATASET
    POST_DATASET --> FINAL
    
    style STAGE1 fill:#f0f0f0
    style STAGE2 fill:#f0f0f0
    style POST_PARTITION fill:#e0e0e0
    style POST_DATASET fill:#e0e0e0
```

**Diagram: Partitioning Integration in Complete Pipeline**

The hierarchical partitioning:
1. **Enables Parallelism**: Partitions process independently
2. **Manages Memory**: Windows fit in available GPU/CPU memory
3. **Optimizes Data Access**: Spatial locality reduces redundant queries
4. **Facilitates Aggregation**: Hierarchical merge reduces I/O operations

For details on post-processing and result aggregation, see [Post-processing and Output](#7.4).

**Sources:** [olmoearth_run_data/nandi/olmoearth_run.yaml:22-52](), [olmoearth_run_data/mozambique_lulc/olmoearth_run.yaml:50-80]()

## Summary

The olmoearth_run partitioning system uses a two-stage hierarchical approach:

1. **Coarse Geographic Partitioning**: Divides large areas into manageable tiles using lat/lon coordinates
2. **Fine Window-Level Processing**: Subdivides partitions into pixel-aligned grids in projected coordinates

Key configuration parameters:

| Stage | Component | Parameter | Typical Values |
|-------|-----------|-----------|----------------|
| Coarse | `partition_request_geometry` | `grid_size` | 0.25-1.0 degrees |
| Fine | `prepare_window_geometries` | `grid_size` | 32-1024 pixels |
| Fine | `output_projection` | `crs` | EPSG:3857 or UTM |
| Fine | `output_projection` | `x_resolution` / `y_resolution` | 10 / -10 meters |
| Fine | `prepare_window_geometries` | `use_utm` | true/false |
| Inference | `predict_config` | `patch_size` | 16 pixels |
| Inference | `predict_config` | `overlap_ratio` | 0.25 |

The system automatically handles:
- UTM zone selection for accurate geographic measurements
- Window grid alignment to projection boundaries
- Patch-level overlap for seamless predictions
- Hierarchical aggregation of results

**Sources:** [olmoearth_run_data/nandi/olmoearth_run.yaml:22-52](), [olmoearth_run_data/mozambique_lulc/olmoearth_run.yaml:50-80](), [olmoearth_run_data/awf/olmoearth_run.yaml:22-52](), [olmoearth_run_data/mozambique_lulc/model.yaml:236-240]()

---

# Page: Post-processing and Output

# Post-processing and Output

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [olmoearth_run_data/awf/olmoearth_run.yaml](olmoearth_run_data/awf/olmoearth_run.yaml)
- [olmoearth_run_data/mozambique_lulc/dataset.json](olmoearth_run_data/mozambique_lulc/dataset.json)
- [olmoearth_run_data/mozambique_lulc/model.yaml](olmoearth_run_data/mozambique_lulc/model.yaml)
- [olmoearth_run_data/mozambique_lulc/olmoearth_run.yaml](olmoearth_run_data/mozambique_lulc/olmoearth_run.yaml)
- [olmoearth_run_data/nandi/olmoearth_run.yaml](olmoearth_run_data/nandi/olmoearth_run.yaml)

</details>



## Purpose and Scope

This document describes the post-processing strategies and output formatting applied during inference in the olmoearth_run pipeline. Post-processing occurs at three hierarchical levels (window, partition, dataset) to aggregate model predictions into final GeoTIFF rasters. This page also documents the inference results configuration system that defines output metadata, including classification value mappings, color schemes, and data types.

For information about the overall inference pipeline, see [olmoearth_run Pipeline](#7.1). For details on partitioning strategies that precede post-processing, see [Partitioning and Grid Processing](#7.3).

---

## Post-processing Architecture

The olmoearth_run pipeline implements a three-level hierarchical post-processing architecture that progressively aggregates model predictions from individual inference windows into complete geographic outputs.

```mermaid
graph TB
    subgraph "Inference Stage"
        MODEL["Model Prediction<br/>RslearnLightningModule.predict()"]
        WRITER["RslearnWriter<br/>prediction_writer.py"]
        MERGER["RasterMerger<br/>padding parameter"]
    end
    
    subgraph "Post-processing Hierarchy"
        WINDOW["process_window<br/>Window-level Processing<br/>NoopRaster"]
        PARTITION["process_partition<br/>Partition-level Aggregation<br/>CombineGeotiff"]
        DATASET["process_dataset<br/>Dataset-level Aggregation<br/>CombineGeotiff"]
    end
    
    subgraph "Configuration"
        YAML["olmoearth_run.yaml<br/>postprocessing_strategies"]
        NODATA["nodata_value<br/>Per-model setting"]
    end
    
    subgraph "Output"
        GEOTIFF["Final GeoTIFF Raster<br/>EPSG:3857 or UTM<br/>10m resolution"]
        METADATA["inference_results_config<br/>Classification mappings<br/>Color schemes"]
    end
    
    MODEL --> WRITER
    WRITER --> MERGER
    MERGER --> WINDOW
    
    YAML --> WINDOW
    YAML --> PARTITION
    YAML --> DATASET
    
    WINDOW --> PARTITION
    PARTITION --> DATASET
    DATASET --> GEOTIFF
    
    NODATA --> PARTITION
    NODATA --> DATASET
    METADATA --> GEOTIFF
    
    style WINDOW fill:#f9f9f9
    style PARTITION fill:#f0f0f0
    style DATASET fill:#e8e8e8
```

**Sources:** [olmoearth_run_data/nandi/olmoearth_run.yaml:40-52](), [olmoearth_run_data/awf/olmoearth_run.yaml:40-52](), [olmoearth_run_data/mozambique_lulc/olmoearth_run.yaml:68-80]()

---

## Post-processing Strategies

### Window-level Processing

Window-level post-processing occurs immediately after model prediction for each inference window. In most configurations, this stage uses `NoopRaster`, which performs no transformations and simply passes predictions through to the next stage.

```mermaid
graph LR
    INPUT["Individual Window<br/>Prediction Array"]
    NOOP["NoopRaster<br/>postprocessors.noop_raster"]
    OUTPUT["Unchanged Array<br/>Ready for aggregation"]
    
    INPUT --> NOOP
    NOOP --> OUTPUT
```

**Configuration Example:**

```yaml
postprocessing_strategies:
  process_window:
    class_path: olmoearth_run.runner.tools.postprocessors.noop_raster.NoopRaster
```

The `NoopRaster` strategy is used when no window-specific transformations are needed, deferring all aggregation to higher levels.

**Sources:** [olmoearth_run_data/nandi/olmoearth_run.yaml:51-52](), [olmoearth_run_data/awf/olmoearth_run.yaml:51-52](), [olmoearth_run_data/mozambique_lulc/olmoearth_run.yaml:79-80]()

### Partition-level Processing

Partition-level post-processing combines predictions from multiple windows within a single geographic partition (typically 1024x1024 pixels) into a unified raster. This stage uses `CombineGeotiff` to merge overlapping predictions and handle nodata regions.

```mermaid
graph TB
    subgraph "Partition Input"
        W1["Window 1<br/>256x256 pixels"]
        W2["Window 2<br/>256x256 pixels"]
        W3["Window 3<br/>256x256 pixels"]
        WN["Window N<br/>256x256 pixels"]
    end
    
    COMBINE["CombineGeotiff<br/>combine_geotiff.py"]
    NODATA["nodata_value<br/>Invalid pixel marker"]
    
    PARTITION_OUT["Partition GeoTIFF<br/>1024x1024 pixels<br/>Single merged raster"]
    
    W1 --> COMBINE
    W2 --> COMBINE
    W3 --> COMBINE
    WN --> COMBINE
    NODATA --> COMBINE
    
    COMBINE --> PARTITION_OUT
```

**Configuration Example:**

```yaml
postprocessing_strategies:
  process_partition:
    class_path: olmoearth_run.runner.tools.postprocessors.combine_geotiff.CombineGeotiff
    init_args:
      nodata_value: 10
```

The `nodata_value` parameter identifies pixels that should be excluded from the output, typically corresponding to invalid or missing predictions.

**Sources:** [olmoearth_run_data/nandi/olmoearth_run.yaml:46-49](), [olmoearth_run_data/awf/olmoearth_run.yaml:46-49](), [olmoearth_run_data/mozambique_lulc/olmoearth_run.yaml:74-77]()

### Dataset-level Processing

Dataset-level post-processing performs the final aggregation, combining all partition GeoTIFFs into a single output raster covering the entire prediction request geometry. This stage also uses `CombineGeotiff` with the same nodata handling.

```mermaid
graph TB
    subgraph "Partition Outputs"
        P1["Partition 1<br/>1024x1024 pixels"]
        P2["Partition 2<br/>1024x1024 pixels"]
        P3["Partition 3<br/>1024x1024 pixels"]
        PN["Partition N<br/>1024x1024 pixels"]
    end
    
    COMBINE["CombineGeotiff<br/>combine_geotiff.py"]
    NODATA["nodata_value<br/>Consistent across levels"]
    
    FINAL["Final Output GeoTIFF<br/>Full request extent<br/>EPSG:3857 or UTM<br/>10m resolution"]
    
    P1 --> COMBINE
    P2 --> COMBINE
    P3 --> COMBINE
    PN --> COMBINE
    NODATA --> COMBINE
    
    COMBINE --> FINAL
```

**Configuration Example:**

```yaml
postprocessing_strategies:
  process_dataset:
    class_path: olmoearth_run.runner.tools.postprocessors.combine_geotiff.CombineGeotiff
    init_args:
      nodata_value: 10
```

The `nodata_value` must be consistent across partition-level and dataset-level processing to ensure proper masking of invalid regions throughout the aggregation hierarchy.

**Sources:** [olmoearth_run_data/nandi/olmoearth_run.yaml:41-44](), [olmoearth_run_data/awf/olmoearth_run.yaml:41-44](), [olmoearth_run_data/mozambique_lulc/olmoearth_run.yaml:69-72]()

---

## RasterMerger During Prediction

Before post-processing strategies are applied, the `RslearnWriter` callback in the training configuration handles prediction merging during inference. The `RasterMerger` manages overlapping predictions from the sliding window approach.

```mermaid
graph LR
    subgraph "Prediction Configuration"
        OVERLAP["overlap_ratio: 0.25<br/>4-pixel overlap on 16-pixel patches"]
        PADDING["padding: 2<br/>Pixels to trim from edges"]
    end
    
    subgraph "RslearnWriter"
        WRITER["RslearnWriter<br/>prediction_writer.py"]
        MERGER["RasterMerger<br/>Overlap resolution"]
    end
    
    PREDICT["Model Predictions<br/>Overlapping windows"]
    OUTPUT_LAYER["PREDICTION_OUTPUT_LAYER<br/>Environment variable"]
    SELECTOR["selector: ['segment']<br/>Task output selection"]
    
    OVERLAP --> PREDICT
    PREDICT --> WRITER
    OUTPUT_LAYER --> WRITER
    SELECTOR --> WRITER
    
    WRITER --> MERGER
    PADDING --> MERGER
    
    MERGER --> WINDOW_OUT["Window Output<br/>Non-overlapping regions"]
```

**Configuration in model.yaml:**

The `RslearnWriter` callback configuration appears in [olmoearth_run_data/mozambique_lulc/model.yaml:269-277]():

```yaml
- class_path: rslearn.train.prediction_writer.RslearnWriter
  init_args:
    path: placeholder
    output_layer: ${PREDICTION_OUTPUT_LAYER}
    selector: ["segment"]
    merger:
      class_path: rslearn.train.prediction_writer.RasterMerger
      init_args:
        padding: 2
```

The `padding: 2` parameter removes 2 pixels from each edge of predictions, eliminating potential boundary artifacts from the model's receptive field constraints.

**Overlap Resolution:**

The predict configuration in [olmoearth_run_data/mozambique_lulc/model.yaml:236-245]() defines the overlap strategy:

```yaml
predict_config:
  load_all_patches: true
  patch_size: 16
  overlap_ratio: 0.25  # 4 / 16
  skip_targets: true
```

With `overlap_ratio: 0.25`, adjacent 16x16 patches overlap by 4 pixels. The `RasterMerger` averages predictions in overlapping regions, creating smooth transitions between windows.

**Sources:** [olmoearth_run_data/mozambique_lulc/model.yaml:236-277]()

---

## Output Format and Structure

The final output from the post-processing pipeline is a GeoTIFF raster file with specific format characteristics and georeferencing.

### GeoTIFF Specifications

| Property | Value | Notes |
|----------|-------|-------|
| **Format** | GeoTIFF | Cloud-Optimized GeoTIFF (COG) compatible |
| **Coordinate System** | EPSG:3857 or UTM | UTM selected automatically if `use_utm: true` |
| **Resolution** | 10m x 10m | Consistent with Sentinel-2 native resolution |
| **Data Type** | Depends on task | INT32 for classification, FLOAT32 for regression |
| **Bands** | 1 (typically) | Single-band for classification/regression |
| **Compression** | LZW (typical) | Reduces file size while preserving data |
| **Nodata Value** | Model-specific | 9, 10, 255, etc. depending on model |

### Coordinate Reference Systems

The output projection is configured in the `prepare_window_geometries` partitioner:

```yaml
prepare_window_geometries:
  class_path: olmoearth_run.runner.tools.partitioners.grid_partitioner.GridPartitioner
  init_args:
    grid_size: 1024
    output_projection:
      class_path: rslearn.utils.geometry.Projection
      init_args:
        crs: EPSG:3857
        x_resolution: 10
        y_resolution: -10
    use_utm: true
```

When `use_utm: true` is set, the system automatically selects the appropriate UTM zone based on the request geometry's centroid, providing locally accurate metric coordinates. If `use_utm: false`, EPSG:3857 (Web Mercator) is used globally.

**Sources:** [olmoearth_run_data/nandi/olmoearth_run.yaml:28-38](), [olmoearth_run_data/awf/olmoearth_run.yaml:28-38](), [olmoearth_run_data/mozambique_lulc/olmoearth_run.yaml:56-66]()

---

## Inference Results Configuration

The `inference_results_config` section in `olmoearth_run.yaml` defines metadata that describes the output raster, including classification value mappings, color schemes, and data types. This configuration enables visualization tools and downstream applications to interpret the numeric pixel values.

```mermaid
graph TB
    CONFIG["inference_results_config"]
    
    subgraph "Data Type"
        DTYPE["data_type: RASTER<br/>or VECTOR"]
    end
    
    subgraph "Classification"
        CLASSF["classification_fields<br/>List of field definitions"]
        PROPNAME["property_name<br/>Task identifier"]
        BAND["band_index<br/>Output band number"]
        VALUES["allowed_values<br/>Value mappings"]
    end
    
    subgraph "Value Definition"
        VAL["value: int<br/>Pixel value"]
        LABEL["label: string<br/>Human-readable name"]
        COLOR["color: [R, G, B]<br/>Visualization color"]
    end
    
    subgraph "Other Fields"
        DETECT["detection_objects<br/>null for classification"]
        REGRESS["regression_fields<br/>null for classification"]
    end
    
    CONFIG --> DTYPE
    CONFIG --> CLASSF
    CONFIG --> DETECT
    CONFIG --> REGRESS
    
    CLASSF --> PROPNAME
    CLASSF --> BAND
    CLASSF --> VALUES
    
    VALUES --> VAL
    VALUES --> LABEL
    VALUES --> COLOR
```

**Sources:** [olmoearth_run_data/nandi/olmoearth_run.yaml:54-91](), [olmoearth_run_data/awf/olmoearth_run.yaml:54-88](), [olmoearth_run_data/mozambique_lulc/olmoearth_run.yaml:1-27]()

### Classification Fields

Classification fields define the mapping between numeric pixel values in the output raster and their semantic meanings. Each classification field represents a prediction task output.

**Structure:**

```yaml
inference_results_config:
  data_type: RASTER
  classification_fields:
    - property_name: segment
      band_index: 1
      allowed_values:
        - value: 0
          label: coffee
          color: [124, 67, 18]
        - value: 1
          label: grassland
          color: [169, 214, 146]
```

| Field | Type | Description |
|-------|------|-------------|
| `property_name` | string | Task identifier matching model output (e.g., "segment", "crop_type_classification") |
| `band_index` | integer | Band number in output GeoTIFF (1-indexed) |
| `allowed_values` | list | List of value mappings defining each class |

**Allowed Values Structure:**

Each entry in `allowed_values` defines a single classification category:

| Field | Type | Description |
|-------|------|-------------|
| `value` | integer | Numeric pixel value in output raster |
| `label` | string | Human-readable class name (e.g., "coffee", "grassland") |
| `color` | [int, int, int] | RGB color values (0-255) for visualization |

**Example: Nandi Crop Classification**

From [olmoearth_run_data/nandi/olmoearth_run.yaml:54-91]():

```yaml
classification_fields:
  - property_name: segment
    band_index: 1
    allowed_values:
      - value: 0
        label: coffee
        color: [124, 67, 18]
      - value: 1
        label: grassland
        color: [169, 214, 146]
      - value: 2
        label: trees
        color: [51, 160, 44]
      - value: 3
        label: maize
        color: [240, 159, 28]
      - value: 4
        label: sugarcane
        color: [251, 154, 153]
      - value: 5
        label: tea
        color: [31, 234, 146]
      - value: 6
        label: vegetables
        color: [166, 206, 227]
      - value: 7
        label: legumes
        color: [227, 26, 28]
      - value: 8
        label: water
        color: [31, 120, 180]
      - value: 9
        label: builtup
        color: [136, 33, 233]
```

This configuration maps pixel values 0-9 to 10 land cover and crop type classes with associated visualization colors.

**Sources:** [olmoearth_run_data/nandi/olmoearth_run.yaml:54-91]()

### Regression Fields

For regression tasks (e.g., Live Fuel Moisture Content), the `regression_fields` configuration would define continuous value outputs instead of discrete classifications. In classification models, this field is set to `null`.

```yaml
inference_results_config:
  data_type: RASTER
  classification_fields: null
  regression_fields:
    - property_name: lfmc
      band_index: 1
      units: "percent"
      min_value: 0.0
      max_value: 300.0
  detection_objects: null
```

**Sources:** [olmoearth_run_data/nandi/olmoearth_run.yaml:91](), [olmoearth_run_data/awf/olmoearth_run.yaml:88]()

### Detection Objects

For object detection tasks, the `detection_objects` configuration would define bounding box outputs. In the current classification models, this field is set to `null`.

```yaml
inference_results_config:
  data_type: RASTER
  classification_fields: [...]
  detection_objects: null
  regression_fields: null
```

**Sources:** [olmoearth_run_data/nandi/olmoearth_run.yaml:90](), [olmoearth_run_data/awf/olmoearth_run.yaml:87]()

---

## Output Examples by Model Type

Different models produce outputs with varying nodata values and classification schemes based on their specific applications.

### Nandi Crop Classification

| Parameter | Value |
|-----------|-------|
| **nodata_value** | 10 |
| **num_classes** | 10 (values 0-9) |
| **property_name** | segment |
| **Classes** | coffee, grassland, trees, maize, sugarcane, tea, vegetables, legumes, water, builtup |

**Sources:** [olmoearth_run_data/nandi/olmoearth_run.yaml:1-91]()

### AWF Land Cover

| Parameter | Value |
|-----------|-------|
| **nodata_value** | 9 |
| **num_classes** | 9 (values 0-8) |
| **property_name** | segment |
| **Classes** | woodland_forest, open_water, shrubland_savanna, herbaceous_wetland, grassland_barren, agriculture_settlement, montane_forest, lava_forest, urban_dense_development |

**Sources:** [olmoearth_run_data/awf/olmoearth_run.yaml:1-88]()

### Mozambique LULC

| Parameter | Value |
|-----------|-------|
| **nodata_value** | 255 |
| **num_classes** | 7 (values 1-7) |
| **property_name** | crop_type_classification |
| **Classes** | Water, Bare Ground, Rangeland, Flooded Vegetation, Trees, Cropland, Buildings |

Note: Mozambique LULC uses 1-indexed classes (1-7) instead of 0-indexed, with nodata_value of 255.

**Sources:** [olmoearth_run_data/mozambique_lulc/olmoearth_run.yaml:1-81]()

---

## Post-processing Data Flow

The complete data flow from model prediction through post-processing to final output follows this sequence:

```mermaid
graph TB
    PREDICT["Model Prediction<br/>RslearnLightningModule"]
    
    subgraph "Prediction Writing"
        WRITER["RslearnWriter<br/>selector: ['segment']"]
        RMERGER["RasterMerger<br/>padding: 2<br/>Handles overlap_ratio: 0.25"]
    end
    
    subgraph "Window-level"
        WINDOW_IN["Window Predictions<br/>Individual arrays"]
        NOOP["NoopRaster<br/>process_window"]
        WINDOW_OUT["Pass-through outputs"]
    end
    
    subgraph "Partition-level"
        PART_IN["Multiple Windows<br/>Within partition"]
        COMBINE_P["CombineGeotiff<br/>process_partition<br/>nodata_value: N"]
        PART_OUT["Partition GeoTIFF<br/>1024x1024 pixels"]
    end
    
    subgraph "Dataset-level"
        DATASET_IN["Multiple Partitions<br/>Full extent"]
        COMBINE_D["CombineGeotiff<br/>process_dataset<br/>nodata_value: N"]
        DATASET_OUT["Final GeoTIFF<br/>Complete output"]
    end
    
    subgraph "Metadata Application"
        METADATA["inference_results_config<br/>classification_fields<br/>value/label/color mappings"]
        FINAL["Annotated GeoTIFF<br/>Ready for visualization"]
    end
    
    PREDICT --> WRITER
    WRITER --> RMERGER
    RMERGER --> WINDOW_IN
    
    WINDOW_IN --> NOOP
    NOOP --> WINDOW_OUT
    WINDOW_OUT --> PART_IN
    
    PART_IN --> COMBINE_P
    COMBINE_P --> PART_OUT
    PART_OUT --> DATASET_IN
    
    DATASET_IN --> COMBINE_D
    COMBINE_D --> DATASET_OUT
    DATASET_OUT --> METADATA
    
    METADATA --> FINAL
```

**Key Processing Steps:**

1. **Prediction**: Model generates overlapping window predictions
2. **RasterMerger**: Resolves overlaps using padding and averaging
3. **Window Processing**: NoopRaster passes predictions unchanged
4. **Partition Aggregation**: CombineGeotiff merges windows into partition rasters
5. **Dataset Aggregation**: CombineGeotiff combines partitions into final output
6. **Metadata Application**: Classification mappings and colors applied to output

**Sources:** [olmoearth_run_data/mozambique_lulc/model.yaml:236-277](), [olmoearth_run_data/nandi/olmoearth_run.yaml:40-91](), [olmoearth_run_data/awf/olmoearth_run.yaml:40-88](), [olmoearth_run_data/mozambique_lulc/olmoearth_run.yaml:68-81]()

---

# Page: OlmoEarth Studio Integration

# OlmoEarth Studio Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [LICENSE](LICENSE)
- [README.md](README.md)
- [olmoearth_run_data/mozambique_lulc/README.md](olmoearth_run_data/mozambique_lulc/README.md)
- [olmoearth_run_data/mozambique_lulc/config.json](olmoearth_run_data/mozambique_lulc/config.json)

</details>



## Purpose and Scope

This page documents how fine-tuned models from the `olmoearth_projects` repository are deployed to **OlmoEarth Studio** for interactive inference and visualization. OlmoEarth Studio provides a web-based interface for applying trained models to user-defined geographic regions without requiring local infrastructure or command-line expertise.

For information about running inference locally using the command-line interface, see [olmoearth_run Pipeline](#7.1). For details about model training and fine-tuning, see [Model Training](#5). For specifics about output formats and post-processing, see [Post-processing and Output](#7.4).

## Overview

**OlmoEarth Studio** is a web application hosted at `https://olmoearth.allenai.org/` that provides an interactive map interface for running inference with OlmoEarth models. The Studio enables users to:

- Draw prediction request geometries directly on a map
- Select temporal ranges for satellite imagery
- Execute model inference without local compute resources
- Visualize classification and regression results interactively
- Download results as GeoTIFF files

The Studio uses the same core infrastructure as local inference pipelines, including the `olmoearth_run` system, configuration files from this repository, and model checkpoints hosted on HuggingFace.

**Sources:** [README.md:1-190](), [olmoearth_run_data/mozambique_lulc/README.md:135]()

## Studio Architecture

```mermaid
graph TB
    subgraph "User Interface Layer"
        MAP["Interactive Map<br/>Drawing Tools<br/>Temporal Selector"]
        CONTROLS["Inference Controls<br/>Model Selection<br/>Parameter Configuration"]
        VIEWER["Results Viewer<br/>Classification Colors<br/>Layer Toggles"]
    end
    
    subgraph "Backend Services"
        API["Studio API<br/>Request Handler<br/>Job Management"]
        QUEUE["Job Queue<br/>Inference Tasks<br/>Status Tracking"]
    end
    
    subgraph "Inference Infrastructure"
        RUNNER["olmoearth_run Pipeline<br/>partition_request_geometry<br/>prepare_window_geometries"]
        LOADER["Model Loader<br/>Checkpoint Loading<br/>HuggingFace Integration"]
        PREDICTOR["Inference Engine<br/>Batch Processing<br/>GPU Execution"]
    end
    
    subgraph "Configuration & Data"
        CONFIGS["Model Configurations<br/>model.yaml<br/>dataset.json<br/>olmoearth_run.yaml"]
        CHECKPOINTS["Model Checkpoints<br/>HuggingFace Hub<br/>allenai/OlmoEarth-v1-FT-*"]
        PC["Planetary Computer<br/>Sentinel-2 L2A<br/>Sentinel-1 RTC"]
    end
    
    subgraph "Output Storage"
        RESULTS["Results Storage<br/>GeoTIFF Files<br/>Metadata JSON"]
        CACHE["Result Cache<br/>Previously Computed<br/>Predictions"]
    end
    
    MAP --> API
    CONTROLS --> API
    API --> QUEUE
    QUEUE --> RUNNER
    
    CONFIGS --> RUNNER
    CHECKPOINTS --> LOADER
    LOADER --> PREDICTOR
    RUNNER --> PREDICTOR
    
    PC --> PREDICTOR
    
    PREDICTOR --> RESULTS
    RESULTS --> CACHE
    RESULTS --> VIEWER
    VIEWER --> MAP
    
    CACHE -.->|"reuse"| VIEWER
```

**Diagram: OlmoEarth Studio system architecture showing the flow from user interaction to inference results**

**Sources:** [README.md:49-140](), [olmoearth_run_data/mozambique_lulc/README.md:135]()

## Model Deployment Workflow

The deployment of models from `olmoearth_projects` to OlmoEarth Studio follows a structured workflow:

```mermaid
graph LR
    subgraph "Development Phase"
        TRAIN["Model Training<br/>rslearn + Lightning<br/>GPU Cluster"]
        CHECKPOINT["Checkpoint Saved<br/>best.ckpt<br/>WEKA Storage"]
        TEST["Model Validation<br/>Test Set Metrics<br/>Quality Assurance"]
    end
    
    subgraph "Publication Phase"
        HF_UPLOAD["HuggingFace Upload<br/>allenai/OlmoEarth-v1-FT-*<br/>model.ckpt"]
        CONFIGS_COMMIT["Config Files Commit<br/>model.yaml<br/>dataset.json<br/>olmoearth_run.yaml"]
        DOCS["Model Documentation<br/>docs/*.md<br/>Usage Examples"]
    end
    
    subgraph "Studio Integration"
        REGISTRY["Studio Model Registry<br/>Model Metadata<br/>Configuration Paths"]
        DEPLOY["Studio Deployment<br/>Model Available<br/>in UI"]
        UI_TEST["UI Testing<br/>Sample Predictions<br/>Validation"]
    end
    
    subgraph "Production Use"
        USERS["End Users<br/>Interactive Inference<br/>Result Downloads"]
    end
    
    TRAIN --> CHECKPOINT
    CHECKPOINT --> TEST
    TEST --> HF_UPLOAD
    TEST --> CONFIGS_COMMIT
    CONFIGS_COMMIT --> DOCS
    
    HF_UPLOAD --> REGISTRY
    CONFIGS_COMMIT --> REGISTRY
    DOCS --> REGISTRY
    
    REGISTRY --> DEPLOY
    DEPLOY --> UI_TEST
    UI_TEST --> USERS
```

**Diagram: Model deployment workflow from training to Studio availability**

**Sources:** [README.md:142-185](), [olmoearth_run_data/mozambique_lulc/README.md:117-124]()

### Deployment Requirements

For a model to be integrated into OlmoEarth Studio, the following artifacts must be available:

| Artifact | Location | Purpose |
|----------|----------|---------|
| Model Checkpoint | HuggingFace Hub: `allenai/OlmoEarth-v1-FT-{TASK}-Base` | Pre-trained weights for inference |
| `model.yaml` | `olmoearth_run_data/{PROJECT}/model.yaml` | Model architecture and hyperparameters |
| `dataset.json` | `olmoearth_run_data/{PROJECT}/dataset.json` | Data source configuration |
| `olmoearth_run.yaml` | `olmoearth_run_data/{PROJECT}/olmoearth_run.yaml` | Partitioning and post-processing |
| Model Documentation | `docs/{PROJECT}.md` | Usage instructions and performance metrics |

**Sources:** [README.md:62-74]()

## Studio Capabilities

### Interactive Geometry Definition

Users can define prediction request geometries directly in the Studio interface:

```mermaid
graph TB
    subgraph "Geometry Creation Methods"
        DRAW["Draw Polygons<br/>Manual Drawing<br/>Multi-polygon Support"]
        UPLOAD["Upload GeoJSON<br/>File Import<br/>prediction_request_geometry.geojson"]
        SELECT["Select Features<br/>Pre-defined Regions<br/>Administrative Boundaries"]
    end
    
    subgraph "Temporal Configuration"
        START["oe_start_time<br/>ISO 8601 Format<br/>Date Picker"]
        END["oe_end_time<br/>ISO 8601 Format<br/>Date Picker"]
        VALIDATION["Date Validation<br/>Model-specific Rules<br/>Data Availability Check"]
    end
    
    subgraph "Generated GeoJSON"
        FEATURE["Feature Properties<br/>oe_start_time<br/>oe_end_time<br/>model_id"]
        GEOMETRY["Geometry<br/>Polygon Coordinates<br/>WGS84 (EPSG:4326)"]
    end
    
    DRAW --> FEATURE
    UPLOAD --> FEATURE
    SELECT --> FEATURE
    
    START --> VALIDATION
    END --> VALIDATION
    VALIDATION --> FEATURE
    
    FEATURE --> GEOMETRY
```

**Diagram: Interactive geometry definition workflow in OlmoEarth Studio**

The Studio automatically generates a `prediction_request_geometry.geojson` file matching the format expected by `olmoearth_run`. For example, Mozambique LULC inference uses polygons manually drawn around provinces in the Studio interface.

**Sources:** [README.md:75-104](), [olmoearth_run_data/mozambique_lulc/README.md:135]()

### Model Selection and Configuration

The Studio presents available models with their metadata:

| Model Information | Source | Display |
|-------------------|--------|---------|
| Model Name | Documentation (`docs/*.md`) | User-friendly name |
| Task Type | `model.yaml` → `task.name` | Classification, Regression, Segmentation |
| Input Requirements | `dataset.json` → `layers` | Sentinel-1, Sentinel-2, bands |
| Temporal Configuration | `dataset.json` → `query_config` | Number of timesteps, period duration |
| Output Classes | `olmoearth_run.yaml` → `inference_metadata` | Class names, value mappings |
| Performance Metrics | Model documentation | Accuracy, F1 scores per class |

**Sources:** [README.md:8-23](), [olmoearth_run_data/mozambique_lulc/config.json:1-70]()

## Integration with olmoearth_run

The Studio backend executes inference using the same `olmoearth_run` pipeline as command-line users. The key components are:

```mermaid
graph TB
    subgraph "Studio Request"
        GEOJSON["User-drawn Geometry<br/>oe_start_time<br/>oe_end_time"]
        MODEL_SELECT["Selected Model<br/>model_id<br/>checkpoint_reference"]
    end
    
    subgraph "olmoearth_run Execution"
        CONFIG_LOAD["Load Configurations<br/>model.yaml<br/>dataset.json<br/>olmoearth_run.yaml"]
        CHECKPOINT_LOAD["Load Checkpoint<br/>Download from HuggingFace<br/>Cache Locally"]
        PARTITION["partition_request_geometry<br/>GridPartitioner<br/>Coarse Grid"]
        WINDOWS["prepare_window_geometries<br/>GridPartitioner<br/>Fine Grid"]
        QUERY["Query Planetary Computer<br/>Sentinel-2 L2A<br/>Temporal Mosaicking"]
        PREDICT["Run Inference<br/>Batch Processing<br/>Overlap Handling"]
        POSTPROCESS["Post-processing<br/>CombineGeotiff<br/>Final Assembly"]
    end
    
    subgraph "Studio Response"
        RESULT_GEOTIFF["GeoTIFF Output<br/>Classification/Regression<br/>Projected Coordinates"]
        METADATA["Inference Metadata<br/>Class Colors<br/>Value Mappings"]
        PREVIEW["Map Preview<br/>Raster Overlay<br/>Interactive Legend"]
    end
    
    GEOJSON --> CONFIG_LOAD
    MODEL_SELECT --> CONFIG_LOAD
    MODEL_SELECT --> CHECKPOINT_LOAD
    
    CONFIG_LOAD --> PARTITION
    CHECKPOINT_LOAD --> PREDICT
    PARTITION --> WINDOWS
    WINDOWS --> QUERY
    QUERY --> PREDICT
    PREDICT --> POSTPROCESS
    
    POSTPROCESS --> RESULT_GEOTIFF
    CONFIG_LOAD --> METADATA
    RESULT_GEOTIFF --> PREVIEW
    METADATA --> PREVIEW
```

**Diagram: Studio integration with olmoearth_run pipeline components**

**Sources:** [README.md:106-140]()

### Configuration File Usage

The Studio reads the same configuration files stored in `olmoearth_run_data/{PROJECT}/`:

**`model.yaml`** [olmoearth_run_data/{PROJECT}/model.yaml]():
- Defines the OlmoEarth encoder and task-specific decoder
- Specifies data normalization transforms
- Configures inference batch size and overlap handling

**`dataset.json`** [olmoearth_run_data/{PROJECT}/dataset.json]():
- Configures Planetary Computer query parameters
- Defines temporal mosaicking strategy (`PER_PERIOD_MOSAIC`)
- Specifies harmonization settings for Sentinel-2

**`olmoearth_run.yaml`** [olmoearth_run_data/{PROJECT}/olmoearth_run.yaml]():
- Defines partitioning strategy (grid sizes, overlap ratios)
- Configures post-processing operations (`CombineGeotiff`)
- Specifies output projection (`use_utm: true`, resolution)

**Sources:** [README.md:62-74](), [olmoearth_run_data/mozambique_lulc/config.json:1-70]()

## Studio vs Local Inference

Users can choose between Studio-based inference and local command-line execution:

| Aspect | OlmoEarth Studio | Local olmoearth_run |
|--------|------------------|---------------------|
| **Access** | Web browser at `olmoearth.allenai.org` | Command line with Python environment |
| **Geometry Input** | Interactive map drawing | GeoJSON file creation |
| **Compute Resources** | Studio-managed GPU infrastructure | User-provided GPU/CPU |
| **Installation** | None required | `uv sync`, dependencies, model downloads |
| **Job Management** | Automatic queuing and status tracking | Manual execution and monitoring |
| **Result Delivery** | Download link + map preview | Local directory with GeoTIFFs |
| **Use Case** | Quick exploration, small to medium areas | Large-scale processing, custom workflows |
| **Customization** | Limited to Studio-supported models | Full control over all parameters |
| **Data Access** | Planetary Computer (Studio-configured) | Any data source (configurable) |

**Sources:** [README.md:49-140]()

## Model-Specific Studio Configurations

Each model in the repository has specific considerations for Studio deployment:

### Mozambique LULC Models

The Mozambique land cover models demonstrate typical Studio integration:

**Inference Configuration:**
- User draws polygons around provinces (Gaza, Manica, Zambezia)
- Studio automatically uses 8 months of Sentinel-2 imagery
- Results show 7 LULC classes or 7 crop types
- Classification colors defined in `olmoearth_run.yaml`

**Studio Workflow:**
1. User selects "Mozambique LULC" or "Mozambique Crop Type" model
2. Draws polygon around target province
3. Studio uses fixed temporal configuration (year-long, aligned dates)
4. Results displayed with per-class colors and legend

**Sources:** [olmoearth_run_data/mozambique_lulc/README.md:1-136]()

## Output Visualization

The Studio provides interactive visualization of inference results:

```mermaid
graph TB
    subgraph "GeoTIFF Processing"
        GEOTIFF["Input GeoTIFF<br/>Classification Values<br/>Projected Coordinates"]
        COG["Cloud Optimized GeoTIFF<br/>Tiled Structure<br/>Pyramids"]
        COLORS["Apply Color Mapping<br/>inference_metadata<br/>RGB Values"]
    end
    
    subgraph "Map Rendering"
        TILES["Map Tiles<br/>Web Mercator<br/>Zoom Levels"]
        OVERLAY["Raster Overlay<br/>Transparent Background<br/>Class Boundaries"]
        LEGEND["Interactive Legend<br/>Class Names<br/>Toggle Layers"]
    end
    
    subgraph "User Interactions"
        ZOOM["Zoom & Pan<br/>Multi-resolution<br/>Smooth Navigation"]
        INSPECT["Click Inspection<br/>Pixel Values<br/>Class Labels"]
        DOWNLOAD["Download Options<br/>Original GeoTIFF<br/>Styled PNG"]
    end
    
    GEOTIFF --> COG
    COG --> COLORS
    COLORS --> TILES
    TILES --> OVERLAY
    OVERLAY --> LEGEND
    
    LEGEND --> ZOOM
    LEGEND --> INSPECT
    LEGEND --> DOWNLOAD
```

**Diagram: Studio output visualization pipeline**

**Sources:** [README.md:132-140]()

### Classification Display

For classification tasks (LULC, crop types, mangroves, ecosystems), the Studio:
- Maps integer class values to RGB colors
- Displays class names in the legend
- Allows toggling individual classes on/off
- Supports opacity adjustment for overlays

### Regression Display

For regression tasks (LFMC), the Studio:
- Uses continuous color gradients (e.g., blue to red)
- Displays value range in the legend
- Shows precise values on pixel inspection
- Supports custom color ramp configuration

**Sources:** [README.md:8-17]()

## Deployment Checklist

To deploy a new model to OlmoEarth Studio, ensure:

1. **Model Checkpoint:** Uploaded to HuggingFace Hub under `allenai` organization
2. **Configuration Files:** Committed to `olmoearth_run_data/{PROJECT}/`
   - `model.yaml` with OlmoEarth encoder and decoder
   - `dataset.json` with Planetary Computer configuration
   - `olmoearth_run.yaml` with partitioning and output settings
3. **Documentation:** Created at `docs/{PROJECT}.md` with:
   - Model description and use case
   - Training data sources and splits
   - Performance metrics (accuracy, F1 scores)
   - Usage instructions
4. **Inference Metadata:** Defined in `olmoearth_run.yaml`:
   - Classification fields with class names
   - Value mappings (integer to class)
   - Color schemes for visualization
5. **Validation:** Test inference locally using `olmoearth_run` before Studio deployment
6. **README Update:** Add model to main repository README.md

**Sources:** [README.md:1-190](), [olmoearth_run_data/mozambique_lulc/README.md:1-136]()

---

# Page: Data Sources and Formats

# Data Sources and Formats

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/awf.md](docs/awf.md)
- [docs/forest_loss_driver.md](docs/forest_loss_driver.md)
- [docs/lfmc.md](docs/lfmc.md)
- [docs/nandi.md](docs/nandi.md)
- [olmoearth_run_data/awf/dataset.json](olmoearth_run_data/awf/dataset.json)
- [olmoearth_run_data/forest_loss_driver/model.yaml](olmoearth_run_data/forest_loss_driver/model.yaml)
- [olmoearth_run_data/nandi/dataset.json](olmoearth_run_data/nandi/dataset.json)
- [olmoearth_run_data/nandi/prediction_request_geometry.geojson](olmoearth_run_data/nandi/prediction_request_geometry.geojson)

</details>



This document describes the satellite imagery and training label data sources used throughout the olmoearth_projects repository, along with their configuration formats and specifications. It covers Sentinel-2 and Sentinel-1 data acquisition through Microsoft's Planetary Computer, query configurations, band specifications, and training label sources. For information about how to set up and run inference pipelines, see [Inference and Deployment](#7). For details on dataset organization and splitting, see [Data Splitting and Organization](#4.3).

## Overview

All models in this repository utilize satellite imagery from the European Space Agency's Copernicus program, accessed through Microsoft's Planetary Computer STAC API. The primary data source is **Sentinel-2 L2A** (Level 2A atmospherically corrected surface reflectance), with some models also incorporating **Sentinel-1 RTC** (Radiometric Terrain Corrected) radar data. Training labels come from various authoritative sources including research institutions, conservation organizations, and field surveys.

Data sources are configured in `dataset.json` files located in each project's `olmoearth_run_data/{project}/` directory. These JSON files specify the layers, bands, data types, and query parameters used during both training and inference.

## Satellite Imagery Data Sources

### Sentinel-2 Level 2A

Sentinel-2 L2A provides multispectral optical imagery at 10-20 meter resolution with atmospheric correction already applied. This is the primary data source for all models in the repository.

**Dataset.json Configuration Structure:**

```mermaid
graph TB
    subgraph "dataset.json Structure"
        ROOT["dataset.json root"]
        LAYERS["layers object"]
        S2_LAYER["sentinel2 layer"]
        BANDSETS["band_sets array"]
        BANDS["bands array<br/>12 Sentinel-2 bands"]
        DATASOURCE["data_source object"]
        CLASSNAME["class_path:<br/>rslearn.data_sources.planetary_computer.Sentinel2"]
        INITARGS["init_args object"]
        QUERYCONFIG["query_config object"]
    end
    
    ROOT --> LAYERS
    LAYERS --> S2_LAYER
    S2_LAYER --> BANDSETS
    S2_LAYER --> DATASOURCE
    BANDSETS --> BANDS
    DATASOURCE --> CLASSNAME
    DATASOURCE --> INITARGS
    DATASOURCE --> QUERYCONFIG
    
    INITARGS --> CACHE["cache_dir:<br/>cache/planetary_computer"]
    INITARGS --> HARMONIZE["harmonize: true"]
    INITARGS --> SORT["sort_by:<br/>eo:cloud_cover"]
    
    QUERYCONFIG --> MAXMATCH["max_matches: 12"]
    QUERYCONFIG --> MINMATCH["min_matches: 12"]
    QUERYCONFIG --> PERIOD["period_duration:<br/>30d"]
    QUERYCONFIG --> SPACE["space_mode:<br/>PER_PERIOD_MOSAIC"]
```

**Sources:** [olmoearth_run_data/awf/dataset.json:25-61](), [olmoearth_run_data/nandi/dataset.json:25-61]()

### Band Specifications

Sentinel-2 L2A provides 12 spectral bands that are used across all models:

| Band | Name | Wavelength (nm) | Resolution (m) | Description |
|------|------|-----------------|----------------|-------------|
| B01 | Coastal aerosol | 443 | 60 | Atmospheric correction |
| B02 | Blue | 490 | 10 | Visible blue |
| B03 | Green | 560 | 10 | Visible green |
| B04 | Red | 665 | 10 | Visible red |
| B05 | Red Edge 1 | 705 | 20 | Vegetation monitoring |
| B06 | Red Edge 2 | 740 | 20 | Vegetation monitoring |
| B07 | Red Edge 3 | 783 | 20 | Vegetation monitoring |
| B08 | NIR | 842 | 10 | Near-infrared |
| B8A | NIR Narrow | 865 | 20 | Narrow near-infrared |
| B09 | Water vapor | 945 | 60 | Atmospheric correction |
| B11 | SWIR 1 | 1610 | 20 | Moisture content |
| B12 | SWIR 2 | 2190 | 20 | Moisture content |

All bands are stored as `uint16` data type with digital numbers that can be converted to surface reflectance values. The band order in `dataset.json` configurations is:

```json
["B01", "B02", "B03", "B04", "B05", "B06", "B07", "B08", "B8A", "B09", "B11", "B12"]
```

**Sources:** [olmoearth_run_data/awf/dataset.json:28-41](), [olmoearth_run_data/nandi/dataset.json:28-41]()

### Sentinel-1 RTC (Radar Data)

Some models, particularly the LFMC (Live Fuel Moisture Content) model, incorporate Sentinel-1 Radiometric Terrain Corrected SAR data. Sentinel-1 provides C-band synthetic aperture radar imagery with VV and VH polarizations, which penetrates clouds and provides complementary information to optical imagery.

```mermaid
graph LR
    subgraph "Sentinel-1 RTC Specification"
        S1["Sentinel-1 RTC"]
        POL["Polarizations:<br/>VV, VH"]
        FREQ["C-Band<br/>5.405 GHz"]
        RES["Resolution:<br/>10m"]
        SOURCE["Data Source:<br/>Planetary Computer"]
    end
    
    S1 --> POL
    S1 --> FREQ
    S1 --> RES
    S1 --> SOURCE
    
    subgraph "Use Cases"
        LFMC["LFMC Model<br/>12 timesteps"]
        FOREST["Forest Loss Driver<br/>Optional enhancement"]
    end
    
    SOURCE --> LFMC
    SOURCE --> FOREST
```

**Sources:** [docs/lfmc.md:16-20]()

## Planetary Computer Integration

All satellite data is accessed through Microsoft's Planetary Computer, which provides a STAC (SpatioTemporal Asset Catalog) API for querying and retrieving satellite imagery. The integration is handled by the `rslearn.data_sources.planetary_computer.Sentinel2` class.

### Data Source Configuration

```mermaid
graph TB
    subgraph "Planetary Computer Data Source"
        CLASSDEF["rslearn.data_sources.planetary_computer.Sentinel2"]
        INIT["init_args"]
        QUERY["query_config"]
    end
    
    subgraph "Initialization Parameters"
        CACHE["cache_dir:<br/>cache/planetary_computer"]
        HARMONIZE["harmonize: true<br/>Cross-sensor consistency"]
        SORTBY["sort_by:<br/>eo:cloud_cover"]
        INGEST["ingest: false<br/>No pre-download"]
    end
    
    subgraph "Query Parameters"
        MAX["max_matches: 12<br/>Maximum images per period"]
        MIN["min_matches: 12<br/>Minimum required images"]
        DURATION["period_duration: 30d<br/>Time window per mosaic"]
        MODE["space_mode:<br/>PER_PERIOD_MOSAIC"]
    end
    
    CLASSDEF --> INIT
    CLASSDEF --> QUERY
    INIT --> CACHE
    INIT --> HARMONIZE
    INIT --> SORTBY
    INIT --> INGEST
    QUERY --> MAX
    QUERY --> MIN
    QUERY --> DURATION
    QUERY --> MODE
```

**Sources:** [olmoearth_run_data/awf/dataset.json:45-58](), [olmoearth_run_data/nandi/dataset.json:45-58]()

### Key Configuration Parameters

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `cache_dir` | `"cache/planetary_computer"` | Local cache directory for downloaded imagery tiles |
| `harmonize` | `true` | Apply harmonization to ensure cross-sensor consistency across Sentinel-2A and Sentinel-2B |
| `sort_by` | `"eo:cloud_cover"` | Prioritize scenes with lowest cloud cover |
| `ingest` | `false` | Do not pre-download data; fetch on-demand during training/inference |
| `max_matches` | `12` | Maximum number of images to retrieve per time period |
| `min_matches` | `12` | Minimum required images (will fail if insufficient coverage) |
| `period_duration` | `"30d"` | Duration of each time period for temporal mosaicking |
| `space_mode` | `"PER_PERIOD_MOSAIC"` | Create one cloud-free mosaic per time period |

**Sources:** [olmoearth_run_data/awf/dataset.json:48-58]()

### Temporal Mosaicking Strategy

The `PER_PERIOD_MOSAIC` space mode creates temporal composites by selecting the best pixels from multiple Sentinel-2 scenes within each 30-day period. This approach:

1. Divides the total time range into 30-day periods
2. Queries all available Sentinel-2 scenes within each period
3. Sorts scenes by cloud cover (lowest first)
4. Creates a mosaic by selecting cloud-free pixels from available scenes
5. Results in 12 timesteps for a one-year time range (360 days ÷ 30 days)

Different projects may use different period durations:
- **Standard models** (Nandi, AWF, Mozambique): 30-day periods → 12 timesteps per year
- **LFMC model**: 14-day periods → 12 timesteps for 168 days

**Sources:** [docs/nandi.md:14-15](), [docs/awf.md:14-15](), [docs/lfmc.md:16-20]()

## Training Label Sources

Training labels come from various authoritative sources depending on the application domain:

### Label Source Inventory

```mermaid
graph TB
    subgraph "Global Research Datasets"
        GLOBELFMC["Globe-LFMC 2.0<br/>Fuel moisture samples<br/>Continental US<br/>CC0 License"]
        GMW["Global Mangrove Watch<br/>Mangrove extent<br/>Worldwide"]
    end
    
    subgraph "Regional Organizations"
        CGIAR["CGIAR/IFPRI<br/>Crop labels<br/>Nandi County, Kenya<br/>819 polygons"]
        AWF["African Wildlife Foundation<br/>Land cover points<br/>Southern Kenya<br/>1469 points"]
        ACA["Amazon Conservation Association<br/>Forest loss drivers<br/>South America<br/>CC BY 4.0"]
    end
    
    subgraph "Supplementary Sources"
        ESA["ESA WorldCover<br/>Global land cover<br/>Gap filling"]
        GLAD["GLAD-S2 Alerts<br/>Forest loss detection<br/>Weekly updates"]
        STUDIO["OlmoEarth Studio<br/>Custom annotations<br/>Expert corrections"]
    end
    
    subgraph "Model Training"
        LFMCM["LFMC Model"]
        NANDIM["Nandi Model"]
        AWFM["AWF Model"]
        FLDM["Forest Loss Driver Model"]
        MANGM["Mangrove Model"]
    end
    
    GLOBELFMC --> LFMCM
    CGIAR --> NANDIM
    ESA --> NANDIM
    STUDIO --> NANDIM
    AWF --> AWFM
    ESA --> AWFM
    ACA --> FLDM
    GLAD --> FLDM
    GMW --> MANGM
```

**Sources:** [docs/lfmc.md:27-40](), [docs/nandi.md:29-37](), [docs/awf.md:29-35](), [docs/forest_loss_driver.md:54-63]()

### Label Format by Source

| Source | Format | Geometry Type | Attributes | License |
|--------|--------|---------------|------------|---------|
| Globe-LFMC 2.0 | GeoJSON/CSV | Point | lon, lat, timestamp, fuel_type, LFMC value | CC0 |
| CGIAR/IFPRI | GPKG | Polygon | crop_type, survey_date | Proprietary |
| AWF | GeoJSON | Point | lon, lat, time_range, land_cover_type | Proprietary |
| Amazon Conservation | GeoJSON | Polygon | GLAD alert geometry, timestamp, driver_category | CC BY 4.0 |
| ESA WorldCover | Raster (GeoTIFF) | N/A | Land cover class (10m resolution) | CC BY 4.0 |
| GLAD-S2 | Raster (GeoTIFF) | N/A | Forest loss alerts (10m resolution) | Public |

**Sources:** [docs/lfmc.md:27-40](), [docs/nandi.md:29-37](), [docs/awf.md:29-35](), [docs/forest_loss_driver.md:54-63]()

### Data Augmentation from Multiple Sources

The Nandi model demonstrates a common pattern of combining multiple label sources:

1. **Primary source**: CGIAR/IFPRI field survey data (819 polygons)
2. **Gap filling**: ESA WorldCover for Water and Built-up classes (underrepresented in primary source)
3. **Expert correction**: OlmoEarth Studio annotations to correct Coffee/Tree misclassifications

This multi-source approach ensures balanced class representation and corrects systematic labeling errors.

**Sources:** [docs/nandi.md:29-33]()

## Data Formats

### GeoJSON for Annotations

Training annotations are stored in GeoJSON format with specific properties:

```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Point" | "Polygon",
        "coordinates": [...]
      },
      "properties": {
        "category": "...",
        "timestamp": "...",
        "other_domain_specific_fields": "..."
      }
    }
  ]
}
```

**Inference Request Format:**

For inference, `prediction_request_geometry.geojson` specifies the spatial and temporal extent:

```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Polygon",
        "coordinates": [[[lon1, lat1], [lon2, lat2], ...]]
      },
      "properties": {
        "oe_start_time": "2022-09-01T00:00:00Z",
        "oe_end_time": "2023-09-01T00:00:00Z"
      }
    }
  ]
}
```

**Sources:** [olmoearth_run_data/nandi/prediction_request_geometry.geojson:1-39]()

### GeoPackage (GPKG) for Raw Data

Field survey data and raw annotations are often provided in GeoPackage format, which is a SQLite-based geospatial data format. These are processed by scripts in the data processing pipeline to create training windows.

**Sources:** [docs/nandi.md:31-32]()

### GeoTIFF for Outputs

Model predictions and reference data are stored as GeoTIFF rasters:
- **Data type**: Varies by task (int32 for classification, float32 for regression)
- **Projection**: EPSG:3857 (Web Mercator) or local UTM zones
- **Resolution**: 10 meters per pixel
- **Bands**: Single band for most models, multiple bands for probability outputs

### rslearn Dataset Archives

Training datasets are packaged as `.tar` archives containing:
- `dataset.json` - Layer and data source specifications
- `windows.db` - SQLite database of training window metadata
- Rasterized label files (when labels are ingested)

These archives are distributed via HuggingFace Datasets and Google Cloud Storage.

**Sources:** [docs/nandi.md:10](), [docs/awf.md:10](), [docs/lfmc.md:12]()

## Dataset.json Layer Configuration

The `dataset.json` file defines three types of layers:

```mermaid
graph LR
    subgraph "Layer Types in dataset.json"
        LABEL["label layer<br/>type: raster<br/>dtype: int32<br/>Training targets"]
        OUTPUT["output layer<br/>type: raster<br/>dtype: float32<br/>Model predictions"]
        SENTINEL2["sentinel2 layer<br/>type: raster<br/>dtype: uint16<br/>Input imagery"]
    end
    
    subgraph "Usage During Pipeline"
        TRAIN["Training Phase"]
        INFERENCE["Inference Phase"]
    end
    
    LABEL --> TRAIN
    SENTINEL2 --> TRAIN
    SENTINEL2 --> INFERENCE
    OUTPUT --> INFERENCE
```

**Sources:** [olmoearth_run_data/awf/dataset.json:1-63](), [olmoearth_run_data/nandi/dataset.json:1-63]()

### Label Layer

Stores training labels (ground truth):
- **Band**: `category` (integer class indices)
- **Data type**: `int32`
- **Type**: `raster`

### Output Layer

Stores model predictions during inference:
- **Band**: `output` (predicted class or regression value)
- **Data type**: `float32`
- **Type**: `raster`

### Sentinel2 Layer

Defines the satellite imagery input:
- **Bands**: All 12 Sentinel-2 bands (B01-B12)
- **Data type**: `uint16` (digital numbers)
- **Type**: `raster`
- **Data source**: `rslearn.data_sources.planetary_computer.Sentinel2`

This layer is the most complex, containing the full Planetary Computer integration configuration including query parameters and harmonization settings.

**Sources:** [olmoearth_run_data/awf/dataset.json:25-61](), [olmoearth_run_data/nandi/dataset.json:25-61]()

## Time Series Configuration

Models use different temporal configurations depending on their application:

| Model | Time Period | Timesteps | Total Duration | Period Duration |
|-------|-------------|-----------|----------------|-----------------|
| Nandi | 2022-09 to 2023-09 | 12 | 1 year | 30 days |
| AWF | 2023-01 to 2023-12 | 12 | 1 year | 30 days |
| LFMC | 168 days ending at sample timestamp | 12 | 168 days | 14 days |
| Forest Loss Driver | Pre/post forest loss | 8 (4+4) | Variable | Variable |
| Mangrove | 1 year | 12 | 1 year | 30 days |

The Forest Loss Driver model uses a unique configuration with separate pre- and post-forest-loss time series:

```yaml
# From model.yaml
inputs:
  sentinel2_l2a:
    layers: [
      "pre_sentinel2", "pre_sentinel2.1", "pre_sentinel2.2", "pre_sentinel2.3",
      "post_sentinel2", "post_sentinel2.1", "post_sentinel2.2", "post_sentinel2.3"
    ]
```

**Sources:** [docs/nandi.md:35](), [docs/awf.md:33](), [docs/lfmc.md:35](), [olmoearth_run_data/forest_loss_driver/model.yaml:47]()

## Data Normalization

All input imagery is normalized using the `OlmoEarthNormalize` transform, which applies sensor-specific normalization based on statistics computed from the OlmoEarth pre-training dataset. This ensures consistency between pre-training and fine-tuning.

```yaml
# Standard normalization configuration
- class_path: rslearn.models.olmoearth_pretrain.norm.OlmoEarthNormalize
  init_args:
    band_names:
      sentinel2_l2a: ["B02", "B03", "B04", "B08", "B05", "B06", "B07", "B8A", "B11", "B12", "B01", "B09"]
```

**Sources:** [olmoearth_run_data/forest_loss_driver/model.yaml:75-78]()

---

# Page: Sentinel-2 L2A Data

# Sentinel-2 L2A Data

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [olmoearth_run_data/awf/dataset.json](olmoearth_run_data/awf/dataset.json)
- [olmoearth_run_data/mozambique_lulc/dataset.json](olmoearth_run_data/mozambique_lulc/dataset.json)
- [olmoearth_run_data/mozambique_lulc/model.yaml](olmoearth_run_data/mozambique_lulc/model.yaml)
- [olmoearth_run_data/mozambique_lulc/olmoearth_run.yaml](olmoearth_run_data/mozambique_lulc/olmoearth_run.yaml)
- [olmoearth_run_data/nandi/dataset.json](olmoearth_run_data/nandi/dataset.json)

</details>



## Purpose and Scope

This page documents the Sentinel-2 Level 2A (L2A) atmospheric correction data used as the primary optical imagery source across all models in the olmoearth_projects repository. It covers band specifications, query configurations, harmonization settings, temporal mosaicking strategies, and data type handling. For information about the Planetary Computer API used to access this data, see [Planetary Computer Integration](#8.2).

## Overview

Sentinel-2 L2A provides bottom-of-atmosphere reflectance imagery from the European Space Agency's Copernicus program. All models in this repository use a standardized 12-band configuration accessed via Microsoft's Planetary Computer, with consistent harmonization and temporal mosaicking applied.

```mermaid
graph TB
    S2["Sentinel-2 L2A<br/>ESA Copernicus"]
    PC["Planetary Computer API<br/>Microsoft Azure"]
    DS["rslearn.data_sources.planetary_computer.Sentinel2"]
    CONFIG["dataset.json<br/>Band Configuration"]
    QUERY["Query Parameters<br/>max_matches<br/>period_duration<br/>space_mode"]
    HARMONIZE["Harmonization<br/>Cross-sensor Alignment"]
    MOSAIC["Temporal Mosaicking<br/>PER_PERIOD_MOSAIC<br/>30-day Periods"]
    DATA["uint16 Raster Data<br/>12 Bands<br/>10m Resolution"]
    
    S2 --> PC
    PC --> DS
    CONFIG --> DS
    DS --> QUERY
    DS --> HARMONIZE
    QUERY --> MOSAIC
    HARMONIZE --> MOSAIC
    MOSAIC --> DATA
    
    style DS fill:#f9f9f9
    style CONFIG fill:#f9f9f9
    style DATA fill:#f9f9f9
```

**Sources:** [olmoearth_run_data/mozambique_lulc/dataset.json](), [olmoearth_run_data/awf/dataset.json](), [olmoearth_run_data/nandi/dataset.json]()

## Band Specifications

Sentinel-2 L2A data includes 13 spectral bands, but this repository uses a standardized subset of 12 bands across all models. The following table describes each band's characteristics:

| Band ID | Resolution | Wavelength (nm) | Description | Usage |
|---------|------------|-----------------|-------------|-------|
| B01 | 60m | 443 | Coastal aerosol | Atmospheric correction, water vapor |
| B02 | 10m | 490 | Blue | Visible spectrum, water bodies |
| B03 | 10m | 560 | Green | Visible spectrum, vegetation |
| B04 | 10m | 665 | Red | Visible spectrum, vegetation stress |
| B05 | 20m | 705 | Red Edge 1 | Vegetation classification |
| B06 | 20m | 740 | Red Edge 2 | Vegetation health |
| B07 | 20m | 783 | Red Edge 3 | Vegetation moisture |
| B08 | 10m | 842 | NIR | Near-infrared, biomass |
| B8A | 20m | 865 | Narrow NIR | Vegetation indices |
| B09 | 60m | 945 | Water vapor | Atmospheric correction |
| B11 | 20m | 1610 | SWIR 1 | Moisture content, soil |
| B12 | 20m | 2190 | SWIR 2 | Geology, land cover |

**Note:** Band B10 (1375nm, cirrus detection) is not used in this repository's models.

**Sources:** [olmoearth_run_data/mozambique_lulc/dataset.json:28-41](), [olmoearth_run_data/awf/dataset.json:28-41]()

## Data Source Configuration

Sentinel-2 data is configured in `dataset.json` files using the `rslearn.data_sources.planetary_computer.Sentinel2` class. The configuration defines band sets, data types, and access parameters.

```mermaid
graph LR
    subgraph "dataset.json Structure"
        LAYERS["layers"]
        S2["sentinel2"]
        BANDSETS["band_sets"]
        BANDS["bands: [B01...B12]"]
        DTYPE["dtype: uint16"]
        DS["data_source"]
        CLASSPATH["class_path:<br/>rslearn.data_sources.<br/>planetary_computer.Sentinel2"]
        INITARGS["init_args"]
        QUERYCONFIG["query_config"]
    end
    
    LAYERS --> S2
    S2 --> BANDSETS
    S2 --> DS
    BANDSETS --> BANDS
    BANDSETS --> DTYPE
    DS --> CLASSPATH
    DS --> INITARGS
    DS --> QUERYCONFIG
    
    style S2 fill:#f9f9f9
    style DS fill:#f9f9f9
```

**Sources:** [olmoearth_run_data/mozambique_lulc/dataset.json:25-61]()

### Standard Configuration Template

All Sentinel-2 layers in `dataset.json` follow this structure:

```json
"sentinel2": {
  "band_sets": [{
    "bands": ["B01", "B02", "B03", "B04", "B05", "B06", "B07", 
              "B08", "B8A", "B09", "B11", "B12"],
    "dtype": "uint16"
  }],
  "data_source": {
    "class_path": "rslearn.data_sources.planetary_computer.Sentinel2",
    "ingest": false,
    "init_args": {
      "cache_dir": "cache/planetary_computer",
      "harmonize": true,
      "sort_by": "eo:cloud_cover"
    },
    "query_config": {
      "max_matches": 8-12,
      "min_matches": 8-12,
      "period_duration": "30d",
      "space_mode": "PER_PERIOD_MOSAIC"
    }
  },
  "type": "raster"
}
```

**Sources:** [olmoearth_run_data/mozambique_lulc/dataset.json:25-61](), [olmoearth_run_data/awf/dataset.json:25-61]()

## Query Configuration Parameters

The `query_config` section controls how Sentinel-2 imagery is queried and aggregated over time and space:

| Parameter | Type | Values | Description |
|-----------|------|--------|-------------|
| `max_matches` | int | 8, 12 | Maximum number of timesteps to retrieve |
| `min_matches` | int | 8, 12 | Minimum required timesteps for valid data |
| `period_duration` | str | "30d" | Duration of each temporal period |
| `space_mode` | str | "PER_PERIOD_MOSAIC" | Spatial aggregation strategy |

### Temporal Mosaicking Strategy

The `PER_PERIOD_MOSAIC` mode creates composite images for each 30-day period by selecting the best pixels from all available scenes:

```mermaid
graph TB
    subgraph "Temporal Mosaicking Flow"
        START["Time Range<br/>(oe_start_time to oe_end_time)"]
        DIVIDE["Divide into 30-day Periods"]
        QUERY["Query Sentinel-2 Scenes<br/>per Period"]
        SORT["Sort by eo:cloud_cover"]
        SELECT["Select Best Pixels<br/>(lowest cloud cover)"]
        MOSAIC["Create Period Mosaic"]
        STACK["Stack 8-12 Timesteps"]
        OUTPUT["Multi-temporal<br/>Image Cube"]
    end
    
    START --> DIVIDE
    DIVIDE --> QUERY
    QUERY --> SORT
    SORT --> SELECT
    SELECT --> MOSAIC
    MOSAIC --> STACK
    STACK --> OUTPUT
    
    style MOSAIC fill:#f9f9f9
    style OUTPUT fill:#f9f9f9
```

**Sources:** [olmoearth_run_data/mozambique_lulc/dataset.json:53-58]()

### Model-Specific Configurations

Different models use different numbers of timesteps based on their temporal requirements:

| Model | max_matches | min_matches | Purpose |
|-------|-------------|-------------|---------|
| Mozambique LULC | 8 | 8 | Single growing season coverage |
| AWF Land Cover | 12 | 12 | Full annual cycle |
| Nandi Crop Type | 12 | 12 | Complete crop phenology |

**Sources:** [olmoearth_run_data/mozambique_lulc/dataset.json:54-55](), [olmoearth_run_data/awf/dataset.json:54-55](), [olmoearth_run_data/nandi/dataset.json:54-55]()

## Harmonization

The `harmonize: true` setting in `init_args` enables cross-sensor radiometric consistency by applying the harmonization algorithm described in the Sentinel-2 documentation. This corrects for systematic differences between Sentinel-2A and Sentinel-2B satellites, ensuring consistent reflectance values across the time series.

**Harmonization Effects:**
- Adjusts Sentinel-2B band values to match Sentinel-2A reference
- Applies correction factors to visible and NIR bands
- Ensures temporal consistency when both satellites contribute to the same mosaic

**Sources:** [olmoearth_run_data/mozambique_lulc/dataset.json:50](), [olmoearth_run_data/awf/dataset.json:50]()

## Band Ordering in Model Inputs

While `dataset.json` defines bands in numerical order (B01-B12), the model inputs reorder bands for optimal processing. The `model.yaml` configuration specifies the exact band order used during training and inference:

```mermaid
graph LR
    subgraph "Band Order Transformation"
        JSON["dataset.json<br/>B01, B02, B03, B04,<br/>B05, B06, B07, B08,<br/>B8A, B09, B11, B12"]
        YAML["model.yaml inputs<br/>B02, B03, B04, B08,<br/>B05, B06, B07, B8A,<br/>B11, B12, B01, B09"]
        NORM["OlmoEarthNormalize<br/>band_names parameter"]
    end
    
    JSON --> YAML
    YAML --> NORM
    
    style YAML fill:#f9f9f9
    style NORM fill:#f9f9f9
```

**Standard Band Order in Model Inputs:**
```
["B02", "B03", "B04", "B08", "B05", "B06", "B07", "B8A", "B11", "B12", "B01", "B09"]
```

This ordering groups visible bands first (B02-B04), followed by NIR (B08), red edge bands (B05-B07, B8A), SWIR bands (B11-B12), and finally atmospheric bands (B01, B09).

**Sources:** [olmoearth_run_data/mozambique_lulc/model.yaml:40](), [olmoearth_run_data/mozambique_lulc/model.yaml:204]()

## Data Types and Conversions

Sentinel-2 data undergoes data type conversions at different stages of the pipeline:

```mermaid
graph TB
    UINT16["dataset.json<br/>dtype: uint16<br/>Raw reflectance values<br/>0-10000 range"]
    LOAD["Data Loading<br/>rslearn DataModule"]
    FLOAT32["model.yaml<br/>dtype: FLOAT32<br/>Normalized values"]
    NORM["OlmoEarthNormalize<br/>Transform"]
    TENSOR["PyTorch Tensors<br/>torch.float32"]
    
    UINT16 --> LOAD
    LOAD --> FLOAT32
    FLOAT32 --> NORM
    NORM --> TENSOR
    
    style UINT16 fill:#f9f9f9
    style FLOAT32 fill:#f9f9f9
    style NORM fill:#f9f9f9
```

### Data Type Specifications

| Stage | Data Type | Range | Location |
|-------|-----------|-------|----------|
| Storage | `uint16` | 0-10000 | dataset.json band_sets |
| Model Input | `FLOAT32` | 0.0-1.0 (after norm) | model.yaml inputs |
| Processing | `torch.float32` | Normalized | PyTorch tensors |

**Sources:** [olmoearth_run_data/mozambique_lulc/dataset.json:42](), [olmoearth_run_data/mozambique_lulc/model.yaml:42]()

## Input Configuration in model.yaml

The `model.yaml` file defines how Sentinel-2 data is consumed by the training and inference pipelines:

```mermaid
graph TB
    subgraph "Input Configuration Structure"
        INPUTS["inputs section"]
        S2L2A["sentinel2_l2a"]
        DATATYPE["data_type: raster"]
        LAYERS["layers: [sentinel2]"]
        BANDS["bands: [B02, B03,...]"]
        PASSTHROUGH["passthrough: true"]
        DTYPE["dtype: FLOAT32"]
        LOADALL["load_all_item_groups: true<br/>load_all_layers: true"]
    end
    
    INPUTS --> S2L2A
    S2L2A --> DATATYPE
    S2L2A --> LAYERS
    S2L2A --> BANDS
    S2L2A --> PASSTHROUGH
    S2L2A --> DTYPE
    S2L2A --> LOADALL
    
    style S2L2A fill:#f9f9f9
    style BANDS fill:#f9f9f9
```

### Key Input Parameters

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `data_type` | "raster" | Identifies as raster data |
| `layers` | ["sentinel2"] | References dataset.json layer name |
| `bands` | 12-element list | Specifies band order for model |
| `passthrough` | true | Passes data directly without modifications |
| `dtype` | FLOAT32 | Target data type for model processing |
| `load_all_item_groups` | true | Loads all temporal groups |
| `load_all_layers` | true | Loads all spatial layers |

**Sources:** [olmoearth_run_data/mozambique_lulc/model.yaml:36-44]()

## Normalization Transform

The `OlmoEarthNormalize` transform applies standardized normalization to Sentinel-2 bands:

```yaml
- class_path: rslearn.models.olmoearth_pretrain.norm.OlmoEarthNormalize
  init_args:
    band_names:
      sentinel2_l2a: ["B02", "B03", "B04", "B08", "B05", "B06", "B07", 
                      "B8A", "B11", "B12", "B01", "B09"]
```

This transform is applied in three contexts:
1. **Training transforms** - with augmentations (lines 219-222)
2. **Default config transforms** - for validation/test (lines 201-204)
3. **Predict config transforms** - for inference (lines 242-245)

**Sources:** [olmoearth_run_data/mozambique_lulc/model.yaml:201-204](), [olmoearth_run_data/mozambique_lulc/model.yaml:219-222](), [olmoearth_run_data/mozambique_lulc/model.yaml:242-245]()

## Caching and Performance

The Sentinel-2 data source configuration includes caching to improve performance:

```json
"init_args": {
  "cache_dir": "cache/planetary_computer",
  "harmonize": true,
  "sort_by": "eo:cloud_cover"
}
```

- **cache_dir**: Local directory for caching downloaded imagery tiles
- **sort_by**: Prioritizes scenes with lowest cloud cover
- **ingest**: Set to `false`, indicating data is queried on-demand rather than pre-ingested

**Sources:** [olmoearth_run_data/mozambique_lulc/dataset.json:49-51]()

## Resolution and Resampling

Sentinel-2 bands have native resolutions of 10m, 20m, or 60m. The system handles multi-resolution data by:

1. **Target Resolution**: All bands are resampled to 10m resolution as specified in `olmoearth_run.yaml`:
   ```yaml
   output_projection:
     class_path: rslearn.utils.geometry.Projection
     init_args:
       crs: EPSG:3857
       x_resolution: 10
       y_resolution: -10
   ```

2. **Resampling Method**: Planetary Computer's Sentinel-2 interface handles resampling automatically using bilinear interpolation for 20m and 60m bands.

**Sources:** [olmoearth_run_data/mozambique_lulc/olmoearth_run.yaml:60-65]()

---

# Page: Planetary Computer Integration

# Planetary Computer Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/forest_loss_driver.md](docs/forest_loss_driver.md)
- [docs/lfmc.md](docs/lfmc.md)
- [olmoearth_run_data/awf/dataset.json](olmoearth_run_data/awf/dataset.json)
- [olmoearth_run_data/forest_loss_driver/model.yaml](olmoearth_run_data/forest_loss_driver/model.yaml)
- [olmoearth_run_data/nandi/dataset.json](olmoearth_run_data/nandi/dataset.json)

</details>



## Purpose and Scope

This document describes how the olmoearth_projects system integrates with Microsoft Planetary Computer to access satellite imagery data. Planetary Computer serves as the primary data acquisition backend for both training and inference workflows, providing standardized access to Sentinel-2 and Sentinel-1 satellite datasets.

For details on Sentinel-2 band specifications and configurations, see [Sentinel-2 L2A Data](#8.1). For information on how this data flows through the training pipeline, see [Data Module and Transforms](#5.4).

## Overview

Microsoft Planetary Computer is a cloud-based API that provides access to petabytes of earth observation data, including Sentinel-2 L2A optical imagery and Sentinel-1 RTC radar data. The system integrates with Planetary Computer through the `rslearn` framework, which handles query construction, data retrieval, caching, and harmonization.

```mermaid
graph TB
    subgraph "olmoearth_projects System"
        CONFIG["dataset.json<br/>Data Source Configuration"]
        RSLEARN["rslearn.data_sources<br/>Data Source Abstraction"]
        CACHE["Local Cache Directory<br/>cache/planetary_computer/"]
    end
    
    subgraph "Microsoft Planetary Computer"
        STAC["STAC API<br/>Spatiotemporal Asset Catalog"]
        S2_CATALOG["Sentinel-2 L2A Catalog<br/>Optical Imagery"]
        S1_CATALOG["Sentinel-1 RTC Catalog<br/>Radar Data"]
    end
    
    subgraph "Data Consumers"
        TRAINING["Model Training<br/>RslearnDataModule"]
        INFERENCE["Inference Pipeline<br/>olmoearth_run"]
    end
    
    CONFIG --> RSLEARN
    RSLEARN --> STAC
    STAC --> S2_CATALOG
    STAC --> S1_CATALOG
    S2_CATALOG --> CACHE
    S1_CATALOG --> CACHE
    CACHE --> TRAINING
    CACHE --> INFERENCE
```

**Sources**: [olmoearth_run_data/awf/dataset.json:45-52](), [olmoearth_run_data/nandi/dataset.json:45-52](), [docs/lfmc.md:17-20]()

## Data Source Configuration

Planetary Computer integration is configured in `dataset.json` files through the `data_source` field of each layer definition. The configuration uses the `rslearn.data_sources.planetary_computer.Sentinel2` class for Sentinel-2 data access.

### Configuration Structure

| Parameter | Type | Description |
|-----------|------|-------------|
| `class_path` | string | Fully qualified class name for the data source |
| `ingest` | boolean | Whether to pre-ingest data (typically `false` for PC) |
| `init_args` | object | Initialization arguments for the data source class |
| `query_config` | object | Query behavior configuration |

### Initialization Arguments

The `init_args` object configures how the data source connects to and processes Planetary Computer data:

```json
{
  "cache_dir": "cache/planetary_computer",
  "harmonize": true,
  "sort_by": "eo:cloud_cover"
}
```

| Argument | Purpose |
|----------|---------|
| `cache_dir` | Local directory path for caching downloaded imagery tiles |
| `harmonize` | Enable cross-sensor radiometric harmonization for Sentinel-2 |
| `sort_by` | STAC property used to prioritize which scenes to select |

The `harmonize: true` setting applies offset corrections to ensure radiometric consistency between Sentinel-2A and Sentinel-2B satellites, critical for multi-temporal analysis.

**Sources**: [olmoearth_run_data/awf/dataset.json:48-52](), [olmoearth_run_data/nandi/dataset.json:48-52]()

## Query Configuration

The `query_config` object defines temporal mosaicking and scene selection behavior:

```json
{
  "max_matches": 12,
  "min_matches": 12,
  "period_duration": "30d",
  "space_mode": "PER_PERIOD_MOSAIC"
}
```

### Query Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `max_matches` | integer | Maximum number of temporal composites to retrieve |
| `min_matches` | integer | Minimum required composites (query fails if not met) |
| `period_duration` | string | Duration of each temporal period (e.g., "30d", "14d") |
| `space_mode` | enum | Spatial aggregation strategy within each period |

### Space Mode Options

The `space_mode` parameter controls how multiple scenes within a temporal period are combined:

- **`PER_PERIOD_MOSAIC`**: Creates a single mosaic per period by selecting the best pixels from all available scenes based on the `sort_by` criterion. This is the most common mode, reducing cloud contamination by choosing clearest pixels.

For example, with `period_duration: "30d"` and `max_matches: 12`, the system queries for 12 temporal periods spanning 360 days (12 × 30), creating one cloud-optimized mosaic per 30-day period.

**Sources**: [olmoearth_run_data/awf/dataset.json:53-58](), [olmoearth_run_data/nandi/dataset.json:53-58]()

## Data Source Classes

### Sentinel-2 Data Source

The `rslearn.data_sources.planetary_computer.Sentinel2` class provides access to Sentinel-2 Level 2A surface reflectance data.

```mermaid
graph LR
    QUERY["Query Request<br/>Geometry + Time Range"]
    SENTINEL2["rslearn.data_sources<br/>.planetary_computer<br/>.Sentinel2"]
    STAC_SEARCH["STAC API Search<br/>collection=sentinel-2-l2a"]
    FILTER["Filter by Cloud Cover<br/>Sort by eo:cloud_cover"]
    MOSAIC["Create Period Mosaic<br/>Best-pixel Selection"]
    DOWNLOAD["Download & Cache<br/>COG Tiles"]
    OUTPUT["Multi-temporal Array<br/>[T, C, H, W]"]
    
    QUERY --> SENTINEL2
    SENTINEL2 --> STAC_SEARCH
    STAC_SEARCH --> FILTER
    FILTER --> MOSAIC
    MOSAIC --> DOWNLOAD
    DOWNLOAD --> OUTPUT
```

The Sentinel-2 data source:
1. Constructs STAC API queries from spatial and temporal extents
2. Filters scenes by cloud cover using `eo:cloud_cover` metadata
3. Applies harmonization offsets for cross-sensor consistency
4. Creates per-period mosaics by selecting best pixels
5. Downloads Cloud Optimized GeoTIFF (COG) tiles as needed
6. Caches downloaded data to avoid redundant API calls

**Sources**: [olmoearth_run_data/awf/dataset.json:45-52](), [docs/lfmc.md:17-20]()

### Sentinel-1 Data Source

For radar data, the system uses `rslearn.data_sources.planetary_computer.Sentinel1RTC`, which accesses Sentinel-1 Radiometrically Terrain Corrected (RTC) backscatter data. This is used in models like LFMC that benefit from all-weather observation capabilities.

```mermaid
graph TB
    LFMC_MODEL["LFMC Model<br/>Fuel Moisture Prediction"]
    S2_SOURCE["Sentinel-2 L2A<br/>12 Optical Mosaics<br/>14-day periods"]
    S1_SOURCE["Sentinel-1 RTC<br/>12 Radar Mosaics<br/>14-day periods<br/>VV/VH Polarization"]
    PC_S2["Planetary Computer<br/>sentinel-2-l2a collection"]
    PC_S1["Planetary Computer<br/>sentinel-1-rtc collection"]
    
    LFMC_MODEL --> S2_SOURCE
    LFMC_MODEL --> S1_SOURCE
    S2_SOURCE --> PC_S2
    S1_SOURCE --> PC_S1
```

The LFMC model demonstrates multi-sensor integration, querying both Sentinel-2 optical and Sentinel-1 radar data for the same temporal periods to capture complementary information.

**Sources**: [docs/lfmc.md:16-20]()

## Caching Architecture

The caching system improves performance and reduces redundant API calls during training and inference:

```mermaid
graph TB
    REQUEST["Data Request<br/>Geometry + Time + Bands"]
    CHECK_CACHE["Check Cache<br/>cache/planetary_computer/"]
    CACHE_HIT{"Cache Hit?"}
    LOAD_CACHE["Load from Disk"]
    QUERY_PC["Query Planetary Computer<br/>STAC API"]
    DOWNLOAD["Download COG Tiles"]
    WRITE_CACHE["Write to Cache"]
    RETURN["Return NumPy Array"]
    
    REQUEST --> CHECK_CACHE
    CHECK_CACHE --> CACHE_HIT
    CACHE_HIT -->|Yes| LOAD_CACHE
    CACHE_HIT -->|No| QUERY_PC
    QUERY_PC --> DOWNLOAD
    DOWNLOAD --> WRITE_CACHE
    WRITE_CACHE --> RETURN
    LOAD_CACHE --> RETURN
```

### Cache Organization

The cache directory structure is organized by:
- Collection name (e.g., `sentinel-2-l2a`)
- Spatial extent (bounding box hash)
- Temporal extent (date range)
- Query parameters (bands, resolution)

This ensures that identical queries across multiple training runs or inference requests reuse cached data without re-downloading.

**Sources**: [olmoearth_run_data/awf/dataset.json:49](), [olmoearth_run_data/nandi/dataset.json:49]()

## Integration Points

### Training Pipeline Integration

During model training, the `RslearnDataModule` loads windows from the rslearn dataset, which reference Planetary Computer as the data source:

```mermaid
graph LR
    WINDOW["Training Window<br/>Spatial/Temporal Extent"]
    DATAMODULE["RslearnDataModule<br/>Batch Loading"]
    DATASET_JSON["dataset.json<br/>PC Configuration"]
    PC_QUERY["Planetary Computer Query<br/>Mosaic Creation"]
    TRANSFORM["OlmoEarthNormalize<br/>Band Normalization"]
    MODEL["Model Training<br/>Batch Processing"]
    
    WINDOW --> DATAMODULE
    DATAMODULE --> DATASET_JSON
    DATASET_JSON --> PC_QUERY
    PC_QUERY --> TRANSFORM
    TRANSFORM --> MODEL
```

**Sources**: [olmoearth_run_data/forest_loss_driver/model.yaml:43-50]()

### Inference Pipeline Integration

The `olmoearth_run` inference pipeline uses the same Planetary Computer integration but with on-demand querying for user-specified geometries:

```mermaid
graph TB
    REQUEST["prediction_request_geometry.geojson<br/>User-defined Polygon"]
    PARTITION["Partition into Windows<br/>GridPartitioner"]
    QUERY_BUILD["Build PC Query<br/>Geometry + Time Range"]
    PC_DATA["Planetary Computer<br/>Scene Selection & Mosaic"]
    INFERENCE["Model Inference<br/>Per-window Prediction"]
    OUTPUT["GeoTIFF Output<br/>Classification Results"]
    
    REQUEST --> PARTITION
    PARTITION --> QUERY_BUILD
    QUERY_BUILD --> PC_DATA
    PC_DATA --> INFERENCE
    INFERENCE --> OUTPUT
```

The inference pipeline constructs queries dynamically based on the prediction request geometry's `oe_start_time` and `oe_end_time` properties, ensuring that predictions use the appropriate temporal data range.

**Sources**: [docs/forest_loss_driver.md:67-96]()

## Harmonization

Sentinel-2 harmonization addresses radiometric differences between Sentinel-2A and Sentinel-2B satellites. When `harmonize: true`, the data source applies offset corrections based on the [Sentinel-2 Radiometric Offset](https://planetarycomputer.microsoft.com/docs/tutorials/sentinel-2-radiometric-offsets/) methodology.

| Band | Offset (DN) | Purpose |
|------|-------------|---------|
| B02 (Blue) | -1000 | Correct S2A/S2B differences |
| B03 (Green) | -1000 | Ensure temporal consistency |
| B04 (Red) | -1000 | Enable multi-temporal analysis |
| Other bands | 0 | No correction needed |

This correction is essential for time series analysis where scenes may come from different satellites. Without harmonization, temporal discontinuities would appear as the operational satellite switches between S2A and S2B.

**Sources**: [olmoearth_run_data/awf/dataset.json:50]()

## Example Configurations

### Standard 12-Timestep Configuration

Used by most land cover classification models:

```json
{
  "data_source": {
    "class_path": "rslearn.data_sources.planetary_computer.Sentinel2",
    "ingest": false,
    "init_args": {
      "cache_dir": "cache/planetary_computer",
      "harmonize": true,
      "sort_by": "eo:cloud_cover"
    },
    "query_config": {
      "max_matches": 12,
      "min_matches": 12,
      "period_duration": "30d",
      "space_mode": "PER_PERIOD_MOSAIC"
    }
  }
}
```

This configuration retrieves 12 monthly mosaics spanning one year, selecting the clearest pixels within each 30-day period.

**Sources**: [olmoearth_run_data/awf/dataset.json:45-59](), [olmoearth_run_data/nandi/dataset.json:45-59]()

### High-Frequency Configuration

Used by LFMC model for shorter temporal periods:

```json
{
  "query_config": {
    "max_matches": 12,
    "min_matches": 12,
    "period_duration": "14d",
    "space_mode": "PER_PERIOD_MOSAIC"
  }
}
```

This configuration creates 12 bi-weekly mosaics spanning 168 days, providing higher temporal resolution for monitoring rapidly changing conditions like vegetation moisture.

**Sources**: [docs/lfmc.md:32-35]()

## Error Handling

The Planetary Computer integration includes several error handling mechanisms:

| Condition | Behavior |
|-----------|----------|
| `min_matches` not met | Query fails with error, window skipped |
| No scenes in period | Period returns null, handled by downstream transforms |
| API rate limiting | Automatic retry with exponential backoff |
| Cache corruption | Re-download from Planetary Computer |
| Network timeout | Retry up to 3 times before failing |

These mechanisms ensure robustness during large-scale training and inference operations where thousands of queries may be executed.

**Sources**: [olmoearth_run_data/awf/dataset.json:54-55]()

## Performance Considerations

### Query Optimization

To minimize latency and API load:
1. **Batch processing**: Group nearby windows to reuse cached tiles
2. **Spatial clustering**: Process spatially adjacent areas sequentially
3. **Temporal alignment**: Use consistent period durations across queries
4. **Cache warmup**: Pre-populate cache for large inference jobs

### Bandwidth Management

Planetary Computer data access is bandwidth-intensive. Typical bandwidth requirements:

| Operation | Data Volume | Duration |
|-----------|-------------|----------|
| Single window (256×256, 12 timesteps) | ~50 MB | 2-5 seconds |
| Training batch (32 windows) | ~1.6 GB | 1-2 minutes |
| Large inference (1000 km²) | ~100 GB | 2-4 hours |

The caching system significantly reduces these requirements for repeated operations on the same geographic areas.

**Sources**: [olmoearth_run_data/awf/dataset.json](), [olmoearth_run_data/nandi/dataset.json]()

---

# Page: Development Guide

# Development Guide

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/build-test.yml](.github/workflows/build-test.yml)
- [Dockerfile](Dockerfile)
- [docs/internal.md](docs/internal.md)
- [olmoearth_projects/utils/label_quality/__init__.py](olmoearth_projects/utils/label_quality/__init__.py)
- [olmoearth_run_data/sample/model.yaml](olmoearth_run_data/sample/model.yaml)
- [olmoearth_run_data/satlas_solar_farm/model.yaml](olmoearth_run_data/satlas_solar_farm/model.yaml)
- [pyproject.toml](pyproject.toml)
- [tests/integration/olmoearth_run/test_olmoearth_run.py](tests/integration/olmoearth_run/test_olmoearth_run.py)
- [tests/unit/utils/label_quality/test_wrapper.py](tests/unit/utils/label_quality/test_wrapper.py)
- [uv.lock](uv.lock)

</details>



This guide covers the complete development workflow for contributing to the olmoearth_projects repository, including environment setup, testing procedures, CI/CD processes, and the bifurcated development model between rslearn_projects (research/development) and olmoearth_projects (production/deployment). For information about training models and fine-tuning, see [Model Training](#5). For information about running inference, see [Inference and Deployment](#7).

---

## Development Environment Setup

The repository uses `uv` for fast, reliable Python dependency management and requires Python 3.11 or higher.

### Dependency Management

The project's dependencies are defined in [pyproject.toml:12-21]() and locked in [uv.lock](). The main dependencies include:

| Package | Purpose |
|---------|---------|
| `rslearn[extra]>=0.0.18` | Core training and data processing framework |
| `olmoearth-runner>=0.1.10` | Inference pipeline execution |
| `olmoearth_pretrain` | OlmoEarth encoder models |
| `geopandas>=1.1.1` | Geospatial data manipulation |
| `wandb>=0.21` | Experiment tracking |
| `PyYAML>=6` | Configuration file parsing |

### Local Development Setup

```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the repository
git clone https://github.com/allenai/olmoearth_projects.git
cd olmoearth_projects

# Create virtual environment and install dependencies
uv sync --all-extras

# Activate the virtual environment
source .venv/bin/activate
```

### Development Dependencies

Additional development tools are specified in [pyproject.toml:24-34]() and include:

- **ruff** (>=0.7): Fast Python linter and formatter
- **mypy** (>=1.17.1): Static type checker
- **pytest** (>=8.2): Testing framework
- **pre-commit** (>=4.3.0): Git hook management
- **interrogate** (>=1.7.0): Docstring coverage checker

**Sources**: [pyproject.toml:1-67](), [uv.lock:1-21]()

---

## Development Workflow Architecture

The repository follows a bifurcated development model where code progresses through distinct stages from research to production.

### Workflow Overview Diagram

```mermaid
graph TB
    subgraph "rslearn_projects Repository"
        DEV_CODE["rslp/[project_name]/<br/>Data Curation Scripts<br/>Window Creation Code"]
        DEV_CONFIG["data/[project_name]/<br/>[version_id]/<br/>dataset.json<br/>model.yaml"]
        DEV_DATASET["WEKA Storage<br/>/weka/dfive-default/<br/>rslearn-eai/datasets/"]
        DEV_TRAIN["Fine-tuning Jobs<br/>Beaker/Saturn Cluster<br/>GPU Training"]
        DEV_CHECKPOINT["Model Checkpoints<br/>WEKA Storage<br/>epoch=X-step=Y.ckpt"]
    end
    
    subgraph "olmoearth_projects Repository"
        PROD_CONFIG["olmoearth_run_data/<br/>[project_name]/<br/>model.yaml<br/>dataset.json<br/>olmoearth_run.yaml"]
        PROD_CODE["olmoearth_projects/<br/>[project_name]/<br/>Supporting Code"]
        PROD_GCS["GCS Storage<br/>gs://rslearn-eai/<br/>model_checkpoints/"]
        PROD_INFERENCE["OlmoEarth Studio<br/>Production Inference<br/>olmoearth_run Pipeline"]
    end
    
    DEV_CODE --> DEV_CONFIG
    DEV_CONFIG --> DEV_DATASET
    DEV_DATASET --> DEV_TRAIN
    DEV_TRAIN --> DEV_CHECKPOINT
    
    DEV_CONFIG -->|"Copy configs"| PROD_CONFIG
    DEV_CODE -->|"Copy supporting code"| PROD_CODE
    DEV_CHECKPOINT -->|"Publish for inference"| PROD_GCS
    
    PROD_CONFIG --> PROD_INFERENCE
    PROD_CODE --> PROD_INFERENCE
    PROD_GCS --> PROD_INFERENCE
```

**Sources**: [docs/internal.md:1-56](), Diagram 5 from high-level architecture

### Project Code Organization

When developing a new model or application, code should be organized according to this structure:

**In rslearn_projects (Development Phase)**:
1. Data curation and window creation scripts: `rslp/[project_name]/`
2. Configuration files: `data/[project_name]/[version_id]/`
3. rslearn datasets: `/weka/dfive-default/rslearn-eai/datasets/[project_name]/[version_id]`

**In olmoearth_projects (Deployment Phase)**:
1. Deployment configurations: `olmoearth_run_data/[project_name]/`
2. Supporting code: `olmoearth_projects/[project_name]/`
3. Model checkpoints: `gs://rslearn-eai/model_checkpoints/[project_name]/`

**Sources**: [docs/internal.md:3-29]()

### Development Process Flow

```mermaid
graph LR
    IDEA["New Model<br/>Concept"] --> CURATE["Data Curation<br/>rslp/[project]/"]
    CURATE --> WINDOWS["Window Creation<br/>create_windows_*.py"]
    WINDOWS --> QUALITY["Quality Assessment<br/>check_label_quality"]
    QUALITY --> DATASET["rslearn Dataset<br/>/weka/.../datasets/"]
    DATASET --> TRAIN["Fine-tuning<br/>rslp_finetuning.py"]
    TRAIN --> CHECKPOINT["Checkpoint<br/>/weka/.../checkpoints/"]
    CHECKPOINT --> COPY["Copy to<br/>olmoearth_projects"]
    COPY --> DEPLOY["Deploy to<br/>OlmoEarth Studio"]
```

**Sources**: [docs/internal.md:3-29](), Diagram 5 from high-level architecture

---

## Testing Infrastructure

The repository includes comprehensive unit and integration tests to ensure code quality and functionality.

### Test Organization Structure

```mermaid
graph TB
    subgraph "Test Suite Organization"
        TEST_ROOT["tests/"]
        UNIT["unit/<br/>Fast, Isolated Tests"]
        INTEGRATION["integration/<br/>End-to-End Tests"]
        
        UNIT_LQ["unit/utils/label_quality/<br/>test_wrapper.py<br/>test_spatial_clustering.py<br/>test_spatial_extent.py<br/>test_label_imbalance.py"]
        
        INT_OER["integration/olmoearth_run/<br/>test_olmoearth_run.py<br/>Full Pipeline Tests"]
    end
    
    TEST_ROOT --> UNIT
    TEST_ROOT --> INTEGRATION
    UNIT --> UNIT_LQ
    INTEGRATION --> INT_OER
```

### Unit Tests

Unit tests focus on testing individual components in isolation. They are fast and do not require external resources like GPUs or cloud storage.

**Example: Label Quality Tests**

The label quality utilities have unit tests at [tests/unit/utils/label_quality/test_wrapper.py:1-23]():

```python
# Unit test structure
def test_label_quality_wrapper() -> None:
    # Create test data
    gdf = gpd.GeoDataFrame(...)
    
    # Run the function being tested
    check_label_quality(gdf, checks_to_run=["label_imbalance"])
    
    # Assertions would go here
```

Unit tests verify components like:
- **label_imbalance**: Checks class distribution balance
- **spatial_clustering**: Measures spatial autocorrelation using F1 score
- **spatial_extent**: Analyzes geographic coverage

The `check_label_quality` function at [olmoearth_projects/utils/label_quality/__init__.py:14-61]() orchestrates multiple checks and displays results in a formatted table.

**Running Unit Tests**:
```bash
# Run all unit tests
pytest tests/unit -vv

# Run specific test file
pytest tests/unit/utils/label_quality/test_wrapper.py -vv
```

**Sources**: [tests/unit/utils/label_quality/test_wrapper.py:1-23](), [olmoearth_projects/utils/label_quality/__init__.py:1-61]()

### Integration Tests

Integration tests validate complete workflows, including data loading, model inference, and result generation. These tests may require access to cloud resources and take longer to execute.

**Example: OlmoEarth Run Pipeline Test**

The [tests/integration/olmoearth_run/test_olmoearth_run.py:21-119]() test validates the entire inference pipeline:

```mermaid
graph LR
    SETUP["Test Setup<br/>tmp_path<br/>config_dir"] --> CONFIG["Copy Configs<br/>dataset.json<br/>model.yaml<br/>olmoearth_run.yaml"]
    CONFIG --> CUSTOMIZE["Customize<br/>Request Geometry<br/>Small AOI"]
    CUSTOMIZE --> EXECUTE["olmoearth_run()<br/>Full Pipeline"]
    EXECUTE --> VALIDATE["Validate Output<br/>Check GeoTIFF<br/>Solar Farm %"]
```

The test performs:
1. Creates a small test area centered on a known solar farm
2. Configures the pipeline with single-window processing
3. Executes the full `olmoearth_run` pipeline
4. Validates the output raster contains expected solar farm percentage

**Running Integration Tests**:
```bash
# Run all integration tests (requires GCP credentials)
pytest tests/integration -vv --forked

# Run with pytest-xdist for parallelization
pytest tests/integration -vv --forked -n auto
```

**Sources**: [tests/integration/olmoearth_run/test_olmoearth_run.py:1-119]()

### Test Configuration

Test configuration is defined in [pyproject.toml:60-66]():

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = ["--import-mode=importlib"]
```

The `--forked` flag in integration tests ensures each test runs in an isolated process, preventing memory leaks from model loading.

**Sources**: [pyproject.toml:60-66]()

---

## CI/CD Pipeline

The repository uses GitHub Actions for continuous integration and deployment, automatically building Docker images and running tests on every push and pull request.

### GitHub Actions Workflow

```mermaid
graph TB
    TRIGGER["Trigger<br/>Push to main<br/>Pull Request"] --> BUILD["Build Job<br/>ubuntu-latest"]
    
    subgraph "Build Job Steps"
        CHECKOUT["Checkout Code<br/>actions/checkout@v4"]
        LOGIN["Docker Login<br/>ghcr.io"]
        META["Extract Metadata<br/>Tags & Labels"]
        CLEANUP["Cleanup Disk<br/>Remove Docker Images"]
        BUILD_PUSH["Build & Push<br/>Docker Image"]
        STORE["Store Image Name<br/>Output to test job"]
    end
    
    subgraph "Test Job Steps"
        TEST_CHECKOUT["Checkout Code"]
        TEST_LOGIN["Docker Login"]
        PULL["Pull Built Image"]
        GCP_AUTH["GCP Auth<br/>Service Account"]
        UNIT_TEST["Run Unit Tests<br/>pytest tests/unit"]
        INT_TEST["Run Integration Tests<br/>pytest tests/integration"]
        CLEANUP_TEST["Cleanup<br/>Prune Images"]
    end
    
    BUILD --> CHECKOUT
    CHECKOUT --> LOGIN
    LOGIN --> META
    META --> CLEANUP
    CLEANUP --> BUILD_PUSH
    BUILD_PUSH --> STORE
    
    STORE --> TEST_CHECKOUT
    TEST_CHECKOUT --> TEST_LOGIN
    TEST_LOGIN --> PULL
    PULL --> GCP_AUTH
    GCP_AUTH --> UNIT_TEST
    UNIT_TEST --> INT_TEST
    INT_TEST --> CLEANUP_TEST
```

### Build Job Configuration

The build job is defined in [.github/workflows/build-test.yml:19-75]() and performs:

1. **Checkout**: Clone the repository
2. **Docker Login**: Authenticate to GitHub Container Registry
3. **Metadata Extraction**: Generate tags (SHA, latest)
4. **Disk Cleanup**: Free space for Docker build
5. **Build & Push**: Build image and push to `ghcr.io/allenai/olmoearth_projects`

**Image Tagging Strategy**:
```yaml
tags: |
  type=sha,format=long     # Full commit SHA
  type=sha,format=short    # Short commit SHA
  type=raw,value=latest,enable={{is_default_branch}}
```

The image is tagged with the commit SHA for traceability and `latest` for the main branch.

**Sources**: [.github/workflows/build-test.yml:19-75]()

### Test Job Configuration

The test job is defined in [.github/workflows/build-test.yml:76-122]() and runs on `ubuntu-latest-m` (medium-sized runner) to handle model loading:

**Unit Tests Execution** [.github/workflows/build-test.yml:99-105]():
```bash
docker run --rm \
  -e CI="true" \
  ${{ needs.build.outputs.ghcr_docker_image }} \
  pytest tests/unit -vv
```

**Integration Tests Execution** [.github/workflows/build-test.yml:107-115]():
```bash
docker run --rm \
  -e CI="true" \
  -v ${GOOGLE_GHA_CREDS_PATH}:/tmp/gcp-credentials.json:ro \
  -e GOOGLE_APPLICATION_CREDENTIALS=/tmp/gcp-credentials.json \
  ${{ needs.build.outputs.ghcr_docker_image }} \
  pytest tests/integration -vv --forked
```

The `--forked` flag is critical for integration tests to prevent memory issues when loading large models.

**Sources**: [.github/workflows/build-test.yml:76-122]()

### Concurrency Control

The workflow includes concurrency control at [.github/workflows/build-test.yml:14-16]():

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

This ensures that only one workflow runs per branch at a time, canceling older runs when new commits are pushed.

**Sources**: [.github/workflows/build-test.yml:14-16]()

---

## Docker Environment

The Docker container provides a consistent, reproducible environment for development, testing, and deployment.

### Docker Architecture

```mermaid
graph TB
    BASE["Base Image<br/>pytorch/pytorch:2.7.0<br/>cuda12.8-cudnn9-runtime"] --> GIT["Install Git<br/>Configure GitHub Token"]
    GIT --> UV["Copy uv Binary<br/>ghcr.io/astral-sh/uv"]
    UV --> WORKDIR["Set Working Directory<br/>/olmoearth_projects"]
    WORKDIR --> COPY_LOCK["Copy Dependency Files<br/>pyproject.toml<br/>uv.lock"]
    COPY_LOCK --> SYNC_DEPS["Install Dependencies<br/>uv sync --all-extras<br/>--no-install-project"]
    SYNC_DEPS --> ENV_PATH["Add to PATH<br/>/olmoearth_projects/.venv/bin"]
    ENV_PATH --> COPY_CODE["Copy Source Code<br/>./ → /olmoearth_projects"]
    COPY_CODE --> SYNC_PROJ["Install Project<br/>uv sync --all-extras --locked"]
```

### Dockerfile Structure

The [Dockerfile:1-19]() is optimized for layer caching and build speed:

**Base Image Selection** [Dockerfile:1]():
```dockerfile
FROM pytorch/pytorch:2.7.0-cuda12.8-cudnn9-runtime
```
Uses the official PyTorch image with CUDA 12.8 and cuDNN 9 support for GPU acceleration.

**Git Configuration** [Dockerfile:4-6]():
```dockerfile
ARG GITHUB_TOKEN
RUN git config --global url."https://x-access-token:${GITHUB_TOKEN}@github.com/".insteadOf "https://github.com/"
```
Configures Git to use the provided GitHub token for accessing private repositories (like `olmoearth_pretrain`).

**UV Integration** [Dockerfile:8]():
```dockerfile
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
```
Copies the `uv` binary from the official image for fast dependency resolution.

**Dependency Installation** [Dockerfile:12-14]():
```dockerfile
COPY pyproject.toml uv.lock /olmoearth_projects/
RUN uv sync --all-extras --no-install-project
```
Installs dependencies first (without the project itself) to maximize Docker layer caching.

**Project Installation** [Dockerfile:16-18]():
```dockerfile
ENV PATH="/olmoearth_projects/.venv/bin:$PATH"
COPY ./ /olmoearth_projects
RUN uv sync --all-extras --locked
```
Copies source code and installs the project with locked dependencies.

**Sources**: [Dockerfile:1-19]()

### Building the Docker Image Locally

```bash
# Build with GitHub token for private repo access
docker build \
  --build-arg GITHUB_TOKEN=<your_token> \
  -t olmoearth_projects:local \
  .

# Run tests in the container
docker run --rm olmoearth_projects:local pytest tests/unit -vv

# Interactive development shell
docker run --rm -it \
  -v $(pwd):/olmoearth_projects \
  olmoearth_projects:local \
  bash
```

### Environment Variables

The Docker container respects several environment variables:

| Variable | Purpose | Example |
|----------|---------|---------|
| `WANDB_MODE` | Control Weights & Biases logging | `disabled` for tests |
| `GOOGLE_APPLICATION_CREDENTIALS` | GCP service account key path | `/tmp/gcp-credentials.json` |
| `CI` | Indicate CI environment | `true` in GitHub Actions |
| `NUM_WORKERS` | PyTorch DataLoader workers | Template in model.yaml |
| `DATASET_PATH` | Path to rslearn dataset | Template in model.yaml |

**Sources**: [Dockerfile:1-19](), [.github/workflows/build-test.yml:99-115]()

---

## Code Quality Standards

The repository enforces code quality through automated tools configured in [pyproject.toml]().

### Linting and Formatting with Ruff

**Ruff Configuration** [pyproject.toml:48-58]():
```toml
[tool.ruff]
fix = true  # Auto-fix issues when possible

[tool.ruff.lint]
extend-select = ["D", "I", "UP"]  # Docstrings, Imports, Upgrades

[tool.ruff.lint.per-file-ignores]
"tests/**" = ["D"]  # Skip docstring checks in tests

[tool.ruff.lint.pydocstyle]
convention = "google"  # Google-style docstrings
```

**Selected Ruff Rules**:
- **D**: Enforce docstrings on public modules, classes, and functions
- **I**: Sort and organize imports
- **UP**: Upgrade syntax for newer Python versions

**Running Ruff**:
```bash
# Check for issues
ruff check .

# Auto-fix issues
ruff check --fix .

# Format code
ruff format .
```

**Sources**: [pyproject.toml:48-58]()

### Type Checking with MyPy

MyPy is configured as a development dependency [pyproject.toml:27]() to catch type errors:

```bash
# Run type checking
mypy olmoearth_projects/
```

### Pre-commit Hooks

Pre-commit hooks are recommended for automated quality checks before commits [pyproject.toml:28]():

```bash
# Install pre-commit hooks
pre-commit install

# Run manually on all files
pre-commit run --all-files
```

### Docstring Coverage

The `interrogate` tool checks docstring coverage [pyproject.toml:26]():

```bash
# Check docstring coverage
interrogate -v olmoearth_projects/
```

**Sources**: [pyproject.toml:24-34]()

---

## Contributing Workflow

### Step-by-Step Contribution Process

1. **Create a Feature Branch**:
   ```bash
   git checkout -b feature/my-new-feature
   ```

2. **Make Changes**:
   - Add code to appropriate directories
   - Include unit tests for new functionality
   - Update documentation as needed

3. **Run Quality Checks**:
   ```bash
   # Format and lint
   ruff format .
   ruff check --fix .
   
   # Type check
   mypy olmoearth_projects/
   
   # Run tests
   pytest tests/unit -vv
   pytest tests/integration -vv --forked
   ```

4. **Commit Changes**:
   ```bash
   git add .
   git commit -m "Add feature: description"
   ```

5. **Push and Create Pull Request**:
   ```bash
   git push origin feature/my-new-feature
   ```
   Then open a pull request on GitHub.

6. **CI/CD Validation**:
   - GitHub Actions will automatically build Docker image
   - Run unit and integration tests
   - Verify all checks pass before merging

### Pull Request Requirements

All pull requests must:
- Pass all CI/CD checks (build, unit tests, integration tests)
- Follow code quality standards (Ruff, MyPy)
- Include tests for new functionality
- Update documentation when adding features

**Sources**: [.github/workflows/build-test.yml:1-122](), [pyproject.toml:48-58]()

---

## Common Development Tasks

### Adding a New Model Application

When adding a new model to the repository:

1. **Development Phase** (in rslearn_projects):
   - Create data curation scripts in `rslp/[project_name]/`
   - Generate training windows with proper spatial splitting
   - Run label quality checks using utilities from [olmoearth_projects/utils/label_quality/]()
   - Create rslearn dataset and store in `/weka/dfive-default/rslearn-eai/datasets/`

2. **Deployment Phase** (in olmoearth_projects):
   - Copy configurations to `olmoearth_run_data/[project_name]/`
   - Add supporting code to `olmoearth_projects/[project_name]/`
   - Publish checkpoint to `gs://rslearn-eai/model_checkpoints/`
   - Document in project README

### Running Local Fine-tuning

While fine-tuning typically happens on GPU clusters via rslearn_projects, you can test configurations locally:

```bash
# Set environment variables
export WANDB_PROJECT=my_project
export WANDB_NAME=local_test
export DATASET_PATH=/path/to/dataset
export TRAINER_DATA_PATH=/tmp/checkpoints

# Run training (with small dataset for testing)
python -m rslearn.train.rslp_finetuning fit \
  --config olmoearth_run_data/[project]/model.yaml
```

### Testing Configuration Changes

Before deploying configuration changes:

1. Create a small test geometry
2. Run the integration test with your config
3. Verify output matches expectations

Example using the test from [tests/integration/olmoearth_run/test_olmoearth_run.py]():

```python
# Customize for your model
checkpoint_path = "path/to/your/checkpoint.ckpt"
config_dir = "olmoearth_run_data/your_project/"
olmoearth_run(config_path=config_dir, checkpoint_path=checkpoint_path)
```

**Sources**: [docs/internal.md:3-29](), [tests/integration/olmoearth_run/test_olmoearth_run.py:1-119]()

---

# Page: Development Workflow

# Development Workflow

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/internal.md](docs/internal.md)
- [olmoearth_run_data/mozambique_lulc/README.md](olmoearth_run_data/mozambique_lulc/README.md)
- [olmoearth_run_data/mozambique_lulc/config.json](olmoearth_run_data/mozambique_lulc/config.json)
- [olmoearth_run_data/sample/model.yaml](olmoearth_run_data/sample/model.yaml)
- [olmoearth_run_data/satlas_solar_farm/model.yaml](olmoearth_run_data/satlas_solar_farm/model.yaml)
- [tests/integration/olmoearth_run/test_olmoearth_run.py](tests/integration/olmoearth_run/test_olmoearth_run.py)

</details>



This document explains the bifurcated development workflow used in the olmoearth_projects ecosystem. The workflow separates research and experimentation activities (conducted in the `rslearn_projects` repository) from deployment and inference activities (conducted in this repository). This separation enables clean organization of experimental code while maintaining production-ready configurations and inference pipelines.

For information about model training configuration details, see [Training Configuration Files](#5.1). For details about the inference pipeline, see [olmoearth_run Pipeline](#7.1). For CI/CD processes, see [CI/CD Pipeline](#9.2).

## Repository Structure Overview

The development workflow spans two repositories with distinct purposes:

| Repository | Purpose | Key Contents |
|------------|---------|--------------|
| `rslearn_projects` | Research and development | Data curation scripts, programmatic window creation, experimental configs, fine-tuning job management |
| `olmoearth_projects` | Deployment and production | Production configs, inference scripts, supporting utilities, documentation |

This bifurcated structure enables:
- **Rapid experimentation** in `rslearn_projects` without affecting production systems
- **Clean production code** in `olmoearth_projects` with only deployment-relevant files
- **Version control** with separate commit histories for research vs. production
- **Clear handoff** from research to production stages

```mermaid
graph TB
    subgraph "rslearn_projects Repository"
        DATACUR["rslp/[project_name]/<br/>Data Curation Scripts"]
        WINDOWGEN["rslp/[project_name]/<br/>Window Generation Scripts"]
        DEVCONFIG["data/[project_name]/[version_id]/<br/>Development Configs"]
        FINETUNE["rslp/common/<br/>Fine-tuning Commands"]
    end
    
    subgraph "WEKA Storage"
        DATASET["/weka/dfive-default/rslearn-eai/<br/>datasets/[project_name]/[version_id]/<br/>rslearn Dataset"]
        CHECKPOINT["/weka/dfive-default/rslearn-eai/<br/>checkpoints/[project_name]/<br/>Model Checkpoints"]
    end
    
    subgraph "olmoearth_projects Repository"
        PRODCONFIG["olmoearth_run_data/<br/>[project_name]/[version_id]/<br/>model.yaml, dataset.json,<br/>olmoearth_run.yaml"]
        SUPPORTCODE["olmoearth_projects/projects/<br/>[project_name]/<br/>create_windows_for_lulc.py<br/>check_label_quality.py"]
        INFERENCE["olmoearth_run/<br/>Inference Pipeline"]
    end
    
    subgraph "Public Distribution"
        GCS["gs://rslearn-eai/<br/>model_checkpoints/<br/>Public Checkpoints"]
        STUDIO["OlmoEarth Studio<br/>olmoearth.allenai.org"]
    end
    
    DATACUR --> DATASET
    WINDOWGEN --> DATASET
    DEVCONFIG --> DATASET
    FINETUNE --> CHECKPOINT
    DATASET --> FINETUNE
    
    DEVCONFIG -.->|"copy configs"| PRODCONFIG
    WINDOWGEN -.->|"migrate code"| SUPPORTCODE
    CHECKPOINT -.->|"publish"| GCS
    
    PRODCONFIG --> INFERENCE
    SUPPORTCODE --> INFERENCE
    GCS --> STUDIO
    INFERENCE --> STUDIO
```

**Sources:** [docs/internal.md:1-29]()

## Development Phase

The development phase occurs in the `rslearn_projects` repository and focuses on data preparation, experimentation, and model training.

### Step 1: Data Curation

Data curation scripts are added to `rslp/[project_name]/` in `rslearn_projects`. These scripts typically:
- Process raw geospatial data (GPKG files, shapefiles)
- Generate training windows
- Create label rasters
- Perform spatial data splitting

Example location for Mozambique LULC:
- `rslp/mozambique_lulc/create_windows_for_lulc.py`
- `rslp/mozambique_lulc/create_label_raster.py`
- `rslp/mozambique_lulc/update_train_test_split.py`

**Sources:** [docs/internal.md:8-9](), [olmoearth_run_data/mozambique_lulc/README.md:14-37]()

### Step 2: Window Creation

Training windows are created from raw data using project-specific scripts:

```mermaid
graph LR
    GPKG["Raw GPKG Files<br/>/weka/dfive-default/<br/>yawenz/datasets/<br/>mozambique/"]
    SCRIPT["create_windows_for_lulc.py<br/>--gpkg_dir<br/>--ds_path<br/>--window_size 32"]
    WINDOWS["Window GeoJSONs<br/>train/val/test splits"]
    DATASET["rslearn Dataset<br/>/weka/dfive-default/<br/>rslearn-eai/datasets/<br/>[project_name]/[version_id]/"]
    
    GPKG --> SCRIPT
    SCRIPT --> WINDOWS
    WINDOWS --> DATASET
```

The window creation process:
1. Reads point or polygon labels from GPKG files
2. Creates fixed-size windows (typically 32-1024 pixels)
3. Applies spatial data splitting using `SpatialDataSplitter`
4. Writes output windows as GeoJSON features

**Sources:** [olmoearth_run_data/mozambique_lulc/README.md:16-21]()

### Step 3: Configuration and Dataset Preparation

After window creation, configurations are added and the dataset is prepared:

1. **Copy `config.json`** to the dataset root at `/weka/dfive-default/rslearn-eai/datasets/[project_name]/[version_id]/config.json`
   - Defines data layers (Sentinel-2, labels, etc.)
   - Specifies data source configurations (Planetary Computer queries)
   - Sets tile storage parameters

2. **Run `rslearn dataset prepare`** to prepare the dataset:
   ```bash
   rslearn dataset prepare --root $DATASET_PATH --workers 64 \
     --no-use-initial-job --retry-max-attempts 8 --retry-backoff-seconds 60
   ```

3. **Launch data materialization jobs** to download satellite imagery:
   ```bash
   python -m rslp.main common launch_data_materialization_jobs \
     --image yawenzzzz/rslp20251112h --ds_path $DATASET_PATH \
     --clusters+=ai2/neptune-cirrascale --num_jobs 5
   ```

**Sources:** [olmoearth_run_data/mozambique_lulc/README.md:22-32](), [olmoearth_run_data/mozambique_lulc/config.json:1-69]()

### Step 4: Label Quality Assessment

Before training, label quality is assessed using utility scripts. These scripts should be added to the deployment repository for reusability:

```bash
python olmoearth_projects/projects/mozambique_lulc/check_label_quality.py \
  --ds_path /weka/dfive-default/rslearn-eai/datasets/crop/mozambique_lulc/20251202 \
  --split train
```

Quality metrics computed:
- **Label Imbalance**: Class distribution (should be balanced)
- **Spatial Clustering F1**: Measure of spatial autocorrelation
- **Spatial Extent**: Geographic coverage per class

**Sources:** [olmoearth_run_data/mozambique_lulc/README.md:51-115]()

### Step 5: Fine-tuning

Fine-tuning jobs are launched from `rslearn_projects` using the `rslp` command-line interface:

```bash
python -m rslp.main olmoearth_pretrain launch_finetune \
  --image_name yawenzzzz/rslp20251112h \
  --config_paths+=olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml \
  --cluster+=ai2/saturn \
  --rslp_project <MY_RSLP_PROJECT_NAME> \
  --experiment_id <MY_EXPERIMENT_ID>
```

Training configuration includes:
- **`model.yaml`**: Defines encoder (OlmoEarth), decoder, tasks
- **`rslp_finetuning.yaml`**: Specifies training parameters, callbacks, data paths
- Training runs on Beaker clusters (Saturn, Neptune-Cirrascale)
- Checkpoints saved to `/weka/dfive-default/rslearn-eai/checkpoints/`

**Sources:** [olmoearth_run_data/mozambique_lulc/README.md:117-123]()

### Step 6: Testing

Model testing is performed interactively on Beaker:

```bash
# Start interactive session with GPU
beaker session create --remote --bare --budget ai2/es-platform \
  --cluster ai2/saturn \
  --mount src=weka,ref=dfive-default,dst=/weka/dfive-default \
  --image beaker://yawenzzzz/rslp20251112h --gpus 1

# Navigate to working directory
cd /weka/dfive-default/gabrielt/olmoearth_projects

# Set environment variable
export RSLP_PREFIX=/weka/dfive-default/rslearn-eai

# Run test
python -m rslp.rslearn_main model test \
  --config olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml \
  --rslp_experiment <MY_EXPERIMENT_ID> \
  --rslp_project <MY_RSLP_PROJECT_NAME> \
  --force_log=true --load_best=true --verbose true
```

**Sources:** [olmoearth_run_data/mozambique_lulc/README.md:125-131]()

## Deployment Phase

Once model training is complete and validated, configurations and supporting code are migrated to `olmoearth_projects` for deployment.

### Step 1: Configuration Migration

```mermaid
graph LR
    subgraph "rslearn_projects"
        SRCMODEL["data/[project_name]/<br/>[version_id]/<br/>model.yaml"]
        SRCDATASET["data/[project_name]/<br/>[version_id]/<br/>dataset.json"]
        SRCRUN["data/[project_name]/<br/>[version_id]/<br/>olmoearth_run.yaml"]
    end
    
    subgraph "olmoearth_projects"
        DSTMODEL["olmoearth_run_data/<br/>[project_name]/<br/>[version_id]/<br/>model.yaml"]
        DSTDATASET["olmoearth_run_data/<br/>[project_name]/<br/>[version_id]/<br/>dataset.json"]
        DSTRUN["olmoearth_run_data/<br/>[project_name]/<br/>[version_id]/<br/>olmoearth_run.yaml"]
        README["olmoearth_run_data/<br/>[project_name]/<br/>README.md"]
    end
    
    SRCMODEL -.->|"copy"| DSTMODEL
    SRCDATASET -.->|"copy"| DSTDATASET
    SRCRUN -.->|"copy or create"| DSTRUN
    DSTMODEL --> README
    DSTDATASET --> README
    DSTRUN --> README
```

Configuration files to copy:
- **`model.yaml`**: Contains `RslearnLightningModule` configuration with encoder/decoder definitions
- **`dataset.json`**: Defines data layers, query configurations, tile storage
- **`olmoearth_run.yaml`**: Specifies inference-specific settings like partitioning strategies

Each project directory should include a `README.md` documenting:
- Source of configurations
- Version history
- Dataset locations on WEKA
- Special notes about `olmoearth_run.yaml` settings

**Sources:** [docs/internal.md:18-26]()

### Step 2: Supporting Code Migration

Supporting code used during development may be migrated if needed for deployment:

```
olmoearth_projects/projects/[project_name]/
├── create_windows_for_lulc.py       # Window generation
├── check_label_quality.py           # Quality assessment
├── create_label_raster.py           # Label processing
└── update_train_test_split.py       # Data splitting
```

This code enables:
- Regenerating datasets with updated parameters
- Assessing label quality for new data
- Creating additional training windows
- CI/CD integration for quality checks

**Sources:** [docs/internal.md:22-23]()

### Step 3: Checkpoint Publication

For inference-only deployments (not requiring direct WEKA access):

```bash
# Copy from WEKA to Google Cloud Storage
gsutil cp /weka/dfive-default/rslearn-eai/checkpoints/[project_name]/[version].ckpt \
  gs://rslearn-eai/model_checkpoints/[project_name]/[version].ckpt
```

Checkpoint locations:
- **WEKA**: `/weka/dfive-default/rslearn-eai/checkpoints/[project_name]/`
- **GCS**: `gs://rslearn-eai/model_checkpoints/[project_name]/`
- **HuggingFace**: `allenai/OlmoEarth-v1-FT-[TaskName]-Base`

**Sources:** [docs/internal.md:24-26]()

### Step 4: OlmoEarth Studio Deployment

Models deployed to OlmoEarth Studio require:
- Checkpoint accessible from GCS
- Configuration files in `olmoearth_run_data/[project_name]/`
- `prediction_request_geometry.geojson` for spatial/temporal extent
- Metadata defining class mappings and visualization

**Sources:** [olmoearth_run_data/mozambique_lulc/README.md:133-135]()

## Practical Example: Mozambique LULC

The following diagram shows the complete workflow for the Mozambique LULC project:

```mermaid
graph TB
    RAWDATA["Raw GPKG Files<br/>Field Survey Data<br/>Gaza, Zambezia, Manica"]
    
    CREATE["create_windows_for_lulc.py<br/>--gpkg_dir ...<br/>--ds_path $DATASET_PATH<br/>--window_size 32"]
    
    LABEL["create_label_raster.py<br/>--ds_path $DATASET_PATH<br/>Convert point labels to raster"]
    
    CONFIG["Copy config.json<br/>Sentinel-2 configuration<br/>Planetary Computer queries"]
    
    PREPARE["rslearn dataset prepare<br/>--workers 64<br/>--retry-max-attempts 8"]
    
    MATERIALIZE["launch_data_materialization_jobs<br/>--num_jobs 5<br/>Download satellite imagery"]
    
    QUALITY["check_label_quality.py<br/>--split train<br/>Assess spatial clustering,<br/>imbalance, extent"]
    
    FINETUNE["launch_finetune<br/>--config_paths rslp_finetuning.yaml<br/>--cluster ai2/saturn<br/>Train on GPU cluster"]
    
    TEST["model test<br/>Interactive Beaker session<br/>--load_best=true<br/>Evaluate on test set"]
    
    COPY["Copy configs to<br/>olmoearth_run_data/<br/>mozambique_lulc/"]
    
    STUDIO["Deploy to<br/>OlmoEarth Studio<br/>Draw province polygons<br/>Run inference"]
    
    RAWDATA --> CREATE
    CREATE --> LABEL
    LABEL --> CONFIG
    CONFIG --> PREPARE
    PREPARE --> MATERIALIZE
    MATERIALIZE --> QUALITY
    QUALITY --> FINETUNE
    FINETUNE --> TEST
    TEST --> COPY
    COPY --> STUDIO
```

**Key commands executed:**

```bash
# 1. Window creation
export DATASET_PATH=/weka/dfive-default/rslearn-eai/datasets/crop/mozambique_lulc/20251113
python create_windows_for_lulc.py --gpkg_dir /weka/dfive-default/yawenz/datasets/mozambique/train_test_samples \
  --ds_path $DATASET_PATH --window_size 32

# 2. Label rasterization
python create_label_raster.py --ds_path $DATASET_PATH

# 3. Dataset preparation
rslearn dataset prepare --root $DATASET_PATH --workers 64

# 4. Quality assessment
python check_label_quality.py --ds_path $DATASET_PATH --split train

# 5. Fine-tuning
python -m rslp.main olmoearth_pretrain launch_finetune \
  --config_paths+=olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml \
  --cluster+=ai2/saturn

# 6. Testing
python -m rslp.rslearn_main model test --config olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml
```

**Sources:** [olmoearth_run_data/mozambique_lulc/README.md:1-136]()

## Version Management

Dataset versions are tracked on WEKA with systematic naming:

```
/weka/dfive-default/rslearn-eai/datasets/[project_name]/[YYYYMMDD]/
```

Example from Mozambique LULC showing version evolution:

| Version | Changes | Location |
|---------|---------|----------|
| `20251023` | Initial version with train/test split from GPKG | `/weka/.../mozambique_lulc/20251023` |
| `20251113` | Added spatial validation split (val_ratio=0.2) | `/weka/.../mozambique_lulc/20251113` |
| `20251114` | Aligned dates across all provinces | `/weka/.../mozambique_lulc/20251114` |
| `20251202` | Aligned 8-month temporal coverage, updated val_ratio=0.1 | `/weka/.../mozambique_lulc/20251202` |

Each version directory contains:
- `config.json`: Data layer and source configuration
- `tiles/`: Materialized satellite imagery tiles
- `windows/`: Training window GeoJSON files organized by split
- `cache/`: Downloaded raw data cache

Version history should be documented in `data/[project_name]/README.md` in `rslearn_projects` and `olmoearth_run_data/[project_name]/README.md` in `olmoearth_projects`.

**Sources:** [olmoearth_run_data/mozambique_lulc/README.md:39-49](), [docs/internal.md:31-56]()

## Configuration Files Reference

The three key configuration files used across development and deployment:

### model.yaml Structure

Defines the model architecture and training parameters:

```yaml
trainer:
  callbacks:
    - class_path: lightning.pytorch.callbacks.ModelCheckpoint
    - class_path: rslearn.train.callbacks.freeze_unfreeze.FreezeUnfreeze
      init_args:
        module_selector: ["model", "encoder", 0]
        unfreeze_at_epoch: 20
        unfreeze_lr_factor: 10.0
  max_epochs: 500
  
model:
  class_path: rslearn.train.lightning_module.RslearnLightningModule
  init_args:
    model:
      class_path: rslearn.models.multitask.MultiTaskModel
      init_args:
        encoder:
          - class_path: rslearn.models.olmoearth_pretrain.model.OlmoEarth
            init_args:
              model_id: OLMOEARTH_V1_BASE
              patch_size: 8
        decoders:
          class:
            - class_path: rslearn.models.unet.UNetDecoder
            - class_path: rslearn.train.tasks.segmentation.SegmentationHead
    
data:
  class_path: rslearn.train.data_module.RslearnDataModule
  init_args:
    path: ${DATASET_PATH}
    batch_size: 8
    inputs:
      sentinel2_l2a:
        data_type: raster
        layers: ["sentinel2", "sentinel2.1", "sentinel2.2", "sentinel2.3"]
    task:
      class_path: rslearn.train.tasks.multi_task.MultiTask
```

**Sources:** [olmoearth_run_data/satlas_solar_farm/model.yaml:1-166]()

### dataset.json Structure

Defines data layers and acquisition configuration:

```json
{
  "layers": {
    "sentinel2": {
      "type": "raster",
      "data_source": {
        "name": "rslearn.data_sources.planetary_computer.Sentinel2",
        "harmonize": true,
        "query_config": {
          "max_matches": 8,
          "min_matches": 8,
          "period_duration": "30d",
          "space_mode": "PER_PERIOD_MOSAIC"
        }
      },
      "band_sets": [
        {
          "bands": ["B02", "B03", "B04", "B08"],
          "dtype": "uint16"
        }
      ]
    }
  },
  "tile_store": {
    "name": "file",
    "root_dir": "tiles"
  }
}
```

**Sources:** [olmoearth_run_data/mozambique_lulc/config.json:1-69]()

### olmoearth_run.yaml Structure

Defines inference-specific configuration (created during deployment phase):

```yaml
partition_strategies:
  partition_request_geometry:
    class_path: olmoearth_run.runner.tools.partitioners.grid_partitioner.GridPartitioner
    init_args:
      grid_size: 0.5
      
  prepare_window_geometries:
    class_path: olmoearth_run.runner.tools.partitioners.grid_partitioner.GridPartitioner
    init_args:
      grid_size: 256
      output_projection:
        x_resolution: 10
        y_resolution: -10
        
post_processing:
  process_window:
    class_path: olmoearth_run.runner.tools.post_processors.noop_raster.NoopRaster
  process_partition:
    class_path: olmoearth_run.runner.tools.post_processors.combine_geotiff.CombineGeotiff
```

**Sources:** [tests/integration/olmoearth_run/test_olmoearth_run.py:67-87]()

## Testing in Development Workflow

### Unit Testing

Quality assessment utilities are tested in CI:

```python
# tests/projects/mozambique_lulc/test_label_quality.py
def test_spatial_clustering():
    """Test spatial clustering metric computation."""
    
def test_label_imbalance():
    """Test label distribution calculation."""
    
def test_spatial_extent():
    """Test geographic coverage metrics."""
```

**Sources:** Reference to testing framework from [CI/CD Pipeline](#9.2)

### Integration Testing

End-to-end inference pipeline testing:

```python
# tests/integration/olmoearth_run/test_olmoearth_run.py
def test_olmoearth_run_solar_farm(tmp_path, monkeypatch):
    """Test olmoearth_run pipeline on small request geometry."""
    checkpoint_path = "gs://ai2-rslearn-projects-data/projects/..."
    
    # Customize configuration files
    config_dir = tmp_path / "config"
    # Copy dataset.json, create prediction_request_geometry.geojson
    # Modify model.yaml for smaller batch size
    
    # Run inference
    olmoearth_run(
        config_path=config_dir,
        scratch_path=scratch_dir,
        checkpoint_path=checkpoint_path,
    )
    
    # Verify output
    result_fname = result_dir / "*.tif"
    assert result_fname.exists()
```

**Sources:** [tests/integration/olmoearth_run/test_olmoearth_run.py:21-119]()

## Summary

The development workflow follows a clear progression:

1. **Development Phase** (in `rslearn_projects`)
   - Create data curation scripts
   - Generate training windows
   - Prepare datasets with `rslearn dataset prepare`
   - Assess label quality
   - Launch fine-tuning jobs on Beaker
   - Test models interactively

2. **Deployment Phase** (in `olmoearth_projects`)
   - Copy configuration files to `olmoearth_run_data/`
   - Migrate supporting code to `olmoearth_projects/projects/`
   - Publish checkpoints to GCS
   - Deploy to OlmoEarth Studio

3. **Version Control**
   - Track datasets on WEKA with date-based versions
   - Document version history in README files
   - Maintain separate commit histories for research vs. production

This bifurcated approach enables rapid experimentation while maintaining production stability and clear handoff between research and deployment stages.

**Sources:** [docs/internal.md:1-56](), [olmoearth_run_data/mozambique_lulc/README.md:1-136]()

---

# Page: CI/CD Pipeline

# CI/CD Pipeline

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/build-test.yml](.github/workflows/build-test.yml)
- [Dockerfile](Dockerfile)
- [olmoearth_projects/utils/label_quality/__init__.py](olmoearth_projects/utils/label_quality/__init__.py)
- [pyproject.toml](pyproject.toml)
- [tests/unit/utils/label_quality/test_wrapper.py](tests/unit/utils/label_quality/test_wrapper.py)
- [uv.lock](uv.lock)

</details>



## Purpose and Scope

This document describes the Continuous Integration and Continuous Deployment (CI/CD) pipeline for the olmoearth_projects repository. The pipeline automates Docker image building, testing, and publishing to GitHub Container Registry (GHCR) on every push to the main branch and for pull requests. For information about the testing infrastructure and test implementation details, see [Testing](#9.3). For Docker environment configuration specifics, see [Docker Environment](#9.4).

**Sources:** [.github/workflows/build-test.yml:1-122]()

## Pipeline Overview

The CI/CD pipeline is implemented using GitHub Actions and consists of two primary jobs: `build` and `test`. The pipeline executes automatically when:

- Code is pushed to the `main` branch
- Pull requests are opened, synchronized, or reopened

The pipeline uses a concurrency group `${{ github.workflow }}-${{ github.ref }}` with `cancel-in-progress: true` to ensure that only one pipeline run executes per branch at a time, canceling any in-progress runs when new commits are pushed.

**Sources:** [.github/workflows/build-test.yml:1-16]()

## Pipeline Architecture

```mermaid
graph TB
    subgraph "Trigger Events"
        PUSH["Push to main branch"]
        PR["Pull Request<br/>(opened, sync, reopened)"]
    end
    
    subgraph "Build Job<br/>(ubuntu-latest)"
        CHECKOUT1["Checkout repository<br/>actions/checkout@v4"]
        LOGIN1["Log in to GHCR<br/>docker/login-action@v3"]
        META["Extract metadata<br/>docker/metadata-action@v5<br/>Tags: sha, latest"]
        CLEANUP["Cleanup disk space<br/>Remove images, dotnet, ghc, boost"]
        BUILD["Build and push Docker<br/>docker/build-push-action@v6<br/>With GITHUB_TOKEN"]
        STORE["Store image names<br/>Output: ghcr_docker_image"]
    end
    
    subgraph "Test Job<br/>(ubuntu-latest-m)"
        CHECKOUT2["Checkout repository"]
        LOGIN2["Log in to GHCR"]
        PULL["Pull Docker image<br/>from build outputs"]
        GCP["Authenticate to GCP<br/>google-github-actions/auth@v2"]
        UNIT["Run unit tests<br/>pytest tests/unit -vv"]
        INTEGRATION["Run integration tests<br/>pytest tests/integration -vv --forked<br/>with GCP credentials"]
        CLEAN["Cleanup images"]
    end
    
    subgraph "Outputs"
        GHCR["GitHub Container Registry<br/>ghcr.io/allenai/olmoearth_projects<br/>Tags: latest, sha256"]
        RESULTS["Test Results<br/>Unit & Integration"]
    end
    
    PUSH --> CHECKOUT1
    PR --> CHECKOUT1
    CHECKOUT1 --> LOGIN1
    LOGIN1 --> META
    META --> CLEANUP
    CLEANUP --> BUILD
    BUILD --> STORE
    
    STORE --> CHECKOUT2
    CHECKOUT2 --> LOGIN2
    LOGIN2 --> PULL
    PULL --> GCP
    GCP --> UNIT
    UNIT --> INTEGRATION
    INTEGRATION --> CLEAN
    
    BUILD --> GHCR
    INTEGRATION --> RESULTS
```

**Diagram: CI/CD Pipeline Flow** - Shows the complete workflow from trigger events through build and test jobs to final outputs.

**Sources:** [.github/workflows/build-test.yml:18-122]()

## Build Job Configuration

The `build` job runs on `ubuntu-latest` runners and produces a Docker image that is pushed to GitHub Container Registry.

### Build Job Steps

| Step | Action | Purpose |
|------|--------|---------|
| Checkout | `actions/checkout@v4` | Retrieves repository code |
| Login | `docker/login-action@v3` | Authenticates to `ghcr.io` using `GITHUB_TOKEN` |
| Metadata | `docker/metadata-action@v5` | Generates Docker tags and labels |
| Cleanup | Custom shell script | Frees disk space by removing unnecessary files |
| Build & Push | `docker/build-push-action@v6` | Builds image and pushes to registry |
| Store Names | Shell script | Saves image digest for downstream jobs |

**Sources:** [.github/workflows/build-test.yml:19-74]()

### Docker Image Tagging Strategy

The pipeline uses `docker/metadata-action@v5` to generate multiple tags for each image:

```yaml
tags: |
  type=sha,format=long
  type=sha,format=short
  type=raw,value=latest,enable={{is_default_branch}}
```

This produces:
- **Long SHA tag**: `sha-<full-40-char-commit-sha>`
- **Short SHA tag**: `sha-<7-char-commit-sha>`
- **Latest tag**: `latest` (only on main branch)

The image name format is: `ghcr.io/allenai/olmoearth_projects:<tag>`

**Sources:** [.github/workflows/build-test.yml:37-46]()

### Disk Space Optimization

Before building, the pipeline runs a cleanup step to free disk space on the GitHub Actions runner:

```bash
sudo docker rmi $(docker image ls -aq) >/dev/null 2>&1 || true
sudo docker image prune --all --force >/dev/null 2>&1 || true
sudo rm -rf /usr/share/dotnet
sudo rm -rf /opt/ghc
sudo rm -rf /usr/local/share/boost
```

This removes:
- All existing Docker images
- .NET SDK files (`/usr/share/dotnet`)
- Haskell GHC compiler (`/opt/ghc`)
- Boost C++ libraries (`/usr/local/share/boost`)

**Sources:** [.github/workflows/build-test.yml:48-54]()

### Build Arguments

The Docker build process receives the `GITHUB_TOKEN` secret as a build argument:

```yaml
build-args: |
  GITHUB_TOKEN=${{ secrets.CLONE_GITHUB_TOKEN }}
```

This token is used within the Dockerfile to configure Git authentication for cloning private repositories during the build process.

**Sources:** [.github/workflows/build-test.yml:64-65](), [Dockerfile:5-6]()

## Test Job Configuration

The `test` job runs on `ubuntu-latest-m` runners (medium-sized machines) and depends on the successful completion of the `build` job.

```mermaid
graph LR
    subgraph "Test Environment Setup"
        PULL["Pull Docker Image<br/>${{ needs.build.outputs.ghcr_docker_image }}"]
        GCP_AUTH["GCP Authentication<br/>GOOGLE_CREDENTIALS secret"]
    end
    
    subgraph "Unit Tests"
        UNIT_RUN["docker run --rm<br/>-e CI=true<br/>pytest tests/unit -vv"]
    end
    
    subgraph "Integration Tests"
        INT_RUN["docker run --rm<br/>-e CI=true<br/>-v gcp-credentials.json<br/>-e GOOGLE_APPLICATION_CREDENTIALS<br/>pytest tests/integration -vv --forked"]
    end
    
    PULL --> UNIT_RUN
    PULL --> GCP_AUTH
    GCP_AUTH --> INT_RUN
    UNIT_RUN --> INT_RUN
```

**Diagram: Test Job Execution Flow** - Shows the sequence of test execution within Docker containers.

**Sources:** [.github/workflows/build-test.yml:76-122]()

### Unit Test Execution

Unit tests run in a minimal Docker environment with only the `CI` environment variable set:

```bash
docker run --rm \
  -e CI="true" \
  ${{ needs.build.outputs.ghcr_docker_image }} \
  pytest tests/unit -vv
```

The `-vv` flag enables verbose output for detailed test results. Unit tests do not require external credentials or network access.

**Sources:** [.github/workflows/build-test.yml:99-105]()

### Integration Test Execution

Integration tests require Google Cloud Platform credentials to access resources like Google Cloud Storage:

```bash
docker run --rm \
  -e CI="true" \
  -v ${{env.GOOGLE_GHA_CREDS_PATH}}:/tmp/gcp-credentials.json:ro \
  -e GOOGLE_APPLICATION_CREDENTIALS=/tmp/gcp-credentials.json \
  ${{ needs.build.outputs.ghcr_docker_image }} \
  pytest tests/integration -vv --forked
```

Key configurations:
- **Volume mount**: GCP credentials file mounted as read-only (`ro`)
- **Environment variable**: `GOOGLE_APPLICATION_CREDENTIALS` points to mounted credentials
- **`--forked` flag**: Runs each test in a separate process to prevent state contamination

**Sources:** [.github/workflows/build-test.yml:107-115]()

## Docker Image Build Process

The Dockerfile defines a multi-stage build process using `uv` for dependency management.

```mermaid
graph TB
    subgraph "Base Image"
        BASE["pytorch/pytorch:2.7.0-cuda12.8-cudnn9-runtime<br/>Digest: sha256:7db0e1bf..."]
    end
    
    subgraph "System Setup"
        GIT["Install git<br/>apt-get install git"]
        TOKEN["Configure git with GITHUB_TOKEN<br/>git config --global url"]
        UV["Copy uv binary<br/>from ghcr.io/astral-sh/uv:latest"]
    end
    
    subgraph "Dependency Installation"
        COPY1["Copy pyproject.toml & uv.lock"]
        SYNC1["uv sync --all-extras --no-install-project"]
    end
    
    subgraph "Project Installation"
        COPY2["Copy all project files"]
        SYNC2["uv sync --all-extras --locked"]
        ENV["Set PATH=/olmoearth_projects/.venv/bin:$PATH"]
    end
    
    BASE --> GIT
    GIT --> TOKEN
    TOKEN --> UV
    UV --> COPY1
    COPY1 --> SYNC1
    SYNC1 --> COPY2
    COPY2 --> SYNC2
    SYNC2 --> ENV
```

**Diagram: Docker Image Build Stages** - Shows the sequential steps in constructing the Docker image.

**Sources:** [Dockerfile:1-19]()

### Base Image Selection

The pipeline uses a specific PyTorch base image with CUDA support:

```dockerfile
FROM pytorch/pytorch:2.7.0-cuda12.8-cudnn9-runtime@sha256:7db0e1bf...
```

This provides:
- **PyTorch 2.7.0** for deep learning operations
- **CUDA 12.8** for GPU acceleration
- **cuDNN 9** for optimized neural network primitives
- **Runtime variant** (not development) for smaller image size

**Sources:** [Dockerfile:1]()

### Git Authentication Configuration

The Dockerfile configures Git to use the provided GitHub token for authentication:

```dockerfile
ARG GITHUB_TOKEN
RUN git config --global url."https://x-access-token:${GITHUB_TOKEN}@github.com/".insteadOf "https://github.com/"
```

This allows the build process to clone private repositories, including `olmoearth_pretrain` and other internal dependencies.

**Sources:** [Dockerfile:4-6]()

### Dependency Management with uv

The build process uses `uv` for fast, reproducible dependency installation:

1. **Copy uv binary** from official Astral image:
   ```dockerfile
   COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
   ```

2. **Initial sync** without installing the project itself:
   ```dockerfile
   COPY pyproject.toml /olmoearth_projects/pyproject.toml
   COPY uv.lock /rslearn/uv.lock
   RUN uv sync --all-extras --no-install-project
   ```

3. **Final sync** with the complete project:
   ```dockerfile
   COPY ./ /olmoearth_projects
   RUN uv sync --all-extras --locked
   ```

The `--locked` flag ensures that the exact versions specified in `uv.lock` are installed, preventing drift between development and production environments.

**Sources:** [Dockerfile:8-18]()

## Environment Variables and Secrets

The pipeline uses several environment variables and GitHub secrets:

| Variable/Secret | Scope | Purpose |
|----------------|-------|---------|
| `REGISTRY` | Workflow env | Set to `ghcr.io` |
| `IMAGE_NAME` | Workflow env | Set to `${{ github.repository }}` |
| `SERVICE_NAME` | Workflow env | Set to `"olmoearth_projects"` |
| `GITHUB_TOKEN` | Build job | Automatically provided by GitHub Actions |
| `CLONE_GITHUB_TOKEN` | Build step | Secret for cloning private repos |
| `GOOGLE_CREDENTIALS` | Test job | GCP service account credentials JSON |
| `CI` | Test containers | Set to `"true"` to indicate CI environment |
| `GOOGLE_APPLICATION_CREDENTIALS` | Integration tests | Path to GCP credentials file |

**Sources:** [.github/workflows/build-test.yml:9-12](), [.github/workflows/build-test.yml:35](), [.github/workflows/build-test.yml:65](), [.github/workflows/build-test.yml:97]()

## Pipeline Permissions

The build job requires specific permissions to interact with GitHub Container Registry:

```yaml
permissions:
  contents: read
  packages: write
```

- **`contents: read`**: Allows checking out repository code
- **`packages: write`**: Allows pushing Docker images to GHCR

**Sources:** [.github/workflows/build-test.yml:21-23]()

## Test Discovery and Execution

The pipeline runs two test suites using pytest:

### Unit Test Suite

Tests in `tests/unit/` directory verify individual components in isolation. Example test structure:

```python
# tests/unit/utils/label_quality/test_wrapper.py
def test_label_quality_wrapper() -> None:
    # Creates test GeoDataFrame
    # Runs check_label_quality
```

These tests run without external dependencies and execute quickly.

**Sources:** [tests/unit/utils/label_quality/test_wrapper.py:1-23]()

### Integration Test Suite

Tests in `tests/integration/` directory verify end-to-end workflows that require external services like Google Cloud Storage. The `--forked` flag ensures process isolation:

```bash
pytest tests/integration -vv --forked
```

**Sources:** [.github/workflows/build-test.yml:115]()

## Image Naming Convention

The pipeline generates lowercase image names with digests for reproducibility:

```bash
GHCR_IMAGE="${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}@${{ steps.build-push.outputs.digest }}"
GHCR_IMAGE=`echo ${GHCR_IMAGE} | tr '[:upper:]' '[:lower:]'`
```

Example output: `ghcr.io/allenai/olmoearth_projects@sha256:abc123...`

The digest-based naming ensures that downstream jobs use the exact image that was built, even if tags are updated concurrently.

**Sources:** [.github/workflows/build-test.yml:70-74]()

## Cleanup and Resource Management

The test job includes a cleanup step that always runs, even if tests fail:

```yaml
- name: Clean up
  if: always()
  run: |
    docker image prune -f
```

This prevents accumulation of Docker images on GitHub Actions runners.

**Sources:** [.github/workflows/build-test.yml:118-121]()

## Dependencies Defined in pyproject.toml

The project dependencies are managed in `pyproject.toml`:

```toml
dependencies = [
    "geopandas>=1.1.1",
    "openpyxl>=3.1.5",
    "python-dotenv>=1.0",
    "PyYAML>=6",
    "rslearn[extra]>=0.0.18",
    "wandb>=0.21",
    "olmoearth-runner>=0.1.10",
    "olmoearth_pretrain",
]
```

Development dependencies include testing and linting tools:

```toml
[project.optional-dependencies]
dev = [
    "interrogate>=1.7.0",
    "mypy>=1.17.1,<2",
    "pre-commit>=4.3.0",
    "pytest>=8.2",
    "pytest-dotenv",
    "pytest-forked",
    "pytest-xdist",
    "ruff>=0.7",
]
```

The `--all-extras` flag in the Dockerfile ensures that both production and development dependencies are installed.

**Sources:** [pyproject.toml:12-34](), [Dockerfile:14]()

---

# Page: Testing

# Testing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/build-test.yml](.github/workflows/build-test.yml)
- [docs/internal.md](docs/internal.md)
- [olmoearth_projects/utils/label_quality/__init__.py](olmoearth_projects/utils/label_quality/__init__.py)
- [olmoearth_projects/utils/label_quality/spatial_clustering.py](olmoearth_projects/utils/label_quality/spatial_clustering.py)
- [olmoearth_run_data/sample/model.yaml](olmoearth_run_data/sample/model.yaml)
- [olmoearth_run_data/satlas_solar_farm/model.yaml](olmoearth_run_data/satlas_solar_farm/model.yaml)
- [tests/integration/olmoearth_run/test_olmoearth_run.py](tests/integration/olmoearth_run/test_olmoearth_run.py)
- [tests/unit/utils/__init__.py](tests/unit/utils/__init__.py)
- [tests/unit/utils/label_quality/__init__.py](tests/unit/utils/label_quality/__init__.py)
- [tests/unit/utils/label_quality/test_spatial_clustering.py](tests/unit/utils/label_quality/test_spatial_clustering.py)
- [tests/unit/utils/label_quality/test_wrapper.py](tests/unit/utils/label_quality/test_wrapper.py)

</details>



This document describes the testing infrastructure in the olmoearth_projects repository, including unit tests for label quality utilities, integration tests for the inference pipeline, and the CI/CD workflow that executes tests automatically. For information about the CI/CD pipeline configuration and Docker environment, see [CI/CD Pipeline](#9.2) and [Docker Environment](#9.4). For details about the label quality assessment tools being tested, see [Label Quality Assessment](#4.2).

## Test Organization

The testing infrastructure is organized into two primary categories: unit tests and integration tests, executed through a GitHub Actions CI/CD pipeline.

```mermaid
graph TB
    subgraph "Test Suite Organization"
        TESTS["tests/"]
        
        UNIT["tests/unit/"]
        UNIT_UTILS["tests/unit/utils/"]
        UNIT_LABEL["tests/unit/utils/label_quality/"]
        
        INTEGRATION["tests/integration/"]
        INTEGRATION_RUN["tests/integration/olmoearth_run/"]
    end
    
    subgraph "Test Files"
        TEST_SPATIAL["test_spatial_clustering.py<br/>Spatial KNN tests"]
        TEST_WRAPPER["test_wrapper.py<br/>check_label_quality tests"]
        TEST_RUN["test_olmoearth_run.py<br/>Full pipeline test"]
    end
    
    subgraph "Code Under Test"
        SPATIAL_CLUSTER["spatial_clustering.py<br/>spatial_clustering()"]
        LABEL_QUALITY["__init__.py<br/>check_label_quality()"]
        OLMOEARTH_RUN["olmoearth_run.py<br/>olmoearth_run()"]
    end
    
    TESTS --> UNIT
    TESTS --> INTEGRATION
    
    UNIT --> UNIT_UTILS
    UNIT_UTILS --> UNIT_LABEL
    UNIT_LABEL --> TEST_SPATIAL
    UNIT_LABEL --> TEST_WRAPPER
    
    INTEGRATION --> INTEGRATION_RUN
    INTEGRATION_RUN --> TEST_RUN
    
    TEST_SPATIAL --> SPATIAL_CLUSTER
    TEST_WRAPPER --> LABEL_QUALITY
    TEST_RUN --> OLMOEARTH_RUN
```

**Sources**: [tests/unit/utils/label_quality/test_spatial_clustering.py:1-51](), [tests/unit/utils/label_quality/test_wrapper.py:1-23](), [tests/integration/olmoearth_run/test_olmoearth_run.py:1-119]()

## Unit Tests for Label Quality Utilities

Unit tests validate the label quality assessment functions that evaluate spatial clustering, label imbalance, and spatial extent. These utilities are critical for assessing the quality of training data before model fine-tuning.

### Spatial Clustering Tests

The `test_spatial_clustering.py` module contains tests for the `spatial_clustering()` function, which performs spatial K-nearest neighbors analysis to detect whether labels are spatially clustered.

#### Classification Tests

The function `test_spatial_clustering_classification()` validates the spatial clustering metric for classification tasks:

| Test Scenario | Input Labels | Expected F1 Score | Description |
|--------------|--------------|-------------------|-------------|
| Highly clustered | `["South", "South", "South", "North", "North"]` | `1.0` per class | Labels match geographic clustering |
| No clustering | `["Random", "Labels", "Totally", "Mixed", "Up"]` | `0.0` per class | Labels completely spatially mixed |

The test uses a synthetic dataset of South American cities where labels initially match their geographic regions (high clustering), then are randomized (no clustering). The function [tests/unit/utils/label_quality/test_spatial_clustering.py:7-29]() validates that F1 scores correctly reflect spatial clustering patterns.

#### Regression Tests

The function `test_spatial_clustering_regression()` validates the spatial clustering metric for regression tasks using mean squared error (MSE):

| Test Scenario | Input Values | Expected MSE | Description |
|--------------|--------------|--------------|-------------|
| Highly clustered | `[0.5, 0.5, 0.5, 1.5, 1.5]` | `0.0` | Values match geographic clustering |
| No clustering | `[1.5, 0.5, 2.5, 0.5, 1.5]` | `1.0` | Values spatially mixed |

The test [tests/unit/utils/label_quality/test_spatial_clustering.py:32-51]() creates a GeoDataFrame with point geometries and validates that MSE increases when labels are less spatially clustered.

**Implementation Details**: The `spatial_clustering()` function [olmoearth_projects/utils/label_quality/spatial_clustering.py:30-89]() implements spatial KNN using the Haversine distance formula [olmoearth_projects/utils/label_quality/spatial_clustering.py:10-27]() to compute great circle distances between points on Earth.

**Sources**: [tests/unit/utils/label_quality/test_spatial_clustering.py:1-51](), [olmoearth_projects/utils/label_quality/spatial_clustering.py:1-90]()

### Wrapper Function Tests

The `test_wrapper.py` module tests the `check_label_quality()` function, which provides a unified interface for running all label quality checks and displaying results in a formatted table.

The test function `test_label_quality_wrapper()` [tests/unit/utils/label_quality/test_wrapper.py:7-23]() validates:
- The function executes without errors when given valid input
- The `checks_to_run` parameter correctly filters which checks are executed
- The GeoDataFrame input validation works correctly

The `check_label_quality()` function [olmoearth_projects/utils/label_quality/__init__.py:14-61]() validates that input DataFrames contain required columns (`geometry` and `label`) and uses the Rich library to display results in a formatted console table [olmoearth_projects/utils/label_quality/__init__.py:46-60]().

**Sources**: [tests/unit/utils/label_quality/test_wrapper.py:1-23](), [olmoearth_projects/utils/label_quality/__init__.py:1-61]()

## Integration Tests for olmoearth_run Pipeline

Integration tests validate the complete inference pipeline, from request geometry definition through final output generation. These tests ensure that all components work together correctly in a production-like environment.

### Pipeline Test Architecture

```mermaid
graph LR
    subgraph "Test Setup"
        TEST_FN["test_olmoearth_run()"]
        TMP_PATH["tmp_path fixture<br/>Temporary directory"]
        CONFIG_COPY["Config file copying<br/>dataset.json<br/>model.yaml<br/>olmoearth_run.yaml"]
        GEOMETRY["Request geometry<br/>Solar farm location<br/>(-111.613, 33.267)"]
    end
    
    subgraph "Test Execution"
        RUN_FN["olmoearth_run()<br/>Main pipeline function"]
        PARTITION["Partitioning<br/>NoopPartitioner<br/>ReprojectionPartitioner"]
        INFERENCE["Model inference<br/>Solar farm checkpoint<br/>Batch size: 1"]
        OUTPUT["Result generation<br/>GeoTIFF output"]
    end
    
    subgraph "Validation"
        FILE_CHECK["File existence check<br/>results_raster/*.tif"]
        PIXEL_CHECK["Pixel value validation<br/>10-50% solar coverage"]
    end
    
    TEST_FN --> TMP_PATH
    TEST_FN --> CONFIG_COPY
    TEST_FN --> GEOMETRY
    
    CONFIG_COPY --> RUN_FN
    GEOMETRY --> RUN_FN
    
    RUN_FN --> PARTITION
    PARTITION --> INFERENCE
    INFERENCE --> OUTPUT
    
    OUTPUT --> FILE_CHECK
    FILE_CHECK --> PIXEL_CHECK
```

**Sources**: [tests/integration/olmoearth_run/test_olmoearth_run.py:1-119]()

### Solar Farm Integration Test

The function `test_olmoearth_run_solar_farm()` [tests/integration/olmoearth_run/test_olmoearth_run.py:21-119]() validates the complete olmoearth_run pipeline using the solar farm segmentation model. The test performs the following operations:

#### Configuration Preparation

The test customizes configuration files for the test environment:

1. **Dataset Configuration**: Copies `dataset.json` without modification [tests/integration/olmoearth_run/test_olmoearth_run.py:36-40]()

2. **Request Geometry**: Creates a custom prediction request centered on a known solar farm location at coordinates `(-111.613, 33.267)` with a bounding box extending 0.01 degrees in each direction [tests/integration/olmoearth_run/test_olmoearth_run.py:43-64]()

3. **Partitioning Configuration**: Modifies `olmoearth_run.yaml` to use `NoopPartitioner` for the request geometry (treating the entire area as one partition) and `ReprojectionPartitioner` for window geometries with EPSG:3857 projection and 10m resolution [tests/integration/olmoearth_run/test_olmoearth_run.py:69-87]()

4. **Model Configuration**: Adjusts `model.yaml` to use batch size 1 to accommodate CI environment memory constraints [tests/integration/olmoearth_run/test_olmoearth_run.py:90-98]()

#### Pipeline Execution

The test executes the pipeline [tests/integration/olmoearth_run/test_olmoearth_run.py:104-108]() with:
- Config path pointing to the temporary directory with customized configurations
- Scratch path for intermediate and final outputs
- Checkpoint path to the trained solar farm model on Google Cloud Storage

#### Validation

The test validates output correctness [tests/integration/olmoearth_run/test_olmoearth_run.py:110-118]():
1. Verifies the results directory exists at `scratch/results/results_raster`
2. Confirms exactly one GeoTIFF file is generated
3. Reads the raster output using `rasterio`
4. Validates that solar farm pixels (value `1`) constitute between 10% and 50% of the total area

This range validation ensures the model is detecting the solar farm (>10% coverage) but not over-classifying (≤50% coverage) for this specific test location.

**Sources**: [tests/integration/olmoearth_run/test_olmoearth_run.py:21-119]()

## CI/CD Testing Pipeline

The GitHub Actions workflow automates testing on every push to `main` and on all pull requests. The pipeline consists of two jobs: `build` and `test`.

### Build Job

```mermaid
graph TB
    subgraph "Build Job Steps"
        CHECKOUT["Checkout repository<br/>actions/checkout@v4"]
        LOGIN["Docker login<br/>ghcr.io registry<br/>GITHUB_TOKEN"]
        META["Extract metadata<br/>SHA tags + latest tag"]
        CLEANUP["Disk space cleanup<br/>Remove unused images<br/>and frameworks"]
        BUILD["Build and push image<br/>docker/build-push-action@v6<br/>GITHUB_TOKEN for rslearn clone"]
        STORE["Store image name<br/>Output digest to variable"]
    end
    
    CHECKOUT --> LOGIN
    LOGIN --> META
    META --> CLEANUP
    CLEANUP --> BUILD
    BUILD --> STORE
```

The build job [.github/workflows/build-test.yml:19-74]() performs these operations:

1. **Container Registry Login**: Authenticates to GitHub Container Registry using `GITHUB_TOKEN` [.github/workflows/build-test.yml:30-35]()

2. **Metadata Extraction**: Generates Docker image tags including SHA-based tags (long and short) and `latest` for the default branch [.github/workflows/build-test.yml:37-46]()

3. **Disk Space Cleanup**: Removes unused Docker images and system frameworks to prevent disk space issues during build [.github/workflows/build-test.yml:48-54]()

4. **Image Build and Push**: Builds the Docker image and pushes to `ghcr.io/allenai/olmoearth_projects` with `CLONE_GITHUB_TOKEN` passed as a build arg for accessing private rslearn repository [.github/workflows/build-test.yml:56-65]()

5. **Image Name Storage**: Saves the full image digest to job outputs for use in the test job [.github/workflows/build-test.yml:67-74]()

**Sources**: [.github/workflows/build-test.yml:19-74]()

### Test Job

The test job runs on `ubuntu-latest-m` (medium-sized runner) and executes both unit and integration tests inside the Docker container:

```mermaid
graph TB
    subgraph "Test Job Execution"
        WAIT["Wait for build job<br/>needs: build"]
        CHECKOUT["Checkout repository"]
        LOGIN["Docker login"]
        PULL["Pull built image<br/>Using digest from build job"]
        GCP_AUTH["GCP authentication<br/>GOOGLE_CREDENTIALS secret<br/>For data access"]
        UNIT["Run unit tests<br/>pytest tests/unit -vv"]
        INTEGRATION["Run integration tests<br/>pytest tests/integration -vv<br/>--forked flag"]
        CLEANUP["Cleanup<br/>Prune Docker images"]
    end
    
    WAIT --> CHECKOUT
    CHECKOUT --> LOGIN
    LOGIN --> PULL
    PULL --> GCP_AUTH
    GCP_AUTH --> UNIT
    UNIT --> INTEGRATION
    INTEGRATION --> CLEANUP
```

#### Test Execution Commands

**Unit Tests** [.github/workflows/build-test.yml:99-105]():
```bash
docker run --rm \
  -e CI="true" \
  ${{ needs.build.outputs.ghcr_docker_image }} \
  pytest tests/unit -vv
```

**Integration Tests** [.github/workflows/build-test.yml:107-115]():
```bash
docker run --rm \
  -e CI="true" \
  -v ${{env.GOOGLE_GHA_CREDS_PATH}}:/tmp/gcp-credentials.json:ro \
  -e GOOGLE_APPLICATION_CREDENTIALS=/tmp/gcp-credentials.json \
  ${{ needs.build.outputs.ghcr_docker_image }} \
  pytest tests/integration -vv --forked
```

Key differences for integration tests:
- **Volume Mount**: Mounts GCP credentials JSON file into the container [.github/workflows/build-test.yml:112]()
- **Environment Variable**: Sets `GOOGLE_APPLICATION_CREDENTIALS` to enable access to Google Cloud Storage for model checkpoints and test data [.github/workflows/build-test.yml:113]()
- **Forked Execution**: Uses `--forked` flag to run tests in separate processes, providing isolation for resource-intensive tests [.github/workflows/build-test.yml:115]()

**Sources**: [.github/workflows/build-test.yml:76-122]()

## Running Tests Locally

### Unit Tests

To run unit tests locally with the same environment as CI:

```bash
# Build the Docker image
docker build -t olmoearth_projects .

# Run unit tests
docker run --rm olmoearth_projects pytest tests/unit -vv
```

For development without Docker, install dependencies and run directly:

```bash
# Install dependencies using uv
uv sync

# Run unit tests
uv run pytest tests/unit -vv

# Run specific test module
uv run pytest tests/unit/utils/label_quality/test_spatial_clustering.py -vv
```

### Integration Tests

Integration tests require GCP credentials to access model checkpoints and satellite data:

```bash
# Set GCP credentials path
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json

# Run integration tests with Docker
docker run --rm \
  -v $GOOGLE_APPLICATION_CREDENTIALS:/tmp/gcp-credentials.json:ro \
  -e GOOGLE_APPLICATION_CREDENTIALS=/tmp/gcp-credentials.json \
  olmoearth_projects pytest tests/integration -vv --forked

# Or run directly with uv
uv run pytest tests/integration -vv --forked
```

**Sources**: Derived from [.github/workflows/build-test.yml:99-115]()

## Test Configuration and Dependencies

### pytest Configuration

The repository uses `pytest` as the test framework with the following key features:

| Feature | Purpose | Implementation |
|---------|---------|----------------|
| Fixtures | Temporary directories for test isolation | `tmp_path` fixture in integration tests |
| Parametrization | Test multiple scenarios with one function | Not currently used but available |
| Verbose output | Detailed test execution logs | `-vv` flag in CI and local runs |
| Forked execution | Process isolation for integration tests | `--forked` flag with `pytest-forked` plugin |
| Monkeypatching | Environment variable mocking | Used to disable W&B in tests |

### Test Dependencies

Tests require several external dependencies:

- **Core Testing**: `pytest`, `pytest-forked` for test execution
- **Geospatial**: `geopandas`, `rasterio`, `shapely` for geospatial data validation
- **ML/Data**: `numpy`, `pandas`, `torch` for numerical validation
- **Infrastructure**: `upath` for universal path handling, `pyyaml` for config manipulation

The test environment also requires access to:
- **Google Cloud Storage**: For model checkpoints (e.g., `gs://ai2-rslearn-projects-data/projects/`)
- **Planetary Computer**: For satellite imagery access during integration tests

**Sources**: [tests/integration/olmoearth_run/test_olmoearth_run.py:1-19](), [tests/unit/utils/label_quality/test_spatial_clustering.py:1-5](), [.github/workflows/build-test.yml:94-115]()

## Test Coverage and Gaps

### Current Coverage

The test suite currently covers:

1. **Label Quality Utilities** (High Coverage):
   - Spatial clustering for classification and regression
   - Wrapper function execution and parameter filtering
   - GeoDataFrame input validation

2. **olmoearth_run Pipeline** (Moderate Coverage):
   - Complete pipeline execution for solar farm model
   - Configuration file customization
   - Output validation for classification tasks

### Known Gaps

Areas that could benefit from additional test coverage:

| Component | Current Status | Recommendation |
|-----------|---------------|----------------|
| Label imbalance checks | No dedicated tests | Add tests to validate imbalance metrics |
| Spatial extent checks | No dedicated tests | Add tests for extent calculation |
| Multiple partitioning strategies | Only Noop/Reprojection tested | Test GridPartitioner variants |
| Post-processing operations | Indirectly tested | Add explicit tests for CombineGeotiff |
| Error handling | Limited coverage | Add tests for invalid inputs and edge cases |
| Regression models | Not integration tested | Add test for LFMC or similar model |

**Sources**: Inferred from [tests/unit/utils/label_quality/]() and [tests/integration/olmoearth_run/test_olmoearth_run.py:1-119]()

---

# Page: Docker Environment

# Docker Environment

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Dockerfile](Dockerfile)
- [pyproject.toml](pyproject.toml)
- [uv.lock](uv.lock)

</details>



This document describes the Docker containerization infrastructure used in the olmoearth_projects repository. It covers the Dockerfile configuration, base image selection, dependency installation process, and how the Docker environment integrates with development and deployment workflows.

For information about the CI/CD pipeline that builds Docker images, see [CI/CD Pipeline](#9.2). For general development setup including local environment configuration, see [Getting Started](#2).

## Purpose and Overview

The Docker environment provides a reproducible, GPU-enabled runtime environment for training and inference with OlmoEarth models. The containerization strategy ensures consistent dependency versions across development, training clusters (Beaker/Saturn), and deployment environments. The container includes PyTorch with CUDA support, all Python dependencies managed through `uv`, and the complete olmoearth_projects codebase.

**Sources:** [Dockerfile:1-19]()

## Base Image Configuration

The Docker image is built on the official PyTorch base image with full GPU support:

```dockerfile
FROM pytorch/pytorch:2.7.0-cuda12.8-cudnn9-runtime@sha256:7db0e1bf4b1ac274ea09cf6358ab516f8a5c7d3d0e02311bed445f7e236a5d80
```

### Base Image Components

| Component | Version | Purpose |
|-----------|---------|---------|
| PyTorch | 2.7.0 | Deep learning framework for model training and inference |
| CUDA | 12.8 | NVIDIA GPU computing platform |
| cuDNN | 9 | NVIDIA deep learning primitives library |
| Runtime Variant | runtime | Optimized for inference and training (excludes development tools) |

The base image uses a content-addressable SHA256 digest to ensure exact reproducibility across builds, preventing unexpected changes from upstream image updates.

**Sources:** [Dockerfile:1]()

## Docker Build Process

The following diagram illustrates the complete Docker image build process:

```mermaid
graph TB
    BASE["pytorch/pytorch:2.7.0-cuda12.8-cudnn9-runtime<br/>Base Image"]
    UV_IMAGE["ghcr.io/astral-sh/uv:latest<br/>UV Binary Source"]
    
    STAGE1["System Dependencies<br/>apt-get install git"]
    STAGE2["Git Configuration<br/>Setup GITHUB_TOKEN"]
    STAGE3["Copy UV Binary<br/>/usr/local/bin/uv"]
    STAGE4["Workspace Setup<br/>WORKDIR /olmoearth_projects"]
    STAGE5["Copy Manifests<br/>pyproject.toml, uv.lock"]
    STAGE6["Install Dependencies<br/>uv sync --all-extras"]
    STAGE7["Set PATH<br/>.venv/bin"]
    STAGE8["Copy Codebase<br/>Full Repository"]
    STAGE9["Final Sync<br/>uv sync --all-extras --locked"]
    
    FINAL["Final Image<br/>Ready for Training/Inference"]
    
    BASE --> STAGE1
    STAGE1 --> STAGE2
    UV_IMAGE --> STAGE3
    STAGE2 --> STAGE4
    STAGE3 --> STAGE4
    STAGE4 --> STAGE5
    STAGE5 --> STAGE6
    STAGE6 --> STAGE7
    STAGE7 --> STAGE8
    STAGE8 --> STAGE9
    STAGE9 --> FINAL
```

**Build Process Stages:**

1. **System Dependencies:** Installs git for accessing private repositories
2. **Git Configuration:** Configures git to use GITHUB_TOKEN for authentication
3. **UV Installation:** Copies the `uv` binary from Astral's official image
4. **Workspace Initialization:** Sets `/olmoearth_projects` as the working directory
5. **Dependency Installation:** Installs Python dependencies without the project itself
6. **Environment Configuration:** Adds virtual environment to PATH
7. **Codebase Copy:** Copies the complete repository into the container
8. **Final Installation:** Installs the project itself with locked dependencies

**Sources:** [Dockerfile:1-19]()

## Dependency Management with UV

The Docker image uses `uv` as the package installer, which provides significantly faster dependency resolution and installation compared to traditional pip.

### UV Installation Strategy

```mermaid
graph LR
    UV_UPSTREAM["ghcr.io/astral-sh/uv:latest"]
    UV_BINARY["/usr/local/bin/uv"]
    UV_LOCK["uv.lock<br/>Locked Dependencies"]
    PYPROJECT["pyproject.toml<br/>Project Manifest"]
    VENV[".venv<br/>Virtual Environment"]
    
    UV_UPSTREAM -->|"COPY --from"| UV_BINARY
    PYPROJECT --> UV_BINARY
    UV_LOCK --> UV_BINARY
    UV_BINARY -->|"uv sync"| VENV
```

### Dependency Installation Commands

The Dockerfile executes two separate `uv sync` commands:

**First Sync (Dependencies Only):**
```dockerfile
RUN uv sync --all-extras --no-install-project
```
- `--all-extras`: Installs all optional dependency groups including `dev`
- `--no-install-project`: Skips installing the olmoearth_projects package itself
- Purpose: Caches dependency installation layer separately from code changes

**Second Sync (Project Installation):**
```dockerfile
RUN uv sync --all-extras --locked
```
- `--all-extras`: Installs all optional dependencies
- `--locked`: Uses exact versions from `uv.lock` without updating
- Purpose: Installs the olmoearth_projects package with guaranteed reproducibility

This two-stage approach optimizes Docker layer caching—dependency installations are cached and only rebuilt when `pyproject.toml` or `uv.lock` change, while code changes only trigger the final sync.

**Sources:** [Dockerfile:12-18](), [pyproject.toml:12-21]()

## Build Arguments and Environment Variables

### Build Arguments

The Dockerfile accepts one build argument:

| Argument | Required | Purpose | Usage |
|----------|----------|---------|-------|
| `GITHUB_TOKEN` | Yes | Authenticates git operations for private repositories | Passed during `docker build --build-arg GITHUB_TOKEN=<token>` |

The token is used to configure git to access private dependencies:

```dockerfile
ARG GITHUB_TOKEN
RUN git config --global url."https://x-access-token:${GITHUB_TOKEN}@github.com/".insteadOf "https://github.com/"
```

This configuration allows `uv` to install dependencies from private GitHub repositories specified in `pyproject.toml`, such as `olmoearth_pretrain`.

### Runtime Environment Variables

The Dockerfile sets one runtime environment variable:

```dockerfile
ENV PATH="/olmoearth_projects/.venv/bin:$PATH"
```

This prepends the virtual environment's `bin` directory to PATH, ensuring that:
- Python executables resolve to the virtual environment's Python
- Installed console scripts are available without full paths
- Commands like `python`, `pip`, and `uv` use the virtual environment versions

**Sources:** [Dockerfile:3-6](), [Dockerfile:16]()

## Directory Structure

The container's filesystem is organized as follows:

```mermaid
graph TB
    ROOT["/"]
    WORKSPACE["/olmoearth_projects<br/>WORKDIR"]
    VENV[".venv<br/>Virtual Environment"]
    BIN["bin/<br/>Python executables"]
    LIB["lib/python3.x/site-packages<br/>Installed packages"]
    PYPROJECT["pyproject.toml"]
    UVLOCK["uv.lock"]
    CODE["Source Code"]
    
    ROOT --> WORKSPACE
    WORKSPACE --> VENV
    WORKSPACE --> PYPROJECT
    WORKSPACE --> UVLOCK
    WORKSPACE --> CODE
    VENV --> BIN
    VENV --> LIB
```

### Key Directories and Files

| Path | Description |
|------|-------------|
| `/olmoearth_projects` | Working directory and project root |
| `/olmoearth_projects/.venv` | Virtual environment created by `uv` |
| `/olmoearth_projects/.venv/bin` | Python executables and console scripts |
| `/olmoearth_projects/pyproject.toml` | Project manifest with dependency specifications |
| `/olmoearth_projects/uv.lock` | Lock file with exact dependency versions |
| `/usr/local/bin/uv` | UV package manager binary |

**Sources:** [Dockerfile:8-18]()

## Integration with Development Workflow

The following diagram shows how the Docker environment integrates with the complete development and deployment workflow:

```mermaid
graph TB
    DEV["Developer Workstation"]
    DOCKERFILE["Dockerfile"]
    PYPROJECT["pyproject.toml"]
    UVLOCK["uv.lock"]
    
    CI["GitHub Actions<br/>CI/CD Pipeline"]
    DOCKER_BUILD["docker build<br/>--build-arg GITHUB_TOKEN"]
    IMAGE["Docker Image<br/>olmoearth_projects:latest"]
    
    BEAKER["Beaker Cluster<br/>GPU Training"]
    SATURN["Saturn Cluster<br/>GPU Training"]
    LOCAL["Local Development<br/>Docker Compose"]
    
    DEV --> DOCKERFILE
    DEV --> PYPROJECT
    DEV --> UVLOCK
    
    DOCKERFILE --> CI
    PYPROJECT --> CI
    UVLOCK --> CI
    
    CI --> DOCKER_BUILD
    DOCKER_BUILD --> IMAGE
    
    IMAGE --> BEAKER
    IMAGE --> SATURN
    IMAGE --> LOCAL
```

### Build Contexts

The Docker image is built in multiple contexts:

**1. CI/CD Pipeline:**
- Triggered by pushes to main branch or pull requests
- Uses GitHub Actions secrets for `GITHUB_TOKEN`
- Builds and optionally pushes to container registry
- See [CI/CD Pipeline](#9.2) for details

**2. Local Development:**
- Developers build images locally for testing
- Uses personal access token or GitHub CLI token
- Enables rapid iteration on Dockerfile changes

**3. Training Clusters:**
- Pre-built images are deployed to Beaker and Saturn
- Ensures consistency between local testing and cluster execution
- GPU-enabled containers run training jobs with identical environments

### Docker Image Layers

The multi-stage build process creates the following layer structure:

| Layer | Cached Until | Size Impact | Purpose |
|-------|--------------|-------------|---------|
| Base PyTorch Image | Base image SHA changes | ~4-6 GB | Provides PyTorch, CUDA, cuDNN |
| System Dependencies (git) | apt package versions change | ~50 MB | Enables git operations |
| UV Binary | UV version changes | ~10 MB | Provides fast package management |
| Project Manifests | pyproject.toml or uv.lock change | <1 MB | Defines dependencies |
| Python Dependencies | Dependencies change | ~1-3 GB | rslearn, torch extensions, ML libraries |
| Application Code | Code changes | ~50-100 MB | olmoearth_projects source code |

The layer structure optimizes for Docker's build cache—the most frequently changing components (application code) are placed at the end, while stable dependencies are cached earlier in the build process.

**Sources:** [Dockerfile:1-19](), [pyproject.toml:1-67]()

## Key Dependencies from Project Manifest

The container includes all dependencies specified in `pyproject.toml`:

### Core Dependencies

```python
dependencies = [
    "geopandas>=1.1.1",           # Geospatial data processing
    "openpyxl>=3.1.5",            # Excel file handling
    "python-dotenv>=1.0",         # Environment variable management
    "PyYAML>=6",                  # YAML configuration parsing
    "rslearn[extra]>=0.0.18",     # Remote sensing ML framework
    "wandb>=0.21",                # Experiment tracking
    "olmoearth-runner>=0.1.10",   # Inference pipeline
    "olmoearth_pretrain",         # OlmoEarth pre-trained models (private)
]
```

### Development Dependencies

```python
dev = [
    "interrogate>=1.7.0",         # Documentation coverage
    "mypy>=1.17.1,<2",           # Static type checking
    "pre-commit>=4.3.0",         # Git hooks for code quality
    "pytest>=8.2",               # Testing framework
    "pytest-dotenv",             # Test environment configuration
    "pytest-forked",             # Forked test execution
    "pytest-xdist",              # Parallel test execution
    "ruff>=0.7",                 # Fast Python linter
]
```

The `rslearn[extra]` dependency pulls in additional packages including PyTorch Lightning, torchmetrics, albumentations, and geospatial libraries. All transitive dependencies are locked in `uv.lock` to ensure reproducibility.

**Sources:** [pyproject.toml:12-34]()

## Usage Examples

### Building the Docker Image

```bash
# Build with GitHub token from environment
docker build \
  --build-arg GITHUB_TOKEN=${GITHUB_TOKEN} \
  -t olmoearth_projects:latest \
  .

# Build with GitHub CLI token
docker build \
  --build-arg GITHUB_TOKEN=$(gh auth token) \
  -t olmoearth_projects:latest \
  .
```

### Running the Container

```bash
# Interactive shell for development
docker run -it --gpus all \
  -v /path/to/data:/data \
  -v /path/to/checkpoints:/checkpoints \
  olmoearth_projects:latest \
  bash

# Execute training script
docker run --gpus all \
  -v /weka/dfive-default:/weka/dfive-default \
  olmoearth_projects:latest \
  python -m rslearn.train \
  --config model.yaml \
  --dataset dataset.json

# Run inference pipeline
docker run --gpus all \
  -v $(pwd)/outputs:/outputs \
  olmoearth_projects:latest \
  olmoearth_run \
  --model-path /checkpoints/model.pt \
  --geometry prediction_request_geometry.geojson \
  --config olmoearth_run.yaml
```

### Common Environment Variables

Additional environment variables often set at runtime:

| Variable | Purpose | Example |
|----------|---------|---------|
| `CUDA_VISIBLE_DEVICES` | Specify GPUs to use | `0,1,2,3` |
| `WANDB_API_KEY` | Authenticate with Weights & Biases | Secret token |
| `PYTHONPATH` | Extend Python module search path | `/olmoearth_projects` |
| `OMP_NUM_THREADS` | OpenMP thread count | `8` |

**Sources:** [Dockerfile:1-19]()

## Troubleshooting

### Common Build Issues

**Issue: "Could not read from remote repository"**
- **Cause:** Invalid or missing `GITHUB_TOKEN`
- **Solution:** Verify token has `repo` scope and is passed correctly

**Issue: "uv: command not found" during build**
- **Cause:** UV binary copy failed
- **Solution:** Check internet connectivity to ghcr.io

**Issue: Layer cache not invalidated after dependency change**
- **Cause:** Docker cache incorrectly reused
- **Solution:** Build with `--no-cache` flag or modify `uv.lock` file

### Runtime Issues

**Issue: "ModuleNotFoundError" for installed packages**
- **Cause:** PATH environment variable not set correctly
- **Solution:** Ensure `.venv/bin` is in PATH or activate virtual environment

**Issue: CUDA out of memory errors**
- **Cause:** GPU memory exhausted
- **Solution:** Reduce batch size, use gradient accumulation, or enable mixed precision training

**Issue: Permission denied accessing mounted volumes**
- **Cause:** User ID mismatch between host and container
- **Solution:** Run container with `--user $(id -u):$(id -g)` or set appropriate volume permissions

**Sources:** [Dockerfile:1-19]()

---

# Page: Reference

# Reference

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [olmoearth_run_data/awf/olmoearth_run.yaml](olmoearth_run_data/awf/olmoearth_run.yaml)
- [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml](olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml)
- [olmoearth_run_data/mozambique_lulc/rslp_finetuning_croptype.yaml](olmoearth_run_data/mozambique_lulc/rslp_finetuning_croptype.yaml)
- [olmoearth_run_data/mozambique_lulc/rslp_finetuning_croptype_in_season_novmar.yaml](olmoearth_run_data/mozambique_lulc/rslp_finetuning_croptype_in_season_novmar.yaml)
- [olmoearth_run_data/mozambique_lulc/rslp_finetuning_in_season_novmar.yaml](olmoearth_run_data/mozambique_lulc/rslp_finetuning_in_season_novmar.yaml)
- [olmoearth_run_data/nandi/olmoearth_run.yaml](olmoearth_run_data/nandi/olmoearth_run.yaml)

</details>



## Purpose and Scope

This section provides technical reference documentation for the olmoearth_projects repository. It documents the configuration file schemas, rslearn framework components, and utility scripts used throughout the codebase. This reference is intended for developers and advanced users who need to understand the technical details of system configuration and implementation.

For step-by-step guides on using these configurations, see [Getting Started](#2). For conceptual overviews of the training and inference workflows, see [System Architecture](#3) and [Model Training](#5). For information about specific models and their parameters, see [Available Models](#6).

## Configuration File Overview

The olmoearth_projects system uses three primary YAML configuration file types that work together to define model training and inference pipelines:

| Configuration File | Purpose | Primary Use Case | Key Sections |
|-------------------|---------|------------------|--------------|
| `rslp_finetuning.yaml` | Defines model architecture, training hyperparameters, and data loading configuration | Model training with PyTorch Lightning | `model`, `data`, `trainer` |
| `model.yaml` | Simplified model definition extracted from training config | Inference with trained checkpoints | `encoder`, `decoders`, `tasks` |
| `olmoearth_run.yaml` | Configures inference pipeline including partitioning and post-processing | Large-area inference deployment | `partition_strategies`, `postprocessing_strategies`, `inference_results_config` |

All configuration files use a consistent `class_path` and `init_args` pattern for instantiating Python classes, enabling declarative configuration of complex object hierarchies.

### Configuration File Relationship Diagram

```mermaid
graph TB
    subgraph "Training Phase"
        TRAIN_CONFIG["rslp_finetuning.yaml"]
        MODEL_DEF["model:<br/>RslearnLightningModule"]
        DATA_DEF["data:<br/>RslearnDataModule"]
        TRAINER_DEF["trainer:<br/>Callbacks"]
    end
    
    subgraph "Extraction Phase"
        MODEL_YAML["model.yaml<br/>(extracted)"]
        ENCODER_DEF["encoder:<br/>OlmoEarth"]
        DECODER_DEF["decoders:<br/>Upsample + Conv"]
    end
    
    subgraph "Inference Phase"
        RUN_CONFIG["olmoearth_run.yaml"]
        PARTITION_DEF["partition_strategies:<br/>GridPartitioner"]
        POSTPROC_DEF["postprocessing_strategies:<br/>CombineGeotiff"]
        RESULTS_DEF["inference_results_config:<br/>classification_fields"]
    end
    
    TRAIN_CONFIG --> MODEL_DEF
    TRAIN_CONFIG --> DATA_DEF
    TRAIN_CONFIG --> TRAINER_DEF
    
    MODEL_DEF --> MODEL_YAML
    MODEL_DEF --> ENCODER_DEF
    MODEL_DEF --> DECODER_DEF
    
    MODEL_YAML --> RUN_CONFIG
    RUN_CONFIG --> PARTITION_DEF
    RUN_CONFIG --> POSTPROC_DEF
    RUN_CONFIG --> RESULTS_DEF
```

**Sources:** [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:1-268](), [olmoearth_run_data/nandi/olmoearth_run.yaml:1-92]()

## Class Path Pattern

All configuration files use a consistent pattern for specifying Python classes and their initialization arguments:

```yaml
component_name:
  class_path: full.module.path.ClassName
  init_args:
    parameter1: value1
    parameter2: value2
```

This pattern enables:
- **Declarative instantiation**: Classes are created automatically from configuration
- **Type flexibility**: Any Python class can be specified via its import path
- **Composability**: Complex objects can be nested as init_args for other objects
- **Validation**: The rslearn framework validates class paths and arguments at load time

### Key Component Type Diagram

```mermaid
graph TB
    subgraph "Model Components"
        LIGHTNING["RslearnLightningModule<br/>rslearn.train.lightning_module"]
        MULTITASK["MultiTaskModel<br/>rslearn.models.multitask"]
        OLMOEARTH["OlmoEarth<br/>rslearn.models.olmoearth_pretrain.model"]
        UPSAMPLE["Upsample<br/>rslearn.models.upsample"]
        CONV["Conv<br/>rslearn.models.conv"]
        SEGHEAD["SegmentationHead<br/>rslearn.train.tasks.segmentation"]
    end
    
    subgraph "Data Components"
        DATAMODULE["RslearnDataModule<br/>rslearn.train.data_module"]
        MULTITASK_TASK["MultiTask<br/>rslearn.train.tasks.multi_task"]
        SEG_TASK["SegmentationTask<br/>rslearn.train.tasks.segmentation"]
        SEG_METRIC["SegmentationMetric<br/>rslearn.train.tasks.segmentation"]
    end
    
    subgraph "Transform Components"
        NORMALIZE["OlmoEarthNormalize<br/>rslearn.models.olmoearth_pretrain.norm"]
        PAD["Pad<br/>rslearn.train.transforms.pad"]
        CROP["Crop<br/>rslearn.train.transforms.crop"]
        FLIP["Flip<br/>rslearn.train.transforms.flip"]
    end
    
    subgraph "Scheduler Components"
        PLATEAU["PlateauScheduler<br/>rslearn.train.scheduler"]
    end
    
    subgraph "Callback Components"
        CHECKPOINT["ModelCheckpoint<br/>lightning.pytorch.callbacks"]
        LR_MONITOR["LearningRateMonitor<br/>lightning.pytorch.callbacks"]
        FREEZE_UNFREEZE["FreezeUnfreeze<br/>rslearn.train.callbacks.freeze_unfreeze"]
    end
    
    subgraph "Inference Components"
        GRID_PART["GridPartitioner<br/>olmoearth_run.runner.tools.partitioners.grid_partitioner"]
        COMBINE_GEOTIFF["CombineGeotiff<br/>olmoearth_run.runner.tools.postprocessors.combine_geotiff"]
        NOOP_RASTER["NoopRaster<br/>olmoearth_run.runner.tools.postprocessors.noop_raster"]
        SPATIAL_SPLITTER["SpatialDataSplitter<br/>olmoearth_run.runner.tools.data_splitters.spatial_data_splitter"]
    end
    
    LIGHTNING --> MULTITASK
    MULTITASK --> OLMOEARTH
    MULTITASK --> UPSAMPLE
    MULTITASK --> CONV
    MULTITASK --> SEGHEAD
    
    DATAMODULE --> MULTITASK_TASK
    MULTITASK_TASK --> SEG_TASK
    SEG_TASK --> SEG_METRIC
```

**Sources:** [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:1-50](), [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:50-248](), [olmoearth_run_data/nandi/olmoearth_run.yaml:22-52]()

## Training Configuration Structure

The `rslp_finetuning.yaml` file has a three-part structure that mirrors PyTorch Lightning's architecture:

### Training Configuration Hierarchy

```mermaid
graph TB
    ROOT["rslp_finetuning.yaml"]
    
    subgraph "Model Section"
        MODEL_ROOT["model:<br/>class_path: RslearnLightningModule"]
        MODEL_INNER["model.model:<br/>class_path: MultiTaskModel"]
        ENCODER["encoder:<br/>[OlmoEarth]"]
        DECODERS["decoders:<br/>{segment: [Upsample, Conv, PickFeatures, SegmentationHead]}"]
        LR["lr: 0.0001"]
        SCHEDULER["scheduler:<br/>PlateauScheduler"]
    end
    
    subgraph "Data Section"
        DATA_ROOT["data:<br/>class_path: RslearnDataModule"]
        PATH["path:<br/>/weka/dfive-default/rslearn-eai/datasets/..."]
        INPUTS["inputs:<br/>{sentinel2_l2a, label}"]
        TASK["task:<br/>MultiTask"]
        BATCH["batch_size: 64"]
        WORKERS["num_workers: 32"]
        TRAIN_CONFIG["train_config:<br/>{transforms, groups, tags}"]
        VAL_CONFIG["val_config:<br/>{patch_size, groups, tags}"]
        TEST_CONFIG["test_config:<br/>{patch_size, groups, tags}"]
    end
    
    subgraph "Trainer Section"
        TRAINER_ROOT["trainer"]
        EPOCHS["max_epochs: 100"]
        CALLBACKS["callbacks:<br/>[LearningRateMonitor, ModelCheckpoint, FreezeUnfreeze]"]
    end
    
    ROOT --> MODEL_ROOT
    ROOT --> DATA_ROOT
    ROOT --> TRAINER_ROOT
    
    MODEL_ROOT --> MODEL_INNER
    MODEL_ROOT --> LR
    MODEL_ROOT --> SCHEDULER
    MODEL_INNER --> ENCODER
    MODEL_INNER --> DECODERS
    
    DATA_ROOT --> PATH
    DATA_ROOT --> INPUTS
    DATA_ROOT --> TASK
    DATA_ROOT --> BATCH
    DATA_ROOT --> WORKERS
    DATA_ROOT --> TRAIN_CONFIG
    DATA_ROOT --> VAL_CONFIG
    DATA_ROOT --> TEST_CONFIG
    
    TRAINER_ROOT --> EPOCHS
    TRAINER_ROOT --> CALLBACKS
```

**Sources:** [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:1-268]()

## Inference Configuration Structure

The `olmoearth_run.yaml` file configures the inference pipeline with four main sections:

### Inference Configuration Components

```mermaid
graph LR
    ROOT["olmoearth_run.yaml"]
    
    subgraph "Window Preparation"
        WINDOW_PREP["window_prep"]
        SAMPLER["sampler:<br/>NoopSampler"]
        PREPARER["labeled_window_preparer:<br/>PointToRasterWindowPreparer"]
        SPLITTER["data_splitter:<br/>SpatialDataSplitter"]
        LABEL_LAYER["label_layer: label"]
        GROUP_NAME["group_name: spatial_split"]
    end
    
    subgraph "Partitioning"
        PARTITION_STRAT["partition_strategies"]
        PART_REQUEST["partition_request_geometry:<br/>GridPartitioner(grid_size: 1.0)"]
        PREP_WINDOWS["prepare_window_geometries:<br/>GridPartitioner(grid_size: 1024)"]
    end
    
    subgraph "Post-processing"
        POSTPROC_STRAT["postprocessing_strategies"]
        PROC_DATASET["process_dataset:<br/>CombineGeotiff"]
        PROC_PARTITION["process_partition:<br/>CombineGeotiff"]
        PROC_WINDOW["process_window:<br/>NoopRaster"]
    end
    
    subgraph "Results Config"
        RESULTS["inference_results_config"]
        DATA_TYPE["data_type: RASTER"]
        CLASSIFICATION["classification_fields:<br/>[{property_name, band_index, allowed_values}]"]
    end
    
    ROOT --> WINDOW_PREP
    ROOT --> PARTITION_STRAT
    ROOT --> POSTPROC_STRAT
    ROOT --> RESULTS
    
    WINDOW_PREP --> SAMPLER
    WINDOW_PREP --> PREPARER
    WINDOW_PREP --> SPLITTER
    WINDOW_PREP --> LABEL_LAYER
    WINDOW_PREP --> GROUP_NAME
    
    PARTITION_STRAT --> PART_REQUEST
    PARTITION_STRAT --> PREP_WINDOWS
    
    POSTPROC_STRAT --> PROC_DATASET
    POSTPROC_STRAT --> PROC_PARTITION
    POSTPROC_STRAT --> PROC_WINDOW
    
    RESULTS --> DATA_TYPE
    RESULTS --> CLASSIFICATION
```

**Sources:** [olmoearth_run_data/nandi/olmoearth_run.yaml:1-92](), [olmoearth_run_data/awf/olmoearth_run.yaml:1-89]()

## Common Configuration Patterns

### Module Selectors

Module selectors are list paths used to navigate nested module hierarchies, particularly for callbacks like `FreezeUnfreeze`:

```yaml
callbacks:
  - class_path: rslearn.train.callbacks.freeze_unfreeze.FreezeUnfreeze
    init_args:
      module_selector: ["model", "encoder", 0]  # Navigate to model.encoder[0]
      unfreeze_at_epoch: 20
      unfreeze_lr_factor: 10
```

The selector `["model", "encoder", 0]` resolves to:
1. `RslearnLightningModule.model` (the `MultiTaskModel`)
2. `.encoder` (the list of encoder modules)
3. `[0]` (the first encoder, the `OlmoEarth` module)

**Sources:** [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:261-265]()

### Input Mapping

Input mapping connects data inputs to task targets:

```yaml
task:
  class_path: rslearn.train.tasks.multi_task.MultiTask
  init_args:
    tasks:
      segment:
        class_path: rslearn.train.tasks.segmentation.SegmentationTask
    input_mapping:
      segment:
        label: "targets"  # Maps data input "label" to task target "targets"
```

**Sources:** [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:207-209]()

### Band Name Specification

Band names must be specified consistently across data loading and normalization:

```yaml
inputs:
  sentinel2_l2a:
    bands: ["B02", "B03", "B04", "B08", "B05", "B06", "B07", "B8A", "B11", "B12", "B01", "B09"]

transforms:
  - class_path: rslearn.models.olmoearth_pretrain.norm.OlmoEarthNormalize
    init_args:
      band_names:
        sentinel2_l2a: ["B02", "B03", "B04", "B08", "B05", "B06", "B07", "B8A", "B11", "B12", "B01", "B09"]
```

The band order must match between data loading and normalization to ensure correct preprocessing.

**Sources:** [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:55-59](), [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:214-217]()

### Transform Chains

Transforms are applied sequentially as a pipeline. For training, a common pattern is:

```yaml
train_config:
  transforms:
    - class_path: rslearn.train.transforms.pad.Pad
      init_args:
        size: 31
        mode: "center"
    - class_path: rslearn.train.transforms.crop.Crop
      init_args:
        crop_size: 16
    - class_path: rslearn.train.transforms.flip.Flip
    - class_path: rslearn.models.olmoearth_pretrain.norm.OlmoEarthNormalize
```

This creates 16×16 patches with data augmentation (random crops and flips) and normalization.

**Sources:** [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:218-235]()

### Classification Field Definitions

Classification results are defined with value-to-label mappings and colors:

```yaml
inference_results_config:
  data_type: RASTER
  classification_fields:
    - property_name: segment
      band_index: 1
      allowed_values:
        - value: 0
          label: coffee
          color: [124, 67, 18]
        - value: 1
          label: grassland
          color: [169, 214, 146]
```

Each allowed value maps an integer class index to a human-readable label and RGB color for visualization.

**Sources:** [olmoearth_run_data/nandi/olmoearth_run.yaml:54-89]()

## Decoder Architecture Pattern

Most segmentation models use a standard decoder architecture:

```mermaid
graph LR
    INPUT["Encoder Output<br/>(768 channels)"]
    UPSAMPLE["Upsample<br/>scale_factor: 4<br/>mode: bilinear"]
    CONV["Conv<br/>768 → N classes<br/>kernel_size: 1"]
    PICK["PickFeatures<br/>indexes: [0]<br/>collapse: true"]
    SEGHEAD["SegmentationHead"]
    OUTPUT["Class Logits<br/>(N channels)"]
    
    INPUT --> UPSAMPLE
    UPSAMPLE --> CONV
    CONV --> PICK
    PICK --> SEGHEAD
    SEGHEAD --> OUTPUT
```

This pattern:
1. **Upsamples** from encoder resolution (patch_size=4) to original resolution
2. **Reduces channels** from 768 to number of classes with 1×1 convolution
3. **Picks first timestep** if multiple timesteps are present
4. **Wraps in SegmentationHead** for proper loss computation

**Sources:** [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:17-38]()

## Metric Configuration Pattern

Per-class metrics are configured using `SegmentationMetric` wrappers around torchmetrics:

```yaml
other_metrics:
  water_precision:
    class_path: rslearn.train.tasks.segmentation.SegmentationMetric
    init_args:
      metric:
        class_path: torchmetrics.classification.MulticlassPrecision
        init_args:
          num_classes: 8
          average: null
      class_idx: 1
  water_recall:
    class_path: rslearn.train.tasks.segmentation.SegmentationMetric
    init_args:
      metric:
        class_path: torchmetrics.classification.MulticlassRecall
        init_args:
          num_classes: 8
          average: null
      class_idx: 1
```

The `class_idx` parameter extracts metrics for a specific class from the multi-class metric output.

**Sources:** [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:81-98]()

## Checkpoint Path Configuration

Model checkpoints are loaded via the `checkpoint_path` parameter:

```yaml
encoder:
  - class_path: rslearn.models.olmoearth_pretrain.model.OlmoEarth
    init_args:
      checkpoint_path: /weka/dfive-default/helios/checkpoints/joer/phase2.0_base_lr0.0001_wd0.02/step667200
      selector:
        - encoder
      patch_size: 4
      random_initialization: false
      autocast_dtype: bfloat16
```

Key parameters:
- `checkpoint_path`: Full path to checkpoint directory
- `selector`: List path to extract specific module (e.g., `["encoder"]` extracts just the encoder weights)
- `random_initialization`: If `true`, ignores checkpoint and initializes randomly
- `autocast_dtype`: Dtype for automatic mixed precision (typically `bfloat16` for better numerical stability)

**Sources:** [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:8-16]()

## Temporal Layer Configuration

Multi-temporal models specify multiple layers:

```yaml
inputs:
  sentinel2_l2a:
    data_type: "raster"
    layers: ["sentinel2", "sentinel2.1", "sentinel2.2", "sentinel2.3", "sentinel2.4"]
    bands: ["B02", "B03", "B04", "B08", "B05", "B06", "B07", "B8A", "B11", "B12", "B01", "B09"]
    load_all_layers: true
```

This loads 5 timesteps of Sentinel-2 imagery (60 total channels: 5 timesteps × 12 bands). The layers must correspond to time periods defined in the dataset's `dataset.json`.

**Sources:** [olmoearth_run_data/mozambique_lulc/rslp_finetuning_in_season_novmar.yaml:54-61]()

## Data Splitting Configuration

Spatial data splitting prevents spatial autocorrelation in train/val/test splits:

```yaml
data_splitter:
  class_path: olmoearth_run.runner.tools.data_splitters.spatial_data_splitter.SpatialDataSplitter
  init_args:
    train_prop: 0.75
    val_prop: 0.25
    test_prop: 0.0
    grid_size: 128  # in pixels
```

The `grid_size` parameter determines the spatial resolution of splitting. Larger grid sizes create coarser spatial separation between splits.

**Sources:** [olmoearth_run_data/nandi/olmoearth_run.yaml:11-17]()

## Further Reference Documentation

For detailed documentation of specific components:

- **Configuration schemas**: See [Configuration Schema Reference](#10.1) for complete field definitions and validation rules
- **rslearn components**: See [rslearn Components](#10.2) for class signatures and behavior
- **Utility scripts**: See [Utility Scripts Reference](#10.3) for command-line tools and their options

---

# Page: Configuration Schema Reference

# Configuration Schema Reference

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [olmoearth_run_data/awf/dataset.json](olmoearth_run_data/awf/dataset.json)
- [olmoearth_run_data/awf/olmoearth_run.yaml](olmoearth_run_data/awf/olmoearth_run.yaml)
- [olmoearth_run_data/mozambique_lulc/dataset.json](olmoearth_run_data/mozambique_lulc/dataset.json)
- [olmoearth_run_data/mozambique_lulc/model.yaml](olmoearth_run_data/mozambique_lulc/model.yaml)
- [olmoearth_run_data/mozambique_lulc/olmoearth_run.yaml](olmoearth_run_data/mozambique_lulc/olmoearth_run.yaml)
- [olmoearth_run_data/nandi/dataset.json](olmoearth_run_data/nandi/dataset.json)
- [olmoearth_run_data/nandi/olmoearth_run.yaml](olmoearth_run_data/nandi/olmoearth_run.yaml)

</details>



This document provides a comprehensive reference for all YAML and JSON configuration files used in the olmoearth_projects repository. These configuration files control model training, data loading, inference pipelines, and output formats.

The system uses three primary configuration file types:
- **model.yaml**: Defines model architecture, training parameters, and data loading configuration for PyTorch Lightning training
- **dataset.json**: Specifies data sources, layer definitions, and satellite imagery query parameters
- **olmoearth_run.yaml**: Configures inference pipelines including partitioning strategies and post-processing

For information about how these configurations are used during training, see [Model Training](#5). For inference pipeline usage, see [olmoearth_run Pipeline](#7.1).

---

## Configuration System Overview

The following diagram shows how configuration files map to Python classes and system components:

```mermaid
graph TB
    subgraph "Configuration Files"
        MODEL_YAML["model.yaml"]
        DATASET_JSON["dataset.json"]
        RUN_YAML["olmoearth_run.yaml"]
    end
    
    subgraph "Python Classes"
        LIGHTNING["RslearnLightningModule"]
        DATAMODULE["RslearnDataModule"]
        MULTITASK["MultiTaskModel"]
        OLMOEARTH["OlmoEarth"]
        SEGHEAD["SegmentationHead"]
        SEGTASK["SegmentationTask"]
        SENTINEL2["Sentinel2"]
        GRIDPART["GridPartitioner"]
        COMBINEGEOTIFF["CombineGeotiff"]
    end
    
    subgraph "Runtime Components"
        TRAINER["PyTorch Lightning Trainer"]
        CALLBACKS["Callbacks"]
        DATALOADER["DataLoader"]
        INFERENCE["Inference Pipeline"]
    end
    
    MODEL_YAML -->|"model.class_path"| LIGHTNING
    MODEL_YAML -->|"model.init_args.model"| MULTITASK
    MODEL_YAML -->|"encoder"| OLMOEARTH
    MODEL_YAML -->|"decoders"| SEGHEAD
    MODEL_YAML -->|"data.class_path"| DATAMODULE
    MODEL_YAML -->|"task"| SEGTASK
    MODEL_YAML -->|"trainer"| TRAINER
    MODEL_YAML -->|"callbacks"| CALLBACKS
    
    DATASET_JSON -->|"data_source.class_path"| SENTINEL2
    DATASET_JSON -->|"layers"| DATALOADER
    
    RUN_YAML -->|"partition_strategies"| GRIDPART
    RUN_YAML -->|"postprocessing_strategies"| COMBINEGEOTIFF
    RUN_YAML -->|"inference_results_config"| INFERENCE
    
    LIGHTNING --> TRAINER
    DATAMODULE --> DATALOADER
    MULTITASK --> TRAINER
```

**Sources:** [olmoearth_run_data/mozambique_lulc/model.yaml:1-278](), [olmoearth_run_data/mozambique_lulc/dataset.json:1-63](), [olmoearth_run_data/mozambique_lulc/olmoearth_run.yaml:1-81]()

---

## model.yaml Schema

The `model.yaml` file configures the complete training pipeline using PyTorch Lightning's CLI interface. It follows the [jsonargparse](https://jsonargparse.readthedocs.io/) format with `class_path` and `init_args` structure.

### Root Structure

```mermaid
graph LR
    ROOT["model.yaml root"]
    MODEL["model"]
    DATA["data"]
    TRAINER["trainer"]
    
    ROOT --> MODEL
    ROOT --> DATA
    ROOT --> TRAINER
    
    MODEL --> LIGHTNING["RslearnLightningModule"]
    DATA --> DATAMODULE["RslearnDataModule"]
    TRAINER --> CALLBACKS["callbacks[]"]
```

**Sources:** [olmoearth_run_data/mozambique_lulc/model.yaml:1-278]()

### Model Section

Defines the `RslearnLightningModule` and its nested model architecture.

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `class_path` | string | Fully qualified class path | `rslearn.train.lightning_module.RslearnLightningModule` |
| `init_args.model` | object | Nested model definition | See MultiTaskModel schema |
| `init_args.lr` | float | Initial learning rate | `0.0001` |
| `init_args.plateau` | boolean | Enable ReduceLROnPlateau scheduler | `true` |
| `init_args.plateau_factor` | float | LR reduction factor | `0.2` |
| `init_args.plateau_patience` | int | Epochs before LR reduction | `2` |
| `init_args.plateau_min_lr` | float | Minimum learning rate | `0` |
| `init_args.plateau_cooldown` | int | Cooldown epochs after LR reduction | `10` |

**Sources:** [olmoearth_run_data/mozambique_lulc/model.yaml:1-31]()

#### MultiTaskModel Schema

The `model.init_args.model` field typically uses `rslearn.models.multitask.MultiTaskModel`:

| Field | Type | Description |
|-------|------|-------------|
| `class_path` | string | `rslearn.models.multitask.MultiTaskModel` |
| `init_args.encoder` | list | List of encoder modules (typically one OlmoEarth encoder) |
| `init_args.decoders` | dict | Task-specific decoder pipelines keyed by task name |

**Sources:** [olmoearth_run_data/mozambique_lulc/model.yaml:4-25]()

#### OlmoEarth Encoder Configuration

```yaml
encoder:
  - class_path: rslearn.models.olmoearth_pretrain.model.OlmoEarth
    init_args:
      checkpoint_path: ${EXTRA_FILES_PATH}
      selector: ["encoder"]
      patch_size: 4
```

| Field | Type | Description |
|-------|------|-------------|
| `checkpoint_path` | string | Path to pre-trained checkpoint (supports environment variables) |
| `selector` | list[string] | Component selector for loading checkpoint |
| `patch_size` | int | Patch size for vision transformer (typically 4) |

**Sources:** [olmoearth_run_data/mozambique_lulc/model.yaml:8-12]()

#### Decoder Configuration

Decoders are organized by task name. Each decoder is a sequential list of modules:

```yaml
decoders:
  segment:
    - class_path: rslearn.models.upsample.Upsample
      init_args:
        scale_factor: 4
    - class_path: rslearn.models.conv.Conv
      init_args:
        in_channels: 768
        out_channels: 8
        kernel_size: 1
        activation:
          class_path: torch.nn.Identity
    - class_path: rslearn.train.tasks.segmentation.SegmentationHead
```

Common decoder modules:

| Module | Purpose | Key Parameters |
|--------|---------|----------------|
| `rslearn.models.upsample.Upsample` | Spatial upsampling | `scale_factor` |
| `rslearn.models.conv.Conv` | Convolution layer | `in_channels`, `out_channels`, `kernel_size`, `activation` |
| `rslearn.train.tasks.segmentation.SegmentationHead` | Task-specific head | None (infers from data) |

**Sources:** [olmoearth_run_data/mozambique_lulc/model.yaml:13-25]()

### Data Section

Configures the `RslearnDataModule` for data loading and preprocessing.

```mermaid
graph TB
    DATA["data section"]
    INPUTS["inputs"]
    TASK["task"]
    CONFIGS["config sections"]
    
    DATA --> INPUTS
    DATA --> TASK
    DATA --> CONFIGS
    
    INPUTS --> SENTINEL["sentinel2_l2a"]
    INPUTS --> LABEL["label"]
    
    TASK --> MULTITASK["MultiTask"]
    MULTITASK --> SEGTASK["SegmentationTask"]
    
    CONFIGS --> DEFAULT["default_config"]
    CONFIGS --> TRAIN["train_config"]
    CONFIGS --> VAL["val_config"]
    CONFIGS --> TEST["test_config"]
    CONFIGS --> PREDICT["predict_config"]
```

**Sources:** [olmoearth_run_data/mozambique_lulc/model.yaml:32-245]()

#### Core Data Parameters

| Field | Type | Description |
|-------|------|-------------|
| `class_path` | string | `rslearn.train.data_module.RslearnDataModule` |
| `init_args.path` | string | Path to dataset (supports environment variables like `${DATASET_PATH}`) |
| `init_args.batch_size` | int | Batch size for training/validation |
| `init_args.num_workers` | int | Number of data loading workers |

**Sources:** [olmoearth_run_data/mozambique_lulc/model.yaml:32-193]()

#### Inputs Configuration

The `inputs` dictionary defines data layers to load:

```yaml
inputs:
  sentinel2_l2a:
    data_type: "raster"
    layers: ["sentinel2"]
    bands: ["B02", "B03", "B04", "B08", "B05", "B06", "B07", "B8A", "B11", "B12", "B01", "B09"]
    passthrough: true
    dtype: FLOAT32
    load_all_item_groups: true
    load_all_layers: true
  label:
    data_type: "raster"
    layers: ["label_raster"]
    bands: ["label"]
    is_target: true
    dtype: INT32
```

| Field | Type | Description |
|-------|------|-------------|
| `data_type` | string | Data type: `"raster"`, `"vector"`, etc. |
| `layers` | list[string] | Layer names to load from dataset |
| `bands` | list[string] | Band names to extract |
| `passthrough` | boolean | Whether to pass data through without processing |
| `dtype` | string | Data type: `FLOAT32`, `INT32`, etc. |
| `load_all_item_groups` | boolean | Load all temporal groups |
| `load_all_layers` | boolean | Load all layer variants |
| `is_target` | boolean | Mark as target/label data |

**Sources:** [olmoearth_run_data/mozambique_lulc/model.yaml:36-50]()

#### Task Configuration

The `task` field defines the learning task and metrics:

```yaml
task:
  class_path: rslearn.train.tasks.multi_task.MultiTask
  init_args:
    tasks:
      segment:
        class_path: rslearn.train.tasks.segmentation.SegmentationTask
        init_args:
          num_classes: 8
          zero_is_invalid: true
          metric_kwargs:
            average: "micro"
```

**SegmentationTask Parameters:**

| Field | Type | Description |
|-------|------|-------------|
| `num_classes` | int | Number of output classes |
| `zero_is_invalid` | boolean | Treat class 0 as invalid/ignore |
| `metric_kwargs.average` | string | Averaging strategy: `"micro"`, `"macro"`, `"weighted"`, or `null` |
| `other_metrics` | dict | Additional per-class metrics |

**Sources:** [olmoearth_run_data/mozambique_lulc/model.yaml:51-188]()

#### Per-Class Metrics

Define additional metrics for individual classes using `other_metrics`:

```yaml
other_metrics:
  water_precision:
    class_path: rslearn.train.tasks.segmentation.SegmentationMetric
    init_args:
      metric:
        class_path: torchmetrics.classification.MulticlassPrecision
        init_args:
          num_classes: 8
          average: null
      class_idx: 1
```

| Field | Type | Description |
|-------|------|-------------|
| `metric.class_path` | string | Torchmetrics class path |
| `metric.init_args.num_classes` | int | Total number of classes |
| `metric.init_args.average` | null/string | Set to `null` for per-class metrics |
| `class_idx` | int | Index of class to extract |

**Sources:** [olmoearth_run_data/mozambique_lulc/model.yaml:62-188]()

#### Configuration Sections

Different configurations for train/val/test/predict stages:

| Section | Purpose | Key Fields |
|---------|---------|------------|
| `default_config` | Applied to all stages | `transforms` |
| `train_config` | Training stage | `transforms`, `groups`, `tags`, `patch_size` not used (full images) |
| `val_config` | Validation stage | `patch_size`, `groups`, `tags` |
| `test_config` | Test stage | `patch_size`, `groups`, `tags` |
| `predict_config` | Inference stage | `load_all_patches`, `patch_size`, `overlap_ratio`, `skip_targets`, `transforms` |

**Sources:** [olmoearth_run_data/mozambique_lulc/model.yaml:194-245]()

#### Transform Pipelines

Transforms are specified as lists of class instantiations:

```yaml
transforms:
  - class_path: rslearn.train.transforms.pad.Pad
    init_args:
      size: 31
      mode: "center"
      image_selectors: ["sentinel2_l2a", "target/segment/classes", "target/segment/valid"]
  - class_path: rslearn.train.transforms.crop.Crop
    init_args:
      crop_size: 16
      image_selectors: ["sentinel2_l2a", "target/segment/classes", "target/segment/valid"]
  - class_path: rslearn.models.olmoearth_pretrain.norm.OlmoEarthNormalize
    init_args:
      band_names:
        sentinel2_l2a: ["B02", "B03", "B04", "B08", "B05", "B06", "B07", "B8A", "B11", "B12", "B01", "B09"]
```

**Common Transforms:**

| Transform | Purpose | Key Parameters |
|-----------|---------|----------------|
| `rslearn.train.transforms.pad.Pad` | Pad images | `size` (pixels), `mode`, `image_selectors` |
| `rslearn.train.transforms.crop.Crop` | Random crop | `crop_size`, `image_selectors` |
| `rslearn.train.transforms.flip.Flip` | Random flip augmentation | `image_selectors` |
| `rslearn.models.olmoearth_pretrain.norm.OlmoEarthNormalize` | Normalize for OlmoEarth | `band_names` (dict mapping layer to band list) |

**Sources:** [olmoearth_run_data/mozambique_lulc/model.yaml:195-245]()

#### Predict Configuration

Special parameters for inference:

| Field | Type | Description |
|-------|------|-------------|
| `load_all_patches` | boolean | Load entire image as patches |
| `patch_size` | int | Size of inference patches |
| `overlap_ratio` | float | Overlap between patches (e.g., `0.25` = 25% overlap) |
| `skip_targets` | boolean | Skip loading target data |

**Sources:** [olmoearth_run_data/mozambique_lulc/model.yaml:236-245]()

### Trainer Section

Configures PyTorch Lightning `Trainer` and callbacks:

```yaml
trainer:
  max_epochs: 100
  default_root_dir: ${TRAINER_DATA_PATH}
  logger:
    class_path: lightning.pytorch.loggers.WandbLogger
    init_args:
      project: ${WANDB_PROJECT}
      name: ${WANDB_NAME}
      entity: ${WANDB_ENTITY}
  callbacks:
    - class_path: lightning.pytorch.callbacks.LearningRateMonitor
    - class_path: lightning.pytorch.callbacks.ModelCheckpoint
    - class_path: rslearn.train.callbacks.freeze_unfreeze.FreezeUnfreeze
    - class_path: rslearn.train.prediction_writer.RslearnWriter
```

**Sources:** [olmoearth_run_data/mozambique_lulc/model.yaml:246-278]()

#### Trainer Parameters

| Field | Type | Description |
|-------|------|-------------|
| `max_epochs` | int | Maximum training epochs |
| `default_root_dir` | string | Root directory for checkpoints and logs |
| `logger` | object | Logger configuration (typically WandbLogger) |

#### Callback Configurations

**LearningRateMonitor:**
```yaml
- class_path: lightning.pytorch.callbacks.LearningRateMonitor
  init_args:
    logging_interval: "epoch"
```

**ModelCheckpoint:**
```yaml
- class_path: lightning.pytorch.callbacks.ModelCheckpoint
  init_args:
    save_top_k: 1
    save_last: true
    monitor: val_loss
    mode: min
```

| Field | Description |
|-------|-------------|
| `save_top_k` | Number of best models to save |
| `save_last` | Whether to save last checkpoint |
| `monitor` | Metric to monitor |
| `mode` | `"min"` or `"max"` |

**FreezeUnfreeze:**
```yaml
- class_path: rslearn.train.callbacks.freeze_unfreeze.FreezeUnfreeze
  init_args:
    module_selector: ["model", "encoder", 0]
    unfreeze_at_epoch: 2
```

| Field | Description |
|-------|-------------|
| `module_selector` | Path to module to freeze/unfreeze |
| `unfreeze_at_epoch` | Epoch at which to unfreeze |

**RslearnWriter:**
```yaml
- class_path: rslearn.train.prediction_writer.RslearnWriter
  init_args:
    path: placeholder
    output_layer: ${PREDICTION_OUTPUT_LAYER}
    selector: ["segment"]
    merger:
      class_path: rslearn.train.prediction_writer.RasterMerger
      init_args:
        padding: 2
```

| Field | Description |
|-------|-------------|
| `path` | Output path for predictions |
| `output_layer` | Layer name for output |
| `selector` | Task selector |
| `merger` | Merger for combining predictions |

**Sources:** [olmoearth_run_data/mozambique_lulc/model.yaml:255-278]()

---

## dataset.json Schema

The `dataset.json` file defines data layers, their structure, and data source configurations. It uses a JSON format with nested dictionaries.

### Root Structure

```mermaid
graph TB
    ROOT["dataset.json"]
    LAYERS["layers"]
    
    ROOT --> LAYERS
    
    LAYERS --> LABEL["label"]
    LAYERS --> OUTPUT["output"]
    LAYERS --> SENTINEL["sentinel2"]
    
    SENTINEL --> BANDS["band_sets"]
    SENTINEL --> SOURCE["data_source"]
    
    SOURCE --> CLASSPATH["class_path"]
    SOURCE --> INIT["init_args"]
    SOURCE --> QUERY["query_config"]
```

**Sources:** [olmoearth_run_data/mozambique_lulc/dataset.json:1-63]()

### Layers Structure

Each layer defines a data source or output specification:

```json
{
  "layers": {
    "layer_name": {
      "type": "raster",
      "band_sets": [...],
      "data_source": {...}
    }
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `type` | string | Layer type: `"raster"`, `"vector"`, etc. |
| `band_sets` | list | List of band set definitions |
| `data_source` | object | Optional data source configuration |

**Sources:** [olmoearth_run_data/mozambique_lulc/dataset.json:2-62]()

### Band Sets

Define the bands available in a layer:

```json
"band_sets": [
  {
    "bands": ["B01", "B02", "B03", "B04", "B05", "B06", "B07", "B08", "B8A", "B09", "B11", "B12"],
    "dtype": "uint16"
  }
]
```

| Field | Type | Description |
|-------|------|-------------|
| `bands` | list[string] | Band names |
| `dtype` | string | Data type: `"uint16"`, `"int32"`, `"float32"` |

**Sources:** [olmoearth_run_data/mozambique_lulc/dataset.json:26-43]()

### Data Source Configuration

Specifies how to acquire data from external sources:

```json
"data_source": {
  "class_path": "rslearn.data_sources.planetary_computer.Sentinel2",
  "ingest": false,
  "init_args": {
    "cache_dir": "cache/planetary_computer",
    "harmonize": true,
    "sort_by": "eo:cloud_cover"
  },
  "query_config": {
    "max_matches": 8,
    "min_matches": 8,
    "period_duration": "30d",
    "space_mode": "PER_PERIOD_MOSAIC"
  }
}
```

**Sources:** [olmoearth_run_data/mozambique_lulc/dataset.json:45-58]()

#### Data Source Parameters

| Field | Type | Description |
|-------|------|-------------|
| `class_path` | string | Python class for data source (e.g., `rslearn.data_sources.planetary_computer.Sentinel2`) |
| `ingest` | boolean | Whether to ingest data into dataset |
| `init_args` | object | Initialization arguments for data source class |
| `query_config` | object | Query configuration for temporal/spatial queries |

#### Sentinel-2 Init Args

| Field | Type | Description |
|-------|------|-------------|
| `cache_dir` | string | Directory for caching downloaded data |
| `harmonize` | boolean | Apply harmonization to Sentinel-2 data |
| `sort_by` | string | Property to sort results by (e.g., `"eo:cloud_cover"`) |

**Sources:** [olmoearth_run_data/mozambique_lulc/dataset.json:48-52]()

#### Query Configuration

| Field | Type | Description | Example Values |
|-------|------|-------------|----------------|
| `max_matches` | int | Maximum temporal images to return | `8`, `12` |
| `min_matches` | int | Minimum temporal images required | `8`, `12` |
| `period_duration` | string | Duration of each temporal period | `"30d"`, `"15d"` |
| `space_mode` | string | Spatial aggregation mode | `"PER_PERIOD_MOSAIC"`, `"SINGLE_MOSAIC"` |

**Space Mode Values:**
- `PER_PERIOD_MOSAIC`: Create one mosaic per temporal period
- `SINGLE_MOSAIC`: Create a single mosaic for entire time range

**Sources:** [olmoearth_run_data/mozambique_lulc/dataset.json:53-58](), [olmoearth_run_data/awf/dataset.json:53-58](), [olmoearth_run_data/nandi/dataset.json:53-58]()

### Label and Output Layers

Standard layers without data sources:

```json
"label": {
  "band_sets": [
    {
      "bands": ["category"],
      "dtype": "int32"
    }
  ],
  "type": "raster"
}
```

```json
"output": {
  "band_sets": [
    {
      "bands": ["output"],
      "dtype": "float32"
    }
  ],
  "type": "raster"
}
```

**Sources:** [olmoearth_run_data/mozambique_lulc/dataset.json:3-24]()

---

## olmoearth_run.yaml Schema

The `olmoearth_run.yaml` file configures the inference pipeline, including data preparation, partitioning strategies, post-processing, and output metadata.

### Root Structure

```mermaid
graph TB
    ROOT["olmoearth_run.yaml"]
    
    WINDOW["window_prep"]
    PARTITION["partition_strategies"]
    POSTPROC["postprocessing_strategies"]
    INFERENCE["inference_results_config"]
    
    ROOT --> WINDOW
    ROOT --> PARTITION
    ROOT --> POSTPROC
    ROOT --> INFERENCE
    
    WINDOW --> SAMPLER["sampler"]
    WINDOW --> PREPARER["labeled_window_preparer"]
    WINDOW --> SPLITTER["data_splitter"]
    
    PARTITION --> REQ["partition_request_geometry"]
    PARTITION --> PREP["prepare_window_geometries"]
    
    POSTPROC --> DATASET["process_dataset"]
    POSTPROC --> PART["process_partition"]
    POSTPROC --> WIN["process_window"]
    
    INFERENCE --> DTYPE["data_type"]
    INFERENCE --> CLASSFIELDS["classification_fields"]
```

**Sources:** [olmoearth_run_data/mozambique_lulc/olmoearth_run.yaml:1-81](), [olmoearth_run_data/nandi/olmoearth_run.yaml:1-92](), [olmoearth_run_data/awf/olmoearth_run.yaml:1-89]()

### Window Preparation

Configures how to prepare training/inference windows:

```yaml
window_prep:
  sampler:
    class_path: olmoearth_run.runner.tools.samplers.noop_sampler.NoopSampler
  labeled_window_preparer:
    class_path: olmoearth_run.runner.tools.labeled_window_preparers.point_to_raster_window_preparer.PointToRasterWindowPreparer
    init_args:
      window_buffer: 31
      window_resolution: 10.0
      dtype: INT32
      nodata_value: 255
  data_splitter:
    class_path: olmoearth_run.runner.tools.data_splitters.spatial_data_splitter.SpatialDataSplitter
    init_args:
      train_prop: 0.75
      val_prop: 0.25
      test_prop: 0.0
      grid_size: 128
  label_layer: "label"
  group_name: "spatial_split"
  split_property: "split"
```

**Sources:** [olmoearth_run_data/mozambique_lulc/olmoearth_run.yaml:29-48]()

#### Window Prep Parameters

| Field | Type | Description |
|-------|------|-------------|
| `sampler.class_path` | string | Sampler class (typically `NoopSampler` for no sampling) |
| `labeled_window_preparer.class_path` | string | Window preparer class |
| `data_splitter.class_path` | string | Data splitting strategy class |
| `label_layer` | string | Name of label layer in dataset |
| `group_name` | string | Group name for organizing splits |
| `split_property` | string | Property name for split assignment |

#### PointToRasterWindowPreparer

| Field | Type | Description |
|-------|------|-------------|
| `window_buffer` | int | Buffer around point in pixels |
| `window_resolution` | float | Resolution in meters per pixel |
| `dtype` | string | Data type for output raster |
| `nodata_value` | int | Value to use for no-data pixels |

**Sources:** [olmoearth_run_data/mozambique_lulc/olmoearth_run.yaml:32-38]()

#### SpatialDataSplitter

| Field | Type | Description |
|-------|------|-------------|
| `train_prop` | float | Proportion for training (0.0-1.0) |
| `val_prop` | float | Proportion for validation (0.0-1.0) |
| `test_prop` | float | Proportion for testing (0.0-1.0) |
| `grid_size` | int | Grid cell size in pixels for spatial splitting |

**Sources:** [olmoearth_run_data/mozambique_lulc/olmoearth_run.yaml:39-45]()

### Partition Strategies

Define how to partition large geographic areas:

```yaml
partition_strategies:
  partition_request_geometry:
    class_path: olmoearth_run.runner.tools.partitioners.grid_partitioner.GridPartitioner
    init_args:
      grid_size: 0.25
  
  prepare_window_geometries:
    class_path: olmoearth_run.runner.tools.partitioners.grid_partitioner.GridPartitioner
    init_args:
      grid_size: 1024
      output_projection:
        class_path: rslearn.utils.geometry.Projection
        init_args:
          crs: EPSG:3857
          x_resolution: 10
          y_resolution: -10
      use_utm: true
```

**Sources:** [olmoearth_run_data/mozambique_lulc/olmoearth_run.yaml:50-66]()

#### GridPartitioner Parameters

| Field | Type | Description | Typical Values |
|-------|------|-------------|----------------|
| `grid_size` | float/int | Grid cell size in degrees (for geographic) or pixels (for projected) | `0.25`, `1.0` (degrees), `1024` (pixels) |
| `output_projection` | object | Projection specification for output | See Projection schema |
| `use_utm` | boolean | Automatically use appropriate UTM zone | `true`, `false` |

#### Projection Schema

| Field | Type | Description |
|-------|------|-------------|
| `crs` | string | Coordinate reference system (e.g., `EPSG:3857`, `EPSG:4326`) |
| `x_resolution` | float | X-axis resolution in CRS units |
| `y_resolution` | float | Y-axis resolution in CRS units (negative for north-up) |

**Sources:** [olmoearth_run_data/mozambique_lulc/olmoearth_run.yaml:60-65]()

### Post-processing Strategies

Define how to combine and process results at different levels:

```yaml
postprocessing_strategies:
  process_dataset:
    class_path: olmoearth_run.runner.tools.postprocessors.combine_geotiff.CombineGeotiff
    init_args:
      nodata_value: 255
  
  process_partition:
    class_path: olmoearth_run.runner.tools.postprocessors.combine_geotiff.CombineGeotiff
    init_args:
      nodata_value: 255
  
  process_window:
    class_path: olmoearth_run.runner.tools.postprocessors.noop_raster.NoopRaster
```

**Sources:** [olmoearth_run_data/mozambique_lulc/olmoearth_run.yaml:68-80]()

#### Post-processing Levels

| Level | Purpose | Typical Class |
|-------|---------|---------------|
| `process_window` | Process individual inference windows | `NoopRaster` (no processing) |
| `process_partition` | Combine windows within a partition | `CombineGeotiff` |
| `process_dataset` | Combine all partitions into final output | `CombineGeotiff` |

#### CombineGeotiff Parameters

| Field | Type | Description |
|-------|------|-------------|
| `nodata_value` | int | Value representing no-data pixels |

**Sources:** [olmoearth_run_data/mozambique_lulc/olmoearth_run.yaml:68-77]()

### Inference Results Configuration

Defines metadata for output rasters including classification schemes and visualization:

```yaml
inference_results_config:
  data_type: RASTER
  classification_fields:
    - property_name: segment
      band_index: 1
      allowed_values:
        - value: 0
          label: coffee
          color: [124, 67, 18]
        - value: 1
          label: grassland
          color: [169, 214, 146]
  detection_objects: null
  regression_fields: null
```

**Sources:** [olmoearth_run_data/nandi/olmoearth_run.yaml:54-92]()

#### Results Config Schema

| Field | Type | Description |
|-------|------|-------------|
| `data_type` | string | Output data type (typically `RASTER`) |
| `classification_fields` | list | List of classification field definitions |
| `detection_objects` | list/null | Object detection definitions (if applicable) |
| `regression_fields` | list/null | Regression field definitions (if applicable) |

#### Classification Field Schema

| Field | Type | Description |
|-------|------|-------------|
| `property_name` | string | Name of the classification property |
| `band_index` | int | Band index in output raster (1-indexed) |
| `allowed_values` | list | List of valid class definitions |

#### Allowed Value Schema

| Field | Type | Description |
|-------|------|-------------|
| `value` | int | Pixel value in output raster |
| `label` | string | Human-readable class label |
| `color` | list[int] | RGB color for visualization [R, G, B] where each component is 0-255 |

**Sources:** [olmoearth_run_data/nandi/olmoearth_run.yaml:56-90](), [olmoearth_run_data/awf/olmoearth_run.yaml:56-88](), [olmoearth_run_data/mozambique_lulc/olmoearth_run.yaml:1-27]()

---

## Configuration Schema Cross-Reference

The following diagram shows how different configuration schemas interact during training and inference:

```mermaid
graph TB
    subgraph "Training Phase"
        MODEL_TRAIN["model.yaml<br/>model section"]
        MODEL_DATA["model.yaml<br/>data section"]
        DATASET["dataset.json"]
        
        MODEL_DATA -->|"path"| DATASET
        MODEL_TRAIN -->|"encoder checkpoint"| WEIGHTS["Pre-trained Weights"]
    end
    
    subgraph "Inference Phase"
        OERUN["olmoearth_run.yaml"]
        DATASET_INF["dataset.json"]
        MODEL_INF["model.yaml"]
        
        OERUN -->|"partition_strategies"| GEOMS["Window Geometries"]
        DATASET_INF -->|"query_config"| IMAGERY["Satellite Imagery"]
        MODEL_INF -->|"predict_config"| PATCHES["Inference Patches"]
        OERUN -->|"inference_results_config"| METADATA["Output Metadata"]
    end
    
    subgraph "Outputs"
        CHECKPOINT["Model Checkpoint"]
        GEOTIFF["Result GeoTIFF"]
        
        MODEL_TRAIN --> CHECKPOINT
        CHECKPOINT --> MODEL_INF
        PATCHES --> GEOTIFF
        METADATA --> GEOTIFF
    end
```

**Sources:** All configuration files referenced above

---

## Environment Variables in Configuration

Configuration files support environment variable substitution using the `${VAR_NAME}` syntax:

| Variable | Usage | Description |
|----------|-------|-------------|
| `${EXTRA_FILES_PATH}` | `model.yaml` encoder checkpoint path | Path to OlmoEarth pre-trained weights |
| `${DATASET_PATH}` | `model.yaml` data path | Path to training dataset |
| `${NUM_WORKERS}` | `model.yaml` data loader | Number of data loading workers |
| `${TRAINER_DATA_PATH}` | `model.yaml` trainer root dir | Path for checkpoints and logs |
| `${WANDB_PROJECT}` | `model.yaml` logger | Weights & Biases project name |
| `${WANDB_NAME}` | `model.yaml` logger | Weights & Biases run name |
| `${WANDB_ENTITY}` | `model.yaml` logger | Weights & Biases entity |
| `${PREDICTION_OUTPUT_LAYER}` | `model.yaml` prediction writer | Output layer name for predictions |

**Sources:** [olmoearth_run_data/mozambique_lulc/model.yaml:10-272]()

---

## Common Configuration Patterns

### Pattern 1: Segmentation Task

Standard configuration for semantic segmentation:

```yaml
# model.yaml
model:
  init_args:
    model:
      encoder:
        - class_path: rslearn.models.olmoearth_pretrain.model.OlmoEarth
      decoders:
        segment:
          - class_path: rslearn.models.upsample.Upsample
          - class_path: rslearn.models.conv.Conv
          - class_path: rslearn.train.tasks.segmentation.SegmentationHead
data:
  init_args:
    task:
      tasks:
        segment:
          class_path: rslearn.train.tasks.segmentation.SegmentationTask
          init_args:
            num_classes: 8
```

**Sources:** [olmoearth_run_data/mozambique_lulc/model.yaml:1-59]()

### Pattern 2: Multi-Temporal Sentinel-2

Standard dataset configuration for time series:

```json
{
  "data_source": {
    "class_path": "rslearn.data_sources.planetary_computer.Sentinel2",
    "query_config": {
      "max_matches": 12,
      "min_matches": 12,
      "period_duration": "30d",
      "space_mode": "PER_PERIOD_MOSAIC"
    }
  }
}
```

**Sources:** [olmoearth_run_data/awf/dataset.json:45-58](), [olmoearth_run_data/nandi/dataset.json:45-58]()

### Pattern 3: Hierarchical Partitioning

Standard partitioning for large-area inference:

```yaml
partition_strategies:
  partition_request_geometry:
    class_path: olmoearth_run.runner.tools.partitioners.grid_partitioner.GridPartitioner
    init_args:
      grid_size: 1.0  # degrees
  
  prepare_window_geometries:
    class_path: olmoearth_run.runner.tools.partitioners.grid_partitioner.GridPartitioner
    init_args:
      grid_size: 1024  # pixels
      use_utm: true
```

**Sources:** [olmoearth_run_data/nandi/olmoearth_run.yaml:22-38](), [olmoearth_run_data/awf/olmoearth_run.yaml:22-38]()

---

## Validation and Error Handling

Configuration files are validated at runtime using the following mechanisms:

1. **Class Path Resolution**: All `class_path` fields must resolve to valid Python classes
2. **Type Checking**: Parameters are type-checked against class signatures
3. **Required Fields**: Missing required parameters raise errors during initialization
4. **Value Constraints**: Some fields have valid value constraints (e.g., `average` must be `"micro"`, `"macro"`, `"weighted"`, or `null`)

Common validation errors:

| Error Type | Cause | Solution |
|------------|-------|----------|
| `ModuleNotFoundError` | Invalid `class_path` | Verify class path and imports |
| `TypeError` | Invalid parameter type | Check parameter types in schema |
| `ValueError` | Invalid parameter value | Check allowed values for field |
| `KeyError` | Missing required field | Add required field to configuration |

**Sources:** All configuration files

---

# Page: rslearn Components

# rslearn Components

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [olmoearth_run_data/mangrove/dataset.json](olmoearth_run_data/mangrove/dataset.json)
- [olmoearth_run_data/mangrove/model.yaml](olmoearth_run_data/mangrove/model.yaml)
- [olmoearth_run_data/mangrove/olmoearth_run.yaml](olmoearth_run_data/mangrove/olmoearth_run.yaml)
- [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml](olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml)
- [olmoearth_run_data/mozambique_lulc/rslp_finetuning_croptype.yaml](olmoearth_run_data/mozambique_lulc/rslp_finetuning_croptype.yaml)
- [olmoearth_run_data/mozambique_lulc/rslp_finetuning_croptype_in_season_novmar.yaml](olmoearth_run_data/mozambique_lulc/rslp_finetuning_croptype_in_season_novmar.yaml)
- [olmoearth_run_data/mozambique_lulc/rslp_finetuning_in_season_novmar.yaml](olmoearth_run_data/mozambique_lulc/rslp_finetuning_in_season_novmar.yaml)

</details>



This document provides technical reference documentation for the `rslearn` framework components used throughout the olmoearth_projects repository. The rslearn framework is a PyTorch Lightning-based training and inference system that provides standardized interfaces for model definition, data loading, training, and evaluation.

For configuration file schemas using these components, see [Configuration Schema Reference](#10.1). For information about the training process that orchestrates these components, see [Model Training](#5).

## Component Architecture Overview

The rslearn framework follows a modular architecture where components are composed via YAML configuration files using PyTorch Lightning's class path instantiation system.

```mermaid
graph TB
    subgraph "Top-Level Components"
        LightningModule["rslearn.train.lightning_module<br/>RslearnLightningModule"]
        DataModule["rslearn.train.data_module<br/>RslearnDataModule"]
        Trainer["lightning.pytorch.Trainer"]
    end
    
    subgraph "Model Architecture Components"
        MultiTaskModel["rslearn.models.multitask<br/>MultiTaskModel"]
        Encoder["rslearn.models.olmoearth_pretrain.model<br/>OlmoEarth"]
        Decoders["Decoder Layers<br/>Upsample, Conv, PickFeatures"]
        TaskHead["rslearn.train.tasks.segmentation<br/>SegmentationHead"]
    end
    
    subgraph "Data Components"
        DataInput["rslearn.train.dataset<br/>DataInput"]
        Task["rslearn.train.tasks.multi_task<br/>MultiTask"]
        SegTask["rslearn.train.tasks.segmentation<br/>SegmentationTask"]
        SplitConfig["rslearn.train.dataset<br/>SplitConfig"]
    end
    
    subgraph "Training Components"
        Scheduler["rslearn.train.scheduler<br/>PlateauScheduler"]
        Callbacks["rslearn.train.callbacks.freeze_unfreeze<br/>FreezeUnfreeze"]
        Writer["rslearn.train.prediction_writer<br/>RslearnWriter"]
    end
    
    subgraph "Transform Components"
        Normalize["rslearn.models.olmoearth_pretrain.norm<br/>OlmoEarthNormalize"]
        Pad["rslearn.train.transforms.pad<br/>Pad"]
        Crop["rslearn.train.transforms.crop<br/>Crop"]
        Flip["rslearn.train.transforms.flip<br/>Flip"]
    end
    
    Trainer --> LightningModule
    Trainer --> DataModule
    
    LightningModule --> MultiTaskModel
    LightningModule --> Scheduler
    
    MultiTaskModel --> Encoder
    MultiTaskModel --> Decoders
    Decoders --> TaskHead
    
    DataModule --> DataInput
    DataModule --> Task
    DataModule --> SplitConfig
    
    Task --> SegTask
    
    SplitConfig --> Normalize
    SplitConfig --> Pad
    SplitConfig --> Crop
    SplitConfig --> Flip
    
    Trainer --> Callbacks
    Trainer --> Writer
```

**Sources:** [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:1-268](), [olmoearth_run_data/mangrove/model.yaml:1-394]()

## RslearnLightningModule

The `rslearn.train.lightning_module.RslearnLightningModule` is the top-level training module that wraps the model architecture and training logic. It extends PyTorch Lightning's `LightningModule` to provide standardized training, validation, and testing loops.

### Configuration Structure

```yaml
model:
  class_path: rslearn.train.lightning_module.RslearnLightningModule
  init_args:
    model: <MultiTaskModel or other model>
    lr: <learning_rate>
    scheduler: <scheduler_config>
    optimizer: <optimizer_config>
```

### Key Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `model` | Model | The neural network model (typically `MultiTaskModel`) |
| `lr` | float | Base learning rate (e.g., 0.0001) |
| `scheduler` | dict | Learning rate scheduler configuration |
| `optimizer` | dict | Optimizer configuration (default: AdamW) |
| `plateau` | bool | Whether to use plateau-based scheduling |
| `visualize_dir` | str | Directory for visualization outputs |
| `print_parameters` | bool | Whether to print parameter counts |

**Sources:** [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:1-6](), [olmoearth_run_data/mangrove/model.yaml:3-40]()

## RslearnDataModule

The `rslearn.train.data_module.RslearnDataModule` manages data loading, transformations, and batch generation for training and inference. It provides a unified interface for accessing rslearn datasets.

```mermaid
graph LR
    subgraph "RslearnDataModule"
        Path["path:<br/>Dataset directory"]
        Inputs["inputs:<br/>DataInput specifications"]
        Task["task:<br/>Task definitions"]
        BatchSize["batch_size:<br/>Batch configuration"]
    end
    
    subgraph "Split Configurations"
        Train["train_config:<br/>SplitConfig"]
        Val["val_config:<br/>SplitConfig"]
        Test["test_config:<br/>SplitConfig"]
        Predict["predict_config:<br/>SplitConfig"]
    end
    
    subgraph "Data Pipeline"
        Dataset["rslearn Dataset<br/>tar archive"]
        Loader["PyTorch DataLoader"]
        Transforms["Transform Pipeline"]
    end
    
    Path --> Dataset
    Inputs --> Dataset
    Task --> Dataset
    
    Train --> Transforms
    Val --> Transforms
    Test --> Transforms
    Predict --> Transforms
    
    Dataset --> Loader
    Transforms --> Loader
    BatchSize --> Loader
```

### Configuration Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `path` | str | Path to rslearn dataset directory or tar file |
| `inputs` | dict | Dictionary of `DataInput` specifications for each input source |
| `task` | Task | Task configuration (e.g., `MultiTask`, `SegmentationTask`) |
| `batch_size` | int | Number of samples per batch (e.g., 64, 128) |
| `num_workers` | int | Number of data loading workers |
| `default_config` | SplitConfig | Default configuration for all splits |
| `train_config` | SplitConfig | Training-specific configuration |
| `val_config` | SplitConfig | Validation-specific configuration |
| `test_config` | SplitConfig | Test-specific configuration |
| `predict_config` | SplitConfig | Inference-specific configuration |

**Sources:** [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:50-248](), [olmoearth_run_data/mangrove/model.yaml:41-340]()

### DataInput Specification

The `rslearn.train.dataset.DataInput` class defines how to load individual data sources.

```yaml
sentinel2_l2a:
  data_type: "raster"
  layers: ["sentinel2"]
  bands: ["B02", "B03", "B04", "B08", "B05", "B06", "B07", "B8A", "B11", "B12", "B01", "B09"]
  passthrough: true
  dtype: FLOAT32
  load_all_item_groups: true
  load_all_layers: true
```

| Field | Type | Description |
|-------|------|-------------|
| `data_type` | str | Type of data: "raster" or "vector" |
| `layers` | list[str] | Layer names to load from dataset |
| `bands` | list[str] | Specific bands to extract |
| `passthrough` | bool | Whether to pass through to model unchanged |
| `is_target` | bool | Whether this is a target/label |
| `dtype` | str | Data type: FLOAT32, INT32, etc. |
| `load_all_layers` | bool | Load all temporal layers |
| `load_all_item_groups` | bool | Load all spatial groups |

**Sources:** [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:54-68](), [olmoearth_run_data/mangrove/model.yaml:44-83]()

### SplitConfig

The `rslearn.train.dataset.SplitConfig` class configures data loading for specific splits (train/val/test).

```yaml
train_config:
  groups: ["gaza", "manica", "zambezia"]
  tags:
    split: "train"
  transforms:
    - class_path: rslearn.train.transforms.pad.Pad
      init_args:
        size: 31
        mode: "center"
    - class_path: rslearn.train.transforms.crop.Crop
      init_args:
        crop_size: 16
```

| Field | Type | Description |
|-------|------|-------------|
| `groups` | list[str] | Dataset groups to include (e.g., provinces) |
| `names` | list[str] | Specific sample names to include |
| `tags` | dict | Tag filters (e.g., `split: "train"`) |
| `num_samples` | int | Limit number of samples |
| `transforms` | list | Transformation pipeline |
| `patch_size` | int | Patch size for inference |
| `overlap_ratio` | float | Overlap ratio for sliding window inference |

**Sources:** [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:218-248](), [olmoearth_run_data/mangrove/model.yaml:287-316]()

## Model Components

### MultiTaskModel

The `rslearn.models.multitask.MultiTaskModel` enables training multiple tasks simultaneously with shared encoders and task-specific decoders.

```mermaid
graph TB
    Input["Input Data<br/>sentinel2_l2a"]
    
    subgraph "MultiTaskModel"
        Encoder["encoder:<br/>List of encoder layers"]
        Trunk["trunk:<br/>Optional shared layers"]
        
        subgraph "Task-Specific Decoders"
            Decoder1["decoders['segment']:<br/>Segmentation decoder"]
            Decoder2["decoders['task2']:<br/>Additional task"]
        end
        
        LossWeights["loss_weights:<br/>Task loss weighting"]
    end
    
    Output1["Task 1 Output"]
    Output2["Task 2 Output"]
    
    Input --> Encoder
    Encoder --> Trunk
    Trunk --> Decoder1
    Trunk --> Decoder2
    
    Decoder1 --> Output1
    Decoder2 --> Output2
    
    LossWeights -.->|weight| Output1
    LossWeights -.->|weight| Output2
```

**Configuration:**

```yaml
model:
  class_path: rslearn.models.multitask.MultiTaskModel
  init_args:
    encoder:
      - class_path: rslearn.models.olmoearth_pretrain.model.OlmoEarth
        init_args:
          checkpoint_path: /path/to/checkpoint
          patch_size: 4
    decoders:
      segment:
        - class_path: rslearn.models.upsample.Upsample
        - class_path: rslearn.models.conv.Conv
        - class_path: rslearn.train.tasks.segmentation.SegmentationHead
    lazy_decode: false
    loss_weights: null
```

**Sources:** [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:4-41](), [olmoearth_run_data/mangrove/model.yaml:6-27]()

### OlmoEarth Encoder

The `rslearn.models.olmoearth_pretrain.model.OlmoEarth` is the pre-trained foundation model encoder.

| Parameter | Type | Description |
|-----------|------|-------------|
| `checkpoint_path` | str | Path to pre-trained checkpoint |
| `model_id` | str | Model identifier (e.g., "OLMOEARTH_V1_BASE") |
| `selector` | list[str] | Component to extract (e.g., ["encoder"]) |
| `patch_size` | int | Patch size for vision transformer (2 or 4) |
| `random_initialization` | bool | Use random weights instead of checkpoint |
| `embedding_size` | int | Embedding dimension (null for default) |
| `autocast_dtype` | str | Automatic mixed precision dtype (e.g., "bfloat16") |

**Sources:** [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:8-16](), [olmoearth_run_data/mangrove/model.yaml:10-13]()

### Decoder Layers

#### Upsample

The `rslearn.models.upsample.Upsample` layer increases spatial resolution.

```yaml
- class_path: rslearn.models.upsample.Upsample
  init_args:
    scale_factor: 4
    mode: bilinear
```

#### Conv

The `rslearn.models.conv.Conv` layer applies convolution operations.

```yaml
- class_path: rslearn.models.conv.Conv
  init_args:
    in_channels: 768
    out_channels: 8
    kernel_size: 1
    padding: same
    stride: 1
    activation:
      class_path: torch.nn.Identity
```

#### PickFeatures

The `rslearn.models.pick_features.PickFeatures` selects specific feature dimensions.

```yaml
- class_path: rslearn.models.pick_features.PickFeatures
  init_args:
    indexes: [0]
    collapse: true
```

**Sources:** [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:19-37]()

#### SegmentationPoolingDecoder

The `rslearn.models.pooling_decoder.SegmentationPoolingDecoder` uses pooling operations for segmentation.

```yaml
- class_path: rslearn.models.pooling_decoder.SegmentationPoolingDecoder
  init_args:
    in_channels: 768
    out_channels: 4
    num_conv_layers: 0
    num_fc_layers: 0
    conv_channels: 128
    fc_channels: 512
    image_key: "sentinel2_l2a"
```

**Sources:** [olmoearth_run_data/mangrove/model.yaml:16-24]()

## Task Components

### MultiTask

The `rslearn.train.tasks.multi_task.MultiTask` manages multiple task definitions and loss computation.

```yaml
task:
  class_path: rslearn.train.tasks.multi_task.MultiTask
  init_args:
    tasks:
      segment:
        class_path: rslearn.train.tasks.segmentation.SegmentationTask
    input_mapping:
      segment:
        label: "targets"
```

**Sources:** [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:69-209]()

### SegmentationTask

The `rslearn.train.tasks.segmentation.SegmentationTask` defines semantic segmentation training and evaluation.

```mermaid
graph TB
    subgraph "SegmentationTask Configuration"
        NumClasses["num_classes:<br/>Number of classes"]
        ZeroInvalid["zero_is_invalid:<br/>Ignore class 0"]
        Colors["colors:<br/>Visualization colors"]
        
        subgraph "Metrics"
            Accuracy["enable_accuracy_metric"]
            MIoU["enable_miou_metric"]
            F1["enable_f1_metric"]
            MetricKwargs["metric_kwargs:<br/>e.g. average='micro'"]
        end
        
        subgraph "Per-Class Metrics"
            OtherMetrics["other_metrics:<br/>Per-class precision/recall"]
        end
    end
    
    Predictions["Model Predictions"]
    Targets["Ground Truth Targets"]
    
    Predictions --> NumClasses
    Targets --> NumClasses
    
    NumClasses --> Accuracy
    NumClasses --> MIoU
    NumClasses --> F1
    
    MetricKwargs --> Accuracy
    MetricKwargs --> MIoU
    MetricKwargs --> F1
    
    OtherMetrics --> Accuracy
```

**Key Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `num_classes` | int | Number of classification classes |
| `zero_is_invalid` | bool | Treat class 0 as invalid/ignore |
| `colors` | list[list[int]] | RGB colors for each class |
| `enable_accuracy_metric` | bool | Compute overall accuracy |
| `enable_miou_metric` | bool | Compute mean IoU |
| `enable_f1_metric` | bool | Compute F1 score |
| `metric_kwargs` | dict | Kwargs for metrics (e.g., `average: "micro"`) |
| `other_metrics` | dict | Additional per-class metrics |
| `image_bands` | list[int] | Bands to use for visualization |

**Sources:** [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:73-206](), [olmoearth_run_data/mangrove/model.yaml:88-243]()

### SegmentationHead

The `rslearn.train.tasks.segmentation.SegmentationHead` is the final layer that produces class logits.

```yaml
- class_path: rslearn.train.tasks.segmentation.SegmentationHead
```

This component is typically the last layer in the decoder pipeline and converts feature maps to per-pixel class predictions.

**Sources:** [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:38](), [olmoearth_run_data/mangrove/model.yaml:25]()

### SegmentationMetric

The `rslearn.train.tasks.segmentation.SegmentationMetric` wraps torchmetrics for per-class evaluation.

```yaml
water_precision:
  class_path: rslearn.train.tasks.segmentation.SegmentationMetric
  init_args:
    metric:
      class_path: torchmetrics.classification.MulticlassPrecision
      init_args:
        num_classes: 8
        average: null
    class_idx: 1
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `metric` | torchmetrics.Metric | Underlying torchmetrics metric |
| `class_idx` | int | Class index to evaluate |
| `pass_probabilities` | bool | Pass probabilities instead of predictions |

**Sources:** [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:81-98](), [olmoearth_run_data/mangrove/model.yaml:149-178]()

## Transform Components

Transform components modify input data during training and inference. They are applied in sequence as defined in the `transforms` list.

```mermaid
graph LR
    Input["Raw Input<br/>sentinel2_l2a"]
    
    subgraph "Training Transforms"
        Pad1["rslearn.train.transforms.pad.Pad<br/>Add border padding"]
        Crop1["rslearn.train.transforms.crop.Crop<br/>Random crop"]
        Flip1["rslearn.train.transforms.flip.Flip<br/>Random flip"]
        Norm1["rslearn.models.olmoearth_pretrain.norm<br/>OlmoEarthNormalize"]
    end
    
    Output["Transformed Data"]
    
    Input --> Pad1
    Pad1 --> Crop1
    Crop1 --> Flip1
    Flip1 --> Norm1
    Norm1 --> Output
```

### Pad

The `rslearn.train.transforms.pad.Pad` adds border padding to images.

```yaml
- class_path: rslearn.train.transforms.pad.Pad
  init_args:
    size: 31
    mode: "center"
    image_selectors: ["sentinel2_l2a", "target/segment/classes", "target/segment/valid"]
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `size` | int | Padding size in pixels |
| `mode` | str | Padding mode: "center", "edge", etc. |
| `image_selectors` | list[str] | Images to apply padding to |
| `box_selectors` | list[str] | Bounding boxes to adjust |

**Sources:** [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:220-224](), [olmoearth_run_data/mangrove/model.yaml:261-269]()

### Crop

The `rslearn.train.transforms.crop.Crop` performs random or center cropping.

```yaml
- class_path: rslearn.train.transforms.crop.Crop
  init_args:
    crop_size: 16
    image_selectors: ["sentinel2_l2a", "target/segment/classes", "target/segment/valid"]
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `crop_size` | int | Size of cropped region |
| `image_selectors` | list[str] | Images to crop |

**Sources:** [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:225-228]()

### Flip

The `rslearn.train.transforms.flip.Flip` performs random horizontal/vertical flipping.

```yaml
- class_path: rslearn.train.transforms.flip.Flip
  init_args:
    image_selectors: ["sentinel2_l2a", "target/segment/classes", "target/segment/valid"]
```

**Sources:** [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:229-231]()

### OlmoEarthNormalize

The `rslearn.models.olmoearth_pretrain.norm.OlmoEarthNormalize` normalizes satellite imagery to match OlmoEarth pre-training statistics.

```yaml
- class_path: rslearn.models.olmoearth_pretrain.norm.OlmoEarthNormalize
  init_args:
    band_names:
      sentinel2_l2a: ["B02", "B03", "B04", "B08", "B05", "B06", "B07", "B8A", "B11", "B12", "B01", "B09"]
    std_multiplier: 2.0
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `band_names` | dict | Mapping of input keys to band name lists |
| `std_multiplier` | float | Standard deviation multiplier (default: 2.0) |

This transform applies per-band normalization using statistics from OlmoEarth pre-training. It is essential for proper model performance.

**Sources:** [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:214-217](), [olmoearth_run_data/mangrove/model.yaml:270-286]()

## Callback Components

Callbacks extend training behavior with additional functionality executed at specific points in the training loop.

### FreezeUnfreeze

The `rslearn.train.callbacks.freeze_unfreeze.FreezeUnfreeze` callback implements progressive unfreezing for transfer learning.

```yaml
- class_path: rslearn.train.callbacks.freeze_unfreeze.FreezeUnfreeze
  init_args:
    module_selector: ["model", "encoder", 0]
    unfreeze_at_epoch: 20
    unfreeze_lr_factor: 10
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `module_selector` | list[str] | Path to module to freeze/unfreeze |
| `unfreeze_at_epoch` | int | Epoch at which to unfreeze |
| `unfreeze_lr_factor` | float | Learning rate multiplier after unfreezing |

**Behavior:**
1. Initially freezes the encoder (typically pre-trained OlmoEarth)
2. Trains only decoder layers and task heads
3. At `unfreeze_at_epoch`, unfreezes encoder
4. Multiplies encoder learning rate by `unfreeze_lr_factor`

**Sources:** [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:261-265](), [olmoearth_run_data/mangrove/model.yaml:379-386]()

### RslearnWriter

The `rslearn.train.prediction_writer.RslearnWriter` saves inference predictions back to the dataset format.

```yaml
- class_path: rslearn.train.prediction_writer.RslearnWriter
  init_args:
    path: ${DATASET_PATH}
    output_layer: ${PREDICTION_OUTPUT_LAYER}
    selector: ["mangrove_classification"]
    merger: null
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `path` | str | Dataset path for output |
| `output_layer` | str | Layer name for predictions |
| `selector` | list[str] | Task outputs to write |
| `merger` | object | Optional merger for combining predictions |

**Sources:** [olmoearth_run_data/mangrove/model.yaml:356-361]()

### Standard Lightning Callbacks

The system also uses standard PyTorch Lightning callbacks:

#### ModelCheckpoint

```yaml
- class_path: lightning.pytorch.callbacks.ModelCheckpoint
  init_args:
    save_top_k: 1
    save_last: true
    monitor: val_segment/accuracy
    mode: max
```

Saves best and last checkpoints based on validation metrics.

#### LearningRateMonitor

```yaml
- class_path: lightning.pytorch.callbacks.LearningRateMonitor
  init_args:
    logging_interval: "epoch"
```

Logs learning rate changes to tracking systems (e.g., Weights & Biases).

**Sources:** [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:250-265](), [olmoearth_run_data/mangrove/model.yaml:362-377]()

## Scheduler Components

### PlateauScheduler

The `rslearn.train.scheduler.PlateauScheduler` reduces learning rate when validation metrics plateau.

```yaml
scheduler:
  class_path: rslearn.train.scheduler.PlateauScheduler
  init_args:
    factor: 0.2
    patience: 2
    min_lr: 0
    cooldown: 10
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `factor` | float | Learning rate reduction factor (new_lr = lr * factor) |
| `patience` | int | Number of epochs with no improvement before reduction |
| `min_lr` | float | Minimum learning rate threshold |
| `cooldown` | int | Number of epochs to wait before resuming monitoring |

**Alternative Configuration:**

The scheduler can also be configured via convenience parameters on `RslearnLightningModule`:

```yaml
model:
  init_args:
    plateau: true
    plateau_factor: 0.2
    plateau_patience: 2
    plateau_min_lr: 0.0
    plateau_cooldown: 10
```

**Sources:** [olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml:43-49](), [olmoearth_run_data/mangrove/model.yaml:36-40]()

## Data Source Components

### Planetary Computer Sentinel-2

While not directly part of rslearn, datasets often specify data sources using `rslearn.data_sources.planetary_computer.Sentinel2`:

```yaml
sentinel2:
  data_source:
    class_path: "rslearn.data_sources.planetary_computer.Sentinel2"
    duration: "366d"
    time_offset: "-180d"
    init_args:
      cache_dir: "cache/planetary_computer"
      harmonize: true
      sort_by: "eo:cloud_cover"
    query_config:
      max_matches: 12
      min_matches: 12
      period_duration: "30d"
      space_mode: "PER_PERIOD_MOSAIC"
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `duration` | str | Total time window (e.g., "366d") |
| `time_offset` | str | Offset from reference time (e.g., "-180d") |
| `harmonize` | bool | Apply cross-sensor harmonization |
| `sort_by` | str | Sort criterion (e.g., "eo:cloud_cover") |
| `max_matches` | int | Maximum images per period |
| `min_matches` | int | Minimum images required |
| `period_duration` | str | Duration of each time period |
| `space_mode` | str | Spatial aggregation mode (e.g., "PER_PERIOD_MOSAIC") |

**Sources:** [olmoearth_run_data/mangrove/dataset.json:37-52]()

## Component Instantiation Pattern

All rslearn components follow a consistent instantiation pattern using `class_path` and `init_args`:

```yaml
component_name:
  class_path: fully.qualified.ClassName
  init_args:
    parameter1: value1
    parameter2: value2
    nested_component:
      class_path: another.ClassName
      init_args:
        nested_param: value
```

This pattern enables:
1. **Configuration as code** - Complex object hierarchies defined in YAML
2. **Type safety** - PyTorch Lightning validates class paths exist
3. **Composability** - Components nest arbitrarily deep
4. **Extensibility** - New components integrate without code changes

The pattern is used consistently for models, tasks, transforms, callbacks, data sources, and all other configurable components.

**Sources:** All configuration files in [olmoearth_run_data/]()

---

# Page: Utility Scripts Reference

# Utility Scripts Reference

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [olmoearth_projects/projects/mozambique_lulc/__init__.py](olmoearth_projects/projects/mozambique_lulc/__init__.py)
- [olmoearth_projects/projects/mozambique_lulc/check_label_quality.py](olmoearth_projects/projects/mozambique_lulc/check_label_quality.py)
- [olmoearth_projects/projects/mozambique_lulc/create_label_raster.py](olmoearth_projects/projects/mozambique_lulc/create_label_raster.py)
- [olmoearth_projects/projects/mozambique_lulc/create_windows_for_lulc.py](olmoearth_projects/projects/mozambique_lulc/create_windows_for_lulc.py)
- [olmoearth_projects/projects/mozambique_lulc/update_train_test_split.py](olmoearth_projects/projects/mozambique_lulc/update_train_test_split.py)
- [olmoearth_projects/utils/label_quality/spatial_extent.py](olmoearth_projects/utils/label_quality/spatial_extent.py)
- [olmoearth_run_data/mozambique_lulc/prediction_request_geometry.geojson](olmoearth_run_data/mozambique_lulc/prediction_request_geometry.geojson)

</details>



This page documents the utility scripts used for data preparation, quality assessment, and dataset management in the olmoearth_projects repository. These scripts are primarily used during the data curation phase before model training, handling tasks such as window generation from geospatial data, train/validation split management, and label quality assessment.

For information about training configuration files, see [Training Configuration Files](#5.1). For details about the training process itself, see [Model Training](#5).

## Overview

The repository contains several utility scripts organized by project:

| Script | Purpose | Primary Use Case |
|--------|---------|------------------|
| `create_windows_for_lulc.py` | Generate training windows from GPKG files | Initial dataset creation from field survey data |
| `update_train_test_split.py` | Update train/val/test split assignments | Modifying split strategy after initial window creation |
| `check_label_quality.py` | Assess label quality metrics | Dataset quality validation before training |
| `create_label_raster.py` | Convert vector labels to raster format | Creating raster label layers for training |

**Sources:** [olmoearth_projects/projects/mozambique_lulc/create_windows_for_lulc.py:1-339](), [olmoearth_projects/projects/mozambique_lulc/update_train_test_split.py:1-86](), [olmoearth_projects/projects/mozambique_lulc/check_label_quality.py:1-51](), [olmoearth_projects/projects/mozambique_lulc/create_label_raster.py:1-110]()

## Data Preparation Workflow

The following diagram shows how these utility scripts fit into the data preparation pipeline:

**Diagram: Data Preparation Pipeline with Utility Scripts**

```mermaid
graph TB
    subgraph "Input Data"
        GPKG["GPKG Files<br/>gaza_train.gpkg<br/>manica_test.gpkg<br/>training_*.gpkg"]
    end
    
    subgraph "Window Creation"
        CREATE_WIN["create_windows_for_lulc.py<br/>--gpkg_dir<br/>--ds_path<br/>--window_size<br/>--crop_type"]
        CALC_BOUNDS["calculate_bounds()<br/>31-pixel buffer calculation"]
        CREATE_WINDOW["create_window()<br/>Window instantiation<br/>Label layer creation"]
    end
    
    subgraph "Split Management"
        SPLITTER["SpatialDataSplitter<br/>train_prop=0.9<br/>val_prop=0.1<br/>grid_size=32"]
        UPDATE_SPLIT["update_train_test_split.py<br/>--ds_path<br/>--splitter<br/>--workers"]
    end
    
    subgraph "Label Processing"
        CREATE_RASTER["create_label_raster.py<br/>Vector to raster conversion<br/>1x1 center pixel labeling"]
    end
    
    subgraph "Quality Assessment"
        CHECK_QUALITY["check_label_quality.py<br/>--ds_path<br/>--split<br/>--crop_type"]
        METRICS["Label Quality Metrics<br/>spatial_clustering<br/>label_imbalance<br/>spatial_extent"]
    end
    
    subgraph "Output"
        DATASET["rslearn Dataset<br/>Window objects<br/>label layer<br/>label_raster layer"]
    end
    
    GPKG --> CREATE_WIN
    CREATE_WIN --> CALC_BOUNDS
    CALC_BOUNDS --> CREATE_WINDOW
    CREATE_WINDOW --> SPLITTER
    SPLITTER --> DATASET
    
    DATASET --> UPDATE_SPLIT
    UPDATE_SPLIT --> DATASET
    
    DATASET --> CREATE_RASTER
    CREATE_RASTER --> DATASET
    
    DATASET --> CHECK_QUALITY
    CHECK_QUALITY --> METRICS
```

**Sources:** [olmoearth_projects/projects/mozambique_lulc/create_windows_for_lulc.py:1-339](), [olmoearth_projects/projects/mozambique_lulc/update_train_test_split.py:1-86](), [olmoearth_projects/projects/mozambique_lulc/check_label_quality.py:1-51](), [olmoearth_projects/projects/mozambique_lulc/create_label_raster.py:1-110]()

## create_windows_for_lulc.py

This script creates training windows from GPKG (GeoPackage) files containing point or polygon annotations with class labels. It generates `Window` objects in the rslearn dataset format, computing appropriate UTM projections and bounds for each annotation.

**Sources:** [olmoearth_projects/projects/mozambique_lulc/create_windows_for_lulc.py:1-339]()

### Command-Line Interface

```bash
python create_windows_for_lulc.py \
  --gpkg_dir /path/to/gpkg/files \
  --ds_path /path/to/output/dataset \
  --window_size 1 \
  --max_workers 32 \
  [--crop_type]
```

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `--gpkg_dir` | Yes | - | Directory containing `{province}_{split}.gpkg` files |
| `--ds_path` | Yes | - | Output dataset root path (supports local or cloud paths via UPath) |
| `--window_size` | No | 1 | Window size in pixels (each pixel = 10m at output resolution) |
| `--max_workers` | No | 32 | Number of worker processes for parallel window creation |
| `--crop_type` | No | False | Process crop type labels instead of LULC labels |

**Sources:** [olmoearth_projects/projects/mozambique_lulc/create_windows_for_lulc.py:268-298]()

### Input Data Requirements

The script expects GPKG files following specific naming conventions:

**For LULC classification:**
- `gaza_train.gpkg`, `gaza_test.gpkg`
- `manica_train.gpkg`, `manica_test.gpkg`
- `zambezia_train.gpkg`, `zambezia_test.gpkg`

Required columns: `class` (integer), `geometry`

**For crop type classification:**
- `training_gaza_zambezia_manica.gpkg`
- `test_gaza_zambezia_manica.gpkg`

Required columns: `crop1` (string), `geometry`

**Sources:** [olmoearth_projects/projects/mozambique_lulc/create_windows_for_lulc.py:110-145](), [olmoearth_projects/projects/mozambique_lulc/create_windows_for_lulc.py:299-314]()

### Class Mappings

The script uses predefined class mappings:

**LULC Classes:**

```python
CLASS_MAP = {
    0: "Water",
    1: "Bare Ground",
    2: "Rangeland",
    3: "Flooded Vegetation",
    4: "Trees",
    5: "Cropland",
    6: "Buildings",
}
```

**Crop Type Classes:**

```python
CROP_TYPE_MAP = {
    "corn": 0,
    "cassava": 1,
    "rice": 2,
    "sesame": 3,
    "beans": 4,
    "millet": 5,
    "sorghum": 6,
}
```

**Sources:** [olmoearth_projects/projects/mozambique_lulc/create_windows_for_lulc.py:29-50]()

### Temporal Coverage Configuration

Each province or group has defined temporal coverage for satellite data acquisition:

```python
GROUP_TIME = {
    "gaza": (datetime(2024, 10, 23, tzinfo=UTC), datetime(2025, 6, 20, tzinfo=UTC)),
    "manica": (datetime(2024, 10, 23, tzinfo=UTC), datetime(2025, 6, 20, tzinfo=UTC)),
    "zambezia": (datetime(2024, 10, 23, tzinfo=UTC), datetime(2025, 6, 20, tzinfo=UTC)),
    "crop_type": (datetime(2024, 10, 23, tzinfo=UTC), datetime(2025, 6, 20, tzinfo=UTC)),
}
```

These time ranges define the satellite imagery acquisition window stored in each `Window`'s `time_range` property.

**Sources:** [olmoearth_projects/projects/mozambique_lulc/create_windows_for_lulc.py:53-74]()

### Window Creation Process

**Diagram: Window Creation from GPKG Annotation**

```mermaid
graph LR
    subgraph "Input"
        POINT["GPKG Point/Polygon<br/>longitude, latitude<br/>class or crop1"]
    end
    
    subgraph "Coordinate Transformation"
        WGS84["WGS84 Point<br/>shapely.Point"]
        UTM["get_utm_ups_crs()<br/>Appropriate UTM zone"]
        PROJ["Projection<br/>resolution=10m<br/>y_resolution=-10m"]
        DST_GEOM["Projected Geometry<br/>STGeometry"]
    end
    
    subgraph "Bounds Calculation"
        CALC["calculate_bounds()<br/>window_size parameter<br/>centered on point"]
        BOUNDS["Bounds Tuple<br/>(x_min, y_min, x_max, y_max)"]
    end
    
    subgraph "Window Object"
        WINDOW["Window<br/>path, group, name<br/>projection, bounds<br/>time_range, options"]
        LABEL["Label Layer<br/>GeojsonVectorFormat<br/>category_id, category, fid"]
    end
    
    POINT --> WGS84
    WGS84 --> UTM
    UTM --> PROJ
    PROJ --> DST_GEOM
    DST_GEOM --> CALC
    CALC --> BOUNDS
    BOUNDS --> WINDOW
    WINDOW --> LABEL
```

The `calculate_bounds()` function computes window bounds centered on the annotation point:

- Even window sizes: `x_center ± window_size/2`
- Odd window sizes: `x_center ± (window_size/2 + adjustment)` to ensure proper centering

**Sources:** [olmoearth_projects/projects/mozambique_lulc/create_windows_for_lulc.py:77-108](), [olmoearth_projects/projects/mozambique_lulc/create_windows_for_lulc.py:147-216]()

### Window Metadata

Each created window includes metadata in the `options` dictionary:

```python
window.options = {
    "split": "train" or "val" or "test",
    "category_id": 0-6,  # integer class index
    "category": "Water",  # human-readable class name
    "fid": 12345,  # original feature ID from GPKG
    "source": "gpkg",
}
```

The `split` assignment for training data is determined by `SpatialDataSplitter` to ensure spatial separation between train/val splits.

**Sources:** [olmoearth_projects/projects/mozambique_lulc/create_windows_for_lulc.py:182-201]()

### Parallel Processing

The script uses multiprocessing for efficient window creation:

- Single-process mode (`--max_workers 1`): Sequential processing with `tqdm` progress bar
- Multi-process mode: Uses `multiprocessing.Pool` with `star_imap_unordered()` for parallel execution
- Forkserver start method ensures clean process initialization

**Sources:** [olmoearth_projects/projects/mozambique_lulc/create_windows_for_lulc.py:257-266](), [olmoearth_projects/projects/mozambique_lulc/create_windows_for_lulc.py:269]()

## update_train_test_split.py

This script updates the train/validation/test split assignments for existing windows in a dataset. It is used when you want to change the splitting strategy after initial window creation without regenerating the entire dataset.

**Sources:** [olmoearth_projects/projects/mozambique_lulc/update_train_test_split.py:1-86]()

### Command-Line Interface

```bash
python update_train_test_split.py \
  --ds_path /path/to/dataset \
  --workers 1 \
  --splitter spatial \
  [--crop_type]
```

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `--ds_path` | Yes | - | Path to the dataset |
| `--workers` | No | 1 | Number of worker processes |
| `--splitter` | No | spatial | Splitter type: `spatial` or `random` |
| `--crop_type` | No | False | Process crop_type group instead of province groups |

**Sources:** [olmoearth_projects/projects/mozambique_lulc/update_train_test_split.py:31-53]()

### Splitter Options

**SpatialDataSplitter:**

```python
SpatialDataSplitter(
    train_prop=0.9,
    val_prop=0.1,
    test_prop=0.0,
    grid_size=32
)
```

Ensures spatial separation between train/val splits using a 32-pixel grid. Samples in the same grid cell are assigned to the same split to prevent data leakage.

**RandomDataSplitter:**

```python
RandomDataSplitter(
    train_prop=0.9,
    val_prop=0.1,
    test_prop=0.0
)
```

Randomly assigns windows to splits without spatial considerations.

**Sources:** [olmoearth_projects/projects/mozambique_lulc/update_train_test_split.py:55-65]()

### Update Logic

The `update_train_val_split()` function only modifies windows with `split` in `["train", "val"]`:

```python
def update_train_val_split(window: Window, splitter: DataSplitterInterface) -> None:
    if window.options["split"] in ["train", "val"]:
        split = splitter.choose_split_for_window(window)
        print(f"Window was {window.options['split']}, changing to {split}")
        window.options["split"] = split
        window.save()
```

Test split windows are never modified, preserving the original test set.

**Sources:** [olmoearth_projects/projects/mozambique_lulc/update_train_test_split.py:22-28]()

## check_label_quality.py

This script assesses the quality of training labels using multiple metrics defined in the `utils.label_quality` module. It helps identify potential issues with label distribution, spatial coverage, and class imbalance before training.

**Sources:** [olmoearth_projects/projects/mozambique_lulc/check_label_quality.py:1-51]()

### Command-Line Interface

```bash
python check_label_quality.py \
  --ds_path /path/to/dataset \
  --split train \
  [--crop_type]
```

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `--ds_path` | Yes | - | Path to the dataset |
| `--split` | No | train | Split to assess: `train`, `val`, `test`, or `all` |
| `--crop_type` | No | False | Process crop_type group instead of province groups |

**Sources:** [olmoearth_projects/projects/mozambique_lulc/check_label_quality.py:12-28]()

### Data Loading

The script loads windows from the dataset and extracts label and geometry information:

```python
windows = dataset.load_windows(show_progress=True, groups=groups)
labels, geometry = [], []
for window in windows:
    split = window.options["split"]
    if split in splits_to_keep:
        labels.append(window.options["category"])
        geometry.append(window.get_geometry().to_projection(WGS84_PROJECTION).shp)

df = gpd.GeoDataFrame({"label": labels, "geometry": geometry})
```

The resulting `GeoDataFrame` is passed to `check_label_quality()` for analysis.

**Sources:** [olmoearth_projects/projects/mozambique_lulc/check_label_quality.py:35-50]()

### Label Quality Metrics

The `check_label_quality()` function (referenced but not shown in provided files) computes multiple quality metrics. Based on the utility functions provided, the following metric is implemented:

**Spatial Extent Metric:**

The `spatial_extent()` function calculates what fraction of the total labeled area each class occupies:

```python
def spatial_extent(df: gpd.GeoDataFrame) -> dict[str | int, float]:
    """How much of the total label spatial extent does each class occupy?
    
    For each class, values close to 1 are desirable.
    """
    total_area = relative_area(df.total_bounds)
    
    output_dict: dict[str | int, float] = {}
    for class_label in df.label.unique():
        label_area = relative_area(df[df.label == class_label].total_bounds)
        output_dict[class_label] = label_area / total_area
    
    return output_dict
```

The `relative_area()` function computes approximate area using spherical geometry:

```python
def relative_area(bounds: tuple[float, float, float, float]) -> float:
    """A = R^2 * (sin(f2)-sin(f1)) * (l2-l1) / 180"""
    min_lon, min_lat, max_lon, max_lat = bounds
    return (np.sin(np.radians(max_lat)) - np.sin(np.radians(min_lat))) * (
        max_lon - min_lon
    )
```

Values close to 1.0 indicate that a class is well-distributed spatially across the entire labeled region. Lower values suggest the class is concentrated in a small geographic area, which may lead to poor generalization.

**Sources:** [olmoearth_projects/utils/label_quality/spatial_extent.py:1-32]()

## create_label_raster.py

This script converts vector label layers to raster format, creating a `label_raster` layer with the class ID encoded in the center pixel of each window. This is used by training configurations that expect raster labels rather than vector labels.

**Sources:** [olmoearth_projects/projects/mozambique_lulc/create_label_raster.py:1-110]()

### Command-Line Interface

```bash
python create_label_raster.py \
  --ds_path /path/to/dataset \
  --workers 64 \
  [--crop_type]
```

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `--ds_path` | Yes | - | Path to the dataset |
| `--workers` | No | 64 | Number of worker processes |
| `--crop_type` | No | False | Process crop_type group instead of province groups |

**Sources:** [olmoearth_projects/projects/mozambique_lulc/create_label_raster.py:79-95]()

### Raster Creation Process

**Diagram: Vector to Raster Label Conversion**

```mermaid
graph TB
    subgraph "Input"
        LABEL_VEC["label Layer<br/>GeojsonVectorFormat<br/>category property"]
    end
    
    subgraph "Class Mapping"
        CLASS_NAME["Class Name String<br/>e.g., 'Water'"]
        LULC_NAMES["LULC_CLASS_NAMES<br/>8 classes"]
        CROP_NAMES["CROPTYPE_CLASS_NAMES<br/>8 crop types"]
        CLASS_ID["class_id<br/>Integer index"]
    end
    
    subgraph "Raster Generation"
        ZEROS["np.zeros()<br/>Shape: (1, height, width)<br/>dtype: uint8"]
        CENTER["Center Pixel<br/>raster[:, h//2, w//2] = class_id"]
        ENCODED["Raster Array<br/>Single band, class ID at center"]
    end
    
    subgraph "Output"
        LABEL_RASTER["label_raster Layer<br/>GeotiffRasterFormat<br/>band: 'label'"]
    end
    
    LABEL_VEC --> CLASS_NAME
    CLASS_NAME --> LULC_NAMES
    CLASS_NAME --> CROP_NAMES
    LULC_NAMES --> CLASS_ID
    CROP_NAMES --> CLASS_ID
    CLASS_ID --> ZEROS
    ZEROS --> CENTER
    CENTER --> ENCODED
    ENCODED --> LABEL_RASTER
```

**Sources:** [olmoearth_projects/projects/mozambique_lulc/create_label_raster.py:54-77]()

### Class Name Arrays

The script defines class name arrays for looking up class IDs:

```python
LULC_CLASS_NAMES = [
    "invalid",
    "Water",
    "Bare Ground",
    "Rangeland",
    "Flooded Vegetation",
    "Trees",
    "Cropland",
    "Buildings",
]

CROPTYPE_CLASS_NAMES = [
    "invalid",
    "corn",
    "cassava",
    "rice",
    "sesame",
    "beans",
    "millet",
    "sorghum",
]
```

The class ID is determined by finding the index of the class name in the appropriate array.

**Sources:** [olmoearth_projects/projects/mozambique_lulc/create_label_raster.py:30-49]()

### Dataset Configuration Update

After running this script, the dataset's `config.json` must be updated to include the new layer:

```json
{
  "label_raster": {
    "band_sets": [
      {
        "bands": ["label"],
        "dtype": "int32"
      }
    ],
    "type": "raster"
  }
}
```

This configuration enables the training system to load the raster labels.

**Sources:** [olmoearth_projects/projects/mozambique_lulc/create_label_raster.py:1-17]()

## Common Usage Patterns

### Complete Dataset Preparation Workflow

The following sequence is typically used to prepare a dataset from scratch:

```bash
# 1. Create windows from GPKG files
python create_windows_for_lulc.py \
  --gpkg_dir /data/raw/gpkg \
  --ds_path /data/datasets/mozambique_lulc \
  --window_size 1 \
  --max_workers 32

# 2. Check initial label quality
python check_label_quality.py \
  --ds_path /data/datasets/mozambique_lulc \
  --split all

# 3. (Optional) Update split strategy if needed
python update_train_test_split.py \
  --ds_path /data/datasets/mozambique_lulc \
  --workers 16 \
  --splitter spatial

# 4. Create raster labels if required by training config
python create_label_raster.py \
  --ds_path /data/datasets/mozambique_lulc \
  --workers 64

# 5. Final quality check on training split
python check_label_quality.py \
  --ds_path /data/datasets/mozambique_lulc \
  --split train
```

**Sources:** [olmoearth_projects/projects/mozambique_lulc/create_windows_for_lulc.py:268-339](), [olmoearth_projects/projects/mozambique_lulc/update_train_test_split.py:31-86](), [olmoearth_projects/projects/mozambique_lulc/check_label_quality.py:12-51](), [olmoearth_projects/projects/mozambique_lulc/create_label_raster.py:79-110]()

### Crop Type vs LULC Processing

The scripts support two distinct use cases controlled by the `--crop_type` flag:

| Aspect | LULC Mode | Crop Type Mode |
|--------|-----------|----------------|
| Groups | `["gaza", "manica", "zambezia"]` | `["crop_type"]` |
| Input Files | `{province}_{train\|test}.gpkg` | `training_*.gpkg`, `test_*.gpkg` |
| Class Column | `class` (integer) | `crop1` (string) |
| Number of Classes | 7 | 7 |
| Spatial Organization | Per-province | Combined provinces |

**Sources:** [olmoearth_projects/projects/mozambique_lulc/create_windows_for_lulc.py:296-314](), [olmoearth_projects/projects/mozambique_lulc/update_train_test_split.py:52-74](), [olmoearth_projects/projects/mozambique_lulc/check_label_quality.py:26-40]()

## Integration with rslearn Dataset Format

All utility scripts interact with rslearn's `Dataset` and `Window` classes:

**Diagram: rslearn Dataset Structure**

```mermaid
graph TB
    subgraph "Dataset Structure"
        DATASET["Dataset<br/>UPath root"]
        GROUPS["Groups<br/>gaza, manica, zambezia"]
        WINDOWS["Window objects<br/>group/window_name/"]
    end
    
    subgraph "Window Contents"
        WINDOW["Window<br/>config.json"]
        LAYERS["Layers"]
        LABEL["label/<br/>GeojsonVectorFormat"]
        LABEL_RASTER["label_raster/<br/>GeotiffRasterFormat"]
        OPTIONS["window.options<br/>split, category_id<br/>category, fid"]
    end
    
    subgraph "Data Splitters"
        SPATIAL["SpatialDataSplitter<br/>grid_size=32<br/>choose_split_for_window()"]
        RANDOM["RandomDataSplitter<br/>choose_split_for_window()"]
    end
    
    DATASET --> GROUPS
    GROUPS --> WINDOWS
    WINDOWS --> WINDOW
    WINDOW --> LAYERS
    WINDOW --> OPTIONS
    LAYERS --> LABEL
    LAYERS --> LABEL_RASTER
    
    SPATIAL --> OPTIONS
    RANDOM --> OPTIONS
```

**Sources:** [olmoearth_projects/projects/mozambique_lulc/create_windows_for_lulc.py:18-24](), [olmoearth_projects/projects/mozambique_lulc/update_train_test_split.py:6-19](), [olmoearth_projects/projects/mozambique_lulc/create_label_raster.py:24-28]()

## Multiprocessing Considerations

All scripts use Python's multiprocessing for parallel execution:

- **Start method:** `forkserver` is explicitly set for clean process initialization
- **Progress tracking:** `tqdm` progress bars work with both single-process and multi-process modes
- **Worker count:** Configurable via command-line arguments, typically 1-64 workers
- **Job distribution:** Uses `star_imap_unordered()` for efficient parallel mapping

```python
multiprocessing.set_start_method("forkserver", force=True)
p = multiprocessing.Pool(max_workers)
outputs = star_imap_unordered(p, function, jobs)
for _ in tqdm.tqdm(outputs, total=len(jobs)):
    pass
p.close()
```

**Sources:** [olmoearth_projects/projects/mozambique_lulc/create_windows_for_lulc.py:269](), [olmoearth_projects/projects/mozambique_lulc/update_train_test_split.py:32](), [olmoearth_projects/projects/mozambique_lulc/create_label_raster.py:80]()