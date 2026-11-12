<!-- source: DeepWiki mcp.deepwiki.com · repo yoshitomo-matsubara/torchdistill · page 3 Components · fetched 2026-10-21 -->

# Components

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [tests/registry_test.py](tests/registry_test.py)
- [torchdistill/datasets/__init__.py](torchdistill/datasets/__init__.py)
- [torchdistill/datasets/registry.py](torchdistill/datasets/registry.py)
- [torchdistill/datasets/sample_loader.py](torchdistill/datasets/sample_loader.py)
- [torchdistill/datasets/util.py](torchdistill/datasets/util.py)
- [torchdistill/datasets/wrapper.py](torchdistill/datasets/wrapper.py)

</details>



This document covers the major component categories in torchdistill and their registration system. Components are the building blocks that can be dynamically selected and configured through YAML configuration files. The framework provides registries for datasets, models, loss functions, and optimization components.

For detailed information about the core registry architecture, see [Component Registry System](#2.3). For configuration-driven usage patterns, see [Configuration-Driven System](#2.1).

## Registry Pattern Overview

All components in torchdistill follow a consistent registry pattern that enables dynamic component selection and instantiation through decorators and lookup functions.

### Registry Architecture

```mermaid
graph TB
    subgraph "Registration Phase"
        DECORATOR_DATASET["@register_dataset"]
        DECORATOR_MODEL["@register_model"]
        DECORATOR_LOSS["@register_high_level_loss"]
        DECORATOR_OPTIM["@register_optimizer"]
        DECORATOR_TRANSFORM["@register_transform"]
        DECORATOR_WRAPPER["@register_dataset_wrapper"]
    end
    
    subgraph "Storage Layer"
        DATASET_DICT["DATASET_DICT"]
        MODEL_DICT["MODEL_DICT"]
        LOSS_DICT["HIGH_LEVEL_LOSS_DICT"]
        OPTIM_DICT["OPTIM_DICT"]
        TRANSFORM_DICT["TRANSFORM_DICT"]
        WRAPPER_DICT["DATASET_WRAPPER_DICT"]
    end
    
    subgraph "Retrieval Layer"
        GET_DATASET["get_dataset()"]
        GET_MODEL["get_model()"]
        GET_LOSS["get_high_level_loss()"]
        GET_OPTIM["get_optimizer()"]
        GET_TRANSFORM["get_transform()"]
        GET_WRAPPER["get_dataset_wrapper()"]
    end
    
    subgraph "Runtime Usage"
        YAML_CONFIG["YAML Configuration"]
        IMPORT_CALL["!import_call"]
        COMPONENT_INSTANTIATION["Component Instantiation"]
    end
    
    DECORATOR_DATASET --> DATASET_DICT
    DECORATOR_MODEL --> MODEL_DICT
    DECORATOR_LOSS --> LOSS_DICT
    DECORATOR_OPTIM --> OPTIM_DICT
    DECORATOR_TRANSFORM --> TRANSFORM_DICT
    DECORATOR_WRAPPER --> WRAPPER_DICT
    
    DATASET_DICT --> GET_DATASET
    MODEL_DICT --> GET_MODEL
    LOSS_DICT --> GET_LOSS
    OPTIM_DICT --> GET_OPTIM
    TRANSFORM_DICT --> GET_TRANSFORM
    WRAPPER_DICT --> GET_WRAPPER
    
    YAML_CONFIG --> IMPORT_CALL
    IMPORT_CALL --> GET_DATASET
    IMPORT_CALL --> GET_MODEL
    IMPORT_CALL --> GET_LOSS
    IMPORT_CALL --> GET_OPTIM
    IMPORT_CALL --> GET_TRANSFORM
    IMPORT_CALL --> GET_WRAPPER
    
    GET_DATASET --> COMPONENT_INSTANTIATION
    GET_MODEL --> COMPONENT_INSTANTIATION
    GET_LOSS --> COMPONENT_INSTANTIATION
    GET_OPTIM --> COMPONENT_INSTANTIATION
    GET_TRANSFORM --> COMPONENT_INSTANTIATION
    GET_WRAPPER --> COMPONENT_INSTANTIATION
```

Sources: [tests/registry_test.py:1-458](), [torchdistill/datasets/registry.py:1-360]()

### Registration Decorators

The registry system provides decorators for component registration that support both default and custom keys:

| Decorator | Purpose | Registry Dict |
|-----------|---------|---------------|
| `@register_dataset` | Dataset classes | `DATASET_DICT` |
| `@register_collate_func` | Collate functions | `COLLATE_FUNC_DICT` |
| `@register_sample_loader` | Sample loader classes | `SAMPLE_LOADER_DICT` |
| `@register_batch_sampler` | Batch sampler classes | `BATCH_SAMPLER_DICT` |
| `@register_transform` | Transform classes | `TRANSFORM_DICT` |
| `@register_dataset_wrapper` | Dataset wrapper classes | `DATASET_WRAPPER_DICT` |

Sources: [torchdistill/datasets/registry.py:16-267](), [tests/registry_test.py:20-173]()

## Dataset Management Components

Dataset management is handled through a multi-layered system of datasets, transforms, wrappers, and loaders that work together to provide flexible data processing pipelines.

### Dataset Component Hierarchy

```mermaid
graph TB
    subgraph "Core Dataset Layer"
        TORCHVISION_DATASETS["torchvision.datasets.*"]
        CUSTOM_DATASETS["Custom Dataset Classes"]
        REGISTERED_DATASETS["@register_dataset classes"]
    end
    
    subgraph "Dataset Wrapper Layer"
        BASE_WRAPPER["BaseDatasetWrapper"]
        CACHEABLE_WRAPPER["CacheableDataset"]
        CRD_WRAPPER["CRDDatasetWrapper"]
        SSKD_WRAPPER["SSKDDatasetWrapper"]
        CUSTOM_WRAPPERS["Custom Dataset Wrappers"]
    end
    
    subgraph "Transform Layer"
        TORCHVISION_TRANSFORMS["torchvision.transforms.*"]
        CUSTOM_TRANSFORMS["@register_transform classes"]
    end
    
    subgraph "Sample Loading Layer"
        DEFAULT_LOADER["default_loader"]
        JPEG_LOADER["JpegCompressionLoader"]
        CUSTOM_LOADERS["@register_sample_loader classes"]
    end
    
    subgraph "Data Loading Layer"
        COLLATE_FUNCS["Collate Functions"]
        BATCH_SAMPLERS["Batch Samplers"]
        DATA_LOADERS["DataLoader instances"]
    end
    
    TORCHVISION_DATASETS --> BASE_WRAPPER
    CUSTOM_DATASETS --> BASE_WRAPPER
    REGISTERED_DATASETS --> BASE_WRAPPER
    
    BASE_WRAPPER --> CACHEABLE_WRAPPER
    BASE_WRAPPER --> CRD_WRAPPER
    BASE_WRAPPER --> SSKD_WRAPPER
    BASE_WRAPPER --> CUSTOM_WRAPPERS
    
    TORCHVISION_TRANSFORMS --> CACHEABLE_WRAPPER
    CUSTOM_TRANSFORMS --> CACHEABLE_WRAPPER
    TORCHVISION_TRANSFORMS --> CRD_WRAPPER
    CUSTOM_TRANSFORMS --> CRD_WRAPPER
    
    DEFAULT_LOADER --> TORCHVISION_DATASETS
    JPEG_LOADER --> TORCHVISION_DATASETS
    CUSTOM_LOADERS --> TORCHVISION_DATASETS
    
    CACHEABLE_WRAPPER --> DATA_LOADERS
    CRD_WRAPPER --> DATA_LOADERS
    SSKD_WRAPPER --> DATA_LOADERS
    CUSTOM_WRAPPERS --> DATA_LOADERS
    
    COLLATE_FUNCS --> DATA_LOADERS
    BATCH_SAMPLERS --> DATA_LOADERS
```

Sources: [torchdistill/datasets/wrapper.py:27-159](), [torchdistill/datasets/sample_loader.py:11-32](), [torchdistill/datasets/util.py:69-119]()

### Dataset Wrapper Types

The framework provides several dataset wrapper implementations:

#### BaseDatasetWrapper
The base wrapper class that extends the original dataset to return supplementary data:

```python
# Returns (sample, target, supp_dict) instead of (sample, target)
def __getitem__(self, index):
    sample, target = self.org_dataset.__getitem__(index)
    return sample, target, dict()
```

#### CacheableDataset
Extends `BaseDatasetWrapper` to support cached data loading from disk:

```python
def __getitem__(self, index):
    sample, target, supp_dict = super().__getitem__(index)
    cache_file_path = os.path.join(self.cache_dir_path, self.idx2subath_func(index) + self.ext)
    if file_util.check_if_exists(cache_file_path):
        cached_data = torch.load(cache_file_path)
        supp_dict['cached_data'] = cached_data
    return sample, target, supp_dict
```

#### Specialized Knowledge Distillation Wrappers
- `CRDDatasetWrapper`: Provides contrastive samples for Contrastive Representation Distillation
- `SSKDDatasetWrapper`: Generates rotated samples for Self-Supervised Knowledge Distillation

Sources: [torchdistill/datasets/wrapper.py:27-159]()

### Data Loading Pipeline

The data loading pipeline integrates multiple components through the `build_data_loader` function:

```mermaid
graph LR
    subgraph "Configuration Input"
        DATASET_CONFIG["dataset config"]
        LOADER_CONFIG["data_loader config"]
    end
    
    subgraph "Dataset Construction"
        GET_DATASET_FUNC["get_dataset()"]
        DATASET_INSTANCE["Dataset Instance"]
        WRAPPER_APPLICATION["Dataset Wrapper Application"]
    end
    
    subgraph "Sampling Configuration"
        SAMPLER_CONFIG["sampler config"]
        BATCH_SAMPLER_CONFIG["batch_sampler config"]
        DISTRIBUTED_SAMPLER["DistributedSampler"]
        CUSTOM_SAMPLERS["Custom Samplers"]
    end
    
    subgraph "Final Data Loader"
        COLLATE_FUNC["get_collate_func()"]
        DATALOADER["DataLoader"]
    end
    
    DATASET_CONFIG --> GET_DATASET_FUNC
    GET_DATASET_FUNC --> DATASET_INSTANCE
    DATASET_INSTANCE --> WRAPPER_APPLICATION
    LOADER_CONFIG --> WRAPPER_APPLICATION
    
    WRAPPER_APPLICATION --> DISTRIBUTED_SAMPLER
    WRAPPER_APPLICATION --> CUSTOM_SAMPLERS
    SAMPLER_CONFIG --> CUSTOM_SAMPLERS
    BATCH_SAMPLER_CONFIG --> CUSTOM_SAMPLERS
    
    DISTRIBUTED_SAMPLER --> DATALOADER
    CUSTOM_SAMPLERS --> DATALOADER
    COLLATE_FUNC --> DATALOADER
```

Sources: [torchdistill/datasets/util.py:69-119]()

## Model Architecture Components

Model components are registered through the model registry system and include standard architectures, custom models, and auxiliary wrappers that modify model behavior during training.

### Model Registry Categories

| Registry | Purpose | Usage |
|----------|---------|-------|
| `MODEL_DICT` | Standard model architectures | Teacher/student models |
| `ADAPTATION_MODULE_DICT` | Feature adaptation modules | Dimension matching between teacher/student |
| `AUXILIARY_MODEL_WRAPPER_DICT` | Model behavior wrappers | Modify forward pass behavior |

Sources: [tests/registry_test.py:310-377]()

## Loss Function Components

Loss functions are organized in a hierarchical system with high-level composite losses, mid-level knowledge distillation losses, and low-level loss functions.

### Loss Function Hierarchy

| Level | Registry | Purpose |
|-------|----------|---------|
| High-level | `HIGH_LEVEL_LOSS_DICT` | Composite losses that combine multiple loss terms |
| Mid-level | `MIDDLE_LEVEL_LOSS_DICT` | Knowledge distillation specific losses |
| Low-level | PyTorch built-ins | Basic loss functions (CrossEntropy, MSE, etc.) |

Additional loss-related registries:
- `LOSS_WRAPPER_DICT`: Loss function wrappers
- `FUNC2EXTRACT_MODEL_OUTPUT_DICT`: Functions to extract specific outputs from models

Sources: [tests/registry_test.py:175-262]()

## Optimization Components

Optimization components include optimizers, learning rate schedulers, and related utilities for training configuration.

### Optimization Registry

| Registry | Purpose | Built-in Support |
|----------|---------|------------------|
| `OPTIM_DICT` | Optimizers | PyTorch optimizers |
| `SCHEDULER_DICT` | Learning rate schedulers | PyTorch schedulers |

Sources: [tests/registry_test.py:264-308]()

## Component Integration Flow

Components integrate through the configuration system and training pipeline:

```mermaid
graph TB
    subgraph "YAML Configuration"
        YAML_DATASETS["datasets: {...}"]
        YAML_MODELS["models: {...}"]
        YAML_LOSSES["train: loss: {...}"]
        YAML_OPTIM["train: optimizer: {...}"]
    end
    
    subgraph "Component Resolution"
        IMPORT_CALL_PROC["!import_call processing"]
        REGISTRY_LOOKUP["Registry lookups"]
        COMPONENT_INSTANTIATION["Component instantiation"]
    end
    
    subgraph "Training Pipeline"
        DISTILLATION_BOX["DistillationBox"]
        TRAINING_BOX["TrainingBox"]
        FORWARD_HOOKS["Forward hooks"]
        LOSS_COMPUTATION["Loss computation"]
        OPTIMIZATION["Optimization step"]
    end
    
    YAML_DATASETS --> IMPORT_CALL_PROC
    YAML_MODELS --> IMPORT_CALL_PROC
    YAML_LOSSES --> IMPORT_CALL_PROC
    YAML_OPTIM --> IMPORT_CALL_PROC
    
    IMPORT_CALL_PROC --> REGISTRY_LOOKUP
    REGISTRY_LOOKUP --> COMPONENT_INSTANTIATION
    
    COMPONENT_INSTANTIATION --> DISTILLATION_BOX
    COMPONENT_INSTANTIATION --> TRAINING_BOX
    
    DISTILLATION_BOX --> FORWARD_HOOKS
    TRAINING_BOX --> FORWARD_HOOKS
    FORWARD_HOOKS --> LOSS_COMPUTATION
    LOSS_COMPUTATION --> OPTIMIZATION
```

Sources: [torchdistill/datasets/util.py:122-143]()

This component system provides the foundation for torchdistill's modular architecture, enabling researchers to easily swap and configure different components for their knowledge distillation experiments.

---

