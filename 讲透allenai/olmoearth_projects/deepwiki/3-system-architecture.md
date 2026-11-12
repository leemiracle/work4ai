<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/olmoearth_projects · page 3 System Architecture · fetched 2026-10-26 -->

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

