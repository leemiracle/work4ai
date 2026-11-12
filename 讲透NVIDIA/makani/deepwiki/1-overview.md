<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/makani · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/tests.yml](.github/workflows/tests.yml)
- [README.md](README.md)
- [pyproject.toml](pyproject.toml)

</details>



This document provides a high-level architectural overview of the Makani system, a PyTorch-based library designed for massively parallel training of machine learning weather and climate models. This overview covers the system's core execution engines, model registry, data pipeline, and distributed computing framework.

For detailed information about specific model architectures, see [Neural Network Models](#4). For configuration management details, see [Configuration System](#6). For data processing workflows, see [Data Pipeline](#5).

## Purpose and Scope

Makani is an experimental research library that enables training and inference of machine learning based weather and climate models on 100+ GPUs. The system supports various neural operator architectures including Spherical Fourier Neural Operators (SFNO) and Adaptive Fourier Neural Operators (AFNO), with comprehensive support for model parallelism, data parallelism, and distributed computing.

The system provides two main execution modes through CLI entry points: `makani.train` for distributed training and `makani.inference` for model evaluation and prediction.

Sources: [README.md:1-27](), [pyproject.toml:36-36]()

## System Architecture Overview

The following diagram illustrates the high-level architecture of Makani, showing the relationships between major system components and their corresponding code entities:

```mermaid
graph TB
    subgraph "CLI_Entry_Points"
        makani_train["makani.train"]
        makani_inference["makani.inference"]
    end
    
    subgraph "Core_Engines"
        trainer_py["trainer.py"]
        inferencer["inference/*"]
    end
    
    subgraph "Model_Registry"
        get_model["networks/models.py:get_model"]
        entry_points["pyproject.toml:entry-points"]
        sfnonet["networks/sfnonet.py"]
        afnonet["networks/afnonet.py"]
        vit["networks/vit.py"]
    end
    
    subgraph "Data_System"
        get_dataloader["utils/dataloader.py:get_dataloader"]
        dali_loader["utils/dataloaders/dali.py"]
        multifiles_loader["utils/dataloaders/multifiles.py"]
        zarr_loader["utils/dataloaders/zarr.py"]
    end
    
    subgraph "Distributed_Computing"
        comm_py["utils/comm.py"]
        mpu["mpu/*"]
        init_dist["utils/comm.py:init"]
    end
    
    subgraph "Configuration"
        yaml_configs["config/*.yaml"]
        sfnonet_yaml["config/sfnonet.yaml"]
        afnonet_yaml["config/afnonet.yaml"]
    end
    
    makani_train --> trainer_py
    makani_inference --> inferencer
    
    trainer_py --> get_model
    inferencer --> get_model
    
    get_model --> entry_points
    entry_points --> sfnonet
    entry_points --> afnonet
    entry_points --> vit
    
    trainer_py --> get_dataloader
    inferencer --> get_dataloader
    
    get_dataloader --> dali_loader
    get_dataloader --> multifiles_loader
    get_dataloader --> zarr_loader
    
    trainer_py --> comm_py
    inferencer --> comm_py
    comm_py --> mpu
    comm_py --> init_dist
    
    trainer_py --> yaml_configs
    inferencer --> yaml_configs
    yaml_configs --> sfnonet_yaml
    yaml_configs --> afnonet_yaml
```

Sources: [README.md:98-99](), [README.md:83-96](), [pyproject.toml:106-115]()

## Core Execution Engines

Makani provides two primary execution engines accessible through CLI commands:

### Training Engine
The training engine is launched via `makani.train` and implemented in `trainer.py`. It handles distributed training orchestration, model checkpointing, and performance optimization features including:

| Feature | CLI Argument | Implementation |
|---------|--------------|----------------|
| Automatic Mixed Precision | `--amp_mode` | `none`, `fp16`, `bf16` |
| JIT Compilation | `--jit_mode` | `none`, `script`, `inductor` |
| CUDA Graphs | `--cuda_graph_mode` | `none`, `fwdbwd`, `step` |
| Activation Checkpointing | `--checkpointing_level` | 0,1,2,3 |

### Inference Engine
The inference engine is accessed via `makani.inference` and implemented in the `inference/` directory. It supports the same distributed computing features as training and handles model evaluation on out-of-sample datasets.

```mermaid
graph LR
    subgraph "Training_Flow"
        train_cli["makani.train"]
        trainer_main["trainer.py:main"]
        train_loop["trainer.py:train"]
    end
    
    subgraph "Inference_Flow"
        infer_cli["makani.inference"]
        inferencer_main["inference/inferencer.py"]
        infer_loop["inference/inferencer.py:predict"]
    end
    
    subgraph "Shared_Components"
        model_registry["networks/models.py"]
        data_factory["utils/dataloader.py"]
        comm_init["utils/comm.py:init"]
    end
    
    train_cli --> trainer_main
    trainer_main --> train_loop
    
    infer_cli --> inferencer_main
    inferencer_main --> infer_loop
    
    train_loop --> model_registry
    infer_loop --> model_registry
    
    train_loop --> data_factory
    infer_loop --> data_factory
    
    trainer_main --> comm_init
    inferencer_main --> comm_init
```

Sources: [README.md:31-35](), [README.md:61-65](), [README.md:39-50](), [README.md:95-96]()

## Model Registry and Entry Points

Makani implements a dynamic model loading system through Python entry points and a centralized model registry. The system supports plugin-style model registration for both internal Makani models and external framework integration.

### Entry Points Configuration
The model registry uses Python entry points defined in `pyproject.toml` to enable dynamic model discovery:

| Entry Point Group | Models | Purpose |
|-------------------|---------|---------|
| `makani.models` | AFNOv1, AFNO, FNO, SFNO, DebugNet, ViT | Internal Makani models |
| `modulus.models` | SFNO | Integration with NVIDIA Modulus framework |

### Model Resolution Flow
```mermaid
graph TD
    subgraph "Model_Request"
        yaml_config["config/*.yaml:nettype"]
        cli_config["--config parameter"]
    end
    
    subgraph "Registry_Resolution"
        get_model_func["networks/models.py:get_model"]
        entry_point_lookup["pkg_resources.iter_entry_points"]
        model_class_import["Dynamic import"]
    end
    
    subgraph "Model_Implementations"
        sfno_class["sfnonet.py:SphericalFourierNeuralOperatorNet"]
        afno_class["afnonet.py:AdaptiveFourierNeuralOperatorNet"]
        vit_class["vit.py:VisionTransformer"]
        debug_class["debug.py:DebugNet"]
    end
    
    yaml_config --> get_model_func
    cli_config --> get_model_func
    
    get_model_func --> entry_point_lookup
    entry_point_lookup --> model_class_import
    
    model_class_import --> sfno_class
    model_class_import --> afno_class
    model_class_import --> vit_class
    model_class_import --> debug_class
```

Sources: [pyproject.toml:106-115](), [README.md:105-105](), [README.md:109-109]()

## Data Pipeline Architecture

The data pipeline supports multiple data formats and distributed loading strategies through a factory pattern implemented in `get_dataloader`. The system handles HDF5, Zarr, and synthetic data sources with GPU-accelerated loading capabilities.

### DataLoader Factory System
```mermaid
graph TB
    subgraph "Data_Sources"
        hdf5_data["HDF5 Files"]
        zarr_data["Zarr Arrays"]
        synthetic["Synthetic Data"]
    end
    
    subgraph "DataLoader_Factory"
        get_dataloader_func["utils/dataloader.py:get_dataloader"]
        loader_selection["Loader type resolution"]
    end
    
    subgraph "Loader_Implementations"
        dali_impl["dataloaders/dali.py:DaliDataLoader"]
        multifiles_impl["dataloaders/multifiles.py:MultifilesDataLoader"]
        zarr_impl["dataloaders/zarr.py:ZarrDataLoader"]
        dummy_impl["dataloaders/dummy.py:DummyDataLoader"]
    end
    
    subgraph "Distributed_IO"
        io_grid["I/O process grid"]
        spatial_sharding["Spatial data sharding"]
        rank_assignment["Process rank assignment"]
    end
    
    hdf5_data --> get_dataloader_func
    zarr_data --> get_dataloader_func
    synthetic --> get_dataloader_func
    
    get_dataloader_func --> loader_selection
    
    loader_selection --> dali_impl
    loader_selection --> multifiles_impl
    loader_selection --> zarr_impl
    loader_selection --> dummy_impl
    
    dali_impl --> io_grid
    multifiles_impl --> io_grid
    zarr_impl --> spatial_sharding
    
    io_grid --> rank_assignment
    spatial_sharding --> rank_assignment
```

### Data Format Support
The system expects training data in specific formats with accompanying metadata:

- **HDF5 Format**: Annual files with `inp` and `tar` variables for time-series prediction
- **Metadata**: `data.json` files describing dataset structure, channels, and grid coordinates
- **Grid Types**: Support for `equiangular` and `legendre-gauss` coordinate systems

Sources: [README.md:88-89](), [README.md:127-149]()

## Distributed Computing Framework

Makani implements multi-dimensional parallelization through an orthogonal communicator infrastructure managed by `comm.py`. The system supports data parallelism, spatial model parallelism, and channel parallelism.

### Communication Infrastructure
```mermaid
graph TB
    subgraph "Process_Groups"
        world_group["World communicator"]
        model_group["Model parallel group"]
        data_group["Data parallel group"]
        spatial_group["Spatial parallel group"]
    end
    
    subgraph "Parallelism_Strategies"
        data_parallel["Data Parallelism<br/>--batch_size"]
        spatial_parallel["Spatial Parallelism<br/>--h_parallel_size --w_parallel_size"]
        channel_parallel["Channel Parallelism<br/>--fin_parallel_size --fout_parallel_size"]
    end
    
    subgraph "Communication_Ops"
        allreduce["AllReduce operations"]
        allgather["AllGather operations"]
        scatter_gather["Scatter/Gather operations"]
    end
    
    subgraph "MPU_Utils"
        mpu_init["mpu/initialize.py"]
        mpu_utils["mpu/utils.py"]
        mpu_mapping["mpu/mappings.py"]
    end
    
    world_group --> model_group
    world_group --> data_group
    world_group --> spatial_group
    
    data_parallel --> data_group
    spatial_parallel --> spatial_group
    channel_parallel --> model_group
    
    model_group --> allreduce
    data_group --> allgather
    spatial_group --> scatter_gather
    
    allreduce --> mpu_init
    allgather --> mpu_utils
    scatter_gather --> mpu_mapping
```

### Parallelization Configuration
The system supports flexible parallelization strategies configurable via CLI arguments:

| Parallelism Type | CLI Arguments | Purpose |
|------------------|---------------|---------|
| Data Parallelism | `--batch_size` | Distribute batches across processes |
| Spatial Parallelism | `--h_parallel_size`, `--w_parallel_size` | Split spatial dimensions |
| Channel Parallelism | `--fin_parallel_size`, `--fout_parallel_size` | Split feature channels |

Sources: [README.md:92-92](), [README.md:47-50](), [README.md:84-84]()

## Configuration Management

The system uses YAML-based configuration files located in the `config/` directory to specify model architectures, training parameters, and dataset configurations. Each configuration file contains complete specifications for reproducible training runs.

### Configuration Structure
Key configuration parameters include:

| Parameter | Description | Location |
|-----------|-------------|----------|
| `nettype` | Model architecture selection | Maps to entry points |
| `train_data_path` | Training dataset location | File system path |
| `metadata_json_path` | Dataset metadata file | `data.json` file |
| `channel_names` | Input/output channels | Dataset-specific |

The configuration system integrates with the model registry to dynamically load appropriate model classes based on the `nettype` parameter.

Sources: [README.md:104-123](), [README.md:78-78]()

---

