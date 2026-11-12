<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/geeflow · page 8 Utilities and Helpers · fetched 2026-10-26 -->

# Utilities and Helpers

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [geeflow/times.py](geeflow/times.py)
- [geeflow/utils.py](geeflow/utils.py)

</details>



This document provides an overview of the utility modules that support GeoFlow's core functionality. The utilities are organized into two main categories: general-purpose utilities for configuration, data conversion, and Earth Engine integration, and specialized time/date handling utilities for temporal data processing.

For detailed information about time and date utilities, see [Time and Date Utilities](#8.1). For detailed information about general utilities, see [General Utilities](#8.2).

## Purpose and Integration

The utility modules in GeoFlow serve as foundational support layers for the main processing pipelines and data handling operations. They provide essential services including Earth Engine initialization, configuration argument parsing, coordinate system calculations, data type conversions, and comprehensive time/date management.

### System Integration Overview

```mermaid
graph TB
    subgraph "Main Pipelines"
        EXPORT["export_beam_tfds.py<br/>Dataset Export Pipeline"]
        STATS["compute_stats_beam.py<br/>Statistics Pipeline"]
    end
    
    subgraph "Core Processing"
        PIPELINES["pipelines.py<br/>Data Processing"]
        EE_ALGO["ee_algo.py<br/>EE Algorithms"]
        COORDS["coords.py<br/>Coordinate Systems"]
    end
    
    subgraph "Utility Layer"
        UTILS["utils.py<br/>General Utilities"]
        TIMES["times.py<br/>Time/Date Utilities"]
    end
    
    subgraph "External Systems"
        EE["Google Earth Engine"]
        CONFIGS["Configuration Files"]
    end
    
    EXPORT --> UTILS
    STATS --> UTILS
    PIPELINES --> UTILS
    PIPELINES --> TIMES
    EE_ALGO --> TIMES
    COORDS --> UTILS
    COORDS --> TIMES
    
    UTILS --> EE
    UTILS --> CONFIGS
    TIMES --> EE
```

Sources: [geeflow/utils.py:1-228](), [geeflow/times.py:1-145]()

## Core Utility Categories

GeoFlow's utilities are organized into several functional categories that address different aspects of the system's requirements:

| Category | Module | Primary Functions | Usage Context |
|----------|--------|------------------|---------------|
| Configuration | `utils.py` | Argument parsing, type conversion | Pipeline initialization, config processing |
| Earth Engine | `utils.py` | EE initialization, authentication | All EE-dependent operations |
| Data Conversion | `utils.py` | NumPy conversion, type handling | Data processing, statistics |
| Coordinate Math | `utils.py` | UTM grid calculations | Spatial processing, coordinate systems |
| File Operations | `utils.py` | Caching, copying | Data management, temporary storage |
| Time Processing | `times.py` | Date parsing, timezone handling | Temporal data processing |
| Date Ranges | `times.py` | Range generation, calculations | Time series analysis |

### Function Distribution and Dependencies

```mermaid
graph LR
    subgraph "utils.py Functions"
        PARSE["parse_arg()<br/>Configuration Parsing"]
        INIT_EE["initialize_ee()<br/>EE Authentication"]
        TO_NP["to_np()<br/>NumPy Conversion"]
        UTM_GRID["get_utm_grid_size()<br/>UTM Calculations"]
        CACHE["cache_data()<br/>File Caching"]
        CONFIG_SRC["get_source_config()<br/>Config Generation"]
    end
    
    subgraph "times.py Functions"
        DATETIME_CONV["millis_to_datetime()<br/>to_timestr()<br/>to_datestr()"]
        TZ_HANDLING["is_tza()<br/>make_tza()"]
        DATE_RANGES["get_date_ranges()<br/>incremental_date_list()"]
        EE_TIME["date_range_mean()<br/>outer_date_range()"]
    end
    
    subgraph "Usage Patterns"
        CONFIG_PROC["Configuration Processing"]
        SPATIAL_CALC["Spatial Calculations"]
        TEMPORAL_PROC["Temporal Processing"]
        DATA_CONV["Data Conversion"]
    end
    
    PARSE --> CONFIG_PROC
    CONFIG_SRC --> CONFIG_PROC
    
    UTM_GRID --> SPATIAL_CALC
    INIT_EE --> SPATIAL_CALC
    
    DATETIME_CONV --> TEMPORAL_PROC
    DATE_RANGES --> TEMPORAL_PROC
    EE_TIME --> TEMPORAL_PROC
    TZ_HANDLING --> TEMPORAL_PROC
    
    TO_NP --> DATA_CONV
    CACHE --> DATA_CONV
```

Sources: [geeflow/utils.py:35-53](), [geeflow/utils.py:56-61](), [geeflow/utils.py:63-75](), [geeflow/times.py:41-48](), [geeflow/times.py:79-91]()

## Configuration and Type System Support

The utilities provide sophisticated support for configuration management and type conversion, particularly through the `parse_arg` function which enables flexible command-line argument parsing for ML Collections ConfigDict objects.

### Configuration Argument Flow

```mermaid
flowchart TD
    CMD_LINE["Command Line Arguments<br/>--config demo.py:runlocal,res=128"]
    
    PARSE_ARG["parse_arg()<br/>Argument Parser"]
    
    subgraph "Type Processing"
        GET_TYPE["get_type_with_default()<br/>Type Extraction"]
        AUTO_TYPE["autotype()<br/>Auto Conversion"]
        STRICT_BOOL["strict_bool()<br/>Boolean Parsing"]
    end
    
    CONFIG_DICT["mlc.ConfigDict<br/>Structured Configuration"]
    
    subgraph "Config Validation"
        SPEC["Specification Matching"]
        LAZY["Lazy Parsing Option"]
        DEFAULT["Default Values"]
    end
    
    CMD_LINE --> PARSE_ARG
    PARSE_ARG --> GET_TYPE
    PARSE_ARG --> AUTO_TYPE
    GET_TYPE --> STRICT_BOOL
    
    PARSE_ARG --> CONFIG_DICT
    CONFIG_DICT --> SPEC
    CONFIG_DICT --> LAZY
    CONFIG_DICT --> DEFAULT
```

Sources: [geeflow/utils.py:108-181](), [geeflow/utils.py:184-201](), [geeflow/utils.py:203-214]()

## Earth Engine Integration Utilities

The utilities provide essential Earth Engine integration capabilities, including authentication, initialization, and data conversion functions that ensure seamless interaction with Google Earth Engine services.

### Earth Engine Utility Functions

```mermaid
graph TB
    subgraph "EE Integration Points"
        INIT["initialize_ee(ee_project)<br/>Authentication & Setup"]
        TO_NP_FUNC["to_np(x)<br/>EE Data → NumPy"]
        CACHE_FUNC["cache_data(src, dst_dir)<br/>Local Caching"]
    end
    
    subgraph "Data Flow"
        EE_DATA["Earth Engine Data<br/>ee.Image, ee.FeatureCollection"]
        NP_ARRAYS["NumPy Arrays<br/>Processed Data"]
        LOCAL_CACHE["Local File Cache<br/>/tmp/geeflow_cache"]
    end
    
    subgraph "Pipeline Integration"
        EXPORT_PIPELINE["export_beam_tfds.py"]
        STATS_PIPELINE["compute_stats_beam.py"]
        PROCESSING["Data Processing Functions"]
    end
    
    INIT --> EE_DATA
    EE_DATA --> TO_NP_FUNC
    TO_NP_FUNC --> NP_ARRAYS
    
    EE_DATA --> CACHE_FUNC
    CACHE_FUNC --> LOCAL_CACHE
    
    INIT --> EXPORT_PIPELINE
    TO_NP_FUNC --> STATS_PIPELINE
    CACHE_FUNC --> PROCESSING
```

Sources: [geeflow/utils.py:56-61](), [geeflow/utils.py:63-75](), [geeflow/utils.py:77-106]()

## Spatial and Temporal Calculation Support

The utilities provide critical mathematical functions for spatial coordinate calculations and comprehensive temporal data handling, supporting GeoFlow's geospatial processing requirements.

### Coordinate and Time Calculation Integration

```mermaid
graph LR
    subgraph "Spatial Utilities"
        LAT_LON_CONST["LAT_TO_METERS = 111694<br/>LON_TO_METERS = 112000"]
        UTM_CALC["get_utm_grid_size()<br/>Grid Dimension Calculation"]
    end
    
    subgraph "Temporal Utilities"
        TZ_DEFS["UTC, ZRH, PT, ET<br/>Timezone Definitions"]
        DATE_FORMATS["DATE_FORMAT<br/>TIME_FORMAT<br/>TIME_FORMAT_ISO_8601"]
        CONVERSION_FUNCS["millis_to_datetime()<br/>to_timestr()<br/>to_datestr()"]
    end
    
    subgraph "Processing Context"
        COORD_SYS["coords.py<br/>UTM Grid Mapping"]
        PIPELINE_TEMPORAL["Pipeline Temporal Logic"]
        EE_TEMPORAL["Earth Engine Date Ranges"]
    end
    
    LAT_LON_CONST --> UTM_CALC
    UTM_CALC --> COORD_SYS
    
    TZ_DEFS --> CONVERSION_FUNCS
    DATE_FORMATS --> CONVERSION_FUNCS
    CONVERSION_FUNCS --> PIPELINE_TEMPORAL
    CONVERSION_FUNCS --> EE_TEMPORAL
```

Sources: [geeflow/utils.py:31-33](), [geeflow/utils.py:35-53](), [geeflow/times.py:31-38](), [geeflow/times.py:41-55]()

## Usage Patterns and Integration Points

The utility modules are designed to be imported and used throughout the GeoFlow codebase, providing consistent interfaces for common operations. They serve as the foundation layer that enables higher-level components to focus on their specific domain logic.

Key integration patterns include:
- **Configuration Processing**: `parse_arg` enables flexible command-line configuration for all pipeline scripts
- **Earth Engine Setup**: `initialize_ee` provides standardized EE authentication across all EE-dependent modules  
- **Data Type Management**: `to_np` ensures consistent NumPy array handling for statistics and processing
- **Temporal Consistency**: Timezone-aware datetime handling ensures accurate temporal data processing
- **Spatial Calculations**: UTM grid size calculations support the coordinate system mapping functionality

Sources: [geeflow/utils.py:1-228](), [geeflow/times.py:1-145]()

---

