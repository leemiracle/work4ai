<!-- source: DeepWiki mcp.deepwiki.com · repo yoshitomo-matsubara/torchdistill · page 4 Examples and Usage · fetched 2026-10-21 -->

# Examples and Usage

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [examples/README.md](examples/README.md)
- [examples/torchvision/coco/__init__.py](examples/torchvision/coco/__init__.py)
- [examples/torchvision/coco/dataset.py](examples/torchvision/coco/dataset.py)
- [examples/torchvision/coco/eval.py](examples/torchvision/coco/eval.py)
- [examples/torchvision/image_classification.py](examples/torchvision/image_classification.py)
- [examples/torchvision/object_detection.py](examples/torchvision/object_detection.py)
- [examples/torchvision/semantic_segmentation.py](examples/torchvision/semantic_segmentation.py)
- [examples/torchvision/utils/__init__.py](examples/torchvision/utils/__init__.py)
- [examples/torchvision/utils/dataset.py](examples/torchvision/utils/dataset.py)
- [examples/torchvision/utils/eval.py](examples/torchvision/utils/eval.py)
- [torchdistill/common/constant.py](torchdistill/common/constant.py)
- [torchdistill/misc/log.py](torchdistill/misc/log.py)

</details>



This document provides practical examples and usage patterns for the torchdistill framework across different domains and tasks. The examples demonstrate how to configure and execute knowledge distillation experiments using the framework's declarative YAML-based configuration system.

