<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/makani · page 7 Model Deployment and Packaging · fetched 2026-10-26 -->

# Model Deployment and Packaging

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [datasets/copernicus/get_data.py](datasets/copernicus/get_data.py)
- [makani/convert_legacy_to_flexible.py](makani/convert_legacy_to_flexible.py)
- [makani/models/model_package.py](makani/models/model_package.py)

</details>



This document covers the model deployment and packaging system in Makani, which provides functionality for creating self-contained, deployment-ready model packages. The system enables models trained in the Makani framework to be packaged with all necessary metadata, normalization data, and configuration files for inference in external frameworks, particularly earth2mip.

For information about the model registry and dynamic model loading, see [Model Registry System](#3.2). For details about the training and inference engines, see [Training and Inference Engines](#3.1).

## Model Package Structure

The Makani model packaging system creates self-contained packages that include all components necessary for inference. Each package follows a standardized directory structure that ensures compatibility with external frameworks.

```mermaid
graph TB
    subgraph "ModelPackage"
        CONFIG["config.json<br/>Complete parameter configuration"]
        CHECKPOINT["training_checkpoints/best_ckpt_mp0.tar<br/>Flexible checkpoint format"]
        METADATA["metadata.json<br/>earth2mip entrypoint specification"]
        NORM_DATA["Normalization Data<br/>means/stds/mins/maxs"]
        STATIC_DATA["Static Data<br/>orography.nc, land_mask.nc"]
    end
    
    subgraph "Package Interface"
        LOCAL_PKG["LocalPackage<br/>Package abstraction"]
        GET_METHOD["get(path)<br/>File path resolution"]
    end
    
    subgraph "Loading Functions"
        LOAD_MODEL["load_model_package()<br/>Returns ModelWrapper"]
        LOAD_TIMELOOP["load_time_loop()<br/>Returns earth2mip TimeLoop"]
    end
    
    LOCAL_PKG --> GET_METHOD
    GET_METHOD --> CONFIG
    GET_METHOD --> CHECKPOINT
    GET_METHOD --> METADATA
    GET_METHOD --> NORM_DATA
    GET_METHOD --> STATIC_DATA
    
    LOAD_MODEL --> LOCAL_PKG
    LOAD_TIMELOOP --> LOCAL_PKG
    
    LOAD_MODEL --> MODEL_WRAPPER["ModelWrapper<br/>Inference-ready model"]
    LOAD_TIMELOOP --> EARTH2MIP_TIMELOOP["earth2mip.networks.Inference<br/>TimeLoop object"]
```

The package structure includes these key components:

| Component | File Path | Description |
|-----------|-----------|-------------|
| Configuration | `config.json` | Complete parameter configuration from training |
| Model Weights | `training_checkpoints/best_ckpt_mp0.tar` | Flexible checkpoint format |
| Metadata | `metadata.json` | earth2mip entrypoint specification |
| Normalization | `global_means.npy`, `global_stds.npy` | Z-score normalization statistics |
| Min/Max Data | `mins.npy`, `maxs.npy` | Min-max normalization bounds |
| Static Data | `orography.nc`, `land_mask.nc` | Geographical data files |

Sources: [makani/models/model_package.py:50-56](), [makani/models/model_package.py:131-138]()

## ModelWrapper for Inference

The `ModelWrapper` class provides a simplified interface for model inference outside of the Makani training framework. It handles preprocessing steps like zenith angle calculation and provides a clean `forward()` method for predictions.

```mermaid
graph LR
    subgraph "ModelWrapper"
        WRAPPER_INIT["__init__(model, params)<br/>Initialize wrapper"]
        FORWARD["forward(x, time)<br/>Single prediction step"]
        MODEL_ATTR["model<br/>Wrapped ML model"]
        PARAMS_ATTR["params<br/>ParamsBase object"]
    end
    
    subgraph "Preprocessing"
        ZENITH_CHECK["add_zenith check<br/>params.add_zenith"]
        ZENITH_CALC["cos_zenith_angle()<br/>Calculate solar angle"]
        COORD_GRID["lat/lon grid generation<br/>meshgrid calculation"]
    end
    
    subgraph "Input Processing"
        INPUT_X["x<br/>Input tensor"]
        TIME_INPUT["time<br/>Timestamp"]
        ZENITH_TENSOR["z<br/>Zenith angle tensor"]
        CONCAT["torch.cat([x, z], dim=1)<br/>Channel concatenation"]
    end
    
    WRAPPER_INIT --> MODEL_ATTR
    WRAPPER_INIT --> PARAMS_ATTR
    
    FORWARD --> ZENITH_CHECK
    ZENITH_CHECK -->|"if add_zenith"| ZENITH_CALC
    ZENITH_CALC --> COORD_GRID
    COORD_GRID --> ZENITH_TENSOR
    
    INPUT_X --> CONCAT
    ZENITH_TENSOR --> CONCAT
    CONCAT --> MODEL_ATTR
    
    TIME_INPUT --> ZENITH_CALC
```

The wrapper performs these key operations:

- **Zenith Angle Integration**: Automatically adds solar zenith angle as an additional input channel when `add_zenith` is enabled
- **Coordinate Grid Management**: Maintains latitude/longitude grids for zenith angle calculations  
- **Device Handling**: Ensures tensors are on the correct device for computation
- **Dimension Broadcasting**: Handles tensor dimension matching for concatenation

Sources: [makani/models/model_package.py:58-97]()

## Package Creation and Management

The package creation system saves all necessary components for model deployment through the `save_model_package()` function. This function creates a complete, self-contained package from a trained model.

```mermaid
graph TB
    subgraph "save_model_package()"
        PARAMS_INPUT["params<br/>ParamsBase object"]
        CONFIG_SAVE["Save config.json<br/>Human-readable JSON"]
        STATIC_COPY["Copy static files<br/>orography, landmask"]
        NORM_COPY["Copy normalization data<br/>means, stds, mins, maxs"]
        METADATA_CREATE["Create metadata.json<br/>earth2mip entrypoint"]
    end
    
    subgraph "File Operations"
        JSON_BEAUTIFY["jsbeautifier<br/>Format JSON output"]
        SHUTIL_COPY["shutil.copy()<br/>File copying"]
        EXPERIMENT_DIR["params.experiment_dir<br/>Output directory"]
    end
    
    subgraph "Static Data Handling"
        OROGRAPHY_CHECK["add_orography check<br/>params.add_orography"]
        LANDMASK_CHECK["add_landmask check<br/>params.add_landmask"]
        NORM_CHECK["normalization mode<br/>zscore vs minmax"]
    end
    
    PARAMS_INPUT --> CONFIG_SAVE
    CONFIG_SAVE --> JSON_BEAUTIFY
    JSON_BEAUTIFY --> EXPERIMENT_DIR
    
    PARAMS_INPUT --> STATIC_COPY
    STATIC_COPY --> OROGRAPHY_CHECK
    STATIC_COPY --> LANDMASK_CHECK
    OROGRAPHY_CHECK --> SHUTIL_COPY
    LANDMASK_CHECK --> SHUTIL_COPY
    
    PARAMS_INPUT --> NORM_COPY
    NORM_COPY --> NORM_CHECK
    NORM_CHECK --> SHUTIL_COPY
    
    PARAMS_INPUT --> METADATA_CREATE
    METADATA_CREATE --> EXPERIMENT_DIR
```

The package creation process handles different normalization modes and optional static data:

| Component | Condition | Source Path | Target Path |
|-----------|-----------|-------------|-------------|
| Orography | `add_orography=True` | `params.orography_path` | `orography.nc` |
| Land Mask | `add_landmask=True` | `params.landmask_path` | `land_mask.nc` |
| Global Stats | `normalization='zscore'` | `global_means_path`, `global_stds_path` | `global_means.npy`, `global_stds.npy` |
| Min/Max | `normalization='minmax'` | `min_path`, `max_path` | `mins.npy`, `maxs.npy` |

Sources: [makani/models/model_package.py:99-138]()

## earth2mip Integration

The Makani packaging system provides seamless integration with the earth2mip framework through the `load_time_loop()` function, which creates earth2mip-compatible inference objects.

```mermaid
graph TB
    subgraph "earth2mip Integration"
        LOAD_TIMELOOP["load_time_loop()<br/>Entry point function"]
        PACKAGE_INPUT["package<br/>LocalPackage object"]
        DEVICE_PARAM["device<br/>Compute device"]
        TIMESTEP_PARAM["time_step_hours<br/>Temporal resolution"]
    end
    
    subgraph "Configuration Loading"
        CONFIG_LOAD["Load config.json<br/>ParamsBase.from_json()"]
        CHANNEL_EXTRACT["Extract channel names<br/>params.channel_names"]
        GRID_CREATE["Create equiangular grid<br/>equiangular_lat_lon_grid()"]
    end
    
    subgraph "Normalization Setup"
        NORM_MODE["Check normalization<br/>minmax vs zscore"]
        LOAD_STATS["Load normalization files<br/>numpy arrays"]
        CENTER_SCALE["Calculate center/scale<br/>For earth2mip format"]
    end
    
    subgraph "earth2mip Objects"
        MODEL_LOAD["load_model_package()<br/>Get ModelWrapper"]
        INFERENCE_CREATE["earth2mip.networks.Inference<br/>TimeLoop object"]
        FINAL_INFERENCE["Configured Inference<br/>Ready for deployment"]
    end
    
    LOAD_TIMELOOP --> PACKAGE_INPUT
    PACKAGE_INPUT --> CONFIG_LOAD
    CONFIG_LOAD --> CHANNEL_EXTRACT
    CONFIG_LOAD --> GRID_CREATE
    
    PACKAGE_INPUT --> NORM_MODE
    NORM_MODE --> LOAD_STATS
    LOAD_STATS --> CENTER_SCALE
    
    PACKAGE_INPUT --> MODEL_LOAD
    
    MODEL_LOAD --> INFERENCE_CREATE
    CHANNEL_EXTRACT --> INFERENCE_CREATE
    CENTER_SCALE --> INFERENCE_CREATE
    GRID_CREATE --> INFERENCE_CREATE
    
    INFERENCE_CREATE --> FINAL_INFERENCE
```

The earth2mip integration handles:

- **Grid Configuration**: Creates equiangular latitude-longitude grids compatible with earth2mip
- **Normalization Adaptation**: Converts Makani normalization to earth2mip format (center/scale)
- **Channel Mapping**: Maps model channels to earth2mip variable names
- **Time Step Configuration**: Sets temporal resolution for inference loops

Sources: [makani/models/model_package.py:199-268]()

## Checkpoint Format Conversion

The checkpoint conversion system transforms legacy distributed checkpoints into flexible single-file formats suitable for deployment. This is handled by the `convert_legacy_to_flexible.py` script.

```mermaid
graph LR
    subgraph "Legacy Format"
        LEGACY_DIR["Legacy checkpoint directory<br/>Multiple rank files"]
        LEGACY_CONFIG["config.json<br/>Original configuration"]
        RANK_FILES["best_ckpt_mp{rank}.tar<br/>Per-rank checkpoints"]
    end
    
    subgraph "Conversion Process"
        CHECKPOINT_SAVER["CheckpointSaver<br/>Extends Trainer class"]
        DIST_INIT["dist.init_process_group()<br/>Setup distributed environment"]
        LOAD_CHECKPOINT["restore_checkpoint()<br/>Load legacy format"]
        SAVE_FLEXIBLE["save_checkpoint()<br/>flexible mode"]
    end
    
    subgraph "Flexible Format"
        FLEXIBLE_CHECKPOINT["best_ckpt_mp0.tar<br/>Single consolidated file"]
        UPDATED_CONFIG["config.json<br/>Updated parameters"]
        PACKAGE_METADATA["metadata.json<br/>earth2mip compatibility"]
    end
    
    LEGACY_DIR --> CHECKPOINT_SAVER
    LEGACY_CONFIG --> CHECKPOINT_SAVER
    RANK_FILES --> LOAD_CHECKPOINT
    
    CHECKPOINT_SAVER --> DIST_INIT
    DIST_INIT --> LOAD_CHECKPOINT
    LOAD_CHECKPOINT --> SAVE_FLEXIBLE
    
    SAVE_FLEXIBLE --> FLEXIBLE_CHECKPOINT
    CHECKPOINT_SAVER --> UPDATED_CONFIG
    CHECKPOINT_SAVER --> PACKAGE_METADATA
```

The conversion process:

1. **Process Group Setup**: Initializes distributed environment matching original training configuration
2. **Legacy Loading**: Restores checkpoints using original distributed parameters
3. **Flexible Saving**: Consolidates model state into single checkpoint file
4. **Package Generation**: Creates complete model package with updated metadata

Key parameters updated during conversion:

| Parameter | Legacy Value | Flexible Value |
|-----------|--------------|----------------|
| `img_local_offset_x` | Distributed offset | `0` |
| `img_local_offset_y` | Distributed offset | `0` |
| `img_local_shape_x` | Local partition size | `params.img_shape_x` |
| `img_local_shape_y` | Local partition size | `params.img_shape_y` |

Sources: [makani/convert_legacy_to_flexible.py:41-103](), [makani/models/model_package.py:171-177]()

## Deployment Workflows

The model deployment system supports multiple deployment scenarios through standardized interfaces and package formats.

```mermaid
graph TB
    subgraph "Training Output"
        TRAINED_MODEL["Trained Model<br/>Distributed checkpoints"]
        TRAINING_CONFIG["Training Configuration<br/>YAML + derived params"]
        NORM_STATS["Normalization Statistics<br/>Data preprocessing"]
    end
    
    subgraph "Package Preparation"
        LEGACY_CHECK{"Legacy Format?"}
        CONVERT_SCRIPT["convert_legacy_to_flexible.py<br/>Format conversion"]
        PACKAGE_SAVE["save_model_package()<br/>Create deployment package"]
    end
    
    subgraph "Deployment Targets"
        EARTH2MIP["earth2mip Framework<br/>load_time_loop()"]
        MODULUS["NVIDIA Modulus<br/>Package interface"]
        STANDALONE["Standalone Inference<br/>load_model_package()"]
    end
    
    subgraph "Inference Interfaces"
        TIMELOOP["TimeLoop Interface<br/>earth2mip.networks.Inference"]
        MODEL_WRAPPER["ModelWrapper Interface<br/>Direct model calls"]
        PACKAGE_INTERFACE["Package Interface<br/>LocalPackage abstraction"]
    end
    
    TRAINED_MODEL --> LEGACY_CHECK
    TRAINING_CONFIG --> PACKAGE_SAVE
    NORM_STATS --> PACKAGE_SAVE
    
    LEGACY_CHECK -->|"Yes"| CONVERT_SCRIPT
    LEGACY_CHECK -->|"No"| PACKAGE_SAVE
    CONVERT_SCRIPT --> PACKAGE_SAVE
    
    PACKAGE_SAVE --> EARTH2MIP
    PACKAGE_SAVE --> MODULUS
    PACKAGE_SAVE --> STANDALONE
    
    EARTH2MIP --> TIMELOOP
    MODULUS --> PACKAGE_INTERFACE
    STANDALONE --> MODEL_WRAPPER
```

The deployment system provides these key benefits:

- **Format Standardization**: Consistent package structure across all deployment targets
- **Framework Compatibility**: Native integration with earth2mip and Modulus
- **Self-Contained Packages**: All dependencies included for reproducible inference
- **Legacy Support**: Conversion tools for existing model checkpoints

Sources: [makani/models/model_package.py:36-47](), [makani/convert_legacy_to_flexible.py:105-134]()

---

