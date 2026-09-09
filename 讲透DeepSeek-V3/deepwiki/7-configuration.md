> 来源: [https://deepwiki.com/deepseek-ai/DeepSeek-V3/7-configuration](https://deepwiki.com/deepseek-ai/DeepSeek-V3/7-configuration)
> DeepWiki deepseek-ai/DeepSeek-V3

# Configuration

  Relevant source files 
 - [inference/configs/config_671B.json](https://github.com/deepseek-ai/DeepSeek-V3/blob/9b4e9788/inference/configs/config_671B.json)
 
  This page documents the configuration system for DeepSeek-V3, including the structure of configuration files, how they are loaded and used throughout the codebase, and how configuration parameters map to model architecture components. For detailed documentation of individual configuration parameters, see [Configuration Options](https://deepwiki.com/deepseek-ai/DeepSeek-V3/7.1-configuration-options). For information about different model size configurations available, see [Model Sizes](https://deepwiki.com/deepseek-ai/DeepSeek-V3/7.2-model-sizes).

 
## Overview

 The DeepSeek-V3 configuration system uses JSON files to define all architectural hyperparameters for model instantiation. Configuration files specify dimensions, layer counts, MoE topology, attention parameters, LoRA ranks, and quantization settings. The configuration drives the construction of all model components from embedding layers through transformer blocks to output projections.

 **Sources:** [inference/configs/config_671B.json1-22](https://github.com/deepseek-ai/DeepSeek-V3/blob/9b4e9788/inference/configs/config_671B.json#L1-L22)

 
## Configuration File Structure

 Configuration files are stored in the `inference/configs/` directory and follow a flat JSON schema. The primary configuration file for the 671B parameter model is `config_671B.json`:

 
```

```

 The configuration file contains no nested structures - all parameters are defined at the top level for straightforward parsing and validation.

 **Sources:** [inference/configs/config_671B.json1-22](https://github.com/deepseek-ai/DeepSeek-V3/blob/9b4e9788/inference/configs/config_671B.json#L1-L22)

 
## Configuration Loading Process

 
### ModelArgs Dataclass

 Configuration parameters are loaded into a `ModelArgs` dataclass defined in `model.py`. This dataclass provides type safety and default values for all configuration parameters. The loading process follows this workflow:

 
```

```

 **Diagram 1: Configuration Loading Pipeline**

 The configuration dictionary is unpacked directly into the `ModelArgs` constructor, which validates parameter types and applies any necessary transformations before model instantiation.

 **Sources:** [inference/configs/config_671B.json1-22](https://github.com/deepseek-ai/DeepSeek-V3/blob/9b4e9788/inference/configs/config_671B.json#L1-L22)

 
## Configuration Parameter Categories

 Configuration parameters are organized into several logical categories that control different aspects of the model architecture:

 
| Category | Parameters | Purpose |
|---|---|---|
| Model Dimensions | vocab_size, dim, inter_dim, moe_inter_dim | Define vocabulary size and hidden dimensions for embeddings and feed-forward layers |
| Layer Structure | n_layers, n_dense_layers | Specify total transformer layers (61) and initial dense layers (3) |
| Attention | n_heads, q_lora_rank, kv_lora_rank, qk_nope_head_dim, qk_rope_head_dim, v_head_dim | Control Multi-head Latent Attention configuration with LoRA and RoPE/NOPE dimensions |
| MoE Topology | n_routed_experts, n_shared_experts, n_activated_experts, n_expert_groups, n_limited_groups | Define expert routing with 256 total experts, 8 activated per token, and expert grouping |
| Routing | route_scale, score_func | Configure routing mechanism using sigmoid scoring with scale factor 2.5 |
| Quantization | dtype | Specify weight precision (fp8 or bf16) |

 **Sources:** [inference/configs/config_671B.json1-22](https://github.com/deepseek-ai/DeepSeek-V3/blob/9b4e9788/inference/configs/config_671B.json#L1-L22)

 
## Configuration-Architecture Mapping

 The following diagram illustrates how configuration parameters map to specific architectural components in the model implementation:

 
```

```

 **Diagram 2: Configuration Parameter to Code Entity Mapping**

 This diagram shows the direct relationships between configuration parameters and the classes/components they instantiate. Note that:

 
 - `vocab_size` and `dim` control the `ParallelEmbedding` size
 - `n_layers` (61) defines the total number of `TransformerBlock` instances
 - `n_dense_layers` (3) specifies that layers 0-2 use standard FFN with `inter_dim`
 - Layers 3-60 use `MoE` components with `moe_inter_dim` and expert parameters
 - Attention parameters control the `Attention` module's LoRA and RoPE/NOPE configuration
 - `dtype` affects quantization across all linear layers
 
 **Sources:** [inference/configs/config_671B.json1-22](https://github.com/deepseek-ai/DeepSeek-V3/blob/9b4e9788/inference/configs/config_671B.json#L1-L22)

 
## Configuration Usage in Code

 Configuration is typically loaded at model initialization time. The standard pattern involves:

 
 - Loading the JSON configuration file
 - Constructing a `ModelArgs` instance from the configuration dictionary
 - Passing `ModelArgs` to the `Transformer` constructor
 - The `Transformer` uses configuration parameters to instantiate all sub-components
 
 
### Dense vs MoE Layer Selection

 A critical aspect of the configuration is the distinction between dense and MoE layers:

 
```

```

 **Diagram 3: Layer Type Selection Logic**

 The first `n_dense_layers` (3) use standard feed-forward networks with `inter_dim` (18,432) as the intermediate dimension. The remaining 58 layers use MoE with `moe_inter_dim` (2,048) per expert.

 **Sources:** [inference/configs/config_671B.json4-7](https://github.com/deepseek-ai/DeepSeek-V3/blob/9b4e9788/inference/configs/config_671B.json#L4-L7)

 
## Configuration Validation

 The `ModelArgs` dataclass enforces type safety and provides validation for configuration parameters:

 
 - **Dimension consistency**: `dim` must be divisible by `n_heads` for proper attention head splitting
 - **MoE constraints**: `n_routed_experts` must be divisible by `n_expert_groups`
 - **LoRA dimensions**: `q_lora_rank` and `kv_lora_rank` define the compressed latent space
 - **Head dimensions**: `qk_nope_head_dim + qk_rope_head_dim` defines the per-head dimension for queries/keys
 - **Layer structure**: `n_dense_layers` must be less than `n_layers`
 
 Invalid configurations will raise errors during model initialization, preventing runtime failures.

 **Sources:** [inference/configs/config_671B.json1-22](https://github.com/deepseek-ai/DeepSeek-V3/blob/9b4e9788/inference/configs/config_671B.json#L1-L22)

 
## Configuration and Model Parallelism

 Configuration parameters interact with model parallelism settings (world size, rank) to determine shard sizes:

 
| Parameter | Sharding Strategy |
|---|---|
| vocab_size | Partitioned across ranks in ParallelEmbedding |
| n_routed_experts | Each rank loads n_routed_experts // world_size experts |
| dim | Split for ColumnParallelLinear (output features) |
| dim | Split for RowParallelLinear (input features) |

 The configuration file itself does not specify parallelism settings - these are provided through environment variables (`WORLD_SIZE`, `RANK`, `LOCAL_RANK`) at runtime. The model code combines configuration parameters with parallelism settings to compute local dimensions.

 **Sources:** [inference/configs/config_671B.json2-9](https://github.com/deepseek-ai/DeepSeek-V3/blob/9b4e9788/inference/configs/config_671B.json#L2-L9)

 
## Configuration Extension Points

 While the 671B configuration is the primary production configuration, the system supports arbitrary configurations through the same JSON schema. New model sizes can be defined by creating additional configuration files (e.g., `config_16B.json`, `config_236B.json`) with appropriate parameter values. See [Model Sizes](https://deepwiki.com/deepseek-ai/DeepSeek-V3/7.2-model-sizes) for documentation of available configurations.

 The configuration system is designed for extensibility:

 
 - New parameters can be added to `ModelArgs` with default values
 - Existing parameters can be overridden for experimentation
 - Configuration files can be programmatically generated for architecture search
 
 **Sources:** [inference/configs/config_671B.json1-22](https://github.com/deepseek-ai/DeepSeek-V3/blob/9b4e9788/inference/configs/config_671B.json#L1-L22)
