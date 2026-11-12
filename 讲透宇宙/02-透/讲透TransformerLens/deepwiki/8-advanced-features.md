> 来源: [https://deepwiki.com/TransformerLensOrg/TransformerLens/8-advanced-features](https://deepwiki.com/TransformerLensOrg/TransformerLens/8-advanced-features)
> DeepWiki TransformerLensOrg/TransformerLens | Last indexed: 16 July 2026 (4ba218

# Advanced Features

  Relevant source files 
 - [tests/acceptance/test_multi_gpu.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/tests/acceptance/test_multi_gpu.py)
 - [tests/unit/pretrained_weight_conversions/test_apertus.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/tests/unit/pretrained_weight_conversions/test_apertus.py)
 - [tests/unit/pretrained_weight_conversions/test_olmo3.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/tests/unit/pretrained_weight_conversions/test_olmo3.py)
 - [tests/unit/test_split_qkv.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/tests/unit/test_split_qkv.py)
 - [tests/unit/test_use_attn_result.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/tests/unit/test_use_attn_result.py)
 - [tests/unit/utilities/test_devices.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/tests/unit/utilities/test_devices.py)
 - [transformer_lens/model_bridge/bridge.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/model_bridge/bridge.py)
 - [transformer_lens/model_bridge/generalized_components/attention.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/model_bridge/generalized_components/attention.py)
 - [transformer_lens/model_bridge/generalized_components/base.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/model_bridge/generalized_components/base.py)
 - [transformer_lens/model_bridge/generalized_components/block.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/model_bridge/generalized_components/block.py)
 - [transformer_lens/model_bridge/generalized_components/joint_qkv_attention.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/model_bridge/generalized_components/joint_qkv_attention.py)
 - [transformer_lens/train.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/train.py)
 - [transformer_lens/utilities/devices.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/utilities/devices.py)
 
  TransformerLens provides advanced capabilities for performance optimization, memory efficiency, specialized model architectures, and training. This page documents features that extend beyond core inference and activation caching.

 
## Weight Processing

 TransformerLens includes utilities for transforming model weights into more interpretability-friendly forms without changing the model's output. These transformations include LayerNorm folding, weight centering, and value bias folding.

 The `ProcessWeights` utility handles these conversions, particularly during the transition from a native HuggingFace model to a `TransformerBridge` or `HookedTransformer`.

 For details, see [Weight Processing](https://deepwiki.com/TransformerLensOrg/TransformerLens/8.1-weight-processing).

 Sources: [transformer_lens/model_bridge/bridge.py160-183](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/model_bridge/bridge.py#L160-L183) [transformer_lens/model_bridge/generalized_components/base.py81-93](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/model_bridge/generalized_components/base.py#L81-L93)

 
## Key-Value Caching

 When performing iterative inference or text generation, recomputing attention for the entire context is inefficient. Key-Value (KV) caching stores previously computed key and value projections. TransformerLens supports KV caching across both its legacy `HookedTransformer` and the newer `TransformerBridge` architectures, including support for Grouped Query Attention (GQA).

 
### KV Cache Flow in TransformerBridge

 
```

```

 For details, see [Key-Value Caching](https://deepwiki.com/TransformerLensOrg/TransformerLens/8.2-key-value-caching).

 Sources: [transformer_lens/model_bridge/generalized_components/attention.py141-146](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/model_bridge/generalized_components/attention.py#L141-L146) [transformer_lens/model_bridge/generalized_components/joint_qkv_attention.py101-128](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/model_bridge/generalized_components/joint_qkv_attention.py#L101-L128)

 
## Multi-GPU Support

 TransformerLens supports distributing model layers across multiple GPUs. This is essential for large models (e.g., Llama-3 70B) that exceed the memory of a single device. The system uses pipeline parallelism to partition `blocks` across available devices.

 
### Device Management

 The `move_to_and_update_config` utility ensures that moving a model to a new device also updates its internal `cfg.device` state, keeping the model and its metadata synchronized.

 
```

```

 For details, see [Multi-GPU Support](https://deepwiki.com/TransformerLensOrg/TransformerLens/8.3-multi-gpu-support).

 Sources: [transformer_lens/utilities/devices.py152-191](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/utilities/devices.py#L152-L191) [tests/acceptance/test_multi_gpu.py22-89](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/tests/acceptance/test_multi_gpu.py#L22-L89)

 
## FactoredMatrix

 The `FactoredMatrix` class is a specialized utility for representing a large matrix as the product of two smaller ones ($A = L \times R$). This is particularly useful in mechanistic interpretability for analyzing the $QK$ and $OV$ circuits of attention heads without materializing the full $d_{vocab} \times d_{vocab}$ matrices.

 
### Attention Circuit Analysis

 
```

```

 For details, see [FactoredMatrix](https://deepwiki.com/TransformerLensOrg/TransformerLens/8.4-factoredmatrix).

 Sources: [transformer_lens/model_bridge/bridge.py37](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/model_bridge/bridge.py#L37-L37) [transformer_lens/model_bridge/generalized_components/attention.py33-52](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/model_bridge/generalized_components/attention.py#L33-L52)

 
## Training

 While TransformerLens is primarily an inference and analysis library, it provides a `train()` function and `HookedTransformerTrainConfig` for fine-tuning or training small models from scratch on autoregressive language modeling tasks.

 
### Training Configuration

 
| Parameter | Role |
|---|---|
| lr | Learning rate |
| optimizer_name | Supports "Adam", "AdamW", and "SGD" |
| warmup_steps | Linear learning rate warmup |
| max_grad_norm | Gradient clipping threshold |

 The training loop integrates with `Weights and Biases` (wandb) for experiment tracking and provides automated checkpointing.

 For details, see [Training](https://deepwiki.com/TransformerLensOrg/TransformerLens/8.5-training).

 Sources: [transformer_lens/train.py22-61](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/train.py#L22-L61) [transformer_lens/train.py63-161](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/train.py#L63-L161)
