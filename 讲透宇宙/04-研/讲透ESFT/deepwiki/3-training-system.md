> 来源: [https://deepwiki.com/deepseek-ai/ESFT/3-training-system](https://deepwiki.com/deepseek-ai/ESFT/3-training-system)
> DeepWiki deepseek-ai/ESFT

# Training System

  Relevant source files 
 - [README.md](https://github.com/deepseek-ai/ESFT/blob/579a7711/README.md?plain=1)
 - [train.py](https://github.com/deepseek-ai/ESFT/blob/579a7711/train.py)
 - [train_ep.py](https://github.com/deepseek-ai/ESFT/blob/579a7711/train_ep.py)
 
  
## Purpose and Scope

 This document provides a comprehensive overview of the ESFT training system, which is responsible for fine-tuning models using the Expert-Specialized Fine-Tuning approach. This system enables efficient customization of Large Language Models (LLMs) with Mixture-of-Experts (MoE) architecture by selectively training only task-relevant experts while keeping others frozen.

 The document covers the standard training pipeline, expert parallelism training, data preparation, and the distributed architecture used for efficient multi-GPU training. For information about expert evaluation and scoring, see [Expert Evaluation System](https://deepwiki.com/deepseek-ai/ESFT/2-expert-evaluation-system).

 
## Training System Overview

 The ESFT training system consists of two main implementations:

 
 - **Standard Training Pipeline** - A single-process implementation suitable for smaller models or limited GPU resources
 - **Expert Parallelism (EP) Training** - A distributed implementation optimized for multi-GPU training with expert parallelism
 
 Both implementations are built on the Hugging Face Trainer API but differ in how they distribute model components across GPUs and synchronize gradients.

 
```

```

 Sources: [train.py1-117](https://github.com/deepseek-ai/ESFT/blob/579a7711/train.py#L1-L117) [train_ep.py1-162](https://github.com/deepseek-ai/ESFT/blob/579a7711/train_ep.py#L1-L162) [README.md79-97](https://github.com/deepseek-ai/ESFT/blob/579a7711/README.md?plain=1#L79-L97)

 
## Standard Training Pipeline

 The standard training pipeline (`train.py`) is designed for simpler deployment scenarios where expert parallelism is not required. This pipeline:

 
 - Loads a pre-trained DeepseekV2 model
 - Applies ESFT adaptation based on expert configuration
 - Prepares training data
 - Initializes the Hugging Face Trainer
 - Trains the model with selective expert fine-tuning
 - Saves checkpoints
 
 
```

```

 
### Key Components

 
 - **Model Loading**: Loads the DeepseekV2ForCausalLM model with flash attention
 - **ESFT Adaptation**: Applies expert configuration to selectively enable/disable training for specific experts
 - **Data Preparation**: Processes training data from JSONL files
 - **Training Configuration**: Uses YAML configuration for training parameters
 - **Checkpointing**: Saves model state at regular intervals and at the end of training
 
 Sources: [train.py17-114](https://github.com/deepseek-ai/ESFT/blob/579a7711/train.py#L17-L114)

 
## Expert Parallelism Training

 The expert parallelism training pipeline (`train_ep.py`) is an optimized implementation for distributed training across multiple GPUs. It:

 
 - Initializes parallel processing groups
 - Distributes experts across GPUs
 - Synchronizes gradients across expert parallelism (EP) and expert data parallelism (EDP) groups
 - Handles custom gradient communication between GPUs
 
 
```

```

 
### Key Components

 
 - **Parallel Group Initialization**: Initializes EP and EDP process groups for distributed training
 - **Expert Distribution**: Assigns experts to different GPU groups
 - **Custom All-to-All Communication**: Handles cross-GPU communication for expert outputs
 - **Gradient Synchronization**: Custom implementation for synchronizing gradients across distributed experts
 - **EP Size Configuration**: Controls number of GPUs per expert parallel group
 
 Sources: [train_ep.py17-159](https://github.com/deepseek-ai/ESFT/blob/579a7711/train_ep.py#L17-L159)

 
## Data Preparation Pipeline

 Both training implementations use the same data preparation approach:

 
```

```

 The data preparation process involves:

 
 - Loading JSONL-formatted training data
 - Tokenizing and formatting inputs and targets
 - Optional concatenation of examples to fixed sequence length
 - Creating PyTorch TensorDatasets
 - Splitting into training and validation sets
 
 Sources: [train.py45-57](https://github.com/deepseek-ai/ESFT/blob/579a7711/train.py#L45-L57) [train_ep.py53-65](https://github.com/deepseek-ai/ESFT/blob/579a7711/train_ep.py#L53-L65)

 
## Training Configuration

 The training system uses a YAML configuration file to specify training parameters:

 
| Parameter | Description | Default Value |
|---|---|---|
| seed | Random seed for reproducibility | 42 |
| steps | Maximum training steps | 1000 |
| per_device_batch_size | Batch size per GPU | 4 |
| warmup_steps | Learning rate warmup steps | 100 |
| weight_decay | Weight decay for optimization | 0.01 |
| logging_steps | Steps between logging | 10 |
| save_steps | Steps between checkpoints | 100 |
| eval_steps | Steps between evaluations | 100 |
| gradient_accumulation_steps | Steps for gradient accumulation | 1 |
| learning_rate | Learning rate | 5e-5 |
| optim | Optimizer type | 'adamw_torch' |
| seq_length | Maximum sequence length | 2048 |
| random_concat_ratio | Ratio for random concatenation | 0.5 |
| gradient_checkpointing | Enable gradient checkpointing | true |
| ep_size | Expert parallelism group size | 1 |

 Additional expert parallelism parameters are configured through the EP initialization process.

 Sources: [train.py60-85](https://github.com/deepseek-ai/ESFT/blob/579a7711/train.py#L60-L85) [train_ep.py68-94](https://github.com/deepseek-ai/ESFT/blob/579a7711/train_ep.py#L68-L94)

 
## Expert Distribution Architecture

 The expert parallelism training distributes experts across GPU groups for efficient parallel processing:

 
```

```

 The expert distribution architecture allows:

 
 - **Expert Parallelism (EP)**: Distributes different experts across GPU groups
 - **Expert Data Parallelism (EDP)**: Synchronizes gradients for same expert group across processes
 - **Custom All-to-All Communication**: Handles routing between experts during forward/backward pass
 
 Sources: [train_ep.py49-51](https://github.com/deepseek-ai/ESFT/blob/579a7711/train_ep.py#L49-L51) [train_ep.py102-121](https://github.com/deepseek-ai/ESFT/blob/579a7711/train_ep.py#L102-L121)

 
## ESFT Model Adaptation

 The adaptation process converts a standard DeepseekV2 model to an ESFT-enabled model:

 
```

```

 The ESFT adaptation selectively enables or disables training for specific experts based on the expert configuration generated during the evaluation phase.

 Sources: [train.py93-94](https://github.com/deepseek-ai/ESFT/blob/579a7711/train.py#L93-L94) [train_ep.py101-106](https://github.com/deepseek-ai/ESFT/blob/579a7711/train_ep.py#L101-L106)

 
## Gradient Synchronization

 For expert parallelism training, custom gradient synchronization is implemented:

 
```

```

 The custom gradient synchronization:

 
 - Overrides the default backward method of the accelerator
 - Identifies expert parameters requiring synchronization
 - Performs all-reduce operations across EDP groups
 - Ensures consistent gradient updates across distributed experts
 
 Sources: [train_ep.py132-142](https://github.com/deepseek-ai/ESFT/blob/579a7711/train_ep.py#L132-L142)

 
## Checkpointing and Model Saving

 Both training implementations implement model checkpointing with different approaches for distributed training:

 
### Standard Training

 
 - Saves complete model and tokenizer at regular intervals
 - Supports resuming from checkpoints
 - Stores best model based on evaluation loss
 
 
### Expert Parallelism Training

 
 - Coordinates checkpoint saving across processes
 - Only process 0 (or processes < `ep_size`) save their portion of the model
 - Handles proper resumption from distributed checkpoints
 
 Sources: [train.py105-112](https://github.com/deepseek-ai/ESFT/blob/579a7711/train.py#L105-L112) [train_ep.py145-156](https://github.com/deepseek-ai/ESFT/blob/579a7711/train_ep.py#L145-L156)
