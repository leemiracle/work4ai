<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/rslearn_projects · page 4 Vessel Detection Systems · fetched 2026-10-26 -->

# Vessel Detection Systems

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [ai2_docs/README.md](ai2_docs/README.md)
- [ai2_docs/batch_inference.md](ai2_docs/batch_inference.md)
- [ai2_docs/coding_best_practices_brainstorm.md](ai2_docs/coding_best_practices_brainstorm.md)
- [ai2_docs/landsat_vessels/api_use.md](ai2_docs/landsat_vessels/api_use.md)
- [ai2_docs/landsat_vessels/images/missed_vessels_B8.png](ai2_docs/landsat_vessels/images/missed_vessels_B8.png)
- [ai2_docs/landsat_vessels/images/missed_vessels_RGB.png](ai2_docs/landsat_vessels/images/missed_vessels_RGB.png)
- [ai2_docs/landsat_vessels/model_summary.md](ai2_docs/landsat_vessels/model_summary.md)
- [ai2_docs/landsat_vessels/train_eval.md](ai2_docs/landsat_vessels/train_eval.md)
- [docs/images/landsat_vessels/prediction.png](docs/images/landsat_vessels/prediction.png)
- [docs/landsat_vessels.md](docs/landsat_vessels.md)
- [docs/sentinel2_vessels.md](docs/sentinel2_vessels.md)
- [rslp/landsat_vessels/predict_pipeline.py](rslp/landsat_vessels/predict_pipeline.py)
- [rslp/sentinel2_vessels/predict_pipeline.py](rslp/sentinel2_vessels/predict_pipeline.py)
- [rslp/utils/filter.py](rslp/utils/filter.py)
- [tests/integration/test_lightning_cli.py](tests/integration/test_lightning_cli.py)
- [tests/unit/forest_loss_driver/inference/test_unit_extract_alerts.py](tests/unit/forest_loss_driver/inference/test_unit_extract_alerts.py)
- [tests/unit/test_filter.py](tests/unit/test_filter.py)

</details>



This document covers the dual vessel detection systems for analyzing satellite imagery to identify ships and maritime vessels. The repository contains two complete detection pipelines: one for Landsat 8/9 imagery and another for Sentinel-2 imagery. Both systems integrate with the rslearn framework for data processing and provide REST APIs for operational deployment.

