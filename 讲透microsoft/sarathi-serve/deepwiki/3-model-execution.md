<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/sarathi-serve · page 3 Model Execution · fetched 2026-10-26 -->

# Model Execution

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [sarathi/model_executor/model_runner.py](sarathi/model_executor/model_runner.py)
- [sarathi/model_executor/models/mistral.py](sarathi/model_executor/models/mistral.py)
- [sarathi/model_executor/models/mixtral.py](sarathi/model_executor/models/mixtral.py)

</details>



This document explains how Sarathi-Serve executes language models during inference, covering the model execution workflow, model implementations, and key optimization mechanisms. For information about attention mechanisms specifically, see [Attention Mechanisms](#3.1). For details on parallel processing configurations, see [Parallel Processing](#3.3).

## Model Execution Overview

Model execution in Sarathi-Serve refers to the process of running inference on a language model, from preparing input tokens to generating output tokens. The framework supports various model architectures (like Mistral and Mixtral) and employs optimizations for high-throughput, low-latency inference.

```mermaid
flowchart TD
    subgraph "Model Execution Flow"
        A["Input Preparation"] --> B["Model Forward Pass"]
        B --> C["Token Sampling"]
        C --> D["Output Generation"]
        
        B --> B1["Embedding Layer"]
        B --> B2["Transformer Layers"]
        B --> B3["Output Layer"]
        
        B2 --> B2A["Self-Attention"]
        B2 --> B2B["Feed-Forward/MoE"]
    end
```

Sources: [sarathi/model_executor/model_runner.py:225-257]()

## ModelRunner

The `ModelRunner` class is the central component responsible for model execution, handling input preparation, model initialization, and inference.

```mermaid
classDiagram
    class ModelRunner {
        +config: SystemConfig
        +device: torch.device
        +rank: int
        +attention_backend_wrapper: BaseAttentionWrapper
        +model: CausalLM
        +sampler: Sampler
        +init_kv_cache(num_gpu_blocks)
        +_prepare_inputs(seq_metadata_list)
        +run(seq_metadata_list)
        +profile_num_available_blocks(block_size, gpu_memory_utilization)
    }

    ModelRunner --> "1" BaseAttentionWrapper: uses
    ModelRunner --> "1" CausalLM: executes
    ModelRunner --> "1" Sampler: samples tokens
```

Sources: [sarathi/model_executor/model_runner.py:24-66]()

### Input Preparation

Before executing the model, `ModelRunner` prepares inputs by:
1. Collecting tokens from prompt sequences (for prefill phase)
2. Collecting last tokens from generation sequences (for decode phase)
3. Converting inputs to tensors and optimizing for GPU execution

```mermaid
flowchart LR
    A["Input Sequences"] --> B["Extract Tokens"]
    B --> C["Extract Positions"]
    C --> D["Pad to Alignment"]
    D --> E["Convert to Tensors"]
```

Sources: [sarathi/model_executor/model_runner.py:67-117]()

### Model Execution Process

The `run` method in `ModelRunner` is the main entry point for model execution:

```mermaid
sequenceDiagram
    participant Scheduler
    participant ModelRunner
    participant AttentionBackend
    participant Model
    participant Sampler
    
    Scheduler->>ModelRunner: run(seq_metadata_list)
    ModelRunner->>ModelRunner: _prepare_inputs()
    ModelRunner->>AttentionBackend: begin_forward()
    ModelRunner->>Model: forward(hidden_states, positions, attention_backend_wrapper)
    
    loop For each layer
        Model->>Model: Process layer
        Model->>AttentionBackend: forward(q, k, v)
    end
    
    Model-->>ModelRunner: Return logits
    ModelRunner->>Sampler: Sample next tokens
    ModelRunner->>AttentionBackend: end_forward()
    ModelRunner-->>Scheduler: Return sampled tokens
```

Sources: [sarathi/model_executor/model_runner.py:225-257]()

## Model Implementations

Sarathi-Serve supports different model architectures, each with its own implementation. The model implementations follow a similar structure, with architecture-specific differences.

### Common Model Structure

```mermaid
classDiagram
    class BaseCausalLM {
        +config
        +model
        +lm_head
        +forward(hidden_states, positions, attention_backend_wrapper)
        +load_weights(model_name_or_path)
    }
    
    class BaseModel {
        +embed_tokens
        +layers
        +norm
        +forward(hidden_states, positions, attention_backend_wrapper)
    }
    
    class DecoderLayer {
        +self_attn
        +mlp/moe
        +layernorms
        +forward(positions, hidden_states, layer_cache_idx, attention_backend_wrapper)
    }
    
    BaseCausalLM --> BaseModel: contains
    BaseModel --> DecoderLayer: contains
```

Sources: [sarathi/model_executor/models/mistral.py:292-316](), [sarathi/model_executor/models/mixtral.py:317-341]()

### Model-Specific Implementations

#### Mistral Model

The Mistral model uses a standard feed-forward MLP in each decoder layer:

```mermaid
flowchart TD
    subgraph "MistralDecoderLayer"
        A["Input"] --> B["Self-Attention"]
        B --> C["MLP (Feed-Forward)"]
        C --> D["Output"]
        
        B1["Input LayerNorm"] --> B
        C1["Post-Attention LayerNorm"] --> C
    end
```

Sources: [sarathi/model_executor/models/mistral.py:180-232]()

#### Mixtral Model

The Mixtral model uses a Mixture of Experts (MoE) architecture in place of the standard MLP:

```mermaid
flowchart TD
    subgraph "MixtralDecoderLayer"
        A["Input"] --> B["Self-Attention"]
        B --> C["Mixture of Experts (MoE)"]
        C --> D["Output"]
        
        B1["Input LayerNorm"] --> B
        C1["Post-Attention LayerNorm"] --> C
        
        C --> C2["Router/Gate"]
        C2 --> C3["Select Top-k Experts"]
        C3 --> C4["Combine Expert Outputs"]
    end
```

Sources: [sarathi/model_executor/models/mixtral.py:194-258]()

## Parallelism in Model Execution

Sarathi-Serve implements two forms of parallelism for model execution:

### Tensor Parallelism

Tensor parallelism splits individual tensors across multiple GPUs:

```mermaid
flowchart TD
    subgraph "Tensor Parallelism"
        A["Model Weights"] --> B["Split Across GPUs"]
        
        subgraph "GPU 0"
            C0["Weight Shard 0"]
        end
        
        subgraph "GPU 1"
            C1["Weight Shard 1"]
        end
        
        subgraph "GPU 2"
            C2["Weight Shard 2"]
        end
        
        B --> C0
        B --> C1
        B --> C2
        
        C0 --> D0["Local Computation"]
        C1 --> D1["Local Computation"]
        C2 --> D2["Local Computation"]
        
        D0 --> E["All-Reduce/All-Gather"]
        D1 --> E
        D2 --> E
        
        E --> F["Final Output"]
    end
```

Sources: [sarathi/model_executor/models/mistral.py:128-177](), [sarathi/model_executor/models/mixtral.py:146-191]()

### Pipeline Parallelism

Pipeline parallelism splits the model layers across multiple GPUs:

```mermaid
flowchart LR
    subgraph "Pipeline Parallelism"
        A["Input"] --> B["GPU 0: Embedding + Layers 0-N/3"]
        B --> C["GPU 1: Layers N/3+1-2N/3"]
        C --> D["GPU 2: Layers 2N/3+1-N + Output"]
        D --> E["Result"]
    end
```

Sources: [sarathi/model_executor/models/mistral.py:235-289](), [sarathi/model_executor/models/mixtral.py:261-316]()

## Memory Optimization

Model execution in Sarathi-Serve incorporates several memory optimizations:

1. **KV Cache Management**: Stores key-value pairs to avoid recomputing them for already processed tokens
2. **Tensor Alignment**: Pads tensors to optimize for hardware acceleration (tensor cores)
3. **Memory Profiling**: Profiles memory usage to allocate optimal number of blocks for KV cache

```mermaid
flowchart TD
    subgraph "Memory Optimization"
        A["ModelRunner.profile_num_available_blocks()"] --> B["Empty CUDA Cache"]
        B --> C["Execute Model Profile Run"]
        C --> D["Measure Peak Memory"]
        D --> E["Calculate Available Blocks"]
        E --> F["Initialize KV Cache"]
    end
```

Sources: [sarathi/model_executor/model_runner.py:119-223]()

## Token Sampling

After model execution, Sarathi-Serve uses a sampling mechanism to select the next token:

```mermaid
flowchart LR
    A["Model Logits"] --> B["Sampler"]
    B --> C["Apply Sampling Parameters"]
    C --> D["Select Next Token"]
    
    C --> C1["Temperature"]
    C --> C2["Top-K/Top-P"]
    C --> C3["Repetition Penalty"]
```

Sources: [sarathi/model_executor/model_runner.py:250-252]()

## Model Execution Workflow

The complete model execution workflow combines all these components:

```mermaid
flowchart TD
    A["Scheduler Selects Sequences"] --> B["Prepare Input Tokens & Positions"]
    B --> C["Initialize Attention Backend"]
    C --> D["Execute Model Forward Pass"]
    
    D --> D1["Embedding Lookup"]
    D1 --> D2["Process Through Transformer Layers"]
    D2 --> D3["Process Final Norm Layer"]
    
    D2 --> D2A["Self-Attention with KV Cache"]
    D2 --> D2B["Feed-Forward or MoE"]
    
    D3 --> E["Sample Next Token"]
    E --> F["Update Sequence State"]
    F --> G["Continue Until Completion"]
```

Sources: [sarathi/model_executor/model_runner.py:225-257](), [sarathi/model_executor/models/mistral.py:292-316](), [sarathi/model_executor/models/mixtral.py:317-341]()

---

