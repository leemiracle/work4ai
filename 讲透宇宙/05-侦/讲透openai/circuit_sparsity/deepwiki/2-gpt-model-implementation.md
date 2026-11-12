<!-- source: DeepWiki mcp.deepwiki.com · repo openai/circuit_sparsity · page 2 GPT Model Implementation · fetched 2026-10-26 -->

# GPT Model Implementation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [circuit_sparsity/inference/gpt.py](circuit_sparsity/inference/gpt.py)

</details>



This document provides an overview of the GPT transformer model implementation in `circuit_sparsity/inference/gpt.py`. This implementation is designed specifically to support sparse neural network circuits with extensive instrumentation for activation recording and analysis.

For detailed information on specific components, see:
- Configuration parameters and the `GPT` class: [GPT and GPTConfig](#2.1)
- Internal architecture components: [Model Architecture Components](#2.2)
- Sparsity mechanisms: [Sparsity Features](#2.3)
- Activation recording infrastructure: [Hook System for Activation Recording](#2.4)

## Purpose and Scope

The GPT implementation serves as the core inference engine for sparse circuit analysis. It provides:

1. A lightweight, configurable transformer architecture suitable for CPU/GPU inference
2. Built-in support for activation sparsity (`afrac`) and weight sparsity
3. Integration with the hook system for recording intermediate activations
4. Multiple architectural variants including concatenated position embeddings and attention sinks
5. Compatibility with the visualization and training pipelines

This implementation prioritizes analyzability and configurability over raw performance, making it suitable for research on sparse circuits rather than production deployment.

**Sources:** [circuit_sparsity/inference/gpt.py:1-940](), [README.md:30-58]()

## System Architecture Overview

The following diagram shows how the major classes and modules relate to each other in the GPT implementation:

```mermaid
graph TB
    subgraph "Configuration Layer"
        GPTConfig["GPTConfig<br/>(dataclass)"]
    end
    
    subgraph "Model Class"
        GPT["GPT<br/>(nn.Module)"]
    end
    
    subgraph "Transformer Components"
        Block["Block<br/>(nn.Module)"]
        BlockCatPosEmb["BlockCatPosEmb<br/>(nn.Module)"]
        CausalSelfAttention["CausalSelfAttention<br/>(nn.Module)"]
        CausalSelfAttentionCatPosEmb["CausalSelfAttentionCatPosEmb<br/>(nn.Module)"]
        MLP["MLP<br/>(nn.Module)"]
        MLPCatPosEmb["MLPCatPosEmb<br/>(nn.Module)"]
        LayerNorm["LayerNorm<br/>(nn.Module)"]
        SDPAWithSink["SDPAWithSink<br/>(nn.Module)"]
    end
    
    subgraph "Utilities"
        AbsTopK["AbsTopK<br/>(nn.Module)"]
        load_model["load_model()"]
    end
    
    subgraph "External Integration"
        hook_utils["hook_utils<br/>(hook_save, hook_namespace)"]
        kernels["kernels<br/>(sample_top_k)"]
    end
    
    GPTConfig -->|"configures"| GPT
    GPT -->|"contains h: ModuleList"| Block
    GPT -->|"contains h: ModuleList (if cat_pos_emb)"| BlockCatPosEmb
    
    Block -->|"contains attn"| CausalSelfAttention
    Block -->|"contains mlp"| MLP
    Block -->|"contains ln_1, ln_2"| LayerNorm
    
    BlockCatPosEmb -->|"contains attn"| CausalSelfAttentionCatPosEmb
    BlockCatPosEmb -->|"contains mlp"| MLPCatPosEmb
    
    CausalSelfAttention -->|"uses (if config.sink)"| SDPAWithSink
    
    GPTConfig -->|"provides maybe_activation_sparsity()"| AbsTopK
    
    load_model -->|"instantiates"| GPT
    load_model -->|"reads beeg_config.json"| GPTConfig
    
    GPT -->|"calls hook_save() throughout"| hook_utils
    MLP -->|"calls hook_save()"| hook_utils
    CausalSelfAttention -->|"calls hook_save()"| hook_utils
    
    GPT -->|"uses for init"| kernels
```

**Sources:** [circuit_sparsity/inference/gpt.py:32-940]()

## Model Forward Pass Data Flow

This diagram illustrates how data flows through the model during a forward pass, mapping conceptual operations to specific code entities:

```mermaid
graph TB
    Input["idx<br/>(B, T)<br/>token indices"]
    
    subgraph "Embedding Stage"
        wte["transformer.wte<br/>(Embedding)"]
        wpe["transformer.wpe<br/>(Embedding)"]
        drop["transformer.drop<br/>(Dropout)"]
    end
    
    subgraph "Block Processing"
        Block0["transformer.h[0]<br/>(Block)"]
        BlockN["transformer.h[n]<br/>(Block)"]
        
        subgraph "Inside Each Block"
            ln_1["ln_1<br/>(LayerNorm/RMSNorm)"]
            attn["attn<br/>(CausalSelfAttention)"]
            ln_2["ln_2<br/>(LayerNorm/RMSNorm)"]
            mlp["mlp<br/>(MLP)"]
        end
    end
    
    subgraph "Output Stage"
        ln_f["transformer.ln_f<br/>(LayerNorm/RMSNorm)"]
        lm_head["lm_head<br/>(Linear)"]
        final_logits_bias["final_logits_bias<br/>(buffer)"]
    end
    
    Output["logits, loss, hs<br/>(B, T, vocab_size)"]
    
    Input -->|"forward(idx)"| wte
    Input -->|"forward(idx)"| wpe
    wte -->|"tok_emb"| drop
    wpe -->|"pos_emb (added or cat)"| drop
    drop -->|"x"| Block0
    Block0 -->|"residual stream"| BlockN
    
    BlockN -->|"x"| ln_1
    ln_1 -->|"normalized"| attn
    attn -->|"+ residual"| ln_2
    ln_2 -->|"normalized"| mlp
    mlp -->|"+ residual"| ln_f
    
    ln_f -->|"final hidden state"| lm_head
    lm_head -->|"+ bias"| final_logits_bias
    final_logits_bias -->|"returns"| Output
    
    subgraph "Hook Integration"
        hook_recorder["hook_recorder()<br/>(context manager)"]
        hook_save_calls["hook_save('act_in', x)<br/>hook_save('resid_mid', x)<br/>hook_save('final_resid', x)"]
    end
    
    attn -.->|"records activations"| hook_save_calls
    mlp -.->|"records activations"| hook_save_calls
    hook_recorder -.->|"captures"| hook_save_calls
```

**Sources:** [circuit_sparsity/inference/gpt.py:683-778]()

## Configuration System

The model is configured via the `GPTConfig` dataclass, which provides a comprehensive set of parameters:

| Parameter Category | Key Fields | Purpose |
|-------------------|------------|---------|
| **Model Dimensions** | `d_model`, `d_mlp`, `d_head`, `n_layer`, `n_head` | Define model size and architecture |
| **Sequence Length** | `block_size`, `vocab_size` | Define input/output dimensions |
| **Sparsity** | `afrac`, `afrac_loctypes` | Control activation sparsity (see [Sparsity Features](#2.3)) |
| **Position Embeddings** | `d_pos_emb`, `cat_pos_emb`, `sinusoidal_cat_pos_emb` | Configure position encoding strategy |
| **Attention** | `flash`, `sink` | Enable Flash Attention and attention sinks |
| **Normalization** | `rms_norm`, `ln_bias` | Choose normalization type |
| **Activation Functions** | `activation_type`, `residual_activation_type` | Select non-linearities |
| **Training** | `dropout`, `grad_checkpointing` | Control training behavior |
| **Advanced** | `tied_unembed`, `enable_bigram_table` | Additional features |

The configuration system provides a `maybe_activation_sparsity()` method [circuit_sparsity/inference/gpt.py:544-557]() that applies top-k sparsity selectively based on `afrac` and `afrac_loctypes` settings.

**Sources:** [circuit_sparsity/inference/gpt.py:484-558]()

## Key Architectural Components

The following table maps conceptual components to their code implementations:

| Component | Class | Key Methods | Line Reference |
|-----------|-------|-------------|----------------|
| **Token Embedding** | `nn.Embedding` | Accessed as `transformer.wte` | [circuit_sparsity/inference/gpt.py:574]() |
| **Position Embedding** | `nn.Embedding` | Accessed as `transformer.wpe` | [circuit_sparsity/inference/gpt.py:575]() |
| **Transformer Block** | `Block` or `BlockCatPosEmb` | `forward()`, `forward_attn_block()`, `forward_mlp_block()` | [circuit_sparsity/inference/gpt.py:285-482]() |
| **Self-Attention** | `CausalSelfAttention` | `forward(x)` returns attention output | [circuit_sparsity/inference/gpt.py:61-168]() |
| **Feed-Forward** | `MLP` | `forward(x)` applies c_fc → act → c_proj | [circuit_sparsity/inference/gpt.py:170-209]() |
| **Output Head** | `nn.Linear` | Accessed as `lm_head` | [circuit_sparsity/inference/gpt.py:584]() |

### Block Structure

Each `Block` decomposes into two sub-operations:

```mermaid
graph LR
    resid_in["resid_in"] -->|"forward_attn_block()"| resid_mid["resid_mid"]
    resid_mid -->|"forward_mlp_block()"| resid_out["resid_out"]
    
    subgraph "forward_attn_block"
        ln_1["ln_1(x)"]
        attn_op["attn(...)"]
        add1["+"]
    end
    
    subgraph "forward_mlp_block"
        ln_2["ln_2(x)"]
        mlp_op["mlp(...)"]
        add2["+"]
    end
```

This decomposition allows selective computation when analyzing circuits (see `include_resid_mid` parameter in [circuit_sparsity/inference/gpt.py:683]()).

**Sources:** [circuit_sparsity/inference/gpt.py:285-349](), [circuit_sparsity/inference/gpt.py:413-482]()

## Model Loading and Instantiation

The repository provides a convenience function `load_model()` for loading pre-trained models:

```python
def load_model(model_path, flash=False, grad_checkpointing=False, cuda=True)
```

**Loading Process:**

```mermaid
sequenceDiagram
    participant User
    participant load_model
    participant read_file_cached
    participant GPTConfig
    participant GPT
    participant torch
    
    User->>load_model: model_path
    load_model->>read_file_cached: beeg_config.json
    read_file_cached-->>load_model: JSON dict
    load_model->>GPTConfig: **config_dict
    GPTConfig-->>load_model: config instance
    load_model->>GPT: GPT(config)
    GPT-->>load_model: model instance
    load_model->>read_file_cached: final_model.pt
    read_file_cached-->>load_model: checkpoint bytes
    load_model->>torch: torch.load()
    torch-->>load_model: state_dict
    load_model->>GPT: load_state_dict(sd)
    load_model-->>User: model (in eval mode)
```

The function expects a directory containing:
- `beeg_config.json`: Serialized `GPTConfig` parameters
- `final_model.pt`: Model checkpoint with weights

**Sources:** [circuit_sparsity/inference/gpt.py:906-939](), [README.md:36-38]()

## Architecture Variants

The implementation includes several architectural variants for different use cases:

### Standard Architecture

The default configuration uses:
- Additive position embeddings (`pos_emb` added to `tok_emb`)
- Standard `Block`, `CausalSelfAttention`, and `MLP` classes
- Optional Flash Attention via `F.scaled_dot_product_attention`

**Sources:** [circuit_sparsity/inference/gpt.py:560-626]()

### Concatenated Position Embeddings

When `config.d_pos_emb` is set, the model uses concatenation instead of addition:

```mermaid
graph LR
    tok_emb["tok_emb<br/>(B, T, d_model)"]
    pos_emb["pos_emb<br/>(B, T, d_pos_emb)"]
    concat["torch.cat([x, p], dim=-1)"]
    result["combined<br/>(B, T, d_model + d_pos_emb)"]
    
    tok_emb --> concat
    pos_emb --> concat
    concat --> result
```

This variant uses:
- `BlockCatPosEmb` instead of `Block`
- `CausalSelfAttentionCatPosEmb` and `MLPCatPosEmb` with modified input dimensions
- Separate layer norms for position embeddings (`ln_p1`, `ln_p2`)

The `config.d_model_in` property [circuit_sparsity/inference/gpt.py:527-528]() returns `d_model + d_pos_emb` when concatenation is enabled.

**Sources:** [circuit_sparsity/inference/gpt.py:351-482](), [circuit_sparsity/inference/gpt.py:513-528]()

### Attention Sinks

When `config.sink=True`, the model uses `SDPAWithSink` [circuit_sparsity/inference/gpt.py:211-283]() which adds a learnable attention sink mechanism:

1. Prepends a dummy key-value slot with zero value
2. Adds a learnable per-head `sink_logit` parameter to the attention scores
3. Allows the model to "discard" information by attending to the sink

This is only compatible with `flash=True` (Flash Attention).

**Sources:** [circuit_sparsity/inference/gpt.py:84-86](), [circuit_sparsity/inference/gpt.py:211-283]()

## Integration Points

The GPT model integrates with other system components:

```mermaid
graph TB
    GPT["GPT Model"]
    
    subgraph "Training System"
        train_py["train.py"]
        apply_topk["apply_topk_()"]
    end
    
    subgraph "Visualization System"
        viz_py["viz.py"]
        build_figure["build_figure()"]
    end
    
    subgraph "Hook System"
        hook_recorder["hook_recorder()"]
        HookContext["HookContext"]
    end
    
    subgraph "Examples"
        bracket_example["bracket_counting_example.py"]
    end
    
    subgraph "Registries"
        registries["registries.py"]
        MODEL_BASE_DIR["MODEL_BASE_DIR"]
        Datapoint["Datapoint"]
    end
    
    train_py -->|"instantiates, trains"| GPT
    apply_topk -->|"applies sparsity to"| GPT
    
    viz_py -->|"loads via load_model()"| GPT
    build_figure -->|"uses for rendering"| GPT
    
    GPT -->|"calls hook_save()"| hook_recorder
    hook_recorder -->|"captures activations"| HookContext
    
    bracket_example -->|"loads, analyzes"| GPT
    
    MODEL_BASE_DIR -->|"provides path to"| GPT
    GPT -->|"processes"| Datapoint
```

**Key Integration Methods:**

| Method | Purpose | Used By |
|--------|---------|---------|
| `forward(idx, targets)` | Standard forward pass with optional loss | Training, evaluation, examples |
| `forward_tail(x, n, ...)` | Forward from intermediate layer `n` | Circuit analysis, ablations |
| `generate(idx, max_new_tokens)` | Autoregressive generation | Interactive demos |
| `get_num_params()` | Count parameters | Model reporting |
| `is_mlp_param(p)`, `is_attn_param(p)` | Parameter classification | Sparse training, analysis |

**Sources:** [circuit_sparsity/inference/gpt.py:683-818](), [circuit_sparsity/inference/gpt.py:820-898]()

## Hook Integration for Activation Recording

The model extensively uses the hook system (detailed in [Hook System for Activation Recording](#2.4)) to save intermediate activations. Key hook points include:

| Hook Name | Location | Code Reference |
|-----------|----------|----------------|
| `"act_in"` | Input to attention/MLP | [circuit_sparsity/inference/gpt.py:101](), [circuit_sparsity/inference/gpt.py:184]() |
| `"k"`, `"q"`, `"v"` | Attention components | [circuit_sparsity/inference/gpt.py:113-115]() |
| `"y"` | Attention output before projection | [circuit_sparsity/inference/gpt.py:158]() |
| `"post_act"` | MLP after activation function | [circuit_sparsity/inference/gpt.py:196]() |
| `"resid_in"`, `"resid_mid"` | Residual stream states | [circuit_sparsity/inference/gpt.py:305](), [circuit_sparsity/inference/gpt.py:328]() |
| `"resid_delta"` | Residual additions | [circuit_sparsity/inference/gpt.py:313](), [circuit_sparsity/inference/gpt.py:331]() |
| `"final_resid"` | Final hidden state | [circuit_sparsity/inference/gpt.py:763]() |

Hooks are organized by layer using `hook_namespace(f"{layer_idx}")` [circuit_sparsity/inference/gpt.py:756]().

**Sources:** [circuit_sparsity/inference/gpt.py:97-209](), [circuit_sparsity/inference/gpt.py:305-343]()

## Usage Example

Basic usage pattern from tests:

```python
from circuit_sparsity.inference.gpt import GPT, GPTConfig, load_model
from circuit_sparsity.inference.hook_utils import hook_recorder
from circuit_sparsity.registries import MODEL_BASE_DIR

# Option 1: Create from config
config = GPTConfig(block_size=8, vocab_size=16, n_layer=1, n_head=1, d_model=8)
model = GPT(config)

# Option 2: Load pre-trained
model = load_model(f"{MODEL_BASE_DIR}/models/csp_yolo1", cuda=False)

# Forward pass
logits, loss, _ = model(idx, targets=targets)

# Capture activations
with hook_recorder() as rec:
    logits, _, _ = model(idx)
# rec now contains {"0.attn.act_in": tensor(...), "0.attn.k": tensor(...), ...}
```

**Sources:** [README.md:40-58](), [tests/test_gpt.py]()

## Model Parameter Classification

The `GPT` class provides utility methods for classifying parameters, useful for applying different training strategies:

```mermaid
graph TB
    param["Parameter p"]
    
    is_mlp_param{"is_mlp_param(p)"}
    is_attn_param{"is_attn_param(p)"}
    is_bias{"is_bias(p)"}
    is_ln_param{"is_ln_param(p)"}
    is_param_embed{"is_param_embed(p)"}
    is_sparse_param{"is_sparse_param(p)"}
    
    param --> is_mlp_param
    param --> is_attn_param
    param --> is_bias
    param --> is_ln_param
    param --> is_param_embed
    param --> is_sparse_param
    
    is_mlp_param -->|"True"| mlp_weights["c_fc.weight, c_proj.weight<br/>in all MLP layers"]
    is_attn_param -->|"True"| attn_weights["c_attn.weight, c_proj.weight<br/>in all attention layers"]
    is_bias -->|"True"| biases["All bias parameters"]
    is_ln_param -->|"True"| ln_weights["LayerNorm/RMSNorm weights"]
    is_param_embed -->|"True"| embeddings["wte.weight, wpe.weight"]
    is_sparse_param -->|"True"| sparse["Parameters eligible for sparsity"]
```

These methods enable selective parameter handling during training (e.g., applying sparsity only to certain parameter classes).

**Sources:** [circuit_sparsity/inference/gpt.py:820-898]()

---

