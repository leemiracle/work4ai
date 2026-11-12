<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/rslearn_projects · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [LICENSE](LICENSE)
- [README.md](README.md)
- [docs/images/sentinel2_vessels/prediction.png](docs/images/sentinel2_vessels/prediction.png)
- [docs/satlas_marine_infra.md](docs/satlas_marine_infra.md)
- [rslp/forest_loss_driver/README.md](rslp/forest_loss_driver/README.md)

</details>



## Purpose and Scope

The `rslearn_projects` repository contains production machine learning applications for remote sensing built on the [rslearn framework](https://github.com/allenai/rslearn). This repository serves as the operational deployment layer for AI2's remote sensing capabilities, providing complete end-to-end systems from data processing to model inference and API services.

The repository encompasses three primary categories of systems:
- **Geospatial analysis applications** for forest monitoring, infrastructure detection, and ecosystem mapping
- **Vessel detection systems** for maritime surveillance using multiple satellite data sources
- **Foundation model integrations** enabling transfer learning across remote sensing tasks

For specific application documentation, see [Forest Loss Driver System](#3), [Vessel Detection Systems](#4), and [Satlas System](#5). For infrastructure details, see [Core Infrastructure](#2).

## System Architecture

The repository implements a layered architecture where specialized applications build upon shared infrastructure components:

```mermaid
graph TB
    subgraph "Application Layer"
        fld["forest_loss_driver"]
        landsat_vessels["landsat_vessels"] 
        sentinel2_vessels["sentinel2_vessels"]
        satlas_apps["satlas applications"]
        maldives["maldives_ecosystem_mapping"]
        helios_tasks["helios fine-tuning"]
    end
    
    subgraph "Framework Layer"
        rslp_main["rslp.main"]
        rslearn_main["rslp.rslearn_main"]
        custom_lightning["CustomLightningCLI"]
        multi_task["MultiTaskModel"]
    end
    
    subgraph "Infrastructure Layer"
        rslearn_framework["rslearn framework"]
        pytorch_lightning["PyTorch Lightning"]
        docker_base["Docker containers"]
        beaker_platform["Beaker platform"]
    end
    
    subgraph "Storage & Services"
        gcs["Google Cloud Storage"]
        ghcr["GitHub Container Registry"]
        fastapi_services["FastAPI services"]
        pubsub["Google Cloud Pub/Sub"]
    end
    
    fld --> rslp_main
    landsat_vessels --> rslearn_main
    sentinel2_vessels --> rslearn_main
    satlas_apps --> rslp_main
    maldives --> rslearn_main
    helios_tasks --> rslearn_main
    
    rslp_main --> rslearn_framework
    rslearn_main --> custom_lightning
    custom_lightning --> pytorch_lightning
    multi_task --> custom_lightning
    
    rslearn_framework --> docker_base
    docker_base --> beaker_platform
    
    landsat_vessels --> fastapi_services
    sentinel2_vessels --> fastapi_services
    fld --> gcs
    satlas_apps --> pubsub
    
    fastapi_services --> ghcr
    beaker_platform --> gcs
```

Sources: [README.md:1-47](), [rslp/forest_loss_driver/README.md:1-60]()

## Application Ecosystem

The repository contains seven major application systems, each serving distinct remote sensing use cases:

```mermaid
graph LR
    subgraph "Forest Monitoring"
        fld_extract["extract_alerts.py"]
        fld_materialize["materialize_dataset.py"] 
        fld_predict["predict_pipeline.py"]
        fld_index["index_windows.py"]
    end
    
    subgraph "Vessel Detection"
        landsat_detect["landsat_detect.py"]
        sentinel2_detect["sentinel2_detect.py"]
        vessel_attrs["vessel_attributes.py"]
        vessel_api["vessel_api services"]
    end
    
    subgraph "Infrastructure Detection"
        satlas_marine["marine_infra application"]
        satlas_wind["wind_turbine application"]
        satlas_solar["solar_farm application"]
        satlas_predict["satlas predict pipeline"]
    end
    
    subgraph "Foundation Models"
        helios_finetune["helios fine-tuning"]
        satlaspretrain["SatlasPretrain encoders"]
        multitask_models["MultiTaskModel instances"]
    end
    
    subgraph "Specialized Applications"
        maldives_segment["maldives segmentation"]
        crop_mapping["crop_type_mapping"]
        eurosat["EuroSAT classification"]
    end
    
    fld_extract --> fld_materialize
    fld_materialize --> fld_predict
    fld_predict --> fld_index
    
    landsat_detect --> vessel_api
    sentinel2_detect --> vessel_api
    vessel_attrs --> sentinel2_detect
    
    satlas_marine --> satlas_predict
    satlas_wind --> satlas_predict
    satlas_solar --> satlas_predict
    
    helios_finetune --> multitask_models
    satlaspretrain --> multitask_models
    multitask_models --> landsat_detect
    multitask_models --> sentinel2_detect
    multitask_models --> fld_predict
```

Sources: [README.md:36-47](), [docs/satlas_marine_infra.md:1-116]()

## Core Technology Stack

The repository standardizes on a specific technology stack that enables consistent development and deployment patterns across all applications:

| Component | Technology | Purpose |
|-----------|------------|---------|
| ML Framework | `rslearn` + PyTorch Lightning | Dataset management, model training, and inference |
| CLI Interface | `CustomLightningCLI` | Enhanced Lightning CLI with cloud checkpointing |
| Containerization | Docker + Docker Compose | Development environment and deployment packaging |
| Orchestration | Beaker platform | GPU cluster job scheduling and execution |
| Storage | Google Cloud Storage | Model checkpoints, datasets, and results |
| APIs | FastAPI | Production inference services |
| Job Queuing | Google Cloud Pub/Sub | Distributed processing coordination |
| Registry | GitHub Container Registry | Container image publishing |

The `RSLP_PREFIX` environment variable serves as the root path for all model checkpoints and auxiliary files, typically pointing to a Google Cloud Storage bucket for production deployments.

Sources: [README.md:28-34]()

## Development and Deployment Pipeline

The repository implements a comprehensive CI/CD pipeline that transforms code changes into production-ready containerized services:

```mermaid
graph TD
    subgraph "Development"
        local_dev["Local Development"]
        env_setup[".env configuration"]
        requirements["requirements.txt"]
        docker_compose["docker-compose.yml"]
    end
    
    subgraph "CI/CD Pipeline"
        github_actions[".github/workflows/"]
        build_test["Build & Test"]
        docker_build["Docker Image Build"]
        publish_ghcr["Publish to GHCR"]
    end
    
    subgraph "Production Deployment"
        beaker_experiments["Beaker experiments"]
        gpu_clusters["AI2 GPU clusters"]
        model_checkpoints["Model checkpoints in GCS"]
        api_deployment["FastAPI service deployment"]
    end
    
    subgraph "Monitoring & Outputs"
        wandb_logging["Weights & Biases logging"]
        prometheus_metrics["Prometheus metrics"]
        geojson_outputs["GeoJSON prediction outputs"]
        vector_tiles["Vector tile generation"]
    end
    
    local_dev --> env_setup
    env_setup --> requirements
    requirements --> docker_compose
    
    docker_compose --> github_actions
    github_actions --> build_test
    build_test --> docker_build
    docker_build --> publish_ghcr
    
    publish_ghcr --> beaker_experiments
    beaker_experiments --> gpu_clusters
    gpu_clusters --> model_checkpoints
    model_checkpoints --> api_deployment
    
    gpu_clusters --> wandb_logging
    api_deployment --> prometheus_metrics
    beaker_experiments --> geojson_outputs
    geojson_outputs --> vector_tiles
```

The deployment process leverages AI2's internal infrastructure, with Beaker providing GPU cluster access and Google Cloud Storage serving as the primary data persistence layer. All applications follow the same containerization patterns, enabling consistent deployment and scaling across different use cases.

Sources: [README.md:12-34]()

---

