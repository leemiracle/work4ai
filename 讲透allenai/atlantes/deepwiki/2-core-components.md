<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/atlantes · page 2 Core Components · fetched 2026-10-26 -->

# Core Components

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [ais/README.md](ais/README.md)
- [ais/src/atlantes/atlas/ais_dataset.py](ais/src/atlantes/atlas/ais_dataset.py)

</details>



This page provides an overview of the primary functional components that make up the Atlantes system. Atlantes is a real-time GPS trajectory modeling system for processing maritime AIS (Automatic Identification System) data to classify vessel activities and entities. This page summarizes the main components and how they interact to form the complete system.

For detailed information about system architecture, see [System Architecture](#1.2). For more specifics on individual components, refer to the subpages on [ATLAS Models](#2.1), [Data Processing Pipeline](#2.2), and [Inference Services](#2.3).

## Core Components Overview

Atlantes consists of several interconnected components that work together to process AIS data and provide vessel activity and entity classifications:

```mermaid
flowchart TD
    AIS[("AIS Data")] --> DataProcessing["Data Processing Pipeline"]
    DataProcessing --> TrainingData["Training Data"]
    TrainingData --> ModelTraining["Model Training"]
    
    ModelTraining --> AtlasModels["ATLAS Models"]
    AtlasModels --> ActivityModel["Activity Classification Model"]
    AtlasModels --> EntityModel["Entity Classification Model"]
    
    ActivityModel --> ActivityService["Activity Service"]
    EntityModel --> EntityService["Entity Service"]
    
    ActivityService --> InferenceResults["Inference Results"]
    EntityService --> EntityPostprocessor["Entity Postprocessor"]
    EntityPostprocessor --> InferenceResults
    
    CPDService["Contextual Property Detection (CPD) Service"] --> ActivityService
```

Sources: [ais/README.md:16-25](). This diagram reflects the Atlantes AIS modeling tasks described in lines 16-25 of the README, showing the two main classification tasks.

## ATLAS Models

At the core of Atlantes are two main machine learning model systems collectively referred to as ATLAS (AIS Transformer Learning with Active Subpaths):

### Activity Classification Models

The Activity Classification models focus on determining what vessels are doing based on their movement patterns:

1. **End of Sequence Activity Classification**: Classifies the activity of a vessel at the end of a trajectory (e.g., fishing, anchored, transiting).
2. **Dense Activity Classification**: Classifies the activity for each subpath within a trajectory, providing a more granular view of vessel behavior over time.

### Entity Classification Models

The Entity Classification models focus on identifying what type of entity is transmitting AIS data:

1. **Vessel vs. Buoy Classification**: Distinguishes whether an AIS signal is coming from a vessel or a stationary buoy.
2. **Vessel Type Classification**: Identifies the specific type of vessel (e.g., fishing vessel, cargo ship, tanker).

```mermaid
classDiagram
    class AISTrajectoryBaseDataset {
        +__init__(dataset_config, mode)
        +apply_augmentations()
        +_preprocess()
        +_normalize_features()
        +_load_trackfile()
    }
    
    class ActivityDatasetEndOfSequence {
        +__init__(dataset_config, activity_label_file_paths, mode)
        +_init_train_mode()
        +_init_online_mode()
        +__getitem__(idx)
    }
    
    class AISTrajectoryEntityDataset {
        +__init__(dataset_config, entity_labels_path, mode)
        +_init_train_mode()
        +_init_online_mode()
        +__getitem__(idx)
    }
    
    AISTrajectoryBaseDataset <|-- ActivityDatasetEndOfSequence
    AISTrajectoryBaseDataset <|-- AISTrajectoryEntityDataset
```

Sources: [ais/src/atlantes/atlas/ais_dataset.py:60-1119]()

## Data Processing Pipeline

The Data Processing Pipeline handles the ingestion, cleaning, and transformation of AIS data for both model training and inference.

### Key Components of the Data Processing Pipeline:

1. **Data Loading**: Reading and parsing AIS data from various sources (CSV, Parquet).
2. **Preprocessing**: Cleaning and standardizing the raw AIS data.
3. **Feature Engineering**: Computing derived features such as:
   - Relative course over ground (rel_cog)
   - Amount of light (based on solar position)
   - Spatial intervals (using haversine distance)
   - Temporal intervals (time between AIS messages)
4. **Normalization**: Applying various transformations to features (sqrt, log, z-scaling).
5. **Augmentation**: Data augmentation for training robustness.

```mermaid
flowchart LR
    subgraph "Data Processing Pipeline"
        Load["Data Loading\n(_load_trackfile)"] --> Preproc["Preprocessing\n(_preprocess)"]
        Preproc --> FeatEng["Feature Engineering"]
        FeatEng --> Norm["Normalization\n(_normalize_features)"]
        Norm --> Aug["Augmentation\n(apply_augmentations)"]
    end
    
    subgraph "Feature Engineering"
        RelCOG["Relative COG\n(_calculate_relative_cog)"]
        Light["Amount of Light\n(_add_amount_of_light_feature)"]
        Space["Spatial Intervals\n(_get_spatial_intervals)"]
        Time["Time Intervals\n(_get_time_intervals)"]
    end
    
    FeatEng --> RelCOG
    FeatEng --> Light
    FeatEng --> Space
    FeatEng --> Time
```

Sources: [ais/src/atlantes/atlas/ais_dataset.py:299-401]()

## Inference Services

Atlantes provides several services that expose the ATLAS models for real-time inference:

### Key Inference Services

1. **Activity Service**: Classifies vessel activities using the ATLAS Activity Model.
2. **Entity Service**: Classifies vessels and buoys using the ATLAS Entity Model.
3. **Entity Postprocessor**: Post-processes entity classification results.
4. **Contextual Property Detection (CPD) Service**: Provides contextual information to the Activity Service.

These services are exposed through gRPC interfaces and are typically deployed as Docker containers.

```mermaid
flowchart TD
    subgraph "Docker Containers"
        ActivityService["Activity Service\n(Port 8000)"]
        EntityService["Entity Service\n(Port 8001)"]
        CPDService["CPD Service\n(Port 5206)"]
        EntityPostprocessor["Entity Postprocessor\n(Port 5207)"]
    end
    
    AISData[("AIS Data")] --> ActivityService
    AISData --> EntityService
    
    MarineData[("Marine Infrastructure Data")] --> CPDService
    
    CPDService --> ActivityService
    EntityService --> EntityPostprocessor
    
    ActivityService --> Client["Client Applications"]
    EntityPostprocessor --> Client
```

Sources: [ais/README.md:119-122](), referring to the deployment documentation mentioned in the README.

## Core Libraries and Dependencies

Atlantes relies on several key libraries and frameworks for its functionality:

| Library | Purpose |
|---------|---------|
| PyTorch | Deep learning framework for model implementation |
| Dask | Parallel and distributed data processing |
| Pandas | Data manipulation and analysis |
| Pandera | Schema-based validation for DataFrames |
| Wandb | Experiment tracking |
| Beaker | AI2 experimentation platform |

The system also requires authentication to Google Cloud Platform (GCP) for accessing AIS data and weights and biases for experiment tracking.

```mermaid
flowchart LR
    subgraph "Atlantes Core Dependencies"
        PyTorch["PyTorch\n(Modeling)"]
        Dask["Dask\n(Parallel Processing)"]
        Pandas["Pandas\n(Data Manipulation)"]
        Pandera["Pandera\n(Schema Validation)"]
        Wandb["Wandb\n(Experiment Tracking)"]
        Beaker["Beaker\n(AI2 Platform)"]
    end
    
    subgraph "External Dependencies"
        GCP["Google Cloud Platform\n(Data Storage)"]
        GPU["CUDA/cuDNN\n(GPU Acceleration)"]
    end
    
    Atlantes["Atlantes System"] --> PyTorch
    Atlantes --> Dask
    Atlantes --> Pandas
    Atlantes --> Pandera
    Atlantes --> Wandb
    Atlantes --> Beaker
    
    Atlantes --> GCP
    PyTorch --> GPU
```

Sources: [ais/README.md:26-33]()

## Dataset Classes

The dataset components are critical for both training and inference. Atlantes implements specialized dataset classes for handling AIS trajectory data:

### Base Dataset Class

The `AISTrajectoryBaseDataset` serves as the foundation for all trajectory datasets, providing common functionality for:
- Loading and preprocessing trajectory data
- Computing spatiotemporal intervals for the Continuous Point Embedding (CPE)
- Normalizing features
- Applying data augmentations

### Specialized Dataset Classes

1. **ActivityDatasetEndOfSequence**: Handles data for activity classification
   - Loads trajectory and corresponding activity labels
   - Prepares input features and labels for the activity model
   - Supports both training and online (inference) modes

2. **AISTrajectoryEntityDataset**: Handles data for entity classification
   - Loads trajectory and corresponding entity labels
   - Prepares input features and labels for the entity model
   - Supports both training and online (inference) modes

```mermaid
flowchart TD
    subgraph "Dataset Workflow"
        TrackFile["Trajectory File\n(.csv or .parquet)"] --> LoadTrack["_load_trackfile()"]
        LoadTrack --> Preprocess["_preprocess()"]
        Preprocess --> FeatureEng["Feature Engineering"]
        FeatureEng --> Normalize["_normalize_features()"]
        Normalize --> Intervals["Compute Intervals\n(_get_spatial_intervals, _get_time_intervals)"]
        Intervals --> ModelInput["Model Input Tensors"]
    end
    
    subgraph "Dataset Modes"
        Train["Train Mode\n(with labels)"]
        Online["Online Mode\n(inference)"]
    end
    
    Train --> LoadTrack
    Online --> LoadTrack
```

Sources: [ais/src/atlantes/atlas/ais_dataset.py:60-119](), [ais/src/atlantes/atlas/ais_dataset.py:537-923](), [ais/src/atlantes/atlas/ais_dataset.py:928-1119]()

## Data Flow Through Components

To understand how the components work together, here's a data flow diagram showing how AIS data is processed through the system:

```mermaid
flowchart LR
    AIS[("AIS Data")] --> DataProc["Data Processing"]
    DataProc --> TrajDS["AISTrajectoryBaseDataset"]
    
    subgraph "Training Flow"
        TrajDS --> ActDS["ActivityDatasetEndOfSequence\n(Train Mode)"]
        TrajDS --> EntDS["AISTrajectoryEntityDataset\n(Train Mode)"]
        ActDS --> ActTrain["Activity Model\nTraining"]
        EntDS --> EntTrain["Entity Model\nTraining"]
        ActTrain --> ActModel["Trained Activity\nModel"]
        EntTrain --> EntModel["Trained Entity\nModel"]
    end
    
    subgraph "Inference Flow"
        TrajDS --> ActDSOnline["ActivityDatasetEndOfSequence\n(Online Mode)"]
        TrajDS --> EntDSOnline["AISTrajectoryEntityDataset\n(Online Mode)"]
        ActModel --> ActServ["Activity Service"]
        EntModel --> EntServ["Entity Service"]
        ActDSOnline --> ActServ
        EntDSOnline --> EntServ
        CPD["CPD Service"] --> ActServ
        EntServ --> EntPost["Entity Postprocessor"]
    end
    
    ActServ --> API["API Endpoints"]
    EntPost --> API
```

Sources: [ais/src/atlantes/atlas/ais_dataset.py:145-148](), [ais/src/atlantes/atlas/ais_dataset.py:585-616](), [ais/src/atlantes/atlas/ais_dataset.py:985-987](), [ais/README.md:90-95]()

This data flow diagram shows how AIS data moves through the system from initial processing to final API endpoints, including both the training and inference paths.

---

