<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/rslearn · page 3 Core Concepts · fetched 2026-10-26 -->

# Core Concepts

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [rslearn/config/__init__.py](rslearn/config/__init__.py)
- [rslearn/config/dataset.py](rslearn/config/dataset.py)
- [rslearn/dataset/dataset.py](rslearn/dataset/dataset.py)
- [rslearn/tile_stores/__init__.py](rslearn/tile_stores/__init__.py)
- [rslearn/tile_stores/tile_store.py](rslearn/tile_stores/tile_store.py)
- [rslearn/utils/geometry.py](rslearn/utils/geometry.py)
- [rslearn/utils/jsonargparse.py](rslearn/utils/jsonargparse.py)

</details>



This page covers the fundamental building blocks of the rslearn framework: datasets, spatiotemporal geometry, configuration system, and data storage abstractions. These concepts form the foundation for data ingestion, processing, and machine learning workflows. For information about specific data sources and their implementations, see [Data Sources](#4). For machine learning training concepts and model architectures, see [Machine Learning Framework](#7).

## Datasets

A `Dataset` is the primary organizational unit in rslearn, representing a collection of spatiotemporal windows with associated data layers. Datasets are stored as directory structures containing configuration files, windows, and processed data.

### Dataset Structure

```mermaid
graph TD
    subgraph "Dataset Directory Structure"
        ROOT["dataset/"]
        CONFIG["config.json"]
        WINDOWS_DIR["windows/"]
        
        subgraph "Window Groups"
            GROUP1["group1/"]
            GROUP2["group2/"]
        end
        
        subgraph "Individual Windows"
            WINDOW1["epsg:3857_10_623565_1528020/"]
            METADATA["metadata.json"]
            LAYERS_DIR["layers/"]
            
            subgraph "Layer Data"
                RASTER_LAYER["sentinel2/"]
                VECTOR_LAYER["label/"]
                RASTER_FILE["0_0_tci.tif"]
                VECTOR_FILE["0_0_label.json"]
            end
        end
    end
    
    ROOT --> CONFIG
    ROOT --> WINDOWS_DIR
    WINDOWS_DIR --> GROUP1
    WINDOWS_DIR --> GROUP2
    GROUP1 --> WINDOW1
    WINDOW1 --> METADATA
    WINDOW1 --> LAYERS_DIR
    LAYERS_DIR --> RASTER_LAYER
    LAYERS_DIR --> VECTOR_LAYER
    RASTER_LAYER --> RASTER_FILE
    VECTOR_LAYER --> VECTOR_FILE
```

The `Dataset` class loads configuration from `config.json` and provides methods to load windows, manage layers, and access tile stores. Each dataset contains multiple window groups, where each group contains spatiotemporal windows identified by their projection and pixel bounds.

Sources: [rslearn/dataset/dataset.py:18-125]()

### Windows

Windows represent spatiotemporal regions of interest defined by their projection, pixel bounds, and time range. They serve as the fundamental unit for data retrieval and materialization in rslearn.

```mermaid
graph LR
    subgraph "Window Concept"
        WINDOW["Window"]
        PROJECTION["Projection<br/>(CRS + Resolution)"]
        BOUNDS["PixelBounds<br/>(minx, miny, maxx, maxy)"]
        TIME["Time Range<br/>(start, end)"]
    end
    
    WINDOW --> PROJECTION
    WINDOW --> BOUNDS
    WINDOW --> TIME
    
    subgraph "Window Processing"
        LOAD["Window.load()"]
        METADATA["metadata.json"]
        LAYERS["Layer Data"]
    end
    
    LOAD --> METADATA
    LOAD --> LAYERS
```

Sources: [rslearn/dataset/dataset.py:69-116]()

## Spatiotemporal Geometry

The framework provides robust handling of spatial coordinate systems and temporal ranges through the `Projection` and `STGeometry` classes.

### Projection System

```mermaid
graph TD
    subgraph "Projection Components"
        PROJ["Projection"]
        CRS["CRS<br/>(Coordinate Reference System)"]
        XRES["x_resolution<br/>(pixels per unit)"]
        YRES["y_resolution<br/>(pixels per unit)"]
    end
    
    PROJ --> CRS
    PROJ --> XRES  
    PROJ --> YRES
    
    subgraph "Operations"
        SERIALIZE["serialize()"]
        DESERIALIZE["deserialize()"]
        EQUAL["__eq__()"]
        HASH["__hash__()"]
    end
    
    PROJ --> SERIALIZE
    PROJ --> DESERIALIZE
    PROJ --> EQUAL
    PROJ --> HASH
```

The `Projection` class combines a coordinate reference system (CRS) with x and y resolutions to define how pixel coordinates map to real-world coordinates. It supports serialization for configuration storage and provides comparison operations.

Sources: [rslearn/utils/geometry.py:45-113]()

### Spatiotemporal Geometry

```mermaid
graph TD
    subgraph "STGeometry Components"
        STGEOM["STGeometry"]
        PROJ2["Projection"]
        SHAPE["shapely.Geometry"]
        TIMERANGE["Time Range<br/>(optional)"]
    end
    
    STGEOM --> PROJ2
    STGEOM --> SHAPE
    STGEOM --> TIMERANGE
    
    subgraph "Spatial Operations"
        INTERSECTS["intersects()"]
        TO_PROJ["to_projection()"]
        IS_GLOBAL["is_global()"]
        IS_TOO_LARGE["is_too_large()"]
    end
    
    subgraph "Temporal Operations"
        CONTAINS_TIME["contains_time()"]
        DISTANCE_TIME["distance_to_time()"]
        INTERSECTS_TIME["intersects_time_range()"]
    end
    
    STGEOM --> INTERSECTS
    STGEOM --> TO_PROJ
    STGEOM --> IS_GLOBAL
    STGEOM --> IS_TOO_LARGE
    STGEOM --> CONTAINS_TIME
    STGEOM --> DISTANCE_TIME
    STGEOM --> INTERSECTS_TIME
```

`STGeometry` combines spatial geometry (using Shapely) with temporal information and projection details. It supports spatial intersection testing, coordinate system transformations, and temporal range operations essential for matching windows with data items.

Sources: [rslearn/utils/geometry.py:116-314]()

## Configuration System

The configuration system provides structured, serializable definitions for all dataset components through a hierarchy of configuration classes.

### Configuration Class Hierarchy

```mermaid
graph TD
    subgraph "Layer Configurations"
        LAYER_CONFIG["LayerConfig"]
        RASTER_LAYER["RasterLayerConfig"]
        VECTOR_LAYER["VectorLayerConfig"]
        LAYER_TYPE["LayerType<br/>(RASTER/VECTOR)"]
    end
    
    LAYER_CONFIG --> RASTER_LAYER
    LAYER_CONFIG --> VECTOR_LAYER
    LAYER_CONFIG --> LAYER_TYPE
    
    subgraph "Data Source Configuration"
        DS_CONFIG["DataSourceConfig"]
        QUERY_CONFIG["QueryConfig"]
        SPACE_MODE["SpaceMode<br/>(CONTAINS/INTERSECTS/MOSAIC)"]
        TIME_MODE["TimeMode<br/>(WITHIN/NEAREST/BEFORE/AFTER)"]
    end
    
    DS_CONFIG --> QUERY_CONFIG
    QUERY_CONFIG --> SPACE_MODE
    QUERY_CONFIG --> TIME_MODE
    
    subgraph "Raster-Specific"
        BANDSET_CONFIG["BandSetConfig"]
        DTYPE["DType"]
        RASTER_FORMAT["RasterFormatConfig"]
        RESAMPLING["Resampling Method"]
    end
    
    RASTER_LAYER --> BANDSET_CONFIG
    BANDSET_CONFIG --> DTYPE
    BANDSET_CONFIG --> RASTER_FORMAT
    RASTER_LAYER --> RESAMPLING
    
    subgraph "Vector-Specific"
        VECTOR_FORMAT["VectorFormatConfig"]
        CLASS_NAMES["Class Names"]
    end
    
    VECTOR_LAYER --> VECTOR_FORMAT
    VECTOR_LAYER --> CLASS_NAMES
    
    LAYER_CONFIG --> DS_CONFIG
```

The configuration system uses composition to build complex dataset specifications from simple, reusable components. Each configuration class supports serialization to/from JSON for storage in `config.json` files.

Sources: [rslearn/config/dataset.py:1-532]()

### Query Configuration

Query configurations define how spatiotemporal windows are matched with data items from data sources:

| SpaceMode | Description |
|-----------|-------------|
| `CONTAINS` | Items must contain the entire window |
| `INTERSECTS` | Items must overlap any portion of the window |
| `MOSAIC` | Groups of items are computed to cover the entire window |

| TimeMode | Description |
|----------|-------------|
| `WITHIN` | Items must be within the window time range |
| `NEAREST` | Select items closest to the window time range |
| `BEFORE` | Select items before the end of the window time range |
| `AFTER` | Select items after the start of the window time range |

Sources: [rslearn/config/dataset.py:226-302]()

### Band Set Configuration

Raster layers use `BandSetConfig` to specify how bands are grouped, stored, and processed:

```mermaid
graph LR
    subgraph "BandSetConfig"
        BANDSET["BandSetConfig"]
        BANDS["bands: list[str]"]
        DTYPE_VAL["dtype: DType"]
        FORMAT["format: dict"]
        ZOOM_OFFSET["zoom_offset: int"]
        REMAP["remap: dict"]
        CLASS_NAMES_VAL["class_names: list[list[str]]"]
    end
    
    BANDSET --> BANDS
    BANDSET --> DTYPE_VAL
    BANDSET --> FORMAT
    BANDSET --> ZOOM_OFFSET
    BANDSET --> REMAP
    BANDSET --> CLASS_NAMES_VAL
    
    subgraph "Zoom Offset Effects"
        ZOOM_POS["zoom_offset > 0<br/>Higher Resolution"]
        ZOOM_NEG["zoom_offset < 0<br/>Lower Resolution"]
        ZOOM_ZERO["zoom_offset = 0<br/>Window Resolution"]
    end
    
    ZOOM_OFFSET --> ZOOM_POS
    ZOOM_OFFSET --> ZOOM_NEG
    ZOOM_OFFSET --> ZOOM_ZERO
```

The `zoom_offset` parameter enables storing data at different resolutions than the window resolution, allowing optimization for storage space or detail preservation.

Sources: [rslearn/config/dataset.py:116-224]()

## Data Storage Abstraction

The `TileStore` system provides an abstraction layer for reading and writing raster and vector data during ingestion and materialization phases.

### TileStore Architecture

```mermaid
graph TD
    subgraph "TileStore Abstraction"
        TILESTORE["TileStore<br/>(Abstract Base)"]
        DEFAULT_TS["DefaultTileStore"]
        CUSTOM_TS["Custom TileStore<br/>Implementations"]
    end
    
    TILESTORE --> DEFAULT_TS
    TILESTORE --> CUSTOM_TS
    
    subgraph "Operations"
        RASTER_OPS["Raster Operations"]
        VECTOR_OPS["Vector Operations"]
        
        subgraph "Raster Methods"
            IS_READY["is_raster_ready()"]
            GET_BOUNDS["get_raster_bounds()"]
            READ_RASTER["read_raster()"]
            WRITE_RASTER["write_raster()"]
        end
        
        subgraph "Vector Methods"
            IS_VEC_READY["is_vector_ready()"]
            READ_VECTOR["read_vector()"]
            WRITE_VECTOR["write_vector()"]
        end
    end
    
    RASTER_OPS --> IS_READY
    RASTER_OPS --> GET_BOUNDS
    RASTER_OPS --> READ_RASTER
    RASTER_OPS --> WRITE_RASTER
    
    VECTOR_OPS --> IS_VEC_READY
    VECTOR_OPS --> READ_VECTOR
    VECTOR_OPS --> WRITE_VECTOR
    
    subgraph "Convenience Wrapper"
        TSL["TileStoreWithLayer"]
        LAYER_NAME["layer_name: str"]
    end
    
    TSL --> LAYER_NAME
    TILESTORE --> TSL
```

The `TileStoreWithLayer` wrapper provides layer-specific access to tile store operations, automatically passing the layer name to the underlying `TileStore` methods.

Sources: [rslearn/tile_stores/tile_store.py:12-329](), [rslearn/tile_stores/__init__.py:15-62]()

## Data Type System

The framework provides a unified data type system for handling different numeric formats across NumPy and PyTorch:

| DType | NumPy | PyTorch | Common Use |
|-------|-------|---------|------------|
| `UINT8` | `np.uint8` | - | RGB imagery, categorical data |
| `UINT16` | `np.uint16` | - | High-precision imagery |
| `FLOAT32` | `np.float32` | `torch.float32` | Continuous values, ML training |
| `INT32` | `np.int32` | `torch.int32` | Integer labels, indices |

The `DType` enum provides conversion methods `get_numpy_dtype()` and `get_torch_dtype()` to bridge between different numeric computing libraries.

Sources: [rslearn/config/dataset.py:17-60]()

## Configuration Loading

The framework uses a factory pattern to load configuration objects from JSON dictionaries:

```mermaid
graph LR
    subgraph "Configuration Loading"
        JSON["config.json"]
        LOAD_LAYER["load_layer_config()"]
        LAYER_TYPE_CHECK["LayerType Check"]
        RASTER_FACTORY["RasterLayerConfig.from_config()"]
        VECTOR_FACTORY["VectorLayerConfig.from_config()"]
    end
    
    JSON --> LOAD_LAYER
    LOAD_LAYER --> LAYER_TYPE_CHECK
    LAYER_TYPE_CHECK --> RASTER_FACTORY
    LAYER_TYPE_CHECK --> VECTOR_FACTORY
    
    subgraph "Deserialization Chain"
        DS_FROM_CONFIG["DataSourceConfig.from_config()"]
        QUERY_FROM_CONFIG["QueryConfig.from_config()"]
        BANDSET_FROM_CONFIG["BandSetConfig.from_config()"]
    end
    
    RASTER_FACTORY --> DS_FROM_CONFIG
    RASTER_FACTORY --> BANDSET_FROM_CONFIG
    DS_FROM_CONFIG --> QUERY_FROM_CONFIG
```

Each configuration class implements a `from_config()` static method that handles deserialization from dictionary representations, enabling flexible configuration file formats.

Sources: [rslearn/config/dataset.py:524-531](), [rslearn/config/__init__.py:1-33]()

---

