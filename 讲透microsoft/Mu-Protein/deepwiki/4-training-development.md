<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/Mu-Protein · page 4 Training & Development · fetched 2026-10-26 -->

# Training & Development

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [mu-former/main.py](mu-former/main.py)
- [mu-former/src/trainer.py](mu-former/src/trainer.py)
- [pmlm/README.md](pmlm/README.md)

</details>



This document provides a comprehensive guide for training models and developing with the μProtein framework. It covers the overall training pipeline, development workflow, and key components involved in training both PMLM and μFormer models.

For detailed step-by-step training procedures, see [μFormer Training](#4.1) and [PMLM Training](#4.2). For API reference of training utilities, see [Training Utilities](#5.3).

## Training Pipeline Overview

The μProtein framework implements a three-stage training pipeline where each stage builds upon the previous one:

```mermaid
flowchart TD
    subgraph "Stage 1: PMLM Pretraining"
        UNIREF["UniRef50 Dataset"]
        PREPROCESS["fairseq-preprocess"]
        PRETRAIN_SCRIPT["pmlm/script/pretrain.sh"]
        PMLM_MODEL["pmlm_650m.pt"]
    end
    
    subgraph "Stage 2: μFormer Training"
        TSV_DATA["Mutation Data (TSV)"]
        FASTA_DATA["Protein Sequences (FASTA)"]
        MAIN_PY["mu-former/main.py"]
        TRAINER_CLASS["Trainer.train()"]
        MUFORMER_MODEL["Fine-tuned μFormer"]
    end
    
    subgraph "Stage 3: μSearch Optimization"
        FITNESS_ORACLE["Fitness Prediction Oracle"]
        RL_SEARCH["Reinforcement Learning"]
        OPTIMIZED_PROTEINS["Optimized Protein Variants"]
    end
    
    UNIREF --> PREPROCESS
    PREPROCESS --> PRETRAIN_SCRIPT
    PRETRAIN_SCRIPT --> PMLM_MODEL
    
    PMLM_MODEL --> MAIN_PY
    TSV_DATA --> MAIN_PY
    FASTA_DATA --> MAIN_PY
    MAIN_PY --> TRAINER_CLASS
    TRAINER_CLASS --> MUFORMER_MODEL
    
    MUFORMER_MODEL --> FITNESS_ORACLE
    FITNESS_ORACLE --> RL_SEARCH
    RL_SEARCH --> OPTIMIZED_PROTEINS
```

**Sources:** [pmlm/README.md:1-59](), [mu-former/main.py:1-142]()

## Development Workflow

The typical development workflow involves setting up the environment, preparing data, and executing training scripts:

```mermaid
flowchart LR
    subgraph "Environment Setup"
        CONDA["conda create -n mutation python==3.8"]
        REQUIREMENTS["pip install -r requirements.txt"]
        PYTORCH["pip install torch==1.12.0+cu113"]
    end
    
    subgraph "Data Preparation"
        FORMAT["Format sequences with spaces"]
        FAIRSEQ_PREP["fairseq-preprocess"]
        BINARY_DATA["Binary format data"]
    end
    
    subgraph "Training Execution"
        PMLM_TRAIN["bash pmlm/script/pretrain.sh"]
        MUFORMER_TRAIN["python mu-former/main.py"]
        CHECKPOINTS["Model checkpoints"]
    end
    
    CONDA --> REQUIREMENTS
    REQUIREMENTS --> PYTORCH
    PYTORCH --> FORMAT
    FORMAT --> FAIRSEQ_PREP
    FAIRSEQ_PREP --> BINARY_DATA
    BINARY_DATA --> PMLM_TRAIN
    PMLM_TRAIN --> MUFORMER_TRAIN
    MUFORMER_TRAIN --> CHECKPOINTS
```

**Sources:** [pmlm/README.md:7-21](), [pmlm/README.md:25-47]()

## Core Training Components

The training system is built around several key components that handle different aspects of the training process:

```mermaid
graph TB
    subgraph "Training Orchestration"
        MAIN["main.py"]
        TRAINER["Trainer class"]
        ARGS["argparse configuration"]
    end
    
    subgraph "Model Architecture"
        MUFORMER["Muformer model"]
        ENCODER["pretrained encoder"]
        DECODER["siamese decoder"]
    end
    
    subgraph "Data Pipeline"
        PAIRED_DATASET["PairedDataset"]
        DATALOADERS["train/valid/test loaders"]
        BATCH_PROCESSING["batch processing"]
    end
    
    subgraph "Training Infrastructure"
        OPTIMIZER["Adam optimizer"]
        CRITERION["loss functions"]
        SCHEDULER["learning rate schedulers"]
        EARLY_STOPPING["EarlyStopping"]
    end
    
    subgraph "Persistence Layer"
        SAVER["Saver utility"]
        CHECKPOINTS["model checkpoints"]
        LOGGER["Logger utility"]
    end
    
    MAIN --> TRAINER
    ARGS --> TRAINER
    
    TRAINER --> MUFORMER
    ENCODER --> MUFORMER
    DECODER --> MUFORMER
    
    TRAINER --> PAIRED_DATASET
    PAIRED_DATASET --> DATALOADERS
    DATALOADERS --> BATCH_PROCESSING
    
    TRAINER --> OPTIMIZER
    TRAINER --> CRITERION
    TRAINER --> SCHEDULER
    TRAINER --> EARLY_STOPPING
    
    TRAINER --> SAVER
    SAVER --> CHECKPOINTS
    TRAINER --> LOGGER
```

**Sources:** [mu-former/main.py:16-42](), [mu-former/src/trainer.py:80-216]()

### Training Configuration

The training system uses extensive configuration through command-line arguments:

| Parameter Category | Key Arguments | Purpose |
|-------------------|---------------|---------|
| Data | `--train`, `--valid`, `--test`, `--fasta` | Input data files |
| Model | `--hidden-size`, `--dropout`, `--encoder-name` | Model architecture |
| Training | `--epochs`, `--batch-size`, `--lr`, `--patience` | Training hyperparameters |
| Infrastructure | `--num-workers`, `--local-rank`, `--output-dir` | System configuration |

**Sources:** [mu-former/main.py:73-135]()

## Training Loop Implementation

The core training logic is implemented in the `Trainer` class with a sophisticated training loop:

```mermaid
flowchart TD
    subgraph "Training Initialization"
        INIT_MODEL["init_model()"]
        PREPARE_DATA["_prepare_dataloaders()"]
        RESUME_STATE["_resume_training_state()"]
        INIT_SCHEDULER["_init_scheduler()"]
    end
    
    subgraph "Training Loop"
        EPOCH_START["epoch iteration"]
        TRAIN_EPOCH["_train_epoch()"]
        EVALUATE["_evaluate_and_save_best()"]
        CHECK_STOP["early stopping check"]
        SAVE_CHECKPOINT["checkpoint saving"]
    end
    
    subgraph "Training Epoch Details"
        FORWARD_PASS["model forward pass"]
        LOSS_CALC["criterion loss calculation"]
        BACKWARD_PASS["loss.backward()"]
        CLIP_GRAD["gradient clipping"]
        OPTIMIZER_STEP["optimizer.step()"]
        SCHEDULER_STEP["scheduler.step()"]
    end
    
    INIT_MODEL --> PREPARE_DATA
    PREPARE_DATA --> RESUME_STATE
    RESUME_STATE --> INIT_SCHEDULER
    INIT_SCHEDULER --> EPOCH_START
    
    EPOCH_START --> TRAIN_EPOCH
    TRAIN_EPOCH --> EVALUATE
    EVALUATE --> CHECK_STOP
    CHECK_STOP --> SAVE_CHECKPOINT
    SAVE_CHECKPOINT --> EPOCH_START
    
    TRAIN_EPOCH --> FORWARD_PASS
    FORWARD_PASS --> LOSS_CALC
    LOSS_CALC --> BACKWARD_PASS
    BACKWARD_PASS --> CLIP_GRAD
    CLIP_GRAD --> OPTIMIZER_STEP
    OPTIMIZER_STEP --> SCHEDULER_STEP
```

**Sources:** [mu-former/src/trainer.py:389-430](), [mu-former/src/trainer.py:467-499]()

### Distributed Training Support

The framework supports distributed training across multiple GPUs:

```mermaid
graph LR
    subgraph "Distributed Setup"
        ENV_VARS["RANK, WORLD_SIZE, LOCAL_RANK"]
        INIT_PROCESS["torch.distributed.init_process_group"]
        BARRIER["torch.distributed.barrier"]
    end
    
    subgraph "Model Wrapping"
        DDP["DistributedDataParallel"]
        DEVICE_MAPPING["device_ids=[local_rank]"]
        UNUSED_PARAMS["find_unused_parameters=True"]
    end
    
    subgraph "Data Distribution"
        SAMPLER["DistributedSampler"]
        SET_EPOCH["sampler.set_epoch()"]
        SYNC_BATCHES["synchronized batching"]
    end
    
    ENV_VARS --> INIT_PROCESS
    INIT_PROCESS --> BARRIER
    BARRIER --> DDP
    DDP --> DEVICE_MAPPING
    DEVICE_MAPPING --> UNUSED_PARAMS
    UNUSED_PARAMS --> SAMPLER
    SAMPLER --> SET_EPOCH
    SET_EPOCH --> SYNC_BATCHES
```

**Sources:** [mu-former/src/trainer.py:40-63](), [mu-former/src/trainer.py:147-151](), [mu-former/src/trainer.py:236-238]()

## Checkpoint Management

The framework provides comprehensive checkpoint management for model persistence and resumption:

| Operation | Method | Purpose |
|-----------|--------|---------|
| Save | `save_checkpoint()` | Save model and optimizer state |
| Load | `load_checkpoint()` | Load complete checkpoint |
| Load (stripped) | `load_checkpoint_strip()` | Load with module prefix handling |
| Resume | `_resume_training_state()` | Resume from specific epoch |

The checkpoint structure includes:
- `model_state_dict`: Model parameters
- `optimizer_state_dict`: Optimizer state  
- `log_info`: Training metadata (epoch, best score, etc.)

**Sources:** [mu-former/src/trainer.py:285-355](), [mu-former/src/trainer.py:384-387](), [mu-former/src/trainer.py:440-456]()

## Learning Rate Scheduling

The framework implements sophisticated learning rate scheduling:

```mermaid
graph TD
    subgraph "Scheduler Options"
        INVERSE_SQRT["InverseSqrtLRDecay"]
        POLYNOMIAL["PolynomialLRDecay"]
        WARMUP["warmup_updates"]
    end
    
    subgraph "Configuration"
        WARMUP_EPOCHS["warmup_epochs = 5"]
        STEPS_PER_EPOCH["len(train_loader)"]
        TOTAL_STEPS["epochs * steps_per_epoch"]
    end
    
    subgraph "Implementation"
        SCHEDULER_INIT["scheduler initialization"]
        STEP_CALL["scheduler.step()"]
        LR_UPDATE["learning rate adjustment"]
    end
    
    WARMUP_EPOCHS --> WARMUP
    STEPS_PER_EPOCH --> TOTAL_STEPS
    TOTAL_STEPS --> SCHEDULER_INIT
    WARMUP --> SCHEDULER_INIT
    SCHEDULER_INIT --> STEP_CALL
    STEP_CALL --> LR_UPDATE
```

**Sources:** [mu-former/src/trainer.py:462-465](), [mu-former/src/trainer.py:397-398]()

## Model Evaluation and Testing

The evaluation system supports multiple modes and ensemble prediction:

```mermaid
flowchart TD
    subgraph "Evaluation Modes"
        VAL_MODE["validation mode"]
        TEST_MODE["test mode"]  
        ENSEMBLE_MODE["ensemble mode"]
    end
    
    subgraph "Evaluation Process"
        MODEL_EVAL["model.eval()"]
        NO_GRAD["torch.no_grad()"]
        FORWARD_PASS["model forward pass"]
        LOSS_CALC["loss calculation"]
        METRIC_CALC["correlation metrics"]
    end
    
    subgraph "Ensemble Logic"
        MULTI_MODELS["multiple models"]
        CONCAT_PREDS["concatenate predictions"]
        MEAN_ENSEMBLE["esb_ypred.mean(axis=1)"]
        FINAL_METRICS["spearmanr correlation"]
    end
    
    VAL_MODE --> MODEL_EVAL
    TEST_MODE --> MODEL_EVAL
    ENSEMBLE_MODE --> MODEL_EVAL
    
    MODEL_EVAL --> NO_GRAD
    NO_GRAD --> FORWARD_PASS
    FORWARD_PASS --> LOSS_CALC
    LOSS_CALC --> METRIC_CALC
    
    ENSEMBLE_MODE --> MULTI_MODELS
    MULTI_MODELS --> CONCAT_PREDS
    CONCAT_PREDS --> MEAN_ENSEMBLE
    MEAN_ENSEMBLE --> FINAL_METRICS
```

**Sources:** [mu-former/src/trainer.py:545-600](), [mu-former/src/trainer.py:584-588]()

---

