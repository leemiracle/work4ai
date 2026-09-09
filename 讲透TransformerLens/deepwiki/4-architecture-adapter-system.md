> 来源: [https://deepwiki.com/TransformerLensOrg/TransformerLens/4-architecture-adapter-system](https://deepwiki.com/TransformerLensOrg/TransformerLens/4-architecture-adapter-system)
> DeepWiki TransformerLensOrg/TransformerLens | Last indexed: 16 July 2026 (4ba218

# Architecture Adapter System

  Relevant source files 
 - [transformer_lens/factories/architecture_adapter_factory.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/factories/architecture_adapter_factory.py)
 - [transformer_lens/model_bridge/architecture_adapter.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/model_bridge/architecture_adapter.py)
 - [transformer_lens/model_bridge/generalized_components/__init__.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/model_bridge/generalized_components/__init__.py)
 - [transformer_lens/model_bridge/generalized_components/embedding.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/model_bridge/generalized_components/embedding.py)
 - [transformer_lens/model_bridge/generalized_components/linear.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/model_bridge/generalized_components/linear.py)
 - [transformer_lens/model_bridge/generalized_components/mlp.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/model_bridge/generalized_components/mlp.py)
 - [transformer_lens/model_bridge/generalized_components/normalization.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/model_bridge/generalized_components/normalization.py)
 - [transformer_lens/model_bridge/generalized_components/unembedding.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/model_bridge/generalized_components/unembedding.py)
 - [transformer_lens/model_bridge/sources/transformers.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/model_bridge/sources/transformers.py)
 - [transformer_lens/model_bridge/supported_architectures/__init__.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/model_bridge/supported_architectures/__init__.py)
 - [transformer_lens/model_bridge/supported_architectures/gpt2.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/model_bridge/supported_architectures/gpt2.py)
 - [transformer_lens/tools/model_registry/__init__.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/tools/model_registry/__init__.py)
 - [transformer_lens/tools/model_registry/data/supported_models.json](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/tools/model_registry/data/supported_models.json)
 - [transformer_lens/tools/model_registry/data/verification_history.json](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/tools/model_registry/data/verification_history.json)
 - [transformer_lens/tools/model_registry/generate_report.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/tools/model_registry/generate_report.py)
 - [transformer_lens/utilities/architectures.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/utilities/architectures.py)
 - [transformer_lens/weight_processing.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/weight_processing.py)
 
  The **Architecture Adapter System** is the translation layer of TransformerLens v3.0. It allows the library to support over 50 different transformer architectures (including Llama, GPT-2, Mistral, and Mamba) by mapping heterogeneous HuggingFace (HF) module structures into a unified, hookable TransformerLens format [transformer_lens/model_bridge/sources/transformers.py23-26](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/model_bridge/sources/transformers.py#L23-L26)

 Instead of hard-coding every model's internal path, TransformerLens uses **Architecture Adapters** to define how a specific model family's weights should be rearranged and how its components map to the standardized `TransformerBridge` hooks [transformer_lens/model_bridge/architecture_adapter.py29-35](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/model_bridge/architecture_adapter.py#L29-L35)

 
### System Overview: From HF to TransformerLens

 The following diagram illustrates how the `ArchitectureAdapterFactory` selects the correct adapter to bridge a HuggingFace model into the `TransformerBridge` ecosystem.

 **Model Loading and Mapping Flow**

 
```

```

 **Sources:** [transformer_lens/factories/architecture_adapter_factory.py164-167](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/factories/architecture_adapter_factory.py#L164-L167) [transformer_lens/model_bridge/bridge.py1-20](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/model_bridge/bridge.py#L1-L20) [transformer_lens/model_bridge/architecture_adapter.py136-147](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/model_bridge/architecture_adapter.py#L136-L147)

 
---

 
### Core Concepts

 
#### [ArchitectureAdapter Base Class](https://deepwiki.com/TransformerLensOrg/TransformerLens/4.1-architectureadapter-base-class)

 The `ArchitectureAdapter` is the source of truth for a model's structure. It defines:

 
 - **Component Mapping**: A dictionary (`ComponentMapping`) that translates standardized TransformerLens paths (e.g., `blocks.0.attn.q`) to the specific module paths in the HF model (e.g., `model.layers.0.self_attn.q_proj`) [transformer_lens/model_bridge/architecture_adapter.py136-147](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/model_bridge/architecture_adapter.py#L136-L147)
 - **Weight Conversions**: Rules for transforming weights, such as splitting combined QKV tensors or transposing Conv1D weights into standard Linear formats [transformer_lens/model_bridge/architecture_adapter.py93-119](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/model_bridge/architecture_adapter.py#L93-L119)
 - **Configuration Mapping**: Standardizing HF config fields (like `hidden_size` or `num_attention_heads`) into TL fields (`d_model`, `n_heads`) [transformer_lens/model_bridge/sources/transformers.py37-52](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/model_bridge/sources/transformers.py#L37-L52)
 
 For details, see [ArchitectureAdapter Base Class](https://deepwiki.com/TransformerLensOrg/TransformerLens/4.1-architectureadapter-base-class).

 
#### [Generalized Components](https://deepwiki.com/TransformerLensOrg/TransformerLens/4.2-generalized-components)

 Generalized Components are wrapper classes that inherit from `GeneralizedComponent`. They "bridge" the gap by wrapping an original HF module while providing standard `HookPoint` attributes [transformer_lens/model_bridge/generalized_components/normalization.py12-16](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/model_bridge/generalized_components/normalization.py#L12-L16)

 
 - **AttentionBridge**: Handles standard, GQA, and MQA attention patterns.
 - **MLPBridge**: Handles standard, gated (SiLU/GeLU), and MoE MLP structures.
 - **NormalizationBridge**: Standardizes LayerNorm and RMSNorm, including upcasting for precision [transformer_lens/model_bridge/generalized_components/normalization.py86-98](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/model_bridge/generalized_components/normalization.py#L86-L98)
 
 For details, see [Generalized Components](https://deepwiki.com/TransformerLensOrg/TransformerLens/4.2-generalized-components).

 
#### [Supported Architecture Adapters](https://deepwiki.com/TransformerLensOrg/TransformerLens/4.3-supported-architecture-adapters)

 TransformerLens supports a vast array of models via the `SUPPORTED_ARCHITECTURES` registry [transformer_lens/factories/architecture_adapter_factory.py83-161](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/factories/architecture_adapter_factory.py#L83-L161) This includes:

 
 - **Autoregressive**: GPT-2, Llama 1/2/3, Mistral, Mixtral, Qwen, Gemma 1/2.
 - **Non-Transformer**: Mamba, Mamba2 (SSMs).
 - **Encoder/Multimodal**: BERT, T5, LLaVA, Qwen-VL.
 
 For details, see [Supported Architecture Adapters](https://deepwiki.com/TransformerLensOrg/TransformerLens/4.3-supported-architecture-adapters).

 
---

 
### Component Interaction Diagram

 This diagram shows how specific code entities interact to resolve a request for a specific weight, such as `blocks.0.attn.W_Q`.

 **Path Translation and Weight Access**

 
```

```

 **Sources:** [transformer_lens/weight_processing.py38-51](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/weight_processing.py#L38-L51) [transformer_lens/model_bridge/architecture_adapter.py149-165](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/model_bridge/architecture_adapter.py#L149-L165) [transformer_lens/model_bridge/supported_architectures/gpt2.py145-154](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/model_bridge/supported_architectures/gpt2.py#L145-L154)

 
### Summary Table: Adapter Responsibilities

 
| Feature | Handled By | Code Entity |
|---|---|---|
| Path Mapping | get_component_mapping | ArchitectureAdapter.get_component_mapping |
| Weight Rearranging | weight_processing_conversions | ArchitectureAdapter.weight_processing_conversions |
| Module Wrapping | GeneralizedComponent | GeneralizedComponent.set_original_component |
| HF Config Mapping | map_default_transformer_lens_config | transformer_lens/model_bridge/sources/transformers.py37 |
| Registry | SUPPORTED_ARCHITECTURES | transformer_lens/factories/architecture_adapter_factory.py83 |

 
---

 
### [Creating a New Adapter](https://deepwiki.com/TransformerLensOrg/TransformerLens/4.4-creating-a-new-adapter)

 Adding support for a new model involves subclassing `ArchitectureAdapter`, defining the `ComponentMapping` for its layers, and specifying any required weight transformations (e.g., if the model uses a non-standard attention layout) [transformer_lens/model_bridge/supported_architectures/gpt2.py97-115](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/model_bridge/supported_architectures/gpt2.py#L97-L115)

 For a step-by-step guide, see [Creating a New Adapter](https://deepwiki.com/TransformerLensOrg/TransformerLens/4.4-creating-a-new-adapter).
