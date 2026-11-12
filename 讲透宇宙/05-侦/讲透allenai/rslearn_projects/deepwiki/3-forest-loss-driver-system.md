<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/rslearn_projects · page 3 Forest Loss Driver System · fetched 2026-10-26 -->

# Forest Loss Driver System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/forest_loss_driver_prediction.yaml](.github/workflows/forest_loss_driver_prediction.yaml)
- [rslp/forest_loss_driver/inference/config.py](rslp/forest_loss_driver/inference/config.py)
- [rslp/forest_loss_driver/inference/config/forest_loss_driver_predict_pipeline_config.yaml](rslp/forest_loss_driver/inference/config/forest_loss_driver_predict_pipeline_config.yaml)
- [rslp/forest_loss_driver/inference/extract_alerts.py](rslp/forest_loss_driver/inference/extract_alerts.py)
- [rslp/forest_loss_driver/predict_pipeline.py](rslp/forest_loss_driver/predict_pipeline.py)
- [tests/integration/forest_loss_driver/inference/test_extract_alerts.py](tests/integration/forest_loss_driver/inference/test_extract_alerts.py)
- [tests/integration/forest_loss_driver/test_predict_pipeline.py](tests/integration/forest_loss_driver/test_predict_pipeline.py)

</details>



The Forest Loss Driver System is an automated machine learning pipeline for processing forest loss alerts and predicting the underlying drivers of deforestation. This system processes Hansen/GLAD S2 alert data, extracts satellite imagery from Planet Labs, and applies trained models to classify the cause of forest loss events.

