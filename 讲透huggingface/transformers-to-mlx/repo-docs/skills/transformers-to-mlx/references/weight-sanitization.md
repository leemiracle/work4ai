# Weight Sanitization

The `sanitize()` method on the `Model` class transforms checkpoint weight names and shapes to match the MLX model's module structure. This is where most loading errors occur — expect to iterate.

**Important:** `sanitize()` must handle two sources of weights:

1. **Transformers-native weights** — the original safetensors checkpoint from Hugging Face
2. **MLX-quantized weights** — produced by `mlx_lm.convert` after quantization, which use the MLX model's own key names

After a model is quantized with `mlx_lm.convert`, the resulting weights already use the MLX module names (the output of a previous `sanitize()` pass). When these quantized weights are loaded, `sanitize()` runs again. If it blindly applies transformations (e.g., renaming keys that no longer match the original patterns), it can break loading.

In practice, this means sanitize logic should be **idempotent** or guarded — transformations should check whether a key matches the source pattern before rewriting it, and pass through keys that already match the MLX structure unchanged.

## Common Transformations

These appear in nearly every conversion:

### Remove weights not needed at inference

```python
# RoPE frequencies are computed at runtime in MLX
if "rotary_emb.inv_freq" in k:
    continue
```

Other examples: MTP (multi-token prediction) heads, training-only buffers.

### Transpose conv1d weights

PyTorch conv1d stores `(out_channels, 1, kernel_size)`, MLX expects `(out_channels, kernel_size, 1)`:

```python
if "conv1d.weight" in k and v.ndim == 3 and v.shape[-1] != 1:
    v = v.moveaxis(2, 1)
```

### Handle tied embeddings

When `tie_word_embeddings=True`, the checkpoint may contain a duplicate `lm_head.weight`:

```python
if self.args.tie_word_embeddings:
    sanitized.pop("lm_head.weight", None)
```

### Stack expert weights

Individual expert weights are stacked into a single tensor for `SwitchGLU`:

```python
# experts.0.gate_proj.weight, experts.1.gate_proj.weight, ...
# -> switch_mlp.gate_proj.weight with shape (num_experts, ...)
```

### nn.Sequential index insertion

MLX's `nn.Sequential` stores children as `.layers.{idx}`, but checkpoints often omit the `layers` level:

```python
# checkpoint: adapter_list.0.0.weight  (adapter 0, sequential element 0)
# MLX needs:  adapter_list.0.layers.0.weight
if "_adapter_list" in k:
    new_key = re.sub(r'\.(\d+)\.(\d+)\.weight$', r'.\1.layers.\2.weight', k)
```

## Weight Format Detection

Different model sizes sometimes use different weight naming conventions, even within the same architecture. Always check weight prefixes across all target models before writing `sanitize()`.

**How to detect:** Inspect the weight name patterns from the safetensors index (this avoids downloading full weights):

```python
from huggingface_hub import hf_hub_download
import json

index_path = hf_hub_download(repo_id, "model.safetensors.index.json")
with open(index_path) as f:
    weight_names = sorted(json.load(f)["weight_map"].keys())
for name in weight_names[:20]:
    print(name)
```

**When formats differ**, the sanitize function must detect which format is present and branch accordingly:

```python
is_legacy_format = any("model.blocks." in k for k in weights.keys())

if is_legacy_format:
    # Remap legacy weight names to match the MLX model structure
    ...
else:
    # Standard format, minimal renaming
    ...
```

### Transformers conversion_mapping.py

Transformers maintains a centralized weight key remapping registry in `src/transformers/modeling_utils.py` (or as `_checkpoint_conversion_mapping` on individual model classes). However, the most reliable source is `conversion_mapping.py` in the model's directory:

```
transformers/src/transformers/models/<model_type>/conversion_mapping.py
```

This file maps between checkpoint key names and the transformers model attribute names. Always check it when the checkpoint uses different naming than the transformers model class attributes. The MLX model should use **transformers attribute names** (the right-hand side of the mapping), and `sanitize()` should remap checkpoint names to match.