For detailed information about the core framework components, see [Core Architecture](#2). For configuration system details, see [Configuration-Driven System](#2.1). For component-specific documentation, see [Components](#3).

## Example Structure Overview

The torchdistill repository provides comprehensive examples organized by domain and integration:

| Domain | Location | Description |
|--------|----------|-------------|
| Computer Vision | `examples/torchvision/` | Image classification, object detection, semantic segmentation |
| Natural Language Processing | `examples/hf_transformers/` | GLUE tasks, text classification with Hugging Face |
| Legacy Examples | `examples/legacy/` | Examples for torchdistill ≤ v0.3.3 |

**Example Script Architecture:**

```mermaid
graph TB
    subgraph "Example Script Structure"
        ARGS["Argument Parser<br/>--config, --device, --world_size"]
        CONFIG["Configuration Loading<br/>yaml_util.load_yaml_file()"]
        DIST["Distributed Setup<br/>init_distributed_mode()"]
        MODELS["Model Loading<br/>load_model() functions"]
        TRAINING["Training Pipeline<br/>get_training_box() or get_distillation_box()"]
        EVAL["Evaluation<br/>evaluate() functions"]
    end
    
    subgraph "Core Framework Integration"
        TRAIN_BOX["TrainingBox"]
        DISTILL_BOX["DistillationBox"]
        HOOK_MGR["ForwardHookManager"]
        LOSS_REG["Loss Registry"]
    end
    
    ARGS --> CONFIG
    CONFIG --> DIST
    CONFIG --> MODELS
    MODELS --> TRAINING
    TRAINING --> TRAIN_BOX
    TRAINING --> DISTILL_BOX
    DISTILL_BOX --> HOOK_MGR
    TRAINING --> LOSS_REG
    TRAINING --> EVAL
```

Sources: [examples/README.md:1-12](), [examples/torchvision/image_classification.py:26-42](), [examples/torchvision/object_detection.py:32-50](), [examples/torchvision/semantic_segmentation.py:28-45]()

## Computer Vision Examples

### Image Classification

The image classification example demonstrates standard knowledge distillation for image classification tasks using torchvision models.

**Key Components:**

```mermaid
graph LR
    subgraph "Image Classification Pipeline"
        LOAD_MODEL["load_model()<br/>get_image_classification_model()"]
        TRAIN_EPOCH["train_one_epoch()<br/>MetricLogger, SmoothedValue"]
        EVALUATE["evaluate()<br/>compute_accuracy()"]
        MAIN["main()<br/>Orchestrates full pipeline"]
    end
    
    subgraph "Framework Integration"
        GET_TRAIN["get_training_box()"]
        GET_DISTILL["get_distillation_box()"]
        BUILD_LOADER["build_data_loader()"]
        YAML_LOAD["yaml_util.load_yaml_file()"]
    end
    
    LOAD_MODEL --> GET_TRAIN
    LOAD_MODEL --> GET_DISTILL
    YAML_LOAD --> BUILD_LOADER
    GET_TRAIN --> TRAIN_EPOCH
    GET_DISTILL --> TRAIN_EPOCH
    TRAIN_EPOCH --> EVALUATE
    MAIN --> LOAD_MODEL
```

**Training Loop Pattern:**
- Uses `MetricLogger` for tracking training metrics
- Implements top-1 and top-5 accuracy computation
- Supports both standard training and knowledge distillation modes
- Handles distributed training with `DistributedDataParallel`

Sources: [examples/torchvision/image_classification.py:45-54](), [examples/torchvision/image_classification.py:56-72](), [examples/torchvision/image_classification.py:89-119]()

### Object Detection

The object detection example supports COCO-style object detection with multiple IoU types (bbox, segmentation, keypoints).

**Detection-Specific Components:**

```mermaid
graph TB
    subgraph "Object Detection Pipeline"
        LOAD_OBJ["load_model()<br/>get_object_detection_model()"]
        TRAIN_OBJ["train_one_epoch()<br/>Handles list inputs"]
        EVAL_OBJ["evaluate()<br/>CocoEvaluator integration"]
        IOU_TYPES["get_iou_types()<br/>MaskRCNN, KeypointRCNN detection"]
    end
    
    subgraph "COCO Integration"
        COCO_EVAL["CocoEvaluator<br/>coco/eval.py"]
        COCO_API["get_coco_api_from_dataset()"]
        COCO_DATASET["CustomCocoDetection<br/>coco/dataset.py"]
    end
    
    LOAD_OBJ --> TRAIN_OBJ
    TRAIN_OBJ --> EVAL_OBJ
    EVAL_OBJ --> IOU_TYPES
    EVAL_OBJ --> COCO_EVAL
    COCO_EVAL --> COCO_API
    COCO_API --> COCO_DATASET
```

**Key Features:**
- Handles variable-length inputs for detection models
- Integrates with pycocotools for evaluation
- Supports multiple IoU metrics (bbox, segmentation, keypoints)
- Uses `CocoEvaluator` for standardized evaluation

Sources: [examples/torchvision/object_detection.py:53-62](), [examples/torchvision/object_detection.py:84-95](), [examples/torchvision/object_detection.py:103-154]()

### Semantic Segmentation

The semantic segmentation example implements pixel-level knowledge distillation for segmentation tasks.

**Segmentation-Specific Components:**

```mermaid
graph TB
    subgraph "Segmentation Pipeline"
        LOAD_SEG["load_model()<br/>get_semantic_segmentation_model()"]
        TRAIN_SEG["train_one_epoch()<br/>Pixel-level targets"]
        EVAL_SEG["evaluate()<br/>SegEvaluator"]
        SEG_EVAL["SegEvaluator<br/>IoU computation"]
    end
    
    subgraph "Evaluation Metrics"
        CONFUSION["Confusion Matrix<br/>self.mat tensor"]
        IOU_CALC["IoU Calculation<br/>compute() method"]
        REDUCE_PROC["reduce_from_all_processes()<br/>Distributed reduction"]
    end
    
    LOAD_SEG --> TRAIN_SEG
    TRAIN_SEG --> EVAL_SEG
    EVAL_SEG --> SEG_EVAL
    SEG_EVAL --> CONFUSION
    CONFUSION --> IOU_CALC
    IOU_CALC --> REDUCE_PROC
```

**Evaluation Features:**
- Uses `SegEvaluator` for IoU computation
- Maintains confusion matrix for pixel-level accuracy
- Supports distributed evaluation with tensor reduction
- Computes mean IoU and per-class metrics

Sources: [examples/torchvision/semantic_segmentation.py:48-57](), [examples/torchvision/semantic_segmentation.py:78-108](), [examples/torchvision/utils/eval.py:4-42]()

## Common Usage Patterns

### Configuration-Driven Execution

All examples follow a consistent pattern for configuration-driven execution:

**Configuration Loading Pattern:**
```mermaid
graph LR
    subgraph "Configuration Pipeline"
        YAML_FILE["YAML Configuration File<br/>--config argument"]
        LOAD_YAML["yaml_util.load_yaml_file()"]
        IMPORT_DEPS["import_dependencies()<br/>config['dependencies']"]
        EXTRACT_CONFIGS["Extract Sections<br/>models, datasets, train, test"]
    end
    
    YAML_FILE --> LOAD_YAML
    LOAD_YAML --> IMPORT_DEPS
    IMPORT_DEPS --> EXTRACT_CONFIGS
```

**Model Loading Pattern:**
- Check for official model implementations first
- Fall back to registry-based loading with `get_model()`
- Load checkpoints if specified in configuration
- Move models to appropriate device

Sources: [examples/torchvision/image_classification.py:45-54](), [examples/torchvision/object_detection.py:53-62](), [examples/torchvision/semantic_segmentation.py:48-57]()

### Training Box Selection

Examples implement a consistent pattern for selecting between training and distillation modes:

**Box Selection Logic:**
```mermaid
graph TB
    TEACHER_CHECK{"teacher_model is None?"}
    GET_TRAINING["get_training_box()<br/>Standard training"]
    GET_DISTILL["get_distillation_box()<br/>Knowledge distillation"]
    
    TEACHER_CHECK -->|Yes| GET_TRAINING
    TEACHER_CHECK -->|No| GET_DISTILL
```

This pattern appears identically across all three example scripts, enabling seamless switching between standard training and knowledge distillation based on configuration.

Sources: [examples/torchvision/image_classification.py:126-129](), [examples/torchvision/object_detection.py:161-164](), [examples/torchvision/semantic_segmentation.py:115-118]()

### Distributed Training Support

All examples include comprehensive distributed training support:

**Distributed Training Components:**

| Component | Purpose | Implementation |
|-----------|---------|----------------|
| `init_distributed_mode()` | Initialize distributed process group | Sets up world_size, rank, device_ids |
| `DistributedDataParallel` | Model parallelization | Wraps models for distributed training |
| `adjust_lr` flag | Learning rate scaling | Multiplies LR by world_size |
| `is_main_process()` | Process coordination | Controls logging and checkpointing |

### Evaluation and Checkpointing

Examples implement domain-specific evaluation with consistent checkpointing:

**Checkpoint Management:**
- Load existing checkpoints if available
- Save best model based on validation metrics
- Track best performance (accuracy, mAP, mIoU)
- Support test-only mode for evaluation

Sources: [examples/torchvision/image_classification.py:130-149](), [examples/torchvision/object_detection.py:165-189](), [examples/torchvision/semantic_segmentation.py:119-142]()

## Logging and Monitoring

### MetricLogger System

All examples use a consistent logging system based on `MetricLogger` and `SmoothedValue`:

**Logging Architecture:**
```mermaid
graph TB
    subgraph "Logging Components"
        METRIC_LOGGER["MetricLogger<br/>torchdistill.misc.log"]
        SMOOTHED_VALUE["SmoothedValue<br/>Deque-based averaging"]
        LOG_EVERY["log_every()<br/>Periodic logging iterator"]
    end
    
    subgraph "Metrics Tracked"
        LOSS["loss<br/>Training loss"]
        LR["lr<br/>Learning rate"]
        THROUGHPUT["img/s<br/>Images per second"]
        CUSTOM["Custom Metrics<br/>Task-specific"]
    end
    
    METRIC_LOGGER --> SMOOTHED_VALUE
    METRIC_LOGGER --> LOG_EVERY
    LOG_EVERY --> LOSS
    LOG_EVERY --> LR
    LOG_EVERY --> THROUGHPUT
    LOG_EVERY --> CUSTOM
```

**Key Features:**
- Windowed averaging with configurable window size
- Distributed synchronization support
- GPU memory tracking when available
- ETA calculation for training progress

Sources: [torchdistill/misc/log.py:41-120](), [torchdistill/misc/log.py:122-250](), [examples/torchvision/image_classification.py:56-72]()

## Running Examples

### Command Line Interface

Each example script provides a consistent command-line interface:

**Common Arguments:**

| Argument | Purpose | Example |
|----------|---------|---------|
| `--config` | YAML configuration file path | `--config configs/image_classification.yaml` |
| `--device` | Training device | `--device cuda` |
| `--world_size` | Distributed training processes | `--world_size 4` |
| `--test_only` | Evaluation-only mode | `-test_only` |
| `--student_only` | Skip teacher evaluation | `-student_only` |
| `--log_config` | Print configuration | `-log_config` |

### Execution Pattern

**Standard execution flow:**
1. Parse command-line arguments
2. Initialize distributed training environment
3. Load YAML configuration and import dependencies
4. Initialize models (teacher and student)
5. Create training or distillation box
6. Execute training loop with validation
7. Final evaluation on test set

Sources: [examples/torchvision/image_classification.py:160-207](), [examples/torchvision/object_detection.py:200-248](), [examples/torchvision/semantic_segmentation.py:153-201]()

---

