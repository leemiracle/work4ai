# Hybrid and SSM Models

This reference covers challenges specific to models that mix layer types (e.g., Mamba/SSM + Attention) or use state-space models.

## Layer Type Dispatch

Hybrid models declare per-layer architecture in the config, typically via `layer_types` or `layers_block_type`:

```json
"layers_block_type": ["mamba", "mamba", "mamba", "hybrid", "mamba", "mamba", "hybrid", ...]
```

The model's `DecoderLayer` must dispatch to the right sub-modules based on the layer type. Each layer may also contain multiple blocks — for example, a Mamba block AND an MLP/MoE block.

## Cache Construction

Hybrid layers need different cache types for their different sub-modules. The `make_cache()` method must return the right cache type per layer:

```python
from mlx_lm.models.cache import CacheList, KVCache
from mlx_lm.models.ssm import ArraysCache

def make_cache(self):
    caches = []
    for layer_type in self.args.layers_block_type:
        if layer_type == "hybrid":
            # Attention needs KVCache, SSM needs ArraysCache
            caches.append(CacheList(KVCache(), ArraysCache(size=2)))
        else:
            # Pure SSM layer
            caches.append(ArraysCache(size=2))
    return caches
```

Key points:
- `KVCache` — for attention layers (stores key/value states)
- `ArraysCache(size=N)` — for SSM layers (stores conv state + ssm state)
- `CacheList` — combines multiple cache types for a single layer
- The `size` parameter in `ArraysCache` must match the number of state tensors the SSM expects

Getting this wrong typically causes `'tuple' has no attribute 'state'` or similar errors at generation time (not during a single forward pass, so it may not be caught by the numerical comparison scripts).

## CUDA-Only Dependencies

Some model architectures depend on CUDA-only packages like `mamba_ssm` or `causal_conv1d` for optimized kernels. These cannot be installed on macOS.

**Transformers fallback:** The transformers library includes naive Python implementations of these operations as a fallback. When running transformers on CPU for comparison testing, these fallbacks are used automatically. No action needed, but be aware:
- Installation will show warnings/errors for `mamba_ssm` — these can be ignored
- The fallback implementations are slower but numerically correct
- If the transformers model code has a hard dependency (no fallback), you won't be able to run transformers comparisons for that model

**MLX side:** The mlx-lm library has its own SSM implementations in `mlx_lm/models/ssm.py` with Metal kernels. These are the reference for the MLX conversion — don't try to port the CUDA kernels.

## Attention Scaling Variants

Some hybrid models use non-standard attention scaling. Always verify the scaling factor in the transformers source:

```python
# Standard
scale = head_dim ** -0.5

# Zamba2: uses half the head dimension
scale = (head_dim // 2) ** -0.5

# Models with attention_multiplier config
scale = config.attention_multiplier
```

A wrong scaling factor produces plausible-looking but incorrect output — predictions will be confident but wrong. This is hard to catch from generation alone; the numerical comparison will show systematic differences in attention output magnitudes.

## GatedDeltaNet (Linear Attention)

GatedDeltaNet is a linear attention variant used in hybrid models like Qwen3.5 and OLMo-Hybrid. It replaces standard attention in most layers, with full attention every N layers.

### Key Components

- **Depthwise conv1d**: Applied to the projected QKV before the linear attention update. Some implementations fuse QKV+Z into a single projection (`in_proj_qkvz`), others keep separate projections (`in_proj_qkv`, `in_proj_z`).
- **Gated delta update**: The core linear attention mechanism in `gated_delta.py`. Takes Q, K, V, alpha, beta, A_log, dt_bias, and computes a running state update. Try to use the update function in `gated_delta.py` instead of replicating the computations in the model implementation. If this is not possible, point out why in your report, but do not refactor the code unless asked.
- **RMSNormGated**: A gated variant of RMSNorm applied to the output, using a gate (Z) produced from the input projection.

### Cache

GatedDeltaNet layers typically use `ArraysCache` (not `KVCache`). The cache holds slots for the conv1d state(s) and slots for the running SSM state. For example, Qwen 3.5 uses two slots (one fused conv1d + one SSM state), while OLMo Hybrid uses four (separate q, k, v conv1d states + one SSM state).

```python
# Adjust `size` to the number of slots this model's layers need.
def make_cache(self):
    return [
        ArraysCache(size=N) if l.is_linear else KVCache()
        for l in self.layers
    ]
```

### Mask Handling

GatedDeltaNet uses `create_ssm_mask` (not `create_attention_mask`) for its layers. The model must create both mask types and dispatch per layer:

```python
fa_mask = create_attention_mask(hidden_states, cache[self.fa_idx])
ssm_mask = create_ssm_mask(hidden_states, cache[self.ssm_idx])

for layer, c in zip(self.layers, cache):
    mask = ssm_mask if layer.is_linear else fa_mask
    hidden_states = layer(hidden_states, mask=mask, cache=c)
```

### Implementation Variants

Two main patterns exist in mlx-lm:

1. **Separate projections** (`qwen3_5.py`): `in_proj_qkv`, `in_proj_z`, `in_proj_b`, `in_proj_a` as separate `nn.Linear` modules
2. **Fused projections** (`qwen3_next.py`): `in_proj_qkvz` and `in_proj_ba` with interleaved head layout requiring `fix_query_key_value_ordering` to unpack

When porting from transformers, check whether the checkpoint uses fused or separate projections by inspecting weight names.

### RoPE in GatedDeltaNet Models

GatedDeltaNet layers do **not** use RoPE — only the full attention layers do. RoPE configuration is typically nested inside `rope_parameters` as a dict, not as top-level config fields:

```json
"rope_parameters": {
    "type": "default",
    "rope_theta": 100000,
    "partial_rotary_factor": 0.25
}
```

Extract these in `__post_init__` to populate the top-level fields that `initialize_rope` expects.

