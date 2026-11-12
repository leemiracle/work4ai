<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/geeflow · page 4 Main Pipelines · fetched 2026-10-26 -->

# Main Pipelines

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [geeflow/export_beam_tfds.py](geeflow/export_beam_tfds.py)
- [geeflow/stats/compute_stats_beam.py](geeflow/stats/compute_stats_beam.py)

</details>



This document provides an overview of the two primary Apache Beam pipelines that form the core of GeoFlow's data processing system. These pipelines work sequentially to extract geospatial data from Google Earth Engine and generate machine learning-ready datasets with computed statistics.

For detailed explanations of individual pipeline components and configuration, see [Dataset Export Pipeline](#4.1) and [Statistics Computation Pipeline](#4.2). For information about configuring these pipelines, see [Configuration System](#6).

## Pipeline Architecture Overview

GeoFlow operates through two main Apache Beam pipelines that process geospatial data in sequence:

```mermaid
graph TD
    subgraph "Input Sources"
        CONFIG["Configuration Files<br/>(ConfigDict)"]
        LABELS["Label Data<br/>(CSV/Parquet)"]
        GEE["Google Earth Engine<br/>(Satellite Data)"]
    end
    
    subgraph "Pipeline 1: Dataset Export"
        EXPORT_MAIN["export_beam_tfds.py"]
        TFDS_BUILDER["TFDSBuilder"]
        CREATE_DATA["CreateData DoFn"]
        GET_INFO["GetInfo DoFn"]
    end
    
    subgraph "Intermediate Output"
        TFDS_DATASET["TFDS Dataset<br/>(TensorFlow Records)"]
    end
    
    subgraph "Pipeline 2: Statistics Computation"
        STATS_MAIN["compute_stats_beam.py"]
        READ_TFDS["ReadFromTFDS"]
        STATS_UTILS["compute_stats_beam_utils"]
    end
    
    subgraph "Final Output"
        STATS_JSON["Statistics Files<br/>(JSON per band)"]
    end
    
    CONFIG --> EXPORT_MAIN
    LABELS --> EXPORT_MAIN
    GEE --> EXPORT_MAIN
    
    EXPORT_MAIN --> TFDS_BUILDER
    TFDS_BUILDER --> CREATE_DATA
    CREATE_DATA --> GET_INFO
    GET_INFO --> TFDS_DATASET
    
    TFDS_DATASET --> STATS_MAIN
    STATS_MAIN --> READ_TFDS
    READ_TFDS --> STATS_UTILS
    STATS_UTILS --> STATS_JSON
```

**Sources:** [geeflow/export_beam_tfds.py:1-486](), [geeflow/stats/compute_stats_beam.py:1-83]()

## Pipeline Component Mapping

The following diagram maps the high-level pipeline components to their specific code implementations:

```mermaid
graph TB
    subgraph "export_beam_tfds.py Components"
        TFDS_BUILDER_CLASS["TFDSBuilder<br/>(lines 323-405)"]
        CREATE_DATA_CLASS["CreateData DoFn<br/>(lines 74-120)"]
        APPLY_FILTERS["apply_filters function<br/>(lines 126-136)"]
        APPLY_TRANSFORMS["apply_transforms function<br/>(lines 198-241)"]
        PROCESS_EXAMPLE["_process_example function<br/>(lines 243-274)"]
    end
    
    subgraph "compute_stats_beam.py Components"
        CONVERT_FORMAT["convert_format function<br/>(lines 44-46)"]
        CREATE_PIPELINE_SPLIT["create_pipeline_for_split<br/>(lines 48-62)"]
        MAIN_PIPELINE["create_pipeline function<br/>(lines 64-70)"]
    end
    
    subgraph "External Dependencies"
        EE_EXPORT_UTILS["ee_export_utils.GetInfo"]
        COMPUTE_STATS_UTILS["compute_stats_beam_utils"]
        TFDS_BEAM["tfds.beam.ReadFromTFDS"]
        PIPELINES["pipelines module"]
    end
    
    TFDS_BUILDER_CLASS --> CREATE_DATA_CLASS
    CREATE_DATA_CLASS --> EE_EXPORT_UTILS
    CREATE_DATA_CLASS --> PIPELINES
    TFDS_BUILDER_CLASS --> APPLY_FILTERS
    TFDS_BUILDER_CLASS --> APPLY_TRANSFORMS
    TFDS_BUILDER_CLASS --> PROCESS_EXAMPLE
    
    CREATE_PIPELINE_SPLIT --> TFDS_BEAM
    CREATE_PIPELINE_SPLIT --> CONVERT_FORMAT
    CREATE_PIPELINE_SPLIT --> COMPUTE_STATS_UTILS
    MAIN_PIPELINE --> CREATE_PIPELINE_SPLIT
```

**Sources:** [geeflow/export_beam_tfds.py:74-120](), [geeflow/export_beam_tfds.py:323-405](), [geeflow/stats/compute_stats_beam.py:48-70]()

## Dataset Export Pipeline

The dataset export pipeline (`export_beam_tfds.py`) serves as the primary data extraction and transformation engine. This pipeline:

| Component | Function | Key Classes/Functions |
|-----------|----------|----------------------|
| **Data Creation** | Reads label data and creates initial feature collections | `CreateData` DoFn |
| **EE Query Processing** | Executes distributed Google Earth Engine queries | `ee_export_utils.GetInfo` DoFn |
| **Data Filtering** | Applies configurable filters to remove unwanted samples | `apply_filters` function |
| **Data Transformation** | Performs spatial cropping, CCDC generation, and format conversion | `apply_transforms` function |
| **TFDS Generation** | Converts processed data to TensorFlow Dataset format | `TFDSBuilder` class |

The pipeline processes data through the following stages:
1. **Label Processing**: Reads CSV/Parquet files containing sample locations and metadata [geeflow/export_beam_tfds.py:85-92]()
2. **Split Generation**: Creates train/validation/test splits either from data columns or geographic distribution [geeflow/export_beam_tfds.py:94-113]()
3. **Earth Engine Queries**: Retrieves satellite imagery and geospatial data for each location [geeflow/export_beam_tfds.py:384-396]()
4. **Data Processing**: Applies algorithms, filters, and transformations to raw data [geeflow/export_beam_tfds.py:397-404]()

**Sources:** [geeflow/export_beam_tfds.py:323-405](), [geeflow/export_beam_tfds.py:74-120]()

## Statistics Computation Pipeline

The statistics computation pipeline (`compute_stats_beam.py`) operates on the TFDS datasets generated by the export pipeline. This pipeline:

| Component | Function | Implementation |
|-----------|----------|----------------|
| **TFDS Reading** | Loads generated datasets for analysis | `tfds.beam.ReadFromTFDS` |
| **Format Conversion** | Converts TensorFlow data to NumPy arrays | `convert_format` function |
| **Statistics Processing** | Computes per-band statistics across all samples | `compute_stats_beam_utils` module |
| **Output Generation** | Saves statistics as JSON files for each band and split | File I/O operations |

The pipeline operates in the following sequence:
1. **Dataset Loading**: Reads TFDS datasets for specified splits [geeflow/stats/compute_stats_beam.py:50-55]()
2. **Data Conversion**: Transforms data format for statistics computation [geeflow/stats/compute_stats_beam.py:44-46]()
3. **Statistics Calculation**: Computes comprehensive statistics per band [geeflow/stats/compute_stats_beam.py:60-61]()
4. **Results Storage**: Outputs JSON files with statistical summaries [geeflow/stats/compute_stats_beam.py:56-61]()

**Sources:** [geeflow/stats/compute_stats_beam.py:48-70](), [geeflow/stats/compute_stats_beam.py:44-46]()

## Pipeline Execution and Configuration

Both pipelines are designed to run with Apache Beam and support multiple execution modes:

- **Direct Runner**: Local execution with configurable threading [geeflow/export_beam_tfds.py:467-468]()
- **Cloud Runner**: Distributed execution on Google Cloud Dataflow [geeflow/export_beam_tfds.py:469-470]()

The pipelines accept command-line arguments for configuration and can be launched independently:

```bash
# Export pipeline
python -m geeflow.export_beam_tfds --config_path=... --tfds_name=... --output_dir=...

# Statistics pipeline  
python -m geeflow.stats.compute_stats_beam --tfds_name=... --split=... --data_dir=...
```

Both pipelines integrate with the ML Collections configuration system and support flexible parameterization through config files and command-line overrides.

**Sources:** [geeflow/export_beam_tfds.py:45-68](), [geeflow/stats/compute_stats_beam.py:28-41]()

---