**Common mistake:** Using checkpoint key names directly in the MLX model definition instead of the transformers attribute names. This causes weight loading failures because `sanitize()` remaps to transformers names but the MLX model expects checkpoint names (or vice versa). The mapping in `conversion_mapping.py` is the authoritative source of truth.

### Mixed formats in a single checkpoint

Some checkpoints contain weights in **both** formats simultaneously (e.g., shared block weights in legacy format alongside layer-specific adapter weights in standard format). When this happens, process the more-specific format first (with `continue`), then let the general format fill in the rest.

## Shared / Tied Weights

Some architectures share a set of weights across multiple layers (e.g., Zamba2's `num_mem_blocks` shared attention blocks). The checkpoint stores these weights once, but the MLX model expects a copy at each layer.

### Replication pattern

The first N hybrid layers hold unique weights; subsequent layers are tied to one of those N based on cycling:

```python
# hybrid_layer_ids: indices of layers that use the shared block
# num_mem_blocks: how many unique shared blocks exist
unique_source_layers = hybrid_layer_ids[:num_mem_blocks]

for target_pos, target_layer_idx in enumerate(hybrid_layer_ids):
    if target_pos < num_mem_blocks:
        continue  # this is a unique block, already has weights

    source_block_id = target_pos % num_mem_blocks
    source_layer_idx = unique_source_layers[source_block_id]

    for source_key in keys_starting_with(f"model.layers.{source_layer_idx}.shared_transformer"):
        target_key = source_key.replace(
            f"model.layers.{source_layer_idx}.",
            f"model.layers.{target_layer_idx}.",
        )
        if target_key not in sanitized:
            sanitized[target_key] = sanitized[source_key]
```

### Adapter filtering

When shared blocks have per-layer adapters (e.g., LoRA), each block stores adapters for ALL positions but only some belong to that block. Filter by `adapter_idx % num_mem_blocks == block_id`:

```python
adapter_idx = int(match.group(1))
if adapter_idx % num_mem_blocks != block_id:
    continue  # this adapter belongs to a different block
```

## Ordering of Transformations

The order in which name transformations are applied matters. A common bug: a general rename (e.g., `linear_fc1` -> `gate_up_proj`) runs before a more specific pattern (e.g., `linear_fc1_lora_A_list` -> `gate_up_proj_adapter_list.*.layers.0`) and corrupts the key before the specific pattern can match.

**Rule: process specific patterns before general renames.**

```python
# CORRECT: specific LoRA patterns first
lora_a_match = re.match(r"feed_forward\.linear_fc1_lora_A_list\.(\d+)\.weight", rest)
lora_b_match = re.match(r"feed_forward\.linear_fc1_lora_B_list\.(\d+)\.weight", rest)

if lora_a_match:
    # Handle LoRA A -> adapter_list.{idx}.layers.0
    ...
elif lora_b_match:
    # Handle LoRA B -> adapter_list.{idx}.layers.1
    ...
else:
    # General MLP rename (only for non-LoRA keys)
    rest = rest.replace("linear_fc1.", "gate_up_proj.")
    rest = rest.replace("linear_fc2.", "down_proj.")
```

## Debugging Tips

### Count mismatches

When loading fails with "N parameters not in model", the error message tells you how many keys are wrong. Track this number — it should decrease with each fix.

### Print what you're producing

Add temporary logging to sanitize to see the key mapping:

```python
if new_key != k:
    print(f"  {k}\n  -> {new_key}")
```

### Compare key sets

```python
model_keys = set(dict(model.named_parameters()).keys())
weight_keys = set(sanitized.keys())

missing = model_keys - weight_keys
extra = weight_keys - model_keys

print(f"Missing from weights ({len(missing)}):")
for k in sorted(missing)[:20]:
    print(f"  {k}")
print(f"Extra in weights ({len(extra)}):")
for k in sorted(extra)[:20]:
    print(f"  {k}")
```

Look for systematic patterns in the missing/extra keys — they usually point to a single transformation that's wrong or missing.
