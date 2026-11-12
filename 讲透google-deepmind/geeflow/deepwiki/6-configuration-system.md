<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/geeflow · page 6 Configuration System · fetched 2026-10-26 -->

# Configuration System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [geeflow/configs/public/demo.py](geeflow/configs/public/demo.py)
- [geeflow/configs/public/global_drivers_1km_2022_v1.py](geeflow/configs/public/global_drivers_1km_2022_v1.py)

</details>



## Purpose and Scope

The Configuration System in GeoFlow provides a flexible and declarative way to specify dataset generation parameters using ML Collections ConfigDict files. This system defines what data sources to extract from Google Earth Engine, where to find label data, and how to process and structure the resulting datasets.

The configuration system is the primary interface for users to customize GeoFlow's behavior without modifying code. For information about the specific data sources available, see [Earth Engine Datasets](#5.1). For details on how configurations are processed into executable pipelines, see [Main Pipelines](#4).

## Configuration Architecture

The configuration system operates through Python configuration files that return structured `ConfigDict` objects. These configurations drive the entire dataset generation pipeline from data source specification to final TFDS output.

### Configuration Flow

```mermaid
flowchart TD
    CONFIG_FILE["Config File<br/>(demo.py, global_drivers.py)"] --> GET_CONFIG["get_config()"]
    GET_CONFIG --> PARSE_ARG["utils.parse_arg()"]
    GET_CONFIG --> CONFIG_DICT["ConfigDict<br/>{sources, labels}"]
    
    CONFIG_DICT --> SOURCES_CONFIG["get_sources_config()"]
    CONFIG_DICT --> LABELS_CONFIG["get_labels_config()"]
    
    SOURCES_CONFIG --> SOURCE_CONFIGS["Individual Source Configs<br/>{s2, s1, elevation, ...}"]
    LABELS_CONFIG --> LABEL_PARAMS["Label Parameters<br/>{path, img_width_m, meta_keys}"]
    
    SOURCE_CONFIGS --> GET_SOURCE_CONFIG["utils.get_source_config()"]
    GET_SOURCE_CONFIG --> EE_DATA_CLASSES["ee_data classes<br/>(Sentinel2, Hansen, etc.)"]
    
    CONFIG_DICT --> EXPORT_PIPELINE["export_beam_tfds.py"]
    CONFIG_DICT --> STATS_PIPELINE["compute_stats_beam.py"]
    
    EXPORT_PIPELINE --> PIPELINES["pipelines.py<br/>get_roi_sample_fn()"]
    PIPELINES --> EE_PROCESSING["Earth Engine Processing"]
```

Sources: [README.md:56-147](), [geeflow/configs/public/demo.py:66-71](), [geeflow/configs/public/global_drivers_1km_2022_v1.py:105-119]()

### Configuration Components

The configuration system consists of two main components that work together to define complete dataset specifications:

| Component | Purpose | Key Parameters |
|-----------|---------|----------------|
| **Labels Configuration** | Defines sample locations and metadata | `path`, `img_width_m`, `meta_keys`, `max_cell_size_m` |
| **Sources Configuration** | Specifies Earth Engine data sources | `scale`, `select`, `date_ranges`, `sampling_kw` |

Sources: [README.md:65-147]()

## Configuration Structure

### Labels Configuration

The labels configuration specifies where to find sample locations and how to structure the resulting dataset. It requires a CSV or Parquet file with location data and defines the spatial extent and metadata for each sample.

```mermaid
graph TB
    LABELS_CONFIG["Labels ConfigDict"] --> PATH["path<br/>CSV/Parquet file path"]
    LABELS_CONFIG --> IMG_WIDTH["img_width_m<br/>Image width in meters"]
    LABELS_CONFIG --> MAX_CELL["max_cell_size_m<br/>Reference pixel size"]
    LABELS_CONFIG --> META_KEYS["meta_keys<br/>Additional columns to include"]
    LABELS_CONFIG --> NUM_SAMPLES["num_max_samples<br/>Limit for debugging"]
    
    PATH --> CSV_FILE["CSV File<br/>{lat, lon, split, ...}"]
    IMG_WIDTH --> SPATIAL_EXTENT["Spatial Extent<br/>240m x 240m patches"]
    MAX_CELL --> MULTI_SCALE["Multi-scale Gridding<br/>30m reference resolution"]
    META_KEYS --> METADATA["Sample Metadata<br/>Labels, splits, coordinates"]
```

Key configuration parameters:

