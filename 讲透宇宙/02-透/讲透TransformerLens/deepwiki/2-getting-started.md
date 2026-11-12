> 来源: [https://deepwiki.com/TransformerLensOrg/TransformerLens/2-getting-started](https://deepwiki.com/TransformerLensOrg/TransformerLens/2-getting-started)
> DeepWiki TransformerLensOrg/TransformerLens | Last indexed: 16 July 2026 (4ba218

# Getting Started

  Relevant source files 
 - [demos/Colab_Compatibility.ipynb](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/demos/Colab_Compatibility.ipynb)
 - [demos/Direct_Logit_Attribution_Demo.ipynb](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/demos/Direct_Logit_Attribution_Demo.ipynb)
 - [demos/Exploratory_Analysis_Demo.ipynb](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/demos/Exploratory_Analysis_Demo.ipynb)
 - [demos/Interactive_Neuroscope.ipynb](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/demos/Interactive_Neuroscope.ipynb)
 - [demos/Main_Demo.ipynb](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/demos/Main_Demo.ipynb)
 - [demos/No_Position_Experiment.ipynb](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/demos/No_Position_Experiment.ipynb)
 - [docs/source/_static/model_properties_table.jsonl](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/docs/source/_static/model_properties_table.jsonl)
 - [docs/source/content/getting_started.md](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/docs/source/content/getting_started.md?plain=1)
 - [docs/source/content/migrating_to_v3.md](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/docs/source/content/migrating_to_v3.md?plain=1)
 - [docs/source/content/model_structure.md](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/docs/source/content/model_structure.md?plain=1)
 - [docs/source/content/special_cases.md](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/docs/source/content/special_cases.md?plain=1)
 - [tests/unit/test_xielu.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/tests/unit/test_xielu.py)
 - [tests/unit/tools/test_model_registry.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/tests/unit/tools/test_model_registry.py)
 - [transformer_lens/components/mlps/can_be_used_as_mlp.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/components/mlps/can_be_used_as_mlp.py)
 - [transformer_lens/factories/activation_function_factory.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/factories/activation_function_factory.py)
 - [transformer_lens/model_bridge/supported_architectures/qwen3_5.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/model_bridge/supported_architectures/qwen3_5.py)
 - [transformer_lens/pretrained/weight_conversions/__init__.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/pretrained/weight_conversions/__init__.py)
 - [transformer_lens/pretrained/weight_conversions/apertus.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/pretrained/weight_conversions/apertus.py)
 - [transformer_lens/pretrained/weight_conversions/gemma.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/pretrained/weight_conversions/gemma.py)
 - [transformer_lens/pretrained/weight_conversions/hubert.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/pretrained/weight_conversions/hubert.py)
 - [transformer_lens/utilities/activation_functions.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/utilities/activation_functions.py)
 
  This guide covers the initial steps for installing TransformerLens and using its core APIs to explore model internals. With the release of version 3.0, the library has shifted to a "bridge" architecture that instruments native Hugging Face models, while maintaining a compatibility layer for existing code.

 
## Installation

 TransformerLens can be installed via pip. For a basic installation:

 
```

```

 For specialized use cases (e.g., multimodal models, quantization, or development), see the detailed instructions in [Installation and Configuration](https://deepwiki.com/TransformerLensOrg/TransformerLens/2.1-installation-and-configuration).

 Sources: [README.md30-33](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/README.md?plain=1#L30-L33) [docs/source/content/getting_started.md11-17](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/docs/source/content/getting_started.md?plain=1#L11-L17)

 
## The v3 API: TransformerBridge

 In TransformerLens v3, `TransformerBridge` is the primary entry point. It wraps native Hugging Face models using **Architecture Adapters**, allowing you to use TransformerLens features (hooks, caching, patching) on the real HF model implementation rather than a reimplementation.

 
```

```

 For users moving from `HookedTransformer.from_pretrained`, refer to [Migrating from v2 to v3](https://deepwiki.com/TransformerLensOrg/TransformerLens/2.2-migrating-from-v2-to-v3).

 Sources: [docs/source/content/getting_started.md19-32](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/docs/source/content/getting_started.md?plain=1#L19-L32) [docs/source/content/migrating_to_v3.md13-27](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/docs/source/content/migrating_to_v3.md?plain=1#L13-L27)

 
## System Architecture

 The following diagrams illustrate how the high-level user API maps to the underlying code entities.

 
### Bootstrapping a Model

 
```

```

 Sources: [docs/source/content/getting_started.md30-32](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/docs/source/content/getting_started.md?plain=1#L30-L32) [docs/source/content/model_structure.md127-134](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/docs/source/content/model_structure.md?plain=1#L127-L134)

 
### Hook Execution Flow

 
```

```

 Sources: [docs/source/content/model_structure.md45-113](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/docs/source/content/model_structure.md?plain=1#L45-L113) [transformer_lens/model_bridge/bridge.py560-660](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/model_bridge/bridge.py#L560-L660)

 
## Basic Usage Patterns

 
### Running with Cache

 The `run_with_cache` method is the workhorse of mechanistic interpretability. It executes the model and returns an `ActivationCache` containing every intermediate tensor.

 
```

```

 
### Intervention with Hooks

 Hooks allow you to modify activations on the fly. This is essential for techniques like **Activation Patching**.

 
```

```

 Sources: [docs/source/content/model_structure.md45-113](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/docs/source/content/model_structure.md?plain=1#L45-L113) [docs/source/content/migrating_to_v3.md103-111](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/docs/source/content/migrating_to_v3.md?plain=1#L103-L111) [demos/Main_Demo.ipynb326-393](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/demos/Main_Demo.ipynb#L326-L393)

 
## Key Concepts

 
| Feature | Code Entity | Description |
|---|---|---|
| Model Loading | TransformerBridge.boot_transformers | The standard way to load and instrument HF models. |
| Activation Access | ActivationCache | A dictionary-like object storing tensors from a forward pass. |
| Intervention | HookPoint | Objects inserted into the model graph where functions can be "hooked". |
| Compatibility | enable_compatibility_mode() | Method to enable weight folding/centering for legacy parity. |

 Sources: [docs/source/content/getting_started.md19-32](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/docs/source/content/getting_started.md?plain=1#L19-L32) [docs/source/content/migrating_to_v3.md49-74](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/docs/source/content/migrating_to_v3.md?plain=1#L49-L74) [docs/source/content/model_structure.md7-10](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/docs/source/content/model_structure.md?plain=1#L7-L10)

 
## Next Steps

 
 - **Installation Details**: See [Installation and Configuration](https://deepwiki.com/TransformerLensOrg/TransformerLens/2.1-installation-and-configuration) for environment variables like `HF_TOKEN` and `TRANSFORMERLENS_HF_RETRY`.
 - **Migration**: If you have code using `HookedTransformer`, see [Migrating from v2 to v3](https://deepwiki.com/TransformerLensOrg/TransformerLens/2.2-migrating-from-v2-to-v3) to understand how to maintain numerical parity.
 - **Deep Dive**: Learn about the underlying [Core Architecture](https://deepwiki.com/TransformerLensOrg/TransformerLens/3-core-architecture) and the [Hook System](https://deepwiki.com/TransformerLensOrg/TransformerLens/3.3-hook-system).
 
 Sources: [docs/source/content/getting_started.md38-66](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/docs/source/content/getting_started.md?plain=1#L38-L66) [docs/source/content/migrating_to_v3.md1-5](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/docs/source/content/migrating_to_v3.md?plain=1#L1-L5)
