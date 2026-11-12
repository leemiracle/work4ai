<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/picotron · page 5 Parallelism Implementations · fetched 2026-10-26 -->

# Parallelism Implementations

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CITATION.cff](CITATION.cff)
- [README.md](README.md)
- [extract_metrics.py](extract_metrics.py)
- [picotron/pipeline_parallel/pipeline_parallel.py](picotron/pipeline_parallel/pipeline_parallel.py)
- [picotron/utils.py](picotron/utils.py)

</details>



## Purpose and Scope

This document provides a technical overview of the parallelism strategies implemented in Picotron for distributed training of large language models. It covers the 4D parallelism approach - Data, Tensor, Pipeline, and Context parallel - and details how each strategy is implemented. For information about the general system architecture, see [System Architecture](#2).

## Introduction to 4D Parallelism

Picotron implements a 4D parallelism strategy that combines four complementary approaches to distribute model training across multiple GPUs:

```mermaid
graph TD
    subgraph "4D Parallelism"
        DP["Data Parallelism (DP)"]
        TP["Tensor Parallelism (TP)"]
        PP["Pipeline Parallelism (PP)"]
        CP["Context Parallelism (CP)"]
    end
    
    DP --> |"Replicates model,\nSplits data batches"| Training
    TP --> |"Splits model parameters\nwithin layers"| Training
    PP --> |"Splits model layers\nacross devices"| Training
    CP --> |"Splits input sequences\nacross devices"| Training
    
    subgraph "Training Process"
        Training["Distributed Training"]
    end
```

Sources: [README.md:1-47]()

## Process Group Manager

The Process Group Manager is the central component that establishes and manages the communication groups required for distributed training. It creates four process groups:

1. **Data Parallel Group (DP)**: Processes that work on different batches of data with the same model replica
2. **Tensor Parallel Group (TP)**: Processes that split individual tensors within layers
3. **Pipeline Parallel Group (PP)**: Processes that handle different layers of the model
4. **Context Parallel Group (CP)**: Processes that split sequences along the context dimension

```mermaid
classDiagram
    class ProcessGroupManager {
        +initialize()
        +dp_group
        +tp_group
        +pp_group
        +cp_group
        +world_size
        +dp_world_size
        +tp_world_size
        +pp_world_size
        +cp_world_size
        +rank
        +dp_rank
        +tp_rank
        +pp_rank
        +cp_rank
        +pp_is_first_stage
        +pp_is_last_stage
    }
    
    ProcessGroupManager --> TensorParallel: "Provides groups for"
    ProcessGroupManager --> PipelineParallel: "Provides groups for" 
    ProcessGroupManager --> DataParallel: "Provides groups for"
    ProcessGroupManager --> ContextParallel: "Provides groups for"
```

Sources: [picotron/utils.py:10-11](), [picotron/utils.py:61-78]()

## Pipeline Parallelism

Pipeline parallelism splits the model vertically, assigning different layers to different devices. This allows training of models that are too large to fit on a single device.

### Implementation

The `PipelineParallel` class wraps the base model and distributes its layers across GPUs:

```mermaid
flowchart TD
    subgraph "PipelineParallel Implementation"
        PP["PipelineParallel"] -->|"First stage only"| Embedding
        PP -->|"Distributed evenly"| DecoderLayers["Decoder Layers"]
        PP -->|"Last stage only"| FinalNorm["Final Normalization"]
        PP -->|"Last stage only"| FinalProj["Final Projection"]
        
        DecoderLayers -->|"Layer 0-N"| Device1["Device 0"]
        DecoderLayers -->|"Layer N+1-M"| Device2["Device 1"]
        DecoderLayers -->|"Layer M+1-End"| Device3["Device ..."]
    end
```

Sources: [picotron/pipeline_parallel/pipeline_parallel.py:8-63]()

### Training Strategies

Pipeline Parallelism in Picotron supports two scheduling strategies:

1. **All-Forward-All-Backward (AFAB)**: Performs all forward passes first, then all backward passes
2. **One-Forward-One-Backward (1F1B)**: Interleaves forward and backward passes to improve GPU utilization

```mermaid
sequenceDiagram
    participant R0 as "Rank 0"
    participant R1 as "Rank 1"
    participant R2 as "Rank 2"
    
    Note over R0,R2: 1F1B Pipeline Schedule
    
    R0->>R0: F(mb1)
    R0->>R1: Send F(mb1)
    R0->>R0: F(mb2)
    R1->>R1: F(mb1)
    R0->>R1: Send F(mb2)
    R1->>R2: Send F(mb1)
    R1->>R1: F(mb2)
    R2->>R2: F(mb1)
    R2->>R1: Send B(mb1)
    R1->>R2: Send F(mb2)
    R1->>R0: Send B(mb1)
    R2->>R2: F(mb2)
    R0->>R0: B(mb1)
    R1->>R1: B(mb1)
    R2->>R1: Send B(mb2)
    R1->>R0: Send B(mb2)
    R0->>R0: B(mb2)
    R1->>R1: B(mb2)
    R2->>R2: B(mb2)
    
    Note over R0,R2: F = Forward pass, B = Backward pass, mb = microbatch
```

Sources: [picotron/pipeline_parallel/pipeline_parallel.py:77-120](), [picotron/pipeline_parallel/pipeline_parallel.py:122-214]()

### Pipeline Communication

Pipeline parallelism requires efficient communication between adjacent stages in the pipeline:

```mermaid
flowchart LR
    subgraph "Pipeline Communication"
        FwdRecv["Receive Forward"] --> ForwardPass["Forward Pass"]
        ForwardPass --> FwdSend["Send Forward"]
        BwdRecv["Receive Backward"] --> BackwardPass["Backward Pass"]
        BackwardPass --> BwdSend["Send Backward"]
    end
    
    FwdSend -.-> |"Next stage"| FwdRecv
    BwdSend -.-> |"Previous stage"| BwdRecv
```

For the 1F1B schedule, Picotron uses bidirectional communication to reduce overhead:

```mermaid
flowchart LR
    subgraph "Bidirectional Communication (1F1B)"
        SendFwdRecvBwd["send_fwd_recv_bwd()"] 
        SendBwdRecvFwd["send_bwd_recv_fwd()"]
    end
    
    SendFwdRecvBwd <-.-> |"Simultaneous\nCommunication"| SendBwdRecvFwd
```

Sources: [picotron/pipeline_parallel/pipeline_parallel.py:84-85](), [picotron/pipeline_parallel/pipeline_parallel.py:185-202]()

## Tensor Parallelism

Tensor parallelism splits individual layers horizontally by partitioning the parameters of specific operations across multiple devices.

### Implementation

Tensor parallelism in Picotron primarily targets the most parameter-intensive parts of the model:

```mermaid
flowchart LR
    subgraph "Tensor Parallel Targets"
        Attention["Attention Matrices"]
        MLP["MLP Layers"]
        Embedding["Embedding Layers"]
        FinalProj["Final Projection"]
    end
    
    TP["Tensor Parallelism"] --> |"Shards"| Attention
    TP --> |"Shards"| MLP
    TP --> |"Shards"| Embedding
    TP --> |"Shards"| FinalProj
```

The utils.py file contains functions that help identify tensor-parallel parameters and handle their distribution:

```mermaid
flowchart TD
    subgraph "Tensor Parallel Parameter Counting"
        CountParams["get_num_params()"] --> TPDetect["Detect TP parameters"]
        TPDetect --> Scale["Scale by tp_world_size"]
        Scale --> Total["Calculate total parameters"]
    end
```

Sources: [picotron/utils.py:51-80]()

## Data Parallelism

Data parallelism replicates the model across multiple devices, with each device processing a different subset of the training data.

### Implementation

```mermaid
flowchart TD
    subgraph "Data Parallel System"
        DP["Data Parallelism"]
        Batch["Full Batch"]
        GradSync["Gradient Synchronization"]
    end
    
    Batch --> |"Split"| MB1["Microbatch 1"]
    Batch --> |"Split"| MB2["Microbatch 2"]
    Batch --> |"Split"| MB3["Microbatch N"]
    
    MB1 --> |"Device 1"| Replica1["Model Replica 1"]
    MB2 --> |"Device 2"| Replica2["Model Replica 2"]
    MB3 --> |"Device N"| ReplicaN["Model Replica N"]
    
    Replica1 --> GradSync
    Replica2 --> GradSync
    ReplicaN --> GradSync
```

Picotron implements gradient synchronization across data-parallel ranks through the following mechanism in `utils.py`:

```mermaid
flowchart LR
    subgraph "Data Parallel Gradient Synchronization"
        Loss["Loss Computation"]
        ReduceLoss["average_loss_across_dp_cp_ranks()"]
        AllReduce["dist.all_reduce()"]
    end
    
    Loss --> ReduceLoss
    ReduceLoss --> |"Uses CP-DP group"| AllReduce
    AllReduce --> |"Returns averaged loss"| Result["Synchronized Result"]
```

Sources: [picotron/utils.py:94-99]()

## Context Parallelism

Context parallelism splits input sequences across multiple devices, allowing each device to process a portion of the input context.

### Implementation

Context parallelism is particularly useful for handling long sequences that would exceed memory constraints on a single device:

```mermaid
flowchart LR
    subgraph "Context Parallelism"
        Input["Long Input Sequence"]
        CP["Context Parallelism"]
    end
    
    Input --> |"Split"| Chunk1["Sequence Chunk 1"]
    Input --> |"Split"| Chunk2["Sequence Chunk 2"]
    Input --> |"Split"| ChunkN["Sequence Chunk N"]
    
    Chunk1 --> |"Device 1"| Attn1["Attention Computation 1"]
    Chunk2 --> |"Device 2"| Attn2["Attention Computation 2"]
    ChunkN --> |"Device N"| AttnN["Attention Computation N"]
    
    Attn1 --> CP
    Attn2 --> CP
    AttnN --> CP
```

Context parallelism requires specialized communication for attention computations to ensure correct results across sequence boundaries.

Sources: [picotron/utils.py:94-99]()

## Interaction Between Parallelism Strategies

The 4D parallelism strategies work together to enable efficient training of large models:

```mermaid
graph TD
    subgraph "4D Parallelism Integration"
        DP["Data Parallelism"]
        TP["Tensor Parallelism"]
        PP["Pipeline Parallelism"]
        CP["Context Parallelism"]
    end
    
    subgraph "Process Groups"
        DPGroup["DP Group"]
        TPGroup["TP Group"]
        PPGroup["PP Group"]
        CPGroup["CP Group"]
        CPDP["CP-DP Group"]
    end
    
    DP --> DPGroup
    TP --> TPGroup
    PP --> PPGroup
    CP --> CPGroup
    
    CP --> CPDP
    DP --> CPDP
    
    subgraph "Model Distribution"
        CPDP --> |"Loss Synchronization"| LossSync["average_loss_across_dp_cp_ranks()"]
        PP --> |"Layer Distribution"| LayerDist["PipelineParallel"]
        TP --> |"Parameter Sharding"| ParamShard["Sharded Parameters"]
    end
```

The utils.py file contains several functions that facilitate the interaction between different parallelism strategies:

- `get_num_params()`: Calculates total parameters accounting for tensor and pipeline parallelism
- `average_loss_across_dp_cp_ranks()`: Synchronizes loss values across data-parallel and context-parallel ranks

Sources: [picotron/utils.py:51-80](), [picotron/utils.py:94-99]()

## Pipeline Parallelism Implementation Details

The pipeline parallelism implementation in Picotron deserves special attention due to its complexity:

### PipelineParallel Class

The `PipelineParallel` class wraps the base model and distributes its layers:

1. The `__init__` method divides the model based on pipeline rank
2. The `distribute_layers` method calculates which layers should be assigned to each GPU
3. The `forward` and `backward` methods handle the flow of data through the pipeline

### Pipeline Training Strategies

```mermaid
flowchart TD
    subgraph "Pipeline Training Strategies"
        AFAB["All-Forward-All-Backward (AFAB)"]
        OneForwardOneBackward["One-Forward-One-Backward (1F1B)"]
    end
    
    AFAB --> |"Implements"| AFABFunc["train_step_pipeline_afab()"]
    OneForwardOneBackward --> |"Implements"| OneForwardOneBackwardFunc["train_step_pipeline_1f1b()"]
    
    AFABFunc --> |"Phases"| AF["All Forward Passes"]
    AF --> |"Then"| AB["All Backward Passes"]
    
    OneForwardOneBackwardFunc --> |"Phases"| Warmup["1. Warmup Phase"]
    Warmup --> |"Then"| SteadyState["2. Steady State"]
    SteadyState --> |"Then"| Cooldown["3. Cooldown Phase"]
```

The 1F1B strategy is more complex but provides better hardware utilization:

1. **Warmup Phase**: Fills the pipeline with forward passes
2. **Steady State**: Alternates between forward and backward passes
3. **Cooldown Phase**: Completes remaining backward passes

Sources: [picotron/pipeline_parallel/pipeline_parallel.py:77-120](), [picotron/pipeline_parallel/pipeline_parallel.py:122-214]()

## Performance Considerations

Picotron's parallelism implementations are designed for educational clarity rather than maximum performance, but still achieve reasonable efficiency:

```mermaid
flowchart LR
    subgraph "Model Size & Parallelism Strategy"
        Small["Small Models"]
        Medium["Medium Models"]
        Large["Large Models"]
    end
    
    Small --> |"Best with"| DP["DP Only"]
    Medium --> |"Best with"| DPTP["DP + TP"]
    Large --> |"Best with"| Full4D["Full 4D Parallelism"]
```

As noted in the README, Picotron can achieve:
- ~38% MFU (Model FLOPs Utilization) on a LLaMA-2-7B model using 64 H100 GPUs
- ~50% MFU on the SmolLM-1.7B model with 8 H100 GPUs

Sources: [README.md:6-8](), [picotron/utils.py:40-49]()

## Integration with Other Systems

The parallelism implementations interface with other components in the Picotron system:

```mermaid
flowchart TD
    subgraph "Parallelism Integration"
        PP["Pipeline Parallel"]
        TP["Tensor Parallel"]
        DP["Data Parallel"]
        CP["Context Parallel"]
    end
    
    subgraph "Supporting Systems"
        Checkpoint["Checkpoint System"]
        DataLoader["Data Loader"]
        Model["Model Definition"]
    end
    
    PP --> |"Layer Distribution"| Model
    TP --> |"Parameter Sharding"| Model
    DP --> |"Gradient Synchronization"| Optimizer["Optimizer"]
    CP --> |"Sequence Splitting"| DataLoader
    
    Checkpoint --> |"Handles"| ShardedSave["Sharded Checkpoint Saving"]
    Checkpoint --> |"Handles"| ShardedLoad["Sharded Checkpoint Loading"]
```

Sources: [picotron/utils.py:51-80]()

## Conclusion

Picotron's 4D parallelism implementation provides a clear, educational framework for understanding distributed training strategies. While designed for simplicity rather than maximum performance, it still achieves reasonable efficiency for training large language models.

---

