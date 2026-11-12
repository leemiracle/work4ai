> 来源: [https://deepwiki.com/TransformerLensOrg/TransformerLens/11-glossary](https://deepwiki.com/TransformerLensOrg/TransformerLens/11-glossary)
> DeepWiki TransformerLensOrg/TransformerLens | Last indexed: 16 July 2026 (4ba218

# Glossary

  Relevant source files 
 - [tests/acceptance/test_activation_cache.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/tests/acceptance/test_activation_cache.py)
 - [tests/acceptance/test_hooked_encoder.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/tests/acceptance/test_hooked_encoder.py)
 - [tests/acceptance/test_hooked_transformer.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/tests/acceptance/test_hooked_transformer.py)
 - [tests/unit/components/test_attention.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/tests/unit/components/test_attention.py)
 - [tests/unit/test_hooked_root_module.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/tests/unit/test_hooked_root_module.py)
 - [transformer_lens/ActivationCache.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/ActivationCache.py)
 - [transformer_lens/BertNextSentencePrediction.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/BertNextSentencePrediction.py)
 - [transformer_lens/HookedEncoder.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/HookedEncoder.py)
 - [transformer_lens/HookedTransformer.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/HookedTransformer.py)
 - [transformer_lens/SVDInterpreter.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/SVDInterpreter.py)
 - [transformer_lens/benchmarks/main_benchmark.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/benchmarks/main_benchmark.py)
 - [transformer_lens/components/abstract_attention.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/components/abstract_attention.py)
 - [transformer_lens/components/grouped_query_attention.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/components/grouped_query_attention.py)
 - [transformer_lens/components/t5_block.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/components/t5_block.py)
 - [transformer_lens/components/transformer_block.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/components/transformer_block.py)
 - [transformer_lens/head_detector.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/head_detector.py)
 - [transformer_lens/hook_points.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/hook_points.py)
 - [transformer_lens/loading_from_pretrained.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/loading_from_pretrained.py)
 - [transformer_lens/model_bridge/bridge.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/model_bridge/bridge.py)
 - [transformer_lens/model_bridge/generalized_components/attention.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/model_bridge/generalized_components/attention.py)
 - [transformer_lens/model_bridge/generalized_components/base.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/model_bridge/generalized_components/base.py)
 - [transformer_lens/model_bridge/generalized_components/block.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/model_bridge/generalized_components/block.py)
 - [transformer_lens/model_bridge/generalized_components/joint_qkv_attention.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/model_bridge/generalized_components/joint_qkv_attention.py)
 - [transformer_lens/patching.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/patching.py)
 - [transformer_lens/pretrained/weight_conversions/neox.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/pretrained/weight_conversions/neox.py)
 - [transformer_lens/tools/model_registry/data/architecture_gaps.json](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/tools/model_registry/data/architecture_gaps.json)
 - [transformer_lens/tools/model_registry/hf_scraper.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/tools/model_registry/hf_scraper.py)
 - [transformer_lens/tools/model_registry/verify_models.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/tools/model_registry/verify_models.py)
 - [transformer_lens/utils.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/utils.py)
 
  This page provides definitions for codebase-specific terms, technical jargon, and domain concepts used throughout TransformerLens. It is intended to help onboarding engineers navigate the architectural distinctions between legacy and v3.0 systems.

 
## Core Architectural Concepts

 
### HookPoint

 The fundamental building block of TransformerLens. A `HookPoint` is a dummy `nn.Module` that acts as an identity function by default but allows for the registration of custom functions (hooks) to inspect or modify activations during the forward or backward pass [transformer_lens/hook_points.py143-150](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/hook_points.py#L143-L150)

 
### TransformerBridge (v3.0)

 The new primary interface for interacting with models. Unlike the legacy `HookedTransformer`, which re-implements model architectures in native TransformerLens code, `TransformerBridge` wraps existing HuggingFace (HF) models. It uses an `ArchitectureAdapter` to map HF internal modules to a standardized TransformerLens-like interface [transformer_lens/model_bridge/bridge.py99-105](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/model_bridge/bridge.py#L99-L105)

 
### HookedTransformer (Legacy)

 The original implementation of TransformerLens. It contains manual PyTorch implementations of various architectures (GPT-2, Llama, etc.) designed to be "hookable" from the ground up [transformer_lens/HookedTransformer.py105-113](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/HookedTransformer.py#L105-L113)

 
### Architecture Adapter

 A system in v3.0 that defines how a specific HuggingFace model architecture (e.g., `LlamaForCausalLM`) maps to TransformerLens components. It handles weight path translation and activation reshaping [transformer_lens/model_bridge/architecture_adapter.py1-20](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/model_bridge/architecture_adapter.py#L1-L20)

 
### Generalized Component

 A wrapper class used by `TransformerBridge` to provide a consistent API for different parts of a model (e.g., `AttentionBridge`, `MLPBridge`). These components "bridge" the gap between the raw HF module and the expected TransformerLens behavior [transformer_lens/model_bridge/generalized_components/base.py18-24](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/model_bridge/generalized_components/base.py#L18-L24)

 
---

 
## Component and Activation Terms

 
| Term | Definition | Code Pointer |
|---|---|---|
| Residual Stream | The sum of embeddings and all previous layer outputs. Often accessed via hook_resid_pre or hook_resid_post. | transformer_lens/ActivationCache.py116-117 |
| Logit Attribution | The process of decomposing the final logit prediction into contributions from individual components (heads, MLPs). | transformer_lens/ActivationCache.py70-72 |
| KV Cache | A mechanism to store Key and Value tensors during inference to avoid redundant computations in autoregressive generation. | transformer_lens/HookedTransformer.py48 |
| Folded LayerNorm | An optimization where LayerNorm weights are mathematically "folded" into the weights of the subsequent linear layer. | transformer_lens/weight_processing.py1-20 |
| Rotary Embeddings (RoPE) | A type of relative positional encoding that rotates query and key vectors in the complex plane. | transformer_lens/components/abstract_attention.py30 |

 
---

 
## Data Structures

 
### ActivationCache

 A dictionary-like object that stores activations captured during a model run. It includes helper methods for residual stream decomposition and logit lens analysis [transformer_lens/ActivationCache.py53-62](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/ActivationCache.py#L53-L62)

 
### FactoredMatrix

 A specialized class for representing a large matrix as the product of two smaller ones (e.g., $W_{QK} = W_Q \cdot W_K^T$). This is highly efficient for analyzing attention circuits without instantiating full $d_{model} \times d_{model}$ matrices [transformer_lens/FactoredMatrix.py1-15](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/FactoredMatrix.py#L1-L15)

 
---

 
## Visualizing the Codebase

 
### From Natural Language to Code Entities (v3 Architecture)

 This diagram shows how a user's request to load a model travels through the v3.0 `TransformerBridge` system.

 
```

```

 **Sources:** [transformer_lens/model_bridge/bridge.py99-105](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/model_bridge/bridge.py#L99-L105) [transformer_lens/model_bridge/generalized_components/base.py18-24](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/model_bridge/generalized_components/base.py#L18-L24) [transformer_lens/model_bridge/generalized_components/attention.py26-38](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/model_bridge/generalized_components/attention.py#L26-L38)

 
### Hook System and Data Flow

 This diagram illustrates how activations flow through a `HookPoint` and how user-defined hooks intercept them.

 
```

```

 **Sources:** [transformer_lens/hook_points.py143-167](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/hook_points.py#L143-L167) [transformer_lens/hook_points.py198-212](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/hook_points.py#L198-L212)

 
---

 
## Domain Jargon

 
 - **BOS (Beginning of Sequence):** A special token prepended to prompts. TransformerLens often defaults `prepend_bos=True` because many models use the 0th position as a "rest" position for attention heads [transformer_lens/HookedTransformer.py121-127](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/HookedTransformer.py#L121-L127)
 - **DLA (Direct Logit Attribution):** A technique to see how much a specific component contributes to the logit of the correct token [transformer_lens/ActivationCache.py70-72](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/ActivationCache.py#L70-L72)
 - **Ablation:** Manually setting an activation to zero (or a mean value) to see how it affects model performance, used for causal discovery [transformer_lens/patching.py1-10](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/patching.py#L1-L10)
 - **Refactoring:** In the context of weights, this usually refers to `refactor_factored_attn_matrices`, which simplifies $W_Q, W_K, W_V, W_O$ into $W_{QK}$ and $W_{OV}$ matrices for easier interpretation [tests/acceptance/test_hooked_transformer.py170](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/tests/acceptance/test_hooked_transformer.py#L170-L170)
 
 **Sources:**

 
 - [transformer_lens/hook_points.py1-212](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/hook_points.py#L1-L212)
 - [transformer_lens/model_bridge/bridge.py1-182](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/model_bridge/bridge.py#L1-L182)
 - [transformer_lens/HookedTransformer.py1-150](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/HookedTransformer.py#L1-L150)
 - [transformer_lens/ActivationCache.py1-165](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/ActivationCache.py#L1-L165)
 - [transformer_lens/model_bridge/generalized_components/base.py1-164](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/model_bridge/generalized_components/base.py#L1-L164)
 - [transformer_lens/model_bridge/generalized_components/attention.py1-158](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/model_bridge/generalized_components/attention.py#L1-L158)
