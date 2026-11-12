> 来源: [https://deepwiki.com/TransformerLensOrg/TransformerLens/7-interpretability-tools](https://deepwiki.com/TransformerLensOrg/TransformerLens/7-interpretability-tools)
> DeepWiki TransformerLensOrg/TransformerLens | Last indexed: 16 July 2026 (4ba218

# Interpretability Tools

  Relevant source files 
 - [tests/acceptance/test_activation_cache.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/tests/acceptance/test_activation_cache.py)
 - [tests/integration/model_bridge/test_direct_logit_attribution.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/tests/integration/model_bridge/test_direct_logit_attribution.py)
 - [tests/unit/test_hooked_root_module.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/tests/unit/test_hooked_root_module.py)
 - [tests/unit/tools/test_direct_logit_attribution.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/tests/unit/tools/test_direct_logit_attribution.py)
 - [transformer_lens/ActivationCache.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/ActivationCache.py)
 - [transformer_lens/SVDInterpreter.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/SVDInterpreter.py)
 - [transformer_lens/head_detector.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/head_detector.py)
 - [transformer_lens/hook_points.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/hook_points.py)
 - [transformer_lens/patching.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/patching.py)
 - [transformer_lens/tools/__init__.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/tools/__init__.py)
 - [transformer_lens/tools/analysis/__init__.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/tools/analysis/__init__.py)
 - [transformer_lens/tools/analysis/direct_logit_attribution.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/tools/analysis/direct_logit_attribution.py)
 
  This page provides an overview of the analysis and interpretability tools available in TransformerLens. These tools enable researchers to understand how transformer models work internally by examining activations, performing causal interventions, and detecting specialized components.

 For basic model loading and caching functionality, see [Core Architecture](https://deepwiki.com/TransformerLensOrg/TransformerLens/3-core-architecture). For specific evaluation metrics and datasets, see [Evaluation Tools](https://deepwiki.com/TransformerLensOrg/TransformerLens/7.5-evaluation-tools).

 
## Hook System Foundation

 TransformerLens interpretability tools are built on top of the hook system, which provides access to intermediate model activations during forward passes. The `HookedRootModule` class enables temporary or permanent intervention on any activation via `HookPoint` modules.

 
### Code Entity Mapping: Hook System

 
```

```

 The hook system allows tools to:

 
 - Cache activations with `run_with_cache()` [transformer_lens/ActivationCache.py62](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/ActivationCache.py#L62-L62)
 - Apply temporary interventions with `run_with_hooks()` [transformer_lens/hook_points.py440-450](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/hook_points.py#L440-L450)
 - Perform causal analysis through activation patching [transformer_lens/patching.py10-25](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/patching.py#L10-L25)
 
 Sources: [transformer_lens/hook_points.py143-167](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/hook_points.py#L143-L167) [transformer_lens/ActivationCache.py53-137](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/ActivationCache.py#L53-L137) [transformer_lens/tools/analysis/__init__.py1-12](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/tools/analysis/__init__.py#L1-L12)

 
## Core Interpretability Tools

 
### Activation Patching

 The `patching.py` module implements activation patching techniques for causal analysis. The core function `generic_activation_patch()` enables systematic intervention on model activations by swapping "clean" activations into a "corrupted" run.

 
| Function | Purpose | Key Parameters |
|---|---|---|
| generic_activation_patch() | Generic patching framework | patch_setter, activation_name, patching_metric |
| get_act_patch_direct_path() | High-level path patching | model, corrupted_tokens, clean_cache |

 For details, see [Activation Patching](https://deepwiki.com/TransformerLensOrg/TransformerLens/7.1-activation-patching).

 Sources: [transformer_lens/patching.py92-148](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/patching.py#L92-L148) [transformer_lens/tools/analysis/direct_path_patching.py18-21](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/tools/analysis/direct_path_patching.py#L18-L21)

 
### Head Detection

 The `head_detector.py` module provides automated detection of specialized attention heads (e.g., induction heads) using pattern matching against the attention `pattern` stored in the `ActivationCache`.

 
```

```

 For details, see [Head Detection](https://deepwiki.com/TransformerLensOrg/TransformerLens/7.2-head-detection).

 Sources: [transformer_lens/head_detector.py34-100](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/head_detector.py#L34-L100) [transformer_lens/head_detector.py151-153](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/head_detector.py#L151-L153)

 
### SVD Interpreter

 The `SVDInterpreter` class analyzes singular vectors of model weight matrices (OV, $W_{in}$, $W_{out}$) to understand learned representations in the vocabulary space.

 
| Vector Type | Matrix Analyzed | Method |
|---|---|---|
| "OV" | Attention Output-Value | _get_OV_matrix() |
| "w_in" | MLP Input Weights | _get_w_in_matrix() |
| "w_out" | MLP Output Weights | _get_w_out_matrix() |

 For details, see [SVD Interpreter](https://deepwiki.com/TransformerLensOrg/TransformerLens/7.3-svd-interpreter).

 Sources: [transformer_lens/SVDInterpreter.py19-37](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/SVDInterpreter.py#L19-L37) [transformer_lens/SVDInterpreter.py127-165](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/SVDInterpreter.py#L127-L165)

 
### Direct Logit Attribution (DLA)

 DLA decomposes the final logit output into additive contributions from each component (embeddings, attention heads, MLP layers). This is implemented via `ActivationCache.logit_attrs` and the high-level `direct_logit_attribution` tool.

 **Key Invariant:** `sum(component_attribution) + b_U[token] == logit[token]` [tests/integration/model_bridge/test_direct_logit_attribution.py8](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/tests/integration/model_bridge/test_direct_logit_attribution.py#L8-L8)

 For details, see [Direct Logit Attribution](https://deepwiki.com/TransformerLensOrg/TransformerLens/7.4-direct-logit-attribution).

 Sources: [transformer_lens/tools/analysis/direct_logit_attribution.py1-22](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/tools/analysis/direct_logit_attribution.py#L1-L22) [transformer_lens/ActivationCache.py83-89](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/ActivationCache.py#L83-L89)

 
## Evaluation and Analysis Tools

 
### Model Evaluation

 TransformerLens includes utilities for assessing model performance on tasks relevant to mechanistic interpretability, such as Indirect Object Identification (IOI).

 
```

```

 For details, see [Evaluation Tools](https://deepwiki.com/TransformerLensOrg/TransformerLens/7.5-evaluation-tools).

 Sources: [transformer_lens/tools/analysis/direct_logit_attribution.py24-39](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/tools/analysis/direct_logit_attribution.py#L24-L39) [tests/acceptance/test_activation_cache.py11-47](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/tests/acceptance/test_activation_cache.py#L11-L47)

 
## Integration with Analysis Workflows

 These tools integrate with TransformerLens's caching and hook systems to enable comprehensive analysis workflows:

 
 - **Circuit Discovery**: Use `detect_head` to identify specialized components like induction heads.
 - **Causal Validation**: Apply `generic_activation_patch` to test if identified heads are causally necessary for a behavior.
 - **Logit Attribution**: Use `direct_logit_attribution` to see which heads or layers contribute most to the final prediction.
 - **Weight Analysis**: Use `SVDInterpreter` to map the directions used by those heads back to human-interpretable concepts in the vocabulary.
 
 Sources: [transformer_lens/tools/analysis/direct_logit_attribution.py15-22](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/tools/analysis/direct_logit_attribution.py#L15-L22) [transformer_lens/patching.py30-47](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/patching.py#L30-L47)
