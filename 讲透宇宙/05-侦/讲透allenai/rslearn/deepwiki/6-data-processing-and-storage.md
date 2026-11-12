<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/rslearn · page 6 Data Processing and Storage · fetched 2026-10-26 -->

# Data Processing and Storage

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [rslearn/data_sources/raster_source.py](rslearn/data_sources/raster_source.py)
- [rslearn/dataset/materialize.py](rslearn/dataset/materialize.py)
- [rslearn/tile_stores/default.py](rslearn/tile_stores/default.py)
- [rslearn/utils/raster_format.py](rslearn/utils/raster_format.py)
- [tests/unit/tile_stores/test_default.py](tests/unit/tile_stores/test_default.py)
- [tests/unit/utils/test_raster_format.py](tests/unit/utils/test_raster_format.py)

</details>



This page covers the data storage formats, tile store systems, and materialization pipeline that convert raw remote sensing data into training-ready formats. This includes raster and vector format implementations, tile storage abstractions, and the materialization process that transforms ingested data into final dataset windows.

For information about data ingestion from external sources, see [Data Sources](#4). For details about dataset management and window creation, see [Dataset Management](#5). For machine learning data loading, see [Data Loading for Training](#7.4).

## Overview

The rslearn framework implements a multi-stage data processing pipeline that transforms raw remote sensing data into formats optimized for machine learning training:

```mermaid
graph TD
    SOURCES["Data Sources"] --> INGEST["Data Ingest"]
    INGEST --> TILESTORE["TileStore Storage"]
    TILESTORE --> MATERIALIZE["Materialization Process"] 
    MATERIALIZE --> WINDOWS["Dataset Windows"]
    
    subgraph "Storage Formats"
        RASTERFORMAT["RasterFormat Implementations"]
        VECTORFORMAT["VectorFormat Implementations"]
    end
    
    subgraph "Processing Components"
        MATERIALIZERS["Materializer Classes"]
        REMAPPERS["Data Remappers"]
    end
    
    TILESTORE --> MATERIALIZERS
    MATERIALIZERS --> RASTERFORMAT
    MATERIALIZERS --> VECTORFORMAT
    MATERIALIZERS --> WINDOWS
    REMAPPERS --> MATERIALIZERS
```

**Sources:** [rslearn/dataset/materialize.py:1-254](), [rslearn/utils/raster_format.py:1-702](), [rslearn/tile_stores/default.py:1-354]()

## Storage Format System

The framework provides pluggable storage formats for both raster and vector data through abstract base classes and concrete implementations.

### Raster Formats

The `RasterFormat` abstract class defines the interface for encoding and decoding raster data:

| Format | Class | Use Case | File Output |
|--------|-------|----------|-------------|
| `geotiff` | `GeotiffRasterFormat` | Single large GeoTIFF files | `geotiff.tif` |
| `image_tile` | `ImageTileRasterFormat` | Tiled storage with multiple files | `{col}_{row}.{ext}` |
| `single_image` | `SingleImageRasterFormat` | Simple image output | `image.{ext}` |

#### GeotiffRasterFormat

Stores raster data as a single tiled GeoTIFF file with configurable compression and tiling options:

```mermaid
graph LR
    INPUT["Input Array"] --> PROFILE["GeoTIFF Profile"]
    PROFILE --> TILING{"Enable Tiling?"}
    TILING -->|Yes| COG["Cloud Optimized GeoTIFF"]
    TILING -->|No| SIMPLE["Simple GeoTIFF"]
    COG --> OUTPUT["geotiff.tif"]
    SIMPLE --> OUTPUT
```

**Sources:** [rslearn/utils/raster_format.py:381-534]()

#### ImageTileRasterFormat

Splits large rasters into a grid of smaller tiles, with each tile stored as a separate image file:

```mermaid
graph TD
    ARRAY["Input Raster Array"] --> GRID["Tile Grid Calculation"]
    GRID --> PADDING["Array Padding to Grid"]
    PADDING --> TILES["Individual Tile Creation"]
    TILES --> METADATA["metadata.json"]
    TILES --> TILEFILES["{col}_{row}.{ext} Files"]
```

**Sources:** [rslearn/utils/raster_format.py:132-379]()

### Vector Formats

Vector data storage is handled through the `VectorFormat` interface, with implementations for common geospatial vector formats.

**Sources:** [rslearn/utils/vector_format.py](), [rslearn/dataset/materialize.py:215-254]()

## Tile Store System

Tile stores provide an abstraction layer for managing raw ingested data before materialization. The `DefaultTileStore` class implements the primary storage backend.

### DefaultTileStore Architecture

```mermaid
graph TB
    subgraph "Storage Layout"
        ROOT["Dataset Root Path"]
        LAYER["Layer Directories"]
        ITEM["Item Directories"] 
        BANDS["Band Set Directories"]
        FILES["Data Files + completed"]
    end
    
    ROOT --> LAYER
    LAYER --> ITEM
    ITEM --> BANDS
    BANDS --> FILES
    
    subgraph "Operations"
        WRITE["write_raster()"]
        READ["read_raster()"] 
        CHECK["is_raster_ready()"]
        BOUNDS["get_raster_bounds()"]
    end
    
    FILES --> READ
    WRITE --> FILES
    CHECK --> FILES
    BOUNDS --> FILES
```

The tile store organizes data in a hierarchical directory structure: `{layer}/{item}/{bands}/files`. Each raster is stored with a completion marker file to indicate successful writes.

**Sources:** [rslearn/tile_stores/default.py:33-354]()

### TileStore Operations

| Method | Purpose | Return Type |
|--------|---------|-------------|
| `write_raster()` | Store raster array with metadata | `None` |
| `read_raster()` | Read raster in specified projection/bounds | `numpy.ndarray` |
| `get_raster_bounds()` | Get bounds of stored raster | `PixelBounds` |
| `is_raster_ready()` | Check if raster ingestion completed | `bool` |
| `get_raster_bands()` | List available band sets for item | `list[list[str]]` |

**Sources:** [rslearn/tile_stores/default.py:125-354]()

## Materialization Process

Materialization transforms ingested tile store data into final dataset formats through the `Materializer` system. This process handles projection transformations, band selection, data remapping, and format conversion.

### Materializer Classes

```mermaid
graph TD
    MATERIALIZER["Materializer<LayerConfigType>"]
    RASTERMATERIALIZER["RasterMaterializer"]
    VECTORMATERIALIZER["VectorMaterializer"]
    
    MATERIALIZER -.->|inherits| RASTERMATERIALIZER
    MATERIALIZER -.->|inherits| VECTORMATERIALIZER
    
    subgraph "Raster Processing"
        TILESTORE1["TileStore"] --> READ1["read_raster_window_from_tiles()"]
        READ1 --> REMAP["Remapper.apply()"]
        REMAP --> FORMAT1["RasterFormat.encode_raster()"]
    end
    
    subgraph "Vector Processing"  
        TILESTORE2["TileStore"] --> READ2["read_vector()"]
        READ2 --> FORMAT2["VectorFormat.encode_vector()"]
    end
    
    RASTERMATERIALIZER --> TILESTORE1
    VECTORMATERIALIZER --> TILESTORE2
```

**Sources:** [rslearn/dataset/materialize.py:31-254]()

### Raster Materialization Pipeline

The `RasterMaterializer` implements a sophisticated pipeline for processing raster data:

1. **Band Resolution**: Determines which tile store band sets contain the required output bands
2. **Projection Handling**: Applies zoom offsets and projection transformations via `BandSetConfig`
3. **Data Reading**: Uses `read_raster_window_from_tiles()` to extract data from multiple items
4. **Remapping**: Applies optional data transformations via `Remapper` classes
5. **Format Encoding**: Writes final data using the configured `RasterFormat`

```mermaid
graph TD
    CONFIG["BandSetConfig"] --> PROJECTION["get_final_projection_and_bounds()"]
    PROJECTION --> ARRAY["Create destination array"]
    
    subgraph "Multi-Item Processing"
        ITEMS["Item Groups"] --> BANDMAP["Band Mapping Resolution"]
        BANDMAP --> TILEREAD["read_raster_window_from_tiles()"]
        TILEREAD --> REMAP["Optional Remapping"]
        REMAP --> MERGE["Merge into destination"]
    end
    
    ARRAY --> ITEMS
    MERGE --> ENCODE["RasterFormat.encode_raster()"]
    ENCODE --> COMPLETE["mark_layer_completed()"]
```

**Sources:** [rslearn/dataset/materialize.py:115-213](), [rslearn/dataset/materialize.py:54-113]()

### Data Remapping

The materialization process supports optional data transformations through the `Remapper` system, which can modify pixel values during the materialization process. This enables operations like value scaling, categorical remapping, and data type conversions.

**Sources:** [rslearn/dataset/materialize.py:102-103](), [rslearn/dataset/remap.py]()

## Window Data Organization

Materialized data is organized into window-specific directories with a consistent structure for both raster and vector data:

```mermaid
graph TD
    WINDOW["Window Directory"] --> LAYERS["Layer Subdirectories"]
    LAYERS --> GROUPS["Group ID Subdirectories"]  
    GROUPS --> RASTERDATA["Raster Band Directories"]
    GROUPS --> VECTORDATA["Vector Data Files"]
    
    RASTERDATA --> RASTERFILES["Format-specific files"]
    VECTORDATA --> VECTORFILES["Format-specific files"]
    
    subgraph "Completion Tracking"
        COMPLETED["completed marker files"]
        RASTERFILES --> COMPLETED
        VECTORFILES --> COMPLETED
    end
```

The `Window` class provides methods for accessing materialized data paths and tracking completion status across layers and group IDs.

**Sources:** [rslearn/dataset/window.py](), [rslearn/dataset/materialize.py:204-212]()

## Integration with Data Pipeline

The data processing and storage system integrates with the broader rslearn pipeline through well-defined interfaces:

- **Input**: Raw data from `DataSource` implementations via tile store ingestion
- **Configuration**: Layer specifications from `RasterLayerConfig` and `VectorLayerConfig`  
- **Output**: Training-ready data accessible via `Window` objects for ML data loading
- **Monitoring**: Completion tracking and progress reporting through marker files

This design enables efficient parallel processing, resumable operations, and flexible storage backend configurations while maintaining data integrity throughout the pipeline.

**Sources:** [rslearn/dataset/materialize.py:34-51](), [rslearn/config/__init__.py]()

---

