> 来源: [https://deepwiki.com/TransformerLensOrg/TransformerLens/3-core-architecture](https://deepwiki.com/TransformerLensOrg/TransformerLens/3-core-architecture)
> DeepWiki TransformerLensOrg/TransformerLens | Last indexed: 16 July 2026 (4ba218

# Core Architecture

  Relevant source files 
 - [tests/acceptance/test_hooked_encoder.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/tests/acceptance/test_hooked_encoder.py)
 - [tests/acceptance/test_hooked_transformer.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/tests/acceptance/test_hooked_transformer.py)
 - [transformer_lens/HookedEncoder.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/HookedEncoder.py)
 - [transformer_lens/HookedTransformer.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/HookedTransformer.py)
 - [transformer_lens/loading_from_pretrained.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/loading_from_pretrained.py)
 - [transformer_lens/model_bridge/bridge.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/model_bridge/bridge.py)
 - [transformer_lens/model_bridge/generalized_components/attention.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/model_bridge/generalized_components/attention.py)
 - [transformer_lens/model_bridge/generalized_components/base.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/model_bridge/generalized_components/base.py)
 - [transformer_lens/model_bridge/generalized_components/block.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/model_bridge/generalized_components/block.py)
 - [transformer_lens/model_bridge/generalized_components/joint_qkv_attention.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/model_bridge/generalized_components/joint_qkv_attention.py)
 - [transformer_lens/utils.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/utils.py)
 
  This page provides an overview of the core architectural components of TransformerLens. In version 3.0, the library introduced a major architectural shift with the `TransformerBridge`, while maintaining the legacy `HookedTransformer` for backwards compatibility. These components work together to provide a unified interface for mechanistic interpretability across dozens of different model architectures.

 
## High-Level Architecture Overview

 The TransformerLens architecture is now split into two primary paths: the **Bridge Path** (v3) and the **Native Path** (Legacy). Both paths are built upon the `HookedRootModule` base class, which provides the fundamental hooking infrastructure.

 
 - **TransformerBridge (v3)**: Wraps existing HuggingFace (HF) models in-place. It uses `ArchitectureAdapter` objects to map HF components to `GeneralizedComponent` bridges, allowing interpretability tools to work without converting weights to a new format.
 - **HookedTransformer (Legacy)**: A "clean-room" implementation of the transformer architecture. It requires converting pretrained weights into a specific TransformerLens format.
 - **Hook System**: The shared foundation (via `HookPoint`) that enables accessing and modifying activations.
 - **Architecture Adapters**: The translation layer that allows `TransformerBridge` to understand the internal structure of various model families (Llama, GPT-2, Mistral, etc.).
 
 
### System Flow: Natural Language to Code Entities

 The following diagram maps high-level concepts to the specific classes and files that implement them in the codebase.

 
```

```

 Sources: [transformer_lens/model_bridge/bridge.py99-151](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/model_bridge/bridge.py#L99-L151) [transformer_lens/HookedTransformer.py105-137](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/HookedTransformer.py#L105-L137) [transformer_lens/HookedRootModule.py1-40](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/HookedRootModule.py#L1-L40) [transformer_lens/hook_points.py170-200](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/hook_points.py#L170-L200)

 
## Core Component Hierarchy

 The relationship between the new Bridge system and the legacy components is managed through inheritance from `HookedRootModule`.

 
```

```

 Sources: [transformer_lens/model_bridge/bridge.py99-160](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/model_bridge/bridge.py#L99-L160) [transformer_lens/model_bridge/architecture_adapter.py25-80](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/model_bridge/architecture_adapter.py#L25-L80) [transformer_lens/model_bridge/generalized_components/base.py18-50](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/model_bridge/generalized_components/base.py#L18-L50) [transformer_lens/HookedTransformer.py105-165](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/HookedTransformer.py#L105-L165)

 
## Key Architectural Components

 
### TransformerBridge (v3)

 The `TransformerBridge` is the primary entry point for version 3.0. Instead of re-implementing the model, it "bridges" an existing `torch.nn.Module` (typically from HuggingFace). It intercepts the forward pass to trigger hooks at standardized locations.

 
 - For details, see [TransformerBridge](https://deepwiki.com/TransformerLensOrg/TransformerLens/3.1-transformerbridge).
 
 
### HookedTransformer (Legacy)

 The `HookedTransformer` is the original TransformerLens implementation. It is highly optimized for mechanistic interpretability research on GPT-style models and supports features like `fold_ln` (LayerNorm folding) and `center_writing_weights`.

 
 - For details, see [HookedTransformer (Legacy)](https://deepwiki.com/TransformerLensOrg/TransformerLens/3.2-hookedtransformer-(legacy)).
 
 
### Hook System

 The hook system is powered by `HookPoint`. These are identity modules inserted into the computation graph. When the model reaches a `HookPoint`, it checks for registered hook functions and executes them, allowing users to inspect or modify the tensor.

 
 - For details, see [Hook System](https://deepwiki.com/TransformerLensOrg/TransformerLens/3.3-hook-system).
 
 
### Activation Cache

 The `ActivationCache` is a container returned by `run_with_cache`. It provides a dictionary-like interface to all tensors captured during a forward pass, along with helper methods for common interpretability tasks like residual stream decomposition.

 
 - For details, see [Activation Cache](https://deepwiki.com/TransformerLensOrg/TransformerLens/3.4-activation-cache).
 
 
### Model Configuration

 Configurations are handled by `HookedTransformerConfig` (for legacy) and `TransformerBridgeConfig` (for bridge). These classes store metadata about the model architecture, such as `d_model`, `n_heads`, and `act_fn`.

 
 - For details, see [Model Configuration](https://deepwiki.com/TransformerLensOrg/TransformerLens/3.5-model-configuration).
 
 
## Component Comparison

 
| Feature | TransformerBridge (v3) | HookedTransformer (Legacy) |
|---|---|---|
| Model Source | Any nn.Module (HF, etc.) | Custom Implementation |
| Weight Conversion | None (uses original weights) | Required (TL format) |
| Architecture Support | Broad (50+ adapters) | Mostly GPT-style / BERT |
| Numerical Parity | Exact (calls original code) | Approximate (re-implemented) |
| Hook Placement | Via GeneralizedComponent | Hardcoded in blocks |

 Sources: [transformer_lens/model_bridge/bridge.py100-128](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/model_bridge/bridge.py#L100-L128) [transformer_lens/HookedTransformer.py105-137](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/HookedTransformer.py#L105-L137) [transformer_lens/loading_from_pretrained.py126-166](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/loading_from_pretrained.py#L126-L166)

 
## Model Loading Pipeline

 The loading pipeline differs significantly between the two architectures. `TransformerBridge` relies on `boot_transformers` to initialize the bridge and adapter, while `HookedTransformer` uses `from_pretrained` to trigger weight conversion scripts.

 
```

```

 Sources: [transformer_lens/model_bridge/bridge.py350-400](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/model_bridge/bridge.py#L350-L400) [transformer_lens/loading_from_pretrained.py29-57](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/loading_from_pretrained.py#L29-L57) [transformer_lens/HookedTransformer.py800-850](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/HookedTransformer.py#L800-L850)
