<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/rslearn · page 5 Dataset Management · fetched 2026-10-26 -->

# Dataset Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [rslearn/data_sources/raster_source.py](rslearn/data_sources/raster_source.py)
- [rslearn/dataset/manage.py](rslearn/dataset/manage.py)
- [rslearn/dataset/materialize.py](rslearn/dataset/materialize.py)
- [rslearn/main.py](rslearn/main.py)

</details>



This document covers the comprehensive dataset management system in rslearn, which handles the creation, preparation, ingestion, and materialization of remote sensing datasets. The system enables users to define spatial-temporal windows of interest and systematically process data from various remote sensing sources into training-ready formats.

For information about configuring data sources and their connection parameters, see [Data Sources](#4). For details about the underlying data storage formats and tile stores, see [Data Processing and Storage](#6).

## Overview

The dataset management system operates through a four-stage pipeline that transforms raw remote sensing data into structured, window-based datasets suitable for machine learning applications. Each stage is implemented as a separate CLI command and can be executed independently or as part of a complete workflow.

### Dataset Management Workflow

```mermaid
graph TD
    User["User"] --> CLI["rslearn CLI"]
    
    CLI --> AddWindows["add_windows"]
    CLI --> Prepare["prepare"] 
    CLI --> Ingest["ingest"]
    CLI --> Materialize["materialize"]
    
    AddWindows --> WindowsCreated["Windows Created<br/>in Dataset"]
    WindowsCreated --> Prepare
    
    Prepare --> PrepareHandler["PrepareHandler.__call__()"]
    PrepareHandler --> DataSources["Data Sources<br/>get_items()"]
    DataSources --> WindowLayerData["WindowLayerData<br/>saved to windows"]
    
    WindowLayerData --> Ingest
    Ingest --> IngestHandler["IngestHandler.__call__()"]
    IngestHandler --> TileStore["TileStore<br/>Raw tiles stored"]
    
    TileStore --> Materialize
    Materialize --> MaterializeHandler["MaterializeHandler.__call__()"]
    MaterializeHandler --> Materializers["RasterMaterializer/<br/>VectorMaterializer"]
    Materializers --> FinalDataset["Final Dataset<br/>Ready for ML Training"]
```

Sources: [rslearn/main.py:76-234](), [rslearn/main.py:419-460](), [rslearn/main.py:612-653](), [rslearn/main.py:697-740]()

## Window Management

### Creating Windows

Windows define the spatial and temporal extents for data processing. The `add_windows` command creates these windows based on bounding boxes or vector files.

| Parameter | Purpose | Example |
|-----------|---------|---------|
| `--box` | Define extent by coordinates | `--box -122.5,37.7,-122.4,37.8` |
| `--fname` | Define extents from vector file | `--fname regions.geojson` |
| `--crs` | Output coordinate system | `--crs EPSG:4326` |
| `--resolution` | Spatial resolution | `--resolution 10` |
| `--grid_size` | Create grid of windows | `--grid_size 1000` |
| `--window_size` | Fixed window size | `--window_size 512` |
| `--utm` | Use appropriate UTM projection | `--utm` |

### Window Creation Implementation

```mermaid
graph TD
    AddWindowsCmd["add_windows command"] --> ParseArgs["Parse CLI arguments"]
    ParseArgs --> CheckInput{"Box or File?"}
    
    CheckInput -->|Box| AddWindowsFromBox["add_windows_from_box()"]
    CheckInput -->|File| AddWindowsFromFile["add_windows_from_file()"]
    
    AddWindowsFromBox --> CreateWindows["Create Window objects"]
    AddWindowsFromFile --> CreateWindows
    
    CreateWindows --> SaveToDataset["Save to Dataset"]
    SaveToDataset --> WindowObjects["Window objects<br/>with projection<br/>and bounds"]
```

Sources: [rslearn/main.py:76-234](), [rslearn/dataset/add_windows.py]()

## Data Preparation

The preparation stage identifies which data items from configured data sources are needed for each window. This creates a mapping between windows and the specific remote sensing products required.

### Preparation Process

```mermaid
graph TD
    PrepareCommand["rslearn dataset prepare"] --> PrepareHandler["PrepareHandler"]
    PrepareHandler --> ApplyOnWindows["apply_on_windows()"]
    
    ApplyOnWindows --> LoadWindows["dataset.load_windows()"]
    LoadWindows --> WindowBatches["Window batches"]
    
    WindowBatches --> PrepareDatasetWindows["prepare_dataset_windows()"]
    PrepareDatasetWindows --> IterateLayers["Iterate dataset layers"]
    
    IterateLayers --> DataSourceFromConfig["data_source_from_config()"]
    DataSourceFromConfig --> GetGeometries["Get window geometries"]
    GetGeometries --> DataSourceGetItems["data_source.get_items()"]
    
    DataSourceGetItems --> SerializedItems["Serialized items"]
    SerializedItems --> WindowLayerData["WindowLayerData"]
    WindowLayerData --> SaveLayerData["window.save_layer_datas()"]
```

Sources: [rslearn/main.py:375-417](), [rslearn/main.py:419-460](), [rslearn/dataset/manage.py:53-133]()

### PrepareHandler Class

The `PrepareHandler` implements the core preparation logic with support for retries and error handling:

```mermaid
classDiagram
    class PrepareHandler {
        +force: bool
        +dataset: Dataset
        +retry_max_attempts: int
        +retry_backoff: timedelta
        +set_dataset(dataset)
        +__call__(windows)
    }
    
    class WindowLayerData {
        +layer_name: str
        +serialized_item_groups: list
    }
    
    class DataSource {
        +get_items(geometries, query_config)
        +deserialize_item(serialized_item)
    }
    
    PrepareHandler --> DataSource : uses
    PrepareHandler --> WindowLayerData : creates
    WindowLayerData --> Window : saved to
```

Sources: [rslearn/main.py:375-417](), [rslearn/dataset/manage.py:53-133]()

## Data Ingestion

Ingestion downloads the identified data items and stores them as tiles in the dataset's tile store. This stage handles the actual data transfer and tile-based storage.

### Ingestion Architecture

```mermaid
graph TD
    IngestCommand["rslearn dataset ingest"] --> IngestHandler["IngestHandler"]
    IngestHandler --> GetJobs["get_jobs()"]
    
    GetJobs --> LoadLayerDatas["Load WindowLayerData<br/>for all windows"]
    LoadLayerDatas --> GroupByItem["Group geometries<br/>by Item"]
    GroupByItem --> IngestJobs["Ingest job tuples<br/>(layer_name, layer_cfg, item, geometries)"]
    
    IngestJobs --> ApplyOnWindows["apply_on_windows()"]
    ApplyOnWindows --> IngestCall["IngestHandler.__call__()"]
    
    IngestCall --> GroupByLayer["Group jobs by layer"]
    GroupByLayer --> GetTileStore["get_tile_store_with_layer()"]
    GetTileStore --> DataSourceIngest["data_source.ingest()"]
    DataSourceIngest --> TileStorePopulated["TileStore populated<br/>with raw tiles"]
```

Sources: [rslearn/main.py:469-610](), [rslearn/main.py:612-653](), [rslearn/dataset/manage.py:135-194]()

### IngestHandler Implementation

The `IngestHandler` optimizes ingestion by grouping windows by the items they require, avoiding duplicate downloads:

| Method | Purpose | Input | Output |
|--------|---------|--------|--------|
| `get_jobs()` | Compute ingest jobs from windows | `list[Window]` | `list[tuple[str, LayerConfig, Item, list[STGeometry]]]` |
| `__call__()` | Execute ingest jobs | Ingest jobs | Populated TileStore |
| `_load_layer_data_for_windows()` | Load layer data with multiprocessing | `list[Window]` | `list[tuple[Window, dict[str, WindowLayerData]]]` |

Sources: [rslearn/main.py:469-610]()

## Data Materialization

Materialization extracts the window-specific portions of ingested data from the tile store and writes them in the final format for machine learning consumption.

### Materialization System

```mermaid
graph TD
    MaterializeCommand["rslearn dataset materialize"] --> MaterializeHandler["MaterializeHandler"]
    MaterializeHandler --> ApplyOnWindows["apply_on_windows()"]
    
    ApplyOnWindows --> MaterializeDatasetWindows["materialize_dataset_windows()"]
    MaterializeDatasetWindows --> IterateLayers["Iterate dataset layers"]
    
    IterateLayers --> MaterializeWindow["materialize_window()"]
    MaterializeWindow --> CheckCompleted{"Layer already<br/>completed?"}
    
    CheckCompleted -->|No| LoadLayerData["Load WindowLayerData"]
    LoadLayerData --> CheckIngested{"Items ingested?"}
    
    CheckIngested -->|Yes| SelectMaterializer["Select Materializer<br/>based on layer type"]
    CheckIngested -->|No| DirectMaterialize["Direct data source<br/>materialization"]
    
    SelectMaterializer --> RasterMaterializer["RasterMaterializer.materialize()"]
    SelectMaterializer --> VectorMaterializer["VectorMaterializer.materialize()"]
    
    RasterMaterializer --> WindowData["Window-specific<br/>raster files"]
    VectorMaterializer --> WindowData
    DirectMaterialize --> WindowData
```

Sources: [rslearn/main.py:655-695](), [rslearn/main.py:697-740](), [rslearn/dataset/manage.py:245-333](), [rslearn/dataset/manage.py:335-373]()

### Materializer Classes

The materialization system uses specialized classes for different data types:

```mermaid
classDiagram
    class Materializer~LayerConfigType~ {
        <<abstract>>
        +materialize(tile_store, window, layer_name, layer_cfg, item_groups)
    }
    
    class RasterMaterializer {
        +materialize(tile_store, window, layer_name, layer_cfg, item_groups)
        -read_raster_window_from_tiles()
    }
    
    class VectorMaterializer {
        +materialize(tile_store, window, layer_name, layer_cfg, item_groups)
    }
    
    class Materializers {
        <<registry>>
        +raster: RasterMaterializer
        +vector: VectorMaterializer
    }
    
    Materializer <|-- RasterMaterializer
    Materializer <|-- VectorMaterializer
    Materializers --> RasterMaterializer
    Materializers --> VectorMaterializer
```

Sources: [rslearn/dataset/materialize.py:31-51](), [rslearn/dataset/materialize.py:115-213](), [rslearn/dataset/materialize.py:215-254]()

### Raster Materialization Process

For raster data, materialization involves reading from multiple tiles and combining them into window-specific arrays:

```mermaid
graph TD
    RasterMaterialize["RasterMaterializer.materialize()"] --> IterateBandSets["Iterate band_sets"]
    IterateBandSets --> GetProjectionBounds["Get final projection<br/>and bounds"]
    
    GetProjectionBounds --> CreateDestArray["Create destination array<br/>np.zeros()"]
    CreateDestArray --> IterateItems["Iterate items in group"]
    
    IterateItems --> MapBands["Map wanted bands<br/>to available bands"]
    MapBands --> ReadRasterWindow["read_raster_window_from_tiles()"]
    
    ReadRasterWindow --> TileStoreRead["tile_store.read_raster()"]
    TileStoreRead --> ApplyRemapper["Apply remapper<br/>(if configured)"]
    ApplyRemapper --> CombineData["Combine into<br/>destination array"]
    
    CombineData --> EncodeRaster["raster_format.encode_raster()"]
    EncodeRaster --> MarkCompleted["window.mark_layer_completed()"]
```

Sources: [rslearn/dataset/materialize.py:115-213](), [rslearn/dataset/materialize.py:54-113]()

## Parallel Processing and Error Handling

### apply_on_windows Function

The dataset management system uses a common parallel processing pattern implemented in `apply_on_windows()`:

| Parameter | Purpose | Default |
|-----------|---------|---------|
| `workers` | Number of parallel processes | 0 (sequential) |
| `load_workers` | Workers for loading windows | Same as `workers` |
| `batch_size` | Windows per batch | 1 |
| `jobs_per_process` | Jobs before process restart | None |
| `use_initial_job` | Run first job in main thread | True |

```mermaid
graph TD
    ApplyOnWindows["apply_on_windows()"] --> SetDataset["f.set_dataset(dataset)"]
    SetDataset --> LoadWindows["dataset.load_windows()"]
    LoadWindows --> GetJobs{"f.get_jobs() exists?"}
    
    GetJobs -->|Yes| ComputeJobs["f.get_jobs(windows)"]
    GetJobs -->|No| UseWindows["jobs = windows"]
    
    ComputeJobs --> ShuffleJobs["random.shuffle(jobs)"]
    UseWindows --> ShuffleJobs
    
    ShuffleJobs --> InitialJob{"use_initial_job<br/>and jobs > 0?"}
    InitialJob -->|Yes| RunFirst["f([jobs[0]])"]
    InitialJob -->|No| CreateBatches["Create batches"]
    RunFirst --> CreateBatches
    
    CreateBatches --> CheckWorkers{"workers == 0?"}
    CheckWorkers -->|Yes| Sequential["Sequential processing<br/>with tqdm"]
    CheckWorkers -->|No| Parallel["multiprocessing.Pool<br/>with tqdm"]
    
    Sequential --> Complete["Processing complete"]
    Parallel --> Complete
```

Sources: [rslearn/main.py:283-357](), [rslearn/main.py:359-373]()

### Retry Mechanism

All dataset operations support configurable retry logic for handling transient failures:

```mermaid
graph TD
    RetryFunction["retry()"] --> AttemptLoop["for attempt_idx in range(retry_max_attempts)"]
    AttemptLoop --> TryFunction["try: fn()"]
    
    TryFunction --> Success["Return result"]
    TryFunction --> Exception["except Exception"]
    
    Exception --> CalculateBackoff["sleep_base_seconds = <br/>retry_backoff * (attempt_idx + 1)"]
    CalculateBackoff --> RandomizedSleep["time.sleep(sleep_base_seconds * <br/>(1 + random.random()))"]
    RandomizedSleep --> AttemptLoop
    
    AttemptLoop --> FinalAttempt["Final attempt:<br/>fn() without try/catch"]
    FinalAttempt --> Success
    FinalAttempt --> FinalException["Exception propagated"]
```

Sources: [rslearn/dataset/manage.py:26-51]()

## CLI Integration

The dataset management commands are integrated into the main rslearn CLI through a handler registry system:

```mermaid
graph TD
    MainCLI["rslearn CLI main()"] --> ParseCategory["Parse category and command"]
    ParseCategory --> HandlerRegistry["handler_registry.get()"]
    
    HandlerRegistry --> AddWindowsHandler["add_windows handler"]
    HandlerRegistry --> PrepareHandler["prepare handler"]  
    HandlerRegistry --> IngestHandler["ingest handler"]
    HandlerRegistry --> MaterializeHandler["materialize handler"]
    
    AddWindowsHandler --> AddWindowsFunction["add_windows()"]
    PrepareHandler --> DatasetPrepareFunction["dataset_prepare()"]
    IngestHandler --> DatasetIngestFunction["dataset_ingest()"]
    MaterializeHandler --> DatasetMaterializeFunction["dataset_materialize()"]
```

Sources: [rslearn/main.py:34-48](), [rslearn/main.py:812-842]()

The handlers are registered using the `@register_handler` decorator:

- `@register_handler("dataset", "add_windows")` - [rslearn/main.py:76]()
- `@register_handler("dataset", "prepare")` - [rslearn/main.py:419]()
- `@register_handler("dataset", "ingest")` - [rslearn/main.py:612]()
- `@register_handler("dataset", "materialize")` - [rslearn/main.py:697]()

Each handler follows a consistent pattern of argument parsing, creating handler objects, and calling `apply_on_windows_args()` for distributed processing.

Sources: [rslearn/main.py:41-48](), [rslearn/main.py:76-234](), [rslearn/main.py:419-460](), [rslearn/main.py:612-653](), [rslearn/main.py:697-740]()

---