- **`path`**: File path to CSV/Parquet with sample locations (`lat`, `lon` columns required)
- **`img_width_m`**: Image width and height in meters for UTM projected samples
- **`max_cell_size_m`**: Reference maximal pixel size for proper multi-scale gridding
- **`meta_keys`**: List of additional columns to include in dataset samples
- **`default_scale`**: Default resolution per pixel for all sources (can be overridden per source)

Sources: [README.md:65-83](), [geeflow/configs/public/demo.py:55-63](), [geeflow/configs/public/global_drivers_1km_2022_v1.py:86-102]()

### Sources Configuration

The sources configuration defines which Earth Engine datasets to extract and how to process them. Each source is configured independently with its own spatial, temporal, and spectral parameters.

```mermaid
graph TB
    SOURCES_CONFIG["Sources ConfigDict"] --> S2_CONFIG["s2<br/>Sentinel-2 Configuration"]
    SOURCES_CONFIG --> S1_CONFIG["s1<br/>Sentinel-1 Configuration"]
    SOURCES_CONFIG --> ELEVATION_CONFIG["elevation<br/>Elevation Configuration"]
    SOURCES_CONFIG --> CUSTOM_CONFIG["Custom Sources<br/>Hansen, DynamicWorld, etc."]
    
    S2_CONFIG --> S2_PARAMS["scale: 10m<br/>select: [B3,B2,B1]<br/>mode: L2A<br/>reduce_fn: median"]
    S1_CONFIG --> S1_PARAMS["scale: 10m<br/>mode: IW<br/>pols: [VV,VH]<br/>reduce_fn: mean"]
    ELEVATION_CONFIG --> ELEV_PARAMS["scale: 30m<br/>select: [elevation,slope,aspect]"]
    
    S2_CONFIG --> DATE_RANGES["date_ranges<br/>[(2023-01-01, 12, 0)]"]
    S1_CONFIG --> SAMPLING_KW["sampling_kw<br/>{reduce_fn, cloud_mask_fn}"]
    
    CUSTOM_CONFIG --> EE_DATA_CLASSES["ee_data classes<br/>Hansen, DynamicWorld, GHSPop"]
```

Key source parameters:

- **`scale`**: Resolution per pixel in meters
- **`select`**: Which bands/channels to include, in order
- **`date_ranges`**: List of time ranges as (`start_date`, `months`, `days`) tuples
- **`sampling_kw`**: Keyword arguments for temporal aggregation (e.g., `reduce_fn`, `cloud_mask_fn`)
- **`kw`**: Additional parameters passed to the Earth Engine data class

Sources: [README.md:95-147](), [geeflow/configs/public/demo.py:30-52](), [geeflow/configs/public/global_drivers_1km_2022_v1.py:29-83]()

## Configuration Loading and Processing

### Configuration File Structure

Configuration files follow a standard pattern with three main functions that create modular, reusable configurations:

```mermaid
flowchart TD
    CONFIG_FILE["Configuration File<br/>(demo.py)"] --> GET_CONFIG_FUNC["get_config(arg=None)"]
    GET_CONFIG_FUNC --> PARSE_ARGS["utils.parse_arg(arg, ...)"]
    GET_CONFIG_FUNC --> BUILD_CONFIG["Build ConfigDict"]
    
    BUILD_CONFIG --> GET_SOURCES["get_sources_config()"]
    BUILD_CONFIG --> GET_LABELS["get_labels_config(labels_path, num_examples)"]
    
    GET_SOURCES --> SOURCE_SETUP["utils.get_source_config(class_name, type)"]
    GET_SOURCES --> SOURCE_PARAMS["Configure scale, select, date_ranges"]
    
    GET_LABELS --> LABEL_PARAMS["Configure path, img_width_m, meta_keys"]
    
    SOURCE_SETUP --> EE_DATA_LOOKUP["ee_data class lookup<br/>(Sentinel2, Hansen, etc.)"]
    
    BUILD_CONFIG --> FINAL_CONFIG["Final ConfigDict<br/>{sources: {...}, labels: {...}}"]
```

The standard configuration file pattern includes:

1. **`get_config(arg=None)`**: Main entry point that parses arguments and assembles the complete configuration
2. **`get_sources_config()`**: Builds the sources configuration with all Earth Engine data sources
3. **`get_labels_config(labels_path, ...)`**: Builds the labels configuration with location and metadata parameters

Sources: [geeflow/configs/public/demo.py:66-71](), [geeflow/configs/public/global_drivers_1km_2022_v1.py:105-119]()

### Source Configuration Factory

The `utils.get_source_config()` function provides a factory pattern for creating standardized source configurations:

