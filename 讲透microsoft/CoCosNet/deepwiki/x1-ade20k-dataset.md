<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/CoCosNet · extra page ADE20K Dataset · fetched 2026-10-26 -->

# ADE20K Dataset

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [data/ade20k_dataset.py](data/ade20k_dataset.py)
- [data/ade20k_ref_test.txt](data/ade20k_ref_test.txt)

</details>



## Purpose and Scope

This document covers the ADE20K dataset implementation in CoCosNet, specifically the `ADE20KDataset` class that enables mask-to-image translation for scene parsing tasks. The ADE20K dataset contains scene images with corresponding semantic segmentation masks across 150 object and scene categories.

For information about the broader dataset architecture and factory pattern, see [Dataset Architecture](#3.1). For other dataset implementations, see [Dataset Implementations](#3.2).

## Dataset Overview

The `ADE20KDataset` class provides integration with the ADE20K scene parsing dataset, enabling cross-domain correspondence learning between semantic masks and natural scene images. This implementation supports both training and inference phases with appropriate data splits and reference mappings.

```mermaid
graph TD
    subgraph "ADE20K Integration"
        ADE20K["ADE20KDataset"]
        PIX2PIX["Pix2pixDataset"]
        BASE["BaseDataset"]
        
        ADE20K --> PIX2PIX
        PIX2PIX --> BASE
    end
    
    subgraph "Core Functionality"
        MODIFY["modify_commandline_options()"]
        GET_PATHS["get_paths()"]
        GET_REF["get_ref()"]
        
        ADE20K --> MODIFY
        ADE20K --> GET_PATHS
        ADE20K --> GET_REF
    end
    
    subgraph "Data Sources"
        TRAIN_FOLDER["training/"]
        VAL_FOLDER["validation/"]
        REF_TRAIN["ade20k_ref.txt"]
        REF_TEST["ade20k_ref_test.txt"]
        
        GET_PATHS --> TRAIN_FOLDER
        GET_PATHS --> VAL_FOLDER
        GET_REF --> REF_TRAIN
        GET_REF --> REF_TEST
    end
```

Sources: [data/ade20k_dataset.py:9-61]()

## Class Structure and Configuration

The `ADE20KDataset` class inherits from `Pix2pixDataset` and customizes configuration options specific to scene parsing tasks. The class defines preprocessing parameters, image dimensions, and dataset-specific settings through the `modify_commandline_options` static method.

### Configuration Parameters

| Parameter | Training Value | Test Value | Purpose |
|-----------|---------------|------------|---------|
| `preprocess_mode` | `resize_and_crop` | `resize_and_crop` | Image preprocessing strategy |
| `load_size` | 286 | 256 | Initial image loading size |
| `crop_size` | 256 | 256 | Final cropped image size |
| `label_nc` | 150 | 150 | Number of semantic label classes |
| `contain_dontcare_label` | True | True | Handle undefined label regions |
| `cache_filelist_read` | False | False | Disable file list caching |

```mermaid
graph LR
    subgraph "Configuration Pipeline"
        PARSER["ArgumentParser"]
        PIX2PIX_OPTS["Pix2pixDataset.modify_commandline_options()"]
        ADE20K_OPTS["ADE20KDataset.modify_commandline_options()"]
        DEFAULTS["set_defaults()"]
        
        PARSER --> PIX2PIX_OPTS
        PIX2PIX_OPTS --> ADE20K_OPTS
        ADE20K_OPTS --> DEFAULTS
    end
    
    subgraph "Parameter Categories"
        PREPROCESS["preprocess_mode='resize_and_crop'"]
        DIMENSIONS["load_size, crop_size, display_winsize"]
        LABELS["label_nc=150, contain_dontcare_label=True"]
        CACHE["cache_filelist_read/write=False"]
        
        DEFAULTS --> PREPROCESS
        DEFAULTS --> DIMENSIONS
        DEFAULTS --> LABELS
        DEFAULTS --> CACHE
    end
```

Sources: [data/ade20k_dataset.py:11-25]()

## Data Organization and File Structure

The `get_paths` method handles the discovery and organization of image and label files within the ADE20K dataset directory structure. It differentiates between training and validation phases and filters files based on naming conventions.

### Directory Structure

```
dataroot/
├── training/
│   ├── *_train_*.jpg (scene images)
│   └── *_train_*.png (semantic masks)
└── validation/
    ├── *_val_*.jpg (scene images)
    └── *_val_*.png (semantic masks)
```

### File Discovery Pipeline

```mermaid
graph TD
    subgraph "Path Resolution"
        OPT_DATAROOT["opt.dataroot"]
        PHASE_MAP["phase='test' → subfolder='validation'<br/>phase='train' → subfolder='training'"]
        MAKE_DATASET["make_dataset()"]
        
        OPT_DATAROOT --> PHASE_MAP
        PHASE_MAP --> MAKE_DATASET
    end
    
    subgraph "File Filtering"
        ALL_IMAGES["all_images (sorted)"]
        PHASE_FILTER["filter by '_train_' or '_val_'"]
        EXT_FILTER["split by .jpg/.png extension"]
        
        MAKE_DATASET --> ALL_IMAGES
        ALL_IMAGES --> PHASE_FILTER
        PHASE_FILTER --> EXT_FILTER
    end
    
    subgraph "Output Paths"
        IMAGE_PATHS["image_paths (.jpg files)"]
        LABEL_PATHS["label_paths (.png files)"]
        
        EXT_FILTER --> IMAGE_PATHS
        EXT_FILTER --> LABEL_PATHS
    end
```

Sources: [data/ade20k_dataset.py:27-43]()

## Reference File System

The ADE20K dataset implementation uses reference files to establish correspondences between validation images and training images. This enables exemplar-based generation during inference by providing reference images for style transfer.

### Reference File Format

The reference files (`ade20k_ref.txt` and `ade20k_ref_test.txt`) contain comma-separated mappings:

```
ADE_val_00001232.jpg,ADE_train_00004996.jpg
ADE_val_00001517.jpg,ADE_train_00007201.jpg
ADE_val_00001697.jpg,ADE_train_00015171.jpg
```

### Reference Loading Logic

```mermaid
graph TD
    subgraph "Reference File Selection"
        PHASE_CHECK["opt.phase == 'test'"]
        FILE_TRAIN["./data/ade20k_ref.txt"]
        FILE_TEST["./data/ade20k_ref_test.txt"]
        
        PHASE_CHECK -->|True| FILE_TEST
        PHASE_CHECK -->|False| FILE_TRAIN
    end
    
    subgraph "Reference Parsing"
        READ_LINES["fd.readlines()"]
        PARSE_CSV["items = line.strip().split(',')"]
        BUILD_DICT["ref_dict[key] = val"]
        
        READ_LINES --> PARSE_CSV
        PARSE_CSV --> BUILD_DICT
    end
    
    subgraph "Value Assignment"
        TEST_MODE["phase='test': val = items[1:]"]
        TRAIN_MODE["phase='train': val = [items[1], items[-1]]"]
        FOLDER_TUPLE["train_test_folder = ('training', 'validation')"]
        
        BUILD_DICT --> TEST_MODE
        BUILD_DICT --> TRAIN_MODE
        BUILD_DICT --> FOLDER_TUPLE
    end
```

Sources: [data/ade20k_dataset.py:45-59](), [data/ade20k_ref_test.txt:1-6]()

## Data Loading Integration

The `ADE20KDataset` integrates with the broader CoCosNet data loading pipeline through inheritance from `Pix2pixDataset`. The class provides dataset-specific implementations while leveraging the core functionality of the parent classes.

### Integration Points

```mermaid
graph TB
    subgraph "Dataset Factory"
        FIND_DATASET["find_dataset_using_name('ade20k')"]
        IMPORT_MODULE["importlib.import_module('data.ade20k_dataset')"]
        GET_CLASS["getattr(module, 'ADE20KDataset')"]
        
        FIND_DATASET --> IMPORT_MODULE
        IMPORT_MODULE --> GET_CLASS
    end
    
    subgraph "Initialization Pipeline"
        CREATE_INSTANCE["ADE20KDataset()"]
        INITIALIZE["dataset.initialize(opt)"]
        GET_PATHS_CALL["self.get_paths(opt)"]
        GET_REF_CALL["self.get_ref(opt)"]
        
        GET_CLASS --> CREATE_INSTANCE
        CREATE_INSTANCE --> INITIALIZE
        INITIALIZE --> GET_PATHS_CALL
        INITIALIZE --> GET_REF_CALL
    end
    
    subgraph "Data Processing"
        PIX2PIX_INIT["Pix2pixDataset.initialize()"]
        LOAD_SIZE["load_size=286/256"]
        CROP_SIZE["crop_size=256"]
        LABEL_NC["label_nc=150"]
        
        GET_REF_CALL --> PIX2PIX_INIT
        PIX2PIX_INIT --> LOAD_SIZE
        PIX2PIX_INIT --> CROP_SIZE
        PIX2PIX_INIT --> LABEL_NC
    end
```

Sources: [data/ade20k_dataset.py:9-61]()

## Implementation Details

### Method Signatures

The `ADE20KDataset` class implements three key methods:

- **`modify_commandline_options(parser, is_train)`**: Static method that configures dataset-specific command-line options
- **`get_paths(opt)`**: Returns tuple of `(label_paths, image_paths)` for the specified phase
- **`get_ref(opt)`**: Returns tuple of `(ref_dict, train_test_folder)` containing reference mappings

### Key Features

1. **150 Semantic Classes**: Supports the full ADE20K label vocabulary with `label_nc=150`
2. **Phase-Aware Processing**: Handles both training and validation phases with appropriate folder mapping
3. **Reference-Based Generation**: Enables exemplar-based image synthesis through reference file system
4. **Optimized Caching**: Disables file list caching for test phase to ensure fresh data loading

Sources: [data/ade20k_dataset.py:11-61]()

---

