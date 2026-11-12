<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/picotron_tutorial · page 2 Tutorial Progression · fetched 2026-10-26 -->

# Tutorial Progression

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [assets/llama1B_sanity_check.png](assets/llama1B_sanity_check.png)
- [requirements.txt](requirements.txt)
- [setup.py](setup.py)
- [step1_modeling/train.py](step1_modeling/train.py)

</details>



This document outlines the step-by-step progression of the Picotron tutorial, which systematically builds distributed training capabilities from a simple single-process model to full 3D parallelism. The tutorial demonstrates how to incrementally add tensor parallelism, data parallelism, and pipeline parallelism to a LLaMA transformer model.

For detailed implementation of individual components, see [Core Architecture](#3). For specific parallelism strategies, see [Parallelism Strategies](#4).

## Tutorial Overview

The Picotron tutorial follows a progressive complexity model, where each step builds upon the previous ones while introducing new distributed training concepts. The progression moves from basic model training to sophisticated 3D parallelism combining three parallelization strategies.

### Step Progression Flow

```mermaid
graph TD
    STEP1["step1_modeling<br/>Single Process Training<br/>Basic LLaMA + AdamW"]
    STEP2["step2_process_group_manager<br/>Distributed Infrastructure<br/>ProcessGroupManager"]
    STEP3["step3_dataloader<br/>Data Pipeline<br/>MicroBatchDataLoader + Tokenization"]
    STEP4["step4_tensor_parallel<br/>Model Sharding<br/>ColumnParallelLinear + RowParallelLinear"]
    STEP5["step5_data_parallel_naive<br/>Gradient Synchronization<br/>DataParallelNaive"]
    STEP6["step6_data_parallel_bucket<br/>Optimized Gradients<br/>DataParallelBucket"]
    STEP7["step7_pipeline_parallel_afab<br/>Stage Separation<br/>AFAB Engine"]
    STEP8["step8_pipeline_parallel_1f1b<br/>Overlapped Execution<br/>1F1B Engine"]
    FINAL["3D Parallelism<br/>Combined TP + DP + PP<br/>--tp_size --dp_size --pp_size"]
    
    STEP1 --> STEP2
    STEP2 --> STEP3
    STEP3 --> STEP4
    STEP4 --> STEP5
    STEP5 --> STEP6
    STEP6 --> STEP7
    STEP7 --> STEP8
    STEP8 --> FINAL
```

Sources: [README.md:29-48]()

### Command Line Evolution

The tutorial progression is reflected in the increasing complexity of command line arguments, showing how new parallelism dimensions are added:

| Step | Key Arguments | Purpose |
|------|---------------|---------|
| Step 1 | `--micro_batch_size`, `--seq_len` | Basic training parameters |
| Step 2 | `--nproc_per_node` | Multi-process setup |
| Step 3 | `--gradient_accumulation_steps`, `--num_proc` | Data pipeline optimization |
| Step 4 | `--tp_size` | Tensor parallelism dimension |
| Step 5-6 | `--dp_size` | Data parallelism dimension |
| Step 7-8 | `--pp_size`, `--pp_engine` | Pipeline parallelism dimension |
| 3D | `--tp_size --dp_size --pp_size` | All dimensions combined |

Sources: [README.md:29-48]()

## Foundation Steps (1-3)

### Step 1: Basic Model Training

```mermaid
graph LR
    TRAIN["train.py<br/>Single Process Script"]
    CONFIG["AutoConfig<br/>HuggingFace Config"]
    MODEL["Llama<br/>Transformer Model"]
    OPTIM["AdamW<br/>Optimizer"]
    DUMMY["torch.randint<br/>Dummy Data"]
    
    TRAIN --> CONFIG
    CONFIG --> MODEL
    MODEL --> OPTIM
    DUMMY --> MODEL
    MODEL --> LOSS["F.cross_entropy<br/>Language Modeling Loss"]
```

Step 1 establishes the fundamental training loop with a LLaMA model running on a single process. The implementation in `step1_modeling/train.py` sets up the basic components: model initialization, optimizer setup, and a simple forward-backward pass with dummy data.

Key code entities:
- `Llama` class from `model.py`
- `torch.distributed.init_process_group` for basic distributed setup
- `AdamW` optimizer with learning rate scheduling
- Cross-entropy loss computation with vocabulary projection

Sources: [step1_modeling/train.py:1-97]()

### Step 2: Process Group Management

Step 2 introduces the `ProcessGroupManager` class, which becomes the central coordinator for all distributed training operations. This step doesn't change the training logic but establishes the infrastructure needed for multi-GPU coordination.

### Step 3: Data Loading Pipeline

Step 3 replaces dummy data with a real data pipeline featuring the `MicroBatchDataLoader` class. This step introduces tokenization, gradient accumulation, and proper batch management for distributed training scenarios.

Sources: [README.md:31-32]()

## Parallelism Integration Steps (4-8)

### Tensor Parallelism (Step 4)

```mermaid
graph TB
    subgraph "Model Transformation"
        BASE["Base Llama Model"]
        TP_WRAP["apply_tensor_parallel<br/>Tensor Parallel Wrapper"]
        COL_PAR["ColumnParallelLinear<br/>Split Output Features"]
        ROW_PAR["RowParallelLinear<br/>Split Input Features"]
        VOCAB_PAR["VocabParallelEmbedding<br/>Split Vocabulary"]
    end
    
    subgraph "Process Groups"
        TP_GROUP["Tensor Parallel Group<br/>tp_size processes"]
        ALL_REDUCE["All-Reduce Communication<br/>Weight Synchronization"]
    end
    
    BASE --> TP_WRAP
    TP_WRAP --> COL_PAR
    TP_WRAP --> ROW_PAR
    TP_WRAP --> VOCAB_PAR
    
    TP_GROUP --> ALL_REDUCE
    ALL_REDUCE --> COL_PAR
    ALL_REDUCE --> ROW_PAR
```

Step 4 introduces tensor parallelism by sharding model weights across multiple GPUs. The `apply_tensor_parallel` function transforms linear layers into parallel variants that communicate through all-reduce operations.

Command: `torchrun --nproc_per_node 4 train.py --tp_size 4`

Sources: [README.md:34-36]()

### Data Parallelism (Steps 5-6)

Steps 5 and 6 implement two approaches to data parallelism:

- **Step 5 (Naive)**: `DataParallelNaive` performs simple all-reduce operations on gradients
- **Step 6 (Bucketed)**: `DataParallelBucket` optimizes communication by bucketing gradients

```mermaid
graph LR
    subgraph "Data Parallel Approaches"
        NAIVE["DataParallelNaive<br/>Simple All-Reduce"]
        BUCKET["DataParallelBucket<br/>Gradient Bucketing"]
    end
    
    subgraph "Communication Patterns"
        ALLREDUCE["torch.distributed.all_reduce<br/>Gradient Synchronization"]
        BUCKETING["Gradient Bucketing<br/>Communication Optimization"]
    end
    
    NAIVE --> ALLREDUCE
    BUCKET --> BUCKETING
    BUCKETING --> ALLREDUCE
```

Command: `torchrun --nproc_per_node 4 train.py --dp_size 4`

Sources: [README.md:38-40]()

### Pipeline Parallelism (Steps 7-8)

Steps 7 and 8 implement pipeline parallelism with two execution engines:

- **Step 7 (AFAB)**: Activation Forward-Activation Backward engine with separated phases
- **Step 8 (1F1B)**: One Forward One Backward engine with overlapped execution

```mermaid
graph TB
    subgraph "Pipeline Engines"
        AFAB["AFAB Engine<br/>Forward-Then-Backward"]
        F1B1["1F1B Engine<br/>Overlapped Pipeline"]
    end
    
    subgraph "Pipeline Stages"
        STAGE0["Pipeline Stage 0<br/>Embedding + Early Layers"]
        STAGE1["Pipeline Stage 1<br/>Middle Layers"]  
        STAGE2["Pipeline Stage 2<br/>Late Layers + Output"]
    end
    
    subgraph "Communication"
        P2P["torch.distributed.send/recv<br/>Point-to-Point Activation Transfer"]
    end
    
    AFAB --> STAGE0
    AFAB --> STAGE1
    AFAB --> STAGE2
    F1B1 --> STAGE0
    F1B1 --> STAGE1
    F1B1 --> STAGE2
    
    STAGE0 --> P2P
    STAGE1 --> P2P
    STAGE2 --> P2P
```

Command: `torchrun --nproc_per_node 4 train.py --pp_size 4 --pp_engine 1f1b`

Sources: [README.md:42-44]()

## 3D Parallelism Integration

The final step combines all three parallelism strategies into a single training run. This requires careful coordination between tensor parallel groups, data parallel groups, and pipeline parallel stages.

### 3D Parallelism Architecture

```mermaid
graph TB
    subgraph "3D Parallelism Coordination"
        TP["Tensor Parallel<br/>--tp_size 2<br/>Model Weight Sharding"]
        DP["Data Parallel<br/>--dp_size 2<br/>Gradient Synchronization"]  
        PP["Pipeline Parallel<br/>--pp_size 2<br/>Stage Distribution"]
    end
    
    subgraph "Process Group Management"
        PGM["ProcessGroupManager<br/>Coordinate All Groups"]
        TP_GROUP["TP Process Groups<br/>Within Each Stage"]
        DP_GROUP["DP Process Groups<br/>Across Stages"]
        PP_GROUP["PP Process Groups<br/>Between Stages"]
    end
    
    subgraph "Training Execution"
        TRAIN_SCRIPT["train.py<br/>3D Parallelism Script"]
        ENGINE["1F1B Pipeline Engine<br/>Overlapped Execution"]
        SYNC["Multi-Level Synchronization<br/>TP + DP + PP Coordination"]
    end
    
    TP --> PGM
    DP --> PGM
    PP --> PGM
    
    PGM --> TP_GROUP
    PGM --> DP_GROUP
    PGM --> PP_GROUP
    
    TRAIN_SCRIPT --> ENGINE
    ENGINE --> SYNC
```

The 3D parallelism configuration demonstrates the full power of the tutorial's incremental complexity build-up, requiring 8 processes with a 2×2×2 configuration.

Command: `torchrun --nproc_per_node 8 train.py --tp_size 2 --pp_size 2 --pp_engine 1f1b --dp_size 2`

Sources: [README.md:46-47]()

## Tutorial Design Principles

### Incremental Complexity

Each step introduces exactly one new concept while preserving all previous functionality. This allows learners to isolate and understand individual distributed training components before combining them.

### Code Reusability

The tutorial follows a modular design where components from earlier steps are reused in later steps. For example, the `ProcessGroupManager` from Step 2 is used throughout all subsequent steps.

### Verification Strategy

The tutorial includes sanity checks that verify convergence behavior remains consistent across different parallelism configurations, ensuring correctness of the distributed implementations.

Sources: [README.md:24-26]()

---

