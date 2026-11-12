<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/procthor · page 5 Database System · fetched 2026-10-26 -->

# Database System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [procthor/constants.py](procthor/constants.py)
- [tasks.py](tasks.py)

</details>



## Purpose and Scope

The Database System provides static metadata that drives procedural generation in ProcTHOR. It consists of six specialized databases that store information about assets (3D objects), materials (textures), placement rules, object relationships, and architectural components. These databases are generated once from AI2-THOR metadata and distributed as part of the package, enabling deterministic and data-driven house generation.

This page provides an overview of the database architecture and data flow. For detailed information about specific database components, see [Database Architecture](#5.1). For the generation process that creates these databases, see [Database Generation](#5.2). For how generation stages query and filter database content, see [Asset Selection and Filtering](#5.3).

---

## Database Components

The ProcTHOR database system comprises six specialized databases stored as JSON files in the `procthor/databases/` directory:

| Database | File | Purpose | Primary Consumers |
|----------|------|---------|------------------|
| Asset Database | `asset-database.json` | Object metadata indexed by type (e.g., "Bed", "Chair") | Floor object placement, wall object placement |
| Material Database | `material-database.json` | Material identifiers grouped by material type | Material randomization |
| Asset Groups | `object-groups.json` | Semantically related asset collections | Floor object placement |
| Receptacles | `receptacles.json` | Object containment relationships and probabilities | Small object placement |
| Wall Holes | `wall-holes.json` | Geometric specifications for windows and doors | Door placement, window placement |
| Placement Annotations | Not explicitly stored separately | Spawn rules and placement constraints | Asset filtering across all stages |

These databases are immutable at runtime—they are generated once during development and packaged with the distribution.

**Sources:** [tasks.py:1-619](), [Diagram 3 from context]

---

## Database Architecture Overview

```mermaid
graph TB
    subgraph "Database Files"
        ASSET_DB["asset-database.json<br/>~1-2MB"]
        MATERIAL_DB["material-database.json<br/>~20KB"]
        OBJECT_GROUPS["object-groups.json<br/>~50KB"]
        RECEPTACLES["receptacles.json<br/>~10KB"]
        WALL_HOLES["wall-holes.json<br/>~30KB"]
    end
    
    subgraph "Runtime Access"
        PTDB["ProcTHORDatabase<br/>Global singleton"]
        ASSET_ACCESS["ASSET_DATABASE<br/>Dict[str, List[Asset]]"]
        MATERIAL_ACCESS["MATERIAL_DATABASE<br/>Dict[str, List[str]]"]
    end
    
    subgraph "Generation Consumers"
        FLOOR_OBJ["add_floor_objects()"]
        WALL_OBJ["add_wall_objects()"]
        DOORS["add_doors()"]
        MATERIALS["randomize_materials()"]
    end
    
    ASSET_DB --> PTDB
    MATERIAL_DB --> PTDB
    OBJECT_GROUPS --> PTDB
    RECEPTACLES --> PTDB
    WALL_HOLES --> PTDB
    
    PTDB --> ASSET_ACCESS
    PTDB --> MATERIAL_ACCESS
    
    ASSET_ACCESS --> FLOOR_OBJ
    ASSET_ACCESS --> WALL_OBJ
    ASSET_ACCESS --> DOORS
    
    MATERIAL_ACCESS --> MATERIALS
    
    OBJECT_GROUPS --> FLOOR_OBJ
    RECEPTACLES --> FLOOR_OBJ
    WALL_HOLES --> DOORS
    WALL_HOLES --> WALL_OBJ
```

**Database Architecture: Physical storage, runtime loading, and consumption by generation stages**

The database architecture follows a clear separation between storage (JSON files), runtime access (in-memory dictionaries), and consumption (generation functions). The `ProcTHORDatabase` class loads all JSON files on initialization and exposes them as queryable data structures.

**Sources:** [tasks.py:3-4](), [Diagram 3 from context]

---

## Database Generation Pipeline

```mermaid
graph LR
    subgraph "Input Sources"
        AI2THOR["AI2-THOR Simulator<br/>Asset metadata API"]
        MANUAL["Manual Annotations<br/>Placement rules"]
    end
    
    subgraph "Generation Script"
        TASKS["tasks.py"]
        CONTROLLER["Controller<br/>AI2-THOR connection"]
    end
    
    subgraph "Extraction Functions"
        GET_ASSETS["GetAssetDatabase<br/>action"]
        GET_MATERIALS["GetMaterials<br/>action"]
        GET_HOLES["GetAssetHoleMetadata<br/>action"]
        ANALYZE_SCENES["Scene object analysis"]
    end
    
    subgraph "Processing Functions"
        UPDATE_BBOX["update_asset_database_by_type()"]
        CREATE_SPLITS["create_splits()"]
        SET_STATES["set_object_states()"]
        SET_MATERIALS["set_materials_per_asset_id()"]
        SAVE_RECEPT["save_receptacles()"]
        SET_HOLES["set_wall_holes()"]
    end
    
    subgraph "Output Files"
        OUT_ASSET["asset-database.json"]
        OUT_MAT["material-database.json"]
        OUT_HOLES["wall-holes.json"]
        OUT_RECEPT["receptacles.json"]
    end
    
    AI2THOR --> CONTROLLER
    CONTROLLER --> GET_ASSETS
    CONTROLLER --> GET_MATERIALS
    CONTROLLER --> GET_HOLES
    CONTROLLER --> ANALYZE_SCENES
    
    TASKS --> CONTROLLER
    MANUAL --> TASKS
    
    GET_ASSETS --> UPDATE_BBOX
    UPDATE_BBOX --> CREATE_SPLITS
    CREATE_SPLITS --> SET_STATES
    SET_STATES --> SET_MATERIALS
    SET_MATERIALS --> OUT_ASSET
    
    GET_MATERIALS --> OUT_MAT
    
    GET_HOLES --> SET_HOLES
    SET_HOLES --> OUT_HOLES
    
    ANALYZE_SCENES --> SAVE_RECEPT
    SAVE_RECEPT --> OUT_RECEPT
```

**Database Generation Pipeline: One-time extraction from AI2-THOR to JSON files**

The database generation process is a one-time operation performed during development. The `tasks.py` script connects to AI2-THOR, queries various metadata endpoints, processes and enriches the data, then saves it as JSON files. This process is not run by end users.

**Sources:** [tasks.py:19-619]()

---

## Asset Database Schema

The Asset Database is the largest and most complex database, containing detailed metadata for every 3D asset in AI2-THOR.

```mermaid
graph TB
    subgraph "Top-Level Structure"
        ROOT["Asset Database<br/>Dict[objectType, List[Asset]]"]
    end
    
    subgraph "Object Types (Keys)"
        BED["'Bed'"]
        CHAIR["'Chair'"]
        TABLE["'DiningTable'"]
        WINDOW["'Window'"]
        DOOR["'Doorway'"]
        MORE["... ~100+ types"]
    end
    
    subgraph "Asset Entry Fields"
        ASSET_ID["assetId: str<br/>'Bed_1', 'Chair_23'"]
        OBJ_TYPE["objectType: str<br/>'Bed'"]
        BBOX["boundingBox: Dict<br/>{x, y, z} dimensions"]
        MATERIALS["materials: List<br/>[[group, material], ...]"]
        PROPS["secondaryProperties: List<br/>['CanOpen', 'Receptacle']"]
        SCENES["scenes: List[str]<br/>AI2-THOR scenes using this"]
        SPLIT["split: str<br/>'train', 'val', 'test', None"]
        STATES["states: Dict<br/>{'open': {boundingBox}}"]
    end
    
    ROOT --> BED
    ROOT --> CHAIR
    ROOT --> TABLE
    ROOT --> WINDOW
    ROOT --> DOOR
    ROOT --> MORE
    
    BED --> ASSET_ID
    BED --> OBJ_TYPE
    BED --> BBOX
    BED --> MATERIALS
    BED --> PROPS
    BED --> SCENES
    BED --> SPLIT
    BED --> STATES
```

**Asset Database Schema: Hierarchical structure with object types and per-asset metadata**

Each object type key maps to a list of asset entries. Each asset entry contains:
- **assetId**: Unique identifier (e.g., `"Bed_12"`)
- **objectType**: Category (e.g., `"Bed"`)
- **boundingBox**: 3D dimensions `{x, y, z}` in meters
- **materials**: List of `[materialGroup, material]` pairs for randomization
- **secondaryProperties**: Capabilities like `"CanOpen"`, `"Receptacle"`, `"Breakable"`
- **scenes**: List of AI2-THOR scene names where this asset appears
- **split**: Train/val/test designation for dataset splits, or `null` for assets with <6 instances
- **states**: Optional state-specific metadata (e.g., bounding box when open)

**Sources:** [tasks.py:85-180](), [tasks.py:412-467]()

---

## Material Database Schema

The Material Database organizes texture identifiers by material group, enabling semantic material randomization.

```mermaid
graph LR
    subgraph "Material Database"
        ROOT["Material Database<br/>Dict[materialGroup, List[materialId]]"]
    end
    
    subgraph "Material Groups"
        WOOD["'Wood'<br/>['Wood_01', 'Wood_02', ...]"]
        FABRIC["'Fabric'<br/>['Fabric_01', 'Fabric_02', ...]"]
        METAL["'Metal'<br/>['Metal_01', 'Metal_02', ...]"]
        CERAMIC["'Ceramic'<br/>['Ceramic_01', ...]"]
        PLASTIC["'Plastic'<br/>['Plastic_01', ...]"]
        MORE["... ~15+ groups"]
    end
    
    ROOT --> WOOD
    ROOT --> FABRIC
    ROOT --> METAL
    ROOT --> CERAMIC
    ROOT --> PLASTIC
    ROOT --> MORE
```

**Material Database Schema: Material identifiers grouped by semantic type**

The structure is a flat dictionary where each key is a material group (e.g., `"Wood"`, `"Fabric"`) and each value is a sorted list of material identifiers (e.g., `["Wood_01", "Wood_02", ...]`). This allows generation code to sample random materials while maintaining semantic coherence (e.g., a wooden table gets a wood texture, not metal).

**Sources:** [tasks.py:28-46](), [tasks.py:204-233]()

---

## Receptacle Database Schema

The Receptacle Database encodes probabilistic object containment relationships derived from AI2-THOR scene analysis.

```mermaid
graph TB
    subgraph "Receptacle Database"
        ROOT["Receptacle Database<br/>Dict[receptacleType, Dict[childType, Stats]]"]
    end
    
    subgraph "Example: Desk Receptacle"
        DESK["'Desk'"]
        LAPTOP["'Laptop': {p: 0.35, count: 42}"]
        PEN["'Pen': {p: 0.67, count: 80}"]
        BOOK["'Book': {p: 0.44, count: 53}"]
    end
    
    subgraph "Stats Object"
        PROB["p: float<br/>Probability (0-1)"]
        COUNT["count: int<br/>Occurrences in scenes"]
    end
    
    ROOT --> DESK
    DESK --> LAPTOP
    DESK --> PEN
    DESK --> BOOK
    
    LAPTOP --> PROB
    LAPTOP --> COUNT
```

**Receptacle Database Schema: Probability distributions for object containment**

Each receptacle type (e.g., `"Desk"`, `"CounterTop"`) maps to a dictionary of child object types. Each child entry contains:
- **p**: Probability this child appears on/in this receptacle (derived from AI2-THOR scene frequency)
- **count**: Number of times this relationship was observed

This drives realistic small object placement—laptops are more likely to appear on desks than on toilets.

**Sources:** [tasks.py:533-592]()

---

## Wall Holes Database Schema

The Wall Holes Database stores geometric specifications for assets that create openings in walls (windows and doors).

```mermaid
graph TB
    subgraph "Wall Holes Database"
        ROOT["Wall Holes Database<br/>Dict[assetId, HoleSpec]"]
    end
    
    subgraph "Hole Specification"
        WINDOW_1["'Window_1'"]
        DOOR_1["'Doorway_8'"]
        
        HOLE_BB["holePolygon: List<br/>2D boundary points"]
        HOLE_HEIGHT["height: float<br/>Vertical extent"]
        HOLE_DEPTH["depth: float<br/>Wall thickness"]
    end
    
    ROOT --> WINDOW_1
    ROOT --> DOOR_1
    
    WINDOW_1 --> HOLE_BB
    WINDOW_1 --> HOLE_HEIGHT
    WINDOW_1 --> HOLE_DEPTH
    
    DOOR_1 --> HOLE_BB
    DOOR_1 --> HOLE_HEIGHT
    DOOR_1 --> HOLE_DEPTH
```

**Wall Holes Database Schema: Geometric specifications for wall openings**

Each window or door asset ID maps to a specification containing:
- **holePolygon**: 2D boundary points defining the opening shape
- **height**: Vertical dimension in meters
- **depth**: Wall thickness requirement

This metadata is queried during door and window placement to ensure proper wall cutouts and collision avoidance.

**Sources:** [tasks.py:596-618]()

---

## Database Loading and Access Patterns

At runtime, database files are loaded once during module initialization and exposed through global constants and the `ProcTHORDatabase` class.

```mermaid
graph TB
    subgraph "Package Initialization"
        INIT["procthor/__init__.py<br/>Module import"]
        DB_MODULE["procthor/databases.py<br/>Database loading"]
    end
    
    subgraph "File System"
        DB_DIR["procthor/databases/<br/>JSON files"]
        ASSET_FILE["asset-database.json"]
        MAT_FILE["material-database.json"]
        GROUPS_FILE["object-groups.json"]
        RECEPT_FILE["receptacles.json"]
        HOLES_FILE["wall-holes.json"]
    end
    
    subgraph "Runtime Globals"
        ASSET_DB_CONST["ASSET_DATABASE<br/>Global constant"]
        MAT_DB_CONST["MATERIAL_DATABASE<br/>Global constant"]
        PTDB_CLASS["ProcTHORDatabase<br/>Singleton instance"]
    end
    
    subgraph "Generation Usage"
        GEN_FUNC["GenerationFunctions<br/>Protocol implementations"]
        QUERY["Database queries:<br/>- Filter by type<br/>- Sample by weight<br/>- Check constraints"]
    end
    
    INIT --> DB_MODULE
    
    DB_MODULE --> DB_DIR
    DB_DIR --> ASSET_FILE
    DB_DIR --> MAT_FILE
    DB_DIR --> GROUPS_FILE
    DB_DIR --> RECEPT_FILE
    DB_DIR --> HOLES_FILE
    
    ASSET_FILE --> ASSET_DB_CONST
    MAT_FILE --> MAT_DB_CONST
    GROUPS_FILE --> PTDB_CLASS
    RECEPT_FILE --> PTDB_CLASS
    HOLES_FILE --> PTDB_CLASS
    
    ASSET_DB_CONST --> GEN_FUNC
    MAT_DB_CONST --> GEN_FUNC
    PTDB_CLASS --> GEN_FUNC
    
    GEN_FUNC --> QUERY
```

**Database Loading: From JSON files to runtime access patterns**

Database loading follows this sequence:

1. **Module Import**: When `procthor` is imported, `__init__.py` triggers database loading
2. **JSON Parsing**: `databases.py` reads JSON files from `procthor/databases/` directory
3. **Global Constants**: Databases are exposed as module-level constants (`ASSET_DATABASE`, `MATERIAL_DATABASE`)
4. **Query Interface**: Generation functions access databases directly via these constants

This design ensures databases are loaded exactly once and remain immutable throughout execution, supporting thread-safe access and deterministic generation.

**Sources:** [tasks.py:3-4]()

---

## Database Versioning and Splits

The Asset Database includes versioning metadata to support train/val/test dataset splits and backward compatibility.

### Train/Val/Test Splits

Asset splits are determined during database generation via the `create_splits()` function:

```mermaid
graph TB
    ASSETS["All assets of one type<br/>(e.g., all 'Bed' assets)"]
    
    CHECK{"Count >= 6?"}
    
    NO_SPLIT["split = null<br/>(all assets always available)"]
    
    SHUFFLE["Shuffle with seed=42"]
    
    PARTITION["Partition:<br/>67% train<br/>16.7% val<br/>16.7% test"]
    
    TRAIN["split = 'train'"]
    VAL["split = 'val'"]
    TEST["split = 'test'"]
    
    ASSETS --> CHECK
    CHECK -->|No| NO_SPLIT
    CHECK -->|Yes| SHUFFLE
    SHUFFLE --> PARTITION
    PARTITION --> TRAIN
    PARTITION --> VAL
    PARTITION --> TEST
```

**Asset Split Determination: Reproducible train/val/test partitioning**

Object types with fewer than 6 assets receive `split=null` and are available in all datasets. Types with 6+ assets are deterministically partitioned (seed 42) into approximately 2/3 train, 1/6 val, 1/6 test. This ensures:
- Reproducibility across ProcTHOR versions
- Balanced visual diversity across splits
- No data leakage between splits

The `USE_ITHOR_SPLITS` constant [procthor/constants.py:1-2]() controls whether iTHOR object splits should be used instead.

**Sources:** [tasks.py:93-135](), [procthor/constants.py:1-2]()

---

## Integration with Generation Pipeline

The database system serves as the foundation for all generation stages, providing the content that fills procedurally generated structures.

| Generation Stage | Database Usage | Query Pattern |
|-----------------|----------------|---------------|
| Structure Generation | None | N/A (geometric algorithms only) |
| Door Placement | Wall Holes Database | Filter by type (`"Doorway"`), check dimensions |
| Light Placement | None | N/A (procedurally placed) |
| Exterior Walls | Material Database | Sample from `"WallMaterial"` group |
| Room Setup | Material Database | Sample from `"FloorMaterial"`, `"WallMaterial"` |
| Floor Objects | Asset Database, Asset Groups, Receptacles | Filter by room type, weight, placement annotations |
| Wall Objects | Asset Database, Wall Holes Database | Filter by `onWall=True`, check dimensions |
| Small Objects | Asset Database, Receptacles | Filter by `isPickupable=True`, sample by receptacle probability |
| Material Randomization | Material Database, Asset Database | Match material groups to asset material slots |

The database system's static nature enables:
- **Deterministic Generation**: Same seed + same database = same house
- **Fast Access**: In-memory lookups with no I/O overhead
- **Package Distribution**: Databases are bundled with the package, no external dependencies
- **Version Stability**: Database changes trigger new package versions, ensuring reproducibility

**Sources:** [Diagram 3 from context], [tasks.py:1-619]()

---

## Summary

The Database System is the content repository for ProcTHOR, storing metadata for 100+ object types, 1000+ assets, and semantic relationships. Generated once from AI2-THOR and distributed as JSON files, it provides the foundation for all procedural generation stages. The architecture balances comprehensive metadata (bounding boxes, materials, states, relationships) with efficient runtime access (in-memory dictionaries, global constants). For implementation details, see subsection pages [5.1](#5.1), [5.2](#5.2), and [5.3](#5.3).

---

