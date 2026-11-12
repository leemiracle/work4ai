<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/rslearn · page 4 Data Sources · fetched 2026-10-26 -->

# Data Sources

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [rslearn/data_sources/__init__.py](rslearn/data_sources/__init__.py)
- [rslearn/data_sources/data_source.py](rslearn/data_sources/data_source.py)
- [rslearn/data_sources/utils.py](rslearn/data_sources/utils.py)
- [tests/unit/data_sources/__init__.py](tests/unit/data_sources/__init__.py)
- [tests/unit/data_sources/test_match_candidate_items_to_window.py](tests/unit/data_sources/test_match_candidate_items_to_window.py)

</details>



The data sources system provides a unified interface for accessing remote sensing data from various providers and formats. This system abstracts the complexity of different data repositories, enabling consistent access to satellite imagery, climate data, and other geospatial datasets through a common API.

For specific data source implementations, see [AWS Data Sources](#4.1), [Google Cloud Data Sources](#4.2), [Climate Data Sources](#4.3), [European Space Agency Data Sources](#4.4), and [Local and Web Data Sources](#4.5). For dataset management operations that use these data sources, see [Dataset Management](#5).

## Core Architecture

The data source system is built around several key abstractions that enable flexible data access patterns and query modes.

### Data Source Class Hierarchy

```mermaid
classDiagram
    class DataSource~ItemType~ {
        <<abstract>>
        +get_items(geometries, query_config) list~list~list~ItemType~~~
        +deserialize_item(serialized_item) ItemType
        +ingest(tile_store, items, geometries) void
        +materialize(window, item_groups, layer_name, layer_cfg) void
    }
    
    class ItemLookupDataSource~ItemType~ {
        +get_item_by_name(name) ItemType
    }
    
    class RetrieveItemDataSource~ItemType~ {
        +retrieve_item(item) Generator~tuple~str_BinaryIO~~
    }
    
    class Item {
        +name: str
        +geometry: STGeometry
        +serialize() dict
        +deserialize(dict) Item
    }
    
    DataSource <|-- ItemLookupDataSource
    DataSource <|-- RetrieveItemDataSource
    DataSource --> Item : "works with"
```

**Sources:** [rslearn/data_sources/data_source.py:12-130]()

### Item Structure

The `Item` class represents individual data objects within a data source, such as satellite scenes or vector files. Each item has a unique name and spatiotemporal geometry.

| Property | Type | Description |
|----------|------|-------------|
| `name` | `str` | Unique identifier for the item |
| `geometry` | `STGeometry` | Spatial and temporal extent |

**Sources:** [rslearn/data_sources/data_source.py:12-52]()

## Query System

The data source system supports sophisticated querying based on spatial and temporal criteria through the `QueryConfig` system.

### Space and Time Modes

```mermaid
graph TD
    QueryConfig["QueryConfig"] --> SpaceMode["SpaceMode"]
    QueryConfig --> TimeMode["TimeMode"]
    QueryConfig --> MaxMatches["max_matches"]
    
    SpaceMode --> CONTAINS["CONTAINS<br/>Item must contain geometry"]
    SpaceMode --> INTERSECTS["INTERSECTS<br/>Item must intersect geometry"]
    SpaceMode --> MOSAIC["MOSAIC<br/>Combine items to cover geometry"]
    
    TimeMode --> WITHIN["WITHIN<br/>Items within time range"]
    TimeMode --> BEFORE["BEFORE<br/>Items before time range"]
    TimeMode --> AFTER["AFTER<br/>Items after time range"]
    
    MOSAIC --> PendingMosaic["PendingMosaic<br/>items: list<br/>remainder: Polygon<br/>completed: bool"]
```

**Sources:** [rslearn/data_sources/utils.py:40-180]()

### Item Matching Algorithm

The `match_candidate_items_to_window` function implements the core logic for matching data source items to spatial windows based on query configuration.

```mermaid
flowchart TD
    Start["match_candidate_items_to_window"] --> TimeFilter["Filter items by time range"]
    TimeFilter --> TimeSort["Sort by TimeMode<br/>(BEFORE: reverse, AFTER: forward)"]
    TimeSort --> SpaceMode{"SpaceMode?"}
    
    SpaceMode -->|CONTAINS| Contains["Check if item.shp.contains(geometry.shp)"]
    SpaceMode -->|INTERSECTS| Intersects["Check if shp_intersects(item.shp, geometry.shp)"]
    SpaceMode -->|MOSAIC| MosaicStart["Initialize pending_mosaics: list[PendingMosaic]"]
    
    Contains --> ContainsResult["Return individual item groups"]
    Intersects --> IntersectsResult["Return individual item groups"]
    
    MosaicStart --> MosaicLoop["For each item"]
    MosaicLoop --> CheckExisting["Try to add to existing mosaic"]
    CheckExisting --> CheckCoverage["Check MOSAIC_MIN_ITEM_COVERAGE"]
    CheckCoverage --> UpdateRemainder["Update mosaic.remainder = remainder - item.shp"]
    UpdateRemainder --> CheckComplete["Check if remainder.area < MOSAIC_REMAINDER_EPSILON"]
    CheckComplete --> MosaicResult["Return mosaic groups"]
```

**Sources:** [rslearn/data_sources/utils.py:40-180]()

## Data Source Loading

Data sources are dynamically loaded from configuration using a factory pattern.

### Dynamic Loading Process

```mermaid
sequenceDiagram
    participant Config as "LayerConfig"
    participant Factory as "data_source_from_config"
    participant ImportLib as "importlib"
    participant DataSource as "DataSource Class"
    
    Config->>Factory: config.data_source.name
    Factory->>Factory: Parse module and class name
    Factory->>ImportLib: import_module(module_name)
    ImportLib->>Factory: module
    Factory->>DataSource: getattr(module, class_name)
    DataSource->>Factory: class_.from_config(config, ds_path)
    Factory->>Config: DataSource instance
```

The loading process splits the fully qualified class name (e.g., `"rslearn.data_sources.landsat.LandsatOliTirs"`) into module and class components for dynamic import.

**Sources:** [rslearn/data_sources/__init__.py:26-42]()

## Data Source Operations

Data sources support two primary operations for data access:

### Ingest Operation

The `ingest` method downloads and stores raw data from the source into a tile store:

```mermaid
graph LR
    Items["Items<br/>(from get_items)"] --> Ingest["ingest()"]
    Geometries["Required Geometries"] --> Ingest
    Ingest --> TileStore["TileStoreWithLayer<br/>(raw data storage)"]
```

### Materialize Operation

The `materialize` method processes data directly for specific windows:

```mermaid
graph LR
    Window["Window"] --> Materialize["materialize()"]
    ItemGroups["Item Groups"] --> Materialize
    LayerConfig["LayerConfig"] --> Materialize
    Materialize --> WindowData["Processed Window Data"]
```

**Sources:** [rslearn/data_sources/data_source.py:81-111]()

## Mosaic Creation

The mosaic system enables combining multiple overlapping items to provide complete coverage of a spatial region.

### Mosaic Algorithm Constants

| Constant | Value | Purpose |
|----------|-------|---------|
| `MOSAIC_MIN_ITEM_COVERAGE` | 0.1 | Minimum fraction of area an item must cover |
| `MOSAIC_REMAINDER_EPSILON` | 0.01 | Threshold for considering mosaic complete |

### PendingMosaic State

The `PendingMosaic` dataclass tracks the state of mosaics being constructed:

```mermaid
stateDiagram-v2
    [*] --> Creating : New PendingMosaic
    Creating --> Adding : Add intersecting items
    Adding --> Adding : More items fit
    Adding --> Completed : remainder.area < MOSAIC_REMAINDER_EPSILON
    Completed --> [*]
    
    note right of Adding : Check MOSAIC_MIN_ITEM_COVERAGE<br/>Update remainder geometry
```

**Sources:** [rslearn/data_sources/utils.py:13-38](), [rslearn/data_sources/utils.py:113-179]()

## Integration with Dataset System

Data sources integrate with the broader rslearn dataset system through standardized interfaces:

```mermaid
graph TB
    subgraph "Dataset Layer"
        Window["Window"]
        LayerConfig["LayerConfig"]
    end
    
    subgraph "Data Source Layer"
        DataSource["DataSource"]
        Items["Items"]
        QueryConfig["QueryConfig"]
    end
    
    subgraph "Storage Layer"
        TileStore["TileStoreWithLayer"]
        MaterializedData["Materialized Data"]
    end
    
    Window --> DataSource : "get_items()"
    LayerConfig --> DataSource : "configuration"
    QueryConfig --> DataSource : "query parameters"
    
    DataSource --> Items : "produces"
    Items --> TileStore : "ingest()"
    Items --> MaterializedData : "materialize()"
```

**Sources:** [rslearn/data_sources/data_source.py:1-130](), [rslearn/data_sources/utils.py:1-181]()

---

