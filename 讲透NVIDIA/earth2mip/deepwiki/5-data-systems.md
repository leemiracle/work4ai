<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/earth2mip · page 5 Data Systems · fetched 2026-10-26 -->

# Data Systems

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [earth2mip/grid.py](earth2mip/grid.py)
- [earth2mip/initial_conditions/__init__.py](earth2mip/initial_conditions/__init__.py)

</details>



The Data Systems component of Earth-2 MIP provides a unified interface for accessing meteorological data from multiple sources and transforming it into the formats required by AI weather models. This system handles initial condition data loading, spatial regridding, and caching to support both real-time and historical weather forecasting workflows.

This page covers the data access layer, grid management, and regridding capabilities. For information about how data flows into ensemble forecasting workflows, see [Ensemble Forecasting](#6.1). For details on specific model data requirements, see [Model Interface (TimeLoop)](#3.2).

## Architecture Overview

The data systems architecture follows a factory pattern that abstracts different meteorological data providers behind a common `DataSource` interface. This design enables models to work seamlessly with data from various sources without modification.

```mermaid
graph TB
    subgraph "Data Source Factory"
        GetDataSource["get_data_source()"]
        InitialConditionSource["schema.InitialConditionSource"]
    end
    
    subgraph "DataSource Implementations"
        CDSDataSource["cds.DataSource"]
        GFSDataSource["gfs.DataSource"] 
        IFSDataSource["ifs.DataSource"]
        HDF5DataSource["hdf5.DataSource"]
        HRMIPDataSource["hrmip.HDFPlSl"]
    end
    
    subgraph "Grid System"
        LatLonGrid["grid.LatLonGrid"]
        EquiangularGrid["equiangular_lat_lon_grid()"]
        GridEnum["schema.Grid"]
    end
    
    subgraph "Data Processing"
        GetDataFromSource["get_data_from_source()"]
        Regridder["regrid.get_regridder()"]
        GetInitialCondition["get_initial_condition_for_model()"]
    end
    
    GetDataSource --> InitialConditionSource
    InitialConditionSource --> CDSDataSource
    InitialConditionSource --> GFSDataSource
    InitialConditionSource --> IFSDataSource
    InitialConditionSource --> HDF5DataSource
    InitialConditionSource --> HRMIPDataSource
    
    CDSDataSource --> GetDataFromSource
    GFSDataSource --> GetDataFromSource
    IFSDataSource --> GetDataFromSource
    HDF5DataSource --> GetDataFromSource
    
    GridEnum --> LatLonGrid
    EquiangularGrid --> LatLonGrid
    LatLonGrid --> Regridder
    
    GetDataFromSource --> Regridder
    Regridder --> GetInitialCondition
```

**Data Source Factory Architecture**: This diagram shows how the `get_data_source()` factory function creates appropriate DataSource implementations based on the `InitialConditionSource` enum, and how data flows through the regridding system to produce model-ready tensors.

**Sources:** [earth2mip/initial_conditions/__init__.py:36-54](), [earth2mip/grid.py:24-58]()

## DataSource Interface and Factory

The core of the data system is the `DataSource` abstraction that provides a unified interface for accessing meteorological data. The factory function `get_data_source()` creates appropriate implementations based on the specified data source type.

### Factory Function

The `get_data_source()` function serves as the main entry point for creating data source instances:

```mermaid
flowchart TD
    Start["get_data_source(channel_names, initial_condition_source)"]
    ERA5Check{source == era5?}
    CDSCheck{source == cds?}
    GFSCheck{source == gfs?}
    IFSCheck{source == ifs?}
    HRMIPCheck{source == hrmip?}
    
    ERA5Return["hdf5.DataSource.from_path(config.ERA5_HDF5)"]
    CDSReturn["cds.DataSource(channel_names)"]
    GFSReturn["gfs.DataSource(channel_names)"]
    IFSReturn["ifs.DataSource(channel_names)"]
    HRMIPReturn["hrmip.HDFPlSl(config.ERA5_HDF5)"]
    NotImplemented["raise NotImplementedError"]
    
    Start --> ERA5Check
    ERA5Check -->|Yes| ERA5Return
    ERA5Check -->|No| CDSCheck
    CDSCheck -->|Yes| CDSReturn
    CDSCheck -->|No| GFSCheck
    GFSCheck -->|Yes| GFSReturn
    GFSCheck -->|No| IFSCheck
    IFSCheck -->|Yes| IFSReturn
    IFSCheck -->|No| HRMIPCheck
    HRMIPCheck -->|Yes| HRMIPReturn
    HRMIPCheck -->|No| NotImplemented
```

**DataSource Factory Logic**: Shows the decision tree implemented in `get_data_source()` for creating appropriate DataSource instances based on the `InitialConditionSource` enum value.

**Sources:** [earth2mip/initial_conditions/__init__.py:36-54]()

### Supported Data Sources

| Data Source | Implementation | Purpose | Configuration |
|------------|----------------|---------|---------------|
| `era5` | `hdf5.DataSource` | ERA5 reanalysis from local HDF5 files | `config.ERA5_HDF5` |
| `cds` | `cds.DataSource` | Climate Data Store API access | API credentials |
| `gfs` | `gfs.DataSource` | NOAA GFS operational forecasts | GRIB file access |
| `ifs` | `ifs.DataSource` | ECMWF IFS operational forecasts | S3 or local access |
| `hrmip` | `hrmip.HDFPlSl` | High-resolution model intercomparison | HDF5 specialized format |

**Sources:** [earth2mip/initial_conditions/__init__.py:24](), [earth2mip/initial_conditions/__init__.py:41-52]()

## Grid System

The grid system provides standardized spatial coordinate handling and regridding capabilities for transforming data between different model requirements.

### LatLonGrid Implementation

The `LatLonGrid` class represents regular latitude-longitude grids:

| Property | Type | Description |
|----------|------|-------------|
| `lat` | `List[float]` | Latitude coordinates (90° to -90°) |
| `lon` | `List[float]` | Longitude coordinates (0° to 360°) |
| `shape` | `tuple` | Grid dimensions (nlat, nlon) |

### Standard Grid Configurations

```mermaid
graph LR
    subgraph "Grid Enum Values"
        Grid720["schema.Grid.grid_720x1440"]
        Grid721["schema.Grid.grid_721x1440"] 
        S2SChallenge["schema.Grid.s2s_challenge"]
    end
    
    subgraph "Grid Generator"
        EquiangularFunc["equiangular_lat_lon_grid(nlat, nlon, includes_south_pole)"]
    end
    
    subgraph "Grid Instances"
        Grid720Instance["LatLonGrid(720x1440)<br/>No South Pole"]
        Grid721Instance["LatLonGrid(721x1440)<br/>With South Pole"]
        S2SInstance["LatLonGrid(181x360)<br/>With South Pole"]
    end
    
    Grid720 --> EquiangularFunc
    Grid721 --> EquiangularFunc
    S2SChallenge --> EquiangularFunc
    
    EquiangularFunc --> Grid720Instance
    EquiangularFunc --> Grid721Instance
    EquiangularFunc --> S2SInstance
```

**Standard Grid Configurations**: Shows how the `from_enum()` function maps grid enumeration values to specific `LatLonGrid` instances with different resolutions and pole handling.

**Sources:** [earth2mip/grid.py:35-46](), [earth2mip/grid.py:49-57]()

## Data Processing Pipeline

The data processing pipeline transforms raw meteorological data into model-ready tensors through a series of operations including time selection, channel selection, and spatial regridding.

### Data Retrieval and Processing

The `get_data_from_source()` function orchestrates the complete data processing pipeline:

```mermaid
sequenceDiagram
    participant Client
    participant GetDataFromSource as "get_data_from_source()"
    participant DataSource as "DataSource"
    participant Regridder as "regrid.get_regridder()"
    participant Torch as "torch.Tensor"
    
    Client->>GetDataFromSource: "time, channel_names, grid, n_history_levels"
    
    loop "for i in range(n_history_levels)"
        GetDataFromSource->>DataSource: "[time - i * time_step]"
        DataSource-->>GetDataFromSource: "numpy array (c, lat, lon)"
        Note over GetDataFromSource: "Validate array shape"
    end
    
    Note over GetDataFromSource: "Stack time levels: (time, c, lat, lon)"
    Note over GetDataFromSource: "Select channels by index"
    
    GetDataFromSource->>Regridder: "get_regridder(source_grid, target_grid)"
    Regridder-->>GetDataFromSource: "regridder instance"
    
    GetDataFromSource->>Torch: "torch.from_numpy(values)"
    Note over GetDataFromSource: "Add batch dimension [None]"
    GetDataFromSource->>Regridder: "regridder(tensor)"
    Regridder-->>GetDataFromSource: "regridded tensor"
    
    GetDataFromSource-->>Client: "torch.Tensor (1, time, c, lat, lon)"
```

**Data Processing Pipeline**: Shows the sequence of operations in `get_data_from_source()` from raw data retrieval through regridding to produce model-ready tensors.

**Sources:** [earth2mip/initial_conditions/__init__.py:57-103]()

### Model Integration

The `get_initial_condition_for_model()` function provides a simplified interface for models to obtain initial conditions:

| Parameter | Source | Description |
|-----------|--------|-------------|
| `channel_names` | `time_loop.in_channel_names` | Required atmospheric variables |
| `grid` | `time_loop.grid` | Target spatial grid |
| `n_history_levels` | `time_loop.n_history_levels` | Number of time steps needed |
| `time_step` | `time_loop.history_time_step` | Temporal spacing between levels |
| `device` | `time_loop.device` | Target compute device |
| `dtype` | `time_loop.dtype` | Tensor data type |

**Sources:** [earth2mip/initial_conditions/__init__.py:106-118]()

## Error Handling and Validation

The data systems include comprehensive validation to ensure data consistency:

- **Shape Validation**: Arrays must match expected dimensions `(len(channel_names), *grid.shape)` [earth2mip/initial_conditions/__init__.py:87-90]()
- **Channel Mapping**: Channel names are validated against data source capabilities [earth2mip/initial_conditions/__init__.py:95]()
- **Grid Compatibility**: Source and target grids must be compatible for regridding [earth2mip/initial_conditions/__init__.py:97]()
- **Device Transfer**: Automatic tensor device and dtype conversion [earth2mip/initial_conditions/__init__.py:98]()

**Sources:** [earth2mip/initial_conditions/__init__.py:82-103]()

---

