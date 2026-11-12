<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/large-scale-image-deduplication · page 2 Embedding Generation System · fetched 2026-10-26 -->

# Embedding Generation System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [compute_embeddings.py](compute_embeddings.py)

</details>



## Purpose and Scope

The Embedding Generation System is the core processing engine of the Large-Scale Image Deduplication Toolkit, responsible for transforming images from various dataset sources into numerical vector representations using Facebook's SSCD (Self-Supervised Copy Detection) model. This system serves as the foundation for all downstream analysis tasks including duplicate detection, clustering, and similarity search.

For information about tools that analyze the generated embeddings, see [Analysis & Deduplication Tools](#3). For batch processing workflows that orchestrate this system, see [Batch Processing & Utilities](#4).

## System Architecture

The embedding generation system centers around the `compute_embeddings.py` script and follows a modular pipeline architecture with clear separation of concerns:

### Core System Components

```mermaid
graph TB
    subgraph "Input Layer"
        HF["HuggingFace Datasets"]
        IMG["Individual Images"]
        ARGS["CLI Arguments"]
    end
    
    subgraph "Processing Engine - compute_embeddings.py"
        MAIN["compute_embeddings()"]
        COLLATOR["ImageCollator"]
        TRANSFORMS["create_transforms()"]
        DEVICE["setup_device()"]
        MODEL["load_model()"]
    end
    
    subgraph "Inference Pipeline"
        DATALOADER["DataLoader"]
        BATCH["compute_batch_embeddings()"]
        SSCD["SSCD Model\nsscd_disc_mixup.torchscript.pt"]
    end
    
    subgraph "Output Layer"
        SAVE["save_results()"]
        NPY_EMB["*_embeddings.npy"]
        NPY_IDS["*_image_ids.npy"]
    end
    
    HF --> MAIN
    IMG --> MAIN
    ARGS --> MAIN
    
    MAIN --> COLLATOR
    MAIN --> TRANSFORMS
    MAIN --> DEVICE
    MAIN --> MODEL
    
    COLLATOR --> DATALOADER
    TRANSFORMS --> COLLATOR
    DATALOADER --> BATCH
    MODEL --> BATCH
    BATCH --> SSCD
    
    BATCH --> SAVE
    SAVE --> NPY_EMB
    SAVE --> NPY_IDS
```

Sources: [compute_embeddings.py:190-234]()

### Data Flow Pipeline

```mermaid
graph LR
    subgraph "Image Loading"
        DATASET["load_dataset()"]
        INDEX["add_column(dataset_idx)"]
        LOADER["DataLoader"]
    end
    
    subgraph "Image Processing"
        COLLATE["ImageCollator.__call__()"]
        VALID["_is_valid_image()"]
        CONVERT["img.convert('RGB')"]
        TRANSFORM["transform(img)"]
    end
    
    subgraph "Model Inference"
        BATCH_TENSOR["batch_tensor.to(device)"]
        MODEL_FORWARD["model(batch_tensor)"]
        CPU_MOVE["embeddings.cpu()"]
    end
    
    subgraph "Output Generation"
        VSTACK["np.vstack()"]
        SAVE_EMB["save_results()"]
        STATS["print_results()"]
    end
    
    DATASET --> INDEX
    INDEX --> LOADER
    LOADER --> COLLATE
    
    COLLATE --> VALID
    VALID --> CONVERT
    CONVERT --> TRANSFORM
    
    TRANSFORM --> BATCH_TENSOR
    BATCH_TENSOR --> MODEL_FORWARD
    MODEL_FORWARD --> CPU_MOVE
    
    CPU_MOVE --> VSTACK
    VSTACK --> SAVE_EMB
    SAVE_EMB --> STATS
```

Sources: [compute_embeddings.py:190-221](), [compute_embeddings.py:140-157](), [compute_embeddings.py:39-109]()

## Core Components

### ImageCollator Class

The `ImageCollator` class handles batch processing and image validation with support for multiple dataset formats and optional deduplication:

| Component | Purpose | Key Methods |
|-----------|---------|-------------|
| `__init__()` | Initialize collator with transforms and deduplication settings | Sets up `transform`, `deduplicate`, `seen_ids` |
| `_is_valid_image()` | Validate image integrity before processing | Tests `img.load()` and `img.convert('RGB')` |
| `__call__()` | Process batches with multiple image key patterns | Handles `image`, `images`, `image_N` patterns |

The collator supports flexible image key patterns including single images (`image`), image lists (`images`), and numbered sequences (`image_0`, `image_1`, etc.).

Sources: [compute_embeddings.py:15-109]()

### Model Management Functions

The system provides dedicated functions for device and model setup:

```mermaid
graph TD
    subgraph "Device Setup"
        SETUP_DEV["setup_device()"]
        CUDA_CHECK["torch.cuda.is_available()"]
        DEVICE_SELECT["torch.device()"]
    end
    
    subgraph "Model Loading"
        LOAD_MODEL["load_model()"]
        JIT_LOAD["torch.jit.load()"]
        MODEL_EVAL["model.eval()"]
        MODEL_TO_DEV["model.to(device)"]
    end
    
    subgraph "Transform Pipeline"
        CREATE_TRANS["create_transforms()"]
        RESIZE["Resize([320, 320])"]
        TOTENSOR["ToTensor()"]
        NORMALIZE["Normalize(mean, std)"]
    end
    
    SETUP_DEV --> CUDA_CHECK
    CUDA_CHECK --> DEVICE_SELECT
    
    LOAD_MODEL --> JIT_LOAD
    JIT_LOAD --> MODEL_EVAL
    MODEL_EVAL --> MODEL_TO_DEV
    
    CREATE_TRANS --> RESIZE
    RESIZE --> TOTENSOR
    TOTENSOR --> NORMALIZE
```

Sources: [compute_embeddings.py:112-137]()

### Batch Processing Engine

The `compute_batch_embeddings()` function orchestrates the core inference loop:

| Phase | Operations | Timing Tracked |
|-------|------------|----------------|
| Setup | `torch.no_grad()` context, progress tracking with `tqdm` | - |
| Processing | `batch_tensor.to(device)`, `model(batch_tensor)` | `model_inference_time` |
| Collection | `embeddings.cpu().numpy()`, `image_ids.extend()` | - |

The function returns embeddings, image IDs, and detailed timing information for performance analysis.

Sources: [compute_embeddings.py:140-157]()

## Processing Pipeline

### Input Validation and Preprocessing

The system implements robust image validation through the `_is_valid_image()` method:

```mermaid
graph TD
    subgraph "Image Validation Pipeline"
        INPUT["Image Input"]
        NULL_CHECK["img is None?"]
        LOAD_TEST["img.load()"]
        RGB_TEST["img.convert('RGB')"]
        VALID["Valid Image"]
        INVALID["Invalid Image"]
    end
    
    INPUT --> NULL_CHECK
    NULL_CHECK -->|"Yes"| INVALID
    NULL_CHECK -->|"No"| LOAD_TEST
    LOAD_TEST -->|"Exception"| INVALID
    LOAD_TEST -->|"Success"| RGB_TEST
    RGB_TEST -->|"Exception"| INVALID
    RGB_TEST -->|"Success"| VALID
```

The validation catches `OSError`, `IOError`, `Image.DecompressionBombError`, and other exceptions to ensure only processable images enter the pipeline.

Sources: [compute_embeddings.py:24-37]()

### SSCD Model Configuration

The system uses a standardized transform pipeline optimized for the SSCD model:

| Transform Stage | Configuration | Purpose |
|----------------|---------------|---------|
| Resize | `[320, 320]` | Standardize input dimensions |
| ToTensor | Default | Convert PIL to tensor format |
| Normalize | `mean=[0.485, 0.456, 0.406]`, `std=[0.229, 0.224, 0.225]` | ImageNet normalization |

Sources: [compute_embeddings.py:128-137]()

### Output Management

The `save_results()` function handles file organization and naming:

```mermaid
graph LR
    subgraph "Filename Generation"
        DATASET["dataset_name"]
        SANITIZE1["replace('/', '-')"]
        NAME_OPT["name (optional)"]
        SPLIT["split"]
        COMBINE["filename_base"]
    end
    
    subgraph "File Output"
        EMB_FILE["*_embeddings.npy"]
        IDS_FILE["*_image_ids.npy"]
        MKDIR["os.makedirs()"]
    end
    
    DATASET --> SANITIZE1
    NAME_OPT --> SANITIZE1
    SANITIZE1 --> COMBINE
    SPLIT --> COMBINE
    
    COMBINE --> MKDIR
    MKDIR --> EMB_FILE
    MKDIR --> IDS_FILE
```

Sources: [compute_embeddings.py:160-173]()

## Configuration and Usage

### Command Line Interface

The system accepts the following parameters through `argparse`:

| Parameter | Type | Default | Purpose |
|-----------|------|---------|---------|
| `--dataset` | string | required | HuggingFace dataset identifier |
| `--split` | string | `"val"` | Dataset split to process |
| `--name` | string | `None` | Dataset subset name |
| `--output_dir` | string | `"embeddings"` | Output directory path |
| `--batch_size` | integer | `32` | Processing batch size |
| `--deduplicate` | flag | `False` | Enable ID-based deduplication |
| `--id_column` | string | `"image_id"` | Column name for image IDs |

Sources: [compute_embeddings.py:223-234]()

### Performance Monitoring

The system provides comprehensive timing instrumentation:

```mermaid
graph TD
    subgraph "Timing Metrics"
        FUNC_START["function_start_time"]
        PROC_START["start_time"]
        MODEL_TIME["model_inference_time"]
        PROC_END["end_time"]
        FUNC_END["function_end_time"]
    end
    
    subgraph "Calculated Metrics"
        TOTAL_TIME["total_time"]
        TIME_PER_SAMPLE["time_per_sample"]
        MODEL_PER_SAMPLE["model_time_per_sample"]
        FUNC_TOTAL["function_total_time"]
    end
    
    FUNC_START --> FUNC_TOTAL
    PROC_START --> TOTAL_TIME
    MODEL_TIME --> MODEL_PER_SAMPLE
    PROC_END --> TOTAL_TIME
    FUNC_END --> FUNC_TOTAL
    
    TOTAL_TIME --> TIME_PER_SAMPLE
```

The `print_results()` function outputs detailed performance statistics including per-sample timing and model inference overhead.

Sources: [compute_embeddings.py:176-187](), [compute_embeddings.py:192](), [compute_embeddings.py:218-220]()

---