For information about the broader ML infrastructure supporting these systems, see [Core Infrastructure](#2). For details about distributed job processing, see [Distributed Worker System](#2.4).

## System Architecture Overview

The vessel detection systems consist of two independent but architecturally similar pipelines that share common utilities and deployment infrastructure.

```mermaid
graph TB
    subgraph "Landsat Vessel Detection"
        LandsatInput["Landsat Scene Input<br/>scene_id, zip_path, image_files"]
        LandsatDetector["Object Detector<br/>DETECT_MODEL_CONFIG"]
        LandsatClassifier["Binary Classifier<br/>CLASSIFY_MODEL_CONFIG"]
        LandsatOutput["Detection Results<br/>JSON, GeoJSON, Crops"]
    end
    
    subgraph "Sentinel-2 Vessel Detection"
        S2Input["Sentinel-2 Scene Input<br/>scene_id, image_files"]
        S2Detector["Object Detector<br/>DETECT_MODEL_CONFIG"]
        S2Attributes["Attribute Predictor<br/>ATTRIBUTE_MODEL_CONFIG"]
        S2Output["Detection + Attributes<br/>JSON, GeoJSON, Crops"]
    end
    
    subgraph "Shared Infrastructure"
        RSLearn["rslearn Framework<br/>Dataset, Window, MaterializeDataset"]
        VesselClasses["VesselDetection<br/>VesselAttributes<br/>VesselDetectionSource"]
        InfraFilter["NearInfraFilter<br/>Marine Infrastructure Filtering"]
        LightningCLI["CustomLightningCLI<br/>Model Training & Inference"]
    end
    
    subgraph "API Services"
        LandsatAPI["Landsat FastAPI<br/>Port 5555"]
        S2API["Sentinel-2 FastAPI<br/>Port 5555"]
        PrometheusMetrics["Prometheus Metrics<br/>TimerOperations"]
    end
    
    LandsatInput --> LandsatDetector
    LandsatDetector --> LandsatClassifier
    LandsatClassifier --> LandsatOutput
    
    S2Input --> S2Detector
    S2Detector --> S2Attributes
    S2Attributes --> S2Output
    
    LandsatDetector --> RSLearn
    LandsatClassifier --> RSLearn
    S2Detector --> RSLearn
    S2Attributes --> RSLearn
    
    LandsatOutput --> VesselClasses
    S2Output --> VesselClasses
    
    LandsatOutput --> InfraFilter
    S2Output --> InfraFilter
    
    RSLearn --> LightningCLI
    
    LandsatOutput --> LandsatAPI
    S2Output --> S2API
    
    LandsatAPI --> PrometheusMetrics
    S2API --> PrometheusMetrics
```

Sources: [rslp/landsat_vessels/predict_pipeline.py:1-592](), [rslp/sentinel2_vessels/predict_pipeline.py:1-572](), [rslp/utils/filter.py:1-126]()

## Common Data Models

Both systems use shared data models for representing detections and managing pipeline execution:

```mermaid
classDiagram
    class VesselDetection {
        +VesselDetectionSource source
        +int col
        +int row
        +Projection projection
        +float score
        +str scene_id
        +datetime ts
        +dict metadata
        +VesselAttributes attributes
        +get_lon_lat() tuple
        +to_dict() dict
        +to_feature() dict
    }
    
    class VesselAttributes {
        +float length
        +float width
        +float speed
        +float heading
        +str vessel_type
    }
    
    class SceneData {
        +Projection projection
        +PixelBounds bounds
        +tuple time_range
        +Item item
    }
    
    class NearInfraFilter {
        +str infra_url
        +float infra_distance_threshold
        +should_filter(lon, lat) bool
        +_get_haversine_distances() ndarray
    }
    
    VesselDetection --> VesselAttributes
    VesselDetection --> SceneData
    VesselDetection --> NearInfraFilter
```

Sources: [rslp/vessels.py](), [rslp/utils/filter.py:56-123]()

## Processing Pipeline Flow

Both systems follow a similar processing pattern with dataset materialization, model inference, and post-processing:

```mermaid
flowchart LR
    Input["Scene Input<br/>ID or Files"] --> Setup["setup_dataset()<br/>Create rslearn Dataset"]
    Setup --> Materialize["materialize_dataset()<br/>Download & Process Imagery"]
    Materialize --> Detect["run_model_predict()<br/>Object Detection Model"]
    Detect --> Classify["Secondary Model<br/>Classifier or Attributes"]
    Classify --> Filter["NearInfraFilter<br/>Remove Near Infrastructure"]
    Filter --> Crops["Generate Crops<br/>RGB/Pan Images"]
    Crops --> Output["Output Generation<br/>JSON, GeoJSON, Files"]
    
    subgraph "rslearn Integration"
        Dataset["Dataset Configuration"]
        Windows["Window Management"]
        Layers["Layer Processing"]
    end
    
    Setup --> Dataset
    Materialize --> Windows
    Materialize --> Layers
```

Sources: [rslp/landsat_vessels/predict_pipeline.py:83-163](), [rslp/sentinel2_vessels/predict_pipeline.py:248-338](), [rslp/utils/rslearn.py]()

## Input Modes and Configuration

The systems support multiple input modes for flexible deployment scenarios:

| Input Mode | Landsat Support | Sentinel-2 Support | Description |
|------------|----------------|-------------------|-------------|
| Scene ID | ✅ AWS S3 | ✅ GCP Public Data | Automatic download by scene identifier |
| Zip Archive | ✅ Local/GCS | ❌ | Compressed scene archive |
| Image Files | ✅ Multi-band | ✅ Multi-band | Direct file paths to band images |
| Window Path | ✅ | ❌ | Pre-processed rslearn window |

Sources: [rslp/landsat_vessels/predict_pipeline.py:270-408](), [rslp/sentinel2_vessels/predict_pipeline.py:116-245]()

## Model Architecture Differences

The two systems employ different detection strategies:

**Landsat (Two-Stage Pipeline):**
- Stage 1: Object detector identifies potential vessels
- Stage 2: Binary classifier filters false positives
- Window size: `CLASSIFY_WINDOW_SIZE` for classification crops
- Bands used: B2, B3, B4, B5, B6, B7, B8

**Sentinel-2 (Detection + Attributes):**
- Stage 1: Object detector identifies vessels
- Stage 2: Multi-task attribute predictor estimates vessel properties
- Window size: `CROP_WINDOW_SIZE` (128x128) for attribute prediction
- Bands used: B01-B12, B8A for newer models

Sources: [rslp/landsat_vessels/predict_pipeline.py:166-249](), [rslp/sentinel2_vessels/predict_pipeline.py:341-439](), [rslp/landsat_vessels/config.py](), [rslp/sentinel2_vessels/predict_pipeline.py:43-62]()

## Infrastructure Integration

Both systems integrate with the shared infrastructure components:

```mermaid
graph TB
    subgraph "Dataset Management"
        MaterializeArgs["MaterializeArgs<br/>PrepareArgs, IngestArgs"]
        ApplyWindowsArgs["ApplyWindowsArgs<br/>group, workers"]
        WindowLayerData["WindowLayerData<br/>Layer metadata management"]
    end
    
    subgraph "Model Execution"
        ModelConfig["Model Config Files<br/>YAML configurations"]
        RunModelPredict["run_model_predict()<br/>Lightning CLI wrapper"]
        CustomLightningCLI["CustomLightningCLI<br/>Checkpoint management"]
    end
    
    subgraph "Output Processing"
        GeojsonVectorFormat["GeojsonVectorFormat<br/>Spatial data encoding"]
        GeotiffRasterFormat["GeotiffRasterFormat<br/>Raster data encoding"]
        CropGeneration["Crop Generation<br/>RGB and pan-sharpened images"]
    end
    
    MaterializeArgs --> RunModelPredict
    ApplyWindowsArgs --> MaterializeArgs
    WindowLayerData --> MaterializeArgs
    
    ModelConfig --> RunModelPredict
    RunModelPredict --> CustomLightningCLI
    
    RunModelPredict --> GeojsonVectorFormat
    GeojsonVectorFormat --> CropGeneration
    CropGeneration --> GeotiffRasterFormat
```

Sources: [rslp/utils/rslearn.py](), [rslp/lightning_cli.py](), [rslp/landsat_vessels/predict_pipeline.py:118-131](), [rslp/sentinel2_vessels/predict_pipeline.py:285-298]()

---