```mermaid
graph LR
    GET_SOURCE_CONFIG["utils.get_source_config(class_name, type)"] --> LOOKUP["Class Lookup<br/>ee_data module"]
    LOOKUP --> BASE_CONFIG["Base ConfigDict<br/>{class_name, type, kw, ...}"]
    BASE_CONFIG --> CUSTOMIZATION["User Customization<br/>scale, select, date_ranges"]
    CUSTOMIZATION --> FINAL_SOURCE["Complete Source Config"]
    
    LOOKUP --> EE_DATA_CLASSES["Sentinel2<br/>Sentinel1<br/>Hansen<br/>NasaDem<br/>CustomImage<br/>CustomIC<br/>CustomFC"]
```

This factory approach ensures consistent configuration structure while allowing flexible customization of individual source parameters.

Sources: [geeflow/configs/public/demo.py:34-51](), [geeflow/configs/public/global_drivers_1km_2022_v1.py:33-82]()

## Configuration Processing Pipeline

### From Configuration to Execution

The configuration system integrates with the main processing pipelines through a well-defined interface:

```mermaid
flowchart TD
    CONFIG_DICT["ConfigDict<br/>{sources, labels}"] --> EXPORT_BEAM["export_beam_tfds.py"]
    CONFIG_DICT --> STATS_BEAM["compute_stats_beam.py"]
    
    EXPORT_BEAM --> TFDS_BUILDER["TFDSBuilder<br/>_generate_examples()"]
    TFDS_BUILDER --> LABELS_DF["Labels DataFrame<br/>from config.labels.path"]
    TFDS_BUILDER --> ROI_SAMPLE_FN["pipelines.get_roi_sample_fn()"]
    
    ROI_SAMPLE_FN --> SOURCE_PROCESSING["Source Processing<br/>per config.sources"]
    SOURCE_PROCESSING --> EE_QUERIES["Earth Engine Queries<br/>ee_export_utils.py"]
    
    STATS_BEAM --> STATS_PIPELINE["Statistics Pipeline<br/>compute_stats_beam_utils.py"]
    STATS_PIPELINE --> BAND_STATS["Per-band Statistics<br/>JSON output"]
    
    LABELS_DF --> COORDINATES["Sample Coordinates<br/>coords.py UTM mapping"]
    SOURCE_PROCESSING --> EE_ALGORITHMS["ee_algo.py<br/>Processing algorithms"]
```

The configuration drives the entire pipeline execution by:

1. **Labels Processing**: Converting the labels file path into a pandas DataFrame of sample locations
2. **Source Processing**: Creating processing functions for each configured Earth Engine source
3. **Coordinate Mapping**: Using the spatial parameters for UTM grid mapping
4. **Algorithm Selection**: Choosing appropriate Earth Engine algorithms based on source configuration

Sources: [README.md:161-176]()

## Advanced Configuration Patterns

### Dynamic Date Ranges

Advanced configurations can use functions to generate dynamic date ranges based on geographic location:

```mermaid
graph TB
    DATE_RANGES_FN["date_ranges_fn<br/>times.adjust_for_hemisphere()"] --> HEMISPHERE_LOGIC["Hemisphere Detection<br/>from sample coordinates"]
    HEMISPHERE_LOGIC --> NORTH_DATES["Northern Hemisphere<br/>[(2018-06-01, 3, 0), ...]"]
    HEMISPHERE_LOGIC --> SOUTH_DATES["Southern Hemisphere<br/>[(2017-12-01, 3, 0), ...]"]
    
    NORTH_DATES --> SEASONAL_ADJUST["Seasonal Adjustment<br/>Summer growing season"]
    SOUTH_DATES --> SEASONAL_ADJUST
```

This pattern allows for sophisticated temporal sampling that adapts to geographic and seasonal variations.

Sources: [geeflow/configs/public/global_drivers_1km_2022_v1.py:64-67]()

### Custom Feature Collections

For specialized datasets, configurations can reference custom Earth Engine assets:

```mermaid
graph LR
    CUSTOM_FC["CustomFC Configuration"] --> ASSET_NAME["asset_name<br/>projects/wri-datalab/..."]
    CUSTOM_FC --> FEATURE_PROCESSING["fc_to_image algorithm<br/>ee_algo.fc_to_image"]
    CUSTOM_FC --> REDUCER["sampling_kw.reducer<br/>first, mean, max"]
    
    ASSET_NAME --> EE_ASSET["Earth Engine Asset<br/>Feature Collection"]
    FEATURE_PROCESSING --> IMAGE_CONVERSION["Convert to Image<br/>for pixel sampling"]
```

This enables integration of custom datasets and research-specific feature collections into the standardized processing pipeline.

Sources: [geeflow/configs/public/global_drivers_1km_2022_v1.py:33-40](), [geeflow/configs/public/global_drivers_1km_2022_v1.py:50-55]()

---

