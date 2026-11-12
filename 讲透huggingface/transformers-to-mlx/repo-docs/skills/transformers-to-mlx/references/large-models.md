# Large Models

This reference covers challenges specific to models that push hardware limits — typically models where the quantized weights consume a significant fraction of available RAM (e.g., 400+ GB on a 512 GB machine).

## System Configuration

### Wired memory limit

macOS limits the amount of memory that can be wired (pinned) for GPU use. For large models, the default limit may be insufficient, causing the model to fail to load or triggering OOM during inference.

Increase the limit before loading the model:

```bash
sudo sysctl iogpu.wired_limit_mb=412000
```

The value must be:
- **Larger** than what the model requires for inference (model weights + KV cache + intermediate activations + overhead)
- **Smaller** than the total physical memory

A good rule of thumb: set it to ~80% of physical RAM. For a 512 GB machine with a 418 GB model, `412000` (412 GB) leaves headroom for the OS and other processes.

This setting does not persist across reboots; add it to a startup script if needed.

### `MLX_METAL_FAST_SYNCH=1`

This environment variable should be set for large model inference on Apple Silicon. It enables faster GPU synchronization which improves throughput:

```bash
MLX_METAL_FAST_SYNCH=1 mlx_lm.generate --model /path/to/model --prompt "Hello"
```

## OOM from `mlx_lm.generate`

The standard `mlx_lm.generate` API uses `mx.async_eval` to pipeline two forward passes simultaneously, overlapping computation with memory transfers. This roughly **doubles peak memory** compared to a single forward pass.

For models that nearly fill available RAM, this causes OOM even when the model loaded successfully. Symptoms:
- Model loads fine (memory usage matches expected model size)
- First forward pass starts but the process is killed or hangs

### Workaround: manual generation loop

Use a manual generation loop with a single `mx.eval` per step:

```python
import mlx.core as mx
from mlx_lm.utils import load

model, tokenizer = load("/path/to/model")
prompt_tokens = tokenizer.encode("Your prompt here")
input_ids = mx.array([prompt_tokens])

# Prefill
logits = model(input_ids)
next_token = mx.argmax(logits[:, -1, :], axis=-1)
mx.eval(next_token)

# Decode
cache = ...  # from prefill
for _ in range(max_tokens):
    logits = model(next_token[:, None], cache=cache)
    next_token = mx.argmax(logits[:, -1, :], axis=-1)
    # Fuse argmax + cache update into a single eval
    mx.eval(next_token, [c.state for c in cache])
    token_id = next_token.item()
    if token_id in tokenizer.eos_token_id:
        break
    print(tokenizer.decode([token_id]), end="", flush=True)
```

**Key detail:** fuse the argmax into the same `mx.eval` call as the cache state. Having two separate `mx.eval` calls (one for logits, one for argmax) materializes the full logits tensor in memory — for a 155K-token vocabulary, that's a significant allocation. The fused version computes the argmax as part of the computation graph, avoiding the intermediate materialization.

## Quantize-First Testing Strategy

When a model is too large to run in fp16/bf16 on available hardware, the standard testing workflow (Phase 4) cannot be used because you can't run transformers for comparison. The workflow changes to:

1. **Write modeling code + sanitize** — following Phases 1-3 as normal
2. **Quantize** — use `mlx_lm.convert` to validate sanitize and produce a quantized model
3. **Validate via generation only** — run the quantized model and verify:
   - Output is coherent and contextually appropriate
   - The model correctly follows its chat template (if applicable)
   - For instruction/chat models, it responds appropriately to the system prompt
   - For reasoning models, it produces thinking traces before answering
4. **Skip numerical comparison** — transformers comparison isn't feasible at this scale

This is less rigorous than the standard workflow, but for models at this scale there's often no practical alternative on a single machine.

## Memory System Pressure on Very Large MoE Models

MoE models have a deceptively large memory footprint. While only a fraction of experts are active per token, **all expert weights must reside in memory**. This creates unique performance challenges:

### The bandwidth illusion

For a model with 256 experts, 8 active per token:
- **Total weights in memory**: ~418 GB
- **Active weights per token**: ~23 GB
- **Theoretical time at 800 GB/s**: ~29ms

But **actual time can be 500x slower** (e.g., 15s/token) when the model nearly fills available RAM. This is not a software bug — it's a fundamental hardware limitation.

### Root cause: memory system thrashing

`gather_qmm` (the MLX primitive for sparse expert selection) is genuinely selective — it reads only the active expert weights. Profiling confirms:
- Isolated single tensor: 8/256 experts takes 0.56ms vs 3.08ms for all 256
- Same tensor with full model loaded: 8/256 takes 6.53ms (scattered access across a massive address space)
- Sequential access across 75 MoE layers: 57ms/layer → ~4.3s total for just one projection

The performance collapse comes from:
1. **TLB (page table) thrashing** — 418 GB / 16KB pages = ~26M pages, far exceeding GPU TLB capacity
2. **Dual-die cross-fabric access** — on M3/M4 Ultra, accessing memory across dies adds latency
3. **Scattered gather patterns** — reading 8 random experts from a 256-expert tensor creates non-sequential access patterns that defeat memory prefetching

### Mitigation

The only effective solution is to **reduce per-node memory pressure**:
- **Tensor parallelism** across multiple machines (see [Distributed Inference](distributed-inference.md))
- **More aggressive quantization** (3-bit instead of 4-bit) to shrink the footprint
- **Smaller model variant** if available

Splitting a 418 GB model across 2 nodes (~209 GB each) can yield 100-150x speedup — not because of doubled compute, but because each node's working set fits comfortably in the GPU's efficient memory range.
