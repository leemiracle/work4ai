<!-- source: DeepWiki mcp.deepwiki.com · repo pykale/pykale · page 2 Pipeline API Reference · fetched 2026-10-21 -->

# Pipeline API Reference

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/source/index.rst](docs/source/index.rst)
- [docs/source/kale.embed.rst](docs/source/kale.embed.rst)
- [docs/source/kale.evaluate.rst](docs/source/kale.evaluate.rst)
- [docs/source/kale.loaddata.rst](docs/source/kale.loaddata.rst)
- [docs/source/kale.pipeline.rst](docs/source/kale.pipeline.rst)
- [docs/source/kale.predict.rst](docs/source/kale.predict.rst)
- [docs/source/kale.prepdata.rst](docs/source/kale.prepdata.rst)
- [docs/source/kale.utils.rst](docs/source/kale.utils.rst)

</details>



This document provides comprehensive documentation of PyKale's core pipeline modules and their interfaces. The Pipeline API implements PyKale's knowledge-aware machine learning philosophy through a standardized, modular architecture that supports multimodal learning and transfer learning workflows.

For specific domain applications and examples, see [Examples and Tutorials](#5). For development guidelines and testing infrastructure, see [Development Guide](#6). For detailed implementation of domain adaptation techniques that utilize these pipeline components, see [Domain Adaptation](#3).

## Core Pipeline Architecture

PyKale's pipeline-based API follows a systematic approach to machine learning workflows, organizing functionality into six core modules that can be combined flexibly while maintaining standardization and reusability.

### Pipeline Flow Overview

```mermaid
graph TB
    subgraph "Data Pipeline"
        LOADDATA["kale.loaddata<br/>dataset_access.MultiDomainDatasets<br/>video_access.VideoFrameDataset<br/>molecular_datasets.BindingDBDataset"]
        PREPDATA["kale.prepdata<br/>image_transform.ImageTransform<br/>video_transform.VideoTransform<br/>chem_transform.mol_graph_transform"]
    end
    
    subgraph "Model Pipeline"
        EMBED["kale.embed<br/>image_cnn.SmallCNN<br/>video.i3d.InceptionI3d<br/>gcn.GCNConv"]
        PREDICT["kale.predict<br/>class_domain_nets.ClassNetSmallImage<br/>decode.DecodingNet<br/>isonet.ISONet"]
    end
    
    subgraph "Analysis Pipeline"
        EVALUATE["kale.evaluate<br/>metrics.Accuracy<br/>cross_validation.LeaveOneDomainOut<br/>uncertainty_metrics.ECELoss"]
        INTERPRET["kale.interpret<br/>visualize.plot_tsne<br/>uncertainty_quantiles.uncertainty_quantile_binning"]
    end
    
    subgraph "Orchestration"
        PIPELINE["kale.pipeline<br/>base_nn_trainer.BaseNNTrainer<br/>domain_adapter.BaseAdaptTrainer<br/>deepdta.DeepDTATrainer"]
        UTILS["kale.utils<br/>seed.set_seed<br/>logger.construct_logger<br/>download.download_file"]
    end
    
    LOADDATA --> PREPDATA
    PREPDATA --> EMBED
    EMBED --> PREDICT
    PREDICT --> EVALUATE
    EVALUATE --> INTERPRET
    
    PIPELINE --> LOADDATA
    PIPELINE --> PREPDATA
    PIPELINE --> EMBED
    PIPELINE --> PREDICT
    PIPELINE --> EVALUATE
    PIPELINE --> INTERPRET
    
    UTILS --> PIPELINE
    UTILS --> LOADDATA
    UTILS --> PREPDATA
    UTILS --> EMBED
    UTILS --> PREDICT
    UTILS --> EVALUATE
    UTILS --> INTERPRET
```

**Sources:** [README.md:35-43](), [docs/source/index.rst:22-31]()

### Module Dependencies and Integration

```mermaid
graph TB
    subgraph "Core Dependencies"
        PYTORCH["torch<br/>PyTorch Framework"]
        LIGHTNING["pytorch_lightning<br/>Training Infrastructure"]
        NUMPY["numpy<br/>Numerical Computing"]
        SKLEARN["scikit_learn<br/>ML Utilities"]
    end
    
    subgraph "Optional Dependencies"
        PYGEOMETRIC["torch_geometric<br/>Graph Neural Networks"]
        TDC["PyTDC<br/>Drug Discovery"]
        RDKIT["rdkit<br/>Chemical Informatics"]
        DICOM["pydicom<br/>Medical Imaging"]
    end
    
    subgraph "kale.loaddata"
        DATASET_ACCESS["dataset_access"]
        VIDEO_ACCESS["video_access"]
        MOLECULAR_DATASETS["molecular_datasets"]
        MULTI_DOMAIN["multi_domain"]
        SAMPLER["sampler"]
    end
    
    subgraph "kale.embed"
        IMAGE_CNN["image_cnn"]
        VIDEO_I3D["video_i3d"]
        GCN["gcn"]
        GRIPNET["gripnet"]
        FEATURE_FUSION["feature_fusion"]
    end
    
    subgraph "kale.pipeline"
        BASE_TRAINER["base_nn_trainer"]
        DOMAIN_ADAPTER["domain_adapter"]
        MULTI_DOMAIN_ADAPTER["multi_domain_adapter"]
        VIDEO_DOMAIN_ADAPTER["video_domain_adapter"]
    end
    
    PYTORCH --> BASE_TRAINER
    LIGHTNING --> BASE_TRAINER
    PYGEOMETRIC --> GCN
    PYGEOMETRIC --> GRIPNET
    TDC --> MOLECULAR_DATASETS
    RDKIT --> MOLECULAR_DATASETS
    
    BASE_TRAINER --> DOMAIN_ADAPTER
    BASE_TRAINER --> MULTI_DOMAIN_ADAPTER
    BASE_TRAINER --> VIDEO_DOMAIN_ADAPTER
    
    DATASET_ACCESS --> MULTI_DOMAIN
    VIDEO_ACCESS --> VIDEO_I3D
    IMAGE_CNN --> FEATURE_FUSION
    GCN --> FEATURE_FUSION
```

**Sources:** [setup.py:16-26](), [setup.py:30-46]()

## Data Loading Module (kale.loaddata)

The `kale.loaddata` module provides unified interfaces for accessing diverse data sources including images, videos, molecular data, and multimodal datasets. It implements standardized dataset access patterns and sampling strategies.

### Key Components

| Component | Purpose | Key Classes |
|-----------|---------|-------------|
| `dataset_access` | Core dataset access interface | `DatasetAccess`, `MultiDomainDatasets` |
| `video_access` | Video dataset loading | `VideoFrameDataset`, `VideoDataset` |
| `molecular_datasets` | Drug discovery datasets | `BindingDBDataset`, `TDCDataset` |
| `multi_domain` | Multi-source domain datasets | `MultiDomainDatasets` |
| `sampler` | Sampling strategies | `ImbalancedDatasetSampler`, `RandomMultiDomainSampler` |

### Dataset Access Pattern

```mermaid
graph TB
    subgraph "Data Sources"
        IMAGES["Images<br/>CIFAR, Office, USPS"]
        VIDEOS["Videos<br/>EPIC-KITCHENS, ADL"]
        MOLECULES["Molecules<br/>BindingDB, TDC"]
        MULTIOMICS["Multiomics<br/>Cancer Datasets"]
        MEDICAL["Medical<br/>CMR, Neuroimaging"]
    end
    
    subgraph "Access Layer"
        DATASET_ACCESS["dataset_access<br/>MultiDomainDatasets"]
        VIDEO_ACCESS["video_access<br/>VideoFrameDataset"]
        MOLECULAR_ACCESS["molecular_datasets<br/>BindingDBDataset"]
        TABULAR_ACCESS["tabular_access<br/>TabularDataset"]
        SIGNAL_ACCESS["signal_access<br/>SignalDataset"]
    end
    
    subgraph "Sampling Layer"
        BALANCED_SAMPLER["sampler<br/>ImbalancedDatasetSampler"]
        MULTI_DOMAIN_SAMPLER["sampler<br/>RandomMultiDomainSampler"]
        FEW_SHOT_SAMPLER["few_shot<br/>FewShotSampler"]
    end
    
    subgraph "Output"
        DATALOADERS["PyTorch<br/>DataLoaders"]
    end
    
    IMAGES --> DATASET_ACCESS
    VIDEOS --> VIDEO_ACCESS
    MOLECULES --> MOLECULAR_ACCESS
    MULTIOMICS --> TABULAR_ACCESS
    MEDICAL --> SIGNAL_ACCESS
    
    DATASET_ACCESS --> BALANCED_SAMPLER
    VIDEO_ACCESS --> MULTI_DOMAIN_SAMPLER
    MOLECULAR_ACCESS --> FEW_SHOT_SAMPLER
    
    BALANCED_SAMPLER --> DATALOADERS
    MULTI_DOMAIN_SAMPLER --> DATALOADERS
    FEW_SHOT_SAMPLER --> DATALOADERS
```

**Sources:** [docs/source/kale.loaddata.rst:1-169](), [examples/video_loading/README.md:9-25]()

## Feature Embedding Module (kale.embed)

The `kale.embed` module implements feature extraction and representation learning across multiple modalities. It provides CNN architectures, video models, graph neural networks, and multimodal fusion techniques.

### Architecture Components

| Component | Purpose | Key Classes |
|-----------|---------|-------------|
| `image_cnn` | CNN feature extraction | `SmallCNN`, `ResNet18`, `ResNet50` |
| `video_i3d` | Video feature extraction | `InceptionI3d`, `I3DBackbone` |
| `gcn` | Graph convolution | `GCNConv`, `GCNNet` |
| `gripnet` | Heterogeneous graphs | `GripNet`, `HeteroGCN` |
| `feature_fusion` | Multimodal fusion | `ConcateFusion`, `AttentionFusion` |

### Embedding Architecture

```mermaid
graph TB
    subgraph "Input Modalities"
        IMAGES["Images<br/>RGB, Grayscale"]
        VIDEOS["Videos<br/>RGB + Optical Flow"]
        GRAPHS["Graphs<br/>Heterogeneous Networks"]
        SEQUENCES["Sequences<br/>Text, Molecular"]
        SIGNALS["Signals<br/>Time Series, Medical"]
    end
    
    subgraph "Feature Extractors"
        IMAGE_CNN["image_cnn<br/>ResNet, CNN"]
        VIDEO_I3D["video_i3d<br/>InceptionI3d"]
        VIDEO_RES3D["video_res3d<br/>ResNet3D"]
        GCN_EMBED["gcn<br/>GCNConv"]
        GRIPNET_EMBED["gripnet<br/>GripNet"]
        SEQ_NN["seq_nn<br/>CNNEncoder, GCNEncoder"]
        SIGNAL_CNN["signal_cnn<br/>SignalCNN"]
    end
    
    subgraph "Fusion & Processing"
        FEATURE_FUSION["feature_fusion<br/>ConcateFusion, AttentionFusion"]
        ATTENTION_CNN["attention_cnn<br/>AttentionCNN"]
        POSITIONAL_ENCODING["positional_encoding<br/>PositionalEncoding"]
        MULTIMODAL_ENCODER["multimodal_encoder<br/>MultiModalEncoder"]
    end
    
    subgraph "Output"
        EMBEDDINGS["Feature<br/>Embeddings"]
    end
    
    IMAGES --> IMAGE_CNN
    VIDEOS --> VIDEO_I3D
    VIDEOS --> VIDEO_RES3D
    GRAPHS --> GCN_EMBED
    GRAPHS --> GRIPNET_EMBED
    SEQUENCES --> SEQ_NN
    SIGNALS --> SIGNAL_CNN
    
    IMAGE_CNN --> FEATURE_FUSION
    VIDEO_I3D --> FEATURE_FUSION
    GCN_EMBED --> FEATURE_FUSION
    SEQ_NN --> POSITIONAL_ENCODING
    SIGNAL_CNN --> ATTENTION_CNN
    
    FEATURE_FUSION --> MULTIMODAL_ENCODER
    ATTENTION_CNN --> MULTIMODAL_ENCODER
    POSITIONAL_ENCODING --> MULTIMODAL_ENCODER
    
    MULTIMODAL_ENCODER --> EMBEDDINGS
```

**Sources:** [docs/source/kale.embed.rst:1-172](), [tests/embed/test_seq_nn.py:1-49]()

## Training Pipeline Module (kale.pipeline)

The `kale.pipeline` module orchestrates training workflows through specialized trainers built on PyTorch Lightning. It provides domain adaptation, multimodal learning, and application-specific training pipelines.

### Trainer Architecture

| Component | Purpose | Key Classes |
|-----------|---------|-------------|
| `base_nn_trainer` | Base training infrastructure | `BaseNNTrainer`, `LightningModule` |
| `domain_adapter` | Domain adaptation training | `BaseAdaptTrainer`, `DANNTrainer` |
| `multi_domain_adapter` | Multi-source DA training | `MultiDomainAdaptTrainer` |
| `video_domain_adapter` | Video DA training | `VideoDANNTrainer` |
| `deepdta` | Drug-target interaction | `DeepDTATrainer` |
| `multiomics_trainer` | Multiomics analysis | `MultiomicsTrainer` |

### Training Pipeline Flow

```mermaid
graph TB
    subgraph "Configuration"
        YAML_CONFIG["YAML<br/>Configuration"]
        PYTHON_CONFIG["Python<br/>Configuration"]
    end
    
    subgraph "Base Infrastructure"
        BASE_TRAINER["base_nn_trainer<br/>BaseNNTrainer"]
        LIGHTNING_MODULE["PyTorch Lightning<br/>LightningModule"]
    end
    
    subgraph "Specialized Trainers"
        DOMAIN_ADAPTER["domain_adapter<br/>BaseAdaptTrainer"]
        MULTI_DOMAIN_ADAPTER["multi_domain_adapter<br/>MultiDomainAdaptTrainer"]
        VIDEO_DOMAIN_ADAPTER["video_domain_adapter<br/>VideoDANNTrainer"]
        DEEPDTA_TRAINER["deepdta<br/>DeepDTATrainer"]
        MULTIOMICS_TRAINER["multiomics_trainer<br/>MultiomicsTrainer"]
        MPCA_TRAINER["mpca_trainer<br/>MPCATrainer"]
    end
    
    subgraph "Training Components"
        OPTIMIZERS["Optimizers<br/>Adam, SGD"]
        SCHEDULERS["Schedulers<br/>StepLR, CosineAnnealingLR"]
        CALLBACKS["Callbacks<br/>EarlyStopping, ModelCheckpoint"]
        LOGGERS["Loggers<br/>TensorBoard, WandB"]
    end
    
    YAML_CONFIG --> BASE_TRAINER
    PYTHON_CONFIG --> BASE_TRAINER
    BASE_TRAINER --> LIGHTNING_MODULE
    
    LIGHTNING_MODULE --> DOMAIN_ADAPTER
    LIGHTNING_MODULE --> MULTI_DOMAIN_ADAPTER
    LIGHTNING_MODULE --> VIDEO_DOMAIN_ADAPTER
    LIGHTNING_MODULE --> DEEPDTA_TRAINER
    LIGHTNING_MODULE --> MULTIOMICS_TRAINER
    LIGHTNING_MODULE --> MPCA_TRAINER
    
    BASE_TRAINER --> OPTIMIZERS
    BASE_TRAINER --> SCHEDULERS
    BASE_TRAINER --> CALLBACKS
    BASE_TRAINER --> LOGGERS
```

**Sources:** [docs/source/kale.pipeline.rst:1-96](), [setup.py:20]()

## Data Preprocessing Module (kale.prepdata)

The `kale.prepdata` module provides data transformation and preprocessing functionality for different modalities including images, videos, signals, and molecular data.

### Preprocessing Components

| Component | Purpose | Key Classes |
|-----------|---------|-------------|
| `image_transform` | Image preprocessing | `ImageTransform`, `Resize`, `Normalize` |
| `video_transform` | Video preprocessing | `VideoTransform`, `ImglistToTensor` |
| `signal_transform` | Signal preprocessing | `SignalTransform`, `Standardize` |
| `chem_transform` | Chemical preprocessing | `ChemTransform`, `MoleculeTransform` |
| `tabular_transform` | Tabular preprocessing | `TabularTransform`, `StandardScaler` |

**Sources:** [docs/source/kale.prepdata.rst:1-87]()

## Prediction Module (kale.predict)

The `kale.predict` module implements prediction models and classification networks, including domain adaptation networks and uncertainty quantification.

### Prediction Components

| Component | Purpose | Key Classes |
|-----------|---------|-------------|
| `class_domain_nets` | Classification networks | `ClassNetSmallImage`, `DomainNetSmallImage` |
| `decode` | Decoding networks | `DecodingNet`, `FeatureDecoder` |
| `isonet` | Isometric networks | `ISONet`, `ISONetClassifier` |
| `uncertainty_binning` | Uncertainty quantification | `UncertaintyBinning`, `QuantileBinning` |

**Sources:** [docs/source/kale.predict.rst:1-48]()

## Evaluation Module (kale.evaluate)

The `kale.evaluate` module provides performance evaluation metrics, cross-validation strategies, and similarity measures for various machine learning tasks.

### Evaluation Components

| Component | Purpose | Key Classes |
|-----------|---------|-------------|
| `metrics` | Performance metrics | `Accuracy`, `F1Score`, `AUC` |
| `cross_validation` | CV strategies | `StratifiedKFold`, `GroupKFold` |
| `similarity_metrics` | Similarity measures | `MMD`, `HSIC`, `CKA` |
| `uncertainty_metrics` | Uncertainty evaluation | `CalibrationError`, `Reliability` |

**Sources:** [docs/source/kale.evaluate.rst:1-47]()

## Interpretation Module (kale.interpret)

The `kale.interpret` module provides model interpretation and visualization tools for understanding model behavior and predictions.

### Interpretation Components

| Component | Purpose | Key Classes |
|-----------|---------|-------------|
| `model_weights` | Weight analysis | `WeightAnalysis`, `ModelInspection` |
| `visualize` | Visualization tools | `PlotUtils`, `TensorboardUtils` |
| `uncertainty_quantiles` | Uncertainty analysis | `QuantileAnalysis`, `UncertaintyPlot` |
| `signal_image_attribution` | Attribution methods | `GradCAM`, `IntegratedGradients` |

**Sources:** [docs/source/kale.interpret.rst:1-49]()

## Utilities Module (kale.utils)

The `kale.utils` module provides supporting utilities for logging, initialization, data handling, and other common operations across the pipeline.

### Utility Components

| Component | Purpose | Key Classes |
|-----------|---------|-------------|
| `logger` | Logging utilities | `Logger`, `LoggerConfig` |
| `seed` | Reproducibility | `set_seed`, `seed_everything` |
| `download` | Data downloading | `download_file`, `extract_archive` |
| `initialize_nn` | Network initialization | `init_weights`, `init_modules` |

**Sources:** [docs/source/kale.utils.rst:1-72]()

## Pipeline Integration Patterns

### Standard Pipeline Workflow

```mermaid
graph LR
    subgraph "Data Stage"
        LOAD["loaddata<br/>MultiDomainDatasets"]
        PREP["prepdata<br/>ImageTransform"]
    end
    
    subgraph "Model Stage"
        EMBED["embed<br/>ResNet18"]
        PREDICT["predict<br/>ClassNetSmallImage"]
    end
    
    subgraph "Analysis Stage"
        EVAL["evaluate<br/>Accuracy"]
        INTERPRET["interpret<br/>GradCAM"]
    end
    
    subgraph "Orchestration"
        PIPELINE["pipeline<br/>BaseAdaptTrainer"]
    end
    
    LOAD --> PREP
    PREP --> EMBED
    EMBED --> PREDICT
    PREDICT --> EVAL
    EVAL --> INTERPRET
    
    PIPELINE --> LOAD
    PIPELINE --> PREP
    PIPELINE --> EMBED
    PIPELINE --> PREDICT
    PIPELINE --> EVAL
    PIPELINE --> INTERPRET
```

**Sources:** [README.md:35-43](), [docs/source/index.rst:33]()

---

