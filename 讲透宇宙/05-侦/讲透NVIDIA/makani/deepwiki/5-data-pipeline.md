<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/makani · page 5 Data Pipeline · fetched 2026-10-26 -->

# Data Pipeline

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [makani/utils/dataloader.py](makani/utils/dataloader.py)
- [makani/utils/dataloaders/__init__.py](makani/utils/dataloaders/__init__.py)

</details>



## Purpose and Scope

The Data Pipeline system in Makani provides a unified interface for loading and distributing climate and weather data across multiple GPUs and nodes for training and inference. This system abstracts the complexities of different data formats, distributed I/O patterns, and GPU-accelerated data loading to support the massive scale requirements of weather and climate ML models.

This page covers the high-level data pipeline architecture and the factory system that selects appropriate data loaders. For detailed documentation of specific data loader implementations, see [Data Loaders](#5.1). For information about data preprocessing and statistical computations, see [Data Processing and Statistics](#5.2).

## Data Pipeline Architecture

The data pipeline follows a factory pattern that automatically selects the appropriate data loader based on configuration parameters and integrates with Makani's distributed computing framework to enable scalable data loading across multiple processes.

```mermaid
graph TB
    subgraph "Entry_Points"
        TRAIN["makani.train"]
        INFERENCE["makani.inference"]
    end
    
    subgraph "Data_Pipeline_Factory"
        GET_DATALOADER["get_dataloader()"]
        INIT_DIST_IO["init_distributed_io()"]
    end
    
    subgraph "Data_Loader_Types"
        ZARR_LOADER["zarr_helper.get_data_loader()"]
        MULTIFILES_LOADER["MultifilesDataset"]
        DUMMY_LOADER["DummyLoader"]
        DALI_LOADER["ERA5DaliESDataloader2D"]
    end
    
    subgraph "Data_Sources"
        HDF5_FILES["HDF5 Climate Data"]
        ZARR_FILES["Zarr Arrays"]
        SYNTHETIC_DATA["Synthetic Data"]
        NETCDF_FILES["NetCDF Files"]
    end
    
    subgraph "Distributed_Computing"
        COMM_SYSTEM["comm system"]
        SPATIAL_GROUPS["spatial process groups"]
        DATA_GROUPS["data process groups"]
    end
    
    TRAIN --> GET_DATALOADER
    INFERENCE --> GET_DATALOADER
    
    GET_DATALOADER --> INIT_DIST_IO
    
    INIT_DIST_IO --> COMM_SYSTEM
    COMM_SYSTEM --> SPATIAL_GROUPS
    COMM_SYSTEM --> DATA_GROUPS
    
    GET_DATALOADER --> ZARR_LOADER
    GET_DATALOADER --> MULTIFILES_LOADER
    GET_DATALOADER --> DUMMY_LOADER
    GET_DATALOADER --> DALI_LOADER
    
    ZARR_LOADER --> ZARR_FILES
    MULTIFILES_LOADER --> HDF5_FILES
    DUMMY_LOADER --> SYNTHETIC_DATA
    DALI_LOADER --> HDF5_FILES
    DALI_LOADER --> NETCDF_FILES
```

Sources: [makani/utils/dataloader.py:1-152]()

## Data Loader Factory System

The `get_dataloader` function serves as the central factory that determines which data loading implementation to use based on configuration parameters. The selection logic follows a priority-based approach:

```mermaid
flowchart TD
    START["get_dataloader(params, files_pattern, device, train, final_eval)"]
    
    INIT_IO["init_distributed_io(params)"]
    
    CHECK_ZARR{"params.data_type == 'zarr'"}
    CHECK_MULTIFILES{"params.multifiles == True"}
    CHECK_SYNTHETIC{"params.enable_synthetic_data == True"}
    
    ZARR_PATH["zarr_helper.get_data_loader()"]
    MULTIFILES_PATH["MultifilesDataset + DistributedSampler"]
    DUMMY_PATH["DummyLoader"]
    DALI_PATH["ERA5DaliESDataloader2D"]
    
    BENCHY_CHECK{"params.enable_benchy && train"}
    BENCHY_WRAP["BenchmarkGenericIteratorWrapper"]
    
    RETURN_TRAIN{"train == True"}
    RETURN_TRAIN_RESULT["return dataloader, dataset, sampler"]
    RETURN_EVAL_RESULT["return dataloader, dataset"]
    
    START --> INIT_IO
    INIT_IO --> CHECK_ZARR
    
    CHECK_ZARR -->|Yes| ZARR_PATH
    CHECK_ZARR -->|No| CHECK_MULTIFILES
    
    CHECK_MULTIFILES -->|Yes| MULTIFILES_PATH
    CHECK_MULTIFILES -->|No| CHECK_SYNTHETIC
    
    CHECK_SYNTHETIC -->|Yes| DUMMY_PATH
    CHECK_SYNTHETIC -->|No| DALI_PATH
    
    DALI_PATH --> BENCHY_CHECK
    BENCHY_CHECK -->|Yes| BENCHY_WRAP
    BENCHY_CHECK -->|No| RETURN_TRAIN
    BENCHY_WRAP --> RETURN_TRAIN
    
    ZARR_PATH --> RETURN_TRAIN
    MULTIFILES_PATH --> RETURN_TRAIN
    DUMMY_PATH --> RETURN_TRAIN
    
    RETURN_TRAIN -->|Yes| RETURN_TRAIN_RESULT
    RETURN_TRAIN -->|No| RETURN_EVAL_RESULT
```

Sources: [makani/utils/dataloader.py:63-152]()

## Distributed I/O Initialization

The `init_distributed_io` function configures the data sharding and spatial distribution parameters required for distributed data loading. This function integrates with Makani's communication framework to determine how data should be partitioned across processes.

| Parameter | Description | Source |
|-----------|-------------|---------|
| `data_num_shards` | Number of data parallel shards | `comm.get_size("data")` |
| `data_shard_id` | Current process's data shard ID | `comm.get_rank("data")` |
| `io_grid` | 3D grid layout for I/O processes | `[1, comm.get_size("h"), comm.get_size("w")]` |
| `io_rank` | Current process's position in I/O grid | `[0, comm.get_rank("h"), comm.get_rank("w")]` |

The I/O grid configuration ensures that spatial dimensions are properly distributed across processes while maintaining data consistency. The system enforces constraints that the number of I/O ranks must either be 1 (no spatial parallelism) or equal to the spatial process group size.

```mermaid
graph LR
    subgraph "Process_Groups"
        DATA_GROUP["data process group"]
        SPATIAL_GROUP["spatial process group"]
        H_GROUP["h process group"]
        W_GROUP["w process group"]
    end
    
    subgraph "IO_Configuration"
        DATA_SHARDS["data_num_shards"]
        DATA_SHARD_ID["data_shard_id"]
        IO_GRID["io_grid[batch, h, w]"]
        IO_RANK["io_rank[0, h_rank, w_rank]"]
    end
    
    subgraph "Constraints"
        CONSTRAINT1["num_io_ranks == 1 OR num_io_ranks == spatial_size"]
        CONSTRAINT2["io_grid[1] == h_size OR io_grid[1] == 1"]
        CONSTRAINT3["io_grid[2] == w_size OR io_grid[2] == 1"]
    end
    
    DATA_GROUP --> DATA_SHARDS
    DATA_GROUP --> DATA_SHARD_ID
    
    H_GROUP --> IO_GRID
    W_GROUP --> IO_GRID
    H_GROUP --> IO_RANK
    W_GROUP --> IO_RANK
    
    SPATIAL_GROUP --> CONSTRAINT1
    H_GROUP --> CONSTRAINT2
    W_GROUP --> CONSTRAINT3
```

Sources: [makani/utils/dataloader.py:27-61]()

## Data Loader Types

The data pipeline supports four distinct data loader implementations, each optimized for different data formats and use cases:

| Data Loader | Configuration Trigger | Primary Use Case | Data Formats |
|-------------|----------------------|------------------|--------------|
| **Zarr Loader** | `params.data_type == "zarr"` | Cloud-optimized chunked arrays | Zarr |
| **Multifiles Loader** | `params.multifiles == True` | Distributed HDF5 files | HDF5, NetCDF |
| **Dummy Loader** | `params.enable_synthetic_data == True` | Testing and benchmarking | Synthetic data |
| **DALI Loader** | Default (none of above) | GPU-accelerated production workloads | HDF5, NetCDF |

### Common Interface

All data loaders provide a consistent interface with the following attributes:

- `in_channels` / `out_channels`: Number of input/output channels
- `grid_converter`: Spatial grid conversion utilities  
- `img_shape_x` / `img_shape_y`: Global image dimensions
- `img_crop_shape_x` / `img_crop_shape_y`: Cropped region dimensions
- `img_local_shape_x` / `img_local_shape_y`: Local process dimensions
- `get_input_normalization()` / `get_output_normalization()`: Normalization parameters

Sources: [makani/utils/dataloader.py:66-151]()

## Integration with Benchy

For performance benchmarking during training, the data pipeline can optionally wrap the DALI data loader with `BenchmarkGenericIteratorWrapper` when `params.enable_benchy` is enabled. This provides detailed timing and throughput metrics for the data loading pipeline.

Sources: [makani/utils/dataloader.py:140-143]()

---

