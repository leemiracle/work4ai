# Page: Overview

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [docs/source/getting_started/advanced.rst](docs/source/getting_started/advanced.rst)
- [docs/source/getting_started/benchmarks.rst](docs/source/getting_started/benchmarks.rst)
- [docs/source/getting_started/benchmarks/cifar10_benchmark.py](docs/source/getting_started/benchmarks/cifar10_benchmark.py)
- [docs/source/getting_started/benchmarks/imagenet100_benchmark.py](docs/source/getting_started/benchmarks/imagenet100_benchmark.py)
- [docs/source/getting_started/benchmarks/imagenette_benchmark.py](docs/source/getting_started/benchmarks/imagenette_benchmark.py)
- [docs/source/getting_started/command_line_tool.rst](docs/source/getting_started/command_line_tool.rst)
- [docs/source/getting_started/images/lightly_overview.png](docs/source/getting_started/images/lightly_overview.png)
- [docs/source/getting_started/install.rst](docs/source/getting_started/install.rst)
- [docs/source/getting_started/lightly_at_a_glance.rst](docs/source/getting_started/lightly_at_a_glance.rst)
- [docs/source/getting_started/main_concepts.rst](docs/source/getting_started/main_concepts.rst)
- [docs/source/index.rst](docs/source/index.rst)
- [docs/source/lightly.models.rst](docs/source/lightly.models.rst)
- [docs/source/lightly.models.utils.rst](docs/source/lightly.models.utils.rst)
- [lightly/__init__.py](lightly/__init__.py)
- [lightly/api/_version_checking.py](lightly/api/_version_checking.py)
- [tests/api/test_version_checking.py](tests/api/test_version_checking.py)
- [tests/api_workflow/test_api_workflow_client.py](tests/api_workflow/test_api_workflow_client.py)
- [tests/conftest.py](tests/conftest.py)

</details>



**Lightly** is a computer vision framework for self-supervised learning (SSL) built on top of PyTorch. It enables training deep learning models without labeled data, helping users understand and work with large unlabeled datasets through self-supervised pre-training and active learning workflows.

This page provides a high-level introduction to the Lightly framework architecture, covering its major subsystems and how they relate to each other. For detailed information about specific subsystems, see:
- Self-supervised learning models and architectures: [2](#2)
- Data handling and processing: [3](#3)
- Command-line interface usage: [4](#4)
- Programmatic Python API: [5](#5)
- Platform integration and API workflows: [6](#6)
- Benchmarking and evaluation: [7](#7)

Sources: [lightly/__init__.py:1-93](), [README.md:1-438]()

## Purpose and Scope

The Lightly framework provides a modular, PyTorch-compatible toolkit for self-supervised learning with three primary use cases:

1. **Local Training**: Train SSL models (SimCLR, MoCo, BYOL, DINO, etc.) on local datasets without requiring labels
2. **Feature Extraction**: Generate embeddings from pre-trained models for downstream tasks
3. **Platform Integration**: Connect to the Lightly Platform for dataset management, compute worker scheduling, and active learning workflows

The framework exposes both low-level building blocks (loss functions, projection heads, transforms) and high-level abstractions (CLI commands, one-line training functions) to support users at different expertise levels.

Sources: [lightly/__init__.py:1-72](), [README.md:14-27]()

## Framework Architecture

The following diagram shows how the major code modules in the Lightly package relate to each other:

```mermaid
graph TB
    subgraph "User Entry Points"
        CLI["CLI Commands<br/>lightly.cli"]
        Core["lightly.core<br/>train_model_and_embed_images<br/>train_embedding_model<br/>embed_images"]
        DirectImport["Direct Import<br/>import lightly"]
    end
    
    subgraph "Core Framework Modules"
        Data["lightly.data<br/>LightlyDataset<br/>VideoDataset<br/>LightlyDataLoader"]
        Models["lightly.models<br/>ResNetGenerator<br/>heads<br/>modules<br/>utils"]
        Loss["lightly.loss<br/>NTXentLoss<br/>NegativeCosineSimilarity<br/>DINOLoss<br/>BarlowTwinsLoss"]
        Transforms["lightly.transforms<br/>SimCLRTransform<br/>DINOTransform<br/>MultiViewTransform"]
        Benchmarking["lightly.utils.benchmarking<br/>BenchmarkModule<br/>kNN evaluation"]
    end
    
    subgraph "Platform Integration Modules"
        ApiWorkflow["lightly.api<br/>ApiWorkflowClient<br/>_DatasetsMixin<br/>_ComputeWorkerMixin"]
        OpenAPI["lightly.openapi_generated<br/>DatasetsApi<br/>SamplesApi<br/>EmbeddingsApi"]
        Utils["lightly.api.utils<br/>retry logic<br/>pagination"]
    end
    
    subgraph "Configuration & Infrastructure"
        Config["config.yaml<br/>Hydra configuration"]
        Version["lightly.api._version_checking<br/>check_is_latest_version_in_background"]
    end
    
    CLI --> Config
    CLI --> Data
    CLI --> Models
    CLI --> Loss
    Core --> Data
    Core --> Models
    Core --> Loss
    DirectImport --> Version
    
    Data --> Transforms
    Models --> Loss
    Benchmarking --> Models
    Benchmarking --> Data
    
    ApiWorkflow --> OpenAPI
    ApiWorkflow --> Utils
    CLI --> ApiWorkflow
    Core --> ApiWorkflow
    
    style CLI fill:#e8f4f8
    style ApiWorkflow fill:#f8e8e8
    style Models fill:#e8f8e8
```

Sources: [lightly/__init__.py:10-72](), [README.md:40-77]()

## Core Subsystems

The Lightly framework is organized into distinct modules, each handling a specific aspect of the self-supervised learning workflow:

| Module | Purpose | Key Classes/Functions |
|--------|---------|----------------------|
| **lightly.models** | SSL model architectures, backbones, projection/prediction heads | `ResNetGenerator`, `heads.SimCLRProjectionHead`, `heads.BYOLPredictionHead`, `heads.DINOProjectionHead`, `utils.update_momentum` |
| **lightly.loss** | Self-supervised loss functions | `NTXentLoss`, `NegativeCosineSimilarity`, `DINOLoss`, `BarlowTwinsLoss`, `VICRegLoss`, `SwaVLoss` |
| **lightly.data** | Dataset wrappers and data loading | `LightlyDataset`, `VideoDataset`, `LightlyDataLoader` |
| **lightly.transforms** | Data augmentation pipelines for SSL | `SimCLRTransform`, `DINOTransform`, `BYOLTransform`, `MultiViewTransform` |
| **lightly.cli** | Command-line interface | `lightly-ssl-train`, `lightly-embed`, `lightly-magic`, `lightly-download` |
| **lightly.core** | High-level training API | `train_model_and_embed_images()`, `train_embedding_model()`, `embed_images()` |
| **lightly.api** | Platform integration client | `ApiWorkflowClient`, `_DatasetsMixin`, `_ComputeWorkerMixin`, `_UploadEmbeddingsMixin` |
| **lightly.utils** | Utilities and benchmarking | `BenchmarkModule`, `LARS`, `scheduler`, `io` |

Sources: [lightly/__init__.py:10-72](), [README.md:40-77]()

## User Interfaces

Lightly provides three ways to interact with the framework, each suited to different workflows:

```mermaid
graph LR
    subgraph "Interface Options"
        CLI["Command-Line Interface<br/>lightly.cli._train_cli<br/>lightly.cli._embed_cli<br/>lightly.cli._lightly_cli"]
        PythonAPI["Python API<br/>lightly.core.train_model_and_embed_images<br/>lightly.core.train_embedding_model<br/>lightly.core.embed_images"]
        DirectUse["Direct Module Import<br/>from lightly import loss<br/>from lightly.data import LightlyDataset<br/>from lightly.models.modules import heads"]
    end
    
    subgraph "Configuration"
        Hydra["Hydra Framework<br/>config.yaml overrides"]
        EnvVars["Environment Variables<br/>LIGHTLY_SERVER_LOCATION<br/>LIGHTLY_DID_VERSION_CHECK"]
    end
    
    subgraph "Implementation"
        TrainImpl["Training Implementation<br/>PyTorch Lightning Trainer<br/>BenchmarkModule"]
        EmbedImpl["Embedding Implementation<br/>torch.no_grad feature extraction"]
    end
    
    CLI --> Hydra
    CLI --> TrainImpl
    CLI --> EmbedImpl
    PythonAPI --> TrainImpl
    PythonAPI --> EmbedImpl
    DirectUse --> TrainImpl
    
    EnvVars -.environment.-> CLI
    EnvVars -.environment.-> PythonAPI
```

### 1. Command-Line Interface (CLI)

The CLI provides executable commands for common workflows, configured via `config.yaml` with Hydra overrides:

- **`lightly-ssl-train`**: Train self-supervised models
- **`lightly-embed`**: Generate embeddings from trained models
- **`lightly-magic`**: Combined training and embedding pipeline
- **`lightly-crop`**: Preprocess images for object detection
- **`lightly-download`**: Download datasets from the Lightly Platform

Sources: [lightly/__init__.py:16-20](), [README.md:94-278]()

### 2. Python API (lightly.core)

The `lightly.core` module provides high-level functions for programmatic use:

- `train_model_and_embed_images()`: Train a model and generate embeddings in one call
- `train_embedding_model()`: Train a self-supervised model only
- `embed_images()`: Generate embeddings from a trained model

Sources: [lightly/__init__.py:22-24]()

### 3. Direct Module Import

For maximum flexibility, users can import individual components directly:

```python
from lightly.data import LightlyDataset
from lightly.loss import NTXentLoss
from lightly.models.modules import heads
from lightly.transforms import SimCLRTransform
```

This approach allows custom training loops with full control over model architecture, loss functions, and data augmentation.

Sources: [README.md:125-219]()

## Training and Evaluation Workflow

The following diagram illustrates the complete data flow from raw images through training to evaluation:

```mermaid
graph TD
    subgraph "Data Input"
        RawData["Raw Images/Videos<br/>Local or Cloud Storage"]
    end
    
    subgraph "Data Loading"
        Dataset["LightlyDataset<br/>VideoDataset"]
        Transform["Transform Pipeline<br/>SimCLRTransform<br/>DINOTransform"]
        Dataloader["torch.utils.data.DataLoader"]
    end
    
    subgraph "Model Components"
        Backbone["Backbone Network<br/>ResNet / ViT / ConvNeXt<br/>from torchvision or timm"]
        ProjHead["Projection Head<br/>SimCLRProjectionHead<br/>DINOProjectionHead"]
        PredHead["Prediction Head<br/>SimSiamPredictionHead<br/>BYOLPredictionHead"]
    end
    
    subgraph "Training"
        SSLLoss["SSL Loss<br/>NTXentLoss<br/>DINOLoss<br/>BarlowTwinsLoss"]
        Trainer["PyTorch Lightning Trainer<br/>or custom training loop"]
    end
    
    subgraph "Outputs"
        Checkpoint["Model Checkpoint<br/>.ckpt or .pth file"]
        Embeddings["Embeddings<br/>CSV format<br/>lightly.utils.io"]
    end
    
    subgraph "Evaluation"
        KNN["BenchmarkModule<br/>kNN evaluation"]
        Linear["Linear Probing"]
        Finetune["Fine-tuning"]
    end
    
    RawData --> Dataset
    Dataset --> Transform
    Transform --> Dataloader
    Dataloader --> Backbone
    Backbone --> ProjHead
    ProjHead --> PredHead
    ProjHead --> SSLLoss
    SSLLoss --> Trainer
    Trainer --> Checkpoint
    Checkpoint --> Embeddings
    Embeddings --> KNN
    Checkpoint --> Linear
    Checkpoint --> Finetune
```

Sources: [README.md:125-278](), [docs/source/getting_started/benchmarks.rst:1-219]()

### Supported SSL Algorithms

Lightly implements over 20 state-of-the-art self-supervised learning algorithms with full PyTorch and PyTorch Lightning support:

| Algorithm | Year | Loss Function | Key Components |
|-----------|------|---------------|----------------|
| SimCLR | 2020 | `NTXentLoss` | `SimCLRProjectionHead`, `SimCLRTransform` |
| MoCo | 2019 | `NTXentLoss` + memory bank | `MoCoProjectionHead`, momentum encoder |
| SimSiam | 2021 | `NegativeCosineSimilarity` | `SimSiamProjectionHead`, `SimSiamPredictionHead` |
| BYOL | 2020 | `NegativeCosineSimilarity` | `BYOLProjectionHead`, `BYOLPredictionHead`, momentum encoder |
| DINO | 2021 | `DINOLoss` | `DINOProjectionHead`, teacher-student architecture |
| Barlow Twins | 2021 | `BarlowTwinsLoss` | `BarlowTwinsProjectionHead`, redundancy reduction |
| VICReg | 2021 | `VICRegLoss` | `VICRegProjectionHead`, variance-covariance regularization |
| SwAV | 2020 | `SwaVLoss` | `SwaVProjectionHead`, `SwaVPrototypes`, online clustering |
| MAE | 2021 | MSE reconstruction | `MAEDecoderTIMM`, masked autoencoder for ViT |

Sources: [README.md:55-77](), [docs/source/getting_started/benchmarks.rst:30-46]()

## Platform Integration Overview

The `ApiWorkflowClient` class in `lightly.api` provides integration with the Lightly Platform for:

- **Dataset Management**: Create, update, and delete datasets
- **Compute Worker Orchestration**: Schedule and monitor worker runs for large-scale processing
- **Embeddings Upload/Download**: Sync embeddings with the platform
- **Sample Operations**: Upload metadata, manage tags, and create selections
- **Datasource Configuration**: Configure cloud storage connections (S3, Azure, GCS)

The client uses a mixin architecture, composing functionality from specialized mixins (`_DatasetsMixin`, `_ComputeWorkerMixin`, `_UploadEmbeddingsMixin`, etc.) that delegate to OpenAPI-generated clients for HTTP communication.

For detailed platform integration documentation, see [6](#6).

Sources: [lightly/api/api_workflow_client.py]() (inferred from test), [tests/api_workflow/test_api_workflow_client.py:10-103]()

## Version Management

Lightly automatically checks for version compatibility on import to ensure compatibility with the Lightly Platform API:

```mermaid
graph LR
    Import["import lightly"]
    Check["lightly.api._version_checking<br/>check_is_latest_version_in_background"]
    EnvCheck["Check LIGHTLY_DID_VERSION_CHECK"]
    Thread["Background Thread"]
    VersionAPI["VersioningApi<br/>get_latest_pip_version<br/>get_minimum_compatible_pip_version"]
    
    Import --> EnvCheck
    EnvCheck -->|not set| Check
    Check --> Thread
    Thread --> VersionAPI
    VersionAPI -.warning.-> User["User Console"]
```

The version check runs in a background thread to avoid blocking package import. It can be disabled by setting the `LIGHTLY_DID_VERSION_CHECK` environment variable to `"True"`.

Sources: [lightly/__init__.py:83-92](), [lightly/api/_version_checking.py:1-74](), [tests/api/test_version_checking.py:1-88]()

## Benchmarking and Evaluation

The framework includes comprehensive benchmarking infrastructure to evaluate SSL models on standard datasets:

| Dataset | Classes | Training Images | Evaluation Protocol | Backbone Options |
|---------|---------|-----------------|---------------------|------------------|
| ImageNet1k | 1,000 | 1.28M | kNN, Linear, Fine-tune | ResNet-50, ViT-S/16, ViT-B/16 |
| ImageNet100 | 100 | 130k | kNN | ResNet-18 |
| Imagenette | 10 | 9,469 | kNN | ResNet-18, ViT-S |
| CIFAR-10 | 10 | 50k | kNN | ResNet-18 (3x3 conv) |

The `BenchmarkModule` class in `lightly.utils.benchmarking` provides kNN evaluation during training using PyTorch Lightning callbacks. Evaluation results for all supported algorithms on ImageNet1k are available in the repository.

Sources: [docs/source/getting_started/benchmarks.rst:1-219](), [docs/source/getting_started/benchmarks/imagenette_benchmark.py:1-708](), [docs/source/getting_started/benchmarks/cifar10_benchmark.py:1-596](), [docs/source/getting_started/benchmarks/imagenet100_benchmark.py:1-501]()

## Installation and Dependencies

Lightly requires:
- Python 3.7+ (Python 3.13 not yet supported)
- PyTorch >= 1.11.0
- Torchvision >= 0.12.0  
- PyTorch Lightning >= 1.7.1

Install via pip:
```bash
pip3 install lightly
```

The framework is compatible with PyTorch and PyTorch Lightning v2.0+.

Sources: [README.md:96-116]()

## Next Steps

- **Model Training**: See [2](#2) for details on SSL algorithms and model components
- **Data Handling**: See [3](#3) for dataset wrappers and transform pipelines
- **CLI Usage**: See [4](#4) for command-line training and embedding workflows
- **Python API**: See [5](#5) for programmatic training interfaces
- **Platform Integration**: See [6](#6) for dataset management and compute worker orchestration
- **Benchmarking**: See [7](#7) for evaluation protocols and performance metrics
- **Examples**: See [8](#8) for practical tutorials and code examples

Sources: [README.md:78-93](), [docs/source/getting_started/benchmarks.rst:215-219]()

---

# Page: Self-Supervised Learning Models

# Self-Supervised Learning Models

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/check_example_nbs.yml](.github/workflows/check_example_nbs.yml)
- [.github/workflows/discord_release_notification.yml](.github/workflows/discord_release_notification.yml)
- [Makefile](Makefile)
- [README.md](README.md)
- [benchmarks/imagenet/vitb16/dinov2.py](benchmarks/imagenet/vitb16/dinov2.py)
- [benchmarks/imagenet/vitb16/ibot.py](benchmarks/imagenet/vitb16/ibot.py)
- [docs/source/getting_started/benchmarks.rst](docs/source/getting_started/benchmarks.rst)
- [docs/source/getting_started/benchmarks/cifar10_benchmark.py](docs/source/getting_started/benchmarks/cifar10_benchmark.py)
- [docs/source/getting_started/benchmarks/imagenet100_benchmark.py](docs/source/getting_started/benchmarks/imagenet100_benchmark.py)
- [docs/source/getting_started/benchmarks/imagenette_benchmark.py](docs/source/getting_started/benchmarks/imagenette_benchmark.py)
- [lightly/loss/pmsn_loss.py](lightly/loss/pmsn_loss.py)
- [lightly/models/modules/__init__.py](lightly/models/modules/__init__.py)
- [lightly/models/modules/heads.py](lightly/models/modules/heads.py)
- [lightly/models/modules/ijepa_timm.py](lightly/models/modules/ijepa_timm.py)
- [lightly/models/modules/masked_autoencoder_timm.py](lightly/models/modules/masked_autoencoder_timm.py)
- [lightly/models/modules/masked_vision_transformer_timm.py](lightly/models/modules/masked_vision_transformer_timm.py)
- [lightly/models/utils.py](lightly/models/utils.py)
- [pyproject.toml](pyproject.toml)
- [tests/loss/test_msn_loss.py](tests/loss/test_msn_loss.py)
- [tests/loss/test_pmsn_loss.py](tests/loss/test_pmsn_loss.py)
- [tests/models/modules/test_masked_autoencoder.py](tests/models/modules/test_masked_autoencoder.py)
- [tests/models/test_ModelUtils.py](tests/models/test_ModelUtils.py)
- [tests/models/test_ProjectionHeads.py](tests/models/test_ProjectionHeads.py)

</details>



This page provides an overview of the self-supervised learning (SSL) model implementations in Lightly. It explains how models are composed from modular building blocks and lists the 19+ supported SSL algorithms. For detailed information about specific components, see:

- **Page 2.1** - Model Architectures (backbones)
- **Page 2.2** - Model Components and Utilities (heads, momentum encoders, utilities)
- **Page 2.3** - Loss Functions
- **Page 2.4** - Transforms and Augmentations

## Modular SSL Architecture

Lightly implements SSL models using a modular architecture where each model is composed from interchangeable components:

1. **Backbone networks** - Feature extractors (ResNet, Vision Transformers) - See page 2.1
2. **Projection heads** - Transform features into embedding space - See page 2.2
3. **Prediction heads** - Optional asymmetric networks (SimSiam, BYOL) - See page 2.2
4. **Loss functions** - Define training objectives (contrastive, distillation, masking) - See page 2.3
5. **Transforms** - Generate augmented views for training - See page 2.4

This modularity allows researchers to experiment with different combinations and implement new SSL methods by reusing existing components.

SSL Model Composition Architecture:

```mermaid
graph TB
    subgraph "1. Data Augmentation"
        Images["Input Images"] --> Transform["Transform<br/>(lightly.transforms)"]
        Transform --> View0["View 0"]
        Transform --> View1["View 1"]
        Transform --> ViewN["View N"]
    end
    
    subgraph "2. Backbone (Feature Extraction)"
        View0 --> Backbone["Backbone Network<br/>torchvision.models / timm"]
        View1 --> Backbone
        ViewN --> Backbone
        Backbone --> Features["Feature Vectors<br/>shape: (batch, feature_dim)"]
    end
    
    subgraph "3. Projection Head"
        Features --> ProjHead["ProjectionHead<br/>(lightly.models.modules.heads)"]
        ProjHead --> Embeddings["Embeddings<br/>shape: (batch, embed_dim)"]
    end
    
    subgraph "4. Prediction Head (Optional)"
        Embeddings --> PredHead["PredictionHead<br/>(SimSiam, BYOL only)"]
        PredHead --> Predictions["Predictions"]
    end
    
    subgraph "5. Loss Computation"
        Embeddings --> Loss["Loss Function<br/>(lightly.loss)"]
        Predictions --> Loss
        Loss --> LossValue["Scalar Loss"]
    end
    
    subgraph "Optional Components"
        MomentumEncoder["Momentum Encoder<br/>update_momentum()"]
        MemoryBank["Memory Bank<br/>NNMemoryBankModule"]
        Prototypes["Prototypes<br/>SwaVPrototypes"]
    end
    
    MomentumEncoder -.used by.-> Loss
    MemoryBank -.used by.-> Loss
    Prototypes -.used by.-> Loss
```

This diagram shows the typical forward pass through an SSL model. Different SSL methods use different combinations of these components.

Sources:
- [lightly/models/modules/__init__.py:1-57]()
- [lightly/models/modules/heads.py:15-66]()
- [README.md:125-189]()

## Supported SSL Methods

Lightly implements 19+ self-supervised learning methods. Each method is defined by its combination of components:

| Model | Year | Type | Key Components | Paper |
|-------|------|------|----------------|-------|
| SimCLR | 2020 | Contrastive | SimCLRProjectionHead, NTXentLoss | [arxiv](https://arxiv.org/abs/2002.05709) |
| MoCo/MoCoV2 | 2019/2020 | Contrastive + Momentum | MoCoProjectionHead, momentum encoder, memory bank | [arxiv](https://arxiv.org/abs/1911.05722) |
| SimSiam | 2021 | Similarity | SimSiamProjectionHead, SimSiamPredictionHead | [arxiv](https://arxiv.org/abs/2011.10566) |
| BYOL | 2020 | Similarity + Momentum | BYOLProjectionHead, BYOLPredictionHead, momentum encoder | [arxiv](https://arxiv.org/abs/2006.07733) |
| NNCLR | 2021 | Contrastive + NN | NNCLRProjectionHead, NNCLRPredictionHead, NNMemoryBankModule | [arxiv](https://arxiv.org/abs/2104.14548) |
| Barlow Twins | 2021 | Redundancy Reduction | BarlowTwinsProjectionHead, BarlowTwinsLoss | [arxiv](https://arxiv.org/abs/2103.03230) |
| VICReg | 2021 | Variance-Covariance | VICRegProjectionHead, VICRegLoss | [arxiv](https://arxiv.org/abs/2105.04906) |
| SwAV | 2020 | Clustering | SwaVProjectionHead, SwaVPrototypes, SwaVLoss | [arxiv](https://arxiv.org/abs/2006.09882) |
| DINO | 2021 | Distillation | DINOProjectionHead, DINOLoss, momentum teacher | [arxiv](https://arxiv.org/abs/2104.14294) |
| DINOv2 | 2023 | Distillation | DINOv2ProjectionHead, DINOLoss, IBOTPatchLoss | [arxiv](https://arxiv.org/abs/2304.07193) |
| iBOT | 2021 | Distillation + Masking | DINOProjectionHead, DINOLoss, IBOTPatchLoss | [arxiv](https://arxiv.org/abs/2111.07832) |
| MAE | 2021 | Masked Autoencoder | MAEEncoder, MAEDecoder, MSE loss | [arxiv](https://arxiv.org/abs/2111.06377) |
| SimMIM | 2022 | Masked Image Modeling | MaskedVisionTransformer, L1 loss | [arxiv](https://arxiv.org/abs/2111.09886) |
| MSN | 2022 | Masked Siamese | MSNProjectionHead, MSNLoss | [arxiv](https://arxiv.org/abs/2204.07141) |
| PMSN | 2022 | Prototype MSN | MSNProjectionHead, PMSNLoss | [arxiv](https://arxiv.org/abs/2210.07277) |
| DCL/DCLW | 2021 | Decoupled Contrastive | SimCLRProjectionHead, DCLLoss/DCLWLoss | [arxiv](https://arxiv.org/abs/2110.06848) |
| DenseCL | 2021 | Dense Contrastive | DenseCLProjectionHead, NTXentLoss | [arxiv](https://arxiv.org/abs/2011.09157) |
| SMoG | 2022 | Group Momentum | SMoGProjectionHead, SMoGPrototypes | [arxiv](https://arxiv.org/abs/2207.06167) |
| AIM | 2024 | Autoregressive | AIMPredictionHead, masked modeling | [arxiv](https://arxiv.org/abs/2401.08541) |

Sources:
- [README.md:55-76]()
- [docs/source/getting_started/benchmarks.rst:1-219]()
- [lightly/models/modules/heads.py:1-1317]()

## SSL Method Paradigms

SSL methods can be categorized into paradigms based on their learning approach. Each paradigm uses different combinations of components:

SSL Method Paradigms by Learning Approach:

```mermaid
graph TB
    subgraph "Contrastive Learning"
        Contrastive["Maximize agreement between positive pairs<br/>Minimize agreement with negative pairs"]
        SimCLR["SimCLR: NTXentLoss"]
        MoCo["MoCo: NTXentLoss + memory bank"]
        NNCLR["NNCLR: NNMemoryBankModule"]
        DCL["DCL/DCLW: Decoupled loss"]
        Contrastive --> SimCLR
        Contrastive --> MoCo
        Contrastive --> NNCLR
        Contrastive --> DCL
    end
    
    subgraph "Similarity Learning"
        Similarity["Maximize agreement between views<br/>No negative pairs"]
        SimSiam["SimSiam: stop-gradient"]
        BYOL["BYOL: momentum encoder"]
        Similarity --> SimSiam
        Similarity --> BYOL
    end
    
    subgraph "Redundancy Reduction"
        Redundancy["Minimize redundancy in embeddings"]
        BarlowTwins["Barlow Twins: cross-correlation"]
        VICReg["VICReg: variance + covariance"]
        Redundancy --> BarlowTwins
        Redundancy --> VICReg
    end
    
    subgraph "Clustering"
        Clustering["Online clustering of features"]
        SwAV["SwAV: SwaVPrototypes"]
        SMoG["SMoG: group momentum"]
        Clustering --> SwAV
        Clustering --> SMoG
    end
    
    subgraph "Knowledge Distillation"
        Distillation["Student learns from teacher"]
        DINO["DINO: self-distillation"]
        DINOv2["DINOv2: + patch loss"]
        iBOT["iBOT: masked distillation"]
        Distillation --> DINO
        Distillation --> DINOv2
        Distillation --> iBOT
    end
    
    subgraph "Masked Modeling"
        Masked["Predict masked image regions"]
        MAE["MAE: pixel reconstruction"]
        SimMIM["SimMIM: patch prediction"]
        MSN["MSN/PMSN: prototype prediction"]
        Masked --> MAE
        Masked --> SimMIM
        Masked --> MSN
    end
```

Sources:
- [README.md:55-76]()
- [lightly/models/modules/heads.py:1-630]()
- [lightly/loss/]()

## Model Composition Examples

Different SSL methods are composed from different combinations of components. Here are examples:

Component Composition for Common SSL Methods:

| Method | Backbone | Projection Head | Prediction Head | Momentum Encoder | Memory Bank | Loss Function |
|--------|----------|----------------|-----------------|------------------|-------------|---------------|
| SimCLR | ResNet / ViT | `SimCLRProjectionHead` | - | - | - | `NTXentLoss` |
| MoCo | ResNet / ViT | `MoCoProjectionHead` | - | ✓ | ✓ (optional) | `NTXentLoss` |
| SimSiam | ResNet / ViT | `SimSiamProjectionHead` | `SimSiamPredictionHead` | - | - | `NegativeCosineSimilarity` |
| BYOL | ResNet / ViT | `BYOLProjectionHead` | `BYOLPredictionHead` | ✓ | - | `NegativeCosineSimilarity` |
| NNCLR | ResNet / ViT | `NNCLRProjectionHead` | `NNCLRPredictionHead` | - | `NNMemoryBankModule` | `NTXentLoss` |
| Barlow Twins | ResNet / ViT | `BarlowTwinsProjectionHead` | - | - | - | `BarlowTwinsLoss` |
| SwAV | ResNet / ViT | `SwaVProjectionHead` + `SwaVPrototypes` | - | - | - | `SwaVLoss` |
| DINO | ResNet / ViT | `DINOProjectionHead` | - | ✓ | - | `DINOLoss` |
| MAE | ViT | `MAEEncoder` + `MAEDecoder` | - | - | - | MSE Loss |
| MSN | ViT | `MSNProjectionHead` | - | ✓ | - | `MSNLoss` |

**Backbone Sources**: Lightly supports backbones from three sources:
- **torchvision**: Standard ResNet, VGG, EfficientNet, ViT (requires >=0.12)
- **timm**: Extensive model zoo including ViT variants, Swin, ConvNeXt (requires >=0.9.9)
- **Lightly**: CIFAR-optimized ResNet via `ResNetGenerator`

See **page 2.1** for detailed documentation on backbone architectures.

Sources:
- [lightly/models/modules/__init__.py:12-57]()
- [lightly/models/modules/heads.py:1-630]()
- [README.md:55-76]()
- [benchmarks/imagenet/resnet50/]()

## Model Components

Lightly provides reusable components that can be combined to implement SSL methods. The main component categories are:

### Projection and Prediction Heads

All projection heads inherit from `ProjectionHead` base class and transform backbone features into embeddings:

```mermaid
classDiagram
    class ProjectionHead {
        +layers: Sequential
        +forward(x: Tensor) Tensor
    }
    
    class SimCLRProjectionHead {
        +input_dim: int
        +hidden_dim: int
        +output_dim: int
    }
    
    class DINOProjectionHead {
        +input_dim: int
        +bottleneck_dim: int
        +output_dim: int
        +freeze_last_layer: int
    }
    
    class SimSiamPredictionHead {
        +input_dim: int
        +hidden_dim: int
        +output_dim: int
    }
    
    class SwaVPrototypes {
        +n_prototypes: int
        +normalize()
    }
    
    ProjectionHead <|-- SimCLRProjectionHead
    ProjectionHead <|-- DINOProjectionHead
    ProjectionHead <|-- SimSiamPredictionHead
```

Available heads include: `SimCLRProjectionHead`, `MoCoProjectionHead`, `BYOLProjectionHead`, `BYOLPredictionHead`, `SimSiamProjectionHead`, `SimSiamPredictionHead`, `NNCLRProjectionHead`, `NNCLRPredictionHead`, `BarlowTwinsProjectionHead`, `SwaVProjectionHead`, `DINOProjectionHead`, `DINOv2ProjectionHead`, `MSNProjectionHead`, and more.

See **page 2.2** for detailed documentation on all projection and prediction heads.

### Momentum Encoders and Memory Banks

Some SSL methods use additional components:

- **Momentum Encoders**: Slowly updated copies of the model used in MoCo, BYOL, DINO. Updated using `update_momentum()` utility function.
- **Memory Banks**: Store features from previous batches. `NNMemoryBankModule` is used by NNCLR. `NTXentLoss` has built-in memory bank support for MoCo.
- **Prototypes**: Learnable cluster centers used by SwAV (`SwaVPrototypes`) and SMoG (`SMoGPrototypes`).

See **page 2.2** for detailed documentation on these components and utility functions.

Sources:
- [lightly/models/modules/heads.py:15-630]()
- [lightly/models/modules/__init__.py:12-57]()
- [lightly/models/modules/nn_memory_bank.py]()
- [lightly/models/utils.py:262-292]()

## Example Model Implementations

Here are simplified examples showing how to compose SSL models from components:

### SimCLR Example

```python
# Contrastive learning with two augmented views
class SimCLRModel(nn.Module):
    def __init__(self):
        super().__init__()
        resnet = torchvision.models.resnet18()
        self.backbone = nn.Sequential(*list(resnet.children())[:-1])
        self.projection_head = heads.SimCLRProjectionHead(512, 512, 128)
        self.criterion = NTXentLoss()
    
    def forward(self, x):
        features = self.backbone(x).flatten(start_dim=1)
        z = self.projection_head(features)
        return z
```

### MoCo Example

```python
# Contrastive learning with momentum encoder and memory bank
class MoCoModel(nn.Module):
    def __init__(self):
        super().__init__()
        resnet = torchvision.models.resnet18()
        self.backbone = nn.Sequential(*list(resnet.children())[:-1])
        self.projection_head = heads.MoCoProjectionHead(512, 2048, 128)
        
        # Momentum encoder (no gradients)
        self.backbone_momentum = copy.deepcopy(self.backbone)
        self.projection_head_momentum = copy.deepcopy(self.projection_head)
        utils.deactivate_requires_grad(self.backbone_momentum)
        utils.deactivate_requires_grad(self.projection_head_momentum)
        
        # Loss with memory bank
        self.criterion = NTXentLoss(memory_bank_size=(4096, 128))
    
    def training_step(self, x0, x1):
        # Update momentum encoder (m=0.999)
        utils.update_momentum(self.backbone, self.backbone_momentum, 0.999)
        utils.update_momentum(self.projection_head, self.projection_head_momentum, 0.999)
        
        # Forward pass with batch shuffling
        x1_shuffled, shuffle = utils.batch_shuffle(x1)
        z0 = self.forward(x0)
        with torch.no_grad():
            z1 = self.forward_momentum(x1_shuffled)
            z1 = utils.batch_unshuffle(z1, shuffle)
        
        loss = self.criterion(z0, z1)
        return loss
```

### DINO Example

```python
# Self-distillation with momentum teacher
class DINOModel(nn.Module):
    def __init__(self):
        super().__init__()
        from timm.models.vision_transformer import vit_small_patch16_224
        
        self.student_backbone = MaskedVisionTransformerTIMM(
            vit=vit_small_patch16_224()
        )
        self.student_head = DINOProjectionHead(
            input_dim=384, hidden_dim=2048, 
            bottleneck_dim=256, output_dim=65536
        )
        
        # Teacher is EMA of student
        self.teacher_backbone = copy.deepcopy(self.student_backbone)
        self.teacher_head = copy.deepcopy(self.student_head)
        utils.deactivate_requires_grad(self.teacher_backbone)
        utils.deactivate_requires_grad(self.teacher_head)
        
        self.criterion = DINOLoss(output_dim=65536)
    
    def training_step(self, global_views, local_views):
        # Student: process all views
        student_out = [self.student_head(self.student_backbone(v)) 
                       for v in global_views + local_views]
        
        # Teacher: process only global views
        with torch.no_grad():
            teacher_out = [self.teacher_head(self.teacher_backbone(v)) 
                          for v in global_views]
            utils.update_momentum(self.student_backbone, self.teacher_backbone, 0.996)
            utils.update_momentum(self.student_head, self.teacher_head, 0.996)
        
        loss = self.criterion(teacher_out, student_out)
        return loss
```

See **page 2.2** for utility functions like `update_momentum()`, `batch_shuffle()`, and masking operations.

Sources:
- [docs/source/getting_started/benchmarks/cifar10_benchmark.py:323-456]()
- [benchmarks/imagenet/vitb16/dinov2.py:48-224]()
- [README.md:125-189]()
- [lightly/models/utils.py:262-292]()

## Training Workflow

Diagram: SSL Training Pipeline

```mermaid
flowchart TD
    subgraph "Data Loading"
        Dataset["LightlyDataset"] --> Transform["SSL Transform"]
        Transform --> Views["Multiple Views<br/>(x0, x1, ..., xN)"]
        Views --> DataLoader["DataLoader<br/>batch_size, shuffle=True"]
    end
    
    subgraph "Forward Pass"
        DataLoader --> Backbone["backbone(x)"]
        Backbone --> Features["features.flatten()"]
        Features --> ProjectionHead["projection_head(features)"]
        ProjectionHead --> Embeddings["z (embeddings)"]
        
        Embeddings --> ModelType{"Model Type"}
        
        ModelType -->|"SimCLR, MoCo"| Contrastive["Contrastive<br/>z0, z1"]
        ModelType -->|"SimSiam, BYOL"| Asymmetric["prediction_head(z)<br/>p (predictions)"]
        ModelType -->|"DINO, DINOv2"| Distill["Teacher network<br/>momentum update"]
        ModelType -->|"MAE, SimMIM"| Masked["Masked patches<br/>reconstruction"]
    end
    
    subgraph "Loss Computation"
        Contrastive --> NTXentLoss["NTXentLoss"]
        Asymmetric --> NegCosineLoss["NegativeCosineSimilarity"]
        Distill --> DINOLossFunc["DINOLoss"]
        Masked --> MSELoss["MSE / L1 Loss"]
        
        NTXentLoss --> Loss["Total Loss"]
        NegCosineLoss --> Loss
        DINOLossFunc --> Loss
        MSELoss --> Loss
    end
    
    subgraph "Optimization"
        Loss --> Backward["loss.backward()"]
        Backward --> OptimizerStep["optimizer.step()"]
        OptimizerStep --> ZeroGrad["optimizer.zero_grad()"]
        ZeroGrad --> MomentumUpdate{"Momentum Model?"}
        MomentumUpdate -->|"Yes"| UpdateMom["update_momentum()"]
        MomentumUpdate -->|"No"| NextBatch["Next Batch"]
        UpdateMom --> NextBatch
    end
```

**Typical Training Loop**:

```python
# Setup (from benchmarks)
model = BenchmarkModule(dataloader_kNN, num_classes)
optimizer = torch.optim.SGD(model.parameters(), lr=0.06)
trainer = pl.Trainer(max_epochs=200, devices=1)

# Training step implementation
def training_step(self, batch, batch_idx):
    (x0, x1), targets, filenames = batch
    
    # Forward pass
    z0 = self.backbone(x0).flatten(start_dim=1)
    z0 = self.projection_head(z0)
    z1 = self.backbone(x1).flatten(start_dim=1)
    z1 = self.projection_head(z1)
    
    # Compute loss
    loss = self.criterion(z0, z1)
    
    # Momentum update (if applicable)
    if hasattr(self, 'backbone_momentum'):
        utils.update_momentum(self.backbone, self.backbone_momentum, m=0.99)
    
    return loss
```

Sources:
- [docs/source/getting_started/benchmarks/cifar10_benchmark.py:390-731]()
- [docs/source/getting_started/benchmarks/imagenette_benchmark.py:257-817]()
- [lightly/utils/benchmarking/benchmark_module.py]()
- [README.md:125-274]()

## Using Pretrained SSL Models

After training, the backbone network can be used for various downstream tasks:

1. **Feature Extraction**: Using the backbone to extract features for visualization or clustering
   ```python
   model.eval()
   embeddings = []
   with torch.no_grad():
       for img, _, _ in dataloader:
           emb = model.backbone(img).flatten(start_dim=1)
           embeddings.append(emb)
   ```

2. **Transfer Learning**: Fine-tuning the pretrained backbone for a specific task
   ```python
   # Use the pretrained backbone
   pretrained_backbone = model.backbone
   
   # Create a new classifier with the pretrained backbone
   classifier = nn.Sequential(
       pretrained_backbone,
       nn.Linear(backbone_output_dim, num_classes)
   )
   ```

Sources:
- [docs/source/tutorials_source/package/tutorial_simclr_clothing.py:187-204]()
- [docs/source/tutorials_source/package/tutorial_moco_memory_bank.py:292-317]()
- [docs/source/tutorials_source/package/tutorial_simsiam_esa.py:264-281]()
- [docs/source/tutorials_source/package/tutorial_pretrain_detectron2.py:169-180]()

## Examples and Tutorials

Lightly provides several tutorials for training and using SSL models:

1. **SimCLR on Clothing Dataset** - Training a SimCLR model and exploring nearest neighbors in embedding space
2. **MoCo with Memory Bank** - Training a MoCo model with a memory bank on CIFAR-10
3. **SimSiam on Satellite Images** - Training a SimSiam model on a dataset of satellite images
4. **Custom Augmentations** - Training an SSL model with custom augmentations for X-ray images
5. **Pre-train Detectron2 Backbone** - Using Lightly to pre-train a Detectron2 backbone for object detection

Sources:
- [docs/source/tutorials_source/package/tutorial_simclr_clothing.py]()
- [docs/source/tutorials_source/package/tutorial_moco_memory_bank.py]()
- [docs/source/tutorials_source/package/tutorial_simsiam_esa.py]()
- [docs/source/tutorials_source/package/tutorial_custom_augmentations.py]()
- [docs/source/tutorials_source/package/tutorial_pretrain_detectron2.py]()
- [docs/source/examples/models.rst]()

---

# Page: Model Architectures

# Model Architectures

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/check_example_nbs.yml](.github/workflows/check_example_nbs.yml)
- [.github/workflows/discord_release_notification.yml](.github/workflows/discord_release_notification.yml)
- [Makefile](Makefile)
- [README.md](README.md)
- [docs/source/getting_started/benchmarks.rst](docs/source/getting_started/benchmarks.rst)
- [docs/source/getting_started/benchmarks/cifar10_benchmark.py](docs/source/getting_started/benchmarks/cifar10_benchmark.py)
- [docs/source/getting_started/benchmarks/imagenet100_benchmark.py](docs/source/getting_started/benchmarks/imagenet100_benchmark.py)
- [docs/source/getting_started/benchmarks/imagenette_benchmark.py](docs/source/getting_started/benchmarks/imagenette_benchmark.py)
- [docs/source/tutorials/structure_your_input.rst](docs/source/tutorials/structure_your_input.rst)
- [docs/source/tutorials_source/package/Base-RCNN-FPN.yaml](docs/source/tutorials_source/package/Base-RCNN-FPN.yaml)
- [docs/source/tutorials_source/package/tutorial_custom_augmentations.py](docs/source/tutorials_source/package/tutorial_custom_augmentations.py)
- [docs/source/tutorials_source/package/tutorial_moco_memory_bank.py](docs/source/tutorials_source/package/tutorial_moco_memory_bank.py)
- [docs/source/tutorials_source/package/tutorial_pretrain_detectron2.py](docs/source/tutorials_source/package/tutorial_pretrain_detectron2.py)
- [docs/source/tutorials_source/package/tutorial_simclr_clothing.py](docs/source/tutorials_source/package/tutorial_simclr_clothing.py)
- [docs/source/tutorials_source/package/tutorial_simsiam_esa.py](docs/source/tutorials_source/package/tutorial_simsiam_esa.py)
- [lightly/loss/pmsn_loss.py](lightly/loss/pmsn_loss.py)
- [lightly/models/modules/ijepa_timm.py](lightly/models/modules/ijepa_timm.py)
- [lightly/models/modules/masked_autoencoder_timm.py](lightly/models/modules/masked_autoencoder_timm.py)
- [lightly/models/modules/masked_vision_transformer_timm.py](lightly/models/modules/masked_vision_transformer_timm.py)
- [pyproject.toml](pyproject.toml)
- [tests/loss/test_msn_loss.py](tests/loss/test_msn_loss.py)
- [tests/loss/test_pmsn_loss.py](tests/loss/test_pmsn_loss.py)

</details>



This page documents the backbone architectures available in Lightly for self-supervised learning. Backbones are the feature extraction networks that process input images into learned representations. The framework supports standard ResNet and Vision Transformer (ViT) architectures, as well as specialized variants for masked image modeling methods like MAE and I-JEPA.

For information about projection heads, prediction heads, and other model components that build on top of backbones, see [Model Components and Utilities](#2.2). For loss functions used to train these architectures, see [Loss Functions](#2.3).

## Overview of Available Backbones

The Lightly framework provides three main categories of backbone architectures:

| Architecture Family | Variants | Primary Use Cases | Integration Source |
|-------------------|----------|------------------|-------------------|
| **ResNet** | ResNet-18, ResNet-50, ResNet-101 | General-purpose SSL, benchmarking | torchvision |
| **Vision Transformer** | ViT-S/16, ViT-B/16, ViT-B/32 | Attention-based SSL methods (DINO, MAE) | torchvision, TIMM |
| **Masked Vision Transformer** | Masked ViT variants | Masked image modeling (MAE, I-JEPA, iBOT) | Custom + TIMM |

All backbone architectures can be combined with method-specific projection heads to create complete SSL models.

**Sources:** [README.md:50-76](), [docs/source/getting_started/benchmarks.rst:30-46]()

## ResNet Backbones

### Standard ResNet Architecture

ResNet backbones from torchvision are the most commonly used architectures in the framework. When creating a ResNet backbone for SSL, the classification head is typically removed to extract features:

```python
import torchvision
import torch.nn as nn

# Create ResNet-18 backbone
resnet = torchvision.models.resnet18()
backbone = nn.Sequential(*list(resnet.children())[:-1])
# Output shape: (batch_size, 512, 1, 1) for ResNet-18
```

The feature dimensions for standard ResNet variants are:
- ResNet-18: 512 dimensions
- ResNet-50: 2048 dimensions  
- ResNet-101: 2048 dimensions

**Sources:** [docs/source/tutorials_source/package/tutorial_simclr_clothing.py:143-145](), [docs/source/tutorials_source/package/tutorial_moco_memory_bank.py:226-229]()

### ResNet for Small Images (CIFAR-10)

For small input images like CIFAR-10 (32x32 pixels), the framework provides a specialized ResNet variant that uses a 3x3 convolution instead of the standard 7x7 convolution, with no stride and no MaxPool2d in the first layer. This prevents excessive downsampling of already small images.

```mermaid
graph LR
    Input["Input Image<br/>(32x32)"] --> Conv3x3["3x3 Conv<br/>stride=1<br/>no MaxPool"]
    Conv3x3 --> ResBlocks["ResNet Blocks<br/>(res2, res3, res4, res5)"]
    ResBlocks --> GAP["Global Average Pool"]
    GAP --> Features["Feature Vector<br/>(512-dim for ResNet-18)"]
    
    Input2["Input Image<br/>(224x224)"] --> Conv7x7["7x7 Conv<br/>stride=2<br/>+ MaxPool"]
    Conv7x7 --> ResBlocks2["ResNet Blocks"]
    ResBlocks2 --> GAP2["Global Average Pool"]
    GAP2 --> Features2["Feature Vector"]
    
    style Input fill:#f9f9f9
    style Input2 fill:#f9f9f9
```
**Diagram: ResNet Architecture Variants for Different Input Sizes**

This specialized variant is created using `ResNetGenerator` from `lightly.models`:

```python
from lightly.models import ResNetGenerator
import torch.nn as nn

# ResNet for small images (CIFAR-10)
resnet = ResNetGenerator("resnet-18")
backbone = nn.Sequential(
    *list(resnet.children())[:-1], 
    nn.AdaptiveAvgPool2d(1)
)
```

**Sources:** [docs/source/getting_started/benchmarks.rst:144-147](), [docs/source/getting_started/benchmarks/cifar10_benchmark.py:296-299](), [docs/source/getting_started/benchmarks/cifar10_benchmark.py:362-365]()

### Split Batch Normalization

For methods like MoCo that use momentum encoders, the framework supports split batch normalization to simulate multi-GPU behavior. This prevents information leakage through batch statistics:

```python
from lightly.models import ResNetGenerator

# Create ResNet with 8 batch norm splits
num_splits = 8
resnet = ResNetGenerator("resnet-18", num_splits=num_splits)
```

The `num_splits` parameter controls how the batch is divided for independent batch norm calculation.

**Sources:** [docs/source/tutorials_source/package/tutorial_moco_memory_bank.py:218-221](), [docs/source/getting_started/benchmarks/cifar10_benchmark.py:295-296]()

## Vision Transformer (ViT) Backbones

### Standard ViT Architecture

Vision Transformers process images as sequences of patches. The framework supports ViT architectures from both torchvision and TIMM libraries:

```mermaid
graph TB
    Image["Input Image<br/>(224x224x3)"] --> PatchEmbed["Patch Embedding<br/>16x16 patches<br/>→ 196 tokens"]
    PatchEmbed --> AddCLS["Prepend CLS Token<br/>→ 197 tokens"]
    AddCLS --> AddPosEmbed["Add Positional<br/>Embeddings"]
    AddPosEmbed --> TransformerBlocks["Transformer Blocks<br/>(12 for ViT-B)"]
    TransformerBlocks --> Norm["Layer Normalization"]
    Norm --> Output["Output Options"]
    
    Output --> CLSToken["CLS Token<br/>(768-dim for ViT-B)"]
    Output --> AvgPool["Average Pool<br/>all tokens"]
    Output --> AttnPool["Attention Pool"]
```
**Diagram: Vision Transformer Architecture Flow**

ViT variants differ primarily in:
- **Patch size**: 16x16 (ViT-*/16) or 32x32 (ViT-*/32)
- **Model size**: Small (ViT-S), Base (ViT-B), Large (ViT-L)
- **Embedding dimension**: 384 (ViT-S), 768 (ViT-B), 1024 (ViT-L)

**Sources:** [lightly/models/modules/masked_vision_transformer_timm.py:68-90]()

### TIMM Integration

The framework integrates with the TIMM library to support a wider range of ViT architectures and features. TIMM models provide additional functionality like dynamic image sizes and flexible pooling strategies:

```python
from timm.models.vision_transformer import vit_base_patch32_224
import torch.nn as nn

# Create ViT-B/32 from TIMM
vit = vit_base_patch32_224(pretrained=False)
# Use as backbone (remove head if present)
```

Key TIMM features used in Lightly:
- **Dynamic image size**: Resample positional embeddings for different input sizes
- **Flexible prefix tokens**: Support for both class tokens and register tokens
- **Multiple pooling strategies**: Class token, average pooling, or attention pooling

**Sources:** [lightly/models/modules/masked_vision_transformer_timm.py:1-218](), [docs/source/getting_started/benchmarks/imagenette_benchmark.py:73-74]()

## Masked Vision Transformers

### MaskedVisionTransformerTIMM

For masked image modeling methods (MAE, SimMIM, iBOT), the framework provides `MaskedVisionTransformerTIMM`, which extends standard ViT to support masking patches during training:

```mermaid
graph TB
    Images["Input Images"] --> PatchEmbed["images_to_tokens()"]
    PatchEmbed --> Tokens["Patch Tokens"]
    
    Tokens --> Masking{Masking Strategy}
    Masking -->|idx_keep| Keep["Keep Visible Tokens"]
    Masking -->|idx_mask| Replace["Replace with<br/>Mask Tokens"]
    Masking -->|mask| Boolean["Boolean Mask"]
    
    Keep --> PrependPrefix["prepend_prefix_tokens()<br/>(CLS, register tokens)"]
    Replace --> PrependPrefix
    Boolean --> PrependPrefix
    
    PrependPrefix --> AddPos["add_pos_embed()"]
    AddPos --> Encode["encode()<br/>(transformer blocks)"]
    Encode --> Output["Encoded Features"]
```
**Diagram: MaskedVisionTransformerTIMM Processing Pipeline**

The class provides three methods for token preprocessing:

| Method | Parameters | Purpose |
|--------|-----------|---------|
| `images_to_tokens()` | `images` | Convert images to patch tokens |
| `prepend_prefix_tokens()` | `x` | Add CLS and register tokens |
| `add_pos_embed()` | `x` | Add positional embeddings (with resampling) |
| `encode()` | `images, idx_mask, idx_keep, mask` | Full encoding with optional masking |

**Key features:**
- **Flexible masking**: Supports token indices (`idx_keep`, `idx_mask`) or boolean masks
- **Positional embedding resampling**: Handles dynamic image sizes via `resample_abs_pos_embed`
- **Weight initialization**: Configurable initialization strategies ('', 'skip')
- **Positional embedding initialization**: Supports 'learn', 'sincos', 'skip' strategies

**Sources:** [lightly/models/modules/masked_vision_transformer_timm.py:15-218]()

### MAEDecoderTIMM

The MAE decoder reconstructs masked patches from encoded representations:

```mermaid
graph TB
    Encoder["Encoder Output<br/>(visible tokens)"] --> Embed["decoder_embed<br/>Linear projection"]
    Embed --> InsertMask["Insert Mask Tokens<br/>at masked positions"]
    InsertMask --> AddPosEmbed["Add Positional<br/>Embeddings"]
    AddPosEmbed --> DecoderBlocks["Decoder Transformer<br/>Blocks"]
    DecoderBlocks --> Norm["decoder_norm"]
    Norm --> Pred["decoder_pred<br/>Linear to pixels"]
    Pred --> Reconstruction["Reconstructed Patches<br/>(patch_size² × 3)"]
```
**Diagram: MAE Decoder Architecture**

The decoder is typically much smaller than the encoder:
- **Encoder**: 1024-dim embeddings, 24 blocks (ViT-B)
- **Decoder**: 512-dim embeddings, 8 blocks

Configuration parameters:
```python
MAEDecoderTIMM(
    num_patches=196,           # Number of patches (14×14 for 224×224 image)
    patch_size=16,             # Size of each patch
    embed_dim=1024,            # Encoder embedding dimension
    decoder_embed_dim=512,     # Decoder embedding dimension
    decoder_depth=8,           # Number of decoder blocks
    decoder_num_heads=16,      # Attention heads in decoder
    mlp_ratio=4.0,            # MLP hidden dim ratio
)
```

**Sources:** [lightly/models/modules/masked_autoencoder_timm.py:14-218]()

### IJEPAPredictorTIMM

For I-JEPA (Joint-Embedding Predictive Architecture), the predictor network predicts target patch embeddings from context embeddings:

```mermaid
graph TB
    Context["Context Tokens<br/>(from encoder)"] --> PredEmbed["predictor_embed<br/>Project to predictor dim"]
    PredEmbed --> AddCtxPos["Add Context<br/>Positional Embeddings"]
    
    MaskTokens["Mask Tokens"] --> AddTargetPos["Add Target<br/>Positional Embeddings"]
    
    AddCtxPos --> Concat["Concatenate<br/>Context + Mask Tokens"]
    AddTargetPos --> Concat
    
    Concat --> PredBlocks["Predictor Transformer<br/>Blocks"]
    PredBlocks --> PredNorm["predictor_norm"]
    PredNorm --> ExtractTarget["Extract Target Tokens<br/>(remove context)"]
    ExtractTarget --> PredProj["predictor_proj<br/>Project back to<br/>encoder dim"]
    PredProj --> PredFeatures["Predicted Target<br/>Features"]
```
**Diagram: I-JEPA Predictor Architecture**

The predictor uses a bottleneck architecture:
- **Input**: Encoder dimension (e.g., 768 for ViT-B)
- **Predictor**: Smaller dimension (e.g., 384)
- **Output**: Back to encoder dimension

Configuration example:
```python
IJEPAPredictorTIMM(
    num_patches=196,
    depth=6,                    # Predictor depth
    mlp_dim=768,               # Encoder dimension
    predictor_embed_dim=384,   # Bottleneck dimension
    num_heads=12,
    qkv_bias=True,
    mlp_ratio=4.0,
)
```

**Sources:** [lightly/models/modules/ijepa_timm.py:15-152]()

## Backbone Selection by SSL Method

Different SSL methods have different architectural requirements and perform best with specific backbones:

| SSL Method | Recommended Backbone | Feature Dimension | Notes |
|------------|---------------------|------------------|-------|
| SimCLR, MoCo | ResNet-18/50 | 512/2048 | Standard choice for contrastive learning |
| BYOL, SimSiam | ResNet-18/50 | 512/2048 | Momentum encoder variants |
| DINO, DINOv2 | ViT-S/16, ResNet-50 | 384/512 | Works with both CNN and ViT |
| MAE | ViT-B/16 | 768 | Requires masked ViT |
| iBOT | ViT-S/16 | 384 | Combines DINO with masked modeling |
| MSN, PMSN | ViT-S | 384 | Prototype-based with ViT |
| SimMIM | ViT-B/32 | 768 | Masked modeling |
| I-JEPA | ViT-B/16 | 768 | Requires predictor network |

**Sources:** [README.md:57-76](), [docs/source/getting_started/benchmarks.rst:30-46]()

## Common Usage Patterns

### Pattern 1: ResNet Backbone for Contrastive Learning

```python
import torchvision
import torch.nn as nn
from lightly.models.modules.heads import SimCLRProjectionHead

# Create ResNet-18 backbone
resnet = torchvision.models.resnet18()
backbone = nn.Sequential(*list(resnet.children())[:-1])

# Add projection head
projection_head = SimCLRProjectionHead(
    input_dim=512,
    hidden_dim=512,
    output_dim=128,
)

# Forward pass
features = backbone(images).flatten(start_dim=1)  # (batch, 512)
projections = projection_head(features)            # (batch, 128)
```

**Sources:** [docs/source/tutorials_source/package/tutorial_simclr_clothing.py:139-155]()

### Pattern 2: ViT Backbone for DINO

```python
from timm.models.vision_transformer import VisionTransformer
from lightly.models.modules import DINOProjectionHead

# Create ViT backbone (simplified)
vit = VisionTransformer(
    patch_size=16,
    embed_dim=384,
    depth=12,
    num_heads=6,
)

# DINO uses both student and teacher networks
# Teacher is a momentum-updated copy of student
teacher = copy.deepcopy(vit)
```

**Sources:** [docs/source/getting_started/benchmarks/imagenette_benchmark.py:661-668]()

### Pattern 3: Masked ViT for MAE

```python
from timm.models.vision_transformer import VisionTransformer
from lightly.models.modules import MaskedVisionTransformerTIMM, MAEDecoderTIMM

# Create encoder
vit = VisionTransformer(...)
encoder = MaskedVisionTransformerTIMM(vit=vit)

# Create decoder
decoder = MAEDecoderTIMM(
    num_patches=196,
    patch_size=16,
    embed_dim=768,
    decoder_embed_dim=512,
    decoder_depth=8,
)

# Forward with masking
encoded = encoder.encode(images, idx_keep=idx_keep)
reconstructed = decoder(encoded)
```

**Sources:** [lightly/models/modules/masked_autoencoder_timm.py:109-122]()

## Architecture Considerations

### Input Size Adaptation

When using different input sizes than the standard 224×224, consider:

1. **ResNet**: Works with any input size ≥32×32. For small images (32×32), use `ResNetGenerator` to avoid excessive downsampling.

2. **ViT**: Positional embeddings are designed for specific grid sizes. Use TIMM's `resample_abs_pos_embed()` for dynamic sizes:

```python
# Handled automatically in MaskedVisionTransformerTIMM
pos_embed = resample_abs_pos_embed(
    self.vit.pos_embed,
    (H, W),  # New grid size
    num_prefix_tokens=1,
    antialias=True,
)
```

**Sources:** [lightly/models/modules/masked_vision_transformer_timm.py:156-179]()

### Memory Requirements

Approximate GPU memory requirements for common configurations (batch size 256):

| Architecture | Input Size | Memory | Typical Use |
|-------------|-----------|--------|------------|
| ResNet-18 | 32×32 | 1.5 GB | CIFAR-10 benchmarks |
| ResNet-18 | 128×128 | 4.0 GB | ImageNette |
| ResNet-50 | 224×224 | 11.3 GB | ImageNet |
| ViT-S/16 | 224×224 | 14.7 GB | ImageNet SSL |
| ViT-B/16 | 224×224 | ~20 GB | MAE pretraining |

**Sources:** [docs/source/getting_started/benchmarks.rst:69-81](), [docs/source/getting_started/benchmarks/imagenette_benchmark.py:103-127]()

### Checkpoint Compatibility

Backbones trained with Lightly can be used with other frameworks:

```python
# Save backbone
state_dict = {"resnet18_parameters": backbone.state_dict()}
torch.save(state_dict, "backbone.pth")

# Load in another framework
resnet18 = torchvision.models.resnet18()
backbone = nn.Sequential(*list(resnet18.children())[:-1])
backbone.load_state_dict(torch.load("backbone.pth")["resnet18_parameters"])
```

For Detectron2 integration, see the specialized tutorial at [docs/source/tutorials_source/package/tutorial_pretrain_detectron2.py:1-334]().

**Sources:** [docs/source/tutorials_source/package/tutorial_simclr_clothing.py:289-307](), [docs/source/tutorials_source/package/tutorial_pretrain_detectron2.py:1-334]()

---

# Page: Model Components and Utilities

# Model Components and Utilities

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [benchmarks/imagenet/vitb16/dinov2.py](benchmarks/imagenet/vitb16/dinov2.py)
- [benchmarks/imagenet/vitb16/ibot.py](benchmarks/imagenet/vitb16/ibot.py)
- [docs/source/getting_started/benchmarks.rst](docs/source/getting_started/benchmarks.rst)
- [docs/source/getting_started/benchmarks/cifar10_benchmark.py](docs/source/getting_started/benchmarks/cifar10_benchmark.py)
- [docs/source/getting_started/benchmarks/imagenet100_benchmark.py](docs/source/getting_started/benchmarks/imagenet100_benchmark.py)
- [docs/source/getting_started/benchmarks/imagenette_benchmark.py](docs/source/getting_started/benchmarks/imagenette_benchmark.py)
- [lightly/models/modules/__init__.py](lightly/models/modules/__init__.py)
- [lightly/models/modules/heads.py](lightly/models/modules/heads.py)
- [lightly/models/utils.py](lightly/models/utils.py)
- [tests/models/modules/test_masked_autoencoder.py](tests/models/modules/test_masked_autoencoder.py)
- [tests/models/test_ModelUtils.py](tests/models/test_ModelUtils.py)
- [tests/models/test_ProjectionHeads.py](tests/models/test_ProjectionHeads.py)

</details>



This page documents the modular components and utility functions used to construct self-supervised learning (SSL) models in Lightly. These components include projection heads, prediction heads, prototypes, and various utility functions for momentum updates, batch operations, token manipulation, and masking strategies.

For information about complete SSL model implementations and loss functions, see [Loss Functions](#2.2). For data augmentation pipelines, see [Transforms](#2.3).

## Overview

SSL models in Lightly follow a composable architecture where different components can be mixed and matched to implement various algorithms. The main building blocks are:

- **Projection Heads**: MLPs that map backbone features to embedding space
- **Prediction Heads**: MLPs used in asymmetric architectures (SimSiam, BYOL)
- **Prototypes**: Learnable prototype vectors for clustering-based methods (SwaV, SMoG)
- **Utility Functions**: Shared functionality for momentum updates, masking, and token operations

```mermaid
graph TB
    subgraph "Base Components"
        ProjectionHead["ProjectionHead<br/>(Base Class)"]
        Utils["lightly.models.utils"]
    end
    
    subgraph "Projection Heads"
        SimCLR["SimCLRProjectionHead"]
        MoCo["MoCoProjectionHead"]
        BYOL["BYOLProjectionHead"]
        DINO["DINOProjectionHead"]
        DINOv2["DINOv2ProjectionHead"]
        SwaV["SwaVProjectionHead"]
        BarlowTwins["BarlowTwinsProjectionHead"]
        VICReg["VICRegProjectionHead"]
    end
    
    subgraph "Prediction Heads"
        SimSiamPred["SimSiamPredictionHead"]
        BYOLPred["BYOLPredictionHead"]
        NNCLRPred["NNCLRPredictionHead"]
        SMoGPred["SMoGPredictionHead"]
    end
    
    subgraph "Prototypes"
        SwaVProto["SwaVPrototypes"]
        SMoGProto["SMoGPrototypes"]
    end
    
    subgraph "Utilities"
        UpdateMomentum["update_momentum"]
        BatchShuffle["batch_shuffle<br/>batch_unshuffle"]
        TokenOps["random_token_mask<br/>patchify<br/>unpatchify"]
        Masking["random_block_mask<br/>mask_at_index"]
    end
    
    ProjectionHead --> SimCLR
    ProjectionHead --> MoCo
    ProjectionHead --> BYOL
    ProjectionHead --> DINO
    ProjectionHead --> DINOv2
    ProjectionHead --> SwaV
    ProjectionHead --> BarlowTwins
    ProjectionHead --> VICReg
    
    ProjectionHead --> SimSiamPred
    ProjectionHead --> BYOLPred
    ProjectionHead --> NNCLRPred
    ProjectionHead --> SMoGPred
    
    Utils --> UpdateMomentum
    Utils --> BatchShuffle
    Utils --> TokenOps
    Utils --> Masking
```

**Diagram: Component Architecture Overview**

Sources: [lightly/models/modules/heads.py:1-987](), [lightly/models/utils.py:1-100]()

## Projection Heads

### Base Class: ProjectionHead

The `ProjectionHead` base class provides a flexible architecture for building MLPs with configurable blocks. Each block consists of a linear layer, optional batch normalization, and optional non-linearity.

```mermaid
graph LR
    Input["Input Features<br/>(B, input_dim)"]
    
    subgraph Block1["Block 1"]
        Linear1["nn.Linear"]
        BN1["nn.BatchNorm1d<br/>(optional)"]
        ReLU1["nn.ReLU<br/>(optional)"]
        Linear1 --> BN1
        BN1 --> ReLU1
    end
    
    subgraph Block2["Block 2"]
        Linear2["nn.Linear"]
        BN2["nn.BatchNorm1d<br/>(optional)"]
        ReLU2["nn.ReLU<br/>(optional)"]
        Linear2 --> BN2
        BN2 --> ReLU2
    end
    
    subgraph BlockN["Block N"]
        LinearN["nn.Linear"]
        BNN["nn.BatchNorm1d<br/>(optional)"]
        ReLUN["Non-linearity<br/>(optional)"]
        LinearN --> BNN
        BNN --> ReLUN
    end
    
    Output["Output Embeddings<br/>(B, output_dim)"]
    
    Input --> Block1
    Block1 --> Block2
    Block2 --> BlockN
    BlockN --> Output
```

**Diagram: ProjectionHead Block Architecture**

The constructor accepts a sequence of block tuples with the format:
```
(input_dim, output_dim, batch_norm_layer, non_linearity_layer, use_bias (optional))
```

If `use_bias` is not specified, bias is automatically disabled when batch normalization is used (following common practice).

Sources: [lightly/models/modules/heads.py:15-66]()

### Algorithm-Specific Projection Heads

Each SSL algorithm has a projection head with architecture parameters from the original paper:

| Head | Layers | Hidden Dim | Output Dim | Batch Norm | Non-linearity | Reference |
|------|--------|------------|------------|------------|---------------|-----------|
| `SimCLRProjectionHead` | 2-3 | 2048 | 128 | Yes | ReLU | [lightly/models/modules/heads.py:264-324]() |
| `MoCoProjectionHead` | 2-3 | 2048-4096 | 128-256 | Optional | ReLU | [lightly/models/modules/heads.py:143-206]() |
| `BYOLProjectionHead` | 2 | 4096 | 256 | Yes | ReLU | [lightly/models/modules/heads.py:100-119]() |
| `SimSiamProjectionHead` | 3 | 2048 | 2048 | Yes (no affine on last) | ReLU | [lightly/models/modules/heads.py:327-351]() |
| `DINOProjectionHead` | 3 + last | 2048 | 65536 | Optional | GELU | [lightly/models/modules/heads.py:632-731]() |
| `DINOv2ProjectionHead` | 3 + last | 2048 | 65536 | Optional | GELU | [lightly/models/modules/heads.py:733-776]() |
| `SwaVProjectionHead` | 2 | 2048 | 128 | Yes | ReLU | [lightly/models/modules/heads.py:531-546]() |
| `BarlowTwinsProjectionHead` | 3 | 8192 | 8192 | Yes | ReLU | [lightly/models/modules/heads.py:68-97]() |
| `VICRegProjectionHead` | 3 | 8192 | 8192 | Yes | ReLU | [lightly/models/modules/heads.py:904-943]() |

**Table: Projection Head Architectures by Algorithm**

#### Special Cases: DINO Heads

The DINO projection heads have unique characteristics:

```mermaid
graph TB
    Input["Input Features"]
    
    subgraph "3-Layer MLP"
        Layer1["Linear + BN/None + GELU"]
        Layer2["Linear + BN/None + GELU"]
        Layer3["Linear (bottleneck_dim)"]
    end
    
    L2Norm["L2 Normalization"]
    LastLayer["Weight-Normalized Linear<br/>(output_dim)<br/>weight_g = 1"]
    
    Output["Output Embeddings"]
    
    Input --> Layer1
    Layer1 --> Layer2
    Layer2 --> Layer3
    Layer3 --> L2Norm
    L2Norm --> LastLayer
    LastLayer --> Output
    
    Freezing["Gradient Freezing<br/>(freeze_last_layer epochs)"]
    Freezing -.-> LastLayer
```

**Diagram: DINO Projection Head Architecture**

Key features:
- L2 normalization before the last layer [lightly/models/modules/heads.py:714-716]()
- Weight-normalized last layer with `weight_g.data.fill_(1)` [lightly/models/modules/heads.py:696-698]()
- Optional gradient freezing via `cancel_last_layer_gradients()` [lightly/models/modules/heads.py:704-709]()
- Truncated normal initialization for stability [lightly/models/modules/heads.py:719-730]()

Sources: [lightly/models/modules/heads.py:632-776](), [benchmarks/imagenet/vitb16/dinov2.py:81-99]()

## Prediction Heads

Prediction heads are used in asymmetric SSL architectures where one branch predicts the representations of another branch. Unlike projection heads, prediction heads typically have no batch normalization on the output layer and use only ReLU activations.

```mermaid
graph LR
    subgraph "Asymmetric Architecture"
        View1["View 1"]
        View2["View 2"]
        
        Backbone1["Backbone"]
        Backbone2["Backbone<br/>(shared)"]
        
        ProjHead1["Projection Head"]
        ProjHead2["Projection Head<br/>(shared)"]
        
        PredHead["Prediction Head<br/>(only on one branch)"]
        
        Loss["Similarity Loss"]
        
        View1 --> Backbone1
        View2 --> Backbone2
        Backbone1 --> ProjHead1
        Backbone2 --> ProjHead2
        ProjHead1 --> PredHead
        PredHead --> Loss
        ProjHead2 --> Loss
    end
```

**Diagram: Asymmetric Architecture with Prediction Head**

| Head | Layers | Hidden Dim | Output Dim | Reference |
|------|--------|------------|------------|-----------|
| `SimSiamPredictionHead` | 2 | 512 | 2048 | [lightly/models/modules/heads.py:501-528]() |
| `BYOLPredictionHead` | 2 | 4096 | 256 | [lightly/models/modules/heads.py:122-140]() |
| `NNCLRPredictionHead` | 2 | 4096 | 256 | [lightly/models/modules/heads.py:243-261]() |
| `SMoGPredictionHead` | 2 | 2048 | 128 | [lightly/models/modules/heads.py:469-498]() |

**Table: Prediction Head Architectures**

All prediction heads follow the pattern:
1. First layer: Linear → BatchNorm → ReLU
2. Last layer: Linear (no BatchNorm, no activation)

Sources: [lightly/models/modules/heads.py:122-528](), [tests/models/test_ProjectionHeads.py:1-320]()

## Prototypes

Prototypes are learnable vectors used in clustering-based SSL methods. They act as cluster centers in the embedding space.

### SwaVPrototypes

The `SwaVPrototypes` module implements learnable prototypes for SwAV with support for multi-head prototypes and prototype freezing.

```mermaid
graph TB
    Features["Normalized Features<br/>(B, input_dim)"]
    
    subgraph "Multi-Head Prototypes"
        Head1["Linear Layer 1<br/>(input_dim → n_prototypes[0])"]
        Head2["Linear Layer 2<br/>(input_dim → n_prototypes[1])"]
        HeadN["Linear Layer N<br/>(input_dim → n_prototypes[N-1])"]
    end
    
    Normalize["Weight Normalization<br/>normalize()"]
    
    Logits1["Logits 1<br/>(B, n_prototypes[0])"]
    Logits2["Logits 2<br/>(B, n_prototypes[1])"]
    LogitsN["Logits N<br/>(B, n_prototypes[N-1])"]
    
    Features --> Head1
    Features --> Head2
    Features --> HeadN
    
    Normalize -.->|"Unit sphere<br/>constraint"| Head1
    Normalize -.-> Head2
    Normalize -.-> HeadN
    
    Head1 --> Logits1
    Head2 --> Logits2
    HeadN --> LogitsN
```

**Diagram: SwaVPrototypes Multi-Head Architecture**

Key features:
- Supports single or multiple prototype heads via `n_prototypes` parameter [lightly/models/modules/heads.py:576-592]()
- Prototype weights normalized to unit sphere via `normalize()` [lightly/models/modules/heads.py:616-619]()
- Optional prototype freezing for initial epochs via `n_steps_frozen_prototypes` [lightly/models/modules/heads.py:621-629]()

Sources: [lightly/models/modules/heads.py:549-630](), [tests/models/test_ProjectionHeads.py:92-155]()

### SMoGPrototypes

The `SMoGPrototypes` module implements Synchronous Momentum Grouping with momentum-updated group features.

Key operations:
- **Forward pass**: Computes logits via cosine similarity with temperature scaling [lightly/models/modules/heads.py:374-393]()
- **Group assignment**: Assigns samples to nearest group via `assign_groups()` [lightly/models/modules/heads.py:419-430]()
- **Momentum update**: Updates group features via exponential moving average [lightly/models/modules/heads.py:395-413]()

```python
# Momentum update formula
group_features[c] = beta * group_features[c] + (1 - beta) * x[mask].mean(dim=0)
```

Sources: [lightly/models/modules/heads.py:354-431]()

## Utility Functions

The `lightly.models.utils` module provides shared functionality used across SSL models.

### Momentum Updates

```mermaid
graph LR
    Student["Student Model<br/>(θ)"]
    Teacher["Teacher Model<br/>(θ_ema)"]
    
    UpdateRule["θ_ema = m * θ_ema + (1-m) * θ"]
    
    Student --> UpdateRule
    UpdateRule --> Teacher
    
    Momentum["Momentum Factor (m)<br/>Typically 0.99-0.999"]
    Momentum -.-> UpdateRule
```

**Diagram: Momentum Encoder Update**

The `update_momentum()` function updates teacher/momentum encoder parameters using exponential moving average:

```python
update_momentum(model, model_ema, m=0.999)
```

Implementation: [lightly/models/utils.py:262-288]()

Used in MoCo, BYOL, DINO, and other momentum-based methods. See examples: [benchmarks/imagenet/vitb16/dinov2.py:359-360](), [benchmarks/imagenet/vitb16/ibot.py:296-297]()

### Batch Operations

Batch shuffling is used in MoCo to prevent the model from learning shortcuts by ensuring samples in the momentum encoder come from different GPUs.

| Function | Purpose | Distributed Support |
|----------|---------|-------------------|
| `batch_shuffle()` | Randomly shuffle batch | Yes via `distributed=True` |
| `batch_unshuffle()` | Restore original order | Yes via `distributed=True` |
| `concat_all_gather()` | Gather tensors from all GPUs | Multi-GPU only |

**Table: Batch Operation Functions**

```python
# Usage example
x1_shuffled, shuffle = batch_shuffle(x1, distributed=True)
f1 = momentum_encoder(x1_shuffled)
out1 = batch_unshuffle(f1, shuffle, distributed=True)
```

Sources: [lightly/models/utils.py:81-231](), [tests/models/test_ModelUtils.py:170-176]()

### Token Manipulation

Vision Transformer (ViT) operations for working with image patches as tokens:

```mermaid
graph LR
    subgraph "Image to Tokens"
        Image["Image<br/>(B, C, H, W)"]
        Patchify["patchify(patch_size)"]
        Tokens["Tokens<br/>(B, N, C*P²)"]
        Image --> Patchify
        Patchify --> Tokens
    end
    
    subgraph "Token Operations"
        Mask["random_token_mask"]
        GetIdx["get_at_index"]
        SetIdx["set_at_index"]
        MaskIdx["mask_at_index"]
        PrependCls["prepend_class_token"]
    end
    
    subgraph "Tokens to Image"
        TokensOut["Tokens<br/>(B, N, C*P²)"]
        Unpatchify["unpatchify(patch_size)"]
        ImageOut["Image<br/>(B, C, H, W)"]
        TokensOut --> Unpatchify
        Unpatchify --> ImageOut
    end
    
    Tokens --> Mask
    Tokens --> GetIdx
    Tokens --> SetIdx
    Tokens --> MaskIdx
    Tokens --> PrependCls
```

**Diagram: Token Manipulation Functions**

#### Key Functions

| Function | Purpose | Input Shape | Output Shape |
|----------|---------|-------------|--------------|
| `patchify()` | Convert images to patches | (B, C, H, W) | (B, N, C·P²) |
| `unpatchify()` | Reconstruct images from patches | (B, N, C·P²) | (B, C, H, W) |
| `random_token_mask()` | Generate random mask indices | (B, N) | (idx_keep, idx_mask) |
| `get_at_index()` | Select tokens at indices | (B, N, D) | (B, K, D) |
| `set_at_index()` | Set tokens at indices | (B, N, D) | (B, N, D) |
| `mask_at_index()` | Replace tokens with mask token | (B, N, D) | (B, N, D) |
| `prepend_class_token()` | Prepend class token | (B, N, D) | (B, N+1, D) |

**Table: Token Manipulation Functions**

Example usage in MAE:
```python
# Create patches
patches = patchify(images, patch_size=16)  # (B, N, C*16²)

# Random masking
idx_keep, idx_mask = random_token_mask(
    size=(batch_size, sequence_length),
    mask_ratio=0.75,
    mask_class_token=False
)

# Get visible tokens
visible_tokens = get_at_index(tokens, idx_keep)

# Reconstruct
reconstructed = unpatchify(decoded_patches, patch_size=16, channels=3)
```

Sources: [lightly/models/utils.py:358-563](), [tests/models/test_ModelUtils.py:219-338]()

### Masking Strategies

Advanced masking strategies for masked image modeling (MIM) methods:

#### Random Token Mask

Creates random masks for individual tokens, commonly used in MAE:

```python
idx_keep, idx_mask = random_token_mask(
    size=(batch_size, sequence_length),
    mask_ratio=0.75,
    mask_class_token=False  # Never mask class token
)
```

Sources: [lightly/models/utils.py:565-611](), [tests/models/modules/test_masked_autoencoder.py:34-37]()

#### Random Block Mask

Creates block-based masks used in DINOv2 and iBOT:

```mermaid
graph TB
    Input["Image Batch<br/>(B, H, W patches)"]
    
    subgraph "Block Mask Generation"
        SelectImages["Select batch_mask_ratio<br/>of images to mask"]
        
        subgraph "Per Image"
            SampleRatio["Sample mask ratio<br/>[min_image_mask_ratio, max_image_mask_ratio]"]
            GenerateBlocks["Generate random blocks<br/>with random aspect ratios"]
        end
        
        Combine["Combine masks<br/>+ add unmasked images"]
    end
    
    Output["Boolean Mask<br/>(B, H, W)"]
    
    Input --> SelectImages
    SelectImages --> SampleRatio
    SampleRatio --> GenerateBlocks
    GenerateBlocks --> Combine
    Combine --> Output
```

**Diagram: Random Block Mask Generation**

Key parameters:
- `batch_mask_ratio`: Percentage of images to mask (e.g., 0.5)
- `min_image_mask_ratio`, `max_image_mask_ratio`: Range of mask ratios per image
- `min_num_masks_per_block`, `max_num_masks_per_block`: Block size constraints
- `min_block_aspect_ratio`, `max_block_aspect_ratio`: Block shape constraints

```python
# DINOv2-style block masking
block_mask = random_block_mask(
    size=(batch_size, height_patches, width_patches),
    batch_mask_ratio=0.5,
    min_image_mask_ratio=0.1,
    max_image_mask_ratio=0.5,
)
```

Sources: [lightly/models/utils.py:654-832](), [benchmarks/imagenet/vitb16/dinov2.py:153](), [benchmarks/imagenet/vitb16/ibot.py:130-134]()

### Additional Utilities

| Function | Purpose | Reference |
|----------|---------|-----------|
| `normalize_weight()` | Normalize layer weights to unit length | [lightly/models/utils.py:290-293]() |
| `deactivate_requires_grad()` | Disable gradients for a model | [lightly/models/utils.py:233-245]() |
| `activate_requires_grad()` | Enable gradients for a model | [lightly/models/utils.py:248-259]() |
| `nearest_neighbors()` | Find nearest neighbors in feature maps | [lightly/models/utils.py:835-892]() |
| `most_similar_index()` | Find most similar feature indices | [lightly/models/utils.py:895-925]() |
| `pool_masked()` | Pool features according to mask indices | [lightly/models/utils.py:30-78]() |

**Table: Additional Utility Functions**

Sources: [lightly/models/utils.py:1-1500](), [tests/models/test_ModelUtils.py:1-800]()

---

# Page: Loss Functions

# Loss Functions

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/check_example_nbs.yml](.github/workflows/check_example_nbs.yml)
- [.github/workflows/discord_release_notification.yml](.github/workflows/discord_release_notification.yml)
- [Makefile](Makefile)
- [README.md](README.md)
- [benchmarks/imagenet/vitb16/dinov2.py](benchmarks/imagenet/vitb16/dinov2.py)
- [benchmarks/imagenet/vitb16/ibot.py](benchmarks/imagenet/vitb16/ibot.py)
- [docs/source/getting_started/benchmarks.rst](docs/source/getting_started/benchmarks.rst)
- [docs/source/getting_started/benchmarks/cifar10_benchmark.py](docs/source/getting_started/benchmarks/cifar10_benchmark.py)
- [docs/source/getting_started/benchmarks/imagenet100_benchmark.py](docs/source/getting_started/benchmarks/imagenet100_benchmark.py)
- [docs/source/getting_started/benchmarks/imagenette_benchmark.py](docs/source/getting_started/benchmarks/imagenette_benchmark.py)
- [lightly/loss/pmsn_loss.py](lightly/loss/pmsn_loss.py)
- [lightly/models/modules/__init__.py](lightly/models/modules/__init__.py)
- [lightly/models/modules/heads.py](lightly/models/modules/heads.py)
- [lightly/models/modules/ijepa_timm.py](lightly/models/modules/ijepa_timm.py)
- [lightly/models/modules/masked_autoencoder_timm.py](lightly/models/modules/masked_autoencoder_timm.py)
- [lightly/models/modules/masked_vision_transformer_timm.py](lightly/models/modules/masked_vision_transformer_timm.py)
- [lightly/models/utils.py](lightly/models/utils.py)
- [pyproject.toml](pyproject.toml)
- [tests/loss/test_msn_loss.py](tests/loss/test_msn_loss.py)
- [tests/loss/test_pmsn_loss.py](tests/loss/test_pmsn_loss.py)
- [tests/models/modules/test_masked_autoencoder.py](tests/models/modules/test_masked_autoencoder.py)
- [tests/models/test_ModelUtils.py](tests/models/test_ModelUtils.py)
- [tests/models/test_ProjectionHeads.py](tests/models/test_ProjectionHeads.py)

</details>



## Purpose and Scope

This page documents the loss functions available in the Lightly framework for self-supervised learning. Loss functions are a core component of SSL methods, computing the training objective that drives representation learning. Each SSL method (SimCLR, DINO, MAE, etc.) requires specific loss functions that work in conjunction with model architectures and data augmentations.

For information about model architectures and projection heads that produce the inputs to these loss functions, see [Model Components and Utilities](#2.2). For complete SSL model implementations that combine backbones, heads, and losses, see [Self-Supervised Learning Models](#2).

---

## Loss Function Architecture

The following diagram shows how loss functions fit into the SSL training pipeline:

```mermaid
graph TB
    subgraph "Input"
        IMG[Input Images]
    end
    
    subgraph "Data Augmentation"
        VIEWS[Multiple Views<br/>e.g., view0, view1]
    end
    
    subgraph "Model Forward Pass"
        BACKBONE[Backbone Network<br/>ResNet, ViT]
        PROJ_HEAD[Projection Head<br/>SimCLRProjectionHead<br/>DINOProjectionHead, etc.]
        PRED_HEAD[Prediction Head<br/>Optional<br/>SimSiamPredictionHead]
    end
    
    subgraph "Loss Computation"
        LOSS[Loss Function<br/>NTXentLoss<br/>DINOLoss<br/>MSNLoss, etc.]
        MEMORY[Memory Bank<br/>Optional<br/>NNMemoryBankModule]
    end
    
    subgraph "Training"
        OPT[Optimizer Step]
    end
    
    IMG --> VIEWS
    VIEWS --> BACKBONE
    BACKBONE --> PROJ_HEAD
    PROJ_HEAD --> PRED_HEAD
    PRED_HEAD --> LOSS
    PROJ_HEAD --> LOSS
    MEMORY --> LOSS
    LOSS --> OPT
    OPT -.updates.-> BACKBONE
    OPT -.updates.-> PROJ_HEAD
```

**Sources:** [README.md:125-189](), [docs/source/getting_started/benchmarks/cifar10_benchmark.py:1-220]()

---

## Loss Function Categories

Lightly provides loss functions organized into distinct categories based on their learning paradigm:

| Category | Learning Approach | Example Losses | Characteristics |
|----------|------------------|----------------|-----------------|
| **Contrastive** | Maximize similarity between positive pairs, minimize similarity between negative pairs | `NTXentLoss`, `DCLLoss`, `DCLWLoss` | Requires negative samples, often uses memory banks |
| **Asymmetric** | Online network predicts target network outputs | `NegativeCosineSimilarity` | No negative pairs needed, uses stop-gradient |
| **Prototype-Based** | Cluster assignments via learnable prototypes | `SwaVLoss`, `MSNLoss`, `PMSNLoss` | Uses Sinkhorn-Knopp algorithm |
| **Distillation** | Student mimics teacher outputs | `DINOLoss`, `IBOTPatchLoss` | Uses momentum teacher, centering |
| **Regularization** | Enforce properties on embeddings | `BarlowTwinsLoss`, `VICRegLoss`, `VICRegLLoss` | Invariance, variance, covariance constraints |
| **Reconstruction** | Predict masked input patches | MAE reconstruction loss | Used with masked autoencoders |
| **Specialized** | Task-specific objectives | `TiCoLoss`, `KoLeoLoss`, `SMoGLoss` | Method-specific design |

**Sources:** [lightly/loss/__init__.py](), [docs/source/getting_started/benchmarks/imagenette_benchmark.py:77-90]()

---

## Available Loss Functions

The following table lists all implemented loss functions with their primary use cases:

| Loss Function | SSL Method | Year | Key Parameters | Description |
|---------------|------------|------|----------------|-------------|
| `NTXentLoss` | SimCLR, MoCo | 2020 | `temperature`, `memory_bank_size` | Normalized temperature-scaled cross entropy loss |
| `NegativeCosineSimilarity` | BYOL, SimSiam | 2020-2021 | None | Negative cosine similarity between predictions |
| `BarlowTwinsLoss` | Barlow Twins | 2021 | `lambda_param`, `gather_distributed` | Cross-correlation matrix with invariance term |
| `DINOLoss` | DINO, iBOT | 2021 | `output_dim`, `teacher_temp`, `student_temp` | Knowledge distillation with centering |
| `MSNLoss` | MSN | 2022 | `temperature`, `sinkhorn_iterations` | Masked Siamese Networks with prototypes |
| `PMSNLoss` | PMSN | 2022 | `power_law_exponent`, `regularization_weight` | MSN with power law target distribution |
| `SwaVLoss` | SwaV | 2020 | `temperature`, `sinkhorn_iterations` | Swapped prediction with online clustering |
| `VICRegLoss` | VICReg | 2021 | `lambda_param`, `mu_param`, `nu_param` | Variance-Invariance-Covariance regularization |
| `VICRegLLoss` | VICRegL | 2022 | Inherits VICReg params + local loss | VICReg with local feature regularization |
| `DCLLoss` | DCL | 2021 | `temperature`, `weight_fn` | Decoupled Contrastive Learning |
| `DCLWLoss` | DCLW | 2021 | `temperature`, `sigma` | DCL with Gaussian weighting |
| `TiCoLoss` | TiCo | 2024 | `temperature`, `gather_distributed` | Transformation invariance and covariance |
| `IBOTPatchLoss` | iBOT | 2021 | `output_dim`, `teacher_temp` | Patch-level distillation for masked tokens |
| `KoLeoLoss` | DINOv2 | 2023 | None | KoLeo regularization for uniform distribution |
| `SMoGLoss` | SMoG | 2022 | `temperature` | Synchronous momentum grouping |

**Sources:** [docs/source/getting_started/benchmarks/imagenette_benchmark.py:77-90](), [lightly/loss/pmsn_loss.py:1-80](), [benchmarks/imagenet/vitb16/dinov2.py:15-16]()

---

## Loss Function Hierarchy

```mermaid
graph TD
    subgraph "Contrastive Family"
        NT["NTXentLoss<br/>(lightly.loss.ntx_ent_loss)"]
        DCL["DCLLoss<br/>(lightly.loss.dcl_loss)"]
        DCLW["DCLWLoss<br/>(lightly.loss.dclw_loss)"]
    end
    
    subgraph "Prototype Family"
        SWAV["SwaVLoss<br/>(lightly.loss.swav_loss)"]
        MSN["MSNLoss<br/>(lightly.loss.msn_loss)"]
        PMSN["PMSNLoss<br/>(lightly.loss.pmsn_loss)"]
    end
    
    subgraph "Distillation Family"
        DINO["DINOLoss<br/>(lightly.loss.dino_loss)"]
        IBOT["IBOTPatchLoss<br/>(lightly.loss.ibot_patch_loss)"]
    end
    
    subgraph "Regularization Family"
        BARLOW["BarlowTwinsLoss<br/>(lightly.loss.barlow_twins_loss)"]
        VICREG["VICRegLoss<br/>(lightly.loss.vicreg_loss)"]
        VICREGL["VICRegLLoss<br/>(lightly.loss.vicregl_loss)"]
    end
    
    subgraph "Other"
        NEG_COS["NegativeCosineSimilarity<br/>(lightly.loss.neg_cos_sim)"]
        TICO["TiCoLoss<br/>(lightly.loss.tico_loss)"]
        KOLEO["KoLeoLoss<br/>(lightly.loss.koleo_loss)"]
    end
    
    MSN -.extends.-> PMSN
    VICREG -.extends.-> VICREGL
```

**Sources:** [lightly/loss/pmsn_loss.py:10-11](), [lightly/loss/msn_loss.py]()

---

## Common Loss Parameters

### Temperature Scaling

Most contrastive and prototype-based losses use a temperature parameter to control the sharpness of probability distributions:

| Loss | Temperature Parameter | Typical Range | Effect |
|------|----------------------|---------------|---------|
| `NTXentLoss` | `temperature` | 0.1 - 0.5 | Lower = sharper distributions, harder negatives |
| `DINOLoss` | `student_temp`, `teacher_temp` | 0.04 - 0.1 | Asymmetric temps balance predictions |
| `MSNLoss` | `temperature` | 0.1 | Controls prototype assignment sharpness |
| `SwaVLoss` | `temperature` | 0.1 | Affects clustering behavior |

**Example from benchmark:**

[docs/source/getting_started/benchmarks/cifar10_benchmark.py:342-344]()

**Sources:** [docs/source/getting_started/benchmarks/cifar10_benchmark.py:340-388](), [tests/loss/test_msn_loss.py:30-36]()

### Memory Bank Configuration

Memory banks store previous embeddings to provide additional negative samples without recomputing:

| Parameter | Purpose | Typical Values |
|-----------|---------|----------------|
| `memory_bank_size` | Number of cached embeddings | 4096 - 65536 |
| Tuple format | `(bank_size, embedding_dim)` | `(4096, 128)` |

**Example usage:**

[docs/source/getting_started/benchmarks/cifar10_benchmark.py:342-344]()

Memory banks are particularly important for:
- **MoCo**: Core component storing momentum encoder outputs
- **NNCLR**: Nearest neighbor lookup for support set
- Small batch sizes where in-batch negatives are insufficient

**Sources:** [docs/source/getting_started/benchmarks/cifar10_benchmark.py:323-387](), [docs/source/getting_started/benchmarks/imagenette_benchmark.py:122]()

### Distributed Training Support

Losses support gathering features from multiple GPUs before computing loss:

| Parameter | Purpose | When to Use |
|-----------|---------|-------------|
| `gather_distributed` | Gather embeddings from all GPUs | When using DDP and want global negatives |

**Example configuration:**

[docs/source/getting_started/benchmarks/cifar10_benchmark.py:119-121]()

When `gather_distributed=True`:
- Effective batch size for loss computation = `batch_size * num_gpus`
- All GPUs see the same negative samples
- Improves training quality at computational cost

**Sources:** [README.md:263-274](), [docs/source/getting_started/benchmarks/cifar10_benchmark.py:108-139]()

---

## Integration with SSL Methods

The following table shows which loss functions are used by each SSL method:

```mermaid
graph LR
    subgraph "Contrastive Methods"
        SIMCLR["SimCLR"]
        MOCO["MoCo"]
        NNCLR["NNCLR"]
        DENSECL["DenseCL"]
    end
    
    subgraph "Asymmetric Methods"
        BYOL["BYOL"]
        SIMSIAM["SimSiam"]
    end
    
    subgraph "Clustering Methods"
        SWAV["SwaV"]
        MSN_M["MSN"]
        PMSN_M["PMSN"]
    end
    
    subgraph "Distillation Methods"
        DINO_M["DINO"]
        IBOT_M["iBOT"]
        DINOV2["DINOv2"]
    end
    
    subgraph "Regularization Methods"
        BARLOW_M["BarlowTwins"]
        VICREG_M["VICReg"]
        VICREGL_M["VICRegL"]
    end
    
    subgraph "Loss Functions"
        L_NTXENT["NTXentLoss"]
        L_NEGCOS["NegativeCosineSimilarity"]
        L_SWAV["SwaVLoss"]
        L_MSN["MSNLoss"]
        L_PMSN["PMSNLoss"]
        L_DINO["DINOLoss"]
        L_IBOT["IBOTPatchLoss"]
        L_BARLOW["BarlowTwinsLoss"]
        L_VICREG["VICRegLoss"]
        L_VICREGL["VICRegLLoss"]
        L_KOLEO["KoLeoLoss"]
    end
    
    SIMCLR --> L_NTXENT
    MOCO --> L_NTXENT
    NNCLR --> L_NTXENT
    DENSECL --> L_NTXENT
    BYOL --> L_NEGCOS
    SIMSIAM --> L_NEGCOS
    SWAV --> L_SWAV
    MSN_M --> L_MSN
    PMSN_M --> L_PMSN
    DINO_M --> L_DINO
    IBOT_M --> L_DINO
    IBOT_M --> L_IBOT
    DINOV2 --> L_DINO
    DINOV2 --> L_IBOT
    DINOV2 --> L_KOLEO
    BARLOW_M --> L_BARLOW
    VICREG_M --> L_VICREG
    VICREGL_M --> L_VICREGL
```

**Sources:** [docs/source/getting_started/benchmarks/cifar10_benchmark.py:62-82](), [docs/source/getting_started/benchmarks/imagenette_benchmark.py:77-90](), [benchmarks/imagenet/vitb16/dinov2.py:113-116]()

---

## Usage Patterns

### Basic Contrastive Loss (SimCLR)

Typical usage of `NTXentLoss` for contrastive learning:

[README.md:174-176]()

The loss computes similarity between positive pairs (z0, z1) and pushes apart negative pairs from the same batch.

**Full training loop example:**

[README.md:180-189]()

**Sources:** [README.md:125-189](), [docs/source/getting_started/benchmarks/cifar10_benchmark.py:390-419]()

### Asymmetric Loss (SimSiam)

Using `NegativeCosineSimilarity` with prediction head:

[README.md:214-216]()

Note the `.detach()` on the projection output - this implements the stop-gradient operation critical to SimSiam.

**Full example:**

[README.md:196-216]()

**Sources:** [README.md:195-218](), [docs/source/getting_started/benchmarks/cifar10_benchmark.py:421-456]()

### Prototype-Based Loss (MSN)

`MSNLoss` and `PMSNLoss` require prototypes and use Sinkhorn-Knopp normalization:

[tests/loss/test_msn_loss.py:46-65]()

**Key parameters:**
- `temperature`: Controls sharpness of prototype assignments (default: 0.1)
- `sinkhorn_iterations`: Number of normalization iterations (default: 3)
- `regularization_weight`: Weight for entropy regularization (default: 1.0)

**PMSN-specific:**

[lightly/loss/pmsn_loss.py:47-54]()

The `power_law_exponent` parameter (default: 0.25) controls the prior distribution over prototypes.

**Sources:** [lightly/loss/pmsn_loss.py:1-80](), [tests/loss/test_msn_loss.py:1-100]()

### Distillation Loss (DINO)

`DINOLoss` implements knowledge distillation with centering and sharpening:

[benchmarks/imagenet/vitb16/dinov2.py:113-116]()

**Teacher temperature scheduling:**

[benchmarks/imagenet/vitb16/dinov2.py:182-189]()

The teacher temperature typically uses a warmup schedule, starting low (e.g., 0.04) and increasing to a final value (e.g., 0.07).

**Loss computation:**

[benchmarks/imagenet/vitb16/dinov2.py:189-193]()

**Sources:** [benchmarks/imagenet/vitb16/dinov2.py:48-205](), [benchmarks/imagenet/vitb16/ibot.py:85-92]()

### Multi-Loss Training (DINOv2)

Complex methods like DINOv2 combine multiple losses:

[benchmarks/imagenet/vitb16/dinov2.py:113-116]()

**Weighted combination:**

[benchmarks/imagenet/vitb16/dinov2.py:189-205]()

Loss weights can be scheduled during training to balance different objectives.

**Sources:** [benchmarks/imagenet/vitb16/dinov2.py:113-206]()

---

## Memory Bank Integration

### NNMemoryBankModule

The `NNMemoryBankModule` stores feature vectors for nearest neighbor lookup:

```mermaid
graph LR
    subgraph "Training Step"
        INPUT["Input Batch<br/>Features z"]
        BANK["Memory Bank<br/>Stored Features"]
        NN["Nearest Neighbor<br/>Lookup"]
        LOSS["Loss Computation<br/>with NN"]
        UPDATE["Update Bank<br/>with New Features"]
    end
    
    INPUT --> NN
    BANK --> NN
    NN --> LOSS
    INPUT --> UPDATE
    UPDATE --> BANK
```

**Usage pattern in MoCo:**

[docs/source/getting_started/benchmarks/cifar10_benchmark.py:342-344]()

The memory bank is created with a tuple `(memory_bank_size, embedding_dim)` and automatically manages FIFO updates.

**Benefits:**
- Provides more negative samples than fit in a single batch
- Enables larger effective batch sizes without increased GPU memory
- Critical for contrastive methods on small batch sizes

**Sources:** [docs/source/getting_started/benchmarks/cifar10_benchmark.py:323-387](), [lightly/models/modules/__init__.py:32]()

### Memory Bank Configuration for Distributed Training

When using distributed training with larger batch sizes, memory bank size should be adjusted:

[docs/source/getting_started/benchmarks/cifar10_benchmark.py:342-344]()

**Note:** Comments in benchmarks indicate memory banks are increased from 4096 to 8192 for batch size 512 to prevent rapid turnover.

**Sources:** [docs/source/getting_started/benchmarks/cifar10_benchmark.py:29-51]()

---

## Specialized Loss Functions

### IBOTPatchLoss

Patch-level distillation for masked image modeling:

[benchmarks/imagenet/vitb16/ibot.py:89-92]()

**Usage in training:**

[benchmarks/imagenet/vitb16/ibot.py:194-198]()

The `mask` parameter specifies which patches are masked and should be predicted.

**Sources:** [benchmarks/imagenet/vitb16/ibot.py:38-206](), [benchmarks/imagenet/vitb16/dinov2.py:114]()

### KoLeoLoss

Regularization for uniform distribution of features:

[benchmarks/imagenet/vitb16/dinov2.py:115]()

**Usage:**

[benchmarks/imagenet/vitb16/dinov2.py:199-202]()

Encourages feature vectors to be uniformly distributed on the unit sphere, preventing dimensional collapse.

**Sources:** [benchmarks/imagenet/vitb16/dinov2.py:115-202]()

### TiCoLoss

Transformation invariance and covariance loss:

[docs/source/getting_started/benchmarks/imagenette_benchmark.py:87]()

Used in the TiCo method for learning invariant representations.

**Sources:** [docs/source/getting_started/benchmarks/imagenette_benchmark.py:85-89]()

---

## Loss Function Parameters Reference

### NTXentLoss

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `temperature` | float | 0.5 | Temperature scaling parameter |
| `memory_bank_size` | int or tuple | 0 | Size of memory bank, 0 disables |
| `gather_distributed` | bool | False | Gather features from all GPUs |

### DINOLoss

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `output_dim` | int | 65536 | Dimension of output features |
| `teacher_temp` | float | 0.04 | Teacher network temperature |
| `student_temp` | float | 0.1 | Student network temperature |
| `center_momentum` | float | 0.9 | EMA momentum for center |

### MSNLoss

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `temperature` | float | 0.1 | Temperature for prototype similarities |
| `sinkhorn_iterations` | int | 3 | Number of Sinkhorn-Knopp iterations |
| `regularization_weight` | float | 1.0 | Weight for entropy regularization |
| `gather_distributed` | bool | False | Gather features from all GPUs |

### PMSNLoss (extends MSNLoss)

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `power_law_exponent` | float | 0.25 | Exponent for power law prior |
| All MSNLoss params | - | - | Inherits all MSNLoss parameters |

### BarlowTwinsLoss

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `lambda_param` | float | 5e-3 | Weight for off-diagonal terms |
| `gather_distributed` | bool | False | Gather features from all GPUs |

### VICRegLoss

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `lambda_param` | float | 25.0 | Weight for variance term |
| `mu_param` | float | 25.0 | Weight for invariance term |
| `nu_param` | float | 1.0 | Weight for covariance term |

**Sources:** [tests/loss/test_msn_loss.py:30-44](), [lightly/loss/pmsn_loss.py:47-54]()

---

## Performance Considerations

### Computational Complexity

Different loss functions have varying computational requirements:

| Loss Type | Complexity | Memory Usage | Notes |
|-----------|------------|--------------|-------|
| `NTXentLoss` | O(B²) | Low | Scales quadratically with batch size |
| `NTXentLoss` + memory bank | O(B·M) | Medium | M = memory bank size |
| `DINOLoss` | O(B·D) | Low | D = output dimension |
| `MSNLoss` | O(B·K·I) | Medium | K = prototypes, I = Sinkhorn iterations |
| `BarlowTwinsLoss` | O(D²) | Low | Computes cross-correlation matrix |

### Distributed Training Impact

When using `gather_distributed=True`:

**Memory increase:**
- Features from all GPUs are gathered
- Memory usage scales with number of GPUs
- Batch size per GPU can be reduced to compensate

**Computation increase:**
- Loss computed with global view of data
- Better gradient quality
- Longer training time per step

**Example from benchmark:**

[README.md:263-274]()

**Sources:** [README.md:263-277](), [docs/source/getting_started/benchmarks/cifar10_benchmark.py:108-139]()

---

## Summary

Lightly provides a comprehensive set of loss functions covering all major self-supervised learning paradigms:

1. **Contrastive losses** (`NTXentLoss`, `DCLLoss`) for learning by comparing positive and negative pairs
2. **Prototype-based losses** (`MSNLoss`, `PMSNLoss`, `SwaVLoss`) for online clustering
3. **Distillation losses** (`DINOLoss`, `IBOTPatchLoss`) for knowledge transfer
4. **Regularization losses** (`BarlowTwinsLoss`, `VICRegLoss`) for decorrelation
5. **Specialized losses** for specific methods and use cases

Key configuration considerations:
- **Temperature** controls prediction sharpness
- **Memory banks** provide additional negatives efficiently
- **Distributed gathering** improves training quality at computational cost
- **Loss combinations** enable sophisticated training objectives

For complete training examples demonstrating these losses in action, see the benchmark implementations and the main README examples.

**Sources:** [README.md:1-437](), [docs/source/getting_started/benchmarks.rst:1-219](), [lightly/loss/__init__.py]()

---

# Page: Transforms and Augmentations

# Transforms and Augmentations

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [docs/source/getting_started/advanced.rst](docs/source/getting_started/advanced.rst)
- [docs/source/getting_started/benchmarks.rst](docs/source/getting_started/benchmarks.rst)
- [docs/source/getting_started/benchmarks/cifar10_benchmark.py](docs/source/getting_started/benchmarks/cifar10_benchmark.py)
- [docs/source/getting_started/benchmarks/imagenet100_benchmark.py](docs/source/getting_started/benchmarks/imagenet100_benchmark.py)
- [docs/source/getting_started/benchmarks/imagenette_benchmark.py](docs/source/getting_started/benchmarks/imagenette_benchmark.py)
- [docs/source/getting_started/command_line_tool.rst](docs/source/getting_started/command_line_tool.rst)
- [docs/source/getting_started/images/lightly_overview.png](docs/source/getting_started/images/lightly_overview.png)
- [docs/source/getting_started/install.rst](docs/source/getting_started/install.rst)
- [docs/source/getting_started/lightly_at_a_glance.rst](docs/source/getting_started/lightly_at_a_glance.rst)
- [docs/source/getting_started/main_concepts.rst](docs/source/getting_started/main_concepts.rst)
- [docs/source/index.rst](docs/source/index.rst)
- [docs/source/lightly.models.utils.rst](docs/source/lightly.models.utils.rst)
- [docs/source/tutorials/structure_your_input.rst](docs/source/tutorials/structure_your_input.rst)
- [docs/source/tutorials_source/package/Base-RCNN-FPN.yaml](docs/source/tutorials_source/package/Base-RCNN-FPN.yaml)
- [docs/source/tutorials_source/package/tutorial_custom_augmentations.py](docs/source/tutorials_source/package/tutorial_custom_augmentations.py)
- [docs/source/tutorials_source/package/tutorial_moco_memory_bank.py](docs/source/tutorials_source/package/tutorial_moco_memory_bank.py)
- [docs/source/tutorials_source/package/tutorial_pretrain_detectron2.py](docs/source/tutorials_source/package/tutorial_pretrain_detectron2.py)
- [docs/source/tutorials_source/package/tutorial_simclr_clothing.py](docs/source/tutorials_source/package/tutorial_simclr_clothing.py)
- [docs/source/tutorials_source/package/tutorial_simsiam_esa.py](docs/source/tutorials_source/package/tutorial_simsiam_esa.py)

</details>



This page documents the transform and augmentation system in Lightly SSL, which is responsible for creating multiple augmented views of input images during self-supervised learning. Transforms define what invariances the model learns and are critical to the success of SSL training.

For information about how transforms integrate with the data loading pipeline, see [Data Handling](#3). For details on specific SSL methods that use these transforms, see [Self-Supervised Learning Models](#2).

## Overview

Self-supervised learning methods typically create multiple views of each input image by applying random transformations. The model then learns to produce similar representations for different views of the same image, thereby learning invariance to the applied transformations. Lightly provides:

- **Method-specific transforms**: Pre-configured transform pipelines for popular SSL methods (SimCLR, DINO, MAE, etc.)
- **Custom transform composition**: Tools to build custom multi-view transforms
- **Modular augmentations**: Individual augmentation operations that can be mixed and matched

The transforms are implemented using PyTorch/torchvision primitives and are compatible with the standard PyTorch data loading pipeline.

Sources: [lightly/transforms/](https://github.com/lightly-ai/lightly/tree/master/lightly/transforms), [docs/source/getting_started/advanced.rst:8-74](), [README.md:125-162]()

## Transform Pipeline Architecture

```mermaid
graph TB
    Input["Input Image<br/>(PIL/numpy)"]
    Transform["Transform Pipeline<br/>(e.g., SimCLRTransform)"]
    Views["Multiple Views<br/>(torch.Tensor)"]
    Collate["MultiViewCollate<br/>(optional)"]
    Batch["Batched Views<br/>for Model"]
    
    Input --> Transform
    Transform --> Views
    Views --> Collate
    Collate --> Batch
    
    subgraph "Transform Components"
        RC["RandomResizedCrop"]
        HF["RandomHorizontalFlip"]
        CJ["ColorJitter"]
        GB["GaussianBlur"]
        GS["RandomGrayscale"]
        Sol["RandomSolarization"]
        Norm["Normalize"]
        
        RC --> HF
        HF --> CJ
        CJ --> GB
        GB --> GS
        GS --> Sol
        Sol --> Norm
    end
    
    Transform -.contains.-> RC
```

**Transform Pipeline Flow**

The transform pipeline processes each input image through a sequence of augmentation operations to produce one or more augmented views. The number and type of views depends on the SSL method being used.

Sources: [lightly/transforms/simclr_transform.py](), [lightly/transforms/multi_view_transform.py](), [docs/source/getting_started/advanced.rst:76-92]()

## Method-Specific Transforms

Lightly provides pre-configured transform classes for major SSL methods. Each transform creates the specific number and types of views required by its corresponding SSL method.

```mermaid
graph LR
    subgraph "Contrastive Methods (2 views)"
        SimCLRTransform["SimCLRTransform<br/>2 random crops"]
        MoCoTransform["MoCoV2Transform<br/>2 random crops"]
        BYOLTransform["BYOLTransform<br/>view1 + view2"]
        SimSiamTransform["SimSiamTransform<br/>2 random crops"]
    end
    
    subgraph "Multi-Crop Methods"
        DINOTransform["DINOTransform<br/>2 global + N local"]
        SwaVTransform["SwaVTransform<br/>2 standard + 6 small"]
        FastSiamTransform["FastSiamTransform<br/>4 crops total"]
    end
    
    subgraph "Masked Methods (1 view)"
        MAETransform["MAETransform<br/>1 crop + masking"]
        MSNTransform["MSNTransform<br/>1 random + focal"]
        SimMIMTransform["SimMIMTransform<br/>1 crop + masking"]
    end
```

**SSL Method to Transform Mapping**

| Transform Class | SSL Method | Number of Views | Key Parameters |
|-----------------|------------|-----------------|----------------|
| `SimCLRTransform` | SimCLR | 2 | `input_size`, `cj_prob`, `gaussian_blur` |
| `MoCoV2Transform` | MoCo v2 | 2 | `input_size`, `gaussian_blur` |
| `BYOLTransform` | BYOL | 2 | `view_1_transform`, `view_2_transform` |
| `SimSiamTransform` | SimSiam | 2 | `input_size`, `cj_strength` |
| `DINOTransform` | DINO/DINOv2 | 2 global + N local | `global_crop_size`, `local_crop_size`, `n_local_views` |
| `SwaVTransform` | SwaV | Configurable | `crop_sizes`, `crop_counts` |
| `MAETransform` | MAE | 1 | `input_size` (masking done in model) |
| `MSNTransform` | MSN/PMSN | 2 | `random_size`, `focal_size` |
| `FastSiamTransform` | FastSiam | 4 | `input_size` |

Sources: [lightly/transforms/simclr_transform.py](), [lightly/transforms/dino_transform.py](), [lightly/transforms/mae_transform.py](), [lightly/transforms/swav_transform.py](), [docs/source/getting_started/benchmarks/imagenette_benchmark.py:169-235]()

### Common Transform Parameters

Most transforms accept these configuration parameters:

- **`input_size`**: Target size for cropped images (int or tuple)
- **`cj_prob`**: Probability of applying color jitter (default varies by method)
- **`cj_strength`**: Strength of color jitter (default varies by method)
- **`gaussian_blur`**: Probability or tuple of probabilities for Gaussian blur
- **`hf_prob`**: Probability of horizontal flip (default 0.5)
- **`vf_prob`**: Probability of vertical flip (default 0.0)
- **`rr_prob`**: Probability of random 90-degree rotation (default 0.0)
- **`min_scale`**: Minimum scale for random resized crop (default varies)
- **`random_gray_scale`**: Probability of grayscale conversion

Example usage from tutorials:

```python
# SimCLR transform with custom parameters
from lightly.transforms import SimCLRTransform

transform = SimCLRTransform(
    input_size=128,      # Resize to 128x128
    cj_prob=0.5,         # 50% chance of color jitter
    gaussian_blur=0.0,   # Disable Gaussian blur
)
```

Sources: [docs/source/tutorials_source/package/tutorial_simclr_clothing.py:91](), [docs/source/getting_started/advanced.rst:100-110](), [docs/source/getting_started/benchmarks/cifar10_benchmark.py:166-213]()

## MultiViewTransform Composition

The `MultiViewTransform` class allows composition of arbitrary transforms to create custom multi-view pipelines.

```mermaid
graph TB
    Image["Input Image"]
    MVT["MultiViewTransform"]
    T1["Transform 1<br/>(e.g., global crop)"]
    T2["Transform 2<br/>(e.g., global crop)"]
    T3["Transform 3<br/>(e.g., local crop)"]
    T4["Transform 4<br/>(e.g., local crop)"]
    
    V1["View 1"]
    V2["View 2"]
    V3["View 3"]
    V4["View 4"]
    
    Views["Tuple of Views<br/>(view1, view2, view3, view4)"]
    
    Image --> MVT
    MVT --> T1
    MVT --> T2
    MVT --> T3
    MVT --> T4
    
    T1 --> V1
    T2 --> V2
    T3 --> V3
    T4 --> V4
    
    V1 --> Views
    V2 --> Views
    V3 --> Views
    V4 --> Views
```

**MultiViewTransform Architecture**

Example from documentation:

```python
from torchvision import transforms as T
from lightly.transforms import MultiViewTransform

# Global view transform (224x224 patches)
global_view = T.Compose([
    T.RandomResizedCrop(size=224, scale=(0.08, 1.0)),
    T.RandomHorizontalFlip(p=0.5),
    T.RandomGrayscale(p=0.2),
    T.ToTensor(),
])

# Local view transform (96x96 patches)
local_view = T.Compose([
    T.RandomResizedCrop(size=96, scale=(0.05, 0.4)),
    T.RandomHorizontalFlip(p=0.5),
    T.ToTensor(),
])

# Combine: 2 global + 2 local views
transform = MultiViewTransform([
    global_view,
    global_view,
    local_view,
    local_view,
])

# Returns tuple of 4 views
views = transform(image)
```

Sources: [docs/source/getting_started/advanced.rst:116-142](), [lightly/transforms/multi_view_transform.py]()

## Augmentation Types and Learned Invariances

Different augmentations induce different invariances in the learned representations. Understanding these is crucial for selecting appropriate transforms for your domain.

### Augmentation Catalog

```mermaid
graph TB
    subgraph "Spatial Augmentations"
        RRC["RandomResizedCrop<br/>Scale + aspect ratio invariance"]
        HF["RandomHorizontalFlip<br/>Left-right invariance"]
        VF["RandomVerticalFlip<br/>Up-down invariance"]
        RR["RandomRotate90<br/>Orientation invariance"]
    end
    
    subgraph "Color Augmentations"
        CJ["ColorJitter<br/>Brightness, contrast, saturation, hue"]
        GS["RandomGrayscale<br/>Color channel invariance"]
        SOL["RandomSolarization<br/>Pixel value inversion"]
    end
    
    subgraph "Texture Augmentations"
        GB["GaussianBlur<br/>High-frequency detail invariance"]
    end
    
    subgraph "Normalization"
        NORM["Normalize<br/>ImageNet statistics"]
    end
```

**Augmentation Categories and Effects**

| Category | Augmentation | Invariance Learned | Typical Use Cases |
|----------|--------------|-------------------|-------------------|
| **Spatial** | `RandomResizedCrop` | Object scale, position, partial visibility | Universal (all datasets) |
| | `RandomHorizontalFlip` | Left-right orientation | Natural images, objects |
| | `RandomVerticalFlip` | Up-down orientation | Satellite/aerial imagery, medical scans |
| | `RandomRotate` (90°) | Camera orientation | Satellite imagery, texture classification |
| **Color** | `ColorJitter` | Color variations, lighting | Natural images (avoid for X-ray, medical) |
| | `RandomGrayscale` | Color presence | Objects where color is not discriminative |
| | `RandomSolarization` | Pixel value inversion | Robustness augmentation |
| **Texture** | `GaussianBlur` | High-frequency details | Focusing on shape over texture |

Sources: [docs/source/getting_started/advanced.rst:26-59](), [README.md:14-24]()

### Domain-Specific Considerations

**Natural Images** (ImageNet, COCO):
- Use all standard augmentations including color jitter and blur
- Typical config: `SimCLRTransform(input_size=224)`

**Small Images** (CIFAR-10, CIFAR-100):
- Disable Gaussian blur (images too small)
- Example: `SimCLRTransform(input_size=32, gaussian_blur=0.0)`

**Satellite/Aerial Imagery**:
- Enable vertical flip and 90° rotation
- Use weak color jitter
- Example: `SimCLRTransform(input_size=256, vf_prob=0.5, rr_prob=0.5, cj_prob=0.2)`

**Medical/X-ray Images**:
- Disable color augmentations (grayscale images)
- Use custom preprocessing (e.g., histogram normalization)
- Focus on spatial augmentations only

Sources: [docs/source/tutorials_source/package/tutorial_simsiam_esa.py:92-108](), [docs/source/tutorials_source/package/tutorial_custom_augmentations.py:88-151](), [docs/source/getting_started/benchmarks/cifar10_benchmark.py:172-177]()

## Custom Augmentation Implementation

Users can implement custom augmentations and integrate them with Lightly's transform system. Custom augmentations should be callable objects that accept and return images.

### Custom Augmentation Pattern

```mermaid
graph LR
    Input["Input<br/>(PIL/numpy/tensor)"]
    Custom1["Custom Aug 1<br/>__call__(image)"]
    Custom2["Custom Aug 2<br/>__call__(image)"]
    Torchvision["Torchvision Aug<br/>(e.g., ToTensor)"]
    Lightly["Lightly Aug<br/>(e.g., Normalize)"]
    Output["Output<br/>(torch.Tensor)"]
    
    Input --> Custom1
    Custom1 --> Custom2
    Custom2 --> Torchvision
    Torchvision --> Lightly
    Lightly --> Output
```

**Custom Augmentation Integration**

Example from X-ray tutorial showing histogram normalization and Gaussian noise:

```python
# Custom augmentation for 16-bit to 8-bit conversion
class HistogramNormalize:
    def __init__(self, number_bins=256):
        self.number_bins = number_bins
    
    def __call__(self, image: np.array) -> Image:
        # Histogram equalization
        histogram, bins = np.histogram(
            image.flatten(), self.number_bins, density=True
        )
        cdf = histogram.cumsum()
        cdf = 255 * cdf / cdf[-1]
        image_equalized = np.interp(image.flatten(), bins[:-1], cdf)
        return Image.fromarray(image_equalized.reshape(image.shape))

# Custom noise augmentation
class GaussianNoise:
    def __call__(self, sample: torch.Tensor) -> torch.Tensor:
        mu = sample.mean()
        snr = np.random.randint(low=4, high=8)
        sigma = mu / snr
        noise = torch.normal(torch.zeros(sample.shape), sigma)
        return sample + noise

# Compose with standard transforms
transform = T.Compose([
    HistogramNormalize(number_bins=256),  # Custom
    T.RandomResizedCrop(128),
    T.RandomHorizontalFlip(),
    T.ToTensor(),
    GaussianNoise(),  # Custom (after ToTensor)
    T.Normalize(mean=[0.485], std=[0.229]),
])
```

Sources: [docs/source/tutorials_source/package/tutorial_custom_augmentations.py:100-144](), [docs/source/getting_started/advanced.rst:95-162]()

## Transform Configuration Patterns

### Pattern 1: Using Pre-configured Transforms

The simplest approach is to use method-specific transforms with default or slightly modified parameters:

```python
from lightly.data import LightlyDataset
from lightly.transforms import SimCLRTransform

# Use defaults
transform = SimCLRTransform()

# Or customize parameters
transform = SimCLRTransform(
    input_size=128,
    cj_prob=0.8,
    gaussian_blur=0.5,
)

dataset = LightlyDataset(
    input_dir='path/to/data',
    transform=transform
)
```

Sources: [docs/source/tutorials_source/package/tutorial_simclr_clothing.py:79-106](), [README.md:160-161]()

### Pattern 2: Multi-View Custom Composition

For research or custom SSL methods, compose multiple transforms:

```python
from torchvision import transforms as T
from lightly.transforms import MultiViewTransform
from lightly.transforms.utils import IMAGENET_NORMALIZE

# Define individual view transforms
strong_aug = T.Compose([
    T.RandomResizedCrop(224, scale=(0.2, 1.0)),
    T.RandomHorizontalFlip(),
    T.ColorJitter(0.4, 0.4, 0.4, 0.1),
    T.RandomGrayscale(p=0.2),
    T.ToTensor(),
    T.Normalize(**IMAGENET_NORMALIZE),
])

weak_aug = T.Compose([
    T.RandomResizedCrop(224, scale=(0.5, 1.0)),
    T.RandomHorizontalFlip(),
    T.ToTensor(),
    T.Normalize(**IMAGENET_NORMALIZE),
])

# Combine into multi-view transform
transform = MultiViewTransform([strong_aug, weak_aug])
```

Sources: [docs/source/getting_started/advanced.rst:116-142]()

### Pattern 3: Dataset-Specific Transforms

Different transforms for training vs. inference:

```python
from lightly.transforms import SimCLRTransform
import torchvision.transforms as T

# Training: Multi-view augmentation
train_transform = SimCLRTransform(input_size=128)
train_dataset = LightlyDataset(
    input_dir='data/train',
    transform=train_transform
)

# Inference: Single view, minimal augmentation
test_transform = T.Compose([
    T.Resize(128),
    T.CenterCrop(128),
    T.ToTensor(),
    T.Normalize(mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]),
])
test_dataset = LightlyDataset(
    input_dir='data/test',
    transform=test_transform
)
```

Sources: [docs/source/tutorials_source/package/tutorial_moco_memory_bank.py:126-161](), [docs/source/getting_started/benchmarks/imagenette_benchmark.py:242-249]()

## Transform Utilities

Lightly provides utility functions and constants for common transform operations.

### IMAGENET_NORMALIZE

Pre-computed normalization statistics for ImageNet:

```python
from lightly.transforms.utils import IMAGENET_NORMALIZE

# Usage
T.Normalize(
    mean=IMAGENET_NORMALIZE["mean"],  # [0.485, 0.456, 0.406]
    std=IMAGENET_NORMALIZE["std"],    # [0.229, 0.224, 0.225]
)
```

Sources: [lightly/transforms/utils.py](), [docs/source/getting_started/benchmarks/imagenette_benchmark.py:236-239]()

### Custom Augmentation Classes

Lightly provides custom augmentations not available in torchvision:

- **`RandomSolarization`**: Inverts pixel values above a threshold
- **`RandomRotate`**: 90-degree rotations (0°, 90°, 180°, 270°)

These can be imported from `lightly.transforms`:

```python
from lightly.transforms import RandomRotate, RandomSolarization

# Use in custom pipelines
transform = T.Compose([
    T.RandomResizedCrop(224),
    RandomRotate(prob=0.5),  # 50% chance of 90° rotation
    RandomSolarization(prob=0.2),  # 20% chance of solarization
    T.ToTensor(),
])
```

Sources: [docs/source/getting_started/advanced.rst:91-92]()

## Integration with Data Loading

Transforms are applied automatically by the dataset and dataloader pipeline:

```mermaid
graph LR
    Dataset["LightlyDataset<br/>+ transform"]
    Loader["DataLoader<br/>+ collate_fn"]
    Batch["Batch<br/>(views, labels, filenames)"]
    Model["SSL Model"]
    
    Dataset -->|"__getitem__<br/>applies transform"| Loader
    Loader -->|"collate_fn<br/>stacks views"| Batch
    Batch --> Model
```

**Data Loading Pipeline**

When using `LightlyDataset` with a transform:

1. **`LightlyDataset.__getitem__(index)`** loads raw image and applies transform
2. Transform returns tuple of views: `(view0, view1, ...)`
3. **`DataLoader`** collects multiple samples into a batch
4. **`MultiViewCollate`** (optional) properly stacks multi-view batches
5. Model receives batch: `((view0_batch, view1_batch, ...), labels, filenames)`

Example from benchmark code:

```python
from lightly.data import LightlyDataset
from lightly.transforms import SimCLRTransform

# Create dataset with transform
transform = SimCLRTransform(input_size=128)
dataset = LightlyDataset(
    input_dir='path/to/images',
    transform=transform
)

# Create dataloader
dataloader = torch.utils.data.DataLoader(
    dataset,
    batch_size=256,
    shuffle=True,
    drop_last=True,
    num_workers=8,
)

# Training loop receives multi-view batches
for (view0, view1), labels, filenames in dataloader:
    z0 = model(view0)
    z1 = model(view1)
    loss = criterion(z0, z1)
```

Sources: [docs/source/tutorials_source/package/tutorial_simclr_clothing.py:106-124](), [docs/source/getting_started/benchmarks/cifar10_benchmark.py:263-287]()

## Performance Considerations

### Memory vs. Computation Tradeoff

- **More views**: Higher GPU memory usage but better representations
- **Larger input sizes**: More memory, longer training time
- **Blur/strong augmentations**: Increased CPU preprocessing time

Typical configurations by GPU memory:

| GPU Memory | Batch Size | Input Size | Example Config |
|------------|------------|------------|----------------|
| 8 GB | 128 | 128×128 | CIFAR-10 style training |
| 16 GB | 256 | 128×128 | Medium-scale training |
| 16 GB | 128 | 224×224 | ImageNet-style training |
| 32+ GB | 256+ | 224×224 | Full-scale ImageNet training |

Sources: [docs/source/tutorials_source/package/tutorial_simclr_clothing.py:56-65](), [docs/source/tutorials_source/package/tutorial_custom_augmentations.py:66-69]()

### CPU Preprocessing

Use `num_workers > 0` in DataLoader to parallelize transform application:

```python
dataloader = torch.utils.data.DataLoader(
    dataset,
    batch_size=256,
    num_workers=8,  # 8 parallel workers for data loading
    pin_memory=True,  # Faster GPU transfer
)
```

Sources: [docs/source/tutorials_source/package/tutorial_simclr_clothing.py:110-116]()

## Summary

The transform system in Lightly provides:

1. **Pre-configured transforms** for major SSL methods (SimCLR, DINO, MAE, etc.)
2. **Flexible composition** via `MultiViewTransform` for custom pipelines  
3. **Domain-specific customization** for different image types
4. **Seamless integration** with PyTorch data loading

Key classes and modules:
- `lightly.transforms.SimCLRTransform`, `DINOTransform`, `MAETransform`, etc.
- `lightly.transforms.MultiViewTransform`
- `lightly.transforms.utils.IMAGENET_NORMALIZE`
- `lightly.data.LightlyDataset` (applies transforms automatically)

Sources: [lightly/transforms/](), [docs/source/getting_started/advanced.rst:8-162](), [README.md:125-189]()

---

# Page: Data Handling

# Data Handling

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/source/getting_started/advanced.rst](docs/source/getting_started/advanced.rst)
- [docs/source/getting_started/command_line_tool.rst](docs/source/getting_started/command_line_tool.rst)
- [docs/source/getting_started/images/lightly_overview.png](docs/source/getting_started/images/lightly_overview.png)
- [docs/source/getting_started/install.rst](docs/source/getting_started/install.rst)
- [docs/source/getting_started/lightly_at_a_glance.rst](docs/source/getting_started/lightly_at_a_glance.rst)
- [docs/source/getting_started/main_concepts.rst](docs/source/getting_started/main_concepts.rst)
- [docs/source/index.rst](docs/source/index.rst)
- [docs/source/lightly.models.utils.rst](docs/source/lightly.models.utils.rst)
- [lightly/data/_helpers.py](lightly/data/_helpers.py)
- [lightly/data/_image.py](lightly/data/_image.py)
- [lightly/data/_video.py](lightly/data/_video.py)
- [lightly/data/dataset.py](lightly/data/dataset.py)
- [lightly/data/lightly_subset.py](lightly/data/lightly_subset.py)
- [lightly/data/multi_view_collate.py](lightly/data/multi_view_collate.py)
- [tests/data/test_LightlyDataset.py](tests/data/test_LightlyDataset.py)
- [tests/data/test_LightlySubset.py](tests/data/test_LightlySubset.py)
- [tests/data/test_VideoDataset.py](tests/data/test_VideoDataset.py)

</details>



This page documents the data handling infrastructure in the Lightly SSL framework. It covers the dataset classes used to load images and videos, the supported input formats, filtering mechanisms, and batch collation for multi-view self-supervised learning.

For information about data augmentation and transforms, see [Transforms and Augmentations](#2.4). For dataset management via the Lightly Platform, see [Dataset and Tag Management](#6.3).

## Overview

The data handling layer provides a unified interface for working with different data sources in self-supervised learning workflows. The core abstraction is `LightlyDataset`, which wraps various underlying dataset types and provides consistent access to samples in the format `(sample, target, filename)`.

**Key Features:**
- Automatic detection of data type (images vs videos)
- Support for flat directories and nested folder structures
- Integration with torchvision datasets
- Video frame extraction without pre-processing
- Filename-based dataset filtering via `LightlySubset`
- Multi-view collation for batch preparation

**Sources:** [lightly/data/dataset.py:19-71](), [docs/source/getting_started/main_concepts.rst:19-26]()

## Dataset Classes

### LightlyDataset

`LightlyDataset` is the primary class for loading data in Lightly. It automatically detects the data format and delegates to the appropriate underlying implementation.

```mermaid
graph TB
    LD["LightlyDataset"]
    VD["VideoDataset"]
    IF["ImageFolder<br/>(torchvision)"]
    DF["DatasetFolder"]
    TD["Torchvision Dataset"]
    
    LD -->|"videos in dir"| VD
    LD -->|"subdirs present"| IF
    LD -->|"flat image dir"| DF
    LD -->|"from_torch_dataset()"| TD
    
    VD -->|"returns"| Frame["(PIL Image, video_idx, filename)"]
    IF -->|"returns"| Folder["(PIL Image, class_idx, filename)"]
    DF -->|"returns"| Flat["(PIL Image, 0, filename)"]
    TD -->|"returns"| Torch["(PIL Image, target, filename)"]
```

**Sources:** [lightly/data/dataset.py:19-295](), [lightly/data/_helpers.py:93-151]()

#### Initialization

`LightlyDataset` can be initialized from a directory or from an existing PyTorch dataset:

| Initialization Method | Description | Returns |
|----------------------|-------------|---------|
| `LightlyDataset(input_dir)` | Loads from directory | Auto-detects format |
| `LightlyDataset.from_torch_dataset(dataset)` | Wraps PyTorch dataset | Adds filename tracking |

The class uses `_load_dataset_from_folder()` to determine the appropriate underlying dataset type:

1. Check if directory contains videos (`.mp4`, `.mov`, `.avi`, etc.) → `VideoDataset`
2. Check if directory contains subdirectories → `ImageFolder` 
3. Otherwise → `DatasetFolder` (flat image directory)

**Sources:** [lightly/data/dataset.py:73-111](), [lightly/data/dataset.py:112-151](), [lightly/data/_helpers.py:93-151]()

#### Core Methods

```mermaid
classDiagram
    class LightlyDataset {
        +dataset: VisionDataset
        +input_dir: str
        +index_to_filename: Callable
        +__getitem__(index) (sample, target, filename)
        +__len__() int
        +get_filenames() List[str]
        +dump(output_dir, filenames, format)
        +get_filepath_from_filename(filename, image) str
        +transform: Compose
    }
```

| Method | Purpose |
|--------|---------|
| `__getitem__(index)` | Returns `(sample, target, filename)` tuple |
| `get_filenames()` | Returns list of all filenames in dataset |
| `dump(output_dir, filenames, format)` | Saves subset of images to disk |
| `get_filepath_from_filename(filename, image)` | Resolves full path for a filename |

**Sources:** [lightly/data/dataset.py:153-294]()

### VideoDataset

`VideoDataset` enables efficient random access to video frames without extracting them beforehand. It uses `VideoLoader` for frame reading and supports both PyAV and torchvision video backends.

```mermaid
graph TB
    subgraph "Video Loading Architecture"
        VD["VideoDataset"]
        VL["VideoLoader<br/>(thread-local)"]
        Backend{Backend}
        VR["VideoReader<br/>(video_reader)"]
        PyAV["PyAV"]
        
        VD -->|"_get_video_loader()"| VL
        VL --> Backend
        Backend -->|"if available"| VR
        Backend -->|"fallback"| PyAV
    end
    
    subgraph "Metadata"
        VD -->|"stores"| Timestamps["video_timestamps<br/>(per video)"]
        VD -->|"stores"| Offsets["offsets<br/>(frame indices)"]
        VD -->|"stores"| Videos["videos<br/>(file paths)"]
    end
```

**Sources:** [lightly/data/_video.py:307-604](), [lightly/data/_video.py:89-305]()

#### Frame Access

Frames are accessed by global index, which is mapped to `(video_index, frame_index_within_video)`:

```mermaid
sequenceDiagram
    participant User
    participant VD as VideoDataset
    participant VL as VideoLoader
    
    User->>VD: __getitem__(index=25)
    VD->>VD: Find video_idx from offsets
    VD->>VD: Calculate frame timestamp
    VD->>VL: read_frame(timestamp)
    VL->>VL: Seek to timestamp
    VL->>VL: Read frame data
    VL-->>VD: PIL Image
    VD-->>User: (image, video_idx, filename)
```

The filename for video frames is constructed as: `{video_name}-{frame_number:0{padding}}-{video_format}.png`

**Sources:** [lightly/data/_video.py:397-469](), [lightly/data/_video.py:479-526](), [lightly/data/_video.py:570-578]()

#### Non-Increasing Timestamps

`VideoDataset` detects frames with non-increasing timestamps (which can cause wrong frames to be loaded) and raises `NonIncreasingTimestampError` by default. This can be disabled:

```python
dataset.exception_on_non_increasing_timestamp = False
```

**Sources:** [lightly/data/_video.py:324-327](), [lightly/data/_video.py:446-456](), [lightly/data/_video.py:709-734]()

#### Multi-threading and Multi-processing

`VideoLoader` is thread-safe (inherits from `threading.local`). `VideoDataset` tracks worker references to avoid sharing `VideoLoader` instances between DataLoader workers, which is necessary for the `video_reader` backend.

**Sources:** [lightly/data/_video.py:66-86](), [lightly/data/_video.py:580-603]()

### DatasetFolder

`DatasetFolder` handles flat image directories (no subdirectories). All images are assigned label `0` since they're in the same directory.

**Sources:** [lightly/data/_image.py:16-108](), [lightly/data/_image.py:110-159]()

### LightlySubset

`LightlySubset` creates a filtered view of a `LightlyDataset` based on a list of filenames. It's used for active learning and selection workflows.

```mermaid
graph LR
    BD["Base Dataset<br/>(1000 images)"]
    LS["LightlySubset<br/>(200 filenames)"]
    Mapping["Index Mapping<br/>[subset_idx → base_idx]"]
    
    BD --> LS
    LS --> Mapping
    Mapping -->|"__getitem__(50)"| BD
```

The subset maintains a mapping from subset indices to base dataset indices, computed during initialization.

**Sources:** [lightly/data/lightly_subset.py:6-97]()

#### Usage Pattern

```python
base_dataset = LightlyDataset(input_dir='data/')
selected_filenames = ['img_001.jpg', 'img_005.jpg', 'img_042.jpg']
subset = LightlySubset(
    base_dataset=base_dataset,
    filenames_subset=selected_filenames
)
```

**Sources:** [lightly/data/lightly_subset.py:7-27](), [tests/data/test_LightlySubset.py:28-39]()

## Data Sources and Formats

### Supported Input Formats

```mermaid
graph TB
    subgraph "Image Formats"
        IMG["Image Files"]
        IEXT[".jpg, .jpeg, .png,<br/>.ppm, .bmp, .pgm,<br/>.tif, .tiff, .webp"]
        IMG --> IEXT
    end
    
    subgraph "Video Formats"
        VID["Video Files"]
        VEXT[".mp4, .mov, .avi,<br/>.mpg, .hevc, .m4v,<br/>.webm, .mpeg"]
        VID --> VEXT
    end
    
    subgraph "Directory Structures"
        FLAT["Flat Directory<br/>data/<br/>  img1.jpg<br/>  img2.jpg"]
        NESTED["Nested Folders<br/>data/<br/>  class1/img1.jpg<br/>  class2/img2.jpg"]
        VIDEO["Video Directory<br/>data/<br/>  video1.mp4<br/>  video2.mp4"]
    end
    
    IMG --> FLAT
    IMG --> NESTED
    VID --> VIDEO
```

**Supported Extensions:**

| Category | Extensions |
|----------|-----------|
| Images | `.jpg`, `.jpeg`, `.png`, `.ppm`, `.bmp`, `.pgm`, `.tif`, `.tiff`, `.webp` |
| Videos | `.mp4`, `.mov`, `.avi`, `.mpg`, `.hevc`, `.m4v`, `.webm`, `.mpeg` |

**Sources:** [lightly/data/_helpers.py:23-35]()

### Directory Detection Logic

The framework uses these helper functions to determine data type:

```mermaid
flowchart TD
    Start["_load_dataset_from_folder()"]
    CheckVideos{"_contains_videos()"}
    CheckSubdirs{"_contains_subdirs()"}
    
    Start --> CheckVideos
    CheckVideos -->|Yes| VD["Return VideoDataset"]
    CheckVideos -->|No| CheckSubdirs
    CheckSubdirs -->|Yes| IF["Return ImageFolder"]
    CheckSubdirs -->|No| DF["Return DatasetFolder"]
    
    VD --> Check{VideoDataset<br/>available?}
    Check -->|No| Error["Raise ValueError:<br/>Install PyAV"]
    Check -->|Yes| Done["Dataset Created"]
    IF --> Done
    DF --> Done
```

**Sources:** [lightly/data/_helpers.py:38-91](), [lightly/data/_helpers.py:93-151]()

### Torchvision Integration

Any torchvision dataset can be wrapped using `from_torch_dataset()`:

```python
import torchvision
from lightly.data import LightlyDataset

cifar10 = torchvision.datasets.CIFAR10(root='./')
dataset = LightlyDataset.from_torch_dataset(cifar10)
```

This adds filename tracking to the underlying dataset.

**Sources:** [lightly/data/dataset.py:112-151](), [tests/data/test_LightlyDataset.py:165-175]()

## Data Collation

### MultiViewCollate

Self-supervised learning methods create multiple augmented views of each image. `MultiViewCollate` reorganizes batch data from per-image views to per-view batches.

```mermaid
graph TB
    subgraph "Input Batch Structure"
        I1["Image 0<br/>[view0, view1]"]
        I2["Image 1<br/>[view0, view1]"]
        I3["Image B<br/>[view0, view1]"]
    end
    
    subgraph "MultiViewCollate Transformation"
        MVC["MultiViewCollate"]
    end
    
    subgraph "Output Structure"
        V0["View 0 Batch<br/>Tensor([img0_v0,<br/>img1_v0,<br/>imgB_v0])"]
        V1["View 1 Batch<br/>Tensor([img0_v1,<br/>img1_v1,<br/>imgB_v1])"]
        Labels["Labels<br/>[label0, label1, labelB]"]
        Fnames["Filenames<br/>[fname0, fname1, fnameB]"]
    end
    
    I1 --> MVC
    I2 --> MVC
    I3 --> MVC
    
    MVC --> V0
    MVC --> V1
    MVC --> Labels
    MVC --> Fnames
```

**Input Format:**
```python
[
    ([img_0_view_0, ..., img_0_view_N], label_0, filename_0),
    ([img_1_view_0, ..., img_1_view_N], label_1, filename_1),
    ...
    ([img_B_view_0, ..., img_B_view_N], label_B, filename_B),
]
```

**Output Format:**
```python
(
    [
        Tensor([img_0_view_0, ..., img_B_view_0]),  # view 0
        ...
        Tensor([img_0_view_N, ..., img_B_view_N]),  # view N
    ],
    torch.tensor([label_0, ..., label_B], dtype=torch.long),
    [filename_0, ..., filename_B],
)
```

**Sources:** [lightly/data/multi_view_collate.py:8-86]()

#### Usage with DataLoader

```python
from torch.utils.data import DataLoader
from lightly.data import LightlyDataset, MultiViewCollate
from lightly.transforms import SimCLRTransform

transform = SimCLRTransform()
dataset = LightlyDataset(input_dir='data/', transform=transform)
dataloader = DataLoader(
    dataset,
    batch_size=128,
    collate_fn=MultiViewCollate()
)

for views, targets, filenames in dataloader:
    view0, view1 = views  # Each is a tensor of shape (batch_size, C, H, W)
```

**Sources:** [lightly/data/multi_view_collate.py:16-21](), [docs/source/getting_started/lightly_at_a_glance.rst:36-50]()

## Data Flow Pipeline

```mermaid
flowchart LR
    subgraph "Data Sources"
        FS["Local Filesystem"]
        Cloud["Cloud Storage<br/>(via Platform API)"]
        TV["Torchvision<br/>Datasets"]
    end
    
    subgraph "Dataset Layer"
        LD["LightlyDataset"]
        VD["VideoDataset"]
        Sub["LightlySubset"]
    end
    
    subgraph "Transformation"
        Trans["Transform Pipeline<br/>(Multi-view generation)"]
    end
    
    subgraph "Batching"
        Collate["MultiViewCollate"]
    end
    
    subgraph "Training"
        DL["DataLoader"]
        Model["SSL Model"]
    end
    
    FS --> LD
    FS --> VD
    Cloud --> LD
    TV --> LD
    
    LD --> Sub
    VD --> Sub
    
    LD --> Trans
    VD --> Trans
    Sub --> Trans
    
    Trans --> Collate
    Collate --> DL
    DL --> Model
```

**Typical Workflow:**

1. **Initialization:** Create `LightlyDataset` from directory or torchvision dataset
2. **Filtering (Optional):** Wrap in `LightlySubset` to select specific samples
3. **Transformation:** Apply multi-view transforms (e.g., `SimCLRTransform`)
4. **Collation:** Use `MultiViewCollate` in DataLoader to organize views
5. **Training:** Iterate over batches in SSL training loop

**Sources:** [docs/source/getting_started/lightly_at_a_glance.rst:16-60](), [lightly/data/dataset.py:19-71]()

## File Operations

### Dumping Datasets

`LightlyDataset.dump()` saves images to disk, either copying from source or re-encoding:

| Source Dataset Type | Behavior |
|--------------------|----------|
| `ImageFolder` / `DatasetFolder` | Direct file copy (preserves format) |
| `VideoDataset` / Torchvision datasets | Load and save (default format: PNG) |

```python
dataset.dump(
    output_dir='selected_images/',
    filenames=['img_001.jpg', 'img_042.jpg'],
    format='jpg'  # Optional: specify output format
)
```

**Sources:** [lightly/data/dataset.py:188-239](), [lightly/data/dataset.py:342-360]()

### Filename Handling

The framework maintains consistent filename conventions:

- **Images:** Relative path from dataset root (e.g., `subdir/img.jpg`)
- **Videos:** `{video_name}-{frame_number:0{padding}}-{video_format}.png`

For temporary operations (e.g., uploading from VideoDataset), `get_filepath_from_filename()` creates temporary files as needed.

**Sources:** [lightly/data/dataset.py:241-284](), [lightly/data/dataset.py:297-313](), [lightly/data/_video.py:479-578]()

## Configuration and Dependencies

### Video Support

Video functionality requires PyAV:

```bash
pip install "lightly[video]"
```

If videos are present but PyAV is not installed, a `ValueError` is raised with installation instructions.

**Sources:** [lightly/data/_helpers.py:14-20](), [lightly/data/_helpers.py:122-130](), [docs/source/getting_started/install.rst:28-33]()

### Video Backends

Two backends are supported:

| Backend | Description | Availability |
|---------|-------------|------------|
| `video_reader` | Faster sequential reads | Requires torchvision with video support |
| `pyav` | Fallback, works with random access | Requires PyAV installation |

The backend is automatically selected based on availability, with `video_reader` preferred if available.

**Sources:** [lightly/data/_video.py:28-29](), [lightly/data/_video.py:133-152]()

## Common Usage Patterns

### Basic Image Dataset

```python
from lightly.data import LightlyDataset

dataset = LightlyDataset(input_dir='my_images/')
print(f"Dataset size: {len(dataset)}")
print(f"Filenames: {dataset.get_filenames()}")

sample, target, fname = dataset[0]
```

**Sources:** [lightly/data/dataset.py:50-70]()

### Video Dataset with Frame Counting Workers

```python
dataset = LightlyDataset(
    input_dir='my_videos/',
    num_workers_video_frame_counting=4  # Parallel frame counting
)
```

**Sources:** [tests/data/test_LightlyDataset.py:149-160]()

### Filtered Dataset

```python
base_dataset = LightlyDataset(input_dir='data/')
selected_files = ['img_001.jpg', 'img_050.jpg']
subset = LightlySubset(base_dataset, selected_files)
```

**Sources:** [lightly/data/lightly_subset.py:7-27]()

### With Transforms and DataLoader

```python
from torch.utils.data import DataLoader
from lightly.transforms import SimCLRTransform
from lightly.data import LightlyDataset, MultiViewCollate

transform = SimCLRTransform(input_size=224)
dataset = LightlyDataset('data/', transform=transform)

dataloader = DataLoader(
    dataset,
    batch_size=128,
    shuffle=True,
    collate_fn=MultiViewCollate(),
    num_workers=8
)

for views, targets, filenames in dataloader:
    # views is a list of 2 tensors (for SimCLR)
    view0, view1 = views
```

**Sources:** [docs/source/getting_started/lightly_at_a_glance.rst:23-50]()

---

# Page: Datasets

# Datasets

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [lightly/data/_helpers.py](lightly/data/_helpers.py)
- [lightly/data/_image.py](lightly/data/_image.py)
- [lightly/data/_video.py](lightly/data/_video.py)
- [lightly/data/dataset.py](lightly/data/dataset.py)
- [lightly/data/lightly_subset.py](lightly/data/lightly_subset.py)
- [lightly/data/multi_view_collate.py](lightly/data/multi_view_collate.py)
- [tests/data/test_LightlyDataset.py](tests/data/test_LightlyDataset.py)
- [tests/data/test_LightlySubset.py](tests/data/test_LightlySubset.py)
- [tests/data/test_VideoDataset.py](tests/data/test_VideoDataset.py)

</details>



This page documents the dataset classes used in Lightly for loading and managing image and video data. For information about data collation and batching for SSL training, see [Data Collation and Batching](#3.2).

## Overview

Lightly provides three primary dataset classes for data loading:

- **`LightlyDataset`**: Main interface that wraps image or video datasets and provides a uniform interface returning `(sample, target, filename)` tuples
- **`VideoDataset`**: Specialized dataset for extracting frames from video files without pre-extraction
- **`LightlySubset`**: Filtered view of a dataset based on a list of filenames

The framework automatically selects the appropriate underlying dataset implementation based on directory contents.

---

## Dataset Type Selection

```mermaid
flowchart TB
    INPUT["input_dir"]
    CHECK_EXISTS{"Directory<br/>exists?"}
    CHECK_VIDEOS{"Contains<br/>videos?"}
    CHECK_SUBDIRS{"Contains<br/>subdirectories?"}
    
    VIDEO_DS["VideoDataset"]
    IMAGE_FOLDER["torchvision.datasets.ImageFolder"]
    DATASET_FOLDER["DatasetFolder"]
    ERROR["ValueError"]
    
    INPUT --> CHECK_EXISTS
    CHECK_EXISTS -->|No| ERROR
    CHECK_EXISTS -->|Yes| CHECK_VIDEOS
    CHECK_VIDEOS -->|Yes| VIDEO_DS
    CHECK_VIDEOS -->|No| CHECK_SUBDIRS
    CHECK_SUBDIRS -->|Yes| IMAGE_FOLDER
    CHECK_SUBDIRS -->|No| DATASET_FOLDER
    
    VIDEO_DS --> LIGHTLY["LightlyDataset<br/>wrapper"]
    IMAGE_FOLDER --> LIGHTLY
    DATASET_FOLDER --> LIGHTLY
```

**Dataset Selection Logic**

The `_load_dataset_from_folder()` function implements automatic dataset type detection:

Sources: [lightly/data/_helpers.py:93-151]()

---

## LightlyDataset

`LightlyDataset` is the primary dataset class that provides a uniform interface for all data types in Lightly. It wraps underlying PyTorch datasets and ensures all items are returned as `(sample, target, filename)` tuples.

### Creation from Directory

```python
from lightly.data import LightlyDataset

# Images in flat directory
dataset = LightlyDataset(input_dir='path/to/images/')

# Images in subdirectories (ImageNet-style)
dataset = LightlyDataset(input_dir='path/to/imagenet/')

# Videos
dataset = LightlyDataset(input_dir='path/to/videos/')
```

**Supported Directory Structures:**

| Structure | Example | Underlying Dataset |
|-----------|---------|-------------------|
| Flat directory | `images/img1.jpg, img2.jpg, ...` | `DatasetFolder` |
| Subdirectories | `imagenet/class1/img1.jpg, class2/img2.jpg, ...` | `torchvision.datasets.ImageFolder` |
| Videos | `videos/video1.mp4, video2.mp4, ...` | `VideoDataset` |

### Creation from PyTorch Dataset

```python
import torchvision.datasets as datasets
from lightly.data import LightlyDataset

# Load CIFAR-10 from torchvision
cifar10 = datasets.CIFAR10(root='./data', download=True)
dataset = LightlyDataset.from_torch_dataset(cifar10)
```

Sources: [lightly/data/dataset.py:112-151]()

### Constructor Parameters

```python
LightlyDataset(
    input_dir: Union[str, None],
    transform: transforms.Compose = None,
    index_to_filename: Callable = None,
    filenames: List[str] = None,
    tqdm_args: Dict[str, Any] = None,
    num_workers_video_frame_counting: int = 0,
)
```

| Parameter | Description |
|-----------|-------------|
| `input_dir` | Path to directory containing images or videos. Can be `None` when using `from_torch_dataset()`. |
| `transform` | Torchvision transforms to apply to samples. |
| `index_to_filename` | Custom function mapping dataset index to filename. |
| `filenames` | Optional list to filter dataset to specific filenames. |
| `tqdm_args` | Arguments for progress bar during video frame counting. |
| `num_workers_video_frame_counting` | Number of workers for parallel video timestamp extraction. |

Sources: [lightly/data/dataset.py:73-111]()

### Key Methods

**`__getitem__(index)`**: Returns `(sample, target, filename)` tuple

```python
sample, target, fname = dataset[0]
# sample: PIL Image or Tensor (if transform applied)
# target: int (class label or video index)
# fname: str (relative path to file)
```

**`get_filenames()`**: Returns list of all filenames in dataset

```python
filenames = dataset.get_filenames()
# ['img1.jpg', 'img2.jpg', 'subdir/img3.jpg', ...]
```

**`dump(output_dir, filenames=None, format=None)`**: Saves images to output directory

```python
# Save all images
dataset.dump('output/')

# Save specific images
dataset.dump('output/', filenames=['img1.jpg', 'img2.jpg'])

# Save with specific format
dataset.dump('output/', format='png')
```

For `VideoDataset` and PyTorch datasets, images are loaded and saved (not copied). For `ImageFolder` and `DatasetFolder`, images are copied directly.

**`get_filepath_from_filename(filename, image=None)`**: Gets or creates filepath for a filename

For regular image datasets, returns existing filepath. For video datasets and PyTorch datasets, creates temporary file if needed.

Sources: [lightly/data/dataset.py:153-294]()

### Filename Handling

```mermaid
flowchart LR
    INDEX["Dataset Index"]
    FUNC["index_to_filename<br/>function"]
    DATASET_TYPE{"Dataset Type"}
    
    INDEX --> FUNC
    FUNC --> DATASET_TYPE
    
    DATASET_TYPE -->|ImageFolder| IMAGE_FOLDER_PATH["Path relative<br/>to root"]
    DATASET_TYPE -->|DatasetFolder| DATA_FOLDER_PATH["Path relative<br/>to root"]
    DATASET_TYPE -->|VideoDataset| VIDEO_FNAME["Generated from<br/>video filename<br/>+ frame number"]
    DATASET_TYPE -->|Other| FALLBACK["str(index)"]
    
    IMAGE_FOLDER_PATH --> FNAME["Filename"]
    DATA_FOLDER_PATH --> FNAME
    VIDEO_FNAME --> FNAME
    FALLBACK --> FNAME
```

The `index_to_filename` function maps dataset indices to filenames. Default implementations:

- **ImageFolder**: `relative_path(dataset.imgs[index][0], dataset.root)`
- **DatasetFolder**: `relative_path(dataset.samples[index][0], dataset.root)`
- **VideoDataset**: `video_name-frame_number-video_format.png`
- **Other**: `str(index)` (fallback)

Sources: [lightly/data/dataset.py:297-312]()

---

## VideoDataset

`VideoDataset` enables efficient random access to video frames without extracting all frames to disk. It uses `VideoLoader` for frame reading and supports both `pyav` and `video_reader` backends.

### Architecture

```mermaid
flowchart TB
    subgraph "VideoDataset"
        VD["VideoDataset"]
        VIDEOS["videos: List[str]"]
        TIMESTAMPS["video_timestamps:<br/>List[List[float]]"]
        OFFSETS["offsets: List[int]"]
        VL_CACHE["_video_loader:<br/>VideoLoader | None"]
        VL_INDEX["_video_index:<br/>int | None"]
    end
    
    subgraph "VideoLoader (thread-local)"
        VL["VideoLoader"]
        READER["reader:<br/>VideoReader | None"]
        PATH["path: str"]
        TS_LIST["timestamps:<br/>List[float]"]
        CURRENT["current_index:<br/>int | None"]
    end
    
    subgraph "Backends"
        READER_BACKEND["video_reader<br/>(torchvision)"]
        PYAV_BACKEND["pyav<br/>(torchvision.io)"]
    end
    
    VD --> VIDEOS
    VD --> TIMESTAMPS
    VD --> OFFSETS
    VD --> VL_CACHE
    VL_CACHE --> VL
    
    VL --> READER
    VL --> PATH
    VL --> TS_LIST
    VL --> CURRENT
    
    READER -->|if available| READER_BACKEND
    READER -->|fallback| PYAV_BACKEND
```

### VideoLoader

`VideoLoader` is a thread-local class that efficiently reads frames from video files. It automatically detects sequential frame access and optimizes reading.

**Key Features:**
- Thread-safe through `threading.local` inheritance
- Optimized sequential reading with `video_reader` backend
- Automatic fallback to `pyav` backend
- Frame seeking with timestamp validation

Sources: [lightly/data/_video.py:89-305]()

### Constructor Parameters

```python
VideoDataset(
    root: str,
    extensions: Tuple[str, ...] = None,
    transform: Callable = None,
    target_transform: Callable = None,
    is_valid_file: Callable = None,
    exception_on_non_increasing_timestamp: bool = True,
    tqdm_args: Dict[str, Any] = None,
    num_workers: int = 0,
)
```

| Parameter | Description |
|-----------|-------------|
| `root` | Root directory containing video files. |
| `extensions` | Tuple of valid video extensions (e.g., `('.mp4', '.avi')`). |
| `transform` | Transform to apply to frames (PIL Images). |
| `exception_on_non_increasing_timestamp` | Raise error if timestamps are non-increasing. |
| `tqdm_args` | Arguments for progress bar during initialization. |
| `num_workers` | Workers for parallel timestamp extraction during initialization. |

Sources: [lightly/data/_video.py:331-395]()

### Video Frame Extraction

During initialization, `VideoDataset` reads timestamps from all videos using `_make_dataset()`:

```mermaid
flowchart LR
    VIDEOS["Video Files"]
    TIMESTAMP_DS["_TimestampFpsFromVideosDataset"]
    DATALOADER["torch.utils.data.DataLoader"]
    TIMESTAMPS["video_timestamps:<br/>List[List[Fraction]]"]
    OFFSETS["offsets:<br/>List[int]"]
    
    VIDEOS --> TIMESTAMP_DS
    TIMESTAMP_DS --> DATALOADER
    DATALOADER -->|parallel extraction| TIMESTAMPS
    TIMESTAMPS --> OFFSETS
```

The offsets list enables O(log n) video lookup: `offsets[i]` indicates the global index of the first frame in video `i`.

Sources: [lightly/data/_video.py:620-706]()

### Frame Filename Generation

Video frames have generated filenames following this pattern:

```
{video_name}-{frame_number:0{padding}}-{video_format}.png
```

Example: For frame 153 of `my_video.mp4`:
```
my_video-153-mp4.png
```

Sources: [lightly/data/_video.py:479-578]()

### Thread Safety and Multi-Processing

The `VideoDataset` is designed to be safe for use with PyTorch DataLoader:

- **Single-threaded**: Works with both backends
- **Multi-processing**: Each worker gets its own `VideoLoader` instance
- **Multi-threading**: Use with caution - `pyav` backend is single-threaded

Worker detection prevents `VideoLoader` sharing between DataLoader workers using weak references to track worker identity.

Sources: [lightly/data/_video.py:66-87](), [lightly/data/_video.py:580-603]()

### Exception Handling

**Custom Exceptions:**

| Exception | Raised When |
|-----------|-------------|
| `EmptyVideoError` | Video has no frames |
| `FrameShapeError` | Loaded frame has unexpected shape |
| `NonIncreasingTimestampError` | Frame timestamp ≤ previous timestamps |
| `UnseekableTimestampError` | Cannot seek to requested timestamp |

**Non-Increasing Timestamps:**

Videos with non-increasing frame timestamps can cause the wrong frame to be loaded. By default, `VideoDataset` raises `NonIncreasingTimestampError` for such frames. Disable with:

```python
dataset.exception_on_non_increasing_timestamp = False
```

Sources: [lightly/data/_video.py:32-63](), [lightly/data/_video.py:446-456]()

---

## LightlySubset

`LightlySubset` creates a filtered view of a `LightlyDataset` based on a list of filenames. This is useful for working with dataset selections from the Lightly Platform or custom filtering.

### Architecture

```mermaid
flowchart LR
    BASE["base_dataset:<br/>LightlyDataset"]
    FILENAMES["filenames_subset:<br/>List[str]"]
    MAPPING["mapping_subset_index<br/>_to_baseset_index:<br/>List[int]"]
    
    SUBSET["LightlySubset"]
    
    BASE --> SUBSET
    FILENAMES --> SUBSET
    SUBSET --> MAPPING
    
    GETITEM["__getitem__(subset_idx)"]
    MAPPING --> GETITEM
    GETITEM --> BASE
```

### Usage

```python
from lightly.data import LightlyDataset, LightlySubset

# Create base dataset
base_dataset = LightlyDataset(input_dir='path/to/data/')

# Get all filenames
all_filenames = base_dataset.get_filenames()

# Select subset (e.g., first half)
subset_filenames = all_filenames[:len(all_filenames)//2]

# Create filtered view
subset = LightlySubset(
    base_dataset=base_dataset,
    filenames_subset=subset_filenames
)

# Access works as normal
sample, target, fname = subset[0]
len(subset)  # Length is len(subset_filenames)
```

### Implementation Details

During initialization, `LightlySubset` builds a mapping from subset indices to base dataset indices:

1. Creates a `filename -> base_index` dictionary for the base dataset
2. Maps each filename in `filenames_subset` to its base index
3. Stores this mapping for O(1) index translation

Index translation: `subset[i]` → `base_dataset[mapping[i]]`

Sources: [lightly/data/lightly_subset.py:1-97]()

### Methods

**`__getitem__(index_subset)`**: Access sample by subset index

```python
sample, target, fname = subset[10]  # 10th item in subset
```

**`__len__()`**: Returns number of samples in subset

```python
length = len(subset)
```

**`get_filenames()`**: Returns list of filenames in subset

```python
filenames = subset.get_filenames()  # Returns filenames_subset
```

**Properties:**
- `input_dir`: Returns base dataset's input directory
- `dataset`: Returns base dataset's underlying dataset

Sources: [lightly/data/lightly_subset.py:29-96]()

---

## DatasetFolder

`DatasetFolder` is a simple dataset for flat directories (no subdirectories) containing images. It's similar to `torchvision.datasets.ImageFolder` but for non-hierarchical folder structures.

### Key Characteristics

- All images in the root directory (no subdirectories)
- All samples assigned target label `0`
- Samples sorted alphabetically by path
- Supports custom image loaders and file validation

### Constructor

```python
DatasetFolder(
    root: str,
    loader: Callable = default_loader,
    extensions: Tuple[str, ...] = None,
    transform: Callable = None,
    target_transform: Callable = None,
    is_valid_file: Callable = None,
)
```

Sources: [lightly/data/_image.py:16-108]()

---

## Supported File Formats

### Image Extensions

```python
IMG_EXTENSIONS = (
    '.jpg', '.jpeg', '.png', '.ppm', '.bmp', 
    '.pgm', '.tif', '.tiff', '.webp'
)
```

### Video Extensions

```python
VIDEO_EXTENSIONS = (
    '.mp4', '.mov', '.avi', '.mpg', '.hevc', 
    '.m4v', '.webm', '.mpeg'
)
```

Video support requires `pyav` and/or torchvision video backend to be installed.

Sources: [lightly/data/_helpers.py:23-35]()

---

## Usage Examples

### Basic Image Loading

```python
from lightly.data import LightlyDataset

# Load images from directory
dataset = LightlyDataset(input_dir='data/images/')

# Iterate over dataset
for sample, target, filename in dataset:
    print(f"Loaded {filename} with label {target}")
```

### Video Loading with Progress Bar

```python
dataset = LightlyDataset(
    input_dir='data/videos/',
    tqdm_args={'desc': 'Loading videos'},
    num_workers_video_frame_counting=4
)
```

### Creating Subset from API Selection

```python
from lightly.data import LightlyDataset, LightlySubset

# Load full dataset
full_dataset = LightlyDataset(input_dir='data/')

# Get selected filenames from Lightly Platform
# (e.g., through ApiWorkflowClient)
selected_filenames = ['img1.jpg', 'img5.jpg', 'img10.jpg']

# Create subset
subset = LightlySubset(
    base_dataset=full_dataset,
    filenames_subset=selected_filenames
)

# Train on subset
for sample, target, fname in subset:
    # Training code
    pass
```

### From PyTorch Dataset with Transforms

```python
import torchvision
from lightly.data import LightlyDataset
from lightly.transforms import SimCLRTransform

# Load CIFAR-10
cifar = torchvision.datasets.CIFAR10(
    root='./data', 
    train=True, 
    download=True
)

# Wrap with LightlyDataset and add SSL transforms
transform = SimCLRTransform()
dataset = LightlyDataset.from_torch_dataset(
    cifar,
    transform=transform
)
```

### Dumping Subset to Disk

```python
# Create subset
subset = LightlySubset(base_dataset, selected_filenames)

# Save images to output directory
subset.dump(
    output_dir='output/selected/',
    format='png'
)
```

Sources: [tests/data/test_LightlyDataset.py:85-329](), [tests/data/test_LightlySubset.py:1-86]()

---

# Page: Data Collation and Batching

# Data Collation and Batching

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [docs/source/getting_started/benchmarks.rst](docs/source/getting_started/benchmarks.rst)
- [docs/source/getting_started/benchmarks/cifar10_benchmark.py](docs/source/getting_started/benchmarks/cifar10_benchmark.py)
- [docs/source/getting_started/benchmarks/imagenet100_benchmark.py](docs/source/getting_started/benchmarks/imagenet100_benchmark.py)
- [docs/source/getting_started/benchmarks/imagenette_benchmark.py](docs/source/getting_started/benchmarks/imagenette_benchmark.py)
- [lightly/data/_helpers.py](lightly/data/_helpers.py)
- [lightly/data/_image.py](lightly/data/_image.py)
- [lightly/data/_video.py](lightly/data/_video.py)
- [lightly/data/dataset.py](lightly/data/dataset.py)
- [lightly/data/lightly_subset.py](lightly/data/lightly_subset.py)
- [lightly/data/multi_view_collate.py](lightly/data/multi_view_collate.py)
- [tests/data/test_LightlyDataset.py](tests/data/test_LightlyDataset.py)
- [tests/data/test_LightlySubset.py](tests/data/test_LightlySubset.py)
- [tests/data/test_VideoDataset.py](tests/data/test_VideoDataset.py)

</details>



This page describes how Lightly handles data collation and batching for self-supervised learning. Specifically, it covers the `MultiViewCollate` class that prepares batches of multiple augmented views for contrastive and other SSL methods. For information about creating and loading datasets, see [Datasets](#3.1). For information about the transforms that generate multiple views, see [Transforms and Augmentations](#2.4).

## Purpose and Scope

In self-supervised learning, each image is typically transformed into multiple augmented views (e.g., two views for SimCLR, global and local views for DINO). These views must be properly collated into batches so that the training loop can process them efficiently. The collation step reorganizes data from a per-sample structure (multiple views per image) to a per-view structure (all images for each view grouped together).

This document covers:
- The `MultiViewCollate` class and its functionality
- Batch structure before and after collation
- Integration with PyTorch `DataLoader`
- Usage patterns in SSL training workflows

## Overview of Collation in SSL Training

The data flow from dataset to model involves several steps:

```mermaid
graph TB
    Dataset["LightlyDataset<br/>(lightly/data/dataset.py)"]
    Transform["Transform Pipeline<br/>(e.g., SimCLRTransform)"]
    Sample["Per-Sample Structure<br/>(views_list, label, filename)"]
    Collate["MultiViewCollate<br/>(lightly/data/multi_view_collate.py)"]
    Batch["Batched Structure<br/>(views, labels, filenames)"]
    Training["Training Loop<br/>Forward pass with views"]
    
    Dataset -->|"__getitem__(idx)"| Transform
    Transform -->|"returns"| Sample
    Sample -->|"N samples"| Collate
    Collate -->|"collate_fn in DataLoader"| Batch
    Batch -->|"unpacked in loop"| Training
    
    style Collate fill:#e1f5ff
    style Batch fill:#ffe1e1
```

**Sources:** [lightly/data/multi_view_collate.py:1-87](), [lightly/data/dataset.py:153-167]()

When a dataset with multi-view transforms is accessed, each sample returns:
- A list of view tensors (e.g., `[view0, view1]` for 2-view methods)
- A label (integer)
- A filename (string)

The `MultiViewCollate` class reorganizes a batch of these samples into a structure suitable for SSL training.

## MultiViewCollate Class

### Class Definition and Responsibility

The `MultiViewCollate` class is a collate function designed for use with PyTorch's `DataLoader`. It transforms a list of per-sample tuples into a per-view batch structure.

```mermaid
graph LR
    subgraph "Input: List of Samples"
        S0["Sample 0<br/>[view0, view1], label0, fname0"]
        S1["Sample 1<br/>[view0, view1], label1, fname1"]
        S2["Sample 2<br/>[view0, view1], label2, fname2"]
    end
    
    Collate["MultiViewCollate.__call__()"]
    
    subgraph "Output: Batched Views"
        V0["View 0 Batch<br/>Tensor([img0_v0, img1_v0, img2_v0])"]
        V1["View 1 Batch<br/>Tensor([img0_v1, img1_v1, img2_v1])"]
        Labels["Labels<br/>Tensor([label0, label1, label2])"]
        Files["Filenames<br/>[fname0, fname1, fname2]"]
    end
    
    S0 --> Collate
    S1 --> Collate
    S2 --> Collate
    
    Collate --> V0
    Collate --> V1
    Collate --> Labels
    Collate --> Files
    
    style Collate fill:#e1f5ff
```

**Sources:** [lightly/data/multi_view_collate.py:8-87]()

### Implementation Details

The core logic of `MultiViewCollate` is in its `__call__` method:

| Step | Operation | Code Location |
|------|-----------|---------------|
| 1. Initialize containers | Create empty lists for views, labels, and filenames | [lightly/data/multi_view_collate.py:70-77]() |
| 2. Iterate batch | Loop through each (views, label, filename) tuple | [lightly/data/multi_view_collate.py:78-82]() |
| 3. Group views | Collect all samples' view i into views[i] list | [lightly/data/multi_view_collate.py:79-80]() |
| 4. Concatenate | Stack views into tensors using `torch.cat` | [lightly/data/multi_view_collate.py:84]() |
| 5. Return tuple | Return (views, labels, filenames) | [lightly/data/multi_view_collate.py:86]() |

**Sources:** [lightly/data/multi_view_collate.py:23-86]()

The method handles edge cases such as empty batches by issuing a warning and returning empty structures [lightly/data/multi_view_collate.py:73-75]().

## Batch Structure

### Input Structure (Per-Sample)

Before collation, each sample from the dataset has this structure:

```
Sample i:
  - views: List[Tensor]  # e.g., [view0_tensor, view1_tensor]
  - label: int           # class label or video index
  - filename: str        # unique identifier
```

For a batch of size B with N views per sample, the input to `MultiViewCollate.__call__` is:

```
[
    (List[Tensor of shape (C, H, W)], int, str),  # Sample 0
    (List[Tensor of shape (C, H, W)], int, str),  # Sample 1
    ...
    (List[Tensor of shape (C, H, W)], int, str),  # Sample B-1
]
```

**Sources:** [lightly/data/multi_view_collate.py:24-42]()

### Output Structure (Per-View)

After collation, the structure is reorganized:

```
(
    [Tensor of shape (B, C, H, W),  # All samples, view 0
     Tensor of shape (B, C, H, W),  # All samples, view 1
     ...
     Tensor of shape (B, C, H, W)], # All samples, view N-1
    Tensor of shape (B,),           # All labels
    List[str]                       # All filenames
)
```

This structure allows SSL methods to easily access all samples for a specific view without additional indexing.

**Sources:** [lightly/data/multi_view_collate.py:45-65]()

## Integration with PyTorch DataLoader

### Basic Usage Pattern

The `MultiViewCollate` class is passed to PyTorch's `DataLoader` via the `collate_fn` parameter:

```mermaid
graph TB
    Dataset["LightlyDataset<br/>with transform"]
    DataLoader["torch.utils.data.DataLoader<br/>collate_fn=MultiViewCollate()"]
    Iterator["DataLoader iterator"]
    Loop["Training loop<br/>for views, labels, fnames in dataloader:"]
    
    Dataset -->|"dataset parameter"| DataLoader
    DataLoader -->|"iter()"| Iterator
    Iterator -->|"next()"| Loop
    
    style DataLoader fill:#e1f5ff
```

**Sources:** [docs/source/getting_started/benchmarks/cifar10_benchmark.py:263-269](), [docs/source/getting_started/benchmarks/imagenette_benchmark.py:296-302]()

### DataLoader Configuration

Typical DataLoader configuration for SSL training:

| Parameter | Typical Value | Purpose |
|-----------|---------------|---------|
| `dataset` | `LightlyDataset` with multi-view transform | Source of samples |
| `batch_size` | 128-512 | Number of images per batch |
| `shuffle` | `True` for training | Randomize sample order |
| `drop_last` | `True` for training | Ensure consistent batch sizes |
| `num_workers` | 4-12 | Parallel data loading |
| `collate_fn` | `MultiViewCollate()` (implicit) | Batch collation |

**Sources:** [docs/source/getting_started/benchmarks/cifar10_benchmark.py:263-269](), [docs/source/getting_started/benchmarks/imagenette_benchmark.py:296-302]()

Note: When using transforms that return multiple views (like `SimCLRTransform`, `DINOTransform`), the `MultiViewCollate` behavior is often the default or implicit behavior handled by the framework. Users typically don't need to explicitly instantiate it.

### Training Loop Pattern

In training loops, the collated batch is unpacked:

```mermaid
graph LR
    DataLoader["DataLoader yields batch"]
    Unpack["Unpack:<br/>(x0, x1), targets, filenames"]
    Forward["Model forward pass<br/>z0 = model(x0)<br/>z1 = model(x1)"]
    Loss["Loss computation<br/>loss = criterion(z0, z1)"]
    
    DataLoader --> Unpack
    Unpack --> Forward
    Forward --> Loss
    
    style Unpack fill:#e1f5ff
```

**Sources:** [docs/source/getting_started/benchmarks/cifar10_benchmark.py:374-380](), [README.md:182-189]()

Common unpacking patterns:

**Two-view methods (SimCLR, MoCo, BYOL):**
```python
for (x0, x1), targets, filenames in dataloader:
    z0 = model(x0)
    z1 = model(x1)
    loss = criterion(z0, z1)
```

**Multi-view methods (SwaV, DINO, FastSiam):**
```python
for views, targets, filenames in dataloader:
    # views is a list of tensors
    features = [model(view) for view in views]
    loss = compute_loss(features)
```

**Sources:** [docs/source/getting_started/benchmarks/cifar10_benchmark.py:374-380](), [docs/source/getting_started/benchmarks/imagenette_benchmark.py:462-474]()

## Method-Specific Batch Patterns

Different SSL methods use different numbers of views and may require different collation patterns:

```mermaid
graph TB
    subgraph "2-View Methods"
        SimCLR["SimCLR<br/>SimCLRTransform<br/>2 crops @ same size"]
        MoCo["MoCo<br/>SimCLRTransform<br/>2 crops @ same size"]
        BYOL["BYOL<br/>BYOLTransform<br/>2 crops @ different aug"]
    end
    
    subgraph "Multi-View Methods"
        DINO["DINO<br/>DINOTransform<br/>2 global + N local crops"]
        SwaV["SwaV<br/>SwaVTransform<br/>2 crops @ 224px + 6 @ 96px"]
        FastSiam["FastSiam<br/>FastSiamTransform<br/>Multiple crops"]
    end
    
    Collate["MultiViewCollate<br/>Handles any number of views"]
    
    SimCLR --> Collate
    MoCo --> Collate
    BYOL --> Collate
    DINO --> Collate
    SwaV --> Collate
    FastSiam --> Collate
    
    style Collate fill:#e1f5ff
```

**Sources:** [docs/source/getting_started/benchmarks/cifar10_benchmark.py:166-213](), [docs/source/getting_started/benchmarks/imagenette_benchmark.py:169-234]()

### View Count by Method

| Method | Transform | Number of Views | View Types |
|--------|-----------|-----------------|------------|
| SimCLR | `SimCLRTransform` | 2 | Two random crops with strong augmentation |
| MoCo | `SimCLRTransform` | 2 | Two random crops with strong augmentation |
| BYOL | `BYOLTransform` | 2 | View 1 (stronger) + View 2 (weaker) |
| SimSiam | `SimSiamTransform` | 2 | Two random crops with augmentation |
| DINO | `DINOTransform` | 2-10 | 2 global crops + N local crops (default N=8) |
| SwaV | `SwaVTransform` | 2-8 | 2 crops @ 224px + 6 crops @ 96px |
| FastSiam | `FastSiamTransform` | Variable | Multiple random crops |
| MAE | `MAETransform` | 1 | Single crop (masking done in model) |

**Sources:** [docs/source/getting_started/benchmarks/imagenette_benchmark.py:169-234](), [lightly/transforms/__init__.py]()

## Code Entity Reference

Key classes and their locations:

```mermaid
graph TB
    subgraph "lightly/data/"
        Dataset["dataset.py<br/>LightlyDataset"]
        Collate["multi_view_collate.py<br/>MultiViewCollate"]
        Subset["lightly_subset.py<br/>LightlySubset"]
    end
    
    subgraph "torch.utils.data"
        DataLoader["DataLoader<br/>collate_fn parameter"]
    end
    
    subgraph "lightly/transforms"
        SimCLR["SimCLRTransform"]
        DINO["DINOTransform"]
        BYOL["BYOLTransform"]
    end
    
    Dataset -->|"returns multi-view samples"| Collate
    Subset -->|"returns multi-view samples"| Collate
    Collate -->|"used as"| DataLoader
    SimCLR -->|"applied in"| Dataset
    DINO -->|"applied in"| Dataset
    BYOL -->|"applied in"| Dataset
    
    style Collate fill:#e1f5ff
    style DataLoader fill:#ffe1e1
```

**Sources:** [lightly/data/multi_view_collate.py:1-87](), [lightly/data/dataset.py:1-361](), [lightly/data/lightly_subset.py:1-97]()

### Key Methods

| Class | Method | Purpose | Location |
|-------|--------|---------|----------|
| `MultiViewCollate` | `__call__` | Collate batch of multi-view samples | [lightly/data/multi_view_collate.py:23-86]() |
| `LightlyDataset` | `__getitem__` | Return (sample, target, filename) | [lightly/data/dataset.py:153-167]() |
| `LightlySubset` | `__getitem__` | Return subset sample via base dataset | [lightly/data/lightly_subset.py:29-45]() |

**Sources:** [lightly/data/multi_view_collate.py:23-86](), [lightly/data/dataset.py:153-167](), [lightly/data/lightly_subset.py:29-45]()

## Performance Considerations

### Memory Efficiency

The collation process creates new tensors by concatenating view tensors along the batch dimension. For a batch of B images with N views:

- Input: B lists of N tensors, each of shape (C, H, W)
- Output: N tensors, each of shape (B, C, H, W)

Memory usage is O(B × N × C × H × W), which is the same before and after collation, but the reorganization enables efficient batch processing.

**Sources:** [lightly/data/multi_view_collate.py:78-84]()

### Multi-Worker Considerations

When using `num_workers > 0` in `DataLoader`, collation happens in the main process after workers fetch samples. This means:

1. Workers independently load and transform samples
2. Main process receives samples from workers
3. Main process calls collate function to create batch
4. Batch is passed to training loop

**Sources:** [docs/source/getting_started/benchmarks/cifar10_benchmark.py:263-269](), [docs/source/getting_started/benchmarks/imagenette_benchmark.py:296-302]()

### Edge Cases

The `MultiViewCollate` class handles several edge cases:

| Case | Behavior | Code |
|------|----------|------|
| Empty batch | Warning issued, returns `([], torch.tensor([]), [])` | [lightly/data/multi_view_collate.py:73-75]() |
| Single sample | Works correctly, batch dimension = 1 | [lightly/data/multi_view_collate.py:78-84]() |
| Variable view count | Expects all samples to have same number of views | [lightly/data/multi_view_collate.py:77]() |

**Sources:** [lightly/data/multi_view_collate.py:70-86]()

## Example Usage

### Complete DataLoader Setup

A complete example showing dataset creation, transform application, and dataloader configuration:

```mermaid
graph TB
    Input["Input directory<br/>with images"]
    CreateDataset["dataset = LightlyDataset(<br/>  input_dir=path,<br/>  transform=SimCLRTransform()<br/>)"]
    CreateLoader["dataloader = DataLoader(<br/>  dataset,<br/>  batch_size=256,<br/>  shuffle=True,<br/>  drop_last=True,<br/>  num_workers=8<br/>)"]
    Loop["for (x0, x1), labels, fnames in dataloader:<br/>  # x0, x1 are tensors of shape (256, 3, H, W)"]
    
    Input --> CreateDataset
    CreateDataset --> CreateLoader
    CreateLoader --> Loop
    
    style CreateLoader fill:#e1f5ff
```

**Sources:** [README.md:164-172](), [docs/source/getting_started/benchmarks/cifar10_benchmark.py:232-269]()

### Benchmark Usage Patterns

The benchmark scripts demonstrate real-world usage:

| Benchmark | Batch Size | Workers | Transform | Purpose |
|-----------|------------|---------|-----------|---------|
| CIFAR-10 | 128-512 | 8 | Method-specific | Fast small-scale testing | 
| ImageNette | 128-256 | 12 | Method-specific | Medium-scale validation |
| ImageNet100 | 256 | 12 | Method-specific | Large-scale subset |
| ImageNet1k | 256 | Variable | Method-specific | Full-scale benchmarks |

**Sources:** [docs/source/getting_started/benchmarks/cifar10_benchmark.py:104-138](), [docs/source/getting_started/benchmarks/imagenette_benchmark.py:121-148](), [docs/source/getting_started/benchmarks/imagenet100_benchmark.py:65-105]()

All benchmarks use the implicit `MultiViewCollate` behavior through the dataset's multi-view transforms, demonstrating that explicit collate function specification is often unnecessary when using Lightly's transform classes.

---

# Page: Command-Line Interface

# Command-Line Interface

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/source/getting_started/advanced.rst](docs/source/getting_started/advanced.rst)
- [docs/source/getting_started/command_line_tool.rst](docs/source/getting_started/command_line_tool.rst)
- [docs/source/getting_started/images/lightly_overview.png](docs/source/getting_started/images/lightly_overview.png)
- [docs/source/getting_started/install.rst](docs/source/getting_started/install.rst)
- [docs/source/getting_started/lightly_at_a_glance.rst](docs/source/getting_started/lightly_at_a_glance.rst)
- [docs/source/getting_started/main_concepts.rst](docs/source/getting_started/main_concepts.rst)
- [docs/source/index.rst](docs/source/index.rst)
- [docs/source/lightly.models.utils.rst](docs/source/lightly.models.utils.rst)
- [lightly/cli/__init__.py](lightly/cli/__init__.py)
- [lightly/cli/_helpers.py](lightly/cli/_helpers.py)
- [lightly/cli/config/config.yaml](lightly/cli/config/config.yaml)
- [lightly/cli/download_cli.py](lightly/cli/download_cli.py)
- [lightly/cli/embed_cli.py](lightly/cli/embed_cli.py)
- [lightly/cli/lightly_cli.py](lightly/cli/lightly_cli.py)
- [lightly/cli/train_cli.py](lightly/cli/train_cli.py)
- [requirements/base.txt](requirements/base.txt)
- [setup.py](setup.py)
- [tests/cli/test_cli_download.py](tests/cli/test_cli_download.py)
- [tests/cli/test_cli_magic.py](tests/cli/test_cli_magic.py)
- [tests/cli/test_cli_train.py](tests/cli/test_cli_train.py)
- [tests/embedding/test_embedding.py](tests/embedding/test_embedding.py)

</details>



The Lightly command-line interface (CLI) provides a set of tools for training self-supervised learning models, generating embeddings, and interacting with the Lightly Platform without writing Python code. The CLI enables quick experimentation and integration into automated workflows through shell scripts or CI/CD pipelines.

For information about using Lightly as a Python library, see [Python API](#5). For details on platform integration via the Python API, see [Platform Integration](#6).

---

## Overview of CLI Commands

The Lightly CLI consists of five primary commands, each serving a specific purpose in the self-supervised learning workflow:

| Command | Entry Point Function | Purpose |
|---------|---------------------|---------|
| `lightly-magic` | `lightly_cli()` | Train a model and generate embeddings in one command |
| `lightly-ssl-train` | `train_cli()` | Train a self-supervised model |
| `lightly-embed` | `embed_cli()` | Generate embeddings from a trained or pre-trained model |
| `lightly-download` | `download_cli()` | Download tagged samples from the Lightly Platform |
| `lightly-crop` | `crop_cli()` | Crop objects from images using YOLO-format labels |
| `lightly-version` | N/A | Display the installed Lightly version |

Each command is implemented as a separate module within [lightly/cli]() and uses Hydra for configuration management. Commands can be configured through YAML files or command-line parameter overrides.

Sources: [lightly/cli/__init__.py:1-14](), [docs/source/getting_started/command_line_tool.rst:1-237]()

---

## CLI Command Flow Architecture

```mermaid
graph TB
    subgraph "User Interface"
        USER["Shell/Terminal"]
        ENV_VARS["Environment Variables<br/>LIGHTLY_LAST_CHECKPOINT_PATH<br/>LIGHTLY_LAST_EMBEDDING_PATH<br/>LIGHTLY_LAST_DATASET_ID"]
    end
    
    subgraph "CLI Commands"
        MAGIC["lightly-magic<br/>lightly_cli()"]
        TRAIN["lightly-ssl-train<br/>train_cli()"]
        EMBED["lightly-embed<br/>embed_cli()"]
        DOWNLOAD["lightly-download<br/>download_cli()"]
        CROP["lightly-crop<br/>crop_cli()"]
        VERSION["lightly-version"]
    end
    
    subgraph "Internal Functions"
        TRAIN_INTERNAL["_train_cli()"]
        EMBED_INTERNAL["_embed_cli()"]
        DOWNLOAD_INTERNAL["_download_cli()"]
        HELPERS["_helpers.py<br/>get_model_from_config()<br/>get_ptmodel_from_config()<br/>load_from_state_dict()"]
    end
    
    subgraph "Configuration System"
        HYDRA["Hydra Framework"]
        CONFIG_YAML["config.yaml"]
        OVERRIDES["CLI Parameter Overrides"]
    end
    
    subgraph "Core Framework"
        DATASET["LightlyDataset"]
        MODEL["_SimCLR Model"]
        EMBEDDING["SelfSupervisedEmbedding"]
        COLLATE["ImageCollateFunction"]
    end
    
    subgraph "Platform Integration"
        API_CLIENT["ApiWorkflowClient"]
        PLATFORM["Lightly Platform"]
    end
    
    subgraph "Outputs"
        CHECKPOINT["*.ckpt files"]
        EMBEDDINGS["embeddings.csv"]
        FILELIST["tag_name.txt"]
    end
    
    USER --> MAGIC
    USER --> TRAIN
    USER --> EMBED
    USER --> DOWNLOAD
    USER --> CROP
    USER --> VERSION
    
    MAGIC --> TRAIN_INTERNAL
    MAGIC --> EMBED_INTERNAL
    TRAIN --> TRAIN_INTERNAL
    EMBED --> EMBED_INTERNAL
    DOWNLOAD --> DOWNLOAD_INTERNAL
    
    TRAIN_INTERNAL --> HELPERS
    EMBED_INTERNAL --> HELPERS
    
    HYDRA --> CONFIG_YAML
    HYDRA --> OVERRIDES
    CONFIG_YAML --> TRAIN_INTERNAL
    CONFIG_YAML --> EMBED_INTERNAL
    CONFIG_YAML --> DOWNLOAD_INTERNAL
    
    TRAIN_INTERNAL --> DATASET
    TRAIN_INTERNAL --> MODEL
    TRAIN_INTERNAL --> COLLATE
    TRAIN_INTERNAL --> EMBEDDING
    
    EMBED_INTERNAL --> DATASET
    EMBED_INTERNAL --> EMBEDDING
    
    DOWNLOAD_INTERNAL --> API_CLIENT
    API_CLIENT --> PLATFORM
    
    TRAIN_INTERNAL --> CHECKPOINT
    CHECKPOINT --> ENV_VARS
    EMBED_INTERNAL --> EMBEDDINGS
    EMBEDDINGS --> ENV_VARS
    DOWNLOAD_INTERNAL --> FILELIST
    
    CHECKPOINT --> EMBED_INTERNAL
```

**CLI Command Flow and Integration**

The diagram shows how CLI commands interact with the configuration system, core framework, and platform. Commands use Hydra for configuration management and track outputs via environment variables, enabling command chaining.

Sources: [lightly/cli/lightly_cli.py:1-69](), [lightly/cli/train_cli.py:1-188](), [lightly/cli/embed_cli.py:1-129](), [lightly/cli/download_cli.py:1-135]()

---

## Configuration System Architecture

The CLI uses Hydra for hierarchical configuration management. All commands share a common configuration file with command-specific parameter overrides.

```mermaid
graph TB
    subgraph "Configuration File Structure"
        CONFIG["config.yaml"]
        
        IO["I/O Parameters<br/>input_dir<br/>output_dir<br/>embeddings<br/>checkpoint"]
        PLATFORM["Platform Parameters<br/>token<br/>dataset_id<br/>tag_name<br/>upload mode"]
        TRAINING["Training Parameters<br/>pre_trained<br/>seed"]
        
        MODEL["model namespace<br/>name: resnet-18<br/>out_dim: 128<br/>num_ftrs: 32<br/>width: 1"]
        CRITERION["criterion namespace<br/>temperature: 0.5<br/>memory_bank_size: 0"]
        OPTIMIZER["optimizer namespace<br/>lr: 1.0<br/>weight_decay: 0.00001"]
        
        COLLATE["collate namespace<br/>input_size: 64<br/>cj_prob: 0.8<br/>gaussian_blur: 0.5<br/>min_scale: 0.15"]
        LOADER["loader namespace<br/>batch_size: 16<br/>shuffle: True<br/>num_workers: -1<br/>drop_last: True"]
        TRAINER["trainer namespace<br/>gpus: 1<br/>max_epochs: 100<br/>precision: 32"]
        
        CKPT_CB["checkpoint_callback<br/>save_last: True<br/>save_top_k: 1"]
        ENV_NAMES["environment_variable_names<br/>lightly_last_checkpoint_path<br/>lightly_last_embedding_path"]
        HYDRA_CFG["hydra namespace<br/>run.dir output path"]
    end
    
    subgraph "Override Mechanism"
        CLI_OVERRIDE["CLI Override<br/>trainer.max_epochs=10<br/>loader.batch_size=128"]
        PROGRAMMATIC["Programmatic Override<br/>cfg['trainer']['max_epochs']"]
    end
    
    subgraph "Target Components"
        RESNET["ResNetGenerator"]
        NTXENT["NTXentLoss"]
        SGD["torch.optim.SGD"]
        IMG_COLLATE["ImageCollateFunction"]
        DATALOADER["torch.utils.data.DataLoader"]
        PL_TRAINER["SelfSupervisedEmbedding"]
    end
    
    CONFIG --> IO
    CONFIG --> PLATFORM
    CONFIG --> TRAINING
    CONFIG --> MODEL
    CONFIG --> CRITERION
    CONFIG --> OPTIMIZER
    CONFIG --> COLLATE
    CONFIG --> LOADER
    CONFIG --> TRAINER
    CONFIG --> CKPT_CB
    CONFIG --> ENV_NAMES
    CONFIG --> HYDRA_CFG
    
    CLI_OVERRIDE -.overrides.-> CONFIG
    PROGRAMMATIC -.overrides.-> CONFIG
    
    MODEL --> RESNET
    CRITERION --> NTXENT
    OPTIMIZER --> SGD
    COLLATE --> IMG_COLLATE
    LOADER --> DATALOADER
    TRAINER --> PL_TRAINER
```

**Hydra Configuration Hierarchy**

The configuration file is organized into namespaces that map directly to PyTorch and Lightly components. Parameters can be overridden via CLI (`key.subkey=value`) or programmatically.

Sources: [lightly/cli/config/config.yaml:1-160](), [lightly/cli/_helpers.py:36-54]()

---

## Configuration Parameters

### I/O Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `input_dir` | str | `''` | Path to directory containing images |
| `output_dir` | str | `''` | Path for downloaded images/outputs |
| `embeddings` | str | `''` | Path to embeddings CSV file |
| `checkpoint` | str | `''` | Path to model checkpoint (`.ckpt` file) |
| `label_dir` | str | `''` | Path to directory with YOLO format labels |

### Platform Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `token` | str | `''` | Lightly Platform API token |
| `dataset_id` | str | `''` | Platform dataset identifier |
| `tag_name` | str | `'initial-tag'` | Tag name for downloads/uploads |
| `upload` | str | `'full'` | Upload mode: `'full'`, `'thumbnails'`, or `'none'` |
| `embedding_name` | str | `'default'` | Name for embeddings on platform |

### Training Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `pre_trained` | bool | `True` | Use pre-trained model from Lightly model zoo |
| `seed` | int | `1` | Random seed for reproducibility |
| `trainer.max_epochs` | int | `100` | Number of training epochs |
| `trainer.gpus` | int | `1` | Number of GPUs to use (deprecated in favor of `devices`) |
| `trainer.precision` | int | `32` | Training precision (16 or 32) |
| `loader.batch_size` | int | `16` | Batch size for training/inference |
| `loader.num_workers` | int | `-1` | Number of data loading workers (-1 = auto) |

### Model Architecture

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `model.name` | str | `'resnet-18'` | Model architecture (resnet-18/34/50/101/152) |
| `model.out_dim` | int | `128` | Projection head output dimension |
| `model.num_ftrs` | int | `32` | Feature vector dimension |
| `model.width` | float | `1` | ResNet width multiplier |

### Augmentation Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `collate.input_size` | int | `64` | Input image size in pixels |
| `collate.cj_prob` | float | `0.8` | Color jitter probability |
| `collate.gaussian_blur` | float | `0.5` | Gaussian blur probability |
| `collate.min_scale` | float | `0.15` | Minimum crop scale |
| `collate.hf_prob` | float | `0.5` | Horizontal flip probability |

Sources: [lightly/cli/config/config.yaml:1-160]()

---

## Environment Variables for Output Tracking

The CLI automatically sets environment variables to track outputs, enabling command chaining:

```mermaid
graph LR
    subgraph "Training Workflow"
        TRAIN_CMD["lightly-ssl-train<br/>input_dir=data/"]
        TRAIN_OUT["checkpoint.ckpt"]
        ENV_CKPT["$LIGHTLY_LAST_CHECKPOINT_PATH"]
    end
    
    subgraph "Embedding Workflow"
        EMBED_CMD["lightly-embed<br/>checkpoint=$LIGHTLY_LAST_CHECKPOINT_PATH"]
        EMBED_OUT["embeddings.csv"]
        ENV_EMB["$LIGHTLY_LAST_EMBEDDING_PATH"]
    end
    
    subgraph "Platform Workflow"
        UPLOAD["Upload to Platform"]
        ENV_DATASET["$LIGHTLY_LAST_DATASET_ID"]
    end
    
    TRAIN_CMD --> TRAIN_OUT
    TRAIN_OUT --> ENV_CKPT
    ENV_CKPT --> EMBED_CMD
    EMBED_CMD --> EMBED_OUT
    EMBED_OUT --> ENV_EMB
    ENV_EMB --> UPLOAD
    UPLOAD --> ENV_DATASET
```

**Environment Variable Chaining**

Commands set environment variables upon completion, allowing subsequent commands to reference previous outputs without manual path specification.

The environment variable names are configurable in [lightly/cli/config/config.yaml:106-109]():

```yaml
environment_variable_names:
  lightly_last_checkpoint_path: LIGHTLY_LAST_CHECKPOINT_PATH
  lightly_last_embedding_path: LIGHTLY_LAST_EMBEDDING_PATH
  lightly_last_dataset_id: LIGHTLY_LAST_DATASET_ID
```

Sources: [lightly/cli/config/config.yaml:106-109](), [lightly/cli/train_cli.py:149-151](), [lightly/cli/embed_cli.py:85-87]()

---

## Training Commands (lightly-ssl-train and lightly-magic)

### lightly-ssl-train

The `lightly-ssl-train` command trains a self-supervised SimCLR model on an image dataset. It is implemented in [lightly/cli/train_cli.py]() with the entry point function `train_cli()` decorated with `@hydra.main()`.

**Training Workflow Implementation:**

```mermaid
graph TB
    START["train_cli(cfg)"]
    
    FIX_PATH["fix_input_path()<br/>Convert to absolute path"]
    SET_SEED["Set random seed<br/>torch.manual_seed()"]
    CHECK_GPU["Determine accelerator<br/>GPU or CPU"]
    
    LOAD_CKPT["Load checkpoint<br/>if checkpoint or pre_trained"]
    GET_PT["get_ptmodel_from_config()<br/>Get model zoo URL"]
    LOAD_URL["load_state_dict_from_url()"]
    LOAD_FILE["torch.load()"]
    
    BUILD_MODEL["Build _SimCLR model<br/>ResNetGenerator + features"]
    CREATE_LOSS["Create NTXentLoss"]
    CREATE_OPT["Create SGD optimizer"]
    
    LOAD_DATA["Create LightlyDataset<br/>ImageCollateFunction<br/>DataLoader"]
    
    CREATE_EMB["Create SelfSupervisedEmbedding<br/>model, criterion, optimizer, dataloader"]
    
    TRAIN["encoder.train_embedding()<br/>PyTorch Lightning Trainer"]
    
    SAVE_ENV["Save checkpoint path to<br/>LIGHTLY_LAST_CHECKPOINT_PATH"]
    
    START --> FIX_PATH
    FIX_PATH --> SET_SEED
    SET_SEED --> CHECK_GPU
    CHECK_GPU --> LOAD_CKPT
    
    LOAD_CKPT --> GET_PT
    GET_PT --> LOAD_URL
    GET_PT --> LOAD_FILE
    
    LOAD_URL --> BUILD_MODEL
    LOAD_FILE --> BUILD_MODEL
    
    BUILD_MODEL --> CREATE_LOSS
    CREATE_LOSS --> CREATE_OPT
    CREATE_OPT --> LOAD_DATA
    LOAD_DATA --> CREATE_EMB
    CREATE_EMB --> TRAIN
    TRAIN --> SAVE_ENV
```

**lightly-ssl-train Execution Flow**

The command builds a SimCLR model with ResNet backbone, configures training components, and trains using PyTorch Lightning's Trainer. The checkpoint path is stored in an environment variable for downstream use.

**Example Usage:**

```bash
# Train with default settings
lightly-ssl-train input_dir=data/

# Train for 5 epochs with batch size 128
lightly-ssl-train input_dir=data/ trainer.max_epochs=5 loader.batch_size=128

# Continue training from checkpoint
lightly-ssl-train input_dir=data/ trainer.max_epochs=10 \
                  checkpoint=$LIGHTLY_LAST_CHECKPOINT_PATH

# Train with multiple GPUs (DDP strategy)
lightly-ssl-train input_dir=data/ trainer.gpus=4

# Train from scratch (no pre-trained weights)
lightly-ssl-train input_dir=data/ pre_trained=False

# Train with half precision
lightly-ssl-train input_dir=data/ trainer.precision=16
```

**Key Implementation Details:**

- **Model Architecture:** Uses `_SimCLR` class from [lightly/cli/_cli_simclr.py]() which combines a ResNet backbone with a projection head
- **Features Extraction:** Constructs features from `ResNetGenerator` with normalization layer and adaptive pooling [lightly/cli/train_cli.py:92-100]()
- **Checkpoint Loading:** Supports URLs (model zoo), local files, and state dict filtering for compatibility [lightly/cli/train_cli.py:83-90]()
- **Batch Size Warning:** Issues warning if batch size < 64 [lightly/cli/train_cli.py:57-63]()
- **Worker Count:** Auto-determines number of workers if set to -1 using `cpu_count()` [lightly/cli/train_cli.py:66-67]()

Sources: [lightly/cli/train_cli.py:37-153](), [lightly/cli/_helpers.py:199-238]()

### lightly-magic

The `lightly-magic` command combines training and embedding in a single execution. It internally calls `_train_cli()` followed by `_embed_cli()`.

**lightly-magic Execution Flow:**

```mermaid
graph TB
    START["lightly_cli(cfg)"]
    
    SET_TRAIN["Set training configs<br/>shuffle=True, drop_last=True"]
    CHECK_EPOCHS["trainer.max_epochs > 0?"]
    
    TRAIN["_train_cli(cfg)<br/>Train model"]
    GET_CKPT["checkpoint = training output"]
    SKIP_TRAIN["checkpoint = empty string"]
    
    SET_EMBED["Set embedding configs<br/>shuffle=False, drop_last=False<br/>cfg['checkpoint'] = checkpoint"]
    
    EMBED["_embed_cli(cfg)<br/>Generate embeddings"]
    
    FINISH["Finished"]
    
    START --> SET_TRAIN
    SET_TRAIN --> CHECK_EPOCHS
    CHECK_EPOCHS -->|Yes| TRAIN
    CHECK_EPOCHS -->|No| SKIP_TRAIN
    TRAIN --> GET_CKPT
    SKIP_TRAIN --> SET_EMBED
    GET_CKPT --> SET_EMBED
    SET_EMBED --> EMBED
    EMBED --> FINISH
```

**lightly-magic Command Flow**

The command conditionally trains a model (if `max_epochs > 0`), then uses the resulting checkpoint (or pre-trained model) to generate embeddings.

**Example Usage:**

```bash
# Train for 10 epochs and generate embeddings
lightly-magic input_dir=data/ trainer.max_epochs=10

# Only generate embeddings (using pre-trained model)
lightly-magic input_dir=data/ trainer.max_epochs=0

# Custom batch size
lightly-magic input_dir=data/ trainer.max_epochs=5 loader.batch_size=128
```

Sources: [lightly/cli/lightly_cli.py:20-64](), [docs/source/getting_started/command_line_tool.rst:84-108]()

---

## Embedding Generation (lightly-embed)

The `lightly-embed` command generates embeddings from images using a trained model or pre-trained weights. It is implemented in [lightly/cli/embed_cli.py]() with entry point `embed_cli()`.

**Embedding Generation Workflow:**

```mermaid
graph TB
    START["embed_cli(cfg)"]
    
    FIX_PATH["fix_input_path()"]
    SET_DEVICE["Set device<br/>cuda or cpu"]
    
    CREATE_TRANSFORM["Create transform pipeline<br/>Resize + ToTensor + Normalize"]
    CREATE_DATASET["LightlyDataset(input_dir, transform)"]
    
    CONFIG_LOADER["Configure DataLoader<br/>drop_last=False<br/>shuffle=False"]
    AUTO_WORKERS["Set num_workers<br/>if -1, use cpu_count()"]
    
    GET_MODEL["get_model_from_config()<br/>Load checkpoint or pre-trained"]
    
    EMBED["encoder.embed(dataloader, device)<br/>Returns embeddings, labels, filenames"]
    
    SAVE["save_embeddings()<br/>embeddings.csv"]
    
    SET_ENV["Set LIGHTLY_LAST_EMBEDDING_PATH"]
    
    START --> FIX_PATH
    FIX_PATH --> SET_DEVICE
    SET_DEVICE --> CREATE_TRANSFORM
    CREATE_TRANSFORM --> CREATE_DATASET
    CREATE_DATASET --> CONFIG_LOADER
    CONFIG_LOADER --> AUTO_WORKERS
    AUTO_WORKERS --> GET_MODEL
    GET_MODEL --> EMBED
    EMBED --> SAVE
    SAVE --> SET_ENV
```

**lightly-embed Execution Flow**

The command creates a dataset with inference transforms (resize, normalize), loads a model, runs inference to generate embeddings, and saves results to CSV.

**Transform Pipeline:**

The embedding command uses a standard inference transform [lightly/cli/embed_cli.py:56-62]():

```python
transform = T.Compose([
    T.Resize((cfg["collate"]["input_size"], cfg["collate"]["input_size"])),
    T.ToTensor(),
    T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])
```

**Example Usage:**

```bash
# Embed with pre-trained model
lightly-embed input_dir=data/

# Embed with custom checkpoint
lightly-embed input_dir=data/ checkpoint=my_checkpoint.ckpt

# Embed using the last trained checkpoint
lightly-embed input_dir=data/ checkpoint=$LIGHTLY_LAST_CHECKPOINT_PATH

# Embed with custom input size
lightly-embed input_dir=data/ collate.input_size=224

# Embed with custom feature dimension
lightly-embed input_dir=data/ model.num_ftrs=512
```

**Output Format:**

The command generates a CSV file named `embeddings.csv` in the current working directory with the following structure:

| Column | Description |
|--------|-------------|
| `filenames` | Image filename |
| `embedding_0`, `embedding_1`, ... | Embedding dimensions (count = `model.num_ftrs`) |
| `labels` | Integer labels (auto-generated from directory structure) |

Sources: [lightly/cli/embed_cli.py:31-124](), [docs/source/getting_started/command_line_tool.rst:155-182]()

---

## Platform Integration Commands (lightly-download)

The `lightly-download` command retrieves tagged samples from the Lightly Platform. It supports three modes of operation:

1. Download a list of filenames
2. Download full images from the platform
3. Copy images from a local input directory to an output directory

**Download Command Workflow:**

```mermaid
graph TB
    START["download_cli(cfg)"]
    
    VALIDATE["Validate parameters<br/>tag_name, token, dataset_id"]
    AUTO_WORKERS["Set num_workers<br/>min(max(8, cpu_count()), 32)"]
    
    CREATE_CLIENT["ApiWorkflowClient<br/>token, dataset_id"]
    
    GET_TAG["get_tag_by_name(tag_name)"]
    GET_FILES["get_filenames_in_tag()<br/>exclude_parent_tag option"]
    
    SAVE_LIST["Save to tag_name.txt"]
    
    CHECK_MODE{"Which mode?"}
    
    MODE_LIST["List only<br/>no input_dir, no output_dir"]
    MODE_DOWNLOAD["Download from platform<br/>no input_dir, has output_dir"]
    MODE_COPY["Copy local files<br/>has input_dir, has output_dir"]
    
    DOWNLOAD_API["api_workflow_client.download_dataset()"]
    
    COPY_LOCAL["LightlyDataset.dump()<br/>Copy files to output_dir"]
    
    FINISH["Finish"]
    
    START --> VALIDATE
    VALIDATE --> AUTO_WORKERS
    AUTO_WORKERS --> CREATE_CLIENT
    CREATE_CLIENT --> GET_TAG
    GET_TAG --> GET_FILES
    GET_FILES --> SAVE_LIST
    SAVE_LIST --> CHECK_MODE
    
    CHECK_MODE --> MODE_LIST
    CHECK_MODE --> MODE_DOWNLOAD
    CHECK_MODE --> MODE_COPY
    
    MODE_DOWNLOAD --> DOWNLOAD_API
    MODE_COPY --> COPY_LOCAL
    
    MODE_LIST --> FINISH
    DOWNLOAD_API --> FINISH
    COPY_LOCAL --> FINISH
```

**lightly-download Execution Flow**

The command retrieves filenames from a tag, saves them to a text file, and optionally downloads images or copies them from a local directory based on the provided parameters.

**Example Usage:**

```bash
# Download list of filenames in a tag
lightly-download tag_name='my-tag' dataset_id='XYZ' token='123'

# Download list excluding parent tag samples
lightly-download tag_name='my-tag' dataset_id='XYZ' token='123' \
                 exclude_parent_tag=True

# Download full images from platform
lightly-download tag_name='my-tag' dataset_id='XYZ' token='123' \
                 output_dir='downloaded_images/'

# Copy tagged images from local directory
lightly-download tag_name='my-tag' dataset_id='XYZ' token='123' \
                 input_dir='all_images/' output_dir='selected_images/'
```

**Key Parameters:**

| Parameter | Required | Description |
|-----------|----------|-------------|
| `tag_name` | Yes | Tag name to download (use 'initial-tag' for all images) |
| `dataset_id` | Yes | Platform dataset identifier |
| `token` | Yes | Platform API token |
| `input_dir` | No | Source directory for local copy mode |
| `output_dir` | No | Destination directory for downloads/copies |
| `exclude_parent_tag` | No | If True, exclude samples from parent tag |

**Output:**

The command always creates a `{tag_name}.txt` file containing the list of filenames. If `output_dir` is specified, images are downloaded or copied to that directory.

Sources: [lightly/cli/download_cli.py:22-131](), [docs/source/getting_started/command_line_tool.rst:183-209]()

---

## Image Cropping (lightly-crop)

The `lightly-crop` command extracts object crops from images based on YOLO-format bounding box labels. This is useful for object-level self-supervised learning rather than image-level.

**Label Format:**

Labels must be in YOLO format with one `.txt` file per image. Each line in the label file contains:

```
class x_center y_center width height
```

Where all coordinates are normalized to [0, 1]. Example [docs/source/getting_started/command_line_tool.rst:70-73]():

```
0 0.23 0.14 0.05 0.04
1 0.43 0.13 0.12 0.08
```

**Example Usage:**

```bash
# Crop with 20% padding around bounding boxes
lightly-crop input_dir=images label_dir=labels output_dir=cropped_images \
             crop_padding=0.2

# Include class names in output filenames
lightly-crop input_dir=images label_dir=labels output_dir=cropped_images \
             label_names_file=data.yaml
```

**Label Names File Format:**

The `label_names_file` should be a YAML file with class names [docs/source/getting_started/command_line_tool.rst:78-79]():

```yaml
names: [cat, dog]
```

**Workflow:**

1. Read images from `input_dir`
2. Read corresponding labels from `label_dir`
3. For each bounding box, extract a crop with padding
4. Save crops to `output_dir` with naming: `{original_filename}_{class_name}_{index}.jpg`

The cropped images can then be used as input for `lightly-ssl-train` to learn object-level representations.

Sources: [docs/source/getting_started/command_line_tool.rst:42-82]()

---

## Version Check (lightly-version)

The `lightly-version` command displays the installed Lightly package version. This is useful for verifying the installation and debugging compatibility issues.

**Example Usage:**

```bash
lightly-version
# Output: lightly version 1.1.4
```

Sources: [docs/source/getting_started/command_line_tool.rst:27-40]()

---

## Configuration Override Mechanisms

The CLI supports multiple ways to override default configuration values:

### CLI Override Syntax

Parameters can be overridden using dot notation:

```bash
# Override top-level parameter
lightly-ssl-train input_dir=data/ pre_trained=False

# Override nested parameter
lightly-ssl-train input_dir=data/ trainer.max_epochs=10

# Override deeply nested parameter
lightly-ssl-train input_dir=data/ checkpoint_callback.save_top_k=3

# Multiple overrides
lightly-ssl-train input_dir=data/ \
                  trainer.max_epochs=5 \
                  loader.batch_size=128 \
                  model.num_ftrs=256
```

### Configuration File Customization

Users can create custom configuration files and specify them via Hydra's config path mechanism. The default configuration is located at [lightly/cli/config/config.yaml]().

### Programmatic Configuration

When using CLI functions programmatically (e.g., in tests), configuration can be modified via dictionary access:

```python
from hydra.experimental import compose, initialize

with initialize(config_path="lightly/cli/config"):
    cfg = compose(
        config_name="config",
        overrides=["input_dir=data/", "trainer.max_epochs=5"]
    )
    # Modify programmatically
    cfg["trainer"]["max_epochs"] = 10
    cfg["loader"]["batch_size"] = 128
```

Sources: [lightly/cli/train_cli.py:155-183](), [tests/cli/test_cli_train.py:26-33]()

---

## Hydra Integration Details

The CLI uses Hydra 1.0+ for configuration management. Each CLI command is decorated with `@hydra.main()` which handles:

1. **Configuration Loading:** Reads [lightly/cli/config/config.yaml]()
2. **Override Processing:** Applies CLI parameter overrides
3. **Working Directory Management:** Changes to Hydra output directory
4. **Help Generation:** Auto-generates help text from config

**Hydra Decorator Usage:**

```python
@hydra.main(**fix_hydra_arguments(config_path="config", config_name="config"))
def train_cli(cfg):
    return _train_cli(cfg)
```

The `fix_hydra_arguments()` helper [lightly/cli/_helpers.py:36-54]() provides backward compatibility across Hydra versions by conditionally adding the `version_base` parameter for Hydra 1.2+.

**Hydra Output Directory:**

By default, Hydra creates outputs in timestamped directories [lightly/cli/config/config.yaml:117-118]():

```yaml
hydra:
  run:
    dir: lightly_outputs/${now:%Y-%m-%d}/${now:%H-%M-%S}
```

This can be overridden:

```bash
lightly-ssl-train input_dir=data/ hydra.run.dir=./my_output
```

Sources: [lightly/cli/_helpers.py:36-54](), [lightly/cli/config/config.yaml:114-160]()

---

## Helper Functions and Utilities

The [lightly/cli/_helpers.py]() module provides shared utilities for CLI commands:

### Path Handling

- **`fix_input_path(path)`** [lightly/cli/_helpers.py:29-33](): Converts relative paths to absolute using Hydra's `utils.to_absolute_path()`
- Used by all CLI commands to handle user-provided paths correctly

### Model Loading

- **`get_ptmodel_from_config(model)`** [lightly/cli/_helpers.py:62-72](): Constructs model zoo key from config parameters
- **`get_model_from_config(cfg, is_cli_call)`** [lightly/cli/_helpers.py:199-238](): Loads a complete model from config, checkpoint, or model zoo
- **`load_state_dict_from_url(url)`** [lightly/cli/_helpers.py:75-92](): Downloads checkpoint from URL with HTTP fallback

### State Dict Compatibility

- **`load_from_state_dict(model, state_dict)`** [lightly/cli/_helpers.py:175-197](): Loads weights with compatibility handling
- **`_filter_state_dict(state_dict)`** [lightly/cli/_helpers.py:119-141](): Removes model prefix for PyTorch Lightning compatibility
- **`_fix_projection_head_keys(state_dict)`** [lightly/cli/_helpers.py:144-172](): Updates old checkpoint format to new structure
- **`_maybe_expand_batchnorm_weights()`** [lightly/cli/_helpers.py:95-116](): Expands BatchNorm weights for SplitBatchNorm compatibility

### System Information

- **`cpu_count()`** [lightly/cli/_helpers.py:20-26](): Returns system CPU count for auto-determining worker count

Sources: [lightly/cli/_helpers.py:1-238]()

---

## Model Architecture in CLI

The CLI uses a simplified SimCLR architecture defined in `_SimCLR` class. The model construction process:

```mermaid
graph TB
    START["Model Construction"]
    
    RESNET["ResNetGenerator<br/>name, width"]
    NORM["get_norm_layer(3, 0)<br/>Input normalization"]
    BACKBONE["ResNet layers<br/>[:-1] exclude fc"]
    CONV["Conv2d<br/>last_conv_channels → num_ftrs"]
    POOL["AdaptiveAvgPool2d(1)"]
    
    FEATURES["features module<br/>Sequential of above"]
    
    SIMCLR["_SimCLR<br/>features, num_ftrs, out_dim"]
    
    PROJECTION["SimCLRProjectionHead<br/>internal component"]
    
    START --> RESNET
    RESNET --> NORM
    NORM --> BACKBONE
    BACKBONE --> CONV
    CONV --> POOL
    POOL --> FEATURES
    FEATURES --> SIMCLR
    SIMCLR --> PROJECTION
```

**CLI Model Architecture Construction**

The CLI builds a feature extractor from ResNet components and wraps it in a `_SimCLR` model with a projection head.

The features module [lightly/cli/train_cli.py:93-100]() combines:
1. Input normalization layer
2. ResNet backbone (excluding final FC layer)
3. 1x1 convolution to project to `num_ftrs` dimensions
4. Global average pooling

This is then passed to `_SimCLR` which adds a projection head for contrastive learning.

Sources: [lightly/cli/train_cli.py:92-106](), [lightly/cli/_helpers.py:220-231]()

---

## CLI Testing Infrastructure

The CLI has comprehensive test coverage in the [tests/cli]() directory:

- **`test_cli_train.py`**: Tests training command execution and checkpoint creation
- **`test_cli_magic.py`**: Tests combined training and embedding workflow
- **`test_cli_download.py`**: Tests platform download functionality with mocked API
- **Embedding tests**: Located in [tests/embedding/test_embedding.py]()

**Test Structure:**

Tests use Hydra's `compose()` and `initialize()` for programmatic configuration [tests/cli/test_cli_train.py:26-33]():

```python
with initialize(config_path="../../lightly/cli/config", job_name="test_app"):
    cfg = compose(
        config_name="config",
        overrides=[
            f"input_dir={folder_path}",
            "trainer.max_epochs=1",
        ],
    )
```

Tests verify:
- Checkpoint creation and path storage in environment variables
- Embeddings generation with correct ordering
- Configuration parsing and override handling
- Platform integration with mocked API client

Sources: [tests/cli/test_cli_train.py:1-63](), [tests/cli/test_cli_magic.py:1-92](), [tests/cli/test_cli_download.py:1-136](), [tests/embedding/test_embedding.py:1-82]()

---

## Common Usage Patterns

### Pattern 1: Complete Local Workflow

```bash
# Train a model
lightly-ssl-train input_dir=raw_images/ trainer.max_epochs=100 \
                  loader.batch_size=256

# Generate embeddings from trained model
lightly-embed input_dir=raw_images/ checkpoint=$LIGHTLY_LAST_CHECKPOINT_PATH
```

### Pattern 2: Using Pre-trained Models

```bash
# Use pre-trained model from model zoo (default)
lightly-embed input_dir=images/ collate.input_size=224

# Specify model architecture for pre-trained weights
lightly-embed input_dir=images/ model.name=resnet-50 model.num_ftrs=2048
```

### Pattern 3: Platform-Integrated Workflow

```bash
# Download tagged subset
lightly-download tag_name=curated_v1 dataset_id=$DATASET_ID token=$TOKEN \
                 input_dir=all_images/ output_dir=selected_images/

# Train on selected subset
lightly-ssl-train input_dir=selected_images/ trainer.max_epochs=50

# Generate embeddings
lightly-embed input_dir=selected_images/ checkpoint=$LIGHTLY_LAST_CHECKPOINT_PATH
```

### Pattern 4: Object Detection Preprocessing

```bash
# Crop objects from images
lightly-crop input_dir=images/ label_dir=yolo_labels/ \
             output_dir=crops/ crop_padding=0.1

# Train on object crops
lightly-ssl-train input_dir=crops/ trainer.max_epochs=100
```

### Pattern 5: One-Command Training and Embedding

```bash
# Train and embed in single command
lightly-magic input_dir=images/ trainer.max_epochs=50 loader.batch_size=128
```

Sources: [docs/source/getting_started/command_line_tool.rst:110-228]()

---

## Advanced Configuration Examples

### Multi-GPU Training

```bash
# Distributed data parallel with 4 GPUs
lightly-ssl-train input_dir=data/ trainer.gpus=4 loader.batch_size=64
# Note: Effective batch size = 4 GPUs × 64 = 256
```

### Half-Precision Training

```bash
# 16-bit precision for faster training and reduced memory
lightly-ssl-train input_dir=data/ trainer.precision=16
```

### Custom Augmentation Parameters

```bash
# Disable color jittering and Gaussian blur
lightly-ssl-train input_dir=data/ \
                  collate.cj_prob=0.0 \
                  collate.gaussian_blur=0.0

# Strong augmentations for large images
lightly-ssl-train input_dir=data/ \
                  collate.input_size=224 \
                  collate.min_scale=0.08 \
                  collate.cj_prob=0.8 \
                  collate.gaussian_blur=0.5
```

### Custom Model Architecture

```bash
# Use ResNet-50 with larger feature dimension
lightly-ssl-train input_dir=data/ \
                  model.name=resnet-50 \
                  model.num_ftrs=2048 \
                  model.out_dim=256
```

### Memory Bank Configuration

```bash
# Use memory bank for MoCo-style training
lightly-ssl-train input_dir=data/ \
                  criterion.memory_bank_size=4096 \
                  criterion.temperature=0.07
```

### Checkpoint Management

```bash
# Save top 3 checkpoints based on validation metric
lightly-ssl-train input_dir=data/ \
                  checkpoint_callback.save_top_k=3

# Specify custom checkpoint directory
lightly-ssl-train input_dir=data/ \
                  checkpoint_callback.dirpath=./checkpoints/
```

Sources: [lightly/cli/config/config.yaml:1-160](), [docs/source/getting_started/command_line_tool.rst:110-147]()

---

# Page: Training Commands

# Training Commands

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/source/getting_started/advanced.rst](docs/source/getting_started/advanced.rst)
- [docs/source/getting_started/command_line_tool.rst](docs/source/getting_started/command_line_tool.rst)
- [docs/source/getting_started/images/lightly_overview.png](docs/source/getting_started/images/lightly_overview.png)
- [docs/source/getting_started/install.rst](docs/source/getting_started/install.rst)
- [docs/source/getting_started/lightly_at_a_glance.rst](docs/source/getting_started/lightly_at_a_glance.rst)
- [docs/source/getting_started/main_concepts.rst](docs/source/getting_started/main_concepts.rst)
- [docs/source/index.rst](docs/source/index.rst)
- [docs/source/lightly.models.utils.rst](docs/source/lightly.models.utils.rst)
- [lightly/cli/_helpers.py](lightly/cli/_helpers.py)
- [lightly/cli/config/config.yaml](lightly/cli/config/config.yaml)
- [lightly/cli/embed_cli.py](lightly/cli/embed_cli.py)
- [lightly/cli/lightly_cli.py](lightly/cli/lightly_cli.py)
- [lightly/cli/train_cli.py](lightly/cli/train_cli.py)
- [tests/cli/test_cli_magic.py](tests/cli/test_cli_magic.py)
- [tests/cli/test_cli_train.py](tests/cli/test_cli_train.py)

</details>



## Purpose and Scope

This document covers the command-line tools for training self-supervised learning models in Lightly. The primary commands are `lightly-ssl-train` for training models and `lightly-magic` for combined training and embedding generation.

For information about generating embeddings from trained models, see [Embedding Generation](#4.2). For details about configuration parameters and Hydra-based configuration, see [CLI Configuration](#4.4). For platform integration commands, see [Platform Integration Commands](#4.3).

## Overview

Lightly provides two main training commands:

| Command | Purpose | Typical Use Case |
|---------|---------|------------------|
| `lightly-ssl-train` | Train a self-supervised model | Full control over training process, resume from checkpoint |
| `lightly-magic` | Train and embed in one command | Quick experimentation, end-to-end workflow |

Both commands use the same underlying training infrastructure but differ in their workflow and outputs.

## Command Execution Flow

```mermaid
graph TB
    subgraph "lightly-ssl-train"
        TRAIN_START["lightly-ssl-train<br/>entry point"]
        TRAIN_HYDRA["hydra.main decorator<br/>train_cli()"]
        TRAIN_IMPL["_train_cli()"]
        TRAIN_SETUP["Setup:<br/>- Load config<br/>- Fix paths<br/>- Set random seed"]
        TRAIN_MODEL["Create Model:<br/>- ResNetGenerator<br/>- _SimCLR wrapper<br/>- NTXentLoss"]
        TRAIN_DATA["Create DataLoader:<br/>- LightlyDataset<br/>- ImageCollateFunction"]
        TRAIN_EMBEDDING["SelfSupervisedEmbedding<br/>train_embedding()"]
        TRAIN_SAVE["Save checkpoint<br/>Set LIGHTLY_LAST_CHECKPOINT_PATH"]
    end
    
    subgraph "lightly-magic"
        MAGIC_START["lightly-magic<br/>entry point"]
        MAGIC_HYDRA["hydra.main decorator<br/>lightly_cli()"]
        MAGIC_IMPL["_lightly_cli()"]
        MAGIC_TRAIN["Call _train_cli()<br/>if max_epochs > 0"]
        MAGIC_EMBED["Call _embed_cli()<br/>with checkpoint"]
        MAGIC_DONE["Output embeddings<br/>Set env variables"]
    end
    
    TRAIN_START --> TRAIN_HYDRA
    TRAIN_HYDRA --> TRAIN_IMPL
    TRAIN_IMPL --> TRAIN_SETUP
    TRAIN_SETUP --> TRAIN_MODEL
    TRAIN_SETUP --> TRAIN_DATA
    TRAIN_MODEL --> TRAIN_EMBEDDING
    TRAIN_DATA --> TRAIN_EMBEDDING
    TRAIN_EMBEDDING --> TRAIN_SAVE
    
    MAGIC_START --> MAGIC_HYDRA
    MAGIC_HYDRA --> MAGIC_IMPL
    MAGIC_IMPL --> MAGIC_TRAIN
    MAGIC_TRAIN --> MAGIC_EMBED
    MAGIC_EMBED --> MAGIC_DONE
```

Sources: [lightly/cli/train_cli.py:155-188](), [lightly/cli/lightly_cli.py:20-64]()

## lightly-ssl-train Command

### Purpose

The `lightly-ssl-train` command trains self-supervised learning models using the SimCLR method. It provides fine-grained control over training parameters, checkpoint management, and distributed training.

### Entry Point and Initialization

The command is registered via the `train_cli()` function which is decorated with `hydra.main` to enable hierarchical configuration management:

```python
@hydra.main(**fix_hydra_arguments(config_path="config", config_name="config"))
def train_cli(cfg):
    return _train_cli(cfg)
```

Sources: [lightly/cli/train_cli.py:155-183]()

### Basic Usage Examples

```bash
# Train with default parameters
lightly-ssl-train input_dir=path/to/images

# Train for 5 epochs with custom batch size
lightly-ssl-train input_dir=path/to/images trainer.max_epochs=5 loader.batch_size=128

# Continue training from checkpoint
lightly-ssl-train input_dir=path/to/images checkpoint=model.ckpt trainer.max_epochs=10

# Train with multiple GPUs (DDP strategy)
lightly-ssl-train input_dir=path/to/images trainer.gpus=2

# Train with half-precision
lightly-ssl-train input_dir=path/to/images trainer.precision=16

# Use last checkpoint via environment variable
lightly-ssl-train input_dir=path/to/images checkpoint=$LIGHTLY_LAST_CHECKPOINT_PATH
```

Sources: [docs/source/getting_started/command_line_tool.rst:112-151](), [lightly/cli/config/config.yaml:120-143]()

### Training Architecture

```mermaid
graph TB
    CONFIG["Configuration<br/>config.yaml"]
    SEED["Set Random Seed<br/>torch.manual_seed()"]
    CHECKPOINT_LOAD["Load Checkpoint<br/>(if specified)"]
    
    subgraph "Model Creation"
        RESNET["ResNetGenerator<br/>cfg['model']['name']<br/>cfg['model']['width']"]
        NORM["get_norm_layer(3, 0)"]
        FEATURES["Feature Extractor<br/>Conv2d + AdaptiveAvgPool2d"]
        SIMCLR["_SimCLR<br/>num_ftrs, out_dim"]
    end
    
    subgraph "Loss and Optimizer"
        CRITERION["NTXentLoss<br/>temperature<br/>memory_bank_size"]
        OPTIMIZER["torch.optim.SGD<br/>lr, weight_decay"]
    end
    
    subgraph "Data Pipeline"
        DATASET["LightlyDataset<br/>input_dir"]
        COLLATE["ImageCollateFunction<br/>input_size, augmentations"]
        DATALOADER["torch.utils.data.DataLoader<br/>batch_size, num_workers"]
    end
    
    EMBEDDING["SelfSupervisedEmbedding<br/>model, criterion, optimizer, dataloader"]
    TRAIN["train_embedding()<br/>trainer_config<br/>checkpoint_callback_config"]
    SAVE["Save Checkpoint<br/>encoder.checkpoint"]
    ENV["Set Environment Variable<br/>LIGHTLY_LAST_CHECKPOINT_PATH"]
    
    CONFIG --> SEED
    CONFIG --> CHECKPOINT_LOAD
    CONFIG --> RESNET
    CONFIG --> CRITERION
    CONFIG --> OPTIMIZER
    CONFIG --> DATASET
    
    RESNET --> NORM
    NORM --> FEATURES
    FEATURES --> SIMCLR
    CHECKPOINT_LOAD --> SIMCLR
    
    DATASET --> COLLATE
    COLLATE --> DATALOADER
    
    SIMCLR --> EMBEDDING
    CRITERION --> EMBEDDING
    OPTIMIZER --> EMBEDDING
    DATALOADER --> EMBEDDING
    
    EMBEDDING --> TRAIN
    TRAIN --> SAVE
    SAVE --> ENV
```

Sources: [lightly/cli/train_cli.py:37-152]()

### Key Configuration Parameters

The training command uses parameters from the Hydra configuration file. Key parameters include:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `input_dir` | `''` | Path to directory containing images |
| `checkpoint` | `''` | Path to model checkpoint for resuming training |
| `pre_trained` | `True` | Whether to use pre-trained weights from model zoo |
| `seed` | `1` | Random seed for reproducibility |
| `model.name` | `'resnet-18'` | Backbone architecture name |
| `model.out_dim` | `128` | Output dimension for projection head |
| `model.num_ftrs` | `32` | Feature embedding dimension |
| `model.width` | `1` | ResNet width multiplier |
| `criterion.temperature` | `0.5` | Temperature for NTXentLoss |
| `criterion.memory_bank_size` | `0` | Size of memory bank (0 = disabled) |
| `optimizer.lr` | `1.0` | Learning rate |
| `optimizer.weight_decay` | `0.00001` | L2 regularization weight |
| `loader.batch_size` | `16` | Batch size for training |
| `loader.num_workers` | `-1` | Number of data loading workers (-1 = auto) |
| `trainer.max_epochs` | `100` | Number of training epochs |
| `trainer.gpus` | `1` | Number of GPUs to use |
| `trainer.precision` | `32` | Training precision (16 or 32) |

Sources: [lightly/cli/config/config.yaml:1-112]()

### Model Architecture Details

The training command creates a SimCLR model using the following components:

1. **Backbone**: Created via `ResNetGenerator` with configurable architecture and width
2. **Feature Extraction**: Sequential pipeline with normalization layer, ResNet backbone (without final FC layer), 1x1 convolution, and adaptive pooling
3. **Projection Head**: Wrapped in `_SimCLR` class which adds the SimCLR projection head
4. **Loss Function**: `NTXentLoss` with optional memory bank support

Sources: [lightly/cli/train_cli.py:92-106]()

### Checkpoint Management

The training process handles checkpoints through multiple mechanisms:

1. **Pre-trained Models**: If `pre_trained=True` and no checkpoint specified, downloads from model zoo via `get_ptmodel_from_config()`
2. **Custom Checkpoints**: Loads state dict from specified checkpoint path or URL
3. **Resume Training**: Uses `load_from_state_dict()` to load weights, handling compatibility issues
4. **Save Checkpoints**: Saves via PyTorch Lightning's checkpoint callback
5. **Environment Variable**: Sets `LIGHTLY_LAST_CHECKPOINT_PATH` to latest checkpoint path

```mermaid
graph LR
    CHECK_PRE["pre_trained=True<br/>checkpoint=''"]
    CHECK_CUSTOM["checkpoint specified"]
    
    ZOO["Model Zoo<br/>get_ptmodel_from_config()"]
    URL["URL<br/>load_state_dict_from_url()"]
    FILE["Local File<br/>torch.load()"]
    
    FILTER["Filter State Dict<br/>_filter_state_dict()"]
    FIX_HEADS["Fix Projection Head Keys<br/>_fix_projection_head_keys()"]
    EXPAND_BN["Expand BatchNorm<br/>_maybe_expand_batchnorm_weights()"]
    LOAD["model.load_state_dict()"]
    
    CHECK_PRE --> ZOO
    CHECK_CUSTOM --> URL
    CHECK_CUSTOM --> FILE
    
    ZOO --> FILTER
    URL --> FILTER
    FILE --> FILTER
    
    FILTER --> FIX_HEADS
    FIX_HEADS --> EXPAND_BN
    EXPAND_BN --> LOAD
```

Sources: [lightly/cli/train_cli.py:69-106](), [lightly/cli/_helpers.py:119-197]()

### Distributed Training Configuration

The command automatically configures distributed training based on available GPUs:

```python
accelerator = "gpu" if torch.cuda.is_available() else "cpu"
if accelerator == "gpu" and cfg["trainer"]["gpus"] > 1:
    devices = cfg["trainer"]["gpus"]
    strategy = "ddp"
else:
    devices = 1
    strategy = None
```

This configuration:
- Uses GPU if available, otherwise CPU
- Enables Distributed Data Parallel (DDP) strategy for multi-GPU training
- Automatically adjusts for PyTorch Lightning version compatibility

Sources: [lightly/cli/train_cli.py:49-56](), [lightly/cli/train_cli.py:127-137]()

### Data Loading Configuration

The command creates the data pipeline with the following components:

1. **Dataset**: `LightlyDataset` created from input directory
2. **Collate Function**: `ImageCollateFunction` configured with augmentation parameters
3. **DataLoader**: PyTorch DataLoader with configurable batch size and workers
4. **Auto-Configuration**: 
   - Batch size capped at dataset size
   - Number of workers auto-detected if set to -1 (via `cpu_count()`)
   - Warning issued if batch size < 64

Sources: [lightly/cli/train_cli.py:57-118]()

## lightly-magic Command

### Purpose

The `lightly-magic` command provides a streamlined workflow that combines model training and embedding generation in a single command. It internally calls `_train_cli()` followed by `_embed_cli()`.

### Workflow

```mermaid
graph TB
    START["lightly-magic invoked"]
    CHECK_EPOCHS["Check trainer.max_epochs"]
    
    subgraph "Training Phase (if max_epochs > 0)"
        CONFIG_TRAIN["Configure for training:<br/>shuffle=True<br/>drop_last=True"]
        TRAIN["_train_cli(cfg)"]
        CHECKPOINT["Get checkpoint path"]
    end
    
    subgraph "Embedding Phase"
        CONFIG_EMBED["Configure for embedding:<br/>shuffle=False<br/>drop_last=False<br/>checkpoint=checkpoint"]
        EMBED["_embed_cli(cfg)"]
        SAVE_EMB["Save embeddings.csv<br/>Set LIGHTLY_LAST_EMBEDDING_PATH"]
    end
    
    START --> CHECK_EPOCHS
    CHECK_EPOCHS -->|"> 0"| CONFIG_TRAIN
    CHECK_EPOCHS -->|"= 0"| CONFIG_EMBED
    CONFIG_TRAIN --> TRAIN
    TRAIN --> CHECKPOINT
    CHECKPOINT --> CONFIG_EMBED
    CONFIG_EMBED --> EMBED
    EMBED --> SAVE_EMB
```

Sources: [lightly/cli/lightly_cli.py:20-38]()

### Basic Usage Examples

```bash
# Train for 10 epochs and generate embeddings
lightly-magic input_dir=path/to/images trainer.max_epochs=10

# Use pre-trained model only (no training)
lightly-magic input_dir=path/to/images trainer.max_epochs=0

# Custom batch size and workers
lightly-magic input_dir=path/to/images trainer.max_epochs=10 loader.batch_size=128 loader.num_workers=8

# Custom image size
lightly-magic input_dir=path/to/images collate.input_size=224 trainer.max_epochs=5
```

Sources: [docs/source/getting_started/command_line_tool.rst:84-108]()

### Configuration Changes

The `lightly-magic` command modifies configuration between training and embedding phases:

| Phase | shuffle | drop_last | Purpose |
|-------|---------|-----------|---------|
| Training | `True` | `True` | Randomize batches, ensure consistent batch sizes |
| Embedding | `False` | `False` | Preserve order, process all samples |

Sources: [lightly/cli/lightly_cli.py:21-31]()

### Equivalence to Separate Commands

The `lightly-magic` command is equivalent to running:

```bash
# Train the model
lightly-ssl-train input_dir=data_dir

# Generate embeddings using the trained checkpoint
lightly-embed input_dir=data_dir checkpoint=$LIGHTLY_LAST_CHECKPOINT_PATH
```

Sources: [docs/source/getting_started/command_line_tool.rst:210-228]()

## Environment Variables

Both training commands manage environment variables for workflow integration:

| Variable Name | Set By | Purpose |
|---------------|--------|---------|
| `LIGHTLY_LAST_CHECKPOINT_PATH` | `lightly-ssl-train`, `lightly-magic` | Path to most recent checkpoint file |
| `LIGHTLY_LAST_EMBEDDING_PATH` | `lightly-magic` | Path to most recent embeddings file |

The environment variable names are configurable via the `environment_variable_names` section in the configuration file:

```yaml
environment_variable_names:
  lightly_last_checkpoint_path: LIGHTLY_LAST_CHECKPOINT_PATH
  lightly_last_embedding_path: LIGHTLY_LAST_EMBEDDING_PATH
```

These variables enable chaining commands and resuming workflows without manually tracking file paths.

Sources: [lightly/cli/config/config.yaml:105-109](), [lightly/cli/train_cli.py:146-151]()

## Code Entity Reference

### Key Classes and Functions

| Entity | Location | Purpose |
|--------|----------|---------|
| `train_cli()` | [lightly/cli/train_cli.py:156]() | Entry point for `lightly-ssl-train` |
| `_train_cli()` | [lightly/cli/train_cli.py:37]() | Core training implementation |
| `lightly_cli()` | [lightly/cli/lightly_cli.py:42]() | Entry point for `lightly-magic` |
| `_lightly_cli()` | [lightly/cli/lightly_cli.py:20]() | Core magic command implementation |
| `_SimCLR` | [lightly/cli/_cli_simclr.py]() | SimCLR model wrapper for CLI |
| `ResNetGenerator` | [lightly/models]() | Creates ResNet backbones |
| `ImageCollateFunction` | [lightly/data]() | Collates augmented image batches |
| `SelfSupervisedEmbedding` | [lightly/embedding]() | Wrapper for training and embedding |
| `get_ptmodel_from_config()` | [lightly/cli/_helpers.py:62]() | Downloads pre-trained models from zoo |
| `load_from_state_dict()` | [lightly/cli/_helpers.py:175]() | Loads checkpoints with compatibility fixes |
| `cpu_count()` | [lightly/cli/_helpers.py:20]() | Gets number of available CPU cores |
| `fix_input_path()` | [lightly/cli/_helpers.py:29]() | Converts relative paths to absolute |

Sources: [lightly/cli/train_cli.py](), [lightly/cli/lightly_cli.py](), [lightly/cli/_helpers.py]()

---

# Page: Embedding Generation

# Embedding Generation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/source/getting_started/advanced.rst](docs/source/getting_started/advanced.rst)
- [docs/source/getting_started/command_line_tool.rst](docs/source/getting_started/command_line_tool.rst)
- [docs/source/getting_started/images/lightly_overview.png](docs/source/getting_started/images/lightly_overview.png)
- [docs/source/getting_started/install.rst](docs/source/getting_started/install.rst)
- [docs/source/getting_started/lightly_at_a_glance.rst](docs/source/getting_started/lightly_at_a_glance.rst)
- [docs/source/getting_started/main_concepts.rst](docs/source/getting_started/main_concepts.rst)
- [docs/source/index.rst](docs/source/index.rst)
- [docs/source/lightly.models.utils.rst](docs/source/lightly.models.utils.rst)
- [lightly/cli/_helpers.py](lightly/cli/_helpers.py)
- [lightly/cli/config/config.yaml](lightly/cli/config/config.yaml)
- [lightly/cli/embed_cli.py](lightly/cli/embed_cli.py)
- [lightly/cli/lightly_cli.py](lightly/cli/lightly_cli.py)
- [lightly/cli/train_cli.py](lightly/cli/train_cli.py)
- [tests/cli/test_cli_magic.py](tests/cli/test_cli_magic.py)
- [tests/cli/test_cli_train.py](tests/cli/test_cli_train.py)

</details>



This page documents the embedding generation system in Lightly, which creates compact numerical representations (embeddings) of images using trained self-supervised models. Embeddings can be used for similarity search, nearest neighbor finding, clustering, or as inputs to the Lightly Platform for dataset curation.

For information about training models that generate embeddings, see [Training Commands](#4.1). For platform integration workflows, see [Platform Integration Commands](#4.3).

## Overview

Embedding generation extracts feature vectors from images by passing them through the backbone of a trained SSL model. The system supports:

- **Pre-trained models**: Use Lightly's model zoo for immediate embedding generation
- **Custom checkpoints**: Load user-trained models from `.ckpt` files
- **Batch processing**: Efficient processing of large image datasets
- **Multiple output formats**: CSV files with embeddings, labels, and filenames

The primary interface is the `lightly-embed` CLI command, though the functionality is also available through the Python API.

Sources: [lightly/cli/embed_cli.py:1-129](), [docs/source/getting_started/command_line_tool.rst:153-182]()

## CLI Command Usage

### Basic Embedding Generation

```bash
# Use pre-trained Lightly model
lightly-embed input_dir=path/to/images

# Use custom checkpoint from training
lightly-embed input_dir=path/to/images checkpoint=model.ckpt

# Use the last trained checkpoint (from environment variable)
lightly-embed input_dir=path/to/images checkpoint=$LIGHTLY_LAST_CHECKPOINT_PATH
```

### Configuration Parameters

The embedding process is controlled by parameters in the Hydra configuration:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `input_dir` | `''` | Path to directory containing images |
| `checkpoint` | `''` | Path to model checkpoint (empty uses pre-trained) |
| `collate.input_size` | `64` | Image resize dimension before embedding |
| `loader.batch_size` | `16` | Batch size for inference |
| `loader.num_workers` | `-1` | Number of CPU cores for data loading (-1 = auto) |
| `model.name` | `'resnet-18'` | Backbone architecture name |
| `model.num_ftrs` | `32` | Embedding dimensionality |
| `model.width` | `1` | ResNet width multiplier |

Sources: [lightly/cli/config/config.yaml:4-38](), [docs/source/getting_started/command_line_tool.rst:155-172]()

## Embedding Generation Pipeline

```mermaid
flowchart TB
    CLI["lightly-embed CLI Entry<br/>embed_cli()"]
    CFG["Load Hydra Config<br/>config.yaml"]
    FIXPATH["Fix Input Paths<br/>fix_input_path()"]
    
    subgraph "Model Loading"
        CKPT_CHECK{"Checkpoint<br/>Specified?"}
        CKPT_LOAD["Load from Checkpoint<br/>torch.load()"]
        PRETRAIN["Download Pre-trained<br/>get_ptmodel_from_config()"]
        MODEL_BUILD["Build Model<br/>ResNetGenerator + _SimCLR"]
        STATE_LOAD["Load State Dict<br/>load_from_state_dict()"]
    end
    
    subgraph "Data Preparation"
        TRANS["Create Transform<br/>Resize + ToTensor + Normalize"]
        DATASET["LightlyDataset<br/>from input_dir"]
        LOADER["DataLoader<br/>shuffle=False, drop_last=False"]
    end
    
    subgraph "Embedding Extraction"
        ENCODER["SelfSupervisedEmbedding"]
        EMBED["encoder.embed()<br/>Pass images through backbone"]
        FEATURES["Extract Features<br/>backbone output"]
    end
    
    subgraph "Output"
        SAVE["save_embeddings()<br/>embeddings.csv"]
        ENV["Set Environment Variable<br/>LIGHTLY_LAST_EMBEDDING_PATH"]
    end
    
    CLI --> CFG
    CFG --> FIXPATH
    FIXPATH --> CKPT_CHECK
    
    CKPT_CHECK -->|Yes| CKPT_LOAD
    CKPT_CHECK -->|No| PRETRAIN
    
    CKPT_LOAD --> MODEL_BUILD
    PRETRAIN --> MODEL_BUILD
    MODEL_BUILD --> STATE_LOAD
    
    STATE_LOAD --> TRANS
    TRANS --> DATASET
    DATASET --> LOADER
    
    LOADER --> ENCODER
    STATE_LOAD --> ENCODER
    ENCODER --> EMBED
    EMBED --> FEATURES
    
    FEATURES --> SAVE
    SAVE --> ENV
```

**Embedding Generation Pipeline Flow**

Sources: [lightly/cli/embed_cli.py:31-90](), [lightly/cli/_helpers.py:199-237]()

## Model and Checkpoint Loading

The embedding system supports multiple model loading strategies:

### Pre-trained Model Zoo

When no checkpoint is specified, the system downloads pre-trained models from the Lightly model zoo based on the configuration:

```python
# Model zoo key construction: {model.name}/simclr/d{num_ftrs}/w{width}
# Example: "resnet-18/simclr/d32/w1"
```

The key is constructed in [lightly/cli/_helpers.py:62-72]() using parameters from `model` configuration namespace.

### Custom Checkpoint Loading

Checkpoints can be loaded from:
- **Local files**: Absolute or relative paths to `.ckpt` files
- **URLs**: Direct download from HTTPS URLs (e.g., Google Cloud Storage)

The loading process handles:
- State dict filtering to remove PyTorch Lightning `model.` prefix
- Backward compatibility with old checkpoint formats (pre-v1.0.6)
- Projection head key transformations for refactored heads

Sources: [lightly/cli/_helpers.py:56-93](), [lightly/cli/_helpers.py:119-197]()

## Model Architecture for Embedding

```mermaid
graph TB
    subgraph "Model Components"
        NORM["BatchNorm Layer<br/>get_norm_layer(3, 0)"]
        RESNET["ResNet Backbone<br/>ResNetGenerator"]
        CONV["1x1 Conv<br/>nn.Conv2d → num_ftrs channels"]
        POOL["Global Average Pooling<br/>nn.AdaptiveAvgPool2d(1)"]
    end
    
    subgraph "Wrapper"
        SIMCLR["_SimCLR Model<br/>features + projection_head"]
        EMBED_WRAP["SelfSupervisedEmbedding<br/>encoder.embed() method"]
    end
    
    IMAGE["Input Image<br/>Resized + Normalized"] --> NORM
    NORM --> RESNET
    RESNET --> CONV
    CONV --> POOL
    POOL --> FEATURES["Feature Vector<br/>num_ftrs dimensions"]
    
    FEATURES --> SIMCLR
    SIMCLR --> EMBED_WRAP
    EMBED_WRAP --> OUTPUT["Embeddings<br/>numpy array"]
    
    NOTE["Note: Projection head<br/>not used for embeddings,<br/>only backbone features"]
```

**Model Architecture Used for Embedding Extraction**

The embedding is extracted from the backbone output (after the 1x1 convolution and pooling), not from the projection head. This is standard practice as the backbone features generalize better to downstream tasks.

Sources: [lightly/cli/_helpers.py:220-236](), [lightly/cli/train_cli.py:93-106]()

## Data Transformation for Inference

Unlike training, embedding generation uses minimal transformations to preserve image content:

```python
# Transform pipeline in embed_cli.py
transform = T.Compose([
    T.Resize((input_size, input_size)),       # Resize to model input size
    T.ToTensor(),                              # Convert to tensor
    T.Normalize(                               # ImageNet normalization
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    ),
])
```

Key differences from training transforms:
- **No augmentations**: No random cropping, color jitter, flipping, or blurring
- **Single view**: Only one view per image (training uses multiple views)
- **Deterministic**: Fixed resize ensures reproducible embeddings
- **Full coverage**: `drop_last=False` ensures all images are embedded

Sources: [lightly/cli/embed_cli.py:56-62](), [lightly/cli/embed_cli.py:66-69]()

## Output Format

### CSV Structure

Embeddings are saved to `embeddings.csv` in the current working directory with the following format:

```csv
filenames,embedding_0,embedding_1,...,embedding_N,labels
image1.jpg,0.123,-0.456,...,0.789,0
image2.jpg,-0.234,0.567,...,-0.123,1
```

| Column | Type | Description |
|--------|------|-------------|
| `filenames` | string | Original image filename |
| `embedding_0` to `embedding_N` | float | Feature vector components (N = `model.num_ftrs`) |
| `labels` | int | Numeric label (from directory structure or enumeration) |

The CSV is written by `save_embeddings()` utility function defined in [lightly/utils/io.py]().

Sources: [lightly/cli/embed_cli.py:82-84](), [docs/source/getting_started/command_line_tool.rst:173-182]()

### Environment Variable

After successful embedding generation, the output path is stored in an environment variable:

```bash
echo $LIGHTLY_LAST_EMBEDDING_PATH
# Output: /path/to/working/directory/embeddings.csv
```

This enables chaining commands in workflows:

```bash
# Train model
lightly-ssl-train input_dir=data/ trainer.max_epochs=10

# Generate embeddings from trained model
lightly-embed input_dir=data/ checkpoint=$LIGHTLY_LAST_CHECKPOINT_PATH

# Use embeddings in subsequent operations
echo $LIGHTLY_LAST_EMBEDDING_PATH
```

Sources: [lightly/cli/embed_cli.py:85-87](), [lightly/cli/config/config.yaml:106-109]()

## Python API Usage

The embedding functionality is accessible programmatically for integration into Python scripts:

### Using the Internal API

```python
from lightly.cli.embed_cli import _embed_cli
from omegaconf import OmegaConf

# Create configuration
cfg = OmegaConf.create({
    'input_dir': 'path/to/images',
    'checkpoint': 'model.ckpt',
    'collate': {'input_size': 224},
    'loader': {'batch_size': 64, 'num_workers': 8, 'shuffle': False, 'drop_last': False},
    'model': {'name': 'resnet-18', 'num_ftrs': 128, 'width': 1, 'out_dim': 128},
    'environment_variable_names': {'lightly_last_embedding_path': 'LIGHTLY_LAST_EMBEDDING_PATH'}
})

# Generate embeddings (returns embeddings, labels, filenames)
embeddings, labels, filenames = _embed_cli(cfg, is_cli_call=False)
```

### Using SelfSupervisedEmbedding Directly

```python
import torch
from lightly.embedding import SelfSupervisedEmbedding
from lightly.data import LightlyDataset
from torchvision import transforms as T

# Load your trained model
model = ...  # Your trained SSL model

# Create encoder
encoder = SelfSupervisedEmbedding(model, None, None, None)

# Prepare dataset and dataloader
transform = T.Compose([
    T.Resize((224, 224)),
    T.ToTensor(),
    T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])
dataset = LightlyDataset('path/to/images', transform=transform)
dataloader = torch.utils.data.DataLoader(dataset, batch_size=64)

# Generate embeddings
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
embeddings, labels, filenames = encoder.embed(dataloader, device=device)
```

Sources: [lightly/cli/embed_cli.py:31-90](), [docs/source/getting_started/lightly_at_a_glance.rst:183-211]()

## Embedding Generation vs Training

```mermaid
graph TB
    subgraph "Training Mode"
        TR_INPUT["Images"]
        TR_AUG["Multiple Augmented Views<br/>SimCLRTransform, etc."]
        TR_MODEL["Full Model<br/>backbone + projection_head"]
        TR_LOSS["Loss Computation<br/>NTXentLoss, etc."]
        TR_BACK["Backward Pass<br/>Update Weights"]
    end
    
    subgraph "Embedding Mode"
        EM_INPUT["Images"]
        EM_TRANS["Minimal Transform<br/>Resize + Normalize only"]
        EM_MODEL["Backbone Only<br/>No projection head"]
        EM_FEAT["Feature Extraction<br/>model.eval() + no_grad()"]
        EM_SAVE["Save to CSV"]
    end
    
    TR_INPUT --> TR_AUG
    TR_AUG --> TR_MODEL
    TR_MODEL --> TR_LOSS
    TR_LOSS --> TR_BACK
    
    EM_INPUT --> EM_TRANS
    EM_TRANS --> EM_MODEL
    EM_MODEL --> EM_FEAT
    EM_FEAT --> EM_SAVE
    
    style TR_INPUT fill:#f9f9f9
    style EM_INPUT fill:#f9f9f9
```

**Comparison of Training vs Embedding Mode**

| Aspect | Training | Embedding |
|--------|----------|-----------|
| Transforms | Multiple augmented views | Single minimal transform |
| Batch preparation | `MultiViewCollate` | Standard collate |
| Model components | Backbone + projection head | Backbone only |
| Model mode | `train()` | `eval()` |
| Gradient computation | Enabled | Disabled (`torch.no_grad()`) |
| Shuffle data | True | False |
| Drop last batch | True | False |
| Output | Model checkpoint | Embeddings CSV |

Sources: [lightly/cli/embed_cli.py:56-69](), [lightly/cli/train_cli.py:111-118](), [lightly/cli/lightly_cli.py:20-35]()

## Common Use Cases

### 1. Zero-shot Embedding with Pre-trained Models

Generate embeddings immediately without training:

```bash
lightly-embed input_dir=my_images collate.input_size=224
```

This downloads and uses a pre-trained ResNet-18 model from the Lightly model zoo.

### 2. Embedding After Training

Use a checkpoint from a training run:

```bash
# Train
lightly-ssl-train input_dir=data/ trainer.max_epochs=50

# Embed with trained model
lightly-embed input_dir=data/ checkpoint=$LIGHTLY_LAST_CHECKPOINT_PATH
```

### 3. Using lightly-magic

The `lightly-magic` command combines training and embedding in one step:

```bash
lightly-magic input_dir=data/ trainer.max_epochs=10
```

This internally calls:
1. `_train_cli()` to train the model
2. `_embed_cli()` with the trained checkpoint

Sources: [lightly/cli/lightly_cli.py:20-38](), [docs/source/getting_started/command_line_tool.rst:84-108]()

## Implementation Details

### Checkpoint State Dict Processing

The system handles several checkpoint compatibility issues:

1. **PyTorch Lightning prefix removal**: Removes `model.` prefix from keys
2. **Backbone renaming**: Converts old `features` backbone name to `backbone`
3. **Projection head refactoring**: Inserts `layers` into projection head keys for backward compatibility

These transformations are applied in [lightly/cli/_helpers.py:119-172]().

### Automatic CPU Core Detection

When `loader.num_workers=-1`, the system automatically detects available CPU cores:

```python
if cfg["loader"]["num_workers"] < 0:
    cfg["loader"]["num_workers"] = cpu_count()
```

This ensures optimal data loading performance without manual configuration.

Sources: [lightly/cli/embed_cli.py:71-73](), [lightly/cli/_helpers.py:20-26]()

### Device Selection

The system automatically selects the best available device:

```python
if torch.cuda.is_available():
    device = torch.device("cuda")
else:
    device = torch.device("cpu")
```

All embedding computation happens on the selected device for optimal performance.

Sources: [lightly/cli/embed_cli.py:51-54]()

## Integration with lightly-magic

The `lightly-magic` command provides a streamlined workflow that combines training and embedding:

```mermaid
sequenceDiagram
    participant User
    participant Magic as lightly_cli()
    participant Train as _train_cli()
    participant Embed as _embed_cli()
    participant FS as File System
    
    User->>Magic: lightly-magic input_dir=data/<br/>trainer.max_epochs=10
    
    Magic->>Magic: Set shuffle=True, drop_last=True
    
    alt max_epochs > 0
        Magic->>Train: Train model
        Train->>FS: Save checkpoint
        Train-->>Magic: Return checkpoint path
    end
    
    Magic->>Magic: Set shuffle=False, drop_last=False<br/>cfg.checkpoint = trained_checkpoint
    
    Magic->>Embed: Generate embeddings
    Embed->>FS: Save embeddings.csv
    Embed-->>Magic: Return embedding path
    
    Magic->>User: Finished
```

**lightly-magic Workflow Sequence**

Sources: [lightly/cli/lightly_cli.py:20-38](), [docs/source/getting_started/command_line_tool.rst:210-228]()

---

# Page: Platform Integration Commands

# Platform Integration Commands

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/source/getting_started/advanced.rst](docs/source/getting_started/advanced.rst)
- [docs/source/getting_started/command_line_tool.rst](docs/source/getting_started/command_line_tool.rst)
- [docs/source/getting_started/images/lightly_overview.png](docs/source/getting_started/images/lightly_overview.png)
- [docs/source/getting_started/install.rst](docs/source/getting_started/install.rst)
- [docs/source/getting_started/lightly_at_a_glance.rst](docs/source/getting_started/lightly_at_a_glance.rst)
- [docs/source/getting_started/main_concepts.rst](docs/source/getting_started/main_concepts.rst)
- [docs/source/index.rst](docs/source/index.rst)
- [docs/source/lightly.models.utils.rst](docs/source/lightly.models.utils.rst)
- [lightly/cli/__init__.py](lightly/cli/__init__.py)
- [lightly/cli/_helpers.py](lightly/cli/_helpers.py)
- [lightly/cli/config/config.yaml](lightly/cli/config/config.yaml)
- [lightly/cli/download_cli.py](lightly/cli/download_cli.py)
- [lightly/cli/embed_cli.py](lightly/cli/embed_cli.py)
- [lightly/cli/lightly_cli.py](lightly/cli/lightly_cli.py)
- [lightly/cli/train_cli.py](lightly/cli/train_cli.py)
- [requirements/base.txt](requirements/base.txt)
- [setup.py](setup.py)
- [tests/cli/test_cli_download.py](tests/cli/test_cli_download.py)
- [tests/cli/test_cli_magic.py](tests/cli/test_cli_magic.py)
- [tests/cli/test_cli_train.py](tests/cli/test_cli_train.py)
- [tests/embedding/test_embedding.py](tests/embedding/test_embedding.py)

</details>



This page documents the command-line interface (CLI) commands for interacting with the Lightly Platform. These commands enable downloading datasets and tags from the platform, uploading data, and preprocessing images for self-supervised learning workflows. For information about training models, see [Training Commands](#4.1). For embedding generation, see [Embedding Generation](#4.2). For configuration details, see [CLI Configuration](#4.4).

## Overview

The Lightly CLI provides commands to bridge local training workflows with the Lightly Platform's dataset management and selection capabilities. The primary integration commands are:

- **`lightly-download`**: Download tagged samples, file lists, or full datasets from the platform
- **`lightly-crop`**: Preprocess images by cropping objects based on YOLO-format labels
- **Platform configuration parameters**: Token-based authentication and dataset management settings

All platform integration commands use the `ApiWorkflowClient` internally (see [API Workflow Client](#6.1)) to communicate with the Lightly Platform REST API.

Sources: [lightly/cli/download_cli.py:1-135](), [lightly/cli/config/config.yaml:13-27](), [docs/source/getting_started/command_line_tool.rst:183-209]()

## Command Architecture

```mermaid
graph TB
    subgraph "CLI Commands"
        DOWNLOAD["lightly-download<br/>download_cli()"]
        CROP["lightly-crop<br/>crop_cli()"]
    end
    
    subgraph "Configuration"
        CONFIG["config.yaml<br/>Hydra configuration"]
        ENV["Environment Variables<br/>LIGHTLY_LAST_*"]
    end
    
    subgraph "API Layer"
        CLIENT["ApiWorkflowClient<br/>token, dataset_id"]
        MIXINS["Mixins:<br/>_DatasourcesMixin<br/>_TagsMixin<br/>_DownloadDatasetMixin"]
    end
    
    subgraph "Platform Operations"
        API_GET["GET /tags<br/>GET /samples"]
        API_DOWNLOAD["Download images<br/>from datasource"]
        LOCAL_COPY["Copy files<br/>from input_dir"]
    end
    
    subgraph "Outputs"
        TXT["tag_name.txt<br/>List of filenames"]
        IMAGES["output_dir/<br/>Downloaded images"]
        CROPPED["cropped_images/<br/>Preprocessed data"]
    end
    
    DOWNLOAD --> CONFIG
    CROP --> CONFIG
    CONFIG --> ENV
    
    DOWNLOAD --> CLIENT
    CLIENT --> MIXINS
    
    MIXINS --> API_GET
    MIXINS --> API_DOWNLOAD
    DOWNLOAD --> LOCAL_COPY
    
    API_GET --> TXT
    API_DOWNLOAD --> IMAGES
    LOCAL_COPY --> IMAGES
    CROP --> CROPPED
    
    CROPPED -.input to.-> DOWNLOAD
```

Sources: [lightly/cli/download_cli.py:1-135](), [lightly/api/api_workflow_client.py](), [lightly/cli/config/config.yaml:1-160]()

## lightly-download Command

The `lightly-download` command retrieves data from the Lightly Platform based on dataset tags. It supports three distinct modes of operation.

### Command Signature

```bash
lightly-download \
    tag_name=<tag_name> \
    dataset_id=<dataset_id> \
    token=<token> \
    [input_dir=<path>] \
    [output_dir=<path>] \
    [exclude_parent_tag=<bool>]
```

Sources: [lightly/cli/download_cli.py:22-82](), [docs/source/getting_started/command_line_tool.rst:183-209]()

### Required Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `token` | User access token for platform authentication | `token='your_access_token'` |
| `dataset_id` | Unique identifier of the dataset on the platform | `dataset_id='XYZ123'` |
| `tag_name` | Name of the tag to download (defaults to `'initial-tag'`) | `tag_name='my-tag'` |

Sources: [lightly/cli/download_cli.py:23-26](), [lightly/cli/config/config.yaml:16-26]()

### Optional Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `input_dir` | Local directory containing original images | `''` (empty) |
| `output_dir` | Target directory for downloaded/copied images | `''` (empty) |
| `exclude_parent_tag` | Exclude samples from parent tag | `False` |
| `loader.num_workers` | Number of parallel download workers | Auto-detected (8-32) |

Sources: [lightly/cli/download_cli.py:34-41](), [lightly/cli/config/config.yaml:5-26]()

### Operation Modes

```mermaid
graph TB
    START["lightly-download command"]
    
    CHECK_PARAMS{"Check parameters"}
    
    MODE1["Mode 1: List Only<br/>No input_dir, no output_dir"]
    MODE2["Mode 2: Download Images<br/>output_dir only"]
    MODE3["Mode 3: Copy Local<br/>input_dir + output_dir"]
    
    API["ApiWorkflowClient<br/>get_tag_by_name()"]
    FILENAMES["get_filenames_in_tag()<br/>exclude_parent_tag"]
    
    OUT1["tag_name.txt<br/>List of filenames"]
    OUT2["output_dir/<br/>Downloaded from platform"]
    OUT3["output_dir/<br/>Copied from input_dir"]
    
    START --> CHECK_PARAMS
    CHECK_PARAMS --> MODE1
    CHECK_PARAMS --> MODE2
    CHECK_PARAMS --> MODE3
    
    MODE1 --> API
    MODE2 --> API
    MODE3 --> API
    
    API --> FILENAMES
    
    FILENAMES --> OUT1
    MODE2 --> OUT2
    MODE3 --> OUT3
    
    OUT1 -.always created.-> OUT2
    OUT1 -.always created.-> OUT3
```

Sources: [lightly/cli/download_cli.py:42-82]()

#### Mode 1: Download Filename List Only

When neither `input_dir` nor `output_dir` is specified, the command downloads only the list of filenames in the tag and saves it to a `.txt` file.

```bash
# Download list of all files in the dataset
lightly-download tag_name='initial-tag' dataset_id='XYZ' token='123'

# Download list of files in a specific tag
lightly-download tag_name='my-tag' dataset_id='XYZ' token='123'
```

**Output**: Creates `{tag_name}.txt` in the current working directory containing one filename per line.

Sources: [lightly/cli/download_cli.py:53-61](), [docs/source/getting_started/command_line_tool.rst:198-201]()

#### Mode 2: Download Images from Platform

When `output_dir` is specified but `input_dir` is not, the command downloads the actual images from the platform's datasource.

```bash
# Download images to output directory
lightly-download tag_name='my-tag' dataset_id='XYZ' token='123' \
    output_dir='my_data/'
```

This uses the `ApiWorkflowClient.download_dataset()` method to retrieve images directly from the configured datasource (S3, Azure, GCS, or local storage).

Sources: [lightly/cli/download_cli.py:63-68](), [docs/source/getting_started/command_line_tool.rst:202-204]()

#### Mode 3: Copy Images from Local Directory

When both `input_dir` and `output_dir` are specified, the command copies files from the local input directory to the output directory based on the tag's file list.

```bash
# Copy tagged files from local directory
lightly-download tag_name='my-tag' dataset_id='XYZ' token='123' \
    input_dir='data/' output_dir='my_data/'
```

This mode is efficient for extracting subsets from large local datasets without re-downloading from the platform.

Sources: [lightly/cli/download_cli.py:70-82](), [docs/source/getting_started/command_line_tool.rst:206-208]()

### Implementation Details

The download command implementation uses the following workflow:

1. **Validation**: Check that `tag_name`, `token`, and `dataset_id` are provided [lightly/cli/download_cli.py:27-32]()
2. **Worker Configuration**: Auto-detect optimal number of workers (8-32) if not specified [lightly/cli/download_cli.py:34-40]()
3. **API Client Initialization**: Create `ApiWorkflowClient` with authentication [lightly/cli/download_cli.py:42-44]()
4. **Tag Resolution**: Retrieve tag data by name using `get_tag_by_name()` [lightly/cli/download_cli.py:47]()
5. **Filename Retrieval**: Get list of filenames in tag with optional parent exclusion [lightly/cli/download_cli.py:48-51]()
6. **File List Export**: Always write filenames to `{tag_name}.txt` [lightly/cli/download_cli.py:53-61]()
7. **Image Retrieval**: Download or copy images based on specified directories [lightly/cli/download_cli.py:63-82]()

Sources: [lightly/cli/download_cli.py:22-82]()

### Excluding Parent Tags

The `exclude_parent_tag` parameter filters out samples that exist in both the specified tag and its parent tag, returning only samples unique to the specified tag.

```bash
# Download only samples in 'my-tag' but not in its parent
lightly-download tag_name='my-tag' dataset_id='XYZ' token='123' \
    exclude_parent_tag=True
```

Sources: [lightly/cli/download_cli.py:48-51](), [lightly/cli/config/config.yaml:26](), [docs/source/getting_started/command_line_tool.rst:148-149]()

### Error Handling

The command includes validation and error handling for common issues:

| Scenario | Behavior |
|----------|----------|
| Missing `token`, `dataset_id`, or `tag_name` | Prints warning and returns without action |
| Tag name not found | Raises `ValueError` (from `get_tag_by_name()`) |
| Integer tag name | Correctly converts to string (fixes issue #575) |

Sources: [lightly/cli/download_cli.py:27-32](), [tests/cli/test_cli_download.py:77-82](), [tests/cli/test_cli_download.py:117-129]()

## lightly-crop Command

The `lightly-crop` command preprocesses datasets by cropping objects from images based on YOLO-format bounding box labels. This is useful for object-centric self-supervised learning where features should focus on individual objects rather than full scenes.

### Command Signature

```bash
lightly-crop \
    input_dir=<images> \
    label_dir=<labels> \
    output_dir=<cropped_images> \
    [crop_padding=<float>] \
    [label_names_file=<path>]
```

Sources: [docs/source/getting_started/command_line_tool.rst:42-80](), [lightly/cli/config/config.yaml:30]()

### Parameters

| Parameter | Description | Default | Example |
|-----------|-------------|---------|---------|
| `input_dir` | Directory containing input images | Required | `input_dir=images` |
| `label_dir` | Directory containing YOLO-format label files | Required | `label_dir=labels` |
| `output_dir` | Directory to store cropped images | Required | `output_dir=cropped_images` |
| `crop_padding` | Padding around bounding box (fraction) | `0.1` | `crop_padding=0.2` |
| `label_names_file` | YAML file with class names | Optional | `label_names_file=data.yaml` |

Sources: [lightly/cli/config/config.yaml:30](), [docs/source/getting_started/command_line_tool.rst:56-63]()

### YOLO Label Format

Each image must have a corresponding `.txt` file with the same base name. Each line in the label file represents one object:

```
class_id x_center y_center width height
```

Where coordinates are normalized to [0, 1] relative to image dimensions.

**Example label file (`image_001.txt`):**
```text
0 0.23 0.14 0.05 0.04
1 0.43 0.13 0.12 0.08
```

Sources: [docs/source/getting_started/command_line_tool.rst:66-74]()

### Class Names File

Optional YAML file mapping class IDs to human-readable names. When provided, class names are included in output filenames.

**Example `data.yaml`:**
```yaml
names: [cat, dog, car]
```

Sources: [docs/source/getting_started/command_line_tool.rst:76-79]()

### Usage Examples

```bash
# Basic cropping with 20% padding
lightly-crop input_dir=images label_dir=labels output_dir=cropped_images \
    crop_padding=0.2

# Cropping with class names in output filenames
lightly-crop input_dir=images label_dir=labels output_dir=cropped_images \
    label_names_file=data.yaml
```

The cropped images can be used as input for training commands:

```bash
# Use cropped images for training
lightly-ssl-train input_dir=cropped_images trainer.max_epochs=10
```

Sources: [docs/source/getting_started/command_line_tool.rst:56-82]()

### Preprocessing Workflow

```mermaid
graph LR
    INPUT["input_dir/<br/>Original images"]
    LABELS["label_dir/<br/>YOLO labels"]
    NAMES["label_names_file<br/>Class names YAML"]
    
    CROP["lightly-crop<br/>crop_cli()"]
    
    OUTPUT["output_dir/<br/>Cropped objects"]
    
    TRAIN["lightly-ssl-train<br/>Train on objects"]
    
    INPUT --> CROP
    LABELS --> CROP
    NAMES -.optional.-> CROP
    
    CROP --> OUTPUT
    OUTPUT --> TRAIN
```

Sources: [docs/source/getting_started/command_line_tool.rst:42-82]()

## Platform Configuration Parameters

Platform integration requires several configuration parameters in `config.yaml` or as command-line overrides.

### Authentication Parameters

```yaml
# Lightly platform authentication
token: ''                     # User access token to the Lightly platform
dataset_id: ''                # Identifier of the dataset on the Lightly platform
```

These parameters are required for all platform operations. The token authenticates API requests, and the dataset_id specifies which dataset to operate on.

Sources: [lightly/cli/config/config.yaml:16-17]()

### Dataset Management Parameters

```yaml
# Dataset creation and modification
new_dataset_name: ''          # Name of the new dataset to be created
append: False                 # True to append samples to existing dataset
tag_name: 'initial-tag'       # Name of the tag to download/operate on
exclude_parent_tag: False     # Exclude samples from parent tag
```

Sources: [lightly/cli/config/config.yaml:18-26]()

### Upload Configuration

```yaml
# Image upload settings
upload: 'full'                # Upload mode: 'full', 'thumbnails', 'none'
resize: -1                    # Resize images before upload: -1, x, or [x,y]
```

The `upload` parameter controls what gets uploaded to the platform:
- `'full'`: Upload full-resolution images
- `'thumbnails'`: Upload thumbnail versions only
- `'none'`: Upload metadata only (no image data)

Sources: [lightly/cli/config/config.yaml:19-22]()

### Embedding Upload Parameters

```yaml
# Embedding configuration
embedding_name: 'default'     # Name for the embedding on the platform
emb_upload_bsz: 32           # Batch size for embedding uploads
```

When embeddings are uploaded to the platform (typically after running `lightly-embed`), these parameters control the upload behavior.

Sources: [lightly/cli/config/config.yaml:23-24]()

### Environment Variables

The CLI uses environment variables to track outputs and chain commands:

| Variable | Purpose | Set By |
|----------|---------|--------|
| `LIGHTLY_LAST_CHECKPOINT_PATH` | Path to most recent checkpoint | `lightly-ssl-train` |
| `LIGHTLY_LAST_EMBEDDING_PATH` | Path to most recent embeddings CSV | `lightly-embed` |
| `LIGHTLY_LAST_DATASET_ID` | Most recently created/used dataset ID | Various commands |

These enable command chaining without manually specifying paths:

```bash
# Train model
lightly-ssl-train input_dir=data/ trainer.max_epochs=10

# Embed using the trained model
lightly-embed input_dir=data/ checkpoint=$LIGHTLY_LAST_CHECKPOINT_PATH
```

Sources: [lightly/cli/config/config.yaml:105-109](), [lightly/cli/train_cli.py:149-152](), [lightly/cli/embed_cli.py:85-87]()

## Platform Integration Workflows

### End-to-End Workflow with Platform

```mermaid
graph TB
    subgraph "1. Download Data"
        DL["lightly-download<br/>tag_name='initial-tag'"]
        DATA["output_dir/<br/>Downloaded images"]
    end
    
    subgraph "2. Preprocess (Optional)"
        CROP["lightly-crop<br/>Extract objects"]
        CROPPED["cropped_images/"]
    end
    
    subgraph "3. Train Model"
        TRAIN["lightly-ssl-train<br/>trainer.max_epochs=100"]
        CKPT["checkpoint.ckpt<br/>$LIGHTLY_LAST_CHECKPOINT_PATH"]
    end
    
    subgraph "4. Generate Embeddings"
        EMBED["lightly-embed<br/>checkpoint=$LIGHTLY_LAST_CHECKPOINT_PATH"]
        EMB["embeddings.csv<br/>$LIGHTLY_LAST_EMBEDDING_PATH"]
    end
    
    subgraph "5. Upload & Select (API)"
        UPLOAD["ApiWorkflowClient<br/>upload_embeddings()"]
        SELECT["Platform Selection<br/>CORESET, diversity, etc."]
    end
    
    subgraph "6. Download Selected"
        DL2["lightly-download<br/>tag_name='selected-subset'"]
        SUBSET["output_dir/<br/>Selected images"]
    end
    
    DL --> DATA
    DATA --> CROP
    CROP --> CROPPED
    CROPPED --> TRAIN
    DATA -.skip crop.-> TRAIN
    
    TRAIN --> CKPT
    CKPT --> EMBED
    EMBED --> EMB
    
    EMB --> UPLOAD
    UPLOAD --> SELECT
    SELECT --> DL2
    DL2 --> SUBSET
```

Sources: [docs/source/getting_started/command_line_tool.rst:1-237](), [lightly/cli/download_cli.py:1-135]()

### Typical Command Sequence

```bash
# Step 1: Download initial dataset from platform
lightly-download \
    tag_name='initial-tag' \
    dataset_id='abc123' \
    token='your_token' \
    output_dir='raw_data/'

# Step 2: (Optional) Crop objects for object-centric learning
lightly-crop \
    input_dir='raw_data/' \
    label_dir='labels/' \
    output_dir='cropped_data/' \
    crop_padding=0.2

# Step 3: Train self-supervised model
lightly-ssl-train \
    input_dir='cropped_data/' \
    trainer.max_epochs=100 \
    loader.batch_size=128

# Step 4: Generate embeddings
lightly-embed \
    input_dir='cropped_data/' \
    checkpoint=$LIGHTLY_LAST_CHECKPOINT_PATH

# Step 5: Upload embeddings to platform (via Python API)
# See API Workflow Client documentation

# Step 6: Download selected subset after platform selection
lightly-download \
    tag_name='active-learning-selected' \
    dataset_id='abc123' \
    token='your_token' \
    input_dir='raw_data/' \
    output_dir='selected_subset/'
```

Sources: [docs/source/getting_started/command_line_tool.rst:145-209](), [docs/source/lightly.cli.rst]()

### Iterative Active Learning Loop

```bash
# Initial dataset download
lightly-download tag_name='initial-tag' dataset_id='XYZ' token='123' \
    output_dir='iteration_0/'

# Iteration 1: Train and select
lightly-ssl-train input_dir='iteration_0/' trainer.max_epochs=50
lightly-embed input_dir='iteration_0/' checkpoint=$LIGHTLY_LAST_CHECKPOINT_PATH
# Upload embeddings via API and run selection strategy

# Download newly selected samples
lightly-download tag_name='iteration_1' dataset_id='XYZ' token='123' \
    output_dir='iteration_1/'

# Iteration 2: Train on expanded dataset
lightly-ssl-train input_dir='iteration_1/' trainer.max_epochs=50
# ... repeat
```

Sources: [docs/source/getting_started/command_line_tool.rst:1-237]()

## Integration with API Client

While the CLI commands provide a simple interface for common operations, more advanced platform features require direct use of the `ApiWorkflowClient` (see [API Workflow Client](#6.1)). The CLI commands internally use this client:

```python
# Internal implementation of lightly-download
from lightly.api.api_workflow_client import ApiWorkflowClient

api_workflow_client = ApiWorkflowClient(
    token=token, 
    dataset_id=dataset_id,
    creator=Creator.USER_PIP_LIGHTLY_MAGIC
)

# Get tag data
tag_data = api_workflow_client.get_tag_by_name(tag_name)

# Get filenames in tag
filenames = api_workflow_client.get_filenames_in_tag(
    tag_data,
    exclude_parent_tag=cfg["exclude_parent_tag"],
)

# Download images
api_workflow_client.download_dataset(
    output_dir, 
    tag_name=tag_name, 
    max_workers=cfg["loader"]["num_workers"]
)
```

For operations not exposed through CLI commands (such as uploading embeddings, configuring datasources, or managing compute workers), use the Python API directly.

Sources: [lightly/cli/download_cli.py:42-68]()

## Summary

Platform integration commands bridge the gap between local training workflows and cloud-based dataset management:

| Command | Primary Use Case | Output |
|---------|-----------------|--------|
| `lightly-download` | Retrieve tagged samples from platform | File list or images |
| `lightly-crop` | Preprocess images for object-centric learning | Cropped object images |

These commands work in conjunction with training commands ([Training Commands](#4.1)) and embedding generation ([Embedding Generation](#4.2)) to enable complete active learning and dataset curation workflows. All platform operations require authentication via `token` and `dataset_id` parameters, which can be set in the Hydra configuration file or as command-line overrides (see [CLI Configuration](#4.4)).

For programmatic access to platform features beyond what the CLI exposes, use the `ApiWorkflowClient` directly (see [Platform Integration](#6)).

Sources: [lightly/cli/download_cli.py:1-135](), [docs/source/getting_started/command_line_tool.rst:1-237](), [lightly/cli/config/config.yaml:1-160]()

---

# Page: CLI Configuration

# CLI Configuration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [lightly/cli/_helpers.py](lightly/cli/_helpers.py)
- [lightly/cli/config/config.yaml](lightly/cli/config/config.yaml)
- [lightly/cli/embed_cli.py](lightly/cli/embed_cli.py)
- [lightly/cli/lightly_cli.py](lightly/cli/lightly_cli.py)
- [lightly/cli/train_cli.py](lightly/cli/train_cli.py)
- [tests/cli/test_cli_magic.py](tests/cli/test_cli_magic.py)
- [tests/cli/test_cli_train.py](tests/cli/test_cli_train.py)

</details>



This document describes the Hydra-based configuration system used by the Lightly CLI tools. It covers the structure of `config.yaml`, parameter override mechanisms, environment variable management, and Hydra integration specifics.

For information about the CLI commands that use this configuration system, see [Training Commands](#4.1) and [Embedding Generation](#4.2). For platform-specific configuration, see [Platform Integration Commands](#4.3).

## Overview

The Lightly CLI uses [Hydra](https://hydra.cc/) for hierarchical configuration management. All CLI commands (`lightly-ssl-train`, `lightly-embed`, `lightly-magic`) load their default configuration from [lightly/cli/config/config.yaml:1-160]() and accept parameter overrides via command-line arguments. The configuration is organized into logical namespaces that map directly to Python objects used during training and embedding.

Sources: [lightly/cli/config/config.yaml:1-160](), [lightly/cli/train_cli.py:155-183](), [lightly/cli/embed_cli.py:93-124]()

## Configuration File Structure

The configuration file is organized into hierarchical namespaces, each controlling a specific aspect of the training or embedding pipeline.

### Configuration Namespace Overview

```mermaid
graph TB
    subgraph "Input/Output Configuration"
        IO["I/O Paths<br/>lines 1-11"]
        IO_INPUT["input_dir<br/>output_dir<br/>embeddings<br/>checkpoint<br/>label_dir"]
    end
    
    subgraph "Platform Configuration"
        PLATFORM["Lightly Platform<br/>lines 13-26"]
        PLATFORM_PARAMS["token<br/>dataset_id<br/>new_dataset_name<br/>upload<br/>embedding_name"]
    end
    
    subgraph "Model & Training Configuration"
        MODEL["model namespace<br/>lines 33-38"]
        CRITERION["criterion namespace<br/>lines 41-44"]
        OPTIMIZER["optimizer namespace<br/>lines 47-49"]
        
        MODEL_PARAMS["name: resnet-18<br/>out_dim: 128<br/>num_ftrs: 32<br/>width: 1"]
        CRITERION_PARAMS["temperature: 0.5<br/>memory_bank_size: 0"]
        OPTIMIZER_PARAMS["lr: 1.0<br/>weight_decay: 0.00001"]
    end
    
    subgraph "Data Pipeline Configuration"
        COLLATE["collate namespace<br/>lines 52-74"]
        LOADER["loader namespace<br/>lines 77-83"]
        
        COLLATE_PARAMS["input_size: 64<br/>cj_prob: 0.8<br/>min_scale: 0.15<br/>gaussian_blur: 0.5"]
        LOADER_PARAMS["batch_size: 16<br/>shuffle: True<br/>num_workers: -1<br/>drop_last: True"]
    end
    
    subgraph "Training Control Configuration"
        TRAINER["trainer namespace<br/>lines 86-92"]
        CHECKPOINT["checkpoint_callback namespace<br/>lines 95-99"]
        
        TRAINER_PARAMS["gpus: 1<br/>max_epochs: 100<br/>precision: 32"]
        CHECKPOINT_PARAMS["save_last: True<br/>save_top_k: 1<br/>dirpath: None"]
    end
    
    subgraph "System Configuration"
        ENV["environment_variable_names<br/>lines 106-109"]
        SEED["seed: 1<br/>line 112"]
        HYDRA["hydra namespace<br/>lines 114-160"]
        
        ENV_PARAMS["lightly_last_checkpoint_path<br/>lightly_last_embedding_path<br/>lightly_last_dataset_id"]
        HYDRA_PARAMS["run.dir<br/>help.header<br/>help.footer"]
    end
    
    IO --> IO_INPUT
    PLATFORM --> PLATFORM_PARAMS
    MODEL --> MODEL_PARAMS
    CRITERION --> CRITERION_PARAMS
    OPTIMIZER --> OPTIMIZER_PARAMS
    COLLATE --> COLLATE_PARAMS
    LOADER --> LOADER_PARAMS
    TRAINER --> TRAINER_PARAMS
    CHECKPOINT --> CHECKPOINT_PARAMS
    ENV --> ENV_PARAMS
    HYDRA --> HYDRA_PARAMS
```

Sources: [lightly/cli/config/config.yaml:1-160]()

### Core Configuration Namespaces

The following table summarizes each configuration namespace and its purpose:

| Namespace | Purpose | Passed To | Key Parameters |
|-----------|---------|-----------|----------------|
| `model` | Model architecture configuration | `lightly.models.ResNetGenerator` | `name`, `out_dim`, `num_ftrs`, `width` |
| `criterion` | Loss function configuration | `lightly.loss.NTXentLoss` | `temperature`, `memory_bank_size` |
| `optimizer` | Optimizer settings | `torch.optim.SGD` | `lr`, `weight_decay` |
| `collate` | Data augmentation pipeline | `lightly.data.ImageCollateFunction` | `input_size`, `cj_prob`, `min_scale`, `gaussian_blur` |
| `loader` | DataLoader settings | `torch.utils.data.DataLoader` | `batch_size`, `shuffle`, `num_workers`, `drop_last` |
| `trainer` | PyTorch Lightning trainer | `pytorch_lightning.Trainer` | `gpus`, `max_epochs`, `precision` |
| `checkpoint_callback` | Checkpoint saving behavior | Checkpoint callback config | `save_last`, `save_top_k`, `dirpath` |
| `summary_callback` | Model summary depth | Summary callback config | `max_depth` |
| `environment_variable_names` | Environment variable tracking | System environment | `lightly_last_checkpoint_path`, etc. |

Sources: [lightly/cli/config/config.yaml:33-103](), [lightly/cli/train_cli.py:93-144]()

### Configuration to Code Mapping

```mermaid
graph LR
    subgraph "config.yaml Namespaces"
        CFG_MODEL["model:<br/>name, out_dim, num_ftrs, width"]
        CFG_CRITERION["criterion:<br/>temperature, memory_bank_size"]
        CFG_OPTIMIZER["optimizer:<br/>lr, weight_decay"]
        CFG_COLLATE["collate:<br/>input_size, cj_prob, etc."]
        CFG_LOADER["loader:<br/>batch_size, num_workers"]
        CFG_TRAINER["trainer:<br/>gpus, max_epochs, precision"]
    end
    
    subgraph "Python Code Usage"
        CODE_MODEL["ResNetGenerator(**cfg['model'])<br/>_helpers.py:93, 220"]
        CODE_CRITERION["NTXentLoss(**cfg['criterion'])<br/>train_cli.py:108"]
        CODE_OPTIMIZER["torch.optim.SGD(**cfg['optimizer'])<br/>train_cli.py:109"]
        CODE_COLLATE["ImageCollateFunction(**cfg['collate'])<br/>train_cli.py:115"]
        CODE_LOADER["DataLoader(**cfg['loader'])<br/>train_cli.py:116-118"]
        CODE_TRAINER["SelfSupervisedEmbedding<br/>.train_embedding(trainer_config)<br/>train_cli.py:140-144"]
    end
    
    CFG_MODEL --> CODE_MODEL
    CFG_CRITERION --> CODE_CRITERION
    CFG_OPTIMIZER --> CODE_OPTIMIZER
    CFG_COLLATE --> CODE_COLLATE
    CFG_LOADER --> CODE_LOADER
    CFG_TRAINER --> CODE_TRAINER
```

Sources: [lightly/cli/train_cli.py:93-144](), [lightly/cli/_helpers.py:93-237](), [lightly/cli/embed_cli.py:56-75]()

## Parameter Override System

Hydra allows overriding any configuration parameter via command-line arguments using dot notation. Parameters are specified as `key=value` or `namespace.key=value`.

### Override Syntax

The general syntax for parameter overrides:

```bash
lightly-<command> <config_path>=<value> [<namespace>.<key>=<value> ...]
```

Examples of valid override patterns:

```bash
# Top-level parameters
lightly-ssl-train input_dir=data/ checkpoint=model.ckpt

# Nested parameters using dot notation
lightly-ssl-train input_dir=data/ loader.batch_size=128

# Multiple overrides
lightly-ssl-train input_dir=data/ trainer.max_epochs=50 loader.batch_size=64

# Deep nesting
lightly-ssl-train input_dir=data/ collate.input_size=224 collate.cj_prob=0.9
```

Sources: [lightly/cli/config/config.yaml:127-149](), [lightly/cli/train_cli.py:156-183]()

### Common Override Patterns

The following table shows frequently used parameter overrides and their effects:

| Override | Default | Purpose | Example |
|----------|---------|---------|---------|
| `input_dir` | `''` | Specify input image directory | `input_dir=./my_dataset` |
| `loader.batch_size` | `16` | Control training batch size | `loader.batch_size=128` |
| `trainer.max_epochs` | `100` | Set training duration | `trainer.max_epochs=50` |
| `collate.input_size` | `64` | Set input image resolution | `collate.input_size=224` |
| `model.name` | `resnet-18` | Choose backbone architecture | `model.name=resnet-50` |
| `model.num_ftrs` | `32` | Set embedding dimension | `model.num_ftrs=512` |
| `trainer.precision` | `32` | Enable mixed precision | `trainer.precision=16` |
| `checkpoint` | `''` | Resume from checkpoint | `checkpoint=path/to/ckpt` |
| `pre_trained` | `True` | Use pre-trained weights | `pre_trained=False` |
| `loader.num_workers` | `-1` | Set data loader workers | `loader.num_workers=8` |

Sources: [lightly/cli/config/config.yaml:1-112](), [lightly/cli/train_cli.py:37-152]()

### Special Value Handling

Some parameters have special value interpretations:

- **`loader.num_workers = -1`**: Automatically uses `os.cpu_count()` to determine optimal worker count [lightly/cli/_helpers.py:20-26](), [lightly/cli/train_cli.py:66-67]()
- **`checkpoint = ''`**: When empty and `pre_trained=True`, downloads pre-trained model from model zoo [lightly/cli/train_cli.py:71-80]()
- **`trainer.gpus`**: Deprecated in PyTorch Lightning 2.0+, automatically converted to `accelerator` and `devices` [lightly/cli/train_cli.py:128-137]()
- **`collate.kernel_size = null`**: Deprecated in favor of `sigmas` parameter [lightly/cli/config/config.yaml:63-65]()

Sources: [lightly/cli/train_cli.py:66-80](), [lightly/cli/_helpers.py:20-26](), [lightly/cli/config/config.yaml:63-65]()

## Environment Variables

The CLI uses environment variables to track outputs and enable command chaining. These variables are set automatically after successful execution.

### Output Tracking Variables

```mermaid
graph TB
    subgraph "CLI Commands"
        TRAIN["lightly-ssl-train"]
        EMBED["lightly-embed"]
        MAGIC["lightly-magic"]
    end
    
    subgraph "Environment Variables"
        ENV_CKPT["LIGHTLY_LAST_CHECKPOINT_PATH"]
        ENV_EMB["LIGHTLY_LAST_EMBEDDING_PATH"]
        ENV_DS["LIGHTLY_LAST_DATASET_ID"]
    end
    
    subgraph "Configuration"
        CFG_ENV["environment_variable_names:<br/>lightly_last_checkpoint_path<br/>lightly_last_embedding_path<br/>lightly_last_dataset_id"]
    end
    
    subgraph "Output Files"
        CKPT_FILE["checkpoint.ckpt"]
        EMB_FILE["embeddings.csv"]
    end
    
    TRAIN --> CKPT_FILE
    CKPT_FILE -->|sets| ENV_CKPT
    
    EMBED --> EMB_FILE
    EMB_FILE -->|sets| ENV_EMB
    
    MAGIC --> TRAIN
    MAGIC --> EMBED
    
    CFG_ENV -.defines.-> ENV_CKPT
    CFG_ENV -.defines.-> ENV_EMB
    CFG_ENV -.defines.-> ENV_DS
```

Sources: [lightly/cli/config/config.yaml:106-109](), [lightly/cli/train_cli.py:149-152](), [lightly/cli/embed_cli.py:85-87]()

### Environment Variable Definitions

The environment variable names are configurable through the `environment_variable_names` namespace:

```yaml
environment_variable_names:
  lightly_last_checkpoint_path: LIGHTLY_LAST_CHECKPOINT_PATH
  lightly_last_embedding_path: LIGHTLY_LAST_EMBEDDING_PATH
  lightly_last_dataset_id: LIGHTLY_LAST_DATASET_ID
```

After executing `lightly-ssl-train`, the checkpoint path is stored:

```python
os.environ[cfg["environment_variable_names"]["lightly_last_checkpoint_path"]] = encoder.checkpoint
```

After executing `lightly-embed`, the embeddings path is stored:

```python
os.environ[cfg["environment_variable_names"]["lightly_last_embedding_path"]] = path
```

Sources: [lightly/cli/config/config.yaml:106-109](), [lightly/cli/train_cli.py:149-152](), [lightly/cli/embed_cli.py:85-87]()

### Command Chaining Example

Environment variables enable chaining commands without manually specifying intermediate outputs:

```bash
# Train model (sets LIGHTLY_LAST_CHECKPOINT_PATH)
lightly-ssl-train input_dir=data/ trainer.max_epochs=10

# Embed using the checkpoint from previous command
# (automatically reads from LIGHTLY_LAST_CHECKPOINT_PATH if checkpoint not specified)
lightly-embed input_dir=data/
```

Sources: [lightly/cli/train_cli.py:149-152](), [lightly/cli/embed_cli.py:85-87]()

## Hydra Integration

The CLI uses Hydra's `@hydra.main` decorator to enable hierarchical configuration management and automatic help generation.

### Hydra Decorator Usage

Each CLI entrypoint uses the `@hydra.main` decorator with version-adaptive arguments:

```python
@hydra.main(**fix_hydra_arguments(config_path="config", config_name="config"))
def train_cli(cfg):
    return _train_cli(cfg)
```

The `fix_hydra_arguments` helper ensures compatibility across Hydra versions:

```python
def fix_hydra_arguments(config_path: str = "config", config_name: str = "config"):
    hydra_args = {"config_path": config_path, "config_name": config_name}
    
    if version_compare(hydra.__version__, "1.2.0") >= 0:
        hydra_args["version_base"] = None
    elif version_compare(hydra.__version__, "1.1.2") > 0:
        hydra_args["version_base"] = "1.1"
    
    return hydra_args
```

Sources: [lightly/cli/train_cli.py:155-157](), [lightly/cli/_helpers.py:36-53]()

### Output Directory Management

Hydra automatically creates timestamped output directories for each run:

```yaml
hydra:
  run:
    dir: lightly_outputs/${now:%Y-%m-%d}/${now:%H-%M-%S}
```

This creates directory structures like:

```
lightly_outputs/
├── 2024-01-15/
│   ├── 10-30-45/
│   │   ├── .hydra/
│   │   │   ├── config.yaml
│   │   │   ├── hydra.yaml
│   │   │   └── overrides.yaml
│   │   ├── embeddings.csv
│   │   └── version_0/
│   │       └── checkpoints/
│   └── 14-22-11/
│       └── ...
```

Sources: [lightly/cli/config/config.yaml:116-118]()

### Path Resolution

Hydra changes the working directory to the output directory at runtime. The CLI uses `fix_input_path` to resolve relative paths correctly:

```python
def fix_input_path(path):
    """Fix broken relative paths."""
    if not os.path.isabs(path):
        path = utils.to_absolute_path(path)
    return path
```

This is applied to input paths before use:

```python
input_dir = cfg["input_dir"]
if input_dir and is_cli_call:
    input_dir = fix_input_path(input_dir)
```

Sources: [lightly/cli/_helpers.py:29-33](), [lightly/cli/train_cli.py:38-40](), [lightly/cli/embed_cli.py:44-46]()

### Help System

Hydra generates help text from the configuration file's `hydra.help` section:

```yaml
hydra:
  help:
    header: |
      == Description ==
      The lightly Python package is a command-line tool for self-supervised learning.
    
    footer: |
      == Examples ==
      
      Use a pre-trained resnet-18 to embed your images
      > lightly-embed input='path/to/image/folder' collate.input_size=224
      
      Train a self-supervised model on your image dataset from scratch
      > lightly-ssl-train input_dir='path/to/image/folder' pre_trained=False
```

Users can view help with `--help`:

```bash
lightly-ssl-train --help
```

Sources: [lightly/cli/config/config.yaml:119-159]()

## Configuration Validation and Warnings

The CLI performs runtime validation and issues warnings for problematic configurations:

### Small Batch Size Warning

Training with small batch sizes can harm embedding quality. The CLI warns when batch size is below 64:

```python
if cfg["loader"]["batch_size"] < 64:
    msg = "Training a self-supervised model with a small batch size: {}! "
    msg = msg.format(cfg["loader"]["batch_size"])
    msg += "Small batch size may harm embedding quality."
    warnings.warn(msg)
```

Sources: [lightly/cli/train_cli.py:57-63]()

### Batch Size Adjustment

The batch size is automatically reduced if it exceeds the dataset size:

```python
cfg["loader"]["batch_size"] = min(cfg["loader"]["batch_size"], len(dataset))
```

Sources: [lightly/cli/train_cli.py:113](), [lightly/cli/embed_cli.py:69]()

### Missing Checkpoint Warning

When `pre_trained=True` but no matching checkpoint exists in the model zoo:

```python
if not checkpoint:
    msg = "Cannot download checkpoint for key {} ".format(key)
    msg += "because it does not exist! "
    msg += "Model will be trained from scratch."
    warnings.warn(msg)
```

Sources: [lightly/cli/train_cli.py:75-79]()

## Configuration in Tests

Test files demonstrate configuration usage patterns:

### Test Configuration Setup

Tests use Hydra's `initialize` and `compose` functions to create test configurations:

```python
with initialize(config_path="../../lightly/cli/config", job_name="test_app"):
    self.cfg = compose(
        config_name="config",
        overrides=[
            f"input_dir={self.folder_path}",
            "trainer.max_epochs=1",
        ],
    )
```

Sources: [tests/cli/test_cli_train.py:26-33](), [tests/cli/test_cli_magic.py:27-34]()

### Programmatic Override Parsing

Tests parse CLI strings to apply overrides programmatically:

```python
def parse_cli_string(self, cli_words: str):
    cli_words = cli_words.replace("lightly-magic ", "")
    cli_words = re.split("=| ", cli_words)
    dict_keys = cli_words[0::2]
    dict_values = cli_words[1::2]
    
    for key, value in zip(dict_keys, dict_values):
        key_subparts = key.split(".")
        if len(key_subparts) == 1:
            self.cfg[key] = value
        elif len(key_subparts) == 2:
            self.cfg[key_subparts[0]][key_subparts[1]] = value
```

Sources: [tests/cli/test_cli_magic.py:50-73]()

## Advanced Configuration Patterns

### Seed Configuration

For reproducible training, set the seed parameter:

```yaml
seed: 1
```

This is applied to PyTorch's random number generators:

```python
if "seed" in cfg.keys():
    seed = cfg["seed"]
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
```

Sources: [lightly/cli/config/config.yaml:112](), [lightly/cli/train_cli.py:42-47]()

### Multi-GPU Configuration

For distributed training, configure multiple GPUs:

```bash
lightly-ssl-train input_dir=data/ trainer.gpus=4
```

This automatically enables DDP strategy:

```python
if accelerator == "gpu" and cfg["trainer"]["gpus"] > 1:
    devices = cfg["trainer"]["gpus"]
    strategy = "ddp"
else:
    devices = 1
    strategy = None
```

Sources: [lightly/cli/train_cli.py:49-55]()

### Checkpoint Directory Configuration

Control where checkpoints are saved:

```yaml
checkpoint_callback:
  save_last: True
  save_top_k: 1
  dirpath:  # None uses Hydra output dir
```

If `dirpath` is not set, checkpoints are stored in the Hydra-managed output directory.

Sources: [lightly/cli/config/config.yaml:95-99](), [lightly/cli/train_cli.py:142-143]()

---

# Page: Python API

# Python API

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [docs/source/getting_started/advanced.rst](docs/source/getting_started/advanced.rst)
- [docs/source/getting_started/benchmarks.rst](docs/source/getting_started/benchmarks.rst)
- [docs/source/getting_started/benchmarks/cifar10_benchmark.py](docs/source/getting_started/benchmarks/cifar10_benchmark.py)
- [docs/source/getting_started/benchmarks/imagenet100_benchmark.py](docs/source/getting_started/benchmarks/imagenet100_benchmark.py)
- [docs/source/getting_started/benchmarks/imagenette_benchmark.py](docs/source/getting_started/benchmarks/imagenette_benchmark.py)
- [docs/source/getting_started/command_line_tool.rst](docs/source/getting_started/command_line_tool.rst)
- [docs/source/getting_started/images/lightly_overview.png](docs/source/getting_started/images/lightly_overview.png)
- [docs/source/getting_started/install.rst](docs/source/getting_started/install.rst)
- [docs/source/getting_started/lightly_at_a_glance.rst](docs/source/getting_started/lightly_at_a_glance.rst)
- [docs/source/getting_started/main_concepts.rst](docs/source/getting_started/main_concepts.rst)
- [docs/source/index.rst](docs/source/index.rst)
- [docs/source/lightly.models.utils.rst](docs/source/lightly.models.utils.rst)
- [docs/source/tutorials/structure_your_input.rst](docs/source/tutorials/structure_your_input.rst)
- [docs/source/tutorials_source/package/Base-RCNN-FPN.yaml](docs/source/tutorials_source/package/Base-RCNN-FPN.yaml)
- [docs/source/tutorials_source/package/tutorial_custom_augmentations.py](docs/source/tutorials_source/package/tutorial_custom_augmentations.py)
- [docs/source/tutorials_source/package/tutorial_moco_memory_bank.py](docs/source/tutorials_source/package/tutorial_moco_memory_bank.py)
- [docs/source/tutorials_source/package/tutorial_pretrain_detectron2.py](docs/source/tutorials_source/package/tutorial_pretrain_detectron2.py)
- [docs/source/tutorials_source/package/tutorial_simclr_clothing.py](docs/source/tutorials_source/package/tutorial_simclr_clothing.py)
- [docs/source/tutorials_source/package/tutorial_simsiam_esa.py](docs/source/tutorials_source/package/tutorial_simsiam_esa.py)

</details>



The Python API provides a programmatic interface to Lightly's self-supervised learning functionality through the `lightly.core` module. This API wraps the command-line interface implementations, allowing users to train models and generate embeddings directly from Python code with full control over configuration and return values.

For information about the command-line interface, see [Command-Line Interface](#4). For details on the underlying API client for platform integration, see [Platform Integration](#6).

## Overview

The Python API consists of three main functions in the `lightly.core` module that mirror the CLI commands:

```mermaid
graph TB
    subgraph "lightly.core Module"
        train_model_and_embed_images["train_model_and_embed_images()"]
        train_embedding_model["train_embedding_model()"]
        embed_images["embed_images()"]
    end
    
    subgraph "CLI Implementations"
        _lightly_cli["_lightly_cli()"]
        _train_cli["_train_cli()"]
        _embed_cli["_embed_cli()"]
    end
    
    subgraph "Configuration"
        config_yaml["config.yaml"]
        kwargs["kwargs overrides"]
    end
    
    subgraph "Outputs"
        embeddings["embeddings: np.ndarray"]
        labels["labels: List[int]"]
        filenames["filenames: List[str]"]
        checkpoint["checkpoint: str"]
    end
    
    config_yaml --> train_model_and_embed_images
    kwargs --> train_model_and_embed_images
    train_model_and_embed_images --> _lightly_cli
    train_model_and_embed_images --> embeddings
    train_model_and_embed_images --> labels
    train_model_and_embed_images --> filenames
    
    config_yaml --> train_embedding_model
    kwargs --> train_embedding_model
    train_embedding_model --> _train_cli
    train_embedding_model --> checkpoint
    
    config_yaml --> embed_images
    kwargs --> embed_images
    embed_images --> _embed_cli
    embed_images --> embeddings
    embed_images --> labels
    embed_images --> filenames
```

**Purpose:** Bridge the gap between CLI functionality and Python integration by providing functions that accept Python data structures, handle configuration merging, and return results directly to the caller.

Sources: [lightly/core.py:1-221]()

## Core Functions

### train_model_and_embed_images

```python
def train_model_and_embed_images(
    config_path: str = None, **kwargs
) -> Tuple[np.ndarray, List[int], List[str]]
```

This function combines model training and embedding generation in a single call. It first trains a self-supervised model using the training CLI, then uses the trained checkpoint to generate embeddings for all images.

**Parameters:**
- `config_path`: Optional path to a YAML configuration file. If `None`, uses the default configuration from [lightly/cli/config/config.yaml:1-160]()
- `**kwargs`: Dictionary of configuration overrides organized by namespace (e.g., `trainer={'max_epochs': 10}`)

**Returns:**
- `embeddings`: NumPy array of shape `(n_samples, embedding_size)`
- `labels`: List of integer labels (enumerated from dataset structure)
- `filenames`: List of image filenames

**Implementation Flow:**

```mermaid
sequenceDiagram
    participant User
    participant train_model_and_embed_images
    participant _get_config_path
    participant _load_config_file
    participant _add_kwargs
    participant _train_cli
    participant _embed_cli
    
    User->>train_model_and_embed_images: config_path, **kwargs
    train_model_and_embed_images->>_get_config_path: config_path
    _get_config_path-->>train_model_and_embed_images: resolved path
    train_model_and_embed_images->>_load_config_file: config_path
    _load_config_file-->>train_model_and_embed_images: config_args dict
    train_model_and_embed_images->>_add_kwargs: config_args, kwargs
    _add_kwargs-->>train_model_and_embed_images: merged config
    train_model_and_embed_images->>_train_cli: config, is_cli_call=False
    _train_cli-->>train_model_and_embed_images: checkpoint path
    train_model_and_embed_images->>_embed_cli: config + checkpoint, is_cli_call=False
    _embed_cli-->>train_model_and_embed_images: embeddings, labels, filenames
    train_model_and_embed_images-->>User: embeddings, labels, filenames
```

Sources: [lightly/core.py:78-124]()

### train_embedding_model

```python
def train_embedding_model(config_path: str = None, **kwargs) -> str
```

Trains a self-supervised model and returns the path to the saved checkpoint. This function mirrors the `lightly-ssl-train` CLI command.

**Parameters:**
- `config_path`: Optional path to a YAML configuration file
- `**kwargs`: Configuration overrides (e.g., `loader={'batch_size': 100, 'num_workers': 8}`)

**Returns:**
- `str`: Path to the saved model checkpoint file (`.ckpt`)

**Key Configuration Namespaces:**
- `trainer`: PyTorch Lightning trainer parameters (max_epochs, gpus, precision)
- `loader`: DataLoader parameters (batch_size, num_workers, shuffle)
- `model`: Model architecture parameters (name, out_dim, num_ftrs)
- `optimizer`: Optimizer parameters (lr, weight_decay)
- `collate`: Data augmentation parameters (input_size, cj_prob, etc.)

Sources: [lightly/core.py:127-171](), [lightly/cli/train_cli.py:37-153]()

### embed_images

```python
def embed_images(
    checkpoint: str, 
    config_path: str = None, 
    **kwargs
) -> Tuple[np.ndarray, List[int], List[str]]
```

Generates embeddings for images using a pre-trained model checkpoint. This function mirrors the `lightly-embed` CLI command.

**Parameters:**
- `checkpoint`: Path to the model checkpoint file (`.ckpt`)
- `config_path`: Optional path to a YAML configuration file
- `**kwargs`: Configuration overrides

**Returns:**
- `embeddings`: NumPy array of shape `(n_samples, embedding_size)`
- `labels`: List of integer labels
- `filenames`: List of image filenames

**Behavior Differences from CLI:**
- When called programmatically (`is_cli_call=False`), returns embeddings directly instead of saving to CSV
- Disables shuffling and drop_last in the DataLoader for deterministic ordering
- Uses a simple transform pipeline: Resize → ToTensor → Normalize

Sources: [lightly/core.py:174-221](), [lightly/cli/embed_cli.py:31-91]()

## Configuration System

### Configuration Architecture

```mermaid
graph LR
    subgraph "Configuration Sources"
        default_yaml["Default config.yaml"]
        custom_yaml["Custom config.yaml"]
        kwargs_dict["kwargs Dictionary"]
    end
    
    subgraph "Configuration Loading"
        _get_config_path["_get_config_path()"]
        _load_config_file["_load_config_file()"]
        _add_kwargs["_add_kwargs()"]
    end
    
    subgraph "Configuration Structure"
        input_dir["input_dir"]
        trainer_ns["trainer: {...}"]
        loader_ns["loader: {...}"]
        model_ns["model: {...}"]
        optimizer_ns["optimizer: {...}"]
        collate_ns["collate: {...}"]
        criterion_ns["criterion: {...}"]
    end
    
    default_yaml --> _get_config_path
    custom_yaml --> _get_config_path
    _get_config_path --> _load_config_file
    _load_config_file --> _add_kwargs
    kwargs_dict --> _add_kwargs
    
    _add_kwargs --> input_dir
    _add_kwargs --> trainer_ns
    _add_kwargs --> loader_ns
    _add_kwargs --> model_ns
    _add_kwargs --> optimizer_ns
    _add_kwargs --> collate_ns
    _add_kwargs --> criterion_ns
```

Sources: [lightly/core.py:17-76]()

### Configuration Loading

The `_get_config_path()` function resolves the configuration file path:

| Input | Resolution |
|-------|-----------|
| `None` | Uses default config at `lightly/cli/config/config.yaml` |
| Custom path | Validates existence and returns the path |
| Non-existent path | Raises `ValueError` |

The `_load_config_file()` function uses PyYAML's `FullLoader` to parse the YAML file into a nested dictionary structure.

Sources: [lightly/core.py:17-53]()

### Configuration Merging

The `_add_kwargs()` function recursively merges keyword arguments into the loaded configuration:

**Merge Strategy:**
- **Scalar values**: Direct override (e.g., `input_dir='path/to/data'`)
- **Nested dictionaries**: Recursive merge (e.g., `trainer={'max_epochs': 10}` only updates `max_epochs`)
- **New keys**: Added to configuration (e.g., `+optimizer.momentum=0.9` in CLI becomes `optimizer={'momentum': 0.9}`)

**Example Configuration Merge:**

```python
# Base config
base = {
    'input_dir': '',
    'trainer': {'max_epochs': 100, 'gpus': 1},
    'loader': {'batch_size': 16}
}

# User overrides
kwargs = {
    'input_dir': '/data/images',
    'trainer': {'max_epochs': 50},  # Only updates max_epochs
    'loader': {'batch_size': 128, 'num_workers': 8}  # Updates batch_size, adds num_workers
}

# Result
result = {
    'input_dir': '/data/images',
    'trainer': {'max_epochs': 50, 'gpus': 1},  # max_epochs changed, gpus retained
    'loader': {'batch_size': 128, 'num_workers': 8}
}
```

Sources: [lightly/core.py:56-75]()

### Default Configuration Structure

The default configuration file defines the following namespaces:

| Namespace | Purpose | Key Parameters |
|-----------|---------|----------------|
| `input_dir` | Image directory path | String path |
| `output_dir` | Output directory for results | String path |
| `checkpoint` | Model checkpoint path | String path or URL |
| `model` | Model architecture | `name`, `out_dim`, `num_ftrs`, `width` |
| `trainer` | PyTorch Lightning trainer | `max_epochs`, `gpus`, `precision` |
| `loader` | DataLoader settings | `batch_size`, `num_workers`, `shuffle` |
| `optimizer` | SGD optimizer | `lr`, `weight_decay` |
| `criterion` | Loss function | `temperature`, `memory_bank_size` |
| `collate` | Data augmentation | `input_size`, `cj_prob`, `min_scale`, etc. |

Sources: [lightly/cli/config/config.yaml:1-160]()

## CLI Integration

### Bridging Mechanism

The Python API functions call internal CLI implementations with `is_cli_call=False` to modify their behavior:

```mermaid
graph TB
    subgraph "Python API Layer"
        api_train["train_embedding_model()"]
        api_embed["embed_images()"]
        api_both["train_model_and_embed_images()"]
    end
    
    subgraph "CLI Implementation Layer"
        cli_train["_train_cli(cfg, is_cli_call)"]
        cli_embed["_embed_cli(cfg, is_cli_call)"]
        cli_magic["_lightly_cli(cfg, is_cli_call)"]
    end
    
    subgraph "Behavior Modifications"
        no_path_fix["Skip path resolution"]
        return_values["Return values directly"]
        no_env_vars["Skip env var setting"]
    end
    
    api_train -->|"is_cli_call=False"| cli_train
    api_embed -->|"is_cli_call=False"| cli_embed
    api_both -->|"is_cli_call=False"| cli_magic
    
    cli_train --> no_path_fix
    cli_embed --> no_path_fix
    
    cli_train --> return_values
    cli_embed --> return_values
    
    cli_embed --> no_env_vars
```

**Key Behavioral Differences:**

| Aspect | CLI Mode (`is_cli_call=True`) | API Mode (`is_cli_call=False`) |
|--------|-------------------------------|--------------------------------|
| Path resolution | Applies `fix_input_path()` | Uses paths as-is |
| Return values | Saves to disk, prints paths | Returns data directly |
| Environment variables | Sets `LIGHTLY_LAST_*_PATH` | No side effects |
| Output format | CSV files for embeddings | NumPy arrays |

Sources: [lightly/cli/train_cli.py:37-153](), [lightly/cli/embed_cli.py:31-91]()

### Path Resolution

The `fix_input_path()` helper converts relative paths to absolute paths when called from CLI:

```python
def fix_input_path(path):
    """Fix broken relative paths."""
    if not os.path.isabs(path):
        path = utils.to_absolute_path(path)
    return path
```

This is skipped in API mode to allow users to pass paths relative to their Python script's working directory.

Sources: [lightly/cli/_helpers.py:29-33]()

## Usage Examples

### Example 1: Train and Embed with Default Settings

```python
import lightly

# Train a model and generate embeddings with all defaults
embeddings, labels, filenames = lightly.train_model_and_embed_images(
    input_dir='data/images'
)

print(f"Generated {len(embeddings)} embeddings of dimension {embeddings.shape[1]}")
```

Sources: [docs/source/getting_started/lightly_at_a_glance.rst:1-238]()

### Example 2: Custom Training Configuration

```python
import lightly

# Train with custom settings
checkpoint = lightly.train_embedding_model(
    input_dir='data/images',
    trainer={'max_epochs': 50, 'gpus': 2},
    loader={'batch_size': 128, 'num_workers': 8},
    model={'name': 'resnet-50', 'num_ftrs': 128}
)

print(f"Model saved to: {checkpoint}")
```

This is equivalent to the CLI command:
```bash
lightly-ssl-train input_dir=data/images trainer.max_epochs=50 trainer.gpus=2 \
    loader.batch_size=128 loader.num_workers=8 model.name=resnet-50 model.num_ftrs=128
```

Sources: [lightly/core.py:144-166]()

### Example 3: Embed with Pre-trained Model

```python
import lightly

# Use a pre-trained checkpoint to embed images
embeddings, labels, filenames = lightly.embed_images(
    checkpoint='models/checkpoint.ckpt',
    input_dir='data/images',
    collate={'input_size': 224}  # Use larger input size at inference
)

# Use embeddings for downstream tasks
from sklearn.neighbors import NearestNeighbors
nn = NearestNeighbors(n_neighbors=5)
nn.fit(embeddings)
distances, indices = nn.kneighbors([embeddings[0]])
```

Sources: [lightly/core.py:192-212]()

### Example 4: Custom Configuration File

```python
import lightly

# Load configuration from custom YAML file
checkpoint = lightly.train_embedding_model(
    config_path='configs/my_config.yaml',
    input_dir='data/images',  # Override specific parameters
    trainer={'max_epochs': 20}
)
```

Sources: [lightly/core.py:152-153]()

### Example 5: Programmatic Training Loop Integration

```python
import lightly
import numpy as np
from sklearn.decomposition import PCA

# Train model with multiple configurations
results = []
for num_ftrs in [32, 64, 128]:
    embeddings, labels, filenames = lightly.train_model_and_embed_images(
        input_dir='data/images',
        trainer={'max_epochs': 10},
        model={'num_ftrs': num_ftrs}
    )
    
    # Analyze embedding quality
    pca = PCA(n_components=2)
    reduced = pca.fit_transform(embeddings)
    variance_explained = np.sum(pca.explained_variance_ratio_)
    
    results.append({
        'num_ftrs': num_ftrs,
        'variance_explained': variance_explained
    })

print(f"Best configuration: {max(results, key=lambda x: x['variance_explained'])}")
```

Sources: [tests/core/test_Core.py:44-64]()

## Implementation Details

### Model Loading and Checkpoint Handling

The Python API delegates to CLI helper functions for model loading:

```mermaid
graph TB
    subgraph "Checkpoint Sources"
        pretrained["Pre-trained Models"]
        custom_ckpt["Custom Checkpoint"]
        url_ckpt["URL Checkpoint"]
    end
    
    subgraph "Helper Functions"
        get_ptmodel["get_ptmodel_from_config()"]
        load_url["load_state_dict_from_url()"]
        load_file["torch.load()"]
    end
    
    subgraph "Model Construction"
        resnet_gen["ResNetGenerator"]
        features["Features Module"]
        simclr["_SimCLR Model"]
        load_state["load_from_state_dict()"]
    end
    
    pretrained --> get_ptmodel
    get_ptmodel --> load_url
    url_ckpt --> load_url
    custom_ckpt --> load_file
    
    load_url --> load_state
    load_file --> load_state
    
    resnet_gen --> features
    features --> simclr
    load_state --> simclr
```

**Checkpoint Resolution Logic:**
1. If `pre_trained=True` and no checkpoint specified: Fetch from model zoo using `get_ptmodel_from_config()`
2. If checkpoint is URL: Download using `load_state_dict_from_url()`
3. If checkpoint is file path: Load directly using `torch.load()`

Sources: [lightly/cli/train_cli.py:69-106](), [lightly/cli/_helpers.py:62-93]()

### Embedding Generation Process

The `_embed_cli()` function implements the embedding pipeline:

1. **Setup:** Create dataset with resize and normalize transforms
2. **DataLoader:** Configure with `shuffle=False`, `drop_last=False` for deterministic ordering
3. **Model Loading:** Load checkpoint and create `SelfSupervisedEmbedding` wrapper
4. **Inference:** Call `encoder.embed(dataloader, device)`
5. **Return:** Either save to CSV (CLI mode) or return arrays (API mode)

**Transform Pipeline:**
```python
transform = T.Compose([
    T.Resize((input_size, input_size)),
    T.ToTensor(),
    T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])
```

Sources: [lightly/cli/embed_cli.py:56-90]()

### Environment Variable Management

In CLI mode, the implementation sets environment variables for chaining commands:

| Variable | Purpose | Set By |
|----------|---------|--------|
| `LIGHTLY_LAST_CHECKPOINT_PATH` | Path to last trained checkpoint | `_train_cli()` |
| `LIGHTLY_LAST_EMBEDDING_PATH` | Path to last generated embeddings | `_embed_cli()` |
| `LIGHTLY_LAST_DATASET_ID` | Last created dataset ID | Platform upload |

These variables are not set in API mode (`is_cli_call=False`).

Sources: [lightly/cli/train_cli.py:149-151](), [lightly/cli/embed_cli.py:85-87](), [lightly/cli/config/config.yaml:106-109]()

### Model Architecture

The Python API uses the `_SimCLR` model wrapper defined in `lightly.cli._cli_simclr`:

```python
model = _SimCLR(
    features,  # ResNet backbone
    num_ftrs=cfg['model']['num_ftrs'],  # Feature dimension
    out_dim=cfg['model']['out_dim']      # Projection head output
)
```

The features module consists of:
- Normalization layer: `get_norm_layer(3, 0)`
- ResNet backbone: `ResNetGenerator(name, width)`
- 1x1 convolution: `Conv2d(channels, num_ftrs, 1)`
- Global average pooling: `AdaptiveAvgPool2d(1)`

Sources: [lightly/cli/train_cli.py:92-106]()

## Integration with Other Components

### Dataset Management

The Python API uses `LightlyDataset` for data loading:
- Supports image directories and video files
- Applies transforms from the collate configuration
- Returns tuples of `(sample, target, filename)`

For details on dataset functionality, see [Data Handling](#3).

Sources: [lightly/cli/train_cli.py:111-118](), [lightly/cli/embed_cli.py:64-75]()

### Training Infrastructure

Training uses PyTorch Lightning's `Trainer` with configurations from the `trainer` namespace:
- Handles multi-GPU training with DDP strategy
- Supports mixed precision training
- Creates checkpoints automatically

For benchmarking and evaluation details, see [Benchmarking](#7).

Sources: [lightly/cli/train_cli.py:122-144]()

### Loss Functions and Optimizers

The API configures:
- **Loss:** `NTXentLoss` with temperature and optional memory bank
- **Optimizer:** `torch.optim.SGD` with learning rate and weight decay

For loss function details, see [Loss Functions](#2.2).

Sources: [lightly/cli/train_cli.py:108-109]()

---

# Page: Platform Integration

# Platform Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/source/lightly.models.rst](docs/source/lightly.models.rst)
- [lightly/__init__.py](lightly/__init__.py)
- [lightly/api/_version_checking.py](lightly/api/_version_checking.py)
- [lightly/api/api_workflow_client.py](lightly/api/api_workflow_client.py)
- [lightly/api/api_workflow_compute_worker.py](lightly/api/api_workflow_compute_worker.py)
- [lightly/api/api_workflow_datasets.py](lightly/api/api_workflow_datasets.py)
- [lightly/openapi_generated/swagger_client/__init__.py](lightly/openapi_generated/swagger_client/__init__.py)
- [lightly/openapi_generated/swagger_client/api/datasets_api.py](lightly/openapi_generated/swagger_client/api/datasets_api.py)
- [lightly/openapi_generated/swagger_client/api/datasources_api.py](lightly/openapi_generated/swagger_client/api/datasources_api.py)
- [lightly/openapi_generated/swagger_client/api/docker_api.py](lightly/openapi_generated/swagger_client/api/docker_api.py)
- [lightly/openapi_generated/swagger_client/api/embeddings_api.py](lightly/openapi_generated/swagger_client/api/embeddings_api.py)
- [lightly/openapi_generated/swagger_client/api/samples_api.py](lightly/openapi_generated/swagger_client/api/samples_api.py)
- [lightly/openapi_generated/swagger_client/api/tags_api.py](lightly/openapi_generated/swagger_client/api/tags_api.py)
- [lightly/openapi_generated/swagger_client/models/__init__.py](lightly/openapi_generated/swagger_client/models/__init__.py)
- [lightly/openapi_generated/swagger_client/models/api_error_code.py](lightly/openapi_generated/swagger_client/models/api_error_code.py)
- [lightly/openapi_generated/swagger_client/models/create_sample_with_write_urls_response.py](lightly/openapi_generated/swagger_client/models/create_sample_with_write_urls_response.py)
- [tests/api/test_version_checking.py](tests/api/test_version_checking.py)
- [tests/api_workflow/mocked_api_workflow_client.py](tests/api_workflow/mocked_api_workflow_client.py)
- [tests/api_workflow/test_api_workflow.py](tests/api_workflow/test_api_workflow.py)
- [tests/api_workflow/test_api_workflow_client.py](tests/api_workflow/test_api_workflow_client.py)
- [tests/api_workflow/test_api_workflow_compute_worker.py](tests/api_workflow/test_api_workflow_compute_worker.py)
- [tests/api_workflow/test_api_workflow_datasets.py](tests/api_workflow/test_api_workflow_datasets.py)
- [tests/conftest.py](tests/conftest.py)

</details>



The Platform Integration component provides a standardized, layered interface for communication between the Lightly framework and the Lightly Platform. This page documents the overall architecture, including the `ApiWorkflowClient`, the mixin pattern, the OpenAPI generated client layer, and the infrastructure layer (retry mechanisms, pagination, error handling). For details on specific functional areas like dataset management, compute workers, or datasources, see their respective dedicated pages (sections 6.1-6.6).

## Architecture Overview

The platform integration uses a layered architecture with four main layers:

### Layered Architecture

```mermaid
flowchart TB
    subgraph "Layer 1: Client Application"
        UserCode["User Code<br/>(Python Scripts/CLI)"]
    end
    
    subgraph "Layer 2: Workflow Client"
        ApiWorkflowClient["ApiWorkflowClient<br/>lightly/api/api_workflow_client.py"]
    end
    
    subgraph "Layer 3: Mixin Layer"
        DatasetsMixin["_DatasetsMixin"]
        ComputeWorkerMixin["_ComputeWorkerMixin"]
        EmbeddingsMixin["_UploadEmbeddingsMixin"]
        MetadataMixin["_UploadCustomMetadataMixin"]
        TagsMixin["_TagsMixin"]
        DatasourceMixin["_DatasourcesMixin"]
        SelectionMixin["_SelectionMixin"]
        OtherMixins["+ 5 more mixins"]
    end
    
    subgraph "Layer 4: OpenAPI Generated Clients"
        DatasetsApi["DatasetsApi"]
        DockerApi["DockerApi"]
        EmbeddingsApi["EmbeddingsApi"]
        SamplesApi["SamplesApi"]
        TagsApi["TagsApi"]
        DatasourcesApi["DatasourcesApi"]
        JobsApi["JobsApi"]
        OtherApis["+ 7 more API modules"]
    end
    
    subgraph "Layer 5: Infrastructure"
        RetryUtils["retry_utils<br/>Exponential Backoff"]
        PaginationUtils["paginate_endpoint<br/>Cursor Handling"]
        VersionCheck["_version_checking<br/>Compatibility"]
    end
    
    subgraph "External: Lightly Platform"
        RestAPI["REST API<br/>(Swagger/OpenAPI)"]
        Database[("Platform Database")]
        WorkerQueue["Worker Queue"]
        CloudStorage["Cloud Storage"]
    end
    
    UserCode --> ApiWorkflowClient
    ApiWorkflowClient --> DatasetsMixin
    ApiWorkflowClient --> ComputeWorkerMixin
    ApiWorkflowClient --> EmbeddingsMixin
    ApiWorkflowClient --> MetadataMixin
    ApiWorkflowClient --> TagsMixin
    ApiWorkflowClient --> DatasourceMixin
    ApiWorkflowClient --> SelectionMixin
    ApiWorkflowClient --> OtherMixins
    
    DatasetsMixin --> DatasetsApi
    ComputeWorkerMixin --> DockerApi
    EmbeddingsMixin --> EmbeddingsApi
    MetadataMixin --> SamplesApi
    TagsMixin --> TagsApi
    DatasourceMixin --> DatasourcesApi
    SelectionMixin --> JobsApi
    
    DatasetsApi --> RetryUtils
    DockerApi --> RetryUtils
    EmbeddingsApi --> PaginationUtils
    SamplesApi --> RetryUtils
    
    RetryUtils --> RestAPI
    PaginationUtils --> RestAPI
    ApiWorkflowClient -.imports.-> VersionCheck
    
    RestAPI --> Database
    RestAPI --> WorkerQueue
    RestAPI --> CloudStorage
```

Sources: [lightly/api/api_workflow_client.py:52-146](), [lightly/api/api_workflow_compute_worker.py:1-729](), [tests/api_workflow/mocked_api_workflow_client.py:1-1260]()

### Layer Responsibilities

| Layer | Components | Responsibility |
|-------|-----------|----------------|
| **Client Application** | User code, CLI scripts | Entry point for all platform operations |
| **Workflow Client** | `ApiWorkflowClient` | Central coordinator, manages authentication and dataset context |
| **Mixin Layer** | 12 specialized mixins | High-level workflow methods grouped by functionality |
| **OpenAPI Generated Clients** | 14 API modules | Low-level HTTP communication with platform endpoints |
| **Infrastructure** | Retry utils, pagination, version check | Cross-cutting concerns like error handling and compatibility |

Sources: [lightly/api/api_workflow_client.py:52-66](), [lightly/openapi_generated/swagger_client/__init__.py:1-295]()

## ApiWorkflowClient

The `ApiWorkflowClient` class is the main entry point for all platform operations. It composes functionality from multiple mixins and manages the connection to the Lightly Platform.

### Class Structure

```mermaid
classDiagram
    class ApiWorkflowClient {
        -token: str
        -_dataset_id: str
        -embedding_id: str
        -_creator: Creator
        -api_client: LightlySwaggerApiClient
        -_datasets_api: DatasetsApi
        -_compute_worker_api: DockerApi
        -_embeddings_api: EmbeddingsApi
        -_samples_api: SamplesApi
        -_tags_api: TagsApi
        -_datasources_api: DatasourcesApi
        +__init__(token, dataset_id, embedding_id, creator)
        +dataset_id: str
        +upload_file_with_signed_url()
        +get_filenames()
    }
    
    ApiWorkflowClient --|> _DatasetsMixin
    ApiWorkflowClient --|> _ComputeWorkerMixin
    ApiWorkflowClient --|> _UploadEmbeddingsMixin
    ApiWorkflowClient --|> _TagsMixin
    ApiWorkflowClient --|> _DatasourcesMixin
    ApiWorkflowClient --|> _SelectionMixin
    ApiWorkflowClient --|> _DownloadDatasetMixin
    ApiWorkflowClient --|> _UploadCustomMetadataMixin
    ApiWorkflowClient --|> _CollaborationMixin
    ApiWorkflowClient --|> _PredictionsMixin
    ApiWorkflowClient --|> _ArtifactsMixin
    ApiWorkflowClient --|> _ExportDatasetMixin
    
    ApiWorkflowClient --> LightlySwaggerApiClient
    LightlySwaggerApiClient --> DatasetsApi
    LightlySwaggerApiClient --> DockerApi
    LightlySwaggerApiClient --> EmbeddingsApi
```

Sources: [lightly/api/api_workflow_client.py:52-146]()

### Initialization and Authentication

The `ApiWorkflowClient` requires an API token for authentication. The token can be provided directly or via the `LIGHTLY_TOKEN` environment variable.

```python
from lightly.api import ApiWorkflowClient

# Initialize with token provided directly
client = ApiWorkflowClient(token="YOUR_API_TOKEN")

# Initialize with token from environment variable LIGHTLY_TOKEN
import os
os.environ["LIGHTLY_TOKEN"] = "YOUR_API_TOKEN"
client = ApiWorkflowClient()

# Initialize with specific dataset and embedding
client = ApiWorkflowClient(
    token="YOUR_API_TOKEN",
    dataset_id="YOUR_DATASET_ID",
    embedding_id="YOUR_EMBEDDING_ID"
)
```

Sources: [lightly/api/api_workflow_client.py:90-129]()

### Constructor Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `token` | `Optional[str]` | API token. If not provided, reads from `LIGHTLY_TOKEN` environment variable. |
| `dataset_id` | `Optional[str]` | ID of the dataset to use. If not set, defaults to the most recently modified dataset. |
| `embedding_id` | `Optional[str]` | ID of the embedding to use. If not set, defaults to the newest embedding. |
| `creator` | `str` | Creator identifier passed to API requests. Default is `Creator.USER_PIP`. |

Sources: [lightly/api/api_workflow_client.py:73-96]()

### Key Properties

| Property | Type | Description |
|----------|------|-------------|
| `dataset_id` | `str` | Current dataset ID. Auto-selected if not explicitly set. |
| `token` | `str` | API authentication token. |
| `api_client` | `LightlySwaggerApiClient` | Underlying OpenAPI client instance. |

The `dataset_id` property implements lazy loading: if not explicitly set, it queries the platform for all datasets and selects the most recently modified one.

Sources: [lightly/api/api_workflow_client.py:148-189]()

## Mixin Architecture

The `ApiWorkflowClient` uses a mixin-based composition pattern to organize functionality into cohesive modules. Each mixin provides high-level workflow methods for a specific domain.

### Mixin Composition Pattern

```mermaid
flowchart TB
    subgraph "ApiWorkflowClient Composition"
        ApiWorkflowClient["ApiWorkflowClient"]
    end
    
    subgraph "Dataset Operations"
        DatasetsMixin["_DatasetsMixin<br/>create_dataset()<br/>get_datasets()<br/>delete_dataset_by_id()"]
        TagsMixin["_TagsMixin<br/>get_tags()<br/>create_tag()<br/>delete_tag_by_tag_id()"]
        DownloadMixin["_DownloadDatasetMixin<br/>download_dataset()"]
        ExportMixin["_ExportDatasetMixin<br/>export_tag_to_*()"]
    end
    
    subgraph "Data Management"
        EmbeddingsMixin["_UploadEmbeddingsMixin<br/>upload_embeddings()"]
        MetadataMixin["_UploadCustomMetadataMixin<br/>upload_custom_metadata()"]
        SelectionMixin["_SelectionMixin<br/>selection()"]
    end
    
    subgraph "Storage Configuration"
        DatasourceMixin["_DatasourcesMixin<br/>set_*_datasource()<br/>verify_datasource()"]
        ListingMixin["_DatasourceListingMixin<br/>get_raw_samples()"]
    end
    
    subgraph "Compute Operations"
        ComputeWorkerMixin["_ComputeWorkerMixin<br/>register_compute_worker()<br/>schedule_compute_worker_run()"]
    end
    
    subgraph "Collaboration & Predictions"
        CollabMixin["_CollaborationMixin<br/>share_dataset()"]
        PredictionsMixin["_PredictionsMixin<br/>upload_predictions()"]
        ArtifactsMixin["_ArtifactsMixin<br/>download_artifacts()"]
    end
    
    ApiWorkflowClient --> DatasetsMixin
    ApiWorkflowClient --> TagsMixin
    ApiWorkflowClient --> DownloadMixin
    ApiWorkflowClient --> ExportMixin
    ApiWorkflowClient --> EmbeddingsMixin
    ApiWorkflowClient --> MetadataMixin
    ApiWorkflowClient --> SelectionMixin
    ApiWorkflowClient --> DatasourceMixin
    ApiWorkflowClient --> ListingMixin
    ApiWorkflowClient --> ComputeWorkerMixin
    ApiWorkflowClient --> CollabMixin
    ApiWorkflowClient --> PredictionsMixin
    ApiWorkflowClient --> ArtifactsMixin
```

Sources: [lightly/api/api_workflow_client.py:52-66]()

### Mixin Catalog

| Mixin | File | Key Methods | Purpose |
|-------|------|-------------|---------|
| `_DatasetsMixin` | `api_workflow_datasets.py` | `create_dataset()`, `get_datasets()`, `delete_dataset_by_id()` | Dataset CRUD operations |
| `_TagsMixin` | `api_workflow_tags.py` | `get_tags()`, `create_tag()`, `delete_tag_by_tag_id()` | Tag management |
| `_UploadEmbeddingsMixin` | `api_workflow_upload_embeddings.py` | `upload_embeddings()` | Embedding upload |
| `_UploadCustomMetadataMixin` | `api_workflow_upload_metadata.py` | `upload_custom_metadata()` | Custom metadata upload |
| `_DatasourcesMixin` | `api_workflow_datasources.py` | `set_s3_datasource()`, `verify_datasource()` | Datasource configuration |
| `_DatasourceListingMixin` | `api_workflow_datasource_listing.py` | `get_raw_samples()` | Raw sample listing from datasources |
| `_ComputeWorkerMixin` | `api_workflow_compute_worker.py` | `register_compute_worker()`, `schedule_compute_worker_run()` | Compute worker management |
| `_SelectionMixin` | `api_workflow_selection.py` | `selection()` | Sample selection |
| `_DownloadDatasetMixin` | `api_workflow_download_dataset.py` | `download_dataset()` | Dataset download |
| `_CollaborationMixin` | `api_workflow_collaboration.py` | `share_dataset()` | Collaboration features |
| `_PredictionsMixin` | `api_workflow_predictions.py` | `upload_predictions()` | Prediction upload |
| `_ArtifactsMixin` | `api_workflow_artifacts.py` | `download_artifacts()` | Artifact management |
| `_ExportDatasetMixin` | `api_workflow_export.py` | `export_tag_to_*()` | Dataset export to various formats |

Sources: [lightly/api/api_workflow_client.py:14-26](), [lightly/api/api_workflow_datasets.py:15-509](), [lightly/api/api_workflow_compute_worker.py:84-625]()

## OpenAPI Generated Client Layer

The platform integration uses auto-generated client code from the OpenAPI specification. These generated clients handle the low-level HTTP communication with the Lightly Platform REST API.

### Generated API Modules

```mermaid
flowchart LR
    subgraph "Generated Client Modules"
        DatasetsApi["DatasetsApi<br/>lightly/openapi_generated/.../datasets_api.py"]
        DockerApi["DockerApi<br/>docker_api.py"]
        EmbeddingsApi["EmbeddingsApi<br/>embeddings_api.py"]
        SamplesApi["SamplesApi<br/>samples_api.py"]
        TagsApi["TagsApi<br/>tags_api.py"]
        DatasourcesApi["DatasourcesApi<br/>datasources_api.py"]
        JobsApi["JobsApi<br/>jobs_api.py"]
        MappingsApi["MappingsApi<br/>mappings_api.py"]
        ScoresApi["ScoresApi<br/>scores_api.py"]
        SamplingsApi["SamplingsApi<br/>samplings_api.py"]
        CollaborationApi["CollaborationApi<br/>collaboration_api.py"]
        PredictionsApi["PredictionsApi<br/>predictions_api.py"]
        QuotaApi["QuotaApi<br/>quota_api.py"]
        VersioningApi["VersioningApi<br/>versioning_api.py"]
    end
    
    subgraph "Platform REST Endpoints"
        Datasets["/v1/datasets"]
        Docker["/v1/docker"]
        Embeddings["/v1/datasets/{id}/embeddings"]
        Samples["/v1/datasets/{id}/samples"]
        Tags["/v1/datasets/{id}/tags"]
        Datasources["/v1/datasets/{id}/datasource"]
    end
    
    DatasetsApi --> Datasets
    DockerApi --> Docker
    EmbeddingsApi --> Embeddings
    SamplesApi --> Samples
    TagsApi --> Tags
    DatasourcesApi --> Datasources
```

Sources: [lightly/openapi_generated/swagger_client/__init__.py:20-37](), [lightly/api/api_workflow_client.py:131-146]()

### API Module Instantiation

The `ApiWorkflowClient` instantiates all OpenAPI client modules in its constructor:

```python
# From ApiWorkflowClient.__init__
self._collaboration_api = CollaborationApi(api_client=self.api_client)
self._compute_worker_api = DockerApi(api_client=self.api_client)
self._datasets_api = DatasetsApi(api_client=self.api_client)
self._datasources_api = DatasourcesApi(api_client=self.api_client)
self._selection_api = SamplingsApi(api_client=self.api_client)
self._jobs_api = JobsApi(api_client=self.api_client)
self._tags_api = TagsApi(api_client=self.api_client)
self._embeddings_api = EmbeddingsApi(api_client=self.api_client)
self._mappings_api = MappingsApi(api_client=self.api_client)
self._scores_api = ScoresApi(api_client=self.api_client)
self._samples_api = SamplesApi(api_client=self.api_client)
self._quota_api = QuotaApi(api_client=self.api_client)
self._metadata_configurations_api = MetaDataConfigurationsApi(api_client=self.api_client)
self._predictions_api = PredictionsApi(api_client=self.api_client)
```

Sources: [lightly/api/api_workflow_client.py:131-146]()

### Generated Models

The OpenAPI client also generates data models that represent API request and response objects:

| Model Category | Example Classes |
|----------------|-----------------|
| **Dataset Models** | `DatasetData`, `DatasetCreateRequest`, `DatasetType` |
| **Tag Models** | `TagData`, `TagCreateRequest`, `InitialTagCreateRequest` |
| **Sample Models** | `SampleData`, `SampleCreateRequest`, `SampleUpdateRequest` |
| **Embedding Models** | `DatasetEmbeddingData`, `WriteCSVUrlData` |
| **Worker Models** | `DockerRunData`, `DockerRunScheduledData`, `DockerWorkerRegistryEntryData` |
| **Configuration Models** | `DockerWorkerConfigV4`, `SelectionConfigV4` |
| **Datasource Models** | `DatasourceConfig`, `DatasourceConfigS3`, `DatasourceConfigAzure` |
| **Error Models** | `ApiErrorResponse`, `ApiErrorCode` |

Sources: [lightly/openapi_generated/swagger_client/models/__init__.py:1-270](), [lightly/openapi_generated/swagger_client/__init__.py:50-269]()

## Infrastructure Layer

The infrastructure layer provides cross-cutting functionality that supports reliable communication with the platform.

### Retry Mechanism

The platform integration includes retry logic with exponential backoff to handle transient network errors and rate limiting.

#### Retry Flow

```mermaid
sequenceDiagram
    participant Mixin as Mixin Method
    participant RetryUtil as retry_utils.retry()
    participant OpenAPI as OpenAPI Client
    participant Platform as Lightly Platform
    
    Mixin->>RetryUtil: Call API operation
    loop Retry Loop
        RetryUtil->>OpenAPI: Execute request
        OpenAPI->>Platform: HTTP Request
        
        alt Success
            Platform-->>OpenAPI: 200 OK
            OpenAPI-->>RetryUtil: Response
            RetryUtil-->>Mixin: Success
        else Retryable Error
            Platform-->>OpenAPI: 429/503/Network Error
            OpenAPI-->>RetryUtil: ApiException/HTTPError
            Note over RetryUtil: Wait with<br/>exponential backoff
            RetryUtil->>RetryUtil: Retry
        else Non-Retryable Error
            Platform-->>OpenAPI: 400/404/Other
            OpenAPI-->>RetryUtil: ApiException
            RetryUtil-->>Mixin: Raise Exception
        end
    end
```

Sources: [lightly/api/retry_utils.py:1-100]() (inferred from usage in [lightly/api/api_workflow_compute_worker.py:489-493]())

### Pagination Utilities

For endpoints that return large result sets, the platform integration uses cursor-based pagination.

#### Pagination Pattern

```mermaid
flowchart LR
    subgraph "Client Side"
        PaginateEndpoint["utils.paginate_endpoint()"]
    end
    
    subgraph "API Calls"
        FirstPage["GET /endpoint?page_offset=0&page_size=5000"]
        NextPage["GET /endpoint?page_offset=5000&page_size=5000"]
        FinalPage["GET /endpoint?page_offset=10000&page_size=5000"]
    end
    
    subgraph "Results"
        Iterator["Iterator[ResultType]"]
    end
    
    PaginateEndpoint --> FirstPage
    FirstPage --> NextPage
    NextPage --> FinalPage
    FinalPage --> Iterator
    
    PaginateEndpoint -.yields items.-> Iterator
```

Example usage from `_DatasetsMixin`:
```python
# Paginate over all datasets
datasets = utils.paginate_endpoint(
    self._datasets_api.get_datasets,
    page_size=5000,
    shared=False,
)
```

Sources: [lightly/api/api_workflow_datasets.py:221-240](), [lightly/api/utils.py:1-100]() (inferred from usage)

### Version Compatibility Checking

On initialization, the client verifies compatibility with the platform API version.

```mermaid
sequenceDiagram
    participant Client as ApiWorkflowClient.__init__()
    participant VersionCheck as _version_checking
    participant Platform as Lightly Platform
    
    Client->>VersionCheck: is_compatible_version(__version__)
    VersionCheck->>Platform: GET /pip/version
    Platform-->>VersionCheck: min_compatible_version
    
    alt Compatible
        VersionCheck-->>Client: True
        Client->>Client: Continue initialization
    else Incompatible
        VersionCheck-->>Client: False
        Client->>Client: warnings.warn(UserWarning)
        Client->>Client: Continue (degraded)
    end
```

Sources: [lightly/api/api_workflow_client.py:97-118](), [lightly/api/_version_checking.py:1-74]() (inferred from usage)

### Error Handling

The platform integration handles various error conditions:

| Error Type | HTTP Status | Action |
|------------|-------------|--------|
| Authentication Error | 401, 403 | Raise `ApiException` immediately |
| Not Found | 404 | Raise `ApiException` immediately |
| Rate Limiting | 429 | Retry with exponential backoff |
| Server Error | 500, 503 | Retry with exponential backoff |
| Network Error | N/A | Retry with exponential backoff |
| Invalid Configuration | 400 | Raise `InvalidConfigurationError` with suggestions |

The `ApiErrorCode` enum defines all possible error codes returned by the platform:

```python
# From ApiErrorCode enum
BAD_REQUEST = 'BAD_REQUEST'
FORBIDDEN = 'FORBIDDEN'
UNAUTHORIZED = 'UNAUTHORIZED'
NOT_FOUND = 'NOT_FOUND'
DATASET_UNKNOWN = 'DATASET_UNKNOWN'
DOCKER_WORKER_CONFIG_INVALID = 'DOCKER_WORKER_CONFIG_INVALID'
# ... and many more
```

Sources: [lightly/openapi_generated/swagger_client/models/api_error_code.py:26-111](), [lightly/api/api_workflow_compute_worker.py:38-40]()

## Communication Flow

### Typical API Request Flow

```mermaid
sequenceDiagram
    participant User as User Code
    participant Client as ApiWorkflowClient
    participant Mixin as Specific Mixin
    participant OpenAPI as OpenAPI Client
    participant Retry as retry_utils
    participant Platform as Lightly Platform
    
    User->>Client: client.get_datasets()
    Client->>Mixin: _DatasetsMixin.get_datasets()
    Mixin->>Mixin: utils.paginate_endpoint()
    
    loop For each page
        Mixin->>OpenAPI: _datasets_api.get_datasets(page_offset=N)
        OpenAPI->>Retry: Wrapped with retry logic
        Retry->>Platform: GET /v1/datasets?page_offset=N
        
        alt Success
            Platform-->>Retry: 200 OK + [datasets]
            Retry-->>OpenAPI: Response
            OpenAPI-->>Mixin: List[DatasetData]
        else Transient Error
            Platform-->>Retry: 429/503
            Retry->>Retry: Exponential backoff
            Retry->>Platform: Retry GET /v1/datasets
        else Permanent Error
            Platform-->>Retry: 400/404
            Retry-->>OpenAPI: ApiException
            OpenAPI-->>Mixin: ApiException
            Mixin-->>Client: ApiException
            Client-->>User: ApiException
        end
    end
    
    Mixin-->>Client: Iterator[DatasetData]
    Client-->>User: List[DatasetData]
```

Sources: [lightly/api/api_workflow_client.py:1-296](), [lightly/api/api_workflow_datasets.py:196-284]()

### Configuration Validation Flow

When creating compute worker configurations, the client validates configuration dictionaries before sending them to the platform:

```mermaid
flowchart TB
    UserDict["User provides<br/>worker_config dict"]
    
    ConvertCamel["_config_to_camel_case()<br/>Convert snake_case to camelCase"]
    
    Deserialize["_get_deserialize()<br/>Parse dict into Pydantic model"]
    
    Validate["_validate_config()<br/>Check all keys are valid"]
    
    subgraph "Validation Checks"
        CheckKey["For each key in dict"]
        HasAttr["hasattr(obj, key)?"]
        SuggestMatch["difflib.get_close_matches()<br/>Find similar valid keys"]
        RaiseError["Raise InvalidConfigurationError<br/>with suggestion"]
    end
    
    CreateRequest["Create DockerWorkerConfigOmniVXCreateRequest"]
    
    SendAPI["Send to platform via<br/>_compute_worker_api"]
    
    UserDict --> ConvertCamel
    ConvertCamel --> Deserialize
    Deserialize --> Validate
    
    Validate --> CheckKey
    CheckKey --> HasAttr
    HasAttr -->|No| SuggestMatch
    SuggestMatch --> RaiseError
    HasAttr -->|Yes| CheckKey
    
    Validate -->|Valid| CreateRequest
    CreateRequest --> SendAPI
```

Example error message:
```
InvalidConfigurationError: Option 'batch_siz' does not exist! Did you mean 'batch_size'?
```

Sources: [lightly/api/api_workflow_compute_worker.py:681-729](), [tests/api_workflow/test_api_workflow_compute_worker.py:538-596]()

## Configuration and Environment

### Environment Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `LIGHTLY_TOKEN` | API authentication token | Required if not passed to constructor |
| `LIGHTLY_SERVER_LOCATION` | Platform API base URL | `https://api.lightly.ai` |
| `LIGHTLY_S3_SSE_KMS_KEY` | Enable S3 server-side encryption | None (disabled) |
| `LIGHTLY_DID_VERSION_CHECK` | Skip version compatibility check (internal) | False |

Sources: [lightly/api/api_workflow_client.py:48-49](), [lightly/api/api_workflow_client.py:268-286]()

### S3 Server-Side Encryption

When uploading files to S3 using signed URLs, you can enable server-side encryption:

```python
import os

# Option 1: Use AWS-managed keys
os.environ["LIGHTLY_S3_SSE_KMS_KEY"] = "True"

# Option 2: Use customer-managed KMS key
os.environ["LIGHTLY_S3_SSE_KMS_KEY"] = "arn:aws:kms:region:account:key/key-id"

# Upload file (encryption headers added automatically)
client.upload_file_with_signed_url(file_obj, signed_url)
```

The client automatically adds the appropriate headers:
- `x-amz-server-side-encryption: AES256` (for AWS-managed keys)
- `x-amz-server-side-encryption: aws:kms` (for customer KMS)
- `x-amz-server-side-encryption-aws-kms-key-id: <key-arn>` (for customer KMS)

Sources: [lightly/api/api_workflow_client.py:264-286]()

## Usage Examples

### Basic Initialization and Dataset Creation

```python
from lightly.api import ApiWorkflowClient
from lightly.openapi_generated.swagger_client.models import DatasetType

# Initialize client
client = ApiWorkflowClient(token="YOUR_API_TOKEN")

# Create a new dataset
client.create_dataset("my-dataset", dataset_type=DatasetType.IMAGES)

# Find existing dataset by name
client.set_dataset_id_by_name("my-dataset")

# Get all datasets
datasets = client.get_datasets()
```

Sources: [lightly/api/api_workflow_client.py:90-129](), [lightly/api/api_workflow_datasets.py:354-403]()

### Working with Compute Workers

```python
# Register a compute worker
worker_id = client.register_compute_worker(
    name="my-worker",
    labels=["gpu", "us-west"]
)

# Schedule a run
scheduled_run_id = client.schedule_compute_worker_run(
    selection_config={
        "n_samples": 1000,
        "strategies": [
            {
                "input": {"type": "EMBEDDINGS"},
                "strategy": {"type": "DIVERSITY"}
            }
        ]
    },
    runs_on=["gpu"]  # Only workers with "gpu" label can pick this up
)

# Monitor run status
for run_info in client.compute_worker_run_info_generator(scheduled_run_id):
    print(f"State: {run_info.state}, Message: {run_info.message}")
    if run_info.in_end_state():
        break
```

Sources: [lightly/api/api_workflow_compute_worker.py:85-596]()

### File Ordering and Reordering

The client can reorder local data to match the server's sample order:

```python
# Get server's canonical filename order
filenames_on_server = client.get_filenames()

# Your local data (possibly in different order)
local_filenames = ["img_2.jpg", "img_0.jpg", "img_1.jpg"]
local_embeddings = [emb_2, emb_0, emb_1]

# Reorder to match server
ordered_embeddings = client._order_list_by_filenames(
    filenames_for_list=local_filenames,
    list_to_order=local_embeddings
)
# Result: [emb_0, emb_1, emb_2] (matches server order)
```

Sources: [lightly/api/api_workflow_client.py:191-214]()

## Best Practices

1. **Token Management**: Store your API token securely, preferably using environment variables
2. **Error Handling**: Implement proper exception handling for API operations 
3. **Dataset Management**: Use dataset IDs consistently to ensure operations are performed on the correct dataset
4. **File Uploads**: Consider using server-side encryption for sensitive data when uploading to S3
5. **Version Compatibility**: Keep the Lightly package updated to ensure compatibility with the platform

Sources: [lightly/api/api_workflow_client.py:73-144]()

---

# Page: API Workflow Client

# API Workflow Client

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/source/lightly.models.rst](docs/source/lightly.models.rst)
- [lightly/__init__.py](lightly/__init__.py)
- [lightly/api/_version_checking.py](lightly/api/_version_checking.py)
- [lightly/api/api_workflow_client.py](lightly/api/api_workflow_client.py)
- [lightly/api/api_workflow_datasets.py](lightly/api/api_workflow_datasets.py)
- [tests/api/test_version_checking.py](tests/api/test_version_checking.py)
- [tests/api_workflow/mocked_api_workflow_client.py](tests/api_workflow/mocked_api_workflow_client.py)
- [tests/api_workflow/test_api_workflow.py](tests/api_workflow/test_api_workflow.py)
- [tests/api_workflow/test_api_workflow_client.py](tests/api_workflow/test_api_workflow_client.py)
- [tests/api_workflow/test_api_workflow_datasets.py](tests/api_workflow/test_api_workflow_datasets.py)
- [tests/conftest.py](tests/conftest.py)

</details>



The `ApiWorkflowClient` is the primary interface for communicating with the Lightly Platform API. It provides a unified Python interface for dataset management, datasource configuration, embedding uploads, compute worker orchestration, and data selection operations. The client uses a mixin-based architecture to organize functionality into logical domains and wraps auto-generated OpenAPI clients to provide a higher-level, workflow-oriented interface.

For information about compute worker operations specifically, see [Compute Workers](#6.2). For dataset and tag management operations, see [Dataset and Tag Management](#6.3). For datasource configuration, see [Datasources](#6.4).

## Client Initialization and Authentication

The `ApiWorkflowClient` is initialized with authentication credentials and optional context identifiers:

```python
from lightly.api import ApiWorkflowClient

# Initialize with token only
client = ApiWorkflowClient(token="YOUR_TOKEN")

# Initialize with specific dataset and embedding
client = ApiWorkflowClient(
    token="YOUR_TOKEN",
    dataset_id="dataset_xyz",
    embedding_id="embedding_xyz"
)
```

**Authentication**: The client requires a Lightly API token for authentication. The token can be provided explicitly or read from the `LIGHTLY_TOKEN` environment variable ([lightly/api/utils.py:74-80]()). The token is stored in the client configuration and passed to all API requests via the `ApiKeyAuth` authentication scheme ([lightly/api/api_workflow_client.py:120-124]()).

**Dataset Context**: The `dataset_id` parameter sets the default dataset for subsequent operations. If not provided, the client automatically selects the most recently modified dataset when a dataset ID is first needed ([lightly/api/api_workflow_client.py:149-171]()).

**Embedding Context**: The `embedding_id` parameter sets the default embedding for operations that require embeddings. Similar to dataset_id, it can be set during initialization or later ([lightly/api/api_workflow_client.py:127-128]()).

**Creator Tracking**: The optional `creator` parameter (default: `Creator.USER_PIP`) identifies the source of API operations for analytics purposes ([lightly/api/api_workflow_client.py:95-96]()).

```mermaid
graph TB
    Init["ApiWorkflowClient.__init__"]
    Token["token parameter<br/>or LIGHTLY_TOKEN env var"]
    Config["utils.get_api_client_configuration"]
    SwaggerClient["LightlySwaggerApiClient"]
    VersionCheck["_version_checking.is_compatible_version"]
    GeneratedAPIs["Initialize Generated API Clients<br/>DatasetsApi, DatasourcesApi,<br/>DockerApi, EmbeddingsApi, etc."]
    
    Init --> Token
    Token --> Config
    Config --> SwaggerClient
    Init --> VersionCheck
    SwaggerClient --> GeneratedAPIs
    
    Token -.stored in.-> ConfigObj["configuration.api_key['ApiKeyAuth']"]
    
    style Init fill:#f9f9f9
    style GeneratedAPIs fill:#f9f9f9
```

**Initialization Flow**:

1. Retrieve token from parameter or `LIGHTLY_TOKEN` environment variable
2. Create API client configuration with token authentication
3. Perform version compatibility check (non-blocking, warns if incompatible)
4. Initialize `LightlySwaggerApiClient` with configuration
5. Set custom User-Agent header with platform information
6. Initialize all generated API clients (DatasetsApi, EmbeddingsApi, etc.)
7. Set dataset_id and embedding_id if provided

Sources: [lightly/api/api_workflow_client.py:90-147](), [lightly/api/utils.py:74-106]()

## Mixin-Based Architecture

The `ApiWorkflowClient` uses multiple inheritance from specialized mixin classes to organize functionality. Each mixin handles a specific domain of operations and maintains separation of concerns.

```mermaid
graph TB
    Client["ApiWorkflowClient"]
    
    subgraph "Functional Mixins"
        Embeddings["_UploadEmbeddingsMixin<br/>upload_embeddings()"]
        Selection["_SelectionMixin<br/>trigger_sampling()"]
        Download["_DownloadDatasetMixin<br/>download_dataset()"]
        Datasets["_DatasetsMixin<br/>create_dataset()<br/>get_datasets()"]
        Metadata["_UploadCustomMetadataMixin<br/>upload_custom_metadata()"]
        Tags["_TagsMixin<br/>create_tag()<br/>get_tags()"]
        Datasources["_DatasourcesMixin<br/>set_datasource()"]
        DatasourceListing["_DatasourceListingMixin<br/>list_datasource_samples()"]
        Worker["_ComputeWorkerMixin<br/>register_worker()<br/>schedule_run()"]
        Collab["_CollaborationMixin<br/>share_dataset()"]
        Predictions["_PredictionsMixin<br/>upload_predictions()"]
        Artifacts["_ArtifactsMixin<br/>download_artifacts()"]
        Export["_ExportDatasetMixin<br/>export_dataset()"]
    end
    
    Client -.inherits from.-> Embeddings
    Client -.inherits from.-> Selection
    Client -.inherits from.-> Download
    Client -.inherits from.-> Datasets
    Client -.inherits from.-> Metadata
    Client -.inherits from.-> Tags
    Client -.inherits from.-> Datasources
    Client -.inherits from.-> DatasourceListing
    Client -.inherits from.-> Worker
    Client -.inherits from.-> Collab
    Client -.inherits from.-> Predictions
    Client -.inherits from.-> Artifacts
    Client -.inherits from.-> Export
```

**Mixin Responsibilities**:

| Mixin | File | Primary Methods | Purpose |
|-------|------|-----------------|---------|
| `_UploadEmbeddingsMixin` | api_workflow_upload_embeddings.py | `upload_embeddings()` | Upload feature embeddings to platform |
| `_SelectionMixin` | api_workflow_selection.py | `trigger_sampling()` | Trigger data selection strategies |
| `_DownloadDatasetMixin` | api_workflow_download_dataset.py | `download_dataset()` | Download selected samples |
| `_DatasetsMixin` | api_workflow_datasets.py | `create_dataset()`, `get_datasets()` | Dataset lifecycle management |
| `_UploadCustomMetadataMixin` | api_workflow_upload_metadata.py | `upload_custom_metadata()` | Upload custom sample metadata |
| `_TagsMixin` | api_workflow_tags.py | `create_tag()`, `get_tags()` | Tag/selection management |
| `_DatasourcesMixin` | api_workflow_datasources.py | `set_datasource()` | Configure cloud storage connections |
| `_DatasourceListingMixin` | api_workflow_datasource_listing.py | `list_datasource_samples()` | List samples from datasources |
| `_ComputeWorkerMixin` | api_workflow_compute_worker.py | `register_worker()`, `schedule_run()` | Orchestrate compute workers |
| `_CollaborationMixin` | api_workflow_collaboration.py | `share_dataset()` | Dataset sharing operations |
| `_PredictionsMixin` | api_workflow_predictions.py | `upload_predictions()` | Upload model predictions |
| `_ArtifactsMixin` | api_workflow_artifacts.py | `download_artifacts()` | Download worker artifacts |
| `_ExportDatasetMixin` | api_workflow_export.py | `export_dataset()` | Export datasets in various formats |

Each mixin accesses the generated API clients initialized in the base `ApiWorkflowClient` class (e.g., `self._datasets_api`, `self._embeddings_api`).

Sources: [lightly/api/api_workflow_client.py:52-66](), [lightly/api/api_workflow_client.py:14-25]()

## Generated API Clients

The `ApiWorkflowClient` wraps multiple auto-generated API clients created from the Lightly OpenAPI specification. These generated clients handle low-level HTTP communication with the platform.

```mermaid
graph LR
    subgraph "ApiWorkflowClient"
        Client["ApiWorkflowClient<br/>High-level interface"]
        
        subgraph "Instance Variables - Generated Clients"
            DatasetsApi["self._datasets_api<br/>DatasetsApi"]
            DatasourcesApi["self._datasources_api<br/>DatasourcesApi"]
            DockerApi["self._compute_worker_api<br/>DockerApi"]
            EmbeddingsApi["self._embeddings_api<br/>EmbeddingsApi"]
            JobsApi["self._jobs_api<br/>JobsApi"]
            MappingsApi["self._mappings_api<br/>MappingsApi"]
            SamplesApi["self._samples_api<br/>SamplesApi"]
            TagsApi["self._tags_api<br/>TagsApi"]
            SamplingsApi["self._selection_api<br/>SamplingsApi"]
            ScoresApi["self._scores_api<br/>ScoresApi"]
            QuotaApi["self._quota_api<br/>QuotaApi"]
            PredictionsApi["self._predictions_api<br/>PredictionsApi"]
            MetaDataConfigurationsApi["self._metadata_configurations_api<br/>MetaDataConfigurationsApi"]
            CollaborationApi["self._collaboration_api<br/>CollaborationApi"]
        end
    end
    
    Platform["Lightly Platform<br/>REST API<br/>api.lightly.ai"]
    
    DatasetsApi --> Platform
    DatasourcesApi --> Platform
    DockerApi --> Platform
    EmbeddingsApi --> Platform
    JobsApi --> Platform
    MappingsApi --> Platform
    SamplesApi --> Platform
    TagsApi --> Platform
    SamplingsApi --> Platform
    ScoresApi --> Platform
    QuotaApi --> Platform
    PredictionsApi --> Platform
    MetaDataConfigurationsApi --> Platform
    CollaborationApi --> Platform
```

**Generated Client Initialization**: All generated API clients are instantiated in the `ApiWorkflowClient.__init__` method and stored as instance variables ([lightly/api/api_workflow_client.py:131-146]()):

- `self._datasets_api`: Dataset CRUD operations
- `self._datasources_api`: Datasource configuration
- `self._compute_worker_api`: Worker registration and run scheduling
- `self._embeddings_api`: Embedding upload/download
- `self._jobs_api`: Async job status monitoring
- `self._tags_api`: Tag/selection management
- `self._samples_api`: Sample-level operations
- `self._mappings_api`: Sample ID/filename mappings
- `self._selection_api`: Sampling/selection strategies
- `self._scores_api`: Active learning scores
- `self._quota_api`: Quota information
- `self._predictions_api`: Prediction upload/download
- `self._metadata_configurations_api`: Metadata configuration
- `self._collaboration_api`: Dataset sharing

**API Client Configuration**: All clients share the same `LightlySwaggerApiClient` instance ([lightly/api/api_workflow_client.py:121]()) which contains:
- Authentication token in `configuration.api_key["ApiKeyAuth"]`
- Custom User-Agent header with platform and Python version information
- Server location from configuration (defaults to api.lightly.ai)

Sources: [lightly/api/api_workflow_client.py:131-146](), [lightly/openapi_generated/swagger_client/api]()

## Core Properties and Concepts

### Dataset ID Management

The `dataset_id` property provides automatic dataset selection when not explicitly set:

```python
# Get dataset_id - auto-selects last modified if not set
dataset_id = client.dataset_id  

# Set dataset_id explicitly (validates existence)
client.dataset_id = "dataset_xyz"  

# Or set by name
client.set_dataset_id_by_name("my-dataset")
```

**Lazy Loading**: When `dataset_id` is accessed but not set, the client queries all accessible datasets, sorts by `last_modified_at`, and selects the most recent one ([lightly/api/api_workflow_client.py:149-171]()). A warning is issued indicating which dataset was automatically selected.

**Validation**: When setting `dataset_id` via the property setter, the client validates that the dataset exists by calling `self.dataset_exists()` ([lightly/api/api_workflow_client.py:173-189]()).

**Shared Datasets**: The `shared` parameter in dataset-related methods controls whether to include datasets shared with the user or owned by teams ([lightly/api/api_workflow_datasets.py:50-79]()):
- `shared=False`: Only datasets owned by the user
- `shared=True`: Only shared/team datasets (excludes user's own)
- `shared=None`: All accessible datasets

Sources: [lightly/api/api_workflow_client.py:148-190](), [lightly/api/api_workflow_datasets.py:15-80]()

### File Ordering and Synchronization

The client maintains filename ordering consistency between local and server representations:

**Filename Retrieval**: The `get_filenames()` method downloads the complete list of filenames from the server in canonical order ([lightly/api/api_workflow_client.py:216-234]()):

```python
filenames = client.get_filenames()  # Expensive operation for large datasets
```

**Reordering Utility**: The `_order_list_by_filenames()` method ensures local lists match server ordering ([lightly/api/api_workflow_client.py:191-214]()). This is used internally when uploading embeddings or other per-sample data to ensure correct alignment.

Sources: [lightly/api/api_workflow_client.py:191-234]()

### File Upload with Signed URLs

The `upload_file_with_signed_url()` method handles file uploads to cloud storage via pre-signed URLs:

```python
response = client.upload_file_with_signed_url(
    file=open("data.csv", "rb"),
    signed_write_url="https://...",
    headers={"custom": "header"}
)
```

**Server-Side Encryption Support**: The method automatically adds AWS S3 server-side encryption headers when the `LIGHTLY_S3_SSE_KMS_KEY` environment variable is set ([lightly/api/api_workflow_client.py:265-286]()):
- If set to `"true"`: Uses AWS-managed keys (AES256)
- If set to a KMS key ARN: Uses customer-managed KMS key

**Datasource Detection**: The method detects the destination storage type from the signed URL and only applies S3-specific headers for S3 destinations ([lightly/api/api_workflow_client.py:270-272]()).

Sources: [lightly/api/api_workflow_client.py:236-295](), [lightly/api/api_workflow_client.py:48-49]()

## Version Compatibility Checking

The client performs automatic version compatibility checking during initialization to ensure the installed `lightly` package is compatible with the Lightly Platform API.

```mermaid
graph TB
    Init["ApiWorkflowClient.__init__"]
    VersionCheck["_version_checking.is_compatible_version"]
    GetMinVersion["VersioningApi.get_minimum_compatible_pip_version"]
    Compare["version_compare.version_compare"]
    Compatible{"Compatible?"}
    Warn["warnings.warn<br/>Incompatible version"]
    Continue["Continue initialization"]
    CatchErrors["Catch exceptions:<br/>ValueError, ApiException, HTTPError"]
    
    Init --> VersionCheck
    VersionCheck --> GetMinVersion
    GetMinVersion --> Compare
    Compare --> Compatible
    Compatible -->|No| Warn
    Compatible -->|Yes| Continue
    Warn --> Continue
    VersionCheck -.may raise.-> CatchErrors
    CatchErrors --> Continue
    
    style Warn fill:#fff9e6
```

**Check Process** ([lightly/api/api_workflow_client.py:97-118]()):

1. Call `_version_checking.is_compatible_version(__version__)` with current package version
2. Query platform API for minimum compatible version via `VersioningApi.get_minimum_compatible_pip_version()`
3. Compare current version against minimum version using semantic versioning
4. If incompatible, issue a `UserWarning` but continue initialization
5. If version check fails (network error, API error), silently continue

**Non-Blocking Design**: Version check failures are caught and ignored to prevent blocking client initialization in offline or restricted network environments ([lightly/api/api_workflow_client.py:108-118]()). The client remains functional even if version verification fails.

**Background Checking**: The package also performs a background version check on import to notify users of new releases without blocking ([lightly/__init__.py:83-92]()):

```python
# In lightly/__init__.py
if multiprocessing.current_process().name == "MainProcess":
    from lightly.api import _version_checking
    _version_checking.check_is_latest_version_in_background(
        current_version=__version__
    )
```

This spawns a daemon thread that checks for updates asynchronously.

Sources: [lightly/api/api_workflow_client.py:97-118](), [lightly/api/_version_checking.py:1-74](), [lightly/__init__.py:83-92]()

## Common Usage Patterns

### Dataset Creation and Selection

```python
from lightly.api import ApiWorkflowClient
from lightly.openapi_generated.swagger_client.models import DatasetType

# Create new dataset
client = ApiWorkflowClient(token="TOKEN")
client.create_dataset("my-dataset", dataset_type=DatasetType.IMAGES)

# Later session - connect to existing dataset
client = ApiWorkflowClient(token="TOKEN")
client.set_dataset_id_by_name("my-dataset")

# Create with unique name (auto-increment if exists)
client.create_new_dataset_with_unique_name("my-dataset")
```

**Dataset Query and Iteration** ([lightly/api/api_workflow_datasets.py:196-284]()):

```python
# Get all owned datasets
datasets = client.get_datasets(shared=False)

# Include shared/team datasets
all_datasets = client.get_datasets(shared=None)

# Iterate over datasets (memory efficient for large lists)
for dataset in client.get_datasets_iter(shared=False):
    print(dataset.name, dataset.id)

# Query by name
datasets = client.get_datasets_by_name("my-dataset", shared=False)
```

### Typical Workflow Sequence

```mermaid
sequenceDiagram
    participant User
    participant Client as ApiWorkflowClient
    participant DatasetsAPI as _datasets_api
    participant DatasourceAPI as _datasources_api
    participant EmbeddingsAPI as _embeddings_api
    participant TagsAPI as _tags_api
    participant Platform as Lightly Platform
    
    User->>Client: create_dataset("my-dataset")
    Client->>DatasetsAPI: create_dataset(DatasetCreateRequest)
    DatasetsAPI->>Platform: POST /datasets
    Platform-->>DatasetsAPI: CreateEntityResponse(id)
    DatasetsAPI-->>Client: dataset_id
    
    User->>Client: set_datasource(config)
    Client->>DatasourceAPI: update_datasource_by_dataset_id()
    DatasourceAPI->>Platform: PUT /datasets/{id}/datasources
    
    User->>Client: upload_embeddings("embeddings.csv")
    Client->>EmbeddingsAPI: get_embeddings_csv_write_url()
    EmbeddingsAPI->>Platform: GET /embeddings/write-url
    Platform-->>EmbeddingsAPI: signed_write_url
    Client->>Platform: PUT signed_write_url (CSV data)
    
    User->>Client: get_tags()
    Client->>TagsAPI: get_tags_by_dataset_id()
    TagsAPI->>Platform: GET /datasets/{id}/tags
    Platform-->>TagsAPI: List[TagData]
    TagsAPI-->>Client: tags
    Client-->>User: tags
```

This sequence shows a common workflow: creating a dataset, configuring its datasource, uploading embeddings for analysis, and retrieving tags (selections).

Sources: [lightly/api/api_workflow_datasets.py:354-426](), [lightly/api/api_workflow_client.py:90-147]()

## Error Handling and Validation

The client performs validation at multiple levels:

**Dataset Validation** ([lightly/api/api_workflow_datasets.py:26-48]()):
- `dataset_exists(dataset_id)`: Returns `True/False`, raises non-404 `ApiException`
- `dataset_name_exists(dataset_name)`: Checks name existence with configurable shared scope
- Setting `dataset_id` property validates existence and raises `ValueError` if not found

**Duplicate Prevention** ([lightly/api/api_workflow_datasets.py:392-398]()):
```python
# Raises ValueError if dataset already exists
client.create_dataset("existing-name")  

# Creates with incremented suffix if exists
client.create_new_dataset_with_unique_name("existing-name")  # -> "existing-name_1"
```

**Multiple Dataset Warning** ([lightly/api/api_workflow_datasets.py:339-352]()): When multiple datasets with the same name exist (due to sharing), `set_dataset_id_by_name()` issues a warning and uses the first match, suggesting to use `shared=False` to avoid ambiguity.

Sources: [lightly/api/api_workflow_datasets.py:26-509](), [lightly/openapi_generated/swagger_client/rest.py]()

## Testing Infrastructure

The client includes comprehensive mocking infrastructure for testing:

**MockedApiWorkflowClient** ([tests/api_workflow/mocked_api_workflow_client.py:1033-1900]()):
- Extends `ApiWorkflowClient` with mocked API implementations
- Replaces all generated API clients with mock versions
- Enables unit testing without network calls
- Simulates realistic API responses

**Mock API Implementations** include:
- `MockedDatasetsApi`: Dataset CRUD with in-memory storage
- `MockedEmbeddingsApi`: Simulated embedding upload/download
- `MockedTagsApi`: Tag management with predefined tags
- `MockedJobsApi`: Job status simulation with state transitions
- `MockedComputeWorkerApi`: Worker registration and run scheduling

Each mock maintains internal state to simulate realistic API behavior across multiple calls.

Sources: [tests/api_workflow/mocked_api_workflow_client.py:1-1900](), [tests/api_workflow/test_api_workflow.py:1-121]()

---

# Page: Compute Workers

# Compute Workers

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [lightly/api/api_workflow_compute_worker.py](lightly/api/api_workflow_compute_worker.py)
- [lightly/openapi_generated/swagger_client/__init__.py](lightly/openapi_generated/swagger_client/__init__.py)
- [lightly/openapi_generated/swagger_client/api/datasets_api.py](lightly/openapi_generated/swagger_client/api/datasets_api.py)
- [lightly/openapi_generated/swagger_client/api/datasources_api.py](lightly/openapi_generated/swagger_client/api/datasources_api.py)
- [lightly/openapi_generated/swagger_client/api/docker_api.py](lightly/openapi_generated/swagger_client/api/docker_api.py)
- [lightly/openapi_generated/swagger_client/api/embeddings_api.py](lightly/openapi_generated/swagger_client/api/embeddings_api.py)
- [lightly/openapi_generated/swagger_client/api/samples_api.py](lightly/openapi_generated/swagger_client/api/samples_api.py)
- [lightly/openapi_generated/swagger_client/api/tags_api.py](lightly/openapi_generated/swagger_client/api/tags_api.py)
- [lightly/openapi_generated/swagger_client/models/__init__.py](lightly/openapi_generated/swagger_client/models/__init__.py)
- [lightly/openapi_generated/swagger_client/models/api_error_code.py](lightly/openapi_generated/swagger_client/models/api_error_code.py)
- [lightly/openapi_generated/swagger_client/models/create_sample_with_write_urls_response.py](lightly/openapi_generated/swagger_client/models/create_sample_with_write_urls_response.py)
- [tests/api_workflow/test_api_workflow_compute_worker.py](tests/api_workflow/test_api_workflow_compute_worker.py)

</details>



## Purpose and Scope

This page documents the Lightly Worker (formerly Docker Worker) integration within the `ApiWorkflowClient`, covering worker registration, configuration creation, run scheduling, status monitoring, and the complete lifecycle of worker runs. Workers are compute instances that execute data processing tasks (selection, embedding generation, active learning) on behalf of the Lightly Platform.

For information about other platform integration features, see:
- Dataset and tag management: [Dataset and Tag Management](#6.3)
- Datasource configuration: [Datasources](#6.4)
- Overall API client architecture: [API Workflow Client](#6.1)

**Sources:** [lightly/api/api_workflow_compute_worker.py:1-729]()

---

## Worker Registration and Management

### Worker Registration

Workers must be registered with the platform before they can execute runs. Registration creates a worker identity with a name and optional labels for run assignment.

```mermaid
graph LR
    UserCode["User Code"] --> register["_ComputeWorkerMixin.<br/>register_compute_worker()"]
    register --> CreateRequest["CreateDockerWorkerRegistryEntryRequest"]
    CreateRequest --> ComputeWorkerAPI["self._compute_worker_api<br/>(DockerApi)"]
    ComputeWorkerAPI --> RegisterEndpoint["register_docker_worker()"]
    RegisterEndpoint --> Platform["Lightly Platform API<br/>/v1/docker/worker"]
    Platform --> Response["CreateEntityResponse"]
    Response --> WorkerID["worker_id: str"]
    
    CreateRequest --> |"name: str"| RequestFields["Request Fields"]
    CreateRequest --> |"labels: List[str]"| RequestFields
    CreateRequest --> |"worker_type: FULL"| RequestFields
    CreateRequest --> |"creator: self._creator"| RequestFields
```

**Worker Registration Flow**

The `_ComputeWorkerMixin` class provides these worker management methods:

| Method | Location | Parameters | Returns | Description |
|--------|----------|-----------|---------|-------------|
| `register_compute_worker` | [api_workflow_compute_worker.py:85-119]() | `name: str`, `labels: Optional[List[str]]` | `str` (worker ID) | Registers a new worker or returns existing worker ID if name already exists |
| `get_compute_worker_ids` | [api_workflow_compute_worker.py:121-135]() | None | `List[str]` | Fetches all registered worker IDs |
| `get_compute_workers` | [api_workflow_compute_worker.py:136-157]() | None | `List[DockerWorkerRegistryEntryData]` | Fetches detailed information about all workers |
| `delete_compute_worker` | [api_workflow_compute_worker.py:158-175]() | `worker_id: str` | `None` | Removes a registered worker |

**Sources:** [lightly/api/api_workflow_compute_worker.py:84-175]()

### Worker Labels and Assignment

Labels enable selective run assignment. Workers with matching labels can pick up scheduled runs that specify those labels via the `runs_on` parameter.

```python
# Register worker with labels
worker_id = client.register_compute_worker(
    name="gpu-worker-1",
    labels=["gpu", "high-memory"]
)

# Schedule run for specific worker labels
run_id = client.schedule_compute_worker_run(
    selection_config={...},
    runs_on=["gpu"]  # Only workers with "gpu" label can pick up this run
)
```

**Sources:** [lightly/api/api_workflow_compute_worker.py:85-119](), [lightly/api/api_workflow_compute_worker.py:258-323]()

---

## Configuration System

### Configuration Structure

Worker runs require three types of configuration, all managed by `create_compute_worker_config`:

```mermaid
graph TB
    CreateConfigMethod["_ComputeWorkerMixin.<br/>create_compute_worker_config()"] --> ProcessWorker["Process worker_config"]
    CreateConfigMethod --> ProcessLightly["Process lightly_config"]
    CreateConfigMethod --> ProcessSelection["Process selection_config"]
    
    ProcessWorker --> |"If provided"| CamelCase1["_config_to_camel_case()"]
    CamelCase1 --> Deserialize1["_get_deserialize()<br/>klass=DockerWorkerConfigV4Docker"]
    Deserialize1 --> Validate1["_validate_config()"]
    Validate1 --> DockerConfig["DockerWorkerConfigV4Docker"]
    
    ProcessLightly --> |"If provided"| CamelCase2["_config_to_camel_case()"]
    CamelCase2 --> Deserialize2["_get_deserialize()<br/>klass=DockerWorkerConfigV3Lightly"]
    Deserialize2 --> Validate2["_validate_config()"]
    Validate2 --> LightlyConfig["DockerWorkerConfigV3Lightly"]
    
    ProcessSelection --> |"If dict"| SelectionConvert["selection_config_from_dict()"]
    ProcessSelection --> |"If SelectionConfigV4"| SelectionDirect["Use directly"]
    SelectionConvert --> SelectionConfig["SelectionConfigV4"]
    SelectionDirect --> SelectionConfig
    
    DockerConfig --> FinalConfig["DockerWorkerConfigV4"]
    LightlyConfig --> FinalConfig
    SelectionConfig --> FinalConfig
    FinalConfig --> CreateRequest["DockerWorkerConfigOmniVXCreateRequest"]
    CreateRequest --> API["_compute_worker_api.<br/>create_docker_worker_config_vx()"]
    API --> ConfigID["config_id: str"]
```

**Configuration Processing Flow**

| Configuration | Purpose | Optional | Class | Validation |
|--------------|---------|----------|-------|-----------|
| `worker_config` | Controls worker behavior (pretagging, training) | Yes | `DockerWorkerConfigV4Docker` | Via `_validate_config` |
| `lightly_config` | Controls data loading and processing | Yes | `DockerWorkerConfigV3Lightly` | Via `_validate_config` |
| `selection_config` | Defines selection strategies and sample count | No | `SelectionConfigV4` | Via Pydantic validation |

**Sources:** [lightly/api/api_workflow_compute_worker.py:176-257]()

### Configuration Creation

The `create_compute_worker_config` method creates a configuration and returns its ID:

```python
config_id = client.create_compute_worker_config(
    worker_config={
        "training": {
            "task_name": "lightly_pretagging"
        }
    },
    lightly_config={
        "loader": {
            "batch_size": 64,
            "num_workers": 4
        }
    },
    selection_config={
        "n_samples": 20,
        "strategies": [
            {
                "input": {"type": "EMBEDDINGS"},
                "strategy": {"type": "DIVERSITY"}
            }
        ]
    }
)
```

**Sources:** [lightly/api/api_workflow_compute_worker.py:176-257]()

### Selection Configuration

The `selection_config_from_dict` function converts dictionary configurations to `SelectionConfigV4` instances:

```mermaid
graph TB
    ConfigDict["User Dict"] --> SelectionFunc["selection_config_from_dict()<br/>[lines 627-639]"]
    SelectionFunc --> CopyDict["copy.deepcopy(cfg)"]
    CopyDict --> ProcessStrategies["Process strategies list"]
    ProcessStrategies --> ProcessAutoTasks["Process auto_tasks list"]
    
    ProcessStrategies --> StrategyLoop["For each entry in<br/>cfg['strategies']"]
    StrategyLoop --> EntryFunc["selection_config_entry_from_dict()<br/>[lines 641-646]"]
    EntryFunc --> CreateInput["SelectionConfigV4EntryInput(**entry['input'])"]
    EntryFunc --> CreateStrategy["SelectionConfigV4EntryStrategy(**entry['strategy'])"]
    CreateInput --> CreateEntry["SelectionConfigV4Entry(input, strategy)"]
    CreateStrategy --> CreateEntry
    
    ProcessAutoTasks --> AutoLoop["For each entry in<br/>cfg['auto_tasks']"]
    AutoLoop --> AutoFunc["auto_task_from_dict()<br/>[lines 648-660]"]
    AutoFunc --> CheckType["Check entry['type']"]
    CheckType --> |"TILING"| CreateTiling["AutoTaskTiling(**entry)"]
    CheckType --> |"Unknown"| RaiseError["ValueError: type not supported"]
    CreateTiling --> WrapAutoTask["AutoTask(actual_instance=...)"]
    
    CreateEntry --> FinalConfig["SelectionConfigV4(**new_cfg)"]
    WrapAutoTask --> FinalConfig
    FinalConfig --> Return["Return SelectionConfigV4"]
```

**Selection Configuration Classes**

| Class | Location | Purpose |
|-------|----------|---------|
| `SelectionConfigV4` | [swagger_client/models]() | Top-level config with `n_samples`, `strategies`, `auto_tasks` |
| `SelectionConfigV4Entry` | [swagger_client/models]() | Single strategy with `input` and `strategy` |
| `SelectionConfigV4EntryInput` | [swagger_client/models]() | Input specification (type: EMBEDDINGS, SCORES, METADATA, etc.) |
| `SelectionConfigV4EntryStrategy` | [swagger_client/models]() | Strategy type (DIVERSITY, SIMILARITY, THRESHOLD, etc.) |
| `AutoTask` | [swagger_client/models]() | Wrapper for auto tasks (currently supports TILING) |
| `AutoTaskTiling` | [swagger_client/models]() | Tiling configuration with `num_rows`, `num_cols`, `overlap` |

**Sources:** [lightly/api/api_workflow_compute_worker.py:627-660]()

### Configuration Validation

Configuration validation occurs through three helper functions defined in `api_workflow_compute_worker.py`:

```mermaid
graph TB
    UserDict["User Config Dict<br/>(snake_case keys)"] --> ConvertKeys["_config_to_camel_case()<br/>[lines 681-691]"]
    ConvertKeys --> RecursiveConvert["Recursively converts<br/>all nested dict keys"]
    RecursiveConvert --> CamelDict["Dict with camelCase keys"]
    
    CamelDict --> Deserialize["_get_deserialize()<br/>[lines 665-679]"]
    Deserialize --> UseApiClient["Uses ApiClient.__deserialize<br/>via getattr()"]
    UseApiClient --> DeserializedObj["OpenAPI Model Instance"]
    
    DeserializedObj --> Validate["_validate_config()<br/>[lines 699-729]"]
    Validate --> CheckKeys["For each key in cfg:<br/>Check hasattr(obj, key)"]
    CheckKeys --> |"Key exists"| RecurseNested["If value is dict,<br/>recurse into nested object"]
    CheckKeys --> |"Key missing"| FindMatch["difflib.get_close_matches()"]
    FindMatch --> RaiseError["Raise InvalidConfigurationError<br/>with suggestion"]
    RecurseNested --> Success["Validation Complete"]
    
    ConvertKeys --> |"Uses"| SnakeToCamel["_snake_to_camel_case()<br/>[lines 693-697]"]
    SnakeToCamel --> SplitUnderscores["Split on '_'"]
    SplitUnderscores --> Capitalize["Capitalize components[1:]"]
```

**Configuration Validation Functions**

| Function | Lines | Purpose | Key Operations |
|----------|-------|---------|----------------|
| `_snake_to_camel_case` | [693-697]() | Convert single key | `"batch_size"` → `"batchSize"` |
| `_config_to_camel_case` | [681-691]() | Convert entire dict | Recursively processes all keys |
| `_get_deserialize` | [665-679]() | Get deserializer | Returns `ApiClient.__deserialize` bound to target class |
| `_validate_config` | [699-729]() | Validate against schema | Uses `difflib` for suggestions on invalid keys |

**Sources:** [lightly/api/api_workflow_compute_worker.py:665-729]()

---

## Scheduling Runs

### Run Scheduling Process

The `schedule_compute_worker_run` method combines configuration creation with run scheduling:

```mermaid
sequenceDiagram
    participant User
    participant Mixin as _ComputeWorkerMixin
    participant CreateConfig as create_compute_worker_config
    participant DockerAPI as self._compute_worker_api
    participant Platform as Platform API
    
    User->>Mixin: schedule_compute_worker_run(configs, runs_on)
    Mixin->>CreateConfig: Call with worker_config,<br/>lightly_config, selection_config
    CreateConfig->>CreateConfig: Validate & serialize configs
    CreateConfig->>DockerAPI: create_docker_worker_config_vx()
    DockerAPI-->>CreateConfig: config_id
    CreateConfig-->>Mixin: config_id
    
    Mixin->>Mixin: Create DockerRunScheduledCreateRequest<br/>(config_id, priority, runs_on, creator)
    Mixin->>DockerAPI: create_docker_run_scheduled_by_dataset_id<br/>(request, dataset_id)
    DockerAPI->>Platform: POST /v1/datasets/{id}/docker/worker/schedule
    Platform-->>DockerAPI: CreateEntityResponse
    DockerAPI-->>Mixin: response.id
    Mixin-->>User: scheduled_run_id
```

**Run Scheduling Methods**

| Method | Lines | Returns | Description |
|--------|-------|---------|-------------|
| `schedule_compute_worker_run` | [258-323]() | `str` (scheduled run ID) | Creates config and schedules run in one operation |
| `create_compute_worker_config` | [176-257]() | `str` (config ID) | Creates reusable configuration |
| `get_scheduled_compute_worker_runs` | [436-473]() | `List[DockerRunScheduledData]` | Lists scheduled runs for current dataset |

**Sources:** [lightly/api/api_workflow_compute_worker.py:176-323](), [lightly/api/api_workflow_compute_worker.py:436-473]()

### Priority and Worker Assignment

Scheduled runs support priority levels and worker label matching:

```python
run_id = client.schedule_compute_worker_run(
    selection_config={...},
    priority=DockerRunScheduledPriority.HIGH,  # HIGH, MID, LOW
    runs_on=["gpu", "high-memory"]  # Worker must have ALL these labels
)
```

**Sources:** [lightly/api/api_workflow_compute_worker.py:258-323]()

---

## Monitoring Run Status

### Run Information Retrieval

The `get_compute_worker_run_info` method handles three database states:

```mermaid
graph TB
    GetInfo["get_compute_worker_run_info(scheduled_run_id)<br/>[lines 502-554]"] --> TryCase1["Case 1: Try get_docker_run_by_scheduled_id()"]
    
    TryCase1 --> |"Success"| DockerExists["DockerRunData found"]
    DockerExists --> ExtractState1["Extract run.state and run.message"]
    ExtractState1 --> Return1["Return ComputeWorkerRunInfo<br/>state=DockerRunState<br/>message=run.message"]
    
    TryCase1 --> |"ApiException"| TryCase2["Case 2: Try _get_scheduled_run_by_id()"]
    TryCase2 --> |"Success"| ScheduledExists["DockerRunScheduledData found"]
    ScheduledExists --> Return2["Return ComputeWorkerRunInfo<br/>state=DockerRunScheduledState.OPEN<br/>message='Waiting for pickup...'"]
    
    TryCase2 --> |"ApiException"| Case3["Case 3: Neither found"]
    Case3 --> Return3["Return ComputeWorkerRunInfo<br/>state=STATE_SCHEDULED_ID_NOT_FOUND<br/>message='Could not find job...'"]
    
    PrivateMethod["_get_scheduled_run_by_id()<br/>[lines 474-501]"] --> CallAPI["get_docker_runs_scheduled_by_dataset_id()"]
    CallAPI --> FilterList["Filter by run.id == scheduled_run_id"]
    FilterList --> |"Found"| ReturnRun["Return DockerRunScheduledData"]
    FilterList --> |"Not found"| RaiseException["Raise ApiException"]
```

**Run Status Methods**

| Method | Lines | Input | Returns | Description |
|--------|-------|-------|---------|-------------|
| `get_compute_worker_run_info` | [502-554]() | `scheduled_run_id: str` | `ComputeWorkerRunInfo` | Get current run status (handles 3 cases) |
| `_get_scheduled_run_by_id` | [474-501]() | `scheduled_run_id: str` | `DockerRunScheduledData` | Private: Find scheduled run by ID |
| `get_compute_worker_run` | [378-403]() | `run_id: str` | `DockerRunData` | Get run details by run ID |
| `get_compute_worker_run_from_scheduled_run` | [404-435]() | `scheduled_run_id: str` | `DockerRunData` | Get run details by scheduled run ID |
| `get_compute_worker_runs` | [349-377]() | `dataset_id: Optional[str]` | `List[DockerRunData]` | List all runs, optionally filtered by dataset |
| `get_compute_worker_runs_iter` | [324-348]() | `dataset_id: Optional[str]` | `Iterator[DockerRunData]` | Iterator version for pagination |
| `get_compute_worker_run_tags` | [598-625]() | `run_id: str` | `List[TagData]` | Get tags created by the run (version ≥2.4.2) |

**Sources:** [lightly/api/api_workflow_compute_worker.py:324-625]()

### ComputeWorkerRunInfo Dataclass

The `ComputeWorkerRunInfo` dataclass defined at [lines 42-82]() encapsulates run state:

```mermaid
graph TB
    DataClass["@dataclasses.dataclass<br/>ComputeWorkerRunInfo"] --> StateField["state: Union[<br/>DockerRunState,<br/>DockerRunScheduledState.OPEN,<br/>STATE_SCHEDULED_ID_NOT_FOUND]"]
    DataClass --> MessageField["message: str"]
    DataClass --> InEndState["in_end_state() -> bool"]
    DataClass --> EndedSuccess["ended_successfully() -> bool"]
    
    InEndState --> CheckState["Check if state in:<br/>COMPLETED, ABORTED,<br/>FAILED, CRASHED,<br/>CANCELED_OR_NOT_EXISTING"]
    
    EndedSuccess --> RequireEnd["Requires in_end_state() == True"]
    RequireEnd --> |"True"| CheckComplete["Return state == COMPLETED"]
    RequireEnd --> |"False"| RaiseValue["Raise ValueError"]
```

**ComputeWorkerRunInfo Methods**

| Method | Lines | Returns | Behavior |
|--------|-------|---------|----------|
| `in_end_state()` | [58-67]() | `bool` | Returns `True` if `state` is COMPLETED, ABORTED, FAILED, CRASHED, or CANCELED_OR_NOT_EXISTING |
| `ended_successfully()` | [68-82]() | `bool` | Returns `True` if state is COMPLETED; raises `ValueError` if run still in progress |

**Constants**

- `STATE_SCHEDULED_ID_NOT_FOUND = "CANCELED_OR_NOT_EXISTING"` [line 35]() - Special state when neither DockerRun nor ScheduledRun exists

**Sources:** [lightly/api/api_workflow_compute_worker.py:35-82]()

### Continuous Monitoring

The `compute_worker_run_info_generator` method at [lines 555-597]() provides continuous status polling:

```mermaid
graph TB
    Generator["compute_worker_run_info_generator(scheduled_run_id)"] --> InitVars["last_run_info = None"]
    InitVars --> InfiniteLoop["while True:"]
    
    InfiniteLoop --> GetInfo["run_info = get_compute_worker_run_info()"]
    GetInfo --> Compare["if run_info != last_run_info:"]
    Compare --> |"Changed"| Yield["yield run_info"]
    Compare --> |"Same"| Skip["Skip yield"]
    
    Yield --> CheckEnd["if run_info.in_end_state():"]
    Skip --> CheckEnd
    CheckEnd --> |"True"| Break["break"]
    CheckEnd --> |"False"| Sleep["time.sleep(30)"]
    
    Sleep --> UpdateLast["last_run_info = run_info"]
    UpdateLast --> InfiniteLoop
    Break --> StopIteration["StopIteration"]
```

**Generator Behavior**

| Aspect | Implementation | Note |
|--------|----------------|------|
| Polling Interval | `time.sleep(30)` [line 594]() | 30 seconds minimum to prevent rate limiting |
| State Change Detection | `run_info != last_run_info` [line 586]() | Only yields when state or message changes |
| Exit Condition | `run_info.in_end_state()` [line 590]() | Stops on COMPLETED, FAILED, ABORTED, CRASHED, or NOT_FOUND |
| State Tracking | `last_run_info = run_info` [line 596]() | Remembers previous state to detect changes |

**Example Usage:**

```python
# Poll status every 30 seconds until completion
for run_info in client.compute_worker_run_info_generator(scheduled_run_id):
    print(f"State: {run_info.state}, Message: {run_info.message}")
    
# Generator automatically stops when run reaches end state
```

**Sources:** [lightly/api/api_workflow_compute_worker.py:555-597]()

---

## Run Lifecycle

### State Transitions

```mermaid
stateDiagram-v2
    [*] --> OPEN: Run scheduled
    OPEN --> LOCKED: Worker picks up run
    LOCKED --> TRAINING: Worker starts processing
    TRAINING --> EMBEDDING: Training complete
    EMBEDDING --> SELECTING: Embeddings generated
    SELECTING --> GENERATING_REPORT: Selection complete
    GENERATING_REPORT --> COMPLETED: Report generated
    
    TRAINING --> FAILED: Error
    EMBEDDING --> FAILED: Error
    SELECTING --> FAILED: Error
    GENERATING_REPORT --> FAILED: Error
    
    OPEN --> CANCELED: Manual cancellation
    LOCKED --> CANCELED: Manual cancellation
    
    TRAINING --> ABORTED: User abort
    EMBEDDING --> ABORTED: User abort
    SELECTING --> ABORTED: User abort
    
    TRAINING --> CRASHED: Worker crash
    EMBEDDING --> CRASHED: Worker crash
    SELECTING --> CRASHED: Worker crash
    
    COMPLETED --> [*]
    FAILED --> [*]
    CANCELED --> [*]
    ABORTED --> [*]
    CRASHED --> [*]
```

**Worker Run States**

### Scheduled Run States

| State | Description | End State |
|-------|-------------|-----------|
| `OPEN` | Run scheduled, waiting for worker pickup | No |
| `LOCKED` | Worker has claimed the run | No |
| `DONE` | Run processing complete (check DockerRun for actual outcome) | Yes |
| `CANCELED` | Run canceled before worker pickup | Yes |

**Sources:** [lightly/openapi_generated/swagger_client/models/docker_run_scheduled_state.py]()

### Docker Run States

| State | Description | End State | Success |
|-------|-------------|-----------|---------|
| `TRAINING` | Worker training models | No | - |
| `EMBEDDING` | Worker generating embeddings | No | - |
| `SELECTING` | Worker performing selection | No | - |
| `GENERATING_REPORT` | Worker creating report | No | - |
| `COMPLETED` | Run finished successfully | Yes | Yes |
| `FAILED` | Run failed with error | Yes | No |
| `ABORTED` | User aborted the run | Yes | No |
| `CRASHED` | Worker crashed during execution | Yes | No |

**Sources:** [lightly/api/api_workflow_compute_worker.py:42-82](), [lightly/openapi_generated/swagger_client/models/docker_run_state.py]()

### Three-State Lifecycle

The `get_compute_worker_run_info` method handles three distinct cases:

1. **DockerRun Exists**: Worker has picked up and started processing
   - Returns actual `DockerRunState` and message

2. **Only ScheduledRun Exists**: Run scheduled but not yet claimed
   - Returns `DockerRunScheduledState.OPEN`
   - Message: "Waiting for pickup by Lightly Worker..."

3. **Neither Exists**: Run canceled or never existed
   - Returns `STATE_SCHEDULED_ID_NOT_FOUND`
   - Message: "Could not find a job for the given run_id..."

**Sources:** [lightly/api/api_workflow_compute_worker.py:502-554]()

---

## Integration with ApiWorkflowClient

### Mixin Architecture

The `_ComputeWorkerMixin` class provides worker functionality to `ApiWorkflowClient`:

```mermaid
graph TB
    ApiWorkflowClient["ApiWorkflowClient"] --> |"inherits from"| ComputeWorkerMixin["_ComputeWorkerMixin"]
    ApiWorkflowClient --> |"inherits from"| OtherMixins["Other Mixins<br/>(_DatasetsMixin, _TagsMixin, etc.)"]
    
    ComputeWorkerMixin --> |"uses"| ComputeWorkerAPI["self._compute_worker_api<br/>(DockerApi)"]
    ComputeWorkerMixin --> |"uses"| APIClient["self.api_client<br/>(LightlySwaggerApiClient)"]
    
    ComputeWorkerAPI --> |"calls"| PlatformEndpoints["Platform REST API<br/>/docker/worker/*<br/>/docker/run/*"]
```

**Key Client Properties**

The mixin accesses shared client state:
- `self._compute_worker_api`: Instance of `DockerApi` for API calls
- `self.api_client`: Shared `ApiClient` for deserialization
- `self.dataset_id`: Current dataset context
- `self._creator`: Creator tag for audit trail (e.g., `Creator.USER_PIP`)

**Sources:** [lightly/api/api_workflow_client.py:52-147](), [lightly/api/api_workflow_compute_worker.py:84-729]()

### Complete Usage Example

```python
from lightly.api import ApiWorkflowClient

# Initialize client
client = ApiWorkflowClient(token="YOUR_TOKEN", dataset_id="YOUR_DATASET_ID")

# 1. Register worker
worker_id = client.register_compute_worker(
    name="my-worker",
    labels=["gpu"]
)

# 2. Schedule run
scheduled_run_id = client.schedule_compute_worker_run(
    worker_config={
        "pretagging": True
    },
    lightly_config={
        "loader": {
            "batch_size": 64
        }
    },
    selection_config={
        "n_samples": 100,
        "strategies": [
            {
                "input": {"type": "EMBEDDINGS"},
                "strategy": {"type": "DIVERSITY"}
            }
        ]
    },
    runs_on=["gpu"]
)

# 3. Monitor run
for run_info in client.compute_worker_run_info_generator(scheduled_run_id):
    print(f"{run_info.state}: {run_info.message}")

# 4. Check result
if run_info.ended_successfully():
    # Get tags created by the run
    tags = client.get_compute_worker_run_tags(run_id=scheduled_run_id)
    print(f"Created tags: {[tag.name for tag in tags]}")
```

**Sources:** [lightly/api/api_workflow_compute_worker.py:85-625](), [tests/api_workflow/test_api_workflow_compute_worker.py:61-201]()

---

## Error Handling

### Configuration Errors

Invalid configuration keys raise `InvalidConfigurationError` with suggestions:

```python
try:
    config_id = client.create_compute_worker_config(
        lightly_config={
            "loader": {
                "batch_siz": 64  # Typo: should be "batch_size"
            }
        }
    )
except InvalidConfigurationError as e:
    print(e)  # "Option 'batch_siz' does not exist! Did you mean 'batch_size'?"
```

**Sources:** [lightly/api/api_workflow_compute_worker.py:699-729]()

### API Errors

Run scheduling may raise `ApiException` with specific error codes:

| Status Code | Reason | Description |
|-------------|--------|-------------|
| 400 | Bad Request | Missing or invalid parameters |
| 402 | Payment Required | Insufficient plan for requested operation |
| 403 | Forbidden | Invalid token or unauthorized access |
| 404 | Not Found | Dataset or config not found |
| 422 | Unprocessable Entity | Missing or invalid file in datasource |

**Sources:** [lightly/api/api_workflow_compute_worker.py:258-323](), [tests/api_workflow/test_api_workflow_compute_worker.py:538-628]()

---

## Testing Support

### MockedComputeWorkerApi

The test infrastructure provides a mocked API for testing worker operations:

```python
class MockedComputeWorkerApi(DockerApi):
    def register_docker_worker(self, body, **kwargs):
        # Returns CreateEntityResponse with generated ID
        
    def get_docker_worker_registry_entries(self, **kwargs):
        # Returns list of registered workers
        
    def create_docker_worker_config_vx(self, body, **kwargs):
        # Returns config ID
        
    def create_docker_run_scheduled_by_dataset_id(self, request, dataset_id, **kwargs):
        # Returns scheduled run ID
        
    def get_docker_runs(self, page_size, page_offset, **kwargs):
        # Returns paginated runs
```

**Sources:** [tests/api_workflow/mocked_api_workflow_client.py:830-994]()

---

# Page: Dataset and Tag Management

# Dataset and Tag Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [lightly/api/api_workflow_client.py](lightly/api/api_workflow_client.py)
- [lightly/api/api_workflow_datasets.py](lightly/api/api_workflow_datasets.py)
- [tests/api_workflow/mocked_api_workflow_client.py](tests/api_workflow/mocked_api_workflow_client.py)
- [tests/api_workflow/test_api_workflow.py](tests/api_workflow/test_api_workflow.py)
- [tests/api_workflow/test_api_workflow_datasets.py](tests/api_workflow/test_api_workflow_datasets.py)

</details>



This page documents dataset and tag management operations in the Lightly Platform through the `ApiWorkflowClient`. Datasets are containers that hold samples (images or videos), while tags represent named selections or subsets of samples within a dataset. These operations enable users to organize data, track sample selections from active learning or selection strategies, and export curated datasets for downstream tasks.

For information about configuring datasources to connect datasets to cloud storage, see [Datasources](#6.4). For uploading embeddings and running selection strategies, see [API Workflow Client](#6.1).

## Architecture Overview

The dataset and tag management functionality is implemented through a mixin-based architecture in the `ApiWorkflowClient`. The client delegates dataset operations to `_DatasetsMixin` and tag operations to `_TagsMixin`, which internally use OpenAPI-generated clients to communicate with the Lightly Platform REST API.

```mermaid
graph TB
    Client["ApiWorkflowClient"]
    DatasetsMixin["_DatasetsMixin"]
    TagsMixin["_TagsMixin"]
    DatasetsApi["DatasetsApi<br/>(OpenAPI Generated)"]
    TagsApi["TagsApi<br/>(OpenAPI Generated)"]
    MappingsApi["MappingsApi<br/>(OpenAPI Generated)"]
    Platform["Lightly Platform<br/>REST API"]
    
    Client -->|inherits| DatasetsMixin
    Client -->|inherits| TagsMixin
    DatasetsMixin -->|uses| DatasetsApi
    TagsMixin -->|uses| TagsApi
    TagsMixin -->|uses| MappingsApi
    DatasetsApi -->|HTTP requests| Platform
    TagsApi -->|HTTP requests| Platform
    MappingsApi -->|HTTP requests| Platform
    
    subgraph "Dataset Operations"
        DatasetsMixin
        DatasetsApi
    end
    
    subgraph "Tag Operations"
        TagsMixin
        TagsApi
        MappingsApi
    end
```

**Diagram: API Client Architecture for Dataset and Tag Management**

Sources: [lightly/api/api_workflow_client.py:52-66](), [lightly/api/api_workflow_client.py:131-142]()

## Dataset Management

### Dataset Data Model

A dataset in the Lightly Platform is represented by the `DatasetData` model, which contains metadata about the dataset including its ID, name, type, creation timestamp, and ownership information.

| Field | Type | Description |
|-------|------|-------------|
| `id` | `str` | Unique dataset identifier |
| `name` | `str` | Human-readable dataset name |
| `type` | `str` | Dataset type: `"Images"` or `"Videos"` |
| `created_at` | `int` | Unix timestamp of creation |
| `last_modified_at` | `int` | Unix timestamp of last modification |
| `user_id` | `str` | Owner user ID |
| `size_in_bytes` | `int` | Total size of dataset samples |
| `n_samples` | `int` | Number of samples in dataset |

Sources: [tests/api_workflow/mocked_api_workflow_client.py:525-537](), [lightly/openapi_generated/swagger_client/models]()

### Dataset Context in ApiWorkflowClient

The `ApiWorkflowClient` maintains a current dataset context through the `dataset_id` property. Once set, all subsequent operations automatically use this dataset unless explicitly overridden.

```mermaid
graph LR
    User["User Code"]
    Client["ApiWorkflowClient"]
    Property["dataset_id property"]
    Explicit["Explicitly set:<br/>client.dataset_id = 'xxx'"]
    Implicit["Auto-selected:<br/>last modified dataset"]
    
    User -->|"access dataset_id"| Client
    Client --> Property
    Property --> Explicit
    Property -->|"fallback if not set"| Implicit
```

**Diagram: Dataset Context Resolution**

The `dataset_id` property implements lazy initialization. If not explicitly set, it queries all datasets and selects the most recently modified one, issuing a warning to the user.

Sources: [lightly/api/api_workflow_client.py:148-171](), [lightly/api/api_workflow_client.py:173-189]()

### Creating Datasets

#### create_dataset()

Creates a new dataset with a specified name. Raises `ValueError` if a dataset with the same name already exists.

```python
from lightly.api import ApiWorkflowClient
from lightly.openapi_generated.swagger_client.models import DatasetType

client = ApiWorkflowClient(token="YOUR_TOKEN")
client.create_dataset('my-dataset', dataset_type=DatasetType.IMAGES)
dataset_id = client.dataset_id  # Automatically set to new dataset
```

**Method signature:** [lightly/api/api_workflow_datasets.py:354-402]()

Sources: [lightly/api/api_workflow_datasets.py:354-402](), [tests/api_workflow/test_api_workflow_datasets.py:467-480]()

#### create_new_dataset_with_unique_name()

Creates a dataset with a unique name by appending a counter suffix if the base name already exists. This is useful for automated workflows that need to ensure unique dataset names without manual checking.

```python
# First call creates "experiment-1"
client.create_new_dataset_with_unique_name('experiment-1')

# Second call creates "experiment-1_1" since "experiment-1" exists
client.create_new_dataset_with_unique_name('experiment-1')
```

**Implementation details:** The method queries existing datasets with names starting with the basename, finds the highest numeric suffix, and creates a dataset with `basename_{max_suffix + 1}`.

Sources: [lightly/api/api_workflow_datasets.py:427-486](), [tests/api_workflow/test_api_workflow_datasets.py:133-149]()

### Querying Datasets

The API client provides multiple methods to query and retrieve dataset information, with support for shared datasets and team access.

```mermaid
graph TB
    Query["Dataset Query Methods"]
    ByID["get_dataset_by_id(dataset_id)"]
    ByName["get_datasets_by_name(dataset_name, shared)"]
    AllDatasets["get_datasets(shared)"]
    Iterator["get_datasets_iter(shared)"]
    Exists["dataset_exists(dataset_id)"]
    NameExists["dataset_name_exists(dataset_name, shared)"]
    
    Query --> ByID
    Query --> ByName
    Query --> AllDatasets
    Query --> Iterator
    Query --> Exists
    Query --> NameExists
    
    SharedParam["'shared' parameter:<br/>False: own datasets only<br/>True: shared datasets only<br/>None: all accessible datasets"]
    
    ByName -.uses.- SharedParam
    AllDatasets -.uses.- SharedParam
    Iterator -.uses.- SharedParam
    NameExists -.uses.- SharedParam
```

**Diagram: Dataset Query Methods**

Sources: [lightly/api/api_workflow_datasets.py:81-104](), [lightly/api/api_workflow_datasets.py:106-194]()

#### Shared Dataset Access

The `shared` parameter controls which datasets are returned in query operations:

- `shared=False` (default): Returns only datasets owned by the current user
- `shared=True`: Returns datasets shared with the user and team datasets, excluding owned datasets
- `shared=None`: Returns all datasets the user has access to (owned + shared + team)

The implementation handles potential duplicates when `shared=None` by de-duplicating based on dataset IDs.

Sources: [lightly/api/api_workflow_datasets.py:196-248](), [tests/api_workflow/test_api_workflow_datasets.py:230-278]()

#### get_dataset_by_id()

Retrieves a single dataset by its unique identifier. Raises `ApiException` with status 404 if the dataset does not exist.

**Method signature:** [lightly/api/api_workflow_datasets.py:81-104]()

#### get_datasets_by_name()

Returns a list of datasets matching the specified name. Can return multiple datasets if shared access is enabled and multiple users have datasets with the same name.

**Method signature:** [lightly/api/api_workflow_datasets.py:106-194]()

Example:
```python
# Get only owned datasets
datasets = client.get_datasets_by_name('my-dataset', shared=False)

# Get all datasets with this name (owned + shared)
all_datasets = client.get_datasets_by_name('my-dataset', shared=None)
```

Sources: [lightly/api/api_workflow_datasets.py:106-194](), [tests/api_workflow/test_api_workflow_datasets.py:280-398]()

#### get_datasets() and get_datasets_iter()

Returns all datasets accessible to the user. The `get_datasets_iter()` method returns an iterator for memory-efficient processing of large dataset lists, while `get_datasets()` returns a complete list.

**Implementation note:** Both methods use pagination internally through `utils.paginate_endpoint()` to handle large result sets.

Sources: [lightly/api/api_workflow_datasets.py:196-284](), [tests/api_workflow/test_api_workflow_datasets.py:230-278]()

### Setting Dataset Context

#### set_dataset_id_by_name()

Sets the current dataset context by name rather than ID. This is useful when starting a new session and you know the dataset name but not its ID.

```python
client = ApiWorkflowClient(token="YOUR_TOKEN")
client.set_dataset_id_by_name('existing-dataset')
# Future operations now use this dataset automatically
```

If multiple datasets with the same name exist (e.g., shared datasets), the method uses the first match and emits a warning.

Sources: [lightly/api/api_workflow_datasets.py:300-352](), [tests/api_workflow/test_api_workflow_datasets.py:401-464]()

### Deleting Datasets

#### delete_dataset_by_id()

Permanently deletes a dataset from the Lightly Platform. This operation also clears the `dataset_id` property from the client instance.

**Warning:** This operation is irreversible and will delete all samples, tags, embeddings, and other data associated with the dataset.

Sources: [lightly/api/api_workflow_datasets.py:488-508](), [tests/api_workflow/test_api_workflow_datasets.py:219-227]()

### Dataset Type Property

The `dataset_type` property returns the type of the current dataset (`"Images"` or `"Videos"`). This is a read-only property that queries the platform for the current dataset's type.

Sources: [lightly/api/api_workflow_datasets.py:16-24](), [tests/api_workflow/test_api_workflow_datasets.py:211-216]()

## Tag Management

Tags represent named subsets or selections of samples within a dataset. They are the primary mechanism for tracking which samples have been selected by active learning strategies, manual curation, or automated selection algorithms.

### Tag Data Model

A tag is represented by the `TagData` model with the following key fields:

| Field | Type | Description |
|-------|------|-------------|
| `id` | `str` | Unique tag identifier |
| `dataset_id` | `str` | Parent dataset ID |
| `name` | `str` | Human-readable tag name |
| `prev_tag_id` | `str` | Previous tag ID (for tag history) |
| `bit_mask_data` | `str` | Hexadecimal bitmask of selected samples |
| `tot_size` | `int` | Number of samples in the tag |
| `created_at` | `int` | Unix timestamp of creation |

Sources: [tests/api_workflow/mocked_api_workflow_client.py:217-256]()

### Tag Hierarchy and History

Tags form a directed acyclic graph (DAG) where each tag can reference a previous tag through `prev_tag_id`. This enables tracking the evolution of sample selections over time, particularly useful in active learning loops.

```mermaid
graph LR
    Initial["initial-tag<br/>prev_tag_id: None<br/>size: 100"]
    Round1["round-1-selection<br/>prev_tag_id: initial-tag<br/>size: 80"]
    Round2["round-2-selection<br/>prev_tag_id: round-1-selection<br/>size: 60"]
    Manual["manual-review<br/>prev_tag_id: initial-tag<br/>size: 95"]
    
    Initial --> Round1
    Round1 --> Round2
    Initial --> Manual
```

**Diagram: Tag Hierarchy Example**

Sources: [tests/api_workflow/mocked_api_workflow_client.py:217-256]()

### Tag Operations via TagsApi

The `_TagsMixin` provides high-level tag management operations by wrapping the `TagsApi` OpenAPI client. Key operations include:

```mermaid
graph TB
    TagOps["Tag Operations"]
    Create["Create Operations"]
    Query["Query Operations"]
    Modify["Modification Operations"]
    Export["Export Operations"]
    
    TagOps --> Create
    TagOps --> Query
    TagOps --> Modify
    TagOps --> Export
    
    Create --> CreateInitial["create_initial_tag_by_dataset_id<br/>Creates first tag"]
    Create --> CreateNew["create_tag_by_dataset_id<br/>Creates derived tag"]
    
    Query --> GetAll["get_tags_by_dataset_id<br/>Lists all tags"]
    Query --> GetOne["get_tag_by_tag_id<br/>Gets specific tag"]
    
    Modify --> Arithmetic["perform_tag_arithmetics<br/>Union/intersection/difference"]
    Modify --> Delete["delete_tag_by_tag_id<br/>Removes leaf tag"]
    
    Export --> LabelStudio["export_tag_to_label_studio_tasks"]
    Export --> LabelBox["export_tag_to_label_box_data_rows"]
    Export --> BasicExport["export_tag_to_basic_filenames"]
```

**Diagram: Tag Operations Through TagsApi**

Sources: [tests/api_workflow/mocked_api_workflow_client.py:188-418](), [lightly/api/api_workflow_tags.py]()

### Creating Tags

#### Initial Tag Creation

The initial tag typically includes all samples in a dataset and serves as the root of the tag hierarchy. It's created using `create_initial_tag_by_dataset_id()`.

**API Method:** [tests/api_workflow/mocked_api_workflow_client.py:189-196]()

#### Creating Derived Tags

New tags are created through selection strategies or manual operations. Each new tag references a previous tag and contains a bitmask indicating which samples are included.

**API Method:** [tests/api_workflow/mocked_api_workflow_client.py:296-310]()

Sources: [tests/api_workflow/mocked_api_workflow_client.py:189-310]()

### Querying Tags

#### get_tags_by_dataset_id()

Returns all tags for a dataset. Tags are returned as a list of `TagData` objects containing metadata and the bitmask representation of selected samples.

Example mock response structure:
```python
[
    TagData(id="tag-1", name="initial-tag", tot_size=100, prev_tag_id=None),
    TagData(id="tag-2", name="selection-1", tot_size=75, prev_tag_id="tag-1"),
    TagData(id="tag-3", name="selection-2", tot_size=50, prev_tag_id="tag-2")
]
```

**API Method:** [tests/api_workflow/mocked_api_workflow_client.py:214-270]()

#### get_tag_by_tag_id()

Retrieves detailed information about a specific tag including its bitmask, size, and ancestry.

**API Method:** [tests/api_workflow/mocked_api_workflow_client.py:198-212]()

Sources: [tests/api_workflow/mocked_api_workflow_client.py:188-270]()

### Tag Arithmetic Operations

Tag arithmetic enables creating new tag selections by combining existing tags using set operations (union, intersection, difference). The `perform_tag_arithmetics()` method accepts a `TagArithmeticsRequest` specifying the operation and operand tags.

```mermaid
graph LR
    TagA["Tag A<br/>{sample1, sample2, sample3}"]
    TagB["Tag B<br/>{sample2, sample3, sample4}"]
    
    Union["Union (A ∪ B)<br/>{sample1, sample2, sample3, sample4}"]
    Intersection["Intersection (A ∩ B)<br/>{sample2, sample3}"]
    Difference["Difference (A - B)<br/>{sample1}"]
    
    TagA --> Union
    TagB --> Union
    TagA --> Intersection
    TagB --> Intersection
    TagA --> Difference
    TagB --> Difference
```

**Diagram: Tag Arithmetic Operations**

The method can either return a bitmask result (if `new_tag_name` is not provided) or create a new persisted tag (if `new_tag_name` is provided).

Sources: [tests/api_workflow/mocked_api_workflow_client.py:272-287]()

### Tag Export Operations

Tags can be exported to various formats for integration with labeling tools and downstream workflows.

#### Export Formats

| Export Method | Format | Use Case |
|--------------|--------|----------|
| `export_tag_to_label_studio_tasks()` | Label Studio JSON | Integration with Label Studio annotation tool |
| `export_tag_to_label_box_data_rows()` | LabelBox JSON (v3) | Integration with LabelBox Classic |
| `export_tag_to_label_box_v4_data_rows()` | LabelBox JSON (v4) | Integration with LabelBox Editor |
| `export_tag_to_basic_filenames_and_read_urls()` | Filename + URL pairs | Programmatic access with read URLs |
| `export_tag_to_basic_filenames()` | Plain text filenames | Simple filename list |

All export methods support pagination through `page_offset` parameters to handle large tag selections.

Sources: [tests/api_workflow/mocked_api_workflow_client.py:320-418]()

#### Label Studio Export

Exports tag samples as Label Studio tasks with full sample metadata:

```python
[
    {
        "id": 0,
        "data": {
            "image": "https://api.lightly.ai/v1/datasets/{dataset_id}/samples/{sample_id}/readurlRedirect?type=full",
            "lightly_file_name": "image_001.jpg",
            "lightly_meta_info": {
                "id": "sample_id_0",
                "type": "IMAGE",
                "file_name": "image_001.jpg",
                "meta_data": {
                    "sharpness": 27.31,
                    "size_in_bytes": 48224,
                    ...
                }
            }
        }
    }
]
```

**API Method:** [tests/api_workflow/mocked_api_workflow_client.py:320-369]()

#### Basic Filename Export

Returns a simple newline-separated list of filenames:

```
IMG_2276_jpeg_jpg.rf.7411b1902c81bad8cdefd2cc4eb3a97b.jpg
IMG_2285_jpeg_jpg.rf.4a93d99b9f0b6cccfb27bf2f4a13b99e.jpg
IMG_2274_jpeg_jpg.rf.2f319e949748145fb22dcb52bb325a0c.jpg
```

**API Method:** [tests/api_workflow/mocked_api_workflow_client.py:408-417]()

Sources: [tests/api_workflow/mocked_api_workflow_client.py:320-418]()

### Deleting Tags

#### delete_tag_by_tag_id()

Deletes a tag from the dataset. The implementation enforces that only leaf tags (tags with no children) can be deleted, preventing orphaned tag hierarchies.

**Validation logic:**
1. Verify tag exists in dataset
2. Verify no other tags reference this tag as their `prev_tag_id`
3. Delete if validation passes

Sources: [tests/api_workflow/mocked_api_workflow_client.py:312-318]()

## Sample Filename Mapping

The `get_filenames()` method retrieves the ordered list of sample filenames from the server. This is a critical operation for maintaining sample order consistency across the platform and local operations.

```mermaid
graph LR
    Client["ApiWorkflowClient"]
    Method["get_filenames()"]
    MappingsApi["MappingsApi"]
    Paginate["paginate_endpoint<br/>page_size=25000"]
    Server["Lightly Platform"]
    
    Client --> Method
    Method --> MappingsApi
    MappingsApi --> Paginate
    Paginate -->|"HTTP GET<br/>/mappings"| Server
    Server -->|"List[str]"| Paginate
    Paginate --> Method
    Method -->|"Complete filename list"| Client
```

**Diagram: Filename Mapping Retrieval**

**Warning:** This operation is expensive for large datasets as it downloads all filenames. The results should be cached when possible.

**Implementation:** The method uses pagination with a page size of 25,000 to handle datasets of any size. It internally calls `_mappings_api.get_sample_mappings_by_dataset_id()` with field `"fileName"`.

Sources: [lightly/api/api_workflow_client.py:216-234](), [tests/api_workflow/mocked_api_workflow_client.py:431-444]()

## Sample Ordering

The `_order_list_by_filenames()` method reorders a list of values to match the server's canonical sample order. This is essential when uploading embeddings or predictions to ensure they align with the platform's sample indices.

**Use case:** When generating embeddings locally with shuffled data loaders, this method reorders the embeddings to match the server's filename order before upload.

```mermaid
graph TB
    Local["Local Data Order<br/>[img_c, img_a, img_b]"]
    Server["Server Canonical Order<br/>[img_a, img_b, img_c]"]
    Values["Associated Values<br/>[embedding_c, embedding_a, embedding_b]"]
    Reorder["_order_list_by_filenames()"]
    Result["Reordered Values<br/>[embedding_a, embedding_b, embedding_c]"]
    
    Local --> Reorder
    Server --> Reorder
    Values --> Reorder
    Reorder --> Result
```

**Diagram: Sample Reordering Process**

The method uses `reordering.sort_items_by_keys()` utility to perform the reordering and validates that all server filenames are present in the provided filename list.

Sources: [lightly/api/api_workflow_client.py:191-214](), [tests/api_workflow/test_api_workflow.py:59-120]()

## Integration Pattern

The typical workflow for dataset and tag management follows this pattern:

```mermaid
sequenceDiagram
    participant User as User Code
    participant Client as ApiWorkflowClient
    participant Datasets as _DatasetsMixin
    participant Tags as _TagsMixin
    participant Platform as Lightly Platform
    
    User->>Client: Initialize with token
    User->>Client: create_dataset(name)
    Client->>Datasets: create_dataset()
    Datasets->>Platform: POST /datasets
    Platform-->>Datasets: dataset_id
    Datasets-->>Client: Set dataset_id
    
    Note over User,Client: Dataset now set as context
    
    User->>Client: Perform selection strategy
    Client->>Platform: Run selection
    Platform-->>Client: new_tag_id
    
    User->>Client: get_tags_by_dataset_id()
    Client->>Tags: get_tags_by_dataset_id()
    Tags->>Platform: GET /datasets/{id}/tags
    Platform-->>Tags: List[TagData]
    Tags-->>Client: Tags with selections
    Client-->>User: Tag metadata
    
    User->>Client: export_tag_to_basic_filenames()
    Client->>Tags: export_tag()
    Tags->>Platform: GET /datasets/{id}/tags/{tag_id}/export
    Platform-->>Tags: Filename list
    Tags-->>User: Selected filenames
```

**Diagram: Typical Dataset and Tag Management Workflow**

Sources: [lightly/api/api_workflow_client.py:52-146](), [lightly/api/api_workflow_datasets.py]()

---

# Page: Datasources

# Datasources

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [lightly/api/__init__.py](lightly/api/__init__.py)
- [lightly/api/api_workflow_datasource_listing.py](lightly/api/api_workflow_datasource_listing.py)
- [lightly/api/api_workflow_datasources.py](lightly/api/api_workflow_datasources.py)
- [lightly/api/download.py](lightly/api/download.py)
- [tests/api/test_download.py](tests/api/test_download.py)
- [tests/api_workflow/test_api_workflow_datasource_listing.py](tests/api_workflow/test_api_workflow_datasource_listing.py)
- [tests/api_workflow/test_api_workflow_datasources.py](tests/api_workflow/test_api_workflow_datasources.py)

</details>



Datasources are cloud storage configurations that connect the Lightly Platform to your raw training data. They enable the platform to list, read, and optionally write files directly from cloud storage providers without uploading data to Lightly servers. This page covers datasource configuration, permission management, data listing, and incremental processing.

For information about the overall API Workflow Client architecture, see [API Workflow Client](#6.1). For information about dataset and tag management, see [Dataset and Tag Management](#6.3).

---

## Overview

A datasource represents a connection to a cloud storage bucket or local file server where your images, videos, predictions, and metadata are stored. Once configured, the Lightly Platform and Compute Workers can access this data directly through read URLs, enabling efficient processing of large datasets without data duplication.

**Datasource Architecture**

```mermaid
graph TB
    subgraph "User Code"
        Client["ApiWorkflowClient"]
    end
    
    subgraph "Mixins"
        DatasourcesMixin["_DatasourcesMixin<br/>Configuration methods"]
        ListingMixin["_DatasourceListingMixin<br/>Listing and download methods"]
    end
    
    subgraph "Generated API"
        DatasourcesApi["DatasourcesApi<br/>OpenAPI client"]
    end
    
    subgraph "Lightly Platform"
        Platform["Platform API<br/>Stores datasource config"]
    end
    
    subgraph "Cloud Storage"
        S3["AWS S3<br/>s3://bucket/path"]
        Azure["Azure Blob<br/>container/path"]
        GCS["Google Cloud Storage<br/>gs://bucket/path"]
        Local["Local File Server<br/>http://localhost:3456"]
        OBS["Telekom OBS<br/>obs://bucket/path"]
    end
    
    Client --> DatasourcesMixin
    Client --> ListingMixin
    DatasourcesMixin --> DatasourcesApi
    ListingMixin --> DatasourcesApi
    DatasourcesApi --> Platform
    
    Platform -.reads/writes.-> S3
    Platform -.reads/writes.-> Azure
    Platform -.reads/writes.-> GCS
    Platform -.reads/writes.-> Local
    Platform -.reads/writes.-> OBS
```

Sources: [lightly/api/api_workflow_datasources.py:9-338](), [lightly/api/api_workflow_datasource_listing.py:35-690]()

---

## Supported Datasource Types

Lightly supports six datasource types, each with specific configuration requirements:

| Datasource Type | Method | Primary Use Case |
|----------------|--------|------------------|
| **S3** | `set_s3_config()` | AWS S3 buckets with access keys |
| **S3 Delegated Access** | `set_s3_delegated_access_config()` | AWS S3 with IAM role-based access |
| **Azure** | `set_azure_config()` | Azure Blob Storage with SAS tokens |
| **GCS** | `set_gcs_config()` | Google Cloud Storage with service account credentials |
| **Local** | `set_local_config()` | Local file server for on-premise deployments |
| **OBS** | `set_obs_config()` | Telekom Open Telekom Cloud Object Storage |

Sources: [lightly/api/api_workflow_datasources.py:22-309]()

---

## Datasource Configuration

### Configuration Workflow

```mermaid
flowchart LR
    subgraph "User Actions"
        CreateDataset["Create Dataset<br/>ApiWorkflowClient"]
        ConfigDatasource["Configure Datasource<br/>set_*_config()"]
        VerifyPerms["Verify Permissions<br/>list_datasource_permissions()"]
    end
    
    subgraph "API Operations"
        UpdateDatasource["update_datasource_by_dataset_id<br/>DatasourcesApi"]
        VerifyDatasource["verify_datasource_by_dataset_id<br/>DatasourcesApi"]
    end
    
    subgraph "Platform"
        StoredConfig["DatasourceConfig<br/>Stored in platform"]
        PermissionCheck["Permission Validation<br/>can_read, can_write, can_list"]
    end
    
    CreateDataset --> ConfigDatasource
    ConfigDatasource --> UpdateDatasource
    UpdateDatasource --> StoredConfig
    
    VerifyPerms --> VerifyDatasource
    VerifyDatasource --> PermissionCheck
    PermissionCheck --> VerifyPerms
```

Sources: [lightly/api/api_workflow_datasources.py:22-309](), [lightly/api/api_workflow_datasources.py:311-337]()

### AWS S3 Configuration

The `set_s3_config()` method configures standard S3 access using access keys:

```python
client = ApiWorkflowClient(token="TOKEN", dataset_id="DATASET_ID")
client.set_s3_config(
    resource_path="s3://my-bucket/path/to/data",
    region="eu-central-1",
    access_key="AKIAIOSFODNN7EXAMPLE",
    secret_access_key="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
    thumbnail_suffix=".lightly/thumbnails/[filename]_thumb.[extension]",
    purpose=DatasourcePurpose.INPUT_OUTPUT
)
```

**Parameters:**
- `resource_path`: S3 URI (e.g., `s3://bucket/prefix`)
- `region`: AWS region (e.g., `eu-central-1`, `us-west-2`)
- `access_key`: AWS access key ID
- `secret_access_key`: AWS secret access key
- `thumbnail_suffix`: Path template for thumbnail storage (set to `None` to disable thumbnails)
- `purpose`: `INPUT` (read-only), `INPUT_OUTPUT` (read/write), or `LIGHTLY` (platform-managed)

Sources: [lightly/api/api_workflow_datasources.py:161-210](), [tests/api_workflow/test_api_workflow_datasources.py:93-109]()

### AWS S3 Delegated Access

The `set_s3_delegated_access_config()` method uses IAM role assumption instead of static credentials, providing enhanced security:

```python
client.set_s3_delegated_access_config(
    resource_path="s3://my-bucket/path/to/data",
    region="eu-central-1",
    role_arn="arn:aws:iam::000000000000:role/LightlyRole",
    external_id="my-external-id",
    thumbnail_suffix=".lightly/thumbnails/[filename]_thumb.[extension]",
    purpose=DatasourcePurpose.INPUT_OUTPUT
)
```

**Parameters:**
- `role_arn`: ARN of the IAM role to assume
- `external_id`: External ID for role assumption (security measure)

When using delegated access, `use_redirected_read_url` is automatically enabled, providing unlimited access duration for read URLs.

Sources: [lightly/api/api_workflow_datasources.py:212-261](), [tests/api_workflow/test_api_workflow_datasources.py:111-128]()

### Azure Blob Storage Configuration

The `set_azure_config()` method configures Azure Blob Storage access using SAS tokens:

```python
client.set_azure_config(
    container_name="my-container/path/to/data",
    account_name="mystorageaccount",
    sas_token="?sv=2021-06-08&ss=b&srt=sco&sp=rwdlacupiytfx...",
    thumbnail_suffix=".lightly/thumbnails/[filename]_thumb.[extension]",
    purpose=DatasourcePurpose.INPUT_OUTPUT
)
```

**Parameters:**
- `container_name`: Container name with optional path prefix
- `account_name`: Azure storage account name
- `sas_token`: Shared Access Signature token (includes leading `?`)

Sources: [lightly/api/api_workflow_datasources.py:22-67](), [tests/api_workflow/test_api_workflow_datasources.py:21-36]()

### Google Cloud Storage Configuration

The `set_gcs_config()` method configures GCS access using service account credentials:

```python
import json

with open("service-account-key.json") as f:
    credentials = json.dumps(json.load(f))

client.set_gcs_config(
    resource_path="gs://my-bucket/path/to/data",
    project_id="my-project-id",
    credentials=credentials,
    thumbnail_suffix=".lightly/thumbnails/[filename]_thumb.[extension]",
    purpose=DatasourcePurpose.INPUT_OUTPUT
)
```

**Parameters:**
- `resource_path`: GCS URI (e.g., `gs://bucket/prefix`)
- `project_id`: Google Cloud project ID
- `credentials`: Service account key JSON file contents as a string

Sources: [lightly/api/api_workflow_datasources.py:69-116](), [tests/api_workflow/test_api_workflow_datasources.py:38-53]()

### Local File Server Configuration

The `set_local_config()` method configures access to a local file server for on-premise deployments:

```python
client.set_local_config(
    relative_path="path/to/data",
    web_server_location="http://localhost:3456",
    thumbnail_suffix=".lightly/thumbnails/[filename]_thumb.[extension]",
    purpose=DatasourcePurpose.INPUT_OUTPUT
)
```

**Parameters:**
- `relative_path`: Relative path from the server mount root
- `web_server_location`: HTTP URL of the local file server (default: `http://localhost:3456`)

Sources: [lightly/api/api_workflow_datasources.py:118-159](), [tests/api_workflow/test_api_workflow_datasources.py:55-91]()

### Telekom OBS Configuration

The `set_obs_config()` method configures Telekom Open Telekom Cloud Object Storage:

```python
client.set_obs_config(
    resource_path="obs://my-bucket/path/to/data",
    obs_endpoint="obs.eu-de.otc.t-systems.com",
    obs_access_key_id="OBS_ACCESS_KEY",
    obs_secret_access_key="OBS_SECRET_KEY",
    thumbnail_suffix=".lightly/thumbnails/[filename]_thumb.[extension]",
    purpose=DatasourcePurpose.INPUT_OUTPUT
)
```

**Parameters:**
- `resource_path`: OBS URI (e.g., `obs://bucket/prefix`)
- `obs_endpoint`: OBS endpoint URL
- `obs_access_key_id`: OBS access key ID
- `obs_secret_access_key`: OBS secret access key

Sources: [lightly/api/api_workflow_datasources.py:263-309]()

### Common Configuration Options

**Thumbnail Suffix:**
All datasource types support the `thumbnail_suffix` parameter, which defines where thumbnails are stored. The template uses placeholders:
- `[filename]`: Original filename without extension
- `[extension]`: Original file extension

Example: `.lightly/thumbnails/[filename]_thumb.[extension]` transforms `image.jpg` to `.lightly/thumbnails/image_thumb.jpg`.

Set to `None` to disable thumbnails and use full-resolution images from the datasource.

**Datasource Purpose:**
The `purpose` parameter determines read/write permissions:
- `INPUT`: Read-only access (Lightly never writes to the datasource)
- `INPUT_OUTPUT`: Read and write access (Lightly can write thumbnails, predictions, metadata)
- `LIGHTLY`: Platform-managed datasource (deprecated)

Sources: [lightly/api/api_workflow_datasources.py:27-29](), [lightly/api/api_workflow_datasources.py:44-51]()

---

## Permission Management

### Verifying Datasource Permissions

The `list_datasource_permissions()` method verifies that the configured datasource has the required permissions:

```python
permissions = client.list_datasource_permissions()
# Returns:
# {
#     'can_read': True,
#     'can_write': True,
#     'can_list': False,
#     'can_overwrite': True,
#     'errors': {'can_list': 'Access denied: ListBucket'}
# }
```

**Permission Types:**
- `can_read`: Can read individual files
- `can_write`: Can write new files
- `can_list`: Can list bucket contents
- `can_overwrite`: Can overwrite existing files
- `errors`: Dictionary of error messages for failed permissions

If any permission check fails, the `errors` dictionary contains the permission name as key and error message as value.

Sources: [lightly/api/api_workflow_datasources.py:311-337](), [tests/api_workflow/test_api_workflow_datasources.py:130-172]()

**Permission Verification Flow**

```mermaid
flowchart TB
    Start["list_datasource_permissions()"] --> Verify["verify_datasource_by_dataset_id<br/>DatasourcesApi"]
    
    Verify --> TestRead["Test Read Permission<br/>Attempt to read file"]
    Verify --> TestWrite["Test Write Permission<br/>Attempt to write file"]
    Verify --> TestList["Test List Permission<br/>Attempt to list bucket"]
    Verify --> TestOverwrite["Test Overwrite Permission<br/>Attempt to overwrite file"]
    
    TestRead --> CollectResults["Collect Results<br/>DatasourceConfigVerifyData"]
    TestWrite --> CollectResults
    TestList --> CollectResults
    TestOverwrite --> CollectResults
    
    CollectResults --> ReturnDict["Return permission dict<br/>with errors if any"]
```

Sources: [lightly/api/api_workflow_datasources.py:311-337]()

---

## Listing Data from Datasources

The `_DatasourceListingMixin` provides methods for listing files stored in configured datasources. These methods retrieve filenames and read URLs without downloading the actual files.

### Listing Raw Samples

**Method Signature:**
```python
download_raw_samples(
    from_: int = 0,
    to: Optional[int] = None,
    relevant_filenames_file_name: Optional[str] = None,
    divide_and_conquer_shards: int = 1,
    use_redirected_read_url: bool = False,
    progress_bar: Optional[tqdm.tqdm] = None,
) -> List[Tuple[str, str]]
```

**Usage:**
```python
samples = client.download_raw_samples(
    from_=1684750000,  # Unix timestamp
    to=1684760000,
    divide_and_conquer_shards=4  # Parallel listing with 4 shards
)
# Returns: [('image-1.png', 'https://...'), ('image-2.png', 'https://...')]
```

**Parameters:**
- `from_`: Unix timestamp for start of time range (inclusive)
- `to`: Unix timestamp for end of time range (inclusive, defaults to current time)
- `relevant_filenames_file_name`: Path to a text file in the bucket containing filenames to list (optional filter)
- `divide_and_conquer_shards`: Number of parallel shards for listing (improves performance for large buckets)
- `use_redirected_read_url`: Return unlimited-duration URLs instead of time-limited URLs
- `progress_bar`: Optional tqdm progress bar instance

Sources: [lightly/api/api_workflow_datasource_listing.py:36-94](), [tests/api_workflow/test_api_workflow_datasource_listing.py:21-67]()

### Listing Predictions

**Method Signature:**
```python
download_raw_predictions_iter(
    task_name: str,
    from_: int = 0,
    to: Optional[int] = None,
    relevant_filenames_file_name: Optional[str] = None,
    run_id: Optional[str] = None,
    relevant_filenames_artifact_id: Optional[str] = None,
    divide_and_conquer_shards: int = 1,
    use_redirected_read_url: bool = False,
    progress_bar: Optional[tqdm.tqdm] = None,
) -> Iterator[Tuple[str, str]]
```

**Usage:**
```python
predictions = list(client.download_raw_predictions_iter(
    task_name="object-detection",
    from_=1684750000
))
# Returns: [('.lightly/predictions/object-detection/image-1.json', 'https://...'), ...]
```

**Additional Parameters:**
- `task_name`: Name of the prediction task (predictions are stored in `.lightly/predictions/{task_name}/`)
- `run_id`: Optional run ID to filter predictions from a specific run
- `relevant_filenames_artifact_id`: Optional artifact ID containing relevant filenames (must be used with `run_id`)

The iterator version (`download_raw_predictions_iter()`) is memory-efficient for large datasets. The non-iterator version (`download_raw_predictions()`) returns a full list.

Sources: [lightly/api/api_workflow_datasource_listing.py:96-203](), [tests/api_workflow/test_api_workflow_datasource_listing.py:105-253]()

### Listing Metadata

**Method Signature:**
```python
download_raw_metadata_iter(
    from_: int = 0,
    to: Optional[int] = None,
    run_id: Optional[str] = None,
    relevant_filenames_artifact_id: Optional[str] = None,
    relevant_filenames_file_name: Optional[str] = None,
    divide_and_conquer_shards: int = 1,
    use_redirected_read_url: bool = False,
    progress_bar: Optional[tqdm.tqdm] = None,
) -> Iterator[Tuple[str, str]]
```

**Usage:**
```python
metadata = list(client.download_raw_metadata_iter())
# Returns: [('.lightly/metadata/image-1.json', 'https://...'), ...]
```

Metadata files are stored in `.lightly/metadata/` in the datasource.

Sources: [lightly/api/api_workflow_datasource_listing.py:235-305](), [tests/api_workflow/test_api_workflow_datasource_listing.py:304-428]()

### Divide and Conquer Listing

Large buckets can take significant time to list. The divide-and-conquer strategy parallelizes listing by splitting the bucket into multiple shards:

```mermaid
flowchart TB
    Start["download_raw_samples()"] --> GetCursors["_get_divide_and_conquer_list_cursors()<br/>Request N cursors from API"]
    
    GetCursors --> DNCFunction["get_divide_and_conquer_list_of_raw_samples_from_datasource_by_dataset_id<br/>Returns cursor list"]
    
    DNCFunction --> Cursors["Cursors<br/>['cursor1', 'cursor2', 'cursor3', 'cursor4']"]
    
    Cursors --> Parallel["ThreadPoolExecutor<br/>max_workers=len(cursors)"]
    
    Parallel --> Shard1["Thread 1<br/>_download_raw_files_cursor_iter<br/>cursor='cursor1'"]
    Parallel --> Shard2["Thread 2<br/>_download_raw_files_cursor_iter<br/>cursor='cursor2'"]
    Parallel --> Shard3["Thread 3<br/>_download_raw_files_cursor_iter<br/>cursor='cursor3'"]
    Parallel --> Shard4["Thread 4<br/>_download_raw_files_cursor_iter<br/>cursor='cursor4'"]
    
    Shard1 --> Merge["Merge Results<br/>yield from future.result()"]
    Shard2 --> Merge
    Shard3 --> Merge
    Shard4 --> Merge
    
    Merge --> Results["List[Tuple[str, str]]<br/>All filenames and URLs"]
```

Sources: [lightly/api/api_workflow_datasource_listing.py:486-606]()

**Implementation Details:**

1. **Cursor Request:** The API call `get_divide_and_conquer_list_of_raw_samples_from_datasource_by_dataset_id()` with `dnc_shards=N` returns N cursors, each representing a partition of the bucket.

2. **Parallel Download:** Each cursor is processed in a separate thread using `ThreadPoolExecutor`.

3. **Continuous Pagination:** Within each thread, the cursor-based API (`get_list_of_raw_samples_from_datasource_by_dataset_id()`) is called repeatedly with the current cursor until `has_more=False`.

4. **Result Merging:** Results from all threads are merged using `yield from future.result()`.

Sources: [lightly/api/api_workflow_datasource_listing.py:545-653](), [tests/api_workflow/test_api_workflow_datasource_listing.py:564-635]()

---

## Incremental Processing

### Tracking Processed Samples

The platform maintains a "processed until timestamp" for each dataset, enabling incremental processing workflows where only new samples are retrieved.

**Getting Processed Timestamp:**
```python
last_processed = client.get_processed_until_timestamp()
# Returns: 1684750513 (Unix timestamp)
```

**Updating Processed Timestamp:**
```python
import time
client.update_processed_until_timestamp(timestamp=int(time.time()))
```

Sources: [lightly/api/api_workflow_datasource_listing.py:358-409](), [tests/api_workflow/test_api_workflow_datasource_listing.py:469-514]()

### Downloading New Samples

The `download_new_raw_samples()` method automatically retrieves only samples added since the last processed timestamp:

```python
new_samples = client.download_new_raw_samples(
    divide_and_conquer_shards=4,
    use_redirected_read_url=False
)
# Returns: [('image-3.png', 'https://...'), ('image-4.png', 'https://...')]
```

**Implementation:**
1. Retrieves `processed_until_timestamp` from the platform
2. Lists samples from `processed_until_timestamp + 1` to current time
3. Updates `processed_until_timestamp` to current time
4. Returns the new samples

This enables continuous monitoring workflows where the method is called periodically to process new data as it arrives.

Sources: [lightly/api/api_workflow_datasource_listing.py:307-356](), [tests/api_workflow/test_api_workflow_datasource_listing.py:430-466]()

**Incremental Processing Workflow**

```mermaid
sequenceDiagram
    participant User
    participant Client as ApiWorkflowClient
    participant API as DatasourcesApi
    participant Storage as Cloud Storage
    
    User->>Client: download_new_raw_samples()
    Client->>API: get_datasource_processed_until_timestamp_by_dataset_id()
    API-->>Client: processed_until_timestamp = 1684750513
    
    Note over Client: Calculate time range<br/>from_ = 1684750513 + 1<br/>to = current time
    
    Client->>API: get_divide_and_conquer_list_of_raw_samples_from_datasource_by_dataset_id()
    API-->>Client: cursors = ['cursor1', 'cursor2', ...]
    
    par Parallel Listing
        Client->>API: get_list_of_raw_samples_from_datasource_by_dataset_id(cursor='cursor1')
        API->>Storage: List files
        Storage-->>API: Files batch 1
        API-->>Client: {data: [...], cursor: 'cursor1_next', has_more: true}
    and
        Client->>API: get_list_of_raw_samples_from_datasource_by_dataset_id(cursor='cursor2')
        API->>Storage: List files
        Storage-->>API: Files batch 2
        API-->>Client: {data: [...], cursor: 'cursor2_next', has_more: true}
    end
    
    Note over Client: Merge results
    
    Client->>API: update_datasource_processed_until_timestamp_by_dataset_id(timestamp=current_time)
    API-->>Client: Success
    
    Client-->>User: List[(filename, url)]
```

Sources: [lightly/api/api_workflow_datasource_listing.py:307-356]()

---

## Downloading Files

### File Download Utilities

The `lightly.api.download` module provides utility functions for downloading files from URLs:

**Single File Download:**
```python
from lightly.api.download import download_and_write_file

download_and_write_file(
    url="https://example.com/image.jpg",
    output_path="/path/to/local/image.jpg",
    session=None,  # Optional requests.Session
    retry_fn=retry_utils.retry,  # Retry function
    request_kwargs={"timeout": 10}  # Additional requests.get() parameters
)
```

**Batch Download:**
```python
from lightly.api.download import download_and_write_all_files

file_infos = [
    ("image-1.jpg", "https://example.com/image-1.jpg"),
    ("image-2.jpg", "https://example.com/image-2.jpg"),
]

download_and_write_all_files(
    file_infos=file_infos,
    output_dir="/path/to/output",
    max_workers=None,  # None = use CPU count
    verbose=True,  # Show progress bar
)
```

**Implementation Details:**
- Downloads are parallelized using `ThreadPoolExecutor`
- Each thread maintains its own `requests.Session` for connection pooling
- Failed downloads are logged as warnings but don't stop the batch
- Supports retry logic through configurable `retry_fn`
- Creates output directories automatically

Sources: [lightly/api/download.py:18-132](), [tests/api/test_download.py:9-123]()

### Getting Read URLs

For specific files, you can retrieve read URLs without listing the entire datasource:

**Prediction File URL:**
```python
url = client.get_prediction_read_url(filename="object-detection/image-1.json")
# Returns: "https://..."
```

**Metadata File URL:**
```python
url = client.get_metadata_read_url(filename="image-1.json")
# Returns: "https://..."
```

**Custom Embedding File URL:**
```python
url = client.get_custom_embedding_read_url(filename="embeddings.csv")
# Returns: "https://..."
```

These methods return read URLs for files in the `.lightly/predictions/`, `.lightly/metadata/`, and `.lightly/embeddings/` directories respectively. Note that a URL is returned even if the file doesn't exist.

Sources: [lightly/api/api_workflow_datasource_listing.py:423-484](), [tests/api_workflow/test_api_workflow_datasource_listing.py:516-541]()

---

## Implementation Details

### Class Structure

```mermaid
classDiagram
    class ApiWorkflowClient {
        +dataset_id: str
        +_datasources_api: DatasourcesApi
    }
    
    class _DatasourcesMixin {
        +get_datasource() DatasourceConfig
        +set_s3_config(...)
        +set_s3_delegated_access_config(...)
        +set_azure_config(...)
        +set_gcs_config(...)
        +set_local_config(...)
        +set_obs_config(...)
        +list_datasource_permissions() Dict
    }
    
    class _DatasourceListingMixin {
        +download_raw_samples(...) List~Tuple~
        +download_raw_predictions(...) List~Tuple~
        +download_raw_predictions_iter(...) Iterator~Tuple~
        +download_raw_metadata(...) List~Tuple~
        +download_raw_metadata_iter(...) Iterator~Tuple~
        +download_new_raw_samples(...) List~Tuple~
        +get_processed_until_timestamp() int
        +update_processed_until_timestamp(timestamp)
        +get_prediction_read_url(filename) str
        +get_metadata_read_url(filename) str
        +get_custom_embedding_read_url(filename) str
        -_get_divide_and_conquer_list_cursors(...) List~str~
        -_download_raw_files(...) List~Tuple~
        -_download_raw_files_divide_and_conquer_iter(...) Iterator~Tuple~
        -_download_raw_files_cursor_iter(...) Iterator~Tuple~
    }
    
    class DatasourcesApi {
        +get_datasource_by_dataset_id(dataset_id)
        +update_datasource_by_dataset_id(dataset_id, datasource_config)
        +verify_datasource_by_dataset_id(dataset_id)
        +get_list_of_raw_samples_from_datasource_by_dataset_id(...)
        +get_divide_and_conquer_list_of_raw_samples_from_datasource_by_dataset_id(...)
        +get_list_of_raw_samples_predictions_from_datasource_by_dataset_id(...)
        +get_list_of_raw_samples_metadata_from_datasource_by_dataset_id(...)
        +get_datasource_processed_until_timestamp_by_dataset_id(dataset_id)
        +update_datasource_processed_until_timestamp_by_dataset_id(...)
    }
    
    ApiWorkflowClient --|> _DatasourcesMixin
    ApiWorkflowClient --|> _DatasourceListingMixin
    _DatasourcesMixin ..> DatasourcesApi : uses
    _DatasourceListingMixin ..> DatasourcesApi : uses
```

Sources: [lightly/api/api_workflow_datasources.py:9-338](), [lightly/api/api_workflow_datasource_listing.py:35-690]()

### Data Models

**DatasourceConfig:**
Represents datasource configuration stored in the platform. Contains type-specific fields:
- `type`: "S3", "S3DelegatedAccess", "AZURE", "GCS", "LOCAL", "OBS"
- `fullPath`: Resource path (e.g., `s3://bucket/path`)
- `thumbSuffix`: Thumbnail path template
- `purpose`: "INPUT", "INPUT_OUTPUT", or "LIGHTLY"
- Type-specific authentication fields

**DatasourceRawSamplesData:**
Response from listing operations:
- `data`: List of `DatasourceRawSamplesDataRow` objects
- `cursor`: Cursor for pagination (empty string if no more data)
- `hasMore`: Boolean indicating more data available

**DatasourceRawSamplesDataRow:**
Individual file entry:
- `fileName`: Relative path within datasource
- `readUrl`: Time-limited or unlimited URL for reading the file

**DivideAndConquerCursorData:**
Response from divide-and-conquer cursor request:
- `cursors`: List of cursor strings for parallel processing

Sources: [lightly/openapi_generated/swagger_client/models](), [lightly/api/api_workflow_datasource_listing.py:13-19]()

### Retry Logic

All datasource API calls are wrapped with retry logic to handle transient errors:

```python
from lightly.api.retry_utils import retry

response = retry(
    fn=self._datasources_api.get_list_of_raw_samples_from_datasource_by_dataset_id,
    dataset_id=self.dataset_id,
    cursor=cursor,
    use_redirected_read_url=use_redirected_read_url
)
```

The `retry()` function automatically retries on HTTP 5xx errors and certain network errors, with exponential backoff.

Sources: [lightly/api/api_workflow_datasource_listing.py:374-377](), [lightly/api/api_workflow_datasource_listing.py:640-648]()

### Validation and Filtering

The `_sample_unseen_and_valid()` function validates samples during listing:

**Validations:**
1. Rejects absolute file paths starting with `/`
2. Rejects relative paths with dot notation (`./`, `../`)
3. Rejects duplicate filenames within the same listing operation

All validation failures emit `UserWarning` messages but don't stop processing.

Sources: [lightly/api/api_workflow_datasource_listing.py:655-689](), [tests/api_workflow/test_api_workflow_datasource_listing.py:776-802]()

---

## Common Workflows

### Initial Datasource Setup

```python
from lightly.api import ApiWorkflowClient
from lightly.openapi_generated.swagger_client.models import DatasourcePurpose

# Initialize client
client = ApiWorkflowClient(token="TOKEN", dataset_id="DATASET_ID")

# Configure S3 datasource
client.set_s3_config(
    resource_path="s3://my-bucket/training-data",
    region="eu-central-1",
    access_key="ACCESS_KEY",
    secret_access_key="SECRET_KEY",
    purpose=DatasourcePurpose.INPUT_OUTPUT
)

# Verify permissions
permissions = client.list_datasource_permissions()
if not permissions["can_read"]:
    print(f"Read permission failed: {permissions.get('errors', {}).get('can_read')}")
```

### Listing and Downloading Data

```python
# List all samples
samples = client.download_raw_samples(
    divide_and_conquer_shards=8  # Parallel listing for performance
)

# Download files
from lightly.api.download import download_and_write_all_files

download_and_write_all_files(
    file_infos=samples,
    output_dir="/path/to/output",
    max_workers=16,
    verbose=True
)
```

### Incremental Processing Loop

```python
import time

while True:
    # Get new samples since last run
    new_samples = client.download_new_raw_samples(
        divide_and_conquer_shards=4
    )
    
    if new_samples:
        print(f"Found {len(new_samples)} new samples")
        # Process new samples...
        
    # Wait before checking again
    time.sleep(3600)  # Check every hour
```

Sources: [lightly/api/api_workflow_datasources.py](), [lightly/api/api_workflow_datasource_listing.py]()

---

# Page: Version Checking and Compatibility

# Version Checking and Compatibility

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/source/lightly.models.rst](docs/source/lightly.models.rst)
- [lightly/__init__.py](lightly/__init__.py)
- [lightly/api/_version_checking.py](lightly/api/_version_checking.py)
- [tests/api/test_version_checking.py](tests/api/test_version_checking.py)
- [tests/api_workflow/test_api_workflow_client.py](tests/api_workflow/test_api_workflow_client.py)
- [tests/conftest.py](tests/conftest.py)

</details>



## Purpose and Scope

This document describes the automatic version checking and compatibility verification mechanisms built into the Lightly framework. When the `lightly` package is imported, it automatically verifies that the installed version is up-to-date and compatible with the Lightly Platform API. This helps ensure smooth integration between local code and cloud services.

For information about the broader platform integration architecture, see [Platform Integration](#6).

## Automatic Version Check on Import

The Lightly package performs an automatic background version check when imported. This check runs only once per Python process and executes in a separate thread to avoid blocking the main application.

### Version Check Initialization Flow

```mermaid
flowchart TB
    IMPORT["Import lightly package"]
    CHECK_ENV{"Check<br/>LIGHTLY_DID_VERSION_CHECK<br/>environment variable"}
    SET_ENV["Set LIGHTLY_DID_VERSION_CHECK=True"]
    CHECK_PROC{"Is current process<br/>MainProcess?"}
    START_THREAD["Start background thread<br/>check_is_latest_version_in_background()"]
    SKIP["Skip version check"]
    CONTINUE["Continue with import"]
    
    IMPORT --> CHECK_ENV
    CHECK_ENV -->|"False"| SET_ENV
    CHECK_ENV -->|"True"| SKIP
    SET_ENV --> CHECK_PROC
    CHECK_PROC -->|"Yes"| START_THREAD
    CHECK_PROC -->|"No"| SKIP
    START_THREAD --> CONTINUE
    SKIP --> CONTINUE
```

**Initialization Sequence**

The version check initialization occurs in the package's `__init__.py` module:

| Step | Component | Action |
|------|-----------|--------|
| 1 | Environment Check | Check `LIGHTLY_DID_VERSION_CHECK` variable |
| 2 | Flag Setting | Set environment variable to `"True"` |
| 3 | Process Check | Verify running in main process via `multiprocessing.current_process().name` |
| 4 | Thread Spawn | Call `check_is_latest_version_in_background()` with current version |

**Sources:** [lightly/__init__.py:83-92]()

## Version Checking Functions

The `lightly.api._version_checking` module provides programmatic access to version verification functions.

```mermaid
flowchart TB
    subgraph "Public API Functions"
        IS_LATEST["is_latest_version(current_version)<br/>→ bool"]
        IS_COMPAT["is_compatible_version(current_version)<br/>→ bool"]
        GET_LATEST["get_latest_version(current_version, timeout_sec)<br/>→ str"]
        GET_MIN["get_minimum_compatible_version(timeout_sec)<br/>→ str"]
        CHECK_BG["check_is_latest_version_in_background(current_version)<br/>→ None"]
    end
    
    subgraph "Internal Components"
        VERS_API["_get_versioning_api()<br/>→ VersioningApi"]
        VER_COMPARE["version_compare.version_compare()<br/>semantic version comparison"]
    end
    
    subgraph "Platform API Endpoints"
        EP_LATEST["VersioningApi.get_latest_pip_version()"]
        EP_MIN["VersioningApi.get_minimum_compatible_pip_version()"]
    end
    
    IS_LATEST --> GET_LATEST
    IS_LATEST --> VER_COMPARE
    IS_COMPAT --> GET_MIN
    IS_COMPAT --> VER_COMPARE
    
    GET_LATEST --> VERS_API
    GET_MIN --> VERS_API
    CHECK_BG --> IS_LATEST
    
    VERS_API --> EP_LATEST
    VERS_API --> EP_MIN
```

### Core Version Checking Functions

The module provides the following functions for version verification:

**`is_latest_version(current_version: str) -> bool`**

Compares the current version against the latest released version available on PyPI. Returns `True` if the current version is greater than or equal to the latest version.

**`is_compatible_version(current_version: str) -> bool`**

Verifies that the current version meets the minimum compatibility requirements for the Lightly Platform API. Returns `True` if the current version is greater than or equal to the minimum compatible version.

**`get_latest_version(current_version: str, timeout_sec: float = 2) -> str`**

Retrieves the latest version number from the Lightly Platform API. The `current_version` parameter is sent to the API for tracking purposes. The default timeout is 2 seconds.

**`get_minimum_compatible_version(timeout_sec: float = 2) -> str`**

Retrieves the minimum compatible version number from the Lightly Platform API. This represents the oldest version that can successfully interact with the current API.

**`check_is_latest_version_in_background(current_version: str) -> None`**

Spawns a daemon thread to check if the current version is the latest. Silently catches and ignores any exceptions to avoid disrupting the application. This is the function called during package import.

**Sources:** [lightly/api/_version_checking.py:12-63]()

## API Version Endpoints

The version checking system communicates with two Lightly Platform API endpoints through the generated `VersioningApi` client.

```mermaid
flowchart LR
    subgraph "Local Environment"
        FUNC["Version checking functions"]
        API_CLIENT["LightlySwaggerApiClient<br/>(retries=0)"]
        VERS_API["VersioningApi instance"]
    end
    
    subgraph "Platform API"
        EP1["GET /versioning/pip/latest<br/>?current_version={version}"]
        EP2["GET /versioning/pip/minimum-compatible"]
    end
    
    FUNC --> VERS_API
    VERS_API --> API_CLIENT
    API_CLIENT --> EP1
    API_CLIENT --> EP2
```

### API Client Configuration

The `_get_versioning_api()` function creates a specialized API client for version checking:

| Configuration | Value | Purpose |
|--------------|-------|---------|
| Authentication | No token required | Version check works without authentication |
| Retries | 0 | Fail fast on timeout rather than retrying |
| Timeout | 2 seconds (default) | Quick response to avoid blocking |
| Server Location | From `LIGHTLY_SERVER_LOCATION` env var | Configurable endpoint |

**Sources:** [lightly/api/_version_checking.py:65-73]()

## Version Information in API Requests

When an `ApiWorkflowClient` instance is created, the client automatically includes version and platform information in its User-Agent header.

### User-Agent Header Format

```
Lightly/{version} ({system}/{release}; {platform}; {processor};) python/{python_version}
```

**Header Components:**

| Component | Source | Example |
|-----------|--------|---------|
| `version` | `lightly.__version__` | `1.5.22` |
| `system` | `platform.system()` | `Linux`, `Darwin`, `Windows` |
| `release` | `platform.release()` | `5.15.0-58-generic` |
| `platform` | `platform.platform()` | `Linux-5.15.0-58-generic-x86_64-with-glibc2.35` |
| `processor` | `platform.processor()` | `x86_64` |
| `python_version` | `platform.python_version()` | `3.10.6` |

This information helps the Lightly Platform track client versions and diagnose compatibility issues.

**Sources:** [tests/api_workflow/test_api_workflow_client.py:86-102]()

## Disabling Version Checks

The version check can be disabled by setting the `LIGHTLY_DID_VERSION_CHECK` environment variable before importing the `lightly` package.

### Disabling in Application Code

```python
import os
os.environ["LIGHTLY_DID_VERSION_CHECK"] = "True"

import lightly  # Version check will be skipped
```

### Disabling in Tests

The test suite automatically disables version checking in the pytest configuration hook:

**Sources:** [tests/conftest.py:23-28]()

### Use Cases for Disabling

| Scenario | Reason |
|----------|--------|
| Unit Testing | Avoid network calls and speed up test execution |
| CI/CD Pipelines | Prevent timeouts in isolated build environments |
| Offline Usage | Work without internet connectivity |
| Debugging | Eliminate version check as potential source of issues |

## Compatibility Requirements

The Lightly framework uses semantic versioning to determine compatibility between the local package and the Lightly Platform API.

### Version Comparison Logic

```mermaid
flowchart TB
    CURRENT["Current Version<br/>e.g., 1.5.22"]
    
    subgraph "Latest Version Check"
        GET_L["get_latest_version()"]
        COMPARE_L["version_compare()"]
        LATEST_OK{"current >= latest?"}
        UP_TO_DATE["✓ Up to date"]
        OUTDATED["⚠ Update available"]
    end
    
    subgraph "Compatibility Check"
        GET_M["get_minimum_compatible_version()"]
        COMPARE_M["version_compare()"]
        COMPAT_OK{"current >= minimum?"}
        COMPATIBLE["✓ Compatible"]
        INCOMPATIBLE["✗ Incompatible"]
    end
    
    CURRENT --> GET_L
    CURRENT --> GET_M
    
    GET_L --> COMPARE_L
    COMPARE_L --> LATEST_OK
    LATEST_OK -->|"Yes"| UP_TO_DATE
    LATEST_OK -->|"No"| OUTDATED
    
    GET_M --> COMPARE_M
    COMPARE_M --> COMPAT_OK
    COMPAT_OK -->|"Yes"| COMPATIBLE
    COMPAT_OK -->|"No"| INCOMPATIBLE
```

### Version Comparison Rules

The `version_compare()` utility function performs semantic version comparison following these rules:

- Returns positive value if `current_version > compared_version`
- Returns zero if `current_version == compared_version`
- Returns negative value if `current_version < compared_version`

**Compatibility Guarantees:**

| Current Version | Minimum Compatible | Latest | Status |
|----------------|-------------------|--------|--------|
| 1.5.22 | 1.5.0 | 1.5.22 | ✓ Up-to-date and compatible |
| 1.5.22 | 1.5.0 | 1.5.25 | ⚠ Compatible but update available |
| 1.4.8 | 1.5.0 | 1.5.25 | ✗ Incompatible - must upgrade |

**Sources:** [lightly/api/_version_checking.py:12-21](), [tests/api/test_version_checking.py:20-40]()

## Error Handling and Timeouts

The version checking system is designed to fail gracefully without disrupting application functionality.

### Timeout Behavior

```mermaid
flowchart TB
    START["Version check initiated"]
    API_CALL["API request with timeout<br/>(default: 2 seconds)"]
    SUCCESS{"Request<br/>successful?"}
    RETURN["Return version string"]
    TIMEOUT{"Timeout or<br/>connection error?"}
    CATCH["Exception caught<br/>in background thread"]
    SILENT["Silently ignored"]
    CONTINUE["Application continues normally"]
    
    START --> API_CALL
    API_CALL --> SUCCESS
    SUCCESS -->|"Yes"| RETURN
    SUCCESS -->|"No"| TIMEOUT
    TIMEOUT -->|"Yes"| CATCH
    CATCH --> SILENT
    RETURN --> CONTINUE
    SILENT --> CONTINUE
```

### Exception Handling

| Exception Type | Context | Handling |
|---------------|---------|----------|
| Connection errors | Network unavailable | Silently ignored in background check |
| Timeout errors | API unresponsive | Request aborted after timeout period |
| Invalid URL | Incorrect `LIGHTLY_SERVER_LOCATION` | Raises `MaxRetryError` |
| Any exception | Background thread | Caught and ignored to prevent crashes |

The background version check wraps all operations in a try-except block that catches and ignores any exceptions, ensuring that version checking failures never prevent the application from running.

**Sources:** [lightly/api/_version_checking.py:47-62](), [tests/api/test_version_checking.py:49-76]()

## Testing Considerations

The version checking system includes special provisions for testing environments.

### Test Mocking Strategy

The test suite uses a module-scoped fixture to mock version checking API calls:

**Mock Behavior:**

| Mocked Method | Return Value | Purpose |
|--------------|--------------|---------|
| `get_latest_pip_version()` | Current version parameter | Simulates up-to-date installation |
| `get_minimum_compatible_pip_version()` | `"1.0.0"` | Ensures all versions appear compatible |

This approach avoids actual network calls during testing while maintaining test coverage of version-dependent logic.

**Sources:** [tests/conftest.py:44-72]()

### Environment Variable Configuration

Tests can override the API server location using the `LIGHTLY_SERVER_LOCATION` environment variable:

```python
os.environ["LIGHTLY_SERVER_LOCATION"] = "https://dummy-url"
```

This allows testing of timeout behavior and error handling without requiring actual API connectivity.

**Sources:** [tests/conftest.py:31](), [tests/api/test_version_checking.py:50, 70]()

---

# Page: Benchmarking

# Benchmarking

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [benchmarks/imagenet/resnet50/finetune_eval.py](benchmarks/imagenet/resnet50/finetune_eval.py)
- [benchmarks/imagenet/resnet50/knn_eval.py](benchmarks/imagenet/resnet50/knn_eval.py)
- [benchmarks/imagenet/resnet50/linear_eval.py](benchmarks/imagenet/resnet50/linear_eval.py)
- [benchmarks/imagenet/resnet50/main.py](benchmarks/imagenet/resnet50/main.py)
- [benchmarks/imagenet/vitb16/dino.py](benchmarks/imagenet/vitb16/dino.py)
- [benchmarks/imagenet/vitb16/finetune_eval.py](benchmarks/imagenet/vitb16/finetune_eval.py)
- [benchmarks/imagenet/vitb16/knn_eval.py](benchmarks/imagenet/vitb16/knn_eval.py)
- [benchmarks/imagenet/vitb16/linear_eval.py](benchmarks/imagenet/vitb16/linear_eval.py)
- [benchmarks/imagenet/vitb16/main.py](benchmarks/imagenet/vitb16/main.py)
- [docs/source/getting_started/benchmarks.rst](docs/source/getting_started/benchmarks.rst)
- [docs/source/getting_started/benchmarks/cifar10_benchmark.py](docs/source/getting_started/benchmarks/cifar10_benchmark.py)
- [docs/source/getting_started/benchmarks/imagenet100_benchmark.py](docs/source/getting_started/benchmarks/imagenet100_benchmark.py)
- [docs/source/getting_started/benchmarks/imagenette_benchmark.py](docs/source/getting_started/benchmarks/imagenette_benchmark.py)
- [lightly/utils/benchmarking/knn_classifier.py](lightly/utils/benchmarking/knn_classifier.py)
- [tests/utils/benchmarking/test_knn_classifier.py](tests/utils/benchmarking/test_knn_classifier.py)

</details>



The Lightly framework provides a comprehensive benchmarking infrastructure for evaluating self-supervised learning (SSL) methods on standard datasets. This page documents the benchmark scripts, evaluation protocols, and supporting utilities used to measure model performance and compare SSL methods.

For information about specific SSL model implementations, see [Self-Supervised Learning Models](#2). For details on training models using the CLI or Python API, see [Command-Line Interface](#4) and [Python API](#5).

## Purpose and Scope

The benchmarking system enables:
- Standardized evaluation of SSL methods on ImageNet1k, ImageNet100, Imagenette, and CIFAR-10
- Three evaluation protocols: kNN classification, linear evaluation, and fine-tuning
- Reproducible results with documented hyperparameters and training settings
- Support for both ResNet and Vision Transformer backbones
- Distributed training and multi-GPU evaluation

## Benchmark Architecture

The benchmarking infrastructure follows a modular design with separate components for pre-training, evaluation, and metrics tracking.

```mermaid
graph TB
    subgraph "Benchmark Entry Points"
        MAIN_R50["main.py<br/>(ResNet50)"]
        MAIN_VIT["main.py<br/>(ViT-B/16)"]
        CIFAR["cifar10_benchmark.py"]
        NETTE["imagenette_benchmark.py"]
        N100["imagenet100_benchmark.py"]
    end
    
    subgraph "Training Phase"
        METHODS["Method Implementations<br/>barlowtwins.py, byol.py, etc."]
        PRETRAIN["pretrain()<br/>SSL model training"]
        DATASETS["LightlyDataset"]
        TRANSFORMS["Method-specific transforms<br/>SimCLRTransform, DINOTransform"]
    end
    
    subgraph "Evaluation Phase"
        KNN["knn_eval.py<br/>KNN Evaluation"]
        LINEAR["linear_eval.py<br/>Linear Evaluation"]
        FINETUNE["finetune_eval.py<br/>Fine-tune Evaluation"]
    end
    
    subgraph "Evaluation Utilities"
        KNN_CLASS["KNNClassifier"]
        LINEAR_CLASS["LinearClassifier"]
        FINETUNE_CLASS["FinetuneClassifier"]
        METRIC_CB["MetricCallback"]
        ONLINE_CLS["OnlineLinearClassifier"]
    end
    
    subgraph "Outputs"
        CKPT["Model Checkpoints<br/>.ckpt files"]
        TENSORBOARD["TensorBoard Logs<br/>Training & eval metrics"]
        METRICS["Evaluation Metrics<br/>Top1, Top5 accuracy"]
    end
    
    MAIN_R50 --> PRETRAIN
    MAIN_VIT --> PRETRAIN
    CIFAR --> PRETRAIN
    NETTE --> PRETRAIN
    N100 --> PRETRAIN
    
    PRETRAIN --> METHODS
    PRETRAIN --> DATASETS
    PRETRAIN --> TRANSFORMS
    METHODS --> CKPT
    PRETRAIN --> ONLINE_CLS
    
    CKPT --> KNN
    CKPT --> LINEAR
    CKPT --> FINETUNE
    
    KNN --> KNN_CLASS
    LINEAR --> LINEAR_CLASS
    FINETUNE --> FINETUNE_CLASS
    
    KNN_CLASS --> METRIC_CB
    LINEAR_CLASS --> METRIC_CB
    FINETUNE_CLASS --> METRIC_CB
    
    METRIC_CB --> METRICS
    METRIC_CB --> TENSORBOARD
    ONLINE_CLS --> TENSORBOARD
    
    style PRETRAIN fill:#e1f5ff
    style KNN fill:#ffe1e1
    style LINEAR fill:#ffe1e1
    style FINETUNE fill:#ffe1e1
```

**Sources:** [benchmarks/imagenet/resnet50/main.py:1-323](), [benchmarks/imagenet/vitb16/main.py:1-304](), [benchmarks/imagenet/resnet50/knn_eval.py:1-106]()

## Supported Datasets

The benchmarking infrastructure supports four standard datasets with different characteristics and use cases.

| Dataset | Classes | Train Images | Val Images | Image Size | Benchmark Script |
|---------|---------|--------------|------------|------------|------------------|
| ImageNet1k | 1000 | 1,281,167 | 50,000 | 224×224 | `benchmarks/imagenet/resnet50/main.py` |
| ImageNet100 | 100 | 130,000 | 5,000 | 224×224 | `docs/source/getting_started/benchmarks/imagenet100_benchmark.py` |
| Imagenette | 10 | 9,469 | 3,925 | 160→128 | `docs/source/getting_started/benchmarks/imagenette_benchmark.py` |
| CIFAR-10 | 10 | 50,000 | 10,000 | 32×32 | `docs/source/getting_started/benchmarks/cifar10_benchmark.py` |

**Dataset Selection Guidelines:**
- **ImageNet1k**: Standard benchmark for comparing with published SSL papers. Training takes ~4 days on 2×4090 GPUs for 100 epochs.
- **ImageNet100**: Faster alternative (20-30 hours) for development and hyperparameter tuning.
- **Imagenette**: Quick validation (3-5 hours) for testing implementations.
- **CIFAR-10**: Small-scale testing with modified ResNet-18 architecture (3×3 initial convolution, no MaxPool).

**Sources:** [docs/source/getting_started/benchmarks.rst:14-219](), [README.md:285-327]()

## Evaluation Protocols

Benchmarks use three standardized evaluation protocols to measure learned representation quality. Each protocol freezes or fine-tunes different parts of the model.

```mermaid
graph LR
    subgraph "kNN Evaluation"
        KNN_INPUT["Test Image"]
        KNN_BACKBONE["Backbone<br/>(frozen)"]
        KNN_FEATURES["Features"]
        KNN_SEARCH["k-Nearest<br/>Neighbors"]
        KNN_PRED["Prediction"]
        
        KNN_INPUT --> KNN_BACKBONE
        KNN_BACKBONE --> KNN_FEATURES
        KNN_FEATURES --> KNN_SEARCH
        KNN_SEARCH --> KNN_PRED
    end
    
    subgraph "Linear Evaluation"
        LIN_INPUT["Train Image"]
        LIN_BACKBONE["Backbone<br/>(frozen)"]
        LIN_FEATURES["Features"]
        LIN_HEAD["Linear Head<br/>(trainable)"]
        LIN_PRED["Prediction"]
        
        LIN_INPUT --> LIN_BACKBONE
        LIN_BACKBONE --> LIN_FEATURES
        LIN_FEATURES --> LIN_HEAD
        LIN_HEAD --> LIN_PRED
    end
    
    subgraph "Fine-tune Evaluation"
        FT_INPUT["Train Image"]
        FT_BACKBONE["Backbone<br/>(trainable)"]
        FT_FEATURES["Features"]
        FT_HEAD["Linear Head<br/>(trainable)"]
        FT_PRED["Prediction"]
        
        FT_INPUT --> FT_BACKBONE
        FT_BACKBONE --> FT_FEATURES
        FT_FEATURES --> FT_HEAD
        FT_HEAD --> FT_PRED
    end
    
    style KNN_BACKBONE fill:#e1f5ff
    style LIN_BACKBONE fill:#e1f5ff
    style FT_BACKBONE fill:#ffe1e1
    style LIN_HEAD fill:#ffe1e1
    style FT_HEAD fill:#ffe1e1
```

**Sources:** [benchmarks/imagenet/resnet50/knn_eval.py:17-106](), [benchmarks/imagenet/resnet50/linear_eval.py:17-119](), [benchmarks/imagenet/resnet50/finetune_eval.py:17-119]()

### kNN Evaluation

The k-Nearest Neighbors evaluation protocol provides a parameter-free assessment of representation quality. It follows InstDisc [arxiv:1805.01978] settings.

**Configuration:**
- **k (neighbors)**: 200 for ImageNet1k, 20 for ImageNet100, 200 for CIFAR-10
- **Temperature**: 0.1 for ResNet, 0.07 for ViT
- **Feature normalization**: L2 normalization applied
- **No training required**: Uses training set as memory bank

**Implementation:** The `KNNClassifier` class at [lightly/utils/benchmarking/knn_classifier.py:13-170]() implements the evaluation:

```python
# Key components of KNN evaluation
classifier = KNNClassifier(
    model=model,           # Pre-trained SSL model
    num_classes=num_classes,
    knn_k=200,            # Number of neighbors
    knn_t=0.1,            # Temperature for reweighting
)

# Two-pass evaluation:
# Pass 1: Extract features from training set
# Pass 2: Classify validation samples using kNN
trainer.validate(
    model=classifier,
    dataloaders=[train_dataloader, val_dataloader],
)
```

**Process:**
1. Extract features from all training images using frozen backbone
2. Store features in memory bank on GPU/CPU
3. For each validation image, find k nearest neighbors in feature space
4. Weight neighbors by temperature-scaled cosine similarity
5. Predict class via weighted voting

**Sources:** [benchmarks/imagenet/resnet50/knn_eval.py:17-106](), [lightly/utils/benchmarking/knn_classifier.py:13-170]()

### Linear Evaluation

Linear evaluation trains a linear classifier on top of frozen features, following SimCLR settings.

**Configuration (ResNet):**
- **Epochs**: 90
- **Optimizer**: SGD
- **Learning rate**: 0.1 (base) × batch_size / 256
- **Momentum**: 0.9
- **Weight decay**: 0.0
- **LR schedule**: Cosine annealing without warmup
- **Backbone**: Frozen

**Configuration (ViT with MAE):**
- **Epochs**: 90
- **Optimizer**: LARS
- **Learning rate**: Scaled by batch size
- **Weight decay**: 0.0
- **LR schedule**: Cosine with 10-epoch warmup
- **Additional**: BatchNorm layer before classification head

**Implementation Details:**

The `LinearClassifier` class freezes the backbone and trains only the classification head:

```python
classifier = LinearClassifier(
    model=model,
    batch_size_per_device=batch_size_per_device,
    feature_dim=model.online_classifier.feature_dim,
    num_classes=num_classes,
)
```

For MAE models, a specialized `LinearClassifierMAE` variant adds BatchNorm before the linear layer and uses LARS optimizer at [benchmarks/imagenet/vitb16/linear_eval.py:20-72]().

**Sources:** [benchmarks/imagenet/resnet50/linear_eval.py:17-119](), [benchmarks/imagenet/vitb16/linear_eval.py:74-174]()

### Fine-tuning Evaluation

Fine-tuning evaluation trains both the backbone and classification head, following SimCLR settings for ResNet and MAE settings for ViT.

**Configuration (ResNet):**
- **Epochs**: 30
- **Optimizer**: SGD
- **Learning rate**: 0.05 (base) × batch_size / 256
- **Momentum**: 0.9
- **Weight decay**: 0.0
- **LR schedule**: Cosine annealing without warmup

**Configuration (ViT with MAE):**
- **Epochs**: 100
- **Optimizer**: AdamW with layer-wise learning rate decay (0.65)
- **Base learning rate**: 5e-4
- **Weight decay**: 0.05 (varies by layer)
- **Augmentation**: RandAugment, Mixup, CutMix
- **Stochastic depth**: 0.1
- **LR schedule**: Cosine with 5-epoch warmup

**MAE-specific Features:**

The `FinetuneClassifierMAE` class at [benchmarks/imagenet/vitb16/finetune_eval.py:28-142]() implements advanced techniques:
- **Mixup and CutMix**: Data augmentation applied during training
- **Layer-wise LR decay**: Different learning rates for each ViT layer
- **Stochastic depth**: Path dropout added to ViT blocks

**Sources:** [benchmarks/imagenet/resnet50/finetune_eval.py:17-119](), [benchmarks/imagenet/vitb16/finetune_eval.py:28-269]()

## Running Benchmarks

### ImageNet Benchmarks

The main ImageNet benchmark scripts support both ResNet50 and ViT-B/16 backbones with multiple SSL methods.

**ResNet50 Benchmark:**

```bash
cd benchmarks/imagenet/resnet50
python main.py \
    --train-dir /datasets/imagenet/train \
    --val-dir /datasets/imagenet/val \
    --batch-size-per-device 128 \
    --epochs 100 \
    --devices 2 \
    --accelerator gpu \
    --methods simclr byol dino
```

**ViT-B/16 Benchmark:**

```bash
cd benchmarks/imagenet/vitb16
python main.py \
    --train-dir /datasets/imagenet/train \
    --val-dir /datasets/imagenet/val \
    --batch-size-per-device 128 \
    --epochs 100 \
    --devices 2 \
    --eval-method mae \
    --methods mae dino ibot
```

**Key Parameters:**
- `--methods`: Space-separated list of SSL methods to benchmark
- `--batch-size-per-device`: Batch size per GPU (total = devices × batch_size_per_device)
- `--epochs`: Training epochs (0 to skip pre-training and only evaluate)
- `--ckpt-path`: Path to pre-trained checkpoint for evaluation-only runs
- `--skip-knn-eval`, `--skip-linear-eval`, `--skip-finetune-eval`: Skip specific evaluation protocols
- `--strategy`: PyTorch Lightning strategy (default: `ddp_find_unused_parameters_true`)

**Available Methods:**

ResNet50: `barlowtwins`, `byol`, `dcl`, `dclw`, `dino`, `mocov2`, `simclr`, `swav`, `tico`, `vicreg`

ViT-B/16: `dino`, `dinov2`, `ibot`, `mae`, `aim`

**Sources:** [benchmarks/imagenet/resnet50/main.py:48-86](), [benchmarks/imagenet/vitb16/main.py:31-60]()

### CIFAR-10, Imagenette, and ImageNet100 Benchmarks

Smaller dataset benchmarks use standalone Python scripts with embedded configuration.

**CIFAR-10 Example:**

```python
# Edit configuration in cifar10_benchmark.py
max_epochs = 200
batch_size = 128
models = [SimCLRModel, BYOLModel, DINOModel]

# Run benchmark
python docs/source/getting_started/benchmarks/cifar10_benchmark.py
```

**Key Configuration Variables:**
- `max_epochs`: Training duration
- `batch_size`: Batch size for training
- `knn_k`, `knn_t`: kNN evaluation parameters
- `distributed`: Enable distributed training
- `sync_batchnorm`: Synchronize batch norm across GPUs
- `gather_distributed`: Gather features across GPUs for loss computation

**Sources:** [docs/source/getting_started/benchmarks/cifar10_benchmark.py:101-139](), [docs/source/getting_started/benchmarks/imagenette_benchmark.py:119-162]()

## Benchmark Workflow

The benchmark execution follows a consistent workflow across all datasets and methods.

```mermaid
flowchart TD
    START["Start Benchmark"]
    INIT["Initialize Method<br/>Load backbone, heads"]
    
    PRETRAIN_CHECK{"epochs > 0?"}
    PRETRAIN["Pre-training Phase<br/>pretrain()"]
    LOAD_CKPT["Load Checkpoint<br/>--ckpt-path"]
    
    TRAIN_DATA["Setup Training Data<br/>LightlyDataset + Transform"]
    TRAINER["PyTorch Lightning Trainer<br/>with callbacks"]
    TRAIN_LOOP["Training Loop<br/>self-supervised loss"]
    ONLINE_EVAL["Online Classification<br/>OnlineLinearClassifier"]
    SAVE_CKPT["Save Checkpoint"]
    
    KNN_CHECK{"skip_knn_eval?"}
    KNN_EVAL["kNN Evaluation<br/>knn_eval()"]
    
    LINEAR_CHECK{"skip_linear_eval?"}
    LINEAR_EVAL["Linear Evaluation<br/>linear_eval()"]
    
    FINETUNE_CHECK{"skip_finetune_eval?"}
    FINETUNE_EVAL["Fine-tune Evaluation<br/>finetune_eval()"]
    
    METRICS["Aggregate Metrics<br/>Top1, Top5"]
    REPORT["Print Results<br/>Markdown table"]
    END["End Benchmark"]
    
    START --> INIT
    INIT --> PRETRAIN_CHECK
    
    PRETRAIN_CHECK -->|Yes| PRETRAIN
    PRETRAIN_CHECK -->|No| LOAD_CKPT
    
    PRETRAIN --> TRAIN_DATA
    TRAIN_DATA --> TRAINER
    TRAINER --> TRAIN_LOOP
    TRAIN_LOOP --> ONLINE_EVAL
    ONLINE_EVAL --> SAVE_CKPT
    
    LOAD_CKPT --> KNN_CHECK
    SAVE_CKPT --> KNN_CHECK
    
    KNN_CHECK -->|No| KNN_EVAL
    KNN_CHECK -->|Yes| LINEAR_CHECK
    KNN_EVAL --> LINEAR_CHECK
    
    LINEAR_CHECK -->|No| LINEAR_EVAL
    LINEAR_CHECK -->|Yes| FINETUNE_CHECK
    LINEAR_EVAL --> FINETUNE_CHECK
    
    FINETUNE_CHECK -->|No| FINETUNE_EVAL
    FINETUNE_CHECK -->|Yes| METRICS
    FINETUNE_EVAL --> METRICS
    
    METRICS --> REPORT
    REPORT --> END
    
    style PRETRAIN fill:#e1f5ff
    style KNN_EVAL fill:#ffe1e1
    style LINEAR_EVAL fill:#ffe1e1
    style FINETUNE_EVAL fill:#ffe1e1
```

**Sources:** [benchmarks/imagenet/resnet50/main.py:88-208](), [benchmarks/imagenet/vitb16/main.py:63-188]()

## Metrics and Logging

### Metric Tracking

The `MetricCallback` class tracks metrics during training and evaluation:

```python
from lightly.utils.benchmarking import MetricCallback

metric_callback = MetricCallback()
trainer = Trainer(callbacks=[metric_callback])
trainer.fit(model, train_dataloader, val_dataloader)

# Access metrics
max_top1 = max(metric_callback.val_metrics["val_top1"])
max_top5 = max(metric_callback.val_metrics["val_top5"])
```

**Tracked Metrics:**
- `train_loss`: Self-supervised training loss
- `val_online_cls_top1`, `val_online_cls_top5`: Online classifier accuracy during pre-training
- `val_top1`, `val_top5`: Evaluation protocol accuracy (kNN, linear, fine-tune)

**Sources:** [benchmarks/imagenet/resnet50/main.py:258-286](), [lightly/utils/benchmarking/knn_classifier.py:158-164]()

### Online Classification

During pre-training, an online linear classifier tracks representation quality without interrupting training:

```python
from lightly.utils.benchmarking import OnlineLinearClassifier

self.online_classifier = OnlineLinearClassifier(
    feature_dim=384,
    num_classes=num_classes
)

# In training_step
cls_loss, cls_log = self.online_classifier.training_step(
    (features.detach(), targets), batch_idx
)
self.log_dict(cls_log)
```

This provides early feedback on model quality and helps detect training issues.

**Sources:** [benchmarks/imagenet/vitb16/dino.py:35-91]()

### TensorBoard Logging

All benchmarks log to TensorBoard for visualization:

```python
trainer = Trainer(
    logger=TensorBoardLogger(
        save_dir=str(log_dir),
        name="pretrain"  # or "knn_eval", "linear_eval", "finetune_eval"
    )
)
```

**Log Structure:**
```
benchmark_logs/
  method_name/
    2024-01-15_10-30-45/
      pretrain/
        version_0/
          events.out.tfevents.*
          checkpoints/
            epoch=99-step=500400.ckpt
      knn_eval/
        version_0/
          events.out.tfevents.*
      linear_eval/
        version_0/
          events.out.tfevents.*
      finetune_eval/
        version_0/
          events.out.tfevents.*
```

**Sources:** [benchmarks/imagenet/resnet50/main.py:270](), [benchmarks/imagenet/resnet50/knn_eval.py:84]()

## Benchmark Results Format

The benchmark scripts output results in markdown table format for easy documentation:

```python
def eval_metrics_to_markdown(metrics: Dict[str, Dict[str, float]]) -> str:
    """Convert evaluation metrics to markdown table."""
    # Example output:
    # | Eval Name | Metric Name | Value |
    # |:----------|:------------|:------|
    # | knn       | val_top1    | 67.50 |
    # | knn       | val_top5    | 89.70 |
    # | linear    | val_top1    | 73.30 |
    # | linear    | val_top5    | 91.30 |
    # | finetune  | val_top1    | 79.80 |
    # | finetune  | val_top5    | 95.00 |
```

**Sources:** [benchmarks/imagenet/resnet50/main.py:288-318](), [benchmarks/imagenet/vitb16/main.py:269-299]()

## Implementation Notes

### Distributed Training

Benchmarks support distributed training via PyTorch Lightning:

```python
trainer = Trainer(
    devices=2,                          # Number of GPUs
    accelerator="gpu",
    strategy="ddp_find_unused_parameters_true",
    sync_batchnorm=True,               # Sync BN across GPUs
)

# Loss functions support distributed gather
criterion = NTXentLoss(gather_distributed=True)
```

**Sources:** [benchmarks/imagenet/resnet50/main.py:259-274]()

### Memory Optimization

For large-scale benchmarks, several optimizations reduce memory usage:

1. **Feature dtype reduction:** kNN classifier supports `torch.float16` features
2. **Persistent workers:** Reuse dataloader workers across epochs
3. **No sanity validation:** Set `num_sanity_val_steps=0` to save memory
4. **Gradient checkpointing:** Can be enabled for ViT models

**Sources:** [lightly/utils/benchmarking/knn_classifier.py:43-46](), [benchmarks/imagenet/vitb16/main.py:255]()

### Custom Backbones

Benchmarks can be extended with custom backbones by implementing the method interface:

```python
# Method must provide:
# - model: LightningModule with forward() method
# - transform: Data augmentation transform

METHODS = {
    "custom_method": {
        "model": CustomModel,
        "transform": CustomTransform(),
    }
}
```

**Sources:** [benchmarks/imagenet/resnet50/main.py:71-85]()

---

# Page: ImageNet Benchmarks

# ImageNet Benchmarks

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [benchmarks/imagenet/resnet50/finetune_eval.py](benchmarks/imagenet/resnet50/finetune_eval.py)
- [benchmarks/imagenet/resnet50/knn_eval.py](benchmarks/imagenet/resnet50/knn_eval.py)
- [benchmarks/imagenet/resnet50/linear_eval.py](benchmarks/imagenet/resnet50/linear_eval.py)
- [benchmarks/imagenet/resnet50/main.py](benchmarks/imagenet/resnet50/main.py)
- [benchmarks/imagenet/vitb16/dino.py](benchmarks/imagenet/vitb16/dino.py)
- [benchmarks/imagenet/vitb16/finetune_eval.py](benchmarks/imagenet/vitb16/finetune_eval.py)
- [benchmarks/imagenet/vitb16/knn_eval.py](benchmarks/imagenet/vitb16/knn_eval.py)
- [benchmarks/imagenet/vitb16/linear_eval.py](benchmarks/imagenet/vitb16/linear_eval.py)
- [benchmarks/imagenet/vitb16/main.py](benchmarks/imagenet/vitb16/main.py)
- [docs/source/getting_started/benchmarks.rst](docs/source/getting_started/benchmarks.rst)
- [docs/source/getting_started/benchmarks/cifar10_benchmark.py](docs/source/getting_started/benchmarks/cifar10_benchmark.py)
- [docs/source/getting_started/benchmarks/imagenet100_benchmark.py](docs/source/getting_started/benchmarks/imagenet100_benchmark.py)
- [docs/source/getting_started/benchmarks/imagenette_benchmark.py](docs/source/getting_started/benchmarks/imagenette_benchmark.py)
- [lightly/utils/benchmarking/knn_classifier.py](lightly/utils/benchmarking/knn_classifier.py)
- [tests/utils/benchmarking/test_knn_classifier.py](tests/utils/benchmarking/test_knn_classifier.py)

</details>



## Purpose and Scope

The ImageNet benchmarks provide standardized evaluation of self-supervised learning (SSL) methods on the ImageNet-1K dataset. These benchmarks measure the quality of learned representations through three evaluation protocols: k-Nearest Neighbors (kNN), linear probing, and fine-tuning. The benchmarks support both ResNet50 and Vision Transformer (ViT) backbones with multiple SSL methods.

For detailed information about the evaluation protocols themselves (kNN, linear, fine-tuning), see [Evaluation Protocols](#7.2). For benchmarks on other datasets (ImageNet100, Imagenette, CIFAR-10), see [Benchmarking](#7).

## Supported Configurations

The ImageNet benchmarks support two primary backbone architectures with different SSL methods:

| Backbone | SSL Methods Supported | Benchmark Directory |
|----------|----------------------|---------------------|
| ResNet50 | BarlowTwins, BYOL, DCL, DCLW, DINO, MoCoV2, SimCLR, SwAV, TiCo, VICReg | [benchmarks/imagenet/resnet50]() |
| ViT-B/16 | AIM, DINO, DINOv2, iBOT, MAE | [benchmarks/imagenet/vitb16]() |
| ViT-S/16 | DINO, iBOT | [benchmarks/imagenet/vitb16]() |

Sources: [benchmarks/imagenet/resnet50/main.py:71-85](), [benchmarks/imagenet/vitb16/main.py:54-60](), [README.md:297-311]()

## Benchmark Architecture

### Component Overview

```mermaid
graph TB
    subgraph "Entry Point"
        MAIN["main.py<br/>Command-line interface"]
    end
    
    subgraph "SSL Methods"
        BARLOWTWINS["barlowtwins.py"]
        BYOL["byol.py"]
        DINO["dino.py"]
        MAE["mae.py"]
        SIMCLR["simclr.py"]
        SWAV["swav.py"]
        OTHER["... other methods"]
    end
    
    subgraph "Pretraining"
        PRETRAIN["pretrain()<br/>Trains SSL model"]
        DATASET["LightlyDataset"]
        TRANSFORM["Method-specific<br/>Transform"]
        TRAINER["PyTorch Lightning<br/>Trainer"]
    end
    
    subgraph "Evaluation"
        KNN["knn_eval.py<br/>knn_eval()"]
        LINEAR["linear_eval.py<br/>linear_eval()"]
        FINETUNE["finetune_eval.py<br/>finetune_eval()"]
    end
    
    subgraph "Evaluation Components"
        KNNCLASS["KNNClassifier"]
        LINEARCLASS["LinearClassifier"]
        FINETUNECLASS["FinetuneClassifier"]
    end
    
    subgraph "Outputs"
        CKPT["model.ckpt<br/>Trained weights"]
        TENSORBOARD["TensorBoard logs"]
        METRICS["Evaluation metrics<br/>Top1/Top5 accuracy"]
    end
    
    MAIN --> PRETRAIN
    MAIN --> KNN
    MAIN --> LINEAR
    MAIN --> FINETUNE
    
    PRETRAIN --> BARLOWTWINS
    PRETRAIN --> BYOL
    PRETRAIN --> DINO
    PRETRAIN --> MAE
    PRETRAIN --> SIMCLR
    PRETRAIN --> SWAV
    PRETRAIN --> OTHER
    
    BARLOWTWINS --> DATASET
    BARLOWTWINS --> TRANSFORM
    TRANSFORM --> TRAINER
    DATASET --> TRAINER
    
    TRAINER --> CKPT
    TRAINER --> TENSORBOARD
    
    KNN --> KNNCLASS
    LINEAR --> LINEARCLASS
    FINETUNE --> FINETUNECLASS
    
    KNNCLASS --> METRICS
    LINEARCLASS --> METRICS
    FINETUNECLASS --> METRICS
```

Sources: [benchmarks/imagenet/resnet50/main.py:88-208](), [benchmarks/imagenet/vitb16/main.py:63-188]()

### Benchmark Workflow

```mermaid
graph LR
    START["Start Benchmark"] --> SETUP["Setup:<br/>Load dataset<br/>Initialize model<br/>Configure transform"]
    
    SETUP --> PRETRAIN_CHECK{epochs > 0?}
    
    PRETRAIN_CHECK -->|Yes| PRETRAIN["pretrain():<br/>Train SSL model<br/>for N epochs"]
    PRETRAIN_CHECK -->|No| LOAD["Load from<br/>--ckpt-path"]
    
    PRETRAIN --> SAVE["Save checkpoint<br/>to log_dir"]
    LOAD --> EVAL_START
    SAVE --> EVAL_START
    
    EVAL_START["Begin Evaluations"] --> KNN_CHECK{skip_knn_eval?}
    
    KNN_CHECK -->|No| KNN["knn_eval():<br/>K-NN accuracy<br/>k=200, t=0.1"]
    KNN_CHECK -->|Yes| LINEAR_CHECK
    
    KNN --> LINEAR_CHECK{skip_linear_eval?}
    
    LINEAR_CHECK -->|No| LINEAR["linear_eval():<br/>90 epochs<br/>Frozen backbone"]
    LINEAR_CHECK -->|Yes| FINETUNE_CHECK
    
    LINEAR --> FINETUNE_CHECK{skip_finetune_eval?}
    
    FINETUNE_CHECK -->|No| FINETUNE["finetune_eval():<br/>30 epochs<br/>All params"]
    FINETUNE_CHECK -->|Yes| REPORT
    
    FINETUNE --> REPORT["Report Results:<br/>Print markdown table<br/>with all metrics"]
    
    REPORT --> END["End"]
```

Sources: [benchmarks/imagenet/resnet50/main.py:88-208](), [benchmarks/imagenet/vitb16/main.py:63-188]()

## Directory Structure

The benchmark code is organized by backbone architecture:

```mermaid
graph TB
    BENCH["benchmarks/imagenet/"]
    
    RESNET["resnet50/"]
    VIT["vitb16/"]
    
    BENCH --> RESNET
    BENCH --> VIT
    
    RESNET --> R_MAIN["main.py<br/>Entry point"]
    RESNET --> R_KNN["knn_eval.py"]
    RESNET --> R_LINEAR["linear_eval.py"]
    RESNET --> R_FINETUNE["finetune_eval.py"]
    RESNET --> R_METHODS["Method files:<br/>barlowtwins.py<br/>byol.py<br/>dino.py<br/>simclr.py<br/>..."]
    
    VIT --> V_MAIN["main.py<br/>Entry point"]
    VIT --> V_KNN["knn_eval.py"]
    VIT --> V_LINEAR["linear_eval.py"]
    VIT --> V_FINETUNE["finetune_eval.py"]
    VIT --> V_METHODS["Method files:<br/>dino.py<br/>mae.py<br/>ibot.py<br/>..."]
```

Sources: [benchmarks/imagenet/resnet50/main.py:1-323](), [benchmarks/imagenet/vitb16/main.py:1-304]()

## Running Benchmarks

### Basic Usage

The benchmark scripts use command-line arguments for configuration:

**ResNet50 Benchmarks:**
```bash
python benchmarks/imagenet/resnet50/main.py \
    --train-dir /datasets/imagenet/train \
    --val-dir /datasets/imagenet/val \
    --methods simclr dino byol \
    --batch-size-per-device 128 \
    --epochs 100 \
    --devices 2 \
    --accelerator gpu
```

**ViT-B/16 Benchmarks:**
```bash
python benchmarks/imagenet/vitb16/main.py \
    --train-dir /datasets/imagenet/train \
    --val-dir /datasets/imagenet/val \
    --methods mae dino \
    --batch-size-per-device 128 \
    --epochs 100 \
    --devices 2 \
    --accelerator gpu
```

Sources: [benchmarks/imagenet/resnet50/main.py:48-70](), [benchmarks/imagenet/vitb16/main.py:31-53]()

### Command-Line Arguments

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `--train-dir` | Path | `/datasets/imagenet/train` | ImageNet training directory |
| `--val-dir` | Path | `/datasets/imagenet/val` | ImageNet validation directory |
| `--log-dir` | Path | `benchmark_logs` | Directory for logs and checkpoints |
| `--batch-size-per-device` | int | 128 | Batch size per GPU |
| `--epochs` | int | 100 | Number of pretraining epochs |
| `--num-workers` | int | 8 | DataLoader worker processes |
| `--accelerator` | str | `gpu` | Hardware accelerator (gpu/cpu) |
| `--devices` | int | 1 | Number of devices to use |
| `--precision` | str | `16-mixed` | Training precision |
| `--methods` | str[] | All methods | SSL methods to benchmark |
| `--ckpt-path` | Path | None | Load checkpoint instead of training |
| `--skip-knn-eval` | bool | False | Skip kNN evaluation |
| `--skip-linear-eval` | bool | False | Skip linear evaluation |
| `--skip-finetune-eval` | bool | False | Skip fine-tuning evaluation |
| `--knn-k` | int | 200 | Number of nearest neighbors |
| `--knn-t` | float | 0.1 (ResNet) / 0.07 (ViT) | kNN temperature parameter |
| `--strategy` | str | `ddp_find_unused_parameters_true` | PyTorch Lightning strategy |
| `--seed` | int | None | Random seed for reproducibility |

Sources: [benchmarks/imagenet/resnet50/main.py:48-70](), [benchmarks/imagenet/vitb16/main.py:31-53]()

### Example: Training and Evaluating

To train SimCLR on ResNet50 for 100 epochs and run all evaluations:

```bash
python benchmarks/imagenet/resnet50/main.py \
    --train-dir /datasets/imagenet/train \
    --val-dir /datasets/imagenet/val \
    --methods simclr \
    --batch-size-per-device 256 \
    --epochs 100 \
    --devices 2 \
    --precision 16-mixed
```

To evaluate an existing checkpoint without retraining:

```bash
python benchmarks/imagenet/resnet50/main.py \
    --ckpt-path path/to/checkpoint.ckpt \
    --methods simclr \
    --epochs 0 \
    --devices 2
```

Sources: [benchmarks/imagenet/resnet50/main.py:132-151]()

## Pretraining Process

The `pretrain()` function orchestrates the SSL model training:

```mermaid
graph TB
    PRETRAIN_START["pretrain() called"] --> SETUP_DATA["Setup Data:<br/>Create LightlyDataset<br/>Apply method transform<br/>Create DataLoader"]
    
    SETUP_DATA --> SETUP_VAL["Setup Validation:<br/>Standard transforms<br/>Resize → CenterCrop<br/>Normalize"]
    
    SETUP_VAL --> SETUP_CALLBACKS["Setup Callbacks:<br/>LearningRateMonitor<br/>EarlyStopping<br/>DeviceStatsMonitor<br/>MetricCallback"]
    
    SETUP_CALLBACKS --> CREATE_TRAINER["Create Trainer:<br/>max_epochs<br/>accelerator<br/>devices<br/>strategy<br/>precision"]
    
    CREATE_TRAINER --> FIT["trainer.fit():<br/>train_dataloaders<br/>val_dataloaders<br/>ckpt_path"]
    
    FIT --> LOG_METRICS["Log Metrics:<br/>val_online_cls_top1<br/>val_online_cls_top5"]
    
    LOG_METRICS --> SAVE_CKPT["Save Checkpoint:<br/>log_dir/pretrain/version_0/<br/>checkpoints/epoch=N.ckpt"]
```

**Key Components:**

- **Dataset:** `LightlyDataset` loads images from the training directory
- **Transforms:** Method-specific transforms from `METHODS[method]["transform"]`
- **Trainer:** PyTorch Lightning `Trainer` with distributed training support
- **Callbacks:** Track metrics and monitor training progress
- **Online Classifier:** Most SSL models include an `OnlineLinearClassifier` that trains during pretraining to provide intermediate validation metrics

Sources: [benchmarks/imagenet/resnet50/main.py:210-286](), [benchmarks/imagenet/vitb16/main.py:190-267]()

## Evaluation Protocols

After pretraining, the benchmark runs three evaluation protocols. For detailed information about these protocols, see [Evaluation Protocols](#7.2).

### kNN Evaluation

The `knn_eval()` function evaluates representation quality using k-Nearest Neighbors classification:

**Key Settings:**
- **k (knn_k):** 200 neighbors
- **Temperature (knn_t):** 0.1 for ResNet50, 0.07 for ViT
- **Implementation:** `KNNClassifier` from [lightly/utils/benchmarking/knn_classifier.py]()
- **Protocol:** Based on InstDisc (Wu et al., 2018)

Sources: [benchmarks/imagenet/resnet50/knn_eval.py:17-106](), [benchmarks/imagenet/vitb16/knn_eval.py:17-106]()

### Linear Evaluation

The `linear_eval()` function trains a linear classifier on frozen features:

**Key Settings:**
- **Epochs:** 90
- **Learning Rate:** 0.1 (ResNet), varies for ViT
- **Optimizer:** SGD for ResNet, LARS for ViT with MAE
- **Protocol:** Based on SimCLR (Chen et al., 2020)

Sources: [benchmarks/imagenet/resnet50/linear_eval.py:17-119](), [benchmarks/imagenet/vitb16/linear_eval.py:74-174]()

### Fine-tuning Evaluation

The `finetune_eval()` function fine-tunes the entire model:

**Key Settings:**
- **Epochs:** 30 for ResNet, 100 for ViT
- **Learning Rate:** 0.05 (ResNet), 5e-4 (ViT with MAE)
- **Optimizer:** SGD for ResNet, AdamW for ViT
- **Additional:** Mixup/CutMix for ViT with MAE
- **Protocol:** Based on SimCLR for ResNet, MAE for ViT

Sources: [benchmarks/imagenet/resnet50/finetune_eval.py:17-119](), [benchmarks/imagenet/vitb16/finetune_eval.py:144-269]()

## SSL Method Implementations

Each SSL method is implemented in its own Python file. The structure follows this pattern:

```mermaid
graph TB
    METHOD_FILE["Method file<br/>(e.g., simclr.py)"]
    
    METHOD_FILE --> MODEL_CLASS["LightningModule<br/>SSL Model Class"]
    METHOD_FILE --> TRANSFORM["transform variable<br/>Method-specific transform"]
    
    MODEL_CLASS --> BACKBONE["backbone<br/>ResNet or ViT"]
    MODEL_CLASS --> HEADS["Projection/Prediction<br/>Heads"]
    MODEL_CLASS --> CRITERION["Loss Function"]
    MODEL_CLASS --> ONLINE_CLS["online_classifier<br/>OnlineLinearClassifier"]
    
    MODEL_CLASS --> TRAIN_STEP["training_step()"]
    MODEL_CLASS --> VAL_STEP["validation_step()"]
    MODEL_CLASS --> CONFIGURE_OPT["configure_optimizers()"]
    
    TRAIN_STEP --> LOSS_COMPUTE["Compute SSL loss"]
    TRAIN_STEP --> ONLINE_TRAIN["Train online classifier"]
    
    VAL_STEP --> ONLINE_VAL["Validate online classifier"]
```

**Example: DINO for ViT-S/16**

The DINO implementation demonstrates the typical structure:

- **Model Class:** `DINO(LightningModule)` at [benchmarks/imagenet/vitb16/dino.py:18-155]()
- **Backbone:** `MaskedVisionTransformerTIMM` wrapping `vit_small_patch16_224`
- **Heads:** `DINOProjectionHead` for both student and teacher
- **Loss:** `DINOLoss` for distillation
- **Transform:** `DINOTransform` with global and local views
- **Momentum Update:** Teacher network updated with cosine schedule
- **Online Classifier:** Evaluates features during training

Sources: [benchmarks/imagenet/vitb16/dino.py:18-172]()

## Benchmark Results and Outputs

### Output Structure

Each benchmark run creates a timestamped directory:

```
benchmark_logs/
└── {method}/
    └── {timestamp}/
        ├── pretrain/
        │   └── version_0/
        │       ├── checkpoints/
        │       │   └── epoch=99-step=500400.ckpt
        │       └── events.out.tfevents.*
        ├── knn_eval/
        │   └── version_0/
        │       └── events.out.tfevents.*
        ├── linear_eval/
        │   └── version_0/
        │       └── events.out.tfevents.*
        └── finetune_eval/
            └── version_0/
                └── events.out.tfevents.*
```

Sources: [benchmarks/imagenet/resnet50/main.py:119-122]()

### Metrics Reporting

At the end of evaluation, the benchmark prints a markdown table with results:

```
| Eval Name | Metric Name | Value  |
|:----------|:------------|:-------|
| knn       | val_top1    | 44.80  |
| knn       | val_top5    | 73.90  |
| linear    | val_top1    | 63.20  |
| linear    | val_top5    | 85.20  |
| finetune  | val_top1    | 73.90  |
| finetune  | val_top5    | 91.90  |
```

The function `eval_metrics_to_markdown()` formats these results:

Sources: [benchmarks/imagenet/resnet50/main.py:288-317](), [benchmarks/imagenet/vitb16/main.py:269-298]()

### Published Results

The official benchmark results are maintained in the repository documentation. For ResNet50 (100 epochs, batch size 256):

| Model | Linear Top1 | Finetune Top1 | kNN Top1 | Checkpoint |
|-------|-------------|---------------|----------|------------|
| SimCLR* | 63.2 | 73.9 | 44.8 | [link](https://lightly-ssl-checkpoints.s3.amazonaws.com/imagenet_resnet50_simclr_2023-06-22_09-11-13/pretrain/version_0/checkpoints/epoch%3D99-step%3D500400.ckpt) |
| DINO (Res50) | 68.2 | 72.5 | 49.9 | [link](https://lightly-ssl-checkpoints.s3.amazonaws.com/imagenet_resnet50_dino_2023-06-06_13-59-48/pretrain/version_0/checkpoints/epoch%3D99-step%3D1000900.ckpt) |
| SwAV | 67.2 | 75.4 | 49.5 | [link](https://lightly-ssl-checkpoints.s3.amazonaws.com/imagenet_resnet50_swav_2023-05-25_08-29-14/pretrain/version_0/checkpoints/epoch%3D99-step%3D500400.ckpt) |

For ViT (100 epochs, batch size 128-256):

| Model | Backbone | Linear Top1 | Finetune Top1 | kNN Top1 |
|-------|----------|-------------|---------------|----------|
| DINO | ViT-S/16 | 73.3 | 79.8 | 67.5 |
| iBOT | ViT-S/16 | 72.2 | 78.3 | 65.4 |
| MAE | ViT-B/16 | 46.0 | 81.3 | 11.2 |

*Note: SimCLR uses square root learning rate scaling instead of linear scaling for better results with smaller batch sizes.*

Sources: [README.md:297-311](), [docs/source/getting_started/benchmarks.rst:30-48]()

## Hardware Requirements

The benchmarks were conducted on systems with the following specifications:

- **GPU:** 2x NVIDIA RTX 4090 (or equivalent)
- **Training Time:** ~4 days for 100 epochs including all evaluations (~35 min/epoch)
- **Memory:** Varies by method, typically 11-17 GB for ResNet50
- **Batch Size:** 128-256 per device (effective batch size: batch_size × devices)

For distributed training, the effective batch size is multiplied by the number of devices, and the learning rate is scaled accordingly using `lr_factor = batch_size / reference_batch_size`.

Sources: [docs/source/getting_started/benchmarks.rst:20-21](), [benchmarks/imagenet/resnet50/main.py:147]()

## Advanced Configuration

### Distributed Training

The benchmarks support distributed data parallel (DDP) training via PyTorch Lightning:

```bash
python benchmarks/imagenet/resnet50/main.py \
    --devices 4 \
    --strategy ddp_find_unused_parameters_true \
    --batch-size-per-device 64  # 64 × 4 = 256 effective batch size
```

The `ddp_find_unused_parameters_true` strategy is used because some SSL methods (like DINO) have unused parameters in the computational graph during certain training steps.

Sources: [benchmarks/imagenet/resnet50/main.py:68-69]()

### Mixed Precision Training

The benchmarks use 16-bit mixed precision by default for faster training:

```bash
python benchmarks/imagenet/resnet50/main.py \
    --precision 16-mixed  # PyTorch AMP mixed precision
```

Sources: [benchmarks/imagenet/resnet50/main.py:57]()

### Model Compilation

For PyTorch 2.0+, model compilation can be enabled for additional performance:

```bash
python benchmarks/imagenet/resnet50/main.py \
    --compile-model
```

This uses `torch.compile()` to optimize the model graph.

Sources: [benchmarks/imagenet/resnet50/main.py:59](), [benchmarks/imagenet/resnet50/main.py:127-130]()

### Reproducibility

To ensure reproducible results, set a random seed:

```bash
python benchmarks/imagenet/resnet50/main.py \
    --seed 42
```

This calls `seed_everything(seed, workers=True)` to set seeds for Python, NumPy, PyTorch, and DataLoader workers.

Sources: [benchmarks/imagenet/resnet50/main.py:69](), [benchmarks/imagenet/resnet50/main.py:112]()

---

# Page: Evaluation Protocols

# Evaluation Protocols

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [benchmarks/imagenet/resnet50/finetune_eval.py](benchmarks/imagenet/resnet50/finetune_eval.py)
- [benchmarks/imagenet/resnet50/knn_eval.py](benchmarks/imagenet/resnet50/knn_eval.py)
- [benchmarks/imagenet/resnet50/linear_eval.py](benchmarks/imagenet/resnet50/linear_eval.py)
- [benchmarks/imagenet/resnet50/main.py](benchmarks/imagenet/resnet50/main.py)
- [benchmarks/imagenet/vitb16/dino.py](benchmarks/imagenet/vitb16/dino.py)
- [benchmarks/imagenet/vitb16/finetune_eval.py](benchmarks/imagenet/vitb16/finetune_eval.py)
- [benchmarks/imagenet/vitb16/knn_eval.py](benchmarks/imagenet/vitb16/knn_eval.py)
- [benchmarks/imagenet/vitb16/linear_eval.py](benchmarks/imagenet/vitb16/linear_eval.py)
- [benchmarks/imagenet/vitb16/main.py](benchmarks/imagenet/vitb16/main.py)
- [lightly/utils/benchmarking/knn_classifier.py](lightly/utils/benchmarking/knn_classifier.py)
- [tests/utils/benchmarking/test_knn_classifier.py](tests/utils/benchmarking/test_knn_classifier.py)

</details>



This document describes the evaluation protocols used to measure the quality of self-supervised learning (SSL) representations in the Lightly framework. These protocols provide standardized methods to assess how well pre-trained models transfer to downstream classification tasks on ImageNet and other datasets.

For information about the benchmark module that integrates these protocols during training, see [Benchmark Module](#7.1). For general benchmarking infrastructure, see [Benchmarking](#7).

## Overview

The Lightly framework implements three standard evaluation protocols for assessing SSL model quality:

1. **kNN Evaluation** - k-Nearest Neighbors classification without any training
2. **Linear Evaluation** - Training a linear classifier on frozen backbone features  
3. **Fine-tuning Evaluation** - End-to-end fine-tuning of the entire model

These protocols follow established practices from influential SSL papers (InstDisc, SimCLR, MoCo, MAE) and provide comparable metrics across different SSL methods. Each protocol represents a different point on the spectrum between zero training (kNN) and full model adaptation (fine-tuning).

**Sources:** [benchmarks/imagenet/resnet50/main.py:88-208](), [benchmarks/imagenet/vitb16/main.py:63-188]()

## Evaluation Protocol Architecture

```mermaid
graph TB
    subgraph "Entry Point"
        MainScript["main.py<br/>main()"]
    end
    
    subgraph "Pre-trained Model"
        PretrainedBackbone["Backbone<br/>(ResNet50/ViT-B/16)<br/>forward(images)"]
        TrainedWeights["Model Checkpoint<br/>.ckpt file"]
    end
    
    subgraph "Evaluation Protocols"
        KNNEval["knn_eval.knn_eval()<br/>KNNClassifier"]
        LinearEval["linear_eval.linear_eval()<br/>LinearClassifier"]
        FinetuneEval["finetune_eval.finetune_eval()<br/>FinetuneClassifier"]
    end
    
    subgraph "Data Preparation"
        TrainData["Training Data<br/>LightlyDataset<br/>ImageNet train/"]
        ValData["Validation Data<br/>LightlyDataset<br/>ImageNet val/"]
        Transforms["Evaluation Transforms<br/>Resize(256)<br/>CenterCrop(224)<br/>Normalize"]
    end
    
    subgraph "Evaluation Results"
        Metrics["Metrics Dictionary<br/>val_top1<br/>val_top5"]
        Logging["TensorBoard Logs<br/>knn_eval/<br/>linear_eval/<br/>finetune_eval/"]
    end
    
    MainScript --> PretrainedBackbone
    TrainedWeights --> PretrainedBackbone
    
    MainScript --> KNNEval
    MainScript --> LinearEval
    MainScript --> FinetuneEval
    
    TrainData --> KNNEval
    ValData --> KNNEval
    TrainData --> LinearEval
    ValData --> LinearEval
    TrainData --> FinetuneEval
    ValData --> FinetuneEval
    
    Transforms --> TrainData
    Transforms --> ValData
    
    PretrainedBackbone --> KNNEval
    PretrainedBackbone --> LinearEval
    PretrainedBackbone --> FinetuneEval
    
    KNNEval --> Metrics
    LinearEval --> Metrics
    FinetuneEval --> Metrics
    
    KNNEval --> Logging
    LinearEval --> Logging
    FinetuneEval --> Logging
```

**Sources:** [benchmarks/imagenet/resnet50/main.py:88-208](), [benchmarks/imagenet/resnet50/knn_eval.py:17-106](), [benchmarks/imagenet/resnet50/linear_eval.py:17-119](), [benchmarks/imagenet/resnet50/finetune_eval.py:17-119]()

## kNN Evaluation Protocol

### Purpose and Settings

The kNN (k-Nearest Neighbors) evaluation protocol assesses representation quality without any training. It extracts features from the pre-trained backbone, builds a feature bank from the training set, and classifies validation samples by voting among their k nearest neighbors.

**Key hyperparameters follow InstDisc [0] settings:**

| Parameter | ResNet50 Value | ViT-B/16 Value | Description |
|-----------|---------------|----------------|-------------|
| `knn_k` | 200 | 200 | Number of nearest neighbors |
| `knn_t` | 0.1 | 0.07 | Temperature for similarity reweighting |
| `normalize` | True | True | L2-normalize features before comparison |
| `feature_dtype` | `torch.float32` | `torch.float32` | Data type for feature storage |

The temperature parameter `knn_t` reweights similarities using a softmax with temperature scaling, emphasizing closer neighbors more strongly.

**Sources:** [benchmarks/imagenet/resnet50/knn_eval.py:17-42](), [benchmarks/imagenet/vitb16/knn_eval.py:17-42]()

### Implementation Flow

```mermaid
graph LR
    subgraph "Phase 1: Feature Extraction - Training Set"
        TrainImages["Training Images<br/>~1.28M samples"]
        ExtractTrain["Extract Features<br/>model.forward(images)<br/>F.normalize(features)"]
        TrainFeatureBank["Train Feature Bank<br/>Tensor(dim, num_samples)<br/>_train_features_tensor"]
        TrainLabels["Train Labels<br/>_train_targets_tensor"]
    end
    
    subgraph "Phase 2: Feature Extraction - Validation Set"
        ValImages["Validation Images<br/>~50K samples"]
        ExtractVal["Extract Features<br/>model.forward(images)<br/>F.normalize(features)"]
        ValFeatures["Validation Features<br/>Batch tensors"]
    end
    
    subgraph "Phase 3: kNN Classification"
        KNNPredict["knn_predict()<br/>Compute similarities<br/>Find k neighbors<br/>Weighted voting"]
        PredictedClasses["Predicted Classes<br/>Per validation sample"]
    end
    
    subgraph "Phase 4: Metric Computation"
        TopKAccuracy["mean_topk_accuracy()<br/>Top-1 and Top-5"]
        Results["Results Dict<br/>val_top1<br/>val_top5"]
    end
    
    TrainImages --> ExtractTrain
    ExtractTrain --> TrainFeatureBank
    ExtractTrain --> TrainLabels
    
    ValImages --> ExtractVal
    ExtractVal --> ValFeatures
    
    ValFeatures --> KNNPredict
    TrainFeatureBank --> KNNPredict
    TrainLabels --> KNNPredict
    
    KNNPredict --> PredictedClasses
    PredictedClasses --> TopKAccuracy
    TopKAccuracy --> Results
```

**Sources:** [lightly/utils/benchmarking/knn_classifier.py:13-170](), [benchmarks/imagenet/resnet50/knn_eval.py:42-106]()

### KNNClassifier Implementation

The `KNNClassifier` class wraps a pre-trained model and implements the kNN protocol as a PyTorch Lightning module. It operates in two phases during validation:

**Phase 1 (dataloader_idx=0):** Extracts and accumulates features from the training set.

```python
# Feature extraction and storage
def validation_step(self, batch, batch_idx: int, dataloader_idx: int) -> None:
    images, targets = batch[0], batch[1]
    features = self(images)  # Calls forward() with normalization
    
    if dataloader_idx == 0:
        # Store training features
        self.append_train_features(features=features, targets=targets)
```

**Phase 2 (dataloader_idx=1):** Concatenates training features and performs kNN classification on validation set.

```python
    else:
        if batch_idx == 0 and dataloader_idx == 1:
            # Concatenate accumulated features from all devices
            self.concat_train_features()
        
        # Perform kNN classification
        predicted_classes = knn_predict(
            feature=features,
            feature_bank=self._train_features_tensor,
            feature_labels=self._train_targets_tensor,
            num_classes=self.num_classes,
            knn_k=self.knn_k,
            knn_t=self.knn_t,
        )
```

The `forward()` method normalizes features and converts them to the specified dtype:

```python
def forward(self, images: Tensor) -> Tensor:
    features = self.model.forward(images).flatten(start_dim=1)
    if self.normalize:
        features = F.normalize(features, dim=1)
    features = features.to(self.feature_dtype)
    return features
```

**Sources:** [lightly/utils/benchmarking/knn_classifier.py:105-165]()

### Usage Pattern

The kNN evaluation is invoked from the main benchmark script:

```python
# From benchmarks/imagenet/resnet50/main.py
if not skip_knn_eval:
    eval_metrics["knn"] = knn_eval.knn_eval(
        model=model,
        num_classes=num_classes,
        train_dir=train_dir,
        val_dir=val_dir,
        log_dir=method_dir,
        batch_size_per_device=batch_size_per_device,
        num_workers=num_workers,
        accelerator=accelerator,
        devices=devices,
        strategy=strategy,
        knn_k=knn_k,  # Default: 200
        knn_t=knn_t,  # Default: 0.1 for ResNet, 0.07 for ViT
    )
```

**Sources:** [benchmarks/imagenet/resnet50/main.py:153-169](), [benchmarks/imagenet/vitb16/main.py:131-147]()

## Linear Evaluation Protocol

### Purpose and Settings

The linear evaluation protocol measures representation quality by training a linear classifier on top of frozen backbone features. This is the most widely used evaluation method in SSL research, following SimCLR [0] conventions.

**Key hyperparameters for ResNet50:**

| Parameter | Value | Description |
|-----------|-------|-------------|
| `max_epochs` | 90 | Training epochs |
| `optimizer` | SGD | Optimizer type |
| `lr` | 0.1 | Base learning rate (scaled by batch size) |
| `momentum` | 0.9 | SGD momentum |
| `weight_decay` | 0.0 | Weight decay (disabled for classifier head) |
| `lr_schedule` | Cosine | Learning rate schedule without warmup |
| `backbone` | Frozen | Backbone parameters frozen during training |

The linear classifier is a single fully-connected layer mapping from the backbone's feature dimension to the number of classes.

**Sources:** [benchmarks/imagenet/resnet50/linear_eval.py:17-45](), [benchmarks/imagenet/vitb16/linear_eval.py:74-88]()

### Data Augmentation

Linear evaluation uses simple augmentations to prevent overfitting:

**Training transforms:**
```python
train_transform = T.Compose([
    T.RandomResizedCrop(224),
    T.RandomHorizontalFlip(),
    T.ToTensor(),
    T.Normalize(mean=IMAGENET_NORMALIZE["mean"], std=IMAGENET_NORMALIZE["std"]),
])
```

**Validation transforms:**
```python
val_transform = T.Compose([
    T.Resize(256),
    T.CenterCrop(224),
    T.ToTensor(),
    T.Normalize(mean=IMAGENET_NORMALIZE["mean"], std=IMAGENET_NORMALIZE["std"]),
])
```

**Sources:** [benchmarks/imagenet/resnet50/linear_eval.py:48-75]()

### LinearClassifier Implementation

The `LinearClassifier` class (from `lightly.utils.benchmarking`) wraps the frozen backbone with a trainable linear layer:

```python
class LinearClassifier(LightningModule):
    def __init__(
        self,
        model: Module,
        batch_size_per_device: int,
        lr: float = 0.1,
        feature_dim: int = 2048,
        num_classes: int = 1000,
        topk: Tuple[int, ...] = (1, 5),
    ) -> None:
        # model: Pre-trained backbone (frozen during training)
        # feature_dim: Output dimension of backbone features
        # classification_head: Linear(feature_dim, num_classes)
```

The training step freezes the backbone and only updates the classifier:

```python
def training_step(self, batch: Tuple[Tensor, ...], batch_idx: int) -> Tensor:
    images, targets = batch[0], batch[1]
    # Extract features with frozen backbone
    features = self.forward(images)  # No gradients to backbone
    # Train only the classification head
    predictions = self.classification_head(features)
    loss = self.criterion(predictions, targets)
    return loss
```

**Sources:** [lightly/utils/benchmarking/linear_classifier.py]() (referenced by imports)

### Usage Pattern

```python
# From benchmarks/imagenet/resnet50/main.py
if not skip_linear_eval:
    eval_metrics["linear"] = linear_eval.linear_eval(
        model=model,
        num_classes=num_classes,
        train_dir=train_dir,
        val_dir=val_dir,
        log_dir=method_dir,
        batch_size_per_device=batch_size_per_device,
        num_workers=num_workers,
        accelerator=accelerator,
        devices=devices,
        strategy=strategy,
        precision=precision,
    )
```

**Sources:** [benchmarks/imagenet/resnet50/main.py:171-186]()

## Fine-tuning Evaluation Protocol

### Purpose and Settings

The fine-tuning evaluation protocol measures representation quality by training the entire model end-to-end. This protocol allows the backbone to adapt to the downstream task, typically achieving higher accuracy than linear evaluation.

**Key hyperparameters for ResNet50 (following SimCLR):**

| Parameter | Value | Description |
|-----------|-------|-------------|
| `max_epochs` | 30 | Training epochs |
| `optimizer` | SGD | Optimizer type |
| `lr` | 0.05 | Base learning rate |
| `momentum` | 0.9 | SGD momentum |
| `weight_decay` | 0.0 | Weight decay disabled |
| `lr_schedule` | Cosine | Learning rate schedule without warmup |
| `backbone` | Trainable | All model parameters trainable |

**Sources:** [benchmarks/imagenet/resnet50/finetune_eval.py:17-45]()

### FinetuneClassifier Implementation

The `FinetuneClassifier` is similar to `LinearClassifier` but with the backbone unfrozen:

```python
class FinetuneClassifier(LightningModule):
    def __init__(
        self,
        model: Module,
        batch_size_per_device: int,
        lr: float = 0.05,
        feature_dim: int = 2048,
        num_classes: int = 1000,
        topk: Tuple[int, ...] = (1, 5),
    ) -> None:
        # All parameters of model are trainable
        # classification_head: Linear(feature_dim, num_classes)
```

The training step updates both backbone and classifier:

```python
def training_step(self, batch: Tuple[Tensor, ...], batch_idx: int) -> Tensor:
    images, targets = batch[0], batch[1]
    # Extract features (gradients flow to backbone)
    features = self.forward(images)
    predictions = self.classification_head(features)
    loss = self.criterion(predictions, targets)
    return loss  # Updates both backbone and head
```

**Sources:** [benchmarks/imagenet/resnet50/finetune_eval.py:30-119]()

### Usage Pattern

```python
# From benchmarks/imagenet/resnet50/main.py
if not skip_finetune_eval:
    eval_metrics["finetune"] = finetune_eval.finetune_eval(
        model=model,
        num_classes=num_classes,
        train_dir=train_dir,
        val_dir=val_dir,
        log_dir=method_dir,
        batch_size_per_device=batch_size_per_device,
        num_workers=num_workers,
        accelerator=accelerator,
        devices=devices,
        strategy=strategy,
        precision=precision,
    )
```

**Sources:** [benchmarks/imagenet/resnet50/main.py:188-203]()

## Architecture-Specific Adaptations

### ViT-B/16 Evaluation Methods

Vision Transformer models require different evaluation settings compared to ResNet models. The ViT benchmark scripts support two evaluation methods controlled by the `--eval-method` flag:

| Method | Based On | Linear Eval Settings | Fine-tune Settings |
|--------|----------|---------------------|-------------------|
| `"mae"` | MAE paper | LARS optimizer, 90 epochs, extra BatchNorm | AdamW, 100 epochs, layer-wise LR decay, mixup/cutmix |
| `"simclr"` | SimCLR paper | SGD optimizer, 90 epochs, standard head | SGD, 30 epochs, standard training |

**Sources:** [benchmarks/imagenet/vitb16/main.py:44](), [benchmarks/imagenet/vitb16/linear_eval.py:74-88](), [benchmarks/imagenet/vitb16/finetune_eval.py:144-158]()

### MAE-Specific Linear Evaluation

The `LinearClassifierMAE` class adds a batch normalization layer before the classification head:

```python
class LinearClassifierMAE(LinearClassifier):
    def __init__(self, ...):
        super().__init__(...)
        # MAE adds extra batch norm before classification
        self.classification_head = Sequential(
            BatchNorm1d(feature_dim, affine=False, eps=1e-6),
            Linear(feature_dim, num_classes),
        )
    
    def configure_optimizers(self):
        # Uses LARS optimizer instead of SGD
        optimizer = LARS(
            parameters,
            lr=self.get_effective_lr(),
            momentum=0.9,
            weight_decay=0.0,
        )
        # 10 epoch warmup
        scheduler = CosineWarmupScheduler(
            optimizer=optimizer,
            warmup_epochs=10,
            max_epochs=90,
        )
```

**Sources:** [benchmarks/imagenet/vitb16/linear_eval.py:20-72]()

### MAE-Specific Fine-tuning Evaluation

The `FinetuneClassifierMAE` class implements sophisticated training strategies from the MAE paper:

**Stochastic depth (path dropout):**
```python
class FinetuneClassifierMAE(FinetuneClassifier):
    def __init__(self, ...):
        super().__init__(...)
        # Add path dropout to transformer blocks
        add_stochastic_depth_to_blocks(self.model, prob=0.1)
        # Add mixup and cutmix augmentation
        self.mixup = Mixup(
            mixup_alpha=0.8,
            cutmix_alpha=1.0,
            label_smoothing=0.1,
            num_classes=num_classes,
        )
```

**Layer-wise learning rate decay:**
```python
    def configure_optimizers(self):
        layerwise_lr_decay = 0.65
        # Group parameters by layer depth
        for name, module in get_named_leaf_modules(self.model).items():
            if "encoder_layer_" in name:
                layer_index = int(name.split("encoder_layer_")[1].split(".")[0])
                # LR increases from first layer (index 0) to last layer (index 11)
                group_lr = lr * (layerwise_lr_decay ** (11 - layer_index))
            else:
                group_lr = lr
```

**AdamW optimizer with weight decay:**
```python
        optimizer = AdamW(
            param_groups,
            betas=(0.9, 0.999),
        )
        # 5 epoch warmup for 100 epoch training
        scheduler = CosineWarmupScheduler(
            optimizer=optimizer,
            warmup_epochs=5,
            max_epochs=100,
        )
```

**Sources:** [benchmarks/imagenet/vitb16/finetune_eval.py:28-142]()

### Transform Differences

MAE fine-tuning uses more aggressive data augmentation from the TIMM library:

```python
if eval_method == "mae":
    train_transform = create_transform(
        input_size=224,
        is_training=True,
        auto_augment="rand-m9-mstd0.5-inc1",  # RandAugment
        interpolation="bicubic",
        re_prob=0.25,  # Random erasing
        re_mode="pixel",
        re_count=1,
        mean=IMAGENET_NORMALIZE["mean"],
        std=IMAGENET_NORMALIZE["std"],
    )
```

**Sources:** [benchmarks/imagenet/vitb16/finetune_eval.py:170-180]()

## Evaluation Results Format

### Metrics Dictionary Structure

All evaluation functions return a dictionary with top-1 and top-5 accuracy:

```python
metrics_dict: Dict[str, float] = {
    "val_top1": 0.7234,  # Top-1 accuracy
    "val_top5": 0.9012,  # Top-5 accuracy
}
```

The main script collects metrics from all protocols:

```python
eval_metrics: Dict[str, Dict[str, float]] = {
    "knn": {
        "val_top1": 0.6523,
        "val_top5": 0.8734,
    },
    "linear": {
        "val_top1": 0.7234,
        "val_top5": 0.9012,
    },
    "finetune": {
        "val_top1": 0.7856,
        "val_top5": 0.9345,
    },
}
```

**Sources:** [benchmarks/imagenet/resnet50/main.py:152-207]()

### Markdown Results Table

The main script formats results as a markdown table:

```python
def eval_metrics_to_markdown(metrics: Dict[str, Dict[str, float]]) -> str:
    """Formats evaluation metrics as a markdown table."""
    # Creates table with columns: Eval Name | Metric Name | Value
    # Example output:
    # | knn     | val_top1 | 65.23 |
    # | knn     | val_top5 | 87.34 |
    # | linear  | val_top1 | 72.34 |
    # | linear  | val_top5 | 90.12 |
    # | finetune| val_top1 | 78.56 |
    # | finetune| val_top5 | 93.45 |
```

**Sources:** [benchmarks/imagenet/resnet50/main.py:288-318](), [benchmarks/imagenet/vitb16/main.py:269-298]()

## Execution Flow

```mermaid
graph TB
    subgraph "Command Line Arguments"
        Args["ArgumentParser<br/>--methods<br/>--skip-knn-eval<br/>--skip-linear-eval<br/>--skip-finetune-eval<br/>--knn-k, --knn-t"]
    end
    
    subgraph "Main Loop"
        MethodLoop["For each method in methods:<br/>barlowtwins, byol, dino, etc."]
        CreateModel["Instantiate Model<br/>METHODS[method]['model']"]
        CompileCheck["Optional:<br/>torch.compile(model)"]
    end
    
    subgraph "Pretraining (Optional)"
        CheckEpochs["epochs > 0?"]
        PretrainFunc["pretrain()<br/>Train with SSL objective"]
        LoadCkpt["Load from --ckpt-path"]
    end
    
    subgraph "Evaluation Protocols"
        KNN["if not skip_knn_eval:<br/>knn_eval()"]
        Linear["if not skip_linear_eval:<br/>linear_eval()"]
        Finetune["if not skip_finetune_eval:<br/>finetune_eval()"]
    end
    
    subgraph "Results"
        CollectMetrics["eval_metrics: Dict[str, Dict[str, float]]"]
        PrintTable["eval_metrics_to_markdown()<br/>Print formatted table"]
    end
    
    Args --> MethodLoop
    MethodLoop --> CreateModel
    CreateModel --> CompileCheck
    CompileCheck --> CheckEpochs
    
    CheckEpochs -->|Yes| PretrainFunc
    CheckEpochs -->|No| LoadCkpt
    
    PretrainFunc --> KNN
    LoadCkpt --> KNN
    
    KNN --> Linear
    Linear --> Finetune
    
    KNN --> CollectMetrics
    Linear --> CollectMetrics
    Finetune --> CollectMetrics
    
    CollectMetrics --> PrintTable
```

**Sources:** [benchmarks/imagenet/resnet50/main.py:88-208](), [benchmarks/imagenet/vitb16/main.py:63-188]()

## PyTorch Lightning Integration

All evaluation protocols use PyTorch Lightning for training orchestration:

```python
# Common trainer configuration
trainer = Trainer(
    max_epochs=epochs,
    accelerator=accelerator,
    devices=devices,
    callbacks=[
        LearningRateMonitor(),
        DeviceStatsMonitor(),
        metric_callback,  # Collects metrics
    ],
    logger=TensorBoardLogger(save_dir=str(log_dir), name="protocol_name"),
    precision=precision,
    strategy=strategy,
    num_sanity_val_steps=0,  # Saves shared memory
)
```

The `MetricCallback` accumulates validation metrics across epochs:

```python
# After training
for metric in ["val_top1", "val_top5"]:
    max_value = max(metric_callback.val_metrics[metric])
    metrics_dict[metric] = max_value
```

**Sources:** [benchmarks/imagenet/resnet50/linear_eval.py:85-111](), [benchmarks/imagenet/resnet50/finetune_eval.py:85-111]()

## Command-Line Usage

The benchmark scripts provide flags to control which evaluations run:

```bash
# Run all evaluation protocols
python benchmarks/imagenet/resnet50/main.py \
    --train-dir /datasets/imagenet/train \
    --val-dir /datasets/imagenet/val \
    --methods simclr mocov2 byol \
    --epochs 100 \
    --batch-size-per-device 128 \
    --devices 4 \
    --accelerator gpu

# Skip specific protocols
python benchmarks/imagenet/resnet50/main.py \
    --skip-knn-eval \
    --skip-finetune-eval \
    --methods simclr

# Only evaluate from checkpoint (no pretraining)
python benchmarks/imagenet/resnet50/main.py \
    --epochs 0 \
    --ckpt-path ./checkpoint.ckpt \
    --methods simclr

# Customize kNN parameters
python benchmarks/imagenet/resnet50/main.py \
    --knn-k 100 \
    --knn-t 0.2
```

**Sources:** [benchmarks/imagenet/resnet50/main.py:48-69](), [benchmarks/imagenet/vitb16/main.py:31-53]()

## Evaluation Protocol Comparison

| Protocol | Training Required | Computation Cost | Typical Accuracy | Use Case |
|----------|------------------|------------------|------------------|----------|
| **kNN** | No | Low (single pass) | Lowest | Quick quality check, no GPU memory for training |
| **Linear** | Yes (90 epochs) | Medium (head only) | Medium | Standard benchmark, most comparable across papers |
| **Fine-tune** | Yes (30-100 epochs) | High (full model) | Highest | Maximum downstream performance, task adaptation |

**Linear evaluation is the standard protocol** for comparing SSL methods in research papers because it:
- Isolates the quality of learned representations from task-specific adaptations
- Provides reproducible results with standardized hyperparameters
- Balances computational cost with meaningful performance measurement

**Sources:** [benchmarks/imagenet/resnet50/main.py:1-323](), [benchmarks/imagenet/vitb16/main.py:1-304]()

---

# Page: Tutorials and Examples

# Tutorials and Examples

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/source/getting_started/advanced.rst](docs/source/getting_started/advanced.rst)
- [docs/source/getting_started/command_line_tool.rst](docs/source/getting_started/command_line_tool.rst)
- [docs/source/getting_started/images/lightly_overview.png](docs/source/getting_started/images/lightly_overview.png)
- [docs/source/getting_started/install.rst](docs/source/getting_started/install.rst)
- [docs/source/getting_started/lightly_at_a_glance.rst](docs/source/getting_started/lightly_at_a_glance.rst)
- [docs/source/getting_started/main_concepts.rst](docs/source/getting_started/main_concepts.rst)
- [docs/source/index.rst](docs/source/index.rst)
- [docs/source/lightly.models.utils.rst](docs/source/lightly.models.utils.rst)
- [docs/source/tutorials/structure_your_input.rst](docs/source/tutorials/structure_your_input.rst)
- [docs/source/tutorials_source/package/Base-RCNN-FPN.yaml](docs/source/tutorials_source/package/Base-RCNN-FPN.yaml)
- [docs/source/tutorials_source/package/tutorial_custom_augmentations.py](docs/source/tutorials_source/package/tutorial_custom_augmentations.py)
- [docs/source/tutorials_source/package/tutorial_moco_memory_bank.py](docs/source/tutorials_source/package/tutorial_moco_memory_bank.py)
- [docs/source/tutorials_source/package/tutorial_pretrain_detectron2.py](docs/source/tutorials_source/package/tutorial_pretrain_detectron2.py)
- [docs/source/tutorials_source/package/tutorial_simclr_clothing.py](docs/source/tutorials_source/package/tutorial_simclr_clothing.py)
- [docs/source/tutorials_source/package/tutorial_simsiam_esa.py](docs/source/tutorials_source/package/tutorial_simsiam_esa.py)

</details>



This page provides a comprehensive guide to the hands-on tutorials and examples available in the Lightly framework. These tutorials demonstrate complete workflows for training self-supervised learning models, from basic data loading to advanced custom augmentations and integration with external frameworks like Detectron2.

For API reference documentation, see the Python API sections ([2](#2), [3](#3), [4](#4), [5](#5)). For command-line usage, see [Command-Line Interface](#4).

## Tutorial Overview

The tutorials are organized in order of increasing complexity, allowing users to build understanding progressively:

| Tutorial | Topic | Key Concepts | Dataset |
|----------|-------|--------------|---------|
| Tutorial 1 | Structure Your Input | Dataset creation, data loading, transforms | Generic images/videos |
| Tutorial 2 | Train MoCo on CIFAR-10 | Memory banks, momentum encoders, linear evaluation | CIFAR-10 |
| Tutorial 3 | Train SimCLR on Clothing | Contrastive learning, nearest neighbors | Clothing dataset |
| Tutorial 4 | Train SimSiam on Satellite Images | Siamese networks, embeddings visualization | Sentinel-2 satellite |
| Tutorial 5 | Custom Augmentations | Domain-specific transforms, 16-bit images | Medical X-rays |
| Tutorial 6 | Detectron2 Integration | Transfer learning, object detection | Freiburg Groceries |

**Sources:** [docs/source/index.rst:82-94](), [docs/source/tutorials/structure_your_input.rst:1-250]()

---

## Tutorial 1: Structure Your Input

This tutorial covers the fundamental data handling capabilities of the framework, focusing on creating datasets and dataloaders compatible with various data sources.

### Supported Data Sources and Formats

```mermaid
graph TB
    subgraph "Data Sources"
        IMG["Local Images<br/>.jpg, .png, .tiff"]
        VID["Local Videos<br/>.mov, .mp4, .avi"]
        TORCH["Torchvision Datasets<br/>CIFAR10, ImageNet, etc."]
        HF["Hugging Face Datasets<br/>via datasets library"]
    end
    
    subgraph "Lightly Data Layer"
        LD["LightlyDataset"]
        VD["VideoDataset"]
        SUBSET["LightlySubset"]
    end
    
    subgraph "PyTorch Integration"
        LOADER["torch.utils.data.DataLoader"]
    end
    
    IMG --> LD
    VID --> VD
    TORCH --> LD
    HF --> LD
    
    LD --> SUBSET
    VD --> SUBSET
    
    LD --> LOADER
    VD --> LOADER
    SUBSET --> LOADER
```

### Basic Dataset Creation

The `LightlyDataset` class provides a unified interface for image and video data:

```python
# Unlabeled images in a single directory
from lightly.data import LightlyDataset
from lightly.transforms import SimCLRTransform

transform = SimCLRTransform()
dataset = LightlyDataset(input_dir='image_dir/', transform=transform)
```

**Key class:** `lightly.data.LightlyDataset` [lightly/data/dataset.py]()

For labeled data with subdirectories per class:
```python
# Labeled images: parent_dir/class_name/image.jpg
labeled_dataset = LightlyDataset(input_dir='labeled_image_dir/', transform=transform)
```

### Video Dataset Support

Videos are supported natively without frame extraction:

```python
# Works with .mov, .mp4, .avi files
video_dataset = LightlyDataset(input_dir='video_dir/', transform=transform)
```

**Note:** Video support requires `pip install "lightly[video]"` to install PyAV dependencies.

**Sources:** [docs/source/tutorials/structure_your_input.rst:17-129](), [lightly/data/__init__.py]()

### Transform Pipeline Integration

```mermaid
graph LR
    IMG["Input Image"]
    T1["SimCLRTransform"]
    V0["View 0"]
    V1["View 1"]
    COLLATE["MultiViewCollate"]
    BATCH["Batch"]
    
    IMG --> T1
    T1 --> V0
    T1 --> V1
    V0 --> COLLATE
    V1 --> COLLATE
    COLLATE --> BATCH
```

The framework supports three transform approaches:

1. **Pre-defined transforms** from `lightly.transforms` (SimCLR, DINO, MAE, etc.)
2. **Torchvision transforms** for standard augmentations
3. **Custom transforms** including Albumentations or custom implementations

Example with multiple transform libraries:

```python
import albumentations as A
import torchvision.transforms as T
from lightly.transforms import SimCLRTransform

# Torchvision
tv_transform = T.Compose([T.RandomHorizontalFlip(), T.ToTensor()])

# Albumentations
alb_transform = A.Compose([
    A.CenterCrop(height=128, width=128),
    A.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225))
])

# Lightly
lightly_transform = SimCLRTransform()
```

**Sources:** [docs/source/tutorials/structure_your_input.rst:180-227](), [lightly/transforms/__init__.py]()

---

## Tutorial 2: Train MoCo on CIFAR-10

This tutorial demonstrates training a Momentum Contrast (MoCo) model with a memory bank on CIFAR-10, followed by linear evaluation to assess embedding quality.

### MoCo Architecture Components

```mermaid
graph TB
    subgraph "Query Path"
        Q_IMG["Input Image x_q"]
        Q_BACK["Query Backbone<br/>ResNetGenerator"]
        Q_HEAD["Query Projection Head<br/>MoCoProjectionHead"]
        Q_EMB["Query Embedding q"]
    end
    
    subgraph "Key Path (Momentum)"
        K_IMG["Input Image x_k<br/>(batch shuffled)"]
        K_BACK["Momentum Backbone<br/>(EMA updated)"]
        K_HEAD["Momentum Projection Head<br/>(EMA updated)"]
        K_EMB["Key Embedding k"]
    end
    
    subgraph "Loss Computation"
        BANK["Memory Bank<br/>4096 x 128"]
        LOSS["NTXentLoss<br/>temperature=0.1"]
    end
    
    Q_IMG --> Q_BACK
    Q_BACK --> Q_HEAD
    Q_HEAD --> Q_EMB
    
    K_IMG --> K_BACK
    K_BACK --> K_HEAD
    K_HEAD --> K_EMB
    
    Q_EMB --> LOSS
    K_EMB --> LOSS
    BANK --> LOSS
```

### Key Implementation Details

**MoCo Model Structure:**
- **Backbone:** `ResNetGenerator("resnet-18", 1, num_splits=8)` with split batch normalization
- **Projection head:** `MoCoProjectionHead(512, 512, 128)` 
- **Momentum encoder:** Exponential moving average (EMA) copy of backbone and head
- **Memory bank:** 4096 negative samples of dimension 128

**Code reference:** [docs/source/tutorials_source/package/tutorial_moco_memory_bank.py:221-283]()

```python
class MocoModel(pl.LightningModule):
    def __init__(self):
        super().__init__()
        # Create backbone and head
        resnet = ResNetGenerator("resnet-18", 1, num_splits=8)
        self.backbone = nn.Sequential(*list(resnet.children())[:-1], nn.AdaptiveAvgPool2d(1))
        self.projection_head = MoCoProjectionHead(512, 512, 128)
        
        # Momentum copies
        self.backbone_momentum = copy.deepcopy(self.backbone)
        self.projection_head_momentum = copy.deepcopy(self.projection_head)
        deactivate_requires_grad(self.backbone_momentum)
        deactivate_requires_grad(self.projection_head_momentum)
        
        # Loss with memory bank
        self.criterion = NTXentLoss(temperature=0.1, memory_bank_size=(4096, 128))
```

**Key functions used:**
- `update_momentum()` - Updates momentum encoder weights [lightly/models/utils/__init__.py]()
- `batch_shuffle()` / `batch_unshuffle()` - Prevents information leakage through batch norm [lightly/models/utils/__init__.py]()
- `deactivate_requires_grad()` - Freezes momentum encoder parameters [lightly/models/utils/__init__.py]()

### Training and Evaluation Workflow

```mermaid
graph TD
    DATA["CIFAR-10 Training Data<br/>with MoCoV2Transform"]
    TRAIN["Self-Supervised Training<br/>MocoModel<br/>100 epochs"]
    FREEZE["Extract Frozen Backbone"]
    CLASSIFIER["Linear Classifier<br/>512 → 10 classes<br/>frozen backbone"]
    EVAL["Linear Evaluation<br/>on test set"]
    
    DATA --> TRAIN
    TRAIN --> FREEZE
    FREEZE --> CLASSIFIER
    CLASSIFIER --> EVAL
```

**Linear classifier implementation:** [docs/source/tutorials_source/package/tutorial_moco_memory_bank.py:292-356]()

The linear evaluation protocol trains only a linear layer on top of frozen features:
- Backbone is frozen using `deactivate_requires_grad()`
- Single linear layer: `nn.Linear(512, 10)` for 10 CIFAR-10 classes
- Trained with cross-entropy loss for 100 epochs
- Achieves ~73% test accuracy after 100 epochs, ~80% after 200 epochs

**Sources:** [docs/source/tutorials_source/package/tutorial_moco_memory_bank.py:1-404](), [docs/source/getting_started/advanced.rst:282-297]()

---

## Tutorial 3: Train SimCLR on Clothing

This tutorial trains a SimCLR model on the Freiburg Clothing dataset and demonstrates how to visualize embeddings through nearest neighbor analysis.

### SimCLR Training Pipeline

```mermaid
graph LR
    IMG["Input Image"]
    TRANS["SimCLRTransform<br/>vf_prob=0.5<br/>rr_prob=0.5"]
    V0["Augmented View 0"]
    V1["Augmented View 1"]
    BACK["ResNet-18 Backbone"]
    H0["Features h0"]
    H1["Features h1"]
    HEAD["SimCLRProjectionHead<br/>512 → 512 → 128"]
    Z0["Projection z0"]
    Z1["Projection z1"]
    LOSS["NTXentLoss<br/>temperature=0.5"]
    
    IMG --> TRANS
    TRANS --> V0
    TRANS --> V1
    V0 --> BACK
    V1 --> BACK
    BACK --> H0
    BACK --> H1
    H0 --> HEAD
    H1 --> HEAD
    HEAD --> Z0
    HEAD --> Z1
    Z0 --> LOSS
    Z1 --> LOSS
```

### Model Implementation

**Complete SimCLR model structure:** [docs/source/tutorials_source/package/tutorial_simclr_clothing.py:139-171]()

```python
class SimCLRModel(pl.LightningModule):
    def __init__(self):
        super().__init__()
        # ResNet backbone without classification head
        resnet = torchvision.models.resnet18()
        self.backbone = nn.Sequential(*list(resnet.children())[:-1])
        
        hidden_dim = resnet.fc.in_features  # 512 for ResNet-18
        self.projection_head = SimCLRProjectionHead(hidden_dim, hidden_dim, 128)
        self.criterion = NTXentLoss()
    
    def training_step(self, batch, batch_idx):
        (x0, x1), _, _ = batch
        z0 = self.forward(x0)
        z1 = self.forward(x1)
        loss = self.criterion(z0, z1)
        return loss
```

### Dataset-Specific Augmentations

For clothing images taken from above, custom augmentations include:
- **Vertical flip:** `vf_prob=0.5` (clothing can be upside down)
- **Random rotation:** `rr_prob=0.5` by 90 degrees (orientation invariance)
- **Color jittering:** Standard to learn structure over color

**Augmentation configuration:** [docs/source/tutorials_source/package/tutorial_simclr_clothing.py:91]()

### Embedding Visualization and Analysis

```mermaid
graph TD
    MODEL["Trained SimCLR Model"]
    TEST["Test Dataset<br/>no augmentation"]
    BACKBONE["Extract Features<br/>via backbone"]
    EMB["Embeddings<br/>normalized"]
    KNN["K-Nearest Neighbors<br/>sklearn NearestNeighbors"]
    VIZ["Visualize Results"]
    
    MODEL --> BACKBONE
    TEST --> BACKBONE
    BACKBONE --> EMB
    EMB --> KNN
    KNN --> VIZ
```

**Embedding generation function:** [docs/source/tutorials_source/package/tutorial_simclr_clothing.py:188-204]()

```python
def generate_embeddings(model, dataloader):
    embeddings = []
    filenames = []
    with torch.no_grad():
        for img, _, fnames in dataloader:
            img = img.to(model.device)
            emb = model.backbone(img).flatten(start_dim=1)
            embeddings.append(emb)
            filenames.extend(fnames)
    
    embeddings = torch.cat(embeddings, 0)
    embeddings = normalize(embeddings)  # L2 normalization
    return embeddings, filenames
```

**Color invariance experiment:** The tutorial demonstrates training with and without color augmentations to show how this affects the learned representations ([tutorial_simclr_clothing.py:259-283]()).

**Sources:** [docs/source/tutorials_source/package/tutorial_simclr_clothing.py:1-321](), [lightly/models/modules/heads.py]()

---

## Tutorial 4: Train SimSiam on Satellite Images

This tutorial demonstrates SimSiam training on ESA Sentinel-2 satellite imagery, showcasing domain-specific considerations and embedding quality assessment through collapse detection.

### SimSiam Architecture

```mermaid
graph TB
    IMG1["Augmented View x0"]
    IMG2["Augmented View x1"]
    
    subgraph "Shared Backbone"
        BACK["ResNet-18<br/>pretrained"]
    end
    
    subgraph "Projection Branch"
        PROJ["SimSiamProjectionHead<br/>512 → 512 → 512"]
    end
    
    subgraph "Prediction Branch"
        PRED["SimSiamPredictionHead<br/>512 → 128 → 512"]
    end
    
    IMG1 --> BACK
    IMG2 --> BACK
    BACK --> |"Features f"| PROJ
    PROJ --> |"Projection z"| PRED
    PRED --> |"Prediction p"| LOSS["NegativeCosineSimilarity<br/>symmetric"]
    PROJ --> |"Projection z<br/>(stop gradient)"| LOSS
```

**Key architectural difference from SimCLR:** SimSiam uses a prediction head and stop-gradient operation instead of a momentum encoder.

### Domain-Specific Augmentations for Satellite Images

**Augmentation strategy:** [docs/source/tutorials_source/package/tutorial_simsiam_esa.py:92-108]()

```python
transform = SimCLRTransform(
    input_size=256,
    hf_prob=0.5,      # horizontal flip
    vf_prob=0.5,      # vertical flip (valid for satellite)
    rr_prob=0.5,      # random rotation by 90° (orientation invariant)
    min_scale=0.5,    # slight random crop (same altitude)
    cj_prob=0.2,      # weak color jitter
    cj_bright=0.1,
    cj_contrast=0.1,
    cj_hue=0.1,
    cj_sat=0.1,
)
```

**Rationale:**
- Satellite images have no canonical "up" direction → vertical flip and rotation are appropriate
- All images from same altitude → minimal scale variation
- Water color can vary slightly → weak color augmentation

### Collapse Detection

SimSiam models can suffer from representation collapse where all outputs become similar. The tutorial implements collapse detection:

**Collapse monitoring:** [docs/source/tutorials_source/package/tutorial_simsiam_esa.py:235-256]()

```python
# Inside training loop
output = p0.detach()
output = torch.nn.functional.normalize(output, dim=1)  # L2 normalize
output_std = torch.std(output, 0)  # Per-dimension std
output_std = output_std.mean()

# Collapse level: should be close to 1/sqrt(dim)
# For 512 dimensions: expected ~0.044
collapse_level = max(0.0, 1 - math.sqrt(out_dim) * avg_output_std)
```

**Expected values:**
- No collapse: `std ≈ 1/sqrt(dim)` (e.g., ~0.044 for 512-dim)
- Collapse: `std → 0`

### Training Configuration

**Model parameters:** [docs/source/tutorials_source/package/tutorial_simsiam_esa.py:155-178]()
- Backbone: ResNet-18 (pretrained for faster training)
- Projection hidden: 512, output: 512
- Prediction hidden: 128 (bottleneck architecture)
- Learning rate: `0.05 * batch_size / 256` (scaled by batch size)
- Optimizer: SGD with momentum=0.9, weight_decay=5e-4

**Sources:** [docs/source/tutorials_source/package/tutorial_simsiam_esa.py:1-449](), [lightly/models/modules/heads.py]()

---

## Tutorial 5: Custom Augmentations for X-ray Images

This tutorial addresses challenges with non-standard image formats (16-bit TIFF) and domain-specific augmentations for medical imaging.

### Custom Transform Pipeline

```mermaid
graph LR
    TIFF["16-bit TIFF Image<br/>numpy array"]
    HIST["HistogramNormalize<br/>custom transform"]
    IMG8["8-bit PIL Image"]
    GRAY["Grayscale → RGB<br/>repeat channels"]
    CROP["RandomResizedCrop"]
    FLIP["Random Flips"]
    BLUR["GaussianBlur"]
    TENSOR["ToTensor"]
    NOISE["GaussianNoise<br/>custom transform"]
    FINAL["Augmented Tensor"]
    
    TIFF --> HIST
    HIST --> IMG8
    IMG8 --> GRAY
    GRAY --> CROP
    CROP --> FLIP
    FLIP --> BLUR
    BLUR --> TENSOR
    TENSOR --> NOISE
    NOISE --> FINAL
```

### Custom Augmentation Implementations

**Histogram Normalization:** [docs/source/tutorials_source/package/tutorial_custom_augmentations.py:100-122]()

Converts 16-bit depth to 8-bit using histogram equalization:

```python
class HistogramNormalize:
    def __init__(self, number_bins: int = 256):
        self.number_bins = number_bins
    
    def __call__(self, image: np.array) -> Image:
        # Get histogram and cumulative distribution
        image_histogram, bins = np.histogram(image.flatten(), self.number_bins, density=True)
        cdf = image_histogram.cumsum()
        cdf = 255 * cdf / cdf[-1]  # Normalize to [0, 255]
        
        # Linear interpolation for new pixel values
        image_equalized = np.interp(image.flatten(), bins[:-1], cdf)
        return Image.fromarray(image_equalized.reshape(image.shape))
```

**Gaussian Noise:** [docs/source/tutorials_source/package/tutorial_custom_augmentations.py:130-144]()

Adds signal-dependent noise (SNR-based):

```python
class GaussianNoise:
    def __call__(self, sample: torch.Tensor) -> torch.Tensor:
        mu = sample.mean()
        snr = np.random.randint(low=4, high=8)
        sigma = mu / snr
        noise = torch.normal(torch.zeros(sample.shape), sigma)
        return sample + noise
```

### Dataset Integration with Custom Loader

**Custom image loader for 16-bit TIFF:** [docs/source/tutorials_source/package/tutorial_custom_augmentations.py:215-224]()

```python
def tiff_loader(f):
    """Loads a 16-bit tiff image and returns it as a numpy array."""
    with open(f, "rb") as f:
        image = Image.open(f)
        return np.array(image)

# Override default loader
dataset_train = LightlyDataset(input_dir=path_to_data, transform=transform)
dataset_train.dataset.loader = tiff_loader
```

**Why this is needed:** Default torchvision loader converts images to 8-bit RGB, which would clip all pixel values above 255 in 16-bit images.

### Complete Transform Composition

**Full augmentation pipeline:** [docs/source/tutorials_source/package/tutorial_custom_augmentations.py:159-174]()

```python
view_transform = torchvision.transforms.Compose([
    HistogramNormalize(),                          # 16-bit → 8-bit
    torchvision.transforms.Grayscale(num_output_channels=3),  # 1 → 3 channels
    torchvision.transforms.RandomResizedCrop(size=128, scale=(0.2, 1.0)),
    torchvision.transforms.RandomHorizontalFlip(p=0.5),
    torchvision.transforms.RandomVerticalFlip(p=0.5),
    torchvision.transforms.GaussianBlur(21),
    torchvision.transforms.ToTensor(),
    GaussianNoise(),                               # Applied after ToTensor
])
```

**Sources:** [docs/source/tutorials_source/package/tutorial_custom_augmentations.py:1-436](), [lightly/transforms/multi_view_transform.py]()

---

## Tutorial 6: Pre-train Detectron2 Backbone

This tutorial demonstrates integrating Lightly with Facebook's Detectron2 framework for object detection, showing how to extract, pre-train, and save a Detectron2-compatible ResNet50 backbone.

### Integration Architecture

```mermaid
graph TB
    subgraph "Detectron2 Model"
        CFG["Config File<br/>Base-RCNN-FPN.yaml"]
        DMODEL["DetectionCheckpointer<br/>build_model()"]
        D_BACK["Detectron2 ResNet50<br/>bottom_up"]
        D_OUT["Output Dict<br/>res1...res5"]
    end
    
    subgraph "Lightly Adaptation"
        SELECT["SelectStage('res5')<br/>custom module"]
        POOL["AdaptiveAvgPool2d(1)<br/>→ shape: bsz x 2048"]
        HEAD["SimCLRProjectionHead<br/>2048 → 2048 → 128"]
    end
    
    subgraph "Training"
        DATA["Freiburg Groceries<br/>SimCLRTransform"]
        LOSS["NTXentLoss"]
        OPT["Adam Optimizer"]
    end
    
    subgraph "Export"
        SAVE["DetectionCheckpointer<br/>save('my_model.pth')"]
    end
    
    CFG --> DMODEL
    DMODEL --> D_BACK
    D_BACK --> D_OUT
    D_OUT --> SELECT
    SELECT --> POOL
    POOL --> HEAD
    
    DATA --> POOL
    HEAD --> LOSS
    LOSS --> OPT
    OPT --> POOL
    
    D_BACK --> SAVE
```

### Extracting Detectron2 Backbone

**Key challenge:** Detectron2 ResNet outputs a dictionary with keys `["res2", "res3", "res4", "res5"]` instead of a single tensor.

**Solution - Custom stage selector:** [docs/source/tutorials_source/package/tutorial_pretrain_detectron2.py:113-122]()

```python
class SelectStage(torch.nn.Module):
    """Selects features from a given stage."""
    def __init__(self, stage: str = "res5"):
        super().__init__()
        self.stage = stage
    
    def forward(self, x):
        return x[self.stage]  # Extract res5 output
```

**Backbone construction:** [docs/source/tutorials_source/package/tutorial_pretrain_detectron2.py:143-149]()

```python
detmodel = modeling.build_model(cfg)

simclr_backbone = torch.nn.Sequential(
    detmodel.backbone.bottom_up,  # Detectron2 ResNet
    SelectStage("res5"),           # Extract res5 features (bsz x 2048 x 4 x 4)
    torch.nn.AdaptiveAvgPool2d(1), # Pool to (bsz x 2048)
)
```

### Configuration Adjustments

**Required config modifications:** [docs/source/tutorials_source/package/tutorial_pretrain_detectron2.py:126-136]()

```python
cfg = config.get_cfg()
cfg.merge_from_file("Base-RCNN-FPN.yaml")

cfg.MODEL.DEVICE = "cuda"          # Set device
cfg.MODEL.WEIGHTS = ""              # Random initialization (no pre-trained weights)
cfg.INPUT.FORMAT = "RGB"            # PyTorch uses RGB, Detectron2 default is BGR
```

**Important:** The `INPUT.FORMAT = "RGB"` is critical because:
- Lightly/PyTorch transforms expect RGB
- Detectron2 defaults to BGR
- Training with wrong format causes poor performance

### Self-Supervised Pre-training

**Training loop:** [docs/source/tutorials_source/package/tutorial_pretrain_detectron2.py:204-224]()

Simple contrastive training with SimCLR:
- Uses Adam optimizer (lr=1e-4) for stability
- Projects features through `SimCLRProjectionHead(2048, 2048, 128)`
- Optimizes `NTXentLoss` on projected features
- Trains for 5 epochs (demonstration only; production would use more)

### Saving for Detectron2

**Checkpoint export:** [docs/source/tutorials_source/package/tutorial_pretrain_detectron2.py:232-240]()

```python
# Extract pre-trained backbone from sequential wrapper
detmodel.backbone.bottom_up = simclr_backbone[0]

# Save in Detectron2 format
checkpointer = DetectionCheckpointer(detmodel, save_dir="./")
checkpointer.save("my_model")
```

### Using Pre-trained Checkpoint

**Fine-tuning command:** [docs/source/tutorials_source/package/tutorial_pretrain_detectron2.py:253-259]()

```bash
python train_net.py \
    --config-file configs/COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_1x.yaml \
    MODEL.WEIGHTS path/to/my_model.pth \
    MODEL.PIXEL_MEAN 123.675,116.280,103.530 \
    MODEL.PIXEL_STD 58.395,57.120,57.375 \
    INPUT.FORMAT RGB
```

**Normalization values:** These correspond to ImageNet statistics scaled to [0, 255] range because SimCLR pre-training used ImageNet normalization.

**Sources:** [docs/source/tutorials_source/package/tutorial_pretrain_detectron2.py:1-290](), [detectron2/config/__init__.py]()

---

## Model Examples Reference

Beyond the tutorials, the framework provides ready-to-use implementations of major SSL methods. These serve as reference implementations and starting points for custom models.

### Available Model Implementations

| Model | Paper | Key Features | Primary Components |
|-------|-------|--------------|-------------------|
| SimCLR | [arXiv:2002.05709](https://arxiv.org/abs/2002.05709) | Simple contrastive learning | `SimCLRProjectionHead`, `NTXentLoss` |
| MoCo | [arXiv:1911.05722](https://arxiv.org/abs/1911.05722) | Momentum encoder + memory bank | `MoCoProjectionHead`, momentum updates |
| BYOL | [arXiv:2006.07733](https://arxiv.org/abs/2006.07733) | No negative samples | `BYOLProjectionHead`, `BYOLPredictionHead` |
| SimSiam | [arXiv:2011.10566](https://arxiv.org/abs/2011.10566) | Stop-gradient, no momentum | `SimSiamProjectionHead`, `SimSiamPredictionHead` |
| DINO | [arXiv:2104.14294](https://arxiv.org/abs/2104.14294) | Self-distillation with ViT | `DINOProjectionHead`, multi-crop |
| MAE | [arXiv:2111.06377](https://arxiv.org/abs/2111.06377) | Masked autoencoding | `MaskedVisionTransformerTIMM`, masking utils |
| MSN/PMSN | [arXiv:2204.07141](https://arxiv.org/abs/2204.07141) | Masked Siamese Networks | `MSNProjectionHead`, prototype learning |
| SwaV | [arXiv:2006.09882](https://arxiv.org/abs/2006.09882) | Swapped assignments | `SwaVProjectionHead`, `SwaVPrototypes` |

**Model implementations location:** [lightly/models/]()

**Loss functions location:** [lightly/loss/]()

**Transform implementations:** [lightly/transforms/]()

### Example Usage Pattern

All models follow a similar pattern:

```mermaid
graph LR
    BACK["Backbone<br/>ResNet or ViT"]
    HEAD["Method-Specific Head<br/>Projection/Prediction"]
    TRANS["Method-Specific Transform<br/>View generation"]
    LOSS["Method-Specific Loss<br/>Contrastive/Distillation"]
    
    TRANS --> |"Augmented views"| BACK
    BACK --> |"Features"| HEAD
    HEAD --> |"Embeddings"| LOSS
```

Each model example typically includes:
1. Complete model architecture definition
2. Transform pipeline configuration
3. Loss function setup
4. Training loop (PyTorch or Lightning)
5. Embedding generation code

**Access model examples:** See the `examples/models.rst` documentation section or explore implementations in [lightly/models/]().

**Sources:** [docs/source/index.rst:95-100](), [docs/source/getting_started/advanced.rst:211-219](), [lightly/models/__init__.py]()

---

## Common Patterns Across Tutorials

### Standard Training Workflow

```mermaid
graph TD
    DS["Create Dataset<br/>LightlyDataset"]
    TRANS["Configure Transforms<br/>method-specific"]
    LOADER["Create DataLoader<br/>batch_size, num_workers"]
    MODEL["Define Model<br/>backbone + heads"]
    LOSS["Initialize Loss<br/>contrastive/distillation"]
    OPT["Setup Optimizer<br/>SGD or Adam"]
    TRAIN["Training Loop<br/>PyTorch or Lightning"]
    EVAL["Generate Embeddings<br/>frozen backbone"]
    ANALYZE["Analysis<br/>kNN, visualization, etc."]
    
    DS --> TRANS
    TRANS --> LOADER
    MODEL --> TRAIN
    LOSS --> TRAIN
    OPT --> TRAIN
    LOADER --> TRAIN
    TRAIN --> EVAL
    EVAL --> ANALYZE
```

### Key Classes and Functions

**Data handling:**
- `lightly.data.LightlyDataset` - Unified dataset interface
- `lightly.data.VideoDataset` - Video frame extraction
- `lightly.transforms.*Transform` - Method-specific augmentations

**Model components:**
- `lightly.models.modules.heads.*` - Projection and prediction heads
- `lightly.models.utils.update_momentum()` - EMA updates for momentum encoders
- `lightly.models.utils.deactivate_requires_grad()` - Freeze parameters
- `lightly.models.utils.batch_shuffle()` - Prevent batch norm leakage

**Loss functions:**
- `lightly.loss.NTXentLoss` - NT-Xent contrastive loss with optional memory bank
- `lightly.loss.NegativeCosineSimilarity` - For SimSiam/BYOL
- `lightly.loss.DINOLoss` - Self-distillation loss
- `lightly.loss.MSNLoss` / `PMSNLoss` - Masked Siamese Networks

**Training frameworks:**
- Direct PyTorch training loops (Tutorial 4)
- PyTorch Lightning modules (Tutorials 2, 3, 5, 6)

**Sources:** [lightly/__init__.py](), [lightly/data/__init__.py](), [lightly/models/__init__.py](), [lightly/loss/__init__.py]()

---

## Additional Resources

### Related Documentation Pages

- **Data Handling:** [Datasets](#3.1), [Data Collation and Batching](#3.2)
- **Model Architecture:** [Model Architectures](#2.1), [Model Components and Utilities](#2.2)
- **Transforms:** [Transforms and Augmentations](#2.4)
- **CLI Usage:** [Training Commands](#4.1), [Embedding Generation](#4.2)
- **Benchmarking:** [ImageNet Benchmarks](#7.1), [Evaluation Protocols](#7.2)

### Tutorial Files

All tutorial source files are available at:
- [docs/source/tutorials/]() - RST documentation files
- [docs/source/tutorials_source/package/]() - Executable Python tutorial scripts

**Sources:** [docs/source/index.rst:1-130](), [docs/source/getting_started/lightly_at_a_glance.rst:1-238]()

---

# Page: Developer Guide

# Developer Guide

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/check_example_nbs.yml](.github/workflows/check_example_nbs.yml)
- [.github/workflows/discord_release_notification.yml](.github/workflows/discord_release_notification.yml)
- [.github/workflows/release_pypi.yml](.github/workflows/release_pypi.yml)
- [.github/workflows/test.yml](.github/workflows/test.yml)
- [.github/workflows/test_api_deps_only.yml](.github/workflows/test_api_deps_only.yml)
- [.github/workflows/test_code_format.yml](.github/workflows/test_code_format.yml)
- [.github/workflows/test_minimal_deps.yml](.github/workflows/test_minimal_deps.yml)
- [.github/workflows/test_setup.yml](.github/workflows/test_setup.yml)
- [.github/workflows/tests_unmocked.yml](.github/workflows/tests_unmocked.yml)
- [.github/workflows/weekly_dependency_test.yml](.github/workflows/weekly_dependency_test.yml)
- [Makefile](Makefile)
- [lightly/cli/__init__.py](lightly/cli/__init__.py)
- [lightly/cli/download_cli.py](lightly/cli/download_cli.py)
- [lightly/loss/pmsn_loss.py](lightly/loss/pmsn_loss.py)
- [lightly/models/modules/ijepa_timm.py](lightly/models/modules/ijepa_timm.py)
- [lightly/models/modules/masked_autoencoder_timm.py](lightly/models/modules/masked_autoencoder_timm.py)
- [lightly/models/modules/masked_vision_transformer_timm.py](lightly/models/modules/masked_vision_transformer_timm.py)
- [pyproject.toml](pyproject.toml)
- [requirements/base.txt](requirements/base.txt)
- [setup.py](setup.py)
- [tests/cli/test_cli_download.py](tests/cli/test_cli_download.py)
- [tests/embedding/test_embedding.py](tests/embedding/test_embedding.py)
- [tests/loss/test_msn_loss.py](tests/loss/test_msn_loss.py)
- [tests/loss/test_pmsn_loss.py](tests/loss/test_pmsn_loss.py)

</details>



This document provides essential information for developers contributing to the Lightly codebase. It covers development environment setup, code organization, testing practices, and build system configuration. For detailed information about build configuration and dependency management, see [Project Configuration](#9.1). For comprehensive testing and CI/CD documentation, see [Testing and CI/CD](#9.2).

## Development Environment Setup

The Lightly project uses a modern Python development toolchain with `uv` for fast package management and virtual environment handling. The project requires Python 3.6 or higher ([pyproject.toml:10]()).

### Installing Dependencies

The project provides several dependency installation targets via the Makefile:

| Target | Purpose | Use Case |
|--------|---------|----------|
| `install-pinned` | Pinned versions for reproducibility | Standard development |
| `install-pinned-extras` | Pinned versions + dev tools | Development with testing/formatting |
| `install-minimal` | Minimal PyTorch versions | Testing backward compatibility |
| `install-minimal-extras` | Minimal + dev tools | Testing with older dependencies |
| `install-latest` | Latest available versions | Upstream compatibility testing |
| `install-api-only` | API client dependencies only | Platform integration work |

**Development Environment Setup:**

```bash
# Install uv and create virtual environment
make install-uv reset-venv

# Activate the virtual environment
source .venv/bin/activate

# Install development dependencies
make install-pinned-extras
```

The `install-pinned-extras` target installs all core dependencies plus development tools including pytest, black, isort, mypy, sphinx, and other utilities needed for testing and documentation ([pyproject.toml:60-91]()).

Sources: [pyproject.toml:1-321](), [.github/workflows/test.yml:49-53](), [.github/workflows/test_setup.yml:44-48]()

## Repository Structure

The Lightly codebase follows a modular architecture organized into functional subsystems:

```
lightly/
├── api/                    # Platform integration layer
│   ├── api_workflow_client.py
│   ├── retry_utils.py
│   └── download.py
├── cli/                    # Command-line interface
│   ├── train_cli.py
│   ├── embed_cli.py
│   └── config/
├── data/                   # Dataset and data loading
│   ├── dataset.py
│   └── collate.py
├── models/                 # SSL model architectures
│   ├── modules/
│   └── utils.py
├── loss/                   # Loss functions
├── transforms/             # Data augmentation
├── utils/                  # Utilities and helpers
│   └── benchmarking/
├── core.py                 # Python API entry points
└── openapi_generated/      # Auto-generated API client
```

**Key subsystems:**
- **Models**: SSL architectures, backbones, projection heads (see [Self-Supervised Learning Models](#2))
- **Data**: Dataset classes, data loading, transforms (see [Data Handling](#3))
- **CLI**: Command-line tools and Hydra configuration (see [Command-Line Interface](#4))
- **API**: Platform integration and workflow client (see [Platform Integration](#6))
- **Utils**: Benchmarking, helper functions, retry logic

Sources: [pyproject.toml:127-129](), repository structure

## Development Workflow

### Development Workflow Overview

```mermaid
graph TB
    subgraph "Development Tools"
        UV["uv<br/>Package Manager"]
        Venv[".venv<br/>Virtual Environment"]
        Make["Makefile<br/>Task Runner"]
    end
    
    subgraph "Code Quality Tools"
        Black["black==23.1.0<br/>Code Formatter"]
        Isort["isort==5.11.5<br/>Import Sorter"]
        Mypy["mypy==1.4.1<br/>Type Checker"]
    end
    
    subgraph "Testing Tools"
        Pytest["pytest<br/>Test Runner"]
        PytestCov["pytest-cov<br/>Coverage Reporter"]
        PytestMock["pytest-mock<br/>Mocking Utilities"]
        Responses["responses<br/>HTTP Mocking"]
    end
    
    subgraph "Make Commands"
        FormatCheck["make format-check<br/>black + isort"]
        TypeCheck["make type-check<br/>mypy"]
        Test["pytest -s -v<br/>Run Tests"]
    end
    
    subgraph "Configuration Files"
        PyProject["pyproject.toml<br/>Build + Tool Config"]
        PreCommit[".pre-commit-config.yaml<br/>Git Hooks"]
    end
    
    UV --> Venv
    Make --> UV
    
    Make --> FormatCheck
    Make --> TypeCheck
    
    FormatCheck --> Black
    FormatCheck --> Isort
    TypeCheck --> Mypy
    
    Test --> Pytest
    Pytest --> PytestCov
    Pytest --> PytestMock
    Pytest --> Responses
    
    PyProject --> Black
    PyProject --> Isort
    PyProject --> Mypy
    PyProject --> Pytest
    
    PreCommit --> Black
    PreCommit --> Isort
```

Sources: [pyproject.toml:60-91](), [pyproject.toml:137-142](), [.github/workflows/test_code_format.yml:1-42]()

### Code Formatting

The project enforces consistent code style using `black` and `isort` with frozen versions to ensure consistency across development machines and CI:

```bash
# Check code format without modifying files
make format-check

# Auto-format code (if available in Makefile)
black lightly/ tests/
isort lightly/ tests/
```

**Black Configuration** ([pyproject.toml:137-138]()):
- Extends exclusion to skip `lightly/openapi_generated/.*` (auto-generated code)

**Isort Configuration** ([pyproject.toml:140-142]()):
- Profile: `black` (compatible with black formatting)
- Extends skip to exclude `lightly/openapi_generated`

Versions are pinned at:
- `black==23.1.0`
- `isort==5.11.5`

These must match the versions in `.pre-commit-config.yaml` to ensure pre-commit hooks match CI validation.

Sources: [pyproject.toml:82-84](), [pyproject.toml:137-142](), [.github/workflows/test_code_format.yml:34-37]()

### Type Checking

The project uses `mypy` with strict configuration to enforce type safety. Type checking runs on modified code during CI:

```bash
# Run type checking
make type-check
```

**Mypy Configuration** ([pyproject.toml:147-181]()):

| Setting | Value | Purpose |
|---------|-------|---------|
| `disallow_untyped_defs` | `true` | All functions must have type annotations |
| `disallow_any_generics` | `true` | Generic types must have type parameters |
| `strict_equality` | `true` | Strict equality checks |
| `warn_return_any` | `true` | Warn when returning `Any` |
| `warn_unreachable` | `true` | Detect unreachable code |

**Exclusions**: Many modules are currently excluded from type checking ([pyproject.toml:185-297]()). The project is gradually adding type annotations, with a long-term goal to remove these exclusions.

**Module-Level Overrides**:
- API, CLI, data, and models modules: `follow_imports = "skip"` ([pyproject.toml:300-309]())
- OpenAPI generated code: `ignore_errors = true` ([pyproject.toml:312-316]())

Sources: [pyproject.toml:147-316](), [.github/workflows/test_code_format.yml:38-41]()

### Running Tests Locally

The test suite uses `pytest` with several plugins for enhanced functionality:

```bash
# Activate virtual environment
source .venv/bin/activate

# Set environment variable to skip version checking
export LIGHTLY_SERVER_LOCATION="localhost:-1"

# Run all tests
python -m pytest -s -v --runslow

# Run specific test file
python -m pytest tests/api/test_download.py -v

# Run with coverage (Python 3.12)
python -m pytest --cov=./lightly --cov-report=xml --ignore=./lightly/openapi_generated/
```

**Pytest Plugins**:
- `pytest-forked`: Run tests in isolated processes ([pyproject.toml:64]())
- `pytest-xdist`: Parallel test execution ([pyproject.toml:65]())
- `pytest-mock`: Mocking utilities ([pyproject.toml:66]())
- `responses`: HTTP request mocking ([pyproject.toml:67]())

**Test Organization**:
- Unit tests in `tests/` mirror the `lightly/` structure
- Mocked API tests use `responses` library to avoid real API calls
- Unmocked integration tests in `tests/UNMOCKED_end2end_tests/` (run manually)

Sources: [pyproject.toml:63-67](), [.github/workflows/test.yml:56-68](), [tests/api/test_download.py:1-124]()

## Testing Infrastructure Overview

The CI/CD system uses GitHub Actions with multiple workflows for different testing scenarios. The testing strategy includes:

```mermaid
graph TB
    subgraph "CI Workflows"
        Test["test.yml<br/>Main Unit Tests"]
        CodeFormat["test_code_format.yml<br/>Black + Isort + Mypy"]
        Setup["test_setup.yml<br/>CLI Validation"]
        Minimal["test_minimal_deps.yml<br/>Backward Compatibility"]
        API["test_api_deps_only.yml<br/>API Client Only"]
        Weekly["weekly_dependency_test.yml<br/>Latest Dependencies"]
        Unmocked["tests_unmocked.yml<br/>Integration Tests"]
    end
    
    subgraph "Change Detection"
        PathFilter["dorny/paths-filter@v3<br/>Skip on docs-only changes"]
    end
    
    subgraph "Test Matrix"
        Python37["Python 3.7<br/>Minimum Version"]
        Python312["Python 3.12<br/>Current Version"]
        PinnedDeps["Pinned Dependencies"]
        MinimalDeps["Minimal Dependencies"]
        LatestDeps["Latest Dependencies"]
    end
    
    subgraph "Coverage & Reporting"
        Codecov["codecov/codecov-action@v4<br/>Coverage Upload"]
    end
    
    Test --> PathFilter
    CodeFormat --> PathFilter
    Setup --> PathFilter
    Minimal --> PathFilter
    API --> PathFilter
    
    PathFilter -->|"Code Changed"| Python37
    PathFilter -->|"Code Changed"| Python312
    
    Python37 --> PinnedDeps
    Python37 --> MinimalDeps
    Python312 --> PinnedDeps
    Python312 --> LatestDeps
    
    Python312 --> Codecov
    
    Weekly --> LatestDeps
    Unmocked --> PathFilter
```

**Key Features**:

1. **Change Detection**: Uses `dorny/paths-filter` to skip expensive tests when only documentation changes ([.github/workflows/test.yml:11-26]())

2. **Test Matrix**: Tests against multiple Python versions (3.7, 3.12) and dependency configurations (pinned, minimal, latest)

3. **Coverage**: Collected only on Python 3.12 to avoid redundancy, uploaded to Codecov ([.github/workflows/test.yml:62-75]())

4. **Weekly Testing**: Scheduled runs with latest dependencies catch external breakages ([.github/workflows/weekly_dependency_test.yml:9-10]())

5. **Manual Workflows**: Integration tests against staging server run via `workflow_dispatch` ([.github/workflows/tests_unmocked.yml:2]())

For detailed information about testing strategies, mocking patterns, and CI/CD pipelines, see [Testing and CI/CD](#9.2).

Sources: [.github/workflows/test.yml:1-76](), [.github/workflows/test_code_format.yml:1-42](), [.github/workflows/weekly_dependency_test.yml:1-42]()

## Build and Distribution System

The project uses modern Python packaging with `pyproject.toml` as the single source of configuration:

### Build System Architecture

```mermaid
graph LR
    subgraph "Configuration"
        PyProject["pyproject.toml<br/>PEP 621 Metadata"]
        SetupPy["setup.py<br/>Legacy Compatibility"]
        Version["lightly.__version__<br/>Dynamic Version"]
        Readme["README.md<br/>Dynamic Readme"]
    end
    
    subgraph "Build Backend"
        SetupTools["setuptools>=21<br/>Build System"]
        SetupToolsSCM["setuptools-scm<br/>Version from Git"]
    end
    
    subgraph "CLI Registration"
        Crop["lightly-crop<br/>crop_cli:entry"]
        Download["lightly-download<br/>download_cli:entry"]
        Embed["lightly-embed<br/>embed_cli:entry"]
        Magic["lightly-magic<br/>lightly_cli:entry"]
        Serve["lightly-serve<br/>serve_cli:entry"]
        Train["lightly-ssl-train<br/>train_cli:entry"]
        VersionCLI["lightly-version<br/>version_cli:entry"]
    end
    
    subgraph "Distribution"
        Wheel["wheel<br/>Binary Distribution"]
        SDist["sdist<br/>Source Distribution"]
        PyPI["PyPI<br/>pypi.org"]
    end
    
    PyProject --> SetupTools
    SetupPy --> SetupTools
    SetupToolsSCM --> Version
    
    PyProject --> Crop
    PyProject --> Download
    PyProject --> Embed
    PyProject --> Magic
    PyProject --> Serve
    PyProject --> Train
    PyProject --> VersionCLI
    
    Version --> SetupTools
    Readme --> SetupTools
    
    SetupTools --> Wheel
    SetupTools --> SDist
    
    Wheel --> PyPI
    SDist --> PyPI
```

**Key Components**:

1. **Build System** ([pyproject.toml:1-6]()):
   - Uses `setuptools>=21` with `setuptools-scm` for version management
   - Follows PEP 517/518 standards

2. **Project Metadata** ([pyproject.toml:8-54]()):
   - Name: `lightly`
   - Requires Python >=3.6
   - Dynamic fields: `version`, `readme`
   - Version derived from Git tags via `setuptools-scm`

3. **CLI Scripts** ([pyproject.toml:118-126]()):
   - Seven command-line entry points registered
   - Each maps to an `entry` function in its respective CLI module

4. **Package Discovery** ([pyproject.toml:127-129]()):
   - Includes all packages matching `lightly*`
   - Package data includes `lightly/cli/config/*.yaml`

5. **Optional Dependencies** ([pyproject.toml:56-108]()):
   - `all`: Full installation with all extras
   - `dev`: Development tools (testing, formatting, type checking)
   - `minimal`: Backward compatibility testing
   - `timm`: Vision transformer models
   - `video`: Video processing support
   - `matplotlib`: Visualization support
   - `openapi`: API client dependencies

For complete build configuration details, see [Project Configuration](#9.1).

Sources: [pyproject.toml:1-136](), [setup.py:1-6](), [.github/workflows/release_pypi.yml:1-58]()

## Contributing Guidelines

### Pre-Commit Checks

Before submitting a pull request, ensure:

1. **Code is formatted**: Run `make format-check` or auto-format with `black` and `isort`
2. **Types check**: Run `make type-check` to verify mypy passes
3. **Tests pass**: Run `pytest -s -v --runslow` locally
4. **Environment variables**: Set `LIGHTLY_SERVER_LOCATION="localhost:-1"` to skip version checking during tests

### Pull Request Workflow

When you open a pull request, GitHub Actions automatically runs:

1. **Change Detection**: Determines if code changes require testing
2. **Code Format Check**: Validates black, isort, and mypy on Python 3.7 and 3.12
3. **Unit Tests**: Runs full test suite on Python 3.7 (pinned deps) and 3.12 (pinned + minimal deps)
4. **Setup Validation**: Tests CLI installation and basic commands
5. **Coverage**: Uploads coverage report to Codecov (Python 3.12 only)

### Release Process

Releases are handled via `workflow_dispatch` on [.github/workflows/release_pypi.yml:1-58]():

1. **Checkout**: Fetches latest release tag from Git
2. **Build**: Creates wheel and source distribution using `python -m build`
3. **Upload**: Publishes to PyPI using `twine`
4. **Notifications**: Sends updates to Slack (internal) and Discord (community)

The Discord notification is also triggered automatically when a GitHub release is published ([.github/workflows/discord_release_notification.yml:1-42]()).

Sources: [.github/workflows/test.yml:1-76](), [.github/workflows/test_code_format.yml:1-42](), [.github/workflows/release_pypi.yml:1-58]()

## Testing Patterns

### Mocking HTTP Requests

The test suite uses the `responses` library to mock HTTP calls to the Lightly platform:

```python
# Example from test_download.py
mock_response = MagicMock()
mock_response.raw = MagicMock()
mock_response_manager = MagicMock()
mock_response_manager.__enter__.return_value = mock_response
mock_requests_get = mocker.patch("requests.get", return_value=mock_response_manager)
```

The `download_and_write_file` function ([lightly/api/download.py:18-48]()) supports:
- URL downloads with retry logic
- Session persistence for connection pooling
- Configurable retry functions
- Timeout handling

### Multi-threaded Testing

The `download_and_write_all_files` function ([lightly/api/download.py:51-132]()) uses `ThreadPoolExecutor` for parallel downloads. Tests verify:
- Thread-safe session management
- Lock-based coordination
- Progress bar integration (via `tqdm`)
- Exception handling per file

### Environment Configuration

Tests set `LIGHTLY_SERVER_LOCATION="localhost:-1"` to disable version checking and prevent real API calls. This environment variable is checked throughout the codebase to determine if the application should attempt to contact the Lightly platform.

Sources: [tests/api/test_download.py:1-124](), [lightly/api/download.py:1-132](), [.github/workflows/test.yml:60-61]()

## Dependency Management Strategy

The project uses a tiered dependency strategy to ensure compatibility across different use cases:

| Requirements File | Purpose | Usage |
|-------------------|---------|-------|
| `requirements/base.txt` | Minimal API client deps | Platform integration only |
| `pyproject.toml` [project.dependencies] | Core framework deps | Standard installation |
| `pyproject.toml` [project.optional-dependencies.minimal] | Minimum PyTorch versions | Backward compatibility testing |
| `pyproject.toml` [project.optional-dependencies.dev] | Dev tools | Local development |

**Base Dependencies** ([requirements/base.txt:1-13]()):
- Core: `certifi`, `requests`, `urllib3`, `tqdm`
- Configuration: `hydra-core>=1.0.0`
- Data: `numpy>=1.18.1`
- Serialization: `pydantic>=1.10.5`
- Utilities: `six`, `python_dateutil`, `aenum`, `lightly_utils`

**Core Dependencies** ([pyproject.toml:38-53]()):
- Extends base with `torch`, `torchvision`, `pytorch_lightning>=1.0.4`

**Version Pinning**:
- Dev tools (`black`, `isort`, `mypy`) use exact versions to prevent formatting/type check drift
- Production dependencies use minimum version specifiers (`>=`) for flexibility
- Comment in pyproject.toml emphasizes matching pre-commit hook versions ([pyproject.toml:82]())

Sources: [requirements/base.txt:1-13](), [pyproject.toml:38-91](), [.github/workflows/test_minimal_deps.yml:35-36]()

---

# Page: Project Configuration

# Project Configuration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/check_example_nbs.yml](.github/workflows/check_example_nbs.yml)
- [.github/workflows/discord_release_notification.yml](.github/workflows/discord_release_notification.yml)
- [Makefile](Makefile)
- [lightly/cli/__init__.py](lightly/cli/__init__.py)
- [lightly/cli/download_cli.py](lightly/cli/download_cli.py)
- [lightly/loss/pmsn_loss.py](lightly/loss/pmsn_loss.py)
- [lightly/models/modules/ijepa_timm.py](lightly/models/modules/ijepa_timm.py)
- [lightly/models/modules/masked_autoencoder_timm.py](lightly/models/modules/masked_autoencoder_timm.py)
- [lightly/models/modules/masked_vision_transformer_timm.py](lightly/models/modules/masked_vision_transformer_timm.py)
- [pyproject.toml](pyproject.toml)
- [requirements/base.txt](requirements/base.txt)
- [setup.py](setup.py)
- [tests/cli/test_cli_download.py](tests/cli/test_cli_download.py)
- [tests/embedding/test_embedding.py](tests/embedding/test_embedding.py)
- [tests/loss/test_msn_loss.py](tests/loss/test_msn_loss.py)
- [tests/loss/test_pmsn_loss.py](tests/loss/test_pmsn_loss.py)

</details>



This document explains the build system, dependency management, and package configuration in the Lightly framework. It is intended for developers and contributors who need to understand how the project is structured, built, and packaged for distribution.

## Build System Configuration

Lightly uses modern Python packaging standards with `pyproject.toml` ([PEP 517](https://peps.python.org/pep-0517/), [PEP 518](https://peps.python.org/pep-0518/)) as the primary configuration file. The build backend is `setuptools` with `setuptools-scm` for version management.

**Build System Configuration**

```mermaid
graph TD
    subgraph "pyproject.toml Sections"
        BuildSystem["[build-system]<br/>requires setuptools>=21<br/>setuptools-scm"]
        Project["[project]<br/>name, version, dependencies"]
        OptionalDeps["[project.optional-dependencies]<br/>all, dev, minimal, timm, video"]
        Scripts["[project.scripts]<br/>CLI entry points"]
        ToolBlack["[tool.black]"]
        ToolIsort["[tool.isort]"]
        ToolMypy["[tool.mypy]"]
        ToolCoverage["[tool.coverage.run]"]
        SetupTools["[tool.setuptools.*]<br/>packages, package-data"]
    end
    
    Setup["setup.py"] --> |"legacy compatibility"| BuildSystem
    Requirements["requirements/base.txt"] --> |"API-only install"| Project
    
    BuildSystem --> |"builds"| WheelDist["wheel + sdist"]
    Scripts --> |"registers"| CLICommands["lightly-magic<br/>lightly-ssl-train<br/>lightly-embed<br/>lightly-download<br/>etc."]
```

The build configuration consists of:

- **`[build-system]`**: Declares `setuptools>=21` and `setuptools-scm` as build dependencies
- **`[project]`**: Package metadata, dependencies, and scripts
- **`[tool.*]`**: Tool-specific configuration (black, isort, mypy, coverage)
- **`setup.py`**: Minimal shim for backward compatibility with legacy build tools

Sources: [pyproject.toml:1-7](), [setup.py:1-7]()

### Package Metadata

The `[project]` section in `pyproject.toml` defines core package metadata:

| Field | Value | Notes |
|-------|-------|-------|
| `name` | `"lightly"` | Package name on PyPI |
| `requires-python` | `">=3.6"` | Minimum Python version |
| `authors` | `Lightly Team` | Package maintainers |
| `license` | `{file = "LICENSE.txt"}` | MIT License |
| `description` | `"A deep learning package for self-supervised learning"` | Short description |
| `classifiers` | Python 3.6-3.12, MIT License, etc. | PyPI classifiers |
| `dynamic` | `["version", "readme"]` | Version from `lightly.__version__`, README from `README.md` |

The version is dynamically determined from `lightly.__version__` using `setuptools-scm`, which derives the version from git tags.

Sources: [pyproject.toml:8-54](), [pyproject.toml:130-132]()

## Dependency Management

Lightly's dependencies are organized into core dependencies and optional extras. The core dependencies in the `[project]` section include all packages needed for self-supervised learning workflows.

### Core Dependencies

The base dependencies required for all installations:

| Package | Version Constraint | Purpose |
|---------|-------------------|---------|
| `certifi` | `>=14.05.14` | SSL certificates |
| `hydra-core` | `>=1.0.0` | CLI configuration management |
| `lightly_utils` | `~=0.0.0` | Lightly utility functions |
| `numpy` | `>=1.18.1` | Numerical operations |
| `python_dateutil` | `>=2.5.3` | Date parsing for API |
| `requests` | `>=2.27.0` | HTTP client for API |
| `six` | `>=1.10` | Python 2/3 compatibility |
| `tqdm` | `>=4.44` | Progress bars |
| `torch` | (unversioned) | PyTorch deep learning framework |
| `torchvision` | (unversioned) | PyTorch vision utilities |
| `pydantic` | `>=1.10.5` | Data validation (API models) |
| `pytorch_lightning` | `>=1.0.4` | Training framework |
| `urllib3` | `>=1.25.3` | HTTP client utilities |
| `aenum` | `>=3.1.11` | Enhanced enumerations (API) |

Note that `torch` and `torchvision` have no version constraints in `pyproject.toml` to allow flexible PyTorch installations. The `minimal` extras group specifies minimum tested versions.

These same dependencies are listed in `requirements/base.txt` for API-only installations (see "Minimal Installation" below).

Sources: [pyproject.toml:38-53](), [requirements/base.txt:1-13]()

### Optional Dependency Groups

The `[project.optional-dependencies]` section defines extras for different use cases:

| Extra | Contents | Purpose |
|-------|----------|---------|
| `all` | `lightly[dev,matplotlib,minimal,timm,video]` | All optional dependencies combined |
| `dev` | `sphinx`, `pylint`, `pytest`, `black==23.1.0`, `isort==5.11.5`, `mypy==1.4.1`, etc. | Development tools (frozen versions for consistency) |
| `minimal` | `torch>=1.10.0`, `torchvision>=0.11.0`, `pytorch_lightning>=1.6` | Minimum tested versions |
| `openapi` | `python_dateutil>=2.5.3`, `pydantic>=1.10.5`, `aenum>=3.1.11` | API client generation |
| `timm` | `timm>=0.9.9` | TIMM model support (`MaskedVisionTransformerTIMM`, `MAEDecoderTIMM`) |
| `video` | `av>=8.0.3; python_version>='3.8'` | Video dataset support (`VideoDataset`) |
| `matplotlib` | `matplotlib>=3` | Plotting utilities |

**Installation Examples**

```bash
# Full installation with all extras
pip install lightly[all]

# API client only (minimal dependencies)
pip install -r requirements/base.txt
pip install lightly --no-deps

# Development installation
pip install lightly[dev]

# Training with TIMM models
pip install lightly[timm]
```

**Dependency Relationships**

```mermaid
graph LR
    User["User Installation"]
    
    User --> |"pip install lightly"| CoreDeps["Core Dependencies<br/>torch, torchvision,<br/>pytorch_lightning, etc."]
    User --> |"pip install lightly[timm]"| CorePlusTimm["Core + timm>=0.9.9"]
    User --> |"pip install lightly[video]"| CorePlusVideo["Core + av>=8.0.3"]
    User --> |"pip install lightly[all]"| AllDeps["All Extras"]
    User --> |"requirements/base.txt"| ApiOnly["API Client Only<br/>certifi, requests,<br/>pydantic, etc."]
    
    CorePlusTimm --> |"enables"| TimmModels["MaskedVisionTransformerTIMM<br/>MAEDecoderTIMM<br/>IJEPAPredictorTIMM"]
    CorePlusVideo --> |"enables"| VideoDataset["VideoDataset"]
```

Sources: [pyproject.toml:56-108](), [requirements/base.txt:1-13]()

## CLI Entry Points

The `[project.scripts]` section registers command-line tools that are installed as executable scripts:

| Command | Entry Point | Purpose |
|---------|------------|---------|
| `lightly-crop` | `lightly.cli.crop_cli:entry` | Crop images based on YOLO labels |
| `lightly-download` | `lightly.cli.download_cli:entry` | Download tagged samples from platform |
| `lightly-embed` | `lightly.cli.embed_cli:entry` | Generate embeddings from checkpoints |
| `lightly-magic` | `lightly.cli.lightly_cli:entry` | One-command train + embed workflow |
| `lightly-serve` | `lightly.cli.serve_cli:entry` | Serve embeddings (deprecated) |
| `lightly-ssl-train` | `lightly.cli.train_cli:entry` | Train SSL models |
| `lightly-version` | `lightly.cli.version_cli:entry` | Display version information |

**Entry Point Structure**

```mermaid
graph TD
    PyProjectScripts["[project.scripts]<br/>in pyproject.toml"]
    
    PyProjectScripts --> |"registers"| CropEntry["lightly-crop =<br/>lightly.cli.crop_cli:entry"]
    PyProjectScripts --> |"registers"| DownloadEntry["lightly-download =<br/>lightly.cli.download_cli:entry"]
    PyProjectScripts --> |"registers"| EmbedEntry["lightly-embed =<br/>lightly.cli.embed_cli:entry"]
    PyProjectScripts --> |"registers"| MagicEntry["lightly-magic =<br/>lightly.cli.lightly_cli:entry"]
    PyProjectScripts --> |"registers"| TrainEntry["lightly-ssl-train =<br/>lightly.cli.train_cli:entry"]
    
    CropEntry --> |"calls"| CropFunc["def entry():<br/>    crop_cli()"]
    DownloadEntry --> |"calls"| DownloadFunc["def entry():<br/>    download_cli()"]
    EmbedEntry --> |"calls"| EmbedFunc["def entry():<br/>    embed_cli()"]
    MagicEntry --> |"calls"| MagicFunc["def entry():<br/>    lightly_cli()"]
    TrainEntry --> |"calls"| TrainFunc["def entry():<br/>    train_cli()"]
    
    DownloadFunc --> |"decorated with"| HydraMain["@hydra.main(config_path='config',<br/>config_name='config')"]
    HydraMain --> |"loads"| ConfigYAML["lightly/cli/config/config.yaml"]
```

Each CLI module defines an `entry()` function that serves as the entry point. Most CLI tools use Hydra for configuration management, loading settings from YAML files in `lightly/cli/config/`.

**Configuration Package Data**

The configuration files are included in the package distribution via the `[tool.setuptools.package-data]` section:

```
[tool.setuptools.package-data]
lightly = ["lightly/cli/config/*.yaml"]
```

Sources: [pyproject.toml:118-126](), [pyproject.toml:134-135](), [lightly/cli/__init__.py:1-14](), [lightly/cli/download_cli.py:84-135]()

## Development Tool Configuration

The `[tool.*]` sections configure development tools. These configurations are read directly by the tools when invoked.

### Code Formatting Tools

**Black Configuration**

```toml
[tool.black]
extend-exclude = "lightly/openapi_generated/.*"
```

Black formats all Python code except auto-generated OpenAPI client code in `lightly/openapi_generated/`.

**Isort Configuration**

```toml
[tool.isort]
profile = "black"
extend_skip = "lightly/openapi_generated"
```

Isort is configured to be compatible with Black's formatting and skips the same generated code directory.

**Running Format Checks**

```bash
# Format code (Makefile target)
make format

# Check formatting without modifying files
make format-check
```

Sources: [pyproject.toml:137-142](), [Makefile:37-46]()

### Type Checking Configuration

Mypy is configured with strict type checking in `[tool.mypy]`:

| Setting | Value | Purpose |
|---------|-------|---------|
| `ignore_missing_imports` | `true` | Allow imports from untyped libraries |
| `strict_equality` | `true` | Strict equality comparisons |
| `disallow_any_decorated` | `true` | Disallow `Any` in decorated functions |
| `disallow_any_generics` | `true` | Require explicit generic types |
| `disallow_untyped_defs` | `true` | All functions must have type hints |
| `disallow_incomplete_defs` | `true` | Function signatures must be complete |
| `check_untyped_defs` | `true` | Check bodies of untyped functions |
| `warn_unused_ignores` | `false` | Allow different ignores per Python version |
| `plugins` | `["numpy.typing.mypy_plugin"]` | NumPy type checking support |

**Exclusions**

The configuration excludes several modules that are in the process of being typed:

- CLI modules (`lightly/cli/*.py`)
- API workflow modules (`lightly/api/*.py`)
- Data modules (`lightly/data/*.py`)
- Deprecated models
- Test files
- Auto-generated OpenAPI code (`lightly/openapi_generated/*`)

These exclusions are defined in the `exclude` field and `[[tool.mypy.overrides]]` sections.

```bash
# Run type checking
make type-check
```

Sources: [pyproject.toml:147-316](), [Makefile:66-68]()

### Coverage Configuration

```toml
[tool.coverage.run]
omit = ["lightly/openapi_generated/*"]
```

Code coverage analysis excludes auto-generated OpenAPI client code.

Sources: [pyproject.toml:144-145]()

### Jupytext Configuration

```toml
[tool.jupytext]
notebook_metadata_filter="-all"
cell_metadata_filter="-all"
```

Jupytext is configured to strip notebook and cell metadata when converting between `.py` and `.ipynb` formats, reducing git diff noise.

Sources: [pyproject.toml:318-320]()

## Package Structure Configuration

The `[tool.setuptools.*]` sections define how the package is built and what files are included.

### Package Discovery

```toml
[tool.setuptools.packages.find]
include = ["lightly*"]
```

This configuration tells setuptools to include all packages starting with `lightly`, which includes:
- `lightly` (main package)
- `lightly.cli` (CLI modules)
- `lightly.api` (API client)
- `lightly.data` (data handling)
- `lightly.models` (SSL models)
- `lightly.loss` (loss functions)
- `lightly.transforms` (augmentations)
- `lightly.openapi_generated` (generated API client)
- All other subpackages

### Dynamic Metadata

```toml
[tool.setuptools.dynamic]
readme = {file = ["README.md"], content-type = "text/markdown"}
version = {attr = "lightly.__version__"}
```

- **README**: Loaded from `README.md` and used as the PyPI long description
- **Version**: Extracted from `lightly.__version__` attribute, which is managed by `setuptools-scm` based on git tags

### Package Data

```toml
[tool.setuptools.package-data]
lightly = ["lightly/cli/config/*.yaml"]
```

Includes Hydra configuration YAML files in the distributed package. These files are located in `lightly/cli/config/` and are needed for CLI tools to function.

Sources: [pyproject.toml:127-135]()

## Installation Targets

The Makefile provides targets for installing the package with different dependency configurations. These targets use `uv` (a fast Python package installer) for dependency management.

**Installation Targets Overview**

```mermaid
graph TD
    subgraph "Development Environment Setup"
        InstallUV["make install-uv"] --> |"installs"| UVTool["uv 0.2.25"]
        ResetVenv["make reset-venv"] --> |"creates"| FreshVenv[".venv/"]
        UVTool --> InstallCommands["Installation Targets"]
    end
    
    subgraph "Installation Targets"
        InstallDev["make install-dev"] --> |"uv pip install -e .[all]"| DevEnv["Development Environment"]
        InstallApiOnly["make install-api-only"] --> |"requirements/base.txt + --no-deps"| ApiOnlyEnv["API Client Only"]
        InstallMinimal["make install-minimal"] --> |"--resolution=lowest-direct .[minimal]"| MinimalEnv["Minimal Dependencies"]
        InstallPinned["make install-pinned-extras"] --> |"--exclude-newer date .[all]"| PinnedEnv["Pinned Dependencies"]
        InstallLatest["make install-latest"] --> |"--upgrade .[all]"| LatestEnv["Latest Dependencies"]
    end
    
    DevEnv --> |"includes"| PreCommit["pre-commit hooks"]
    MinimalEnv --> |"tests"| CI["CI Compatibility Tests"]
    PinnedEnv --> |"used in"| CI
```

### Key Installation Targets

| Target | Command | Purpose |
|--------|---------|---------|
| `install-dev` | `uv pip install -e . --all-extras` | Full development installation with pre-commit hooks |
| `install-api-only` | Install from `requirements/base.txt` then `pip install . --no-deps` | API client only, no PyTorch |
| `install-minimal` | `uv pip install --resolution=lowest-direct -e .[minimal]` | Minimum tested versions |
| `install-minimal-extras` | Same with extras `[matplotlib,minimal,timm,video]` | Minimum tested versions + extras |
| `install-pinned-extras` | `--exclude-newer ${EXCLUDE_NEWER_DATE} -e . --all-extras` | Pinned to specific date for CI stability |
| `install-latest` | `--upgrade --reinstall -e . --all-extras` | Latest compatible versions |

### Dependency Resolution Strategies

**Lowest Direct Dependencies (`install-minimal`)**

The `--resolution=lowest-direct` flag installs the minimum version for direct dependencies while allowing transitive dependencies to use newer compatible versions. This is used to test backward compatibility:

```bash
# Install minimal dependencies (Python 3.7 compatible)
make reset-venv
source .venv/bin/activate
make install-minimal
```

**Pinned Dependencies (`install-pinned-extras`)**

The `--exclude-newer` flag pins dependencies to versions released before a specific date (`EXCLUDE_NEWER_DATE="2025-08-07"` in the Makefile). This keeps CI stable when new dependency versions are released:

```bash
# Install with date-pinned dependencies
make install-pinned-extras
```

**CI-Specific Targets**

The Makefile defines Python version-specific targets used in CI:

- `install-pinned-extras-3.7`: Pinned extras without video support (PyAV requires Python 3.8+)
- `install-pinned-extras-3.12`: Pinned extras with PyAV system dependencies installed

Sources: [Makefile:95-217]()

### Code Quality Targets

| Target | Commands | Purpose |
|--------|----------|---------|
| `format` | `isort $(PYTHON_DIRS)` + `black $(PYTHON_DIRS)` | Format code in-place |
| `format-check` | `isort --check-only --diff` + `black --check` | Check formatting without changes |
| `lint` | `pylint --rcfile=pylintrc lightly tests` | Static code analysis |
| `type-check` | `mypy lightly tests` | Type checking |
| `test` | `pytest tests --runslow` | Run all tests including slow ones |
| `test-fast` | `pytest tests` | Run tests except slow ones |
| `static-checks` | `format-check` + `type-check` | All static checks |
| `all-checks` | `static-checks` + `test` | Full validation |

The `PYTHON_DIRS` variable defines directories to format: `benchmarks docs examples lightly tests`.

Sources: [Makefile:34-74]()

### Build and Distribution

```bash
# Build source and wheel distributions
make dist

# Clean build artifacts
make clean
```

The `dist` target builds both source distributions (`.tar.gz`) and wheel distributions (`.whl`) using `python -m build`.

Sources: [Makefile:76-79]()

## Data Configuration

The Lightly framework includes configuration for data handling components:

```mermaid
graph TD
    subgraph "Data Configuration"
        Config["config.yaml"] --> |configures| DataLoader["DataLoader"]
        DataLoader --> |loads| LightlyDataset["LightlyDataset"]
        LightlyDataset --> |creates subset| LightlySubset["LightlySubset"]
        LightlyDataset --> |transforms| MultiViews["Multiple Views"]
        MultiViews --> |collated by| MultiViewCollate["MultiViewCollate"]
    end
    
    subgraph "CLI Tool Example"
        DownloadCLI["lightly-download"] --> |uses| InputDir["input_dir"]
        DownloadCLI --> |uses| OutputDir["output_dir"]
        DownloadCLI --> |uses| NumWorkers["loader.num_workers"]
    end
    
    DataLoader --> |configured by| NumWorkers
    LightlyDataset --> |reads from| InputDir
    LightlyDataset --> |writes to| OutputDir
```

Configuration parameters control:
- Input and output directories for data
- Number of workers for data loading
- Batch size and other loader parameters

Sources: [lightly/cli/download_cli.py:22-82](), [lightly/data/lightly_subset.py:1-97](), [lightly/data/multi_view_collate.py:1-87](), [tests/data/test_LightlySubset.py:1-86]()

## Summary

The Lightly project configuration provides a comprehensive system for managing dependencies, development tools, and CLI tools. The configuration is primarily defined in `pyproject.toml` and supplemented by Makefile targets for common development tasks. The Hydra configuration system is used to manage CLI parameters, allowing users to override defaults through command-line arguments.

This configuration system ensures that Lightly can be used in various environments with different dependency requirements, from minimal installations to full development setups.

---

# Page: Testing and CI/CD

# Testing and CI/CD

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/check_example_nbs.yml](.github/workflows/check_example_nbs.yml)
- [.github/workflows/discord_release_notification.yml](.github/workflows/discord_release_notification.yml)
- [.github/workflows/release_pypi.yml](.github/workflows/release_pypi.yml)
- [.github/workflows/test.yml](.github/workflows/test.yml)
- [.github/workflows/test_api_deps_only.yml](.github/workflows/test_api_deps_only.yml)
- [.github/workflows/test_code_format.yml](.github/workflows/test_code_format.yml)
- [.github/workflows/test_minimal_deps.yml](.github/workflows/test_minimal_deps.yml)
- [.github/workflows/test_setup.yml](.github/workflows/test_setup.yml)
- [.github/workflows/tests_unmocked.yml](.github/workflows/tests_unmocked.yml)
- [.github/workflows/weekly_dependency_test.yml](.github/workflows/weekly_dependency_test.yml)
- [Makefile](Makefile)
- [lightly/loss/pmsn_loss.py](lightly/loss/pmsn_loss.py)
- [lightly/models/modules/ijepa_timm.py](lightly/models/modules/ijepa_timm.py)
- [lightly/models/modules/masked_autoencoder_timm.py](lightly/models/modules/masked_autoencoder_timm.py)
- [lightly/models/modules/masked_vision_transformer_timm.py](lightly/models/modules/masked_vision_transformer_timm.py)
- [pyproject.toml](pyproject.toml)
- [tests/loss/test_msn_loss.py](tests/loss/test_msn_loss.py)
- [tests/loss/test_pmsn_loss.py](tests/loss/test_pmsn_loss.py)

</details>



This page documents the testing infrastructure and continuous integration/continuous deployment (CI/CD) pipelines for the Lightly codebase. It covers test categories, mocking strategies, GitHub Actions workflows, dependency management approaches, and the release process.

For information about the project configuration and build system, see [Project Configuration](#9.1).

---

## Test Infrastructure Overview

The Lightly codebase employs a multi-layered testing strategy that balances comprehensive coverage with practical constraints around API quotas, execution time, and external dependencies. Tests are organized by purpose and dependency requirements.

```mermaid
graph TB
    subgraph "Test Categories"
        UnitTests["Unit Tests<br/>pytest with mocked server"]
        MinimalDeps["Minimal Dependency Tests<br/>Over-dependency checks"]
        CLITests["CLI Tests<br/>Command validation"]
        FormatTests["Code Format Tests<br/>black + isort"]
        TypeTests["Type Checking<br/>mypy strict"]
        UnmockedTests["Unmocked Tests<br/>Staging server"]
    end
    
    subgraph "Test Execution"
        LocalDev["Local Development"]
        CI["CI Pipeline"]
        Manual["Manual Trigger"]
        Weekly["Weekly Schedule"]
    end
    
    subgraph "Coverage Reporting"
        PytestCov["pytest-cov"]
        Codecov["Codecov Upload"]
    end
    
    LocalDev --> UnitTests
    LocalDev --> FormatTests
    LocalDev --> TypeTests
    
    CI --> UnitTests
    CI --> MinimalDeps
    CI --> CLITests
    CI --> FormatTests
    CI --> TypeTests
    
    Manual --> UnmockedTests
    Weekly --> MinimalDeps
    
    UnitTests --> PytestCov
    PytestCov --> Codecov
    
    style UnitTests fill:#e1f5ff
    style UnmockedTests fill:#ffe1e1
    style Codecov fill:#e1ffe1
```

**Sources:** [.github/workflows/test.yml:1-76](), [.github/workflows/test_minimal_deps.yml:1-58](), [.github/workflows/tests_unmocked.yml:1-34]()

---

## Mocking Strategy

The test suite uses a comprehensive mocking system to simulate API interactions without hitting actual servers. This approach enables fast, reliable, and quota-free testing.

### MockedApiWorkflowClient Architecture

The `MockedApiWorkflowClient` class extends `ApiWorkflowClient` and replaces all API clients with mocked versions:

```mermaid
graph TB
    ApiWorkflowClient["ApiWorkflowClient<br/>Production Client"]
    MockedApiWorkflowClient["MockedApiWorkflowClient<br/>Test Client"]
    
    subgraph "Mocked API Clients"
        MockedEmbeddingsApi["MockedEmbeddingsApi"]
        MockedSamplingsApi["MockedSamplingsApi"]
        MockedJobsApi["MockedJobsApi"]
        MockedTagsApi["MockedTagsApi"]
        MockedSamplesApi["MockedSamplesApi"]
        MockedDatasetsApi["MockedDatasetsApi"]
        MockedDatasourcesApi["MockedDatasourcesApi"]
        MockedComputeWorkerApi["MockedComputeWorkerApi"]
        MockedScoresApi["MockedScoresApi"]
        MockedMappingsApi["MockedMappingsApi"]
    end
    
    subgraph "In-Memory State"
        DatasetState["datasets<br/>shared_datasets"]
        SampleState["sample_create_requests"]
        WorkerState["_compute_worker_runs<br/>_registered_workers"]
        DatasourceState["_datasources<br/>_processed_until_timestamp"]
    end
    
    MockedApiWorkflowClient --|extends| ApiWorkflowClient
    
    MockedApiWorkflowClient --> MockedEmbeddingsApi
    MockedApiWorkflowClient --> MockedSamplingsApi
    MockedApiWorkflowClient --> MockedJobsApi
    MockedApiWorkflowClient --> MockedTagsApi
    MockedApiWorkflowClient --> MockedSamplesApi
    MockedApiWorkflowClient --> MockedDatasetsApi
    MockedApiWorkflowClient --> MockedDatasourcesApi
    MockedApiWorkflowClient --> MockedComputeWorkerApi
    MockedApiWorkflowClient --> MockedScoresApi
    MockedApiWorkflowClient --> MockedMappingsApi
    
    MockedDatasetsApi --> DatasetState
    MockedSamplesApi --> SampleState
    MockedComputeWorkerApi --> WorkerState
    MockedDatasourcesApi --> DatasourceState
```

**Sources:** [tests/api_workflow/mocked_api_workflow_client.py:1033-1056]()

### Key Mocking Components

Each mocked API class maintains in-memory state and returns realistic data structures:

| Mocked Class | Purpose | Key State |
|--------------|---------|-----------|
| `MockedDatasetsApi` | Dataset CRUD operations | `datasets`, `shared_datasets` |
| `MockedSamplesApi` | Sample management | `sample_create_requests` |
| `MockedEmbeddingsApi` | Embedding operations | `embeddings` list |
| `MockedTagsApi` | Tag creation and retrieval | Generates tag data on-the-fly |
| `MockedComputeWorkerApi` | Worker registration and runs | `_compute_worker_runs`, `_registered_workers` |
| `MockedDatasourcesApi` | Datasource configuration | `_datasources`, `_processed_until_timestamp` |
| `MockedJobsApi` | Job status polling | Simulates job completion after 3 calls |
| `MockedMappingsApi` | Sample filename mappings | `sample_names` |

**Sources:** [tests/api_workflow/mocked_api_workflow_client.py:100-829]()

### Mocking File Uploads

File upload operations are mocked by replacing the `requests.put` method:

```mermaid
graph LR
    Client["ApiWorkflowClient"]
    SignedURL["upload_file_with_signed_url"]
    MockedPut["mocked_request_put"]
    Validation["Validates:<br/>- URL is string<br/>- Content starts with 'filenames'<br/>- Returns 200"]
    
    Client --> SignedURL
    SignedURL --> MockedPut
    MockedPut --> Validation
```

The mocked PUT request validates that data is provided correctly without performing actual network operations.

**Sources:** [tests/api_workflow/mocked_api_workflow_client.py:1001-1008](), [tests/api_workflow/mocked_api_workflow_client.py:1055]()

### Test Data Constants

Tests use predefined constants for consistency:
- `N_FILES_ON_SERVER = 100` - Number of files available in mocked server
- Generated IDs via `utils.generate_id()` for realistic ID patterns

**Sources:** [tests/api_workflow/mocked_api_workflow_client.py:97]()

---

## CI/CD Workflows

The CI/CD system uses GitHub Actions with multiple workflows for different testing purposes.

### Change Detection Strategy

All test workflows use the `dorny/paths-filter` action to skip expensive operations when only documentation changes:

```mermaid
graph LR
    Push["Push/PR Event"]
    Filter["dorny/paths-filter"]
    Analyze["Analyze git diff"]
    Decision{"Code changed?"}
    RunTests["Run Test Job"]
    SkipTests["Skip Test Job"]
    
    Push --> Filter
    Filter --> Analyze
    Analyze --> Decision
    Decision -->|Yes| RunTests
    Decision -->|No| SkipTests
```

The filter excludes:
- `docs/**` - Documentation changes
- `examples/**` - Example script changes (except for CLI tests)
- `benchmarks/**` - Benchmark code changes

**Sources:** [.github/workflows/test.yml:11-27](), [.github/workflows/test_minimal_deps.yml:11-27]()

### Main Unit Test Workflow

**File:** `.github/workflows/test.yml`

**Triggers:**
- Push to `master` branch
- Pull requests
- Manual workflow dispatch

**Test Matrix:**

| Python Version | Dependencies | Coverage | Purpose |
|----------------|--------------|----------|---------|
| 3.7 | pinned-extras | No | Minimum version compatibility |
| 3.12 | pinned-extras | Yes | Current version with coverage tracking |

**Execution Flow:**

```mermaid
graph TB
    Trigger["Trigger: push/PR/manual"]
    DetectChanges["Detect Code Changes<br/>dorny/paths-filter"]
    Changed{"Code changed?"}
    SetupEnv["Setup Environment<br/>- install-uv<br/>- reset-venv<br/>- install-pinned-extras"]
    
    subgraph "Python 3.7"
        RunPytest37["Run Pytest<br/>python -m pytest -s -v --runslow"]
    end
    
    subgraph "Python 3.12"
        RunPytestCov["Run Pytest with Coverage<br/>pytest --cov=./lightly --cov-report=xml"]
        UploadCodecov["Upload Coverage to Codecov"]
    end
    
    Trigger --> DetectChanges
    DetectChanges --> Changed
    Changed -->|Yes| SetupEnv
    Changed -->|No| Skip["Skip Tests"]
    SetupEnv --> RunPytest37
    SetupEnv --> RunPytestCov
    RunPytestCov --> UploadCodecov
```

**Environment Variables:**
- `LIGHTLY_SERVER_LOCATION="localhost:-1"` - Disables real API connections

**Sources:** [.github/workflows/test.yml:1-76]()

### CLI Testing Workflow

**File:** `.github/workflows/test_setup.yml`

Tests that CLI commands are properly registered and functional:

**Commands Tested:**
- `lightly-crop --help`
- `lightly-ssl-train --help`
- `lightly-embed --help`
- `lightly-magic --help`
- `lightly-download --help`
- `lightly-version`

**Functional Test:**
Downloads a small clothing dataset and runs full training + embedding pipeline to verify end-to-end CLI functionality.

**Sources:** [.github/workflows/test_setup.yml:49-67]()

### Minimal Dependency Tests

**File:** `.github/workflows/test_minimal_deps.yml`

**Purpose:** Ensures the package doesn't have hidden dependencies and can function with minimal installs.

**Test Matrix:**

| Dependency Set | Description |
|----------------|-------------|
| `minimal` | Core package dependencies only |
| `minimal-extras` | Core + optional extras |

**Special Setup:**
- Installs `libavformat-dev` and `libavdevice-dev` for PyAV (versions < 9.0 lack FFMPEG wheels)
- Uses specific `libssh-gcrypt-4=0.9.6-2build1` to avoid 404 errors

**Sources:** [.github/workflows/test_minimal_deps.yml:1-58]()

### Unmocked Integration Tests

**File:** `.github/workflows/tests_unmocked.yml`

**Trigger:** Manual only (`workflow_dispatch`)

**Why Manual Only:**
1. Quota concerns (3000 minute limit for pip package)
2. Tests depend on unreliable staging API
3. Execution takes ~10 minutes
4. Already extensive unit test coverage

Tests run against actual Lightly staging server with real API token.

**Sources:** [.github/workflows/tests_unmocked.yml:1-34]()

### Weekly Dependency Testing

**File:** `.github/workflows/weekly_dependency_test.yml`

**Schedule:** Every Thursday at 22:00 UTC

**Purpose:** Detect upstream dependency breakages early by always installing latest versions.

**Execution:**
1. Fresh environment with Python 3.12
2. Install with `make install-latest` (no version pinning)
3. Run full test suite
4. Slack notification on pass/fail

**Notification:**
```mermaid
graph LR
    WeeklyRun["Weekly Test Run"]
    TestOutcome{"Outcome"}
    SlackWebhook["Slack Webhook"]
    
    WeeklyRun --> TestOutcome
    TestOutcome -->|Success| SlackWebhook
    TestOutcome -->|Failure| SlackWebhook
    
    SlackWebhook --> TeamNotification["Team Notified<br/>SLACK_WEBHOOK_NIGHTLY"]
```

**Sources:** [.github/workflows/weekly_dependency_test.yml:1-42]()

### Code Format and Type Checking

**File:** `.github/workflows/test_code_format.yml`

**Runs on:** Python 3.7 and 3.12

**Checks:**
1. **Format Check** - `make format-check`
   - `black` for code formatting
   - `isort` for import sorting
2. **Type Check** - `make type-check`
   - `mypy` in strict mode

**Sources:** [.github/workflows/test_code_format.yml:1-42]()

### API-Only Installation Test

**File:** `.github/workflows/test_api_deps_only.yml`

**Purpose:** Verifies that API client can be used without full package dependencies.

**Test:** Imports and instantiates `ApiWorkflowClient` with minimal dependencies.

```python
from lightly.api import ApiWorkflowClient
ApiWorkflowClient(token='abc')
```

**Sources:** [.github/workflows/test_api_deps_only.yml:1-53]()

---

## Dependency Management Strategy

The project uses multiple dependency installation targets to balance reproducibility and upstream compatibility:

```mermaid
graph TB
    subgraph "Dependency Profiles"
        Pinned["install-pinned<br/>Exact versions<br/>Reproducible builds"]
        PinnedExtras["install-pinned-extras<br/>Pinned + optional deps"]
        Minimal["install-minimal<br/>Core dependencies only"]
        MinimalExtras["install-minimal-extras<br/>Core + extras minimum"]
        Latest["install-latest<br/>Latest compatible versions"]
        APIOnly["install-api-only<br/>API client only"]
    end
    
    subgraph "Use Cases"
        CI["CI Regular Tests"]
        DevEnv["Development"]
        DepCheck["Dependency Validation"]
        UpstreamCheck["Upstream Compatibility"]
        LightweightAPI["Lightweight Integration"]
    end
    
    CI --> PinnedExtras
    DevEnv --> PinnedExtras
    DepCheck --> Minimal
    DepCheck --> MinimalExtras
    UpstreamCheck --> Latest
    LightweightAPI --> APIOnly
```

**Sources:** [.github/workflows/test.yml:52-53](), [.github/workflows/test_minimal_deps.yml:44-52](), [.github/workflows/weekly_dependency_test.yml:24-27]()

---

## Release Pipeline

The release process consists of building distribution packages, uploading to PyPI, and notifying stakeholders.

### PyPI Release Workflow

**File:** `.github/workflows/release_pypi.yml`

**Trigger:** Manual (`workflow_dispatch`)

**Process:**

```mermaid
graph TB
    Manual["Manual Trigger"]
    Checkout["Checkout Code<br/>fetch-depth: 0"]
    GetLatestTag["Get Latest Release Tag<br/>git describe --tags"]
    CheckoutTag["Checkout Tag"]
    SetupPython["Setup Python 3.12"]
    
    subgraph "Build"
        InstallTools["Install:<br/>- wheel<br/>- twine<br/>- build"]
        MakeDist["make dist<br/>Build wheel + sdist"]
    end
    
    Upload["Upload to PyPI<br/>twine upload"]
    
    subgraph "Notification"
        EmojiConvert["Convert outcome to emoji<br/>✓ or ✗"]
        SlackNotify["Slack Notification<br/>SLACK_WEBHOOK_RELEASES"]
    end
    
    Manual --> Checkout
    Checkout --> GetLatestTag
    GetLatestTag --> CheckoutTag
    CheckoutTag --> SetupPython
    SetupPython --> InstallTools
    InstallTools --> MakeDist
    MakeDist --> Upload
    Upload --> EmojiConvert
    EmojiConvert --> SlackNotify
```

**Credentials:**
- `PYPI_USER_NAME` - PyPI username (secret)
- `PYPI_PASSWORD` - PyPI password (secret)
- `SLACK_WEBHOOK_RELEASES` - Internal team webhook (secret)

**Sources:** [.github/workflows/release_pypi.yml:1-58]()

### Community Notification

**File:** `.github/workflows/discord_release_notification.yml`

**Trigger:** Release published (GitHub release event)

**Process:**
1. Extract release metadata (name, tag, URL, body)
2. Truncate description at `<!-- STOP DISCORD MESSAGE -->` comment
3. Format as JSON for webhook
4. POST to Discord webhook

**Message Format:**
```json
{
  "username": "Lightly",
  "avatar_url": "https://avatars.githubusercontent.com/u/50146475",
  "content": "Lightly {TAG} has been released!",
  "embeds": [{
    "title": "{RELEASE_NAME}",
    "url": "{RELEASE_URL}",
    "color": 5814783,
    "description": "{TRUNCATED_BODY}"
  }]
}
```

**Sources:** [.github/workflows/discord_release_notification.yml:1-42]()

---

## Test Execution Flow

### Typical Test Execution

```mermaid
graph TB
    Start["Test Execution Start"]
    EnvSetup["Environment Setup<br/>make install-uv reset-venv"]
    InstallDeps["Install Dependencies<br/>make install-pinned-extras"]
    SetEnvVar["Set Environment Variables<br/>LIGHTLY_SERVER_LOCATION=localhost:-1"]
    
    subgraph "Pytest Execution"
        Discovery["Test Discovery<br/>pytest -s -v --runslow"]
        SetupMocks["Setup Mocks<br/>MockedApiWorkflowClient"]
        RunTests["Run Test Cases"]
        Assertions["Assertions & Validations"]
    end
    
    subgraph "Coverage (Python 3.12 only)"
        CollectCoverage["Collect Coverage<br/>pytest-cov"]
        GenerateXML["Generate XML Report"]
        UploadCodecov["Upload to Codecov"]
    end
    
    Teardown["Cleanup"]
    
    Start --> EnvSetup
    EnvSetup --> InstallDeps
    InstallDeps --> SetEnvVar
    SetEnvVar --> Discovery
    Discovery --> SetupMocks
    SetupMocks --> RunTests
    RunTests --> Assertions
    Assertions --> CollectCoverage
    CollectCoverage --> GenerateXML
    GenerateXML --> UploadCodecov
    UploadCodecov --> Teardown
```

**Sources:** [.github/workflows/test.yml:49-75]()

### Example Test Pattern

Tests typically follow this structure:

```mermaid
graph TB
    TestClass["Test Class<br/>Inherits MockedApiWorkflowSetup"]
    SetupMethod["setUp()<br/>Initialize MockedApiWorkflowClient"]
    
    subgraph "Test Methods"
        TestMethod1["test_register_compute_worker()<br/>Call API method"]
        Assertions1["Assert response structure"]
        
        TestMethod2["test_with_mock()<br/>Override specific behavior"]
        MockPatch["mock.patch() specific method"]
        Assertions2["Assert expected calls"]
    end
    
    TestClass --> SetupMethod
    SetupMethod --> TestMethod1
    TestMethod1 --> Assertions1
    SetupMethod --> TestMethod2
    TestMethod2 --> MockPatch
    MockPatch --> Assertions2
```

**Example Test Methods:**
- `test_register_compute_worker()` - Tests worker registration returns valid ID
- `test_create_compute_worker_config()` - Tests config creation with nested structures
- `test_schedule_compute_worker_run()` - Tests run scheduling with priorities and labels
- `test_get_compute_worker_state_and_message_OPEN()` - Tests state retrieval logic

**Sources:** [tests/api_workflow/test_api_workflow_compute_worker.py:61-77](), [tests/api_workflow/test_api_workflow_compute_worker.py:506-536]()

---

## Test Organization

### Test Directory Structure

```mermaid
graph TB
    TestsRoot["tests/"]
    
    APIWorkflow["api_workflow/<br/>API client tests"]
    MockedClient["mocked_api_workflow_client.py<br/>Mocking infrastructure"]
    TestFiles["test_api_workflow*.py<br/>Test implementations"]
    
    UnmockedTests["UNMOCKED_end2end_tests/<br/>Integration tests"]
    RunScript["run_all_unmocked_tests.sh"]
    
    OtherTests["Other test modules"]
    
    TestsRoot --> APIWorkflow
    APIWorkflow --> MockedClient
    APIWorkflow --> TestFiles
    TestsRoot --> UnmockedTests
    UnmockedTests --> RunScript
    TestsRoot --> OtherTests
```

**Key Test Files:**
- `tests/api_workflow/mocked_api_workflow_client.py` - Mock implementations
- `tests/api_workflow/test_api_workflow.py` - General client tests
- `tests/api_workflow/test_api_workflow_compute_worker.py` - Worker tests
- `tests/api_workflow/test_api_workflow_datasets.py` - Dataset tests
- `tests/UNMOCKED_end2end_tests/run_all_unmocked_tests.sh` - Integration test runner

**Sources:** [tests/api_workflow/mocked_api_workflow_client.py:1-1258](), [tests/api_workflow/test_api_workflow.py:1-121](), [tests/api_workflow/test_api_workflow_datasets.py:1-509]()

---

## Configuration Validation Testing

Tests extensively validate configuration serialization and deserialization to catch schema errors early:

```mermaid
graph TB
    ConfigDict["Configuration Dictionary<br/>worker_config, lightly_config,<br/>selection_config"]
    
    SnakeToCamel["_snake_to_camel_case()<br/>Convert keys to camelCase"]
    Deserialize["_get_deserialize()<br/>ApiClient deserialization"]
    
    ValidateConfig["_validate_config()<br/>Check all keys exist"]
    
    ConfigObject["Pydantic Model Instance<br/>DockerWorkerConfigV4"]
    
    subgraph "Validation"
        CheckKeys["Check dict keys match<br/>model attributes"]
        SuggestMatch["difflib.get_close_matches()<br/>Suggest corrections"]
        RaiseError["InvalidConfigurationError"]
    end
    
    ConfigDict --> SnakeToCamel
    SnakeToCamel --> Deserialize
    Deserialize --> ConfigObject
    ConfigDict --> ValidateConfig
    ConfigObject --> ValidateConfig
    ValidateConfig --> CheckKeys
    CheckKeys -->|Invalid key| SuggestMatch
    SuggestMatch --> RaiseError
```

**Test Coverage:**
- Valid config creation
- Extra key detection with suggestions
- Nested config validation
- Selection config from dict conversion
- AutoTask type validation

**Sources:** [lightly/api/api_workflow_compute_worker.py:699-729](), [tests/api_workflow/test_api_workflow_compute_worker.py:215-266](), [tests/api_workflow/test_api_workflow_compute_worker.py:340-364]()

---

## Summary

The Lightly testing and CI/CD infrastructure provides comprehensive quality assurance through:

1. **Multi-layered Testing** - Unit, integration, minimal dependency, and format checks
2. **Sophisticated Mocking** - Full API mocking system for fast, reliable tests
3. **Smart Change Detection** - Skip expensive operations for documentation changes
4. **Matrix Testing** - Multiple Python versions and dependency configurations
5. **Coverage Tracking** - Code coverage monitoring with Codecov integration
6. **Automated Releases** - Streamlined PyPI publishing with stakeholder notifications
7. **Upstream Monitoring** - Weekly checks for dependency compatibility

This architecture ensures code quality while managing practical constraints around API quotas, execution time, and resource usage.