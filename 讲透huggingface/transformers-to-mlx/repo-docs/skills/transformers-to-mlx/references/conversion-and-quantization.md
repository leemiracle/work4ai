# Conversion and Quantization

## `mlx_lm.convert`

The primary tool for converting and quantizing models is `mlx_lm.convert`. It reads the original safetensors checkpoint, applies `sanitize()`, optionally quantizes weights, and writes the result as MLX-format safetensors.

### Basic usage

```bash
# Quantize to 4-bit (default group_size=64)
mlx_lm.convert --hf-path /path/to/model -q --q-bits 4 --mlx-path /path/to/output

# From a local directory
mlx_lm.convert --hf-path ./models/MyModel -q --mlx-path ./models/MyModel-4bit
```

### Iterative sanitize validation

`mlx_lm.convert` is the fastest way to validate your `sanitize()` method. Run it after each change — the error messages tell you exactly which weight keys don't match the model structure:

```
N parameters not in model: [list of extra keys]
M parameters missing: [list of missing keys]
```

Track the count of mismatches — it should decrease with each fix. When it reaches zero, conversion succeeds and you can move on to inference testing.

### Streaming conversion

`mlx_lm.convert` streams weights through memory rather than loading the entire model at once. This means you can quantize models larger than available RAM — the full fp16 model never needs to fit in memory. Only the output (quantized) model size matters for disk space.

### Common options

| Flag | Description |
|------|-------------|
| `-q` | Enable quantization |
| `--q-bits 4` | Bits per weight (default: 4) |
| `--q-group-size 64` | Quantization group size (default: 64) |
| `--hf-path` | Source model path (local dir or HF repo ID) |
| `--mlx-path` | Output directory |

### Output structure

After conversion, the output directory contains:
- `config.json` — model config with `quantization` and `quantization_config` fields added
- `model-NNNNN-of-MMMMM.safetensors` — weight shards
- `model.safetensors.index.json` — shard index
- `tokenizer.json`, `tokenizer_config.json`, etc. — tokenizer files (copied from source)

## Quantization considerations

### Bits per weight

- **4-bit**: Standard choice, good quality/size tradeoff. Most models work well at 4-bit.
- **3-bit**: More aggressive compression, may degrade quality for some models. Useful for very large models that need to fit in memory.
- **8-bit**: Minimal quality loss, larger size. Useful when quality is paramount.

### Model size estimation

For 4-bit quantization with group_size=64, the effective bits per weight is slightly above 4 (typically ~4.5) due to scale and bias metadata. A rough estimate:

```
size_gb ≈ total_parameters × 4.5 / 8 / 1e9
```

### Verifying conversion

After conversion, verify the quantized model loads correctly:

```python
from mlx_lm.utils import load
model, tokenizer = load("/path/to/output")
```

Then run generation tests (see Phase 4 in the main skill document).

## Quantize-first strategy

For very large models that cannot fit in fp16/bf16 on available hardware, the testing workflow changes fundamentally — see [Large Models](large-models.md) for guidance on the quantize-first approach where transformers comparison isn't feasible.
