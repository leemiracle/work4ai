<!-- source: DeepWiki mcp.deepwiki.com · repo TissueImageAnalytics/tiatoolbox · page 2 Data Systems · fetched 2026-10-21 -->

# Data Systems

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [tests/test_annotation_stores.py](tests/test_annotation_stores.py)
- [tests/test_annotation_tilerendering.py](tests/test_annotation_tilerendering.py)
- [tests/test_visualization.py](tests/test_visualization.py)
- [tests/test_wsireader.py](tests/test_wsireader.py)
- [tiatoolbox/annotation/storage.py](tiatoolbox/annotation/storage.py)
- [tiatoolbox/utils/visualization.py](tiatoolbox/utils/visualization.py)
- [tiatoolbox/wsicore/wsireader.py](tiatoolbox/wsicore/wsireader.py)
- [whitelist.txt](whitelist.txt)

</details>



## Purpose and Scope

This document covers TIAToolbox's data handling systems for whole slide images (WSIs) and spatial annotations. The data systems provide unified interfaces for reading medical imaging data from various formats, managing spatial annotations with efficient storage and querying capabilities, and rendering annotations for visualization.

For information about image processing operations on this data, see [Image Processing Pipeline](#3). For machine learning inference using this data, see [Model and Inference Systems](#4).

## WSI Reading Architecture

The WSI reading system provides format-agnostic access to whole slide images through the `WSIReader` factory pattern. The system automatically detects file formats and instantiates appropriate readers, handling multi-resolution pyramids and coordinate system conversions.

### WSI Reader Factory and Format Detection

```mermaid
graph TB
    subgraph "WSI Reader Factory"
        WSIReaderOpen["WSIReader.open()"]
        FormatDetection["Format Detection Logic"]
        ReaderInstantiation["Reader Instantiation"]
    end
    
    subgraph "Concrete Readers"
        OpenSlideWSIReader["OpenSlideWSIReader"]
        TIFFWSIReader["TIFFWSIReader"] 
        DICOMWSIReader["DICOMWSIReader"]
        NGFFWSIReader["NGFFWSIReader"]
        JP2WSIReader["JP2WSIReader"]
        VirtualWSIReader["VirtualWSIReader"]
        FsspecJsonWSIReader["FsspecJsonWSIReader"]
        AnnotationStoreReader["AnnotationStoreReader"]
    end
    
    subgraph "Format Support"
        SVS[".svs files"]
        NDPI[".ndpi files"]
        TIFF[".tiff/.tif files"]
        DICOM["DICOM directories"]
        NGFF["NGFF/Zarr files"]
        JP2[".jp2 files"]
        NumPy["numpy arrays"]
        Remote["Remote files via fsspec"]
        AnnotationDB[".db annotation files"]
    end
    
    WSIReaderOpen --> FormatDetection
    FormatDetection --> ReaderInstantiation
    
    ReaderInstantiation --> OpenSlideWSIReader
    ReaderInstantiation --> TIFFWSIReader
    ReaderInstantiation --> DICOMWSIReader
    ReaderInstantiation --> NGFFWSIReader
    ReaderInstantiation --> JP2WSIReader
    ReaderInstantiation --> VirtualWSIReader
    ReaderInstantiation --> FsspecJsonWSIReader
    ReaderInstantiation --> AnnotationStoreReader
    
    OpenSlideWSIReader --> SVS
    OpenSlideWSIReader --> NDPI
    TIFFWSIReader --> TIFF
    DICOMWSIReader --> DICOM
    NGFFWSIReader --> NGFF
    JP2WSIReader --> JP2
    VirtualWSIReader --> NumPy
    FsspecJsonWSIReader --> Remote
    AnnotationStoreReader --> AnnotationDB
```

**WSI Reader Selection Logic**

Sources: [tiatoolbox/wsicore/wsireader.py:324-414]()

The `WSIReader.open()` method [tiatoolbox/wsicore/wsireader.py:324-414]() implements a cascading detection system:

| Format Check | Detection Method | Reader Class |
|--------------|------------------|--------------|
| DICOM | `is_dicom()` checks for `.dcm` files | `DICOMWSIReader` |
| NGFF | `is_ngff()` validates zarr metadata | `NGFFWSIReader` |
| OME-TIFF | Suffix pattern matching | `TIFFWSIReader` |
| OpenSlide | `OpenSlide.detect_format()` | `OpenSlideWSIReader` |
| Tiled TIFF | `is_tiled_tiff()` validation | `TIFFWSIReader` |
| Virtual formats | Extension-based routing | `VirtualWSIReader`/`JP2WSIReader` |

### Multi-Resolution and Coordinate Systems

```mermaid
graph TB
    subgraph "WSI Coordinate Systems"
        BaselineLevel["Baseline (Level 0)"]
        MPPUnits["MPP (microns per pixel)"]
        PowerUnits["Objective Power"]
        LevelUnits["Pyramid Level"]
        BaselineUnits["Baseline Scale Factor"]
    end
    
    subgraph "Resolution Conversion"
        ConvertResolutionUnits["convert_resolution_units()"]
        FindOptimalLevel["_find_optimal_level_and_downsample()"]
        FindReadParams["find_read_rect_params()"]
    end
    
    subgraph "Multi-Resolution Pyramid"
        Level0["Level 0 (Full Resolution)"]
        Level1["Level 1 (2x downsampled)"]
        Level2["Level 2 (4x downsampled)"]
        LevelN["Level N (2^N downsampled)"]
    end
    
    BaselineLevel --> ConvertResolutionUnits
    MPPUnits --> ConvertResolutionUnits
    PowerUnits --> ConvertResolutionUnits
    LevelUnits --> ConvertResolutionUnits
    BaselineUnits --> ConvertResolutionUnits
    
    ConvertResolutionUnits --> FindOptimalLevel
    FindOptimalLevel --> FindReadParams
    
    FindReadParams --> Level0
    FindReadParams --> Level1
    FindReadParams --> Level2
    FindReadParams --> LevelN
```

Sources: [tiatoolbox/wsicore/wsireader.py:530-759](), [tiatoolbox/wsicore/wsireader.py:993-1034]()

The system supports multiple coordinate systems and automatically converts between them using `convert_resolution_units()` [tiatoolbox/wsicore/wsireader.py:993-1034](). The `_find_optimal_level_and_downsample()` method [tiatoolbox/wsicore/wsireader.py:530-588]() determines the most efficient resolution level to read from based on the requested output resolution.

## Annotation Storage and Management

The annotation system provides persistent storage and efficient spatial querying of geometric annotations through an abstract `AnnotationStore` interface with multiple concrete implementations.

### Annotation Storage Architecture

```mermaid
graph TB
    subgraph "Annotation Core"
        Annotation["Annotation"]
        Geometry["Shapely Geometry"]
        Properties["Properties Dict"]
        WKB["WKB Bytes"]
    end
    
    subgraph "Storage Abstraction"
        AnnotationStore["AnnotationStore (ABC)"]
        MutableMapping["MutableMapping Interface"]
    end
    
    subgraph "Concrete Stores"
        SQLiteStore["SQLiteStore"]
        DictionaryStore["DictionaryStore"]
    end
    
    subgraph "SQLite Features"
        SpatialIndex["R-Tree Spatial Index"]
        PropertyIndex["Property Indexes"]
        Compression["Geometry Compression"]
        Transactions["ACID Transactions"]
    end
    
    subgraph "Query Interface"
        SpatialQuery["Spatial Queries"]
        PropertyQuery["Property Queries"]
        CombinedQuery["Combined Queries"]
    end
    
    Annotation --> Geometry
    Annotation --> Properties
    Annotation --> WKB
    
    AnnotationStore --> MutableMapping
    SQLiteStore --> AnnotationStore
    DictionaryStore --> AnnotationStore
    
    SQLiteStore --> SpatialIndex
    SQLiteStore --> PropertyIndex
    SQLiteStore --> Compression
    SQLiteStore --> Transactions
    
    AnnotationStore --> SpatialQuery
    AnnotationStore --> PropertyQuery
    AnnotationStore --> CombinedQuery
```

Sources: [tiatoolbox/annotation/storage.py:110-438](), [tiatoolbox/annotation/storage.py:443-460]()

### Annotation Data Model

The `Annotation` class [tiatoolbox/annotation/storage.py:110-438]() provides a unified representation:

| Component | Type | Purpose |
|-----------|------|---------|
| `geometry` | Shapely Geometry | Point, LineString, or Polygon |
| `properties` | Dict | Key-value metadata |
| `wkb` | bytes | Well-Known Binary serialization |

The class implements lazy geometry loading - Shapely objects are only created when first accessed, improving memory efficiency for large annotation sets.

### SQLite Storage Implementation

```mermaid
graph TB
    subgraph "SQLite Storage Schema"
        AnnotationsTable["annotations table"]
        MetadataTable["metadata table"]
        RTreeIndex["rtree_annotations index"]
        PropertyIndexes["property indexes"]
    end
    
    subgraph "Storage Operations"
        SerializeGeometry["serialise_geometry()"]
        DeserializeGeometry["deserialize_geometry()"]
        SpatialQueries["Spatial R-Tree queries"]
        PropertyQueries["Property JSON queries"]
    end
    
    subgraph "Performance Features"
        GeometryCompression["zlib/blosc compression"]
        IndexOptimization["create_index()"]
        QueryOptimization["ANALYZE statistics"]
        VacuumOptimization["optimize() with VACUUM"]
    end
    
    AnnotationsTable --> SerializeGeometry
    AnnotationsTable --> DeserializeGeometry
    RTreeIndex --> SpatialQueries
    PropertyIndexes --> PropertyQueries
    
    SerializeGeometry --> GeometryCompression
    IndexOptimization --> PropertyIndexes
    QueryOptimization --> PropertyIndexes
    VacuumOptimization --> AnnotationsTable
```

Sources: [tiatoolbox/annotation/storage.py:2025-2685]()

The `SQLiteStore` [tiatoolbox/annotation/storage.py:2025-2685]() provides enterprise-grade features:

- **Spatial Indexing**: R-Tree index for efficient geometric queries
- **Property Indexing**: Custom indexes on annotation properties for fast filtering
- **Compression**: Configurable geometry compression (zlib, blosc, or none)
- **ACID Compliance**: Full transaction support with rollback capabilities

## Data Format Support

TIAToolbox supports reading WSIs from multiple medical imaging formats through format-specific readers that handle the unique characteristics of each format.

### Supported WSI Formats

| Format | Extensions | Reader Class | Key Features |
|--------|-----------|--------------|--------------|
| Aperio SVS | `.svs` | `OpenSlideWSIReader` | Pyramid levels, associated images |
| Hamamatsu NDPI | `.ndpi` | `OpenSlideWSIReader` | Multi-focal planes, metadata |
| MIRAX | `.mrxs` | `OpenSlideWSIReader` | Hierarchical structure |
| Generic TIFF | `.tiff`, `.tif` | `TIFFWSIReader` | Tiled TIFF support |
| OME-TIFF | `.ome.tiff` | `TIFFWSIReader` | OME metadata, multi-channel |
| DICOM WSI | `.dcm`, directories | `DICOMWSIReader` | DICOM metadata, series |
| NGFF/Zarr | `.zarr` | `NGFFWSIReader` | Cloud-native, chunked storage |
| JPEG2000 | `.jp2` | `JP2WSIReader` | Wavelet compression |
| Virtual | `.npy`, `.png`, `.jpg` | `VirtualWSIReader` | In-memory arrays, single images |

Sources: [tiatoolbox/wsicore/wsireader.py:434-452]()

### Format Detection Logic

```mermaid
graph TD
    InputPath["Input Path"]
    
    InputPath --> IsDICOM{"is_dicom()"}
    IsDICOM -->|Yes| DICOMWSIReader
    IsDICOM -->|No| IsFsspecJSON{"FsspecJsonWSIReader.is_valid_zarr_fsspec()"}
    
    IsFsspecJSON -->|Yes| FsspecJsonWSIReader
    IsFsspecJSON -->|No| IsDB{"suffix == .db"}
    
    IsDB -->|Yes| AnnotationStoreReader
    IsDB -->|No| IsZarr{"suffix == .zarr"}
    
    IsZarr -->|Yes| IsNGFF{"is_ngff()"}
    IsNGFF -->|Yes| NGFFWSIReader
    IsNGFF -->|No| FileNotSupportedError
    
    IsZarr -->|No| IsOMETIFF{"suffixes == [.ome, .tiff]"}
    IsOMETIFF -->|Yes| TIFFWSIReader
    IsOMETIFF -->|No| IsTIFF{"suffix in [.tif, .tiff]"}
    
    IsTIFF -->|Yes| TryOpenSlide{"OpenSlide.detect_format()"}
    TryOpenSlide -->|Success| OpenSlideWSIReader
    TryOpenSlide -->|Fail| IsTiledTIFF{"is_tiled_tiff()"}
    IsTiledTIFF -->|Yes| TIFFWSIReader
    IsTiledTIFF -->|No| TryVirtual
    
    IsTIFF -->|No| TryVirtual{"_handle_virtual_wsi()"}
    TryVirtual -->|Success| VirtualOrJP2["VirtualWSIReader or JP2WSIReader"]
    TryVirtual -->|Fail| FallbackOpenSlide["OpenSlideWSIReader (fallback)"]
```

Sources: [tiatoolbox/wsicore/wsireader.py:375-414]()

## Visualization and Rendering

The visualization system renders spatial annotations onto image tiles through the `AnnotationRenderer` class, supporting various color mapping strategies and rendering optimizations.

### Annotation Rendering Pipeline

```mermaid
graph TB
    subgraph "Rendering Input"
        AnnotationStore["AnnotationStore"]
        WSIMeta["WSI Metadata"]
        RenderConfig["AnnotationRenderer Config"]
    end
    
    subgraph "AnnotationRenderer"
        ScoreProp["score_prop"]
        Mapper["Color Mapper"]
        WhereClause["where clause filter"]
        ScoreFn["score_fn transform"]
    end
    
    subgraph "Color Mapping Strategies"
        DirectColor["Direct color properties"]
        CategoricalMapper["Categorical mapping"]
        ContinuousMapper["Continuous colormap"]
        FunctionMapper["Custom function mapping"]
        SecondaryColormap["Secondary colormap"]
    end
    
    subgraph "Rendering Output"
        TileImage["Rendered Tile Image"]
        BlurFilter["Gaussian Blur (optional)"]
        TileGenerator["AnnotationTileGenerator"]
    end
    
    AnnotationStore --> AnnotationRenderer
    WSIMeta --> AnnotationRenderer
    RenderConfig --> AnnotationRenderer
    
    AnnotationRenderer --> ScoreProp
    AnnotationRenderer --> Mapper
    AnnotationRenderer --> WhereClause
    AnnotationRenderer --> ScoreFn
    
    Mapper --> DirectColor
    Mapper --> CategoricalMapper
    Mapper --> ContinuousMapper
    Mapper --> FunctionMapper
    Mapper --> SecondaryColormap
    
    AnnotationRenderer --> TileImage
    TileImage --> BlurFilter
    BlurFilter --> TileGenerator
```

Sources: [tiatoolbox/utils/visualization.py:570-877]()

### Color Mapping Configuration

| Mapping Strategy | Configuration | Use Case |
|------------------|---------------|----------|
| Direct Color | `score_prop="color"` | Pre-defined RGBA values in properties |
| Categorical | `mapper=["cat1", "cat2", ...]` | Discrete categories with random colors |
| Continuous | `mapper="viridis"` | Numerical values with matplotlib colormap |
| Dictionary | `mapper={value: color, ...}` | Explicit value-to-color mapping |
| Function | `function_mapper=lambda props: color` | Custom color computation |

Sources: [tiatoolbox/utils/visualization.py:630-644](), [tiatoolbox/utils/visualization.py:693-770]()

The rendering system optimizes performance through:
- **Scale-based simplification**: Polygons rendered as bounding boxes at high zoom levels
- **Decimation strategies**: Selective rendering of annotations when zoomed out
- **Lazy tile generation**: On-demand rendering with caching
- **GPU acceleration**: OpenCV-based rendering operations

Sources: [tiatoolbox/utils/visualization.py:600-610](), [tiatoolbox/tools/pyramid.py]()

---

