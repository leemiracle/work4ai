<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/CvT · page 4 Usage Guide · fetched 2026-10-26 -->

# Usage Guide

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [experiments/imagenet/cvt/cvt-13-224x224.yaml](experiments/imagenet/cvt/cvt-13-224x224.yaml)
- [tools/train.py](tools/train.py)

</details>



This document provides practical guidance for using the CvT (Convolutional vision Transformers) repository to train and evaluate models. It covers the main workflows, entry points, and configuration patterns that users need to understand for effective operation of the CvT training system.

For detailed step-by-step training instructions, see [Training Models](#4.1). For evaluation procedures and metrics, see [Model Evaluation](#4.2). For complete configuration parameter reference, see [Configuration Reference](#4.3).

## System Overview

The CvT repository follows a configuration-driven training workflow where users specify model architecture, training parameters, and data settings through YAML configuration files. The primary entry point is the `tools/train.py` script, which orchestrates the entire training pipeline.

### Core Usage Workflow

```mermaid
flowchart TD
    user["User"]
    
    subgraph "Configuration Phase"
        yaml["YAML Config File<br/>experiments/imagenet/cvt/*.yaml"]
        args["Command Line Arguments<br/>--cfg, --local_rank, opts"]
    end
    
    subgraph "Execution Phase"
        trainpy["tools/train.py<br/>main(), parse_args()"]
        config["config module<br/>update_config()"]
        init["Initialization<br/>init_distributed()<br/>setup_cudnn()"]
    end
    
    subgraph "Training Components"
        model["build_model()"]
        data["build_dataloader()"]
        optim["build_optimizer()"]
        criterion["build_criterion()"]
        scheduler["build_lr_scheduler()"]
    end
    
    subgraph "Training Loop"
        epoch["Training Epochs<br/>train_one_epoch()"]
        eval["Validation<br/>test()"]
        checkpoint["Checkpointing<br/>save_checkpoint_on_master()"]
    end
    
    subgraph "Outputs"
        logs["Training Logs"]
        models["Model Checkpoints<br/>model_best.pth<br/>final_state.pth"]
        tensorboard["TensorBoard Logs"]
    end
    
    user --> yaml
    user --> args
    yaml --> trainpy
    args --> trainpy
    trainpy --> config
    config --> init
    
    init --> model
    init --> data
    init --> optim
    init --> criterion
    init --> scheduler
    
    model --> epoch
    data --> epoch
    optim --> epoch
    criterion --> epoch
    epoch --> eval
    eval --> checkpoint
    scheduler --> epoch
    
    checkpoint --> logs
    checkpoint --> models
    epoch --> tensorboard
```

**Title: CvT Training Workflow from User Input to Model Output**

Sources: [tools/train.py:1-211](), [experiments/imagenet/cvt/cvt-13-224x224.yaml:1-84]()

## Entry Points and Commands

### Primary Training Command

The main entry point for training CvT models is `tools/train.py`. The basic command structure is:

```bash
python tools/train.py --cfg <config_file> [opts]
```

Key command line arguments defined in `parse_args()`:

| Argument | Purpose | Example |
|----------|---------|---------|
| `--cfg` | Required configuration file path | `experiments/imagenet/cvt/cvt-13-224x224.yaml` |
| `--local_rank` | GPU rank for distributed training | `0` |
| `--port` | Port for distributed communication | `9000` |
| `opts` | Configuration overrides | `TRAIN.LR 0.001 MODEL.SPEC.DEPTH [1,2,12]` |

### Distributed Training Support

The system automatically handles distributed training setup through `init_distributed()` and supports multi-GPU training with `DistributedDataParallel`:

```mermaid
graph LR
    subgraph "Distributed Training Setup"
        args["Command Line Args<br/>--local_rank, --port"]
        init["init_distributed(args)<br/>tools/train.py:63"]
        ddp["DistributedDataParallel<br/>tools/train.py:110-114"]
    end
    
    subgraph "Data Distribution"
        sampler["Distributed Sampler<br/>train_loader.sampler.set_epoch()"]
        loader["build_dataloader()<br/>distributed=True"]
    end
    
    subgraph "Model Synchronization"
        sync["Gradient Synchronization<br/>find_unused_parameters=True"]
        save["save_checkpoint_on_master()<br/>tools/train.py:171-180"]
    end
    
    args --> init
    init --> ddp
    ddp --> sync
    loader --> sampler
    sampler --> sync
    sync --> save
```

**Title: Distributed Training Component Integration**

Sources: [tools/train.py:46-48](), [tools/train.py:63](), [tools/train.py:109-114](), [tools/train.py:131-132]()

## Configuration Management

### Configuration Loading Process

The configuration system processes multiple sources with a defined precedence order:

```mermaid
graph TD
    subgraph "Configuration Sources (Priority Order)"
        default["Default Configuration<br/>lib/config/default.py"]
        yaml["YAML File<br/>experiments/imagenet/cvt/*.yaml"]
        cmdline["Command Line Overrides<br/>opts parameter"]
    end
    
    subgraph "Processing Pipeline"
        update["update_config(config, args)<br/>tools/train.py:66"]
        validate["Configuration Validation"]
        save["save_config()<br/>tools/train.py:79"]
    end
    
    subgraph "Configuration Usage"
        model["Model Building<br/>build_model(config)"]
        training["Training Setup<br/>optimizer, scheduler, criterion"]
        data["Data Pipeline<br/>build_dataloader(config)"]
    end
    
    default --> update
    yaml --> update  
    cmdline --> update
    update --> validate
    validate --> save
    
    save --> model
    save --> training
    save --> data
```

**Title: Configuration Processing and Application Pipeline**

### Key Configuration Sections

Based on the provided YAML example, the main configuration categories are:

| Section | Purpose | Key Parameters |
|---------|---------|----------------|
| `MODEL.SPEC` | CvT architecture definition | `NUM_STAGES`, `DIM_EMBED`, `NUM_HEADS`, `DEPTH` |
| `TRAIN` | Training hyperparameters | `LR`, `BATCH_SIZE_PER_GPU`, `END_EPOCH`, `OPTIMIZER` |
| `DATASET` | Data configuration | `ROOT`, `TRAIN_SET`, `TEST_SET` |
| `AUG` | Data augmentation settings | `MIXUP`, `TIMM_AUG`, `AUTO_AUGMENT` |
| `AMP` | Automatic Mixed Precision | `ENABLED`, `MEMORY_FORMAT` |

Sources: [tools/train.py:66](), [tools/train.py:77-79](), [experiments/imagenet/cvt/cvt-13-224x224.yaml:7-84]()

## Training Pipeline Components

### Component Initialization Sequence

The training system initializes components in a specific order to ensure proper dependencies:

```mermaid
graph TD
    subgraph "System Setup"
        distributed["init_distributed(args)"]
        cudnn["setup_cudnn(config)"]
        logger["create_logger()"]
    end
    
    subgraph "Model Setup"
        model["build_model(config)<br/>tools/train.py:81"]
        cuda["model.to(torch.device('cuda'))<br/>tools/train.py:82"]
        amp["Convert to NHWC<br/>tools/train.py:87-89"]
    end
    
    subgraph "Training Setup"
        optimizer["build_optimizer(config, model)<br/>tools/train.py:100"]
        resume["resume_checkpoint()<br/>tools/train.py:102-104"]
        dataloader["build_dataloader()<br/>tools/train.py:106-107"]
        criterion["build_criterion(config)<br/>tools/train.py:116-119"]
        scheduler["build_lr_scheduler()<br/>tools/train.py:121"]
        scaler["torch.cuda.amp.GradScaler<br/>tools/train.py:123"]
    end
    
    distributed --> cudnn
    cudnn --> logger
    logger --> model
    model --> cuda
    cuda --> amp
    amp --> optimizer
    optimizer --> resume
    resume --> dataloader
    dataloader --> criterion
    criterion --> scheduler
    scheduler --> scaler
```

**Title: Training Component Initialization Dependencies**

### Training Loop Structure

The main training loop in `tools/train.py` follows this pattern for each epoch:

| Phase | Function | Key Operations |
|-------|----------|----------------|
| Setup | Epoch initialization | Set sampler epoch, logging setup |
| Training | `train_one_epoch()` | Forward pass, loss computation, backpropagation |
| Evaluation | `test()` | Validation accuracy computation |
| Checkpointing | `save_checkpoint_on_master()` | Save model state and optimizer state |
| Scheduling | `lr_scheduler.step()` | Update learning rate |

Sources: [tools/train.py:21-22](), [tools/train.py:81-123](), [tools/train.py:126-195]()

## Output Management

### Generated Artifacts

The training process generates several types of outputs in the specified `OUTPUT_DIR`:

| Artifact Type | File Pattern | Purpose |
|---------------|--------------|---------|
| Configuration | `config.yaml` | Saved configuration used for training |
| Model Checkpoints | `model_best.pth`, `final_state.pth` | Best and final model weights |
| Training State | Checkpoint files with optimizer state | Resume training capability |
| Logs | Training logs and metrics | Performance tracking |
| TensorBoard | TensorBoard log directory | Training visualization |

### Model Saving Strategy

```mermaid
graph LR
    subgraph "Model Saving Logic"
        eval["Validation Performance<br/>test() returns perf"]
        compare["best_model = (perf > best_perf)<br/>tools/train.py:156"]
        best["save_model_on_master()<br/>model_best.pth<br/>tools/train.py:182-185"]
        checkpoint["save_checkpoint_on_master()<br/>tools/train.py:171-180"]
        final["Final Model Save<br/>final_state.pth<br/>tools/train.py:197-199"]
    end
    
    subgraph "Optional Saving"
        all_models["SAVE_ALL_MODELS<br/>model_epoch.pth<br/>tools/train.py:187-190"]
        swa["SWA Model<br/>swa_state.pth<br/>tools/train.py:201-204"]
    end
    
    eval --> compare
    compare --> best
    compare --> checkpoint
    checkpoint --> final
    checkpoint --> all_models
    final --> swa
```

**Title: Model Checkpoint and Artifact Management Strategy**

Sources: [tools/train.py:149-204]()

## Quick Reference

For immediate usage, the most common workflow is:

1. **Select Configuration**: Choose from `experiments/imagenet/cvt/` directory
2. **Run Training**: `python tools/train.py --cfg <config_path>`  
3. **Monitor Progress**: Check logs and TensorBoard output
4. **Access Results**: Find trained models in the specified `OUTPUT_DIR`

For advanced configuration customization, parameter tuning, and evaluation procedures, refer to the detailed sub-pages of this usage guide.

---

