<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/procthor · page 4 Spatial Reasoning Systems · fetched 2026-10-26 -->

# Spatial Reasoning Systems

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [procthor/generation/objects.py](procthor/generation/objects.py)
- [procthor/generation/wall_objects.py](procthor/generation/wall_objects.py)

</details>



## Purpose and Scope

This document covers the spatial reasoning systems that enable physically plausible object placement in ProcTHOR. These systems handle geometric primitives, collision detection, available space tracking, and position calculation for both floor and wall objects. The spatial reasoning layer ensures that objects do not overlap and maintains appropriate spacing based on object type and placement location.

For information about how these spatial systems are used during specific generation stages, see [Generation Stages](#3). For database-driven placement rules and asset metadata, see [Database System](#5).

## System Architecture

The spatial reasoning systems operate on multiple geometric representations that are progressively refined as objects are placed:

```mermaid
graph TB
    subgraph "Core Primitives"
        ORTHO["OrthogonalPolygon<br/>Room floor space"]
        BBOX["BoundingBox<br/>Asset 3D extents"]
        VEC3["Vector3<br/>3D coordinates"]
        POLY["Polygon (Shapely)<br/>2D collision geometry"]
    end
    
    subgraph "Space Tracking"
        ROOM_POLY["room_polygon<br/>Original room boundary"]
        OPEN_POLY["open_polygon<br/>Available placement area"]
        RECTS["rectangles<br/>Set of placement zones"]
    end
    
    subgraph "Placement Operations"
        SAMPLE_RECT["sample_next_rectangle()<br/>Choose placement zone"]
        SAMPLE_ANCHOR["sample_anchor_location()<br/>Choose position type"]
        GET_POLY["get_top_down_poly()<br/>Calculate footprint"]
        ADD_MARGIN["add_margin_to_top_down_poly()<br/>Add spacing"]
    end
    
    subgraph "Collision Management"
        SUBTRACT["polygon.subtract()<br/>Remove occupied space"]
        INTERSECT["polygon.intersects()<br/>Check collisions"]
        CONTAINS["polygon.contains()<br/>Validate placement"]
    end
    
    ORTHO --> ROOM_POLY
    ORTHO --> OPEN_POLY
    OPEN_POLY --> RECTS
    
    RECTS --> SAMPLE_RECT
    SAMPLE_RECT --> SAMPLE_ANCHOR
    SAMPLE_ANCHOR --> GET_POLY
    GET_POLY --> ADD_MARGIN
    
    ADD_MARGIN --> SUBTRACT
    POLY --> INTERSECT
    POLY --> CONTAINS
    
    BBOX --> GET_POLY
    VEC3 --> GET_POLY
```

**Sources:** [procthor/generation/objects.py:235-343](), [procthor/generation/objects.py:504-595]()

## Geometric Primitives

### OrthogonalPolygon

The `OrthogonalPolygon` class wraps a Shapely polygon and provides operations optimized for axis-aligned rectangular spaces. It maintains cached lists of unique x and z coordinates that form the grid lines of the room.

```mermaid
classDiagram
    class OrthogonalPolygon {
        +Polygon polygon
        +List~float~ xs
        +List~float~ zs
        +List~float~ unique_xs
        +List~float~ unique_zs
        +Dict x_edges_map
        +Dict z_edges_map
        
        +get_neighboring_rectangles() Set~Tuple~
        +get_all_rectangles() Set~Tuple~
        +is_point_inside(point) bool
        +subtract(polygon) None
        
        +get_top_down_poly(anchor_location, anchor_delta, asset_bb, rotated) List~Tuple~
        +add_margin_to_top_down_poly(poly, rotation, anchor_type) Sequence~Tuple~
    }
    
    class ProceduralRoom {
        +OrthogonalPolygon room_polygon
        +OrthogonalPolygon open_polygon
        +List~Asset~ assets
        +Set~Tuple~ last_rectangles
        
        +add_asset(asset) None
        +sample_next_rectangle(choose_largest_rectangle, cache_rectangles) Optional~Tuple~
        +sample_anchor_location(rectangle) Tuple
    }
    
    ProceduralRoom --> OrthogonalPolygon : contains
```

The class decomposes complex room shapes into collections of non-overlapping axis-aligned rectangles. This decomposition enables efficient sampling of placement locations weighted by available area.

**Key Operations:**
- **get_neighboring_rectangles()**: Returns the minimal set of rectangles formed by the grid of unique x and z coordinates ([procthor/generation/objects.py:280-290]())
- **_join_neighboring_rectangles()**: Merges adjacent rectangles to create larger placement zones ([procthor/generation/objects.py:292-312]())
- **get_all_rectangles()**: Iteratively joins rectangles until no more merging is possible ([procthor/generation/objects.py:314-322]())

**Sources:** [procthor/generation/objects.py:235-343]()

### Asset Footprints

Assets and asset groups maintain multiple polygon representations:

| Attribute | Purpose | Includes Padding | Includes Margin |
|-----------|---------|------------------|-----------------|
| `top_down_poly` | Base footprint | ✓ | ✗ |
| `top_down_poly_with_margin` | Collision boundary | ✓ | ✓ |
| `poly_xs`, `poly_zs` | Cached coordinates for base | ✓ | ✗ |
| `margined_poly_xs`, `margined_poly_zs` | Cached coordinates for collision | ✓ | ✓ |

```mermaid
graph LR
    subgraph "Asset Polygon Representations"
        BASE["Base Asset<br/>Bounding Box"]
        PADDED["top_down_poly<br/>+ PADDING_AGAINST_WALL"]
        MARGINED["top_down_poly_with_margin<br/>+ anchor-specific MARGIN"]
    end
    
    BASE --> PADDED
    PADDED --> MARGINED
    
    MARGINED --> SUBTRACT["Subtracted from<br/>open_polygon"]
```

**Sources:** [procthor/generation/objects.py:88-145](), [procthor/generation/objects.py:147-233]()

### Wall Space Representation

Wall objects use `LineString` and `MultiLineString` from Shapely to represent available wall segments:

```mermaid
graph TB
    subgraph "Wall Space Evolution"
        BOUNDARY["BoundaryGroups<br/>Room-to-room boundaries"]
        MULTI["MultiLineString<br/>Per-room wall segments"]
        WALL_MAP["room_to_wall_to_string<br/>Dict[room_id, Dict[wall_id, LineString]]"]
        DF["rooms_lines_df_map<br/>DataFrame with wall segments"]
    end
    
    BOUNDARY --> MULTI
    MULTI --> WALL_MAP
    WALL_MAP --> SUBTRACT_ASSETS["subtract_wall_assets()<br/>Remove blocked segments"]
    WALL_MAP --> SUBTRACT_DOORS["subtract_doors_and_windows()<br/>Remove openings"]
    SUBTRACT_ASSETS --> CONVERT["convert_multi_lines_to_single_lines()"]
    SUBTRACT_DOORS --> CONVERT
    CONVERT --> DF
```

**Sources:** [procthor/generation/wall_objects.py:81-113](), [procthor/generation/wall_objects.py:170-188]()

## Rectangle Sampling and Anchoring

### Rectangle Selection

The `sample_next_rectangle()` method selects a placement zone from available rectangles using a hybrid strategy:

```mermaid
graph TD
    START["sample_next_rectangle()"]
    CACHE{"cache_rectangles?"}
    GET_CACHED["Use last_rectangles"]
    GET_ALL["open_polygon.get_all_rectangles()"]
    
    EMPTY{"len(rectangles) == 0?"}
    RETURN_NONE["return None"]
    
    PROB{"random() < P_LARGEST_RECTANGLE?"}
    CHOOSE_LARGEST["Select rectangle<br/>with max area"]
    CHOOSE_WEIGHTED["random.choices()<br/>weighted by area"]
    
    FILTER["Filter rectangles where<br/>both sides >= MIN_RECTANGLE_SIDE_SIZE"]
    
    START --> CACHE
    CACHE -->|Yes| GET_CACHED
    CACHE -->|No| GET_ALL
    GET_CACHED --> EMPTY
    GET_ALL --> EMPTY
    
    EMPTY -->|Yes| RETURN_NONE
    EMPTY -->|No| PROB
    
    PROB -->|Yes, 0.8| CHOOSE_LARGEST
    PROB -->|No, 0.2| FILTER
    FILTER --> CHOOSE_WEIGHTED
    
    CHOOSE_LARGEST --> RETURN["return rectangle"]
    CHOOSE_WEIGHTED --> RETURN
```

**Configuration Constants:**
- `P_LARGEST_RECTANGLE = 0.8`: Probability of choosing the largest available rectangle ([procthor/constants.py]())
- `MIN_RECTANGLE_SIDE_SIZE`: Minimum dimension for valid rectangles ([procthor/constants.py]())

**Sources:** [procthor/generation/objects.py:550-594]()

### Anchor Delta System

The anchor delta system defines 9 possible placement positions relative to a reference point, numbered 0-8:

```
    0   1   2
        |
    3 - 4 - 5
        |
    6   7   8
```

Each anchor delta specifies both the reference point direction and the object's rotation:

```mermaid
graph TB
    subgraph "Anchor Delta 0 (Top-Left)"
        A0_REF["Reference: (x, z)"]
        A0_OBJ["Object extends<br/>down and left"]
        A0_ROT["Rotation: 0° or 270°"]
    end
    
    subgraph "Anchor Delta 1 (Top-Center)"
        A1_REF["Reference: (x, z)"]
        A1_OBJ["Object extends<br/>down, centered on x"]
        A1_ROT["Rotation: 0°"]
    end
    
    subgraph "Anchor Delta 4 (Center)"
        A4_REF["Reference: rectangle"]
        A4_OBJ["Object placed<br/>anywhere in rectangle"]
        A4_ROT["Rotation: random"]
    end
```

The `get_top_down_poly()` static method calculates the asset footprint based on anchor delta:

**Sources:** [procthor/generation/objects.py:411-501]()

### Anchor Type Selection

The `sample_anchor_location()` method determines the anchor type by analyzing the rectangle's relationship to the room boundary:

```mermaid
graph TD
    START["sample_anchor_location(rectangle)"]
    
    CHECK_CORNERS["Check each corner<br/>with epsilon offset"]
    CORNER_LOGIC["Count quadrants<br/>inside room boundary"]
    
    CORNER_FOUND{"Found corner?"}
    RETURN_CORNER["return (x, z, anchor_delta, 'inCorner')"]
    
    CHECK_EDGES["Check each edge<br/>against room boundary"]
    EDGE_IN_ROOM{"Edge contained in<br/>room outer boundary?"}
    EDGE_FOUND{"Found edge?"}
    
    PROB_EDGE{"random() < P_CHOOSE_EDGE?"}
    RETURN_EDGE["return (xs, zs, anchor_delta, 'onEdge')"]
    
    RETURN_MIDDLE["return (None, None, 4, 'inMiddle')"]
    
    START --> CHECK_CORNERS
    CHECK_CORNERS --> CORNER_LOGIC
    CORNER_LOGIC --> CORNER_FOUND
    
    CORNER_FOUND -->|Yes| RETURN_CORNER
    CORNER_FOUND -->|No| CHECK_EDGES
    
    CHECK_EDGES --> EDGE_IN_ROOM
    EDGE_IN_ROOM --> EDGE_FOUND
    
    EDGE_FOUND -->|Yes| PROB_EDGE
    EDGE_FOUND -->|No| RETURN_MIDDLE
    
    PROB_EDGE -->|Yes, 0.7| RETURN_EDGE
    PROB_EDGE -->|No, 0.3| RETURN_MIDDLE
```

**Corner Detection Logic**: A point is a corner if it has exactly 1 or 2 adjacent quadrants inside the room boundary ([procthor/generation/objects.py:862-878]())

**Sources:** [procthor/generation/objects.py:817-899](), [procthor/constants.py]()

## Collision Avoidance

### Margin Calculation

Margins define minimum spacing between objects and vary by anchor type:

```mermaid
graph TB
    subgraph "Margin Configuration"
        CORNER["MARGIN['corner']<br/>front: 0.2<br/>back: 0.05<br/>sides: 0.05"]
        EDGE["MARGIN['edge']<br/>front: 0.2<br/>back: 0.05<br/>sides: 0.15"]
        MIDDLE["MARGIN['middle']<br/>all sides: 0.15"]
    end
    
    subgraph "Application by Rotation"
        ROT0["rotation=0<br/>front → +z<br/>back → -z"]
        ROT90["rotation=90<br/>front → +x<br/>back → -x"]
        ROT180["rotation=180<br/>front → -z<br/>back → +z"]
        ROT270["rotation=270<br/>front → -x<br/>back → +x"]
    end
    
    CORNER --> ROT0
    EDGE --> ROT0
    MIDDLE --> ROT0
    
    CORNER --> ROT90
    EDGE --> ROT90
    MIDDLE --> ROT90
    
    CORNER --> ROT180
    EDGE --> ROT180
    MIDDLE --> ROT180
    
    CORNER --> ROT270
    EDGE --> ROT270
    MIDDLE --> ROT270
```

The `add_margin_to_top_down_poly()` method expands the base polygon by the appropriate margin values based on rotation and anchor type ([procthor/generation/objects.py:346-408]()).

**Key Constant:**
- `PADDING_AGAINST_WALL`: Additional padding when objects are against walls ([procthor/constants.py]())

**Sources:** [procthor/generation/objects.py:346-408](), [procthor/constants.py]()

### Polygon Subtraction for Floor Objects

The collision avoidance workflow for floor objects uses progressive polygon subtraction:

```mermaid
sequenceDiagram
    participant R as ProceduralRoom
    participant OP as open_polygon
    participant A as Asset/AssetGroup
    
    R->>OP: get_all_rectangles()
    OP-->>R: Set[rectangle]
    
    R->>R: sample_next_rectangle()
    R->>R: sample_anchor_location(rectangle)
    R->>R: sample_and_add_floor_asset()
    
    Note over R: Asset placement chosen
    
    R->>A: Create Asset with<br/>top_down_poly_with_margin
    R->>R: add_asset(asset)
    R->>OP: subtract(Polygon(asset.top_down_poly_with_margin))
    
    Note over OP: Available space reduced
    
    R->>OP: get_all_rectangles()
    Note over OP: New rectangles exclude<br/>placed asset's margin
```

The `open_polygon` is maintained as a `MultiPolygon` after subtractions, and the rectangle extraction process automatically accounts for the reduced available space.

**Sources:** [procthor/generation/objects.py:542-548](), [procthor/generation/objects.py:338-340]()

### Wall Space Subtraction

Wall object placement uses `LineString` subtraction to track available wall segments:

```mermaid
graph TB
    START["Initial wall LineStrings<br/>from boundary_groups"]
    
    SUB_ASSETS["subtract_wall_assets()"]
    SUB_DOORS["subtract_doors_and_windows()"]
    
    CONVERT["convert_multi_lines_to_single_lines()"]
    
    CREATE_DF["get_line_string_df_map()<br/>Create DataFrame per room"]
    
    PLACE["Place window/painting/TV"]
    
    UPDATE["LineString -= Polygon(asset_poly)"]
    
    MULTI{"Result is<br/>MultiLineString?"}
    
    SPLIT["Split into individual<br/>LineStrings"]
    ADD_BACK["Add non-empty segments<br/>back to DataFrame"]
    
    START --> SUB_ASSETS
    SUB_ASSETS --> SUB_DOORS
    SUB_DOORS --> CONVERT
    CONVERT --> CREATE_DF
    
    CREATE_DF --> PLACE
    PLACE --> UPDATE
    UPDATE --> MULTI
    
    MULTI -->|Yes| SPLIT
    MULTI -->|No| ADD_BACK
    SPLIT --> ADD_BACK
    ADD_BACK --> PLACE
```

**Key Functions:**
- `subtract_wall_assets()`: Removes wall segments behind floor objects taller than `min_height` ([procthor/generation/wall_objects.py:191-262]())
- `subtract_doors_and_windows()`: Removes segments occupied by doors and windows ([procthor/generation/wall_objects.py:494-613]())
- `add_padding_to_poly()`: Adds `POLYGON_PADDING` to avoid floating-point comparison issues ([procthor/generation/wall_objects.py:41-58]())

**Sources:** [procthor/generation/wall_objects.py:191-262](), [procthor/generation/wall_objects.py:494-613](), [procthor/generation/wall_objects.py:265-281]()

### Collision Retry Logic

Asset groups may have internal collisions between objects. The placement system retries up to `MAX_INTERSECTING_OBJECT_RETRIES` times:

```mermaid
graph TD
    START["place_asset_group()"]
    INIT["retries = 0"]
    
    SAMPLE["asset_group_generator.sample_object_placement()"]
    CHECK["get_intersecting_objects()"]
    
    COLLISION{"any_collisions?"}
    
    INCREMENT["retries += 1"]
    MAX{"retries >= MAX_INTERSECTING_OBJECT_RETRIES?"}
    
    RETURN_NONE["return None"]
    RETURN_ASSET["return ChosenAssetGroup"]
    
    START --> INIT
    INIT --> SAMPLE
    SAMPLE --> CHECK
    CHECK --> COLLISION
    
    COLLISION -->|Yes| INCREMENT
    INCREMENT --> MAX
    MAX -->|Yes| RETURN_NONE
    MAX -->|No| SAMPLE
    
    COLLISION -->|No| RETURN_ASSET
```

**Constant:** `MAX_INTERSECTING_OBJECT_RETRIES = 5` ([procthor/constants.py]())

**Sources:** [procthor/generation/objects.py:752-795](), [procthor/constants.py]()

## Wall Space Management

### Boundary Extraction

The `get_boundary_strings()` function extracts wall segments from room boundaries:

```mermaid
graph TB
    BG["boundary_groups<br/>Dict[(room0_id, room1_id), BoundaryGroups]"]
    
    FILTER["Filter by:<br/>- from_room_types<br/>- only_connected_to_outside"]
    
    COLLECT["Collect LineStrings<br/>for each room_id"]
    
    MULTI["Create MultiLineString<br/>per room"]
    
    OUTPUT["Dict[room_id, MultiLineString]"]
    
    BG --> FILTER
    FILTER --> COLLECT
    COLLECT --> MULTI
    MULTI --> OUTPUT
```

**Parameters:**
- `from_room_types`: Set of room types to include (e.g., `{"Bedroom", "Kitchen", "LivingRoom"}`)
- `only_connected_to_outside`: If `True`, only include boundaries where one room is `OUTDOOR_ROOM_ID`

**Sources:** [procthor/generation/wall_objects.py:81-113]()

### Wall ID Generation

Each wall segment is assigned a unique identifier based on its spatial coordinates:

```
wall|{room_id}|{min_x:.2f}|{min_z:.2f}|{max_x:.2f}|{max_z:.2f}
```

This identifier is stable across processing steps and enables tracking which walls have had objects placed on them.

**Sources:** [procthor/generation/wall_objects.py:170-188]()

### Wall Object Height Tracking

For wall objects that can stack vertically (e.g., painting above a short table), the system maintains height information:

```mermaid
classDiagram
    class WallObjectHeight {
        +Polygon poly
        +float height
    }
    
    class sample_asset_y_position {
        +float asset_height
        +List~WallObjectHeight~ wall_object_heights
        +Polygon asset_top_down_poly
        +float ceiling_height
        returns (min_y, max_y)
    }
    
    WallObjectHeight --> sample_asset_y_position : input
```

The `sample_asset_y_position()` function:
1. Finds the maximum height of any object below the asset's footprint
2. Calculates available vertical space between that height and `min(ceiling_height, MAX_CENTER_Y_HEIGHT)`
3. Samples a y-position using a beta distribution for visual variety

**Configuration:**
- `MAX_CENTER_Y_HEIGHT = 3.0`: Clips vertical centering for tall rooms ([procthor/generation/wall_objects.py:27-32]())
- `BETA_A = 12`, `BETA_B = 12`: Beta distribution parameters for centered sampling ([procthor/generation/wall_objects.py:34-38]())
- `NO_PAINTINGS_ABOVE_ASSETS_OF_HEIGHT = 1.15`: Minimum height to block painting placement ([procthor/generation/wall_objects.py:481-482]())

**Sources:** [procthor/generation/wall_objects.py:128-158](), [procthor/generation/wall_objects.py:191-262]()

### DataFrame-Based Wall Segment Management

Wall segments are converted to pandas DataFrames for efficient filtering and sampling:

```mermaid
graph LR
    LINESTRING["LineString objects"]
    DF["DataFrame with columns:<br/>- length<br/>- x1, x2, z1, z2<br/>- lineString<br/>- wallId"]
    
    FILTER["filter_room_lines_df()<br/>length > min_asset_size"]
    
    SAMPLE["random.choices()<br/>weighted by length"]
    
    LINESTRING --> DF
    DF --> FILTER
    FILTER --> SAMPLE
```

This approach enables:
- Efficient filtering by minimum size requirements
- Weighted random sampling proportional to wall segment length
- Fast lookups by wall ID

**Sources:** [procthor/generation/wall_objects.py:283-311](), [procthor/generation/wall_objects.py:314-322]()

## Placement Position Calculation

### Floor Object Position

The `sample_place_asset_in_rectangle()` method calculates the final 3D position:

```mermaid
graph TD
    INPUT["Inputs:<br/>- asset (sizes)<br/>- rectangle<br/>- anchor_type<br/>- anchor_delta<br/>- x_info, z_info"]
    
    CALC_BB["Calculate effective<br/>bounding box (bb)<br/>considering rotation"]
    
    ANCHOR_TYPE{"anchor_type?"}
    
    CORNER["'inCorner'<br/>x, z = x_info, z_info<br/>rotation from anchor_delta"]
    
    EDGE["'onEdge'<br/>Randomize along edge<br/>rotation perpendicular to edge"]
    
    MIDDLE["'inMiddle'<br/>Random (x, z) in rectangle<br/>random rotation"]
    
    GET_POLY["get_top_down_poly()<br/>Calculate footprint polygon"]
    
    CENTER["center_x = mean(poly x)<br/>center_z = mean(poly z)"]
    
    ADD_MARGIN["add_margin_to_top_down_poly()"]
    
    CREATE["Create Asset/AssetGroup<br/>with calculated position"]
    
    INPUT --> CALC_BB
    CALC_BB --> ANCHOR_TYPE
    
    ANCHOR_TYPE --> CORNER
    ANCHOR_TYPE --> EDGE
    ANCHOR_TYPE --> MIDDLE
    
    CORNER --> GET_POLY
    EDGE --> GET_POLY
    MIDDLE --> GET_POLY
    
    GET_POLY --> CENTER
    CENTER --> ADD_MARGIN
    ADD_MARGIN --> CREATE
```

**Key Insight:** The position calculation separates the anchor point calculation (which varies by anchor type) from the footprint geometry calculation (which is standardized via `get_top_down_poly()`).

**Sources:** [procthor/generation/objects.py:596-739]()

### Wall Object Position

The `get_wall_placement_info()` function calculates placement data for wall objects:

```mermaid
graph TB
    INPUT["Inputs:<br/>- wall_poly<br/>- room_line (DataFrame row)<br/>- asset (DataFrame row)<br/>- start_position"]
    
    CHECK_AXIS{"Wall parallel<br/>to x or z?"}
    
    X_AXIS["Parallel to x-axis<br/>- centerX from start_position<br/>- centerZ based on wall normal<br/>- rotation: 0° or 180°"]
    
    Z_AXIS["Parallel to z-axis<br/>- centerZ from start_position<br/>- centerX based on wall normal<br/>- rotation: 90° or 270°"]
    
    CREATE_POLY["Create asset_poly<br/>with POLYGON_PADDING"]
    
    OUTPUT["Return:<br/>- poly<br/>- rotation<br/>- centerX<br/>- centerZ"]
    
    INPUT --> CHECK_AXIS
    CHECK_AXIS --> X_AXIS
    CHECK_AXIS --> Z_AXIS
    
    X_AXIS --> CREATE_POLY
    Z_AXIS --> CREATE_POLY
    
    CREATE_POLY --> OUTPUT
```

The rotation is determined by the wall polygon's point order, ensuring objects face into the room:
- Wall points increasing in z → rotation 90° (object extends +x)
- Wall points decreasing in z → rotation 270° (object extends -x)
- Wall points increasing in x → rotation 180° (object extends -z)
- Wall points decreasing in x → rotation 0° (object extends +z)

**Wall Padding:** `PAINTING_WALL_PADDING = 5e-3` prevents z-fighting by slightly offsetting objects from the wall surface ([procthor/generation/wall_objects.py:478-479]()).

**Sources:** [procthor/generation/wall_objects.py:615-710]()

## Integration with Generation Pipeline

The spatial reasoning systems are invoked at multiple stages:

```mermaid
graph TB
    STRUCT["Stage: Structure Generation<br/>Creates initial room polygons"]
    
    DOORS["Stage: Door Placement<br/>door_polygons created"]
    
    ROOMS["Stage: Room Setup<br/>ProceduralRoom initialized<br/>- room_polygon<br/>- open_polygon<br/>- door_polygons subtracted"]
    
    FLOOR["Stage: Floor Objects<br/>- sample_next_rectangle()<br/>- sample_anchor_location()<br/>- get_top_down_poly()<br/>- add_margin_to_top_down_poly()<br/>- open_polygon.subtract()"]
    
    WALL["Stage: Wall Objects<br/>- get_boundary_strings()<br/>- subtract_wall_assets()<br/>- subtract_doors_and_windows()<br/>- LineString operations"]
    
    STRUCT --> DOORS
    DOORS --> ROOMS
    ROOMS --> FLOOR
    FLOOR --> WALL
```

**Sources:** [procthor/generation/objects.py:1157-1188](), [procthor/generation/objects.py:1191-1304](), [procthor/generation/wall_objects.py:1041-1084]()

---

