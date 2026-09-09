> 来源: [https://deepwiki.com/TransformerLensOrg/TransformerLens/1-overview](https://deepwiki.com/TransformerLensOrg/TransformerLens/1-overview)
> DeepWiki TransformerLensOrg/TransformerLens | Last indexed: 16 July 2026 (4ba218

# Overview

  Relevant source files 
 - [.github/workflows/checks.yml](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/.github/workflows/checks.yml)
 - [.github/workflows/release.yml](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/.github/workflows/release.yml)
 - [README.md](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/README.md?plain=1)
 - [demos/Exploratory_Analysis_Demo.ipynb](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/demos/Exploratory_Analysis_Demo.ipynb)
 - [demos/Interactive_Neuroscope.ipynb](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/demos/Interactive_Neuroscope.ipynb)
 - [demos/Main_Demo.ipynb](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/demos/Main_Demo.ipynb)
 - [demos/No_Position_Experiment.ipynb](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/demos/No_Position_Experiment.ipynb)
 - [demos/doc_sanitize.cfg](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/demos/doc_sanitize.cfg)
 - [docs/source/_static/custom.css](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/docs/source/_static/custom.css)
 - [docs/source/content/getting_started_mech_interp.md](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/docs/source/content/getting_started_mech_interp.md?plain=1)
 - [docs/source/content/model_tables.md](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/docs/source/content/model_tables.md?plain=1)
 - [docs/source/content/news/release-3.0.md](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/docs/source/content/news/release-3.0.md?plain=1)
 - [makefile](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/makefile)
 - [pyproject.toml](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/pyproject.toml)
 - [transformer_lens/__init__.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/__init__.py)
 - [uv.lock](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/uv.lock)
 
  TransformerLens is a library for mechanistic interpretability of generative language models. It provides programmatic access to internal activations and enables interventions on these activations to reverse engineer the algorithms learned during training. The library is designed for exploratory analysis with short feedback loops to make research feel like play.

 With the release of **TransformerLens 3.0**, the library introduces the **TransformerBridge** architecture, which allows for instrumentation of 9,000+ HuggingFace models across 50+ architecture families by wrapping native implementations rather than reimplementing them [docs/source/content/news/release-3.0.md4-26](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/docs/source/content/news/release-3.0.md?plain=1#L4-L26)

 
## Library Purpose and Design Philosophy

 TransformerLens fills the gap between model usage infrastructure (HuggingFace, DeepSpeed) and interpretability research tools. The core design principle enables exploratory analysis by minimizing the time between having an experiment idea and seeing results [demos/Exploratory_Analysis_Demo.ipynb206-211](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/demos/Exploratory_Analysis_Demo.ipynb#L206-L211)

 The library addresses four key requirements:

 
 - **Activation Access**: Expose internal model activations through `HookPoint` objects.
 - **Activation Intervention**: Enable editing, removal, or replacement of activations via the hook system.
 - **Model Loading**: Support loading 9,000+ models with preserved or converted weights [README.md23-26](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/README.md?plain=1#L23-L26)
 - **Analysis Tools**: Provide built-in tools for mechanistic interpretability research such as patching and SVD analysis.
 
 Sources: [README.md18-26](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/README.md?plain=1#L18-L26) [docs/source/content/news/release-3.0.md4-26](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/docs/source/content/news/release-3.0.md?plain=1#L4-L26)

 
## Core Architecture (v3.0)

 TransformerLens 3.0 introduces a dual-path architecture. While `HookedTransformer` remains as the legacy path, `TransformerBridge` is the recommended path for modern models.

 
### Code Entity Space: TransformerBridge vs HookedTransformer

 
```

```

 Sources: [transformer_lens/model_bridge/bridge.py1-100](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/model_bridge/bridge.py#L1-L100) [transformer_lens/HookedTransformer.py1-50](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/HookedTransformer.py#L1-L50) [docs/source/content/news/release-3.0.md21-26](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/docs/source/content/news/release-3.0.md?plain=1#L21-L26)

 
### Key Classes and Roles

 
| Class | Purpose | Key Methods |
|---|---|---|
| TransformerBridge | v3.0 interface wrapping native HF models | boot_transformers(), run_with_cache(), enable_compatibility_mode() |
| HookedTransformer | Legacy implementation of decoder-only models | from_pretrained(), run_with_cache(), fold_ln() |
| ArchitectureAdapter | Maps HF module graphs to generalized components | get_component_mapping(), get_weight_conversions() |
| HookPoint | Interception points for activations | add_hook(), remove_hooks() |
| ActivationCache | Storage and analysis for activations | decompose_resid(), logit_attrs() |

 Sources: [transformer_lens/__init__.py19-25](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/__init__.py#L19-L25) [transformer_lens/model_bridge/bridge.py44-55](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/model_bridge/bridge.py#L44-L55) [docs/source/content/news/release-3.0.md36-39](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/docs/source/content/news/release-3.0.md?plain=1#L36-L39)

 
## Model Loading and Data Flow

 The `TransformerBridge` system uses an adapter pattern to instrument models without reimplementing their forward passes.

 
### Natural Language Space to Code Entity Space: The Bridge Loading Flow

 
```

```

 Sources: [transformer_lens/model_bridge/bridge.py110-150](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/model_bridge/bridge.py#L110-L150) [docs/source/content/news/release-3.0.md21-26](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/docs/source/content/news/release-3.0.md?plain=1#L21-L26)

 
### Weight Processing in v3.0

 Unlike the legacy `HookedTransformer`, the `TransformerBridge` preserves raw HuggingFace weights by default. Weight folding (LayerNorm folding) and centering are now opt-in via `bridge.enable_compatibility_mode()` [docs/source/content/news/release-3.0.md36-39](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/docs/source/content/news/release-3.0.md?plain=1#L36-L39)

 
## Analysis Tools Overview

 TransformerLens provides specialized tools for mechanistic interpretability research, integrated with both the legacy and bridge architectures.

 
| Module | Primary Functionality | Code Reference |
|---|---|---|
| patching | Causal analysis via activation replacement | transformer_lens/patching.py |
| head_detector | Automated detection of induction/S-inhibition heads | transformer_lens/head_detector.py |
| SVDInterpreter | SVD analysis of weight matrices (OV/QK circuits) | transformer_lens/SVDInterpreter.py |
| FactoredMatrix | Memory-efficient operations on decomposed matrices | transformer_lens/FactoredMatrix.py |

 Sources: [transformer_lens/__init__.py1-12](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/__init__.py#L1-L12) [README.md57-90](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/README.md?plain=1#L57-L90)

 
## Basic Usage (v3.0)

 The standard entry point for using the library in v3.0 is the `TransformerBridge`.

 
```

```

 Sources: [README.md43-51](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/README.md?plain=1#L43-L51) [docs/source/content/news/release-3.0.md40-43](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/docs/source/content/news/release-3.0.md?plain=1#L40-L43)

 
## Supported Architectures

 TransformerLens supports over 50 architecture families, including:

 
 - **Autoregressive (Decoder-only)**: Llama (1, 2, 3), GPT-2, Mistral, Gemma, Phi, Qwen, Pythia.
 - **Encoder-only**: BERT.
 - **Encoder-Decoder**: T5.
 - **Non-Transformer**: Mamba (State-Space Models).
 - **Multimodal**: LLaVA, Gemma 3 Multimodal.
 
 Sources: [docs/source/content/news/release-3.0.md21-26](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/docs/source/content/news/release-3.0.md?plain=1#L21-L26) [transformer_lens/__init__.py21-23](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/__init__.py#L21-L23)