This document covers the prediction pipeline, data processing, and orchestration components. For information about the core ML infrastructure shared across applications, see [Core Infrastructure](#2). For details about model training and the rslearn framework integration, see [rslearn Framework Integration](#2.1).

## System Overview

The Forest Loss Driver System operates as an integrated pipeline that transforms raw forest loss alerts into classified predictions about deforestation drivers. The system runs on a weekly schedule via GitHub Actions and processes data across distributed Beaker clusters.

### High-Level Architecture

```mermaid
graph TB
    subgraph "Data Sources"
        hansen["Hansen GLAD S2 Alerts<br/>gs://earthenginepartners-hansen"]
        planet["Planet Labs NICFI Imagery<br/>API Integration"]
        shapes["Country Boundaries<br/>Natural Earth Data"]
    end
    
    subgraph "Alert Processing"
        extract["extract_alerts_pipeline"]
        mask["create_forest_loss_mask"]
        events["process_shapes_into_events"]
        windows["write_event"]
    end
    
    subgraph "Dataset Pipeline"
        materialize_inf["materialize_dataset<br/>(inference layers)"]
        materialize_vis["materialize_dataset<br/>(visualization layers)"]
        select_cloudy["select_least_cloudy_images_pipeline"]
    end
    
    subgraph "Model Pipeline"
        predict["run_model_predict"]
        output["GeoJSON Outputs"]
    end
    
    subgraph "Orchestration"
        github_actions["GitHub Actions Workflow<br/>forest_loss_driver_prediction.yaml"]
        beaker["Beaker Job Execution<br/>beaker_launcher"]
        docker["Docker Container<br/>rslearn_projects-test"]
    end
    
    hansen --> extract
    shapes --> extract
    extract --> mask
    mask --> events
    events --> windows
    
    windows --> materialize_inf
    windows --> materialize_vis
    planet --> materialize_inf
    planet --> materialize_vis
    
    materialize_inf --> select_cloudy
    materialize_vis --> select_cloudy
    select_cloudy --> predict
    predict --> output
    
    github_actions --> docker
    docker --> beaker
    beaker --> extract
    
    style extract fill:#f9f9f9
    style predict fill:#f9f9f9
    style github_actions fill:#e1f5fe
```

**System Architecture Flow**

Sources: [.github/workflows/forest_loss_driver_prediction.yaml:1-108](), [rslp/forest_loss_driver/predict_pipeline.py:35-94](), [rslp/forest_loss_driver/inference/extract_alerts.py:375-481]()

### Core Pipeline Components

| Component | Purpose | Input | Output |
|-----------|---------|--------|--------|
| `extract_alerts_pipeline` | Extract forest loss events from GLAD alerts | Hansen GeoTIFF files | rslearn Windows with masks |
| `materialize_dataset` | Fetch satellite imagery for windows | Windows + Planet API | Materialized image layers |
| `select_least_cloudy_images_pipeline` | Choose best images per window | Multiple image options | Selected image metadata |
| `run_model_predict` | Apply ML model to windows | Materialized dataset | GeoJSON predictions |

Sources: [rslp/forest_loss_driver/predict_pipeline.py:48-77](), [rslp/forest_loss_driver/inference/config.py:201-234]()

## Alert Extraction Pipeline

The alert extraction pipeline processes Hansen GLAD S2 alert data to identify recent forest loss events and create rslearn-compatible windows for downstream processing.

### Alert Processing Workflow

```mermaid
graph TB
    subgraph "Input Data"
        conf_tiff["Confidence GeoTIFF<br/>alert/*.tif"]
        date_tiff["Date GeoTIFF<br/>alertDate/*.tif"]
        country_shp["Country Shapefile<br/>ne_10m_admin_0_countries.shp"]
    end
    
    subgraph "Alert Filtering"
        read_conf["read_forest_alerts_confidence_raster"]
        read_date["read_forest_alerts_date_raster"]
        create_mask["create_forest_loss_mask<br/>(min_confidence, days)"]
        shapes_extract["rasterio.features.shapes"]
    end
    
    subgraph "Event Processing"
        process_shapes["process_shapes_into_events"]
        area_filter["Area Filter<br/>(min_area)"]
        country_filter["Country Boundary Filter<br/>(ISO_A2 == 'PE')"]
        limit_events["Limit Events<br/>(max_number_of_events)"]
    end
    
    subgraph "Window Creation"
        forest_event["ForestLossEvent"]
        window_meta["output_window_metadata"]
        window_save["Window.save()"]
        mask_raster["output_mask_raster"]
        event_meta["output_forest_event_metadata"]
    end
    
    conf_tiff --> read_conf
    date_tiff --> read_date
    read_conf --> create_mask
    read_date --> create_mask
    create_mask --> shapes_extract
    shapes_extract --> process_shapes
    
    process_shapes --> area_filter
    area_filter --> country_filter
    country_filter --> limit_events
    limit_events --> forest_event
    
    forest_event --> window_meta
    forest_event --> mask_raster
    forest_event --> event_meta
    window_meta --> window_save
    
    country_shp --> country_filter
    
    style create_mask fill:#f9f9f9
    style forest_event fill:#f9f9f9
```

**Alert Extraction Data Flow**

Sources: [rslp/forest_loss_driver/inference/extract_alerts.py:223-324](), [rslp/forest_loss_driver/inference/extract_alerts.py:375-481]()

### Key Processing Parameters

The alert extraction is controlled by several key parameters defined in `ExtractAlertsArgs`:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `min_confidence` | 2 | Minimum GLAD alert confidence threshold |
| `days` | 365 | Days to look back from prediction time |
| `min_area` | 16.0 | Minimum area (pixels) for event inclusion |
| `max_number_of_events` | None | Maximum events to process per tile |
| `workers` | 128 | Parallel workers for processing |

Sources: [rslp/forest_loss_driver/inference/config.py:56-112]()

### Forest Loss Event Structure

The `ForestLossEvent` class encapsulates each detected deforestation event:

```mermaid
classDiagram
    class ForestLossEvent {
        +STGeometry polygon_geom
        +STGeometry center_geom
        +tuple center_pixel
        +datetime ts
        +__init__(polygon_geom, center_geom, center_pixel, ts)
    }
    
    class Window {
        +UPath path
        +str group
        +str name
        +Projection projection
        +tuple bounds
        +tuple time_range
        +save()
    }
    
    ForestLossEvent --> Window : "creates"
    
    note for ForestLossEvent "Represents a single<br/>forest loss event with<br/>geometry and timing"
    note for Window "rslearn Window<br/>for model processing"
```

**Forest Loss Event Data Model**

Sources: [rslp/forest_loss_driver/inference/extract_alerts.py:54-78](), [rslp/forest_loss_driver/inference/extract_alerts.py:161-173]()

## Dataset Materialization

The dataset materialization process fetches satellite imagery for each extracted forest loss window using the rslearn framework and Planet Labs API integration.

### Layer Configuration

The system processes two distinct sets of imagery layers:

| Layer Type | Purpose | Workers | Layers |
|------------|---------|---------|---------|
| Inference | Model prediction | 128 | `pre_0` through `pre_6`, `post` |
| Visualization | Display/analysis | 32 | `planet_pre_0` through `planet_pre_2`, `planet_post_0` through `planet_post_2` |

```mermaid
graph LR
    subgraph "Inference Layers"
        pre0["pre_0"]
        pre1["pre_1"]
        pre2["pre_2"]
        pre3["pre_3"]
        pre4["pre_4"]
        pre5["pre_5"]
        pre6["pre_6"]
        post["post"]
    end
    
    subgraph "Visualization Layers"
        planet_pre0["planet_pre_0"]
        planet_pre1["planet_pre_1"]
        planet_pre2["planet_pre_2"]
        planet_post0["planet_post_0"]
        planet_post1["planet_post_1"]
        planet_post2["planet_post_2"]
    end
    
    subgraph "Materialization Process"
        prepare["PrepareArgs<br/>(use_initial_job=True)"]
        ingest["IngestArgs<br/>(ignore_errors=True)"]
        materialize["MaterializeArgs<br/>(ignore_errors=True)"]
    end
    
    pre0 --> prepare
    pre1 --> prepare
    pre2 --> prepare
    pre3 --> prepare
    pre4 --> prepare
    pre5 --> prepare
    pre6 --> prepare
    post --> prepare
    
    planet_pre0 --> prepare
    planet_pre1 --> prepare
    planet_pre2 --> prepare
    planet_post0 --> prepare
    planet_post1 --> prepare
    planet_post2 --> prepare
    
    prepare --> ingest
    ingest --> materialize
    
    style prepare fill:#f9f9f9
    style materialize fill:#f9f9f9
```

**Layer Materialization Architecture**

Sources: [rslp/forest_loss_driver/inference/config.py:18-37](), [rslp/forest_loss_driver/inference/config.py:115-183]()

### Materialization Configuration

The system uses separate configuration classes for different layer types:

- `InferenceLayerMaterializeArgs`: High worker count (128), disables visualization layers
- `VisLayerMaterializeArgs`: Limited workers (32) due to API rate limits, disables inference layers

Sources: [rslp/forest_loss_driver/inference/config.py:114-183]()

## Configuration System

The Forest Loss Driver system uses a hierarchical configuration approach combining dataclasses, YAML files, and environment variables.

### Configuration Architecture

```mermaid
graph TB
    subgraph "Configuration Sources"
        yaml_config["forest_loss_driver_predict_pipeline_config.yaml"]
        env_vars["Environment Variables<br/>(PL_API_KEY, RSLP_BUCKET)"]
        defaults["Dataclass Defaults"]
    end
    
    subgraph "Configuration Classes"
        predict_config["PredictPipelineConfig"]
        extract_args["ExtractAlertsArgs"]
        inf_materialize["InferenceLayerMaterializeArgs"]
        vis_materialize["VisLayerMaterializeArgs"]
        cloudy_args["SelectLeastCloudyImagesArgs"]
    end
    
    subgraph "Runtime Parameters"
        ds_root["ds_root: Dataset path"]
        model_cfg["model_cfg_fname: Model config"]
        workers["workers: Parallelization"]
        thresholds["min_confidence, min_area, days"]
    end
    
    yaml_config --> predict_config
    env_vars --> predict_config
    defaults --> predict_config
    
    predict_config --> extract_args
    predict_config --> inf_materialize
    predict_config --> vis_materialize
    predict_config --> cloudy_args
    
    extract_args --> ds_root
    extract_args --> workers
    extract_args --> thresholds
    inf_materialize --> model_cfg
    
    style predict_config fill:#f9f9f9
    style extract_args fill:#f9f9f9
```

**Configuration Hierarchy**

Sources: [rslp/forest_loss_driver/inference/config.py:201-234](), [rslp/forest_loss_driver/inference/config/forest_loss_driver_predict_pipeline_config.yaml:1-9]()

### Key Configuration Parameters

| Parameter | Location | Purpose |
|-----------|----------|---------|
| `ds_root` | Runtime | Dataset storage path (overwritten by pipeline) |
| `model_cfg_fname` | YAML | Path to model configuration file |
| `index_cache_dir` | YAML | Temporary index cache location |
| `tile_store_dir` | YAML | Weka storage path for tiles |
| `workers` | YAML | Parallel processing worker count |

Sources: [rslp/forest_loss_driver/inference/config/forest_loss_driver_predict_pipeline_config.yaml:1-9]()

## Pipeline Orchestration

The Forest Loss Driver system orchestrates complex workflows through GitHub Actions, Beaker job scheduling, and Docker containerization.

### GitHub Actions Workflow

```mermaid
graph TB
    subgraph "Trigger Events"
        manual["workflow_dispatch<br/>(Manual trigger)"]
        schedule["Cron Schedule<br/>(Mondays 8:00 AM UTC)"]
    end
    
    subgraph "Build Phase"
        checkout["Checkout repository"]
        cleanup["Cleanup disk space"]
        setup_beaker["Setup Beaker CLI"]
        build_docker["docker compose build<br/>(rslearn_projects-test)"]
        create_image["beaker image create<br/>(forest_loss_driver)"]
    end
    
    subgraph "Execution Phase"
        launch_job["beaker_launcher"]
        beaker_job["Beaker Job Execution"]
        pipeline_run["integrated_pipeline workflow"]
    end
    
    subgraph "Job Configuration"
        clusters["ai2/jupiter-cirrascale-2"]
        resources["1 GPU, 256GiB shared memory"]
        mounts["Weka mounts: /dfive-default"]
        secrets["PL_API_KEY from secrets"]
    end
    
    manual --> checkout
    schedule --> checkout
    checkout --> cleanup
    cleanup --> setup_beaker
    setup_beaker --> build_docker
    build_docker --> create_image
    create_image --> launch_job
    
    launch_job --> beaker_job
    beaker_job --> pipeline_run
    
    clusters --> beaker_job
    resources --> beaker_job
    mounts --> beaker_job
    secrets --> beaker_job
    
    style beaker_job fill:#f9f9f9
    style pipeline_run fill:#f9f9f9
```

**Orchestration Workflow**

Sources: [.github/workflows/forest_loss_driver_prediction.yaml:1-108]()

### Execution Environment

The system executes within a containerized environment with specific resource requirements:

| Resource | Configuration |
|----------|---------------|
| Container | `rslearn_projects-test` (built via docker-compose) |
| Cluster | `ai2/jupiter-cirrascale-2` |
| GPU | 1 GPU, preemptible instances |
| Memory | 256GiB shared memory |
| Storage | Weka mount at `/dfive-default` |
| API Keys | Planet Labs API key from GitHub secrets |

Sources: [.github/workflows/forest_loss_driver_prediction.yaml:84-107]()

### Pipeline Execution Flow

```mermaid
sequenceDiagram
    participant GHA as "GitHub Actions"
    participant Docker as "Docker Container"
    participant Beaker as "Beaker Cluster"
    participant Pipeline as "ForestLossDriverPredictionPipeline"
    participant Storage as "GCS/Weka Storage"
    
    GHA->>Docker: Build rslearn_projects-test image
    GHA->>Beaker: Create beaker image
    GHA->>Beaker: Launch job with config
    Beaker->>Pipeline: Execute integrated_pipeline
    Pipeline->>Pipeline: extract_dataset()
    Pipeline->>Storage: Read Hansen GLAD alerts
    Pipeline->>Storage: Write rslearn windows
    Pipeline->>Pipeline: materialize datasets
    Pipeline->>Storage: Fetch Planet imagery
    Pipeline->>Pipeline: run_model_predict()
    Pipeline->>Storage: Write GeoJSON outputs
    Pipeline-->>Beaker: Job completion
    Beaker-->>GHA: Status update
```

**Pipeline Execution Sequence**

Sources: [.github/workflows/forest_loss_driver_prediction.yaml:70-88](), [rslp/forest_loss_driver/predict_pipeline.py:35-94]()

The Forest Loss Driver System represents a sophisticated integration of remote sensing data processing, machine learning inference, and cloud-based orchestration, providing automated weekly assessment of forest loss drivers across targeted geographic regions.

---

