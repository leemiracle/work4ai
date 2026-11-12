<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/object-edit · page 3 Data System · fetched 2026-10-26 -->

# Data System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [ldm/data/__init__.py](ldm/data/__init__.py)
- [ldm/data/base.py](ldm/data/base.py)
- [ldm/data/simple.py](ldm/data/simple.py)

</details>



## Purpose and Scope

The Data System is responsible for loading, preprocessing, and preparing image datasets for training and evaluation of the latent diffusion model. It provides unified interfaces for loading Objaverse 3D object datasets with task-specific annotations (rotation, translation, removal, insertion), as well as support for large-scale datasets like LAION-5B and standard computer vision datasets.

This document provides an overview of the data system architecture, core components, and data loading pipeline. For detailed information about:
- Base dataset classes and interfaces, see [Dataset Base Classes](#3.1)
- Objaverse task-specific loaders, see [Objaverse Dataset](#3.2)
- COCO, ImageNet, and LSUN loaders, see [Standard Computer Vision Datasets](#3.3)
- LAION-5B and WebDataset infrastructure, see [LAION and Large-Scale Datasets](#3.4)
- Specialized datasets (NeRF, inpainting, dummy datasets), see [Specialized Datasets](#3.5)

## System Architecture

The data system follows a hierarchical architecture with base classes providing common interfaces, task-specific dataset implementations, and infrastructure for efficient loading and preprocessing.

```mermaid
graph TB
    subgraph "ldm.data Package"
        BASE["base.py<br/>Txt2ImgIterableBaseDataset<br/>PRNGMixin"]
        SIMPLE["simple.py<br/>Objaverse Task Datasets"]
        LAION["laion.py<br/>LAION-5B Loaders"]
        COCO["coco.py<br/>COCO Dataset"]
        IMAGENET["imagenet.py<br/>ImageNet Dataset"]
        OTHER["Other Dataset Modules"]
    end
    
    subgraph "Task-Specific Classes"
        DATAMODULE["ObjaverseTaskDataModuleFromConfig"]
        ROTATE["ObjaverseDataRotation"]
        TRANSLATE["ObjaverseDataTranslation"]
        REMOVE["ObjaverseDataRemove"]
        INSERT["ObjaverseDataInsert"]
        MULTITASK["ObjaverseDataMultitask"]
    end
    
    subgraph "Infrastructure"
        WDS["webdataset.WebDataset"]
        WDLOADER["webdataset.WebLoader"]
        SAMPLER["DistributedSampler"]
        LIGHTNING["PyTorch Lightning<br/>DataModule Interface"]
    end
    
    subgraph "Preprocessing"
        TFORM["torchvision.transforms"]
        PREPROC["preprocess_image()<br/>preprocess_mask()"]
        GETSAMPLE["get_sample()"]
    end
    
    BASE -.inherits.-> SIMPLE
    BASE -.inherits.-> LAION
    
    SIMPLE --> DATAMODULE
    DATAMODULE --> ROTATE
    DATAMODULE --> TRANSLATE
    DATAMODULE --> REMOVE
    DATAMODULE --> INSERT
    DATAMODULE --> MULTITASK
    
    LIGHTNING -.interface.-> DATAMODULE
    
    DATAMODULE --> WDLOADER
    ROTATE --> WDS
    TRANSLATE --> WDS
    REMOVE --> WDS
    INSERT --> WDS
    MULTITASK --> WDS
    
    WDLOADER --> SAMPLER
    
    TFORM --> PREPROC
    PREPROC --> GETSAMPLE
    GETSAMPLE --> ROTATE
    GETSAMPLE --> TRANSLATE
    GETSAMPLE --> REMOVE
    GETSAMPLE --> INSERT
```

**Sources:** [ldm/data/base.py:1-41](), [ldm/data/simple.py:1-534]()

## Data Module and DataLoader Creation

The `ObjaverseTaskDataModuleFromConfig` class implements the PyTorch Lightning `DataModule` interface, providing a standardized way to create train, validation, and test dataloaders for different tasks.

```mermaid
graph LR
    CONFIG["OmegaConf Configuration<br/>task: rotate/translate/remove/insert"]
    
    DATAMODULE["ObjaverseTaskDataModuleFromConfig<br/>__init__()"]
    
    subgraph "DataLoader Creation Methods"
        TRAIN["train_dataloader()"]
        VAL["val_dataloader()"]
        TEST["test_dataloader()"]
    end
    
    subgraph "Dataset Instantiation"
        TASKMAP["task_classes dict:<br/>{rotate: ObjaverseDataRotation,<br/>translate: ObjaverseDataTranslation,<br/>remove: ObjaverseDataRemove,<br/>insert: ObjaverseDataInsert,<br/>multitask: ObjaverseDataMultitask}"]
    end
    
    subgraph "Data Splits"
        TRAIN_DS["Task Dataset<br/>split=train, seen"]
        VAL_SEEN["Task Dataset<br/>split=val, seen"]
        VAL_UNSEEN["Task Dataset<br/>split=val, unseen"]
        TEST_SEEN["Task Dataset<br/>split=test, seen"]
        TEST_UNSEEN["Task Dataset<br/>split=test, unseen"]
    end
    
    CONFIG --> DATAMODULE
    DATAMODULE --> TASKMAP
    
    TRAIN --> TASKMAP
    VAL --> TASKMAP
    TEST --> TASKMAP
    
    TRAIN --> TRAIN_DS
    VAL --> VAL_SEEN
    VAL --> VAL_UNSEEN
    TEST --> TEST_SEEN
    TEST --> TEST_UNSEEN
    
    TRAIN_DS --> SAMPLER["DistributedSampler"]
    SAMPLER --> LOADER["WebLoader<br/>batch_size, num_workers"]
```

**Sources:** [ldm/data/simple.py:31-121]()

### DataModule Configuration

| Parameter | Type | Description |
|-----------|------|-------------|
| `root_dir` | str | Root directory containing task datasets |
| `task` | str | Task name: "rotate", "translate", "remove", "insert", or "multitask" |
| `batch_size` | int | Batch size for dataloaders |
| `num_workers` | int | Number of worker processes for data loading (default: 4) |
| `num_samples` | int | Maximum number of samples to load (default: 100000) |
| `train` | dict | Training dataset configuration |
| `validation` | dict | Validation dataset configuration |

**Sources:** [ldm/data/simple.py:32-39]()

## Task-Specific Dataset Classes

Each task (rotation, translation, removal, insertion) has a dedicated dataset class that handles task-specific data loading, preprocessing, and metadata interpretation.

### Dataset Class Hierarchy

```mermaid
graph TB
    DATASET["torch.utils.data.Dataset"]
    
    ROTATE["ObjaverseDataRotation<br/>rotation_angle → T tensor<br/>prompt: 'rotate the {object}'"]
    TRANSLATE["ObjaverseDataTranslation<br/>end_location_2d → T tensor<br/>prompt: 'move the {object}'"]
    REMOVE["ObjaverseDataRemove<br/>T = [0,0,0,0]<br/>prompt: 'remove the {object}'"]
    INSERT["ObjaverseDataInsert<br/>Uses inverted remove data<br/>prompt: 'insert the {object}'"]
    MULTITASK["ObjaverseDataMultitask<br/>Aggregates all tasks<br/>indices: [(task, idx), ...]"]
    
    DATASET -.inherits.-> ROTATE
    DATASET -.inherits.-> TRANSLATE
    DATASET -.inherits.-> REMOVE
    DATASET -.inherits.-> INSERT
    DATASET -.inherits.-> MULTITASK
    
    MULTITASK --> ROTATE
    MULTITASK --> TRANSLATE
    MULTITASK --> REMOVE
    MULTITASK --> INSERT
```

**Sources:** [ldm/data/simple.py:123-484]()

### Task-Specific T Tensor Format

Each task encodes its parameters into a 4-element tensor `T` used for conditioning the diffusion model:

| Task | T Tensor Format | Components | Source |
|------|----------------|------------|---------|
| Rotation | `[π/2, sin(θ), cos(θ), 0]` | Matches Zero123 format with azimuth angle | [ldm/data/simple.py:167-170]() |
| Translation | `[0, x, y, 0]` | x,y are normalized 2D coordinates | [ldm/data/simple.py:246-248]() |
| Removal | `[0, 0, 0, 0]` | No transformation parameters | [ldm/data/simple.py:323-325]() |
| Insertion | `[0, x, y, 0]` | x,y are insertion location coordinates | [ldm/data/simple.py:395-397]() |

**Sources:** [ldm/data/simple.py:167-170](), [ldm/data/simple.py:246-248](), [ldm/data/simple.py:323-325](), [ldm/data/simple.py:395-397]()

## Dataset Directory Structure

Task datasets are organized in a hierarchical directory structure:

```
{root_dir}/
├── rotate/
│   ├── train/
│   │   └── {uid}/
│   │       ├── 1.png              # Condition image
│   │       ├── 2.png              # Target image
│   │       ├── 1_mask.png         # Condition mask
│   │       ├── 2_mask.png         # Target mask
│   │       └── metadata.json      # Task metadata
│   ├── val/
│   │   ├── seen/
│   │   └── unseen/
│   └── test/
│       ├── seen/
│       └── unseen/
├── translate/
│   └── (same structure)
├── remove/
│   └── (same structure)
└── insert/
    └── (uses remove data, inverted)
```

**Sources:** [ldm/data/simple.py:142-147](), [ldm/data/simple.py:222-225](), [ldm/data/simple.py:299-302](), [ldm/data/simple.py:372-377]()

## Data Loading and Preprocessing Pipeline

The data loading pipeline processes raw images and metadata into tensors suitable for model training.

```mermaid
sequenceDiagram
    participant DS as "Dataset.__getitem__(index)"
    participant GS as "get_sample()"
    participant PI as "preprocess_image()"
    participant PM as "preprocess_mask()"
    participant LI as "load_image()"
    participant TFORM as "image_transforms"
    
    DS->>GS: Call with root_dir, uid, transforms
    
    GS->>LI: Load 1.png (condition)
    LI-->>GS: PIL Image
    GS->>PI: preprocess_image(cond_im, tform)
    PI->>PI: Convert to RGB
    PI->>TFORM: Apply transforms:<br/>Resize → ToTensor → Normalize
    TFORM-->>PI: Tensor [-1, 1] range
    PI-->>GS: cond_im tensor
    
    GS->>LI: Load 2.png (target)
    LI-->>GS: PIL Image
    GS->>PI: preprocess_image(target_im, tform)
    PI-->>GS: target_im tensor
    
    GS->>PM: Load 1_mask.png
    PM->>PM: Convert RGBA to binary mask<br/>Extract object pixels (color matching)
    PM-->>GS: mask_cond tensor
    
    GS->>PM: Load 2_mask.png
    PM-->>GS: mask_target tensor
    
    GS->>GS: Load metadata.json
    
    GS-->>DS: (cond_im, target_im,<br/>mask_cond, mask_target, metadata)
    
    DS->>DS: Extract task parameters<br/>Create T tensor<br/>Format prompt
    DS-->>DS: Return data dict
```

**Sources:** [ldm/data/simple.py:524-532](), [ldm/data/simple.py:487-489](), [ldm/data/simple.py:491-516](), [ldm/data/simple.py:519-522]()

### Image Transform Pipeline

The image transform pipeline normalizes images to the expected input format:

1. **Resize:** Images are resized to the configured size (typically 256×256)
2. **ToTensor:** Convert PIL Image to PyTorch tensor (range [0, 1])
3. **Normalize:** Scale to range [-1, 1] and rearrange dimensions to (H, W, C)

```python
# From ldm/data/simple.py:58-63
image_transforms = [torchvision.transforms.Resize(dataset_config.image_transforms.size)]
image_transforms.extend([
    transforms.ToTensor(),
    transforms.Lambda(lambda x: rearrange(x * 2. - 1., 'c h w -> h w c'))
])
self.image_transforms = torchvision.transforms.Compose(image_transforms)
```

**Sources:** [ldm/data/simple.py:57-63]()

## Data Dictionary Format

Each dataset returns a dictionary containing all necessary information for training:

```mermaid
graph TB
    DATA["data dict"]
    
    MASK_COND["mask_cond<br/>Binary mask for condition image"]
    MASK_TARGET["mask_target<br/>Binary mask for target image"]
    UID["uid<br/>Unique sample identifier"]
    IMAGE_TARGET["image_target<br/>Target image tensor"]
    COND["cond dict"]
    T_TENSOR["T<br/>Task parameter tensor [4]"]
    LOG_KEY["log_key<br/>Dataset split identifier"]
    
    COND_IMAGE["image<br/>Condition image tensor"]
    COND_TEXT["text<br/>Task prompt string"]
    
    DATA --> MASK_COND
    DATA --> MASK_TARGET
    DATA --> UID
    DATA --> IMAGE_TARGET
    DATA --> COND
    DATA --> T_TENSOR
    DATA --> LOG_KEY
    
    COND --> COND_IMAGE
    COND --> COND_TEXT
```

**Sources:** [ldm/data/simple.py:190-200](), [ldm/data/simple.py:267-277](), [ldm/data/simple.py:340-350](), [ldm/data/simple.py:416-426]()

## Object Annotations and Prompts

Object descriptions are loaded from a JSON file `objaverse_cat_descriptions_64k.json` which maps object UIDs to natural language descriptions. These descriptions are formatted into task-specific prompts.

### Prompt Templates by Task

| Task | Template | Example |
|------|----------|---------|
| Rotation | `"rotate the {description}"` | "rotate the red chair" |
| Translation | `"move the {description}"` | "move the blue lamp" |
| Removal | `"remove the {description}"` | "remove the wooden table" |
| Insertion | `"insert the {description}"` | "insert the green plant" |

**Sources:** [ldm/data/simple.py:152-157](), [ldm/data/simple.py:186-187](), [ldm/data/simple.py:235](), [ldm/data/simple.py:312](), [ldm/data/simple.py:338-339](), [ldm/data/simple.py:414-415]()

## Mask Preprocessing

Masks are stored as RGBA images with color-coded object labels. The preprocessing pipeline converts these colored masks to binary masks identifying the primary object.

```mermaid
graph LR
    RGBA["RGBA Mask Image<br/>Color-coded objects"]
    
    RESHAPE["Reshape to (N, 4)<br/>N = num_pixels"]
    
    COLOR_MAP["Compare against<br/>9 predefined colors:<br/>red, blue, green, purple,<br/>orange, yellow, brown,<br/>pink, gray"]
    
    DISTANCE["Calculate L2 distance<br/>to each color"]
    
    ARGMIN["Find closest color<br/>per pixel"]
    
    EXTRACT["Extract pixels with<br/>color index 1 (blue)"]
    
    BINARY["Binary mask tensor<br/>{0, 1}"]
    
    RGBA --> RESHAPE
    RESHAPE --> COLOR_MAP
    COLOR_MAP --> DISTANCE
    DISTANCE --> ARGMIN
    ARGMIN --> EXTRACT
    EXTRACT --> BINARY
```

The mask color map defines 9 standard colors (red, blue, green, purple, orange, yellow, brown, pink, gray). The preprocessing identifies which pixels correspond to the primary object (color index 1, blue) and creates a binary mask.

**Sources:** [ldm/data/simple.py:491-516]()

## Multitask Dataset Aggregation

The `ObjaverseDataMultitask` class aggregates all four task datasets into a single unified dataset for training models on multiple tasks simultaneously.

```mermaid
graph TB
    MULTI["ObjaverseDataMultitask"]
    
    TASKS["self.tasks = [rotate, translate,<br/>remove, insert]"]
    
    CLASSES["self.task_classes = {<br/>rotate: ObjaverseDataRotation,<br/>translate: ObjaverseDataTranslation,<br/>remove: ObjaverseDataRemove,<br/>insert: ObjaverseDataInsert}"]
    
    DATASETS["self.task_datasets = {<br/>task: TaskClass(params)<br/>for task in tasks}"]
    
    INDICES["self.indices = [<br/>(rotate, 0), (rotate, 1), ...,<br/>(translate, 0), ...,<br/>(remove, 0), ...,<br/>(insert, 0), ...]"]
    
    GETITEM["__getitem__(index)<br/>→ task, idx = indices[index]<br/>→ return task_datasets[task][idx]"]
    
    MULTI --> TASKS
    MULTI --> CLASSES
    MULTI --> DATASETS
    MULTI --> INDICES
    MULTI --> GETITEM
    
    DATASETS --> GETITEM
    INDICES --> GETITEM
```

The multitask dataset creates a flat index mapping that interleaves samples from all tasks. When accessed, it routes to the appropriate task-specific dataset.

**Sources:** [ldm/data/simple.py:430-484]()

## WebDataset Integration

The data system uses WebDataset for efficient streaming and distributed loading:

1. **WebDataset Wrapping:** Task datasets are wrapped in `webdataset.WebDataset` for streaming
2. **WebLoader:** `webdataset.WebLoader` provides a DataLoader-compatible interface
3. **DistributedSampler:** Ensures each GPU receives different data in distributed training

```python
# From ldm/data/simple.py:75-76
sampler = DistributedSampler(dataset)
return wds.WebLoader(dataset, batch_size=self.batch_size, 
                     num_workers=self.num_workers, shuffle=False, sampler=sampler)
```

**Sources:** [ldm/data/simple.py:66-76](), [ldm/data/simple.py:87-97](), [ldm/data/simple.py:110-121]()

## Error Handling

All task dataset classes implement fallback error handling: if loading a sample fails, they fall back to loading the first sample (`self.samples[0]`). This prevents training crashes from corrupted or missing data files.

```python
# Pattern used in all task datasets
try:
    sample_dir = self.samples[index]
    cond_im, target_im, mask_cond, mask_target, metadata = get_sample(...)
except Exception as e: 
    sample_dir = self.samples[0]
    cond_im, target_im, mask_cond, mask_target, metadata = get_sample(...)
```

**Sources:** [ldm/data/simple.py:176-181](), [ldm/data/simple.py:253-258](), [ldm/data/simple.py:331-336](), [ldm/data/simple.py:403-408]()

## Base Dataset Classes

The `ldm.data.base` module provides foundational classes used across all dataset implementations:

### Txt2ImgIterableBaseDataset

An abstract base class defining the interface for iterable text-to-image datasets. It provides:
- `num_records`: Total number of examples
- `valid_ids`: Set of valid sample identifiers
- `size`: Image size
- `__len__()`: Returns number of records
- `__iter__()`: Abstract method to be implemented by subclasses

**Sources:** [ldm/data/base.py:7-26]()

### PRNGMixin

A mixin class providing process-safe random number generation. The `prng` property returns a `numpy.RandomState` that reinitializes whenever the process ID changes, preventing synchronized sampling in multiprocessing scenarios.

**Sources:** [ldm/data/base.py:28-41]()

## Summary

The Data System provides a modular, task-oriented architecture for loading and preprocessing Objaverse 3D object datasets. Key features include:

- **PyTorch Lightning Integration:** `ObjaverseTaskDataModuleFromConfig` provides standardized DataModule interface
- **Task-Specific Datasets:** Dedicated classes for rotation, translation, removal, and insertion tasks
- **Unified T Tensor Format:** Task parameters encoded as 4-element tensors for model conditioning
- **Flexible Data Splits:** Support for train/val/test splits with seen/unseen categories
- **WebDataset Infrastructure:** Efficient streaming and distributed loading
- **Robust Error Handling:** Fallback mechanisms prevent training crashes
- **Consistent Preprocessing:** Standardized image normalization and mask extraction

For implementation details of specific dataset types, refer to the child pages in the table of contents.

---

