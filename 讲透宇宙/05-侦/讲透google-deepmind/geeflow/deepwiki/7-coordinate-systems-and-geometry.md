<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/geeflow · page 7 Coordinate Systems and Geometry · fetched 2026-10-26 -->

# Coordinate Systems and Geometry

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [geeflow/coords.py](geeflow/coords.py)
- [geeflow/coords_test.py](geeflow/coords_test.py)
- [geeflow/ee_data_test.py](geeflow/ee_data_test.py)

</details>



This document explains the coordinate systems and geometric operations used throughout GeoFlow. The primary focus is on the Universal Transverse Mercator (UTM) grid mapping system implemented in the `UtmGridMapping` class, which handles coordinate transformations, spatial projections, and integration with Google Earth Engine geometries.

For information about Earth Engine datasets and their spatial properties, see [Earth Engine Datasets](#5.1). For details about data processing algorithms that use these coordinate systems, see [Data Processing Algorithms](#5.2).

## UTM Grid System Overview

GeoFlow uses the Universal Transverse Mercator (UTM) coordinate system as its primary spatial reference system. UTM divides the Earth into 60 longitudinal zones, each 6 degrees wide, with separate projections for northern and southern hemispheres.

**UTM Grid System Architecture**

```mermaid
graph TB
    subgraph "World Coordinates"
        LATLON["Latitude/Longitude<br/>(WGS84)"]
    end
    
    subgraph "UTM Projection"
        UTMZONE["UTM Zone<br/>(e.g., '18N', '10C')"]
        EASTING["Easting (X)<br/>Meters"]
        NORTHING["Northing (Y)<br/>Meters"]
    end
    
    subgraph "Grid Mapping"
        CELLSIZE["cell_size<br/>Pixel resolution"]
        GRIDCELLS["Grid Cells<br/>(width × height)"]
        BBOX["Bounding Box<br/>(utm_x_min, utm_y_min)"]
    end
    
    subgraph "Output Systems"
        EEPSG["EPSG Code<br/>(e.g., EPSG:32618)"]
        EEGEOM["Earth Engine<br/>Geometry"]
        SHAPELY["Shapely<br/>Polygon"]
    end
    
    LATLON --> UTMZONE
    UTMZONE --> EASTING
    UTMZONE --> NORTHING
    
    EASTING --> CELLSIZE
    NORTHING --> CELLSIZE
    CELLSIZE --> GRIDCELLS
    GRIDCELLS --> BBOX
    
    BBOX --> EEPSG
    BBOX --> EEGEOM
    BBOX --> SHAPELY
```

Sources: [geeflow/coords.py:40-172]()

## UtmGridMapping Class

The `UtmGridMapping` class is the core component for handling coordinate transformations and spatial projections in GeoFlow. It manages the conversion between world coordinates (latitude/longitude) and projected pixel coordinates in UTM space.

**UtmGridMapping Class Structure**

```mermaid
classDiagram
    class UtmGridMapping {
        +str utm_zone
        +float cell_size
        +int|ndarray width
        +int|ndarray height
        +float utm_x_min
        +float utm_y_min
        
        +from_bbox(utm_zone, cell_size, bbox) UtmGridMapping
        +from_latlon_center(lat, lon, cell_size, width, height) UtmGridMapping
        +rescale(cell_size) UtmGridMapping
        
        +grid_cell_size() float
        +epsg() str
        +crs() tuple
        +centroid() tuple
        +centroid_latlon() tuple
        +bbox() tuple
        +bbox_latlon() tuple
        
        +to_ee_point(utm) ee.geometry.Geometry
        +to_ee(utm) ee.Geometry
        +to_ee_bbox() ee.Geometry
        +to_shapely_polygon() shapely.geometry.Polygon
    }
    
    class "External Libraries" {
        <<interface>>
        utm_lib
        ee
        shapely.geometry
        numpy
    }
    
    UtmGridMapping --> "External Libraries"
```

The class provides three main construction methods:

| Method | Purpose | Parameters |
|--------|---------|------------|
| `from_bbox` | Create from UTM bounding box | `utm_zone`, `cell_size`, `bbox` |
| `from_latlon_center` | Create from lat/lon center point | `lat`, `lon`, `cell_size`, `width`, `height` |
| Direct constructor | Create with explicit UTM parameters | All UTM parameters directly |

Sources: [geeflow/coords.py:39-76]()

## Coordinate Transformations

The coordinate transformation system handles conversions between different spatial reference systems used throughout GeoFlow's processing pipeline.

**Coordinate Transformation Flow**

```mermaid
flowchart TD
    subgraph "Input Coordinates"
        LAT["Latitude"]
        LON["Longitude"]
        BBOX_LATLON["LatLon BBox<br/>(south, west, north, east)"]
    end
    
    subgraph "UTM Conversion"
        UTM_LIB["utm_lib.from_latlon()"]
        ZONE_CALC["Zone Calculation<br/>zone_number + zone_letter"]
    end
    
    subgraph "Grid Mapping"
        CELL_ALIGN["Cell Alignment<br/>round(coord / cell_size) * cell_size"]
        GRID_CALC["Grid Calculation<br/>width = (x1 - x0) / cell_size"]
    end
    
    subgraph "Output Formats"
        UTM_COORDS["UTM Coordinates<br/>(easting, northing)"]
        EPSG_CODE["EPSG Code<br/>EPSG:32{6|7}{zone:02}"]
        CRS_TRANSFORM["CRS Transform<br/>(x_scale, x_shear, x_trans, y_shear, y_scale, y_trans)"]
    end
    
    LAT --> UTM_LIB
    LON --> UTM_LIB
    UTM_LIB --> ZONE_CALC
    
    ZONE_CALC --> CELL_ALIGN
    CELL_ALIGN --> GRID_CALC
    
    GRID_CALC --> UTM_COORDS
    UTM_COORDS --> EPSG_CODE
    UTM_COORDS --> CRS_TRANSFORM
    
    BBOX_LATLON --> UTM_LIB
```

### EPSG Code Generation

The system automatically generates EPSG codes based on UTM zone information:

```python
# Northern hemisphere: EPSG:326XX
# Southern hemisphere: EPSG:327XX
# Where XX is the zero-padded zone number
```

The logic implemented in `epsg` property:
- Northern hemisphere zones (N-Z): EPSG:326XX
- Southern hemisphere zones (A-M): EPSG:327XX

Sources: [geeflow/coords.py:83-86](), [geeflow/coords.py:72-76](), [geeflow/coords.py:89-97]()

## Earth Engine Integration

GeoFlow integrates UTM grid mappings with Google Earth Engine geometry objects for spatial queries and data extraction.

**Earth Engine Geometry Integration**

```mermaid
graph TB
    subgraph "UtmGridMapping Methods"
        TO_EE_POINT["to_ee_point(utm=False)"]
        TO_EE["to_ee(utm=False)"]
        TO_EE_BBOX["to_ee_bbox()"]
    end
    
    subgraph "Earth Engine Geometries"
        EE_POINT["ee.Geometry.Point"]
        EE_RECTANGLE["ee.Geometry.Rectangle"]
        EE_BBOX["ee.Geometry.BBox"]
    end
    
    subgraph "Coordinate Options"
        LATLON_MODE["LatLon Mode<br/>(default)"]
        UTM_MODE["UTM Mode<br/>(with EPSG projection)"]
    end
    
    TO_EE_POINT --> EE_POINT
    TO_EE --> EE_RECTANGLE
    TO_EE_BBOX --> EE_BBOX
    
    TO_EE_POINT --> LATLON_MODE
    TO_EE_POINT --> UTM_MODE
    TO_EE --> LATLON_MODE
    TO_EE --> UTM_MODE
    
    EE_POINT --> LATLON_MODE
    EE_RECTANGLE --> LATLON_MODE
    EE_RECTANGLE --> UTM_MODE
    EE_BBOX --> LATLON_MODE
```

### Geometry Conversion Methods

| Method | Output Type | Coordinate System | Usage |
|--------|-------------|-------------------|-------|
| `to_ee_point(utm=False)` | `ee.Geometry.Point` | LatLon or UTM | Point-based queries |
| `to_ee(utm=False)` | `ee.Geometry.Rectangle` | LatLon or UTM | Area-based queries |
| `to_ee_bbox()` | `ee.Geometry.BBox` | LatLon only | Bounding box queries |

Sources: [geeflow/coords.py:147-171]()

## Geometric Operations

The system provides integration with Shapely for advanced geometric operations and spatial analysis.

**Shapely Integration**

```mermaid
graph LR
    subgraph "UtmGridMapping"
        BBOX_LATLON_PROP["bbox_latlon property"]
        TO_SHAPELY["to_shapely_polygon()"]
    end
    
    subgraph "Coordinate Extraction"
        SOUTH["south (y0)"]
        WEST["west (x0)"]
        NORTH["north (y1)"]
        EAST["east (x1)"]
    end
    
    subgraph "Shapely Output"
        POLYGON["shapely.geometry.Polygon"]
        VERTICES["Polygon Vertices<br/>[[x0,y0], [x0,y1], [x1,y1], [x1,y0]]"]
    end
    
    BBOX_LATLON_PROP --> SOUTH
    BBOX_LATLON_PROP --> WEST
    BBOX_LATLON_PROP --> NORTH
    BBOX_LATLON_PROP --> EAST
    
    TO_SHAPELY --> SOUTH
    TO_SHAPELY --> WEST
    TO_SHAPELY --> NORTH
    TO_SHAPELY --> EAST
    
    SOUTH --> VERTICES
    WEST --> VERTICES
    NORTH --> VERTICES
    EAST --> VERTICES
    
    VERTICES --> POLYGON
```

### Bounding Box Calculations

The system provides multiple bounding box representations:

| Property | Coordinate System | Format | Usage |
|----------|-------------------|--------|-------|
| `bbox` | UTM | `(x0, y0, x1, y1)` | UTM-based calculations |
| `bbox_latlon` | LatLon | `(south, west, north, east)` | Geographic queries |
| `centroid` | UTM | `(x, y)` | UTM center point |
| `centroid_latlon` | LatLon | `(lat, lon)` | Geographic center point |

Sources: [geeflow/coords.py:112-134](), [geeflow/coords.py:168-171]()

## Grid Rescaling and Pixel Alignment

The `UtmGridMapping` class supports rescaling operations to change pixel resolution while maintaining spatial alignment.

**Grid Rescaling Process**

```mermaid
flowchart TD
    subgraph "Original Grid"
        ORIG_CELL["Original cell_size"]
        ORIG_WIDTH["Original width"]
        ORIG_HEIGHT["Original height"]
        ORIG_BOUNDS["Original bounds<br/>(utm_x_min, utm_y_min)"]
    end
    
    subgraph "Rescaling Operation"
        NEW_CELL["New cell_size"]
        SCALE_FACTOR["Scale Factor<br/>old_size / new_size"]
        ALIGNMENT["Pixel Alignment<br/>round(coord / new_size) * new_size"]
    end
    
    subgraph "Rescaled Grid"
        NEW_WIDTH["New width<br/>old_width * scale_factor"]
        NEW_HEIGHT["New height<br/>old_height * scale_factor"]
        NEW_BOUNDS["Aligned bounds<br/>Rounded to new cell size"]
    end
    
    ORIG_CELL --> SCALE_FACTOR
    NEW_CELL --> SCALE_FACTOR
    SCALE_FACTOR --> NEW_WIDTH
    SCALE_FACTOR --> NEW_HEIGHT
    
    ORIG_WIDTH --> NEW_WIDTH
    ORIG_HEIGHT --> NEW_HEIGHT
    ORIG_BOUNDS --> ALIGNMENT
    ALIGNMENT --> NEW_BOUNDS
```

The `rescale` method ensures that:
- New grid dimensions are calculated proportionally
- Pixel boundaries remain aligned to the new cell size
- UTM coordinates are rounded to maintain grid consistency

Sources: [geeflow/coords.py:136-145](), [geeflow/coords.py:54-56]()

## Utility Functions

The coordinate system includes utility functions for common spatial operations.

### Region of Interest (ROI) Generation

The `get_lat_lon_roi` function creates Earth Engine geometry objects for spatial queries:

```python
def get_lat_lon_roi(lat, lon, width_m=None, width_deg=None):
    # Creates ee.Geometry.Rectangle centered on lat/lon
    # with specified width in meters or degrees
```

**ROI Generation Process**

```mermaid
graph LR
    subgraph "Input Parameters"
        LAT_IN["Latitude"]
        LON_IN["Longitude"]
        WIDTH_M["Width (meters)"]
        WIDTH_DEG["Width (degrees)"]
    end
    
    subgraph "Conversion"
        DEG_CONV["Degree Conversion<br/>width_m / DEG_AT_EQUATOR_IN_M"]
        DELTA_CALC["Delta Calculation<br/>width_deg / 2"]
    end
    
    subgraph "Output"
        EE_RECT["ee.Geometry.Rectangle<br/>[lon-δ, lat-δ, lon+δ, lat+δ]"]
    end
    
    WIDTH_M --> DEG_CONV
    WIDTH_DEG --> DEG_CONV
    DEG_CONV --> DELTA_CALC
    
    LAT_IN --> EE_RECT
    LON_IN --> EE_RECT
    DELTA_CALC --> EE_RECT
```

The constant `DEG_AT_EQUATOR_IN_M = 111_111.111` represents the approximate meters per degree at the equator.

Sources: [geeflow/coords.py:31-36](), [geeflow/coords.py:28]()

---

