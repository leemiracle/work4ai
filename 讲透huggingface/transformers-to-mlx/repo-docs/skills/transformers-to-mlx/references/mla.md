# Multi-head Latent Attention (MLA)

MLA is a compressed attention mechanism introduced by DeepSeek that reduces KV cache size while maintaining model quality. It's used by DeepSeek V2/V3, GLM-4/5, and similar architectures.

## Architecture overview

Instead of storing full K and V projections per head, MLA compresses them into a low-rank latent representation:

```
                    ┌─→ q_pe (rope dims) ──────────────────────┐
x → q_a_proj → q_a_layernorm → q_b_proj → reshape → q_nope ──┤→ attention
                                                                │
x → kv_a_proj_with_mqa ──┬─→ k_pe (rope dims) ────────────────┤
                          └─→ kv_a_layernorm ──┬─→ embed_q ───┘
                                                └─→ unembed_out → o_proj → output
```

### Key components

| Component | Shape | Purpose |
|-----------|-------|---------|
| `q_a_proj` | `(hidden, q_lora_rank)` | Compress queries to latent space |
| `q_a_layernorm` | `(q_lora_rank,)` | Normalize compressed queries |
| `q_b_proj` | `(q_lora_rank, heads × q_head_dim)` | Expand to per-head Q |
| `kv_a_proj_with_mqa` | `(hidden, kv_lora_rank + rope_dim)` | Compress KV + extract RoPE keys |
| `kv_a_layernorm` | `(kv_lora_rank,)` | Normalize compressed KV |
| `embed_q` | MultiLinear `(nope_dim, kv_lora_rank, heads)` | Per-head nope-K projection |
| `unembed_out` | MultiLinear `(kv_lora_rank, v_head_dim, heads)` | Per-head V projection |
| `o_proj` | `(heads × v_head_dim, hidden)` | Output projection |

### KV cache efficiency

The KV cache stores only the compressed representation (`kv_lora_rank + rope_dim` dimensions per position) instead of full K and V per head. For example, with `kv_lora_rank=512` and `rope_dim=64`, that's 576 values per position instead of `2 × heads × head_dim` (e.g., 2 × 64 × 256 = 32,768 for GLM-5).

## MLX implementation

MLA models in MLX use `MultiLinear` (from `mlx_lm/models/mla.py`) for the per-head projections `embed_q` and `unembed_out`. `MultiLinear` efficiently batches independent linear transformations across heads.

### Reference models

- `deepseek_v3.py` — base MLA + MoE without DSA indexer
- `deepseek_v32.py` — MLA + MoE with DSA indexer (uses `CacheList` for dual caches)
- `glm4_moe_lite.py` — MLA + MoE, close to deepseek_v3 pattern

## Weight sanitization: `kv_b_proj` splitting

Transformers stores a single `kv_b_proj` weight that combines the nope-K and V projections. MLX splits this into separate `embed_q` and `unembed_out` MultiLinear weights.

The sanitize transformation:

```python
if "kv_b_proj" in key:
    # 1. Get the full kv_b_proj weight
    weight = weights[key]  # shape: (heads * (nope_dim + v_dim), kv_lora_rank)

    # 2. If quantized, dequantize first
    if quantized:
        weight = mx.dequantize(weight, scales, biases, group_size, bits)

    # 3. Reshape to per-head blocks
    weight = weight.reshape(num_heads, nope_dim + v_dim, kv_lora_rank)

    # 4. Split into embed_q (nope-K) and unembed_out (V)
    embed_q = weight[:, :nope_dim, :]       # (heads, nope_dim, kv_lora_rank)
    unembed_out = weight[:, nope_dim:, :]   # (heads, v_dim, kv_lora_rank)

    # 5. Store with the correct key names
    prefix = key.replace("kv_b_proj.weight", "")
    new_weights[prefix + "embed_q.weight"] = embed_q
    new_weights[prefix + "unembed_out.weight"] = unembed_out
    continue
```

When the source weights are quantized, you must dequantize before splitting (since the split boundary may not align with quantization groups), then the weights will be re-quantized when loaded by the MLX model.

## Config parsing: `rope_parameters` nested dict

Some MLA models (e.g., GLM-5) store RoPE configuration in a nested `rope_parameters` dict instead of top-level `rope_theta` and `rope_scaling` fields:

```json
"rope_parameters": {
    "rope_theta": 1000000,
    "rope_type": "default"
}
```

Handle this in `__post_init__`:

```python
def __post_init__(self):
    if self.rope_parameters is not None:
        if "rope_theta" in self.rope_parameters:
            self.rope_theta = self.rope_parameters["rope_theta"]
        rope_type = self.rope_parameters.get("rope_type", "default")
        if rope_type != "default":
            self.rope_scaling = self.rope_parameters
```

This extracts `rope_theta` and, for non-default rope types (e.g., `yarn`, `dynamic`), passes the entire dict as `rope_scaling` for `initialize_rope()` to process.

## Attention scaling with `mscale`

Some MLA models with extended context use `mscale_all_dim` to adjust the attention scale factor based on the RoPE scaling factor:

```python
if config.rope_scaling is not None:
    mscale_all_dim = config.rope_scaling.get("mscale_all_dim", 0)
    if mscale_all_dim:
        scaling_factor = config.rope_scaling["factor"]
        if scaling_factor > 1:
            s = 0.1 * mscale_all_dim * math.log(scaling_factor) + 1.0
            self.scale = self.scale * s * s
```

This replaces the standard `1/sqrt(head_dim)` scaling. Missing this produces plausible-looking but subtly wrong output — typically visible only in numerical comparisons, not generation quality.

## RoPE interleaving

MLA models commonly use interleaved RoPE. In config: `rope_interleave: true`. In MLX: `traditional=True` (counterintuitively — MLX's "traditional" mode matches PyTorch's interleaved layout).

```python
self.rope = initialize_rope(
    dims=self.qk_rope_head_dim,
    base=self.rope_theta,
    traditional=config.rope_interleave,  # True = interleaved
    ...
)
```
